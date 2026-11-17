#!/usr/bin/python3
# tools/matmul/mm1/v0/forecasts-e206-armB.py: MM1-v0's forecasts for E206's ARM B points (aifoundry1 card 1, 600 MHz), made by the
# frozen predictor beside this file (mm1_v0.py, committed in 2d1413f5) UNCHANGED. This wrapper adds no model: it
#   1. checks mm1_v0.py's sha256 against the committed one (printed first) and refuses any other file;
#   2. imports mm1_v0.py as it stands: its own module code runs (the energy refit, its arm A forecasts, the blind-day plan) and writes
#      its outputs into --scratch, which must reproduce the four committed outputs byte for byte (SHA256SUMS), or the run is refused;
#   3. rebuilds arm A's 119 rows from predict() in the arm A file's form and checks them byte for byte against mm1_v0_e206.csv (so
#      the row form below is the frozen code's own);
#   4. takes card 1's arguments from the frozen code and its vendored inputs (README note, "Card 1's arguments"): the card name
#      'aifoundry1 card 1' (in the predictor's CARDS list), the ledger key whose resident anchors the energy table gives card 1's rows
#      ('c1'), the voltage every card-1 row of the energy table carries (0.517 V, s_V = 1), 600 MHz, and G = 0 (a pinned card);
#   5. calls predict() for every point with on_arm_B True in tools/claims-v3/e206/points-e206.csv and writes the rows in the arm A
#      file's form (the same columns, the same rounding, the same notes).
# No refit, no new constant, no change to the predictor. Desk only: it reads no card and no E206 datum.
#   /usr/bin/python3 -I -B tools/matmul/mm1/v0/forecasts-e206-armB.py --scratch <new folder> --out <folder>
# Writes in --out: forecasts-e206-armB.csv and forecasts-e206-armB.json (deterministic: no clock in either); prints their sha256.
# Made with /usr/bin/python3 3.12.3 and numpy 1.26.4 on Ubuntu 24.04 (the interpreter the frozen outputs were written with).
# SPDX-License-Identifier: Apache-2.0
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys

FROZEN_SHA256 = '7dabaeac53c67ed52815aa7e11d356e550058085f6f5a83469be38430d5f7971'   # tools/matmul/mm1/v0/mm1_v0.py at 2d1413f5
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PRED = os.path.join(HERE, 'mm1_v0.py')
POINTS = os.path.join(TOP, 'tools', 'claims-v3', 'e206', 'points-e206.csv')
OUTPUTS = ('mm1_v0_params.json', 'mm1_v0_e206.csv', 'mm1_v0_e206.json', 'blind_day_plan.csv')
CARD_NAME = 'aifoundry1 card 1'
F_MHZ = 600.0


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def die(msg, rc):
    print('REFUSED: ' + msg)
    sys.exit(rc)


args = sys.argv[1:]
if len(args) != 4 or args[0] != '--scratch' or args[2] != '--out':
    sys.exit('usage: /usr/bin/python3 -I -B forecasts-e206-armB.py --scratch <new folder> --out <folder>')
SCR, OUT = os.path.abspath(args[1]), os.path.abspath(args[3])
for d in (SCR, OUT):
    if os.path.realpath(d) == os.path.realpath(HERE):
        die('--scratch and --out must not be this folder (the committed files beside the code stay as committed)', 2)
if os.path.realpath(SCR) == os.path.realpath(OUT):
    die('--scratch and --out must differ', 2)
if os.path.exists(SCR) and os.listdir(SCR):
    die('--scratch must be a new or empty folder (a stale output could pass the reproduction check)', 2)
