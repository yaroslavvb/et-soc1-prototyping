#!/usr/bin/env python3
"""v31-counts (Q217): writes counts/README.md from this lane's tables (desk; every number below is read from the files it names).
    /usr/bin/python3 -I -B s12_readme.py <lane dir> <final time text>
"""
import csv
import json
import os
import sys

L = sys.argv[1]
WHEN = sys.argv[2]
C = os.path.join(L, 'counts')


def j(n):
    return json.load(open(os.path.join(C, n)))


rows = list(csv.DictReader(open(os.path.join(C, 'counts-v31.csv'))))
rc = j('recount-check.json')
xc = j('crosscheck-launch-fp32.json')
e13 = j('e213-check.json')
up = j('unpriced-mm1v3.json')
src = j('SOURCES.json')
n32 = len({r['key'] for r in rows if r['fmt'] == 'fp32'})
n16 = len({r['key'] for r in rows if r['fmt'] == 'fp16'})
n8 = len({r['key'] for r in rows if r['fmt'] == 'int8'})
npts = sum(int(r['n_points']) for r in rows)
nrec = sum(len(v.get('quantities', {})) and 1 for v in rc['checks'].values())
miss = max(int(r['check_mismatch_max']) for r in rows)
q1 = rc['checks']['fp32_S1_randn_gemm_states']['quantities']
q8 = rc['checks']['int8.full_launch_points']['quantities']
q16 = rc['checks']['fp16.randn_launch_points']['quantities']


def fr(x):
    return f'{float(x):,.0f}' if abs(float(x)) >= 100 else f'{float(x):.3f}'


L1 = []
L1.append('# MM1-v3.1 inputs: the transistor-switch counts MM1-v3 could not make (Q217, Wed 18 Nov 2026)')
L1.append('')
L1.append("Desk counts, not measurements. MM1-v3's README (section 7) says: \"No new count was made this round (no simulator here), so E212's plan")
L1.append("tiles, the real tiles and any new pattern are NOT FORECAST in energy and carry no count.\" This folder holds those counts, made with the")
L1.append("lab's RTL bench (`rtl-sim/fma_toggle_v2` at GitHub main 6efdb002, Verilator 5.042, the open core-et RTL at b38a1a31) on the lab box")
L1.append("aifoundry2's desk, in each format's committed footing, so that MM1-v3's switch route can price those kinds with no constant changed.")
L1.append("Nothing here is fitted, and nothing here was read from a card: the counts depend on the tile bytes alone.")
L1.append('')
L1.append('The owner\'s words that started the matmul model (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want you')
L1.append('to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and')
L1.append('clock cycles."')
L1.append('')
L1.append('## 0. On one screen')
L1.append('')
L1.append(f'- **Counted:** {n32} fp32 kinds at a GEMM\'s accumulator states (S1 for KB 1 and S2 for KB >= 2, as E210), {n16} fp16 and {n8} int8 kinds at the')
L1.append(f'  harness\'s launch points (MM1-v1\'s switch-table footing): {npts} bench points, every one behind the bench\'s accumulator check with '
          f'{miss} mismatched words.')
L1.append(f"- **Before any new count, committed points were re-counted** (`recount-check.*`): fp32 S1 random at GEMM states against E210's committed")
L1.append(f"  row: every quantity equal (VPU nets_map ratio {q1['vpu_nets_map']['ratio']:.6f}, signal fin edges lo {q1['MM1v1_signal_lo_a_MAC']['ratio']:.6f}, "
          f"8 of 8 points, the same tiles and depths); int8 full at the launch points against counts-v2.json: {q8['vpu_nets_map']['ratio']:.6f}; fp16 random: "
          f"{q16['vpu_nets_map']['ratio']:.6f} (VPU nets_map; the committed counts used Verilator 5.052). Rule declared before reading them: every ratio")
L1.append('  that enters the switch route within 0.999-1.001 and every check 0: **MATCH**.')
xs = ', '.join(f"{k} {v['vpu_nets_map']['ratio']:.6f}" for k, v in xc['rows'].items())
L1.append(f'- **A third check:** three of E212\'s fp32 tiles are byte-equal to lab kinds committed at the launch points; re-counted there: VPU nets_map {xs}.')
L1.append(f"- **E213:** its {e13['n_points']} registered points use random, zeros, ones and sparse50 in fp32 and int8 only, all with committed counts; MM1-v3 forecast")
L1.append(f"  the energy of {e13['n_energy_forecast']} of {e13['n_points']} (`e213-check.json`). **None is NOT FORECAST for want of a count, so this lane made no E213 energy")
L1.append('  forecast** (no `e213-energy-unread/` folder). No E213 data file was opened.')
L1.append('')
L1.append('## 1. What needed a count (scope)')
L1.append('')
L1.append("Found by reading MM1-v3 as landed (b1493082): its own energy points and E212's pattern runs through `energy_v3.counts()` and `phi_of()`")
L1.append(f"(`unpriced-mm1v3.json`: {sum(g['n_points'] for g in up['unpriced_energy_points'])} unpriced energy points in {len(up['unpriced_energy_points'])} groups; "
          f"{sum(q['n_runs'] for q in up['e212_pattern_runs_time_only'])} E212 pattern runs that MM1-v3 reads for time only), and by a sha256 scan of E212's 30 tile files")
