# E86: the real tensors' energy (GPT-2 small's numbers on aifoundry3, 600 MHz)

*Sat 31 Oct 2026 (week 44), Q130's evening round. Pre-registered in `190c1ac4` (committed 20:05:44, pushed 20:05:48
PDT, before the claim and the first launch): [`tools/claims-v3/kinds/E86.md`](../../../../tools/claims-v3/kinds/E86.md),
frozen numbers in `predictions-e86.json` (sha256 `e1f173c1…`). aifoundry3 card 0 at 600 MHz, 521.6 mV mean, TDP 0 /
threshold 65 °C read at the session's start (20:07:09) and end (20:40:56), never set. Nothing was written to the card,
and no `--reset-ms` was sent. Claim 1566287365469896725 in #community-lab, posted 20:06:48 PDT, released 20:41:29 PDT
(held 34.7 min; card time 33.8 min, 20:07:09–20:40:56, inside the registered 40 card-minutes;
[`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

*Corrected after verification, Sat 31 Oct 2026, at the desk, with no card touched and nothing re-run (§ [Corrections
after verification](#corrections-after-verification-sat-31-oct-2026), C1–C7): the int8 tiles warm the die less than
random int8 in 2 s, not as much; every ratio now names its baseline (over the type's all-zeros level, over idle, or of
the whole board), int8's included; E89 is cited as it was corrected; the int8 tiles hold 1–9% zero values, though no
zero word; the predictor's errors sit beside a no-model baseline; two push times and the 0.3803 arm's count are fixed;
and the claims are scoped to the three tiles measured. No number in `e86*.json`, `runs*.csv`, `scored*.json`,
`results*.md` or `posthoc/` changed, no registered verdict changed (4 PASS, 2 INCONCLUSIVE), and no frozen input
changed.*

**What ran.** Q130(n)'s nine real GPT-2 small tiles: layer 0's MLP up-projection, layer 6's MLP down-projection and
layer 6's attention QK^T, each in fp32, fp16 and int8. Beside them in every pass ran E78's six anchors (each type's
zeros and its random kind, three times a pass) and E78's three comparison kinds (fp32/fp16 `nn_like`, int8 `gauss_q`,
once a pass). The protocol is E78's, and E78's runner and reduction ran unchanged (sha256-checked). Five passes ran
(8610–8614). The registered random-anchor gate set pass 8614 aside, so **four passes are kept, the registered
minimum**. D is each tile's board power over its own type's all-zeros level (the registered quantity), S its board
power over idle, and p80 the window's whole board power (idle plus S, leakage-corrected); each ratio below says which
it divides. Each format ran one 16-token × 16-column window per matrix, so these are three tiles of one model, not
GPT-2 in general (C7). Every interval below is 95% over passes, t(0.975, 3) × SE.

## Results

**1. Over each format's all-zeros level (D), the real fp32 tiles cost 98.3–99.4% of the same pass's random data, the
fp16 tiles 97.1–99.6%, and the int8 tiles 78–89% of uniform random int8. Over idle (S) that is 98.5–99.6%,
97.2–99.7% and 85–92%; of the whole board's power (p80), 99.2–99.7%, 98.7–99.8% and 95.8–97.7%.** Per pass, each
tile's D was divided by the same pass's random kind, then averaged (`scored.json` › `tiles`):

| tile | D (W) | ±95% | D ÷ random | ±95% | − random (W) | ±95% | below random? | D ÷ nn_like / gauss_q (same format, same pass) | S over idle (W) | pJ/MAC (S) | pJ/MAC (D) | ΔT (°C) |
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

Averaged over a format's three tiles, D ÷ random is fp32 **0.988 ± 0.010**, fp16 **0.987 ± 0.014** and int8
**0.827 ± 0.050** (`scored.json` › `rules.E86-R3`). The same ratios against the three baselines, paired per pass in
the same way ([`corrections-check.txt`](corrections-check.txt) C2):

| tile | D ÷ random (over the type's zeros) | S ÷ random (over idle) | p80 ÷ random (whole board) |
|---|---|---|---|
| fp32 `l0_mlp_up` | 0.9863 ± 0.0310 | 0.9891 ± 0.0295 | 0.9939 ± 0.0139 |
| fp32 `l6_mlp_down` | 0.9937 ± 0.0012 | 0.9963 ± 0.0060 | 0.9974 ± 0.0010 |
| fp32 `l6_attn_qk` | 0.9833 ± 0.0023 | 0.9852 ± 0.0062 | 0.9923 ± 0.0016 |
| *fp32, three-tile mean* | *0.9878 ± 0.0103* | *0.9902 ± 0.0090* | *0.9945 ± 0.0040* |
| fp16 `l0_mlp_up` | 0.9950 ± 0.0162 | 0.9937 ± 0.0095 | 0.9975 ± 0.0062 |
| fp16 `l6_mlp_down` | 0.9957 ± 0.0175 | 0.9967 ± 0.0177 | 0.9983 ± 0.0072 |
| fp16 `l6_attn_qk` | 0.9710 ± 0.0120 | 0.9722 ± 0.0084 | 0.9868 ± 0.0040 |
| *fp16, three-tile mean* | *0.9872 ± 0.0142* | *0.9875 ± 0.0107* | *0.9942 ± 0.0057* |
| int8 `l0_mlp_up` | 0.8879 ± 0.1022 | 0.9202 ± 0.0823 | 0.9767 ± 0.0215 |
| int8 `l6_mlp_down` | 0.8109 ± 0.0441 | 0.8639 ± 0.0268 | 0.9624 ± 0.0066 |
| int8 `l6_attn_qk` | 0.7820 ± 0.0558 | 0.8520 ± 0.0200 | 0.9578 ± 0.0089 |
| *int8, three-tile mean* | *0.8269 ± 0.0501* | *0.8787 ± 0.0316* | *0.9657 ± 0.0110* |

So the int8 tiles save 11–22% of the power above int8's all-zeros level, 8–15% of the power above idle, and 2.3–4.2%
of the whole board's: int8's all-zeros level sits 2.5 W above idle, and the idle board draws 25.9 W. The fp32 tiles
save 0.6–1.7% over the zeros level and 0.3–0.8% of the whole board, the fp16 tiles 0.4–2.9% and 0.2–1.3%.

No real tile has an all-zero 32-bit operand word, so the zero gate, which acts on whole words, never fires on any of
them (gated fraction 0.000; `real.json` › `tiles.*.stats.*.zero_word_frac`). The fp32 and fp16 tiles hold no zero
value at all, so their savings come from the operand bits alone. The int8 tiles do hold zero values: 1.1–9.3% of each
operand's bytes (C4). Those count among the small values, and E86 does not split int8's saving between zeros and
small magnitudes.

pJ/MAC is the switching over idle (S, or D over the type's zeros) divided by the work the launch records completed
in the window (1.121 × 10⁹ ops/s for fp32/fp16, 1.926 × 10⁹ for int8), over 4,096, 8,192 or 16,384 MACs an op. Per
flop (fp32, fp16), halve it. ΔT is the firmware's whole-degree die reading over the 2 s window minus the launch
reading; E89 found that reading truncated.

**2. Q130(n)'s frozen predictions: every tile lies inside its interval. The direction holds in fp32 and int8 and is
unresolved in fp16.** The registered verdicts at the primary leakage slope (`scored.json` › `rules`):

| rule | registered | happened | verdict |
|---|---|---|---|
| **E86-R1** intervals | ≥ 7 of 9 inside Amendment 1's scoring intervals | **9 of 9** (also 9 of 9 inside the frozen intervals) | **PASS** |
| **E86-R2** accuracy | rms ≤ 2.0 / 2.0 / 1.0 W | rms 0.155 / 0.393 / 0.417 W; mean error −0.043 / +0.259 / +0.253 W (Amendment 1 expected 1.125 / 1.089 / 0.606). Beside it, labelled and not a rule: the no-model baseline "each tile costs E78's random kind" scores 0.353 / 0.446 / 1.237 W, and int8 against E78's `gauss_q` 0.802 W (C5) | **PASS** |
| **E86-R3** real below random | 3-tile mean ratio's 95% upper bound < 1 / 1 / 0.9 | fp32 0.9878 ± 0.0103 (PASS); fp16 0.9872 ± 0.0142 (upper bound 1.0014: INCONCLUSIVE); int8 0.8269 ± 0.0501 (PASS) | **INCONCLUSIVE** |
| **E86-R4** order against E78's network stand-ins | each tile on the frozen points' side of `nn_like` / `gauss_q` | fp32 3 of 3 above `nn_like` (+11.3 to +11.6 W); fp16 3 of 3 above (+3.8 to +4.3 W); int8 `l6_mlp_down` and `l6_attn_qk` below `gauss_q` (−0.72 ± 0.23, −0.92 ± 0.55 W), `l0_mlp_up` −0.17 ± 0.77 W (INCONCLUSIVE) | **INCONCLUSIVE** |
| **E86-R5** the session tie | every reference cell within ±0.50 W (float) / ±0.25 W (int8) of E78's | −0.135 to +0.052 W (fp32 randn −0.033, fp16 randn −0.084, int8 full +0.034, fp32 nn_like −0.091, fp16 nn_like +0.059, int8 gauss_q −0.135, anchor_pi +0.052) | **PASS** |
| **E86-S1** like with like | ≥ 7 of 9 ratios inside the ratio intervals | **9 of 9** (frozen: 9 of 9). Anchored on E78's random D: fp32 24.31–24.57 W, fp16 21.52–22.07 W, int8 5.52–6.27 W | **PASS** |

Tally: 4 PASS, 2 INCONCLUSIVE, no FAIL. Q130(n)'s points sit 0.10–0.63 W from the measurements: its predictor was
fitted on E78's 51 synthetic kinds before any card ran a real tile. Its 95% intervals (±2.4 / ±2.4 / ±1.3 W) are
2–29 times the measurement's, so R1 and S1 say little beyond "no gross miss". R2 says more: the errors run 1.5–7
times smaller than the nested-LOO rms Amendment 1 expected (7× fp32, 2.8× fp16, 1.5× int8). But the real fp32 and
fp16 tiles sit close to random data, so a baseline with no model scores well too: "each real tile costs E78's random
kind of its format" (E78's D, frozen in `predictions-e86.json` › `e78_reference`) misses by 0.353 / 0.446 / 1.237 W
rms, and "each int8 tile costs E78's `gauss_q`" by 0.802 W ([`corrections-check.txt`](corrections-check.txt) C5;
labelled, not a rule). The predictor beats that baseline 2.3× in fp32 and 3.0× in int8 (1.9× against `gauss_q`), and
only 1.13× in fp16. With three tiles a format, that describes these tiles; it does not establish the predictor's
skill. Q130(n) put the fp16 tiles 0.15–1.8% below its randn fit. The measured fp16 mean is 1.3% below random, but
this session's fp16 random anchor carries one dip-hit run (result 4), which widens the interval past 1.

**3. E78's synthetic network kinds stand in badly for these real fp32 and fp16 tiles, and well for the int8 ones.**
Over each type's zeros (D), in the same passes, the real fp32 tiles cost 1.88–1.90× E78's fp32 `nn_like` (relu(randn)
activations, half of them exact zeros, which gate lanes), and the real fp16 tiles 1.21–1.25× E78's fp16 `nn_like`.
GPT-2's activations in these windows have no exact zeros: `l0_mlp_up`'s A is a LayerNorm output, `l6_mlp_down`'s a
GELU output, and `l6_attn_qk`'s a query projection. int8 `gauss_q` (round(16·randn)) lands within 3–14% of the real
int8 tiles (0.86–0.97×).

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

**5. Heat follows the switching power: in 2 s the fp32 and fp16 tiles warm the die as much as random data of their
format, and the int8 tiles warm it less.** These are the firmware's whole-degree readings (E89 found them truncated),
each tile paired per pass with the same pass's random kind ([`corrections-check.txt`](corrections-check.txt) C1).
- **fp32 and fp16:** fp32 reads 3.17–3.25 °C against random's 3.19, differences −0.01 to +0.06 °C. fp16 reads
  2.75–2.90 °C against 2.89, differences −0.14 to +0.01 °C. All six intervals include 0.
- **int8:** the tiles read 1.00 / 1.00 / 0.95 °C against random int8's 1.125 ± 0.046 °C. The differences are
  −0.13 ± 0.05, −0.13 ± 0.05 and −0.18 ± 0.16 °C, and every interval excludes 0.

Their lower switching predicts this. At random int8's own 0.117 °C per W of S, the int8 tiles' S deficits of
0.77–1.42 W predict −0.09 to −0.17 °C. The float tiles' deficits (0.08–0.67 W) predict −0.01 to −0.08 °C, which the
whole-degree reading cannot resolve in four passes.

E89, as corrected (`ae24b0af`), measured six of E78's 16 int8 kinds and fp32 ones, and no real tile. Per board watt,
those kinds heat the die 1.04–1.11 times as much as fp32 random data (E89 `tables.txt` T1). Post hoc, per watt of the
minion rail, they are within about 2% of it (0.98–1.01, `posthoc.txt` POST HOC 2). E86 adds no finer heat
measurement.

## Registered against happened

- **Before the card.** The registration was committed at 20:05:44 and pushed at 20:05:48, the claim posted at
  20:06:48, and the first device access came at 20:07:09 (`logs/push-and-claim-times.txt`). `run_e86.sh setup` (no
  device access) found the reused E78 files and E86's files identical to the freeze and every real tile matching its
  sha256, and its dry pass made 34 launches, 9 of them on real tiles (`logs/e86-dry.log`, `logs/box-harness.sha256`).
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

- **For the blog's kinds table:** a "real model" row, measured on three tiles cut from GPT-2 small (one 16-token ×
  16-column window per matrix and format; int8 with one calibration, symmetric, activations per tensor and weights per
  output channel). Every ratio names its baseline:
  - **fp32:** 98.3–99.4% of random data's power above the type's all-zeros level (98.8% averaged over the three
    tiles), 98.5–99.6% of its power above idle, and 99.2–99.7% of its whole-board power. 5.72–5.79 pJ per
    multiply-add over idle.
  - **fp16:** 97.1–99.6% over the zeros level (98.7% averaged), 97.2–99.7% over idle and 98.7–99.8% of the whole
    board. 2.54–2.61 pJ per multiply-add over idle.
  - **int8:** 78–89% of uniform random int8 over int8's all-zeros level, 85–92% over idle and 95.8–97.7% of the whole
    board. 0.26–0.28 pJ/MAC.

  In these tiles, trained float numbers look like random bits to the multiplier. The quantised int8 tiles save 11–22%
  over the zeros level, which is 8–15% over idle and 2.3–4.2% of the board. No 32-bit operand word is all zero, so
  the zero gate never fires. 1–9% of the int8 values are zero, and those count among the small values. E86 does not
  split the saving between zeros and small magnitudes.
- **For the predictor (Q130(n)):** out of sample on these real tiles, it lands every tile inside its interval with
  errors of 0.16 / 0.39 / 0.42 W rms. It was fitted only on E78's synthetic kinds. A no-model baseline ("each tile
  costs E78's random kind") misses by 0.35 / 0.45 / 1.24 W. So the predictor's bit-statistics features add something
  over "real = random" in fp32 (2.3×) and int8 (3.0×, or 1.9× against `gauss_q`), and next to nothing in fp16 (1.13×).
  With three tiles a format, that is a description, not a test.
- **For E78's stand-ins:** `nn_like` is not what these float tiles cost. Its exact zeros make it a sparse kind, not a
  realistic one. `gauss_q` is a fair int8 stand-in for them.
- **For the instrument record (`14-card-behaviour.md`):** aifoundry3 card 0's board reading shows E82's
  launch-boundary dip too. It appears in E78's passes as well. A run gate on in-window dips would make the random-range
  gate fire less often. That needs a registration of its own.
- **Hub:** this answers the critic's item 3 (real tensors) for energy on aifoundry3, for three tiles of one model.
  E87 (speed, aifoundry2) and E91 (an aifoundry1 card-1 replicate) are separate lanes.

## Files

| file | what |
|---|---|
| `e86.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered reduction (reduce_e78.py unchanged, via reduce_e86.py), primary leakage slope |
| `e86-leak{0.1994,0.3803,0}.json`, `runs-leak*.csv`, `reduce-leak*.{txt,log}` | the registered leakage arms |
| `scored.json`, `results.md`, `score.log` | every rule, verdicts at the arms beside (score_e86.py) |
| `scored-leak*.json`, `results-leak*.md` | each arm scored on its own (details behind "at the arms") |
| `posthoc/` | the labelled post-hoc dip view: `dips.json`, `e86-nodips.{json,txt}`, `runs-nodips.csv`, `scored-nodips.json`, `results-nodips.md`; `dip-counts.txt` and `count_dips.py` (E78's and E86's passes) |
| `aifoundry3/kinds/p8610…p8614`, `kinds-smoke-p8601` | raw passes as the box wrote them (telemetry at 10 Hz, launch records, marks, dumped tiles, config reads, manifests) |
| `logs/` | the queue log, the dry pass, the box's harness sha256, the session's config reads, `et-lab-manifest`; `push-and-claim-times.txt` (the two commits' push times and the claim's post and release, added after verification) |
| `code.sha256` | every harness file, the freeze and the tiles, as reduced |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind Corrections after verification: every number it quotes, from the committed files (standard library only) |

Code: `tools/claims-v3/kinds/` (`E86.md`, `e86_common.py`, `run_e86.py`, `block_e86.sh`, `queue_e86.sh`, `run_e86.sh`,
`reduce_e86.py`, `score_e86.py`, `collect_e86.sh`, `selftest_e86.py`, `make_predictions_e86.py`,
`predictions-e86.json`; post hoc: `posthoc_dips_e86.py`). Reproduce from a copy of the raw passes at
`build/claims-v3/aifoundry3-e86/`: `PY=/usr/bin/python3 bash tools/claims-v3/kinds/collect_e86.sh 'p86[1-9][0-9]'
build/claims-v3/aifoundry3-e86`.

## Corrections after verification (Sat 31 Oct 2026)

An independent verifier checked E86 after the data commit (`a3c0b60d`). It re-ran the registered reduction and scorer
on the committed raw passes and got `e86*.json`, `runs*.csv` and `scored.json` back unchanged. It recomputed every
tile and rule from `runs.csv` and spot-checked window means against the raw telemetry. It found the registration
order, the frozen inputs, the unchanged E78 code, the post-hoc dip view and the safety record sound. It found two
major and five minor faults in how the numbers were stated. Each is corrected above, desk only: no card was touched,
nothing was re-run, and no registered prediction, rule, number or verdict changed (4 PASS, 2 INCONCLUSIVE). Every
number below is printed by [`corrections-check.py`](corrections-check.py) into
[`corrections-check.txt`](corrections-check.txt), under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: the int8 heat claim contradicted the data.** Result 5 said the real tiles warm the die as much in 2 s as the random kind of their format. For int8, paired per pass, they warm it less: −0.125 ± 0.046, −0.125 ± 0.046 and −0.175 ± 0.157 °C against int8 full, in every pass (−0.10 to −0.32), and every interval excludes 0. fp32 and fp16 differ by −0.14 to +0.06 °C, and all six of their intervals include 0 | Result 5 now says the float tiles warm the die as much as random data and the int8 tiles less (1.00 / 1.00 / 0.95 against 1.125 °C). Their S deficits of 0.77–1.42 W predict −0.09 to −0.17 °C at random int8's own 0.117 °C per W, and all of it is on the truncated whole-degree reading |
| C2 | **Major: the ratios never named their baseline, and int8's other baselines were missing.** Result 1's heading and What it changes quoted D ÷ random, D being power over each format's own all-zeros level, as "cost" or "switching power". The total-board ratios were given for fp32 and fp16 only, and fp32's started at "99.3%". The data commit's subject ("of random data's switching power") has the same gap | Result 1 has a table of D, S and p80 ratios for every tile and format, paired per pass. Over the zeros level int8 costs 78–89%, over idle 85–92%, and of the whole board 95.8–97.7%: a saving of 11–22%, 8–15% or 2.3–4.2%. The README's first arithmetic from item means (idle level plus S) gives 96.0–97.8%, the verifier's figure, and both are printed. fp32's whole-board ratio starts at 99.2% either way (99.23% paired, 99.25% from item means). The subject of `a3c0b60d` stays as committed: its percentages are over each format's all-zeros level |
| C3 | **E89 was cited in a form it had withdrawn.** Result 5 said "E89 measured every kind heating the die by the same amount per minion-rail watt (0.98–1.01), so the real tiles' heat is their D times that coefficient". E89's corrections (`ae24b0af`, 20:36:55, before this data commit) narrowed that to six of E78's 16 int8 kinds and fp32 ones and labelled the per-minion-rail result post hoc. The sentence also multiplied a board-watt D by a ratio defined per minion-rail watt | E89 is now cited as corrected: per board watt 1.04–1.11 times fp32 random data (`tables.txt` T1), and post hoc within about 2% per minion-rail watt (0.98–1.01, `posthoc.txt` POST HOC 2). E89 ran no real tile. The D-times-coefficient sentence is gone |
| C4 | **The int8 saving was said to come "from small integers, not from zeros".** The int8 tiles hold zero values: 3.1–9.3% of A's bytes and 1.1–5.5% of B's (`real.json` › `tiles.int8.*.stats.*.zero_elem_frac`). What none of them holds is an all-zero 32-bit word, which is what the zero gate needs. E86 does not measure where the saving comes from | Result 1 and What it changes now say: no 32-bit operand word is all zero, so the zero gate never fires. 1–9% of the int8 values are zero and count among the small values, and E86 does not split the saving between zeros and small magnitudes. The float tiles hold no zero value, so their wording stands |
| C5 | **The predictor's errors had no baseline beside them.** In fp32 and fp16 the real tiles sit near random data, so "each tile costs E78's random kind" scores 0.353 / 0.446 / 1.237 W rms (int8 against E78's `gauss_q`: 0.802 W). The predictor's are 0.155 / 0.393 / 0.417 W. What it changes said the predictor's "bit-statistics features carry over to real tensors" | The baseline sits in the R2 row and in result 2. What it changes says the features add something over "real = random" in fp32 (2.3×) and int8 (3.0×, 1.9× against `gauss_q`), next to nothing in fp16 (1.13×), and that three tiles a format describe rather than test |
| C6 | **Factual slips.** "Pushed 20:05:44" was `190c1ac4`'s commit time; GitHub's push record reads 20:05:48. The result handed on put `a3c0b60d`'s push at "~20:53"; it was 20:48:15. It also said the 0.3803 leakage arm set three passes aside by the zeros-line gate; that gate set two aside (8610, 8613), and 8614 fell to the random-range gate, as the Leakage bullet above already said. While checking, the desk also found "34.6 min, inside the registered 40": the claim was held 34.7 min (20:06:48.140–20:41:29), and the registered 40 counts card-minutes, which were 33.8 (20:07:09–20:40:56) | The header and Registered against happened give the commit and push times, the release at 20:41:29, the hold and the card time (`logs/push-and-claim-times.txt`, new). The result handed on is corrected the same way |
| C7 | **The statements reached beyond what ran.** "GPT-2 small's MLP and attention operands", "Trained float numbers" and "the same layers" rest on one window per matrix and format. E86.md's "What the rules cannot say" already says so ("One tile a cell is a draw"). int8 uses one simple calibration: Q130(n)'s predictor puts four other common ones at 0.735–0.869× of `full`, and none of them ran on the card (`real/amendment-1.json` › `calibration_sensitivity`). "fp16 tiles 1.2×" did not say it meant E78's fp16 `nn_like` | What ran, result 3, What it changes and the hub line now say three tiles cut from GPT-2 small: one 16-token × 16-column window per matrix and format, and int8 with one calibration. The `nn_like` ratios name their format, and the windows are listed in C7 |

One proposed fix was not taken as written. C7 asked for "int8 with one per-tensor calibration". `real.json` quantises
the activations per tensor and the weights per output channel (`conventions.int8`; `tiles.int8.*.quantisation`), so the
text says "one calibration, symmetric: activations per tensor, weights per output channel".
