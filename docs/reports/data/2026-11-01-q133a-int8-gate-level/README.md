# Q133(a): int8's multiply-add at gate level, beside fp32 and fp16 in one bench

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 12, "int8 at gate level" (the list at `1fe8377a18af`): "int8's multiply is behavioural in the public RTL, so its counts below the multiply-add are not comparable and the bench undercounts its single flips ([Q132(b)](../2026-11-01-q132-rtl-bench/README.md), [E102](../2026-11-01-e102-balanced-bit-prices/README.md)). A gate-level count of `tima_top` would give them."*

*Sun 1 Nov 2026 (week 44), Q133, desk work on a desk machine shared with other lanes' benches, 10:43 to 12:09 PST (the runs 11:21 to 12:06). **No card was opened and nothing was measured in watts here**: every watt below is a committed experiment's (E78, E79, E102), named where it is used. The int8 unit, `tima_top`, and for comparison the float unit, `txfma_top`, were synthesized with the open flow (Yosys `33177a407` with the slang frontend, ASAP7 RVT TT, the open flow's own recipe) and run, in place of their RTL, in Q132(b)'s whole-`vpu_top` bench (Verilator 5.052, `-fno-dfg`), counted by that bench's own counter. How: [METHOD.md](METHOD.md). Code: [`tools/open-flow/tima/`](../../../../tools/open-flow/tima/), [`rtl-sim/tima_gate/`](../../../../rtl-sim/tima_gate/). Versions: [`versions.txt`](versions.txt). Every number is in [`analysis.json`](analysis.json), written by [`analyze.py`](analyze.py) from the committed counts; [`tables.md`](tables.md) is generated from it.*

*Corrected the same day after an independent verification ([Corrections after verification](#corrections-after-verification)). The main change: **every RTL-side number now names its merge.** Q132(b)'s primary merge, `nets_map`, is given beside `nets_hier`, the merge Q132(b) §4 demoted for regular streams. At gate level the two merges agree on random data; at RTL they do not.*

## Results

**1. As gates, a random int8 multiply-add switches 175 merged nets on the primary netlist, five times what the RTL bench counts, and the multiplier is most of it.**
On `int8.full` the primary netlist (radix-4 Booth on B with carry-save sums, `booth_tree`) switches **175.0 merged nets per MAC** in the unit. Its three launch points read 174.95–175.04. `booth_tree` was chosen as primary when the arms were built, and it was built and run first; the choice was not registered, and no timestamped record shows it was made before any count was set beside a card. The RTL bench counts 35.6 (mean of three launch points; `nets_hier` and Q132(b)'s `nets_map` read the same for int8, `analysis.json` `merges.int8_unit`; `runs/booth_tree/counts_kinds.json`, `analysis.json` `kinds.full`). **How the tool builds the multiplier moves this**: at the middle launch point the four netlists give 173 to 206, 4.8–5.8× the RTL (result 6). The stage the behavioural `*` hid, the four 9×9 products and their sum, goes
from **17.2 to 139.0** (8.1×), 79–83% of the unit's count in every netlist. The operand registers and their enable multiplexers go from 10.2 to 15.2, and the add of C and the result from 8.1 to 20.4.
All 16 int8 kinds at three launch points, 48 tile-points, pass the bench's check: **0 of 256 accumulator words wrong** in every one, and no X.

| per MAC, in the unit | `full` | `gauss_q` | `sorted` | `pos` | `smallint` | `ternary` | `sparse50` | `wsparse50` | `highbit` | `sparse90` | `ones` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RTL (Q132(b); either merge) | 35.6 | 35.6 | 31.5 | 27.7 | 35.3 | 29.9 | 26.8 | 16.7 | 12.9 | 6.6 | 0.1 |
| **gates, `booth_tree`** | **175.0** | **147.7** | **152.9** | **133.0** | **131.4** | **103.9** | **99.8** | **63.5** | **43.6** | **15.3** | **0.3** |
| × RTL | 4.91 | 4.15 | 4.86 | 4.81 | 3.72 | 3.47 | 3.72 | 3.80 | 3.38 | 2.34 | 2.7 |

(`nets_hier`. At gate level `nets_map` reads within 0.1% of it on seven of these kinds, 1.2% higher on `pos` and `highbit`, and 4–7% higher on the 90%-sparse kinds. On the constant streams, where `nets_hier` folds fan-out that switches in step, `nets_map` reads 2.7× higher on `ones` (0.9) and 7.8× on `neg_ones`; `analysis.json` `merges.int8_unit`.)

**At gate level the kinds fall in the card's order.** E78 measures, in watts over int8's zeros, `full` 7.06, `gauss_q` 6.60, `sorted` 6.59,
`pos` 6.17, `smallint` 6.00, `ternary` 5.19, `highbit` 3.23. Over those seven dense kinds Spearman's ρ between the card and the count is
**0.964 for every netlist, against 0.821 for the RTL count** (all 15 non-zero kinds: 0.921–0.925 against 0.882; `analysis.json`
`rank_vs_card`). The RTL put `smallint` level with `full` (0.99 of it), because a behavioural product has no partial products to stay quiet;
the primary netlist puts it at 0.75 and the card at 0.85.

**2. The control: Q132(b)'s bench, rebuilt here, reproduces its committed counts exactly.** 16 tile-points (`full`, `gauss_q`, `ones`,
`zeros` at three launch points; `hq`, `bk_5`, `a8q`, `a8_7` at the middle one): every unit and whole-VPU `nets_hier`, register bit clocked
and changed, and valid slot equals `counts-v2.json`, `counts-e102.json` or `counts-hlp.json` to the unit, with 0 words wrong
(`analysis.json` `control`). So everything below differs from Q132(b) by the netlist alone. The control's own `nets_map` is not compared:
its map was learned on one stream. Every RTL `nets_map` number here is read from Q132(b)'s committed counts, which its trained map made.

**3. All three formats at gate level, in one bench, from one flow.** With the float unit's netlist in place of its RTL (`txfma_top`, 16,063
cells; all 35 fp32 and fp16 kinds of Q132(b) at the middle launch point, every one with 0 words wrong; `runs/f_txfma_flat/counts_kinds.json`,
`analysis.json` `float_gate`, `merges.float_unit`):

| per MAC, random data, in the unit | fp32 `randn` | fp16 `randn` | int8 `full` |
|---|---:|---:|---:|
| RTL bench, `nets_map`, Q132(b)'s primary (the same point) | 1,810.2 | 745.4 | 35.7 |
| RTL bench, `nets_hier` (Q132(b), the same point) | 1,427.0 | 579.1 | 35.7 |
| **gates, this bench, `nets_hier`** | **3,386.5** | **1,368.2** | **175.0** (three points: 175.0) |
| gates ÷ RTL, by `nets_map` | **1.87** | **1.84** | 4.91 |
| gates ÷ RTL, by `nets_hier` | 2.37 | 2.36 | 4.91 |
| cells (one lane holds one float unit and two int8 units) | 16,063 | 16,063 | 2 × 2,019 |

**By Q132(b)'s primary merge the float unit's RTL count is about 1.9× low in both formats** (1.87× fp32, 1.84× fp16; median 1.91 over the 29
kinds whose lanes multiply, 1.71–2.13 over the 24 of them that carry varying data). So the RTL count misses 46–47% of the gates' switching nets.
By `nets_hier`, which folds the RTL's same-waveform fan-out, it is about 2.4× low (2.37×, 2.36×; median 2.47, 2.29–3.32) and misses 58%
(`analysis.json` `merges.float_unit`). **int8's RTL count is 4.9× low on random data in either merge, and 3.4–4.9× on its dense kinds**: the float multiplier is written
out structurally in the RTL and int8's is not. At gate level the two merges agree within 0.2% on these kinds (`nets_map` 3,386.5, 1,368.4, 175.1).
Q126's open netlist counted 3,299 for fp32 on another stream and bench ([open netlist](../2026-10-26-open-netlist/POWER.md)), 3% from this.
**At gate level a random MAC switches 19× as many nets in fp32 as in int8 on the primary netlist, and 7.8× in fp16**. Across the four int8
netlists that is 16.5–19.6× and 6.7–7.9× (`float_gate.randn_over_int8_full_mid`). Per TensorFMA op (4,096, 8,192 and 16,384 MACs) the
primary netlist's figures come to 13.9 M, 11.2 M and 2.9 M.

**4. At gate level the floats and the netlists that Booth-recode B want the same price per net toggle, and the cross-format miss falls by 60–80%; int8's clock constant stays about twice the floats'.**
D = rate × (k × nets toggled in the VPU + a × register bits clocked), each over the type's zeros, on E78's measured watts. This is the
bench's model M2 (`analysis.json` `model`, `float_gate.cross_format`; both merges in `merges.m2`). ± is a jackknife standard error over
kinds (`coef_jackknife_se_fJ`).

| counts | merge | fitted on | n | k, fJ per net toggle | a, fJ per clocked bit | rms (W) | leave-one-out (W) |
|---|---|---|---:|---:|---:|---:|---:|
| RTL | `nets_map` (Q132(b)'s primary) | fp32 + fp16 | 33 | 1.88 ± 0.02 | 1.09 ± 0.01 | 0.352 | 0.369 |
| RTL | `nets_hier` | fp32 + fp16 | 33 | 2.36 ± 0.04 | 1.12 ± 0.03 | 0.409 | 0.437 |
| **gates** | `nets_hier` | fp32 + fp16 | 33 | **1.05 ± 0.01** | 1.08 ± 0.01 | 0.391 | 0.405 |
| RTL | `nets_map` | int8 | 15 | 3.74 ± 0.14 | 2.13 ± 0.09 | 0.287 | 0.331 |
| RTL | `nets_hier` | int8 | 15 | 3.90 ± 0.13 | 2.13 ± 0.06 | 0.276 | 0.315 |
| **gates, `booth_tree`** | `nets_hier` | int8 | 15 | **1.01 ± 0.05** | 2.38 ± 0.20 | 0.259 | 0.295 |
| gates, `booth` | `nets_hier` | int8 | 15 | 1.02 ± 0.05 | 2.38 ± 0.20 | 0.259 | 0.295 |
| gates, `booth_swap` | `nets_hier` | int8 | 15 | 0.86 ± 0.02 | 2.16 ± 0.07 | 0.238 | 0.257 |
| gates, `plain` | `nets_hier` | int8 | 15 | 0.83 ± 0.04 | 2.49 ± 0.27 | 0.373 | 0.420 |

(In `nets_map` the gate rows' k moves by under 1%: floats 1.045, `booth_tree` 1.003. The other netlists' maps were learned on one stream.)

| the floats' constants put on int8's 15 kinds (middle point) | merge | rms (W) | bias (W) | worst (W) | r |
|---|---|---:|---:|---:|---:|
| RTL counts both sides (Q132(b) read 2.215 and −1.813 on three-point means) | `nets_map` | 2.211 | −1.810 | 3.65 | 0.9935 |
| RTL counts both sides (Q132(b) read 1.867 and −1.528) | `nets_hier` | 1.863 | −1.524 | 3.07 | 0.9935 |
| **gate counts both sides, `booth_tree`** | `nets_hier` | **0.705** | **−0.641** | 1.28 | 0.9936 |
| gate counts both sides, `booth_tree` | `nets_map` | 0.664 | −0.601 | 1.24 | 0.9939 |
| gate counts both sides, `plain` | `nets_hier` | 0.575 | −0.213 | 0.81 | 0.9871 |
| gate counts both sides, `booth_swap` | `nets_hier` | 0.434 | −0.067 | 0.81 | 0.9947 |
| gate counts both sides, `booth` | `nets_hier` | 0.736 | −0.671 | 1.33 | 0.9936 |

At RTL the two units wanted different prices per net toggle: 1.88 and 3.74 fJ by Q132(b)'s primary merge, 2.36 and 3.90 fJ by `nets_hier`.
**At gate level the floats want 1.05 ± 0.01 fJ, and the two netlists that Booth-recode B want 1.01 ± 0.05 and 1.02 ± 0.05: the same, within
their errors** (0.8 and 0.6 combined standard errors from the floats). `booth_swap` (0.86 ± 0.02) and `plain` (0.83 ± 0.04) sit 8.5 and 4.6
below, so one price holds for Booth on B, not for every way of building the multiplier. **The clock constant does not converge**: int8's fits
want a = 2.16–2.49 fJ per clocked bit in every netlist, as at RTL (2.13), against the floats' 1.08 ± 0.01, 5.2–14.6 standard errors apart
(`merges.int8_vs_floats_gate_fit`). Carried over to int8, the
floats' two gate-level constants miss by **0.43–0.74 W rms (bias −0.07 to −0.67 W)**, according to the multiplier the tool builds. With RTL
counts on both sides the miss is **2.21 W rms (bias −1.81 W) in Q132(b)'s map** (1.86 W, −1.52 W in `nets_hier`). int8's own fits reach
0.24–0.37 W. The level of the count does not decide the floats' own fit: the RTL count fits them better in `nets_map` (0.352 against
0.386 W), and the gates do in `nets_hier` (0.391 against 0.409). What separates int8 from the floats sits in the clock term. That is a
reading: whatever else scales with int8's register clocking, the integer units' clock tree or the reads Q132(b) §14 names, is outside the
count. Nothing here is blind: every fit came after E78's data.

**The gate count alone does not make the best int8 model.** With the lane's operand bus priced apart (Q132(b)'s I3, in `nets_hier`) the RTL
count fits E78's int8 kinds at 0.168 W, the primary netlist at 0.253 W and `booth_swap` at 0.182 W (leave-one-out 0.231, 0.302, 0.205;
`model.arms.*.i3_int8_alone`). Under M2 (the table above; `model.arms.*.int8_alone.resid_w`), the primary netlist shrinks the dense kinds'
residuals (`smallint` −0.49 → −0.03 W, `ternary` −0.62 → +0.04, `pos` +0.42 → +0.03), the gated kinds keep the known shortfall (+0.20 to
+0.55 W, Q132(b) §6), and `full` is over-counted (−0.43 W). Under I3 the same three go −0.26 → +0.02, −0.23 → +0.12 and +0.07 → −0.05 W, the
gated kinds run +0.10 to +0.51 W, and `full` reads −0.42 W (`model.arms.*.i3_int8_alone.resid_w`).

