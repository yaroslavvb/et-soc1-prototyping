# unread-e214: DECLARED before any E214 measurement is read (MM1-v3.1, MM1-v3, MM1-v2 UNREAD on E214)

*Declared Thu 19 Nov 2026 10:42:28 PST, round Q225 track A, at the desk on aifoundry2 (work copy of GitHub main 8bde0182). Python: /usr/bin/python3 3.12.3, numpy 1.26.4, single-threaded in slot.sh. Nothing here was measured; no E214 data file was opened for this declaration.*

**Label: UNREAD.** UNREAD: MM1-v3.1 (landed 2c971828), MM1-v3 (b1493082) and MM1-v2 (3ca4b717) frozen, unchanged, with the switch counts frozen (MM1-v3.1 counts/ 3e8991d0, SHA256SUMS c74c2d49...; counts-e214 land dir, SHA256SUMS 4c39d0d3..., verified HOLDS), before this lane reads any E214 measurement. Not blind: E214's data existed (committed Wed 18 Nov 16:44-21:06 PST, notes 10f662e3) and earlier lanes read them (section g).

## a. The runs
- **593 runs** ({'anchor': 38, 'arm': 555}) in E214's seven sessions, 361 arms, 518 cases; by card {'aifoundry1 card 0': 247, 'aifoundry1 card 1': 346}; by format {'fp16': 85, 'fp32': 289, 'int8': 219}. All 593 ran (queue), rc 0, every check exact or approx, no flag.
- Source: the registered schedules (tools/claims-v3/e214/proposal/src/sched/<s>.json, each equal to its session's queue.json sched_sha256), arms.json, and each committed session/queue.json (fields i, block, role, arm, run, form, ran, rc, check, checks, flags) and meta-e214-<s>.json (sid, card, schedule) at GitHub main 8bde0182; no measurement column. The run ids are in `DECLARED-unread-e214.json` (a_runs.run_ids) and `work/step1/runs-listed.json`.
- Time selection: as MM1-v3.1's own loader data_v31.mms_runs_all (= data_v3.mms_runs): ran; role not null; values gemmL<MB>x<NB>x<KB>: and shires present; the primary view (band600 on card 1, win on card 0: reduce_mms.py) has T_op_us, cyc_op_max and n_launch >= 1. Nulls are not runs here.
- Energy selection: the same, and the primary view's dP_w is not None, its p_mean_w is truthy, the run is not capped and its role is not "time" (data_v31.mms_runs_all's energy condition, every kind read)
- Case: (card, arm gemmL<MB>x<NB>x<KB>, format, kind as the arm spells it, mask) over all of that card's sessions (a case run in two sessions is one case), MM1-v3's case form; anchors (4x8x8 int8 random) are cases like any other
- Group M (main): every listed run: time for every kind; energy for every kind a model prices (593 runs)
- Group S (the switch-pattern arms): the runs of E214's 20 new tile kinds (54 runs, 33 arms): ['pattern:ar_e5', 'pattern:bh3_e3', 'pattern:h_ar_e3', 'pattern:h_bh_sm2', 'pattern:h_hi_all16a8', 'pattern:h_hi_s11a5', 'pattern:h_ka_m9', 'pattern:hi_all32a25', 'pattern:hi_e3s27a20', 'pattern:hi_m23a7', 'pattern:hi_s24a20', 'pattern:i8_ar_d13', 'pattern:i8_bh_hi12', 'pattern:i8_bh_lo11', 'pattern:i8_hi_b28', 'pattern:i8_hi_b32a8', 'pattern:i8_sp_bh', 'pattern:ka_e3m8', 'pattern:kb_s5m', 'pattern:sp_ar4']
- Group C (the sparse50 pools): pattern:sparse50f / sparse50h / sparse50i (44 runs), priced as the committed sparse50 kind

