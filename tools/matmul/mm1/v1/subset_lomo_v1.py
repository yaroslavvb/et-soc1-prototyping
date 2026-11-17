#!/usr/bin/env python3
"""MM1-v1's subset terms held out properly: leave one shire mask out over E206's subset points, EVERY constant refitted from a cold start
without the mask's points. Desk; post hoc (every point existed before the fit); held out, not blind.

    /usr/bin/python3 -I -B subset_lomo_v1.py --out <dir>      writes subset_lomo_v1.json into <dir> (never this folder)

Why this file (verify-mm1v1 finding 2, Mon 16 Nov 2026): fit_v1.py's `subset_leave_one_mask_out` (holdout_v1.json) refits chi alone with each
mask held out and keeps every other constant at the all-data fit, which saw the held-out mask; its comparator zeroes chi without refitting
anything. Both are kept there, labelled "chi only". This file is the clean version:
  HELD OUT, v1's form: for each of E206's five subset masks, fit_time.fit on the other 874 + 9 points (cold start from fit_time.TH0; c3, m3, cF,
      mF, kA, x50, s, zeta, piF0, T2, chi and eta all refitted), then predict the mask's points;
  HELD OUT, no subset term: the same loop with chi and eta fixed at 0 (every other constant refitted without the mask);
  IN SAMPLE, no subset term: chi and eta fixed at 0, every other constant refitted on all 888 points (the comparator verify-mm1v1 quoted).
Errors are wall cycles an op, forecast / measured - 1. The measured side: data_v1.time_points (E206's points the mean of pass 1 and pass 2).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v1 as D  # noqa: E402
import fit_time as FT  # noqa: E402

TV1 = 'v1_r1conf_dramr0_t2us'


def st(e):
    e = np.asarray(e, float)
    if len(e) == 0:
        return None
    return {'n': int(len(e)), 'rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(e)) * 100, 2),
            'worst_pct': round(float(e[np.argmax(np.abs(e))]) * 100, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('subset_lomo_v1.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    P = D.time_points()
    var = FT.VARIANTS[TV1]
    var0 = dict(var, free=[k for k in var['free'] if k not in ('chi', 'eta')])
    data = FT.TimeData(P, var['masked_map'])
    halves = var.get('halves', False)
    sub = [i for i, p in enumerate(P) if p['exp'] == 'E206' and p['mask'] != '0xffffffff']
    masks = sorted({P[i]['mask'] for i in sub})
    held, held0, thetas = {}, {}, {}
    for m in masks:
        te = [i for i in sub if P[i]['mask'] == m]
        tr = np.array([i for i in range(len(P)) if P[i]['mask'] != m or P[i]['exp'] != 'E206'])
        assert not set(te) & set(tr.tolist())
        th = FT.fit(data, tr, var)
        pr = data.predict(th, var['rule'], halves=halves)
        th0 = FT.fit(data, tr, var0)
        pr0 = data.predict(th0, var['rule'], halves=halves)
        for i in te:
            held[i] = float(pr[i])
            held0[i] = float(pr0[i])
        thetas[m] = {'v1 form': th, 'no subset term': th0, 'n_train': int(len(tr)), 'n_held_out': len(te)}
        print(m, 'held out', len(te), 'chi', round(th['chi'], 4), 'eta', round(th['eta'], 6),
              'v1 form rms %.2f%%' % (100 * np.sqrt(np.mean([(held[i] / data.T[i] - 1) ** 2 for i in te]))),
              'no term rms %.2f%%' % (100 * np.sqrt(np.mean([(held0[i] / data.T[i] - 1) ** 2 for i in te])))); sys.stdout.flush()
    thin = FT.fit(data, np.arange(len(P)), var0)
    pin = data.predict(thin, var['rule'], halves=halves)
    e1 = [held[i] / data.T[i] - 1 for i in sub]
    e0 = [held0[i] / data.T[i] - 1 for i in sub]
    ein = [pin[i] / data.T[i] - 1 for i in sub]
    res = {'what': "leave one shire mask out over E206's subset points, every constant refitted from a cold start (fit_time.TH0) without the "
                   "mask's points; beside it the form with no subset term (chi = eta = 0), held out the same way and in sample",
           'label': 'desk; post hoc; held out (one mask at a time), not blind; wall cycles an op',
           'answers': 'verify-mm1v1 finding 2 (Mon 16 Nov 2026): holdout_v1.json subset_leave_one_mask_out refits chi only (labelled chi only)',
           'form': TV1, 'n_points': len(sub), 'masks': masks,
           'held_out_v1_form': st(e1), 'held_out_no_subset_term': st(e0), 'in_sample_no_subset_term_all_888': st(ein),
           'by_mask_rms_pct': {m: {'v1 form held out': st([held[i] / data.T[i] - 1 for i in sub if P[i]['mask'] == m])['rms_pct'],
                                   'no subset term held out': st([held0[i] / data.T[i] - 1 for i in sub if P[i]['mask'] == m])['rms_pct'],
                                   'no subset term in sample': st([pin[i] / data.T[i] - 1 for i in sub if P[i]['mask'] == m])['rms_pct']} for m in masks},
           'thetas': thetas, 'theta_no_subset_term_all_888': thin,
           'points': [{'id': P[i]['id'], 'arm': P[i]['arm'], 'fmt': P[i]['fmt'], 'mask': P[i]['mask'], 'meas_cyc_wall': round(data.T[i] * P[i]['f'], 1),
                       'held_out_v1_form': round(held[i] * P[i]['f'], 1), 'held_out_no_subset_term': round(held0[i] * P[i]['f'], 1),
                       'in_sample_no_subset_term': round(float(pin[i]) * P[i]['f'], 1),
                       'err_pct_v1_form': round((held[i] / data.T[i] - 1) * 100, 2), 'err_pct_no_term_held_out': round((held0[i] / data.T[i] - 1) * 100, 2)}
                      for i in sub],
           'python': sys.version.split()[0], 'numpy': np.__version__}
    json.dump(res, open(os.path.join(out, 'subset_lomo_v1.json'), 'w'), indent=1, sort_keys=True)
    print('held out, v1 form:', res['held_out_v1_form'])
    print('held out, no subset term:', res['held_out_no_subset_term'])
    print('in sample, no subset term (all 888):', res['in_sample_no_subset_term_all_888'])


if __name__ == '__main__':
    main()
