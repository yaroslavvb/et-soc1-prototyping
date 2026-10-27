# E70 results — the saturation ladder and the A-side multi-bit ladder (aifoundry3, 600 MHz, 521.6 mV)

Passes run [790, 791, 792, 793, 794, 795, 796]; kept [790, 791, 793, 794, 795, 796]; 203 runs, 0 failed a per-run gate; leakage 0.1975000000000174 W/°C; mean op rate 1.1208 Gop/s per minion.

## Pass health (departures D-a and D-b)

| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (Gop/s) | load1 | gate |
|---|---|---|---|---|---|---|---|
| 790 | 29 | 0 | +0.240 | 0.313 | 1.1209 | 0.72 | kept |
| 791 | 29 | 0 | +0.076 | 0.162 | 1.1208 | 1.32 | kept |
| 792 | 29 | 0 | +0.110 | 0.489 | 1.1209 | 0.72 | SET ASIDE: constant-operand spread 0.49 W |
| 793 | 29 | 0 | +0.031 | 0.101 | 1.1208 | 0.77 | kept |
| 794 | 29 | 0 | +0.071 | 0.136 | 1.1210 | 0.85 | kept |
| 795 | 29 | 0 | +0.101 | 0.119 | 1.1208 | 0.78 | kept |
| 796 | 29 | 0 | +0.063 | 0.152 | 1.1208 | 0.77 | kept |

## lq — the low layout (B's low h mantissa bits), each rung against lq_h0

| item | h | designed bits/op | measured ΔW | SE | fJ per flipped bit | W per flipped position | additive sum S | measured/S | law W (frozen) | law A | E60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `lq_h1` | 1 | 4096 | 0.606 | 0.017 | 132 | 0.606 | 0.625 | 0.969 | 0.610 | 0.625 | 0.594 |
| `lq_h2` | 2 | 8192 | 0.928 | 0.042 | 101 | 0.464 | 1.138 | 0.815 | 1.088 | 1.138 | 0.841 |
| `lq_h3` | 3 | 12288 | 1.294 | 0.016 | 94 | 0.431 | 1.543 | 0.838 | 1.453 | 1.543 | — |
| `lq_h4` | 4 | 16384 | 1.505 | 0.201 | 82 | 0.376 | 2.026 | 0.743 | 1.871 | 2.026 | 1.712 |
| `lq_h6` | 6 | 24576 | 2.357 | 0.083 | 86 | 0.393 | 2.970 | 0.794 | 2.646 | 2.970 | — |
| `lq_h8` | 8 | 32768 | 3.248 | 0.028 | 88 | 0.406 | 3.886 | 0.836 | 3.343 | 3.886 | 3.206 |
| `lq_h12` | 12 | 49152 | 5.502 | 0.041 | 100 | 0.458 | 7.078 | 0.777 | 5.414 | 7.078 | 5.536 |
| `lq_h16` | 16 | 65536 | 8.364 | 0.028 | 114 | 0.523 | 15.122 | 0.553 | 8.799 | 15.122 | 8.299 |
| `lq_h23` | 23 | 94208 | 12.145 | 0.158 | 115 | 0.528 | 40.384 | 0.301 | 12.073 | 40.384 | 12.261 |

## ls — the spread layout (h bits spread over B's mantissa), each rung against lq_h0

