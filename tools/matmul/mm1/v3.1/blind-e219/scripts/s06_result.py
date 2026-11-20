#!/usr/bin/env python3
"""decl-e219 (Q232) step 6: result.md and result.json at the lane root, from this lane's own files (the hashes, the progress log, the
declaration, the nominal forecasts' meta, the recheck, the land dir's SHA256SUMS) and the orchestrator's E219 release record. Desk.
Run: /usr/bin/python3 -I -B s06_result.py <lane dir>"""
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
TZ = dict(os.environ, TZ='America/Los_Angeles')
LAND = os.path.join(L, 'land')
D = os.path.join(LAND, 'tools', 'matmul', 'mm1', 'v3.1', 'blind-e219')
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


now = subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()
DE = json.load(open(os.path.join(L, 'DECLARED-blind-e219.json')))
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e219.json')))['meta']
RC = json.load(open(os.path.join(L, 'work', 'recheck', 'recheck.json')))
V32 = json.load(open(os.path.join(L, 'work', 'v32-status.json')))
REL = [x for x in open(os.path.join(W, 'out', 'orch', 'e219-releases.txt')).read().splitlines() if x.startswith('#14')]
CLAIMS = sorted(f for f in os.listdir(os.path.join(W, 'out', 'orch')) if f.startswith('claim-'))
LAB = '<LAB>'
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=ENV).stdout.strip()
v32_now = subprocess.run(['git', '-C', LAB, 'ls-tree', '--name-only', head, 'tools/matmul/mm1/v3.2'], capture_output=True, text=True, env=ENV).stdout.strip()
nland = sum(1 for _ in open(os.path.join(D, 'SHA256SUMS'))) + 1
H = {n: sha(os.path.join(L, n)) for n in ('DECLARED-blind-e219.md', 'DECLARED-blind-e219.json', 'forecasts-nominal-e219.csv',
                                          'forecasts-nominal-e219.json', 'FROZEN.txt')}
H['logs/step1-sha256.txt'] = sha(os.path.join(L, 'logs', 'step1-sha256.txt'))
H['logs/step2-sha256.txt'] = sha(os.path.join(L, 'logs', 'step2-sha256.txt'))
H['work/step2/fc-nominal.json'] = sha(os.path.join(L, 'work', 'step2', 'fc-nominal.json'))
H['land SHA256SUMS'] = sha(os.path.join(D, 'SHA256SUMS'))
dom = DE['domain']
e219_claim = any('CLAIM' in x for x in REL)

