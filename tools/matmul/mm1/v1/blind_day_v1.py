#!/usr/bin/env python3
"""MM1-v1's forecasts for THE BLIND MATMUL DAY (aifoundry3 card 0, 600 MHz as found, rgm136 unchanged), and the day's point list: mm-synth's
54-point plan revised as mm-critic said (time scored per distinct (shape, format, mask) case; points under about 3 W over idle scored in watts;
long-K all-fresh points added; never-run points only) and for mm1v0-e206's findings (int8 one-K-block shapes not in E206, the power-of-two
neighbours kept). Desk.

    /usr/bin/python3 -I -B blind_day_v1.py --out <dir> [--found found.json ...] [--e208-arms arms.json]
        writes mm1_v1_blind_day.csv / .json (the forecasts), blind_day_points.csv (the list), and with --found the never-run record
        neverrun_blind_day.json

Every point never ran as a (arm, format, data kind, minions, mask) configuration on any card, by E206's own scanner over every data directory
of ours (the lab's committed data at GitHub main, the round's lane folders, the model session's sweep folder) and by the model session's
planned sweep (E208, 1116-mmsweep: its arms.json, planned or run). A point with a run anywhere is dropped, never forecast.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mm1_core as C  # noqa: E402
import mm1_v1 as M1  # noqa: E402

CARD = 'aifoundry3 card 0'
F_MHZ = 600.0
V_A3 = 0.522
REST_HIGH_W = 26.0      # planning peak: aifoundry3's high-side rest + 1.10 x W over idle + 1 W (mm-synth's planning form)
LOW_W = 3.0
KT = 'tools/claims-v3/kinds/'
RANDN = {'fp32': KT + 'tiles/fp32/randn.bin', 'fp16': KT + 'tiles/fp16/randn.bin', 'int8': KT + 'tiles/int8/full.bin'}
B4 = {'fp32': ['fp32.real_pythia_embed_qkv', 'fp32.real_qwen_q_down'], 'fp16': ['fp16.real_pythia_embed_qkv', 'fp16.real_qwen_ln_down'],
      'int8': ['int8.real_pythia_embed_mlpout', 'int8.real_qwen_q_down']}


def P_(pid, fam, mb, nb, kb, fmt, kind='random', mask='0xffffffff', note=''):
    return {'id': pid, 'family': fam, 'arm': f'gemmL{mb}x{nb}x{kb}', 'fmt': fmt, 'kind': kind, 'mask': mask, 'note': note}


POINTS = [
    P_('b01', 'inside', 1, 3, 2, 'fp32'), P_('b02', 'inside', 1, 3, 2, 'int8'), P_('b03', 'inside', 1, 3, 2, 'fp16'),
    P_('b04', 'inside', 2, 3, 2, 'fp32'), P_('b05', 'inside', 2, 3, 2, 'int8'), P_('b06', 'inside', 3, 2, 2, 'fp32'),
    P_('b07', 'inside', 3, 2, 2, 'int8'), P_('b08', 'inside', 1, 4, 3, 'fp32'), P_('b09', 'inside', 1, 4, 3, 'int8'),
    P_('b10', 'knee', 1, 9, 3, 'fp32'), P_('b11', 'knee', 1, 9, 3, 'int8'), P_('b12', 'knee', 2, 3, 5, 'fp32'), P_('b13', 'knee', 2, 3, 5, 'int8'),
    P_('b14', 'knee', 2, 3, 5, 'fp16'), P_('b15', 'knee', 3, 3, 4, 'fp32'), P_('b16', 'knee', 3, 3, 4, 'int8'), P_('b17', 'knee', 5, 2, 3, 'fp32'),
    P_('b18', 'knee', 5, 2, 3, 'int8'),
    P_('b19', 'past', 3, 5, 5, 'fp32'), P_('b20', 'past', 3, 5, 5, 'int8'), P_('b21', 'past', 5, 3, 6, 'fp32'), P_('b22', 'past', 2, 6, 10, 'fp32'),
    P_('b23', 'past', 1, 3, 24, 'fp32'), P_('b24', 'past', 1, 3, 24, 'int8'), P_('b25', 'past', 6, 6, 6, 'fp32'), P_('b26', 'past', 6, 6, 6, 'fp16'),
    P_('b27', 'stride', 1, 7, 6, 'fp32'), P_('b28', 'stride', 1, 8, 6, 'fp32'), P_('b29', 'stride', 1, 9, 6, 'fp32'), P_('b30', 'stride', 1, 4, 12, 'fp32'),
    P_('b31', 'stride', 1, 5, 10, 'fp32'), P_('b32', 'stride', 1, 8, 6, 'int8'), P_('b33', 'stride', 1, 7, 6, 'int8'),
    P_('b34', 'subset', 3, 6, 4, 'fp32', mask='0x3'), P_('b35', 'subset', 3, 6, 4, 'fp32', mask='0xfff'), P_('b36', 'subset', 3, 6, 4, 'fp32', mask='0xffffff'),
    P_('b37', 'subset', 3, 6, 4, 'fp32', mask='0x0f0f0f0f'), P_('b38', 'subset', 3, 6, 4, 'int8', mask='0x3'),
    P_('b39', 'subset', 3, 6, 4, 'int8', mask='0xffffff'), P_('b40', 'subset', 1, 2, 2, 'fp32', mask='0x3'), P_('b41', 'subset', 1, 2, 2, 'fp32', mask='0xfff'),
    P_('b42', 'kinds', 1, 3, 2, 'fp32', kind='e37', note="the host's e37 generator (+-1, +-2, E37's fill); never on any GEMM"),
    P_('b43', 'kinds', 3, 5, 5, 'fp32', kind='e37', note='as b42, past the L3'),
    P_('b49', 'kinds', 1, 3, 2, 'fp32', kind='real:blind4', note="blind4's committed pythia and qwen tiles, never in a GEMM"),
    P_('b50', 'kinds', 1, 3, 2, 'fp16', kind='real:blind4', note='as b49 in fp16'),
    P_('b51', 'kinds', 1, 3, 2, 'int8', kind='real:blind4', note='as b49 in int8'),
    P_('b52', 'kinds', 3, 5, 5, 'fp32', kind='designed:blind3 a_colconst_b_randn', note="blind3's committed constant-column A against random B"),
    P_('n01', 'int8 one K block', 1, 3, 1, 'int8', note="v1's L2 time in the gemmL loop (T2), blind, on int8 KB = 1 shapes E206 did not run"),
    P_('n02', 'int8 one K block', 3, 5, 1, 'int8', note='as n01, a mixed footprint (41 MB)'),
    P_('n03', 'int8 one K block', 3, 5, 1, 'fp32', note="n02's fp32 twin: the L2 time hides under fp32's 529-cycle floor"),
    P_('n04', 'long K', 1, 7, 16, 'fp32', note="mm-critic F8: long-K all-fresh; beside n05, NB 7 against the power of two 8"),
    P_('n05', 'long K', 1, 8, 16, 'fp32', note='long K, NB a power of two: the stride terms where E190 fp32 sat +6% in sample'),
    P_('n06', 'long K', 2, 3, 16, 'int8', note='long K, all fresh, int8'),
]
DROPPED = [
    ('b44', 'gemmL1x3x2 int8 e37', "no resident price for int8 +-1/+-2 tiles (ledger v2 has int8.pm1, +-1 only; no committed prediction): energy could not be forecast and its time duplicates b02's case"),
    ('b45', 'gemmL3x5x5 int8 e37', 'as b44; duplicates b20'),
    ('b46', 'gemmL1x3x2 fp32 sparse25', 'no resident price for sparse25 (no ledger row, no committed prediction); duplicates b01'),
    ('b47', 'gemmL3x5x5 fp32 sparse25', 'as b46; duplicates b19'),
    ('b48', 'gemmL1x3x2 fp32 ones', 'no resident price for ones in ledger v2 and no committed prediction; duplicates b01'),
    ('b53', 'gemmL1x3x2 fp32 designed pair, original', 'the tile files do not exist yet (to be made by the kit) and no resident prediction exists for them: not forecastable before the freeze'),
    ('b54', 'gemmL1x3x2 fp32 designed pair, permuted', 'as b53'),
]


def kind_specs(p):
    fmt, kind = p['fmt'], p['kind']
    if kind == 'random':
        return None, None, f"{p['arm']}:randn:{RANDN[fmt]}"
    if kind == 'e37':
        return ({'source': 'ledger', 'keys': ['fp32.small_int']}, {'gen': 'e37'}, f"{p['arm']}:e37:{RANDN[fmt]}")
    if kind == 'real:blind4':
        tiles = [f'{KT}blind4/tiles/{fmt}/{t}.bin' for t in B4[fmt]]
        return ({'source': 'blind4', 'keys': B4[fmt]}, {'tiles': [f'tiles/blind4__{fmt}__{t}.bin' for t in B4[fmt]]}, f"{p['arm']}:tiles:" + ','.join(tiles))
    if kind.startswith('designed:blind3'):
        return ({'source': 'blind3', 'keys': ['fp32.a_colconst_b_randn']}, {'tiles': ['tiles/blind3__fp32__a_colconst_b_randn.bin']},
                f"{p['arm']}:tiles:{KT}blind3/tiles/fp32/a_colconst_b_randn.bin")
    raise ValueError(kind)


def kind_scan(p):
    """the data kind as E206's scanner reads it from --values (randn -> random; e37 -> e37; tiles of other files -> tiles:other)"""
    return {'random': 'random', 'e37': 'e37'}.get(p['kind'], 'tiles:other')


