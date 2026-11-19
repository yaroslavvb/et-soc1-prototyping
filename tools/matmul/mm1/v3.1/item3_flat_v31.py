#!/usr/bin/env python3
"""MM1-v3.1: item 3's constants checked for identification in every LOEO fold, post hoc (lane fix-fit-v31, round Q222, answering
verify-fit-v31's finding 1). Desk; REPORTED; no fit; never deciding a rule.

For each of item 3's forms with constants (Gplace, Goperand, Gcoop: item 8's winner + G + n/32, their fits in out/fits/), in every LOEO fold,
each free constant of the form is moved alone to its two declared bounds with the fold's other constants at the fold's fitted values. A
constant whose training predictions do not change at all (max |change| exactly 0) has no sensitivity in that fold: the fold's training cost
is flat along it, and the fold's fitted value is wherever the optimizer stopped. For each such constant the fold's training cost and its
held-out predictions are re-evaluated over the bounds (37 even steps and the fold's own value); item 3's scores (the LOEO wall rms over the
touched points, twins excluded and with them; the pooled LOEO wall rms over all points) are re-made with that fold's predictions replaced and
every other fold as stored; and item 3's rule and guard (DECLARED-v31.md section 3) are re-applied at each value.

Writes <out>/item3_flat_v31.json (run again, only its 'when' and 'secs' change). With --label it adds the labels to <out>/decisions_v31.json's
step3: new keys only, no existing key changed; run again, it writes the same file.

    /usr/bin/python3 -I -B item3_flat_v31.py --out out [--label]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_v31 as F  # noqa: E402

TV, DV = F.TV, F.DV
G_FORMS = ('Gplace', 'Goperand', 'Gcoop')
G_NCONST = {'G0': 0, 'Gcoop': 3, 'Gplace': 5, 'Goperand': 5}
ORDER = {'G0': 0, 'Gcoop': 1, 'Gplace': 2, 'Goperand': 3}
NGRID = 37
BY = 'fix-fit-v31 (Q222), answering verify-fit-v31 finding 1 (medium)'


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rms(e):
    """run_v31.rms"""
    e = np.asarray([x for x in e if x is not None and not (isinstance(x, float) and math.isnan(x))], float)
    return float(np.sqrt(np.mean(e ** 2))) * 100 if len(e) else None


def rule3(scores, pools):
    """item 3's rule and guard (run_v31.Run.step3): the winner by score, within 0.25 points the fewer constants, then Gplace before Goperand;
    the guard: the winner's pooled LOEO wall rms within 0.05 points of G0's, else G0"""
    best = min(scores.values())
    cands = [g for g in scores if scores[g] <= best + 0.25]
    win = sorted(cands, key=lambda g: (G_NCONST[g], ORDER[g]))[0]
    guard = pools[win] <= pools['G0'] + 0.05
    return win, guard, (win if guard else 'G0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--label', action='store_true')
    a = ap.parse_args()
    O = a.out
    t0 = time.time()
    dpath = os.path.join(O, 'decisions_v31.json')
    D = json.load(open(dpath))
    s3 = D['steps']['step3']
    tcs = 'T5r' if D['steps']['step1']['tc'] == 'r2' else 'tC'
    P = DV.time_points()
    ids = [p['id'] for p in P]
    N = len(P)
    ALL = np.arange(N)
    Tm = np.array([p['T'] for p in P])
    rung = F.rung_mask(P)
    touched = np.array([F._loop(p) in F.TOUCHED for p in P])
    ones = np.ones(N, bool)
    en = TV.Engine31(P)
    TR = {}
    fits_sha = {}
    for G in ('G0',) + G_FORMS:
        fp = os.path.join(O, 'fits', f'time_{tcs}+{G}+n32.json')
        TR[G] = json.load(open(fp))
        fits_sha[f'out/fits/time_{tcs}+{G}+n32.json'] = sha(fp)
        assert TR[G]['ids'] == ids, f'{G}: the fit is for another point set'

    def loeo_pred(rec):
        """run_v31.Run.loeo_pred"""
        pr = np.full(N, np.nan)
        tw = np.zeros(N, bool)
        for name, fd in rec['folds'].items():
            if not (name.startswith('LOEO ') and name[5:] in F.LOEO_EXPS):
                continue
            te = np.array(fd['test_idx'])
            pr[te] = fd['pred_test']
            m = np.zeros(N, bool)
            m[te] = True
            trc = {F.cfg_t(P[i]) for i in range(N) if not m[i] and not rung[i]}
            for i in te:
                tw[i] = F.cfg_t(P[i]) in trc
        return pr, tw

    def err(pr, sel):
        return [pr[i] / Tm[i] - 1 for i in range(N) if sel[i] and not math.isnan(pr[i])]

    def scores_of(pr, tw):
        return {'touched_no_twin': rms(err(pr, touched & ~tw)), 'touched_with_twins': rms(err(pr, touched)), 'pooled_LOEO_all': rms(err(pr, ones))}

    base, repl = {}, {}
    for G in TR:
        pr, tw = loeo_pred(TR[G])
        base[G] = (pr, tw)
        sc = scores_of(pr, tw)
        st = s3['forms'][G]
        repl[G] = {'stored': {'touched_no_twin': st['score_touched_no_twin'], 'touched_with_twins': st['score_touched_with_twins'],
                              'pooled_LOEO_all': st['pooled_LOEO_all']},
                   'remade': sc,
                   'equal': (sc['touched_no_twin'] == st['score_touched_no_twin'] and sc['touched_with_twins'] == st['score_touched_with_twins']
                             and sc['pooled_LOEO_all'] == st['pooled_LOEO_all'])}
    stored_scores = {g: repl[g]['stored']['touched_no_twin'] for g in repl}
    stored_pools = {g: repl[g]['stored']['pooled_LOEO_all'] for g in repl}

    screen, flats, fold_checks = [], [], []
    for G in G_FORMS:
        form, free = F.parse_form_name(f'{tcs}+{G}+n32')
        for fn, fd in TR[G]['folds'].items():
            if not (fn.startswith('LOEO ') and fn[5:] in F.LOEO_EXPS):
                continue
            te = np.array(fd['test_idx'])
            tmask = np.zeros(N, bool)
            tmask[te] = True
            tr = ALL[(~tmask) & (~rung)]
            th = dict(fd['theta'])
            pins = fd['fit']['pins']
            p0 = en.predict(th, form)
            c0 = 0.5 * float(np.sum((p0[tr] / Tm[tr] - 1.0) ** 2))
            fold_checks.append({'form': G, 'fold': fn, 'pred_test_max_rel_diff_vs_stored': float(np.max(np.abs(p0[te] / np.array(fd['pred_test']) - 1))),
                                'train_cost_remade': c0, 'train_cost_stored': fd['fit']['winner_cost']})
            for k in TV.G_CONST[G]:
                if k in pins:
                    screen.append({'form': G, 'fold': fn, 'constant': k, 'pinned_at': pins[k]})
                    continue
                lo, hi = F.LO[k], F.HI[k]
                plo = en.predict({**th, k: lo}, form)
                phi = en.predict({**th, k: hi}, form)
                if k in F.PIN_SETS:
                    inset = [int(i) for i in tr if F.PIN_SETS[k](P[i])]
                else:
                    inset = [int(i) for i in tr if F.PIN_SETS['gamma_3'](P[i]) or F.PIN_SETS['gamma_F'](P[i])]
                d_tr = float(np.max(np.abs(plo[tr] - phi[tr])))
                rec = {'form': G, 'fold': fn, 'constant': k, 'fold_value': th[k], 'bounds': [lo, hi],
                       'train_max_abs_change_us': d_tr, 'train_max_rel_change': float(np.max(np.abs(plo[tr] / phi[tr] - 1))),
                       'test_max_rel_change': float(np.max(np.abs(plo[te] / phi[te] - 1))),
                       'pin_set_training_points': len(inset), 'pin_set_training_ids': [P[i]['id'] for i in inset][:12],
                       'pin_set_max_abs_change_us': (float(np.max(np.abs(plo[inset] - phi[inset]))) if inset else None),
                       'flat': d_tr == 0.0}
                screen.append(rec)
                if d_tr == 0.0:
                    flats.append((G, fn, k, form, th, te, tr, fd))

    by_fold = {}
    for G, fn, k, *_ in flats:
        by_fold.setdefault((G, fn), []).append(k)
    scans = []
    for G, fn, k, form, th, te, tr, fd in flats:
        lo, hi = F.LO[k], F.HI[k]
        grid = sorted(set([float(v) for v in np.linspace(lo, hi, NGRID)] + [float(th[k])]))
        rows = []
        for v in grid:
            pv = en.predict({**th, k: v}, form)
            cost = 0.5 * float(np.sum((pv[tr] / Tm[tr] - 1.0) ** 2))
            pr = base[G][0].copy()
            pr[te] = pv[te]
            sc = scores_of(pr, base[G][1])
            scores = dict(stored_scores)
            pools = dict(stored_pools)
            scores[G] = sc['touched_no_twin']
            pools[G] = sc['pooled_LOEO_all']
            win, guard, final = rule3(scores, pools)
            rows.append({'value': v, 'train_cost': cost, 'fold_rms_pct': rms(list(pv[te] / Tm[te] - 1.0)),
                         'touched_no_twin': sc['touched_no_twin'], 'touched_with_twins': sc['touched_with_twins'],
                         'pooled_LOEO_all': sc['pooled_LOEO_all'], 'rule_winner': win, 'guard_pass': guard, 'decision': final,
                         'is_fold_value': v == float(th[k])})
        costs = [r['train_cost'] for r in rows]
        col = lambda q: [r[q] for r in rows]  # noqa: E731
        scans.append({'form': G, 'fold': fn, 'constant': k, 'fold_value': float(th[k]), 'bounds': [lo, hi], 'n_values': len(rows),
                      'other_flat_constants_same_fold': [x for x in by_fold[(G, fn)] if x != k],
                      'train_cost_span': max(costs) - min(costs), 'train_cost': min(costs),
                      'touched_no_twin_range': [min(col('touched_no_twin')), max(col('touched_no_twin'))],
                      'touched_with_twins_range': [min(col('touched_with_twins')), max(col('touched_with_twins'))],
                      'pooled_LOEO_all_range': [min(col('pooled_LOEO_all')), max(col('pooled_LOEO_all'))],
                      'decision_at_every_value': sorted(set(col('decision'))), 'rows': rows})

    # every combination of the flat constants' values across forms: G0 keeps the rule if no form can score lower than G0 by more than 0.25
    g0s, g0p = stored_scores['G0'], stored_pools['G0']
    lows = {}
    for s in scans:
        lows.setdefault(s['form'], []).append(s['touched_no_twin_range'][0])
    joint_ok = all(len(by_fold[(G, fn)]) == 1 for G, fn in by_fold)
    g0_every_combination = joint_ok and all(min(v) >= g0s - 0.25 for v in lows.values())
    rec = {'what': ("Item 3's constants checked for identification in every LOEO fold (post hoc, REPORTED; no fit; never deciding a rule): "
                    "each free constant moved alone to its bounds with the fold's other constants held; a constant with no effect on any "
                    "training point is flat in that fold, and item 3's scores are re-made over its bounds with every other fold as stored."),
           'by': BY, 'when': time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime()),
           'interpreter': '/usr/bin/python3 %s, numpy %s' % (sys.version.split()[0], np.__version__),
           'inputs': {'decisions_v31.json step3 (as fitted)': {k: s3[k] for k in ('winner', 'rule_winner', 'guard_pass', 'lowest_score')},
                      'fits_sha256': fits_sha, 'n_time_points': N},
           'replication_of_step3_scores': repl,
           'fold_checks': fold_checks,
           'screen': screen,
           'flat': scans,
           'G0_reference': {'touched_no_twin': g0s, 'pooled_LOEO_all': g0p, 'guard_bar': g0p + 0.05},
           'joint_reading': ('one flat constant per (form, fold): each form varies on its own line, so every combination of values is covered '
                             'by the per-form ranges' if joint_ok else 'more than one flat constant in a (form, fold): a joint scan is needed'),
           'decision_G0_at_every_combination': g0_every_combination,
           'secs': round(time.time() - t0, 1)}
    op = os.path.join(O, 'item3_flat_v31.json')
    json.dump(rec, open(op + '.tmp', 'w'), indent=1, sort_keys=True, default=float)
    os.replace(op + '.tmp', op)
    print('replication of step 3 scores equal:', {g: repl[g]['equal'] for g in repl})
    print('fold checks: worst pred_test rel diff', max(c['pred_test_max_rel_diff_vs_stored'] for c in fold_checks),
          'worst cost rel diff', max(abs(c['train_cost_remade'] / c['train_cost_stored'] - 1) for c in fold_checks))
    print('screen:', len(screen), 'entries;', sum(1 for s in screen if s.get('flat')), 'flat;', sum(1 for s in screen if 'pinned_at' in s), 'pinned')
    for s in scans:
        print(f"FLAT {s['form']} {s['fold']} {s['constant']} at {s['fold_value']:.4f}: cost span {s['train_cost_span']:.3g}; touched "
              f"{s['touched_no_twin_range'][0]:.3f}-{s['touched_no_twin_range'][1]:.3f}%; pooled {s['pooled_LOEO_all_range'][0]:.3f}-"
              f"{s['pooled_LOEO_all_range'][1]:.3f}%; decisions {s['decision_at_every_value']}")
    print('G0 reference', round(g0s, 3), round(g0p, 4), '; decision G0 at every combination:', g0_every_combination, '; secs', rec['secs'])
    if a.label:
        label(dpath, D, rec, op)


def label(dpath, D, rec, op):
    """the labels in decisions_v31.json's step3: new keys only"""
    s3 = D['steps']['step3']
    flat = rec['flat']
    flat_forms = sorted({s['form'] for s in flat})
    s3['identification_post_hoc'] = {
        'by': BY,
        'reading': ("post hoc, REPORTED; the decision is unchanged. A constant whose training predictions do not move at all over its declared "
                    "bounds in a fold has no sensitivity there: the fold's training cost is flat along it, so its fitted value, and every score "
                    "read from that fold's held-out predictions, is wherever the optimizer stopped (not identified)."),
        'flat_constants': [{'form': s['form'], 'fold': s['fold'], 'constant': s['constant'], 'fitted_value': s['fold_value'],
                            'train_cost_span_over_bounds': s['train_cost_span'], 'touched_no_twin_range_pct': s['touched_no_twin_range'],
                            'pooled_LOEO_all_range_pct': s['pooled_LOEO_all_range'], 'decision_at_every_value': s['decision_at_every_value']}
                           for s in flat],
        'decision_G0_at_every_combination': rec['decision_G0_at_every_combination'],
        'G0_reference': rec['G0_reference'],
        'source': 'out/item3_flat_v31.json (its sha256 in SHA256SUMS)',
        'note': ("The declared pin rule pins a constant only when its pin set is empty in a fold; here the set is not empty but its points do not "
                 "depend on the constant. A later declaration could pin any constant whose training Jacobian column is zero (verify-fit-v31).")}
    for G, r in s3['forms'].items():
        mine = [s for s in flat if s['form'] == G]
        if G == 'G0':
            r['scores_identified'] = True
            r['scores_identified_reading'] = 'G0 has no item 3 constant'
            continue
        if not mine:
            r['scores_identified'] = True
            r['scores_identified_reading'] = 'no flat constant in any LOEO fold (out/item3_flat_v31.json)'
            continue
        lo_t = min(s['touched_no_twin_range'][0] for s in mine)
        hi_t = max(s['touched_no_twin_range'][1] for s in mine)
        lo_w = min(s['touched_with_twins_range'][0] for s in mine)
        hi_w = max(s['touched_with_twins_range'][1] for s in mine)
        lo_p = min(s['pooled_LOEO_all_range'][0] for s in mine)
        hi_p = max(s['pooled_LOEO_all_range'][1] for s in mine)
        where = '; '.join(f"{s['constant']} in {s['fold']} (fitted {s['fold_value']:.5g}, flat over [{s['bounds'][0]:g}, {s['bounds'][1]:g}])" for s in mine)
        r['scores_identified'] = False
        r['scores_identified_reading'] = (f"unidentified (a flat direction in a fold, post hoc): score_touched_no_twin, score_touched_with_twins and "
                                          f"pooled_LOEO_all read {where}, where the fold's training cost does not change; over the bounds the touched "
                                          f"score (no twin) spans {lo_t:.2f}-{hi_t:.2f}% and the pooled LOEO {lo_p:.3f}-{hi_p:.3f}%; the decision G0 "
                                          f"holds at every value (REPORTED; {BY}; out/item3_flat_v31.json)")
        r['score_touched_no_twin_range_post_hoc'] = [lo_t, hi_t]
        r['score_touched_with_twins_range_post_hoc'] = [lo_w, hi_w]
        r['pooled_LOEO_all_range_post_hoc'] = [lo_p, hi_p]
    json.dump(D, open(dpath + '.tmp', 'w'), indent=1, sort_keys=True, default=float)
    os.replace(dpath + '.tmp', dpath)
    print('labels written to', os.path.basename(dpath), 'for', flat_forms)


if __name__ == '__main__':
    main()
