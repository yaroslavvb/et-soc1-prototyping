#!/usr/bin/env python3
"""mask-ceiling (Q238 track C): the definitions every step shares (declared in DECLARED-mask-ceiling.md before any fit).

SCOPE (the points the reference may move): rgm136's cooperative gemmL loop (kernel rgm136, arm gemmL<MB>x<NB>x<KB>) at a shire SUBSET
  (mask not 0xffffffff) with MB x NB >= 2 (a multi-tile shape). Every other point keeps MM1-v3.2's op time to the last bit.
THE MASK CLASS (blind-e221's class definition, applied by this code to every point): the scope's points (the core-group placements of a
  multi-tile shape on shire groups) plus their whole-chip twins: a full-chip rgm136 gemmL point of the same experiment, card, arm, format and
  kind as a MASK subset point. On E221 this reproduces blind-e221's labels exactly (392 MASK cases, 341 others: checked in r01).
  Other classes (REPORTED, deciding nothing): CELL1 (rgm136 gemmL 1x1x1 at a subset), SUB1 (rgm136 gemmL MB x NB = 1, KB > 1, at a subset:
  E221's L2I8 among them), FULL (every other full-chip point), and every other kernel's subset points (none here: checked).
THE FOLD FAMILIES (COMMON): LOSO (one fold per E221 session; a case's session = its first run's), LOEO (one fold per experiment, every
  experiment; E215-E224's named), LOCO (one fold per card), LOMO (one fold per subset mask that E221, E217 or E224 ran; its test = every point
  at that mask, from any experiment). THE BASE of a fold: MM1-v3.2's stored fold constants where its fit record has that fold ('LOEO <exp>'
  for E105-E215, 'LOCO <card>'), else its all-data constants (E216-E224 were never in its fit; LOSO and LOMO folds). The reference's
  training points = the fold's non-test points in scope, their targets ln(T_meas / T_base) at that fold's base.
TWINS (per fold): a test point is a twin when a training point of the fold (any point outside the fold's test set) has the same card,
  kernel, arm, format and mask (layout2's twin key). LOCO and LOMO folds have no twins by construction. Headlines are without twins.
ERROR (blind-e221's): forecast / measured - 1 of the wall cycles an op (= of the op time at the point's clock); rms in %.
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4.
SPDX-License-Identifier: Apache-2.0
"""
import collections
import math
import re

import numpy as np

FULL = '0xffffffff'
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
FMT = {'fp32': 0, 'fp16': 1, 'int8': 2}
FEATS_M = ('n', 'R', 'C', 'rmax', 'cmax', 'rimb', 'cimb', 'G1', 'hlag', 'spread', 'bbox', 'memd', 'link', 'dist_rel', 'Fp', 'Fs', 'LAG')
FEATS_X = ('MB', 'NB', 'lnKB', 'fmt', 'f')
FEATS = FEATS_M + FEATS_X
GROUPS = {'count': ('n',), 'groups': ('R', 'C', 'rmax', 'cmax', 'rimb', 'cimb', 'dist_rel'), 'position': ('G1', 'hlag', 'spread', 'bbox'),
          'memory distance': ('memd',), 'link': ('link',), 'DRAM private/shared': ('Fp', 'Fs', 'LAG'), 'context (shape)': FEATS_X}
CARDS = ('aifoundry1 card 0', 'aifoundry1 card 1', 'aifoundry2 card 0', 'aifoundry3 card 0')
LOMO_EXPS = ('E217', 'E221', 'E224')


def shape(arm):
    m = SHAPE.match(arm)
    return tuple(int(x) for x in m.groups()) if m else None


def in_scope(p):
    s = shape(p['arm'])
    return p['kernel'] == 'rgm136' and s is not None and s[0] * s[1] >= 2 and p['mask'] != FULL


def classes(P):
    sub = {(p['exp'], p['card'], p['arm'], p['fmt'], p.get('kind')) for p in P if in_scope(p)}
    out = []
    for p in P:
        s = shape(p['arm'])
        if in_scope(p):
            out.append('MASK')
        elif p['mask'] == FULL and p['kernel'] == 'rgm136' and s is not None and (p['exp'], p['card'], p['arm'], p['fmt'], p.get('kind')) in sub:
            out.append('MASK')
        elif p['mask'] != FULL and p['kernel'] == 'rgm136' and s is not None and s == (1, 1, 1):
            out.append('CELL1')
        elif p['mask'] != FULL and p['kernel'] == 'rgm136' and s is not None:
            out.append('SUB1')
        elif p['mask'] != FULL:
            out.append('SUBother')
        else:
            out.append('FULL')
    return out


def key(p):
    return (p['card'], p['kernel'], p['arm'], p['fmt'], p['mask'])


def folds(P, base_names):
    """{family: [(fold name, test index array, base name)]}; base_names: the fold bases e01 stored"""
    idx = np.arange(len(P))
    F = collections.OrderedDict()
    ss = sorted({p['session'] for p in P if p['exp'] == 'E221'})
    F['LOSO'] = [('LOSO E221 ' + s, idx[[p['exp'] == 'E221' and p['session'] == s for p in P]], 'all') for s in ss]
    exps = sorted({p['exp'] for p in P}, key=lambda e: int(e[1:]))
    F['LOEO'] = [('LOEO ' + e, idx[[p['exp'] == e for p in P]], ('LOEO ' + e) if ('LOEO ' + e) in base_names else 'all') for e in exps]
    F['LOCO'] = [('LOCO ' + c, idx[[p['card'] == c for p in P]], 'LOCO ' + c) for c in CARDS]
    masks = sorted({p['mask'] for p in P if p['exp'] in LOMO_EXPS and p['mask'] != FULL}, key=lambda m: int(m, 16))
    F['LOMO'] = [('LOMO ' + m, idx[[p['mask'] == m for p in P]], 'all') for m in masks]
    return F


def twins(P, test):
    tset = set(int(i) for i in test)
    train_keys = {key(p) for i, p in enumerate(P) if i not in tset}
    return np.array([key(P[i]) in train_keys for i in test], bool)


def rms(v):
    v = np.asarray(v, float)
    return float(math.sqrt(np.mean(v * v)) * 100) if len(v) else None


def bias(v):
    v = np.asarray(v, float)
    return float(np.mean(v) * 100) if len(v) else None


def feature_rows(P, sc, feats_json):
    """the reference's feature matrix at the in-scope rows sc (indices into P): FEATS order (the mask features, then the shape context)"""
    rows = []
    for i in sc:
        p = P[i]
        MB, NB, KB = shape(p['arm'])
        f = feats_json['%s|%s' % (p['arm'], p['mask'])]
        rows.append([float(f[c]) for c in FEATS_M] + [float(MB), float(NB), math.log(KB), float(FMT[p['fmt']]), float(p['f'])])
    return np.array(rows, float)
