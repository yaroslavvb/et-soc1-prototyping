# Q130(b): how each number format is multiplied, and what each kind of number switches

*Sat 31 Oct 2026 (week 44), on the Intel. Desk compute only: no card was opened, nothing was measured in
watts here. Everything below is either a reading of the public RTL (`external/core-et`, Apache-2.0) or a
Verilator replay of the Q130(s) kinds tiles through that RTL. The bench is
[`rtl-sim/fma_toggle_formats/`](../../../../rtl-sim/fma_toggle_formats/); it does not touch
`rtl-sim/fma_toggle/`, whose fp32 figures it instead reproduces as a cross-check.*

## 1. The results, first

**The three number formats are not three settings of one multiplier. They are two different units, two
different operand streams, and three different zero gates — and that, not the arithmetic, is what sets
what a kind of number costs.**

| | fp32 | fp16 | int8 |
|---|---|---|---|
| unit | `txfma_top` ×8 | `txfma_top` ×8, dtype `F16_F32` | `tima_top` ×16 |
| micro-ops per op | 512 | 512 | **256** |
| cycles per op (card) | 546 | 546 | **318** |
| column slots per micro-op | 8 | 8 | **16** |
| MACs per op | 4,096 | 8,192 | 16,384 |
| multiplier | one radix-4 Booth array, 17 partial products | **the same array**, masked into two corners | 4 × signed 9×9 |
| accumulator | fp32 | fp32 | **int32** |
| gate decision needs | one 32-bit word | one 32-bit word (2 halves) | **two** 32-bit words ANDed (8 bytes) |
| **toggled nets per MAC** (randn / full) | **1,349.8** | **509.7** | **13.1** |

The last row is the headline: **per multiply-add, random fp16 switches 2.6× less than random fp32 and
random int8 switches 103× less.** Per *op* the gap is smaller (fp16 does twice the MACs in the same 512
micro-ops), which is exactly why fp16 saves far less power than its MAC count suggests.

Fitted on fp32 `zeros`, `ones` and `randn` alone, the predictor reaches **2.486 fJ per toggled net** and
predicts fp16's three held-out cells to 3–6%. **It fails on int8 by up to 6.1×**, and the reason is
measured, not guessed: see §5.

## 2. The mechanics, with citations

All paths are under `external/core-et/rtl/shire/minion/vpu/`.

**Which datapath.** `req_int8` (`vpu_tensorfma.v:305`) splits the unit at the clock gate:
`clock_en_txfma = (enabled_int & ~req_int8) | …` and `clock_en_tima = (enabled_int & req_int8) | …`
(`vpu_tensorfma.v:157-166`). fp32 and fp16 both run on `txfma_top` with the TIMA clock off; int8 runs on
`tima_top` with the txfma clock off. There is no third unit and no shared one.

**fp16 shares fp32's multiplier, and it is masked, not shrunk.** `mul_hp_mode` is set by
`op_dtype == VPU_DTYPE_F16_F32` (`txfma_7s/txfma_c0.v:483`), and that single bit reaches the one radix-4
Booth partial-product generator as `ph` (`txfma_booth_ppg_32r4.v:54-56`). In fp16 the array is not
narrowed; its 17 partial products are **masked into opposite ends of the same 64-bit Wallace tree**:
`pp1 = pp1_raw & {{20{~ph}}, 13'h1fff}` for pp1–pp7 and `pp11 = pp11_raw & {15'h7fff, {18{~ph}}}` for
pp11–pp17 (`:203-219`), with pp8–pp10 untouched. The tree (`txfma_wallace1.v`, 64-bit
`txfma_4_2_compressor_array`) and the final adder are the fp32 ones. One 24×24 significand product or two
11×11 products — same silicon, same clock, two corners.

**int8's multiplier is a separate, tiny one.** `tima_top.v` holds `TIMA_INT8_MUL_NUM` = 4
(`rtl/inc/tima_defines.vh:8`) signed 9×9 products (`f2_prod[i] = $signed(f2_in1_part[i]) * $signed(f2_in2_part[i])`),
summed to 19 bits (`f2_prod_add`), sign-extended to 32 and added to a 32-bit accumulator by `tima_adder`
(a plain `a + b`). No Booth recoding, no Wallace tree, no alignment, no rounding, no normalisation.

