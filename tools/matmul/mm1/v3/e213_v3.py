#!/usr/bin/env python3
"""MM1-v3's forecasts for E213, the blind day the spec plans for MM1-v3 (v3-spec section 12): the candidate points of its six families,
each checked never run on its card, MM1-v3's forecasts as frozen and MM1-v2's (frozen, unchanged) beside. Desk; numpy.

    /usr/bin/python3 -I -B e213_v3.py scan --lab <the lab's top> --lanes <W/out> --out <dir>      the never-run scan (neverrun_e213.json)
    /usr/bin/python3 -I -B e213_v3.py forecast --params <mm1_v3_params.json> --scan <neverrun_e213.json> --out <dir>
        writes e213_points.csv, mm1_v3_e213.csv, mm1_v3_e213.json, mm1_v2_e213.csv

THE POINTS (the spec's families; fp32 random unless named; rgm136's gemmL unless named; the full chip unless named):
  I int8 / fp32 pairs, inside the L3 2x1x2, 4x1x2, 3x1x3, 1x2x7 and at the knee 1x2x11, 2x2x7, 1x3x9, 2x3x6 (the int8 L3 factor d8);
  R 1x1x18, 1x1x22, 1x1x26, 1x1x30, 1x1x34, 1x2x13, 1x2x18, 1x2x22, 2x1x8, 2x1x10, 3x1x6, 3x1x7, 3x1x9, 4x1x6 (the two-edge retention);
  C KB = 1 at 3x2x1, 4x5x1, 7x3x1, 9x7x1, 10x10x1, 14x12x1, int8 and fp32 (the C store over C from 12 to 336 MiB);
  M fp32 zeros, 2x8x8 and 1x3x12 at 0x3, 0x11, 0x01010101, 0x000f0000, 0x0f0f, 0x22222222, 0x03030303, 0xfff, 0x07070707, 0x0f0f0f0f,
    0x55555555, with each shape's full chip as its reference (the subset layout; v3.0 has no layout model: these test the gap);
  P rgm136 gemmL, rgm211 gemmLn and rgm211's own gemmL at 3x1x3, 1x6x5, 4x1x6, 1x1x44 (one op stream: the census path term blind), gemmLnc
    at those four and at 1x1x1 int8 (the cooperation cost, pinned 0 in v3.0), rgm136's gemmL1x1x1 int8 beside as its twin;
  E deep K 1x3x40, 2x2x44, 1x4x36 in zeros and random; the anchor gemmL4x8x8 int8 random at two die gates (48 and 56 C); fp16 and int8
    ungated patterns never run: NOT FORECAST (no committed count).
  Arm A: aifoundry3 card 0 at its pinned 600 MHz. The optional arm B (aifoundry2 card 0 under its governor, at its top point 799 MHz given):
  families I, R and E's deep-K pairs.
NEVER RUN: a point is kept for its card when no committed data folder of the lab (docs/reports/data, every experiment, ours and the model
session's), no committed E212 schedule and no card lane's folder in W/out names its kernel's arm token (gemmL / gemmLn / gemmLnc + shape) in a
folder of that card or of no named card; MM1-v3's own measured points are checked too. A hit on another card is recorded, not disqualifying.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

A3 = 'aifoundry3 card 0'
A2 = 'aifoundry2 card 0'


def points():
    P = []

    def add(fam, arm, fmt, kind, mask='0xffffffff', kernel='rgm136', card=A3, f=600.0, t0=None, note=''):
        P.append({'family': fam, 'arm': arm, 'fmt': fmt, 'kind': kind, 'mask': mask, 'kernel': kernel, 'card': card, 'f': f, 't0_c': t0,
                  'note': note})
    I_in = ['2x1x2', '4x1x2', '3x1x3', '1x2x7']
    I_knee = ['1x2x11', '2x2x7', '1x3x9', '2x3x6']
    R = ['1x1x18', '1x1x22', '1x1x26', '1x1x30', '1x1x34', '1x2x13', '1x2x18', '1x2x22', '2x1x8', '2x1x10', '3x1x6', '3x1x7', '3x1x9', '4x1x6']
    Cs = ['3x2x1', '4x5x1', '7x3x1', '9x7x1', '10x10x1', '14x12x1']
    Ms = ['0x3', '0x11', '0x01010101', '0x000f0000', '0x0f0f', '0x22222222', '0x03030303', '0xfff', '0x07070707', '0x0f0f0f0f', '0x55555555']
    Ps = ['3x1x3', '1x6x5', '4x1x6', '1x1x44']
    Es = ['1x3x40', '2x2x44', '1x4x36']
    for card, f, arm_tag in ((A3, 600.0, 'A'), (A2, 799.0, 'B')):
        for s in I_in + I_knee:
            for fmt in ('int8', 'fp32'):
                add(arm_tag + ':I', 'gemmL' + s, fmt, 'random', card=card, f=f, note='inside the L3' if s in I_in else 'the knee')
        for s in R:
            add(arm_tag + ':R', 'gemmL' + s, 'fp32', 'random', card=card, f=f)
        for s in Es:
            for kind in ('zeros', 'random'):
                add(arm_tag + ':E', 'gemmL' + s, 'fp32', kind, card=card, f=f, note='deep K')
        if arm_tag == 'B':
            break
        for s in Cs:
            for fmt in ('int8', 'fp32'):
                add('A:C', 'gemmL' + s, fmt, 'random')
        for s in ('2x8x8', '1x3x12'):
            add('A:M', 'gemmL' + s, 'fp32', 'zeros', note='reference: the full chip')
            for m in Ms:
                add('A:M', 'gemmL' + s, 'fp32', 'zeros', mask=m)
        for s in Ps:
            add('A:P', 'gemmL' + s, 'fp32', 'random', kernel='rgm136', note='rgm136 gemmL')
            add('A:P', 'gemmLn' + s, 'fp32', 'random', kernel='rgm211', note='rgm211 gemmLn (one op stream at MB = 1 or NB = 1)')
            add('A:P', 'gemmL' + s, 'fp32', 'random', kernel='rgm211', note="rgm211's own gemmL (simulator only so far)")
            add('A:P', 'gemmLnc' + s, 'fp32', 'random', kernel='rgm136', note='rgm136 gemmLnc (no cooperation)')
        add('A:P', 'gemmLnc1x1x1', 'int8', 'random', kernel='rgm136', note='rgm136 gemmLnc at the L2')
        add('A:P', 'gemmL1x1x1', 'int8', 'random', kernel='rgm136', note="gemmLnc1x1x1's twin (ran before: a reference)")
        for t0 in (48.0, 56.0):
            add('A:E', 'gemmL4x8x8', 'int8', 'random', t0=t0, note=f'the anchor at a {t0:.0f} C die gate (ran before: a reference)')
    # merge duplicates (the same kernel, arm, format, kind, mask, card, clock, die), keeping every family label
    out = {}
    for p in P:
        k = (p['kernel'], p['arm'], p['fmt'], p['kind'], p['mask'], p['card'], p['f'], p['t0_c'])
        if k in out:
            out[k]['family'] += '+' + p['family'].split(':')[1]
            continue
        out[k] = p
    L = list(out.values())
    for j, p in enumerate(L):
        p['id'] = ('a' if p['card'] == A3 else 'b') + '%03d' % (j + 1)
    return L


def token(p):
    return p['arm']


def exp_cards(lab):
    """experiment number -> card, from the committed data folders whose names carry the card (e.g. ...-e207-blind-matmul-aifoundry3)"""
    m = {}
    for d in os.listdir(os.path.join(lab, 'docs', 'reports', 'data')):
        e = re.search(r'-e(\d{2,3})-', d)
        c = folder_card(d, {})
        if e and c:
            m.setdefault(e.group(1), c)
    return m


def folder_card(path, expmap):
    """the card a data or lane folder's path names, or None (no card named)"""
    q = '/' + path
    for keys, c in ((('aifoundry3', '/a3-', 'card-a3-', '-a3-'), A3), (('aifoundry1-c1', '/a1c1-', 'card-a1c1-', 'a1c1'), 'aifoundry1 card 1'),
                    (('aifoundry1-card0', '/a1c0-', 'card-a1c0-', 'a1c0'), 'aifoundry1 card 0'),
                    (('aifoundry2', '/a2-', 'card-a2-', 'a2c0'), A2), (('aifoundry1', '/a1-', 'card-a1-'), 'aifoundry1 (card not named)')):
        if any(k in q for k in keys):
            return c
    e = re.search(r'card-e(\d{2,3})', q)
    if e:
        return expmap.get(e.group(1))
    return None


