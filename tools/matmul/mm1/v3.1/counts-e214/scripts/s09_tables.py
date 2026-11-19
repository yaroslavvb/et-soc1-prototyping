#!/usr/bin/env python3
"""counts-e214 (Q225) step 9: the tables, in the committed form of tools/matmul/mm1/v3.1/counts/ (fix-v31counts' s04_tables.py, the same
arithmetic to the last digit: MM1-v1 units, E210's k off the committed switch-counts-e210.json for fp32; design C's switch-table formula
for fp16 and int8), for E214's 20 plan-tile kinds with no committed count; desk; reads this lane's bench outputs, writes counts/:
  counts-fp32-gemm-states.json  shapes -> S1 | S2 -> 'pattern:<name>' (the fields of v3.1's counts/ and E210's switch-counts-e210.json)
  counts-fp16-int8-launch.json  rows -> '<fmt>.pattern:<name>' (MM1-v1's switch-table row form), tiles -> each tile's own row
  counts-e214.csv, counts-e214-tiles.csv  the same rows (a tile per row for the launch-point kinds)
  crosscheck-sparse50h.json/.txt  E214's sparse50h file at the launch points against the committed fp16 sparse50 row (not a new count)
Each row carries counts_footing (MM1-v3.1's COUNT_FOOTING for its format, verbatim from mm1_v31.py at 8bde0182) and
counts_footing_mm1_v3 (MM1-v3's, verbatim from mm1_v3.py), both checked by ast; the bench sources manifest sha256; and, for fp32, a note
saying which E214 arms read that state. Checked: a pool of fewer than 3 files is measured at every file (every kind here is one file);
no key of these tables is a key of the committed tables MM1-v3.1 merges (E210's S1 / S2, v3.1's counts/, MM1-v1's switch table).
    /usr/bin/python3 -I -B s09_tables.py <lane dir>
"""
import ast
import csv
import hashlib
import json
import os
import sys

L = sys.argv[1]
sys.path.insert(0, os.path.join(L, 'scripts'))
import inventory_e214 as I  # noqa: E402

LAB = os.path.join(L, 'work', 'lab')
C = os.path.join(L, 'work', 'counts')
OUT = os.path.join(L, 'counts')
os.makedirs(OUT, exist_ok=True)
MACS = {'fp32': 4096, 'fp16': 8192, 'int8': 16384}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def j(p):
    return json.load(open(p))


def footing(path):
    v = [ast.literal_eval(n.value) for n in ast.parse(open(path).read()).body
         if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'COUNT_FOOTING' for t in n.targets)]
    assert len(v) == 1, path
    return v[0]


FOOT = footing(os.path.join(LAB, 'tools/matmul/mm1/v3.1/mm1_v31.py'))       # MM1-v3.1's labels, verbatim
FOOT3 = footing(os.path.join(LAB, 'tools/matmul/mm1/v3/mm1_v3.py'))         # MM1-v3's labels, verbatim
assert set(FOOT) == set(FOOT3) == {'fp32', 'fp16', 'int8'}
assert FOOT['fp16'] == FOOT3['fp16'] and FOOT['int8'] == FOOT3['int8']

scope = j(os.path.join(L, 'work', 'scope-e214.json'))
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
SRC = {'bench': 'rtl-sim/fma_toggle_v2 at GitHub main 8bde0182 (vpu_top, -fno-dfg; Verilator 5.042; the Makefile copy -j 10 -> -j 2)',
       'bench_sources_manifest_sha256': benchsrc, 'core_et': 'b38a1a31 (rtl, dv/inc, extern by git archive)', 'core_et_manifest_sha256': coremf}
# the committed tables MM1-v3.1 merges (its vendored copies), for the key-collision check and the vendored copies' identity
V3I = os.path.join(LAB, 'tools/matmul/mm1/v3/inputs')
e210v = j(os.path.join(V3I, 'e210', 'switch-counts-e210.json'))
swtv = j(os.path.join(V3I, 'v2', 'v1', 'switch_table.json'))['rows']
v31_32 = j(os.path.join(LAB, 'tools/matmul/mm1/v3.1/counts/counts-fp32-gemm-states.json'))['shapes']
v31_L = j(os.path.join(LAB, 'tools/matmul/mm1/v3.1/counts/counts-fp16-int8-launch.json'))['rows']
problems = []
if sha(os.path.join(V3I, 'e210', 'switch-counts-e210.json')) != sha(os.path.join(LAB, 'tools/claims-v3/e210/desk/switch-counts-e210.json')):
    problems.append("MM1-v3's vendored switch-counts-e210.json differs from E210's committed one")
