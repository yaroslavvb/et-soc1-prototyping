#!/usr/bin/env python3
"""counts-e217 (decl-e217 step 4; counts-e214's s06b with E217's labels) step 6b: this build's re-counts of two committed rows against MM1-v3.1's committed counts (3e8991d0) (desk; JSON only).

The rule was written and hashed before the re-counts ran (work/recount-rule.txt, s06a_recount_rule.py). Point by point (matched by tile
and depth j for fp32, by launch point n0 for fp16 and int8) every numeric leaf the bench reports is compared (bit-equality reported);
the rule's quantities gate the verdict; the row-level numbers (MM1-v1 units) are recomputed from the re-counted means exactly as the
committed tables compute them (fix-v31counts' s04_tables.py arithmetic) and compared with the committed rows.
    /usr/bin/python3 -I -B s06b_compare.py <lane dir>
"""
import hashlib
import json
import os
import sys

L = sys.argv[1]
LAB = os.path.join(L, 'work', 'lab')
CN = os.path.join(LAB, 'tools', 'matmul', 'mm1', 'v3.1', 'counts')
TOL = 1e-3
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}


def j(p):
    return json.load(open(p))


def leaves(o, pre=''):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(leaves(v, f'{pre}.{k}' if pre else k))
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out[pre] = float(o)
    return out


def ratio(a, b):
    return (a / b) if b else (1.0 if a == b else None)


sc = j(os.path.join(LAB, 'tools/claims-v3/e210/desk/switch-counts-e210.json'))
k_lo, k_hi, k_clk = sc['k_sig_lo'], sc['k_sig_hi'], sc['k_clk']
st = j(os.path.join(LAB, 'tools/matmul/mm1/v1/inputs/switch_table.json'))['rows']
c2 = j(os.path.join(LAB, 'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json'))['rows']
r32 = c2['fp32.randn']['mean']
g_zd = 4132.5 / (r32['unit']['nets_map'] / 4096)
g_t = 6494.8 / (r32['unit']['nets_map'] / 4096)
rule_p = os.path.join(L, 'work', 'recount-rule.txt')
res = {'what': "counts-e217 re-counts of two committed rows of MM1-v3.1's counts (3e8991d0) against the committed values (desk)",
       'rule_file': 'recount-rule.txt', 'rule_sha256': hashlib.sha256(open(rule_p, 'rb').read()).hexdigest(), 'tolerance': TOL,
       'checks': {}, 'pass': True}
lines = [res['what'], f"rule (written before the re-counts) sha256 {res['rule_sha256']}"]


def cmp_points(ours, comm, keyf, gate):
    po = {keyf(p): p for p in ours['points']}
    pc = {keyf(p): p for p in comm['points']}
    same = sorted(po) == sorted(pc)
    n_leaf = n_eq = 0
    worst = 0.0
    gate_ok = True
    for k in sorted(set(po) & set(pc)):
        lo, lc = leaves(po[k]), leaves(pc[k])
        for nm in sorted(set(lo) | set(lc)):
            if nm in ('j', 'n0'):
                continue
            n_leaf += 1
            a, b = lo.get(nm), lc.get(nm)
            if a is not None and b is not None and a == b:
                n_eq += 1
            elif a is not None and b is not None and b != 0:
                worst = max(worst, abs(a / b - 1))
            if nm in gate:
                r = ratio(a, b) if (a is not None and b is not None) else None
                if r is None or abs(r - 1) > TOL:
                    gate_ok = False
    return same, n_leaf, n_eq, worst, gate_ok


# (1) fp32 at GEMM states
raw32 = {'S1': j(os.path.join(CN, 'raw', 'new-fp32-S1.json')), 'S2': j(os.path.join(CN, 'raw', 'new-fp32-S2.json'))}
tab32 = j(os.path.join(CN, 'counts-fp32-gemm-states.json'))['shapes']
for s, key, kind, fn in (('S1', 'fp32.e212.fld_mant', 'pattern:fld_mant', 'recount-fp32-S1-fld_mant.json'),
                         ('S2', 'fp32.e212.den8', 'pattern:den8', 'recount-fp32-S2-den8.json')):
    o = j(os.path.join(L, 'work', 'counts', fn))
    ours, comm = o['rows'][key], raw32[s]['rows'][key]
    same, n_leaf, n_eq, worst, gate_ok = cmp_points(ours, comm, lambda p: (p['tile'], p['j']), {'vpu.nets_map', 'clock_nets_cov', 'valid_slots'})
    miss = max(p['check_mismatch'] for p in ours['points'])
    m = ours['mean']
    vpu, clk = m['vpu']['nets_map'] / 4096, m['clock_nets_cov'] / 4096
    mine = {'signal_lo': vpu * k_lo, 'signal_hi': vpu * k_hi, 'clock': clk * k_clk, 'fin_edges_lo': vpu * k_lo + clk * k_clk,
            'fin_edges_hi': vpu * k_hi + clk * k_clk, 'S_signal_lo_per_op': vpu * k_lo * 4096, 'valid_slots': m['valid_slots'] / 4096}
    row = tab32[s][kind]
    rq = {nm: {'ours': v, 'committed': row[nm], 'ratio': ratio(v, row[nm]), 'equal': v == row[nm]} for nm, v in mine.items()}
    row_ok = all(x['ratio'] is not None and abs(x['ratio'] - 1) <= TOL for x in rq.values())
    ok = same and miss == 0 and gate_ok and row_ok and not o.get('incomplete')
    res['checks'][f'fp32_{s}_{kind}'] = {'committed': f'tools/matmul/mm1/v3.1/counts/raw/new-fp32-{s}.json row {key}; counts-fp32-gemm-states.json {s} {kind}',
                                         'n_points': [len(ours['points']), len(comm['points'])], 'same_tiles_and_depths': same,
                                         'check_mismatch_max_ours': miss, 'leaves_compared': n_leaf, 'leaves_bit_equal': n_eq,
                                         'worst_relative_difference': worst, 'gate_quantities_within_tolerance': gate_ok, 'row': rq, 'pass': ok}
    res['pass'] &= ok
    lines.append(f"(1) fp32 {s} {kind}: points {len(ours['points'])}/{len(comm['points'])}, same tiles and depths {same}, check mismatches {miss}; "
                 f"leaves bit-equal {n_eq} of {n_leaf} (worst rel. diff {worst:.3g}); row " +
                 ', '.join(f"{nm} {x['ratio']:.6f}{'' if x['equal'] else ' (not bit-equal)'}" for nm, x in rq.items()) + f" -> {'PASS' if ok else 'FAIL'}")
