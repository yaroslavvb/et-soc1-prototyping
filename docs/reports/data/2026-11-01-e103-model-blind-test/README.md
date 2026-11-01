# E103: a blind test built to break the bench's power model (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, item 6 of the kinds page's section 11. Pre-registered in `b5f1e5d7`, pushed 01:37:31 PST, before the claim and the first launch: [`tools/claims-v3/kinds/E103.md`](../../../../tools/claims-v3/kinds/E103.md), frozen numbers in `predictions-e103.json` (sha256 `7ac59cae…`), the scorer `score_e103.py` and its self-test in the same commit. aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz in every sample, 498.7 mV mean, TDP 65 W / threshold 65 °C read under the card lock at both ends of every block, never set. Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566397290267025444 in #community-lab, posted 02:23:36 PST, released by editing it at 02:51 PST: 27.7 min. Smoke 10301 at 02:23:47; queue 02:24:38–02:50:23 PST, 1,545 s. **No amendments.***

**In plain words.** The bench's model has four constants, fitted on 33 kinds of number on another card. From 215 candidates I chose the 30 tiles where it and the simple predictors disagree most, and froze every prediction. **It held: 0.31 W rms over 23 float tiles running from 3 to 24 W, where the best simple predictor missed by 3.96 W and E92's flop-price refit by 1.78 W.** int8, on its own constants, reads 0.37 W. It is not perfect, and the misses have a pattern: all five tiles outside their intervals are fp32, and the worst is a near-cancelling sum, 0.89 W low.

## Results

**1. Registered against what happened** ([`scored.json`](scored.json), [`results.md`](results.md)). All three passes kept, 148 of 148 runs.

| rule | what | threshold | result | verdict | what I expected, frozen |
|---|---|---|---:|---|---|
| **E103-R1** | **rms(D − M4), 23 float tiles** | PASS ≤ 0.60 W, FAIL > 1.00 W | **0.314 W** [0.197, 0.425], bias −0.05 W | **PASS** | PASS near 0.5 W |
| **E103-R2** | beats the named null, Q130(n) | gap's 95% above 0 | **3.646 W** [2.142, 5.435]: 0.314 against 3.960 W (0.320 against 2.788 W without `fp32.z_dn_ab`) | **PASS** | PASS |
| **E103-R3** | beats E92's flop-price refit | the same | **1.462 W** [0.324, 2.567]: 0.314 against 1.775 W (0.320 against 0.913 W without `fp32.z_dn_ab`) | **PASS** | PASS, narrowly, without the denormal tile |
| **E103-R4** | **rms(D − I3), 7 int8 tiles** | PASS ≤ 0.40 W, FAIL > 0.80 W | **0.365 W** [0.200, 0.524], bias +0.15 W | **PASS**, arm-sensitive | INCONCLUSIVE |
| **E103-R5** | I3 beats Q130(n) | gap's 95% above 0 | 0.542 W [0.070, 0.990]: 0.365 against 0.907 W | **PASS**, arm-sensitive | |
| **E103-R6** | the bus price earns its term: M4 beats M2 | gap's 95% above 0 | **0.265 W** [0.162, 0.364]: 0.314 against 0.579 W | **PASS** | PASS |
| **E103-R7** | D inside the frozen 95% interval | PASS ≥ 80%, FAIL < 50% | **25 of 30, 83%** | **PASS**, arm-sensitive | INCONCLUSIVE or PASS |
| **E103-R8** | the A side: mean (D − T)/(M4 − T), T the clock term | PERSISTS if upper bound < 0.95; GONE if inside [0.95, 1.05] | 0.947 ± 0.037 | **UNRESOLVED** | PERSISTS |
| **E103-R9** | gated float tiles: mean D − M4 | PASS inside ±0.30 W; FAIL if it excludes ±0.30 W | +0.151 ± 0.382 W, n = 5 (M2: +0.598 W) | **INCONCLUSIVE** | PASS |
| **E103-S1** | the session tie against E82, dips removed | ±0.50 W, int8 ±0.25 W | `fp32.randn` 24.07 (24.00), `fp16.randn` 21.61 (21.49), `anchor_pi` 8.04 (8.14), `int8.full` 6.96 (6.84) | **PASS** | |

