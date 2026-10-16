#!/usr/bin/env python3
"""Build a readable verification pack for the 60-record human check.

A CSV with one record per line, abstracts included, is not something a person can read and
judge. This produces a PDF with one record per page: the title, venue, keywords and
abstract, then what the automated screening decided in each round and why, then a place to
say whether the reviewer agrees.

Only disagreements need recording, so the response file lists all 60 records and asks for a
mark against the ones the reviewer disagrees with, with the reason.

  python3 make_verification_pack.py          # writes the .tex, .pdf and response CSV
  python3 make_verification_pack.py --no-pdf # just the .tex

Venue and year are shown although they are not part of the topic judgement: criteria I1,
I2, E1, E2 and E6 turn on publication type and date, which cannot be judged without them.
"""
import argparse, csv, pathlib, re, subprocess, sys, unicodedata

csv.field_size_limit(10 ** 9)
HERE = pathlib.Path(__file__).resolve().parent
SCREENING = HERE.parent / "screening"
SEARCHES = HERE.parent / "searches" / "filter" / "searches.csv"
norm = lambda t: re.sub(r"[^a-z0-9]+", "", (t or "").lower())

TEXREP = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
          "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
          "^": r"\textasciicircum{}"}


def tex(s):
    """Escape for pdflatex. Records come from vendor exports and carry zero-width spaces,
    smart quotes, Greek letters and the like; anything pdflatex cannot set is dropped
    rather than left to abort the build."""
    for a, b in (("\u2013", "--"), ("\u2014", "---"), ("\u2212", "-"), ("\u2018", "`"),
                 ("\u2019", "'"), ("\u201c", "``"), ("\u201d", "''"), ("\u00a0", " "),
                 ("\u2026", "..."), ("\u00d7", "x")):
        s = (s or "").replace(a, b)
    # drop format and control characters: zero-width space, joiners, BOM, soft hyphen
    s = "".join(c for c in s if unicodedata.category(c) not in ("Cf", "Cc", "Co", "Cs"))
    # keep ASCII and the Latin supplements pdflatex sets without extra packages
    s = "".join(c if ord(c) < 0x180 else " " for c in s)
    s = "".join(TEXREP.get(c, c) for c in s)
    return re.sub(r"\s+", " ", s).strip()


def load(name):
    with open(SCREENING / name, encoding="utf-8", errors="replace") as fh:
        return list(csv.DictReader(fh))


def keyword_index():
    if not SEARCHES.exists():
        return {}
    fields = ("Author Keywords", "IEEE Terms", "keywords", "keyword")
    idx = {}
    with open(SEARCHES, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh):
            k = norm(r.get("title"))
            if not k or k in idx:
                continue
            kws = [v.strip() for f in fields if (v := (r.get(f) or "").strip())]
            if kws:
                idx[k] = "; ".join(dict.fromkeys(kws))[:400]
    return idx


ROUNDS = [("Round 1 — screening against the criteria", "LLM_SCREEN_full_gpt-6-luna.csv"),
          ("Round 2 — re-read of borderline records", "LLM_SCREEN_pass2_gpt-6-luna.csv"),
          ("Round 3 — rescoring of the included set", "LLM_RESCORE_includes_gpt-6-luna.csv")]

PREAMBLE = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[margin=22mm,top=20mm,bottom=20mm]{geometry}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{fancyhdr}
\definecolor{rule}{gray}{0.62}
\definecolor{soft}{gray}{0.35}
\definecolor{panel}{gray}{0.96}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\footnotesize\color{soft}Screening verification --- 60-record sample}
\fancyhead[R]{\footnotesize\color{soft}\thepage}
\renewcommand{\headrulewidth}{0.2pt}
\begin{document}
"""

INTRO = r"""
\begin{center}
{\large\bfseries Screening verification: 60-record sample}\\[2mm]
{\color{soft}Python for DO-178C-compliant airborne software --- systematic literature review}
\end{center}
\vspace{4mm}

This pack contains 60 records drawn from the screening set: 30 that the automated screening
included and 30 that it excluded, in random order. For each one you are shown the title,
venue, keywords where available, and abstract, followed by what the screening decided in
each round and the reason it gave.

For each record, decide whether you agree with the final decision. Where you agree, move on;
nothing needs recording. Where you \textbf{disagree}, open
\texttt{VERIFY\_60\_response.csv}, find that record number, and put \texttt{d} in the
\texttt{disagree} column with your reason in the \texttt{why} column. The other columns are
already filled in; leave them alone. Only the disagreements are of interest, and the review reports how many of the
60 were disputed and on what grounds.

The criteria are in \texttt{slr/protocol.md} \S5. Judge each record against those criteria,
not against what you would personally have retrieved.

Not every record went through every round, so the rounds shown differ from page to page.
Round 1 screened all 3{,}709 records. Round 2 re-read only those whose relevance fell in the
band where repeated screening proved unreliable. Round 3 rescored only the records that were
included after rounds 1 and 2, to put them on one comparable scale. Where a round is absent,
that record was not eligible for it; where two rounds disagree, the later one stands.

