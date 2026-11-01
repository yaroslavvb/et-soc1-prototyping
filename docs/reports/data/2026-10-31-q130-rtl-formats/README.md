# Q130(b): how each number format is multiplied, and what each kind of number switches

*Dated 1 Nov 2026: the fault this README reports, no multiply-add returning a·b + c, is fixed by [Q132(b)](../2026-11-01-q132-rtl-bench/README.md), with the bench [`rtl-sim/fma_toggle_v2/`](../../../../rtl-sim/fma_toggle_v2/README.md): Verilator 5.052's data-flow-graph optimiser was the cause, and `-fno-dfg` fixes it. This README's counts stay as they were.*

*Sat 31 Oct 2026 (week 44), on the Intel. Desk compute only: no card was opened and nothing was measured in watts
here. Everything below is one of three things: a reading of the public RTL (`external/core-et`, Apache-2.0), a
Verilator replay of the Q130(s) kinds tiles through that RTL, or a reduction of committed card data (E64, E36). The
bench is [`rtl-sim/fma_toggle_formats/`](../../../../rtl-sim/fma_toggle_formats/); it does not touch
`rtl-sim/fma_toggle/`. **This is revision 2, written the same day.** Revision 1 (commit `e05f2a3b`) was verified and
did not hold as stated: the bench's arithmetic is wrong, its toggle conversion does not transfer, the predictor's
absolute level is a gauge, and several claims were circular. §0 lists every change; the rest of the file is
corrected in place.*

## 0. Revision 2 (Sat 31 Oct 2026, after verification): what changed

**The RTL readings stand (§2). Every toggle count is now PROVISIONAL. The r1 predictor (`predictor.json`) is
withdrawn as E78's prediction and kept unchanged as the record. `predictor-r2.json` replaces it: gauge-free,
with intervals, and itself provisional.**

