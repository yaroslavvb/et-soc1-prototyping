#!/usr/bin/env python3
"""decl-e223 (Q239) step 1e: write the declaration, DECLARED-blind-e223.md and DECLARED-blind-e223.json, at the lane root, from this lane's
step-0/1 records only (no E223 datum exists for this lane: none is opened). decl-e221's s01e_declare.py in form (sections 0, a-i, the
inputs by sha256), E223's runs, classes, held-out sets, cards and models. Refuses to overwrite a declaration whose hash is logged.
Reads W/out/orch/q238-frozen-posts.txt now (copied to work/q238-frozen-posts-at-declaration.txt) and names what it held.
Run: /usr/bin/python3 -I -B s01e_declare.py <lane dir>"""
import collections
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
TZ = dict(os.environ, TZ='America/Los_Angeles')
MD = os.path.join(L, 'DECLARED-blind-e223.md')
JS = os.path.join(L, 'DECLARED-blind-e223.json')
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
LABC = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
REL = open(os.path.join(W, 'out', 'orch', 'e223-releases.txt')).read()
# Q238's freeze posts, read now
QP = os.path.join(W, 'out', 'orch', 'q238-frozen-posts.txt')
QREAD = now()
shutil.copyfile(QP, os.path.join(L, 'work', 'q238-frozen-posts-at-declaration.txt'))
qtxt = open(os.path.join(L, 'work', 'q238-frozen-posts-at-declaration.txt')).read()
posted = {}
for ln in qtxt.splitlines():
    m = re.match(r'^(#[0-9.]+) (\S+ \S+ \S+): (\S+) .*FROZEN\.txt ([0-9a-f]{64})\s*$', ln)
    if m:
        posted.setdefault(m.group(3), []).append({'post': m.group(1), 'at': m.group(2), 'sha256': m.group(4)})
q238 = collections.OrderedDict()
for lane in ('mask-posimb', 'mask-mesh', 'mask-ceiling'):
    fp = os.path.join(W, 'out', lane, 'FROZEN.txt')
    disk = sha(fp) if os.path.exists(fp) else None
    pl = posted.get(lane, [])
    inc = disk is not None and any(p['sha256'] == disk for p in pl)
    q238[lane] = {'posted': pl, 'FROZEN.txt on disk sha256': disk, 'INCLUDED': inc}
assert q238['mask-posimb']['INCLUDED'], 'mask-posimb no longer matches its posted line'
assert not q238['mask-mesh']['INCLUDED'] and not q238['mask-ceiling']['INCLUDED'], ('a further Q238 candidate now qualifies: integrate it first', q238)
R, CC = RL['runs'], RL['cases']
cnt = RL['counts']
CARDS = ['aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0']
CLASSES = RL['classes']
HOSETS = sorted(cnt['ho_cases_by_set'])
by_cl_runs = collections.Counter(r['class'] for r in R)
by_cl_cases = collections.Counter(c['class'] for c in CC)
sub_by_cl = collections.Counter(c['class'] for c in CC if c['group_mask'] == 'SUB')
full_by_cl = collections.Counter(c['class'] for c in CC if c['group_mask'] == 'FULL')
probe_ok = {m: sum(1 for c in CC if DP['cases'][c['case']][m]['time'] == 'FORM' and DP['cases'][c['case']][m]['energy'] == 'FORECAST')
            for m in ('MM1-v3.2', 'MM1-v3.1', 'MM1-v3', 'MM1-v2')}
