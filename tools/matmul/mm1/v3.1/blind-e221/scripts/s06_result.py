#!/usr/bin/env python3
"""decl-e221 (Q235) step 6: result.md and result.json at the lane root, from this lane's files (hashes read, not typed) and the orchestrator's
records (e221-releases.txt, the claim files, q234-frozen-posts.txt). Desk. decl-e219's s06_result.py in role.
Run: /usr/bin/python3 -I -B s06_result.py <lane dir>"""
import hashlib
import json
import os
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
LAB = '<LAB>'
TZ = dict(os.environ, TZ='America/Los_Angeles')
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
LAND = os.path.join(L, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'blind-e221')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


made = subprocess.run(['date', '+%a %d %b %Y %H:%M:%S %Z'], capture_output=True, text=True, env=TZ).stdout.strip()
H = {n: sha(os.path.join(L, n)) for n in ('DECLARED-blind-e221.md', 'DECLARED-blind-e221.json', 'forecasts-nominal-e221.csv',
                                          'forecasts-nominal-e221.json', 'FROZEN.txt')}
H['logs/step1-sha256.txt'] = sha(os.path.join(L, 'logs', 'step1-sha256.txt'))
H['logs/step2-sha256.txt'] = sha(os.path.join(L, 'logs', 'step2-sha256.txt'))
H['work/step2/fc-nominal.json'] = sha(os.path.join(L, 'work', 'step2', 'fc-nominal.json'))
H['work/recheck/recheck.json'] = sha(os.path.join(L, 'work', 'recheck', 'recheck.json'))
H['land SHA256SUMS'] = sha(os.path.join(LAND, 'SHA256SUMS'))
nland = sum(1 for _ in open(os.path.join(LAND, 'SHA256SUMS'))) + 1
DE = json.load(open(os.path.join(L, 'DECLARED-blind-e221.json')))
DD = DE['declaration']
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e221.json')))['meta']
RC = json.load(open(os.path.join(L, 'work', 'recheck', 'recheck.json')))
BD = json.load(open(os.path.join(L, 'work', 'step1', 'bands.json')))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
REL = [x for x in open(os.path.join(W, 'out', 'orch', 'e221-releases.txt')).read().splitlines() if x.startswith('#15')]
CLAIMS = sorted(f for f in os.listdir(os.path.join(W, 'out', 'orch')) if f.startswith('claim-'))
Q234 = [x for x in open(os.path.join(W, 'out', 'orch', 'q234-frozen-posts.txt')).read().splitlines() if x.startswith('#')
        and not x.startswith('# ')]
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=ENV).stdout.strip()
e221_claims = [x for x in REL if 'CLAIM' in x]
new_claim_after_15_1 = [x for x in e221_claims if not x.startswith('#15.1 ')]
cards = ['aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0']
bands = {c: dict({q: v['band'] for q, v in BD['cards'][c]['bands'].items()}, watts_W=BD['cards'][c]['band_w']['band_W']) for c in cards}
cl_cases = {cl: b['cases'] for cl, b in DD['domain']['by_class'].items()}
numbers = {'runs': DE['n_runs'], 'runs_by_role': RL['counts']['by_role'], 'cases': DE['n_cases'], 'in_domain_cases': DE['n_in_domain'],
           'out_of_domain_cases': 0, 'cases_by_class': cl_cases, 'cases_by_card': RL['counts']['cases_by_card'],
           'subset_mask_cases': RL['counts']['cases_by_group_mask']['SUB'], 'distinct_masks': RL['counts']['distinct_masks'],
           'models': FN['models'], 'models_reported': FN['models_reported'], 'not_applicable': ['v3.1+gemmLnc', 'MM1-v3.2+AF4'],
           'energy_forecast_each_model': FN['energy_status']['MM1-v3.2'], 'csv_rows': 8796, 'checks': FN['checks'],
           'factor_ranges_subset_only': FN['factor_ranges_subset_only'], 'l3s_ratio_range_full_mask': FN['l3s_ratio_range_full_mask'],
           'recheck': RC, 'bands_E215_form': bands, 'nominal': FN['nominal_conditions'],
           'twins_at_nominal_clock': DD['metric']['twins'].split('At the nominal clocks')[1] if 'At the nominal clocks' in DD['metric']['twins'] else ''}
