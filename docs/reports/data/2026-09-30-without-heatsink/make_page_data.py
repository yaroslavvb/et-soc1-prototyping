#!/usr/bin/env python3
"""Write page.json for "Feasibility of running the ET-SoC-1 without its heatsink" (docs/reports/2026-09-30-esperanto-without-heatsink.html).

    python3 docs/reports/data/2026-09-30-without-heatsink/make_page_data.py [--check]

It imports nohs_calc.py (the feasibility model, seed 20260929) with its printout captured, checks that the printout
still matches nohs_calc.out, and takes every table from that printout, so the page shows exactly the numbers of the
model's record. It then runs one thing the model does not print: junction-temperature trajectories after power-on for
aifoundry2, bare in still air, bare with a fan (nohs_calc.py's two-node model and its input ranges), and with the
heatsink (the Foster chain fitted on aifoundry2, docs/findings/11-thermal-model.md), each at idle and under a random
fp32 matmul on 1,024 minions, with its own fixed seed (20260930). The options table is the brief's ranking, written
out below. Section 5 (slower clocks, added on the evening of 30 September) reads the `lowclock` block from the
records of three more scripts here, never recomputing them: lowclock_calc.json (the envelope model), imaging_calc.json
(the imaging model) and lc_plan_calc.out (the measurement plan's predictions); each is checked against its printout
first. Takes about four minutes (nohs_calc.py's transients are most of it). No card access: arithmetic only.

--check rebuilds in memory and exits 1 if page.json would change."""
import contextlib
import io
import json
import math
import os
import re
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True   # no __pycache__ in the data directory
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    import nohs_calc as M  # noqa: E402  (runs the whole model, seeded)
OUT = buf.getvalue()
REF = open(os.path.join(HERE, 'nohs_calc.out')).read()
if OUT != REF:
    sys.exit('nohs_calc.py no longer reproduces nohs_calc.out: rerun `python3 nohs_calc.py > nohs_calc.out` and review')

NUM = r'[-+]?(?:\d+\.?\d*(?:e[-+]?\d+)?|inf|nan)'


def p3(s):
    """'65.6 / 105 / 167' -> [65.6, 105, 167]; 1e+09 (the model's 'never') -> None"""
    v = [float(x) for x in re.findall(NUM, s)[:3]]
    return [None if x >= 1e8 else x for x in v]


def line(pat):
    m = re.search(pat, OUT, re.M)
    if not m:
        sys.exit('pattern not found in the model output: ' + pat)
    return m


P3 = rf'({NUM} / {NUM} / {NUM})'
CARDS = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0@300']
CARD_ID = {'aifoundry2': 'aifoundry2', 'aifoundry3': 'aifoundry3', 'aifoundry1-c1': 'aifoundry1-c1',
           'aifoundry1-c0@300': 'aifoundry1-c0'}

# ---------- A, B: package, bare theta ----------
pkg = {
    'lid_plate_mm': p3(line(rf'lid plate thickness \(derived\) mm: {P3}').group(1)),
    'C_die': p3(line(rf'C_die J/K {P3}').group(1)),
    'C_lid': p3(line(rf'\| C_lid {P3}').group(1)),
    'C_sub': p3(line(rf'C_substrate\(all\) {P3}').group(1)),
    'C_J': p3(line(rf'C_J \(die\+lid\+fast substrate\) J/K: {P3}').group(1)),
    'C_B': p3(line(rf'C_B \(near package\) {P3}').group(1)),
    'foster': [{'tau_s': t, 'R': r, 'C': round(t / r, 1)} for t, r in zip(M.taus, M.Rs)],
    'foster_total': round(sum(M.Rs), 3),
    'src_foster': 'docs/findings/11-thermal-model.md:29-31',
}
m = line(rf'R lid-top->air: still {P3} C/W, fan {P3}')
bare = {
    'R_lid_still': p3(m.group(1)), 'R_lid_fan': p3(m.group(2)),
    'theta_still': p3(line(rf'theta_JA bare, STILL AIR: {P3}').group(1)),
    'theta_fan': p3(line(rf'theta_JA bare, FAN 1-2.5 m/s: {P3}').group(1)),
    'lid_share_still': p3(line(rf'share of heat through the lid top \(still\): {P3}').group(1)),
    # vendor theta_JA tables, lidded packages with no heatsink: AMD UG575 Table 10-1 (40-47.5 mm; still air, and
    # 250-500 LFM = 1.27-2.54 m/s) and Microchip UG0722 Table 9-1 (MPF500T in the 35 mm FCG1152; still air, 1.0 and 2.5 m/s)
    'vendor_still': [5.4, 7.9], 'vendor_fan': [2.7, 5.8],
    'range_still': list(M.TH_STILL), 'range_fan': list(M.TH_FAN),
}

