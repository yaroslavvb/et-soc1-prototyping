# MM1-v3's switch route on runs it never read in energy: the declaration (unread-e212sw, Q218, Wed 18 Nov 2026)

**Label: UNREAD.** MM1-v3 is frozen (landed b1493082; read here from GitHub main 8e91dda6, where its folder is unchanged and its `SHA256SUMS` checks 170 of 170). The switch counts it lacked are frozen too: fix-v31counts' folder, `SHA256SUMS` sha256 `c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f`, 71 of 71 files OK. The orchestrator posted that hash at 06:28:37 PST (#2.7.2.1.1); it supersedes the first version, 76ad5d97..., posted at 05:35:16 PST (#2.7.2.1). This file is written before this lane reads any power, energy or seconds of the runs below. **Not blind:** the data existed, data lanes had read them, and some MM1-v3 design lanes had tabulated some of them (section g).

The owner's words that set the matmul focus (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles." MM1 reports switches, and no card counts them. A card can check the count only through energy, when only the data changes (E210). This test asks whether MM1-v3's switch route, with no constant changed, prices data patterns whose energy it never saw.

**The order (each step's files hashed into the lane's log, with the time, before the next):** 1 this declaration; 2 the forecasts, made by MM1-v3's landed predictor unchanged (only the new count rows and the phi rule of section e added); 3 the read of the runs' measurements and the score, exactly as declared here.

## a. The runs

These are the committed runs whose kind MM1-v3 left NOT FORECAST in energy for want of a count, and which now have one. They are listed by run id from the registered schedules, the arms file, each committed session's `session/queue.json` and the registered point files. No measurement column was opened (`scripts/s01_list.py`, `work/step1/runs-listed.json`). MM1-v3's own `counts()` and `phi_of()` were called on each kind: every kind below returns no count (group A) or no phi (group B) in MM1-v3 as landed.

**Group A, the pass rule's pool.** There are 46 E212 runs in three sessions and 13 registered points of E206 and E207 (26 runs). E206's and E207's points are in MM1-v3's energy points, but the fit excludes them: `fit_v3.py` trains energy on `usable3` alone, and a point without a count or a phi is not usable. E212's pattern arms get no energy record at all (`data_v3.mms_runs`). The time of every one of them is in MM1-v3's time fit (time is kind-blind), and W given t uses the measured time.

