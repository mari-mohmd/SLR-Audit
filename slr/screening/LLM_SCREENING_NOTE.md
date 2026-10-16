# LLM-assisted screening: what was run, and what it is worth

This note documents the automated title/abstract screening of the 3,709-record screening set. It
records the limitations as well as the results, because several of them bear directly on how the
output files may be used.

## Why an automated pass

The screening set is too large to read exhaustively within the candidature timeframe, and the
keyword-whitelist filter it replaced discarded relevant topics not named in advance: measured
against the corpus it was run on, that filter retained 1 of 107 worst-case execution time records
and none of the 60 concerning memory management (see protocol §6.1). An LLM pass judges each record
against the protocol's criteria rather than against a word list.

Each record is screened in a separate API call with no conversational history, so no record can
influence the judgement of another. The prompt is derived from protocol §2 and §5 and contains no
paper-specific content: no titles, authors or known-item lists. This is what makes the known-item
check below a measurement rather than a restatement.

## The three passes

| pass | records | prompt (sha256 prefix) | output |
|---|---|---|---|
| 1. screening | 3,709 | `screening_prompt.md` b388a04df2664fb4 | `LLM_SCREEN_full_gpt-6-luna.csv` |
| 2. borderline adjudication | 645 | `screening_prompt_pass2.md` 3ab267be315a8306 | `LLM_SCREEN_pass2_gpt-6-luna.csv` |
| 3. rescore of the included set | 945 | `screening_prompt_rescore.md` dba37f55038ccfda | `LLM_RESCORE_includes_gpt-6-luna.csv` |

Model `gpt-6-luna` throughout; zero API or parse failures in all three passes. Pass 1 took 43
minutes, the whole pipeline including pilots cost approximately US$5.50.

Pass 1 asks whether a record meets the inclusion criteria. Pass 2 asks a different and sharper
question of the borderline records — whether a full-text reading would fill any field of the §7
extraction schema in a way bearing on RQ1-RQ3. Pass 3 applies that same question to every included
record, so that the set can be ordered. No pass is shown any earlier verdict or score: anchoring a
re-reading on the reading it is meant to check would make the comparison meaningless.

Decisions: 823 include at pass 1; pass 2 promoted 164 and demoted 42, giving 945; pass 3 dropped a
further 94, giving **851 included records**.

## Validation

**Known items.** 14 Tier-1 references present in the corpus were forced into the pilot samples (this
affects which records are screened, never how they are judged). Recall rose from 10/14 to 13/14
across four prompt revisions, and reached **14/14** after pass 2. Each revision fixed a criterion
that had been misread, never a paper: the three resulting clarifications are recorded in protocol §5
under "Interpretation of the criteria". The surviving difficulty is RPython, whose abstract
discusses only CLI/JVM interoperability and never mentions restriction or subsets; it is relevant
because RPython *is* a restricted subset, which is knowledge not present in the title or abstract.
Records of this kind cannot be recovered by title/abstract screening at all and are brought in by
backward snowballing from the included set instead.

**Repeat agreement.** Screening the same 100 records twice with an identical prompt agreed on 92% of
decisions (Cohen's kappa 0.81). Agreement was no lower for records without abstracts (90%) than with
(92%), so missing abstracts are not the source of instability. Essentially all disagreement fell at
relevance 2-3, which is why that band was re-read in pass 2.

**Key-topic retention** (title+abstract matching, pass 1 → merged): MC/DC and structural coverage
95% → 93%, tool qualification 77% → 71%, safety-critical Java 60% → 65%, MISRA 50% → 59%, DO-178
family 66% → 61%, Python 9% → 15%, WCET 16% → 17%. The fall in the DO-178 family is intended: pass 2
demoted certification *process* studies, which protocol §5 excludes.

## Limitations

1. **The three relevance scales are not comparable.** On the 187 records included by both of the
   first two passes, pass 2 scored 0.67 higher on average. Pass 3 exists to put the included set on
   one scale and supersedes the earlier scores for ordering; the `relevance` columns of passes 1 and
   2 are screening artefacts and must not be mixed with pass 3 or with each other.
2. **Pass 3 does not discriminate in the band that matters.** 76% of the 945 records scored 4 or 5
   (567 at 4, 152 at 5). A six-point scale assigned from independent single judgements cannot finely
   rank 945 items, so pass 3 supports a two-tier split — 152 core records and a precedent pool of
   567 — rather than a ranking. Selecting ~100 for extraction by rank is therefore not supported by
   these files; a finer instrument, such as counting which extraction fields each paper would fill,
   would be needed.
3. **The borderline selection matched titles only.** Pass 1's output carries no abstract column, so
   `select_second_pass.py` as run matched titles alone and selected 645 records. The same rules
   applied to title+abstract select 1,133, so pass 2 covered 57% of eligible borderline records, and
   just 15 of 134 for the managed-runtime timing rule. This, not the rule's wording, is why WCET
   retention barely moved. The remaining 488 records are a known gap; run
   `select_second_pass.py --exclude-done SECOND_PASS_candidates.csv` to generate them.
4. **Residual instability at the include/exclude boundary.** "A Modular Worst-case Execution Time
   Analysis Tool for Java Processors" was excluded while two near-identical Java-processor WCET
   papers were included. Records in this band should be treated as provisional.
5. **This is not a second reviewer.** All passes use one model. They cannot serve as the independent
   inter-rater check; protocol §6.2 still requires a human second screen of a sample, and the
   agreement figures above measure self-consistency only.
6. **Band coverage.** Only bands 1-2 were screened. Band 3 (775 records) is unscreened; band 4 is
   retained for a sampled estimate of what the banding rule misses.

## Files

Outputs: `LLM_SCREEN_full_gpt-6-luna.csv` (pass 1, all 3,709),
`LLM_SCREEN_pass2_gpt-6-luna.csv` (pass 2), `LLM_RESCORE_includes_gpt-6-luna.csv` (pass 3 — the
file to use for ordering). Intermediate selections: `SECOND_PASS_candidates.csv`,
`RESCORE_includes.csv`. Pilots `llm_pilot2..5b_gpt-6-luna.csv` are retained as the record of the
prompt revisions and the repeat-agreement measurement; pilot 5b is the repeat of pilot 5.

Tools: `../tools/screen_llm.py` (screening, stdlib only), `../tools/select_second_pass.py`
(borderline selection), `../tools/fetch_abstracts2.py` (abstract recovery; 863 cached, further
retrieval has reached diminishing returns at 7 recovered from 177 attempts across four sources).
The API key is read from `~/.openai_key` and is never logged, written or committed.
