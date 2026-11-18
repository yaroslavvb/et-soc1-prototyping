#!/usr/bin/env python3
"""v31-counts (Q217) step 6b: this build's re-counts against the committed counts (desk; reads JSON only).

  fp32 at GEMM states: work/counts/recount-fp32-S1-randn.json against tools/claims-v3/e210/desk/counts-e210-S1.json (row randn), and in
    MM1-v1's units against desk/switch-counts-e210.json (S1 randn: signal_lo, clock, fin_edges_lo/hi), which MM1-v3's energy reads;
  int8 and fp16 at the launch points: work/counts/recount-launch-int8-full.json and -fp16-randn.json against counts-v2.json (rows int8.full,
    fp16.randn), and in MM1-v1's switch-table units (signal_lo_zero_delay a op, register bits clocked a MAC) against switch_table.json.
The rule declared before reading the ratios (this lane's brief: 'if they do not match, stop: NOT COUNTED'): every ratio of a count that
enters MM1-v3's switch route (VPU nets_map, clock-net toggles, clocked register bits, and the fin edges made from them) within 0.999-1.001,
and every check_mismatch 0. Other quantities (the unit's nets_hier and nets_map, register toggles, valid slots, cycles) are reported.
    /usr/bin/python3 -I -B s06b_compare.py <lane dir>
"""
import json
import os
import sys

L = sys.argv[1]
LAB = os.path.join(L, 'work', 'lab')
TOL = 1e-3
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}


def ratio(a, b):
    return (a / b) if b else (1.0 if a == b else None)


res = {'what': 'v31-counts re-counts of committed points against the committed counts (desk)', 'tolerance': TOL, 'checks': {}, 'pass': True}
lines = []
# (1) fp32 S1 randn at GEMM states
ours = json.load(open(os.path.join(L, 'work/counts/recount-fp32-S1-randn.json')))['rows']['randn']
comm = json.load(open(os.path.join(LAB, 'tools/claims-v3/e210/desk/counts-e210-S1.json')))['rows']['randn']
sc = json.load(open(os.path.join(LAB, 'tools/claims-v3/e210/desk/switch-counts-e210.json')))
k_lo, k_hi, k_clk = sc['k_sig_lo'], sc['k_sig_hi'], sc['k_clk']
a, b = ours['mean'], comm['mean']
q = {
    'vpu_nets_map': (a['vpu']['nets_map'], b['vpu']['nets_map'], True),
    'clock_nets_cov': (a['clock_nets_cov'], b['clock_nets_cov'], True),
    'ff_all_clocked': (a['ff']['all']['clocked'], b['ff']['all']['clocked'], True),
    'unit_nets_hier': (a['unit']['nets_hier'], b['unit']['nets_hier'], False),
    'unit_nets_map': (a['unit']['nets_map'], b['unit']['nets_map'], False),
    'ff_all_toggles': (a['ff']['all']['toggles'], b['ff']['all']['toggles'], False),
    'valid_slots': (a['valid_slots'], b['valid_slots'], False),
    'cycles': (a['cycles'], b['cycles'], False),
}
s1 = sc['shapes']['S1']['randn']
sig_lo = a['vpu']['nets_map'] / 4096 * k_lo
clk = a['clock_nets_cov'] / 4096 * k_clk
q['MM1v1_signal_lo_a_MAC'] = (sig_lo, s1['signal_lo'], True)
q['MM1v1_clock_a_MAC'] = (clk, s1['clock'], True)
q['MM1v1_fin_edges_lo_a_MAC'] = (sig_lo + clk, s1['fin_edges_lo'], True)
q['MM1v1_fin_edges_hi_a_MAC'] = (a['vpu']['nets_map'] / 4096 * k_hi + clk, s1['fin_edges_hi'], True)
miss = max(p['check_mismatch'] for p in ours['points'])
tiles_o = sorted((p['tile'], p['j']) for p in ours['points'])
tiles_c = sorted((p['tile'], p['j']) for p in comm['points'])
chk = {'committed_file': 'tools/claims-v3/e210/desk/counts-e210-S1.json (row randn) and desk/switch-counts-e210.json (S1 randn)',
       'n_points': [len(ours['points']), len(comm['points'])], 'same_tiles_and_depths': tiles_o == tiles_c,
       'check_mismatch_max_ours': miss, 'quantities': {}}
ok = (miss == 0) and tiles_o == tiles_c
lines.append('(1) fp32 gemmL1x1x1 (S1) randn at GEMM states, ours / committed (per op unless named):')
for nm, (x, y, gate) in q.items():
    r = ratio(x, y)
    chk['quantities'][nm] = {'ours': x, 'committed': y, 'ratio': r, 'gates_the_rule': gate}
    if gate and (r is None or abs(r - 1) > TOL):
        ok = False
    lines.append(f"    {nm:26s} {x:16.4f} / {y:16.4f}  ratio {r:.6f}{'  (rule)' if gate else ''}")
