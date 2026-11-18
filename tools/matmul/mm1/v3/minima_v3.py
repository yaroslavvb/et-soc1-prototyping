#!/usr/bin/env python3
"""MM1-v3: the minima the six declared starts reach (a diagnostic, in sample only; it changes nothing frozen). For each form named, the all-data
time fit from each start alone: its training cost, evaluations, status, in-sample rms and constants. Desk; numpy; post hoc.

    /usr/bin/python3 -I -B minima_v3.py --out <dir> <form> [<form> ...]      writes <dir>/minima_<form>.json ('+' written as '_')

Why: in fit_v3.py's record most folds of MM1-v3's forms have one start of six at the lowest training cost (n_starts_at_best 1); this shows
what the other starts reach (README section 3).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_v3 as D  # noqa: E402
import engine_v3 as E  # noqa: E402
import fit_v3 as F  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('forms', nargs='+')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    P = D.time_points()
    eng = E.TimeEngine(P)
    rung = np.array([bool(p['exp'] == 'E146' and F.STORE_RUNG.search(p['id'])) for p in P])
    tr = np.arange(len(P))[~rung]
    Tm = np.array([p['T'] for p in P])
    for name in a.forms:
        form, free = F.form_of(name)
        rec = {'form': name, 'free': free, 'interpreter': sys.version.split()[0], 'label': 'in sample only; post hoc; a diagnostic', 'starts': []}
        for j, s0 in enumerate(F.STARTS):
            th, r = F.fit_time(eng, P, tr, None, form, free, starts=[s0])
            e = eng.predict(th, form)[tr] / Tm[tr] - 1
            s = r['starts'][0]
            rec['starts'].append({'start': j, 'train_cost': s['train_cost'], 'nfev': s['nfev'], 'status': s['status'],
                                  'in_sample_rms_pct': round(float(np.sqrt(np.mean(e ** 2))) * 100, 3),
                                  'theta': {k: round(float(th[k]), 5) for k in free}})
            print(name, j, s['train_cost'], rec['starts'][-1]['in_sample_rms_pct'], flush=True)
        fn = os.path.join(a.out, 'minima_%s.json' % re.sub('[^A-Za-z0-9_]', '_', name))
        json.dump(rec, open(fn, 'w'), indent=1, sort_keys=True)


if __name__ == '__main__':
    main()
