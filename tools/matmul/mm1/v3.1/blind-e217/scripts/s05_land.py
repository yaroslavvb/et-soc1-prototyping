#!/usr/bin/env python3
"""decl-e217 (Q228) step 5: the land dir land/tools/matmul/mm1/v3.1/blind-e217/ (new files only): the declaration, FROZEN.txt, the nominal
forecasts (and group S's with the counts), COUNTS-FROZEN.txt, counts-e217 (tables, raw bench outputs, scope, re-count rule and check,
SOURCES), the step inputs, the logs, the scripts (the box's paths replaced by <W>, <LAB>, <CORE_ET>, <VERILATOR_BIN>, ~), a README with the
order of hashes and times, and SHA256SUMS. Then a scan for home paths, logins and scratch paths. Desk.
Run: /usr/bin/python3 -I -B s05_land.py <lane dir>"""
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
CORE = '<CORE_ET>'
REL = 'tools/matmul/mm1/v3.1/blind-e217'
D = os.path.join(L, 'land', REL)
if os.path.exists(os.path.join(L, 'land')):
    shutil.rmtree(os.path.join(L, 'land'))
os.makedirs(D)
HOME = os.path.expanduser('~')
REPL = [(os.path.join(W, 'out', 'decl-e217', 'cnt'), '<W>/out/decl-e217/cnt'), (W, '<W>'), (LAB, '<LAB>'), (CORE, '<CORE_ET>'),
        (os.path.join(HOME, '.local', 'verilator', 'bin'), '<VERILATOR_BIN>'), ('<SCRATCH>', '<SCRATCH>'), (HOME, '~')]


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


TOP = ['DECLARED-blind-e217.md', 'DECLARED-blind-e217.json', 'FROZEN.txt', 'forecasts-nominal-e217.csv', 'forecasts-nominal-e217.json',
       'forecasts-nominal-e217-counts.csv', 'forecasts-nominal-e217-counts.json', 'COUNTS-FROZEN.txt']
for n in TOP:
    if os.path.exists(os.path.join(L, n)):
        cp(os.path.join(L, n), n)
for n in ('runs-listed.json', 'models-step1.json', 'twin-keys.json', 'bands.json'):
    cp(os.path.join(L, 'work', 'step1', n), os.path.join('inputs', 'step1', n))
for n in ('walk-feats-e217.json', 'fc-nominal.json'):
    cp(os.path.join(L, 'work', 'step2', n), os.path.join('inputs', 'step2', n))
for n in ('fc-counts-v31.json', 'fc-counts-v3.json'):
    p = os.path.join(L, 'work', 'step4', n)
    if os.path.exists(p):
        cp(p, os.path.join('inputs', 'step4', n))
if os.path.exists(os.path.join(L, 'work', 'recheck', 'recheck.json')):
    cp(os.path.join(L, 'work', 'recheck', 'recheck.json'), os.path.join('inputs', 'recheck', 'recheck.json'))
CN = os.path.join(L, 'cnt', 'counts')
if os.path.isdir(CN):
    for n in sorted(os.listdir(CN)):
        if os.path.isfile(os.path.join(CN, n)):
            cp(os.path.join(CN, n), os.path.join('counts-e217', n), text=n.endswith(('.txt', '.json', '.csv')))
RAW = os.path.join(L, 'cnt', 'work', 'counts')
if os.path.isdir(RAW):
    for n in sorted(os.listdir(RAW)):
        if n.endswith('.json'):
            cp(os.path.join(RAW, n), os.path.join('counts-e217', 'raw', n), text=True)
for n in ('progress.txt', 'step1-sha256.txt', 'step2-sha256.txt'):
    cp(os.path.join(L, 'logs', n), os.path.join('logs', n), text=True)
for n in sorted(os.listdir(os.path.join(L, 'scripts'))):
    p = os.path.join(L, 'scripts', n)
    if os.path.isfile(p) and not n.endswith('.from-counts-e214'):
        cp(p, os.path.join('scripts', n), text=True)
UNRUN = {'s07_chain.sh', 's12_readme.py', 's13_land.sh', 's14_land_check.py', 's15_result.py', 'wait_file.sh'}   # counts-e214's, copied, never run here
for n in sorted(os.listdir(os.path.join(L, 'scripts', 'cnt'))):
    p = os.path.join(L, 'scripts', 'cnt', n)
    if os.path.isfile(p) and not n.endswith('.from-counts-e214') and n not in UNRUN:
        cp(p, os.path.join('scripts', 'cnt', n), text=True)

