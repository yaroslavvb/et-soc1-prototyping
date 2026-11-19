# E214's switch counts: the transistor-switch counts for E214's operand-pattern tiles that had none (Q225, Thu 19 Nov 2026)

Desk counts, not measurements. E214 (the model session's third matmul sweep, 1118-mmsweep3, registered in `tools/claims-v3/e214/`) ran
20 operand-pattern tiles that no committed count covers; MM1-v3.1's `counts31()` and MM1-v3's `counts()` return no count for any
of them, so their runs could not be priced by the switch route. This folder holds those counts, made exactly as MM1-v3.1's committed
counts were (`tools/matmul/mm1/v3.1/counts/`, landed 3e8991d0, with its verifier's and fixer's lessons), with the lab's RTL bench
(`rtl-sim/fma_toggle_v2` at GitHub main 8bde0182, Verilator 5.042, the open core-et RTL at b38a1a31) on the lab box aifoundry2's desk, in
each format's committed footing. Nothing here is fitted, and nothing here was read from a card: the counts depend on the tile bytes alone.
E214's tiles and arms come from its registration and its kit's source only; **no E214 measurement file was read** by this lane.

The owner's words that started the matmul model (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want you
to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and
clock cycles."

## 0. On one screen

- **Counted:** 9 fp32 kinds at a GEMM's accumulator states (S1 for KB 1 and S2 for KB >= 2, as E210 and v31-counts), 5 fp16 and 6 int8
  kinds at the harness's launch points (MM1-v1's switch-table footing): 105 bench points in the tables, every accumulator check 0 mismatched words.
  These are E214's 20 plan tiles of gen `tiles` (each a single tile pair the card's pool repeats), run by 33 of E214's 361 arms.
- **Before any new count, two committed rows were re-counted** (`recount-check.*`; the rule written and hashed before they ran,
  `recount-rule.txt`): MM1-v3.1's fp32 `pattern:fld_mant` at S1 and `pattern:den8` at S2 (count_e210.py), and its int8 `pattern:i8_pm1` and fp16
  `pattern:fld16_mant` at the launch points (run_kinds.py): 14 bench points; **1,971 of 1,971 reported numbers bit-equal** to the
  committed points, every row number equal: **MATCH**.
