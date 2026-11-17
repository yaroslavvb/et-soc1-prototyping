#!/usr/bin/env python3
"""MM1-v1: the model-selection table, recomputed (post hoc): every candidate time form of fit_time.VARIANTS and the energy forms of fit_energy on
the same 888 time points and 791 energy points, the same LOEO (12) and LOCO (3) folds, cold starts, every constant refitted per fold. The chosen
forms (time v1_r1conf_dramr0_t2us, energy pmem1) are the best of these on the same folds, so their held-out numbers are optimistic.

    /usr/bin/python3 -I -B select_forms.py --out <dir>        writes model_selection.json (about 6 minutes on aifoundry2)
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
import fit_energy as FE  # noqa: E402
import fit_time as FT  # noqa: E402
import fit_v1 as FV  # noqa: E402

ENERGY_FORMS = ('v0form', 'pmem1', 'pmemcard', 'pmem1_l3a3')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    P = D.time_points()
    E, _ = D.energy_points()
    tidx = {p['id']: i for i, p in enumerate(P)}
    G = FV.time_groups()
    out = {'what': __doc__.split('\n\n')[0], 'time_forms': {}, 'energy_forms': {}, 'python': sys.version.split()[0], 'numpy': np.__version__}
    for v in FT.VARIANTS:
        r, d = FT.run_variant(P, v)
        rec = {'config': FT.VARIANTS[v], 'theta_all': r['theta_all']}
        for lab in ('pred_in_sample', 'pred_loeo', 'pred_loco'):
            e = r[lab] / d.T - 1
            rec[lab.replace('pred_', '')] = {g: FV.st(e[[i for i, p in enumerate(P) if fn(p)]]) for g, fn in G.items()}
        el = r['pred_loeo'] / d.T - 1
        rec['loeo_by_exp'] = {x: FV.st(el[[i for i, p in enumerate(P) if p['exp'] == x]]) for x in sorted({p['exp'] for p in P})}
        out['time_forms'][v] = rec
        print(v, rec['in_sample']['all']['rms_pct'], rec['loeo']['all']['rms_pct'], rec['loeo_by_exp']['E206']['rms_pct']); sys.stdout.flush()
        if v == FV.TV1:
            eg = {'all': lambda e: True, 'E206': lambda e: e['exp'] == 'E206'}
            for ev in ENERGY_FORMS:
                th_all, th_f, acc = FV.energy_block(E, P, r, FT.VARIANTS[v], ev, tidx)
                out['energy_forms'][ev] = {'theta_all': th_all, 'stats': FV.energy_stats(E, acc, eg)}
    json.dump(out, open(os.path.join(a.out, 'model_selection.json'), 'w'), indent=1, sort_keys=True, default=float)


if __name__ == '__main__':
    main()