SKIP_EXT = ('.gz', '.bin', '.npz', '.npy', '.png', '.pdf', '.elf', '.o', '.a', '.so', '.zip', '.xz', '.zst')


def scan(lab, lanes, out):
    sys.path.insert(0, HERE)
    import data_v3 as D  # noqa: E402
    P = points()
    toks = sorted({token(p) for p in P})
    expmap = exp_cards(lab)
    hits = {t: [] for t in toks}
    rx = re.compile(r'(gemmL(?:n|nc)?\d+x\d+x\d+)(?![0-9x])')
    roots = [os.path.join(lab, 'docs', 'reports', 'data'), os.path.join(lab, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'sched')]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith('card-') or d.startswith('a1') or d.startswith('a2')
                        or d.startswith('a3'))
    nfiles = 0
    for root in roots + lane_roots:
        for dp, dn, fns in os.walk(root):
            for fn in fns:
                pth = os.path.join(dp, fn)
                if fn.endswith(SKIP_EXT) or os.path.islink(pth) or os.path.getsize(pth) > 60_000_000:
                    continue
                try:
                    txt = open(pth, 'rb').read().decode('utf-8', 'ignore')
                except OSError:
                    continue
                nfiles += 1
                found = set(rx.findall(txt))
                for t in found & set(toks):
                    rel = os.path.relpath(pth, lab) if pth.startswith(lab) else 'W/out/' + os.path.relpath(pth, lanes)
                    hits[t].append({'file': rel, 'card': folder_card(rel, expmap)})
    measured = {}
    for p in D.time_points():
        measured.setdefault(p['arm'], set()).add((p['kernel'], p['card']))
    rec = {'what': 'MM1-v3 E213 never-run scan', 'files_read': nfiles, 'roots': [os.path.relpath(r, lab) for r in roots],
           'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots], 'points': []}
    for p in P:
        t = token(p)
        h = hits[t]
        cards = sorted({x['card'] or 'no card named' for x in h})
        ms = sorted(measured.get(t, set()))
        kernel_ran_here = any(k == p['kernel'] and c == p['card'] for k, c in ms)
        named_here = any((x['card'] in (p['card'], None)) for x in h)
        # rgm211's own gemmL: the token gemmL<shape> names rgm136's runs; it ran on no card (its kit's runs are rgm136's or gemmLn)
        if p['kernel'] == 'rgm211' and p['arm'].startswith('gemmL') and not p['arm'].startswith('gemmLn'):
            named_here = False
            kernel_ran_here = False
        never = not (kernel_ran_here or named_here)
        rec['points'].append({'id': p['id'], 'token': t, 'kernel': p['kernel'], 'card': p['card'], 'never_run_on_card': never,
                              'hit_cards': cards, 'n_hits': len(h), 'hit_files': sorted({x['file'] for x in h})[:12],
                              'measured_in_v3_points': [f'{k} on {c}' for k, c in ms]})
    json.dump(rec, open(os.path.join(out, 'neverrun_e213.json'), 'w'), indent=1, sort_keys=True)
    n = sum(1 for x in rec['points'] if x['never_run_on_card'])
    print(f'scan: {nfiles} files; {n} of {len(P)} points never run on their card')


def v2_model():
    V2 = os.path.normpath(os.path.join(HERE, '..', 'v2'))
    sys.path.insert(0, HERE)
    import unread_v2_e212 as U  # noqa: E402
    M, n = U.v2_model()
    return M


def forecast(params_path, scan_path, out):
    import mm1_v3  # noqa: E402
    params = json.load(open(params_path))
    M3 = mm1_v3.Model(params)
    M2 = v2_model()
    S = {x['id']: x for x in json.load(open(scan_path))['points']}
    P = points()
    rows3, rows2, js = [], [], {}
    for p in P:
        s = S[p['id']]
        V = None
        r3 = M3.predict(p['card'], p['arm'], p['fmt'], p['kind'], p['mask'], p['f'], kernel=p['kernel'], t0_c=p['t0_c'])
        row = {'id': p['id'], 'family': p['family'], 'card': p['card'], 'f_mhz': p['f'], 'kernel': p['kernel'], 'arm': p['arm'], 'fmt': p['fmt'],
               'kind': p['kind'], 'mask': p['mask'], 't0_c': p['t0_c'] if p['t0_c'] is not None else '', 'never_run_on_card': s['never_run_on_card'],
               'note': p['note'], 'footprint_MB': r3['footprint_MB'], 'cycles_per_op_wall': round(r3['cycles_per_op_wall'], 3),
               'cycles_per_op_mean': round(r3['cycles_per_op_mean'], 3), 'seconds_per_gemm': r3.get('seconds_per_gemm'),
               'T_op_us': round(r3['T_op_us'], 6), 'census_D_B_cycles': r3['census_path_D_cycles']['D_B']}
        if 'W_over_idle' in r3:
            row.update({'W_over_idle': round(r3['W_over_idle'], 4), 'A_W': round(r3['W_affine']['A_W'], 5), 'B_W_us': round(r3['W_affine']['B_W_us'], 5),
                        'J_over_idle_per_gemm': r3.get('J_over_idle_per_gemm'),
                        'J_at_rest_per_gemm_REPORTED': (r3.get('rest_law') or {}).get('J_at_rest_per_gemm_REPORTED'),
                        'P_rest_W_REPORTED': (r3.get('rest_law') or {}).get('P_rest_W')})
            sw = r3.get('switches') or {}
            row['switches_counted_signal_lo'] = (sw.get('counted_signal_fin_edges') or {}).get('lo_zero_delay')
            row['switches_data_term_equivalent'] = (sw.get('data_term_energy_equivalent') or {}).get('value')
        else:
            row['energy'] = r3.get('energy')
        rows3.append(row)
        js[p['id']] = r3
        # MM1-v2 beside: its predictor unchanged; a kernel it has no term for is priced as its rgm136 twin (v2 literally)
        arm2 = p['arm'].replace('gemmLnc', 'gemmL').replace('gemmLn', 'gemmL')
        kind2 = p['kind'] if p['kind'] in ('zeros', 'random', 'ones') else 'random'
        r2 = M2.predict(p['card'], arm2, p['fmt'], kind2, p['mask'], p['f'], V=V, t0_c=p['t0_c'])
        row2 = {'id': p['id'], 'v2_arm_called': arm2, 'cycles_per_op_wall': round(r2['cycles_per_op_wall'], 3),
                'cycles_per_op_mean': round(r2['cycles_per_op_mean'], 3), 'seconds_per_gemm': r2.get('seconds_per_gemm'),
                'note': ('MM1-v2 has no term for this kernel: its rgm136 twin, literally' if arm2 != p['arm'] or p['kernel'] == 'rgm211' else '')}
        if 'W_over_idle' in r2:
            row2.update({'W_over_idle': round(r2['W_over_idle'], 4), 'A_W': round(r2['W_affine']['A_W'], 5), 'B_W_us': round(r2['W_affine']['B_W_us'], 5),
                         'J_over_idle_per_gemm': r2.get('J_over_idle_per_gemm'),
                         'J_at_rest_per_gemm_REPORTED': (r2.get('rest_law') or {}).get('J_at_rest_per_gemm_REPORTED')})
        else:
            row2['energy'] = r2.get('energy')
        rows2.append(row2)
    os.makedirs(out, exist_ok=True)
    pcols = ['id', 'family', 'card', 'f_mhz', 'kernel', 'arm', 'fmt', 'kind', 'mask', 't0_c', 'never_run_on_card', 'note']
    with open(os.path.join(out, 'e213_points.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=pcols, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows3:
            w.writerow(r)
    c3 = pcols + ['footprint_MB', 'cycles_per_op_wall', 'cycles_per_op_mean', 'T_op_us', 'seconds_per_gemm', 'census_D_B_cycles', 'W_over_idle', 'A_W',
                  'B_W_us', 'J_over_idle_per_gemm', 'P_rest_W_REPORTED', 'J_at_rest_per_gemm_REPORTED', 'switches_counted_signal_lo',
                  'switches_data_term_equivalent', 'energy']
    with open(os.path.join(out, 'mm1_v3_e213.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=c3, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows3:
            w.writerow(r)
    c2 = ['id', 'v2_arm_called', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
          'J_at_rest_per_gemm_REPORTED', 'energy', 'note']
    with open(os.path.join(out, 'mm1_v2_e213.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=c2, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows2:
            w.writerow(r)
    meta = {'what': "MM1-v3's E213 forecasts (every field of its predictor), MM1-v2 beside in mm1_v2_e213.csv",
            'params_sha256': hashlib.sha256(open(params_path, 'rb').read()).hexdigest(),
            'scan_sha256': hashlib.sha256(open(scan_path, 'rb').read()).hexdigest(), 'points': js}
    json.dump(meta, open(os.path.join(out, 'mm1_v3_e213.json'), 'w'), indent=1, sort_keys=True, default=float)
    for fn in ('e213_points.csv', 'mm1_v3_e213.csv', 'mm1_v2_e213.csv', 'mm1_v3_e213.json'):
        print(hashlib.sha256(open(os.path.join(out, fn), 'rb').read()).hexdigest(), fn)


def e212_s3s4(params_path, out):
    """MM1-v3's (and MM1-v2's) forecasts of E212 a2c0-S3 and a2c0-S4's scheduled arms (their committed schedules, vendored), aifoundry2 card 0
    at its top point 799 MHz given (the win view); time for every kind, energy for random, zeros and ones. Label: made after S4's first card
    command (15:03 PST Tue 17 Nov 2026), so never blind for S4; for S3 blind only if pushed before S3's first card command (the spec's 9.7)."""
    import mm1_v3  # noqa: E402
    M3 = mm1_v3.Model(json.load(open(params_path)))
    M2 = v2_model()
    rows = []
    kmap = {'rnd': 'random', 'zeros': 'zeros', 'ones': 'ones'}
    for sess in ('a2c0-S3', 'a2c0-S4'):
        S = json.load(open(os.path.join(HERE, 'inputs', 'e212', f'sched__{sess}.json')))
        seen = set()
        for r in S['runs']:
            if r.get('role') not in ('arm', 'anchor'):
                continue
            m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', r.get('values') or '')
            mk = re.fullmatch(r'\d+x\d+x\d+-(?:fp32|fp16|int8)-([A-Za-z0-9_]+?)(?:-(?:s\d+|m[0-9a-f]+))?', r['arm'])
            if not m or not mk:
                continue
            key = (sess, r['arm'], r['shires'])
            if key in seen:
                continue
            seen.add(key)
            arm = 'gemmL%sx%sx%s' % m.groups()
            kind = kmap.get(mk.group(1), 'pattern:' + mk.group(1))
            r3 = M3.predict(A2, arm, r['type'], kind if not kind.startswith('pattern') else 'random', r['shires'], 799.0)
            k2 = kind if kind in ('random', 'zeros', 'ones') else 'random'
            r2 = M2.predict(A2, arm, r['type'], k2, r['shires'], 799.0)
            row = {'session': sess, 'arm_label': r['arm'], 'arm': arm, 'fmt': r['type'], 'kind': kind, 'mask': r['shires'], 'f_mhz': 799.0,
                   'v3_cycles_per_op_wall': round(r3['cycles_per_op_wall'], 3), 'v3_cycles_per_op_mean': round(r3['cycles_per_op_mean'], 3),
                   'v2_cycles_per_op_wall': round(r2['cycles_per_op_wall'], 3), 'v2_cycles_per_op_mean': round(r2['cycles_per_op_mean'], 3)}
            if not kind.startswith('pattern') and 'W_affine' in r3:
                row.update({'v3_A_W': round(r3['W_affine']['A_W'], 5), 'v3_B_W_us': round(r3['W_affine']['B_W_us'], 5),
                            'v3_W_over_idle': round(r3['W_over_idle'], 4)})
            if 'W_affine' in r2 and not kind.startswith('pattern'):
                row.update({'v2_A_W': round(r2['W_affine']['A_W'], 5), 'v2_B_W_us': round(r2['W_affine']['B_W_us'], 5),
                            'v2_W_over_idle': round(r2['W_over_idle'], 4)})
            rows.append(row)
    cols = ['session', 'arm_label', 'arm', 'fmt', 'kind', 'mask', 'f_mhz', 'v3_cycles_per_op_wall', 'v3_cycles_per_op_mean', 'v3_A_W', 'v3_B_W_us',
            'v3_W_over_idle', 'v2_cycles_per_op_wall', 'v2_cycles_per_op_mean', 'v2_A_W', 'v2_B_W_us', 'v2_W_over_idle']
    fn = os.path.join(out, 'mm1_v3_e212_s3s4.csv')
    with open(fn, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore', lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(hashlib.sha256(open(fn, 'rb').read()).hexdigest(), 'mm1_v3_e212_s3s4.csv', len(rows), 'arms')


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--lanes', required=True)
    a1.add_argument('--out', required=True)
    a2 = sp.add_parser('forecast')
    a2.add_argument('--params', required=True)
    a2.add_argument('--scan', required=True)
    a2.add_argument('--out', required=True)
    a3 = sp.add_parser('e212')
    a3.add_argument('--params', required=True)
    a3.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        os.makedirs(a.out, exist_ok=True)
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    elif a.cmd == 'e212':
        e212_s3s4(a.params, a.out)
    else:
        forecast(a.params, a.scan, a.out)


if __name__ == '__main__':
    main()