| # | session | run | arm (registered) | format | kind | mask | share of D |
|---:|---|---|---|---|---|---|---|
| 1 | a1c1-S2 | `003-1x1x1-fp32-den4` | `1x1x1-fp32-den4` | fp32 | pattern:den4 | `0xffffffff` | yes |
| 2 | a1c1-S2 | `007-1x1x1-fp32-pow2` | `1x1x1-fp32-pow2` | fp32 | pattern:pow2 | `0xffffffff` | yes |
| 3 | a1c1-S2 | `008-1x1x1-fp32-den8` | `1x1x1-fp32-den8` | fp32 | pattern:den8 | `0xffffffff` | yes |
| 4 | a1c1-S2 | `009-1x1x1-fp32-lanes2` | `1x1x1-fp32-lanes2` | fp32 | pattern:lanes2 | `0xffffffff` | yes |
| 5 | a1c1-S2 | `010-1x1x1-fp32-fld_sign` | `1x1x1-fp32-fld_sign` | fp32 | pattern:fld_sign | `0xffffffff` | yes |
| 6 | a1c1-S2 | `012-1x1x1-fp32-den21-s16` | `1x1x1-fp32-den21-s16` | fp32 | pattern:den21 | `0xffff` | yes |
| 7 | a1c1-S2 | `016-1x1x1-fp32-fld_mant-s16` | `1x1x1-fp32-fld_mant-s16` | fp32 | pattern:fld_mant | `0xffff` | yes |
| 8 | a1c1-S2 | `017-1x1x1-fp32-den16-s16` | `1x1x1-fp32-den16-s16` | fp32 | pattern:den16 | `0xffff` | yes |
| 9 | a1c1-S2 | `061-1x1x1-int8-i8_den6` | `1x1x1-int8-i8_den6` | int8 | pattern:i8_den6 | `0xffffffff` | yes |
| 10 | a1c1-S2 | `062-1x1x1-int8-i8_den3` | `1x1x1-int8-i8_den3` | int8 | pattern:i8_den3 | `0xffffffff` | yes |
| 11 | a1c1-S2 | `064-1x1x1-int8-i8_pm1` | `1x1x1-int8-i8_pm1` | int8 | pattern:i8_pm1 | `0xffffffff` | yes |
| 12 | a1c1-S2 | `065-1x1x1-int8-i8_den1` | `1x1x1-int8-i8_den1` | int8 | pattern:i8_den1 | `0xffffffff` | yes |
| 13 | a1c1-S2 | `068-1x1x1-fp16-fld16_mant` | `1x1x1-fp16-fld16_mant` | fp16 | pattern:fld16_mant | `0xffffffff` | yes |
| 14 | a1c1-S2 | `069-1x1x1-fp16-den16_4` | `1x1x1-fp16-den16_4` | fp16 | pattern:den16_4 | `0xffffffff` | yes |
| 15 | a1c1-S2 | `071-1x1x1-fp16-den16_10` | `1x1x1-fp16-den16_10` | fp16 | pattern:den16_10 | `0xffffffff` | yes |
| 16 | a1c1-S2 | `072-1x1x1-fp16-fld16_sign` | `1x1x1-fp16-fld16_sign` | fp16 | pattern:fld16_sign | `0xffffffff` | yes |
| 17 | a1c1-S2 | `073-1x1x1-fp16-fld16_exp` | `1x1x1-fp16-fld16_exp` | fp16 | pattern:fld16_exp | `0xffffffff` | yes |
| 18 | a1c1-S3 | `004-1x1x1-fp32-fld_sign` | `1x1x1-fp32-fld_sign` | fp32 | pattern:fld_sign | `0xffffffff` | yes |
| 19 | a1c1-S3 | `005-1x1x1-fp32-lanes2` | `1x1x1-fp32-lanes2` | fp32 | pattern:lanes2 | `0xffffffff` | yes |
| 20 | a1c1-S3 | `006-1x1x1-fp32-den8` | `1x1x1-fp32-den8` | fp32 | pattern:den8 | `0xffffffff` | yes |
| 21 | a1c1-S3 | `007-1x1x1-fp32-pow2` | `1x1x1-fp32-pow2` | fp32 | pattern:pow2 | `0xffffffff` | yes |
| 22 | a1c1-S3 | `010-1x1x1-fp32-den4` | `1x1x1-fp32-den4` | fp32 | pattern:den4 | `0xffffffff` | yes |
| 23 | a1c1-S3 | `011-1x1x1-fp32-den16-s16` | `1x1x1-fp32-den16-s16` | fp32 | pattern:den16 | `0xffff` | yes |
| 24 | a1c1-S3 | `012-1x1x1-fp32-fld_mant-s16` | `1x1x1-fp32-fld_mant-s16` | fp32 | pattern:fld_mant | `0xffff` | yes |
| 25 | a1c1-S3 | `016-1x1x1-fp32-den21-s16` | `1x1x1-fp32-den21-s16` | fp32 | pattern:den21 | `0xffff` | yes |
| 26 | a1c1-S3 | `021-4x8x8-fp32-fld_sign` | `4x8x8-fp32-fld_sign` | fp32 | pattern:fld_sign | `0xffffffff` | yes |
| 27 | a1c1-S3 | `022-4x8x8-fp32-den8` | `4x8x8-fp32-den8` | fp32 | pattern:den8 | `0xffffffff` | yes |
| 28 | a1c1-S3 | `055-1x1x1-fp16-fld16_exp` | `1x1x1-fp16-fld16_exp` | fp16 | pattern:fld16_exp | `0xffffffff` | yes |
| 29 | a1c1-S3 | `056-1x1x1-fp16-fld16_sign` | `1x1x1-fp16-fld16_sign` | fp16 | pattern:fld16_sign | `0xffffffff` | yes |
| 30 | a1c1-S3 | `057-1x1x1-fp16-den16_10` | `1x1x1-fp16-den16_10` | fp16 | pattern:den16_10 | `0xffffffff` | yes |
| 31 | a1c1-S3 | `059-1x1x1-fp16-den16_4` | `1x1x1-fp16-den16_4` | fp16 | pattern:den16_4 | `0xffffffff` | yes |
| 32 | a1c1-S3 | `060-1x1x1-fp16-fld16_mant` | `1x1x1-fp16-fld16_mant` | fp16 | pattern:fld16_mant | `0xffffffff` | yes |
| 33 | a1c1-S3 | `063-1x1x1-int8-i8_den1` | `1x1x1-int8-i8_den1` | int8 | pattern:i8_den1 | `0xffffffff` | yes |
| 34 | a1c1-S3 | `064-1x1x1-int8-i8_pm1` | `1x1x1-int8-i8_pm1` | int8 | pattern:i8_pm1 | `0xffffffff` | yes |
| 35 | a1c1-S3 | `066-1x1x1-int8-i8_den3` | `1x1x1-int8-i8_den3` | int8 | pattern:i8_den3 | `0xffffffff` | yes |
| 36 | a1c1-S3 | `067-1x1x1-int8-i8_den6` | `1x1x1-int8-i8_den6` | int8 | pattern:i8_den6 | `0xffffffff` | yes |
| 37 | a1c1-S3 | `073-1x1x1-fp32-fp16grid-s16` | `1x1x1-fp32-fp16grid-s16` | fp32 | pattern:fp16grid | `0xffff` | yes |
| 38 | a1c1-S3 | `074-1x1x1-fp32-bf16trunc` | `1x1x1-fp32-bf16trunc` | fp32 | pattern:bf16trunc | `0xffffffff` | yes |
| 39 | a2c0-S2 | `003-4x8x8-fp32-fld_sign` | `4x8x8-fp32-fld_sign` | fp32 | pattern:fld_sign | `0xffffffff` | yes |
| 40 | a2c0-S2 | `007-4x8x8-fp32-lanes2` | `4x8x8-fp32-lanes2` | fp32 | pattern:lanes2 | `0xffffffff` | yes |
| 41 | a2c0-S2 | `008-4x8x8-fp32-den4` | `4x8x8-fp32-den4` | fp32 | pattern:den4 | `0xffffffff` | yes |
| 42 | a2c0-S2 | `009-4x8x8-fp32-den8` | `4x8x8-fp32-den8` | fp32 | pattern:den8 | `0xffffffff` | yes |
| 43 | a2c0-S2 | `011-1x1x1-fp32-fld_sign` | `1x1x1-fp32-fld_sign` | fp32 | pattern:fld_sign | `0xffffffff` | NOT SCORED (no random in the session at this configuration) |
| 44 | a2c0-S2 | `012-1x1x1-fp32-lanes2` | `1x1x1-fp32-lanes2` | fp32 | pattern:lanes2 | `0xffffffff` | NOT SCORED (no random in the session at this configuration) |
| 45 | a2c0-S2 | `015-1x1x1-fp32-lanes2-s16` | `1x1x1-fp32-lanes2-s16` | fp32 | pattern:lanes2 | `0xffff` | yes |
| 46 | a2c0-S2 | `018-1x1x1-fp32-fld_sign-s16` | `1x1x1-fp32-fld_sign-s16` | fp32 | pattern:fld_sign | `0xffff` | yes |

