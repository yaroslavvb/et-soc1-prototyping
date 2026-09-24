#!/usr/bin/env python3
"""Independent fits on bursts.json: per-hop slopes, slope(P) model, contention, axis, lanes."""
import json, os, sys, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, 'bursts.json')))
DROP_BAD = '--keep-bad' not in sys.argv
if DROP_BAD:
    B = [b for b in B if not b['bad']]
if '--leak' in sys.argv:   # swap in the leakage-corrected board meter (pipeline's model) to size its effect
    for b in B:
        b['pJB_board'] = b['pJB_boardleak']
METERS = ('board', 'noc')
CARDS = ('aifoundry2', 'aifoundry3')
RES = {}


def pts(vs, card, pred, meter, dkey='hop'):
    xs, ys = [], []
    for b in B:
        if b['set'] == vs and b['card'] == card and pred(b['cfg'], b):
            xs.append(b[dkey]); ys.append(b['pJB_' + meter])
    return np.array(xs, float), np.array(ys, float)


def linfit(x, y):
    A = np.vstack([np.ones_like(x), x]).T
    c, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ c
    n = len(x)
    s2 = (r @ r) / max(n - 2, 1)
    cov = s2 * np.linalg.inv(A.T @ A)
    return c[0], c[1], np.sqrt(cov[1, 1]), np.sqrt(s2)


def cfg_re(pat):
    rx = re.compile(pat)
    return lambda c, b: rx.fullmatch(c) is not None


def slope_for(vs, card, meter, pat, ds, dkey='hop'):
    f = cfg_re(pat)
    x, y = pts(vs, card, lambda c, b: f(c, b), meter, dkey)
    m = np.isin(np.round(x).astype(int), ds); x, y = x[m], y[m]
    return linfit(x, y), len(x)


def mean_at(vs, card, meter, pat, d):
    f = cfg_re(pat)
    x, y = pts(vs, card, lambda c, b: f(c, b) and b['hop'] == d, meter)
    return y.mean(), y.std(ddof=1) if len(y) > 1 else 0, len(y)


def P_of(s):
    return float(s)


lines = []
def pr(*a):
    s = ' '.join(str(x) for x in a); print(s); lines.append(s)

# ---------------- per-P slopes -----------------
slopes = {}
for card in CARDS:
    for meter in METERS:
        for vs, fam, Ps, ds in [('v1', 'wbern', ['0', '0.1', '0.25', '0.5', '0.75', '0.9', '1'], [1, 2, 3, 4, 6]),
                                 ('v2', 'wu', ['0', '0.25', '0.5', '0.75', '1'], [1, 2, 3, 4, 6])]:
            for P in Ps:
                (i0, s, se, rms), n = slope_for(vs, card, meter, rf'{fam}/p{re.escape(P)}/hop\d', ds)
                h0 = mean_at(vs, card, meter, rf'{fam}/p{re.escape(P)}/hop0', 0)[0]
                slopes[(vs, card, meter, fam, P)] = dict(i=i0, s=s, se=se, rms=rms, n=n, hop0=h0)
        # wfrz
        (i0, s, se, rms), n = slope_for('v2', card, meter, r'wfrz/hop\d', [1, 3, 6])
        h0 = mean_at('v2', card, meter, r'wfrz/hop0', 0)[0]
        slopes[('v2', card, meter, 'wfrz', 'frz')] = dict(i=i0, s=s, se=se, rms=rms, n=n, hop0=h0)

pr('=== per-hop slopes (pJ/B/hop), intercept at d=0 from fit, measured hop0 ===')
for k, v in sorted(slopes.items()):
    pr(k, 'slope %.3f +- %.3f  icpt %.3f  hop0 %.3f  rms %.3f n=%d' % (v['s'], v['se'], v['i'], v['hop0'], v['rms'], v['n']))

# ---------------- slope(P) model -----------------
def model_fit(vs, card, meter, fam, Ps, with_frz):
    rows, ys, names = [], [], []
    for P in Ps:
        p = float(P)
        rows.append([1, 2 * p * (1 - p), p]); ys.append(slopes[(vs, card, meter, fam, P)]['s']); names.append(P)
    if with_frz:
        p = 244 / 512
        rows.append([1, 0.0, p]); ys.append(slopes[(vs, card, meter, 'wfrz', 'frz')]['s']); names.append('frz')
    A = np.array(rows); y = np.array(ys)
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ c
    rms = np.sqrt(np.mean(r ** 2))
    return c, rms, dict(zip(names, r))