Two things I expected came out better than I said: R1's 0.31 W and R4's PASS. Two came out weaker: R8 and R9 are unresolved, because five tiles do not bound them. **R9's interval is driven by one tile, `fp32.x_e_g`, +0.62 W;** the other four read −0.23 to +0.25 W.

**2. By format, every model, the same tiles** (`scored.json` `primary.reported`; rms in W, bias is predicted minus measured):

| | n | **M4 or I3** | M2 | Q130(n), the null | E92's flop price | the gate law |
|---|---:|---:|---:|---:|---:|---:|
| fp32 | 13 | **0.392** (−0.14) | 0.702 (−0.14) | 4.674 (+1.01) | 2.190 (+0.89) | 8.550 (+5.90) |
| fp16 | 10 | **0.162** (+0.06) | 0.360 (−0.08) | 2.768 (+0.71) | 1.006 (−0.14) | 5.642 (+3.79) |
| int8 | 7 | **0.365** (+0.15) | 0.381 (+0.01) | 0.907 (+0.03) | | 1.942 (+0.95) |

**3. Every tile.** D is 95% over three passes; ⚠ marks D outside the frozen interval.

| tile | why it is here | D, W | **M4 or I3 [95%]** | D − M | M2 | Q130(n) | flop |
|---|---|---:|---:|---:|---:|---:|---:|
| `fp32.c_near_rand` ⚠ | near-cancelling sums | 19.15 ± 0.62 | **18.26** [17.56, 18.96] | **+0.89** | 17.80 | 16.23 | 20.55 |
| `fp32.x_e_g` ⚠ | exponent spread and a 47% gate | 14.79 ± 0.40 | **14.17** [13.81, 14.53] | **+0.62** | 13.86 | 11.77 | 14.16 |
| `fp32.h_a_all_pi` ⚠ | A side, busy partner | 14.31 ± 0.29 | **14.81** [14.35, 15.27] | **−0.50** | 15.45 | 17.72 | 14.53 |
| `fp32.s_bhalf_alt` ⚠ | moving sums, adder alternates each cycle | 23.91 ± 0.29 | **23.46** [23.05, 23.87] | **+0.45** | 23.79 | 22.82 | 23.66 |
| `fp32.t_4_23` ⚠ | A truncated to 4 bits | 20.17 ± 0.56 | **19.73** [19.33, 20.13] | **+0.44** | 19.53 | 18.16 | 20.64 |
| `fp32.g_bcol500` | half of B's columns zero | 14.28 ± 0.04 | 14.04 [13.66, 14.41] | +0.25 | 13.78 | 10.74 | 13.26 |
| `fp32.o_a_maxflip_4_pi` | A's order, busy partner | 10.32 ± 0.16 | 10.53 [10.14, 10.91] | −0.21 | 10.96 | 14.53 | 11.86 |
| `fp32.h_a_lo_pi` | A side, low bits, busy partner | 10.52 ± 0.33 | 10.71 [10.30, 11.11] | −0.19 | 11.15 | 15.05 | 11.81 |
| `fp32.x_s_t` | sign alternation and truncation | 17.18 ± 0.21 | 17.02 [16.64, 17.39] | +0.16 | 16.96 | 15.10 | 17.41 |
| `fp32.s_abs` | moving sums, always adds | 22.35 ± 0.27 | 22.44 [22.00, 22.87] | −0.09 | 22.93 | 23.79 | 22.39 |
| `fp32.z_dn_ab` | denormal words both sides | 9.42 ± 0.26 | 9.48 [9.11, 9.86] | −0.06 | 9.19 | **23.19** | 16.78 |
| `fp32.e_a` | A's exponents spread | 10.71 ± 0.06 | 10.69 [10.31, 11.06] | +0.02 | 10.62 | 12.09 | 11.02 |
| `fp32.g_relu_shift15` | 91% gate, operands moving on closed lanes | 3.06 ± 0.43 | 3.05 [2.70, 3.41] | +0.01 | 2.36 | 2.15 | 3.60 |
| `fp16.e_ab` | exponents spread, both sides | 13.32 ± 0.33 | 13.68 [13.28, 14.08] | −0.35 | 13.19 | 16.40 | 13.47 |
| `fp16.g_bcol500` | half of B's columns zero | 11.79 ± 0.17 | 12.02 [11.66, 12.38] | −0.23 | 11.83 | 9.75 | 11.61 |
| `fp16.c_near8` | near-cancelling sums | 17.75 ± 0.32 | 17.55 [17.14, 17.97] | +0.20 | 17.37 | 13.75 | 17.23 |
| `fp16.g_relu_shift15` | 85% gate, operands moving on closed lanes | 4.24 ± 0.20 | 4.13 [3.77, 4.49] | +0.11 | 3.34 | 2.74 | 4.25 |
| `fp16.s_arow_adds` | A's sign by row, always adds | 19.42 ± 0.40 | 19.52 [19.14, 19.91] | −0.10 | 19.40 | 21.78 | 18.99 |
| `fp16.h_a_all` | A side | 12.39 ± 0.32 | 12.48 [12.10, 12.86] | −0.09 | 12.81 | 16.32 | 11.08 |
| `fp16.f_hi1` | one element of each word 1.0 | 15.85 ± 0.23 | 15.93 [15.56, 16.30] | −0.08 | 15.80 | 17.40 | 15.66 |
| `fp16.x_e_s` | exponents spread and alternation | 23.49 ± 0.17 | 23.42 [23.04, 23.79] | +0.07 | 23.33 | 21.47 | 26.08 |
| `fp16.o_a_maxflip_1` | A's order | 11.31 ± 0.26 | 11.37 [10.98, 11.77] | −0.06 | 11.65 | 14.67 | 10.37 |
| `fp16.t_10_1` | B truncated to 1 bit | 18.51 ± 0.11 | 18.53 [18.15, 18.91] | −0.02 | 18.52 | 20.94 | 17.96 |
| `int8.i_a127_bfull` | A still, B random | 2.43 ± 0.71 | 3.16 [2.25, 4.07] | −0.73 | 2.21 | 1.76 | |
| `int8.i_w8_1` | B one bit wide | 5.44 ± 0.70 | 5.83 [5.26, 6.41] | −0.39 | 5.93 | 6.02 | |
| `int8.i_sort_a` | A sorted | 6.23 ± 0.72 | 5.87 [5.28, 6.46] | +0.36 | 5.55 | 6.29 | |
| `int8.i_bpair875` | 88% gate | 2.02 ± 0.51 | 1.81 [1.26, 2.36] | +0.21 | 1.96 | 0.86 | |
| `int8.i_afull_b127` | A random, B still | 6.16 ± 0.28 | 6.36 [5.80, 6.93] | −0.20 | 6.34 | 7.86 | |
| `int8.i_w2_2` | both sides two bits wide | 5.30 ± 0.40 | 5.46 [4.83, 6.08] | −0.16 | 5.77 | 5.74 | |
| `int8.i_arow500` | half of A's rows zero | 4.18 ± 0.57 | 4.30 [3.74, 4.87] | −0.12 | 4.07 | 3.44 | |