**5. int8's single bits: the card's odd-and-even direction on B appears at gate level only when the Booth recoder sits on B, and larger than on the card.** E102
measured int8's B list on the rail (A = 1, one set of base bytes, 1,024 flips an op a bit). Its singles put the odd bits at 2.85× [1.89, 6.09]
the even bits (post hoc; E102 [`check_e102.txt`](../2026-11-01-e102-balanced-bit-prices/check_e102.txt)), its registered masks at 1.97×
[1.69, 2.33], and all eight bits flipped together at 0.63 [0.53, 0.77] of the singles. E79's A list (B = 1, 8,192 flips an op) is flat over
the magnitude bits, and its sign bit costs 1.85×. The table gives merged-net toggles in the unit per flipped bit, at the middle launch point,
in `nets_map` (the merge learned once on random data; these are regular streams, see Departures; `analysis.json` `bits`):

| list | count | bit 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (sign) | odd ÷ even | sign ÷ rest |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B | **card, rail fJ (E102)** | 20 | 61 | 29 | 60 | 19 | 72 | 41 | 76 | **2.85** | 1.77 |
| B | RTL | 5.2 | 5.1 | 5.1 | 5.2 | 5.1 | 5.2 | 5.2 | 27.1 | 1.01 | 5.25 |
| B | **gates, Booth on B (`booth_tree`)** | 8.0 | 93.3 | 20.0 | 72.6 | 24.9 | 67.4 | 24.7 | 127.2 | **4.42** | 2.86 |
| B | gates, Booth on A (`booth_swap`) | 8.5 | 9.4 | 10.9 | 14.4 | 17.5 | 17.6 | 17.4 | 140.0 | 1.12 | 10.24 |
| B | gates, no Booth (`plain`) | 9.7 | 11.4 | 13.4 | 15.4 | 13.8 | 18.5 | 15.7 | 163.5 | 1.22 | 11.69 |
| A | **card, board fJ (E79)** | 86 | 75 | 71 | 88 | 92 | 84 | 78 | 152 | **0.99** | 1.85 |
| A | RTL | 21.5 | 21.9 | 20.6 | 24.3 | 19.4 | 24.7 | 20.6 | 63.5 | 1.15 | 2.91 |
| A | **gates, Booth on B (`booth_tree`)** | 46.4 | 50.4 | 49.8 | 63.4 | 57.6 | 69.8 | 60.7 | 290.8 | **1.19** | 5.11 |
| A | gates, Booth on A (`booth_swap`) | 44.4 | 172.4 | 48.3 | 142.9 | 66.6 | 211.3 | 61.2 | 263.4 | 3.31 | 2.47 |
| A | gates, no Booth (`plain`) | 46.9 | 55.6 | 55.9 | 64.0 | 60.4 | 70.4 | 63.2 | 295.5 | 1.16 | 4.97 |

