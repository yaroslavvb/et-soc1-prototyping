#!/usr/bin/env python3
"""MM1-v2: aifoundry2's governor clock model (post hoc), and the rest law per card. Desk; numpy, scipy.

    /usr/bin/python3 -I -B governor_v2.py --core <dir with mm1_v2_params_core.json> --out <dir>
        writes <dir>/governor_v2.json (the fitted constants, every E208 aifoundry2 run's simulated and measured clock, the fit's errors) and
        <dir>/rest_v2.json (the rest law per card and its error on E208's rests).

THE GOVERNOR, as the lab's findings document it (docs/findings/16-dvfs-and-leakage.md, "The loop"; 14-card-behaviour.md, "Which limit acts,
read from the governor's own log", E64), on aifoundry2 card 0 as E208 read its config (TDP 65 W, temperature threshold 65 C, power state 3):
  - three operating points, 600 / 700 / 800 MHz at 0.517 / 0.568 / 0.618 V; each process starts at the 600 MHz boot point and the governor
    climbs to the top point (E208: 800 MHz launches from about 0.5-1.0 s into each process);
  - once per pass of the device-management task (dt, about 0.16 s under a 10 Hz sampler: E41), thermal first: the shires' mean die above
    65 C steps the clock down one point; else the power test on a first-order running average of the board power (time constant tau; E64:
    1.3 s) against the TDP: above, step down one point; below, step up one point; no dead band;
  - the board power at each point is the run's rest plus its W over idle at that clock (v2's own energy model; the given-clock route).
FITTED (post hoc, on E208's aifoundry2 runs only: S1 and S2, every run with launches, the 'time' runs included): the climb time t_climb, the
  average's time constant tau and the power threshold P_th, by least squares on each run's measured fraction of launches in the 800 MHz band
  1.0 s or more after its process's first launch (frac_800_after_step; the reducer's capped rule is this fraction under 0.8) and its burst
  view's mean kernel clock; each run's power at 800 MHz from its own launches (the 90th percentile of the launches' board power at or above
  790 MHz), at 700 and 600 MHz scaled by v2's W(f) / W(800). The die's rise over a burst: a line in the board power over the rest, fitted on
  the same runs' die at most against their start (for the thermal test; no E208 run on this card came within 6 C of 65 C).
THE CLOCK FORECAST for a run (forecast_clock): the same loop driven by v2's own forecast powers (the rest law's rest + v2's W at each point),
  over the run's processes (6 s each): the 800 MHz share after 1.0 s, capped or not (under 0.8), the burst's mean clock, and the clock of
  the reducer's 'win' view (the 800 MHz launches 1.0-3.5 s into each process: 800 MHz whenever any launch there holds the top point).
THE REST LAW: P_rest(T0) per card at the run's start die: ledger v2's frozen footing quads for aifoundry2, aifoundry3 and card 1
  (inputs/v1/ledger_frozen-v2.json); card 0 has none, so a line through E208's card-0 rests (post hoc). REPORTED: the scored J at rest uses
  the run's measured rest.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_e208 as D8  # noqa: E402
import kinds_v2 as K  # noqa: E402
import mm1_v2 as M2  # noqa: E402

PTS = [600.0, 700.0, 800.0]
DT = 0.16
T_PROC = 6.0
DIE_TH = 65.0


def simulate(P_of, P_rest, die0, prm, t_proc=T_PROC, dt=DT):
    """one process: clock trace on a 10 ms grid; returns (t, f, die) arrays. P_of: {600: W, 700: W, 800: W} board power at each point"""
    tc, tau, Pth, kdie = prm['t_climb'], prm['tau'], prm['P_th'], prm['k_die']
    n = int(round(t_proc / 0.01))
    t = np.arange(n) * 0.01
    f = np.empty(n)
    die = np.empty(n)
    cur = 600.0
    Pavg = P_rest
    next_pass = tc
    climbed = False
    for i in range(n):
        if t[i] >= next_pass - 1e-9:
            d = die0 + kdie * (Pavg - P_rest)
            if not climbed:
                cur = 800.0 if (Pavg < Pth and d <= DIE_TH) else 700.0
                climbed = True
            elif d > DIE_TH and cur > 600.0:
                cur -= 100.0
            elif Pavg > Pth and cur > 600.0:
                cur -= 100.0
            elif Pavg < Pth and cur < 800.0:
                cur += 100.0
            next_pass += dt
        P = P_of[cur]
        Pavg += (P - Pavg) * (1.0 - np.exp(-0.01 / tau))
        f[i] = cur
        die[i] = die0 + kdie * (Pavg - P_rest)
    return t, f, die


def summarize(t, f, launch_s=0.44):
    """the reducer's quantities from a clock trace: launches of launch_s tile the process; each launch's clock = its time-average"""
    nL = max(int(T_PROC / launch_s), 1)
    clocks, starts = [], []
    for k in range(nL):
        a, b = k * launch_s, min((k + 1) * launch_s, T_PROC)
        m = (t >= a) & (t < b)
        if m.any():
            clocks.append(float(np.mean(f[m])))
            starts.append(a)
    clocks = np.array(clocks)
    starts = np.array(starts)
    after = clocks[starts >= 1.0]
    frac = float(np.mean(after >= 790.0)) if len(after) else 0.0
    win = clocks[(starts >= 1.0) & (starts <= 3.5) & (clocks >= 790.0)]
    return {'frac_800_after_1s': frac, 'capped': frac < 0.8, 'f_burst_mean': float(np.mean(clocks)), 'f_after_1s_mean': float(np.mean(after)) if len(after) else None,
            'f_win': (800.0 if len(win) else None), 'n_launch_win': int(len(win))}


def w_at(M, r, f):
    o = M.predict(r['card'], r['arm'], r['fmt'], r['kind'], r['mask'], f, ops=r['ops'], minions=r['minions'])
    return o.get('W_over_idle')


def run_inputs(M, R):
    """per aifoundry2 run: the measured targets and the powers that drive the loop"""
    out = []
    for r in R:
        L = r['burst']['launches']
        if not L:
            continue
        t0 = {}
        for x in L:
            if x['launch'] == 0:
                t0[x['proc']] = x['t_start_ms']
        hi = [x['board_w'] for x in L if x['kclock_mhz'] and x['kclock_mhz'] >= 790 and x['board_w']]
        if not hi:
            continue
        P800m = float(np.percentile(hi, 90))
        rest = r.get('p_rest') or r['p_rest_plain_w']
        ws = {f: w_at(M, r, f) for f in PTS}
        if any(v is None for v in ws.values()):
            ws = {f: w_at(M, dict(r, kind='zeros'), f) for f in PTS}
        lw = float(np.median([x['wall_s'] for x in L if x.get('wall_s')]))
        out.append({'id': r['id'], 'arm': r['arm_e208'], 'role': r['role'], 'form': r['form'], 'capped': r['capped'], 'rest': rest, 'die0': r['die_start_c'],
                    'die_max': r['burst'].get('die_max_c') or r.get('die_max_c'), 'P800_meas': P800m, 'w_v2': ws, 'launch_s': lw,
                    'frac_meas': r.get('frac_800_after_step'), 'fbar_meas': r['burst'].get('kclock_mhz'), 'n_proc': len(t0)})
    return out


def P_of_run(x, scale=True):
    k = (x['P800_meas'] - x['rest']) / x['w_v2'][800.0] if scale else 1.0
    return {f: x['rest'] + k * x['w_v2'][f] for f in PTS}


def fit(X, kdie):
    def res(q):
        prm = {'t_climb': q[0], 'tau': q[1], 'P_th': q[2], 'k_die': kdie}
        e = []
        for x in X:
            t, f, d = simulate(P_of_run(x), x['rest'], x['die0'], prm)
            s = summarize(t, f, x['launch_s'])
            e.append((s['frac_800_after_1s'] - x['frac_meas']) if x['frac_meas'] is not None else 0.0)
            e.append((s['f_burst_mean'] - x['fbar_meas']) / 50.0)
        return np.array(e)
    r = least_squares(res, [0.7, 1.3, 65.0], bounds=([0.1, 0.2, 55.0], [2.0, 5.0, 75.0]), diff_step=[0.05, 0.05, 0.01])
    return {'t_climb': float(r.x[0]), 'tau': float(r.x[1]), 'P_th': float(r.x[2]), 'k_die': kdie, 'cost': float(r.cost)}


def forecast_clock(M, card, arm, fmt, kind, mask, prm, rest_law, die0=None, ops=None, minions=None, n_proc=1, e_res_spec=None, phi_spec=None):
    """the governor model driven by v2's own forecast powers: the run's clock forecast on aifoundry2 card 0"""
    rl = rest_law[card]
    T0 = die0 if die0 is not None else rl['T0_forecast_c']
    rest = rl['a'] * T0 * T0 + rl['b'] * T0 + rl['c']
    ws = {}
    for f in PTS:
        o = M.predict(card, arm, fmt, kind, mask, f, ops=ops, minions=minions, e_res_spec=e_res_spec, phi_spec=phi_spec)
        ws[f] = o.get('W_over_idle')
    if any(v is None for v in ws.values()):
        return {'note': 'energy NOT FORECAST, so the clock cannot be forecast by the power loop', 'f_win': None}
    P_of = {f: rest + ws[f] for f in PTS}
    o8 = M.predict(card, arm, fmt, kind, mask, 800.0, ops=ops, minions=minions, e_res_spec=e_res_spec, phi_spec=phi_spec)
    launch_s = max(min(0.44, (o8.get('seconds_per_gemm') or 0.44)), 0.05)
    t, f, d = simulate(P_of, rest, T0, prm)
    s = summarize(t, f, launch_s)
    s.update({'P_board_forecast_W': {str(int(k)): v for k, v in P_of.items()}, 'rest_forecast_W': rest, 'die0_forecast_c': T0,
              'die_max_forecast_c': float(np.max(d)), 'launch_s': launch_s})
    return s


def chain_powers(M, r, RL):
    """the forecast chain's powers for an E208 run: the rest law at the run's start die + v2's W over idle at each point"""
    rl = RL[r['card']]
    T0 = r['die_start_c']
    rest = rl['a'] * T0 * T0 + rl['b'] * T0 + rl['c']
    ws = {f: w_at(M, r, f) for f in PTS}
    if any(v is None for v in ws.values()):
        return None, None
    return {f: rest + ws[f] for f in PTS}, rest


