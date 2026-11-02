# E113 — the A side's two layouts at fixed Hamming weight (scored)

Passes run [1131, 1132, 1133, 1134, 1135, 1136, 1137], kept [1131, 1132, 1133, 1134, 1135, 1136] (E67's two gates and E70's D-a). Runs 168, failed a per-run gate 0.

## Pass health

| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (Gop/s) | set aside |
|---|---|---|---|---|---|---|
| 1131 | 24 | 0 | 0.228 | 0.261 | 1.1208 | — |
| 1132 | 24 | 0 | 0.247 | 0.247 | 1.1210 | — |
| 1133 | 24 | 0 | 0.192 | 0.229 | 1.1208 | — |
| 1134 | 24 | 0 | 0.182 | 0.305 | 1.1210 | — |
| 1135 | 24 | 0 | 0.125 | 0.196 | 1.1208 | — |
| 1136 | 24 | 0 | 0.184 | 0.197 | 1.1208 | — |
| 1137 | 24 | 0 | 0.109 | 0.858 | 1.1209 | constant-operand spread 0.858 W |

## The rungs (W over the zero, paired per pass; mean ± SE over the kept passes)

| item | k | layout | bits | dW (W) | ± SE | fJ / designed bit | S_A | law A | law WA (6.37) | law M (c 0.643) | E70 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `alq_h1` | 1 | low | [0] | 0.314 | 0.058 | 137 | 0.459 | 0.459 | 0.443 | 0.390 | 0.282 |
| `alq_h2` | 2 | low | [0,1] | 0.951 | 0.025 | 207 | 1.599 | 1.599 | 1.414 | 0.597 | 0.829 |
| `alq_h3` | 3 | low | [0,1,2] | 0.950 | 0.026 | 138 | 2.072 | 2.072 | 1.769 | 0.832 | — |
| `alq_h4` | 4 | low | [0,1,2,3] | 1.594 | 0.026 | 174 | 3.150 | 3.150 | 2.485 | 0.968 | 1.578 |
| `alq_h6` | 6 | low | [0,1,2,3,4,5] | 2.045 | 0.023 | 148 | 4.209 | 4.209 | 3.081 | 1.516 | — |
| `alq_h8` | 8 | low | [0,1,2,3,4,5,6,7] | 2.026 | 0.028 | 110 | 5.784 | 5.784 | 3.801 | 2.089 | 1.957 |
| `alq_h12` | 12 | low | [0,1,2,3,4,5,6,7,8,9,10,11] | 3.504 | 0.043 | 127 | 9.025 | 9.025 | 4.826 | 3.539 | 3.482 |
| `alq_h16` | 16 | low | [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] | 5.743 | 0.071 | 156 | 15.913 | 15.913 | 5.848 | 5.381 | 5.709 |
| `alq_h23` | 23 | low | [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22] | 7.598 | 0.032 | 144 | 32.852 | 32.852 | 6.336 | 7.813 | 7.560 |
| `als_h2` | 2 | spread | [0,12] | 1.177 | 0.028 | 256 | 1.429 | 1.429 | 1.280 | 1.342 | — |
| `als_h3` | 3 | spread | [0,8,15] | 2.641 | 0.095 | 384 | 3.279 | 3.279 | 2.563 | 2.225 | — |
| `als_h4` | 4 | spread | [0,6,12,17] | 2.827 | 0.029 | 308 | 3.923 | 3.923 | 2.930 | 2.848 | — |
| `als_h6` | 6 | spread | [0,4,8,12,15,19] | 3.941 | 0.169 | 286 | 7.264 | 7.264 | 4.334 | 3.786 | — |
| `als_h8` | 8 | spread | [0,3,6,9,12,14,17,20] | 4.844 | 0.056 | 264 | 9.743 | 9.743 | 4.991 | 4.573 | — |
| `als_h12` | 12 | spread | [0,2,4,6,8,10,12,13,15,17,19,21] | 6.061 | 0.062 | 220 | 15.715 | 15.715 | 5.832 | 5.719 | — |
| `als_h16` | 16 | spread | [0,1,3,4,6,7,9,10,12,13,14,16,17,19,20,22] | 6.504 | 0.049 | 177 | 22.477 | 22.477 | 6.185 | 6.271 | — |
| `lq_h0` | — | — | — | 0.000 | 0.000 | — | — | — | — | — | — |
| `lq_h8` | — | — | — | 3.037 | 0.189 | — | — | — | — | — | — |
| `ls_h8` | — | — | — | 7.177 | 0.048 | — | — | — | — | — | — |
| `nrd_a` | — | — | — | 7.195 | 0.052 | — | — | — | — | — | — |
| `nrd_b` | — | — | — | 10.842 | 0.037 | — | — | — | — | — | — |

