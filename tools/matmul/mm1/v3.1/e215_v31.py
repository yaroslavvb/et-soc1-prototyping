#!/usr/bin/env python3
"""MM1-v3.1's blind day E215: the candidates, the never-run scan in E213's form, DECLARED-v31.md item 10's point rule on both frozen models,
and the forecasts of the chosen points (MM1-v3.1 and MM1-v3, both frozen), arm A only: aifoundry3 card 0 at 600 MHz (the round's brief: the
lab's card; aifoundry1 is the model session's tonight; aifoundry2 is not an arm of the day). Desk; no card.

    /usr/bin/python3 -I -B e215_v31.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        E213's scan (tools/claims-v3/e213/desk/neverrun_e213.py, its token rule, roots and folder classes) re-run for E215: every file under
        the lab's committed data folders, E212's and E208's committed schedules, and the round's card and data lane folders, gzip read through;
        nothing subtracted (E213 has run: its folders count; no E215 folder exists); the measured points are MM1-v3.1's own (data_v31)
    /usr/bin/python3 -I -B e215_v31.py choose --scan <scan json> --params <mm1_v31_params.json> --out <dir>
        the grids of families L, P, C, R, S (item 10), the never-run candidates, the scores |ln(F_v3.1 / F_v3)|, the point rule, the forecasts

THE TOKEN (E213's): a point's arm as the host spells it, matched whole (gemmL<MB>x<NB>x<KB>, gemmLn.., gemmLnc..): SHAPE-LEVEL. Arm A keeps a
candidate only if its token has no hit on ANY card and MM1-v3.1's measured points do not hold it. Under that rule families L and S have no
candidate (every L shape ran full-chip on aifoundry3 by the grid's own condition; S's gemmL3x1x3 ran in E213): the literal selection is
reported, and beside it (labelled post hoc, a named departure for E215's registration to adopt or not by a dated amendment) L and S chosen
with a configuration-level never-run reading: L a (shape, mask) that no measured point and no scanned file holds; S a counted kind never
run in a GEMM on aifoundry3 card 0 (MM1-v3.1's data). Forecasts are frozen for every candidate of both readings that the rule chooses.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import csv
import datetime
import gzip
import hashlib
import itertools
import json
import math
import os
import random
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
A3 = 'aifoundry3 card 0'
RX = re.compile(r'(gemmL(?:n|nc)?\d+x\d+x\d+)(?![0-9x])')
SKIP_EXT = ('.bin', '.npz', '.npy', '.png', '.pdf', '.elf', '.o', '.a', '.so', '.zip', '.xz', '.zst', '.gguf', '.pkl')
MAX_BYTES = 400_000_000
QUOTA_A = {'L': 20, 'P': 12, 'C': 10, 'R': 10, 'S': 8}
FULL = '0xffffffff'


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def _e213_scan_module(lab):
    import importlib.util
    p = os.path.join(lab, 'tools', 'claims-v3', 'e213', 'desk', 'neverrun_e213.py')
    spec = importlib.util.spec_from_file_location('neverrun_e213', p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, sha(p)


def scan(lab, lanes, out):
    """E213's scan for E215 (its token rule, roots, folder classes and reader); nothing subtracted; masks beside each hit for item L"""
    N, nsha = _e213_scan_module(lab)
    t0 = now()
    expmap = N.exp_cards(lab)
    roots = [os.path.join(lab, 'docs', 'reports', 'data'), os.path.join(lab, 'tools', 'claims-v3', 'e212', 'proposal', 'src', 'sched'),
             os.path.join(lab, 'tools', 'claims-v3', 'e208', 'proposal', 'src')]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(('card-', 'data-', 'a1', 'a2', 'a3')))
    hits = {}
    masks_near = collections.defaultdict(set)
    nfiles, big, unreadable, git_dirs = 0, [], 0, 0
    MRX = re.compile(r'0x[0-9a-fA-F]{1,8}\b')
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if '.git' in dn or '.git' in fns:
                dn[:] = []
                git_dirs += 1
                continue
            dn.sort()
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > MAX_BYTES:
                        big.append(p)
                        continue
                    txt = N.read_text(p)
                except (OSError, EOFError):
                    unreadable += 1
                    continue
                nfiles += 1
                found = set(RX.findall(txt))
                if not found:
                    continue
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else 'W/out/' + os.path.relpath(p, lanes)
                c = N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE
                fmasks = {('0x%x' % int(m, 16)) for m in MRX.findall(txt)}
                for t in found:
                    hits.setdefault(t, {}).setdefault(c, []).append(rel)
                    masks_near[t] |= fmasks
    sys.path.insert(0, HERE)
    import data_v31 as DV
    measured = collections.defaultdict(set)
    measured_cfg = collections.defaultdict(set)
    for p in DV.time_points():
        measured[p['arm']].add((p['kernel'], p['card']))
        measured_cfg[p['arm']].add('0x%x' % int(p['mask'], 16))
    rec = {'what': "E215's never-run scan in E213's form (neverrun_e213.py's token rule, roots, folder classes and reader; nothing subtracted)",
           'neverrun_e213_sha256': nsha, 'started': t0, 'ended': now(), 'files_read': nfiles,
           'roots': [os.path.relpath(r, lab) for r in roots], 'lane_roots': ['W/out/' + os.path.basename(r) for r in lane_roots],
           'over_400MB_not_read': len(big), 'unreadable': unreadable, 'git_dirs_not_read': git_dirs,
           'tokens': {t: {c: {'n': len(v), 'files': sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           'masks_in_files_holding_token': {t: sorted(v) for t, v in sorted(masks_near.items())},
           'mm1_v31_measured_points': {t: sorted(f'{k} on {c}' for k, c in v) for t, v in sorted(measured.items())},
           'mm1_v31_measured_masks': {t: sorted(v) for t, v in sorted(measured_cfg.items())}}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, 'scan-e215.json')
    json.dump(rec, open(pth, 'w'), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(big)} over 400 MB, {unreadable} unreadable; {t0} - {rec['ended']}; {sha(pth)}")


# ------------------------------------------------------------------------------------------------ the grids (item 10)
def footprint(MB, NB, KB):
    import mm1_core_v3 as C
    return C.footprint(MB, NB, KB)


def mask_of(G, Cc):
    m = 0
    for g in G:
        for c in Cc:
            m |= 1 << (4 * g + c)
    return '0x%x' % m


def grid_L(full_runs):
    """rgm136 gemmL fp32 zeros and random at 40-160 MB (MB, NB, KB <= 16) whose full-chip configuration (shape, fp32, kind) ran on aifoundry3
    card 0; masks {4 g + c : g in G, c in C} for every row-group set G and column-group set C with n = |G| |C| from 2 to 28"""
    out = []
    shapes = sorted(full_runs)
    for (b, kind) in shapes:
        for a in range(1, 9):
            for bb in range(1, 5):
                if not (2 <= a * bb <= 28):
                    continue
                for G in itertools.combinations(range(8), a):
                    for Cc in itertools.combinations(range(4), bb):
                        out.append({'family': 'L', 'loop': 'rgm136 gemmL', 'kernel': 'rgm136', 'arm': 'gemmL%dx%dx%d' % b, 'fmt': 'fp32',
                                    'kind': kind, 'mask': mask_of(G, Cc), 'G': len(G), 'C': len(Cc)})
    return out


def one_stream_shapes(lo, hi):
    out = []
    for MB in range(1, 17):
        for NB in range(1, 17):
            if MB != 1 and NB != 1:
                continue
            for KB in range(1, 49):
                F = footprint(MB, NB, KB)
                if lo <= F <= hi:
                    out.append((MB, NB, KB))
    return out


def grid_P():
    """rgm211 gemmLn, rgm211 gemmL, gemmLnc and rgm136 gemmL, fp32 random (and int8 random at KB <= 2), one-stream shapes, 5-200 MB, KB 1-48"""
    out = []
    for b in one_stream_shapes(5.0, 200.0):
        for loop, kernel, pre in (('rgm211 gemmLn', 'rgm211', 'gemmLn'), ('rgm211 gemmL', 'rgm211', 'gemmL'), ('rgm136 gemmLnc', 'rgm136', 'gemmLnc'),
                                  ('rgm136 gemmL', 'rgm136', 'gemmL')):
            fmts = ['fp32'] + (['int8'] if b[2] <= 2 else [])
            for fmt in fmts:
                out.append({'family': 'P', 'loop': loop, 'kernel': kernel, 'arm': pre + '%dx%dx%d' % b, 'fmt': fmt, 'kind': 'random', 'mask': FULL})
    return out


def grid_C():
    out = []
    for MB in range(1, 17):
        for NB in range(1, 17):
            if MB * NB < 2:
                continue
            for KB in (1, 2):
                for fmt in ('int8', 'fp32'):
                    out.append({'family': 'C', 'loop': 'rgm136 gemmL', 'kernel': 'rgm136', 'arm': 'gemmL%dx%dx%d' % (MB, NB, KB), 'fmt': fmt,
                                'kind': 'random', 'mask': FULL})
    return out


def grid_R():
    out = []
    for MB in range(1, 5):
        for NB in range(1, 5):
            for KB in range(1, 200):
                F = footprint(MB, NB, KB)
                if 36.0 <= F <= 140.0:
                    for fmt in ('fp32', 'int8'):
                        out.append({'family': 'R', 'loop': 'rgm136 gemmL', 'kernel': 'rgm136', 'arm': 'gemmL%dx%dx%d' % (MB, NB, KB), 'fmt': fmt,
                                    'kind': 'random', 'mask': FULL})
    return out


def grid_S():
    """kinds v31-counts counted, at gemmL3x1x3 fp32 (and int8 where counted): every counted fp32 and int8 kind (the never-run test follows)"""
    import energy_v31 as EV
    out = []
    for k in sorted(EV.C32['S2']):
        out.append({'family': 'S', 'loop': 'rgm136 gemmL', 'kernel': 'rgm136', 'arm': 'gemmL3x1x3', 'fmt': 'fp32', 'kind': k, 'mask': FULL})
    for rk in sorted(EV.C16):
        fmt, k = rk.split('.', 1)
        if fmt == 'int8':
            out.append({'family': 'S', 'loop': 'rgm136 gemmL', 'kernel': 'rgm136', 'arm': 'gemmL3x1x3', 'fmt': 'int8', 'kind': k, 'mask': FULL})
    return out


def sort_key(c):
    return (c['arm'], c['loop'], c['fmt'], c['kind'], c['mask'])


def token_str(c):
    return f"{c['loop']}|{c['arm']}|{c['fmt']}|{c['kind']}|{c['mask']}"


def choose(scan_path, params_path, out, rehearsal=False):
    import data_v31 as DV
    import mm1_v31 as M31
    S = json.load(open(scan_path))
    T = S['tokens']
    meas = S['mm1_v31_measured_points']
    meas_masks = S['mm1_v31_measured_masks']
    near = S['masks_in_files_holding_token']
    P31 = json.load(open(params_path))
    v3p = json.load(open(os.path.join(HERE, '..', 'v3', 'out', 'mm1_v3_params.json')))
    # the full-chip fp32 zeros / random configurations that ran on aifoundry3 card 0 (MM1-v3.1's data: time and energy points)
    full_runs = set()
    for p in DV.time_points() + DV.energy_points():
        if p['card'] == A3 and p['kernel'] == 'rgm136' and p['arm'].startswith('gemmL') and not p['arm'].startswith('gemmLn') \
                and p['fmt'] == 'fp32' and p['mask'].lower() == FULL:
            b = DV.D.blocks(p['arm'])
            kinds = set(str(p.get('kind', '')).split('+'))
            for k in ('zeros', 'random'):
                if k in kinds and max(b) <= 16 and 40.0 <= footprint(*b) <= 160.0:
                    full_runs.add((b, k))
    grids = {'L': grid_L(full_runs), 'P': grid_P(), 'C': grid_C(), 'R': grid_R(), 'S': grid_S()}
    # the literal never-run rule (shape-level token, any card, MM1-v3.1's measured points)
    lit = {}
    for fam, cs in grids.items():
        keep = []
        for c in cs:
            tok = c['arm']
            if T.get(tok) or meas.get(tok):
                continue
            keep.append(c)
        lit[fam] = keep
    # the post hoc configuration-level reading for L and S (named departure)
    ran_kinds_a3 = {(e['fmt'], e['kind']) for e in DV.energy_points() if e['card'] == A3}
    ran_kinds_a3 |= {(p['fmt'], k) for p in DV.time_points() if p['card'] == A3 for k in str(p.get('kind', '')).split('+')}
    dep = {}
    dep['L'] = [c for c in grids['L'] if c['mask'] not in set(meas_masks.get(c['arm'], [])) and c['mask'] not in set(near.get(c['arm'], []))]
    dep['S'] = [c for c in grids['S'] if (c['fmt'], c['kind']) not in ran_kinds_a3]
    # the models
    M = M31.Model(P31, t7_cache_dir=os.path.join(out, 'cache'))
    sys.path.insert(0, os.path.join(HERE, '..', 'v3'))
    import mm1_v3 as MV3
    MV3m = MV3.Model(v3p)
    import engine_v3 as E3
    res = {'when': now(), 'scan_sha256': sha(scan_path), 'params_sha256': sha(params_path), 'quota_A': QUOTA_A, 'families': {}}

    def v3_wall(cs):
        pts = [{'arm': c['arm'], 'kernel': c['kernel'], 'fmt': c['fmt'], 'mask': c['mask'], 'f': 600.0} for c in cs]
        if not pts:
            return np.array([])
        eng = E3.TimeEngine(pts)
        return eng.predict(v3p['time']['theta'], v3p['time']['form']) * 600.0

    def v31_wall(cs):
        pts = [{'arm': c['arm'], 'kernel': c['kernel'], 'fmt': c['fmt'], 'mask': c['mask'], 'f': 600.0} for c in cs]
        if not pts:
            return np.array([])
        T_, _, _, _ = M.time_many(pts)
        return T_ * 600.0

    def score_time(cs, rep_masks=False):
        if not cs:
            return []
        if rep_masks:
            # family L: at a product mask both models' op times depend on (shape, |G|, |C|) only (time_v31's and engine_v3's inputs: the
            # masked walk's stream is the same up to an order-preserving relabeling of tiles, n/32, n_eff, the row imbalance); one
            # representative mask (the lowest groups) a (shape, |G|, |C|) is computed and the equality is checked at sampled masks
            reps = {}
            for c in cs:
                k = (c['arm'], c['G'], c['C'])
                if k not in reps:
                    reps[k] = dict(c, mask=mask_of(range(c['G']), range(c['C'])))
            keys = sorted(reps)
            rl = [reps[k] for k in keys]
            f31 = dict(zip(keys, v31_wall(rl)))
            f3 = dict(zip(keys, v3_wall(rl)))
            for c in cs:
                k = (c['arm'], c['G'], c['C'])
                c['F31_wall'], c['F3_wall'] = float(f31[k]), float(f3[k])
                c['score'] = abs(math.log(c['F31_wall'] / c['F3_wall']))
            return cs
        a, b = v31_wall(cs), v3_wall(cs)
        for c, x, y in zip(cs, a, b):
            c['F31_wall'], c['F3_wall'] = float(x), float(y)
            c['score'] = abs(math.log(x / y))
        return cs

    def score_S(cs):
        import energy_v31 as EV
        import energy_v3 as EN3
        out_ = []
        for c in cs:
            r31 = M.predict(A3, c['arm'], c['fmt'], c['kind'], c['mask'], 600.0, c['kernel'])
            # F_v3: MM1-v3's energy form at its landed constants with item 7's counts and phi (energy_v31's features, MM1-v3's W_v3)
            t3 = float(v3_wall([c])[0]) / 600.0
            pt = {'card': A3, 'fmt': c['fmt'], 'kind': c['kind'], 'arm': c['arm'], 'kernel': c['kernel'], 'minions': 1024, 'mask': FULL,
                  'f': 600.0, 'T': t3, 'w': 0.0, 'idle_w': None, 'G': 0.0, 'die_start': None, 's': (0.522 / 0.517) ** 2}
            X = EV.Features31([pt])
            if 'W_over_idle' not in r31 or not X.usable3[0]:
                continue
            q = MV3m.time(c['arm'], c['kernel'], c['fmt'], c['mask'], 600.0)
            n2, n3, nF = (float(v) for v in EV.C.lines(0.5 * (q[1] + q[2])))
            rC = EV.rC_of(X.Ffull, v3p['time']['theta'], v3p['time']['form'])
            W3 = float(EN3.W_v3(v3p['energy']['theta'], X, np.array([0]), np.array([n2]), np.array([n3]), np.array([nF]), np.array([t3]), rC, 'v3')[0])
            c['F31_W'], c['F3_W'] = float(r31['W_over_idle']), W3
            c['score'] = abs(math.log(c['F31_W'] / W3))
            out_.append(c)
        return out_

    def pick(fam, cs, q):
        cs = sorted(cs, key=sort_key)
        if len(cs) <= q:
            return [dict(c, how='all (fewer candidates than the quota)') for c in cs]
        h = math.ceil(q / 2)
        by = sorted(cs, key=lambda c: (-c['score'], sort_key(c)))
        top = [dict(c, how=f'by score ({i + 1} of {h})') for i, c in enumerate(by[:h])]
        topk = {token_str(c) for c in by[:h]}
        rest = [c for c in cs if token_str(c) not in topk]
        rnd = random.Random(f'v3.1-blind|A|{fam}').sample(rest, q - h)
        return top + [dict(c, how=f'random draw {i + 1} of {q - h}') for i, c in enumerate(rnd)]

    chosen = {}
    for fam in ('L', 'P', 'C', 'R', 'S'):
        q = QUOTA_A[fam]
        rec = {'grid_n': len(grids[fam]), 'literal_candidates_n': len(lit[fam])}
        if fam == 'S':
            cl = score_S([dict(c) for c in lit[fam]])
        else:
            cl = score_time([dict(c) for c in lit[fam]], rep_masks=(fam == 'L'))
        rec['literal_chosen'] = [dict(c, reading='literal') for c in pick(fam, cl, q)] if cl else []
        if fam in dep:
            rec['posthoc_candidates_n'] = len(dep[fam])
            cd = score_S([dict(c) for c in dep[fam]]) if fam == 'S' else score_time([dict(c) for c in dep[fam]], rep_masks=(fam == 'L'))
            rec['posthoc_chosen'] = [dict(c, reading='posthoc') for c in pick(fam, cd, q)] if cd else []
            rec['posthoc_reading'] = ('L: a (shape, mask) no MM1-v3.1 measured point holds and no scanned file holding the shape token names the mask; '
                                      'the shape ran full-chip on aifoundry3 by the grid\'s condition' if fam == 'L' else
                                      'S: a counted kind never run in a GEMM on aifoundry3 card 0 (no MM1-v3.1 time or energy point of that format and kind there)')
        res['families'][fam] = rec
        chosen[fam] = rec['literal_chosen'] + rec.get('posthoc_chosen', [])
    # the symmetry check for L's representative masks (at sampled masks of the chosen L points)
    chk = []
    for c in (res['families']['L'].get('posthoc_chosen') or [])[:6]:
        a = float(v31_wall([c])[0])
        chk.append({'token': token_str(c), 'representative': c['F31_wall'], 'at_its_mask': a, 'equal': abs(a / c['F31_wall'] - 1) < 1e-12})
    res['L_representative_mask_check'] = chk
    # the forecasts: every chosen point, both models, every field of MM1-v3.1's predictor
    pts = []
    for fam in ('L', 'P', 'C', 'R', 'S'):
        for c in chosen[fam]:
            pts.append(c)
    specs = [{'card': A3, 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'f': 600.0, 'kernel': c['kernel']} for c in pts]
    F31 = M.predict_many(specs)
    rows = []
    for c, r in zip(pts, F31):
        r3 = MV3m.predict(A3, c['arm'], c['fmt'], c['kind'], c['mask'], 600.0, kernel=c['kernel'])
        rows.append({'family': c['family'], 'reading': c['reading'], 'how': c['how'],
                     'token': token_str(c), 'loop': c['loop'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'],
                     'score': c.get('score'), 'v31': r, 'v3': r3})
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, 'e215_choice.json'), 'w'), indent=1, sort_keys=True, default=float)
    json.dump({'what': 'E215 (MM1-v3.1 blind day) forecasts, arm A aifoundry3 card 0 at 600 MHz: MM1-v3.1 and MM1-v3, both frozen',
               'params_v31_sha256': sha(params_path), 'params_v3_sha256': sha(os.path.join(HERE, '..', 'v3', 'out', 'mm1_v3_params.json')),
               'points': rows}, open(os.path.join(out, 'mm1_v31_e215.json'), 'w'), indent=1, sort_keys=True, default=float)
    with open(os.path.join(out, 'mm1_v31_e215.csv'), 'w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['family', 'reading', 'how', 'token', 'loop', 'arm', 'fmt', 'kind', 'mask', 'score_abs_ln_v31_over_v3',
                    'v31_cycles_wall', 'v31_cycles_mean', 'v31_seconds_per_gemm', 'v31_W_over_idle', 'v31_J_over_idle', 'v31_W_A', 'v31_W_B_us',
                    'v3_cycles_wall', 'v3_cycles_mean', 'v3_seconds_per_gemm', 'v3_W_over_idle', 'v3_J_over_idle'])
        for r in rows:
            a, b = r['v31'], r['v3']
            w.writerow([r['family'], r['reading'], r['how'], r['token'], r['loop'], r['arm'], r['fmt'], r['kind'], r['mask'],
                        ('%.6f' % r['score']) if r['score'] is not None else '',
                        '%.4f' % a['cycles_per_op_wall'], '%.4f' % a['cycles_per_op_mean'], '%.9e' % a.get('seconds_per_gemm', float('nan')),
                        ('%.5f' % a['W_over_idle']) if 'W_over_idle' in a else 'NOT FORECAST', ('%.9e' % a['J_over_idle_per_gemm']) if 'J_over_idle_per_gemm' in a else '',
                        ('%.6f' % a['W_affine']['A_W']) if 'W_affine' in a else '', ('%.6f' % a['W_affine']['B_W_us']) if 'W_affine' in a else '',
                        '%.4f' % b['cycles_per_op_wall'], '%.4f' % b['cycles_per_op_mean'], '%.9e' % b.get('seconds_per_gemm', float('nan')),
                        ('%.5f' % b['W_over_idle']) if 'W_over_idle' in b else 'NOT FORECAST', ('%.9e' % b['J_over_idle_per_gemm']) if 'J_over_idle_per_gemm' in b else ''])
    # the card time (desk estimate in E213's run form: E207's pace on aifoundry3, 47.16 card-minutes / 109 runs, plus the smoke)
    lit_runs = sum(len(res['families'][f]['literal_chosen']) * (4 if f == 'S' else 1) for f in res['families'])
    ph_runs = lit_runs + sum(len(res['families'][f].get('posthoc_chosen') or []) * (4 if f == 'S' else 1) for f in ('L', 'S'))
    pace = 47.16 * 60 / 109
    res['card_time_desk'] = {'pace_s_per_run': pace, 'smoke_min': 0.89, 'literal_runs': lit_runs, 'literal_minutes': round(lit_runs * pace / 60 + 0.89, 1),
                             'with_posthoc_L_S_runs': ph_runs, 'with_posthoc_L_S_minutes': round(ph_runs * pace / 60 + 0.89, 1), 'cap_A_min': 70,
                             'note': 'S as A B B A blocks (4 runs a kind); one run a point otherwise; the registration plans the runs'}
    json.dump(res, open(os.path.join(out, 'e215_choice.json'), 'w'), indent=1, sort_keys=True, default=float)
    for fam, r in res['families'].items():
        print(fam, 'grid', r['grid_n'], 'literal', r['literal_candidates_n'], 'chosen', len(r['literal_chosen']),
              'posthoc', r.get('posthoc_candidates_n'), len(r.get('posthoc_chosen') or []))
    print('card time', res['card_time_desk'])
    for f in ('e215_choice.json', 'mm1_v31_e215.json', 'mm1_v31_e215.csv'):
        print(sha(os.path.join(out, f)), f)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    a1 = sp.add_parser('scan')
    a1.add_argument('--lab', required=True)
    a1.add_argument('--lanes', required=True)
    a1.add_argument('--out', required=True)
    a2 = sp.add_parser('choose')
    a2.add_argument('--scan', required=True)
    a2.add_argument('--params', required=True)
    a2.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.cmd == 'scan':
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    else:
        choose(a.scan, a.params, a.out)


if __name__ == '__main__':
    main()