n_sub = sum(1 for c in CC if c['group_mask'] == 'SUB')
n_full = len(CC) - n_sub
twp = MS['twin_preview_nominal']
bands = {c: {q: v['band'] for q, v in BD['cards'][c]['bands'].items()} for c in CARDS}
bandw = {c: BD['cards'][c]['band_w']['band_W'] for c in CARDS}
ties = {c: BD['cards'][c]['ties'] for c in CARDS}
rel_lines = [x for x in REL.splitlines() if x.startswith('#16')]
PMP = json.load(open(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.4-cands', 'posimb-mask', 'params-posimb-mask.json')))
FITP = json.load(open(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'posimb', 'out', 'fit_results.json')))
FITL = json.load(open(os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.3-cands', 'l3s', 'out', 'fit', 'fit-l3s.json')))
A_HOP, A_LAG = FITP['constants_all_data']['posimb']
LAM = float(FITL['lam_all'])
hos = collections.OrderedDict()
for h in HOSETS:
    cs = [c for c in CC if h in c['ho_sets']]
    hos[h] = {'cases': len(cs), 'runs': cnt['ho_runs_by_set'][h], 'by_card': dict(collections.Counter(c['card'] for c in cs)),
              'classes': dict(collections.Counter(c['class'] for c in cs)), 'subset_mask_cases': sum(1 for c in cs if c['group_mask'] == 'SUB'),
              'full_chip_cases': sum(1 for c in cs if c['group_mask'] == 'FULL'),
              'arms': sorted({c['arm_label'] for c in cs})}

T = 'work/lab/tools/'
INPUTS = ['work/step1/runs-listed.json', 'work/step1/models-step1.json', 'work/step1/twin-keys.json', 'work/step1/bands.json',
          'work/step1/domain-probe.json', 'work/lab-commit.txt', 'work/e223-src/SRC-SHA256SUMS.txt', 'work/e223-src/src/arms.json',
          'work/e223-src/src/README.md', 'work/e223-src/src/mms_common.py', 'work/e223-src/src/reduce_mms.py',
          'work/mask-posimb-FROZEN.txt', 'work/mask-posimb-frozen-lines.txt', 'work/q238-frozen-posts-at-setup.txt',
          'work/q238-frozen-posts-at-declaration.txt',
          T + 'matmul/mm1/v3.2/SHA256SUMS', T + 'matmul/mm1/v3.2/out/mm1_v32_params.json', T + 'matmul/mm1/v3.2/mm1_v32.py',
          T + 'matmul/mm1/v3.1/SHA256SUMS', T + 'matmul/mm1/v3.1/out/mm1_v31_params.json',
          T + 'matmul/mm1/v3/SHA256SUMS', T + 'matmul/mm1/v3/out/mm1_v3_params.json', T + 'matmul/mm1/v3/unread_v2_e212.py',
          T + 'matmul/mm1/v2/SHA256SUMS', T + 'matmul/mm1/v2/out/mm1_v2_params.json',
          T + 'matmul/mm1/v3.3-cands/posimb/SHA256SUMS', T + 'matmul/mm1/v3.3-cands/posimb/SHA256SUMS-note1',
          T + 'matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS', T + 'matmul/mm1/v3.3-cands/gemmlnc-af4/SHA256SUMS-note1',
          T + 'matmul/mm1/v3.3-cands/l3s/SHA256SUMS', T + 'matmul/mm1/v3.3-cands/l3s/SHA256SUMS-note1',
          T + 'matmul/mm1/v3.4-cands/posimb-mask/SHA256SUMS', T + 'matmul/mm1/v3.4-cands/posimb-mask/posimb_mask.py',
          T + 'matmul/mm1/v3.4-cands/posimb-mask/params-posimb-mask.json',
          T + 'claims-v3/e224/desk/models_e224.py', T + 'claims-v3/e224/SHA256SUMS-e224-registration', T + 'claims-v3/e224/SHA256SUMS-e224-kit',
          T + 'claims-v3/e224/forecast-e224.csv', T + 'claims-v3/e222/desk/models_e222.py', T + 'claims-v3/e222/SHA256SUMS-e222-registration',
          T + 'claims-v3/e215/rules_e215.py', 'work/lab/workloads/nocbench/analyze.py']
for s in sorted(os.listdir(os.path.join(L, 'work', 'e223-src', 'src', 'sched'))):
    INPUTS.append('work/e223-src/src/sched/' + s)
SCRIPTS = ['scripts/' + f for f in sorted(os.listdir(os.path.join(L, 'scripts'))) if f.endswith(('.py', '.sh'))]
inputs_sha = {p: sha(os.path.join(L, p)) for p in INPUTS + SCRIPTS}

BASE = ['MM1-v3.2', 'MM1-v3.3', 'MM1-v3.1', 'MM1-v3', 'MM1-v2']
REPORTED = ['MM1-v3.2 + posimb', 'MM1-v3.2 + L3S', 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S',
            'MM1-v3.2 + all three', 'MM1-v3.2 + posimb-mask', 'MM1-v3.2 + AF4 + posimb-mask']
MODELS = BASE + REPORTED
MASKC = ['MM1-v3.2 + posimb', 'MM1-v3.2 + posimb-mask']
D = collections.OrderedDict()
D['label'] = 'BLIND (sessions whose first datum follows the freeze post); UNREAD (any whose first datum precedes it)'
D['experiment'] = ("E223 (#16, 01:25:49 PST Sat 21 Nov 2026): the model session's seventh matmul sweep, 1121-mmsweep7, of E136's rgm136 "
                   "unchanged (kernel ELF aace138c...): 839 runs over 299 gemmL arms of the lab's kinds and an anchor in nine sessions "
                   "(aifoundry1 card 1 S1-S3 at 600 MHz, card 0 S1-S3 low power, aifoundry2 card 0 S1-S3 under the sixth sweep's live stops "
                   "85 W x3 / 80 C), no designed tiles; a blind test of its frozen v3.7, the core-group placement law first with its held-out "
                   "placements in 15 sets, then the held-walk edge, the L3 region, the wide-B wait and the masked energy terms; its sealed "
                   "forecast eb5478f6... is not read here. The kit is the sixth sweep's (E221's) with its name changed: the same cards, bands, "
                   "gates, reducer and run forms (reduce_mms.py, run_mms.py and mms_common.py equal E221's kit copy but for the "
                   "sweep's name: checked by diff with the name masked, so the data JSON's fields are E221's)")
D['state_at_declaration'] = rel_lines + ['(no claim file for E223 at this declaration; aifoundry1\'s push waits for the owner\'s network '
                                         'approval (#16.1.1): its six sessions may not run tonight; a card with no session is NO DATA)']
dom_by = collections.OrderedDict()
for cl in CLASSES:
    dom_by[cl] = {'what': RL['class_what'][cl], 'cases': by_cl_cases[cl], 'runs': by_cl_runs[cl], 'subset_mask_cases': sub_by_cl[cl],
                  'full_chip_cases': full_by_cl[cl], 'MM1-v2': 'yes (probe p01)', 'MM1-v3': 'yes (probe p01)', 'MM1-v3.1': 'yes (probe p01)',
                  'MM1-v3.2': 'yes (probe p01)', 'MM1-v3.3': 'yes: MM1-v3.2 + AF4, AF4 0 here (no gemmLnc)',
                  'posimb and posimb-mask scope': '%d subset-mask cases (their terms act there; MM1-v3.2 at the full chip)' % sub_by_cl[cl],
                  'L3S domain': '%d full-chip cases (MM1-v3.2 at the subset masks)' % full_by_cl[cl]}
D['domain'] = collections.OrderedDict([
    ('verdict', "EVERY E223 case is IN MM1's domain: all 299 arms and the anchor are rgm136's cooperative gemmL<MB>x<NB>x<KB> loop (no "
                "gemmLnc, no block, stream or TenB arm; arms.json and every schedule checked) at the lab's kinds (zeros, ones, random; fp32, fp16, "
                "int8) on the three cards MM1-v3.2 has per-card constants for; NO case is OUT OF DOMAIN, so none is left unforecast"),
    ('evidence', f"probe p01: every one of the {len(CC)} cases has a form (finite wall and mean cycles, op time; energy FORECAST) in "
                 f"MM1-v3.2 {probe_ok['MM1-v3.2']}, MM1-v3.1 {probe_ok['MM1-v3.1']}, MM1-v3 {probe_ok['MM1-v3']}, MM1-v2 {probe_ok['MM1-v2']} "
                 "at the nominal footing (work/step1/domain-probe.json, status only); the models' code: mm1_v32.py, mm1_v31.py, mm1_v3.py and "
                 "MM1-v2 take any gemmL<MB>x<NB>x<KB> token and shire mask on rgm136 (the masked map); the terms' scopes by their own code "
                 "(posimb_rows / posimb_mask.in_scope: mask not 0xffffffff, kernel rgm136, arm gemmL; L3S's domain_key: the full mask; AF4: "
                 "gemmLnc tokens only)"),
    ('by_class', dom_by),
    ('not_applicable', "AF4 (the gemmLnc energy term) acts at no E223 case (no gemmLnc arm): MM1-v3.3 = 'MM1-v3.2 + AF4' equals MM1-v3.2 on "
                       "every case (checked to 1e-12 by its frozen per-row form), and so do 'MM1-v3.2 + posimb + AF4' = 'MM1-v3.2 + posimb', "
                       "'MM1-v3.2 + AF4 + L3S' = 'MM1-v3.2 + L3S', 'MM1-v3.2 + all three' = 'MM1-v3.2 + posimb + L3S' and 'MM1-v3.2 + AF4 + "
                       "posimb-mask' = 'MM1-v3.2 + posimb-mask'; each is forecast and printed all the same (by its construction), and the "
                       "MM1-v3.3 vs MM1-v3.2 sign test reads NO DATA (no untied case) by construction, declared here before any datum"),
    ('domain_limits_reported', "IN the domain but beyond the fits, REPORTED apart (they enter the rules like every case): the core-group "
                               f"placements at shire masks no fit holds (most of E223's {cnt['distinct_masks']} masks), the 26-shire mask, "
                               "MB up to 16, NB up to 24 and KB up to 32; aifoundry2 card 0 and aifoundry1 card 0 under their governors (the "
                               "clock read from each run's start-of-run records; the nominal footing at 800 MHz); configuration twins "
                               "(section c) split"),
    ('held_out_sets', hos),
    ('maske221', "blind-e221's MASK class by its own definition (decl-e221's precedence ANCHOR, L2I8 (family L2I8), CELL1 (families CLK, "
                 "PLS), then MASK = family PL): E223's arms.json carries no L2I8, CLK or PLS code, so MASKE221 = every non-anchor arm of "
                 f"family PL: {cnt['maske221_cases']} cases, {cnt['maske221_runs']} runs, all at subset masks (E223's PL arms have no "
                 "whole-chip member; a whole-chip twin of a PL case is the case of the same card, token, format and kind at 0xffffffff "
                 "wherever E223 runs one)"),
    ('gateset', f"the masked energy cases: every arm of family GATE ({cnt['gateset_cases']} cases), in whichever class (most are PLACE)")])
D['runs'] = collections.OrderedDict([
    ('listed', f"{cnt['listed_runs (arm and anchor; nulls and smoke left out)']} runs ({cnt['by_role']}) of the schedules' 839 (36 nulls and "
               f"each session's smoke left out), {len(CC)} cases (a case = card, arm, format, kind, mask); by session {cnt['by_session']}; by "
               f"card {cnt['by_card']} runs, {cnt['cases_by_card']} cases; by format {cnt['by_fmt']} runs; by kind {cnt['by_kind']} runs; by "
               f"class {dict(by_cl_runs)} runs, {dict(by_cl_cases)} cases; subset masks {n_sub} cases over {cnt['distinct_masks']} masks "
               f"({cnt['subset_configurations (shape, mask)']} subset configurations), the whole chip {n_full} cases; the 15 held-out sets "
               f"{cnt['ho_cases_any']} cases / {cnt['ho_runs_any']} runs (an arm may sit in two sets)"),
    ('ids', "E223|<card>-<S>|<i:03d>-<arm id>: the kit's own run key (run_mms.py), from src/sched/<card>-<S>.json and src/arms.json of "
            "the orchestrator's copy (SRC-SHA256SUMS.txt 627b622e..., 53/53; the kit's own SRC-SHA256SUMS 52/52); the list is "
            "work/step1/runs-listed.json"),
    ('fit_inclusion', "NO E223 point can be in any fit: E223 has no datum for this lane. Checked all the same: no E223 token in any model's "
                      "inputs or loaders (MM1-v3.2 13 files, MM1-v3.1 28, MM1-v3 115, MM1-v2 86, Q234 posimb 23, gemmlnc-af4 20, l3s 25, "
                      "Q238 posimb-mask 29: 0 hits) and no E223 id in any landed point record (MM1-v3.2 to E215, MM1-v3.1 to E213, MM1-v3 "
                      "to E212, MM1-v2 to E208; posimb and L3S to E219, AF4 to E218, posimb-mask to E224)"),
    ('tiles', "E223 designs no tile: arms.json's tiles table is empty and its 9 tile files (6 named by arms) equal the lab's kinds "
              "(tools/claims-v3/kinds/tiles) byte for byte, each a committed blob; so no switch count is made (step 4 NOT NEEDED)")])
D['quantities'] = collections.OrderedDict([
    ('per_card', "aifoundry1 card 1 at 600 MHz (not governed); aifoundry1 card 0 low power under its governor (main band 800 MHz); "
                 "aifoundry2 card 0 under its governor (main band 800 MHz), the kit's live stops"),
    ('T1_wall', 'cycles an op, the slowest minion: forecast cycles_per_op_wall / cyc_op_max - 1'),
    ('T2_counter_mean', "the counter's mean cycles an op: forecast cycles_per_op_mean / cyc_op_mean - 1"),
    ('T3_seconds', "seconds a pass (one GEMM): 64 MB NB KB x T_forecast(us) x 1e-6 / t_pass_s - 1 (the host's ops a minion a pass); at the "
                   "measured clock T3 equals T1 identically (the reducer's T_op_us = wall / ops): both printed"),
    ('E1_W_and_J_over_idle_given_t', "W over idle at the measured op time, W = A + B / t_meas (the predictor's W_affine at the run's "
                                     "conditions) against the primary view's dP_w; its relative error is also J over idle given t's (J = W "
                                     "t_meas on both sides); relative when the case's mean MM1-v3.2 W given t and its mean measured dP_w are "
                                     "both 3 W or more; else a WATTS case scored in watts (E215's form; the watts set fixed by MM1-v3.2 and "
                                     "the measurement, the same for every model)"),
    ('E2_J_over_idle_t_forecast', "(W_fc x T_fc) / (dP_w x t_meas) - 1, W_fc at the model's own op time; at a watts case W_fc - dP_w"),
    ('E3_J_at_rest_given_t', '(P_rest + W given t) / (P_rest + dP_w) - 1, P_rest = p_mean_w - dP_w (the run\'s rest, measured, given)'),
    ('E4_J_at_rest_t_forecast', '(P_rest + W_fc) x T_fc / ((P_rest + dP_w) x t_meas) - 1'),
    ('split', f"per card; per format and kind; per class ({', '.join(CLASSES)}), THE PLACEMENTS FIRST; per held-out set ({', '.join(HOSETS)}); "
              "MASKE221 (blind-e221's MASK by its own definition); GATESET (the masked energy cases); FULL and SUB; configuration twins "
              "apart (section c)")])
D['models'] = collections.OrderedDict([
    ('MM1-v3.2', "THE REGISTERED BASELINE (tools/matmul/mm1/v3.2, landed 4e386f75; SHA256SUMS d52c9cce, 58/58): mm1_v32.Model(out/"
                 "mm1_v32_params.json).predict_many([{card, arm, fmt, kind, mask, f, kernel rgm136, V, t0_c}]); the pass rule's model (section f)"),
    ('MM1-v3.3', "= 'MM1-v3.2 + AF4', E222's registered selection (SEL, read by E222's frozen scorer at 00:57 PST Sat; committed with E222's "
                 "scores c661275c): by its frozen per-row form (tools/claims-v3/e224/desk/models_e224.py af4_rows, = gemmlnc-af4/scripts/"
                 "s03_freeze.py's) on MM1-v3.2's forecast at the same conditions; AF4 acts at gemmLnc tokens only, so at every E223 case it is "
                 "MM1-v3.2 exactly"),
    ('MM1-v3.1', 'tools/matmul/mm1/v3.1 (landed 2c971828; SHA256SUMS f6840d2d, 64/64): mm1_v31.Model(out/mm1_v31_params.json).predict_many'),
    ('MM1-v3', "tools/matmul/mm1/v3 (landed b1493082; SHA256SUMS c24efc14, 170/170): mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, "
               "fmt, kind, mask, f, kernel='rgm136', V=, t0_c=)"),
    ('MM1-v2', "tools/matmul/mm1/v2 (SHA256SUMS eafb6558, 114/114) through MM1-v3's unread_v2_e212.call (blind-e221's caller): card 1 V None "
               "(the 0.517 V footing), the governed cards the measured volts (V_mv); energy for random, zeros and ones (E223's only kinds); no "
               "die term"),
    ('MM1-v3.2 + posimb (REPORTED)', "Q234's layout2 candidate (landed tools/matmul/mm1/v3.3-cands/posimb/; FROZEN-e220 81d04c97), by "
                                     "E224's frozen caller models_e224.posimb_rows (h01_freeze.py's per-row form) at its all-data a_hop = "
                                     f"{A_HOP!r}, a_lag = {A_LAG!r}: in scope at the subset masks of rgm136 gemmL ({n_sub} cases), MM1-v3.2 "
                                     "to the last bit elsewhere; energy MM1-v3.2's affine at the composed op time"),
    ('MM1-v3.2 + L3S (REPORTED)', "Q234's l3-edge candidate (tools/matmul/mm1/v3.3-cands/l3s/), term_l3s.ModelL3S(MM1-v3.2's params, lam "
                                  f"= {LAM!r}, the landed cache + E224's extra records + the frozen set model's records for E223's new "
                                  f"full-mask shapes) by E224's caller: in its domain at the full mask ({n_full} cases), MM1-v3.2 at the "
                                  "subset masks"),
    ('compositions (REPORTED)', "by E222's and E224's construction, no refit (models_e224.compose and compose_sub, E222's SEL restricted to "
                                "the joining terms): 'MM1-v3.2 + posimb + AF4', 'MM1-v3.2 + posimb + L3S', 'MM1-v3.2 + AF4 + L3S', "
                                "'MM1-v3.2 + all three'; E224's own checks run at every case (compose_sub at all three = compose; each "
                                "single term = its own candidate)"),
    ('MM1-v3.2 + posimb-mask (REPORTED)', "Q238's mask-posimb (track P), KEPT by its declared rule, FROZEN 01:48:34 PST (FROZEN.txt "
                                          "0cd8e9da..., posted #1.30.1.2.1.1.1.1.1 at 01:49:15, before any E223 datum), its land folder "
                                          "copied unchanged to work/lab/tools/matmul/mm1/v3.4-cands/posimb-mask/ (46/46 files equal its "
                                          "FROZEN.txt lines): posimb_mask.Model().predict_many_with_af4 at its constants "
                                          f"{json.dumps(PMP['constants'])} on MM1-v3.2 4e386f75 unchanged; in scope at the subset masks of "
                                          "rgm136 gemmL; 'MM1-v3.2 + AF4 + posimb-mask' beside (its own construction)"),
    ('Q238_read', f"W/out/orch/q238-frozen-posts.txt read at {QREAD} (copied to work/q238-frozen-posts-at-declaration.txt): "
                  + '; '.join(f"{k}: posted {[(p['post'], p['at'], p['sha256'][:8]) for p in v['posted']]}, FROZEN.txt on disk "
                              f"{(v['FROZEN.txt on disk sha256'] or 'none')[:8]}, {'INCLUDED' if v['INCLUDED'] else 'NOT INCLUDED'}"
                              for k, v in q238.items())
                  + ". mask-mesh's posted line (FROZEN 02:02:13) does not match its FROZEN.txt on disk (rewritten 02:03:37), so it is not "
                    "in this freeze; mask-ceiling has no FROZEN.txt. A Q238 candidate that qualifies only after this read is not in this "
                    "freeze: it can be scored on E223 only by a dated amendment hashed before E223's first datum, else as UNREAD"),
    ('maker_checks', "before any output, step 2 re-makes: every row of E224's frozen forecast-e224.csv at the lab's kinds (both arms, every "
                     "clock) by E224's own Models.forecast at this work copy, and every row of posimb-mask's frozen forecasts-compose-e222-"
                     "e224.csv at the lab's kinds (probe p02: 2,431 and 294 rows, worst relative difference 0.0)")])
D['forecast_procedure'] = collections.OrderedDict([
    ('footing_1_measured', "THE PRIMARY FOOTING: each frozen predictor unchanged at each run's measured conditions, read from the data's "
                           "start-of-run records only (MM1's README section 5 form, as blind-e221 did): the primary view's kernel clock "
                           "kclock_mhz; minion volts: card 1 the models' footing 0.517 V, the governed cards the primary view's "
                           "rails.minion.mV / 1000 (else the model's own volts at f); the governed base by the model's own G_of_f(card, f); "
                           "the run's die_start_c (50 C when absent). The candidates and compositions on MM1-v3.2's forecast at the same "
                           "conditions, their features configuration-only. The callers: scripts/s02b_nominal.py's forecast_cases(cases, "
                           "cond), the same code that makes the nominal forecasts (blind-e223 imports it unchanged, cond per run)"),
    ('fields_read_before_scoring', "from each committed E223 data JSON ONLY: the top-level card, session and primary_view, and per run: run, "
                                   "i, ran, role, arm, values, type, shires, minions, die_start_c, arm_token, arm_family, ops_pass, "
                                   "ops_pass_ok, and the primary view's kclock_mhz and rails.minion.mV. No time, cycles, power, energy or "
                                   "seconds field is read until the forecasts at those conditions are hashed"),
    ('footing_2_nominal', 'the nominal forecasts frozen now (section h), scored beside by the same rules (REPORTED)'),
    ('counts_as_inputs', "the switch counts are inputs, never fitted: each model's own tables (MM1-v3.1 and MM1-v3.2: MM1-v3's rows + counts "
                         "3e8991d0; counts-e214); E223's kinds (zeros, ones, random) are committed kinds with committed counts; E223 designs "
                         "no tile, so no count is made (no counts-e217 rows: E224's callers run with e217=False)"),
    ('order', "0 the work copies -> 1 this declaration hashed -> 2 the nominal forecasts hashed -> FROZEN.txt (no step 4: no counts); after "
              "the data: the conditions read -> the measured-conditions forecasts hashed -> the scorer hashed -> the read and the scores")])
D['metric'] = collections.OrderedDict([
    ('error', 'forecast / measured - 1 (the MM1 convention); rms % and signed mean (bias) %; watts cases rms and mean in W'),
    ('case', "a case's error = the mean of its runs' errors (each run at its own conditions); per-run figures REPORTED beside"),
    ('twins', "per model: a time case is a twin when (card, kernel, arm, format, mask, the mean of its runs' measured clocks to 25 MHz) is in "
              "that model's TRAINING time configurations (a base model's landed out/points_time_*.csv, E146 store rungs out; a term's model: "
              "MM1-v3.2's keys UNION every point its term's fit read (gemmlnc-af4/data/s01_points.json, posimb/out/points_all.json, "
              "l3s/out/data/points_all.json, posimb-mask/out/points_all.json), a conservative twin); an energy case when that key and its "
              "kind are in its energy configurations (work/step1/twin-keys.json, %s); the no-twin cases carry the pass rule and the headline; "
              "twins and all cases printed beside. At the nominal clocks (a preview; the measured clock decides): MM1-v3.2 %d time / %d "
              "energy twins of %d, MM1-v3.3 %d / %d, MM1-v3.1 %d / %d, MM1-v3 %d / %d, MM1-v2 %d / %d, posimb and L3S and their "
              "compositions %d / %d, posimb-mask %d / %d (it was fitted on E221's 733 cases, many of whose configurations E223 repeats)"
              % (inputs_sha['work/step1/twin-keys.json'][:8], twp['MM1-v3.2']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.2']['energy_twin_cases_at_nominal_clock'], len(CC), twp['MM1-v3.3']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.3']['energy_twin_cases_at_nominal_clock'], twp['MM1-v3.1']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.1']['energy_twin_cases_at_nominal_clock'], twp['MM1-v3']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3']['energy_twin_cases_at_nominal_clock'], twp['MM1-v2']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v2']['energy_twin_cases_at_nominal_clock'], twp['MM1-v3.2 + posimb']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.2 + posimb']['energy_twin_cases_at_nominal_clock'], twp['MM1-v3.2 + posimb-mask']['time_twin_cases_at_nominal_clock'],
                 twp['MM1-v3.2 + posimb-mask']['energy_twin_cases_at_nominal_clock']))])
