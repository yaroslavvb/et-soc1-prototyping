# Q132(b): the RTL bench returns correct multiply-adds, and what each kind of number switches

*Sun 1 Nov 2026 (week 44). Desk compute on the mini: Verilator 5.052 from Homebrew, Apple clang, core-et `b38a1a31`
([`versions.txt`](versions.txt)). **No card was opened and nothing was measured in watts here**: every watt below comes from a committed
experiment, named where it is used. The bench is [`rtl-sim/fma_toggle_v2/`](../../../../rtl-sim/fma_toggle_v2/). The two old benches are
untouched, as the record. This closes item 7 of section 11 of the kinds page, and narrows items 2, 6 and 12 (§7). Corrected after verification the same day: [Corrections](#corrections-after-verification).*

## Results

**1. The fault was the simulator, not the stimulus.** Verilator 5.052's data-flow-graph optimiser miscompiles `casez` blocks with a wildcard arm
and part-select targets. One of them is the mux in front of the alignment shifter (`txfma_f3.v:160-170`). With the pass on, the shifter's input
reads 0, so a multiply-add returns only its larger operand: c alone, or a·b alone when c = 0, the pattern Q130(b) §0 row 1 reported. **`-fno-dfg`
fixes it.** A small file, 25 lines of code with no RTL of this project, reproduces it, `al=0000` against `al=4000`
([`verilator_dfg_reproducer.sv`](../../../../rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv)). The two old benches, with that one flag added and
nothing else changed, compute fp32 and fp16 right on ungated data ([`old-benches/fcheck-with-and-without-flag.json`](old-benches/fcheck-with-and-without-flag.json)):
A = B = 1, C0 = 5 goes from C = 5 and 37 to the correct 37 and 69. The operand-staging guess is ruled out directly: `use_prev_sigs` on or off makes no
difference, wrong both ways with the pass on and right both ways with it off ([`old-benches/use-prev-sigs.txt`](old-benches/use-prev-sigs.txt)).

The old benches had real faults of their own too, on gated kinds and in int8, and the new bench drops them by not doing those jobs (§2).

**2. The new bench is core-et's `vpu_top`, whole.** The micro-op stream, the zero gate, `use_prev_sigs`, the clock gates, the register files and the
write-back are the RTL's own. **What remains testbench code:** the scratchpad (an array that answers two cycles later and never refuses), the core (one
start pulse and a control word), and back doors that load and read C. It reproduces the card with nothing tuned: **538 and 310 cycles start to start,
where E78 measures 546.001 and 318.000**, the same 8 cycles either way, which fits the core's loop ([`fsm-natural-period.txt`](fsm-natural-period.txt)); 512 micro-ops of 8 lanes against 256 of 16 slots.

**3. The functional check passes** ([`fcheck/`](fcheck/), rerun with `make check`, about 1.5 minutes).

| check | fp32 | fp16 | int8 |
|---|---:|---:|---:|
| one `txfma_top`, random and corner operands (zeros, denormals, infinities, NaNs, near-cancelling sums) | **40,000 of 40,000 exact** | **39,701 of 40,000** on the unit's own window; residue 299, named below | |
| whole TensorFMA ops: words of C exact, 22, 22 and 19 cases (launch, all-MADD, gated, corners), 2–4 ops | **22,016 of 22,016** | **22,016 of 22,016** | **18,944 of 18,944** |
| A = B = 1, C0 = 5, two all-MADD ops (the old probe) | 37 | 69 | 133 |
| valid column slots against the gate rule, 63 cases | all equal | all equal | all equal |
| all 51 kinds at 3 points of a launch: 39,168 words of C against software | 0 mismatched | 0 mismatched | 0 mismatched |
| all 51 kinds: the RTL's valid slots against `kinds.json`'s `gated_lane_frac` | equal | equal | equal |

fp16 is not exact arithmetic, and that is the unit, not the bench: it keeps 25 bits below the largest of its three terms and one's-complements a negative
sum that lost bits, so only 33,793 of those 40,000 vectors equal the exact sum rounded toward zero. [`fp16_model.py`](../../../../rtl-sim/fma_toggle_v2/fp16_model.py)
computes that window, read off `txfma_f3.v`, `txfma_c2.v`, `txfma_f4.v` and `txfma_f5.v`. **The residue is sums that cancel to within one unit of the window,**
where the leading-one logic has nothing to normalise. The vectors are built to hit it, and it is 0 of 22,016 words in whole ops.

**What this check covers, and what it does not.** It compares C at the end of an op, so it tests arithmetic, order and the gate. **A pass does not validate the toggle counts:** wrong latency, bypass or clock gating that leaves the arithmetic right would pass it. Separate evidence for the timing is 538 and 310 cycles against the card's 546 and 318, registers identical at -O0 (which rules out optimiser races only), and the flip's 1,946; nothing ties cycle-level toggles to silicon except the fit, and a fit can absorb systematic error.
- **The 40,000:** in fp32, 26,494 are random vectors and 13,506 are built to align or cancel.
- **The 39,168 words:** 6,912 belong to the 9 kinds with no valid slot, where C stays 0. That leaves 32,256 with content, and 10,752 of those are fp16's.
- **fp16's reference is a model read off the same RTL,** so those words cannot catch a fault in the RTL's own arithmetic or a difference from silicon. They can catch a simulator fault. fp32's reference is exact rational arithmetic, independent except for the flush rules read from the RTL. Order and gate come from the RTL in every format.
- **int8's figure does not test this fix:** with the pass on, in the verifier's control, one unit reads fp32 2,324 and fp16 1,795 of 4,000 exact, whole ops 6,048 and 5,828 of 7,680 words wrong, and int8 0 of 6,656 wrong.
- **No card has checked C:** `runs.jsonl` reads `"result": "unchecked"` on every record.

**4. The counts.** All 51 kinds, per multiply-add (table in §8; [`counts-v2.json`](counts-v2.json) `rows.<type>.<kind>.mean`):

| random data, per multiply-add | fp32 `randn` | fp16 `randn` | int8 `full` |
|---|---:|---:|---:|
| merged nets toggled in the unit, the recount's method (`nets_hier`) | **1,431** | **581** | **35.6** |
| the same, its merge learned once on random data (`nets_map`, §4) | 1,816 | 747 | 35.6 |
| the whole VPU (`nets_map`) | 1,931 | 805 | 45.4 |
| register bits clocked, whole VPU | **1,932** | 965 | 47 |
| register bits that change | 429 | 188 | 7.7 |

**Quote about 1,800 merged nets, a floor, for a random fp32 multiply-add in the unit;** an open netlist counts 3,299 wires. The two merges are not an uncertainty band: the map's merges are a subset of each run's, so it reads at or above `nets_hier` on all 51 kinds by construction, and 1,431 stays only as the like-for-like correction of "about 1,300".

Per op, fp32 switches 1.20× what fp16 does (whole VPU, `nets_map`), with exactly the same bits clocked; per multiply-add that is 2.4×, because fp16 does twice as many. int8
is still **not comparable**: its multiply, product sum and add are behavioural RTL, so no nets inside them exist to count.

**5. Beside E78: two terms predict it. This model is M2;** §11 adds M4, which separates the operand bus, and the two READMEs must not quote "the constants" without naming one. D = rate × (k × merged-net toggles + a × clocked register bits), each over the type's zeros. Fitted on E78's fp32 and fp16 kinds:
**k = 1.871 ± 0.021 fJ, a = 1.092 ± 0.014 fJ, rms 0.357 W, r = 0.9994, ρ = 0.991** over 33 kinds; **leave-one-out rms 0.375 W**. Either term alone fails (nets 3.64 W, clocks 4.85 W).
**Out of sample, with those two numbers frozen:**

| set | what it is | n | rms (W) | r | measured / predicted |
|---|---|---:|---:|---:|---:|
| fp32 → fp16, fp16 → fp32 | fitted on one format, applied to the other | 16, 17 | 0.376, 0.452 | 0.9996, 0.9994 | |
| E86 | GPT-2 tiles, aifoundry3 | 6 | 0.193 | 0.9988 | |
| E90 | signs and re-drawn tiles, aifoundry3 | 16 | 0.482 | 0.9985 | |
| E82, E88 | aifoundry1 card 1, with one card scale (0.971) fitted on E82 | 33, 14 | 0.361, 0.452 | 0.9993, 0.9991 | |
| **E65** | **one B bit at a time, all 32 positions** | **32** | **0.128** | 0.9953 | 1.020 |
| E79 | fp16 B bits, all 16 | 16 | 0.132 | 0.9952 | 1.002 |
| E70 | 2–23 bits at once, low or spread | 16 | 0.281, 0.172 | 0.999 | 1.021, 0.980 |
| E67 | one A bit at a time, all 32 | 32 | 0.264 | 0.9909 | 0.842 |
| E92 | **its 32 tiles, frozen before its data: see 6** | 32 | 0.603 | 0.9944 | |

