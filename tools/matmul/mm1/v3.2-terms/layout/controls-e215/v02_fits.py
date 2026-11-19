#!/usr/bin/env python3
"""verify-lay v02 (round Q225, track C): this lane's OWN two-stage fits of the layout term on MM1-v3.1's committed fold records, with this
lane's OWN features (work/v01_map.json), and the adversarial checks: alternative explanations (functions of the shire count n alone,
of R and C, of the shape-and-n average of the feature), within-n and within-(n, arm) permutation placebos, a placebo of the WHOLE declared
selection (seven forms and the keep rule), bootstraps of the held-out gains, the gain by card, clock and experiment, the L3-capacity
sensitivity, and the E215 factors re-made from this lane's features. Desk; post hoc; held out where it says; nothing blind.

Imports only MM1-v3.1 as landed (fit_v31 for its points, folds, rung mask and lolo_class; time_v31.Engine31 for each fold's base).
Reads the lane's land only for (a) its link and fan-out features (the selection placebo needs the seven declared forms), (b) its
forecast CSV (the comparison target). No E215 datum: E215's registered point list and MM1-v3.1's frozen E215 forecasts only.
/usr/bin/python3 3.12.3 -I -B, numpy, single-threaded. Output: work/v02_fits.json (and work/v02_bases.npz, a cache of the fold bases)."""
import collections
import csv
import json
import os
import re
import sys
import time

import numpy as np

LAB = os.environ.get('ET_LAB') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *['..'] * 6))  # land-terms: the lab's top (was this box's clone path)
V31 = os.path.join(LAB, 'tools/matmul/mm1/v3.1')
ME = os.path.dirname(os.path.abspath(__file__))  # land-terms: this folder (was verify-lay's lane folder); reads and writes ME/work/
LANE = os.path.dirname(ME)  # land-terms: the layout folder above, lay-contention's land byte for byte (was its land path)
sys.path.insert(0, V31)
import fit_v31 as FV  # noqa: E402

FULL = 0xFFFFFFFF
SHAPE = re.compile(r'^gemmL(\d+)x(\d+)x(\d+)$')
NPERM = 1000
NBOOT = 10000
SING = [0]


def key_of(arm, mask):
    MB, NB, KB = (int(x) for x in SHAPE.match(arm).groups())
    return 'rgm136.gemmL|%dx%dx%d|0x%x' % (MB, NB, KB, mask)


def rms(e):
    e = np.asarray(e, float)
    return float(100.0 * np.sqrt(np.mean(e ** 2))) if len(e) else float('nan')