| # | experiment | card | point | arm | format | kind | runs | share of D |
|---:|---|---|---|---|---|---|---|---|
| 1 | E206 arm A | aifoundry3 card 0 | p112 | `gemmL1x1x1` | fp16 | real | `104-pass1-p112`, `138-pass2-p112` | NOT SCORED (no zeros point at this configuration) |
| 2 | E206 arm A | aifoundry3 card 0 | p113 | `gemmL2x4x2` | fp16 | real | `107-pass1-p113`, `135-pass2-p113` | NOT SCORED (no zeros point at this configuration) |
| 3 | E206 arm A | aifoundry3 card 0 | p114 | `gemmL1x1x1` | int8 | real | `118-pass1-p114`, `124-pass2-p114` | yes |
| 4 | E206 arm A | aifoundry3 card 0 | p115 | `gemmL2x4x1` | int8 | real | `108-pass1-p115`, `134-pass2-p115` | NOT SCORED (no zeros point at this configuration) |
| 5 | E206 arm B | aifoundry1 card 1 | p113 | `gemmL2x4x2` | fp16 | real | `098-pass1-p113`, `132-pass2-p113` | NOT SCORED (no zeros point at this configuration) |
| 6 | E206 arm B | aifoundry1 card 1 | p114 | `gemmL1x1x1` | int8 | real | `099-pass1-p114`, `131-pass2-p114` | yes |
| 7 | E206 arm B | aifoundry1 card 1 | p115 | `gemmL2x4x1` | int8 | real | `097-pass1-p115`, `133-pass2-p115` | NOT SCORED (no zeros point at this configuration) |
| 8 | E207 | aifoundry3 card 0 | b42 | `gemmL1x3x2` | fp32 | e37 | `052-pass1-b42`, `058-pass2-b42` | NOT SCORED (no zeros point at this configuration) |
| 9 | E207 | aifoundry3 card 0 | b43 | `gemmL3x5x5` | fp32 | e37 | `050-pass1-b43`, `060-pass2-b43` | NOT SCORED (no zeros point at this configuration) |
| 10 | E207 | aifoundry3 card 0 | b49 | `gemmL1x3x2` | fp32 | real:blind4 | `049-pass1-b49`, `061-pass2-b49` | NOT SCORED (no zeros point at this configuration) |
| 11 | E207 | aifoundry3 card 0 | b50 | `gemmL1x3x2` | fp16 | real:blind4 | `053-pass1-b50`, `057-pass2-b50` | NOT SCORED (no zeros point at this configuration) |
| 12 | E207 | aifoundry3 card 0 | b51 | `gemmL1x3x2` | int8 | real:blind4 | `054-pass1-b51`, `056-pass2-b51` | NOT SCORED (no zeros point at this configuration) |
| 13 | E207 | aifoundry3 card 0 | b52 | `gemmL3x5x5` | fp32 | designed:blind3 a_colconst_b_randn | `051-pass1-b52`, `059-pass2-b52` | NOT SCORED (no zeros point at this configuration) |