summary = (f"FROZEN: E221's BLIND test declared (DECLARED-blind-e221.md {H['DECLARED-blind-e221.md'][:8]}, .json "
           f"{H['DECLARED-blind-e221.json'][:8]}, 06:15:39 PST) and its nominal forecasts frozen (csv {H['forecasts-nominal-e221.csv'][:8]}, json "
           f"{H['forecasts-nominal-e221.json'][:8]}, 06:17:05) for all 733 cases (811 runs) by MM1-v3.2 (the pass rule's model), MM1-v3.1, MM1-v3, "
           f"MM1-v2, '+contention', '+both' and verify-lay's four controls, with the MM1-v3.3 candidates posimb and L3S REPORTED by their own frozen "
           f"makers; every case IN MM1's domain (all rgm136 gemmL), none OUT; AF4 and 'v3.1+gemmLnc' NOT APPLICABLE (no gemmLnc arm); FROZEN.txt "
           f"{H['FROZEN.txt'][:8]} at 06:17:38 PST, before any E221 run ran (S1's start was stopped with no run); no tiles, so no counts; recheck "
           f"{RC['fields_compared']} fields 0 differences; land {nland} files, new files only; no commit.")
findings = [
    {'severity': 'info', 'what': "MM1's domain covers every E221 case: all 345 arms and the anchor are rgm136's cooperative gemmL loop, and probe "
     "p01 found a form (finite time, energy FORECAST) for all 733 cases in MM1-v3.2, MM1-v3.1, MM1-v3 and MM1-v2; so no case is OUT OF DOMAIN "
     "and none is left unforecast. Classes: " + json.dumps(cl_cases) + ". The domain limits (masks no fit holds, the governed cards) are "
     "REPORTED apart, not excluded.", 'fix': 'None.'},
    {'severity': 'info', 'what': "'v3.1 + gemmLnc term' (F3) and 'MM1-v3.2 + gemmLnc term AF4' are 0 off gemmLnc and E221 runs no gemmLnc arm: "
     "declared NOT APPLICABLE (each equals its base on every case). posimb is in scope on the 461 subset-mask cases (1 elsewhere); L3S in its "
     "domain on the 272 full-mask cases (MM1-v3.2 elsewhere).", 'fix': 'None.'},
    {'severity': 'low', 'what': "aifoundry2 card 0's ties and watts band rest on a weak floor: E212 a2c0-S1/S2 hold only 3 cases with two runs "
     "(ties watts 0.4 W, joules 0.02; watts band 0.72 W). The bands for every card come from MM1-v3.1's held-out errors (E215's form) and are "
     "applied to MM1-v3.2 as declared (MM1-v3.2 scored against the bands its predecessor earned).", 'fix': 'None before the data: declared; '
     'the scorer prints the floors beside.'},
    {'severity': 'low', 'what': "Probes ran before the declaration and are disclosed in its section i: p01 (domain status only) and p02 (a code "
     "test of the nominal-forecast script, run twice: the first failed with a KeyError, the second passed; it printed only checks, counts and "
     "the min/max time factors over the subset cases; its output was deleted unread). Nothing in the declaration was chosen from them.",
     'fix': 'None needed.'},
    {'severity': 'info', 'what': "posimb's frozen feature cache (layout2's work/private_shared.json, 05:33) lacks 10 of the E220 configurations its "
     "maker made on the fly at its freeze, so the cache alone does not re-make posimb's E220 forecast; this lane's check made those 10 by the "
     "maker's own branch (h01_freeze.main) and re-made all 306 E220 rows exactly, then dropped them; E221's forecasts use the frozen cache "
     "(11 configurations) plus step 2f's 121 made by the maker's f02_private.", 'fix': "None; for layout2's land: a note that the E220 "
     "features made at the freeze were not saved."},
    {'severity': 'info', 'what': "The orchestrator's COPIED.txt (out/orch/e221-src) reads 'Copied Thu 19 Nov 2026 05:54:33 PST' for a copy made "
     "Fri 20 Nov (file time Nov 20 05:54; the line itself names #15 of Fri 20 Nov); the copy checks 53/53 and the kit's own sums 52/52.",
     'fix': 'A one-word correction in COPIED.txt (Thu 19 -> Fri 20), the orchestrator\'s file.'},
    {'severity': 'info', 'what': "The pre-freeze state: e221-releases.txt held #15, #15.1 (the S1 claim), #15.2 and #15.2.1 (S1 started 05:53:56, "
     "stopped 05:55:27 as its first run began: no run ran; 1.47 card-minutes of rest and smoke in EE/sessions/1795182836-a1c1-S1/, never opened "
     "here, declared not scored); no claim file stood at the freeze. Every E221 session whose first card command follows the freeze POST is "
     "BLIND, S1's re-claim included.", 'fix': 'None.'},
    {'severity': 'info', 'what': "E221 designs no tile: arms.json's tiles table is empty and its tile files are the lab's kinds byte for byte, so "
     "step 4 (counts) is NOT NEEDED and D4 (the switch route) NOT APPLICABLE.", 'fix': 'None.'},
]
incidents = [
    "Probe p01's first try (06:02:12) failed at import (rc 1): MM1-v3.2's energy_v32.py reads tools/claims-v3/e214/proposal/src; step 00d "
    "archived tools/claims-v3/e214 and e213/points-e213.csv from the same commit and p01 passed (06:02:47).",
    "Step 02w's first try (06:05:06) failed (rc 1): work/step2 had not been made; made, and the second try passed (06:05:23-06:06:49).",
    "Probe p02's first try (06:11:55) failed (rc 1, KeyError on an E220 check configuration absent from posimb's frozen cache); the script "
    "gained the maker's own branch for the check; p02's second try passed and its output was deleted unread by a literal-path rm.",
    "At the start four of decl-e219's scripts were copied by mistake into this lane's work/ folder and removed at once by literal-path rm.",
    "A few short read-only 'python3 -c' one-liners and 'python3 - <<EOF' heredocs ran in Bash calls to inspect JSON and to write this lane's "
    "scripts from decl-e219's (no hook refused one).",
]
open_issues = [
    f"For the orchestrator: post FROZEN.txt's four sha256 on #15 as the lab's freeze line before S1 is claimed again: DECLARED-blind-e221.md "
    f"{H['DECLARED-blind-e221.md'][:8]}..., DECLARED-blind-e221.json {H['DECLARED-blind-e221.json'][:8]}..., forecasts-nominal-e221.csv "
    f"{H['forecasts-nominal-e221.csv'][:8]}..., forecasts-nominal-e221.json {H['forecasts-nominal-e221.json'][:8]}... (FROZEN.txt "
    f"{H['FROZEN.txt'][:8]}...). Each session's label follows that post's time against its first card command.",
    "For blind-e221 (the scoring lane): implement the declaration exactly: read only the start-of-run fields first, hash the measured-conditions "
    "forecasts (MM1-v3.2, MM1-v3.1, MM1-v3, MM1-v2, the composed forms and the two candidates by s02b_nominal.py's makers at each run's "
    "conditions), then hash the scorer before the first read; part A on MM1-v3.2 with bands.json's bands; MM1-v3.1 beside, REPORTED; the "
    "stopped S1 start not scored.",
    "The model session's sealed E221 forecast (cab693ef...) was not read or scored here.",
]
res = {'lane': 'decl-e221', 'round': 'Q235', 'verdict': 'FROZEN', 'written_pst': made, 'summary': summary, 'hashes': H,
       'times_pst': {'start': '05:56:18', 'copy_checked': '05:59:49', 'declared': '06:15:39', 'declaration_hash_logged': '06:15:58',
                     'forecasts_made': '06:16:27-06:17:04', 'forecast_files_written': '06:17:05', 'forecast_hash_logged': '06:17:11',
                     'frozen_txt': '06:17:38', 'recheck': '06:18:13-06:19:39', 'land': 'from 06:20:51'},
       'numbers': numbers, 'release_record_at_result': REL, 'claim_files_at_result': CLAIMS,
       'e221_claims_on_record': e221_claims, 'new_e221_claim_after_15_1_at_result': bool(new_claim_after_15_1),
       'q234_frozen_posts_at_result': Q234, 'lab_head_at_result': head, 'findings': findings, 'incidents': incidents,
       'open_issues': open_issues, 'land_dir': os.path.join(L, 'land'),
       'files': [os.path.join(L, n) for n in ('DECLARED-blind-e221.md', 'DECLARED-blind-e221.json', 'forecasts-nominal-e221.csv',
                                              'forecasts-nominal-e221.json', 'FROZEN.txt', 'result.md', 'result.json')] + [LAND],
       'python': '/usr/bin/python3 3.12.3, numpy (single-threaded in slot.sh)'}
