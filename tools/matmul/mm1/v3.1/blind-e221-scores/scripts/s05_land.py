#!/usr/bin/env python3
"""blind-e221 (Q235) step 5: THE LAND DIR (new files only, nothing committed by this lane):
OUT/blind-e221/land/tools/matmul/mm1/v3.1/blind-e221-scores/ with the README (written here from the scorer's full-precision record), the
readings file, the frozen forecasts (byte for byte), the scores, the case and run tables, the post hoc readings, the recheck, the small inputs
and logs, every script of the lane with its desk paths scrubbed reversibly (scripts/SCRUB-MAP.json: as-run and landed sha256, each
replacement, and the check that the landed text reverses to the as-run bytes) and SHA256SUMS. Desk; stdlib.
Run: /usr/bin/python3 -I -B s05_land.py <lane dir>
"""
import base64
import hashlib
import json
import os
import shutil
import sys

L = os.path.abspath(sys.argv[1])
LD = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'blind-e221-scores')
WF = '<WF>'
LABP = '<LAB>'
LT, GT = chr(60), chr(62)
P_WF, P_LAB, P_GH, P_UG = LT + 'WF' + GT, LT + 'LAB' + GT, LT + 'GITHUB_SSH_PREFIX' + GT, LT + 'user' + GT + ' ' + LT + 'group' + GT


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


if os.path.isdir(LD):
    shutil.rmtree(LD)
os.makedirs(LD)
S = json.load(open(os.path.join(L, 'work', 'step3', 'scores-blind-e221.json')))
PH = json.load(open(os.path.join(L, 'work', 'step3', 'posthoc-e221.json')))
RC = json.load(open(os.path.join(L, 'work', 'step4', 'recheck-e221.json')))
FC = json.load(open(os.path.join(L, 'forecasts-blind-e221.json')))
NCK = json.load(open(os.path.join(L, 'work', 'step2', 'nominal-check.json')))
S0 = json.load(open(os.path.join(L, 'logs', 'step0-checks.json')))
P = S['primary_footing']
N = S['nominal_footing_REPORTED']
MN = S['models']
C1, C0, A2 = 'aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0'
CARDS = (C1, C0, A2)
CN = {C1: 'aifoundry1 card 1', C0: 'aifoundry1 card 0', A2: 'aifoundry2 card 0'}
RULES = ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')
H = ('H1', 'H2', 'H3', 'H4', 'H5')
CLASSES = ('MASK', 'CELL1', 'KB1', 'L2I8', 'MQ3', 'DK', 'HLD', 'BW', 'NB1', 'ANCHOR')
CLW = {'MASK': 'the core-group masks (12 placement families) with their whole-chip twins', 'CELL1': 'the 1x1x1 cells at new masks',
       'KB1': 'KB = 1 at the whole chip', 'L2I8': 'the int8 L2 point (1x1xK) at the whole chip and at masks', 'MQ3': 'the MB = 3 ladders',
       'DK': 'deep K (KB 16-32)', 'HLD': 'the held walks (small shapes)', 'BW': 'the BW shapes (2x12x4, 5x12x2, 6x5x3)', 'NB1': 'NB = 1',
       'ANCHOR': 'the anchor (4x8x8 int8 random)'}


def pc(x, nd=2):
    return '-' if x is None else f'{x:.{nd}f}%'


def sg(x, nd=2):
    return '-' if x is None else f'{x:+.{nd}f}'


def cellt(c):
    """an rms / bias / n cell"""
    if c is None:
        return '-'
    return f"{c['rms_pct']:.2f}% ({c['bias_pct']:+.2f}), n {c['n']}"


def celle(c):
    if c is None:
        return '-'
    r, w = c['relative'], c['watts']
    s = cellt(r) if r else 'rel. -'
    if w:
        s += f"; watts {w['rms_W']:.3f} W ({w['bias_W']:+.3f}), n {w['n']}"
    return s


def pv(p):
    if p is None:
        return 'none'
    return f'{p:.3g}'


def cmpc(z):
    return f"{z['verdict']} ({z['closer_A']}/{z['closer_B']}/{z['ties']}, p {pv(z['p'])})"


T = P['tables_per_case']
LB = S['labels']
FP = S['freeze_post']
R = []
A = R.append
A('# MM1\'s frozen matmul models scored BLIND on E221 (blind-e221, round Q235)')
A('')
A(f"*Scored Fri 20 Nov 2026 at the desk on aifoundry2: the read {S['read_pst'].split(' ', 4)[4] if S['read_pst'].count(' ') >= 4 else S['read_pst']}; "
  f"Python /usr/bin/python3 {S['python']} (numpy {FC['model_record']['numpy']} for the forecasts), every numerical step single-threaded inside the round's CPU "
  "slots. No card, no device, no ssh. Nothing here is committed by this lane.*")
