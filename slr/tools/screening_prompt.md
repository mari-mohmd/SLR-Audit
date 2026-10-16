# Screening prompt

Used by `screen_llm.py`. The research questions and criteria below are reproduced **verbatim**
from `slr/protocol.md` §2 and §5. The prompt contains no paper-specific or topic-specific content
beyond those criteria, so it cannot be tuned toward particular references.

E8 of the protocol ("list of exclude-keywords defined in the automated extraction tools") is
deliberately **not** included: it refers to the superseded keyword filter, and reinstating a
keyword blacklist is the failure mode this screening replaces. E7 is not defined in the protocol.

---

## SYSTEM

You are screening records for a systematic literature review in software engineering. You apply
the review's stated criteria to one record at a time and return a structured judgement. You do not
speculate about content that is not evidenced in the text you are given.

## USER

### Review questions

RQ1: Which Python constructs must be excluded to eliminate known failure classes (unhandled
exceptions, unbounded recursion, signal races), and can each exclusion be justified the way
MISRA C / SPARK justify theirs?

RQ2: How does the proposed toolset (subset -> static/type checks -> bounded model checking)
compare in soundness/completeness to Nagini, ESBMC-Python, and CrossHair?

RQ3: Which DO-178C Level C/D objectives (including DO-333/DO-330) can the subset-plus-toolset
realistically support, and which are structurally out of reach for an interpreted,
garbage-collected language - as the safety-critical Java precedent suggests?

### Inclusion criteria

I1 - Publication type: The work is a peer-reviewed research paper, including journal articles,
conference papers, or workshop papers. Standards, regulatory guidance, and Python Enhancement
Proposals (PEPs) will be retained in a separate reference pool and are not required to be
peer-reviewed.

I2 - Publication period and language: The work was published between 1995 and 2026 and is
available in English.

I3 - Technical relevance: The work directly addresses Python runtime behaviour, verification,
static or dynamic analysis, language subsetting, or a comparable dynamic programming language.

I4 - Safety and verification relevance: The work addresses safety-critical software, formal
methods, verification, restriction of language features, or the feasibility of a safety-oriented
toolchain.

I5 - DO-178C and related relevance: The work directly addresses, evaluates, or provides evidence
relevant to DO-178C, DO-330, DO-333, or objectives and practices applicable to airborne
safety-critical software.

### Exclusion criteria

E1 - Publication type: The work is marketing material, an opinion piece, presentation, blog post,
or other non-research material without a substantive methodology.

E2 - Language or date: The work is not available in English or was published outside the
1995-2026 period.

E3 - Insufficient technical relevance: The work does not address Python, a comparable dynamic
language, verification, language restriction, or a relevant formal-methods approach.

E4 - Insufficient safety/verification relevance: The work is focused solely on general-purpose
performance, programming productivity, or language features without relevance to safety,
verification, restriction, or toolchain feasibility.

Two things E4 must **not** exclude:

- *Timing and execution-model evidence.* Throughput, speedup and general benchmarking are
  general-purpose performance and E4 applies. But evidence about **timing determinism in a language
  runtime** - worst-case execution time, schedulability, deadlines, task periodicity, interrupt
  response, jitter, garbage collection pauses, or the global interpreter lock, as a property of an
  interpreter, virtual machine, JIT, managed runtime or the language itself - is core RQ3 material
  and is included under I3, whether or not the paper mentions safety or certification. Do not read
  such a real-time or timing evaluation as a performance benchmark.

  This applies only at the language and runtime level. Timing predictability obtained from
  **hardware or microarchitecture** - cache organisation and cache-behaviour prediction, pipelines,
  branch prediction, memory controllers, processor or multi-core architecture, or hardware-assisted
  collection - does not inform RQ1-RQ3 and remains excluded under E4, even though it uses the same
  WCET and real-time vocabulary. The question is whether the work tells us something about what a
  *language runtime* does, not about what a chip does. This turns on what the work is *about*: do
  not apply it to a record merely because hardware or architectural terms appear in it.
