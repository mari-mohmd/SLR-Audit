#!/usr/bin/env python3
"""Build the SLR screening set from the merged database exports.

Reproduces slr/screening/*.csv from slr/searches/filter/searches.csv in one pass.
Standard library only.

  python3 build_screening_set.py --searches ../searches/filter/searches.csv --out .

Optionally enrich with abstracts retrieved from OpenAlex (see fetch_abstracts.py);
if openalex_abstracts.json is present alongside this script it is used automatically.
"""
import argparse, collections, csv, json, os, re, sys, unicodedata

csv.field_size_limit(10**9)

# ---------------------------------------------------------------- facets
FACETS = {
 'PY': [r'\bpython\b', r'\bcpython\b', r'\bpypy\b', r'\brpython\b', r'\bcython\b', r'\bnuitka\b',
   r'\bnumba\b', r'\bmicropython\b', r'\bjython\b', r'\bmojo\b', r'\bmypy\b', r'\bmypyc\b',
   r'\bcinder\b', r'\bdynamic(ally)?[- ]typed\b', r'\bdynamic languages?\b',
   r'\bgradual typing\b', r'\bgradual types?\b', r'\bduck typing\b', r'\bscripting language'],
 'VERIF': [r'\bstatic analysis\b', r'\bstatic analyz', r'\babstract interpretation\b',
   r'\bmodel check', r'\bsymbolic execution\b', r'\bformal verification\b', r'\bformal method',
   r'\bdeductive verification\b', r'\btheorem prov', r'\bproof assistant\b', r'\bsmt\b',
   r'\btype inference\b', r'\btype check', r'\btype system\b', r'\btype safety\b',
   r'\btype error', r'\bcontracts?\b', r'\bprogram verification\b', r'\bverif(y|ied|ication)\b',
   r'\bsound(ness)?\b', r'\bstatic type', r'\bdataflow analysis\b', r'\bprogram analysis\b',
   r'\bruntime verification\b', r'\bassertion', r'\binvariant'],
 'CERT': [r'\bdo[- ]?178', r'\bdo[- ]?330\b', r'\bdo[- ]?331\b', r'\bdo[- ]?332\b', r'\bdo[- ]?333\b',
   r'\bdo[- ]?248\b', r'\bed[- ]?12\b', r'\barp ?476[14]\b', r'\biec ?61508\b', r'\biso ?26262\b',
   r'\bavionic', r'\bairborne\b', r'\baerospace\b', r'\bflight software\b',
   r'\bsafety[- ]critical\b', r'\bsafety critical\b', r'\bhigh[- ]integrity\b',
   r'\bhigh[- ]assurance\b', r'\bcertification\b', r'\bcertifiab', r'\bqualification\b',
   r'\bmission[- ]critical\b', r'\bdependab', r'\bfunctional safety\b', r'\bassurance case\b',
   r'\bmc/dc\b', r'\bstructural coverage\b', r'\bdal\b', r'\bsafety integrity\b'],
 'RUNTIME': [r'\bwcet\b', r'\bworst[- ]case execution\b', r'\breal[- ]time\b', r'\bdeterminis',
   r'\bgarbage collect', r'\bmemory management\b', r'\bmemory safety\b', r'\bheap\b',
   r'\bmanaged runtime\b', r'\bvirtual machine\b', r'\binterpreter\b', r'\bbytecode\b',
   r'\bjit\b', r'\bjust[- ]in[- ]time\b', r'\bschedulab', r'\blatency\b', r'\bjitter\b',
   r'\btiming analysis\b', r'\bpredictab', r'\bexecution time\b', r'\bstack overflow\b',
   r'\bexception handling\b', r'\bconcurrenc', r'\bglobal interpreter lock\b', r'\bgil\b'],
 'SUBSET': [r'\bmisra\b', r'\bspark\s*(ada|2014)?\b', r'\bada\b', r'\bcoding standard',
   r'\bcoding guideline', r'\blanguage subset\b', r'\brestricted subset\b', r'\bsafe subset\b',
   r'\blanguage restriction', r'\bsafety[- ]critical java\b', r'\brtsj\b', r'\bjsr[- ]?302\b',
   r'\bscj\b', r'\breal[- ]time java\b', r'\bferrocene\b', r'\brust\b', r'\bcompcert\b',
   r'\bverified compil', r'\bcertified compil', r'\btranspil', r'\bcode generat',
   r'\bprogramming language\b', r'\blanguage design\b'],
}
STRONG = [r'\bdo[- ]?178', r'\bdo[- ]?330\b', r'\bdo[- ]?331\b', r'\bdo[- ]?332\b', r'\bdo[- ]?333\b',
  r'\bed[- ]?12\b', r'\bmisra\b', r'\bwcet\b', r'\bworst[- ]case execution\b', r'\bcompcert\b',
  r'\bnagini\b', r'\besbmc\b', r'\brpython\b', r'\bsafety[- ]critical java\b', r'\bjsr[- ]?302\b',
  r'\bmc/dc\b', r'\bglobal interpreter lock\b', r'\bspark 2014\b', r'\btool qualification\b']