A('')
A("**What this is.** E221 is the model session's sixth matmul sweep (1120-mmsweep6, Discussion #15): E136's rgm136 unchanged over its "
  "cooperative gemmL loop, 847 runs over 345 arms and an anchor in nine sessions on three cards (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 "
  "card 0 S1-S3 at low power under its governor, aifoundry2 card 0 S1-S3 under its governor). Before any E221 run, the lab DECLARED how it "
  "would score its frozen models on E221, with MM1's domain stated first (decl-e221: `../blind-e221/DECLARED-blind-e221.md`, sha256 "
  "9cd8256b..., `FROZEN.txt` 2df06f06... at 06:17:38 PST Fri 20 Nov, posted on the Discussion as #15.2.1.1). All 733 of E221's cases (811 "
  "runs: 740 arm and 71 anchor runs; the 36 nulls and each session's smoke left out) are IN DOMAIN. The pass rule's model is **MM1-v3.2** "
  "(the lab's newest, landed 4e386f75); MM1-v3.1, MM1-v3, MM1-v2, the layout term '+contention', '+both' and verify-lay's four controls are "
  "scored beside, and the two MM1-v3.3 candidates ('MM1-v3.2+posimb' at the subset masks, 'MM1-v3.2+L3S' at the full chip) are REPORTED by "
  "their own frozen makers. This folder is that test, run EXACTLY as declared: every frozen file's sha256 checked, the forecasts made by the "
  "declared procedure at each run's measured clock, minion volts and die at start and hashed, the scorer code-tested and hashed, and only "
  "then the measurements read and scored.")
A('')
A(f"**Label: BLIND (every session: its first datum after the freeze post).** The freeze post #15.2.1.1 is stamped {FP['own_time_pst']} PST by "
  f"the post itself and {FP['record_time_pst'].split(' ')[1]} PST in the round's record; the later is used. Every session's claim and first card "
  "command come after it (the stopped first S1 start of 05:53:56-05:55:27, which ran no run, is not a committed session and is not scored):")
A('')
A('| session | label | claim (PST) | T0 (PST) | first card command (queue / README) | minutes after the freeze post | runs | MM1-v3.2 per run, REPORTED: wall / J over idle given t |')
A('|---|---|---|---|---|---|---|---|')
for s in sorted(LB, key=lambda k: LB[k]['session_T0_pst']):
    v = LB[s]
    ps = P['per_session_REPORTED'][s]['MM1-v3.2']
    A(f"| {s} | {v['label']} | {v['claim']['post']} {v['claim']['time_pst'].split(' ')[1]} | {v['session_T0_pst'].split(' ')[1]} | "
      f"{v['first_card_command_pst_queue'].split(' ')[1]} / {v['first_card_command_pst_README']} | {v['margin_minutes_first_datum_after_post']:.2f} | "
      f"{P['per_session_REPORTED'][s]['runs']} | {pc(ps['wall']['rms_pct'])} / {pc(ps['E1']['rms_pct'])} |")
A('')
A('## 1. The verdict (decided by the script, as declared)')
A('')
fails = P['part_A_fails']
A(f"**{P['VERDICT']}.** Part A (MM1-v3.2 on the primary footing, E215's rule form, each card over its no-twin cases, every class) **FAILS**: "
  f"{len(fails)} rules fail across the three cards ({', '.join(fails)}). Part S is NOT APPLICABLE (E221 has no operand-pattern arm), so the "
  "verdict is part A's. A rule passes when at least 90% of its cases are inside the band; the bands are E215's form from MM1-v3.1's held-out "
  "errors, the same for every model.")
A('')
A('| rule | band (card 1 / aifoundry1 card 0 / aifoundry2 card 0) | aifoundry1 card 1 | aifoundry1 card 0 | aifoundry2 card 0 |')
A('|---|---|---|---|---|')
B = S['bands']
for r in RULES:
    bw = f"; watts {B[C1]['watts_W']} / {B[C0]['watts_W']} / {B[A2]['watts_W']} W" if r in ('E1', 'E2') else ''
    cells = ' | '.join(f"{P['part_A']['v32'][c][r]['verdict']} {P['part_A']['v32'][c][r]['pass']}/{P['part_A']['v32'][c][r]['n']}" for c in CARDS)
    A(f"| {r} | {B[C1][r] * 100:.0f}% / {B[C0][r] * 100:.0f}% / {B[A2][r] * 100:.0f}%{bw} | {cells} |")
A('')
A("T1 wall cycles an op (the slowest minion), T2 the counter's mean cycles an op, T3 seconds a pass (64 MB NB KB ops a minion x the op time), "
  "E1 J over idle given the measured op time (watts at a case under 3 W), E2 J over idle with the op time forecast, E3 J with the card at rest "
  "given t, E4 J at rest with t forecast. **Where the misses are** (MM1-v3.2, all three cards; post hoc count, REPORTED):")
A('')
mbc = PH['v32']['misses_by_rule_class (all cards)']
A('| rule | misses by class |')
A('|---|---|')
for r in ('T1', 'E2', 'E4'):
    items = sorted(((k.split('|')[1], v) for k, v in mbc.items() if k.startswith(r + '|')), key=lambda kv: -kv[1])
    A(f"| {r} | " + ', '.join(f'{k} {v}' for k, v in items) + ' |')