**Operand packing.** One 32-bit lane word is one lane operand in every format, carrying E elements of
consecutive k with E·size = 4 bytes: fp32 E=1, fp16 E=2, int8 E=4. The A word is **broadcast**:
`f3_tena_regfile_wdata_l = dcache_scp_data[32 * broadcast_sel +: 32]` (`vpu_ctrl.v:1221`). The B word is
per lane out of a 256-bit TENB row (`vpu_ctrl.v:1233`).

**The micro-op order, and why 546 vs 318.** For fp32/fp16 `fma_exec_b_col` walks 0,1 so each A row is
issued twice (`vpu_tensorfma.v:718`), giving 16·16·2 = 512 micro-ops of 8 lanes. For int8
`fma_exec_last_b_col` is forced true by `req_int8` (`:412`) and `fma_exec_b_col_next = req_int8 ?
fma_exec_b_col : …` never advances (`:717-718`, comment *"for INT8, we do all B cols at once"*), giving
16·16 = **256** micro-ops of 16 column slots. 512 micro-ops at one a cycle cannot retire in 318 cycles;
256 can. This reproduces Q130(s)'s reconstruction independently, from a bench that executes the RTL.

**The zero gate, and its granularity.** One `always_comb` forms it (`vpu_ctrl.v:802-818`):

```
ex_tensor_zero_mask = ex_tensora_zero_mask_mux | (ex_tensorb_zero_mask_tima0 & ex_tensorb_zero_mask_tima1)
```

Eight bits, one per lane. The zero *test* is 32 bits wide in every format
(`f3_zero_data_a/_b`, `vpu_ctrl.v:1229-1234`), so the word-zero rate is p^E in all three. What differs is
how many tests one gate *decision* consumes:

- **fp32/fp16**: `ex_tima_valid_unqual` is 0, so both B terms index `ex_ra2_ten` — the same row — and the
  AND is a no-op. One 32-bit word: one element in fp32, two halves in fp16.
- **int8**: `tima0` reads `ex_tima_tenb_raddr` and `tima1` reads `ex_tima_tenb_raddr | 1` (`:808-811`),
  and `s1_tima_tenb_raddr = {fma_exec_b_rd_ptr, 1'b0}` (`vpu_tensorfma.v:863`) makes those the two 32-byte
  halves of one 64-byte B line. **Eight bytes must all be zero before one lane gates.**

**The open question of Q130(s) is settled: the int8 gate pair is columns (l, l+8), not (2l, 2l+1).**
The B address arithmetic forces it. `dc_read_addr_flat = {scp_b, dc_read_b_col, 5'b0} + {dc_read_b_row, 6'b0}`
(`vpu_tensorfma.v:330`) puts half `c` of B line `r` at byte `r*64 + c*32`, and lane `l` reads bits
`[32l +: 32]` of that 256-bit row, i.e. bytes `c*32 + 4l`, i.e. **word `8c + l`**. So TIMA 0 of lane l
holds column `l` and TIMA 1 holds column `l + 8`. The bench implements that reading and reproduces
`kinds.json`'s primary `gated_lane_frac` for every int8 kind exactly (§4), while A4's alternative
grouping would give different numbers (0.0776 against 0.0703 on `sparse50`).

**Two departures from the Q130(s) spec's gate description, both found here.**
1. In int8 the gate is qualified by `(ex_tima_ren3 && ~ex_tima_last_pass)` (`vpu_ctrl.v:827`), so
   **int8's last A-column pass — the one that writes the VPU register file — is never zero-gated at all**,
   on top of the first pass. The txfma gate is qualified only by `cmd == VPU_FCMD_MADD`
   (`:837`), i.e. the first (MUL) pass alone. For a launch with several A columns this lowers int8's
   realised gating further than any per-op count says.
