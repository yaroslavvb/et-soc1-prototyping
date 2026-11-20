# MM1's frozen matmul models scored BLIND on E219 (blind-e219, round Q232)

*Scored Fri 20 Nov 2026 at the desk on aifoundry2: the read Fri 20 Nov 2026 00:21:14 PST; Python /usr/bin/python3 3.12.3 (numpy 1.26.4 for the forecasts), every numerical step single-threaded inside the round's CPU slots. No card, no device, no ssh. Nothing here is committed by this lane.*

**What this is.** E219 is the model session's fifth matmul sweep (1119-mmsweep5, Discussion #14): rgm136's host over its gemmL loop and its block, stream and TenB arms, 412 runs in five sessions on aifoundry1 (card 1 S1-S3 at 600 MHz, card 0 S1-S2 at low power under its governor). Before any E219 datum existed, the lab DECLARED how it would score its frozen models on E219, with MM1's domain stated first (decl-e219: `../blind-e219/DECLARED-blind-e219.md`, sha256 d629bd14..., FROZEN.txt 73a2dd75... at 18:37:50 PST Thu 19 Nov, posted on the Discussion as #14.1.1). Of E219's 314 cases, 139 are IN DOMAIN (rgm136's gemmL loop: the 1x1x1 controls CTRL, the gap cells GAP and the anchor; run_gemm's c-arm table CTAB; the gemmc16r<R> ladder C16R) and forecast; 175 are OUT OF DOMAIN (no frozen MM1 has a form for their arms) and are reported apart, measured values only. This folder is that test, run EXACTLY as declared: every frozen file's sha256 checked, the forecasts made by the declared procedure at each run's measured clock, minion volts and die at start and hashed, the scorer code-tested and hashed, and only then the measurements read and scored.

**Label: BLIND (every session: its first datum after the freeze post).** The freeze post #14.1.1 is stamped 2026-11-19 18:42:28.612 PST by the post itself and 18:42:34 PST in the round's record; the later is used. Every session's claim and first card command come more than an hour after it:

| session | label | claim (PST) | T0 (PST) | first card command (queue / README) | minutes after the freeze post | in-domain runs | MM1-v3.1 per run, REPORTED: wall / J over idle given t |
|---|---|---|---|---|---|---|---|
| a1c0-S1 | BLIND | #14.1.1.1.1.1 20:30:45 | 20:30:48 | 20:30:52.130 / 20:30:52.130 | 108.3 | 44 | 1.76% / 1.81% |
| a1c0-S2 | BLIND | #14.1.1.1.1.1.1.1.1.1 21:57:53 | 21:57:58 | 21:58:01.757 / 21:58:01.757 | 195.5 | 38 | 4.89% / 3.55% |
| a1c1-S1 | BLIND | #14.1.1.1 19:50:39 | 19:50:45 | 19:50:48.917 / 19:50:48.917 | 68.2 | 34 | 1.88% / 5.90% |
| a1c1-S2 | BLIND | #14.1.1.1.1.1.1.1 21:14:41 | 21:14:46 | 21:14:49.569 / 21:14:49.569 | 152.3 | 47 | 1.85% / 5.89% |
| a1c1-S3 | BLIND | #14.1.1.1.1.1.1.1.1.1.1.1 22:34:44 | 22:34:48 | 22:34:52.364 / 22:34:52.364 | 232.3 | 40 | 5.68% / 4.48% |

## 1. The verdict (decided by the script, as declared)