# ---------- C, D: per card ----------
cards = {}
for c in CARDS:
    law = M.LAWS.get(c)
    e = line(rf'^{re.escape(c)}\s+effective theta with its cooler \(board basis\) ({NUM})-({NUM}) C/W')
    tm = line(rf'^{re.escape(c)}\s+largest theta \(SoC basis\) with ANY idle equilibrium: ({NUM})-({NUM}) C/W')
    gl = line(rf'^{re.escape(c)}\s+largest theta.*\n\s+bare loop gain theta\*dP_SoC/dT\s+(.*)$')
    gains = {}
    for T, fan_lo, st_lo, st_hi in re.findall(rf'(\d+)C: fan ({NUM})\.\. still ({NUM})-({NUM})', gl.group(1)):
        # the model prints the fan range's low end only; its high end is the same product at the range's top
        fan_hi = M.TH_FAN[1] * M.F_SLOPE[1] * float(M.dP_board(c, int(T)))
        gains[T] = {'fan_lo': float(fan_lo), 'fan_hi': round(fan_hi, 2), 'still_lo': float(st_lo), 'still_hi': float(st_hi)}
    ol = line(rf'^{re.escape(c)}\s+largest theta.*\n.*\n\s+open-loop rise at idle SoC power ({NUM})-({NUM}) W: still ({NUM})-({NUM}) C, fan ({NUM})-({NUM}) C')
    eq = {}
    for air in ('still', 'fan'):
        q = line(rf'^  {re.escape(c)}\s+{air}\s*: equilibrium in (\d+)% of draws \((\d+) of (\d+)\); below 90 C in (\d+)%; T_eq (.*)$')
        teq = q.group(5).strip()
        eq[air] = {'n_ok': int(q.group(2)), 'n': int(q.group(3)), 'pct_ok': int(q.group(1)),
                   'T_eq': None if teq == 'none' else p3(teq)}
    slope_T = list(range(30, 121))
    cards[CARD_ID[c]] = {
        'label': c,
        'law': None if law is None else {'P_fix': law[0], 'A80': law[1], 'T_L': law[2]},
        'c0_law': None if law else {'P62': M.C0_P62, 'S62': M.C0_S62, 'T_L': 30.0, 'T_L_range': [25, 36]},
        'idle_T': M.IDLE_PT[c], 'idle_board_w': round(float(M.P_board(c, M.IDLE_PT[c])), 2),
        'theta_sink': [float(e.group(1)), float(e.group(2))],
        'theta_max': [float(tm.group(1)), float(tm.group(2))],
        'loop_gain_bare': gains,
        'open_loop_rise': {'P_soc': [float(ol.group(1)), float(ol.group(2))], 'still': [float(ol.group(3)), float(ol.group(4))],
                           'fan': [float(ol.group(5)), float(ol.group(6))]},
        'equilibrium': eq,
        'slope': [[T, round(float(M.dP_board(c, T)), 4)] for T in slope_T],
    }
# the fitted range of each idle law (docs/reports/data/2026-09-28-overheating/analysis/idle_vs_temp.txt) and card 0's
# measured span (card0_guard.py): the chart draws the law solid there and dashed where it is extrapolated
FIT_RANGE = {'aifoundry2': [67, 84], 'aifoundry3': [54, 85], 'aifoundry1-c1': [56, 82], 'aifoundry1-c0': [60, 64]}
for k, v in FIT_RANGE.items():
    cards[k]['fit_range'] = v
runaway = {'a2_gain_80': 0.948, 'gain_1_at': 81.9, 'rest_22_8': 62.1, 'threshold_22_8': 98.7,
           'src': 'docs/reports/data/2026-09-28-overheating/analysis/runaway.txt:1-4'}

# ---------- E: transients ----------
LOADS = {'idle': 'idle', '+9 W (ones, 1,024)': '+9', '+23 W (randn, 1,024)': '+23'}
cold = []
for mm in re.finditer(rf'^COLD (\S+)\s+(still|fan)\s+(idle|\+9 W \(ones, 1,024\)|\+23 W \(randn, 1,024\))\s+t90 {P3} s \| '
                      rf't120 {P3} s \| T@30s {P3} \| T@60s {P3} \| T@90s {P3} C \| never 90: (\d+)%', OUT, re.M):
    cold.append({'card': CARD_ID[mm.group(1)], 'air': mm.group(2), 'load': LOADS[mm.group(3)], 't90': p3(mm.group(4)),
                 't120': p3(mm.group(5)), 'T30': p3(mm.group(6)), 'T60': p3(mm.group(7)), 'T90': p3(mm.group(8)),
                 'never90_pct': int(mm.group(9))})
