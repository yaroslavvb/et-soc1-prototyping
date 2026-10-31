# Why multiplying zeros is nearly free: the part of the transport the silicon does not pay (Q130(i))

31 October 2026, desk compute on one Mac; **no card was used**. Re-reads Q129's transport netlist
([`../2026-10-27-q129-ledger-scope/`](../2026-10-27-q129-ledger-scope/README.md)) against the RTL
it was assembled from, re-simulates the zero-operand stimulus with the gating that RTL actually
has, and re-prices it. RTL source as Q129: public `core-et`, branch `erbium`, sha `b38a1a31`.

---

## Results

### 1. The headline

Q129's Status item 1 says one lane's **transport** costs **0.654 pJ per multiply-add with every
operand word zero** — 0.223 pJ of clock nets and 0.431 pJ of signal switching — while the **whole
board** costs about **0.27 pJ per multiply-add on the same stimulus** (E38, three-card registered
mean, through Q128 `data.json` → `/permac/mean_zeros_pJ`). Q129 recorded the contradiction and
blamed the latch-array model. **Most of it is not the model. It is three pieces of gating that the
RTL has and Q129's bench does not.**

| zero-operand fp32 multiply-add, one lane, ASAP7 RVT TT, 0.517 V | pJ / MAC |
| --- | ---: |
| Q129, the transport's switching on `zeros` | **0.6540** |
| **this directory, corrected — lower** | **0.1977** |
| **this directory, corrected — upper** | **0.3699** |
| the same signal-only (clock term removed, as an over-idle card figure would) | **0.1468** |
| E38 at the board, over idle, three-card mean | 0.27 |
| Q129's figure ÷ the board | 2.42× |
| **the corrected figure ÷ the board** | **0.73× – 1.37×** (signal-only **0.54×**) |

So the card no longer bounds the bottom-up number out. **Q129's zeros figure failed both readings
of the idle subtract (2.42× the board with the clock, 1.60× without it). The corrected figure
passes both.** It is still a **ceiling** — §5 lists the three reasons — and the correction is a
re-price of the *same* gate-level energies, not a new netlist: §4 says exactly what that buys and
what it does not.

### 2. Where the 0.654 pJ goes

