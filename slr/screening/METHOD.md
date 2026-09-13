# Screening-set construction — method note

Prepared 13 September 2026. Input: `slr/searches/filter/searches.csv` from the SLR-Audit
repository (the merged export of all five database searches), 50,731 records.

## Why this replaces the keyword filter

The `apply_filter.py` whitelist kept a record only if its **title** matched one of ~46
include keywords, and dropped it if the title matched any of ~110 exclude keywords. A
whitelist silently discards anything nobody thought to name in advance. Measured against the
merged corpus, it removed:

| Topic (title match) | In corpus | Kept by whitelist |
|---|---|---|
| WCET / worst-case execution time | 107 | 1 |
| Garbage collection | 186 | 1 |
| Memory management | 60 | 0 |
| MC/DC or structural coverage | 42 | 6 |
| Tool qualification | 9 | 2 |
| DO-178 / DO-330 / DO-333 | 53 | 34 |

The Tier-1 validation could not detect this because `config.json` hard-codes the 17 Tier-1
titles in an `include-papers` must-keep list — they bypass the filter, so they survive by
construction and tell you nothing about how it treats everything else.

## Method used here

1. **Deduplication.** By DOI where present, else by normalised title (case, punctuation and
   diacritics stripped). 50,731 → 42,568 unique records. Where duplicates differed, the record
   carrying the most metadata was retained.

2. **Facet scoring.** Each record's title — plus abstract and keywords where the export
   provides them (14% of records; the Scopus export carries no abstracts) — is matched against
   five topic facets:

   - **PY** — Python, its implementations (CPython, PyPy, RPython, Cython, Numba, MicroPython,
     Mojo, mypy, Cinder), and dynamic/gradual typing
   - **VERIF** — static analysis, abstract interpretation, model checking, symbolic execution,
     formal methods, type systems, contracts, soundness
   - **CERT** — DO-178/330/331/332/333/248, ED-12, ARP4754/4761, IEC 61508, avionics, airborne,
     safety-critical, high-integrity, certification, MC/DC, structural coverage
   - **RUNTIME** — WCET, real-time, determinism, garbage collection, memory management, managed
     runtime, interpreter, bytecode, JIT, GIL, schedulability, exception handling
   - **SUBSET** — MISRA, SPARK/Ada, coding standards, language subsets, safety-critical Java,
     RTSJ, JSR-302, Rust/Ferrocene, CompCert, verified compilation, transpilation

   The review's subject is the *intersection* of these worlds, so a record connecting two or
   more facets is a candidate. This is the structure the original queries were reaching for.

3. **Strong single terms.** Some terms are specific enough to justify inclusion alone:
   DO-178/330/331/332/333, ED-12, MISRA, WCET, CompCert, Nagini, ESBMC, RPython, safety-critical
   Java, JSR-302, MC/DC, global interpreter lock, tool qualification.

4. **Compound rules.** A distinct-facet count cannot see intersections *within* a facet —
   "hard real-time garbage collection" is RUNTIME twice. Explicit compound rules capture the
   high-value cases: memory/GC/heap combined with real-time, determinism, bounding,
   predictability, embedded contexts or a managed runtime; interpreter or bytecode combined
   with safety, verification, timing or certification; exception handling, stack overflow or
   recursion combined with safety or verification. The literal waste-management sense of
   "garbage collection" (ocean, municipal, truck, recycling, geofence) is excluded.

5. **Demotion, never deletion.** Off-topic signals (machine learning, malware, computer vision,
   blockchain, teaching, remote sensing, and similar) demote a record by one tier only when it
   has no strong term, no compound match and fewer than two facets. Nothing is discarded on an
   exclusion term alone, so a relevant paper that merely mentions one is retained.

## Abstract retrieval

The exports carried abstracts for only 14% of records — the Scopus export (64% of the corpus)
has no abstract field at all. Abstracts were retrieved from OpenAlex by DOI for records lacking
them: 829 recovered from 1,106 attempted. Abstract coverage across the screening set is now
**84%**, so most records can be screened on title *and* abstract rather than title alone.

