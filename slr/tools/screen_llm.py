#!/usr/bin/env python3
"""LLM-assisted title/abstract screening for the SLR.

One API call per record, fresh context each time (see slr/screening/SCREENING_PROCESS.md §3).
The prompt is screening_prompt.md, reproduced verbatim from protocol.md §2 and §5.

  python3 screen_llm.py --pilot 100 --model gpt-6-luna
  python3 screen_llm.py --all     --model gpt-6-luna --out ../screening/llm_run_gpt-6-luna.csv

The API key is read from ~/.openai_key and never written to disk or logged.
"""
import argparse, csv, json, os, pathlib, random, re, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# Raw HTTP rather than the openai SDK: the installed SDK negotiates zstd compression
# against a zstandard build that rejects it ("Decompressor.decompress() got an
# unexpected keyword argument 'output_buffer_limit'"). stdlib-only also matches the
# other tools in this directory, which have no third-party dependencies.
API_URL = "https://api.openai.com/v1/chat/completions"


def post(key, payload, timeout=180):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json",
                 "Accept-Encoding": "gzip"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            import gzip
            raw = gzip.decompress(raw)
        return json.loads(raw)

csv.field_size_limit(10**9)
HERE = pathlib.Path(__file__).resolve().parent
SCREENING = HERE.parent / "screening"
SEARCHES = HERE.parent / "searches" / "filter" / "searches.csv"


def load_key():
    p = pathlib.Path.home() / ".openai_key"
    if not p.exists():
        sys.exit("~/.openai_key not found")
    return p.read_text().strip()


def load_prompt(name="screening_prompt.md"):
    t = (HERE / name).read_text() if "/" not in name else pathlib.Path(name).read_text()
    sys_part = t.split("## SYSTEM", 1)[1].split("## USER", 1)[0].strip()
    usr_part = t.split("## USER", 1)[1].strip()
    return sys_part, usr_part


def keyword_index():
    """Keywords live in the raw merge, not the screening file. Rejoin by title."""
    if not SEARCHES.exists():
        return {}
    fields = ("Author Keywords", "IEEE Terms", "keywords", "keyword")
    idx = {}
    with open(SEARCHES, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            t = (r.get("title") or "").strip().lower()
            if not t or t in idx:
                continue
            kws = [v.strip() for f in fields if (v := (r.get(f) or "").strip())]
            if kws:
                idx[t] = "; ".join(dict.fromkeys(kws))[:600]
    return idx


def load_records():
    with open(SCREENING / "SCREEN_bands1-2.csv", encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh))
    kw = keyword_index()
    # Abstracts recovered after the screening set was generated live in the cache,
    # not in the CSV. Consult it so late recoveries are used without regenerating.
    cpath = HERE / "openalex_abstracts.json"
    cache = json.load(open(cpath)) if cpath.exists() else {}
    filled = 0
    for r in rows:
        r["keywords"] = kw.get((r["title"] or "").strip().lower(), "")
        if not (r["abstract"] or "").strip():
            doi = (r.get("doi") or "").strip().lower()
            a = cache.get(doi) or cache.get("title:" + re.sub(r"\s+", " ", re.sub(
                r"[^a-z0-9 ]", " ", (r["title"] or "").lower())).strip())
            if a:
                r["abstract"] = a
                r["has_abstract"] = "yes"
                filled += 1
    if filled:
        print(f"  filled {filled} abstracts from the cache", flush=True)
    return rows


def stratified(rows, n, seed=20261016):
    """Exercise the full range: top / middle / bottom of the score order, the
    high-risk exclusions, and records with no abstract."""
    rnd = random.Random(seed)
    ordered = sorted(rows, key=lambda r: -int(r["score"] or 0))
    third = len(ordered) // 3
    risk_titles = set()
    for hr in (SCREENING / "REVIEW_349_high_risk.csv",
               pathlib.Path.home() / "Documents/PhDs/Mohammad/SLR-screening/round2/REVIEW_349_high_risk.csv"):
        if hr.exists():
            with open(hr, encoding="utf-8", errors="replace") as fh:
                risk_titles = {(x["title"] or "").lower() for x in csv.DictReader(fh)}
            break
    buckets = [
        ("top",        ordered[:third],                                            20),
        ("middle",     ordered[third:2 * third],                                   20),
        ("bottom",     ordered[2 * third:],                                        20),
        ("high_risk",  [r for r in ordered if r["title"].lower() in risk_titles],  15),
        ("no_abstract", [r for r in ordered if r["has_abstract"] != "yes"],        10),
    ]
    picked, seen = [], set()

    # Known-item set, forced into the sample so recall is measurable. This affects
    # which records are screened, never how they are judged: the prompt contains no
    # paper-specific content (see screening_prompt.md).
    known = [r"assessing python.s suitability", r"\bnagini\b", r"esbmc-python",
             r"static value analysis of python", r"static type analysis by abstract",
             r"multilanguage static analysis", r"reconciling dynamically and statically",
             r"gradual soundness", r"python-based embedded real-time",
             r"formal verification of avionics software", r"testing or formal verification",
             r"state of the art in software tool qual", r"misra c coding standard",
             r"high-altitude glider"]
    for pat in known:
        for r in ordered:
            if re.search(pat, (r["title"] or "").lower()) and r["order"] not in seen:
                r["stratum"] = "known_item"; seen.add(r["order"]); picked.append(r); break

    for name, pool, k in buckets:
        pool = [r for r in pool if r["order"] not in seen]
        for r in rnd.sample(pool, min(k, len(pool))):
            r["stratum"] = name
            seen.add(r["order"])
            picked.append(r)
    while len(picked) < n:                       # top up if a bucket was short
        r = rnd.choice(ordered)
        if r["order"] not in seen:
            r["stratum"] = "topup"; seen.add(r["order"]); picked.append(r)
    return picked[:n]