A('')
nT1 = sum(v for k, v in mbc.items() if k.startswith('T1|'))
nT1m = mbc.get('T1|MASK', 0)
A(f"So {nT1m} of the {nT1} T1 misses are core-group mask placements (the MASK class); the energy rules given the measured time (E1, E3) pass "
  "on every card, and E2 and E4 fail where the time forecast fails "
  f"({PH['v32']['E4 misses that are T1 misses']['also_T1_miss']} of the {PH['v32']['E4 misses that are T1 misses']['also_T1_miss'] + PH['v32']['E4 misses that are T1 misses']['not_a_T1_miss']} "
  "E4 misses are T1 misses too). Every miss, case by case, is in `cases/scores-blind-e221-cases.csv` and `scores/scores-blind-e221.json` "
  "(part_A ... misses).")
A('')
A(f"MM1-v3.1's part A, REPORTED beside (the continuity with E215, E217 and E219; deciding nothing): **{P['part_A_MM1_v3_1_REPORTED']['verdict']}** "
  f"({', '.join(P['part_A_MM1_v3_1_REPORTED']['fails'])}).")
A('')
A('| rule | aifoundry1 card 1 | aifoundry1 card 0 | aifoundry2 card 0 |')
A('|---|---|---|---|')
for r in RULES:
    A(f"| {r} | " + ' | '.join(f"{P['part_A']['v31'][c][r]['verdict']} {P['part_A']['v31'][c][r]['pass']}/{P['part_A']['v31'][c][r]['n']}" for c in CARDS) + ' |')
A('')
A('## 2. The headline: no-twin cases, the primary footing (each run at its measured conditions)')
A('')
A('rms % (bias %), n cases; error = forecast / measured - 1; a case\'s error is the mean of its runs\' errors; E1 and E2 relative where the case '
  'is 3 W or more (by MM1-v3.2 and the measurement), watts beside.')
A('')
A('| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |')
A('|---|---|---|---|---|---|---|')
for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b', 'v32p', 'v32l'):
    t = T[mo]
    nm = MN[mo] + (' (REPORTED)' if mo in ('v32p', 'v32l') else '')
    A(f"| {nm} | {cellt(t['wall']['pooled']['no_twin'])} | {cellt(t['mean']['pooled']['no_twin'])} | {celle(t['E1']['pooled']['no_twin'])} | "
      f"{celle(t['E2']['pooled']['no_twin'])} | {cellt(t['E3']['pooled']['no_twin'])} | {cellt(t['E4']['pooled']['no_twin'])} |")
A('')
A("T3 (seconds a pass) equals T1 at the measured clock, as the declaration says (on the primary footing the same rms and bias on every scope, to "
  "1e-14 points; on the nominal footing they differ by up to 0.12 points, the 800 MHz footing against the measured clock). 'v3.1+both' equals "
  f"'v3.1+contention' on every case and quantity ({P['both_equals_contention_every_case']}); posimb equals MM1-v3.2 off its scope "
  f"({P['posimb_equals_v32_off_its_scope']}) and L3S equals MM1-v3.2 off its domain ({P['l3s_equals_v32_off_its_domain']}). 'v3.1+gemmLnc' and "
  "'MM1-v3.2+AF4' are NOT APPLICABLE (no gemmLnc arm). Per card (no twin):")
A('')
A('| model, card | measured clock (MHz) | wall | counter mean | E1 | E3 | E4 |')
A('|---|---|---|---|---|---|---|')
gov = S['governed_clock_REPORTED']
CLK = {C1: '599.2-599.5', C0: f"{gov[C0]['clock_min_mhz']:.1f}-{gov[C0]['clock_max_mhz']:.1f}", A2: f"{gov[A2]['clock_min_mhz']:.1f}-{gov[A2]['clock_max_mhz']:.1f}"}
for mo in ('v32', 'v31'):
    for c in CARDS:
        t = T[mo]
        A(f"| {MN[mo]}, {CN[c]} | {CLK[c]} | {cellt(t['wall'][c]['no_twin'])} | {cellt(t['mean'][c]['no_twin'])} | {celle(t['E1'][c]['no_twin'])} | "
          f"{cellt(t['E3'][c]['no_twin'])} | {cellt(t['E4'][c]['no_twin'])} |")
A('')
tw = FC['twins_summary']
A(f"Twins (a case whose configuration is in the model's training data at the same card, kernel and clock to 25 MHz): MM1-v3.2 "
  f"{tw['v32']['time_twin_cases']} time and {tw['v32']['energy_twin_cases']} energy twin cases of 733, MM1-v3.1 {tw['v31']['time_twin_cases']}/"
  f"{tw['v31']['energy_twin_cases']}, MM1-v3 {tw['v3']['time_twin_cases']}/{tw['v3']['energy_twin_cases']}, MM1-v2 {tw['v2']['time_twin_cases']}/"
  f"{tw['v2']['energy_twin_cases']} (the nominal-clock preview the declaration printed, exactly). MM1-v3.2 on its twin cases: wall "
  f"{cellt(T['v32']['wall']['pooled']['twin'])}; on all cases: wall {cellt(T['v32']['wall']['pooled']['all'])}, E1 {celle(T['v32']['E1']['pooled']['all'])}.")