2. The gate is a **data gate, not a clock gate**. `ex_tima_valid[l][t]` becomes `f1_tima_mul_en`
   (`vpu_lane.v:427`), which is the *enable* of tima_top's F1 operand registers
   (`EN_FF(clock, f1_mul_en, f2_in1…)`), and `f2_tima_en` the enable of the product register. The TIMA's
   own clock gate `cgate_tima` (`vpu_lane_tima.v`) is driven by `clock_en_tima = ex_tima_valid_unqual | …`
   (`vpu_lane.v:214`) — by the *op*, not by the data. Same for txfma (`:194`). **A gated lane still gets
   its clock**; what it loses is new operands.

**The fp16 two-term rule is NOT in the RTL as the PRM states it.** `eprod_hi_zero = ea_hi_zero | eb_hi_zero`
and `eprod_lo_zero = ea_lo_zero | eb_lo_zero` are formed **independently** (`txfma_7s/txfma_c1.v:58`
and `:65`) and are used independently thereafter, each steering its own alignment and sticky path
(`txfma_e2.v:80-83`, `:322-326`). There is no term anywhere that ANDs all four operand-zero flags to
suppress the pair. So the RTL drops **only the zero term**, not the update: the PRM 9.4 pseudo-code's
"all four nonzero" is the host's software expectation (`expectC(…, literal=true)`), not a hardware rule.
It is a *reporting* convention, and the switching consequence is unchanged either way, because
`pair_half_zero` gates no lane and still flips 72,796 operand bits (§4).

## 3. What the bench is

`rtl-sim/fma_toggle_formats/` — `tb_fmt.sv`, `Makefile`, `run_kinds.py`, plus `ff_acct.sv` and `acct.cpp`
copied from `rtl-sim/fma_toggle/`. `+fmt=fp32|fp16|int8` picks the unit, the stream and the gate; each is
coded against the lines cited in §2. `run_kinds.py` replays a Q130(s) tile file (2,048 bytes, A then B)
and, **for fp32, also runs the committed `rtl-sim/fma_toggle/obj_dir/Vtb` on the same tiles**.

Build (the Intel; `nice -n 10`, 4 threads, ~56 s):

```
make CORE_ET=../../external/core-et \
  VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator CXXOVERRIDE=/usr/bin/clang++
```

`AROVERRIDE` defaults to `/usr/bin/ar`: conda-forge's verilator names an archiver it does not ship.

**Known bench caveat, corrected in the analysis, not hidden.** Both units are elaborated and the unused
one is switched off by tying its clock and valid low. A disabled `txfma_top`'s *combinational* input nets
still follow the operand bus, so an int8 run carries ~194k txfma names an op that no clock ever samples.
`predict.py:unit_nets()` counts only `tima*` blocks for int8 and only non-`tima` blocks otherwise.
Separately, `tima_top`'s registers use the `EN_FF` **macro** (`rtl/inc/macros.vh:40`), a plain `always`
block, not the `ff`/`en_ff` modules `ff_acct.sv` shadows — so the `ff_toggles` column reads 0 for int8.
That is a missing instrument, not a claim that nothing clocks there.

## 4. The replay reproduces Q130(s) exactly, which is the cross-check that matters

`counts.json` holds all 51 kinds (and a `+nogate=1` run of each). Two independent routes agree:

| | fp32 randn | fp16 randn | int8 full |
|---|---:|---:|---:|
| `bus_ab` per op, this bench | 82,214 | 84,416 | 69,312 |
| `kinds.json` `bus_bits_per_op` | 82,214 | 84,416 | 69,312 |

and every gate fraction, including the ones Q130(s) revision 2 corrected:

| gated column-slot-cycles | fp32 | fp16 | int8 |
|---|---:|---:|---:|
| `sparse50` (50% element) — bench | 0.7742 | 0.4143 | **0.0703** |
| `sparse50` — `kinds.json` tile | 0.7742 | 0.4143 | **0.0703** |
| `wsparse50` (50% word) — bench | 0.7742 | 0.7600 | **0.6436** |