**PASS.** Part A (MM1-v3.1 on the primary footing, E215's rule form, each card over its in-domain no-twin cases, every class) **PASS**: no rule fails on either card. Part S is NOT APPLICABLE (E219 has no operand-pattern arm), so the verdict is part A's. A rule passes when 90% of its cases are inside the band.

| rule (band card 1 / card 0) | aifoundry1 card 1 | aifoundry1 card 0 |
|---|---|---|
| T1 (10% / 11%) | PASS 71/75 | PASS 51/52 |
| T2 (13% / 16%) | PASS 73/75 | PASS 52/52 |
| T3 (10% / 11%) | PASS 71/75 | PASS 51/52 |
| E1 (14% / 11%; watts 0.56 W) | PASS 78/79 | PASS 52/52 |
| E2 (14% / 13%; watts 0.56 W) | PASS 77/79 | PASS 52/52 |
| E3 (5% / 5%) | PASS 79/79 | PASS 52/52 |
| E4 (10% / 10%) | PASS 77/79 | PASS 51/52 |

T1 wall cycles an op (the slowest minion), T2 the counter's mean cycles an op, T3 seconds a pass (the kit's ops a minion a pass x the op time), E1 J over idle given the measured op time (watts at a case under 3 W), E2 J over idle with the op time forecast, E3 J with the card at rest given t, E4 J at rest with t forecast. The misses, case by case (MM1-v3.1's error; MM1-v3 and MM1-v2 beside):

| card | rule | case (arm, format, kind) | class | MM1-v3.1 | MM1-v3 | MM1-v2 | measured cycles an op | measured W over idle |
|---|---|---|---|---|---|---|---|---|
| card 0 | E4 | gemmL1x13x6 fp16 ones | GAP | +13.3% | +12.1% | +8.1% | 1314.2 | 18.60 W |
| card 0 | T1 | gemmL1x13x6 fp16 ones | GAP | +15.2% | +14.5% | +4.5% | 1314.2 | 18.60 W |
| card 0 | T3 | gemmL1x13x6 fp16 ones | GAP | +15.2% | +14.5% | +4.5% | 1314.2 | 18.60 W |
| card 1 | E1 | gemmc16 int8 zeros | CTAB | -15.9% | -14.7% | -2.9% | 1547.1 | 4.46 W |
| card 1 | E2 | gemmc16r2 int8 zeros | C16R | -14.7% | -13.7% | -2.9% | 912.3 | 4.61 W |
| card 1 | E2 | gemmc16 int8 zeros | CTAB | -17.0% | -16.0% | -4.9% | 1547.1 | 4.46 W |
| card 1 | E4 | gemmL1x11x6 fp32 zeros | GAP | +12.1% | +10.5% | +4.2% | 1087.7 | 4.66 W |
| card 1 | E4 | gemmL2x12x1 int8 zeros | GAP | -11.6% | -11.0% | -23.0% | 1151.3 | 4.48 W |
| card 1 | T1 | gemmL1x11x6 fp32 zeros | GAP | +12.8% | +11.1% | +3.5% | 1087.7 | 4.66 W |
| card 1 | T1 | gemmL1x13x6 fp16 random | GAP | +13.4% | +12.5% | +3.5% | 1087.7 | 19.52 W |
| card 1 | T1 | gemmL2x12x1 int8 zeros | GAP | -11.6% | -11.7% | -22.8% | 1151.3 | 4.48 W |
| card 1 | T1 | gemmL4x4x2 fp32 ones | GAP | +12.2% | +12.8% | +10.1% | 966.5 | 10.78 W |
| card 1 | T2 | gemmL1x13x6 fp16 random | GAP | +13.6% | +12.7% | +3.6% | 1087.7 | 19.52 W |
| card 1 | T2 | gemmL4x4x2 fp32 ones | GAP | +13.5% | +14.1% | +11.4% | 966.5 | 10.78 W |
| card 1 | T3 | gemmL1x11x6 fp32 zeros | GAP | +12.8% | +11.1% | +3.5% | 1087.7 | 4.66 W |
| card 1 | T3 | gemmL1x13x6 fp16 random | GAP | +13.4% | +12.5% | +3.5% | 1087.7 | 19.52 W |
| card 1 | T3 | gemmL2x12x1 int8 zeros | GAP | -11.6% | -11.7% | -22.8% | 1151.3 | 4.48 W |
| card 1 | T3 | gemmL4x4x2 fp32 ones | GAP | +12.2% | +12.8% | +10.1% | 966.5 | 10.78 W |

## 2. The headline: in-domain no-twin cases, the primary footing (each run at its measured conditions)

rms % (bias %), n cases; error = forecast / measured - 1; E1 and E2 relative where the case is 3 W or more, watts beside.

| model | wall cycles (T1) | counter mean (T2) | J over idle given t (E1) | J over idle, t forecast (E2) | J at rest given t (E3) | J at rest, t forecast (E4) |
|---|---|---|---|---|---|---|
| MM1-v3.1 | 4.42% (-1.05), n 127 | 4.74% (-0.59), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.01% (-2.10), n 129; watts 0.011 W (-0.010), n 2 | 1.08% (-0.39), n 131 | 3.88% (-1.21), n 131 |
| MM1-v3 | 4.34% (-1.08), n 127 | 4.67% (-0.62), n 127 | 4.10% (-1.25), n 129; watts 0.011 W (-0.010), n 2 | 4.67% (-1.59), n 129; watts 0.010 W (-0.009), n 2 | 1.01% (-0.24), n 131 | 3.74% (-1.09), n 131 |
| MM1-v2 | 5.74% (-2.31), n 134 | 5.76% (-1.90), n 134 | 7.47% (+2.78), n 131; watts 0.087 W (+0.083), n 3 | 7.96% (+1.84), n 131; watts 0.087 W (+0.084), n 3 | 2.06% (+0.64), n 134 | 5.19% (-1.17), n 134 |
| v3.1+contention | 4.42% (-1.05), n 127 | 4.74% (-0.59), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.01% (-2.10), n 129; watts 0.011 W (-0.010), n 2 | 1.08% (-0.39), n 131 | 3.88% (-1.21), n 131 |
| ctrl N1+N2 | 4.42% (-1.04), n 127 | 4.74% (-0.58), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.02% (-2.10), n 129; watts 0.011 W (-0.010), n 2 | 1.08% (-0.39), n 131 | 3.88% (-1.21), n 131 |
| ctrl G1 | 4.42% (-1.04), n 127 | 4.74% (-0.58), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.02% (-2.10), n 129; watts 0.014 W (-0.014), n 2 | 1.08% (-0.39), n 131 | 3.88% (-1.19), n 131 |
| ctrl G1+N1 | 4.42% (-1.05), n 127 | 4.74% (-0.59), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.00% (-2.11), n 129; watts 0.008 W (-0.008), n 2 | 1.08% (-0.39), n 131 | 3.87% (-1.23), n 131 |
| ctrl F1-layout-blind | 4.42% (-1.05), n 127 | 4.74% (-0.59), n 127 | 4.39% (-1.78), n 129; watts 0.011 W (-0.011), n 2 | 5.01% (-2.10), n 129; watts 0.011 W (-0.010), n 2 | 1.08% (-0.39), n 131 | 3.88% (-1.21), n 131 |

T3 (seconds a pass) equals T1 at the measured clock, as the declaration says (the same rms and bias on every scope: True). 'v3.1+contention' equals MM1-v3.1 on every case and quantity (True: its factor is 1 on every E219 case, as declared) and 'v3.1+both' equals 'v3.1+contention' (True); 'v3.1+gemmLnc' is NOT APPLICABLE (E219 runs no gemmLnc arm). MM1-v3.1 per card (no twin):

| card | measured clock of the in-domain runs | wall | counter mean | E1 | E3 | E4 |
|---|---|---|---|---|---|---|
| aifoundry1 card 1 | 599.2-599.4 MHz | 4.44% (-1.11), n 75 | 4.67% (-0.77), n 75 | 5.17% (-2.70), n 77; watts 0.011 W (-0.011), n 2 | 1.01% (-0.55), n 79 | 3.94% (-1.40), n 79 |
| aifoundry1 card 0 | 798.7-799.2 MHz | 4.39% (-0.95), n 52 | 4.84% (-0.33), n 52 | 2.89% (-0.43), n 52 | 1.17% (-0.15), n 52 | 3.77% (-0.93), n 52 |

Twins (a case whose configuration is in the model's training data at the same card, kernel and clock to 25 MHz): MM1-v3.1 12 time and 8 energy twin cases of 139, MM1-v3 12/8, MM1-v2 5/5 (the nominal-clock preview the declaration printed, exactly). MM1-v3.1 on its twin cases: wall 1.36% (-0.73), n 12; on all cases: wall 4.25% (-1.02), n 139, E1 4.38% (-1.78), n 135; watts 0.026 W (-0.022), n 4.

## 3. The comparisons (each its own verdict; exact two-sided sign test on the untied cases, closer A / closer B / ties)

| comparison | H1 wall | H2 counter mean | H3 seconds | H4 J over idle given t | H5 J over idle, t forecast |
|---|---|---|---|---|---|
| D1 MM1-v3.1 vs MM1-v3, pooled | TOO FEW (1/5/133, p 0.219) | TOO FEW (1/5/133, p 0.219) | TOO FEW (1/5/133, p 0.219) | NOT DECIDED (11/13/115, p 0.839) | NOT DECIDED (9/16/114, p 0.230) |
| D1 MM1-v3.1 vs MM1-v3, card 1 | TOO FEW (1/3/80, p 0.625) | TOO FEW (1/3/80, p 0.625) | TOO FEW (1/3/80, p 0.625) | NOT DECIDED (9/11/64, p 0.824) | NOT DECIDED (9/9/66, p 1.000) |
| D1 MM1-v3.1 vs MM1-v3, card 0 | TOO FEW (0/2/53, p 0.500) | TOO FEW (0/2/53, p 0.500) | TOO FEW (0/2/53, p 0.500) | TOO FEW (2/2/51, p 1.000) | TOO FEW (0/7/48, p 0.016) |
| D2 MM1-v3.1 vs MM1-v2, pooled | MM1-v3.1 BETTER (41/14/84, p 0.00036) | MM1-v3.1 BETTER (41/15/83, p 0.00069) | MM1-v3.1 BETTER (41/14/84, p 0.00036) | MM1-v3.1 BETTER (78/27/34, p 6.5e-07) | MM1-v3.1 BETTER (71/34/34, p 0.00039) |
| D2 MM1-v3.1 vs MM1-v2, card 1 | NOT DECIDED (13/8/63, p 0.383) | NOT DECIDED (13/9/62, p 0.523) | NOT DECIDED (13/8/63, p 0.383) | MM1-v3.1 BETTER (40/17/27, p 0.003) | MM1-v3.1 BETTER (36/18/30, p 0.020) |
| D2 MM1-v3.1 vs MM1-v2, card 0 | MM1-v3.1 BETTER (28/6/21, p 0.0002) | MM1-v3.1 BETTER (28/6/21, p 0.0002) | MM1-v3.1 BETTER (28/6/21, p 0.0002) | MM1-v3.1 BETTER (38/10/7, p 6.2e-05) | MM1-v3.1 BETTER (35/16/4, p 0.011) |

Over the cases that are twins for neither model (REPORTED), pooled: D1 H1 TOO FEW (1/5/121, p 0.219), H4 NOT DECIDED (10/12/109, p 0.832); D2 H1 MM1-v3.1 BETTER (38/14/75, p 0.001), H4 MM1-v3.1 BETTER (76/25/30, p 3.7e-07), H5 MM1-v3.1 BETTER (69/32/30, p 0.0003).

D3, on the 6 subset-mask cases (the gemmL 1x1x1 controls at 0xf and 0xff), each candidate as A against MM1-v3.1 as B. As declared before any datum, every D3 test reads TOO FEW (fewer than 10 untied cases); 'v3.1+contention' and the layout-blind F1 equal MM1-v3.1 there, so every case ties:

| D3 | H1 wall, pooled | H1 card 1 | H1 card 0 | H2 counter mean, pooled | H2 card 1 | H2 card 0 |
|---|---|---|---|---|---|---|
| v3.1+contention vs MM1-v3.1 | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) |
| ctrl N1+N2 vs MM1-v3.1 | TOO FEW (0/3/3, p 0.250) | TOO FEW (0/2/2, p 0.500) | TOO FEW (0/1/1, p 1.000) | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) |
| ctrl G1 vs MM1-v3.1 | TOO FEW (0/2/4, p 0.500) | TOO FEW (0/0/4, p none) | TOO FEW (0/2/0, p 0.500) | TOO FEW (2/0/4, p 0.500) | TOO FEW (2/0/2, p 0.500) | TOO FEW (0/0/2, p none) |
| ctrl G1+N1 vs MM1-v3.1 | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) |
| ctrl F1-layout-blind vs MM1-v3.1 | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) | TOO FEW (0/0/6, p none) | TOO FEW (0/0/4, p none) | TOO FEW (0/0/2, p none) |