The set's own hardest contrasts come out too: **E65's bit 22, 4.63 W measured, 4.63 W predicted (the closest of the 32; the rms over them is the 0.128 W above); E79's balanced layout of that bit, 0.669 W measured, 0.686 W predicted**, the 7×
"all-in price" explained with no new parameter; E70's spread minus low at 8 bits, 3.86 W measured, 4.05 W predicted; E67's two-flip grid, 62–96% of the sum on the card, 64–100% in the bench. Compare
E78's frozen models: Q130(c) rms 2.27, 1.76 W; Q130(b) r2 1.83, 1.41–1.87 W ([`scored.json`](../2026-10-31-e78-kinds-energy-matrix/scored.json) `rules.E78-R2`). That comparison flatters this fit, which came after E78's data; the out-of-sample rows are the fair ones.

int8 fails across formats (rms 2.2 W, the float coefficients under-predict by 1.8 W) because its arithmetic has no nets; by itself it fits k = 3.74, a = 2.13 fJ, rms 0.287 W, leave-one-out 0.331 W.

**6. The sign question, as a prediction.** The bench's count for E92's frozen tiles went up in **`de545f0c` at 00:43:14 PDT** ([`e92-bench-prediction-frozen.json`](e92-bench-prediction-frozen.json) is that file, byte for byte): during E92's card session (00:17–00:55 PDT), before its first data commit (`4e8eb836`, 01:06:51 PDT), and with none of its data read by this lane. A later variant (`nets_map`, `e7cb1f21`, 01:10:16 PDT) was computed before I read E92's data but after it was on main, so by the clock it is post hoc.

| E92 contrast, paired per pass ([`e92-prediction-scored.json`](e92-prediction-scored.json)) | measured (W, 95%) | **frozen prediction** | post hoc variant | the recount's merge |
|---|---:|---:|---:|---:|
| fp32 `h_sub` − `h_add`: the adder alternates, same operands, sums held still | 4.42 ± 0.44 | **3.22** | 4.72 | 0.33 |
| fp16 `h_sub` − `h_add` | 6.86 ± 0.40 | **6.44** | 7.19 | 2.25 |
| fp16 over fp32, that contrast (per-pass ratios) | 1.55 ± 0.25 | **2.00** | 1.52 | 6.82 |
| fp32 `c_alt` − `c_abs`: alternates, no operand sign moves | 5.08 ± 0.45 | **3.85** | 5.78 | 1.11 |
| fp32 `h_allsub` − `h_add`: a steady subtract | 0.04 ± 0.35 | **0.12** | 0.05 | 0.21 |
| fp32 `c_neg` − `c_abs` | 0.02 ± 0.06 | **0.02** | 0.02 | 0.00 |
| fp16 `h_allsub` − `h_add` | 0.19 ± 0.32 | **0.21** | 0.09 | 0.09 |
| fp32 `s_abs` − `c_abs`: random signs, frozen sum | 2.38 ± 0.56 | **2.00** | 2.93 | 0.34 |
| fp32 `r_h_sub` − `r_h_add`: alternates, sums held still, random magnitudes | 4.38 ± 0.64 | **3.22** | 4.72 | 0.33 |
| fp32 `w_h_sub` − `w_h_add`: alternates, sums moving, magnitude 1 | 2.79 ± 0.36 | **2.46** | 2.54 | 1.18 |
| fp32 `wr_h_sub` − `wr_h_add`: alternates, sums moving, random magnitudes | 0.41 ± 3.19; 1.11 ± 0.18 with E92's dips removed | **0.93** | 0.52 | 1.28 |
| 32 tiles, rms, r | | **0.603 W, 0.9944** | 0.434 W, 0.9982 | 2.184 W, 0.9269 |

The frozen count said the alternation is dear, a steady subtract nearly free, and the premium smaller as the sums move. All three held. It was 27% low on fp32's alternation, and its 2.00 for fp16 over fp32 lies outside the card's 1.55 ± 0.25. E92's own rule on the alternation's size, E92-R2, reads INCONCLUSIVE in its primary arm ([`scored.json`](../2026-11-01-e92-sign-split/scored.json) `rules`), so this is agreement with measured numbers and not a verdict on that rule.

**How many adder toggles alternating causes, as frozen:** in fp32, **+1,364,416 merged-net toggles an op in the adder and normaliser, 355 per alternation** (3,840 an op), 89% of the unit's change, with +435,871 register bits changed; a steady subtract, +12,933. In fp16, **+1,792,069, 233 per alternation** of one of its two products (7,680 an op), 60% of the unit's change; a steady subtract, +9,741 ([`e92-bench-prediction-frozen.json`](e92-bench-prediction-frozen.json) `variants.nets_hier2.contrasts_w[].d_unit_hier2_by_stage_per_op`). The post hoc map reads +2,218,107 (578, 98%), +2,317,896 (302, 72%), and +16,741, +12,147 for a steady subtract ([`e92-bench-prediction.json`](e92-bench-prediction.json) `variants.nets_map`). As energy, in fp32 with sums held still: E92 1,028 fJ an alternation (its [`posthoc-check.txt`](../2026-11-01-e92-sign-split/posthoc-check.txt) B), the frozen count 749 fJ, the post hoc count 1,098 fJ, each for the whole contrast.

**What this shows and what it does not.** These are simulated net toggles. They place the premium in the RTL's adder and normaliser; E92 measures its size on one card, not its place. The reading of why is the public RTL's: an effective subtract inverts the 52-bit aligned operand on its way into the adder (`txfma_c2.v:303`, `txfma_f3.v`), so each change of operation flips that bus and what it feeds, even with the sum held still. With random magnitudes and moving sums the adder is busy anyway, and the premium falls to about a quarter: 0.93 of 3.22 W in the frozen count, 1.11 of 4.40 W on the card with E92's dips removed (its primary arm cannot resolve it, 0.41 ± 3.19 W). So the alternation is not the whole of a random sign's cost.

The recount's merge misses the alternation by 13×, and that is a finding about the merge (§4), not about the adder.

**Corrected Sun 1 Nov 2026, after `e57e65a3`.** (1) E65's prices now use only the passes E65's own reduction kept; the first version also averaged in 654 and 656, which E65 set aside, and so read bit 22 as 4.65 W where E65 says 4.63 W. k and a do not move, and E65's rms stays 0.128 W. (2) `e7cb1f21` had rewritten `e92-bench-prediction.json` and dropped the frozen stage split, which broke E92's `posthoc-check.py`, as an independent check of E92 found. The field is back, the frozen file is committed beside it, and that script now reproduces its committed output to the byte. Every predicted watt is unchanged. (3) Result 6 now leads with the count as frozen, adds the fp16-over-fp32 and moving-sum rows, and no longer says the cost "is in the adder" as if that had been measured. (4) The blog lines in §7 are narrowed to what each file shows.

## 1. Why the old benches failed, and how that was found

One lane with 1.5 × 2.5 + 1, 2 × 3 + 1 and 1 × 1 + 5 returned 3.75, 6 and 5: the larger operand alone. Tracing the stages, the exponents, the operand order and the aligner's control were all right, and the aligner's input was 0 while the mux selecting it had valid inputs.
`-O0` made it right; `-fno-*` one pass at a time found `-fno-dfg`, and no other pass mattered. The fault needs the `casez` wildcard: the same block as `case … default`, or as if/else, comes out right ([`verilator_dfg_reproducer.sv`](../../../../rtl-sim/fma_toggle_v2/verilator_dfg_reproducer.sv)).

The recount's own table had the clue: `txfma_align_shf`, zero toggles in every VCD column. MUL ops were always right because they do not use that shifter's input, and the recount's C = 0 points are unchanged by the flag (1,192.0 and 1,197.1 against 1,192.1 and 1,197.7, `old-benches/recount-nodfg.json` `randn.points`).

## 2. What else was wrong in the old benches

With the flag on, the old benches are right on ungated data. These faults remain in them, and none is in the new bench, because the RTL now does these jobs.

| fault | effect | evidence |
|---|---|---|
| `uop_prev` on after any valid (`fma_toggle/tb.sv:94`). The RTL needs a prior micro-op with **all eight lanes valid** (`vpu_ctrl.v:849-861`). | A lane whose first MADD micro-op was gated keeps the MUL control word (`txfma_c0.v:222`) and returns a·b: 423 of 925 results in `sparse50`. | [`old-benches/fcheck-gated-kinds-with-flag.json`](old-benches/fcheck-gated-kinds-with-flag.json) |
| int8's C from the EX-stage word | `tima_top.v:111` adds C in F3, two cycles after a and b. Still C = 161 and 165 with the flag. | [`old-benches/fcheck-with-and-without-flag.json`](old-benches/fcheck-with-and-without-flag.json) |
| a first op entirely MUL | the RTL multiplies only in a launch's first A column (`vpu_tensorfma.v:726`) | |

