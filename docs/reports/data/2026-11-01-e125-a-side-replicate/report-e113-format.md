# E113 — the A side's two layouts at fixed Hamming weight (scored)

Passes run [12501, 12502, 12503, 12504, 12505, 12506, 12507, 12508], kept [12502, 12503, 12504, 12505, 12506, 12507, 12508] (E67's two gates and E70's D-a). Runs 208, failed a per-run gate 0.

## Pass health

| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (Gop/s) | set aside |
|---|---|---|---|---|---|---|
| 12501 | 26 | 0 | 0.328 | 0.328 | 1.1209 | anchor_pi drift +0.328 W |
| 12502 | 26 | 0 | 0.184 | 0.184 | 1.1209 | — |
| 12503 | 26 | 0 | 0.086 | 0.271 | 1.1210 | — |
| 12504 | 26 | 0 | 0.113 | 0.293 | 1.1209 | — |
| 12505 | 26 | 0 | 0.211 | 0.234 | 1.1210 | — |
| 12506 | 26 | 0 | 0.135 | 0.267 | 1.1208 | — |
| 12507 | 26 | 0 | 0.243 | 0.243 | 1.1210 | — |
| 12508 | 26 | 0 | 0.232 | 0.280 | 1.1211 | — |

## The rungs (W over the zero, paired per pass; mean ± SE over the kept passes)

| item | k | layout | bits | dW (W) | ± SE | fJ / designed bit | S_A | law A | law WA (6.37) | law M (c 0.643) | E70 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `alq_h1` | 1 | low | [0] | 0.300 | 0.038 | 131 | 0.459 | 0.459 | 0.443 | 0.390 | 0.282 |
| `alq_h2` | 2 | low | [0,1] | 0.965 | 0.028 | 210 | 1.599 | 1.599 | 1.414 | 0.597 | 0.829 |
| `alq_h3` | 3 | low | [0,1,2] | 0.911 | 0.021 | 132 | 2.072 | 2.072 | 1.769 | 0.832 | — |
| `alq_h4` | 4 | low | [0,1,2,3] | 1.601 | 0.026 | 174 | 3.150 | 3.150 | 2.485 | 0.968 | 1.578 |
| `alq_h6` | 6 | low | [0,1,2,3,4,5] | 2.031 | 0.011 | 147 | 4.209 | 4.209 | 3.081 | 1.516 | — |
| `alq_h8` | 8 | low | [0,1,2,3,4,5,6,7] | 2.048 | 0.019 | 112 | 5.784 | 5.784 | 3.801 | 2.089 | 1.957 |
| `alq_h12` | 12 | low | [0,1,2,3,4,5,6,7,8,9,10,11] | 3.422 | 0.026 | 124 | 9.025 | 9.025 | 4.826 | 3.539 | 3.482 |
| `alq_h16` | 16 | low | [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] | 5.556 | 0.011 | 151 | 15.913 | 15.913 | 5.848 | 5.381 | 5.709 |
| `alq_h23` | 23 | low | [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22] | 7.307 | 0.029 | 138 | 32.852 | 32.852 | 6.336 | 7.813 | 7.560 |
| `als_h2` | 2 | spread | [0,12] | 1.149 | 0.048 | 250 | 1.429 | 1.429 | 1.280 | 1.342 | — |
| `als_h3` | 3 | spread | [0,8,15] | 2.675 | 0.015 | 388 | 3.279 | 3.279 | 2.563 | 2.225 | — |
| `als_h4` | 4 | spread | [0,6,12,17] | 2.738 | 0.029 | 298 | 3.923 | 3.923 | 2.930 | 2.848 | — |
| `als_h6` | 6 | spread | [0,4,8,12,15,19] | 4.027 | 0.032 | 292 | 7.264 | 7.264 | 4.334 | 3.786 | — |
| `als_h8` | 8 | spread | [0,3,6,9,12,14,17,20] | 4.788 | 0.025 | 261 | 9.743 | 9.743 | 4.991 | 4.573 | — |
| `als_h12` | 12 | spread | [0,2,4,6,8,10,12,13,15,17,19,21] | 5.898 | 0.034 | 214 | 15.715 | 15.715 | 5.832 | 5.719 | — |
| `als_h16` | 16 | spread | [0,1,3,4,6,7,9,10,12,13,14,16,17,19,20,22] | 6.190 | 0.021 | 169 | 22.477 | 22.477 | 6.185 | 6.271 | — |
| `lq_h0` | — | — | — | 0.000 | 0.000 | — | — | — | — | — | — |
| `lq_h2` | — | — | — | 1.011 | 0.037 | — | — | — | — | — | — |
| `lq_h4` | — | — | — | 1.725 | 0.037 | — | — | — | — | — | — |
| `lq_h8` | — | — | — | 3.206 | 0.028 | — | — | — | — | — | — |
| `ls_h8` | — | — | — | 6.904 | 0.040 | — | — | — | — | — | — |
| `nrd_a` | — | — | — | 6.952 | 0.038 | — | — | — | — | — | — |
| `nrd_b` | — | — | — | 10.485 | 0.041 | — | — | — | — | — | — |