| part (Q129's per-part rows) | Q129 on `zeros` | corrected | what the RTL does |
| --- | ---: | ---: | --- |
| VPU register file array, 64 × 32 3r2w **(model)** | 0.3050 | **0.1008** | two of the three read ports are read-disabled on a TensorFMA, and their addresses do not sweep; the write is gated off when the operand is zero |
| top-level nets, the clock root, the control's ports | 0.2562 | **0.0841 – 0.2562** | the clock still runs, but 1,422 of the netlist's 1,844 fF of clock-pin load is either a latch-array model standing in for a macro or a branch the chip gates off |
| operand bus + F4…F8 result pipeline (`vpu_bypass`) | 0.0799 | **0.0000** | `vpu_bypass`'s clock is held off for the whole TensorFMA, and on `zeros` no data reaches its combinational muxes |
| the five small register files + the collision bypass + control | 0.0129 | 0.0129 | unchanged |
| **total** | **0.6540** | **0.1977 – 0.3699** | |

### 3. The three pieces of gating, each with its line of RTL

**(a) A TensorFMA reads one of the register file's three ports, not three.** `vpu_ctrl.v`
ll. 534–543:

```
assign id_tena_regfile_bypass_en = id_ml_inst_fma_en & (cmd != XOR & cmd != SETZ) | id_ml_tena_quant_en;
assign id_tenb_regfile_bypass_en = id_ml_inst_fma_en & (cmd != XOR & cmd != SETZ);
assign id_regfile_ren[0] = (id_core_valid_int & (sigs.ren1 | sigs.rend) & !id_tena_regfile_bypass_en) | ex_core_gscing;
assign id_regfile_ren[1] = (id_core_valid_int & sigs.ren2 & !id_tenb_regfile_bypass_en)              | ex_core_gscing;
assign id_regfile_ren[2] = (id_core_valid_int & sigs.ren3)                                           | ex_core_gscing;
```

The RTL's own comment on ports 0 and 1 is *"Regular accesses (TFMA disables it)"*: A and B come out
of TENA and TENB, so only port 2 — the accumulator — is read. `vpu_rf.v` ll. 60, 63, 66 hand those
three enables to the compiled macro as `rd_enable0`, `rd_enable1`, `rd_enable2`, so the chip's
register file can turn a read port off. **The open library's substitute cannot**:
`rf_latch_3r_2w.v` ll. 167–169 are

```
assign rd_data_a = vpu_rf[rd_addr_a];
assign rd_data_b = vpu_rf[rd_addr_b];
assign rd_data_c = vpu_rf[rd_addr_c];
```

— three combinational 64:1 select trees, no enable. And the addresses differ too:
`vpu_tensorfma.v` ll. 677–679 and 699–704 build the generated micro-op so that
`inst[REN3_RA_SEL] = fma_exec_accum_reg = {a_row, b_col}` (the sweeping 2 i + h) while
`inst[REN1_RA_SEL] = fma_exec_mat_a_reg = {4'b0, a_rd_ptr}` and
`inst[REN2_RA_SEL] = fma_exec_mat_b_reg = {2'b01, b_rd_ptr, b_col}` — the TENA/TENB buffer
pointers, which barely move. Q129's bench instead ties all three read ports to the sweeping
accumulator index and enables all three
([`../../../../tools/open-flow/scope/q129_scope_top.v`](../../../../tools/open-flow/scope/q129_scope_top.v),
ll. 312–314):

```
assign rf_rd_en    = {uop_valid, uop_valid, uop_valid};
assign rf_rd_thrid = {acc_thrid, acc_thrid, acc_thrid};
assign rf_rd_addr  = {acc_raddr, acc_raddr, acc_raddr};
```

**(b) On an all-zero operand the accumulator writeback is gated off, and with it the register
file's 64 per-entry write clock gates.** The chain, all in `vpu_ctrl.v` unless named:

| line | what |
| --- | --- |
| `vpu_ctrl.v` ll. 1230–1233 | `f3_zero_data_a/b/tmp = (write data == 0)` — a zero is detected when TENA/TENB is *filled* |
| ll. 748–755 | the per-entry zero masks `ex_tensora/b/tmp_zero_mask` are updated at that write |
| l. 817 | `ex_tensor_zero_mask = A-zero \| (B-zero-tima0 & B-zero-tima1)` |
| l. 837 | `ex_fma_gate_mask = ex_tensor_zero_mask & {8{(cmd == MADD) && ex_tensorfma_en}}` |
| l. 839 | `ex_txfma_valid = {8{all}} & ~ex_fma_gate_mask & ex_ml_gate_mask` — the lane gets no valid |
| l. 844 | `ex_ml_mask_to_f2 = ex_txfma_valid_all ? ~ex_fma_gate_mask & ex_ml_mask : ex_ml_mask` |
| l. 1002 | `if (f2_wen && f2_ml_inst_val) f2_regfile_wmask = f2_ml_mask` |
| ll. 1132, 1330, 1370, … | the mask walks F3 → F8 |
| `vpu_lane.v` l. 520 | `f8_rf_wmask[0] = f3_tima_rf_wen[0] \| (f8_regfile_wen & f8_regfile_wmask)` |
| `vpu_rf.v` l. 22 | `wr_en_masked_0 = wr_en[0] & wr_mask[0]` → **0** |
| `rf_latch_3r_2w.v` ll. 101, 125, 133, 144 | `dec_wr_en_a = (1 << wr_addr_a) & {64{wr_en_a}}` → all zero; `cbuf_wr`'s enable is `wr_en_a \| wr_en_b` → the second-level clock gate blocks; the 64 `cbuf_rf_wr` per-entry gates and `cbuf_wr_data_a` therefore never open |

Q129's bench writes on every micro-op in every pattern: `q129_scope_top.v` instantiates the
control model with `.ex_wmask(uop_valid)` (l. 252) and feeds its `f8_wmask` straight to
`rf_wr_en`/`rf_wr_mask` (ll. 315, 317), and `tb_scope.sv`'s `one_op()` is a bare triple loop of
`issue(1, k, i, h)` with no zero test anywhere in the file. **The arithmetic bench of the same
project does have it** —
[`tools/open-flow/txfma/tb_gate.sv`](../../../../tools/open-flow/txfma/tb_gate.sv) l. 57:

```
assign lane_valid[l] = uop_valid & (uop_mul | ((uop_a != 32'b0) & (uop_b[l] != 32'b0)));
```

so Q126(e)'s arithmetic figures already honour the gate and only the transport's do not. That is
the whole defect in one line.

**(c) `vpu_bypass`'s clock is off for the whole TensorFMA.** `vpu_ctrl.v` ll. 1244, 1334, 1403,
1463, 1538 are all of the form

```
assign fN_bypass_clk_en = (fN_wen & !fN_ctrl_sigs.txfma) | fN_ctrl_sigs.trans
                        | (cmd == VPU_FCMD_MVS_FX) | (cmd == VPU_FCMD_MVZ_FX);
```

Every term is 0 for a TensorFMA32, so `clock_en_bypass` (`vpu_lane.v` l. 218) is 0 and
`cgate_bypass` (l. 245) holds `clock_bypass` low: the block's 190 flip-flops never clock, because a
TXFMA result enters at F8 through a combinational mux and needs none of the F4…F8 bypass registers.
Q129's control model drives them every cycle instead (`q129_lane_ctl`, ll. 189–193: `f3_clk_en = v[1] | uop_valid`, with
`f4…f7_clk_en` tied to it).