FIELDS = ("decision", "criterion", "relevance", "evidence", "reason")


def parse(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON in response")
    d = json.loads(m.group(0))
    missing = [f for f in FIELDS if f not in d]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    if d["decision"] not in ("include", "exclude", "uncertain"):
        raise ValueError(f"bad decision: {d['decision']!r}")
    d["relevance"] = int(d["relevance"])
    return d


def screen_one(key, model, sys_prompt, usr_tmpl, rec, retries=3):
    prompt = (usr_tmpl
              .replace("{title}", rec["title"] or "")
              .replace("{year}", rec["year"] or "")
              .replace("{keywords}", rec["keywords"] or "(none supplied)")
              .replace("{abstract}", (rec["abstract"] or "").strip() or "(not available)"))
    last = None
    for attempt in range(retries):
        try:
            resp = post(key, {
                "model": model,
                "messages": [{"role": "system", "content": sys_prompt},
                             {"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
            })
            out = parse(resp["choices"][0]["message"]["content"])
            u = resp.get("usage", {})
            out["_in"] = u.get("prompt_tokens", 0)
            out["_out"] = u.get("completion_tokens", 0)
            return out
        except Exception as e:                   # transient or malformed
            last = e
            time.sleep(1.5 * (attempt + 1))
    return {"decision": "uncertain", "criterion": "NA", "relevance": -1,
            "evidence": "", "reason": f"API/parse failure: {type(last).__name__}: {last}",
            "_in": 0, "_out": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gpt-6-luna")
    ap.add_argument("--pilot", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--prompt", default="screening_prompt.md")
    ap.add_argument("--only", help="CSV with an 'order' column; screen only those records")
    a = ap.parse_args()

    key = load_key()
    sys_prompt, usr_tmpl = load_prompt(a.prompt)

    rows = load_records()
    if a.only:
        with open(a.only, encoding="utf-8") as fh:
            keep = {r["order"] for r in csv.DictReader(fh)}
        rows = [r for r in rows if r["order"] in keep]
        print(f"  restricted to {len(rows):,} of {len(keep):,} requested records", flush=True)
    if a.pilot:
        rows = stratified(rows, a.pilot)
    elif not a.all:
        sys.exit("specify --pilot N or --all")
    for r in rows:
        r.setdefault("stratum", "all")
    print(f"screening {len(rows):,} records with {a.model} ({a.workers} workers)", flush=True)

    results, t0 = {}, time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(screen_one, key, a.model, sys_prompt, usr_tmpl, r): r for r in rows}
        for i, f in enumerate(as_completed(futs), 1):
            results[futs[f]["order"]] = f.result()
            if i % 25 == 0 or i == len(rows):
                print(f"  {i}/{len(rows)}  ({time.time()-t0:.0f}s)", flush=True)

    out = pathlib.Path(a.out) if a.out else SCREENING / f"llm_pilot_{a.model}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    cols = ["order", "stratum", "decision", "criterion", "relevance", "evidence", "reason",
            "title", "year", "venue", "has_abstract", "doi", "prior_score", "prior_band"]
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(cols)
        for r in rows:
            d = results[r["order"]]
            w.writerow([r["order"], r["stratum"], d["decision"], d["criterion"], d["relevance"],
                        d["evidence"], d["reason"], r["title"], r["year"], r["venue"],
                        r["has_abstract"], r["doi"], r["score"], r["band"]])

    tin = sum(d["_in"] for d in results.values())
    tout = sum(d["_out"] for d in results.values())
    fails = sum(1 for d in results.values() if d["relevance"] == -1)
    from collections import Counter
    print(f"\nwrote {out}")
    print(f"  decisions: {dict(Counter(d['decision'] for d in results.values()))}")
    print(f"  failures:  {fails}")
    print(f"  tokens:    {tin:,} in / {tout:,} out  ({tin/len(rows):.0f} in per record)")
    print(f"  elapsed:   {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
