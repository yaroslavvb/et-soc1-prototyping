# decl-e217: the lab's BLIND test of its frozen matmul models on E217, DECLARED before any E217 datum exists

*Declared Thu 19 Nov 2026 11:35:59 PST, round Q228, at the desk on aifoundry2 (work copy of GitHub main 8bde0182). Python: /usr/bin/python3 3.12.3, numpy 1.26.4, single-threaded in slot.sh. Nothing here was measured. E217 (the model session's fourth matmul sweep, 1119-mmsweep4, Discussion #13, named E217 in #13.1) has not run: no E217 datum exists.*

**Label: BLIND.** BLIND: MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2 (3ca4b717), the contention term F1 (#1.29.1), verify-lay's controls (#1.29.1.1) and the gemmLnc term (#1.29) frozen and unchanged, this declaration and the nominal forecasts hashed and frozen (FROZEN.txt, posted by the orchestrator) before any E217 datum exists. A session whose first datum precedes the freeze post is UNREAD for it.

State at this declaration: out/orch/e217-releases.txt holds 2 post lines (no E217 claim, session or datum on record: only the proposal (#13) and the naming (#13.1)); claim files: none; the aifoundry2 quiet-desk flag absent.

## a. The runs
- **599 runs** ({'anchor': 55, 'arm': 544}) in E217's seven sessions ({'a1c0-S1': 86, 'a1c0-S2': 85, 'a1c0-S3': 83, 'a1c1-S1': 87, 'a1c1-S2': 83, 'a1c1-S3': 90, 'a1c1-S4': 85}), 332 arms, **486 cases**; by card {'aifoundry1 card 0': 254, 'aifoundry1 card 1': 345} runs, {'aifoundry1 card 0': 219, 'aifoundry1 card 1': 267} cases; by format {'fp16': 125, 'fp32': 265, 'int8': 209}.
- Source: the registered kit: the orchestrator's copy of EE/src (out/orch/e217-src, SRC-SHA256SUMS.txt 854bd075..., copied 11:12:05 PST): src/sched/<card>-<S>.json (each run's i, block, role, arm, values, shires, type, form) and src/arms.json; nulls left out; no measurement. Run id: E217|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py: f"{i:03d}-{arm}"). The ids are in `DECLARED-blind-e217.json` (a_runs.run_ids, a_runs.cases).
- Time selection: as MM1-v3.1's own loader data_v31.mms_runs_all (= data_v3.mms_runs), unread-e214's: the session's queue says ran, rc 0, check exact or approx; role not null; values gemmL<MB>x<NB>x<KB>: and shires present; the primary view (band600 on card 1, win on card 0: reduce_mms.py) has T_op_us, cyc_op_max and n_launch >= 1.
- Energy selection: the same, and the primary view's dP_w is not None, its p_mean_w truthy, the run not capped and its role not 'time' (data_v31.mms_runs_all's energy condition).
- A listed run that does not run (a session cut short or not run) is no data: never imputed, never re-listed.
- Case: (card, arm gemmL<MB>x<NB>x<KB>, format, kind as the arm spells it, mask) over all of that card's sessions; anchors (4x8x8 int8 random, full chip) are cases like any other.
- Groups (from arms.json alone):
  - **X1**: the 1x1x1 cells: 105 cases (every format and mask), reported apart
  - **MG**: the new core-group masks: the plan's tag 'P1-sim' (arms.json families), 48 cases, 1x1x1 fp32 and fp16, 12 masks a card: card 1 ['0x1f', '0x22', '0x3', '0x33333333', '0x55555555', '0x5a5a5a5a', '0x7fffffff', '0x80000000', '0xf0f0f0f0', '0xffff0000', '0xfffff', '0xffffff'], card 0 ['0x1f', '0x22', '0x3', '0x33333333', '0x55555555', '0x5a5a5a5a', '0x80000000', '0xf0f0f0f0', '0xffff0000', '0xfffff', '0xffffff', '0xfffffff']; reported apart
  - **SUB**: the other subset masks: 148 cases
  - **FULL**: the full chip: 290 cases
  - **S**: the operand-pattern arms of E217's 21 new tile kinds (no committed count; the prior-tile scan): 35 cases, 63 runs: ['pattern:gt125', 'pattern:gt25', 'pattern:gt875', 'pattern:h_gt25', 'pattern:h_rt32', 'pattern:h_rt64', 'pattern:h_sg', 'pattern:h_th_in', 'pattern:i8_t06', 'pattern:i8_t1', 'pattern:i8_t2', 'pattern:i8_t3', 'pattern:i8_t46', 'pattern:i8_t5', 'pattern:rt16', 'pattern:rt32', 'pattern:rt32b', 'pattern:rt64', 'pattern:sg_kk', 'pattern:sgm1', 'pattern:th_top']
  - **C**: the sparse50 pools (pattern:sparse50f / h / i, byte-equal to E214's pools): 18 cases, 19 runs, priced as the committed sparse50 kind
  - **K**: the lab's kinds (zeros, ones, random): 433 cases

| card | shape | mask group | cases |
|---|---|---|---|
| aifoundry1 card 0 | 1x1x1 | FULL | 1 |
| aifoundry1 card 0 | 1x1x1 | MG | 24 |
| aifoundry1 card 0 | 1x1x1 | SUB | 19 |
| aifoundry1 card 0 | other | FULL | 120 |
| aifoundry1 card 0 | other | SUB | 55 |
| aifoundry1 card 1 | 1x1x1 | FULL | 30 |
| aifoundry1 card 1 | 1x1x1 | MG | 24 |
| aifoundry1 card 1 | 1x1x1 | SUB | 7 |
| aifoundry1 card 1 | other | FULL | 139 |
| aifoundry1 card 1 | other | SUB | 67 |

- **Fit inclusion:** NO E217 point can be in any fit: E217 has no datum (no session has run; e217-releases.txt holds the proposal and the naming only). Checked all the same: no E217 token in any model's inputs or loaders (MM1-v3.1 28 files, MM1-v3 115, MM1-v2 86: 0 hits) and no E217 id in any landed point record (MM1-v3.1 E105-E213; MM1-v3 to E212; MM1-v2 to E208).

## b. The quantities
- **per_card**: aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz)
- **T1_wall**: cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1
- **T2_counter_mean**: the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1
- **T3_seconds**: seconds a GEMM: ops x T_forecast(us) x 1e-6 / t_pass_s - 1 (ops = 64 MB NB KB a minion); at the measured clock T3's error equals T1's identically (the reducer's T_op_us = wall / ops): both printed
- **E1_J_over_idle_given_t**: W over idle at the measured op time: W = A + B / t_meas (the predictor's W_affine at the run's conditions) against the primary view's dP_w; relative (= J over idle given t) when the case's mean MM1-v3.1 W given t and its mean measured dP_w are both 3 W or more; else a WATTS case, scored by the mean of its runs' W - dP_w in watts (E215's form; the watts set fixed by MM1-v3.1 and the measurement, the same for every model)
- **E2_J_over_idle_t_forecast**: (W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc the W over idle at the model's own op time T_fc; at a watts case W_fc - dP_w
- **E3_J_at_rest_given_t**: (P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run's rest, measured, given)
- **E4_J_at_rest_t_forecast**: (P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1
- **split**: per card; per format and kind; the 1x1x1 cells (X1) and the new core-group masks (MG) apart (also SUB, FULL); groups S, C, K; configuration twins apart

## The models
- **MM1-v3.1**: tools/matmul/mm1/v3.1 (landed 2c971828): mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel 'rgm136', V, t0_c}])
- **MM1-v3**: tools/matmul/mm1/v3 (landed b1493082): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=, t0_c=)
- **MM1-v2**: tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's unread_v2_e212.call (its pins and SHA256SUMS checked): card 1 V None (the 0.517 V footing), card 0 the measured volts; energy for random, zeros and ones only (any other kind NOT FORECAST in energy); no die term
- **v3.1+contention**: form F1 (#1.29.1, frozen 09:31:34 PST Thu 19 Nov): T = T_v3.1 x clip(1 + a Phi_fresh, 0.3, 3.0), a = -0.08316593007433395 (forecast-e215-v31-layout.json meta), Phi_fresh by the term's eval_layout.phi_of over the masked walk's features (features_layout.walk_feats + mesh_feats, unchanged; the frozen cache's entries as frozen, the rest made by the same code from the arms alone in step 2w); 0 at the full mask, so the factor is exactly 1 there; energy MM1-v3.1's affine at its own op time (given t: MM1-v3.1's exactly)
- **v3.1+gemmLnc**: term F3 (#1.29): NOT APPLICABLE: E217 runs no gemmLnc arm (0 of 332 arms; rgm136 gemmL only), so it equals MM1-v3.1 on every E217 case; not scored
- **v3.1+both**: the composition declared in reg-e216 (the candidate MM1-v3.2): time = MM1-v3.1's x the contention factor; W at a measured t = A + (B + dW t_op,v3.1) / t with the gemmLnc term's dW, 0 on every E217 case: so it equals 'v3.1+contention' on every E217 case (computed by the composition, compared nowhere separately)
- **controls**: verify-lay's controls (#1.29.1.1), by v02_fits.py's forms unchanged with its all-data constants (work/verify-lay/v02_fits.json): N1+N2 (N1 = 1 - n/32, N2 = N1^2; a = [-0.09348958586302018, 0.11765730189141044]); G1 (hop mean: (110 + 12 h)/(110 + 12 h_full) - 1; a = [0.30314251932286107]); G1+N1 (a = [0.6022127706566506, -0.021675728290377668]); the layout-blind F1 (fresh32_bar_narm: Phi_fresh averaged over the configurations of the same (n shires, arm): here over E217's listed configurations of both cards, as v02_fits.py averages over the fit's points of the same (n, arm); a = [-0.17556875184106632]); factor 1 + sum a_i x_i (unclipped, as v02's E215 control columns), 1 at the full mask; time MM1-v3.1's x the factor, energy MM1-v3.1's affine at its own op time. The features from the term's walk features (verify-lay re-derived them, 148/148); step 2 re-makes v02_e215_controls.csv's N3, N1+N2, G1, G1+N1 columns first

## The forecast procedure
- **footing_1_measured**: THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's start-of-run records only, MM1-v3 README section 5's form as unread-e214 did: the primary view's kernel clock kclock_mhz; minion volts: card 1 the models' footing 0.517 V, card 0 the primary view's rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). The terms and controls on MM1-v3.1's forecast at the same conditions; the layout features are configuration-only (made at step 2w).
- **fields_read_before_scoring**: from each committed E217 data JSON ONLY: the top-level card, session and primary_view, and per run: run, i, ran, role, arm, values, type, shires, minions, die_start_c, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read until the forecasts at those conditions are hashed.
- **footing_2_nominal**: the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED beside the primary footing)
- **counts_as_inputs**: the switch counts are inputs, never fitted: MM1-v3.1's tables (MM1-v3's rows + counts 3e8991d0); counts-e214's land (4c39d0d3; E217 reuses none of its 20 tiles: none added); counts-e217 for E217's 21 new kinds, made in step 4 from the tile files alone (rtl-sim/fma_toggle_v2, Verilator 5.042, counts-e214's form) and frozen (COUNTS-FROZEN.txt) before any E217 measurement is read; added in memory to each model's tables by its own loop (no key colliding: asserted), unread-e214's form
- **order**: 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt -> 4 counts-e217 -> COUNTS-FROZEN.txt; then, after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores

## c. The metric
- **error**: forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W
- **case**: a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside
- **twins**: per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in that model's TRAINING time configurations (its landed out/points_time_*.csv, E146 store rungs out); an energy case when that key and its energy kind are in its energy configurations (work/step1/twin-keys.json, 3418b7d8, equal to unread-e214's). The no-twin cases carry the pass rule and the headline; twins and all cases printed beside. At the nominal clocks: MM1-v3.1 63 time-twin and 24 energy-twin cases of 486 (a preview; the measured clock decides)

## d. The comparisons
- **test**: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none
- **d**: per case, d = |ln(1 + e_B)| - |ln(1 + e_A)| for the pair (A vs B) (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both price (twins included); REPORTED beside over the cases that are twins for neither
- **ties_how**: E215's rule (rules_e215.ties_of), unread-e214's values: card 1 E215 arm B's registered ties; card 0 from E212 a1c0-S1/S2's pooled within-case spread (bands.json card0_floors)
- **D1_v31_vs_v3**: MM1-v3.1 vs MM1-v3 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled
- **D2_v31_vs_v2**: MM1-v3.1 vs MM1-v2 on H1-H5: per card and pooled
- **D3_layout**: on the subset-mask cases (MG and SUB), per card and pooled: 'v3.1+contention' vs MM1-v3.1, and each control (N1+N2, G1, G1+N1, the layout-blind F1) vs MM1-v3.1, on H1 (wall) and H2 (counter mean); the MG cases alone and 'v3.1+contention' vs each control REPORTED beside; H5 (J over idle with t forecast) REPORTED
- **D4_switch**: on group S: MM1-v3.1 with counts-e217 vs the null N, Q1 and Q2 (section e): part S's P2 and P4
- **verdicts**: each comparison is a verdict of its own, never part of PASS
- ties: card 1 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.1}; card 0 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.15}