if sha(os.path.join(V3I, 'v2', 'v1', 'switch_table.json')) != sha(os.path.join(LAB, 'tools/matmul/mm1/v1/inputs/switch_table.json')):
    problems.append("MM1-v3's vendored switch_table.json differs from MM1-v1's")

kb_arms = {}   # (fmt, kind) -> {state: [arm ids]}
for r in scope['kinds']:
    d = {}
    for a in r['arms']:
        kb = int(a.split('-')[0].split('x')[2])
        s = ('S1' if kb == 1 else 'S2') if r['fmt'] == 'fp32' else 'launch'
        d.setdefault(s, []).append(a)
    kb_arms[(r['fmt'], r['kind'])] = d

fp32 = {'S1': j(os.path.join(C, 'new-fp32-S1.json')), 'S2': j(os.path.join(C, 'new-fp32-S2.json'))}
lau = j(os.path.join(C, 'new-launch.json'))['rows']
for s, d in fp32.items():
    if d.get('incomplete'):
        problems.append(f'fp32 {s} incomplete: {d["incomplete"]}')
for k in I.KINDS:
    if k['fmt'] != 'fp32':
        continue
    for s in ('S1', 'S2'):
        got = {p['tile'] for p in fp32[s]['rows'][k['key']]['points']}
        want = {os.path.basename(p) for p in k['files']}
        if len(want) < 3 and got != want:
            problems.append(f"fp32 {s} {k['key']}: a pool of {len(want)} files measured at {len(got)}")

out32 = {'what': ("counts-e214 (Q225) desk switch counts (MM1-v1 units) at GEMM accumulator states for E214's fp32 plan-tile kinds with no "
                  "committed count; desk inputs, not measurements; the form of tools/matmul/mm1/v3.1/counts/counts-fp32-gemm-states.json"),
         'definition': sc['definition'], 'k_sig_lo': k_lo, 'k_sig_hi': k_hi, 'k_clk': k_clk,
         'driver': ("tools/claims-v3/e210/desk/count_e210.py (E210's committed driver, unchanged): S1 j 3, 11, 19, 27 tiles 0, 1; S2 j 15, 47, 79, "
                    "111 tile 2; a pool of fewer than 3 files is measured at every file (every kind here is one file: its one file at both states)"),
         'counts_footing': FOOT['fp32'], 'counts_footing_mm1_v3': FOOT3['fp32'], 'sources': SRC, 'python': sys.version.split()[0],
         'shapes': {'S1': {}, 'S2': {}}}
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
        arms_here = kb_arms[('fp32', k['mm1_v3_kind'])].get(s, [])
        note = (f"read by E214's arm{'s' if len(arms_here) > 1 else ''} {', '.join(sorted(arms_here))} "
                f"({'KB 1' if s == 'S1' else 'KB >= 2: S2, as MM1-v3 reads E210 S2 for every KB >= 2'})" if arms_here else
                f"no E214 arm of this kind runs at {'KB 1' if s == 'S1' else 'KB >= 2'}: counted for completeness, as v31-counts counted every kind at both states")
        row = {'key': k['key'], 'mm1_v3_kind': k['mm1_v3_kind'], 'group': k['group'], 'gen': k['gen'],
               'tiles': [os.path.basename(p) for p in k['files']], 'tiles_sha256': {os.path.basename(p): tinv[p]['sha256'] for p in k['files']},
               'n_points': len(pts), 'check_mismatch_max': max(p['check_mismatch'] for p in pts),
               'fin_edges_lo': sig_lo + c, 'fin_edges_hi': sig_hi + c, 'signal_lo': sig_lo, 'signal_hi': sig_hi, 'clock': c,
               'vpu_nets_map': vpu, 'clock_nets': clk, 'unit_nets_hier': m['unit']['nets_hier'] / 4096, 'unit_nets_map': m['unit']['nets_map'] / 4096,
               'valid_slots': m['valid_slots'] / 4096, 'clocked_bits': m['ff']['all']['clocked'] / 4096,
               'vpu_nets_map_min_max': [min(p['vpu']['nets_map'] for p in pts) / 4096, max(p['vpu']['nets_map'] for p in pts) / 4096],
               'minus_randn_lo': sig_lo + c - rnd['fin_edges_lo'], 'minus_randn_hi': sig_hi + c - rnd['fin_edges_hi'],
               'S_signal_lo_per_op': sig_lo * 4096, 'counts_footing': FOOT['fp32'], 'counts_footing_mm1_v3': FOOT3['fp32'],
               'counts_source': f"counts-e214's desk counts at GEMM states ({'S1, KB = 1' if s == 'S1' else 'S2, KB >= 2'})",
               'e214_arms': sorted(arms_here), 'note': note}
        out32['shapes'][s][k['mm1_v3_kind']] = row
        csv_rows.append({'key': k['key'], 'group': k['group'], 'fmt': 'fp32', 'mm1_v3_kind': k['mm1_v3_kind'],
                         'footing_class': f"{s} (GEMM states, {'KB 1' if s == 'S1' else 'KB >= 2'})", 'n_tiles': len(k['files']), 'n_points': len(pts),
                         'check_mismatch_max': row['check_mismatch_max'], 'S_signal_lo_per_op': round(row['S_signal_lo_per_op'], 1),
                         'signal_lo_per_mac': round(sig_lo, 3), 'signal_hi_per_mac': round(sig_hi, 3), 'clock_per_mac': round(c, 3),
                         'fin_edges_lo_per_mac': round(sig_lo + c, 3), 'fin_edges_hi_per_mac': round(sig_hi + c, 3),
                         'valid_share': round(row['valid_slots'], 6), 'clocked_bits_per_mac': round(row['clocked_bits'], 3),
                         'vpu_nets_map_per_mac': round(vpu, 3), 'unit_nets_hier_per_mac': round(row['unit_nets_hier'], 3),
                         'minus_committed_random_lo_per_mac': round(row['minus_randn_lo'], 3), 'counts_footing': FOOT['fp32'],
                         'tiles': ';'.join(row['tiles']), 'tiles_sha256_16': ';'.join(v[:16] for v in row['tiles_sha256'].values()),
                         'bench_sources_manifest_sha256': benchsrc, 'e214_arms': ';'.join(sorted(arms_here)), 'note': note})


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
            'valid_share_v': min(max(v, 0.0), 1.0), 'valid_share_v_unclipped': v, 'footing': FOOT[fmt], 'counts_footing': FOOT[fmt],
            'counts_footing_mm1_v3': FOOT3[fmt]}


