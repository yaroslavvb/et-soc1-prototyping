#!/usr/bin/env python3
"""lay-contention s11 (REPORTED robustness check, after the freeze; it changes no frozen file): F1 (and G1 if time allows) refitted
JOINTLY with every MM1-v3.1 time constant, by fit_v31.fit_time unchanged (18 declared starts, phase 2, the pin rule), the layout
constant 'lay_a' free in [-3, 3] from 0 at every start, on the same LOEO and LOLO folds; held-out scores as s04. Desk;
/usr/bin/python3 3.12.3 -I -B; single-threaded; resumable (work/s11_joint.json.partial)."""
import csv
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
sys.path.insert(0, HERE)
import eval_layout as S  # noqa: E402

FV, E = S.FV, S.E


class EngLay(FV.TV.Engine31):
    def __init__(self, P, phi):
        super().__init__(P)
        self.phi = phi

    def predict(self, th, form, return_q=False):
        T = super().predict(th, form)
        return T * np.clip(1.0 + th.get('lay_a', 0.0) * self.phi, 0.3, 3.0)


def main():
    which = sys.argv[1:] or ['F1', 'G1']
    t0 = time.time()
    rec = json.load(open(os.path.join(S.V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    assert [p['id'] for p in P] == rec['ids']
    form, _ = FV.parse_form_name(rec['form_name'])
    free_all = list(rec['free']) + ['lay_a']
    FV.LO['lay_a'], FV.HI['lay_a'] = -3.0, 3.0
    FV.NEUTRAL['lay_a'] = 0.0
    for s in FV.TIME_STARTS:
        s['lay_a'] = 0.0
    N = len(P)
    Tm = np.array([p['T'] for p in P])
    rung = FV.rung_mask(P)
    rows = {r['id']: r for r in csv.DictReader(open(os.path.join(S.V31, 'out/points_time_v31.csv')))}
    twin = np.array([rows[p['id']]['twin_LOEO'] == '1' for p in P])
    phi = {'F1': np.zeros(N), 'G1': np.zeros(N)}
    for j, p in enumerate(P):
        lp = E.loop_of(p['arm'], p['kernel']) if S.SHAPE.match(p['arm']) else None
        v, k = S.phi_of(lp, p['arm'], p['mask'])
        phi['F1'][j] = v[0]
        if k:
            f, g = S.FEATS[k], S.FEATS[k.rsplit('|', 1)[0] + '|0xffffffff']
            phi['G1'][j] = (110.0 + 12.0 * f['mesh_hop_mean']) / (110.0 + 12.0 * g['mesh_hop_mean']) - 1.0
    sub = np.array([int(p['mask'], 16) != S.FULL for p in P])
    lclass = np.array([FV.lolo_class(p['mask']) or '' for p in P])
    ALL = np.arange(N)
    fn = os.path.join(WORK, 'joint_layout.json')
    part = fn + '.partial'
    out = json.load(open(part)) if os.path.exists(part) else {}
    folds = [f for f in rec['folds'] if f.startswith('LOEO E') and len(f.split()) == 2] + ['LOLO compact', 'LOLO spread', 'LOLO other']
    for fm in which:
        en = EngLay(P, phi[fm])
        R = out.setdefault(fm, {'folds': {}})
        if 'all' not in R:
            FV.wait_load(print)
            t1 = time.time()
            th, frec = FV.fit_time(en, P, Tm, ALL[~rung], ALL[rung], form, free_all)
            R['all'] = {'lay_a': th['lay_a'], 'theta': th, 'secs': round(time.time() - t1, 1), 'winner_start': frec['winner_start']}
            print(f'{fm} all-data: lay_a {th["lay_a"]:+.5f} ({R["all"]["secs"]} s)', flush=True)
            json.dump(out, open(part, 'w'), default=float)
        for fname in folds:
            if fname in R['folds']:
                continue
            te = np.array(rec['folds'][fname]['test_idx'])
            tm = np.zeros(N, bool)
            tm[te] = True
            tr = ALL[(~tm) & (~rung)]
            FV.wait_load(print)
            t1 = time.time()
            th, frec = FV.fit_time(en, P, Tm, tr, te, form, free_all)
            pred = en.predict(th, form)
            d = {'lay_a': th['lay_a'], 'eta': th.get('eta'), 'pred_test': pred[te].tolist(), 'test_idx': te.tolist(),
                 'secs': round(time.time() - t1, 1)}
            if fname == 'LOLO compact':
                th0 = dict(th)
                th0['eta'] = 0.0
                d['pred_test_b'] = en.predict(th0, form)[te].tolist()
            R['folds'][fname] = d
            e = pred[te] / Tm[te] - 1
            print(f'{fm} {fname}: n {len(te)} rms {100 * np.sqrt(np.mean(e ** 2)):.3f}% lay_a {th["lay_a"]:+.4f} ({d["secs"]} s, '
                  f'total {time.time() - t0:.0f} s)', flush=True)
            json.dump(out, open(part, 'w'), default=float)
        # scores
        hl = np.full(N, np.nan)
        ha = np.full(N, np.nan)
        hb = np.full(N, np.nan)
        for fname, d in R['folds'].items():
            te = np.array(d['test_idx'])
            if fname.startswith('LOEO'):
                hl[te] = d['pred_test']
            else:
                ha[te] = d['pred_test']
                hb[te] = d.get('pred_test_b', d['pred_test'])
        m = ~twin & ~np.isnan(hl)
        R['scores'] = {'LOEO_no_twin_rms': S.rms(hl[m] / Tm[m] - 1), 'LOEO_no_twin_n': int(m.sum()),
                       'LOEO_subset_no_twin_rms': S.rms(hl[m & sub] / Tm[m & sub] - 1),
                       'LOLO_a_rms': S.rms(ha[sub] / Tm[sub] - 1), 'LOLO_b_rms': S.rms(hb[sub] / Tm[sub] - 1),
                       'LOLO_b_by_class': {c: S.rms(hb[sub & (lclass == c)] / Tm[sub & (lclass == c)] - 1) for c in ('compact', 'spread', 'other')},
                       'lay_a_by_fold': {k: v['lay_a'] for k, v in R['folds'].items()}}
        print(fm, json.dumps(R['scores'], indent=0), flush=True)
        json.dump(out, open(part, 'w'), default=float)
    json.dump(out, open(fn, 'w'), indent=1, default=float)
    print('secs', round(time.time() - t0, 1))


if __name__ == '__main__':
    main()
