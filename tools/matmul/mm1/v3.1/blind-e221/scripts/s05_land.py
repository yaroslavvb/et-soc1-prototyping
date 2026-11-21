#!/usr/bin/env python3
"""decl-e221 (Q235) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e221/ (new files only): the declaration, FROZEN.txt, the nominal
forecasts, the domain table (DOMAIN-e221.md and domain-e221.csv: every case's class, token, mask and what its class measures, and each
model's form), the step inputs, the recheck, the logs, the scripts (the box's paths replaced by <W>, <LAB>, <SCRATCH>, ~), a README with the
order of hashes and times, and SHA256SUMS. Then a scan for home paths, logins and scratch paths, and a check that the folder is new on
GitHub main. Desk. decl-e219's s05_land.py in form. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>"""
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
REL = 'tools/matmul/mm1/v3.1/blind-e221'
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


TOP = ['DECLARED-blind-e221.md', 'DECLARED-blind-e221.json', 'FROZEN.txt', 'forecasts-nominal-e221.csv', 'forecasts-nominal-e221.json']
for n in TOP:
    cp(os.path.join(L, n), n)
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json', 'domain-probe.json'):
    cp(os.path.join(L, 'work', 'step1', n), os.path.join('inputs', 'step1', n))
for n in ('walk-feats-e221.json', 'cand-feats-e221.json', 'fc-nominal.json'):
    cp(os.path.join(L, 'work', 'step2', n), os.path.join('inputs', 'step2', n))
cp(os.path.join(L, 'work', 'recheck', 'recheck.json'), os.path.join('inputs', 'recheck', 'recheck.json'))
for n in ('progress.txt', 'step1-sha256.txt', 'step2-sha256.txt'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n), text=True)
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', n)
    if os.path.isfile(p):
        cp(p, os.path.join('scripts', n), text=True)

DE = json.load(open(os.path.join(L, 'DECLARED-blind-e221.json')))
DD = DE['declaration']
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e221.json')))['meta']
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
RC = json.load(open(os.path.join(L, 'work', 'recheck', 'recheck.json')))
CF = json.load(open(os.path.join(L, 'work', 'step2', 'cand-feats-e221.json')))
FZ = open(os.path.join(L, 'FROZEN.txt')).read()
prog = open(os.path.join(L, 'logs', 'progress.txt')).read().splitlines()
l3dom = set(CF['l3s']['domain_keys'])

# ------------------------------------------------------------------ the domain table
with open(os.path.join(D, 'domain-e221.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['case', 'card', 'token', 'fmt', 'kind', 'mask', 'n_shires', 'class', 'subfamily', 'group_mask', 'ops_per_minion_pass', 'n_runs',
                'domain', 'forecast', 'posimb_scope', 'l3s_domain', 'what_its_class_measures'])
    for c in RL['cases']:
        w.writerow([c['case'], c['card'], c['token'], c['fmt'], c['kind'], c['mask'], c['n_shires'], c['class'], c['subfamily'] or '',
                    c['group_mask'], c['ops_per_minion_pass'], len(c['runs']), 'IN', 'FORECAST (every declared model)',
                    int(c['group_mask'] == 'SUB'), int(c['case'] in l3dom), RL['class_what'][c['class']]])
dm = []
A = dm.append
A("# E221: MM1's domain, case by case")
A('')
A("From the declaration's section 0 (DECLARED-blind-e221.md): " + DD['domain']['verdict'] + '. ' + DD['domain']['evidence'] + '. Every case is '
  'in `domain-e221.csv` (class, token, mask, ops a minion a pass, runs, the candidates\' scope, and what its class measures).')
A('')
A('| arm class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | posimb scope | L3S domain |')
A('|---|---|---|---|---|---|---|---|---|---|---|')
for cl, b in DD['domain']['by_class'].items():
    A(f"| {cl} | {b['what']} | {b['cases']} | {b['runs']} | {b['subset_mask_cases']} / {b['full_chip_cases']} | {b['MM1-v2']} | {b['MM1-v3']} | "
      f"{b['MM1-v3.1']} | {b['MM1-v3.2']} | {b['subset_mask_cases']} | {b['full_chip_cases']} |")
A('')
A('- MM1-v0 and MM1-v1 (not declared here, not probed): each has a gemmL form (MM1-v0 maps subsets at the full chip\'s footprint; MM1-v1 has the masked map).')
A(f"- NOT APPLICABLE: {DD['domain']['not_applicable']}.")
A(f"- Domain limits, REPORTED apart: {DD['domain']['domain_limits_reported']}.")
A('- OUT OF DOMAIN: none.')
open(os.path.join(D, 'DOMAIN-e221.md'), 'w').write(scrub('\n'.join(dm)) + '\n')

