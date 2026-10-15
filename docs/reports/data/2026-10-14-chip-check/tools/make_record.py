#!/usr/bin/env python3
"""make_record.py OUTDIR : the repository's record of the 14 October correctness check of the chip diagram:
findings.json (every finding with its skeptic's verdict), citations.json (the settled line citations),
codex-triage.json (the 68 observations of Codex's audit and what was decided), fixes.json (what each fixer reported),
crawl-diff.md (what a reader sees that changed), and tables.md (the tables the README includes)."""
import json, os, sys, shutil, collections, glob

W = '/home/yaroslavvb/claude/work/chip-check-1014'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
WF = '/home/yaroslavvb/.claude-yaroslavvb-mlcollective/projects/-home-yaroslavvb-claude/e68dc1c9-ab74-5a3b-9f82-36229c1b211d/subagents/workflows'

V = json.load(open(f'{W}/findings/verified.json'))
rows = []
for x in V:
    f, v = x['finding'], x['verdict']
    rows.append({'slice': x['slice'], 'key': x['key'], 'severity': v['severity'], 'verdict': v['verdict'],
                 'category': f['category'], 'where': f['where'], 'page_said': f['page_says'], 'truth': f['truth'],
                 'evidence': f['evidence'] + v.get('evidence', []), 'fix': v['fix'] or f['fix'], 'checker_fix': f['fix'],
                 'skeptic': v['reason'], 'source_location': f['source_location']})
json.dump(rows, open(f'{OUT}/findings.json', 'w'), indent=1, ensure_ascii=False)

cit = []
for l in open(f'{WF}/wf_72e8404f-920/journal.jsonl'):
    r = json.loads(l)
    if r.get('type') == 'result':
        cit += [dict(x, batch=r['result']['batch']) for x in r['result']['rows']]
        cit += [{'batch': r['result']['batch'], 'other': o} for o in r['result'].get('other', [])]
json.dump(cit, open(f'{OUT}/citations.json', 'w'), indent=1, ensure_ascii=False)

T = json.load(open(f'{W}/codex/triage.json'))
json.dump(T, open(f'{OUT}/codex-triage.json', 'w'), indent=1, ensure_ascii=False)

fx = {}
for wf, tag in (('wf_829d2bd3-e58', 'pass1'), ('wf_c8bc5849-3cc', 'pass1-resumed'), ('wf_95c4da18-265', 'codex')):
    rr = [json.loads(l) for l in open(f'{WF}/{wf}/journal.jsonl')]
    lab = {r['agentId']: r.get('label') for r in rr if r.get('type') == 'started'}
    for r in rr:
        if r.get('type') == 'result': fx[f"{tag}:{lab[r['agentId']].split(':', 1)[1]}"] = r['result']
json.dump(fx, open(f'{OUT}/fixes.json', 'w'), indent=1, ensure_ascii=False)
shutil.copy(f'{W}/crawl-diff.md', f'{OUT}/crawl-diff.md')
au = {}
for l in open(f'{WF}/wf_3bfe5815-47c/journal.jsonl'):
    r = json.loads(l)
    if r.get('type') == 'result': au[r['result']['group']] = r['result']
json.dump(au, open(f'{OUT}/audit.json', 'w'), indent=1, ensure_ascii=False)

# tables for the README
S = {'s01-die-mesh': 'The die and the mesh', 's02-shire': 'A shire', 's03-minion': 'A minion', 's04-memory': 'DRAM and the latency ladder',
     's05-messaging': 'Messages between shires', 's06-host-power': 'Host link, clocks, power, energy', 's07-memlevels': 'Memory cells (deep zoom)',
     's08-circuits': 'Textbook circuits', 's09-device-physics': 'Transistor, silicon, particles', 's10-outside': 'Outside the chip', 's11-prose': 'Prose, tour, page-wide'}
FIND = {}
for p in glob.glob(f'{W}/findings/*/find-result.json'):
    r = json.load(open(p)); FIND[r['slice']] = r['checked']
t = ['| Slice | Facts | Panels | Flow stages | Findings | Major | Minor | Refuted |', '|---|---:|---:|---:|---:|---:|---:|---:|']
agg = collections.defaultdict(collections.Counter)
for x in rows:
    a = agg[x['slice']]
    a['n'] += 1
    if x['verdict'] == 'refuted': a['ref'] += 1
    else: a[x['severity']] += 1
for s in sorted(S):
    c = FIND.get(s, {}); a = agg[s]
    t.append(f"| {S[s]} | {c.get('facts', 0)} | {c.get('panels', 0)} | {c.get('flow_stages', 0)} | {a['n']} | {a['major']} | {a['minor']} | {a['ref']} |")
tot = collections.Counter()
for a in agg.values(): tot.update(a)
t.append(f"| **All** | | | | **{tot['n']}** | **{tot['major']}** | **{tot['minor']}** | **{tot['ref']}** |")
t += ['', '| Finding | Slice | Severity | Verdict |', '|---|---|---|---|']
for x in sorted(rows, key=lambda x: (x['verdict'] == 'refuted', x['severity'] != 'major', x['slice'], x['key'])):
    t.append(f"| `{x['key']}` | {x['slice']} | {x['severity']} | {x['verdict']} |")
t += ['', '| Codex note | Decision | Covered by / reason, first sentence |', '|---|---|---|']
for k in sorted(T, key=lambda k: (k[0], k)):
    d = T[k]
    first = (d.get('covered_by') or d['reason']).split('. ')[0].replace('|', '/').replace('\n', ' ')[:200]
    t.append(f"| {k} | {d['decision']} | {first} |")
open(f'{OUT}/tables.md', 'w').write('\n'.join(t) + '\n')
print('wrote', OUT, len(rows), 'findings', len(cit), 'citation rows', len(T), 'codex notes', len(fx), 'fixer reports')
