# E90: sign patterns and tile-to-tile spread (aifoundry3, 600 MHz)

*Sat 31 Oct 2026 (week 44), Q130's evening round (optional lane; the Q130 critic's items 6 and 13). Pre-registered
in `6f737d61` (pushed 21:06:14 PDT, before the claim and the first launch):
[`tools/claims-v3/kinds/E90.md`](../../../../tools/claims-v3/kinds/E90.md), frozen numbers in `predictions-e90.json`
(sha256 `d5bdb8b2…`). The scorer and the registered dips-removed arm were committed in `1455065b` (21:11:40 PDT),
before any pass was copied or read. aifoundry3 card 0 at 600 MHz, 521.5 mV mean, TDP 0 / threshold 65 °C / 600 MHz /
523 mV read under the card lock at the session's start (21:07:35) and end (21:33:02), never set. Nothing was written
to the card, and no `--reset-ms` was sent. Claim 1566302603107639337 in #community-lab, posted 21:07:21 PDT, released
21:33 PDT (26 min, inside the registered 30).*

**What ran.** Seventeen new tiles (`tools/claims-v3/kinds/e90/`, written with make_kinds.py's own machinery):
random ±1 signs in fp32, fp16 and int8; ±pi in fp32; E78's own `randn` tiles with every sign bit cleared
(`abs_randn`, all positive) or set (`negabs_randn`, all negative), so they carry exactly the anchors' magnitude bits;
and three fresh draws each of fp32 `sparse50`, fp16 `nn_like` and fp16 `uniform01`. Beside them in every pass ran
E78's six anchors (three times), `fp32.ones`, `fp16.ones` and E78's committed tile of each redrawn rule (once), and
the `anchor_pi` tie (first and last). E78's runner and reduction ran unchanged (sha256-checked). Three passes ran
(9010–9012), 126 runs, **all kept**; no pass was set aside and no run failed. D is a tile's board power over its own
type's zeros. Every interval is 95% over passes, t(0.975, 2) × SE; every step is paired within each pass.

## Results

**1. A random sign costs about 5 W, 8–16 times what its sign bits cost, and the same in fp32 and fp16.** Changing
only the sign of each element, at a fixed magnitude, against the same constant (`scored.json` › `steps`):

| step | measured (W) | ±95% | the bits model (W) | ÷ bits model | fJ per flipped sign bit | Q130(n)'s predictor implies | verdict |
|---|---|---|---|---|---|---|---|
| fp32 ±1 − fp32 +1 | **5.006** | 0.517 | 0.592 | 8.5× | 1,377 | ≈ 3.9 | R1 FAIL |
| fp16 ±1 − fp16 +1 | **5.079** | 0.403 | 0.317 | 16.0× | 745 | ≈ 5.3 | R1 FAIL |
| fp32 ±pi − pi (`anchor_pi`) | **6.555** | 0.343 | 0.680 | 9.6× | 1,868 | ≈ 7.4 | R1 FAIL |

The bits model prices each flipped sign bit at what E65 (fp32 B, 123 fJ) and E67 (fp32 A, 247 fJ) and E79 (fp16
B 34 fJ, a bound; A 71 fJ) measured for that bit alone. The measured steps are far beyond it: a random sign costs
745–1,868 fJ per flipped sign bit (A and B pooled). fp32 ±1 lands at 13.340 ± 0.528 W over zeros, 0.31 of the way
from the constant (8.334 W) to random data (24.718 W). fp16 ±1 costs the same step (5.08 against 5.01 W), although it
flips 6,082 sign bits an op against fp32's 3,244 and its operand sign bits are priced about 3.5× lower.

**2. On random magnitudes, the signs are 7.5% (fp32) and 11.8% (fp16) of random data's switching power.** The same
magnitudes with random signs (E78's `randn`) against all positive (`abs_randn`):

| step | measured (W) | ±95% | bits model (W) | ÷ bits model | fJ per flipped sign bit | verdict |
|---|---|---|---|---|---|---|
| fp32 randn − \|randn\| | **1.866** | 0.596 | 0.547 | 3.4× | 578 | R2 FAIL |
| fp16 randn − \|randn\| | **2.613** | 0.220 | 0.311 | 8.4× | 382 | R2 FAIL |

`fp32.abs_randn` costs 22.852 ± 0.539 W and `fp16.abs_randn` 19.547 ± 0.313 W, against the anchors' 24.718 ± 0.058
and 22.160 ± 0.253 W.

**3. A sign bit held set costs nothing measurable in fp16; fp32 is unresolved.** All negative against all positive,
the same magnitudes (the products are identical, since − × − = +): fp16 **+0.008 ± 0.257 W** (inside ±0.30 W: R3
PASS); fp32 **−0.155 ± 1.567 W** (INCONCLUSIVE; a board-reading dip fell in pass 9011's `fp32.negabs_randn` window,
and with the dips removed it is +0.062 ± 0.714 W, still unresolved with three passes). So R3 is INCONCLUSIVE.

**4. int8 ±1 costs three quarters of uniform random int8.** In two's complement +1 is 0x01 and −1 is 0xFF, so each
sign change flips seven bits. `int8.signs` costs **5.466 ± 0.220 W** over int8 zeros, against `int8.full` 7.227 ±
0.118 W in the same session (0.756×) and E78's int8 ones 1.561 W and neg_ones 1.628 W (cross-session). No bits
prediction was registered for it; it lies inside Q130(n)'s interval (5.605 W [4.718, 6.493]).

**5. Re-drawing a rule moves its cost by up to 0.9 W, and the committed tiles of two rules are not typical.** Each
fresh draw against E78's committed tile of the same rule, paired per pass (`scored.json` › `draws`, `spread`):

| rule | committed tile (W) | d1 / d2 / d3 (W) | draws − committed, mean (W) | sd between the 4 tiles (W) | one tile's between-pass sd (W) | Q130(n)'s deltas (W) | R4 |
|---|---|---|---|---|---|---|---|
| fp32 `sparse50` | 7.295 | 8.193 / 8.178 / 7.622 | **+0.703 ± 0.145** | 0.440 | 0.047 | +0.779 / +0.884 / +0.191 | FAIL |
| fp16 `nn_like` | 17.560 | 16.960 / 16.738 / 16.372 | **−0.871 ± 0.066** | 0.498 | 0.079 | −1.072 / −1.188 / −1.525 | FAIL |
| fp16 `uniform01` | 19.453 | 18.994 / 19.195 / 19.292 | −0.292 ± 0.310 | 0.192 | 0.143 | −0.111 / −0.035 / −0.034 | INCONCLUSIVE |

The between-tile spread is 6–9× one tile's pass-to-pass scatter for the two zero-bearing rules, so E78's intervals on
those cells (±0.06–0.12 W) describe the tile, not the rule. The draws follow their tiles' own statistics: fp32
`sparse50`'s draws gate 0.741–0.763 of lane-cycles against the committed tile's 0.774 and cost more; fp16 `nn_like`'s
gate 0.230–0.250 against 0.195 and cost less. Q130(n)'s predictor, fitted on E78's kinds and run unchanged on each
draw, tracks the nine deltas with an rms error of **0.28 W** and no draw on the wrong side (R5 PASS).

**6. The session tied E78.** Every reference cell lies within its band of E78's value: fp32/fp16 randn −0.007 /
−0.002 W, ones +0.077 / −0.138 W, `anchor_pi` +0.041 W, the three committed redraw tiles −0.042 to +0.027 W, int8 full
+0.170 W (S1 PASS). Fourteen of the seventeen E90 tiles lie inside Q130(n)'s 95% interval (S2 PASS at the registered
14); the three outside are the `uniform01` draws, which the predictor puts 1.8–2.0 W too high, just past its intervals' lower ends.

**7. Heat and rail.** On the whole-degree die reading, ±1 warms the die 1.9–2.0 °C in 2 s (fp32 / fp16), ±pi 2.05 °C,
against 1.0–1.4 °C for the constants and 2.95–3.22 °C for random data (`e90.json` › `items.*.dT_win`; S is 15.3–16.9
W, above E78's ~12 W resolution limit). The minion rail carries most of each step: fp32 ±1 − +1 is +3.86 W on the
rail, fp16 +4.06 W, ±pi − pi +5.10 W, randn − |randn| +1.15 W (fp32) and +1.90 W (fp16) (differences of the rail
means, `items.*.Drail`; reported, not scored).

## Registered against happened

| rule | registered | happened | verdict |
|---|---|---|---|
| E90-R1 | each fixed-magnitude step ≤ 2 × the bits model | 5.006 / 5.079 / 6.555 W against thresholds 1.184 / 0.634 / 1.359 W; every lower bound above its threshold | **FAIL** |
| E90-R2 | randn − \|randn\| ≤ 2 × the bits model | 1.866 / 2.613 W against 1.093 / 0.622 W | **FAIL** |
| E90-R3 | negabs − abs inside ±0.30 W | fp16 PASS (+0.008 ± 0.257); fp32 −0.155 ± 1.567 | **INCONCLUSIVE** |
| E90-R4 | draws − committed inside ±0.50 W | sparse50 +0.703 ± 0.145, nn_like −0.871 ± 0.066 (both entirely outside), uniform01 −0.292 ± 0.310 | **FAIL** |
| E90-R5 | Q130(n)'s deltas: rms ≤ 0.50 W, none resolved opposite | rms 0.277 W, none opposite | **PASS** |
| E90-S1 | session tie within the bands | all nine cells inside | **PASS** |
| E90-S2 | ≥ 14 of 17 inside Q130(n)'s interval | 14 of 17 | **PASS** |

Two registered predictions failed decisively: the sign-bit price model (R1, R2) and E78's committed tile as its
rule's value (R4). The failures are the findings. **Arms** (`scored.json` › `rules.*.arms`): at the fixed slope
0.1994 W/°C every verdict is the primary's. At k = 0 S1 moves to FAIL (that arm compares uncorrected D with E78's
corrected values, as in E86); every other verdict holds. At 0.3803 the zeros-line gate sets pass 9011 aside, so that
arm keeps two passes and scores nothing. The primary leakage slope is 0.2203 W/°C over 109 runs (E86: 0.2290).
**The registered dips-removed arm** (`dips-arm/`): 19 dip samples in the three passes, 4 of them in power windows
(two in `fp16.uniform01_d1`, one each in `fp32.negabs_randn` and `fp16.nn_like_d2`). All three passes were kept, so
it is reported as a sensitivity arm, and its verdicts are identical to the primary's. **Checks:** idle consistency
median |S − S0 − D| 0.050 W; carry-over 0.0004 ± 0.0011 W/W; rail lag 0.95–1.00 s; duty ≥ 0.995; cycles per op
546.001 / 546.001 / 318.0; every dumped tile equal to its registered sha256; the tie's drift 0.13–0.23 W a pass.
**Departures:** none from E90.md. As E86 did, the collection ran over a copy of the raw passes inside the repo's
ignored `build/` tree, so the recorded directories are relative.

## Interpretation (labelled: not measured by E90)

The kernel's accumulator runs through each launch: `MUL` is set only on a launch's first TensorFMA
(`workloads/sparsity/kernel/sparsity.c:168`), so every later op adds into the same C. With every product positive
(the constants, `abs_randn`, `negabs_randn`) each C only grows. With random signs, each update adds or subtracts at
random, so the fp32 adder keeps switching between effective addition and subtraction, and the sum keeps crossing
magnitudes. fp16 (TensorFMA16A32) accumulates into the same fp32 C with the same 4,096 C updates an op as fp32, and
its sign step equals fp32's within error even though its operand sign bits differ in count and price. Both facts
point to the cost of a sign living on the accumulate (result) side, not on the operand bits. That is the critic's
item 2 mechanism, now with a measured size. **E90 does not identify the stage**; the RTL bench that could split
operand-side from accumulate-side toggles still returns no correct multiply-add (Q130(b)). The ±pi step exceeding
the ±1 step (6.56 against 5.01 W) fits a full-mantissa addend switching more of the adder than an integer one, but
that too is a reading, not a measurement.

## What it changes

- **The kinds table gains sign rows** in fp32, fp16 and int8: switching power, pJ per MAC, the 2 s rise
  (`table_cells` of the lane result; `e90.json` › `items`). On aifoundry3 at 600 MHz, fp32 ±1 costs 13.34 W over
  zeros. E64 read 13.10 W on aifoundry2 under its own governor (Q130(c) README), a different card and clock, so the two agree in
  kind, not by design.
- **The post's mechanism needs a qualifier.** "Power is paid for operand bits that change" under-prices a sign
  change 8–16 times. A random sign costs about 5 W at 600 MHz, a third of the way from a constant to random data,
  with almost no operand bits moving (3,244 bus bits an op against random data's 82,214).
- **One tile per cell is a draw, and for zero-bearing rules the draw matters.** E78's fp32 `sparse50` cell is
  0.70 W (10%) below its rule's fresh draws, and fp16 `nn_like` is 0.87 W (5%) above. Quote ±0.5 W for those rules,
  or price a tile with Q130(n)'s predictor, which tracks the draws to 0.28 W rms. fp16 `uniform01`'s spread is
  0.19 W.
- **Hub:** critic item 6 (sign patterns) is measured; item 13 (tile spread) is measured for the three rules the
  critic named; item 2 (the result path) gains its strongest evidence so far, on silicon.

## Caveats

Three passes (t = 4.30), one card, one clock. The bits model assumes per-bit prices measured with the other side held
constant add up in random data, and fp16's B sign price is a bound. The fp32 static-bit test is unresolved. The int8
comparison with E78's constants crosses sessions. The redraw spread rests on three draws per rule (2 degrees of
freedom). The die reading is whole degrees (E89 found it truncated). The rail figures are differences of means, not
paired. The ±1 and ±pi tiles have seeds of their own (`e90.json` › `tiles.*.seed`); another draw of the sign pattern
is not measured.

## Files

`e90.json` (the registered reduction: every item, per pass), `runs.csv`, `reduce.txt`, the leakage arms
(`e90-leak0.1994 / 0.3803 / 0 .json`, `.csv`, `.txt`), `scored.json` and `results.md` (every rule, with the arms),
`dips-arm/` (the registered dips-removed arm: `dips.json`, `e90-nodips.json`, `scored-nodips.json`,
`results-nodips.md`), `code.sha256`, `logs/` (the queue and dry-run logs, the session's start and end config reads),
and `aifoundry3/kinds/` (the three passes' raw data and the smoke, `kinds-smoke-p9001`). The tiles and the
registration are in `tools/claims-v3/kinds/` (`E90.md`, `e90/`, `predictions-e90.json`, `make_e90.py`,
`make_predictions_e90.py`, `e90_common.py`, `run_e90.py`, `reduce_e90.py`, `score_e90.py`, `posthoc_dips_e90.py`,
`block_e90.sh`, `queue_e90.sh`, `run_e90.sh`, `collect_e90.sh`, `selftest_e90.py`).