- **Not counted, because committed:** E214's random, zeros and ones arms (291 arms: the lab's committed kinds, their files the
  lab's kind tiles byte for byte) and its three `sparse50` pools (gen sparse50: rgm136's host draws every pool tile but pair 0 by its own
  sparse50 law; the file is pair 0): `sparse50f` and `sparse50i` are the lab's sparse50 tiles byte for byte, the committed sparse50 kind (as
  E212's were); `sparse50h`'s file is a new draw of the same law, so its arms are the committed fp16 sparse50 kind. **Cross-check**
  (`crosscheck-sparse50h.*`, REPORTED, not a row): the sparse50h file counted at the launch points reads signal 0.9466,
  fin edges lo a MAC 0.9530 and valid share 1.0516 of the committed fp16 sparse50 row
  (its A holds 50.2% zeros and B 51.0%, the lab's tile 44.5% and 50.2%): two one-tile draws of one law differ by
  this much at the launch-point footing, whose committed sparse50 row is itself one tile; the card's pools draw thousands of tiles.
- **The rule a pool of fewer than 3 files is measured at every file** holds trivially: every counted kind is one file, measured at that file.
  The e37 lesson (a card pool's pair 0 that the desk pool leaves out) does not arise: a one-file `tiles` pool holds no other pair.

## 1. What needed a count (scope)

From E214's registered `proposal/src/arms.json` (sha256 68b85ab82c196bd9...: 361 arms, 32 (format, kind) pairs), each arm's kind
named as MM1-v3's data code names an arm of this form (`data_v3.e212_kind`: `rnd` -> random, zeros, ones, else `pattern:<tile name>`),
and MM1-v3.1's `energy_v31.counts31()` and MM1-v3's `energy_v3.counts()` asked at every (format, kind, KB) an arm runs (`scope-e214.json`,
`scope-e214.txt`); every tile file also compared by sha256 with the lab's kind tiles and with every tile v3.1's committed counts measured.

| format | kind | gen | arms | KB of its arms | states | committed count | verdict |
|---|---|---|---:|---|---|---|---|
| fp16 | `pattern:h_ar_e3` | tiles | 2 | 1 | launch points | none | NEEDS COUNT |
| fp16 | `pattern:h_bh_sm2` | tiles | 2 | 1 | launch points | none | NEEDS COUNT |
| fp16 | `pattern:h_hi_all16a8` | tiles | 1 | 1 | launch points | none | NEEDS COUNT |
| fp16 | `pattern:h_hi_s11a5` | tiles | 1 | 1 | launch points | none | NEEDS COUNT |
| fp16 | `pattern:h_ka_m9` | tiles | 1 | 1 | launch points | none | NEEDS COUNT |
| fp32 | `pattern:ar_e5` | tiles | 2 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:bh3_e3` | tiles | 3 | 1, 8 | S1, S2 | none | NEEDS COUNT |
| fp32 | `pattern:hi_all32a25` | tiles | 1 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:hi_e3s27a20` | tiles | 1 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:hi_m23a7` | tiles | 1 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:hi_s24a20` | tiles | 1 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:ka_e3m8` | tiles | 1 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:kb_s5m` | tiles | 2 | 1 | S1 | none | NEEDS COUNT |
| fp32 | `pattern:sp_ar4` | tiles | 2 | 1, 8 | S1, S2 | none | NEEDS COUNT |
| int8 | `pattern:i8_ar_d13` | tiles | 2 | 1 | launch points | none | NEEDS COUNT |
| int8 | `pattern:i8_bh_hi12` | tiles | 2 | 1 | launch points | none | NEEDS COUNT |
| int8 | `pattern:i8_bh_lo11` | tiles | 3 | 1, 8 | launch points | none | NEEDS COUNT |
| int8 | `pattern:i8_hi_b28` | tiles | 1 | 1 | launch points | none | NEEDS COUNT |
| int8 | `pattern:i8_hi_b32a8` | tiles | 2 | 1, 8 | launch points | none | NEEDS COUNT |
| int8 | `pattern:i8_sp_bh` | tiles | 2 | 1, 8 | launch points | none | NEEDS COUNT |
| fp16 | `ones` | tiles | 17 | 1, 2, 4, 5, 6, 13, 14, 16 | launch points | yes | COMMITTED |
| fp16 | `pattern:sparse50h` | sparse50 | 6 | 1, 9, 12, 16 | launch points | as sparse50 | COMMITTED (the sparse50 kind: gen sparse50, the file is pair 0) |
| fp16 | `random` | randn | 17 | 1, 2, 3, 7, 10, 11, 12, 13, 14, 16 | launch points | yes | COMMITTED |
| fp16 | `zeros` | tiles | 18 | 1, 2, 5, 9, 10, 11, 12, 13, 14, 16 | launch points | yes | COMMITTED |
| fp32 | `ones` | tiles | 29 | 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 16, 18, 20, 24, 48 | S1, S2 | yes | COMMITTED |
| fp32 | `pattern:sparse50f` | sparse50 | 11 | 1, 4, 7, 10, 12, 14, 16 | S1, S2 | as sparse50 | COMMITTED (the sparse50 kind: gen sparse50, the file is pair 0) |
| fp32 | `random` | randn | 31 | 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 16, 24, 28, 32 | S1, S2 | yes | COMMITTED |
| fp32 | `zeros` | tiles | 91 | 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13, 16, 24, 40 | S1, S2 | yes | COMMITTED |
| int8 | `ones` | tiles | 12 | 1, 3, 4, 6, 8, 12, 13, 14 | launch points | yes | COMMITTED |
| int8 | `pattern:sparse50i` | sparse50 | 20 | 1, 2, 3, 4, 6, 8, 11, 12, 13, 16, 20 | launch points | as sparse50 | COMMITTED (the sparse50 kind: gen sparse50, the file is pair 0) |
| int8 | `random` | randn | 49 | 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 20 | launch points | yes | COMMITTED |
| int8 | `zeros` | tiles | 27 | 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 14, 16, 24 | launch points | yes | COMMITTED |

The 20 kinds marked NEEDS COUNT are exactly `inventory_e214.NEW` (checked: True). None of their files
equals a lab kind tile or a tile the committed v3.1 counts measured, and E214.md section 2 found none of its 21 new files equal to any of the
lab's 1,746 distinct 2,048-byte tile files. Of the fp32 kinds, only `bh3_e3` and `sp_ar4` run at KB >= 2 (gemmL4x8x8, KB 8); every fp32 kind
is counted at both S1 and S2 anyway (as v31-counts counted every kind at both), and each row's `note` names the E214 arms that read it.

## 2. How (desk)

- **The bench:** `rtl-sim/fma_toggle_v2` by `git archive` of GitHub main 8bde0182 (every file equal to its blob; its source manifest identical
  to the one v31-counts built from at 6efdb002), core-et's rtl, dv/inc and extern by `git archive` of b38a1a31 (1,268 files, the manifest
  identical to v31-counts'), built with Verilator 5.042 and the Makefile's -fno-dfg, the copy's one change Verilator's -j 10 made -j 2 (a
  single-threaded model), make -j 1, under a 4 GB cap, in the lab's CPU slot with no device node visible. obj_unit/Vtb, accum and
  settle_count are byte-equal to v31-counts' build; obj_vpu/Vtb embeds its build paths. fcheck_all.sh PASS on this build (JOBS=1): unit fp32 40,000 of 40,000 exact; unit fp16 39,701 exact + 299 named residue; vpu fp32 22,016, fp16 22,016, int8 18,944 accumulator words exact, 0 mismatched; zero gate 63 cases, 0 differ (the same tallies as v31-counts').
  The net maps were trained on this binary (`train_maps.py`): byte-equal to v31-counts' maps: True.
- **fp32, at GEMM states:** E210's committed driver `tools/claims-v3/e210/desk/count_e210.py`, unchanged (run_kinds.py's measurement: one warm op,
  a coverage run of two ops with the accumulator checked word for word, one op counted by settle_count; C loaded as a GEMM accumulation of j
  ops of the kind, here its own one pair): S1 j = 3, 11, 19, 27 of 32 ops, S2 j = 15, 47, 79, 111 of 128 ops, the one file at both. Units:
  E210's definition to the last digit (signal fin edges a MAC = VPU nets_map a MAC x k_sig, clock fin edges = clock-net toggles a MAC x 39.8;
  k_sig lo 32.9949, hi 51.8560, read off E210's committed switch-counts-e210.json).
