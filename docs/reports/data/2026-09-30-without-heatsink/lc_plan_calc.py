#!/usr/bin/env python3
"""Low clock, heatsink on, then bare: the registered predictions of the measurement plan (30 Sep 2026).

    python3 lc_plan_calc.py > lc_plan_calc.out        (about 4 minutes; nice -n 19 on a shared machine)

Written for docs/reports/data/2026-09-30-without-heatsink/ (it finds the repository from its own path there, or from
the known checkout on aifoundry2 when run from ~/claude/work/lowclock/plan/). Arithmetic on committed data only: no card
is opened. Every input names its source; ASSUMED marks a value that is not measured or read from source.
Not to be confused with lowclock_calc.py beside it: that is the envelope model (the page's low-clock section); this is
the measurement plan's own prediction set. Section K reads lowclock_calc.json and restates its predictions in this
plan's terms, so that both are registered before the first write.

Sections:
  A  aifoundry3's and aifoundry2's idle rails against die temperature (E44's cooling cycles): per-rail laws
     P = P_fix + A exp((T-80)/T_L). P_fix, the part that does not follow temperature, bounds the clock-dependent idle
     power D (dynamic power does not follow temperature; leakage does).
  B  aifoundry2's idle reset (E51): the board step when the governor moves an idle card from 800 MHz (619/830 mV
     minion/SRAM on die) to 600 MHz (519/704 mV) at one die temperature.
  C  A and B read together: the leakage's voltage exponent n (P_leak ~ V^n) and D on aifoundry2.
  D  Stage A predictions (aifoundry3, clock only, 525/700 mV set-points): the idle step 600 -> f per rail and board.
  E  Stage B predictions (aifoundry3 at 100 MHz): idle rails against the minion and SRAM set-points; the lowest point.
  F  The bare card at the low point: SoC power and slope, the largest theta_JA that settles, the Monte Carlo of
     nohs_calc.py (imported: the same model, ranges and code), and the power-on window (600 MHz until the low point is set).
  G  Detection: the noise of a same-temperature idle step on aifoundry3, and what four passes resolve.
  I  The load item and the low-point dwell.   H  The schedule.   J  The gap between two sampler windows.
  K  The envelope model (lowclock_calc.json) restated as predictions for Stages A and B, beside this plan's own.
"""
import collections
import contextlib
import glob
import gzip
import io
import json
import math
import os
import statistics as st
import sys

import numpy as np
from scipy.integrate import solve_ivp

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(HERE) == '2026-09-30-without-heatsink':
    REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
else:
    REPO = '/home/yaroslavvb/claude/et-soc1-prototyping'
DATA = os.path.join(REPO, 'docs', 'reports', 'data')
NOHS = os.path.join(DATA, '2026-09-30-without-heatsink')
V3RAW = os.path.join(DATA, '2026-09-25-claims-v3', 'raw')              # E44 idle cycles: raw/<card>/idle/p1..p3
DV2 = os.path.join(DATA, '2026-09-28-dvfs2-aifoundry2')                 # E51 raw: raw/p*/, validation/raw/p*/
HUB = os.path.join(REPO, 'docs', 'reports', 'sources', 'limits-of-observability.data.json')   # E46 unmetered fit
rng = np.random.default_rng(20260930)
GRID = [12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 60, 80, 120, 200]


def pct(x, p=(5, 50, 95), f='%.3g'):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    return 'n/a' if len(x) == 0 else ' / '.join(f % v for v in np.percentile(x, p))


def hdr(s):
    print()
    print('=' * 110)
    print(s)
    print('=' * 110)


# ------------------------------------------------------------------------------------------------------------------
hdr('A. Idle rails against die temperature (E44 cooling cycles, 600 MHz, samples >= 8 s after the heater)')
# ------------------------------------------------------------------------------------------------------------------
# Selection as docs/reports/data/2026-09-28-overheating/scripts/idle_vs_temp.py (which uses 5 s; 8 s here lets the
# rails' ~1 s filter settle), per whole-degree bin of the 34-sensor mean, bins with >= 20 samples, median per bin.
RAILS = ('board', 'minion', 'sram', 'noc', 'unmetered')
LAW = {}      # LAW[card][rail] = dict(best=(TL, P_fix, A), band=[(TL, P_fix, A), ...within 10 % of the best rms])
BIN = {}
for card in ('aifoundry3', 'aifoundry2'):
    bins = collections.defaultdict(list)
    setp = []
    for pd in sorted(glob.glob(os.path.join(V3RAW, card, 'idle', 'p*'))):
        L = [json.loads(x) for x in open(os.path.join(pd, 'launches.jsonl')) if x.strip()]
        if not L:
            continue
        t_last = max(x['t_end_ms'] for x in L)
        with gzip.open(os.path.join(pd, 'telemetry.jsonl.gz'), 'rt') as fh:
            for line in fh:
                s = json.loads(line)
                if s['t_ms'] < t_last + 8000 or (s.get('mhz') or {}).get('minion') != 600:
                    continue
                sp = s['sp']
                b, m, r, n = s['board_w'], sp['minion_w'][0], sp['sram_w'][0], sp['noc_w'][0]
                bins[s['temp_c']['minshire'][0]].append((b, m, r, n, b - m - r - n))
                setp.append((s['reg_mv']['minion'], s['reg_mv']['sram'], s['reg_mv']['noc']))
    T = np.array(sorted(t for t in bins if len(bins[t]) >= 20), dtype=float)
    N = np.array([len(bins[int(t)]) for t in T])
    BIN[card] = (T, N, bins)
    LAW[card] = {}
    sm = [st.median(x[i] for x in setp) for i in range(3)]
    print(f'{card}: {int(N.sum())} idle samples in {len(T)} bins, {T.min():.0f}-{T.max():.0f} C; set-points minion/SRAM/NoC '
          f'{sm[0]:.0f}/{sm[1]:.0f}/{sm[2]:.0f} mV (reg_mv)  [measured, E44: {os.path.relpath(V3RAW, REPO)}/{card}/idle/p1-p3]')
    for j, rail in enumerate(RAILS):
        P = np.array([st.median(v[j] for v in bins[int(t)]) for t in T])
        fits = []
        for TL in GRID:
            X = np.column_stack([np.ones_like(T), np.exp((T - 80.0) / TL)])
            c, *_ = np.linalg.lstsq(X * np.sqrt(N)[:, None], P * np.sqrt(N), rcond=None)
            if c[1] < 0:
                continue
            rms = math.sqrt(float(np.sum(N * (X @ c - P) ** 2) / N.sum()))
            fits.append((rms, TL, float(c[0]), float(c[1])))
        fits.sort()
        rms0 = fits[0][0]
        band = [(f[1], f[2], f[3]) for f in fits if f[0] <= 1.10 * rms0]
        LAW[card][rail] = {'best': (fits[0][1], fits[0][2], fits[0][3]), 'band': band, 'rms': rms0}
        pf = [b[1] for b in band]
        tl = [b[0] for b in band]
        TLb, Pfb, Ab = fits[0][1], fits[0][2], fits[0][3]
        val = lambda t: Pfb + Ab * math.exp((t - 80) / TLb)
        slope = lambda t: Ab / TLb * math.exp((t - 80) / TLb)
        print(f'  {rail:9s} best T_L {TLb:3d} C: P_fix {Pfb:6.2f} W, A(80 C) {Ab:5.2f} W, rms {rms0:.3f} W | '
              f'T_L within 10% of best rms {min(tl)}-{max(tl)} C: P_fix {min(pf):.2f} .. {max(pf):.2f} W | '
              f'at 56 C {val(56):5.2f} W, slope {slope(56):.3f} W/C, dlnP/dT {slope(56) / val(56):.4f} /C')


