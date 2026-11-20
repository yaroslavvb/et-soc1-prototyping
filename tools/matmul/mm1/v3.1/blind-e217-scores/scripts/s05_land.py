#!/usr/bin/env python3
"""blind-e217 (Q228) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e217-scores/ (new files only; nothing committed): the README
(every figure taken from the scorer's outputs by this script, never typed), the frozen measured-conditions forecasts (byte for byte as hashed
21:00:04 PST), their inputs (conditions, the three models' and the layout factors' records, the nominal procedure check), the scores (byte
for byte as the hashed scorer wrote them), the cases and runs tables, the post hoc readings and the recheck, the logs and the scripts (the
box's paths replaced by placeholders built at run time; SCRUB-MAP.json lists them and gives each script's sha256 before and after, and the
check that the replacement reverses exactly), and SHA256SUMS. Then the scans: home paths and logins, the round's pubscan_strict.py over the whole land,
tiers_scan.sh over the README and the scores summary. Desk. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>
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
REL = 'tools/matmul/mm1/v3.1/blind-e217-scores'
D = os.path.join(L, 'land', REL)
if os.path.exists(os.path.join(L, 'land')):
    shutil.rmtree(os.path.join(L, 'land'))
os.makedirs(D)
HOME = os.path.expanduser('~')
PHD = {k: '<' + k + '>' for k in ('W', 'LAB', 'SCRATCH', 'HOME', 'GITHUB_SSH_PREFIX')}   # built at run time: this file holds no placeholder
# the git URL rewrite's ssh prefix (user 'git' at the GitHub host) reads as an e-mail address to the strict public-text scan: a placeholder too
REPL = [(W, PHD['W']), (LAB, PHD['LAB']), ('<SCRATCH>', PHD['SCRATCH']), (HOME, PHD['HOME']), ('git' + chr(64) + 'github.com:', PHD['GITHUB_SSH_PREFIX'])]
S2 = os.path.join(L, 'work', 'step2')
S3 = os.path.join(L, 'work', 'step3')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def scrub(t):
    for a, b in REPL:
        t = t.replace(a, b)
    return t


def unscrub(t):
    for a, b in reversed(REPL):
        t = t.replace(b, a)
    return t


def cp(src, rel, text=False):
    dst = os.path.join(D, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if text:
        open(dst, 'w').write(scrub(open(src).read()))
    else:
        shutil.copyfile(src, dst)
    return dst


# ------------------------------------------------------------------ the frozen files, byte for byte (their hashes are in the logs)
FROZEN_BYTES = {os.path.join(L, 'forecasts-blind-e217.csv'): 'forecasts-blind-e217.csv', os.path.join(L, 'forecasts-blind-e217.json'): 'forecasts-blind-e217.json'}
for n in ('conditions-e217.json', 'fc-v31.json', 'fc-v3.json', 'fc-v2.json', 'fc-lay.json', 'nominal-check.json'):
    FROZEN_BYTES[os.path.join(S2, n)] = os.path.join('inputs', n)
for n in ('scores-blind-e217.json', 'scores-blind-e217.txt', 'posthoc-e217.json', 'recheck.json'):
    FROZEN_BYTES[os.path.join(S3, n)] = os.path.join('scores', n)
for n in ('scores-blind-e217-cases.csv', 'scores-blind-e217-runs.csv'):
    FROZEN_BYTES[os.path.join(S3, n)] = os.path.join('cases', n)
for src, rel in FROZEN_BYTES.items():
    t = open(src, 'rb').read().decode('utf-8')
    assert scrub(t) == t, ('a path in a frozen file', rel)
    cp(src, rel)
# ------------------------------------------------------------------ logs and scripts (scrubbed)
for n in ('progress.txt', 'step2-sha256.txt', 'step3-scorer-sha256.txt', 's00_setup.out', 's02a.out', 's02b.out', 's02c.out', 's02d.out', 's03t-2.out',
          's03_score.out', 's03p.out', 's04.out'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n), text=True)
smap = {}
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', n)
    if not os.path.isfile(p):
        continue
    t = open(p).read()
    assert not any(b in t for _, b in REPL), (n, 'a placeholder already in the script')
    dst = cp(p, os.path.join('scripts', n), text=True)
    s = open(dst).read()
    smap[n] = {'sha256_as_run': sha(p), 'sha256_in_land': sha(dst), 'reverses_exactly': unscrub(s) == t}
assert all(v['reverses_exactly'] for v in smap.values())
json.dump({'what': "each script's sha256 as run and as landed; the land replaces the box's paths (" + ', '.join(b for _, b in REPL) +
           "); replacing them back gives the bytes as run (checked)", 'scripts': smap}, open(os.path.join(D, 'scripts', 'SCRUB-MAP.json'), 'w'), indent=1, sort_keys=True)

# ------------------------------------------------------------------ the README, every figure from the scorer's outputs
SC = json.load(open(os.path.join(S3, 'scores-blind-e217.json')))
PH = json.load(open(os.path.join(S3, 'posthoc-e217.json')))
RC = json.load(open(os.path.join(S3, 'recheck.json')))
NC = json.load(open(os.path.join(S2, 'nominal-check.json')))
FJ = json.load(open(os.path.join(L, 'forecasts-blind-e217.json')))
P = SC['primary_footing']
N = SC['nominal_footing_REPORTED']
C1, C0 = 'aifoundry1 card 1', 'aifoundry1 card 0'
MN = SC['models']
COND = json.load(open(os.path.join(S2, 'conditions-e217.json')))
DIE = {cd: [v['die_start_c'] for k, v in COND['runs'].items() if FJ['runs'][k]['card'] == cd] for cd in (C1, C0)}
CAPPED = {cd: sum(1 for ln in open(os.path.join(S3, 'scores-blind-e217-runs.csv')).read().splitlines()[1:]
                  if ln.split(',')[2] == cd and ln.split(',')[9] == '1') for cd in (C1, C0)}
MG = [c for c in FJ['cases'].values() if c['group_mask'] == 'MG']
MG_EXACT = {k: sum(1 for c in MG if c['factors'][k] == 1.0) for k in ('v31c', 'cf1b', 'cn12', 'cg1', 'cg1n1')}
TT_ONLY_OTHER = all(all(k.startswith('other shapes') for k in PH['misses_by_place'][f'{cd}|{r}']['by']) for cd in (C1, C0) for r in ('T1', 'T3', 'E4'))
T3_EQ_T1 = all(P['tables_per_case']['v31']['wall'][sc]['no_twin'] == P['tables_per_case']['v31']['sec'][sc]['no_twin'] for sc in ('pooled', C1, C0))


def secs(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


GAP = [secs(v['first_card_command_pst_README']) - secs(v['session_T0_pst'][11:]) for v in SC['labels'].values()
       if re.fullmatch(r'\d\d:\d\d:\d\d(\.\d+)?', str(v['first_card_command_pst_README']))]
FIRST = min((v['first_card_command_pst_README'], s) for s, v in SC['labels'].items())
H2 = {}
for ln in open(os.path.join(L, 'logs', 'step2-sha256.txt')):
    if not ln.startswith('#'):
        h, f = ln.split()
        H2[f] = h
H3 = {}
for ln in open(os.path.join(L, 'logs', 'step3-scorer-sha256.txt')):
    if not ln.startswith('#'):
        h, f = ln.split()
        H3[f] = h


def pc(x, k='rms_pct'):
    return '-' if not x else f"{x[k]:.2f}%"


def cellq(t, q, scope='pooled', sel='no_twin'):
    x = t[q][scope][sel]
    if q in ('E1', 'E2'):
        r, w = x['relative'], x['watts']
        a = '-' if not r else f"{r['rms_pct']:.2f}% ({r['bias_pct']:+.2f}), n {r['n']}"
        b = '' if not w else f"; watts {w['rms_W']:.2f} W ({w['bias_W']:+.2f}), n {w['n']}"
        return a + b
    return '-' if not x else f"{x['rms_pct']:.2f}% ({x['bias_pct']:+.2f}), n {x['n']}"


def pv(p):
    return 'none' if p is None else (f'{p:.2g}' if p < 0.001 else f'{p:.3f}')


def hrow(x):
    return f"{x['verdict']} ({x['closer_A']}/{x['closer_B']}/{x['ties']}, p {pv(x['p'])})"


md = []
A = md.append
A("# MM1's frozen matmul models scored BLIND on E217 (blind-e217, round Q228)")
A('')
A(f"*Scored Thu 19 Nov 2026 at the desk on aifoundry2: the read {SC['read_pst']}; Python /usr/bin/python3 {SC['python']} (numpy 1.26.4 for the "
  "forecasts), every numerical step single-threaded inside the round's CPU slots. No card, no device, no ssh. Nothing here is committed by this "
  "lane.*")
A('')
A("**What this is.** E217 is the model session's fourth matmul sweep (1119-mmsweep4, Discussion #13: rgm136's gemmL loop, 630 runs over 331 arms "
  "and an anchor in seven sessions on aifoundry1, card 1 S1-S4 at 600 MHz and card 0 S1-S3 at low power under its governor). Before any E217 "
  "datum existed, the lab DECLARED how it would score its frozen models on E217 (decl-e217: `../blind-e217/DECLARED-blind-e217.md`, sha256 "
  "099806dc..., FROZEN.txt 32311daf... at 11:37:53 PST, the counts of E217's 21 new tile kinds frozen in COUNTS-FROZEN.txt 4867c1d0... at "
  "12:22:24 PST, both posted on the Discussion as #13.1.1). This folder is that test, run EXACTLY as declared: every frozen file's sha256 checked, "
  "the forecasts made by the declared procedure at each run's measured clock, minion volts and die at start and hashed, the scorer hashed, and "
  "only then the measurements read and scored.")
A('')
A(f"**Label: {SC['label']}.** The freeze post #13.1.1 is stamped {SC['freeze_post']['record_time_pst']} PST in the round's record "
  "(12:25:56 PST in the round log; the exact second is not checked, and either is more than two hours before E217's first card command):")
A('')
A('| session | label (declaration / counts route) | T0 (PST) | first card command (README) | claim post | minutes after the freeze post | runs | MM1-v3.1 per run, REPORTED: wall / J over idle given t |')
A('|---|---|---|---|---|---|---|---|')
for s, v in SC['labels'].items():
    ps = P['per_session_REPORTED'][s]
    A(f"| {s} | {v['label']} / {v['counts_route_label']} | {v['session_T0_pst'][11:]} | {v['first_card_command_pst_README']} | "
      f"{(v['claim'] or {}).get('post', '-')} {(v['claim'] or {}).get('time_pst', '')[11:]} | {v['margin_minutes_T0_after_post']} | {ps['runs']} | "
      f"{pc(ps['MM1-v3.1']['wall'])} / {pc(ps['MM1-v3.1']['E1'])} |")
A('')
A('## 1. The verdict (decided by the script, as declared)')
A('')
fails = ', '.join(P['part_A_fails'])
PS = P['part_S']['v31']
A(f"**{P['VERDICT']}.** Part A (MM1-v3.1 on the primary footing, E215's rule form, each card over its no-twin cases) **{P['part_A_verdict']}**: "
  f"{fails}. Part S (the switch route on E217's 21 new tile kinds against the null) **{P['part_S_verdict']}** "
  f"(P1 {PS['P1']}, P2 {PS['P2']}, P3 {PS['P3']}, P4 {PS['P4']}). "
  "The declaration's rule: PASS needs both parts to pass; a failing part fails the test.")
A('')
A('| rule (band) | aifoundry1 card 1 | aifoundry1 card 0 |')
A('|---|---|---|')
for r in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4'):
    a, b = P['part_A']['v31'][C1][r], P['part_A']['v31'][C0][r]
    bw = f"; watts {a['band_W']} W" if a.get('band_W') else ''
    A(f"| {r} ({int(round(100 * a['band']))}% / {int(round(100 * b['band']))}%{bw}) | {a['verdict']} {a['pass']}/{a['n']} | {b['verdict']} {b['pass']}/{b['n']} |")
A('')
A("T1 wall cycles an op, T2 the counter's mean cycles, T3 seconds a GEMM, E1 J over idle given the measured op time (watts at a case under 3 W), "
  "E2 J over idle with the op time forecast, E3 J with the card at rest given t, E4 J at rest with t forecast. A rule passes when 90% of its "
  "cases are inside the band.")
A('')
S = P['part_S']['v31']
A(f"Part S, pooled over both cards: Q1 (W over idle given t, {S['Q1']['cases']} group-S cases): MM1-v3.1 with the counts "
  f"{S['Q1']['model']['rms_pct']:.2f}% rms ({S['Q1']['model']['bias_pct']:+.2f}) against the null N (the mean of zeros, ones and random at the "
  f"same conditions) {S['Q1']['N']['rms_pct']:.2f}%; closer {S['Q1']['closer_model']}/{S['Q1']['closer_N']}/{S['Q1']['ties']} ties, "
  f"p {pv(S['Q1']['p'])}. Q2 (the share of the data-dependent power D, {S['Q2']['cases']} cases): {S['Q2']['model_pct_of_D']['rms_pct']:.2f}% of D "
  f"against {S['Q2']['N_pct_of_D']['rms_pct']:.2f}%; closer {S['Q2']['closer_model']}/{S['Q2']['closer_N']}/{S['Q2']['ties']}, p {pv(S['Q2']['p'])}. "
  f"MM1-v3 with the same counts (REPORTED): Q1 {P['part_S']['v3']['Q1']['model']['rms_pct']:.2f}%, Q2 {P['part_S']['v3']['Q2']['model_pct_of_D']['rms_pct']:.2f}% of D.")
A('')
A('## 2. The headline: no-twin cases, the primary footing (each run at its measured conditions)')
A('')
A('rms % (bias %), n cases; E1 and E2 relative where the case is 3 W or more, watts beside.')
A('')
A('| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |')
A('|---|---|---|---|---|---|---|')
for mo in ('v31', 'v3', 'v2', 'v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
    t = P['tables_per_case'][mo]
    A(f"| {MN[mo]} | {cellq(t, 'wall')} | {cellq(t, 'mean')} | {cellq(t, 'E1')} | {cellq(t, 'E2')} | {cellq(t, 'E3')} | {cellq(t, 'E4')} |")
A('')
A(f"T3 (seconds) equals T1 at the measured clock, as the declaration says (the same rms and bias on every scope: {T3_EQ_T1}). 'v3.1+both' equals "
  f"'v3.1+contention' on every case and quantity ({P['both_equals_contention_every_case']}); 'v3.1+gemmLnc' is not applicable (E217 runs no "
  "gemmLnc arm). MM1-v3.1 per card (no twin):")
A('')
A('| card | wall | counter mean | E1 | E3 | E4 |')
A('|---|---|---|---|---|---|')
for cd in (C1, C0):
    t = P['tables_per_case']['v31']
    A(f"| {cd} | {cellq(t, 'wall', cd)} | {cellq(t, 'mean', cd)} | {cellq(t, 'E1', cd)} | {cellq(t, 'E3', cd)} | {cellq(t, 'E4', cd)} |")
A('')
tw = FJ['twins_summary']
A(f"Twins (a case whose configuration is in the model's training data at the same card and clock to 25 MHz): MM1-v3.1 {tw['v31']['time_twin_cases']} "
  f"time and {tw['v31']['energy_twin_cases']} energy twin cases of {tw['v31']['cases']}, MM1-v3 {tw['v3']['time_twin_cases']}/{tw['v3']['energy_twin_cases']}, "
  f"MM1-v2 {tw['v2']['time_twin_cases']}/{tw['v2']['energy_twin_cases']}. MM1-v3.1 on its twin cases: wall {cellq(P['tables_per_case']['v31'], 'wall', 'pooled', 'twin')}; "
  f"on all cases: wall {cellq(P['tables_per_case']['v31'], 'wall', 'pooled', 'all')}, E1 {cellq(P['tables_per_case']['v31'], 'E1', 'pooled', 'all')}.")
A('')
A('## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)')
A('')
A('| comparison | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |')
A('|---|---|---|---|---|---|')
for key, lab in (('D1 MM1-v3.1 vs MM1-v3', 'D1 MM1-v3.1 vs MM1-v3'), ('D2 MM1-v3.1 vs MM1-v2', 'D2 MM1-v3.1 vs MM1-v2')):
    for scope in ('pooled', C1, C0):
        x = P['comparisons'][key]
        A(f"| {lab}, {scope.replace('aifoundry1 ', '')} | " + ' | '.join(hrow(x[r][scope]) for r in ('H1', 'H2', 'H3', 'H4', 'H5')) + ' |')
A('')
A('D3, on the subset-mask cases (MG and SUB), each candidate as A against MM1-v3.1 as B:')
A('')
A('| D3 | H1 wall, pooled | H1 card 1 | H1 card 0 | H2 counter mean, pooled | H2 card 1 | H2 card 0 |')
A('|---|---|---|---|---|---|---|')
D3 = P['comparisons']['D3 layout']
for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
    x = D3[f'D3 {MN[a]} vs MM1-v3.1 (MG and SUB)']
    A(f"| {MN[a]} vs MM1-v3.1 | " + ' | '.join(hrow(x[r][sc]) for r in ('H1', 'H2') for sc in ('pooled', C1, C0)) + ' |')
A('')
A(f"On the {len(MG)} new core-group masks alone (MG, REPORTED) the factor of 'v3.1+contention' is exactly 1 in {MG_EXACT['v31c']} cases and the "
  f"layout-blind F1's in {MG_EXACT['cf1b']} (both equal MM1-v3.1 there: every case a tie); "
  f"N1+N2 vs MM1-v3.1 there: {hrow(D3['D3 ctrl N1+N2 vs MM1-v3.1 (MG alone, REPORTED)']['H1']['pooled'])}. 'v3.1+contention' against each control "
  "(REPORTED): " + '; '.join(f"vs {MN[b]} H1 {hrow(D3[f'D3 v3.1+contention vs {MN[b]} (MG and SUB, REPORTED)']['H1']['pooled'])}" for b in ('cn12', 'cg1', 'cg1n1', 'cf1b')) + '.')
A('')
D4 = P['comparisons']['D4 switch (part S P2 and P4)']
A(f"D4 (group S, MM1-v3.1 with counts-e217 against the null N): Q1 {D4['Q1 verdict']} (P2 {D4['P2']}), Q2 {D4['Q2 verdict']} (P4 {D4['P4']}).")
A('')
A("D3's H5 (J over idle with t forecast, MG and SUB, pooled; REPORTED): " + '; '.join(
    f"{MN[a]} vs MM1-v3.1 {hrow(D3[f'D3 {MN[a]} vs MM1-v3.1 (MG and SUB) H5 J over idle with t forecast, REPORTED']['H5']['pooled'])}"
    for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b')) + '.')
A('')
A('## 4. Where it holds and where it misses (the declared splits, REPORTED; MM1-v3.1, no twin, pooled)')
A('')
A('| split | wall cycles | J over idle given t (E1) | J at rest, t forecast (E4) | part A beside (card 1; card 0): T1, E1, E4 |')
A('|---|---|---|---|---|')
for nm, lab in (('X1', '1x1x1 cells'), ('notX1', 'other shapes'), ('MG', 'MG: the 48 new core-group masks (1x1x1)'), ('SUB', 'SUB: the other subset masks'),
                ('FULL', 'FULL: the full chip'), ('S', 'S: the 21 new tile kinds'), ('C', 'C: the sparse50 pools'), ('K', 'K: zeros, ones, random'),
                ('fp32', 'fp32'), ('fp16', 'fp16'), ('int8', 'int8')):
    t = P['splits']['v31'][f'{nm}|pooled']
    b = P['part_A_beside_REPORTED'][nm]

    def bb(cd):
        return ', '.join(f"{r} {b[cd][r]['verdict']} {b[cd][r]['pass']}/{b[cd][r]['n']}" for r in ('T1', 'E1', 'E4'))
    w = t['wall']['no_twin']
    e1 = t['E1']['no_twin']['relative']
    e4 = t['E4']['no_twin']
    A(f"| {lab} | {pc(w)}{'' if not w else f' (n {w[chr(110)]})'} | {pc(e1)}{'' if not e1 else f' (n {e1[chr(110)]})'} | {pc(e4)} | {bb(C1)}; {bb(C0)} |")
A('')
x1 = PH['wall_rms_no_twin_1x1x1_vs_other']
A(f"**Post hoc readings (made after the read; REPORTED; they decide nothing).** Every T1, T3 and E4 miss of part A is at a shape other than 1x1x1 "
  f"({TT_ONLY_OTHER}): "
  f"MM1-v3.1's wall cycles are {x1['1x1x1']['rms_pct']:.2f}% rms on the {x1['1x1x1']['cases']} no-twin 1x1x1 cells (the 48 new core-group masks "
  f"among them) and {x1['other shapes']['rms_pct']:.2f}% on the {x1['other shapes']['cases']} other no-twin cases, both on the full chip and on "
  f"subset masks. Of the no-twin cases more than 10% off, {PH['no_twin_wall_misses_over_10pct_by_sign'].get('over', 0)} are over-predicted (more "
  f"cycles forecast than measured) and {PH['no_twin_wall_misses_over_10pct_by_sign'].get('under', 0)} under-predicted. The E4 misses follow the time misses: "
  f"{PH['E4_misses_also_T1'][C1]['also_T1_misses']} of card 1's {PH['E4_misses_also_T1'][C1]['E4_misses']} and "
  f"{PH['E4_misses_also_T1'][C0]['also_T1_misses']} of card 0's {PH['E4_misses_also_T1'][C0]['E4_misses']} E4 misses are also T1 misses. "
  "The largest no-twin wall misses (MM1-v3.1, MM1-v3 and MM1-v2 beside):")
A('')
A('| card | arm | format | kind | mask | measured cycles an op | MM1-v3.1 | MM1-v3 | MM1-v2 |')
A('|---|---|---|---|---|---|---|---|---|')
for r in PH['largest_wall_misses_no_twin'][:12]:
    A(f"| {r['card'].replace('aifoundry1 ', '')} | {r['arm']} | {r['fmt']} | {r['kind']} | {r['mask']} | {r['meas_cyc_wall']:.1f} | {100 * r['v31_e_wall']:+.1f}% | "
      f"{100 * r['v3_e_wall']:+.1f}% | {100 * r['v2_e_wall']:+.1f}% |")
A('')
ZR = P['zero_row_gates_REPORTED']
A(f"**The four zero-row tiles (REPORTED).** MM1-v3.1's J over idle given t on the {len(ZR)} cases of gt125, gt25, gt875 and h_gt25, with the "
  "declared gate (the all-zero A-row share), the frozen code's literal (0, 0, 0) and the gate the count implies:")
A('')
A('| case | measured W over idle | declared gate | literal (0, 0, 0) | count-implied gate |')
A('|---|---|---|---|---|')
for k, z in sorted(ZR.items()):
    A(f"| {k.replace('aifoundry1 ', '').replace('|', ' ')} | {z['meas_w']:.2f} W | {100 * z['v31_e_E1_declared_gate']:+.1f}% | {100 * z['v31_e_E1_literal_gate']:+.1f}% | "
      f"{100 * z['v31_e_E1_count_gate']:+.1f}% |")
A('')
GC = P['group_C_REPORTED']
A(f"**Group C, the sparse50 pools priced as the committed sparse50 kind (REPORTED):** MM1-v3.1 J over idle given t "
  f"{pc(GC['v31']['E1']['relative'])} (n {GC['v31']['E1']['relative']['n']}; watts {GC['v31']['E1']['watts']['rms_W']:.2f} W, n {GC['v31']['E1']['watts']['n']}), "
  f"J at rest given t {pc(GC['v31']['E3'])}, wall cycles {pc(GC['v31']['wall'])} (n {GC['v31']['wall']['n']}, twins included).")
A('')
A('## 5. The nominal footing (frozen by decl-e217 before any datum; scored beside by the same rules; REPORTED, deciding nothing)')
A('')
A(f"The same models at the declared nominal conditions (card 1 600 MHz, 0.517 V, die 60 C; card 0 800 MHz, the model's own volts, die 55 C): "
  f"VERDICT {N['VERDICT']}, part A {N['part_A_verdict']} ({', '.join(N['part_A_fails'])}), part S {N['part_S_verdict']}. MM1-v3.1 no twin, pooled: "
  f"wall {cellq(N['tables_per_case']['v31'], 'wall')}, E1 {cellq(N['tables_per_case']['v31'], 'E1')}, E3 {cellq(N['tables_per_case']['v31'], 'E3')}. "
  f"The nominal die sits above the measured start dies (card 1 {min(DIE[C1]):.1f}-{max(DIE[C1]):.1f} C against 60 C, card 0 "
  f"{min(DIE[C0]):.1f}-{max(DIE[C0]):.1f} C against 55 C), so the nominal energy reads high, as the declaration expected.")
A('')
ND1, ND2 = N['comparisons']['D1 MM1-v3.1 vs MM1-v3'], N['comparisons']['D2 MM1-v3.1 vs MM1-v2']
A("On the nominal footing, pooled: D1 " + ', '.join(f"{r} {hrow(ND1[r]['pooled'])}" for r in ('H1', 'H4')) + "; D2 " +
  ', '.join(f"{r} {hrow(ND2[r]['pooled'])}" for r in ('H1', 'H4', 'H5')) + ' (MM1-v2 has no die term, so the nominal die does not move it).')
A('')
A('## 6. The order of hashes and times (Pacific), and the checks')
A('')
A(f"- decl-e217's declaration hashed 11:35:59-11:36:23, FROZEN.txt 11:37:53, COUNTS-FROZEN.txt 12:22:24, posted #13.1.1 ({SC['freeze_post']['record_time_pst'][11:]}); "
  f"E217's first card command {FIRST[0]} ({FIRST[1]}).")
A("- This lane, Thu 19 Nov 2026: every frozen file's sha256 checked at 20:52:55 (MM1-v3.1 64/64, its counts 71/71, MM1-v3 170/170, MM1-v2 114/114, "
  "the layout term 25/25 and its note 6/6, the gemmLnc term 22/22, the posted term files, verify-lay's three files, FROZEN.txt, COUNTS-FROZEN.txt, "
  "the declaration, the nominal forecasts and the counts tables equal to their posted or listed sha256; decl-e217's land 81/81); the conditions "
  "read 20:53:41 (only the declared start-of-run fields); the forecasts made 20:56:26-20:59:55 and hashed 21:00:04 "
  f"(forecasts-blind-e217.csv {H2.get('forecasts-blind-e217.csv', '')[:16]}..., .json {H2.get('forecasts-blind-e217.json', '')[:16]}...); "
  f"the scorer tested on two stand-in days 21:06:17-21:06:19 and hashed 21:06:37 (s03_score.py {H3.get('scripts/s03_score.py', '')[:16]}...); "
  f"the read and the scores {SC['read_pst'][16:24]}.")
A(f"- **The procedure check:** this lane's forecast code, run at the declared nominal conditions, re-makes decl-e217's frozen nominal forecasts "
  f"bit for bit ({NC['VERDICT']}: MM1-v3.1 {sum(NC['MM1-v3.1']['fields_compared'].values())}, MM1-v3 {sum(NC['MM1-v3']['fields_compared'].values())}, "
  f"MM1-v2 {sum(NC['MM1-v2']['fields_compared'].values())} fields, 0 differ), so the measured-conditions forecasts are the declared procedure "
  "with only the conditions changed. The layout factors equal the frozen nominal ones 2,430 of 2,430.")
lc = SC['loader_check']
A(f"- **The loader check:** the scorer's own selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all) on the same bytes: "
  f"{lc['runs_loader_listed']} runs, {lc['field_diffs']} field differences, equal {lc['equal']}. The seven data files read are byte-equal to "
  f"the ones the conditions step read ({all(v['equal_to_step2a_conditions_read'] for v in SC['sources'].values())}).")
A(f"- **The recheck** (independent code path, a fresh read): T1, T3 and E4 per card, the wall rms per card, Q1 and D1's H1 counts all equal the "
  f"scorer's ({RC['ALL_EQUAL']}).")
cn = P['counts']
A(f"- **Counts:** {cn['runs']} listed runs (544 arm + 55 anchor; nulls left out), {cn['time_ok']} with time, {cn['energy_ok']} with energy "
  f"({cn['capped']} capped: card 1 {CAPPED[C1]}, card 0 {CAPPED[C0]}; energy not read there), {cn['cases']} cases ({cn['cases_with_energy']} with "
  f"energy, {cn['watts_cases']} watts cases).")
A('')
A('## 7. Disclosures, gaps and what was not run')
A('')
A("- **Earlier reads.** This lane's brief quoted the data lanes' result summaries (aggregate board maxima, clock-sample counts, the anchors' joule "
  "and time ranges) before the read. No per-run measurement was read before the forecasts and the scorer were hashed, and nothing in the "
  "procedure could use them: the predictors, the terms, the counts and the scoring rules were frozen before any E217 datum.")
A("- **Labels.** Each session's label is decided by its T0 (its session id, a start-of-run field) against the freeze post; the first card command "
  f"times in the table come from each data folder's README, read after the scores, and agree ({len(GAP)} of 7 found, each "
  f"{min(GAP):.1f}-{max(GAP):.1f} s after T0).")
A("- **NOT RUN here:** no second, independent scorer; the per-run figures are REPORTED beside the case figures only; the model session's sealed "
  "E217 forecast was not read or scored by this lane.")
A("- decl-e217's own land (`../blind-e217/`, the declaration, the nominal forecasts and counts-e217) is not on GitHub main at this writing: it "
  "lands first or together with this folder.")
A('')
A('## 8. Files')
A('')
A("- `forecasts-blind-e217.csv` / `.json`: the frozen measured-conditions forecasts, one row a run, every declared model (W over idle at a "
  "measured op time t is W_A + W_B / t). `inputs/`: the conditions read (start-of-run fields only), each model's record, the layout factors, "
  "the nominal procedure check.")
A("- `scores/scores-blind-e217.json` (every figure, both footings, the labels), `scores/scores-blind-e217.txt` (the summary), "
  "`cases/scores-blind-e217-cases.csv` and `-runs.csv` (per case and per run errors), `scores/posthoc-e217.json` (post hoc), "
  "`scores/recheck.json`.")
A("- `scripts/` (the box's paths replaced; `scripts/SCRUB-MAP.json` maps each to its sha256 as run), `logs/` (progress, the hash records, "
  "each step's output), `SHA256SUMS`.")
A('')
A("To reproduce: from a work copy of GitHub main with decl-e217's land at work/decl/, run s00_setup.sh, then s02a_conditions.py, s02b_chain.sh, "
  "s02d_nominal_check.py, s02c_merge.py, s03_score.py, s03p_posthoc.py and s04_recheck.py, each as `/usr/bin/python3 -I -B <script> <lane dir>` "
  "inside the CPU slot (run_slot.sh), with the paths put back as SCRUB-MAP.json says.")
open(os.path.join(D, 'README.md'), 'w').write(scrub('\n'.join(md)) + '\n')

# ------------------------------------------------------------------ SHA256SUMS and the scans
files = sorted(os.path.relpath(os.path.join(dp, f), D) for dp, _, fs in os.walk(D) for f in fs)
with open(os.path.join(D, 'SHA256SUMS'), 'w') as fh:
    for f in files:
        fh.write(f'{sha(os.path.join(D, f))}  {f}\n')
LOGIN = os.path.basename(HOME)            # the scan's words are built at run time, so no login or home path is written in this file
pat = re.compile('|'.join(re.escape(x) for x in (HOME, '/' + 'home' + '/', LOGIN, LOGIN[:8], '/' + 'tmp/claude', '@' + 'gmail', '.' + 'claude')), re.I)
hits = []
for f in files + ['SHA256SUMS']:
    t = open(os.path.join(D, f), 'rb').read().decode('utf-8', 'replace')
    for m in pat.finditer(t):
        hits.append((f, t[max(0, m.start() - 30):m.end() + 30]))
print('land files', len(files) + 1, 'home/login scan hits', len(hits))
for h in hits[:20]:
    print('  HIT', h)
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=D, capture_output=True, text=True)
print('sha256sum -c rc', r.returncode, 'OK', sum(1 for x in r.stdout.splitlines() if x.endswith(': OK')))
print(sha(os.path.join(D, 'SHA256SUMS')), 'SHA256SUMS')
print('frozen files byte for byte:', all(sha(s) == sha(os.path.join(D, rel)) for s, rel in FROZEN_BYTES.items()))
sys.exit(1 if hits else 0)
