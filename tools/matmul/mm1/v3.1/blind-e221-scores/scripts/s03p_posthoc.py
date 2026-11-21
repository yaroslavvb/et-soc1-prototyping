#!/usr/bin/env python3
"""blind-e221 (Q235) step 3p: POST HOC readings of the scored cases (REPORTED; deciding nothing; nothing here was declared). From the
scorer's case table (work/step3/scores-blind-e221-cases.csv) and record: where MM1-v3.2's part A misses fall (class, placement family,
shire count), part A recounted without the MASK class, the MASK class by family and shire count, how many E2 and E4 misses are also T1
misses, the worst cases, and the same for MM1-v3.1 beside. Desk; stdlib.
Run: /usr/bin/python3 -I -B s03p_posthoc.py <lane dir>      Writes work/step3/posthoc-e221.json.
"""
import collections
import csv
import hashlib
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
S3 = os.path.join(L, 'work', 'step3')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


SC = json.load(open(os.path.join(S3, 'scores-blind-e221.json')))
BANDS = SC['bands']
rows = list(csv.DictReader(open(os.path.join(S3, 'scores-blind-e221-cases.csv'))))


def fv(x):
    return None if x in ('', None) else float(x)


CARDS = ('aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0')
RQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}


def passes(c, mo, rule):
    q = RQ[rule]
    card = c['card']
    if q in ('wall', 'mean', 'sec'):
        if c[f'twin_time_{mo}'] == '1' or not int(c['n_time']):
            return None
        return abs(fv(c[f'{mo}_e_{q}'])) <= BANDS[card][rule]
    if c[f'twin_energy_{mo}'] == '1' or not int(c['n_energy']):
        return None
    if q in ('E1', 'E2') and c['watts_case'] == '1':
        return abs(fv(c[f'{mo}_d_{q}'])) <= BANDS[card]['watts_W']
    return abs(fv(c[f'{mo}_e_{q}'])) <= BANDS[card][rule]


def verdict(ok, n):
    return 'NO DATA' if n == 0 else ('TOO FEW' if n < 10 else ('PASS' if 10 * ok >= 9 * n else 'FAIL'))


def nsh_bucket(n):
    n = int(n)
    return '1' if n == 1 else ('2-3' if n <= 3 else ('4-7' if n <= 7 else ('8-15' if n <= 15 else ('16-31' if n <= 31 else '32'))))


