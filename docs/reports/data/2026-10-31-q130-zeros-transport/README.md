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
mean, through Q128 `data.json` → `/permac/mean_zeros_pJ`; the three cards themselves read
**0.1633, 0.2512 and 0.4034 pJ/MAC**, `data.json` → `e38_registered`, a spread wider than most of
what is argued below). Q129 recorded the contradiction and blamed the latch-array model. **Most of
it is not the model. It is three pieces of gating that the RTL has and Q129's bench does not.**

| zero-operand fp32 multiply-add, one lane, ASAP7 RVT TT, 0.517 V | pJ / MAC |
| --- | ---: |
| Q129, the transport's switching on `zeros` | **0.6540** |
| **this directory, corrected — lower** | **0.1977** |
| **this directory, corrected — upper** | **0.3699** |
| the same signal-only (clock term removed, as an over-idle card figure would) | **0.1468** |
| the same on the strict same-netlist reading (no read-enable pin at all; §4) | 0.4846 |
| E38 at the board, over idle, three-card mean | 0.27 |
| the three registered cards themselves | 0.1633 / 0.2512 / 0.4034 |

**The contradiction is narrowed, not resolved.** Q129's zeros figure failed both readings of the
idle subtract; the corrected figure passes one of them cleanly and straddles the board on the
other. All four readings, spelled out (`zeros-transport.json` → `card_check.readings`):

| reading | corrected, pJ/MAC | ÷ the board | verdict |
| --- | ---: | ---: | --- |
| signal-only, against the 0.27 mean — the clock term is inside the idle subtract | 0.1468 | **0.54×** | **passes** (Q129: 1.60×) |
| with the clock, against the 0.27 mean — the lane's clocks are gated at idle | 0.1977 – 0.3699 | **0.73× – 1.37×** | **straddles** (Q129: 2.42×) |
| with the clock, against the *lowest* of the three cards, 0.1633 | 0.1977 – 0.3699 | 1.21× – 2.27× | fails |
| strict same-netlist: the latch array has no read-enable pin, so only the bench's addresses are fixable | 0.4846 | 1.79× | fails |

At the top of its own bound one lane's transport still exceeds the **whole board** by 37%, which
is the same kind of contradiction Q129 was faulted for, only smaller: 0.37× over instead of
1.42× over. **So the upper end is the one to quote against a card, and the honest claim is that
the gap closed by about 4× and the remainder is accounted for by named, listed modelling
limits — not that it is gone.** It is still a **ceiling** — §5 lists the reasons — and the
correction is a re-price of the *same* gate-level energies, not a new netlist: §4 says exactly
what that buys and what it does not.

### 2. Where the 0.654 pJ goes

| part (Q129's per-part rows) | Q129 on `zeros` | corrected | what the RTL does |
| --- | ---: | ---: | --- |
| VPU register file array, 64 × 32 3r2w **(model)** | 0.3050 | **0.1008** | two of the three read ports are read-disabled on a TensorFMA, and their addresses do not sweep; the write is gated off when the operand is zero |
| top-level nets, the clock root, the control's ports | 0.2562 | **0.0841 – 0.2562** | the clock still runs, but 1,423 of the netlist's 1,844 fF of clock-pin load is either a latch-array model standing in for a macro or a branch the chip gates off |
| operand bus + F4…F8 result pipeline (`vpu_bypass`) | 0.0799 | **0.0000** | `vpu_bypass`'s clock is held off for the whole TensorFMA, and on `zeros` no data reaches its combinational muxes |
| the five small register files + the collision bypass + control | 0.0129 | 0.0129 | unchanged |
| **total** | **0.6540** | **0.1977 – 0.3699** | |

### 3. The three pieces of gating, each with its line of RTL

**(a) A TensorFMA reads one of the register file's three ports, not three.** `vpu_ctrl.v`
ll. 534–543, **paraphrased to fit** (`cmd` for `id_vpu_ctrl.sigs.cmd`, `XOR`/`SETZ` for the
command macros, two-line assigns joined):

```
assign id_tena_regfile_bypass_en = id_ml_inst_fma_en & (cmd != XOR & cmd != SETZ) | id_ml_tena_quant_en;
assign id_tenb_regfile_bypass_en = id_ml_inst_fma_en & (cmd != XOR & cmd != SETZ);
assign id_regfile_ren[0] = (id_core_valid_int & (sigs.ren1 | sigs.rend) & !id_tena_regfile_bypass_en) | ex_core_gscing;
assign id_regfile_ren[1] = (id_core_valid_int & sigs.ren2 & !id_tenb_regfile_bypass_en)              | ex_core_gscing;
assign id_regfile_ren[2] = (id_core_valid_int & sigs.ren3)                                           | ex_core_gscing;
```

The RTL carries the comment *"Regular accesses (TFMA disables it)"* against these ren lines — on
all three of them, port 2 included, so the argument rests not on the comment but on the
`& !id_ten{a,b}_regfile_bypass_en` terms, which only ports 0 and 1 have: A and B come out of TENA
and TENB, so only port 2 — the accumulator — is read. `vpu_rf.v` ll. 60, 63, 66 hand those
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
ll. 310–314, **its own comment included**):

