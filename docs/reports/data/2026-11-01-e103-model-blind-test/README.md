# E103: a blind test of the bench's power model, on tiles picked per family where it and two simple predictors disagree most (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, item 6 of the kinds page's section 11. Pre-registered in `b5f1e5d7`, pushed 01:37:31 PST, before the claim and the first launch: [`tools/claims-v3/kinds/E103.md`](../../../../tools/claims-v3/kinds/E103.md), frozen numbers in `predictions-e103.json` (sha256 `7ac59cae…`), the scorer `score_e103.py` and its self-test in the same commit. aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz in every sample, 498.7 mV mean, TDP 65 W / threshold 65 °C read under the card lock at both ends of every block, never set. Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566397290267025444 in #community-lab, posted 02:23:36 PST, released by editing it at 02:51 PST: 27.7 min. Smoke 10301 at 02:23:47; queue 02:24:38–02:50:23 PST, 1,545 s. **No amendments.** Corrected after verification the same day: [Corrections](#corrections-after-verification).*

**In plain words.** For floats the bench's model has four constants, fitted on E78's 33 kinds on another card, and one scale for this card from an earlier run of those kinds here (E82). Its form was chosen after reading three experiments on this card. From a pool of 215 tiles, written by someone who knows the model, a quota per family took the tiles where it most disagrees with two simple predictors. **It read 0.31 W rms over 23 float tiles running from 3 to 24 W, against 0.58 W for the first model and, among models with no simulator, 1.7–4 W (0.74–2.8 W without one denormal tile).** So its margin over the best comparators is about 2×. int8, on its own constants, reads 0.37 W. All five tiles outside their intervals are fp32, and the largest miss is +0.89 W, on a tile built to nearly cancel, which it does only at the start of a launch; the cause is unknown.

## Results

**1. Registered against what happened** ([`scored.json`](scored.json), [`results.md`](results.md)). All three passes kept, 148 of 150 planned runs, all 148 kept. The harness's launch-reading rule skipped `fp32.c_near_rand` in pass 10310 (#8) and `fp32.x_e_g` in pass 10312 (#35), so those two tiles rest on two passes.

| rule | what | threshold | result | verdict | what I expected, frozen |
|---|---|---|---:|---|---|
| **E103-R1** | **rms(D − M4), 23 float tiles** | PASS ≤ 0.60 W, FAIL > 1.00 W | **0.314 W** [0.197, 0.425], bias −0.05 W | **PASS** | PASS near 0.5 W |
| **E103-R2** | beats the named null, Q130(n). **Follows from R1 (C1)** | gap's 95% above 0 | **3.646 W** [2.142, 5.435]: 0.314 against 3.960 W (0.320 against 2.788 W without `fp32.z_dn_ab`) | **PASS** | PASS |
| **E103-R3** | beats E92's flop-price refit. **Follows from R1 (C1)** | the same | **1.462 W** [0.324, 2.567]: 0.314 against 1.775 W (0.320 against 0.913 W without `fp32.z_dn_ab`) | **PASS** | PASS, narrowly, without the denormal tile |
| **E103-R4** | **rms(D − I3), 7 int8 tiles** | PASS ≤ 0.40 W, FAIL > 0.80 W | **0.365 W** [0.200, 0.524], bias +0.15 W | **PASS**, arm-sensitive | INCONCLUSIVE |
| **E103-R5** | I3 beats Q130(n) | gap's 95% above 0 | 0.542 W [0.070, 0.990]: 0.365 against 0.907 W | **PASS**, arm-sensitive | |
| **E103-R6** | the bus price earns its term: M4 beats M2 | gap's 95% above 0 | **0.265 W** [0.162, 0.364]: 0.314 against 0.579 W | **PASS**, arm-sensitive | PASS |
| **E103-R7** | D inside the frozen 95% interval | PASS ≥ 80%, FAIL < 50% | **25 of 30, 83%**: fp32 8 of 13, fp16 10 of 10, int8 7 of 7 | **PASS**, arm-sensitive | INCONCLUSIVE or PASS |
| **E103-R8** | the A side: mean (D − T)/(M4 − T), T the clock term | PERSISTS if upper bound < 0.95; GONE if inside [0.95, 1.05] | 0.947 ± 0.037 | **UNRESOLVED** | PERSISTS |
| **E103-R9** | gated float tiles: mean D − M4 | PASS inside ±0.30 W; FAIL if it excludes ±0.30 W | +0.151 ± 0.382 W, n = 5 (M2: +0.598 W) | **INCONCLUSIVE** | PASS |
| **E103-S1** | the session tie against E82, dips removed | ±0.50 W, int8 ±0.25 W | `fp32.randn` 24.07 (24.00), `fp16.randn` 21.61 (21.49), `anchor_pi` 8.04 (8.14), `int8.full` 6.96 (6.84) | **PASS** | |