# ------------------------------------------------------------------ the README
prog = open(os.path.join(L, 'logs', 'progress.txt')).read().splitlines()
FZ = open(os.path.join(L, 'FROZEN.txt')).read()
CF = open(os.path.join(L, 'COUNTS-FROZEN.txt')).read() if os.path.exists(os.path.join(L, 'COUNTS-FROZEN.txt')) else None
DE = json.load(open(os.path.join(L, 'DECLARED-blind-e217.json')))
FN = json.load(open(os.path.join(L, 'forecasts-nominal-e217.json')))['meta']
FC = json.load(open(os.path.join(L, 'forecasts-nominal-e217-counts.json'))) if os.path.exists(os.path.join(L, 'forecasts-nominal-e217-counts.json')) else None
c32 = json.load(open(os.path.join(CN, 'counts-fp32-gemm-states.json'))) if os.path.exists(os.path.join(CN, 'counts-fp32-gemm-states.json')) else None
cL = json.load(open(os.path.join(CN, 'counts-fp16-int8-launch.json'))) if os.path.exists(os.path.join(CN, 'counts-fp16-int8-launch.json')) else None
rcheck = json.load(open(os.path.join(CN, 'recount-check.json'))) if os.path.exists(os.path.join(CN, 'recount-check.json')) else None
md = []
A = md.append
A("# blind-e217: the lab's BLIND test of its frozen matmul models on E217, declared and frozen before any E217 datum")
A('')
A("E217 is the model session's fourth matmul sweep (1119-mmsweep4; proposal #13 on the coordination Discussion, named E217 in #13.1): "
  "E136's rgm136 unchanged, 331 arms and an anchor in seven sessions on aifoundry1 (card 1 S1-S4 at 600 MHz, card 0 S1-S3 at low power), "
  "including 1x1x1 cells at 12 new core-group masks a card and 24 operand-pattern tiles of 2,048 bytes. This folder holds the lab's "
  "declaration of how it will score its own frozen models on E217, the forecasts frozen at nominal conditions, and the switch counts of "
  "E217's 21 new tile kinds, all made at the desk on aifoundry2 before any E217 session ran. Nothing here is a measurement.")
A('')
A('**Label: BLIND.** ' + DE['label'])
A('')
A('## The order of hashes and times (Pacific, Thu 19 Nov 2026; logs/progress.txt)')
A('')
for ln in prog:
    if any(k in ln for k in ('DECLARED', 'FORECAST (rc', 'FROZEN.txt written', 'COUNTS-FROZEN', 'counts-e217 s06b', 'counts-e217 s07 ', 'counts-e217 s08 ',
                             'step 04c', 'step 04 COUNTS')):
        A('- ' + scrub(ln))
A('')
A('## The freeze line (FROZEN.txt)')
A('')
A("FROZEN.txt and COUNTS-FROZEN.txt name the lane's own paths: here `work/step1/` is `inputs/step1/`, `work/step2/` is `inputs/step2/`, "
  "`work/step4/` is `inputs/step4/`, `cnt/counts/` is `counts-e217/` and `cnt/work/counts/` is `counts-e217/raw/`; every file keeps its bytes.")
A('')
A('```')
A(scrub(FZ).rstrip())
A('```')
if CF:
    A('')
    A('## The counts freeze line (COUNTS-FROZEN.txt)')
    A('')
    A('```')
    A(scrub(CF).rstrip())
    A('```')
A('')
A('## What is declared (DECLARED-blind-e217.md; the JSON is the machine form)')
A('')
A(f"- **The runs:** {DE['a_runs']['n_runs']} runs ({DE['a_runs']['by_role']}) in {DE['a_runs']['n_cases']} cases, by id from the kit's schedules; "
  "the 1x1x1 cells (X1), the new core-group masks (MG), the other subset masks and the full chip apart; group S (the 21 new tile kinds), "
  "group C (the sparse50 pools) and the lab's kinds apart; configuration twins apart.")
A('- **The quantities:** wall cycles (T1), the counter mean (T2), seconds (T3), J over idle given t (E1) and with t forecast (E2), J at rest given t (E3) '
  'and with t forecast (E4), per card, format and kind.')
A('- **The models:** ' + '; '.join(f'{k}' for k in DE['models']) + " (see the declaration for each one's call and form).")
A("- **The forecast procedure:** each frozen predictor unchanged at each run's measured clock, minion volts and die at start, read from the "
  "data's start-of-run records only (MM1-v3 README section 5's form, as unread-e214 did); a second footing, the nominal forecasts here, scored beside.")
A('- **The comparisons:** exact sign tests per case (MM1-v3.1 vs MM1-v3, vs MM1-v2; the contention term and each of verify-lay\'s controls '
  'vs MM1-v3.1 on the subset-mask cases; the switch route with the counts vs the null on group S).')
A("- **The pass rule:** part A (MM1-v3.1 within E215's bands on 90% of each card's no-twin cases, every rule) and part S (the switch test P1-P4), "
  "decided by the scoring lane's script, hashed before its first read.")
