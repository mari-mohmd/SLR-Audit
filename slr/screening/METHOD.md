# Screening-set construction — method note

Prepared 13 September 2026; revised 15 September 2026. Input:
`slr/searches/filter/searches.csv` from the SLR-Audit repository — the merged export of all five
database searches, **58,496 records**.

IEEE Queries 5 and 6 were re-exported in batches on 14 September to recover records lost to the
1,000-record export cap (Query 6 rose from 1,000 to 8,251 records, Query 5 from 1,000 to 1,513).
All figures in this note reflect the corpus after that re-export. The comparison against the
superseded keyword filter in the next section is the exception, and is marked accordingly.

## Why this replaces the keyword filter

The `apply_filter.py` whitelist kept a record only if its **title** matched one of ~46
include keywords, and dropped it if the title matched any of ~110 exclude keywords. A
whitelist silently discards anything nobody thought to name in advance. Measured against the
13 September corpus of 58,496 records — the one the filter was actually run on — it removed:

| Topic (title match)              | In corpus | Kept by whitelist |
| -------------------------------- | --------- | ----------------- |
| WCET / worst-case execution time | 107       | 1                 |
| Garbage collection               | 186       | 1                 |
| Memory management                | 60        | 0                 |
| MC/DC or structural coverage     | 42        | 6                 |
| Tool qualification               | 9         | 2                 |
| DO-178 / DO-330 / DO-333         | 53        | 34                |

The Tier-1 validation could not detect this because `config.json` hard-codes the 17 Tier-1
titles in an `include-papers` must-keep list — they bypass the filter, so they survive by
construction and tell you nothing about how it treats everything else.

## Method used here

1. **Deduplication.** By DOI where present, else by normalised title (case, punctuation and
   diacritics stripped). 58,496 → 49,635 unique records. Where duplicates differed, the record
   carrying the most metadata was retained.
2. **Facet scoring.** Each record's title — plus abstract and keywords where the export
   provides them (30% of records after retrieval; the Scopus export carries no abstracts) — is
   matched against five topic facets:

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

The exports carried abstracts for only about 14% of records — the Scopus export has no abstract
field at all. Abstracts were retrieved from OpenAlex by DOI for records lacking them, giving a
cache of 839. Abstract coverage is **87% across the screening set** (3,221 of 3,709) and 30%
across the full deduplicated corpus, so most records can be screened on title *and* abstract
rather than title alone.

## Output

| File                          | Records | What it is                                                                                                                                                                                                |
| ----------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SCREEN_bands1-2.csv`       | 3,709   | **Screen these.** Band 1 (1,769) first — strong term, compound match, or two-plus title facets. Then band 2 (1,940) — one title facet corroborated by the abstract, or Python plus corroboration. |
| `SCREEN_band3_optional.csv` | 775     | Python in the title without corroboration. Screen if time allows — see the recall trade-off below.                                                                                                       |
| `HELD_band4.csv`            | 14,562  | Single facet, no corroboration. Sample ~200 to estimate what the rule misses.                                                                                                                             |
| `EXCLUDED_band5.csv`        | 30,589  | No topical facet in any available field.                                                                                                                                                                  |

Each screening file carries empty `decision`, `criterion` and `notes` columns for the screening
record, and the abstract inline so nothing needs to be looked up separately.

## Where to stop — measured

| Screened    | Records | Tier-1 recall | Held-out recall |
| ----------- | ------- | ------------- | --------------- |
| Band 1 only | 1,769   | 14/14         | 4/9             |
| Bands 1–2  | 3,709   | 14/14         | 7/9             |
| Bands 1–3  | 4,484   | 14/14         | 9/9             |

Band 1 alone is not safe: it loses Vitousek, Behnel, Di Grazia, Stoico and Monat's SOAP paper.
Bands 1–2 loses only Vitousek (gradual typing) and Behnel (Cython), both of which are heavily
cited by the Tier-1 set and would be recovered by the backward snowballing the protocol already
requires. **Bands 1–2 plus snowballing is the recommended stopping point**; bands 1–3 if time
allows.

Key-topic recall at the bands 1–2 cut: worst-case execution time 108/108, DO-178 family 55/55,
MISRA 12/12, tool qualification 10/10, MC/DC and structural coverage 41/43, safety-critical Java
89/97, garbage collection 108/214 and memory management 42/66 (the remainder in those last two
being database, distributed and allocator work with no timing or managed-runtime angle).

## What still needs doing

- The three missing Tier-1 papers (Souyris WCET 2005, Leroy 2009, Kästner ERTS 2026) enter
  through a separate PRISMA "identified via other methods" arm, recorded as citation searching
  — not inserted into the corpus without provenance.
- `prisma_counts.csv` currently records export sizes rather than the hit counts the database
  interfaces reported, and has not been updated for the 14 September re-export.
- Two IEEE batches, `query6-8.csv` and `query6-9.csv`, each contain exactly 1,000 records and so
  appear to remain at the export cap. This is recorded as a limitation; no further re-export is
  planned, since the 14 September re-export added 7,765 records to the corpus but only about two
  further records per key topic (worst-case execution time 107 → 108, DO-178 family 53 → 55).
- Abstracts are absent for 70% of the full corpus, though only 13% of the screening set.
  Re-exporting Scopus with abstracts would close most of the remainder.

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
