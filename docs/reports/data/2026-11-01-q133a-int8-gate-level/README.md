# Q133(a): int8's multiply-add at gate level, beside fp32 and fp16 in one bench

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 12, "int8 at gate level" (the list at `1fe8377a18af`): "int8's multiply is behavioural in the public RTL, so its counts below the multiply-add are not comparable and the bench undercounts its single flips ([Q132(b)](../2026-11-01-q132-rtl-bench/README.md), [E102](../2026-11-01-e102-balanced-bit-prices/README.md)). A gate-level count of `tima_top` would give them."*

*Sun 1 Nov 2026 (week 44), Q133, desk work on a desk machine shared with other lanes' benches, 10:43 to about 13:00 PST. **No card was opened and nothing was measured in watts here**: every watt below is a committed experiment's (E78, E79, E102), named where it is used. The int8 unit, `tima_top`, and for comparison the float unit, `txfma_top`, were synthesized with the open flow (Yosys `33177a407` with the slang frontend, ASAP7 RVT TT, the open flow's own recipe) and run, in place of their RTL, in Q132(b)'s whole-`vpu_top` bench (Verilator 5.052, `-fno-dfg`), counted by that bench's own counter. How: [METHOD.md](METHOD.md). Code: [`tools/open-flow/tima/`](../../../../tools/open-flow/tima/), [`rtl-sim/tima_gate/`](../../../../rtl-sim/tima_gate/). Versions: [`versions.txt`](versions.txt). Every number is in [`analysis.json`](analysis.json), written by [`analyze.py`](analyze.py) from the committed counts; [`tables.md`](tables.md) is generated from it.*

## Results

**1. As gates, a random int8 multiply-add switches 175 merged nets, five times what the RTL bench counts, and the multiplier is most of it.**
On `int8.full` the primary netlist (radix-4 Booth on B with carry-save sums, `booth_tree`, named primary before any count was set beside a
card) switches **175.0 merged nets per MAC** in the unit, where the RTL bench counts 35.6 (`nets_hier`, mean of three launch points;
`runs/booth_tree/counts_kinds.json`, `analysis.json` `kinds.full`). The stage the behavioural `*` hid, the four 9×9 products and their sum, goes
from **17.2 to 139.0** (8.1×); the operand registers and their enable multiplexers from 10.2 to 15.2; the add of C and the result from 8.1 to 20.4.
All 16 int8 kinds at three launch points, 48 tile-points, pass the bench's check: **0 of 256 accumulator words wrong** in every one, and no X.

| per MAC, in the unit | `full` | `gauss_q` | `sorted` | `pos` | `smallint` | `ternary` | `sparse50` | `wsparse50` | `highbit` | `sparse90` | `ones` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RTL (Q132(b)) | 35.6 | 35.6 | 31.5 | 27.7 | 35.3 | 29.9 | 26.8 | 16.7 | 12.9 | 6.6 | 0.1 |
| **gates, `booth_tree`** | **175.0** | **147.7** | **152.9** | **133.0** | **131.4** | **103.9** | **99.8** | **63.5** | **43.6** | **15.3** | **0.3** |
| × RTL | 4.91 | 4.15 | 4.86 | 4.81 | 3.72 | 3.47 | 3.72 | 3.80 | 3.38 | 2.34 | 2.7 |

**At gate level the kinds fall in the card's order.** E78 measures, in watts over int8's zeros, `full` 7.06, `gauss_q` 6.60, `sorted` 6.59,
`pos` 6.17, `smallint` 6.00, `ternary` 5.19, `highbit` 3.23. Over those seven dense kinds Spearman's ρ between the card and the count is
**0.964 for every netlist, against 0.821 for the RTL count** (all 15 non-zero kinds: 0.921–0.925 against 0.882; `analysis.json`
`rank_vs_card`). The RTL put `smallint` level with `full` (0.99 of it), because a behavioural product has no partial products to stay quiet;
the primary netlist puts it at 0.75 and the card at 0.85.

**2. The control: Q132(b)'s bench, rebuilt here, reproduces its committed counts exactly.** 16 tile-points (`full`, `gauss_q`, `ones`,
`zeros` at three launch points; `hq`, `bk_5`, `a8q`, `a8_7` at the middle one): every unit and whole-VPU `nets_hier`, register bit clocked
and changed, and valid slot equals `counts-v2.json`, `counts-e102.json` or `counts-hlp.json` to the unit, with 0 words wrong
(`analysis.json` `control`). So everything below differs from Q132(b) by the netlist alone.

**3. All three formats at gate level, in one bench, from one flow.** With the float unit's netlist in place of its RTL (`txfma_top`, 16,063
cells; all 35 fp32 and fp16 kinds of Q132(b) at the middle launch point, every one with 0 words wrong; `runs/f_txfma_flat/counts_kinds.json`,
`analysis.json` `float_gate`):