hot = []
for mm in re.finditer(rf'^HOT  (\S+)\s+still (idle|\+23 W), cooler removed at 73 C: t90 {P3} s, t120 {P3} s', OUT, re.M):
    hot.append({'card': CARD_ID[mm.group(1)], 'air': 'still', 'load': 'idle' if mm.group(2) == 'idle' else '+23',
                't90': p3(mm.group(3)), 't120': p3(mm.group(4)), 'start_T': 73})
boot = []
for mm in re.finditer(rf'^  (\S+)\s+(still|fan)\s+(idle|\+9 W \(ones, 1,024\)|\+23 W \(randn, 1,024\))\s+T_J at boot end {P3} C \| '
                      rf'window to 90 C {P3} s \| already >=90 at boot: (\d+)%', OUT, re.M):
    boot.append({'card': CARD_ID[mm.group(1)], 'air': mm.group(2), 'load': LOADS[mm.group(3)], 'T_boot': p3(mm.group(4)),
                 'window': p3(mm.group(5)), 'already90_pct': int(mm.group(6))})
m = line(rf'adiabatic initial heating rate, idle SoC 20-27 W over C_J: {P3} C/s; \+23 W load: {P3} C/s')
rates = {'idle': p3(m.group(1)), 'load': p3(m.group(2))}
if not (len(cold) == 20 and len(hot) == 2 and len(boot) == 18):
    sys.exit(f'transient lines: {len(cold)} cold, {len(hot)} hot, {len(boot)} boot (expected 20, 2, 18)')

# ---------- F, G: thermocouple and decay lengths ----------
m = line(rf'absolute error \(rss\) {P3} C')
m2 = line(rf'die mean - lid centre \(theta_JC \* P\): idle {P3} C, under \+23 W load {P3} C')
tc = {'abs_err': p3(m.group(1)), 'die_minus_lid_idle': p3(m2.group(1)), 'die_minus_lid_load': p3(m2.group(2)),
      'step_res': [0.02, 0.1], 'response_s': [0.1, 0.5], 'uncal_K': [2, 3]}
decay = [
    {'key': 'bare_lid', 'what': 'bare lid, cooled by still air', 'v': p3(line(rf'bare lid as a convectively cooled fin.*?: {P3} mm').group(1))},
    {'key': 'bare_die_lid', 'what': 'heatsink off: die and lid spreading over the substrate', 'v': p3(line(rf'heatsink OFF, die\+lid composite.*?: {P3} mm').group(1))},
    {'key': 'sink_lid', 'what': 'heatsink on: the lid (hidden under the sink)', 'v': p3(line(rf'lid with the heatsink on.*?: {P3} mm').group(1))},
    {'key': 'delid', 'what': 'delidded die under an IR-window cooler', 'v': p3(line(rf'delidded die under an IR-window liquid cooler.*?: {P3} mm').group(1))},
]
for f in (1, 5, 10):
    decay.append({'key': f'lockin{f}', 'what': f'the same, lock-in at {f} Hz (diffusion length in silicon)',
                  'v': p3(line(rf'lock-in diffusion length in Si at {f} Hz.*?: {P3} mm').group(1))})
bump = {r: p3(line(rf'1 W concentrated \(one shire\), heatsink off: excess at r = {r} mm: {P3} C').group(1)) for r in (2, 10, 20)}
sensor = {'decay': decay, 'shire_pitch_mm': 3.7, 'die_mm': [22.2, 25.6], 'lid_mm': 44.8, 'eps_lid': [0.05, 0.3],
          'bump_1W': {str(k): v for k, v in bump.items()}}

# ---------- trajectories after power-on (aifoundry2) ----------
rng = np.random.default_rng(20260930)
U = lambda lo, hi, n: rng.uniform(lo, hi, n)
LU = lambda lo, hi, n: np.exp(rng.uniform(math.log(lo), math.log(hi), n))
T_END, DT, NTR = 300.0, 2.0, 400
GRID = np.arange(0.0, T_END + 1e-9, DT)
CAP = 150.0   # the model stops a run at 150 C


