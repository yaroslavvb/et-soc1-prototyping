#!/usr/bin/env python3
"""v31-counts (Q217) step 9: the new counts in MM1-v3's committed units and footings (desk arithmetic on this lane's bench outputs).

fp32, at a GEMM's accumulator states (E210's definition, switch_counts_e210.py, to the last digit):
    signal fin edges a MAC = VPU nets_map a MAC x k_sig (lo: zero delay; hi: timed), clock fin edges a MAC = clock-net toggles a MAC x k_clk,
    k read off MM1-v1's frozen switch table (fp32 randn row): k_sig_lo 32.9949, k_sig_hi 51.8560, k_clk 39.8000. MM1-v3's energy_v3.counts()
    reads S = signal_lo x 4,096 an op and the valid share v = valid slots a MAC (rows keyed by the kind as MM1-v3's data names it).
fp16 and int8, at the harness's launch points (MM1-v1's switch table: design C's switch_table.py, its formula exactly):
    signal_lo_zero_delay an op = VPU nets_map an op x g_zd x 14.5, signal_hi_timed = x g_t x 14.5, clock = clock-net toggles an op x 39.8, with
    g_zd = 4,132.5 and g_t = 6,494.8 gate toggles a random fp32 MAC over the committed counts-v2.json fp32 randn unit nets_map a MAC; values
    rounded as the table rounds them. MM1-v3's counts() reads S = signal_lo_zero_delay and v = (register bits clocked a MAC - zeros') /
    (ones' - zeros') from the committed table's zeros and ones rows, clipped to [0, 1]. A pooled kind (the card's pool cycles its tiles) is
    the mean over its tiles of each raw per-op count, then converted.
Writes counts/: counts-fp32-gemm-states.json, counts-fp16-int8-launch.json, counts-v31.csv, counts-v31-tiles.csv, crosscheck-launch-fp32.json/.txt
    /usr/bin/python3 -I -B s09_tables.py <lane dir>
"""
import csv
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory as I  # noqa: E402