D4 (the switch route): NOT APPLICABLE: E219 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random).

## 4. Where it holds and where it misses (the declared splits, REPORTED; MM1-v3.1, no twin, pooled)

| split | wall cycles | J over idle given t (E1) | J at rest given t (E3) | part A beside (card 1; card 0): T1, E1, E4 |
|---|---|---|---|---|
| CTRL: the gemmL 1x1x1 controls | 0.01% (n 2) | 6.20% (n 2) | 1.14% (n 4) | T1 NO DATA 0/0, E1 TOO FEW 2/2, E4 TOO FEW 2/2; T1 TOO FEW 2/2, E1 TOO FEW 2/2, E4 TOO FEW 2/2 |
| GAP: the gemmL gap cells | 7.85% (n 34) | 4.03% (n 34) | 1.41% (n 34) | T1 FAIL 16/20, E1 PASS 20/20, E4 PASS 18/20; T1 PASS 13/14, E1 PASS 14/14, E4 PASS 13/14 |
| ANCHOR: 4x8x8 int8 random | - | - | - | T1 NO DATA 0/0, E1 NO DATA 0/0, E4 NO DATA 0/0; T1 NO DATA 0/0, E1 NO DATA 0/0, E4 NO DATA 0/0 |
| CTAB: run_gemm's c-arm table | 3.34% (n 18) | 6.98% (n 20) | 1.52% (n 20) | T1 TOO FEW 8/8, E1 PASS 9/10, E4 PASS 10/10; T1 PASS 10/10, E1 PASS 10/10, E4 PASS 10/10 |
| C16R: the gemmc16r<R> ladder | 1.60% (n 73) | 3.49% (n 73) | 0.67% (n 73) | T1 PASS 47/47, E1 PASS 47/47, E4 PASS 47/47; T1 PASS 26/26, E1 PASS 26/26, E4 PASS 26/26 |
| FULL: the full chip | 4.46% (n 125) | 4.36% (n 127) | 1.07% (n 127) | T1 PASS 71/75, E1 PASS 76/77, E4 PASS 75/77; T1 PASS 49/50, E1 PASS 50/50, E4 PASS 49/50 |
| SUB: the subset masks | 0.01% (n 2) | 6.20% (n 2) | 1.14% (n 4) | T1 NO DATA 0/0, E1 TOO FEW 2/2, E4 TOO FEW 2/2; T1 TOO FEW 2/2, E1 TOO FEW 2/2, E4 TOO FEW 2/2 |
| fp32 | 4.47% (n 47) | 4.04% (n 48) | 1.03% (n 49) | T1 PASS 25/27, E1 PASS 29/29, E4 PASS 28/29; T1 PASS 20/20, E1 PASS 20/20, E4 PASS 20/20 |
| fp16 | 4.19% (n 45) | 3.51% (n 45) | 0.99% (n 46) | T1 PASS 27/28, E1 PASS 29/29, E4 PASS 29/29; T1 PASS 16/17, E1 PASS 17/17, E4 PASS 16/17 |
| int8 | 4.64% (n 35) | 5.65% (n 36) | 1.24% (n 36) | T1 PASS 19/20, E1 PASS 20/21, E4 PASS 20/21; T1 PASS 15/15, E1 PASS 15/15, E4 PASS 15/15 |
| zeros | 3.42% (n 77) | 4.88% (n 78) | 0.96% (n 80) | T1 PASS 32/34, E1 PASS 36/37, E4 PASS 35/37; T1 PASS 43/43, E1 PASS 43/43, E4 PASS 43/43 |
| ones | 7.83% (n 9) | 3.41% (n 10) | 1.64% (n 10) | T1 TOO FEW 4/5, E1 TOO FEW 6/6, E4 TOO FEW 6/6; T1 TOO FEW 3/4, E1 TOO FEW 4/4, E4 TOO FEW 3/4 |
| random | 5.02% (n 41) | 3.55% (n 41) | 1.12% (n 41) | T1 PASS 35/36, E1 PASS 36/36, E4 PASS 36/36; T1 TOO FEW 5/5, E1 TOO FEW 5/5, E4 TOO FEW 5/5 |

