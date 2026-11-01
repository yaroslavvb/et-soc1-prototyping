# E88 — what the result path costs against the operand bits (Q130, aifoundry1 card 1, 2026-10-31)

*Pre-registered in [`tools/claims-v3/rpath/E88.md`](../../../../tools/claims-v3/rpath/E88.md) with
[`predictions-e88.json`](../../../../tools/claims-v3/rpath/predictions-e88.json), commit **`3dd99088`** (18:53:19 PDT),
1 min 14 s before the card was claimed in `#community-lab` (18:54:33 PDT, message `1566269185057751163`, "using
aifoundry1 card 1 for 1 h, until ~20:00 PDT"). Card session **18:54:48–19:32:22 PDT** on **aifoundry1 card 1 only**
(`V3_DEVICE=1`, its own lock): the smoke 8801 (18:54:48–18:55:29), six passes 8810–8815 (18:55:43–19:31:48; the
queue's budget rule stopped before 8816) and a closing read-only `ettelem config` (65 W / 65 °C, 600 MHz, 499 mV, as
at every pass's two ends). **37.6 card-minutes of the 45 registered.** No knob was written, no `--reset-ms`, no reset.
**Released at 19:37 PDT** by an edit of the same post, about 30 s after this directory's first commit (`f1c7412e`),
read back as `<ai> Claude says: using aifoundry1 card 1 for 1 h, until ~20:00 PDT doc — released (edited)`.*

> **What this is.** Thirteen operand tiles that freeze a multiply-add's result while its operands keep moving
> (fp32: a 2^100 product at k = 0 absorbs every later product; fp16 and int8: each micro-op's dot product cancels
> exactly), or walk it with the same operands, beside each type's zeros, random data and ones. Paired within each
> pass, they split one random multiply-add's switching power into **(i) the lane being clocked**, **(ii) the result
> path** and **(iii) the operand-side multiplier**, in three formats, at 600 MHz, in E78's frame with E78's runner
> and reduction unchanged.

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

**1. The split.** Switching power over the type's zeros (D), paired per pass, 95% intervals over the five kept
passes; pJ per MAC through each pass's measured rate ([`scored.json`](scored.json) `primary.splits`):

| random data, result walking | (i) the lane clocked | (iii) operand-side multiplier | (ii) the result path | total |
|---|---|---|---|---|
| **fp32** (`r_walk`) | **7.92 ± 0.18 W**, 0.367 ± 0.009 · 1.73 ± 0.04 pJ/MAC | **8.61 ± 0.18 W**, 0.399 ± 0.009 · 1.88 ± 0.04 pJ/MAC | **5.04 ± 0.19 W**, 0.234 ± 0.008 · 1.10 ± 0.04 pJ/MAC | 21.58 ± 0.15 W |
| **fp16** (`r_walk`) | **7.96 ± 0.14 W**, 0.389 ± 0.007 · 0.87 ± 0.02 pJ/MAC | **6.19 ± 0.17 W**, 0.303 ± 0.009 · 0.67 ± 0.02 pJ/MAC | **6.29 ± 0.21 W**, 0.308 ± 0.008 · 0.69 ± 0.02 pJ/MAC | 20.43 ± 0.18 W |
| **int8** (`r_walk`) | **1.71 ± 0.13 W**, 0.257 ± 0.021 · 0.054 ± 0.004 pJ/MAC | **3.14 ± 0.21 W**, 0.472 ± 0.035 · 0.100 ± 0.007 pJ/MAC | **1.81 ± 0.26 W**, 0.271 ± 0.036 · 0.057 ± 0.008 pJ/MAC | 6.66 ± 0.14 W |

(i) = D(constant operands, frozen result: `fp32.c_abs`, `fp16.c_cancel`, `int8.c_cancel`); (iii) = D(the random
operands with the result frozen) − (i); (ii) = D(`r_walk`) − D(the same operands frozen). The second figure in each
cell is the share of the total. `r_walk`'s operands are positive (|N(0,1)|), so its adder never subtracts; E78's
random tile, with random signs, costs 2.24 ± 0.17 W more in fp32 (X32, `scored.json` `primary.contrasts.X32`).

**2. A constant's cost is the lane being clocked; its accumulator's walk costs nothing measurable.** Freezing the
accumulator of an all-ones tile saves **0.10 ± 0.31 W** in fp32, **0.01 ± 0.13 W** in fp16 and **−0.23 ± 0.25 W**
in int8 (W32, W16, W8: H1 PASS in all three, `le` 1.0 / 1.0 / 0.5 W). The frozen constant itself costs **7.92 ±
0.18 W** (fp32), **7.96 ± 0.14 W** (fp16) and **1.71 ± 0.13 W** (int8) over zeros. E78's "the lane is clocked and
its accumulator still walks" (E78 README l.75) keeps its first half only. The stream model says why the walk is
cheap: in a constant tile every accumulator a lane visits in one k sweep holds the same value, so the C read and the
result bus change once every 32 micro-ops, and only the register write moves (about 2 bits a micro-op;
[`tools/claims-v3/rpath/e88.json`](../../../../tools/claims-v3/rpath/e88.json) `model.fp32.ones`).

**3. The result path is a quarter to a third of random data, and mostly a bus swinging between accumulators.**
Holding the operands identical and letting the result walk adds **5.04 ± 0.19 W** in fp32, **6.29 ± 0.21 W** in fp16
and **1.81 ± 0.26 W** in int8 (R32, R16, R8: H2 PASS, `ge` 2 / 2 / 1 W). In fp32, accumulators that are frozen but
differ from each other already cost **3.80 ± 0.17 W** of it (R32bus), and the walk within each adds **1.24 ± 0.11 W**
(R32sum): the bus-swing share is **0.754 ± 0.018** per pass (H5 PASS, `ge` 0.6). A lane alternates between two C
elements every micro-op (columns l and l+8), so the C read and the result bus swing between unrelated values whether
or not either value changes. This is E79 Result 5's hypothesis ("the result path swinging between two diverging
accumulators"), now measured in watts.

**4. The operand bits, with the result frozen, cost 8.61 ± 0.18 W in fp32, 6.19 ± 0.17 W in fp16 and 3.14 ± 0.21
W in int8** (M32, M16, M8: H3 PASS). int8 is the one format where the multiplier side is the largest share (0.47).

**5. Random signs: 4.78 W above a constant in fp32, and the frozen-result design does not freeze them. H4's first
half FAILS.** ±1.0 operands with the result frozen (`s_abs`) cost **2.52 ± 0.19 W** over the constant (M32s; H4
registered ≤ 1.0 W: **FAIL**); letting the result walk adds **2.26 ± 0.16 W** (R32s; ≥ 2.0 W: PASS). The sum, 4.78 W,
matches E64's +4.5 W of random signs above a constant (aifoundry2). The model priced `s_abs` at 0.24 W from its few
changing operand and product bits. E88.md named, before the data, the likely reason a sign survives absorption (known
limit 2): a product's sign sets whether the adder adds or subtracts, and that switches the adder's inputs even when
the sum cannot change. That reading is a hypothesis this experiment does not test; what is measured is that random
signs cost half of their 4.8 W with the result frozen.

**6. Two ways of freezing agree in fp16.** An absorbed result (`r_abs`) costs **0.39 ± 0.11 W** more than a
cancelled one (`r_cancel`) (A16; H6 PASS, |·| ≤ 1 W): cancellation inside the dot product stops about as much of the
result path as absorption at the aligner.

**7. The model with a result-path term, fitted on E82 before E88 existed, predicts 17 of 19 contrasts.** Its frozen
prices (fp32: clocked lane 7.53 W, 19 fJ per operand-bus bit, 74 fJ per product bit, 41 fJ per result bit) put R32 at
5.02 W against 5.04 measured, the constant floors at 7.56 / 7.53 / 1.36 W against 7.92 / 7.96 / 1.71, and the walks at
0.37 / 0.51 / 0.17 W against 0.10 / 0.01 / −0.23. It fails only on the sign pair: M32s (0.24 predicted, 2.52
measured) and R32s (2.26 measured, 0.003 W below its band's 2.262 low edge; it passes at the no-leakage arm). Inside
the bands it misses systematically: the fp32 bus swing (4.75 → 3.80 W) and walk (0.26 → 1.24 W) split
differently, and int8 puts more in the multiplier (2.12 → 3.14 W) and less in the result path (3.07 → 1.81 W) than
predicted ([`scored.json`](scored.json) `primary.contrasts.*.predicted`).

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

The S column (over the idle bracket) agrees with D in every contrast within its interval ([`results.md`](results.md)).

**8. Heat is not resolved here.** Every E88 design except the random ones sits below the ~12 W of S where the die
reading's whole-degree steps decide a 2 s window (E78 C1). `dT_win` is in `e88.json` `items.*.dT_win`, unscored.

## Registered against what happened

| | registered (E88.md, `3dd99088`) | happened |
|---|---|---|
| card, clock | aifoundry1 card 1, 600 MHz, nothing set | as registered; every config read 65 W / 65 °C / 600 MHz / 499 mV |
| budget | ≤ 45 card-min; up to 7 passes inside 41 min of the queue | 37.6 card-min; 6 passes (the budget rule stopped before 8816) |
| primary reduction | `reduce_e78.py` unchanged; card 1's 65/65 config gate; launch-gap dips removed (E82 A2) | as registered; 46 dip samples removed over six passes (`e88.json` `reducer.dip_samples_removed`) |
| passes for scoring | ≥ 4 kept | 5 kept (8813 set aside by the zero-anchor gate) |
| arms | dips kept; leakage 0.545, 0.3803, 0 | leakage arms: same five passes, 29/3, 29/3, 30/2 (only P-R32s moves, to PASS at no correction). Dips kept: the random-anchor gate sets aside 8810, 8813 and 8815 (as on E82), three passes remain, and H2-int8 and H4-signs-result become INCONCLUSIVE, P-R8 FAIL (`scored.json` `verdicts_moving_between_arms`) |
| tally | 13 mechanism rules + 19 bands | 29 pass, 3 fail (H4-signs-mult, P-M32s, P-R32s) |

**Departures and disclosures.**
- **D1** (plumbing, after the freeze and before any pass was reduced): `tools/claims-v3/rpath/collect_e88.sh` was
  added to run the frozen reducer and scorer and assemble this directory; it was run twice, the second time on a
  repo-relative copy of the raw passes so that no committed file carries a home path. Both runs gave the same numbers.
- The runner's log lines read "E78 pass … tiles verified against kinds.json": they are `run_e78.py`'s unchanged
  strings. The tiles were verified against `e88.json` through `e88_common.verify_tiles` before each pass.
- No interim look at power data: the waits read only the queue log, the skip lines and `block.json`. The smoke's own
  board-power ranges were printed by the registered smoke script (r_abs peaked at 49.6 W, r_walk at 55.0 W); nothing
  was chosen from them.

## What this changes

- **For the blog (Horace follow-up, §5 and §6):** "power is paid for operand bits that change" becomes a three-part
  account. About 37% of a random fp32 multiply-add's switching power (over zeros) is paid for the lane being
  clocked at all, 40% for operand bits in the multiplier, 23% for the result path. fp16: 39 / 30 / 31%. int8: 26 / 47
  / 27%. A constant pays only the first part. "Its accumulator still walks" is withdrawn as a cost: measured, it is
  0.1 ± 0.3 W. Random data's result path costs mostly because a lane alternates between two different accumulators
  (75% of it), not because either accumulator changes.
- **For the Horace hub:** Q130(l)'s ranked item 2 (the completeness review) closes for the split. The new open
  item is the sign: half of random signs' cost survives a frozen result. The "no model has an accumulator term" item
  closes: `tools/claims-v3/rpath/make_e88.py`'s stream model plus a four-price fit predicts 17 of 19 out-of-sample
  contrasts. The RTL bench stays broken and was not used (Q130(b) r2 §0).
- **For the records:** E88 in `03-experiments.md`; Q130(l)'s A5 (the blog page §6 l.284, §7 l.297) is now answered with this
  directory.

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

Code: [`tools/claims-v3/rpath/`](../../../../tools/claims-v3/rpath/) — `make_e88.py` (tiles, stream model, fit),
`make_predictions_e88.py`, `e88_common.py`, `run_e88.py`, `block_e88.sh`, `queue_e88.sh`, `run_e88_a1.sh`,
`reduce_e88.py`, `score_e88.py`, `collect_e88.sh`, `selftest_e88.py`.

Reproduce from the raw passes: `PY=/usr/bin/python3 bash tools/claims-v3/rpath/collect_e88.sh <dir holding rpath/,
rpath-smoke/, logs/>` (desk compute, a few minutes).