A('')
A('## The nominal forecasts (forecasts-nominal-e217.csv / .json)')
A('')
A(f"- Conditions: {json.dumps(FN['nominal_conditions'])}.")
A(f"- {FN['n_cases']} cases x {len(FN['models'])} models: {', '.join(FN['models'])}.")
A(f"- Energy: {json.dumps(FN['energy_status'])} (group S's 35 cases have no energy at the first freeze: no count yet).")
A(f"- Checks before any output: the contention term re-made its 94 frozen E215 rows (factor difference {FN['checks']['F1_e215']['worst_abs_factor_diff']:.1e}); "
  f"verify-lay's controls re-made its E215 columns (worst {max(FN['checks']['controls_e215']['worst_abs_diff_cycles'].values()):.1e} cycles, the CSV's rounding).")
A(f"- Factor ranges on the subset masks: {json.dumps({k: [round(v[0], 4), round(v[1], 4)] for k, v in FN['factor_ranges_subset_only'].items()})}.")
if FC:
    A(f"- Group S with counts-e217 (forecasts-nominal-e217-counts.*): {FC['n_cases']} cases, energy {json.dumps(FC['energy_status'])}; "
      "the declared gate for the four zero-row tiles beside the frozen code's literal (REPORTED); the count's valid share beside each declared share: "
      + json.dumps(FC['gate_vs_count_valid_share_REPORTED']) + '.')
A('')
if c32 and cL:
    A('## The counts (counts-e217/)')
    A('')
    A('Made exactly as counts-e214 made E214\'s (its scripts, under scripts/cnt/ here): the RTL bench rtl-sim/fma_toggle_v2 built with Verilator 5.042 '
      '(Verilator -j 2, make -j 1), single-threaded, one bench process, inside slot.sh and nodev.sh; the functional check first; the net maps '
      'trained on this binary; two committed MM1-v3.1 rows re-counted first and matched; then fp32 at the GEMM accumulator states S1 and S2 '
      '(count_e210.py) and fp16 and int8 at the harness launch points (run_kinds.py).')
    if rcheck is not None:
        vt = [x for x in open(os.path.join(CN, 'recount-check.txt')).read().splitlines() if x.startswith('VERDICT')]
        A(f"- Re-count check: pass {rcheck.get('pass')} ({vt[0] if vt else 'no verdict line'}).")
    A('')
    A('| fmt | kind | state | fin edges lo / hi a MAC | valid share | points |')
    A('|---|---|---|---:|---:|---:|')
    for s in ('S1', 'S2'):
        for k, r in sorted(c32['shapes'][s].items()):
            A(f"| fp32 | {k} | {s} | {r['fin_edges_lo']:,.0f} / {r['fin_edges_hi']:,.0f} | {r.get('valid_slots', float('nan')):.3f} | {r.get('n_points', '')} |")
    for k, r in sorted(cL['rows'].items()):
        fe = r.get('fin_edges_per_mac', {})
        A(f"| {k.split('.')[0]} | {k.split('.', 1)[1]} | launch | {fe.get('lo', 0):,} / {fe.get('hi', 0):,} | {r.get('valid_share_v', float('nan')):.3f} | {r.get('n_points', '')} |")
    A('')
A('## Files')
A('')
A('- `DECLARED-blind-e217.md`, `.json`: the declaration (section a the runs, b the quantities, the models, the forecast procedure, c the metric, '
  'd the comparisons, e the switch arms, f the pass rule, g the label rule, h the nominal footing, i the earlier reads, the inputs by sha256).')
A('- `FROZEN.txt`, `COUNTS-FROZEN.txt`: the two freeze lines as written for the Discussion.')
A('- `forecasts-nominal-e217.*`, `forecasts-nominal-e217-counts.*`: the frozen nominal forecasts.')
A('- `counts-e217/`: the counts in the committed tables\' form (`counts-fp32-gemm-states.json`, `counts-fp16-int8-launch.json`, CSVs), the raw bench '
  'outputs (`raw/`), the scope, the re-count rule and check, the merge check, the tile zero shares, SOURCES.json.')
A('- `inputs/`: the step files the forecasts were made from (the run list, the models\' records, the twin keys, the bands, the walk features, '
  'the two models\' group-S runs with the counts).')
A('- `inputs/recheck/recheck.json`: after the freeze, each base model re-made its nominal forecasts in a process of its own and the composed '
  'forms were re-derived: 12,753 fields, 0 differences.')
A('- `logs/`: the progress log and the step hash lists. `scripts/`: every script as run (box paths replaced), `scripts/cnt/` the counting scripts.')
A('')
A('Python: /usr/bin/python3 3.12.3 (-I -B), numpy 1.26.4, every numerical job single-threaded inside slot.sh. No card, no simulator, no commit '
  'by this lane. SPDX-License-Identifier: Apache-2.0')
open(os.path.join(D, 'README.md'), 'w').write(scrub('\n'.join(md)) + '\n')

# ------------------------------------------------------------------ SHA256SUMS and the scan
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
print(sha(os.path.join(D, 'SHA256SUMS')), 'SHA256SUMS')
sys.exit(1 if hits else 0)
