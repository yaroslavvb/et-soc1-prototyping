#!/usr/bin/env python3
"""MM1-v3.2's layout term (DECLARED-v32.md section 3): the candidates' features at every subset configuration of the data and of E218's Y
candidates, F1's feature check, the bundle layout_rule_v32.py reads, and the chosen term's factor. Desk; numpy; single-threaded.

FEATURES (section 3.1): every feature by verify-lay's committed tools/matmul/mm1/v3.2-terms/layout/controls-e215/v01_map.py functions
  (imported, unchanged: my_steps, lru_fresh, groups, mesh; a configuration's record assembled as v01_map.main assembles it, without its
  'loads' diagnostics, as Q229's controls_e216.py v01_record does), keyed 'rgm136.gemmL|<MB>x<NB>x<KB>|0x<mask>' with the shape's full-chip
  record beside: N3 = 32/n - 1; N1 = 1 - n/32; N2 = (1 - n/32)^2; G1 = (110 + 12 h_mean(mask)) / (110 + 12 h_mean(full)) - 1;
  fresh<C> = fresh lines a step at C MB / requested lines a step, minus the full chip's (v02_fits.py's feat_row, verbatim). A configuration
  already in the committed controls-e215/work/v01_map.json (made by those functions: MM1-v3.1's data and E215's registered rows) is read
  from it; any other is made here (E214's, E218's Y candidates) and cached in out/layout/features-v32.json.
F1's CHECK (section 3.1): at every subset configuration of the data, v01_map's fresh32 equals lay-contention's frozen Phi_fresh
  (features_layout.py's walk_feats records + eval_layout.phi_of; a configuration missing from its committed out/features_layout.json is
  made by features_layout.walk_feats and mesh_feats unchanged) within 1e-5; a configuration that fails takes features_layout's value for F1.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
V31 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.1')
LAYOUT = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2-terms', 'layout')
C215 = os.path.join(LAYOUT, 'controls-e215')
V01_JSON = os.path.join(C215, 'work', 'v01_map.json')
FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FEATURES = ('N3', 'N1', 'N2', 'G1', 'fresh24', 'fresh32', 'fresh48')
REPORTED_FEATURES = ('fresh16', 'fresh64')
CAPS_DATA = (16, 24, 32, 48, 64)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


os.environ.setdefault('ET_LAB', REPO)
V01 = load_module('v01_map_committed', os.path.join(C215, 'v01_map.py'))
WK = load_module('walk_v31_ro', os.path.join(V31, 'walk', 'walk', 'walk_v31.py'))


def key_of(arm, m):
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, m)


def mask_int(mask):
    return int(mask, 16) if isinstance(mask, str) else int(mask)


def v01_record(shp, m, caps=CAPS_DATA, check=True):
    """one configuration's record by v01_map.py's functions, as v01_map.main assembles it (no 'loads'); caps: the L3 capacities made"""
    MB, NB, KB = shp
    seq = list(V01.my_steps(MB, NB, KB, m))
    same = None
    if check:
        wseq = list(WK.chip_steps('rgm136.gemmL', MB, NB, KB, m))
        same = len(seq) == len(wseq)
        if same:
            for a, b in zip(seq, wseq):
                if a[0] != b[0]:
                    same = False
                    break
                if a[0] == 'op':
                    if ([(x >> 10, w) for x, w in a[1]] != [(t, w) for t, w in b[2]]
                            or [(x >> 10, w) for x, w in a[2]] != [(t, w) for t, w in b[3]]):
                        same = False
                        break
                elif [x >> 10 for x in a[1]] != list(b[2]):
                    same = False
                    break
        del wseq
    act, rows, cols = V01.groups(m)
    n, R, Cg = len(act), len(rows), len(cols)
    nsteps = MB * NB * 2 * KB * V01.KT
    rec = {'n': n, 'R': R, 'C': Cg, 'steps': nsteps, 'req_lines_step': 16 * 12 * n, 'distinct_lines_step': 16 * (4 * R + 8 * Cg),
           'generator_equals_walk': same}
    fr = {}
    for cap in caps:
        f = V01.lru_fresh(seq, cap * 1024, nsteps)
        fr[str(cap)] = 16.0 * sum(len(a) + len(b) for a, b in f) / nsteps
    rec['fresh_lines_step'] = fr
    hm, hx = V01.mesh(m)
    rec['hop_mean'], rec['hop_max'] = hm, hx
    return rec


class FeatureStore:
    """v01 records: the committed v01_map.json first, then this lane's cache (out/layout/features-v32.json), else made and cached"""

    def __init__(self, cache_path):
        self.committed = json.load(open(V01_JSON))['configs']
        self.cache_path = cache_path
        self.cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
        self.made = 0
        self.t_made = 0.0

    def get(self, shp, m, caps=CAPS_DATA, check=True):
        k = 'rgm136.gemmL|%dx%dx%d|0x%x' % (shp[0], shp[1], shp[2], m)
        if k in self.committed and all(str(c) in self.committed[k]['fresh_lines_step'] for c in caps):
            return self.committed[k], 'committed v01_map.json'
        c = self.cache.get(k)
        if c is not None and all(str(x) in c['fresh_lines_step'] for x in caps):
            return c, 'made here (cache)'
        t0 = time.time()
        rec = v01_record(shp, m, caps=caps, check=check)
        self.t_made += time.time() - t0
        self.made += 1
        self.cache[k] = rec
        if self.made % 20 == 0:
            self.save()
        return rec, 'made here'

    def save(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        json.dump(self.cache, open(self.cache_path + '.tmp', 'w'), indent=0, sort_keys=True)
        os.replace(self.cache_path + '.tmp', self.cache_path)


def feat_row(arm, m, store, caps=CAPS_DATA, check=True):
    """v02_fits.py's feat_row for the seven candidates' features (and fresh16, fresh64 REPORTED); zeros at the full mask"""
    if m == FULL:
        return {c: 0.0 for c in FEATURES + REPORTED_FEATURES}, None
    shp = tuple(int(x) for x in SHAPE.match(arm).groups())
    f, src = store.get(shp, m, caps=caps, check=check)
    g, _ = store.get(shp, FULL, caps=caps, check=check)
    n = f['n']
    out = {'N3': 32.0 / n - 1, 'N1': 1 - n / 32.0, 'N2': (1 - n / 32.0) ** 2,
           'G1': (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1}
    for cap in (16, 24, 32, 48, 64):
        if str(cap) in f['fresh_lines_step'] and str(cap) in g['fresh_lines_step']:
            out['fresh%d' % cap] = f['fresh_lines_step'][str(cap)] / f['req_lines_step'] - g['fresh_lines_step'][str(cap)] / g['req_lines_step']
        else:
            out['fresh%d' % cap] = None
    return out, src


def is_layout_point(p):
    """a subset point of rgm136's gemmL loop (the term's scope); any other subset point takes no term"""
    m = mask_int(p['mask'])
    return m != FULL and p.get('kernel', 'rgm136') == 'rgm136' and bool(SHAPE.match(p['arm']))


def data_features(P, store, log=print):
    """(feats {name: (N,) array}, sub (N,) bool, sources Counter) over the points P"""
    N = len(P)
    feats = {f: np.zeros(N) for f in FEATURES + REPORTED_FEATURES}
    sub = np.zeros(N, bool)
    src = collections.Counter()
    t0 = time.time()
    for j, p in enumerate(P):
        m = mask_int(p['mask'])
        if m == FULL:
            continue
        if not is_layout_point(p):
            src['subset point off rgm136 gemmL (no term)'] += 1
            continue
        sub[j] = True
        row, s = feat_row(p['arm'], m, store)
        src[s] += 1
        for f in FEATURES + REPORTED_FEATURES:
            feats[f][j] = row[f] if row[f] is not None else np.nan
    store.save()
    log(f'  layout features: {int(sub.sum())} subset points, sources {dict(src)}, {store.made} records made ({store.t_made:.0f} s; '
        f'{time.time() - t0:.0f} s in all)')
    return feats, sub, src


# ------------------------------------------------------------------------------------------------ F1's check against lay-contention's frozen Phi_fresh
def f1_check(P, sub, feats, cache_path, log=print):
    """v01_map's fresh32 against features_layout.walk_feats + eval_layout.phi_of's Phi_fresh at every subset configuration of the data"""
    FL = load_module('features_layout_frozen', os.path.join(LAYOUT, 'features_layout.py'))
    EL = load_module('eval_layout_frozen', os.path.join(LAYOUT, 'eval_layout.py'))
    made = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    for k, v in made.items():
        EL.FEATS.setdefault(k, v)
    out = {'configs': {}, 'made_here': [], 'fails': [], 'tolerance': 1e-5}
    seen = set()
    t0 = time.time()
    for j in np.where(sub)[0]:
        p = P[j]
        m = mask_int(p['mask'])
        k = key_of(p['arm'], m)
        if k in seen:
            continue
        seen.add(k)
        shp = tuple(int(x) for x in SHAPE.match(p['arm']).groups())
        for mm in (m, FULL):
            kk = 'rgm136.gemmL|%dx%dx%d|0x%x' % (shp[0], shp[1], shp[2], mm)
            if kk not in EL.FEATS:
                f = FL.walk_feats('rgm136.gemmL', shp, mm)
                f.update({'mesh_' + q: v for q, v in FL.mesh_feats(mm).items() if q != 'n'})
                EL.FEATS[kk] = f
                made[kk] = f
                out['made_here'].append(kk)
        ph, _ = EL.phi_of('rgm136 gemmL', p['arm'], m)
        d = float(abs(feats['fresh32'][j] - ph[0]))
        out['configs'][k] = {'v01_fresh32': float(feats['fresh32'][j]), 'lay_contention_Phi_fresh': float(ph[0]), 'abs_diff': d}
        if d > 1e-5:
            out['fails'].append(k)
    json.dump(made, open(cache_path + '.tmp', 'w'), indent=0, sort_keys=True)
    os.replace(cache_path + '.tmp', cache_path)
    out['n_configs'] = len(out['configs'])
    out['worst_abs_diff'] = max([v['abs_diff'] for v in out['configs'].values()] or [0.0])
    out['secs'] = round(time.time() - t0, 1)
    log(f"  F1 check: {out['n_configs']} configurations, worst |diff| {out['worst_abs_diff']:.3g}, fails {len(out['fails'])}, "
        f"{len(out['made_here'])} lay-contention records made ({out['secs']} s)")
    return out, EL


def apply_f1_fallback(P, sub, feats, chk):
    """a configuration that fails F1's check takes lay-contention's value for F1 (fresh32): named in the record"""
    fails = set(chk['fails'])
    for j in np.where(sub)[0]:
        k = key_of(P[j]['arm'], mask_int(P[j]['mask']))
        if k in fails:
            feats['fresh32'][j] = chk['configs'][k]['lay_contention_Phi_fresh']
    return feats


# ------------------------------------------------------------------------------------------------ the bundle and the factor
def matrix(feats, cols, idx=None):
    if not cols:
        n = len(next(iter(feats.values())))
        return np.zeros((n if idx is None else len(idx), 0))
    M = np.stack([feats[c] for c in cols], axis=1)
    return M if idx is None else M[idx]


def factor(M, a, sub):
    """clip(1 + M a, 0.3, 3.0) at the term's points; 1 elsewhere (every feature is 0 at the full mask)"""
    if M.shape[1] == 0:
        return np.ones(M.shape[0])
    g = np.clip(1.0 + M @ np.asarray(a, float), 0.3, 3.0)
    return np.where(sub, g, 1.0)


def solve(Xs, y):
    """layout_rule_v32.solve (the normal equations, least squares where singular), for folds the bundle does not hold"""
    A = Xs.T @ Xs
    if np.allclose(A, 0):
        return np.zeros(Xs.shape[1])
    try:
        return np.linalg.solve(A, Xs.T @ y)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(Xs, y, rcond=None)[0]


def fold_consts(base, Tm, M, tr_sub):
    """the two-stage constants of one fold: the normal-equation solution over its training subset points"""
    r = base[tr_sub] / Tm[tr_sub]
    return solve(r[:, None] * M[tr_sub], 1.0 - r)
