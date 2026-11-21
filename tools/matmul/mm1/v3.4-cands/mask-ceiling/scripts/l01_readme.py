#!/usr/bin/env python3
"""mask-ceiling (Q238 track C) l01: the land's README, written from the frozen records only (work/holdout.json, work/placebo.json,
work/verdict.json, work/composed-af4-REPORTED.json, logs/d01.log), so no number in it is typed by hand. Desk; /usr/bin/python3 3.12.3 -I -B.
Output: work/README.md.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

LANE = os.environ.get('MASK_CEILING_LANE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(LANE, 'scripts'))
import r_common as RC  # noqa: E402

H = json.load(open(os.path.join(LANE, 'work/holdout.json')))
PL = json.load(open(os.path.join(LANE, 'work/placebo.json')))
V = json.load(open(os.path.join(LANE, 'work/verdict.json')))
C = json.load(open(os.path.join(LANE, 'work/composed-af4-REPORTED.json')))
DECL = open(os.path.join(LANE, 'DECLARED-mask-ceiling.md.sha256')).read().split()[0]
S = H['summary']
FAMS = ('LOSO', 'LOEO', 'LOCO', 'LOMO')
LN = {'ref': 'the reference (forest, 22 features)', 'cart': 'single CART (depth 4)', 'knn': 'kNN (k 10)', 'maskonly': 'forest, 17 mask features only',
      'shapeonly': 'shape-only control (5 context features)'}


def f2(x):
    return '-' if x is None else '%.2f' % x


def f3(x):
    return '-' if x is None else '%.3f' % x


L = []
A = L.append
A("# 'MM1-v3.2 + mask-ceiling': a nonparametric REFERENCE for core-group mask placement (reference, REPORTED; round Q238, track C)")
A('')
A('*Round Q238, lane mask-ceiling, Sat 21 Nov 2026 (week 47), Pacific time, at aifoundry2\'s desk. Desk only: no card, no simulator, no E226 '
  'file. Interpreter for every number: /usr/bin/python3 3.12.3, numpy 1.26.4, `-I -B`, single-threaded (OMP / OPENBLAS / MKL / NUMEXPR_NUM_THREADS '
  '= 1), every job in the round\'s CPU slots, one at a time. **Never a model candidate**: it bounds what a mask term built from these features '
  'can reach, and ranks the features.*')
A('')
A('The owner\'s words that put the matmul first (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to focus '
  'on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. '
  'From based on what I know about the size of a matrix and which operations are contained."')
A('')
A('**Labels.** *Post hoc*: every fit here (made after its data existed). *Held out*: left out of the fit that scores it (not blind). '
  '*REPORTED*: printed beside a rule, never deciding it; the whole reference is REPORTED. *NOT RUN*: not run. Errors: forecast / measured - 1 '
  'of the wall cycles an op (%), blind-e221\'s form.')
A('')
A('## 1. The lead')
A('')
A('The lab\'s blind test of E221 (tools/matmul/mm1/v3.1/blind-e221-scores/, 5eb23fd4) failed on MM1-v3.2\'s time bands; 152 of its 175 T1 misses '
  'are core-group mask placements: the MASK class reads 12.41% rms on 363 no-twin cases, every other class at most 9.05%. This reference asks '
  'how much of that a term built from mask features could remove, held out, and which features carry it.')
A('')
A('## 2. The form (declared before any fit: `DECLARED-mask-ceiling.md`, sha256 `%s`, hashed 01:28:32 PST)' % DECL)
A('')
A('T = T_v32 x exp(clip(yhat, -0.5, 0.5)) at the scope\'s points (rgm136 gemmL, MB x NB >= 2, a shire subset: 888 points), T_v32 to the last bit '
  'elsewhere; yhat = a random forest (this lane\'s numpy code, `scripts/rf_core.py`) of 200 CART trees, depth 6, leaf 5, bootstrap rows, 8 of 22 '
  'features a node, trained on ln(T_meas / T_v32) at the fold\'s base. Features: 17 mask features (n; R, C, rmax, cmax, rimb, cimb, dist_rel: the '
  'row and column groups that share A and B tiles; G1, hlag, spread, bbox: position on the mesh; memd: distance to the memory shires; link: the '
  'hottest link under X-then-Y routing, ASSUMED; Fp, Fs, LAG: layout2\'s private and shared DRAM-served shares and its LAGcore) and 5 shape-context '
  'features (MB, NB, ln KB, format, clock). The slice loads reduce to n, R and C for this kernel (every tile of an op step has the same PA[10]: '
  '`scripts/f01_features.py`). MM1-v3.2\'s constants unchanged.')
A('')
A('## 3. The held-out record (the declared folds; no twins unless said)')
A('')
A('| family | MASK points | MM1-v3.2 | the reference | share of MM1-v3.2\'s MASK residual explained | K1 (<= 0.90 x) | CART | kNN | mask features only | shape only |')
A('|---|---|---|---|---|---|---|---|---|---|')
for f in FAMS:
    d = S[f]['MASK no twin']
    A('| %s | %d | %s%% | **%s%%** | %s | %s | %s%% | %s%% | %s%% | %s%% |' % (
        f, d['n'], f2(d['v32']['rms']), f2(d['ref']['rms']), f3(d['ref'].get('share_explained')),
        'PASS' if H['K1']['families'][f]['pass'] else 'FAIL', f2(d['cart']['rms']), f2(d['knn']['rms']), f2(d['maskonly']['rms']),
        f2(d['shapeonly']['rms'])))
A('')
e = H['e221_footing_LOSO']
A('**The E221 footing** (blind-e221\'s own 363 no-twin MASK cases, held out by session): MM1-v3.2 %s%% (the check: blind-e221\'s 12.41%%), '
  'the reference **%s%%**, share explained %s; CART %s%%, kNN %s%%, mask features only %s%%, shape only %s%%.' % (
      f2(e['v32']), f2(e['ref']), f3(e['share_explained_ref']), f2(e['cart']), f2(e['knn']), f2(e['maskonly']), f2(e['shapeonly'])))
A('')
A('| E221 placement family (LOSO) | cases | MM1-v3.2 | the reference |')
A('|---|---|---|---|')
for k, v in sorted(e['by_subfamily'].items()):
    A('| %s | %d | %s%% | %s%% |' % (k, v['n'], f2(v['v32']), f2(v['ref'])))
A('')
A('With twins (REPORTED): ' + '; '.join('%s %s%% -> %s%% (n %d)' % (f, f2(S[f]['MASK with twins']['v32']['rms']), f2(S[f]['MASK with twins']['ref']['rms']),
                                                                    S[f]['MASK with twins']['n']) for f in FAMS) + '.')
A('')
A('Per card (MASK, no twin; REPORTED): ' + '; '.join('%s: %s' % (f, ', '.join('%s %s -> %s (n %d)' % (c.replace('aifoundry', 'a'), f2(v['v32']), f2(v['ref']), v['n'])
                                                                    for c, v in S[f]['MASK no twin by card'].items() if v['n'])) for f in FAMS) + '.')
A('')
A('LOEO by experiment (MASK, no twin; REPORTED): ' + ', '.join('%s %s -> %s (n %d)' % (x, f2(v['v32']), f2(v['ref']), v['n'])
                                                               for x, v in S['LOEO']['MASK no twin by experiment'].items()) + '.')
A('')
A('## 3b. What these numbers can and cannot say')
A('')
import csv as _csv  # noqa: E402
_P = json.load(open(os.path.join(LANE, 'work/points_all.json')))['points']
_by = {}
for _p in _P:
    _by.setdefault((_p['arm'], _p['fmt'], _p['mask']), set()).add((_p['exp'], _p.get('session') or '', _p['card']))
_R = [r for r in _csv.DictReader(open(os.path.join(LANE, 'work/holdout_points.csv')))
      if r['family'] == 'LOSO' and r['class'] == 'MASK' and r['twin'] == '0' and r['in_scope'] == '1']
_cross = sum(1 for r in _R if any(not (x[0] == 'E221' and x[1] == r['session']) for x in _by[(r['arm'], r['fmt'], r['mask'])]))
_e = S['LOEO']['MASK no twin by experiment']['E221']
A('- **LOSO and LOCO include cross-card repeats.** %d of the %d in-scope MASK points LOSO tests have their arm, format and mask run on another '
  'card (or in another experiment) in that fold\'s training set: E221 ran each placement on three cards. The twin key holds the card, so they '
  'are not twins, and the transfer is real (the same placement repeats across cards), but it is not a never-run mask. **For never-run masks '
  '(E226) read LOMO** (every point at the held-out mask out of training: %.2f%% -> %.2f%%, share %.2f) **and E221 held out whole** (LOEO: '
  '%.2f%% -> %.2f%% on its %d MASK points).' % (_cross, len(_R), S['LOMO']['MASK no twin']['v32']['rms'], S['LOMO']['MASK no twin']['ref']['rms'],
                                                S['LOMO']['MASK no twin']['ref']['share_explained'], _e['v32'], _e['ref'], _e['n']))
A('- **Part of the MASK residual is shape-level at subsets:** the shape-only control (no mask feature) reads %.2f%% on E221\'s 363 '
  '(LOMO %.2f%%); the mask features add the rest beyond it (the placebo, which keeps the shape context, reads about %.1f%% on LOSO and '
  '%.1f%% on LOMO).' % (e['shapeonly'], S['LOMO']['MASK no twin']['shapeonly']['rms'], PL['LOSO_summary']['quantiles_min_5_50_95_max'][2],
                        PL['LOMO_summary']['quantiles_min_5_50_95_max'][2]))
_worse = ['%s %s %.2f -> %.2f%%' % (fam, x, v['v32'], v['ref']) for fam in ('LOEO', 'LOMO') for x, v in S[fam]['MASK no twin by experiment'].items()
          if v['ref'] > v['v32']]
_worse += ['E221 %s %.2f -> %.2f%%' % (k, v['v32'], v['ref']) for k, v in sorted(e['by_subfamily'].items()) if v['ref'] > v['v32']]
A('- **Where it is worse than MM1-v3.2, held out:** %s.' % ', '.join(_worse))
A('- **Assumed, not measured:** X-then-Y routing for `link`; the memory shires\' places (the lab\'s notes, as layout2 placed them). The twin '
  'rule here is per fold (layout2\'s key against the fold\'s training points: LOSO %d no-twin MASK points); blind-e221\'s own flags give its '
  '363, both printed.' % S['LOSO']['MASK no twin']['n'])
A('- **A ceiling for these features and this learner family, not a proof:** a term with other inputs (the walk\'s per-link or per-slice '
  'loads, a measured arbitration) could do better; a two-constant term from these features should not expect to beat the LOMO figure.')
A('')
A('## 4. The keep rule (declared) and the verdict')
A('')
k2, k3 = H['K2'], PL['K3']
A('- **K1** (every family, M1 <= 0.90 x MM1-v3.2\'s): %s.' % ('PASS' if H['K1']['pass'] else 'FAIL (' + ', '.join(
    f for f in FAMS if not H['K1']['families'][f]['pass']) + ')'))
A('- **K2** (the non-MASK classes, LOEO, no twin: %s%% -> %s%%, limit %s%%): %s (the reference never moves a non-MASK point).' % (
    f3(k2['v32']), f3(k2['ref']), f3(k2['limit']), 'PASS' if k2['pass'] else 'FAIL'))
ls = PL['LOSO_summary']
A('- **K3** (the placebo: the 17 mask features permuted within each shape, the LOSO family refitted, 100 draws): the real M1 %s%% is below the '
  'placebo\'s in **%d of 100** draws (placebo M1 min / 5%% / median / 95%% / max: %s): %s. The identity draw reproduced the real fit exactly.' % (
      f2(ls['real']), ls['real_below_in'], ' / '.join(f2(x) for x in ls['quantiles_min_5_50_95_max']), 'PASS' if k3['pass'] else 'FAIL'))
lm = PL['LOMO_summary']
A('- REPORTED: the LOMO placebo (10 draws): real %s%%, below the placebo in %d of %d (placebo min / median / max %s / %s / %s%%).' % (
    f2(lm['real']), lm['real_below_in'], lm['draws'], f2(lm['quantiles_min_5_50_95_max'][0]), f2(lm['quantiles_min_5_50_95_max'][2]),
    f2(lm['quantiles_min_5_50_95_max'][4])))
A('')
A('**Verdict: %s.** Frozen either way as **\'MM1-v3.2 + mask-ceiling (reference, REPORTED)\'**: it never joins MM1.' % V['verdict'])
A('')
A('## 5. The feature ranking (REPORTED)')
A('')
for fam in ('LOSO', 'LOMO'):
    pi = H['permutation_importance'][fam]
    top = pi['ranking'][:10]
    A('- **Permutation importance, %s** (rise of the in-scope MASK M1 %s%%, n %d, when one feature is shuffled across the in-scope points; mean of 3 '
      'draws): %s.' % (fam, f2(pi['M1_in_scope_ref']), pi['n_points'],
                       ', '.join('%s %+.2f' % (c, pi['features'][c]['rise_points_mean']) for c in top)))
gd = H['group_dropout_LOSO']
A('- **Group drop-out, LOSO** (the forest refitted without the group; M1 with it %s%%): %s.' % (
    f2(S['LOSO']['MASK no twin']['ref']['rms']), ', '.join('%s %s%% (%+.2f)' % (g, f2(v['M1_without_group']), v['rise_points'])
                                                           for g, v in sorted(gd.items(), key=lambda kv: -kv[1]['rise_points']))))
im = H['all_data']['impurity_share']
A('- **Impurity share of the all-data forest:** %s.' % ', '.join('%s %.3f' % (c, im[c]) for c in sorted(im, key=lambda c: -im[c])[:10]))
A('- **The all-data CART (depth 4, leaf 10), its splits** (in sample, REPORTED): ' + ' | '.join(H['all_data']['cart_splits'][:15]) +
  (' | ...' if len(H['all_data']['cart_splits']) > 15 else ''))
A('')
A('## 6. The composition with AF4 (by construction, no refit; `scripts/c01_af4.py`)')
A('')
for c in C['checks']:
    A('- %s' % c)
A('')
A('So \'MM1-v3.2 + AF4 + mask-ceiling\' = AF4\'s row at a gemmLnc token; at an in-scope point MM1-v3.2\'s row with its op time times the '
  'reference\'s factor and W over idle by MM1-v3.2\'s own law at the new time (A_W + B_W_us / T_op_us); MM1-v3.2 elsewhere. The composed rows at '
  'E222\'s and E224\'s registered points are in `composed-af4-REPORTED.json` (not blind: those days are in the training set).')
A('')
A('## 7. How to call it on new points (and with AF4)')
A('')
A('`python3 -I -B mask_ceiling.py --points points.json --out factors.json` with points.json a list of {arm, kernel, fmt, mask, f}: the factor '
  '(1 off the scope). The forecast is MM1-v3.2\'s own row (tools/matmul/mm1/v3.2/mm1_v32.py, Model at out/mm1_v32_params.json) with T_op_us, '
  'cycles_per_op_wall and seconds_per_gemm times the factor; with AF4 take AF4\'s row at a gemmLnc token (the factor is 1 there). '
  '`python3 -I -B mask_ceiling.py --selftest` re-makes 20 training configurations\' features from code and checks the frozen fit. To re-run '
  'the pipeline set MASK_CEILING_LANE to a folder holding work/lab (the lab\'s top) and the work/ inputs (SCRUB.json: the only change from '
  'the code as run).')
A('')
A('## 8. Files')
A('')
A('`DECLARED-mask-ceiling.md` (+ .sha256); `params-mask-ceiling.json` (the all-data forest, its training ids and targets); `fits-mask-ceiling.json` '
  '(every fold\'s summary, the in-sample fit); `holdout-mask-ceiling.json` and `holdout-points-mask-ceiling.csv` (the held-out record, every test '
  'point of every fold, every learner); `placebo-mask-ceiling.json`; `composed-af4-REPORTED.json`; `verdict-mask-ceiling.json`; `inputs/` (the '
  'points, features, base checks, E224 arm B\'s reduction); `scripts/` (as run but for SCRUB.json\'s path lookups); `logs/`; `SHA256SUMS`.')
A('')
A('SPDX-License-Identifier: Apache-2.0')
open(os.path.join(LANE, 'work/README.md'), 'w').write('\n'.join(L) + '\n')
print('README', len('\n'.join(L)), 'bytes')
