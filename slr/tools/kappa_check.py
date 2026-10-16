#!/usr/bin/env python3
"""Compare a reviewer's screening of SAMPLE_60_blind.csv against the automated screening.

Fill in the `your_decision` column of ../screening/SAMPLE_60_blind.csv with `include` or
`exclude` for every row - optionally `your_criterion` and `your_notes` too - and run:

  python3 kappa_check.py

It reports percentage agreement, Cohen's kappa with a 95% interval, the 2x2 table and
every disagreement, and prints a sentence that can go straight into the chapter. The
automated verdict is looked up here rather than stored in the sample, so the sample stays
blind until you have finished screening it.

  python3 kappa_check.py --file path/to/filled_sample.csv
"""
import argparse, csv, math, pathlib, re, sys

csv.field_size_limit(10 ** 9)
HERE = pathlib.Path(__file__).resolve().parent
SCREENING = HERE.parent / "screening"
norm = lambda t: re.sub(r"[^a-z0-9]+", "", (t or "").lower())


def kappa_ci(a, b, c, d):
    """a=both include, d=both exclude, b/c=disagreements. Returns (kappa, lo, hi)."""
    n = a + b + c + d
    po = (a + d) / n
    p1 = (a + b) / n * ((a + c) / n)
    p2 = (c + d) / n * ((b + d) / n)
    pe = p1 + p2
    if pe >= 1:
        return None, None, None
    k = (po - pe) / (1 - pe)
    # Fleiss, Cohen & Everitt asymptotic standard error
    se = math.sqrt(po * (1 - po) / (n * (1 - pe) ** 2)) if po < 1 else math.sqrt(
        (1 - pe) / (n * (1 - pe) ** 2))
    return k, max(-1.0, k - 1.96 * se), min(1.0, k + 1.96 * se)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(SCREENING / "SAMPLE_60_blind.csv"))
    a = ap.parse_args()

    with open(a.file, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(SCREENING / "INCLUDED_final.csv", encoding="utf-8") as fh:
        included = {norm(r["title"]) for r in csv.DictReader(fh)}

    blank = [r for r in rows if (r.get("your_decision") or "").strip() == ""]
    bad = [r for r in rows if (r.get("your_decision") or "").strip().lower()
           not in ("", "include", "exclude")]
    if blank:
        sys.exit(f"{len(blank)} of {len(rows)} rows have no your_decision yet "
                 f"(first: id {blank[0]['id']}). Fill every row, then re-run.")
    if bad:
        sys.exit(f"your_decision must be 'include' or 'exclude'; found "
                 f"{bad[0]['your_decision']!r} at id {bad[0]['id']}.")

    cells = {"a": 0, "b": 0, "c": 0, "d": 0}
    disagree = []
    for r in rows:
        auto = "include" if norm(r["title"]) in included else "exclude"
        you = r["your_decision"].strip().lower()
        if auto == "include" and you == "include":
            cells["a"] += 1
        elif auto == "exclude" and you == "exclude":
            cells["d"] += 1
        else:
            cells["b" if auto == "include" else "c"] += 1
            disagree.append((r, auto, you))

    n = len(rows)
    agree = cells["a"] + cells["d"]
    k, lo, hi = kappa_ci(cells["a"], cells["b"], cells["c"], cells["d"])
    print(f"{n} records screened\n")
    print(f"{'':>14}{'you: include':>14}{'you: exclude':>14}")
    print(f"{'auto: include':>14}{cells['a']:>14}{cells['b']:>14}")
    print(f"{'auto: exclude':>14}{cells['c']:>14}{cells['d']:>14}")
    print(f"\nagreement  {agree}/{n} = {agree/n:.0%}")
    if k is None:
        print("kappa      undefined (one margin is empty - every cell must have records)")
    else:
        print(f"kappa      {k:.2f}   95% interval {lo:.2f} to {hi:.2f}")
        band = ("poor" if k < 0.2 else "fair" if k < 0.4 else "moderate" if k < 0.6
                else "substantial" if k < 0.8 else "almost perfect")
        print(f"           ({band} agreement on the Landis-Koch bands)")
    if disagree:
        print(f"\n{len(disagree)} disagreement(s) - read these again and record the resolution:")
        for r, auto, you in disagree:
            print(f"   id {r['id']:>3}  auto {auto:<8} you {you:<8} {r['title'][:62]}")
    if k is not None:
        print(f"\nFor the chapter:\n  A second reviewer independently re-screened a stratified "
              f"sample of {n} records\n  (30 included, 30 excluded) without sight of the automated "
              f"decisions. Agreement\n  was {agree/n:.0%} (Cohen's $\\kappa = {k:.2f}$, 95\\% CI "
              f"{lo:.2f}--{hi:.2f}).")


if __name__ == "__main__":
    main()
