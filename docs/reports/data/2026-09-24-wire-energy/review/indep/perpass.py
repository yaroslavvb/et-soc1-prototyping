#!/usr/bin/env python3
"""Per-pass replicates of the key numbers (to give a spread), same Method A bursts, no leakage correction unless --leak."""
import json, sys, re, numpy as np, os
HERE = os.path.dirname(os.path.abspath(__file__))
B = [b for b in json.load(open(os.path.join(HERE, 'bursts.json'))) if not b['bad']]
LEAK = '--leak' in sys.argv
def val(b, m): return b['pJB_boardleak'] if (m == 'board' and LEAK) else b['pJB_' + m]
def slope(vs, card, m, p, pat, ds, key='hop'):
    x = []; y = []
    for b in B:
        if b['set'] == vs and b['card'] == card and b['pass_'] == p and re.fullmatch(pat, b['cfg']) and round(b[key]) in ds:
            x.append(b[key]); y.append(val(b, m))
    return np.polyfit(x, y, 1)[0]
res = {}
for card in ('aifoundry2', 'aifoundry3'):
    for m in ('noc', 'board'):
        for p in (0, 1, 2):
            S = {P: slope('v2', card, m, p, rf'wu/p{re.escape(P)}/hop\d', [1, 2, 3, 4, 6]) for P in ['0', '0.25', '0.5', '0.75', '1']}
            fz = slope('v2', card, m, p, r'wfrz/hop\d', [1, 3, 6])
            A = [[1, 2*float(P)*(1-float(P)), float(P)] for P in S] + [[1, 0, 244/512]]
            y = list(S.values()) + [fz]
            c, *_ = np.linalg.lstsq(np.array(A), np.array(y), rcond=None)
            rms = np.sqrt(np.mean((np.array(y) - np.array(A) @ c) ** 2))
            sep = {P: slope('v2', card, m, p, rf'wsep/p{re.escape(P)}/hop\d', [1, 2, 3, 4, 5], 'mean_hops') for P in ['0', '0.5']}
            wu = {P: slope('v2', card, m, p, rf'wu/p{re.escape(P)}/hop\d', [1, 2, 3, 4]) for P in ['0', '0.5']}
            V1 = {P: slope('v1', card, m, p, rf'wbern/p{re.escape(P)}/hop\d', [1, 2, 3, 4, 6]) for P in ['0', '0.1', '0.25', '0.5', '0.75', '0.9', '1']}
            A1 = [[1, 2*float(P)*(1-float(P)), float(P)] for P in V1]
            c1, *_ = np.linalg.lstsq(np.array(A1), np.array(list(V1.values())), rcond=None)
            rms1 = np.sqrt(np.mean((np.array(list(V1.values())) - np.array(A1) @ c1) ** 2))
            row = dict(v2_a=c[1]*125, v2_b=c[2]*125, v2_s0=c[0], v2_rms=rms, v1_a=c1[1]*125, v1_b=c1[2]*125, v1_rms=rms1,
                       comp31=(S['0.75']-S['0.25'])*250, comp10=(S['1']-S['0'])*125,
                       sep_data=(sep['0.5']-sep['0'])*125, sep_zero=sep['0']*125, wu_data=(wu['0.5']-wu['0'])*125, wu_zero=wu['0']*125)
            for k, v in row.items(): res.setdefault((card, m, k), []).append(v)
for m in ('noc', 'board'):
    for k in ['v2_a', 'v2_b', 'v2_rms', 'v1_a', 'v1_b', 'v1_rms', 'comp31', 'comp10', 'sep_data', 'wu_data', 'sep_zero', 'wu_zero']:
        a2 = res[('aifoundry2', m, k)]; a3 = res[('aifoundry3', m, k)]
        allv = a2 + a3
        print('%-5s %-9s af2 %7.3f [%7.3f..%7.3f]  af3 %7.3f [%7.3f..%7.3f]  pooled-mean-of-6 %7.3f [%7.3f..%7.3f]' % (
            m, k, np.mean(a2), min(a2), max(a2), np.mean(a3), min(a3), max(a3), np.mean(allv), min(allv), max(allv)))