## 3. What changes, and what does not

| earlier figure | now | source |
|---|---|---|
| **1,946** RTL signal bits for one flip (chip diagram `tfma.flip.stages`: a = π, b bit 11, c = 100) | **Unchanged, to the bit: 1,946**, with the fact's results `42cfc1cc`, `42cfc230`. The faulty build gives 1,295 and returns c alone. That research's simulation was not built with this fault. | [`old-benches/flip-nodfg.json`](old-benches/flip-nodfg.json), `flip-dfg.json` |
| **"about 1,300 physical nets"** per random multiply-add | **1,429**, the recount's own bench, tiles and method with only the flag changed (+9.8%); 1,431 on the new bench over a launch. Still a floor: the merge is learned on each window, and learned over twelve tiles it gives 1,816. | `old-benches/recount-nodfg.json` `randn.mean.nets_hier` ÷ 4,096; `counts-v2.json` |
| **602.5** register bits clocked | The fix does not move that subset: the recount's window reads 595.2 with and without the flag, and 602.5 is the same subset over the 519-cycle window of `toggles-5052.json`. It was only ever the 838 bits the old counter could see. **The whole unit is now measured: 1,739.8 load per multiply-add**, on every ungated kind alike, which is the numerator of the chip diagram's "1,739 of 2,071". (`present` reads 2,052.8 here, not 2,071, because a register reports only on an edge of its own gated clock.) 1,932 across the VPU. | `counts-v2.json` `fp32.randn.mean.ff.txfma.clocked` ÷ 4,096; `old-benches/recount-nodfg.json` and the recount's `recount.json`, `randn.mean.ff_clocked` ÷ 4,096 |
| §5.1's first version: "the tree stays level, the stages after it toggle **three times as much** for bit 22 as for bit 0" (the page's verifier dropped it) | Bit 22 against bit 4: **the adder, normaliser and result path 383 against 19 net toggles a multiply-add, 20×; the multiplier 52.5 against 24.5, 2.1×.** So the tree does not stay quite level and the rest moves far more than 3×. Table in §8. | [`counts-hl.json`](counts-hl.json), `analysis.json` `other_experiments.vpu_map.ladder.e65_bit` |
| Q130(b) r2's 1,557 / 648 / 33.6 per MAC | 1,431 / 581 / 35.6 by the same merge; 2.5× fp32 over fp16 where r2 had 2.4×. int8 stays not comparable. | `counts-v2.json` |
| r2's k of 2.486 fJ, "fitted to a count from a datapath that computes the wrong sum" | 1.871 fJ, with a second term, a = 1.092 fJ per clocked bit. Both are fitting constants, not energies per wire (§6). | `analysis.json` `coef_spread.vpu_map` |
| "the replay, with its broken MADD, cannot say how much of the 8.73 W [all-ones over zeros] costs" | **Almost none of it is data.** All-ones fp32 toggles 24 merged nets a multiply-add against random's 1,931 and clocks the same 1,932 bits: 8.41 W of clocking and 0.08 W of nets, against 8.26 W measured. | `analysis.json` `split.fp32.ones` |
| §0 row 5: the gate's 51-of-51 "two codings of one reading" | Now the RTL's own gate, read from its own valid wires: 51 of 51 equal `kinds.json`. The (l, l+8) pairing and 256 micro-ops of int8 are no longer reconstructed. | `counts-v2.json` `valid_slots` |

**Random data's watts, by the fit** (not a measurement; §8 has all four rows):

| | D measured | register clocking | data nets: multiplier | adder and normaliser | result path | operand bus | exponent, control, sequencer |
|---|---:|---:|---:|---:|---:|---:|---:|
| fp32 `randn` | 24.72 | **8.41** | **7.57** | **4.90** | 0.69 | 1.55 | 1.87 |
| fp16 `randn` | 22.16 | **8.40** | **5.01** | **4.45** | 0.71 | 1.53 | 2.11 |

E88 measured a split of a different stream on another card; the same coefficients and E82's card scale put it at: lane clocked 8.23 W against its 7.92; operand side 9.16 against 8.61; result path 4.85 against 5.04 (fp32); 8.18, 6.56, 5.84 against 7.96, 6.19, 6.29 (fp16) (`analysis.json` `card_scale.vpu_map.e88_pred`).

## 4. Two merges, and why this file's map exists

**The recount's `nets_hier` is reported everywhere, and it cannot be used on a regular stream.** It merges two names with one waveform when one scope is an ancestor of the other, with no bit-position term, learned on each run's own window. A single control bit in a parent scope that flips with a whole bus therefore covers the entire bus. That is precisely what an add/subtract flag does to a 52-bit aligned operand, so on `h_sub` it reports 200,000 net toggles an op against 570,000 register bits that change, which is impossible. The recount's README called this merge "safe on any stimulus"; it is not.

**`nets_map`** ([`train_maps.py`](../../../../rtl-sim/fma_toggle_v2/train_maps.py), `settle_count --train`) applies the same rule once, over 18 tiles of random and gated data in all three formats, and keeps that one list of nets for every run, so a stream cannot merge what it fails to separate. `nets_hier2` is a third, cheaper repair. On E78: rms 0.357 (map), 0.283 (hier2), 0.431 W (hier). On E65's single bits: 0.128 (map, measured/predicted 1.020), 0.303 (hier2, 1.142), 1.118 W (hier, 2.300). **I chose the map as primary after seeing those ladder fits**, so its advantage on them is not independent evidence; E92 is the only blind test, and hier2 is what was frozen for it.

**Stage attribution** credits each merged net to the earliest stage among the names it carries, because a stage drives the next. Stages are read from the scope: f0 and the lane's buses are the operand bus; f1 and f2 the multiplier; f3, f4 and f5 the adder and normaliser; f6 and the C register file the result path.

## 5. Registers and clocks

`macros_acct.vh` instruments the `FF` macro family, the "one line and the obvious next pass" the recount named, so every register in the VPU now reports. Per multiply-add in fp32, on a lane the gate leaves on: 1,739.8 of the unit's bits load and 192.5 more in the rest of the VPU, whatever the numbers; for zeros, 7.3 of the unit's. Of those 1,932, only the data-dependent 429 change. **A lane that is on costs about a third of random fp32's switching power whether or not its numbers change**, and that is what E88 called "the lane clocked".

int8 zeros' extra 0.61 W is not explained here. The RTL clocks fewer bits a second in int8 zeros than in fp32 zeros (0.76 against 1.17 × 10¹⁵), so the VPU's registers point the wrong way. The scratchpad's read rate points the right way, 4.3 against 3.2 × 10¹¹ a second (224 reads an op at 1.72× the rate, against 288), but the dcache is not in this bench, so that is a candidate and nothing more (`counts-v2.json` `scp_reads`, `ff`).

## 6. What this cannot say