def rail(card, name, T, which='best'):
    TL, Pf, A = LAW[card][name][which] if which == 'best' else which
    return Pf + A * np.exp((np.asarray(T, dtype=float) - 80.0) / TL)


KB = 8.617e-5   # Boltzmann constant, eV/K


def pfix_band(card, name, form):
    """P_fix of a rail's idle law in one form: 'exp' P_fix + A e^((T-80)/T_L) (the set's form), 'arr' P_fix + A e^(-Ea/kT),
    'T2arr' P_fix + A T^2 e^(-Ea/kT) (the subthreshold form); the band is every grid value within 10 % of the best rms"""
    T, N, bins = BIN[card]
    j = RAILS.index(name)
    P = np.array([st.median(v[j] for v in bins[int(t)]) for t in T])
    TK = T + 273.15
    grid = GRID if form == 'exp' else list(np.arange(0.05, 1.20, 0.01))
    out = []
    for g in grid:
        if form == 'exp':
            x = np.exp((T - 80.0) / g)
        elif form == 'arr':
            x = np.exp(-g / (KB * TK) + g / (KB * 353.15))
        else:
            x = (TK / 353.15) ** 2 * np.exp(-g / (KB * TK) + g / (KB * 353.15))
        X = np.column_stack([np.ones_like(T), x])
        c, *_ = np.linalg.lstsq(X * np.sqrt(N)[:, None], P * np.sqrt(N), rcond=None)
        if c[1] < 0:
            continue
        out.append((math.sqrt(float(np.sum(N * (X @ c - P) ** 2) / N.sum())), g, float(c[0])))
    out.sort()
    band = [o[2] for o in out if o[0] <= 1.10 * out[0][0]]
    return out[0][0], out[0][1], out[0][2], min(band), max(band)


FORMS = ('exp', 'arr', 'T2arr')
PF = {c: {r: {f: pfix_band(c, r, f) for f in FORMS} for r in ('minion', 'sram')} for c in LAW}
print('Reading (inference): dynamic power does not follow die temperature, so the clock-dependent idle power D of a rail '
      'is at most the part of its idle law that does not follow temperature, P_fix. P_fix depends on the form of the '
      'leakage law (all three fit the 30 C span about equally):')
for c in LAW:
    for r in ('minion', 'sram'):
        print(f'  {c} {r:6s}: ' + ' | '.join(f'{f}: rms {PF[c][r][f][0]:.4f} W, P_fix {PF[c][r][f][2]:.2f} '
                                             f'(band {PF[c][r][f][3]:.2f} .. {PF[c][r][f][4]:.2f})' for f in FORMS))
DCAP_M = {c: max(0.0, max(PF[c]['minion'][f][4] for f in FORMS)) for c in LAW}
DCAP_S = {c: max(0.0, max(PF[c]['sram'][f][4] for f in FORMS)) for c in LAW}
DUP = {c: (PF[c]['minion']['exp'][3], PF[c]['minion']['exp'][4]) for c in LAW}
DSP = {c: (PF[c]['sram']['exp'][3], PF[c]['sram']['exp'][4]) for c in LAW}
print(f'=> bound on D at 600 MHz (union of the three forms): minion rail aifoundry3 <= {DCAP_M["aifoundry3"]:.2f} W, '
      f'aifoundry2 <= {DCAP_M["aifoundry2"]:.2f} W; SRAM rail aifoundry3 <= {DCAP_S["aifoundry3"]:.2f} W, aifoundry2 <= {DCAP_S["aifoundry2"]:.2f} W')

# The unmetered fit (E46, three passes on each card): unmetered W per rail W, i.e. the regulators' delivery loss
hub = json.load(open(HUB))['power']['fit']
K = {c: hub[c]['coef'] for c in ('aifoundry2', 'aifoundry3')}
print('unmetered W per rail W (E46 fit, ' + os.path.relpath(HUB, REPO) + ' power.fit): ' +
      '; '.join(f'{c} minion {K[c]["minion"]:.3f}, SRAM {K[c]["sram"]:.3f}, NoC {K[c]["noc"]:.3f}' for c in K))

# ------------------------------------------------------------------------------------------------------------------
hdr("B. aifoundry2's idle reset (E51): 800 MHz -> 600 MHz on an idle card, board power just before and just after")
# ------------------------------------------------------------------------------------------------------------------
# Event: consecutive 10 Hz samples at 800 then 600 MHz; no launch running; the last kernel ended >= 300 ms before the
# first 'before' sample (board_w is the PMIC's per-pass reading, one pass late); no launch within 800 ms after; >= 3
# 'before' samples with the 800 MHz point's voltages on die (minion >= 610, SRAM >= 825 mV) and a board spread
# <= 0.5 W; >= 3 'after' samples at 600 MHz within 800 ms. Step = median(before) - median(after).
dirs = sorted(glob.glob(os.path.join(DV2, 'raw', 'p*'))) + sorted(glob.glob(os.path.join(DV2, 'validation', 'raw', 'p*')))
EV = []
IDLE2 = collections.defaultdict(list)     # aifoundry2 idle rails at 600 MHz in the same files, by whole degree
for d in dirs:
    lf = os.path.join(d, 'launches.jsonl')
    if not os.path.exists(lf):
        continue
    Ls = [json.loads(x) for x in open(lf) if x.strip()]
    Ls = [x for x in Ls if 't_start_ms' in x and 't_end_ms' in x]
    for tf in sorted(glob.glob(os.path.join(d, 'tel-*.jsonl.gz'))):
        S = []
        with gzip.open(tf, 'rt') as fh:
            for line in fh:
                try:
                    s = json.loads(line)
                except ValueError:
                    continue
                if s.get('mhz') and s.get('board_w') is not None:
                    S.append(s)
        for s in S:   # idle rails: 600 MHz, >= 8 s after any launch ended and >= 2 s before the next starts
            t = s['t_ms']
            if s['mhz']['minion'] != 600:
                continue
            if any(x['t_start_ms'] - 2000 <= t <= x['t_end_ms'] + 8000 for x in Ls):
                continue
            IDLE2[s['temp_c']['minshire'][0]].append((s['board_w'], s['sp']['minion_w'][0], s['sp']['sram_w'][0]))
        for i in range(1, len(S)):
            a, b = S[i - 1], S[i]
            if not (a['mhz']['minion'] == 800 and b['mhz']['minion'] == 600):
                continue
            t = b['t_ms']
            if any(x['t_start_ms'] <= t <= x['t_end_ms'] for x in Ls):
                continue
            ended = [x['t_end_ms'] for x in Ls if x['t_end_ms'] <= t]
            if not ended or any(t < x['t_start_ms'] < t + 800 for x in Ls):
                continue
            kend = max(ended)
            pre = [s for s in S[max(0, i - 20):i] if s['mhz']['minion'] == 800 and s['t_ms'] >= kend + 300
                   and s['die_mv']['minion'] >= 610 and s['die_mv']['sram'] >= 825]
            post = [s for s in S[i:i + 10] if s['mhz']['minion'] == 600 and s['t_ms'] <= t + 800]
            if len(pre) < 3 or len(post) < 3:
                continue
            pb = [s['board_w'] for s in pre]
            if max(pb) - min(pb) > 0.5:
                continue
            EV.append({'file': os.path.relpath(tf, DATA), 'after_end_s': (t - kend) / 1e3, 'n800': len(pre), 'n600': len(post),
                       'before': st.median(pb), 'after': st.median(s['board_w'] for s in post),
                       'T': st.median(s['temp_c']['minshire'][0] for s in pre + post),
                       'mv': (st.median(s['die_mv']['minion'] for s in pre), st.median(s['die_mv']['minion'] for s in post),
                              st.median(s['die_mv']['sram'] for s in pre), st.median(s['die_mv']['sram'] for s in post))})
