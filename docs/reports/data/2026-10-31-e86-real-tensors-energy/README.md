# E86: the real tensors' energy (GPT-2 small's numbers on aifoundry3, 600 MHz)

*Sat 31 Oct 2026 (week 44), Q130's evening round. Pre-registered in `190c1ac4` (pushed 20:05:44 PDT, before the claim
and the first launch): [`tools/claims-v3/kinds/E86.md`](../../../../tools/claims-v3/kinds/E86.md), frozen numbers in
`predictions-e86.json` (sha256 `e1f173c1…`). aifoundry3 card 0 at 600 MHz, 521.6 mV mean, TDP 0 / threshold 65 °C
read at the session's start (20:07:09) and end (20:40:56), never set. Nothing was written to the card, and no
`--reset-ms` was sent. Claim 1566287365469896725 in #community-lab, posted 20:06:48 PDT, released 20:41 PDT (34.6 min,
inside the registered 40).*

**What ran.** Q130(n)'s nine real GPT-2 small tiles: layer 0's MLP up-projection, layer 6's MLP down-projection and
layer 6's attention QK^T, each in fp32, fp16 and int8. Beside them in every pass ran E78's six anchors (each type's
zeros and its random kind, three times a pass) and E78's three comparison kinds (fp32/fp16 `nn_like`, int8 `gauss_q`,
once a pass). The protocol is E78's, and E78's runner and reduction ran unchanged (sha256-checked). Five passes ran
(8610–8614). The registered random-anchor gate set pass 8614 aside, so **four passes are kept, the registered
minimum**. D is each tile's board power over its own type's zeros. Every interval below is 95% over passes,
t(0.975, 3) × SE.

## Results

**1. Real fp32 and fp16 numbers cost within 0.4–2.9% of random numbers. Real int8 costs 78–89% of uniform random
int8.** Per pass, each tile's D was divided by the same pass's random kind, then averaged (`scored.json` › `tiles`):

| tile | D (W) | ±95% | ÷ random | ±95% | − random (W) | ±95% | below random? | ÷ nn_like / gauss_q | S over idle (W) | pJ/MAC (S) | pJ/MAC (D) | ΔT (°C) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 `l0_mlp_up` | 24.353 | 0.777 | 0.9863 | 0.0310 | −0.339 | 0.766 | inconclusive | 1.882 | 26.374 | 5.745 | 5.305 | 3.25 |
| fp32 `l6_mlp_down` | 24.537 | 0.084 | **0.9937** | 0.0012 | −0.155 | 0.030 | yes | 1.896 | 26.567 | 5.787 | 5.345 | 3.24 |
| fp32 `l6_attn_qk` | 24.278 | 0.138 | **0.9833** | 0.0023 | −0.413 | 0.056 | yes | 1.876 | 26.270 | 5.722 | 5.288 | 3.17 |
| fp16 `l0_mlp_up` | 21.966 | 0.267 | 0.9950 | 0.0162 | −0.112 | 0.356 | inconclusive | 1.244 | 23.851 | 2.597 | 2.392 | 2.90 |
| fp16 `l6_mlp_down` | 21.982 | 0.163 | 0.9957 | 0.0175 | −0.096 | 0.385 | inconclusive | 1.245 | 23.923 | 2.605 | 2.394 | 2.77 |
| fp16 `l6_attn_qk` | 21.438 | 0.251 | **0.9710** | 0.0120 | −0.640 | 0.270 | yes | 1.214 | 23.334 | 2.541 | 2.335 | 2.75 |
| int8 `l0_mlp_up` | 6.291 | 0.618 | **0.8879** | 0.1022 | −0.799 | 0.748 | yes | 0.974 | 8.836 | 0.280 | 0.199 | 1.00 |
| int8 `l6_mlp_down` | 5.748 | 0.262 | **0.8109** | 0.0441 | −1.343 | 0.339 | yes | 0.889 | 8.296 | 0.263 | 0.182 | 1.00 |
| int8 `l6_attn_qk` | 5.543 | 0.316 | **0.7820** | 0.0558 | −1.548 | 0.429 | yes | 0.859 | 8.182 | 0.259 | 0.176 | 0.95 |
| *random, same session* | fp32 24.691 ± 0.111; fp16 22.078 ± 0.313; int8 7.090 ± 0.222 | | 1 | | | | | | 26.665 / 24.003 / 9.604 | 5.808 / 2.614 / 0.304 | | 3.19 / 2.89 / 1.12 |