D['comparisons'] = collections.OrderedDict([
    ('test', 'the exact two-sided sign test (binomial at 1/2) on the untied cases, alpha 0.05: A BETTER if p < 0.05 and A is closer in more '
             'cases; B BETTER the other way; NOT DECIDED otherwise; TOO FEW under 10 untied cases; NO DATA with none'),
    ('d', 'per case d = |ln(1 + e_B)| - |ln(1 + e_A)| (A closer when d > tie); at a watts case |dW_B| - |dW_A| in W; over every case both '
          'price (twins included); REPORTED beside over the cases that are twins for neither'),
    ('ties_how', "E215's rule (rules_e215.ties_of) on the floors of work/step1/bands.json (decl-e221's, equal): card 1 E215 arm B's "
                 "registered ties %s; aifoundry1 card 0 %s (E212 a1c0-S1/S2); aifoundry2 card 0 %s (E212 a2c0-S1/S2: a weak floor, 3 cases "
                 "with two runs)" % (ties['aifoundry1 card 1'], ties['aifoundry1 card 0'], ties['aifoundry2 card 0'])),
    ('D0_v33_vs_v32', "MM1-v3.3 vs MM1-v3.2 on H1 wall, H2 counter mean, H3 seconds, H4 J over idle given t (E1), H5 J over idle with t "
                      "forecast (E2): per card and pooled over every case; it reads NO DATA by construction (AF4 acts at no E223 case), "
                      "declared now"),
    ('D1_v32_vs_v31', 'MM1-v3.2 vs MM1-v3.1 on H1-H5: per card and pooled; per class and per held-out set REPORTED'),
    ('D2_v32_vs_v3', 'MM1-v3.2 vs MM1-v3 on H1-H5: per card and pooled; per class and per held-out set REPORTED'),
    ('D3_masks_REPORTED', "deciding nothing: on THE PLACEMENT CLASS (PLACE, %d cases), each REPORTED mask candidate vs MM1-v3.2 (%s) on "
                          "H1 (wall), H2 (counter mean), H3 (seconds) and H5 (J over idle with t forecast), per card and pooled; the same on "
                          "every subset-mask case (%d), on MASKE221 (%d) and on each held-out set, REPORTED; and the two against each other "
                          "('MM1-v3.2 + posimb-mask' vs 'MM1-v3.2 + posimb') beside" % (by_cl_cases['PLACE'], ', '.join(MASKC), n_sub,
                                                                                         cnt['maske221_cases'])),
    ('D4_L3S_REPORTED', "deciding nothing: 'MM1-v3.2 + L3S' vs MM1-v3.2 on its %d full-mask cases (H1-H5), per card and pooled; the "
                        "compositions vs MM1-v3.2 beside" % n_full),
    ('D5_switch', 'NOT APPLICABLE: E223 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random), so the switch '
                  'route with counts against without has nothing to decide'),
    ('verdicts', 'each comparison is a verdict of its own, never part of PASS')])
