# MM1-v3.1 inputs: the transistor-switch counts MM1-v3 could not make (Q217, Wed 18 Nov 2026)

Desk counts, not measurements. MM1-v3's README (section 7) says: "No new count was made this round (no simulator here), so E212's plan
tiles, the real tiles and any new pattern are NOT FORECAST in energy and carry no count." This folder holds those counts, made with the
lab's RTL bench (`rtl-sim/fma_toggle_v2` at GitHub main 6efdb002, Verilator 5.042, the open core-et RTL at b38a1a31) on the lab box
aifoundry2's desk, in each format's committed footing, so that MM1-v3's switch route can price those kinds with no constant changed.
Nothing here is fitted, and nothing here was read from a card: the counts depend on the tile bytes alone.

The owner's words that started the matmul model (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want you
to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and
clock cycles."

## 0. On one screen

- **Counted:** 13 fp32 kinds at a GEMM's accumulator states (S1 for KB 1 and S2 for KB >= 2, as E210), 7 fp16 and 6 int8 kinds at the
  harness's launch points (MM1-v1's switch-table footing): 179 bench points in the tables, every one behind the bench's accumulator check with 0 mismatched words.
- **Fixed after its verification (section 8):** fp32 real:blind4 at S2 now measures both files of E207's two-file pool: **46,811** fin edges lo a MAC
  (8 points). The first version of this folder read file 0 alone (50,378, +7.6%; S +9.05%). The rule: **a pool of fewer than 3
  files is measured at every file.** The e37 rows now say that the card's e37 pools also hold a random pair, which the desk pool leaves
  out, with its bound: about +182 to +188 fin edges lo a MAC (+0.74% to +0.77%) at S2.
- **Before any new count, committed points were re-counted** (`recount-check.*`): fp32 S1 random at GEMM states against E210's committed
  row: every quantity equal (VPU nets_map ratio 1.000000, signal fin edges lo 1.000000, 8 of 8 points, the same tiles and depths); int8 full at the launch points against counts-v2.json: 1.000000; fp16 random: 0.999961 (VPU nets_map; the committed counts used Verilator 5.052). Rule declared before reading them: every ratio
  that enters the switch route within 0.999-1.001 and every check 0: **MATCH**.
- **A third check:** three of E212's fp32 tiles are byte-equal to lab kinds committed at the launch points; re-counted there: VPU nets_map fp32.bf16trunc 0.999945, fp32.fp16grid 0.999953, fp32.pow2 0.999899.
- **E213:** its 131 registered points use random, zeros, ones and sparse50 in fp32 and int8 only, all with committed counts; MM1-v3 forecast
  the energy of 131 of 131 (`e213-check.json`). **None is NOT FORECAST for want of a count, so no E213 energy forecast
  was made** (no `e213-energy-unread/` folder), and the fix changes no E213 file. No E213 data file was opened.

## 1. What needed a count (scope)

Found by reading MM1-v3 as landed (b1493082): its own energy points and E212's pattern runs through `energy_v3.counts()` and `phi_of()`
(`unpriced-mm1v3.json`: 16 unpriced energy points in 13 groups; 51 E212 pattern runs that MM1-v3 reads for time only), and by a sha256 scan of E212's 30 tile files
against the lab's kind tiles (`tools/claims-v3/kinds`).

- **E212's plan tiles** (one tile pair repeated, gen tiles): fp32 den4, den8, den16, den21, fld_mant, fld_sign, lanes2, pow2, bf16trunc, fp16grid;
  fp16 den16_4, den16_10, fld16_exp, fld16_mant, fld16_sign; int8 i8_den1, i8_den3, i8_den6, i8_pm1. bf16trunc, fp16grid and pow2 are byte-equal
  to the lab kinds of those names, committed at the launch points (counts-v2.json) but never at GEMM states, fp32's footing in MM1-v3, so they
  are counted here. E212's ones, zeros, randn and full files are the lab's committed kinds; its sparse50f and sparse50i arms run gen sparse50
  (the file supplies the pool's pair 0 only, every other pair being drawn by the sparse50 law; the file is byte-equal to the lab's sparse50
  tile): the committed sparse50 kind, not counted again.