**Only the netlists that recode B have both lists' shapes**: odd bits dear on B, the magnitude bits level on A. Recoding A puts the
alternation on A, where the card has none; with no recoder there is none anywhere. **The direction is the card's; the amplitude is larger.**
On the primary netlist B's odd bits read 4.42× its even bits in `nets_map` and 4.15× in `nets_hier`, against the card's 2.85× [1.89, 6.09].
B's masks read 2.45 in `nets_map`, just above the card's registered 1.97 [1.69, 2.33], and 2.31, inside it, in `nets_hier`
(`bits.arms.booth_tree.b_shape_map`, `b_shape`). `nets_map` was chosen for single bits after both counts had been seen on these tiles
(Departures), so it is that choice that puts the masks outside the card's interval. All eight bits together read 0.59 of the singles in either
merge (card 0.63 [0.53, 0.77]), so flips share their cost here as on the card; the RTL count reads 1.00 and 0.97. The stage split puts B's
odd-bit excess in the multiplier (bit 5: 62.9 of 67.4; bit 4: 20.8 of 24.9). A radix-4 recoder reads overlapping three-bit windows of its
operand, so an odd bit enters two digits and an even bit one. That is E102's reading, which E102 could not test. It holds in both netlists
built that way (`booth_tree` 4.42, `booth` 4.32) and in no other. **This is post hoc**: both card lists were known before this ran, and nothing
about the chip's own multiplier is public.