D['reported_beside'] = collections.OrderedDict([
    ('classes', "each class's rms and bias per card and model (the placements first, then the held-walk edge, the L3 region, the wide-B "
                "wait, the masked energy cases, the kinds, the 1x1x1 cells, the shape probes, the anchor), REPORTED"),
    ('held_out_sets', "each of the 15 held-out sets' rms and bias per card and model, and part A's cells on each set alone, REPORTED"),
    ('maske221', "blind-e221's MASK class by its own definition: rms and bias per card and model, part A's cells on it alone and on every "
                 "case outside it (so E223 reads blind-e221's finding again), REPORTED"),
    ('mask_ladders', "each subset case against its whole-chip twin (same card, token, format, kind at 0xffffffff) where E223 runs one: "
                     "measured and forecast subset/full ratios per model, REPORTED"),
    ('governed_clock', "on the governed cards: each run's measured clock beside the nominal 800 MHz and the nominal-footing error, REPORTED")])
D['pass_rule'] = collections.OrderedDict([
    ('part_A', "MM1-v3.2 on the PRIMARY footing by E215's rule form on each card over its NO-TWIN cases (every class): a case passes T1, T2, "
               "T3, E3, E4 when |error| is within the band, E1, E2 when |error| is within the band or, at a watts case, |watts difference| "
               "within the watts band; a rule PASSES when at least 90% of its cases pass, FAILS otherwise, TOO FEW under 10 cases, NO DATA "
               "with none. PART A PASSES when no rule FAILS on any card and at least one rule PASSES; FAILS when any rule fails (named); "
               "else NOT DECIDED"),
    ('bands', {c: dict(bands[c], watts_W=bandw[c]) for c in CARDS}),
    ('bands_how', "E215's form by rules_e215.bases from MM1-v3.1's held-out errors (work/step1/bands.json, made by decl-e221's s01d_bands.py "
                  "unchanged on this work copy: every band and tie equal to decl-e221's), the same bands for every model: a declared choice"),
    ('part_A_others_REPORTED', "the same rules for MM1-v3.3 (identical to MM1-v3.2's by construction), MM1-v3.1 (the continuity with E215, "
                               "E217, E219 and E221) and each REPORTED model, REPORTED, deciding nothing"),
    ('part_S', 'NOT APPLICABLE (no operand-pattern arm: D5)'),
    ('verdict', "PASS when part A passes; FAIL when it fails (named); NOT DECIDED otherwise. Decided by a script: blind-e223's scorer (the "
                "scripts of the lane that scores E223, in blind-e221's form), implementing this declaration's sections exactly, code-tested "
                "on a stand-in day built from the frozen forecasts alone, and hashed (sha256 in its progress log, posted with the result) "
                "BEFORE its first read of any E223 measurement; a departure from this declaration is a dated amendment hashed before that "
                "read. The nominal footing (section h) by the same script and rules beside, REPORTED. A session that does not run, or runs "
                "short, is scored on what ran; a card with no session is NO DATA (aifoundry1's six sessions may never run under this freeze)")])
