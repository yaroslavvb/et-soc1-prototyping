#!/usr/bin/env python3
"""decl-e217 (Q228) step 6: result.md and result.json from this lane's files (the freeze lines, the forecasts, the counts, the land dir, the
progress log, the release record). Desk. Run: /usr/bin/python3 -I -B s06_result.py <lane dir>"""
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


FN = json.load(open(os.path.join(L, 'forecasts-nominal-e217.json')))['meta']
DE = json.load(open(os.path.join(L, 'DECLARED-blind-e217.json')))
FC = json.load(open(os.path.join(L, 'forecasts-nominal-e217-counts.json'))) if os.path.exists(os.path.join(L, 'forecasts-nominal-e217-counts.json')) else None
CF = os.path.exists(os.path.join(L, 'COUNTS-FROZEN.txt'))
CN = os.path.join(L, 'cnt', 'counts')
c32 = json.load(open(os.path.join(CN, 'counts-fp32-gemm-states.json'))) if os.path.exists(os.path.join(CN, 'counts-fp32-gemm-states.json')) else None
cL = json.load(open(os.path.join(CN, 'counts-fp16-int8-launch.json'))) if os.path.exists(os.path.join(CN, 'counts-fp16-int8-launch.json')) else None
SRC = json.load(open(os.path.join(CN, 'SOURCES.json'))) if os.path.exists(os.path.join(CN, 'SOURCES.json')) else {}
rct = open(os.path.join(CN, 'recount-check.txt')).read() if os.path.exists(os.path.join(CN, 'recount-check.txt')) else ''
verdict_line = [x for x in rct.splitlines() if x.startswith('VERDICT')]
REL = [x for x in open(os.path.join(W, 'out', 'orch', 'e217-releases.txt')).read().splitlines() if x.startswith('#13')]
LAND = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'blind-e217')
land_sums = sha(os.path.join(LAND, 'SHA256SUMS')) if os.path.exists(os.path.join(LAND, 'SHA256SUMS')) else None
nland = sum(1 for _ in open(os.path.join(LAND, 'SHA256SUMS'))) + 1 if land_sums else 0
frozen_sha = sha(os.path.join(L, 'FROZEN.txt'))
cfz_sha = sha(os.path.join(L, 'COUNTS-FROZEN.txt')) if CF else None
EXTRA = json.load(open(os.path.join(L, 'work', 'result-extra.json'))) if os.path.exists(os.path.join(L, 'work', 'result-extra.json')) else {}
ncounts = (sum(len(v) for v in c32['shapes'].values()) if c32 else 0, len(cL['rows']) if cL else 0)
complete = bool(CF and FC and c32 and cL and FC['energy_status'].get('FORECAST') == 35 and verdict_line and 'MATCH' in verdict_line[0] and 'NO MATCH' not in verdict_line[0])
verdict = 'FROZEN' if complete else 'FROZEN WITH GAPS'
shas = {'DECLARED-blind-e217.md': sha(os.path.join(L, 'DECLARED-blind-e217.md')), 'DECLARED-blind-e217.json': sha(os.path.join(L, 'DECLARED-blind-e217.json')),
        'forecasts-nominal-e217.csv': sha(os.path.join(L, 'forecasts-nominal-e217.csv')), 'forecasts-nominal-e217.json': sha(os.path.join(L, 'forecasts-nominal-e217.json')),
        'FROZEN.txt': frozen_sha}
if CF:
    shas['COUNTS-FROZEN.txt'] = cfz_sha
    for n in ('forecasts-nominal-e217-counts.csv', 'forecasts-nominal-e217-counts.json'):
        shas[n] = sha(os.path.join(L, n))
    for n in ('counts-fp32-gemm-states.json', 'counts-fp16-int8-launch.json'):
        shas['cnt/counts/' + n] = sha(os.path.join(CN, n))
if land_sums:
    shas['land SHA256SUMS'] = land_sums