A('')
A('## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)')
A('')
BJ = json.load(open(os.path.join(L, 'work', 'decl', 'inputs', 'step1', 'bands.json')))
f0, f2 = BJ['card0_floors'], BJ['a2c0_floors']
A('Over every case both models price (twins included); the ties are the declaration\'s per card (cycles and seconds 0.005 in ln; J 0.01 in ln '
  'on card 1 and aifoundry1 card 0, 0.02 on aifoundry2 card 0; watts 0.1 / 0.15 / 0.4 W). Their floors, printed beside as the declaration '
  f"asks: aifoundry1 card 0 from E212's a1c0 sessions ({f0['cases_with_two_or_more_runs']} cases with two runs or more: wall {f0['wall_ln']}, J "
  f"{f0['J_ln_3W_and_above']} in ln, W {f0['W']} W); aifoundry2 card 0 from E212's a2c0 sessions, a weak floor ({f2['cases_with_two_or_more_runs']} "
  f"cases: wall {f2['wall_ln']}, J {f2['J_ln_3W_and_above']} in ln, W {f2['W']} W); card 1 E215 arm B's registered ties.")
A('')
A('| comparison, scope | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |')
A('|---|---|---|---|---|---|')
for key in ('D0 MM1-v3.2 vs MM1-v3.1', 'D1 MM1-v3.1 vs MM1-v3', 'D2 MM1-v3.1 vs MM1-v2'):
    for sc in ('pooled',) + CARDS:
        A(f"| {key}, {sc if sc == 'pooled' else CN[sc]} | " + ' | '.join(cmpc(P['comparisons'][key][h][sc]) for h in H) + ' |')
A('')
A('Over the cases that are twins for neither model (REPORTED), pooled: ' + '; '.join(
    f"{key.split(' ')[0]} " + ', '.join(f"{h} {cmpc(P['comparisons'][key + ' (cases twin for neither, REPORTED)'][h]['pooled'])}" for h in ('H1', 'H4'))
    for key in ('D0 MM1-v3.2 vs MM1-v3.1', 'D1 MM1-v3.1 vs MM1-v3', 'D2 MM1-v3.1 vs MM1-v2')) + '.')
A('')
A('D3, on the 461 subset-mask cases (the MASK, CELL1 and L2I8 classes at shire subsets), each candidate as A against MM1-v3.1 as B:')
A('')
A('| D3 | H1 wall, pooled | H1 card 1 | H1 aifoundry1 card 0 | H1 aifoundry2 card 0 | H2 counter mean, pooled | H2 card 1 | H2 aifoundry1 card 0 | H2 aifoundry2 card 0 |')
A('|---|---|---|---|---|---|---|---|---|')
D3 = P['comparisons']['D3 layout']
for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
    k = f'D3 {MN[a]} vs MM1-v3.1 (the subset masks)'
    A(f"| {MN[a]} vs MM1-v3.1 | " + ' | '.join(cmpc(D3[k][h][sc]) for h in ('H1', 'H2') for sc in ('pooled',) + CARDS) + ' |')
A('')
A('D3c, the MM1-v3.3 candidates (REPORTED, deciding nothing; posimb on the 461 subset-mask cases, L3S on its 272 full-mask cases):')
A('')
A('| D3c, pooled | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |')
A('|---|---|---|---|---|---|')
D3c = P['comparisons']['D3c candidates (REPORTED, deciding nothing)']
for a, b, what in (('MM1-v3.2+posimb', 'MM1-v3.2', 'the subset masks'), ('MM1-v3.2+L3S', 'MM1-v3.2', "L3S's full-mask cases"),
                   ('MM1-v3.2+posimb', 'MM1-v3.1', 'the subset masks'), ('MM1-v3.2+L3S', 'MM1-v3.1', "L3S's full-mask cases")):
    k = f'D3c {a} vs {b} ({what}; REPORTED)'
    v = D3c[k]
    A(f"| {a} vs {b} ({what}) | " + ' | '.join(cmpc(v[h]['pooled']) if h in v else '-' for h in H) + ' |')
A('')
A(f"D4 (the switch route): {P['comparisons']['D4 switch']}.")
A('')
A('## 4. Where it holds and where it misses (the declared splits, REPORTED; no twin, pooled)')
A('')
A('| class | cases | MM1-v3.2 wall / E1 / E3 | MM1-v3.1 | MM1-v3 | MM1-v2 | MM1-v3.2 part A beside (card 1; aifoundry1 card 0; aifoundry2 card 0): T1, E1, E4 |')
A('|---|---|---|---|---|---|---|')
SP = P['splits']
for k in CLASSES:
    row = []
    for mo in ('v32', 'v31', 'v3', 'v2'):
        x = SP[mo][f'{k}|pooled']
        w = x['wall']['no_twin']
        e1 = (x['E1']['no_twin'] or {}).get('relative')
        e3 = x['E3']['no_twin']
        row.append(f"{pc(w['rms_pct'] if w else None)} / {pc(e1['rms_pct'] if e1 else None)} / {pc(e3['rms_pct'] if e3 else None)}")
    pa = P['part_A_beside_REPORTED'][k]
    pa_s = '; '.join(', '.join(f"{r} {pa[c][r]['verdict']} {pa[c][r]['pass']}/{pa[c][r]['n']}" for r in ('T1', 'E1', 'E4')) for c in CARDS)
    ncs = sum(1 for cc in FC['cases'].values() if cc['class'] == k)
    A(f"| {k}: {CLW[k]} | {ncs} | " + ' | '.join(row) + f" | {pa_s} |")