## D1_A: spread minus low at the same k (paired per pass)

| k | measured (W) | ± SE | 95% | σ from 0 | H | WA | M | A | B side, E70 |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 0.184 | 0.039 | [0.088, 0.281] | 4.7 | 0 | -0.134 | 0.745 | -0.170 | 1.158 |
| 3 | 1.765 | 0.022 | [1.712, 1.818] | 81.5 | 0 | 0.794 | 1.393 | 1.207 | 2.165 |
| 4 | 1.137 | 0.024 | [1.078, 1.196] | 47.4 | 0 | 0.444 | 1.880 | 0.773 | 2.922 |
| 6 | 1.996 | 0.033 | [1.915, 2.078] | 60.0 | 0 | 1.254 | 2.270 | 3.055 | 3.528 |
| 8 | 2.740 | 0.029 | [2.669, 2.811] | 94.1 | 0 | 1.190 | 2.483 | 3.959 | 3.860 |
| 12 | 2.476 | 0.034 | [2.393, 2.560] | 72.8 | 0 | 1.005 | 2.180 | 6.691 | 3.388 |
| 16 | 0.633 | 0.022 | [0.579, 0.687] | 28.7 | 0 | 0.337 | 0.891 | 6.564 | 1.385 |

## D2_A: what collapses the two A layouts (15 rungs; `alq_h23` out of sample)

| law | free parameters | rms (W) |
|---|---|---|
| a free value per k (the best any 'how many' law can do) | one per k | 0.865 (matched k only 0.896) |
| one saturating curve in A's own sum S_A, W refitted (5.66 W) | 1 | 0.682 |
| the same curve, W frozen at E70's 6.37 W | 0 | 0.739 |
| the mirror: c × the same mask's B rung (E70), c refitted (0.6617) | 1 | 0.273 |
| the mirror, c frozen at 0.643 | 0 | 0.289 |
| additive (S_A) | 0 | 6.111 |

Out of sample for the frozen laws, the 7 spread rungs alone: mirror (c 0.643) 0.238 W, WA (6.37 W) 0.172 W, additive 7.545 W.

Per-pass refits: W 5.665 ± 0.023 W; c 0.6617 ± 0.0020.

Out of sample, `alq_h23` (7.307 ± 0.029 W): the refitted S_A curve misses it by 1.659 W (58.2 SE) and it sits 1.642 W (57.6 SE) above the refitted W; the refitted mirror misses it by -0.729 W (-25.6 SE), the frozen mirror by -0.506 W.

## rho(8): per designed bit, A over B, at the same mask (E113's own B ties)

- low: 1.278 ± 0.019 (ratio of means 1.277)
- spread: 1.387 ± 0.010 (ratio of means 1.387)
- spread − low: 0.109 ± 0.024

## Replicate of E70 and the B tie

| item | E113 | ± SE | E70 | difference | band |
|---|---|---|---|---|---|
| `alq_h1` | 0.300 | 0.038 | 0.282 | +0.017 | 0.6 |
| `alq_h2` | 0.965 | 0.028 | 0.829 | +0.136 | 0.6 |
| `alq_h4` | 1.601 | 0.026 | 1.578 | +0.023 | 0.6 |
| `alq_h8` | 2.048 | 0.019 | 1.957 | +0.090 | 0.6 |
| `alq_h12` | 3.422 | 0.026 | 3.482 | -0.061 | 0.6 |
| `alq_h16` | 5.556 | 0.011 | 5.709 | -0.152 | 0.6 |
| `alq_h23` | 7.307 | 0.029 | 7.560 | -0.253 | 1.0 |
| `ls_h8` − `lq_h8` | 3.698 | 0.055 | 3.860 | -0.162 | 0.6 |

