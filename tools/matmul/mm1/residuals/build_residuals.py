#!/usr/bin/env python3
"""MM1 residuals, step 1: every residual of the lab's matmul models on data they did not fit, one row a (set, point). Desk; POST HOC.

    /usr/bin/python3 -I -B build_residuals.py --lab <lab repo top> --out <dir>
        writes <dir>/residual-rows.json (every row: the point's attributes, the measured values, each model's forecast, the errors)
        and prints the cross-checks against the lab's committed scorers. Refuses (exit 4) if any forecast or data file differs from its pin.

Own code: the standard library only; nothing is imported from MM1 (v0, v1, v2), the kits, the reducers or the ledger. The forecast files
and the data files are read as data, after their sha256 is checked against the pins below (each pin is the sha256 that the file's own
freeze record or SHA256SUMS lists at the commit named beside it).

THE SETS (label: BLIND = forecast frozen before the data existed; UNREAD = forecast made by a frozen model after the data existed but without
reading it; HELD OUT = the model refitted without that experiment (LOEO) or card (LOCO): post hoc model selection, never blind):
  v0-E206A   MM1-v0 BLIND on E206 arm A (aifoundry3 card 0, 600 MHz; forecasts tools/matmul/mm1/v0/mm1_v0_e206.csv; data d7e4f35e)
  v0-E206B   MM1-v0 BLIND on E206 arm B (aifoundry1 card 1, 600 MHz; forecasts e35a06cb; data 79340bfa; scores f155c8ca)
  v1-E206B   MM1-v1 BLIND on E206 arm B (forecasts d3f031d1; data 79340bfa)
  v1-E207    MM1-v1 BLIND on E207 (aifoundry3 card 0; forecasts 25d2e74e; data 867f6a3f; scores f5c53145)
  v1-E208    MM1-v1 UNREAD on E208's six sessions (forecasts tools/matmul/mm1/v2/out/unread_e208.csv, 3ca4b717; data e99209a5, eed9624f,
             d40b6fe8, 76fb5344, 7693a23c, c2d6536c)
  v0-E208    MM1-v0 UNREAD on the same runs
  v2-E207    MM1-v2 BLIND on E207 (forecasts 4e518735; scored 030ffa42)
  v2-LOEO    MM1-v2 HELD OUT, leave one experiment out (tools/matmul/mm1/v2/out/points_time_v2.csv, points_energy_v2.csv; 3ca4b717)
  v2-LOCO    MM1-v2 HELD OUT, leave one card out (the same files)
  E208's seventh session a2c0-S1r (5d99fe17) has no frozen-model forecast of its own (the UNREAD forecasts depend on each run's measured
  clock and volts): it enters only as the repeat floor (its committed repeat table) and as a side check (S1r's runs against S1's UNREAD
  forecast for the same arm, labelled 'matched', never pooled).

MEASURED (own reduction, the registered definitions): E206 and E207: a point = the mean of its kept pass-1 / pass-2 runs (a run is kept when its
record names the point's arm, format, minions and mask and carries t, p_work, p_rest and cycles); cycles an op on the wall = mean(cycles_gemm)
/ ops a minion; the counter's mean = mean(cycles_per_op); t = mean(t_gemm_s); W over idle = mean(p_work - p_rest); J over idle = mean((p_work
- p_rest) t); J at rest = mean(p_work t); rest = mean(p_rest). E208: a run's primary view (the registered reducer's output): cyc_op_max,
cyc_op_mean, t_pass_s, kclock_mhz, dP_w, p_mean_w - dP_w, J_pass_over, J_pass_with; no energy for a capped run or a 'time' run; null runs out.
The held-out sets: the measured values as MM1-v2's fit tabled them (re-derived here only for E206 arm A and E208, as a cross-check).

ERRORS: e = forecast / measured - 1. Quantities: cyc_wall, cyc_mean, t (seconds a GEMM), jo_g (J over idle given the measured seconds), jo_f
(J over idle with the seconds forecast), jr_g / jr_f (J with the card at rest, given / forecast seconds; the run's measured rest power for every
model, as the lab's scorers did). Given the measured seconds, W is the model's own affine form W = A + B / T: W_g = A + (W_f - A) t_f / t_meas,
with A = MM1-v0's awake power x minions / 1,024 (its frozen card term) or MM1-v1's / MM1-v2's W_affine_A_W column; E208's UNREAD rows carry
the scorer's given-t W column (no A column there). Points under 3 W over idle are scored in watts by the lab: their jo_* stay in the rows,
flagged low_w, and leave the percentage pools.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys

PINS = {  # path from the lab's top: sha256 (the file's freeze record or SHA256SUMS at the named commit)
    'tools/matmul/mm1/v0/mm1_v0_e206.csv': '5759fb7b34fd21101930e4b128931effbf03d839cd5350d2bfbc490a64d90733',       # v0 README freeze line
    'tools/matmul/mm1/v0/mm1_v0_params.json': '370f780cceada134aa3451ed46f5d8cc22a520665e92caf1d92ae532dfc8cde6',     # v0 README freeze line
    'tools/matmul/mm1/v0/forecasts-e206-armB.csv': '1edf61ff0d7a4c40c25131e79bb702bab104c6379d71a26653486ed86a798aae',  # e35a06cb
    'tools/matmul/mm1/v0/forecasts-e206-armB.json': '7f5aef5f782267b4663236ca75a824191b33426831dfcfd41c4f5898d7244f56',  # e35a06cb
    'tools/matmul/mm1/v1/forecasts-e206-armB.csv': '3f9340020c061a264254b4497039127dd46f55c37d51f891abb8930cc5b8f02a',  # d3f031d1
    'tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv': '90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6',  # 25d2e74e, E207.md
    'tools/matmul/mm1/v2/forecasts-e207.csv': '873360bb7ef028c4922f6f55c6c61133a32da28fa6e19a6a02fa7f77d45d63d3',      # 4e518735
    'tools/matmul/mm1/v2/out/unread_e208.csv': 'd5757c8280d3543cf8a235e79704fee4d9ed013f604878b26eba510464bf4adb',     # 3ca4b717
    'tools/matmul/mm1/v2/out/points_time_v2.csv': '78e56a1187a032fe81f8cfe131aca15a8e493e6fc26411acd7962a4425fb6f52',  # 3ca4b717
    'tools/matmul/mm1/v2/out/points_energy_v2.csv': 'ae7c32785967b350106f434b37600f63cf1ecbff07e01099e0038574100dd488',  # 3ca4b717
}
E206A = 'docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3'
E206B = 'docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1'
E207 = 'docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3'
E208 = {'a2c0-S1': '2026-11-16-e208-mmsweep-a2c0-S1', 'a2c0-S2': '2026-11-16-e208-mmsweep-a2c0-S2', 'a1c1-S1': '2026-11-16-e208-mmsweep-a1c1-S1',
        'a1c1-S2': '2026-11-16-e208-mmsweep-a1c1-S2', 'a1c1-S3': '2026-11-16-e208-mmsweep-a1c1-S3', 'a1c0-S1': '2026-11-16-e208-mmsweep-a1c0-S1',
        'a2c0-S1r': '2026-11-17-e208-mmsweep-a2c0-S1r'}
CARD = {'a2c0': 'aifoundry2 card 0', 'a1c1': 'aifoundry1 card 1', 'a1c0': 'aifoundry1 card 0', 'a3': 'aifoundry3 card 0'}
LOW_W = 3.0
QUANT = ('cyc_wall', 'cyc_mean', 't', 'jo_g', 'jo_f', 'jr_g', 'jr_f')
SETS = {
    'v0-E206A': ('MM1-v0', 'BLIND', 'E206 arm A'), 'v0-E206B': ('MM1-v0', 'BLIND', 'E206 arm B'), 'v1-E206B': ('MM1-v1', 'BLIND', 'E206 arm B'),
    'v1-E207': ('MM1-v1', 'BLIND', 'E207'), 'v1-E208': ('MM1-v1', 'UNREAD', 'E208'), 'v0-E208': ('MM1-v0', 'UNREAD', 'E208'),
    'v2-E207': ('MM1-v2', 'BLIND', 'E207'), 'v2-LOEO': ('MM1-v2', 'HELD OUT (LOEO)', 'v2 folds'), 'v2-LOCO': ('MM1-v2', 'HELD OUT (LOCO)', 'v2 folds')}


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as fh:
        for b in iter(lambda: fh.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    x = str(x).strip()
    if x in ('', 'None', 'nan', 'NaN', 'null'):
        return None
    try:
        return float(x)
    except ValueError:
        return None


def kind_norm(k):
    k = (k or '').strip()
    if k in ('random',):
        return 'random'
    if k == 'zeros':
        return 'zeros'
    if k in ('ones', 'constant / one number'):
        return 'ones'
    if k in ('sparse50', 'sparse (random with zeros)'):
        return 'sparse50'
    if k in ('real', 'real tensors') or k.startswith('real:'):
        return 'real'
    if k == 'e37' or k.startswith('designed'):
        return 'patterns'
    return 'other:' + k


def shape_attrs(arm, mask, fmt):
    """the grid point's blocks, footprint (MB, A + B + C, format-independent on rgm136's grid), place, KB class, mask class"""
    m = re.fullmatch(r'gemmL(\d+)x(\d+)x(\d+)', arm or '')
    a = {'arm': arm, 'fmt': fmt, 'mask': mask}
    try:
        nsh = bin(int(mask, 16)).count('1')
    except (TypeError, ValueError):
        nsh = None
    a['shires'] = nsh
    if m:
        MB, NB, KB = (int(m.group(i)) for i in (1, 2, 3))
        fp = 2.0 * MB * KB + NB * KB + 2.0 * MB * NB
        a.update({'MB': MB, 'NB': NB, 'KB': KB, 'footprint_MB': fp,
                  'place': 'inside the L3 (<= 32 MB)' if fp <= 32 else ('the knee (33-70 MB)' if fp <= 70 else 'past the L3 (> 70 MB)'),
                  'KB_class': 'KB 1' if KB == 1 else ('KB 2' if KB == 2 else ('KB 3-8' if KB <= 8 else ('KB 9-15' if KB <= 15 else 'KB >= 16'))),
                  'NB_pow2': (NB & (NB - 1)) == 0, 'law_arm': False})
    else:
        a.update({'MB': None, 'NB': None, 'KB': None, 'footprint_MB': None, 'place': 'law arm (run_gemm)', 'KB_class': 'law arm',
                  'NB_pow2': None, 'law_arm': True})
    if nsh is None:
        a['mask_class'] = 'unknown'
    elif nsh == 32:
        a['mask_class'] = 'full chip (32 shires)'
    elif nsh <= 2:
        a['mask_class'] = '1-2 shires'
    elif nsh <= 8:
        a['mask_class'] = '3-8 shires'
    else:
        a['mask_class'] = '9-31 shires'
    return a


def clock_class(f):
    if f is None:
        return 'unknown'
    if f < 605:
        return '600 MHz'
    if f < 790:
        return 'governed 605-789 MHz'
    return 'about 800 MHz'


def rel(f, m):
    if f is None or m is None or m == 0:
        return None
    return f / m - 1.0


def reduce_points(path, armkey, points):
    """E206 / E207: one record a point, the mean of its kept runs (the registered section-7 reduction)"""
    D = json.load(open(path))
    A = D['arms'][armkey]
    out = {}
    for pid, P in A['points'].items():
        pt = points[pid]
        want = {'arm': pt['arm'], 'type': pt['format'], 'minions': pt['minions'], 'shire_mask': pt['shire_mask']}
        kept = []
        for r in P['runs']:
            rec = r.get('record') or {}
            if any(str(rec.get(k)) != str(v) for k, v in want.items()):
                continue
            if r.get('t_gemm_s') and r.get('p_work_w') is not None and r.get('p_rest_w') is not None and r.get('cycles_gemm'):
                kept.append(r)
        if not kept:
            continue
        n = len(kept)
        ops = pt['ops_per_minion_per_gemm']
        mean = lambda k: sum(float(r[k]) for r in kept) / n  # noqa: E731
        out[pid] = {'n_runs': n, 'ops': ops, 'cyc_wall': mean('cycles_gemm') / ops, 'cyc_mean': mean('cycles_per_op'), 't': mean('t_gemm_s'),
                    'w': sum(r['p_work_w'] - r['p_rest_w'] for r in kept) / n, 'p_rest': mean('p_rest_w'),
                    'jo': sum((r['p_work_w'] - r['p_rest_w']) * r['t_gemm_s'] for r in kept) / n,
                    'jr': sum(r['p_work_w'] * r['t_gemm_s'] for r in kept) / n, 'f': mean('mhz'), 'die_start': mean('die_start_c'),
                    'mhz_min': min(r.get('mhz_min', 600) for r in kept), 'mhz_max': max(r.get('mhz_max', 600) for r in kept)}
    return out


def reduce_e208(lab):
    """E208: one record a run (primary view), null runs out"""
    out = {}
    for sess, d in E208.items():
        D = json.load(open(os.path.join(lab, 'docs/reports/data', d, f'data-e208-{sess}.json')))
        for r in D['runs']:
            if r.get('role') == 'null':
                continue
            m = re.fullmatch(r'(\d+)x(\d+)x(\d+)-(fp32|fp16|int8)-(rnd|zeros|ones)(?:-s(\d+))?', r['arm'])
            if not m:
                continue
            v = (r.get('views') or {}).get(r.get('primary_view')) or {}
            rec = {'session': sess, 'run': r['run'], 'arm_e208': r['arm'], 'arm': f'gemmL{m.group(1)}x{m.group(2)}x{m.group(3)}', 'fmt': m.group(4),
                   'kind': {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}[m.group(5)], 'mask': r['shires'], 'role': r['role'], 'form': r['form'],
                   'capped': bool(r.get('capped')), 'minions': int(r.get('minions') or 0), 'die_start': r.get('die_start_c'), 'view': r.get('primary_view')}
            if v.get('T_op_us') and v.get('cyc_op_max') and v.get('n_launch', 0) >= 1:
                rec.update({'f': float(v['kclock_mhz']), 'cyc_wall': float(v['cyc_op_max']), 'cyc_mean': float(v['cyc_op_mean']), 't': float(v['t_pass_s']),
                            'T_us': float(v['T_op_us'])})
            if v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time':
                rec.update({'w': float(v['dP_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']), 'jo': float(v['J_pass_over']), 'jr': float(v['J_pass_with'])})
            out[f'E208|{sess}|{r["run"]}'] = rec
    return out


def given(A, Wf, tf, tm):
    if None in (A, Wf, tf, tm) or tm == 0:
        return None
    return A + (Wf - A) * tf / tm


def errors(row):
    m, f = row['meas'], row['fc']
    e = {'cyc_wall': rel(f.get('cyc_wall'), m.get('cyc_wall')), 'cyc_mean': rel(f.get('cyc_mean'), m.get('cyc_mean')), 't': rel(f.get('t'), m.get('t')),
         'jo_g': rel(f.get('jo_g'), m.get('jo')), 'jo_f': rel(f.get('jo_f'), m.get('jo')), 'jr_g': rel(f.get('jr_g'), m.get('jr')),
         'jr_f': rel(f.get('jr_f'), m.get('jr'))}
    row['e'] = e
    row['low_w'] = (m.get('w') is not None and m['w'] < LOW_W)
    # watts residual (forecast W given t minus measured W) for the low-watt table
    row['dW_given_W'] = (f['w_g'] - m['w']) if (f.get('w_g') is not None and m.get('w') is not None) else None
    return row


def energy_fc(fc, A, Wf, tf, tm, p_rest, Wg=None):
    """J over idle and J at rest, given and forecast seconds (the run's measured rest for every model)"""
    if Wf is None:
        return
    if Wg is None:
        Wg = given(A, Wf, tf, tm)
    fc.update({'w_f': Wf, 'w_g': Wg, 'jo_f': Wf * tf if tf is not None else None, 'jo_g': Wg * tm if (Wg is not None and tm) else None})
    if p_rest is not None:
        fc['jr_g'] = (p_rest + Wg) * tm if (Wg is not None and tm) else None
        fc['jr_f'] = (p_rest + Wf) * tf if tf is not None else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lab', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    lab = os.path.abspath(a.lab)
    print(f'build_residuals: interpreter {sys.executable} {sys.version.split()[0]}; lab {os.path.basename(lab) or lab}')
    bad = 0
    pins = {}
    for p, h in PINS.items():
        g = sha(os.path.join(lab, p))
        pins[p] = {'pin': h, 'read': g, 'ok': g == h}
        print(f'pin {p}: {g[:16]}... {"OK" if g == h else "DIFFERS"}')
        bad += g != h
    # the data files: each data folder's own SHA256SUMS must list the data file with the sha256 read now
    data_files = [(E206A, 'data-e206.json'), (E206B, 'data-e206.json'), (E207, 'data-e207.json')] + \
                 [(os.path.join('docs/reports/data', d), f'data-e208-{s}.json') for s, d in E208.items()] + \
                 [(os.path.join('docs/reports/data', E208['a2c0-S1r']), 'repeat-e208-a2c0-S1r.json')]
    for d, f in data_files:
        sums = {}
        for ln in open(os.path.join(lab, d, 'SHA256SUMS')):
            parts = ln.split()
            if len(parts) >= 2:
                sums[parts[1].lstrip('*').lstrip('./')] = parts[0]
        g = sha(os.path.join(lab, d, f))
        ok = sums.get(f) == g
        pins[os.path.join(d, f)] = {'pin': sums.get(f), 'read': g, 'ok': ok}
        print(f'data {os.path.join(d, f)}: {g[:16]}... {"OK (its SHA256SUMS)" if ok else "NOT IN ITS SHA256SUMS"}')
        bad += not ok
    for p in ('tools/claims-v3/e206/points-e206.json', 'tools/claims-v3/e207/points-e207.json'):
        d, f = os.path.split(p)
        reg = 'SHA256SUMS-e206-registration' if 'e206' in f else 'SHA256SUMS-e207-registration'
        sums = {}
        for ln in open(os.path.join(lab, d, reg)):
            parts = ln.split()
            if len(parts) >= 2:
                sums[os.path.basename(parts[1].lstrip('*'))] = parts[0]
        g = sha(os.path.join(lab, p))
        ok = sums.get(f) == g
        pins[p] = {'pin': sums.get(f), 'read': g, 'ok': ok}
        print(f'points {p}: {g[:16]}... {"OK (" + reg + ")" if ok else "NOT IN " + reg}')
        bad += not ok
    if bad:
        print(f'REFUSED: {bad} file(s) differ from their pins (exit 4)')
        return 4

    rows = []
    P206 = {p['id']: p for p in json.load(open(os.path.join(lab, 'tools/claims-v3/e206/points-e206.json')))['points']}
    P207 = {p['id']: p for p in json.load(open(os.path.join(lab, 'tools/claims-v3/e207/points-e207.json')))['points']}
    MA = reduce_points(os.path.join(lab, E206A, 'data-e206.json'), 'A', P206)
    MB_ = reduce_points(os.path.join(lab, E206B, 'data-e206.json'), 'B', P206)
    M7 = reduce_points(os.path.join(lab, E207, 'data-e207.json'), 'A', P207)
    M8 = reduce_e208(lab)
    print(f'measured: E206 A {len(MA)} points, B {len(MB_)}, E207 {len(M7)}, E208 {len(M8)} runs (null runs out; S1r included)')
    v0par = json.load(open(os.path.join(lab, 'tools/matmul/mm1/v0/mm1_v0_params.json')))['energy']['theta']
    v0B = json.load(open(os.path.join(lab, 'tools/matmul/mm1/v0/forecasts-e206-armB.json')))['card']

    def base(set_id, pid, card, f, pt, meas):
        model, label, exp = SETS[set_id]
        kind_raw = pt.get('kind')
        a = shape_attrs(pt['arm'], pt.get('shire_mask') or pt.get('mask'), pt.get('format') or pt.get('fmt'))
        r = {'set': set_id, 'model': model, 'label': label, 'exp': exp, 'card': card, 'f_mhz': f, 'clock_class': clock_class(f), 'pid': pid,
             'kind': kind_norm(kind_raw), 'kind_raw': kind_raw, 'family': pt.get('family'), 'minions': pt.get('minions'), 'meas': meas, 'fc': {}}
        r.update(a)
        r['case'] = f"{r['arm']}|{r['fmt']}|{r['mask']}"
        r['cluster'] = f"{r['case']}|{card}"
        return r

    # E206 arm A, MM1-v0 BLIND
    for x in csv.DictReader(open(os.path.join(lab, 'tools/matmul/mm1/v0/mm1_v0_e206.csv'))):
        pid = x['id']
        if pid not in MA:
            continue
        m = MA[pid]
        r = base('v0-E206A', pid, CARD['a3'], m['f'], P206[pid], m)
        cw = num(x['cycles_per_op_wall'])
        tf = num(x['seconds_per_gemm']) or (m['ops'] * cw / 600e6)
        r['fc'] = {'cyc_wall': cw, 'cyc_mean': num(x['cycles_per_op_mean']), 't': tf}
        A = v0par['Paw|aifoundry3 card 0'] * int(x['minions']) / 1024.0
        energy_fc(r['fc'], A, num(x['W_over_idle']), tf, m['t'], m['p_rest'])
        r['fc']['A'] = A
        rows.append(errors(r))
    # E206 arm B, MM1-v0 and MM1-v1 BLIND
    for set_id, path in (('v0-E206B', 'tools/matmul/mm1/v0/forecasts-e206-armB.csv'), ('v1-E206B', 'tools/matmul/mm1/v1/forecasts-e206-armB.csv')):
        for x in csv.DictReader(open(os.path.join(lab, path))):
            pid = x['id']
            if pid not in MB_:
                continue
            m = MB_[pid]
            r = base(set_id, pid, CARD['a1c1'], m['f'], P206[pid], m)
            cw = num(x['cycles_per_op_wall'])
            tf = num(x.get('seconds_per_gemm')) or (m['ops'] * cw / 600e6)
            r['fc'] = {'cyc_wall': cw, 'cyc_mean': num(x['cycles_per_op_mean']), 't': tf}
            if set_id.startswith('v0'):
                A = v0B['P_aw_W_at_1024'] * int(x['minions']) / 1024.0
            else:
                A = num(x.get('W_affine_A_W'))
            energy_fc(r['fc'], A, num(x.get('W_over_idle')), tf, m['t'], m['p_rest'])
            r['fc']['A'] = A
            rows.append(errors(r))
    # E207, MM1-v1 and MM1-v2 BLIND
    for set_id, path in (('v1-E207', 'tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv'), ('v2-E207', 'tools/matmul/mm1/v2/forecasts-e207.csv')):
        for x in csv.DictReader(open(os.path.join(lab, path))):
            pid = x['id']
            if pid not in M7:
                continue
            m = M7[pid]
            r = base(set_id, pid, CARD['a3'], m['f'], P207[pid], m)
            cw = num(x['cycles_per_op_wall'])
            tf = num(x.get('seconds_per_gemm')) or (m['ops'] * cw / 600e6)
            r['fc'] = {'cyc_wall': cw, 'cyc_mean': num(x['cycles_per_op_mean']), 't': tf}
            A = num(x.get('W_affine_A_W'))
            energy_fc(r['fc'], A, num(x.get('W_over_idle')), tf, m['t'], m['p_rest'])
            r['fc']['A'] = A
            r['scored_in_watts_registered'] = str(P207[pid].get('scored_in_watts')) == 'True'
            rows.append(errors(r))
    # E208, MM1-v1 and MM1-v0 UNREAD (the forecasts file carries measured columns too: checked against the own reduction)
    xchk = {'n': 0, 'worst': 0.0, 'missing': []}
    U = list(csv.DictReader(open(os.path.join(lab, 'tools/matmul/mm1/v2/out/unread_e208.csv'))))
    for x in U:
        rid = x['id']
        m = M8.get(rid)
        if m is None or 'cyc_wall' not in m:
            xchk['missing'].append(rid)
            continue
        for k_m, k_x in (('cyc_wall', 'meas_cyc_wall'), ('cyc_mean', 'meas_cyc_mean'), ('t', 'meas_t_gemm'), ('w', 'meas_w_over'), ('p_rest', 'meas_p_rest')):
            if m.get(k_m) is not None and num(x[k_x]) is not None:
                xchk['n'] += 1
                xchk['worst'] = max(xchk['worst'], abs(m[k_m] / num(x[k_x]) - 1))
        pt = {'arm': m['arm'], 'shire_mask': m['mask'], 'format': m['fmt'], 'kind': m['kind'], 'family': m['role'] + '/' + m['form'], 'minions': m['minions']}
        ck = m['session'].split('-')[0]
        for set_id, pre in (('v1-E208', 'v1_'), ('v0-E208', 'v0_')):
            r = base(set_id, rid, CARD[ck], m['f'], pt, m)
            r['session'] = m['session']
            r['capped'] = m['capped']
            r['role'] = m['role']
            tf = num(x[pre + 't_gemm'])
            r['fc'] = {'cyc_wall': num(x[pre + 'cyc_wall']), 'cyc_mean': num(x[pre + 'cyc_mean']), 't': tf}
            Wf, Wg = num(x[pre + 'W']), num(x[pre + 'W_given_t'])
            if Wf is not None and m.get('w') is not None:
                energy_fc(r['fc'], None, Wf, tf, m['t'], m.get('p_rest'), Wg=Wg)
            rows.append(errors(r))
    print(f"E208 measured columns of unread_e208.csv against the own reduction: {xchk['n']} values, worst relative {xchk['worst']:.2e}; "
          f"rows without an own run: {len(xchk['missing'])}")
    # E208 S1r side check (matched to S1's UNREAD forecast for the same arm; never pooled)
    S1 = {x['arm_e208']: x for x in U if x['session'] == 'a2c0-S1'}
    side = []
    for rid, m in M8.items():
        if m['session'] != 'a2c0-S1r' or 'cyc_wall' not in m:
            continue
        x = S1.get(m['arm_e208'])
        if x is None or x['role'] != m['role']:
            continue
        rec = {'id': rid, 'arm_e208': m['arm_e208'], 'f_S1r': m['f'], 'f_S1': num(x['f_mhz']), 'meas': m, 'meas_S1': M8.get(x['id'])}
        for pre in ('v1_', 'v0_'):
            rec[pre + 'e_cyc_wall'] = rel(num(x[pre + 'cyc_wall']), m['cyc_wall'])
            rec[pre + 'e_cyc_wall_S1'] = rel(num(x[pre + 'cyc_wall']), num(x['meas_cyc_wall']))
            if m.get('w') is not None and num(x[pre + 'W_given_t']) is not None and num(x['meas_w_over']) is not None:
                rec[pre + 'e_w_given_S1r'] = rel(num(x[pre + 'W_given_t']), m['w'])
                rec[pre + 'e_w_given_S1'] = rel(num(x[pre + 'W_given_t']), num(x['meas_w_over']))
        side.append(rec)
    # MM1-v2 HELD OUT (LOEO, LOCO): measured as tabled by the fit
    T = {x['id']: x for x in csv.DictReader(open(os.path.join(lab, 'tools/matmul/mm1/v2/out/points_time_v2.csv')))}
    E = {x['id']: x for x in csv.DictReader(open(os.path.join(lab, 'tools/matmul/mm1/v2/out/points_energy_v2.csv')))}
    hchk = {'E206': [], 'E208': []}
    for set_id, col in (('v2-LOEO', 'loeo'), ('v2-LOCO', 'loco')):
        for pid, x in T.items():
            f = num(x['f_mhz'])
            pt = {'arm': x['arm'], 'shire_mask': x['mask'], 'format': x['fmt'], 'kind': x['kind'], 'family': x['exp'], 'minions': None}
            cw_m = num(x['meas_cyc_wall'])
            meas = {'cyc_wall': cw_m}
            y = E.get(pid)
            if y is not None:
                meas.update({'w': num(y['w_meas']), 'p_rest': num(y['idle_w'])})
            r = base(set_id, pid, x['card'], f, pt, meas)
            r['exp_point'] = x['exp']
            cwf = num(x['v2_' + col])
            r['fc'] = {'cyc_wall': cwf}
            if y is not None and meas.get('w') is not None:
                wg = num(y[f'v2_{col}_wg'])
                wf = num(y.get(f'v2_{col}_wf'))  # LOCO carries no seconds-forecast W
                w, rest = meas['w'], meas.get('p_rest')
                # J over idle and at rest in units of the measured seconds (t_meas = 1): J_g = W_g; J_f = W_f x cw_f / cw_m
                meas['jo'] = w
                meas['jr'] = (rest + w) if rest is not None else None
                r['fc']['w_g'] = wg
                r['fc']['jo_g'] = wg
                if rest is not None and wg is not None:
                    r['fc']['jr_g'] = rest + wg
                if wf is not None and cwf is not None and cw_m:
                    r['fc']['w_f'] = wf
                    r['fc']['jo_f'] = wf * cwf / cw_m
                    if rest is not None:
                        r['fc']['jr_f'] = (rest + wf) * cwf / cw_m
            rows.append(errors(r))
            if set_id == 'v2-LOEO' and x['exp'] in ('E206', 'E208'):
                hchk[x['exp']].append(pid)
    # cross-check of the held-out table's measured E206 arm A values against the own reduction
    hx = []
    for pid in hchk['E206']:
        p = pid.split('|')[-1]
        if p in MA:
            hx.append(abs(num(T[pid]['meas_cyc_wall']) / MA[p]['cyc_wall'] - 1))
    print(f"held-out table's E206 arm A wall cycles against the own reduction: {len(hx)} points, worst relative {max(hx) if hx else float('nan'):.2e}")
    print(f'rows: {len(rows)}; ' + ', '.join(f"{s} {sum(1 for r in rows if r['set'] == s)}" for s in SETS))
    # the floor: E208's committed session-repeat table (a2c0-S1r against a2c0-S1; single-run arms; post hoc)
    rp = json.load(open(os.path.join(lab, 'docs/reports/data', E208['a2c0-S1r'], 'repeat-e208-a2c0-S1r.json')))
    floor = {'source': os.path.join('docs/reports/data', E208['a2c0-S1r'], 'repeat-e208-a2c0-S1r.json'),
             'what': 'rms over the single-run arms of (repeat / first S1 - 1), the same 85-run schedule five hours apart on aifoundry2 card 0; '
                     'one measurement\'s own spread is about that / sqrt 2; anchor: sqrt 2 x the pooled within-session relative sd (9 runs each)'}
    for k in ('cyc_op_max', 'cyc_op_mean', 'T_op_us', 'dP_w', 'J_op', 'J_op_corr', 'dP_c50', 'J_op_c50'):
        d = ((rp.get('summary') or {}).get('d_rep_first') or {}).get(k, {}).get('single_run_arms')
        if d:
            floor[k] = {'n': d['n'], 'rms': d['rms'], 'median': d['median']}
            wv = (rp.get('within') or {}).get(k) or {}
            if 'sqrt2_pooled_rel_sd' in wv:
                floor[k]['anchor_sqrt2_pooled_rel_sd'] = wv['sqrt2_pooled_rel_sd']
    print('floor (repeat rms, %): ' + ', '.join(f"{k} {100 * v['rms']:.3f}" for k, v in floor.items() if isinstance(v, dict)))
    os.makedirs(a.out, exist_ok=True)
    out = {'what': 'MM1 residual rows (POST HOC desk arithmetic of committed forecasts and measured records)', 'sets': SETS, 'pins': pins,
           'low_w_threshold_W': LOW_W, 'quantities': QUANT, 'rows': rows, 's1r_side_check': side, 'floor': floor,
           'e208_measured_crosscheck': {'values': xchk['n'], 'worst_rel': xchk['worst'], 'rows_without_own_run': xchk['missing']},
           'heldout_e206_crosscheck': {'points': len(hx), 'worst_rel': max(hx) if hx else None},
           'python': sys.version.split()[0], 'interpreter': sys.executable}
    with open(os.path.join(a.out, 'residual-rows.json'), 'w') as fh:
        json.dump(out, fh, indent=0, sort_keys=False, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