## e. The switch-pattern arms: the counts, phi and the gate
- **counts**: counts-e217 (step 4): the 21 new kinds, fp32 10 (gt125, gt25, gt875, rt16, rt32, rt32b, rt64, sg_kk, sgm1, th_top) at the GEMM states S1 and S2, fp16 5 (h_gt25, h_rt32, h_rt64, h_sg, h_th_in) and int8 6 (i8_t06, i8_t1, i8_t2, i8_t3, i8_t46, i8_t5) at the launch points, exactly as counts-e214 (its scripts, its rules: a pool of fewer than 3 files measured at every file; two committed points re-counted first and matched); then MM1-v3.1: counts-e217's rows added to energy_v31's E210C31 / SWT31, MM1-v3: 3e8991d0's and counts-e217's to energy_v3's E210C / SWT (unread-e214's loop). A kind whose count cannot be made is NOT FORECAST in energy.
- **phi_how**: MM1-v3's own kinds_v3.phi(fmt, {'tiles': [file]}) over each new kind's registered tile file (sha256 checked against arms.json); sparse50f/h/i: MM1-v3's phi_of('sparse50')
- **gate**: DECLARED (before any datum, from the tile files alone): the fp32 tiles gt125, gt25, gt875 and the fp16 tile h_gt25 hold all-zero A rows (13, 10, 2 and 12 of 16), B none: their float gate is the arow form at the tile's own all-zero-row share, (g_op, g_lane, g8) = (share, 0, 0) - E210's arow50 (0.5, 0, 0) and E214's sp_ar4 declaration (unread-e214) - in MM1-v3.1's and MM1-v3's gate_shares; every other new float kind has no zero element: (0, 0, 0), the frozen code's literal; int8 kinds the frozen code's own 1 - v (v the count's valid share). The literal (0, 0, 0) for the four zero-row tiles REPORTED beside; the count's valid share REPORTED beside each declared share.
- **sparse50**: pattern:sparse50f / h / i priced as the committed sparse50 kind (data_v31.SPARSE_GEN plus sparse50h, unread-e214's alias); group C REPORTED
- **Q1**: group S, W over idle given t: MM1-v3.1 + the counts against the null N = the mean over zeros, ones and random of the run's format of the same model's own W given t at the run's conditions (the same base; only the count's information differs); cases with dP_w >= 3 W
- **Q2**: group S, E210's metric, the share of D: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, D = W_R - W_Z measured, R and Z the random and zeros cases of the same card, arm, format and mask (measured means; W_fc(R) the same model's W given t, its runs' mean); for the null [(N(P) - W_fc(R)) - (W_P - W_R)] / D; cases with an R and a Z case and D > 0
- **N2_REPORTED**: the null over ones and random only
- **MM1-v3_REPORTED**: the same with MM1-v3 + the counts

