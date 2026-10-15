#!/usr/bin/env python3
"""summarize.py JOURNAL [--full KEY] : the workflow's results so far: per slice, the checker's findings and the
skeptic's verdicts. Writes findings/all.json with every finding merged with its verdict."""
import json, sys, collections

J = sys.argv[1]
rows = [json.loads(l) for l in open(J)]
label = {r['agentId']: r.get('label') for r in rows if r.get('type') == 'started'}
finds, vers = {}, {}
for r in rows:
    if r.get('type') != 'result' or not isinstance(r.get('result'), dict):
        continue
    res = r['result']
    lab = label.get(r['agentId'], '')
    if lab.startswith('find:'):
        finds[res.get('slice') or lab[5:]] = res
    elif lab.startswith('verify:'):
        vers[res.get('slice') or lab[7:]] = res
merged = []
for s in sorted(finds):
    f = finds[s]
    v = {x['key']: x for x in (vers.get(s) or {}).get('verdicts', [])}
    sev = collections.Counter(x['severity'] for x in f['findings'])
    print(f"== {s}: checked {f['checked']}, findings {len(f['findings'])} {dict(sev)}; verified: {'yes' if s in vers else 'no'}")
    for x in f['findings']:
        vv = v.get(x['key'])
        tag = (vv['verdict'] + '/' + vv['severity']) if vv else '-'
        print(f"   [{x['severity'][:4]}|{x['confidence'][:3]}|{tag}] {x['key']}: {x['where'][:90]}")
        merged.append(dict(x, slice=s, verdict=vv))
    for m in (vers.get(s) or {}).get('missed', []):
        print('   missed:', m[:200])
json.dump({'finds': finds, 'verifies': vers, 'merged': merged}, open('/home/yaroslavvb/claude/work/chip-check-1014/findings/all.json', 'w'), indent=1, ensure_ascii=False)
if '--full' in sys.argv:
    k = sys.argv[sys.argv.index('--full') + 1]
    for m in merged:
        if m['key'] == k:
            print(json.dumps(m, indent=1, ensure_ascii=False))
