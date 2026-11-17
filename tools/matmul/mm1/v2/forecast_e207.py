#!/usr/bin/env python3
"""MM1-v2's forecasts for E207, THE BLIND MATMUL DAY (aifoundry3 card 0 at its pinned 600 MHz, rgm136 unchanged), made by the frozen predictor
in this folder, unchanged. Desk; numpy.

    /usr/bin/python3 -I -B forecast_e207.py --out <dir> [--e207-points <E207's points-e207.csv>]
        writes <dir>/forecasts-e207.csv (one row a point) and <dir>/forecasts-e207.json (every quantity the predictor returns, the arguments
        and the inputs' sha256); it refuses to overwrite either file, and refuses to run if any file this folder's SHA256SUMS lists differs
        from it.

THE POINTS: E207's 53 points (47 cases) are MM1-v1's blind-day list, ../v1/out/mm1_v1_blind_day.csv (sha256 90dffe94..., landed in 25d2e74e),
which E207's registration reads and never re-chooses (its tools/claims-v3/e207/points-e207.csv, sha256 1e6067bc...). This script reads the
list from MM1-v1's file (pinned: exit 4 on any other bytes). When E207's registration file is found (in the lab at
tools/claims-v3/e207/points-e207.csv, or named by --e207-points) it checks that file's sha256 and that its 53 rows name the same id, arm,
format, data kind, shire mask (as a number), shires, minions, M, N, K, ops a minion, values and watts-scored flag (exit 4 on any difference).
The two files write
one mask apart: b37's 0x0f0f0f0f in MM1-v1's list is 0xf0f0f0f in E207's (the same number, as the host prints it); the rows here carry the
mask as E207 writes it (hex of its number) and MM1-v1's string beside it. The outputs do not depend on whether that check ran.

What runs: mm1_v2.Model(out/mm1_v2_params.json).predict(...) once a point. No refit, no new constant, no change to mm1_v2.py, mm1_core_v2.py,
kinds_v2.py, governor_v2.py, the parameter file or inputs/. The arguments:
  - card 'aifoundry3 card 0' (MM1-v2's key a3): ledger v2's aifoundry3 zeros anchors and kind rows, MM1-v2's fitted aifoundry3 awake power,
    its one memory-path power and its rest law for aifoundry3 (out/mm1_v2_params.json);
  - f = 600 MHz, the card's pinned clock (E207 sets nothing): the run's measured clock and the forecast clock are the same, so MM1-v2's two
    clock routes ('given the measured clock', 'with the clock forecast') coincide and no governor model is called;
  - V = None and G = None: the predictor's own defaults for this card, 0.522 V (mm1_core_v2.CARD_V, the footing of MM1-v2's aifoundry3 fit,
    as of MM1-v1's blind day) and no governed base on a pinned card (mm1_core_v2.G_of_f);
  - the shire mask and the ops a minion from the list; minions = 32 x the mask's shires (equal to the listed minions at all 53 points);
  - the data kind as MM1-v1's blind day built it (blind_day_v1.kind_specs): random takes ledger v2's own rows (fp32.randn, fp16.randn,
    int8.full); e37 takes ledger v2's fp32.small_int (whose own text names E37's fill) with the e37 generator's phi; blind4's real tiles and
    blind3's constant-column A pass their own sources ('blind4', 'blind3'), which MM1-v2's predictor does not price (its resident() prices
    ones, zeros, random and ledger kind rows only): their energy is NOT FORECAST. Cycles and seconds are forecast at all 53 points;
  - t0_c = None: the rest law's forecast start die (54.4 C, E206 arm A's median start die, MM1-v1's).
J at rest: the rest law's REPORTED column (P_rest(T0) x t + J over idle); a scored J at rest uses the run's measured rest x seconds + J over idle.
Labels: every constant of MM1-v2 is a desk fit made after its own data existed (post hoc as an act); these forecasts are blind for E207 only
once their sha256 is in a pushed commit made before E207's first card command, and E207's registered rules name MM1-v1, F1 and F2, not
MM1-v2: a score of these forecasts is REPORTED.
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
import mm1_core_v2 as C  # noqa: E402
import mm1_v2 as M2  # noqa: E402

REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
PARAMS = os.path.join(HERE, 'out', 'mm1_v2_params.json')
V1_LIST = os.path.join(HERE, '..', 'v1', 'out', 'mm1_v1_blind_day.csv')
V1_LIST_REL = 'tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv'
V1_LIST_SHA = '90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6'
E207_POINTS_REL = 'tools/claims-v3/e207/points-e207.csv'
E207_POINTS_SHA = '1e6067bcf0fc123c81bf927472bbc27a312b64139de5890add3b4c2991d9b114'
CARD = 'aifoundry3 card 0'
F_MHZ = 600.0
LOW_W = 3.0
NAMES = ('forecasts-e207.csv', 'forecasts-e207.json')
SHOWN = ['mm1_v2.py', 'mm1_core_v2.py', 'kinds_v2.py', 'governor_v2.py', 'out/mm1_v2_params.json', 'inputs/MANIFEST.json',
         'inputs/v1/ledger_frozen-v2.json', 'inputs/v1/predictions-blind4.json', 'inputs/v1/predictions-blind3-extract.json', 'SHA256SUMS']
B4 = {'fp32': ['fp32.real_pythia_embed_qkv', 'fp32.real_qwen_q_down'], 'fp16': ['fp16.real_pythia_embed_qkv', 'fp16.real_qwen_ln_down'],
      'int8': ['int8.real_pythia_embed_mlpout', 'int8.real_qwen_q_down']}


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


def mask_e207(m):
    """the mask as E207 writes it: hex of its number (0x0f0f0f0f -> 0xf0f0f0f; every other mask of the list unchanged)"""
    return hex(int(m, 16))


def kind_specs(fmt, kind):
    """(e_res spec, phi spec) as MM1-v1's blind day built them (blind_day_v1.kind_specs); None, None: the predictor's own ledger rows"""
    if kind == 'random':
        return None, None
    if kind == 'e37':
        return {'source': 'ledger', 'keys': ['fp32.small_int']}, {'gen': 'e37'}
    if kind == 'real:blind4':
        return {'source': 'blind4', 'keys': B4[fmt]}, {'tiles': [f'tiles/blind4__{fmt}__{t}.bin' for t in B4[fmt]]}
    if kind.startswith('designed:blind3'):
        return {'source': 'blind3', 'keys': ['fp32.a_colconst_b_randn']}, {'tiles': ['tiles/blind3__fp32__a_colconst_b_randn.bin']}
    raise ValueError(kind)


def read_points():
    if sha(V1_LIST) != V1_LIST_SHA:
        print(f'forecast_e207.py: {V1_LIST_REL} is not the landed list (sha256 {V1_LIST_SHA[:12]}...): nothing written')
        sys.exit(4)
    return list(csv.DictReader(open(V1_LIST, newline='')))


def check_e207(pts, path):
    """E207's registered points against MM1-v1's list: (checked?, text); exits 4 on any difference"""
    if not path or not os.path.isfile(path):
        return False, 'E207 registration points file not found: not checked'
    h = sha(path)
    if h != E207_POINTS_SHA:
        print(f'forecast_e207.py: E207 points file sha256 {h} is not {E207_POINTS_SHA}: nothing written')
        sys.exit(4)
    reg = list(csv.DictReader(open(path, newline='')))
    if len(reg) != len(pts):
        print(f'forecast_e207.py: E207 lists {len(reg)} points, MM1-v1 {len(pts)}: nothing written')
        sys.exit(4)
    diff = []
    for a, b in zip(reg, pts):
        ka = (a['id'], a['arm'], a['format'], a['kind'], int(a['shire_mask'], 16), a['shires'], a['minions'], a['M'], a['N'], a['K'],
              a['ops_per_minion_per_gemm'], a['values'], a['scored_in_watts'])
        kb = (b['id'], b['arm'], b['fmt'], b['kind'], int(b['mask'], 16), b['shires'], b['minions'], b['M'], b['N'], b['K'],
              b['ops_per_minion_per_gemm'], b['values'], b['scored_in_watts'])
        if ka != kb or a['shire_mask'] != mask_e207(b['mask']):
            diff.append(a['id'])
    if diff:
        print(f'forecast_e207.py: E207 and MM1-v1 differ at {diff}: nothing written')
        sys.exit(4)
    return True, f'E207 registration points ({E207_POINTS_REL}, sha256 {h}): {len(reg)} of {len(reg)} rows equal MM1-v1\'s list'


def forecast(M, p):
    es, ps = kind_specs(p['fmt'], p['kind'])
    mi = C.mask_info(p['mask'])
    return M.predict(CARD, p['arm'], p['fmt'], p['kind'], p['mask'], F_MHZ, None, ops=int(p['ops_per_minion_per_gemm']),
                     minions=32 * mi['n'], e_res_spec=es, phi_spec=ps)


def r(x, n):
    return round(float(x), n) if x is not None else ''


def csv_row(p, o):
    w = o.get('W_over_idle')
    sw = o.get('switches') or {}
    ce = sw.get('counted_fin_edges') or [None, None]
    ee = sw.get('estimated_fin_edges') or [None, None, None]
    rl = o.get('rest_law') or {}
    m7 = mask_e207(p['mask'])
    return {'id': p['id'], 'case': f"{p['arm']}|{p['fmt']}|{m7}", 'family': p['family'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'],
            'mask': m7, 'mask_in_mm1_v1_list': p['mask'], 'shires': int(p['shires']), 'minions': int(o['minions']),
            'M': int(p['M']), 'N': int(p['N']), 'K': int(p['K']), 'values': p['values'],
            'footprint_MB': o['footprint_MB'], 'power_of_two_NB': bool(o['power_of_two_NB']),
            'lines_L2': r(o['lines_L2_L3_F'][0], 3), 'lines_L3': r(o['lines_L2_L3_F'][1], 3), 'lines_F': r(o['lines_L2_L3_F'][2], 3),
            'cycles_per_op_wall': r(o['cycles_per_op_wall'], 3), 'cycles_per_op_mean': r(o['cycles_per_op_mean'], 3),
            'rho_wall_over_mean': r(o['rho_wall_over_mean'], 5), 'ops_per_minion_per_gemm': int(o['ops_per_minion_per_gemm']),
            'cycles_per_gemm_wall': r(o['cycles_per_gemm_wall'], 1), 'seconds_per_gemm': r(o['seconds_per_gemm'], 9),
            'W_over_idle': r(w, 4), 'W_affine_A_W': r(o['W_affine']['A_W'], 5) if w is not None else '',
            'W_affine_B_W_us': r(o['W_affine']['B_W_us'], 5) if w is not None else '',
            'J_over_idle_per_gemm': r(o.get('J_over_idle_per_gemm'), 9), 'V': r(o.get('V'), 4) if w is not None else '',
            'rest_law_P_W': r(rl.get('P_rest_W'), 4) if rl else '', 'rest_law_T0_c': r(rl.get('T0_c'), 2) if rl else '',
            'J_at_rest_rest_law_REPORTED': r(rl.get('J_at_rest_per_gemm_REPORTED'), 9) if rl else '',
            'scored_in_watts_E207': p['scored_in_watts'] == 'True', 'under_3W_over_idle': (bool(w < LOW_W) if w is not None else ''),
            'e_res_nJ': r(o.get('e_res_nJ'), 5), 'e_res_source': o.get('e_res_source', ''), 'phi': r(o.get('phi'), 4),
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
    ap.add_argument('--e207-points', default=os.path.join(REPO, E207_POINTS_REL))
    a = ap.parse_args()
    n, bad = check_frozen()
    if bad:
        sys.exit(f'forecast_e207.py: {len(bad)} of {n} files differ from SHA256SUMS: {bad[:6]}: the predictor is not as frozen; nothing written')
    pts = read_points()
    checked, ctext = check_e207(pts, a.e207_points)
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('forecast_e207.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    for nm in NAMES:
        if os.path.exists(os.path.join(out, nm)):
            sys.exit(f'forecast_e207.py: {nm} exists in {out}: refusing to overwrite')
    M = M2.Model(json.load(open(PARAMS)))
    rows, full, nf = [], [], []
    for p in pts:
        o = py(forecast(M, p))
        rows.append(csv_row(p, o))
        full.append({'id': p['id'], 'listed': {k: p[k] for k in ('family', 'arm', 'fmt', 'kind', 'mask', 'shires', 'minions', 'M', 'N', 'K',
                                                                 'ops_per_minion_per_gemm', 'values', 'scored_in_watts')},
                     'mask_e207': mask_e207(p['mask']), 'forecast': o})
        if o.get('W_over_idle') is None:
            nf.append({'id': p['id'], 'fmt': p['fmt'], 'kind': p['kind'], 'why': o.get('energy', '')})
    with open(os.path.join(out, NAMES[0]), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        for x in rows:
            w.writerow(x)
    V = C.volts(CARD, F_MHZ)
    meta = {'what': "MM1-v2's forecasts for E207's 53 points (THE BLIND MATMUL DAY: aifoundry3 card 0 at its pinned 600 MHz, rgm136 unchanged), "
                    "from the frozen predictor in tools/matmul/mm1/v2 unchanged",
            'model': 'MM1-v2', 'card': CARD, 'card_key': M2.CKEY[CARD], 'f_mhz': F_MHZ, 'V': V, 's_V': (V / 0.517) ** 2, 'G': C.G_of_f(CARD, F_MHZ),
            'V_why': "the predictor's own default for this card (mm1_core_v2.CARD_V, 0.522 V: the footing of MM1-v2's aifoundry3 fit and of MM1-v1's blind day)",
            'clock_routes': "one: the card is pinned at 600 MHz, so 'given the measured clock' and 'with the clock forecast' are the same call",
            'kind_specs': "as MM1-v1's blind day (blind_day_v1.kind_specs): random from ledger v2's own rows; e37 from ledger v2's fp32.small_int "
                          "with the e37 generator's phi; blind4 and blind3 by their own sources, which MM1-v2's predictor does not price",
            'points_file': V1_LIST_REL, 'points_sha256': V1_LIST_SHA,
            'e207_registration_points': {'path': E207_POINTS_REL, 'sha256_pinned': E207_POINTS_SHA,
                                         'rule': 'checked when found (exit 4 on any difference); the mask compared as a number'},
            'n_points': len(rows), 'n_cases_time': len({x['case'] for x in rows}), 'n_energy_forecast': len(rows) - len(nf),
            'energy_not_forecast': nf, 'scored_in_watts_E207': [x['id'] for x in rows if x['scored_in_watts_E207']],
            'frozen_files_sha256': {q: sha(os.path.join(HERE, q)) for q in SHOWN}, 'sha256sums_checked': n,
            'python': sys.version.split()[0], 'numpy': np.__version__, 'scope': C.SCOPE, 'rows': full}
    with open(os.path.join(out, NAMES[1]), 'w') as fh:
        json.dump(meta, fh, indent=1)
        fh.write('\n')
    for x in rows:
        print(f"{x['id']} {x['arm']:12s} {x['fmt']} {x['kind'][:12]:12s} {x['mask']:10s} cyc {x['cycles_per_op_wall']:9.3f} mean {x['cycles_per_op_mean']:9.3f} "
              f"s {x['seconds_per_gemm']:.9f} W {x['W_over_idle']} J {x['J_over_idle_per_gemm']}")
    print(ctext)
    print(f"points {len(rows)}; cases {meta['n_cases_time']}; energy forecast {len(rows) - len(nf)}; energy NOT FORECAST {len(nf)}: "
          f"{[x['id'] for x in nf]}; SHA256SUMS {n} of {n} equal")
    for nm in NAMES:
        print(sha(os.path.join(out, nm)), nm)


if __name__ == '__main__':
    main()