**4. How good the model is, per format, on what, and where it fails** ([`score_all.txt`](score_all.txt), `score_all.json`, `score_all.py`). This answers item 6.

**Blind**, predictions committed before the data reached main, with none of it read first. rms in W (bias):

| set | card | fp32 | fp16 | int8 |
|---|---|---:|---:|---:|
| **E95, 30 real-tensor tiles**, M4 and I3 (`b995463e`; data `ab23b1aa`) | aifoundry3, no scale | **0.102** (+0.08), n 11 | **0.212** (+0.17), n 8 | **0.166** (0.00), n 11 |
| **E103, 30 tiles built to break it**, M4 and I3 (`b5f1e5d7`) | card 1, E82's scale | **0.392** (−0.14), n 13 | **0.162** (+0.06), n 10 | **0.365** (+0.15), n 7 |
| **Both pooled** | | **0.297**, n 24 | **0.186**, n 18 | **0.262**, n 18 |
| the null, Q130(n), on both | | 3.457 | 2.120 | 0.857 |
| the first model, M2, on both (`2b7ece4a`, `b5f1e5d7`) | | 0.591 | 0.380 | 0.326 |
| E92's 32 tiles, an earlier two-term form (`de545f0c`) | aifoundry3 | 0.668 (−0.42), n 23 | 0.389 (−0.21), n 9 | |