findings = [
    {'severity': 'info', 'what': (f"MM1's domain covers {dom['in_domain']['cases']} of E219's {DE['a_runs']['n_cases']} cases "
                                  f"({dom['in_domain']['runs']} of {DE['a_runs']['n_runs']} runs): rgm136's gemmL loop (CTRL 8, GAP 34, ANCHOR 2) and "
                                  "run_gemm's c-arms in the models' table (CTAB 22: gemmc1, gemmc4s, gemmc8s, gemmc16, gemmc16s; C16R 73: gemmc16r<R>). "
                                  f"{dom['out_of_domain']['cases']} cases ({dom['out_of_domain']['runs']} runs) are OUT OF DOMAIN: {dom['out_of_domain']['by_class']}; "
                                  "every one raises KeyError in MM1-v2, MM1-v3 and MM1-v3.1 (probe p01 and the recheck, 175/175 each)."),
     'fix': 'None: declared before any datum; the scores report the OUT cases apart (measured only) as the domain limit.'},
    {'severity': 'info', 'what': ("The c-arm forms are hand-assigned class tables from E105/E107 (mm1_core carm_classes): gemmc16 and gemmc8 get "
                                  "the same classes, and so do gemmc4s and gemmc8s, so every model forecasts gemmc4s = gemmc8s and gemmc16 = gemmc8 "
                                  "in time (p01: 851.1 and 1,485.7 cycles an op on card 1 at 600 MHz for MM1-v3.1); E219 runs gemmc4s and gemmc8s "
                                  "both, so their measured difference is one MM1 cannot forecast by construction."),
     'fix': 'None before the data; the scoring lane can print the gemmc4s/gemmc8s pair beside, REPORTED.'},
    {'severity': 'info', 'what': ("The C16R ladder runs R = 2, 3, 4, 5, 6, 8, 12, 16, 24, 32; R = 3, 5, 6, 12, 16 and 24 were never in any fit "
                                  "(MM1-v3.1's c-arm points: R 2, 4, 8, 32 from E107 on aifoundry3 and E119/E126 on aifoundry2); aifoundry1 card 0 "
                                  "holds no c-arm training point at all (every card-0 c-arm case is a card transfer), card 1 holds E206's gemmc1, "
                                  "gemmc8s and gemmc16s at 600 MHz (configuration twins: 4 time-twin CTAB cases on card 1 at the nominal clock)."),
     'fix': 'None: the R ladder is REPORTED beside (section e); twins are split by the declared rule.'},
    {'severity': 'low', 'what': ("D3 (the layout comparisons) cannot decide on E219: its only subset-mask cases are the 6 gemmL 1x1x1 controls at "
                                 "0xf and 0xff, where F1 and the layout-blind F1 equal MM1-v3.1 by construction (the fresh-line feature is 0 at 1x1x1) "
                                 "and the count controls move the time by under 1% (factors 0.995-1.008); every D3 test reads TOO FEW (fewer than 10 "
                                 "untied cases). Stated in the declaration before any datum."),
     'fix': 'None: E219 is not a layout test; E216 and E218 carry the layout question.'},
    {'severity': 'info', 'what': (f"MM1-v3.2 was NOT on GitHub main at the declaration ({V32['why']}) nor at the freeze (LAB HEAD then 5478fce9, "
                                  f"E216's scores, 18:37:05, no tools/matmul/mm1/v3.2); at this result LAB HEAD {head[:8]}, v3.2 "
                                  f"{'present' if v32_now else 'absent'}. So the freeze holds MM1-v3.1, MM1-v3 and MM1-v2 with the terms and controls; "
                                  "'v3.1 + gemmLnc' NOT APPLICABLE (no gemmLnc arm) and 'v3.1 + both' = 'v3.1 + contention' = MM1-v3.1 on every case."),
     'fix': ("If the orchestrator wants MM1-v3.2 blind on E219 and it lands before E219's first datum: a dated addendum (v3.2 as a declared "
             "model, D5 v3.2 vs v3.1 and vs v3) and v3.2's nominal forecasts by this lane's s02b (it includes v3.2 when work/v32-status.json "
             "reads INCLUDED), hashed and posted as a second freeze line before that datum.")},
    {'severity': 'low', 'what': ("Two probes ran before the declaration: p01 (each predictor on one spec a token, to state the domain) and p02 (a "
                                 "code test of the nominal-forecast script; its output deleted unread, only counts and checks printed); the "
                                 "declaration was first written at 18:36:51 and rewritten at 18:37:19 for one wording fix (the R-ladder form), before "
                                 "any hash was logged. All disclosed in the declaration's section i and the progress log."),
     'fix': 'None needed.'},
    {'severity': 'info', 'what': ("E219 designs no tile: arms.json's tiles table is empty and all 8 tile files are the lab's kinds byte for byte "
                                  "(randn, zeros, ones, full; committed blobs), so step 4 (counts) was NOT NEEDED; E219's kinds are zeros, ones and "
                                  "random only, with committed counts in every model's tables."),
     'fix': 'None.'},
]
incidents = [
    "Probe p02's scratch output (the scratchpad's test-s02b/fc-nominal.json) was deleted by a literal-path rm, unread.",
    "The declaration writer ran twice (18:36:51, 18:37:19) before the step-1 hash; the first output was overwritten, never hashed or posted.",
    "A few short read-only 'python3 -c' one-liners and 'python3 - <<EOF' heredocs ran in Bash calls to inspect JSON (no hook refused one).",
    "Main moved twice during the lane (2b25bd4a, E217 a1c1-S3's data; 5478fce9, E216's scores, 18:37:05): neither touched tools/matmul.",
]
open_issues = [
    ("For the orchestrator: post FROZEN.txt's four sha256 on #14 as the lab's freeze line before E219's first session: DECLARED-blind-e219.md "
     f"{H['DECLARED-blind-e219.md'][:8]}..., DECLARED-blind-e219.json {H['DECLARED-blind-e219.json'][:8]}..., forecasts-nominal-e219.csv "
     f"{H['forecasts-nominal-e219.csv'][:8]}..., forecasts-nominal-e219.json {H['forecasts-nominal-e219.json'][:8]}... (FROZEN.txt "
     f"{H['FROZEN.txt'][:8]}...). E217's card-0 S3 was claimed 18:25-19:47 and card 1's S4 follows, so E219's first session may come near "
     "20:30, earlier than 22:00. E219's labels follow the post time, not the file times."),
    ("MM1-v3.2: not on main by the freeze (see findings); an addendum freeze line is possible if it lands before E219's first datum (the orchestrator's call)."),
    ("For blind-e219 (the scoring lane): implement the declaration exactly (sections 0-h): read only the start-of-run fields first (the list in "
     "the forecast procedure, ops_pass_ok included), hash the measured-conditions forecasts, then hash the scorer before the first read; the "
     "c-arm runs' T3 uses the kit grammar's ops a pass (64 B R), the gemmL runs' 64 MB NB KB; the OUT-OF-DOMAIN cases are reported apart, "
     "measured only, never scored; the CTRL tie to E217 and the R ladder REPORTED beside."),
    "The model session's sealed E219 forecast (ba9e24aa...) was not read or scored here.",
]
res = {'lane': 'decl-e219', 'round': 'Q232', 'verdict': 'FROZEN', 'written_pst': now,
       'summary': (f"FROZEN: E219's BLIND test declared (DECLARED-blind-e219.md {H['DECLARED-blind-e219.md'][:8]}, .json "
                   f"{H['DECLARED-blind-e219.json'][:8]}, 18:37:19 PST) and its nominal forecasts frozen (csv {H['forecasts-nominal-e219.csv'][:8]}, "
                   f"json {H['forecasts-nominal-e219.json'][:8]}, 18:37:34) by MM1-v3.1, MM1-v3, MM1-v2, '+contention', '+both' and verify-lay's "
                   f"four controls for the {dom['in_domain']['cases']} in-domain cases ({dom['in_domain']['runs']} runs) of E219's 314; "
                   f"{dom['out_of_domain']['cases']} cases (gemmc at other B/R/shared C, gemmh, gemm, mm16/mm128, tenb) declared OUT OF DOMAIN, "
                   f"not forecast; FROZEN.txt {H['FROZEN.txt'][:8]} at 18:37:50 PST, before any E219 claim or datum; MM1-v3.2 not on main by "
                   "the freeze; no tiles, so no counts; land " + str(nland) + " files, new files only; no commit."),
       'hashes': H, 'times_pst': {'copy_present': '18:21:16 (COPIED.txt 18:21:08)', 'v32_check': '18:36:38', 'declared': '18:37:19',
                                  'declaration_hash_logged': '18:37:24', 'forecasts_made': '18:37:29-18:37:34', 'forecast_hash_logged': '18:37:35',
                                  'frozen_txt': '18:37:50', 'recheck': '18:38:39-18:38:44', 'land': 'after 18:39:58'},
       'numbers': {'runs': DE['a_runs']['n_runs'], 'cases': DE['a_runs']['n_cases'], 'in_domain_cases': dom['in_domain']['cases'],
                   'in_domain_runs': dom['in_domain']['runs'], 'out_of_domain_cases': dom['out_of_domain']['cases'],
                   'out_of_domain_runs': dom['out_of_domain']['runs'], 'in_domain_by_class': dom['in_domain']['by_class'],
                   'out_by_class': dom['out_of_domain']['by_class'], 'models': FN['models'], 'energy_status': FN['energy_status'],
                   'checks': FN['checks'], 'factor_ranges_subset_only': FN['factor_ranges_subset_only'],
                   'bands': {k: {q: v[q] for q in ('T1', 'T2', 'T3', 'E1', 'E2', 'E3', 'E4', 'watts_W')} for k, v in DE['f_pass_rule']['bands'].items()},
                   'recheck': {k: RC[k] for k in ('fields_compared', 'differences_by_model', 'composed_differences', 'pass')},
                   'land_files': nland},
       'v32': V32, 'release_record_at_result': REL, 'claim_files_at_result': CLAIMS, 'e219_claim_before_freeze': False,
       'e219_claim_at_result': e219_claim, 'lab_head_at_result': head,
       'findings': findings, 'incidents': incidents, 'open_issues': open_issues,
       'land_dir': LAND, 'files': [os.path.join(L, n) for n in ('DECLARED-blind-e219.md', 'DECLARED-blind-e219.json', 'forecasts-nominal-e219.csv',
                                                                'forecasts-nominal-e219.json', 'FROZEN.txt', 'result.md', 'result.json')],
       'python': '/usr/bin/python3 3.12.3, numpy 1.26.4 (single-threaded in slot.sh)'}