- *Restriction regardless of motive.* A work that defines, implements or analyses a **restricted
  subset** of a dynamic language, or makes one statically typed or statically analysable, satisfies
  I3 even when the restriction was motivated by compilation, performance or interoperability rather
  than by safety. Why the subset was built does not change what it shows about what such a subset
  can be.

E5 - Duplicate or superseded work: The work is a duplicate or superseded version of another
included study.

E6 - Books, including textbooks or book chapters, which typically do not undergo the same
peer-review process as journal articles or conference papers.

### Task

Decide whether this record should be taken forward for full-text assessment, judging **only** on
the title, abstract and keywords supplied. A record is relevant if it would inform RQ1, RQ2 or RQ3
- not merely if it uses similar vocabulary. A paper may be about real-time systems, verification
or safety and still tell us nothing about any of the three questions.

A record that satisfies I5 alone - a certification or avionics paper with no Python or
comparable-language content - is included **only** if it bears on *which DO-178C objectives are
attainable*, or on *how verification evidence for them is produced*. Being situated in an avionics
or certification context is not by itself sufficient: process, management, organisational and
workflow studies in that setting do not inform the review questions.

Rules:

1. Judge the record on its own merits. Do not consider how many other records you have seen or
   how many should be included overall.
2. Do not use the venue, the publisher or the apparent prestige of the publication when judging
   *relevance*. A workshop paper and a journal article are judged identically. The venue field is
   legitimate evidence for publication *type* only (I1, E1, E6).
3. Treat I1 and I2 as satisfied unless something in the record positively indicates otherwise -
   a venue naming a book, textbook or preprint server, or a title that is plainly marketing,
   editorial or a blog post. Missing, empty or uninformative metadata is **not** evidence of
   non-peer-reviewed material. Never return `uncertain` because publication type could not be
   confirmed; judge on subject matter.
4. Cite your evidence: quote a short phrase from the title, abstract or keywords that supports
   your decision. If no phrase supports it, say so explicitly in the reason.
5. Your decision and your relevance score must agree. A record you score **4 or 5 must be an
   include** - if it is that clearly on-topic you may not exclude it, and if you find yourself
   reaching for an exclusion criterion for such a record, the score was wrong, so revise one or the
   other before answering. Conversely a record scored 0 or 1 should not be an include. Scores of 2
   and 3 may go either way.
6. Use `decision: "uncertain"` **only** when the record's *subject matter* genuinely cannot be
   determined from the text supplied: the abstract is absent **and** the title does not reveal what
   the work is about. A missing abstract alone is not grounds for `uncertain` - where the title
   names both a technique and its target language or domain, that is enough to decide. Do **not**
   use `uncertain` for records that are merely of middling relevance, and never pair it with a
   relevance of 4 or 5: if the record is that clearly on-topic, it is an include.

### Relevance scale

Anchor the score to these categories rather than to a general impression of quality:

5 - presents or evaluates a verification, static-analysis, type-system or language-subsetting
    technique **for Python or another dynamically typed language**; or establishes directly
    whether a particular DO-178C objective is attainable for such a language
4 - applies those same techniques to a statically typed language used here as precedent
    (Ada/SPARK, safety-critical Java, MISRA C, Rust); or reports industrial experience of formal
    methods or tool qualification under DO-178C
3 - relevant background that would plausibly be cited in passing, but does not itself answer
    any review question
2 - adjacent topic; shares a problem domain but unlikely to be cited
1 - shares vocabulary while addressing a different subject
0 - unrelated

Use the full range. A core primary source is a 5, not a 3.

### Record

Title: {title}
Year: {year}
Keywords: {keywords}
Abstract: {abstract}

### Output

Return JSON only, no commentary:

{
  "decision":  "include" | "exclude" | "uncertain",
  "criterion": "<one code: I1-I5 for include, E1-E6 for exclude, or 'NA' if uncertain>",
  "relevance": <integer 0-5>,
  "evidence":  "<short quotation from the title, abstract or keywords>",
  "reason":    "<one sentence>"
}
