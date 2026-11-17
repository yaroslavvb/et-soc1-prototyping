# MM1-v2: the tables (desk; error = forecast / measured - 1, rms % (bias %) and n)

## 1. MM1-v1 and MM1-v0 on E208, UNREAD (unchanged; every committed run with a time figure)

| model | card | cycles an op, wall | cycles an op, the counter's mean | seconds a GEMM | W = J over idle given t (>= 3 W) | J over idle, seconds forecast (>= 3 W) | J at rest given t | J at rest, seconds forecast | W under 3 W (W rms) |
|---|---|---|---|---|---|---|---|---|---|
| MM1-v1 | all | 7.59 (-1.89) n=401 | 9.05 (-3.34) n=401 | 7.59 (-1.89) n=401 | 9.57 (+3.07) n=278 | 9.42 (+1.97) n=278 | 2.0 (+0.31) n=296 | 5.85 (-1.9) n=296 | 0.291 |
| MM1-v1 | aifoundry2 card 0 | 8.92 (-0.79) n=160 | 10.03 (-1.89) n=160 | 8.92 (-0.79) n=160 | 4.71 (-0.1) n=120 | 5.74 (-1.2) n=120 | 1.98 (+0.14) n=120 | 6.26 (-1.59) n=120 | - |
| MM1-v1 | aifoundry1 card 1 | 6.29 (-2.89) n=195 | 8.44 (-4.82) n=195 | 6.29 (-2.89) n=195 | 12.0 (+5.47) n=158 | 11.44 (+4.38) n=158 | 2.02 (+0.42) n=176 | 5.55 (-2.11) n=176 | 0.291 |
| MM1-v1 | aifoundry1 card 0 | 7.56 (-1.49) n=46 | 7.88 (-2.11) n=46 | 7.56 (-1.49) n=46 | NOT FORECAST | NOT FORECAST | NOT FORECAST | NOT FORECAST | - |
| MM1-v0 | all | 9.39 (-3.7) n=401 | 9.32 (-4.54) n=401 | 9.39 (-3.7) n=401 | 11.39 (+3.43) n=278 | 10.87 (+1.37) n=278 | 2.11 (+0.2) n=296 | 7.51 (-3.11) n=296 | 0.321 |
| MM1-v0 | aifoundry2 card 0 | 9.45 (-3.22) n=160 | 9.34 (-3.74) n=160 | 9.45 (-3.22) n=160 | 4.25 (-1.03) n=120 | 6.95 (-2.92) n=120 | 1.8 (-0.32) n=120 | 7.66 (-3.4) n=120 | - |
| MM1-v0 | aifoundry1 card 1 | 9.47 (-4.04) n=195 | 9.41 (-5.29) n=195 | 9.47 (-4.04) n=195 | 14.65 (+6.82) n=158 | 13.08 (+4.63) n=158 | 2.3 (+0.55) n=176 | 7.41 (-2.92) n=176 | 0.321 |
| MM1-v0 | aifoundry1 card 0 | 8.86 (-3.91) n=46 | 8.82 (-4.14) n=46 | 8.86 (-3.91) n=46 | NOT FORECAST | NOT FORECAST | NOT FORECAST | NOT FORECAST | - |

