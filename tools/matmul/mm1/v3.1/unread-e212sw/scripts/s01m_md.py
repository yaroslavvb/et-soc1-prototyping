#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1m: DECLARED-unread.md from declared-unread.json (tables) and the text below. Desk.
Run: /usr/bin/python3 -I -B s01m_md.py <lane dir>
"""
import json
import os
import sys

L = os.path.abspath(sys.argv[1])
D = json.load(open(os.path.join(L, 'declared-unread.json')))
A = D['a_runs']['group_A_pass_rule_pool']
B = D['a_runs']['group_B_reported_phi_only']
C = D['a_runs']['group_C_reported_sparse50']
phi = D['e_phi']['values']
o = []
w = o.append
w('# MM1-v3\'s switch route on runs it never read in energy: the declaration (unread-e212sw, Q218, Wed 18 Nov 2026)')
w('')
w('**Label: UNREAD.** MM1-v3 is frozen (landed b1493082; read here from GitHub main 8e91dda6, where its folder is unchanged and its '
  '`SHA256SUMS` checks 170 of 170). The switch counts it lacked are frozen too: fix-v31counts\' folder, `SHA256SUMS` sha256 '
  '`c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f`, 71 of 71 files OK. The orchestrator posted that hash at 06:28:37 PST '
  '(#2.7.2.1.1); it supersedes the first version, 76ad5d97..., posted at 05:35:16 PST (#2.7.2.1). This file is written before this lane '
  'reads any power, energy or seconds of the runs below. **Not blind:** the data existed, data lanes had read them, and some MM1-v3 design '
  'lanes had tabulated some of them (section g).')
w('')
w('The owner\'s words that set the matmul focus (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want to have a '
  'model which predicts matte mold energy and number of transistor switches and clock cycles." MM1 reports switches, and no card counts them. '
  'A card can check the count only through energy, when only the data changes (E210). This test asks whether MM1-v3\'s switch route, with no '
  'constant changed, prices data patterns whose energy it never saw.')
w('')
w('**The order (each step\'s files hashed into the lane\'s log, with the time, before the next):** 1 this declaration; 2 the forecasts, made by MM1-v3\'s '
  'landed predictor unchanged (only the new count rows and the phi rule of section e added); 3 the read of the runs\' measurements and the '
  'score, exactly as declared here.')
w('')
w('## a. The runs')
w('')
w('These are the committed runs whose kind MM1-v3 left NOT FORECAST in energy for want of a count, and which now have one. They are listed by run id '
  'from the registered schedules, the arms file, each committed session\'s `session/queue.json` and the registered point files. No measurement column was opened '
  '(`scripts/s01_list.py`, `work/step1/runs-listed.json`). MM1-v3\'s own `counts()` and `phi_of()` were called on each kind: every kind below '
  'returns no count (group A) or no phi (group B) in MM1-v3 as landed.')
w('')
w('**Group A, the pass rule\'s pool.** There are %d E212 runs in three sessions and %d registered points of E206 and E207 (%d runs). E206\'s and '
  'E207\'s points are in MM1-v3\'s energy points, but the fit excludes them: `fit_v3.py` trains energy on `usable3` alone, and a point without a count or a phi is not usable. '
  'E212\'s pattern arms get no energy record at all (`data_v3.mms_runs`). The time of every one of them is in MM1-v3\'s time fit (time is '
  'kind-blind), and W given t uses the measured time.' % (A['counts']['e212_runs'], A['counts']['e206_e207_points'], A['counts']['e206_e207_runs']))
w('')
w('| # | session | run | arm (registered) | format | kind | mask | share of D |')
w('|---:|---|---|---|---|---|---|---|')
for i, r in enumerate(A['e212_runs'], 1):
    w(f"| {i} | {r['session']} | `{r['run']}` | `{r['arm_label']}` | {r['fmt']} | {r['kind']} | `{r['mask']}` | "
      f"{'yes' if r['share_of_D'] else 'NOT SCORED (no random in the session at this configuration)'} |")
w('')
w('| # | experiment | card | point | arm | format | kind | runs | share of D |')
w('|---:|---|---|---|---|---|---|---|---|')
for i, r in enumerate(A['e206_e207_points'], 1):
    miss = [k for k in ('random', 'zeros') if k not in r['refs']]
    w(f"| {i} | {r['exp']}{(' arm ' + r['exp_arm']) if r['exp'] == 'E206' else ''} | {r['card']} | {r['point']} | `{r['arm']}` | {r['fmt']} | "
      f"{r['kind']} | {', '.join('`' + x + '`' for x in r['runs'])} | {'yes' if r['share_of_D'] else 'NOT SCORED (no ' + ' or '.join(miss) + ' point at this configuration)'} |")
w('')
w('**Group B, REPORTED and outside the pass rule.** E206\'s fp32 real points (%s). Their count is E210\'s committed `real` row. MM1-v3 left '
  'them unpriced only because `phi_of()` has no rule for them, so they are priced here by the phi rule of section e.' %
  ', '.join(f"{r['exp']} arm {r['exp_arm']} {r['point']}" for r in B['e206_points']))
w('')
w('**Group C, REPORTED and outside the pass rule.** These are E212\'s %d gen-sparse50 runs (%s). Each file is the lab\'s sparse50 tile as the pool\'s pair 0, and the rest of the '
  'pool is drawn by the sparse50 law. That makes them the committed sparse50 kind (the counts lane\'s reading), priced here as `sparse50` with its committed count, its phi and '
  'its gate. MM1-v3 read them for time only.' % (len(C['e212_runs']), ', '.join(f"{r['session']} `{r['run']}`" for r in C['e212_runs'])))
w('')
w('**Out of scope:** every other E212 run (random, zeros and ones, which MM1-v3 prices and fitted); E212 a2c0-S3 (it never ran); E213. No E213 data '
  'file is opened, and v31-counts found no E213 point NOT FORECAST in energy.')
w('')
w('**Energy inclusion** (the data loaders\' own rules, applied at the read): E212 as `data_v3.mms_runs`: the run ran, has a role, and its primary view has '
  '`T_op_us`, `cyc_op_max` and `n_launch` >= 1. It enters energy only when the view\'s `dP_w` is present, `p_mean_w` is set, the run is not capped and its role '
  'is not `time`. E206/E207 as `data_v3.e206_style`: a run is kept when its host record equals the registered point and its four readings are present, and the point is the mean of '
  'its kept runs. A listed run that fails is NOT SCORED, with the reason printed. **References for the share of D:** the random and zeros runs at the same '
  '(arm, format, mask) in the same session (E212), or the random and zeros points at the same (arm, format, mask) in the same experiment arm (E206/E207), '
  'under the same rules.')
w('')
w('## b. The quantities')
w('')
w('- **Q1, W over idle given the run\'s measured seconds**, as MM1-v3\'s README section 5 scores E212 a2c0-S4. Each model\'s W = A + B / t_meas comes from its '
  'predictor called at the run\'s card, arm, format, kind (priced as declared), mask and clock. The clock is E212\'s primary-view `kclock_mhz`, or 600 MHz for E206/E207 as '
  '`data_v3` sets it. The volts follow `data_v3`\'s footings: aifoundry1 card 1 0.517 V; aifoundry3 0.522 V; the governed cards the primary view\'s minion mV, else '
  '`volts(card, f)`. The governed base is `G_of_f(card, f)`, and the die is `die_start_c` (50 C when absent). t_meas is the primary view\'s `T_op_us` (E212). '
  'E206/E207 points take their conditions and readings exactly as MM1-v3\'s own loader records them (`data_v3.energy_points()`): 600 MHz, the card footing\'s volts, '
  'G 0, t = mean `cycles_gemm` / ops / 600 MHz, w = mean(`p_work_w` - `p_rest_w`) and idle = mean `p_rest_w`. Their die is the kept runs\' mean `die_start_c` '
  'for E206 arm B and E207; for E206 arm A it is none, so 50 C, as MM1-v3 records every arm-A point. **Error = W_fc / W_meas - 1** at W_meas >= 3 W, else the '
  'watts difference. W_meas is the primary view\'s `dP_w` (E212) or the loader\'s w (E206/E207).')
w('- **Q2, the data-dependent power as a share of D**, E210\'s registered metric: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, with D = W_R - W_Z '
  'measured. W_R and W_Z are the means of the in-session reference runs. W_fc(R) is the same model\'s W given t at each reference run\'s own conditions, '
  'averaged. Reported in % of D, signed.')
w('- REPORTED: **J at rest given t**, (P_rest + W_fc) / (P_rest + W_meas) - 1, with P_rest measured (E212 `p_mean_w` - `dP_w`; E206/E207 `p_rest_w`); '
  '**J over idle with the seconds forecast**, W_fc(t_fc) t_fc / (W_meas t_meas) - 1 at >= 3 W, where t_fc is MM1-v3\'s op time at the run\'s clock.')
w('')
w('## c. The metric')
w('')
w('- The **case** is E212\'s (card, arm, format, kind, mask) over the listed sessions, and its error is the mean of its runs\' errors. For E206/E207 the registered '
  'point (the mean of its kept runs) is the case.')
w('- Reported: rms % and signed mean %, per run (the full table) and per case. They are given per card, per format, per group (A, B, C) and pooled.')
w('- **Configuration twins split.** A case is a twin when its time configuration (card, kernel, arm, format, mask, clock to 25 MHz) is among '
  'MM1-v3\'s priced energy points (`usable3`, E146 rungs out) with another kind. Every test kind is new to the energy fit by construction.')
w('- **Also split by section g:** runs whose power an MM1-v3 design or spec lane tabulated before the freeze, and runs no such lane tabulated.')
w('')
w('## d. The comparisons')
w('')
w('- **V3**: MM1-v3 as landed, with its predictor unchanged. The frozen counts are added as data rows (fp32 at GEMM states into `E210C` S1/S2, fp16 and int8 '
  'into the switch table), and phi follows section e. No constant is changed and nothing is refitted.')
w('- **N, the null of the pass rule**: each format\'s mean of the counted kinds on that card. W_N is the mean of MM1-v3\'s own W given t at the run\'s conditions '
  'over the counted kinds zeros, ones and random of the run\'s format. All three are measured at every test configuration in E212 and priced by MM1-v3. '
  'N has V3\'s base, so only the count\'s information differs.')
w('- **N2, REPORTED**: the same over the ungated counted kinds (ones and random), a stricter null for ungated patterns.')
w('- **V1, REPORTED**: MM1-v1 as frozen (25d2e74e; its folder checks 77 of 77), with its kind term where it applies. Its e_res and phi come from its own '
  '`kind_specs`: for E207, e37 from ledger v2 `fp32.small_int`, blind4 from M6 and blind3 from M5; for E206 real, ledger v2\'s real2 rows. Card footings are as V3\'s, '
  'and W = A + B / t_meas. **NOT FORECAST** where its e_res has no source: every E212 run (no ledger row and no frozen per-tile prediction for any plan '
  'tile or for sparse50) and E206 arm B (no card-1 real2 rows). E207\'s points are blind for MM1-v1. E206 arm A\'s were in MM1-v1\'s own '
  'in-sample scoring (its README: "E206\'s 6 real points scored, nothing fitted for the kind").')
w('- **V3 with phi = 1, REPORTED**: every new kind at random\'s phi, to show the weight of rule e.')
w('')
w('## e. phi for the new kinds (declared desk rule; values from tile bytes, `scripts/s01p_phi.py`, `work/step1/phi-declared.json`)')
w('')
w('MM1-v3\'s `phi_of()` has no rule for these kinds. The rule is **MM1-v3\'s own formula**, `kinds_v3.phi(fmt, spec)`: MM1-v1\'s kind-term phi, phi_raw = '
  '(64 h(A) + 128 h(B)) / 192 with h = 0.70 rho / 0.5 + 0.30 tau / 0.5, divided by the format\'s randn generator\'s value. It is computed over each kind\'s tile files, one value '
  'per kind and the same at S1 and S2. The files are: E212 plan tiles, their registered file; E206 real, `kinds_v3.e206_kind`\'s four real2 files; E207 real:blind4, its '
  'two files; blind3, its one file; e37, the generator `e37`. Every tile\'s sha256 was checked against the registration (E212) or the frozen counts\' '
  '`tiles_sha256`, so phi and the count read the same bytes. Group C uses MM1-v3\'s own `phi_of(\'sparse50\')`.')
w('')
w('| format | kind | phi |')
w('|---|---|---:|')
for k, v in sorted(phi.items()):
    f, kd = k.split('|', 1)
    w(f'| {f} | {kd} | {v:.4f} |')
w('')
w('## f. The pass rule (decided by `scripts/s03_score.py`, on group A\'s cases)')
w('')
w('- **P1**: rms of V3\'s Q1 error < rms of N\'s, over the group A cases with Q1 (W_meas >= 3 W).')
w('- **P2**: the exact two-sided sign test on Q1 per case. d = |e_N| - |e_V3|, and |d| < 0.01 (1 percentage point) is a tie, dropped. It holds when p < 0.05 '
  'and V3 is closer on more of the non-tied cases.')
w('- **P3**: rms of V3\'s Q2 error (% of D) < rms of N\'s, over the group A cases with Q2.')
w('- **P4**: the P2 test on Q2, with ties |d| < 0.01 of D.')
w('- **Verdict: PASS** when P1-P4 all hold. **NOT DECIDED** when either sign test has fewer than 6 non-tied cases. Otherwise **FAIL**, with the failing '
  'conditions named. The same four are REPORTED against N2 and V1 (where V1 applies), and for E212 and E206/E207 apart. None of those enters the verdict.')
w('')
w('## g. Earlier lanes that read these runs\' energy (searched: every `OUT/<lane>/scripts/**`, `result.json` and `result.md`, and every text '
  'file of MM1-v3\'s design and build lanes; 9,861 files, 94 lanes with a token; `scripts/s01g_search.py`, `work/step1/earlier-lanes.json`; what each read '
  'was checked by code reads and by reads with every digit masked, `scripts/s01h_context.py`)')
w('')
w('**MM1-v3\'s own design lanes (Q214, before its freeze):**')
w('- **v3-design-c** (about 14:16 PST Tue 17 Nov; `ana1_kinds.py` on E208 and E212 at LAB 7dfba40b) printed, per card, shape and format, the W over idle and the '
  'share of D, (W - zeros) / D, of **14 group A runs**: E212 a1c1-S2\'s full-chip pattern runs 003, 007, 008, 009, 010 (fp32), 068, 069, 071, 072, 073 (fp16), and '
  '061, 062, 064, 065 (int8). It printed the same for **3 group C runs** (a1c0-S2 062, a1c1-S4 069 and 073), all into `work/ana1.json`. Its `ana2_e206_cards.py` tabulated '
  'E206 points p111, p113, p114 and p115 (arm A and arm B W over idle), which are **group A points p113-p115 and group B p111**.')
w('- **v3-spec** (about 14:40 PST Tue 17 Nov; `s02_v2_unread_e212.py`) wrote the measured `dP_w` of 43 pattern-kind runs into `work/s02/v2_unread_e212.csv`, '
  'without scoring them: **all 38 group A runs of a1c1-S2 and a1c1-S3**, and group C\'s a1c1-S3 (2), a1c1-S4 (2) and a1c0-S2 (1).')
w('- **mm1-v3** wrote the measured W of the 16 E206/E207 points it could not price (**groups A and B**) into its committed `out/points_energy_v3.csv`. '
  'No fit used them (`usable3`). Its E212 records give pattern runs no energy. MM1-v3\'s unread files (`out/unread_v2_e212_*`, `out/unread_v3_e212s4_*`) '
  'hold no pattern run\'s power (checked: 0 non-empty).')
w('- **Not tabulated by any MM1-v3 design or spec lane:** E212 a2c0-S2\'s **8 group A runs** (committed after those lanes ran) and a2c0-S4\'s 2 group C runs. '
  'E207\'s points were read by the residual and scoring lanes below, not by MM1-v3\'s design lanes as far as the search shows.')
w('')
w('**Data, scoring and other lanes:**')
w('- E212: **data-e212** and **data-e212 (Q208c)** reduced every run with the registered reducer (power included) and committed them. **verify-e212d** '
  're-derived every numeric leaf of 709 runs. **fix-e212d** read every run\'s rest power and die for its dated notes (`posthoc_note1_e212.py`). The **model '
  'session** ran E212 and holds its data; its own v3.2 seal (8f2df483, registered a1602b0d) forecast those sessions before they ran.')
w('- E206 arm A (aifoundry3): **card-e206a**\'s step-13 scorer, **verify-e206d**, **scores-e206**, **mm1v0-e206** (MM1-v0 blind), **mm-data** and **mm1-v1** (its '
  'in-sample energy scoring with the 6 real points). **sw-design-a/-b** and **reg-e210** used p110\'s measured energy (fp32 real, group B) as one of E210\'s committed '
  'calibration kinds, and **verify-e210** checked it.')
w('- E206 arm B (aifoundry1 card 1): **card-e206b2**\'s scorer, **verify-e206bd** (MM1-v0/v1 blind on arm B) and **scores-e206b**.')
w('- E207 (aifoundry3): **card-e207**\'s step-13 scorer (E1-E4 joules per point), **verify-e207d**, **scores-e207**, **score-v2-e207** (MM1-v2 blind, which priced '
  'none of b49-b52), **mm-residuals** (pooled residuals incl. the real and pattern kinds) and **report-final/-critic/-verify/-fix** (the public matmul report).')
w('- v31-counts, verify-v31counts and fix-v31counts read E212\'s run records for arms and sessions only (their README section 6), and opened no energy.')
w('- Older lanes with a matching token (E78, E80-E84, E115, E127, E137-E142 and earlier) predate these runs, so their hits are the same tile names in other experiments.')
w('')
w('## What this cannot say (stated before the read)')
w('')
w('- It is not a blind test. The model\'s constants never saw these runs\' energy, but its form was chosen by a panel, one of whose lanes had printed 14 of the 46 '
  'E212 runs\' shares of D, and its spec lane had tabulated 38 of them. The a2c0-S2 split is the cleanest part.')
w('- It scores energy through the switch count, not the count itself: no card counts switches.')
w('- E212\'s pattern runs sit on three shapes (`gemmL1x1x1` at 32 and 16 shires, `gemmL4x8x8`) and two cards. fp16 and int8 run on card 1 only.')
w('- fp16\'s count is estimated (RTL x the fp32 gate/RTL ratio), and int8\'s leaves out its arithmetic (m_int8 carries it). fp16/int8 counts are at launch '
  'points, not GEMM states.')
w('- phi is a desk rule, never checked on a card\'s line order.')
w('')
w('Interpreter for every number: `/usr/bin/python3` 3.12.3 (`-I -B`), numpy 1.26.4, single-threaded, inside the round\'s CPU slot. Machine-readable: '
  '`declared-unread.json`.')
open(os.path.join(L, 'DECLARED-unread.md'), 'w').write('\n'.join(o) + '\n')
print('wrote DECLARED-unread.md', len(o), 'lines')