os.makedirs(SCR, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# 1. the frozen predictor, by its sha256
h = sha(PRED)
print(f'frozen predictor tools/matmul/mm1/v0/mm1_v0.py sha256 {h}')
if h != FROZEN_SHA256:
    die(f'mm1_v0.py is not the committed frozen file ({FROZEN_SHA256})', 3)
SUMS = {}
for ln in open(os.path.join(HERE, 'SHA256SUMS')):
    s, n = ln.split()
    SUMS[n] = s
if SUMS.get('mm1_v0.py') != FROZEN_SHA256:
    die('SHA256SUMS does not list the frozen mm1_v0.py', 3)

# 2. import it as it stands; its module code writes its own outputs into --scratch (its printed lines go to scratch/mm1_v0-stdout.txt)
argv0 = sys.argv
sys.argv = [PRED, '--out', SCR]
buf = io.StringIO()
spec = importlib.util.spec_from_file_location('mm1_v0', PRED)
M = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(buf):
    spec.loader.exec_module(M)
sys.argv = argv0
open(os.path.join(SCR, 'mm1_v0-stdout.txt'), 'w').write(buf.getvalue())
for fn in OUTPUTS:
    got = sha(os.path.join(SCR, fn))
    if got != SUMS[fn]:
        die(f'the frozen predictor did not reproduce {fn} here ({got} against the committed {SUMS[fn]})', 4)
print('reproduction: the frozen predictor re-wrote its 4 committed outputs byte for byte: ' + ', '.join(OUTPUTS))

# the row form: the frozen module's own arm A record (mm1_v0.py, the E206 block), the card's arguments made parameters
VPTS = {p['id']: p for p in csv.DictReader(open(os.path.join(HERE, 'inputs', 'points.csv')))}


def row(p, card_key, card_name, f, V):
    pr = M.predict(card_key, card_name, p['arm'], p['format'], p['kind'], f, V, int(p['minions']))
    g = VPTS[p['id']]['group']
    rec = dict(id=p['id'], group=g, arm=p['arm'], fmt=p['format'], kind=p['kind'], shire_mask=p['shire_mask'], minions=int(p['minions']),
               cycles_per_op_wall=round(pr['cycles_per_op_wall'], 2), cycles_per_op_mean=round(pr['cycles_per_op_mean'], 2), rho=pr['rho'],
               floor_cycles=pr['floor_cycles'],
               seconds_per_gemm=(round(pr['seconds_per_gemm'], 7) if 'seconds_per_gemm' in pr else ''),
               W_over_idle=(round(pr['W_over_idle'], 3) if 'W_over_idle' in pr else ''),
               J_over_idle_per_gemm=(round(pr['J_over_idle_per_gemm'], 6) if 'J_over_idle_per_gemm' in pr else ''),
               lines=pr['lines_L2_L3_F'], footprint_MB=pr['footprint_MB'],
               sim_steps_per_minion_per_gemm=pr.get('sim_steps_per_minion_per_gemm', ''),
               note=('v0 has no contention term: a subset point carries its full-chip per-op time' if g == 'subset' else '')
                    + (pr['energy'] if isinstance(pr.get('energy'), str) else ''))
    return rec, pr


def write_csv(path, recs):
    with open(path, 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        wr.writeheader()
        [wr.writerow(r) for r in recs]


# 3. arm A rebuilt from predict() in this form must equal the committed arm A file byte for byte
A = [row(p, 'a3', 'aifoundry3 card 0', 600.0, 0.522)[0] for p in csv.DictReader(open(os.path.join(HERE, 'inputs', 'points.csv')))]
write_csv(os.path.join(SCR, 'armA-rebuilt.csv'), A)
if sha(os.path.join(SCR, 'armA-rebuilt.csv')) != SUMS['mm1_v0_e206.csv']:
    die('the row form does not rebuild the committed arm A file byte for byte', 5)
print(f'row form: arm A rebuilt from predict() ({len(A)} rows) equals the committed mm1_v0_e206.csv byte for byte')

# 4. card 1's arguments, from the frozen code and its vendored inputs
if CARD_NAME not in M.CARDS:
    die(f'{CARD_NAME!r} is not in the predictor\'s CARDS list', 6)
GT = json.load(open(os.path.join(HERE, 'inputs', 'gemm_table.json')))
c1 = [r for r in GT['rows'] if r['card'] == CARD_NAME]
keys = set()
for r in c1:
    kk = M.kindkey(r['fmt'], r['kind'])
    keys |= {ck for (ck, k2), v in M.ERES.items() if k2 == kk and abs(v - r['e_res_nJ']) <= 1e-9 * abs(v)}
if keys != {'c1'}:
    die(f'the energy table\'s card-1 rows do not name one ledger key ({sorted(keys)})', 6)
CARD_KEY = 'c1'
Vs = sorted({r['V'] for r in c1})
Ss = sorted({r['s'] for r in c1})
Gs = sorted({r['G'] for r in c1})
if len(Vs) != 1 or Ss != [1.0] or Gs != [0.0] or any(r['governed'] for r in c1):
    die(f'the energy table\'s card-1 rows do not carry one voltage, s_V 1 and G 0 (V {Vs}, s {Ss}, G {Gs})', 6)
V = Vs[0]
kinds_c1 = sorted(k2 for (ck, k2) in M.ERES if ck == CARD_KEY)
print(f'card 1: name {CARD_NAME!r} (in CARDS {M.CARDS}); ledger key {CARD_KEY!r} (the energy table\'s {len(c1)} card-1 rows carry its '
      f'resident anchors; anchors for {kinds_c1}); V {V} V (every card-1 row; s_V {(V / 0.517) ** 2:.6f}); f {F_MHZ} MHz; G 0 '
      f'(pinned: every card-1 row governed False, G 0); P_aw {M.TH["Paw|" + CARD_NAME]:.6f} W at 1,024 minions (the frozen refit)')

# 5. the arm B points of E206's registered list
REG = list(csv.DictReader(open(POINTS)))
B = [p for p in REG if p['on_arm_B'] == 'True']
bad = [p['id'] for p in B if p['id'] not in VPTS or any(p[a] != VPTS[p['id']][b] for a, b in
       (('arm', 'arm'), ('format', 'format'), ('kind', 'kind'), ('shire_mask', 'shire_mask'), ('minions', 'minions'), ('family', 'group')))]
if bad:
    die(f'registered arm B points differ from the predictor\'s vendored point list: {bad}', 7)
print(f'points: {len(REG)} registered (tools/claims-v3/e206/points-e206.csv, sha256 {sha(POINTS)}), {len(B)} with on_arm_B True; '
      f'each equals the vendored inputs/points.csv row (arm, format, kind, mask, minions, family)')
rows, sw = [], {}
for p in B:
    rec, pr = row(p, CARD_KEY, CARD_NAME, F_MHZ, V)
    rows.append(rec)
    if 'switches' in pr:
        sw[p['id']] = pr['switches']
cpath = os.path.join(OUT, 'forecasts-e206-armB.csv')
jpath = os.path.join(OUT, 'forecasts-e206-armB.json')
write_csv(cpath, rows)
json.dump(dict(what='MM1-v0 forecasts for every E206 arm B point (aifoundry1 card 1, 600 MHz), made by the frozen predictor '
                    'tools/matmul/mm1/v0/mm1_v0.py unchanged; desk; a freeze line for arm B (see forecasts-e206-armB.md)',
               python=sys.version.split()[0], numpy=M.np.__version__,
               predictor=dict(file='tools/matmul/mm1/v0/mm1_v0.py', sha256=FROZEN_SHA256, committed_in='2d1413f5'),
               points=dict(file='tools/claims-v3/e206/points-e206.csv', sha256=sha(POINTS), n_registered=len(REG), n_arm_B=len(B)),
               card=dict(card_name=CARD_NAME, card_key=CARD_KEY, f_MHz=F_MHZ, V=V, s_V=(V / 0.517) ** 2, G=0.0,
                         P_aw_W_at_1024=M.TH['Paw|' + CARD_NAME],
                         source='the frozen code (CARDS) and its vendored inputs (inputs/gemm_table.json: every card-1 row carries the c1 '
                                'resident anchors, V 0.517, s_V 1, G 0, governed False; inputs/tables.json: the c1 anchors)'),
               columns='as the arm A file mm1_v0_e206.csv: cycles an op (wall basis, the slowest minion; and the counter mean = wall / rho), '
                       'rho, the compute floor, seconds a GEMM, W over idle, J over idle a GEMM, lines a shire-op [L2, L3, fresh], '
                       'footprint MB, the timing simulation\'s steps a minion a GEMM, note',
               rows=rows,
               switches_reported=dict(label='REPORTED, not scorable (no switch count is measured on any card); predict()\'s own '
                                            'transistor-switch output, fin edges a GEMM: counted tensor unit [lo, hi] and the '
                                            'energy-scaled rest [low, central, high] (README.md section 5)',
                                      by_id=sw)),
          open(jpath, 'w'), indent=1)
ne = sum(1 for r in rows if r['W_over_idle'] != '')
print(f'arm B rows {len(rows)}, with energy {ne}, without {len(rows) - ne} (no frozen resident anchor for their kind)')
print(f'{sha(cpath)}  forecasts-e206-armB.csv')
print(f'{sha(jpath)}  forecasts-e206-armB.json')
