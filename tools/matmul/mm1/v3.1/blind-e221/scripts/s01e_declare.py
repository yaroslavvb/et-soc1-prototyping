#!/usr/bin/env python3
"""decl-e221 (Q235) step 1e: write the declaration, DECLARED-blind-e221.md and DECLARED-blind-e221.json, at the lane root, from this lane's
step-0/1 records only (no E221 datum exists for this lane: none is opened). decl-e219's s01e_declare.py in form (sections 0, a-i, the
inputs by sha256), E221's runs, classes, cards and models. Refuses to overwrite a declaration whose hash is logged.
Run: /usr/bin/python3 -I -B s01e_declare.py <lane dir>"""
import collections
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
TZ = dict(os.environ, TZ='America/Los_Angeles')
MD = os.path.join(L, 'DECLARED-blind-e221.md')
JS = os.path.join(L, 'DECLARED-blind-e221.json')
if os.path.exists(os.path.join(L, 'logs', 'step1-sha256.txt')):
    raise SystemExit('step 1 is hashed already: the declaration is not rewritten')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


W = os.path.dirname(os.path.dirname(L))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
MS = json.load(open(os.path.join(L, 'work', 'step1', 'models-step1.json')))
BD = json.load(open(os.path.join(L, 'work', 'step1', 'bands.json')))
DP = json.load(open(os.path.join(L, 'work', 'step1', 'domain-probe.json')))
CF = json.load(open(os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')))
WK = json.load(open(os.path.join(L, 'work', 'step2', 'walk-feats-e221.json')))
VL = json.load(open(os.path.join(L, 'work', 'verify-lay', 'v02_fits.json')))
FITP = json.load(open(os.path.join(L, 'work', 'cands', 'layout2', 'work', 'fit_results.json')))
FITL = json.load(open(os.path.join(L, 'work', 'cands', 'l3-edge', 'work', 'fit', 'fit-l3s.json')))
LABC = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
REL = open(os.path.join(W, 'out', 'orch', 'e221-releases.txt')).read()
R, CC = RL['runs'], RL['cases']
cnt = RL['counts']
CARDS = ['aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0']
CLASSES = ['MASK', 'CELL1', 'KB1', 'L2I8', 'MQ3', 'DK', 'HLD', 'BW', 'NB1', 'ANCHOR']
by_cl_runs = collections.Counter(r['class'] for r in R)
by_cl_cases = collections.Counter(c['class'] for c in CC)
sub_by_cl = collections.Counter(c['class'] for c in CC if c['group_mask'] == 'SUB')
full_by_cl = collections.Counter(c['class'] for c in CC if c['group_mask'] == 'FULL')
probe_ok = {m: sum(1 for c in CC if DP['cases'][c['case']][m]['time'] == 'FORM' and DP['cases'][c['case']][m]['energy'] == 'FORECAST')
            for m in ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2')}
n_l3 = len(CF['l3s']['domain_keys'])
n_sub = sum(1 for c in CC if c['group_mask'] == 'SUB')
twp = MS['twin_preview_nominal']
A_HOP, A_LAG = FITP['constants_all_data']['posimb']
LAM = float(FITL['lam_all'])
ctrl = {k: VL['forms'][k]['a_all'] for k in ('N1+N2', 'G1', 'G1+N1', 'fresh32_bar_narm')}
bands = {c: {q: v['band'] for q, v in BD['cards'][c]['bands'].items()} for c in CARDS}
bandw = {c: BD['cards'][c]['band_w']['band_W'] for c in CARDS}
ties = {c: BD['cards'][c]['ties'] for c in CARDS}
rel_lines = [x for x in REL.splitlines() if x.startswith('#15')]

INPUTS = ['work/step1/runs-listed.json', 'work/step1/models-step1.json', 'work/step1/twin-keys.json', 'work/step1/bands.json',
          'work/step1/domain-probe.json', 'work/step2/walk-feats-e221.json', 'work/step2/cand-feats-e221.json', 'work/lab-commit.txt',
          'work/e221-src/SRC-SHA256SUMS.txt', 'work/e221-src/src/arms.json', 'work/verify-lay/v02_fits.json', 'work/verify-lay/v02_fits.py',
          'work/cands/layout2/FROZEN.txt', 'work/cands/lnc-form/FROZEN.txt', 'work/cands/l3-edge/FROZEN.txt',
          'work/cands/layout2/work/fit_results.json', 'work/cands/layout2/work/private_shared.json',
          'work/cands/l3-edge/work/fit/fit-l3s.json', 'work/cands/l3-edge/work/feature/l3s_cache.json',
          'work/lab/tools/matmul/mm1/v3.2/SHA256SUMS', 'work/lab/tools/matmul/mm1/v3.2/out/mm1_v32_params.json',
          'work/lab/tools/matmul/mm1/v3.1/SHA256SUMS', 'work/lab/tools/matmul/mm1/v3.1/out/mm1_v31_params.json',
          'work/lab/tools/matmul/mm1/v3/SHA256SUMS', 'work/lab/tools/matmul/mm1/v3/out/mm1_v3_params.json',
          'work/lab/tools/matmul/mm1/v2/SHA256SUMS', 'work/lab/tools/matmul/mm1/v2/out/mm1_v2_params.json',
          'work/lab/tools/matmul/mm1/v3.2-terms/layout/SHA256SUMS', 'work/lab/tools/matmul/mm1/v3.2-terms/gemmlnc/SHA256SUMS',
          'work/lab/tools/claims-v3/e215/rules_e215.py']
for s in sorted(os.listdir(os.path.join(L, 'work', 'e221-src', 'src', 'sched'))):
    INPUTS.append('work/e221-src/src/sched/' + s)
SCRIPTS = ['scripts/' + f for f in sorted(os.listdir(os.path.join(L, 'scripts'))) if f.endswith(('.py', '.sh'))]
inputs_sha = {p: sha(os.path.join(L, p)) for p in INPUTS + SCRIPTS}

MODELS = ['MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2', 'v3.1+contention', 'v3.1+both', 'ctrl N1+N2', 'ctrl G1', 'ctrl G1+N1',
          'ctrl F1-layout-blind', 'MM1-v3.2+posimb', 'MM1-v3.2+L3S']
D = collections.OrderedDict()
D['label'] = 'BLIND (sessions whose first datum follows the freeze post); UNREAD (any whose first datum precedes it)'
D['experiment'] = ("E221 (#15, 05:53:07 PST Fri 20 Nov 2026): the model session's sixth matmul sweep, 1120-mmsweep6, of E136's rgm136 "
                   "unchanged: 847 runs over 345 gemmL arms and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S3 "
                   "low power, aifoundry2 card 0 S1-S3 under the kit's live stops 85 W x3 / 80 C); its sealed forecast cab693ef... is not read here")
D['state_at_declaration'] = rel_lines
D['domain'] = collections.OrderedDict([
    ('verdict', 'EVERY E221 case is IN MM1\'s domain: all 345 arms and the anchor are rgm136\'s cooperative gemmL<MB>x<NB>x<KB> loop (no '
                'gemmLnc, no block, stream or TenB arm); NO case is OUT OF DOMAIN, so none is left unforecast'),
    ('evidence', f"probe p01: every one of the {len(CC)} cases has a form (finite wall and mean cycles, op time; energy FORECAST) in "
                 f"MM1-v3.2 {probe_ok['MM1-v3.2']}, MM1-v3.1 {probe_ok['MM1-v3.1']}, MM1-v3 {probe_ok['MM1-v3']}, MM1-v2 {probe_ok['MM1-v2']} "
                 "at the nominal footing (work/step1/domain-probe.json, status only)"),
    ('by_class', {cl: {'what': RL['class_what'][cl], 'cases': by_cl_cases[cl], 'runs': by_cl_runs[cl], 'subset_mask_cases': sub_by_cl[cl],
                       'full_chip_cases': full_by_cl[cl],
                       'MM1-v0': 'a gemmL form (mm1_v0.py classes_gemmL; subsets at the full chip footprint); not declared here, not probed',
                       'MM1-v1': 'a gemmL form (mm1_core.py Shape, the masked map); not declared here, not probed',
                       'MM1-v2': 'yes (probe p01)', 'MM1-v3': 'yes (probe p01)', 'MM1-v3.1': 'yes (probe p01)', 'MM1-v3.2': 'yes (probe p01)',
                       'v3.1+contention and the controls': ('their factor at the subset masks (%d cases of this class); 1 at the full chip'
                                                            % sub_by_cl[cl]),
                       'MM1-v3.2+posimb': 'in its scope at the subset masks (%d cases); MM1-v3.2 at the full chip' % sub_by_cl[cl],
                       'MM1-v3.2+L3S': 'in its domain at the full chip (%d cases); MM1-v3.2 at the subset masks' % full_by_cl[cl]}
                  for cl in CLASSES}),
    ('not_applicable', "'v3.1 + gemmLnc term' (#1.29, F3) and 'MM1-v3.2 + gemmLnc term AF4' (lnc-form): each is 0 off gemmLnc and E221 runs "
                       "no gemmLnc arm, so each equals its base on every case: declared NOT APPLICABLE, not scored"),
    ('domain_limits_reported', "IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the 1x1x1 cells and "
                               "core-group masks at shire masks no fit holds (most of E221's 65 masks); aifoundry2 card 0 and aifoundry1 card 0 "
                               "under their governors (the clock read from each run's start-of-run records; the nominal footing at 800 MHz); "
                               "configuration twins (section c) split")])
D['runs'] = collections.OrderedDict([
    ('listed', f"{cnt['listed_runs (arm and anchor; nulls and smoke left out)']} runs ({cnt['by_role']}) of the schedules' 847 (36 nulls and "
               f"each session's smoke left out), {len(CC)} cases (a case = card, arm, format, kind, mask); by session {cnt['by_session']}; by "
               f"card {cnt['by_card']} runs, {cnt['cases_by_card']} cases; by format {cnt['by_fmt']} runs; by kind {cnt['by_kind']} runs; by "
               f"class {dict(by_cl_runs)} runs, {dict(by_cl_cases)} cases; subset masks {n_sub} cases over {cnt['distinct_masks']} masks "
               f"({cnt['subset_configurations (shape, mask)']} subset configurations)"),
    ('ids', 'E221|<card>-<S>|<i:03d>-<arm id>: the kit\'s own run key (run_mms.py), from src/sched/<card>-<S>.json and src/arms.json of '
            'the orchestrator\'s copy (SRC-SHA256SUMS.txt 5680112f..., 53/53; the kit\'s own SRC-SHA256SUMS 52/52); the list is '
            'work/step1/runs-listed.json'),
    ('fit_inclusion', 'NO E221 point can be in any fit: E221 has no datum for this lane. Checked all the same: no E221 token in any model\'s '
                      'inputs or loaders (MM1-v3.2 13 files, MM1-v3.1 28, MM1-v3 115, MM1-v2 86: 0 hits) and no E221 id in any landed '
                      'point record (MM1-v3.2 to E215, MM1-v3.1 to E213, MM1-v3 to E212, MM1-v2 to E208)'),
    ('tiles', 'E221 designs no tile: arms.json\'s tiles table is empty and its 9 tile files (8 named by arms) equal the lab\'s kinds '
              '(tools/claims-v3/kinds/tiles) byte for byte, each a committed blob; so no switch count is made (step 4 NOT NEEDED)'),
    ('aborted_S1_start', 'aifoundry1 card 1\'s S1 started 05:53:56 and was stopped at 05:55:27 as its first run began (#15.2.1): no run ran '
                         '(the opening rest and three smoke processes, 1.47 card-minutes, EE/sessions/1795182836-a1c1-S1/): kept apart, '
                         'not a scheduled session\'s data, never opened by this lane, never scored; S1 is claimed again whole after the '
                         'lab\'s freeze post, and its own session folder and first card command decide its label')])
D['quantities'] = collections.OrderedDict([
    ('per_card', 'aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz); '
                 'aifoundry2 card 0 under its governor (main band 800 MHz), the kit\'s live stops'),
    ('T1_wall', 'cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1'),
    ('T2_counter_mean', 'the counter\'s mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1'),
    ('T3_seconds', 'seconds a pass (one GEMM): 64 MB NB KB x T_forecast(us) x 1e-6 / t_pass_s - 1 (the host\'s ops a minion a pass); at the '
                   'measured clock T3 equals T1 identically (the reducer\'s T_op_us = wall / ops): both printed'),
    ('E1_J_over_idle_given_t', 'W over idle at the measured op time, W = A + B / t_meas (the predictor\'s W_affine at the run\'s conditions) '
                               'against the primary view\'s dP_w; relative (= J over idle given t) when the case\'s mean MM1-v3.2 W given t '
                               'and its mean measured dP_w are both 3 W or more; else a WATTS case scored in watts (E215\'s form; the watts '
                               'set fixed by MM1-v3.2 and the measurement, the same for every model)'),
    ('E2_J_over_idle_t_forecast', '(W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc at the model\'s own op time; at a watts case W_fc - dP_w'),
    ('E3_J_at_rest_given_t', '(P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run\'s rest, measured, given)'),
    ('E4_J_at_rest_t_forecast', '(P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1'),
    ('split', 'per card; per format and kind; per class (MASK, CELL1, KB1, L2I8, MQ3, DK, HLD, BW, NB1, ANCHOR); FULL and SUB; '
              'configuration twins apart (section c)')])
D['models'] = collections.OrderedDict([
    ('MM1-v3.2', 'THE LAB\'S NEWEST (tools/matmul/mm1/v3.2, landed 4e386f75; SHA256SUMS d52c9cce, 58/58): mm1_v32.Model(out/mm1_v32_params.json)'
                 '.predict_many([{card, arm, fmt, kind, mask, f, kernel rgm136, V, t0_c}]); time T5r+G0+n32 refitted, no layout term; energy '
                 'E1t + F3 (0 off gemmLnc). The pass rule\'s model (section f)'),
    ('MM1-v3.1', 'tools/matmul/mm1/v3.1 (landed 2c971828; SHA256SUMS f6840d2d, 64/64): mm1_v31.Model(out/mm1_v31_params.json).predict_many'),
    ('MM1-v3', 'tools/matmul/mm1/v3 (landed b1493082; SHA256SUMS c24efc14, 170/170): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, '
               'fmt, kind, mask, f, kernel=\'rgm136\', V=, t0_c=)'),
    ('MM1-v2', 'tools/matmul/mm1/v2 (SHA256SUMS eafb6558, 114/114) through MM1-v3\'s unread_v2_e212.call: card 1 V None (the 0.517 V '
               'footing), the governed cards the measured volts (V_mv); energy for random, zeros and ones (E221\'s only kinds); no die term'),
    ('v3.1+contention', 'F1 (#1.29.1, tools/matmul/mm1/v3.2-terms/layout): T = T_v3.1 x clip(1 + a Phi_fresh, 0.3, 3.0), a = '
                        '-0.08316593007433395 (forecast-e215-v31-layout.json meta), Phi_fresh by the term\'s eval_layout.phi_of over the '
                        'masked walk\'s features (step 2w: %d configurations computed by the term\'s features_layout code, %d from its '
                        'frozen cache); 1 at the full mask; energy MM1-v3.1\'s affine at its own op time' % (len(WK['computed']),
                                                                                                         len(WK['from_frozen_cache']))),
    ('v3.1+gemmLnc', 'F3 (#1.29): NOT APPLICABLE (no gemmLnc arm in E221; it equals MM1-v3.1 on every case); not scored'),
    ('v3.1+both', 'reg-e216\'s composition: F1\'s time, W = A + (B + dW t_op,v3.1) / t with the gemmLnc term\'s dW, 0 on every E221 case: '
                  'equal to v3.1+contention on every case (computed by the composition all the same)'),
    ('controls', 'verify-lay\'s controls (#1.29.1.1) by v02_fits.py\'s forms unchanged with its all-data constants (work/verify-lay/'
                 'v02_fits.json, re-run on E221\'s configurations): N1+N2 (N1 = 1 - n/32, N2 = N1^2; a = %s); G1 (hop mean: (110 + 12 h)/'
                 '(110 + 12 h_full) - 1; a = %s); G1+N1 (a = %s); the layout-blind F1 (fresh32_bar_narm: Phi_fresh averaged over E221\'s '
                 'listed configurations of the same (n shires, arm); a = %s); factor 1 + sum a_i x_i (unclipped), 1 at the full mask; time '
                 'MM1-v3.1\'s x the factor, energy MM1-v3.1\'s affine at its own op time' % (ctrl['N1+N2'], ctrl['G1'], ctrl['G1+N1'],
                                                                                         ctrl['fresh32_bar_narm'])),
    ('MM1-v3.2+posimb (REPORTED)', 'the MM1-v3.3 candidate of layout2 (Q234; FROZEN.txt 81d04c97 at 05:39:48 PST, posted #1.30.1.2.1 '
                                   '05:47:36; KEPT by its declared rule): by its frozen maker\'s composition unchanged (h01_freeze.py: '
                                   'g_wall = clip(1 + a_hop e G1core + a_lag e LAGcore, 0.3, 3), g_mean = clip(1 + a_hop e G1core, 0.3, 3); '
                                   'e the elasticity of MM1-v3.2\'s op time to its memory constants (x 1.01) by Engine31; G1core = Lmean_act / '
                                   'Lmean_full - 1, LAGcore = (Lmax_act - Lmean_act) / Lmean_full x Fp / (Fp + Fs) from f02_private\'s features '
                                   '(step 2f: %d made, %d from its frozen cache)) at its all-data a_hop = %r, a_lag = %r; in scope at the subset '
                                   'masks of rgm136 gemmL (%d cases), MM1-v3.2 to the last bit elsewhere; energy MM1-v3.2\'s affine at the '
                                   'composed op time (the maker\'s compose)' % (len(CF['posimb']['computed']), len(CF['posimb']['from_frozen_cache']),
                                                                              A_HOP, A_LAG, n_sub)),
    ('MM1-v3.2+L3S (REPORTED)', 'the MM1-v3.3 candidate of l3-edge (Q234; FROZEN.txt e8216cbb at 05:57:20 PST; KEPT by its declared rule): '
                                'its frozen maker\'s term_l3s.ModelL3S(MM1-v3.2\'s params, lam = %r, the set model\'s cache) unchanged; in '
                                'its domain at the full mask (%d cases; the set model\'s records: %d made here by l3s_feature.a_shares, %d '
                                'from its frozen cache), MM1-v3.2 to the last bit at the subset masks; energy MM1-v3.2\'s predictor on the '
                                'shifted class distribution (the maker\'s own)' % (LAM, n_l3, len(CF['l3s']['computed']),
                                                                                  len(CF['l3s']['from_frozen_cache']))),
    ('MM1-v3.2+AF4', 'the MM1-v3.3 candidate of lnc-form (Q234; FROZEN.txt 5373973f at 05:35:36 PST): NOT APPLICABLE (0 off gemmLnc; no '
                     'gemmLnc arm in E221): equal to MM1-v3.2 on every case; not scored'),
    ('maker_checks', 'before any output, step 2 re-makes: F1\'s 94 frozen E215 rows; v02_e215_controls.csv\'s N3, N1+N2, G1, G1+N1 columns; '
                     'every one of posimb\'s 306 frozen E220 rows (g_wall and wall cycles) and L3S\'s 306 frozen E220 rows (wall cycles) '
                     'from their frozen files (probe p02: all exact)')])
D['forecast_procedure'] = collections.OrderedDict([
    ('footing_1_measured', 'THE PRIMARY FOOTING: each frozen predictor unchanged at each run\'s measured conditions, read from the data\'s '
                           'start-of-run records only (MM1\'s README section 5 form, as unread-e214, decl-e217 and decl-e219 did): the '
                           'primary view\'s kernel clock kclock_mhz; minion volts: card 1 the models\' footing 0.517 V, the governed cards '
                           'the primary view\'s rails.minion.mV / 1000 (else the model\'s own volts at f); the governed base by the model\'s '
                           'own G_of_f(card, f); the run\'s die_start_c (50 C when absent). The terms, controls and candidates on their base '
                           'model\'s forecast at the same conditions; their features are configuration-only (steps 2w, 2f)'),
    ('fields_read_before_scoring', 'from each committed E221 data JSON ONLY: the top-level card, session and primary_view, and per run: run, '
                                   'i, ran, role, arm, values, type, shires, minions, die_start_c, arm_token, arm_family, ops_pass, '
                                   'ops_pass_ok, and the primary view\'s kclock_mhz and rails.minion.mV. No time, cycles, power, energy or '
                                   'seconds field is read until the forecasts at those conditions are hashed'),
    ('footing_2_nominal', 'the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED)'),
    ('counts_as_inputs', 'the switch counts are inputs, never fitted: each model\'s own tables (MM1-v3.1 and MM1-v3.2: MM1-v3\'s rows + '
                         'counts 3e8991d0; counts-e214); E221\'s kinds (zeros, ones, random) are committed kinds with committed counts; '
                         'E221 designs no tile, so counts-e217\'s rows are not needed and no count is made'),
    ('order', '0 the work copies -> 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt (no step 4: no counts); after '
              'the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores')])
D['metric'] = collections.OrderedDict([
    ('error', 'forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W'),
    ('case', 'a case\'s error = the mean of its runs\' errors (each run at its own conditions); per-run figures REPORTED beside'),
    ('twins', 'per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs\' measured clocks to 25 MHz) is '
              'in that model\'s TRAINING time configurations (its landed out/points_time_*.csv; E146 store rungs out); an energy case when '
              'that key and its kind are in its energy configurations (work/step1/twin-keys.json, %s); the no-twin cases carry the pass '
              'rule and the headline; twins and all cases printed beside. At the nominal clocks (a preview; the measured clock decides): '
              'MM1-v3.2 %d time / %d energy twins of %d, MM1-v3.1 %d / %d, MM1-v3 %d / %d, MM1-v2 %d / %d'
              % (inputs_sha['work/step1/twin-keys.json'][:8], twp['MM1-v3.2']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.2']['energy_twin_cases_at_nominal_clock'], len(CC), twp['MM1-v3.1']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.1']['energy_twin_cases_at_nominal_clock'], twp['MM1-v3']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3']['energy_twin_cases_at_nominal_clock'], twp['MM1-v2']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v2']['energy_twin_cases_at_nominal_clock']))])
D['comparisons'] = collections.OrderedDict([
    ('test', 'the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more '
             'cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none'),
    ('d', 'per case d = |ln(1 + e_B)| - |ln(1 + e_A)| (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both '
          'price (twins included); REPORTED beside over the cases that are twins for neither'),
    ('ties_how', 'E215\'s rule (rules_e215.ties_of) on the floors of work/step1/bands.json: card 1 E215 arm B\'s registered ties %s; '
                 'aifoundry1 card 0 %s (E212 a1c0-S1/S2); aifoundry2 card 0 %s (E212 a2c0-S1/S2: a weak floor, 3 cases with two runs)'
                 % (ties['aifoundry1 card 1'], ties['aifoundry1 card 0'], ties['aifoundry2 card 0'])),
    ('D0_v32_vs_v31', 'MM1-v3.2 vs MM1-v3.1 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t '
                      'forecast (E2): per card and pooled over every case; per class REPORTED'),
    ('D1_v31_vs_v3', 'MM1-v3.1 vs MM1-v3 on H1-H5: per card and pooled; per class REPORTED'),
    ('D2_v31_vs_v2', 'MM1-v3.1 vs MM1-v2 on H1-H5: per card and pooled; per class REPORTED'),
    ('D3_layout', f'on the subset-mask cases ({n_sub}: the MASK, CELL1 and L2I8 classes at shire subsets), per card and pooled: '
                  '\'v3.1+contention\' vs MM1-v3.1, and each control (N1+N2, G1, G1+N1, the layout-blind F1) vs MM1-v3.1, on H1 (wall) and '
                  'H2 (counter mean); per class REPORTED'),
    ('D3c_candidates_REPORTED', f'deciding nothing: MM1-v3.2+posimb vs MM1-v3.2 on the subset-mask cases (H1, H2); MM1-v3.2+L3S vs MM1-v3.2 '
                                f'on its {n_l3} full-mask cases (H1-H5); each candidate vs MM1-v3.1 beside'),
    ('D4_switch', 'NOT APPLICABLE: E221 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random), so the switch '
                  'route with counts against without has nothing to decide'),
    ('verdicts', 'each comparison is a verdict of its own, never part of PASS')])
D['reported_beside'] = collections.OrderedDict([
    ('classes', 'each class\'s rms and bias per card and model (the 1x1x1 cells at new masks, the core-group masks, KB = 1, deep K, the held '
                'walks, the int8 L2 point, MQ3, NB1, BW, the anchor), REPORTED'),
    ('mask_ladders', 'on the MASK class, each placement family (PLA, PLB, PLC, PLD, PLE, PLH, PLK, PLK3, PLL, PLM, PLN, PLX) against its '
                     'whole-chip twin: measured and forecast subset/full ratios per model, REPORTED'),
    ('governed_clock', 'on the governed cards: each run\'s measured clock beside the nominal 800 MHz and the nominal-footing error, REPORTED')])
D['pass_rule'] = collections.OrderedDict([
    ('part_A', 'MM1-v3.2 on the PRIMARY footing by E215\'s rule form on each card over its NO-TWIN cases (every class): a case passes T1, '
               'T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts '
               'difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 '
               'cases, NO DATA with none. PART A PASSES when no rule FAILS on any card and at least one rule PASSES; FAILS when any rule '
               'fails (named); else NOT DECIDED'),
    ('bands', {c: dict(bands[c], watts_W=bandw[c]) for c in CARDS}),
    ('bands_how', 'E215\'s form by rules_e215.bases from MM1-v3.1\'s held-out errors (work/step1/bands.json; card 1 = E215 arm B\'s bands, '
                  'aifoundry1 card 0 = decl-e219\'s; aifoundry2 card 0 the same arithmetic on its own points and E212 a2c0 floors), the '
                  'same bands for every model: a declared choice (MM1-v3.2 is scored against the bands its predecessor earned)'),
    ('part_A_v31_REPORTED', 'the same rules for MM1-v3.1 (the continuity with E215, E217 and E219), REPORTED, deciding nothing'),
    ('part_S', 'NOT APPLICABLE (no operand-pattern arm: D4)'),
    ('verdict', 'PASS when part A passes; FAIL when it fails (named); NOT DECIDED otherwise. Decided by a script: blind-e221\'s scorer (the '
                'scripts of the lane that scores E221), implementing this declaration\'s sections exactly, code-tested on a stand-in day '
                'built from the frozen forecasts alone, and hashed (sha256 in its progress log, posted with the result) BEFORE its first read '
                'of any E221 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing '
                '(section h) by the same script and rules beside, REPORTED. A session that does not run, or runs short, is scored on what ran; '
                'a card with no session is NO DATA')])
D['label_rule'] = collections.OrderedDict([
    ('BLIND', 'a session is BLIND for this test when FROZEN.txt\'s sha256 lines were posted on the Discussion before the session\'s first '
              'datum (its first card command, the session\'s own log)'),
    ('UNREAD', 'a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the '
               'post (data-e221\'s read times on record); else POST-READ (REPORTED)'),
    ('S1', 'aifoundry1 card 1\'s S1 as re-claimed after the freeze post is labelled by its own first card command; the stopped start of '
           '05:53:56-05:55:27 (no run) is not scored'),
    ('printed', 'every result line names its label, the freeze post time and the session\'s first card command time')])
D['nominal'] = collections.OrderedDict([
    ('aifoundry1 card 1', 'f 600.0 MHz; V 0.517 V (the models\' card-1 footing); die at start 60.0 C (the kit\'s a1c1 start-gate ceiling)'),
    ('aifoundry1 card 0', 'f 800.0 MHz (its planned clock: the kit\'s main band "800"); V the model\'s own volts at f; die at start 55.0 C '
                          '(the kit\'s a1c0 start-gate ceiling)'),
    ('aifoundry2 card 0', 'f 800.0 MHz (the kit\'s main band "800" for the governed card); V the model\'s own volts at f; die at start 55.0 C '
                          '(the kit\'s a2c0 start-gate ceiling)'),
    ('files', 'forecasts-nominal-e221.csv and .json: one forecast a case and model for every case (every run of a case at the same nominal '
              'conditions), all 12 model columns (2 REPORTED)'),
    ('scored', 'by the same rules as the primary footing, beside it, REPORTED')])
D['earlier_reads'] = collections.OrderedDict([
    ('E221_data', 'none read: the only E221 files that exist at this declaration are the stopped S1 start\'s (EE/sessions/1795182836-a1c1-S1/'
                  ', no run), on aifoundry1, never opened (no ssh by this lane)'),
    ('this_lane', 'read the kit copy\'s arms.json, schedules, README, mms_common.py (the cards and gates), reduce_mms.py\'s header (the '
                  'primary view), make_schedule2.py (a grep for the family codes) and the 9 tile files\' bytes against the lab\'s kinds; the '
                  'frozen models\' code and READMEs; the three candidates\' makers (scripts, frozen files, fit records and caches, copied '
                  'read-only); probe p01 (the domain, status only) and probe p02 (a code test of the nominal-forecast script: only its checks, '
                  'counts and the factor ranges over the subset cases printed; its output deleted unread) ran before this declaration and '
                  'chose nothing in it; no E221 forecast of the model session\'s (its sealed cab693ef... was not read); no E220 datum'),
    ('others', 'reg-e221 and data-e221 (Q235) run beside: the registration from #15 and the same copy, and the data lane waiting for '
               'releases; the orchestrator: the copy (05:54:33) and the naming (#15.2)')])
D['models_list'] = MODELS

made = now()
J = {'what': 'decl-e221 (Q235): the lab\'s BLIND test of its frozen matmul models on E221, DECLARED before any E221 datum',
     'written_pst': made, 'python': sys.version.split()[0], 'lab_commit': LABC, 'models': MODELS,
     'models_reported': ['MM1-v3.2+posimb', 'MM1-v3.2+L3S'], 'not_applicable': ['v3.1+gemmLnc', 'MM1-v3.2+AF4'],
     'n_runs': len(R), 'n_cases': len(CC), 'n_in_domain': len(CC), 'n_out_of_domain': 0,
     'cases': [{k: c[k] for k in ('case', 'card', 'arm', 'fmt', 'kind', 'mask', 'class', 'subfamily', 'group_mask', 'MB', 'NB', 'KB',
                                  'ops_per_minion_pass', 'n_shires', 'runs')} for c in CC],
     'declaration': D, 'inputs_sha256': inputs_sha}
json.dump(J, open(JS, 'w'), indent=1)


def md_sec(title, d):
    out = ['', '## ' + title]
    for k, v in d.items():
        if isinstance(v, dict):
            out.append(f'- **{k}**:')
            for k2, v2 in v.items():
                out.append(f'  - {k2}: {json.dumps(v2) if isinstance(v2, dict) else v2}')
        elif isinstance(v, list):
            out.append(f'- **{k}**:')
            for x in v:
                out.append(f'  - {x}')
        else:
            out.append(f'- **{k}**: {v}')
    return out


lines = ['# decl-e221: the lab\'s BLIND test of its frozen matmul models on E221, DECLARED before any E221 datum',
         '',
         f'*Lane decl-e221 (round Q235), aifoundry2\'s desk; written {made}, Pacific time. Desk only: no card, no ssh, no simulator, no commit. '
         f'Interpreter: /usr/bin/python3 {sys.version.split()[0]}, -I -B, single-threaded, every numerical step one slot job. Inputs: a git '
         f'archive of GitHub main {LABC[:8]} (= LAB HEAD), the orchestrator\'s copy of E221\'s kit (SRC-SHA256SUMS.txt 5680112f...), '
         f'verify-lay\'s fits record and the three MM1-v3.3 candidates\' frozen makers (Q234). Labels: registered (this file), measured, '
         f'desk, post hoc, held out, blind; REPORTED = printed beside, deciding nothing.*',
         '',
         f'**The experiment.** {D["experiment"]}.',
         '',
         '**The state at this declaration** (W/out/orch/e221-releases.txt):']
lines += ['- ' + x for x in rel_lines]
lines += ['', '## 0. MM1\'s domain, first', '',
          f'- **{D["domain"]["verdict"]}.**', f'- Evidence: {D["domain"]["evidence"]}.', '',
          '| class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | posimb scope | L3S domain |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
for cl in CLASSES:
    b = D['domain']['by_class'][cl]
    lines.append(f"| {cl} | {b['what']} | {b['cases']} | {b['runs']} | {b['subset_mask_cases']} / {b['full_chip_cases']} | yes | yes | yes | yes | "
                 f"{b['subset_mask_cases']} | {b['full_chip_cases']} |")
lines += ['', f"- MM1-v0 and MM1-v1 (not declared models here, not probed): each has a gemmL form (mm1_v0.py classes_gemmL, subsets at the "
              f"full chip's footprint; mm1_core.py Shape with the masked map).",
          f"- **NOT APPLICABLE:** {D['domain']['not_applicable']}.",
          f"- **Domain limits, REPORTED apart:** {D['domain']['domain_limits_reported']}.",
          '- **OUT OF DOMAIN: none** (0 cases): there is no E221 arm class without a frozen MM1 form, so every case is forecast and scored.']
for title, key in (('a. The runs', 'runs'), ('b. The quantities', 'quantities'), ('The models', 'models'),
                   ('The forecast procedure', 'forecast_procedure'), ('c. The metric', 'metric'), ('d. The comparisons', 'comparisons'),
                   ('e. Reported beside (deciding nothing)', 'reported_beside'), ('f. The pass rule (decided by a script)', 'pass_rule'),
                   ('g. The label rule', 'label_rule'), ('h. The nominal footing (a second footing, frozen now, scored beside)', 'nominal'),
                   ('i. Earlier reads, disclosed', 'earlier_reads')):
    lines += md_sec(title, D[key])
lines += ['', '## The inputs, by sha256', '']
for p, h in inputs_sha.items():
    lines.append(f'- `{h}`  {p}')
lines += ['', 'SPDX-License-Identifier: Apache-2.0', '']
open(MD, 'w').write('\n'.join(lines))
print('written', made)
print(sha(MD), 'DECLARED-blind-e221.md')
print(sha(JS), 'DECLARED-blind-e221.json')