steps = np.array([e['before'] - e['after'] for e in EV])
Tev = np.array([e['T'] for e in EV])
mvs = np.array([e['mv'] for e in EV])
print(f'{len(EV)} idle-reset events in {len(dirs)} E51 pass directories  [measured: {os.path.relpath(DV2, REPO)}/(validation/)raw/p*/tel-*.jsonl.gz]')
for e in EV:
    print(f'  {e["file"]}: reset {e["after_end_s"]:.2f} s after the kernel ended; {e["n800"]} + {e["n600"]} samples; '
          f'board {e["before"]:.2f} -> {e["after"]:.2f} W (step {e["before"] - e["after"]:.2f}); die {e["T"]:.0f} C')
bs = np.array([np.median(rng.choice(steps, len(steps))) for _ in range(4000)])
print(f'step: median {np.median(steps):.2f} W, range {steps.min():.2f} .. {steps.max():.2f} W, bootstrap 95% of the median '
      f'{np.percentile(bs, 2.5):.2f} .. {np.percentile(bs, 97.5):.2f} W; die {Tev.min():.0f}-{Tev.max():.0f} C (median {np.median(Tev):.0f})')
RHO_M = float(np.median(mvs[:, 0]) / np.median(mvs[:, 1]))
RHO_S = float(np.median(mvs[:, 2]) / np.median(mvs[:, 3]))
print(f'on-die voltages (median): minion {np.median(mvs[:, 0]):.0f} -> {np.median(mvs[:, 1]):.0f} mV (x{RHO_M:.4f}), '
      f'SRAM {np.median(mvs[:, 2]):.0f} -> {np.median(mvs[:, 3]):.0f} mV (x{RHO_S:.4f}); NoC unchanged')
T2 = sorted(t for t in IDLE2 if len(IDLE2[t]) >= 20)
print('aifoundry2 idle rails at 600 MHz in the same files (>= 8 s after a kernel): ' +
      '; '.join(f'{t} C: board {st.median(v[0] for v in IDLE2[t]):.2f}, minion {st.median(v[1] for v in IDLE2[t]):.2f}, '
                f'SRAM {st.median(v[2] for v in IDLE2[t]):.2f} W (n {len(IDLE2[t])})' for t in T2 if 59 <= t <= 67))
TEV = float(np.median(Tev))
print(f'E44 laws extrapolated to {TEV:.0f} C (their bins start at 67 C): minion {float(rail("aifoundry2", "minion", TEV)):.2f} W, '
      f'SRAM {float(rail("aifoundry2", "sram", TEV)):.2f} W')

# ------------------------------------------------------------------------------------------------------------------
hdr('C. A and B together: the voltage exponent of leakage (P_leak ~ V^n) and the clock-dependent idle power D')
# ------------------------------------------------------------------------------------------------------------------
# Model (inference): a rail's idle power = L (leakage, ~V^n) + D (dynamic, ~f V^2). The idle-reset step is then
#   S = (1+k_m)[(P_m - D_m)(rho_m^n - 1) + D_m((800/600) rho_m^2 - 1)] + (1+k_s)[(P_s - D_s)(rho_s^n - 1) + D_s((800/600) rho_s^2 - 1)]
# with P_m, P_s the idle rails at 600 MHz at the event temperature and k the delivery loss. One equation, unknowns
# n, D_m, D_s: draw n ~ U(1, 4) (ASSUMED prior, wider than NV's registered 1.4-3.6), D_s ~ U(0, max(0, P_fix,s))
# (section A), P_m, P_s from a whole-degree bin of E51's own idle samples at the event temperature (+-1 C), S from the
# bootstrap of the median step, and solve for D_m. Keep draws with 0 <= D_m <= P_m. Then apply section A's bound
# D_m <= P_fix of the minion law (aifoundry2's band).
def idle2(t):
    t = int(round(t))
    pool = [v for tt in (t - 1, t, t + 1) for v in IDLE2.get(tt, [])]
    if len(pool) < 20:
        return float(rail('aifoundry2', 'minion', t)), float(rail('aifoundry2', 'sram', t))
    return st.median(v[1] for v in pool), st.median(v[2] for v in pool)


PM2, PS2 = idle2(TEV)
km, ks = K['aifoundry2']['minion'], K['aifoundry2']['sram']
fm2 = (800 / 600) * RHO_M ** 2
fs2 = (800 / 600) * RHO_S ** 2


def solve_dm(Sv, nn, Pm, Ps, Ds):
    sram_term = (1 + ks) * ((Ps - Ds) * (RHO_S ** nn - 1) + Ds * (fs2 - 1))
    return ((Sv - sram_term) / (1 + km) - Pm * (RHO_M ** nn - 1)) / (fm2 - RHO_M ** nn)


def n_for_dm(dm, Sv=float(np.median(steps))):
    lo, hi = 0.5, 3.6
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if solve_dm(Sv, mid, PM2, PS2, 0.0) > dm:   # D_m falls as n rises
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


ND = 40000
n = rng.uniform(1.0, 4.0, ND)
Sd = rng.choice(bs, ND)
Ds = rng.uniform(0, DCAP_S['aifoundry2'], ND)
Pm = PM2 * rng.uniform(0.97, 1.03, ND)      # ASSUMED +-3 % for the bin median and the rails' 1/0.94 filter question
Ps = PS2 * rng.uniform(0.97, 1.03, ND)
den = fm2 - RHO_M ** n
Dm = solve_dm(Sd, n, Pm, Ps, Ds)
ok = (den > 0.05) & (Dm >= 0) & (Dm <= Pm)
cap = DCAP_M['aifoundry2']
ok2 = ok & (Dm <= cap)
print(f'idle rails at 600 MHz at {TEV:.0f} C (E51 idle samples): minion {PM2:.2f} W, SRAM {PS2:.2f} W; '
      f'delivery loss k_minion {km:.3f}, k_SRAM {ks:.3f}; SRAM D_s ~ U(0, {DCAP_S["aifoundry2"]:.2f}) W')
print('the relation the step fixes (median step, D_s = 0): D_m on aifoundry2 -> the leakage exponent n: ' +
      ', '.join(f'{d:.1f} W -> {n_for_dm(d):.2f}' for d in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0)))
print(f'draws that reproduce the step with 0 <= D_m <= P_m: {ok.sum()} of {ND}: n {pct(n[ok])}, D_m {pct(Dm[ok])} W')
print(f'... and also D_m <= {cap:.2f} W (section A, aifoundry2, union of the forms): {ok2.sum()}: '
      f'n {pct(n[ok2], (2.5, 50, 97.5))} (2.5/50/97.5 %), D_m {pct(Dm[ok2], (2.5, 50, 97.5))} W')
