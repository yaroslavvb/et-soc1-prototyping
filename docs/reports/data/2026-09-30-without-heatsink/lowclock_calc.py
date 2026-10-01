#!/usr/bin/env python3
"""A slower, lower-voltage ET-SoC-1 without its heatsink: the envelope model (the owner's question of 30 Sep 2026,
~15:45 PDT: how low can the clock go, 100 MHz, 10 MHz, and could a card run ten times slower with no heatsink so that a
thermal camera sees where the computation sits).

Every input names its source (paths relative to the repository root) or is marked ASSUMED / ESTIMATE; every printed
number carries a label: [measured] (the cards' record), [source] (firmware or vendor text), [outside] (a cited outside
source), [fitted] (a fit to measured data), [model], [assumed], [inference].  Ranges are drawn in a Monte Carlo
(uniform; log-uniform where written LU), seed 20260930; outputs are 5th / 50th / 95th percentiles unless a line says
otherwise.  Pure arithmetic on files already in the repository: no card is touched.

THE MODEL.  Each card's idle board power is its measured law at its own operating point (nohs_calc.py section C, the
E44 cooling cycles), minus what a new clock and voltage remove from the three metered rails:

    rail x (minion, SRAM, NoC) = D_x * (f/f0) * (V/V0)^2  +  L_x(T) * G_x(V),     G_x(V) = (V/V0) * exp(kappa_x (V - V0))

D_x is the rail's temperature-independent part (the idle clock tree: the minions sit in WFI, clock-gated inside the
core, but the shire clocks run), L_x(T) = A_x exp((T-80)/T_L) its leakage, both fitted per card and rail on the E44
idle cycles (section B).  kappa_m, the minion leakage's voltage sensitivity, is fixed by two measurements (section C):
aifoundry2's idle at 800 MHz / 0.618 V against 600 MHz / 0.518 V at the same die temperature (vf.json), and aifoundry1
card 0's minion rail at 300 MHz / 0.398 V against aifoundry2's at 600 MHz / 0.519 V at the same die temperature (62 C),
the two chips matched by their NoC rails.  The outside physics (TSMC N7 DIBL ~40 mV/V, swing ~65 mV/decade) gives
kappa = 1.4 /V as the weakest plausible dependence.  The SRAM's kappa_s is drawn wide and is held only by anchor (i),
through the SRAM rail's step at 800 MHz (its 830 mV there is recorded in E51; revised 30 Sep, review).  A switching
workload adds n_shires * P600 * (f/600) * (V/0.517)^2 on the die (the flip model's energies at fixed activity per
cycle; 13-why-low-power.md: 600 against 800 MHz switching agrees with V^2 f to about 10 %).

The SoC (on-die) power is nohs_calc.py's P_SoC(T) (board minus off-die power, the off-die share of the slope removed)
minus the removed rail power; the removed rail power's regulator loss comes off the board, not the die.  The bare
package is nohs_calc.py section D's: theta_JA on the SoC basis, 4-12 C/W in still air, 2-7 C/W with a fan (log-
uniform), ambient 22-30 C; the die settles where Ta + theta * P_SoC(T) = T first holds, and runs away if it never does.
Section F2 also settles the transient model's two-node network, which adds the board's heating by the off-die power.
With the heatsink on, each card's own effective thermal resistance on the board basis reproduces its measured idle
temperature at its own operating point (nohs_calc.py section C).

Sections:  A what the firmware can set        B idle rails against die temperature, fitted per card
           C the anchors: leakage's voltage dependence and the clock tree's share
           D the decomposition of idle and loaded power      E operating points: board power, dP/dT
           F steady state: bare (still air, fan), heatsink on, IR-window cooler
           F2 bare: the two-node network settled (with the board's own heating), and the window after the host boots:
              the low point set 20-60 s after the boot, the look until the plan's 75 C watcher (80 C relay, 85 C)
           G the envelope: the highest clock that settles below 85 C with 90 % probability; the floor; theta needed
           H imaging at each settable point (imaging_calc.json)      I direct answers

Run from anywhere: python3 lowclock_calc.py [--draws N] [--json out.json] [--imaging path/to/imaging_calc.json]
"""
import argparse
import collections
import glob
import gzip
import json
import math
import os
import re
import warnings

import numpy as np

warnings.filterwarnings('ignore', message='All-NaN slice')

ap = argparse.ArgumentParser()
ap.add_argument('--draws', type=int, default=2000, help='accepted Monte Carlo draws (default 2000)')
ap.add_argument('--json', default=None, help='also write the summary numbers to this JSON file')
ap.add_argument('--imaging', default=None, help='imaging_calc.json (default: next to this script)')
args = ap.parse_args()

HERE = os.path.dirname(os.path.abspath(__file__))


def find_root():
    for c in [os.path.join(HERE, *(['..'] * k)) for k in range(1, 6)] + ['/home/yaroslavvb/claude/et-soc1-prototyping']:
        if os.path.isdir(os.path.join(c, 'docs', 'reports', 'data', '2026-09-25-claims-v3')):
            return os.path.normpath(c)
    raise SystemExit('repository root not found')


ROOT = find_root()
DATA = os.path.join(ROOT, 'docs', 'reports', 'data')
SEED = 20260930
rng = np.random.default_rng(SEED)
N = args.draws
OUT = {'seed': SEED, 'draws': N}


def U(lo, hi, n):
    return rng.uniform(lo, hi, n)


def LU(lo, hi, n):
    return np.exp(rng.uniform(math.log(lo), math.log(hi), n))


def pct(x, p=(5, 50, 95), fmt='{:.3g}'):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return 'n/a'
    return ' / '.join(fmt.format(v) for v in np.percentile(x, p))