| kind | phi | tile | sha256 |
|---|---|---|---|
| fp16|pattern:h_gt25 | 0.321810 | `src/tiles/fp16/h_gt25.bin` | `6e15628cdb6beeca...` |
| fp16|pattern:h_rt32 | 0.486664 | `src/tiles/fp16/h_rt32.bin` | `9607b25e400b2ab8...` |
| fp16|pattern:h_rt64 | 0.471917 | `src/tiles/fp16/h_rt64.bin` | `50e5637d5f077319...` |
| fp16|pattern:h_sg | 0.430045 | `src/tiles/fp16/h_sg.bin` | `965c64ea81ccd16b...` |
| fp16|pattern:h_th_in | 1.040170 | `src/tiles/fp16/h_th_in.bin` | `c5da4e977eb04257...` |
| fp32|pattern:gt125 | 0.231665 | `src/tiles/fp32/gt125.bin` | `add855892135e8f6...` |
| fp32|pattern:gt25 | 0.235582 | `src/tiles/fp32/gt25.bin` | `d3de0d95483b133e...` |
| fp32|pattern:gt875 | 0.252703 | `src/tiles/fp32/gt875.bin` | `341677173eeb9e6c...` |
| fp32|pattern:rt16 | 0.364650 | `src/tiles/fp32/rt16.bin` | `abbad7330e404324...` |
| fp32|pattern:rt32 | 0.360859 | `src/tiles/fp32/rt32.bin` | `fc8caea95c621963...` |
| fp32|pattern:rt32b | 0.507427 | `src/tiles/fp32/rt32b.bin` | `bdbc6639bb87c858...` |
| fp32|pattern:rt64 | 0.360859 | `src/tiles/fp32/rt64.bin` | `928aa1ef5b5c0b67...` |
| fp32|pattern:sg_kk | 0.354668 | `src/tiles/fp32/sg_kk.bin` | `e0952b532b80d25b...` |
| fp32|pattern:sgm1 | 0.335336 | `src/tiles/fp32/sgm1.bin` | `dbc41d348fdd25f8...` |
| fp32|pattern:th_top | 1.037092 | `src/tiles/fp32/th_top.bin` | `308543e0d82c25f4...` |
| int8|pattern:i8_t06 | 0.341920 | `src/tiles/int8/i8_t06.bin` | `cc49c60f40e82b4b...` |
| int8|pattern:i8_t1 | 0.334135 | `src/tiles/int8/i8_t1.bin` | `7af3a6bf714bb718...` |
| int8|pattern:i8_t2 | 0.317293 | `src/tiles/int8/i8_t2.bin` | `12ad94464d5b8897...` |
| int8|pattern:i8_t3 | 0.309116 | `src/tiles/int8/i8_t3.bin` | `04a63898ad0d9bb6...` |
| int8|pattern:i8_t46 | 1.099807 | `src/tiles/int8/i8_t46.bin` | `9b653ebd5100aebe...` |
| int8|pattern:i8_t5 | 0.352459 | `src/tiles/int8/i8_t5.bin` | `5454785ce4a188e2...` |