Averaged over a format's three tiles: fp32 **0.988 ± 0.010**, fp16 **0.987 ± 0.014** and int8 **0.827 ± 0.050** of
random (`scored.json` › `rules.E86-R3`). In total board power (idle 25.87 W plus S) the fp32 tiles draw 99.3–99.8%
of random's and the fp16 tiles 98.7–99.8%. No real tile has a zero word, so the zero gate never fires on any of them (gated fraction
0.000, `real.json`). The float savings come from the operand bits alone. pJ/MAC is the switching over idle (S, or D
over the type's zeros) divided by the work the launch records completed in the window (1.121 × 10⁹ ops/s for
fp32/fp16, 1.926 × 10⁹ for int8), over 4,096, 8,192 or 16,384 MACs an op. Per flop (fp32, fp16), halve it. ΔT is the
firmware's whole-degree die reading over the 2 s window minus the launch reading; E89 found that reading truncated.

**2. Q130(n)'s frozen predictions: every tile lies inside its interval. The direction holds in fp32 and int8 and is
unresolved in fp16.** The registered verdicts at the primary leakage slope (`scored.json` › `rules`):

| rule | registered | happened | verdict |
|---|---|---|---|
| **E86-R1** intervals | ≥ 7 of 9 inside Amendment 1's scoring intervals | **9 of 9** (also 9 of 9 inside the frozen intervals) | **PASS** |
| **E86-R2** accuracy | rms ≤ 2.0 / 2.0 / 1.0 W | rms 0.155 / 0.393 / 0.417 W; mean error −0.043 / +0.259 / +0.253 W (Amendment 1 expected 1.125 / 1.089 / 0.606) | **PASS** |
| **E86-R3** real below random | 3-tile mean ratio's 95% upper bound < 1 / 1 / 0.9 | fp32 0.9878 ± 0.0103 (PASS); fp16 0.9872 ± 0.0142 (upper bound 1.0014: INCONCLUSIVE); int8 0.8269 ± 0.0501 (PASS) | **INCONCLUSIVE** |
| **E86-R4** order against E78's network stand-ins | each tile on the frozen points' side of `nn_like` / `gauss_q` | fp32 3 of 3 above `nn_like` (+11.3 to +11.6 W); fp16 3 of 3 above (+3.8 to +4.3 W); int8 `l6_mlp_down` and `l6_attn_qk` below `gauss_q` (−0.72 ± 0.23, −0.92 ± 0.55 W), `l0_mlp_up` −0.17 ± 0.77 W (INCONCLUSIVE) | **INCONCLUSIVE** |
| **E86-R5** the session tie | every reference cell within ±0.50 W (float) / ±0.25 W (int8) of E78's | −0.135 to +0.052 W (fp32 randn −0.033, fp16 randn −0.084, int8 full +0.034, fp32 nn_like −0.091, fp16 nn_like +0.059, int8 gauss_q −0.135, anchor_pi +0.052) | **PASS** |
| **E86-S1** like with like | ≥ 7 of 9 ratios inside the ratio intervals | **9 of 9** (frozen: 9 of 9). Anchored on E78's random D: fp32 24.31–24.57 W, fp16 21.52–22.07 W, int8 5.52–6.27 W | **PASS** |

Tally: 4 PASS, 2 INCONCLUSIVE, no FAIL. Q130(n)'s points sit 0.10–0.63 W from the measurements: its predictor was
fitted on E78's 51 synthetic kinds before any card ran a real tile. Its 95% intervals (±2.4 / ±2.4 / ±1.3 W) are
2–29 times the measurement's, so R1 and S1 say little beyond "no gross miss". R2 says more: the errors run 1.5–7
times smaller than the nested-LOO rms Amendment 1 expected (7× fp32, 2.8× fp16, 1.5× int8). Q130(n) put the fp16 tiles 0.15–1.8% below its randn fit. The
measured fp16 mean is 1.3% below random, but this session's fp16 random anchor carries one dip-hit run (result 4),
which widens the interval past 1.

**3. E78's synthetic network kinds stand in badly for real fp32 and fp16 numbers, and well for real int8.** The real
fp32 tiles cost 1.88–1.90× E78's `nn_like` (relu(randn) activations, half of them exact zeros, which gate lanes), and
the real fp16 tiles 1.21–1.25×. GPT-2's activations here have no exact zeros: `l0_mlp_up`'s A is a LayerNorm output,
`l6_mlp_down`'s a GELU output, and `l6_attn_qk`'s a query projection. int8 `gauss_q` (round(16·randn)) lands within
3–14% of the real int8 tiles (0.86–0.97×).

