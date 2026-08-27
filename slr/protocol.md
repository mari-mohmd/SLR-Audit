Systematic Literature Review Protocol

## Python for DO-178C-Compliant Airborne Software: Restricted Subset and Verification Toolset

**Version:** 1.0 | **Author:** Mohammad Mari | **Supervisors:** Dr. Lian Wen & Qinyi Li |  **Assessor:** Prof. Rene Hexel |  **Affiliation:** Griffith University | **Date:** 2026-08-26

---

## 1. Purpose of the SLR

This SLR is being conducted to address the review comments raised at the confirmation seminar, specifically: (1) insufficient depth/breadth of literature supporting the thesis's claims, (2) the need to revise and strengthen the research questions in light of that literature, and (3) the need for a traceable record of how and why the confirmation report is being amended in response to these comments.

## 2. Revised / New Research Questions

- **RQ1:** Which Python constructs must be excluded to eliminate known failure classes (unhandled exceptions, unbounded recursion, signal races), and can each exclusion be justified the way MISRA C / SPARK justify theirs?
- **RQ2:** How does the proposed toolset (subset → static/type checks → bounded model checking) compare in soundness/completeness to Nagini, ESBMC-Python, and CrossHair?
- **RQ3:** Which DO-178C Level C/D objectives (including DO-333/DO-330) can the subset-plus-toolset realistically support, and which are structurally out of reach for an interpreted, garbage-collected language — as the safety-critical Java precedent suggests?

(RQ4 from the confirmation report is empirical/experimental, not literature-based, so it's out of scope for this SLR.)

## 3. Search Strategy

**Databases:** IEEE Xplore, ACM Digital Library, Scopus, SpringerLink, ScienceDirect. Google Scholar and DBLP for snowballing only.

**Search terms**, combined per topic:

- Python AND ("static analysis" OR "abstract interpretation" OR "type inference" OR "gradual typing" OR "type checking" OR "type error")
- Python AND ("formal verification" OR "model checking" OR "bounded model checking" OR "symbolic execution" OR "deductive verification" OR "theorem proving" OR contract*)
- ("restricted subset" OR "language subset" OR "safe subset" OR "coding standard" OR "coding guideline" OR profile) AND ("safety-critical" OR "high-integrity" OR certification)
- (restricted subset OR MISRA OR SPARK) AND (safety-critical OR high-assurance)
- ("DO-178" OR "DO-330" OR "DO-333" OR "ED-12" OR "airborne software" OR avionics) AND ("formal method*" OR "tool qualification" OR "static analysis" OR verification OR "programming language"
- ("worst-case execution time" OR WCET OR "real-time" OR determinis*) AND ("garbage collection" OR "managed runtime" OR "virtual machine" OR interpreter OR Python OR Java)
- safety-critical Java OR SCJ OR JSF AV
- Mojo OR Cython OR Nuitka OR PyPy OR Numba OR MicroPython (performance-oriented or restricted Python implementations)

**Date range:** 2010–2026 (earlier foundational sources - e.g. Leveson & Harvey 1983, MISRA/SPARK origins - are pulled in via snowballing, not the date-bound search).

**Also:** backward/forward snowballing from Nagini, ESBMC-Python, CrossHair, and the safety-critical Java papers already identified; manual check of key venues (SAFECOMP, ISSTA, ICSE, DASC).

Each query family will be translated into the exact syntax required by each database and run accordingly. For each database, the exact query strings used, filters applied, dates run, and results returned will be logged in a single file under `slr/searches/`, named <database></database>.md (e.g. ieee.md, scopus.md) — internal structure and level of detail within each file is left to the author's discretion.

## 4. Inclusion / Exclusion

**Include:** peer-reviewed, 1995–2026, English, and directly relevant to Python runtime/verification, language-subsetting for safety, or DO-178C/DO-333/DO-330 objectives. Work that analyses, verifies, restricts or benchmarks Python or a comparable dynamic language; formal-methods; and work presenting a restricted-subset strategy in a safety context.

**Exclude:** marketing material with no methodology; performance-focused papers that have no bearing on safety, verification, or subset/toolchain feasibility; duplicate/superseded versions (keep the newer one);

## 5. Screening

Titles and abstracts will be screened first to filter out clearly irrelevant papers. For papers that pass this stage, the methods, results/evaluation, and conclusion sections will be reviewed to make the include/exclude decision - full papers will not be read in full at this stage, given the 1.5-month timeframe for this review. Papers with an unclear or ambiguous fit based on these sections will be read in full before a final decision is made. Every decision (include/exclude, with reason) will be logged in `slr/screening.csv`. Where possible, a supervisor or second reviewer will independently check a sample of ~20% of decisions, with any disagreements resolved by discussion.

## 6. Data Extraction

For each included paper, the following will be recorded: bibliographic information, which RQ(s) it informs, the language/tool studied, its verification or restriction approach, any soundness/completeness claims made by the authors, and its relevance to DO-178C objectives. This data will be captured in `slr/extracted.csv`, with one row per included study.

## 7. Synthesis

Papers will be grouped by verification approach (type-based, model checking, symbolic execution, language subsetting) and compared across groups against RQ1–RQ3.
