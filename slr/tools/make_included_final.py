#!/usr/bin/env python3
"""Produce INCLUDED_final.csv: the included records, highest relevance first.

The screening ran in three passes and no single pass output is the answer. Pass 3
rescored the then-included set onto one comparable scale, and its output holds both the
records it kept and the 94 it dropped. This script filters that output to the includes,
so the result is one file that can be read, cited and sorted without further steps.

The relevance column is pass 3's, which is the only scale comparable across the whole
included set; see LLM_SCREENING_NOTE.md, Limitations item 1.

  python3 make_included_final.py
"""
import csv, pathlib

csv.field_size_limit(10 ** 9)
SCREENING = pathlib.Path(__file__).resolve().parent.parent / "screening"
SRC = SCREENING / "LLM_RESCORE_includes_gpt-6-luna.csv"
OUT = SCREENING / "INCLUDED_final.csv"
COLS = ["order", "relevance", "criterion", "title", "year", "venue", "doi", "evidence", "reason"]


def main():
    with open(SRC, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    inc = [r for r in rows if r["decision"] == "include"]
    inc.sort(key=lambda r: (-int(r["relevance"]), r["title"].lower()))
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(inc)
    by = {}
    for r in inc:
        by[int(r["relevance"])] = by.get(int(r["relevance"]), 0) + 1
    dist = "  ".join(f"{k}:{by[k]}" for k in sorted(by, reverse=True))
    print(f"{len(rows)} rescored -> {len(inc)} included ({len(rows)-len(inc)} dropped)")
    print(f"  relevance  {dist}")
    print(f"  wrote {OUT.relative_to(OUT.parent.parent)}")


if __name__ == "__main__":
    main()
