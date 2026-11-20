#!/usr/bin/env python3
"""MM1-v3.2's layout-term rule (DECLARED-v32.md section 3, item L), frozen as code before any fit of MM1-v3.2 and before any E215 result
was opened. Desk; numpy only; single-threaded. /usr/bin/python3 3.12.3, numpy 1.26.4, run as `-I -B`.

It decides AT MOST ONE layout time term for MM1-v3.2 from the frozen candidates {none, N3, N1+N2, G1, G1+N1, F1, fresh24}, each in the
form verify-lay's v02_fits.py and lay-contention's eval_layout.py score it (tools/matmul/mm1/v3.2-terms/layout/ and its controls-e215/):

    T = T_base(fold) x clip(1 + sum_i a_i x_i, 0.3, 3.0),    every x_i = 0 at the full mask (0xffffffff)

with the a_i the linear least-squares solution of the fold's training residuals (forecast / measured - 1) over its training subset
points of rgm136's gemmL loop (E146's store rungs out): the two-stage fit (the base's constants are not refitted with the term). The
features x_i (desk, from committed code; DECLARED-v32.md section 3 names the makers):
    N3 = 32/n - 1;  N1 = 1 - n/32;  N2 = (1 - n/32)^2;  G1 = (110 + 12 h_mean(mask)) / (110 + 12 h_mean(full)) - 1;
    fresh<C> = the walk's strict-LRU (C MB L3, C stores allocating) DRAM lines a step over the line requests a step, minus the full chip's.
F1 is fresh32; fresh24 is fresh24; fresh48 enters only the L3-convention check (v).

THE BUNDLE (an .npz the fit lane writes from MM1-v3.2's own fits; every array over the N time points in the fit's order):
    T (float, us an op), sub (bool: a subset point of rgm136 gemmL), twin (bool: a configuration twin in its LOEO fold), rung (bool:
    E146's store rungs), card (str), lolo (str: 'compact' / 'spread' / 'other', '' at the full chip), feat_N3, feat_N1, feat_N2,
    feat_G1, feat_fresh24, feat_fresh32, feat_fresh48 (float, 0 off the subset points), base_all (float: the all-data base), arm (str:
    the arm token, read only by the REPORTED label check);
    fold_names (str, every fold below), and for each fold k: base_k (float, the fold's base over every point), test_k (int indices).
    Folds: every main LOEO fold ('LOEO E105' ... 'LOEO E215': the experiment folds, not their card or arm sub-folds), the three LOLO
    folds ('LOLO compact', 'LOLO spread', 'LOLO other'; eta pinned at 0 where no training point carries the row imbalance:
    DECLARED-v32.md section 2) and the four LOCO folds ('LOCO <card>').

THE RULE (registered; DECLARED-v32.md section 3):
  metrics per candidate c: LOEO_nt (pooled rms over every point a main LOEO fold holds out, twins excluded), LOLO (rms over every subset
  point, each scored by its class's LOLO fold), LOCO_sub[card] (rms over the card's subset points in its LOCO fold), the constants of
  every LOCO fold, the all-data constants.
  eligibility of c (every condition):
   (i)   LOLO_c <= LOLO_none - 0.20 (points of rms);
   (ii)  the paired bootstrap of the LOLO points (10,000 resamples, numpy.random.default_rng(20261121).integers(0, n, (10000, n)), the
         same index matrix for every candidate): the 97.5th percentile of rms_c - rms_none is below 0;
   (iii) LOEO_nt_c <= LOEO_nt_none + 0.02;
   (iv)  the card dependence (verify-lay's finding 5): LOCO_sub_c[k] <= LOCO_sub_none[k] + 0.30 for every card k with a subset point, and
         each constant of c has one strict sign in all four LOCO folds;
   (v)   the L3 conventions (verify-lay's finding 4), for F1 and fresh24 only: the all-data constant of the one-feature form fresh24,
         fresh32 and fresh48 has one strict sign at all three capacities.
  choice: among the eligible, the lowest LOLO; within 0.10 points of it, the fewest constants, then the lower LOEO_nt, then the order
         N3, N1+N2, G1, G1+N1, F1, fresh24. No eligible candidate: 'none'.
  the selection placebo: for i in 0..999 the subset points' feature rows are permuted jointly (one permutation,
         numpy.random.default_rng(20261122 + i).permutation(n_sub), applied to every feature column alike) and the eligibility and
         choice are re-run unchanged; d_i = LOLO(winner_i) - LOLO_none (0 with no winner). p_sel = (1 + #{d_i <= d_obs}) / 1001.
         **The winner enters MM1-v3.2 only if p_sel <= 0.05**; else 'none'.
  labels (REPORTED, never deciding): N3 and N1+N2 are 'shire-count corrections'; a placement candidate (G1, G1+N1, F1, fresh24) that
         wins is labelled a placement term only if its LOLO is below that of at least 950 of 1,000 permutations of its own features
         within (n, arm token, card) groups (numpy.random.default_rng(20261123 + i)), else 'a shire-count and shape correction'.

USAGE:  layout_rule_v32.py decide <bundle.npz> <out.json>     (the fit lane, on MM1-v3.2's own fits)
        layout_rule_v32.py selftest <out.json>                (synthetic bundles: a null and a planted term; mechanics only)
SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import sys

import numpy as np

CANDIDATES = collections.OrderedDict([('none', []), ('N3', ['N3']), ('N1+N2', ['N1', 'N2']), ('G1', ['G1']), ('G1+N1', ['G1', 'N1']),
                                      ('F1', ['fresh32']), ('fresh24', ['fresh24'])])
ORDER = ['N3', 'N1+N2', 'G1', 'G1+N1', 'F1', 'fresh24']
COUNT_ONLY = ('N3', 'N1+N2')
FRESH_FAMILY = ('F1', 'fresh24')
FRESH_CHECK = ('fresh24', 'fresh32', 'fresh48')
FEATURES = ('N3', 'N1', 'N2', 'G1', 'fresh24', 'fresh32', 'fresh48')
MARGIN = 0.20
LOEO_GUARD = 0.02
LOCO_GUARD = 0.30
TIE_WINDOW = 0.10
NBOOT = 10000
BOOT_SEED = 20261121
NPERM = 1000
PERM_SEED0 = 20261122
LABEL_SEED0 = 20261123
P_SEL = 0.05
CLIP = (0.3, 3.0)


def rms(e):
    e = np.asarray(e, float)
    return float(100.0 * np.sqrt(np.mean(e ** 2))) if len(e) else float('nan')


def solve(Xs, y):
    """the normal equations, as verify-lay's v02_fits.solve (least squares where singular)"""
    A = Xs.T @ Xs
    if np.allclose(A, 0):
        return np.zeros(Xs.shape[1])
    try:
        return np.linalg.solve(A, Xs.T @ y)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(Xs, y, rcond=None)[0]


