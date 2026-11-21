#!/usr/bin/env python3
"""decl-e223 (Q239) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e223/ (new files only): the declaration, FROZEN.txt, the nominal
forecasts, the domain table (DOMAIN-e223.md and domain-e223.csv: every case's class, held-out sets, token, mask and what its class measures,
and each model's form), the step inputs, the recheck, the logs, the scripts (the box's paths replaced by <W>, <LAB>, <SCRATCH>, ~), a README
with the order of hashes and times, and SHA256SUMS. Then a scan for home paths, logins and scratch paths, and a check that the folder is new
on GitHub main. Desk. decl-e221's s05_land.py in form. Run: /usr/bin/python3 -I -B s05_land.py <lane dir>"""
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
REL = 'tools/matmul/mm1/v3.1/blind-e223'
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


TOP = ['DECLARED-blind-e223.md', 'DECLARED-blind-e223.json', 'FROZEN.txt', 'forecasts-nominal-e223.csv', 'forecasts-nominal-e223.json']
for n in TOP:
    cp(os.path.join(L, n), n)
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json', 'domain-probe.json'):
    cp(os.path.join(L, 'work', 'step1', n), os.path.join('inputs', 'step1', n))
cp(os.path.join(L, 'work', 'step2', 'fc-nominal.json'), os.path.join('inputs', 'step2', 'fc-nominal.json'))
cp(os.path.join(L, 'work', 'recheck', 'recheck.json'), os.path.join('inputs', 'recheck', 'recheck.json'))
for n in ('q238-frozen-posts-at-setup.txt', 'q238-frozen-posts-at-declaration.txt', 'q238-frozen-posts-at-freeze.txt', 'mask-posimb-FROZEN.txt',
          'lab-commit.txt'):
    cp(os.path.join(L, 'work', n), os.path.join('inputs', n))
cp(os.path.join(L, 'work', 'e223-src', 'SRC-SHA256SUMS.txt'), os.path.join('inputs', 'e223-src-SRC-SHA256SUMS.txt'))
for n in ('progress.txt', 'step1-sha256.txt', 'step2-sha256.txt'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n), text=True)
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', n)
    if os.path.isfile(p):
        cp(p, os.path.join('scripts', n), text=True)

DE = json.load(open(os.path.join(L, 'DECLARED-blind-e223.json')))
DD = DE['declaration']
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e223.json')))['meta']
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
RC = json.load(open(os.path.join(L, 'work', 'recheck', 'recheck.json')))
FZ = open(os.path.join(L, 'FROZEN.txt')).read()
prog = open(os.path.join(L, 'logs', 'progress.txt')).read().splitlines()

# ------------------------------------------------------------------ the domain table
with open(os.path.join(D, 'domain-e223.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['case', 'card', 'token', 'arm_label', 'fmt', 'kind', 'mask', 'n_shires', 'class', 'ho_sets', 'maske221', 'gateset', 'group_mask',
                'ops_per_minion_pass', 'n_runs', 'domain', 'forecast', 'posimb_and_posimb_mask_scope', 'l3s_domain', 'af4_scope',
                'what_its_class_measures'])
    for c in RL['cases']:
        w.writerow([c['case'], c['card'], c['token'], c['arm_label'], c['fmt'], c['kind'], c['mask'], c['n_shires'], c['class'],
                    '+'.join(c['ho_sets']), int(c['maske221']), int(c['gateset']), c['group_mask'], c['ops_per_minion_pass'], len(c['runs']),
                    'IN', 'FORECAST (every declared model)', int(c['group_mask'] == 'SUB'), int(c['group_mask'] == 'FULL'), 0,
                    RL['class_what'][c['class']]])
dm = []
A = dm.append
A("# E223: MM1's domain, case by case")
A('')
A("From the declaration's section 0 (DECLARED-blind-e223.md): " + DD['domain']['verdict'] + '. ' + DD['domain']['evidence'] + '. Every case is '
  "in `domain-e223.csv` (class, held-out sets, token, mask, ops a minion a pass, runs, the terms' scopes, and what its class measures).")
A('')
A('| arm class | what it measures | cases | runs | subset / full | MM1-v2 | MM1-v3 | MM1-v3.1 | MM1-v3.2 | MM1-v3.3 | posimb, posimb-mask scope | L3S domain |')
A('|---|---|---|---|---|---|---|---|---|---|---|---|')
for cl, b in DD['domain']['by_class'].items():
    A(f"| {cl} | {b['what']} | {b['cases']} | {b['runs']} | {b['subset_mask_cases']} / {b['full_chip_cases']} | {b['MM1-v2']} | {b['MM1-v3']} | "
      f"{b['MM1-v3.1']} | {b['MM1-v3.2']} | {b['MM1-v3.3']} | {b['subset_mask_cases']} | {b['full_chip_cases']} |")
