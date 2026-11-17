#!/usr/bin/env python3
"""MM1-v1's forecasts for E206's arm B (aifoundry1 card 1 at 600 MHz), made by the frozen predictor in this folder, unchanged. Desk; numpy.

    /usr/bin/python3 -I -B forecast_e206_armB.py --out <dir> [--points <E206's points-e206.csv>]
        writes <dir>/forecasts-e206-armB.csv (one row a point) and <dir>/forecasts-e206-armB.json (every quantity the predictor returns,
        the arguments and the inputs' sha256); it refuses to overwrite either file, and refuses to run if any file this folder's SHA256SUMS
        lists differs from it.

What runs: mm1_v1.Model(out/mm1_v1_params.json).predict(...) once for each point of E206's registered list (tools/claims-v3/e206/
points-e206.csv) with on_arm_B True. No refit, no new constant, no change to mm1_v1.py, mm1_core.py, kinds_v1.py, the parameter file or
inputs/. The arguments are the ones compare_e206.py gives arm A's points, with card 1's in place of aifoundry3's:
  - card 'aifoundry1 card 1' (MM1-v1's key c1): ledger v2's card-1 zeros anchors and kind rows (inputs/ledger_frozen-v2.json), the fitted
    awake power Pmin|aifoundry1 card 1 and the one Pmem (out/mm1_v1_params.json);
  - f = 600 MHz, E206's arm B clock;
  - V = 0.517 V, so s_V = (V / 0.517 V)^2 = 1: the volts on every card-1 row of MM1-v1's energy fit (inputs/gemm_table.json, E190's 18
    card-1 points). At 0.517 V the predictor gives v1's own in-sample card-1 W (out/points_energy_v1.csv) to 0.10 W or better; at 0.499 V
    (ledger v2's volts entry for card 1, which the predictor does not read) it would be about 0.9 W lower;
  - G = 0 (no governed base at 600 MHz); the shire mask and the ops a minion from the registered list; minions = 32 x the mask's shires, as
    the predictor computes them (equal to the registered minions at every arm B point);
  - the data kind as compare_e206.py builds it: random and zeros take ledger v2's own rows (fp32.randn, fp16.randn, int8.full; <fmt>.zeros);
    real takes kinds_v1.e206_kind (E206's four tiles a format), and ledger v2 has no card-1 row for those tiles, so their energy is NOT
    FORECAST; sparse50 has no resident price anywhere, so its energy is NOT FORECAST. Cycles and seconds are forecast at every point.
J at rest: MM1-v1 carries a rest law for aifoundry3 only, so none is given here; a J at rest is the run's measured rest x seconds + J over idle.
Labels: every constant of MM1-v1 is a desk fit made after its own data existed (post hoc as an act); these forecasts are blind for arm B
only once their sha256 is in a pushed commit made before arm B's first card command.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kinds_v1 as K  # noqa: E402
import mm1_core as C  # noqa: E402
import mm1_v1 as M1  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
POINTS = os.path.join(REPO, 'tools', 'claims-v3', 'e206', 'points-e206.csv')
PARAMS = os.path.join(HERE, 'out', 'mm1_v1_params.json')
CARD = 'aifoundry1 card 1'
F_MHZ = 600.0
V_C1 = 0.517
LOW_W = 3.0
NAMES = ('forecasts-e206-armB.csv', 'forecasts-e206-armB.json')
SHOWN = ['mm1_v1.py', 'mm1_core.py', 'kinds_v1.py', 'out/mm1_v1_params.json', 'inputs/MANIFEST.json', 'inputs/ledger_frozen-v2.json',
         'inputs/gemm_table.json', 'SHA256SUMS']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def check_frozen():
    """every file this folder's SHA256SUMS lists, against its bytes: (n checked, the differing paths)"""
    bad, n = [], 0
    for ln in open(os.path.join(HERE, 'SHA256SUMS')):
        if not ln.strip():
            continue
        h, p = ln.rstrip('\n').split('  ', 1)
        n += 1
        fp = os.path.join(HERE, p)
        if not os.path.isfile(fp) or sha(fp) != h:
            bad.append(p)
    return n, bad