def traj_bare(card, air, extra, n=NTR):
    """nohs_calc.mc_transient's draws, cold start; T_J on GRID (150 = past 150 C)"""
    thJB = LU(1.0, 3.0, n)
    if air == 'still':
        Rlid = 1.0 / (U(8, 15, n) * M.A_LID) + U(0.03, 0.10, n)
        RBA = LU(2.5, 8.0, n)
    else:
        Rlid = 1.0 / (U(20, 50, n) * M.A_LID) + U(0.03, 0.10, n)
        RBA = LU(0.8, 3.0, n)
    CJ, CB, Ta = U(9.0, 18.0, n), U(30.0, 80.0, n), U(22.0, 30.0, n)
    Poff, fs, phi = U(*M.P_OFF[card], n), U(*M.F_SLOPE, n), U(0.3, 1.0, n)
    out = np.full((n, len(GRID)), CAP)
    for i in range(n):
        def f(t, y):
            TJ, TB = y
            P = max(M.soc_power(card, TJ, Poff[i], fs[i]), 0.0) + extra
            q = (TJ - TB) / thJB[i]
            return [(P - q - (TJ - Ta[i]) / Rlid[i]) / CJ[i], (phi[i] * Poff[i] + q - (TB - Ta[i]) / RBA[i]) / CB[i]]
        cap = lambda t, y: y[0] - CAP
        cap.terminal, cap.direction = True, 1
        s = solve_ivp(f, (0, T_END), [Ta[i], Ta[i]], t_eval=GRID, events=[cap], max_step=0.5)
        out[i, :len(s.t)] = np.minimum(s.y[0], CAP)
    return out


# The heatsink: the Foster chain fitted on aifoundry2 (11-thermal-model.md: T = T0 + sum x_k, tau_k dx_k/dt = R_k P - x_k)
# with board power P = 12.63 + 23.26 e^((T-80)/36) (runaway.txt), plus, under the matmul, the fitted model's 1.85 W for the
# tensor state machines of 1,024 minions and 27.2 W of switching for random normal operands (11-thermal-model.md's power
# line; 12-heat-management.md:20). T0 is drawn between the two fitted intercepts, 22.8 and 28.0 C (11-thermal-model.md:33).
SINK_LOAD_W = 1.85 + 27.2


def traj_sink(extra_board, n=NTR):
    T0 = U(22.8, 28.0, n)
    taus, Rs = np.array(M.taus), np.array(M.Rs)
    out = np.full((n, len(GRID)), CAP)
    for i in range(n):
        def f(t, x):
            T = T0[i] + x.sum()
            P = 12.63 + 23.26 * math.exp((T - 80.0) / 36.0) + extra_board
            return (Rs * P - x) / taus
        s = solve_ivp(f, (0, T_END), np.zeros(6), t_eval=GRID, max_step=0.5)
        out[i, :len(s.t)] = np.minimum(T0[i] + s.y.sum(axis=0), CAP)
    return out


def summ(a):
    q = np.percentile(a, [5, 50, 95], axis=0)
    return {'p5': [round(float(v), 1) for v in q[0]], 'p50': [round(float(v), 1) for v in q[1]],
            'p95': [round(float(v), 1) for v in q[2]]}


traj = {'t': [float(t) for t in GRID], 'n': NTR, 'seed': 20260930, 'cap_C': CAP, 'boot_window_s': [30, 90],
        'sink_load_board_w': SINK_LOAD_W, 'cases': {}}
for load, extra in (('idle', 0.0), ('+23', 23.0)):
    traj['cases'][load] = {
        'still': summ(traj_bare('aifoundry2', 'still', extra)),
        'fan': summ(traj_bare('aifoundry2', 'fan', extra)),
        'sink': summ(traj_sink(0.0 if load == 'idle' else SINK_LOAD_W)),
    }

