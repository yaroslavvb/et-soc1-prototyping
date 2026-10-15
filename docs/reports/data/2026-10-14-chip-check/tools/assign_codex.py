#!/usr/bin/env python3
"""assign_codex.py : route Codex's observations that the triage decided to implement to the fixer groups that own the
files their fixes touch (the same groups as assign.py, plus F-3d for the 3D companion). Reads the triage's final
results from its journal, else its decision logs. Writes fixes/codex-<group>.json and codex/triage.json."""
import json, os, glob, re, collections, sys
sys.path.insert(0, '/home/yaroslavvb/claude/work/chip-check-1014')
W = '/home/yaroslavvb/claude/work/chip-check-1014'
J = '/home/yaroslavvb/.claude-yaroslavvb-mlcollective/projects/-home-yaroslavvb-claude/e68dc1c9-ab74-5a3b-9f82-36229c1b211d/subagents/workflows/wf_6ce85d95-216/journal.jsonl'
CD = 'docs/reports/data/2026-09-27-chip-diagram/'
GROUPS = {
    'A1-archfacts': [CD + 'research/facts-arch.json', CD + 'research/build_facts_arch.py', CD + 'build_facts.py',
                     'docs/findings/', 'docs/et-soc1-notes.md', 'docs/energy-manual/', 'tools/ettelem/'],
    'A2-numfacts': [CD + 'research/facts-numbers.json', CD + 'research/build_facts_numbers.py', CD + 'research/facts-layout.json',
                    CD + 'research/build_layout_facts.py', CD + 'research/layout.json', CD + 'research/facts-v2.json',
                    CD + 'research/build_facts_v2.py', CD + 'research/asks.json', CD + 'research/make_asks.py'],
    'B-deepzoom': [CD + 'research/build_inside.py', CD + 'research/inside.json', CD + 'research/research-inside',
                   CD + 'research/build_outside.py', CD + 'research/outside.json', CD + 'research/deepzoom.py'],
    'C-pagescript': ['docs/reports/sources/chip-diagram.', 'docs/reports/sources/ladder-', 'docs/reports/sources/ladder.css'],
    'D-memlevels': ['docs/reports/data/2026-09-28-memory-levels/', 'docs/reports/sources/memory-levels.',
                    CD + 'research/circuitkit.', CD + 'research/make_circuitkit.py', 'tools/pagemotion/'],
    'E-ladder': ['docs/reports/data/2026-10-01-ladder/'],
    'F-3d': ['docs/reports/sources/chip-3d/', 'docs/reports/chip-3d.html', 'scripts/build-chip-3d.mjs', 'docs/reports/data/2026-10-14-chip-3d/'],
}
GENERATED = ['docs/reports/2026-09-27-et-soc1-chip-diagram.html', 'docs/reports/2026-09-28-et-soc1-memory-levels.html',
             CD + 'facts.json', 'docs/reports/data/2026-09-28-memory-levels/facts.json', 'docs/reports/ladder-img/ladder-data.json',
             'docs/reports/data/2026-10-01-ladder/ladder.json', 'docs/reports/sources/circuitkit.js']
PATHRX = re.compile(r'((?:docs|tools|scripts|workloads)/[\w./\-]+)')

def group_of(p):
    p = p.replace('/home/yaroslavvb/claude/et-soc1-prototyping/', '').replace('/home/yaroslavvb/claude/work/chip-check-1014/wt-buildtest/', '').strip()
    if any(p.startswith(g) for g in GENERATED): return None
    for g, pre in GROUPS.items():
        if any(p.startswith(x) for x in pre): return g
    return '?'

items = {}
if os.path.exists(J):
    for l in open(J):
        r = json.loads(l)
        if r.get('type') == 'result' and isinstance(r.get('result'), dict):
            for it in r['result']['items']: items[it['id']] = it
for f in glob.glob(f'{W}/codex/*-decisions.jsonl'):
    for l in open(f):
        try: d = json.loads(l)
        except Exception: continue
        items.setdefault(d['id'], d)
json.dump(items, open(f'{W}/codex/triage.json', 'w'), indent=1, ensure_ascii=False)
print('decided', len(items), dict(collections.Counter(d['decision'] for d in items.values())))
work = collections.defaultdict(list); unrouted = []
for i, d in sorted(items.items()):
    if d['decision'] != 'implement': continue
    gs = {group_of(p) for p in d.get('fix_files', [])} - {None}
    if not gs or gs == {'?'}: gs = {group_of(p) for p in PATHRX.findall(d['fix'])} - {None}
    gs.discard('?')
    if not gs: unrouted.append(i); continue
    for g in gs: work[g].append(dict(d, groups=sorted(gs)))
for g, lst in sorted(work.items()):
    json.dump({'group': g, 'owns': GROUPS[g], 'items': lst}, open(f'{W}/fixes/codex-{g}.json', 'w'), indent=1, ensure_ascii=False)
    print(g, len(lst), [x['id'] for x in lst])
print('unrouted', unrouted)
