Systematic Literature Review Protocol

## Python for DO-178C-Compliant Airborne Software: Restricted Subset and Verification Toolset

**Version:** 1.4 | **Author:** Mohammad Mari | **Supervisors:** Dr. Lian Wen & Qinyi Li |  **Assessor:** Prof. Rene Hexel |  **Affiliation:** Griffith University | **Date:** 2026-09-15 (amended 2026-11-22, see §2.1, §3, §4, §6 and §7)

---

## 1. Purpose of the SLR

This SLR is being conducted to address the review comments raised at the confirmation seminar, specifically: (1) insufficient depth/breadth of literature supporting the thesis's claims, (2) the need to revise and strengthen the research questions in light of that literature, and (3) the need for a traceable record of how and why the confirmation report is being amended in response to these comments.

## 2. Research Questions

### 2.0 Thesis research questions (version 1.3)

The questions below are the research questions of the PhD thesis, taken from the confirmation report. Up to version 1.3 this protocol used them directly as the review questions, so the search and screening were designed against them. They remain the thesis questions; this amendment does not change them.

- **Thesis RQ1:** Which Python constructs must be excluded to eliminate known failure classes (unhandled exceptions, unbounded recursion, signal races), and can each exclusion be justified the way MISRA C / SPARK justify theirs?
- **Thesis RQ2:** How does the proposed toolset (subset → static/type checks → bounded model checking) compare in soundness/completeness to Nagini, ESBMC-Python, and CrossHair?
- **Thesis RQ3:** Which DO-178C Level C/D objectives (including DO-333/DO-330) can the subset-plus-toolset realistically support, and which are structurally out of reach for an interpreted, garbage-collected language - as the safety-critical Java precedent suggests?

(Thesis RQ4 from the confirmation report is empirical/experimental, not literature-based, so it is out of scope for this SLR.)

### 2.1 Amendment, 22 November 2026: review questions for the SLR

The thesis questions concern the thesis's own proposed subset and toolset, and the literature cannot answer them directly. The SLR therefore answers its own review questions. Each supplies the literature evidence that one or more thesis questions need:

| SLR review question | Evidence it supplies for |
|---|---|
| **RQ1:** How has research on Python verification developed over time? | Context for all thesis RQs |
| **RQ2:** What tools exist for verifying Python correctness, and what guarantees do they provide? | Thesis RQ2 (the comparators Nagini, ESBMC-Python, CrossHair and others) |
| **RQ2a:** Which Python constructs do existing subsets and verifiers exclude or ban, and on what grounds? Can each exclusion be justified the way MISRA C and SPARK justify theirs? | Thesis RQ1 and the coding guidelines |
| **RQ3:** How have interpreted and managed-runtime languages, such as Java, been adapted for safety-critical use? | Thesis RQ3 (the safety-critical Java precedent) |
| **RQ4:** What challenges remain before Python can meet safety-critical certification requirements? | Thesis RQ3 (attainable and out-of-reach DO-178C objectives) |

Ada and C are not treated as comparators under RQ3, because they are compiled ahead of time and have no managed runtime. Their literature, together with the safety-standard, coverage, WCET and tool-qualification literature, is reference material for RQ4.

**Effect on screening.** Nothing is re-screened. The screening prompts in `slr/tools/` were written against the thesis research questions in §2.0. They are kept unaltered as the record of what was run. The inclusion and exclusion criteria (§5) did not change, and the review questions cover the topics of the thesis questions, so the screening and its verification stand. A study relevant only to the review questions could have been screened out; this is reported as a limitation.

## 3. Search Strategy

**Databases:** IEEE Xplore, ACM Digital Library, Scopus, SpringerLink, ScienceDirect.

**Search terms**, combined per topic:

