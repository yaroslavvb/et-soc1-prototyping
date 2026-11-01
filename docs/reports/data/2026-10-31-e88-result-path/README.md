# E88 — what the result path costs against the operand bits (Q130, aifoundry1 card 1, 2026-10-31)

*Dated 1 Nov 2026: where a random sign's cost goes, which this left open, is taken up by [E92](../2026-11-01-e92-sign-split/README.md), [E104](../2026-11-01-e104-c-readback/README.md) and [E106](../2026-11-01-e106-held-signs/README.md). The adder alternating is a real cost and not most of the step; on one card a held tile keeps a bracket, 0.19–0.45 in fp16 and about 0.35–0.56 in fp32.*

*Pre-registered in [`tools/claims-v3/rpath/E88.md`](../../../../tools/claims-v3/rpath/E88.md) with
[`predictions-e88.json`](../../../../tools/claims-v3/rpath/predictions-e88.json), commit **`3dd99088`** (18:53:19 PDT),
1 min 14 s before the card was claimed in `#community-lab` (18:54:33 PDT, message `1566269185057751163`, "using
aifoundry1 card 1 for 1 h, until ~20:00 PDT"). Card session **18:54:48–19:32:22 PDT** on **aifoundry1 card 1 only**
(`V3_DEVICE=1`, its own lock): the smoke 8801 (18:54:48–18:55:29), six passes 8810–8815 (18:55:43–19:31:48; the
queue's budget rule stopped before 8816) and a closing read-only `ettelem config` (65 W / 65 °C, 600 MHz, 499 mV, as
at every pass's two ends). **37.6 card-minutes of the 45 registered.** No knob was written, no `--reset-ms`, no reset.
**Released at 19:37 PDT** by an edit of the same post, about 30 s after this directory's first commit (`f1c7412e`),
read back as `<ai> Claude says: using aifoundry1 card 1 for 1 h, until ~20:00 PDT doc — released (edited)`.*

*Corrected after verification the same evening, at the desk, with no card touched and nothing re-run: see
[Corrections after verification](#corrections-after-verification-sat-31-oct-2026) and
[`corrections-check.txt`](corrections-check.txt). The frozen outputs (`e88*.json`, `scored.json`, `results.md`) are
byte-identical to the data commit `f1c7412e`, and no registered verdict changed. One statement misled and is replaced:
the split was quoted as "a random multiply-add", but its fp32 design has positive operands and its fp16 and int8
designs pair their values; E78's random tiles are not split (C1).*

> **What this is.** Thirteen operand tiles that freeze a multiply-add's result while its operands keep moving
> (fp32: a 2^100 product at k = 0 absorbs every later product; fp16 and int8: each micro-op's dot product cancels
> exactly), or walk it with the same operands, beside each type's zeros, random data and ones. Paired within each
> pass, they split the board's switching power for a random-operand multiply-add into **(i) the lane being
> clocked**, **(ii) the result path** and **(iii) the operand-side multiplier**, in three formats, at 600 MHz, in
> E78's frame with E78's runner and reduction unchanged. The random operands are designed ones, not E78's random
> tiles: fp32's are positive (|N(0,1)|), and fp16's and int8's repeat each A value in a pair and pair each B value
> with the negation of an independent one, so that a dot product can be made to cancel.

## Results

**Five of six passes kept, 176 of 212 runs; registered tally 29 pass, 3 fail, 0 inconclusive** (13 mechanism rules,
19 model bands; [`scored.json`](scored.json) `primary.tally`). Pass 8813 is set aside by E78's zero-anchor gate (its
`fp16.zeros` departs −0.297 W from its straight line, limit 0.25 W; [`e88.json`](e88.json) `passes_set_aside`). Four
zeros runs were skipped before launch by E78's launch-reading rule (the die read 59 °C after the quiet wait;
`aifoundry1-c1/rpath/p88*/run.log`). Every kept run: 600 MHz, 498.7 mV, 546.001 / 546.001 / 318.000 cycles per op,
duty 0.9958–0.9964 ([`e88.json`](e88.json) `clock_mhz`, `v_mean`, `cycles_per_op`, `checks.duty`); idle 33.053 ±
0.011 W; leakage slope 0.315 W/°C (`auto`, 143 runs). E88's anchors replicate E82 on the same card within 0.7% for
random data (fp32 `randn` 23.82 against 23.99 W, fp16 21.31 / 21.44, int8 `full` 6.82 / 6.87; `e88.json` `items.*.D`
against E82's `e82.json`).

**1. The split.** Board switching power over the type's zeros (D, the board meter's reading), paired per pass, 95%
intervals over the five kept passes (statistical only: the leakage-slope arms move the watts by more, below); pJ per
MAC through each pass's measured rate ([`scored.json`](scored.json) `primary.splits`):

| random-operand design, result walking | (i) the lane clocked | (iii) operand-side multiplier | (ii) the result path | total |
|---|---|---|---|---|
| **fp32** (`r_walk`, positive operands) | **7.92 ± 0.18 W**, 0.367 ± 0.009 · 1.73 ± 0.04 pJ/MAC | **8.61 ± 0.18 W**, 0.399 ± 0.009 · 1.88 ± 0.04 pJ/MAC | **5.04 ± 0.19 W**, 0.234 ± 0.008 · 1.10 ± 0.04 pJ/MAC | 21.58 ± 0.15 W |
| **fp16** (`r_walk`, paired halves) | **7.96 ± 0.14 W**, 0.389 ± 0.007 · 0.87 ± 0.02 pJ/MAC | **6.19 ± 0.17 W**, 0.303 ± 0.009 · 0.67 ± 0.02 pJ/MAC | **6.29 ± 0.21 W**, 0.308 ± 0.008 · 0.69 ± 0.02 pJ/MAC | 20.43 ± 0.18 W |
| **int8** (`r_walk`, paired bytes) | **1.71 ± 0.13 W**, 0.257 ± 0.021 · 0.054 ± 0.004 pJ/MAC | **3.14 ± 0.21 W**, 0.472 ± 0.035 · 0.100 ± 0.007 pJ/MAC | **1.81 ± 0.26 W**, 0.271 ± 0.036 · 0.057 ± 0.008 pJ/MAC | 6.66 ± 0.14 W |

(i) = D(constant operands, frozen result: `fp32.c_abs`, `fp16.c_cancel`, `int8.c_cancel`); (iii) = D(the random
operands with the result frozen) − (i); (ii) = D(`r_walk`) − D(the same operands frozen). The second figure in each
cell is the share of the total.

**These are not E78's random tiles, and the split does not place the difference.** fp32's `r_walk` has positive
operands (|N(0,1)|, its k = 0 slice fixed at 1.0), so its adder never subtracts. E78's random tile (`fp32.randn`:
random signs and a random k = 0 slice) costs 2.24 ± 0.17 W more (X32, `scored.json` `primary.contrasts.X32`), and
none of the three parts holds that: as shares of `fp32.randn` the parts are **0.333 ± 0.006 (i), 0.362 ± 0.009 (iii)
and 0.212 ± 0.008 (ii), plus 0.094 ± 0.007 the split does not place**. fp16's and int8's `r_walk` repeat each A
value in a pair ((x, x); (x, x, y, y)) and pair each B value with the negation of an independent one ((u, −u′);
(u, −u′, v, −v′)). They cost 0.959 ± 0.005 of `fp16.randn` and 0.977 ± 0.025 of `int8.full`; as shares of those
anchors the parts are 0.373 / 0.291 / 0.295 in fp16 (plus 0.041 ± 0.005) and 0.251 / 0.461 / 0.265 in int8 (plus
0.023 ± 0.025) ([`corrections-check.txt`](corrections-check.txt) C1).