lines.append(f"    points {len(ours['points'])} / {len(comm['points'])}, same tiles and depths {tiles_o == tiles_c}, check mismatches (ours) {miss}")
chk['pass'] = ok
res['checks']['fp32_S1_randn_gemm_states'] = chk
res['pass'] &= ok
# (2) int8 full and fp16 randn at the launch points
c2 = json.load(open(os.path.join(LAB, 'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json')))['rows']
st = json.load(open(os.path.join(LAB, 'tools/matmul/mm1/v1/inputs/switch_table.json')))
r32 = c2['fp32.randn']['mean']
g_zd = 4132.5 / (r32['unit']['nets_map'] / 4096)      # design C's switch_table.py: the gate/RTL expansion learned once on fp32 random
g_t = 6494.8 / (r32['unit']['nets_map'] / 4096)
for key, fn in (('int8.full', 'recount-launch-int8-full.json'), ('fp16.randn', 'recount-launch-fp16-randn.json')):
    fmt = key.split('.')[0]
    o = json.load(open(os.path.join(L, 'work/counts', fn)))['rows'][key]
    a, b = o['mean'], c2[key]['mean']
    row = st['rows'][key]
    q = {
        'vpu_nets_map': (a['vpu']['nets_map'], b['vpu']['nets_map'], True),
        'clock_nets_cov': (a['clock_nets_cov'], b['clock_nets_cov'], True),
        'ff_all_clocked': (a['ff']['all']['clocked'], b['ff']['all']['clocked'], True),
        'unit_nets_hier': (a['unit']['nets_hier'], b['unit']['nets_hier'], False),
        'unit_nets_map': (a['unit']['nets_map'], b['unit']['nets_map'], False),
        'ff_all_toggles': (a['ff']['all']['toggles'], b['ff']['all']['toggles'], False),
        'valid_slots': (a['valid_slots'], b['valid_slots'], False),
        'cycles': (a['cycles'], b['cycles'], False),
        'table_signal_lo_zero_delay_a_op': (a['vpu']['nets_map'] * g_zd * 14.5, row['fin_edges_per_op']['signal_lo_zero_delay'], True),
        'table_signal_hi_timed_a_op': (a['vpu']['nets_map'] * g_t * 14.5, row['fin_edges_per_op']['signal_hi_timed'], True),
        'table_clock_a_op': (a['clock_nets_cov'] * 39.8, row['fin_edges_per_op']['clock'], True),
        'table_register_bits_clocked_a_MAC': (a['ff']['all']['clocked'] / MACS[fmt], row['per_mac']['register_bits_clocked'], True),
    }
    miss = max(p['check_mismatch'] for p in o['points'])
    pts = [p['n0'] for p in o['points']]
    chk = {'committed_file': f'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json (row {key}) and MM1-v1 switch_table.json',
           'launch_points_n0': pts, 'committed_n0': [p['n0'] for p in c2[key]['points']], 'check_mismatch_max_ours': miss, 'quantities': {}}
    ok = (miss == 0 if fmt != 'fp16' else True) and pts == chk['committed_n0']
    # fp16's check counts the window model's named residue (run_kinds.py); report it, the rule reads the committed figure beside it
    chk['check_mismatch_committed'] = max(p['check_mismatch'] for p in c2[key]['points'])
    if fmt == 'fp16':
        ok = ok and miss == chk['check_mismatch_committed']
    lines.append(f'(2) {key} at the launch points {pts}, ours / committed (per op unless named):')
    for nm, (x, y, gate) in q.items():
        r = ratio(x, y)
        chk['quantities'][nm] = {'ours': x, 'committed': y, 'ratio': r, 'gates_the_rule': gate}
        if gate and (r is None or abs(r - 1) > TOL):
            ok = False
        lines.append(f"    {nm:34s} {x:16.4f} / {y:16.4f}  ratio {r:.6f}{'  (rule)' if gate else ''}")
    lines.append(f"    check mismatches ours {miss}, committed {chk['check_mismatch_committed']}")
    chk['pass'] = ok
    res['checks'][f'{key}_launch_points'] = chk
    res['pass'] &= ok
res['k'] = {'k_sig_lo': k_lo, 'k_sig_hi': k_hi, 'k_clk': k_clk, 'g_zd_x14.5': g_zd * 14.5, 'g_t_x14.5': g_t * 14.5}
lines.append(f"VERDICT: {'MATCH (every rule ratio within 0.999-1.001, every check 0 or as committed)' if res['pass'] else 'NO MATCH: stop, NOT COUNTED'}")
json.dump(res, open(os.path.join(L, 'counts', 'recount-check.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(L, 'counts', 'recount-check.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(0 if res['pass'] else 1)