**Group B, REPORTED and outside the pass rule.** E206's fp32 real points (E206 arm A p110, E206 arm A p111, E206 arm B p111). Their count is E210's committed `real` row. MM1-v3 left them unpriced only because `phi_of()` has no rule for them, so they are priced here by the phi rule of section e.

**Group C, REPORTED and outside the pass rule.** These are E212's 7 gen-sparse50 runs (a1c0-S2 `062-2x4x1-int8-sparse50i`, a1c1-S3 `072-1x1x1-int8-sparse50i`, a1c1-S3 `075-1x1x1-fp32-sparse50f`, a1c1-S4 `069-2x4x4-fp32-sparse50f`, a1c1-S4 `073-2x4x1-int8-sparse50i`, a2c0-S4 `047-2x4x1-int8-sparse50i`, a2c0-S4 `050-2x4x4-fp32-sparse50f`). Each file is the lab's sparse50 tile as the pool's pair 0, and the rest of the pool is drawn by the sparse50 law. That makes them the committed sparse50 kind (the counts lane's reading), priced here as `sparse50` with its committed count, its phi and its gate. MM1-v3 read them for time only.

**Out of scope:** every other E212 run (random, zeros and ones, which MM1-v3 prices and fitted); E212 a2c0-S3 (it never ran); E213. No E213 data file is opened, and v31-counts found no E213 point NOT FORECAST in energy.