N_LO, N_HI = float(np.percentile(n[ok2], 2.5)), float(np.percentile(n[ok2], 97.5))
N_MID = float(np.median(n[ok2]))
print(f'=> registered leakage exponent band (inference from measured A and B): n in [{N_LO:.2f}, {N_HI:.2f}], central {N_MID:.2f}. '
      f'FinFET textbook (tools/claims-v3/nv/DESIGN.md s3): 1.5-2.4; DIBL-only with the O11 figures (40 mV/V, 65 mV/dec) at 0.52 V: '
      f'{1 + 0.040 * 0.52 / (0.065 / math.log(10)):.2f}')
for vr, lab in ((400 / 525, 'minion 525 -> 400 mV'), (660 / 700, 'SRAM 700 -> 660 mV')):
    print(f'   leakage power factor {lab}: x{vr ** N_HI:.3f} .. x{vr ** N_LO:.3f} (central x{vr ** N_MID:.3f}); '
          f'under the rival band n 1.4 .. {N_LO:.2f}: x{vr ** N_LO:.3f} .. x{vr ** 1.4:.3f}')
# transfer to aifoundry3: n is the process's; D scales with the card's switching (aifoundry3 / aifoundry2 = 0.92-0.99
# as registered in version 3, docs/findings/11-thermal-model.md) and with V^2 (525 vs 520 mV set-points)
sc3 = rng.uniform(0.92, 0.99, ok2.sum()) * (525 / 520) ** 2
J_n = n[ok2]
J_dm3 = Dm[ok2] * sc3
keep = J_dm3 <= DCAP_M['aifoundry3']
J_n, J_dm3 = J_n[keep], J_dm3[keep]
J_ds3 = rng.uniform(0, DCAP_S['aifoundry3'], len(J_n))
print(f'transferred to aifoundry3 ({len(J_n)} joint draws): D_m {pct(J_dm3)} W, n {pct(J_n)}')
print('CROSS-PREDICTION (registered): the D_m that Stage A measures on aifoundry3 fixes the n that Stage B must find: ' +
      ', '.join(f'{d:.1f} W -> n {n_for_dm(d / (0.955 * (525 / 520) ** 2)):.2f}' for d in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5)) +
      ' (+-0.05 from the step\'s spread and the 0.92-0.99 transfer)')

# ------------------------------------------------------------------------------------------------------------------
hdr('D. Stage A predictions: aifoundry3, clock only (set-points 525/700/485 mV), idle, die at T_ref')
# ------------------------------------------------------------------------------------------------------------------
# D_m(aifoundry3) ~ U(0, P_fix band top); D_s ~ U(0, max(0, P_fix,s top)) (section A); k from E46.
k3m, k3s, k3n = K['aifoundry3']['minion'], K['aifoundry3']['sram'], K['aifoundry3']['noc']
Dm3, Ds3 = J_dm3, J_ds3
Dm3_best = max(0.0, PF['aifoundry3']['minion']['exp'][2])
Ds3_best = max(0.0, PF['aifoundry3']['sram']['exp'][2])
LEVELS = (400, 300, 200, 100)
print('TH-C0 (null): no clock-dependent idle power: |board step| <= 0.3 W at every level')
print('TH-CS (the record): step = (1 - f/600) [(1 + k_m) D_m + (1 + k_s) D_s] with 0 < D <= P_fix; NoC rail 0; '
      'unmetered k_m dP_m + k_s dP_s')
for f_ in FORMS:
    cm, cs = max(0, PF['aifoundry3']['minion'][f_][4]), max(0, PF['aifoundry3']['sram'][f_][4])
    print(f'   largest 100 MHz board step allowed if the leakage law is {f_:5s}: '
          f'{5 / 6 * ((1 + k3m) * cm + (1 + k3s) * cs):.2f} W')
STEP_MAX = 5 / 6 * ((1 + k3m) * DCAP_M['aifoundry3'] + (1 + k3s) * DCAP_S['aifoundry3'])
print(f'TH-CL (rival): a clock-dependent idle power larger than any form of the idle law allows: the 100 MHz board step '
      f'> {STEP_MAX:.2f} W')
for f in LEVELS:
    x = 1 - f / 600
    dmr, dsr = x * Dm3, x * Ds3
    bd = (1 + k3m) * dmr + (1 + k3s) * dsr
    print(f'  600 -> {f:3d} MHz (TH-CS, joint draws), the fall in W: board {pct(bd)}; minion rail {pct(dmr)}; SRAM {pct(dsr)}; '
          f'NoC 0; unmetered {pct(k3m * dmr + k3s * dsr)}')
B56 = float(rail('aifoundry3', 'board', 56))
print(f'  (aifoundry3 idle board at 56 C by its E44 law: {B56:.2f} W; the largest allowed 100 MHz step is '
      f'{100 * STEP_MAX / B56:.0f}% of it)')
print(f'  under TH-CS the step does not depend on the die temperature, and the slope dP/dT is the same at every clock '
      f'(aifoundry3 board at 56 C: {LAW["aifoundry3"]["board"]["best"][2] / LAW["aifoundry3"]["board"]["best"][0] * math.exp((56 - 80) / LAW["aifoundry3"]["board"]["best"][0]):.3f} W/C)')

# ------------------------------------------------------------------------------------------------------------------
hdr('E. Stage B predictions: aifoundry3 at 100 MHz, idle, die at 56 C; minion then SRAM set-points stepped down')
# ------------------------------------------------------------------------------------------------------------------
nB = J_n


def low_rails(T_m, T_s, Dm, Ds, nn, vm, vs, f=100):
    """minion and SRAM idle rails at clock f and set-points vm, vs, from their 600 MHz / 525 / 700 mV values"""
    pm = (T_m - Dm) * (vm / 525) ** nn + Dm * (f / 600) * (vm / 525) ** 2
    ps = (T_s - Ds) * (vs / 700) ** nn + Ds * (f / 600) * (vs / 700) ** 2
    return pm, ps


Pm56, Ps56 = float(rail('aifoundry3', 'minion', 56)), float(rail('aifoundry3', 'sram', 56))
print(f'at 600 MHz, 525/700 mV, 56 C (E44 laws): minion {Pm56:.2f} W, SRAM {Ps56:.2f} W, board {B56:.2f} W')
print(f'TH-VS (the record, section C): leakage ~ V^n, n in [{N_LO:.2f}, {N_HI:.2f}]; TH-VD (FinFET DIBL, rival): '
      f'n in [1.4, {N_LO:.2f}); TH-VX (steeper): n > {N_HI:.2f}; TH-V0 (null, the reading does not follow the set-point): n <= 0.5')
for vm in (525, 500, 475, 450, 425, 400):
    pm, ps = low_rails(Pm56, Ps56, Dm3, Ds3, nB, vm, 700)
    brd = B56 - (1 + k3m) * (Pm56 - pm) - (1 + k3s) * (Ps56 - ps)
    print(f'  100 MHz, minion {vm} mV, SRAM 700: minion rail {pct(pm)} W; board {pct(brd)} W')
for vs in (700, 680, 660):
    pm, ps = low_rails(Pm56, Ps56, Dm3, Ds3, nB, 400, vs)
    brd = B56 - (1 + k3m) * (Pm56 - pm) - (1 + k3s) * (Ps56 - ps)
    print(f'  100 MHz, minion 400 mV, SRAM {vs}: SRAM rail {pct(ps)} W; board {pct(brd)} W')