# ---------- the options, ranked (the brief's table, plus who does each) ----------
options = [
    {'rank': 1, 'option': 'Keep the heatsink; use the on-die sensors (read with lock-in of a pattern of work switched against its '
                          'complement), the IR-drop voltage map, and the thermal camera on the back of '
                          'the board and on the heatsink, with emissivity tape wherever it looks', 'feasible': 'now', 'risk': 'none', 'cost': '$0–350', 'time': 'days',
     'measures': 'where the unmetered ~14–17 W goes on the board; current per shire; with lock-in, a coarse map of where the work runs '
                 '(section 5.4: on the stock firmware one sensor beside the I/O shire, read with a slow dither of the chip\'s power; a '
                 'map of every shire needs a rebuilt boot loader)',
     'who': 'us for the host-side readings; AI Foundry\'s people on site to mount the camera'},
    {'rank': 2, 'option': 'A fine thermocouple taped to the heatsink base or fins, never between the lid and the heatsink, read by '
                          'a standalone logger', 'feasible': 'one visit, card off',
     'risk': 'negligible', 'cost': '$30–100', 'time': '30 min on site',
     'measures': 'the heatsink\'s own temperature, which the camera plan suggests explains the all-ones matmul\'s 107 s '
                 'against 162–167 s to 90 °C from the same 80 °C reading (R6, R13; inference); a log independent of the host',
     'who': 'AI Foundry\'s people on site, with the lab lead\'s consent; the lab admin powers the host down and up'},
    {'rank': 3, 'option': 'A fine thermocouple soldered into a groove cut in the lid\'s centre (Intel\'s case-temperature method), on '
                          'aifoundry1 card 0 during the visit request SH1 already asks for', 'feasible': 'only with the lab\'s consent',
     'risk': 'moderate: the lid is cut, and Intel solders the bead in at 150 °C; the heatsink comes off and is re-pasted, which '
             'resets that card\'s fitted thermal constants', 'cost': '$50–150 plus machining', 'time': 'about a day',
     'measures': 'the lid\'s temperature at its centre, where Intel defines case temperature; θJC; a physical point between die and cooler',
     'who': 'AI Foundry\'s people on site, with the lab lead\'s and AI Foundry\'s consent for card 0'},
    {'rank': 4, 'option': 'A bare card on a bench: 12 V through a relay that a thermocouple at 85 °C opens within half a second, '
                          'and a fan', 'feasible': 'a spare card only',
     'risk': 'to that card', 'cost': '$150–400', 'time': 'days',
     'measures': 'the bare package\'s heat capacity and θJA (tests whether the 1.5 s stage is the package)',
     'who': 'whoever holds a spare card, with AI Foundry\'s consent'},
    {'rank': 5, 'option': 'An IR-window liquid cooler on a delidded die, imaged by a mid-wave IR camera as the published setups were '
                          '(for the P3, a germanium or zinc-selenide window over a mineral-oil film, untried)', 'feasible': 'a sacrificial card only',
     'risk': 'the card is lost if delidding fails: an exposed die\'s corners are easily damaged, one slip can damage the parts '
             'around it, and a soldered lid needs 165–180 °C to lift', 'cost': 'thousands of dollars (a 50 mm germanium or zinc-selenide window alone about $900)',
     'time': 'weeks',
     'measures': 'temperature maps at the scale of a shire',
     'who': 'a lab equipped for delidding and IR imaging, with AI Foundry\'s consent for the card'},
    {'rank': 6, 'option': 'A bare card running short bursts in a lab host: at 600 MHz; or at 100 MHz and the firmware\'s lowest voltages, '
                          'behind a latching mains cut at 80 °C, with a fan or blower (section 5.5, alternative 3)',
     'feasible': 'not at 600 MHz; at 100 MHz only in some power-ons, with forced air',
     'risk': 'high at 600 MHz; at 100 MHz moderate, behind the cut and only after the measurement plan',
     'cost': '—', 'time': '—',
     'measures': 'at 600 MHz nothing worth the risk; at 100 MHz, through a taped lid and with lock-in, single shires and coarse '
                 'patterns within about 10 s and a checkerboard of shires in about half a minute, inside the minute or so a fan '
                 'leaves in about three power-ons in five; in still air, none (sections 5.3–5.4)',
     'who': 'the lab lead and someone on site throughout, with the owner\'s approval, after Stages A and B of the plan'},
]
prereq = ('Options 4 and 5 need a card that may be lost: the loose green board with a copper block on the lab\'s top shelf, if it '
          'is an ET card (unidentified: question 6 in the full camera plan), or card 0 only with AI Foundry\'s consent.')