def fit_chain(M, R, RL, prm):
    """THE CHAIN: the power threshold refitted with v2's own forecast powers in place of the measured ones (t_climb, tau and k_die kept),
    so that the clock forecast (v2's power -> the loop) reproduces E208's aifoundry2 capped split and burst clocks as well as it can. Post hoc.
    It absorbs v2's power bias in the high-power corner E208 left unread (its capped runs carry no registered energy figure)."""
    X = []
    for r in R:
        Pf, rest = chain_powers(M, r, RL)
        if Pf is None or not r['burst']['launches']:
            continue
        lw = float(np.median([x['wall_s'] for x in r['burst']['launches'] if x.get('wall_s')]))
        X.append((r, Pf, rest, lw))

    def res(q):
        pp = dict(prm, P_th=float(q[0]))
        e = []
        for r, Pf, rest, lw in X:
            t, f, d = simulate(Pf, rest, r['die_start_c'], pp)
            s_ = summarize(t, f, lw)
            e.append(s_['frac_800_after_1s'] - (r.get('frac_800_after_step') or 0.0))
            e.append((s_['f_burst_mean'] - (r['burst'].get('kclock_mhz') or s_['f_burst_mean'])) / 50.0)
        return np.array(e)
    grid = np.arange(60.0, 70.01, 0.1)
    costs = [float(np.sum(res([g]) ** 2)) for g in grid]
    best = float(grid[int(np.argmin(costs))])
    pp = dict(prm, P_th=best)
    agree, rows = 0, []
    for r, Pf, rest, lw in X:
        t, f, d = simulate(Pf, rest, r['die_start_c'], pp)
        s_ = summarize(t, f, lw)
        agree += (s_['capped'] == bool(r['capped']))
        rows.append({'id': r['id'], 'arm': r['arm_e208'], 'capped_meas': bool(r['capped']), 'capped_chain': s_['capped'], 'P800_chain': round(Pf[800.0], 2),
                     'fbar_meas': r['burst'].get('kclock_mhz'), 'fbar_chain': round(s_['f_burst_mean'], 1)})
    fe = np.array([x['fbar_chain'] - x['fbar_meas'] for x in rows if x['fbar_meas']])
    return pp, {'P_th_chain_W': best, 'grid_W': [60.0, 70.0, 0.1], 'capped_agree': f'{agree} of {len(rows)}',
                'f_burst_mean_rms_mhz': round(float(np.sqrt(np.mean(fe ** 2))), 2), 'f_burst_mean_bias_mhz': round(float(np.mean(fe)), 2), 'rows': rows}