A('')
A('**The held-out sets** (the proposal\'s 15 HO-<x> families; an arm may sit in two):')
A('')
A('| set | cases | runs | classes | subset / full |')
A('|---|---|---|---|---|')
for h, v in DD['domain']['held_out_sets'].items():
    A(f"| {h} | {v['cases']} | {v['runs']} | {json.dumps(v['classes'])} | {v['subset_mask_cases']} / {v['full_chip_cases']} |")
A('')
A(f"- MASKE221: {DD['domain']['maske221']}.")
A(f"- GATESET: {DD['domain']['gateset']}.")
A(f"- NOT APPLICABLE in effect: {DD['domain']['not_applicable']}.")
A(f"- Domain limits, REPORTED apart: {DD['domain']['domain_limits_reported']}.")
A('- OUT OF DOMAIN: none.')
open(os.path.join(D, 'DOMAIN-e223.md'), 'w').write(scrub('\n'.join(dm)) + '\n')

# ------------------------------------------------------------------ the README
md = []
A = md.append
A("# blind-e223: the lab's BLIND test of its frozen matmul models on E223, declared and frozen before any E223 datum")
A('')
A("E223 is the model session's seventh matmul sweep (1121-mmsweep7; proposal #16 on the coordination Discussion): E136's rgm136 unchanged "
  "over 299 gemmL arms of the lab's kinds and an anchor in nine sessions (aifoundry1 card 1 S1-S3 at 600 MHz, aifoundry1 card 0 S1-S3 at low "
  "power, aifoundry2 card 0 S1-S3 under its governor), no designed tiles: the core-group placements first (the proposal's held-out placements "
  "in 15 sets), then the held-walk edge, the L3 region, the wide-B wait and the masked energy cases. This folder holds the lab's declaration "
  "of how it will score its frozen models on E223, MM1's domain stated first, and the forecasts frozen at nominal conditions, all made at the "
  "desk on aifoundry2 before any E223 datum. Nothing here is a measurement.")
A('')
A('**Label:** ' + DD['label'] + '.')
A('')
A("**MM1's domain first** (DOMAIN-e223.md, domain-e223.csv): " + DD['domain']['verdict'] + '.')
A('')
A('## The order of hashes and times (Pacific, Sat 21 Nov 2026; logs/progress.txt)')
A('')
for ln in prog:
    if any(k in ln for k in ('step 01 DECLARED', 'step 02 FORECAST', 'FROZEN.txt written', 'recheck (after the freeze', 'probe p02 (a code',
                             'step 00a setup lab', 'step 00b kit copy')):
        A('- ' + scrub(ln))
A('')
A('## The freeze line (FROZEN.txt)')
A('')
A("FROZEN.txt names the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`; every file keeps its bytes. "
  "The scripts under `scripts/` carry the box's paths replaced (<W>, <LAB>, <SCRATCH>, ~), so their sha256 differ from the as-run hashes in "
  "logs/step1-sha256.txt / step2-sha256.txt; the declaration, the forecasts and the inputs keep their bytes. The work copy the forecasts were "
  "made from is a git archive of GitHub main c661275c (inputs/lab-commit.txt) plus Q238's frozen posimb-mask folder at its own land path "
  "tools/matmul/mm1/v3.4-cands/posimb-mask/ (every file equal to its FROZEN.txt lines, inputs/mask-posimb-FROZEN.txt).")
A('')
A('```')
A(scrub(FZ).rstrip())
A('```')
A('')
A('## What is declared (DECLARED-blind-e223.md; the JSON is the machine form)')
A('')
A(f"- **The runs:** {DE['n_runs']} runs in {DE['n_cases']} cases, by id from the kit's schedules; every case in domain; classes "
  f"{', '.join(DE['classes'])} (the placements first); the 15 held-out sets; MASKE221 (blind-e221's MASK class by its own definition); "
  "GATESET (the masked energy cases); FULL and SUB; configuration twins apart.")
A('- **The quantities:** wall cycles (T1), the counter mean (T2), seconds a pass (T3), W and J over idle given t (E1) and J over idle with t '
  'forecast (E2), J at rest given t (E3) and with t forecast (E4), per card, format, kind, class and held-out set.')
