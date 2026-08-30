Systematic Literature Review Protocol

## Python for DO-178C-Compliant Airborne Software: Restricted Subset and Verification Toolset

**Version:** 1.1 | **Author:** Mohammad Mari | **Supervisors:** Dr. Lian Wen & Qinyi Li |  **Assessor:** Prof. Rene Hexel |  **Affiliation:** Griffith University | **Date:** 2026-08-26

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
- ("DO-178" OR "DO-330" OR "DO-333" OR "ED-12" OR "airborne software" OR avionics) AND ("formal method*" OR "tool qualification" OR "static analysis" OR verification OR "programming language")
- ("worst-case execution time" OR WCET OR "real-time" OR determinis*) AND ("garbage collection" OR "managed runtime" OR "virtual machine" OR interpreter OR Python OR Java)
- safety-critical Java OR SCJ OR JSF AV
- Mojo OR Cython OR Nuitka OR PyPy OR Numba OR MicroPython (performance-oriented or restricted Python implementations)

**Date range:** 1995–2026 (earlier foundational sources - e.g. Leveson & Harvey 1983, MISRA/SPARK origins - are pulled in via snowballing, not the date-bound search).

**Also:** backward/forward snowballing from Nagini, ESBMC-Python, CrossHair, and the safety-critical Java papers already identified; manual check of key venues (SAFECOMP, ISSTA, ICSE, DASC).

Each query family will be translated into the exact syntax required by each database and run accordingly. For each database, the exact query strings used, filters applied, dates run, and results returned will be logged in a single file under `slr/searches/`, named <database></database>.md (e.g. ieee.md, scopus.md) — internal structure and level of detail within each file is left to the author's discretion.

## 4. Inclusion / Exclusion

**Inclusion criteria**

A study will be included if it satisfies the following criteria:

* I1 — Publication type: The work is a peer-reviewed research paper, including journal articles, conference papers, or workshop papers. Standards, regulatory guidance, and Python Enhancement Proposals (PEPs) will be retained in a separate reference pool and are not required to be peer-reviewed.

* I2 — Publication period and language: The work was published between 1995 and 2026 and is available in English.

* I3 — Technical relevance: The work directly addresses Python runtime behaviour, verification, static or dynamic analysis, language subsetting, or a comparable dynamic programming language.

* I4 — Safety and verification relevance: The work addresses safety-critical software, formal methods, verification, restriction of language features, or the feasibility of a safety-oriented toolchain.

* I5 — DO-178C and related relevance: The work directly addresses, evaluates, or provides evidence relevant to DO-178C, DO-330, DO-333, or objectives and practices applicable to airborne safety-critical software. Relevant DO-178C, DO-330, DO-333, and PEP documents will be retained in the separate reference pool to support the interpretation of the included studies.

**Exclusion criteria**

A candidate will be excluded if any of the following criteria apply:

* E1 — Publication type: The work is marketing material, an opinion piece, presentation, blog post, or other non-research material without a substantive methodology.

* E2 — Language or date: The work is not available in English or was published outside the 1995--2026 period.

* E3 — Insufficient technical relevance: The work does not address Python, a comparable dynamic language, verification, language restriction, or a relevant formal-methods approach.

* E4 — Insufficient safety/verification relevance: The work is focused solely on general-purpose performance, programming productivity, or language features without relevance to safety, verification, restriction, or toolchain feasibility.

* E5 — Duplicate or superseded work: The work is a duplicate or superseded version of another included study. Where multiple versions exist, the most complete or recent version will be retained.

## 5. Screening

Titles and abstracts will be screened first to filter out clearly irrelevant papers. For papers that pass this stage, the methods, results/evaluation, and conclusion sections will be reviewed to make the include/exclude decision - full papers will not be read in full at this stage, given the 1.5-month timeframe for this review. Papers with an unclear or ambiguous fit based on these sections will be read in full before a final decision is made. Every decision (include/exclude, with reason) will be logged in `slr/screening.csv`. Where possible, a supervisor or second reviewer will independently check a sample of ~20% of decisions, with any disagreements resolved by discussion.

Titles and abstracts will be screened first to exclude clearly irrelevant papers. The included studies will then be assessed using a two-tier reading strategy.  **Core comparator studies** , including key approaches such as Nagini, ESBMC-Python, Monat, Fromherz, RPython, CrossHair, PyVeritas, and the CompCert qualification work, will be read in full because the detailed extraction fields required for this review cannot reliably be recovered from abstracts or selected sections alone. For all other studies, the methods, results/evaluation, and conclusion sections will be reviewed to make the include/exclude decision. Papers with an unclear or ambiguous fit will be read in full before a final decision is made.

Given the 1.5-month timeframe, this targeted-reading approach is an explicit limitation of the review. Every screening decision (include/exclude, with reason) will be recorded in `slr/screening.csv`.  A supervisor or second reviewer will independently check a sample of approximately 20% of screening decisions, with disagreements resolved through discussion.

## 6. Data Extraction

For each included paper, data will be extracted using a predefined extraction schema and recorded in `slr/extraction.csv`, with one row per included study. The schema will capture the following information:

* Bibliographic information: authors, title, publication year, venue, and DOI or other persistent identifier where available.
* RQ mapping: the research question(s) (RQ1--RQ4) informed by the study and the evidence relevant to each RQ.
* Language and tool: the programming language, tool, framework, analysis technique, or verification technology studied.
* Verification or restriction approach: the approach used to verify, analyse, restrict, or otherwise establish properties of the language or programs.
* Subset restrictions: any language subset, coding restrictions, or programming constructs that the approach requires or imposes, together with the stated rationale for each restriction.
* Excluded dynamic features: dynamic-language features explicitly excluded, unsupported, or discouraged by the approach, including the reason for their exclusion where stated.
* Property classes: the classes of properties addressed by the approach, distinguishing properties that are formally proven from those that are heuristically detected, tested, inferred, or otherwise approximated.
* Soundness and completeness: any soundness or completeness claims made by the authors, including the scope and conditions under which such claims hold.
* Translation and semantic preservation: whether the approach translates programs into another language, representation, or intermediate form; the translation target; and how the authors justify semantic preservation or correctness of the translation.
* Trusted computing base (TCB): components, tools, assumptions, libraries, runtimes, compilers, or other elements that must be trusted for the claimed verification or analysis results to hold.
* Developer burden: the annotation, specification, contracts, type declarations, or other information that developers must provide, including any stated effort or maintenance burden.
* Evaluation corpus and scale: the benchmark programs, datasets, case studies, or software systems evaluated, together with their size and relevant characteristics.
* Scalability: reported performance or scalability characteristics, including program size, execution time, resource requirements, or explicit scalability limits.
* DO-178C relevance: the stated or assessed relevance of the approach to DO-178C objectives, verification activities, or restrictions associated with airborne safety-critical software.
* Author-stated limitations: limitations, threats to validity, assumptions, or unresolved issues explicitly identified by the authors.

Where a field is not reported or cannot be determined from the paper, it will be recorded as NR (not reported) rather than inferred.

## 7. Synthesis

Papers will be grouped by verification approach (type-based, model checking, symbolic execution, language subsetting) and compared across groups against RQ1–RQ3.