aifoundry1 card 0, borrowed footing (aifoundry2's card terms; not a forecast of either model): v1_borrowed: W|t 6.28 (+3.85) n=39; v0_borrowed: W|t 5.55 (+2.96) n=39

## 2. Held out, the same points and folds for v2 and for MM1-v1's form refitted (cold starts; every constant refitted per fold)

| quantity | v2 | v1 form refitted | v2 without F2 | v2 with one chi |
|---|---|---|---|---|
| cycles (wall), in sample | 4.11 (-0.3) n=1072 | 4.43 (-0.32) n=1072 | 4.36 (-0.32) n=1072 | 4.18 (-0.31) n=1072 |
| cycles, LOEO all | 5.41 (-0.09) n=1072 | 5.7 (-0.22) n=1072 | 5.55 (-0.18) n=1072 | 5.56 (-0.13) n=1072 |
| cycles, LOEO the 888 pre-E208 points | 4.77 (+0.2) n=888 | 5.07 (+0.1) n=888 | 4.96 (+0.09) n=888 | 4.89 (+0.22) n=888 |
| cycles, LOEO E208 (its fold) | 7.77 (-1.48) n=184 | 8.05 (-1.79) n=184 | 7.77 (-1.48) n=184 | 8.05 (-1.79) n=184 |
| cycles, LOEO E206 (its fold) | 6.0 (+0.57) n=119 | 7.41 (-0.17) n=119 | 7.1 (-0.32) n=119 | 6.36 (+0.72) n=119 |
| cycles, LOEO subsets | 7.87 (+3.41) n=37 | 10.62 (+1.48) n=37 | 8.73 (+2.5) n=37 | 9.92 (+2.39) n=37 |
| cycles, LOCO all | 5.5 (+1.41) n=1072 | 5.37 (+0.87) n=1072 | 5.34 (+0.95) n=1072 | 5.65 (+1.38) n=1072 |
| cycles, LOCO aifoundry3 card 0 | 4.46 (+0.7) n=385 | 4.95 (+0.44) n=385 | 4.94 (+0.43) n=385 | 4.48 (+0.71) n=385 |
| cycles, LOCO aifoundry1 card 1 | 4.98 (-1.67) n=92 | 5.83 (-2.47) n=92 | 5.49 (-2.06) n=92 | 5.36 (-2.08) n=92 |
| cycles, LOCO aifoundry2 card 0 | 6.21 (+2.65) n=557 | 5.5 (+1.88) n=557 | 5.52 (+1.97) n=557 | 6.4 (+2.65) n=557 |
| cycles, LOCO aifoundry1 card 0 | 5.24 (-2.12) n=38 | 6.19 (-1.46) n=38 | 6.19 (-1.55) n=38 | 5.24 (-2.03) n=38 |
| cycles, LOEO by experiment | E105 2.61; E107 4.0; E119 4.12; E126 4.05; E136 3.49; E146 4.76; E158 5.19; E159 4.54; E168 2.26; E169 7.08; E190 6.15; E206 6.0; E208 7.77 | E105 2.62; E107 4.27; E119 3.94; E126 4.19; E136 3.58; E146 4.64; E158 5.2; E159 4.67; E168 2.26; E169 7.05; E190 6.16; E206 7.41; E208 8.05 | | |

| energy (same points: those v1's form prices) | v2 | v1 form refitted |
|---|---|---|
| in, W = J over idle given t (>= 3 W), all | 5.13 (-0.41) n=922 | 5.15 (-0.42) n=922 |
| in, W = J over idle given t (>= 3 W), E208 aifoundry2 card 0 | 5.06 (-0.72) n=52 | 5.05 (-0.67) n=52 |
| in, W = J over idle given t (>= 3 W), E208 aifoundry1 card 1 | 6.1 (-2.27) n=59 | 6.27 (-2.09) n=59 |
| in, W = J over idle given t (>= 3 W), E208 aifoundry1 card 0 | 4.28 (+0.53) n=32 | 4.94 (+0.37) n=32 |
| in, W = J over idle given t (>= 3 W), aifoundry3 card 0 | 5.52 (-0.32) n=300 | 5.49 (-0.4) n=300 |
| in, J over idle t forecast (>= 3 W), all | 5.89 (-0.46) n=922 | 5.89 (-0.47) n=922 |
| in, J over idle t forecast (>= 3 W), E208 aifoundry2 card 0 | 5.65 (-1.35) n=52 | 5.6 (-1.35) n=52 |
| in, J over idle t forecast (>= 3 W), E208 aifoundry1 card 1 | 6.6 (-2.77) n=59 | 6.67 (-2.75) n=59 |
| in, J over idle t forecast (>= 3 W), E208 aifoundry1 card 0 | 5.21 (-0.31) n=32 | 5.77 (-0.11) n=32 |
| in, J over idle t forecast (>= 3 W), aifoundry3 card 0 | 5.98 (-0.28) n=300 | 5.99 (-0.38) n=300 |
| in, J at rest given t, all | 1.82 (-0.15) n=940 | 1.83 (-0.15) n=940 |
| in, J at rest given t, E208 aifoundry2 card 0 | 2.15 (-0.01) n=52 | 2.14 (+0.01) n=52 |
| in, J at rest given t, E208 aifoundry1 card 1 | 2.04 (-1.03) n=65 | 2.07 (-1.01) n=65 |
| in, J at rest given t, E208 aifoundry1 card 0 | 1.62 (+0.14) n=32 | 1.94 (+0.07) n=32 |
| in, J at rest given t, aifoundry3 card 0 | 1.44 (-0.07) n=312 | 1.43 (-0.11) n=312 |
| in, J at rest t forecast, all | 4.15 (-0.3) n=940 | 4.28 (-0.32) n=940 |
| in, J at rest t forecast, E208 aifoundry2 card 0 | 4.26 (-1.1) n=52 | 4.8 (-1.1) n=52 |
| in, J at rest t forecast, E208 aifoundry1 card 1 | 4.64 (-2.35) n=65 | 5.14 (-2.89) n=65 |
| in, J at rest t forecast, E208 aifoundry1 card 0 | 4.41 (-1.2) n=32 | 5.08 (-0.72) n=32 |
| in, J at rest t forecast, aifoundry3 card 0 | 3.55 (-0.0) n=312 | 3.74 (-0.07) n=312 |
| LOEO, W = J over idle given t (>= 3 W), all | 6.59 (+0.68) n=922 | 6.55 (+0.65) n=922 |
| LOEO, W = J over idle given t (>= 3 W), E208 aifoundry2 card 0 | 4.82 (-0.7) n=52 | 4.81 (-0.69) n=52 |
| LOEO, W = J over idle given t (>= 3 W), E208 aifoundry1 card 1 | 12.63 (+5.56) n=59 | 12.72 (+5.6) n=59 |
| LOEO, W = J over idle given t (>= 3 W), E208 aifoundry1 card 0 | 6.99 (+4.83) n=32 | 6.95 (+4.77) n=32 |
| LOEO, W = J over idle given t (>= 3 W), aifoundry3 card 0 | 7.05 (+1.02) n=300 | 7.04 (+0.95) n=300 |
| LOEO, J over idle t forecast (>= 3 W), all | 7.35 (+0.61) n=922 | 7.35 (+0.56) n=922 |
| LOEO, J over idle t forecast (>= 3 W), E208 aifoundry2 card 0 | 5.94 (-1.5) n=52 | 6.0 (-1.88) n=52 |
| LOEO, J over idle t forecast (>= 3 W), E208 aifoundry1 card 1 | 12.15 (+4.47) n=59 | 12.24 (+4.49) n=59 |
| LOEO, J over idle t forecast (>= 3 W), E208 aifoundry1 card 0 | 8.1 (+4.0) n=32 | 8.07 (+3.93) n=32 |
| LOEO, J over idle t forecast (>= 3 W), aifoundry3 card 0 | 7.75 (+1.14) n=300 | 7.85 (+1.04) n=300 |
| LOEO, J at rest given t, all | 2.03 (+0.08) n=940 | 1.98 (+0.07) n=940 |
| LOEO, J at rest given t, E208 aifoundry2 card 0 | 2.02 (-0.1) n=52 | 2.0 (-0.1) n=52 |
| LOEO, J at rest given t, E208 aifoundry1 card 1 | 2.13 (+0.33) n=65 | 2.14 (+0.33) n=65 |
| LOEO, J at rest given t, E208 aifoundry1 card 0 | 2.61 (+1.8) n=32 | 2.59 (+1.77) n=32 |
| LOEO, J at rest given t, aifoundry3 card 0 | 1.73 (+0.18) n=312 | 1.69 (+0.12) n=312 |
| LOEO, J at rest t forecast, all | 5.05 (+0.07) n=940 | 5.25 (-0.05) n=940 |
| LOEO, J at rest t forecast, E208 aifoundry2 card 0 | 6.31 (-1.47) n=52 | 6.7 (-1.96) n=52 |
| LOEO, J at rest t forecast, E208 aifoundry1 card 1 | 5.27 (-1.85) n=65 | 5.76 (-2.22) n=65 |
| LOEO, J at rest t forecast, E208 aifoundry1 card 0 | 7.37 (+0.64) n=32 | 7.37 (+0.61) n=32 |
| LOEO, J at rest t forecast, aifoundry3 card 0 | 4.78 (+0.81) n=312 | 5.27 (+0.59) n=312 |
| LOCO, W = J over idle given t (>= 3 W), all | 10.13 (-1.29) n=922 | 9.15 (-0.2) n=922 |
| LOCO, W = J over idle given t (>= 3 W), E208 aifoundry2 card 0 | 9.03 (-5.33) n=52 | 7.75 (-3.78) n=52 |
| LOCO, W = J over idle given t (>= 3 W), E208 aifoundry1 card 1 | 13.88 (-12.87) n=59 | 11.4 (-10.45) n=59 |
| LOCO, W = J over idle given t (>= 3 W), E208 aifoundry1 card 0 | 6.17 (+3.59) n=32 | 6.08 (+3.41) n=32 |
| LOCO, W = J over idle given t (>= 3 W), aifoundry3 card 0 | 12.3 (+8.56) n=300 | 11.99 (+8.09) n=300 |
| LOCO, J over idle t forecast (>= 3 W), all | 10.2 (-0.37) n=922 | 9.55 (+0.42) n=922 |
| LOCO, J over idle t forecast (>= 3 W), E208 aifoundry2 card 0 | 9.02 (-5.08) n=52 | 7.86 (-3.6) n=52 |
| LOCO, J over idle t forecast (>= 3 W), E208 aifoundry1 card 1 | 14.49 (-13.32) n=59 | 12.21 (-11.1) n=59 |
| LOCO, J over idle t forecast (>= 3 W), E208 aifoundry1 card 0 | 6.33 (+2.52) n=32 | 6.71 (+2.83) n=32 |
| LOCO, J over idle t forecast (>= 3 W), aifoundry3 card 0 | 12.76 (+8.69) n=300 | 12.55 (+8.22) n=300 |
| LOCO, J at rest given t, all | 3.02 (-0.65) n=940 | 2.58 (-0.36) n=940 |
| LOCO, J at rest given t, E208 aifoundry2 card 0 | 3.29 (-1.75) n=52 | 2.9 (-1.14) n=52 |
| LOCO, J at rest given t, E208 aifoundry1 card 1 | 3.66 (-3.08) n=65 | 3.28 (-2.63) n=65 |
| LOCO, J at rest given t, E208 aifoundry1 card 0 | 2.36 (+1.36) n=32 | 2.32 (+1.28) n=32 |
| LOCO, J at rest given t, aifoundry3 card 0 | 2.9 (+2.0) n=312 | 2.38 (+1.64) n=312 |
| LOCO, J at rest t forecast, all | 5.41 (+0.75) n=940 | 5.16 (+0.52) n=940 |
| LOCO, J at rest t forecast, E208 aifoundry2 card 0 | 4.41 (-1.42) n=52 | 5.2 (-0.89) n=52 |
| LOCO, J at rest t forecast, E208 aifoundry1 card 1 | 6.51 (-4.84) n=65 | 6.9 (-5.09) n=65 |
| LOCO, J at rest t forecast, E208 aifoundry1 card 0 | 4.45 (-0.18) n=32 | 5.42 (+0.39) n=32 |
| LOCO, J at rest t forecast, aifoundry3 card 0 | 5.28 (+2.76) n=312 | 5.21 (+2.22) n=312 |
| ones (v2 only; v1's form has no ones price), LOCO W given t | 7.71 (-4.34) n=24 | NOT FORECAST |

Counter's mean on E208 (v2's wall / its rho): v2_in 4.81 (-2.16) n=184; v2_loeo 7.88 (-2.14) n=184; v2_loco 4.84 (-1.69) n=184

### The fold fits (fix-mm1v2): the pin rule, every start converged, the lowest training cost kept

- pin rule (constant: the experiment that alone identifies it; pinned at 0 in a fold without it): {'F2': 'E208', 'chi3': 'E208', 'chiF': 'E206'}; 6 cold starts a fold
- v2: pinned folds LOCO aifoundry3 card 0 {'chiF': 0.0}; LOEO E206 {'chiF': 0.0}; LOEO E208 {'F2': 0.0, 'chi3': 0.0}; largest held-out spread among the starts at the best cost 0.01 pt; folds whose starts end at different training costs (cost -> held-out rms): LOCO aifoundry2 card 0: cost 0.3310 -> 6.21%, cost 0.3471 -> 5.17/5.18%; LOEO E169: cost 0.7790 -> 7.08%, cost 0.8031 -> 8.47%; all-data fit frozen cost 0.90566 (in sample 4.111%) against converged 0.905657 (4.111%)
- v1form: pinned folds none; largest held-out spread among the starts at the best cost 0.0 pt; folds whose starts end at different training costs (cost -> held-out rms): LOEO E169: cost 0.9242 -> 7.05%, cost 0.9487 -> 8.62%; all-data fit frozen cost 1.050208 (in sample 4.426%) against converged 1.050208 (4.426%)
- v2_noF2: pinned folds LOCO aifoundry3 card 0 {'chiF': 0.0}; LOEO E206 {'chiF': 0.0}; LOEO E208 {'chi3': 0.0}; largest held-out spread among the starts at the best cost 0.0 pt; folds whose starts end at different training costs (cost -> held-out rms): LOEO E169: cost 0.8937 -> 7.06%, cost 0.9184 -> 8.49%; all-data fit frozen cost 1.020201 (in sample 4.363%) against converged 1.020201 (4.363%)
- v2_onechi: pinned folds LOEO E208 {'F2': 0.0}; largest held-out spread among the starts at the best cost 0.0 pt; folds whose starts end at different training costs (cost -> held-out rms): LOCO aifoundry1 card 1: cost 0.8195 -> 5.36%, cost 0.8196 -> 5.36/5.37%; LOCO aifoundry2 card 0: cost 0.3463 -> 6.4%, cost 0.3696 -> 5.16%; LOEO E169: cost 0.8095 -> 7.06%, cost 0.8337 -> 8.6%; all-data fit frozen cost 0.935784 (in sample 4.178%) against converged 0.935784 (4.178%)
- v2 profile LOCO aifoundry3 card 0 | chiF: chiF over [-0.6, -0.3, 0.0, 0.3, 0.6, 0.9]: training cost 0.664885-0.664885; held out 3.94-7.95%, its subsets 6.0-36.69%
- v2 profile LOEO E206 | chiF: chiF over [-0.6, -0.3, 0.0, 0.3, 0.6, 0.9]: training cost 0.787849-0.787862; held out 4.6-13.0%, its subsets 5.84-35.92%
- v2 profile LOEO E208 | F2: F2 over [0.0, 150.0, 300.0, 450.0]: training cost 0.646818-0.73458; held out 6.66-7.77%, its subsets 1.26-1.38%
- v2 profile LOEO E208 | chi3: chi3 over [-0.2, 0.0, 0.1, 0.2, 0.4]: training cost 0.646818-0.646818; held out 7.77-8.68%, its subsets 1.38-11.05%
- E209's v2 forecasts at 799 MHz if the all-data fit were the converged refit (a record; the frozen fit stays): cycles 0.0127% rms (max 0.0476%), W over idle 0.0056% rms (max 0.0134%) on 45 / 45 points
- LOEO cases that recur in another experiment (that experiment trains in the fold): E206 11; E208 12 (one point a card and case; LOCO holds every case of its card out)

## 3. The governor clock model (post hoc, E208 aifoundry2 runs only) and the rest law

- loop on measured powers: t_climb 0.638 s, tau 1.402 s (E64: 1.3 s), P_th 66.61 W (TDP 65 W), k_die 0.1731 C/W; capped 159 of 160; burst mean clock rms 10.77 MHz (bias 0.0)
- the chain (v2's own powers into the loop; the clock-forecast route): P_th 63.3 W; capped 157 of 160; burst mean clock rms 11.15 MHz (bias -0.22)
- rest law aifoundry1 card 0: a line through E208 a1c0-S1 rests against the start die (45 runs; post hoc); T0 forecast 50.0 C; on E208's rests {'mean_W': 0.0, 'n': 45, 'rms_W': 0.081}
- rest law aifoundry1 card 1: ledger v2 frozen idle law aifoundry1-c1 (footing law): docs/reports/data/2026-11-05-q145a-; T0 forecast 55.0 C; on E208's rests {'mean_W': 0.277, 'n': 195, 'rms_W': 0.312}
- rest law aifoundry2 card 0: ledger v2 frozen idle law aifoundry2 (footing law): docs/reports/data/2026-11-05-q145a-foo; T0 forecast 51.0 C; on E208's rests {'mean_W': 0.135, 'n': 137, 'rms_W': 0.179}
- rest law aifoundry3 card 0: ledger v2 frozen idle law aifoundry3 (footing law): docs/reports/data/2026-11-05-q145a-foo; T0 forecast 54.4 C; on E208's rests None
- base rate: 19 of 160 runs measured capped, so 'never capped' agrees on 141; the loop agrees on 159 on measured powers and 157 in the chain; misses on measured powers: E208|a2c0-S2|052-1x1x1-int8-ones (capped True, 800 MHz share 0.75, launch power 41.77 W, die max 54 C); in the chain: E208|a2c0-S1|017-1x1x10-fp32-rnd (capped True, v2's power 64.28 W against 70.23 W); E208|a2c0-S2|052-1x1x1-int8-ones (capped True, v2's power 40.85 W against 41.77 W); E208|a2c0-S2|068-1x1x10-fp32-rnd (capped True, v2's power 64.43 W against 69.5 W); out of sample: NOT RUN (E190 arm A, E194 and E200 ran on this card under its governor; none was read); the vendored telemetry files (inputs/e208/a2c0-S*__telemetry.jsonl.gz) are read by no script here

## 4. E209 (planning and the predicted gaps between the models; not a score)

- 45 points (distinct cases), 55 runs planned; card-minutes: {'E208 forms (burst 23 s, three-process 70 s a run, gates included, as E208 a2c0-S1 averaged)': 22.6, 'every run three processes (70 s a run)': 64.2, 'plus the anchor (E208 4x8x8-int8-rnd), the smoke and the opening rest': 'about 5'}
- predicted rms |ln| gaps on the same points: {'cycles v1/v2': (4.8, 45), 'cycles F1@800/v2': (17.1, 45), 'W v1/v2': (2.6, 39), 'W F1@800/v2': (56.9, 42), 'W F2@800/v2': (84.9, 42)}
- forecast capped: ['e44']; highest forecast board at the top point 67.2 W; die at most 58.6 C (6 s burst), 64.2 C (three processes, desk); stops 85 W x3 / 80 C
- the clock routes: forecast win-view clock {'799.0': 45} (MHz: points); so with the clock forecast every point's cycles, seconds and W are the 799.0 MHz column, as given a measured 799.0 MHz; the routes part only in the capped flag (['e44']) and the burst means
- E208 measured on this card (the planning bound; vendored checks, C5): a2c0-S1 board max 71.81 W, die max 59 C, hottest-sensor latch [61, 62] C; a2c0-S2 board max 71.86 W, die max 60 C, hottest-sensor latch [62, 62] C