**Energy inclusion** (the data loaders' own rules, applied at the read): E212 as `data_v3.mms_runs`: the run ran, has a role, and its primary view has `T_op_us`, `cyc_op_max` and `n_launch` >= 1. It enters energy only when the view's `dP_w` is present, `p_mean_w` is set, the run is not capped and its role is not `time`. E206/E207 as `data_v3.e206_style`: a run is kept when its host record equals the registered point and its four readings are present, and the point is the mean of its kept runs. A listed run that fails is NOT SCORED, with the reason printed. **References for the share of D:** the random and zeros runs at the same (arm, format, mask) in the same session (E212), or the random and zeros points at the same (arm, format, mask) in the same experiment arm (E206/E207), under the same rules.

## b. The quantities

- **Q1, W over idle given the run's measured seconds**, as MM1-v3's README section 5 scores E212 a2c0-S4. Each model's W = A + B / t_meas comes from its predictor called at the run's card, arm, format, kind (priced as declared), mask and clock. The clock is E212's primary-view `kclock_mhz`, or 600 MHz for E206/E207 as `data_v3` sets it. The volts follow `data_v3`'s footings: aifoundry1 card 1 0.517 V; aifoundry3 0.522 V; the governed cards the primary view's minion mV, else `volts(card, f)`. The governed base is `G_of_f(card, f)`, and the die is `die_start_c` (50 C when absent). t_meas is the primary view's `T_op_us` (E212). E206/E207 points take their conditions and readings exactly as MM1-v3's own loader records them (`data_v3.energy_points()`): 600 MHz, the card footing's volts, G 0, t = mean `cycles_gemm` / ops / 600 MHz, w = mean(`p_work_w` - `p_rest_w`) and idle = mean `p_rest_w`. Their die is the kept runs' mean `die_start_c` for E206 arm B and E207; for E206 arm A it is none, so 50 C, as MM1-v3 records every arm-A point. **Error = W_fc / W_meas - 1** at W_meas >= 3 W, else the watts difference. W_meas is the primary view's `dP_w` (E212) or the loader's w (E206/E207).
- **Q2, the data-dependent power as a share of D**, E210's registered metric: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, with D = W_R - W_Z measured. W_R and W_Z are the means of the in-session reference runs. W_fc(R) is the same model's W given t at each reference run's own conditions, averaged. Reported in % of D, signed.
- REPORTED: **J at rest given t**, (P_rest + W_fc) / (P_rest + W_meas) - 1, with P_rest measured (E212 `p_mean_w` - `dP_w`; E206/E207 `p_rest_w`); **J over idle with the seconds forecast**, W_fc(t_fc) t_fc / (W_meas t_meas) - 1 at >= 3 W, where t_fc is MM1-v3's op time at the run's clock.

## c. The metric

- The **case** is E212's (card, arm, format, kind, mask) over the listed sessions, and its error is the mean of its runs' errors. For E206/E207 the registered point (the mean of its kept runs) is the case.
- Reported: rms % and signed mean %, per run (the full table) and per case. They are given per card, per format, per group (A, B, C) and pooled.
- **Configuration twins split.** A case is a twin when its time configuration (card, kernel, arm, format, mask, clock to 25 MHz) is among MM1-v3's priced energy points (`usable3`, E146 rungs out) with another kind. Every test kind is new to the energy fit by construction.
- **Also split by section g:** runs whose power an MM1-v3 design or spec lane tabulated before the freeze, and runs no such lane tabulated.

## d. The comparisons

- **V3**: MM1-v3 as landed, with its predictor unchanged. The frozen counts are added as data rows (fp32 at GEMM states into `E210C` S1/S2, fp16 and int8 into the switch table), and phi follows section e. No constant is changed and nothing is refitted.
- **N, the null of the pass rule**: each format's mean of the counted kinds on that card. W_N is the mean of MM1-v3's own W given t at the run's conditions over the counted kinds zeros, ones and random of the run's format. All three are measured at every test configuration in E212 and priced by MM1-v3. N has V3's base, so only the count's information differs.
- **N2, REPORTED**: the same over the ungated counted kinds (ones and random), a stricter null for ungated patterns.
- **V1, REPORTED**: MM1-v1 as frozen (25d2e74e; its folder checks 77 of 77), with its kind term where it applies. Its e_res and phi come from its own `kind_specs`: for E207, e37 from ledger v2 `fp32.small_int`, blind4 from M6 and blind3 from M5; for E206 real, ledger v2's real2 rows. Card footings are as V3's, and W = A + B / t_meas. **NOT FORECAST** where its e_res has no source: every E212 run (no ledger row and no frozen per-tile prediction for any plan tile or for sparse50) and E206 arm B (no card-1 real2 rows). E207's points are blind for MM1-v1. E206 arm A's were in MM1-v1's own in-sample scoring (its README: "E206's 6 real points scored, nothing fitted for the kind").
- **V3 with phi = 1, REPORTED**: every new kind at random's phi, to show the weight of rule e.

## e. phi for the new kinds (declared desk rule; values from tile bytes, `scripts/s01p_phi.py`, `work/step1/phi-declared.json`)

MM1-v3's `phi_of()` has no rule for these kinds. The rule is **MM1-v3's own formula**, `kinds_v3.phi(fmt, spec)`: MM1-v1's kind-term phi, phi_raw = (64 h(A) + 128 h(B)) / 192 with h = 0.70 rho / 0.5 + 0.30 tau / 0.5, divided by the format's randn generator's value. It is computed over each kind's tile files, one value per kind and the same at S1 and S2. The files are: E212 plan tiles, their registered file; E206 real, `kinds_v3.e206_kind`'s four real2 files; E207 real:blind4, its two files; blind3, its one file; e37, the generator `e37`. Every tile's sha256 was checked against the registration (E212) or the frozen counts' `tiles_sha256`, so phi and the count read the same bytes. Group C uses MM1-v3's own `phi_of('sparse50')`.

| format | kind | phi |
|---|---|---:|
| fp16 | pattern:den16_10 | 0.6489 |
| fp16 | pattern:den16_4 | 0.4719 |
| fp16 | pattern:fld16_exp | 0.3180 |
| fp16 | pattern:fld16_mant | 0.9863 |
| fp16 | pattern:fld16_sign | 0.4183 |
| fp16 | real | 0.9546 |
| fp16 | real:blind4 | 0.8211 |
| fp32 | designed:blind3 a_colconst_b_randn | 0.9178 |
| fp32 | e37 | 0.2729 |
| fp32 | pattern:bf16trunc | 0.5144 |
| fp32 | pattern:den16 | 0.5236 |
| fp32 | pattern:den21 | 0.5944 |
| fp32 | pattern:den4 | 0.3538 |
| fp32 | pattern:den8 | 0.4104 |
| fp32 | pattern:fld_mant | 1.0047 |
| fp32 | pattern:fld_sign | 0.3261 |
| fp32 | pattern:fp16grid | 0.6048 |
| fp32 | pattern:lanes2 | 0.3255 |
| fp32 | pattern:pow2 | 0.2479 |
| fp32 | pattern:sparse50f | 0.6001 |
| fp32 | real | 0.9718 |
| fp32 | real:blind4 | 0.5183 |
| int8 | pattern:i8_den1 | 0.2335 |
| int8 | pattern:i8_den3 | 0.3503 |
| int8 | pattern:i8_den6 | 0.5254 |
| int8 | pattern:i8_pm1 | 1.0488 |
| int8 | pattern:sparse50i | 0.5760 |
| int8 | real | 1.0535 |
| int8 | real:blind4 | 0.9750 |

## f. The pass rule (decided by `scripts/s03_score.py`, on group A's cases)

- **P1**: rms of V3's Q1 error < rms of N's, over the group A cases with Q1 (W_meas >= 3 W).
- **P2**: the exact two-sided sign test on Q1 per case. d = |e_N| - |e_V3|, and |d| < 0.01 (1 percentage point) is a tie, dropped. It holds when p < 0.05 and V3 is closer on more of the non-tied cases.
- **P3**: rms of V3's Q2 error (% of D) < rms of N's, over the group A cases with Q2.
- **P4**: the P2 test on Q2, with ties |d| < 0.01 of D.
- **Verdict: PASS** when P1-P4 all hold. **NOT DECIDED** when either sign test has fewer than 6 non-tied cases. Otherwise **FAIL**, with the failing conditions named. The same four are REPORTED against N2 and V1 (where V1 applies), and for E212 and E206/E207 apart. None of those enters the verdict.

## g. Earlier lanes that read these runs' energy (searched: every `OUT/<lane>/scripts/**`, `result.json` and `result.md`, and every text file of MM1-v3's design and build lanes; 9,861 files, 94 lanes with a token; `scripts/s01g_search.py`, `work/step1/earlier-lanes.json`; what each read was checked by code reads and by reads with every digit masked, `scripts/s01h_context.py`)

**MM1-v3's own design lanes (Q214, before its freeze):**
- **v3-design-c** (about 14:16 PST Tue 17 Nov; `ana1_kinds.py` on E208 and E212 at LAB 7dfba40b) printed, per card, shape and format, the W over idle and the share of D, (W - zeros) / D, of **14 group A runs**: E212 a1c1-S2's full-chip pattern runs 003, 007, 008, 009, 010 (fp32), 068, 069, 071, 072, 073 (fp16), and 061, 062, 064, 065 (int8). It printed the same for **3 group C runs** (a1c0-S2 062, a1c1-S4 069 and 073), all into `work/ana1.json`. Its `ana2_e206_cards.py` tabulated E206 points p111, p113, p114 and p115 (arm A and arm B W over idle), which are **group A points p113-p115 and group B p111**.
- **v3-spec** (about 14:40 PST Tue 17 Nov; `s02_v2_unread_e212.py`) wrote the measured `dP_w` of 43 pattern-kind runs into `work/s02/v2_unread_e212.csv`, without scoring them: **all 38 group A runs of a1c1-S2 and a1c1-S3**, and group C's a1c1-S3 (2), a1c1-S4 (2) and a1c0-S2 (1).
- **mm1-v3** wrote the measured W of the 16 E206/E207 points it could not price (**groups A and B**) into its committed `out/points_energy_v3.csv`. No fit used them (`usable3`). Its E212 records give pattern runs no energy. MM1-v3's unread files (`out/unread_v2_e212_*`, `out/unread_v3_e212s4_*`) hold no pattern run's power (checked: 0 non-empty).
- **Not tabulated by any MM1-v3 design or spec lane:** E212 a2c0-S2's **8 group A runs** (committed after those lanes ran) and a2c0-S4's 2 group C runs. E207's points were read by the residual and scoring lanes below, not by MM1-v3's design lanes as far as the search shows.

**Data, scoring and other lanes:**
- E212: **data-e212** and **data-e212 (Q208c)** reduced every run with the registered reducer (power included) and committed them. **verify-e212d** re-derived every numeric leaf of 709 runs. **fix-e212d** read every run's rest power and die for its dated notes (`posthoc_note1_e212.py`). The **model session** ran E212 and holds its data; its own v3.2 seal (8f2df483, registered a1602b0d) forecast those sessions before they ran.
- E206 arm A (aifoundry3): **card-e206a**'s step-13 scorer, **verify-e206d**, **scores-e206**, **mm1v0-e206** (MM1-v0 blind), **mm-data** and **mm1-v1** (its in-sample energy scoring with the 6 real points). **sw-design-a/-b** and **reg-e210** used p110's measured energy (fp32 real, group B) as one of E210's committed calibration kinds, and **verify-e210** checked it.
- E206 arm B (aifoundry1 card 1): **card-e206b2**'s scorer, **verify-e206bd** (MM1-v0/v1 blind on arm B) and **scores-e206b**.
- E207 (aifoundry3): **card-e207**'s step-13 scorer (E1-E4 joules per point), **verify-e207d**, **scores-e207**, **score-v2-e207** (MM1-v2 blind, which priced none of b49-b52), **mm-residuals** (pooled residuals incl. the real and pattern kinds) and **report-final/-critic/-verify/-fix** (the public matmul report).
- v31-counts, verify-v31counts and fix-v31counts read E212's run records for arms and sessions only (their README section 6), and opened no energy.
- Older lanes with a matching token (E78, E80-E84, E115, E127, E137-E142 and earlier) predate these runs, so their hits are the same tile names in other experiments.

## What this cannot say (stated before the read)

- It is not a blind test. The model's constants never saw these runs' energy, but its form was chosen by a panel, one of whose lanes had printed 14 of the 46 E212 runs' shares of D, and its spec lane had tabulated 38 of them. The a2c0-S2 split is the cleanest part.
- It scores energy through the switch count, not the count itself: no card counts switches.
- E212's pattern runs sit on three shapes (`gemmL1x1x1` at 32 and 16 shires, `gemmL4x8x8`) and two cards. fp16 and int8 run on card 1 only.
- fp16's count is estimated (RTL x the fp32 gate/RTL ratio), and int8's leaves out its arithmetic (m_int8 carries it). fp16/int8 counts are at launch points, not GEMM states.
- phi is a desk rule, never checked on a card's line order.

Interpreter for every number: `/usr/bin/python3` 3.12.3 (`-I -B`), numpy 1.26.4, single-threaded, inside the round's CPU slot. Machine-readable: `declared-unread.json`.