def p3(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return [float(v) for v in np.percentile(x, [5, 50, 95])] if len(x) else None


def hdr(t):
    print()
    print('=' * 110)
    print(t)
    print('=' * 110)


def jsonl(path):
    op = gzip.open(path, 'rt') if path.endswith('.gz') else open(path)
    out = []
    with op as fh:
        for line in fh:
            if line.strip().startswith('{'):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


CARDS = ['aifoundry2', 'aifoundry3', 'aifoundry1-c1', 'aifoundry1-c0']
SHORT = {'aifoundry2': 'a2', 'aifoundry3': 'a3', 'aifoundry1-c1': 'c1', 'aifoundry1-c0': 'c0'}

# ======================================================================================================================
hdr('A. What the firmware can set')
# The minions run on the step clock (SP PLL4, a Movellus HPDPLL) in every lab build; DM_CMD_SET_FREQUENCY with
# use_step_clock = 1 (what the stock dev_mngt_service sends) accepts exactly the outputs of the HPDPLL mode table and
# changes no voltage (BL2 services/thermal_power_monitor.c:775-800,870-920; main.c:94,411-414; minion_configuration.c:
# 670-721; work notes fw.md sections 0-2, decoded by pll_modes.py).  The table's outputs with the cards' 100 MHz
# reference, up to 700 MHz (etsoc-hal/include/hwinc/hpdpll_modes_config.h:637-767 for 100-275 MHz):
TABLE_MHZ = [100, 125, 150, 166, 175, 200, 225, 250, 275, 300, 325, 333, 350, 375, 400, 425, 450, 475, 498, 500, 502,
             505, 525, 550, 575, 600, 625, 650, 675, 700]
_h = os.path.join(ROOT, 'external', 'et-platform', 'etsoc-hal', 'include', 'hwinc', 'hpdpll_modes_config.h')
if os.path.exists(_h):
    txt = open(_h).read()
    blocks = re.findall(r'\.input_frequency\s*=\s*(\d+)[^}]*?\.output_frequency\s*=\s*(\d+)', txt, flags=re.S)
    parsed = sorted({int(o) // 1000000 for i, o in blocks if int(i) == 100000000 and int(o) <= 700000000})
    assert parsed == TABLE_MHZ, ('HPDPLL table differs from the recorded list', parsed)
    print(f'HPDPLL table read from {os.path.relpath(_h, ROOT)}: {len(parsed)} outputs <= 700 MHz with a 100 MHz '
          f'reference match the recorded list [source]')
else:
    print('external/et-platform not present; using the recorded list (fw.md section 2) [source]')
CLOCKS = [600, 400, 300, 200, 100, 50, 25, 10]
SETTABLE = {f: (f in TABLE_MHZ) for f in CLOCKS}
print('minion clocks studied: ' + ', '.join(f'{f} MHz ({"settable" if SETTABLE[f] else "NOT settable: no PLL mode"})'
                                            for f in CLOCKS) + ' [source]')
print('below 100 MHz: the post-dividers could reach 10-50 MHz (HPDPLL 9 bits, LVDPLL 8 bits), but no mode table entry, '
      'DM command or BL2 path programs them; PLL4 bypass and the shire mux\'s reference position are 100 MHz too [source]')
# Rail floors (BL2 0.20.0 / 0.21.0 / HEAD range checks, bl2_pmic_controller.h:170-248; 0.18.0 has none) and the vendor's
# safe state, 300 MHz at 400 mV minion / 660 mV SRAM (0.21.0 thermal_pwr_mgmt.h:67-80); card 0 idles there (398 / 660 mV
# on the die, measured below).
FLOOR = {'minion': 0.398, 'sram': 0.660, 'noc': 0.398}   # on-die volts for set-points 400 / 660 / 400 mV (card 0: 398 on die)
print('voltage floors the firmware accepts (0.20.0+): minion 400 mV, SRAM 660 mV, NoC 400 mV [source]; on the die a 400 mV '
      'set-point reads 398 mV (card 0) [measured]; 0.18.0 (card 1) checks nothing, and writes every NoC set to flash [source]')
print('policies: "boot" = SET_FREQUENCY only, voltages stay at the card\'s 600 MHz point; "floor" = minion 400 mV and SRAM '
      '660 mV at and below 300 MHz, linear to the 600 MHz point between (the safe state\'s pair; ASSUMED line between); '
      '"floor+NoC" = floor, and the NoC at 200 MHz (the vendor test\'s value, TestDevMgmtApiSyncCmds.cpp) and 400 mV '
      '(the firmware floor; the vendor\'s operating-point validator stops at 485 mV and 300 MHz, so untested) [source/assumed]')
print('at 400 MHz the floor line gives 438 mV (aifoundry2); the 0.18.0 governor\'s own law (10 mV per 50 MHz from the '
      'boot point) would give 460-478 mV and the measured 600-800 MHz table\'s slope, extrapolated, 416 mV: which is '
      'safe at 400 MHz is not established; at and below 300 MHz 400 / 660 mV is the vendor\'s safe state [source/inference]')
print('other rails are not lowered: DDR (700-870 mV accepted) feeds the memory shires at a fixed 933 MHz, PCIe-logic '
      '(731-815) the link (a link retrain hung a host on 30 Sep), Maxion is already at its 600 mV floor [source/inference]')

# ======================================================================================================================
hdr('B. Idle rails against die temperature, per card [measured], and their fits [fitted]')
# E44: the version-3 cooling cycles (heat to 88 C, then 900 s idle at 600 MHz), docs/reports/data/2026-09-25-claims-v3/
# raw/<card>/idle/p1..p3; idle = more than 5 s after the heater's last launch, clock 600 MHz (as the overheating page's
# idle_vs_temp.py).  Rails: the PMIC's output-side power per rail (sp.<rail>_w[0]); voltages on the die (die_mv).
BASE = os.path.join(DATA, '2026-09-25-claims-v3', 'raw')


def e44_bins(card):
    bins = collections.defaultdict(list)
    for pd in sorted(glob.glob(os.path.join(BASE, card, 'idle', 'p*'))):
        L = jsonl(os.path.join(pd, 'launches.jsonl'))
        if not L:
            continue
        t_last = max(x['t_end_ms'] for x in L)
        for s in jsonl(os.path.join(pd, 'telemetry.jsonl.gz')):
            if s['t_ms'] < t_last + 5000 or (s.get('mhz') or {}).get('minion') != 600:
                continue
            sp, dm = s['sp'], s['die_mv']
            bins[s['temp_c']['minshire'][0]].append((s['board_w'], sp['minion_w'][0], sp['sram_w'][0], sp['noc_w'][0],
                                                     dm['minion'], dm['sram'], dm['noc']))
    return bins


def h21_bins(sess):
    """aifoundry2's 21 Sep sessions (docs/reports/data/2026-09-21-horace-aifoundry2/<sess>): idle 600 MHz samples more
    than 5 s after a launch ended and more than 0.5 s before the next began"""
    d = os.path.join(DATA, '2026-09-21-horace-aifoundry2', sess)
    runs = jsonl(os.path.join(d, 'runs.jsonl'))
    iv = sorted((r['t_start_ms'], r['t_end_ms']) for r in runs)
    st, en = np.array([a for a, b in iv]), np.array([b for a, b in iv])
    bins = collections.defaultdict(list)
    for s in jsonl(os.path.join(d, 'telemetry.jsonl.gz')):
        t = s['t_ms']
        if s['mhz']['minion'] != 600:
            continue
        k = np.searchsorted(st, t) - 1
        if (k >= 0 and t < en[k] + 5000) or (k + 1 < len(st) and st[k + 1] - t < 500):
            continue
        sp = s['sp']
        bins[s['temp_c']['minshire'][0]].append((s['board_w'], sp['minion_w'][0], sp['sram_w'][0], sp['noc_w'][0],
                                                 s['die_mv']['minion'], np.nan, np.nan))
    return bins


def c0_bins():
    """aifoundry1 card 0 at 300 MHz (firmware 1.4.1's low_power state): the read-only guard samples under
    docs/reports/data/**/guard.jsonl.gz, as card0_guard.py"""
    bins = collections.defaultdict(list)
    for f in sorted(glob.glob(os.path.join(DATA, '**', 'guard.jsonl.gz'), recursive=True)):
        for d in jsonl(f):
            try:
                if d['mhz']['minion'] != 300:
                    continue
                bins[d['temp_c']['minshire'][0]].append((d['board_w'], d['sp']['minion_w'][0], d['sp']['sram_w'][0],
                                                         d['sp']['noc_w'][0], d['die_mv']['minion'],
                                                         d['die_mv']['sram'], d['die_mv']['noc']))
            except (KeyError, TypeError, IndexError):
                pass
    return bins


def table(bins, nmin=20):
    T = np.array(sorted(t for t in bins if len(bins[t]) >= nmin), dtype=float)
    n = np.array([len(bins[int(t)]) for t in T])
    M = np.array([np.nanmedian(np.array(bins[int(t)], dtype=float), axis=0) for t in T])
    return T, n, M


RAILS = ['minion', 'sram', 'noc']
BINS = {c: table(e44_bins(c)) for c in CARDS[:3]}
BINS['aifoundry1-c0'] = table(c0_bins())
H21 = {s: table(h21_bins(s), nmin=10) for s in ('cold1', 'cold2')}
for c in CARDS:
    T, n, M = BINS[c]
    print(f'{c:14s} {int(n.sum()):6d} idle samples in {len(T)} whole-degree bins {T.min():.0f}-{T.max():.0f} C; die mV '
          f'minion {np.median(M[:, 4]):.0f}, SRAM {np.nanmedian(M[:, 5]):.0f}, NoC {np.nanmedian(M[:, 6]):.0f} [measured]')
    for Tq in sorted({int(T.min()), 60, 62, 65, 70, 75, 80, int(T.max())}):
        k = np.where(T == Tq)[0]
        if len(k):
            m = M[k[0]]
            print(f'   {Tq:3d} C: board {m[0]:6.2f}  minion {m[1]:6.3f}  SRAM {m[2]:5.3f}  NoC {m[3]:5.3f}  off the rails '
                  f'{m[0]-m[1]-m[2]-m[3]:6.2f} W')
# Boot (reference) voltages on the die, from the same samples [measured]
BOOT = {}
for c in CARDS:
    T, n, M = BINS[c]
    BOOT[c] = {'vm': round(float(np.median(M[:, 4])) / 1000, 3), 'vs': round(float(np.nanmedian(M[:, 5])) / 1000, 3),
               'vn': round(float(np.nanmedian(M[:, 6])) / 1000, 3), 'f0': 300 if c == 'aifoundry1-c0' else 600}
FIT_TOL = 1.5
TL_GRID = np.arange(20, 61)


def fit_rail(T, n, P):
    """rail = F + A exp((T-80)/T_L) on a T_L grid; weights min(n, 500); the acceptable set: rms within FIT_TOL of the
    best fit, F >= 0, A > 0"""
    W = np.minimum(n, 500).astype(float)
    fits = []
    for TL in TL_GRID:
        X = np.column_stack([np.ones_like(T), np.exp((T - 80.0) / TL)])
        c, *_ = np.linalg.lstsq(X * np.sqrt(W)[:, None], P * np.sqrt(W), rcond=None)
        rms = math.sqrt(float(np.sum(W * (X @ c - P) ** 2) / W.sum()))
        fits.append((float(TL), float(c[0]), float(c[1]), rms))
    best = min(fits, key=lambda f: f[3])
    ok = [f for f in fits if f[3] <= FIT_TOL * best[3] and f[1] >= 0 and f[2] > 0]
    return best, ok


FITS = {}
print(f'\nper-rail fits, rail = F + A e^((T-80)/T_L) [fitted]; acceptable = rms within {FIT_TOL}x the best, F >= 0 '
      f'(F = the temperature-independent part: the idle clock tree, D below)')
for c in CARDS[:3]:
    T, n, M = BINS[c]
    for j, r in enumerate(RAILS):
        best, ok = fit_rail(T, n, M[:, 1 + j])
        FITS[(c, r)] = ok
        print(f'  {c:14s} {r:6s}: best T_L {best[0]:.0f} C, F {best[1]:.2f}, A80 {best[2]:.2f} W, rms {best[3]*1e3:.0f} mW; '
              f'acceptable T_L {ok[0][0]:.0f}-{ok[-1][0]:.0f} C, F {min(f[1] for f in ok):.2f}-{max(f[1] for f in ok):.2f} W, '
              f'A80 {min(f[2] for f in ok):.2f}-{max(f[2] for f in ok):.2f} W ({len(ok)} fits)')
OUT['rail_fits'] = {f'{c}|{r}': {'TL': [ok[0][0], ok[-1][0]], 'F': [min(f[1] for f in ok), max(f[1] for f in ok)]}
                    for (c, r), ok in FITS.items()}


def at(bins, Tq, j):
    """a rail's value at Tq by a straight line through the bins within 3 C (all bins with >= 10 samples)"""
    T, n, M = bins
    m = np.abs(T - Tq) <= 3
    return float(np.polyval(np.polyfit(T[m], M[m, j], 1), Tq)), float(np.polyfit(T[m], M[m, j], 1)[0])


# aifoundry2 at 62-68 C, 21 September (cold1, cold2), the anchors' reference
_cold = {}
for s, (T, n, M) in H21.items():
    for t, k, m in zip(T, n, M):
        _cold.setdefault(t, []).append((k, m))
Tc = np.array(sorted(_cold), dtype=float)
Mc = np.array([np.average([m for k, m in _cold[t]], axis=0, weights=[k for k, m in _cold[t]]) for t in Tc])
A2COLD = (Tc, np.array([sum(k for k, m in _cold[t]) for t in Tc]), Mc)
print('\naifoundry2 on 21 Sep (cold1, cold2), idle at 600 MHz [measured]: ' + '; '.join(
    f'{t:.0f} C minion {m[1]:.3f} SRAM {m[2]:.3f} NoC {m[3]:.3f} W' for t, m in zip(Tc, Mc)))

# ======================================================================================================================
hdr('C. The anchors: how much of each rail the clock can remove, and how leakage falls with voltage')
# (i) aifoundry2's idle at 800 MHz / 0.618 V against 600 MHz / 0.518 V, both from a cool start at 63-68 C
#     (docs/reports/data/2026-09-21-horace-aifoundry2/vf.json, tools/ettelem/build_vf.py: idle800 = 10 samples at
#     64-65 C after a zeros run while the clock stayed at 800; idle600 = 122 samples at 63-68 C, 0.5-2.5 s after runs).
VF = json.load(open(os.path.join(DATA, '2026-09-21-horace-aifoundry2', 'vf.json')))
OP = json.load(open(os.path.join(DATA, '2026-09-22-dvfs-aifoundry2', 'dvfs.json')))['operating_points']
V600, V800 = [p['volts'] for p in OP if p['mhz'] == 600][0], [p['volts'] for p in OP if p['mhz'] == 800][0]
LAWS = {'aifoundry2': (12.24, 23.71, 36.0), 'aifoundry3': (15.45, 21.89, 30.0), 'aifoundry1-c1': (18.45, 30.50, 30.0)}
law_a2 = lambda T: LAWS['aifoundry2'][0] + LAWS['aifoundry2'][1] * math.exp((T - 80.0) / LAWS['aifoundry2'][2])
d800_raw = VF['idle800'] - VF['idle600']
d800_law = VF['idle800'] - law_a2(64.5)
A1_C, A1_TOL = 0.5 * (d800_raw + d800_law), 0.5 * abs(d800_law - d800_raw) + 0.5
# the SRAM rail's set-point at 800 MHz: E51 (docs/reports/data/2026-09-28-dvfs2-aifoundry2/(validation/)raw/p*/tel-*,
# the same governor's 800 and 600 MHz points on aifoundry2), median on-die mV per minion clock [measured]
_e51 = collections.defaultdict(list)
_E51D = os.path.join(DATA, '2026-09-28-dvfs2-aifoundry2')
for _f in (sorted(glob.glob(os.path.join(_E51D, 'raw', 'p*', 'tel-*.jsonl.gz'))) +
           sorted(glob.glob(os.path.join(_E51D, 'validation', 'raw', 'p*', 'tel-*.jsonl.gz')))):
    for _s in jsonl(_f):
        _dm, _mz = _s.get('die_mv') or {}, (_s.get('mhz') or {}).get('minion')
        if _mz in (600, 800) and _dm.get('sram') is not None:
            _e51[_mz].append((_dm['minion'], _dm['sram']))
E51V = {m: np.median(np.array(v, dtype=float), axis=0) / 1000 for m, v in _e51.items()}
VS600, VS800 = round(float(E51V[600][1]), 3), round(float(E51V[800][1]), 3)
print(f'(i) aifoundry2 idle: {VF["idle800"]} W at 800 MHz / {V800} V (die {VF["die_c"]["idle800"]} C) against '
      f'{VF["idle600"]} W at 600 MHz / {V600} V (die {VF["die_c"]["idle600"]} C) [measured]; against the idle law at '
      f'64.5 C ({law_a2(64.5):.2f} W) the step is {d800_law:.2f} W, raw {d800_raw:.2f} W: anchor {A1_C:.2f} +- '
      f'{A1_TOL:.2f} W at the board')
print(f'    the same governor points in E51 (aifoundry2, 28 Sep), median on die: minion {E51V[800][0]*1e3:.0f} / '
      f'{E51V[600][0]*1e3:.0f} mV, SRAM {VS800*1e3:.0f} / {VS600*1e3:.0f} mV at 800 / 600 MHz ({len(_e51[800])} and '
      f'{len(_e51[600])} samples) [measured]: the SRAM rail steps too, and its step is part of the anchor')
Pm645, _ = at(A2COLD, 64.5, 1)
Pm62, sm62 = at(A2COLD, 62.0, 1)
Pn62, _ = at(A2COLD, 62.0, 3)
Ps62, ss62 = at(A2COLD, 62.0, 2)
Ps645, _ = at(A2COLD, 64.5, 2)
# (ii) card 0 at 300 MHz / 0.398 V against aifoundry2 at 600 MHz / 0.519 V, both at a 62 C die
Tc0, nc0, Mc0 = BINS['aifoundry1-c0']
k62 = int(np.where(Tc0 == 62)[0][0])
c0m, c0s, c0n = Mc0[k62, 1], Mc0[k62, 2], Mc0[k62, 3]
c0_slope = [float(np.polyfit(Tc0, Mc0[:, j], 1, w=np.sqrt(nc0))[0]) for j in (1, 2, 3)]
CORNER = c0n / Pn62
A2_R = c0m / (Pm62 * CORNER)
A2_TOL = 0.10
print(f'(ii) at a 62 C die: card 0 (1.4.1, 300 MHz, minion {BOOT["aifoundry1-c0"]["vm"]} V, SRAM '
      f'{BOOT["aifoundry1-c0"]["vs"]} V) minion {c0m:.3f} W, SRAM {c0s:.3f}, NoC {c0n:.3f} W; aifoundry2 (600 MHz, '
      f'0.519 V) minion {Pm62:.3f} W, SRAM {Ps62:.3f}, NoC {Pn62:.3f} W [measured]')
print(f'     the NoC rails, same voltage and clock on both, agree to {CORNER:.3f}: the two chips leak alike; minion ratio '
      f'corrected for it: {A2_R:.3f} +- {A2_TOL*100:.0f} % (the anchor)')
# the NoC rail as a proxy for a chip's leakage: the other cards at a 67 C die (E44), minion ratio against NoC ratio
T2, n2, M2 = BINS['aifoundry2']
for c in ('aifoundry3', 'aifoundry1-c1'):
    Tx, nx, Mx = BINS[c]
    i2, ix = int(np.where(T2 == 67)[0][0]), int(np.where(Tx == 67)[0][0])
    print(f'     check at 67 C, {c} over aifoundry2: NoC rail x{Mx[ix, 3]/M2[i2, 3]:.3f}, minion rail x{Mx[ix, 1]/M2[i2, 1]:.3f} '
          f'at {BOOT[c]["vm"]*1e3:.0f} against {BOOT["aifoundry2"]["vm"]*1e3:.0f} mV [measured]')
print(f'     card 0\'s own temperature slopes at 60-64 C: minion {c0_slope[0]:.3f}, SRAM {c0_slope[1]:.4f}, NoC '
      f'{c0_slope[2]:.3f} W/C; aifoundry2 at 62 C: minion {sm62:.3f}, SRAM {ss62:.4f} W/C [measured]')

# ---- the clock tree, shared: one design, one clock ------------------------------------------------------------------
# A rail's temperature-independent part (the idle clock tree, D) is C V^2 f, a property of the design at its clock and
# voltage.  The three cards run one design at 600 MHz, so their minion clock trees differ only by V^2 and their NoC
# clock trees (400 MHz, 484-486 mV) not at all.  The draws take D from the range that every card's own fit allows
# (section B), and each card's leakage law is then refitted with that D held fixed (the best T_L and A by least
# squares).  aifoundry2's own fit alone leaves its minion D anywhere in 0-4.7 W, because its idle data span only
# 67-84 C; aifoundry3's 54-85 C pin the shared value.  The SRAM rails are not shared: aifoundry1 card 1's has about 1 W
# more temperature-independent power than aifoundry3's at nearly the same voltage, which no clock tree explains, so each
# card keeps its own SRAM fits.
VREF = {'minion': 0.518, 'noc': 0.484}
VKEY = {'minion': 'vm', 'sram': 'vs', 'noc': 'vn'}
DGRID = np.round(np.arange(0.0, 6.0001, 0.01), 2)


def fit_fixed(T, n, P, F):
    """the best (T_L, A, rms) of rail = F + A exp((T-80)/T_L) with F held fixed"""
    W = np.minimum(n, 500).astype(float)
    best = None
    for TL in TL_GRID:
        x = np.exp((T - 80.0) / TL)
        A = float(np.sum(W * x * (P - F)) / np.sum(W * x * x))
        rms = math.sqrt(float(np.sum(W * (F + A * x - P) ** 2) / W.sum()))
        if best is None or rms < best[2]:
            best = (float(TL), A, rms)
    return best


LOOK, BESTRMS, SHARED, SHGRID = {}, {}, {}, {}
for r in ('minion', 'noc'):
    j = 1 + RAILS.index(r)
    okm = np.ones(len(DGRID), dtype=bool)
    for c in CARDS[:3]:
        T, n, M = BINS[c]
        LOOK[(c, r)] = np.array([fit_fixed(T, n, M[:, j], F) for F in DGRID])
        BESTRMS[(c, r)] = fit_rail(T, n, M[:, j])[0][3]
        Dc = DGRID * (BOOT[c][VKEY[r]] / VREF[r]) ** 2
        k = np.clip(np.rint(Dc / 0.01).astype(int), 0, len(DGRID) - 1)
        okm &= LOOK[(c, r)][k, 2] <= FIT_TOL * BESTRMS[(c, r)]
    assert okm.any(), r
    SHGRID[r] = DGRID[okm]
    SHARED[r] = (float(SHGRID[r].min()), float(SHGRID[r].max()))
    print(f'shared {r} clock tree' + (' at 600 MHz' if r == 'minion' else ' (NoC at 400 MHz)') +
          f' and {VREF[r]*1e3:.0f} mV: the values at which every card\'s refit stays within {FIT_TOL}x its best rms: '
          f'{SHARED[r][0]:.2f}-{SHARED[r][1]:.2f} W ({okm.sum()} grid values of 0.01 W) [fitted]')
OUT['shared_clock_tree_W'] = SHARED

# ---- the Monte Carlo draws -------------------------------------------------------------------------------------------
NC = 80 * N                                 # about 2-3 % of candidates pass every anchor
D0 = {r: SHGRID[r][rng.integers(0, len(SHGRID[r]), NC)] + U(-0.005, 0.005, NC) for r in ('minion', 'noc')}
kap_m = U(0.5, 8.0, NC)                     # ASSUMED prior, per volt; the anchors select
kap_s = U(1.4, 10.0, NC)                    # ASSUMED prior: N7 DIBL-only (1.4, outside [O11]) to a strong 10; anchor (i)
#                                             selects, through the SRAM rail's recorded 704 -> 830 mV step at 800 MHz
# regulator delivery loss per rail: the unmetered fit's coefficients (19-observability-and-the-unmetered.md, E46;
# docs/reports/sources/limits-of-observability.data.json power.fit; card 0 not fitted, aifoundry2's used); +-0.03
# (minion, SRAM) and +-0.04 (NoC, its standard error 0.02) for the rails' scale (ibid.: 1 % of rail scale moves a
# coefficient ~1.2 points).  Revised 30 Sep (review): the NoC rail had the minion's coefficient and the SRAM a shared
# ASSUMED 0.03-0.20.  Card 1's SRAM coefficient, 0.54, is the fit's and is not explained.
ETA_M = {'aifoundry2': 0.188, 'aifoundry3': 0.181, 'aifoundry1-c1': 0.102, 'aifoundry1-c0': 0.188}
ETA_S = {'aifoundry2': 0.034, 'aifoundry3': 0.043, 'aifoundry1-c1': 0.540, 'aifoundry1-c0': 0.034}
ETA_N = {'aifoundry2': 0.291, 'aifoundry3': 0.294, 'aifoundry1-c1': 0.205, 'aifoundry1-c0': 0.291}
eta_m = {c: U(v - 0.03, v + 0.03, NC) for c, v in ETA_M.items()}
eta_s = {c: U(max(v - 0.03, 0.0), v + 0.03, NC) for c, v in ETA_S.items()}
eta_n = {c: U(v - 0.04, v + 0.04, NC) for c, v in ETA_N.items()}


def draw_fit(c, r, n):
    ok = FITS[(c, r)]
    idx = rng.integers(0, len(ok), n)
    a = np.array(ok)
    return a[idx, 0], a[idx, 1], a[idx, 2]   # TL, F (= D), A80


PAR = {}
fit_ok = np.ones(NC, dtype=bool)
for c in CARDS[:3]:
    for r in RAILS:
        if r == 'sram':
            PAR[(c, r)] = draw_fit(c, r, NC)
            continue
        D = D0[r] * (BOOT[c][VKEY[r]] / VREF[r]) ** 2
        k = np.clip(np.rint(D / 0.01).astype(int), 0, len(DGRID) - 1)
        row = LOOK[(c, r)][k]
        fit_ok &= row[:, 2] <= FIT_TOL * BESTRMS[(c, r)]
        PAR[(c, r)] = (row[:, 0], DGRID[k], row[:, 1])
D_a2 = PAR[('aifoundry2', 'minion')][1]
G = lambda V, V0, k: (V / V0) * np.exp(k * (V - V0))
r800 = (800 / 600) * (V800 / V600) ** 2
# the SRAM rail's part of the step: its clock tree x (800/600)(830/704)^2 and its leakage x G(830 mV) (was an ASSUMED
# 0-0.7 W "not recorded" before 30 Sep; E51 records the voltage)
Ds_a2 = PAR[('aifoundry2', 'sram')][1]
r800s = (800 / 600) * (VS800 / VS600) ** 2
S800 = (1 + eta_s['aifoundry2']) * (Ds_a2 * (r800s - 1) + np.clip(Ps645 - Ds_a2, 0, None) * (G(VS800, VS600, kap_s) - 1))
dP800 = (1 + eta_m['aifoundry2']) * (D_a2 * (r800 - 1) + (Pm645 - D_a2) * (G(V800, V600, kap_m) - 1)) + S800
s_c0 = (300 / 600) * (BOOT['aifoundry1-c0']['vm'] / 0.519) ** 2
Rmod = (D_a2 * s_c0 + (Pm62 - D_a2) * G(BOOT['aifoundry1-c0']['vm'], 0.519, kap_m)) / Pm62
acc1 = np.abs(dP800 - A1_C) <= A1_TOL
acc2 = np.abs(Rmod - A2_R) <= A2_TOL * A2_R
acc = np.nonzero(acc1 & acc2 & fit_ok)[0]
print(f'\nanchors: {acc1.mean()*100:.0f} % of prior draws pass (i), {acc2.mean()*100:.0f} % pass (ii), '
      f'{fit_ok.mean()*100:.0f} % keep every refitted rail within {FIT_TOL}x its best rms, {len(acc)/NC*100:.0f} % pass '
      f'all; the first {N} are kept')
assert len(acc) >= N, 'not enough accepted draws: raise the candidate pool'
NACC = len(acc)
acc = acc[:N]
kap_m, kap_s, S800 = kap_m[acc], kap_s[acc], S800[acc]
D0 = {r: v[acc] for r, v in D0.items()}
eta_m = {c: v[acc] for c, v in eta_m.items()}
eta_s = {c: v[acc] for c, v in eta_s.items()}
eta_n = {c: v[acc] for c, v in eta_n.items()}
for k in PAR:
    PAR[k] = tuple(v[acc] for v in PAR[k])
D_a2 = D_a2[acc]
Gm40 = G(FLOOR['minion'], V600, kap_m)
print(f'kappa_m (minion leakage, per volt) [fitted]: {pct(kap_m)}  (prior 0.5-8; N7 DIBL-only 1.4 [outside, O11])')
print(f'minion leakage at 398 mV over 518 mV, G = (V/V0) e^(kappa (V-V0)) [fitted]: {pct(Gm40)};  DIBL-only [outside]: '
      f'{float(G(0.398, 0.518, 1.42)):.2f}')
print(f'minion leakage at 618 mV over 518 mV [fitted]: {pct(G(V800, V600, kap_m))}')
print(f'minion clock tree at 600 MHz / 518 mV [fitted]: {pct(D0["minion"])} W (correlation with kappa '
      f'{np.corrcoef(D_a2, kap_m)[0, 1]:+.2f}); NoC clock tree at 400 MHz: {pct(D0["noc"])} W')
for c in CARDS[:3]:
    print(f'   {c:14s} leakage T_L, minion {pct(PAR[(c, "minion")][0])} C, SRAM {pct(PAR[(c, "sram")][0])} C, NoC '
          f'{pct(PAR[(c, "noc")][0])} C; SRAM clock tree {pct(PAR[(c, "sram")][1])} W [fitted]')
_km = float(np.median(kap_m))
for c in ('aifoundry3', 'aifoundry1-c1'):
    Tx, nx, Mx = BINS[c]
    i2, ix = int(np.where(T2 == 67)[0][0]), int(np.where(Tx == 67)[0][0])
    print(f'check (not an anchor): at 67 C, {c}\'s minion rail over aifoundry2\'s, corrected to 518 mV with the fitted '
          f'kappa: x{Mx[ix, 1]/M2[i2, 1]/float(G(BOOT[c]["vm"], BOOT["aifoundry2"]["vm"], _km)):.3f}, against its NoC rail\'s '
          f'x{Mx[ix, 3]/M2[i2, 3]:.3f}: the NoC rail tracks a chip\'s leakage [measured/model]')
print(f'kappa_s (SRAM leakage, per volt) [fitted, through anchor (i)]: {pct(kap_s)} (prior 1.4-10); the SRAM rail\'s part '
      f'of the 800 MHz step {pct(S800)} W (of {A1_C:.2f} +- {A1_TOL:.2f})')
print(f'SRAM leakage at 660 mV over 704 mV [fitted]: {pct(G(0.660, 0.704, kap_s))}')
print(f'anchor tension: (i) alone passes {acc1.mean()*100:.1f} % of the prior, (ii) alone {acc2.mean()*100:.1f} %, both '
      f'{np.mean(acc1 & acc2)*100:.1f} %; card 0\'s 1.4.1 low-power state may not be a pure change of voltage and clock '
      f'[inference]')
# checks the anchors did not use
c0_s_pred = (PAR[('aifoundry2', 'sram')][1] * 0.5 * (0.660 / 0.704) ** 2 + (Ps62 - PAR[('aifoundry2', 'sram')][1]).clip(0)
             * G(0.660, 0.704, kap_s)) / Ps62
_a3s62 = BINS['aifoundry3'][2][np.where(BINS['aifoundry3'][0] == 62)[0][0], 2]
print(f'check (not an anchor): card 0\'s SRAM rail over aifoundry2\'s at 62 C, model {pct(c0_s_pred)}, measured '
      f'{c0s/Ps62:.2f}; the SRAM rails do not follow the NoC rails between cards (aifoundry3\'s is {_a3s62/Ps62:.2f}x '
      f'aifoundry2\'s at 62 C), so the model keeps the wider range [measured/model]')
_Dc0m = np.minimum(D0['minion'] * 0.5 * (BOOT['aifoundry1-c0']['vm'] / VREF['minion']) ** 2, 0.8 * c0m)
print(f'check (not an anchor): card 0\'s minion temperature slope at 62 C, model (its leakage over aifoundry2\'s T_L) '
      f'{pct((c0m - _Dc0m) / PAR[("aifoundry2", "minion")][0])} W/C, measured {c0_slope[0]:.3f}; a larger T_L at low voltage '
      f'would make the model\'s slopes at the floor a little high, i.e. pessimistic [model/measured]')
OUT['anchors'] = {'i_W': [A1_C, A1_TOL], 'ii_ratio': [A2_R, A2_TOL], 'corner': CORNER, 'kappa_m': p3(kap_m),
                  'G_minion_398mV': p3(Gm40), 'D_minion_W': p3(D0['minion']), 'D_noc_W': p3(D0['noc']),
                  'G_sram_660mV': p3(G(0.660, 0.704, kap_s)), 'kappa_s': p3(kap_s), 'S800_W': p3(S800),
                  'sram_mV_800_600': [VS800 * 1e3, VS600 * 1e3], 'accept_frac': NACC / NC}

# ---- per-card parameters for the rest -------------------------------------------------------------------------------
# card 0: its own rails at 62 C, aifoundry2's T_L (the two chips match by the NoC rail); its clock trees are the shared
# ones at its clock and voltage (minion and SRAM at 300 MHz; the SRAM's is aifoundry2's).  Its board law is
# nohs_calc.py's: 17.97 W at 62 C, slope 0.207 W/C, T_L 25-36 C.
TLc0 = U(25.0, 36.0, N)
P_OFF = {'aifoundry2': (5.0, 8.2), 'aifoundry3': (4.5, 7.5), 'aifoundry1-c1': (5.5, 9.0), 'aifoundry1-c0': (3.8, 6.0)}
F_SLOPE = (0.80, 0.95)
IDLE_PT = {'aifoundry2': 73.0, 'aifoundry3': 56.0, 'aifoundry1-c1': 60.0, 'aifoundry1-c0': 62.0}
C0_P62, C0_S62 = 17.97, 0.207
PC = {}   # per card and rail: (D, A80, T_L), arrays of length N
for c in CARDS[:3]:
    PC[c] = {r: (PAR[(c, r)][1], PAR[(c, r)][2], PAR[(c, r)][0]) for r in RAILS}
dc0 = {}
b0 = BOOT['aifoundry1-c0']
for r, pmeas, Dc0 in (('minion', c0m, D0['minion'] * 0.5 * (b0['vm'] / VREF['minion']) ** 2),
                      ('sram', c0s, PAR[('aifoundry2', 'sram')][1] * 0.5 * (b0['vs'] / BOOT['aifoundry2']['vs']) ** 2),
                      ('noc', c0n, D0['noc'] * (b0['vn'] / VREF['noc']) ** 2)):
    TLa = PAR[('aifoundry2', r)][0]
    Dc0 = np.minimum(Dc0, 0.8 * pmeas)
    dc0[r] = (Dc0, (pmeas - Dc0) * np.exp((80.0 - 62.0) / TLa), TLa)
PC['aifoundry1-c0'] = dc0


def board_law(c, T):
    """measured idle board law at the card's own operating point (nohs_calc.py section C); T: (N, k) or scalar"""
    if c == 'aifoundry1-c0':
        A = C0_S62 * TLc0[:, None]
        return (C0_P62 - A) + A * np.exp((T - 62.0) / TLc0[:, None])
    Pf, A, TL = LAWS[c]
    return Pf + A * np.exp((T - 80.0) / TL)


# nohs_calc.py section D's SoC split, per draw
Poff = {c: U(*P_OFF[c], N) for c in CARDS}
fs = {c: U(*F_SLOPE, N) for c in CARDS}


def soc_base(c, T):
    """nohs_calc.py soc_power: board(T0) - Poff + fs (board(T) - board(T0))"""
    T0 = IDLE_PT[c]
    b0 = board_law(c, np.full((N, 1), T0))
    return b0 - Poff[c][:, None] + fs[c][:, None] * (board_law(c, T) - b0)


# ======================================================================================================================
hdr('D. The decomposition of idle and loaded power, per card, at its own operating point')
POLICIES = ['boot', 'floor', 'floor+NoC']


def volts(c, f, pol):
    b = BOOT[c]
    if c == 'aifoundry1-c0':
        vm, vs = (b['vm'], b['vs']) if f <= 300 else (np.nan, np.nan)
    elif pol == 'boot' or f >= 600:
        vm, vs = b['vm'], b['vs']
    elif f <= 300:
        vm, vs = FLOOR['minion'], FLOOR['sram']
    else:
        t = (f - 300.0) / 300.0
        vm, vs = FLOOR['minion'] + t * (b['vm'] - FLOOR['minion']), FLOOR['sram'] + t * (b['vs'] - FLOOR['sram'])
    fn, vn = (200.0, FLOOR['noc']) if pol == 'floor+NoC' else (400.0, b['vn'])
    return vm, vs, fn, vn


def removed(c, f, pol, T):
    """on-die rail power removed (positive) or added (negative) against the card's own operating point, and its regulator
    loss at the board; T: (N, k) array"""
    b = BOOT[c]
    vm, vs, fn, vn = volts(c, f, pol)
    f0 = b['f0']
    out, loss = 0.0, 0.0
    for r, v, v0, fr, kap, eta in (('minion', vm, b['vm'], f / f0, kap_m, eta_m[c]),
                                   ('sram', vs, b['vs'], f / f0, kap_s, eta_s[c]),
                                   ('noc', vn, b['vn'], fn / 400.0, kap_m, eta_n[c])):
        D, A80, TL = PC[c][r]
        s = fr * (v / v0) ** 2
        g = G(v, v0, kap)
        dr = (D * (1 - s))[:, None] + (A80[:, None] * np.exp((T - 80.0) / TL[:, None])) * (1 - g)[:, None]
        out = out + dr
        loss = loss + dr * eta[:, None]
    return out, loss


P600 = U(0.60, 0.76, N)          # W per shire on the die, fp32 randn TensorFMA at 600 MHz / 0.517 V (imaging_calc.py A;
#                                  revised 30 Sep from U(0.55, 0.75), which sat 8-10 % below aifoundry2's 16- and
#                                  32-shire runs: 12.5-13.9 W and +27.1 W at the board)
UDIE = U(0.83, 0.88, N)          # on-die share of a workload's added board watts (19-observability...md:64-66)
LOADS = {'idle': 0, 'pattern (16 shires)': 16, 'whole chip (32 shires)': 32}


def load_die(c, f, pol, nsh):
    vm = volts(c, f, pol)[0]
    return nsh * P600 * (f / 600.0) * (vm / 0.517) ** 2


def board(c, f, pol, T, nsh=0):
    rm, loss = removed(c, f, pol, T)
    return board_law(c, T) - rm - loss + (load_die(c, f, pol, nsh) / UDIE)[:, None]


def soc(c, f, pol, T, nsh=0):
    rm, _ = removed(c, f, pol, T)
    return soc_base(c, T) - rm + load_die(c, f, pol, nsh)[:, None]


def soc_off(c, f, pol, T, nsh=0):
    """(SoC power, off-die power that heats the board) at the point: the off-die power is the card's own idle point's
    (nohs_calc.py P_OFF, as section E of nohs_calc.py and F2 here draw it), less the regulator loss the point removes,
    plus the off-die share of a workload"""
    rm, loss = removed(c, f, pol, T)
    ld = load_die(c, f, pol, nsh)[:, None]
    return soc_base(c, T) - rm + ld, Poff[c][:, None] - loss + ld * (1.0 / UDIE[:, None] - 1.0)


def parts(c, T):
    """(fixed, leakage m+s, clock tree m+s, regulator loss of m+s) at the card's own point, board watts; T scalar"""
    Tq = np.full((N, 1), float(T))
    tot = board_law(c, Tq)[:, 0]
    leak = sum(PC[c][r][1] * np.exp((T - 80.0) / PC[c][r][2]) for r in ('minion', 'sram'))
    dyn = PC[c]['minion'][0] + PC[c]['sram'][0]
    reg = eta_m[c] * (PC[c]['minion'][0] + PC[c]['minion'][1] * np.exp((T - 80.0) / PC[c]['minion'][2])) + \
        eta_s[c] * (PC[c]['sram'][0] + PC[c]['sram'][1] * np.exp((T - 80.0) / PC[c]['sram'][2]))
    return tot, tot - leak - dyn - reg, leak, dyn, reg


print('Board power at the card\'s own point = (a) the part no minion clock or voltage touches (off the metered rails: '
      'SP, PCIe, memory shires and DRAM, IO, Maxion, board and regulator losses; plus the NoC rail at its own clock) + '
      '(b) minion and SRAM leakage (+ its regulator loss) + (c) the minion and SRAM clock tree at idle (+ loss).')
print('(a) is the measured law less (b) and (c); (b) and (c) come from the per-rail fits (section B) [fitted/model]; the '
      'regulator loss of (b) and (c) is counted with them.')
DECOMP = {}
for c in CARDS:
    lab = f'{c} ({BOOT[c]["f0"]} MHz, {BOOT[c]["vm"]*1e3:.0f}/{BOOT[c]["vs"]*1e3:.0f} mV)'
    for T in sorted({25.0, 40.0, 60.0, IDLE_PT[c]}):
        tot, fixed, leak, dyn, reg = parts(c, T)
        lk = leak + reg * leak / (leak + dyn)
        dy = dyn + reg * dyn / (leak + dyn)
        DECOMP[f'{c}|{T:.0f}'] = {'board': p3(tot), 'fixed': p3(fixed), 'leak': p3(lk), 'clock_tree': p3(dy)}
        print(f'  {lab:32s} die {T:4.0f} C: board {np.median(tot):5.1f} W = (a) {pct(fixed)} + (b) {pct(lk)} + (c) '
              f'{pct(dy)} W; (c) is {pct(100*dy/tot, fmt="{:.1f}")} %  [model]')
OUT['decomposition'] = DECOMP
DV = json.load(open(os.path.join(DATA, '2026-09-22-dvfs-aifoundry2', 'dvfs.json')))
_busy, _idle = DV['busy_randn_80c'], DV['idle_80c']
tot80, fx80, lk80, dy80, rg80 = parts('aifoundry2', 80.0)
_sw = _busy - _idle
print(f'loaded, aifoundry2 at 80 C, fp32 randn on 1,024 minions: {_busy:.1f} W at the board [measured, dvfs.json '
      f'busy_randn_80c] = (a) {np.median(fx80):.1f} + (b) {np.median(lk80 + rg80 * lk80 / (lk80 + dy80)):.1f} + (c) '
      f'{np.median(dy80 + rg80 * dy80 / (lk80 + dy80)):.1f} + switching {_sw:.1f} W [measured: busy - idle {_idle:.1f}] '
      f'(medians; (a)-(c) model): the switching is {_sw/_busy*100:.0f} %, the clock tree {np.median(dy80)/_busy*100:.0f} %; '
      f'at 100 MHz and the floor voltages the switching would be {_sw*(100/600)*(0.398/V600)**2:.1f} W [model]')
# Esperanto's own measured idle breakdown (outside O3: D. Ditzel, RISC-V Summit, 13 Dec 2022, slide 14, read off the
# chart): card 20.0 W, minion 5.8, NoC 1.6, SRAM 1.7 W; its clock and die temperature are not given.
_Tg = np.arange(25.0, 80.01, 0.5)
_mr = np.median(PC['aifoundry2']['minion'][0][:, None] + PC['aifoundry2']['minion'][1][:, None] *
                np.exp((_Tg[None, :] - 80.0) / PC['aifoundry2']['minion'][2][:, None]), axis=0)
_Te = float(np.interp(5.8, _mr, _Tg))
_nr = np.median(PC['aifoundry2']['noc'][0] + PC['aifoundry2']['noc'][1] * np.exp((_Te - 80.0) / PC['aifoundry2']['noc'][2]))
_sr = np.median(PC['aifoundry2']['sram'][0] + PC['aifoundry2']['sram'][1] * np.exp((_Te - 80.0) / PC['aifoundry2']['sram'][2]))
print(f'check against Esperanto\'s measured idle (outside O3, RISC-V Summit 2022: card 20.0 W, minion 5.8, NoC 1.6, SRAM '
      f'1.7 W; clock and temperature not given): aifoundry2\'s model reaches a 5.8 W minion rail at a {_Te:.0f} C die, where '
      f'its NoC rail is {_nr:.2f} W, its SRAM rail {_sr:.2f} W (Esperanto: 1.7) and the card {law_a2(_Te):.1f} W '
      f'[model/outside]; {_Te:.0f} C lies below every measured bin of aifoundry2 (62-84 C), so these are its fitted laws '
      f'extrapolated')
# a workload: switching on the die scales as f V^2 (13-why-low-power.md: 800 against 600 MHz, 2.0-2.1x measured where
# V^2 f predicts 1.91x)
print(f'loaded: fp32 randn TensorFMA adds {pct(P600*32/UDIE)} W at the board on 32 shires at 600 MHz (measured +27.1 '
      f'on aifoundry2, 10-data-dependent-power.md) [measured/assumed range]; x f V^2: at 100 MHz and 398 mV '
      f'{pct(P600*32/UDIE*(100/600)*(0.398/0.517)**2)} W, at 10 MHz {pct(P600*32/UDIE*(10/600)*(0.398/0.517)**2)} W [model]')

# ======================================================================================================================
hdr('E. Operating points: idle board power at 25 / 40 / 60 C die, its slope, and loaded power (median [5-95])')
TGRID = np.arange(15.0, 125.01, 0.1)       # a root above 125 C is no operating point (and the laws are far from data)
TQ = [25.0, 40.0, 60.0]


def allowed(c, f, pol):
    if not SETTABLE[f]:
        return 'not settable (no PLL mode)'
    if c == 'aifoundry1-c0':
        return 'off-limits (card 0 overheats); its own 1.4.1 idle point' if f == 300 else 'off-limits (card 0 overheats)'
    if pol != 'boot' and c == 'aifoundry1-c1':
        return 'forbidden by the lab rule (0.18.0: no range check, NoC sets written to flash)'
    if c == 'aifoundry2' and f != 600:
        return 'settable; the governor restores 600 MHz unless the owner changes it'
    return 'settable'


OPS = []
for c in CARDS:
    pols = ['floor', 'floor+NoC'] if c == 'aifoundry1-c0' else POLICIES
    for pol in pols:
        for f in CLOCKS:
            if c == 'aifoundry1-c0' and f > 300:
                continue
            if pol != 'boot' and f == 600 and c != 'aifoundry1-c0' and pol == 'floor':
                continue   # at 600 MHz the floor policy is the boot point
            OPS.append((c, f, pol))
EROWS = {}
print(f'{"card":14s} {"clock":>6s} {"policy":10s} {"minion/SRAM mV":>15s} {"idle board W, 25 / 40 / 60 C [5-95 at 60]":>40s} '
      f'{"dP/dT board W/C at 60":>22s} {"+16 shires at 60 C":>19s} {"+32 shires":>12s}  status')
for c, f, pol in OPS:
    vm, vs, fn, vn = volts(c, f, pol)
    Tq = np.array(TQ)[None, :].repeat(N, 0)
    P = board(c, f, pol, Tq)
    dP = (board(c, f, pol, Tq + 0.05) - board(c, f, pol, Tq - 0.05)) / 0.1
    dS = (soc(c, f, pol, Tq + 0.05) - soc(c, f, pol, Tq - 0.05)) / 0.1
    P16 = board(c, f, pol, Tq, 16)[:, 2]
    P32 = board(c, f, pol, Tq, 32)[:, 2]
    EROWS[f'{c}|{f}|{pol}'] = {'mV': [vm * 1e3, vs * 1e3], 'noc': [fn, vn * 1e3],
                               'board_W': {str(int(t)): p3(P[:, i]) for i, t in enumerate(TQ)},
                               'dPdT_board': {str(int(t)): p3(dP[:, i]) for i, t in enumerate(TQ)},
                               'dPdT_soc': {str(int(t)): p3(dS[:, i]) for i, t in enumerate(TQ)},
                               'board16_60': p3(P16), 'board32_60': p3(P32), 'status': allowed(c, f, pol)}
    cells = ' / '.join(f'{np.median(P[:, i]):.1f}' for i in range(3))
    rng5 = f'[{np.percentile(P[:, 2], 5):.1f}-{np.percentile(P[:, 2], 95):.1f}]'
    print(f'{c:14s} {f:6d} {pol:10s} {vm*1e3:7.0f}/{vs*1e3:4.0f}{"*" if pol == "floor+NoC" else " "}   '
          f'{cells:>20s} {rng5:>13s}  {np.median(dP[:, 2]):6.3f} (SoC {np.median(dS[:, 2]):.3f})  '
          f'{np.median(P16):7.1f}  {np.median(P32):7.1f}      {allowed(c, f, pol)}')
print('(* NoC at 200 MHz / 400 mV; otherwise 400 MHz at the card\'s own voltage.  [model] throughout; 25 C lies below the '
      'measured range (54-85 C), so it is an extrapolation of the fitted exponentials)')
OUT['operating_points'] = EROWS
# the floor no clock removes
print()
print('What no clock removes (f -> 0, at the card\'s own temperature law) [model]:')
FLOORS = {}
for c in CARDS[:3]:
    for pol in POLICIES:
        Tq = np.array(TQ)[None, :].repeat(N, 0)
        P0 = board(c, 1e-6, pol, Tq)
        P6 = board(c, 600, 'boot', Tq)
        S0 = soc(c, 1e-6, pol, Tq)
        FLOORS[f'{c}|{pol}'] = {'board_W': {str(int(t)): p3(P0[:, i]) for i, t in enumerate(TQ)},
                                'soc_W': {str(int(t)): p3(S0[:, i]) for i, t in enumerate(TQ)},
                                'removed_frac_60': p3(1 - P0[:, 2] / P6[:, 2])}
        print(f'  {c:14s} voltages {pol:10s}: board {pct(P0[:, 0])} W at 25 C, {pct(P0[:, 2])} W at 60 C (the die\'s '
              f'share {pct(S0[:, 2])} W); that is {pct(100*(1-P0[:,2]/P6[:,2]), fmt="{:.0f}")} % below 600 MHz idle')
OUT['floor_no_clock_removes'] = FLOORS

# ======================================================================================================================
hdr('F. Steady state: bare package (still air, fan), heatsink on, IR-window cooler')
TH_STILL, TH_FAN = (4.0, 12.0), (2.0, 7.0)          # nohs_calc.py section B, SoC basis
th = {'still': LU(*TH_STILL, N), 'fan': LU(*TH_FAN, N)}
Ta = {'still': U(22.0, 30.0, N), 'fan': U(22.0, 30.0, N)}
# heatsink on: the card's effective board-basis resistance reproduces its own idle point (nohs_calc.py section C:
# Ta 22-28 C), theta = (T0 - Ta) / P_board(T0)
Ta['heatsink'] = U(22.0, 28.0, N)
th['heatsink'] = {c: (IDLE_PT[c] - Ta['heatsink']) / board_law(c, np.full((N, 1), IDLE_PT[c]))[:, 0] for c in CARDS}
# IR-window liquid cooler on a delidded die (nohs_calc.py G: h 5e3-2e4 W/m2K over the 570 mm2 die) + the die itself
A_DIE = 25.6e-3 * 22.2e-3
th['irwin'] = 1.0 / (LU(5e3, 2e4, N) * A_DIE) + U(0.45e-3, 0.775e-3, N) / (130.0 * A_DIE)
Ta['irwin'] = U(20.0, 30.0, N)                        # ASSUMED coolant temperature
print(f'theta SoC basis [model, nohs_calc.py B]: still {pct(th["still"])}, fan {pct(th["fan"])} C/W; IR-window cooler '
      f'{pct(th["irwin"])} C/W; heatsink (board basis, from each card\'s idle point): ' +
      ', '.join(f'{SHORT[c]} {pct(th["heatsink"][c])}' for c in CARDS))


def settle_from(P, cool, thv):
    """first root of Ta + theta P(T) - T above Ta on TGRID: the stable temperature, NaN if none below 200 C"""
    T = TGRID[None, :]
    g = Ta[cool][:, None] + thv[:, None] * np.maximum(P, 0) - T
    neg = (g <= 0) & (T >= Ta[cool][:, None])
    has = neg.any(axis=1)
    i = np.argmax(neg, axis=1)
    return np.where(has, TGRID[i], np.nan)


RES = {}
COOLS = ['still', 'fan', 'heatsink', 'irwin']
LOADKEYS = [('idle', 0), ('pattern', 16)]
TG = np.repeat(TGRID[None, :], N, 0)
for c, f, pol in OPS:
    for lk, nsh in LOADKEYS:
        Psoc = soc(c, f, pol, TG, nsh)
        Pbrd = board(c, f, pol, TG, nsh)
        r = {}
        for cool in COOLS:
            Te = settle_from(Pbrd if cool == 'heatsink' else Psoc, cool,
                             th['heatsink'][c] if cool == 'heatsink' else th[cool])
            r[cool] = {'p_stable': float(np.isfinite(Te).mean()), 'p_below85': float((Te < 85).mean()),
                       'T_eq': p3(Te) if np.isfinite(Te).any() else None, 'n_stable': int(np.isfinite(Te).sum())}
        m85 = (TGRID >= 25.05) & (TGRID <= 85.0)
        r['theta85_soc'] = p3(np.max((TGRID[m85] - 25.0) / np.maximum(Psoc[:, m85], 1e-9), axis=1))
        r['theta85_board'] = p3(np.max((TGRID[m85] - 25.0) / np.maximum(Pbrd[:, m85], 1e-9), axis=1))
        RES[(c, f, pol, lk)] = r
del TG


def cell(d):
    if d is None:
        return '-'
    s = f'{d["p_below85"]*100:3.0f}%'
    if d['T_eq'] is not None and d['n_stable'] >= 20:
        s += f' {d["T_eq"][1]:3.0f}C'
    elif d['n_stable']:
        s += f' ({d["n_stable"]} st)'
    return s


print('Cells: share of draws that settle below 85 C, then the median settled temperature of those that settle below '
      '125 C ("(n st)" = only n of the draws settle below 125 C).  theta85 = the largest SoC-basis theta that settles at or below 85 C '
      'with Ta 25 C (bare lid: 4-12 still, 2-7 fan) [model]')
for lk, _ in LOADKEYS:
    print(f'-- load: {lk}{" (fp32 randn on 16 shires, the checkerboard or half-die pattern)" if lk == "pattern" else ""}')
    print(f'{"card":14s} {"clock":>6s} {"policy":10s} {"still air":>12s} {"fan":>12s} {"heatsink on":>12s} '
          f'{"theta85 SoC C/W":>18s}')
    for c, f, pol in OPS:
        r = RES[(c, f, pol, lk)]
        print(f'{c:14s} {f:6d} {pol:10s} {cell(r["still"]):>12s} {cell(r["fan"]):>12s} {cell(r["heatsink"]):>12s} '
              f'{pct(r["theta85_soc"]):>18s}{"" if SETTABLE[f] else "   (not settable)"}')
# consistency with nohs_calc.py section D at each card's own point (it drew 600 per card: a2 still 0, fan 1; a3 0, 0;
# c1 0, 0; c0@300 still 0, fan 200 of 600)
print('check against nohs_calc.out section D at the cards\' own points (idle): ' + '; '.join(
    f'{SHORT[c]} still {RES[(c, BOOT[c]["f0"], "floor" if c == "aifoundry1-c0" else "boot", "idle")]["still"]["p_stable"]*100:.1f} %, '
    f'fan {RES[(c, BOOT[c]["f0"], "floor" if c == "aifoundry1-c0" else "boot", "idle")]["fan"]["p_stable"]*100:.1f} %'
    for c in CARDS) + ' settle (nohs: 0, 0.2; 0, 0; 0, 0; 0, 33 %)')
# check the heatsink case against the recorded flip budget (12-heat-management.md: +3.1 W of switching at 82 C in the
# room of 21 Sep, intercept 22.8 C, network 1.467 C/W)
bud = None
_base = LAWS['aifoundry2'][0] + LAWS['aifoundry2'][1] * np.exp((TGRID - 80.0) / LAWS['aifoundry2'][2])
for extra in np.arange(0.0, 8.0, 0.05):
    if not ((22.8 + 1.467 * (_base + extra) - TGRID) <= 0).any():
        bud = extra
        break
print(f'check: the heatsink model\'s aifoundry2 law with 1.467 C/W and 22.8 C holds a sustained switching load of up to '
      f'{bud:.2f} W at the board (recorded flip budget: 3.1 W, 12-heat-management.md) [model/measured]')
print('IR-window cooler, 16-shire pattern: ' + '; '.join(
    f'{SHORT[c]} {f} MHz {pol}: {RES[(c, f, pol, "pattern")]["irwin"]["p_below85"]*100:.0f} % below 85 C, median '
    f'{RES[(c, f, pol, "pattern")]["irwin"]["T_eq"][1]:.0f} C' for c, f, pol in OPS
    if c == 'aifoundry2' and f in (600, 100)) + ' [model]')
OUT['steady'] = {f'{c}|{f}|{pol}|{lk}': v for (c, f, pol, lk), v in RES.items()}

# ======================================================================================================================
hdr('F2. Bare: the transient model\'s network settled, and the window after the host boots')
# nohs_calc.py section E's two-node model and input ranges: the package node (C_J 9-18 J/K) and the board around it
# (C_B 30-80 J/K); junction to board theta_JB LU(1, 3) C/W; lid top to air 1/(h A_lid) + 0.03-0.10 C/W with h 8-15
# (still) or 20-50 (fan) W/m2K; board to air LU(2.5, 8) (still) or LU(0.8, 3) (fan) C/W; a share phi 0.3-1.0 of the
# off-die power heats the board node; ambient 22-30 C.  The off-die power is the card's own idle point's (nohs_calc.py
# P_OFF), less the regulator loss a lower point removes, plus the off-die share of a workload (revised 30 Sep: before,
# the board node kept the idle point's off-die power at every point and load).
# (1) Settled: the network's steady state, T_J = Ta + theta_eff P_SoC(T_J) + Z phi P_off, with theta_eff = R_lid ||
#     (theta_JB + R_BA) and Z = R_BA R_lid / (R_lid + theta_JB + R_BA), the junction's rise per watt into the board.
#     Section F's theta draw (4-12, 2-7 C/W) leaves out the second term; this one has it (added 30 Sep, review).
# (2) The window: the host boots for 30-90 s (ASSUMED, as nohs_calc.py: the boot time is not recorded) with the card
#     idle at its own point, since nothing can set a clock before the driver is up; then 20-60 s to set the low point
#     (ASSUMED, as lc_plan_calc.py F: power management off, the voltages, the clock), still idle at the boot point;
#     then the low point and the load until the die reaches the plan's stops: the software watcher at 75 C on the die,
#     the latching relay at 80 C (on the lid, taken here as the die), and 85 C.  "Look" = the seconds from the low point
#     being set to the stop; 0 = none left.  At the card's own point (600 MHz) nothing needs setting.  Also printed, as
#     before, the seconds to 85 C if the point could be set the instant the host boots ("set at boot").
#     Explicit Euler, 0.25 s steps, up to 30 min.
A_LID = 44.8e-3 ** 2
tr = {'thJB': LU(1.0, 3.0, N), 'CJ': U(9.0, 18.0, N), 'CB': U(30.0, 80.0, N), 'phi': U(0.3, 1.0, N),
      'tb': U(30.0, 90.0, N), 'Ta': U(22.0, 30.0, N),
      'Rlid': {'still': 1.0 / (U(8.0, 15.0, N) * A_LID) + U(0.03, 0.10, N),
               'fan': 1.0 / (U(20.0, 50.0, N) * A_LID) + U(0.03, 0.10, N)},
      'RBA': {'still': LU(2.5, 8.0, N), 'fan': LU(0.8, 3.0, N)}}
tr['tset'] = U(20.0, 60.0, N)          # drawn last, so that the draws above are unchanged
DT, TMAX = 0.25, 1800.0
STOPS = (75.0, 80.0, 85.0)
th_eff = {cool: tr['Rlid'][cool] * (tr['thJB'] + tr['RBA'][cool]) / (tr['Rlid'][cool] + tr['thJB'] + tr['RBA'][cool])
          for cool in ('still', 'fan')}
Zb = {cool: tr['RBA'][cool] * tr['Rlid'][cool] / (tr['Rlid'][cool] + tr['thJB'] + tr['RBA'][cool]) for cool in ('still', 'fan')}

# ---- (1) the network settled ----------------------------------------------------------------------------------------
TG = np.repeat(TGRID[None, :], N, 0)
for c, f, pol in OPS:
    for lk, nsh in LOADKEYS:
        Ps_, Po_ = soc_off(c, f, pol, TG, nsh)
        for cool in ('still', 'fan'):
            g = (tr['Ta'][:, None] + th_eff[cool][:, None] * np.maximum(Ps_, 0) + (Zb[cool] * tr['phi'])[:, None]
                 * np.maximum(Po_, 0) - TG)
            neg = (g <= 0) & (TG >= tr['Ta'][:, None])
            Te = np.where(neg.any(axis=1), TGRID[np.argmax(neg, axis=1)], np.nan)
            RES[(c, f, pol, lk)][cool + '_net'] = {'p_stable': float(np.isfinite(Te).mean()),
                                                   'p_below85': float((Te < 85).mean()),
                                                   'T_eq': p3(Te) if np.isfinite(Te).any() else None,
                                                   'n_stable': int(np.isfinite(Te).sum())}
del TG
OUT['theta_eff_net'] = {cool: p3(th_eff[cool]) for cool in ('still', 'fan')}
print('(1) Settled on the transient model\'s network [model]: theta_eff = R_lid || (theta_JB + R_BA), C/W: still '
      f'{pct(th_eff["still"])}, fan {pct(th_eff["fan"])} (section F draws 4-12 and 2-7); the board\'s heating adds '
      'Z phi P_off at the junction:')
for c, f, pol in (('aifoundry2', 600, 'boot'), ('aifoundry2', 100, 'floor'), ('aifoundry2', 100, 'floor+NoC')):
    T60 = np.full((N, 1), 60.0)
    _, Po_ = soc_off(c, f, pol, T60, 0)
    print(f'   {c} {f} MHz {pol:10s} idle at a 60 C die: off-die {pct(Po_[:, 0])} W; board heating adds '
          f'{pct(Zb["still"] * tr["phi"] * Po_[:, 0])} C (still), {pct(Zb["fan"] * tr["phi"] * Po_[:, 0])} C (fan) '
          'at the junction')
print('Share of draws that settle below 85 C, idle | 16-shire pattern: section F (theta drawn, no board heating) against '
      'the network (with it) [model]:')
for c in CARDS:
    for f, pol in ((600, 'boot'), (300, 'floor'), (100, 'boot'), (100, 'floor'), (100, 'floor+NoC')):
        key = (c, f, pol, 'idle')
        if key not in RES:
            continue
        cells_ = []
        for cool in ('still', 'fan'):
            a_ = [RES[(c, f, pol, lk)][cool]['p_below85'] * 100 for lk, _ in LOADKEYS]
            b_ = [RES[(c, f, pol, lk)][cool + '_net']['p_below85'] * 100 for lk, _ in LOADKEYS]
            cells_.append(f'{cool}: F {a_[0]:.0f} | {a_[1]:.0f} %, network {b_[0]:.0f} | {b_[1]:.0f} %')
        print(f'   {c:14s} {f:4d} MHz {pol:10s} ' + '; '.join(cells_))


# ---- (2) the window --------------------------------------------------------------------------------------------------
def step(c, f, pol, nsh, cool, TJ, TB):
    P, Po = soc_off(c, f, pol, TJ[:, None], nsh)
    P, Po = np.maximum(P[:, 0], 0.0), np.maximum(Po[:, 0], 0.0)
    q = (TJ - TB) / tr['thJB']
    dTJ = (P - q - (TJ - tr['Ta']) / tr['Rlid'][cool]) / tr['CJ']
    dTB = (tr['phi'] * Po + q - (TB - tr['Ta']) / tr['RBA'][cool]) / tr['CB']
    return np.minimum(TJ + DT * dTJ, 150.0), np.minimum(TB + DT * dTB, 150.0)


BOOTEND = {}


def boot_end(c, cool):
    if (c, cool) not in BOOTEND:
        TJ, TB = tr['Ta'].copy(), tr['Ta'].copy()
        f0, pol0 = BOOT[c]['f0'], ('floor' if c == 'aifoundry1-c0' else 'boot')
        for k in range(int(np.ceil(tr['tb'].max() / DT))):
            on = k * DT < tr['tb']
            nj, nb = step(c, f0, pol0, 0, cool, TJ, TB)
            TJ, TB = np.where(on, nj, TJ), np.where(on, nb, TB)
        BOOTEND[(c, cool)] = (TJ, TB)
    return BOOTEND[(c, cool)]


def window(c, f, pol, nsh, cool, delay, stops):
    """seconds from the end of the host boot until the die first reaches each stop (inf: not within 30 min); for the
    first `delay` seconds (per draw) the card idles at its boot point while the low point is set"""
    TJ, TB = (x.copy() for x in boot_end(c, cool))
    f0, pol0 = BOOT[c]['f0'], ('floor' if c == 'aifoundry1-c0' else 'boot')
    tc = {s_: np.where(TJ >= s_, 0.0, np.inf) for s_ in stops}
    dmax = float(np.max(delay))
    for k in range(int(TMAX / DT)):
        nj, nb = step(c, f, pol, nsh, cool, TJ, TB)
        if k * DT < dmax:
            on = k * DT < delay
            bj, bb = step(c, f0, pol0, 0, cool, TJ, TB)
            nj, nb = np.where(on, bj, nj), np.where(on, bb, nb)
        TJ, TB = nj, nb
        for s_ in stops:
            tc[s_] = np.where(np.isinf(tc[s_]) & (TJ >= s_), (k + 1) * DT, tc[s_])
        if np.isfinite(tc[max(stops)]).all():
            break
    return tc


WIN = {}
WPTS = [(600, 'boot'), (400, 'boot'), (400, 'floor'), (300, 'boot'), (300, 'floor'), (200, 'boot'),
        (200, 'floor'), (100, 'boot'), (100, 'floor'), (100, 'floor+NoC')]
fm = (lambda x: '>30 min' if x >= TMAX else f'{x:.0f} s')
print('\n(2) The window [model].  "set at boot": seconds from the end of the host boot to a die of 85 C if the point '
      'could be set at that instant (median [5-95]; ">30 min" = not within 30 min).  "look": seconds from the low point '
      'being set (20-60 s after the boot; none at 600 MHz) to the stop, median [5-95], and the share of draws with none '
      'left (the die at the stop before the point is set)')
for c in ('aifoundry2', 'aifoundry3'):
    for cool in ('still', 'fan'):
        TJb = boot_end(c, cool)[0]
        print(f'-- {c}, {cool}: die at the end of the host boot {pct(TJb)} C, at or above 85 C in {(TJb >= 85).mean()*100:.0f} % '
              f'of draws (nohs_calc.out E: a2 still 44 / 61 / 96, fan 43 / 56 / 78; a3 still 46 / 61 / 101, fan 45 / 58 / 93; '
              f'already >= 90 C at boot: a2 8 %, 2 %; a3 9 %, 5 %)')
        WIN[f'{c}|{cool}|boot_end'] = {'T_C': p3(TJb), 'frac_ge85': float((TJb >= 85).mean())}
        for f, pol in WPTS:
            for lk, nsh in LOADKEYS:
                own = (f == BOOT[c]['f0'] and pol == 'boot')
                t85 = window(c, f, pol, nsh, cool, np.zeros(N), (85.0,))[85.0]
                dl = np.zeros(N) if own else tr['tset']
                tc = window(c, f, pol, nsh, cool, dl, STOPS)
                rec = {'t85_s': p3(np.where(np.isinf(t85), 1e9, t85)), 'never_frac': float(np.isinf(t85).mean()),
                       'look_s': {}, 'look_none': {}, 'look_never': {}}
                cells_ = [f'set at boot, to 85 C {fm(np.median(np.where(np.isinf(t85), 1e9, t85)))}']
                for s_ in STOPS:
                    look = np.where(np.isinf(tc[s_]), np.inf, np.maximum(tc[s_] - dl, 0.0))
                    lk9 = np.where(np.isinf(look), 1e9, look)
                    rec['look_s'][f'{s_:.0f}'] = p3(lk9)
                    rec['look_none'][f'{s_:.0f}'] = float(np.mean(look <= 0))
                    rec['look_never'][f'{s_:.0f}'] = float(np.mean(np.isinf(look)))
                    q = np.percentile(lk9, [5, 50, 95])
                    cells_.append(f'look to {s_:.0f} C {fm(q[1])} [{fm(q[0])} - {fm(q[2])}], none {np.mean(look <= 0)*100:.0f} %')
                WIN[f'{c}|{cool}|{lk}|{f}|{pol}'] = rec
                print(f'   {f:4d} MHz {pol:10s} {lk:8s} ' + '; '.join(cells_))
OUT['window_after_boot'] = WIN

# ======================================================================================================================
hdr('G. The envelope')
ENV = {}
for c in CARDS:
    for cool in ('still', 'fan', 'heatsink'):
        for lk, _ in LOADKEYS:
            for pol in (['floor', 'floor+NoC'] if c == 'aifoundry1-c0' else POLICIES):
                best_set, best_any, pmax = None, None, (0.0, None)
                for f in CLOCKS:
                    key = (c, f, 'boot' if (pol == 'floor' and f == 600 and c != 'aifoundry1-c0') else pol, lk)
                    if key not in RES:
                        continue
                    p = RES[key][cool]['p_below85']
                    if p > pmax[0]:
                        pmax = (p, f)
                    if p >= 0.9:
                        if SETTABLE[f] and best_set is None:
                            best_set = f
                        if best_any is None:
                            best_any = f
                ENV[f'{c}|{cool}|{lk}|{pol}'] = {'highest_settable_90': best_set, 'highest_any_90': best_any,
                                                  'best_p': pmax[0], 'best_p_at': pmax[1]}
print('Highest clock at which the die settles below 85 C in >= 90 % of draws (settable clocks; "none" = no clock does, '
      'then the best share and where) [model]')
for cool in ('still', 'fan', 'heatsink'):
    print(f'-- {cool}')
    for c in CARDS:
        for lk, _ in LOADKEYS:
            cells_ = []
            for pol in (['floor', 'floor+NoC'] if c == 'aifoundry1-c0' else POLICIES):
                e = ENV[f'{c}|{cool}|{lk}|{pol}']
                if e['highest_settable_90']:
                    cells_.append(f'{pol}: {e["highest_settable_90"]} MHz')
                elif e['best_p'] == 0:
                    cells_.append(f'{pol}: none (0 % at every clock)')
                else:
                    cells_.append(f'{pol}: none (best {e["best_p"]*100:.0f} % at {e["best_p_at"]} MHz)')
            print(f'   {c:14s} {lk:8s} ' + ' | '.join(cells_))
OUT['envelope'] = ENV
print()
print('The cooling each point needs: theta85 (SoC basis, C/W, median [5-95]), idle and with the 16-shire pattern [model]')
for c in CARDS[:3]:
    for pol in POLICIES:
        cells_ = []
        for f in CLOCKS:
            if (c, f, pol, 'idle') not in RES:
                continue
            a, b = RES[(c, f, pol, 'idle')]['theta85_soc'], RES[(c, f, pol, 'pattern')]['theta85_soc']
            cells_.append(f'{f}: {a[1]:.2f}|{b[1]:.2f}')
        print(f'   {c:14s} {pol:10s} ' + '  '.join(cells_))
print('   (bare lid: 4-12 C/W still air, 2-7 with a fan; the stock heatsink ~1.1-1.6 C/W on the board basis)')

# ======================================================================================================================
hdr('H. Imaging at each settable point (imaging_calc.py\'s model, imaging_calc.json)')
IMG = args.imaging or os.path.join(HERE, 'imaging_calc.json')
IMGOUT = {}
if not os.path.exists(IMG):
    print(f'{IMG} not found: run imaging_calc.py --json first; section H skipped')
else:
    J = json.load(open(IMG))
    print(f'read {os.path.relpath(IMG, ROOT) if IMG.startswith(ROOT) else IMG} (seed {J["seed"]}, {J["draws"]} draws)')
    PAT = ['checkerboard', 'one shire', '2x2 block moving', 'half die']
    # per-shire switching power (W) at a point: P600 (median of U(0.60, 0.76), as imaging_calc.py A) x (f/600)(V/0.517)^2
    P600M = 0.68

    def lock_time(pm60, pm600, p):
        """seconds of lock-in for SNR 3 at per-shire power p (W), from the imaging model's least power at 60 and 600 s
        (median mW).  sigma ~ 1/sqrt(T); at >= 200 s every f_mod is allowed, so the 600 s value scales exactly; below
        it the 60 s value gives an upper bound"""
        t600 = 600.0 * (pm600 / (p * 1e3)) ** 2
        if t600 >= 200:
            return t600, False
        t60 = 60.0 * (pm60 / (p * 1e3)) ** 2
        return max(10.0, t60), True

    VIEWS = [('(b) lid top, taped, fan', 'fan', 'the camera on the taped lid, heatsink off, a fan'),
             ('(b) lid top, taped, still air', 'still', 'the camera on the taped lid, heatsink off, still air'),
             ('(a) delidded die, black-coated, IR-window cooler', 'irwin', 'a delidded, black-coated die under an IR-window cooler'),
             ('sensors', 'heatsink', 'the 34 on-die sensors, heatsink on, per-shire raw codes (a rebuilt BL2)'),
             ('stock', 'heatsink', 'the stock firmware\'s I/O-shire sensor, heatsink on (2x2 block beside it)')]
    # the camera's reading per kelvin of each view (emissivity, and through an IR-window cooler also the window's and the
    # oil film's transmission), medians from imaging_calc.json
    EPS_MED = {k: J['eps_median'][k] for k in ('(b) lid top, taped, fan', '(b) lid top, taped, still air',
                                               '(a) delidded die, black-coated, IR-window cooler')}
    print('the camera\'s reading per kelvin (medians, imaging_calc.json): ' + '; '.join(f'{k} {v:.3f}' for k, v in EPS_MED.items()))
    VIEWKEY = {'(b) lid top, taped, fan': 'b_fan', '(b) lid top, taped, still air': 'b_still',
               '(a) delidded die, black-coated, IR-window cooler': 'a_win'}
    # check the scaling against the imaging model's own lock-in time (taped lid, fan, checkerboard, 100 MHz, floor)
    lp = J['least_power']['(b) lid top, taped, fan']['checkerboard']
    tchk, _ = lock_time(lp['lock-in 60 s']['pmin_mW'][1], lp['lock-in 600 s']['pmin_mW'][1],
                        P600M * (100 / 600) * (0.398 / 0.517) ** 2)
    print(f'check: taped lid, fan, checkerboard at 100 MHz / 398 mV: {tchk:.0f} s by scaling the least power; the imaging '
          f'model\'s own median at 100 MHz / 398 mV: {J["lockin_time_s_floor"]["(b) lid top, taped, fan"]["checkerboard"]["100"][1]:.0f} s')
    print('A look of 10 s or less needs no steady state: with the heatsink on, 512 minions of random data (13.6 W, about '
          '16 shires) took 84 s from 80 to 90 C (12-heat-management.md) [measured]; bare, section F2 gives the seconds '
          'from the end of the host boot to 85 C with the pattern running (median) [model].')
    print('Per settable point (aifoundry2\'s voltages): per-shire switching power; for each view, whether a sustained 16-shire '
          'pattern settles below 85 C (share of draws), and per pattern the camera\'s apparent contrast in a 1 s-per-state '
          'difference image (mK, emissivity applied, product of medians) and the lock-in time to SNR 3 (median; "<=" = '
          'an upper bound; 10 = 10 s or less).  Sensors: contrast in real mK at the transistor plane.  [model]')
    SPTS = [(f, pol) for f in (600, 400, 300, 200, 100) for pol in (('boot',) if f == 600 else ('boot', 'floor'))]
    for f, pol in SPTS:
        vm = volts('aifoundry2', f, pol)[0]
        p = P600M * (f / 600.0) * (vm / 0.517) ** 2
        print(f'-- {f} MHz, {pol} ({vm*1e3:.0f} mV): {p*1e3:.0f} mW per shire of fp32 randn (x{p/P600M:.3f} of 600 MHz)')
        for vk, cool, desc in VIEWS:
            st_ = RES.get(('aifoundry2', f, 'boot' if f == 600 else pol, 'pattern'), {}).get(cool)
            stab = f'sustained: {st_["p_below85"]*100:.0f} % settle' if st_ else '-'
            wk = f'aifoundry2|{cool}|pattern|{f}|{pol}'
            if cool in ('still', 'fan') and wk in WIN:
                _lk = WIN[wk]['look_s']['75'][1]
                stab += (f'; after boot, a look of {_lk:.0f} s to the 75 C stop' if _lk < TMAX else '; after boot >30 min') + \
                    f' (none left in {WIN[wk]["look_none"]["75"]*100:.0f} %)'
            cells_ = []
            for pt in PAT:
                if vk == 'sensors':
                    s = J['sensors'][f'c_hs|{pt}']
                    g = s['mK_per_W'][1]
                    t, ub = lock_time(s['pmin_mW_median'][1], s['pmin_mW_median'][2], p)
                    con = g * p
                elif vk == 'stock':
                    if pt != '2x2 block moving':
                        continue
                    s = J['stock_io']
                    t, ub = lock_time(s['(0,4)|60']['pmin_mW'][1], s['(0,4)|600']['pmin_mW'][1], p)
                    con = float('nan')
                else:
                    lpv = J['least_power'][vk][pt]
                    g = J['contrast_mK_per_W'][VIEWKEY[vk]]['top'][pt][1]
                    con = EPS_MED[vk] * g * p
                    t, ub = lock_time(lpv['lock-in 60 s']['pmin_mW'][1], lpv['lock-in 600 s']['pmin_mW'][1], p)
                ts = ('10' if t <= 10.0 else (('<=' if ub else '') + (f'{t:.0f} s' if t < 600 else f'{t/60:.0f} min')))
                cells_.append(f'{pt}: {"" if not np.isfinite(con) else f"{con:.3g} mK, "}{ts}')
                IMGOUT[f'{f}|{pol}|{vk}|{pt}'] = {'mW_per_shire': p * 1e3, 'contrast_mK': None if not np.isfinite(con) else con,
                                                  'lockin_s': t, 'upper_bound': ub,
                                                  'p_settle85': None if not st_ else st_['p_below85']}
            print(f'   {desc[:62]:62s} [{stab}]  ' + '; '.join(cells_))
    OUT['imaging'] = IMGOUT

# ======================================================================================================================
hdr('I. Direct answers (numbers from the sections above)')
a2 = 'aifoundry2'


def rp(c, f, pol, lk, cool):
    key = (c, f, 'boot' if (f == 600 and c != 'aifoundry1-c0') else pol, lk)
    return RES[key][cool]


ANS = {}
T60 = np.full((N, 1), 60.0)
for c in ('aifoundry2', 'aifoundry3', 'aifoundry1-c1'):
    p600 = board(c, 600, 'boot', T60)[:, 0]
    p100b = board(c, 100, 'boot', T60)[:, 0]
    p100f = board(c, 100, 'floor', T60)[:, 0]
    p100n = board(c, 100, 'floor+NoC', T60)[:, 0]
    p10n = board(c, 10, 'floor+NoC', T60)[:, 0]
    s600 = (soc(c, 600, 'boot', T60 + 0.05) - soc(c, 600, 'boot', T60 - 0.05))[:, 0] / 0.1
    s100 = (soc(c, 100, 'floor+NoC', T60 + 0.05) - soc(c, 100, 'floor+NoC', T60 - 0.05))[:, 0] / 0.1
    ANS[c] = {'idle600_60C': p3(p600), 'clock_only_100': p3(p600 - p100b), 'voltage_floor_more': p3(p100b - p100f),
              'noc_more': p3(p100f - p100n), 'ten_MHz_more': p3(p100n - p10n), 'left_100_floorNoC': p3(p100n),
              'dPdT_soc_600': p3(s600), 'dPdT_soc_100_floorNoC': p3(s100),
              'load16_board': {f'{f_}|{pol_}': p3((board(c, f_, pol_, T60, 16) - board(c, f_, pol_, T60))[:, 0])
                               for f_, pol_ in ((600, 'boot'), (100, 'boot'), (100, 'floor'))}}
    print(f'{c}, idle, die at 60 C [model]: {np.median(p600):.1f} W at 600 MHz.  100 MHz with the voltages left (SET_FREQUENCY '
          f'alone) removes {pct(p600 - p100b)} W; the floor voltages remove {pct(p100b - p100f)} W more; the NoC at '
          f'200 MHz / 400 mV {pct(p100f - p100n)} W more; 10 MHz (not settable) would remove {pct(p100n - p10n)} W '
          f'more.  Left: {pct(p100n)} W.  The die\'s dP/dT: {pct(s600)} W/C at 600 MHz, {pct(s100)} at 100 MHz '
          f'floor+NoC')
    for cool in ('still', 'fan'):
        print(f'   bare, {cool:5s}: settles below 85 C at idle in ' + ', '.join(
            f'{f} MHz {pol} {rp(c, f, pol, "idle", cool)["p_below85"]*100:.0f} %'
            for f, pol in ((600, 'boot'), (100, 'boot'), (100, 'floor'), (100, 'floor+NoC'), (10, 'floor+NoC'))) +
            ' of draws [model]')
    th = RES[(c, 100, 'floor+NoC', 'idle')]['theta85_soc']
    print(f'   to settle below 85 C at 100 MHz floor+NoC it needs theta <= {th[1]:.2f} C/W on the SoC basis [5-95: '
          f'{th[0]:.2f}-{th[2]:.2f}]; the bare lid gives 4-12 in still air and 2-7 with a fan [model]')
OUT['answers'] = ANS
print()
print('Can the owner run at 100 MHz?  The command can: DM_CMD_SET_FREQUENCY -f 100,400 selects mode 62 (1100 MHz / 11) '
      'of the step clock; the handler is identical in 0.18.0, 0.20.0 and 0.21.0 (the public source nearest card 0\'s '
      '0.21.2); it changes no voltage [source].  No lab card has run below 300 MHz (beyond the microseconds each PLL4 change spends bypassed '
      'to the 100 MHz reference: inference from io_pll.c), so whether the minions, the shire DLL and the master minion\'s '
      'runtime (its handshake timeouts, 5-10 timer ticks, are 52-105 ms of wall time if a tick is the 10.5 ms that the '
      'measured ~1.05 s heartbeat implies, review-governor.md section 1.4) work there is not established [inference].  aifoundry3 '
      'is the natural card (its governor is latched); on aifoundry2 the governor restores 600 MHz at its next idle or '
      'thermal-loop exit unless the owner changes it; card 1 must not have its voltages set; card 0 is off-limits [source].')
print('Thermally, 100 MHz alone does not make a bare card safe: see the lines above.  With the heatsink on, every '
      'settable clock settles at idle, and a sustained 16-shire pattern settles below 85 C in >= 90 % of draws at: ' +
      '; '.join(f'{SHORT[c]} ' + (f'{ENV[f"{c}|heatsink|pattern|boot"]["highest_settable_90"]} MHz'
                                   if ENV[f"{c}|heatsink|pattern|boot"]["highest_settable_90"] else 'no settable clock') +
                f' with the voltages left, {ENV[f"{c}|heatsink|pattern|floor"]["highest_settable_90"]} MHz at the floor'
                for c in CARDS[:3]) + ' [model]')
_ct100 = (PC[a2]['minion'][0] * (FLOOR['minion'] / BOOT[a2]['vm']) ** 2 +
          PC[a2]['sram'][0] * (FLOOR['sram'] / BOOT[a2]['vs']) ** 2) * (100 / 600)
OUT['clock_tree_left_100_floor_die_W'] = p3(_ct100)
print('10 MHz: no PLL mode exists; it needs a new BL2 (signed and flashed; the cards have never run one) or a debugger '
      '[source].  At the floor voltages the minion and SRAM clock tree left at 100 MHz is only ' +
      f'{pct(_ct100)} W on aifoundry2\'s die; 10 MHz would remove nine tenths of it, '
      f'{" / ".join(f"{v:.3g}" for v in ANS[a2]["ten_MHz_more"])} W at the board with its regulators\' loss (NoC lowered '
      'too): everything left is leakage and power no clock touches [model].')
sw = P600 * 16 / UDIE
print('What ten times slower buys: the clock can be set to 100 MHz (6x slower; 60 MHz, 10x, is not in the table).  At '
      f'idle it removes the clock tree, {" / ".join(f"{v:.3g}" for v in ANS[a2]["clock_only_100"])} W of aifoundry2\'s idle at 60 C '
      '(5th/50th/95th), and nothing of the leakage, which the voltage and the die temperature set.  Under a 16-shire '
      f'pattern the switching falls from {pct(sw)} W at the board at 600 MHz to {pct(sw/6)} W with the voltages left, '
      f'{pct(sw*(100/600)*(0.398/0.517)**2)} W at the floor: the load stops mattering, the idle floor does not.  The '
      f'camera\'s signal falls by the same factor, and the lock-in time a pattern needs grows as 1/signal^2: '
      f'{(600/100)**2:.0f} times at 100 MHz with the voltages left, {((600/100)*(V600/FLOOR["minion"])**2)**2:.0f} times at the '
      'floor; on a taped lid most patterns still show within 10-40 s at 100 MHz (section H) [model].')
if IMGOUT:
    print('A short look on a bare, taped lid (aifoundry2): lock-in seconds for SNR 3 against the look a bare card leaves, '
          'from the low point being set (20-60 s after the boot) to the plan\'s 75 C stop with the 16-shire pattern running '
          '(median, and the share with none left), and, for comparison, the seconds to 85 C had the point been set at the '
          'instant of boot (median) [model]:')
    for f, pol in ((600, 'boot'), (300, 'floor'), (100, 'floor'), (100, 'floor+NoC')):
        pk = pol if pol != 'floor+NoC' else 'floor'
        lk_ = {pt: IMGOUT.get(f'{f}|{pk}|(b) lid top, taped, fan|{pt}', {}).get('lockin_s') for pt in
               ('checkerboard', 'one shire', '2x2 block moving', 'half die')}
        W_ = {cool: WIN[f'aifoundry2|{cool}|pattern|{f}|{pol}'] for cool in ('still', 'fan')}
        print(f'   {f} MHz {pol:10s}: lock-in ' + ', '.join(f'{pt} {"<=10" if v is not None and v <= 10 else f"{v:.0f}"} s'
                                                     for pt, v in lk_.items() if v is not None) +
              '; look to 75 C ' + ', '.join(f'{cool} {fm(w["look_s"]["75"][1])} ({w["look_none"]["75"]*100:.0f} % none)'
                                            for cool, w in W_.items()) +
              '; set at boot, to 85 C ' + ', '.join(f'{cool} {fm(w["t85_s"][1])}' for cool, w in W_.items()))
if args.json:
    with open(args.json, 'w') as fh:
        json.dump(OUT, fh, indent=1, default=float)
    print('\nwrote', os.path.basename(args.json))