OFFTOPIC = [r'\bmalware\b', r'\bransomware\b', r'\bphishing\b', r'\bintrusion detection\b',
  r'\bdeep learning\b', r'\bneural network', r'\bmachine learning\b', r'\bconvolutional\b',
  r'\blarge language model', r'\bchatgpt\b', r'\bimage (classification|recognition|segmentation)\b',
  r'\bcomputer vision\b', r'\bspeech recognition\b', r'\brecommender\b', r'\bsocial (media|network)\b',
  r'\bblockchain\b', r'\bsmart (grid|city|home|farming)\b', r'\bwireless sensor\b', r'\b5g\b',
  r'\bbioinformatic', r'\bgenom', r'\bmedical imag', r'\bremote sensing\b', r'\bagricultur',
  r'\bstudents?\b', r'\bcurricul', r'\bteaching\b', r'\bclassroom\b', r'\bmooc\b']
# intersections a distinct-facet count cannot see (e.g. "real-time garbage collection")
COMPOUND = [
 (r'garbage collect|memory management|memory allocat|\bheap\b|\bgc\b',
  r'real[- ]?time|determinis|worst[- ]case|bounded|predictab|embedded|\bjava\b|\bjvm\b|'
  r'virtual machine|interpreter|microcontroller|microprocessor|pause'),
 (r'\binterpreter\b|\bbytecode\b|\bvirtual machine\b',
  r'safety|verif|real[- ]?time|determinis|certif|optimi|analys'),
 (r'\bexception (handling|safety)\b|\bstack overflow\b|\brecursion\b',
  r'safety|verif|static|real[- ]?time|bound'),
]
LITERAL = r'\bocean\b|\bwaste\b|municipal|\btruck|recycl|geofence|\blitter\b|refuse collection|smart city'

FC = {k: [re.compile(p) for p in v] for k, v in FACETS.items()}
SC = [re.compile(p) for p in STRONG]
OC = [re.compile(p) for p in OFFTOPIC]
CP = [(re.compile(a), re.compile(b)) for a, b in COMPOUND]
LT = re.compile(LITERAL)


def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', s.lower())).strip()


def pick(row, *keys):
    for k in keys:
        v = row.get(k)
        if v and str(v).strip():
            return str(v).strip()
    return ''


