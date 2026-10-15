#!/usr/bin/env python3
"""assign.py : route every surviving finding (confirmed or partly) and every settled citation to the fixer groups that
own the files its fix touches. Writes fixes/<group>.json. Generated files are mapped to nothing; a finding whose fix
names only generated files is routed by the source locations in the finding."""
import json, os, re, glob, collections

W = '/home/yaroslavvb/claude/work/chip-check-1014'
CD = 'docs/reports/data/2026-09-27-chip-diagram/'
GROUPS = {
    'A1-archfacts': [CD + 'research/facts-arch.json', CD + 'research/build_facts_arch.py', CD + 'build_facts.py',
                     'docs/findings/', 'docs/et-soc1-notes.md', 'docs/energy-manual/'],
    'A2-numfacts': [CD + 'research/facts-numbers.json', CD + 'research/build_facts_numbers.py', CD + 'research/facts-layout.json',
                    CD + 'research/build_layout_facts.py', CD + 'research/layout.json', CD + 'research/facts-v2.json',
                    CD + 'research/build_facts_v2.py', CD + 'research/asks.json', CD + 'research/make_asks.py'],
    'B-deepzoom': [CD + 'research/build_inside.py', CD + 'research/inside.json', CD + 'research/research-inside',
                   CD + 'research/build_outside.py', CD + 'research/outside.json', CD + 'research/deepzoom.py'],
    'C-pagescript': ['docs/reports/sources/chip-diagram.', 'docs/reports/sources/ladder-', 'docs/reports/sources/ladder.css'],
    'D-memlevels': ['docs/reports/data/2026-09-28-memory-levels/', 'docs/reports/sources/memory-levels.',
                    CD + 'research/circuitkit.', CD + 'research/make_circuitkit.py', 'tools/pagemotion/ml_'],
    'E-ladder': ['docs/reports/data/2026-10-01-ladder/'],
}
GENERATED = ['docs/reports/2026-09-27-et-soc1-chip-diagram.html', 'docs/reports/2026-09-28-et-soc1-memory-levels.html',
             CD + 'facts.json', 'docs/reports/data/2026-09-28-memory-levels/facts.json', 'docs/reports/ladder-img/ladder-data.json',
             'docs/reports/data/2026-10-01-ladder/ladder.json', 'docs/reports/sources/circuitkit.js']
PATHRX = re.compile(r'((?:docs|tools|scripts|workloads)/[\w./\-]+)')

def group_of(path):
    path = path.replace('/home/yaroslavvb/claude/et-soc1-prototyping/', '').strip()
    if any(path.startswith(g) for g in GENERATED): return None
    for g, pre in GROUPS.items():
        if any(path.startswith(p) for p in pre): return g
    return '?'

V = json.load(open(f'{W}/findings/verified.json'))
work = collections.defaultdict(lambda: {'items': [], 'citations': []})
unrouted = []
for x in V:
    v = x['verdict']
    if not v or v['verdict'] == 'refuted': continue
    paths = list(v.get('fix_files') or [])
    gs = {group_of(p) for p in paths} - {None}
    if not gs or gs == {'?'}:
        gs = {group_of(p) for p in PATHRX.findall(x['finding']['source_location'] + ' ' + v['fix'])} - {None, '?'}
    gs.discard('?')
    if not gs: unrouted.append(x['key']); continue
    item = {'slice': x['slice'], 'key': x['key'], 'severity': v['severity'], 'verdict': v['verdict'],
            'where': x['finding']['where'], 'page_says': x['finding']['page_says'], 'truth': x['finding']['truth'],
            'evidence': x['finding']['evidence'] + v.get('evidence', []), 'source_location': x['finding']['source_location'],
            'skeptic_reason': v['reason'], 'fix': v['fix'] or x['finding']['fix'], 'checker_fix': x['finding']['fix'],
            'fix_files': paths, 'groups': sorted(gs)}
    for g in gs: work[g]['items'].append(item)
# the skeptics' "missed" notes: new errors seen while verifying, not yet verified: the fixer checks each before applying
for p in glob.glob(f'{W}/findings/*/verify-result.json'):
    vr = json.load(open(p))
    for m in vr.get('missed', []):
        gs = {group_of(q) for q in PATHRX.findall(m)} - {None, '?'}
        if not gs: gs = {'C-pagescript'}
        item = {'slice': vr.get('slice'), 'key': 'missed: ' + m[:60], 'severity': 'minor', 'verdict': 'unverified',
                'where': '', 'page_says': '', 'truth': m, 'evidence': [], 'source_location': '', 'skeptic_reason': '',
                'fix': 'UNVERIFIED (a skeptic saw it while checking another finding): confirm it from the evidence it names before applying; if it is real, fix it as the note implies, in your files only. ' + m,
                'checker_fix': '', 'fix_files': PATHRX.findall(m), 'groups': sorted(gs)}
        for g in gs: work[g]['items'].append(item)
# the settled citations: route by where each fact is generated
CJ = '/home/yaroslavvb/.claude-yaroslavvb-mlcollective/projects/-home-yaroslavvb-claude/e68dc1c9-ab74-5a3b-9f82-36229c1b211d/subagents/workflows/wf_72e8404f-920/journal.jsonl'
REPO = '/home/yaroslavvb/claude/et-soc1-prototyping'
def gen_file(fid):
    for g, files in (('A1-archfacts', ['facts-arch.json']), ('A2-numfacts', ['facts-numbers.json', 'facts-layout.json', 'facts-v2.json']),
                     ('B-deepzoom', ['inside.json', 'outside.json'])):
        for f in files:
            if f'"{fid}"' in open(f'{REPO}/{CD}research/{f}').read(): return g
    if fid.startswith('ml:'): return 'D-memlevels'
    for f in glob.glob(f'{REPO}/docs/reports/data/2026-10-01-ladder/research/*.json'):
        if f'"{fid}"' in open(f).read(): return 'E-ladder'
    if f"'{fid}'" in open(f'{REPO}/{CD}build_facts.py').read(): return 'A1-archfacts'
    if fid.split('.')[0] in ('out', 'in', 'size'): return 'B-deepzoom'
    return '?'
ncit = collections.Counter()
if os.path.exists(CJ):
    for l in open(CJ):
        r = json.loads(l)
        if r.get('type') != 'result' or not isinstance(r.get('result'), dict): continue
        for row in r['result']['rows']:
            if row['action'] == 'keep': continue
            g = gen_file(row['fact']); ncit[(g, row['action'])] += 1
            work[g]['citations'].append(row)
        for o in r['result'].get('other', []):
            if o.startswith('None wrong'): continue
            gs = {group_of(q) for q in PATHRX.findall(o)} - {None, '?'} or {'A1-archfacts'}
            for g in gs: work[g]['citations'].append({'other': o})
os.makedirs(f'{W}/fixes', exist_ok=True)
for g, w in sorted(work.items()):
    w['group'] = g; w['owns'] = GROUPS.get(g, [])
    json.dump(w, open(f'{W}/fixes/{g}.json', 'w'), indent=1, ensure_ascii=False)
    print(g, len(w['items']), 'items', len(w['citations']), 'citations')
print('unrouted:', unrouted)
print('citations by group/action:', dict(ncit))