- **RTL, not silicon, and not a netlist.** core-et is the Erbium branch, a later revision of the same lineage. Zero delay, so no glitches: k absorbs them.
- **fp16's reference is a model read off the same RTL,** so that check shows the bench runs the RTL's window arithmetic consistently, not that silicon does the same. fp32's reference is exact arithmetic, independent of the RTL. No card has had C read back for these vectors; a short card run on near-cancelling fp16 sums would test the window.
- **k and a are fitting constants at 600 MHz and 522 mV.** A merged net is a floor on wires (the open netlist counts 3,299 switching nets where this counts 1,816), so 1.87 fJ is not the energy of a wire. Leakage arms move them to 1.92, 1.12 and 1.83, 1.07 fJ.
- **The scratchpad, the dcache and the core are not modelled**, and it shows: the fit under-predicts every kind whose operands move on gated lanes, by 0.17–0.65 W (`sparse50`, `wsparse50`, one operand all zero). That is the term most clearly missing.
- **On the A side the prediction runs high by 15–20%** (E67 measured / predicted 0.842; E70's A ladder 0.802), and **on high-toggle bit ladders with a busy partner too** (E60 `lb`, 0.871). The B side does not. Unexplained.
- **int8's multiply is one line of behavioural RTL**, so its k and a are not comparable with the float ones. A gate-level count of `tima_top` would be.
- **Counts carry some of the tool.** With every Verilator optimisation off, registers are identical. `nets_hier` moves +3.2% (fp32 `randn`, VPU) and +5.8% (fp16), but that is the merge §4 says cannot be used on a regular stream. **`nets_hier2` moves +34.8% and +31.8%, and +48.8% on `fp32.ones`** ([`optimiser-sensitivity/`](optimiser-sensitivity/)). **`nets_map`, its merge learned again on the -O0 binary, moves +3.5% and +5.2%** (`counts-O0-map.json`), multiplier +2–3%, adder and normaliser +7–10%, lane bus unchanged, so the primary count is much steadier than hier2. No constant has been refitted at -O0, and "1.6 fJ" still means "at this build". int8's unit moves +35%, on small numbers.
- **The fit came after E78's data, and the choice of merge after E65's** (§4). E92 is the only blind test. The frozen variant under-predicted fp32's alternation by 27%, put fp16 over fp32 at 2.00 where the card says 1.55 ± 0.25, and had the right order and the right near-zeros.

## 7. Section 11, and what a reader can be told

- **Item 7 closes as worded:** the multiply-add now returns right values, and fp32 and fp16 counts exist. int8's counts below the multiply-add remain not comparable.
- **Item 6 narrows; it does not close.** The wording is in [E103's README](../2026-11-01-e103-model-blind-test/README.md).
- **Item 2 narrows,** with E92: the count of adder toggles is in Result 6. The frozen count ran 27% low on fp32's alternation, the post hoc one 7% high. Where the power goes on silicon stays unmeasured.
- **Item 12:** E79's list and its layout probe are predicted; int8 zeros' 0.61 W and zeros' transport are §14.

**For the blog, each from a committed file:**

- One optimisation pass of Verilator 5.052 miscompiled the bench, and a one-line flag fixes it; a small file with no project RTL shows it (`verilator_dfg_reproducer.sv`).
- In fp32 the simulated unit matches exact arithmetic on 40,000 random and corner cases. fp16 matches a model of its window read off the same RTL. No card has read C back (`fcheck/`).
- A random 32-bit float multiply-add flips about 1,800 merged nets in the multiply-add unit, a floor; an open netlist counts 3,299 wires (`counts-v2.json`).
- Multiplying the same number over and over flips almost nothing and still draws a third of what random data draws over an all-zero matmul. By the fit, that third is a working lane's registers being clocked anyway (`analysis.json` `split`).
- Fitted constants turn those counts into watts. On single B-side bit flips they did not see they read 0.13–0.30 W rms, depending on the model and the merge, and 0.24–0.30 W with a flip on the A side (`corrections-check.txt` D, `analysis.json`, E103's `score_all.json`).
- In the simulation, a high mantissa bit switches twenty times as much after the multiplier as a low bit does, and only twice as much inside it (`counts-hl.json`).
- Hold the running sum still and fix the numbers: making the adder alternate between adding and subtracting costs one card 4.4 W in fp32 at 600 MHz, and a simulation frozen before that data was read said 3.2 W and put 89% of the extra net toggles in the adder and normaliser (E92 `scored.json`, `e92-bench-prediction-frozen.json`).
- Subtracting steadily, with the sum frozen, costs nothing measurable: 0.04 ± 0.35 W (E92 `scored.json`).
- The public RTL suggests why: an effective subtract inverts a 52-bit bus on its way into the adder (`txfma_c2.v:303`, a reading). With random magnitudes and moving sums the premium is about a quarter as large (E92's dips-removed reading), so it is not the whole of a random sign's cost.

**Any of this, on the RTL's later revision (Erbium), not the ET-SoC-1's own.** A post may not say that the check validates toggle counts, that silicon does the fp16 window, that 1,400–1,800 is a range, or fJ per wire.

**Next:** report the optimiser fault to Verilator, a decision for the owner, since it would go out in his name; a gate-level count of `tima_top`; the dcache's read bus in scope.

## 8. The tables

Generated by [`make_tables.py`](make_tables.py) from [`analysis.json`](analysis.json), written by [`analyze.py`](analyze.py).

### All 51 kinds

Per multiply-add for the counts, watts over the type's own zeros for D. `fit` is the plain two-term fit (fp32 and fp16 pooled; int8 by itself), so `fit − D` is in-sample.
nets = merged-net toggles of the whole VPU (`nets_map`); unit = the multiply-add unit alone, the first by this file's map, the second by the recount's per-run merge; clocked = register bits clocked; changed = register bits that change.

| kind | D (W) | fit − D | nets | unit (map) | unit (recount) | clocked | changed | slots valid of 4,096 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| fp32.randn_small | 24.76 | +0.28 | 1,950.6 | 1,833.1 | 1,451.0 | 1,932.3 | 436.0 | 4,096 |
| fp32.randn | 24.72 | +0.15 | 1,930.7 | 1,816.1 | 1,431.4 | 1,932.3 | 428.8 | 4,096 |
| fp32.randn_large | 24.71 | +0.14 | 1,927.3 | 1,812.3 | 1,432.6 | 1,932.3 | 426.6 | 4,096 |
| fp32.randn_sorted | 23.38 | +0.47 | 1,811.7 | 1,703.6 | 1,354.1 | 1,932.3 | 407.7 | 4,096 |
| fp32.uniform01 | 22.65 | +0.84 | 1,768.4 | 1,664.1 | 1,237.3 | 1,932.3 | 364.5 | 4,096 |
| fp32.fp16grid | 19.62 | +0.07 | 1,327.6 | 1,232.5 | 944.3 | 1,932.3 | 340.1 | 4,096 |
| fp32.bf16trunc | 18.14 | -0.14 | 1,129.8 | 1,039.2 | 779.3 | 1,932.3 | 308.2 | 4,096 |
| fp32.smallint | 14.08 | -0.43 | 743.0 | 662.3 | 461.1 | 1,728.5 | 227.3 | 3,614 |
| fp32.pow2 | 13.98 | -0.38 | 617.8 | 535.2 | 344.4 | 1,932.3 | 213.9 | 4,096 |
| fp32.nn_like | 13.04 | -0.42 | 1,016.4 | 918.6 | 731.2 | 1,052.8 | 223.9 | 2,016 |
| fp32.pi | 8.47 | +0.04 | 25.4 | 5.3 | 4.2 | 1,932.3 | 13.4 | 4,096 |
| fp32.ones | 8.26 | +0.24 | 23.9 | 5.1 | 4.0 | 1,932.3 | 12.8 | 4,096 |
| fp32.neg_ones | 8.14 | +0.36 | 23.9 | 5.1 | 4.0 | 1,932.3 | 12.8 | 4,096 |
| fp32.sparse50 | 7.30 | -0.56 | 538.4 | 452.8 | 367.5 | 701.0 | 115.2 | 925 |
| fp32.a_zeros_b_randn | 0.81 | -0.50 | 50.3 | 14.1 | 14.1 | 254.4 | 8.4 | 0 |
| fp32.a_randn_b_zeros | 0.62 | -0.33 | 47.3 | 7.2 | 7.2 | 254.4 | 8.4 | 0 |
| fp32.sparse90 | 0.58 | -0.17 | 52.1 | 24.1 | 12.9 | 270.8 | 12.8 | 34 |
| fp32.zeros | 0.00 | +0.00 | 14.2 | 0.0 | 0.0 | 254.4 | 8.4 | 0 |
| fp16.randn_small | 22.21 | -0.08 | 806.2 | 747.2 | 597.4 | 965.3 | 189.2 | 4,096 |
| fp16.randn | 22.16 | -0.06 | 804.5 | 746.5 | 580.6 | 965.2 | 188.1 | 4,096 |
| fp16.randn_sorted | 20.75 | +0.24 | 739.4 | 686.3 | 537.7 | 965.2 | 173.9 | 4,096 |
| fp16.pair_half_zero | 20.12 | -0.43 | 664.1 | 609.7 | 488.4 | 965.2 | 173.6 | 4,096 |
| fp16.uniform01 | 19.43 | +0.13 | 656.4 | 604.9 | 438.8 | 965.2 | 149.7 | 4,096 |
| fp16.fp8grid | 18.05 | -0.15 | 560.1 | 512.6 | 386.7 | 965.2 | 148.6 | 4,096 |
| fp16.nn_like | 17.60 | -0.44 | 615.8 | 561.4 | 450.5 | 796.3 | 150.6 | 3,296 |
| fp16.smallint | 17.00 | -0.35 | 489.0 | 443.9 | 329.5 | 962.0 | 136.6 | 4,080 |
| fp16.sparse50 | 13.20 | -0.40 | 471.9 | 421.5 | 345.8 | 607.0 | 118.4 | 2,399 |
| fp16.ones | 8.45 | +0.04 | 11.9 | 2.6 | 2.1 | 965.2 | 6.4 | 4,096 |
| fp16.neg_ones | 8.38 | +0.11 | 11.9 | 2.6 | 2.1 | 965.2 | 6.4 | 4,096 |
| fp16.wsparse50 | 7.06 | -0.65 | 241.6 | 199.9 | 160.2 | 364.3 | 54.2 | 983 |
| fp16.sparse90 | 1.41 | -0.31 | 48.9 | 31.0 | 23.6 | 165.8 | 11.7 | 160 |
| fp16.a_zeros_b_randn | 0.78 | -0.47 | 25.2 | 7.1 | 7.1 | 127.2 | 4.2 | 0 |
| fp16.wsparse90 | 0.74 | -0.29 | 27.8 | 12.0 | 7.6 | 136.8 | 6.5 | 40 |
| fp16.a_randn_b_zeros | 0.66 | -0.38 | 23.4 | 3.5 | 3.5 | 127.2 | 4.2 | 0 |
| fp16.zeros | 0.00 | +0.00 | 7.1 | 0.0 | 0.0 | 127.2 | 4.2 | 0 |
| int8.full | 7.06 | -0.32 | 45.4 | 35.6 | 35.6 | 46.9 | 7.7 | 4,096 |
| int8.gauss_q | 6.60 | +0.06 | 44.7 | 35.6 | 35.6 | 46.9 | 7.8 | 4,096 |
| int8.sorted | 6.59 | -0.45 | 40.3 | 31.5 | 31.5 | 46.9 | 6.5 | 4,096 |
| int8.pos | 6.17 | -0.45 | 36.7 | 27.7 | 27.7 | 46.9 | 6.2 | 4,096 |
| int8.smallint | 6.00 | +0.58 | 44.0 | 35.3 | 35.3 | 46.9 | 7.8 | 4,096 |
| int8.sparse50 | 5.46 | -0.11 | 34.5 | 26.8 | 26.8 | 45.3 | 6.3 | 3,808 |
| int8.ternary | 5.19 | +0.57 | 37.1 | 29.9 | 29.9 | 46.7 | 6.8 | 4,064 |
| int8.highbit | 3.23 | -0.03 | 15.4 | 12.9 | 12.9 | 46.9 | 2.3 | 4,096 |
| int8.wsparse50 | 3.14 | +0.07 | 23.8 | 16.7 | 16.7 | 32.2 | 3.2 | 1,460 |
| int8.neg_ones | 1.63 | +0.04 | 2.3 | 0.1 | 0.1 | 46.9 | 0.6 | 4,096 |
| int8.ones | 1.56 | +0.06 | 1.9 | 0.1 | 0.1 | 46.9 | 0.6 | 4,096 |
| int8.sparse90 | 1.14 | +0.11 | 9.5 | 6.6 | 6.6 | 28.2 | 1.3 | 730 |
| int8.wsparse90 | 0.54 | +0.04 | 5.8 | 2.9 | 2.9 | 24.6 | 0.7 | 82 |
| int8.a_full_b_zeros | 0.50 | +0.17 | 6.8 | 0.2 | 0.2 | 24.1 | 0.5 | 0 |
| int8.a_zeros_b_full | 0.31 | -0.05 | 3.3 | 0.4 | 0.4 | 24.1 | 0.5 | 0 |
| int8.zeros | 0.00 | +0.00 | 1.2 | 0.0 | 0.0 | 24.1 | 0.5 | 0 |

### The fits on E78

| scope | counted as | rms (W) | leave-one-out rms (W) | r | ρ | worst (W) | k (fJ per net toggle) | a (fJ per clocked bit) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fp32 | vpu_map | 0.366 | 0.403 | 0.9993 | 0.990 | 0.68 | 1.854 | 1.089 |
| fp32 | unit_map | 0.511 | 0.557 | 0.9988 | 0.990 | 0.98 | 1.948 | 1.107 |
| fp32 | vpu_hier | 0.482 | 0.552 | 0.9987 | 0.988 | 0.97 | 2.326 | 1.124 |
| fp32 | unit_hier | 0.638 | 0.727 | 0.9977 | 0.988 | 1.26 | 2.448 | 1.149 |
| fp32 | vpu_hier2 | 0.282 | 0.309 | 0.9996 | 0.993 | 0.47 | 1.834 | 1.079 |
| fp32 | vpu_map_only | 3.994 | 4.045 | 0.9484 | 0.880 | 8.32 | 2.96 | None |
| fp32 | clk_only | 5.524 | 6.001 | 0.7658 | 0.586 | 9.87 | None | 2.338 |
| fp32 | ff_toggles_clk | 0.873 | 0.973 | 0.9954 | 0.988 | 1.68 | 8.626 | 0.977 |
| fp16 | vpu_map | 0.303 | 0.322 | 0.9997 | 0.997 | 0.59 | 1.909 | 1.084 |
| fp16 | unit_map | 0.436 | 0.458 | 0.9994 | 0.997 | 0.93 | 2.042 | 1.093 |
| fp16 | vpu_hier | 0.343 | 0.381 | 0.9994 | 0.991 | 0.56 | 2.399 | 1.106 |
| fp16 | unit_hier | 0.453 | 0.499 | 0.9991 | 0.997 | 0.83 | 2.579 | 1.116 |
| fp16 | vpu_hier2 | 0.279 | 0.299 | 0.9997 | 0.997 | 0.47 | 1.812 | 1.089 |
| fp16 | vpu_map_only | 3.095 | 3.131 | 0.9517 | 0.891 | 8.31 | 3.208 | None |
| fp16 | clk_only | 4.016 | 4.434 | 0.8714 | 0.838 | 9.56 | None | 2.332 |
| fp16 | ff_toggles_clk | 0.562 | 0.606 | 0.9985 | 0.994 | 1.05 | 8.102 | 1.051 |
| fp32+fp16 | vpu_map | 0.357 | 0.375 | 0.9994 | 0.991 | 0.84 | 1.871 | 1.092 |
| fp32+fp16 | unit_map | 0.507 | 0.530 | 0.9989 | 0.991 | 1.01 | 1.975 | 1.11 |
| fp32+fp16 | vpu_hier | 0.431 | 0.460 | 0.9990 | 0.988 | 0.96 | 2.349 | 1.121 |
| fp32+fp16 | unit_hier | 0.576 | 0.615 | 0.9982 | 0.991 | 1.24 | 2.487 | 1.143 |
| fp32+fp16 | vpu_hier2 | 0.283 | 0.294 | 0.9997 | 0.994 | 0.49 | 1.827 | 1.082 |
| fp32+fp16 | vpu_map_only | 3.636 | 3.670 | 0.9476 | 0.883 | 8.31 | 3.061 | None |
| fp32+fp16 | clk_only | 4.852 | 5.070 | 0.8171 | 0.717 | 9.85 | None | 2.335 |
| fp32+fp16 | ff_toggles_clk | 0.753 | 0.793 | 0.9967 | 0.988 | 1.70 | 8.436 | 1.003 |
| int8 | vpu_map | 0.287 | 0.331 | 0.9934 | 0.968 | 0.58 | 3.735 | 2.133 |
| int8 | unit_map | 0.368 | 0.418 | 0.9897 | 0.971 | 0.69 | 4.589 | 2.166 |
| int8 | vpu_hier | 0.276 | 0.315 | 0.9940 | 0.971 | 0.62 | 3.896 | 2.129 |
| int8 | unit_hier | 0.368 | 0.418 | 0.9897 | 0.971 | 0.69 | 4.589 | 2.166 |
| int8 | vpu_hier2 | 0.288 | 0.332 | 0.9934 | 0.968 | 0.58 | 3.727 | 2.157 |
| int8 | vpu_map_only | 0.682 | 0.707 | 0.9693 | 0.882 | 1.45 | 4.967 | None |
| int8 | clk_only | 1.656 | 1.830 | 0.7548 | 0.657 | 3.47 | None | 7.017 |
| int8 | ff_toggles_clk | 0.485 | 0.550 | 0.9843 | 0.929 | 0.87 | 21.903 | 2.414 |

### Across formats, coefficients fitted on one and applied to the other

| counted as | fp32 → fp16 rms (W), r | fp16 → fp32 rms (W), r | fp32+fp16 → int8 rms (W), bias (W), r |
|---|---:|---:|---:|
| vpu_map | 0.376, 0.9996 | 0.452, 0.9994 | 2.215, -1.813, 0.9934 |
| vpu_hier | 0.382, 0.9993 | 0.528, 0.9987 | 1.867, -1.528, 0.9935 |
| vpu_hier2 | 0.285, 0.9997 | 0.292, 0.9996 | 2.261, -1.852, 0.9934 |

### Coefficients frozen on E78's fp32 and fp16 kinds, applied to other experiments

| set | measured on | n | rms (W) | bias (W) | r | ρ | measured / predicted |
|---|---|---:|---:|---:|---:|---:|---:|
| e90, floats | aifoundry3, E90 | 16 | 0.482 | -0.065 | 0.9985 | 0.985 | |
| e86, floats | aifoundry3, E86 | 6 | 0.193 | +0.105 | 0.9988 | 1.000 | |
| e82, floats, card scale 0.9711 fitted here | aifoundry1 card 1 | 33 | 0.361 | -0.104 | 0.9993 | 0.991 | |
| e88, floats, E82's card scale | aifoundry1 card 1 | 14 | 0.452 | +0.383 | 0.9991 | 0.991 | |
| E65, fp32 B, one bit, A = 1.0 | aifoundry3 | 32 | 0.128 | -0.019 | 0.9953 | 0.976 | 1.020 |
| E65, B, A = π | aifoundry3 | 5 | 0.717 | +0.691 | 0.9983 | 1.000 | 0.887 |
| E67, fp32 A, one bit, B = 1.0 | aifoundry3 | 32 | 0.264 | +0.164 | 0.9909 | 0.974 | 0.842 |
| E67, A, B = π | aifoundry3 | 5 | 0.520 | +0.518 | 0.9986 | 1.000 | 0.828 |
| E67, the interaction grid | aifoundry3 | 24 | 0.938 | +0.820 | 0.9745 | 0.961 | 0.854 |
| E70, low bits together | aifoundry3 | 9 | 0.281 | +0.032 | 0.9988 | 1.000 | 1.021 |
| E70, spread bits | aifoundry3 | 7 | 0.172 | +0.141 | 0.9993 | 1.000 | 0.980 |
| E70, A, low bits | aifoundry3 | 7 | 0.999 | +0.809 | 0.9985 | 1.000 | 0.802 |
| E60, low bits, A = π | aifoundry3 | 7 | 1.238 | +1.184 | 0.9992 | 1.000 | 0.871 |
| E60, A's order | aifoundry3 | 8 | 0.522 | +0.518 | 0.9992 | 1.000 | 0.859 |
| E79, a16 | aifoundry3 | 16 | 0.222 | +0.079 | 0.9839 | 0.959 | 0.923 |
| E79, a8 | aifoundry3 | 8 | 0.523 | +0.173 | 0.9607 | 0.333 | 0.792 |
| E79, b16 | aifoundry3 | 16 | 0.132 | -0.005 | 0.9952 | 0.988 | 1.002 |
| E79, b8 | aifoundry3 | 8 | 0.062 | +0.004 | 0.7091 | 0.833 | 1.396 |
| E79, b8k | aifoundry3 | 8 | 0.088 | -0.033 | -0.5117 | -0.119 | 0.751 |

### What the coefficients do under other readings

- vpu_map: k 1.871 ± 0.021 fJ, a 1.092 ± 0.014 fJ (jackknife over kinds); leakage arm 0: 1.917, 1.122, rms 0.384 W; arm 0.3803: 1.829, 1.065, rms 0.335 W
- vpu_hier: k 2.349 ± 0.040 fJ, a 1.121 ± 0.027 fJ (jackknife over kinds); leakage arm 0: 2.406, 1.152, rms 0.460 W; arm 0.3803: 2.296, 1.093, rms 0.405 W
- vpu_hier2: k 1.827 ± 0.014 fJ, a 1.082 ± 0.011 fJ (jackknife over kinds); leakage arm 0: 1.872, 1.111, rms 0.305 W; arm 0.3803: 1.786, 1.055, rms 0.265 W

### Random data's watts, split by the model

| kind | D | clocked register bits | data nets | multiplier | adder and normaliser | result path (f6 + C register file) | operand bus (f0 + lane) | exponent | control | sequencer |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fp32.randn | 24.72 | 8.41 | 16.46 | 7.57 | 4.90 | 0.69 | 1.55 | 0.89 | 0.60 | 0.38 |
| fp16.randn | 22.16 | 8.40 | 13.69 | 5.01 | 4.45 | 0.71 | 1.53 | 1.11 | 0.62 | 0.38 |
| int8.full | 7.06 | 1.53 | 5.21 | 2.03 | 0.96 | 0.00 | 1.81 | 0.00 | 0.01 | 0.54 |
| fp32.ones | 8.26 | 8.41 | 0.08 | 0.00 | 0.01 | 0.04 | 0.01 | 0.00 | 0.01 | 0.12 |

(The split is of the fit, not a measurement, and it is over the type's zeros only in total: the stage columns are absolute nets at the fit's k.)

### Merged-net toggles per multiply-add, by stage (the whole VPU, `nets_map`)

| kind | clocked | changed | operand bus | multiplier | adder and normaliser | result path | exponent | control | sequencer | total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fp32.randn | 1,932 | 429 | 180.2 | 881.3 | 570.1 | 80.2 | 103.7 | 69.9 | 44.2 | 1,930.7 |
| fp32.uniform01 | 1,932 | 364 | 174.3 | 885.8 | 515.9 | 72.6 | 56.2 | 21.3 | 41.3 | 1,768.4 |
| fp32.smallint | 1,729 | 227 | 61.9 | 89.9 | 324.6 | 73.8 | 91.4 | 66.8 | 32.9 | 743.0 |
| fp32.ones | 1,932 | 13 | 1.6 | 0.2 | 1.2 | 4.9 | 0.4 | 1.0 | 14.3 | 23.9 |
| fp32.nn_like | 1,053 | 224 | 125.3 | 432.9 | 281.6 | 47.4 | 48.1 | 36.8 | 42.5 | 1,016.4 |
| fp16.randn | 965 | 188 | 88.9 | 291.9 | 259.3 | 41.5 | 64.9 | 35.9 | 22.1 | 804.5 |
| fp16.uniform01 | 965 | 150 | 83.5 | 290.4 | 169.1 | 36.7 | 43.0 | 13.3 | 20.3 | 656.4 |
| fp16.ones | 965 | 6 | 0.8 | 0.1 | 0.5 | 2.4 | 0.2 | 0.7 | 7.2 | 11.9 |
| int8.full | 47 | 8 | 15.4 | 17.2 | 8.1 | 0.0 | 0.0 | 0.1 | 4.6 | 45.4 |
| int8.ones | 47 | 1 | 0.7 | 0.0 | 0.1 | 0.0 | 0.0 | 0.1 | 1.1 | 1.9 |

### E65's list: a flip of one B bit, A = 1.0, by stage, per multiply-add over `lq_h0`

| bit | D (W) | predicted (W) | nets | operand bus | multiplier | adder and normaliser | result path | exponent | control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.63 | 0.84 | 97.5 | 8.0 | 26.3 | 19.1 | 0.1 | 39.9 | 3.7 |
| 2 | 0.41 | 0.46 | 53.8 | 8.1 | 22.9 | 19.2 | -0.3 | 3.4 | 0.3 |
| 4 | 0.48 | 0.45 | 52.1 | 8.1 | 24.5 | 18.9 | -0.0 | 0.0 | 0.0 |
| 6 | 0.38 | 0.43 | 50.4 | 8.1 | 22.6 | 19.5 | -0.1 | 0.0 | 0.0 |
| 8 | 0.52 | 0.47 | 54.5 | 8.8 | 21.8 | 22.5 | 0.9 | 0.1 | 0.1 |
| 10 | 0.96 | 0.95 | 110.6 | 16.1 | 28.8 | 51.6 | 10.1 | 1.5 | 0.3 |
| 12 | 1.57 | 1.48 | 172.8 | 24.9 | 33.4 | 87.7 | 19.2 | 1.6 | 2.4 |
| 14 | 2.16 | 2.15 | 250.5 | 32.3 | 39.8 | 132.0 | 31.3 | 5.2 | 3.7 |
| 16 | 2.79 | 2.73 | 317.3 | 37.1 | 46.7 | 181.7 | 40.1 | 1.9 | 1.6 |
| 18 | 3.15 | 3.12 | 363.4 | 42.5 | 53.1 | 204.5 | 51.2 | 1.4 | 1.4 |
| 20 | 3.97 | 3.85 | 448.0 | 47.6 | 56.5 | 252.4 | 66.0 | 9.1 | 5.1 |
| 21 | 4.16 | 4.24 | 493.8 | 50.1 | 56.9 | 281.9 | 71.9 | 12.7 | 7.7 |
| 22 | 4.63 | 4.63 | 538.7 | 44.7 | 52.5 | 311.4 | 71.5 | 30.5 | 15.6 |
| 23 | 0.80 | 0.73 | 85.3 | 8.4 | -0.0 | 2.5 | 9.6 | 51.8 | 9.0 |
| 25 | 0.68 | 0.55 | 64.0 | 4.4 | -0.0 | 2.7 | 6.5 | 40.5 | 8.3 |
| 27 | 0.51 | 0.45 | 51.8 | 6.1 | 0.0 | 2.0 | 3.0 | 34.6 | 5.0 |
| 29 | 1.06 | 1.21 | 140.4 | 8.1 | -0.0 | 3.8 | 8.4 | 99.1 | 19.0 |
| 30 | 0.74 | 1.00 | 116.4 | 6.1 | -0.0 | 3.1 | 6.1 | 81.0 | 17.3 |
| 31 | 0.56 | 0.65 | 75.3 | 4.1 | -0.0 | 0.1 | 18.7 | 0.0 | 50.8 |

## 9. Files, and how to rerun

| file | what |
|---|---|
| `counts-v2.json` | all 51 kinds at 3 points of a launch: `rows.<type>.<kind>.points[]` and `.mean`; `unit` and `vpu` each with `nets_hier`, `nets_hier2`, `nets_map`, names, ids, `by_stage`; `ff.{all,txfma,tima,rest}.{clocked,toggles,present}`; `valid_slots`; `check_mismatch` |
| `counts-e92.json`, `counts-e88.json`, `counts-e90.json`, `counts-e86.json`, `counts-hl.json`, `counts-hlp.json` | the same for E92's, E88's, E90's and E86's tiles, E60–E70's 146 and E79's 73 |
| `analysis.json`, `analyze.py`, `make_tables.py` | every fit and out-of-sample score above |
| `e92-bench-prediction-frozen.json` | the prediction as frozen at `de545f0c`, byte for byte |
| `e92-bench-prediction.json`, `predict_e92.py`, `e92-prediction-scored.json`, `score_e92_prediction.py` | every variant of the prediction (its `nets_hier2` is checked against the frozen file), and the score |
| `counts-e94e95.json`, `predict_e94_e95.py`, `e94-e95-bench-prediction.json`, `e94-e95-bench-prediction.md` | M2's frozen predictions for E94 and E95 (§10) |
| `predict_m4.py`, `m4-bench-prediction.json`, `m4-bench-prediction.md` | M4 and I3, frozen for E95 (§11) |
| `score_frozen.py`, `scored-frozen.json` | those frozen predictions against E95 and E94 (§12) |
| `counts-e103-pool.json`, `simple-e103-pool.json` | the bench and the simple predictors on E103's 215 candidates |
| `fcheck/` | the functional check's output |
| `old-benches/` | the old benches with and without the flag; the recount redone; `use_prev_sigs`; the flip |
| `optimiser-sensitivity/` | the same three kinds with Verilator's optimisations off and on, before the map existed; `counts-O0-map.json`, five kinds at -O0 with the map learned again on that binary |
| `model-form-search/` | the search behind M4 and I3, 14 float forms and 5 int8 forms |
| `zeros/` | §14: which clocks and registers stay on for zeros, and Q130(i) rerun |
| `corrections-check.py`, `corrections-check.txt` | the corrections' numbers |
| `versions.txt` | tool versions and core-et's commit |

```
cd rtl-sim/fma_toggle_v2
make CORE_ET=../../external/core-et && make check CORE_ET=../../external/core-et
python3 train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds ../../tools/claims-v3/kinds --out maps
python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds ../../tools/claims-v3/kinds --out counts-v2.json --jobs 8
```

A clean build from the committed files reproduced `counts-v2.json`'s fp32 `randn` exactly, register for register and net for net. Installed for this: `brew install verilator` on the mini, and numpy under `uv` for the analysis. Nothing ran on a lab host.

## 10. Frozen predictions for E94 and E95

[`e94-e95-bench-prediction.md`](e94-e95-bench-prediction.md) gives every tile's predicted D with a 95% interval; the JSON beside it holds the same with both merges and each launch point. The commit holding these files is the freeze.

**What was frozen before what.** E95: the commit precedes any E95 data on main, and I read none of its data. E94: **post hoc by the clock**. Its data commit, `a3824bb8` at 01:55:23 PDT, landed 11 seconds after this bench run started and before this commit. I read none of it, and `predict_e94_e95.py` opens neither data directory, but nothing proves that from outside. E95's three partner tiles from E86 are marked: E86 read them on that card, and k and a did not use them. (02:00 PDT became 01:00 PST during this work.)

**The model, unchanged from §Results 5.** Floats: k = 1.871 fJ, a = 1.092 fJ, fitted on E78's 33 fp32 and fp16 kinds alone. E95 runs on E78's card, so no scale. E94 runs on aifoundry1 card 1: one scale from E82 alone, 0.9711 ± 0.0043. `nets_hier2`'s prediction stands beside it in every row.

**int8 has its own empirical terms.** k = 3.735 fJ and a = 2.133 fJ, fitted on E78's 15 int8 kinds alone (rms 0.287 W, leave-one-out 0.331 W). Its multiply and adds are behavioural RTL with no nets inside them, so these are fitting constants on the counts that exist, not comparable with the float constants, and the float constants fail on int8 (bias −1.8 W). Card 1's int8 scale, from E82 alone: 0.9736 ± 0.0242.

**The interval** is t(0.975, n − 2) × √(s² + x′Cx + m²). s is the rms of out-of-sample errors already read on that card: 0.411 W over 87 (floats, aifoundry3: E78 leave-one-out, E86, E90, E92's tiles under this merge, which E92 had by then published), 0.355 W over 19 (int8, aifoundry3), 0.391 W over 47 (floats, card 1: E82 after its scale, E88), 0.282 W over 20 (int8, card 1). C is the coefficients' jackknife covariance on E78, and m the tile's standard error over its three launch points. No correction for the known bias: gated kinds have run 0.17–0.65 W low, and only the interval covers that. Offsets get √2 × s, which is conservative.

**Every tile passes the functional check:** 0 of 256 words wrong at all three launch points, all 84 tiles.

Rerun: `run_kinds.py … --types fp32,fp16,int8 --only __none__ --extra-tiles <type>:<name>:<path>,…` over `tools/claims-v3/kinds/e94/tiles`, `real2/tiles` (named `r2_<name>`), and `real/tiles`' three partners (named `real_<name>`), writing `counts-e94e95.json`; then `predict_e94_e95.py`.

## 11. A second model, frozen for E95: the operand bus gets its own price

[`m4-bench-prediction.md`](m4-bench-prediction.md) (`predict_m4.py`). Reading the frozen §10 predictions against E94's published data (post hoc by the clock, as §10 says): fp32 rms 0.44 W, bias −0.37; fp16 0.40 W, bias −0.16; int8 0.34 W, bias −0.33; every tile inside its interval. The misses sit on gated kinds, as §6 named. So I compared forms on what had been read, holding out whole experiments, and one change stands out: **the lane's operand bus costs about four to five times a local net.** Fitted on E78 alone, M4 is k_core 1.62 fJ (multiplier, adder and normaliser), k_bus 7.53 fJ, k_rest 2.22 fJ (every other net), a 1.07 fJ per clocked bit: E78 fit 0.136 W against M2's 0.357 W, E86 0.145 against 0.193, E90 0.220 against 0.482, E92 0.242 against 0.434, card 1 with E82's scale: E88 0.214 against 0.452, E94 0.178 against 0.416. It does not help everywhere: E70's spread ladder gets worse, 0.369 against 0.172, and E60's low-bit ladder stays near 1 W. int8's own form, I3 (nets, bus 16.7 fJ, clocks), fits E78 at 0.181 W against 0.287 W.

**The form was chosen after reading E94, so E94 does not test it. E95 does:** this section's commit precedes E95's data on main, and I read none of it. §10's M2 stands as committed. The search is committed and counted: 14 float forms and 5 int8 forms, on what had been read ([`model-form-search/`](model-form-search/)).

## 12. The frozen models against E95 and E94

[`scored-frozen.json`](scored-frozen.json), `score_frozen.py`. **E95 is the clean test:** M2 went up in `2b7ece4a` at 01:03:01 PST and M4 in `b995463e` at 01:08:31 PST, and E95's data commit `ab23b1aa` came at 01:37:06 PST, on aifoundry3 card 0, E78's card, with no scale.

| E95, 30 blind tiles | n | M4 or I3: rms (W), bias, r | M2: rms (W), bias, r | Q130(n)'s (a): rms (W) | inside M4's 95% |
|---|---:|---:|---:|---:|---:|
| floats | 19 | **0.158**, +0.116, 0.9999 | 0.415, +0.041, 0.9996 | 0.610 | 19 |
| fp32 | 11 | **0.102**, +0.078, 1.0000 | 0.424, +0.138, 0.9996 | 0.506 | 11 |
| fp16 | 8 | **0.212**, +0.169, 0.9999 | 0.403, −0.093, 0.9999 | 0.730 | 8 |
| int8 | 11 | **0.166**, +0.004, 0.9942 | 0.285, −0.249, 0.9953 | 0.824 | 11 |
| floats, gate closing ≥ 10% | 7 | **0.082**, +0.053 | 0.482, −0.356 | 0.806 | 7 |
| floats, dense | 12 | **0.189**, +0.153 | 0.371, +0.272 | 0.458 | 12 |

So the bus term did what it was added for: M2's 0.36 W shortfall on real gated tiles is gone, blind. **The largest misses:** `fp16.r2_bert_l6_up`, 21.74 W measured, 22.13 W predicted, and the other dense fp16 tiles, all 0.1–0.4 W high; int8's calibrations, ±0.3 W. These are real tensors, which E78's kinds resemble: E103 is the test built to hurt it.

**E94, by the clock post hoc for M2 and no test at all for M4** (§10, §11). M2 on the 51 draws: fp32 0.437 W, bias −0.373; fp16 0.397 W, −0.159; int8 0.338 W, −0.332; all 51 inside the interval. M4 on them, for the record: 0.183, 0.174 and 0.283 W. **Within one rule, the bench says which draw costs more:** centred on the rule's mean, M2's error is 0.03–0.07 W where the draws themselves spread by 0.47–0.53 W (`fp32.nn_like`, `fp32.sparse50`, `fp16.nn_like`; `scored-frozen.json` `e94.within_rule`). I read no E94 data before M2's commit, but nothing shows that from outside.

## 13. E103

M4 and I3 then met [E103](../2026-11-01-e103-model-blind-test/README.md), 30 tiles picked per family where they most disagree with two simple predictors, from a pool I wrote, on a second card with one scale from E82: 0.314 W rms in floats and 0.365 W in int8. Its margin over the best comparators is about 2×, not the 12.6× against Q130(n), whose size the selection sets. That README holds the plain statement of how good the model is, per format, on what, and where it fails.

## 14. Item 12's last two pieces: int8 zeros' 0.61 W, and zeros' transport

*Post hoc. Nothing here was registered, E78's 0.61 W was known first, and no card ran. Everything is in [`zeros/zeros-check.txt`](zeros/zeros-check.txt) (`zeros/zeros_check.py`).*

**int8 zeros: the count does not explain the 0.61 W, and it points the wrong way.** Per second, chip-wide, allowing for int8's higher op rate:

| per second | fp32 zeros | int8 zeros | int8 ÷ fp32 |
|---|---:|---:|---:|
| TensorFMA ops | 1.121 × 10⁹ | 1.926 × 10⁹ | 1.72 |
| register bits clocked, enable high | 1.168 × 10¹⁵ | 0.761 × 10¹⁵ | 0.65 |
| register bits seeing a clock edge | 6.79 × 10¹⁵ | 3.44 × 10¹⁵ | 0.51 |
| of which the multiply-add unit's | 4.21 × 10¹⁵ | 0.86 × 10¹⁵ | 0.20 |
| register bits that change | 3.88 × 10¹³ | 1.71 × 10¹³ | 0.44 |
| merged nets toggling | 6.53 × 10¹³ | 3.67 × 10¹³ | 0.56 |
| scratchpad line reads, **not priced: the dcache is not in the bench** | 3.23 × 10¹¹ | 4.31 × 10¹¹ | **1.34** |
| **measured S, E78, W over idle** | **1.986 ± 0.059** | **2.605 ± 0.028** | **1.31** |

At M4's float constants, an extrapolation because M4 was fitted over zeros and its a has never been tested on the bits that stay clocked there, the count gives fp32 1.42 W of its 1.99 W and int8 0.91 W of its 2.61 W. **So it says int8 − fp32 = −0.51 W against the measured +0.62 W, leaving 1.13 W unexplained.** The gap is a property of the formats: +0.41 to +0.62 W, ratio 1.19–1.31, over 13 committed sessions on two cards.

**Which clocks stay on when every slot is gated,** from the VCD (`zeros/clocks-*.json`, `zeros/acct-*.txt`). In both formats the unit's root clock ignores the gate. fp32's `clock_txfma` rises 534 times in the 559 cycles, on all 8 lanes (`vpu_lane.v:194,221-223`), and feeds 3.76 M register-bit edges an op with their enables low, mostly in `txfmactl0_top` and `txfmaexp0_top`, while the operand clocks of `txfmafrac_top.v:337-356` never rise. int8's `tima_clock` rises 304 times in 331 cycles on all 16 units (`vpu_lane.v:212-214`, `vpu_lane_tima.v`), and feeds 0.45 M, and TenC's read enable stays high whatever the gate says (`vpu_lane.v:432`). So the integer unit keeps its clock on, as the RTL reading suggested, but it is a much smaller load than the float unit's.

**What points the right way is outside the bench:** scratchpad reads, ×1.34, and ops, ×1.72. If all of S(zeros) scaled with reads, int8 would read 2.65 W, near the measured 2.61 W, though the 13 sessions' ratio is below 1.34 in every one. Solving S = c × clocked + r × reads gives c = 0.06 fJ a bit and r = 5.9 pJ a line, which needs the bits clocked on zeros to be nearly free; S = c + e × ops gives 770 pJ an op and 1.12 W. **One number cannot separate these.** A card run that changes the read rate on zeros could.

**The caveat:** int8's arithmetic is behavioural in the public RTL, so its register count may not be the silicon's. For the integer unit's clock alone to close the gap it would need 135 more register bits on a slot's clock, against the RTL's 109: 2.2×. This bench cannot rule that out.

**Zeros' transport: the fixed bench does not change the 0.20–0.37 pJ.** Q130(i) re-prices Q129's gate-level energies by activity ratios from its own structural simulation, and on zeros no multiply-add runs, so the fault's path is never used. Its simulation, its own `run.sh`, reproduces its committed `counts.txt` byte for byte with and without `-fno-dfg` ([`zeros/q130i-rerun.txt`](zeros/q130i-rerun.txt)), and the recount's bench on zeros is unchanged by the flag. **What the fixed bench adds is the whole `vpu_top` confirming its three gating claims directly on fp32 zeros:** `rd_enable0` and `rd_enable1` never rise and `rd_enable2` does; `wr_enable0` and `wr_enable1` never rise; `clock_bypass` never rises. As a different yardstick, at M4's constants, again extrapolated: the whole VPU on fp32 zeros is 0.04 pJ of nets and 0.27 pJ of clocked bits, 0.31 pJ a multiply-add, against E78's 0.43 pJ over idle. No new gate-level energy exists, so the reading stays "narrowed, not closed".

## Corrections after verification

*Sun 1 Nov 2026, against `8c354a91`, from an independent verifier's read. **No frozen file, data file or registered verdict changed.** Wrong sentences are replaced above. Every number here is recomputed in [`corrections-check.txt`](corrections-check.txt) unless it is marked the verifier's. The fix reproduced in its hands: the reproducer on two Verilator builds, the check from a clean copy with a fresh seed (fp32 40,000 of 40,000; fp16 39,774 plus 226 `window_cancel`), and M4's refit.*

- **C1: the optimiser caveat understated by 10×, as written.** "+3.2%, +5.9%" was `nets_hier` only. `nets_hier2`, within 1% of the map at the default build, moves +34.8% and +31.8% (A). **I reran the map at -O0, as it asked, and that narrows it:** learned again on that binary, +3.5% and +5.2% (A2). §6 now quotes all three. The verifier's "'1,816' and the bus's ratio depend on the tool setting" holds for hier2; for the map, by 3–5%, with the lane bus unchanged. No constant has been refitted at -O0.
- **C2: "about 1,400 to 1,800" was not a band.** The map reads at or above `nets_hier` on 51 of 51 kinds by construction (B). Blind, two terms read E103 1.18 W and E95 0.50 W under `nets_hier`, 0.58 and 0.42 W under `nets_map`, 0.56 and 0.38 W under `nets_hier2` (the verifier's), so map and hier2 are not separated, and choosing the map after the ladders changed little.
- **C3: "two constants … to about a tenth of a watt" named no model, and its merge was chosen after those ladders.** M2 with the map 0.128 W, M2 with the merge frozen first 0.303 W, M4 0.185 W, on E65. M4 is worse than M2 on E65 and on E70's spread, 0.369 against 0.172 W (D).
- **C4: the check's wording and scope** are now in Result 3 (C): "hand-built hard cases", the 6,912 trivial words, fp16's 10,752, int8's figure, no card, and that a pass does not validate counts. The control with the pass on is the verifier's. The blog lines add that core-et is a later revision.
- **C5: small.** The reproducer is 25 lines of code, not 20 (E), fixed here, in `rtl-sim/fma_toggle_v2/README.md` and in the Makefile's comment. `accum.c`'s comment said 20,000 of 20,000, now 40,000, a comment only. M4's form search is committed and counted (§11).
- **E103's own corrections are in its README.** None of the verifier's faults was rejected; C1 is narrowed by the rerun it asked for.
