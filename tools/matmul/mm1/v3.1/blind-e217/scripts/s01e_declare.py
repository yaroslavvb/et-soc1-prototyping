#!/usr/bin/env python3
"""decl-e217 (Q228) step 1e: write DECLARED-blind-e217.md and DECLARED-blind-e217.json, the lab's BLIND test of its frozen models on E217
(the model session's fourth matmul sweep, 1119-mmsweep4, #13), declared before any E217 datum exists. Reads only this lane's step-1 files
(the registered arms and schedules, the models' records, the bands) and the orchestrator's records of E217's claims; writes the two files.
Run: /usr/bin/python3 -I -B s01e_declare.py <lane dir>"""
import collections
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
W = os.path.normpath(os.path.join(L, '..', '..'))
S1 = os.path.join(L, 'work', 'step1')
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
LNC = os.path.join(MM1, 'v3.2-terms', 'gemmlnc')
SRC = os.path.join(L, 'work', 'e217-src')
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
MS = json.load(open(os.path.join(S1, 'models-step1.json')))
BD = json.load(open(os.path.join(S1, 'bands.json')))
REL = open(os.path.join(W, 'out', 'orch', 'e217-releases.txt')).read()
REL_LINES = [x for x in REL.splitlines() if x.strip() and not x.startswith('# ')]   # '# ' is the file's header; '#13...' lines are posts
claim_files = sorted(f for f in os.listdir(os.path.join(W, 'out', 'orch')) if f.startswith('claim-'))
QUIET = os.path.exists(os.path.join(W, 'locks', 'quiet-desk-aifoundry2'))
R = RL['runs']
CASES = RL['cases']
C1, C0 = 'aifoundry1 card 1', 'aifoundry1 card 0'
DECLARED_AT = now()
cnt = RL['counts']
by_s = collections.Counter(r['session'] for r in R)
grp_tab = collections.Counter((c['card'], c['group_shape'], c['group_mask']) for c in CASES)
kind_tab = collections.Counter((c['card'], c['group_kind']) for c in CASES)
fmt_tab = collections.Counter((c['card'], c['fmt']) for c in CASES)
newk = cnt['new_kinds']
S_cases = [c for c in CASES if c['group_kind'] == 'S']
S_runs = [r for r in R if r['group_kind'] == 'S']
C_runs = [r for r in R if r['group_kind'] == 'C']
mg = cnt['mg_masks_by_card']
zs = MS['zero_structure']
GATE = {}
for t in ('gt125', 'gt25', 'gt875', 'h_gt25'):
    fmt = zs[t]['type']
    GATE[f'{fmt}|pattern:{t}'] = {'g_op': zs[t]['A_all_zero_row_share'], 'g_lane': 0.0, 'g8': 0.0,
                                  'A_all_zero_rows_of_16': int(round(16 * zs[t]['A_all_zero_row_share'])),
                                  'A_zero_share': zs[t]['A_zero_share'], 'B_zero_share': zs[t]['B_zero_share']}
