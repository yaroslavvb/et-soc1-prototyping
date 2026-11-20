#!/usr/bin/env python3
"""decl-e219 (Q232) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e219/ (new files only): the declaration, FROZEN.txt, the nominal
forecasts, the domain table (DOMAIN-e219.md and domain-e219.csv: every case's domain, class, token and what its class measures), the step
inputs, the recheck, the logs, the scripts (the box's paths replaced by <W>, <LAB>, <SCRATCH>, ~), a README with the order of hashes and
times, and SHA256SUMS. Then a scan for home paths, logins and scratch paths, and a check that the folder is new on GitHub main. Desk.
decl-e217's s05_land.py in form. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>"""
import collections
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = os.path.dirname(os.path.dirname(L))
LAB = '<LAB>'
REL = 'tools/matmul/mm1/v3.1/blind-e219'
D = os.path.join(L, 'land', REL)
if os.path.exists(os.path.join(L, 'land')):
    shutil.rmtree(os.path.join(L, 'land'))
os.makedirs(D)
HOME = os.path.expanduser('~')
REPL = [(W, '<W>'), (LAB, '<LAB>'), ('<SCRATCH>', '<SCRATCH>'), (HOME, '~')]
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def scrub(t):
    for a, b in REPL:
        t = t.replace(a, b)
    return t


def cp(src, rel, text=False):
    dst = os.path.join(D, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if text:
        open(dst, 'w').write(scrub(open(src).read()))
    else:
        shutil.copyfile(src, dst)


TOP = ['DECLARED-blind-e219.md', 'DECLARED-blind-e219.json', 'FROZEN.txt', 'forecasts-nominal-e219.csv', 'forecasts-nominal-e219.json']
for n in TOP:
    cp(os.path.join(L, n), n)
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json'):
    cp(os.path.join(L, 'work', 'step1', n), os.path.join('inputs', 'step1', n))
for n in ('walk-feats-e219.json', 'fc-nominal.json'):
    cp(os.path.join(L, 'work', 'step2', n), os.path.join('inputs', 'step2', n))
cp(os.path.join(L, 'work', 'v32-status.json'), os.path.join('inputs', 'v32-status.json'))
cp(os.path.join(L, 'work', 'recheck', 'recheck.json'), os.path.join('inputs', 'recheck', 'recheck.json'))
for n in ('progress.txt', 'step1-sha256.txt', 'step2-sha256.txt'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n), text=True)
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', n)
    if os.path.isfile(p):
        cp(p, os.path.join('scripts', n), text=True)

DE = json.load(open(os.path.join(L, 'DECLARED-blind-e219.json')))
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e219.json')))['meta']
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
RC = json.load(open(os.path.join(L, 'work', 'recheck', 'recheck.json')))
FZ = open(os.path.join(L, 'FROZEN.txt')).read()
prog = open(os.path.join(L, 'logs', 'progress.txt')).read().splitlines()

# ------------------------------------------------------------------ the domain table (from the declaration's section 0 and the run list)
MEAS = {'CTRL': 'the gemmL 1x1x1 controls: rgm136\'s gemmL loop at one block (L2-held), full chip and 4 or 8 shires; they tie E219 to E217',
        'GAP': 'rgm136\'s gemmL loop at shapes between those run before (the gap cells), full chip',
        'ANCHOR': 'the 4x8x8 int8 random anchor (rgm136 gemmL), full chip, between blocks',
        'CTAB': "run_gemm's c-arm table: gemmc<B>(s) at B = 1, 4s, 8s, 16, 16s, B packed by column, cooperative loads, C per block or shared",
        'C16R': "gemmc16r<R>: gemmc16's 16 blocks, each passed R times before the walk moves on"}
for k, v in DE['domain']['classes'].items():
    if v['domain'] == 'OUT':
        MEAS[k.split(' ')[0]] = v['measures']