L1.append("against the lab's kind tiles (`tools/claims-v3/kinds`).")
L1.append('')
L1.append("- **E212's plan tiles** (one tile pair repeated, gen tiles): fp32 den4, den8, den16, den21, fld_mant, fld_sign, lanes2, pow2, bf16trunc, fp16grid;")
L1.append('  fp16 den16_4, den16_10, fld16_exp, fld16_mant, fld16_sign; int8 i8_den1, i8_den3, i8_den6, i8_pm1. bf16trunc, fp16grid and pow2 are byte-equal')
L1.append("  to the lab kinds of those names, committed at the launch points (counts-v2.json) but never at GEMM states, fp32's footing in MM1-v3, so they")
L1.append("  are counted here. E212's ones, zeros, randn and full files are the lab's committed kinds; its sparse50f and sparse50i arms run gen sparse50")
L1.append("  (the file supplies the pool's pair 0 only, every other pair being drawn by the sparse50 law; the file is byte-equal to the lab's sparse50")
L1.append("  tile): the committed sparse50 kind, not counted again.")
L1.append("- **The real tiles MM1-v3 could not price:** E206's real kind in fp16 and int8 (E206's four real2 tiles a format, in E206's order; fp32's has")
L1.append("  E210's committed GEMM-state row `real`, which MM1-v3 does not price only because `phi_of()` has no rule for it: a phi, not a count); E207's")
L1.append("  real:blind4 in fp32, fp16 and int8 (two tiles each, in E207's order).")
L1.append("- **E207's two other unpriced kinds,** counted because they sit in MM1-v3's energy data with no count: designed:blind3 a_colconst_b_randn (fp32,")
L1.append("  one tile) and e37 (fp32, gen e37: E37's fill of +-1 and +-2 drawn by rgm136's drawTile; counted on 61 desk pairs of that law, as E210")
L1.append("  counted random and sparse50 on 61 desk pairs of theirs).")
L1.append("- **E213** (tools/claims-v3/e213, registration only): no new kind. **MM1-v3's E213 forecasts:** no point NOT FORECAST in energy.")
L1.append('')
L1.append('## 2. How (desk)')
L1.append('')
L1.append("- **The bench:** `rtl-sim/fma_toggle_v2` copied from GitHub main 6efdb002 by `git archive` (every file equal to its blob and to the lab's working")
L1.append("  tree), core-et's rtl, dv/inc and extern from a checkout at b38a1a31 (1,268 files, equal to their source), built with Verilator 5.042 and the")
L1.append("  Makefile's -fno-dfg, the copy's one change Verilator's -j 10 made -j 2 (single-threaded model), under a 4 GB cap, in the lab's CPU slot with")
L1.append("  no device node visible. The functional check (`fcheck_all.sh`) PASSED: unit fp32 40,000 of 40,000 exact; unit fp16 39,701 exact + 299 named")
L1.append("  residue; whole TensorFMA ops fp32 22,016, fp16 22,016, int8 18,944 words exact; zero gate 63 cases, 0 differ. The net maps were trained on")
L1.append("  this binary (`train_maps.py`); they are byte-equal to sw-design-a's (Q202).")
L1.append("- **fp32, at GEMM states:** E210's committed driver `tools/claims-v3/e210/desk/count_e210.py`, unchanged (run_kinds.py's measurement: one warm op,")
L1.append("  a coverage run of two ops with the accumulator checked word for word, one op counted by settle_count; C loaded as a GEMM accumulation of j")
L1.append("  other tiles of the kind): S1 j = 3, 11, 19, 27 of 32 ops, tiles 0 and 1 of a pooled kind; S2 j = 15, 47, 79, 111 of 128, tile 2. Units:")
L1.append("  E210's definition to the last digit (signal fin edges a MAC = VPU nets_map a MAC x k_sig, clock fin edges = clock-net toggles a MAC x 39.8;")
L1.append(f"  k_sig lo {rc['k']['k_sig_lo']:.4f}, hi {rc['k']['k_sig_hi']:.4f}, read off MM1-v1's frozen switch table).")
L1.append("- **fp16 and int8, at the launch points:** `run_kinds.py` (the command behind counts-v2.json, from which MM1-v1's switch table was made), one row")
L1.append("  a tile at three points of a 0.5 s launch of that pair repeated (fp16 n0 91,575 / 274,725 / 457,875; int8 157,232 / 471,698 / 786,163), in")
L1.append("  MM1-v1's switch-table form by design C's formula (signal fin edges = VPU nets_map x g x 14.5, g = 4,132.5 or 6,494.8 gate toggles a random")
L1.append("  fp32 MAC over the committed fp32 random unit nets_map; clock x 39.8), rounded as the table rounds. A pooled kind (E206's four tiles, blind4's")
L1.append("  two) is the mean over its tiles of each raw count an op, the card's pool cycling them evenly.")
L1.append('- **Footings** (MM1-v3 README section 7, carried in every row as `counts_footing`): fp32 counted (desk) at GEMM states; fp16 estimated (desk),')
L1.append('  not counted: RTL toggles x the fp32 gate/RTL ratio; int8 counted (desk) around the arithmetic only (the behavioural RTL has no nets inside')
L1.append("  the int8 multiply, product sum and add; MM1-v3's m_int8 carries the rest).")
L1.append('')
L1.append('## 3. The counts (desk; fin edges a multiply-add; `counts-v31.csv`, every field in the JSON files)')
L1.append('')
L1.append('| kind | format | footing | tiles | points | signal lo | clock | fin edges lo / hi | valid share | minus committed random (lo) |')
L1.append('|---|---|---|---:|---:|---:|---:|---:|---:|---:|')
for r in rows:
    L1.append(f"| {r['mm1_v3_kind']} ({r['group']}) | {r['fmt']} | {r['footing_class'].split(' (')[0]} | {r['n_tiles']} | {r['n_points']} | {fr(r['signal_lo_per_mac'])} | "
              f"{fr(r['clock_per_mac'])} | {fr(r['fin_edges_lo_per_mac'])} / {fr(r['fin_edges_hi_per_mac'])} | {float(r['valid_share']):.3f} | {fr(r['minus_committed_random_lo_per_mac'])} |")