- Query1 - Python AND ("static analysis" OR "abstract interpretation" OR "type inference" OR "gradual typing" OR "type checking" OR "type error")
- Query2 - Python AND ("formal verification" OR "model checking" OR "bounded model checking" OR "symbolic execution" OR "deductive verification" OR "theorem proving" OR contract*)
- Query3 - ("restricted subset" OR "language subset" OR "safe subset" OR "coding standard" OR "coding guideline" OR profile) AND ("safety-critical" OR "high-integrity" OR certification)
- Query4 - (restricted subset OR MISRA OR SPARK) AND (safety-critical OR high-assurance)
- Query5 - ("DO-178" OR "DO-330" OR "DO-333" OR "ED-12" OR "airborne software" OR avionics) AND ("formal method*" OR "tool qualification" OR "static analysis" OR verification OR "programming language")
- Query6 - ("worst-case execution time" OR WCET OR "real-time" OR determinis*) AND ("garbage collection" OR "managed runtime" OR "virtual machine" OR interpreter OR Python OR Java)
- Query7 - safety-critical Java OR SCJ OR JSF AV
- Query8 - Mojo OR Cython OR Nuitka OR PyPy OR Numba OR MicroPython (performance-oriented or restricted Python implementations)

**Date range:** 1995–2026. This is the scope of the review. Earlier sources are not sought.

**Snowballing.** Not performed at this stage (amendment of 22 November 2026). Earlier versions of this protocol planned backward and forward snowballing and a manual check of key venues. Both were removed, and the absence of snowballing is reported as a limitation of the review. The only records added outside the database searches are the known-item references in §4 that no database returned.

Each query family will be translated into the exact syntax required by each database and executed accordingly. Search results will be logged in `slr/searches/`. Each database will have its own folder containing the export of each search query. Any deviations from the search queries or conditions defined above will be documented in `prisma_counts.csv`, in the `note` column. The internal structure and level of detail within each file are left to the author’s discretion.

## 4. Search Validation
Before screening begins, the search strategy is validated against a known-item set: the Tier-1 references identified in supervisory guidance of 12 August 2026. A search strategy that fails to retrieve papers known to be in scope and indexed in the searched databases is revised before proceeding.

**Result.** Of the 17 Tier-1 references, 14 were present in the merged search results. All 14 are carried through to the screened set (see Section 6.1). The three absent references — Souyris et al. (2005), Leroy (2009) and Pister, Kästner et al. (2026) — were not returned by any database search. They enter the review as an "identified via other methods" route in the PRISMA flow, each with its reason:

| Reference | Why no database search returned it |
|---|---|
| Souyris et al. (2005), *Computing the worst case execution time of an avionics program by abstract interpretation*, 5th International Workshop on WCET Analysis (WCET 2005) | Workshop proceedings that none of the five databases indexes |
| Leroy (2009), *Formal verification of a realistic compiler*, CACM 52(7) | Indexed by ACM, but its title and abstract use none of the query terms on safety, certification, Python or runtimes, so no query family matches it |
| Pister, Kästner et al. (2026), *Qualifying CompCert for safety-critical avionics software*, ERTS 2026, doi:10.82331/ERTS.2026.35 | ERTS proceedings are not indexed by the five databases (the paper is open access on HAL, hal-05513825) |

All three full texts were retrieved on 22 November 2026; they are assessed and extracted as core studies (IDs C01–C03 in `slr/extraction.csv`).

RPython (Ancona et al., 2007) is a known item that the database searches did return (record 494 in `INCLUDED_final.csv`). It is therefore not added through this route, because that would count it twice.

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
There is no E7, and the former E8 — "list of exclude-keywords defined in the automated extraction
tools" — has been removed. It referred to the keyword-whitelist filter described and superseded in
§6.1, and a keyword blacklist is the failure mode the screening procedure replaces: measured against
the corpus it was run on, that filter retained 1 of 107 worst-case execution time records and none of
the 60 concerning memory management. E8 was never recorded against a screening decision, so its
removal invalidates no logged decision. The screening prompts kept in `slr/tools/` were written while
E8 still stood and state that it is deliberately not applied; they are retained unaltered as the
record of what was actually run.

**Interpretation of the criteria**

The criteria above state what is in scope; the following rules settle the cases where two of them
appear to conflict. They were added after a validated screening pilot in which each had caused a
known-relevant paper to be misclassified, and they change how the criteria are read, not which
criteria apply. Codes I1-I5 and E1-E6 are unchanged, so decisions already logged under them remain
valid.