**4. An instrument property, not the data: aifoundry3's board meter sometimes reads one or two samples 5–20 W low
just after a launch boundary.** It is E82's card-1 dip (E82 amendment A2), and it occurs on this card too. With E82's
definition (`board_w[i] < min(board_w[i−2], board_w[i+2]) − 4.0 W`), the five passes hold 40 dips. Thirteen of them
fall inside power windows, 12–151 ms after a launch boundary, each 1–2 samples at 27–44 W against neighbours of
35–53 W (`posthoc/dips.json`). E78's six passes on this card hold 5–19 dips each, 1–7 of them inside power windows
(`posthoc/dip-counts.txt`), so the property predates E86. Two of the dip-hit runs read low and are visible in the
per-pass values: fp32 `l0_mlp_up` in pass 8611 reads 23.63 W against 24.51–24.70 W, and int8 `l0_mlp_up` in pass
8611 reads 5.72 W against 6.41–6.54 W. Those two runs make those tiles' wide intervals. In pass 8614, two dip samples
(33.18 W against 52.8–53.1 W) sit inside the third `fp32.randn` run's window. That run read 2.0 W low, and **the
registered gate (random anchor range ≤ 1.0 W) set the pass aside**.

*Labelled POST-HOC view, written after the reduction. It is not a rule and it moves no verdict.* The same registered
reduction and scorer ran on copies of the five passes with the dip samples removed (`posthoc_dips_e86.py`;
`posthoc/scored-nodips.json`, `posthoc/results-nodips.md`). Every gate passes, so all five passes are kept, and the
intervals narrow:

| | fp32 3-tile mean ÷ random | fp16 | int8 | fp32 tiles | fp16 tiles | int8 tiles |
|---|---|---|---|---|---|---|
| registered (4 passes) | 0.9878 ± 0.0103 | 0.9872 ± 0.0142 | 0.8269 ± 0.0501 | 0.983–0.994 | 0.971–0.996 | 0.782–0.888 |
| post hoc, dips removed (5 passes) | 0.9910 ± 0.0002 | 0.9832 ± 0.0039 | 0.8288 ± 0.0087 | 0.983–0.997 | 0.965–0.992 | 0.776–0.905 |

With the dips removed, R3 reads PASS in every format, R4's int8 `l0_mlp_up` stays INCONCLUSIVE (−0.08 ± 0.19 W
against `gauss_q`), and R1, R2, R5 and S1 are unchanged (5 PASS, 1 INCONCLUSIVE). The registered verdicts above stand.

**5. Heat follows the switching power.** On the whole-degree reading, the real tiles warm the die as much in 2 s as
the random kind of their format: fp32 3.17–3.25 °C against 3.19, fp16 2.75–2.90 against 2.89, int8 0.95–1.00
against 1.12. E89 measured every kind heating the die by the same amount per minion-rail watt (0.98–1.01), so the
real tiles' heat is their D times that coefficient. E86 adds no finer heat measurement.

## Registered against happened

- **Before the card.** The registration was pushed at 20:05:44, the claim posted at 20:06:48, and the first device
  access came at 20:07:09. `run_e86.sh setup` (no device access) found the reused E78 files and E86's files identical
  to the freeze and every real tile matching its sha256, and its dry pass made 34 launches, 9 of them on real tiles
  (`logs/e86-dry.log`, `logs/box-harness.sha256`).
- **Card state, read only.** `ettelem config` under the card lock (`timeout 10`) read TDP 0, threshold 65 °C,
  600 MHz and 523 mV at 20:07:09 and again at 20:40:56 (`logs/config_session_*.json`), and so did each pass's two
  reads (`aifoundry3/kinds/p86*/config_*.json`). `et-who` read "No process holds an ET-SoC-1 device node or card lock"
  before the claim, before the queue and after it.
- **Smoke, pass 8601** (20:07:10–20:07:53): seven 2 s runs, three of them on real tiles. Every record was ok, cycles
  per op were 546.0 / 546.0 / 318.0, and launch coverage was 0.9975–0.998.
- **Passes.** The queue ran 8610–8614 between 20:08:03 and 20:40:29: 6.7, 6.3, 6.2, 6.0 and 6.1 min, 160 runs, no run
  skipped, no run-gate failure. At 20:40:44 the registered budget rule stopped it before 8615: 32 min had elapsed,
  and the longest pass, 6.7 min, would have ended past the 36 card-minute queue budget. The registration expected
  six passes. The first pass started from a cold die (52 °C) and set the projection at 6.7 min, so the rule allowed
  five. Pass 8614 was set aside by the registered random-range gate (result 4), leaving **four kept passes, 128 runs**.
