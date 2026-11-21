#!/usr/bin/env python3
"""mask-mesh r01 (REPORTED, post hoc; decides nothing): summaries of the frozen held-out record for the README: per experiment the MASK
points' rms (MM1-v3.2 against the term, LOMO where the mask is a LOMO fold, else LOEO), the lead by card, gemmL2x6x10's single-shire
placements (measured / MM1-v3.2 / the term held out), the worst remaining lead cases, the fold constants' ranges and signs.
Run: python3 -I -B r01_report.py <lane dir>  ->  work/fit/report-mesh.json"""
import collections
import json
import math
import os
import sys

L = os.path.abspath(sys.argv[1])
R = json.load(open(os.path.join(L, 'work', 'fit', 'points-scored-mesh.json')))['rows']
H = json.load(open(os.path.join(L, 'work', 'fit', 'holdout-mesh.json')))
lomo = set(H['lomo_masks'])


def rr(v):
    return round(100 * math.sqrt(sum(x * x for x in v) / len(v)), 2) if v else None


def bias(v):
    return round(100 * sum(v) / len(v), 2) if v else None


out = {'what': 'mask-mesh r01: REPORTED summaries (post hoc) of the frozen record'}
per = collections.defaultdict(lambda: {'v32': [], 'mesh': []})
for r in R:
    if not r['MASK'] or r['twin_x']:
        continue
    held = r['mesh_LOMO'] if (r['layout_point'] and r['mask'] in lomo) else r['mesh_LOEO']
    base = r['v32_all'] if (r['layout_point'] and r['mask'] in lomo) else r['v32_LOEO']
    d = per[r['exp']]
    d['v32'].append(base / r['T_meas_us'] - 1)
    d['mesh'].append(held / r['T_meas_us'] - 1)
out['MASK_no_twin_by_experiment'] = {e: {'n': len(d['v32']), 'rms_MM1-v3.2': rr(d['v32']), 'bias_MM1-v3.2': bias(d['v32']),
                                         'rms_mesh_held_out': rr(d['mesh']), 'bias_mesh': bias(d['mesh'])} for e, d in sorted(per.items())}
bycard = collections.defaultdict(lambda: {'v32': [], 'mesh': []})
for r in R:
    if r['lead']:
        bycard[r['card']]['v32'].append(r['v32_all'] / r['T_meas_us'] - 1)
        bycard[r['card']]['mesh'].append(r['mesh_LOMO'] / r['T_meas_us'] - 1)
out['lead_by_card_LOMO'] = {c: {'n': len(d['v32']), 'rms_MM1-v3.2': rr(d['v32']), 'rms_mesh': rr(d['mesh'])} for c, d in sorted(bycard.items())}
sing = []
for r in R:
    if r['exp'] == 'E221' and r['arm'] == 'gemmL2x6x10' and r['n_shires'] == 1 and r['fmt'] == 'fp32' and r['kind'] == 'zeros':
        s = int(r['mask'], 16).bit_length() - 1
        sing.append({'shire': s, 'card': r['card'], 'row_group_equals_column_group_mod4': ((s >> 2) & 3) == (s & 3),
                     'err_MM1-v3.2_pct': round(100 * (r['v32_all'] / r['T_meas_us'] - 1), 2),
                     'err_mesh_LOMO_pct': round(100 * (r['mesh_LOMO'] / r['T_meas_us'] - 1), 2), 'dA': round(r['dA'], 4), 'dB': round(r['dB'], 4),
                     'g3': round(r['g3'], 4)})
sing.sort(key=lambda x: (x['shire'], x['card']))
out['gemmL2x6x10_single_shires'] = sing
grp = collections.defaultdict(lambda: {'v32': [], 'mesh': []})
for x in sing:
    k = 'collision set (row group = column group mod 4)' if x['row_group_equals_column_group_mod4'] else 'the other shires'
    grp[k]['v32'].append(x['err_MM1-v3.2_pct'] / 100)
    grp[k]['mesh'].append(x['err_mesh_LOMO_pct'] / 100)
out['gemmL2x6x10_single_shires_by_set'] = {k: {'n': len(d['v32']), 'rms_MM1-v3.2': rr(d['v32']), 'bias_MM1-v3.2': bias(d['v32']),
                                               'rms_mesh': rr(d['mesh']), 'bias_mesh': bias(d['mesh'])} for k, d in grp.items()}
worst = sorted((r for r in R if r['lead']), key=lambda r: -abs(r['mesh_LOMO'] / r['T_meas_us'] - 1))[:12]
out['worst_lead_cases_LOMO'] = [{'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'], 'n': r['n_shires'],
                                 'family': r['subfamily'], 'err_MM1-v3.2_pct': round(100 * (r['v32_all'] / r['T_meas_us'] - 1), 2),
                                 'err_mesh_pct': round(100 * (r['mesh_LOMO'] / r['T_meas_us'] - 1), 2)} for r in worst]
fc = H['fold_constants']
rng = {}
for k, d in fc.items():
    a = [v[0] for v in d.values()]
    h = [v[1] for v in d.values()]
    rng[k] = {'folds': len(d), 'a_set_min': round(min(a), 4), 'a_set_max': round(max(a), 4), 'a_hop_min': round(min(h), 4),
              'a_hop_max': round(max(h), 4), 'a_set_positive_in': sum(1 for x in a if x > 0), 'a_hop_positive_in': sum(1 for x in h if x > 0)}
out['fold_constants_range'] = rng
nonmask_scope = [r for r in R if r['layout_point'] and not r['MASK']]
fac = [r['mesh_in_sample'] / r['v32_all'] for r in nonmask_scope]
out['non_MASK_scope_points'] = {'n': len(nonmask_scope), 'factor_min': round(min(fac), 4), 'factor_max': round(max(fac), 4)}
lead_sub = [r for r in R if r['lead'] and r['layout_point']]
fl = [r['mesh_in_sample'] / r['v32_all'] for r in lead_sub]
out['lead_subset_factor_range_in_sample'] = {'n': len(fl), 'min': round(min(fl), 4), 'max': round(max(fl), 4)}
json.dump(out, open(os.path.join(L, 'work', 'fit', 'report-mesh.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ('gemmL2x6x10_single_shires',)}, indent=1))