*Dated 1 Nov 2026: [E102](../2026-11-01-e102-balanced-bit-prices/README.md) reads R3's null from the sums the RTL's arithmetic gives, at 1.694 W, not 1.775 W: gap +1.380 W [+0.242, +2.522], and without the denormal tile +0.385 W [+0.202, +0.571], not +0.593 ([`fault_e103_null_e102.txt`](../../../../tools/claims-v3/kinds/fault_e103_null_e102.txt)). R3's registered PASS stands, and every frozen file here stays.*

Two things I expected came out better than I said: R1's 0.31 W and R4's PASS. Two came out weaker: R8 and R9 are unresolved, because five tiles do not bound them. **R9's interval is driven by one tile, `fp32.x_e_g`, +0.62 W;** the other four read −0.23 to +0.25 W.

**2. By format, every model, the same tiles** (`scored.json` `primary.reported`; rms in W, bias is predicted minus measured):

| | n | **M4 or I3** | M2 | Q130(n), the null | E92's flop price | the gate law |
|---|---:|---:|---:|---:|---:|---:|
| fp32 | 13 | **0.392** (−0.14) | 0.702 (−0.14) | 4.674 (+1.01) | 2.190 (+0.89) | 8.550 (+5.90) |
| fp16 | 10 | **0.162** (+0.06) | 0.360 (−0.08) | 2.768 (+0.71) | 1.006 (−0.14) | 5.642 (+3.79) |
| int8 | 7 | **0.365** (+0.15) | 0.381 (+0.01) | 0.907 (+0.03) | | 1.942 (+0.95) |

**Q130(n) was the registered null, not the best comparator.** The verifier fitted harder ones the way M4 was fitted, constants on E78 alone and the scale from E82. **These are post hoc,** their forms fixed after E103's data, and everything it tried is listed. I recomputed them ([`corrections-check.txt`](corrections-check.txt) [G]) and they agree within 0.005 W.

| rms, W | E103 floats, n 23 | without `z_dn_ab`, n 22 | E95 floats, n 19, nobody chose these |
|---|---:|---:|---:|
| **M4, frozen** | **0.314** | **0.320** | **0.158** |
| M2, frozen | 0.579 | 0.590 | 0.415 |
| clocked bits + register bits that change, 2 constants, bench | 0.734 | 0.714 | 0.630 |
| E92's flop-price form refit on E78 alone, per format, no simulator | 1.716 | **0.740** | **0.266** |
| E92's flop price, frozen | 1.775 | 0.913 | |
| u + (A+B), gate share and bus bits, 2 constants, pooled | 2.941 | 1.692 | 1.692 |
| u + (A+B), per format | 3.098 | 1.475 | 1.300 |
| clocked bits + bus nets, 2 constants, bench | 2.816 | 2.580 | 3.049 |
| Q130(n), frozen | 3.960 | 2.788 | 0.610 |
| u alone | 4.644 | 4.424 | 3.951 |

Its gaps over M4, 95% over tiles, without `z_dn_ab`: flop refit 0.42 [0.16, 0.68] W; registers 0.39 [0.19, 0.59] W; M2 0.27 [0.17, 0.37] W; two constants 1.37 [0.81, 1.86] W. All above 0, so M4 beats every comparator, **by about 2× over the best of them**. A trivial predictor does not do nearly as well: gate share plus bus bits misses by 2.9 W here and 1.3–1.7 W on real tensors. int8, E103 n 7 and E95 n 11: I3 0.365 and 0.166 W; M2 0.381 and 0.285 W; clocks + bus + register bits 0.672 and 0.305 W; u + (A+B) 0.853 and 1.085 W; Q130(n) 0.907 and 0.824 W.