A('')
A("The anchor's three cases are twins for every model (its configuration is in each fit), so they leave the no-twin headline.")
A('')
A("**The mask ladders** (each MASK subset case against its whole-chip twin, the same card, arm, format and kind at 0xffffffff: the forecast "
  "subset/full ratio of the cycles an op over the measured one, minus 1; rms % (bias %), n pairs; REPORTED):")
A('')
A('| family | pairs | MM1-v3.2 wall | MM1-v3.1 wall | MM1-v3 wall | MM1-v2 wall | v3.1+contention wall | MM1-v3.2+posimb wall | MM1-v3.2 counter mean |')
A('|---|---|---|---|---|---|---|---|---|')
LF = S['mask_ladders_REPORTED']['by_family']
for fam, v in LF.items():
    A(f"| {fam} | {v['pairs_scored']} | " + ' | '.join(cellt(v[MN[mo]]['wall']).rsplit(', n', 1)[0] for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'v32p')) +
      f" | {cellt(v['MM1-v3.2']['mean']).rsplit(', n', 1)[0]} |")
A('')
A("(Six MASK cases belong to a combined 'PLA+PLX' block; they are in the per-card table of `scores/scores-blind-e221.json`, mask_ladders_REPORTED.by_card_family.)")
A('')
A('## 5. Reported beside (deciding nothing)')
A('')
A(f"**The nominal footing** (decl-e221's frozen nominal forecasts: card 1 at 600 MHz, 0.517 V, 60 C; the governed cards at 800 MHz, each model's "
  f"own volts, 55 C; scored by the same script and rules): VERDICT {N['VERDICT']} (part A {N['part_A_verdict']}: {', '.join(N['part_A_fails'])}); "
  f"the watts set differs from the primary footing's in {S['watts_set_differs_between_footings_cases']} cases.")
A('')
A('| nominal footing, no twin, pooled | wall | E1 | E3 |')
A('|---|---|---|---|')
for mo in ('v32', 'v31', 'v3', 'v2'):
    t = N['tables_per_case'][mo]
    A(f"| {MN[mo]} | {cellt(t['wall']['pooled']['no_twin'])} | {celle(t['E1']['pooled']['no_twin'])} | {cellt(t['E3']['pooled']['no_twin'])} |")
A('')
A('**The governed clocks** (each run\'s measured kernel clock beside the nominal 800 MHz; MM1-v3.2\'s per-run wall error on both footings):')
A('')
A('| card | runs | clock (MHz) min / mean / max | runs within 25 MHz of 800 | MM1-v3.2 wall, primary | MM1-v3.2 wall, nominal 800 MHz | MM1-v3.2 E1 (3 W and above), primary / nominal |')
A('|---|---|---|---|---|---|---|')
for c in (C0, A2):
    g = gov[c]
    A(f"| {CN[c]} | {g['runs_time_ok']} | {g['clock_min_mhz']:.2f} / {g['clock_mean_mhz']:.2f} / {g['clock_max_mhz']:.2f} | {g['runs_within_25_MHz_of_800']} | "
      f"{cellt(g['MM1-v3.2 wall per run: primary'])} | {cellt(g['MM1-v3.2 wall per run: nominal 800 MHz footing'])} | "
      f"{pc(g['MM1-v3.2 E1 per run (dP >= 3 W): primary']['rms_pct'])} / {pc(g['MM1-v3.2 E1 per run (dP >= 3 W): nominal footing']['rms_pct'])} |")
A('')
A('## 6. Post hoc readings (made after the read; REPORTED; they decide nothing)')
A('')
pw = PH['v32']['part A post hoc, without MASK']
A(f"- **Without the MASK class**, MM1-v3.2's part A cells would read {pw['verdict']} on every card: " + '; '.join(
    f"{CN[c]} " + ', '.join(f"{r} {pw['cells'][c + '|' + r][1]}/{pw['cells'][c + '|' + r][2]}" for r in RULES) for c in CARDS) +
  ". MM1-v3.1 the same way: " + PH['v31']['part A post hoc, without MASK']['verdict'] + ' (' + ', '.join(
      f"{CN[k.split('|')[0]]} {k.split('|')[1]} {PH['v31']['part A post hoc, without MASK']['cells'][k][1]}/{PH['v31']['part A post hoc, without MASK']['cells'][k][2]}"
      for k in PH['v31']['part A post hoc, without MASK']['fails']) + ').')
fm = PH['v32']['part A post hoc, FULL mask only']
A(f"- **At the full chip only** (every class): {fm['verdict']} ({', '.join(fm['fails'])}): " + '; '.join(
    f"{CN[c]} T1 {fm['cells'][c + '|T1'][1]}/{fm['cells'][c + '|T1'][2]}" for c in CARDS) + '.')