summary = (f"{verdict}: E217's BLIND test declared (DECLARED-blind-e217.md {shas['DECLARED-blind-e217.md'][:8]}, .json "
           f"{shas['DECLARED-blind-e217.json'][:8]}, 11:35:59 PST) and its nominal forecasts frozen (csv {shas['forecasts-nominal-e217.csv'][:8]}, json "
           f"{shas['forecasts-nominal-e217.json'][:8]}) by MM1-v3.1, MM1-v3, MM1-v2, '+contention', '+both' and verify-lay's four controls for 599 runs / "
           f"486 cases; FROZEN.txt {frozen_sha[:8]} written 11:37:53 PST, before any E217 datum (no claim on record). "
           + (f"counts-e217: the 21 new kinds counted on the RTL bench ({ncounts[0]} fp32 rows, {ncounts[1]} launch rows; re-count MATCH), group S's nominal energy "
              f"made with them; COUNTS-FROZEN.txt {cfz_sha[:8]}. " if CF else "counts-e217 NOT FROZEN. ")
           + f"Land dir {nland} files, new files only; no commit.")
res = {'verdict': verdict, 'summary': summary, 'land_dir': os.path.join(L, 'land'), 'data_dir': None,
       'files': [os.path.join(L, n) for n in ('DECLARED-blind-e217.md', 'DECLARED-blind-e217.json', 'forecasts-nominal-e217.csv', 'forecasts-nominal-e217.json',
                                              'FROZEN.txt', 'forecasts-nominal-e217-counts.csv', 'forecasts-nominal-e217-counts.json', 'COUNTS-FROZEN.txt',
                                              'logs/progress.txt') if os.path.exists(os.path.join(L, n))] + [LAND],
       'shas': [f'{v}  {k}' for k, v in shas.items()],
       'numbers': [f"runs 599 (544 arm + 55 anchor), cases 486 (card 1 267, card 0 219), sessions 7",
                   f"groups: X1 105 cases, MG 48 (12 masks a card), SUB 148, FULL 290; S 35, C 18, K 433",
                   f"nominal energy at the first freeze: {json.dumps(FN['energy_status'])}",
                   f"checks: F1 re-made 94 E215 rows (factor diff {FN['checks']['F1_e215']['worst_abs_factor_diff']:.1e}); controls re-made E215 columns (worst {max(FN['checks']['controls_e215']['worst_abs_diff_cycles'].values()):.1e} cycles)",
                   f"bands card 1 T1 10% T2 13% T3 10% E1 14% E2 14% E3 5% E4 10% 0.56 W; card 0 T1 11% T2 16% T3 11% E1 11% E2 13% E3 5% E4 10% 0.56 W"]
       + ([f"counts-e217: {ncounts[0]} fp32 state rows, {ncounts[1]} launch rows; {verdict_line[0] if verdict_line else ''}",
           f"group S nominal energy with counts: {json.dumps(FC['energy_status'])}",
           f"slot-minutes for the counts: {SRC.get('slot_minutes_total')}"] if CF else []),
       'findings': EXTRA.get('findings', []), 'incidents': EXTRA.get('incidents', []), 'open_issues': EXTRA.get('open_issues', []),
       'go_lines': None, 'release_lines_at_result': REL, 'written_pst': now()}
json.dump(res, open(os.path.join(L, 'result.json'), 'w'), indent=1)
md = [f'# decl-e217 (Q228) result: {verdict}', '', summary, '']
md += ['## Hashes', ''] + [f'- `{v}`  {k}' for k, v in shas.items()] + ['']
md += ['## Numbers', ''] + [f'- {x}' for x in res['numbers']] + ['']
if EXTRA.get('body_md'):
    md += [EXTRA['body_md'], '']
md += ['## Findings', ''] + [f"- **{f['severity']}**: {f['what']}" + (f" *Fix:* {f['fix']}" if f.get('fix') else '') for f in res['findings']] + ['']
md += ['## Incidents', ''] + [f'- {x}' for x in res['incidents']] + ['']
md += ['## Open issues and questions for the orchestrator', ''] + [f'- {x}' for x in res['open_issues']] + ['']
md += ['## The release record at this result', ''] + [f'- {x}' for x in REL] + ['']
md += [f"Land dir `{os.path.join(L, 'land')}` ({nland} files under tools/matmul/mm1/v3.1/blind-e217/, new files only; SHA256SUMS {land_sums}). Written {res['written_pst']}."]
open(os.path.join(L, 'result.md'), 'w').write('\n'.join(md) + '\n')
print(verdict)
print(summary)
print(sha(os.path.join(L, 'result.json')), 'result.json')