def py(x):
    """numpy scalars and arrays to plain Python, for JSON"""
    if isinstance(x, dict):
        return {k: py(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [py(v) for v in x]
    if isinstance(x, np.ndarray):
        return py(x.tolist())
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return float(x)
    return x


def kind_specs(fmt, kind):
    """the e_res and phi specs as compare_e206.py builds them for arm A (None, None: the predictor's own ledger rows)"""
    if kind == 'real':
        return K.e206_kind(fmt, 'real')
    if kind == 'sparse50':
        return {'source': None}, {'gen': 'sparse50'}
    return None, None


def arm_b_points(path):
    return [p for p in csv.DictReader(open(path)) if p['on_arm_B'] == 'True']


def forecast(M, p, card=CARD, V=V_C1):
    es, ps = kind_specs(p['format'], p['kind'])
    return M.predict(card, p['arm'], p['format'], p['kind'], p['shire_mask'], F_MHZ, V, e_res_spec=es, phi_spec=ps,
                     ops=int(p['ops_per_minion_per_gemm']))


def r(x, n):
    return round(float(x), n) if x is not None else ''


def csv_row(p, o):
    w = o.get('W_over_idle')
    sw = o.get('switches') or {}
    ce = sw.get('counted_fin_edges') or [None, None]
    ee = sw.get('estimated_fin_edges') or [None, None, None]
    return {'id': p['id'], 'name': p['name'], 'case': f"{p['arm']}|{p['format']}|{p['shire_mask']}", 'family': p['family'], 'tier': p['tier'],
            'arm': p['arm'], 'fmt': p['format'], 'kind': p['kind'], 'mask': p['shire_mask'], 'shires': int(p['shires']), 'minions': int(o['minions']),
            'M': int(p['M']), 'N': int(p['N']), 'K': int(p['K']), 'values': p['values'],
            'footprint_MB': o['footprint_MB'], 'power_of_two_NB': bool(o['power_of_two_NB']),
            'lines_L2': r(o['lines_L2_L3_F'][0], 3), 'lines_L3': r(o['lines_L2_L3_F'][1], 3), 'lines_F': r(o['lines_L2_L3_F'][2], 3),
            'cycles_per_op_wall': r(o['cycles_per_op_wall'], 3), 'cycles_per_op_mean': r(o['cycles_per_op_mean'], 3),
            'rho_wall_over_mean': r(o['rho_wall_over_mean'], 5), 'ops_per_minion_per_gemm': int(o['ops_per_minion_per_gemm']),
            'cycles_per_gemm_wall': r(o['cycles_per_gemm_wall'], 1), 'seconds_per_gemm': r(o['seconds_per_gemm'], 9),
            'W_over_idle': r(w, 4), 'W_affine_A_W': r(o['W_affine']['A_W'], 5) if w is not None else '',
            'W_affine_B_W_us': r(o['W_affine']['B_W_us'], 5) if w is not None else '',
            'J_over_idle_per_gemm': r(o.get('J_over_idle_per_gemm'), 9),
            'rest_law_P_W': r(o['rest_law']['P_rest_W'], 4) if 'rest_law' in o else '',
            'J_at_rest_rest_law_REPORTED': r(o['rest_law']['J_at_rest_per_gemm_REPORTED'], 9) if 'rest_law' in o else '',
            'under_3W_over_idle': (bool(w < LOW_W) if w is not None else ''), 'e_res_nJ': r(o.get('e_res_nJ'), 5),
            'e_res_source': o.get('e_res_source', ''), 'phi': r(o.get('phi'), 4),
            'switches_counted_lo': py(ce[0]) if ce[0] is not None else '', 'switches_counted_hi': py(ce[1]) if ce[1] is not None else '',
            'switches_estimated_lo': py(ee[0]) if ee[0] is not None else '', 'switches_estimated_central': py(ee[1]) if ee[1] is not None else '',
            'switches_estimated_hi': py(ee[2]) if ee[2] is not None else '',
            'switches_int8_arithmetic_central': py(sw.get('of_which_int8_arithmetic_central')) if sw.get('of_which_int8_arithmetic_central') is not None else '',
            'fresh_lines_J_apart': py(sw.get('fresh_lines_J_apart')) if sw.get('fresh_lines_J_apart') is not None else '',
            'sim_steps_per_minion_per_gemm': o['sim_steps_per_minion_per_gemm'], 'floor_cycles_measured_tenb': o['floor_cycles_measured_tenb'],
            'bench_resident_cycles_simulated': o['bench_resident_cycles_simulated'],
            'energy_note': o.get('energy', '') if w is None else ''}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--points', default=POINTS)
    a = ap.parse_args()
    n, bad = check_frozen()
    if bad:
        sys.exit(f'forecast_e206_armB.py: {len(bad)} of {n} files differ from SHA256SUMS: {bad[:6]}: the predictor is not as frozen; nothing written')
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    for nm in NAMES:
        if os.path.exists(os.path.join(out, nm)):
            sys.exit(f'forecast_e206_armB.py: {nm} exists in {out}: refusing to overwrite')
    M = M1.Model(json.load(open(PARAMS)))
    pts = arm_b_points(a.points)
    rows, full, nf = [], [], []
    for p in pts:
        o = py(forecast(M, p))
        rows.append(csv_row(p, o))
        full.append({'id': p['id'], 'registered': {k: p[k] for k in ('name', 'family', 'tier', 'arm', 'format', 'kind', 'shire_mask', 'shires', 'minions',
                                                                     'M', 'N', 'K', 'ops_per_minion_per_gemm', 'values')},
                     'forecast': o})
        if o.get('W_over_idle') is None:
            nf.append({'id': p['id'], 'fmt': p['format'], 'kind': p['kind'], 'why': o.get('energy', '')})
    with open(os.path.join(out, NAMES[0]), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for x in rows:
            w.writerow(x)
    meta = {'what': "MM1-v1's forecasts for E206's arm B points (aifoundry1 card 1, 600 MHz), from the frozen predictor in tools/matmul/mm1/v1 unchanged",
            'model': 'MM1-v1', 'card': CARD, 'card_key': M1.CARD_KEY[CARD], 'f_mhz': F_MHZ, 'V': V_C1, 's_V': (V_C1 / 0.517) ** 2, 'G': 0.0,
            'V_why': ("the volts on every card-1 row of MM1-v1's energy fit (inputs/gemm_table.json, E190's 18 card-1 points); the predictor "
                      "reproduces v1's in-sample card-1 W at them; ledger v2's volts entry for card 1 (0.499 V) is not read by the predictor"),
            'kind_specs': "as compare_e206.py: random and zeros from ledger v2's own rows; real from kinds_v1.e206_kind; sparse50 none",
            'points_file': 'tools/claims-v3/e206/points-e206.csv', 'points_sha256': sha(a.points), 'n_points': len(rows),
            'n_energy_forecast': len(rows) - len(nf), 'energy_not_forecast': nf,
            'frozen_files_sha256': {p: sha(os.path.join(HERE, p)) for p in SHOWN}, 'sha256sums_checked': n,
            'python': sys.version.split()[0], 'numpy': np.__version__, 'scope': C.SCOPE, 'rows': full}
    with open(os.path.join(out, NAMES[1]), 'w') as fh:
        json.dump(meta, fh, indent=1)
        fh.write('\n')
    for x in rows:
        print(f"{x['id']} {x['arm']:12s} {x['fmt']} {x['kind']:8s} {x['mask']:10s} cyc {x['cycles_per_op_wall']:9.3f} mean {x['cycles_per_op_mean']:9.3f} "
              f"s {x['seconds_per_gemm']:.9f} W {x['W_over_idle']} J {x['J_over_idle_per_gemm']}")
    print(f"points {len(rows)}; energy forecast {len(rows) - len(nf)}; energy NOT FORECAST {len(nf)}: {[x['id'] for x in nf]}; SHA256SUMS {n} of {n} equal")


if __name__ == '__main__':
    main()
