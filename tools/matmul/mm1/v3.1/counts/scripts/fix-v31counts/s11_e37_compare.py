#!/usr/bin/env python3
"""fix-v31counts (Q217) step 11: the e37 bound (verify-v31counts' finding 2) as counted by E210's committed driver, against the verifier's own
driver and v31-counts' published point (desk; reads JSON, writes work/e37-bound.json + counts/e37-randn-pair0-bound.json).
  G4 (pure desk pool, S2 tile 2 j 47) must be identical in every field to v31-counts' published S2 point e37_02 j 47;
  G7 (the first accumulated op's A from randn.bin) must equal verify-v31counts' G7 on the 11 quantities its driver reports.
The affected shares of E207's two e37 arms are the verifier's layout estimates (its work/compare.json), quoted, not re-derived here.
    /usr/bin/python3 -I -B s11_e37_compare.py <lane dir> <verify-v31counts dir>
"""
import hashlib
import json
import os
import sys

L, VV = sys.argv[1], sys.argv[2]
C = os.path.join(L, 'work', 'counts')
g4 = json.load(open(os.path.join(C, 'e37-bound-G4.json')))['rows']['fp32.e207.e37']['points']
g7 = json.load(open(os.path.join(C, 'e37-bound-G7.json')))['rows']['fp32.e207.e37.randnpair0']['points']
pub = [p for p in json.load(open(os.path.join(C, 'new-fp32-S2.json')))['rows']['fp32.e207.e37']['points'] if p['tile'] == 'e37_02.bin' and p['j'] == 47]
vfile = os.path.join(VV, 'work', 'counts', 'mine.json')
ver = {p['id']: p for p in json.load(open(vfile))['points']}
vcmp_file = os.path.join(VV, 'work', 'compare.json')
vcmp = json.load(open(vcmp_file))['g7']
sc = json.load(open(os.path.join(L, 'work', 'lab', 'tools/claims-v3/e210/desk/switch-counts-e210.json')))
k_lo, k_clk = sc['k_sig_lo'], sc['k_clk']
row = json.load(open(os.path.join(L, 'counts', 'counts-fp32-gemm-states.json')))['shapes']['S2']['e37']['fin_edges_lo']
assert len(g4) == 1 and len(g7) == 1 and len(pub) == 1


def q(p, theirs):
    g = (lambda k: p[k]) if theirs else (lambda k: {'ff_all_clocked': p['ff']['all']['clocked'], 'ff_all_toggles': p['ff']['all']['toggles']}.get(k, p.get(k)))
    return {'vpu_nets_map': p['vpu']['nets_map'], 'vpu_nets_hier': p['vpu']['nets_hier'], 'unit_nets_map': p['unit']['nets_map'],
            'unit_nets_hier': p['unit']['nets_hier'], 'clock_nets_cov': p['clock_nets_cov'], 'ff_all_clocked': g('ff_all_clocked'),
            'ff_all_toggles': g('ff_all_toggles'), 'valid_slots': p['valid_slots'], 'cycles': p['cycles'], 'nets_cov': p['nets_cov'],
            'check_mismatch': p['check_mismatch']}


def fe(p):
    return (p['vpu']['nets_map'] * k_lo + p['clock_nets_cov'] * k_clk) / 4096


g4_same = g4[0] == pub[0]
a7, b7 = q(g7[0], False), q(ver['G7-e37-randnpair0-S2-t2-j47'], True)
a4, b4 = q(g4[0], False), q(ver['G4-e37-S2-t2-j47'], True)
n7 = sum(a7[k] == b7[k] for k in a7)
n4 = sum(a4[k] == b4[k] for k in a4)
f4, f7 = fe(g4[0]), fe(g7[0])
shares = {'b42': 159 / 6144, 'b43': 0.025}
out = {'what': ("fp32 e37: the card's pools (E207 b42 gemmL1x3x2 and b43 gemmL3x5x5) hold randn.bin as pair 0, which the desk pool (61 pure e37 "
                "pairs) leaves out; the effect of one randn product at the start of a C tile's accumulation, counted at S2 tile 2 j 47 (post hoc, desk)"),
       'driver': "tools/claims-v3/e210/desk/count_e210.py (E210's committed driver, unchanged), on v31-counts' binary and maps",
       'G4_pure_e37_fin_edges_lo_a_MAC': f4, 'G7_randn_A_first_fin_edges_lo_a_MAC': f7, 'difference': f7 - f4, 'relative': f7 / f4 - 1,
       'G4_identical_to_v31counts_published_point_e37_02_j47': g4_same,
       'G7_quantities_equal_to_verify_v31counts_driver': f'{n7}/11', 'G4_quantities_equal_to_verify_v31counts_driver': f'{n4}/11',
       'e37_S2_row_fin_edges_lo': row,
       'affected_share_of_op_steps (verify-v31counts layout estimates, quoted)': {
           'b42 gemmL1x3x2: one randn pair in pools of A 4,096 and B 6,144 tiles; 159 of 6,144 C tiles from their first op': shares['b42'],
           'b43 gemmL3x5x5: pools of 8,192 repeat, four randn A and four randn B tiles; about 2.5% of op-steps, layout-dependent': shares['b43']},
       'effect_on_the_e37_S2_row': {k: {'fin_edges_lo_a_MAC': v * (f7 - f4), 'relative': v * (f7 - f4) / row} for k, v in shares.items()},
       'sources': {'verify-v31counts work/compare.json sha256': hashlib.sha256(open(vcmp_file, 'rb').read()).hexdigest(),
                   'verify-v31counts work/counts/mine.json sha256': hashlib.sha256(open(vfile, 'rb').read()).hexdigest(),
                   'verifier_G7_minus_G4': vcmp['difference']},
       'not_counted': "the e37 rows stay pure-e37 counts; a mixture row would need each arm's layout share, which is v3.1's to declare"}
json.dump(out, open(os.path.join(L, 'counts', 'e37-randn-pair0-bound.json'), 'w'), indent=1, sort_keys=True)
print(f"G4 (pure e37) {f4:,.1f}, G7 (randn A first) {f7:,.1f} fin edges lo a MAC: +{f7 - f4:,.1f} ({f7 / f4 - 1:+.1%}); "
      f"G4 {'IDENTICAL' if g4_same else 'NOT IDENTICAL'} to v31-counts' published point; G7 {n7}/11 and G4 {n4}/11 equal to the verifier's driver")
for k, v in out['effect_on_the_e37_S2_row'].items():
    print(f"  {k}: share {shares[k]:.2%} -> {v['fin_edges_lo_a_MAC']:+,.0f} fin edges lo a MAC ({v['relative']:+.2%} of the S2 row {row:,.1f})")
sys.exit(0 if g4_same and n7 == 11 and n4 == 11 else 1)
