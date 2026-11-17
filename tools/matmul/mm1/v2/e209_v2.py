#!/usr/bin/env python3
"""MM1-v2: E209's points (the blind matmul day on aifoundry2 card 0 under its governor), the never-run scan, and the forecasts. Desk.

    /usr/bin/python3 -I -B e209_v2.py scan --lab <the lab's top> --out <dir> [--extra <dir> ...]
        greps every rgm136 shape of the list below in the lab's data and tools, and in the extra folders (the round's lane folders, the lab
        account's work folders on aifoundry2), and writes <dir>/neverrun_e209.json: every hit with its path and whether the path is aifoundry2
        run data (a hit there takes the shape off the list).
    /usr/bin/python3 -I -B e209_v2.py forecast --params <mm1_v2_params.json> --scan <neverrun_e209.json> --out <dir>
        writes <dir>/e209_points.csv (the point list), <dir>/mm1_v2_e209.csv and .json (MM1-v2's forecasts: given the measured clock, at the
        top point's measured kernel clock 799.0 MHz and at 700 and 600 MHz, and with the clock forecast by the governor model) and
        <dir>/mm1_v1_e209.csv (MM1-v1 as landed, unchanged, called with aifoundry2's arguments at the same clocks).

THE CARD: aifoundry2 card 0 under its own governor, as found (TDP 65 W, threshold 65 C, power state 3: E208's config reads), nothing set;
  rgm136 unchanged (kernel ELF aace138c..., E206's and E208's host flags); each process a 6 s burst (E208's form).
THE CLOCK: 'given the measured clock' = the frozen predictor at the run's measured kernel clock in its scored window (the volts and the
  governed base from the clock: mm1_core_v2.volts, G_of_f); the frozen table gives it at 799.0 MHz (E208's aifoundry2 win-view median),
  700 and 600 MHz. 'With the clock forecast' = the frozen predictor at the governor model's forecast (governor_v2.forecast_clock): the
  win view's clock (the top point, 799.0 MHz, when any launch 1.0-3.5 s into a process holds it), whether the run is capped (the reducer's
  rule: under 80% of the launches after 1.0 s in the 800 MHz band), and the burst's mean clock.
PLANNING (not forecasts of a stop): the predicted board power at the top point (the rest law's rest at 51 C + v2's W over idle) and at the
  burst's mean clock; the die at most over a 6 s burst (die0 + k_die (P - rest), governor_v2's fitted k_die) and over three back-to-back
  processes (die0 + 0.30 C/W x (P - rest): a desk estimate between the burst slope and E64's sustained 0.47 C/W); the kit's stops (E194's and
  E200's kits on this card: board above 85 W on 3 samples in a row; the shires' mean or the hottest sensor at or above 80 C).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import governor_v2 as GV  # noqa: E402
import mm1_core_v2 as C  # noqa: E402
import mm1_v2 as M2  # noqa: E402

CARD = 'aifoundry2 card 0'
F_TOP = 799.0
REAL_TILES = {'fp32': ['gpt2_l9_attn_qk', 'gpt2_l3_mlp_down', 'bert_l6_up', 'vit_l5_down'],
              'fp16': ['gpt2_l9_attn_qk', 'bert_l6_up', 'vit_l5_down', 'gpt2_l6_mlp_down_fp16fwd'],
              'int8': ['gpt2_l6_down_p999', 'gpt2_l6_down_p9999', 'gpt2_l6_down_per_token', 'gpt2_l11_down_p999']}
W_FMT = {'fp32': 1, 'fp16': 2, 'int8': 4}

# (id, family, arm, format, kind, mask, runs) - every shape never run on aifoundry2's card (the scan checks it)
LIST = [
    # inside the L3
    ('e01', 'inside the L3', 'gemmL1x3x2', 'int8', 'random', '0xffffffff', 2),
    ('e02', 'inside the L3', 'gemmL2x3x2', 'fp16', 'random', '0xffffffff', 1),
    ('e03', 'inside the L3', 'gemmL3x2x2', 'int8', 'zeros', '0xffffffff', 1),
    ('e04', 'inside the L3', 'gemmL1x3x2', 'fp32', 'random', '0x0000ffff', 2),
    ('e05', 'inside the L3', 'gemmL1x4x3', 'fp32', 'ones', '0xffffffff', 1),
    ('e06', 'inside the L3', 'gemmL2x3x2', 'fp32', 'zeros', '0xffffffff', 1),
    # one K block (the L2 time)
    ('e07', 'one K block', 'gemmL1x3x1', 'int8', 'random', '0xffffffff', 2),
    ('e08', 'one K block', 'gemmL3x5x1', 'int8', 'random', '0xffffffff', 1),
    ('e09', 'subsets', 'gemmL2x1x3', 'fp32', 'random', '0x000000ff', 1),
    # the knee
    ('e10', 'the knee', 'gemmL1x1x11', 'fp32', 'random', '0xffffffff', 2),
    ('e11', 'the knee', 'gemmL1x1x13', 'fp32', 'zeros', '0xffffffff', 1),
    ('e12', 'the knee', 'gemmL1x2x9', 'fp32', 'random', '0xffffffff', 2),
    ('e13', 'the knee', 'gemmL2x1x6', 'int8', 'random', '0xffffffff', 1),
    ('e14', 'the knee', 'gemmL2x2x5', 'fp16', 'random', '0xffffffff', 1),
    ('e15', 'the knee', 'gemmL3x1x5', 'fp32', 'zeros', '0xffffffff', 1),
    ('e16', 'the knee', 'gemmL1x3x7', 'int8', 'random', '0xffffffff', 1),
    ('e17', 'subsets', 'gemmL1x1x7', 'int8', 'random', '0x0000000f', 1),
    # past the L3
    ('e18', 'past the L3', 'gemmL2x6x10', 'fp32', 'random', '0xffffffff', 2),
    ('e19', 'past the L3', 'gemmL3x5x5', 'fp16', 'random', '0xffffffff', 1),
    ('e20', 'past the L3', 'gemmL6x6x6', 'int8', 'random', '0xffffffff', 1),
    ('e21', 'past the L3', 'gemmL5x3x6', 'fp32', 'zeros', '0xffffffff', 1),
    ('e22', 'past the L3', 'gemmL3x5x5', 'int8', 'ones', '0xffffffff', 1),
    # long K
    ('e23', 'long K', 'gemmL1x1x40', 'fp32', 'random', '0xffffffff', 2),
    ('e24', 'long K', 'gemmL1x2x24', 'fp32', 'zeros', '0xffffffff', 1),
    ('e25', 'long K', 'gemmL2x1x20', 'int8', 'random', '0xffffffff', 1),
    ('e26', 'long K', 'gemmL1x2x14', 'int8', 'random', '0xffffffff', 1),
    ('e27', 'long K', 'gemmL2x3x16', 'fp16', 'random', '0xffffffff', 1),
    # power-of-two strides (NB a power of two >= 4 past 32 MB, each beside a neighbour)
    ('e28', 'power-of-two stride', 'gemmL1x8x6', 'fp32', 'random', '0xffffffff', 2),
    ('e29', 'power-of-two stride', 'gemmL1x7x6', 'fp32', 'random', '0xffffffff', 2),
    ('e30', 'power-of-two stride', 'gemmL2x8x4', 'int8', 'random', '0xffffffff', 1),
    ('e31', 'subsets', 'gemmL2x3x2', 'int8', 'random', '0x00001111', 1),
    ('e32', 'power-of-two stride', 'gemmL1x4x12', 'fp32', 'random', '0xffffffff', 1),
    ('e33', 'power-of-two stride', 'gemmL1x16x6', 'fp16', 'random', '0xffffffff', 1),
    # data kinds (real: E206's four tiles a format; ones; zeros)
    ('e34', 'kinds', 'gemmL2x6x10', 'fp32', 'real', '0xffffffff', 2),
    ('e35', 'kinds', 'gemmL1x3x2', 'int8', 'real', '0xffffffff', 1),
    ('e36', 'kinds', 'gemmL3x5x5', 'fp16', 'real', '0xffffffff', 1),
    ('e37', 'kinds', 'gemmL2x6x10', 'fp16', 'ones', '0xffffffff', 1),
    ('e38', 'kinds', 'gemmL6x6x6', 'int8', 'zeros', '0xffffffff', 1),
    # shire subsets (16, 4 and 1 shires; layouts never run on this card)
    ('e39', 'subsets', 'gemmL2x6x10', 'fp32', 'random', '0x80000000', 1),
    ('e40', 'subsets', 'gemmL1x8x6', 'fp32', 'random', '0x00001111', 1),
    ('e41', 'subsets', 'gemmL3x5x5', 'fp32', 'random', '0xffff0000', 1),
    ('e42', 'subsets', 'gemmL6x6x6', 'int8', 'random', '0x0000f000', 1),
    ('e43', 'subsets', 'gemmL1x3x2', 'fp16', 'random', '0x00000001', 1),
    # the governor (forecast capped by the power loop: time and clock read, energy not read under E208's reducer rule)
    ('e44', 'governor', 'gemmL1x3x2', 'fp32', 'random', '0xffffffff', 1),
    ('e45', 'governor', 'gemmL1x4x3', 'fp16', 'random', '0xffffffff', 1),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def shapes():
    return sorted({x[2] for x in LIST})


def a2_context(path):
    """is a hit's path aifoundry2 run data? (conservative: a data folder not named for another card counts as aifoundry2's)"""
    p = path.replace('\\', '/')
    if '/docs/reports/data/' in p:
        d = p.split('/docs/reports/data/')[1].split('/')[0]
        other = ('aifoundry3' in d or 'aifoundry1' in d or re.search(r'(^|-)a3-|(^|-)a1c[01]', d) or '-a1c0-' in d or '-a1c1-' in d)
        return not other
    m = re.search(r'/out/([^/]+)/', p)
    if m:
        lane = m.group(1)
        return bool(re.match(r'(a2-|card-a2|card-e190$|card-e194$|card-e200$|card-e208)', lane)) or (lane == 'data-e208' and 'a2c0' in p)
    if '/ee-1116-mmsweep/sessions/' in p:
        return 'a2c0' in p
    if '/claude/work/' in p and 'aifoundry2' in p:
        return True
    return False


def scan(lab, extra, out):
    toks = shapes()
    pat = 'gemmL(' + '|'.join(t[5:] for t in toks) + ')([^0-9]|$)'
    roots = [os.path.join(lab, 'docs'), os.path.join(lab, 'tools')] + list(extra)
    labels = {os.path.join(lab, 'docs'): '<lab>/docs', os.path.join(lab, 'tools'): '<lab>/tools'}
    for i, x in enumerate(extra):
        labels[x] = '<extra%d:%s>' % (i, os.path.basename(x.rstrip('/')))

    def rel(path):
        for top, lab_ in labels.items():
            if path.startswith(top.rstrip('/') + '/'):
                return lab_ + path[len(top.rstrip('/')):]
        return '<elsewhere>'
    hits = {t: [] for t in toks}
    nfiles = {}
    for top in roots:
        if not os.path.exists(top):
            continue
        r = subprocess.run(['grep', '-rIoE', '--exclude-dir=.git', pat, top], capture_output=True, text=True)
        for ln in r.stdout.splitlines():
            path, _, m = ln.partition(':')
            tok = re.match(r'gemmL\d+x\d+x\d+', m)
            if tok and tok.group(0) in hits:
                hits[tok.group(0)].append(path)
        nfiles[top] = sum(len(fs) for _, _, fs in os.walk(top))
    res = {'what': "every rgm136 shape of E209's list grepped (token gemmL<MB>x<NB>x<KB> not followed by a digit); paths are relative to their folder's label",
           'pattern': pat, 'roots': [labels[r] for r in roots], 'files_under_root': {labels[k]: v for k, v in nfiles.items()}, 'shapes': {}}
    for t in toks:
        ps = sorted(set(hits[t]))
        a2 = [p for p in ps if a2_context(p)]
        res['shapes'][t] = {'n_files': len(ps), 'aifoundry2_run_data': [rel(p) for p in a2], 'other_paths_sample': [rel(p) for p in ps if p not in a2][:12],
                            'never_run_on_aifoundry2': len(a2) == 0}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'neverrun_e209.json'), 'w'), indent=1, sort_keys=True)
    bad = [t for t in toks if not res['shapes'][t]['never_run_on_aifoundry2']]
    print('shapes', len(toks), 'with aifoundry2 run data', bad)
    for t in bad:
        print(t, res['shapes'][t]['aifoundry2_run_data'][:5])


def specs(fmt, kind):
    if kind == 'real':
        return ({'source': 'ledger', 'keys': [f'{fmt}.real2:{t}' for t in REAL_TILES[fmt]]},
                {'tiles': [f'tiles/real2__{fmt}__{t}.bin' for t in REAL_TILES[fmt]]})
    return None, None


def values_arg(arm, fmt, kind):
    if kind == 'random':
        tile = 'full.bin' if fmt == 'int8' else 'randn.bin'
        return f'{arm}:randn:src/tiles/{fmt}/{tile}'
    if kind in ('zeros', 'ones'):
        return f'{arm}:tiles:src/tiles/{fmt}/{kind}.bin'
    return f'{arm}:tiles:' + ','.join(f'tools/claims-v3/kinds/real2/tiles/{fmt}/{t}.bin' for t in REAL_TILES[fmt])


def load_v1():
    v1 = os.path.normpath(os.path.join(HERE, '..', 'v1'))
    n, bad = 0, []
    for ln in open(os.path.join(v1, 'SHA256SUMS')):
        if ln.strip():
            h, p = ln.rstrip('\n').split('  ', 1)
            n += 1
            if sha(os.path.join(v1, p)) != h:
                bad.append(p)
    if bad:
        sys.exit(f'MM1-v1 not as landed: {bad[:4]}')
    sys.path.insert(0, v1)
    spec = importlib.util.spec_from_file_location('mm1_v1_landed', os.path.join(v1, 'mm1_v1.py'))
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    import kinds_v1 as K1
    sys.path.remove(v1)
    return M.Model(json.load(open(os.path.join(v1, 'out', 'mm1_v1_params.json')))), K1, n


def v1_call(M1, K1, p, f):
    """MM1-v1 unchanged with aifoundry2's arguments: f, V by the energy manual's line, G by the M7 relation; kinds as v1 prices them"""
    V = C.interp_pts(C.V_LAW, f)
    G = C.G_of_f(CARD, f)
    es = ps = None
    if p['kind'] == 'ones':
        es, ps = {'source': None}, {'gen': 'zeros'}
    elif p['kind'] == 'real':
        es, ps = ({'source': 'ledger', 'keys': [f"{p['fmt']}.real2:{t}" for t in REAL_TILES[p['fmt']]]},
                  {'tiles': [f"tiles/real2__{p['fmt']}__{t}.bin" for t in REAL_TILES[p['fmt']]]})
    o = M1.predict(CARD, p['arm'], p['fmt'], p['kind'], p['mask'], f, V, G=G, e_res_spec=es, phi_spec=ps, ops=p['ops'], minions=p['minions'])
    return o


def forecast(params_path, scan_path, out):
    P = json.load(open(params_path))
    M = M2.Model(P)
    M1, K1, n1 = load_v1()
    sc = json.load(open(scan_path))
    prm = P['governor']['constants']
    RL = P['rest_law']
    T0 = RL[CARD]['T0_forecast_c']
    rest = RL[CARD]['a'] * T0 * T0 + RL[CARD]['b'] * T0 + RL[CARD]['c']
    pts, rows, rows1, full = [], [], [], []
    for (pid, fam, arm, fmt, kind, mask, nruns) in LIST:
        if not sc['shapes'][arm]['never_run_on_aifoundry2']:
            continue
        MB, NB, KB = C.parse_arm(arm)
        mi = C.mask_info(mask)
        p = {'id': pid, 'family': fam, 'arm': arm, 'fmt': fmt, 'kind': kind, 'mask': mask, 'shires': mi['n'], 'minions': 32 * mi['n'],
             'M': 1024 * MB, 'N': 512 * NB, 'K': 512 * KB * W_FMT[fmt], 'ops': 64 * MB * NB * KB, 'runs_planned': nruns,
             'case': f'{arm}|{fmt}|{kind}|{mask}', 'values': values_arg(arm, fmt, kind), 'footprint_MB': C.footprint(MB, NB, KB)}
        es, ps = specs(fmt, kind)
        fc = {f: M.predict(CARD, arm, fmt, kind, mask, f, ops=p['ops'], minions=p['minions'], e_res_spec=es, phi_spec=ps) for f in (F_TOP, 700.0, 600.0)}
        g = GV.forecast_clock(M, CARD, arm, fmt, kind, mask, prm, RL, ops=p['ops'], minions=p['minions'], e_res_spec=es, phi_spec=ps)
        fwin = F_TOP if g.get('f_win') else None
        fbur = g.get('f_burst_mean')
        o_cf = M.predict(CARD, arm, fmt, kind, mask, fbur, ops=p['ops'], minions=p['minions'], e_res_spec=es, phi_spec=ps) if fbur else None
        W8 = fc[F_TOP].get('W_over_idle')
        P8 = rest + W8 if W8 is not None else None
        die0 = T0
        kd = prm['k_die']
        p.update({'pred_board_top_W': P8, 'pred_board_peak_planning_W': (P8 + 2.0) if P8 else None,
                  'pred_die_peak_burst_c': (die0 + kd * W8) if W8 else None, 'pred_die_peak_3proc_c': (die0 + 0.30 * W8) if W8 else None,
                  'pred_capped': g.get('capped'), 'form_planned': ('sus3' if (W8 is not None and W8 < 8.0) else 'burst')})
        pts.append(p)
        r = {'id': pid, 'case': p['case'], 'family': fam, 'arm': arm, 'fmt': fmt, 'kind': kind, 'mask': mask, 'shires': mi['n'], 'ops_per_minion_per_gemm': p['ops'],
             'footprint_MB': round(p['footprint_MB'], 1)}
        for f in (F_TOP, 700.0, 600.0):
            o = fc[f]
            tag = str(int(round(f)))
            r[f'cyc_wall@{tag}'] = round(o['cycles_per_op_wall'], 3)
            r[f'cyc_mean@{tag}'] = round(o['cycles_per_op_mean'], 3)
            r[f's_gemm@{tag}'] = round(o['seconds_per_gemm'], 9)
            r[f'W_over@{tag}'] = round(o['W_over_idle'], 4) if 'W_over_idle' in o else ''
            r[f'W_A@{tag}'] = round(o['W_affine']['A_W'], 5) if 'W_over_idle' in o else ''
            r[f'W_B_us@{tag}'] = round(o['W_affine']['B_W_us'], 5) if 'W_over_idle' in o else ''
            r[f'J_over@{tag}'] = round(o['J_over_idle_per_gemm'], 9) if 'W_over_idle' in o else ''
        r.update({'clock_fc_win_mhz': fwin or '', 'clock_fc_capped': g.get('capped'), 'clock_fc_burst_mean_mhz': round(fbur, 2) if fbur else '',
                  'clock_fc_frac800_after_1s': round(g.get('frac_800_after_1s', 0), 3) if 'frac_800_after_1s' in g else '',
                  'cyc_wall@clock_fc_burst': round(o_cf['cycles_per_op_wall'], 3) if o_cf else '', 's_gemm@clock_fc_burst': round(o_cf['seconds_per_gemm'], 9) if o_cf else '',
                  'W_over@clock_fc_burst': round(o_cf['W_over_idle'], 4) if (o_cf and 'W_over_idle' in o_cf) else '',
                  'rest_law_W': round(rest, 4), 'J_rest_law@799_REPORTED': round((rest + W8) * fc[F_TOP]['seconds_per_gemm'], 9) if W8 is not None else '',
                  'under_3W_over_idle': (bool(W8 < 3.0) if W8 is not None else ''), 'pred_board_top_W': round(P8, 2) if P8 else '',
                  'pred_capped': g.get('capped'), 'e_res_source': fc[F_TOP].get('e_res_source', ''), 'energy_note': fc[F_TOP].get('energy', ''),
                  'switches_estimated_central@799': (fc[F_TOP]['switches']['estimated_fin_edges'][1] if 'switches' in fc[F_TOP] else ''),
                  'switches_counted_hi@799': (fc[F_TOP]['switches']['counted_fin_edges'][1] if 'switches' in fc[F_TOP] and fc[F_TOP]['switches']['counted_fin_edges'][1] else ''),
                  'sim_steps_per_minion_per_gemm': fc[F_TOP]['sim_steps_per_minion_per_gemm'], 'floor_cycles_measured_tenb': fc[F_TOP]['floor_cycles_measured_tenb']})
        rows.append(r)
        full.append({'id': pid, 'point': p, 'v2': {str(int(round(f))): fc[f] for f in fc}, 'clock_forecast': g, 'v2_at_clock_forecast_burst': o_cf})
        r1 = {'id': pid, 'case': p['case']}
        for f in (F_TOP, 700.0, 600.0):
            o1 = v1_call(M1, K1, p, f)
            tag = str(int(round(f)))
            r1[f'cyc_wall@{tag}'] = round(o1['cycles_per_op_wall'], 3)
            r1[f'cyc_mean@{tag}'] = round(o1['cycles_per_op_mean'], 3)
            r1[f's_gemm@{tag}'] = round(o1['seconds_per_gemm'], 9)
            r1[f'W_over@{tag}'] = round(o1['W_over_idle'], 4) if 'W_over_idle' in o1 else ''
            r1[f'W_A@{tag}'] = round(o1['W_affine']['A_W'], 5) if 'W_over_idle' in o1 else ''
            r1[f'W_B_us@{tag}'] = round(o1['W_affine']['B_W_us'], 5) if 'W_over_idle' in o1 else ''
            r1[f'J_over@{tag}'] = round(o1['J_over_idle_per_gemm'], 9) if 'W_over_idle' in o1 else ''
            r1[f'energy_note@{tag}'] = o1.get('energy', '') if 'W_over_idle' not in o1 else ''
        rows1.append(r1)
    os.makedirs(out, exist_ok=True)
    for name, rr in (('e209_points.csv', pts), ('mm1_v2_e209.csv', rows), ('mm1_v1_e209.csv', rows1)):
        keys = list(rr[0])
        with open(os.path.join(out, name), 'w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=keys, lineterminator='\n')
            w.writeheader()
            for x in rr:
                w.writerow(x)
    runs = sum(p['runs_planned'] for p in pts)
    burst = sum(p['runs_planned'] for p in pts if p['form_planned'] == 'burst')
    sus = runs - burst
    plan_e208_forms = (burst * 23.0 + sus * 70.0) / 60.0
    plan_all_sus3 = runs * 70.0 / 60.0
    meta = {'what': "MM1-v2's forecasts for E209's points (aifoundry2 card 0 under its governor), frozen by the files' sha256",
            'card': CARD, 'f_top_measured_mhz': F_TOP, 'rest_law_T0_c': T0, 'rest_law_W': rest, 'governor_constants': prm, 'params_sha256': sha(params_path),
            'scan_sha256': sha(scan_path), 'v1_sha256sums_checked': n1, 'n_points': len(pts), 'n_runs_planned': runs,
            'planning_card_minutes': {'E208 forms (burst 23 s, three-process 70 s a run, gates included, as E208 a2c0-S1 averaged)': round(plan_e208_forms, 1),
                                      'every run three processes (70 s a run)': round(plan_all_sus3, 1), 'plus the anchor (E208 4x8x8-int8-rnd), the smoke and the opening rest': 'about 5'},
            'python': sys.version.split()[0], 'numpy': np.__version__, 'rows': full}
    json.dump(meta, open(os.path.join(out, 'mm1_v2_e209.json'), 'w'), indent=1, default=float)
    print('points', len(pts), 'runs', runs, 'burst', burst, 'sus3', sus, 'card-minutes E208 forms', round(plan_e208_forms, 1), 'all sus3', round(plan_all_sus3, 1))
    for r in rows:
        print(r['id'], r['case'].ljust(36), 'cyc', r['cyc_wall@799'], 'W', r['W_over@799'], 'P', r['pred_board_top_W'], 'capped', r['pred_capped'], 'fbur', r['clock_fc_burst_mean_mhz'])
    for name in ('e209_points.csv', 'mm1_v2_e209.csv', 'mm1_v2_e209.json', 'mm1_v1_e209.csv'):
        print(sha(os.path.join(out, name)), name)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--out', required=True)
    a1.add_argument('--extra', action='append', default=[])
    a2 = sp.add_parser('forecast')
    a2.add_argument('--params', required=True)
    a2.add_argument('--scan', required=True)
    a2.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(os.path.abspath(a.lab), [os.path.abspath(x) for x in a.extra], os.path.abspath(a.out))
    else:
        forecast(os.path.abspath(a.params), os.path.abspath(a.scan), os.path.abspath(a.out))


if __name__ == '__main__':
    main()