* **Timing and execution-model evidence (I3 against E4).** General benchmarking — throughput,
  speedup, productivity comparisons — is general-purpose performance and E4 applies. Evidence about
  *timing determinism in a language runtime*, however, is central to RQ3 and is included under I3
  whether or not the work mentions safety or certification: worst-case execution time,
  schedulability, deadlines, task periodicity, interrupt response, jitter, garbage-collection pauses
  and the global interpreter lock, considered as properties of an interpreter, virtual machine, JIT
  or managed runtime. The boundary is the level of the claim. Timing predictability obtained from
  hardware or microarchitecture — cache organisation and cache-behaviour prediction, pipelines,
  branch prediction, memory controllers, processor and multi-core architecture, hardware-assisted
  collection — does not inform RQ1-RQ3 and remains excluded under E4, despite sharing the WCET and
  real-time vocabulary. What matters is whether the work tells us what a *language runtime* does
  rather than what a processor does.
* **Restriction irrespective of motive (I3 against E4).** A work that defines, implements or
  analyses a restricted subset of a dynamic language, or renders one statically typed or statically
  analysable, satisfies I3 even where the restriction was motivated by compilation, performance or
  interoperability rather than by safety. The motivation for a subset does not change the evidence
  it provides about what such a subset can be, which is the question RQ1 asks.
* **Publication type is presumed (I1, E1, E6).** I1 and I2 are treated as satisfied unless
  something in the record positively indicates otherwise — a venue naming a book, textbook or
  preprint server, or a title that is plainly marketing, editorial or a blog post. Missing, empty or
  uninformative metadata is not evidence of non-peer-reviewed material. The venue field is evidence
  for publication *type* only: it must play no part in judging relevance, so a workshop paper and a
  journal article are assessed identically. This matters at scale, because 488 records in the
  screening set carry no abstract while only 11 of those also lack venue information; treating thin
  metadata as disqualifying would have discarded the rest on a technicality.

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

**Relevance scoring and the first screening pass.** Because the screening set is too large to read
exhaustively, the title/abstract pass records a relevance score from 0 to 5 alongside the
include/exclude decision, so that the included set can be ordered rather than merely partitioned. A
5 presents or evaluates a verification, static-analysis, type-system or language-subsetting
technique for Python or another dynamically typed language, or establishes directly whether a given
DO-178C objective is attainable for such a language; a 4 applies those techniques to a statically
typed language used here as precedent (Ada/SPARK, safety-critical Java, MISRA C, Rust), or reports
industrial experience of formal methods or tool qualification under DO-178C; lower scores record
progressively weaker connections to the research questions.

The decision and the score must be consistent: a record scored 4 or 5 is an include, and a record
scored 0 or 1 is not, so that an exclusion can never be recorded against a paper simultaneously
judged highly relevant. Scores of 2 and 3 straddle the threshold and may fall either way; these are
retained as a borderline band for a second pass rather than being decided on a single reading,
because repeat screening of the same records agreed on 92% of decisions overall (Cohen's kappa
0.81) with essentially all disagreement concentrated at this 2-3 boundary. Agreement was no lower
for records lacking abstracts (90%) than for those carrying them (92%).

Given the 1.5-month timeframe, this targeted-reading approach is an explicit limitation of the review. Every screening decision (include/exclude, with reason) is recorded in the `decision`, `criterion` and `notes` columns of `slr/screening/SCREEN_bands1-2.csv`, which serves as the screening log.  A reviewer verifies a stratified sample of 60 screening decisions — 30 drawn from the included set and 30 from the excluded — presented one record per page with its title, venue, keywords and abstract, followed by the decision, criterion, relevance and recorded reasoning for each round that applied to it. For each record the reviewer states whether they agree with the final decision. Agreements are not recorded individually; the review reports how many of the 60 decisions were disputed and the grounds for each dispute. `slr/tools/make_verification_pack.py` builds the pack and `slr/tools/summarise_verification.py` summarises the responses.

Agreement and Cohen's kappa are computed from the responses, a disagreement on an included record being taken as a judgement to exclude it and vice versa, and are reported together with the design that produced them. This is a verification of the screening rather than an independent second screen, and two features of it raise the coefficient above what an independent check would give: the reviewer is shown each decision and its reasoning before judging it, so the two readings are not independent; and the sample is stratified in equal halves, so the screening's marginal is 50% here rather than its true 23% include rate, which alters the chance correction. The kappa is accordingly reported as an upper bound, and the substantive result is the count of disputed decisions and the grounds given for them. What the sample establishes is whether a human reader, given the evidence the screening had, endorses its decisions and where it departs from their judgement. It was chosen over a blind re-screen deliberately: judging 60 records blind from a spreadsheet is not work a person can do attentively, and an inattentive blind screen measures fatigue rather than agreement.