def main():
    t0 = time.time()
    rec = json.load(open(os.path.join(V31, 'out/fits/time_T5r+G0+n32.json')))
    P = FV.DV.time_points()
    ids = [p['id'] for p in P]
    assert ids == rec['ids']
    form, free = FV.parse_form_name(rec['form_name'])
    N = len(P)
    Tm = np.array([p['T'] for p in P], float)
    rung = FV.rung_mask(P)
    rows = {r['id']: r for r in csv.DictReader(open(os.path.join(V31, 'out/points_time_v31.csv')))}
    twin = np.array([rows[i]['twin_LOEO'] == '1' for i in ids])
    masks = np.array([int(p['mask'], 16) for p in P], dtype=np.int64)
    sub = masks != FULL
    loeo_names = [f for f in rec['folds'] if f.startswith('LOEO E') and len(f.split()) == 2]
    lolo_names = ['LOLO compact', 'LOLO spread', 'LOLO other']
    loco_names = [f for f in rec['folds'] if f.startswith('LOCO ')]
    names = loeo_names + lolo_names + loco_names
    # ---------------------------------------------------------------- the fold bases (Engine31 at each fold's stored constants)
    cache = os.path.join(ME, 'work/v02_bases.npz')
    checks = {}
    if os.path.exists(cache):
        Z = np.load(cache)
        base_all = Z['base_all']
        bases = {nm: Z['b_' + str(i)] for i, nm in enumerate(names)}
        base_b_compact = Z['b_compact_eta0']
        checks = json.load(open(cache + '.checks.json'))
    else:
        en = FV.TV.Engine31(P)
        base_all = en.predict(rec['theta_all'], form)
        checks['all'] = float(np.max(np.abs(base_all / np.array(rec['pred_all']) - 1)))
        bases = {}
        for nm in names:
            fr = rec['folds'][nm]
            b = en.predict(fr['theta'], form)
            te = np.array(fr['test_idx'])
            checks[nm] = float(np.max(np.abs(b[te] / np.array(fr['pred_test']) - 1)))
            bases[nm] = b
            print(f'  base {nm}: check {checks[nm]:.2e} ({time.time() - t0:.0f} s)', flush=True)
        th0 = dict(rec['folds']['LOLO compact']['theta'])
        th0['eta'] = 0.0
        base_b_compact = en.predict(th0, form)
        np.savez(cache, base_all=base_all, b_compact_eta0=base_b_compact, **{'b_' + str(i): bases[nm] for i, nm in enumerate(names)})
        json.dump(checks, open(cache + '.checks.json', 'w'))
    print('bases ready; worst check', max(checks.values()), flush=True)
    test = {nm: np.array(rec['folds'][nm]['test_idx']) for nm in names}
    # ---------------------------------------------------------------- features (this lane's v01)
    V1 = json.load(open(os.path.join(ME, 'work/v01_map.json')))['configs']
    lanef = json.load(open(os.path.join(LANE, 'out/features_layout.json')))
    F = collections.OrderedDict()
    cols = ['fresh32', 'fresh16', 'fresh24', 'fresh48', 'fresh64', 'distinct', 'G1', 'F3', 'N1', 'N2', 'N3', 'N4', 'Rf', 'Cf',
            'link', 'fan']
    for c in cols:
        F[c] = np.zeros(N)
    nn = np.zeros(N, int)
    RR = np.zeros(N, int)
    CC = np.zeros(N, int)
    for j, p in enumerate(P):
        if not sub[j]:
            continue
        k = key_of(p['arm'], masks[j])
        kf = key_of(p['arm'], FULL)
        f, g = V1[k], V1[kf]
        n, R, C = f['n'], f['R'], f['C']
        nn[j], RR[j], CC[j] = n, R, C
        for cap in (16, 24, 32, 48, 64):
            F['fresh%d' % cap][j] = f['fresh_lines_step'][str(cap)] / f['req_lines_step'] - g['fresh_lines_step'][str(cap)] / g['req_lines_step']
        F['distinct'][j] = f['distinct_lines_step'] / f['req_lines_step'] - g['distinct_lines_step'] / g['req_lines_step']
        F['G1'][j] = (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1
        F['F3'][j] = (110 + 12 * f['hop_max']) / (110 + 12 * g['hop_max']) - 1
        F['N1'][j] = 1 - n / 32.0
        F['N2'][j] = (1 - n / 32.0) ** 2
        F['N3'][j] = 32.0 / n - 1
        F['N4'][j] = np.log2(32.0 / n)
        F['Rf'][j] = 1 - R / 8.0
        F['Cf'][j] = 1 - C / 4.0
        lf, lg = lanef[k], lanef[kf]
        F['link'][j] = lf['mesh_link_max_lines'] / lg['mesh_link_max_lines'] - n / 32.0
        F['fan'][j] = lf['fanw'] / n - lg['fanw'] / 32.0
    # layout-averaged versions of fresh32: the mean within n, and within (n, arm)
    S = np.where(sub)[0]
    arm = np.array([p['arm'] for p in P])
    for nmx, grpf in (('fresh32_bar_n', lambda j: nn[j]), ('fresh32_bar_narm', lambda j: (nn[j], arm[j]))):
        g = collections.defaultdict(list)
        for j in S:
            g[grpf(j)].append(j)
        v = np.zeros(N)
        for gg, js in g.items():
            v[js] = np.mean(F['fresh32'][js])
        F[nmx] = v
    F['fresh32_minus_bar_n'] = F['fresh32'] - F['fresh32_bar_n']
    # ---------------------------------------------------------------- the machinery
    lclass = np.array([FV.lolo_class(p['mask']) or '' for p in P])
    ALL = np.arange(N)
    fold_tr_sub = {}
    for nm in names:
        tm = np.zeros(N, bool)
        tm[test[nm]] = True
        fold_tr_sub[nm] = ALL[(~tm) & (~rung) & sub]
    tr_all_sub = ALL[(~rung) & sub]
    loeo_nt = np.zeros(N, bool)
    for nm in loeo_names:
        loeo_nt[test[nm]] = True
    loeo_nt &= ~twin
    lolo_m = np.zeros(N, bool)
    for nm in lolo_names:
        lolo_m[test[nm]] = True
    lolo_m &= sub
    loco_m = np.zeros(N, bool)
    for nm in loco_names:
        loco_m[test[nm]] = True
    # pairs (the lane's definition, re-written)
    grp = collections.defaultdict(list)
    for j in S:
        p = P[j]
        if p['exp'] in ('E212', 'E213'):
            grp[(p['card'], p['kernel'], p['arm'], p['fmt'], int(round(p['f'] / 25.0)), nn[j])].append(j)
    pairs = []
    for g, idx in grp.items():
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                i, k = idx[x], idx[y]
                if masks[i] == masks[k]:
                    continue
                d = np.log(Tm[i] / Tm[k])
                if abs(d) > 0.01:
                    pairs.append((i, k, d))

    def pair_score(pred):
        ok = ties = 0
        for i, k, d in pairs:
            s = np.sign(np.log(pred[i] / pred[k]))
            ok += int(s == np.sign(d))
            ties += int(s == 0)
        return ok, ties

    def solve(Xs, y):
        A = Xs.T @ Xs
        if np.allclose(A, 0):
            return np.zeros(Xs.shape[1])
        try:
            return np.linalg.solve(A, Xs.T @ y)
        except np.linalg.LinAlgError:
            SING[0] += 1
            return np.linalg.lstsq(Xs, y, rcond=None)[0]

    def evaluate(M, want_pairs=True, want_err=False):
        """M: (N, k) feature matrix (zero off subset points). Two-stage per fold; returns the metrics"""
        M = np.asarray(M, float)
        if M.ndim == 1:
            M = M[:, None]
        heldL = np.full(N, np.nan)
        heldLa = np.full(N, np.nan)
        heldLb = np.full(N, np.nan)
        heldC = np.full(N, np.nan)
        consts = {}
        clip_bind = 0
        for nm in names:
            b = bases[nm]
            tr = fold_tr_sub[nm]
            r = b[tr] / Tm[tr]
            a = solve(r[:, None] * M[tr], 1.0 - r)
            consts[nm] = a.tolist()
            te = test[nm]
            g = 1.0 + M[te] @ a
            clip_bind += int(np.sum((g < 0.3) | (g > 3.0)))
            pr = b[te] * np.clip(g, 0.3, 3.0)
            if nm in loeo_names:
                heldL[te] = pr
            elif nm in lolo_names:
                heldLa[te] = pr
                bb = base_b_compact if nm == 'LOLO compact' else b
                heldLb[te] = bb[te] * np.clip(g, 0.3, 3.0)
            else:
                heldC[te] = pr
        r = base_all[tr_all_sub] / Tm[tr_all_sub]
        a_all = solve(r[:, None] * M[tr_all_sub], 1.0 - r)
        ins = base_all * np.clip(1.0 + M @ a_all, 0.3, 3.0)
        eL = heldL[loeo_nt] / Tm[loeo_nt] - 1
        esub = heldL[loeo_nt & sub] / Tm[loeo_nt & sub] - 1
        ea = heldLa[lolo_m] / Tm[lolo_m] - 1
        eb = heldLb[lolo_m] / Tm[lolo_m] - 1
        ec = heldC[loco_m] / Tm[loco_m] - 1
        out = {'a_all': a_all.tolist(), 'LOEO_nt': rms(eL), 'LOEO_sub_nt': rms(esub), 'LOLO_a': rms(ea), 'LOLO_b': rms(eb),
               'LOLO_b_by_class': {c: rms(heldLb[lolo_m & (lclass == c)] / Tm[lolo_m & (lclass == c)] - 1) for c in ('compact', 'spread', 'other')},
               'LOCO': rms(ec), 'in_sample_sub': rms(ins[sub] / Tm[sub] - 1), 'clip_binds': clip_bind,
               'n': {'LOEO_nt': int(loeo_nt.sum()), 'LOEO_sub_nt': int((loeo_nt & sub).sum()), 'LOLO': int(lolo_m.sum()), 'LOCO': int(loco_m.sum())}}
        if want_pairs:
            out['pairs_in_sample'], out['pairs_in_sample_ties'] = pair_score(ins)
            out['pairs_LOEO'], out['pairs_LOEO_ties'] = pair_score(heldL)
            out['pairs_n'] = len(pairs)
        if want_err:
            out['_heldL'], out['_heldLb'], out['_ins'], out['_consts'] = heldL, heldLb, ins, consts
        return out

    res = {'n_points': N, 'n_subset': int(sub.sum()), 'n_pairs': len(pairs), 'base_checks_worst': max(checks.values())}
    Z0 = np.zeros(N)
    base = evaluate(Z0, want_err=True)
    res['base'] = {k: v for k, v in base.items() if not k.startswith('_')}
    print('base', res['base'], flush=True)
    forms = collections.OrderedDict()
    for c in ['fresh32', 'fresh16', 'fresh24', 'fresh48', 'fresh64', 'distinct', 'G1', 'F3', 'N1', 'N2', 'N3', 'N4', 'Rf', 'Cf',
              'fresh32_bar_n', 'fresh32_bar_narm', 'fresh32_minus_bar_n', 'link', 'fan']:
        forms[c] = [c]
    forms['fresh32+N1'] = ['fresh32', 'N1']
    forms['fresh32+N4'] = ['fresh32', 'N4']
    forms['fresh32+fan'] = ['fresh32', 'fan']
    forms['fresh32+link'] = ['fresh32', 'link']
    forms['fresh32+F3'] = ['fresh32', 'F3']
    forms['G1+N1'] = ['G1', 'N1']
    forms['N1+N2'] = ['N1', 'N2']
    forms['Rf+Cf'] = ['Rf', 'Cf']
    full_eval = {}
    for nm, cs in forms.items():
        M = np.stack([F[c] for c in cs], axis=1)
        full_eval[nm] = evaluate(M, want_err=(nm == 'fresh32'))
        x = full_eval[nm]
        print(f"  {nm:22s} a={['%+.4f' % v for v in x['a_all']]} LOEO {x['LOEO_nt']:.4f} sub {x['LOEO_sub_nt']:.4f} LOLO(a) {x['LOLO_a']:.3f} "
              f"LOLO(b) {x['LOLO_b']:.4f} {x['LOLO_b_by_class']} LOCO {x['LOCO']:.4f} pairs {x['pairs_in_sample']}/{x['pairs_LOEO']} "
              f"(ties {x['pairs_in_sample_ties']}/{x['pairs_LOEO_ties']}) clip {x['clip_binds']}", flush=True)
    res['forms'] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('_')} for k, v in full_eval.items()}
    f1 = full_eval['fresh32']
    # ---------------------------------------------------------------- the declared keep rule on this lane's numbers
    b0 = res['base']
    keep = {}
    for nm in forms:
        x = full_eval[nm]
        keep[nm] = {'c1_LOLOb_lower': x['LOLO_b'] < b0['LOLO_b'], 'c2_LOLOa_not_higher': x['LOLO_a'] <= b0['LOLO_a'],
                    'c3_LOEO_le_4.72': x['LOEO_nt'] <= 4.72, 'c3_LOEO_le_v31': x['LOEO_nt'] <= b0['LOEO_nt']}
    res['keep_rule'] = keep
    # ---------------------------------------------------------------- bootstraps (paired, held-out points resampled; constants fixed)
    rng = np.random.default_rng(424242)
    eb0 = base['_heldLb'][lolo_m] / Tm[lolo_m] - 1
    eb1 = f1['_heldLb'][lolo_m] / Tm[lolo_m] - 1
    el0 = base['_heldL'][loeo_nt] / Tm[loeo_nt] - 1
    el1 = f1['_heldL'][loeo_nt] / Tm[loeo_nt] - 1
    def boot(e0, e1):
        n = len(e0)
        d = np.empty(NBOOT)
        for i in range(NBOOT):
            ix = rng.integers(0, n, n)
            d[i] = rms(e1[ix]) - rms(e0[ix])
        return {'delta': rms(e1) - rms(e0), 'ci95': [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
                'share_boot_delta_ge_0': float(np.mean(d >= 0)), 'n': n,
                'points_better': int(np.sum(np.abs(e1) < np.abs(e0))), 'points_worse': int(np.sum(np.abs(e1) > np.abs(e0))),
                'points_equal': int(np.sum(np.abs(e1) == np.abs(e0)))}
    res['boot_LOLO_b'] = boot(eb0, eb1)
    res['boot_LOEO_nt'] = boot(el0, el1)
    es0 = base['_heldL'][loeo_nt & sub] / Tm[loeo_nt & sub] - 1
    es1 = f1['_heldL'][loeo_nt & sub] / Tm[loeo_nt & sub] - 1
    res['boot_LOEO_sub_nt'] = boot(es0, es1)
    # the gain by experiment, card and class (sum of squared held-out errors, LOLO (b))
    idx = np.where(lolo_m)[0]
    by = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for j, x0, x1 in zip(idx, eb0, eb1):
        for kk in (('exp', P[j]['exp']), ('card', P[j]['card']), ('class', lclass[j]), ('n', int(nn[j]))):
            v = by[kk]
            v[0] += 1
            v[1] += x0 ** 2
            v[2] += x1 ** 2
    res['LOLO_b_by_group'] = {'%s=%s' % k: {'n': v[0], 'rms_v31': float(100 * np.sqrt(v[1] / v[0])), 'rms_F1': float(100 * np.sqrt(v[2] / v[0])),
                                            'sse_change_share_of_total': None, 'sse_change': float(v[2] - v[1])} for k, v in sorted(by.items(), key=lambda t: str(t[0]))}
    tot = float(np.sum(eb1 ** 2) - np.sum(eb0 ** 2))
    for v in res['LOLO_b_by_group'].values():
        v['sse_change_share_of_total'] = v['sse_change'] / tot if tot else None
    res['LOLO_b_total_sse_change'] = tot
    # ---------------------------------------------------------------- the constant by clock group / card (all-data base, two-stage)
    clk = {}
    for nmg, sel in (('600 MHz cards (aifoundry3 c0, aifoundry1 c1)', lambda p: p['f'] < 700),
                     ('800 MHz cards (aifoundry2 c0, aifoundry1 c0)', lambda p: p['f'] >= 700)):
        js = np.array([j for j in tr_all_sub if sel(P[j])])
        r = base_all[js] / Tm[js]
        a = solve(r[:, None] * F['fresh32'][js][:, None], 1 - r)
        clk[nmg] = {'n': int(len(js)), 'a_fresh32': float(a[0]), 'in_sample_rms_v31': rms(r - 1),
                    'in_sample_rms_F1': rms(r * (1 + a[0] * F['fresh32'][js]) - 1)}
    for c in sorted({P[j]['card'] for j in tr_all_sub}):
        js = np.array([j for j in tr_all_sub if P[j]['card'] == c])
        r = base_all[js] / Tm[js]
        a = solve(r[:, None] * F['fresh32'][js][:, None], 1 - r)
        clk['card ' + c] = {'n': int(len(js)), 'a_fresh32': float(a[0]), 'in_sample_rms_v31': rms(r - 1),
                            'in_sample_rms_F1': rms(r * (1 + a[0] * F['fresh32'][js]) - 1)}
    for e in sorted({P[j]['exp'] for j in tr_all_sub}):
        js = np.array([j for j in tr_all_sub if P[j]['exp'] == e])
        r = base_all[js] / Tm[js]
        a = solve(r[:, None] * F['fresh32'][js][:, None], 1 - r)
        clk['exp ' + e] = {'n': int(len(js)), 'a_fresh32': float(a[0]), 'in_sample_rms_v31': rms(r - 1),
                           'in_sample_rms_F1': rms(r * (1 + a[0] * F['fresh32'][js]) - 1)}
    res['constant_by_group'] = clk
    # correlations among the subset points' features
    cor = {}
    for c in ['N1', 'N2', 'N3', 'N4', 'Rf', 'Cf', 'distinct', 'G1', 'F3', 'fresh32_bar_n', 'fresh32_bar_narm', 'link', 'fan']:
        cor[c] = float(np.corrcoef(F['fresh32'][S], F[c][S])[0, 1])
    res['corr_fresh32_with'] = cor
    # in-sample residual correlation with f and with the feature, by clock group
    rr = base_all[S] / Tm[S] - 1
    res['subset_resid_v31_corr'] = {'with_fresh32': float(np.corrcoef(rr, F['fresh32'][S])[0, 1]),
                                    'with_f_MHz': float(np.corrcoef(rr, np.array([P[j]['f'] for j in S]))[0, 1]),
                                    'with_N1': float(np.corrcoef(rr, F['N1'][S])[0, 1])}
    # ---------------------------------------------------------------- placebos for F1 (LOLO (b) and LOEO no twins)
    real_b = f1['LOLO_b']
    real_l = f1['LOEO_nt']
    def perm_within(groupf, seed0):
        g = collections.defaultdict(list)
        for j in S:
            g[groupf(j)].append(j)
        outb, outl = [], []
        movable = sum(len(v) for v in g.values() if len(v) > 1 and len(set(np.round(F['fresh32'][v], 12))) > 1)
        for i in range(NPERM):
            rg = np.random.default_rng(seed0 + i)
            v = F['fresh32'].copy()
            for js in g.values():
                if len(js) > 1:
                    v[js] = F['fresh32'][np.array(js)[rg.permutation(len(js))]]
            x = evaluate(v, want_pairs=False)
            outb.append(x['LOLO_b'])
            outl.append(x['LOEO_nt'])
        outb, outl = np.array(outb), np.array(outl)
        return {'n_perm': NPERM, 'points_in_movable_groups': int(movable), 'n_groups': len(g),
                'placebo_LOLO_b_median': float(np.median(outb)), 'placebo_LOLO_b_p05': float(np.percentile(outb, 5)),
                'real_F1_LOLO_b': real_b, 'share_placebo_LOLO_b_le_real': float(np.mean(outb <= real_b)),
                'placebo_LOEO_median': float(np.median(outl)), 'share_placebo_LOEO_le_real': float(np.mean(outl <= real_l))}
    tp = time.time()
    res['placebo_global'] = perm_within(lambda j: 0, 10_000)
    print('placebo global', res['placebo_global'], f'({time.time() - tp:.0f} s)', flush=True)
    res['placebo_within_n'] = perm_within(lambda j: int(nn[j]), 20_000)
    print('placebo within n', res['placebo_within_n'], flush=True)
    res['placebo_within_n_arm'] = perm_within(lambda j: (int(nn[j]), arm[j]), 30_000)
    print('placebo within (n, arm)', res['placebo_within_n_arm'], flush=True)
    res['placebo_within_n_exp'] = perm_within(lambda j: (int(nn[j]), P[j]['exp']), 40_000)
    print('placebo within (n, exp)', res['placebo_within_n_exp'], flush=True)
    # ---------------------------------------------------------------- the whole declared selection, under a joint permutation
    DECL = {'F1': ['fresh32'], 'F2': ['link'], 'F3': ['F3'], 'F4': ['fan'], 'F5': ['fresh32', 'fan'], 'F6': ['fresh32', 'link'],
            'F7': ['fresh32', 'F3']}
    def rule(FF):
        ev = {}
        for fm, cs in DECL.items():
            ev[fm] = evaluate(np.stack([FF[c] for c in cs], axis=1), want_pairs=False)
        kept = [fm for fm in DECL if ev[fm]['LOLO_b'] < b0['LOLO_b'] and ev[fm]['LOLO_a'] <= b0['LOLO_a'] and ev[fm]['LOEO_nt'] <= 4.72]
        if not kept:
            return None, None, ev
        lo = min(ev[fm]['LOLO_b'] for fm in kept)
        near = sorted([fm for fm in kept if ev[fm]['LOLO_b'] <= lo + 0.10], key=lambda fm: (len(DECL[fm]), ev[fm]['LOEO_nt'], fm))
        return near[0], ev[near[0]]['LOLO_b'], ev
    w_real, b_real, ev_real = rule(F)
    res['declared_rule_this_lane'] = {'winner': w_real, 'winner_LOLO_b': b_real,
                                      'forms': {fm: {k: ev_real[fm][k] for k in ('a_all', 'LOEO_nt', 'LOLO_a', 'LOLO_b')} for fm in DECL}}
    print('declared rule here:', w_real, b_real, flush=True)
    NSEL = 300
    sel = []
    nowin = 0
    for i in range(NSEL):
        rg = np.random.default_rng(50_000 + i)
        perm = S[rg.permutation(len(S))]
        FF = {c: F[c].copy() for c in ('fresh32', 'link', 'F3', 'fan')}
        for c in FF:
            FF[c][S] = F[c][perm]
        w, bb, _ = rule(FF)
        if w is None:
            nowin += 1
        else:
            sel.append(bb)
    sel = np.array(sel)
    res['placebo_selection'] = {'n_perm': NSEL, 'no_form_kept': nowin, 'winner_LOLO_b_median': float(np.median(sel)) if len(sel) else None,
                                'share_with_winner_LOLO_b_le_real': float(np.sum(sel <= b_real) / NSEL) if b_real else None,
                                'real_winner': w_real, 'real_winner_LOLO_b': b_real}
    print('selection placebo', res['placebo_selection'], f'({time.time() - tp:.0f} s)', flush=True)
    # ---------------------------------------------------------------- E215: the frozen factors from this lane's own features
    a1 = f1['a_all'][0]
    lane_rows = list(csv.DictReader(open(os.path.join(LANE, 'forecast-e215-v31-layout.csv'))))
    reg = {r['id']: r for r in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv')))}
    v31f = {}
    for fn in ('tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv',):
        for r in csv.DictReader(open(os.path.join(LAB, fn))):
            v31f[r['token']] = float(r['v31_cycles_wall'])
    e215 = []
    worst_phi = worst_fac = worst_v31c = 0.0
    full_nonunit = 0
    aG1 = full_eval['G1']['a_all'][0]
    worst_g1 = 0.0
    for r in lane_rows:
        rg_ = reg[r['id']]
        m = int(rg_['shire_mask'], 16)
        if m == FULL:
            phi = 0.0
            g1 = 0.0
        else:
            k = key_of(rg_['arm_token'], m)
            kf = key_of(rg_['arm_token'], FULL)
            f, g = V1[k], V1[kf]
            phi = f['fresh_lines_step']['32'] / f['req_lines_step'] - g['fresh_lines_step']['32'] / g['req_lines_step']
            g1 = (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1
        fac = 1 + a1 * phi
        v31 = float(r['v31_cycles_per_op_wall'])
        mine = v31 * fac
        if m == FULL and float(r['layout_factor']) != 1.0:
            full_nonunit += 1
        worst_phi = max(worst_phi, abs(phi - float(r['phi_fresh'])))
        worst_fac = max(worst_fac, abs(fac / float(r['layout_factor']) - 1))
        worst_v31c = max(worst_v31c, abs(mine / float(r['v31c_cycles_per_op_wall']) - 1))
        g1c = v31 * (1 + aG1 * g1)
        if r.get('REPORTED_G1_cycles_per_op_wall'):
            worst_g1 = max(worst_g1, abs(g1c / float(r['REPORTED_G1_cycles_per_op_wall']) - 1))
        e215.append({'id': r['id'], 'mask': rg_['shire_mask'], 'arm': rg_['arm_token'], 'phi_mine': phi, 'phi_lane': float(r['phi_fresh']),
                     'factor_mine': fac, 'factor_lane': float(r['layout_factor']), 'g1_mine': g1})
    subphi = [x['phi_mine'] for x in e215 if x['mask'].lower() != '0xffffffff']
    res['e215'] = {'a_fresh32_all_data_this_lane': a1, 'a_lane': -0.08316593007433395, 'a_rel_diff': abs(a1 / -0.08316593007433395 - 1),
                   'rows': len(e215), 'full_rows_nonunit_factor_in_lane_csv': full_nonunit, 'worst_abs_phi_diff': worst_phi,
                   'worst_rel_factor_diff': worst_fac, 'worst_rel_v31c_diff_4dp': worst_v31c, 'worst_rel_G1_col_diff': worst_g1,
                   'aG1_this_lane': aG1, 'subset_phi_range_e215': [min(subphi), max(subphi)],
                   'subset_phi_range_fit': [float(F['fresh32'][S].min()), float(F['fresh32'][S].max())],
                   'rows_detail': e215}
    print('E215', {k: v for k, v in res['e215'].items() if k != 'rows_detail'}, flush=True)
    # REPORTED desk control columns for E215's subset rows (made here before any E215 datum; never frozen by this lane)
    ctrl_forms = ['N3', 'N1+N2', 'G1', 'G1+N1', 'fresh24']
    def feat_row(arm_token, m):
        if m == FULL:
            return {c: 0.0 for c in cols}
        k = key_of(arm_token, m)
        kf = key_of(arm_token, FULL)
        f, g = V1[k], V1[kf]
        n = f['n']
        return {'fresh32': f['fresh_lines_step']['32'] / f['req_lines_step'] - g['fresh_lines_step']['32'] / g['req_lines_step'],
                'fresh24': f['fresh_lines_step']['24'] / f['req_lines_step'] - g['fresh_lines_step']['24'] / g['req_lines_step'],
                'G1': (110 + 12 * f['hop_mean']) / (110 + 12 * g['hop_mean']) - 1, 'N1': 1 - n / 32.0, 'N2': (1 - n / 32.0) ** 2,
                'N3': 32.0 / n - 1}
    ctrl = []
    for r in lane_rows:
        rg_ = reg[r['id']]
        m = int(rg_['shire_mask'], 16)
        fr_ = feat_row(rg_['arm_token'], m)
        v31 = float(r['v31_cycles_per_op_wall'])
        row = {'id': r['id'], 'mask': rg_['shire_mask'], 'arm': rg_['arm_token'], 'v31_cycles_per_op_wall': v31,
               'F1_frozen_cycles_per_op_wall': float(r['v31c_cycles_per_op_wall'])}
        for fm in ctrl_forms:
            cs = forms[fm]
            a = full_eval[fm]['a_all']
            row[fm] = v31 * (1.0 + sum(ai * fr_.get(c, 0.0) for ai, c in zip(a, cs)))
        ctrl.append(row)
    res['e215_control_columns'] = {'forms': {fm: {'features': forms[fm], 'a_all': full_eval[fm]['a_all']} for fm in ctrl_forms},
                                   'made_at': time.strftime('%Y-%m-%d %H:%M:%S %Z'), 'rows': ctrl}
    with open(os.path.join(ME, 'work/v02_e215_controls.csv'), 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['id', 'mask', 'arm', 'v31_cycles_per_op_wall', 'F1_frozen_cycles_per_op_wall'] + ['REPORTED_%s_cycles_per_op_wall' % fm for fm in ctrl_forms])
        for row in ctrl:
            w.writerow([row['id'], row['mask'], row['arm'], '%.4f' % row['v31_cycles_per_op_wall'], '%.4f' % row['F1_frozen_cycles_per_op_wall']] + ['%.4f' % row[fm] for fm in ctrl_forms])
    res['singular_fallbacks'] = SING[0]
    res['secs'] = round(time.time() - t0, 1)
    json.dump(res, open(os.path.join(ME, 'work/v02_fits.json'), 'w'), indent=1, default=float)
    print('done', res['secs'], 's')


if __name__ == '__main__':
    main()