def load(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        for row in csv.DictReader(fh):
            t = pick(row, 'title', 'Document Title')
            if not t:
                continue
            yield {
                'title': t, 'nt': norm(t),
                'doi': pick(row, 'DOI', 'doi').lower().replace('https://doi.org/', ''),
                'abstract': pick(row, 'Abstract', 'abstract'),
                'kw': ' '.join([pick(row, 'Author Keywords'), pick(row, 'keywords'),
                                pick(row, 'keyword'), pick(row, 'IEEE Terms')]),
                'year': pick(row, 'Publication Year', 'Year', 'year'),
                'venue': pick(row, 'Publication Title', 'Source title', 'journal', 'booktitle', 'venue'),
                'link': pick(row, 'Link', 'url', 'PDF Link'),
            }


def dedupe(recs):
    by_doi, by_title, out = {}, {}, []
    for r in recs:
        key, book = (r['doi'], by_doi) if r['doi'] else (r['nt'], by_title)
        if key in book:
            prev = book[key]
            if len(r['abstract']) > len(prev['abstract']):
                prev.update(r)
            continue
        book[key] = r
        out.append(r)
    seen, final = {}, []
    for r in out:                                  # collapse titles surviving via different DOIs
        if r['nt'] in seen:
            prev = seen[r['nt']]
            if len(r['abstract']) > len(prev['abstract']):
                prev.update(r)
            continue
        seen[r['nt']] = r
        final.append(r)
    return final


def band(rec):
    t = rec['title'].lower()
    ext = (rec['abstract'] + ' ' + rec['kw']).lower()
    hT = {f: [p.pattern for p in ps if p.search(t)] for f, ps in FC.items()}
    hT = {k: v for k, v in hT.items() if v}
    hX = {f: [p.pattern for p in ps if p.search(ext)] for f, ps in FC.items()} if ext.strip() else {}
    hX = {k: v for k, v in hX.items() if v}
    strong = [p.pattern for p in SC if p.search(t) or p.search(ext)]
    off = [p.pattern for p in OC if p.search(t)]
    comp = any(a.search(t) and b.search(t) for a, b in CP) and not LT.search(t)
    nT, nAll, py = len(hT), len(set(hT) | set(hX)), 'PY' in hT
    has_ab = bool(rec['abstract'].strip())
    score = (nT * 3 + (nAll - nT) * 2 + len(strong) * 4 + (3 if comp else 0)
             - (3 if off and nT < 2 and not strong and not comp else 0))
    if strong and (nAll >= 2 or not has_ab):  b = 1
    elif comp or nT >= 2:                     b = 1
    elif strong:                              b = 1
    elif py and nAll >= 2:                    b = 2
    elif nT == 1 and nAll >= 2:               b = 2
    elif py:                                  b = 3
    elif nT == 1 or hX:                       b = 4
    else:                                     b = 5
    if LT.search(t) and nT < 2:               b = 5
    if off and not strong and not comp and nT < 2 and not py:
        b = min(b + 1, 5)
    why = (['COMPOUND'] if comp else []) + [
        f"{f}:" + ",".join(x.replace('\\b', '').replace('\\', '') for x in v[:3])
        for f, v in sorted(hT.items())]
    extra = sorted(set(hX) - set(hT))
    if extra:
        why.append('abs:' + '+'.join(extra))
    return b, score, '+'.join(sorted(hT)) or '-', '+'.join(extra) or '-', \
           ('yes' if has_ab else 'no'), '; '.join(why) or '-'


COLS = ['order', 'band', 'score', 'decision', 'criterion', 'notes', 'title', 'year', 'venue',
        'has_abstract', 'abstract', 'doi', 'link', 'facets_title', 'facets_abstract', 'why']


def emit(path, rows):
    rows.sort(key=lambda r: (r['band'], -r['score'], r['title'].lower()))
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(COLS)
        for i, r in enumerate(rows, 1):
            w.writerow([i, r['band'], r['score'], '', '', '', r['title'], r['year'], r['venue'],
                        r['has_abstract'], r['abstract'][:2000], r['doi'], r['link'],
                        r['facets_title'], r['facets_abstract'], r['why']])
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--searches', default='../searches/filter/searches.csv')
    ap.add_argument('--out', default='.')
    ap.add_argument('--abstracts', default=None,
                    help='openalex_abstracts.json (default: alongside this script, if present)')
    a = ap.parse_args()

    cache = a.abstracts or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'openalex_abstracts.json')
    extra = json.load(open(cache)) if os.path.exists(cache) else {}
    if extra:
        print(f"abstract cache: {len(extra):,} entries")

    raw = list(load(a.searches))
    recs = dedupe(raw)
    filled = 0
    for r in recs:
        if not r['abstract'].strip() and r['doi'] in extra:
            r['abstract'] = extra[r['doi']]
            filled += 1
    print(f"raw {len(raw):,} -> unique {len(recs):,}   abstracts filled from cache: {filled:,}")

    for r in recs:
        r['band'], r['score'], r['facets_title'], r['facets_abstract'], r['has_abstract'], r['why'] = band(r)

    os.makedirs(a.out, exist_ok=True)
    groups = {'SCREEN_bands1-2.csv':      [r for r in recs if r['band'] <= 2],
              'SCREEN_band3_optional.csv': [r for r in recs if r['band'] == 3],
              'HELD_band4.csv':            [r for r in recs if r['band'] == 4],
              'EXCLUDED_band5.csv':        [r for r in recs if r['band'] == 5]}
    for name, rows in groups.items():
        print(f"  {name:<28}{emit(os.path.join(a.out, name), rows):>7,}")

    cov = sum(1 for r in groups['SCREEN_bands1-2.csv'] if r['has_abstract'] == 'yes')
    n = len(groups['SCREEN_bands1-2.csv'])
    print(f"\nscreening-set abstract coverage: {cov:,}/{n:,} ({cov/n:.0%})")


if __name__ == '__main__':
    main()