That the `bypass` row's whole `zeros` cost is its clock is visible in Q129's own data without any
re-simulation: on `zeros` the block shows **216.5 toggles/MAC**, and the clock root `(top)` shows
**216.4** — 2 × 529 cycles ÷ 512 MACs = 2.066 toggles per net per MAC, the signature of about 105
nets toggling on every edge — while `sim_acct.txt` records `bus_toggles = res_toggles = 0` for that
pattern, so no data moved in it at all.
(`../2026-10-27-q129-ledger-scope/power-mixed/power_gr_zeros.json` → `blocks/bypass`, `blocks/(top)`.)

### 4. What was re-simulated, and the factors it measured

A full gate-level re-price is **out of reach on this machine**: `tools/open-flow/txfma/setup.sh`
pins `oss-cad-suite-linux-x64` and an OpenROAD build from a `linux-64` conda channel, Q129's
netlist and SAIFs are not committed, and the approved lab host for this run was not available. What
is here instead is a **structural simulation of the register file's read and write paths** under
Verilator — the one tool this desk has — driven by the same micro-op stream and the same operand
files, in Q129's wiring and in the RTL's, so the ratio between them can be measured and applied to
Q129's committed gate-level energies.

[`sim/rf3r2w_struct.sv`](sim/rf3r2w_struct.sv) writes `rf_latch_3r_2w`'s read path out the way a
synthesis tool builds it — six levels of 2:1 muxes per bit per port, 32 + 16 + 8 + 4 + 2 + 1 = 63
per bit, 2,016 per port, 6,048 in all — plus the one-hot write decode (l. 125), the second-level write
clock gate (l. 133), the 64 per-entry gates (l. 144) and the Ph2 write-data latch (l. 101).
[`sim/tb_gate_audit.sv`](sim/tb_gate_audit.sv) drives two copies of it from one stream (PRM 9.4:
for each B row k, for each A row i, two micro-ops; 512 per op, one lane), one wired as
`q129_scope_top.v` wires it and one as `vpu_ctrl.v`/`vpu_tensorfma.v` present it, and counts
**mux-output bit transitions** and **select-pin transitions** (an address bit that changed, times
the muxes it selects, times 32 bits — the quantity the address buffer tree's capacitance is
proportional to). [`sim/counts.txt`](sim/counts.txt) is the output; the cross-check is that the
bench copy's address-bit flips come to 2,976 = 3 × 992, and 992 is exactly Q129's own
`idx_toggles` per op in `sim_acct.txt`.

| measured on `zeros` | bench wiring | RTL wiring | factor |
| --- | ---: | ---: | ---: |
| select-pin transitions, all three ports | 2,095,104 | 1,495,040 | 0.7136 |
| select-pin transitions, port 2 alone *(what the macro enables)* | 2,095,104 | **698,368** | **0.33333** |
| mux-output bit transitions | **0** | **0** | — |
| per-entry write clock edges | 1,024 | 64 | **0.0625** |
| micro-ops the zero gate fires on, of 512 | 0 | **480** | — |

Two things fall out of the second and third rows. **The array's entire `zeros` energy is
address-tree switching**: with every entry holding zero, not one mux output in 6,048 × 32 changes
state, which is why the 0.3050 pJ/MAC splits as 0.3016 pJ of address/select tree and 0.0034 pJ of
the array's own gated clocks (the latter read straight off Q129's `power-mixed-clkwide/` run, which
widened the clock regex to catch `clk_rf_wr[i]`, `clk_wr_data_a_n` and `enclk`). And **the three
read ports are identical in the bench**, so dropping two of them is exactly a factor of 3 — on
`zeros` and on every other pattern.