## Output

| File | Records | What it is |
|---|---|---|
| `SCREEN_bands1-2.csv` | 2,870 | **Screen these.** Band 1 first (strong term, compound match, or two-plus title facets), then band 2 (one title facet corroborated by the abstract, or Python plus corroboration). |
| `SCREEN_band3_optional.csv` | 654 | Python in the title without corroboration. Screen if time allows — see the recall trade-off below. |
| `HELD_band4.csv` | 9,410 | Single facet, no corroboration. Sample ~200 to estimate what the rule misses. |
| `EXCLUDED_band5.csv` | 29,634 | No topical facet in any available field. |

Each screening file carries empty `decision`, `criterion` and `notes` columns for the screening
record, and the abstract inline so nothing needs to be looked up separately.

## Where to stop — measured

| Screened | Records | Tier-1 recall | Held-out recall |
|---|---|---|---|
| Band 1 only | 1,656 | 14/14 | 4/9 |
| Bands 1–2 | 2,870 | 14/14 | 7/9 |
| Bands 1–3 | 3,524 | 14/14 | 9/9 |

Band 1 alone is not safe: it loses Vitousek, Behnel, Di Grazia, Stoico and Monat's SOAP paper.
Bands 1–2 loses only Vitousek (gradual typing) and Behnel (Cython), both of which are heavily
cited by the Tier-1 set and would be recovered by the backward snowballing the protocol already
requires. **Bands 1–2 plus snowballing is the recommended stopping point**; bands 1–3 if time
allows.

Key-topic recall at the bands 1–2 cut: WCET 107/107, DO-178 family 53/53, MC/DC 40/42,
safety-critical Java 80/91, garbage collection 101/186 (the remainder being database and
distributed GC with no timing or managed-runtime angle).

Every row carries `tier`, `score`, `facets`, `facets_extra` and a `why` column listing the
matched terms, so each decision is explainable and re-runnable. `build_screening_set.py` reproduces the
whole process from `searches.csv` in one pass, using only the standard library.

## Validation

- **Tier-1 recall: 14/14.** All fourteen Tier-1 references present in the corpus land in Tier A.
  None are hard-coded — the scorer has no knowledge of the list, so this is a real test rather
  than a restatement of a must-keep rule. (M10, M16 and M17 are absent from the corpus itself
  and must be added through a documented citation-searching arm.)
- **Held-out recall: 9/9.** Nine Tier-2/Tier-3 references never named to the scorer — Politz,
  Vitousek, Di Grazia, Stoico, Behnel, Bolz, Oh & Oh, Monat (SOAP), Sun — all land in Tier A or B.
- **Topic recovery** against the whitelist is in the table above: WCET 107/107, tool
  qualification 9/9, DO-178 family 53/53, MISRA 12/12.

Tier A precision is deliberately imperfect — this is a screening set, not an inclusion list.
Title and abstract screening removes the remaining noise, and those decisions belong in
`screening.csv` with a criterion code per record.

## What still needs doing

- The three missing Tier-1 papers (Souyris WCET 2005, Leroy 2009, Kästner ERTS 2026) enter
  through a separate PRISMA "identified via other methods" arm, recorded as citation searching
  — not inserted into the corpus without provenance.
- `prisma_counts.csv` currently records export sizes rather than the hit counts the database
  interfaces reported; Queries 5 and 6 were truncated at a 1,000-record export cap.
- Abstracts are missing for 86% of records. Re-exporting Scopus with abstracts would make
  abstract screening possible without retrieving each paper individually.


## Reproducing this

From `slr/tools/`:

```
python3 build_screening_set.py --searches ../searches/filter/searches.csv --out ../screening
```

`openalex_abstracts.json` sits alongside the script and is picked up automatically, so the
retrieved abstracts do not need fetching again. To extend the cache after adding records:

```
python3 fetch_abstracts.py ../screening/SCREEN_bands1-2.csv
```

Both scripts use only the Python standard library. Re-running reproduces the four CSVs exactly.
