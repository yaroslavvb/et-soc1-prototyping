#!/usr/bin/env python3
"""unread-e212sw (Q218) step 1d: write declared-unread.json, the machine-readable declaration (before any read of the test runs' power,
energy or seconds). Built from step 1a's run list (schedules, queues, point files), step 1p's phi (tile bytes) and step 1g's search,
plus the rules below. Desk. Run: /usr/bin/python3 -I -B s01d_declare.py <lane dir>
"""
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
S1 = os.path.join(L, 'work', 'step1')
V3 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


R = json.load(open(os.path.join(S1, 'runs-listed.json')))
PHI = json.load(open(os.path.join(S1, 'phi-declared.json')))
e212 = R['e212']
refs = R['e212_refs']


def refs_for(r):
    out = {}
    for q in refs:
        if q['session'] == r['session'] and (q['arm'], q['fmt'], q['mask']) == (r['arm'], r['fmt'], r['mask']):
            out.setdefault(q['kind'], []).append(q['run'])
    return out


def e212_row(r):
    rf = refs_for(r)
    return {'id': f"E212|{r['session']}|{r['run']}", 'session': r['session'], 'card': r['card'], 'run': r['run'], 'arm_label': r['arm_label'],
            'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'], 'priced_as': r['priced_as'], 'mask': r['mask'], 'role': r['role'],
            'block': r['block'], 'refs': rf, 'share_of_D': ('random' in rf and 'zeros' in rf)}


def pt_row(x):
    return {'id': f"{x['exp']}{x['exp_arm'] if x['exp'] == 'E206' else ''}|{x['point']}", 'exp': x['exp'], 'exp_arm': x['exp_arm'],
            'card': x['card'], 'point': x['point'], 'arm': x['arm'], 'fmt': x['fmt'], 'kind': x['kind'], 'priced_as': x['kind'], 'mask': x['mask'],
            'runs': [q['run'] for q in x['runs']], 'refs': x['refs'], 'share_of_D': ('random' in x['refs'] and 'zeros' in x['refs'])}


A212 = [e212_row(r) for r in e212 if r['group'] == 'A']
C212 = [e212_row(r) for r in e212 if r['group'] == 'C']
APT = [pt_row(x) for x in R['e206_e207'] if x['group'] == 'A']
BPT = [pt_row(x) for x in R['e206_e207'] if x['group'] == 'B']
SEEN_V3C = ['003-1x1x1-fp32-den4', '007-1x1x1-fp32-pow2', '008-1x1x1-fp32-den8', '009-1x1x1-fp32-lanes2', '010-1x1x1-fp32-fld_sign',
            '061-1x1x1-int8-i8_den6', '062-1x1x1-int8-i8_den3', '064-1x1x1-int8-i8_pm1', '065-1x1x1-int8-i8_den1',
            '068-1x1x1-fp16-fld16_mant', '069-1x1x1-fp16-den16_4', '071-1x1x1-fp16-den16_10', '072-1x1x1-fp16-fld16_sign',
            '073-1x1x1-fp16-fld16_exp']
for r in A212:
    r['tabulated_by_v3_spec_s02'] = r['session'] in ('a1c1-S2', 'a1c1-S3')
    r['printed_by_v3_design_c_ana1'] = (r['session'] == 'a1c1-S2' and r['run'] in SEEN_V3C)
for r in C212:
    r['tabulated_by_v3_spec_s02'] = r['session'] in ('a1c1-S3', 'a1c1-S4', 'a1c0-S2')
    r['printed_by_v3_design_c_ana1'] = r['id'] in ('E212|a1c0-S2|062-2x4x1-int8-sparse50i', 'E212|a1c1-S4|069-2x4x4-fp32-sparse50f',
                                                   'E212|a1c1-S4|073-2x4x1-int8-sparse50i')
for r in APT + BPT:
    r['read_by_v3_design_c_ana2'] = r['point'] in ('p111', 'p113', 'p114', 'p115')
