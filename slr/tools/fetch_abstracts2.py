#!/usr/bin/env python3
"""Second-pass abstract retrieval for records still lacking one.

fetch_abstracts.py queries OpenAlex by DOI. This tries four sources in order and
also handles records with no DOI at all, which the first pass could not:

  1. Semantic Scholar by DOI
  2. Crossref by DOI
  3. OpenAlex by title
  4. Semantic Scholar by title

Title lookups are guarded by a similarity check (default 0.85) so a wrong paper
cannot be silently attached to a record. Results extend openalex_abstracts.json,
which build_screening_set.py already reads, so nothing already held is re-fetched.

  python3 fetch_abstracts2.py ../screening/SCREEN_bands1-2.csv
"""
import csv, difflib, html, json, os, pathlib, re, sys, time, unicodedata
import urllib.error, urllib.parse, urllib.request

csv.field_size_limit(10**9)
HERE = pathlib.Path(__file__).resolve().parent
CACHE = HERE / "openalex_abstracts.json"
SIM_MIN = 0.85


def norm_title(s):
    """Normalise for comparison and for querying: unify quotes, strip markup."""
    s = html.unescape(s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def similar(a, b):
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


def get(url, timeout=30, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method="POST" if data else "GET",
                                 headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def inv_to_text(inv):
    if not inv:
        return ""
    return " ".join(w for _, w in sorted((i, w) for w, idxs in inv.items() for i in idxs))


# ---------------------------------------------------------------- sources
def s2_by_doi(batch):
    """Semantic Scholar batch endpoint: up to 500 ids per call."""
    out = {}
    data = json.dumps({"ids": [f"DOI:{d}" for d in batch]}).encode()
    res = get("https://api.semanticscholar.org/graph/v1/paper/batch?fields=abstract",
              data=data, headers={"Content-Type": "application/json"})
    for doi, item in zip(batch, res):
        if item and item.get("abstract"):
            out[doi] = item["abstract"]
    return out


def crossref_by_doi(doi):
    d = get(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")
    a = (d.get("message") or {}).get("abstract") or ""
    a = re.sub(r"<[^>]+>", " ", a)               # JATS markup
    return re.sub(r"\s+", " ", html.unescape(a)).strip()


def openalex_by_title(title):
    q = urllib.parse.quote(norm_title(title)[:200])
    d = get(f"https://api.openalex.org/works?per-page=1&select=title,abstract_inverted_index&search={q}")
    for c in (d.get("results") or []):
        if similar(title, c.get("title") or "") >= SIM_MIN:
            return inv_to_text(c.get("abstract_inverted_index"))
    return ""


def s2_by_title(title):
    q = urllib.parse.quote(norm_title(title)[:200])
    d = get(f"https://api.semanticscholar.org/graph/v1/paper/search?limit=1&fields=title,abstract&query={q}")
    for c in (d.get("data") or []):
        if similar(title, c.get("title") or "") >= SIM_MIN:
            return c.get("abstract") or ""
    return ""


def main(paths):
    cache = json.load(open(CACHE)) if CACHE.exists() else {}
    before = len(cache)
    rows = []
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as fh:
            rows += [r for r in csv.DictReader(fh) if r.get("has_abstract") != "yes"]
    # key by DOI where present, else by normalised title
    todo = []
    for r in rows:
        doi = (r.get("doi") or "").strip().lower()
        key = doi or "title:" + norm_title(r["title"])
        if key not in cache:
            todo.append((key, doi, r["title"]))
    print(f"{len(rows)} records lack an abstract; {len(todo)} not yet in cache", flush=True)

    with_doi = [t for t in todo if t[1]]
    print(f"\n[1/4] Semantic Scholar by DOI ({len(with_doi)})", flush=True)
    for i in range(0, len(with_doi), 100):
        chunk = with_doi[i:i + 100]
        try:
            found = s2_by_doi([d for _, d, _ in chunk])
            for key, doi, _ in chunk:
                if doi in found:
                    cache[key] = found[doi]
        except Exception as e:
            print(f"   batch {i} failed: {type(e).__name__}", flush=True)
        time.sleep(1.2)
    print(f"   cache now {len(cache):,} (+{len(cache)-before})", flush=True)

    stages = [("[2/4] Crossref by DOI", lambda key, doi, t: crossref_by_doi(doi) if doi else "", 0.15),
              ("[3/4] OpenAlex by title", lambda key, doi, t: openalex_by_title(t), 0.2),
              ("[4/4] Semantic Scholar by title", lambda key, doi, t: s2_by_title(t), 1.2)]
    for label, fn, delay in stages:
        remaining = [t for t in todo if t[0] not in cache]
        print(f"\n{label} ({len(remaining)} remaining)", flush=True)
        start = len(cache)
        for n, (key, doi, title) in enumerate(remaining, 1):
            try:
                a = fn(key, doi, title)
                if a and len(a) > 80:
                    cache[key] = a
            except Exception:
                pass
            if n % 100 == 0:
                print(f"   {n}/{len(remaining)}  cache {len(cache):,}", flush=True)
            time.sleep(delay)
        print(f"   recovered {len(cache)-start}; cache now {len(cache):,}", flush=True)

    json.dump(cache, open(CACHE, "w"))
    print(f"\ntotal recovered this run: {len(cache)-before}")
    print(f"cache: {len(cache):,} abstracts -> {CACHE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