bands = {card: {q: BD['cards'][card]['bands'][q]['band'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')} for card in (C1, C0)}
for card in (C1, C0):
    bands[card]['watts_W'] = BD['cards'][card]['band_w']['band_W']
    bands[card]['arithmetic'] = {q: BD['cards'][card]['bands'][q]['arithmetic'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
    bands[card]['arithmetic']['watts'] = BD['cards'][card]['band_w']['arithmetic']
ties = {card: BD['cards'][card]['ties'] for card in (C1, C0)}
assert BD['check_card1_all_equal'], 'card 1 bands differ from E215 arm B'

INPUTS = collections.OrderedDict()
INPUTS['E217 kit src copy: out/orch/e217-src/SRC-SHA256SUMS.txt (75/75 OK)'] = sha(os.path.join(SRC, 'SRC-SHA256SUMS.txt'))
INPUTS['E217 src/arms.json'] = sha(os.path.join(SRC, 'src', 'arms.json'))
for s in sorted(RL['sessions']):
    INPUTS[f'E217 src/sched/{s}.json'] = RL['sessions'][s]['sched_sha256']
INPUTS['MM1-v3.1 out/mm1_v31_params.json'] = sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))
INPUTS['MM1-v3.1 SHA256SUMS (2c971828; 64/64 OK)'] = sha(os.path.join(MM1, 'v3.1', 'SHA256SUMS'))
INPUTS['MM1-v3.1 counts/SHA256SUMS (3e8991d0; 71/71 OK)'] = sha(os.path.join(MM1, 'v3.1', 'counts', 'SHA256SUMS'))
INPUTS['MM1-v3 out/mm1_v3_params.json'] = sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))
INPUTS['MM1-v3 SHA256SUMS (b1493082; 170/170 OK)'] = sha(os.path.join(MM1, 'v3', 'SHA256SUMS'))
INPUTS['MM1-v2 out/mm1_v2_params.json'] = sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json'))
INPUTS['MM1-v2 SHA256SUMS (3ca4b717; 114/114 OK)'] = sha(os.path.join(MM1, 'v2', 'SHA256SUMS'))
INPUTS['contention term F1 (#1.29.1) forecast-e215-v31-layout.json'] = sha(os.path.join(LAY, 'forecast-e215-v31-layout.json'))
INPUTS['contention term F1 (#1.29.1) eval_layout.py'] = sha(os.path.join(LAY, 'eval_layout.py'))
INPUTS['contention term F1 (#1.29.1) features_layout.py'] = sha(os.path.join(LAY, 'features_layout.py'))
INPUTS['contention term F1 (#1.29.1) out/features_layout.json (the frozen walk cache)'] = sha(os.path.join(LAY, 'out', 'features_layout.json'))
INPUTS['contention term land SHA256SUMS (25 files, 25/25 OK)'] = sha(os.path.join(LAY, 'SHA256SUMS'))
INPUTS['gemmLnc term F3 (#1.29) term-gemmlnc.json'] = sha(os.path.join(LNC, 'term-gemmlnc.json'))
INPUTS["verify-lay's maker v02_fits.py (#1.29.1.1)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'))
INPUTS["verify-lay's fits record v02_fits.json (the controls' constants)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_fits.json'))
INPUTS["verify-lay's E215 control columns v02_e215_controls.csv (#1.29.1.1)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'))
INPUTS['counts-e214 SHA256SUMS (49/49 OK; no E217 tile is one of its tiles)'] = sha(os.path.join(L, 'work', 'counts-e214', 'SHA256SUMS'))
INPUTS['E215 rules_e215.py (the band form)'] = sha(os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e215', 'rules_e215.py'))
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json'):
    INPUTS[f'work/step1/{n}'] = sha(os.path.join(S1, n))
for n in ('s00_setup.sh', 's01_list.py', 's01b_models.py', 's01d_bands.py', 's01e_declare.py', 's02w_walk.py', 's02b_nominal.py', 's02c_write.py', 'env.sh', 'run_slot.sh'):
    INPUTS[f'scripts/{n}'] = sha(os.path.join(L, 'scripts', n))

D = collections.OrderedDict()
D['lane'] = 'decl-e217'
D['round'] = 'Q228'
D['declared_pst'] = DECLARED_AT
D['interpreter'] = f'/usr/bin/python3 {sys.version.split()[0]}, numpy {np.__version__}, single-threaded in slot.sh'
D['lab_commit'] = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
D['label'] = ('BLIND: MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2 (3ca4b717), the contention term F1 (#1.29.1), verify-lay\'s controls '
              '(#1.29.1.1) and the gemmLnc term (#1.29) frozen and unchanged, this declaration and the nominal forecasts hashed and frozen (FROZEN.txt, '
              'posted by the orchestrator) before any E217 datum exists. A session whose first datum precedes the freeze post is UNREAD for it.')
D['state_at_declaration'] = {'e217_releases_txt_lines': REL_LINES, 'claim_files': claim_files, 'quiet_desk_flag_aifoundry2': QUIET,
                             'reading': ('no E217 claim, session or datum on record: only the proposal (#13) and the naming (#13.1)'
                                         if [x.split()[0] for x in REL_LINES] == ['#13', '#13.1'] else 'MORE THAN THE PROPOSAL AND THE NAMING: see the lines')}
D['a_runs'] = {
    'n_runs': len(R), 'by_role': cnt['by_role'], 'by_session': dict(by_s), 'by_card': cnt['by_card'], 'by_fmt': cnt['by_fmt'],
    'n_cases': len(CASES), 'cases_by_card': cnt['cases_by_card'],
    'source': ("the registered kit: the orchestrator's copy of EE/src (out/orch/e217-src, SRC-SHA256SUMS.txt 854bd075..., copied 11:12:05 PST): "
               "src/sched/<card>-<S>.json (each run's i, block, role, arm, values, shires, type, form) and src/arms.json; nulls left out; no measurement"),
    'run_id': "E217|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py: f\"{i:03d}-{arm}\")",
    'time_selection': ("as MM1-v3.1's own loader data_v31.mms_runs_all (= data_v3.mms_runs), unread-e214's: the session's queue says ran, rc 0, "
                       "check exact or approx; role not null; values gemmL<MB>x<NB>x<KB>: and shires present; the primary view (band600 on card 1, "
                       "win on card 0: reduce_mms.py) has T_op_us, cyc_op_max and n_launch >= 1"),
    'energy_selection': ("the same, and the primary view's dP_w is not None, its p_mean_w truthy, the run not capped and its role not 'time' "
                         "(data_v31.mms_runs_all's energy condition)"),
    'not_run': 'a listed run that does not run (a session cut short or not run) is NO DATA: never imputed, never re-listed',
    'case': ("(card, arm gemmL<MB>x<NB>x<KB>, format, kind as the arm spells it, mask) over all of that card's sessions; anchors "
             "(4x8x8 int8 random, full chip) are cases like any other"),
    'groups': {
        'X1': f"the 1x1x1 cells: {cnt['cases_by_group_shape']['X1']} cases (every format and mask), reported apart",
        'MG': (f"the new core-group masks: the plan's tag 'P1-sim' (arms.json families), {cnt['cases_by_group_mask']['MG']} cases, 1x1x1 fp32 and "
               f"fp16, 12 masks a card: card 1 {mg[C1]}, card 0 {mg[C0]}; reported apart"),
        'SUB': f"the other subset masks: {cnt['cases_by_group_mask']['SUB']} cases",
        'FULL': f"the full chip: {cnt['cases_by_group_mask']['FULL']} cases",
        'S': (f"the operand-pattern arms of E217's 21 new tile kinds (no committed count; the prior-tile scan): {len(S_cases)} cases, "
              f"{len(S_runs)} runs: {newk}"),
        'C': f"the sparse50 pools (pattern:sparse50f / h / i, byte-equal to E214's pools): {cnt['cases_by_group_kind']['C']} cases, {len(C_runs)} runs, priced as the committed sparse50 kind",
        'K': f"the lab's kinds (zeros, ones, random): {cnt['cases_by_group_kind']['K']} cases"},
    'group_table_cases': {f'{a}|{b}|{c}': v for (a, b, c), v in sorted(grp_tab.items())},
    'kind_table_cases': {f'{a}|{b}': v for (a, b), v in sorted(kind_tab.items())},
    'fmt_table_cases': {f'{a}|{b}': v for (a, b), v in sorted(fmt_tab.items())},
    'run_ids': [r['id'] for r in R],
    'cases': [{'case': c['case'], 'runs': c['runs'], 'group_shape': c['group_shape'], 'group_mask': c['group_mask'], 'group_kind': c['group_kind']} for c in CASES]}
D['a2_fit_inclusion'] = ('NO E217 point can be in any fit: E217 has no datum (no session has run; e217-releases.txt holds the proposal and the '
                         'naming only). Checked all the same: no E217 token in any model\'s inputs or loaders (MM1-v3.1 28 files, MM1-v3 115, MM1-v2 86: '
                         '0 hits) and no E217 id in any landed point record (MM1-v3.1 E105-E213; MM1-v3 to E212; MM1-v2 to E208).')
D['b_quantities'] = {
    'per_card': 'aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz)',
    'T1_wall': 'cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1',
    'T2_counter_mean': "the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1",
    'T3_seconds': ("seconds a GEMM: ops x T_forecast(us) x 1e-6 / t_pass_s - 1 (ops = 64 MB NB KB a minion); at the measured clock T3's error "
                   "equals T1's identically (the reducer's T_op_us = wall / ops): both printed"),
    'E1_J_over_idle_given_t': ("W over idle at the measured op time: W = A + B / t_meas (the predictor's W_affine at the run's conditions) against "
                               "the primary view's dP_w; relative (= J over idle given t) when the case's mean MM1-v3.1 W given t and its mean measured "
                               "dP_w are both 3 W or more; else a WATTS case, scored by the mean of its runs' W - dP_w in watts (E215's form; the "
                               "watts set fixed by MM1-v3.1 and the measurement, the same for every model)"),
    'E2_J_over_idle_t_forecast': '(W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc the W over idle at the model\'s own op time T_fc; at a watts case W_fc - dP_w',
    'E3_J_at_rest_given_t': '(P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run\'s rest, measured, given)',
    'E4_J_at_rest_t_forecast': '(P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1',
    'split': ('per card; per format and kind; the 1x1x1 cells (X1) and the new core-group masks (MG) apart (also SUB, FULL); groups S, C, K; '
              'configuration twins apart')}
D['models'] = collections.OrderedDict([
    ('MM1-v3.1', "tools/matmul/mm1/v3.1 (landed 2c971828): mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel 'rgm136', V, t0_c}])"),
    ('MM1-v3', "tools/matmul/mm1/v3 (landed b1493082): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=, t0_c=)"),
    ('MM1-v2', ("tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's unread_v2_e212.call (its pins and SHA256SUMS checked): card 1 V None "
                "(the 0.517 V footing), card 0 the measured volts; energy for random, zeros and ones only (any other kind NOT FORECAST in energy); no die term")),
    ('v3.1+contention', ("form F1 (#1.29.1, frozen 09:31:34 PST Thu 19 Nov): T = T_v3.1 x clip(1 + a Phi_fresh, 0.3, 3.0), a = -0.08316593007433395 "
                         "(forecast-e215-v31-layout.json meta), Phi_fresh by the term's eval_layout.phi_of over the masked walk's features "
                         "(features_layout.walk_feats + mesh_feats, unchanged; the frozen cache's entries as frozen, the rest made by the same code from "
                         "the arms alone in step 2w); 0 at the full mask, so the factor is exactly 1 there; energy MM1-v3.1's affine at its own op time "
                         "(given t: MM1-v3.1's exactly)")),
    ('v3.1+gemmLnc', ("term F3 (#1.29): NOT APPLICABLE: E217 runs no gemmLnc arm (0 of 332 arms; rgm136 gemmL only), so it equals MM1-v3.1 on "
                      "every E217 case; not scored")),
    ('v3.1+both', ("the composition declared in reg-e216 (the candidate MM1-v3.2): time = MM1-v3.1's x the contention factor; W at a measured t = "
                   "A + (B + dW t_op,v3.1) / t with the gemmLnc term's dW, 0 on every E217 case: so it equals 'v3.1+contention' on every E217 case "
                   "(computed by the composition, compared nowhere separately)")),
    ('controls', ("verify-lay's controls (#1.29.1.1), by v02_fits.py's forms unchanged with its all-data constants (work/verify-lay/v02_fits.json): "
                  "N1+N2 (N1 = 1 - n/32, N2 = N1^2; a = [-0.09348958586302018, 0.11765730189141044]); G1 (hop mean: (110 + 12 h)/(110 + 12 h_full) - 1; "
                  "a = [0.30314251932286107]); G1+N1 (a = [0.6022127706566506, -0.021675728290377668]); the layout-blind F1 (fresh32_bar_narm: "
                  "Phi_fresh averaged over the configurations of the same (n shires, arm): here over E217's listed configurations of both cards, as "
                  "v02_fits.py averages over the fit's points of the same (n, arm); a = [-0.17556875184106632]); factor 1 + sum a_i x_i (unclipped, "
                  "as v02's E215 control columns), 1 at the full mask; time MM1-v3.1's x the factor, energy MM1-v3.1's affine at its own op time. "
                  "The features from the term's walk features (verify-lay re-derived them, 148/148); step 2 re-makes v02_e215_controls.csv's "
                  "N3, N1+N2, G1, G1+N1 columns first"))])
D['forecast_procedure'] = {
    'footing_1_measured': ("THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's start-of-run "
                           "records only, MM1-v3 README section 5's form as unread-e214 did: the primary view's kernel clock kclock_mhz; minion volts: "
                           "card 1 the models' footing 0.517 V, card 0 the primary view's rails.minion.mV / 1000 (else the model's own volts at f); "
                           "the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). The terms and controls on "
                           "MM1-v3.1's forecast at the same conditions; the layout features are configuration-only (made at step 2w)."),
    'fields_read_before_scoring': ("from each committed E217 data JSON ONLY: the top-level card, session and primary_view, and per run: run, i, ran, "
                                   "role, arm, values, type, shires, minions, die_start_c, and the primary view's kclock_mhz and rails.minion.mV. No time, "
                                   "cycles, power, energy or seconds field is read until the forecasts at those conditions are hashed."),
    'footing_2_nominal': 'the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED beside the primary footing)',
    'counts_as_inputs': ("the switch counts are inputs, never fitted: MM1-v3.1's tables (MM1-v3's rows + counts 3e8991d0); counts-e214's land "
                         "(4c39d0d3; E217 reuses none of its 20 tiles: none added); counts-e217 for E217's 21 new kinds, made in step 4 from the "
                         "tile files alone (rtl-sim/fma_toggle_v2, Verilator 5.042, counts-e214's form) and frozen (COUNTS-FROZEN.txt) before any "
                         "E217 measurement is read; added in memory to each model's tables by its own loop (no key colliding: asserted), "
                         "unread-e214's form"),
    'order': '1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt -> 4 counts-e217 -> COUNTS-FROZEN.txt; then, after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores'}
D['c_metric'] = {
    'error': 'forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W',
    'case': "a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside",
    'twins': ("per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in that "
              "model's TRAINING time configurations (its landed out/points_time_*.csv, E146 store rungs out); an energy case when that key and its "
              "energy kind are in its energy configurations (work/step1/twin-keys.json, 3418b7d8, equal to unread-e214's). The no-twin cases "
              "carry the pass rule and the headline; twins and all cases printed beside. At the nominal clocks: MM1-v3.1 63 time-twin and 24 "
              "energy-twin cases of 486 (a preview; the measured clock decides)")}
D['d_comparisons'] = {
    'test': ("the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; "
             "B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none"),
    'd': ("per case, d = |ln(1 + e_B)| - |ln(1 + e_A)| for the pair (A vs B) (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over "
          "every case both price (twins included); REPORTED beside over the cases that are twins for neither"),
    'ties': ties,
    'ties_how': ("E215's rule (rules_e215.ties_of), unread-e214's values: card 1 E215 arm B's registered ties; card 0 from E212 a1c0-S1/S2's pooled "
                 "within-case spread (bands.json card0_floors)"),
    'D1_v31_vs_v3': 'MM1-v3.1 vs MM1-v3 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled',
    'D2_v31_vs_v2': 'MM1-v3.1 vs MM1-v2 on H1-H5: per card and pooled',
    'D3_layout': ("on the subset-mask cases (MG and SUB), per card and pooled: 'v3.1+contention' vs MM1-v3.1, and each control (N1+N2, G1, G1+N1, "
                  "the layout-blind F1) vs MM1-v3.1, on H1 (wall) and H2 (counter mean); the MG cases alone and 'v3.1+contention' vs each control "
                  "REPORTED beside; H5 (J over idle with t forecast) REPORTED"),
    'D4_switch': "on group S: MM1-v3.1 with counts-e217 vs the null N, Q1 and Q2 (section e): part S's P2 and P4",
    'verdicts': 'each comparison is a verdict of its own, never part of PASS'}
D['e_switch'] = {
    'counts': ("counts-e217 (step 4): the 21 new kinds, fp32 10 (gt125, gt25, gt875, rt16, rt32, rt32b, rt64, sg_kk, sgm1, th_top) at the GEMM "
               "states S1 and S2, fp16 5 (h_gt25, h_rt32, h_rt64, h_sg, h_th_in) and int8 6 (i8_t06, i8_t1, i8_t2, i8_t3, i8_t46, i8_t5) at the "
               "launch points, exactly as counts-e214 (its scripts, its rules: a pool of fewer than 3 files measured at every file; two committed "
               "points re-counted first and matched); then MM1-v3.1: counts-e217's rows added to energy_v31's E210C31 / SWT31, MM1-v3: 3e8991d0's and "
               "counts-e217's to energy_v3's E210C / SWT (unread-e214's loop). A kind whose count cannot be made is NOT FORECAST in energy."),
    'phi': {k: v for k, v in MS['phi_new_kinds'].items()},
    'phi_how': "MM1-v3's own kinds_v3.phi(fmt, {'tiles': [file]}) over each new kind's registered tile file (sha256 checked against arms.json); sparse50f/h/i: MM1-v3's phi_of('sparse50')",
    'gate': ("DECLARED (before any datum, from the tile files alone): the fp32 tiles gt125, gt25, gt875 and the fp16 tile h_gt25 hold all-zero A rows "
             "(13, 10, 2 and 12 of 16), B none: their float gate is the arow form at the tile's own all-zero-row share, (g_op, g_lane, g8) = "
             "(share, 0, 0) - E210's arow50 (0.5, 0, 0) and E214's sp_ar4 declaration (unread-e214) - in MM1-v3.1's and MM1-v3's gate_shares; "
             "every other new float kind has no zero element: (0, 0, 0), the frozen code's literal; int8 kinds the frozen code's own 1 - v "
             "(v the count's valid share). The literal (0, 0, 0) for the four zero-row tiles REPORTED beside; the count's valid share REPORTED "
             "beside each declared share."),
    'gate_values': GATE,
    'sparse50': 'pattern:sparse50f / h / i priced as the committed sparse50 kind (data_v31.SPARSE_GEN plus sparse50h, unread-e214\'s alias); group C REPORTED',
    'Q1': ("group S, W over idle given t: MM1-v3.1 + the counts against the null N = the mean over zeros, ones and random of the run's format of the "
           "same model's own W given t at the run's conditions (the same base; only the count's information differs); cases with dP_w >= 3 W"),
    'Q2': ("group S, E210's metric, the share of D: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, D = W_R - W_Z measured, R and Z the random and "
           "zeros cases of the same card, arm, format and mask (measured means; W_fc(R) the same model's W given t, its runs' mean); for the null "
           "[(N(P) - W_fc(R)) - (W_P - W_R)] / D; cases with an R and a Z case and D > 0"),
    'N2_REPORTED': 'the null over ones and random only', 'MM1-v3_REPORTED': 'the same with MM1-v3 + the counts'}
D['f_pass_rule'] = {
    'bands': bands,
    'bands_how': ("E215's form (rules_e215.py, unchanged; unread-e214's s01d_bands.py re-run here): 2 x max(B1, B2) rounded up to a whole percent, "
                  "B1 MM1-v3.1's LOEO no-twin error over every point, B2 over this card's points (holdout_v31.json reproduced first); T3 takes T1's "
                  "bases; watts band 2 x max(B1 W, B2 W, SD_rep) rounded up to 0.01 W. Card 1's equal E215 arm B's registered bands (checked)."),
    'part_A': ("MM1-v3.1 on the PRIMARY footing by E215's rule form on each card over the NO-TWIN cases: a case passes T1, T2, T3, E3, E4 when |error| "
               "is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule "
               "PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no rule "
               "FAILS on either card and at least one rule PASSES; FAILS when any rule fails (named). Printed beside, deciding nothing: X1, MG, SUB, "
               "FULL; S, C, K; per format; twins."),
    'part_S': ("Q218's P1-P4 for MM1-v3.1 + counts-e217 against N on group S, pooled over both cards: P1 rms(Q1) < N's; P2 the exact two-sided sign "
               "test on d = |e_N| - |e_V| per case, a tie when |d| < 0.01, holds when p < 0.05 and MM1-v3.1 is closer in more; P3 rms(Q2) < N's; "
               "P4 P2's test on Q2 (ties |d| < 0.01 of D). PART S PASSES when P1-P4 hold; NOT DECIDED when either sign test has fewer than 6 "
               "untied cases or counts-e217 is not frozen before the read; else FAILS (named)."),
    'verdict': ("PASS when part A and part S pass; FAIL when either fails (named); NOT DECIDED otherwise. Decided by a script: blind-e217's scorer "
                "(scripts/s03_score.py of the lane that scores E217), which implements sections a-f of this declaration exactly, is code-tested on a "
                "stand-in day built from the frozen forecasts alone, and is hashed (sha256 in its progress log, posted with the result) BEFORE its first "
                "read of any E217 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing "
                "(section h) is scored by the same script and rules beside, REPORTED, deciding nothing.")}
D['g_label_rule'] = {
    'BLIND': ("a session is BLIND for this test when this declaration's and the nominal forecasts' sha256 (FROZEN.txt) were posted on the Discussion "
              "before the session's first datum (its first card command, the session's own log)"),
    'UNREAD': "a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the post (data-e217's read times on record); else POST-READ (REPORTED)",
    'counts_route': ("the switch-route energy of group S takes COUNTS-FROZEN.txt's post time by the same rule, session by session; the nominal "
                     "footing's group-S energy (made after counts-e217) likewise"),
    'printed': 'every result line names its label, the freeze post time and the session\'s first card command time'}
D['h_nominal_footing'] = {
    'conditions': {'aifoundry1 card 1': 'f 600.0 MHz; V 0.517 V (the models\' card-1 footing); die at start 60.0 C (the kit\'s start-gate ceiling, mms_common.CARDS a1c1)',
                   'aifoundry1 card 0': ('f 800.0 MHz (its planned clock: the kit\'s main band "800" for the governed card); V the model\'s own volts at f '
                                         '(0.604 V); die at start 55.0 C (the kit\'s a1c0 start-gate ceiling)')},
    'files': 'forecasts-nominal-e217.csv and .json: one forecast a case and model (every run of a case at the same nominal conditions)',
    'group_S_energy': 'NOT FORECAST at the freeze (no count); made by the frozen predictors with counts-e217 after step 4 into forecasts-nominal-e217-counts.csv/.json, listed in COUNTS-FROZEN.txt',
    'scored': 'by the same rules as the primary footing, beside it, REPORTED'}
D['i_earlier_reads'] = {
    'E217_data': 'none exists at this declaration (no session has run)',
    'this_lane': ("read the kit copy's arms.json, schedules, README, mms_common.py, make_schedule2.py (planning lines), tiles_gen.py's docstring and "
                  "the 24 plan tile files (zero structure, phi); E214's committed start conditions (unread-e214's conditions file: the clocks, volts "
                  "and dies of E214's runs on the same two cards, to choose nothing but to see the nominal footing's scale); no E217 forecast of the "
                  "model session's (its sealed ce793daa... was not read)"),
    'others': ("reg-e217 (Q228): the registration from #13 and the same copy; data-e217 (Q228): waiting for releases; the orchestrator: the copy and "
               "the naming (#13.1)")}
D['inputs_sha256'] = INPUTS
D['order'] = D['forecast_procedure']['order']
JP = os.path.join(L, 'DECLARED-blind-e217.json')
json.dump(D, open(JP, 'w'), indent=1)


def fmt_pct(x):
    return f'{round(100 * x)}%'


md = []
A = md.append
A('# decl-e217: the lab\'s BLIND test of its frozen matmul models on E217, DECLARED before any E217 datum exists')
A('')
A(f'*Declared {DECLARED_AT}, round Q228, at the desk on aifoundry2 (work copy of GitHub main {D["lab_commit"][:8]}). Python: /usr/bin/python3 '
  f'{sys.version.split()[0]}, numpy {np.__version__}, single-threaded in slot.sh. Nothing here was measured. E217 (the model session\'s fourth matmul '
  'sweep, 1119-mmsweep4, Discussion #13, named E217 in #13.1) has not run: no E217 datum exists.*')
A('')
A(f'**Label: BLIND.** {D["label"]}')
A('')
A('State at this declaration: out/orch/e217-releases.txt holds ' + str(len(REL_LINES)) + ' post lines (' + D['state_at_declaration']['reading'] + '); '
  f'claim files: {claim_files if claim_files else "none"}; the aifoundry2 quiet-desk flag {"present" if QUIET else "absent"}.')
A('')
A('## a. The runs')
A(f'- **{len(R)} runs** ({cnt["by_role"]}) in E217\'s seven sessions ({dict(by_s)}), {len({r["arm_label"] for r in R})} arms, **{len(CASES)} cases**; by card '
  f'{cnt["by_card"]} runs, {cnt["cases_by_card"]} cases; by format {cnt["by_fmt"]}.')
A(f'- Source: {D["a_runs"]["source"]}. Run id: {D["a_runs"]["run_id"]}. The ids are in `DECLARED-blind-e217.json` (a_runs.run_ids, a_runs.cases).')
A(f'- Time selection: {D["a_runs"]["time_selection"]}.')
A(f'- Energy selection: {D["a_runs"]["energy_selection"]}.')
A(f'- {D["a_runs"]["not_run"].capitalize()}.')
A(f'- Case: {D["a_runs"]["case"]}.')
A('- Groups (from arms.json alone):')
for k, v in D['a_runs']['groups'].items():
    A(f'  - **{k}**: {v}')
A('')
A('| card | shape | mask group | cases |')
A('|---|---|---|---|')
for (a, b, c), v in sorted(grp_tab.items()):
    A(f'| {a} | {"1x1x1" if b == "X1" else "other"} | {c} | {v} |')
A('')
A(f'- **Fit inclusion:** {D["a2_fit_inclusion"]}')
A('')
A('## b. The quantities')
for k, v in D['b_quantities'].items():
    A(f'- **{k}**: {v}')
A('')
A('## The models')
for k, v in D['models'].items():
    A(f'- **{k}**: {v}')
A('')
A('## The forecast procedure')
for k, v in D['forecast_procedure'].items():
    A(f'- **{k}**: {v}')
A('')
A('## c. The metric')
for k, v in D['c_metric'].items():
    A(f'- **{k}**: {v}')
A('')
A('## d. The comparisons')
for k, v in D['d_comparisons'].items():
    if k != 'ties':
        A(f'- **{k}**: {v}')
A(f'- ties: card 1 {ties[C1]}; card 0 {ties[C0]}')
A('')
A('## e. The switch-pattern arms: the counts, phi and the gate')
for k in ('counts', 'phi_how', 'gate', 'sparse50', 'Q1', 'Q2', 'N2_REPORTED', 'MM1-v3_REPORTED'):
    A(f'- **{k}**: {D["e_switch"][k]}')
A('')
A('| kind | phi | tile | sha256 |')
A('|---|---|---|---|')
for k, v in sorted(MS['phi_new_kinds'].items()):
    A(f'| {k} | {v["phi"]:.6f} | `{v["tile"]}` | `{v["sha256"][:16]}...` |')
A('')
A('| zero-row tile | declared gate (g_op, g_lane, g8) | all-zero A rows of 16 | A zero share | B zero share |')
A('|---|---|---|---|---|')
for k, v in GATE.items():
    A(f'| {k} | ({v["g_op"]:.4f}, 0, 0) | {v["A_all_zero_rows_of_16"]} | {v["A_zero_share"]:.4f} | {v["B_zero_share"]:.4f} |')
A('')
A('## f. The pass rule (decided by a script)')
A(f'- **Part A:** {D["f_pass_rule"]["part_A"]}')
A(f'- Bands ({D["f_pass_rule"]["bands_how"]}):')
A('')
A('| card | T1 | T2 | T3 | E1 | E2 | E3 | E4 | watts |')
A('|---|---|---|---|---|---|---|---|---|')
for card in (C1, C0):
    b = bands[card]
    A(f'| {card} | ' + ' | '.join(fmt_pct(b[q]) for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')) + f' | {b["watts_W"]:.2f} W |')
A('')
for card in (C1, C0):
    A(f'- {card}: ' + '; '.join(f'{q} {v}' for q, v in bands[card]['arithmetic'].items()))
A(f'- **Part S:** {D["f_pass_rule"]["part_S"]}')
A(f'- **Verdict:** {D["f_pass_rule"]["verdict"]}')
A('')
A('## g. The label rule')
for k, v in D['g_label_rule'].items():
    A(f'- **{k}**: {v}')
A('')
A('## h. The nominal footing (a second footing, frozen now, scored beside)')
for k, v in D['h_nominal_footing']['conditions'].items():
    A(f'- **{k}**: {v}')
for k in ('files', 'group_S_energy', 'scored'):
    A(f'- **{k}**: {D["h_nominal_footing"][k]}')
A('')
A('## i. Earlier reads, disclosed')
for k, v in D['i_earlier_reads'].items():
    A(f'- **{k}**: {v}')
A('')
A('## The inputs, by sha256')
A('')
A('| input | sha256 |')
A('|---|---|')
for k, v in INPUTS.items():
    A(f'| {k} | `{v}` |')
A('')
A(f'**Order:** {D["order"]}. Every sha256 and time in logs/progress.txt.')
MP = os.path.join(L, 'DECLARED-blind-e217.md')
open(MP, 'w').write('\n'.join(md) + '\n')
print('declared', DECLARED_AT)
print(sha(MP), 'DECLARED-blind-e217.md')
print(sha(JP), 'DECLARED-blind-e217.json')