json.dump(res, open(os.path.join(L, 'result.json'), 'w'), indent=1)
md = []
A = md.append
A('# decl-e219 (Q232) result: FROZEN')
A('')
A(res['summary'])
A('')
A('## Hashes')
A('')
for k, v in H.items():
    A(f'- `{v}`  {k}')
A('')
A("## MM1's domain (the declaration's section 0)")
A('')
A('| arm class | domain | MM1-v0 | MM1-v1 | MM1-v2 | MM1-v3 | MM1-v3.1 | cases |')
A('|---|---|---|---|---|---|---|---|')
for k, v in dom['classes'].items():
    f = v['forms']
    A(f'| {k} | {v["domain"]} | {f.get("MM1-v0", "")} | {f.get("MM1-v1", "")} | {f.get("MM1-v2", "")} | {f.get("MM1-v3", "")} | {f.get("MM1-v3.1", "")} | {v["cases"]} |')
A('')
A('## Numbers')
A('')
A(f"- runs {DE['a_runs']['n_runs']} ({DE['a_runs']['by_role']}), cases {DE['a_runs']['n_cases']}: in domain {dom['in_domain']['cases']} "
  f"({dom['in_domain']['by_class']}), out of domain {dom['out_of_domain']['cases']} ({dom['out_of_domain']['by_class']})")
