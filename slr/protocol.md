Systematic Literature Review Protocol

## Python for DO-178C-Compliant Airborne Software: Restricted Subset and Verification Toolset

**Version:** 1.3 | **Author:** Mohammad Mari | **Supervisors:** Dr. Lian Wen & Qinyi Li |  **Assessor:** Prof. Rene Hexel |  **Affiliation:** Griffith University | **Date:** 2026-09-15

---

## 1. Purpose of the SLR

This SLR is being conducted to address the review comments raised at the confirmation seminar, specifically: (1) insufficient depth/breadth of literature supporting the thesis's claims, (2) the need to revise and strengthen the research questions in light of that literature, and (3) the need for a traceable record of how and why the confirmation report is being amended in response to these comments.

## 2. Revised / New Research Questions

- **RQ1:** Which Python constructs must be excluded to eliminate known failure classes (unhandled exceptions, unbounded recursion, signal races), and can each exclusion be justified the way MISRA C / SPARK justify theirs?
- **RQ2:** How does the proposed toolset (subset → static/type checks → bounded model checking) compare in soundness/completeness to Nagini, ESBMC-Python, and CrossHair?
- **RQ3:** Which DO-178C Level C/D objectives (including DO-333/DO-330) can the subset-plus-toolset realistically support, and which are structurally out of reach for an interpreted, garbage-collected language - as the safety-critical Java precedent suggests?

