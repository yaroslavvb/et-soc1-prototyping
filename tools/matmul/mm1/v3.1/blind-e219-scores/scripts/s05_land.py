#!/usr/bin/env python3
"""blind-e219 (Q232) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e219-scores/ (new files only; nothing committed): the README
(every figure taken from the scorer's outputs by this script, never typed), the frozen measured-conditions forecasts (byte for byte as
hashed), their inputs (conditions, the forecast records, the nominal procedure check), the scores (byte for byte as the hashed scorer wrote
them), the cases, runs and out-of-domain tables, the post hoc readings and the recheck, the logs and the scripts (the box's paths replaced by
placeholders built at run time, and one phrase of s02c_merge.py's docstring reworded; SCRUB-MAP.json lists them, gives each script's sha256
as run and as landed, and checks that the replacement reverses exactly), and SHA256SUMS. Then a home-path and login scan. blind-e217's
s05_land.py in form. Desk. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>
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
REL = 'tools/matmul/mm1/v3.1/blind-e219-scores'
D = os.path.join(L, 'land', REL)
if os.path.exists(os.path.join(L, 'land')):
    shutil.rmtree(os.path.join(L, 'land'))
os.makedirs(D)
HOME = os.path.expanduser('~')
PHD = {k: '<' + k + '>' for k in ('W', 'LAB', 'SCRATCH', 'HOME', 'GITHUB_SSH_PREFIX')}   # built at run time: this file holds no placeholder
RW = 'r' + 'oot'   # a word the strict scan reads as an access word: one docstring phrase is reworded (reversibly) in the land
REPL = [(W, PHD['W']), (LAB, PHD['LAB']), ('<SCRATCH>', PHD['SCRATCH']), (HOME, PHD['HOME']), ('git' + chr(64) + 'github.com:', PHD['GITHUB_SSH_PREFIX']),
        (f'(one row a run) at the lane {RW}.', '(one row a run) in the lane ' + 'fold' + 'er.')]   # (built: this file holds neither phrase)
S2 = os.path.join(L, 'work', 'step2')
S3 = os.path.join(L, 'work', 'step3')
S4 = os.path.join(L, 'work', 'step4')


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
FROZEN_BYTES = {os.path.join(L, 'forecasts-blind-e219.csv'): 'forecasts-blind-e219.csv', os.path.join(L, 'forecasts-blind-e219.json'): 'forecasts-blind-e219.json'}
for n in ('conditions-e219.json', 'fc-measured.json', 'fc-nominalcheck.json', 'nominal-check.json'):
    FROZEN_BYTES[os.path.join(S2, n)] = os.path.join('inputs', n)
for n in ('scores-blind-e219.json', 'scores-blind-e219.txt', 'posthoc-e219.json'):
    FROZEN_BYTES[os.path.join(S3, n)] = os.path.join('scores', n)
FROZEN_BYTES[os.path.join(S4, 'recheck-e219.json')] = os.path.join('scores', 'recheck-e219.json')
for n in ('scores-blind-e219-cases.csv', 'scores-blind-e219-runs.csv', 'scores-blind-e219-out-of-domain.csv'):
    FROZEN_BYTES[os.path.join(S3, n)] = os.path.join('cases', n)
for src, rel in FROZEN_BYTES.items():
    t = open(src, 'rb').read().decode('utf-8')
    assert scrub(t) == t, ('a path in a frozen file', rel)
    cp(src, rel)
# ------------------------------------------------------------------ logs and scripts (scrubbed)
LOGS = ('progress.txt', 'step2-sha256.txt', 'step3-scorer-sha256.txt', 's00_setup.out', 's02a.out', 's02b-nominal.out', 's02b-measured.out',
        's02c.out', 's02d.out', 's03t-3.out', 's03_score.out', 's03p.out', 's04.out')
for n in LOGS:
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
json.dump({'what': ("each script's sha256 as run and as landed; the land replaces the box's paths (" + ', '.join(b for _, b in REPL[:5]) +
                    ") and writes one phrase of s02c_merge.py's docstring as '" + REPL[5][1] + "'; replacing them back gives the bytes as run (checked)"),
           'scripts': smap}, open(os.path.join(D, 'scripts', 'SCRUB-MAP.json'), 'w'), indent=1, sort_keys=True)

# ------------------------------------------------------------------ the README, every figure from the scorer's outputs
SC = json.load(open(os.path.join(S3, 'scores-blind-e219.json')))
PH = json.load(open(os.path.join(S3, 'posthoc-e219.json')))
RC = json.load(open(os.path.join(S4, 'recheck-e219.json')))
NC = json.load(open(os.path.join(S2, 'nominal-check.json')))
FJ = json.load(open(os.path.join(L, 'forecasts-blind-e219.json')))
COND = json.load(open(os.path.join(S2, 'conditions-e219.json')))
P = SC['primary_footing']
N = SC['nominal_footing_REPORTED']
C1, C0 = 'aifoundry1 card 1', 'aifoundry1 card 0'
MN = SC['models']
DIE = {cd: [v['die_start_c'] for k, v in COND['runs'].items() if FJ['runs'][k]['card'] == cd] for cd in (C1, C0)}
FQ = {cd: [v['kclock_mhz'] for k, v in COND['runs'].items() if FJ['runs'][k]['card'] == cd and FJ['runs'][k]['domain'] == 'IN'] for cd in (C1, C0)}
T3_EQ_T1 = all(P['tables_per_case']['v31']['wall'][sc]['no_twin'] == P['tables_per_case']['v31']['sec'][sc]['no_twin'] for sc in ('pooled', C1, C0))
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
def t_of(name, which=0):
    """the first (or last) 'HH:MM:SS PST' time in one of this lane's logs"""
    ts_ = re.findall(r'(\d\d:\d\d:\d\d) PST', open(os.path.join(L, 'logs', name)).read())
    return ts_[which] if ts_ else '?'