- **Leakage.** The primary `auto` slope is 0.2290 W/°C over 133 runs (E78's was 0.1994). The registered arms:
  - **0.1994** gives the same verdicts as the primary.
  - **0** moves R3 to PASS. It also moves R5 to FAIL, with fp32 randn at +0.63 W and fp16 nn_like at +0.50 W. That
    arm compares E86's uncorrected D with E78's values at E78's primary slope.
  - **0.3803** sets two more passes aside by the registered zeros-line gate (8610 `int8.zeros` departs −0.284 W, 8613
    `fp16.zeros` −0.300 W). That leaves two passes, so every rule is NOT SCORED at that arm (`scored-leak0.3803.json`).

  `scored.json` flags every rule `slope_sensitive`, because the scorer counts NOT SCORED at an arm as a move. The
  verdicts that actually move between scored arms are R3 and R5, both at k = 0.
- **Checks (E78-R5's, reported):**
  - idle consistency, median |S − S0 − D|: 0.071 W (≤ 0.15);
  - rail lag re-fitted: median 1.00 s (in [0.80, 1.15]);
  - duty: 0.9960–0.9967 (in [0.990, 1.000]);
  - carry-over: 0.0024 ± 0.0016 W/W (≤ 0.01);
  - every dumped tile equals its registered sha256 (a run gate, no failure);
  - the idle level is 25.873 ± 0.017 W.
- **Departures.** None from the registered protocol, analysis or rules. One view was added after the data, the dip
  removal in result 4. It is labelled post hoc and moves no verdict. A scratch one-liner that re-checked the smoke's
  tile dumps failed on a filename parse. It was not part of the harness: the reduction's dump gate checked every
  dump.

## What it changes

- **For the blog's kinds table:** a "real model" row, measured. In fp32 and fp16, GPT-2 small's MLP and attention
  operands cost 97–99.6% of iid random data's switching power (98.7–98.8% averaged over the three tiles), 5.72–5.79
  and 2.54–2.61 pJ per multiply-add over idle. In int8 they cost 78–89% of uniform random int8, 0.26–0.28 pJ/MAC. Trained
  float numbers look like random bits to the multiplier. A quantised int8 tensor saves 11–22% because its values are
  small integers, not because of zeros.
- **For the predictor (Q130(n)):** out of sample on real data, it lands every tile inside its interval with errors of
  0.16 / 0.39 / 0.42 W rms. It was fitted only on E78's synthetic kinds, and its bit-statistics features carry over
  to real tensors.
- **For E78's stand-ins:** `nn_like` is not what network numbers cost. Its exact zeros make it a sparse kind, not a
  realistic one. `gauss_q` is a fair int8 stand-in.
- **For the instrument record (`14-card-behaviour.md`):** aifoundry3 card 0's board reading shows E82's
  launch-boundary dip too. It appears in E78's passes as well. A run gate on in-window dips would make the random-range
  gate fire less often. That needs a registration of its own.
- **Hub:** this answers the critic's item 3 (real tensors) for energy on aifoundry3. E87 (speed, aifoundry2) and E91
  (an aifoundry1 card-1 replicate) are separate lanes.

## Files

| file | what |
|---|---|
| `e86.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered reduction (reduce_e78.py unchanged, via reduce_e86.py), primary leakage slope |
| `e86-leak{0.1994,0.3803,0}.json`, `runs-leak*.csv`, `reduce-leak*.{txt,log}` | the registered leakage arms |
| `scored.json`, `results.md`, `score.log` | every rule, verdicts at the arms beside (score_e86.py) |
| `scored-leak*.json`, `results-leak*.md` | each arm scored on its own (details behind "at the arms") |
| `posthoc/` | the labelled post-hoc dip view: `dips.json`, `e86-nodips.{json,txt}`, `runs-nodips.csv`, `scored-nodips.json`, `results-nodips.md`; `dip-counts.txt` and `count_dips.py` (E78's and E86's passes) |
| `aifoundry3/kinds/p8610…p8614`, `kinds-smoke-p8601` | raw passes as the box wrote them (telemetry at 10 Hz, launch records, marks, dumped tiles, config reads, manifests) |
| `logs/` | the queue log, the dry pass, the box's harness sha256, the session's config reads, `et-lab-manifest` |
| `code.sha256` | every harness file, the freeze and the tiles, as reduced |

Code: `tools/claims-v3/kinds/` (`E86.md`, `e86_common.py`, `run_e86.py`, `block_e86.sh`, `queue_e86.sh`, `run_e86.sh`,
`reduce_e86.py`, `score_e86.py`, `collect_e86.sh`, `selftest_e86.py`, `make_predictions_e86.py`,
`predictions-e86.json`; post hoc: `posthoc_dips_e86.py`). Reproduce from a copy of the raw passes at
`build/claims-v3/aifoundry3-e86/`: `PY=/usr/bin/python3 bash tools/claims-v3/kinds/collect_e86.sh 'p86[1-9][0-9]'
build/claims-v3/aifoundry3-e86`.