### a2. Did any E214 point enter MM1-v3.1's fit?
**NO E214 point entered MM1-v3.1's fit, nor MM1-v3's or MM1-v2's: (a) no E214 token in any model's inputs or loaders (MM1-v3.1 28 files, MM1-v3 115, MM1-v2 86: 0 hits); (b) no E214 id in the landed point records (points_time / points_energy of each model; MM1-v3.1's experiments E105-E213); (c) by git, E214 a1c0-S1's data commit 3b3e4182 (16:44:33 PST) was ON GitHub main f0d58c84 when MM1-v3.1's fit started (17:03:47 PST), but data_v31.py reads only vendored inputs (inputs/ and ../v3/inputs/) and none is E214's; its README section 0: "E214 ... enters only by a dated amendment (none was made)". Every other E214 session was committed after the fit started. MM1-v3 (58f01105) and MM1-v2 (3ca4b717) predate every E214 datum. So every E214 point is unread for all three models.**

| session | data commit | committed (PST) | on main when MM1-v3.1 was fitted (f0d58c84)? |
|---|---|---|---|
| a1c0-S1 | 3b3e4182 | 2026-11-18 16:44:33 | on main when fitted (an ancestor) |
| a1c0-S2 | 317ce38c | 2026-11-18 18:09:19 | not on main when fitted |
| a1c0-S3 | 117ca637 | 2026-11-18 19:35:53 | not on main when fitted |
| a1c1-S1 | f7f3257c | 2026-11-18 17:28:54 | not on main when fitted |
| a1c1-S2 | a457d7fc | 2026-11-18 18:53:24 | not on main when fitted |
| a1c1-S3 | 9ac3c338 | 2026-11-18 20:19:53 | not on main when fitted |
| a1c1-S4 | 0e95201d | 2026-11-18 21:05:35 | not on main when fitted |

Twins: a configuration twin is NOT an E214 point in a fit: it is an E214 case whose configuration (card, kernel, arm, format, mask, clock to 25 MHz; energy adds the kind) is among the model's training points from other experiments (E208, E212 on these cards): split out in every table (section c).

## b. The quantities
- **how_each_model_is_called**: at each run's measured conditions, as MM1-v3 README section 5 (the unread S4 form): the primary view's kernel clock kclock_mhz; minion volts: aifoundry1 card 1 the models' footing 0.517 V (data_v3.cases, MM1-v2's default), aifoundry1 card 0 the primary view's minion rail mV / 1000 (else mm1_core_v3.volts); the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). MM1-v3.1: mm1_v31.Model(out/mm1_v31_params.json).predict_many; MM1-v3: mm1_v3.Model(out/mm1_v3_params.json).predict; MM1-v2: unread_v2_e212.call (MM1-v3's caller of MM1-v2: card 1 V None (0.517 footing), G 0; card 0 the measured volts; energy for random, zeros and ones only, any other kind NOT FORECAST in energy; no die term). Kernel rgm136 (E214 runs rgm136 gemmL only). Time is kind-blind in every MM1.
- **conditions_read_in_step_2**: step 2 reads from each committed data-e214-<s>.json ONLY: the top-level card, session and primary_view, and per run: run, i, ran, role, arm, values, type, shires, minions, die_start_c, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read before step 3.
- **T1_wall**: cycles an op, the slowest minion: forecast cycles_per_op_wall (T x f, f the run's measured clock) / cyc_op_max - 1
- **T2_counter_mean**: the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1
- **T3_seconds**: seconds a GEMM: ops x T_forecast(us) x 1e-6 / t_pass_s - 1 (ops = 64 MB NB KB a minion). By the reducer (reduce_mms.py: T_op_us = wall / ops, cyc_op_max = sum cycles / ops, kclock = sum cycles / wall, t_pass_s = wall / passes) and with the forecast made at the measured clock, T3's error equals T1's identically: both are scored and printed
- **E1_J_over_idle_given_t**: W over idle at the measured op time: W = A + B / t_meas (the predictor's W_affine at the run's conditions), against the primary view's dP_w; relative (= J over idle given t) when the case's mean MM1-v3.1 W given t and its mean measured dP_w are both 3 W or more; else a WATTS case, scored by the mean of its runs' W - dP_w in watts (E215's form; the watts set is fixed by MM1-v3.1 and the measurement, the same set for every model and for E2; Q1 of the switch test keeps Q218's own condition, the measured dP_w >= 3 W)
- **E2_J_over_idle_t_forecast**: (W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc the predictor's W over idle at its own op time T_fc; at a watts case W_fc - dP_w in watts
- **E3_J_at_rest_given_t**: (P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run's rest, measured, given)
- **E4_J_at_rest_t_forecast**: (P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1
- **split**: per card (aifoundry1 card 1 at 600 MHz; aifoundry1 card 0 at low power under its governor), per format and kind, configuration twins apart

## c. The metric
- **error**: forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W
- **case**: a case's error = the mean of its runs' errors (each run at its own conditions; Q218's form); per-run figures REPORTED beside
- **twins**: per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' clocks to 25 MHz) is in that model's TRAINING time configurations (its landed out/points_time_*.csv, E146 store rungs out); an energy case when that key and its energy kind are in the model's energy configurations (out/points_energy_*.csv; an energy point's clock its time record's, else 600 MHz on a pinned card) (work/step1/twin-keys.json). The no-twin cases carry the pass rule and the headline; twins and all cases are printed beside.

## d. The comparisons
- **pairs**: ['MM1-v3.1 vs MM1-v3', 'MM1-v3.1 vs MM1-v2', 'MM1-v3 vs MM1-v2']
- **rules**: H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled
- **d**: per case, d = |ln(1 + e_B)| - |ln(1 + e_A)| for the pair (A vs B) (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both models price (twins included); REPORTED beside over the cases that are twins for neither model
- **ties_how**: E215's rule (rules_e215.ties_of): at or above the card's replicate floor, never below E209's (0.005 in ln for cycles and seconds, 0.01 for joules, 0.05 W): card 1 E215 arm B's registered ties; card 0 from E212 a1c0-S1/S2's pooled within-case spread (bands.json card0_floors)
- **test**: the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none
- ties: card 1 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.1}; card 0 {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.15}

## e. The switch-pattern arms, the counts, phi and the sp_ar4 gate
- **counts**: MM1-v3.1: its own merged tables (MM1-v3's rows + 3e8991d0's) with counts-e214's 9 fp32 rows at S1 and S2 and 11 fp16/int8 rows added in memory by energy_v31's own loop (no key collides: asserted); MM1-v3: 3e8991d0's rows and counts-e214's added to energy_v3's E210C / SWT the same way (Q218's form). Every E214 energy cell has a count and a phi in both (cells-v31.json, cells-v3.json: 49 of 49 usable).
- **gate_sp_ar4**: DECLARED: E210's arow50 gate (g_op, g_lane, g8) = (0.5, 0, 0) for fp32 pattern:sp_ar4 (MM1-v3's gate_shares as for arow50), because the tile's A holds 8 all-zero rows (4-7, 12-15) and B none, and its count's valid share is 0.500 at S1 and S2, equal to arow50's (cells-v31.json sp_ar4); the frozen code's literal (0, 0, 0) for an unknown kind name is REPORTED beside
- **Q1**: group S, W over idle given t: MM1-v3.1 + the counts against the null N = the mean over zeros, ones and random of the run's format of the same model's own W given t at the run's conditions (the same base; only the count's information differs); cases with dP_w >= 3 W
- **Q2**: group S, E210's metric, the share of D: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, D = W_R - W_Z measured, R and Z the random and zeros cases of the same card, arm, format and mask (measured means; W_fc(R) the same model's W given t, its runs' mean); for the null [(N(P) - W_fc(R)) - (W_P - W_R)] / D; cases with an R and a Z case and D > 0
- **N2_REPORTED**: the null over ones and random only
- **MM1-v3_REPORTED**: the same with MM1-v3 + the counts
- **group_C_REPORTED**: sparse50 pools at the committed sparse50 row
- verify-counts-e214's fixes applied: merge counts-e214's two tables in memory (no key collides); pattern:sparse50f, pattern:sparse50h and pattern:sparse50i priced as the committed sparse50 kind (data_v31.SPARSE_GEN plus sparse50h); phi for the 20 new kinds by kinds_v3.phi over E214's registered tile files (section e_phi); sp_ar4's float gate declared before any E214 energy is read (gate below).
- phi (MM1-v3's own formula, kinds_v3.phi(fmt, {"tiles": [file]}), over each new kind's registered tile file (one value a kind, KB classes alike), sha256 checked against arms.json; sparse50f/h/i: MM1-v3's own phi_of("sparse50")):

| kind | phi | tile | sha256 |
|---|---|---|---|
| fp16|pattern:h_ar_e3 | 0.347617 | `tools/claims-v3/e214/proposal/src/tiles/fp16/h_ar_e3.bin` | `1e145d847dfd010f...` |
| fp16|pattern:h_bh_sm2 | 0.501412 | `tools/claims-v3/e214/proposal/src/tiles/fp16/h_bh_sm2.bin` | `f156f032118614ff...` |
| fp16|pattern:h_hi_all16a8 | 0.986233 | `tools/claims-v3/e214/proposal/src/tiles/fp16/h_hi_all16a8.bin` | `83fe7e6daaccb4b4...` |
| fp16|pattern:h_hi_s11a5 | 1.055296 | `tools/claims-v3/e214/proposal/src/tiles/fp16/h_hi_s11a5.bin` | `e78e75630859f0c2...` |
| fp16|pattern:h_ka_m9 | 0.486664 | `tools/claims-v3/e214/proposal/src/tiles/fp16/h_ka_m9.bin` | `d180bfbc30db2653...` |
| fp32|pattern:ar_e5 | 0.320427 | `tools/claims-v3/e214/proposal/src/tiles/fp32/ar_e5.bin` | `34d51fc901437d1a...` |
| fp32|pattern:bh3_e3 | 0.281258 | `tools/claims-v3/e214/proposal/src/tiles/fp32/bh3_e3.bin` | `9d5d2e2444e70a31...` |
| fp32|pattern:hi_all32a25 | 0.974485 | `tools/claims-v3/e214/proposal/src/tiles/fp32/hi_all32a25.bin` | `f4df7e09ac8177c2...` |
| fp32|pattern:hi_e3s27a20 | 1.034438 | `tools/claims-v3/e214/proposal/src/tiles/fp32/hi_e3s27a20.bin` | `cb30697ac0b00d47...` |
| fp32|pattern:hi_m23a7 | 1.003672 | `tools/claims-v3/e214/proposal/src/tiles/fp32/hi_m23a7.bin` | `52e959a686ca3a33...` |
| fp32|pattern:hi_s24a20 | 1.057245 | `tools/claims-v3/e214/proposal/src/tiles/fp32/hi_s24a20.bin` | `60c93b38f2c6badb...` |
| fp32|pattern:ka_e3m8 | 0.332557 | `tools/claims-v3/e214/proposal/src/tiles/fp32/ka_e3m8.bin` | `920ac494ba142321...` |
| fp32|pattern:kb_s5m | 0.454865 | `tools/claims-v3/e214/proposal/src/tiles/fp32/kb_s5m.bin` | `3ab46d3998464552...` |
| fp32|pattern:sp_ar4 | 0.338116 | `tools/claims-v3/e214/proposal/src/tiles/fp32/sp_ar4.bin` | `958aa1e06d94b769...` |
| int8|pattern:i8_ar_d13 | 0.876692 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_ar_d13.bin` | `0b53c8f3d316255e...` |
| int8|pattern:i8_bh_hi12 | 0.754727 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_bh_hi12.bin` | `cd4742d791bf4cfa...` |
| int8|pattern:i8_bh_lo11 | 0.788085 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_bh_lo11.bin` | `637fa676397214a0...` |
| int8|pattern:i8_hi_b28 | 0.913797 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_hi_b28.bin` | `c9b34c81ed894579...` |
| int8|pattern:i8_hi_b32a8 | 0.947643 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_hi_b32a8.bin` | `e3ba092238cdfc1f...` |
| int8|pattern:i8_sp_bh | 0.700520 | `tools/claims-v3/e214/proposal/src/tiles/int8/i8_sp_bh.bin` | `5dedd103e17616a9...` |

## f. The pass rule (decided by scripts/s03_score.py)
- **Part A:** MM1-v3.1 by E215's rule form on each card over the NO-TWIN cases: a case passes T1, T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no rule FAILS on either card and at least one rule PASSES; FAILS when any rule fails (named).
- Bands (E215's form (rules_e215.py, unchanged): 2 x max(B1, B2) rounded up to a whole percent, B1 MM1-v3.1's LOEO no-twin error over every point, B2 over this card's points (reproduced 29 of 29 of holdout_v31.json first); T3 takes T1's bases; watts band 2 x max(B1 W, B2 W, SD_rep) rounded up to 0.01 W. Card 1's equal E215 arm B's registered bands (checked).):

| card | T1 | T2 | T3 | E1 | E2 | E3 | E4 | watts |
|---|---|---|---|---|---|---|---|---|
| aifoundry1 card 1 | 10% | 13% | 10% | 14% | 14% | 5% | 10% | 0.56 W |
| aifoundry1 card 0 | 11% | 16% | 11% | 11% | 13% | 5% | 10% | 0.56 W |

- aifoundry1 card 1: T1 2 x max(4.723, 4.998) = 10.00 -> 10%; T2 2 x max(6.050, 6.450) = 12.90 -> 13%; T3 2 x max(4.723, 4.998) = 10.00 -> 10%; E1 2 x max(5.476, 6.623) = 13.25 -> 14%; E2 2 x max(6.014, 6.731) = 13.46 -> 14%; E3 2 x max(2.153, 2.321) = 4.64 -> 5%; E4 2 x max(4.473, 4.628) = 9.26 -> 10%; watts 2 x max(0.2794, 0.2607, SD_rep 0.08373) -> 0.56 W
- aifoundry1 card 0: T1 2 x max(4.723, 5.135) = 10.27 -> 11%; T2 2 x max(6.050, 7.523) = 15.05 -> 16%; T3 2 x max(4.723, 5.135) = 10.27 -> 11%; E1 2 x max(5.476, 5.417) = 10.95 -> 11%; E2 2 x max(6.014, 6.153) = 12.31 -> 13%; E3 2 x max(2.153, 1.919) = 4.31 -> 5%; E4 2 x max(4.473, 4.673) = 9.35 -> 10%; watts 2 x max(0.2794, None, SD_rep 0.11509) -> 0.56 W
- **Part S:** Q218's P1-P4 for MM1-v3.1 + the counts against N on group S, pooled over both cards: P1 rms(Q1) < N's; P2 the exact two-sided sign test on d = |e_N| - |e_V| per case, a tie when |d| < 0.01, holds when p < 0.05 and MM1-v3.1 is closer in more; P3 rms(Q2) < N's; P4 P2's test on Q2 (ties |d| < 0.01 of D). PART S PASSES when P1-P4 hold; NOT DECIDED when either sign test has fewer than 6 untied cases; else FAILS (named).
- **Verdict:** PASS when part A and part S pass; FAIL when either fails (named); NOT DECIDED otherwise. Decided by scripts/s03_score.py (hashed before the read). The comparisons (section d) are verdicts of their own, never part of PASS.

## g. Earlier reads of E214, disclosed
- **data lanes (read every E214 measurement)**:
  - data-e214 (Q220): rsynced each released session read-only, checked it (C0-C9, W), reduced it with the registered reducer, committed it
  - verify-e214d (Q220): re-derived every session from its raw files (183,450 numeric leaves)
  - fix-e214d (Q220): dated note 1 in each data folder (the checker's planning line, a1c1-S1's die reference, check K's lines)
- **parser tests (raw host records, no model, no number reported)**:
  - kit-e215 (Q224), verify-e215, fix-e215, ready-e215: E215 kit's real-bytes desk test RB-E214 read the 4 committed card-1 sessions' 376 host stdouts (5,951 records) through the host-record parser; printed counts only (tools/claims-v3/e215/logs/realbytes-e215.txt)
- **never-run scans (configuration tokens only)**: E215's scans (fit-v31's e215_v31.py scan, reg-e215, verify-e215: "81,355 files, E214 included") and ready-e213b2's step 6n read E214's planned or committed arm names
- **named E214 without reading its data**:
  - reg-e214, verify-reg-e214, land-reg-e214 (Q220): the registration, before any E214 datum
  - counts-e214, verify-counts-e214 (Q225): arms.json and the tiles only: "No E214 measurement ... was read"
  - lnc-energy (Q225): "No E214 data file was read" (E214 holds no gemmLnc arm)
  - card-e213b2, ready-e213b2 (Q219): E214's kit folder by name (before any E214 session)
  - report-v2-draft (Q226): E214's run count and card-minutes from data-e214's result; E214's unread score PENDING
  - the orchestrator (CONTEXT 126-129, the Discussion, the status page): claims and releases (runs, card-minutes, no stop); no measurement
- **the model session (its own box)**: ran and reduced every E214 session and sealed its own forecasts (27bf4e19, 804e269b); its models are not scored here
- **search**: scripts/s01g_search.py over 10507 lane files (scripts, results, progress logs; card-e215 lanes and E215 data paths skipped): lanes naming an E214 data token: ['card-e213b2', 'counts-e214', 'data-e214', 'fix-e214d', 'kit-e215', 'land-reg-e214', 'lnc-energy', 'ready-e213b2', 'reg-e214', 'verify-counts-e214', 'verify-e214d', 'verify-reg-e214']
- **MM1 model lanes**: no MM1-v3.1 lane read E214 (section a2); MM1-v3 and MM1-v2 predate it. So, unlike Q218 (where MM1-v3's design lanes had tabulated some of E212's runs), no lane that shaped any of the three models read E214.

## The inputs, by sha256

| input | sha256 |
|---|---|
| MM1-v3.1 out/mm1_v31_params.json | `d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3` |
| MM1-v3.1 SHA256SUMS (work copy of 8bde0182, 64/64 OK) | `f6840d2de6617a739c30485904230e96b744b03b7c82c08b14b6de2d942528ed` |
| MM1-v3.1 counts/SHA256SUMS (3e8991d0, 71/71 OK) | `c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f` |
| MM1-v3 out/mm1_v3_params.json | `1fdc07496a39a5398021c2da0e60f157a2e7f693d845e039f8dc661f6aa325db` |
| MM1-v3 SHA256SUMS (170/170 OK) | `c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74` |
| MM1-v2 out/mm1_v2_params.json | `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5` |
| MM1-v2 SHA256SUMS (114/114 OK) | `eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2` |
| counts-e214 SHA256SUMS (land dir and work copy, 49/49 OK; verify-counts-e214 HOLDS) | `4c39d0d3cf4ad405d5d32d4128f828d0d39272aab8dc0c822a2eacbb49be664a` |
| E214 registration SHA256SUMS-e214-registration (91/91 OK) | `48ac51001faab305b7e2dc8dcb35502aa578df0ca74c1c47513fd3d0fdd73070` |
| work/step1/runs-listed.json | `c17c9ec1c2ae2b509008969cdbf3cf45c61379975e205fad97e4997569ebf224` |
| work/step1/models-step1.json | `e46cc791a6273a176852a37930885b982b60f278077bef8f4af34411d6e0615b` |
| work/step1/cells-v31.json | `52ca378bcf87f0323bada16b2bf3c9f2a5baeae0273b95b3861d06197784c3eb` |
| work/step1/cells-v3.json | `9afa9232492ee9b62eef78355205fdc97ec798bcbb7c8e8823cb724ece1f73da` |
| work/step1/bands.json | `7a362cef0006dd308b20c8e877d0f592843dc53cc3412f6b2192d01d71a882ce` |
| work/step1/twin-keys.json | `3418b7d8de1f0e07e765de8deb2486d44392788f83c7bb9159ff8230fb96893c` |
| work/step1/earlier-lanes.json | `057ab637e2c91a873306e356abcf69d08720a69baf3933666b7f26796566c7d1` |

**Order:** 1 this declaration (hashed) -> 2 the conditions and forecasts (hashed) -> the scorer s03_score.py hashed -> 3 the read and the scores (hashed); every sha256 and time in logs/progress.txt. No E215 datum is opened at any step.