```
  // Sources 1 and 2 come from TENA / TENB, so only the third read port carries the
  // accumulator; vpu_ctrl.v still presents all three addresses, which is what the
  // read-port and index energy below is measured against.
  assign rf_rd_en    = {uop_valid, uop_valid, uop_valid};
  assign rf_rd_thrid = {acc_thrid, acc_thrid, acc_thrid};
  assign rf_rd_addr  = {acc_raddr, acc_raddr, acc_raddr};
```

**This is a stated convention, not an oversight, and exactly half of it is right.** Q129 knew
sources 1 and 2 come from TENA/TENB and said so. What it got wrong is the inference: it is true
that `vpu_ctrl.v` presents three addresses, but (i) two of them are **read-disabled** — the
`& !id_ten{a,b}_regfile_bypass_en` terms above, which the compiled macro honours as
`rd_enable0/1` — and (ii) the two it presents are the TENA/TENB **buffer pointers**, which barely
move, not three copies of the sweeping accumulator index. So the convention over-prices the read
path by exactly 3× against the silicon, and by 1/0.714 = 1.40× even against the enable-less latch
array it was measured on.

**(b) On an all-zero operand the accumulator writeback is gated off, and with it the register
file's 64 per-entry write clock gates.** The chain, all in `vpu_ctrl.v` unless named:

| line | what |
| --- | --- |
| `vpu_ctrl.v` ll. 1230–1233 | `f3_zero_data_a/b/tmp = (write data == 0)` — a zero is detected when TENA/TENB is *filled*. The A test is one scalar word broadcast to all eight lane bits (`{8{…}}`, l. 1230); the B test is per lane (l. 1233) |
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

**Why one 32-bit B word is the exact test here, and not a simplification.** Line 817's B term is
an **AND of two** TENB entries — `ex_tensorb_zero_mask[raddr]` and `[raddr | 1]` (ll. 808, 811) —
so on the face of it a lane is gated only when *both* halves of the paired B operand are zero,
which would make this directory's `sparse75` figure too high. It is not, because **both indices
collapse to the same entry on an fp32 TensorFMA**: each is selected by `ex_tima_valid_unqual`, and