**3. Every tile.** D is 95% over three passes, or two where marked †, with t(1) = 12.7; ⚠ marks D outside the frozen interval.

| tile | why it is here | D, W | **M4 or I3 [95%]** | D − M | M2 | Q130(n) | flop |
|---|---|---:|---:|---:|---:|---:|---:|
| `fp32.c_near_rand` ⚠ † | built to nearly cancel | 19.15 ± 0.62 | **18.26** [17.56, 18.96] | **+0.89** | 17.80 | 16.23 | 20.55 |
| `fp32.x_e_g` ⚠ † | exponent spread and a 47% gate | 14.79 ± 0.40 | **14.17** [13.81, 14.53] | **+0.62** | 13.86 | 11.77 | 14.16 |
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
| **E95, 30 real-tensor tiles nobody chose**, M4 and I3 (`b995463e`; data `ab23b1aa`) | aifoundry3, no scale | **0.102** (+0.08), n 11 | **0.212** (+0.17), n 8 | **0.166** (0.00), n 11 |
| the same tiles: M2 (`2b7ece4a`) | | 0.424 | 0.403 | 0.285 |
| the same tiles: Q130(n) | | 0.506 | 0.730 | 0.824 |
| **E103, 30 tiles picked per family**, M4 and I3 (`b5f1e5d7`) | card 1, E82's scale | **0.392** (−0.14), n 13 | **0.162** (+0.06), n 10 | **0.365** (+0.15), n 7 |
| the same tiles: M2 | | 0.702 | 0.360 | 0.381 |
| the same tiles: Q130(n), whose size the selection sets (C1) | | 4.674 | 2.768 | 0.907 |
| E92's 32 tiles, an earlier two-term form (`de545f0c`) | aifoundry3 | 0.668 (−0.42), n 23 | 0.389 (−0.21), n 9 | |

**The fair ratio is E95's: 0.158 against 0.610 W in floats, 3.9×.** Quote the sets apart. Their biases differ in sign, so a pooled figure depends on the mix.

**Constants first:** M4's constants were committed before E102's data, and E102's lane counted its tiles before its data, but I did the arithmetic afterwards. E102's single-bit prices, balanced and all-in, on card 1, each over its own zero: fp32 B 0.237 and 0.224 W, fp32 A 0.126 and 0.216 W, fp16 0.096 and 0.232 W, int8 B 0.101 W. M2, frozen in E102's own registration: 0.254, 0.238, 0.197, 0.210, 0.147, 0.247, 0.179 W.

**Post hoc,** M4's form chosen after these were read, the constants not fitted on them: E86 0.145, E90 0.220, E92 0.242, E88 0.229, E94 0.176 W in floats; int8 E86 0.256, E88 0.365, E94 0.295 W. Single-bit ladders: E65 0.185 W, E67's A bits 0.241 W, E70 low 0.289 W.

**Where it fails, plainly:**

- **`fp32.c_near_rand`, +0.89 W on two passes.** It was built to nearly cancel, and it does only at the start of a launch: MACs losing 8 or more bits fall from 50% at op 0 to 4.7% at op 5,000 and to 0 at the bench's three launch points, in a launch of about 534,000 ops ([`replay-c-near-rand.txt`](replay-c-near-rand.txt)). **So the cause is unknown,** and "near-cancelling" is not a named gap. It is mostly a sign-alternating tile, so it may be the same class as `s_bhalf_alt` (a guess).
- **The A side and high-toggle ladders with a busy partner run high, and the fitted terms do not fix it.** E103's fp32 A tiles read 0.92–0.93 of the predicted switching, fp16's 0.98 (R8). On the older ladders, post hoc: E60's low bits with A = π 0.95 W, measured/predicted 0.90; E67's two-flip grid 0.69 W, 0.90; E70's A ladder 0.65 W, 0.86.
- **Adder alternation on moving sums runs low:** `s_bhalf_alt` 0.45 W low. It reads +1.56 ± 0.11 W over `s_abs` (different draws of the same magnitudes), where M4 says +1.02 W and M2 +0.86 W.
- **Exponent spread with a gate:** `x_e_g` 0.62 W low on two passes, and it alone keeps R9 from passing.
- **The intervals:** they held on 8 of 13 fp32 tiles, so a 95% interval may not be quoted for fp32 on a new design.
- **int8 where one side is still:** `i_a127_bfull` 0.73 W high on 2.43 W. int8's arithmetic is behavioural, so I3 is an empirical fit, and its constants are not comparable with the float ones.
- **Dense real fp16 runs high:** 0.1–0.4 W on E95's tiles.