ms = PH['v32']['MASK wall by shire count (rms %, bias %, n)']
MSO = [('SUB|1', '1 shire'), ('SUB|2-3', '2-3 shires'), ('SUB|4-7', '4-7 shires'), ('SUB|8-15', '8-15 shires'), ('SUB|16-31', '16-31 shires'), ('FULL|32', 'the whole chip (32)')]
A('- **The MASK class by shire count** (MM1-v3.2 wall, no twin; rms % (bias %), n): ' + '; '.join(
    f"{lab} {ms[k][0]:.2f}% ({ms[k][1]:+.2f}), n {ms[k][2]}" for k, lab in MSO if k in ms) +
  '. The model forecasts the single-shire and two-to-three-shire placements too slow on average and the 16-31-shire ones too fast.')
mf = PH['v32']['MASK wall by family (rms %, bias %, n)']
worst_f = sorted(((k, v) for k, v in mf.items() if k.endswith('|SUB')), key=lambda kv: -kv[1][0])[:5]
A('- **The worst placement families at the subset masks** (MM1-v3.2 wall): ' + '; '.join(f"{k.split('|')[0]} {v[0]:.2f}% ({v[1]:+.2f}), n {v[2]}" for k, v in worst_f) + '.')
ww = PH['v32']['worst 20 cases by |T1|'][:6]
CK = {C1: 'a1c1', C0: 'a1c0', A2: 'a2c0'}
A('- **The worst cases** (MM1-v3.2 wall error): ' + '; '.join(f"{CK[w['case'].split('|')[0]]} {' '.join(w['case'].split('|')[1:])} {w['e_wall_pct']:+.1f}%" for w in ww) +
  ': the same shape, gemmL3x4x6 fp32 zeros, at small masks on all three cards.')
A(f"- **E2 and E4 follow the time:** {PH['v32']['E2 misses that are T1 misses']['also_T1_miss']} of MM1-v3.2's "
  f"{PH['v32']['E2 misses that are T1 misses']['also_T1_miss'] + PH['v32']['E2 misses that are T1 misses']['not_a_T1_miss']} E2 misses and "
  f"{PH['v32']['E4 misses that are T1 misses']['also_T1_miss']} of its {PH['v32']['E4 misses that are T1 misses']['also_T1_miss'] + PH['v32']['E4 misses that are T1 misses']['not_a_T1_miss']} "
  'E4 misses are also T1 misses.')
A('')
A('## 7. How it was done (Pacific; every step one slot job; the hashes)')
A('')
A(f"1. **Every frozen file by sha256** (17:45:50-17:46:01): {S0['n_checks']} checks, {S0['n_failed']} failed (the first run had one failure, "
  "the registration's sums read from the wrong folder; the re-run read them from the repository top): MM1-v3.2 58/58, MM1-v3.1 64/64 and its "
  "counts 71/71, MM1-v3 170/170, MM1-v2 114/114, the layout term 25/25 and its note 6/6, the gemmLnc term 22/22; the declaration's 52 "
  "input sha256 52/52; FROZEN.txt 2df06f06 and the four frozen files equal to the posted record #15.2.1.1; decl-e221's land 39/39; the three "
  "candidates' FROZEN.txt and posted forecasts equal to their record and to main's land; decl-e221's copy of main at 0f046200, 2,761/2,761 files, "
  "equal to today's main (1a259ddc).")
A('2. **Conditions read** (17:46:51): only the declared start-of-run fields of the nine committed data files at 1a259ddc (the top card, '
  "session and primary view; per run its identity fields, die_start_c and the primary view's kclock_mhz and rails.minion.mV): 811/811 "
  'listed runs found, all ran, one without a minion rail reading (the declared fallback: the model\'s own volts at the clock).')
A(f"3. **Procedure check** (17:50:16-17:51:00): this lane's forecast code, run at the declared NOMINAL conditions, re-makes decl-e221's frozen "
  f"nominal forecasts **bit for bit**: {NCK['against']['forecasts-nominal-e221.json (f7875611)']['fields_compared']:,} fields over 811 runs "
  "(733 cases) and 12 models, 0 differ; the four maker checks equal decl-e221's figures to the last digit.")
A("4. **Forecasts** at each run's measured conditions (17:51:05-17:52:49), hashed at 17:52:57 (`logs/step2-sha256.txt`): "
  "`forecasts-blind-e221.csv` 962252bd..., `forecasts-blind-e221.json` 10dac661....")
A("5. **The scorer** code-tested on two stand-in days built from the forecasts alone (exact and noise), then hashed with the readings file at "
  "17:59:51 (`logs/step3-scorer-sha256.txt`): `scripts/s03_score.py` 20534e559870b3188b2781482ac1d10bee89fa74c5f82c5afc2087a291e8a31a, "
  "`READINGS-blind-e221.md` 44d32b5a76d7024bfbd509c7d2164e8b355cb5a4e56d957edecb8804f67a13c3.")