out = {'what': 'blind-e221 step 3p: post hoc readings (REPORTED, deciding nothing)', 'scores_json_sha256': sha(os.path.join(S3, 'scores-blind-e221.json'))}
for mo in ('v32', 'v31'):
    O = {}
    miss = collections.Counter()
    for c in rows:
        for rule in ('T1', 'E2', 'E4'):
            p = passes(c, mo, rule)
            if p is False:
                miss[(c['card'], rule, c['class'], c['subfamily'] or '-')] += 1
    O['misses_by_card_rule_class_family'] = {f'{k[0]}|{k[1]}|{k[2]}|{k[3]}': v for k, v in sorted(miss.items())}
    cls = collections.Counter()
    for (card, rule, k, fam), v in miss.items():
        cls[(rule, k)] += v
    O['misses_by_rule_class (all cards)'] = {f'{a}|{b}': v for (a, b), v in sorted(cls.items())}
    # part A recounted without the MASK class, and on the MASK class alone (post hoc)
    for nm, sel in (('without MASK', lambda c: c['class'] != 'MASK'), ('MASK only', lambda c: c['class'] == 'MASK'),
                    ('FULL mask only', lambda c: c['group_mask'] == 'FULL'), ('SUB masks only', lambda c: c['group_mask'] != 'FULL')):
        T = {}
        for card in CARDS:
            for rule in RQ:
                ps = [passes(c, mo, rule) for c in rows if c['card'] == card and sel(c)]
                ps = [p for p in ps if p is not None]
                T[f'{card}|{rule}'] = [verdict(sum(ps), len(ps)), sum(ps), len(ps)]
        fails = [k for k, v in T.items() if v[0] == 'FAIL']
        passes_ = [k for k, v in T.items() if v[0] == 'PASS']
        O[f'part A post hoc, {nm}'] = {'cells': T, 'verdict': 'FAIL' if fails else ('PASS' if passes_ else 'NOT DECIDED'), 'fails': fails}
    # E2 / E4 misses that are also T1 misses (the time forecast carried into the energy with t forecast)
    for rule in ('E2', 'E4'):
        both = only = 0
        for c in rows:
            pe, pt = passes(c, mo, rule), passes(c, mo, 'T1')
            if pe is False:
                if pt is False:
                    both += 1
                else:
                    only += 1
        O[f'{rule} misses that are T1 misses'] = {'also_T1_miss': both, 'not_a_T1_miss': only}
    # MASK by family and shire count (wall)
    fam = collections.defaultdict(list)
    famn = collections.defaultdict(list)
    for c in rows:
        if c['class'] != 'MASK' or c[f'twin_time_{mo}'] == '1' or not int(c['n_time']):
            continue
        e = fv(c[f'{mo}_e_wall'])
        fam[(c['subfamily'], c['group_mask'])].append(e)
        famn[(c['group_mask'], nsh_bucket(c['n_shires']))].append(e)
    O['MASK wall by family (rms %, bias %, n)'] = {f'{k[0]}|{k[1]}': [100 * math.sqrt(sum(x * x for x in v) / len(v)), 100 * sum(v) / len(v), len(v)]
                                                   for k, v in sorted(fam.items())}
    O['MASK wall by shire count (rms %, bias %, n)'] = {f'{k[0]}|{k[1]}': [100 * math.sqrt(sum(x * x for x in v) / len(v)), 100 * sum(v) / len(v), len(v)]
                                                        for k, v in sorted(famn.items())}
    allw = [(abs(fv(c[f'{mo}_e_wall'])), c['case'], fv(c[f'{mo}_e_wall']), c['class'], c['subfamily']) for c in rows
            if int(c['n_time']) and c[f'twin_time_{mo}'] != '1']
    O['worst 20 cases by |T1|'] = [{'case': k, 'e_wall_pct': 100 * e, 'class': cl, 'family': fa} for _, k, e, cl, fa in sorted(allw, reverse=True)[:20]]
    out[mo] = O
json.dump(out, open(os.path.join(S3, 'posthoc-e221.json'), 'w'), indent=1, sort_keys=True)
for mo in ('v32', 'v31'):
    O = out[mo]
    print('==', mo)
    print(' misses by rule|class:', json.dumps(O['misses_by_rule_class (all cards)']))
    for nm in ('without MASK', 'MASK only', 'FULL mask only', 'SUB masks only'):
        x = O[f'part A post hoc, {nm}']
        print(f' part A post hoc, {nm}: {x["verdict"]} fails {x["fails"]}')
        print('   ', ' '.join(f"{k.split('|')[0].replace('aifoundry', 'a')}:{k.split('|')[1]} {v[1]}/{v[2]}" for k, v in x['cells'].items()))
    print(' E2/E4 vs T1:', json.dumps({k: v for k, v in O.items() if 'T1 misses' in k}))
    print(' MASK wall by family:', json.dumps({k: [round(v[0], 2), round(v[1], 2), v[2]] for k, v in O['MASK wall by family (rms %, bias %, n)'].items()}))
    print(' MASK wall by shire count:', json.dumps({k: [round(v[0], 2), round(v[1], 2), v[2]] for k, v in O['MASK wall by shire count (rms %, bias %, n)'].items()}))
    print(' worst:', json.dumps([(w['case'].replace('aifoundry', 'a'), round(w['e_wall_pct'], 1)) for w in O['worst 20 cases by |T1|'][:12]]))
print(sha(os.path.join(S3, 'posthoc-e221.json')), 'work/step3/posthoc-e221.json')