A('- **The models:** ' + ', '.join(DE['models']) + ' (all but the first five REPORTED). MM1-v3.3 = \'MM1-v3.2 + AF4\' (E222\'s selection) '
  'equals MM1-v3.2 on every E223 case: AF4 acts only at gemmLnc tokens and E223 runs none.')
A("- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the "
  "data's start-of-run records only (the callers: scripts/s02b_nominal.py's forecast_cases); a second footing, the nominal forecasts here, "
  "scored beside.")
A("- **The comparisons:** exact sign tests per case: MM1-v3.3 vs MM1-v3.2 (NO DATA by construction), MM1-v3.2 vs MM1-v3.1 and vs MM1-v3 "
  "(H1-H5); on the placement class, each REPORTED mask candidate ('MM1-v3.2 + posimb', 'MM1-v3.2 + posimb-mask') vs MM1-v3.2 (H1, H2, H3, "
  "H5), REPORTED; L3S on its full-mask cases REPORTED; the switch route NOT APPLICABLE (no operand-pattern arm).")
A("- **The pass rule:** part A (MM1-v3.2 within E215's bands on 90% of each card's no-twin cases, every rule), decided by the scoring lane's "
  "script, hashed before its first read; the others by the same rules REPORTED; part S NOT APPLICABLE.")
A("- **E223 designs no tile:** every tile file it names is one of the lab's kinds byte for byte, so no switch count is made (no step 4).")
A('')
A('## The nominal forecasts (forecasts-nominal-e223.csv / .json)')
A('')
A(f"- Conditions: {json.dumps(FN['nominal_conditions'])}.")
A(f"- {FN['n_cases']} cases x {len(FN['models'])} models: {', '.join(FN['models'])}.")
A(f"- Energy: every model FORECAST on every case ({json.dumps(FN['energy_status']['MM1-v3.2'])} for MM1-v3.2).")
A(f"- The terms' scopes: {json.dumps(FN['scope'])}.")
A(f"- Checks before any output: E224's frozen forecast rows re-made by E224's own callers ({FN['checks']['A_e224_forecasts_remade']['rows']} "
  f"rows, worst relative difference {FN['checks']['A_e224_forecasts_remade']['worst_rel']}); posimb-mask's frozen E222/E224 rows re-made "
  f"({FN['checks']['B_posimb_mask_remade']['rows']} rows, worst {FN['checks']['B_posimb_mask_remade']['worst_rel']}).")
A(f"- Recheck after the freeze (inputs/recheck/recheck.json): {RC['fields_compared']} fields re-made in a process of their own, "
  f"{RC['differing']} differing.")
A('')
A('## Not in this freeze (REPORTED candidates only)')
A('')
A("- Q238's mask-mesh ('MM1-v3.2 + mesh'): its freeze line posted at 02:03:18 PST names a FROZEN.txt sha256 (3d4942fa...) that is not "
  "the file the lane holds (487188c7..., written 02:03:37 PST), at the declaration's read (02:19:24) and at the freeze (02:22:09).")
A("- Q238's mask-ceiling ('MM1-v3.2 + mask-ceiling', a nonparametric reference, never a model candidate): frozen 02:21:13 and posted "
  "02:21:44 PST, after the declaration was read and hashed (02:19:24 / 02:19:31).")
A("- Either joins the blind test only by a dated amendment hashed and posted before E223's first datum (the declaration's rule), else is "
  "scored as UNREAD.")
A('')
A('## Files')
A('')
A('- `DECLARED-blind-e223.md`, `.json`: the declaration (section 0 the domain, a the runs, b the quantities, the models, the forecast '
  'procedure, c the metric, d the comparisons, e reported beside, f the pass rule, g the label rule, h the nominal footing, i the earlier '
  'reads, the inputs by sha256).')
A('- `FROZEN.txt`: the freeze line as written for the Discussion.')
A('- `forecasts-nominal-e223.*`: the frozen nominal forecasts.')
A('- `DOMAIN-e223.md`, `domain-e223.csv`: the domain table (made from the declaration and the run list after the freeze; not in the freeze line).')
A("- `inputs/`: the step files (the run list, the domain probe, the models' records, the twin keys, the bands, the nominal forecasts' full "
  "record), the recheck, the Q238 posts as read, the posimb-mask FROZEN.txt, the kit copy's SRC-SHA256SUMS.txt and the lab commit.")
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