| zero-row tile | declared gate (g_op, g_lane, g8) | all-zero A rows of 16 | A zero share | B zero share |
|---|---|---|---|---|
| fp32|pattern:gt125 | (0.8125, 0, 0) | 13 | 0.8750 | 0.0000 |
| fp32|pattern:gt25 | (0.6250, 0, 0) | 10 | 0.7500 | 0.0000 |
| fp32|pattern:gt875 | (0.1250, 0, 0) | 2 | 0.1250 | 0.0000 |
| fp16|pattern:h_gt25 | (0.7500, 0, 0) | 12 | 0.7500 | 0.0000 |

## f. The pass rule (decided by a script)
- **Part A:** MM1-v3.1 on the PRIMARY footing by E215's rule form on each card over the NO-TWIN cases: a case passes T1, T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no rule FAILS on either card and at least one rule PASSES; FAILS when any rule fails (named). Printed beside, deciding nothing: X1, MG, SUB, FULL; S, C, K; per format; twins.
- Bands (E215's form (rules_e215.py, unchanged; unread-e214's s01d_bands.py re-run here): 2 x max(B1, B2) rounded up to a whole percent, B1 MM1-v3.1's LOEO no-twin error over every point, B2 over this card's points (holdout_v31.json reproduced first); T3 takes T1's bases; watts band 2 x max(B1 W, B2 W, SD_rep) rounded up to 0.01 W. Card 1's equal E215 arm B's registered bands (checked).):

