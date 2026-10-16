#!/usr/bin/env python3
"""Summarise the human verification of the 60-record sample.

Read VERIFY_60.pdf, decide for each record whether you agree with the final decision, and
mark the ones you do not in VERIFY_60_response.csv: put any of y/yes/x/1 in the `disagree`
column and give the reason in `why`. Rows left blank count as agreed.

  python3 summarise_verification.py

This reports how many of the 60 were disputed and on what grounds, and computes agreement
and Cohen's kappa from the responses.

Read the kappa with its design in mind. A disagreement on an included record means the
reviewer would have excluded it, so the 2x2 table reconstructs and kappa follows - but the
reviewer saw each decision and its reasoning before judging it, so the two readings are not
independent, and the sample is stratified 30/30, so the screening's marginal is 50% here
rather than its true 23% include rate. Both raise kappa above what an independent, randomly
sampled check would give. Report it with the design stated, as the printed sentence does.
"""
import argparse, csv, math, pathlib, re, sys

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
    # Reconstruct the 2x2: a disagreement means the reviewer took the opposite view.
    inc = [r for r in rows if r["automated_decision"] == "include"]
    exc = [r for r in rows if r["automated_decision"] == "exclude"]
    d_inc = sum(1 for r in inc if (r.get("disagree") or "").strip().lower() in YES)
    d_exc = sum(1 for r in exc if (r.get("disagree") or "").strip().lower() in YES)
    a, b = len(inc) - d_inc, d_inc          # screening included: reviewer agreed / would exclude
    c, d = d_exc, len(exc) - d_exc          # screening excluded: reviewer would include / agreed
    po = (a + d) / n
    pe = ((a + b) / n) * ((a + c) / n) + ((c + d) / n) * ((b + d) / n)
    print(f"\n{'':>16}{'reviewer: in':>14}{'reviewer: out':>15}")
    print(f"{'screening: in':>16}{a:>14}{b:>15}")
    print(f"{'screening: out':>16}{c:>14}{d:>15}")
    if pe >= 1:
        print("\nkappa undefined: one margin is empty")
        k = lo = hi = None
    else:
        k = (po - pe) / (1 - pe)
        se = math.sqrt(po * (1 - po) / (n * (1 - pe) ** 2)) if 0 < po < 1 else 0.0
        lo, hi = max(-1.0, k - 1.96 * se), min(1.0, k + 1.96 * se)
        band = ("poor" if k < 0.2 else "fair" if k < 0.4 else "moderate" if k < 0.6
                else "substantial" if k < 0.8 else "almost perfect")
        print(f"\nagreement  {a+d}/{n} = {po:.0%}")
        print(f"kappa      {k:.2f}   95% interval {lo:.2f} to {hi:.2f}   ({band})")

    if k is not None:
        print(f"\nFor the chapter:\n  A reviewer verified a stratified sample of {n} screening "
              f"decisions (30 included,\n  30 excluded), reviewing each decision together with the "
              f"reasoning recorded for it.\n  {len(dis)} decisions were disputed, giving "
              f"{po:.0%} agreement (Cohen's $\\kappa = {k:.2f}$, 95\\% CI\n  {lo:.2f}--{hi:.2f}). "
              f"Because the reviewer was shown each decision before judging it, this\n  measures "
              f"verification of the screening rather than independent agreement, and the\n  "
              f"coefficient should be read as an upper bound.")
        return
    print(f"\nFor the chapter:\n  A reviewer verified a stratified sample of {n} screening "
          f"decisions (30 included,\n  30 excluded), reviewing each decision together with the "
          f"reasoning recorded for it.\n  {len(dis)} of the {n} were disputed"
          + ("." if not dis else "; the grounds are given in \\S6.2.")
          + "\n  Because the reviewer saw each decision before judging it, this is a "
            "verification of\n  the screening rather than an independent second screen, and no "
            "agreement\n  coefficient is computed from it.")


if __name__ == "__main__":
    main()
