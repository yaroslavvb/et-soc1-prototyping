#!/usr/bin/env python3
"""unread-e214 (Q225) step 5: the land dir land/tools/matmul/mm1/v3.1/unread-e214/ (new files only): the declaration, the forecasts, the
scores, the post hoc reading and recheck, step 1-2's inputs, the logs, the scripts (the box's paths replaced by <W>, <LAB>, <SCRATCH>), a
README written from the scores and the progress log, and SHA256SUMS. Then a scan for home paths, logins and scratch paths. Desk.
Run: /usr/bin/python3 -I -B s05_land.py <lane dir>
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
LAB = '<LAB>'
REL = 'tools/matmul/mm1/v3.1/unread-e214'
D = os.path.join(L, 'land', REL)
if os.path.exists(os.path.join(L, 'land')):
    shutil.rmtree(os.path.join(L, 'land'))
os.makedirs(D)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def cp(src, rel):
    dst = os.path.join(D, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


for n in ('DECLARED-unread-e214.md', 'DECLARED-unread-e214.json', 'forecasts-unread-e214.csv', 'forecasts-unread-e214.json'):
    cp(os.path.join(L, n), n)
for n in ('scores-unread-e214.json', 'scores-unread-e214-cases.csv', 'scores-unread-e214-runs.csv', 'posthoc-time-misses.json', 'recheck.json'):
    cp(os.path.join(L, 'work', 'step3', n), n)
for n in ('runs-listed.json', 'models-step1.json', 'cells-v31.json', 'cells-v3.json', 'bands.json', 'twin-keys.json', 'earlier-lanes.json'):
    cp(os.path.join(L, 'work', 'step1', n), os.path.join('inputs', 'step1', n))
for n in ('conditions-e214.json', 'fc-v31.json', 'fc-v3.json', 'fc-v2.json'):
    cp(os.path.join(L, 'work', 'step2', n), os.path.join('inputs', 'step2', n))
for n in ('step1-sha256.txt', 'step2-sha256.txt', 'step3-sha256.txt', 's03_score.out', 'progress.txt'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n))
REPL = [(W, '<W>'), (LAB, '<LAB>'), ('<SCRATCH>', '<SCRATCH>')]
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    t = open(os.path.join(L, 'scripts', n)).read()
    for a, b in REPL:
        t = t.replace(a, b)
    os.makedirs(os.path.join(D, 'scripts'), exist_ok=True)
    open(os.path.join(D, 'scripts', n), 'w').write(t)

# ------------------------------------------------------------------ the README, from the scores and the log
S = json.load(open(os.path.join(L, 'work', 'step3', 'scores-unread-e214.json')))
DE = json.load(open(os.path.join(L, 'DECLARED-unread-e214.json')))
PH = json.load(open(os.path.join(L, 'work', 'step3', 'posthoc-time-misses.json')))
RC = json.load(open(os.path.join(L, 'work', 'step3', 'recheck.json')))
FJ = json.load(open(os.path.join(L, 'forecasts-unread-e214.json')))
prog = open(os.path.join(L, 'logs', 'progress.txt')).read().splitlines()
C1, C0 = 'aifoundry1 card 1', 'aifoundry1 card 0'
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2'}
T = S['tables_per_case']


def fx(x):
    if not x:
        return '-'
    return f"{x['rms_pct']:.2f}% ({x['bias_pct']:+.2f}), n {x['n']}"


def fw(x):
    if not x:
        return '-'
    return f"{x['rms_W']:.3f} W ({x['bias_W']:+.3f}), n {x['n']}"


md = []
A = md.append
A('# unread-e214: MM1-v3.1, MM1-v3 and MM1-v2 scored UNREAD on E214 (the model session\'s third matmul sweep, 593 runs on aifoundry1\'s two cards)')
A('')
A('*Round Q225 (track A), lane unread-e214, Thu 19 Nov 2026, at the desk on aifoundry2: no card, no simulator, nothing measured here. Every '
  'numerical job ran in the round\'s CPU slots single-threaded; interpreter `/usr/bin/python3` 3.12.3 (`-I -B`), numpy 1.26.4.*')
A('')
A('**Label: UNREAD.** The three models are frozen and unchanged (MM1-v3.1 landed 2c971828, MM1-v3 b1493082, MM1-v2 3ca4b717), with the switch '
  'counts frozen (MM1-v3.1\'s `counts/`, 3e8991d0; `counts-e214/`, SHA256SUMS 4c39d0d3..., verified), before this lane read any E214 measurement. '
  'Not blind: E214\'s data existed (committed Wed 18 Nov 2026 16:44-21:06 PST, notes 10f662e3) and its data lanes had read them (section 7). '
  '**No E214 point entered any of the three fits** (section 6). Error = forecast / measured - 1; rms and signed mean (bias) in %; a case is '
  '(card, shape, format, kind, mask) over that card\'s sessions, its error the mean of its runs\'.')
A('')
A('The owner\'s words that started the matmul model (Mon 16 Nov 2026; "matte mold" is the matmul): "I want you to focus on the matte mold most of '
  'all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know '
  'about the size of a matrix and which operations are contained."')
A('')
A('## 1. The order, hashed (Pacific, Thu 19 Nov 2026; `logs/progress.txt`)')
A('')
A('| step | time | files (sha256) |')
A('|---|---|---|')
A(f"| 1. DECLARED (before any E214 measurement) | 10:42:28 written, 10:42:41 logged | `DECLARED-unread-e214.md` {sha(os.path.join(L, 'DECLARED-unread-e214.md'))}, `DECLARED-unread-e214.json` {sha(os.path.join(L, 'DECLARED-unread-e214.json'))} |")
A(f"| 2. conditions read (clock, minion volts, die at start only) | 10:43:04 | `inputs/step2/conditions-e214.json` {sha(os.path.join(L, 'work', 'step2', 'conditions-e214.json'))} |")
A(f"| 2. FORECAST (the frozen predictors, unchanged) | 10:44-10:46:14 written, 10:46:42 logged | `forecasts-unread-e214.csv` {sha(os.path.join(L, 'forecasts-unread-e214.csv'))}, `forecasts-unread-e214.json` {sha(os.path.join(L, 'forecasts-unread-e214.json'))} |")
A(f"| the scorer frozen (after a stand-in code test) | 10:49:30 | `scripts/s03_score.py` (the lane's copy) {sha(os.path.join(L, 'scripts', 's03_score.py'))} |")
A(f"| 3. READ AND SCORED | 10:49:34 | `scores-unread-e214.json` {sha(os.path.join(L, 'work', 'step3', 'scores-unread-e214.json'))}, `-cases.csv` {sha(os.path.join(L, 'work', 'step3', 'scores-unread-e214-cases.csv'))}, `-runs.csv` {sha(os.path.join(L, 'work', 'step3', 'scores-unread-e214-runs.csv'))} |")
A(f"| post hoc reading (REPORTED) | 10:50:23 | `posthoc-time-misses.json` {sha(os.path.join(L, 'work', 'step3', 'posthoc-time-misses.json'))} |")
A(f"| recheck (independent path) | 10:51:07 | `recheck.json` {sha(os.path.join(L, 'work', 'step3', 'recheck.json'))} |")
A('')
A('Every step-1, step-2 and step-3 file is listed with its sha256 in `logs/step1-sha256.txt`, `logs/step2-sha256.txt` and `logs/step3-sha256.txt`. '
  'The scripts in `scripts/` are the lane\'s with the box\'s paths replaced by `<W>`, `<LAB>` and `<SCRATCH>`; the sha256 in the logs are of the '
  'lane\'s own copies.')
A('')
A(f"## 2. The verdict (the declared pass rule, decided by `scripts/s03_score.py`): **{S['VERDICT']}**")
A('')
A(f"- **Part A, MM1-v3.1 by E215's rule form on the no-twin cases: {S['part_A_verdict']}.** Failing: {', '.join(S['part_A_fails']) or 'none'}. "
  'Each case passes when |error| is within its band (E1, E2: watts at a watts case); a rule passes when at least 90% of its cases pass.')
A(f"- **Part S, the switch route with the new counts against the null: {S['part_S_verdict']}** (P1-P4 all hold).")
A('')
A('| rule | card 1 (band) | card 1 pass | card 0 (band) | card 0 pass |')
A('|---|---|---|---|---|')
for r in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4'):
    a, b = S['part_A']['v31'][C1][r], S['part_A']['v31'][C0][r]
    bw1 = f", {a['band_W']:.2f} W" if a['band_W'] else ''
    bw0 = f", {b['band_W']:.2f} W" if b['band_W'] else ''
    A(f"| {r} | {a['band']:.0%}{bw1} | **{a['verdict']}** {a['pass']}/{a['n']} ({100 * a['pass'] / a['n']:.1f}%) | {b['band']:.0%}{bw0} | **{b['verdict']}** {b['pass']}/{b['n']} ({100 * b['pass'] / b['n']:.1f}%) |")
A('')
A('T1: wall cycles; T2: the counter\'s mean; T3: seconds a GEMM (identical to T1 here: the reducer\'s seconds and cycles share the wall time, and '
  'every forecast is made at the run\'s measured clock); E1: J over idle given t; E2: J over idle with t forecast; E3, E4: J with the card at rest, '
  'given t and with t forecast. The bands are 2 x MM1-v3.1\'s own held-out error (card 1\'s equal E215 arm B\'s registered bands).')
A('')
A('**At MM1-v3.1\'s bands, REPORTED beside:** ' + '; '.join(
    f"{MN[mo]} {card[-6:]}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in S['part_A'][mo][card].items())
    for mo in ('v3', 'v2') for card in (C1, C0)) + '.')
A('')
A('## 3. The errors, per case (no configuration twin; all cases and twins beside)')
A('')
for scope in (C1, C0, 'pooled'):
    A(f"**{scope}**")
    A('')
    A('| quantity | MM1-v3.1 no twin | MM1-v3 no twin | MM1-v2 no twin | MM1-v3.1 all | MM1-v3.1 twins |')
    A('|---|---|---|---|---|---|')
    for q, lab in (('wall', 'T1 wall cycles'), ('mean', 'T2 counter mean'), ('sec', 'T3 seconds a GEMM'), ('E1', 'E1 J over idle given t'),
                   ('E2', 'E2 J over idle, t forecast'), ('E3', 'E3 J at rest given t'), ('E4', 'E4 J at rest, t forecast')):
        if q in ('E1', 'E2'):
            cells = [T[mo][q][scope]['no_twin'] for mo in ('v31', 'v3', 'v2')] + [T['v31'][q][scope]['all'], T['v31'][q][scope]['twin']]
            A(f"| {lab} (3 W and above) | " + ' | '.join(fx(c['relative']) for c in cells) + ' |')
            A(f"| {lab}, watts cases | " + ' | '.join(fw(c['watts']) for c in cells) + ' |')
        else:
            cells = [T[mo][q][scope]['no_twin'] for mo in ('v31', 'v3', 'v2')] + [T['v31'][q][scope]['all'], T['v31'][q][scope]['twin']]
            A(f"| {lab} | " + ' | '.join(fx(c) for c in cells) + ' |')
    A('')
A(f"Twins (configuration in the model's training set from E208/E212 on these cards): MM1-v3.1 {FJ['twins_summary']['v31']['time_twin_cases']} time "
  f"and {FJ['twins_summary']['v31']['energy_twin_cases']} energy cases of {FJ['twins_summary']['v31']['cases']}; MM1-v3 "
  f"{FJ['twins_summary']['v3']['time_twin_cases']} / {FJ['twins_summary']['v3']['energy_twin_cases']}; MM1-v2 {FJ['twins_summary']['v2']['time_twin_cases']} / "
  f"{FJ['twins_summary']['v2']['energy_twin_cases']}. MM1-v2 prices energy for random, zeros and ones only (98 runs NOT FORECAST in energy).")
A('')
A('**By card and format** (MM1-v3.1, no twin; MM1-v3 and MM1-v2 in `scores-unread-e214.json` > by_card_format_kind):')
A('')
A('| card | format | wall | J over idle given t (3 W and above) | J at rest given t |')
A('|---|---|---|---|---|')
for card in (C1, C0):
    for fmt in ('fp32', 'fp16', 'int8'):
        x = S['by_card_format_kind']['v31'].get(f'{card}|{fmt}|ALL')
        if x:
            A(f"| {card} | {fmt} | {fx(x['wall']['no_twin'])} | {fx(x['E1']['no_twin']['relative'])} | {fx(x['E3']['no_twin'])} |")
A('')
A('## 4. The comparisons (exact two-sided sign test, alpha 0.05; per case; ties at each card\'s replicate floor)')
A('')
A('| pair | rule | pooled: A closer / B closer / ties, p | card 1 | card 0 |')
A('|---|---|---|---|---|')
for key in ('MM1-v3.1 vs MM1-v3', 'MM1-v3.1 vs MM1-v2', 'MM1-v3 vs MM1-v2'):
    for r in ('H1', 'H2', 'H3', 'H4', 'H5'):
        x = S['head_to_head'][key][r]

        def fh(y):
            p = '-' if y['p'] is None else f"{y['p']:.2g}"
            return f"**{y['verdict']}** {y['closer_A']}/{y['closer_B']}/{y['ties']}, p {p}"
        A(f"| {key} | {r} | {fh(x['pooled'])} | {fh(x[C1])} | {fh(x[C0])} |")
A('')
A('H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t, H5 J over idle with t forecast. Over the cases that are twins for neither model '
  '(REPORTED, `scores-unread-e214.json` > head_to_head) every verdict is the same. MM1-v3.1\'s time form is MM1-v3\'s refitted (its declaration\'s '
  'outcome), so the two differ by less than either\'s error and most cases tie.')
A('')
SV = S['part_S']['v31']
S3 = S['part_S']['v3']
A('## 5. The switch-pattern arms (group S: E214\'s 20 new tile kinds, 33 arms, 54 runs), Q218\'s test')
A('')
A(f"- **Q1, W over idle given t** ({SV['Q1']['cases']} cases at 3 W and above): MM1-v3.1 + the counts **{fx(SV['Q1']['model'])}** against the null N "
  f"(each format's mean of zeros, ones and random, the same model) {fx(SV['Q1']['N'])}; MM1-v3.1 closer in {SV['Q1']['closer_model']}, N in "
  f"{SV['Q1']['closer_N']}, {SV['Q1']['ties']} tie; p = {SV['Q1']['p']:.2g}. N2 (ones and random, REPORTED) {fx(SV['Q1']['N2_REPORTED'])}.")
A(f"- **Q2, the share of D** (E210's metric; {SV['Q2']['cases']} cases with a random and a zeros case of the same card, shape, format and mask): "
  f"**{fx(SV['Q2']['model_pct_of_D'])} of D** against N's {fx(SV['Q2']['N_pct_of_D'])}; closer {SV['Q2']['closer_model']} / {SV['Q2']['closer_N']}; "
  f"p = {SV['Q2']['p']:.2g}.")
A(f"- By format (Q1): " + '; '.join(f"{f} {fx(v)}" for f, v in SV['by_format_Q1'].items()) + '. By card: ' +
  '; '.join(f"{c} {fx(v)}" for c, v in SV['by_card_Q1'].items()) + '.')
A(f"- MM1-v3 + the same counts (REPORTED): Q1 {fx(S3['Q1']['model'])} vs N {fx(S3['Q1']['N'])} ({S3['Q1']['closer_model']}/{S3['Q1']['closer_N']}, "
  f"p {S3['Q1']['p']:.2g}); Q2 {fx(S3['Q2']['model_pct_of_D'])} of D vs {fx(S3['Q2']['N_pct_of_D'])}: PASS by the same rule.")
sg = S['sp_ar4_gate_REPORTED']
A('- **The sp_ar4 gate** (declared before the read: arow50\'s, (0.5, 0, 0)): J over idle given t ' + '; '.join(
    f"{k.split('|')[1]} declared gate {100 * v['v31_e_E1_arow50_gate']:+.1f}%, the frozen literal (no gate, REPORTED) {100 * v['v31_e_E1_literal_no_gate']:+.1f}%"
    for k, v in sg.items()) + ' (MM1-v3.1).')
gc = S['group_C_REPORTED']
A(f"- Group C, the sparse50 pools at the committed sparse50 row (REPORTED): MM1-v3.1 J over idle given t {fx(gc['v31']['E1']['relative'])}, MM1-v3 {fx(gc['v3']['E1']['relative'])}.")
A('')
A('## 6. Did any E214 point enter a fit? No')
A('')
A(DE['a2_fit_inclusion']['finding'])
A('')
A('## 7. Earlier reads of E214 (disclosed in the declaration, section g)')
A('')
for k, v in DE['g_earlier_reads'].items():
    if isinstance(v, dict):
        A(f'- **{k}**: ' + '; '.join(f'{k2}: {v2}' for k2, v2 in v.items()))
    else:
        A(f'- **{k}**: {v}')
A('')
A('## 8. Post hoc: where MM1-v3.1\'s time misses sit (REPORTED; read after the scores, deciding nothing)')
A('')
g = PH['groups']
A(f"{len(PH['T1_misses_v31'])} of {PH['no_twin_time_cases']} no-twin cases miss T1's band. No-twin wall rms by group (MM1-v3.1 / MM1-v3 / MM1-v2):")
A('')
A('| group | MM1-v3.1 | MM1-v3 | MM1-v2 | T1 misses |')
A('|---|---|---|---|---|')
for k in ('mask: full chip', 'mask: subset mask', 'KB: KB 1', 'KB: KB 2-4', 'KB: KB 5-16', 'KB: KB > 16', 'NB: NB 1', 'NB: NB 2-4', 'NB: NB > 4',
          "depth: past the first sweep's largest K", 'kind: zeros', 'kind: random', 'kind: ones', 'kind: sparse50 pools', 'top family: blind',
          'top family: mech', 'tag: MQ2-mixed', 'tag: bl-held', 'tag: bl-mixed', 'tag: MQ6', 'tag: bl-L3'):
    if k in g:
        x = g[k]
        A(f"| {k} | {fx(x['v31'])} | {fx(x['v3'])} | {fx(x['v2'])} | {x['T1_misses_v31']} |")
A('')
A('The largest misses (MM1-v3.1 / MM1-v3 / MM1-v2): ' + '; '.join(f"{m['arm']} {m['e_v31_pct']:+.1f} / {m['e_v3_pct']:+.1f} / {m['e_v2_pct']:+.1f}%"
                                                              for m in PH['T1_misses_v31'][:12]) + '. ' +
  f"{sum(1 for m in PH['T1_misses_v31'] if m['e_v31_pct'] > 0)} of the {len(PH['T1_misses_v31'])} misses are over-forecasts (MM1-v3.1 slower "
  'than the card), mostly mid-depth shapes (KB 2-16, NB above 4) on both cards; '
  f"{sum(1 for m in PH['T1_misses_v31'] if m['e_v31_pct'] < 0)} are under-forecasts, most on spread or offset masks (0x11111111, 0x1111, the "
  '24-shire 4x4x8 int8 pair). KB 1, deep K past the first sweep\'s largest, the L3 ladder (bl-L3) and the MQ6 pairs hold to 1-5%. MM1-v3 misses '
  'the same cases (its time form is the same); MM1-v2 is closer on several full-chip zeros shapes and worse on the masks.')
A('')
A('## 9. Departures, gaps and NOT RUN')
A('')
A('- The pass rule is this lane\'s, declared before the read: E215\'s registered rule form (bands, 90%, watts at points under 3 W) applied to an '
  'unread sweep, plus Q218\'s switch test. Card 0\'s bands were computed by E215\'s own code from MM1-v3.1\'s record (card 0\'s B2); its watts band '
  'and ties use E212 a1c0-S1/S2\'s replicate spread (no E213 or E215 arm ran on card 0).')
A('- T3 equals T1 identically in this run form (section 2); both are printed.')
A('- MM1-v2: energy NOT FORECAST for the 98 runs of new tiles and sparse50 pools (it prices random, zeros and ones only), as MM1-v3\'s caller of '
  'MM1-v2 does.')
A('- The sp_ar4 gate is a declared input (arow50\'s), not the frozen code\'s literal reading of an unknown kind name; both are printed.')
A('- The scorer was tested on a stand-in day built from the forecasts alone before the read (its outputs kept apart, never a result); it was not '
  'changed after the read. The post hoc reading was re-run once after the read with kind groups added (post hoc either way).')
A('- NOT RUN here: an independent verifier (the next lane); the model session\'s sealed E214 forecasts (27bf4e19, 804e269b; theirs to score); '
  'phi = 1 for the new kinds; a card-held-out reading.')
A('- No E215 datum was opened at any step: the earlier-reads search skipped the E215 card lanes and every E215 data path.')
A('')
A('## 10. Files and how to reproduce')
A('')
A('- `DECLARED-unread-e214.md` / `.json` (step 1), `inputs/step1/` (runs listed from schedules and queues, fit inclusion and phi, count cells, '
  'bands, twin keys, the earlier-reads search), `inputs/step2/` (conditions, each model\'s forecasts), `forecasts-unread-e214.csv` / `.json` '
  '(step 2), `scores-unread-e214.json` / `-cases.csv` / `-runs.csv` (step 3), `posthoc-time-misses.json`, `recheck.json`, `logs/`, `scripts/`.')
A('- From a lane folder holding `work/lab` (git archive of GitHub main 8bde0182: tools/matmul/mm1/v3.1, v3, v2, tools/claims-v3/e214, '
  'tools/claims-v3/e215/rules_e215.py and rules-e215.json) and `work/counts-e214` (the counts-e214 land dir), each with `/usr/bin/python3 -I -B` and '
  'single-threaded: s01_list.py, s01b_models.py, s01c_cells.py (v31, v3), s01d_bands.py, s01g_search.py, s01e_declare.py; s02a_conditions.py, '
  's02b_forecast.py (v31, v3, v2), s02c_merge.py; s03_score.py; s03p_posthoc.py; s04_recheck.py; s05_land.py. `SHA256SUMS`: every file here but itself.')
A('')
open(os.path.join(D, 'README.md'), 'w').write('\n'.join(md))

# ------------------------------------------------------------------ SHA256SUMS and the scan
files = sorted(os.path.relpath(os.path.join(dp, f), D) for dp, _, fs in os.walk(D) for f in fs)
with open(os.path.join(D, 'SHA256SUMS'), 'w') as fh:
    for f in files:
        fh.write(f'{sha(os.path.join(D, f))}  {f}\n')
HOME = os.path.expanduser('~')
bad = re.compile('|'.join(re.escape(x) for x in (HOME, os.path.basename(HOME), '/' + 'home' + '/', 'moved-from' + '-intel', 'scratch' + 'pad',
                                                  '/tmp/' + 'claude-', '.' + 'claude')))   # built at run time: no login written in this file
hits = []
for f in files + ['SHA256SUMS']:
    t = open(os.path.join(D, f), errors='replace').read()
    m = bad.search(t)
    if m:
        hits.append((f, m.group(0)))
r = subprocess.run(['git', '-C', LAB, 'ls-tree', '-r', '--name-only', 'HEAD', REL], capture_output=True, text=True)
print('land files', len(files) + 1, 'SHA256SUMS', sha(os.path.join(D, 'SHA256SUMS')))
print('scan hits', hits)
print('paths already at LAB HEAD under', REL, ':', len([x for x in r.stdout.splitlines() if x.strip()]))
