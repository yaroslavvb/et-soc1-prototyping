#!/usr/bin/env python3
"""'MM1-v3.2 + mask-ceiling' (reference, REPORTED; round Q238 track C): THE PREDICTOR FOR NEW POINTS. Never a model candidate.

For each point {arm, kernel, fmt, mask, f} it returns the reference's op-time factor: exp(clip(yhat, -0.5, 0.5)) at an in-scope point
(rgm136's gemmL loop, arm gemmL<MB>x<NB>x<KB> with MB x NB >= 2, a shire subset), exactly 1 elsewhere; yhat = the all-data forest
(params-mask-ceiling.json: 200 trees, trained on every in-scope point through E224 at MM1-v3.2's all-data base) at the point's 22 features
(the 17 mask features by scripts/f01_features.py's code and layout2's committed f02_private.private_shared, the 5 shape-context features
by scripts/r_common.feature_rows' order). THE FORECAST: MM1-v3.2's own op time (tools/matmul/mm1/v3.2/mm1_v32.py Model at
out/mm1_v32_params.json: T_op_us, cycles_per_op_wall, seconds_per_gemm) times the factor; the counter's mean cycles stay MM1-v3.2's; W over
idle at the new op time by MM1-v3.2's law A_W + B_W_us / T_op_us. WITH AF4 (MM1-v3.3 = MM1-v3.2 + AF4): at a gemmLnc token take AF4's row
unchanged (this factor is 1 there), elsewhere this factor on MM1-v3.2's row (AF4 equals MM1-v3.2 off gemmLnc): scripts/c01_af4.py.

    python3 -I -B mask_ceiling.py --points <points.json> [--out <factors.json>]   (points.json: a list of {arm, kernel, fmt, mask, f})
    python3 -I -B mask_ceiling.py --selftest     (20 training configurations' features re-made from code, predictions equal fits)

Finds the lab's top from its own path (this folder is tools/matmul/mm1/v3.4-cands/mask-ceiling/); the committed f02 code reads
<stage>/work/lab, so a staging folder with work/lab -> the lab's top is made in a temporary directory (E224's models_e224.py's way).
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, 'scripts')
REPO = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..'))
if os.path.isdir(os.path.join(HERE, 'work', 'lab')):          # run from the lane folder (its scratch clone)
    REPO = os.path.join(HERE, 'work', 'lab')
_stage = tempfile.mkdtemp(prefix='mask-ceiling-stage-')
os.makedirs(os.path.join(_stage, 'work'))
os.symlink(REPO, os.path.join(_stage, 'work', 'lab'))
os.environ['MASK_CEILING_LANE'] = os.environ.get('MASK_CEILING_LANE_FOR_PREDICTOR', _stage)
sys.path.insert(0, SCRIPTS)
import r_common as RC  # noqa: E402
import rf_core as RF  # noqa: E402
import f01_features as F1  # noqa: E402

PARAMS = os.path.join(HERE, 'params-mask-ceiling.json')
if not os.path.exists(PARAMS):
    PARAMS = os.path.join(HERE, 'work', 'params-mask-ceiling.json')


def features(arm, mask):
    MB, NB, KB = RC.shape(arm)
    m = int(mask, 16)
    f = F1.mask_feats(m)
    r = F1.F02.private_shared(MB, NB, KB, m)
    f.update({'Fp': r['Fp'], 'Fs': r['Fs']})
    f['LAG'] = f['hlag'] * r['Fp'] / (r['Fp'] + r['Fs']) if (r['Fp'] + r['Fs']) > 0 else 0.0
    return f


class Reference:
    def __init__(self, params=PARAMS):
        d = json.load(open(params))
        assert d['features'] == list(RC.FEATS), 'feature order'
        self.forest = RF.Forest.from_json(d['forest'])
        self.clip = d['settings']['clip_ln']
        self.cache = {}

    def factor(self, p):
        q = {'arm': p['arm'], 'kernel': p.get('kernel', 'rgm136'), 'fmt': p['fmt'], 'mask': '0x%x' % int(str(p['mask']), 16)}
        if not RC.in_scope(q):
            return {'in_scope': False, 'ln_factor': 0.0, 'factor': 1.0}
        k = (q['arm'], q['mask'])
        if k not in self.cache:
            self.cache[k] = features(*k)
        ft = self.cache[k]
        MB, NB, KB = RC.shape(q['arm'])
        x = np.array([[float(ft[c]) for c in RC.FEATS_M] + [float(MB), float(NB), math.log(KB), float(RC.FMT[q['fmt']]), float(p['f'])]])
        y = float(np.clip(self.forest.predict(x)[0], -self.clip, self.clip))
        return {'in_scope': True, 'ln_factor': y, 'factor': math.exp(y), 'features': {c: float(ft[c]) for c in RC.FEATS_M}}


def selftest():
    fits = os.path.join(HERE, 'fits-mask-ceiling.json')
    if not os.path.exists(fits):
        fits = os.path.join(HERE, 'work', 'fits-mask-ceiling.json')
    F = json.load(open(fits))
    R = Reference()
    FJ = None
    for fp in (os.path.join(HERE, 'inputs', 'features.json'), os.path.join(HERE, 'work', 'features.json')):
        if os.path.exists(fp):
            FJ = json.load(open(fp))['features']
            break
    rows = F['all_data_in_sample'][:: max(1, len(F['all_data_in_sample']) // 20)][:20]
    bad, dmax = 0, 0.0
    for r in rows:
        o = R.factor({'arm': r['arm'], 'kernel': 'rgm136', 'fmt': r['fmt'], 'mask': r['mask'], 'f': r['f']})
        same_f = FJ is not None and all(o['features'][c] == float(FJ['%s|%s' % (r['arm'], r['mask'])][c]) for c in RC.FEATS_M)
        d = abs(o['ln_factor'] - r['yhat_all_data'])
        dmax = max(dmax, d)
        # the features must be re-made bit for bit; the ln factor to 1e-12 (the forest's mean over 200 trees sums in a different order for
        # one row than for the fit's batch of 888 rows: the last bit may differ)
        if not (o['in_scope'] and same_f and d <= 1e-12):
            bad += 1
            print('DIFF', r['id'], o['ln_factor'], r['yhat_all_data'], 'features equal' if same_f else 'FEATURES DIFFER')
    print('SELFTEST mask-ceiling predictor: %d of %d training configurations re-made from code: features bit-equal, ln factor within 1e-12 '
          'of the frozen fit (largest difference %.1e)' % (len(rows) - bad, len(rows), dmax))
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--points')
    ap.add_argument('--out')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    pts = json.load(open(a.points))
    R = Reference()
    out = [dict(p, **R.factor(p)) for p in pts]
    s = json.dumps(out, indent=1)
    if a.out:
        open(a.out, 'w').write(s)
    else:
        print(s)


if __name__ == '__main__':
    main()