def rest_laws(R):
    lv = K.LV2['idle_laws']
    out = {}
    for card, key in (('aifoundry2 card 0', 'aifoundry2'), ('aifoundry3 card 0', 'aifoundry3'), ('aifoundry1 card 1', 'aifoundry1-c1')):
        q = lv[key]['quad']
        out[card] = {'a': q['a'], 'b': q['b'], 'c': q['c'], 'source': f"ledger v2 frozen idle law {key} (footing law): {lv[key]['quad_source']}"}
    c0 = [r for r in R if r['card_key'] == 'a1c0' and 'p_rest' in r]
    x = np.array([r['die_start_c'] for r in c0])
    y = np.array([r['p_rest'] for r in c0])
    b, c = np.polyfit(x, y, 1)
    out['aifoundry1 card 0'] = {'a': 0.0, 'b': float(b), 'c': float(c), 'source': f'a line through E208 a1c0-S1 rests against the start die ({len(c0)} runs; post hoc)'}
    for card in out:
        cr = [r for r in R if r['card'] == card and 'p_rest' in r]
        out[card]['T0_forecast_c'] = float(np.median([r['die_start_c'] for r in cr])) if cr else 54.4
        e = [(out[card]['a'] * r['die_start_c'] ** 2 + out[card]['b'] * r['die_start_c'] + out[card]['c']) - r['p_rest'] for r in cr]
        out[card]['on_E208_rests'] = ({'n': len(e), 'mean_W': round(float(np.mean(e)), 3), 'rms_W': round(float(np.sqrt(np.mean(np.square(e)))), 3)} if e else None)
    out['aifoundry3 card 0']['T0_forecast_c'] = 54.4
    out['aifoundry3 card 0']['T0_how'] = "E206 arm A's median start die (MM1-v1's)"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--core', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    P = json.load(open(os.path.join(a.core, 'mm1_v2_params_core.json')))
    R = D8.runs()
    RL = rest_laws(R)
    P['rest_law'] = RL
    M = M2.Model(P)
    A2 = [r for r in R if r['card_key'] == 'a2c0']
    X = run_inputs(M, A2)
    dm = [(x['die_max'] - x['die0'], x['P800_meas'] - x['rest']) for x in X if x['die_max'] is not None]
    kdie = float(np.sum([a_ * b_ for a_, b_ in dm]) / np.sum([b_ * b_ for a_, b_ in dm]))
    prm = fit(X, kdie)
    rows = []
    for x in X:
        t, f, d = simulate(P_of_run(x), x['rest'], x['die0'], prm)
        s = summarize(t, f, x['launch_s'])
        rows.append({'id': x['id'], 'arm': x['arm'], 'role': x['role'], 'capped_meas': x['capped'], 'capped_sim': s['capped'], 'frac_meas': x['frac_meas'],
                     'frac_sim': round(s['frac_800_after_1s'], 3), 'fbar_meas': x['fbar_meas'], 'fbar_sim': round(s['f_burst_mean'], 1), 'P800_meas': round(x['P800_meas'], 2),
                     'rest': round(x['rest'], 2), 'die0': x['die0'], 'die_max_meas': x['die_max']})
    agree = sum(1 for r in rows if r['capped_meas'] == r['capped_sim'])
    fe = np.array([r['fbar_sim'] - r['fbar_meas'] for r in rows if r['fbar_meas']])
    res = {'what': "aifoundry2's governor clock model (post hoc, fitted on E208's aifoundry2 runs only)", 'python': sys.version.split()[0],
           'constants': prm, 'dt_s': DT, 't_proc_s': T_PROC, 'die_threshold_c': DIE_TH, 'points_mhz': PTS,
           'fit': {'n_runs': len(rows), 'capped_agree': f'{agree} of {len(rows)}', 'f_burst_mean_rms_mhz': round(float(np.sqrt(np.mean(fe ** 2))), 2),
                   'f_burst_mean_bias_mhz': round(float(np.mean(fe)), 2), 'k_die_c_per_w': kdie},
           'documented': {'TDP_W': 65.0, 'tau_s_E64': 1.3, 'temperature_threshold_c': 65.0, 'pass_s': 0.16}, 'rows': rows}
    json.dump(res, open(os.path.join(out, 'governor_v2.json'), 'w'), indent=1, default=float)
    json.dump(RL, open(os.path.join(out, 'rest_v2.json'), 'w'), indent=1, sort_keys=True)
    pc, chain = fit_chain(M, A2, RL, prm)
    res['chain'] = chain
    res['constants_chain'] = pc
    json.dump(res, open(os.path.join(out, 'governor_v2.json'), 'w'), indent=1, default=float)
    P['governor'] = {'card': 'aifoundry2 card 0', 'constants': pc, 'constants_measured_powers': prm, 'dt_s': DT, 't_proc_s': T_PROC,
                     'die_threshold_c': DIE_TH, 'points_mhz': PTS,
                     'label': ('post hoc, fitted on E208 aifoundry2 runs only (governor_v2.json); constants = the chain (P_th refitted with v2 forecast '
                               'powers: the clock forecast route); constants_measured_powers = the loop on measured powers')}
    print('chain', {k: v for k, v in chain.items() if k != 'rows'})
    P['model'] = 'MM1-v2'
    json.dump(P, open(os.path.join(out, 'mm1_v2_params.json'), 'w'), indent=1, sort_keys=True)
    print('governor', prm, res['fit'])
    print('rest', {k: v['on_E208_rests'] for k, v in RL.items()})
    for fn in ('governor_v2.json', 'rest_v2.json', 'mm1_v2_params.json'):
        print(hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest(), fn)


if __name__ == '__main__':
    main()