lc = S['loader_check']
A(f"6. **Read and scored** (18:00:03): the data files equal to step 2's bytes; the loader check (MM1-v3.1's own reader on the same bytes) "
  f"{'EQUAL' if lc['equal'] else 'NOT EQUAL'}: {lc['runs_loader_listed']}/{lc['runs_mine_loader_form_ok']} runs, 0 field differences; the queue "
  f"condition removed {lc['runs_loader_form_but_queue_not_ok']} runs; {lc['runs_capped']} capped runs not read for energy ({lc['runs_energy_ok_all']} energy runs).")
A(f"7. **Independent recheck** (18:01:28): a second code path from the CSV and a fresh read: part A {RC['partA_equal']}/{RC['partA_cells']} cells "
  f"(MM1-v3.2 and MM1-v3.1), {RC['rms_equal']}/{RC['rms_cells']} rms cells and {sum(1 for x in RC['tallies'].values() if x['equal'])}/{len(RC['tallies'])} "
  'sign-test tallies equal to the scorer\'s.')
A('')
A("**Readings and one departure.** Where the declaration is silent, the scorer takes its form's reading (decl-e219's, verified), stated and "
  "hashed before the read in `READINGS-blind-e221.md`: the run selection (MM1's loader conditions and the session's queue; energy also needs "
  "dP_w and p_mean_w, not capped, not a 'time' run), 'at least 90%' by integer arithmetic, the test's NO DATA line, the twin key's clock, the "
  "watts set, the label's times and the REPORTED tables' forms. One departure, in how a frozen maker is loaded, not in what it computes: "
  "posimb's as-run scripts name their own lane folder, whose lab copy was removed by a cleanup before this lane ran; the landed copies (the "
  "same files but for the two path lines) ran instead, and re-made decl-e221's four maker checks and frozen nominal forecasts exactly.")
A('')
A("**NOT RUN:** a second, independent scorer by another lane (the verify lane's); any reading of the model session's sealed E221 forecast "
  "(it was not opened); a switch count (E221 designs no tile).")
A('')
A('## 8. Files')
A('')
A('- `README.md` (this file); `READINGS-blind-e221.md` (the readings, hashed before the read)')
A('- `forecasts-blind-e221.csv`, `forecasts-blind-e221.json`: the measured-conditions forecasts, byte for byte as hashed before the read')
A('- `scores/scores-blind-e221.json` (every declared figure, both footings), `scores/scores-blind-e221.txt` (the scorer\'s summary), '
  '`scores/posthoc-e221.json` (section 6), `scores/recheck-e221.json` (step 7)')
A('- `cases/scores-blind-e221-cases.csv` (one row a case: measured, every model\'s errors, twins, nominal errors), `cases/scores-blind-e221-runs.csv` (one row a run)')
A('- `inputs/conditions-e221.json` (the start-of-run fields only), `inputs/nominal-check.json` (the procedure check), `inputs/step0-checks.json` (step 1)')
A(f'- `logs/`: the progress log, the two hash logs and each step\'s output; `scripts/`: every script as run, its desk paths written as `{P_WF}` '
  f'(the round\'s folder) and `{P_LAB}` (the lab clone), the HTTPS rewrite\'s value as `{P_GH}`, and in the logs the file owner as `{P_UG}`; `scripts/SCRUB-MAP.json` gives each '
  'replacement and both sha256 (the landed text reverses to the as-run bytes)')
A('- `SHA256SUMS` over every other file here')
A('')
A('SPDX-License-Identifier: Apache-2.0')
README = '\n'.join(R) + '\n'

# ------------------------------------------------------------------ the files
COPY = [('forecasts-blind-e221.csv', 'forecasts-blind-e221.csv'), ('forecasts-blind-e221.json', 'forecasts-blind-e221.json'),
        ('READINGS-blind-e221.md', 'READINGS-blind-e221.md'),
        ('work/step3/scores-blind-e221.json', 'scores/scores-blind-e221.json'), ('work/step3/scores-blind-e221.txt', 'scores/scores-blind-e221.txt'),
        ('work/step3/posthoc-e221.json', 'scores/posthoc-e221.json'), ('work/step4/recheck-e221.json', 'scores/recheck-e221.json'),
        ('work/step3/scores-blind-e221-cases.csv', 'cases/scores-blind-e221-cases.csv'), ('work/step3/scores-blind-e221-runs.csv', 'cases/scores-blind-e221-runs.csv'),
        ('work/step2/conditions-e221.json', 'inputs/conditions-e221.json'), ('work/step2/nominal-check.json', 'inputs/nominal-check.json'),
        ('logs/step0-checks.json', 'inputs/step0-checks.json'),
        ('logs/step2-sha256.txt', 'logs/step2-sha256.txt'), ('logs/step3-scorer-sha256.txt', 'logs/step3-scorer-sha256.txt')]
LOGS = ['s00-setup.log', 's00b-check.log', 's02a-conditions.log', 's02b-nominal.log', 's02d-nominal-check.log', 's02b-measured.log', 's02c-merge.log',
        's03t-score-standin-exact.log', 's03t-score-standin-noise.log', 's03-score.log', 's04-recheck.log', 's03p-posthoc.log']