| per MAC, random data, in the unit | fp32 `randn` | fp16 `randn` | int8 `full` |
|---|---:|---:|---:|
| RTL bench, `nets_hier` (Q132(b), the same point) | 1,427.0 | 579.1 | 35.7 |
| **gates, this bench, `nets_hier`** | **3,386.5** | **1,368.2** | **175.0** (three points: 175.0) |
| gates ÷ RTL | 2.37 | 2.36 | 4.91 |
| cells (one lane holds one float unit and two int8 units) | 16,063 | 16,063 | 2 × 2,019 |

**The float unit's RTL count is about 2.4× low in both formats (median 2.47 over the 29 kinds whose lanes multiply, 2.29–3.32 on those
that carry varying data), and int8's was 3.4–4.9× low on its dense kinds**: the float multiplier is written out structurally in the RTL and int8's is not. Q126's open netlist
counted 3,299 for fp32 on another stream and bench ([open netlist](../2026-10-26-open-netlist/POWER.md)), 3% from this. **At gate level a
random MAC switches 19× as many nets in fp32 as in int8, and 7.8× in fp16**; per TensorFMA op (4,096, 8,192 and 16,384 MACs) that is
13.9 M, 11.2 M and 2.9 M.

**4. One price per net toggle serves both units at gate level, and the cross-format miss shrinks to the size of the architecture
question.** D = rate × (k × nets toggled in the VPU + a × register bits clocked), each over the type's zeros, on E78's measured watts (the
bench's model M2, `nets_hier`; `analysis.json` `model`, `float_gate.cross_format`):

| counts | fitted on | n | k, fJ per net toggle | a, fJ per clocked bit | rms (W) | leave-one-out (W) |
|---|---|---:|---:|---:|---:|---:|
| RTL | fp32 + fp16 | 33 | 2.36 | 1.12 | 0.409 | 0.437 |
| **gates** | fp32 + fp16 | 33 | **1.05** | 1.08 | **0.391** | 0.405 |
| RTL | int8 | 15 | 3.90 | 2.13 | 0.276 | 0.315 |
| **gates, `booth_tree`** | int8 | 15 | **1.01** | 2.38 | **0.259** | 0.295 |
| gates, `booth_swap` / `plain` | int8 | 15 | 0.86 / 0.83 | 2.16 / 2.49 | 0.238 / 0.373 | 0.257 / 0.420 |

| the floats' constants put on int8's 15 kinds | rms (W) | bias (W) | worst (W) | r |
|---|---:|---:|---:|---:|
| RTL counts both sides (Q132(b) read 1.867 and −1.528 on three-point means) | 1.863 | −1.524 | 3.07 | 0.9935 |
| **gate counts both sides, `booth_tree`** | **0.705** | **−0.641** | 1.28 | 0.9936 |
| gate counts both sides, `plain` | 0.575 | −0.213 | 0.81 | 0.9871 |
| gate counts both sides, `booth_swap` | 0.434 | −0.067 | 0.81 | 0.9947 |
| gate counts both sides, `booth` | 0.736 | −0.671 | 1.33 | 0.9936 |

At RTL the two units wanted different prices per net toggle, 2.36 and 3.90 fJ; **at gate level they want the same one, 1.05 and 1.01 fJ**,
and the floats' constants carried over to int8 miss by −0.07 to −0.67 W according to the multiplier the tool builds, where the RTL counts
missed by −1.52 W. What remains sits in the clock term: int8's own fits want a = 2.1–2.5 fJ per clocked bit at both levels, the floats 1.1
(a reading: whatever else scales with int8's register clocking, the integer units' clock tree or the reads Q132(b) §14 names, is outside
the count). Nothing here is blind: every fit came after E78's data.

**The gate count alone does not make the best int8 model.** With the lane's operand bus priced apart (Q132(b)'s I3, in `nets_hier`) the RTL
count fits E78's int8 kinds at 0.168 W, the primary netlist at 0.253 W and `booth_swap` at 0.182 W (leave-one-out 0.231, 0.302, 0.205;
`model.arms.*.i3_int8_alone`). On the primary netlist the dense kinds' residuals shrink (`smallint` −0.49 → −0.03 W, `ternary` −0.62 → +0.04,
`pos` +0.42 → +0.03), the gated kinds keep the known shortfall (+0.2 to +0.55 W, Q132(b) §6), and `full` is over-counted (−0.42 W).