Time twins for MM1-v3.1 by class: CTRL 6 of 8, GAP 0 of 34, ANCHOR 2 of 2, CTAB 4 of 22, C16R 0 of 73 (its fit holds those configurations from E206, E208, E212 on aifoundry1), so they leave the no-twin headline. MM1-v3 and MM1-v2 by class (no twin, pooled; wall / E1 / E3 rms):

| class | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|
| ANCHOR | - / - / - | - / - / - | - / - / - |
| C16R | 1.60% / 3.49% / 0.67% | 1.58% / 3.31% / 0.66% | 1.71% / 7.08% / 1.77% |
| CTAB | 3.34% / 6.98% / 1.52% | 3.35% / 6.67% / 1.44% | 3.53% / 7.35% / 1.80% |
| CTRL | 0.01% / 6.20% / 1.14% | 0.01% / 6.55% / 1.21% | 0.56% / 12.87% / 2.15% |
| GAP | 7.85% / 4.03% / 1.41% | 7.69% / 3.38% / 1.29% | 10.75% / 7.91% / 2.69% |

**Post hoc readings (made after the read; REPORTED; they decide nothing).** Every time miss of part A is a GAP cell (True), and MM1-v2 is closer than MM1-v3.1 on 4 of the 5 T1 misses; the c-arm energy misses are card 1 gemmc16 int8 zeros; card 1 gemmc16r2 int8 zeros (MM1-v3.1 under-forecasts their W over idle).