pr('\n=== slope(P) = s0 + a*2P(1-P) + b*P ; a,b in fJ per bit per hop (pJ/B * 1000/8) ===')
model = {}
for card in CARDS:
    for meter in METERS:
        c, rms, r = model_fit('v2', card, meter, 'wu', ['0', '0.25', '0.5', '0.75', '1'], True)
        model[('v2', card, meter)] = (c, rms)
        pr('v2', card, meter, 's0=%.3f pJ/B/hop  a=%.1f fJ  b=%.1f fJ  rms=%.4f pJ/B/hop' % (c[0], c[1] * 125, c[2] * 125, rms),
           ' resid', {k: round(v, 4) for k, v in r.items()})
        c1, rms1, r1 = model_fit('v1', card, meter, 'wbern', ['0', '0.1', '0.25', '0.5', '0.75', '0.9', '1'], False)
        model[('v1', card, meter)] = (c1, rms1)
        pr('v1', card, meter, 's0=%.3f pJ/B/hop  a=%.1f fJ  b=%.1f fJ  rms=%.4f' % (c1[0], c1[1] * 125, c1[2] * 125, rms1),
           ' resid', {k: round(v, 4) for k, v in r1.items()})

# pooled over cards: average slopes across cards then fit
pr('\n=== model on card-averaged slopes ===')
for vs, fam, Ps, frz in [('v2', 'wu', ['0', '0.25', '0.5', '0.75', '1'], True), ('v1', 'wbern', ['0', '0.1', '0.25', '0.5', '0.75', '0.9', '1'], False)]:
    for meter in METERS:
        rows, ys = [], []
        for P in Ps:
            p = float(P); rows.append([1, 2 * p * (1 - p), p])
            ys.append(np.mean([slopes[(vs, cd, meter, fam, P)]['s'] for cd in CARDS]))
        if frz:
            rows.append([1, 0, 244 / 512]); ys.append(np.mean([slopes[(vs, cd, meter, 'wfrz', 'frz')]['s'] for cd in CARDS]))
        A = np.array(rows); y = np.array(ys)
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        rms = np.sqrt(np.mean((y - A @ c) ** 2))
        model[(vs, 'avg', meter)] = (c, rms)
        pr(vs, 'card-avg', meter, 's0=%.3f a=%.1f b=%.1f rms=%.4f' % (c[0], c[1] * 125, c[2] * 125, rms))

pr('\n=== complement tests (v2 wu) fJ per one-bit per hop ===')
for card in CARDS + ('avg',):
    for meter in METERS:
        g = (lambda P: slopes[('v2', card, meter, 'wu', P)]['s']) if card != 'avg' else (lambda P: np.mean([slopes[('v2', cd, meter, 'wu', P)]['s'] for cd in CARDS]))
        d31 = (g('0.75') - g('0.25')) * 1000 / 4
        d10 = (g('1') - g('0')) * 1000 / 8
        pr(card, meter, 'slope(3/4)-slope(1/4): %.1f fJ/one/hop ; slope(1)-slope(0): %.1f' % (d31, d10))

pr('\n=== all-ones vs random per hop (v2 wu) pJ/B/hop ===')
for card in CARDS:
    for meter in METERS:
        pr(card, meter, 'P=1 %.3f  P=0.5 %.3f  P=0 %.3f  frz %.3f' % tuple(slopes[('v2', card, meter, f, P)]['s'] for f, P in [('wu', '1'), ('wu', '0.5'), ('wu', '0'), ('wfrz', 'frz')]))

# ---------------- contention -----------------
pr('\n=== contention: wsep (mean_hops 1-5) vs wu (d 1-4); fJ per bit per hop ===')
cont = {}
for card in CARDS:
    for meter in METERS:
        def sl(pat, ds, dkey):
            f = cfg_re(pat)
            x, y = pts('v2', card, lambda c, b: f(c, b), meter, dkey)
            m = np.isin(np.round(x).astype(int), ds); x, y = x[m], y[m]
            return linfit(x, y)
        s_sep_r = sl(r'wsep/p0\.5/hop\d', [1, 2, 3, 4, 5], 'mean_hops')
        s_sep_0 = sl(r'wsep/p0/hop\d', [1, 2, 3, 4, 5], 'mean_hops')
        s_wu_r = sl(r'wu/p0\.5/hop\d', [1, 2, 3, 4], 'hop')
        s_wu_0 = sl(r'wu/p0/hop\d', [1, 2, 3, 4], 'hop')
        # also: per-point difference then fit
        dsep = (s_sep_r[1] - s_sep_0[1]) * 125
        dwu = (s_wu_r[1] - s_wu_0[1]) * 125
        cont[(card, meter)] = dict(sep_data=dsep, wu_data=dwu, sep_zero=s_sep_0[1] * 125, wu_zero=s_wu_0[1] * 125,
                                   sep_rand=s_sep_r[1] * 125, wu_rand=s_wu_r[1] * 125)
        pr(card, meter, 'data(random-zeros): wsep %.1f  wu %.1f | zeros: wsep %.1f  wu %.1f | random total: wsep %.1f wu %.1f' % (
            dsep, dwu, s_sep_0[1] * 125, s_wu_0[1] * 125, s_sep_r[1] * 125, s_wu_r[1] * 125))
        # d=1 comparison
        f1 = lambda pat: np.mean([b['pJB_' + meter] for b in B if b['set'] == 'v2' and b['card'] == card and re.fullmatch(pat, b['cfg'])])
        pr('   d=1 pJ/B: wsep p0.5 %.3f wu p0.5 %.3f | wsep p0 %.3f wu p0 %.3f' % (
            f1(r'wsep/p0\.5/hop1'), f1(r'wu/p0\.5/hop1'), f1(r'wsep/p0/hop1'), f1(r'wu/p0/hop1')))