| card | T1 | T2 | T3 | E1 | E2 | E3 | E4 | watts |
|---|---|---|---|---|---|---|---|---|
| aifoundry1 card 1 | 10% | 13% | 10% | 14% | 14% | 5% | 10% | 0.56 W |
| aifoundry1 card 0 | 11% | 16% | 11% | 11% | 13% | 5% | 10% | 0.56 W |

- aifoundry1 card 1: T1 2 x max(4.723, 4.998) = 10.00 -> 10%; T2 2 x max(6.050, 6.450) = 12.90 -> 13%; T3 2 x max(4.723, 4.998) = 10.00 -> 10%; E1 2 x max(5.476, 6.623) = 13.25 -> 14%; E2 2 x max(6.014, 6.731) = 13.46 -> 14%; E3 2 x max(2.153, 2.321) = 4.64 -> 5%; E4 2 x max(4.473, 4.628) = 9.26 -> 10%; watts 2 x max(0.2794, 0.2607, SD_rep 0.08373) -> 0.56 W
- aifoundry1 card 0: T1 2 x max(4.723, 5.135) = 10.27 -> 11%; T2 2 x max(6.050, 7.523) = 15.05 -> 16%; T3 2 x max(4.723, 5.135) = 10.27 -> 11%; E1 2 x max(5.476, 5.417) = 10.95 -> 11%; E2 2 x max(6.014, 6.153) = 12.31 -> 13%; E3 2 x max(2.153, 1.919) = 4.31 -> 5%; E4 2 x max(4.473, 4.673) = 9.35 -> 10%; watts 2 x max(0.2794, None, SD_rep 0.11509) -> 0.56 W
- **Part S:** Q218's P1-P4 for MM1-v3.1 + counts-e217 against N on group S, pooled over both cards: P1 rms(Q1) < N's; P2 the exact two-sided sign test on d = |e_N| - |e_V| per case, a tie when |d| < 0.01, holds when p < 0.05 and MM1-v3.1 is closer in more; P3 rms(Q2) < N's; P4 P2's test on Q2 (ties |d| < 0.01 of D). PART S PASSES when P1-P4 hold; NOT DECIDED when either sign test has fewer than 6 untied cases or counts-e217 is not frozen before the read; else FAILS (named).
- **Verdict:** PASS when part A and part S pass; FAIL when either fails (named); NOT DECIDED otherwise. Decided by a script: blind-e217's scorer (scripts/s03_score.py of the lane that scores E217), which implements sections a-f of this declaration exactly, is code-tested on a stand-in day built from the frozen forecasts alone, and is hashed (sha256 in its progress log, posted with the result) BEFORE its first read of any E217 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing (section h) is scored by the same script and rules beside, REPORTED, deciding nothing.