A(f"- models {FN['models']}; energy {json.dumps(FN['energy_status'])}")
A(f"- checks: F1 re-made 94 E215 rows (factor diff {FN['checks']['F1_e215']['worst_abs_factor_diff']:.1e}); controls re-made E215 columns "
  f"(worst {max(FN['checks']['controls_e215']['worst_abs_diff_cycles'].values()):.1e} cycles); subset factors {json.dumps({k: [round(v[0], 4), round(v[1], 4)] for k, v in FN['factor_ranges_subset_only'].items()})}")
A(f"- bands (E215 form, = decl-e217's): {json.dumps(res['numbers']['bands'])}")
A(f"- recheck after the freeze: {RC['fields_compared']} fields, 0 differences; out-of-domain 175/175 raise in each base model")
A('')
A('## What ran (desk only, aifoundry2, Thu 19 Nov 2026, Pacific; no card, no ssh, no simulator, no commit)')
A('')
A(f"**Label: BLIND.** No E219 claim was on record at the freeze: out/orch/e219-releases.txt held only #14 (the proposal, 18:12:33) and #14.1 "
  f"(the naming, 18:15:03); the one claim file (claim-aifoundry1.txt) held E217's card-0 S3. At this result: {len(REL)} release lines, "
  f"E219 claim {'PRESENT' if e219_claim else 'none'}.")