phi = {f"{x['fmt']}|{x['kind']}": x['phi'] for x in PHI['rows']}
D = {
    'lane': 'unread-e212sw', 'round': 'Q218', 'label': ('UNREAD: MM1-v3 frozen (landed b1493082; work copy of GitHub main 8e91dda6, unchanged since) '
                                                         'and the switch counts frozen (fix-v31counts, SHA256SUMS c74c2d49..., post #2.7.2.1.1 06:28:37 PST) '
                                                         'before this lane reads the runs; not blind: the data existed and data lanes and some MM1-v3 '
                                                         'design lanes had read them (section g)'),
    'declared_pst': time.strftime('%a %d %b %Y %H:%M:%S PST', time.localtime()),
    'interpreter': '/usr/bin/python3 ' + sys.version.split()[0] + ' (-I -B), numpy 1.26.4, single-threaded, inside slot.sh',
    'inputs_sha256': {
        'MM1-v3 SHA256SUMS (work copy, 170/170 OK)': sha(os.path.join(V3, 'SHA256SUMS')),
        'MM1-v3 out/mm1_v3_params.json': sha(os.path.join(V3, 'out', 'mm1_v3_params.json')),
        'MM1-v1 mm1_v1.py': sha(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v1', 'mm1_v1.py')),
        'MM1-v1 out/mm1_v1_params.json': sha(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v1', 'out', 'mm1_v1_params.json')),
        'counts SHA256SUMS (work/counts, 71/71 OK)': sha(os.path.join(L, 'work', 'counts', 'SHA256SUMS')),
        'work/step1/runs-listed.json': sha(os.path.join(S1, 'runs-listed.json')),
        'work/step1/phi-declared.json': sha(os.path.join(S1, 'phi-declared.json')),
        'work/step1/earlier-lanes.json': sha(os.path.join(S1, 'earlier-lanes.json'))},
    'lab_commit': R['lab_commit'],
    'a_runs': {
        'group_A_pass_rule_pool': {'e212_runs': A212, 'e206_e207_points': APT,
                                   'counts': {'e212_runs': len(A212), 'e206_e207_points': len(APT),
                                              'e206_e207_runs': sum(len(x['runs']) for x in APT)}},
        'group_B_reported_phi_only': {'e206_points': BPT, 'why': "E206's fp32 real: its count is E210's committed 'real' row; MM1-v3's phi_of() had no rule"},
        'group_C_reported_sparse50': {'e212_runs': C212, 'why': ("E212's gen-sparse50 arms (file = the lab's sparse50 tile as the pool's pair 0, the rest "
                                                                 "drawn by the sparse50 law): the committed sparse50 kind (the counts lane's reading); "
                                                                 "MM1-v3 read them for time only (data_v3 gives E212 pattern arms no energy)")},
        'not_in_scope': ("every other E212 run (random, zeros, ones: priced and fitted by MM1-v3); E212 a2c0-S3 (never ran); E213 (no data "
                         "file opened; v31-counts: no E213 point NOT FORECAST)"),
        'energy_inclusion_rule_e212': ("as data_v3.mms_runs: ran; role not null; values 'gemmL..:' and shires present; the primary view has T_op_us, "
                                       "cyc_op_max, n_launch >= 1; energy only when the view's dP_w is not None, p_mean_w is truthy, the run "
                                       "is not capped and its role is not 'time'"),
        'energy_inclusion_rule_e206_e207': ("as data_v3.e206_style / e211-style: a run is kept when its host record equals the registered point "
                                            "(arm, type, minions, shire_mask) and t_gemm_s, p_work_w, p_rest_w and cycles_gemm are present; "
                                            "the point = the mean of its kept runs"),
        'references': ("for the share of D: E212, random and zeros runs at the same (arm, fmt, mask) in the same session (the same "
                       "inclusion rule); E206 and E207, the random and zeros points at the same (arm, fmt, mask) in the same experiment "
                       "arm. Without both, the run's share of D is NOT SCORED (said per run).")},
    'b_quantities': {
        'Q1_W_over_idle_given_t': ("each model's W over idle at the run's measured op time t_meas, as MM1-v3 README section 5: W = A + B / t_meas "
                                   "from the predictor called at the run's card, arm, format, kind (priced as declared), mask, clock f (E212: "
                                   "the primary view's kclock_mhz; E206/E207: 600 MHz, as data_v3), volts (aifoundry1 card 1: 0.517 V and "
                                   "aifoundry3: 0.522 V, data_v3's footings; aifoundry2 card 0 and aifoundry1 card 0: the primary view's "
                                   "minion mV / 1000, else volts(card, f)), governed base G_of_f(card, f), die = die_start_c (50 C when "
                                   "absent); t_meas = the primary view's T_op_us (E212). E206/E207 points: their conditions and readings "
                                   "exactly as MM1-v3's own loader records them (data_v3.energy_points(): f 600 MHz, the card footing's volts, "
                                   "G 0, t = mean cycles_gemm / ops / 600 MHz, w = mean(p_work_w - p_rest_w), idle = mean p_rest_w, die = the "
                                   "kept runs' mean die_start_c for E206 arm B and E207, and none (so 50 C) for E206 arm A, as MM1-v3 records "
                                   "every arm-A point). Error = W_fc / W_meas - 1 when W_meas >= 3 W (else the watts difference). W_meas: "
                                   "E212 the primary view's dP_w; E206/E207 the loader's w."),
        'Q2_share_of_D': ("E210's registered metric: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, D = W_R - W_Z measured; W_R, W_Z the "
                          "means of the in-session reference runs (points); W_fc(R) the same model's W given t at each reference run's own "
                          "conditions, averaged. In % of D, signed."),
        'Q3_J_at_rest_given_t_REPORTED': '(P_rest + W_fc) / (P_rest + W_meas) - 1, P_rest the run\'s measured rest (E212 p_mean_w - dP_w; E206/E207 p_rest_w)',
        'Q4_J_over_idle_t_forecast_REPORTED': ("W_fc(t_fc) t_fc / (W_meas t_meas) - 1 at W_meas >= 3 W, t_fc = MM1-v3's op time at the run's "
                                               "clock (the clock is an input)")},
    'c_metric': {
        'case': ("E212: (card, arm, fmt, kind, mask) over the listed sessions; its error = the mean of its runs' errors. E206/E207: the "
                 "registered point (the mean of its kept runs) is the case."),
        'reported': ('rms % and signed mean %, per run and per case; per card, per format, per group (A, B, C), pooled; split by '
                     'configuration twins (a case is a twin when its time configuration (card, kernel, arm, fmt, mask, clock to 25 MHz) is '
                     'among MM1-v3\'s priced energy points (usable3, E146 rungs out) with another kind; every test kind is new to the '
                     'energy fit by construction) and by whether an MM1-v3 design or spec lane tabulated the run\'s power (section g)')},
    'd_comparisons': {
        'V3': 'MM1-v3 as landed, its predictor unchanged, with the frozen counts added as data rows (E210C fp32 S1/S2, SWT fp16/int8) and phi by rule e',
        'N_null_pass_rule': ("each format's mean of the counted kinds on that card: W_N = the mean of MM1-v3's own W given t at the run's "
                             "conditions over the kinds zeros, ones and random of the run's format (all three measured on every test "
                             "configuration's card in E212 and priced by MM1-v3); the same base as V3, only the count's information differs"),
        'N2_REPORTED': 'the same over the ungated counted kinds ones and random only (a stricter null for ungated patterns)',
        'V1_REPORTED': ("MM1-v1 as frozen (25d2e74e; tools/matmul/mm1/v1, 77/77 OK), its kind term where it applies: e_res and phi by its own "
                        "kind_specs (blind_day_v1.kind_specs for E207: e37 ledger fp32.small_int, blind4 M6, blind3 M5; kinds_v1.e206_kind "
                        "for E206 real: ledger v2 real2 rows), card footings as V3, W = A + B / t_meas; NOT FORECAST where its e_res has no "
                        "source: every E212 run (no ledger row or frozen per-tile prediction for any plan tile or sparse50), E206 arm B "
                        "(no card-1 real2 rows). Labels: E207 points blind for MM1-v1 (frozen before E207); E206 arm A points were in "
                        "MM1-v1's own in-sample scoring (its README: 'E206's 6 real points scored, nothing fitted for the kind')"),
        'V3_phi1_REPORTED': 'V3 with phi = 1 (random\'s) for every new kind: the weight of rule e'},
    'e_phi': {'rule': ("MM1-v3's own formula, kinds_v3.phi(fmt, spec), over each kind's tile files (one value a kind, S1 and S2 alike): E212 "
                       "plan tiles their registered file; E206 real kinds_v3.e206_kind's four real2 files; E207 real:blind4 its two files, "
                       "blind3 its one, e37 the generator 'e37'; tile sha256 checked against the registration or the counts rows. Group C: "
                       "MM1-v3's own phi_of('sparse50'). Desk (tile bytes only)."),
              'values': phi},
    'f_pass_rule': {
        'pool': 'group A cases (E212 runs and E206/E207 points pooled)',
        'P1': 'rms of V3\'s Q1 error < rms of N\'s Q1 error, over the group A cases with Q1 (W_meas >= 3 W)',
        'P2': ('exact two-sided sign test on Q1 per case: d = |e_N| - |e_V3|; a tie when |d| < 0.01 (1 percentage point), dropped; '
               'k = cases with d > 0 of n non-ties; p = the exact binomial two-sided p at 1/2; holds when p < 0.05 and k > n - k'),
        'P3': 'rms of V3\'s Q2 error (% of D) < rms of N\'s, over the group A cases with Q2',
        'P4': 'the P2 test on Q2 with ties |d| < 0.01 of D',
        'verdict': ('PASS when P1, P2, P3 and P4 all hold; NOT DECIDED when either sign test has fewer than 6 non-tied cases; else FAIL '
                    '(the failing conditions named). The same four are REPORTED against N2 and, where it applies, V1, and for E212 '
                    'and E206/E207 apart; none of those enters the verdict.'),
        'tie_band_Q1': 0.01, 'tie_band_Q2': 0.01, 'alpha': 0.05, 'min_non_tied': 6},
    'g_earlier_reads': 'see DECLARED-unread.md section g (from work/step1/earlier-lanes.json and digit-masked reads)',
}
json.dump(D, open(os.path.join(L, 'declared-unread.json'), 'w'), indent=1, sort_keys=True)
print('group A E212 runs', len(A212), '; with a share of D', sum(r['share_of_D'] for r in A212))
print('group A E206/E207 points', len(APT), '; with a share of D', sum(r['share_of_D'] for r in APT))
print('group B points', len(BPT), '; with a share of D', sum(r['share_of_D'] for r in BPT))
print('group C runs', len(C212), '; with a share of D', sum(r['share_of_D'] for r in C212))
print('no share of D (group A):', [r['id'] for r in A212 + APT if not r['share_of_D']])