**What it cannot do at all:** predict the zero level or idle (D is over the type's zeros); run on a new card without a scale from that card's own kinds; speak for another clock or voltage (fitted at 600 MHz and about 520 mV, tested at about 500 mV on card 1 with one scale, never at another clock); or say anything about a stream other than this TensorFMA kernel's. E101's real GEMM is a different stream. None of its constants has a physical reading.

**5. The constants hold.** Refitting M4 with everything else in, reported only: E78 alone 1.624, 7.533, 2.222, 1.066 fJ; all 108 float tiles on aifoundry3 1.617, 7.667, 2.195, 1.063 fJ; both cards and E103, 219 tiles, 1.605, 7.628, 2.306, 1.051 fJ. int8 moves more: 3.09, 16.7, 1.79 fJ to 3.28, 14.0, 1.91 fJ.

**6. The registered arms.** R2, R3 and R9 hold at every arm. R1 holds at dips kept, gates off, `auto`, 0.1994 and 0.3803 (0.31–0.41 W) and is INCONCLUSIVE at the two extreme slopes, 0.545 and 0 (0.69, 0.66 W), where the session tie also fails. **R4 is the thin one:** PASS at 0.365 W, INCONCLUSIVE at dips kept (0.422), `auto` (0.409), 0.3803 (0.419) and 0.545 (0.506). R6 falls to INCONCLUSIVE at 0.545. R7 falls to INCONCLUSIVE at dips kept and 0.3803, and FAIL at 0.545 and 0. R8 reads PERSISTS at `auto`, 0.3803 and 0.545.

**A crude look,** post hoc: median board power with no gate, no interpolation and no leakage correction ([`crude-check.txt`](crude-check.txt)), is 0.57 W rms from the reduction in floats and 0.14 W in int8, mostly a level, because the tiles run warmer than their zeros. Against M4 it reads 0.71 W, and against Q130(n) 3.93 W, so the gap to the null does not rest on the reduction.

## Departures

One from the plan, by the harness's own rule: 148 of 150 runs, the two skips named in Result 1. The registered minimum is two passes a tile, and no verdict moves. The session ran 27.7 min from claim to release, against "about 25".

**What the frozen registration says that is not so,** left as registered because it is frozen, and corrected here (C1–C3): "Exceptions, all stated" (36 pool tiles were never eligible); "that refit saw E92's designs, and M4 did not: a hard comparator" (M4's form was chosen after E92, and refitted on E78 alone the flop form does better without the denormal tile); the statement line "the bench's model predicted 23 float tiles built to break it … against Y W for the best simple predictor"; and "E103's own frame" for the scale.

## What this cannot say

- **The selection inflates the worse model's error and cannot inflate the better one's.** A tile chosen because two models disagree must hurt at least one of them. That forces most of the gap to Q130(n) (C1). `fp32.z_dn_ab` alone takes it from 2.79 to 3.96 W, and Q130(n) was never built for denormals.
- **M4's form was chosen after reading E94 and the ladders,** from 14 float forms and 5 int8 forms ([`model-form-search/`](../2026-11-01-q132-rtl-bench/model-form-search/)), with two more constants than M2. E95 and E103 are the tests of that choice, and R6 passes on them.
- **The tiles come from my pool,** written by someone who knows the model, and in M4's own count space they are mostly interpolation: 21 of 23 lie inside E78's largest leverage. The hostile part is the families I chose. A pool I did not think of could do worse.
- **Fit constants, not energies.** 1.62, 7.53 and 2.22 fJ absorb glitches, wire length and whatever the zero-delay bench does not see. No post should quote fJ per wire or the bus's ratio to a core net.
- **n is small inside each family,** one or two tiles, and three passes on one card in one session.
- **fp16's window arithmetic is a model read off the RTL,** and no card has read C back (the bench's README §6). *(Dated 1 Nov 2026: [E104](../2026-11-01-e104-c-readback/README.md) has since read C back on 44 designed tiles, equal to the RTL's arithmetic word for word; E103's own tiles were not among them.)*

## Section 11, and what a reader can be told

**Item 6 narrows; it does not close.** With counts simulated from the public RTL's `vpu_top`, four fitted constants for floats (three for int8), and one scale per card, the model predicts this TensorFMA kernel's power over the type's zeros at 600 MHz. Blind on two sets: real tensors on the card it was fitted on, rms fp32 0.10, fp16 0.21, int8 0.17 W; tiles picked per family where it most disagrees with two simple predictors, on a second card, fp32 0.39, fp16 0.16, int8 0.37 W, with the largest misses +0.89 W (fp32) and −0.73 W (int8). Its 95% intervals held for fp16 and int8, and on only 8 of 13 fp32 tiles. It beats the best comparators by about 2×: M2 0.58 and 0.42 W, a no-simulator stream model 0.74 W (without one denormal tile) and 0.27 W. Still open: fp32 where signs alternate on moving sums or exponents spread under a gate; the A side with a busy partner (R8 unresolved at 0.947 ± 0.037; ladders 0.86–0.90 post hoc); gated kinds (R9 inconclusive, one tile); the zero level and idle; any other clock, voltage or stream, E101's GEMM included; a new card without a scale; a pool written by someone else; and any physical reading of the constants.

**For the blog, each from a committed file:**

- Counts simulated from the public RTL, four fitted constants and one scale per card predict this kernel's power over zeros at 600 MHz. On real tensors nobody chose, on the card it was fitted on, they read 0.16 W rms where the best simpler models read 0.27–0.61 W. [`../2026-11-01-q132-rtl-bench/scored-frozen.json`; [`corrections-check.txt`](corrections-check.txt) G]
- On 23 float tiles picked per family where it most disagrees with two simple predictors, from a pool written by someone who knows the model, on a second card, it read 0.31 W, where models with no simulator read 1.7–4 W (0.74–2.8 W without one denormal tile). [`scored.json`; `corrections-check.txt` G]
- The simulator matters, and so does pricing the operand bus apart: the same counts with one net price read 0.58 W there and 0.42 W on the real tensors. [`corrections-check.txt` G]
- Its largest misses were +0.89 W in fp32 and −0.73 W in int8, and its 95% intervals held on only 8 of 13 fp32 tiles. [`scored.json`; `corrections-check.txt` E]
- int8 has its own constants because its arithmetic is behavioural in the public RTL. With them it read 0.17 W on real tiles and 0.37 W on the picked ones. [`score_all.json`]

**A post may not say:** "a power model for every kind" or "for the chip"; "the best simple predictor", or 0.31 against 3.96 W as a 12× win; "built to break it" without how the tiles were picked; "four constants" without the card scale, or "on another card" as if nothing had been read there; fJ per wire, "the bus costs 4.6×", or the stage split as physics; "near-cancelling" or "normaliser" as the cause of the miss; 95% intervals for fp32; any other clock, voltage, stream or GEMM, or an unscaled new card.

**Next, if the owner wants more:** a pool written by someone else; the same test at a second clock; a short card run reading C back (dated 1 Nov 2026: [E104](../2026-11-01-e104-c-readback/README.md) ran one).

## Corrections after verification

*Sun 1 Nov 2026, against `8c354a91`, from an independent verifier's read. **No frozen file, data file or registered verdict changed;** `E103.md` stands as registered. Wrong sentences are replaced above. Every number here is recomputed by my own code in [`corrections-check.txt`](corrections-check.txt) (`corrections-check.py`, `comparator_features.py`, `replay_c_near_rand.py`) unless it is marked the verifier's. Every E103 number and verdict reproduced from raw telemetry in its hands, and all its faults held against my data.*

- **C1, major: "the best simple predictor missed by 3.96 W" is gone.** Q130(n) is not the best: on these tiles the flop price reads 1.775 and 0.913 W, and a two-constant gate-plus-bus fit 2.94 and 1.69 W. The selection sets the size: frozen, before any data, rms(M4 − Q130(n)) is 3.814 W, so at R1's PASS line Q130(n) must read at least 3.21 W and the gap at least 2.61 W; for the flop price, 1.20 and 0.60 W. **R2 and R3 follow from R1 and are not a second result.** R6 does not follow (frozen rms(M4 − M2) is 0.38 W). As a discriminating test the null was fair, registered and never fitted to this data; as a measure of what a simple predictor can do it is not. The fair ratio is E95's, 3.9×. Result 2 now carries the comparators (`corrections-check.txt` A, G).
- **C2, major: "built to break it" is qualified.** `select_e103.py` is a quota per family: 7 of the 23 float tiles are in the top 23 by disagreement, with ranks from 1 to 155 of 189. 36 pool tiles were never eligible, against "Exceptions, all stated": all the `h_b_` and `h_ab_` tiles, fp16's `z_` tiles, `o_anti` and `o_sort` in fp32, fp32's `s_arow_alt`, `s_bhalf_alt2` and `s_bhalf_alt4`, and `int8.i_neg_pos`; the largest are `fp16.z_dn_ab` 9.74 W and `fp32.h_ab_lo` 8.60 W of disagreement. The omission is not self-serving, because the B side is M4's strength. The score measures distance from the nulls, not M4's risk: median |M4 − M2| is 0.29 W chosen against 0.25 W for the pool. In M4's count space 21 of 23 lie inside E78's largest leverage, median 0.118 against E78's 0.130. The two outside, the `g_relu_shift15` tiles, came out at +0.11 and +0.01 W (B).
- **C3: "four constants" needs its fifth number.** The scale was fitted on that card's 33 E82 kinds. Without it, rms 0.474 W; fitted on E103 itself 0.9773 and 0.303 W, so the frozen 0.9722 is good. The form was chosen after reading three experiments on that card (E82, E88, E94). The scale came from E82 at `auto` 0.2541 W/°C, E103's primary uses 0.2414, so "E103's own frame" is loose by about 0.02 W, the verifier's estimate (C).
- **C4: "normaliser" had no support.** See "Where it fails" (F).
- **C5: 148 of 150, not 148 of 148, and "Departures: None" was wrong.** The two skipped tiles are the largest and third-largest misses, each on two passes, with ±0.62 and ±0.40 W from t(1) = 12.7 (D).
- **C6: "every float kind tried" was too broad.** M4 has two blind sets. Single tiles miss by up to 0.89 W, and post hoc ladders by 0.65–0.95 W. Section 11 above uses the verifier's text.
- **C7: E103-R7's 25 of 30 hid its split:** fp32 8 of 13, fp16 10 of 10, int8 7 of 7 (E).
- **C8: E103-R6 is INCONCLUSIVE at leak 0.545,** unflagged before. M4's form search is committed and counted: 14 float forms, 5 int8 forms (H).
- **C9: the pooled row is gone.** 0.297 W for fp32 blends 0.102 and 0.392 W with opposite biases.

**What the verifier checked and found right:** registration by the push log, the rules line by line, all 30 D from raw telemetry with its own code, M4's refit, blindness on E95, the harness's hashes and tile dumps, public text, and the claim.

## Files

| file | what |
|---|---|
| `scored.json`, `results.md`, `score.log` | the rules, every arm, the tile table |
| `score_all.py`, `score_all.json`, `score_all.txt` | every experiment with a frozen prediction, labelled by the clock, then everything else |
| `crude-check.py`, `crude-check.txt` | the raw telemetry's median, with none of the reduction |
| `corrections-check.py`, `corrections-check.txt`, `comparator_features.py`, `comparator-features.json`, `replay_c_near_rand.py`, `replay-c-near-rand.txt` | the corrections' numbers, the comparators and the replay |
| `e103.json`, `reduce.txt`, `runs.csv`, the `e103-*`, `reduce-*`, `runs-*` arms | the reductions |
| `aifoundry1-c1/kinds/p10310`–`p10312`, `kinds-smoke-p10301` | raw data of every pass and the smoke |
| `logs/`, `code.sha256` | the queue log, the dry run, the hashes |

The registration, the tiles and the code: `tools/claims-v3/kinds/E103.md`, `e103/`, `make_e103_pool.py`, `select_e103.py`, `predictions-e103.json`. The bench's counts: `../2026-11-01-q132-rtl-bench/counts-e103-pool.json`.