for nn_lab, nn in (('TH-VD n = 1.8', 1.8), ('TH-V0 n = 0', 0.0)):
    pm, ps = low_rails(Pm56, Ps56, Dm3_best, Ds3_best, nn, 400, 660)
    print(f'  under {nn_lab}: board at 100 MHz, 400/660 mV: {B56 - (1 + k3m) * (Pm56 - pm) - (1 + k3s) * (Ps56 - ps):.2f} W')
pm, ps = low_rails(Pm56, Ps56, Dm3, Ds3, nB, 400, 660)
low56 = B56 - (1 + k3m) * (Pm56 - pm) - (1 + k3s) * (Ps56 - ps)
print(f'=> lowest settable point (100 MHz, 400/660 mV) at 56 C: board {pct(low56)} W against {B56:.2f} W at 600 MHz '
      f'({pct(100 * (1 - low56 / B56), f="%.0f")} % less); minion rail {pct(pm)} W, SRAM rail {pct(ps)} W')
print(f'   C-METER (board change per minion-rail change while only the minion set-point moves): a true meter gives 1 + k_m = '
      f'{1 + k3m:.3f}; a meter reading the current at a fixed voltage gives (1 + k_m) n/(n - 1) = '
      f'{(1 + k3m) * N_HI / (N_HI - 1):.2f} .. {(1 + k3m) * N_LO / (N_LO - 1):.2f} over the n band; registered pass band [0.9, 1.6]')
print(f'   compare (measured, different card and firmware): aifoundry1 card 0 idles at 300 MHz, 400/660 mV: 17.97 W at 62 C '
      f'(card0_guard.out); minion 4.11, SRAM 0.88, NoC 2.75 W')

# ------------------------------------------------------------------------------------------------------------------
hdr('F. The bare card at the low point (nohs_calc.py imported: its model, ranges and functions)')
# ------------------------------------------------------------------------------------------------------------------
sys.path.insert(0, NOHS)
sys.dont_write_bytecode = True
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    import nohs_calc as M  # noqa: E402  (runs the whole model, seed 20260929)
_ref = os.path.join(NOHS, 'nohs_calc.out')
print('nohs_calc.py reproduces nohs_calc.out: ' + ('yes' if _buf.getvalue() == open(_ref).read() else 'NO (model changed)'))

# A low-point board law for aifoundry3: its board law (nohs_calc LAWS) minus the rails' drop at every T.
_P_board_orig = M.P_board
LOW = {}


def _low_board(key, T):
    Dm, Ds, nn, vm, vs, f = LOW[key]
    T = np.asarray(T, dtype=float)
    Pm_T = rail('aifoundry3', 'minion', T)
    Ps_T = rail('aifoundry3', 'sram', T)
    pm, ps = low_rails(Pm_T, Ps_T, Dm, Ds, nn, vm, vs, f)
    return _P_board_orig('aifoundry3', T) - (1 + k3m) * (Pm_T - pm) - (1 + k3s) * (Ps_T - ps)


def P_board_patched(card, T, TL_c0=30.0):
    return _low_board(card, T) if card in LOW else _P_board_orig(card, T, TL_c0)


M.P_board = P_board_patched
LOW['a3@600'] = (0.0, 0.0, 2.0, 525, 700, 600)            # identity: the 600 MHz law itself (check)
assert abs(float(M.P_board('a3@600', 56.0)) - float(_P_board_orig('aifoundry3', 56.0))) < 1e-9
M.IDLE_PT['a3@600'] = 56.0
M.P_OFF['a3@600'] = M.P_OFF['aifoundry3']


def add_low(key, Dm, Ds, nn, vm=400, vs=660, f=100):
    LOW[key] = (Dm, Ds, nn, vm, vs, f)
    M.IDLE_PT[key] = 56.0
    pm, ps = low_rails(float(rail('aifoundry3', 'minion', 56)), float(rail('aifoundry3', 'sram', 56)), Dm, Ds, nn, vm, vs, f)
    doff = k3m * (Pm56 - pm) + k3s * (Ps56 - ps)          # the regulators' loss falls with the rails; it is off the die
    lo, hi = M.P_OFF['aifoundry3']
    M.P_OFF[key] = (lo - doff, hi - doff)


i_lo = int(np.argmin(np.abs(J_dm3 - np.percentile(J_dm3, 5))))
i_md = int(np.argmin(np.abs(J_dm3 - np.percentile(J_dm3, 50))))
i_hi = int(np.argmin(np.abs(J_dm3 - np.percentile(J_dm3, 95))))
SCEN = [('clock only, 100 MHz, 525/700 mV, D at its largest', DCAP_M['aifoundry3'], DCAP_S['aifoundry3'], N_MID, 525, 700, 100)]
for lab_, ii in (('small D, steep n', i_lo), ('central', i_md), ('large D, shallow n', i_hi)):
    SCEN.append((f'100 MHz, 400/660 mV, {lab_} (D_m {J_dm3[ii]:.2f} W, n {J_n[ii]:.2f})', float(J_dm3[ii]),
                 float(J_ds3[ii]), float(J_n[ii]), 400, 660, 100))
SCEN.append(('100 MHz, 400/660 mV, rival TH-VD n = 1.8, D best fit', Dm3_best, Ds3_best, 1.8, 400, 660, 100))
for i, sc in enumerate(SCEN):
    add_low(f'low{i}', *sc[1:])
keys = ['a3@600'] + [f'low{i}' for i in range(len(SCEN))]
labs = ['600 MHz, 525/700 mV (the card as it is)'] + [s[0] for s in SCEN]
print('board / SoC power and board slope at 56 C, per scenario (SoC = board - off-die, off-die = nohs P_OFF less the regulator-loss cut):')
for k, lab in zip(keys, labs):
    b = float(M.P_board(k, 56.0))
    sl = float((M.P_board(k, 57.0) - M.P_board(k, 55.0)) / 2)
    lo, hi = M.P_OFF[k]
    print(f'  {lab:66s} board {b:5.2f} W, SoC {b - hi:5.2f}-{b - lo:5.2f} W, slope {sl:.3f} W/C (at 80 C '
          f'{float((M.P_board(k, 81.0) - M.P_board(k, 79.0)) / 2):.3f})')


def theta_eq_cap(card, Ta, Poff, fs, cap_c):
    """largest theta (SoC basis) whose stable equilibrium is <= cap_c (bisection on nohs_calc.equilibria)"""
    lo, hi = 0.05, 30.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        s_, _t = M.equilibria(card, mid, Ta, Poff, fs)
        if s_ is not None and s_ <= cap_c:
            lo = mid
        else:
            hi = mid
    return lo


print('largest theta_JA (SoC basis, C/W) with any stable idle equilibrium | with one at or below 70 C '
      '(best case Ta 22, off-die high, slope share 0.80 .. worst Ta 30, off-die low, share 0.95):')
for k, lab in zip(keys, labs):
    lo, hi = M.P_OFF[k]
    a = [M.theta_max(k, Ta, Poff, fs) for Ta, Poff, fs in ((22, hi, 0.80), (30, lo, 0.95))]
    c = [theta_eq_cap(k, Ta, Poff, fs, 70.0) for Ta, Poff, fs in ((22, hi, 0.80), (30, lo, 0.95))]
    print(f'  {lab:66s} any: {a[1]:.2f} .. {a[0]:.2f} | <= 70 C: {c[1]:.2f} .. {c[0]:.2f}')
