#!/usr/bin/env python3
"""lay-contention s12: where each subset configuration's requests are served (descriptive; from work/s03_features.json and the
interleave): per lock step, the lines each L3 home receives (every request goes to one half of the 32 homes, one line of each tile to
each home of that half), the fresh lines each memory shire receives (two lines of each fresh tile to each of the 8), the active shires'
mean and largest mean hop to the 32 homes, and the busiest mesh link's L3-return load; with the runs of the fit set and the E215 rows
that use it. Standard library. Output: work/placement_by_config.csv."""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'out')
LAB = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
F = json.load(open(os.path.join(WORK, 'features_layout.json')))
SHAPE = re.compile(r'^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$')
P = json.load(open(os.path.join(WORK, 'subset_points.json')))
use = {}
for p in P:
    wk = 'rgm136.gemmLnc' if p['arm'].startswith('gemmLnc') else ('rgm211.gemmLn' if p['arm'].startswith('gemmLn') else
                                                                  ('rgm211.gemmL' if p['kernel'] == 'rgm211' else 'rgm136.gemmL'))
    MB, NB, KB = SHAPE.match(p['arm']).groups()
    k = '%s|%sx%sx%s|0x%x' % (wk, MB, NB, KB, int(p['mask'], 16))
    use.setdefault(k, set()).add('%s %s' % (p['exp'], p['card']))
WALK = {'rgm136 gemmL': 'rgm136.gemmL', 'rgm136 gemmLnc': 'rgm136.gemmLnc', 'rgm211 gemmLn': 'rgm211.gemmLn', 'rgm211 gemmL': 'rgm211.gemmL'}
for q in csv.DictReader(open(os.path.join(LAB, 'tools/claims-v3/e215/points-e215.csv'))):
    MB, NB, KB = SHAPE.match(q['arm_token']).groups()
    k = '%s|%sx%sx%s|0x%x' % (WALK[q['loop']], MB, NB, KB, int(q['shire_mask'], 16))
    use.setdefault(k, set()).add('E215 ' + q['id'])
rows = []
for k, f in sorted(F.items()):
    wk, shp, mask = k.split('|')
    full = F['%s|%s|0xffffffff' % (wk, shp)]
    rows.append({'kernel': wk, 'shape': shp, 'mask': mask, 'n': f['n'], 'R': f['R'], 'C': f['C'], 'footprint_MB': f['footprint_MB'],
                 'lines_per_home_per_step': f['lines_req_step'] / 16.0, 'fresh_lines_per_step': f['fresh_lines_step'],
                 'fresh_lines_per_memory_shire_per_step': f['fresh_lines_step'] / 8.0,
                 'fresh_share_of_requests': round(f['fresh_lines_step'] / f['lines_req_step'], 6),
                 'full_chip_fresh_share': round(full['fresh_lines_step'] / full['lines_req_step'], 6),
                 'hop_mean_to_homes': round(f['mesh_hop_mean'], 4), 'hop_max_to_homes': round(f['mesh_hop_max'], 4),
                 'busiest_link_lines_per_step': f['mesh_link_max_lines'], 'fanw': round(f['fanw'], 4),
                 'used_by': '; '.join(sorted(use.get(k, [])))})
with open(os.path.join(WORK, 'placement_by_config.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator='\n')
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'configurations;', sum(1 for r in rows if r['used_by']), 'used by a run or an E215 row')