**Constants first:** M4's constants were committed before E102's data, and E102's lane counted its tiles before its data, but I did the arithmetic afterwards. E102's single-bit prices, balanced and all-in, on card 1, each over its own zero: fp32 B 0.237 and 0.224 W, fp32 A 0.126 and 0.216 W, fp16 0.096 and 0.232 W, int8 B 0.101 W. M2, frozen in E102's own registration: 0.254, 0.238, 0.197, 0.210, 0.147, 0.247, 0.179 W.

**Post hoc,** M4's form chosen after these were read, the constants not fitted on them: E86 0.145, E90 0.220, E92 0.242, E88 0.229, E94 0.176 W in floats; int8 E86 0.256, E88 0.365, E94 0.295 W. Single-bit ladders: E65 0.185 W, E67's A bits 0.241 W, E70 low 0.289 W.

**Where it fails, plainly:**

- **Near-cancelling sums in fp32:** `c_near_rand` 0.89 W low. A sum that nearly cancels moves the normaliser in ways this count underweights. fp16's `c_near8` is fine.
- **The A side and high-toggle ladders with a busy partner run high, and the fitted terms do not fix it.** E103's fp32 A tiles read 0.92–0.93 of the predicted switching, fp16's 0.98 (R8). On the older ladders, post hoc: E60's low bits with A = π 0.95 W, measured/predicted 0.90; E67's two-flip grid 0.69 W, 0.90; E70's A ladder 0.65 W, 0.86.
- **Adder alternation on moving sums runs low:** `s_bhalf_alt` 0.45 W low. It reads +1.56 ± 0.11 W over `s_abs` (different draws of the same magnitudes), where M4 says +1.02 W and M2 +0.86 W.
- **Exponent spread with a gate:** `x_e_g` 0.62 W low, and it alone keeps R9 from passing.
- **int8 where one side is still:** `i_a127_bfull` 0.73 W high on 2.43 W. int8's arithmetic is behavioural, so I3 is an empirical fit, and its constants are not comparable with the float ones.
- **Dense real fp16 runs high:** 0.1–0.4 W on E95's tiles.

**What it cannot do at all:** predict the zero level or idle (D is over the type's zeros); run on a new card without a scale from that card's own kinds; speak for another clock or voltage (fitted at 600 MHz and about 520 mV, tested at about 500 mV on card 1 with one scale, never at another clock); or say anything about a stream other than this TensorFMA kernel's. E101's real GEMM is a different stream.

**5. The constants hold.** Refitting M4 with everything else in, reported only: E78 alone 1.624, 7.533, 2.222, 1.066 fJ; all 108 float tiles on aifoundry3 1.617, 7.667, 2.195, 1.063 fJ; both cards and E103, 219 tiles, 1.605, 7.628, 2.306, 1.051 fJ. int8 moves more: 3.09, 16.7, 1.79 fJ to 3.28, 14.0, 1.91 fJ.

**6. The registered arms.** R2, R3 and R9 hold at every arm. R1 holds at dips kept, gates off, `auto`, 0.1994 and 0.3803 (0.31–0.41 W) and is INCONCLUSIVE at the two extreme slopes, 0.545 and 0 (0.69, 0.66 W), where the session tie also fails. **R4 is the thin one:** PASS at 0.365 W, INCONCLUSIVE at dips kept (0.422), `auto` (0.409), 0.3803 (0.419) and 0.545 (0.506). R7 falls to INCONCLUSIVE at dips kept and 0.3803, and FAIL at 0.545 and 0. R8 reads PERSISTS at `auto`, 0.3803 and 0.545.

**A crude look,** post hoc: median board power with no gate, no interpolation and no leakage correction ([`crude-check.txt`](crude-check.txt)), is 0.57 W rms from the reduction in floats and 0.14 W in int8, mostly a level, because the tiles run warmer than their zeros. Against M4 it reads 0.71 W, and against Q130(n) 3.93 W, so the gap to the null does not rest on the reduction.

## Departures

None from the registration. The session ran 27.7 min from claim to release, against "about 25". One thing I could have registered and did not: the disagreement that chose the tiles is dominated by one denormal tile, so R2 and R3 report their gap without it beside the verdict.

## What this cannot say

- **Selection favours neither model, but it makes the null look bad.** A tile chosen because two models disagree must hurt at least one of them. `fp32.z_dn_ab` alone takes Q130(n) from 2.79 to 3.96 W. Q130(n) was never built for denormals.
- **M4's form was chosen after reading E94 and the ladders,** with two more constants than M2. E95 and E103 are the tests of that choice, and R6 passes on them.
- **The tiles come from my pool,** written by someone who knows the model. A pool I did not think of could do worse. Everything the pool's families cover is in `make_e103_pool.py`.
- **Fit constants, not energies.** 1.62, 7.53 and 2.22 fJ absorb glitches, wire length and whatever the zero-delay bench does not see. "The bus costs 4.6× a core net" is a statement about these fitted terms.
- **n is small inside each family,** one or two tiles, and three passes on one card in one session.
- **fp16's window arithmetic is a model read off the RTL,** and no card has read C back (the bench's README §6).