print(f'bare theta_JA classes (nohs_calc B, physics 5/50/95 %): still {pct(M.th_still)}, fan 1-2.5 m/s {pct(M.th_fan)}; '
      f'ranges carried forward {M.TH_STILL} and {M.TH_FAN}')
# A stronger blower, by nohs_calc's own formulas (ASSUMED 3-6 m/s at the lid, same boost and board model)
u6 = rng.uniform(3.0, 6.0, M.N)
h_lid_b = M.h_forced(u6, 0.045, M.boost) + M.h_rad(M.eps_lid, M.Tlid_s, M.Ta_s)
h_pcb_b = M.h_forced(u6, 0.17, M.boost) + M.h_rad(M.eps_pcb, M.Tpcb_s, M.Ta_s)
th_blow, _, rba_blow, _ = M.theta_JA(h_lid_b, h_pcb_b)
print(f'  a blower at 3-6 m/s (ASSUMED speed; nohs_calc formulas): theta_JA {pct(th_blow)} C/W (the board path, theta_JB 1-3 C/W, sets the floor); '
      f'its board-to-air resistance R_BA {pct(rba_blow)} C/W')

print('Monte Carlo as nohs_calc D (theta log-uniform, Ta 22-30, off-die and slope share in range; 600 draws per row): '
      'share with a stable equilibrium, share with it <= 70 C, T_eq 5/50/95 %')
CLASSES = (('still', M.TH_STILL), ('fan', M.TH_FAN), ('blower', (float(np.percentile(th_blow, 5)), float(np.percentile(th_blow, 95)))))
for k, lab in zip(keys, labs):
    for cname, rngth in CLASSES:
        nn_ = 600
        th = np.exp(rng.uniform(math.log(rngth[0]), math.log(rngth[1]), nn_))
        Ta = rng.uniform(22, 30, nn_)
        Poff = rng.uniform(*M.P_OFF[k], nn_)
        fs = rng.uniform(*M.F_SLOPE, nn_)
        eq = np.array([(lambda r: np.nan if r[0] is None else r[0])(M.equilibria(k, th[i], Ta[i], Poff[i], fs[i])) for i in range(nn_)])
        good = np.isfinite(eq)
        print(f'  {lab:66s} {cname:6s}: equilibrium {good.mean():5.0%} ({good.sum()} of {nn_}); <= 70 C {np.mean(eq <= 70):5.0%}; '
              f'T_eq {pct(eq[good]) if good.any() else "none"}')


def power_on(k_low, air, n_draws=300, t_set_extra=(20.0, 60.0), t_end=1800.0):
    """nohs_calc E's two-node model: 600 MHz idle from a cold power-on for the host boot (U(30, 90) s, nohs_calc's
    ASSUMED boot window) plus the time to set the low point (t_set_extra, ASSUMED), then the low point until t_end.
    Returns the peak die temperature and the temperature at t_end."""
    thJB = np.exp(rng.uniform(math.log(1.0), math.log(3.0), n_draws))
    if air == 'still':
        Rlid = 1.0 / (rng.uniform(8, 15, n_draws) * M.A_LID) + rng.uniform(0.03, 0.10, n_draws)
        RBA = np.exp(rng.uniform(math.log(2.5), math.log(8.0), n_draws))
    elif air == 'fan':
        Rlid = 1.0 / (rng.uniform(20, 50, n_draws) * M.A_LID) + rng.uniform(0.03, 0.10, n_draws)
        RBA = np.exp(rng.uniform(math.log(0.8), math.log(3.0), n_draws))
    else:   # blower: lid h from the 3-6 m/s formula's 5-95 % range; board fin from the same formulas' 5-95 % R_BA
        #         (revised 30 Sep, review: it was an ASSUMED 0.5-1.5 C/W, about half what the formulas give)
        hl = M.h_forced(np.array([3.0, 6.0]), 0.045, np.array([1.2, 2.0]))
        Rlid = 1.0 / (rng.uniform(hl[0], hl[1], n_draws) * M.A_LID) + rng.uniform(0.03, 0.10, n_draws)
        rb = np.percentile(rba_blow, [5, 95])
        RBA = np.exp(rng.uniform(math.log(rb[0]), math.log(rb[1]), n_draws))
    CJ, CB = rng.uniform(9, 18, n_draws), rng.uniform(30, 80, n_draws)
    Ta = rng.uniform(22, 30, n_draws)
    lo, hi = M.P_OFF['aifoundry3']
    u = rng.uniform(0, 1, n_draws)
    Poff6 = lo + u * (hi - lo)
    lo2, hi2 = M.P_OFF[k_low]
    Poffl = lo2 + u * (hi2 - lo2)
    fs = rng.uniform(*M.F_SLOPE, n_draws)
    phi = rng.uniform(0.3, 1.0, n_draws)
    tset = rng.uniform(30, 90, n_draws) + rng.uniform(*t_set_extra, n_draws)
    peak, fin = [], []
    for i in range(n_draws):
        def rhs(t, y):
            TJ, TB = y
            if t < tset[i]:
                P, po = max(M.soc_power('aifoundry3', TJ, Poff6[i], fs[i]), 0.0), Poff6[i]
            else:
                P, po = max(M.soc_power(k_low, TJ, Poffl[i], fs[i]), 0.0), Poffl[i]
            q = (TJ - TB) / thJB[i]
            return [(P - q - (TJ - Ta[i]) / Rlid[i]) / CJ[i], (phi[i] * po + q - (TB - Ta[i]) / RBA[i]) / CB[i]]
        cap = lambda t, y: y[0] - 150.0
        cap.terminal, cap.direction = True, 1
        s = solve_ivp(rhs, (0, t_end), [Ta[i], Ta[i]], events=[cap], max_step=1.0)
        peak.append(min(float(np.max(s.y[0])), 150.0))
        fin.append(150.0 if s.status == 1 else float(s.y[0][-1]))
    return np.array(peak), np.array(fin)


print('POWER-ON: cold start at 600 MHz idle for the host boot (30-90 s) + 20-60 s to set the low point, then the low point '
      'to 30 min; 300 draws each: peak die C, die C at 30 min, share whose peak stays below 80 C (the stop) and whose '
      'end is <= 70 C')
for k, lab in zip(keys[1:], labs[1:]):
    if 'central' not in lab:
        continue
    for air in ('still', 'fan', 'blower'):
        pk, fn = power_on(k, air)
        print(f'  {lab} | {air:6s}: peak {pct(pk)} C; at 30 min {pct(fn)} C; peak < 80: {np.mean(pk < 80):.0%}; '
              f'end <= 70: {np.mean(fn <= 70):.0%}; both: {np.mean((pk < 80) & (fn <= 70)):.0%}')