class Bundle:
    def __init__(self, z):
        self.T = np.asarray(z['T'], float)
        self.N = len(self.T)
        self.sub = np.asarray(z['sub'], bool)
        self.twin = np.asarray(z['twin'], bool)
        self.rung = np.asarray(z['rung'], bool)
        self.card = np.asarray(z['card']).astype(str)
        self.lolo = np.asarray(z['lolo']).astype(str)
        self.feat = {f: np.asarray(z['feat_' + f], float) for f in FEATURES}
        for f, v in self.feat.items():
            assert np.all(v[~self.sub] == 0.0), ('a feature is not 0 off the subset points', f)
        self.base_all = np.asarray(z['base_all'], float)
        self.names = [str(x) for x in z['fold_names']]
        self.base = {k: np.asarray(z['base_' + k], float) for k in self.names}
        self.test = {k: np.asarray(z['test_' + k], int) for k in self.names}
        self.loeo = [k for k in self.names if k.startswith('LOEO E') and len(k.split()) == 2]
        self.lolon = [k for k in self.names if k.startswith('LOLO ')]
        self.locon = [k for k in self.names if k.startswith('LOCO ')]
        assert sorted(self.lolon) == ['LOLO compact', 'LOLO other', 'LOLO spread'], self.lolon
        assert len(self.locon) == 4, self.locon
        ALL = np.arange(self.N)
        self.tr = {}
        for k in self.names:
            m = np.zeros(self.N, bool)
            m[self.test[k]] = True
            self.tr[k] = ALL[(~m) & (~self.rung) & self.sub]
        self.tr_all = ALL[(~self.rung) & self.sub]
        self.loeo_m = np.zeros(self.N, bool)
        for k in self.loeo:
            self.loeo_m[self.test[k]] = True
        self.loeo_nt = self.loeo_m & ~self.twin
        self.lolo_m = np.zeros(self.N, bool)
        for k in self.lolon:
            self.lolo_m[self.test[k]] = True
        self.lolo_m &= self.sub
        self.lolo_idx = np.where(self.lolo_m)[0]
        self.cards_sub = sorted({c for c in self.card[self.sub]})
        rng = np.random.default_rng(BOOT_SEED)
        self.boot_ix = rng.integers(0, len(self.lolo_idx), size=(NBOOT, len(self.lolo_idx)))