# ------------------------------------------------------------------ the README
md = []
A = md.append
A("# blind-e221: the lab's BLIND test of its frozen matmul models on E221, declared and frozen before any E221 datum")
A('')
A("E221 is the model session's sixth matmul sweep (1120-mmsweep6; proposal #15 on the coordination Discussion, named E221 in #15.2): "
  "E136's rgm136 unchanged over 345 gemmL arms and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 card 0 S1-S3 at "
  "low power, aifoundry2 card 0 S1-S3 under its governor): the core-group masks, the 1x1x1 cells at new masks, KB = 1, deep K, the held "
  "walks, the int8 L2 point, the MB = 3 ladders, NB = 1 and the BW shapes. This folder holds the lab's declaration of how it will score its "
  "frozen models on E221, MM1's domain stated first, and the forecasts frozen at nominal conditions, all made at the desk on aifoundry2 before "
  "any E221 run ran. Nothing here is a measurement.")
A('')
A('**Label:** ' + DD['label'] + '.')
A('')
A("**MM1's domain first** (DOMAIN-e221.md, domain-e221.csv): " + DD['domain']['verdict'] + '.')
A('')
A('## The order of hashes and times (Pacific, Fri 20 Nov 2026; logs/progress.txt)')
A('')
for ln in prog:
    if any(k in ln for k in ('step 01 DECLARED', 'step 02 FORECAST', 'FROZEN.txt written', 'recheck (after the freeze', 'probe p02 (a code')):
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
A('## What is declared (DECLARED-blind-e221.md; the JSON is the machine form)')
A('')
A(f"- **The runs:** {DE['n_runs']} runs in {DE['n_cases']} cases, by id from the kit's schedules; every case in domain; classes MASK, CELL1, KB1, "
  "L2I8, MQ3, DK, HLD, BW, NB1, ANCHOR; FULL and SUB; configuration twins apart.")
A('- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), J over idle given t (E1) and with t forecast (E2), J at rest '
  'given t (E3) and with t forecast (E4), per card, format, kind and class.')
A('- **The models:** ' + ', '.join(DE['models']) + ' (the last two REPORTED: the MM1-v3.3 candidates by their own frozen makers); NOT APPLICABLE: '
  + ', '.join(DE['not_applicable']) + '.')
A("- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the "
  "data's start-of-run records only; a second footing, the nominal forecasts here, scored beside.")
A("- **The comparisons:** exact sign tests per case: MM1-v3.2 vs MM1-v3.1, MM1-v3.1 vs MM1-v3 and vs MM1-v2 (H1-H5); the contention term and each "
  "of verify-lay's controls vs MM1-v3.1 on the subset-mask cases (H1, H2); the candidates vs MM1-v3.2 REPORTED; the switch route NOT "
  "APPLICABLE (no operand-pattern arm).")
A("- **The pass rule:** part A (MM1-v3.2 within E215's bands on 90% of each card's no-twin cases, every rule), decided by the scoring lane's "
  "script, hashed before its first read; MM1-v3.1 by the same rules REPORTED; part S NOT APPLICABLE.")
A('- **E221 designs no tile:** every tile file it names is one of the lab\'s kinds byte for byte, so no switch count is made (no step 4).')
A('')
A('## The nominal forecasts (forecasts-nominal-e221.csv / .json)')
A('')
A(f"- Conditions: {json.dumps(FN['nominal_conditions'])}.")
A(f"- {FN['n_cases']} cases x {len(FN['models'])} models: {', '.join(FN['models'])}.")
A(f"- Energy: every model FORECAST on every case ({json.dumps(FN['energy_status']['MM1-v3.2'])} for MM1-v3.2).")
A(f"- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference {FN['checks']['F1_e215']['worst_abs_factor_diff']:.1e}); "
  f"verify-lay's controls re-made its E215 columns (worst {max(FN['checks']['controls_e215']['worst_abs_diff_cycles'].values()):.1e} cycles); "
  f"posimb re-made its {FN['checks']['posimb_e220']['rows']} frozen E220 rows (worst g_wall difference {FN['checks']['posimb_e220']['worst_abs_g_wall_diff']}); "
  f"L3S its {FN['checks']['l3s_e220']['rows']} (worst relative wall-cycle difference {FN['checks']['l3s_e220']['worst_rel_wall_cycles_diff']}).")
A(f"- Recheck after the freeze (inputs/recheck/recheck.json): {RC['fields_compared']} fields, differences {RC['differences_by_model']}, composed "
  f"{RC['composed_differences']}: pass {RC['pass']}.")
A('')
A('## Files')
A('')
A('- `DECLARED-blind-e221.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast procedure, '
  'c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the inputs by sha256).')
A('- `FROZEN.txt`: the freeze line as written for the Discussion.')
A('- `forecasts-nominal-e221.*`: the frozen nominal forecasts.')
A('- `DOMAIN-e221.md`, `domain-e221.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).')
A("- `inputs/`: the step files the forecasts were made from (the run list, the domain probe, the models' records, the twin keys, the bands, "
  "the walk features, the candidates' features) and the recheck.")
A('- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced).')
A('')
A('Python: /usr/bin/python3 3.12.3 (-I -B), numpy, every numerical job single-threaded inside slot.sh. No card, no simulator, no ssh, no '
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