## 5. Reported beside (deciding nothing)

**The R ladder** (C16R with gemmc16 as R = 1; R 2, 4, 8 and 32 were in MM1-v3.1's fit, on other cards; R 3, 5, 6, 12, 16 and 24 never were). MM1-v3.1's wall-cycle error by R, and, post hoc, a straight line in 1/R through it (its value at R -> infinity and its slope per unit 1/R; the residual rms):

| card, format, kind | R 1 | R 2 | R 3 | R 4 | R 5 | R 6 | R 8 | R 12 | R 16 | R 24 | R 32 | at R -> inf | slope per 1/R | residual |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| card 0 fp16 zeros | -4.6% | -2.9% | -2.5% | -1.9% | -1.5% | -1.3% | -0.9% | -0.4% | -0.1% | +0.2% | +0.3% | -0.15% | -4.99% | 0.44% |
| card 0 fp32 zeros | -4.4% | -3.1% | -2.4% | -1.8% | -1.5% | -1.3% | -0.8% | -0.4% | -0.1% | +0.2% | +0.4% | -0.15% | -4.88% | 0.46% |
| card 0 int8 zeros | -4.2% | -2.6% | - | -2.3% | - | - | -1.8% | - | -1.3% | -1.1% | -0.9% | -1.14% | -3.16% | 0.23% |
| card 1 fp16 random | -4.4% | -2.9% | -2.2% | -1.8% | -1.4% | -1.2% | -0.8% | -0.4% | -0.2% | +0.1% | +0.2% | -0.18% | -4.67% | 0.37% |
| card 1 fp16 zeros | -4.4% | -2.8% | -2.2% | -1.8% | -1.4% | -1.2% | -0.8% | -0.4% | -0.2% | +0.1% | +0.2% | -0.17% | -4.68% | 0.36% |
| card 1 fp32 random | -4.4% | -2.9% | - | -1.8% | - | - | -0.8% | - | - | - | - | -0.63% | -3.92% | 0.23% |
| card 1 fp32 zeros | -4.4% | -2.8% | -2.2% | -1.8% | -1.4% | -1.2% | -0.8% | -0.4% | -0.2% | +0.1% | +0.2% | -0.17% | -4.70% | 0.36% |
| card 1 int8 random | -4.1% | -2.7% | - | -2.3% | - | - | -2.0% | - | -1.6% | -1.4% | -1.3% | -1.44% | -2.67% | 0.15% |
| card 1 int8 zeros | -4.0% | -2.7% | - | -2.4% | - | - | -2.0% | - | -1.6% | -1.4% | -1.4% | -1.46% | -2.61% | 0.15% |

By group (rms of the case errors, twins included; wall / E1 relative):

| card | group | cases | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| card 0 | R in a fit (2, 4, 8, 32) | 12 | 1.89% / 1.21% | 1.75% / 0.74% | 2.51% / 5.88% |
| card 0 | R never in a fit (3, 5, 6, 12, 16, 24) | 14 | 1.28% / 0.69% | 1.19% / 0.53% | 1.70% / 6.82% |
| card 0 | gemmc16 (R = 1) | 3 | 4.42% / 1.41% | 4.15% / 0.91% | 5.57% / 4.54% |
| card 1 | R in a fit (2, 4, 8, 32) | 25 | 1.85% / 5.19% | 1.89% / 4.93% | 1.65% / 6.32% |
| card 1 | R never in a fit (3, 5, 6, 12, 16, 24) | 22 | 1.26% / 2.94% | 1.29% / 2.88% | 1.14% / 8.52% |
| card 1 | gemmc16 (R = 1) | 6 | 4.29% / 10.46% | 4.38% / 9.75% | 3.89% / 3.59% |

Post hoc: MM1-v3.1's wall error rises steadily with R across the 9 ladders: -4.6% to -4.0% at R = 1, -1.4% to +0.4% at R = 32; a straight line in 1/R fits each ladder to 0.15-0.46% rms, the never-fitted rungs on the same line as the fitted ones. Read through the declared form (1 - 1/R of the ops with A and B at the L2, 1/R with A fresh), the model under-prices the 1/R part: the cost of an op with A fresh, at each block's first pass.

**The gemmc4s / gemmc8s pair** (decl-e219's finding 2: MM1 gives the two the same class form): on aifoundry1 card 0 fp32 zeros the measured wall cycles an op are 1015.4 (gemmc4s) and 1018.8 (gemmc8s), ratio 1.0034; MM1-v3.1 forecast 1008.4 and 1008.3 at each run's own clock (-0.69% and -1.03%). It is the only pair E219 ran on one card, format and kind.

**The CTRL cases beside E217.** E217 ran 0 of the 8 CTRL configurations (the same card, arm, format, kind and mask), so the declared tie has nothing to compare. Post hoc, the same arm, format, kind and mask ran in E217 on aifoundry1's other card for 4 of them (another card and clock; cycles an op only):

| E219 case | its measured cycles an op | E217, the other card | its clock | its measured cycles an op | E219 / E217 - 1 |
|---|---|---|---|---|---|
| card 0 gemmL1x1x1 fp16 zeros | 542.81 | card 1 (2 runs) | 599.4 MHz | 539.38 | +0.64% |
| card 0 gemmL1x1x1 int8 zeros | 392.47 | card 1 (2 runs) | 599.4 MHz | 389.78 | +0.69% |
| card 1 gemmL1x1x1 fp16 zeros 0xff | 538.88 | card 0 (1 run) | 798.8 MHz | 541.78 | -0.54% |
| card 1 gemmL1x1x1 fp32 zeros 0xff | 538.89 | card 0 (2 runs) | 798.9 MHz | 541.81 | -0.54% |

**The 175 OUT-OF-DOMAIN cases** (measured values only; in no rule, comparison or headline; every value per case is in `cases/scores-blind-e219-out-of-domain.csv`):

| class | what it is | cases | runs (time / energy read) | measured cycles an op, wall | measured W over idle |
|---|---|---|---|---|---|
| OUT-gemm | the block walk with B packed by k | 10 | 10 (10 / 10) | 848.3-1076.5 | 5.52-28.46 W |
| OUT-gemmc | run_gemm at a B, R or shared-C combination the c-arm table does not hold | 121 | 134 (134 / 134) | 316.9-1047.8 | 3.75-28.78 W |
| OUT-gemmh | gemmc's walk with half the K | 32 | 32 (32 / 32) | 321.0-1025.3 | 4.38-19.82 W |
| OUT-mm | the stream loop (A loaded into the core, B through TenB) | 6 | 6 (6 / 6) | 529.0-529.1 | 4.21-15.84 W |
| OUT-tenb | A held in the core, one B tile through TenB every op | 6 | 7 (7 / 7) | 270.0-529.0 | 2.97-28.28 W |

Post hoc: the stream and TenB arms (12 cases) run at MM1's two TenB floors, 529 cycles an op for fp32 and fp16 and 270 for int8 (E101's tenb loop), within 0.010% in every case; no frozen predictor maps these arms, so this is a reading, not a forecast.

## 6. The nominal footing (frozen by decl-e219 before any datum; scored beside by the same rules; REPORTED, deciding nothing)

The same models at the declared nominal conditions (card 1 600 MHz, 0.517 V, die 60 C; card 0 800 MHz, the model's own volts, die 55 C): VERDICT PASS, part A PASS:

| rule | card 1 | card 0 |
|---|---|---|
| T1 | PASS 71/75 | PASS 51/52 |
| T2 | PASS 72/75 | PASS 52/52 |
| T3 | PASS 71/75 | PASS 51/52 |
| E1 | PASS 79/79 | PASS 49/52 |
| E2 | PASS 78/79 | PASS 49/52 |
| E3 | PASS 79/79 | PASS 49/52 |
| E4 | PASS 75/79 | PASS 51/52 |

MM1-v3.1 no twin, pooled: wall 4.41% (-0.99), n 127, E1 6.38% (+4.82), n 129; watts 0.051 W (+0.046), n 2, E3 2.25% (+1.71), n 131. The nominal die sits above the measured start dies (card 1 44.0-47.7 C against 60 C, card 0 41.0-43.4 C against 55 C), so the nominal energy reads high. Pooled: D1 H1 TOO FEW (1/5/133, p 0.219), H4 NOT DECIDED (14/11/114, p 0.690); D2 H1 MM1-v3.1 BETTER (41/14/84, p 0.00036), H4 NOT DECIDED (55/48/36, p 0.555), H5 NOT DECIDED (53/51/35, p 0.922).

## 7. The order of hashes and times (Pacific), and the checks

- decl-e219's declaration written 18:37:19 PST Thu 19 Nov (its hash logged 18:37:24), the nominal forecasts written 18:37:34, FROZEN.txt 18:37:50, posted #14.1.1 (18:42:28); E219's first card command 19:50:48.917 (a1c1-S1).
- This lane, Fri 20 Nov 2026: every frozen file's sha256 checked at 00:05:34 (MM1-v3.1 64/64, its counts 71/71, MM1-v3 170/170, MM1-v2 114/114, the layout term 25/25 and its note 6/6, the gemmLnc term 22/22, the posted term files, verify-lay's three files, FROZEN.txt, the declaration and the nominal forecasts equal to the posted sha256; decl-e219's land 38/38); the conditions read (only the declared start-of-run fields) at 00:08:40; the forecasts made (the nominal self-check from 00:10:54, the measured conditions from 00:11:24) and hashed at 00:12:50 (forecasts-blind-e219.csv 6ebeb3951b6bd023..., .json a5a3c103b13e34ee...); the scorer tested on two stand-in days (its last test from 00:20:49) and hashed at 00:21:05 (s03_score.py 28039e171fbf7267...); the read and the scores 00:21:14.
- **The procedure check:** this lane's forecast code, run at the declared nominal conditions, re-makes decl-e219's frozen nominal forecasts bit for bit (SAME PROCEDURE: every field bit-equal: 37,551 fields over 203 in-domain runs and nine models, 0 differ; the 189 out-of-domain runs NOT FORECAST as frozen), so the measured-conditions forecasts are the declared procedure with only the conditions changed. The layout factors equal the frozen nominal ones, 695 of 695.
- **The loader check:** the scorer's own selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all, which reads gemmL values only) on the same bytes: 90 gemmL runs, 0 field differences, equal True. The session queues say ran, rc 0 and check exact or approx for 392 of 392 listed runs. The five data files read are byte-equal to the ones the conditions step read (True).
- **The recheck** (an independent code path from the frozen CSV and a fresh read): part A's 14 rule cells, the no-twin rms of the three models and D1's and D2's H1 and H4 tallies all equal the scorer's (True).
- **Counts:** 203 in-domain runs of 392 listed (356 arm + 36 anchor; nulls and smoke left out), 203 with time, 202 with energy (1 capped on card 0: energy not read), 139 in-domain cases (139 with energy, 4 watts cases); the 175 out-of-domain cases read 189 runs for time.

## 8. Disclosures, gaps and what was not run

- **Earlier reads.** This lane's brief quoted the data lanes' result summaries (aggregate board peaks, clock-sample counts, the anchors' joule and time ranges) before the read. No per-run measurement was read before the forecasts and the scorer were hashed, and nothing in the procedure could use them: the predictors, the terms and the scoring rules were frozen before any E219 datum.
- **One reading made explicit before the read:** the declaration's test line says 'TOO FEW under 10 untied cases; NO DATA with none' and its D3 line says every D3 test reads TOO FEW, though two of the D3 candidates tie on every case. The scorer reads NO DATA only when no case is compared (so a cell of cases that all tie reads TOO FEW), which makes the two lines agree; it was coded and stand-in tested before the scorer was hashed, and it decides nothing in part A.
- **The selection:** the declared conditions, applied to every listed run: the session queue's ran, rc 0 and check exact or approx; the data's ran, role, values (the registered arm) and shires; the top-level primary view's op time, wall cycles and launches; ops_pass_ok for every block, stream and TenB run; energy where dP_w is read, p_mean_w is set, the run is not capped and its role is not 'time'.
- **MM1-v3.2** reached GitHub main at 19:50 PST Thu 19 Nov (commit 4e386f75), after the freeze and less than a minute before E219's first claim (19:50:39 PST): it is not in the declaration and is not scored here. The model session's sealed E219 forecast was not read or scored by this lane.
- **NOT RUN here:** a second scorer by another lane (the round's verify lane follows); a figure for the out-of-domain arms beyond their measured values.
- decl-e219's own land (`../blind-e219/`: the declaration, the domain and the nominal forecasts) is not on GitHub main at this writing: it lands first or together with this folder.

## 9. Files

- `forecasts-blind-e219.csv` / `.json`: the frozen measured-conditions forecasts, one row a run, every declared model (W over idle at a measured op time t is W_A + W_B / t; out-of-domain rows NOT FORECAST). `inputs/`: the conditions read (start-of-run fields only), the forecast records at the measured and the nominal conditions, the nominal procedure check.
- `scores/scores-blind-e219.json` (every figure, both footings, the labels, everything reported beside), `scores/scores-blind-e219.txt` (the summary), `cases/scores-blind-e219-cases.csv`, `-runs.csv` and `-out-of-domain.csv`, `scores/posthoc-e219.json` (post hoc), `scores/recheck-e219.json`.
- `scripts/` (the box's paths replaced; `scripts/SCRUB-MAP.json` gives each script's sha256 as run), `logs/` (progress, the hash records, each step's output), `SHA256SUMS`.

To reproduce: from a work copy of GitHub main with decl-e219's land at work/decl/, run s00_setup.sh, then s02a_conditions.py, s02b_forecast.py with --nominal, s02d_nominal_check.py, s02b_forecast.py, s02c_merge.py, s03_score.py, s03p_posthoc.py and s04_recheck.py, each as `/usr/bin/python3 -I -B <script> <lane dir>` inside the CPU slot (run_slot.sh), with the paths put back as SCRUB-MAP.json says.