def matrix(B, cand, feat=None):
    feat = B.feat if feat is None else feat
    cols = CANDIDATES[cand]
    if not cols:
        return np.zeros((B.N, 0))
    return np.stack([feat[c] for c in cols], axis=1)


def evaluate(B, M):
    """two-stage per fold; held-out predictions and constants"""
    k = M.shape[1]
    heldL = np.full(B.N, np.nan)
    heldO = np.full(B.N, np.nan)
    heldC = np.full(B.N, np.nan)
    consts = {}
    for nm in B.names:
        b = B.base[nm]
        te = B.test[nm]
        if k:
            tr = B.tr[nm]
            r = b[tr] / B.T[tr]
            a = solve(r[:, None] * M[tr], 1.0 - r)
            g = np.clip(1.0 + M[te] @ a, *CLIP)
        else:
            a = np.zeros(0)
            g = np.ones(len(te))
        consts[nm] = [float(x) for x in a]
        pr = b[te] * g
        if nm in B.loeo:
            heldL[te] = pr
        elif nm in B.lolon:
            heldO[te] = pr
        elif nm in B.locon:
            heldC[te] = pr
    if k:
        r = B.base_all[B.tr_all] / B.T[B.tr_all]
        a_all = [float(x) for x in solve(r[:, None] * M[B.tr_all], 1.0 - r)]
    else:
        a_all = []
    e_lolo = heldO[B.lolo_idx] / B.T[B.lolo_idx] - 1.0
    loco_sub = {}
    for c in B.cards_sub:
        m = B.sub & (B.card == c) & np.isfinite(heldC)
        loco_sub[c] = rms(heldC[m] / B.T[m] - 1.0)
    return {'LOEO_nt': rms(heldL[B.loeo_nt] / B.T[B.loeo_nt] - 1.0), 'LOLO': rms(e_lolo), 'LOCO_sub': loco_sub,
            'LOCO_consts': {nm: consts[nm] for nm in B.locon}, 'a_all': a_all, 'n_LOEO_nt': int(B.loeo_nt.sum()),
            'n_LOLO': int(len(B.lolo_idx)), '_e_lolo': e_lolo}


def fresh_signs(B, feat):
    out = {}
    r = B.base_all[B.tr_all] / B.T[B.tr_all]
    for c in FRESH_CHECK:
        out[c] = float(solve(r[:, None] * feat[c][B.tr_all][:, None], 1.0 - r)[0])
    return out


def boot_upper(B, e1, e0):
    s1 = e1 ** 2
    s0 = e0 ** 2
    d = 100.0 * (np.sqrt(s1[B.boot_ix].mean(axis=1)) - np.sqrt(s0[B.boot_ix].mean(axis=1)))
    return float(np.percentile(d, 97.5)), float(np.percentile(d, 2.5))