- **fp16 and int8, at the launch points:** `run_kinds.py` (the command behind counts-v2.json, from which MM1-v1's switch table was made), one row
  a tile at three points of a 0.5 s launch of that pair repeated (fp16 n0 91,575 / 274,725 / 457,875; int8 157,232 / 471,698 / 786,163), in
  MM1-v1's switch-table form by design C's formula (signal fin edges = VPU nets_map x g x 14.5, g = 4,132.5 or 6,494.8 gate toggles a random
  fp32 MAC over the committed fp32 random unit nets_map; clock x 39.8), rounded as the table rounds. For these kinds the footing's one pair
  repeated is what the card's pool holds (gen `tiles`, one file); the launch points' accumulator states are the footing's, not a GEMM's.
- **Footings and labels:** every row carries `counts_footing`, MM1-v3.1's `COUNT_FOOTING` for its format verbatim (`mm1_v31.py` at 8bde0182),
  and `counts_footing_mm1_v3`, MM1-v3's verbatim (`mm1_v3.py`); both checked by `ast`. fp32 counted (desk) at GEMM states; fp16 estimated
  (desk), not counted: RTL toggles x the fp32 gate/RTL ratio; int8 counted (desk) around the arithmetic only (the behavioural RTL has no nets
  inside the int8 multiply, product sum and add; MM1-v3's m_int8 carries the rest). Every row and tile row also carries the bench sources
  manifest sha256.
- **CPU:** every build and bench run inside the lab's CPU slot (nice 10) with no device node visible, one slot job at a time, one bench process
  (`--jobs 1`); 42.33 slot-minutes in 8 closed slot jobs (`SOURCES.json`).

## 3. The counts (desk; fin edges a multiply-add; `counts-e214.csv`, every field in the JSON files)

| kind | format | footing | tiles | points | signal lo | clock | fin edges lo / hi | valid share | minus committed random (lo) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| pattern:ar_e5 | fp32 | S1 | 1 | 4 | 5,802 | 7,388 | 13,190 / 16,506 | 1.000 | -59,969 |
| pattern:ar_e5 | fp32 | S2 | 1 | 4 | 5,517 | 7,388 | 12,905 / 16,059 | 1.000 | -59,706 |
| pattern:bh3_e3 | fp32 | S1 | 1 | 4 | 3,431 | 7,388 | 10,819 / 12,780 | 1.000 | -62,340 |
| pattern:bh3_e3 | fp32 | S2 | 1 | 4 | 2,612 | 7,388 | 10,000 / 11,493 | 1.000 | -62,611 |
| pattern:hi_all32a25 | fp32 | S1 | 1 | 4 | 74,600 | 7,388 | 81,987 / 124,631 | 1.000 | 8,829 |
| pattern:hi_all32a25 | fp32 | S2 | 1 | 4 | 74,873 | 7,388 | 82,261 / 125,062 | 1.000 | 9,650 |
| pattern:hi_e3s27a20 | fp32 | S1 | 1 | 4 | 78,181 | 7,388 | 85,569 / 130,260 | 1.000 | 12,410 |
| pattern:hi_e3s27a20 | fp32 | S2 | 1 | 4 | 75,896 | 7,388 | 83,284 / 126,669 | 1.000 | 10,672 |
| pattern:hi_m23a7 | fp32 | S1 | 1 | 4 | 67,627 | 7,388 | 75,015 / 113,673 | 1.000 | 1,856 |
| pattern:hi_m23a7 | fp32 | S2 | 1 | 4 | 67,397 | 7,388 | 74,784 / 113,311 | 1.000 | 2,173 |
| pattern:hi_s24a20 | fp32 | S1 | 1 | 4 | 73,234 | 7,388 | 80,622 / 122,485 | 1.000 | 7,463 |
| pattern:hi_s24a20 | fp32 | S2 | 1 | 4 | 72,265 | 7,388 | 79,652 / 120,962 | 1.000 | 7,041 |
| pattern:ka_e3m8 | fp32 | S1 | 1 | 4 | 1,637 | 7,388 | 9,025 / 9,961 | 1.000 | -64,134 |
| pattern:ka_e3m8 | fp32 | S2 | 1 | 4 | 1,628 | 7,388 | 9,016 / 9,946 | 1.000 | -63,596 |
| pattern:kb_s5m | fp32 | S1 | 1 | 4 | 1,489 | 7,388 | 8,876 / 9,727 | 1.000 | -64,282 |
| pattern:kb_s5m | fp32 | S2 | 1 | 4 | 1,519 | 7,388 | 8,906 / 9,774 | 1.000 | -63,705 |
| pattern:sp_ar4 | fp32 | S1 | 1 | 4 | 1,587 | 5,823 | 7,410 / 8,317 | 0.500 | -65,749 |
| pattern:sp_ar4 | fp32 | S2 | 1 | 4 | 1,610 | 5,823 | 7,434 / 8,354 | 0.500 | -65,178 |
| pattern:h_ar_e3 | fp16 | launch points | 1 | 3 | 1,830 | 3,694 | 5,524 / 6,570 | 1.000 | -24,714 |
| pattern:h_bh_sm2 | fp16 | launch points | 1 | 3 | 11,755 | 3,694 | 15,448 / 22,168 | 1.000 | -14,790 |
| pattern:h_hi_all16a8 | fp16 | launch points | 1 | 3 | 28,855 | 3,694 | 32,548 / 49,043 | 1.000 | 2,310 |
| pattern:h_hi_s11a5 | fp16 | launch points | 1 | 3 | 25,970 | 3,694 | 29,663 / 44,509 | 1.000 | -575 |
| pattern:h_ka_m9 | fp16 | launch points | 1 | 3 | 952 | 3,694 | 4,646 / 5,191 | 1.000 | -25,592 |
| pattern:i8_ar_d13 | int8 | launch points | 1 | 3 | 1,446 | 430 | 1,876 / 2,702 | 1.000 | -51 |
| pattern:i8_bh_hi12 | int8 | launch points | 1 | 3 | 795 | 430 | 1,225 / 1,680 | 1.000 | -702 |
| pattern:i8_bh_lo11 | int8 | launch points | 1 | 3 | 145 | 430 | 575 / 657 | 1.000 | -1,352 |
| pattern:i8_hi_b28 | int8 | launch points | 1 | 3 | 287 | 430 | 717 / 881 | 1.000 | -1,210 |
| pattern:i8_hi_b32a8 | int8 | launch points | 1 | 3 | 1,005 | 430 | 1,435 / 2,009 | 1.000 | -492 |
| pattern:i8_sp_bh | int8 | launch points | 1 | 3 | 149 | 430 | 579 / 664 | 1.000 | -1,348 |

The committed random rows for reference (fin edges lo a MAC): fp32 at GEMM states S1 73,159, S2 72,611 (E210); fp16 30,238 and int8 1,927
(MM1-v1's switch table at the launch points). The valid share is fp32's valid lane slots a MAC, or for fp16 and int8 the clocked-register
share between the committed zeros and ones rows, as `energy_v3.counts()` computes it. Zero elements: fp32.e214.sp_ar4 A 0.500, B 0.000; int8.e214.i8_hi_b28 A 0.000, B 0.002; int8.e214.i8_hi_b32a8 A 0.000, B 0.001; int8.e214.i8_sp_bh A 0.000, B 0.500 (`tile-zero-shares.json`).

fp32 rows at S2 that no E214 arm reads are counted for completeness (their `note` says so); E214's KB >= 2 fp32 arms read S2: `pattern:bh3_e3` by 4x8x8-fp32-bh3_e3; `pattern:sp_ar4` by 4x8x8-fp32-sp_ar4.

## 4. How MM1-v3.1 reads them

- The files have the names, keys and fields of `tools/matmul/mm1/v3.1/counts/`, so they merge the way `energy_v31.py` merges that folder's
  tables into MM1-v3's (its asserts hold: no key here is a key of E210's S1 / S2 table, of v3.1's counts or of MM1-v1's switch table, checked):
  fp32: `counts-fp32-gemm-states.json` -> `shapes` -> `S1` (KB 1) or `S2` (KB >= 2) -> `pattern:<tile name>`, so `counts31()` reads
  S = signal_lo x 4,096 an op and v = valid_slots; fp16 and int8: `counts-fp16-int8-launch.json` -> `rows` -> `<format>.pattern:<tile name>`
  (MM1-v1's switch-table row form), so `counts31()` reads S = `fin_edges_per_op.signal_lo_zero_delay` and v from
  `per_mac.register_bits_clocked`; `tiles` holds each tile's own row.
- **The gate.** `pattern:sp_ar4` (fp32, S1) reads a valid share of 0.500; `pattern:sp_ar4` (fp32, S2) reads a valid share of 0.500; tiles with zero elements: fp32.e214.sp_ar4, int8.e214.i8_hi_b28, int8.e214.i8_hi_b32a8, int8.e214.i8_sp_bh (`tile-zero-shares.json`). MM1-v3's `gate_shares()`, which MM1-v3.1 uses,
  gives fp32 and fp16 a micro-op gate only for the kinds `zeros`, `arow50` (E210's, half the multiply-adds gated: 0.5) and `sparse50`, so for a
  `pattern:<name>` kind it gives none, whatever the count's valid share; int8's gate is 1 - v from the count itself (`i8_sp_bh`, half of
  B zero, reads v 1.000 at the launch points, as the int8 real tiles with zeros read: no int8 gate). How a float pattern
  kind with zero rows is gated in the UNREAD test is that test's to declare before any E214 energy is read; the counts here carry v.
- **Merge check** (`merge-check.json`, desk, no energy computed): these rows merged by energy_v31's own loop into a fresh import of it,
  then its `counts31()` asked at every (format, kind, KB) cell an E214 arm runs: 25 (format, kind, KB) cells of E214's NEEDS-COUNT kinds now return a count; 129 committed-kind cells unchanged; problems 0.
- E214's sparse50 arms (`pattern:sparse50f`, `pattern:sparse50h`, `pattern:sparse50i` by `data_v3.e212_kind`) read as the committed
  `sparse50` kind: data_v31's `SPARSE_GEN` alias does that for E212's sparse50f and sparse50i; an E214 reader needs the same alias for all
  three (sparse50h included). Not here: a count for them.
- Not here: phi (the lines' data share). MM1-v3.1's item 7 takes `energy_v3.phi_of`, else the mean of `kinds_v3.phi` over the kind's committed
  tile files (for `pattern:<name>` it looks in `inputs/e212tiles/`, where E214's tiles are not), else a generator law, else no phi (NOT
  FORECAST in energy). E214's tile files are committed in `tools/claims-v3/e214/proposal/src/tiles/`; using them is the reader's to declare.

## 5. What these counts do not cover, the gaps, and NOT RUN

- The memory path, the core, TenB, cell internals and the full-custom register file are not in any count; `hi` is the timed estimate (glitches
  by the gate-level calibration's ratio), `lo` zero delay. fp16 is not gate-level; int8 leaves out its arithmetic (section 2).
- GEMM states are sampled (four depths a state). E214's KB 8 fp32 arms (gemmL4x8x8: `bh3_e3`, `sp_ar4`) read the S2 states (gemmL1x1x4's
  depths, up to 111 of 128 ops), as MM1-v3 reads E210's S2 for every KB >= 2; their own C runs 256 ops deep.
- fp16 and int8 at the launch points model a launch of ONE tile pair repeated, at a launch's accumulator states, not a GEMM's (MM1-v1's
  footing); for E214's one-file kinds the pair is the card's.
- `sparse50h`: the committed fp16 sparse50 row stands for its pools; the cross-check of its pair-0 file is REPORTED only (section 0).
- **NOT RUN:** any card, any simulator other than this RTL bench (no sys_emu), any fit, a gate-level fp16 or int8 count, GEMM-state counts for
  fp16 and int8, a phi for the new kinds, and MM1-v3.1, MM1-v3 or MM1-v2 run with these rows (the UNREAD test of E214's runs is its own lane's).

## 6. The freeze

No E214 measurement (no file of E214's seven data folders, `docs/reports/data/2026-11-18-e214-*`) and no E215 datum was opened by this lane: the
scope read E214's registered arms.json and tile files only. The sha256 of these files (SHA256SUMS) therefore stands before any read of
E214's energy residuals under these counts. Final: Thu 19 Nov 2026 09:58:49 PST.

## 7. Files and how to reproduce

`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json` (the tables), `counts-e214.csv` and `counts-e214-tiles.csv` (the same rows; a tile
per row for the launch-point kinds), `scope-e214.json` and `.txt` (what needed a count), `recount-rule.txt`, `recount-check.*` (the re-counts),
`crosscheck-sparse50h.*`, `merge-check.json`, `tile-zero-shares.json`, `SOURCES.json` (every source's sha256, the binaries and maps with v31-counts' beside, the
drivers, the committed references, the registration files read, every tile, the bench outputs, the slot jobs), `raw/` (the bench drivers' own
outputs), `scripts/` (this lane's scripts as run, with the box's paths replaced by `<W>`, `<LAB>`, `<CORE_ET>`, `<VERILATOR_BIN>`, `~`; order:
s01 sources, s02 build, s03 scope, s04 functional check and E212's tiles, s05 maps, s06a the re-count rule, s06 re-counts, s06b their
comparison, s07a specs, s07 fp32 and s08 fp16 and int8 with the cross-check (s07_chain.sh runs both, after passcheck.py reads the
re-count's MATCH), s09 tables, s09b the merge check, s10 zero shares, s11 sources (s09-s11 as one slot job, s09_desk_inner.sh), s12 this
README, s13 this folder, s14 its check, s15 the lane's result; helpers env.sh, run_slot.sh, inventory_e214.py, keys.py, wait_file.sh).
Interpreter `/usr/bin/python3` 3.12.3 (`-I -B`),
numpy 1.26.4; g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0; Verilator 5.042 2025-11-02 rev v5.042.