Random words: `nrd_a` 6.952 W, `nrd_b` 10.485 W, ratio 0.663 ± 0.002 (mirror c 0.643); the refitted S_A curve predicts `nrd_a` 5.397 W (measured/predicted 1.288).

## The registered rules

| rule | asked | measured | verdict |
|---|---|---|---|
| P1 | dW(als_h8) - dW(alq_h8) > 1.0 W at >= 3 SE (H needs 0; WA 1.19, M 2.48, A 3.96 W) | measured 2.740; se 0.029 | **PASS** |
| P2 | one saturating curve in A's own additive sum S_A, W refitted on the 15 A rungs: ACCEPTED if rms <= 0.40 W, REJECTED if > 0.60 W (E70: 1.063 W on the low layout alone) | measured 0.682; WA_refit_W 5.665 | **REJECTED** |
| P3 | the mirror law with c frozen at 0.643 (fitted on E70's low layout; no free parameter): rms over the 7 spread rungs <= 0.50 W PASS, > 0.80 W FAIL (WA frozen and law A beside it, reported) | measured 0.238; R_SA_frozen_spread_W 0.172; R_A_additive_spread_W 7.545; R_M_frozen_all15_W 0.289; c_refit 0.662 | **PASS** |
| P4 | the verdict on the A side's form, read off D1_A(8) and D2_A together (README) | R_k_W 0.865; R_SA_refit_W 0.682; R_M_refit_W 0.273; one_parameter_laws the mirror law (the same mask's B rung, scaled) collapses the A side better than a curve in S_A | **which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k** |
| P5 | rho(8) per designed bit, A over B, in both layouts inside [0.7, 2.5] and |spread - low| <= 0.30 (M: 1.29 both; WA spread 1.40; A spread 2.74; H spread 0.55) | rho_low 1.278; rho_spread 1.387; spread_minus_low 0.109; se 0.024 | **PASS** |
| P6 | E70's seven alq rungs within 0.6 W (alq_h23 within 1.0 W) and ls_h8 - lq_h8 within 0.6 W of 3.860 W | alq_outside []; D1_B_h8 3.698; D1_B_h8_diff -0.162 | **PASS** |
| P7 | the random-word check: dW(nrd_a) / dW(nrd_b) in the same passes inside [0.55, 0.75] (M: c = 0.643; E70's own pair read 0.668, seen before this registration) | measured 0.663; se 0.002 | **PASS** |

## Arms (reported, never verdicts)

| arm | passes kept | D1_A(8) | R_k | R_SA refit (W) | R_M frozen | R_M refit | c refit | rho8 low / spread | verdicts P1-P7 |
|---|---|---|---|---|---|---|---|---|---|
| all passes (E67's gates, no D-a) | [12501, 12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.710 ± 0.039 | 0.862 | 0.683 | 0.286 | 0.270 | 0.6612 | 1.267 / 1.369 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| E113's own reduction (dips kept, leak auto) | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.686 ± 0.066 | 0.858 | 0.695 | 0.288 | 0.276 | 0.6589 | 1.301 / 1.368 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| dips kept, leak 0.2414 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.669 ± 0.065 | 0.854 | 0.693 | 0.285 | 0.276 | 0.6568 | 1.305 / 1.367 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| dips removed, leak auto | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.757 ± 0.030 | 0.870 | 0.684 | 0.293 | 0.272 | 0.6638 | 1.274 / 1.388 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| dips removed, leak 0.2 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.771 ± 0.031 | 0.873 | 0.686 | 0.296 | 0.272 | 0.6655 | 1.270 / 1.389 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| dips removed, leak 0.3 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.696 ± 0.027 | 0.854 | 0.678 | 0.282 | 0.274 | 0.6562 | 1.290 / 1.385 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| dips removed, leak 0.4 | [12502, 12503, 12504, 12505, 12506, 12507, 12508] | 2.622 ± 0.024 | 0.835 | 0.671 | 0.277 | 0.276 | 0.6470 | 1.311 / 1.380 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