def rule(B, feat=None):
    feat = B.feat if feat is None else feat
    ev = {c: evaluate(B, matrix(B, c, feat)) for c in CANDIDATES}
    n0 = ev['none']
    fs = fresh_signs(B, feat)
    elig = {}
    for c in ORDER:
        x = ev[c]
        up, lo = boot_upper(B, x['_e_lolo'], n0['_e_lolo'])
        cond = collections.OrderedDict()
        cond['i_margin'] = x['LOLO'] <= n0['LOLO'] - MARGIN
        cond['ii_bootstrap'] = up < 0.0
        cond['iii_loeo_guard'] = x['LOEO_nt'] <= n0['LOEO_nt'] + LOEO_GUARD
        card_ok = all(x['LOCO_sub'][k] <= n0['LOCO_sub'][k] + LOCO_GUARD for k in B.cards_sub)
        sign_ok = True
        for j in range(len(CANDIDATES[c])):
            v = np.array([x['LOCO_consts'][nm][j] for nm in B.locon])
            sign_ok = sign_ok and (bool(np.all(v > 0)) or bool(np.all(v < 0)))
        cond['iv_cards'] = bool(card_ok and sign_ok)
        if c in FRESH_FAMILY:
            v = np.array([fs[k] for k in FRESH_CHECK])
            cond['v_l3_conventions'] = bool(np.all(v > 0) or np.all(v < 0))
        elig[c] = {'conditions': {k: bool(v) for k, v in cond.items()}, 'eligible': bool(all(cond.values())),
                   'boot_ci95_delta_LOLO': [lo, up]}
    E = [c for c in ORDER if elig[c]['eligible']]
    if not E:
        return 'none', ev, elig, fs
    lo = min(ev[c]['LOLO'] for c in E)
    near = sorted([c for c in E if ev[c]['LOLO'] <= lo + TIE_WINDOW],
                  key=lambda c: (len(CANDIDATES[c]), ev[c]['LOEO_nt'], ORDER.index(c)))
    return near[0], ev, elig, fs


def permuted(B, perm):
    S = np.where(B.sub)[0]
    out = {}
    for f, v in B.feat.items():
        w = v.copy()
        w[S] = v[S][perm]
        out[f] = w
    return out


def decide(B, nperm=NPERM):
    w, ev, elig, fs = rule(B)
    d_obs = ev[w]['LOLO'] - ev['none']['LOLO'] if w != 'none' else 0.0
    res = {'rule_winner': w, 'd_obs_LOLO': d_obs, 'fresh_signs_all_data': fs,
           'candidates': {c: {k: v for k, v in ev[c].items() if not k.startswith('_')} for c in CANDIDATES},
           'eligibility': elig}
    S = np.where(B.sub)[0]
    if w == 'none':
        res['placebo'] = 'NOT RUN (no rule winner)'
        res['enters'] = 'none'
        return res
    ds = []
    wins = collections.Counter()
    for i in range(nperm):
        perm = np.random.default_rng(PERM_SEED0 + i).permutation(len(S))
        wi, evi, _, _ = rule(B, permuted(B, perm))
        wins[wi] += 1
        ds.append(evi[wi]['LOLO'] - evi['none']['LOLO'] if wi != 'none' else 0.0)
    ds = np.array(ds)
    p_sel = float((1 + np.sum(ds <= d_obs)) / (nperm + 1))
    res['placebo'] = {'n_perm': nperm, 'p_sel': p_sel, 'winners': dict(wins), 'd_median': float(np.median(ds))}
    res['enters'] = w if p_sel <= P_SEL else 'none'
    # the label (REPORTED)
    if res['enters'] in COUNT_ONLY:
        res['label'] = 'a shire-count correction (no placement information)'
    elif res['enters'] != 'none':
        res['label_REPORTED'] = 'computed by the label check (within-group permutations), never deciding'
    return res


def label_check(B, cand, arm, nperm=NPERM):
    """REPORTED: within (n, arm token, card) permutations of the winner's own features (n from N1: n = 32 (1 - N1))"""
    S = np.where(B.sub)[0]
    n = np.round(32.0 * (1.0 - B.feat['N1'])).astype(int)
    groups = collections.defaultdict(list)
    for j in S:
        groups[(int(n[j]), str(arm[j]), str(B.card[j]))].append(j)
    real = evaluate(B, matrix(B, cand))['LOLO']
    below = 0
    for i in range(nperm):
        rg = np.random.default_rng(LABEL_SEED0 + i)
        feat = {f: v.copy() for f, v in B.feat.items()}
        for js in groups.values():
            if len(js) > 1:
                js = np.array(js)
                p = js[rg.permutation(len(js))]
                for f in feat:
                    feat[f][js] = B.feat[f][p]
        if real < evaluate(B, matrix(B, cand, feat))['LOLO']:
            below += 1
    return {'real_LOLO': real, 'n_perm': nperm, 'placebos_above_real': below,
            'label': 'placement term' if below >= 950 else 'a shire-count and shape correction'}