\vspace{3mm}
{\color{soft}\footnotesize Records without an abstract are marked as such: 8 of the 60 carry
a title only, which is itself a limitation worth noting where it affects your judgement.}
\clearpage
"""


def record_page(i, n, rec, kws, rounds, final):
    out = [r"{\color{soft}\footnotesize RECORD %d OF %d}\\[1mm]" % (i, n),
           r"{\large\bfseries %s}\\[1.5mm]" % tex(rec["title"])]
    meta = " \\textperiodcentered{} ".join(
        x for x in (tex(rec.get("year")), tex(rec.get("venue"))) if x)
    if meta:
        out.append(r"{\color{soft}\small %s}\\[2mm]" % meta)
    if kws:
        out.append(r"{\small\textbf{Keywords.} %s}\\[2mm]" % tex(kws))
    ab = (rec.get("abstract") or "").strip()
    if ab and ab != "(not available)":
        out.append(r"{\small\textbf{Abstract.} %s}" % tex(ab))
    else:
        out.append(r"{\small\itshape\color{soft}No abstract available --- "
                   r"this record was judged on its title alone.}")
    out.append(r"\vspace{3mm}")
    out.append(r"\vspace{3mm}{\color{rule}\hrule height 0.4pt}\vspace{2.5mm}")
    out.append(r"{\small\textbf{What the automated screening decided}}\\[2mm]")
    for label, r in rounds:
        out.append(r"{\footnotesize\color{soft}%s}\\[0.5mm]" % tex(label))
        out.append(r"{\small\textbf{%s}, criterion %s, relevance %s/5}\\[0.5mm]"
                   % (tex(r["decision"]), tex(r["criterion"]), tex(r["relevance"])))
        out.append(r"{\small %s}\\[2.5mm]" % tex(r["reason"]))
    out.append(r"{\small\textbf{Final decision: %s}}" % tex(final))
    out.append(r"\vspace{2.5mm}{\color{rule}\hrule height 0.4pt}")
    out.append(r"\vspace{2mm}")
    out.append(r"{\small\textbf{Do you agree with the final decision?}\quad{}"
               r"Agree $\square$\qquad{}Disagree $\square$}\\[1mm]")
    out.append(r"{\footnotesize\color{soft}If you disagree, why:}\\[1mm]")
    out.append(r"\color{rule}\rule{\linewidth}{0.3pt}\\[3mm]"
               r"\rule{\linewidth}{0.3pt}\color{black}")
    out.append(r"\clearpage")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()

    blind = load("SAMPLE_60_records.csv")
    byround = [(lab, {norm(x["title"]): x for x in load(f)}) for lab, f in ROUNDS]
    final = {norm(x["title"]) for x in load("INCLUDED_final.csv")}
    src = {norm(x["title"]): x for x in load("SCREEN_bands1-2.csv")}
    kws = keyword_index()

    pages = [PREAMBLE, INTRO]
    for i, b in enumerate(blind, 1):
        k = norm(b["title"])
        rs = [(lab, d[k]) for lab, d in byround if k in d]
        rec = dict(b)
        rec["venue"] = src.get(k, {}).get("venue", "")
        rec["year"] = src.get(k, {}).get("year", "")
        pages.append(record_page(i, len(blind), rec, kws.get(k, ""), rs,
                                 "include" if k in final else "exclude"))
    pages.append(r"\end{document}")
    texf = SCREENING / "VERIFY_60.tex"
    texf.write_text("\n".join(pages), encoding="utf-8")

    with open(SCREENING / "VERIFY_60_response.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["record", "title", "automated_decision", "disagree", "why"])
        for i, b in enumerate(blind, 1):
            k = norm(b["title"])
            # pre-filled for reference; the reviewer only touches disagree and why
            w.writerow([i, b["title"], "include" if k in final else "exclude", "", ""])

    print(f"wrote {texf.name} and VERIFY_60_response.csv ({len(blind)} records)")
    print(f"  rounds shown per record: "
          f"{sum(1 for b in blind if norm(b['title']) in byround[1][1])} have round 2, "
          f"{sum(1 for b in blind if norm(b['title']) in byround[2][1])} have round 3")
    if a.no_pdf:
        return
    for _ in range(2):
        p = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            texf.name], cwd=SCREENING, capture_output=True, text=True, errors="replace")
    if p.returncode:
        tail = "\n".join(p.stdout.splitlines()[-20:])
        sys.exit(f"pdflatex failed:\n{tail}")
    for ext in (".aux", ".log", ".out"):
        (SCREENING / ("VERIFY_60" + ext)).unlink(missing_ok=True)
    print(f"  built {(SCREENING / 'VERIFY_60.pdf').name}")


if __name__ == "__main__":
    main()
