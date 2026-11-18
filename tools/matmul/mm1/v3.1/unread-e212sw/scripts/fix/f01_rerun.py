#!/usr/bin/env python3
"""fix-unread-e212sw (Q218) step 02: re-run the unread lane's frozen scorer, unchanged, and read its numbers at full precision.

1. A fresh copy of the scorer's inputs in work/rerun/: the landed declaration (sha256 5eb2c93d...) and forecasts (8938bbeb...), MM1-v3's folder and
   the counts folder from this lane's `git archive` of GitHub main 3e8991d0 (step 01).
2. The as-run scorer OUT/unread-e212sw/scripts/s03_score.py (sha256 74df0a06..., asserted) is executed as written (exec of its own source, with
   sys.argv = [it, work/rerun]); it reads E212's data by `git show 8e91dda6:...` from the lab clone and writes work/rerun/work/step3/.
3. Its outputs are compared with the land dir's: the two CSVs byte for byte, the JSON field by field without its two clock stamps.
4. Precision: the README printed every rms and mean from the JSON's values rounded to 3 decimals and then to 2 (finding 7 of
   verify-unread-e212sw). The same blocks are recomputed here from the scorer's own rows with the rounding left out, and every printed figure whose
   2-decimal form differs is listed; the per-case table (section 5) is checked the same way against the cases CSV's 6-decimal values.
Desk; no device; single-threaded (run inside slot.sh). Run: /usr/bin/python3 -I -B f01_rerun.py
"""
import contextlib
import csv
import hashlib
import io
import json
import math
import os
import shutil
import sys

W = '<W>'
ME = os.path.join(W, 'out', 'fix-unread-e212sw')
UL = os.path.join(W, 'out', 'unread-e212sw')
LANDU = os.path.join(UL, 'land', 'tools', 'matmul', 'mm1', 'v3.1', 'unread-e212sw')
RR = os.path.join(ME, 'work', 'rerun')
S03 = os.path.join(UL, 'scripts', 's03_score.py')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


assert sha(S03) == '74df0a0688179a22c2f65c5567a7989eed0f6940abff6ba308aab176bdb743ab', 'scorer differs from the as-run copy'
assert not os.path.exists(RR), 'rerun dir exists'
os.makedirs(os.path.join(RR, 'work', 'lab', 'tools', 'matmul', 'mm1'))
for f, h in (('declared-unread.json', '5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc'),
             ('forecasts-unread.json', '8938bbebd1a6db028d55602773e7c2bce7286f6e378f2bcede948f82deb79f01')):
    shutil.copy2(os.path.join(LANDU, f), os.path.join(RR, f))
    assert sha(os.path.join(RR, f)) == h, f
