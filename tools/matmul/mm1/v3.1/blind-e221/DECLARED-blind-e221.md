# decl-e221: the lab's BLIND test of its frozen matmul models on E221, DECLARED before any E221 datum

*Lane decl-e221 (round Q235), aifoundry2's desk; written Fri 20 Nov 2026 06:15:39 PST, Pacific time. Desk only: no card, no ssh, no simulator, no commit. Interpreter: /usr/bin/python3 3.12.3, -I -B, single-threaded, every numerical step one slot job. Inputs: a git archive of GitHub main 0f046200 (= LAB HEAD), the orchestrator's copy of E221's kit (SRC-SHA256SUMS.txt 5680112f...), verify-lay's fits record and the three MM1-v3.3 candidates' frozen makers (Q234). Labels: registered (this file), measured, desk, post hoc, held out, blind; REPORTED = printed beside, deciding nothing.*

**The experiment.** E221 (#15, 05:53:07 PST Fri 20 Nov 2026): the model session's sixth matmul sweep, 1120-mmsweep6, of E136's rgm136 unchanged: 847 runs over 345 gemmL arms and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S3 low power, aifoundry2 card 0 S1-S3 under the kit's live stops 85 W x3 / 80 C); its sealed forecast cab693ef... is not read here.

**The state at this declaration** (W/out/orch/e221-releases.txt):
- #15 2026-11-20 05:53:07 PST: the proposal (1120-mmsweep6; 847 runs over 345 gemmL arms and an anchor in nine sessions: aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S3 low power, aifoundry2 card 0 S1-S3 under the kit's live stops 85 W x3 / 80 C; sealed forecast cab693ef8a81e796a2d21eea34d5dd3d068b3036e91b47e47784c42adc26ea67).
- #15.1 2026-11-20 05:53:45 PST: CLAIM aifoundry1 card 1 for E221 S1 (a1c1-S1, 96 runs, sha256 6cb71195bff0f289..., about 58.8 card-minutes, at most 72) from 05:53 to 07:20 PST (posted before the lab's freeze: S1 is UNREAD for the lab's declared test).
- #15.2 2026-11-20 05:54:38 PST: the lab names it E221; yes to aifoundry2 card 0 under the kit's live stops (85 W x3, 80 C) as E212 ran there; asks the first session to wait for the lab's freeze post (S1 had already been claimed) and aifoundry1 card 1 and aifoundry2's card for E220 from about 11:30.
- #15.2.1 2026-11-20 05:55:48 PST: the model session: card 1's S1 had started at 05:53:56 (42 s before #15.2); it stopped it at 05:55:27 as its first run began, so NO RUN RAN (only the opening rest and three smoke processes, 1.47 card-minutes, in EE/sessions/1795182836-a1c1-S1/: keep apart, not a scheduled session's data); released aifoundry1 card 1 at 05:55; S1 is claimed again whole after the lab's freeze post; aifoundry1 card 1 and aifoundry2's card left to E220 before its rest for 11:30.

## 0. MM1's domain, first

- **EVERY E221 case is IN MM1's domain: all 345 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no gemmLnc, no block, stream or TenB arm); NO case is OUT OF DOMAIN, so none is left unforecast.**
- Evidence: probe p01: every one of the 733 cases has a form (finite wall and mean cycles, op time; energy FORECAST) in MM1-v3.2 733, MM1-v3.1 733, MM1-v3 733, MM1-v2 733 at the nominal footing (work/step1/domain-probe.json, status only).

| class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | posimb scope | L3S domain |
|---|---|---|---|---|---|---|---|---|---|---|
| MASK | the core-group masks (family PL: placement of one shape on shire groups, PLA/PLB/PLC/PLD/PLE/PLH/PLK/PLK3/PLL/PLM/PLN/PLX), each with its whole-chip twin | 392 | 402 | 360 / 32 | yes | yes | yes | yes | 360 | 32 |
| CELL1 | the 1x1x1 cells at new masks (families CLK and PLS): gemmL 1x1x1 at shire masks never run before, fp32 and fp16 | 79 | 79 | 76 / 3 | yes | yes | yes | yes | 76 | 3 |
| KB1 | KB = 1: gemmL MBxNBx1 at the whole chip (fp32 random and zeros, fp16 ones and zeros) | 72 | 72 | 0 / 72 | yes | yes | yes | yes | 0 | 72 |
| L2I8 | the int8 L2 point: gemmL 1x1xK int8 (K blocks 1-13) at the whole chip and at masks, with two fp32 zeros pairs | 54 | 54 | 25 / 29 | yes | yes | yes | yes | 25 | 29 |
| MQ3 | the MB = 3 ladders: gemmL 3xNBxKB, the whole chip | 47 | 47 | 0 / 47 | yes | yes | yes | yes | 0 | 47 |
| DK | deep K: gemmL at KB 16-32, the whole chip | 30 | 30 | 0 / 30 | yes | yes | yes | yes | 0 | 30 |
| HLD | the held walks: small gemmL shapes (2x3x3, 2x6x2, 2x7x2, 3x3x2, 3x5x2), the whole chip | 23 | 23 | 0 / 23 | yes | yes | yes | yes | 0 | 23 |
| BW | the BW shapes: gemmL 2x12x4, 5x12x2, 6x5x3 at every kind, the whole chip | 18 | 18 | 0 / 18 | yes | yes | yes | yes | 0 | 18 |
| NB1 | NB = 1: gemmL 2x1x7, 9x1x1, 9x1x2, the whole chip | 15 | 15 | 0 / 15 | yes | yes | yes | yes | 0 | 15 |
| ANCHOR | the anchor (4x8x8 int8 random, whole chip): first, between blocks and last in each session | 3 | 71 | 0 / 3 | yes | yes | yes | yes | 0 | 3 |

- MM1-v0 and MM1-v1 (not declared models here, not probed): each has a gemmL form (mm1_v0.py classes_gemmL, subsets at the full chip's footprint; mm1_core.py Shape with the masked map).
- **NOT APPLICABLE:** 'v3.1 + gemmLnc term' (#1.29, F3) and 'MM1-v3.2 + gemmLnc term AF4' (lnc-form): each is 0 off gemmLnc and E221 runs no gemmLnc arm, so each equals its base on every case: declared NOT APPLICABLE, not scored.
- **Domain limits, REPORTED apart:** IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the 1x1x1 cells and core-group masks at shire masks no fit holds (most of E221's 65 masks); aifoundry2 card 0 and aifoundry1 card 0 under their governors (the clock read from each run's start-of-run records; the nominal footing at 800 MHz); configuration twins (section c) split.
- **OUT OF DOMAIN: none** (0 cases): there is no E221 arm class without a frozen MM1 form, so every case is forecast and scored.

## a. The runs
- **listed**: 811 runs ({'anchor': 71, 'arm': 740}) of the schedules' 847 (36 nulls and each session's smoke left out), 733 cases (a case = card, arm, format, kind, mask); by session {'a1c0-S1': 89, 'a1c0-S2': 92, 'a1c0-S3': 78, 'a1c1-S1': 92, 'a1c1-S2': 91, 'a1c1-S3': 93, 'a2c0-S1': 93, 'a2c0-S2': 90, 'a2c0-S3': 93}; by card {'aifoundry1 card 0': 259, 'aifoundry1 card 1': 276, 'aifoundry2 card 0': 276} runs, {'aifoundry1 card 0': 232, 'aifoundry1 card 1': 250, 'aifoundry2 card 0': 251} cases; by format {'fp16': 59, 'fp32': 596, 'int8': 156} runs; by kind {'ones': 89, 'random': 181, 'zeros': 541} runs; by class {'ANCHOR': 71, 'MASK': 402, 'CELL1': 79, 'L2I8': 54, 'KB1': 72, 'MQ3': 47, 'DK': 30, 'HLD': 23, 'NB1': 15, 'BW': 18} runs, {'ANCHOR': 3, 'MASK': 392, 'CELL1': 79, 'L2I8': 54, 'KB1': 72, 'MQ3': 47, 'DK': 30, 'HLD': 23, 'NB1': 15, 'BW': 18} cases; subset masks 461 cases over 65 masks (132 subset configurations)
- **ids**: E221|<card>-<S>|<i:03d>-<arm id>: the kit's own run key (run_mms.py), from src/sched/<card>-<S>.json and src/arms.json of the orchestrator's copy (SRC-SHA256SUMS.txt 5680112f..., 53/53; the kit's own SRC-SHA256SUMS 52/52); the list is work/step1/runs-listed.json
- **fit_inclusion**: NO E221 point can be in any fit: E221 has no datum for this lane. Checked all the same: no E221 token in any model's inputs or loaders (MM1-v3.2 13 files, MM1-v3.1 28, MM1-v3 115, MM1-v2 86: 0 hits) and no E221 id in any landed point record (MM1-v3.2 to E215, MM1-v3.1 to E213, MM1-v3 to E212, MM1-v2 to E208)
- **tiles**: E221 designs no tile: arms.json's tiles table is empty and its 9 tile files (8 named by arms) equal the lab's kinds (tools/claims-v3/kinds/tiles) byte for byte, each a committed blob; so no switch count is made (step 4 NOT NEEDED)
- **aborted_S1_start**: aifoundry1 card 1's S1 started 05:53:56 and was stopped at 05:55:27 as its first run began (#15.2.1): no run ran (the opening rest and three smoke processes, 1.47 card-minutes, EE/sessions/1795182836-a1c1-S1/): kept apart, not a scheduled session's data, never opened by this lane, never scored; S1 is claimed again whole after the lab's freeze post, and its own session folder and first card command decide its label

## b. The quantities
- **per_card**: aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz); aifoundry2 card 0 under its governor (main band 800 MHz), the kit's live stops
- **T1_wall**: cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1
- **T2_counter_mean**: the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1
- **T3_seconds**: seconds a pass (one GEMM): 64 MB NB KB x T_forecast(us) x 1e-6 / t_pass_s - 1 (the host's ops a minion a pass); at the measured clock T3 equals T1 identically (the reducer's T_op_us = wall / ops): both printed
- **E1_J_over_idle_given_t**: W over idle at the measured op time, W = A + B / t_meas (the predictor's W_affine at the run's conditions) against the primary view's dP_w; relative (= J over idle given t) when the case's mean MM1-v3.2 W given t and its mean measured dP_w are both 3 W or more; else a WATTS case scored in watts (E215's form; the watts set fixed by MM1-v3.2 and the measurement, the same for every model)
- **E2_J_over_idle_t_forecast**: (W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc at the model's own op time; at a watts case W_fc - dP_w
- **E3_J_at_rest_given_t**: (P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run's rest, measured, given)
- **E4_J_at_rest_t_forecast**: (P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1
- **split**: per card; per format and kind; per class (MASK, CELL1, KB1, L2I8, MQ3, DK, HLD, BW, NB1, ANCHOR); FULL and SUB; configuration twins apart (section c)

## The models
- **MM1-v3.2**: THE LAB'S NEWEST (tools/matmul/mm1/v3.2, landed 4e386f75; SHA256SUMS d52c9cce, 58/58): mm1_v32.Model(out/mm1_v32_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel rgm136, V, t0_c}]); time T5r+G0+n32 refitted, no layout term; energy E1t + F3 (0 off gemmLnc). The pass rule's model (section f)
- **MM1-v3.1**: tools/matmul/mm1/v3.1 (landed 2c971828; SHA256SUMS f6840d2d, 64/64): mm1_v31.Model(out/mm1_v31_params.json).predict_many
- **MM1-v3**: tools/matmul/mm1/v3 (landed b1493082; SHA256SUMS c24efc14, 170/170): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=, t0_c=)
- **MM1-v2**: tools/matmul/mm1/v2 (SHA256SUMS eafb6558, 114/114) through MM1-v3's unread_v2_e212.call: card 1 V None (the 0.517 V footing), the governed cards the measured volts (V_mv); energy for random, zeros and ones (E221's only kinds); no die term
- **v3.1+contention**: F1 (#1.29.1, tools/matmul/mm1/v3.2-terms/layout): T = T_v3.1 x clip(1 + a Phi_fresh, 0.3, 3.0), a = -0.08316593007433395 (forecast-e215-v31-layout.json meta), Phi_fresh by the term's eval_layout.phi_of over the masked walk's features (step 2w: 137 configurations computed by the term's features_layout code, 5 from its frozen cache); 1 at the full mask; energy MM1-v3.1's affine at its own op time
- **v3.1+gemmLnc**: F3 (#1.29): NOT APPLICABLE (no gemmLnc arm in E221; it equals MM1-v3.1 on every case); not scored
- **v3.1+both**: reg-e216's composition: F1's time, W = A + (B + dW t_op,v3.1) / t with the gemmLnc term's dW, 0 on every E221 case: equal to v3.1+contention on every case (computed by the composition all the same)
- **controls**: verify-lay's controls (#1.29.1.1) by v02_fits.py's forms unchanged with its all-data constants (work/verify-lay/v02_fits.json, re-run on E221's configurations): N1+N2 (N1 = 1 - n/32, N2 = N1^2; a = [-0.09348958586302018, 0.11765730189141044]); G1 (hop mean: (110 + 12 h)/(110 + 12 h_full) - 1; a = [0.30314251932286107]); G1+N1 (a = [0.6022127706566506, -0.021675728290377668]); the layout-blind F1 (fresh32_bar_narm: Phi_fresh averaged over E221's listed configurations of the same (n shires, arm); a = [-0.17556875184106632]); factor 1 + sum a_i x_i (unclipped), 1 at the full mask; time MM1-v3.1's x the factor, energy MM1-v3.1's affine at its own op time
- **MM1-v3.2+posimb (REPORTED)**: the MM1-v3.3 candidate of layout2 (Q234; FROZEN.txt 81d04c97 at 05:39:48 PST, posted #1.30.1.2.1 05:47:36; KEPT by its declared rule): by its frozen maker's composition unchanged (h01_freeze.py: g_wall = clip(1 + a_hop e G1core + a_lag e LAGcore, 0.3, 3), g_mean = clip(1 + a_hop e G1core, 0.3, 3); e the elasticity of MM1-v3.2's op time to its memory constants (x 1.01) by Engine31; G1core = Lmean_act / Lmean_full - 1, LAGcore = (Lmax_act - Lmean_act) / Lmean_full x Fp / (Fp + Fs) from f02_private's features (step 2f: 121 made, 11 from its frozen cache)) at its all-data a_hop = 0.1333333152086018, a_lag = 0.4367172478570998; in scope at the subset masks of rgm136 gemmL (461 cases), MM1-v3.2 to the last bit elsewhere; energy MM1-v3.2's affine at the composed op time (the maker's compose)
- **MM1-v3.2+L3S (REPORTED)**: the MM1-v3.3 candidate of l3-edge (Q234; FROZEN.txt e8216cbb at 05:57:20 PST; KEPT by its declared rule): its frozen maker's term_l3s.ModelL3S(MM1-v3.2's params, lam = 0.6908933059768666, the set model's cache) unchanged; in its domain at the full mask (272 cases; the set model's records: 37 made here by l3s_feature.a_shares, 26 from its frozen cache), MM1-v3.2 to the last bit at the subset masks; energy MM1-v3.2's predictor on the shifted class distribution (the maker's own)
- **MM1-v3.2+AF4**: the MM1-v3.3 candidate of lnc-form (Q234; FROZEN.txt 5373973f at 05:35:36 PST): NOT APPLICABLE (0 off gemmLnc; no gemmLnc arm in E221): equal to MM1-v3.2 on every case; not scored
- **maker_checks**: before any output, step 2 re-makes: F1's 94 frozen E215 rows; v02_e215_controls.csv's N3, N1+N2, G1, G1+N1 columns; every one of posimb's 306 frozen E220 rows (g_wall and wall cycles) and L3S's 306 frozen E220 rows (wall cycles) from their frozen files (probe p02: all exact)

## The forecast procedure
- **footing_1_measured**: THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's start-of-run records only (MM1's README section 5 form, as unread-e214, decl-e217 and decl-e219 did): the primary view's kernel clock kclock_mhz; minion volts: card 1 the models' footing 0.517 V, the governed cards the primary view's rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). The terms, controls and candidates on their base model's forecast at the same conditions; their features are configuration-only (steps 2w, 2f)
- **fields_read_before_scoring**: from each committed E221 data JSON ONLY: the top-level card, session and primary_view, and per run: run, i, ran, role, arm, values, type, shires, minions, die_start_c, arm_token, arm_family, ops_pass, ops_pass_ok, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read until the forecasts at those conditions are hashed
- **footing_2_nominal**: the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED)
- **counts_as_inputs**: the switch counts are inputs, never fitted: each model's own tables (MM1-v3.1 and MM1-v3.2: MM1-v3's rows + counts 3e8991d0; counts-e214); E221's kinds (zeros, ones, random) are committed kinds with committed counts; E221 designs no tile, so counts-e217's rows are not needed and no count is made
- **order**: 0 the work copies -> 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt (no step 4: no counts); after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores

## c. The metric
- **error**: forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W
- **case**: a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside
- **twins**: per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in that model's TRAINING time configurations (its landed out/points_time_*.csv; E146 store rungs out); an energy case when that key and its kind are in its energy configurations (work/step1/twin-keys.json, 3bfd3883); the no-twin cases carry the pass rule and the headline; twins and all cases printed beside. At the nominal clocks (a preview; the measured clock decides): MM1-v3.2 35 time / 31 energy twins of 733, MM1-v3.1 17 / 15, MM1-v3 17 / 15, MM1-v2 8 / 8

## d. The comparisons
- **test**: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none
- **d**: per case d = |ln(1 + e_B)| - |ln(1 + e_A)| (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both price (twins included); REPORTED beside over the cases that are twins for neither
- **ties_how**: E215's rule (rules_e215.ties_of) on the floors of work/step1/bands.json: card 1 E215 arm B's registered ties {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.1}; aifoundry1 card 0 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.15} (E212 a1c0-S1/S2); aifoundry2 card 0 {'cycles_ln': 0.005, 'joules_ln': 0.02, 'seconds_ln': 0.005, 'watts_W': 0.4} (E212 a2c0-S1/S2: a weak floor, 3 cases with two runs)
- **D0_v32_vs_v31**: MM1-v3.2 vs MM1-v3.1 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled over every case; per class REPORTED
- **D1_v31_vs_v3**: MM1-v3.1 vs MM1-v3 on H1-H5: per card and pooled; per class REPORTED
- **D2_v31_vs_v2**: MM1-v3.1 vs MM1-v2 on H1-H5: per card and pooled; per class REPORTED
- **D3_layout**: on the subset-mask cases (461: the MASK, CELL1 and L2I8 classes at shire subsets), per card and pooled: 'v3.1+contention' vs MM1-v3.1, and each control (N1+N2, G1, G1+N1, the layout-blind F1) vs MM1-v3.1, on H1 (wall) and H2 (counter mean); per class REPORTED
- **D3c_candidates_REPORTED**: deciding nothing: MM1-v3.2+posimb vs MM1-v3.2 on the subset-mask cases (H1, H2); MM1-v3.2+L3S vs MM1-v3.2 on its 272 full-mask cases (H1-H5); each candidate vs MM1-v3.1 beside
- **D4_switch**: NOT APPLICABLE: E221 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random), so the switch route with counts against without has nothing to decide
- **verdicts**: each comparison is a verdict of its own, never part of PASS

## e. Reported beside (deciding nothing)
- **classes**: each class's rms and bias per card and model (the 1x1x1 cells at new masks, the core-group masks, KB = 1, deep K, the held walks, the int8 L2 point, MQ3, NB1, BW, the anchor), REPORTED
- **mask_ladders**: on the MASK class, each placement family (PLA, PLB, PLC, PLD, PLE, PLH, PLK, PLK3, PLL, PLM, PLN, PLX) against its whole-chip twin: measured and forecast subset/full ratios per model, REPORTED
- **governed_clock**: on the governed cards: each run's measured clock beside the nominal 800 MHz and the nominal-footing error, REPORTED

## f. The pass rule (decided by a script)
- **part_A**: MM1-v3.2 on the PRIMARY footing by E215's rule form on each card over its NO-TWIN cases (every class): a case passes T1, T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no rule FAILS on any card and at least one rule PASSES; FAILS when any rule fails (named); else NOT DECIDED
- **bands**:
  - aifoundry1 card 1: {"E1": 0.14, "E2": 0.14, "E3": 0.05, "E4": 0.1, "T1": 0.1, "T2": 0.13, "T3": 0.1, "watts_W": 0.56}
  - aifoundry1 card 0: {"E1": 0.11, "E2": 0.13, "E3": 0.05, "E4": 0.1, "T1": 0.11, "T2": 0.16, "T3": 0.11, "watts_W": 0.56}
  - aifoundry2 card 0: {"E1": 0.11, "E2": 0.13, "E3": 0.05, "E4": 0.1, "T1": 0.1, "T2": 0.13, "T3": 0.1, "watts_W": 0.72}
- **bands_how**: E215's form by rules_e215.bases from MM1-v3.1's held-out errors (work/step1/bands.json; card 1 = E215 arm B's bands, aifoundry1 card 0 = decl-e219's; aifoundry2 card 0 the same arithmetic on its own points and E212 a2c0 floors), the same bands for every model: a declared choice (MM1-v3.2 is scored against the bands its predecessor earned)
- **part_A_v31_REPORTED**: the same rules for MM1-v3.1 (the continuity with E215, E217 and E219), REPORTED, deciding nothing
- **part_S**: NOT APPLICABLE (no operand-pattern arm: D4)
- **verdict**: PASS when part A passes; FAIL when it fails (named); NOT DECIDED otherwise. Decided by a script: blind-e221's scorer (the scripts of the lane that scores E221), implementing this declaration's sections exactly, code-tested on a stand-in day built from the frozen forecasts alone, and hashed (sha256 in its progress log, posted with the result) BEFORE its first read of any E221 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing (section h) by the same script and rules beside, REPORTED. A session that does not run, or runs short, is scored on what ran; a card with no session is NO DATA

## g. The label rule
- **BLIND**: a session is BLIND for this test when FROZEN.txt's sha256 lines were posted on the Discussion before the session's first datum (its first card command, the session's own log)
- **UNREAD**: a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the post (data-e221's read times on record); else POST-READ (REPORTED)
- **S1**: aifoundry1 card 1's S1 as re-claimed after the freeze post is labelled by its own first card command; the stopped start of 05:53:56-05:55:27 (no run) is not scored
- **printed**: every result line names its label, the freeze post time and the session's first card command time

## h. The nominal footing (a second footing, frozen now, scored beside)
- **aifoundry1 card 1**: f 600.0 MHz; V 0.517 V (the models' card-1 footing); die at start 60.0 C (the kit's a1c1 start-gate ceiling)
- **aifoundry1 card 0**: f 800.0 MHz (its planned clock: the kit's main band "800"); V the model's own volts at f; die at start 55.0 C (the kit's a1c0 start-gate ceiling)
- **aifoundry2 card 0**: f 800.0 MHz (the kit's main band "800" for the governed card); V the model's own volts at f; die at start 55.0 C (the kit's a2c0 start-gate ceiling)
- **files**: forecasts-nominal-e221.csv and .json: one forecast a case and model for every case (every run of a case at the same nominal conditions), all 12 model columns (2 REPORTED)
- **scored**: by the same rules as the primary footing, beside it, REPORTED

## i. Earlier reads, disclosed
- **E221_data**: none read: the only E221 files that exist at this declaration are the stopped S1 start's (EE/sessions/1795182836-a1c1-S1/, no run), on aifoundry1, never opened (no ssh by this lane)
- **this_lane**: read the kit copy's arms.json, schedules, README, mms_common.py (the cards and gates), reduce_mms.py's header (the primary view), make_schedule2.py (a grep for the family codes) and the 9 tile files' bytes against the lab's kinds; the frozen models' code and READMEs; the three candidates' makers (scripts, frozen files, fit records and caches, copied read-only); probe p01 (the domain, status only) and probe p02 (a code test of the nominal-forecast script: only its checks, counts and the factor ranges over the subset cases printed; its output deleted unread) ran before this declaration and chose nothing in it; no E221 forecast of the model session's (its sealed cab693ef... was not read); no E220 datum
- **others**: reg-e221 and data-e221 (Q235) run beside: the registration from #15 and the same copy, and the data lane waiting for releases; the orchestrator: the copy (05:54:33) and the naming (#15.2)

## The inputs, by sha256

- `3a686510a43c453ac85588d5e649c7fe2e8554c3a98357e79047784e5165fe98`  work/step1/runs-listed.json
- `b2dc3a2ffa7934b8679212f960e256193f7576903f3bd2767836b5bc01387cfe`  work/step1/models-step1.json
- `3bfd3883739214e80d485a06e72a58fde72b5abef44992345ae6c0cf98656807`  work/step1/twin-keys.json
- `57cc5faf6aa88b97023b7c8a3ef7c6200c6f75de90943b9b40e7da2825e91ef8`  work/step1/bands.json
- `f98bf3d54959f4944956cbcd61d4f48c9980c8d09b506ea00fb51199e2069a0e`  work/step1/domain-probe.json
- `b316da119b61c2ec2ab275e9528d843ae6bfad146e29edc36f0ddac6949be7b8`  work/step2/walk-feats-e221.json
- `848db0174a64edd81265ff2bfc8261585b93861b9b9437a27d02e95980e599b2`  work/step2/cand-feats-e221.json
- `80726a42194fef9b2dd457b796c4628d1ee11bb2db2f51789acc9cb2a5f0ea6d`  work/lab-commit.txt
- `5680112f19814172f2fe682b145f3b123a753181ee8173a6f247cc49617077b1`  work/e221-src/SRC-SHA256SUMS.txt
- `7559ddaadd1981dcf8f4485e8c4aee3fc46477d45645170ec6fb3b77fcb3c68b`  work/e221-src/src/arms.json
- `1bfec7fc123787f5590356de65125df80d6bb4366f14e0376806913fbb27d312`  work/verify-lay/v02_fits.json
- `4fb92de3d4876a266ae14c1ad4cf7d4575e3ef4d83b34c60fe5e6f9db3babac8`  work/verify-lay/v02_fits.py
- `81d04c97af0ecf69e16d2a7a17141e0ca0bdf7ce57ebfd9cc42a3440516dd85f`  work/cands/layout2/FROZEN.txt
- `5373973ff4ce03175df72801163241cc7015003b8c0fd52e2f0b5cfaf999bfab`  work/cands/lnc-form/FROZEN.txt
- `e8216cbb2a222a1c48a4b929fd4f07d10d80f4b20f97813b700bbdc6cff401e0`  work/cands/l3-edge/FROZEN.txt
- `816d1d51548b68062ffebf26f2c29b815a9069066c9d1f2cd71cb8fb222d3071`  work/cands/layout2/work/fit_results.json
- `aa5c9cf309bc71ab6cbf6d24b75d6a38aaf321477a62dacc7fc04fdb9c459e17`  work/cands/layout2/work/private_shared.json
- `4fe923507f7fef4d9925e8d5746727a0024b0ea42465dc0d463553e9936d750b`  work/cands/l3-edge/work/fit/fit-l3s.json
- `6171c473e57534be7ca6828f08d989887b770d1197d98044068fa9efaac0668c`  work/cands/l3-edge/work/feature/l3s_cache.json
- `d52c9cce15db12ed66873722b9ec5c07be1fdeec3027a23833c7e3d230d1d761`  work/lab/tools/matmul/mm1/v3.2/SHA256SUMS
- `c991de169b056e1e700a41738b8be0be14b107ef4c9494a7ac0e0f37fc603eab`  work/lab/tools/matmul/mm1/v3.2/out/mm1_v32_params.json
- `f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed`  work/lab/tools/matmul/mm1/v3.1/SHA256SUMS
- `d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3`  work/lab/tools/matmul/mm1/v3.1/out/mm1_v31_params.json
- `c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74`  work/lab/tools/matmul/mm1/v3/SHA256SUMS
- `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db`  work/lab/tools/matmul/mm1/v3/out/mm1_v3_params.json
- `eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2`  work/lab/tools/matmul/mm1/v2/SHA256SUMS
- `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5`  work/lab/tools/matmul/mm1/v2/out/mm1_v2_params.json
- `dc2ae92452f6c601de5ebfb0291c9a181a4d2334d516ccbb37cb283fcfc6fc48`  work/lab/tools/matmul/mm1/v3.2-terms/layout/SHA256SUMS
- `0f671361506bfcc92fb5976219f095affb604f6d1f6e260daedf2c6eebd0e0f5`  work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc/SHA256SUMS
- `5a44879ca9c4f0c7d8c4084f4dca93886fe6b18bfb1cf1a81bb76cc29d6f2272`  work/lab/tools/claims-v3/e215/rules_e215.py
- `9c1c51dcf188153e062225bad261964a16906b0bc1dab04bfb87300cca5fab50`  work/e221-src/src/sched/a1c0-S1.json
- `ea1ab694d1065434969c9b366ee5714aa2f1c891d4e72be64fa5f5f1183835ca`  work/e221-src/src/sched/a1c0-S2.json
- `46ddf92e3a185a9ca4a8888499cfde8757493f8d9283739a344dfaf85b78a111`  work/e221-src/src/sched/a1c0-S3.json
- `6cb71195bff0f289ed7155a495a1d3a54a169a44d3a915a2b4a5dcf71ab4591b`  work/e221-src/src/sched/a1c1-S1.json
- `fb78237c571c5b25d3bdd3ce85360e04106ffffba301b9c5e71653a329aa741e`  work/e221-src/src/sched/a1c1-S2.json
- `a0e0a2eb33f926b8d19bc2faf3884ca5329c9c45941f22d83f25bb214c810288`  work/e221-src/src/sched/a1c1-S3.json
- `3a1a6b7ab5ee90d5fcf3764a8037306f094147f27ca48d97b0472f5231d20168`  work/e221-src/src/sched/a2c0-S1.json
- `8111b2d1b81727ee8e0996e0aa28fb0d5a145cbccfb4528f9167fcdeb6c5730c`  work/e221-src/src/sched/a2c0-S2.json
- `3cd697c5d7a6c83ba3c463aa13c6ff8f321f10e5b63220f445d09852ff696a64`  work/e221-src/src/sched/a2c0-S3.json
- `0569d1dc024ec4a3e6eeaaf8c5bfae2d33eb5213ec9a5dd6e3b5030333c93f1a`  scripts/env.sh
- `67f2a6c4722b8b37d13272d02484990885dc53cba2288124db0414583f3ac066`  scripts/p01_probe.py
- `1f3d64de172f4a2db72599c0256eb086ce9fad1819e85882642e4eab0a01f8a1`  scripts/run_slot.sh
- `061d2a98e731f14b491b5d858cbced4de52961923a5ebda17b40709569b76178`  scripts/s00a_setup_lab.sh
- `220ea27f8d827e1a3742d0072ff9b9cca01414ce58fba33252f5a9b68f398904`  scripts/s00b_setup_kit.sh
- `de120ba2cf3ed9d6ee86cb61b88be2a06a8ef87a588455555ff0d824c2f01229`  scripts/s00d_more_lab.sh
- `858d8c236501c3a807ac1bd4d1e8e2045516ce701fafbb725f4e3b1d809e8bfc`  scripts/s01_list.py
- `690676a57cba2ac2647970bca3dfab1b3655866928d8876a8f0afe3a01110ab4`  scripts/s01b_models.py
- `601e2da20ea49990cecfcaf8eba30ef2a688f1ab2744711f6ab454913ce46c9d`  scripts/s01d_bands.py
- `36e4ef6faee8e16d00448d06d1efb151996ff5477f80a0349f8ad03711f33378`  scripts/s01e_declare.py
- `b43030186fe153b96634e642f75ca73b75a62332ac3b2bfd01cc2443042e75d0`  scripts/s02b_nominal.py
- `342138469cba6ed5ed6bd835214d7ebd883a61c8e07eb30b3ee3502233b8476a`  scripts/s02f_cands.py
- `0a8571ccfbcc8a9fd3418b0a18ca4b1a5508820f30a020f8b29ef476e463357f`  scripts/s02w_walk.py

SPDX-License-Identifier: Apache-2.0
