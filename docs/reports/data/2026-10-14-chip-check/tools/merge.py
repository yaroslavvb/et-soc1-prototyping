#!/usr/bin/env python3
"""merge.py : every finding with its skeptic's verdict, from the first run's checkers (findings/<slice>/find-result.json)
and the second run's checkers and skeptics (its journal). Writes findings/verified.json and prints a table."""
import json, os, glob, collections, sys

W = '/home/yaroslavvb/claude/work/chip-check-1014'
J2 = '/home/yaroslavvb/.claude-yaroslavvb-mlcollective/projects/-home-yaroslavvb-claude/e68dc1c9-ab74-5a3b-9f82-36229c1b211d/subagents/workflows/wf_ab51825c-179/journal.jsonl'
finds, vers = {}, {}
for p in glob.glob(f'{W}/findings/*/find-result.json'):
    r = json.load(open(p)); finds[r['slice']] = r
rows = [json.loads(l) for l in open(J2)]
label = {r['agentId']: r.get('label') for r in rows if r.get('type') == 'started'}
for r in rows:
    if r.get('type') != 'result' or not isinstance(r.get('result'), dict): continue
    lab = label.get(r['agentId'], ''); res = r['result']
    if lab.startswith('find:'):
        finds[res.get('slice') or lab[5:]] = res
        os.makedirs(f"{W}/findings/{lab[5:]}", exist_ok=True)
        json.dump(res, open(f"{W}/findings/{lab[5:]}/find-result.json", 'w'), indent=1, ensure_ascii=False)
    elif lab.startswith('verify:'):
        vers[lab[7:]] = res
        json.dump(res, open(f"{W}/findings/{lab[7:]}/verify-result.json", 'w'), indent=1, ensure_ascii=False)
out = []
tally = collections.Counter()
for s in sorted(finds):
    v = {x['key']: x for x in (vers.get(s) or {}).get('verdicts', [])}
    print(f"== {s}: {len(finds[s]['findings'])} findings; verified: {'yes' if s in vers else 'no'}")
    for x in finds[s]['findings']:
        vv = v.get(x['key'])
        tag = f"{vv['verdict']}/{vv['severity']}" if vv else '-'
        tally[vv['verdict'] if vv else 'pending'] += 1
        print(f"   [{x['severity'][:5]} -> {tag:16}] {x['key']}")
        out.append(dict(slice=s, key=x['key'], finding=x, verdict=vv))
    for m in (vers.get(s) or {}).get('missed', []):
        print('   + missed:', m[:220])
json.dump(out, open(f'{W}/findings/verified.json', 'w'), indent=1, ensure_ascii=False)
print(dict(tally))