A('')
A('| step | time (PST) | file | sha256 |')
A('|---|---|---|---|')
A(f"| 0 copy waited, kit copied and checked | 18:21:16-18:21:42 | work/e219-src (49/49) | 247456da... |")
A(f"| 0c MM1-v3.2 check | 18:36:38 | work/v32-status.json | NOT_ON_MAIN |")
A(f"| 1 DECLARED | 18:37:19 (logged 18:37:24) | DECLARED-blind-e219.md / .json | {H['DECLARED-blind-e219.md'][:8]}... / {H['DECLARED-blind-e219.json'][:8]}... |")
A(f"| 2 FORECAST (nominal) | 18:37:29-18:37:34 (logged 18:37:35) | forecasts-nominal-e219.csv / .json | {H['forecasts-nominal-e219.csv'][:8]}... / {H['forecasts-nominal-e219.json'][:8]}... |")
A(f"| 3 FROZEN.txt | 18:37:50 | FROZEN.txt | {H['FROZEN.txt'][:8]}... |")
A('| 4 counts | - | NOT NEEDED (E219 designs no tile) | - |')
A(f"| recheck (after the freeze) | 18:38:39-18:38:44 | work/recheck/recheck.json | {RC['fields_compared']} fields, 0 differences |")
A(f"| 5 land dir | after 18:39:58 | land SHA256SUMS ({nland} files) | {H['land SHA256SUMS'][:8]}... |")
A('')
A('- **Inputs:** a git archive of GitHub main 1c446c93 (= LAB HEAD then; under the lab-git lock): MM1-v3.1 2c971828 64/64, its counts '
  '3e8991d0 71/71, MM1-v3 b1493082 170/170, MM1-v2 3ca4b717 114/114, MM1-v0 14/14 and MM1-v1 77/77 (domain only), the two terms on main '
  '(layout 595fcb59 25/25, gemmLnc aaeaa495 22/22, each posted sha256 equal), E215\'s band code; verify-lay\'s v02_fits.py / v02_fits.json / '
  'v02_e215_controls.csv from its lane (4fb92de3, 1bfec7fc, c5bc2394); the orchestrator\'s E219 kit copy (SRC-SHA256SUMS.txt 247456da, 49/49; '
  'the kit\'s own src/SRC-SHA256SUMS 48/48 from the kit root).')
A('- **The nominal footing:** card 1 600 MHz, 0.517 V, die 60 C; card 0 800 MHz, the model\'s volts (0.604 V), die 55 C (the kit\'s start-gate ceilings), as decl-e217.')
A('')
A('## Findings')
A('')
for f in findings:
    A(f"- **{f['severity']}**: {f['what']} *Fix:* {f['fix']}")
A('')
A('## Incidents')
A('')
for x in incidents:
    A(f'- {x}')
A('')
A('## Open issues and questions for the orchestrator')
A('')
for x in open_issues:
    A(f'- {x}')
A('')
A('## The release record at this result')
A('')
for x in REL:
    A(f'- {x}')
A('')
A(f"Land dir `{LAND}` ({nland} files under tools/matmul/mm1/v3.1/blind-e219/, new files only; SHA256SUMS {H['land SHA256SUMS']}). Written {now}.")
open(os.path.join(L, 'result.md'), 'w').write('\n'.join(md) + '\n')
print(json.dumps({k: res[k] for k in ('verdict', 'summary')}, indent=1))
print(sha(os.path.join(L, 'result.json')), 'result.json')