| # | Revision 1 said | What holds | Evidence |
|---|---|---|---|
| 1 | the bench "executes" the multiply-add | **It does not compute it.** No MADD micro-op returns a·b + c. In fp32, 3,740 of 4,080 results equal c alone and 340 equal a·b alone. In fp16, none of 4,080 is right, and with A = B = 1 and C0 = 5 two all-MADD ops leave C = 37 against 69. In int8 the accumulator adds another micro-op's C: the same probe leaves C = 157, 161 or 165 against 133. The MUL op is right (fp32 4,090 of 4,096). The older bench `rtl-sim/fma_toggle` fails the same way (3,755 equal c, 341 equal a·b, 0 right). | `verification/fcheck.json`; `predictor-r2.json` `functional_check` |
| 2 | 1,349.8 / 509.7 / 13.1 toggled nets a MAC, so random fp16 switches 2.6× less than fp32 and int8 103× less | **Withdrawn.** The recount's whole-unit factor 5.3271 does not transfer to this bench. Settled VCD counts of its own runs give 4.617 (fp32 randn), 4.193 (fp16 randn) and 2.076 (int8 full) names per merged net, and 2.01–7.31 across the six kinds measured. Per MAC that is 1,557 / 648 / 33.6, i.e. 2.4× and 46×, and still provisional (row 1). The int8 figure is **not comparable**: its multiply, product sum and add are behavioural RTL (`tima_top.v:89`, `:94`; `tima_adder.v:17`), so coverage counts no nets inside them, while the txfma array is structural. | `verification/hier-measured.json`; `predictor-r2.json` `toggles_provisional`, `cross_format_ratios_provisional` |
| 3 | the factor route lands 3.7% from the recount's 1,301 | **Not like for like.** 1,301 is the recount's mean over pre-loaded accumulators (n0 = 1e3 and 4e5), on other tiles. Its own C = 0 points give 1,192 and 1,198 a MAC. With row 1, what C holds moves fp32 randn's count over 1,192–1,557. | `docs/reports/data/2026-10-26-toggle-recount/recount.json` `randn.points` |
| 4 | W0 = 1.440 W "the floor"; fp16 held-out cells "to 3–6%"; int8 "fails by up to 6.1×" | **The level is a gauge.** E64's fit `P_f = B_f + c·s_f` has an exact null direction (`B_f → B_f + d·s_f`, every `c → c − d`). So `c` has no absolute level: three starts of `surface_hpl.py`'s own fit give rms 0.8242 W each, with fp32 zeros at 1.440, 7.953 and −5.072 W. Ratios of `c` values and absolute pJ per MAC mean nothing; differences and errors in watts are unchanged. Scored in watts (r1's model, single factor): fp16 +0.05 ± 0.51, +0.50 ± 0.71, −1.43 ± 0.53 W; int8 −0.68 ± 0.51, +13.76 ± 0.99, +8.36 ± 0.97 W. | `predictor-r2.json` `_gauge`, `variants.*.held_out_scoring` |
| 5 | "a new bench that EXECUTES them reproduces every Q130(s) number exactly"; the gate is "built from vpu_ctrl.v rather than assumed"; "the measurement that settles the pairing question"; int8's `provisional` flag lifted | **Circular, withdrawn.** `vpu_ctrl.v` and `vpu_tensorfma.v` are not instantiated. The gate, the (l, l+8) pair and both micro-op streams are testbench code (`tb_fmt.sv`: the gate `always_comb`, `uop_b[l + 8]`, `B[k][s]`, `one_op`), and `bus_ab` and the gated fraction are computed by it. So the 51-of-51 agreement with `kinds.json` is two codings of one reading agreeing: a consistency check, not evidence. The pairing (l, l+8) **is** right, on the RTL address path alone: `vpu_tensorfma.v:330`, `:581`, `:863`; `vpu_lane.v:404-406`, `:415-418`; `vpu_ctrl.v:1233` (§2). int8's hamming and `bus_bits_per_op` stay provisional, as `kinds.json` has them. | §2, §4 |
| 6 | fp32 here "reproduces that bench exactly" | **Only on ungated kinds** (≤ 0.3%). Gated kinds differ: smallint +8.1%, nn_like +6.1%, sparse50 −1.2%, sparse90 −12.4%; `ff_toggles` differ too (nn_like 203,952 against 131,253). The likely cause is that the write-back mask `q_valid` is read from the `always_comb` gate inside `issue` right after `uop_*` change, so it can carry the previous micro-op's gate. | `predictor-r2.json` `crosscheck_fp32_new_vs_old_bench` |
| 7 | fp16 "only 1.17× below per op", "the wires that switch per step fall only 17%"; fp32 randn anchor 25.526 W; an fp32 `wsparse50` cell of 0.7742 | 1.17 was a ratio of predicted watts, not of switching. In merged nets per op, fp32/fp16 randn is 1.324 (one factor) or 1.202 (per-format factors), provisional. The fit uses **25.638 W**, the three-run mean; 25.526 W is the two ladder runs only. There is no fp32 `wsparse50` kind: in fp32 a word is an element, so that cell was `sparse50`'s figure. | `predictor-r2.json` `cross_format_ratios_provisional`; `predict.py` `ANCHORS` |
| 8 | "a data gate, not a clock gate ... a gated lane still gets its clock", and that is why zeros "still costs 1.44 W" | **Wrong for fp32/fp16, and limited to the RTL for int8.** Only the unit clock follows the op (`vpu_lane.v:194`, `:214`; `vpu_ctrl.v:884`). In fp32/fp16 the zero gate removes the lane's valid (`vpu_ctrl.v:839`). Inside the unit, the operand register files and every pipeline stage clock through explicit `et_clk_gate` cells enabled by that valid (`txfmafrac_top.v:337-356`, `:365` on; enables at `txfma_c0.v:265-267` and `txfma_top.v:942-951`). So at RTL a gated lane's registers lose their clock. This was found while making this revision; the verification had noted only that synthesis usually adds such gates. In int8 the TIMA's operand and product registers are enable flops (`tima_top.v:63-66`, `:107`) behind an op-driven unit clock gate, and whether synthesis adds a gate there is not in the RTL. 1.44 W was the gauge's zero (row 4). | §2 |
| 9 | the fp16 "all four nonzero" rule is not in the RTL because the two product-zero flags are "formed and used independently" | **The conclusion stands, on card evidence.** E36 measured the fp16 pair result "math" at 50% and 100% on aifoundry1-c1, aifoundry2 and aifoundry3, three passes each. The RTL argument was wrong: `txfma_e2.v:83` and `:326` combine the two flags. | `docs/reports/data/2026-09-25-claims-v3/results/lat.json` `items[7]` (LAT-S1) `per_card.*.passes[*]`; `docs/findings/05-claims.md:463` |
| 10 | int8's last-pass qualifier is a fact "the spec did not have", and Q130(s)'s int8 figures should carry it | **Withdrawn.** `kinds.json` `facts.zero_gating.first_op_not_gated` already cites `vpu_ctrl.v:827`. It acts per launch, not per op: the kernel sets MUL on a launch's first op and the TenC copy-out on its last (`workloads/sparsity/kernel/sparsity.c:168`), 2 passes in 16 × iters, so the per-op figures stand in steady state. | |
| 11 | wording | `rtl-sim/fma_toggle/obj_dir/Vtb` is a local, gitignored build, not a committed binary. `tb_fmt.sv`'s comment on `f2_zap_opd3` had the polarity backwards; the code was right. Toggles are "merged nets", not wires. | `.gitignore`; `tima_top.v:111` |

**What revision 2 changes downstream.**

- **E78** freezes `predictor-r2.json`: both variants, scored as errors in watts above fp32 zeros, never as ratios.
- **The blog** quotes no toggle count and no cross-format toggle ratio until the bench passes a functional check.
  It can quote the RTL mechanics (§2), the gate fractions as computations (§4), E64's gauge-free differences (§5)
  and the bound on int8's slot price (§5).
- **The hub**'s Levels and Status: the formats' datapaths, streams and gate widths are read off the RTL (done); the
  per-kind switching counts are blocked on the bench fix.

**Open, and not done here: each needs a bench fix and a re-run, not a reduction.**

1. **Fix the bench** (the three faults now in `tb_fmt.sv`'s header), add a `+check` gate that fails a run unless
   every result equals the multiply-add of its operands, re-run all 51 kinds, and count each with a settled VCD
   pass rather than one factor per format.
2. **The older bench and the toggle recount fail the same check.** `rtl-sim/fma_toggle` (README line 28 says
   "8,192 of 8,192 match") and `docs/reports/data/2026-10-26-toggle-recount/` are not edited here. Their
   `nets_hier`, and every energy per toggle fitted to them, should carry the same provisional flag until that
   bench passes a functional check.
3. Compare int8 with fp32/fp16 only at gate level (the open flow on `tima_top` as well as `txfma_top`).
4. **A term the model lacks.** int8 zeros sits 0.68 ± 0.51 W above fp32 zeros on the card (E64), although both
   gate every slot; int8 runs 1.72× the ops a second.

## 1. The results, first

**The three number formats are not three settings of one multiplier. They are two different units, two
different operand streams and three different zero-gate widths, all read off the RTL (§2).**

| | fp32 | fp16 | int8 |
|---|---|---|---|
| unit | `txfma_top` ×8 | `txfma_top` ×8, dtype `F16_F32` | `tima_top` ×16 |
| micro-ops per op | 512 | 512 | **256** |
| cycles per op (card) | 546 | 546 | **318** |
| column slots per micro-op | 8 | 8 | **16** |
| MACs per op | 4,096 | 8,192 | 16,384 |
| multiplier | one radix-4 Booth array, 17 partial products, 64-bit Wallace tree | **the same array**, masked into two corners | 4 × signed 9×9, written as a behavioural `*` |
| accumulator | fp32 | fp32 | **int32** |
| gate decision needs | one 32-bit word | one 32-bit word (2 halves) | **two** 32-bit words ANDed (8 bytes) |
| a gated lane's registers, in the RTL | clock-gated (explicit `et_clk_gate` cells) | clock-gated (the same cells) | enable flops only |
| merged-net toggles per MAC (randn / full), **provisional** (§0 rows 1–2) | 1,557 | 648 | 33.6, behavioural arithmetic uncounted |

The last row is **not** a headline. Per multiply-add, the fp16 replay switches fewer merged nets than the fp32
one: 2.4× fewer with each format's measured factor, 2.6× with revision 1's single factor. But the replay's
accumulate path computes wrong values, so neither figure can be quoted. The int8 count covers only the named
signals around a behavioural multiply and compares with neither.

**On the card (E64, differences that do not depend on the fit's gauge, `predictor-r2.json`
`e64_gauge_free_differences_W`):**

- random fp16 draws **2.35 ± 0.52 W less** than random fp32 at the same clock, while doing twice the multiply-adds
  per op;
- all-ones costs **8.73 ± 0.50 W** more than all-zeros in fp32 and 8.31 ± 0.72 W in fp16, but only
  **0.56 ± 0.72 W** in int8.

**The predictor (r2, §5).** It is fitted on fp32 zeros, ones and randn alone.

- **fp16:** zeros and ones land within noise (+0.05 ± 0.51 and +0.50 ± 0.71 W). randn misses by −1.43 ± 0.53 W
  (z = −2.7) with revision 1's single toggle factor, and by −0.25 ± 0.53 W with the measured per-format factors.
- **int8:** it over-predicts ones and full by 8 to 14 σ, because it charges an int8 column slot an fp32 lane's
  price. E64's own int8 ones − zeros puts an int8 slot at **0.037 ± 0.048** of an fp32 lane, and at most 0.13
  (2σ).

## 2. The mechanics, with citations

All paths are under `external/core-et/rtl/shire/minion/vpu/`. These readings were re-checked line by line in the
verification and hold.

**Which datapath.** `req_int8` (`vpu_tensorfma.v:305`) splits the unit at the clock gate:
`clock_en_txfma = (enabled_int & ~req_int8) | …` and `clock_en_tima = (enabled_int & req_int8) | …`
(`vpu_tensorfma.v:157-166`). fp32 and fp16 both run on `txfma_top` with the TIMA clock off; int8 runs on
`tima_top` with the txfma clock off. There is no third unit and no shared one.

**fp16 shares fp32's multiplier: it is masked, not shrunk.** `mul_hp_mode` is set by
`op_dtype == VPU_DTYPE_F16_F32` (`txfma_7s/txfma_c0.v:483`), reaches the PPG's mode port (`txfma_f1.v:112`), and
that single bit reaches the one radix-4 Booth partial-product generator as `ph` (`txfma_booth_ppg_32r4.v:54-56`).
In fp16 the array is not narrowed: its 17 partial products are **masked into opposite ends of the same 64-bit
Wallace tree**. `pp1 = pp1_raw & {{20{~ph}}, 13'h1fff}` for pp1–pp7 and `pp11 = pp11_raw & {15'h7fff, {18{~ph}}}`
for pp11–pp17 (`:203-219`), with pp8–pp10 untouched. The tree (`txfma_wallace1.v:81-88`, the 64-bit
`txfma_4_2_compressor_array`) and the final adder are the fp32 ones. One 24×24 significand product or two 11×11
products: same silicon, same clock, two corners.

**int8's multiplier is a separate, small one, written behaviourally.** `tima_top.v` holds `TIMA_INT8_MUL_NUM` = 4
(`rtl/inc/tima_defines.vh:8`) signed 9×9 products, `f2_prod[i] = $signed(f2_in1_part[i]) * $signed(f2_in2_part[i])`
(`tima_top.v:89`). They are summed to 19 bits (`f2_prod_add`, `:94`), sign-extended to 32 bits and added to a
32-bit accumulator by `tima_adder`, a plain `a + b` (`tima_adder.v:17`). There is no exponent, so there is no
alignment, rounding or normalisation. **How the multiply and the adds are built in gates (Booth, Wallace or
otherwise) is synthesis's choice: the RTL does not say,** and a toggle count of this RTL sees no nets inside them.

**Operand packing.** In every format one 32-bit lane word is one lane operand, carrying E elements of consecutive
k with E·size = 4 bytes: fp32 E=1, fp16 E=2, int8 E=4. The A word is **broadcast**:
`f3_tena_regfile_wdata_l = dcache_scp_data[32 * broadcast_sel +: 32]` (`vpu_ctrl.v:1221`). The B word is per lane,
out of a 256-bit TENB row (`vpu_ctrl.v:1233`).

**The micro-op order, and why 546 vs 318.** For fp32/fp16 `fma_exec_b_col` walks 0,1, so each A row is issued
twice (`vpu_tensorfma.v:718`), giving 16·16·2 = 512 micro-ops of 8 lanes. For int8 `fma_exec_last_b_col` is forced
true by `req_int8` (`:412`), and `fma_exec_b_col_next = req_int8 ? fma_exec_b_col : …` never advances (`:717-718`,
comment *"for INT8, we do all B cols at once"*). That gives 16·16 = **256** micro-ops of 16 column slots. 512
micro-ops at one a cycle cannot retire in 318 cycles; 256 can. The bench copies this stream; it does not derive it.

**The zero gate, and its granularity.** One `always_comb` forms it (`vpu_ctrl.v:801-819`):

```
ex_tensor_zero_mask = ex_tensora_zero_mask_mux | (ex_tensorb_zero_mask_tima0 & ex_tensorb_zero_mask_tima1)
```

The mask has eight bits, one per lane. The zero *test* is 32 bits wide in every format (`f3_zero_data_a/_b`,
`vpu_ctrl.v:1229-1234`), so the word-zero rate is p^E in all three. What differs is how many tests one gate
*decision* consumes:

- **fp32/fp16**: `ex_tima_valid_unqual` is 0, so both B terms index `ex_ra2_ten`, the same row, and the AND is a
  no-op. One 32-bit word decides: one element in fp32, two halves in fp16.
- **int8**: `tima0` reads `ex_tima_tenb_raddr` and `tima1` reads `ex_tima_tenb_raddr | 1` (`:808-811`).
  `s1_tima_tenb_raddr = {fma_exec_b_rd_ptr, 1'b0}` (`vpu_tensorfma.v:863`) makes those the two 32-byte halves of
  one 64-byte B line. **Eight bytes must all be zero before one lane gates.**

**The int8 gate pair is columns (l, l+8), not (2l, 2l+1): the RTL address path settles it.**

- **Where a half sits.** `dc_read_addr_flat = {scp_b, dc_read_b_col, 5'b0} + {dc_read_b_row, 6'b0}`
  (`vpu_tensorfma.v:330`) puts half `c` of B line `r` at byte `r*64 + c*32`.
- **Where it is written.** The B write address is `{2'b01, dc_read_b_wr_ptr, dc_read_b_col}` (`:581`), so the half
  index is the TenB entry's low bit.
- **Which TIMA gets it.** TIMA 0 of a lane writes the entries with `waddr[0] == 0` and TIMA 1 those with
  `waddr[0] == 1` (`vpu_lane.v:415-418`); the odd entry is read for TIMA 1 (`vpu_lane.v:404-406`).
- **Which word.** Lane `l` reads bits `[32l +: 32]` of the 256-bit row (`vpu_ctrl.v:1233`), i.e. bytes
  `c*32 + 4l`, i.e. **word `8c + l`**. So TIMA 0 of lane l holds column `l` and TIMA 1 holds column `l + 8`.

The bench implements that reading, so its agreement with `kinds.json`'s primary `gated_lane_frac` is by
construction (§4). For reference: computed on the same tile, (l, l+8) gates 0.0703 of int8 `sparse50`'s
slot-cycles and A4's (2l, 2l+1) grouping 0.0776 (`kinds.json` `kinds.int8.sparse50.stats.gated_lane_frac` and
`gated_lane_frac_alt_grouping`). Neither figure is a measurement.

**Two qualifications of the gate.**

1. In int8 the gate is also qualified by `(ex_tima_ren3 && ~ex_tima_last_pass)` (`vpu_ctrl.v:827`), and the txfma
   gate by `cmd == VPU_FCMD_MADD` (`:837`). `kinds.json` already records this
   (`facts.zero_gating.first_op_not_gated`). It acts per launch, not per op. `s0_tima_last_pass` needs the TenC
   copy-out (`vpu_tensorfma.v:847`), and `first_pass` is the instruction's MUL bit (`:180`, cleared at `:726`). The
   kernel sets MUL only on a launch's first op and the copy-out only on its last
   (`workloads/sparsity/kernel/sparsity.c:168`). So the qualifier touches 2 passes in 16 × iters, and the per-op
   figures stand in steady state.
2. **What the gate does to the clock differs by unit (revision 1 had this wrong for fp32/fp16).** In both units the
   unit clock follows the op, not the data. `cgate_txfma` and `cgate_tima` are driven by `clock_en_txfma` and
   `clock_en_tima` (`vpu_lane.v:194`, `:214`; `vpu_lane_tima.v:77-82`; `vpu_ctrl.v:884`). Below that they differ:
   - **fp32/fp16 (txfma).** The zero gate removes a lane's valid: `ex_txfma_valid = {…ex_txfma_valid_all} &
     ~ex_fma_gate_mask & ex_ml_gate_mask` (`vpu_ctrl.v:839`). Inside the unit, the operand register files clock
     on `opa_frf_clk`, `opb_frf_clk` and `opc_frf_clk`, from explicit `et_clk_gate` cells
     (`txfmafrac_top.v:337-356`) enabled by `opa/opb/opc_valid_rfa_h = in_valid & ren1/2/3`
     (`txfma_c0.v:265-267`, wired at `txfma_top.v:942-944`). Each pipeline stage has its own gated clock enabled by
     that stage's valid (`txfmafrac_top.v:365` on, `txfma_clken_fNa_h = txfma0_ctrl_valid_fNa_h` at
     `txfma_top.v:947-951`). **So at RTL a gated lane's registers are not clocked;** only the unit clock runs.
   - **int8 (TIMA).** `ex_tima_valid[l][t]` becomes `f1_tima_mul_en` (`vpu_lane.v:427`), the enable of
     `tima_top`'s F1 operand registers (`tima_top.v:63-66`), and `f2_tima_en` the enable of its product register
     (`:107`). These are enable flops with no clock gate of their own in the RTL. Synthesis usually turns such an
     enable into a clock gate, and this lab's `ff_acct.sv` (lines 3-4) assumes so, but the RTL does not say.

**The fp16 two-term rule, as the PRM writes it, is not what the chip computes, and the evidence is the card's.**
The PRM 9.4 pseudo-code drops the whole two-term update unless all four of a1, a2, b1, b2 are nonzero
(`expectC(…, literal=true)` in the host). E36 ran that test on three cards. At 50% and 100% sparsity the result
was the plain mathematical one ("math") on aifoundry1-c1, aifoundry2 and aifoundry3, three passes each
(`docs/reports/data/2026-09-25-claims-v3/results/lat.json` `items[7]`, LAT-S1, `per_card.*.passes[*]`;
`docs/findings/05-claims.md:463`). Revision 1 argued it instead from the two product-zero flags `eprod_hi_zero`
and `eprod_lo_zero` (`txfma_7s/txfma_c1.v:58`, `:65`), calling them "formed and used independently". That is
wrong: `txfma_e2.v:83` and `:326` combine them. This bench cannot test the rule until its MADD works (§0 row 1).
`pair_half_zero` gates no lane in fp16 (the zero test is the whole word) and flips 72,796 operand bits an op.

## 3. What the bench is, and what is wrong with it

`rtl-sim/fma_toggle_formats/` holds `tb_fmt.sv`, `Makefile` and `run_kinds.py`, plus `ff_acct.sv` and `acct.cpp`
copied from `rtl-sim/fma_toggle/`. `+fmt=fp32|fp16|int8` picks the unit, the stream and the gate, each coded
against the lines cited in §2. `run_kinds.py` replays a Q130(s) tile file (2,048 bytes, A then B) and, for fp32
only, also runs a local build of `rtl-sim/fma_toggle` (its `obj_dir/Vtb`; `obj_dir/` is gitignored) on the same
tiles.

Build (the Intel; `nice -n 10`, 4 threads, ~56 s):

```
make CORE_ET=../../external/core-et \
  VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator CXXOVERRIDE=/usr/bin/clang++
```

`AROVERRIDE` defaults to `/usr/bin/ar`, because conda-forge's verilator names an archiver it does not ship.

**Known faults (verification, Sat 31 Oct 2026; also in `tb_fmt.sv`'s header). The counts are provisional until
they are fixed.**

1. **MADD does not compute a·b + c** in either bench (§0 row 1; reproduce with `verification/fcheck.py`, seconds a
   run). MUL ops compute a·b correctly, so the operand path into the array works, but the accumulate path
   switches on wrong values. That path carries about 45% of fp32 randn's count: the files outside the array are 45.4% of it
   (`predictor-r2.json` `toggles_provisional.fp32.randn.array_dominated_share` = 0.546). For int8 it is the
   27.6% in `tima_adder`. The cause is not yet found.
2. **int8's C is taken at the wrong stage.** `f3_in3` is fed from the EX-stage `uop_c`, and the result is taken at
   `TIMA_LAT` = 3. But the RTL reads TenC at F2 (`vpu_lane_tima.v:60-71`, `rd_en(f2_tima_in3_en)`) and `f3_out` is
   combinational at F3 (`tima_top.v`), so the accumulator adds another micro-op's C.
3. **The write-back mask can be one micro-op stale** (§0 row 6), which is the likely cause of the gated-kind
   disagreement with the older bench.

**Two instrument caveats, unchanged from revision 1.**

- **The unused unit leaks.** Both units are elaborated, and the unused one is switched off by tying its clock and
  valid low. A disabled `txfma_top`'s combinational input nets still follow the operand bus, so an int8 run
  carries ~194k txfma names an op that no clock samples. `predict.py:unit_nets()` counts only `tima*` blocks for
  int8 and only non-`tima` blocks otherwise.
- **No register counts in int8.** `tima_top`'s registers use the `EN_FF` macro (`rtl/inc/macros.vh:40`), a plain
  `always` block, not the `ff`/`en_ff` modules that `ff_acct.sv` shadows, so the `ff_toggles` column reads 0 for
  int8. That is a missing instrument, not a claim that nothing clocks there.

## 4. What the replay's agreement with Q130(s) does and does not show

`counts.json` holds all 51 kinds, and a `+nogate=1` run of each. The bench's operand bits and gated fractions
equal `kinds.json`'s. **This holds by construction: both are computed from the same tiles by the same reading
of the stream and the gate (§0 row 5). It is a consistency check of two codings, not a measurement.**

| | fp32 randn | fp16 randn | int8 full |
|---|---:|---:|---:|
| `bus_ab` per op, this bench | 82,214 | 84,416 | 69,312 |
| `kinds.json` `bus_bits_per_op` | 82,214 | 84,416 | 69,312 |

| gated column-slot-cycles (computed from the RTL's gate rule) | fp32 | fp16 | int8 |
|---|---:|---:|---:|
| `sparse50` (50% element), this bench = `kinds.json` | 0.7742 | 0.4143 | **0.0703** |
| `wsparse50` (50% word), this bench = `kinds.json` | none: in fp32 a word is an element, so it is `sparse50` | 0.7600 | **0.6436** |

int8's hamming and `bus_bits_per_op` stay **provisional**, as `kinds.json` marks them: the bench copies the
reconstructed 256-micro-op TIMA stream and the 16-slot A-broadcast convention, so it cannot confirm either. int8's
gated fractions were already not provisional there: they depend only on the gate rule. `fp32 smallint` is not a
dense control: 3,614 of 4,096 slot-cycles are live and 11.8% gated.

**The fp32 cross-check against `rtl-sim/fma_toggle`** (`predictor-r2.json` `crosscheck_fp32_new_vs_old_bench`;
txfma-only nets, new over old):

| kind | gated | new / old |
|---|---:|---:|
| randn, randn_large, randn_sorted, pow2, bf16trunc | 0 | 1.00014, 1.00016, 1.00021, 1.0016, 0.9973 |
| ones, neg_ones, pi, fp16grid, randn_small, uniform01 | 0 | 1.0000 |
| zeros, a_randn_b_zeros, a_zeros_b_randn | 1.0 | 1.0000 |
| smallint | 0.118 | **1.0807** |
| nn_like | 0.508 | **1.0608** |
| sparse50 | 0.774 | **0.9884** |
| sparse90 | 0.992 | **0.8757** |

Every partly gated fp32 cell (sparse50 319, smallint, nn_like) and every fp16/int8 sparse and wsparse count
carries this disagreement on top of §0 row 1.

## 5. The predictor, and where it breaks

**Revision 1 (`predictor.json`, sha256 `f886b131…`, commit `e05f2a3b`) is withdrawn as E78's prediction.** It is
kept unchanged; `predict.py counts.json` still reproduces it byte for byte. **Revision 2** is `predictor-r2.json`,
from `predict_r2.py counts.json verification/hier-measured.json verification/fcheck.json`.

**Model.** Its form is unchanged; only differences are stated:

```
dW(kind) = W(kind) − W(fp32 zeros) = g · Δlive_slot_cycles_per_s + k · Δnets_hier_per_s     (600 MHz, 1024 minions)
```

**Calibration.** g and k are fitted exactly on E64's three fp32 anchors, each the mean of three runs (`fit.c`:
zeros 1.406 / 1.473 / 1.442, ones 11.164 / 9.648 / 9.704, randn 25.459 / 25.593 / 25.862 W). The anchors'
standard errors are carried to every number below; a held-out cell (one run) adds the pooled single-run sd,
0.511 W (6 dof).

- **The gauge.** E64's per-run `c` has no absolute level (§0 row 4), so r1's W0 = 1.440 W is not a floor but the
  gauge's zero, and it cancels from every difference and every error.
- **A one-term model is impossible.** fp32 `ones` costs 8.73 ± 0.50 W over `zeros` while its A and B never change
  and its multiplier array has no new inputs. A launch lasts about 0.5 s (E64 README, the `s*/launches.jsonl`
  row) at 600–800 MHz, i.e. 1.1–1.5 million ops a second. So an all-ones fp32 accumulator counts up by 16 an op
  to 9–12 million, short of 2^24 (16.8 million, where adding 1 stops changing it). The accumulate path therefore
  still switches, and the replay, with its broken MADD, cannot say how much of the 8.73 W that costs.
- **g and k.** g = (1.894 ± 0.108) × 10⁻¹² W per live slot-cycle per second. k = 2.486 ± 0.082 fJ per merged-net
  toggle under variant A, 2.155 ± 0.071 fJ under variant B. **k is a fitting constant, not an energy per net**: it
  is fitted to a count from a datapath that computes the wrong sum.

**Two variants, both registered for E78.**

- **A** keeps revision 1's single toggle factor (5.3271).
- **B** divides each format by its own measured factor (`verification/hier-measured.json`).

fp32's predictions are the same in both, because a common factor is absorbed by k. Neither variant is blind for the
six held-out cells below (r1's scores were known when r2 was written); both are blind for every E78 cell.

| held out (E64 SUS-03…08) | measured dW over fp32 zeros | A: error | z | B: error | z |
|---|---:|---:|---:|---:|---:|
| fp16 zeros | −0.05 | +0.05 ± 0.51 W | +0.1 | +0.05 ± 0.51 W | +0.1 |
| fp16 ones | 8.26 | +0.50 ± 0.71 W | +0.7 | +0.50 ± 0.71 W | +0.7 |
| fp16 randn | 21.84 | −1.43 ± 0.53 W | **−2.7** (−1.6 with the noisiest anchor's sd) | −0.25 ± 0.53 W | −0.5 |
| int8 zeros | 0.68 | −0.68 ± 0.51 W | −1.3 | −0.68 ± 0.51 W | −1.3 |
| int8 ones | 1.24 | **+13.76 ± 0.99 W** | +13.9 | +13.78 ± 0.99 W | +13.9 |
| int8 full | 7.66 | **+8.36 ± 0.97 W** | +8.7 | +9.62 ± 0.93 W | +10.3 |

**fp16 is consistent with the fp32 calibration within noise for zeros and ones. randn is borderline under A and
consistent under B. int8 fails, and the failure is reported as a failure.**

**Why int8 fails: the price of a lane being on.** The model charges an int8 column slot what it charges an fp32
lane. Each format's own zeros/ones pair says otherwise (`predictor-r2.json` `per_format_g_from_held_out`, which
uses held-out cells and is **not** part of the frozen prediction):

| format | ones − zeros (W) | g relative to fp32's |
|---|---:|---:|
| fp32 | 8.73 ± 0.50 | 1 |
| fp16 | 8.31 ± 0.72 | 0.95 ± 0.10 |
| int8 | 0.56 ± 0.72 | 0.037 ± 0.048, at most 0.13 (2σ) |

So an int8 slot costs at most about an eighth of an fp32 lane-cycle, and the point estimate is 27× cheaper. That
fits four small integer multipliers and an add against an fp32 FMA's alignment, normalisation and rounding. **E78
refits g per format on its own aifoundry3 anchors, and scores every cell as an error in watts above fp32 zeros.**

**Statistical intervals only.** The intervals above carry the anchors' run-to-run spread. They do not carry the
bench's fault (§0 row 1) or the toggle-factor choice; the A−B spread (up to 1.26 W on int8 full and 1.18 W on fp16
randn) is one measure of the latter.

**Departures, dated Sat 31 Oct 2026 and named before any E78 data exist.**

- (a) **E64 is aifoundry2, not aifoundry3.** It holds the only committed fp32 zeros/ones/randn triple. Its `c` is
  the per-run term over the fit's per-clock offsets `B_f` (E64 README line 102, "busy offsets"), not a figure over
  idle, and has no absolute level.
- (b) **Toggles.** `nets_hier` comes either from one factor (A) or from one factor per format measured on that
  format's random kind (B), not from a settled VCD of every kind. The kind-to-kind spread measured so far is
  2.01–2.08 for int8 random-like kinds and 3.49 for int8 ones, against 4.62 (randn) and 7.31 (ones) for fp32
  (`cross_format_ratios_provisional.kind_factor_spread`).

## 6. Files

| File | What |
|---|---|
| `counts.json` | all 51 kinds × (gated, ungated): raw toggle coverage by RTL block, `bus_ab`, `bus_c`, live slot-cycles, cycles, FF counters. Unchanged; provisional (§0 row 1) |
| `predict.py`, `predictor.json` | revision 1: the model, the fit and the held-out scoring. **Withdrawn**, kept as the record; sha256 `f886b131f07406cfe25b784bff972603b16d70abb01ed3ef827829f7cb46aa83` |
| `predict_r2.py`, `predictor-r2.json` | **revision 2**: gauge-free predictions with intervals, variants A and B, the held-out errors in watts, per-format g, E64's gauge-free differences, every kind's toggles under both factors, the fp32 old/new cross-check and the functional-check summary. Provisional |
| `verification/fcheck.py`, `fcheck.json` | the functional check (§0 row 1), 8 runs: both benches, three formats, the run_kinds protocol and the A = B = 1, C0 = 5 accumulator probe |
| `verification/hier-measured.json` | the six settled-VCD factors measured on this bench's runs (§0 row 2), with raw coverage by block |
| `verification/hier_probe.py`, `dump-window.patch` | how they were measured: the VCD window and trace build for this bench, then the toggle recount's own `scope_modules.py` and `settle_count.cpp`, unchanged |
| `../../../../rtl-sim/fma_toggle_formats/` | the bench; revision 2 changed comments only (the known-fault header, one polarity comment, `run_kinds.py`'s docstring) |

Re-run: `/usr/bin/python3 -I rtl-sim/fma_toggle_formats/run_kinds.py --kinds tools/claims-v3/kinds --out counts.json
--jobs 5 --nogate`, then `predict_r2.py counts.json verification/hier-measured.json verification/fcheck.json --out
predictor-r2.json`. After the bench is fixed, re-run `verification/fcheck.py` first: no count should be quoted
from a run that fails it.