(RQ4 from the confirmation report is empirical/experimental, not literature-based, so it's out of scope for this SLR.)

## 3. Search Strategy

**Databases:** IEEE Xplore, ACM Digital Library, Scopus, SpringerLink, ScienceDirect. Google Scholar and DBLP for snowballing only.

**Search terms**, combined per topic:

- Query1 - Python AND ("static analysis" OR "abstract interpretation" OR "type inference" OR "gradual typing" OR "type checking" OR "type error")
- Query2 - Python AND ("formal verification" OR "model checking" OR "bounded model checking" OR "symbolic execution" OR "deductive verification" OR "theorem proving" OR contract*)
- Query3 - ("restricted subset" OR "language subset" OR "safe subset" OR "coding standard" OR "coding guideline" OR profile) AND ("safety-critical" OR "high-integrity" OR certification)
- Query4 - (restricted subset OR MISRA OR SPARK) AND (safety-critical OR high-assurance)
- Query5 - ("DO-178" OR "DO-330" OR "DO-333" OR "ED-12" OR "airborne software" OR avionics) AND ("formal method*" OR "tool qualification" OR "static analysis" OR verification OR "programming language")
- Query6 - ("worst-case execution time" OR WCET OR "real-time" OR determinis*) AND ("garbage collection" OR "managed runtime" OR "virtual machine" OR interpreter OR Python OR Java)
- Query7 - safety-critical Java OR SCJ OR JSF AV
- Query8 - Mojo OR Cython OR Nuitka OR PyPy OR Numba OR MicroPython (performance-oriented or restricted Python implementations)

**Date range:** 1995–2026 (earlier foundational sources - e.g. Leveson & Harvey 1983, MISRA/SPARK origins - are pulled in via snowballing, not the date-bound search).

**Also:** backward/forward snowballing from Nagini, ESBMC-Python, CrossHair, and the safety-critical Java papers already identified; manual check of key venues (SAFECOMP, ISSTA, ICSE, DASC).

Each query family will be translated into the exact syntax required by each database and executed accordingly. Search results will be logged in `slr/searches/`. Each database will have its own folder containing the export of each search query. Any deviations from the search queries or conditions defined above will be documented in `prisma_counts.csv`, in the `note` column. The internal structure and level of detail within each file are left to the author’s discretion.

## 4. Search Validation
Before screening begins, the search strategy is validated against a known-item set: the Tier-1 references identified in supervisory guidance of 12 August 2026. A search strategy that fails to retrieve papers known to be in scope and indexed in the searched databases is revised before proceeding.

**Result.** Of the 17 Tier-1 references, 14 were present in the merged search results. All 14 are carried through to the screened set (see Section 6.1). The three absent references — Souyris et al. (2005), Leroy (2009) and Kästner et al. (2026) — were not returned by any database search and enter the review through citation searching, recorded as a separate identification route in the PRISMA flow.

**Search coverage limitation.** Exports from IEEE Xplore are capped at 1,000 records per query. Query5 and Query6 initially hit that cap and were re-exported in batches on 14 September 2026, raising Query6 from 1,000 to 8,251 records and Query5 from 1,000 to 1,513. Two batches, `query6-8.csv` and `query6-9.csv`, each return exactly 1,000 records and so appear to remain at the cap; this is recorded as a residual limitation rather than pursued further, since the re-export added 7,765 records to the corpus but only about two further records per key topic. SpringerLink applied a similar export cap and was retrieved in batches. Coverage of this review is accordingly not claimed to be exhaustive. It is claimed to be documented, reproducible, and validated against a known-item set, with 14 of the 14 known-relevant references present in the searched corpus appearing in the screened set.

## 5. Inclusion / Exclusion

**Inclusion criteria**

A study will be included if it satisfies the following criteria:

* I1 - Publication type: The work is a peer-reviewed research paper, including journal articles, conference papers, or workshop papers. Standards, regulatory guidance, and Python Enhancement Proposals (PEPs) will be retained in a separate reference pool and are not required to be peer-reviewed.
* I2 - Publication period and language: The work was published between 1995 and 2026 and is available in English.
* I3 - Technical relevance: The work directly addresses Python runtime behaviour, verification, static or dynamic analysis, language subsetting, or a comparable dynamic programming language.
* I4 - Safety and verification relevance: The work addresses safety-critical software, formal methods, verification, restriction of language features, or the feasibility of a safety-oriented toolchain.
* I5 - DO-178C and related relevance: The work directly addresses, evaluates, or provides evidence relevant to DO-178C, DO-330, DO-333, or objectives and practices applicable to airborne safety-critical software. Relevant DO-178C, DO-330, DO-333, and PEP documents will be retained in the separate reference pool to support the interpretation of the included studies.

**Exclusion criteria**

A candidate will be excluded if any of the following criteria apply:

* E1 - Publication type: The work is marketing material, an opinion piece, presentation, blog post, or other non-research material without a substantive methodology.
* E2 - Language or date: The work is not available in English or was published outside the 1995--2026 period.
* E3 - Insufficient technical relevance: The work does not address Python, a comparable dynamic language, verification, language restriction, or a relevant formal-methods approach.
* E4 - Insufficient safety/verification relevance: The work is focused solely on general-purpose performance, programming productivity, or language features without relevance to safety, verification, restriction, or toolchain feasibility.
* E5 - Duplicate or superseded work: The work is a duplicate or superseded version of another included study. Where multiple versions exist, the most complete or recent version will be retained.
* E6 - Books: including text books or book chapers. Such works are typically do not undergo the same peer-review process as journal articles or conference papers, and their content can vary substantially across editions, making the specific claims difficult to verify or trace to a fixed version.
* E8 - List of`"exclude-keywords"`defined in the automated extraction tools.

## 6. Screening

### 6.1 Construction of the screening set

The database searches returned a corpus too large to screen exhaustively. Records were deduplicated by DOI, and by normalised title where no DOI was present, reducing 58,496 raw records to 49,635 unique records. Because the exports carry abstracts for only about 14% of records — the Scopus export contains no abstract field — abstracts were additionally retrieved from OpenAlex by DOI, raising abstract coverage of the screening set to 87% and of the full corpus to 30%.

Each record was then scored against five topic facets drawn from the research questions: Python and its implementations; verification and static analysis; certification standards and safety-critical software; runtime, memory and timing behaviour; and restricted language subsets and comparator languages. The subject of this review is the intersection of these areas, so a record connecting two or more facets is treated as a candidate. A small set of terms specific enough to warrant inclusion alone (for example DO-178C, MISRA, WCET, CompCert, JSR-302) is treated as sufficient on its own, and explicit compound rules capture intersections that a distinct-facet count cannot see — "hard real-time garbage collection", for instance, matches the runtime facet twice rather than two facets. Off-topic signals demote a record by one band but never remove it, so that a relevant paper which merely mentions an excluded topic is retained.

Records are assigned to bands: band 1 (strong term, compound match, or two or more title facets), band 2 (one title facet corroborated by the abstract, or Python in the title with corroboration), band 3 (Python in the title without corroboration), band 4 (a single facet, no corroboration) and band 5 (no topical facet). Bands 1 and 2 form the screening set of 3,709 records (band 1, 1,769; band 2, 1,940); band 3 (775 records) is screened as time permits; band 4 (14,562 records) is retained and sampled to estimate what the rule misses; band 5 (30,589 records) is excluded.

This rule contains no hard-coded list of known papers, so validation against the Tier-1 set is a measurement rather than a restatement. All 14 Tier-1 references present in the corpus fall in band 1. A further nine references held out from the design of the rule fall in bands 1 to 3, seven of them within the screening set and two in the optional band. Key-topic recall in the screened set is 108/108 for worst-case execution time, 55/55 for the DO-178 family, 12/12 for MISRA, 10/10 for tool qualification and 41/43 for MC/DC and structural coverage.

An earlier keyword-whitelist filter (retained, superseded, under `slr/searches/filter/`) was replaced because a whitelist discards any topic not named in advance: measured against the 50,731-record corpus it was run on, it retained 1 of 107 worst-case execution time records and none of the 60 concerning memory management. Its Tier-1 check did not detect this, because the Tier-1 titles were themselves hard-coded into a must-keep list and so bypassed the filter.

The screening set, the held and excluded sets, and the method note are under `slr/screening/`. `slr/tools/build_screening_set.py` reproduces all four files from `slr/searches/filter/searches.csv` in a single pass using only the standard library.

### 6.2 Screening procedure

Titles and abstracts will be screened first to exclude clearly irrelevant papers. The included studies will then be assessed using a two-tier reading strategy.  **Core comparator studies** , including key approaches such as Nagini, ESBMC-Python, Monat, Fromherz, RPython, CrossHair, PyVeritas, and the CompCert qualification work, will be read in full because the detailed extraction fields required for this review cannot reliably be recovered from abstracts or selected sections alone. For all other studies, the methods, results/evaluation, and conclusion sections will be reviewed to make the include/exclude decision. Papers with an unclear or ambiguous fit will be read in full before a final decision is made.

Given the 1.5-month timeframe, this targeted-reading approach is an explicit limitation of the review. Every screening decision (include/exclude, with reason) is recorded in the `decision`, `criterion` and `notes` columns of `slr/screening/SCREEN_bands1-2.csv`, which serves as the screening log.  A supervisor or second reviewer will independently check a sample of approximately 20% of screening decisions, with disagreements resolved through discussion.

## 7. Data Extraction

For each included paper, data will be extracted using a predefined extraction schema and recorded in `slr/extraction.csv`, with one row per included study. The schema will capture the following information:

* Bibliographic information: authors, title, publication year, venue, and DOI or other persistent identifier where available.
* RQ mapping: the research question(s) (RQ1--RQ3) informed by the study and the evidence relevant to each RQ.
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

## 8. Synthesis

Papers will be grouped by verification approach (type-based, model checking, symbolic execution, language subsetting) and compared across groups against RQ1–RQ3.
