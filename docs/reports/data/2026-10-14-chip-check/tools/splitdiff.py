#!/usr/bin/env python3
"""splitdiff.py DIFF.md OUTDIR : split the crawl diff into one file per audit group, by what each section is about:
a scale (by the checker slices' scales), a fact (by the slice that owns the fact id), a flow, the tour or the page's
static text. Writes OUTDIR/<group>.md and prints the counts."""
import re, sys, os, json, collections
sys.path.insert(0, '/home/yaroslavvb/claude/work/chip-check-1014')
DIFF, OUT = sys.argv[1:3]
W = '/home/yaroslavvb/claude/work/chip-check-1014'
# the slices' scales and facts (partition.py's SCALES and RULES)
src = open(f'{W}/partition.py').read()
SC = {}
for name, lst in re.findall(r"'(s\d\d-[\w-]+)': \[([^\]]*)\]", src):
    for s in re.findall(r"'([\w.]+)'", lst): SC[s] = name
RULES = [(n, rx) for n, rx in re.findall(r"\('(s\d\d-[\w-]+)', r'([^']+)'\)", src)]
AUD = {  # audit groups: slices -> auditor
    's01-die-mesh': 'a1-chip', 's02-shire': 'a1-chip', 's03-minion': 'a1-chip',
    's04-memory': 'a2-flows', 's05-messaging': 'a2-flows', 's06-host-power': 'a2-flows',
    's07-memlevels': 'a3-deep', 's08-circuits': 'a3-deep', 's09-device-physics': 'a4-outer', 's10-outside': 'a4-outer',
}
def slice_of_fact(fid):
    for n, rx in RULES:
        if re.search(rx, fid): return n
    return None
parts = re.split(r'(?m)^## ', open(DIFF).read())[1:]
out = collections.defaultdict(list)
for p in parts:
    key = p.split('\n', 1)[0].strip()
    if key.startswith('scale/'):
        sid = key.split('/')[1]
        g = AUD.get(SC.get(sid), 'a3-deep')
    elif key.startswith('fact/'):
        g = AUD.get(slice_of_fact(key[5:]), 'a5-prose')
    elif key.startswith('flow/'):
        g = 'a2-flows'
    else:
        g = 'a5-prose'          # tour, static sections, asks, electrons
    out[g].append('## ' + p)
os.makedirs(OUT, exist_ok=True)
for g, lst in sorted(out.items()):
    open(f'{OUT}/{g}.md', 'w').write(''.join(lst))
    print(g, len(lst), 'sections', sum(len(x) for x in lst), 'chars')
