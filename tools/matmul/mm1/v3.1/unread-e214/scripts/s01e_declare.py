#!/usr/bin/env python3
"""unread-e214 (Q225) step 1e: THE DECLARATION, written before any E214 measurement is read: DECLARED-unread-e214.json and .md.
It gathers step 1's files (runs-listed, models-step1, cells-v31, cells-v3, bands, twin-keys, earlier-lanes; each by sha256) and states the
runs, the fit-inclusion finding, the quantities, the metric, the comparisons, the switch test, phi and the sp_ar4 gate, the pass rule and the
earlier reads. Desk; no E214 data file is opened. Run: /usr/bin/python3 -I -B s01e_declare.py <lane dir>
"""
import collections
import hashlib
import json
import os
import sys
import time

L = os.path.abspath(sys.argv[1])
S1 = os.path.join(L, 'work', 'step1')
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def j(n):
    return json.load(open(os.path.join(S1, n)))


RL, MS, C31, C3, BD, EL = (j('runs-listed.json'), j('models-step1.json'), j('cells-v31.json'), j('cells-v3.json'), j('bands.json'),
                           j('earlier-lanes.json'))
R = RL['runs']
C0, C1 = 'aifoundry1 card 0', 'aifoundry1 card 1'
NEWK = sorted({r['kind'] for r in R if r['kind'].startswith('pattern:') and not r['kind'].startswith('pattern:sparse50')})
groupS = [r['id'] for r in R if r['kind'] in NEWK]
groupC = [r['id'] for r in R if r['kind'].startswith('pattern:sparse50')]
now = time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())
inputs = {
    'MM1-v3.1 out/mm1_v31_params.json': sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json')),
    'MM1-v3.1 SHA256SUMS (work copy of 8bde0182, 64/64 OK)': sha(os.path.join(MM1, 'v3.1', 'SHA256SUMS')),
    'MM1-v3.1 counts/SHA256SUMS (3e8991d0, 71/71 OK)': sha(os.path.join(MM1, 'v3.1', 'counts', 'SHA256SUMS')),
    'MM1-v3 out/mm1_v3_params.json': sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json')),
    'MM1-v3 SHA256SUMS (170/170 OK)': sha(os.path.join(MM1, 'v3', 'SHA256SUMS')),
    'MM1-v2 out/mm1_v2_params.json': sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json')),
    'MM1-v2 SHA256SUMS (114/114 OK)': sha(os.path.join(MM1, 'v2', 'SHA256SUMS')),
    'counts-e214 SHA256SUMS (land dir and work copy, 49/49 OK; verify-counts-e214 HOLDS)': sha(os.path.join(L, 'work', 'counts-e214', 'SHA256SUMS')),
    'E214 registration SHA256SUMS-e214-registration (91/91 OK)': sha(os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e214', 'SHA256SUMS-e214-registration')),
}
for n in ('runs-listed.json', 'models-step1.json', 'cells-v31.json', 'cells-v3.json', 'bands.json', 'twin-keys.json', 'earlier-lanes.json'):
    inputs[f'work/step1/{n}'] = sha(os.path.join(S1, n))
bands = {}
for card in (C1, C0):
    c = BD['cards'][card]
    bands[card] = {q: c['bands'][q]['band'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
    bands[card]['watts_W'] = c['band_w']['band_W']
    bands[card]['arithmetic'] = {q: c['bands'][q]['arithmetic'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
    bands[card]['arithmetic']['watts'] = c['band_w']['arithmetic']
ties = {card: BD['cards'][card]['ties'] for card in (C1, C0)}
inc = MS['inclusion']
D = {
    'lane': 'unread-e214', 'round': 'Q225 (track A)', 'declared_pst': now, 'lab_commit': RL['lab_commit'],
    'interpreter': '/usr/bin/python3 3.12.3 (-I -B), numpy 1.26.4, single-threaded (OMP/OPENBLAS/MKL/NUMEXPR threads 1), inside slot.sh',
    'label': ('UNREAD: MM1-v3.1 (landed 2c971828), MM1-v3 (b1493082) and MM1-v2 (3ca4b717) frozen, unchanged, with the switch counts frozen '
              '(MM1-v3.1 counts/ 3e8991d0, SHA256SUMS c74c2d49...; counts-e214 land dir, SHA256SUMS 4c39d0d3..., verified HOLDS), before this lane '
              'reads any E214 measurement. Not blind: E214\'s data existed (committed Wed 18 Nov 16:44-21:06 PST, notes 10f662e3) and earlier lanes '
              'read them (section g).'),
    'a_runs': {
        'source': ('the registered schedules (tools/claims-v3/e214/proposal/src/sched/<s>.json, each equal to its session\'s queue.json '
                   'sched_sha256), arms.json, and each committed session/queue.json (fields i, block, role, arm, run, form, ran, rc, check, '
                   'checks, flags) and meta-e214-<s>.json (sid, card, schedule) at GitHub main 8bde0182; no measurement column'),
        'counts': RL['counts'], 'sessions': {s: {k: v for k, v in d.items() if k in ('card', 'sid', 'folder', 'sched_equal', 'primary_view',
                                                                                  'n_queue', 'queue_sha256')} for s, d in RL['sessions'].items()},
        'run_ids': [r['id'] for r in R],
        'selection_time': ('as MM1-v3.1\'s own loader data_v31.mms_runs_all (= data_v3.mms_runs): ran; role not null; values gemmL<MB>x<NB>x<KB>: '
                           'and shires present; the primary view (band600 on card 1, win on card 0: reduce_mms.py) has T_op_us, cyc_op_max and '
                           'n_launch >= 1. Nulls are not runs here.'),
        'selection_energy': ('the same, and the primary view\'s dP_w is not None, its p_mean_w is truthy, the run is not capped and its role '
                             'is not "time" (data_v31.mms_runs_all\'s energy condition, every kind read)'),
        'case': ('(card, arm gemmL<MB>x<NB>x<KB>, format, kind as the arm spells it, mask) over all of that card\'s sessions (a case run in two '
                 'sessions is one case), MM1-v3\'s case form; anchors (4x8x8 int8 random) are cases like any other'),
        'groups': {'M (main)': f'every listed run: time for every kind; energy for every kind a model prices ({len(R)} runs)',
                   'S (the switch-pattern arms)': f'the runs of E214\'s 20 new tile kinds ({len(groupS)} runs, {len({r["arm_label"] for r in R if r["kind"] in NEWK})} arms): {NEWK}',
                   'C (the sparse50 pools)': f'pattern:sparse50f / sparse50h / sparse50i ({len(groupC)} runs), priced as the committed sparse50 kind'},
    },
    'a2_fit_inclusion': {
        'finding': ('NO E214 point entered MM1-v3.1\'s fit, nor MM1-v3\'s or MM1-v2\'s: (a) no E214 token in any model\'s inputs or loaders '
                    f"(MM1-v3.1 {inc['search']['MM1-v3.1']['files_searched']} files, MM1-v3 {inc['search']['MM1-v3']['files_searched']}, "
                    f"MM1-v2 {inc['search']['MM1-v2']['files_searched']}: 0 hits); (b) no E214 id in the landed point records "
                    '(points_time / points_energy of each model; MM1-v3.1\'s experiments E105-E213); (c) by git, E214 a1c0-S1\'s data commit '
                    '3b3e4182 (16:44:33 PST) was ON GitHub main f0d58c84 when MM1-v3.1\'s fit started (17:03:47 PST), but data_v31.py reads '
                    'only vendored inputs (inputs/ and ../v3/inputs/) and none is E214\'s; its README section 0: "E214 ... enters only by a '
                    'dated amendment (none was made)". Every other E214 session was committed after the fit started. MM1-v3 (58f01105) and '
                    'MM1-v2 (3ca4b717) predate every E214 datum. So every E214 point is unread for all three models.'),
        'git': inc['git'], 'search_hits': {m: v['hits'] for m, v in inc['search'].items()},
        'records': {m: {f: {'rows': x['rows'], 'e214_ids': x['e214_ids']} for f, x in v.items()} for m, v in inc['records'].items()},
        'twins_note': ('a configuration twin is NOT an E214 point in a fit: it is an E214 case whose configuration (card, kernel, arm, format, '
                       'mask, clock to 25 MHz; energy adds the kind) is among the model\'s training points from other experiments (E208, E212 '
                       'on these cards): split out in every table (section c)'),
    },
    'b_quantities': {
        'how_each_model_is_called': ('at each run\'s measured conditions, as MM1-v3 README section 5 (the unread S4 form): the primary view\'s '
                                     'kernel clock kclock_mhz; minion volts: aifoundry1 card 1 the models\' footing 0.517 V (data_v3.cases, '
                                     'MM1-v2\'s default), aifoundry1 card 0 the primary view\'s minion rail mV / 1000 (else mm1_core_v3.volts); '
                                     'the governed base by the model\'s own G_of_f(card, f); the run\'s die_start_c (50 C when absent). '
                                     'MM1-v3.1: mm1_v31.Model(out/mm1_v31_params.json).predict_many; MM1-v3: mm1_v3.Model(out/mm1_v3_params.json)'
                                     '.predict; MM1-v2: unread_v2_e212.call (MM1-v3\'s caller of MM1-v2: card 1 V None (0.517 footing), G 0; '
                                     'card 0 the measured volts; energy for random, zeros and ones only, any other kind NOT FORECAST in energy; '
                                     'no die term). Kernel rgm136 (E214 runs rgm136 gemmL only). Time is kind-blind in every MM1.'),
        'conditions_read_in_step_2': ('step 2 reads from each committed data-e214-<s>.json ONLY: the top-level card, session and primary_view, and '
                                      'per run: run, i, ran, role, arm, values, type, shires, minions, die_start_c, and the primary view\'s '
                                      'kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read before step 3.'),
        'T1_wall': 'cycles an op, the slowest minion: forecast cycles_per_op_wall (T x f, f the run\'s measured clock) / cyc_op_max - 1',
        'T2_counter_mean': 'the counter\'s mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1',
        'T3_seconds': ('seconds a GEMM: ops x T_forecast(us) x 1e-6 / t_pass_s - 1 (ops = 64 MB NB KB a minion). By the reducer (reduce_mms.py: '
                       'T_op_us = wall / ops, cyc_op_max = sum cycles / ops, kclock = sum cycles / wall, t_pass_s = wall / passes) and with '
                       'the forecast made at the measured clock, T3\'s error equals T1\'s identically: both are scored and printed'),
        'E1_J_over_idle_given_t': ('W over idle at the measured op time: W = A + B / t_meas (the predictor\'s W_affine at the run\'s conditions), '
                                   'against the primary view\'s dP_w; relative (= J over idle given t) when the case\'s mean MM1-v3.1 W given t '
                                   'and its mean measured dP_w are both 3 W or more; else a WATTS case, scored by the mean of its runs\' W - dP_w '
                                   'in watts (E215\'s form; the watts set is fixed by MM1-v3.1 and the measurement, the same set for every model '
                                   'and for E2; Q1 of the switch test keeps Q218\'s own condition, the measured dP_w >= 3 W)'),
        'E2_J_over_idle_t_forecast': ('(W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc the predictor\'s W over idle at its own op time T_fc; at a '
                                      'watts case W_fc - dP_w in watts'),
        'E3_J_at_rest_given_t': '(P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run\'s rest, measured, given)',
        'E4_J_at_rest_t_forecast': '(P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1',
        'split': 'per card (aifoundry1 card 1 at 600 MHz; aifoundry1 card 0 at low power under its governor), per format and kind, configuration twins apart',
    },
    'c_metric': {
        'error': 'forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W',
        'case': 'a case\'s error = the mean of its runs\' errors (each run at its own conditions; Q218\'s form); per-run figures REPORTED beside',
        'twins': ('per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs\' clocks to 25 MHz) is in that '
                  'model\'s TRAINING time configurations (its landed out/points_time_*.csv, E146 store rungs out); an energy case when that key '
                  'and its energy kind are in the model\'s energy configurations (out/points_energy_*.csv; an energy point\'s clock its time '
                  'record\'s, else 600 MHz on a pinned card) (work/step1/twin-keys.json). The no-twin cases carry the pass rule and the headline; '
                  'twins and all cases are printed beside.'),
    },
    'd_comparisons': {
        'pairs': ['MM1-v3.1 vs MM1-v3', 'MM1-v3.1 vs MM1-v2', 'MM1-v3 vs MM1-v2'],
        'rules': 'H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled',
        'd': ('per case, d = |ln(1 + e_B)| - |ln(1 + e_A)| for the pair (A vs B) (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; '
              'over every case both models price (twins included); REPORTED beside over the cases that are twins for neither model'),
        'ties': ties,
        'ties_how': ('E215\'s rule (rules_e215.ties_of): at or above the card\'s replicate floor, never below E209\'s (0.005 in ln for cycles and '
                     'seconds, 0.01 for joules, 0.05 W): card 1 E215 arm B\'s registered ties; card 0 from E212 a1c0-S1/S2\'s pooled within-case '
                     'spread (bands.json card0_floors)'),
        'test': ('the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more '
                 'cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none'),
    },
    'e_switch': {
        'counts': ('MM1-v3.1: its own merged tables (MM1-v3\'s rows + 3e8991d0\'s) with counts-e214\'s 9 fp32 rows at S1 and S2 and 11 fp16/int8 '
                   'rows added in memory by energy_v31\'s own loop (no key collides: asserted); MM1-v3: 3e8991d0\'s rows and counts-e214\'s added to '
                   'energy_v3\'s E210C / SWT the same way (Q218\'s form). Every E214 energy cell has a count and a phi in both (cells-v31.json, '
                   'cells-v3.json: 49 of 49 usable).'),
        'verifier_fixes_applied': ['merge counts-e214\'s two tables in memory (no key collides)',
                                   'pattern:sparse50f, pattern:sparse50h and pattern:sparse50i priced as the committed sparse50 kind (data_v31.SPARSE_GEN plus sparse50h)',
                                   'phi for the 20 new kinds by kinds_v3.phi over E214\'s registered tile files (section e_phi)',
                                   'sp_ar4\'s float gate declared before any E214 energy is read (gate below)'],
        'gate_sp_ar4': ('DECLARED: E210\'s arow50 gate (g_op, g_lane, g8) = (0.5, 0, 0) for fp32 pattern:sp_ar4 (MM1-v3\'s gate_shares as for arow50), '
                        'because the tile\'s A holds 8 all-zero rows (4-7, 12-15) and B none, and its count\'s valid share is 0.500 at S1 and S2, '
                        'equal to arow50\'s (cells-v31.json sp_ar4); the frozen code\'s literal (0, 0, 0) for an unknown kind name is REPORTED beside'),
        'Q1': ('group S, W over idle given t: MM1-v3.1 + the counts against the null N = the mean over zeros, ones and random of the run\'s '
               'format of the same model\'s own W given t at the run\'s conditions (the same base; only the count\'s information differs); '
               'cases with dP_w >= 3 W'),
        'Q2': ('group S, E210\'s metric, the share of D: e_D = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, D = W_R - W_Z measured, R and Z the '
               'random and zeros cases of the same card, arm, format and mask (measured means; W_fc(R) the same model\'s W given t, its runs\' '
               'mean); for the null [(N(P) - W_fc(R)) - (W_P - W_R)] / D; cases with an R and a Z case and D > 0'),
        'N2_REPORTED': 'the null over ones and random only', 'MM1-v3_REPORTED': 'the same with MM1-v3 + the counts', 'group_C_REPORTED': 'sparse50 pools at the committed sparse50 row',
    },
    'e_phi': {'rule': ('MM1-v3\'s own formula, kinds_v3.phi(fmt, {"tiles": [file]}), over each new kind\'s registered tile file (one value a '
                       'kind, KB classes alike), sha256 checked against arms.json; sparse50f/h/i: MM1-v3\'s own phi_of("sparse50")'),
              'values': {k: v['phi'] for k, v in MS['phi_new_kinds'].items()},
              'tiles': {k: {'tile': v['tile'], 'sha256': v['sha256']} for k, v in MS['phi_new_kinds'].items()}},
    'f_pass_rule': {
        'part_A': ('MM1-v3.1 by E215\'s rule form on each card over the NO-TWIN cases: a case passes T1, T2, T3, E3, E4 when |error| is within '
                   'the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| within the watts band; a rule '
                   'PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA with none. PART A PASSES when no '
                   'rule FAILS on either card and at least one rule PASSES; FAILS when any rule fails (named).'),
        'bands': bands,
        'bands_how': ('E215\'s form (rules_e215.py, unchanged): 2 x max(B1, B2) rounded up to a whole percent, B1 MM1-v3.1\'s LOEO no-twin error '
                      'over every point, B2 over this card\'s points (reproduced 29 of 29 of holdout_v31.json first); T3 takes T1\'s bases; '
                      'watts band 2 x max(B1 W, B2 W, SD_rep) rounded up to 0.01 W. Card 1\'s equal E215 arm B\'s registered bands (checked).'),
        'part_S': ('Q218\'s P1-P4 for MM1-v3.1 + the counts against N on group S, pooled over both cards: P1 rms(Q1) < N\'s; P2 the exact '
                   'two-sided sign test on d = |e_N| - |e_V| per case, a tie when |d| < 0.01, holds when p < 0.05 and MM1-v3.1 is closer in '
                   'more; P3 rms(Q2) < N\'s; P4 P2\'s test on Q2 (ties |d| < 0.01 of D). PART S PASSES when P1-P4 hold; NOT DECIDED when either '
                   'sign test has fewer than 6 untied cases; else FAILS (named).'),
        'verdict': ('PASS when part A and part S pass; FAIL when either fails (named); NOT DECIDED otherwise. Decided by scripts/s03_score.py '
                    '(hashed before the read). The comparisons (section d) are verdicts of their own, never part of PASS.'),
    },
    'g_earlier_reads': {
        'data lanes (read every E214 measurement)': {
            'data-e214 (Q220)': 'rsynced each released session read-only, checked it (C0-C9, W), reduced it with the registered reducer, committed it',
            'verify-e214d (Q220)': 're-derived every session from its raw files (183,450 numeric leaves)',
            'fix-e214d (Q220)': 'dated note 1 in each data folder (the checker\'s planning line, a1c1-S1\'s die reference, check K\'s lines)'},
        'parser tests (raw host records, no model, no number reported)': {
            'kit-e215 (Q224), verify-e215, fix-e215, ready-e215': ('E215 kit\'s real-bytes desk test RB-E214 read the 4 committed card-1 sessions\' 376 '
                                                                     'host stdouts (5,951 records) through the host-record parser; printed counts only '
                                                                     '(tools/claims-v3/e215/logs/realbytes-e215.txt)')},
        'never-run scans (configuration tokens only)': ('E215\'s scans (fit-v31\'s e215_v31.py scan, reg-e215, verify-e215: "81,355 files, E214 '
                                                         'included") and ready-e213b2\'s step 6n read E214\'s planned or committed arm names'),
        'named E214 without reading its data': {
            'reg-e214, verify-reg-e214, land-reg-e214 (Q220)': 'the registration, before any E214 datum',
            'counts-e214, verify-counts-e214 (Q225)': 'arms.json and the tiles only: "No E214 measurement ... was read"',
            'lnc-energy (Q225)': '"No E214 data file was read" (E214 holds no gemmLnc arm)',
            'card-e213b2, ready-e213b2 (Q219)': 'E214\'s kit folder by name (before any E214 session)',
            'report-v2-draft (Q226)': 'E214\'s run count and card-minutes from data-e214\'s result; E214\'s unread score PENDING',
            'the orchestrator (CONTEXT 126-129, the Discussion, the status page)': 'claims and releases (runs, card-minutes, no stop); no measurement'},
        'the model session (its own box)': ('ran and reduced every E214 session and sealed its own forecasts (27bf4e19, 804e269b); its models are '
                                            'not scored here'),
        'search': f"scripts/s01g_search.py over {EL['files_read']} lane files (scripts, results, progress logs; card-e215 lanes and E215 data paths skipped): lanes naming an E214 data token: {sorted(EL['lanes'])}",
        'MM1 model lanes': ('no MM1-v3.1 lane read E214 (section a2); MM1-v3 and MM1-v2 predate it. So, unlike Q218 (where MM1-v3\'s design lanes '
                            'had tabulated some of E212\'s runs), no lane that shaped any of the three models read E214.'),
    },
    'inputs_sha256': inputs,
    'order': ('1 this declaration (hashed) -> 2 the conditions and forecasts (hashed) -> the scorer s03_score.py hashed -> 3 the read and the '
              'scores (hashed); every sha256 and time in logs/progress.txt. No E215 datum is opened at any step.'),
}
json.dump(D, open(os.path.join(L, 'DECLARED-unread-e214.json'), 'w'), indent=1, sort_keys=True)

# ------------------------------------------------------------------ the markdown
cnt = RL['counts']
md = []
A = md.append
A('# unread-e214: DECLARED before any E214 measurement is read (MM1-v3.1, MM1-v3, MM1-v2 UNREAD on E214)')
A('')
A(f"*Declared {now}, round Q225 track A, at the desk on aifoundry2 (work copy of GitHub main {RL['lab_commit'][:8]}). Python: /usr/bin/python3 "
  "3.12.3, numpy 1.26.4, single-threaded in slot.sh. Nothing here was measured; no E214 data file was opened for this declaration.*")
A('')
A('**Label: UNREAD.** ' + D['label'])
A('')
A('## a. The runs')
A(f"- **{cnt['listed_runs (arm and anchor; nulls left out)']} runs** ({cnt['by_role']}) in E214's seven sessions, {cnt['arms_listed']} arms, "
  f"{cnt['cases']} cases; by card {cnt['by_card']}; by format {cnt['by_fmt']}. All {cnt['ran']} ran (queue), rc 0, every check exact or approx, no flag.")
A('- Source: ' + D['a_runs']['source'] + '. The run ids are in `DECLARED-unread-e214.json` (a_runs.run_ids) and `work/step1/runs-listed.json`.')
A('- Time selection: ' + D['a_runs']['selection_time'])
A('- Energy selection: ' + D['a_runs']['selection_energy'])
A('- Case: ' + D['a_runs']['case'])
for k, v in D['a_runs']['groups'].items():
    A(f'- Group {k}: {v}')
A('')
A('### a2. Did any E214 point enter MM1-v3.1\'s fit?')
A('**' + D['a2_fit_inclusion']['finding'] + '**')
A('')
A('| session | data commit | committed (PST) | on main when MM1-v3.1 was fitted (f0d58c84)? |')
A('|---|---|---|---|')
for s, g in sorted(inc['git'].items()):
    v31 = [x for k, x in g.items() if k.startswith('MM1-v3.1')][0]
    A(f"| {s} | {g['data_commit'][:8]} | {g['committed']} | {v31} |")
A('')
A('Twins: ' + D['a2_fit_inclusion']['twins_note'] + '.')
A('')
A('## b. The quantities')
for k in ('how_each_model_is_called', 'conditions_read_in_step_2', 'T1_wall', 'T2_counter_mean', 'T3_seconds', 'E1_J_over_idle_given_t',
          'E2_J_over_idle_t_forecast', 'E3_J_at_rest_given_t', 'E4_J_at_rest_t_forecast', 'split'):
    A(f'- **{k}**: {D["b_quantities"][k]}')
A('')
A('## c. The metric')
for k, v in D['c_metric'].items():
    A(f'- **{k}**: {v}')
A('')
A('## d. The comparisons')
for k in ('pairs', 'rules', 'd', 'ties_how', 'test'):
    A(f'- **{k}**: {D["d_comparisons"][k]}')
A(f"- ties: card 1 {ties[C1]}; card 0 {ties[C0]}")
A('')
A('## e. The switch-pattern arms, the counts, phi and the sp_ar4 gate')
for k in ('counts', 'gate_sp_ar4', 'Q1', 'Q2', 'N2_REPORTED', 'MM1-v3_REPORTED', 'group_C_REPORTED'):
    A(f'- **{k}**: {D["e_switch"][k]}')
A('- verify-counts-e214\'s fixes applied: ' + '; '.join(D['e_switch']['verifier_fixes_applied']) + '.')
A('- phi (' + D['e_phi']['rule'] + '):')
A('')
A('| kind | phi | tile | sha256 |')
A('|---|---|---|---|')
for k, v in sorted(MS['phi_new_kinds'].items()):
    A(f"| {k} | {v['phi']:.6f} | `{v['tile']}` | `{v['sha256'][:16]}...` |")
A('')
A('## f. The pass rule (decided by scripts/s03_score.py)')
A('- **Part A:** ' + D['f_pass_rule']['part_A'])
A('- Bands (' + D['f_pass_rule']['bands_how'] + '):')
A('')
A('| card | T1 | T2 | T3 | E1 | E2 | E3 | E4 | watts |')
A('|---|---|---|---|---|---|---|---|---|')
for card in (C1, C0):
    b = bands[card]
    A(f"| {card} | {b['T1']:.0%} | {b['T2']:.0%} | {b['T3']:.0%} | {b['E1']:.0%} | {b['E2']:.0%} | {b['E3']:.0%} | {b['E4']:.0%} | {b['watts_W']:.2f} W |")
A('')
for card in (C1, C0):
    A(f"- {card}: " + '; '.join(f'{q} {t}' for q, t in bands[card]['arithmetic'].items()))
A('- **Part S:** ' + D['f_pass_rule']['part_S'])
A('- **Verdict:** ' + D['f_pass_rule']['verdict'])
A('')
A('## g. Earlier reads of E214, disclosed')
for k, v in D['g_earlier_reads'].items():
    if isinstance(v, dict):
        A(f'- **{k}**:')
        for k2, v2 in v.items():
            A(f'  - {k2}: {v2}')
    else:
        A(f'- **{k}**: {v}')
A('')
A('## The inputs, by sha256')
A('')
A('| input | sha256 |')
A('|---|---|')
for k, v in inputs.items():
    A(f'| {k} | `{v}` |')
A('')
A('**Order:** ' + D['order'])
A('')
open(os.path.join(L, 'DECLARED-unread-e214.md'), 'w').write('\n'.join(md))
for n in ('DECLARED-unread-e214.md', 'DECLARED-unread-e214.json'):
    print(sha(os.path.join(L, n)), n)