## D1_A: spread minus low at the same k (paired per pass)

| k | measured (W) | ± SE | 95% | σ from 0 | H | WA | M | A | B side, E70 |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 0.226 | 0.010 | [0.200, 0.253] | 21.9 | 0 | -0.134 | 0.745 | -0.170 | 1.158 |
| 3 | 1.692 | 0.084 | [1.475, 1.908] | 20.1 | 0 | 0.794 | 1.393 | 1.207 | 2.165 |
| 4 | 1.233 | 0.018 | [1.187, 1.280] | 67.5 | 0 | 0.444 | 1.880 | 0.773 | 2.922 |
| 6 | 1.897 | 0.166 | [1.470, 2.323] | 11.4 | 0 | 1.254 | 2.270 | 3.055 | 3.528 |
| 8 | 2.818 | 0.051 | [2.688, 2.948] | 55.7 | 0 | 1.190 | 2.483 | 3.959 | 3.860 |
| 12 | 2.556 | 0.022 | [2.499, 2.614] | 115.2 | 0 | 1.005 | 2.180 | 6.691 | 3.388 |
| 16 | 0.761 | 0.059 | [0.610, 0.912] | 13.0 | 0 | 0.337 | 0.891 | 6.564 | 1.385 |

## D2_A: what collapses the two A layouts (15 rungs; `alq_h23` out of sample)

| law | free parameters | rms (W) |
|---|---|---|
| a free value per k (the best any 'how many' law can do) | one per k | 0.877 (matched k only 0.908) |
| one saturating curve in A's own sum S_A, W refitted (5.90 W) | 1 | 0.708 |
| the same curve, W frozen at E70's 6.37 W | 0 | 0.732 |
| the mirror: c × the same mask's B rung (E70), c refitted (0.6779) | 1 | 0.248 |
| the mirror, c frozen at 0.643 | 0 | 0.308 |
| additive (S_A) | 0 | 6.011 |

Out of sample for the frozen laws, the 7 spread rungs alone: mirror (c 0.643) 0.259 W, WA (6.37 W) 0.226 W, additive 7.417 W.

Per-pass refits: W 5.900 ± 0.082 W; c 0.6779 ± 0.0067.

Out of sample, `alq_h23` (7.598 ± 0.032 W): the refitted S_A curve misses it by 1.721 W (54.5 SE) and it sits 1.699 W (53.8 SE) above the refitted W; the refitted mirror misses it by -0.635 W (-20.1 SE), the frozen mirror by -0.215 W.

## rho(8): per designed bit, A over B, at the same mask (E113's own B ties)

- low: 1.366 ± 0.106 (ratio of means 1.334)
- spread: 1.350 ± 0.012 (ratio of means 1.350)
- spread − low: -0.016 ± 0.103

## Replicate of E70 and the B tie

| item | E113 | ± SE | E70 | difference | band |
|---|---|---|---|---|---|
| `alq_h1` | 0.314 | 0.058 | 0.282 | +0.032 | 0.6 |
| `alq_h2` | 0.951 | 0.025 | 0.829 | +0.122 | 0.6 |
| `alq_h4` | 1.594 | 0.026 | 1.578 | +0.016 | 0.6 |
| `alq_h8` | 2.026 | 0.028 | 1.957 | +0.069 | 0.6 |
| `alq_h12` | 3.504 | 0.043 | 3.482 | +0.022 | 0.6 |
| `alq_h16` | 5.743 | 0.071 | 5.709 | +0.034 | 0.6 |
| `alq_h23` | 7.598 | 0.032 | 7.560 | +0.038 | 1.0 |
| `ls_h8` − `lq_h8` | 4.140 | 0.187 | 3.860 | +0.280 | 0.6 |