def synthetic(seed, planted):
    """a stand-in bundle (mechanics only): 600 points, 240 subset points on 4 cards, three classes, 6 LOEO folds"""
    rg = np.random.default_rng(seed)
    N = 600
    sub = np.zeros(N, bool)
    sub[:240] = True
    cards = np.array(['c%d' % (i % 4) for i in range(N)])
    lolo = np.array([['compact', 'spread', 'other'][i % 3] if i < 240 else '' for i in range(N)])
    n = np.where(sub, rg.choice([2, 4, 8, 16, 24, 28], N), 32)
    feat = {'N3': np.where(sub, 32.0 / n - 1, 0.0), 'N1': np.where(sub, 1 - n / 32.0, 0.0)}
    feat['N2'] = feat['N1'] ** 2
    for f in ('G1', 'fresh24', 'fresh32', 'fresh48'):
        feat[f] = np.where(sub, rg.normal(0, 0.1, N), 0.0)
    T = np.exp(rg.normal(0, 0.03, N)) * 1.5
    true = 1.0 + (0.08 * feat['N3'] if planted else 0.0)
    T = T * true
    base = 1.5 * np.ones(N)
    exp = np.array(['E%d' % (100 + i % 6) for i in range(N)])
    z = {'T': T, 'sub': sub, 'twin': np.zeros(N, bool), 'rung': np.zeros(N, bool), 'card': cards, 'lolo': lolo, 'base_all': base}
    for f, v in feat.items():
        z['feat_' + f] = v
    names = []
    for e in sorted(set(exp)):
        k = 'LOEO ' + e
        names.append(k)
        z['base_' + k] = base * np.exp(rg.normal(0, 0.002))
        z['test_' + k] = np.where(exp == e)[0]
    for c in ('compact', 'spread', 'other'):
        k = 'LOLO ' + c
        names.append(k)
        z['base_' + k] = base.copy()
        z['test_' + k] = np.where(lolo == c)[0]
    for c in sorted(set(cards)):
        k = 'LOCO ' + c
        names.append(k)
        z['base_' + k] = base.copy()
        z['test_' + k] = np.where(cards == c)[0]
    z['fold_names'] = np.array(names)
    return z


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == 'decide':
        B = Bundle(np.load(sys.argv[2], allow_pickle=False))
        res = decide(B)
        if res['enters'] not in ('none',) + COUNT_ONLY:
            arm = np.load(sys.argv[2], allow_pickle=False)['arm'].astype(str)
            res['label_check_REPORTED'] = label_check(B, res['enters'], arm)
        json.dump(res, open(sys.argv[3], 'w'), indent=1, sort_keys=True)
        print('enters:', res['enters'], '| rule winner:', res['rule_winner'], '| placebo:', res.get('placebo'))
        return 0
    if len(sys.argv) >= 3 and sys.argv[1] == 'selftest':
        out = {}
        for nm, seed, planted in (('null', 11, False), ('planted_N3', 12, True)):
            B = Bundle(synthetic(seed, planted))
            res = decide(B, nperm=200)
            out[nm] = {'enters': res['enters'], 'rule_winner': res['rule_winner'], 'placebo': res['placebo'],
                       'LOLO': {c: res['candidates'][c]['LOLO'] for c in CANDIDATES},
                       'eligible': {c: res['eligibility'][c]['eligible'] for c in ORDER}}
            print(nm, out[nm]['enters'], out[nm]['rule_winner'], out[nm]['placebo'] if isinstance(out[nm]['placebo'], str) else
                  {k: out[nm]['placebo'][k] for k in ('p_sel', 'n_perm')})
        ok = out['null']['enters'] == 'none' and out['planted_N3']['enters'] == 'N3'
        out['SELFTEST'] = 'PASS' if ok else 'FAIL'
        json.dump(out, open(sys.argv[2], 'w'), indent=1, sort_keys=True)
        print('SELFTEST', out['SELFTEST'])
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