with open(os.path.join(D, 'domain-e219.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['case', 'card', 'token', 'fmt', 'kind', 'mask', 'domain', 'class', 'ops_per_minion_pass', 'n_runs', 'forecast', 'what_its_class_measures'])
    for c in RL['cases']:
        w.writerow([c['case'], c['card'], c['token'], c['fmt'], c['kind'], c['mask'], c['domain'], c['class'], c['ops_per_minion_pass'],
                    len(c['runs']), 'FORECAST (every declared model)' if c['domain'] == 'IN' else 'NOT FORECAST (OUT OF DOMAIN)',
                    MEAS.get(c['class'], '')])
dm = []
A = dm.append
A("# E219: MM1's domain, case by case")
A('')
A("From the declaration's section 0 (DECLARED-blind-e219.md): " + DE['domain']['how'] + '. Every case of E219 is in `domain-e219.csv` '
  '(domain, class, token, ops a minion a pass, runs, and what its class measures).')
A('')
A('| arm class | domain | what it measures | MM1-v0 | MM1-v1 | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | cases |')
A('|---|---|---|---|---|---|---|---|---|---|')
for k, v in DE['domain']['classes'].items():
    f = v['forms']
    A(f'| {k} | {v["domain"]} | {v["measures"]} | {f.get("MM1-v0", "")} | {f.get("MM1-v1", "")} | {f.get("MM1-v2", "")} | {f.get("MM1-v3", "")} | '
      f'{f.get("MM1-v3.1", "")} | {f.get("MM1-v3.2", "not on main")} | {v["cases"]} |')
A('')
A(f"- In domain: {DE['domain']['in_domain']}.")
A(f"- Out of domain: {DE['domain']['out_of_domain']['cases']} cases, {DE['domain']['out_of_domain']['runs']} runs, by class "
  f"{DE['domain']['out_of_domain']['by_class']}: {DE['domain']['out_of_domain']['rule']}.")
A(f"- The c-arm training record: {DE['domain']['c_arm_training']['by_experiment_card']}; {DE['domain']['c_arm_training']['reading']}.")
A(f"- Recheck after the freeze: every out-of-domain case raises in every base model: {json.dumps(RC['out_of_domain_raise'])}.")
open(os.path.join(D, 'DOMAIN-e219.md'), 'w').write(scrub('\n'.join(dm)) + '\n')

# ------------------------------------------------------------------ the README
md = []
A = md.append
A("# blind-e219: the lab's BLIND test of its frozen matmul models on E219, declared and frozen before any E219 datum")
A('')
A("E219 is the model session's fifth matmul sweep (1119-mmsweep5; proposal #14 on the coordination Discussion, named E219 in #14.1): "
  "E136's rgm136 unchanged over 206 arms and an anchor in five sessions on aifoundry1 (card 1 S1-S3 at 600 MHz, card 0 S1-S2 at low power), "
  "mostly the host's own block, stream and TenB arms (gemmc and gemmh with R ladders and shared C, the packed walk gemm, mm16 and mm128, tenb) "
  "with gemmL gap cells and 1x1x1 controls. This folder holds the lab's declaration of how it will score its frozen models on E219, MM1's "
  "domain stated first, and the forecasts frozen at nominal conditions, all made at the desk on aifoundry2 before any E219 session ran. "
  "Nothing here is a measurement.")
A('')
A('**Label: BLIND.** ' + DE['label'])
A('')
A("**MM1's domain first** (DOMAIN-e219.md, domain-e219.csv): " + f"{DE['domain']['in_domain']['cases']} of E219's {DE['a_runs']['n_cases']} cases "
  "are in domain and forecast: rgm136's gemmL loop (the 1x1x1 controls, the gap cells, the anchor) and run_gemm's c-arms that the frozen models' "
  "table holds (gemmc1, gemmc4s, gemmc8s, gemmc16, gemmc16s and the gemmc16r<R> ladder); "
  f"{DE['domain']['out_of_domain']['cases']} are OUT OF DOMAIN (gemmc at other B, R or shared C, gemmh, gemm packed by k, mm16, mm128, tenb): "
  "no frozen MM1 has a form for them, so none is forecast; the scores report them apart as the model's domain limit.")
A('')
A('## The order of hashes and times (Pacific, Thu 19 Nov 2026; logs/progress.txt)')
A('')
for ln in prog:
    if any(k in ln for k in ('step 00c', 'step 01 DECLARED', 'step 02 FORECAST', 'FROZEN.txt written', 'recheck (after the freeze')):
        A('- ' + scrub(ln))
A('')
A('## The freeze line (FROZEN.txt)')
A('')
A("FROZEN.txt names the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`; every file keeps its bytes. "
  "The scripts under `scripts/` carry the box's paths replaced (<W>, <LAB>, <SCRATCH>, ~), so their sha256 differ from the as-run hashes in "
  "FROZEN.txt and logs/step1-sha256.txt / step2-sha256.txt; the declaration, the forecasts and the inputs keep their bytes.")
A('')
A('```')
A(scrub(FZ).rstrip())
A('```')
A('')
A('## What is declared (DECLARED-blind-e219.md; the JSON is the machine form)')
A('')
A(f"- **The runs:** {DE['a_runs']['n_runs']} runs ({DE['a_runs']['by_role']}) in {DE['a_runs']['n_cases']} cases, by id from the kit's schedules; "
  "classes CTRL (the gemmL 1x1x1 controls, apart: the tie to E217), GAP, ANCHOR, CTAB, C16R in domain, the OUT classes apart; configuration twins apart.")
A('- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), J over idle given t (E1) and with t forecast (E2), J at rest '
  'given t (E3) and with t forecast (E4), per card, format, kind and class.')
A('- **The models:** ' + '; '.join(f'{k}' for k in DE['models']) + " (see the declaration for each one's call and form).")
A("- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the "
  "data's start-of-run records only (MM1-v3 README section 5's form, as unread-e214 and decl-e217 did); a second footing, the nominal forecasts here, scored beside.")
A("- **The comparisons:** exact sign tests per case: MM1-v3.1 vs MM1-v3 and vs MM1-v2 (H1-H5); the contention term and each of verify-lay's "
  "controls vs MM1-v3.1 on the 6 subset-mask cases (TOO FEW by construction, stated before the data); the switch route NOT APPLICABLE (no "
  "operand-pattern arm).")
A("- **The pass rule:** part A (MM1-v3.1 within E215's bands on 90% of each card's in-domain no-twin cases, every rule), decided by the scoring "
  "lane's script, hashed before its first read; part S NOT APPLICABLE.")
A('- **E219 designs no tile:** every tile file it names is one of the lab\'s kinds byte for byte, so no switch count is made (no step 4).')
A('')
A('## The nominal forecasts (forecasts-nominal-e219.csv / .json)')
A('')
A(f"- Conditions: {json.dumps(FN['nominal_conditions'])}.")
A(f"- {FN['n_in_domain']} in-domain cases x {len(FN['models'])} models: {', '.join(FN['models'])}; {FN['n_out_of_domain']} out-of-domain cases listed "
  "NOT FORECAST (one row each in the CSV).")
A(f"- Energy: {json.dumps(FN['energy_status'])}.")
A(f"- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference {FN['checks']['F1_e215']['worst_abs_factor_diff']:.1e}); "
  f"verify-lay's controls re-made its E215 columns (worst {max(FN['checks']['controls_e215']['worst_abs_diff_cycles'].values()):.1e} cycles, the CSV's rounding).")
A(f"- Factor ranges on the subset masks: {json.dumps({k: [round(v[0], 4), round(v[1], 4)] for k, v in FN['factor_ranges_subset_only'].items()})}.")
A(f"- Recheck after the freeze (inputs/recheck/recheck.json): {RC['fields_compared']} fields, differences {RC['differences_by_model']}, composed "
  f"{RC['composed_differences']}: pass {RC['pass']}.")
A('')
A('## Files')
A('')
A('- `DECLARED-blind-e219.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast procedure, '
  'c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the '
  'out-of-domain cases, the inputs by sha256).')
A('- `FROZEN.txt`: the freeze line as written for the Discussion.')
A('- `forecasts-nominal-e219.*`: the frozen nominal forecasts.')
A('- `DOMAIN-e219.md`, `domain-e219.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).')
A("- `inputs/`: the step files the forecasts were made from (the run list, the models' records, the twin keys, the bands, the walk features, the "
  "MM1-v3.2 check) and the recheck.")
A('- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced).')
A('')
A('Python: /usr/bin/python3 3.12.3 (-I -B), numpy 1.26.4, every numerical job single-threaded inside slot.sh. No card, no simulator, no ssh, no '
  'commit by this lane. SPDX-License-Identifier: Apache-2.0')
open(os.path.join(D, 'README.md'), 'w').write(scrub('\n'.join(md)) + '\n')

# ------------------------------------------------------------------ SHA256SUMS, the scan, new on main
files = sorted(os.path.relpath(os.path.join(dp, f), D) for dp, _, fs in os.walk(D) for f in fs)
with open(os.path.join(D, 'SHA256SUMS'), 'w') as fh:
    for f in files:
        fh.write(f'{sha(os.path.join(D, f))}  {f}\n')
LOGIN = os.path.basename(HOME)            # the scan's words are built at run time, so no login or home path is written in this file
pat = re.compile('|'.join(re.escape(x) for x in (HOME, '/' + 'home' + '/', LOGIN, LOGIN[:8], '/' + 'tmp/claude', '@' + 'gmail', '.' + 'claude')), re.I)
hits = []
for f in files + ['SHA256SUMS']:
    t = open(os.path.join(D, f), 'rb').read().decode('utf-8', 'replace')
    for m in pat.finditer(t):
        hits.append((f, t[max(0, m.start() - 30):m.end() + 30]))
print('land files', len(files) + 1, 'scan hits', len(hits))
for h in hits[:20]:
    print('  HIT', h)
r = subprocess.run(['sha256sum', '-c', 'SHA256SUMS'], cwd=D, capture_output=True, text=True)
print('sha256sum -c rc', r.returncode, 'OK', sum(1 for x in r.stdout.splitlines() if x.endswith(': OK')))
head = subprocess.run(['git', '-C', LAB, 'rev-parse', 'HEAD'], capture_output=True, text=True, env=ENV).stdout.strip()
ex = subprocess.run(['git', '-C', LAB, 'ls-tree', '--name-only', head, REL], capture_output=True, text=True, env=ENV).stdout.strip()
print('LAB HEAD', head[:8], 'path at HEAD:', repr(ex) if ex else 'absent (new files only)')
print(sha(os.path.join(D, 'SHA256SUMS')), 'SHA256SUMS')
sys.exit(1 if hits or ex else 0)
