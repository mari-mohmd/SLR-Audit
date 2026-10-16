#!/usr/bin/env python3
"""Select the borderline records that need a second screening pass.

Two rules, applied to the first-pass output:

  A  relevance 2-3 (the band where repeat screening disagrees) AND a high-value topic term
  B  excluded, but carrying a timing term together with a language-level term - the
     managed-runtime timing literature that RQ3 names as precedent

The first pass wrote no abstract column, so the original selection matched titles only and
covered 645 records. Matching title+abstract yields 1,133. Both modes are kept: --titles-only
reproduces the selection that was actually screened, and the default uses abstracts.

  python3 select_second_pass.py --titles-only --out ../screening/SECOND_PASS_candidates.csv
  python3 select_second_pass.py --exclude-done ../screening/SECOND_PASS_candidates.csv \
          --out ../screening/SECOND_PASS_remaining.csv
"""
import argparse, csv, pathlib, re, sys

csv.field_size_limit(10 ** 9)
HERE = pathlib.Path(__file__).resolve().parent
SCREENING = HERE.parent / "screening"

HI = re.compile(
    r"do-?178|do-?330|do-?333|misra|tool qualificat|mc/?dc|modified condition|certif"
    r"|\bada\b|spark|safety-?critical java|\bjvm\b|bytecode|byte code|managed runtime|interpreter"
    r"|garbage collect|global interpreter lock|\bgil\b|subset|restrict|type annotat|type hint"
    r"|airborne|avionic|python|dynamic(ally)? typed")
TIME = re.compile(r"worst-?case execution|wcet|schedulab|jitter|determinis")
LANG = re.compile(
    r"python|\bjava\b|\bjvm\b|bytecode|byte code|interpreter|managed runtime|virtual machine"
    r"|garbage collect|\bgil\b|annotation language|dynamic(ally)? typed|high-?level language|scripting")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--screen", default=str(SCREENING / "LLM_SCREEN_full_gpt-6-luna.csv"))
    ap.add_argument("--titles-only", action="store_true",
                    help="match titles alone, reproducing the selection that was screened")
    ap.add_argument("--exclude-done", help="CSV of records already screened; omit them")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    with open(a.screen, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    abstracts = {}
    if not a.titles_only:
        with open(SCREENING / "SCREEN_bands1-2.csv", encoding="utf-8", errors="replace") as fh:
            abstracts = {r["order"]: (r.get("abstract") or "") for r in csv.DictReader(fh)}

    def text(r):
        return ((r["title"] or "") + " " + abstracts.get(r["order"], "")).lower()

    sel = {r["order"] for r in rows if int(r["relevance"]) in (2, 3) and HI.search(text(r))}
    seam = {r["order"] for r in rows
            if r["decision"] != "include" and TIME.search(text(r)) and LANG.search(text(r))}
    keep = sel | seam

    if a.exclude_done:
        with open(a.exclude_done, encoding="utf-8") as fh:
            done = {r["order"] for r in csv.DictReader(fh)}
        keep -= done
        print(f"  omitting {len(done):,} already screened", file=sys.stderr)

    out = [r for r in rows if r["order"] in keep]
    out.sort(key=lambda r: (-int(r["relevance"]), r["title"]))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(out)
    print(f"rule A {len(sel):,}  rule B {len(seam):,}  selected {len(out):,} -> {a.out}")


if __name__ == "__main__":
    main()