| item | h | designed bits/op | measured ΔW | SE | fJ per flipped bit | W per flipped position | additive sum S | measured/S | law W (frozen) | law A | E60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `ls_h2` | 2 | 8192 | 2.085 | 0.012 | 227 | 1.043 | 2.192 | 0.952 | 2.011 | 2.192 | — |
| `ls_h3` | 3 | 12288 | 3.459 | 0.096 | 251 | 1.153 | 3.693 | 0.937 | 3.200 | 3.693 | — |
| `ls_h4` | 4 | 16384 | 4.427 | 0.036 | 241 | 1.107 | 5.410 | 0.818 | 4.397 | 5.410 | — |
| `ls_h6` | 6 | 24576 | 5.885 | 0.118 | 214 | 0.981 | 9.460 | 0.622 | 6.649 | 9.460 | — |
| `ls_h8` | 8 | 32768 | 7.108 | 0.049 | 194 | 0.889 | 12.628 | 0.563 | 7.970 | 12.628 | — |
| `ls_h12` | 12 | 49152 | 8.890 | 0.050 | 161 | 0.741 | 19.987 | 0.445 | 10.012 | 19.987 | — |
| `ls_h16` | 16 | 65536 | 9.749 | 0.250 | 133 | 0.609 | 28.039 | 0.348 | 11.226 | 28.039 | — |

## alq — the A-side ladder (A's low k mantissa bits), each rung against aq_h0

| item | h | designed bits/op | measured ΔW | SE | fJ per flipped bit | W per flipped position | additive sum S | measured/S | law W (frozen) | law A | E60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `alq_h1` | 1 | 2048 | 0.282 | 0.070 | 123 | 0.282 | 0.459 | 0.615 | 0.451 | 0.459 | — |
| `alq_h2` | 2 | 4096 | 0.829 | 0.097 | 181 | 0.414 | 1.599 | 0.518 | 1.502 | 1.599 | — |
| `alq_h4` | 4 | 8192 | 1.578 | 0.017 | 172 | 0.394 | 3.150 | 0.501 | 2.787 | 3.150 | — |
| `alq_h8` | 8 | 16384 | 1.957 | 0.070 | 107 | 0.245 | 5.784 | 0.338 | 4.637 | 5.784 | — |
| `alq_h12` | 12 | 24576 | 3.482 | 0.016 | 126 | 0.290 | 9.025 | 0.386 | 6.441 | 9.025 | — |
| `alq_h16` | 16 | 32768 | 5.709 | 0.136 | 155 | 0.357 | 15.913 | 0.359 | 9.030 | 15.913 | — |
| `alq_h23` | 23 | 47104 | 7.560 | 0.042 | 143 | 0.329 | 32.852 | 0.230 | 11.657 | 32.852 | — |

**What the fJ-per-flipped-bit column is, exactly** (inherited from E65/E67 so that the additive sums `S` stay addable): `fJ_per_bit = 1e15 · ΔW / (designed_bits_per_op · rate)`, where ΔW is a **board** power step for the whole card, `designed_bits_per_op` is the manifest's per-operand-tile flip count and `rate` is the measured op rate **per minion**. The three are not referred to one common denominator, so these figures are a within-experiment currency for comparing rungs — **they must not be carried into Q128's gate-level per-flip ledger** until that scope is settled. No E70 verdict uses them: every discriminator below is in watts or dimensionless.

## D1 — the matched-h layout contrast (the sharpest discriminator)

| h | measured ΔW(ls) − ΔW(lq) | SE | SE from zero | law A / H-offset predict | law W predicts | H-strong predicts |
|---|---|---|---|---|---|---|
| 2 | +1.158 | 0.046 | 25.2 | 1.054 | 0.923 | 0.000 |
| 3 | +2.165 | 0.093 | 23.3 | 2.150 | 1.748 | 0.000 |
| 4 | +2.922 | 0.194 | 15.1 | 3.384 | 2.526 | 0.000 |
| 6 | +3.528 | 0.162 | 21.8 | 6.489 | 4.004 | 0.000 |
| 8 | +3.860 | 0.052 | 73.9 | 8.742 | 4.627 | 0.000 |
| 12 | +3.388 | 0.035 | 95.5 | 12.909 | 4.598 | 0.000 |
| 16 | +1.385 | 0.227 | 6.1 | 12.916 | 2.427 | 0.000 |

## D2 — which variable the two layouts collapse on

Fit set: **8 lq (h = 1..16) + 7 ls = 15; lq_h23 excluded as registered (both layouts own it)**. The fitted rungs span ΔW = 0.606 … 9.749 W.