def avg(objs):
    if isinstance(objs[0], dict):
        return {k: avg([o.get(k, 0) for o in objs]) for k in objs[0]}
    return sum(objs) / len(objs)


outL = {'what': ("counts-e214 (Q225) desk counts at the harness's launch points (run_kinds.py) for E214's fp16 and int8 plan-tile kinds with no "
                 "committed count, in MM1-v1's switch-table form (design C's switch_table.py formula); desk inputs, not measurements; the form "
                 "of tools/matmul/mm1/v3.1/counts/counts-fp16-int8-launch.json"),
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
                          'vpu_nets_per_mac': t['per_mac']['rtl_vpu_net_toggles'],
                          'counts_footing': FOOT[fmt], 'bench_sources_manifest_sha256': benchsrc})
    if len(means) != len(k['files']):
        continue
    t = table_row(avg(means), MACS[fmt], fmt)
    arms_here = kb_arms[(fmt, k['mm1_v3_kind'])].get('launch', [])
    t.update({'kind_key': k['key'], 'mm1_v3_kind': k['mm1_v3_kind'], 'group': k['group'], 'gen': k['gen'], 'n_tiles': len(k['files']),
              'tiles': [os.path.basename(p) for p in k['files']], 'tiles_sha256': {os.path.basename(p): tinv[p]['sha256'] for p in k['files']},
              'n_points': len(pts_all), 'check_mismatch_max': max(q['check_mismatch'] for q in pts_all),
              'counts_source': "counts-e214's desk counts at the harness launch points (run_kinds.py; MM1-v1's switch table form)",
              'e214_arms': sorted(arms_here)})
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
                     'tiles_sha256_16': ';'.join(v[:16] for v in t['tiles_sha256'].values()), 'bench_sources_manifest_sha256': benchsrc,
                     'e214_arms': ';'.join(sorted(arms_here)), 'note': ''})

# the key-collision check: MM1-v3.1 merges new rows only where the key is not committed already (energy_v31's asserts)
for s in ('S1', 'S2'):
    for kk in out32['shapes'][s]:
        if kk in e210v['shapes'][s] or kk in v31_32[s]:
            problems.append(f'fp32 {s} key {kk} is already a committed row')
for kk in outL['rows']:
    if kk in swtv or kk in v31_L:
        problems.append(f'launch key {kk} is already a committed row')

# the cross-check: E214's sparse50h file (pair 0 of its fp16 sparse50 pools) at the launch points against the committed fp16 sparse50 row
xc = {'what': ("E214's sparse50h tile file (pair 0 of an fp16 sparse50 pool; the host draws every other pool tile by rgm136's sparse50 law) "
               "counted at the launch points against the committed fp16 sparse50 row (counts-v2.json, made from tools/claims-v3/kinds/tiles/fp16/"
               "sparse50.bin, and MM1-v1's switch table): a cross-check that a second draw of the law reads like the committed one; not a new count, "
               "and E214's sparse50h arms are the committed fp16 sparse50 kind"), 'rows': {}}