# ---------- the low-clock envelope (added 30 September, evening, at the owner's request) ----------
# Read from the models' own records, never recomputed here: lowclock_calc.json (lowclock_calc.py, the envelope model,
# seed 20260930, 2,000 accepted draws), imaging_calc.json (imaging_calc.py, the imaging model, seed 20260930, 240 draws)
# and lc_plan_calc.out (lc_plan_calc.py, the measurement plan's registered predictions). Each is checked against its
# printout first, so a stale JSON stops the build.
def lowclock_block():
    rd = lambda fn: open(os.path.join(HERE, fn)).read()
    LC, IM = json.loads(rd('lowclock_calc.json')), json.loads(rd('imaging_calc.json'))
    LCO, IMO, PLO = rd('lowclock_calc.out'), rd('imaging_calc.out'), rd('lc_plan_calc.out')
    if not LCO.rstrip().endswith('wrote lowclock_calc.json'):
        sys.exit('lowclock_calc.out does not end with its JSON line: rerun lowclock_calc.py --json lowclock_calc.json')
    if not IMO.rstrip().endswith('imaging_calc.json'):
        sys.exit('imaging_calc.out does not end with its JSON line: rerun imaging_calc.py --json imaging_calc.json')
    if f"imaging_calc.json (seed {IM['seed']}, {IM['draws']} draws)" not in LCO:
        sys.exit('lowclock_calc.out did not read this imaging_calc.json: rerun imaging_calc.py, then lowclock_calc.py')
    g3 = lambda v: ' / '.join(f'{x:.3g}' for x in v)
    a2 = LC['answers']['aifoundry2']
    if f"removes {g3(a2['clock_only_100'])} W" not in LCO:
        sys.exit('lowclock_calc.json does not match lowclock_calc.out (section I): rerun lowclock_calc.py with --json')
    r = lambda v, nd=4: None if v is None else (round(v, nd) if isinstance(v, (int, float)) else [None if x is None or x >= 1e8 else round(x, nd) for x in v])
    CARDS_LC, POL = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1'], ['boot', 'floor', 'floor+NoC']
    clocks, settable = [600, 400, 300, 200, 100, 50, 25, 10], [600, 400, 300, 200, 100]

    def st(s):
        o = {k: round(s[k]['p_below85'], 4) for k in ('still', 'fan', 'heatsink', 'irwin', 'still_net', 'fan_net') if k in s}
        o.update({'n_fan': s['fan']['n_stable'], 'T_fan': r(s['fan']['T_eq'], 1), 'T_sink': r(s['heatsink']['T_eq'], 1),
                  'T_win': r(s['irwin']['T_eq'], 1), 'th85': r(s['theta85_soc'])})
        return o
    pts = {}
    for c in CARDS_LC + ['aifoundry1-c0']:
        pts[c] = {}
        for p in POL:
            rows = []
            for f in clocks:
                k = f'{c}|{f}|{p}'
                if k not in LC['operating_points']:
                    continue
                op = LC['operating_points'][k]
                rows.append({'f': f, 'mV': op['mV'], 'noc': op['noc'], 'status': op['status'],
                             'P': {t: r(op['board_W'][t], 3) for t in ('25', '40', '60')},
                             'dP60': r(op['dPdT_board']['60']), 'dPsoc60': r(op['dPdT_soc']['60']), 'P16': r(op['board16_60'], 3),
                             'idle': st(LC['steady'][k + '|idle']), 'pattern': st(LC['steady'][k + '|pattern'])})
            if rows:
                pts[c][p] = rows
    floor = {k: {'board60': r(v['board_W']['60'], 2), 'board25': r(v['board_W']['25'], 2), 'soc60': r(v['soc_W']['60'], 2),
                 'frac60': r(v['removed_frac_60'])} for k, v in LC['floor_no_clock_removes'].items()}
    decomp = {k: {q: r(v[q], 2) for q in ('board', 'fixed', 'leak', 'clock_tree')} for k, v in LC['decomposition'].items()
              if k.endswith('|60') or k.endswith('|62') or k.endswith('|56')}
    window = {}
    for k, v in LC['window_after_boot'].items():
        if k.endswith('|boot_end'):
            window[k] = {'T': r(v['T_C'], 1), 'ge85': round(v['frac_ge85'], 4)}
        else:   # whole seconds, rounded as the printout rounds; 'look': from the low point being set to each stop
            window[k] = {'t85': r(v['t85_s'], 0), 'never': round(v['never_frac'], 4),
                         'look': {t: r(x, 0) for t, x in v['look_s'].items()},
                         'none': {t: round(x, 4) for t, x in v['look_none'].items()}}
    VIEWS = {'lid_tape': '(b) lid top, taped, fan', 'lid_still': '(b) lid top, taped, still air', 'die_coated': '(a) delidded die, black-coated, fan',
             'die_win': '(a) delidded die, black-coated, IR-window cooler', 'sensors': 'sensors', 'stock': 'stock'}
    himg = {}
    for k, v in LC['imaging'].items():
        f, p, view, pat = k.split('|')
        vk = next((a for a, b in VIEWS.items() if b == view), None)
        if vk:
            himg[f'{f}|{p}|{vk}|{pat}'] = {'mW': r(v['mW_per_shire'], 1), 'mK': r(v['contrast_mK'], 2), 'lockin_s': r(v['lockin_s'], 1),
                                           'upper': v['upper_bound'], 'settle': round(v['p_settle85'], 4)}
    IV = {'die_coated': '(a) delidded die, black-coated, fan', 'die_si': '(a) delidded die, bare silicon, fan',
          'die_win': '(a) delidded die, black-coated, IR-window cooler', 'lid_tape': '(b) lid top, taped, fan', 'lid_bare': '(b) lid top, bare plating, fan'}
    lockin = {k: {pat: {f: r(t, 1) for f, t in d.items()} for pat, d in IM['lockin_time_s_floor'][v].items()} for k, v in IV.items()}
    least = {k: {pat: {m: r(x['fmin_MHz_floor_median'], 2) for m, x in d.items()} for pat, d in IM['least_power'][v].items()} for k, v in IV.items()}
    sensors = {k.split('|')[1]: r(v['fmin_MHz_floor_median'], 2) for k, v in IM['sensors'].items() if k.startswith('c_hs|')}
    stock = {k: r(v['fmin_MHz_floor_median'], 1) for k, v in IM['stock_io'].items()}
    env = {k: {'hi90': v['highest_settable_90'], 'best': round(v['best_p'], 4), 'at': v['best_p_at']} for k, v in LC['envelope'].items()}
    # the measurement plan's bare card at the lowest settable point (lc_plan_calc.out section F) and its schedule (section H)
    pon = {}
    for air in ('still', 'fan', 'blower'):
        m = re.search(rf'central \(D_m 2\.09 W, n 2\.42\) \| {air}\s*: .*?peak < 80: (\d+)%; end <= 70: (\d+)%; both: (\d+)%', PLO)
        if not m:
            sys.exit('lc_plan_calc.out: power-on line not found for ' + air)
        pon[air] = {'peak_lt80': int(m.group(1)), 'end_le70': int(m.group(2)), 'both': int(m.group(3))}
    eqm = {air: int(re.search(rf'central \(D_m 2\.09 W, n 2\.42\)\s+{air}\s*: equilibrium\s+(\d+)%', PLO).group(1)) for air in ('still', 'fan', 'blower')}
    eqr = {air: int(re.search(rf'rival TH-VD n = 1\.8, D best fit\s+{air}\s*: equilibrium\s+(\d+)%', PLO).group(1)) for air in ('still', 'fan', 'blower')}
    mrba = re.search(rf'its board-to-air resistance R_BA ({NUM} / {NUM} / {NUM}) C/W', PLO)
    if not mrba:
        sys.exit('lc_plan_calc.out: the blower R_BA line was not found')
    mb = re.search(rf'a blower at 3-6 m/s .*?theta_JA ({NUM} / {NUM} / {NUM}) C/W', PLO)
    ma = re.search(r'Stage A: .*?: (\d+) min of card time \((\d+) min without', PLO)
    mbB = re.search(r'Stage B: .*?: (\d+) min of card time', PLO)
    mlow = re.search(rf'this plan \(section E\): ({NUM} / {NUM} / {NUM}) W', PLO)
    mstep = re.search(rf'600 -> 100 MHz: envelope model ({NUM} / {NUM} / {NUM}) W', PLO)
    mpstep = re.search(rf'600 -> 100 MHz \(TH-CS, joint draws\), the fall in W: board ({NUM} / {NUM} / {NUM});', PLO)
    if not all((mb, ma, mbB, mlow, mstep, mpstep)):
        sys.exit('lc_plan_calc.out: a plan line was not found')
    plan = {'power_on_central': pon, 'equilibrium_central_pct': eqm, 'equilibrium_rival_pct': eqr, 'blower_theta': p3(mb.group(1)),
            'blower_rba': p3(mrba.group(1)),
            'stageA_min': [int(ma.group(1)), int(ma.group(2))], 'stageB_min': int(mbB.group(1)),
            'low_point_56C_plan': p3(mlow.group(1)), 'step_100_envelope': p3(mstep.group(1)), 'step_100_plan': p3(mpstep.group(1)),
            'file': 'docs/reports/data/2026-09-30-without-heatsink/LOWCLOCK-PLAN.md'}
    # the imaging printout's tables the page shows: the camera-read contrast (1 s per state, 600 / 100 / 10 MHz), the
    # camera thresholds, the IR-window transmission, the MAP check's steady centre and edge values, the quantiser check
    contrast = {}
    for view, key in (('(a) delidded die, black-coated, fan', 'die_coated'), ('(b) lid top, taped, fan', 'lid_tape'),
                      ('(b) lid top, bare plating, fan', 'lid_bare'), ('(a) delidded die, black-coated, IR-window cooler', 'die_win')):
        m = re.search(re.escape(view) + r'\s+(checkerboard: .*?)\s+\(600 / 100 / 10 MHz\)', IMO)
        if not m:
            sys.exit('imaging_calc.out: contrast line not found for ' + view)
        contrast[key] = {pt: [float(x) for x in re.findall(NUM, cells)[:3]]
                         for pt, cells in re.findall(r'(checkerboard|one shire|2x2 block moving|half die): ([^|]+)', m.group(1))}
    mtau = re.search(rf'window x oil-film transmission ({NUM} / {NUM} / {NUM})', IMO)
    mpos = [re.search(rf'I/O at \({w}\): ({NUM}) / ({NUM}) / ({NUM}) C \(medians\)', IMO) for w in ('0,4', '0,5')]
    if not (mtau and all(mpos)):
        sys.exit('imaging_calc.out: transmission or MAP position line not found')
    sens_c = {}
    for f_, p_ in (('600', 'boot'), ('100', 'floor')):
        sens_c[f_] = {pt: r(LC['imaging'][f'{f_}|{p_}|sensors|{pt}']['contrast_mK'], 1)
                      for pt in ('checkerboard', 'one shire', '2x2 block moving', 'half die')}
    imgx = {'contrast_mK': contrast, 'sensors_mK': sens_c, 'threshold_mK': {k: r(v, 3) for k, v in IM['camera_threshold_mK'].items()},
            'tau_window': p3(mtau.group(1)),
            'map_steady_C': {'centre': [float(mpos[0].group(1)), float(mpos[1].group(1))],
                             'edge': [float(mpos[0].group(3)), float(mpos[1].group(3))]},
            'quantiser': {k: {q: (r(v[q], 3) if isinstance(v[q], (list, float)) else v[q]) for q in v}
                          for k, v in IM['stock_quantiser'].items()},
            'stock_lockin_100_s': r(LC['imaging']['100|floor|stock|2x2 block moving']['lockin_s'], 0),
            'p_shire_mW': {f'{f_}|{p_}': r(LC['imaging'][f'{f_}|{p_}|(b) lid top, taped, fan|checkerboard']['mW_per_shire'], 0)
                           for f_, p_ in (('600', 'boot'), ('300', 'boot'), ('300', 'floor'), ('100', 'floor'))}}
    return {
        'model': 'lowclock_calc.py (seed %d, %d accepted draws); imaging_calc.py (seed %d, %d draws); lc_plan_calc.py'
                 % (LC['seed'], LC['draws'], IM['seed'], IM['draws']),
        'draws': LC['draws'], 'img_draws': IM['draws'],
        'clocks': clocks, 'settable': settable, 'cards': CARDS_LC, 'policies': POL, 'pts': pts, 'floor': floor,
        'answers': {c: {k: ({q: r(x) for q, x in v.items()} if isinstance(v, dict) else r(v)) for k, v in a.items()}
                    for c, a in LC['answers'].items()},
        'anchors': {k: r(v) for k, v in LC['anchors'].items()}, 'clock_tree': LC['shared_clock_tree_W'],
        'decomp': decomp, 'window': window, 'envelope': env, 'img': himg, 'lockin': lockin, 'least_clock': least,
        'sensors_least': sensors, 'stock_least': stock, 'plan': plan, 'imgx': imgx,
        'ct_left_100': r(LC['clock_tree_left_100_floor_die_W']), 'theta_eff_fan': r(LC['theta_eff_net']['fan'], 3),
    }


lowclock = lowclock_block()

page = {
    'generated_by': 'docs/reports/data/2026-09-30-without-heatsink/make_page_data.py',
    'model': 'nohs_calc.py (seed 20260929), output nohs_calc.out',
    'package': pkg, 'bare': bare, 'cards': cards, 'runaway_sink': runaway,
    'transients': {'cold': cold, 'hot': hot, 'boot': boot, 'rates': rates, 'boot_assumed_s': [30, 90],
                   'sink_measured': {'randn_80_90_s': [19, 26], 'ones_80_90_s': [107, 167]}},
    'traj': traj, 'thermocouple': tc, 'sensor': sensor, 'options': options, 'prereq': prereq, 'lowclock': lowclock,
}
dst = os.path.join(HERE, 'page.json')
new = json.dumps(page, indent=1, ensure_ascii=False) + '\n'
if '--check' in sys.argv:
    old = open(dst).read() if os.path.exists(dst) else ''
    print('page.json is current' if old == new else 'page.json is stale')
    sys.exit(0 if old == new else 1)
open(dst, 'w').write(new)
print('wrote', dst, len(new), 'bytes')