## Section 11, and what a reader can be told

**Item 6 narrows to its named gaps:** a model now predicts every float kind tried, blind, to an rms of 0.10–0.39 W by format and set, and int8 to 0.17–0.37 W on its own terms. Near-cancelling sums, the A side with a busy partner, moving-sum alternation, and any other stream, clock or card remain.

**For the blog, each from a committed file:**

- Four constants, fitted on 33 kinds of number on one card, predicted 23 float tiles built to break them on another card to 0.31 W rms, with the tiles running from 3 to 24 W. [`scored.json`, E103-R1]
- The best simple predictor missed the same tiles by 3.96 W, or 2.79 W without its worst tile. [`scored.json`, E103-R2]
- The same constants predicted 19 real-tensor float tiles they had never seen to 0.16 W. [`../2026-11-01-q132-rtl-bench/scored-frozen.json`]
- Those constants are fitting constants: about 1.6 fJ a toggle in the multiplier and adder, 7.5 fJ on the lane's operand bus, 2.2 fJ elsewhere, and 1.07 fJ for each register bit clocked. [`tools/claims-v3/kinds/predictions-e103.json`]
- int8 needs its own constants because its arithmetic is behavioural in the public RTL, and with them it predicts real int8 tiles to 0.17 W and built ones to 0.37 W. [`score_all.json`]
- The model's largest miss was 0.89 W, on a near-cancelling sum, and all five tiles outside its intervals were fp32. [`scored.json`, E103-R7]

**Next, if the owner wants more:** a pool written by someone else; the same test at a second clock; a net-level count of what near-cancelling sums do in the normaliser.

## Files

| file | what |
|---|---|
| `scored.json`, `results.md`, `score.log` | the rules, every arm, the tile table |
| `score_all.py`, `score_all.json`, `score_all.txt` | every experiment with a frozen prediction, labelled by the clock, then everything else |
| `crude-check.py`, `crude-check.txt` | the raw telemetry's median, with none of the reduction |
| `e103.json`, `reduce.txt`, `runs.csv`, the `e103-*`, `reduce-*`, `runs-*` arms | the reductions |
| `aifoundry1-c1/kinds/p10310`–`p10312`, `kinds-smoke-p10301` | raw data of every pass and the smoke |
| `logs/`, `code.sha256` | the queue log, the dry run, the hashes |

The registration, the tiles and the code: `tools/claims-v3/kinds/E103.md`, `e103/`, `make_e103_pool.py`, `select_e103.py`, `predictions-e103.json`. The bench's counts: `../2026-11-01-q132-rtl-bench/counts-e103-pool.json`.