# (2) launch points
rawL = j(os.path.join(CN, 'raw', 'new-launch.json'))['rows']
tabL = j(os.path.join(CN, 'counts-fp16-int8-launch.json'))['rows']
oL = j(os.path.join(L, 'work', 'counts', 'recount-launch.json'))['rows']
for key, kind in (('int8.int8.e212.i8_pm1__i8_pm1', 'int8.pattern:i8_pm1'), ('fp16.fp16.e212.fld16_mant__fld16_mant', 'fp16.pattern:fld16_mant')):
    fmt = key.split('.')[0]
    ours, comm = oL[key], rawL[key]
    same, n_leaf, n_eq, worst, gate_ok = cmp_points(ours, comm, lambda p: p['n0'], {'vpu.nets_map', 'clock_nets_cov', 'ff.all.clocked'})
    miss = max(p['check_mismatch'] for p in ours['points'])
    miss_c = max(p['check_mismatch'] for p in comm['points'])
    m = ours['mean']
    macs = MACS[fmt]
    vpu, ffc, clkn = m['vpu']['nets_map'], m['ff']['all']['clocked'], m['clock_nets_cov']
    bz = st[f'{fmt}.zeros']['per_mac']['register_bits_clocked']
    bo = st[f'{fmt}.ones']['per_mac']['register_bits_clocked']
    v = min(max((round(ffc / macs, 2) - bz) / (bo - bz), 0.0), 1.0)
    mine = {'signal_lo_zero_delay': round(vpu * g_zd * 14.5), 'signal_hi_timed': round(vpu * g_t * 14.5), 'clock': round(clkn * 39.8),
            'register_bits_clocked_a_MAC': round(ffc / macs, 2), 'valid_share_v': v}
    row = tabL[kind]
    comm_v = {'signal_lo_zero_delay': row['fin_edges_per_op']['signal_lo_zero_delay'], 'signal_hi_timed': row['fin_edges_per_op']['signal_hi_timed'],
              'clock': row['fin_edges_per_op']['clock'], 'register_bits_clocked_a_MAC': row['per_mac']['register_bits_clocked'],
              'valid_share_v': row['valid_share_v']}
    rq = {nm: {'ours': x, 'committed': comm_v[nm], 'ratio': ratio(x, comm_v[nm]), 'equal': x == comm_v[nm]} for nm, x in mine.items()}
    row_ok = all(x['ratio'] is not None and abs(x['ratio'] - 1) <= TOL for x in rq.values())
    ok = same and (miss == 0 if fmt != 'fp16' else miss == miss_c) and gate_ok and row_ok
    res['checks'][f'{kind}_launch_points'] = {'committed': f'tools/matmul/mm1/v3.1/counts/raw/new-launch.json row {key}; counts-fp16-int8-launch.json {kind}',
                                              'launch_points_n0': [p['n0'] for p in ours['points']], 'same_launch_points': same,
                                              'check_mismatch_max_ours': miss, 'check_mismatch_max_committed': miss_c,
                                              'leaves_compared': n_leaf, 'leaves_bit_equal': n_eq, 'worst_relative_difference': worst,
                                              'gate_quantities_within_tolerance': gate_ok, 'row': rq, 'pass': ok}
    res['pass'] &= ok
    lines.append(f"(2) {kind} at the launch points {[p['n0'] for p in ours['points']]}: same points {same}, check mismatches {miss} (committed {miss_c}); "
                 f"leaves bit-equal {n_eq} of {n_leaf} (worst rel. diff {worst:.3g}); row " +
                 ', '.join(f"{nm} {x['ratio']:.6f}{'' if x['equal'] else ' (not bit-equal)'}" for nm, x in rq.items()) + f" -> {'PASS' if ok else 'FAIL'}")
res['k'] = {'k_sig_lo': k_lo, 'k_sig_hi': k_hi, 'k_clk': k_clk, 'g_zd_x14.5': g_zd * 14.5, 'g_t_x14.5': g_t * 14.5}
lines.append(f"VERDICT: {'MATCH (every rule quantity within 0.999-1.001, every check 0 or as committed, same tiles, depths and points)' if res['pass'] else 'NO MATCH: stop, NOT COUNTED'}")
os.makedirs(os.path.join(L, 'counts'), exist_ok=True)
json.dump(res, open(os.path.join(L, 'counts', 'recount-check.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(L, 'counts', 'recount-check.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
sys.exit(0 if res['pass'] else 1)
