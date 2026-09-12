#!/usr/bin/env python3
"""
apply_filter.py

Filters publication records read from one or more CSV files, based on
the title column and rules defined in a config.json file.

Filter rules (config.json -> "filters"):

  "keywords": Either ONE expression string, or a LIST of expression
              strings (each list item may itself use AND / OR /
              parentheses / "quoted phrases", and the list items
              are OR'd together). Matched against the title. A
              paper is kept at this stage if its title satisfies
              the expression. Leave as "" or [] to disable (keep
              everyone at this stage).
              "Python" -> single term
              "Python AND \"machine learning\"" -> single expr
              ["AI", "Python AND \"mining\""] -> (AI) OR (Python AND "mining")

  "exclude-keywords"  Same string-or-list syntax as "keywords". If a title
                       satisfies this expression the paper is dropped --
                       and this ALWAYS overrides "keywords". Example:
                       keywords="Python", exclude-keywords="AI" -> a paper
                       titled "Python and AI in Healthcare" contains both
                       terms, so it is excluded.

  "include-papers"   A list of exact paper titles (case-insensitive) that
                     must be kept no matter what - even if they would
                     otherwise be caught by "exclude-keywords".

  "whole_word"       false (default) or true. By default a term matches
                     as a plain case-insensitive substring anywhere in
                     the title -- e.g. "cyber" matches "Cybersecurity".
                     That also means a short/generic term can match by
                     accident inside an unrelated word: "ADA" matches
                    "Canada" and "Adapter", "SPARK" matches "sparked".
                       Set whole_word=true to require the term to appear
                       as its own word/phrase (a hyphen, space or string
                       boundary on both sides)

If a "keywords"/"exclude-keywords" item mixes AND and OR with no
parentheses (e.g. "software AND quality OR assurance"), the script prints
a warning to stderr: AND binds tighter than OR, so that example is parsed
as "(software AND quality) OR assurance" -- meaning a title containing
only "assurance" (nothing about software) WILL match. Add explicit
parentheses to say what you mean, e.g. "software AND (quality OR
assurance)".

Precedence, per paper:
    1. Is the title in "include-papers"?  -> always KEEP.
    2. Does the title match "exclude-keywords"?  -> DROP.
    3. Does the title match "keywords" (or is "keywords" empty)?  -> KEEP.
    4. Otherwise -> DROP.

Deduplication (config.json -> "deduplicate"), applied AFTER the above
decision so it never changes which papers are kept vs. dropped -- it only
collapses repeat rows so the same paper isn't listed twice:

  "enabled"  true/false (default true). When true, rows whose title is the
             same after normalizing (trim + collapse whitespace + a
             trailing period + lowercase) are folded into a single row.
             This is common when combining exports from several databases
             (e.g. Scopus + Web of Science) that both list the same paper.

  "keep"     "first" (default) or "last" -- which occurrence's other
             columns to keep when duplicates are folded together.

The kept row's "__source_file" lists every file the paper was found in,
and "__duplicate_count" says how many rows were folded into it. Every
row that got folded away (rather than kept) is written to the
"duplicates_csv" output file for reference.

Usage:
    python apply_filter.py --config config.json
"""

import argparse
import csv
import json
import re
import sys
from collections import OrderedDict
from functools import lru_cache
from pathlib import Path


_TOKEN_RE = re.compile(r'"[^"]*"|\(|\)|\bAND\b|\bOR\b|[^\s()]+', re.IGNORECASE)


def _tokenize(expr: str):
    tokens = []
    for match in _TOKEN_RE.finditer(expr):
        raw = match.group(0)
        upper = raw.upper()
        if upper in ("AND", "OR"):
            tokens.append(upper)
        elif raw in ("(", ")"):
            tokens.append(raw)
        else:
            term = raw[1:-1] if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2 else raw
            tokens.append(("TERM", term))
    return tokens