LAB = os.path.join(L, 'work', 'lab')
C = os.path.join(L, 'work', 'counts')
OUT = os.path.join(L, 'counts')
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}
FOOT = {   # MM1-v3's COUNT_FOOTING (tools/matmul/mm1/v3/mm1_v3.py), verbatim
    'fp32': ("counted (desk): the gate-level bench's VPU net toggles a MAC at GEMM states x the fin edges a toggle calibrated on the fp32 "
             "unit's gate-level run (E210, MM1-v1 units)"),
    'fp16': ("estimated (desk), not counted: fp16's RTL toggles x the fp32 gate/RTL ratio (no fp16 gate-level run; MM1-v1's switch table "
             "footing)"),
    'int8': ("counted (desk) around the arithmetic only: the behavioural RTL has no nets inside the int8 multiply, product sum and add, so "
             "the count is the VPU around them (MM1-v1's switch table footing); m_int8 scales it to the data term the card shows"),
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def j(p):
    return json.load(open(p))


sc = j(os.path.join(LAB, 'tools/claims-v3/e210/desk/switch-counts-e210.json'))
k_lo, k_hi, k_clk = sc['k_sig_lo'], sc['k_sig_hi'], sc['k_clk']
st = j(os.path.join(LAB, 'tools/matmul/mm1/v1/inputs/switch_table.json'))['rows']
c2 = j(os.path.join(LAB, 'docs/reports/data/2026-11-01-q132-rtl-bench/counts-v2.json'))['rows']
r32 = c2['fp32.randn']['mean']
g_zd = 4132.5 / (r32['unit']['nets_map'] / 4096)
g_t = 6494.8 / (r32['unit']['nets_map'] / 4096)
tinv = j(os.path.join(L, 'work', 'tiles-inventory.json'))
benchsrc = sha(os.path.join(L, 'work', 'bench-src.sha256'))
coremf = sha(os.path.join(L, 'work', 'core-et-copy.sha256'))
SRC = {'bench': 'rtl-sim/fma_toggle_v2 at GitHub main 6efdb002 (vpu_top, -fno-dfg; Verilator 5.042; the Makefile copy -j 10 -> -j 2)',
       'bench_sources_manifest_sha256': benchsrc, 'core_et': 'b38a1a31 (rtl, dv/inc, extern copied)', 'core_et_manifest_sha256': coremf}

fp32 = {'S1': j(os.path.join(C, 'new-fp32-S1.json')), 'S2': j(os.path.join(C, 'new-fp32-S2.json'))}
lau = j(os.path.join(C, 'new-launch.json'))['rows']
problems = []
for s, d in fp32.items():
    if d.get('incomplete'):
        problems.append(f'fp32 {s} incomplete: {d["incomplete"]}')

out32 = {'what': ('v31-counts (Q217) desk switch counts (MM1-v1 units) at GEMM accumulator states for fp32 kinds with no committed count; desk '
                  'inputs, not measurements'),
         'definition': sc['definition'], 'k_sig_lo': k_lo, 'k_sig_hi': k_hi, 'k_clk': k_clk,
         'driver': "tools/claims-v3/e210/desk/count_e210.py (E210's committed driver, unchanged): S1 j 3, 11, 19, 27 tiles 0, 1; S2 j 15, 47, 79, 111 tile 2",
         'counts_footing': FOOT['fp32'], 'sources': SRC, 'python': sys.version.split()[0], 'shapes': {'S1': {}, 'S2': {}}}
csv_rows, tile_rows = [], []
for k in I.KINDS:
    if k['fmt'] != 'fp32':
        continue
    for s in ('S1', 'S2'):
        rr = fp32[s]['rows'].get(k['key'])
        if rr is None:
            problems.append(f"fp32 {s} {k['key']}: no row")
            continue
        m = rr['mean']
        pts = rr['points']
        vpu = m['vpu']['nets_map'] / 4096
        clk = m['clock_nets_cov'] / 4096
        sig_lo, sig_hi, c = vpu * k_lo, vpu * k_hi, clk * k_clk
        rnd = sc['shapes'][s]['randn']
        row = {'key': k['key'], 'mm1_v3_kind': k['mm1_v3_kind'], 'group': k['group'], 'gen': k['gen'],
               'tiles': [os.path.basename(p) for p in k['files']] if len(k['files']) <= 8 else f"{len(k['files'])} desk tiles",
               'tiles_sha256': ({os.path.basename(p): tinv[p]['sha256'] for p in k['files']} if len(k['files']) <= 8 else
                                {'list_sha256 (work/dsk/tiles-made.sha256)': sha(os.path.join(L, 'work', 'dsk', 'tiles-made.sha256'))}),
               'n_points': len(pts), 'check_mismatch_max': max(p['check_mismatch'] for p in pts),
               'fin_edges_lo': sig_lo + c, 'fin_edges_hi': sig_hi + c, 'signal_lo': sig_lo, 'signal_hi': sig_hi, 'clock': c,
               'vpu_nets_map': vpu, 'clock_nets': clk, 'unit_nets_hier': m['unit']['nets_hier'] / 4096, 'unit_nets_map': m['unit']['nets_map'] / 4096,
               'valid_slots': m['valid_slots'] / 4096, 'clocked_bits': m['ff']['all']['clocked'] / 4096,
               'vpu_nets_map_min_max': [min(p['vpu']['nets_map'] for p in pts) / 4096, max(p['vpu']['nets_map'] for p in pts) / 4096],
               'minus_randn_lo': sig_lo + c - rnd['fin_edges_lo'], 'minus_randn_hi': sig_hi + c - rnd['fin_edges_hi'],
               'S_signal_lo_per_op': sig_lo * 4096, 'counts_footing': FOOT['fp32'],
               'counts_source': f"v31-counts' desk counts at GEMM states ({'S1, KB = 1' if s == 'S1' else 'S2, KB >= 2'})"}
        out32['shapes'][s][k['mm1_v3_kind']] = row
        csv_rows.append({'key': k['key'], 'group': k['group'], 'fmt': 'fp32', 'mm1_v3_kind': k['mm1_v3_kind'],
                         'footing_class': f"{s} (GEMM states, {'KB 1' if s == 'S1' else 'KB >= 2'})", 'n_tiles': len(k['files']), 'n_points': len(pts),
                         'check_mismatch_max': row['check_mismatch_max'], 'S_signal_lo_per_op': round(row['S_signal_lo_per_op'], 1),
                         'signal_lo_per_mac': round(sig_lo, 3), 'signal_hi_per_mac': round(sig_hi, 3), 'clock_per_mac': round(c, 3),
                         'fin_edges_lo_per_mac': round(sig_lo + c, 3), 'fin_edges_hi_per_mac': round(sig_hi + c, 3),
                         'valid_share': round(row['valid_slots'], 6), 'clocked_bits_per_mac': round(row['clocked_bits'], 3),
                         'vpu_nets_map_per_mac': round(vpu, 3), 'unit_nets_hier_per_mac': round(row['unit_nets_hier'], 3),
                         'minus_committed_random_lo_per_mac': round(row['minus_randn_lo'], 3), 'counts_footing': FOOT['fp32'],
                         'tiles': ';'.join(row['tiles']) if isinstance(row['tiles'], list) else row['tiles'],
                         'tiles_sha256_16': ';'.join(v[:16] for v in row['tiles_sha256'].values()), 'bench_sources_manifest_sha256': benchsrc})

# fp16 and int8 at the launch points (switch-table rows), per tile and pooled
def table_row(m, macs, fmt):
    cyc = m['cycles']
    unit = m['unit']['nets_map']
    vpu = m['vpu']['nets_map']
    ffc = m['ff']['all']['clocked']
    fft = m['ff']['all']['toggles']
    clkn = m['clock_nets_cov']
    sig_lo, sig_hi, clk_f = vpu * g_zd * 14.5, vpu * g_t * 14.5, clkn * 39.8
    bz = st[f'{fmt}.zeros']['per_mac']['register_bits_clocked']
    bo = st[f'{fmt}.ones']['per_mac']['register_bits_clocked']
    v = (round(ffc / macs, 2) - bz) / (bo - bz)
    return {'macs_per_op': macs, 'cycles': cyc, 'rtl_unit_net_toggles': unit, 'rtl_vpu_net_toggles': vpu, 'register_bits_clocked': ffc,
            'register_bits_toggled': fft, 'clock_net_toggles': clkn,
            'per_mac': {'rtl_vpu_net_toggles': round(vpu / macs, 2), 'register_bits_clocked': round(ffc / macs, 2), 'clock_net_toggles': round(clkn / macs, 2)},
            'per_cycle': {'register_bits_clocked': round(ffc / cyc, 1), 'clock_net_toggles': round(clkn / cyc, 1)},
            'fin_edges_per_op': {'signal_lo_zero_delay': round(sig_lo), 'signal_hi_timed': round(sig_hi), 'clock': round(clk_f)},
            'fin_edges_per_mac': {'lo': round((sig_lo + clk_f) / macs), 'hi': round((sig_hi + clk_f) / macs)},
            'valid_share_v': min(max(v, 0.0), 1.0), 'valid_share_v_unclipped': v, 'footing': FOOT[fmt], 'counts_footing': FOOT[fmt]}


def avg(objs):
    if isinstance(objs[0], dict):
        return {k: avg([o.get(k, 0) for o in objs]) for k in objs[0]}
    return sum(objs) / len(objs)


outL = {'what': ("v31-counts (Q217) desk counts at the harness's launch points (run_kinds.py) for fp16 and int8 kinds with no committed count, "
                 "in MM1-v1's switch-table form (design C's switch_table.py formula); desk inputs, not measurements"),
        'formula': 'signal_lo_zero_delay = VPU nets_map an op x g_zd x 14.5; signal_hi_timed = x g_t x 14.5; clock = clock-net toggles x 39.8',
        'gate_per_rtl_toggle': {'zero_delay': g_zd, 'timed': g_t,
                                'from': 'counts-v2.json fp32.randn unit nets_map a MAC (committed), 4,132.5 and 6,494.8 gate toggles a random fp32 MAC'},
        'valid_share_v': "(register bits clocked a MAC - the committed table's zeros row) / (ones row - zeros row), clipped to [0, 1], as energy_v3.counts()",
        'launch_points_n0': {'fp16': [91575, 274725, 457875], 'int8': [157232, 471698, 786163]},
        'sources': SRC, 'python': sys.version.split()[0], 'rows': {}, 'tiles': {}}
for k in I.KINDS:
    if k['fmt'] == 'fp32':
        continue
    fmt = k['fmt']
    means, pts_all = [], []
    for p in k['files']:
        nm = f"{fmt}.{k['key']}__{os.path.basename(p)[:-4]}"
        rr = lau.get(nm)
        if rr is None:
            problems.append(f'launch {nm}: no row')
            continue
        means.append(rr['mean'])
        pts_all += rr['points']
        t = table_row(rr['mean'], MACS[fmt], fmt)
        t.update({'tile': os.path.basename(p), 'tile_sha256': tinv[p]['sha256'], 'n_points': len(rr['points']),
                  'check_mismatch_max': max(q['check_mismatch'] for q in rr['points']), 'kind_key': k['key']})
        outL['tiles'][nm] = t
        tile_rows.append({'kind_key': k['key'], 'fmt': fmt, 'tile': os.path.basename(p), 'tile_sha256_16': tinv[p]['sha256'][:16], 'n_points': len(rr['points']),
                          'check_mismatch_max': t['check_mismatch_max'], 'S_signal_lo_per_op': t['fin_edges_per_op']['signal_lo_zero_delay'],
                          'signal_hi_per_op': t['fin_edges_per_op']['signal_hi_timed'], 'clock_per_op': t['fin_edges_per_op']['clock'],
                          'fin_edges_lo_per_mac': t['fin_edges_per_mac']['lo'], 'fin_edges_hi_per_mac': t['fin_edges_per_mac']['hi'],
                          'register_bits_clocked_per_mac': t['per_mac']['register_bits_clocked'], 'valid_share_v': round(t['valid_share_v'], 6),
                          'vpu_nets_per_mac': t['per_mac']['rtl_vpu_net_toggles']})
    if len(means) != len(k['files']):
        continue
    t = table_row(avg(means), MACS[fmt], fmt)
    t.update({'kind_key': k['key'], 'mm1_v3_kind': k['mm1_v3_kind'], 'group': k['group'], 'gen': k['gen'], 'n_tiles': len(k['files']),
              'tiles': [os.path.basename(p) for p in k['files']], 'tiles_sha256': {os.path.basename(p): tinv[p]['sha256'] for p in k['files']},
              'n_points': len(pts_all), 'check_mismatch_max': max(q['check_mismatch'] for q in pts_all),
              'counts_source': "v31-counts' desk counts at the harness launch points (run_kinds.py; MM1-v1's switch table form)"})
    outL['rows'][f"{fmt}.{k['mm1_v3_kind']}"] = t
    csv_rows.append({'key': k['key'], 'group': k['group'], 'fmt': fmt, 'mm1_v3_kind': k['mm1_v3_kind'], 'footing_class': 'launch points (switch-table form)',
                     'n_tiles': len(k['files']), 'n_points': len(pts_all), 'check_mismatch_max': t['check_mismatch_max'],
                     'S_signal_lo_per_op': t['fin_edges_per_op']['signal_lo_zero_delay'],
                     'signal_lo_per_mac': round(t['fin_edges_per_op']['signal_lo_zero_delay'] / MACS[fmt], 3),
                     'signal_hi_per_mac': round(t['fin_edges_per_op']['signal_hi_timed'] / MACS[fmt], 3),
                     'clock_per_mac': round(t['fin_edges_per_op']['clock'] / MACS[fmt], 3),
                     'fin_edges_lo_per_mac': t['fin_edges_per_mac']['lo'], 'fin_edges_hi_per_mac': t['fin_edges_per_mac']['hi'],
                     'valid_share': round(t['valid_share_v'], 6), 'clocked_bits_per_mac': t['per_mac']['register_bits_clocked'],
                     'vpu_nets_map_per_mac': t['per_mac']['rtl_vpu_net_toggles'], 'unit_nets_hier_per_mac': round(avg(means)['unit']['nets_hier'] / MACS[fmt], 3),
                     'minus_committed_random_lo_per_mac': round((t['fin_edges_per_op']['signal_lo_zero_delay'] + t['fin_edges_per_op']['clock']) / MACS[fmt]
                                                                - st[f"{fmt}.{'randn' if fmt == 'fp16' else 'full'}"]['fin_edges_per_mac']['lo'], 3),
                     'counts_footing': FOOT[fmt], 'tiles': ';'.join(t['tiles']),
                     'tiles_sha256_16': ';'.join(v[:16] for v in t['tiles_sha256'].values()), 'bench_sources_manifest_sha256': benchsrc})

# the fp32 cross-checks at the launch points (committed in counts-v2.json): ours / committed
xc = {'what': ("fp32 kinds byte-equal to E212's tiles of the same names, re-counted at the launch points against the committed counts-v2.json "
               '(a third check of this build; not new counts)'), 'rows': {}}
xl = []
for fmt, nm in I.XCHECK:
    o = lau.get(f'{fmt}.xcheck.{nm}')
    cm = c2.get(f'{fmt}.{nm}')
    if o is None or cm is None:
        problems.append(f'xcheck {fmt}.{nm} missing')
        continue
    a, b = o['mean'], cm['mean']
    q = {'vpu_nets_map': (a['vpu']['nets_map'], b['vpu']['nets_map']), 'clock_nets_cov': (a['clock_nets_cov'], b['clock_nets_cov']),
         'ff_all_clocked': (a['ff']['all']['clocked'], b['ff']['all']['clocked']), 'unit_nets_hier': (a['unit']['nets_hier'], b['unit']['nets_hier']),
         'unit_nets_map': (a['unit']['nets_map'], b['unit']['nets_map'])}
    xc['rows'][f'{fmt}.{nm}'] = {nn: {'ours': x, 'committed': y, 'ratio': (x / y if y else None)} for nn, (x, y) in q.items()}
    xc['rows'][f'{fmt}.{nm}']['check_mismatch_ours'] = max(p['check_mismatch'] for p in o['points'])
    xl.append(f'{fmt}.{nm}: ' + ', '.join(f'{nn} {x / y:.6f}' if y else f'{nn} {x:.1f}/{y:.1f}' for nn, (x, y) in q.items())
              + f"; check mismatches {xc['rows'][f'{fmt}.{nm}']['check_mismatch_ours']}")
json.dump(xc, open(os.path.join(OUT, 'crosscheck-launch-fp32.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(OUT, 'crosscheck-launch-fp32.txt'), 'w').write(xc['what'] + '\n' + '\n'.join(xl) + '\n')

out32['problems'] = problems
outL['problems'] = problems
json.dump(out32, open(os.path.join(OUT, 'counts-fp32-gemm-states.json'), 'w'), indent=1, sort_keys=True)
json.dump(outL, open(os.path.join(OUT, 'counts-fp16-int8-launch.json'), 'w'), indent=1, sort_keys=True)
cols = list(csv_rows[0].keys())
with open(os.path.join(OUT, 'counts-v31.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(csv_rows)
with open(os.path.join(OUT, 'counts-v31-tiles.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(tile_rows[0].keys()))
    w.writeheader()
    w.writerows(tile_rows)
print(f'rows {len(csv_rows)} (fp32 {sum(1 for r in csv_rows if r["fmt"] == "fp32")}, launch {sum(1 for r in csv_rows if r["fmt"] != "fp32")}); '
      f'tiles {len(tile_rows)}; problems {problems or 0}')
for r in csv_rows:
    print(f"  {r['key']:38s} {r['footing_class'][:24]:24s} n {r['n_points']:2d} miss {r['check_mismatch_max']} fin lo/MAC {r['fin_edges_lo_per_mac']:>10} "
          f"sig lo/MAC {r['signal_lo_per_mac']:>10} v {r['valid_share']:.3f} - random {r['minus_committed_random_lo_per_mac']:>10}")
print('\n'.join(xl))
sys.exit(1 if problems else 0)
