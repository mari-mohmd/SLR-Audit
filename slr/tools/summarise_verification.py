#!/usr/bin/env python3
"""Summarise the human verification of the 60-record sample.

Read VERIFY_60.pdf, decide for each record whether you agree with the final decision, and
mark the ones you do not in VERIFY_60_response.csv: put any of y/yes/x/1 in the `disagree`
column and give the reason in `why`. Rows left blank count as agreed.

  python3 summarise_verification.py

This reports how many of the 60 were disputed and on what grounds. It is a verification of
the automated screening, not an independent second screen: the reviewer sees each decision
and its reasoning before judging it, so the result cannot be read as inter-rater agreement
and no kappa is computed from it.
"""
import argparse, csv, pathlib, re, sys

csv.field_size_limit(10 ** 9)
SCREENING = pathlib.Path(__file__).resolve().parent.parent / "screening"
YES = {"y", "yes", "x", "1", "true", "disagree"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(SCREENING / "VERIFY_60_response.csv"))
    a = ap.parse_args()
    with open(a.file, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit("no rows in the response file")

    dis = [r for r in rows if (r.get("disagree") or "").strip().lower() in YES]
    unexplained = [r for r in dis if not (r.get("why") or "").strip()]
    n = len(rows)

    print(f"{n} records verified")
    print(f"  agreed     {n - len(dis)}")
    print(f"  disagreed  {len(dis)}  ({len(dis)/n:.0%})")
    if dis:
        by = {}
        for r in dis:
            by[r["automated_decision"]] = by.get(r["automated_decision"], 0) + 1
        part = ", ".join(f"{v} the screening had {k}d" for k, v in sorted(by.items()))
        print(f"  of those:  {part}")
        print("\ndisagreements:")
        for r in dis:
            why = (r.get("why") or "").strip() or "** no reason recorded **"
            print(f"  {r['record']:>3}  was {r['automated_decision']:<8} {r['title'][:58]}")
            print(f"       {why}")
    if unexplained:
        print(f"\n{len(unexplained)} disagreement(s) have no reason recorded; the review reports "
              f"the grounds, so these need filling in.")
    print(f"\nFor the chapter:\n  A reviewer verified a stratified sample of {n} screening "
          f"decisions (30 included,\n  30 excluded), reviewing each decision together with the "
          f"reasoning recorded for it.\n  {len(dis)} of the {n} were disputed"
          + ("." if not dis else "; the grounds are given in \\S6.2.")
          + "\n  Because the reviewer saw each decision before judging it, this is a "
            "verification of\n  the screening rather than an independent second screen, and no "
            "agreement\n  coefficient is computed from it.")


if __name__ == "__main__":
    main()