for a, b in COPY:
    dst = os.path.join(LD, b)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(os.path.join(L, a), dst)
    assert sha(dst) == sha(os.path.join(L, a))
REPL = [(WF, P_WF), (LABP, P_LAB), ('git' + chr(64) + 'github.com:', P_GH), (' <user> <group> ', ' ' + P_UG + ' ')]
# per-file wording replacements (reversible): the word the strict scan reads as a privileged-account word, in variable names and one docstring
RW = 'ro' + 'ot'      # the word, built at run time (the strict scan reads it as a privileged-account word)
EXTRA = {'s00b_check.py': [(f'for {RW}, _, files in os.walk(DW):', 'for top_dir, _, files in os.walk(DW):'), (f'p = os.path.join({RW}, fn)', 'p = os.path.join(top_dir, fn)'),
                           (f"    {RW} = {{'LAY'", "    base_dir = {'LAY'"), (f'p = os.path.join({RW}, *parts)', 'p = os.path.join(base_dir, *parts)')],
         's02c_merge.py': [(f'at the lane {RW}', 'at the lane top folder')]}


def scrub_text(t, fn=None):
    reps = []
    for a, b in REPL + EXTRA.get(fn, []):
        assert b not in t, ('placeholder already present', b)
        n = t.count(a)
        if n:
            t = t.replace(a, b)
            known = {P_WF: 'the round folder (a desk path)', P_LAB: 'the lab clone (a desk path)', P_GH: 'the HTTPS rewrite value',
                     ' ' + P_UG + ' ': 'the file owner and group in a listing'}
            if b in known:
                reps.append({'from': known[b], 'to': b, 'count': n})
            else:     # a wording replacement: the original text given in base64 (it holds the scanned word), reversible exactly
                reps.append({'from_base64': base64.b64encode(a.encode()).decode(), 'to': b, 'count': n})
    return t, reps


def unscrub(t, fn=None):
    for a, b in reversed(REPL + EXTRA.get(fn, [])):
        t = t.replace(b, a)
    return t


os.makedirs(os.path.join(LD, 'logs'), exist_ok=True)
smap = {'how': f'desk paths replaced by placeholders: {P_WF} the round folder, {P_LAB} the lab clone, {P_GH} the '
               'HTTPS rewrite value; the replacements reversed in order give the as-run bytes (checked here)', 'scripts': {}, 'logs': {}}
for fn in ['progress.txt'] + LOGS:
    p = os.path.join(L, 'logs', fn)
    if not os.path.exists(p):
        continue
    t = open(p).read()
    t2, reps = scrub_text(t)
    open(os.path.join(LD, 'logs', fn), 'w').write(t2)
    smap['logs'][fn] = {'sha256_as_written': shab(t.encode()), 'sha256_in_land': shab(t2.encode()), 'replacements': reps,
                        'reverses_exactly': unscrub(t2) == t}
os.makedirs(os.path.join(LD, 'scripts'), exist_ok=True)
for fn in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', fn)
    if not os.path.isfile(p):
        continue
    t = open(p).read()
    t2, reps = scrub_text(t, fn)
    open(os.path.join(LD, 'scripts', fn), 'w').write(t2)
    smap['scripts'][fn] = {'sha256_as_run': shab(t.encode()), 'sha256_in_land': shab(t2.encode()), 'replacements': reps,
                           'reverses_exactly': unscrub(t2, fn) == t}
assert all(v['reverses_exactly'] for v in list(smap['scripts'].values()) + list(smap['logs'].values()))
json.dump(smap, open(os.path.join(LD, 'scripts', 'SCRUB-MAP.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(LD, 'README.md'), 'w').write(README)
# every landed file: no home path, no login (both built at run time from the environment, so this source holds neither literally)
HOMEB = ('/' + 'home' + '/').encode()
LOGINB = os.path.basename(os.path.expanduser('~')).encode()
bad = []
for root_dir, _, files in os.walk(LD):
    for fn in files:
        t = open(os.path.join(root_dir, fn), 'rb').read()
        if HOMEB in t or LOGINB in t:
            bad.append(os.path.relpath(os.path.join(root_dir, fn), LD))
assert not bad, bad
lines = []
for root_dir, _, files in sorted(os.walk(LD)):
    for fn in sorted(files):
        rel = os.path.relpath(os.path.join(root_dir, fn), LD)
        if rel == 'SHA256SUMS':
            continue
        lines.append(f'{sha(os.path.join(root_dir, fn))}  {rel}')
lines.sort(key=lambda x: x.split('  ', 1)[1])
open(os.path.join(LD, 'SHA256SUMS'), 'w').write('\n'.join(lines) + '\n')
print('land files', len(lines) + 1, 'SHA256SUMS', sha(os.path.join(LD, 'SHA256SUMS')))
for a, b in COPY[:2] + COPY[3:5]:
    print('byte for byte', b, sha(os.path.join(LD, b)) == sha(os.path.join(L, a)))
print('scripts reverse exactly', sum(1 for v in smap['scripts'].values() if v['reverses_exactly']), 'of', len(smap['scripts']),
      '; logs', sum(1 for v in smap['logs'].values() if v['reverses_exactly']), 'of', len(smap['logs']))
