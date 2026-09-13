#!/usr/bin/env python3
"""Retrieve missing abstracts from OpenAlex by DOI and cache them.

The database exports carry abstracts for only ~14% of records (the Scopus export
has no abstract field at all). This fills the gap so screening can be done on
title *and* abstract rather than title alone.

  python3 fetch_abstracts.py SCREEN_bands1-2.csv [more.csv ...]

Writes/updates openalex_abstracts.json alongside this script; build_screening_set.py
picks it up automatically on the next run.
"""
import csv, json, os, sys, time, urllib.parse, urllib.request

csv.field_size_limit(10**9)
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'openalex_abstracts.json')


def inv_to_text(inv):
    if not inv:
        return ''
    return ' '.join(w for _, w in sorted((i, w) for w, idxs in inv.items() for i in idxs))


def main(paths):
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    want = []
    for p in paths:
        for r in csv.DictReader(open(p, encoding='utf-8', errors='replace')):
            doi = (r.get('doi') or '').strip().lower()
            if doi and not (r.get('abstract') or '').strip() and doi not in cache:
                want.append(doi)
    want = sorted(set(want))
    print(f"cache holds {len(cache):,}; fetching {len(want):,} new DOIs", flush=True)

    B = 50
    for i in range(0, len(want), B):
        batch = want[i:i + B]
        url = ("https://api.openalex.org/works?per-page=200"
               "&select=doi,abstract_inverted_index&filter=doi:"
               + urllib.parse.quote('|'.join(batch), safe='|'))
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=60) as fh:
                    data = json.load(fh)
                for w in data.get('results', []):
                    d = (w.get('doi') or '').lower().replace('https://doi.org/', '')
                    a = inv_to_text(w.get('abstract_inverted_index'))
                    if d and a:
                        cache[d] = a
                break
            except Exception as e:
                if attempt == 2:
                    print(f"  batch at {i} failed: {e}", flush=True)
                time.sleep(2 * (attempt + 1))
        if (i // B) % 5 == 0:
            print(f"  {min(i + B, len(want)):>6,}/{len(want):,}  cache: {len(cache):,}", flush=True)
        time.sleep(0.15)

    json.dump(cache, open(CACHE, 'w'))
    print(f"\ncache now holds {len(cache):,} abstracts -> {CACHE}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