class _ExpressionParser:
    """Recursive-descent parser for the AND/OR/() keyword grammar."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def parse(self):
        if not self.tokens:
            return None
        node = self._parse_or()
        if self._peek() is not None:
            raise ValueError(f"Unexpected trailing token in keyword expression: {self._peek()}")
        return node

    def _parse_or(self):
        node = self._parse_and()
        while self._peek() == "OR":
            self._advance()
            node = ("OR", node, self._parse_and())
        return node

    def _parse_and(self):
        node = self._parse_term()
        while True:
            nxt = self._peek()
            if nxt == "AND":
                self._advance()
                node = ("AND", node, self._parse_term())
            elif nxt is not None and nxt not in ("OR", ")"):
                # two terms next to each other with no explicit operator
                # are treated as an implicit AND, e.g.  python "deep learning"
                node = ("AND", node, self._parse_term())
            else:
                break
        return node

    def _parse_term(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of keyword expression")
        if tok == "(":
            self._advance()
            node = self._parse_or()
            if self._peek() != ")":
                raise ValueError("Missing closing parenthesis in keyword expression")
            self._advance()
            return node
        if isinstance(tok, tuple) and tok[0] == "TERM":
            self._advance()
            return tok
        raise ValueError(f"Unexpected token in keyword expression: {tok}")


def _normalize_expression_input(expr):
    """Accepts either a single expression string, or a list of expression
    strings. A list is treated as OR'd alternatives -- each item may still
    use AND/OR/parentheses internally, e.g.:

        ["AI", "Python AND \"mining\""]

    means:  (AI) OR (Python AND "mining")

    Returns a single expression string (possibly empty)."""
    if expr is None:
        return ""
    if isinstance(expr, str):
        return expr
    if isinstance(expr, list):
        parts = [item.strip() for item in expr if isinstance(item, str) and item.strip()]
        if not parts:
            return ""
        # wrap each item in parens so its internal AND/OR is self-contained,
        # then OR the items together
        return " OR ".join(f"({p})" for p in parts)
    raise ValueError(
        f"Expected a string or a list of strings for a keyword filter, got: {type(expr).__name__}"
    )


def _has_ambiguous_precedence(tokens) -> bool:
    """True if AND and OR both appear at the top level (outside any
    parentheses) of a token stream. 'A AND B OR C' is parsed as
    '(A AND B) OR C' (AND binds tighter than OR, like most languages) --
    which is easy to write by accident and rarely what's intended. This
    flags that case so we can warn about it."""
    depth = 0
    has_and = False
    has_or = False
    for tok in tokens:
        if tok == "(":
            depth += 1
        elif tok == ")":
            depth -= 1
        elif depth == 0 and tok == "AND":
            has_and = True
        elif depth == 0 and tok == "OR":
            has_or = True
    return has_and and has_or


def _warn_if_ambiguous(expr_item: str, label: str):
    tokens = _tokenize(expr_item)
    if _has_ambiguous_precedence(tokens):
        print(
            f"warning: {label} expression mixes AND and OR without parentheses: {expr_item!r}\n"
            f"         This is parsed as 'AND' binding tighter than 'OR', e.g. "
            f"'A AND B OR C' means '(A AND B) OR C' -- so a title matching just C alone WILL match.\n"
            f"         If that's not what you meant, add explicit parentheses, "
            f"e.g. 'A AND (B OR C)'.",
            file=sys.stderr,
        )


def compile_expression(expr, label: str = "keyword"):
    """Compile a keyword expression into an AST. `expr` may be a single
    expression string, or a list of expression strings (OR'd together --
    see `_normalize_expression_input`). `label` is only used to make
    ambiguous-precedence warnings (see `_warn_if_ambiguous`) easier to
    trace back to "keywords" vs "exclude-keywords".

    Returns None if the (normalized) expression is empty/blank, which
    callers should treat as "no filter applied here"."""
    # Check each raw item BEFORE it gets wrapped in its own parens by
    # _normalize_expression_input -- that wrapping would otherwise hide
    # an ambiguous AND/OR mix that exists inside a single list item.
    raw_items = expr if isinstance(expr, list) else [expr] if isinstance(expr, str) else []
    for item in raw_items:
        if isinstance(item, str) and item.strip():
            _warn_if_ambiguous(item, label)

    expr = _normalize_expression_input(expr)
    expr = expr.strip()
    if not expr:
        return None
    tokens = _tokenize(expr)
    if not tokens:
        return None
    return _ExpressionParser(tokens).parse()


def _term_matches(term: str, title_lower: str, whole_word: bool) -> bool:
    term_lower = term.lower()
    if not term_lower:
        return False
    if not whole_word:
        return term_lower in title_lower
    # "Whole word/phrase" matching: the term must not be embedded inside a
    # longer run of letters/digits. This is what stops a short term like
    # "ADA" from matching inside unrelated words like "Canada" or
    # "Adapter", while still matching "ADA" as its own word, and still
    # matching hyphenated/punctuated forms normally (a hyphen or space
    # already acts as a boundary).
    pattern = _word_match_pattern(term_lower)
    return pattern.search(title_lower) is not None


@lru_cache(maxsize=None)
def _word_match_pattern(term_lower: str):
    return re.compile(r"(?<![a-z0-9])" + re.escape(term_lower) + r"(?![a-z0-9])")


def eval_expression(node, title_lower: str, whole_word: bool = False) -> bool:
    if node is None:
        return True
    kind = node[0]
    if kind == "TERM":
        return _term_matches(node[1], title_lower, whole_word)
    if kind == "AND":
        return eval_expression(node[1], title_lower, whole_word) and eval_expression(node[2], title_lower, whole_word)
    if kind == "OR":
        return eval_expression(node[1], title_lower, whole_word) or eval_expression(node[2], title_lower, whole_word)
    raise ValueError(f"Unknown expression node type: {kind!r}")

# Load config
DEFAULT_CONFIG = {
    "input": {
        "csv_files": [],
        "title_column": "Title",
        "encoding": "utf-8"
    },
    "output": {
        "included_csv": "included_papers.csv",
        "excluded_csv": "excluded_papers.csv",
        "duplicates_csv": "duplicates_removed.csv"
    },
    "filters": {
        "keywords": "",
        "exclude-keywords": "",
        "include-papers": [],
        "whole_word": False
    },
    "deduplicate": {
        "enabled": True,
        "keep": "first"
    }
}


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        user_cfg = json.load(f)

    cfg = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy of defaults
    for section in ("input", "output", "filters", "deduplicate"):
        if section in user_cfg and isinstance(user_cfg[section], dict):
            cfg[section].update(user_cfg[section])
    return cfg


def discover_csv_files(cfg: dict):
    files = []
    for p in cfg["input"].get("csv_files") or []:
        files.append(Path(p))

    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    return unique_files


def read_papers(files, title_column: str, encoding: str):
    """Yields (source_path, row_dict) for every data row across all files."""
    for path in files:
        if not path.exists():
            print(f"warning: file not found, skipping: {path}", file=sys.stderr)
            continue
        with open(path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                print(f"warning: no header row found in {path}, skipping", file=sys.stderr)
                continue
            if title_column not in reader.fieldnames:
                print(
                    f"warning: title column '{title_column}' not found in {path} "
                    f"(columns found: {reader.fieldnames}); skipping file",
                    file=sys.stderr,
                )
                continue
            for row in reader:
                # csv.DictReader stashes any columns beyond the header
                # count under the key None (a ragged/malformed row). Fold
                # those into a single readable column instead of leaving
                # a None key around, which downstream CSV writing can't
                # handle.
                extras = row.pop(None, None)
                if extras:
                    row["__extra_columns"] = " | ".join(str(v) for v in extras if v is not None)
                yield path, row


class PaperFilter:
    def __init__(self, cfg: dict):
        filters = cfg["filters"]
        self.keywords_ast = compile_expression(filters.get("keywords", ""), label="keywords")
        self.exclude_ast = compile_expression(filters.get("exclude-keywords", ""), label="exclude-keywords")
        self.include_papers = {
            t.strip().lower()
            for t in filters.get("include-papers", [])
            if isinstance(t, str) and t.strip()
        }
        # Whole-word matching stops a short/generic term (e.g. "ADA",
        # "SPARK") from accidentally matching inside an unrelated longer
        # word (e.g. "Canada", "sparked"). Off by default to preserve the
        # original plain-substring behavior; turn on via
        # filters.whole_word = true.
        self.whole_word = bool(filters.get("whole_word", False))

    def decide(self, title: str):
        """Returns (keep: bool, reason: str)."""
        title_lower = (title or "").strip().lower()

        # 1. include-papers always wins, regardless of any other filter.
        if title_lower in self.include_papers:
            return True, "include-papers override"

        # 2. exclude-keywords takes precedence over keywords.
        if self.exclude_ast is not None and eval_expression(self.exclude_ast, title_lower, self.whole_word):
            return False, "matched exclude-keywords"

        # 3. keywords filter (empty keywords = pass-through).
        if self.keywords_ast is not None and not eval_expression(self.keywords_ast, title_lower, self.whole_word):
            return False, "did not match keywords"

        return True, "kept (matched keywords or no keyword filter set)"


# Remove duplicates.
def normalize_title(title: str) -> str:
    """Normalize a title for duplicate comparison: trim, collapse internal
    whitespace, drop one trailing period, lowercase. Deliberately mild --
    it's meant to catch the same paper re-exported from different
    databases (extra spaces, trailing '.', different case), not to merge
    genuinely different titles."""
    t = (title or "").strip()
    t = re.sub(r"\s+", " ", t)
    if t.endswith("."):
        t = t[:-1]
    return t.lower()


def dedupe_rows(rows, title_column: str, keep: str = "first"):
    """Collapses rows that share the same normalized title into one row.

    Returns (deduped_rows, removed_rows):
      - deduped_rows: one row per unique title. Its "__source_file" is the
        combined list of every file the paper appeared in, and
        "__duplicate_count" is how many rows were folded into it.
      - removed_rows: every row that got folded away, each tagged with
        "__duplicate_of_title" naming the title it was merged into.
    """
    groups = OrderedDict()
    for row in rows:
        key = normalize_title(row.get(title_column, ""))
        groups.setdefault(key, []).append(row)

    deduped = []
    removed = []
    for group in groups.values():
        primary_idx = 0 if keep == "first" else len(group) - 1
        primary_source = group[primary_idx]

        sources = []
        for r in group:
            src = r.get("__source_file", "")
            if src and src not in sources:
                sources.append(src)

        primary = dict(primary_source)
        primary["__source_file"] = " | ".join(sources)
        primary["__duplicate_count"] = len(group)
        deduped.append(primary)

        for i, r in enumerate(group):
            if i == primary_idx:
                continue
            dropped = dict(r)
            dropped["__duplicate_of_title"] = primary_source.get(title_column, "")
            removed.append(dropped)

    return deduped, removed


# Output
def write_csv(path, fieldnames, rows):
    fieldnames = fieldnames or []
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


# Main method
def main():
    parser = argparse.ArgumentParser(
        description="Filter publication CSVs by title keyword rules defined in config.json."
    )
    parser.add_argument("--config", default="config.json", help="Path to config.json (default: ./config.json)")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    title_column = cfg["input"].get("title_column", "Title")
    encoding = cfg["input"].get("encoding", "utf-8")

    files = discover_csv_files(cfg)
    if not files:
        print(
            "No input CSV files found. Set 'input.csv_files' in config.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    paper_filter = PaperFilter(cfg)

    included_rows = []
    excluded_rows = []
    fieldnames = []
    seen_fields = set()

    for source, row in read_papers(files, title_column, encoding):
        # Build the fieldname list as the union of every column seen so
        # far, in first-seen order. Different input CSVs (or even ragged
        # rows within one CSV) can carry different column sets, so we
        # can't just take the first row's keys -- that would make
        # DictWriter reject any later row with an extra column.
        for key in row.keys():
            if key not in seen_fields:
                seen_fields.add(key)
                fieldnames.append(key)

        title = row.get(title_column, "")
        keep, reason = paper_filter.decide(title)
        row_out = dict(row)
        row_out["__source_file"] = str(source)
        row_out["__filter_reason"] = reason
        (included_rows if keep else excluded_rows).append(row_out)

    base_fieldnames = fieldnames + ["__source_file", "__filter_reason"]

    dedup_cfg = cfg["deduplicate"]
    dedup_enabled = dedup_cfg.get("enabled", True)
    dedup_keep = dedup_cfg.get("keep", "first")
    if dedup_keep not in ("first", "last"):
        print(f"warning: deduplicate.keep must be 'first' or 'last', got {dedup_keep!r}; using 'first'", file=sys.stderr)
        dedup_keep = "first"

    duplicate_rows = []
    if dedup_enabled:
        included_rows, included_dupes = dedupe_rows(included_rows, title_column, dedup_keep)
        excluded_rows, excluded_dupes = dedupe_rows(excluded_rows, title_column, dedup_keep)
        duplicate_rows = included_dupes + excluded_dupes
        kept_fieldnames = base_fieldnames + ["__duplicate_count"]
        duplicate_fieldnames = base_fieldnames + ["__duplicate_of_title"]
    else:
        kept_fieldnames = base_fieldnames
        duplicate_fieldnames = base_fieldnames

    out_cfg = cfg["output"]
    included_path = out_cfg.get("included_csv", "included_papers.csv")
    excluded_path = out_cfg.get("excluded_csv", "excluded_papers.csv")
    duplicates_path = out_cfg.get("duplicates_csv", "duplicates_removed.csv")

    write_csv(included_path, kept_fieldnames, included_rows)
    write_csv(excluded_path, kept_fieldnames, excluded_rows)

    total = len(included_rows) + len(excluded_rows) + len(duplicate_rows)
    print(f"Processed {total} paper row(s) from {len(files)} file(s).")
    print(f"  Included: {len(included_rows)} -> {included_path}")
    print(f"  Excluded: {len(excluded_rows)} -> {excluded_path}")
    if dedup_enabled:
        write_csv(duplicates_path, duplicate_fieldnames, duplicate_rows)
        print(f"  Duplicates removed: {len(duplicate_rows)} -> {duplicates_path}")


if __name__ == "__main__":
    main()