- **The real tiles MM1-v3 could not price:** E206's real kind in fp16 and int8 (E206's four real2 tiles a format, in E206's order; fp32's has
  E210's committed GEMM-state row `real`, which MM1-v3 does not price only because `phi_of()` has no rule for it: a phi, not a count); E207's
  real:blind4 in fp32, fp16 and int8 (two tiles each, in E207's order).
- **E207's two other unpriced kinds,** counted because they sit in MM1-v3's energy data with no count: designed:blind3 a_colconst_b_randn (fp32,
  one tile) and e37 (fp32, gen e37: E37's fill of +-1 and +-2 drawn by rgm136's drawTile), counted on 61 desk pairs of that law. Unlike
  E210's random and sparse50 desk pools, whose pair 0 is a draw of their own law, the card's e37 pools hold the lab's fp32 randn.bin as
  pair 0 (E207's e37 arms name it); the desk pool leaves that pair out (note [b] in section 3).
- **E213** (tools/claims-v3/e213, registration only): no new kind. **MM1-v3's E213 forecasts:** no point NOT FORECAST in energy.

## 2. How (desk)

- **The bench:** `rtl-sim/fma_toggle_v2` copied from GitHub main 6efdb002 by `git archive` (every file equal to its blob and to the lab's working
  tree), core-et's rtl, dv/inc and extern from a checkout at b38a1a31 (1,268 files, equal to their source), built with Verilator 5.042 and the
  Makefile's -fno-dfg, the copy's one change Verilator's -j 10 made -j 2 (single-threaded model), under a 4 GB cap, in the lab's CPU slot with
  no device node visible. The functional check (`fcheck_all.sh`) PASSED: unit fp32 40,000 of 40,000 exact; unit fp16 39,701 exact + 299 named
  residue; whole TensorFMA ops fp32 22,016, fp16 22,016, int8 18,944 words exact; zero gate 63 cases, 0 differ. The net maps were trained on
  this binary (`train_maps.py`); they are byte-equal to sw-design-a's (Q202). The fix's re-counts ran on the same binary and maps (copied,
  sha256 equal).
- **fp32, at GEMM states:** E210's committed driver `tools/claims-v3/e210/desk/count_e210.py`, unchanged (run_kinds.py's measurement: one warm op,
  a coverage run of two ops with the accumulator checked word for word, one op counted by settle_count; C loaded as a GEMM accumulation of j
  other tiles of the kind): S1 j = 3, 11, 19, 27 of 32 ops, tiles 0 and 1 of a pooled kind; S2 j = 15, 47, 79, 111 of 128, tile 2.
  **A pool of fewer than 3 files is measured at every file:** for E207's two-file real:blind4 pool, S2 measures tiles 2 and 3 (that is,
  both files, as S1's tiles 0 and 1 do); a one-file kind is its one file at both states. Units: E210's definition to the last digit
  (signal fin edges a MAC = VPU nets_map a MAC x k_sig, clock fin edges = clock-net toggles a MAC x 39.8;
  k_sig lo 32.9949, hi 51.8560, read off MM1-v1's frozen switch table).
- **fp16 and int8, at the launch points:** `run_kinds.py` (the command behind counts-v2.json, from which MM1-v1's switch table was made), one row
  a tile at three points of a 0.5 s launch of that pair repeated (fp16 n0 91,575 / 274,725 / 457,875; int8 157,232 / 471,698 / 786,163), in
  MM1-v1's switch-table form by design C's formula (signal fin edges = VPU nets_map x g x 14.5, g = 4,132.5 or 6,494.8 gate toggles a random
  fp32 MAC over the committed fp32 random unit nets_map; clock x 39.8), rounded as the table rounds. A pooled kind (E206's four tiles, blind4's
  two) is the mean over its tiles of each raw count an op, the card's pool cycling them evenly; every tile is measured.
- **Footings** (MM1-v3 README section 7, carried in every row as `counts_footing`, and on every tile row of `counts-v31-tiles.csv`): fp32
  counted (desk) at GEMM states; fp16 estimated (desk), not counted: RTL toggles x the fp32 gate/RTL ratio; int8 counted (desk) around the
  arithmetic only (the behavioural RTL has no nets inside the int8 multiply, product sum and add; MM1-v3's m_int8 carries the rest).

## 3. The counts (desk; fin edges a multiply-add; `counts-v31.csv`, every field in the JSON files)

| kind | format | footing | tiles | points | signal lo | clock | fin edges lo / hi | valid share | minus committed random (lo) |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| pattern:den4 (E212 plan tile) | fp32 | S1 | 1 | 4 | 16,646 | 7,388 | 24,034 / 33,550 | 1.000 | -49,125 |
| pattern:den4 (E212 plan tile) | fp32 | S2 | 1 | 4 | 17,083 | 7,388 | 24,471 / 34,236 | 1.000 | -48,140 |
| pattern:den8 (E212 plan tile) | fp32 | S1 | 1 | 4 | 23,936 | 7,388 | 31,324 / 45,007 | 1.000 | -41,835 |
| pattern:den8 (E212 plan tile) | fp32 | S2 | 1 | 4 | 24,856 | 7,388 | 32,244 / 46,452 | 1.000 | -40,368 |
| pattern:den16 (E212 plan tile) | fp32 | S1 | 1 | 4 | 39,367 | 7,388 | 46,755 / 69,258 | 1.000 | -26,404 |
| pattern:den16 (E212 plan tile) | fp32 | S2 | 1 | 4 | 38,914 | 7,388 | 46,301 / 68,546 | 1.000 | -26,310 |
| pattern:den21 (E212 plan tile) | fp32 | S1 | 1 | 4 | 48,153 | 7,388 | 55,540 / 83,066 | 1.000 | -17,618 |
| pattern:den21 (E212 plan tile) | fp32 | S2 | 1 | 4 | 47,000 | 7,388 | 54,387 / 81,254 | 1.000 | -18,224 |
| pattern:fld_mant (E212 plan tile) | fp32 | S1 | 1 | 4 | 57,813 | 7,388 | 65,201 / 98,249 | 1.000 | -7,958 |
| pattern:fld_mant (E212 plan tile) | fp32 | S2 | 1 | 4 | 57,507 | 7,388 | 64,894 / 97,768 | 1.000 | -7,717 |
| pattern:fld_sign (E212 plan tile) | fp32 | S1 | 1 | 4 | 13,991 | 7,388 | 21,378 / 29,376 | 1.000 | -51,780 |
| pattern:fld_sign (E212 plan tile) | fp32 | S2 | 1 | 4 | 14,547 | 7,388 | 21,935 / 30,251 | 1.000 | -50,676 |
| pattern:lanes2 (E212 plan tile) | fp32 | S1 | 1 | 4 | 6,525 | 7,388 | 13,913 / 17,643 | 1.000 | -59,246 |
| pattern:lanes2 (E212 plan tile) | fp32 | S2 | 1 | 4 | 6,753 | 7,388 | 14,141 / 18,001 | 1.000 | -58,471 |
| pattern:pow2 (E212 plan tile) | fp32 | S1 | 1 | 4 | 19,857 | 7,388 | 27,245 / 38,596 | 1.000 | -45,914 |
| pattern:pow2 (E212 plan tile) | fp32 | S2 | 1 | 4 | 20,019 | 7,388 | 27,406 / 38,850 | 1.000 | -45,205 |
| pattern:bf16trunc (E212 plan tile) | fp32 | S1 | 1 | 4 | 35,681 | 7,388 | 43,068 / 63,465 | 1.000 | -30,090 |
| pattern:bf16trunc (E212 plan tile) | fp32 | S2 | 1 | 4 | 35,688 | 7,388 | 43,076 / 63,477 | 1.000 | -29,535 |
| pattern:fp16grid (E212 plan tile) | fp32 | S1 | 1 | 4 | 42,696 | 7,388 | 50,084 / 74,490 | 1.000 | -23,075 |
| pattern:fp16grid (E212 plan tile) | fp32 | S2 | 1 | 4 | 42,623 | 7,388 | 50,011 / 74,376 | 1.000 | -22,600 |
| real:blind4 (E207 real tiles (blind4)) [a] | fp32 | S1 | 2 | 8 | 39,342 | 7,388 | 46,730 / 69,219 | 1.000 | -26,429 |
| real:blind4 (E207 real tiles (blind4)) [a] | fp32 | S2 | 2 | 8 | 39,424 | 7,388 | 46,811 / 69,347 | 1.000 | -25,800 |
| designed:blind3 a_colconst_b_randn (E207 designed tile (blind3)) | fp32 | S1 | 1 | 4 | 59,771 | 7,388 | 67,159 / 101,327 | 1.000 | -6,000 |
| designed:blind3 a_colconst_b_randn (E207 designed tile (blind3)) | fp32 | S2 | 1 | 4 | 59,369 | 7,388 | 66,757 / 100,695 | 1.000 | -5,854 |
| e37 (E207 generator kind (e37)) [b] | fp32 | S1 | 61 | 8 | 16,930 | 7,388 | 24,318 / 33,996 | 1.000 | -48,840 |
| e37 (E207 generator kind (e37)) [b] | fp32 | S2 | 61 | 4 | 17,004 | 7,388 | 24,392 / 34,112 | 1.000 | -48,219 |
| pattern:den16_4 (E212 plan tile) | fp16 | launch points | 1 | 3 | 13,361 | 3,694 | 17,055 / 24,692 | 1.000 | -13,183 |
| pattern:den16_10 (E212 plan tile) | fp16 | launch points | 1 | 3 | 18,838 | 3,694 | 22,532 / 33,300 | 1.000 | -7,706 |
| pattern:fld16_exp (E212 plan tile) | fp16 | launch points | 1 | 3 | 10,621 | 3,694 | 14,315 / 20,387 | 1.000 | -15,923 |
| pattern:fld16_mant (E212 plan tile) | fp16 | launch points | 1 | 3 | 19,833 | 3,694 | 23,527 / 34,865 | 1.000 | -6,711 |
| pattern:fld16_sign (E212 plan tile) | fp16 | launch points | 1 | 3 | 9,704 | 3,694 | 13,398 / 18,945 | 1.000 | -16,840 |
| pattern:i8_den1 (E212 plan tile) | int8 | launch points | 1 | 3 | 79 | 430 | 509 / 554 | 1.000 | -1,418 |
| pattern:i8_den3 (E212 plan tile) | int8 | launch points | 1 | 3 | 99 | 430 | 530 / 586 | 1.000 | -1,397 |
| pattern:i8_den6 (E212 plan tile) | int8 | launch points | 1 | 3 | 115 | 430 | 545 / 610 | 1.000 | -1,382 |
| pattern:i8_pm1 (E212 plan tile) | int8 | launch points | 1 | 3 | 1,357 | 430 | 1,787 / 2,563 | 1.000 | -140 |
| real (E206 real tiles) | fp16 | launch points | 4 | 12 | 25,855 | 3,694 | 29,549 / 44,329 | 1.000 | -689 |
| real (E206 real tiles) | int8 | launch points | 4 | 12 | 1,094 | 430 | 1,524 / 2,149 | 1.000 | -403 |
| real:blind4 (E207 real tiles (blind4)) | fp16 | launch points | 2 | 6 | 24,904 | 3,694 | 28,598 / 42,834 | 1.000 | -1,640 |
| real:blind4 (E207 real tiles (blind4)) | int8 | launch points | 2 | 6 | 1,375 | 430 | 1,805 / 2,591 | 1.000 | -122 |

The committed random rows for reference (fin edges lo a MAC): fp32 at GEMM states S1 73,159, S2 72,611 (E210); fp16 30,238 and int8 1,927
(MM1-v1's switch table at the launch points). The valid share is fp32's valid lane slots a MAC, or for fp16 and int8 the clocked-register
share between the committed zeros and ones rows, as `energy_v3.counts()` computes it.

**[a] real:blind4 (fp32).** Both files are measured at both states (8 points each). Per file, fin edges lo a MAC: file 0
(pythia_embed_qkv) 50,273 at S1 and 50,378 at S2; file 1 (qwen_q_down) 43,186 and 43,244. So the files differ by 16.4% while depth moves either
by under 0.2%, and the row goes 46,730 -> 46,811 from S1 to S2 (+0.17%). The first version's S2 row (50,378) measured file 0 alone, and its
S1-to-S2 rise was that selection, not depth (`recount-S2-real_blind4-check.*`; raw points `raw/recount-fp32-S2-real_blind4.json`).

**[b] e37 (fp32).** The desk pool is 61 pure e37 pairs (+-1, +-2). On the card, E207's two e37 arms (b42 gemmL1x3x2 and b43 gemmL3x5x5,
both KB >= 2, so both read the S2 row) name `tools/claims-v3/kinds/tiles/fp32/randn.bin` as the pool's pair 0. rgm136's fillPools
(`tools/claims-v3/e136/rgm136/host/main.cpp`) copies files[0] as tile 0 of the A and B pools, draws the rest, and repeats a pool after
8,192 distinct tiles (so in b43 every 8,192nd tile is randn's); every C tile that pair feeds carries random values from then on. That is
**not counted in the rows.** Its bound, post hoc and desk (`e37-randn-pair0-bound.json`): at S2, tile 2, j 47, an op whose C began with
a randn product counts 31,728 fin edges lo a MAC against 24,460 (+29.7%). That point was counted twice, by E210's `count_e210.py` and by
the verifier's own driver, and the two are equal on every quantity; its pure twin is identical to the S2 row's own point. The verifier
estimates from the layouts that 2.5-2.6% of b42's and b43's op-steps are affected, which would raise the S2 row by +182 to +188 (+0.74% to +0.77%).
No E207 e37 run reads the S1 row.

## 4. How MM1-v3.1 reads them

- fp32: `counts-fp32-gemm-states.json` -> `shapes` -> `S1` (KB 1) or `S2` (KB >= 2) -> the kind as MM1-v3's data names it (`pattern:den4`,
  `real:blind4`, `designed:blind3 a_colconst_b_randn`, `e37`): the same fields as `tools/claims-v3/e210/desk/switch-counts-e210.json`, so
  `counts()` reads S = signal_lo x 4,096 an op and v = valid_slots. Rows with a note (real:blind4, e37) also carry `note` and `tiles_measured`.
- fp16 and int8: `counts-fp16-int8-launch.json` -> `rows` -> `<format>.<kind>` (e.g. `fp16.real`, `int8.pattern:i8_pm1`): MM1-v1's switch-table
  row form, so `counts()` reads S = `fin_edges_per_op.signal_lo_zero_delay` and v from `per_mac.register_bits_clocked` (the row also carries
  `valid_share_v`); `tiles` holds each tile's own row.
- Not here: phi (the lines' data share). MM1-v3's `phi_of()` has no rule for these kinds; `kinds_v3.phi()` over the same tile files gives one by
  MM1-v3's own formula; that is the declaration's to settle, not a count.
- The zero gate: only the int8 real tiles hold zero elements (int8.e206.real: A 3.7%, B 1.9%; int8.e207.real_blind4: A 3.1%, B 8.4%; `tile-zero-shares.json`), and the bench reads them fully valid
  (valid share 1.000 by the clocked-register measure `counts()` uses); no other counted tile has a zero element, so `gate_shares()` (zeros, arow50 and
  sparse50 only) gives these kinds no gate, which is what the bench shows.

## 5. What these counts do not cover, the gaps, and NOT RUN

- The memory path, the core, TenB, cell internals and the full-custom register file are not in any count; `hi` is the timed estimate (glitches
  by the gate-level calibration's ratio), `lo` zero delay. fp16 is not gate-level; int8 leaves out its arithmetic (section 2).
- Verilator 5.042 here against the committed counts' 5.052: equal for fp32 and int8 in the re-counts, fp16 0.99996.
- GEMM states are sampled (four depths; one or two tiles of a pool of 3 or more, every file of a smaller pool). E212's plan tiles at gemmL4x8x8
  (KB 8: fp32 den4, den8, fld_sign, lanes2) read the S2 states (gemmL1x1x4), as MM1-v3 reads E210's S2 for every KB >= 2.
- fp16 and int8 at the launch points model a launch of ONE tile pair repeated; a pooled kind's count is the mean of its tiles each repeated
  alone, while the card alternates them (the pair-to-pair switching between different tiles is not in it).
- e37: the card pools' random pair 0 is not in the rows (note [b]; about +0.74% to +0.77% at S2).
- E210's committed fp32 `real` row (what E206's fp32 real points would be priced from) has the kind of selection note [a] removed here:
  of its 4 files it measures 2 at S1 (gpt2_l9_attn_qk 70,555, gpt2_l3_mlp_down 70,423) and 1 at S2 (bert_l6_up 69,927; fin edges lo a MAC, read from
  E210's committed counts-e210-S1/S2.json). Its two S1 files agree within 0.2%, so the effect is likely small, but its other files are
  NOT RUN here, and that committed row is not changed.
- **NOT RUN:** any card, any simulator other than this RTL bench (no sys_emu), any fit, a gate-level fp16 or int8 count, GEMM-state counts for fp16
  and int8, a phi for the new kinds, a counted e37 mixture row, and MM1-v3 run with these rows (no E213 point needed one).

## 6. The freeze

No run of E212's plan tiles, nor any card datum, was read for energy by the lanes that made and fixed these counts (the scope listing
read MM1-v3's committed E212 run records for their arms and sessions only). The sha256 of these files (SHA256SUMS) therefore stands
before any read of those runs' energy residuals under MM1-v3.1: an UNREAD test of the switch route in fp16 and int8 and on a second card is
still open. This version supersedes the first one, whose SHA256SUMS had sha256
76ad5d9719b173e47f0b090e819bae277b45dde60562a8042892a42d45e89c10 (recorded as a freeze line at 05:35:16 PST). No E213 data file was opened. Final: Wed 18 Nov 2026 06:25:57 PST.

## 7. Files and how to reproduce

`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json` (the tables), `counts-v31.csv` and `counts-v31-tiles.csv` (the same rows; a
tile per row for the launch-point kinds), `recount-check.*`, `crosscheck-launch-fp32.*`, `unpriced-mm1v3.json` (the scope listing),
`e213-check.json`, `tile-zero-shares.json`, `recount-S2-real_blind4-check.*` and `e37-randn-pair0-bound.json` (the fix's checks), `SOURCES.json`
(every source's sha256, the binaries, the maps, the drivers, the tiles, the desk tiles, the slot jobs; the fix's in `fix_v31counts`), `raw/`
(the bench drivers' own outputs, the fix's three among them, and the desk tiles' sha256 list), `scripts/` (the first version's scripts as run,
with the box's paths replaced by `<W>`, `<LAB>`, `<CORE_ET>`, `<VERILATOR_BIN>`; order: s02 setup, s03 build, s04 functional check, s05 maps,
s06 re-counts, s06b comparison, s07a specs, s07 fp32, s08 fp16 and int8, s09 tables, s01 scope, s10 E213 (s09 and s10 ran as one slot job, s13),
s14 zero shares, s15 the desk e37 tiles hold only +-1 and +-2, s11 sources, s12 this folder's first version; `inventory.py`'s docstring was
reworded after the run, its code unchanged; `s12_land.sh` carries a note on its own patterns) and `scripts/fix-v31counts/` (the fix as run:
s01 inputs, s02 the re-count, s03 its comparison, s04 the tables, which are s09's arithmetic unchanged with the findings answered, s05 the
change set, s10a, s10 and s11 the e37 bound, s12 the tables again with the e37 note's final text, s13 the first version's untouched files
and the E213 record re-hashed, s06 SOURCES.json, s07 this README, s08 this folder, s09 its check; paths as above). Interpreter
`/usr/bin/python3` 3.12.3 (`-I -B`), numpy 1.26.4; g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0; Verilator 5.042 2025-11-02 rev v5.042. Every bench run inside the lab's CPU slot
(nice 10) with no device node visible, one job at a time: 34.2 slot-minutes for the first version (two bench processes
a job) and 2.3 for the fix (one bench process; `SOURCES.json`).

## 8. The fix (after the verification of the first version)

The first version (SHA256SUMS sha256 76ad5d97...) was verified independently: every count reproduced bit for bit and every row re-derived,
with one row biased. The findings and what answered them:

1. **MEDIUM, fixed by a re-count.** fp32 real:blind4 at S2 measured file 0 of its two-file pool only (the S2 rule's tile 2 is file 0 when
   there are two files). Re-counted with `count_e210.py --tsel 2,3` (8 points, every check 0): its 4 file-0 points are identical, field for
   field, to the first version's; its 4 file-1 points equal the verifier's own driver on all 11 quantities it reports. The row is now
   46,811.2 fin edges lo a MAC (was 50,378.5: +7.62%; S was +9.05% high). The rule, checked on every fp32 kind: a pool of fewer than 3 files is measured at every file.
2. **LOW, fixed by a note** in both e37 rows (`note` in the JSON and the CSV) and in note [b], with the bound. The bound's point was
   counted again by `count_e210.py`, and both of its points agree with the verifier's. The rows stay pure-e37 counts: a mixture row needs
   each arm's layout share, which is MM1-v3.1's to declare.
3. **LOW, fixed:** `counts-v31-tiles.csv` carries `counts_footing` (MM1-v3's own label for the format) and the bench sources manifest sha256
   on all 21 tile rows.
4. **NIT, fixed:** the published `scripts/s12_land.sh` showed its own substitution patterns already substituted. Its copy now opens with a
   note saying which patterns ran, and the fix's own land script builds its patterns from variables, so its copy shows what ran.
5. **NIT, fixed:** every count in section 3 is an integer (int8 signal lo 79 and 99, not 78.908 and 99.433).

Nothing else changed. The other 25 fp32 rows and the 13 fp16 and int8 rows have the same numbers. `counts-fp16-int8-launch.json`, the
cross-checks, the re-count check, the scope listing, `e213-check.json`, the zero shares and the first version's raw files are byte for
byte the first version's. The E213 record is unchanged: `e213-check.json` was re-hashed at Wed 18 Nov 2026 06:22:35 PST, sha256 ce95b1620244bd775d1566a4ddb1026f47298685811bb95cbaab97eedcc0e223, the same file as
in the first version.

