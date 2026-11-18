#!/usr/bin/env python3
"""fix-v31counts (Q217) step 3: the re-count of fp32 real:blind4 at S2 against what it must reproduce (desk; reads JSON, writes JSON + text).
  (1) its 4 file-0 points (fp32.real_pythia_embed_qkv measured) against v31-counts' published S2 points (same tile, same j): every field of
      the point, compared whole (same binary, maps, driver and tiles, so they must be identical);
  (2) its 4 file-1 points (fp32.real_qwen_q_down measured) against verify-v31counts' own driver at the same j (its work/counts/mine2.json):
      the 11 quantities that driver reports;
  (3) the row in MM1-v1 units (E210's k off the committed switch-counts-e210.json), old (file 0 only) and new (both files), beside S1.
    /usr/bin/python3 -I -B s03_compare.py <lane dir> <verify-v31counts dir>
"""
import json
import os
import sys

L, VV = sys.argv[1], sys.argv[2]
C = os.path.join(L, 'work', 'counts')
new = json.load(open(os.path.join(C, 'recount-fp32-S2-real_blind4.json')))
old = json.load(open(os.path.join(C, 'new-fp32-S2.json')))
s1 = json.load(open(os.path.join(C, 'new-fp32-S1.json')))
ver = json.load(open(os.path.join(VV, 'work', 'counts', 'mine2.json')))
sc = json.load(open(os.path.join(L, 'work', 'lab', 'tools/claims-v3/e210/desk/switch-counts-e210.json')))
K = 'fp32.e207.real_blind4'
F0, F1 = 'fp32.real_pythia_embed_qkv.bin', 'fp32.real_qwen_q_down.bin'
k_lo, k_hi, k_clk = sc['k_sig_lo'], sc['k_sig_hi'], sc['k_clk']
npts = new['rows'][K]['points']
out = {'what': 'fix-v31counts: the S2 re-count of fp32 real:blind4 (both files) against v31-counts and verify-v31counts', 'k': [k_lo, k_hi, k_clk],
       'incomplete': new.get('incomplete'), 'file0_vs_v31counts': [], 'file1_vs_verifier': [], 'rows': {}}
lines = []
ok = True
# (1) file 0 against v31-counts' published S2 points
for p in [q for q in npts if q['tile'] == F0]:
    o = [q for q in old['rows'][K]['points'] if q['tile'] == F0 and q['j'] == p['j']]
    same = bool(o) and o[0] == p
    ok &= same
    out['file0_vs_v31counts'].append({'j': p['j'], 'identical': same})
    lines.append(f"file 0 j {p['j']:3d}: {'IDENTICAL' if same else 'DIFFERS'} to v31-counts' published S2 point (every field)")
# (2) file 1 against the verifier's driver
vp = {q['j']: q for q in ver['points'] if q['tile'] == F1}


def q11(p, theirs):
    if theirs:
        return {'vpu_nets_map': p['vpu']['nets_map'], 'vpu_nets_hier': p['vpu']['nets_hier'], 'unit_nets_map': p['unit']['nets_map'],
                'unit_nets_hier': p['unit']['nets_hier'], 'clock_nets_cov': p['clock_nets_cov'], 'ff_all_clocked': p['ff_all_clocked'],
                'ff_all_toggles': p['ff_all_toggles'], 'valid_slots': p['valid_slots'], 'cycles': p['cycles'], 'nets_cov': p['nets_cov'],
                'check_mismatch': p['check_mismatch']}
    return {'vpu_nets_map': p['vpu']['nets_map'], 'vpu_nets_hier': p['vpu']['nets_hier'], 'unit_nets_map': p['unit']['nets_map'],
            'unit_nets_hier': p['unit']['nets_hier'], 'clock_nets_cov': p['clock_nets_cov'], 'ff_all_clocked': p['ff']['all']['clocked'],
            'ff_all_toggles': p['ff']['all']['toggles'], 'valid_slots': p['valid_slots'], 'cycles': p['cycles'], 'nets_cov': p['nets_cov'],
            'check_mismatch': p['check_mismatch']}