**5. int8's single bits: the card's odd-and-even shape on B appears at gate level, and only when the Booth recoder sits on B.** E102
measured int8's B list on the rail (A = 1, one set of base bytes, 1,024 flips an op a bit): odd bits 2.85× even bits, its registered masks
1.97× [1.69, 2.33], all eight bits flipped together 0.63 [0.53, 0.77] of the singles. E79's A list (B = 1, 8,192 flips an op) is flat over
the magnitude bits and its sign bit costs 1.85×. Merged-net toggles in the unit per flipped bit, at the middle launch point, in `nets_map`
(the merge learned once on random data; these are regular streams, see Departures; `analysis.json` `bits`):

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

**Only the netlist that recodes B has both lists' shapes**: odd bits dear on B, the magnitude bits level on A. Recoding A puts the
alternation on A, where the card has none; with no recoder there is none anywhere. On the primary netlist B's masks read 2.45 (card 1.97
[1.69, 2.33]), and all eight bits together 0.59 of the singles (card 0.63 [0.53, 0.77]), so flips share their cost here as on the card;
the RTL count reads 1.00 and 0.97. The stage split puts B's odd-bit excess in the multiplier (bit 5: 62.9 of 67.4; bit 4: 20.8 of 24.9):
a radix-4 recoder reads overlapping three-bit windows of its operand, so an odd bit enters two digits and an even bit one. That is E102's
reading, which E102 could not test, and it holds in both netlists built that way (`booth_tree` 4.42, `booth` 4.32) and in no other. **This
is post hoc**: both card lists
were known before this ran, and nothing about the chip's own multiplier is public.

**E102's undercount, priced.** A flip moves no clocked bit, so its price is k × nets. At the floats' own gate-level price, 1.05 fJ per net
toggle, the primary netlist's B flips average **1.22× the card's rail level and 0.89× its board level** (bits 1–7); the RTL count at
Q132(b)'s own constant for these counts (1.87 fJ, `vpu_map`) gives 0.33× and 0.22×, E102's frozen bench list to within 2 fJ a bit
(`bits.priced_at_one_k`). The A list: gates 1.21× rail and 1.01× board, RTL 0.71× and 0.59×. **The sign bit stays about twice the card's**:
B's bit 7 is 5.1× bit 6 in the count and 1.9× on the card; A's sign bit prices at 306 fJ against 124 rail and 152 board. Yosys's Booth
extends each partial product's sign, and a chip's multiplier need not.

**For the float unit, by contrast, the level of the count does not matter.** E102's fp32 and fp16 all-in B lists at six positions, through
the float netlist (`analysis.json` `float_gate.bits`, in `nets_map`): the gate count per flip is 1.6–2.0× the RTL's, and priced each at its
own constant the two agree within 13% at every position (fp32 bits 0, 11, 16, 22: 179, 240, 552, 684 fJ from gates, 203, 233, 551, 674 from
the RTL; fp16 bits 0, 9: 202, 415 and 206, 402). The float RTL is structural, so its count is a fixed fraction of the gates' and the constant
absorbs it. int8's RTL is not, and there the gate count changes both the level and the shape.

