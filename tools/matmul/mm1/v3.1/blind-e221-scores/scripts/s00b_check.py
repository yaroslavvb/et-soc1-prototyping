#!/usr/bin/env python3
"""blind-e221 (Q235) step 0b: EVERY FROZEN FILE'S sha256, before anything else (the lane's text: 'check every frozen file's sha256 first').
Desk; stdlib; no E221 data file is opened. Checks, each recorded with its count:
  1. the frozen models as landed on GitHub main (work/lab, s00_setup.sh's archive): sha256sum -c of MM1-v3.2, v3.1 (and its counts), v3, v2 and
     the two v3.2 terms (layout, gemmlnc: SHA256SUMS and the dated-note sums); each SHA256SUMS and params file against the declaration's
     table (DECLARED-blind-e221.json inputs_sha256); E215's band code;
  2. every file of decl-e221's own archive (0f046200) equal, by sha256, to this lane's archive at today's main (nothing in the models changed);
  3. FROZEN.txt (2df06f06...) and the four files it freezes against the posted record (W/out/orch/q235-frozen-posts.txt, #15.2.1.1), on
     decl-e221's lane files and on its land dir (copied to work/decl/: its SHA256SUMS -c); FROZEN.txt's supporting lines on both;
  4. the declaration's own input table (52 sha256, relative to decl-e221's lane) on decl-e221's lane files, and on this lane's copies where
     a copy exists (work/verify-lay, work/cands, work/decl/inputs);
  5. the three MM1-v3.3 candidates: each FROZEN.txt and posted forecast file against W/out/orch/q234-frozen-posts.txt, on the copies
     decl-e221 ran (work/cands) and on the landed copies at main (tools/matmul/mm1/v3.3-cands); the files their makers import at run time
     from their own lane folders (layout2's f02_private.py and verify-lay's v01_map.py) against the copies;
  6. E221's registration on main (tools/claims-v3/e221/SHA256SUMS-e221-registration -c) and the orchestrator's kit copy (5680112f...).
Run: /usr/bin/python3 -I -B s00b_check.py <lane dir>      Writes logs/step0-checks.json; exit 1 on any failure.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

L = os.path.abspath(sys.argv[1])
W = '<WF>'
D = os.path.join(W, 'out', 'decl-e221')
WL = os.path.join(L, 'work', 'lab')
M = os.path.join(WL, 'tools', 'matmul', 'mm1')
DEC = os.path.join(L, 'work', 'decl')
rec = {'what': 'blind-e221 step 0b: every frozen file by sha256', 'python': sys.version.split()[0], 'checks': {}, 'failures': []}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ok(name, cond, detail=None):
    rec['checks'][name] = {'ok': bool(cond), 'detail': detail}
    if not cond:
        rec['failures'].append(name)
    print(('OK   ' if cond else 'FAIL ') + name + ('' if detail is None else ' :: ' + json.dumps(detail)[:300]))


def sumsc(d, f='SHA256SUMS'):
    r = subprocess.run(['sha256sum', '-c', f], cwd=d, capture_output=True, text=True)
    lines = [x for x in r.stdout.splitlines() if x.strip()]
    return r.returncode, sum(1 for x in lines if x.endswith(': OK')), sum(1 for x in lines if not x.endswith(': OK'))


DECLJ = json.load(open(os.path.join(D, 'DECLARED-blind-e221.json')))
INP = DECLJ['inputs_sha256']
# ------------------------------------------------------------------ 1. the models as landed at today's main
for nm, d, f in (('MM1-v3.2', 'v3.2', 'SHA256SUMS'), ('MM1-v3.1', 'v3.1', 'SHA256SUMS'), ('MM1-v3.1 counts', 'v3.1/counts', 'SHA256SUMS'),
                 ('MM1-v3', 'v3', 'SHA256SUMS'), ('MM1-v2', 'v2', 'SHA256SUMS'), ('layout term', 'v3.2-terms/layout', 'SHA256SUMS'),
                 ('layout term note 1', 'v3.2-terms/layout', 'SHA256SUMS-note1'), ('gemmLnc term', 'v3.2-terms/gemmlnc', 'SHA256SUMS')):
    p = os.path.join(M, d, f)
    if not os.path.exists(p):
        ok(f'1 {nm} {f} present', False, p)
        continue
    rc, nok, nbad = sumsc(os.path.join(M, d), f)
    ok(f'1 {nm} sha256sum -c {f}', rc == 0 and nbad == 0, {'OK': nok, 'not_OK': nbad, 'sums_sha256': sha(p)})
for k, v in INP.items():
    if k.startswith('work/lab/'):
        p = os.path.join(WL, k[len('work/lab/'):])
        ok(f'1 declared pin {k} at today\'s main', os.path.exists(p) and sha(p) == v, v[:16])
# ------------------------------------------------------------------ 2. decl-e221's archive (0f046200) equal to this lane's (today's main)
DW = os.path.join(D, 'work', 'lab')
n = neq = 0
diff = []
for top_dir, _, files in os.walk(DW):
    for fn in files:
        p = os.path.join(top_dir, fn)
        rel = os.path.relpath(p, DW)
        n += 1
        q = os.path.join(WL, rel)
        if os.path.exists(q) and sha(q) == sha(p):
            neq += 1
        else:
            diff.append(rel)
ok('2 decl-e221 archive (0f046200) files equal in this lane\'s archive (today\'s main)', n > 0 and neq == n,
   {'files': n, 'equal': neq, 'differ_or_missing': diff[:20]})
# ------------------------------------------------------------------ 3. FROZEN.txt, the posted record, the land
POST = open(os.path.join(W, 'out', 'orch', 'q235-frozen-posts.txt')).read()
pl = [x for x in POST.splitlines() if x.startswith('#15.2.1.1 ')]
ok('3 the posted record has the freeze line #15.2.1.1', len(pl) == 1, pl[0][:120] if pl else None)
posted = dict((b, a) for a, b in re.findall(r'(\S+) ([0-9a-f]{64})', pl[0])) if pl else {}
posted_by_name = {}
for name, h in re.findall(r'(FROZEN\.txt|DECLARED-blind-e221\.md|DECLARED-blind-e221\.json|forecasts-nominal-e221\.csv|forecasts-nominal-e221\.json) ([0-9a-f]{64})',
                          pl[0] if pl else ''):
    posted_by_name[name] = h
ok('3 the posted line names five sha256', len(posted_by_name) == 5, posted_by_name)
FROZ = '2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b'
for base, lab in ((D, 'decl-e221 lane'), (DEC, 'work/decl (decl-e221 land copy)')):
    ok(f'3 FROZEN.txt on {lab} = 2df06f06 = posted', sha(os.path.join(base, 'FROZEN.txt')) == FROZ == posted_by_name.get('FROZEN.txt'))
    for fn in ('DECLARED-blind-e221.md', 'DECLARED-blind-e221.json', 'forecasts-nominal-e221.csv', 'forecasts-nominal-e221.json'):
        ok(f'3 {fn} on {lab} = posted', sha(os.path.join(base, fn)) == posted_by_name.get(fn), posted_by_name.get(fn, '')[:16])
rc, nok, nbad = sumsc(DEC)
ok('3 decl-e221 land (work/decl) sha256sum -c SHA256SUMS', rc == 0 and nbad == 0, {'OK': nok, 'not_OK': nbad, 'sums_sha256': sha(os.path.join(DEC, 'SHA256SUMS'))})
rc, nok, nbad = sumsc(os.path.join(D, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'blind-e221'))
ok('3 decl-e221 land (its own folder) sha256sum -c SHA256SUMS', rc == 0 and nbad == 0, {'OK': nok, 'not_OK': nbad})
ok('3 decl-e221 land SHA256SUMS = a83c90fc (decl-e221 result)', sha(os.path.join(DEC, 'SHA256SUMS')).startswith('a83c90fc'), sha(os.path.join(DEC, 'SHA256SUMS'))[:16])
FT = open(os.path.join(D, 'FROZEN.txt')).read()
sup = re.findall(r'^([0-9a-f]{64})  (\S+)$', FT, re.M)
ok('3 FROZEN.txt lists 4 frozen + 9 supporting sha256', len(sup) == 13, len(sup))
LANDMAP = {'scripts/': 'scripts/', 'work/step2/': 'inputs/step2/', 'logs/': 'logs/'}
for h, rel in sup:
    ok(f'3 FROZEN.txt line {rel} on decl-e221 lane', sha(os.path.join(D, rel)) == h, h[:16])
    lr = rel
    for a, b in LANDMAP.items():
        if rel.startswith(a):
            lr = b + rel[len(a):]
    q = os.path.join(DEC, lr)
    if os.path.exists(q) and lr != rel or rel in ('DECLARED-blind-e221.md', 'DECLARED-blind-e221.json', 'forecasts-nominal-e221.csv',
                                                  'forecasts-nominal-e221.json'):
        ok(f'3 FROZEN.txt line {rel} on work/decl ({lr})', os.path.exists(q) and sha(q) == h, h[:16])
# ------------------------------------------------------------------ 4. the declaration's input table
nin = nin_ok = 0
for k, v in INP.items():
    nin += 1
    p = os.path.join(D, k)
    good = os.path.exists(p) and sha(p) == v
    nin_ok += good
    if not good:
        rec['failures'].append(f'4 declared input {k} on decl-e221 lane')
ok('4 the declaration\'s input table on decl-e221\'s lane files', nin == nin_ok == 52, {'inputs': nin, 'equal': nin_ok})
ncp = ncp_ok = 0
for k, v in INP.items():
    for pre, mine in (('work/verify-lay/', os.path.join(L, 'work', 'verify-lay')), ('work/cands/', os.path.join(L, 'work', 'cands')),
                      ('work/step1/', os.path.join(DEC, 'inputs', 'step1')), ('work/step2/', os.path.join(DEC, 'inputs', 'step2'))):
        if k.startswith(pre):
            ncp += 1
            p = os.path.join(mine, k[len(pre):])
            g = os.path.exists(p) and sha(p) == v
            ncp_ok += g
            if not g:
                rec['failures'].append(f'4 declared input {k} on this lane\'s copy')
ok('4 the declaration\'s inputs on this lane\'s copies (verify-lay, cands, work/decl/inputs)', ncp == ncp_ok and ncp > 0, {'inputs': ncp, 'equal': ncp_ok})
# s02b_nominal.py's POSTED table (the terms' posted files and the candidates' frozen files), on this lane's copies
S02B = open(os.path.join(DEC, 'scripts', 's02b_nominal.py')).read()
ok('4 work/decl/scripts/s02b_nominal.py = b4303018 (FROZEN.txt supporting line)', sha(os.path.join(DEC, 'scripts', 's02b_nominal.py')).startswith('b4303018'))
pn = pn_ok = 0
for m in re.finditer(r"os\.path\.join\((LAY|LNC|CANDS|L), ([^)]*)\): '([0-9a-f]{64})'", S02B):
    base, parts, h = m.group(1), [x.strip().strip("'") for x in m.group(2).split(',')], m.group(3)
    base_dir = {'LAY': os.path.join(M, 'v3.2-terms', 'layout'), 'LNC': os.path.join(M, 'v3.2-terms', 'gemmlnc'), 'CANDS': os.path.join(L, 'work', 'cands'),
            'L': L}[base]
    p = os.path.join(base_dir, *parts)
    pn += 1
    g = os.path.exists(p) and sha(p) == h
    pn_ok += g
    if not g:
        rec['failures'].append(f'4 s02b POSTED pin {base}/{"/".join(parts)}')
ok("4 s02b_nominal.py's POSTED pins (the terms' posted files, verify-lay's, the candidates' frozen files) on this lane's copies",
   pn == pn_ok == 20, {'pins': pn, 'equal': pn_ok})
# ------------------------------------------------------------------ 5. the candidates against their posted record and their landed copies
Q234 = [x for x in open(os.path.join(W, 'out', 'orch', 'q234-frozen-posts.txt')).read().splitlines() if x.startswith('#')]
CAND = {'layout2': ('posimb', "'MM1-v3.2 + posimb'", 'forecasts-e220-posimb'), 'lnc-form': ('gemmlnc-af4', 'AF4', 'forecasts-e220-af4'),
        'l3-edge': ('l3s', "'MM1-v3.2 + L3S'", 'forecasts-e220-l3s')}
for lane, (sub, tag, stem) in CAND.items():
    ln = [x for x in Q234 if tag in x]
    if len(ln) != 1:
        ok(f'5 {lane}: one posted line', False, len(ln))
        continue
    ln = ln[0]
    hf = re.search(r'FROZEN\.txt ([0-9a-f]{64})', ln).group(1)
    hc = re.search(re.escape(stem) + r'\.csv ([0-9a-f]{64})', ln).group(1)
    hj = re.search(r', \.json ([0-9a-f]{64})', ln).group(1)
    ht = re.search(r', \.txt ([0-9a-f]{64})', ln)
    ok(f'5 {lane} FROZEN.txt (copy decl-e221 ran) = posted {hf[:8]}', sha(os.path.join(L, 'work', 'cands', lane, 'FROZEN.txt')) == hf)
    pm = os.path.join(M, 'v3.3-cands', sub, 'FROZEN-e220.txt')
    ok(f'5 {lane} FROZEN.txt = landed {sub}/FROZEN-e220.txt at main', os.path.exists(pm) and sha(pm) == hf)
    for ext, h in (('.csv', hc), ('.json', hj), ('.txt', ht.group(1) if ht else None)):
        if h is None:
            continue
        fn = stem + ext
        cp = os.path.join(L, 'work', 'cands', lane, 'land', 'tools', 'matmul', 'mm1', 'v3.3-cands', sub, fn)
        ok(f'5 {lane} {fn} (copy) = posted {h[:8]}', os.path.exists(cp) and sha(cp) == h)
        pm = os.path.join(M, 'v3.3-cands', sub, fn)
        ok(f'5 {lane} {fn} = landed at main', os.path.exists(pm) and sha(pm) == h)
# posimb's makers: decl-e221 ran the as-run copies (layout2's lane paths); the landed copies differ in the LANE (and REG) lines only (SCRUB.json)
SCR = json.load(open(os.path.join(M, 'v3.3-cands', 'posimb', 'SCRUB.json')))
for fn, nrep in (('h01_freeze.py', 2), ('f02_private.py', 1)):
    asrun = os.path.join(L, 'work', 'cands', 'layout2', 'scripts', fn)
    landed = os.path.join(M, 'v3.3-cands', 'posimb', 'scripts', fn)
    e = SCR['files']['scripts/' + fn]
    ok(f'5 posimb {fn}: the copy decl-e221 ran = SCRUB.json sha256_as_run', sha(asrun) == e['sha256_as_run'], e['sha256_as_run'][:16])
    ok(f'5 posimb {fn}: landed at main = SCRUB.json sha256_landed', sha(landed) == e['sha256_landed'], e['sha256_landed'][:16])
    la, lb = open(asrun).read().splitlines(), open(landed).read().splitlines()
    dl = [i for i in range(max(len(la), len(lb))) if (la[i] if i < len(la) else None) != (lb[i] if i < len(lb) else None)]
    words = [(lb[i].split('=')[0].strip() if i < len(lb) else None) for i in dl]
    ok(f'5 posimb {fn}: as run vs landed differ in {nrep} line(s), path constants only', len(la) == len(lb) and len(dl) == nrep == e['replacements']
       and set(words) <= {'LANE', 'REG'}, {'lines': [i + 1 for i in dl], 'names': words})
    ok(f'5 posimb {fn}: out/layout2 (its lane) still holds the as-run file', sha(os.path.join(W, 'out', 'layout2', 'scripts', fn)) == e['sha256_as_run'])
st = os.path.join(L, 'work', 'layout2-lane', 'scripts', 'f02_private.py')
ok("5 posimb stand-in lane: scripts/f02_private.py = the landed copy", sha(st) == SCR['files']['scripts/f02_private.py']['sha256_landed'])
ok("5 posimb stand-in lane: work/lab is this lane's archive", os.path.realpath(os.path.join(L, 'work', 'layout2-lane', 'work', 'lab')) == os.path.realpath(WL))
ok("5 layout2's own lane clone (out/layout2/work/lab) is gone (removed by the 16:07 cleanup): the as-run makers cannot import",
   not os.path.exists(os.path.join(W, 'out', 'layout2', 'work', 'lab')))
# the files f02_private and v01_map read at import, at main: unchanged since before layout2's run (05:05-05:46 PST Fri 20 Nov)
for rel in ('tools/matmul/mm1/v3.2-terms/layout/controls-e215/v01_map.py', 'workloads/nocbench/analyze.py'):
    r = subprocess.run(['git', '-C', '<LAB>', 'log', '-1', '--format=%h %ct %ci', open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip(), '--', rel],
                       capture_output=True, text=True)
    hh, ct = r.stdout.split()[0], int(r.stdout.split()[1])
    ok(f'5 {rel}: last changed on main before 20 Nov 05:00 PST ({hh})', ct < 1795179600, r.stdout.strip())
# L3S: decl-e221 ran its as-run copies (l3-edge's lane), which REWRITES.tsv of the land names as the 'as run' sha256
RW = {}
for x in open(os.path.join(M, 'v3.3-cands', 'l3s', 'scripts', 'REWRITES.tsv')).read().splitlines():
    if x and not x.startswith('#'):
        a3 = x.split('\t')
        RW[a3[0]] = (a3[1], a3[2])
for fn in ('term_l3s.py', 'costs.py', 'l3s_feature.py', 'l3sim.py'):
    asrun = os.path.join(L, 'work', 'cands', 'l3-edge', 'scripts', fn)
    ok(f'5 L3S {fn}: the copy decl-e221 ran = REWRITES.tsv as-run sha256', fn in RW and sha(asrun) == RW[fn][0], RW.get(fn, ('',))[0][:16])
    ok(f'5 L3S {fn}: landed at main = REWRITES.tsv landed sha256', fn in RW and sha(os.path.join(M, 'v3.3-cands', 'l3s', 'scripts', fn)) == RW[fn][1])
# ------------------------------------------------------------------ 6. E221's registration and the kit copy
rc, nok, nbad = sumsc(WL, 'tools/claims-v3/e221/SHA256SUMS-e221-registration')   # its paths are the repository's
ok('6 E221 registration at main: sha256sum -c SHA256SUMS-e221-registration', rc == 0 and nbad == 0, {'OK': nok, 'not_OK': nbad})
ok('6 the orchestrator\'s kit copy SRC-SHA256SUMS.txt = 5680112f', sha(os.path.join(W, 'out', 'orch', 'e221-src', 'SRC-SHA256SUMS.txt')).startswith('5680112f'))
ok('6 decl-e221\'s kit copy SRC-SHA256SUMS.txt = the orchestrator\'s',
   sha(os.path.join(D, 'work', 'e221-src', 'SRC-SHA256SUMS.txt')) == sha(os.path.join(W, 'out', 'orch', 'e221-src', 'SRC-SHA256SUMS.txt')))
rec['lab_commit'] = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
rec['n_checks'] = len(rec['checks'])
rec['n_failed'] = len(rec['failures'])
json.dump(rec, open(os.path.join(L, 'logs', 'step0-checks.json'), 'w'), indent=1, sort_keys=True)
print(f"checks {rec['n_checks']}, failed {rec['n_failed']}: {rec['failures'][:10]}")
sys.exit(1 if rec['failures'] else 0)