So int8's `provisional` flag on `bus_bits_per_op` can be lifted for the stream and the gate: an RTL bench
that executes the TIMA, with the gate built from `vpu_ctrl.v` rather than assumed, lands on the same
numbers. Revision 1's int8 figures (the txfma stream) are confirmed wrong.

`fp32 smallint` is also confirmed not a dense control: 3,614 of 4,096 slot-cycles live, 11.8% gated.

## 5. The predictor, and where it breaks

`predictor.json` (sha256 in §6), from `predict.py counts.json`. Model:

```
W_switching(600 MHz, 1024 minions) = W0 + g · live_slot_cycles_per_s + k · nets_hier_per_s
```

Three parameters, fitted **exactly** on three measured fp32 anchors — E64's `fit.c`, which is the 600 MHz
switching term of `P = B(f) + c·s(f)` with `s(600) = 1.0`
([`figures.json`](../2026-10-23-e64-horace-power-limit/figures.json) `fit.c`): `zeros` 1.440 W, `ones`
10.172 W, `randn` 25.526 W. A one-term model cannot work, because `ones` switches almost nothing
(0.21 nets a MAC) and still costs 8.7 W over `zeros`: what it buys is that **its lanes are not gated**.

Fit: **W0 = 1.440 W, g = 1.894e-12 W per live slot-cycle per second, k = 2.486 fJ per toggled net.**

Scored on the six cells E64 measured that the fit never saw:

| held out | measured W | predicted W | ratio |
|---|---:|---:|---:|
| fp16 zeros | 1.394 | 1.440 | 1.033 |
| fp16 ones | 9.702 | 10.20 | 1.051 |
| fp16 randn | 23.284 | 21.85 | 0.939 |
| int8 zeros | 2.123 | 1.440 | 0.678 |
| int8 ones | 2.684 | 16.44 | **6.126** |
| int8 full | 9.101 | 17.46 | **1.918** |

**fp16 transfers; int8 does not, and the predictor says why.** The `g` term charges an int8 column slot
what it charges an fp32 lane. Each format's own zeros/ones pair implies
(`predictor.json.per_format_g_from_held_out`, which uses held-out data and is therefore **not** part of
the frozen prediction): fp32 1.894e-12, fp16 1.803e-12 (0.95×), **int8 7.09e-14 — 0.037× of fp32, i.e.
26.7× cheaper per enabled slot.** That is the right order for four 9×9 multipliers and a 32-bit add
against a 24×24 Booth/Wallace fp32 FMA with alignment, normalisation and rounding.

**So the registered prediction for E78 is: the fp32 cells and the fp16 cells to within ~6%, and the int8
cells over-predicted — a failure, reported as a failure.** E78 refits W0, g and k on its own aifoundry3
anchors, per format, and the per-kind ratios inside a format do not move.

**Departures, dated today and named before any card ran.** (a) E64 is **aifoundry2**, not aifoundry3; it
is the only committed fp32 zeros/ones/randn triple with a switching-over-idle figure, so absolute watts
here are aifoundry2's. (b) `nets_hier` is reached from the coverage total by the whole-unit factor 5.3271
(`hier-factors.json` `_total`), measured on fp32 randn, **not** by a VCD of these runs; on fp32 randn that
route gives 1,349.8 nets a MAC against the toggle-recount's 1,301 on card tiles, 3.7% apart. Reusing it
for fp16 and the TIMA is this work's largest modelling assumption.

## 6. Files

| File | What |
|---|---|
| `counts.json` | all 51 kinds × (gated, ungated): nets by RTL block, `bus_ab`, `bus_c`, live slot-cycles, cycles, FF counters |
| `predict.py` | the model, the fit and the held-out scoring |
| `predictor.json` | **the frozen prediction**, sha256 `f886b131f07406cfe25b784bff972603b16d70abb01ed3ef827829f7cb46aa83` |
| `../../../../rtl-sim/fma_toggle_formats/` | the bench |

Re-run: `/usr/bin/python3 -I rtl-sim/fma_toggle_formats/run_kinds.py --kinds tools/claims-v3/kinds --out
counts.json --jobs 5 --nogate`, then `predict.py counts.json --out predictor.json`.