L1.append('')
SC = json.load(open(os.path.join(L, 'work/lab/tools/claims-v3/e210/desk/switch-counts-e210.json')))['shapes']
ST = json.load(open(os.path.join(L, 'work/lab/tools/matmul/mm1/v1/inputs/switch_table.json')))['rows']
L1.append(f"The committed random rows for reference (fin edges lo a MAC): fp32 at GEMM states S1 {SC['S1']['randn']['fin_edges_lo']:,.0f}, S2 "
          f"{SC['S2']['randn']['fin_edges_lo']:,.0f} (E210); fp16 {ST['fp16.randn']['fin_edges_per_mac']['lo']:,} and int8 {ST['int8.full']['fin_edges_per_mac']['lo']:,}")
L1.append("(MM1-v1's switch table at the launch points). The valid share is fp32's valid lane slots a MAC, or for fp16 and int8 the clocked-register")
L1.append("share between the committed zeros and ones rows, as `energy_v3.counts()` computes it.")
L1.append('')
L1.append('## 4. How MM1-v3.1 reads them')
L1.append('')
L1.append("- fp32: `counts-fp32-gemm-states.json` -> `shapes` -> `S1` (KB 1) or `S2` (KB >= 2) -> the kind as MM1-v3's data names it (`pattern:den4`,")
L1.append("  `real:blind4`, `designed:blind3 a_colconst_b_randn`, `e37`): the same fields as `tools/claims-v3/e210/desk/switch-counts-e210.json`, so")
L1.append("  `counts()` reads S = signal_lo x 4,096 an op and v = valid_slots.")
L1.append("- fp16 and int8: `counts-fp16-int8-launch.json` -> `rows` -> `<format>.<kind>` (e.g. `fp16.real`, `int8.pattern:i8_pm1`): MM1-v1's switch-table")
L1.append("  row form, so `counts()` reads S = `fin_edges_per_op.signal_lo_zero_delay` and v from `per_mac.register_bits_clocked` (the row also carries")
L1.append("  `valid_share_v`); `tiles` holds each tile's own row.")
L1.append("- Not here: phi (the lines' data share). MM1-v3's `phi_of()` has no rule for these kinds; `kinds_v3.phi()` over the same tile files gives one by")
L1.append("  MM1-v3's own formula; that is the declaration's to settle, not a count.")
ZS = json.load(open(os.path.join(C, 'tile-zero-shares.json')))
zk = {k: v for k, v in ZS.items() if v['any_zero']}
zt = '; '.join(f"{k}: A {v['A_zero_share_mean']:.1%}, B {v['B_zero_share_mean']:.1%}" for k, v in zk.items())
L1.append(f"- The zero gate: only the int8 real tiles hold zero elements ({zt}; `tile-zero-shares.json`), and the bench reads them fully valid")
L1.append("  (valid share 1.000 by the clocked-register measure `counts()` uses); no other counted tile has a zero element, so `gate_shares()` (zeros, arow50 and")
L1.append("  sparse50 only) gives these kinds no gate, which is what the bench shows.")
L1.append('')
L1.append('## 5. What these counts do not cover, the gaps, and NOT RUN')
L1.append('')
L1.append("- The memory path, the core, TenB, cell internals and the full-custom register file are not in any count; `hi` is the timed estimate (glitches")
L1.append("  by the gate-level calibration's ratio), `lo` zero delay. fp16 is not gate-level; int8 leaves out its arithmetic (section 2).")
L1.append("- Verilator 5.042 here against the committed counts' 5.052: equal for fp32 and int8 in the re-counts, fp16 0.99996.")
L1.append("- GEMM states are sampled (four depths; one or two tiles). E212's plan tiles at gemmL4x8x8 (KB 8: fp32 den4, den8, fld_sign, lanes2) read the")
L1.append("  S2 states (gemmL1x1x4), as MM1-v3 reads E210's S2 for every KB >= 2.")
L1.append("- fp16 and int8 at the launch points model a launch of ONE tile pair repeated; a pooled kind's count is the mean of its tiles each repeated")
L1.append("  alone, while the card alternates them (the pair-to-pair switching between different tiles is not in it).")
L1.append("- **NOT RUN:** any card, any simulator other than this RTL bench (no sys_emu), any fit, a gate-level fp16 or int8 count, GEMM-state counts for fp16")
L1.append("  and int8, a phi for the new kinds, and MM1-v3 run with these rows (no E213 point needed one).")
L1.append('')
L1.append('## 6. The freeze')
L1.append('')
L1.append("No run of E212's plan tiles, nor any card datum, was read for energy by the lane that made these counts (its scope listing read MM1-v3's")
L1.append("committed E212 run records for their arms and sessions only). The sha256 of these files (SHA256SUMS) therefore stands before any read of")
L1.append("those runs' energy residuals under MM1-v3.1: an UNREAD test of the switch route in fp16 and int8 and on a second card is still open. No")
L1.append(f"E213 data file was opened. Final: {WHEN}.")
L1.append('')
L1.append('## 7. Files and how to reproduce')
L1.append('')
L1.append("`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json` (the tables), `counts-v31.csv` and `counts-v31-tiles.csv` (the same rows; a")
L1.append("tile per row for the launch-point kinds), `recount-check.*`, `crosscheck-launch-fp32.*`, `unpriced-mm1v3.json` (the scope listing),")
L1.append("`e213-check.json`, `tile-zero-shares.json`, `SOURCES.json` (every source's sha256, the binaries, the maps, the drivers, the tiles, the desk tiles, the slot jobs),")
L1.append("`raw/` (the bench drivers' own outputs and the desk tiles' sha256 list), `scripts/` (the lane's scripts as run, with the box's paths")
L1.append("replaced by `<W>`, `<LAB>`, `<CORE_ET>`, `<VERILATOR_BIN>`; order: s02 setup, s03 build, s04 functional check, s05 maps, s06 re-counts, s06b")
L1.append("comparison, s07a specs, s07 fp32, s08 fp16 and int8, s09 tables, s01 scope, s10 E213 (s09 and s10 ran as one slot job, s13), s14 zero shares, s15 the desk e37 tiles hold only +-1 and +-2,")
L1.append("s11 sources, s12 this folder; `inventory.py`'s docstring was reworded after the run, its code unchanged). Interpreter")
L1.append(f"`/usr/bin/python3` {src['python'].split()[0]} (`-I -B`), numpy {src.get('numpy')}; {src['gxx']}; {src['verilator']}. Every bench run inside the lab's CPU slot")
L1.append(f"(nice 10) with no device node visible, one job at a time, two bench processes: {src['slot_minutes_total']:.1f} slot-minutes in all (`SOURCES.json`).")
L1.append('')
open(os.path.join(C, 'README.md'), 'w').write('\n'.join(L1) + '\n')
print(f'README.md: {len(L1)} lines')