D['label_rule'] = collections.OrderedDict([
    ('BLIND', "a session is BLIND for this test when FROZEN.txt's sha256 lines were posted on the Discussion (#16) before the session's "
              "first datum (its first card command, the session's own log)"),
    ('UNREAD', "a session whose first datum precedes the freeze post is UNREAD for it, provided no lab lane had read its data before the "
               "post (data-e223's read times on record); else POST-READ (REPORTED)"),
    ('printed', 'every result line names its label, the freeze post time and the session\'s first card command time')])
D['nominal'] = collections.OrderedDict([
    ('aifoundry1 card 1', "f 600.0 MHz; V 0.517 V (the models' card-1 footing); die at start 60.0 C (the kit's a1c1 start-gate ceiling)"),
    ('aifoundry1 card 0', "f 800.0 MHz (its planned clock: the kit's main band \"800\"); V the model's own volts at f; die at start 55.0 C "
                          "(the kit's a1c0 start-gate ceiling)"),
    ('aifoundry2 card 0', "f 800.0 MHz (the kit's main band \"800\" for the governed card, its planned governor point: nothing is set); V the "
                          "model's own volts at f; die at start 55.0 C (the kit's a2c0 start-gate ceiling)"),
    ('files', "forecasts-nominal-e223.csv and .json: one forecast a case and model for every case (every run of a case at the same nominal "
              "conditions), all 13 model columns (8 REPORTED)"),
    ('scored', 'by the same rules as the primary footing, beside it, REPORTED')])