xl = []
for fmt, nm, p, ck in I.XCHECK:
    o = lau.get(f'{fmt}.xcheck.{nm}')
    cm = c2.get(ck)
    if o is None or cm is None:
        problems.append(f'xcheck {fmt}.{nm} missing')
        continue
    a, b = o['mean'], cm['mean']
    q = {'vpu_nets_map': (a['vpu']['nets_map'], b['vpu']['nets_map']), 'clock_nets_cov': (a['clock_nets_cov'], b['clock_nets_cov']),
         'ff_all_clocked': (a['ff']['all']['clocked'], b['ff']['all']['clocked']), 'unit_nets_hier': (a['unit']['nets_hier'], b['unit']['nets_hier']),
         'unit_nets_map': (a['unit']['nets_map'], b['unit']['nets_map']), 'valid_slots': (a['valid_slots'], b['valid_slots'])}
    mine = table_row(a, MACS[fmt], fmt)
    row = st[ck]
    tq = {'signal_lo_zero_delay_a_op': (mine['fin_edges_per_op']['signal_lo_zero_delay'], row['fin_edges_per_op']['signal_lo_zero_delay']),
          'clock_a_op': (mine['fin_edges_per_op']['clock'], row['fin_edges_per_op']['clock']),
          'register_bits_clocked_a_MAC': (mine['per_mac']['register_bits_clocked'], row['per_mac']['register_bits_clocked']),
          'fin_edges_lo_a_MAC': (mine['fin_edges_per_mac']['lo'], row['fin_edges_per_mac']['lo'])}
    bz = st[f'{fmt}.zeros']['per_mac']['register_bits_clocked']
    bo = st[f'{fmt}.ones']['per_mac']['register_bits_clocked']
    v_comm = min(max((row['per_mac']['register_bits_clocked'] - bz) / (bo - bz), 0.0), 1.0)
    tq['valid_share_v'] = (mine['valid_share_v'], v_comm)
    xc['rows'][f'{fmt}.{nm}'] = {'tile': p, 'tile_sha256': tinv[p]['sha256'], 'against': f'counts-v2.json {ck} and MM1-v1 switch_table.json {ck}',
                                 'raw': {nn: {'ours': x, 'committed': y, 'ratio': (x / y if y else None)} for nn, (x, y) in q.items()},
                                 'table_units': {nn: {'ours': x, 'committed': y, 'ratio': (x / y if y else None)} for nn, (x, y) in tq.items()},
                                 'check_mismatch_ours': max(pp['check_mismatch'] for pp in o['points']), 'n_points': len(o['points'])}
    xl.append(f'{fmt}.{nm} (E214 tile) / {ck} (committed): ' + ', '.join(f'{nn} {x / y:.4f}' if y else f'{nn} {x}/{y}' for nn, (x, y) in tq.items())
              + '; raw ' + ', '.join(f'{nn} {x / y:.4f}' if y else f'{nn} {x}/{y}' for nn, (x, y) in q.items())
              + f"; check mismatches {xc['rows'][f'{fmt}.{nm}']['check_mismatch_ours']}")
json.dump(xc, open(os.path.join(OUT, 'crosscheck-sparse50h.json'), 'w'), indent=1, sort_keys=True)
open(os.path.join(OUT, 'crosscheck-sparse50h.txt'), 'w').write(xc['what'] + '\n' + '\n'.join(xl) + '\n')

out32['problems'] = problems
outL['problems'] = problems
json.dump(out32, open(os.path.join(OUT, 'counts-fp32-gemm-states.json'), 'w'), indent=1, sort_keys=True)
json.dump(outL, open(os.path.join(OUT, 'counts-fp16-int8-launch.json'), 'w'), indent=1, sort_keys=True)
with open(os.path.join(OUT, 'counts-e214.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
    w.writeheader()
    w.writerows(csv_rows)
with open(os.path.join(OUT, 'counts-e214-tiles.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(tile_rows[0].keys()))
    w.writeheader()
    w.writerows(tile_rows)
print(f'rows {len(csv_rows)} (fp32 {sum(1 for r in csv_rows if r["fmt"] == "fp32")}, launch {sum(1 for r in csv_rows if r["fmt"] != "fp32")}); '
      f'tiles {len(tile_rows)}; problems {problems or 0}')
for r in csv_rows:
    print(f"  {r['key']:26s} {r['footing_class'][:24]:24s} n {r['n_points']:2d} miss {r['check_mismatch_max']} fin lo/MAC {r['fin_edges_lo_per_mac']:>10} "
          f"sig lo/MAC {r['signal_lo_per_mac']:>10} v {r['valid_share']:.3f} - random {r['minus_committed_random_lo_per_mac']:>10}")
print('\n'.join(xl))
sys.exit(1 if problems else 0)