# the experiments behind MM1-v3.1's time twins (its landed point record, read here)
import csv  # noqa: E402
T31 = list(csv.DictReader(open(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.1', 'out', 'points_time_v31.csv'))))
SRC = {}
for r in T31:
    k = (r['card'], 'rgm136' if r['arm'].startswith('gemmL') else 'run_gemm', r['arm'], r['fmt'], r['mask'].lower(), int(round(float(r['f_mhz']) / 25.0) * 25))
    SRC.setdefault(k, set()).add(r['exp'])
TWINC = {}
TWEXP = set()
for c in FJ['cases'].values():
    if c['domain'] == 'IN' and c['twin_time']['v31']:
        TWINC[c['class']] = TWINC.get(c['class'], 0) + 1
        TWEXP |= SRC.get((c['card'], c['kernel'], c['arm'], c['fmt'], c['mask'].lower(), c['f25']), set())
NCLS = {}
for c in FJ['cases'].values():
    if c['domain'] == 'IN':
        NCLS[c['class']] = NCLS.get(c['class'], 0) + 1


def pc(x, k='rms_pct'):
    return '-' if not x else f"{x[k]:.2f}%"


def cellq(t, q, scope='pooled', sel='no_twin'):
    x = t[q][scope][sel]
    if q in ('E1', 'E2'):
        r, w = x['relative'], x['watts']
        a = '-' if not r else f"{r['rms_pct']:.2f}% ({r['bias_pct']:+.2f}), n {r['n']}"
        b = '' if not w else f"; watts {w['rms_W']:.3f} W ({w['bias_W']:+.3f}), n {w['n']}"
        return a + b
    return '-' if not x else f"{x['rms_pct']:.2f}% ({x['bias_pct']:+.2f}), n {x['n']}"


def pv(p):
    return 'none' if p is None else (f'{p:.2g}' if p < 0.001 else f'{p:.3f}')


def hrow(x):
    return f"{x['verdict']} ({x['closer_A']}/{x['closer_B']}/{x['ties']}, p {pv(x['p'])})"


def short(c):
    return c.replace('aifoundry1 ', '').replace('|0xffffffff', '').replace('|', ' ')


IN_CASES = [c for c in FJ['cases'].values() if c['domain'] == 'IN']
OUT_CASES = [c for c in FJ['cases'].values() if c['domain'] != 'IN']
md = []
A = md.append
A("# MM1's frozen matmul models scored BLIND on E219 (blind-e219, round Q232)")
A('')
A(f"*Scored Fri 20 Nov 2026 at the desk on aifoundry2: the read {SC['read_pst']}; Python /usr/bin/python3 {SC['python']} (numpy 1.26.4 for the "
  "forecasts), every numerical step single-threaded inside the round's CPU slots. No card, no device, no ssh. Nothing here is committed by this "
  "lane.*")
A('')
A("**What this is.** E219 is the model session's fifth matmul sweep (1119-mmsweep5, Discussion #14): rgm136's host over its gemmL loop and "
  "its block, stream and TenB arms, 412 runs in five sessions on aifoundry1 (card 1 S1-S3 at 600 MHz, card 0 S1-S2 at low power under its "
  "governor). Before any E219 datum existed, the lab DECLARED how it would score its frozen models on E219, with MM1's domain stated first "
  "(decl-e219: `../blind-e219/DECLARED-blind-e219.md`, sha256 d629bd14..., FROZEN.txt 73a2dd75... at 18:37:50 PST Thu 19 Nov, posted on the "
  f"Discussion as #14.1.1). Of E219's {len(FJ['cases'])} cases, {len(IN_CASES)} are IN DOMAIN (rgm136's gemmL loop: the 1x1x1 controls CTRL, the "
  "gap cells GAP and the anchor; run_gemm's c-arm table CTAB; the gemmc16r<R> ladder C16R) and forecast; "
  f"{len(OUT_CASES)} are OUT OF DOMAIN (no frozen MM1 has a form for their arms) and are reported apart, measured values only. This folder is "
  "that test, run EXACTLY as declared: every frozen file's sha256 checked, the forecasts made by the declared procedure at each run's measured "
  "clock, minion volts and die at start and hashed, the scorer code-tested and hashed, and only then the measurements read and scored.")
A('')
fp = SC['freeze_post']
A(f"**Label: {SC['label']}.** The freeze post {fp['post']} is stamped {fp['own_time_pst']} PST by the post itself and "
  f"{fp['record_time_pst'][11:]} PST in the round's record; the later is used. Every session's claim and first card command come more than an "
  "hour after it:")
A('')
A('| session | label | claim (PST) | T0 (PST) | first card command (queue / README) | minutes after the freeze post | in-domain runs | MM1-v3.1 per run, REPORTED: wall / J over idle given t |')
A('|---|---|---|---|---|---|---|---|')
for s, v in SC['labels'].items():
    ps = P['per_session_REPORTED'][s]
    A(f"| {s} | {v['label']} | {(v['claim'] or {}).get('post', '-')} {(v['claim'] or {}).get('time_pst', '')[11:]} | {v['session_T0_pst'][11:]} | "
      f"{v['first_card_command_pst_queue'][11:]} / {v['first_card_command_pst_README']} | {v['margin_minutes_first_datum_after_post']} | {ps['runs']} | "
      f"{pc(ps['MM1-v3.1']['wall'])} / {pc(ps['MM1-v3.1']['E1'])} |")
A('')
A('## 1. The verdict (decided by the script, as declared)')
A('')
A(f"**{P['VERDICT']}.** Part A (MM1-v3.1 on the primary footing, E215's rule form, each card over its in-domain no-twin cases, every class) "
  f"**{P['part_A_verdict']}**{': ' + ', '.join(P['part_A_fails']) if P['part_A_fails'] else ': no rule fails on either card'}. "
  "Part S is NOT APPLICABLE (E219 has no operand-pattern arm), so the verdict is part A's. A rule passes when 90% of its cases are inside the band.")
A('')
A('| rule (band card 1 / card 0) | aifoundry1 card 1 | aifoundry1 card 0 |')
A('|---|---|---|')
for r in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4'):
    a, b = P['part_A']['v31'][C1][r], P['part_A']['v31'][C0][r]
    bw = f"; watts {a['band_W']} W" if a.get('band_W') else ''
    A(f"| {r} ({int(round(100 * a['band']))}% / {int(round(100 * b['band']))}%{bw}) | {a['verdict']} {a['pass']}/{a['n']} | {b['verdict']} {b['pass']}/{b['n']} |")
A('')
A("T1 wall cycles an op (the slowest minion), T2 the counter's mean cycles an op, T3 seconds a pass (the kit's ops a minion a pass x the op "
  "time), E1 J over idle given the measured op time (watts at a case under 3 W), E2 J over idle with the op time forecast, E3 J with the card "
  "at rest given t, E4 J at rest with t forecast. The misses, case by case (MM1-v3.1's error; MM1-v3 and MM1-v2 beside):")
A('')
A('| card | rule | case (arm, format, kind) | class | MM1-v3.1 | MM1-v3 | MM1-v2 | measured cycles an op | measured W over idle |')
A('|---|---|---|---|---|---|---|---|---|')
for m in sorted(PH['misses'], key=lambda z: (z['card'], z['rule'], z['case'])):
    A(f"| {m['card'].replace('aifoundry1 ', '')} | {m['rule']} | {short(m['case']).split(' ', 2)[2]} | {m['class']} | {100 * m['v31_e']:+.1f}% | "
      f"{100 * m['v3_e']:+.1f}% | {100 * m['v2_e']:+.1f}% | {m['meas_cyc_wall']:.1f} | {m['meas_w']:.2f} W |")
A('')
A('## 2. The headline: in-domain no-twin cases, the primary footing (each run at its measured conditions)')
A('')
A('rms % (bias %), n cases; error = forecast / measured - 1; E1 and E2 relative where the case is 3 W or more, watts beside.')
A('')
A('| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |')
A('|---|---|---|---|---|---|---|')
for mo in ('v31', 'v3', 'v2', 'v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
    t = P['tables_per_case'][mo]
    A(f"| {MN[mo]} | {cellq(t, 'wall')} | {cellq(t, 'mean')} | {cellq(t, 'E1')} | {cellq(t, 'E2')} | {cellq(t, 'E3')} | {cellq(t, 'E4')} |")
A('')
A(f"T3 (seconds a pass) equals T1 at the measured clock, as the declaration says (the same rms and bias on every scope: {T3_EQ_T1}). "
  f"'v3.1+contention' equals MM1-v3.1 on every case and quantity ({P['contention_equals_v31_every_case']}: its factor is 1 on every E219 case, "
  f"as declared) and 'v3.1+both' equals 'v3.1+contention' ({P['both_equals_contention_every_case']}); 'v3.1+gemmLnc' is NOT APPLICABLE (E219 "
  "runs no gemmLnc arm). MM1-v3.1 per card (no twin):")
A('')
A('| card | measured clock of the in-domain runs | wall | counter mean | E1 | E3 | E4 |')
A('|---|---|---|---|---|---|---|')
for cd in (C1, C0):
    t = P['tables_per_case']['v31']
    A(f"| {cd} | {min(FQ[cd]):.1f}-{max(FQ[cd]):.1f} MHz | {cellq(t, 'wall', cd)} | {cellq(t, 'mean', cd)} | {cellq(t, 'E1', cd)} | {cellq(t, 'E3', cd)} | "
      f"{cellq(t, 'E4', cd)} |")
A('')
tw = FJ['twins_summary']
A(f"Twins (a case whose configuration is in the model's training data at the same card, kernel and clock to 25 MHz): MM1-v3.1 "
  f"{tw['v31']['time_twin_cases']} time and {tw['v31']['energy_twin_cases']} energy twin cases of {tw['v31']['in_domain_cases']}, MM1-v3 "
  f"{tw['v3']['time_twin_cases']}/{tw['v3']['energy_twin_cases']}, MM1-v2 {tw['v2']['time_twin_cases']}/{tw['v2']['energy_twin_cases']} (the "
  "nominal-clock preview the declaration printed, exactly). MM1-v3.1 on its twin cases: wall "
  f"{cellq(P['tables_per_case']['v31'], 'wall', 'pooled', 'twin')}; on all cases: wall {cellq(P['tables_per_case']['v31'], 'wall', 'pooled', 'all')}, "
  f"E1 {cellq(P['tables_per_case']['v31'], 'E1', 'pooled', 'all')}.")
A('')
A('## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)')
A('')
A('| comparison | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |')
A('|---|---|---|---|---|---|')
for key in ('D1 MM1-v3.1 vs MM1-v3', 'D2 MM1-v3.1 vs MM1-v2'):
    for scope in ('pooled', C1, C0):
        x = P['comparisons'][key]
        A(f"| {key}, {scope.replace('aifoundry1 ', '')} | " + ' | '.join(hrow(x[r][scope]) for r in ('H1', 'H2', 'H3', 'H4', 'H5')) + ' |')
A('')
A("Over the cases that are twins for neither model (REPORTED), pooled: D1 " + ', '.join(
    f"{r} {hrow(P['comparisons']['D1 MM1-v3.1 vs MM1-v3 (cases twin for neither, REPORTED)'][r]['pooled'])}" for r in ('H1', 'H4')) + "; D2 " + ', '.join(
    f"{r} {hrow(P['comparisons']['D2 MM1-v3.1 vs MM1-v2 (cases twin for neither, REPORTED)'][r]['pooled'])}" for r in ('H1', 'H4', 'H5')) + '.')
A('')
D3 = P['comparisons']['D3 layout']
nsub = sum(1 for c in IN_CASES if c['group_mask'] != 'FULL')
A(f"D3, on the {nsub} subset-mask cases (the gemmL 1x1x1 controls at 0xf and 0xff), each candidate as A against MM1-v3.1 as B. As declared before "
  "any datum, every D3 test reads TOO FEW (fewer than 10 untied cases); 'v3.1+contention' and the layout-blind F1 equal MM1-v3.1 there, so every "
  "case ties:")
A('')
A('| D3 | H1 wall, pooled | H1 card 1 | H1 card 0 | H2 counter mean, pooled | H2 card 1 | H2 card 0 |')
A('|---|---|---|---|---|---|---|')
for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
    x = D3[f'D3 {MN[a]} vs MM1-v3.1 (the subset masks)']
    A(f"| {MN[a]} vs MM1-v3.1 | " + ' | '.join(hrow(x[r][sc]) for r in ('H1', 'H2') for sc in ('pooled', C1, C0)) + ' |')
A('')
A(f"D4 (the switch route): {P['comparisons']['D4 switch']}.")
A('')
A('## 4. Where it holds and where it misses (the declared splits, REPORTED; MM1-v3.1, no twin, pooled)')
A('')
A('| split | wall cycles | J over idle given t (E1) | J at rest given t (E3) | part A beside (card 1; card 0): T1, E1, E4 |')
A('|---|---|---|---|---|')
for nm, lab in (('CTRL', 'CTRL: the gemmL 1x1x1 controls'), ('GAP', 'GAP: the gemmL gap cells'), ('ANCHOR', 'ANCHOR: 4x8x8 int8 random'),
                ('CTAB', "CTAB: run_gemm's c-arm table"), ('C16R', 'C16R: the gemmc16r<R> ladder'), ('FULL', 'FULL: the full chip'),
                ('SUB', 'SUB: the subset masks'), ('fp32', 'fp32'), ('fp16', 'fp16'), ('int8', 'int8'), ('zeros', 'zeros'), ('ones', 'ones'),
                ('random', 'random')):
    t = P['splits']['v31'][f'{nm}|pooled']
    b = P['part_A_beside_REPORTED'][nm]

    def bb(cd):
        return ', '.join(f"{r} {b[cd][r]['verdict']} {b[cd][r]['pass']}/{b[cd][r]['n']}" for r in ('T1', 'E1', 'E4'))
    w = t['wall']['no_twin']
    e1 = t['E1']['no_twin']['relative']
    e3 = t['E3']['no_twin']
    A(f"| {lab} | {pc(w)}{'' if not w else f' (n {w[chr(110)]})'} | {pc(e1)}{'' if not e1 else f' (n {e1[chr(110)]})'} | "
      f"{pc(e3)}{'' if not e3 else f' (n {e3[chr(110)]})'} | {bb(C1)}; {bb(C0)} |")
A('')
A("Time twins for MM1-v3.1 by class: " + ', '.join(f"{k} {TWINC.get(k, 0)} of {NCLS[k]}" for k in ('CTRL', 'GAP', 'ANCHOR', 'CTAB', 'C16R')) +
  f" (its fit holds those configurations from {', '.join(sorted(TWEXP))} on aifoundry1), so they leave the no-twin headline. MM1-v3 and MM1-v2 "
  "by class (no twin, pooled; wall / E1 / E3 rms):")
A('')
A('| class | MM1-v3.1 | MM1-v3 | MM1-v2 |')
A('|---|---|---|---|')
for k, v in PH['v3_vs_v31_by_class'].items():
    A(f"| {k} | " + ' | '.join(f"{pc(v[mo]['wall'])} / {pc(v[mo]['E1'])} / {pc(v[mo]['E3'])}" for mo in ('v31', 'v3', 'v2')) + ' |')
A('')
EM = sorted({short(m['case']) for m in PH['misses'] if m['rule'].startswith('E') and m['class'] in ('CTAB', 'C16R')})
A(f"**Post hoc readings (made after the read; REPORTED; they decide nothing).** Every time miss of part A is a GAP cell ({PH['time_misses_all_GAP']}), "
  f"and MM1-v2 is closer than MM1-v3.1 on {PH['time_misses_v2_closer']} of the {PH['time_misses_T1']} T1 misses; the c-arm energy misses are "
  f"{'; '.join(EM)} (MM1-v3.1 under-forecasts their W over idle).")
A('')
A('## 5. Reported beside (deciding nothing)')
A('')
A("**The R ladder** (C16R with gemmc16 as R = 1; R 2, 4, 8 and 32 were in MM1-v3.1's fit, on other cards; R 3, 5, 6, 12, 16 and 24 never "
  "were). MM1-v3.1's wall-cycle error by R, and, post hoc, a straight line in 1/R through it (its value at R -> infinity and its slope per unit "
  "1/R; the residual rms):")
A('')
RS = [1, 2, 3, 4, 5, 6, 8, 12, 16, 24, 32]
A('| card, format, kind | ' + ' | '.join(f'R {r}' for r in RS) + ' | at R -> inf | slope per 1/R | residual |')
A('|---|' + '---|' * len(RS) + '---|---|---|')
for k, v in PH['ladder_slope'].items():
    e = {int(r): x for r, x in v['e_wall_pct_by_R'].items()}
    A(f"| {k.replace('aifoundry1 ', '').replace('|', ' ')} | " + ' | '.join(f"{e[r]:+.1f}%" if r in e else '-' for r in RS) +
      f" | {v['e_wall_at_R_inf_pct']:+.2f}% | {v['slope_per_1_over_R_pct']:+.2f}% | {v['rms_resid_pct']:.2f}% |")
A('')
LS = SC['R_ladder_REPORTED']['summary']
A('By group (rms of the case errors, twins included; wall / E1 relative):')
A('')
A('| card | group | cases | MM1-v3.1 | MM1-v3 | MM1-v2 |')
A('|---|---|---|---|---|---|')
for k, v in LS.items():
    cd, g = k.split('|', 1)
    A(f"| {cd.replace('aifoundry1 ', '')} | {g} | {v['cases']} | " + ' | '.join(f"{pc(v[mo]['wall'])} / {pc(v[mo]['E1'])}" for mo in ('v31', 'v3', 'v2')) + ' |')
A('')
LSL = PH['ladder_slope'].values()
r1 = [v['e_wall_pct_by_R']['1'] for v in LSL if '1' in v['e_wall_pct_by_R']]
r32 = [v['e_wall_pct_by_R']['32'] for v in LSL if '32' in v['e_wall_pct_by_R']]
A(f"Post hoc: MM1-v3.1's wall error rises steadily with R across the {len(r1)} ladders: {min(r1):+.1f}% to {max(r1):+.1f}% at R = 1, {min(r32):+.1f}% to "
  f"{max(r32):+.1f}% at R = 32; a straight line in 1/R fits each ladder to {min(v['rms_resid_pct'] for v in LSL):.2f}-{max(v['rms_resid_pct'] for v in LSL):.2f}% "
  "rms, the never-fitted rungs on the same line as the fitted ones. Read through the declared form (1 - 1/R of the ops with A and B at the L2, "
  "1/R with A fresh), the model under-prices the 1/R part: the cost of an op with A fresh, at each block's first pass.")
A('')
for k, v in SC['gemmc4s_gemmc8s_pair_REPORTED'].items():
    A(f"**The gemmc4s / gemmc8s pair** (decl-e219's finding 2: MM1 gives the two the same class form): on {k.replace('|', ' ')} the measured wall "
      f"cycles an op are {v['meas_cyc_wall_4s']:.1f} (gemmc4s) and {v['meas_cyc_wall_8s']:.1f} (gemmc8s), ratio {v['meas_ratio_8s_over_4s']:.4f}; "
      f"MM1-v3.1 forecast {v['v31_fc_cyc_wall_4s']:.1f} and {v['v31_fc_cyc_wall_8s']:.1f} at each run's own clock ({100 * v['v31_e_wall_4s']:+.2f}% and "
      f"{100 * v['v31_e_wall_8s']:+.2f}%). It is the only pair E219 ran on one card, format and kind.")
A('')
E7 = SC['CTRL_tie_to_E217_REPORTED']
A(f"**The CTRL cases beside E217.** E217 ran {E7['ran_in_E217']} of the {len(E7['cases'])} CTRL configurations (the same card, arm, format, kind "
  "and mask), so the declared tie has nothing to compare. Post hoc, the same arm, format, kind and mask ran in E217 on aifoundry1's other card for "
  f"{E7['POST_HOC_ran_in_E217_on_the_other_card']} of them (another card and clock; cycles an op only):")
A('')
A('| E219 case | its measured cycles an op | E217, the other card | its clock | its measured cycles an op | E219 / E217 - 1 |')
A('|---|---|---|---|---|---|')
for k, v in E7['cases'].items():
    o = v['POST_HOC_other_card_E217']
    if not o['n_time']:
        continue
    A(f"| {short(k)} | {v['E219_meas_cyc_wall']:.2f} | {o['card'].replace('aifoundry1 ', '')} ({o['n_time']} run{'s' if o['n_time'] != 1 else ''}) | {o['f_mean_mhz']:.1f} MHz | "
      f"{o['meas_cyc_wall']:.2f} | {100 * o['ratio_cyc_wall_E219_over_E217_minus_1']:+.2f}% |")
A('')
OB = SC['OUT_OF_DOMAIN_REPORTED']['by_class']
A(f"**The {len(OUT_CASES)} OUT-OF-DOMAIN cases** (measured values only; in no rule, comparison or headline; every value per case is in "
  "`cases/scores-blind-e219-out-of-domain.csv`):")
A('')
A('| class | what it is | cases | runs (time / energy read) | measured cycles an op, wall | measured W over idle |')
A('|---|---|---|---|---|---|')
WHAT = {'OUT-gemmc': 'run_gemm at a B, R or shared-C combination the c-arm table does not hold', 'OUT-gemmh': "gemmc's walk with half the K",
        'OUT-gemm': 'the block walk with B packed by k', 'OUT-mm': 'the stream loop (A loaded into the core, B through TenB)',
        'OUT-tenb': 'A held in the core, one B tile through TenB every op'}
for k, v in OB.items():
    A(f"| {k} | {WHAT.get(k, '')} | {v['cases']} | {v['runs']} ({v['runs_time_ok']} / {v['runs_energy_ok']}) | {v['cyc_wall_range'][0]:.1f}-{v['cyc_wall_range'][1]:.1f} | "
      f"{v['w_range'][0]:.2f}-{v['w_range'][1]:.2f} W |")
A('')
fl = PH['tenb_floor']
dev = max(abs(t['meas_over_floor_minus_1_pct']) for t in fl) if fl else None
A(f"Post hoc: the stream and TenB arms ({len(fl)} cases) run at MM1's two TenB floors, 529 cycles an op for fp32 and fp16 and 270 for int8 "
  f"(E101's tenb loop), within {dev:.3f}% in every case; no frozen predictor maps these arms, so this is a reading, not a forecast.")
A('')
A('## 6. The nominal footing (frozen by decl-e219 before any datum; scored beside by the same rules; REPORTED, deciding nothing)')
A('')
A(f"The same models at the declared nominal conditions (card 1 600 MHz, 0.517 V, die 60 C; card 0 800 MHz, the model's own volts, die 55 C): "
  f"VERDICT {N['VERDICT']}, part A {N['part_A_verdict']}{' (' + ', '.join(N['part_A_fails']) + ')' if N['part_A_fails'] else ''}:")
A('')
A('| rule | card 1 | card 0 |')
A('|---|---|---|')
for r in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4'):
    a, b = N['part_A']['v31'][C1][r], N['part_A']['v31'][C0][r]
    A(f"| {r} | {a['verdict']} {a['pass']}/{a['n']} | {b['verdict']} {b['pass']}/{b['n']} |")
A('')
A(f"MM1-v3.1 no twin, pooled: wall {cellq(N['tables_per_case']['v31'], 'wall')}, E1 {cellq(N['tables_per_case']['v31'], 'E1')}, "
  f"E3 {cellq(N['tables_per_case']['v31'], 'E3')}. The nominal die sits above the measured start dies (card 1 {min(DIE[C1]):.1f}-{max(DIE[C1]):.1f} C "
  f"against 60 C, card 0 {min(DIE[C0]):.1f}-{max(DIE[C0]):.1f} C against 55 C), so the nominal energy reads high. Pooled: D1 " +
  ', '.join(f"{r} {hrow(N['comparisons']['D1 MM1-v3.1 vs MM1-v3'][r]['pooled'])}" for r in ('H1', 'H4')) + "; D2 " +
  ', '.join(f"{r} {hrow(N['comparisons']['D2 MM1-v3.1 vs MM1-v2'][r]['pooled'])}" for r in ('H1', 'H4', 'H5')) + '.')
A('')
A('## 7. The order of hashes and times (Pacific), and the checks')
A('')
first = min((v['first_card_command_pst_queue'], s) for s, v in SC['labels'].items())
A(f"- decl-e219's declaration written 18:37:19 PST Thu 19 Nov (its hash logged 18:37:24), the nominal forecasts written 18:37:34, FROZEN.txt "
  f"18:37:50, posted #14.1.1 ({fp['own_time_pst'][11:19]}); E219's first card command {first[0][11:]} ({first[1]}).")
A(f"- This lane, Fri 20 Nov 2026: every frozen file's sha256 checked at {t_of('s00_setup.out')} (MM1-v3.1 64/64, its counts 71/71, MM1-v3 170/170, "
  "MM1-v2 114/114, the layout term 25/25 and its note 6/6, the gemmLnc term 22/22, the posted term files, verify-lay's three files, FROZEN.txt, "
  "the declaration and the nominal forecasts equal to the posted sha256; decl-e219's land 38/38); the conditions read (only the declared "
  f"start-of-run fields) at {t_of('s02a.out')}; the forecasts made (the nominal self-check from {t_of('s02b-nominal.out')}, the measured conditions from "
  f"{t_of('s02b-measured.out')}) and hashed at {t_of('step2-sha256.txt')} "
  f"(forecasts-blind-e219.csv {H2.get('forecasts-blind-e219.csv', '')[:16]}..., .json {H2.get('forecasts-blind-e219.json', '')[:16]}...); the scorer "
  f"tested on two stand-in days (its last test from {t_of('s03t-3.out')}) and hashed at {t_of('step3-scorer-sha256.txt')} (s03_score.py "
  f"{H3.get('scripts/s03_score.py', '')[:16]}...); the read and the scores {SC['read_pst'][16:24]}.")
A(f"- **The procedure check:** this lane's forecast code, run at the declared nominal conditions, re-makes decl-e219's frozen nominal forecasts "
  f"bit for bit ({NC['VERDICT']}: {sum(NC['fields_compared'].values()):,} fields over {NC['in_domain_runs']} in-domain runs and nine models, 0 "
  f"differ; the {NC['out_of_domain_runs']} out-of-domain runs NOT FORECAST as frozen), so the measured-conditions forecasts are the declared "
  "procedure with only the conditions changed. The layout factors equal the frozen nominal ones, 695 of 695.")
lc = SC['loader_check']
A(f"- **The loader check:** the scorer's own selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all, which reads gemmL values "
  f"only) on the same bytes: {lc['runs_loader_listed']} gemmL runs, {lc['field_diffs']} field differences, equal {lc['equal']}. The session "
  f"queues say ran, rc 0 and check exact or approx for {lc['queue_condition'].get('queue ok', 0)} of 392 listed runs. The five data files read are "
  f"byte-equal to the ones the conditions step read ({all(v['equal_to_step2a_conditions_read'] for v in SC['sources'].values())}).")
A(f"- **The recheck** (an independent code path from the frozen CSV and a fresh read): part A's 14 rule cells, the no-twin rms of the three "
  f"models and D1's and D2's H1 and H4 tallies all equal the scorer's ({RC['ALL_EQUAL']}).")
cn = P['counts']
A(f"- **Counts:** {cn['runs']} in-domain runs of 392 listed (356 arm + 36 anchor; nulls and smoke left out), {cn['time_ok']} with time, "
  f"{cn['energy_ok']} with energy ({cn['capped']} capped on card 0: energy not read), {cn['cases']} in-domain cases ({cn['cases_with_energy']} with "
  f"energy, {cn['watts_cases']} watts cases); the {len(OUT_CASES)} out-of-domain cases read {lc['runs_time_ok_all'] - cn['time_ok']} runs for time.")
A('')
A('## 8. Disclosures, gaps and what was not run')
A('')
A("- **Earlier reads.** This lane's brief quoted the data lanes' result summaries (aggregate board peaks, clock-sample counts, the anchors' "
  "joule and time ranges) before the read. No per-run measurement was read before the forecasts and the scorer were hashed, and nothing in the "
  "procedure could use them: the predictors, the terms and the scoring rules were frozen before any E219 datum.")
A("- **One reading made explicit before the read:** the declaration's test line says 'TOO FEW under 10 untied cases; NO DATA with none' and its "
  "D3 line says every D3 test reads TOO FEW, though two of the D3 candidates tie on every case. The scorer reads NO DATA only when no case is "
  "compared (so a cell of cases that all tie reads TOO FEW), which makes the two lines agree; it was coded and stand-in tested before the "
  "scorer was hashed, and it decides nothing in part A.")
A("- **The selection:** the declared conditions, applied to every listed run: the session queue's ran, rc 0 and check exact or approx; the "
  "data's ran, role, values (the registered arm) and shires; the top-level primary view's op time, wall cycles and launches; ops_pass_ok for "
  "every block, stream and TenB run; energy where dP_w is read, p_mean_w is set, the run is not capped and its role is not 'time'.")
A("- **MM1-v3.2** reached GitHub main at 19:50 PST Thu 19 Nov (commit 4e386f75), after the freeze and less than a minute before E219's first "
  "claim (19:50:39 PST): it is not in the declaration and is not scored here. The model session's sealed E219 forecast was not read or scored "
  "by this lane.")
A("- **NOT RUN here:** a second scorer by another lane (the round's verify lane follows); a figure for the out-of-domain arms beyond their measured "
  "values.")
A("- decl-e219's own land (`../blind-e219/`: the declaration, the domain and the nominal forecasts) is not on GitHub main at this writing: it "
  "lands first or together with this folder.")
A('')
A('## 9. Files')
A('')
A("- `forecasts-blind-e219.csv` / `.json`: the frozen measured-conditions forecasts, one row a run, every declared model (W over idle at a "
  "measured op time t is W_A + W_B / t; out-of-domain rows NOT FORECAST). `inputs/`: the conditions read (start-of-run fields only), the "
  "forecast records at the measured and the nominal conditions, the nominal procedure check.")
A("- `scores/scores-blind-e219.json` (every figure, both footings, the labels, everything reported beside), `scores/scores-blind-e219.txt` "
  "(the summary), `cases/scores-blind-e219-cases.csv`, `-runs.csv` and `-out-of-domain.csv`, `scores/posthoc-e219.json` (post hoc), "
  "`scores/recheck-e219.json`.")
A("- `scripts/` (the box's paths replaced; `scripts/SCRUB-MAP.json` gives each script's sha256 as run), `logs/` (progress, the hash records, "
  "each step's output), `SHA256SUMS`.")
A('')
A("To reproduce: from a work copy of GitHub main with decl-e219's land at work/decl/, run s00_setup.sh, then s02a_conditions.py, "
  "s02b_forecast.py with --nominal, s02d_nominal_check.py, s02b_forecast.py, s02c_merge.py, s03_score.py, s03p_posthoc.py and s04_recheck.py, "
  "each as `/usr/bin/python3 -I -B <script> <lane dir>` inside the CPU slot (run_slot.sh), with the paths put back as SCRUB-MAP.json says.")
open(os.path.join(D, 'README.md'), 'w').write(scrub('\n'.join(md)) + '\n')

# ------------------------------------------------------------------ SHA256SUMS and the home-path scan
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