Random words: `nrd_a` 7.195 W, `nrd_b` 10.842 W, ratio 0.664 ± 0.006 (mirror c 0.643); the refitted S_A curve predicts `nrd_a` 5.585 W (measured/predicted 1.288).

## The registered rules

| rule | asked | measured | verdict |
|---|---|---|---|
| P1 | dW(als_h8) - dW(alq_h8) > 1.0 W at >= 3 SE (H needs 0; WA 1.19, M 2.48, A 3.96 W) | measured 2.818; se 0.051 | **PASS** |
| P2 | one saturating curve in A's own additive sum S_A, W refitted on the 15 A rungs: ACCEPTED if rms <= 0.40 W, REJECTED if > 0.60 W (E70: 1.063 W on the low layout alone) | measured 0.708; WA_refit_W 5.899 | **REJECTED** |
| P3 | the mirror law with c frozen at 0.643 (fitted on E70's low layout; no free parameter): rms over the 7 spread rungs <= 0.50 W PASS, > 0.80 W FAIL (WA frozen and law A beside it, reported) | measured 0.259; R_SA_frozen_spread_W 0.226; R_A_additive_spread_W 7.417; R_M_frozen_all15_W 0.308; c_refit 0.678 | **PASS** |
| P4 | the verdict on the A side's form, read off D1_A(8) and D2_A together (README) | R_k_W 0.877; R_SA_refit_W 0.708; R_M_refit_W 0.248; one_parameter_laws the mirror law (the same mask's B rung, scaled) collapses the A side better than a curve in S_A | **which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k** |
| P5 | rho(8) per designed bit, A over B, in both layouts inside [0.7, 2.5] and |spread - low| <= 0.30 (M: 1.29 both; WA spread 1.40; A spread 2.74; H spread 0.55) | rho_low 1.366; rho_spread 1.350; spread_minus_low -0.016; se 0.103 | **PASS** |
| P6 | E70's seven alq rungs within 0.6 W (alq_h23 within 1.0 W) and ls_h8 - lq_h8 within 0.6 W of 3.860 W | alq_outside []; D1_B_h8 4.140; D1_B_h8_diff 0.280 | **PASS** |
| P7 | the random-word check: dW(nrd_a) / dW(nrd_b) in the same passes inside [0.55, 0.75] (M: c = 0.643; E70's own pair read 0.668, seen before this registration) | measured 0.664; se 0.006 | **PASS** |

## Arms (reported, never verdicts)

| arm | passes kept | D1_A(8) | R_k | R_SA refit (W) | R_M frozen | R_M refit | c refit | rho8 low / spread | verdicts P1-P7 |
|---|---|---|---|---|---|---|---|---|---|
| all passes (E67's gates, no D-a) | [1131, 1132, 1133, 1134, 1135, 1136, 1137] | 2.837 ± 0.047 | 0.885 | 0.669 | 0.380 | 0.265 | 0.6948 | 1.413 / 1.385 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| leakage 0.2 W per C | [1131, 1132, 1133, 1134, 1135, 1136] | 2.812 ± 0.050 | 0.874 | 0.716 | 0.288 | 0.243 | 0.6727 | 1.366 / 1.349 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| leakage 0.3 W per C | [1131, 1132, 1133, 1134, 1135, 1136] | 2.797 ± 0.051 | 0.865 | 0.737 | 0.247 | 0.231 | 0.6597 | 1.366 / 1.346 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
| leakage 0.4 W per C | [1131, 1132, 1133, 1134, 1135, 1136] | 2.782 ± 0.056 | 0.856 | 0.759 | 0.222 | 0.222 | 0.6467 | 1.366 / 1.344 | P1:PASS P2:REJECTED P3:PASS P4:which bits (as on the B side): the two A layouts collapse on a one-parameter law, not on k P5:PASS P6:PASS P7:PASS |