D['earlier_reads'] = collections.OrderedDict([
    ('E223_data', "none read: by #16.1.1 no E223 session sends a card command before the lab's E223 freeze post, and "
                  "W/out/orch/e223-releases.txt holds no claim or release at this declaration (not checked on the boxes: this lane made no "
                  "ssh call); this lane opened no EE/sessions/ folder on aifoundry1 or aifoundry2 and no data folder named for E223"),
    ('this_lane', "read the kit copy's arms.json, schedules, README, mms_common.py (the cards, bands and gates) and the 9 tile files' bytes "
                  "against the lab's kinds; the frozen models' code; Q234's candidates and E222's and E224's callers as landed; Q238's "
                  "mask-posimb as frozen; probe p01 (the domain, status only) and probe p02 (a code test of the nominal-forecast script: only "
                  "its checks, counts, scopes and the factor ranges printed; its output deleted unread) ran before this declaration and chose "
                  "nothing in it; no forecast of the model session's (its sealed eb5478f6... was not read)"),
    ('others', "reg-e223 and data-e223 (Q239) run beside: the registration from #16 and the same copy, and the data lane waiting for this "
               "freeze and the releases; Q236 (E222's scores, committed c661275c), Q237 (E224) and Q238 (the mask candidates) beside")])
D['models_list'] = MODELS