```
`RST_EN_FF(clock, reset, tima_clk_en, s1_tima_valid, s0_fma_en_conv && req_int8, 1'b0)
```

(`vpu_tensorfma.v` l. 861 → `ex_tima_valid` l. 880 → `vpu_ctrl.v`'s port l. 1747) means TIMA is
live on an **int8** TensorFMA and nowhere else. With `ex_tima_valid_unqual` = 0 both terms index
`ex_ra2_ten`, the AND is idempotent, and the mask is exactly `A-zero | B-zero` — one scalar A word
or one 32-bit B word for that lane. That is what `sim/tb_gate_audit.sv` ll. 103–105 implement, and
it is why `480 of 512` and `454 of 512` are exact and not upper bounds. The AND does bite on an
int8 TIMA op, where the two addresses differ; nothing in this directory is int8, and the bench
does not model that case. (`zeros-transport.json` → `gating_rule`.)

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
per bit, so **6,048 mux outputs in all** (63 per bit × 32 bits × 3 ports) — plus the one-hot write
decode (l. 125), the second-level write clock gate (l. 133), the 64 per-entry gates (l. 144) and
the Ph2 write-data latch (l. 101).
[`sim/tb_gate_audit.sv`](sim/tb_gate_audit.sv) drives two copies of it from one stream (PRM 9.4:
for each B row k, for each A row i, two micro-ops; 512 per op, one lane), one wired as
`q129_scope_top.v` wires it and one as `vpu_ctrl.v`/`vpu_tensorfma.v` present it, and counts
**mux-output bit transitions** and **select-pin transitions** (an address bit that changed, times
the muxes it selects, times 32 bits — the quantity the address buffer tree's capacitance is
proportional to). The fp32 multiply-adds come in from [`sim/accum.py`](sim/accum.py), one word per
micro-op, so the testbench contains no floating point at all (§ Corrections says why).
[`sim/counts.txt`](sim/counts.txt) is the output.

**Three cross-checks, all in the committed output.** (a) The bench copy's address-bit flips come
to 2,976 = 3 × 992, and 992 is exactly Q129's own `idx_toggles` per op in `sim_acct.txt`. (b)
Every row of `counts.txt` carries `rd_chk_fail: 0` — the read tree delivers `rf[rd_addr]` on all
three ports on every cycle of every pattern, which is what catches a mis-built tree. (c) The
counts agree **digit for digit, on all eight rows and every counter**, with two independent Python
replicas of these two SystemVerilog files, one of them written by the reviewer of the first
version before this correction was made.

| measured on `zeros` | bench wiring | RTL wiring | factor |
| --- | ---: | ---: | ---: |
| select-pin transitions, all three ports | 2,095,104 | 1,495,040 | 0.7136 |
| select-pin transitions, port 2 alone *(what the macro enables)* | 2,095,104 | **698,368** | **0.33333** |
| mux-output bit transitions | **0** | **0** | — |
| per-entry write clock edges | 1,024 | 64 | **0.0625** |
| micro-ops the zero gate fires on, of 512 | 0 | **480** | — |

Two things fall out of the second and third rows. **The array's entire `zeros` energy is
address-tree switching**: with every entry holding zero, not one of the 6,048 mux outputs changes
state, which is why the 0.3050 pJ/MAC splits as 0.3016 pJ of address/select tree and 0.0034 pJ of
the array's own gated clocks (the latter read straight off Q129's `power-mixed-clkwide/` run, which
widened the clock regex to catch `clk_rf_wr[i]`, `clk_wr_data_a_n` and `enclk`). And **the three
read ports are identical in the bench**, so dropping two of them is exactly a factor of 3 — on
`zeros` and on every other pattern. (On `randn` the measured ratio is 232,378 / 697,134, which is
1/3 to the digit; on `ones` 1,024 / 3,072, the same.)

[`reprice.py`](reprice.py) applies those factors part by part and writes
[`zeros-transport.json`](zeros-transport.json). The clock term is carried as a **bound**, not a
point: clock-tree energy tracks the pin load the tree drives, and of this netlist's 1,844.0 fF of
clock-pin capacitance (`census_mixed.json` → `total/clk_cap_ff`) **1,065.6 fF is the VPU register
file's latch-array model** and **267.0 fF the TIMA file's**, each standing in for a compiled macro
with one clock pin, while **90.4 fF is `vpu_bypass`, gated off**. **421.0 fF** remains, and it
itemises exactly:

| what survives | fF |
| --- | ---: |
| `tentmp_rf` | 142.14 |
| `LANE_TIMA[0].tenb_rf` | 79.46 |
| `LANE_TIMA[1].tenb_rf` | 79.46 |
| `tena_rf` | 48.13 |
| `vrf` wrapper, excluding the array itself (1,112.70 − 1,065.62) | 47.08 |
| `ctl` | 24.73 |
| **total** | **421.00** |

— TENA, the two TENB files and the TMP file, which are `rf_latch_1r_1w` in the chip too, plus the
register file's own wrapper and the control. So the clock term is between 22.8% and 100% of Q129's
0.2231 pJ/MAC. The three real latch files are not touched.

**The honest reading of what the factors are.** 0.33333 and 0.0625 are *measured* on the stream, on
a structure written from the RTL. Turning them into energy assumes that, inside one block, energy
is proportional to the weighted transition count the simulation returns — which is the same ½CV²
model Q129 priced with, applied at a coarser grain. The clock bound assumes clock-tree energy is
proportional to leaf pin load.

**And the clock bound's lower end is optimistic, in two ways worth naming** (`zeros-transport.json`
→ `clock_bound.bias`). First, the 1,844.0 fF denominator is clock-**pin** capacitance, while the
energy being scaled is the power run's clock-**net** energy, whose capacitance is **2,766.7 fF**
(`power-mixed/power_gr_zeros.json` → `total/clock_cap_fF`) — about **922.7 fF of it tree wiring**.
Re-running CTS on a smaller leaf load drops leaf wires but keeps the trunk, so the real reduction
is *less* than proportional to leaf pin load. Second, the two compiled macros' own clock pins are
removed with their models and never added back. Both push the true figure **above** the lower end,
which is why §1 quotes the **upper** end against the card. All of this is stated here so it can be
attacked; §6 names the simulation that would remove it.

### 5. The corrected figure is still a ceiling, for four reasons

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
   (`../2026-10-27-q129-ledger-scope/METHOD.md` § The flow);
4. **the clock bound's lower end is optimistic** for the two reasons at the end of §4 (a pin-load
   fraction applied to net energy that is 1/3 tree wiring; the macros' own clock pins never added
   back). This one cuts the other way from 1–3: it means the *lower* end of 0.1977 – 0.3699 is
   softer than the upper, which is a second reason to quote the upper.

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

A note on the ordering: the two departures above are dated 31 Oct, but the whole directory landed
in one commit, so *that they were written before the numbers* is an assertion of this README's and
cannot be checked from the record. Nothing was registered here, so the pre-registration rule does
not bite; the claim is still unverifiable rather than verified, and is flagged as such.

---

## Corrections, 31 October 2026

Reviewed the same day it was written, and corrected the same day. Every change below is in this
commit. The two simulation defects are recorded in the source files themselves and in
`zeros-transport.json` → `corrections`.

**Two defects in the structural simulation. Neither moved the headline.**

1. **An off-by-one built the wrong read tree.** `rf3r2w_struct.sv`'s `offs()` read
   `NODES - (ENTRIES >> L)`, which is **−1** at level 0 where its own comment says 0. Level 0's
   first node write was out of range and dropped, every level read its children one index low, and
   the root node `node[NODES-1]` that `rd_data` reads was never assigned. Now
   `ENTRIES - (ENTRIES >> L)`, and a new `rd_chk_fail` counter asserts
   `rd_data[p] == rf[rd_addr[p]]` on every port every cycle so the same mistake cannot pass
   silently again. It reads 0 in every row of `counts.txt`.
2. **The testbench's multiply-add was returning `c`.** It computed the FMA with
   `$bitstoshortreal` / `$shortrealtobits`. **Verilator does not support `shortreal`**: it
   promotes it to `real` and warns `Unsupported: shortreal being promoted to real`, which this
   directory's `-Wno-lint` hid. The casts therefore read a double's bit pattern — 1.0f became a
   denormal of about 5.2 × 10⁻³¹⁵ — every product underflowed to zero, and `a*b + c` returned `c`
   unchanged. Displaying one micro-op shows it plainly:
   `A=3f800000 B=3f800000 C=467a0000 fma=467a0000`, i.e. 1.0 × 1.0 + 16000.0 = 16000.0. The
   register file was still written and read, with the tiles' own initial C values moving around
   it, so the address and write sides were untouched — but the data-dependent columns were
   measured on an accumulator that never accumulated. The arithmetic now comes from the new
   [`sim/accum.py`](sim/accum.py) as a stream of words, one per micro-op, and the testbench holds
   no floating point. One stream serves both wirings because a zero-operand micro-op's result *is*
   the accumulator it read; `accum.py --check` asserts that over the whole stream and `run.sh`
   passes it.

**What those two moved, and what they did not.** Not the headline, and not one pattern total.
`sel_pin_tr` and `addr_tr` are functions of the address stream alone; `dec_tr`, the clock-edge
counters and the zero-gate counts are functions of the gate alone; none of them reads the tree or
the result. `f_read_silicon` is 1/3 exactly before and after, and so is the data-dependent
`f_data_read`, because the bench's three read ports and the RTL's port 2 carry the same addresses
over the same file. What did move: the `mux_out_tr` and `rd_data_tr` columns of `counts.txt`, and
the two `*_model_rewired_only` figures built on their ratio — on `randn` 0.829 → 0.849, on `ones`
0.349 → 1.000. Those are the secondary "what if only the addresses were fixed" figures of §1's
fourth reading; the zeros one is unchanged because its data-dependent term is exactly 0.

**Eight restatements, no new measurement.**

| what | was | now |
| --- | --- | --- |
| §1's verdict | "the corrected figure passes both readings"; "the contradiction is resolved" | **narrowed, not resolved**: one reading passes at 0.54×, one straddles at 0.73×–1.37×, two fail. All four are tabulated and in `card_check.readings` |
| the board figure | the 0.27 mean alone | the mean **and** the three registered cards, 0.1633 / 0.2512 / 0.4034 |
| the ledger's was→now row | 2.61–2.86 pJ and 45–49% beside Q129's 3.21–3.43 and 55–59% | **both internal-energy conventions published**, because Q129's row adds the whole internal estimate and this one scaled it. Like-for-like with Q129: 2.86–3.03 pJ, 49–52% |
| the clock bound | an assumption, direction unstated | the **direction named**: the lower end is optimistic, twice over (§4 end, `clock_bound.bias`) |
| the clock breakdown | five blocks totalling 373.9 of 421.0 fF | the `vrf` wrapper's own 47.08 fF added; the six now total 421.00 |
| Q129's bench | "wrong for a dull reason" | its **own comment quoted** (§3a), and which half of it is wrong said exactly |
| the mux count | "6,048 muxes × 32 bits" | **6,048 mux outputs** (63 per bit × 32 bits × 3 ports) — the bits were already inside the 6,048 |
| the repro line | `python3 -I … tiles.py` | `/usr/bin/python3 … tiles.py`: plain `python3` on this machine has no numpy, and `-I` hides the site-packages that do |

**One fault found in review that this directory does not accept.** The review held that
`sparse75`'s 454 of 512, and the claim that *either* operand word gates a lane, rest on a gate
model weaker than l. 817's `A-zero | (B-zero-tima0 & B-zero-tima1)`, and should be softened to
436–454. They should not: on an **fp32** TensorFMA both of l. 817's B terms index the same TENB
entry, so the AND is idempotent and `A-zero | B-zero` is exact. The proof is `s1_tima_valid <=
s0_fma_en_conv && req_int8` (`vpu_tensorfma.v` l. 861) — TIMA is int8-only, so
`ex_tima_valid_unqual` is 0 here and ll. 808 and 811 both read `ex_ra2_ten`. §3b now carries that
derivation, and the testbench's header, which did paraphrase l. 817 loosely, carries it too. 436
of 512 is the right figure for an **int8** TIMA op, which nothing here measures.

---

## What it changes

**For the Horace hub's Status item 1** — "the transport's zero-operand floor contradicts the card's
own zeros measurement" — the contradiction is **narrowed and the ledger row moves**. Item 1 names
"the register file's read ports, its read mux tree **and its clocking**": the read ports and the
mux tree are now accounted for, the clocking half is still a 22.8%–100% bound, and the array is
still a standard-cell latch-array model that only **E74** replaces. So item 1 shrinks; it does not
close.

The ledger. **Two internal-energy conventions, both published**, because Q129's 1.261 / 1.484 pJ
*add* the whole internal estimate (0.4512 pJ/MAC on `randn`) to the switching, while this
directory's first pass *scaled* it with the switching. Setting one beside the other without saying
so is not like-for-like, so both rows are here and the like-for-like comparison with Q129 is the
middle column:

| | Q129 | corrected, Q129's additive convention | corrected, internal scaled |
| --- | ---: | ---: | ---: |
| transport on `zeros`, switching | 0.6540 | **0.1977 – 0.3699** | **0.1977 – 0.3699** |
| transport on `randn`, switching | 1.0329 | **0.4621 – 0.6342** | **0.4621 – 0.6342** |
| transport on `randn`, + the cells' internal energy | 1.261 – 1.484 | **0.913 – 1.085** | **0.664 – 0.911** |
| the arithmetic, + internal (Q126(e), unchanged — its bench already gates on zeros) | 1.946 | 1.946 | 1.946 |
| **the bottom-up total, one random fp32 multiply-add** | **3.21 – 3.43** | **2.86 – 3.03** | **2.61 – 2.86** |
| closure vs E38 at the board, 5.783 pJ | 55 – 59% | **49 – 52%** | **45 – 49%** |
| closure vs the minion rail, Q128's 4.337 pJ | 74 – 79% | **66 – 70%** | **60 – 66%** |
| closure vs the rail on Q129's corrected footing, 4.77 pJ | 67 – 72% | **60 – 64%** | **55 – 60%** |

The additive column is the one to set against Q129's published 55–59%; the scaled column is the
more defensible of the two in its own right, because the combinational transitions that carry the
internal energy are exactly the ones the gating removes. **Either way the bottom-up ledger closes
less of the board than Q129 published, and that is the right direction**: the part that came off
was a bench artefact, and a ledger that over-charged one lane's transport by 0.4–0.6 pJ was
closing the gap with energy the chip does not spend.

**For the blog's kinds-of-numbers table**, the zeros column now has a mechanism rather than a
contradiction, and the gate is a *data* gate, not a sparsity feature: the same simulation shows it
firing on **480 of 512** micro-ops for an all-zero tile and **454 of 512** for a 75%-sparse one
(`zeros-transport.json` → `gating_by_pattern`), because on an fp32 TensorFMA a lane is gated when
**either** operand word is zero (§3b proves the "either", which is not what l. 817 says on its
face).

## Files

| File | What |
| --- | --- |
| `README.md` | this |
| `reprice.py` | the re-price: reads Q129's `power-mixed/`, `power-mixed-clkwide/` and `census_mixed.json` plus `sim/counts.txt`, writes `zeros-transport.json` |
| `zeros-transport.json` | every number above, with the factors, the bounds and the card check |
| `sim/rf3r2w_struct.sv` | the structural read/write path of `rf_latch_3r_2w` at 64 × 32, with the toggle counters and the read-path self-check |
| `sim/tb_gate_audit.sv` | the micro-op stream, the two wirings, and the zero gate as `vpu_ctrl.v` computes it. No floating point |
| `sim/accum.py` | the fp32 multiply-add stream, one word per micro-op, with the one-stream-serves-both-wirings check |
| `sim/run.sh` | build and run (Verilator + `accum.py`; `nice -n 10`, 4 build jobs) |
| `sim/counts.txt` | the counts, one JSON line per pattern × `+allmadd`; `rd_chk_fail` is 0 in every row |

```bash
# the operand files, the same seed and warm-up Q129 used. /usr/bin/python3 is the interpreter
# with numpy on this machine, and -I would hide the site-packages that hold it
for p in zeros ones randn sparse75; do
  /usr/bin/python3 rtl-sim/fma_toggle/tiles.py $p $TILES/$p.hex --seed 1 --iters-before 1000
done
# run.sh calls sim/accum.py for the arithmetic itself; $PYTHON overrides the interpreter it uses
OUT=$SCRATCH/q130i TILES_DIR=$TILES bash docs/reports/data/2026-10-31-q130-zeros-transport/sim/run.sh
cd docs/reports/data/2026-10-31-q130-zeros-transport
python3 -I reprice.py --q129 ../2026-10-27-q129-ledger-scope --counts sim/counts.txt \
    --out zeros-transport.json
```

Verilator here is the conda-forge build `rtl-sim/fma_toggle/README.md` § "On a Mac" installs
(5.052); its generated makefile names a cross compiler it does not ship, so `run.sh` overrides
`CXX`/`LINK`, exactly as that `Makefile` does. **It does not implement `shortreal`** — it promotes
it to `real` and its bit-cast functions then do not round-trip, which is why no SystemVerilog file
here contains floating point (§ Corrections, defect 2). Anything in this project that prices
floating-point data under Verilator should check for the same thing. The structural simulation is version-insensitive in
the way the RTL toggle counts are not: it counts nodes of a tree this directory writes out itself,
not names the optimiser happens to keep.