**Board power, the rail, and the leakage slope.** On the minion rail (`Drail`: deconvolved, τ 0.95 s, the same window
and correction) the fp32 parts are 6.98 / 7.14 / 3.92 W of 18.03 W (shares 0.387 / 0.396 / 0.217), fp16's 6.89 /
5.28 / 5.04 of 17.22 W (0.400 / 0.307 / 0.293) and int8's 1.47 / 2.83 / 1.69 of 5.98 W (0.245 / 0.473 / 0.282). The
shares hold within two points; the watts and the pJ/MAC are the board's and do not carry over to the rail (C4).
Across the registered leakage-slope arms (0.545, 0.3803 and 0 W/°C, against the primary's fitted 0.315), the parts
move by up to −0.38 / +0.52 W (fp16's clocked lane; fp32's moves −0.30 / +0.41 W), the totals by up to −0.72 /
+0.99 W (fp32: 20.86–22.57 W), and the shares by at most 1.7 points (int8's clocked lane; 0.2 in fp32, 0.9 in fp16)
(C5). **The shares are the robust result**: the watts carry the leakage slope's spread on top of their statistical
intervals.

**2. A constant's cost is the lane being clocked; its accumulator's walk costs nothing measurable.** Freezing the
accumulator of an all-ones tile saves **0.10 ± 0.31 W** in fp32, **0.01 ± 0.13 W** in fp16 and **−0.23 ± 0.25 W**
in int8 (W32, W16, W8: H1 PASS in all three, `le` 1.0 / 1.0 / 0.5 W). The frozen constant itself costs **7.92 ±
0.18 W** (fp32), **7.96 ± 0.14 W** (fp16) and **1.71 ± 0.13 W** (int8) over zeros. E78's "the lane is clocked and
its accumulator still walks" (E78 README l.75) keeps its first half only. The stream model says why the walk is
cheap: in a constant tile every accumulator a lane visits in one k sweep holds the same value, so the C read and the
result bus change once every 32 micro-ops, and only the register write moves (about 2 bits a micro-op;
[`tools/claims-v3/rpath/e88.json`](../../../../tools/claims-v3/rpath/e88.json) `model.fp32.ones`).

**3. The result path is a quarter to a third of the random-operand designs, and mostly a bus swinging between
accumulators.**
Holding the operands identical and letting the result walk adds **5.04 ± 0.19 W** in fp32, **6.29 ± 0.21 W** in fp16
and **1.81 ± 0.26 W** in int8 (R32, R16, R8: H2 PASS, `ge` 2 / 2 / 1 W). In fp32, accumulators that are frozen but
differ from each other already cost **3.80 ± 0.17 W** of it (R32bus), and the walk within each adds **1.24 ± 0.11 W**
(R32sum): the registered bus-swing share is **0.754 ± 0.018** per pass (H5 PASS, `ge` 0.6). R32bus is not a pure
bus swing, though: `r_het`'s k = 0 B row (2^50·m_j with random m_j, where `r_abs` has 2^50) adds operand toggles of
its own, +2,944 operand-bus and +2,946 product bits an op, which the frozen fit prices at 0.31 ± 0.02 W (0.27 W
scaled by M32's measured / predicted, 0.887). Taken off each pass, R32bus is 3.49 ± 0.17 W and the share **0.693 ±
0.018** (0.700 scaled): **about 70% of the fp32 result path is the bus swing** (75% before this post-hoc correction;
H5, registered on the raw ratio, passes either way; C2). A lane alternates between two C elements every micro-op
(columns l and l+8), so the C read and the result bus swing between unrelated values whether or not either value
changes. This is E79 Result 5's hypothesis ("the result path swinging between two diverging accumulators"), now
measured in watts.

**4. The operand bits, with the result frozen, cost 8.61 ± 0.18 W in fp32, 6.19 ± 0.17 W in fp16 and 3.14 ± 0.21
W in int8** (M32, M16, M8: H3 PASS). int8 is the one format where the multiplier side is the largest share (0.47).
In fp16 and int8 this side is measured by cancellation, so it holds the products and whatever part of the in-lane
dot-product adder switches before the sum cancels to zero. `r_abs`, the absorbed design, is 0.39 ± 0.11 W above it in fp16 (A16, §6), and it is not a freeze: it walks.

**5. Random signs: 4.78 W above a constant in fp32, and the frozen-result design does not freeze them. H4's first
half FAILS.** ±1.0 operands with the result frozen (`s_abs`) cost **2.52 ± 0.19 W** over the constant (M32s; H4
registered ≤ 1.0 W: **FAIL**); letting the result walk adds **2.26 ± 0.16 W** (R32s; ≥ 2.0 W: PASS). The sum, 4.78 W,
matches E64's +4.5 W of random signs above a constant (aifoundry2). The model priced `s_abs` at 0.24 W from its few
changing operand and product bits. E88.md named, before the data, the likely reason a sign survives absorption (known
limit 2): a product's sign sets whether the adder adds or subtracts, and that switches the adder's inputs even when
the sum cannot change. That reading is a hypothesis this experiment does not test; what is measured is that random
signs cost half of their 4.8 W with the result frozen.

**6. In fp16 an absorbed design costs 0.39 ± 0.11 W more than a cancelled one, and only the cancelled one is frozen.** `r_abs` costs **0.39 ± 0.11 W** more than `r_cancel` (A16; H6 PASS, |·| ≤ 1 W).
*Corrected Sun 1 Nov 2026 after [E104](../2026-11-01-e104-c-readback/README.md) read the accumulators back. This result said "two ways of freezing agree … cancellation stops about as much of the result path as absorption". They do not: `fp16.r_cancel` holds 0, and `fp16.r_abs` walks one unit a micro-op in one word (4f7fffe9 at n = 2, E104-R3), because fp16 truncates each aligned product separately, so the note "below half an ulp" does not hold there. `r_abs` writes about 8,000 more store bits an op than `r_cancel`, 0.28–0.49 W at 30–52 fJ, about the size of A16: a size match, not a finding. A16 and H6 stand as numbers, the fit stands, and at E88's price R16abs's model falls from 7.23 to about 6.77 W against 5.90 ± 0.14 W. fp32's frozen tiles, and fp16's by cancellation, read back as held.*

**7. The model with a result-path term, fitted on E82 before E88 existed, puts 17 of 19 contrasts inside its
registered bands, and the bands are wide (±0.75 to ±1.80 W).** Its frozen
prices (fp32: clocked lane 7.53 W, 19 fJ per operand-bus bit, 74 fJ per product bit, 41 fJ per result bit) put R32 at
5.02 W against 5.04 measured, the constant floors at 7.56 / 7.53 / 1.36 W against 7.92 / 7.96 / 1.71, and the walks at
0.37 / 0.51 / 0.17 W against 0.10 / 0.01 / −0.23. It fails only on the sign pair: M32s (0.24 predicted, 2.52
measured) and R32s (2.26 measured, 0.003 W below its band's 2.262 low edge; it passes at the no-leakage arm). Inside
the bands it misses systematically: the fp32 bus swing (4.75 → 3.80 W) and walk (0.26 → 1.24 W) split
differently, and int8 puts more in the multiplier (2.12 → 3.14 W) and less in the result path (3.07 → 1.81 W) than
predicted ([`scored.json`](scored.json) `primary.contrasts.*.predicted`). R32's 5.02 against 5.04 W is its closest
match of the 19, not a typical one: M32 (9.72 → 8.61 W, −11%), R16 (7.36 → 6.29 W, −15%) and R16abs (7.23 → 5.90 W,
−18%) also miss by a watt or more inside their bands (C3).

| contrast | what | D (W) ±95% | predicted (W) [band] | verdict |
|---|---|---|---|---|
| F32 | `c_abs` − zeros | 7.922 ± 0.181 | 7.56 [6.48, 8.65] | PASS |
| W32 | `ones` − `c_abs` | 0.100 ± 0.311 | 0.36 [−0.89, 1.62] | PASS |
| M32 | `r_abs` − `c_abs` | 8.614 ± 0.175 | 9.72 [8.16, 11.27] | PASS |
| R32 | `r_walk` − `r_abs` | 5.042 ± 0.193 | 5.02 [3.45, 6.58] | PASS |
| R32bus | `r_het` − `r_abs` | 3.801 ± 0.168 | 4.75 [3.26, 6.24] | PASS |
| R32sum | `r_walk` − `r_het` | 1.241 ± 0.106 | 0.26 [−1.00, 1.52] | PASS |
| M32s | `s_abs` − `c_abs` | 2.524 ± 0.185 | 0.24 [−1.01, 1.50] | **FAIL** |
| R32s | `s_walk` − `s_abs` | 2.259 ± 0.158 | 3.69 [2.26, 5.12] | **FAIL** (by 0.003 W) |
| X32 | `randn` − `r_walk` | 2.241 ± 0.173 | 1.48 [0.23, 2.74] | PASS |
| F16 | `c_cancel` − zeros | 7.955 ± 0.143 | 7.53 [6.41, 8.65] | PASS |
| W16 | `ones` − `c_cancel` | 0.014 ± 0.127 | 0.51 [−0.69, 1.71] | PASS |
| M16 | `r_cancel` − `c_cancel` | 6.190 ± 0.168 | 5.64 [3.97, 7.30] | PASS |
| R16 | `r_walk` − `r_cancel` | 6.289 ± 0.208 | 7.36 [5.56, 9.16] | PASS |
| A16 | `r_abs` − `r_cancel` | 0.388 ± 0.111 | 0.13 [−1.07, 1.32] | PASS |
| R16abs | `r_walk` − `r_abs` | 5.901 ± 0.144 | 7.23 [5.43, 9.03] | PASS |
| F8 | `c_cancel` − zeros | 1.710 ± 0.135 | 1.36 [0.61, 2.11] | PASS |
| W8 | `ones` − `c_cancel` | −0.231 ± 0.249 | 0.17 [−0.64, 0.99] | PASS |
| M8 | `r_cancel` − `c_cancel` | 3.145 ± 0.212 | 2.12 [0.56, 3.69] | PASS |
| R8 | `r_walk` − `r_cancel` | 1.809 ± 0.263 | 3.07 [1.46, 4.67] | PASS |

S (over the idle bracket) and D have overlapping intervals in every contrast; S's point lies inside D's interval in
all but R32 (4.846 W against D's low end, 4.849) ([`results.md`](results.md); C7).

**8. Heat is not scored here.** The constant designs (S 9.8–9.9 W) and every int8 design (S 3.9–9.3 W) sit below the
~12 W of S where the die reading's whole-degree steps decide a 2 s window (E78 C1); the sign designs sit just above it
(`s_abs` 12.3 W, `s_walk` 14.6 W) and the random-operand designs well above (16.0–23.4 W) (`e88.json` `items.*.S`;
C10). `dT_win` is in `e88.json` `items.*.dT_win` for every item, unscored.

## Registered against what happened

| | registered (E88.md, `3dd99088`) | happened |
|---|---|---|
| card, clock | aifoundry1 card 1, 600 MHz, nothing set | as registered; every config read 65 W / 65 °C / 600 MHz / 499 mV |
| budget | ≤ 45 card-min; up to 7 passes inside 41 min of the queue | 37.6 card-min; 6 passes (the budget rule stopped before 8816) |
| primary reduction | `reduce_e78.py` unchanged; card 1's 65/65 config gate; launch-gap dips removed (E82 A2) | as registered; 46 dip samples removed over six passes (`e88.json` `reducer.dip_samples_removed`) |
| passes for scoring | ≥ 4 kept | 5 kept (8813 set aside by the zero-anchor gate) |
| arms | dips kept; leakage 0.545, 0.3803, 0 | leakage arms: same five passes, 29/3, 29/3, 30/2 (only P-R32s moves, to PASS at no correction). Dips kept: the random-anchor gate sets aside 8810, 8813 and 8815 (as on E82) and three passes remain, below the registered minimum of four (`predictions-e88.json` `primary.min_passes`), so that arm is **not scored (3 < 4 passes), exploratory**; read as exploratory contrasts, it would move H2-int8 and H4-signs-result to INCONCLUSIVE and P-R8 to FAIL (`scored.json` `verdicts_moving_between_arms`, filled by a scorer with no pass-count check; C6) |
| tally | 13 mechanism rules + 19 bands | 29 pass, 3 fail (H4-signs-mult, P-M32s, P-R32s) |

**Departures and disclosures.**
- **D1** (plumbing, written at 18:56 PDT, after the freeze, during pass 8810 and before any pass was reduced; first
  committed with the data in `f1c7412e`): `tools/claims-v3/rpath/collect_e88.sh` was added to run the frozen reducer
  and scorer and assemble this directory; it was run twice, the second time on a repo-relative copy of the raw passes
  so that no committed file carries a Mac home path (the box's own working-tree path is in `runs.jsonl`,
  `configs.json` and the logs, as in earlier runs). Both runs gave the same numbers.
- The pre-registration's header says "Written … ~18:55 PDT". It was committed at 18:53:19 and pushed at 18:53:22
  (GitHub's push record), 71 s before the claim (18:54:33.592, the message id's timestamp) and 86 s before the smoke
  (18:54:48). The header's time was an estimate, about two minutes late; `E88.md` is left as committed (C10).
- The runner's log lines read "E78 pass … tiles verified against kinds.json": they are `run_e78.py`'s unchanged
  strings. The tiles were verified against `e88.json` through `e88_common.verify_tiles` before each pass.
- No interim look at power data: the waits read only the queue log, the skip lines and `block.json`. The smoke's own
  board-power ranges were printed by the registered smoke script (r_abs peaked at 49.6 W, r_walk at 55.0 W); nothing
  was chosen from them.

**Limits found after the data** (from the verification; [`corrections-check.txt`](corrections-check.txt)).
- **The card's result was never read back.** With `--values file:` the host prints `"result": "unchecked"` and skips
  `checkC` (`workloads/sparsity/host/main.cpp:614`); all 2,156 launch records say so. Which designs froze and which
  walked rests on the desk emulation (`make_e88.py --check`: 14 of 14 checks true, `tools/claims-v3/rpath/e88.json`
  `checks`) and on the power data agreeing with it (R32 5.04 W against 5.02 predicted; the constants' walks within
  0.3 W of zero). A later run could read C back once per design (C8).
- R32bus carries `r_het`'s own operand toggles (§3, C2); the split's operands are designed, not E78's random tiles
  (§1, C1); its watts and pJ/MAC are board power and carry the leakage slope's spread (§1, C4, C5).

## What this changes

- **For the blog (Horace follow-up, §5 and §6):** "power is paid for operand bits that change" becomes a three-part
  account, in board power over zeros. For random positive fp32 operands (|N(0,1)|), about 37% of a multiply-add's
  switching power is paid for the lane being clocked at all, 40% for operand bits in the multiplier, 23% for the
  result path. E78's random tile (`randn`: random signs, no fixed k = 0 slice) costs 2.24 W more, 9% of its own
  total, which the split does not place, so as shares of it the parts are 33 / 36 / 21% plus 9%. fp16 and int8, on random values in paired halves: 39 / 30 / 31% and 26 /
  47 / 27% (their multiplier side includes the in-lane dot-product adder up to where its sum cancels). A constant
  pays only the first part. "Its accumulator still walks" is withdrawn as a cost: measured, it is 0.1 ± 0.3 W. About
  70% of the fp32 result path (75% before `r_het`'s own operand toggles are taken off) is a lane alternating between
  two different accumulators, not either accumulator changing. Quote the shares: the watts move by up to 1 W with
  the leakage slope.
- **For the Horace hub:** Q130(l)'s ranked item 2 (the completeness review) closes for the split of random positive
  operands; the sign's share is measured (M32s, R32s) but not explained. The new open item is the sign: half of random
  signs' cost survives a frozen result. The "no model has an accumulator term" item closes only in the narrow sense:
  `tools/claims-v3/rpath/make_e88.py`'s stream model plus a four-price fit puts 17 of 19 out-of-sample contrasts
  inside its registered ±0.75–1.80 W bands, but inside them it misplaces the result-path and multiplier parts and it
  misses the sign pair; a refit on E82 + E88 is open. The RTL bench stays broken and was not used (Q130(b) r2 §0).
- **For the records:** E88 in `03-experiments.md`; Q130(l)'s A5 (the blog page §6 l.284, §7 l.297) is now answered with this
  directory.

## Corrections after verification (Sat 31 Oct 2026)

*The Q130 evening workflow's verifier checked E88. It found one major fault and ten minor ones, with the verdict
"holds with fixes", and re-derived every headline number from the committed raw passes and code. These corrections
were made at the desk: no card was touched, nothing was re-run, and no frozen file changed. `e88*.json`,
`scored.json` and `results.md` are byte-identical to the data commit `f1c7412e` (their sha256 open the check), the
pre-registration `E88.md` is left as committed, and no registered verdict changed (29 pass, 3 fail).
[`corrections-check.py`](corrections-check.py) prints every number below from committed files, and
[`corrections-check.txt`](corrections-check.txt) is its output. One minor fault concerns a line `block_e88.sh`
inherited from the lab's earlier block scripts, not E88's own; it is left for a repo-wide cleanup, because
`block_e88.sh`'s sha256 is registered.*

| | what was wrong | what changed |
|---|---|---|
| **C1** (major) | The split was quoted as "a random multiply-add" (the blog bullet, the hub bullet and the result handed to the workflow). fp32's `r_walk` has positive operands (\|N(0,1)\|, its k = 0 slice 1.0), and fp16's and int8's pair their values. E78's random tile costs 2.24 ± 0.17 W more in fp32 (X32), and no part holds that. | "Random positive operands" (fp32) and "random values in paired halves" (fp16, int8) wherever the split is quoted. §1 adds the split as shares of `fp32.randn`: 0.333 / 0.362 / 0.212, plus 0.094 the split does not place; fp16's and int8's `r_walk` are 0.959 and 0.977 of their random anchors. |
| C2 | H5's 75% "bus swing" (R32bus) included `r_het`'s own k = 0 operand toggles (+2,944 bus and +2,946 product bits an op). | §3 reports about 70%: 0.693 ± 0.018 with the fit's 0.31 W taken off each pass (0.700 scaled by M32's measured / predicted), R32bus 3.49 ± 0.17 W. The registered ratio, 0.754, stays as registered; H5 passes either way. |
| C3 | "The model predicts 17 of 19" was quoted with its best match (R32, 5.02 against 5.04 W). | §7 and the hub bullet say 17 of 19 inside registered bands of ±0.75 to ±1.80 W, and name the misses inside them: R32bus −20%, M32 −11%, R16 −15%, R16abs −18%, int8's R8 −41% and M8 +48%. |
| C4 | Neither the split nor the pJ/MAC said they are board power. | §1 names D as board power and adds the split on the minion rail (fp32 6.98 / 7.14 / 3.92 of 18.03 W): the shares hold within two points, the watts do not carry over. |
| C5 | The ± on the watts and pJ/MAC are statistical only, and the registered leakage-slope arms move the parts more. | §1 gives the arms' spread: the parts up to −0.38 / +0.52 W, the totals up to −0.72 / +0.99 W, the shares at most 1.7 points. The shares are named the robust result. |
| C6 | The dips-kept arm kept 3 passes, yet its verdicts were reported; the registration says fewer than 4 means "not scored". | It reads "not scored (3 < 4 passes), exploratory". `score_e88.py` has no pass-count check; `scored.json` stays as the frozen scorer wrote it. |
| C7 | "S agrees with D in every contrast within its interval": in R32, S lies 0.003 W below D's interval. | "S and D have overlapping intervals in every contrast; S's point lies inside D's interval in all but R32." |
| C8 | The card's C was never read back (`"result": "unchecked"` in all 2,156 launch records; `main.cpp:614` skips the check for raw tiles), and the README did not say so. | Added under "Limits found after the data": frozen against walking rests on the desk emulation (14 of 14 checks) and on the power data agreeing with it. |
| C9 | Blog-facing wording went too far in three places: "a sign costs the multiplier little" (E88 cannot separate the multiplier from add/subtract switching); "a third" and "8.0 W" cited only W32; int8's multiplier share includes the in-lane sum. | §4 carries the in-lane-sum caveat. In the result handed to the workflow, the sign point says only that the magnitudes the multiplier sees never change and that the add/subtract reading is untested, and the constant point cites `e88.json` `items.fp32.ones.D` (8.02 W) and `items.fp32.randn.D` (23.82 W). |
| C10 | D1 had no time; "no committed file carries a home path" (the box's working-tree path is in the raw records); `E88.md`'s header says "~18:55 PDT", though it was committed at 18:53:19 and pushed at 18:53:22; §8's "below ~12 W" left out the sign designs (12.3, 14.6 W). | D1 is dated (18:56) and says "no Mac home path"; the pre-registration's push time is in the disclosures (`E88.md` itself is left frozen); §8 is rewritten from `items.*.S`. |

## Files

| file | what |
|---|---|
| `e88.json` | the primary reduction (reduce_e78.py via reduce_e88.py, dips removed): items, per pass, gates, checks |
| `e88-keepdips.json`, `e88-leak0.545.json`, `e88-leak0.3803.json`, `e88-leak0.json` | the registered arms |
| `scored.json`, `results.md` | the contrasts, the splits, every rule's verdict, the arms and the verdicts that move |
| `runs*.csv`, `reduce*.txt`, `reduce*.log`, `score.log` | per-run rows and the reducer's text |
| `aifoundry1-c1/rpath/p8810`–`p8815`, `rpath-smoke-p8801` | raw passes: telemetry (10 Hz), launch records, marks, tile dumps, config reads, manifests |
| `logs/` | the queue log, the dry run, the closing config read |
| `code.sha256` | every file the run and the reduction used |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind the corrections after verification, and its output (standard library only; reads committed files) |

Code: [`tools/claims-v3/rpath/`](../../../../tools/claims-v3/rpath/) — `make_e88.py` (tiles, stream model, fit),
`make_predictions_e88.py`, `e88_common.py`, `run_e88.py`, `block_e88.sh`, `queue_e88.sh`, `run_e88_a1.sh`,
`reduce_e88.py`, `score_e88.py`, `collect_e88.sh`, `selftest_e88.py`.

Reproduce from the raw passes: `PY=/usr/bin/python3 bash tools/claims-v3/rpath/collect_e88.sh <dir holding rpath/,
rpath-smoke/, logs/>` (desk compute, a few minutes).