**E102's undercount, priced.** A flip moves no clocked bit, so its price is k × nets. k was fitted on E78's board watts, so the like-for-like
comparison is with the card's board prices. At the floats' own gate-level price, 1.05 fJ per net toggle, the primary netlist's B flips
(bits 1–7) average **0.89× the card's board level**. The RTL count at Q132(b)'s own constant for these counts (1.87 fJ, `vpu_map`) gives 0.22×,
which matches E102's frozen bench list to within 2 fJ a bit (`bits.priced_at_one_k`). Against the rail, which k was not fitted on, the same
flips read 1.22× (RTL 0.33×). On the A list the gates give 1.01× the board level (1.21× the rail), and the RTL count 0.59× (0.71×). **The sign
bit stays about twice the card's**: B's bit 7 is 5.1× bit 6 in the count and 1.9× on the card, and A's sign bit prices at 306 fJ against
124 rail and 152 board. Yosys's Booth extends each partial product's sign, and a chip's multiplier need not.

**For the float unit, by contrast, the level of the count does not matter.** E102's fp32 and fp16 all-in B lists at six positions went
through the float netlist (`analysis.json` `float_gate.bits`; both levels in `nets_map`). The gate count per flip is 1.6–2.0× the RTL's.
Priced each at its own constant (gates 1.05 fJ, the RTL Q132(b)'s 1.87 fJ for map counts), the two agree within 13% at every position:
fp32 bits 0, 11, 16, 22 read 179, 240, 552, 684 fJ from gates and 203, 233, 551, 674 from the RTL; fp16 bits 0, 9 read 202, 415 and 206, 402.
The float RTL is structural, so its count is a fixed fraction of the gates' and the constant absorbs it. int8's RTL is not, and there the
gate count changes both the level and the shape.

**6. The multiplier is the tool's choice, and it moves the count by a fifth on random data and by up to half on others.** Four netlists of one
RTL (METHOD §1): 1,999 to 2,414 cells, 252 to 306 µm², the same 92 flip-flops. At the middle launch point a random MAC switches 173
(`booth`), 175 (`booth_tree`), 194 (`booth_swap`) or 206 (`plain`) merged nets, 1.19× from least to most. The same ratio is 1.35× on
`smallint`, 1.40× on `ternary`, 1.49× on `sparse50` (98.6 in `booth` to 146.9 in `booth_swap`) and 1.55× on `sparse90` (`tables.md`;
`analysis.json` `kinds`). `booth`, Booth on B without the carry-save trees, sits within about 2% of `booth_tree` on every kind, fit and single
bit (`full` 172.9; B's odd over even 4.32; int8 alone 0.259 W): the sums' structure hardly matters, while the recoder and its operand do.
**The two lines of evidence point at different operands.** The single-bit shapes fit only the recoder on B. E78's kind-level watts fit
`booth_swap` best (cross-format bias −0.07 W, rms 0.43 W; int8 alone 0.238 W), though its price per net toggle, 0.86 ± 0.02 fJ, is not the
floats'. Neither test was registered, and the kinds were not designed to tell the operands apart.

## What was asked and what was done

Asked (Q133's brief, item 12): synthesize `tima_top` with the open flow on the Intel (`nice -n 10`, at most 6 cores), run the int8 kinds
through the netlist at zero delay, and give per-kind and per-bit toggle counts comparable with fp32's and fp16's in the `nets_hier`
convention. Done: all of that, and the float unit through the same flow and bench, so that "comparable" is gate against gate, kind for kind,
and for six float single-bit tiles. Partial where METHOD.md §5 says so.

**Departures, all decided before reading the counts they touch unless marked.**
- **The open flow's `setup.sh` fetches Linux builds only** (oss-cad-suite linux-x64, micromamba linux-64, OpenROAD linux-64). On this Mac:
  oss-cad-suite's darwin-x64 build of the same release ([`setup_darwin.sh`](../../../../tools/open-flow/tima/setup_darwin.sh)), which carries
  the same Yosys sha; OpenROAD not used, since a zero-delay toggle count needs no placement or routing. **The same Yosys on another platform
  maps 0.15% of `txfma_top`'s cells differently** (16,063 against the published 16,087; flip-flops and latches identical), so a count here can
  differ from a Linux run by about that.
- **Four netlists, not one**, because the RTL does not fix the multiplier (METHOD §1). The primary, `booth_tree`, was chosen when the arms
  were built, and it was built and run first. The choice was not registered, and no timestamped record shows it came before the counts
  (corrected after verification; it read "named first").
- **Scope cut for time**, because the machine was shared with other lanes' benches. The load average was not logged: by the lane's reading it
  was 30–150 through the runs (11:21 to 12:06 PST), and about 40–75 at 11:16, before them (`versions.txt`). So there are three launch
  points only for the primary arm's kinds; the single bits, the other arms and the float unit ran at the middle point. E79's `jg` B list
  (`b8_*`, which measured nothing on the card), `b8p_6`, `b8m2`, `b8m4` and `z8` were not run. The other arms' maps were learned on one
  stream, so their `nets_map` is quoted only for single bits, with that caveat.
- **Single bits are quoted in `nets_map`, with `nets_hier` beside it in `analysis.json`** (decided after seeing both on the primary arm's
  tiles). These are regular streams, and `nets_hier` folds a fan-out of nets that switch in step into one ancestor-scope name, as Q132(b) §4
  found on E92's tiles. On the primary netlist's A list it reads a third low (magnitude bits 29–41 against 46–70 a flip, the sign bit 178
  against 291). On its B list the two agree within two toggles a flip, but the choice still moves B's odd over even from 4.15 to 4.42, and its
  masks from 2.31, inside the card's interval, to 2.45, just above it (result 5). On int8's dense random kinds the two agree within 0.1%
  (1.2% on `pos` and `highbit`), and on the float unit's dense kinds within 0.06% (0.2–0.9% on its sparse ones; `analysis.json` `merges`).
  This was corrected after verification; it read "on every random kind".
- **Kinds and fits are quoted in `nets_hier`, the brief's convention, and every RTL-side number also in Q132(b)'s primary, `nets_map`**
  (added after verification). Q132(b) §4 made `nets_map` primary because `nets_hier` folds same-waveform fan-out on regular streams. The RTL
  side's `nets_map` is Q132(b)'s committed counts and trained map, never the control's one-stream map. At gate level the merges agree within
  0.2% on random data (fp32 and fp16 `randn`, int8 `full`) and move the fits' k by under 1%. On the RTL side they do not (results 3 and 4;
  `analysis.json` `merges`; `tables.md`, "Both merges").
- **The register term of every fit takes the unit's clocked bits from the RTL run of the same tile**: in a gate run the unit's flip-flops are
  cells and do not report to the accounting.
- The runs used frozen copies of `run_arm.sh` that differ from the committed file only in the summary line's count of finished tiles.

## What this cannot say

- **A netlist from an open 7 nm library, not the chip's.** ASAP7 is predictive, and the ET-SoC-1's own flow and multiplier are not public.
  Which architecture silicon has is not shown; result 6 says the evidence here points two ways.
- **Zero delay: no glitches.** Q129 measured about 1.5× more toggles in the float multiplier's tree with delays; nothing here prices that
  for int8, and a Booth array summing random signs is the kind of logic that glitches.
- **Toggle counts, not energy.** k is a fitting constant per merged net toggle at 600 MHz on one card, not the energy of a wire, and the
  fits came after E78's data. Which count predicts the card better depends on the model's form (result 4).
- **At RTL the merge matters**: by `nets_map` the RTL undercount and the RTL constants are smaller than by `nets_hier` (results 3 and 4), so
  an RTL number from this README is quoted with its merge.
- **The float netlist has no stage split**, and the units' register accounting is the RTL's.
- **The sign bit is over-priced by these netlists** relative to the card on both sides (result 5).

## Section 11, item 12, and what a reader can be told

- **Item 12 narrows; it does not close.** int8 now has gate-level counts per kind and per bit in the bench's convention, from an open
  netlist, beside fp32 and fp16 counted the same way. The single flips are no longer undercounted on B (0.89× the card's board level, against
  the RTL count's 0.22×), though the odd bits' excess is larger than the card's. Open: which multiplier the chip has (the counts depend on it,
  and the two lines of evidence here disagree), glitches, the sign bit's price, and the clock term that still separates int8 from the floats.
- **Item 6** (a model across kinds): at gate level the floats and the netlists that Booth-recode B want the same price per net toggle (1.05
  and 1.01 fJ). The other netlists want 0.83–0.86 fJ, and int8's clock constant stays about twice the floats'. Carried across formats, the
  miss falls from 2.21 W rms, bias −1.81 W (RTL counts in Q132(b)'s map; 1.86 W, −1.52 W in `nets_hier`), to 0.43–0.74 W rms, bias −0.07 to
  −0.67 W. An int8 model with the bus priced apart still fits better on the RTL count.
- **Item 11** (int8 zeros' extra 0.61 W): not addressed here; result 4's clock term points the same way as Q132(b) §14, a reading.

**For the blog, each from a committed file:**

- In the public RTL an int8 multiply is one line, `a * b`, so a simulation of it has no wires inside to count. Mapped to gates with open
  tools, a random int8 multiply-add switches about 175–205 nets, depending on how the tool builds the multiplier. That is five to six times
  what the RTL simulation counts, and about 80% of them are in the multiplier (`analysis.json` `kinds.full`).
- Counted the same way at gate level, in one bench, a random fp32 multiply-add switches about 3,400 nets, fp16 about 1,370 and int8 about
  175–205: sixteen to twenty times fewer for int8 than fp32, and seven to eight times fewer than fp16 (`analysis.json` `float_gate`,
  `kinds.full`).
- Simulating the float unit's own RTL misses about half of the switching nets an open 7 nm netlist of it has, in both formats: 46–47% by
  the bench's primary merge, 58% by the older one (`analysis.json` `merges.float_unit`).
- At gate level one price per switching net, about 1 fJ at 600 MHz, fits the float unit's watts (1.05 fJ) and the integer unit's when its
  multiplier Booth-recodes B (1.01 fJ). Built other ways, the multiplier wants 0.83–0.86 fJ, and int8's price per clocked register bit
  stays about twice the floats'. At RTL the two units needed 1.9 and 3.7 fJ by the bench's primary merge (2.4 and 3.9 by the older one).
  Carrying the float unit's two constants over to int8 then misses by 0.4–0.7 W rms (bias −0.07 to −0.67 W), depending on how the
  multiplier is built, instead of 2.2 W rms (bias −1.8 W; 1.9 W and −1.5 W by the older merge). These are fitted constants, not the energy
  of a wire (`analysis.json` `merges.m2`, `model`, `float_gate.cross_format`).
- Counted as gates, the int8 kinds rank as the card ranks them (ρ = 0.96 over seven dense kinds, against 0.82 for the RTL count)
  (`analysis.json` `rank_vs_card`).
- On the card, flipping an odd bit of int8's B operand costs two to three times an even bit. A gate-level multiplier shows the same direction
  only when it Booth-recodes B, which reads overlapping three-bit windows, so an odd bit enters two of them. It then shows it larger than the
  card does (4.4× against 2.85×). With the recoder on A, or without one, the pattern is absent (`analysis.json` `bits`). This is post hoc,
  and silicon's multiplier is not public.
- Priced at the same 1 fJ per net, int8's single B-bit flips come out at about 0.9× the card's board-level price, where the RTL count gave
  about 0.2×. The sign bit comes out about twice the card's (`analysis.json` `bits.priced_at_one_k`).
- For the float unit it makes no difference whether one counts the RTL or the gates, as long as each count gets its own price: single-bit
  prices from the two agree within 13%. For int8 it does, because its RTL multiply is one line (`analysis.json` `float_gate.bits`).

**Any of this is one open 7 nm netlist of the public RTL's later revision (Erbium), at zero delay, not the ET-SoC-1's own gates.**

## Files

| file | what |
|---|---|
| `README.md`, `METHOD.md`, `tables.md` | this, the method, the generated tables |
| `analysis.json`, `analyze.py` | every number above: the control, per kind, per bit, the fits with their jackknife errors, the float comparison, the ranks, and both merges side by side (`merges`) |
| `runs/<arm>/counts_kinds.json`, `counts_bits.json` | `run_kinds.py`'s output for `booth_tree`, `plain`, `booth_swap`, `booth`, the RTL control (`rtl`) and the float netlist (`f_txfma_flat`, three batches merged, and its single bits) |
| `netlists/` | the rewritten netlists (gzipped), the stage maps, the cell statistics, the yosys scripts, `sha256.txt`, `recoded_operand.txt` |
| `versions.txt` | tools, shas, host |

```
SCRATCH=<dir> bash tools/open-flow/tima/setup_darwin.sh && bash tools/open-flow/tima/synth_tima.sh && bash tools/open-flow/tima/synth_txfma_flat.sh
# cell models and rewrites: tools/open-flow/tima/README.md; build and run: rtl-sim/tima_gate/README.md
python3 analyze.py        # in this directory, with numpy
```

## Corrections after verification

*Sun 1 Nov 2026, against `5f48e866`, from an independent verifier's read. It reproduced `analysis.json` and `tables.md` byte for byte, and
every raw count; none of its faults needed a new run. **No run, count or data file changed.** `analyze.py` now also writes both merges
(`merges`), a jackknife error on every fit, how far each int8 netlist's constants sit from the floats', each kind's launch-point values and
the fp32 and fp16 ratios to int8 for every netlist. Every value it wrote before is unchanged: 3,923 of 3,923, and
`merges.self_check_max_abs_diff` is 0. Wrong sentences are replaced above. METHOD §1, §4 and §5 and `versions.txt` are corrected to match.*

| | what was wrong | what it says now |
|---|---|---|
| C1 | Every RTL-side number was `nets_hier`, the merge Q132(b) §4 demoted for regular streams, and nothing said so. Q132(b), the hub and the kinds page quote Q132(b)'s primary, `nets_map`, which gives different RTL numbers. | Each RTL-side number names its merge, with `nets_map` beside it. The float RTL count is 1.9× low (2.4× by `nets_hier`) and misses 46–47% (58%). The RTL constants are 1.88 and 3.74 fJ (2.36, 3.90). The RTL cross-format miss is 2.21 W rms, bias −1.81 W (1.86, −1.52). The gate side's k moves under 1%, so the conclusions stand, and by the map the improvement is larger. The README's "within 0.1% on every random kind" for the gate side's two merges is replaced by the per-kind figures. |
| C2 | "One price per net toggle serves both units" held only for the netlists that recode B. The headline dropped the clock term, and "misses by 0.1–0.7 W" was the bias. | Floats 1.05 ± 0.01 fJ; Booth on B 1.01 ± 0.05 and 1.02 ± 0.05; `booth_swap` 0.86 ± 0.02 and `plain` 0.83 ± 0.04, 8.5 and 4.6 standard errors below. int8's clock constant is 2.16–2.49 against the floats' 1.08 in every netlist, 5.2–14.6 standard errors apart (the verifier's "at least 6" holds for all but `plain`). The miss is given as 0.43–0.74 W rms, with the bias beside it. |
| C3 | The odd/even shape "appears", but it is larger than the card's, and the post hoc choice of `nets_map` moved the masks from inside the card's interval to outside it. The card's interval on the singles was missing. | 4.42× (4.15× in `nets_hier`) against the card's 2.85× [1.89, 6.09]. The masks read 2.45 in `nets_map`, above [1.69, 2.33], and 2.31, inside it, in `nets_hier`. |
| C4 | B-flip pricing led with the rail (1.22×), but k is fitted on board watts. | 0.89× the card's board level leads; the rail ratio is a side note. |
| C5 | The I3 paragraph quoted M2's residuals, and its `full` −0.42 W was I3's. | M2's residuals are labelled as M2's (`full` −0.43 W), and I3's own are quoted beside them. |
| C6 | "Named before any count was set beside a card" had no timestamped record. | Chosen when the arms were built, not registered, with no timestamped record. |
| C7 | The blog's int8 count was the primary netlist's alone. | 175–205 nets; 16.5–19.6× and 6.7–7.9× across the netlists. |
| C8 | Slips. The work ran "to about 13:00", but the commit is 12:09:43 and the last run ended 12:06. The load was 30–150 here and 40–75 in `versions.txt`, and neither was logged. "1.19× from least to most" named `booth_tree` as the least, and `sparse50` read "(99.9 to 146.9)". | 10:43 to 12:09. The load is stated as unlogged, with each reading's time. `booth`'s 172.9 is the least (1.19×), and `sparse50` runs 98.6 to 146.9 (1.49×). |