# ------------------------------------------------------------------------------------------------------------------
hdr("G. Detection: a same-temperature idle step's noise on aifoundry3 (E44 idle tails), and what the passes resolve")
# ------------------------------------------------------------------------------------------------------------------
# From the last 240 s of each E44 idle cycle on aifoundry3 (die within 2 C): the difference of two 2.5 s means of
# board_w (the 'before' and 'after' windows of a step) 2.5 s apart, minus the same difference predicted by a straight
# line over those 240 s (the drift an up/down pair cancels).
D_null, D_null_m = [], []
for pd in sorted(glob.glob(os.path.join(V3RAW, 'aifoundry3', 'idle', 'p*'))):
    S = []
    with gzip.open(os.path.join(pd, 'telemetry.jsonl.gz'), 'rt') as fh:
        for line in fh:
            s = json.loads(line)
            if (s.get('mhz') or {}).get('minion') == 600:
                S.append((s['t_ms'] / 1e3, s['board_w'], s['temp_c']['minshire'][0], s['sp']['minion_w'][0]))
    if not S:
        continue
    S = np.array(S)
    tail = S[S[:, 0] >= S[-1, 0] - 240]
    if tail[:, 2].max() - tail[:, 2].min() > 2:
        continue
    p = np.polyfit(tail[:, 0], tail[:, 1], 1)
    pm_ = np.polyfit(tail[:, 0], tail[:, 3], 1)
    t0 = tail[0, 0]
    while t0 + 7.5 <= tail[-1, 0]:
        a = tail[(tail[:, 0] >= t0) & (tail[:, 0] < t0 + 2.5)]
        b = tail[(tail[:, 0] >= t0 + 5.0) & (tail[:, 0] < t0 + 7.5)]
        if len(a) >= 5 and len(b) >= 5:
            D_null.append((a[:, 1].mean() - b[:, 1].mean()) - (np.polyval(p, a[:, 0]).mean() - np.polyval(p, b[:, 0]).mean()))
            D_null_m.append((a[:, 3].mean() - b[:, 3].mean()) - (np.polyval(pm_, a[:, 0]).mean() - np.polyval(pm_, b[:, 0]).mean()))
        t0 += 7.5
D_null = np.array(D_null)
if len(D_null):
    sd = float(np.std(D_null, ddof=1))
    print(f'{len(D_null)} null steps: board SD {sd * 1e3:.0f} mW per step, minion rail SD {np.std(D_null_m, ddof=1) * 1e3:.0f} mW '
          f'(its ~1 s filter smooths it)  [measured noise, E44 aifoundry3 idle tails]')
    for nsteps in (2, 4, 8):
        print(f'  mean of {nsteps} steps (up and down in {nsteps // 2} passes): SE {sd / math.sqrt(nsteps) * 1e3:.0f} mW; '
              f'a step of {3 * sd / math.sqrt(nsteps) * 1e3:.0f} mW is 3 SE')
else:
    print('no idle tail qualified')

# ------------------------------------------------------------------------------------------------------------------
hdr('I. The load item (A3) and the low-point dwell (B-DWELL): predictions')
# ------------------------------------------------------------------------------------------------------------------
DV = json.load(open(os.path.join(DATA, '2026-09-22-dvfs-aifoundry2', 'dvfs.json')))
pat = {p_['values']: p_['a3'] for p_ in DV['cards']['patterns']}
print(f'switching power over idle on aifoundry3 at 600 MHz, 525 mV, 1,024 minions (measured, E20: dvfs.json cards.patterns, '
      f'launch at {DV["cards"]["launch"]["aifoundry3"]["T"]:.1f} C): random normal {pat["randn"]:.2f} W, ones {pat["ones"]:.2f} W, zeros {pat["zeros"]:.2f} W')
print('TH-E1 (energy per operation fixed at fixed voltage): switching power scales as f; at a lower voltage as f V^2')
for f in (600, 300, 100):
    print(f'  {f:3d} MHz, 525 mV: random normal {pat["randn"] * f / 600:5.2f} W, ones {pat["ones"] * f / 600:5.2f} W')
for vm in (400,):
    sw = pat['randn'] * (100 / 600) * (vm / 525) ** 2
    print(f'  100 MHz, {vm} mV: random normal {sw:.2f} W in all, {sw / 32 * 1e3:.0f} mW per compute shire (32); '
          f'ones {pat["ones"] * (100 / 600) * (vm / 525) ** 2:.2f} W')
# the settled idle temperature at the low point with the heatsink on: T = Ta + theta_eff * P(T), theta_eff from the card's
# own rest at 600 MHz (56 C at the E44 law's 25.29 W; ambient 22-28 C as nohs_calc C)
for k, lab in zip(keys[1:], labs[1:]):
    if 'central' not in lab:
        continue
    for Ta in (22.0, 28.0):
        th_eff = (56.0 - Ta) / B56
        T = 56.0
        for _ in range(200):
            T = Ta + th_eff * float(M.P_board(k, T))
        sl = float((M.P_board(k, T + 1) - M.P_board(k, T - 1)) / 2)
        print(f'  heatsink on, {lab}: settles at {T:.1f} C (ambient {Ta:.0f} C, theta_eff {th_eff:.2f} C/W, board basis); '
              f'board {float(M.P_board(k, T)):.2f} W, slope there {sl:.3f} W/C')

# ------------------------------------------------------------------------------------------------------------------
hdr('H. The schedule (plan arithmetic; timings ASSUMED from NV DESIGN.md s6 and nv.json timing_s)')
# ------------------------------------------------------------------------------------------------------------------
W = 9.0 + 2.0 + 1.0          # one ettelem window: --seconds 9, first line <= 2 s, 1 s between windows (nv.json)
C = 1.0                      # one dev_mngt_service call (ASSUMED 1 s; each is capped at timeout -k 3 10)
K1 = 5.0                     # one verification launch (memhier/sparsity, 1-3 s of work, capped at 10 s)
seg = 2 * C + 2 * W          # set, read-back, two windows
a0 = 6 * C + K1 + 2 * W      # APM off (+ the quieting set on S1), read-backs, a 600 MHz launch, windows
a1 = 5 * (2 * C + W + K1 + W)
a2 = 4 * (9 * seg) + 3 * 60
a3 = 3 * (2 * C + 3 * W) + 2 * C
a4 = 2 * (150.0 + 5 * seg) + 60
ar = 4 * C + K1 + W
b1 = 3 * C + 2 * W
bl = (5 + 5) * (3 * C + W + K1 + W)
bs_ = 4 * (3 * C + W + K1 + W)
br = 6 * C + K1 + W
bd = 600.0                   # B-DWELL: 10 min idle at the lowest point (windows back to back)
s0 = 12 * C + 6 * W          # Stage 0: about twelve read-only calls (identity, uptime, table, clocks, voltages, TDP,
                             # threshold, residency, uptime, sptrace) and six baseline windows
print(f'Stage 0 (read-only): {s0 / 60:.1f} min of card time')
print(f'segment (set, read-back, two windows) {seg:.0f} s; a pass of 9 segments {9 * seg / 60:.1f} min')
print(f'Stage A: quieting and checks {a0 / 60:.1f} min, probe {a1 / 60:.1f}, 4 passes {a2 / 60:.1f}, load {a3 / 60:.1f}, '
      f'hot {a4 / 60:.1f}, restore {ar / 60:.1f}: {(a0 + a1 + a2 + a3 + a4 + ar) / 60:.0f} min of card time '
      f'({(a0 + a1 + a2 + ar) / 60:.0f} min without the optional load and hot items)')
print(f'Stage B: first write {b1 / 60:.1f} min, minion ladder down and up {bl / 60:.1f}, SRAM ladder {bs_ / 60:.1f}, '
      f'dwell at the lowest point {bd / 60:.0f}, restore {br / 60:.1f}: {(b1 + bl + bs_ + bd + br) / 60:.0f} min of card time')
print(f'writes: SET_FREQUENCY about {5 + 4 * 8 + 4 + 2 * 4 + 2}: each also re-locks the NoC PLL at 400 MHz (stock CLI); '
      f'SET_MODULE_VOLTAGE {1 + 10 + 4 + 2}; SET_MODULE_ACTIVE_POWER_MANAGEMENT 2')