made = now()
J = {'what': "decl-e223 (Q239): the lab's BLIND test of its frozen matmul models on E223, DECLARED before any E223 datum",
     'written_pst': made, 'python': sys.version.split()[0], 'lab_commit': LABC, 'models': MODELS, 'models_reported': REPORTED,
     'mask_candidates_reported': MASKC, 'q238_read_at': QREAD, 'q238': q238,
     'n_runs': len(R), 'n_cases': len(CC), 'n_in_domain': len(CC), 'n_out_of_domain': 0, 'classes': CLASSES, 'held_out_sets': HOSETS,
     'cases': [{k: c[k] for k in ('case', 'card', 'arm', 'arm_label', 'fmt', 'kind', 'mask', 'class', 'ho_sets', 'maske221', 'gateset',
                                  'subfamily', 'group_mask', 'MB', 'NB', 'KB', 'ops_per_minion_pass', 'n_shires', 'runs')} for c in CC],
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


lines = ["# decl-e223: the lab's BLIND test of its frozen matmul models on E223, DECLARED before any E223 datum",
         '',
         f"*Lane decl-e223 (round Q239), aifoundry2's desk; written {made}, Pacific time. Desk only: no card, no ssh, no simulator, no commit. "
         f"Interpreter: /usr/bin/python3 {sys.version.split()[0]}, -I -B, single-threaded, every numerical step one slot job. Inputs: a git "
         f"archive of GitHub main {LABC[:8]} (= LAB HEAD), the orchestrator's copy of E223's kit (SRC-SHA256SUMS.txt 627b622e...), Q238's "
         f"frozen mask-posimb (FROZEN.txt 0cd8e9da...). Labels: registered (this file), measured, desk, post hoc, held out, blind; REPORTED "
         f"= printed beside, deciding nothing.*",
         '',
         f'**The experiment.** {D["experiment"]}.',
         '',
         '**The state at this declaration** (W/out/orch/e223-releases.txt):']
lines += ['- ' + x for x in D['state_at_declaration']]
lines += ['', "## 0. MM1's domain, first", '',
          f'- **{D["domain"]["verdict"]}.**', f'- Evidence: {D["domain"]["evidence"]}.', '',
          '| class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | MM1-v3.3 | posimb, posimb-mask scope | L3S domain |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']
for cl in CLASSES:
    b = D['domain']['by_class'][cl]
    lines.append(f"| {cl} | {b['what']} | {b['cases']} | {b['runs']} | {b['subset_mask_cases']} / {b['full_chip_cases']} | yes | yes | yes | yes | "
                 f"yes (= MM1-v3.2) | {b['subset_mask_cases']} | {b['full_chip_cases']} |")
lines += ['', '**The held-out sets** (the proposal\'s 15 HO-<x> families; an arm may sit in two; every set is in the domain):', '',
          '| set | cases | runs | by card | classes | subset / full |', '|---|---|---|---|---|---|']
for h, v in hos.items():
    lines.append(f"| {h} | {v['cases']} | {v['runs']} | {json.dumps(v['by_card'])} | {json.dumps(v['classes'])} | {v['subset_mask_cases']} / "
                 f"{v['full_chip_cases']} |")
lines += ['', f"- **MASKE221:** {D['domain']['maske221']}.", f"- **GATESET:** {D['domain']['gateset']}.",
          f"- **NOT APPLICABLE in effect:** {D['domain']['not_applicable']}.",
          f"- **Domain limits, REPORTED apart:** {D['domain']['domain_limits_reported']}.",
          '- **OUT OF DOMAIN: none** (0 cases): there is no E223 arm class without a frozen MM1 form, so every case is forecast and scored.']
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
print('written', made, 'q238 read', QREAD, json.dumps({k: (v['INCLUDED'], (v['FROZEN.txt on disk sha256'] or '')[:8]) for k, v in q238.items()}))
print(sha(MD), 'DECLARED-blind-e223.md')
print(sha(JS), 'DECLARED-blind-e223.json')