[`reprice.py`](reprice.py) applies those factors part by part and writes
[`zeros-transport.json`](zeros-transport.json). The clock term is carried as a **bound**, not a
point: clock-tree energy tracks the pin load the tree drives, and of this netlist's 1,844.0 fF of
clock-pin capacitance (`census_mixed.json` → `total/clk_cap_ff`) **1,065.6 fF is the VPU register
file's latch-array model** and **267.0 fF the TIMA file's**, each standing in for a compiled macro
with one clock pin, while **90.4 fF is `vpu_bypass`, gated off**. 421.0 fF remains — TENA, the two
TENB files and the TMP file, which are `rf_latch_1r_1w` in the chip too, plus the control — so the
clock term is between 22.8% and 100% of Q129's 0.2231 pJ/MAC. The three real latch files are not
touched.

**The honest reading of what the factors are.** 0.33333 and 0.0625 are *measured* on the stream, on
a structure written from the RTL. Turning them into energy assumes that, inside one block, energy
is proportional to the weighted transition count the simulation returns — which is the same ½CV²
model Q129 priced with, applied at a coarser grain. The clock bound assumes clock-tree energy is
proportional to leaf pin load. Both are stated here so they can be attacked; §6 names the
simulation that would remove them.

### 5. The corrected figure is still a ceiling, for three reasons

1. **the array is still a 2 kbit standard-cell latch array.** 0.1008 pJ/MAC is one 64:1 select tree
   per bit with a 1,024-load select net on its first level. The chip has `vpu_64x32_3r2w_vpurf`, a
   compiled macro that reads through a 6-bit decoder, wordlines and sense amplifiers. Q129's
   `METHOD.md` puts the area bias at roughly an order of magnitude; nothing here measures the
   macro;
2. **the clock root is charged to one lane in full.** Q129 says so itself
   (`ledger-scope.json` → `gap.charging_convention`): a one-lane netlist's clock root is not an
   eighth of an eight-lane one, so it is not divided. Divided by `VPU_LANE_NUM` = 8 the corrected
   lower figure would fall by a further ~0.04 pJ/MAC. The convention is kept unchanged here so the
   two ledgers still add;
3. **the flow's own limits are Q129's, unchanged**: global-route capacitance only, no coupling, 25%
   of the extracted capacitance priced on `zeros`, no glitch factor, the SDC missed
   (`../2026-10-27-q129-ledger-scope/METHOD.md` § The flow).

### 6. What would settle it

In order of how much it would buy, and all of it desk work except the last:

1. **re-run Q129's own flow with the bench corrected** — three edits, no new modelling:
   `q129_scope_top.v` → `rf_rd_en = {1'b0, 1'b0, uop_valid}` and the three read addresses driven
   from `fma_exec_accum_reg`, `fma_exec_mat_a_reg`, `fma_exec_mat_b_reg`; `tb_scope.sv` → the
   `lane_valid` term `tb_gate.sv` l. 57 already has; `q129_lane_ctl` → `f3…f7_clk_en = 0` for a
   txfma. Then `synth.sh`, `pnr.tcl`, `gatesim.sh` for `zeros`/`ones`/`randn` and `reduce.sh`. This
   replaces every factor in §4 with a measured gate-level number and re-does CTS on the smaller
   clock load. It needs a Linux host with the pinned `oss-cad-suite` and OpenROAD, about two hours;
2. **blackbox the two macros with a vendor clock-pin capacitance and re-run CTS**, which turns the
   §4 clock bound into a figure;
3. **E74, the register-file-cells card experiment** Q129 already names: the only thing that replaces
   the latch-array model with a measurement and so removes reason 1 above;
4. **a card experiment that moves the gate without moving the data**: an operand stream of
   denormal-but-nonzero words (`0x00000001`) against one of exact zeros, matched in Hamming weight
   per micro-op. Both stream the same number of bits down the operand bus; only the second trips
   `f3_zero_data_a/b`. The difference is the zero gate's own worth at the board, with the bus
   activity held still — which no experiment in this project has yet isolated.

---

## What was planned, and what happened

Planned: read the RTL, find which part of the 0.654 pJ the silicon does not pay, **re-simulate the
zeros stimulus with the gating the RTL actually has (gate-level on the existing netlists)** and
re-price.

Departures, both dated 31 Oct 2026 and both written before the numbers above:

