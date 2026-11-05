"""Post hoc desk check (Q141(r)'s fix pass, Wed 4 Nov 2026), unregistered: the paired-anchor card scale (card 1 over aifoundry3)
at 95%, read at the level of the pass.

anchor_t95_measured.py, beside this file, gives each anchor's ratio its own delta-method variance and adds the anchors' variances
as if the anchors were independent, although all of a format's anchors ran in the same passes. Here the pass is the unit: in each
pass, each anchor's mean D over its non-failed runs is divided by that anchor's mean D on aifoundry3, and the family's anchors are
averaged, giving one index per pass. The scale is card 1's mean index over aifoundry3's; its relative variance adds the two cards'
(the delta method on a ratio of two means), and its degrees of freedom are Welch's, on card 1's passes against aifoundry3's. Any
correlation between anchors inside a pass is then kept rather than assumed away. A pass counts only where every anchor of the
family has a D in it.

Reads only committed files (E153's and E157's primary runs.csv) and takes the t quantile from the committed anchor_scale_t95.py
(ablcore.py's, verbatim). Standard library only:

    python3 -I -B anchor_pass_level.py <lab clone> anchor-pass-level.json > anchor-pass-level.txt

SPDX-License-Identifier: Apache-2.0
"""
import collections
import csv
import importlib.util
import json
import math
import os
import statistics as st
import sys

ROOT = sys.argv[1]
OUT = sys.argv[2]
HERE = 'docs/reports/data/2026-11-04-q140-anchor-scale-t95'
RUNS = {'aifoundry3': 'docs/reports/data/2026-11-03-e153-blind6-aifoundry3/runs.csv',
        'card1': 'docs/reports/data/2026-11-03-e157-blind6-card1/runs.csv'}
FAMILIES = {'int8': ['int8.full', 'int8.anchor6_full'],
            'floats': ['fp32.randn', 'fp32.anchor6_randn', 'fp16.randn', 'fp16.anchor6_randn']}

spec = importlib.util.spec_from_file_location('t95', os.path.join(ROOT, HERE, 'anchor_scale_t95.py'))
T95 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T95)


def pass_means(path):
    """{item: {pass: mean D over the pass's non-failed runs that have a D}}"""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(path, newline='') as fh:
        for row in csv.DictReader(fh):
            if row.get('fail') not in ('0', '', None) or row.get('D') in ('', None):
                continue
            acc[row['item']][row['pass']].append(float(row['D']))
    return {item: {p: st.mean(v) for p, v in by.items()} for item, by in acc.items()}


def corr(x, y):
    mx, my = st.mean(x), st.mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


D = {card: pass_means(os.path.join(ROOT, p)) for card, p in RUNS.items()}
out = {'method': 'pass-level index: per pass, the mean over a family\'s anchors of D / that anchor\'s aifoundry3 mean D; '
                 'scale = mean card-1 index / mean aifoundry3 index; relative variance = var_c1/(n_c1 m_c1^2) + '
                 'var_a3/(n_a3 m_a3^2); Welch df; t from anchor_scale_t95.t_ppf(0.975, df)',
       'inputs': RUNS}
for fam, names in FAMILIES.items():
    base = {n: st.mean(D['aifoundry3'][n].values()) for n in names}
    index, used, dropped = {}, {}, {}
    for card in ('aifoundry3', 'card1'):
        every = sorted(set().union(*(set(D[card][n]) for n in names)))
        common = [p for p in every if all(p in D[card][n] for n in names)]
        dropped[card] = [p for p in every if p not in common]
        used[card] = common
        index[card] = [st.mean(D[card][n][p] / base[n] for n in names) for p in common]
    ma, mc = st.mean(index['aifoundry3']), st.mean(index['card1'])
    na, nc = len(index['aifoundry3']), len(index['card1'])
    va = st.variance(index['aifoundry3']) / (na * ma ** 2)
    vc = st.variance(index['card1']) / (nc * mc ** 2)
    df = (va + vc) ** 2 / (va ** 2 / (na - 1) + vc ** 2 / (nc - 1))
    t = T95.t_ppf(0.975, df)
    rel_se = math.sqrt(va + vc)
    res = {'anchors': names, 'passes_used': used, 'passes_dropped': dropped,
           'index_aifoundry3': [round(v, 6) for v in index['aifoundry3']],
           'index_card1': [round(v, 6) for v in index['card1']],
           'scale': round(mc / ma, 5), 'rel_se': round(rel_se, 5), 'welch_df': round(df, 2), 't975': round(t, 3),
           'half_width_95_rel': round(t * rel_se, 5)}
    if len(names) == 2:
        for card in ('aifoundry3', 'card1'):
            x = [D[card][names[0]][p] for p in used[card]]
            y = [D[card][names[1]][p] for p in used[card]]
            res['anchor_corr_by_pass_' + card] = round(corr(x, y), 3)
    out[fam] = res
with open(OUT, 'w') as fh:
    json.dump(out, fh, indent=1)
    fh.write('\n')
for fam in FAMILIES:
    o = out[fam]
    print('%s: pass-level scale %.4f, rel s.e. %.2f%%, Welch df %.2f, t %.3f, 95%% half-width %.2f%% '
          '(passes: aifoundry3 %d, card 1 %d; dropped: aifoundry3 %s, card 1 %s)' % (
              fam, o['scale'], 100 * o['rel_se'], o['welch_df'], o['t975'], 100 * o['half_width_95_rel'],
              len(o['passes_used']['aifoundry3']), len(o['passes_used']['card1']),
              o['passes_dropped']['aifoundry3'] or 'none', o['passes_dropped']['card1'] or 'none'))
    for card, label in (('aifoundry3', 'aifoundry3'), ('card1', 'card 1')):
        k = 'anchor_corr_by_pass_' + card
        if k in o:
            print('    the two anchors\' D, correlation across passes on %s: %+.2f (n %d)' % (
                label, o[k], len(o['passes_used'][card])))
