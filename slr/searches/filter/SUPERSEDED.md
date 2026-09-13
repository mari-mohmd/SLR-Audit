# Superseded — retained for the record

The keyword filter in this directory (`apply_filter.py` + `config.json`) was the first attempt
to reduce the merged search results to a screenable set. It was replaced on 13 September 2026.

**Why.** The filter retained a record only if its *title* matched one of the include keywords,
so any topic not named in advance was discarded. Measured against `searches.csv`, it kept 1 of
107 records on worst-case execution time, 1 of 186 on garbage collection, none of the 60 on
memory management, and 2 of 9 on tool qualification — all central to RQ3.

The Tier-1 validation did not reveal this, because `config.json` listed the 17 Tier-1 titles in
an `include-papers` must-keep list. Those records bypassed the filter and survived regardless,
so the check could not measure how the filter treated anything else.

The replacement is described in Section 6.1 of `slr/protocol.md`; outputs are under
`slr/screening/`. This directory is kept because the refinement history is part of the record.