The sample is stratified rather than random so that exclusions are checked as closely as inclusions. Only about 23% of screened records are included, so a random sample of this size would contain few inclusions and would leave the decision most consequential for the review — to discard a record — largely unexamined. An earlier version of this protocol specified an independent check of approximately 20% of decisions, which at 3,709 screened records is 742 and was not achievable within the candidature timeframe. Where verification disputes a decision on grounds that implicate a criterion rather than a single record, the criterion is revised and the affected records re-screened, as was done during the development of the automated pass.

**Outcome of the verification (amendment, 22 November 2026).** The reviewer disputed 4 of the 60 decisions (93% agreement, kappa 0.87 as an upper bound); the responses and reasons are in `slr/screening/VERIFY_60_response.csv`. The sample measures the reliability of the screening and is not a re-screen, so individual decisions in the sample are not changed on the strength of a single disputed record. Three disputes are boundary judgements on single records: two inclusions judged to concern security rather than safety (smart-card security certification; MISRA C compliance of open-source RTOSs framed as secure coding) and one inclusion judged unsound and hard to qualify (LLM-based type inference for Python), which the extraction records through its guarantee level. The fourth, the exclusion of restart-based fault tolerance (record 59), implicates a criterion rather than a record: it raises whether architectural containment of unverified components is in scope. It is handled under the rule above as a scope decision (§7), and the affected records are re-screened once that decision is made.

## 7. Data Extraction

For each included paper, data will be extracted using a predefined extraction schema and recorded in `slr/extraction.csv`, with one row per included study. The schema will capture the following information:

* Bibliographic information: authors, title, publication year, venue, and DOI or other persistent identifier where available.
* RQ mapping: the SLR review question(s) (RQ1--RQ4, including RQ2a; §2.1) informed by the study and the evidence relevant to each RQ.
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

* Quality assessment (five items, each scored 1, 0.5 or 0): QA1 the technique is evaluated, not only proposed; QA2 the main claim is substantiated (proved or demonstrated); QA3 the evaluation is at realistic scale; QA4 an artefact is available; QA5 the venue is peer reviewed. The total (0–5) qualifies the synthesis and is not used to exclude studies.

Where a field is not reported or cannot be determined from the paper, it will be recorded as NR (not reported) rather than inferred.

**Depth and order of extraction (amendment, 22 November 2026).**
1. Papers that define or impose a language subset come first. These are core papers, and precedent papers on MISRA, SPARK, Ravenscar, SCJ and similar profiles. Only the subset fields are extracted at this step: restrictions, rationale for each, excluded features with their reason, and the failure class each exclusion targets. These answer RQ2a.
2. The remaining core papers (relevance 5) are then extracted on all fields above, from the full text.
3. The precedent papers (relevance 3–4) get a short row: bibliographic fields, RQ mapping, role (Python tool or empirical study, managed runtime, or reference standard), language, tool, approach, guarantee, a one-sentence finding and a verbatim quote.

Records in an area whose scope is under review are not extracted until the scope is decided. The area of verification record 59 (architectural containment, runtime assurance and restart-based designs) is one such area, pending the supervisory decision of 27 November 2026.

**AI assistance.** Extraction is assisted by a large language model, which works under written instructions: every field must come from the paper text, unreported fields are recorded as NR, and each finding is backed by a verbatim quote that is checked automatically against the source. A human reviewer verifies a stratified sample of rows and records the result in `verified_by` and `verification_notes`. People resolve all disagreements.

## 8. Synthesis

Papers will be grouped by verification approach (type-based, abstract interpretation, deductive, model checking, symbolic execution, testing and runtime checking, language subsetting and translation). For the core papers, a matrix sets each approach against property class, soundness, trusted computing base, developer burden and DO-178C relevance (RQ2). Construct exclusions and their rationale are tabulated against the failure classes they target, alongside MISRA C, SPARK and SCJ (RQ2a). Publication counts are given as a timeline, normalised against the size of the searched corpus in each year (RQ1). The managed-runtime precedent is synthesised by adaptation dimension (RQ3). RQ4 states three to five gaps, each traceable to rows of the extraction table.