def forecasts(M):
    rows = []
    for p in POINTS:
        es, ps, values = kind_specs(p)
        o = M.predict(CARD, p['arm'], p['fmt'], p['kind'], p['mask'], F_MHZ, V_A3, e_res_spec=es, phi_spec=ps)
        b = C.parse_arm(p['arm'])
        mi = C.mask_info(p['mask'])
        w = o.get('W_over_idle')
        sw = o.get('switches') or {}
        row = {'id': p['id'], 'case': f"{p['arm']}|{p['fmt']}|{p['mask']}", 'family': p['family'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'],
               'mask': p['mask'], 'shires': mi['n'], 'minions': 32 * mi['n'], 'M': 1024 * b[0], 'N': 512 * b[1], 'K': 512 * b[2] * C.FMT_W[p['fmt']],
               'values': values, 'footprint_MB': o['footprint_MB'], 'power_of_two_NB': o['power_of_two_NB'],
               'lines_L2': round(o['lines_L2_L3_F'][0], 3), 'lines_L3': round(o['lines_L2_L3_F'][1], 3), 'lines_F': round(o['lines_L2_L3_F'][2], 3),
               'cycles_per_op_wall': round(o['cycles_per_op_wall'], 3), 'cycles_per_op_mean': round(o['cycles_per_op_mean'], 3),
               'ops_per_minion_per_gemm': o['ops_per_minion_per_gemm'], 'cycles_per_gemm_wall': round(o['cycles_per_gemm_wall'], 1),
               'seconds_per_gemm': round(o['seconds_per_gemm'], 9),
               'W_over_idle': (round(w, 4) if w is not None else ''), 'W_affine_A_W': (round(o['W_affine']['A_W'], 5) if w is not None else ''),
               'W_affine_B_W_us': (round(o['W_affine']['B_W_us'], 5) if w is not None else ''),
               'J_over_idle_per_gemm': (round(o['J_over_idle_per_gemm'], 9) if w is not None else ''),
               'rest_law_P_W': (round(o['rest_law']['P_rest_W'], 4) if 'rest_law' in o else ''),
               'J_at_rest_rest_law_REPORTED': (round(o['rest_law']['J_at_rest_per_gemm_REPORTED'], 9) if 'rest_law' in o else ''),
               'scored_in_watts': (w is not None and w < LOW_W), 'e_res_nJ': (round(o['e_res_nJ'], 5) if w is not None else ''),
               'e_res_source': o.get('e_res_source', o.get('energy', '')), 'phi': (round(o['phi'], 4) if w is not None else ''),
               'switches_counted_lo': (sw.get('counted_fin_edges') or [None, None])[0], 'switches_counted_hi': (sw.get('counted_fin_edges') or [None, None])[1],
               'switches_estimated_lo': (sw.get('estimated_fin_edges') or [None] * 3)[0], 'switches_estimated_central': (sw.get('estimated_fin_edges') or [None] * 3)[1],
               'switches_estimated_hi': (sw.get('estimated_fin_edges') or [None] * 3)[2], 'switches_int8_arithmetic_central': sw.get('of_which_int8_arithmetic_central'),
               'fresh_lines_J_apart': sw.get('fresh_lines_J_apart'),
               'sim_steps_per_minion_per_gemm': o['sim_steps_per_minion_per_gemm'], 'floor_cycles_measured_tenb': o['floor_cycles_measured_tenb'],
               'bench_resident_cycles_simulated': o['bench_resident_cycles_simulated'],
               'plan_peak_W': (round(REST_HIGH_W + 1.10 * w + 1.0, 1) if w is not None else ''), 'note': p['note']}
        rows.append(row)
    return rows


def neverrun(found_paths, e208_arms):
    runs = {}
    for fp in found_paths:
        d = json.load(open(fp))
        scans = d['scans'] if 'scans' in d else {'one': d}
        for lab, s in scans.items():
            for key, rec in s['found'].items():
                c = sum(rec['cards'].values())
                if c:
                    runs.setdefault(key, {'card_records': 0, 'cards': set(), 'paths': []})
                    runs[key]['card_records'] += c
                    runs[key]['cards'] |= set(rec['cards'])
                    runs[key]['paths'] += [x for x in rec['paths']][:2]
    planned = set()
    if e208_arms:
        for a in json.load(open(e208_arms))['arms']:
            kind = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}.get(a['kind'], a['kind'])
            planned.add((f"gemmL{a['mb']}x{a['nb']}x{a['kb']}", a['type'], kind, a['shires'].lower()))
    out = []
    for p in POINTS:
        mi = C.mask_info(p['mask'])
        key = f"{p['arm']}|{p['fmt']}|{kind_scan(p)}|{32 * mi['n']}|{p['mask'].lower()}"
        hit = runs.get(key)
        case_hits = [k for k in runs if k.split('|')[0] == p['arm'] and k.split('|')[1] == p['fmt'] and k.split('|')[4] == p['mask'].lower()]
        e208_point = (p['arm'], p['fmt'], p['kind'], p['mask'].lower()) in planned
        e208_case = any((a, t, mk) == (p['arm'], p['fmt'], p['mask'].lower()) for a, t, _, mk in planned)
        out.append({'id': p['id'], 'key': key, 'never_run_point': hit is None and not e208_point, 'never_run_case_any_kind': not case_hits and not e208_case,
                    'card_records': (hit or {}).get('card_records', 0), 'e208_planned_point': e208_point, 'e208_planned_case': e208_case,
                    'case_hits': case_hits[:5]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--params', default=os.path.join(HERE, 'mm1_v1_params.json'))
    ap.add_argument('--found', nargs='*', default=[])
    ap.add_argument('--e208-arms', default=None)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('blind_day_v1.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    M = M1.Model(json.load(open(a.params)))
    rows = forecasts(M)
    with open(os.path.join(out, 'mm1_v1_blind_day.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    meta = {'what': "MM1-v1's frozen forecasts for the blind matmul day (aifoundry3 card 0, 600 MHz pinned, rgm136 unchanged)",
            'params_sha256': hashlib.sha256(open(a.params, 'rb').read()).hexdigest(), 'card': CARD, 'f_mhz': F_MHZ, 'V': V_A3,
            'n_points': len(rows), 'n_cases_time': len({r['case'] for r in rows}), 'dropped_from_mm_synth_plan': [{'id': x[0], 'point': x[1], 'why': x[2]} for x in DROPPED],
            'scored_in_watts': [r['id'] for r in rows if r['scored_in_watts']], 'max_plan_peak_W': max(r['plan_peak_W'] for r in rows if r['plan_peak_W'] != ''),
            'rows': rows}
    json.dump(meta, open(os.path.join(out, 'mm1_v1_blind_day.json'), 'w'), indent=1, default=str)
    nr = None
    if a.found:
        nr = neverrun(a.found, a.e208_arms)
        e208_sha = hashlib.sha256(open(a.e208_arms, 'rb').read()).hexdigest() if a.e208_arms else None
        json.dump({'what': "the blind day points against every GEMM record in our data directories (E206's scanner) and the model session's planned "
                           "sweep (E208, 1116-mmsweep, its arms.json)", 'e208_arms_sha256': e208_sha,
                   'all_never_run_points': all(x['never_run_point'] for x in nr), 'all_never_run_cases': all(x['never_run_case_any_kind'] for x in nr),
                   'rows': nr}, open(os.path.join(out, 'neverrun_blind_day.json'), 'w'), indent=1, default=list)
    for r in rows:
        print(f"{r['id']} {r['family']:16s} {r['arm']:12s} {r['fmt']} {r['kind'][:12]:12s} {r['mask']:10s} F {r['footprint_MB']} cyc {r['cycles_per_op_wall']:8.1f} "
              f"mean {r['cycles_per_op_mean']:8.1f} s {r['seconds_per_gemm']:.6f} W {r['W_over_idle']} peak {r['plan_peak_W']}")
    print('points', len(rows), 'cases', meta['n_cases_time'], 'scored in watts', meta['scored_in_watts'], 'max planned peak', meta['max_plan_peak_W'])
    if nr is not None:
        print('never run (point):', all(x['never_run_point'] for x in nr), '; never run (case, any kind):', all(x['never_run_case_any_kind'] for x in nr))
        for x in nr:
            if not (x['never_run_point'] and x['never_run_case_any_kind']):
                print('   ', x)


if __name__ == '__main__':
    main()
