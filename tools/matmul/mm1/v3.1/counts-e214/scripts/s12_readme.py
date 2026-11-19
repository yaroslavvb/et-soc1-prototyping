#!/usr/bin/env python3
"""counts-e214 (Q225): writes counts/README.md from the tables (desk; every number below is read from the files it names).
The form of tools/matmul/mm1/v3.1/counts/README.md (v31-counts with fix-v31counts' answers): scope, how, the counts, how MM1-v3.1 reads
them, the gaps and NOT RUN, the freeze, the files.
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


rows = list(csv.DictReader(open(os.path.join(C, 'counts-e214.csv'))))
rc = j('recount-check.json')
xc = j('crosscheck-sparse50h.json')
sc = j('scope-e214.json')
src = j('SOURCES.json')
zs = j('tile-zero-shares.json')
c32 = j('counts-fp32-gemm-states.json')
cL = j('counts-fp16-int8-launch.json')
mg = j('merge-check.json')
n32 = len({r['key'] for r in rows if r['fmt'] == 'fp32'})
n16 = len({r['key'] for r in rows if r['fmt'] == 'fp16'})
n8 = len({r['key'] for r in rows if r['fmt'] == 'int8'})
npts = sum(int(r['n_points']) for r in rows)
miss = max(int(r['check_mismatch_max']) for r in rows)
new_kinds = [k for k in sc['kinds'] if k['verdict'] == 'NEEDS COUNT']
n_arms_new = sum(k['n_arms'] for k in new_kinds)
committed = [k for k in sc['kinds'] if k['verdict'] != 'NEEDS COUNT']
n_arms_comm = sum(k['n_arms'] for k in committed)
xr = xc['rows']['fp16.sparse50h']
ck = rc['checks']
rc_pts = sum(c['n_points'][0] if isinstance(c.get('n_points'), list) else len(c['launch_points_n0']) for c in ck.values())
leaves = sum(c['leaves_compared'] for c in ck.values())
leq = sum(c['leaves_bit_equal'] for c in ck.values())
fp32_s2_arms = {r['mm1_v3_kind']: r['e214_arms'] for r in c32['shapes']['S2'].values() if r['e214_arms']}


def fr(x):
    return f'{float(x):,.0f}'


out = []
A = out.append
A("# E214's switch counts: the transistor-switch counts for E214's operand-pattern tiles that had none (Q225, Thu 19 Nov 2026)")
A('')
A("Desk counts, not measurements. E214 (the model session's third matmul sweep, 1118-mmsweep3, registered in `tools/claims-v3/e214/`) ran")
A(f"{len(new_kinds)} operand-pattern tiles that no committed count covers; MM1-v3.1's `counts31()` and MM1-v3's `counts()` return no count for any")
A("of them, so their runs could not be priced by the switch route. This folder holds those counts, made exactly as MM1-v3.1's committed")
A("counts were (`tools/matmul/mm1/v3.1/counts/`, landed 3e8991d0, with its verifier's and fixer's lessons), with the lab's RTL bench")
A("(`rtl-sim/fma_toggle_v2` at GitHub main 8bde0182, Verilator 5.042, the open core-et RTL at b38a1a31) on the lab box aifoundry2's desk, in")
A("each format's committed footing. Nothing here is fitted, and nothing here was read from a card: the counts depend on the tile bytes alone.")
A("E214's tiles and arms come from its registration and its kit's source only; **no E214 measurement file was read** by this lane.")
A('')
A('The owner\'s words that started the matmul model (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want you')
A('to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and')
A('clock cycles."')
A('')
A('## 0. On one screen')
A('')
A(f"- **Counted:** {n32} fp32 kinds at a GEMM's accumulator states (S1 for KB 1 and S2 for KB >= 2, as E210 and v31-counts), {n16} fp16 and {n8} int8")
A(f"  kinds at the harness's launch points (MM1-v1's switch-table footing): {npts} bench points in the tables, every accumulator check {miss} mismatched words.")
A(f"  These are E214's {len(new_kinds)} plan tiles of gen `tiles` (each a single tile pair the card's pool repeats), run by {n_arms_new} of E214's 361 arms.")
s1 = ck['fp32_S1_pattern:fld_mant']
A(f"- **Before any new count, two committed rows were re-counted** (`recount-check.*`; the rule written and hashed before they ran,")
A(f"  `recount-rule.txt`): MM1-v3.1's fp32 `pattern:fld_mant` at S1 and `pattern:den8` at S2 (count_e210.py), and its int8 `pattern:i8_pm1` and fp16")
A(f"  `pattern:fld16_mant` at the launch points (run_kinds.py): {rc_pts} bench points; **{leq:,} of {leaves:,} reported numbers bit-equal** to the")
A(f"  committed points, every row number equal: **{'MATCH' if rc['pass'] else 'NO MATCH'}**.")
A(f"- **Not counted, because committed:** E214's random, zeros and ones arms ({sum(k['n_arms'] for k in committed if k['gen'] != 'sparse50')} arms: the lab's committed kinds, their files the")
A("  lab's kind tiles byte for byte) and its three `sparse50` pools (gen sparse50: rgm136's host draws every pool tile but pair 0 by its own")
A("  sparse50 law; the file is pair 0): `sparse50f` and `sparse50i` are the lab's sparse50 tiles byte for byte, the committed sparse50 kind (as")
A("  E212's were); `sparse50h`'s file is a new draw of the same law, so its arms are the committed fp16 sparse50 kind. **Cross-check**")
xt = xr['table_units']
A(f"  (`crosscheck-sparse50h.*`, REPORTED, not a row): the sparse50h file counted at the launch points reads signal {xt['signal_lo_zero_delay_a_op']['ratio']:.4f},")
A(f"  fin edges lo a MAC {xt['fin_edges_lo_a_MAC']['ratio']:.4f} and valid share {xt['valid_share_v']['ratio']:.4f} of the committed fp16 sparse50 row")
sp = sc['sparse50h_pair0']
A(f"  (its A holds {sp['e214_sparse50h']['A']['zero_share']:.1%} zeros and B {sp['e214_sparse50h']['B']['zero_share']:.1%}, the lab's tile"
  f" {sp['lab_fp16_sparse50']['A']['zero_share']:.1%} and {sp['lab_fp16_sparse50']['B']['zero_share']:.1%}): two one-tile draws of one law differ by")
A("  this much at the launch-point footing, whose committed sparse50 row is itself one tile; the card's pools draw thousands of tiles.")
A("- **The rule a pool of fewer than 3 files is measured at every file** holds trivially: every counted kind is one file, measured at that file.")
A("  The e37 lesson (a card pool's pair 0 that the desk pool leaves out) does not arise: a one-file `tiles` pool holds no other pair.")
A('')
A('## 1. What needed a count (scope)')
A('')
A(f"From E214's registered `proposal/src/arms.json` (sha256 {sc['arms_json_sha256'][:16]}...: {sc['n_arms']} arms, {len(sc['kinds'])} (format, kind) pairs), each arm's kind")
A("named as MM1-v3's data code names an arm of this form (`data_v3.e212_kind`: `rnd` -> random, zeros, ones, else `pattern:<tile name>`),")
A("and MM1-v3.1's `energy_v31.counts31()` and MM1-v3's `energy_v3.counts()` asked at every (format, kind, KB) an arm runs (`scope-e214.json`,")
A("`scope-e214.txt`); every tile file also compared by sha256 with the lab's kind tiles and with every tile v3.1's committed counts measured.")
A('')
A('| format | kind | gen | arms | KB of its arms | states | committed count | verdict |')
A('|---|---|---|---:|---|---|---|---|')
for k in sorted(sc['kinds'], key=lambda k: (k['verdict'] != 'NEEDS COUNT', k['fmt'], k['kind'])):
    have = 'none' if k['verdict'] == 'NEEDS COUNT' else ('as sparse50' if k['gen'] == 'sparse50' else 'yes')
    A(f"| {k['fmt']} | `{k['kind']}` | {k['gen']} | {k['n_arms']} | {', '.join(str(x) for x in k['KB'])} | {', '.join(k['states'])} | {have} | {k['verdict']} |")
A('')
A(f"The {len(new_kinds)} kinds marked NEEDS COUNT are exactly `inventory_e214.NEW` (checked: {sc['needs_count_equals_inventory']}). None of their files")
A("equals a lab kind tile or a tile the committed v3.1 counts measured, and E214.md section 2 found none of its 21 new files equal to any of the")
A("lab's 1,746 distinct 2,048-byte tile files. Of the fp32 kinds, only `bh3_e3` and `sp_ar4` run at KB >= 2 (gemmL4x8x8, KB 8); every fp32 kind")
A("is counted at both S1 and S2 anyway (as v31-counts counted every kind at both), and each row's `note` names the E214 arms that read it.")
A('')
A('## 2. How (desk)')
A('')
A("- **The bench:** `rtl-sim/fma_toggle_v2` by `git archive` of GitHub main 8bde0182 (every file equal to its blob; its source manifest identical")
A("  to the one v31-counts built from at 6efdb002), core-et's rtl, dv/inc and extern by `git archive` of b38a1a31 (1,268 files, the manifest")
A("  identical to v31-counts'), built with Verilator 5.042 and the Makefile's -fno-dfg, the copy's one change Verilator's -j 10 made -j 2 (a")
A("  single-threaded model), make -j 1, under a 4 GB cap, in the lab's CPU slot with no device node visible. obj_unit/Vtb, accum and")
A("  settle_count are byte-equal to v31-counts' build; obj_vpu/Vtb embeds its build paths. " + src['functional_check'].replace('\n', ' '))
A(f"  The net maps were trained on this binary (`train_maps.py`): byte-equal to v31-counts' maps: {src['maps_sha256'] == src['maps_v31counts_sha256']}.")
A("- **fp32, at GEMM states:** E210's committed driver `tools/claims-v3/e210/desk/count_e210.py`, unchanged (run_kinds.py's measurement: one warm op,")
A("  a coverage run of two ops with the accumulator checked word for word, one op counted by settle_count; C loaded as a GEMM accumulation of j")
A("  ops of the kind, here its own one pair): S1 j = 3, 11, 19, 27 of 32 ops, S2 j = 15, 47, 79, 111 of 128 ops, the one file at both. Units:")
A("  E210's definition to the last digit (signal fin edges a MAC = VPU nets_map a MAC x k_sig, clock fin edges = clock-net toggles a MAC x 39.8;")
A(f"  k_sig lo {c32['k_sig_lo']:.4f}, hi {c32['k_sig_hi']:.4f}, read off E210's committed switch-counts-e210.json).")
A("- **fp16 and int8, at the launch points:** `run_kinds.py` (the command behind counts-v2.json, from which MM1-v1's switch table was made), one row")
A("  a tile at three points of a 0.5 s launch of that pair repeated (fp16 n0 91,575 / 274,725 / 457,875; int8 157,232 / 471,698 / 786,163), in")
A("  MM1-v1's switch-table form by design C's formula (signal fin edges = VPU nets_map x g x 14.5, g = 4,132.5 or 6,494.8 gate toggles a random")
A("  fp32 MAC over the committed fp32 random unit nets_map; clock x 39.8), rounded as the table rounds. For these kinds the footing's one pair")
A("  repeated is what the card's pool holds (gen `tiles`, one file); the launch points' accumulator states are the footing's, not a GEMM's.")
A("- **Footings and labels:** every row carries `counts_footing`, MM1-v3.1's `COUNT_FOOTING` for its format verbatim (`mm1_v31.py` at 8bde0182),")
A("  and `counts_footing_mm1_v3`, MM1-v3's verbatim (`mm1_v3.py`); both checked by `ast`. fp32 counted (desk) at GEMM states; fp16 estimated")
A("  (desk), not counted: RTL toggles x the fp32 gate/RTL ratio; int8 counted (desk) around the arithmetic only (the behavioural RTL has no nets")
A("  inside the int8 multiply, product sum and add; MM1-v3's m_int8 carries the rest). Every row and tile row also carries the bench sources")
A("  manifest sha256.")
A(f"- **CPU:** every build and bench run inside the lab's CPU slot (nice 10) with no device node visible, one slot job at a time, one bench process")
A(f"  (`--jobs 1`); {src['slot_minutes_total']} slot-minutes in {len(src['slot_jobs'])} closed slot jobs (`SOURCES.json`).")
A('')
A("## 3. The counts (desk; fin edges a multiply-add; `counts-e214.csv`, every field in the JSON files)")
A('')
A('| kind | format | footing | tiles | points | signal lo | clock | fin edges lo / hi | valid share | minus committed random (lo) |')
A('|---|---|---|---:|---:|---:|---:|---:|---:|---:|')
for r in rows:
    foot = r['footing_class'].split(' ')[0] if r['fmt'] == 'fp32' else 'launch points'
    A(f"| {r['mm1_v3_kind']} | {r['fmt']} | {foot} | {r['n_tiles']} | {r['n_points']} | {fr(r['signal_lo_per_mac'])} | {fr(r['clock_per_mac'])} | "
      f"{fr(r['fin_edges_lo_per_mac'])} / {fr(r['fin_edges_hi_per_mac'])} | {float(r['valid_share']):.3f} | {fr(r['minus_committed_random_lo_per_mac'])} |")
A('')
A("The committed random rows for reference (fin edges lo a MAC): fp32 at GEMM states S1 73,159, S2 72,611 (E210); fp16 30,238 and int8 1,927")
A("(MM1-v1's switch table at the launch points). The valid share is fp32's valid lane slots a MAC, or for fp16 and int8 the clocked-register")
A("share between the committed zeros and ones rows, as `energy_v3.counts()` computes it. "
  + ("No counted tile holds a zero element (`tile-zero-shares.json`)." if not any(v['any_zero'] for kk, v in zs.items() if not kk.startswith('xcheck'))
     else "Zero elements: " + '; '.join(f"{kk} A {v['A_zero_share_mean']:.3f}, B {v['B_zero_share_mean']:.3f}" for kk, v in sorted(zs.items())
                                        if v['any_zero'] and not kk.startswith('xcheck')) + " (`tile-zero-shares.json`)."))
A('')
A("fp32 rows at S2 that no E214 arm reads are counted for completeness (their `note` says so); E214's KB >= 2 fp32 arms read S2: "
  + '; '.join(f"`{kk}` by {', '.join(v)}" for kk, v in sorted(fp32_s2_arms.items())) + '.')
A('')
A('## 4. How MM1-v3.1 reads them')
A('')
A("- The files have the names, keys and fields of `tools/matmul/mm1/v3.1/counts/`, so they merge the way `energy_v31.py` merges that folder's")
A("  tables into MM1-v3's (its asserts hold: no key here is a key of E210's S1 / S2 table, of v3.1's counts or of MM1-v1's switch table, checked):")
A("  fp32: `counts-fp32-gemm-states.json` -> `shapes` -> `S1` (KB 1) or `S2` (KB >= 2) -> `pattern:<tile name>`, so `counts31()` reads")
A("  S = signal_lo x 4,096 an op and v = valid_slots; fp16 and int8: `counts-fp16-int8-launch.json` -> `rows` -> `<format>.pattern:<tile name>`")
A("  (MM1-v1's switch-table row form), so `counts31()` reads S = `fin_edges_per_op.signal_lo_zero_delay` and v from")
A("  `per_mac.register_bits_clocked`; `tiles` holds each tile's own row.")
gated = [r for r in rows if float(r['valid_share']) < 0.999]
zk = sorted(kk for kk, v in zs.items() if v['any_zero'] and not kk.startswith('xcheck'))
A("- **The gate.** " + ('; '.join(f"`{r['mm1_v3_kind']}` ({r['fmt']}, {r['footing_class'].split(' ')[0] if r['fmt'] == 'fp32' else 'launch'}) reads a valid share of "
                                    f"{float(r['valid_share']):.3f}" for r in gated) if gated else 'Every row reads a valid share of 1.000')
  + f"; tiles with zero elements: {', '.join(zk) if zk else 'none'} (`tile-zero-shares.json`). MM1-v3's `gate_shares()`, which MM1-v3.1 uses,")
A("  gives fp32 and fp16 a micro-op gate only for the kinds `zeros`, `arow50` (E210's, half the multiply-adds gated: 0.5) and `sparse50`, so for a")
A("  `pattern:<name>` kind it gives none, whatever the count's valid share; int8's gate is 1 - v from the count itself (`i8_sp_bh`, half of")
A("  B zero, reads v 1.000 at the launch points, as the int8 real tiles with zeros read: no int8 gate). How a float pattern")
A("  kind with zero rows is gated in the UNREAD test is that test's to declare before any E214 energy is read; the counts here carry v.")
A(f"- **Merge check** (`merge-check.json`, desk, no energy computed): these rows merged by energy_v31's own loop into a fresh import of it,")
A(f"  then its `counts31()` asked at every (format, kind, KB) cell an E214 arm runs: {mg['summary']}.")
A("- E214's sparse50 arms (`pattern:sparse50f`, `pattern:sparse50h`, `pattern:sparse50i` by `data_v3.e212_kind`) read as the committed")
A("  `sparse50` kind: data_v31's `SPARSE_GEN` alias does that for E212's sparse50f and sparse50i; an E214 reader needs the same alias for all")
A("  three (sparse50h included). Not here: a count for them.")
A("- Not here: phi (the lines' data share). MM1-v3.1's item 7 takes `energy_v3.phi_of`, else the mean of `kinds_v3.phi` over the kind's committed")
A("  tile files (for `pattern:<name>` it looks in `inputs/e212tiles/`, where E214's tiles are not), else a generator law, else no phi (NOT")
A("  FORECAST in energy). E214's tile files are committed in `tools/claims-v3/e214/proposal/src/tiles/`; using them is the reader's to declare.")
A('')
A('## 5. What these counts do not cover, the gaps, and NOT RUN')
A('')
A("- The memory path, the core, TenB, cell internals and the full-custom register file are not in any count; `hi` is the timed estimate (glitches")
A("  by the gate-level calibration's ratio), `lo` zero delay. fp16 is not gate-level; int8 leaves out its arithmetic (section 2).")
A("- GEMM states are sampled (four depths a state). E214's KB 8 fp32 arms (gemmL4x8x8: `bh3_e3`, `sp_ar4`) read the S2 states (gemmL1x1x4's")
A("  depths, up to 111 of 128 ops), as MM1-v3 reads E210's S2 for every KB >= 2; their own C runs 256 ops deep.")
A("- fp16 and int8 at the launch points model a launch of ONE tile pair repeated, at a launch's accumulator states, not a GEMM's (MM1-v1's")
A("  footing); for E214's one-file kinds the pair is the card's.")
A(f"- `sparse50h`: the committed fp16 sparse50 row stands for its pools; the cross-check of its pair-0 file is REPORTED only (section 0).")
A("- **NOT RUN:** any card, any simulator other than this RTL bench (no sys_emu), any fit, a gate-level fp16 or int8 count, GEMM-state counts for")
A("  fp16 and int8, a phi for the new kinds, and MM1-v3.1, MM1-v3 or MM1-v2 run with these rows (the UNREAD test of E214's runs is its own lane's).")
A('')
A('## 6. The freeze')
A('')
A("No E214 measurement (no file of E214's seven data folders, `docs/reports/data/2026-11-18-e214-*`) and no E215 datum was opened by this lane: the")
A("scope read E214's registered arms.json and tile files only. The sha256 of these files (SHA256SUMS) therefore stands before any read of")
A(f"E214's energy residuals under these counts. Final: {WHEN}.")
A('')
A('## 7. Files and how to reproduce')
A('')
A("`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json` (the tables), `counts-e214.csv` and `counts-e214-tiles.csv` (the same rows; a tile")
A("per row for the launch-point kinds), `scope-e214.json` and `.txt` (what needed a count), `recount-rule.txt`, `recount-check.*` (the re-counts),")
A("`crosscheck-sparse50h.*`, `merge-check.json`, `tile-zero-shares.json`, `SOURCES.json` (every source's sha256, the binaries and maps with v31-counts' beside, the")
A("drivers, the committed references, the registration files read, every tile, the bench outputs, the slot jobs), `raw/` (the bench drivers' own")
A("outputs), `scripts/` (this lane's scripts as run, with the box's paths replaced by `<W>`, `<LAB>`, `<CORE_ET>`, `<VERILATOR_BIN>`, `~`; order:")
A("s01 sources, s02 build, s03 scope, s04 functional check and E212's tiles, s05 maps, s06a the re-count rule, s06 re-counts, s06b their")
A("comparison, s07a specs, s07 fp32 and s08 fp16 and int8 with the cross-check (s07_chain.sh runs both, after passcheck.py reads the")
A("re-count's MATCH), s09 tables, s09b the merge check, s10 zero shares, s11 sources (s09-s11 as one slot job, s09_desk_inner.sh), s12 this")
A("README, s13 this folder, s14 its check, s15 the lane's result; helpers env.sh, run_slot.sh, inventory_e214.py, keys.py, wait_file.sh).")
A("Interpreter `/usr/bin/python3` 3.12.3 (`-I -B`),")
A(f"numpy {src.get('numpy')}; {src['gxx']}; {src['verilator']}.")
open(os.path.join(C, 'README.md'), 'w').write('\n'.join(out) + '\n')
print(f"README.md written: {len(out)} lines")