for meter in METERS:
    pr('card-avg', meter, {k: round(np.mean([cont[(cd, meter)][k] for cd in CARDS]), 1) for k in cont[(CARDS[0], meter)]})

# wsep mean_hops values
pr('wsep mean_hops per cfg:', sorted({(b['cfg'], b['mean_hops']) for b in B if b['cfg'].startswith('wsep') and b['card'] == 'aifoundry2'}))

# ---------------- C1: data-dependent part vs d on noc; hop0 ------------
pr('\n=== C1: random-minus-zeros per byte vs d (v2 wu), and hop0 vs extrapolation ===')
for card in CARDS:
    for meter in METERS:
        row = []
        for d in [0, 1, 2, 3, 4, 6]:
            r = mean_at('v2', card, meter, r'wu/p0\.5/hop%d' % d, d)[0]; z = mean_at('v2', card, meter, r'wu/p0/hop%d' % d, d)[0]
            row.append((d, round(r - z, 3)))
        sr = slopes[('v2', card, meter, 'wu', '0.5')]; sz = slopes[('v2', card, meter, 'wu', '0')]
        icpt = sr['i'] - sz['i']
        pr(card, meter, 'diff by d', row, ' fit icpt of diff %.3f, slope of diff %.3f' % (icpt, sr['s'] - sz['s']))
        # leaving the shire costs ~one extra hop: fit intercept - hop0 value, in hops
        for P in ['0', '0.5', '1']:
            s = slopes[('v2', card, meter, 'wu', P)]
            pr('    P=%s  (fit icpt - hop0)/slope = %.2f hops  [icpt %.3f hop0 %.3f slope %.3f]' % (P, (s['i'] - s['hop0']) / s['s'], s['i'], s['hop0'], s['s']))
    # v1 as well
    for meter in METERS:
        for P in ['0', '0.5', '1']:
            s = slopes[('v1', card, meter, 'wbern', P)]
            pr('  v1', card, meter, 'P=%s (icpt-hop0)/slope = %.2f hops [icpt %.3f hop0 %.3f slope %.3f rms %.3f]' % (P, (s['i'] - s['hop0']) / s['s'], s['i'], s['hop0'], s['s'], s['rms']))

# ---------------- C4 axis ---------------
pr('\n=== C4: waxis x vs y, random minus zeros per hop over d=1-3 (v1) fJ/bit/hop and random total ===')
for card in CARDS:
    for meter in METERS:
        out = []
        for ax in 'xy':
            f5 = slope_for('v1', card, meter, rf'waxis/{ax}/hop[123]/p0\.5', [1, 2, 3])
            f0 = slope_for('v1', card, meter, rf'waxis/{ax}/hop[123]/p0', [1, 2, 3])
            out.append('%s: rand %.1f zeros %.1f data %.1f (n=%d)' % (ax, f5[0][1] * 125, f0[0][1] * 125, (f5[0][1] - f0[0][1]) * 125, f5[1]))
        pr(card, meter, ' | '.join(out))

# ---------------- C6 lanes ---------------
pr('\n=== C6: walt/nN slopes (hops 1,3,6) pJ/B/hop ===')
for card in CARDS:
    for meter in METERS:
        pr(card, meter, ' '.join('n%s %.3f' % (N, slope_for('v1', card, meter, rf'walt/n{N}/hop\d', [1, 3, 6])[0][1]) for N in [16, 32, 64, 128, 256]))

json.dump({'slopes': {'|'.join(map(str, k)): v for k, v in slopes.items()},
           'model': {'|'.join(k): [list(v[0]), v[1]] for k, v in model.items()},
           'contention': {'|'.join(k): v for k, v in cont.items()}}, open(os.path.join(HERE, 'fits%s.json' % ('_leak' if '--leak' in sys.argv else '')), 'w'), indent=1)
open(os.path.join(HERE, 'fits%s.txt' % ('_leak' if '--leak' in sys.argv else '')), 'w').write('\n'.join(lines) + '\n')