json.dump(res, open(os.path.join(L, 'result.json'), 'w'), indent=1)
md = [f"# decl-e221 (Q235) result: FROZEN", '', summary, '', '## Hashes', '']
md += [f'- `{v}`  {k}' for k, v in H.items()]
md += ['', "## MM1's domain (the declaration's section 0)", '',
       '| class | what it measures | cases | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | posimb scope | L3S domain |',
       '|---|---|---|---|---|---|---|---|---|---|']
for cl, b in DD['domain']['by_class'].items():
    md.append(f"| {cl} | {b['what']} | {b['cases']} | {b['subset_mask_cases']} / {b['full_chip_cases']} | yes | yes | yes | yes | "
              f"{b['subset_mask_cases']} | {b['full_chip_cases']} |")
md += ['', '- OUT OF DOMAIN: none. NOT APPLICABLE: v3.1+gemmLnc, MM1-v3.2+AF4 (no gemmLnc arm).', '',
       '## Numbers', '',
       f"- runs {DE['n_runs']} ({RL['counts']['by_role']}), cases {DE['n_cases']} by card {RL['counts']['cases_by_card']}; subset-mask cases "
       f"{numbers['subset_mask_cases']} over {numbers['distinct_masks']} masks",
       f"- models {FN['models']} (REPORTED {FN['models_reported']}); energy FORECAST 733/733 each",
       f"- checks: {json.dumps(FN['checks'])}",
       f"- time factors on the subset masks (min, max): {json.dumps({k: [round(v[0], 4), round(v[1], 4)] for k, v in FN['factor_ranges_subset_only'].items()})}",
       f"- bands (E215 form): {json.dumps(bands)}",
       f"- recheck after the freeze: {RC['fields_compared']} fields, differences {RC['differences_by_model']}, composed {RC['composed_differences']}",
       '', '## What ran (desk only, aifoundry2, Fri 20 Nov 2026, Pacific; no card, no ssh, no simulator, no commit)', '',
       '**Label: BLIND** for every session whose first card command follows the freeze post. No E221 run had run at the freeze: S1\'s start '
       '(05:53:56) was stopped at 05:55:27 with no run (#15.2.1); no claim file stood.', '',
       '| step | time (PST) | file | sha256 |', '|---|---|---|---|',
       '| 0 work copies (GitHub main 0f046200), kit copy checked | 05:59:40-06:02:47 | work/lab, work/e221-src (53/53) | 5680112f... |',
       '| 1 DECLARED | 06:15:39 (logged 06:15:58) | DECLARED-blind-e221.md / .json | %s... / %s... |' % (H['DECLARED-blind-e221.md'][:8], H['DECLARED-blind-e221.json'][:8]),
       '| 2 FORECAST (nominal) | 06:16:27-06:17:05 (logged 06:17:11) | forecasts-nominal-e221.csv / .json | %s... / %s... |' % (H['forecasts-nominal-e221.csv'][:8], H['forecasts-nominal-e221.json'][:8]),
       '| 3 FROZEN.txt | 06:17:38 | FROZEN.txt | %s... |' % H['FROZEN.txt'][:8],
       '| 4 counts | - | NOT NEEDED (E221 designs no tile) | - |',
       '| recheck (after the freeze) | 06:18:13-06:19:39 | work/recheck/recheck.json | %d fields, 0 differences |' % RC['fields_compared'],
       '| 5 land dir | from 06:20:51 | land SHA256SUMS (%d files) | %s... |' % (nland, H['land SHA256SUMS'][:8]),
       '', '## Findings', '']
md += [f"- **{f['severity']}**: {f['what']} *Fix:* {f['fix']}" for f in findings]
md += ['', '## Incidents', ''] + ['- ' + x for x in incidents]
md += ['', '## Open issues and questions for the orchestrator', ''] + ['- ' + x for x in open_issues]
md += ['', '## The release record at this result', ''] + ['- ' + x for x in REL]
md += ['', f"Claim files at this result: {CLAIMS or 'none'}; LAB HEAD {head[:8]}. Land dir `{os.path.join(L, 'land')}` ({nland} files under "
       f"tools/matmul/mm1/v3.1/blind-e221/, new files only; SHA256SUMS {H['land SHA256SUMS']}). Written {made}."]
open(os.path.join(L, 'result.md'), 'w').write('\n'.join(md) + '\n')
print(summary)
print('land SHA256SUMS', H['land SHA256SUMS'], 'files', nland)