for p in [q for q in npts if q['tile'] == F1]:
    a, b = q11(p, False), (q11(vp[p['j']], True) if p['j'] in vp else None)
    neq = {k: (a[k], b[k]) for k in a if b is None or a[k] != b[k]}
    ok &= (b is not None and not neq)
    out['file1_vs_verifier'].append({'j': p['j'], 'n_equal': 11 - len(neq), 'not_equal': neq})
    lines.append(f"file 1 j {p['j']:3d}: {11 - len(neq)}/11 quantities equal to verify-v31counts' driver" + (f' (differs: {neq})' if neq else ''))


def row(pts):
    n = len(pts)
    vpu = sum(p['vpu']['nets_map'] for p in pts) / n / 4096
    clk = sum(p['clock_nets_cov'] for p in pts) / n / 4096
    lo = vpu * k_lo + clk * k_clk
    return {'n_points': n, 'tiles': sorted({p['tile'] for p in pts}), 'vpu_nets_map_per_mac': vpu, 'clock_nets_per_mac': clk,
            'signal_lo': vpu * k_lo, 'fin_edges_lo': lo, 'fin_edges_hi': vpu * k_hi + clk * k_clk, 'S_signal_lo_per_op': vpu * k_lo * 4096,
            'check_mismatch_max': max(p['check_mismatch'] for p in pts)}


rs = {'S2 published (file 0 only, 4 points)': row(old['rows'][K]['points']), 'S2 re-count file 0 (4 points)': row([q for q in npts if q['tile'] == F0]),
      'S2 re-count file 1 (4 points)': row([q for q in npts if q['tile'] == F1]), 'S2 re-count both files (8 points)': row(npts),
      'S1 published (both files, 8 points)': row(s1['rows'][K]['points']),
      'S1 file 0 (4 points)': row([q for q in s1['rows'][K]['points'] if q['tile'] == F0]),
      'S1 file 1 (4 points)': row([q for q in s1['rows'][K]['points'] if q['tile'] == F1])}
out['rows'] = rs
a, b = rs['S2 published (file 0 only, 4 points)'], rs['S2 re-count both files (8 points)']
out['published_over_fixed'] = {'fin_edges_lo': a['fin_edges_lo'] / b['fin_edges_lo'] - 1, 'S_signal_lo_per_op': a['S_signal_lo_per_op'] / b['S_signal_lo_per_op'] - 1}
lines.append('rows (fin edges lo a MAC; S = signal lo an op):')
for nm, r in rs.items():
    lines.append(f"  {nm:40s} {r['fin_edges_lo']:10,.1f}  S {r['S_signal_lo_per_op']:13,.0f}  vpu_map/MAC {r['vpu_nets_map_per_mac']:8.2f}  clk/MAC {r['clock_nets_per_mac']:7.3f}  miss {r['check_mismatch_max']}")
lines.append(f"published S2 over the fixed S2: fin edges lo {out['published_over_fixed']['fin_edges_lo']:+.2%}, S {out['published_over_fixed']['S_signal_lo_per_op']:+.2%}")
f0, f1 = rs['S1 file 0 (4 points)']['fin_edges_lo'], rs['S1 file 1 (4 points)']['fin_edges_lo']
g0, g1 = rs['S2 re-count file 0 (4 points)']['fin_edges_lo'], rs['S2 re-count file 1 (4 points)']['fin_edges_lo']
out['file_and_depth'] = {'S1 file0/file1': f0 / f1 - 1, 'S2 file0/file1': g0 / g1 - 1, 'file0 S2/S1': g0 / f0 - 1, 'file1 S2/S1': g1 / f1 - 1,
                         'both S2/S1': b['fin_edges_lo'] / rs['S1 published (both files, 8 points)']['fin_edges_lo'] - 1}
lines.append('file and depth: ' + ', '.join(f'{k} {v:+.2%}' for k, v in out['file_and_depth'].items()))
out['verdict'] = 'REPRODUCED' if ok and not new.get('incomplete') else 'NOT REPRODUCED'
lines.append(f"VERDICT {out['verdict']} (file 0 identical to v31-counts' points and file 1 equal to the verifier's on every quantity; incomplete {new.get('incomplete') or 'none'})")
json.dump(out, open(os.path.join(L, 'work', 'recount-compare.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(L, 'work', 'recount-compare.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(0 if out['verdict'] == 'REPRODUCED' else 1)
