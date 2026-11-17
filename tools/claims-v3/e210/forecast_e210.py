#!/usr/bin/env python3
"""E210 (Q202): the frozen forecasts of every case's paired difference dJ = J(pattern) - J(random) at the same shape (J over idle a GEMM, on
aifoundry3 card 0 at 600 MHz), by each route, from committed inputs only (every input's sha256 in the output; no E210 datum exists).

    /usr/bin/python3 -I -B tools/claims-v3/e210/forecast_e210.py <lab top>            writes forecast-e210.json and forecast-e210.txt
    /usr/bin/python3 -I -B tools/claims-v3/e210/forecast_e210.py <lab top> --check    recomputes and compares byte for byte (exit 0 PASS, 4 FAIL)

THE MEASURED INPUTS (committed): E206 arm A on aifoundry3 card 0 (d7e4f35e): random, zeros, real and sparse50 at S1 (p029, p080, p110, p116),
random and zeros at S2 (p034, p082): J over idle a GEMM = (p_work - p_rest) t_gemm per run, the mean of its two runs; D = J(random) - J(zeros).
ones never ran in a GEMM on aifoundry3: its share of D, f_ones = (ones - zeros) / (random - zeros), is E208's on aifoundry1 card 1 at the same
shape and 600 MHz (sessions a1c1-S1 and a1c1-S2, the registered primary view band600 dP_w, the mean of the two sessions), carried over to
aifoundry3 as J(ones) = J(zeros) + f_ones D (a cross-card transfer: card 1's D at S1, 29.9 W, is aifoundry3's 29.8 W).
MM1-v1's LINE TERM (tools/matmul/mm1/v1, landed 25d2e74e, called unchanged): its J over idle is affine in phi, the memory lines' data share;
L_phi(S) = J(phi = 1) - J(phi = 0) at the shape with the random resident price, and dL(kind) = (phi(kind) - 1) L_phi(S), phi by MM1-v1's own
kinds_v1 conventions (desk/flips-e210.json).
THE ROUTES (dJ in J a GEMM; W = dJ / t_gemm of E206's random at the shape):
  R1  the switch route (registered): dJ = b_S dS MACs + dL, dS = the case's counted switches a multiply-add minus random's (MM1-v1's units,
      the low column, desk/switch-counts-e210.json), b_S (= 1 / kappa_S, joules a switch) by least squares through the origin over the
      committed UNGATED kinds at the shape (S1: ones, real; S2: ones) of y = dJ_measured - dL against x = dS MACs. For an ungated pattern the
      clock part of dS is random's and cancels, so the low and high columns give the same forecast. Ungated (all-valid) cases only.
  R3  the bit-flip route (registered): dJ = sum_j (f_case[j] - f_random[j]) pi_j MACs + dL, f[j] the operand flips at bit j a multiply-add (A
      and B, the presented view, desk/flips-e210.json), pi_j E65's block-A price of a flipped bit at position j on aifoundry3 at 600 MHz
      (d_p80 / (4,096 x rate), hl.json; a flipped A bit priced as a B bit, an assumption). All-valid cases only.
  R3L the bit-flip route with one scale (registered for H3): dJ = lambda_S x' + dL, x' = R3's flip energy, lambda_S fitted as b_S is.
  R2  MM1-v1's kind term as landed (registered where it applies): a pattern whose every element is drawn from the element law of a kind
      MM1-v1 prices maps to it: bhalfeq, badjeq and hd4 to fp32.randn (their words are normal(0, 1) draws, hd4's re-drawn in mantissa bits only),
      so dJ = J_MM1v1(randn price, phi_case) - J_MM1v1(random) = dL. Every other pattern: NOT FORECAST.
  R4  the null (registered): the nearest committed kind at the shape by (z, rho / 0.5, tau / 0.5) (desk/flips-e210.json), S1 {zeros, ones,
      sparse50, real, random}, S2 {zeros, ones, random}: dJ = J(nearest) - J(random), measured (ones transferred).
  REPORTED beside, no verdict: R1pure (R1 with no line term: y = dJ_measured), R1g (two classes for a gated case: signal fin edges at b_S, clock
      fin edges at b_clk from zeros: y_zeros - b_S dS_signal(zeros) MACs = b_clk dS_clock(zeros) MACs), and each route's residuals on the
      committed kinds, fitted and left out.
THE PLAN CHECK: a case's planning peak = the measured board peak of random at the shape on this card (E206's telemetry, p029 / p034) + 1.10 x
the largest forecast of W over random among R1, R2, R4 and R3L (raw R3 left out: its committed check over-prices random's data part); exit 3
if any case passes the 65 W line.
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import hashlib
import json
import math
import os
import random
import sys

E206 = 'docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/data-e206.json'
E206TEL = 'docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/session/telemetry.jsonl.gz'
E206RUNS = 'docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/session/runs'
E208 = ['docs/reports/data/2026-11-16-e208-mmsweep-a1c1-S1/data-e208-a1c1-S1.json',
        'docs/reports/data/2026-11-16-e208-mmsweep-a1c1-S2/data-e208-a1c1-S2.json']
E65 = 'docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/hl.json'
MM1 = ['tools/matmul/mm1/v1/mm1_v1.py', 'tools/matmul/mm1/v1/mm1_core.py', 'tools/matmul/mm1/v1/kinds_v1.py',
       'tools/matmul/mm1/v1/out/mm1_v1_params.json', 'tools/matmul/mm1/v1/inputs/ledger_frozen-v2.json',
       'tools/matmul/mm1/v1/inputs/switch_table.json', 'tools/matmul/mm1/v1/inputs/linemap.py', 'tools/matmul/mm1/v1/inputs/l2_lab.json']
DESK = ['tools/claims-v3/e210/desk/switch-counts-e210.json', 'tools/claims-v3/e210/desk/flips-e210.json', 'tools/claims-v3/e210/points-e210.json']
E206_IDS = {'S1': {'random': 'p029', 'zeros': 'p080', 'real': 'p110', 'sparse50': 'p116'}, 'S2': {'random': 'p034', 'zeros': 'p082'}}
E208_ARM = {'S1': '1x1x1-fp32', 'S2': '1x1x4-fp32'}
UNGATED_CAL = {'S1': ['ones', 'real'], 'S2': ['ones']}
NULL_CANDS = {'S1': ['zeros', 'ones', 'sparse50', 'real', 'random'], 'S2': ['zeros', 'ones', 'random']}
R2_MAP = {'bhalfeq': 'fp32.randn', 'badjeq': 'fp32.randn', 'hd4': 'fp32.randn'}
LINE_W = 65.0
SIGMA_RUN_W = {'central': 0.11, 'optimistic': 0.06, 'conservative': 0.164}
VOLTS = 0.522


def sha(top, p):
    return hashlib.sha256(open(os.path.join(top, p), 'rb').read()).hexdigest()


def rnd(x):
    if isinstance(x, float):
        return float(f'{x:.10g}') if math.isfinite(x) else str(x)
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rnd(v) for v in x]
    return x


def e206_points(top):
    P = json.load(open(os.path.join(top, E206)))['arms']['A']['points']
    out = {}
    for s, ids in E206_IDS.items():
        for k, pid in ids.items():
            runs = P[pid]['runs']
            J = [(r['p_work_w'] - r['p_rest_w']) * r['t_gemm_s'] for r in runs]
            W = [r['p_work_w'] - r['p_rest_w'] for r in runs]
            out[(s, k)] = {'point': pid, 'J': sum(J) / len(J), 'W': sum(W) / len(W), 't_gemm_s': sum(r['t_gemm_s'] for r in runs) / len(runs),
                           'cycles_per_op': sum(r['cycles_per_op'] for r in runs) / len(runs), 'runs': [r['detail']['run'] for r in runs],
                           'J_runs': J, 'W_runs': W}
    return out


def e206_peaks(top):
    tel = []
    with gzip.open(os.path.join(top, E206TEL), 'rt') as f:
        for ln in f:
            if ln.startswith('{'):
                try:
                    tel.append(json.loads(ln))
                except ValueError:
                    pass
    tel.sort(key=lambda s: s['t_ms'])
    ts = [s['t_ms'] for s in tel]
    peaks = {}
    for rd in sorted(os.listdir(os.path.join(top, E206RUNS))):
        pid = rd.split('-')[-1]
        if pid not in ('p029', 'p034'):
            continue
        rj = json.load(open(os.path.join(top, E206RUNS, rd, 'run.json')))
        w0, w1 = rj['procs'][0]['launch_window_ms']
        i, j = bisect.bisect_left(ts, w0), bisect.bisect_right(ts, w1)
        bw = [s['board_w'] for s in tel[i:j] if s.get('board_w') is not None]
        if bw:
            peaks.setdefault(pid, []).append({'run': rd, 'board_max_w': max(bw)})
    return {'S1': max(p['board_max_w'] for p in peaks['p029']), 'S2': max(p['board_max_w'] for p in peaks['p034']), 'runs': peaks}


def e208_fones(top):
    out = {}
    for s, arm in E208_ARM.items():
        per = []
        for p in E208:
            d = json.load(open(os.path.join(top, p)))
            v = {}
            for r in d['runs']:
                for k, suf in (('zeros', 'zeros'), ('ones', 'ones'), ('random', 'rnd')):
                    if r['arm'] == f'{arm}-{suf}' and r.get('ran') and r['form'] == 'burst':
                        v[k] = (r['run'], r['views']['band600']['dP_w'])
            f = (v['ones'][1] - v['zeros'][1]) / (v['random'][1] - v['zeros'][1])
            per.append({'session': os.path.basename(p), 'runs': {k: x[0] for k, x in v.items()}, 'dP_w': {k: x[1] for k, x in v.items()}, 'f_ones': f})
        out[s] = {'f_ones': sum(x['f_ones'] for x in per) / len(per), 'sessions': per}
    return out


def e65_prices(top):
    it = json.load(open(os.path.join(top, E65)))['cards']['aifoundry3']['items']
    return [it[f'bit_{j}']['d_p80'] / (4096.0 * it[f'bit_{j}']['rate']) for j in range(32)]


def mm1_terms(top, pts):
    sys.path.insert(0, os.path.join(top, 'tools/matmul/mm1/v1'))
    import mm1_v1  # noqa: E402
    params = json.load(open(os.path.join(top, 'tools/matmul/mm1/v1/out/mm1_v1_params.json')))
    M = mm1_v1.Model(params)
    out = {}
    for s, sh in pts['shapes'].items():
        es = {'source': 'ledger', 'keys': ['fp32.randn']}
        j1 = M.predict('aifoundry3 card 0', sh['arm'], 'fp32', 'random', '0xffffffff', 600.0, VOLTS, e_res_spec=es, phi_spec={'gen': 'randn'})
        j0 = M.predict('aifoundry3 card 0', sh['arm'], 'fp32', 'random', '0xffffffff', 600.0, VOLTS, e_res_spec=es, phi_spec={'gen': 'zeros'})
        jr = M.predict('aifoundry3 card 0', sh['arm'], 'fp32', 'random', '0xffffffff', 600.0, VOLTS)
        jz = M.predict('aifoundry3 card 0', sh['arm'], 'fp32', 'zeros', '0xffffffff', 600.0, VOLTS)
        out[s] = {'L_phi_J': j1['J_over_idle_per_gemm'] - j0['J_over_idle_per_gemm'], 'J_random_mm1v1': jr['J_over_idle_per_gemm'],
                  'J_zeros_mm1v1': jz['J_over_idle_per_gemm'], 'phi_random_mm1v1': j1['phi'], 'seconds_per_gemm_mm1v1': jr['seconds_per_gemm'],
                  'line_share_of_D_mm1v1': (j1['J_over_idle_per_gemm'] - j0['J_over_idle_per_gemm']) /
                                           (jr['J_over_idle_per_gemm'] - jz['J_over_idle_per_gemm'])}
    return out


def lsq0(xs, ys):
    sxx = sum(x * x for x in xs)
    return sum(x * y for x, y in zip(xs, ys)) / sxx


def forecast(top):
    pts = json.load(open(os.path.join(top, DESK[2])))
    sc = json.load(open(os.path.join(top, DESK[0])))['shapes']
    fl = json.load(open(os.path.join(top, DESK[1])))['rows']
    meas = e206_points(top)
    peaks = e206_peaks(top)
    f1 = e208_fones(top)
    pi = e65_prices(top)
    mm = mm1_terms(top, pts)
    res = {'experiment': 'E210', 'what': 'frozen forecasts of dJ = J(case) - J(random) at the same shape, J over idle a GEMM, aifoundry3 card 0, 600 MHz',
           'python': sys.version.split()[0], 'routes_registered': ['R1', 'R3', 'R3L', 'R2', 'R4'], 'routes_reported': ['R1pure', 'R1g'],
           'calibration': {}, 'cases': {}, 'plan': {}, 'inputs_sha256': {}}
    for p in [E206, E206TEL] + E208 + [E65] + MM1 + DESK:
        res['inputs_sha256'][p] = sha(top, p)
    for s, sh in pts['shapes'].items():
        macs = sh['macs_per_gemm']
        t = meas[(s, 'random')]['t_gemm_s']
        Jr, Jz = meas[(s, 'random')]['J'], meas[(s, 'zeros')]['J']
        D = Jr - Jz
        Lphi = mm[s]['L_phi_J']
        known = {k: meas[(s, k)]['J'] for k in E206_IDS[s]}
        known['ones'] = Jz + f1[s]['f_ones'] * D
        rows = sc[s]
        S = {k: rows[k]['fin_edges_lo'] for k in rows}
        Ssig = {k: rows[k]['signal_lo'] for k in rows}
        Sclk = {k: rows[k]['clock'] for k in rows}
        Shi = {k: rows[k]['fin_edges_hi'] for k in rows}
        kmap = {'random': 'randn'}
        kk = lambda k: kmap.get(k, k)  # noqa: E731

        def dL(k):
            return (fl[kk(k)]['phi_mm1v1'] - 1.0) * Lphi if k != 'random' else 0.0

        def dS(k, col=None):
            col = col or S
            return (col[kk(k)] - col['randn']) * macs

        def flipE(k):
            a, b = fl[kk(k)][s], fl['randn'][s]
            return sum((a['flips_A_presented'][j] + a['flips_B_presented'][j] - b['flips_A_presented'][j] - b['flips_B_presented'][j]) * pi[j]
                       for j in range(32)) * macs

        cal = UNGATED_CAL[s]
        y = {k: (known[k] - Jr) - dL(k) for k in known}
        b1 = lsq0([dS(k) for k in cal], [y[k] for k in cal])
        b1hi = lsq0([dS(k, Shi) for k in cal], [y[k] for k in cal])
        bp = lsq0([dS(k) for k in cal], [known[k] - Jr for k in cal])
        lam = lsq0([flipE(k) for k in cal], [y[k] for k in cal])
        bclk = (y['zeros'] - b1 * dS('zeros', Ssig)) / dS('zeros', Sclk)
        resid = {}
        for k in known:
            if k == 'random':
                continue
            m = known[k] - Jr
            r1 = b1 * dS(k) + dL(k)
            r1g = b1 * dS(k, Ssig) + bclk * dS(k, Sclk) + dL(k)
            r3 = flipE(k) + dL(k)
            r3l = lam * flipE(k) + dL(k)
            resid[k] = {'measured_dJ': m, 'measured_as': 'transferred from E208 card 1' if k == 'ones' else f"E206 {meas[(s, k)]['point']}",
                        'in_R1_fit': k in cal, 'R1': r1, 'R1_minus_measured_frac_of_D': (r1 - m) / D,
                        'R1pure': bp * dS(k), 'R1pure_minus_measured_frac_of_D': (bp * dS(k) - m) / D,
                        'R1g': r1g, 'R1g_minus_measured_frac_of_D': (r1g - m) / D, 'R1g_uses_it': k == 'zeros',
                        'R3': r3, 'R3_minus_measured_frac_of_D': (r3 - m) / D, 'R3L': r3l, 'R3L_minus_measured_frac_of_D': (r3l - m) / D}
        res['calibration'][s] = {
            'D_J': D, 'D_W': D / t, 't_gemm_s': t, 'J_random': Jr, 'J_zeros': Jz, 'W_random': meas[(s, 'random')]['W'],
            'e206_points': {k: {kk2: v for kk2, v in meas[(s, k)].items()} for k in E206_IDS[s]},
            'f_ones_e208_card1': f1[s], 'J_ones_transferred': known['ones'],
            'mm1v1': mm[s], 'b_S_J_per_switch': b1, 'kappa_S_switches_per_J': 1.0 / b1, 'b_S_hi': b1hi, 'kappa_S_hi': 1.0 / b1hi,
            'b_S_pure': bp, 'lambda_S': lam, 'b_clk_R1g': bclk, 'kappa_clk_R1g': 1.0 / bclk if bclk else None,
            'ungated_calibration_kinds': cal, 'residuals_on_committed_kinds': resid,
            'peak_random_board_w': peaks[s], 'sigma_run_w': SIGMA_RUN_W}
        for c in pts['cases']:
            if c['shape'] != s or c['kind'] == 'random':
                continue
            k = c['kind']
            fk = fl[kk(k)]
            ungated = fk[s]['valid_share'] > 0.999 and fk[s]['z'] == 0.0
            rec = {'case': c['case'], 'kind': k, 'shape': s, 'role': c['role'], 'ungated_all_valid': ungated,
                   'dS_lo_per_mac': S[kk(k)] - S['randn'], 'dS_hi_per_mac': Shi[kk(k)] - Shi['randn'], 'phi': fk['phi_mm1v1'], 'dL_J': dL(k),
                   'features': {'z': fk[s]['z'], 'rho': fk[s]['rho'], 'tau': fk[s]['tau']}, 'routes': {}}
            R = rec['routes']
            if ungated:
                R['R1'] = b1 * dS(k) + dL(k)
                R['R1_hi'] = b1hi * dS(k, Shi) + dL(k)
                R['R3'] = flipE(k) + dL(k)
                R['R3L'] = lam * flipE(k) + dL(k)
            else:
                R['R1'] = 'NOT FORECAST: gated (the switch route prices ungated cases only)'
                R['R3'] = 'NOT FORECAST: gated (a gated slot is not a flip)'
                R['R3L'] = 'NOT FORECAST: gated'
            R['R2'] = dL(k) if k in R2_MAP else 'NOT FORECAST: no MM1-v1 kind with this element law'
            if k in R2_MAP:
                rec['R2_maps_to'] = R2_MAP[k]
            feat = lambda q: (fl[kk(q)][s]['z'], fl[kk(q)][s]['rho'] / 0.5, fl[kk(q)][s]['tau'] / 0.5)  # noqa: E731
            dist = {q: math.dist(feat(k), feat(q)) for q in NULL_CANDS[s]}
            near = min(NULL_CANDS[s], key=lambda q: (dist[q], q))
            R['R4'] = known[near] - Jr
            rec['R4_nearest'] = near
            rec['R4_distances'] = dist
            R['R1pure'] = bp * dS(k)
            R['R1g'] = b1 * dS(k, Ssig) + bclk * dS(k, Sclk) + dL(k)
            rec['routes_W'] = {q: (v / t if isinstance(v, float) else v) for q, v in R.items()}
            rec['routes_frac_of_D'] = {q: (v / D if isinstance(v, float) else v) for q, v in R.items()}
            plan_routes = [R[q] for q in ('R1', 'R2', 'R4', 'R3L', 'R1g') if isinstance(R.get(q), float)]
            if c['role'] == 'control':
                plan_routes.append(known.get(k, Jz + f1[s]['f_ones'] * D) - Jr if k in known else 0.0)
            hot = max([0.0] + [v / t for v in plan_routes])
            rec['planning_peak_w'] = peaks[s] + 1.10 * hot
            res['cases'][c['case']] = rec
        res['plan'][s] = {'line_w': LINE_W, 'max_planning_peak_w': max(r['planning_peak_w'] for r in res['cases'].values() if r['shape'] == s),
                          'hottest_case': max((r for r in res['cases'].values() if r['shape'] == s), key=lambda r: r['planning_peak_w'])['case']}
    res['power'] = power(res)
    return rnd(res)


def power(res):
    """desk: the head-to-head's power against the meter's spread, truth on R1 (or on the other route), 3 blocks a test case"""
    out = {}
    rng = random.Random('E210|power')
    for label, sig in SIGMA_RUN_W.items():
        for other in ('R4', 'R3', 'R3L', 'R2'):
            cases = []
            for c in res['cases'].values():
                if c['role'] != 'test':
                    continue
                f1, fk = c['routes'].get('R1'), c['routes'].get(other)
                if not isinstance(f1, float) or not isinstance(fk, float):
                    continue
                t = res['calibration'][c['shape']]['t_gemm_s']
                cases.append((f1, fk, sig * t / math.sqrt(3)))
            n = len(cases)
            if n == 0:
                out[f'{label}|R1_vs_{other}'] = {'cases': 0}
                continue
            res_t = {}
            for truth in ('R1', other):
                better = 0
                trials = 4000
                for _ in range(trials):
                    w1 = wk = 0
                    for f1, fk, se in cases:
                        m = (f1 if truth == 'R1' else fk) + rng.gauss(0.0, se)
                        e1, ek = abs(m - f1), abs(m - fk)
                        if abs(e1 - ek) < 2 * se:
                            continue
                        if e1 < ek:
                            w1 += 1
                        else:
                            wk += 1
                    nd = w1 + wk
                    crit = crit_two_sided(nd)
                    if truth == 'R1' and nd and w1 >= crit:
                        better += 1
                    if truth != 'R1' and nd and wk >= crit:
                        better += 1
                res_t[f'truth_{truth}'] = better / trials
            out[f'{label}|R1_vs_{other}'] = {'cases': n, 'sigma_run_w': sig, 'power_declares_the_true_route_better': res_t,
                                             'median_abs_forecast_gap_w': sorted(abs(a - b) / (s_ * math.sqrt(3) / sig) * sig / sig
                                                                                 for a, b, s_ in cases)[n // 2] if n else None}
    return out


def crit_two_sided(n, alpha=0.05):
    """the smallest w with P(X >= w) <= alpha / 2 for X ~ Binomial(n, 1/2); n + 1 if none"""
    if n == 0:
        return 1
    tail = 0.0
    for w in range(n, -1, -1):
        tail += math.comb(n, w) / 2 ** n
        if tail > alpha / 2:
            return w + 1
    return 0


def text(res):
    L = ['E210 frozen forecasts: dJ = J(case) - J(random), J over idle a GEMM, aifoundry3 card 0 at 600 MHz (in W over random and as a fraction of D)', '']
    for s, c in res['calibration'].items():
        L.append(f"{s}: D {c['D_W']:.3f} W = {c['D_J'] * 1e3:.5f} mJ a GEMM (E206 measured); t_gemm {c['t_gemm_s']:.6e} s; f_ones {c['f_ones_e208_card1']['f_ones']:.4f} "
                 f"(E208 card 1); MM1-v1 line share of D {c['mm1v1']['line_share_of_D_mm1v1']:.4f}; kappa {c['kappa_S_switches_per_J']:.4e} switches a J "
                 f"(b {c['b_S_J_per_switch']:.4e}); lambda {c['lambda_S']:.4f}; peak random {c['peak_random_board_w']:.2f} W")
        for k, r in c['residuals_on_committed_kinds'].items():
            L.append(f"   committed {k:9s} measured {r['measured_dJ'] / c['t_gemm_s']:+8.3f} W ({r['measured_as']}); R1 {r['R1_minus_measured_frac_of_D']:+.4f} D"
                     f"{' (fit)' if r['in_R1_fit'] else ''}; R1g {r['R1g_minus_measured_frac_of_D']:+.4f} D; R3 {r['R3_minus_measured_frac_of_D']:+.4f} D; "
                     f"R3L {r['R3L_minus_measured_frac_of_D']:+.4f} D; R1pure {r['R1pure_minus_measured_frac_of_D']:+.4f} D")
    L.append('')
    L.append('case               role      R1 W     R3 W    R3L W     R2 W     R4 W (nearest)       R1pure   R1g    | fractions of D: R1, R3L, R4 | plan peak')
    for c in res['cases'].values():
        W = c['routes_W']
        f = lambda v: f'{v:+8.3f}' if isinstance(v, float) else '     n/f'  # noqa: E731
        fd = c['routes_frac_of_D']
        g = lambda v: f'{v:+.3f}' if isinstance(v, float) else ' n/f '  # noqa: E731
        L.append(f"{c['case']:18s} {c['role']:8s} {f(W['R1'])} {f(W['R3'])} {f(W['R3L'])} {f(W['R2'])} {f(W['R4'])} ({c['R4_nearest']:8s}) {f(W['R1pure'])} {f(W['R1g'])} | "
                 f"{g(fd['R1'])} {g(fd['R3L'])} {g(fd['R4'])} | {c['planning_peak_w']:.2f} W")
    L.append('')
    for s, p in res['plan'].items():
        L.append(f"plan {s}: the hottest case {p['hottest_case']} at {p['max_planning_peak_w']:.2f} W against the {p['line_w']:.0f} W line")
    L.append('')
    L.append('power (desk; 3 blocks a test case; truth on one route; the exact two-sided sign test at 0.05 over decided cases):')
    for k, v in res['power'].items():
        if v.get('cases'):
            L.append(f"  {k:28s} cases {v['cases']:2d}: P(R1 BETTER | truth R1) {v['power_declares_the_true_route_better']['truth_R1']:.3f}; "
                     f"P(other BETTER | truth other) {v['power_declares_the_true_route_better']['truth_' + k.split('_vs_')[1]]:.3f}")
        else:
            L.append(f'  {k:28s} no case')
    return '\n'.join(L) + '\n'


def main():
    top = os.path.abspath(sys.argv[1])
    here = os.path.join(top, 'tools/claims-v3/e210')
    res = forecast(top)
    js = json.dumps(res, indent=1, sort_keys=True) + '\n'
    tx = text(res)
    if '--check' in sys.argv:
        ok = open(os.path.join(here, 'forecast-e210.json')).read() == js and open(os.path.join(here, 'forecast-e210.txt')).read() == tx
        print('forecast_e210 --check', 'PASS' if ok else 'FAIL')
        return 0 if ok else 4
    over = [c['case'] for c in res['cases'].values() if c['planning_peak_w'] > LINE_W]
    open(os.path.join(here, 'forecast-e210.json'), 'w').write(js)
    open(os.path.join(here, 'forecast-e210.txt'), 'w').write(tx)
    print(tx, end='')
    if over:
        print('REFUSED: over the line: ' + ', '.join(over))
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