**6. The multiplier is the tool's choice, and it moves the count by a fifth on random data and by up to half on others.** Four netlists of one
RTL (METHOD §1): 1,999 to 2,414 cells, 252 to 306 µm², the same 92 flip-flops. At the middle launch point a random MAC switches 175
(`booth_tree`), 194 (`booth_swap`) or 206 (`plain`) merged nets, 1.19× from least to most; `smallint` 1.35×, `ternary` 1.40×, `sparse50`
1.49× (99.9 to 146.9), `sparse90` 1.55× (`tables.md`; `analysis.json` `kinds`). `booth`, Booth on B without the carry-save trees, sits within 1–2% of `booth_tree` on every kind, fit
and single bit (`full` 172.9; B's odd over even 4.32; int8 alone 0.259 W): the sums' structure hardly matters, the recoder and its operand
do. **The two lines of evidence point at different operands**: the single-bit shapes fit only the
recoder on B, while E78's kind-level watts fit `booth_swap` best (cross-format bias −0.07 W, int8 alone 0.238 W). Neither was registered,
and the kinds were not designed to tell the operands apart.

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
- **Four netlists, not one**, because the RTL does not fix the multiplier (METHOD §1). The primary was named first.
- **Scope cut for time**, because the machine was shared with other lanes' benches (load average 30–150 through the runs): three launch
  points only for the primary arm's kinds; the single bits, the other arms and the float unit at the middle point; E79's `jg` B list (`b8_*`,
  which measured nothing on the card), `b8p_6`, `b8m2`, `b8m4` and `z8` not run. The other arms' maps were learned on one stream, so their
  `nets_map` is quoted only for single bits and with that caveat.
- **Single bits are quoted in `nets_map`, with `nets_hier` beside it in `analysis.json`** (decided after seeing both on the primary arm's
  tiles). These are regular streams, and `nets_hier` folds a fan-out of nets that switch in step into one ancestor-scope name, as Q132(b) §4
  found on E92's tiles: on the primary netlist's A list it reads a third low (magnitude bits 29–41 against 46–70 a flip, the sign bit 178
  against 291); on its B list the two agree within two toggles a flip. On every random kind they agree within 0.1%.
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
- **The float netlist has no stage split**, and the units' register accounting is the RTL's.
- **The sign bit is over-priced by these netlists** relative to the card on both sides (result 5).

## Section 11, item 12, and what a reader can be told

- **Item 12 narrows; it does not close.** int8 now has gate-level counts per kind and per bit in the bench's convention, from an open
  netlist, beside fp32 and fp16 counted the same way, and the single flips are no longer undercounted on B. Open: which multiplier the chip
  has (the counts depend on it, and the two lines of evidence here disagree), glitches, the sign bit's price, and the clock term that still
  separates int8 from the floats.
- **Item 6** (a model across kinds): one price per net toggle serves both units at gate level, and carried across formats the bias falls
  from −1.52 W to −0.07 to −0.67 W; an int8 model with the bus priced apart still fits better on the RTL count.
- **Item 11** (int8 zeros' extra 0.61 W): not addressed here; result 4's clock term points the same way as Q132(b) §14, a reading.

**For the blog, each from a committed file:**

- In the public RTL an int8 multiply is one line, `a * b`, so a simulation of it has no wires inside to count. Mapped to gates with open
  tools, a random int8 multiply-add switches about 175 nets, five times what the RTL simulation counts, and about 80% of them are in the
  multiplier (`analysis.json` `kinds.full`).
- Counted the same way at gate level, in one bench, a random fp32 multiply-add switches about 3,400 nets, fp16 about 1,370 and int8
  about 175: nineteen and eight times fewer for int8 (`analysis.json` `float_gate`, `kinds.full`).
- Simulating the float unit's own RTL misses about 60% of its switching nets, in both formats (`analysis.json` `float_gate.kinds`).
- At gate level one price per switching net, about 1 fJ at 600 MHz, fits the float unit's and the integer unit's watts, where the RTL counts
  needed 2.4 and 3.9 fJ. Carrying the float unit's two constants over to int8 then misses by 0.1–0.7 W instead of 1.5 W, depending on how the
  multiplier is built (`analysis.json` `float_gate.cross_format`, `model`). A fitted constant, not the energy of a wire.
- Counted as gates, the int8 kinds rank as the card ranks them (ρ = 0.96 over seven dense kinds, against 0.82 for the RTL count)
  (`analysis.json` `rank_vs_card`).
- On the card, flipping an odd bit of int8's B operand costs two to three times an even bit. A gate-level multiplier shows that only when it
  Booth-recodes B, which reads overlapping three-bit windows, so an odd bit enters two of them; with the recoder on A or without one, the
  pattern is absent (`analysis.json` `bits`). Post hoc, and silicon's multiplier is not public.
- Priced at the same 1 fJ per net, int8's single B-bit flips come out at 0.9–1.2× the card's level, where the RTL count gave 0.2–0.3×; the
  sign bit comes out about twice the card's (`analysis.json` `bits.priced_at_one_k`).
- For the float unit it makes no difference whether one counts the RTL or the gates, as long as each count gets its own price: single-bit
  prices from the two agree within 13%. For int8 it does, because its RTL multiply is one line (`analysis.json` `float_gate.bits`).

**Any of this is one open 7 nm netlist of the public RTL's later revision (Erbium), at zero delay, not the ET-SoC-1's own gates.**

## Files

| file | what |
|---|---|
| `README.md`, `METHOD.md`, `tables.md` | this, the method, the generated tables |
| `analysis.json`, `analyze.py` | every number above: the control, per kind, per bit, the fits, the float comparison, the ranks |
| `runs/<arm>/counts_kinds.json`, `counts_bits.json` | `run_kinds.py`'s output for `booth_tree`, `plain`, `booth_swap`, `booth`, the RTL control (`rtl`) and the float netlist (`f_txfma_flat`, three batches merged, and its single bits) |
| `netlists/` | the rewritten netlists (gzipped), the stage maps, the cell statistics, the yosys scripts, `sha256.txt`, `recoded_operand.txt` |
| `versions.txt` | tools, shas, host |

```
SCRATCH=<dir> bash tools/open-flow/tima/setup_darwin.sh && bash tools/open-flow/tima/synth_tima.sh && bash tools/open-flow/tima/synth_txfma_flat.sh
# cell models and rewrites: tools/open-flow/tima/README.md; build and run: rtl-sim/tima_gate/README.md
python3 analyze.py        # in this directory, with numpy
```