# ------------------------------------------------------------------------------------------------------------------
hdr('J. The gap between two sampler windows: how much the die moves before the after-window starts')
# ------------------------------------------------------------------------------------------------------------------
# A step is read from the last 2.5 s of the window before the set and the first 2.5 s of the window after it; the
# two are 2-4 s apart (the set's dev_mngt_service call and a sampler start, nv.json timing). In that gap the die
# answers the power step through the fast thermal stages, and the leakage follows. Fast stages: nohs_calc.py's Foster
# chain (aifoundry2's, 11-thermal-model.md; ASSUMED similar on aifoundry3); slope: aifoundry3's board law at 56 C.
sl56 = LAW['aifoundry3']['board']['best'][2] / LAW['aifoundry3']['board']['best'][0] * math.exp((56 - 80) / LAW['aifoundry3']['board']['best'][0])
for gap in (2.0, 3.0, 4.0):
    mid = gap + 1.25                                   # the after-window's 2.5 s average sits 1.25 s past its start
    dT = sum(r * (1 - math.exp(-mid / t)) for t, r in zip(M.taus, M.Rs))
    print(f'  gap {gap:.0f} s: the die moves {dT:.3f} C per W of SoC step by the after-window; with the board slope {sl56:.3f} W/C '
          f'the step reads {100 * dT * sl56:.1f}% large (each direction; up and down steps do not cancel it)')
for k, lab in zip(keys[:2], labs[:2]):
    for Ta in (22.0, 28.0):
        th_eff = (56.0 - Ta) / B56
        T = 56.0
        for _ in range(200):
            T = Ta + th_eff * float(M.P_board(k, T))
        print(f'  heatsink on, {lab}: settles at {T:.1f} C (ambient {Ta:.0f} C), board {float(M.P_board(k, T)):.2f} W')

# ------------------------------------------------------------------------------------------------------------------
hdr('K. The envelope model (lowclock_calc.py, its JSON) restated as Stage A and B predictions, beside this plan\'s')
# ------------------------------------------------------------------------------------------------------------------
# The envelope model fits a shared minion clock tree and kappa in G(V) = (V/V0) exp(kappa (V - V0)) to two anchors:
# aifoundry2's 800/600 MHz idle and card 0's 300 MHz rails; its SRAM kappa is a prior (1.4-10 per volt, no anchor).
# Read here from lowclock_calc.json (5/50/95 % per quantity; percentiles of a monotone function are mapped directly,
# and quantities from different percentiles are not combined into a joint draw).
EMJ = os.path.join(NOHS, 'lowclock_calc.json')
if not os.path.exists(EMJ):
    print(f'lowclock_calc.json not found at {EMJ}: section K skipped')
else:
    E = json.load(open(EMJ))
    OP = E['operating_points']
    b600 = OP['aifoundry3|600|boot']['board_W']
    print('Stage A, the 600 -> f idle board step on aifoundry3 (the envelope model: only the fitted clock tree follows the clock; '
          'T-independent), against this plan\'s TH-CS joint draws (section D):')
    for f in (400, 300, 200, 100):
        bf = OP[f'aifoundry3|{f}|boot']['board_W']['60']
        st_ = [b600['60'][1] - x for x in reversed(bf)]
        print(f'  600 -> {f:3d} MHz: envelope model {st_[0]:.2f} / {st_[1]:.2f} / {st_[2]:.2f} W')
    ct = E['decomposition']['aifoundry3|56']['clock_tree']
    print(f'  (its aifoundry3 clock tree at 600 MHz, minion + SRAM with their regulator loss: {ct[0]:.2f} / {ct[1]:.2f} / {ct[2]:.2f} W; '
          f'x5/6 = {5 / 6 * ct[0]:.2f} / {5 / 6 * ct[1]:.2f} / {5 / 6 * ct[2]:.2f} W)')
    # minion leakage exponent equivalent to the envelope model's G(V), over Stage B's six set-points (525 .. 400 mV),
    # as B-N will fit it: least-squares slope of ln G against ln(V/525); on-die = set-point - 3 mV (aifoundry3 522 at 525)
    vset = np.array([525, 500, 475, 450, 425, 400], dtype=float)
    vdie = (vset - 3.0) / 1000.0
    x = np.log(vset / 525.0)
    km_ = E['anchors']['kappa_m']
    neq = []
    for kap in km_:
        lnG = np.log(vdie / vdie[0]) + kap * (vdie - vdie[0])
        neq.append(float(np.polyfit(x, lnG, 1)[0]))
    Gm = [float((0.397 / 0.522) * math.exp(k_ * (0.397 - 0.522))) for k_ in km_]
    print(f'Stage B, the minion leakage exponent (B-N): envelope model kappa {km_[0]:.2f} / {km_[1]:.2f} / {km_[2]:.2f} per volt '
          f'-> equivalent n over 525..400 mV: {neq[0]:.2f} / {neq[1]:.2f} / {neq[2]:.2f}; '
          f'leakage factor 525 -> 400 mV x{Gm[0]:.3f} / x{Gm[1]:.3f} / x{Gm[2]:.3f}')
    print(f'   this plan (section C): n {N_LO:.2f} .. {N_HI:.2f}, central {N_MID:.2f}; overlap of the two: '
          f'{max(N_LO, neq[0]):.2f} .. {min(N_HI, neq[2]):.2f}')
    gs = E['anchors']['G_sram_660mV']
    ns_eq = [math.log(g) / math.log(660 / 704) for g in gs]
    print(f'Stage B, the SRAM exponent (B-NS): envelope model SRAM leakage at 660 over 704 mV x{gs[0]:.3f} / x{gs[1]:.3f} / x{gs[2]:.3f} '
          f'(a wide prior, held only by the SRAM rail\'s part of the 800 MHz step) -> equivalent n_SRAM {min(ns_eq):.1f} / {ns_eq[1]:.1f} / {max(ns_eq):.1f}; this plan assumes n_SRAM = n')
    # the lowest settable point at 56 C: the envelope model gives 25/40/60 C; interpolate with an exponential slope
    fl = OP['aifoundry3|100|floor']
    s40, s60 = fl['dPdT_board']['40'][1], fl['dPdT_board']['60'][1]
    TLs = 20.0 / math.log(s60 / s40)
    drop = s60 * TLs * (1 - math.exp(-4.0 / TLs))
    low_em = [p_ - drop for p_ in fl['board_W']['60']]
    s56 = s60 * math.exp(-4.0 / TLs)
    print(f'Stage B, the lowest settable point (B-LOW) at 56 C: envelope model {low_em[0]:.2f} / {low_em[1]:.2f} / {low_em[2]:.2f} W '
          f'(its 60 C values {fl["board_W"]["60"][0]:.2f} / {fl["board_W"]["60"][1]:.2f} / {fl["board_W"]["60"][2]:.2f} W less '
          f'{drop:.2f} W, interpolated with its median slopes at 40 and 60 C, T_L {TLs:.1f} C); board slope at 56 C {s56:.3f} W/C')
    print(f'   this plan (section E): {pct(low56)} W; registered B-LOW band [18.4, 20.1] W')
    b600_56 = E['decomposition']['aifoundry3|56']['board'][1]
    print(f'   (both models start from the same 600 MHz law: envelope model {b600_56:.2f} W at 56 C, this plan {B56:.2f} W)')
print('done')