- `R_h` (best any "how many" law can do: free value per h) over 15 rungs: **1.358 W**; over the matched-h pairs only: 1.406 W
- `R_S` (one-parameter coverage curve in the additive sum, ceiling refitted on E70's own rungs, W∞ = 10.52 W): **0.232 W**
- the same curve with the ceiling **frozen** at E60's 12.58 W: 0.595 W
- pure additivity (law A): 6.062 W
- **verdict: shared wires (which bits): the layouts collapse on the additive sum, not on h**

**The excluded top rung, as a check on the two ceilings.** `lq_h23` (ΔW 12.145 ± 0.158 W) is out of the fit by registration, so it tests both curves out of sample: the **refitted** ceiling misses it by **+1.851 W** (11.7 SE, 8.0× the fit's own 0.232 W rms), while the **frozen** 12.58 W curve predicts it to +0.072 W (0.5 SE). The rung also sits +1.625 W (10.3 SE) **above the refitted asymptote itself** — so W∞ is the fit's curvature parameter, not a bound on power. Refitting with the rung included gives W∞ = 11.36 W at rms 0.424 W (reported for context; the registered fit is the 15-rung one).

## D3 — is one shared turn-on enough?

`T_implied = (S − ΔW)/(h − 1)` over the 14 B-side rungs with h > 1 (it is undefined at h = 1, so one of the 15 fitted rungs drops out): 0.091 … 1.219 W, a factor of 13.4, against the grid's 1.351 ± 0.281 W. H-offset needs one constant.

## D4 — the carry-over between operands, measured at each Hamming weight

| h | ρ = A price per bit / B price per bit (mean of per-pass ratios) | SE | ρ, ratio of means | ΔW(alq) | ΔW(lq) | law A predicts | law W predicts |
|---|---|---|---|---|---|---|---|
| 1 | 0.932 | 0.233 | 0.931 | 0.282 | 0.606 | 1.47 | 1.48 |
| 2 | 1.821 | 0.253 | 1.787 | 0.829 | 0.928 | 2.81 | 2.76 |
| 4 | 2.602 | 0.755 | 2.097 | 1.578 | 1.505 | 3.11 | 2.98 |
| 8 | 1.205 | 0.041 | 1.205 | 1.957 | 3.248 | 2.98 | 2.77 |
| 12 | 1.266 | 0.011 | 1.266 | 3.482 | 5.502 | 2.55 | 2.38 |
| 16 | 1.365 | 0.033 | 1.365 | 5.709 | 8.364 | 2.10 | 2.05 |
| 23 | 1.246 | 0.020 | 1.245 | 7.560 | 12.145 | — | — |

The headline ρ is a **mean of per-pass ratios**; the ratio of the two means is given beside it because the denominator is noisy at low h (at h = 4 the two read 2.602 against 2.097; from h = 8 up they agree to 0.001).
The two numbers Q128 had to choose between: raw single-bit median 1.57, turn-on-corrected median 1.01.

**The number Q128's chain should use.** On the registered window — h = 12 and 16 (P6: near a random fp32 word's 13.9 average Hamming distance) — ρ = **1.316**, the mean of ρ(12) = 1.266 ± 0.011 and ρ(16) = 1.365 ± 0.033. The two differ by more than their own SEs, so the honest dispersion is the **between-h spread, 0.070** — not a standard error (the propagated per-h SE is 0.017). **ρ(12) = 1.266 ± 0.011** is the cleanest single number at a random fp32 word's Hamming weight. Averaging h = 23 in as well gives 1.293 (between-h SD 0.064) and is a departure from the registered window.

## The A-side fit, and why its saturating form is rejected

A coverage curve fitted on the seven `alq` rungs gives W∞ = **6.37 W** at a fit rms of 1.063 W — 4.6× the B side's. **That form does not describe the A side**: the fitted asymptote lies 1.187 W (28 SE) **below** the ladder's own top rung `alq_h23` (7.560 ± 0.042 W), and the ladder's increments **accelerate** where saturation requires them to decay (+0.547, +0.749, +0.380, +1.525, +2.226, +1.851 W).

| rung | k | residual vs the A curve (W) | in SE |
|---|---|---|---|
| `alq_h1` | 1 | -0.160 | -2.3 |
| `alq_h2` | 2 | -0.585 | -6.0 |
| `alq_h4` | 4 | -0.908 | -53.4 |
| `alq_h8` | 8 | -1.844 | -26.3 |
| `alq_h12` | 12 | -1.344 | -83.8 |
| `alq_h16` | 16 | -0.139 | -1.0 |
| `alq_h23` | 23 | +1.224 | 29.1 |

The A fit is therefore reported as a **fitted parameter of a rejected form**, not as a measured ceiling. For P5's ceiling clause the ratio to the B side is 0.51 against the **frozen** B ceiling (12.58 W) and 0.61 against the **refitted** one (10.52 W) — outside 1.5× of either, so P5's second clause fails whichever B ceiling is used. A flip-rate-scaled prediction is 6.29 W from the frozen ceiling and 5.26 W from the refitted one; the A fit (6.37 W) is near the first and 21% off the second, so flip-rate scaling is a statement about the frozen ceiling only and is **not** established by E70.

### The two fitted W∞, with between-pass scatter

| side | pooled fit | per-pass fits | per-pass mean ± SE |
|---|---|---|---|
| B (15 rungs) | 10.521 W | 10.63, 10.72, 10.72, 10.54, 10.93, 9.61 | **10.52 ± 0.19 W** (6 passes) |
| A (7 rungs) | 6.373 W | 6.51, 6.08, 6.48, 6.49, 6.39, 6.30 | **6.38 ± 0.07 W** (6 passes) |

🛑 W_inf is the fitted curvature of the coverage curve, NOT an upper bound on power, and the two sides' values are not added: nrd_a and nrd_b (the measured random-operand steps) and the ladders' own top rungs both exceed them. See A_ceiling.form_verdict and D2.excluded_rung.

## D5 — the closure: do the price lists reproduce a random-word step once the law is applied?

| item | additive sum S | measured ΔW (E70) | ratio additive | selected law (refit W∞), ratio | frozen W∞, ratio | E67's ratio |
|---|---|---|---|---|---|---|
| `nrd_a` | 17.30 | 7.209 ± 0.015 | 0.42 | 8.49 W, **0.85** | 9.40 W, 0.77 | 0.43 |
| `nrd_b` | 21.85 | 10.785 ± 0.024 | 0.49 | 9.20 W, **1.17** | 10.36 W, 1.04 | 0.50 |

Both measured random-operand steps exceed their own side's fitted W∞ — `nrd_a` 7.209 ± 0.015 W against the A fit's 6.37 W, `nrd_b` 10.785 ± 0.024 W against the refitted 10.52 W — which is the same evidence as the top rungs: the fitted W∞ is a curvature, not a cap.

## The registered rules, scored

| rule | what it asked | measured | verdict |
|---|---|---|---|
| **P1** | dW_ls - dW_lq > 2.0 W at >= 3 SE at h = 8 (H-strong needs 0) | 3.860 +- 0.052 W (73.9 SE from zero) | **PASS** |
| **P2** | ls rms vs law W's frozen curve <= 2.0 W, and <= law A's rms / 3 — over the 7 ls rungs (the registration's prose says 6, a count stale after amendment A18 added ls h = 3 and 6; its own prediction table lists 7) | law W rms 0.832 W, law A rms 8.468 W, factor 10.18 | **PASS** |
| **P3** | Spearman rho(dW/S, S) < -0.7, and the partial relation of dW/S with h at fixed S weaker than with S at fixed h (the two Spearman rho of the residuals of a single-variable fit) | clause 1: rho vs S -0.804. clause 2 (registered partial, level-space residuals): rho(resid-after-S, h) -0.149 vs rho(resid-after-h, S) -0.229 -> holds; residualising in RANK space instead gives -0.250 vs -0.075 -> fails (the registration does not name the space). The two UNIVARIATE rho, which this script compared when E70 was first published and which are not the registered clause: -0.804 vs -0.836 | **PASS** |
| **P4** | T_implied spans > 4x over the B-side rungs, and >= 1 rung > 3 SE from the grid's 1.351 W | span 13.4x (0.091..1.219 W), 10 of 14 rungs beyond 3 SE (T_implied is undefined at h = 1, so the D3 set is 14 of the 15 fitted rungs) | **PASS** |
| **P5** | dW_alq(23)/23 below dW_alq(1) by >= 2x, and the A ceiling within 1.5x of the B ceiling | bend factor 0.86x (no bend by that metric), A fit 6.37 W against B frozen 12.58 W (ratio 0.51) and B refit 10.52 W (ratio 0.61) — outside 1.5x of either; and the A-side saturating FORM is rejected outright: its asymptote lies 1.19 W (28 SE) BELOW alq_h23 | **FAIL** |
| **P6** | rho(12) and rho(16) in [0.7, 2.5], and rho(16) < rho(2); the measured rho(12..16) is the number Q128's chain should use, with its interval | rho(2) 1.82, rho(12) 1.266 +- 0.011, rho(16) 1.365 +- 0.033; registered window mean 1.316 (between-h spread 0.070, a spread and not an SE) | **PASS** |
| **P7** | both closure ratios in [0.7, 1.4] with the law D2 selects (E67's raw: 0.43, 0.50) | selected law (coverage curve, ceiling refitted on E70's 15 rungs): nrd_a 0.85, nrd_b 1.17; with the ceiling frozen at 12.58 W: 0.77, 1.04; with each side's own fitted ceiling: 1.21, 1.17 | **PASS** |
| **P8** | E60's 7 lq rungs reproduce within 0.6 W (lq_h23 within 1.0 W) | largest |E70 - E60| below h=23: 0.207 W; lq_h23 0.116 W | **PASS** |

## Leakage sensitivity (departure D-d)

| rung | 0.2 W/°C | 0.3 W/°C | 0.4 W/°C |
|---|---|---|---|
| `alq_h1` | 0.346 | 0.328 | 0.310 |
| `alq_h12` | 3.550 | 3.480 | 3.410 |
| `alq_h16` | 5.771 | 5.698 | 5.625 |
| `alq_h2` | 0.898 | 0.866 | 0.834 |
| `alq_h23` | 7.629 | 7.539 | 7.449 |
| `alq_h4` | 1.634 | 1.595 | 1.556 |
| `alq_h8` | 2.021 | 1.967 | 1.912 |
| `lq_h1` | 0.602 | 0.580 | 0.559 |
| `lq_h12` | 5.494 | 5.431 | 5.367 |
| `lq_h16` | 8.353 | 8.251 | 8.148 |
| `lq_h2` | 0.913 | 0.888 | 0.863 |
| `lq_h23` | 12.112 | 11.970 | 11.828 |
| `lq_h3` | 1.292 | 1.256 | 1.221 |
| `lq_h4` | 1.530 | 1.493 | 1.457 |
| `lq_h6` | 2.371 | 2.314 | 2.256 |
| `lq_h8` | 3.246 | 3.184 | 3.121 |
| `ls_h12` | 8.884 | 8.783 | 8.682 |
| `ls_h16` | 9.798 | 9.673 | 9.548 |
| `ls_h2` | 2.071 | 2.042 | 2.013 |
| `ls_h3` | 3.472 | 3.414 | 3.356 |
| `ls_h4` | 4.414 | 4.356 | 4.297 |
| `ls_h6` | 5.900 | 5.835 | 5.771 |
| `ls_h8` | 7.106 | 7.032 | 6.958 |
| `nrd_a` | 7.260 | 7.172 | 7.084 |
| `nrd_b` | 10.784 | 10.662 | 10.539 |