- **gate-level re-simulation was not possible on this machine and was not attempted.** The flow's
  `setup.sh` pins a Linux-x64 toolchain and a `linux-64` OpenROAD; Q129's netlist and SAIFs are not
  committed, so there was nothing to re-simulate on. The structural Verilator simulation of §4
  replaces it, and §6 item 1 is the exact run that would supersede this directory. Every number in
  §1 and §2 is therefore a **re-price of Q129's committed gate-level energies**, not a new
  measurement of them — said again in the result object;
- **the write side's split was taken from Q129's `power-mixed-clkwide/` run** rather than from a new
  one. That run exists precisely because it isolates `clk_rf_wr[i]`, `clk_wr_data_a_n` and `enclk`,
  and Q129 committed it as a robustness check on its own clock/signal split.

Nothing here is a card claim, so nothing was pre-registered; no card was touched and no governor,
clock or threshold was read or set.

---

## What it changes

**For the Horace hub's Status item 1** — "the transport's zero-operand floor contradicts the card's
own zeros measurement" — the contradiction is resolved and the ledger row moves:

| | Q129 | corrected |
| --- | ---: | ---: |
| transport on `zeros`, switching | 0.6540 | **0.1977 – 0.3699** |
| transport on `randn`, switching | 1.0329 | **0.4621 – 0.6342** |
| transport on `randn`, + the cells' internal energy | 1.261 – 1.484 | **0.664 – 0.911** |
| the arithmetic, + internal (Q126(e), unchanged — its bench already gates on zeros) | 1.946 | 1.946 |
| **the bottom-up total, one random fp32 multiply-add** | **3.21 – 3.43** | **2.61 – 2.86** |
| closure vs E38 at the board, 5.783 pJ | 55 – 59% | **45 – 49%** |
| closure vs the minion rail, Q128's 4.337 pJ | 74 – 79% | **60 – 66%** |
| closure vs the rail on Q129's corrected footing, 4.77 pJ | 67 – 72% | **55 – 60%** |

**The bottom-up ledger closes less of the board than Q129 published, and that is the right
direction**: the part that came off was a bench artefact, and a ledger that over-charged one lane's
transport by 0.4–0.6 pJ was closing the gap with energy the chip does not spend.

**For the blog's kinds-of-numbers table**, the zeros column now has a mechanism rather than a
contradiction, and the gate is a *data* gate, not a sparsity feature: the same simulation shows it
firing on **480 of 512** micro-ops for an all-zero tile and **454 of 512** for a 75%-sparse one
(`zeros-transport.json` → `gating_by_pattern`), because a lane is gated when **either** operand
word is zero.

## Files

| File | What |
| --- | --- |
| `README.md` | this |
| `reprice.py` | the re-price: reads Q129's `power-mixed/`, `power-mixed-clkwide/` and `census_mixed.json` plus `sim/counts.txt`, writes `zeros-transport.json` |
| `zeros-transport.json` | every number above, with the factors, the bounds and the card check |
| `sim/rf3r2w_struct.sv` | the structural read/write path of `rf_latch_3r_2w` at 64 × 32, with the toggle counters |
| `sim/tb_gate_audit.sv` | the micro-op stream, the two wirings, and the zero gate as `vpu_ctrl.v` computes it |
| `sim/run.sh` | build and run (Verilator only; `nice -n 10`, 4 build jobs) |
| `sim/counts.txt` | the counts, one JSON line per pattern × `+allmadd` |

```bash
# the operand files, the same seed and warm-up Q129 used
for p in zeros ones randn sparse75; do
  python3 -I rtl-sim/fma_toggle/tiles.py $p $TILES/$p.hex --seed 1 --iters-before 1000
done
OUT=$SCRATCH/q130i TILES_DIR=$TILES bash docs/reports/data/2026-10-31-q130-zeros-transport/sim/run.sh
cd docs/reports/data/2026-10-31-q130-zeros-transport
python3 -I reprice.py --q129 ../2026-10-27-q129-ledger-scope --counts sim/counts.txt \
    --out zeros-transport.json
```

Verilator here is the conda-forge build `rtl-sim/fma_toggle/README.md` § "On a Mac" installs
(5.052); its generated makefile names a cross compiler it does not ship, so `run.sh` overrides
`CXX`/`LINK`, exactly as that `Makefile` does. The structural simulation is version-insensitive in
the way the RTL toggle counts are not: it counts nodes of a tree this directory writes out itself,
not names the optimiser happens to keep.