## g. The label rule
- **BLIND**: a session is BLIND for this test when this declaration's and the nominal forecasts' sha256 (FROZEN.txt) were posted on the Discussion before the session's first datum (its first card command, the session's own log)
- **UNREAD**: a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the post (data-e217's read times on record); else POST-READ (REPORTED)
- **counts_route**: the switch-route energy of group S takes COUNTS-FROZEN.txt's post time by the same rule, session by session; the nominal footing's group-S energy (made after counts-e217) likewise
- **printed**: every result line names its label, the freeze post time and the session's first card command time

## h. The nominal footing (a second footing, frozen now, scored beside)
- **aifoundry1 card 1**: f 600.0 MHz; V 0.517 V (the models' card-1 footing); die at start 60.0 C (the kit's start-gate ceiling, mms_common.CARDS a1c1)
- **aifoundry1 card 0**: f 800.0 MHz (its planned clock: the kit's main band "800" for the governed card); V the model's own volts at f (0.604 V); die at start 55.0 C (the kit's a1c0 start-gate ceiling)
- **files**: forecasts-nominal-e217.csv and .json: one forecast a case and model (every run of a case at the same nominal conditions)
- **group_S_energy**: NOT FORECAST at the freeze (no count); made by the frozen predictors with counts-e217 after step 4 into forecasts-nominal-e217-counts.csv/.json, listed in COUNTS-FROZEN.txt
- **scored**: by the same rules as the primary footing, beside it, REPORTED

## i. Earlier reads, disclosed
- **E217_data**: none exists at this declaration (no session has run)
- **this_lane**: read the kit copy's arms.json, schedules, README, mms_common.py, make_schedule2.py (planning lines), tiles_gen.py's docstring and the 24 plan tile files (zero structure, phi); E214's committed start conditions (unread-e214's conditions file: the clocks, volts and dies of E214's runs on the same two cards, to choose nothing but to see the nominal footing's scale); no E217 forecast of the model session's (its sealed ce793daa... was not read)
- **others**: reg-e217 (Q228): the registration from #13 and the same copy; data-e217 (Q228): waiting for releases; the orchestrator: the copy and the naming (#13.1)

## The inputs, by sha256

| input | sha256 |
|---|---|
| E217 kit src copy: out/orch/e217-src/SRC-SHA256SUMS.txt (75/75 OK) | `854bd07501ca95d97a5861b7c6c6ef26d6d4ac3b4f9a2f558a91cc8177b1585a` |
| E217 src/arms.json | `f30ae8789bd2bd93f35e364290dc8ca47a04fa111b3ede8a7073d7c03925110a` |
| E217 src/sched/a1c0-S1.json | `5d188ce522d9886b8d2546130a0d618b9b028118ea2791a275fd596b832bee8e` |
| E217 src/sched/a1c0-S2.json | `cd30341f6a24b479f07d2c3c0629309a02274f0caa79108a1ae3e6b0e5cc51ad` |
| E217 src/sched/a1c0-S3.json | `037c70d7d6bbbee955a77d939a25975ed6c3b1134460f163258ddcdefdfca758` |
| E217 src/sched/a1c1-S1.json | `033f1ee7ded10c95ff86eb01792665fc1f076237ec5c5f367768210f8bbf1065` |
| E217 src/sched/a1c1-S2.json | `a5b16b39db76de0866ab11dbe91c4439ffd59338a0f91cc80370a93eae3455f3` |
| E217 src/sched/a1c1-S3.json | `4fa1c781155025f41dd2e87aacb1c8a903b9f2ed1833b029973f48bbe78fbdea` |
| E217 src/sched/a1c1-S4.json | `7e253c94286343dccb25538f32f23a0ea0dc66d5a74070d7e346928b6a9ad64a` |
| MM1-v3.1 out/mm1_v31_params.json | `d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3` |
| MM1-v3.1 SHA256SUMS (2c971828; 64/64 OK) | `f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed` |
| MM1-v3.1 counts/SHA256SUMS (3e8991d0; 71/71 OK) | `c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f` |
| MM1-v3 out/mm1_v3_params.json | `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db` |
| MM1-v3 SHA256SUMS (b1493082; 170/170 OK) | `c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74` |
| MM1-v2 out/mm1_v2_params.json | `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5` |
| MM1-v2 SHA256SUMS (3ca4b717; 114/114 OK) | `eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2` |
| contention term F1 (#1.29.1) forecast-e215-v31-layout.json | `f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259` |
| contention term F1 (#1.29.1) eval_layout.py | `f076fa919ab4c28d438e5f4fcad9bd9ea8824a99afad63811d2f394cd4d97ae1` |
| contention term F1 (#1.29.1) features_layout.py | `b1f16c83d7967df7483de3bc20c64f96f9a899dd1efcd722869d942a895e26b3` |
| contention term F1 (#1.29.1) out/features_layout.json (the frozen walk cache) | `1de94e5611c0912eb4bfb4294df9fabeb07078f4c31344e29e15c5200f1b0183` |
| contention term land SHA256SUMS (25 files, 25/25 OK) | `dc2ae92452f6c601de5ebfb0291c9a181a4d2334d516ccbb37cb283fcfc6fc48` |
| gemmLnc term F3 (#1.29) term-gemmlnc.json | `2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4` |
| verify-lay's maker v02_fits.py (#1.29.1.1) | `4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8` |
| verify-lay's fits record v02_fits.json (the controls' constants) | `1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312` |
| verify-lay's E215 control columns v02_e215_controls.csv (#1.29.1.1) | `c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d` |
| counts-e214 SHA256SUMS (49/49 OK; no E217 tile is one of its tiles) | `4c39d0d3cf4ad405d5d32d4128f828d0d39272aab8dc0c822a2eacbb49be664a` |
| E215 rules_e215.py (the band form) | `5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272` |
| work/step1/runs-listed.json | `25154e5dedd47519a145c693273e3ac3f3cbcabc4e82581a30ebaef34d0d4bc1` |
| work/step1/models-step1.json | `2ceaf17a6796e5b5688f7caa23551ae6fad876d7e4abef33ee2617d428834589` |
| work/step1/twin-keys.json | `3418b7d8de1f0e07e765de8deb2486d44392788f83c7bb9159ff8230fb96893c` |
| work/step1/bands.json | `9da7e31ade46527c332938e0eb0cfc69ba8d5aaa79fa2285e1db225d8cdeb988` |
| scripts/s00_setup.sh | `5db6854bb18cfc56013fe307ead9ee7fccdc42834ac4085303bda66830c3024b` |
| scripts/s01_list.py | `c6213fcaf14691da3e0e0178077d6bfabf772046aa51d12ca943d6fe82fe78ca` |
| scripts/s01b_models.py | `522485c48abb673d6dd691906e4e365693cb2dfdb417c9d7c1bcdd342e0d82b2` |
| scripts/s01d_bands.py | `480aadeab194a3ee2072e07fb27720be927e9fbd44569d52617b943c08c7e9d4` |
| scripts/s01e_declare.py | `7b027f642bb3cefdb9f898d4ba37682674050ce79fa59b3c6e14ad8c6c03239b` |
| scripts/s02w_walk.py | `023231764a69015a4dee3000521a3264ef5227a3261282c0952a0b0efcb140bc` |
| scripts/s02b_nominal.py | `0a13366ace4d819e22aac98d1055e1a4a08bfb7085f2c5cdab25879cc7e00f0b` |
| scripts/s02c_write.py | `c4a1273acd59590f555e911a5743e21fa723e22628fa5de8e55afcaedb780cfe` |
| scripts/env.sh | `ab57e9fd9ee760530f20bca6628dbd2edf77be42ee41ad44dea8bcf0c6ede3a0` |
| scripts/run_slot.sh | `b01f6ba7847310ef2e8ba8ba66f8fc0c10875a2d7fdd957a8f7c734c4b947304` |

**Order:** 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt -> 4 counts-e217 -> COUNTS-FROZEN.txt; then, after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores. Every sha256 and time in logs/progress.txt.