shutil.copytree(os.path.join(ME, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3'), os.path.join(RR, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3'))
shutil.copytree(os.path.join(ME, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3.1', 'counts'), os.path.join(RR, 'work', 'counts'))

# ---------------------------------------------------------------- 2. the frozen scorer, as written
ns = {'__name__': '__main__', '__file__': S03}
argv0 = sys.argv[:]
sys.argv = [S03, RR]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(open(S03).read(), S03, 'exec'), ns)
sys.argv = argv0
open(os.path.join(ME, 'logs', 'f01_s03_rerun.out'), 'w').write(buf.getvalue())
print('scorer re-run done; its output in logs/f01_s03_rerun.out; VERDICT', ns['verdict']['verdict'])

# ---------------------------------------------------------------- 3. outputs against the land dir's
out3 = os.path.join(RR, 'work', 'step3')
cmp = {}
for f in ('scores-unread-runs.csv', 'scores-unread-cases.csv'):
    cmp[f] = {'rerun': sha(os.path.join(out3, f)), 'land': sha(os.path.join(LANDU, f))}
    cmp[f]['byte_equal'] = cmp[f]['rerun'] == cmp[f]['land']
a = json.load(open(os.path.join(out3, 'scores-unread.json')))
b = json.load(open(os.path.join(LANDU, 'scores-unread.json')))
stamps = {k: (a.pop(k), b.pop(k)) for k in ('start_pst', 'end_pst')}
cmp['scores-unread.json'] = {'equal_without_clock_stamps': a == b, 'stamps_rerun_vs_land': stamps}
print(json.dumps(cmp, indent=1))
assert all(v.get('byte_equal', v.get('equal_without_clock_stamps')) for v in cmp.values()), 'the re-run differs'

# ---------------------------------------------------------------- 4. full precision
def st_full(es):
    es = [e for e in es if e is not None and not (isinstance(e, float) and math.isnan(e))]
    if not es:
        return None
    n = len(es)
    rms = 100 * math.sqrt(sum(e * e for e in es) / n)
    mean = 100 * sum(es) / n
    return {'n': n, 'rms_pct': round(rms, 3), 'mean_pct': round(mean, 3), 'rms_full': rms, 'mean_full': mean}


ns['st'] = st_full            # the scorer's own functions look st up in this namespace
rule, head, block = ns['rule'], ns['head'], ns['block']
crow, rows = ns['crow'], ns['rows']
A_cases = [c for c in crow if c['group'] == 'A']
full = {'pass_rule_against_N': rule(A_cases, 'N'),
        'reported': {'against_N2': rule(A_cases, 'N2'),
                     'against_V1_where_it_applies': rule([c for c in A_cases if c.get('e1_V1') is not None or c.get('e2_V1') is not None], 'V1'),
                     'E212_alone_against_N': rule([c for c in A_cases if c['source'] == 'E212'], 'N'),
                     'E206_E207_alone_against_N': rule([c for c in A_cases if c['source'] != 'E212'], 'N')}}
scored = [r for r in rows if not r.get('not_scored')]
groups = {}
for g in ('A', 'B', 'C'):
    cs = [c for c in crow if c['group'] == g]
    rs = [r for r in scored if r['group'] == g]
    groups[g] = {'all': block(cs, rs)}
    for key in ('card', 'fmt', 'source'):
        for val in sorted({c[key] for c in cs}):
            groups[g][f'{key}={val}'] = block([c for c in cs if c[key] == val], [r for r in rs if r[key] == val])
    for lab, fn in (('tabulated by an MM1-v3 design/spec lane', lambda c: c['spec_tabulated'] or c['design_c_printed']),
                    ('not tabulated by any MM1-v3 design/spec lane', lambda c: not (c['spec_tabulated'] or c['design_c_printed']))):
        sub = [c for c in cs if fn(c)]
        ids = {i for c in sub for i in c['runs']}
        groups[g][lab] = block(sub, [r for r in rs if r['id'] in ids])
full['groups'] = groups

slips = []


def walk(o, path):
    if isinstance(o, dict):
        if 'rms_full' in o:
            for k, kf, fm in (('rms_pct', 'rms_full', '{:.2f}'), ('mean_pct', 'mean_full', '{:+.2f}')):
                if fm.format(o[k]) != fm.format(o[kf]):
                    slips.append({'where': path + '.' + k, 'printed_from_3dp': fm.format(o[k]), 'from_unrounded': fm.format(o[kf]),
                                  'value_3dp': o[k], 'value_unrounded': o[kf], 'n': o['n']})
        for k, v in o.items():
            walk(v, path + '.' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + f'[{i}]')


walk(full, 'scores')
# section 5: the cases CSV's 6-decimal values, printed as % with 1 decimal (errors), 2 (W, D) or 3 (s)
CS = list(csv.DictReader(open(os.path.join(LANDU, 'scores-unread-cases.csv'))))
cfull = {(c['group'], c['case']): c for c in crow}
case_slips = []
for c in CS:
    f = cfull[(c['group'], c['case'])]
    for k in ('e1_V3', 'e1_N', 'e1_V1', 'e2_V3', 'e2_N'):
        if c[k] in ('', None):
            continue
        p6, pf = f'{100 * float(c[k]):+.1f}', f'{100 * f[k]:+.1f}'
        if p6 != pf:
            case_slips.append({'case': c['case'], 'field': k, 'printed': p6, 'from_unrounded': pf, 'unrounded_pct': 100 * f[k]})
    for k, fm in (('W_meas', '{:.2f}'), ('D_W', '{:.2f}'), ('s_meas', '{:.3f}'), ('s_V3', '{:.3f}')):
        if c[k] in ('', None):
            continue
        if fm.format(float(c[k])) != fm.format(f[k]):
            case_slips.append({'case': c['case'], 'field': k, 'printed': fm.format(float(c[k])), 'from_unrounded': fm.format(f[k])})
ga = groups['A']['all']['V3']
per_run = {'Q1_runs': ga['Q1_runs'], 'Q2_runs': ga['Q2_runs']}
res = {'what': 'fix-unread-e212sw step 02: the frozen scorer re-run unchanged, and its figures at full precision',
       'interpreter': sys.version.split()[0], 'scorer_sha256': sha(S03), 'compare_with_land': cmp,
       'verdict_rerun': ns['verdict']['verdict'], 'per_run_group_A_unrounded': per_run,
       'slips_2dp_in_sections_0_4_6': slips, 'slips_in_section_5': case_slips,
       'group_A_cases_full': [{k: c.get(k) for k in ('group', 'case', 'source', 'card', 'fmt', 'n_runs', 'e1_V3', 'e1_N', 'e1_N2', 'e2_V3', 'e2_N',
                                                     'e2_N2', 'spec_tabulated', 'design_c_printed', 'twin')} for c in A_cases],
       'group_B_cases_full': [{k: c.get(k) for k in ('group', 'case', 'source', 'card', 'fmt', 'n_runs', 'e1_V3', 'e1_N', 'e1_N2', 'e2_V3', 'e2_N')}
                              for c in crow if c['group'] == 'B'],
       'pass_rule_full': full['pass_rule_against_N'], 'groups_full': groups, 'reported_full': full['reported']}
json.dump(res, open(os.path.join(ME, 'work', 'rerun-full.json'), 'w'), indent=1, sort_keys=True, default=str)
print('per-run group A, unrounded:', json.dumps(per_run))
print('2-decimal slips in the README sections 0, 4, 6 (from 3-decimal values):', len(slips))
for s in slips:
    print(' ', json.dumps(s))
print('section-5 slips:', len(case_slips))
for s in case_slips:
    print(' ', json.dumps(s))
print('work/rerun-full.json', sha(os.path.join(ME, 'work', 'rerun-full.json')))
