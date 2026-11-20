#!/usr/bin/env python3
"""decl-e219 (Q232) step 1e: write DECLARED-blind-e219.md and DECLARED-blind-e219.json, the lab's BLIND test of its frozen models on E219
(the model session's fifth matmul sweep, 1119-mmsweep5, #14), declared before any E219 datum exists, MM1's domain stated first.
decl-e217's s01e_declare.py in form. Reads only this lane's step-0/1 files (the registered arms and schedules, the models' records, the
bands, the MM1-v3.2 check) and the orchestrator's record of E219's claims; writes the two files.
Run: /usr/bin/python3 -I -B s01e_declare.py <lane dir>"""
import collections
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

L = os.path.abspath(sys.argv[1])
W = os.path.normpath(os.path.join(L, '..', '..'))
S1 = os.path.join(L, 'work', 'step1')
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
LAY = os.path.join(MM1, 'v3.2-terms', 'layout')
LNC = os.path.join(MM1, 'v3.2-terms', 'gemmlnc')
SRC = os.path.join(L, 'work', 'e219-src')
TZ = dict(os.environ, TZ='America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def now():
    return subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()


RL = json.load(open(os.path.join(S1, 'runs-listed.json')))
MS = json.load(open(os.path.join(S1, 'models-step1.json')))
BD = json.load(open(os.path.join(S1, 'bands.json')))
V32S = json.load(open(os.path.join(L, 'work', 'v32-status.json')))
V32 = V32S['status'] == 'INCLUDED'
REL = open(os.path.join(W, 'out', 'orch', 'e219-releases.txt')).read()
REL_LINES = [x for x in REL.splitlines() if x.strip() and not x.startswith('# ')]   # '# ' is the file's header; '#14...' lines are posts
claim_files = sorted(f for f in os.listdir(os.path.join(W, 'out', 'orch')) if f.startswith('claim-'))
QUIET = os.path.exists(os.path.join(W, 'locks', 'quiet-desk-aifoundry2'))
R = RL['runs']
CASES = RL['cases']
INC = [c for c in CASES if c['domain'] == 'IN']
OUTC = [c for c in CASES if c['domain'] == 'OUT']
C1, C0 = 'aifoundry1 card 1', 'aifoundry1 card 0'
DECLARED_AT = now()
cnt = RL['counts']
by_s = collections.Counter(r['session'] for r in R)
cls_tab = collections.Counter((c['card'], c['class']) for c in CASES)
cls_runs = collections.Counter((r['card'], r['class']) for r in R)
fmt_tab = collections.Counter((c['card'], c['fmt'], c['domain']) for c in CASES)
kind_tab = collections.Counter((c['card'], c['kind'], c['domain']) for c in CASES)
tok_out = collections.defaultdict(list)
for c in OUTC:
    tok_out[c['class']].append(c['token'])
bands = {card: {q: BD['cards'][card]['bands'][q]['band'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')} for card in (C1, C0)}
for card in (C1, C0):
    bands[card]['watts_W'] = BD['cards'][card]['band_w']['band_W']
    bands[card]['arithmetic'] = {q: BD['cards'][card]['bands'][q]['arithmetic'] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4')}
    bands[card]['arithmetic']['watts'] = BD['cards'][card]['band_w']['arithmetic']
ties = {card: BD['cards'][card]['ties'] for card in (C1, C0)}
assert BD['check_card1_all_equal'], 'card 1 bands differ from E215 arm B'
carm = MS['carm_training_record']['MM1-v3.1']
c16r_R = sorted({c['shape']['R'] for c in INC if c['class'] == 'C16R'})
c16r_fit_R = sorted({int(a[len('gemmc16r'):]) for arms in carm['arms_by_card_time'].values() for a in arms if a.startswith('gemmc16r')})
ctab_tok = sorted({c['token'] for c in INC if c['class'] == 'CTAB'})
sub_cases = [c for c in INC if c['mask'] != '0xffffffff']
twp = MS['twin_preview_nominal']

INPUTS = collections.OrderedDict()
INPUTS['E219 kit src copy: out/orch/e219-src/SRC-SHA256SUMS.txt (49/49 OK)'] = sha(os.path.join(SRC, 'SRC-SHA256SUMS.txt'))
INPUTS['E219 src/arms.json'] = sha(os.path.join(SRC, 'src', 'arms.json'))
for s in sorted(RL['sessions']):
    INPUTS[f'E219 src/sched/{s}.json'] = RL['sessions'][s]['sched_sha256']
INPUTS['E219 src/README.md'] = sha(os.path.join(SRC, 'src', 'README.md'))
INPUTS['E219 src/mms_common.py (the cards; the arm grammar arm_of)'] = sha(os.path.join(SRC, 'src', 'mms_common.py'))
INPUTS['E219 src/reduce_mms.py (block arms read by the gemmL rules)'] = sha(os.path.join(SRC, 'src', 'reduce_mms.py'))
INPUTS['MM1-v3.1 out/mm1_v31_params.json'] = sha(os.path.join(MM1, 'v3.1', 'out', 'mm1_v31_params.json'))
INPUTS['MM1-v3.1 SHA256SUMS (2c971828; 64/64 OK)'] = sha(os.path.join(MM1, 'v3.1', 'SHA256SUMS'))
INPUTS['MM1-v3.1 counts/SHA256SUMS (3e8991d0; 71/71 OK)'] = sha(os.path.join(MM1, 'v3.1', 'counts', 'SHA256SUMS'))
INPUTS['MM1-v3 out/mm1_v3_params.json'] = sha(os.path.join(MM1, 'v3', 'out', 'mm1_v3_params.json'))
INPUTS['MM1-v3 SHA256SUMS (b1493082; 170/170 OK)'] = sha(os.path.join(MM1, 'v3', 'SHA256SUMS'))
INPUTS['MM1-v2 out/mm1_v2_params.json'] = sha(os.path.join(MM1, 'v2', 'out', 'mm1_v2_params.json'))
INPUTS['MM1-v2 SHA256SUMS (3ca4b717; 114/114 OK)'] = sha(os.path.join(MM1, 'v2', 'SHA256SUMS'))
INPUTS['MM1-v1 SHA256SUMS (domain read only; 77/77 OK)'] = sha(os.path.join(MM1, 'v1', 'SHA256SUMS'))
INPUTS['MM1-v0 SHA256SUMS (domain read only; 14/14 OK)'] = sha(os.path.join(MM1, 'v0', 'SHA256SUMS'))
if V32:
    INPUTS['MM1-v3.2 out/mm1_v32_params.json'] = sha(os.path.join(MM1, 'v3.2', 'out', 'mm1_v32_params.json'))
    INPUTS['MM1-v3.2 SHA256SUMS (GitHub main; all OK)'] = sha(os.path.join(MM1, 'v3.2', 'SHA256SUMS'))
INPUTS['contention term F1 (#1.29.1) forecast-e215-v31-layout.json'] = sha(os.path.join(LAY, 'forecast-e215-v31-layout.json'))
INPUTS['contention term F1 (#1.29.1) eval_layout.py'] = sha(os.path.join(LAY, 'eval_layout.py'))
INPUTS['contention term F1 (#1.29.1) features_layout.py'] = sha(os.path.join(LAY, 'features_layout.py'))
INPUTS['contention term F1 (#1.29.1) out/features_layout.json (the frozen walk cache)'] = sha(os.path.join(LAY, 'out', 'features_layout.json'))
INPUTS['layout term land SHA256SUMS (595fcb59; 25/25 OK)'] = sha(os.path.join(LAY, 'SHA256SUMS'))
INPUTS['gemmLnc term F3 (#1.29) term-gemmlnc.json'] = sha(os.path.join(LNC, 'term-gemmlnc.json'))
INPUTS['gemmLnc term land SHA256SUMS (aaeaa495; 22/22 OK)'] = sha(os.path.join(LNC, 'SHA256SUMS'))
INPUTS["verify-lay's maker v02_fits.py (#1.29.1.1)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_fits.py'))
INPUTS["verify-lay's fits record v02_fits.json (the controls' constants)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_fits.json'))
INPUTS["verify-lay's E215 control columns v02_e215_controls.csv (#1.29.1.1)"] = sha(os.path.join(L, 'work', 'verify-lay', 'v02_e215_controls.csv'))
INPUTS['E215 rules_e215.py (the band form)'] = sha(os.path.join(L, 'work', 'lab', 'tools', 'claims-v3', 'e215', 'rules_e215.py'))
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json'):
    INPUTS[f'work/step1/{n}'] = sha(os.path.join(S1, n))
INPUTS['work/step2/walk-feats-e219.json'] = sha(os.path.join(L, 'work', 'step2', 'walk-feats-e219.json'))
INPUTS['work/v32-status.json'] = sha(os.path.join(L, 'work', 'v32-status.json'))
for n in ('s00a_setup_lab.sh', 's00b_setup_kit.sh', 's00c_v32.sh', 's01_list.py', 's01b_models.py', 's01d_bands.py', 's01e_declare.py',
          's02w_walk.py', 's02b_nominal.py', 's02c_write.py', 'p01_probe.py', 'env.sh', 'run_slot.sh'):
    INPUTS[f'scripts/{n}'] = sha(os.path.join(L, 'scripts', n))

MODEL_LINE = "MM1-v3.1 (2c971828), MM1-v3 (b1493082), MM1-v2 (3ca4b717)" + (", MM1-v3.2 (GitHub main)" if V32 else "")
D = collections.OrderedDict()
D['lane'] = 'decl-e219'
D['round'] = 'Q232'
D['declared_pst'] = DECLARED_AT
D['interpreter'] = f'/usr/bin/python3 {sys.version.split()[0]}, numpy {np.__version__}, single-threaded in slot.sh'
D['lab_commit'] = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
D['label'] = (f"BLIND: {MODEL_LINE}, the contention term F1 (#1.29.1, landed 595fcb59), verify-lay's controls (#1.29.1.1) and the gemmLnc "
              "term (#1.29, landed aaeaa495) frozen and unchanged; this declaration and the nominal forecasts hashed and frozen (FROZEN.txt, "
              "posted by the orchestrator) before any E219 datum exists. A session whose first datum precedes the freeze post is UNREAD for it.")
D['state_at_declaration'] = {'e219_releases_txt_lines': REL_LINES, 'claim_files': claim_files, 'quiet_desk_flag_aifoundry2': QUIET,
                             'reading': ('no E219 claim, session or datum on record: only the proposal (#14) and the naming (#14.1)'
                                         if [x.split()[0] for x in REL_LINES] == ['#14', '#14.1'] else 'MORE THAN THE PROPOSAL AND THE NAMING: see the lines')}
D['mm1_v32'] = V32S
# ------------------------------------------------------------------------------------------------ 0. MM1's domain, first
D['domain'] = collections.OrderedDict()
D['domain']['how'] = ("read from each frozen MM1's code and README (the arm a predictor maps, and what it raises on) and, for MM1-v2, MM1-v3 "
                      "and MM1-v3.1, probed by calling each predictor unchanged on one spec a token (p01): a token IN DOMAIN gets a forecast, "
                      "one OUT OF DOMAIN raises KeyError in every one of them (no class assignment, no walk, no census)")
D['domain']['classes'] = collections.OrderedDict([
    ('gemmL<MB>x<NB>x<KB> (rgm136\'s gemmL loop: CTRL, GAP, ANCHOR)', {
        'domain': 'IN', 'measures': "rgm136's large GEMM: C (MB x NB blocks of 1,024 x 512) = A (MB x KB) x B (KB x NB), cooperative loads, "
                                     "each C tile accumulated over its whole K before one TensorStore; 64 MB NB KB ops a minion a pass",
        'forms': {'MM1-v0': 'yes (mm1_v0.py classes_gemmL)', 'MM1-v1': 'yes (mm1_core.py Shape, gemmL)', 'MM1-v2': 'yes (mm1_core_v2.py)',
                  'MM1-v3': 'yes (engine_v3.py, the census path)', 'MM1-v3.1': 'yes (time_v31.Engine31)',
                  'MM1-v3.2': ('yes (mm1_v32.py: MM1-v3.1\'s equations)' if V32 else 'not on main at this declaration')},
        'cases': sum(1 for c in INC if c['class'] in ('CTRL', 'GAP', 'ANCHOR'))}),
    ("run_gemm's c-arm table (CTAB: " + ', '.join(ctab_tok) + "; the table also holds gemmc8, which E219 does not run)", {
        'domain': 'IN', 'measures': "run_gemm's block walk (E105/E107): B blocks of C (1,024 x 512) = A (1,024 x K) x B (K x 512), B packed "
                                     "by column, cooperative loads, C per block (s: every block's C into the first block's); 64 B ops a minion a pass",
        'forms': {'MM1-v0': 'yes, time and (zeros/random) energy (mm1_v0.py classes_carm; no awake power for aifoundry1 card 0)',
                  'MM1-v1': 'yes (mm1_core.py carm_classes, CARMS)', 'MM1-v2': 'yes (mm1_core_v2.py, the same table)',
                  'MM1-v3': 'yes (engine_v3.py carm, census path 0: run_gemm\'s census NOT RUN)', 'MM1-v3.1': 'yes (the same)',
                  'MM1-v3.2': ('yes (MM1-v3.1\'s equations)' if V32 else 'not on main at this declaration')},
        'cases': sum(1 for c in INC if c['class'] == 'CTAB')}),
    ('gemmc16r<R> (C16R: the R ladder, R ' + ', '.join(str(x) for x in c16r_R) + ')', {
        'domain': 'IN', 'measures': "gemmc16's walk with each of its 16 blocks passed R times before the walk moves on (E107's r<R>); 64 x 16 x R "
                                     "ops a minion a pass",
        'forms': {'MM1-v0': 'NO in its predictor (classes_carm raises KeyError; only its energy refit\'s Qof held the R form)',
                  'MM1-v1': 'yes (carm_classes: re.fullmatch gemmc16r(\\d+): 1 - 1/R of the ops with A and B at the L2, 1/R with A fresh, half of those with B fresh too)',
                  'MM1-v2': 'yes (the same)', 'MM1-v3': 'yes (the same)', 'MM1-v3.1': 'yes (the same)',
                  'MM1-v3.2': ('yes (the same)' if V32 else 'not on main at this declaration')},
        'R_in_any_fit': c16r_fit_R, 'R_never_in_a_fit': [x for x in c16r_R if x not in c16r_fit_R],
        'cases': sum(1 for c in INC if c['class'] == 'C16R')}),
    ('OUT-gemmc (other B, R or shared C: ' + ', '.join(sorted(set(tok_out['OUT-gemmc']))) + ')', {
        'domain': 'OUT', 'measures': 'see the token: ' + "run_gemm's block walk at a B, R or shared-C combination the c-arm table does not hold",
        'forms': {m: 'no (KeyError)' for m in ('MM1-v0', 'MM1-v1', 'MM1-v2', 'MM1-v3', 'MM1-v3.1')}, 'cases': len(tok_out['OUT-gemmc'])}),
    ('OUT-gemmh (' + ', '.join(sorted(set(tok_out['OUT-gemmh']))) + ')', {
        'domain': 'OUT', 'measures': "gemmc's walk with half the K (16 k tiles a block): 32 B R ops a minion a pass",
        'forms': {m: 'no (KeyError)' for m in ('MM1-v0', 'MM1-v1', 'MM1-v2', 'MM1-v3', 'MM1-v3.1')}, 'cases': len(tok_out['OUT-gemmh'])}),
    ('OUT-gemm (' + ', '.join(sorted(set(tok_out['OUT-gemm']))) + ')', {
        'domain': 'OUT', 'measures': "the block walk with B packed by k (E101's layout), cooperative loads: 64 B R ops a minion a pass",
        'forms': {m: 'no (KeyError)' for m in ('MM1-v0', 'MM1-v1', 'MM1-v2', 'MM1-v3', 'MM1-v3.1')}, 'cases': len(tok_out['OUT-gemm'])}),
    ('OUT-mm (' + ', '.join(sorted(set(tok_out['OUT-mm']))) + ')', {
        'domain': 'OUT', 'measures': "the stream loop: a shared pool of N tile pairs, A into the core's scratchpad and B through TenB; N ops a pass",
        'forms': {m: 'no (KeyError)' for m in ('MM1-v0', 'MM1-v1', 'MM1-v2', 'MM1-v3', 'MM1-v3.1')}, 'cases': len(tok_out['OUT-mm'])}),
    ('OUT-tenb (tenb)', {
        'domain': 'OUT', 'measures': ("A held in the core, one B tile streamed through TenB every op; 1 op a pass. MM1's floors (529 cycles fp32/fp16, "
                                      "270 int8) were measured on E101's tenb loop, but no predictor maps the tenb arm"),
        'forms': {m: 'no (KeyError)' for m in ('MM1-v0', 'MM1-v1', 'MM1-v2', 'MM1-v3', 'MM1-v3.1')}, 'cases': len(tok_out['OUT-tenb'])}),
    ('gemmLnc<..> (rgm136\'s non-cooperative branch)', {
        'domain': 'NOT APPLICABLE', 'measures': 'none: E219 runs no gemmLnc arm (the host\'s grammar here has no gemmLnc; the kit spells none)',
        'forms': {'MM1-v3': 'yes', 'MM1-v3.1': 'yes (+ the gemmLnc term F3)', 'MM1-v3.2': ('yes (F3 inside)' if V32 else 'not on main')}, 'cases': 0})])
D['domain']['in_domain'] = {'cases': len(INC), 'runs': sum(1 for r in R if r['domain'] == 'IN'), 'by_card': dict(collections.Counter(c['card'] for c in INC)),
                            'by_class': dict(collections.Counter(c['class'] for c in INC))}
D['domain']['out_of_domain'] = {'cases': len(OUTC), 'runs': sum(1 for r in R if r['domain'] == 'OUT'),
                                'by_card': dict(collections.Counter(c['card'] for c in OUTC)),
                                'by_class': dict(collections.Counter(c['class'] for c in OUTC)),
                                'rule': ("NO FORECAST by any model. The scores report them apart, as the model's domain limit: per class and case the "
                                         "measured cycles an op (wall and the counter's mean), the seconds a pass and the W over idle, with what each "
                                         "class measures (above); never in the pass rule, a comparison or a headline error"),
                                'cases_list': [c['case'] for c in OUTC]}
D['domain']['c_arm_training'] = {'how': "the experiments, cards and clocks of MM1-v3.1's landed c-arm points (out/points_time_v31.csv)",
                                 'time_points': carm['time_points'], 'energy_points': carm['energy_points'],
                                 'by_experiment_card': carm['time_by_exp_card'], 'arms_by_card': carm['arms_by_card_time'],
                                 'reading': ("aifoundry1 card 1 holds E206's gemmc1, gemmc8s and gemmc16s at 600 MHz (configuration twins there); "
                                             "aifoundry1 card 0 holds no c-arm point: every card-0 c-arm case is a card transfer")}
# ------------------------------------------------------------------------------------------------ a. the runs
D['a_runs'] = {
    'n_runs': len(R), 'by_role': cnt['by_role'], 'by_session': dict(by_s), 'by_card': cnt['by_card'], 'by_fmt': cnt['by_fmt'],
    'by_domain': cnt['by_domain'], 'by_class': cnt['by_class'], 'by_kind': cnt['by_kind'],
    'n_cases': len(CASES), 'cases_by_card': cnt['cases_by_card'], 'cases_by_domain': cnt['cases_by_domain'], 'cases_by_class': cnt['cases_by_class'],
    'source': ("the registered kit: the orchestrator's copy of EE/src (out/orch/e219-src, SRC-SHA256SUMS.txt 247456da..., copied 18:21:08 PST): "
               "src/sched/<card>-<S>.json (each run's i, block, role, arm, values, shires, type, form) and src/arms.json; nulls and smoke left out; "
               "no measurement"),
    'run_id': "E219|<card>-<S>|<i:03d>-<arm>, the kit's own run key (run_mms.py: f\"{i:03d}-{arm}\")",
    'time_selection': ("MM1-v3.1's own loader's conditions (data_v31.mms_runs_all = data_v3.mms_runs, unread-e214's and decl-e217's), applied to "
                       "every in-domain token: the session's queue says ran, rc 0, check exact or approx; role not null; values <token>:<gen>:<file> "
                       "with an IN-DOMAIN token and shires present; the primary view (band600 on card 1, win on card 0: reduce_mms.py) has T_op_us, "
                       "cyc_op_max and n_launch >= 1; a c-arm run also needs the reducer's ops_pass_ok true (every counted launch's iters = its "
                       "passes x the grammar's ops a pass). (The loader itself reads gemmL values only: the scorer applies the same conditions to "
                       "the c-arm runs, the reducer reading them by the same rules: reduce_mms.py's BLOCK ARMS note.)"),
    'energy_selection': ("the same, and the primary view's dP_w is not None, its p_mean_w truthy, the run not capped and its role not 'time' "
                         "(data_v31.mms_runs_all's energy condition)"),
    'not_run': 'a listed run that does not run (a session cut short or not run) is NO DATA: never imputed, never re-listed',
    'case': ("(card, arm token, format, kind as the arm spells it: rnd = random, zeros, ones, mask) over all of that card's sessions; the anchor "
             "(4x8x8 int8 random, full chip) is a case like any other; only the gemmL controls run masks (0xf, 0xff): the kit runs every block "
             "arm on the whole chip"),
    'classes': {'CTRL': 'the gemmL 1x1x1 controls (family control): they tie E219 to E217; reported apart',
                'GAP': 'the gemmL gap cells (family gap): full chip', 'ANCHOR': 'the 4x8x8 int8 random anchor',
                'CTAB': "run_gemm's c-arm table arms", 'C16R': 'gemmc16r<R>, the R ladder (gemmc16 is its R = 1)',
                'OUT-*': 'out of domain (section 0)'},
    'class_table_cases': {f'{a}|{b}': v for (a, b), v in sorted(cls_tab.items())},
    'class_table_runs': {f'{a}|{b}': v for (a, b), v in sorted(cls_runs.items())},
    'fmt_table_cases': {f'{a}|{b}|{c}': v for (a, b, c), v in sorted(fmt_tab.items())},
    'kind_table_cases': {f'{a}|{b}|{c}': v for (a, b, c), v in sorted(kind_tab.items())},
    'run_ids': [r['id'] for r in R],
    'cases': [{'case': c['case'], 'runs': c['runs'], 'domain': c['domain'], 'class': c['class'], 'token': c['token'],
               'ops_per_minion_pass': c['ops_per_minion_pass'], 'group_mask': c['group_mask']} for c in CASES]}
D['a2_fit_inclusion'] = ('NO E219 point can be in any fit: E219 has no datum (no session has run). Checked all the same: no E219 token in any '
                         'model\'s inputs or loaders (MM1-v3.1 28 files, MM1-v3 115, MM1-v2 86: 0 hits) and no E219 id in any landed point record '
                         '(MM1-v3.1 E105-E213; MM1-v3 to E212; MM1-v2 to E208).')
D['a3_tiles'] = ("E219 designs no tile: arms.json's tiles table is empty and every tile file its arms name (8 files: randn, zeros, ones and full "
                 "of the three formats) equals the lab's kinds file (tools/claims-v3/kinds/tiles) byte for byte, each a committed blob on main. "
                 "So no switch count is made (step 4 NOT NEEDED): the kinds' committed counts (3e8991d0) are in every model's tables already.")
# ------------------------------------------------------------------------------------------------ b. the quantities
D['b_quantities'] = {
    'per_card': 'aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz)',
    'T1_wall': 'cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1',
    'T2_counter_mean': "the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1",
    'T3_seconds': ("seconds a pass (one GEMM for gemmL; one walk of the blocks, R passes each, for a c-arm): ops_pass x T_forecast(us) x 1e-6 / "
                   "t_pass_s - 1, ops_pass the host's ops a minion a pass by the kit's grammar (64 MB NB KB; 64 B R); at the measured clock T3's "
                   "error equals T1's identically (the reducer's T_op_us = wall / ops): both printed"),
    'E1_J_over_idle_given_t': ("W over idle at the measured op time: W = A + B / t_meas (the predictor's W_affine at the run's conditions) against "
                               "the primary view's dP_w; relative (= J over idle given t) when the case's mean MM1-v3.1 W given t and its mean measured "
                               "dP_w are both 3 W or more; else a WATTS case, scored by the mean of its runs' W - dP_w in watts (E215's form; the "
                               "watts set fixed by MM1-v3.1 and the measurement, the same for every model)"),
    'E2_J_over_idle_t_forecast': '(W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc the W over idle at the model\'s own op time T_fc; at a watts case W_fc - dP_w',
    'E3_J_at_rest_given_t': '(P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run\'s rest, measured, given)',
    'E4_J_at_rest_t_forecast': '(P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1',
    'split': ('per card; per format and kind; per class (CTRL apart: the controls that tie E219 to E217; GAP, ANCHOR, CTAB, C16R); FULL and SUB; '
              'configuration twins apart')}
# ------------------------------------------------------------------------------------------------ the models
MODELS = collections.OrderedDict([
    ('MM1-v3.1', "tools/matmul/mm1/v3.1 (landed 2c971828): mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel 'rgm136', V, t0_c}]); a c-arm token runs as kernel run_gemm (the predictor's own rule: no gemmL prefix)"),
    ('MM1-v3', "tools/matmul/mm1/v3 (landed b1493082): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, f, kernel='rgm136', V=, t0_c=) (c-arms as run_gemm, its own rule)"),
    ('MM1-v2', ("tools/matmul/mm1/v2 (landed 3ca4b717) through MM1-v3's unread_v2_e212.call (its pins and SHA256SUMS checked): card 1 V None "
                "(the 0.517 V footing), card 0 the measured volts; energy for random, zeros and ones (E219's only kinds); no die term"))])
if V32:
    MODELS['MM1-v3.2'] = ("tools/matmul/mm1/v3.2 (on GitHub main by this declaration: work/v32-status.json): mm1_v32.Model(out/mm1_v32_params.json)."
                          "predict_many, as MM1-v3.1's (MM1-v3.1's equations at its refitted constants, its declared layout term, energy E1t + F3)")
MODELS['v3.1+contention'] = ("form F1 (#1.29.1, frozen 09:31:34 PST Thu 19 Nov, landed 595fcb59): T = T_v3.1 x clip(1 + a Phi_fresh, 0.3, 3.0), "
                             "a = -0.08316593007433395 (forecast-e215-v31-layout.json meta), Phi_fresh by the term's eval_layout.phi_of over the masked "
                             "walk's features (the frozen cache holds all three E219 configurations: 1x1x1 at 0xf, 0xff and the full mask); phi_of "
                             "returns 0 at the full mask and off the walk's loops (run_gemm), so the factor is exactly 1 at every full-chip case and "
                             "every c-arm; at 1x1x1 the walk's fresh-line feature is 0 too (the L2 holds it), so the factor is 1 on every E219 case: "
                             "it equals MM1-v3.1 everywhere (computed all the same); energy MM1-v3.1's affine at its own op time")
MODELS['v3.1+gemmLnc'] = ("term F3 (#1.29, landed aaeaa495): NOT APPLICABLE: E219 runs no gemmLnc arm (0 of 207 arms), so it equals MM1-v3.1 on "
                          "every E219 case; not scored")
MODELS['v3.1+both'] = ("the composition declared in reg-e216: time = MM1-v3.1's x the contention factor; W at a measured t = A + (B + dW t_op,v3.1) / t "
                       "with the gemmLnc term's dW, 0 on every E219 case: so it equals 'v3.1+contention' (= MM1-v3.1) on every E219 case")
MODELS['controls'] = ("verify-lay's controls (#1.29.1.1), by v02_fits.py's forms unchanged with its all-data constants (work/verify-lay/v02_fits.json): "
                      "N1+N2 (N1 = 1 - n/32, N2 = N1^2; a = [-0.09348958586302018, 0.11765730189141044]); G1 (hop mean: (110 + 12 h)/(110 + 12 h_full) - 1; "
                      "a = [0.30314251932286107]); G1+N1 (a = [0.6022127706566506, -0.021675728290377668]); the layout-blind F1 (fresh32_bar_narm: "
                      "Phi_fresh averaged over E219's listed configurations of the same (n shires, arm): one configuration each here, whose feature "
                      "is 0 at 1x1x1; a = [-0.17556875184106632]); factor 1 + sum a_i x_i (unclipped, as v02's E215 control columns), 1 at the full "
                      "mask and at every c-arm (the whole chip); time MM1-v3.1's x the factor, energy MM1-v3.1's affine at its own op time; step 2 "
                      "re-makes v02_e215_controls.csv's N3, N1+N2, G1, G1+N1 columns first")
D['models'] = MODELS
D['models_not_declared'] = ("MM1-v0 and MM1-v1 hold c-arm forms too (section 0) but are not among this test's models (the round's model list); "
                            "the model session's sealed E219 forecast (ba9e24aa...) is theirs: not read, not scored here")
D['forecast_procedure'] = {
    'footing_1_measured': ("THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's start-of-run "
                           "records only, MM1-v3 README section 5's form as unread-e214 and decl-e217 did: the primary view's kernel clock kclock_mhz; "
                           "minion volts: card 1 the models' footing 0.517 V, card 0 the primary view's rails.minion.mV / 1000 (else the model's own "
                           "volts at f); the governed base by the model's own G_of_f(card, f); the run's die_start_c (50 C when absent). The terms and "
                           "controls on MM1-v3.1's forecast at the same conditions; the layout features are configuration-only (step 2w)."),
    'fields_read_before_scoring': ("from each committed E219 data JSON ONLY: the top-level card, session and primary_view, and per run: run, i, ran, "
                                   "role, arm, values, type, shires, minions, die_start_c, arm_token, arm_family, ops_pass, ops_pass_ok, and the primary view's "
                                   "kclock_mhz and rails.minion.mV. No time, cycles, power, energy or seconds field is read until the forecasts at "
                                   "those conditions are hashed."),
    'footing_2_nominal': 'the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED beside the primary footing)',
    'counts_as_inputs': ("the switch counts are inputs, never fitted: each model's own tables (MM1-v3.1: MM1-v3's rows + counts 3e8991d0); E219's "
                         "kinds (zeros, ones, random) are committed kinds with committed counts; E219 designs no tile, so counts-e214's and "
                         "counts-e217's rows are not needed and nothing is added"),
    'order': ('0 the work copies and MM1-v3.2\'s check -> 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt (no step 4: no '
              'counts are made); then, after the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> '
              'the read and the scores')}
D['c_metric'] = {
    'error': 'forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W',
    'case': "a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside",
    'twins': ("per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in that "
              "model's TRAINING time configurations (its landed out/points_time_*.csv, E146 store rungs out; the kernel run_gemm for a c-arm, "
              "rgm136 for gemmL); an energy case when that key and its energy kind are in its energy configurations (work/step1/twin-keys.json, "
              "3418b7d8, equal to unread-e214's and decl-e217's). The no-twin cases carry the pass rule and the headline; twins and all cases "
              f"printed beside. At the nominal clocks: MM1-v3.1 {twp['MM1-v3.1']['time_twin_cases_at_nominal_clock']} time-twin and "
              f"{twp['MM1-v3.1']['energy_twin_cases_at_nominal_clock']} energy-twin cases of {len(INC)} in domain, MM1-v2 "
              f"{twp['MM1-v2']['time_twin_cases_at_nominal_clock']} and {twp['MM1-v2']['energy_twin_cases_at_nominal_clock']} (a preview; the "
              "measured clock decides)")}
D['d_comparisons'] = {
    'test': ("the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more cases; "
             "B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none"),
    'd': ("per case, d = |ln(1 + e_B)| - |ln(1 + e_A)| for the pair (A vs B) (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over "
          "every in-domain case both price (twins included); REPORTED beside over the cases that are twins for neither"),
    'ties': ties,
    'ties_how': ("E215's rule (rules_e215.ties_of), unread-e214's and decl-e217's values: card 1 E215 arm B's registered ties; card 0 from E212 "
                 "a1c0-S1/S2's pooled within-case spread (bands.json card0_floors)"),
    'D1_v31_vs_v3': 'MM1-v3.1 vs MM1-v3 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t forecast (E2): per card and pooled, over the in-domain cases; per class REPORTED',
    'D2_v31_vs_v2': 'MM1-v3.1 vs MM1-v2 on H1-H5: per card and pooled; per class REPORTED',
    'D3_layout': (f"on the subset-mask cases ({len(sub_cases)}: the gemmL 1x1x1 controls at 0xf and 0xff), per card and pooled: 'v3.1+contention' "
                  "vs MM1-v3.1, and each control (N1+N2, G1, G1+N1, the layout-blind F1) vs MM1-v3.1, on H1 (wall) and H2 (counter mean). "
                  "Stated before any datum: 'v3.1+contention' and the layout-blind F1 equal MM1-v3.1 there (factor 1: the fresh-line feature is 0 "
                  "at 1x1x1), so those two tie by construction; with at most 6 cases every D3 test reads TOO FEW (fewer than 10 untied cases); "
                  "the count controls' factors differ from 1 by under 1%"),
    'D4_switch': ("NOT APPLICABLE: E219 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random), so the switch route "
                  "with counts against without has nothing to decide here"),
    'verdicts': 'each comparison is a verdict of its own, never part of PASS'}
if V32:
    D['d_comparisons']['D5_v32'] = 'MM1-v3.2 vs MM1-v3.1 and MM1-v3.2 vs MM1-v3 on H1-H5: per card and pooled; per class REPORTED'
D['e_R_ladder'] = {
    'what': ("REPORTED, deciding nothing: on the C16R cases with gemmc16 as R = 1, per card, format and kind, each model's error against R; "
             f"R {c16r_R} in E219; R {c16r_fit_R} were in MM1-v3.1's fit (E107, E119, E126; never on aifoundry1), so R "
             f"{[x for x in c16r_R if x not in c16r_fit_R]} are never-fitted rungs of the same law (1 - 1/R of the ops with A and B at the L2)"),
    'tie_to_E217': ("REPORTED, deciding nothing: each CTRL case's measured mean (wall cycles, counter mean, W over idle) beside the same (card, arm, "
                    "format, kind, mask)'s committed E217 mean where E217 ran it (read by the scoring lane from E217's committed data)")}
D['f_pass_rule'] = {
    'bands': bands,
    'bands_how': ("E215's form (rules_e215.py, unchanged; unread-e214's s01d_bands.py re-run here, the same figures as decl-e217's): 2 x max(B1, B2) "
                  "rounded up to a whole percent, B1 MM1-v3.1's LOEO no-twin error over every point (gemmL and c-arms), B2 over this card's points "
                  "(holdout_v31.json reproduced first, 29/29); T3 takes T1's bases; watts band 2 x max(B1 W, B2 W, SD_rep) rounded up to 0.01 W. "
                  "Card 1's equal E215 arm B's registered bands (checked)."),
    'part_A': ("MM1-v3.1 on the PRIMARY footing by E215's rule form on each card over the IN-DOMAIN NO-TWIN cases (every class: CTRL, GAP, ANCHOR, "
               "CTAB, C16R): a case passes T1, T2, T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a "
               "watts case, |watts difference| within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO "
               "FEW under 10 cases, NO DATA with none. PART A PASSES when no rule FAILS on either card and at least one rule PASSES; FAILS when "
               "any rule fails (named). Printed beside, deciding nothing: each class alone (CTRL apart), FULL and SUB, per format and kind, "
               "twins, the nominal footing."),
    'part_S': 'NOT APPLICABLE (no operand-pattern arm: section d, D4)',
    'verdict': ("PASS when part A passes; FAIL when it fails (named); NOT DECIDED otherwise. Decided by a script: blind-e219's scorer (the scripts "
                "of the lane that scores E219), which implements sections 0-f of this declaration exactly, is code-tested on a stand-in day built "
                "from the frozen forecasts alone, and is hashed (sha256 in its progress log, posted with the result) BEFORE its first read of any "
                "E219 measurement; a departure from this declaration is a dated amendment hashed before that read. The nominal footing (section h) "
                "is scored by the same script and rules beside, REPORTED, deciding nothing. The OUT-OF-DOMAIN cases enter no rule.")}
D['g_label_rule'] = {
    'BLIND': ("a session is BLIND for this test when this declaration's and the nominal forecasts' sha256 (FROZEN.txt) were posted on the Discussion "
              "before the session's first datum (its first card command, the session's own log)"),
    'UNREAD': "a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the post (data-e219's read times on record); else POST-READ (REPORTED)",
    'printed': 'every result line names its label, the freeze post time and the session\'s first card command time'}
D['h_nominal_footing'] = {
    'conditions': {'aifoundry1 card 1': 'f 600.0 MHz; V 0.517 V (the models\' card-1 footing); die at start 60.0 C (the kit\'s start-gate ceiling, mms_common.CARDS a1c1)',
                   'aifoundry1 card 0': ('f 800.0 MHz (its planned clock: the kit\'s main band "800" for the governed card); V the model\'s own volts at f; '
                                         'die at start 55.0 C (the kit\'s a1c0 start-gate ceiling)')},
    'files': ('forecasts-nominal-e219.csv and .json: one forecast a case and model for every in-domain case (every run of a case at the same '
              'nominal conditions); every out-of-domain case listed NOT FORECAST'),
    'scored': 'by the same rules as the primary footing, beside it, REPORTED'}
D['i_earlier_reads'] = {
    'E219_data': 'none exists at this declaration (no session has run)',
    'this_lane': ("read the kit copy's arms.json, schedules, README, mms_common.py (the cards, the arm grammar) and reduce_mms.py's change from "
                  "E217's (block arms read by the gemmL rules), and the 8 tile files' sha256 only; the frozen models' code and READMEs (the domain); "
                  "probe p01 (each predictor on one spec a token) and probe p02 (a code test of this lane's nominal-forecast script: its output "
                  "deleted unread, only its counts and checks printed) ran before this declaration and chose nothing in it; MM1-v3.2's predictor "
                  "docstring in its unlanded lane folder (its call form) and verify-fit-v32's progress log (whether it might land), choosing nothing; "
                  "no E219 forecast of the model session's (its sealed ba9e24aa... was not read); no E217 datum"),
    'others': ("reg-e219 (Q232): the registration from #14 and the same copy; data-e219 (Q232): waiting for releases; the orchestrator: the copy "
               "and the naming (#14.1)")}
D['inputs_sha256'] = INPUTS
D['order'] = D['forecast_procedure']['order']
JP = os.path.join(L, 'DECLARED-blind-e219.json')
json.dump(D, open(JP, 'w'), indent=1)


def fmt_pct(x):
    return f'{round(100 * x)}%'


md = []
A = md.append
A('# decl-e219: the lab\'s BLIND test of its frozen matmul models on E219, DECLARED before any E219 datum exists')
A('')
A(f'*Declared {DECLARED_AT}, round Q232, at the desk on aifoundry2 (work copy of GitHub main {D["lab_commit"][:8]}). Python: /usr/bin/python3 '
  f'{sys.version.split()[0]}, numpy {np.__version__}, single-threaded in slot.sh. Nothing here was measured. E219 (the model session\'s fifth matmul '
  'sweep, 1119-mmsweep5, Discussion #14, named E219 in #14.1) has not run: no E219 datum exists.*')
A('')
A(f'**Label: BLIND.** {D["label"]}')
A('')
A('State at this declaration: out/orch/e219-releases.txt holds ' + str(len(REL_LINES)) + ' post lines (' + D['state_at_declaration']['reading'] + '); '
  f'claim files: {claim_files if claim_files else "none"}; the aifoundry2 quiet-desk flag {"present" if QUIET else "absent"}. '
  f'MM1-v3.2: {V32S["status"]} ({V32S["why"]}).')
A('')
A('## 0. MM1\'s domain, first')
A(f'- How: {D["domain"]["how"]}.')
A(f'- **IN DOMAIN: {len(INC)} cases ({D["domain"]["in_domain"]["runs"]} runs)**, by card {D["domain"]["in_domain"]["by_card"]}, by class '
  f'{D["domain"]["in_domain"]["by_class"]}. **OUT OF DOMAIN: {len(OUTC)} cases ({D["domain"]["out_of_domain"]["runs"]} runs)**, by card '
  f'{D["domain"]["out_of_domain"]["by_card"]}, by class {D["domain"]["out_of_domain"]["by_class"]}.')
A(f'- Out of domain: {D["domain"]["out_of_domain"]["rule"]}.')
A('')
A('| arm class | domain | what it measures | MM1-v0 | MM1-v1 | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | cases |')
A('|---|---|---|---|---|---|---|---|---|---|')
for k, v in D['domain']['classes'].items():
    f = v['forms']
    A(f'| {k} | {v["domain"]} | {v["measures"]} | {f.get("MM1-v0", "")} | {f.get("MM1-v1", "")} | {f.get("MM1-v2", "")} | {f.get("MM1-v3", "")} | '
      f'{f.get("MM1-v3.1", "")} | {f.get("MM1-v3.2", "not on main" if not V32 else "")} | {v["cases"]} |')
A('')
A(f'- The c-arm training record ({D["domain"]["c_arm_training"]["how"]}): {carm["time_points"]} time and {carm["energy_points"]} energy points, '
  f'{carm["time_by_exp_card"]}; {D["domain"]["c_arm_training"]["reading"]}.')
c16 = D['domain']['classes'][[k for k in D['domain']['classes'] if k.startswith('gemmc16r')][0]]
A(f'- The R ladder: R in any fit {c16["R_in_any_fit"]}; R never in a fit {c16["R_never_in_a_fit"]}.')
A('')
A('## a. The runs')
A(f'- **{len(R)} runs** ({cnt["by_role"]}) in E219\'s five sessions ({dict(by_s)}), {cnt["arms_listed"]} arms, **{len(CASES)} cases**; by card '
  f'{cnt["by_card"]} runs, {cnt["cases_by_card"]} cases; by format {cnt["by_fmt"]} runs; by kind {cnt["by_kind"]} runs.')
A(f'- Source: {D["a_runs"]["source"]}. Run id: {D["a_runs"]["run_id"]}. The ids are in `DECLARED-blind-e219.json` (a_runs.run_ids, a_runs.cases).')
A(f'- Time selection: {D["a_runs"]["time_selection"]}')
A(f'- Energy selection: {D["a_runs"]["energy_selection"]}.')
A(f'- {D["a_runs"]["not_run"].capitalize()}.')
A(f'- Case: {D["a_runs"]["case"]}.')
A('- Classes: ' + '; '.join(f'**{k}** {v}' for k, v in D['a_runs']['classes'].items()) + '.')
A('')
A('| card | class | cases | runs |')
A('|---|---|---|---|')
for (a, b), v in sorted(cls_tab.items()):
    A(f'| {a} | {b} | {v} | {cls_runs[(a, b)]} |')
A('')
A(f'- **Fit inclusion:** {D["a2_fit_inclusion"]}')
A(f'- **Tiles:** {D["a3_tiles"]}')
A('')
A('## b. The quantities')
for k, v in D['b_quantities'].items():
    A(f'- **{k}**: {v}')
A('')
A('## The models')
for k, v in D['models'].items():
    A(f'- **{k}**: {v}')
A(f'- Not declared: {D["models_not_declared"]}.')
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
A('## e. Reported beside (deciding nothing)')
for k, v in D['e_R_ladder'].items():
    A(f'- **{k}**: {v}')
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
for k in ('files', 'scored'):
    A(f'- **{k}**: {D["h_nominal_footing"][k]}')
A('')
A('## i. Earlier reads, disclosed')
for k, v in D['i_earlier_reads'].items():
    A(f'- **{k}**: {v}')
A('')
A('## The out-of-domain cases')
A('')
A('| class | tokens (cases) |')
A('|---|---|')
for k in sorted(tok_out):
    tc = collections.Counter(tok_out[k])
    A(f'| {k} | ' + ', '.join(f'{t} ({n})' for t, n in sorted(tc.items())) + ' |')
A('')
A('## The inputs, by sha256')
A('')
A('| input | sha256 |')
A('|---|---|')
for k, v in INPUTS.items():
    A(f'| {k} | `{v}` |')
A('')
A(f'**Order:** {D["order"]}. Every sha256 and time in logs/progress.txt.')
MP = os.path.join(L, 'DECLARED-blind-e219.md')
open(MP, 'w').write('\n'.join(md) + '\n')
print('declared', DECLARED_AT)
print(sha(MP), 'DECLARED-blind-e219.md')
print(sha(JP), 'DECLARED-blind-e219.json')
