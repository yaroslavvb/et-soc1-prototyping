#!/usr/bin/env python3
"""blind-e219 (Q232) step 3: THE READ AND THE SCORE, exactly as decl-e219's DECLARED-blind-e219.json says (sections 0, a-h; hashed 18:37:19
PST, FROZEN.txt 18:37:50, posted #14.1.1) on the measured-conditions forecasts frozen in forecasts-blind-e219.json (hashed in
logs/step2-sha256.txt) and, beside it (REPORTED, deciding nothing), the NOMINAL footing frozen by decl-e219 (forecasts-nominal-e219.json).
This script is hashed before its first read of any E219 measurement. blind-e217's s03_score.py in form.
Reads E219's committed data-e219-<s>.json (GitHub main, `git show` of work/lab-commit.txt's commit; copied to work/step3/data/ and hashed)
and each session's queue (session/queue.json: ran, rc 0, check exact or approx) and README (its first card command): the measurement fields
now. Scores per run and per case: T1 wall cycles, T2 counter mean, T3 seconds a pass (ops a minion a pass by the kit's grammar x the op
time), E1 J over idle given t (watts at a watts case), E2 J over idle with t forecast, E3 J at rest given t, E4 J at rest with t forecast;
per card and pooled; twins apart (no-twin cases carry the pass rule and the headline); splits per class (CTRL apart, GAP, ANCHOR, CTAB,
C16R), FULL / SUB, format and kind; the pass rule (part A: MM1-v3.1 on the primary footing by E215's rule form per card over the IN-DOMAIN
no-twin cases; part S NOT APPLICABLE); the comparisons D1 (MM1-v3.1 vs MM1-v3), D2 (MM1-v3.1 vs MM1-v2), D3 (the layout term and
verify-lay's controls vs MM1-v3.1 on the subset masks; TOO FEW by construction, as declared), D4 NOT APPLICABLE; REPORTED beside: the R
ladder (gemmc16 as R = 1), the CTRL cases beside E217's committed means, the gemmc4s/gemmc8s pair (decl-e219's finding 2), the OUT-OF-DOMAIN
cases (measured values only, in no rule, comparison or headline); the label per session (BLIND / UNREAD / POST-READ by the freeze post's
time and the session's first card command). Checks first that its own run selection and readings equal MM1-v3.1's loader
(data_v31.mms_runs_all) on the same bytes for the gemmL runs (the loader reads gemmL values only). Desk; stdlib (the loader imports numpy).
Run: /usr/bin/python3 -I -B s03_score.py <lane dir>      (a stand-in test: ... <lane dir> --standin <dir>, outputs in work/step3-standin-<name>/)
"""
import collections
import csv
import datetime
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import zoneinfo

L = os.path.abspath(sys.argv[1])
STANDIN = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--standin' else None   # a stand-in day, never E219
LAB = '<LAB>'
W = '<W>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='<GITHUB_SSH_PREFIX>')
S3 = os.path.join(L, 'work', 'step3' if STANDIN is None else 'step3-standin-' + os.path.basename(STANDIN))
os.makedirs(os.path.join(S3, 'data'), exist_ok=True)
os.makedirs(os.path.join(S3, 'e217'), exist_ok=True)
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
DEC = os.path.join(L, 'work', 'decl')
TZ = zoneinfo.ZoneInfo('America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return datetime.datetime.now(TZ).strftime('%a %d %b %Y %H:%M:%S %Z')


def git(*a, text=False):
    return subprocess.run(['git', '-C', LAB] + list(a), check=True, capture_output=True, text=text, env=ENV).stdout


T_START = ts()
# ------------------------------------------------------------------ the frozen inputs, by their logged sha256
PINS = {os.path.join(DEC, 'DECLARED-blind-e219.json'): '670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479',
        os.path.join(DEC, 'DECLARED-blind-e219.md'): 'd629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495',
        os.path.join(DEC, 'FROZEN.txt'): '73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e',
        os.path.join(DEC, 'forecasts-nominal-e219.json'): 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '0bd052dcbc277c9937c82b1c7dce04124e41deb1b57e21e4699271c8aa2d3376',
        os.path.join(L, 'forecasts-blind-e219.json'): 'a5a3c103b13e34eef5821716b53956bc68545fc9594f56bbe9e928e05805be36',
        os.path.join(L, 'forecasts-blind-e219.csv'): '6ebeb3951b6bd023b2771717bb9b63b00eae7ea4d8e5dfed162cbe384a104e5b',
        os.path.join(L, 'work', 'step2', 'conditions-e219.json'): '4f9c8b8952b6ca33cd9607ca14b077c3ef497405b6c82ae0b0be35a6bdcf0e02'}
for p, h in PINS.items():
    assert sha(p) == h, p
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e219.json')))
FCJ = json.load(open(os.path.join(L, 'forecasts-blind-e219.json')))
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e219.json')))['cases']
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
CONDJ = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e219.json')))
MODELS = ('v31', 'v3', 'v2', 'v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b')
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'v3.1+contention', 'v31b': 'v3.1+both', 'cn12': 'ctrl N1+N2', 'cg1': 'ctrl G1',
      'cg1n1': 'ctrl G1+N1', 'cf1b': 'ctrl F1-layout-blind'}
assert FCJ['models'] == MN
TWIN_OF = {'v31': 'v31', 'v3': 'v3', 'v2': 'v2', 'v31c': 'v31', 'v31b': 'v31', 'cn12': 'v31', 'cg1': 'v31', 'cg1n1': 'v31', 'cf1b': 'v31'}
C0, C1 = 'aifoundry1 card 0', 'aifoundry1 card 1'
CARDS = (C1, C0)
LOW = 3.0
BANDS = DECL['f_pass_rule']['bands']
TIES = DECL['d_comparisons']['ties']
PASS_FRAC, TOO_FEW, ALPHA = 0.9, 10, 0.05
SHAPE = re.compile(r'gemmL(\d+)x(\d+)x(\d+):')
CLASSES = ('CTRL', 'GAP', 'ANCHOR', 'CTAB', 'C16R')
OKCHK = ('exact', 'approx')
R_IN_FIT = [2, 4, 8, 32]
R_NEVER = [3, 5, 6, 12, 16, 24]
assert 'R in any fit [2, 4, 8, 32]' in open(os.path.join(DEC, 'DECLARED-blind-e219.md')).read()

# ------------------------------------------------------------------ the read
DATA, QUEUE, srcs = {}, {}, {}
for s, d in sorted(CONDJ['sessions'].items()):
    path = d['file']
    qpath = f"{d['folder']}/session/queue.json"
    if STANDIN is None:
        raw = git('show', f'{COMMIT}:{path}')
        qraw = git('show', f'{COMMIT}:{qpath}')
    else:
        path = os.path.join(STANDIN, f'data-e219-{s}.json')
        qpath = os.path.join(STANDIN, f'queue-{s}.json')
        raw = open(path, 'rb').read()
        qraw = open(qpath, 'rb').read()
    dst = os.path.join(S3, 'data', f'data-e219-{s}.json')
    open(dst, 'wb').write(raw)
    open(os.path.join(S3, 'data', f'queue-{s}.json'), 'wb').write(qraw)
    h = hashlib.sha256(raw).hexdigest()
    srcs[s] = {'path': path, 'sha256': h, 'equal_to_step2a_conditions_read': h == d['sha256'], 'queue_path': qpath,
               'queue_sha256': hashlib.sha256(qraw).hexdigest()}
    if STANDIN is None:
        assert h == d['sha256'], (s, 'the committed file differs from the one step 2a read')
    DATA[s] = json.loads(raw)
    QUEUE[s] = json.loads(qraw)
T_READ = ts()


def queue_entry(s, run):
    for q in QUEUE[s].get('queue') or []:
        if q.get('run') == run:
            return q
    return None


meas = {}
qsel = collections.Counter()
for s, Dj in DATA.items():
    pv = Dj['primary_view']
    byrun = {r['run']: r for r in Dj['runs']}
    for r in [x for x in RL['runs'] if x['session'] == s]:
        x = byrun[r['run']]
        v = (x.get('views') or {}).get(pv) or {}
        vals = str(x.get('values') or '')
        tok = vals.split(':', 1)[0] if ':' in vals else None
        gl = bool(SHAPE.match(vals))
        base = bool(x.get('ran') and x.get('role') not in (None, 'null') and x.get('arm') and x.get('shires') and tok and tok == r['token'] and
                    v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1)
        block_ok = gl or bool(x.get('ops_pass_ok'))
        q = queue_entry(s, r['run'])
        rcs = (q or {}).get('rcs') or [(q or {}).get('rc')]
        chks = (q or {}).get('checks') or [(q or {}).get('check')]
        queue_ok = bool(q and q.get('ran') and q.get('rc') == 0 and all(c == 0 for c in rcs) and q.get('check') in OKCHK and all(c in OKCHK for c in chks))
        qsel['queue ok' if queue_ok else 'queue NOT ok'] += 1
        tv = base and block_ok and queue_ok
        m = {'time_ok': tv, 'energy_ok': False, 'capped': bool(x.get('capped')), 'loader_form_ok': bool(base and gl), 'queue_ok': queue_ok,
             'block_ok': block_ok, 'base_ok': base, 'checks': chks, 'no_step': bool(x.get('no_step')), 'run_primary_view': x.get('primary_view')}
        if tv:
            m.update({'T': float(v['T_op_us']), 'cw': float(v['cyc_op_max']), 'cm': (float(v['cyc_op_mean']) if v.get('cyc_op_mean') else None),
                      'tp': (float(v['t_pass_s']) if v.get('t_pass_s') else None), 'f': float(v['kclock_mhz']), 'n_launch': v.get('n_launch'),
                      'thin': bool(v.get('thin'))})
            if v.get('dP_w') is not None and v.get('p_mean_w') and not x.get('capped') and x.get('role') != 'time':
                m.update({'energy_ok': True, 'w': float(v['dP_w']), 'pm': float(v['p_mean_w']), 'rest': float(v['p_mean_w']) - float(v['dP_w'])})
        meas[r['id']] = m

# ------------------------------------------------------------------ the loader check: MM1-v3.1's own reader on the same bytes (gemmL runs)
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import data_v31 as DV  # noqa: E402
D3 = DV.D
lchk = {'runs_loader_listed': 0, 'runs_loader_not_listed': 0, 'gemmL_runs_mine_loader_form_ok': sum(1 for m in meas.values() if m['loader_form_ok']),
        'field_diffs': 0, 'missing': [], 'energy_flag_diffs': 0}
for s in DATA:
    got = DV.mms_runs_all((os.path.join(S3, 'data', f'data-e219-{s}.json'),), 'E219', D3.e212_kind)
    for g in got:
        rid = f"E219|{s}|{g['run']}"
        m = meas.get(rid)
        if m is None:
            lchk['runs_loader_not_listed'] += 1   # a run the declaration does not list (none expected: nulls are skipped by both)
            continue
        lchk['runs_loader_listed'] += 1
        if not m['loader_form_ok']:
            lchk['missing'].append(rid)
            continue
        if not m['time_ok']:   # the loader's form holds but the queue or block condition does not (none expected): no fields to compare
            continue
        for a, b in (('T', 'T'), ('cyc_wall', 'cw'), ('cyc_mean', 'cm'), ('t_gemm', 'tp'), ('f', 'f')):
            lchk['field_diffs'] += (g[a] != m[b])
        if ('w' in g) != m['energy_ok']:
            lchk['energy_flag_diffs'] += 1
        elif 'w' in g:
            lchk['field_diffs'] += (g['w'] != m['w']) + (g['p_rest'] != m['rest'])
lchk['equal'] = (lchk['field_diffs'] == 0 and not lchk['missing'] and lchk['energy_flag_diffs'] == 0 and
                 lchk['runs_loader_listed'] == lchk['gemmL_runs_mine_loader_form_ok'] and lchk['runs_loader_not_listed'] == 0)
lchk['queue_condition'] = dict(qsel)
lchk['runs_time_ok_all'] = sum(1 for m in meas.values() if m['time_ok'])
lchk['runs_energy_ok_all'] = sum(1 for m in meas.values() if m['energy_ok'])

# ------------------------------------------------------------------ the two footings: each run's forecast per model
RUNS = FCJ['runs']
CASES = FCJ['cases']
INR = {k: v for k, v in RUNS.items() if v['domain'] == 'IN'}
INC = {k: v for k, v in CASES.items() if v['domain'] == 'IN'}


def primary_fc(rid, m):
    return RUNS[rid][m]


def nominal_fc(rid, m):
    """decl-e219's frozen nominal forecast of the run's case (every run of a case at the same nominal conditions)"""
    base = FCN[RUNS[rid]['case']][MN[m]]
    o = {k: base[k] for k in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_pass')}
    if base.get('energy') == 'FORECAST':
        o.update({'energy': 'FORECAST', 'W_A': base['W_A'], 'W_B': base['W_B'], 'W_fc': base['W_fc']})
    else:
        o['energy'] = base.get('energy') or 'NOT FORECAST'
    return o


def lnabs(e):
    return abs(math.log(1.0 + e))


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def st(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    n = len(v)
    return {'n': n, 'rms_pct': round(100 * math.sqrt(sum(x * x for x in v) / n), 3), 'bias_pct': round(100 * sum(v) / n, 3)}


def sta(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    n = len(v)
    return {'n': n, 'rms_W': round(math.sqrt(sum(x * x for x in v) / n), 4), 'bias_W': round(sum(v) / n, 4)}


def sign_p(k, n):
    if n == 0:
        return None
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2.0 ** n
    return min(1.0, 2.0 * tail)


def decide(npos, nneg, na, nb, n_cases, too_few=TOO_FEW):
    """the declared test (section d): NO DATA with no case compared; TOO FEW under 10 untied cases (all tied included: the reading that makes
    section d's 'test' line and its D3 line ('with at most 6 cases every D3 test reads TOO FEW') agree); else the exact two-sided sign test"""
    n = npos + nneg
    if n_cases == 0:
        return 'NO DATA', None
    p = sign_p(npos, n) if n else None
    if n < too_few:
        return 'TOO FEW', p
    if p < ALPHA and npos > nneg:
        return f'{na} BETTER', p
    if p < ALPHA and nneg > npos:
        return f'{nb} BETTER', p
    return 'NOT DECIDED', p


QT = ('wall', 'mean', 'sec')
QE = ('E1', 'E2', 'E3', 'E4')
RULEQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}
HQ = {'H1': 'wall', 'H2': 'mean', 'H3': 'sec', 'H4': 'E1', 'H5': 'E2'}


def score_footing(FC):
    """every declared figure on one footing (the in-domain runs and cases); FC(rid, model) gives the run's forecast"""
    rrows = {}
    for rid, fr in INR.items():
        m = meas[rid]
        o = {'id': rid, 'session': fr['session'], 'card': fr['card'], 'fmt': fr['fmt'], 'kind': fr['kind'], 'case': fr['case'], 'class': fr['class'],
             'group_mask': fr['group_mask'], 'token': fr['token'], 'time_ok': m['time_ok'], 'energy_ok': m['energy_ok'], 'capped': m['capped']}
        if m['time_ok']:
            o.update({'meas_T_op_us': m['T'], 'meas_cyc_wall': m['cw'], 'meas_cyc_mean': m['cm'], 'meas_t_pass_s': m['tp'], 'meas_f': m['f'],
                      'f_cond_equal': (fr['f_mhz'] is not None and m['f'] == float(fr['f_mhz']))})
            for mo in MODELS:
                F = FC(rid, mo)
                o[f'{mo}_e_wall'] = F['cyc_wall'] / m['cw'] - 1
                o[f'{mo}_e_mean'] = (F['cyc_mean'] / m['cm'] - 1) if m['cm'] else None
                o[f'{mo}_e_sec'] = (F['sec_pass'] / m['tp'] - 1) if m['tp'] else None
        if m['energy_ok']:
            o.update({'meas_w': m['w'], 'meas_rest': m['rest']})
            for mo in MODELS:
                F = FC(rid, mo)
                if F.get('energy') != 'FORECAST':
                    continue
                Wg = F['W_A'] + F['W_B'] / m['T']
                Wf, Tf = F['W_fc'], F['T_op_us']
                o[f'{mo}_Wg'] = Wg
                o[f'{mo}_e_E1'] = Wg / m['w'] - 1
                o[f'{mo}_d_E1'] = Wg - m['w']
                o[f'{mo}_e_E2'] = (Wf * Tf) / (m['w'] * m['T']) - 1
                o[f'{mo}_d_E2'] = Wf - m['w']
                o[f'{mo}_e_E3'] = (m['rest'] + Wg) / (m['rest'] + m['w']) - 1
                o[f'{mo}_e_E4'] = (m['rest'] + Wf) * Tf / ((m['rest'] + m['w']) * m['T']) - 1
        rrows[rid] = o

    crow = {}
    for cid, c in INC.items():
        rs = [rrows[r] for r in c['runs']]
        tr = [r for r in rs if r['time_ok']]
        er = [r for r in rs if r['energy_ok']]
        o = {'case': cid, 'card': c['card'], 'arm': c['arm'], 'token': c['token'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'],
             'mask': c['mask'], 'class': c['class'], 'group_mask': c['group_mask'], 'kernel': c['kernel'], 'shape': c['shape'], 'n_runs': c['n_runs'],
             'n_time': len(tr), 'n_energy': len(er), 'f_mean_mhz': c['f_mean_mhz'], 'f25': c['f25'],
             'twin_time': {mo: c['twin_time'][TWIN_OF[mo]] for mo in MODELS}, 'twin_energy': {mo: c['twin_energy'][TWIN_OF[mo]] for mo in MODELS},
             'factor_contention': c['factors']['v31c'], 'sessions': c['sessions']}
        if tr:
            o['meas_cyc_wall'] = mean([r['meas_cyc_wall'] for r in tr])
            o['meas_cyc_mean'] = mean([r['meas_cyc_mean'] for r in tr])
            o['meas_T_op_us'] = mean([r['meas_T_op_us'] for r in tr])
            o['meas_t_pass_s'] = mean([r['meas_t_pass_s'] for r in tr])
            for mo in MODELS:
                for q in QT:
                    o[f'{mo}_e_{q}'] = mean([r[f'{mo}_e_{q}'] for r in tr])
        if er:
            o['meas_w'] = mean([r['meas_w'] for r in er])
            o['meas_rest'] = mean([r['meas_rest'] for r in er])
            v31g = mean([r.get('v31_Wg') for r in er]) if all('v31_Wg' in r for r in er) else None
            o['v31_Wg_mean'] = v31g
            o['watts_case'] = (v31g is not None and v31g < LOW) or o['meas_w'] < LOW
            for mo in MODELS:
                if any(f'{mo}_Wg' not in r for r in er):
                    continue
                o[f'{mo}_Wg_mean'] = mean([r[f'{mo}_Wg'] for r in er])
                for q in ('E1', 'E2'):
                    o[f'{mo}_e_{q}'] = mean([r[f'{mo}_e_{q}'] for r in er])
                    o[f'{mo}_d_{q}'] = mean([r[f'{mo}_d_{q}'] for r in er])
                for q in ('E3', 'E4'):
                    o[f'{mo}_e_{q}'] = mean([r[f'{mo}_e_{q}'] for r in er])
        crow[cid] = o
    CL = list(crow.values())

    def twin_of(c, q, mo):
        return c['twin_time'][mo] if q in QT else c['twin_energy'][mo]

    def cell(cs, mo, q, twin_sel, twin_mo=None):
        tm = twin_mo or mo
        sel = [c for c in cs if (twin_sel is None or twin_of(c, q, tm) == twin_sel)]
        if q in ('E1', 'E2'):
            rel = [c.get(f'{mo}_e_{q}') for c in sel if c.get('n_energy') and not c.get('watts_case')]
            wat = [c.get(f'{mo}_d_{q}') for c in sel if c.get('n_energy') and c.get('watts_case')]
            return {'relative': st(rel), 'watts': sta(wat)}
        if q in QE:
            return st([c.get(f'{mo}_e_{q}') for c in sel if c.get('n_energy')])
        return st([c.get(f'{mo}_e_{q}') for c in sel if c.get('n_time')])

    SCOPES = (('pooled', lambda c: True), (C1, lambda c: c['card'] == C1), (C0, lambda c: c['card'] == C0))
    tables = {}
    for mo in MODELS:
        T = {}
        for q in QT + QE:
            T[q] = {}
            for scope, fn in SCOPES:
                cs = [c for c in CL if fn(c)]
                T[q][scope] = {'all': cell(cs, mo, q, None), 'no_twin': cell(cs, mo, q, False), 'twin': cell(cs, mo, q, True)}
        tables[mo] = T
    # the declared splits (each model, no twin and all): per class (CTRL apart), FULL / SUB, per format, per kind
    SPL = {**{k: (lambda c, k=k: c['class'] == k) for k in CLASSES},
           'not CTRL': lambda c: c['class'] != 'CTRL', 'gemmL (CTRL, GAP, ANCHOR)': lambda c: c['class'] in ('CTRL', 'GAP', 'ANCHOR'),
           'c-arms (CTAB, C16R)': lambda c: c['class'] in ('CTAB', 'C16R'),
           'FULL': lambda c: c['group_mask'] == 'FULL', 'SUB': lambda c: c['group_mask'] != 'FULL',
           'fp32': lambda c: c['fmt'] == 'fp32', 'fp16': lambda c: c['fmt'] == 'fp16', 'int8': lambda c: c['fmt'] == 'int8',
           'zeros': lambda c: c['kind'] == 'zeros', 'ones': lambda c: c['kind'] == 'ones', 'random': lambda c: c['kind'] == 'random'}
    splits = {}
    for mo in MODELS:
        Sx = {}
        for nm, fn in SPL.items():
            for scope, sfn in SCOPES:
                cs = [c for c in CL if fn(c) and sfn(c)]
                Sx[f'{nm}|{scope}'] = {q: {'all': cell(cs, mo, q, None), 'no_twin': cell(cs, mo, q, False)} for q in QT + QE}
        splits[mo] = Sx
    bykind = {}
    for mo in ('v31', 'v3', 'v2'):
        B = {}
        for card in CARDS:
            for fmt in ('fp32', 'fp16', 'int8'):
                cs = [c for c in CL if c['card'] == card and c['fmt'] == fmt]
                for k in ['ALL'] + sorted({c['kind'] for c in cs}):
                    cc = cs if k == 'ALL' else [c for c in cs if c['kind'] == k]
                    B[f'{card}|{fmt}|{k}'] = {q: {'all': cell(cc, mo, q, None), 'no_twin': cell(cc, mo, q, False)} for q in ('wall', 'mean', 'E1', 'E3')}
        bykind[mo] = B
    RR = list(rrows.values())
    perrun = {}
    for mo in MODELS:
        P = {}
        for scope, fn in SCOPES:
            rs = [r for r in RR if fn(r)]
            P[scope] = {q: st([r.get(f'{mo}_e_{q}') for r in rs if r['time_ok']]) for q in QT}
            P[scope].update({q: st([r.get(f'{mo}_e_{q}') for r in rs if r['energy_ok'] and r.get('meas_w', 0) >= LOW]) for q in ('E1', 'E2')})
            P[scope].update({q: st([r.get(f'{mo}_e_{q}') for r in rs if r['energy_ok']]) for q in ('E3', 'E4')})
            P[scope]['E1_watts_under_3W'] = sta([r.get(f'{mo}_d_E1') for r in rs if r['energy_ok'] and r.get('meas_w', 99) < LOW])
        perrun[mo] = P
    persession = {}
    for s in sorted({r['session'] for r in RR}):
        rs = [r for r in RR if r['session'] == s]
        persession[s] = {MN[mo]: {'wall': st([r.get(f'{mo}_e_wall') for r in rs if r['time_ok']]),
                                  'E1': st([r.get(f'{mo}_e_E1') for r in rs if r['energy_ok'] and r.get('meas_w', 0) >= LOW]),
                                  'E3': st([r.get(f'{mo}_e_E3') for r in rs if r['energy_ok']])} for mo in ('v31', 'v3', 'v2')}
        persession[s]['runs'] = len(rs)
        persession[s]['time_ok'] = sum(1 for r in rs if r['time_ok'])
        persession[s]['energy_ok'] = sum(1 for r in rs if r['energy_ok'])

    # -------------------------------------------------------------- the pass rule, part A (MM1-v3.1, in-domain no-twin cases, every class)
    def rule_cells(mo, card, rule, cs_all, twin_mo='v31', twin_sel=False):
        q = RULEQ[rule]
        band = BANDS[card][rule]
        bw = BANDS[card]['watts_W']
        cs = [c for c in cs_all if c['card'] == card and (twin_sel is None or twin_of(c, q, twin_mo) == twin_sel)]
        passed, n, miss = 0, 0, []
        for c in cs:
            if q in QT:
                if not c.get('n_time') or c.get(f'{mo}_e_{q}') is None:
                    continue
                ok = abs(c[f'{mo}_e_{q}']) <= band
            else:
                if not c.get('n_energy') or c.get(f'{mo}_e_{q}') is None:
                    continue
                if q in ('E1', 'E2') and c['watts_case']:
                    ok = abs(c[f'{mo}_d_{q}']) <= bw
                else:
                    ok = abs(c[f'{mo}_e_{q}']) <= band
            n += 1
            passed += ok
            if not ok:
                miss.append(c['case'])
        if n == 0:
            v = 'NO DATA'
        elif n < TOO_FEW:
            v = 'TOO FEW'
        else:
            v = 'PASS' if passed >= PASS_FRAC * n else 'FAIL'
        return {'verdict': v, 'pass': passed, 'n': n, 'band': band, 'band_W': bw if q in ('E1', 'E2') else None, 'misses': sorted(miss)}

    # every model's cells over MM1-v3.1's no-twin cases (blind-e217's form); only MM1-v3.1's decide (the others REPORTED)
    partA = {mo: {card: {rule: rule_cells(mo, card, rule, CL) for rule in RULEQ} for card in CARDS} for mo in MODELS}
    fails = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'FAIL']
    passes = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'PASS']
    A_verdict = 'FAIL' if fails else ('PASS' if passes else 'NOT DECIDED')
    beside = {}
    for nm, fn in SPL.items():
        cs = [c for c in CL if fn(c)]
        beside[nm] = {card: {rule: {k: v for k, v in rule_cells('v31', card, rule, cs).items() if k != 'misses'} for rule in RULEQ} for card in CARDS}
    beside['twins (the twin cases only)'] = {card: {rule: {k: v for k, v in rule_cells('v31', card, rule, CL, twin_sel=True).items() if k != 'misses'}
                                                    for rule in RULEQ} for card in CARDS}
    beside['all cases (twins included)'] = {card: {rule: {k: v for k, v in rule_cells('v31', card, rule, CL, twin_sel=None).items() if k != 'misses'}
                                                   for rule in RULEQ} for card in CARDS}
    VERDICT = A_verdict   # part S NOT APPLICABLE: the verdict is part A's (PASS / FAIL / NOT DECIDED)

    # -------------------------------------------------------------- the comparisons (sign tests; each its own verdict)
    def hh(a, b, rule, scope, sel=lambda c: True, neither_twin=False):
        q = HQ[rule]
        cs = [c for c in CL if (scope == 'pooled' or c['card'] == scope) and sel(c)]
        npos = nneg = nt = 0
        dl = []
        for c in cs:
            if neither_twin and (twin_of(c, q, a) or twin_of(c, q, b)):
                continue
            tie = TIES[c['card']]
            if q in QT:
                if not c.get('n_time'):
                    continue
                ea, eb = c.get(f'{a}_e_{q}'), c.get(f'{b}_e_{q}')
                if ea is None or eb is None:
                    continue
                d = lnabs(eb) - lnabs(ea)
                t = tie['seconds_ln'] if q == 'sec' else tie['cycles_ln']
            else:
                if not c.get('n_energy') or c.get(f'{a}_e_{q}') is None or c.get(f'{b}_e_{q}') is None:
                    continue
                if c['watts_case']:
                    d = abs(c[f'{b}_d_{q}']) - abs(c[f'{a}_d_{q}'])
                    t = tie['watts_W']
                else:
                    d = lnabs(c[f'{b}_e_{q}']) - lnabs(c[f'{a}_e_{q}'])
                    t = tie['joules_ln']
            dl.append(d)
            if d > t:
                npos += 1
            elif d < -t:
                nneg += 1
            else:
                nt += 1
        v, p = decide(npos, nneg, MN[a], MN[b], len(dl))
        return {'verdict': v, 'p': p, 'closer_A': npos, 'closer_B': nneg, 'ties': nt, 'n': len(dl), 'mean_d': (sum(dl) / len(dl) if dl else None)}

    SUBM = lambda c: c['group_mask'] != 'FULL'  # noqa: E731
    SC3 = ('pooled', C1, C0)
    D = {}
    for key, (a, b) in (('D1 MM1-v3.1 vs MM1-v3', ('v31', 'v3')), ('D2 MM1-v3.1 vs MM1-v2', ('v31', 'v2'))):
        D[key] = {rule: {scope: hh(a, b, rule, scope) for scope in SC3} for rule in HQ}
        D[key + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, b, rule, scope, neither_twin=True) for scope in SC3} for rule in HQ}
        D[key + ' per class (REPORTED)'] = {k: {rule: {scope: hh(a, b, rule, scope, lambda c, k=k: c['class'] == k) for scope in SC3} for rule in HQ}
                                            for k in CLASSES}
    D3 = {}
    for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
        nm = f'D3 {MN[a]} vs MM1-v3.1 (the subset masks)'
        D3[nm] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM) for scope in SC3} for rule in ('H1', 'H2')}
        D3[nm + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM, True) for scope in SC3} for rule in ('H1', 'H2')}
    D['D3 layout'] = D3
    D['D4 switch'] = 'NOT APPLICABLE: E219 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random)'
    both_equal = all(c.get(f'v31b_e_{q}') == c.get(f'v31c_e_{q}') for c in CL for q in QT + QE)
    contention_equal_v31 = all(c.get(f'v31c_e_{q}') == c.get(f'v31_e_{q}') for c in CL for q in QT + QE)
    return {'VERDICT': VERDICT, 'part_A_verdict': A_verdict, 'part_A_fails': fails, 'part_A_passes': passes,
            'part_S_verdict': 'NOT APPLICABLE (no operand-pattern arm)', 'part_A': partA, 'part_A_beside_REPORTED': beside, 'comparisons': D,
            'tables_per_case': tables, 'splits': splits, 'by_card_format_kind': bykind, 'per_run_REPORTED': perrun,
            'per_session_REPORTED': persession, 'both_equals_contention_every_case': both_equal,
            'contention_equals_v31_every_case': contention_equal_v31,
            'counts': {'runs': len(rrows), 'time_ok': sum(1 for r in RR if r['time_ok']), 'energy_ok': sum(1 for r in RR if r['energy_ok']),
                       'capped': sum(1 for r in RR if r['capped']), 'cases': len(CL), 'cases_with_time': sum(1 for c in CL if c['n_time']),
                       'cases_with_energy': sum(1 for c in CL if c['n_energy']), 'watts_cases': sum(1 for c in CL if c.get('watts_case')),
                       'f_cond_equal_all': all(r.get('f_cond_equal', True) for r in RR),
                       'no_twin_time_cases_v31': sum(1 for c in CL if c['n_time'] and not c['twin_time']['v31']),
                       'no_twin_energy_cases_v31': sum(1 for c in CL if c['n_energy'] and not c['twin_energy']['v31'])},
            '_rrows': rrows, '_crow': crow}


PRIM = score_footing(primary_fc)
NOMI = score_footing(nominal_fc)
watts_diff = sum(1 for k in PRIM['_crow'] if PRIM['_crow'][k].get('watts_case') != NOMI['_crow'][k].get('watts_case'))

# ------------------------------------------------------------------ REPORTED beside (deciding nothing)
CR = PRIM['_crow']
# (1) the R ladder: C16R with gemmc16 (CTAB) as R = 1, per card, format and kind
ladder = {}
for cid, c in CR.items():
    if c['class'] not in ('C16R',) and c['token'] != 'gemmc16':
        continue
    R = 1 if c['token'] == 'gemmc16' else int(re.fullmatch(r'gemmc16r(\d+)', c['token']).group(1))
    k = f"{c['card']}|{c['fmt']}|{c['kind']}"
    row = {'R': R, 'case': cid, 'R_in_a_fit': (R in R_IN_FIT), 'R_never_in_a_fit': (R in R_NEVER), 'n_time': c['n_time'], 'n_energy': c['n_energy'],
           'meas_cyc_wall': c.get('meas_cyc_wall'), 'meas_w': c.get('meas_w'), 'watts_case': c.get('watts_case'),
           'twin_time_v31': c['twin_time']['v31']}
    for mo in ('v31', 'v3', 'v2'):
        for q in ('wall', 'mean', 'E1', 'E3'):
            row[f'{mo}_e_{q}'] = c.get(f'{mo}_e_{q}')
        row[f'{mo}_d_E1'] = c.get(f'{mo}_d_E1')
    ladder.setdefault(k, []).append(row)
for k in ladder:
    ladder[k].sort(key=lambda r: r['R'])
lad_sum = {}
for card in CARDS:
    for grp_nm, sel in (('R in a fit (2, 4, 8, 32)', lambda r: r['R_in_a_fit']), ('R never in a fit (3, 5, 6, 12, 16, 24)', lambda r: r['R_never_in_a_fit']),
                        ('gemmc16 (R = 1)', lambda r: r['R'] == 1)):
        rows = [r for k, v in ladder.items() if k.startswith(card + '|') for r in v if sel(r)]
        lad_sum[f'{card}|{grp_nm}'] = {mo: {'wall': st([r[f'{mo}_e_wall'] for r in rows if r['n_time']]),
                                            'E1': st([r[f'{mo}_e_E1'] for r in rows if r['n_energy'] and not r['watts_case']]),
                                            'E3': st([r[f'{mo}_e_E3'] for r in rows if r['n_energy']])} for mo in ('v31', 'v3', 'v2')}
        lad_sum[f'{card}|{grp_nm}']['cases'] = len(rows)
# (2) the gemmc4s / gemmc8s pair (decl-e219's finding 2: MM1 forecasts the two alike)
pair = {}
for cid, c in CR.items():
    if c['token'] != 'gemmc4s':
        continue
    twin = cid.replace('|gemmc4s|', '|gemmc8s|')
    if twin not in CR:
        continue
    d8 = CR[twin]
    pair[f"{c['card']}|{c['fmt']}|{c['kind']}"] = {
        'gemmc4s_case': cid, 'gemmc8s_case': twin, 'meas_cyc_wall_4s': c.get('meas_cyc_wall'), 'meas_cyc_wall_8s': d8.get('meas_cyc_wall'),
        'meas_ratio_8s_over_4s': (d8['meas_cyc_wall'] / c['meas_cyc_wall'] if c.get('meas_cyc_wall') and d8.get('meas_cyc_wall') else None),
        'v31_fc_cyc_wall_4s': mean([RUNS[r]['v31']['cyc_wall'] for r in INC[cid]['runs']]),
        'v31_fc_cyc_wall_8s': mean([RUNS[r]['v31']['cyc_wall'] for r in INC[twin]['runs']]),
        'meas_w_4s': c.get('meas_w'), 'meas_w_8s': d8.get('meas_w'), 'v31_e_wall_4s': c.get('v31_e_wall'), 'v31_e_wall_8s': d8.get('v31_e_wall')}
# (3) the CTRL cases beside E217's committed means (read now from E217's committed data by MM1-v3.1's loader)
e217 = {'folders': {}, 'cases': {}}
names = git('ls-tree', '--name-only', COMMIT, 'docs/reports/data/', text=True).split()
E217F = {}
for n in names:
    mm = re.fullmatch(r'docs/reports/data/2026-11-19-e217-mmsweep4-(a1c[01]-S\d)', n)
    if mm:
        E217F[mm.group(1)] = n
E217R = []
for s7, fo in sorted(E217F.items()):
    raw = git('show', f'{COMMIT}:{fo}/data-e217-{s7}.json')
    p7 = os.path.join(S3, 'e217', f'data-e217-{s7}.json')
    open(p7, 'wb').write(raw)
    e217['folders'][s7] = {'folder': fo, 'sha256': hashlib.sha256(raw).hexdigest()}
    E217R += DV.mms_runs_all((p7,), 'E217', D3.e212_kind)
for cid, c in CR.items():
    if c['class'] != 'CTRL':
        continue
    rs = [g for g in E217R if g['card'] == c['card'] and g['arm'] == c['arm'] and g['fmt'] == c['fmt'] and g['kind'] == c['kind']
          and str(g['mask']).lower() == str(c['mask']).lower()]
    er = [g for g in rs if 'w' in g]
    e217['cases'][cid] = {'E219_n_time': c['n_time'], 'E219_meas_cyc_wall': c.get('meas_cyc_wall'), 'E219_meas_cyc_mean': c.get('meas_cyc_mean'),
                          'E219_meas_w': c.get('meas_w'), 'E219_f_mean_mhz': c.get('f_mean_mhz'),
                          'E217_n_time': len(rs), 'E217_n_energy': len(er),
                          'E217_meas_cyc_wall': mean([g['cyc_wall'] for g in rs]), 'E217_meas_cyc_mean': mean([g['cyc_mean'] for g in rs]),
                          'E217_meas_w': mean([g['w'] for g in er]), 'E217_f_mean_mhz': mean([g['f'] for g in rs]),
                          'E217_runs': sorted(g['id'] for g in rs)}
    x = e217['cases'][cid]
    for q in ('cyc_wall', 'cyc_mean', 'w'):
        a, b = x[f'E219_meas_{q}'], x[f'E217_meas_{q}']
        x[f'ratio_{q}_E219_over_E217_minus_1'] = (a / b - 1) if (a is not None and b) else None
    # post hoc (REPORTED, not declared): the same arm, format, kind and mask on aifoundry1's OTHER card in E217 (another card and clock)
    other = C0 if c['card'] == C1 else C1
    ro = [g for g in E217R if g['card'] == other and g['arm'] == c['arm'] and g['fmt'] == c['fmt'] and g['kind'] == c['kind']
          and str(g['mask']).lower() == str(c['mask']).lower()]
    eo = [g for g in ro if 'w' in g]
    x['POST_HOC_other_card_E217'] = {'card': other, 'n_time': len(ro), 'n_energy': len(eo), 'meas_cyc_wall': mean([g['cyc_wall'] for g in ro]),
                                     'meas_cyc_mean': mean([g['cyc_mean'] for g in ro]), 'f_mean_mhz': mean([g['f'] for g in ro]),
                                     'meas_w': mean([g['w'] for g in eo]), 'runs': sorted(g['id'] for g in ro)}
    if ro and x['E219_meas_cyc_wall'] is not None:
        x['POST_HOC_other_card_E217']['ratio_cyc_wall_E219_over_E217_minus_1'] = x['E219_meas_cyc_wall'] / x['POST_HOC_other_card_E217']['meas_cyc_wall'] - 1
        if x['E219_meas_cyc_mean'] is not None and x['POST_HOC_other_card_E217']['meas_cyc_mean']:
            x['POST_HOC_other_card_E217']['ratio_cyc_mean_E219_over_E217_minus_1'] = (x['E219_meas_cyc_mean'] /
                                                                                       x['POST_HOC_other_card_E217']['meas_cyc_mean'] - 1)
e217['ran_in_E217'] = sum(1 for v in e217['cases'].values() if v['E217_n_time'])
e217['POST_HOC_ran_in_E217_on_the_other_card'] = sum(1 for v in e217['cases'].values() if v['POST_HOC_other_card_E217']['n_time'])
e217['key'] = 'the same (card, arm, format, kind, mask), E217 read by MM1-v3.1 loader (data_v31.mms_runs_all) from its committed data'
# (4) the OUT-OF-DOMAIN cases: measured values only, by class and case (never in a rule, a comparison or a headline)
ood_cases = {}
for cid, c in CASES.items():
    if c['domain'] == 'IN':
        continue
    ms = [meas[r] for r in c['runs']]
    tr = [m for m in ms if m['time_ok']]
    er = [m for m in ms if m['energy_ok']]
    ood_cases[cid] = {'class': c['class'], 'token': c['token'], 'card': c['card'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'],
                      'shape': c['shape'], 'ops_per_minion_pass': c['ops_per_minion_pass'], 'n_runs': c['n_runs'], 'n_time': len(tr), 'n_energy': len(er),
                      'meas_cyc_wall': mean([m['cw'] for m in tr]), 'meas_cyc_mean': mean([m['cm'] for m in tr]),
                      'meas_t_pass_s': mean([m['tp'] for m in tr]), 'meas_T_op_us': mean([m['T'] for m in tr]), 'meas_f_mhz': mean([m['f'] for m in tr]),
                      'meas_w': mean([m['w'] for m in er]), 'forecast': 'NOT FORECAST (OUT OF DOMAIN)'}
ood_by_class = {}
for k in sorted({v['class'] for v in ood_cases.values()}):
    vs = [v for v in ood_cases.values() if v['class'] == k]
    ood_by_class[k] = {'cases': len(vs), 'runs': sum(v['n_runs'] for v in vs), 'runs_time_ok': sum(v['n_time'] for v in vs),
                       'runs_energy_ok': sum(v['n_energy'] for v in vs),
                       'cyc_wall_range': [min((v['meas_cyc_wall'] for v in vs if v['meas_cyc_wall'] is not None), default=None),
                                          max((v['meas_cyc_wall'] for v in vs if v['meas_cyc_wall'] is not None), default=None)],
                       'w_range': [min((v['meas_w'] for v in vs if v['meas_w'] is not None), default=None),
                                   max((v['meas_w'] for v in vs if v['meas_w'] is not None), default=None)]}

# ------------------------------------------------------------------ the label per session (the declaration, section g)
FPOST = {}
for ln in open(os.path.join(W, 'out', 'orch', 'q232-frozen-posts.txt')):
    mm = re.match(r'#(14\.1\.1) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST', ln)
    if mm:
        FPOST = {'post': '#' + mm.group(1), 'record_time_pst': f'{mm.group(2)} {mm.group(3)}',
                 'epoch_record': datetime.datetime.strptime(f'{mm.group(2)} {mm.group(3)}', '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ).timestamp(),
                 'names_FROZEN_txt': '73a2dd754b70d18a4a7803cd782b1179984d36185c762058d94219ad0fc69f1e' in ln,
                 'names_declaration_md': 'd629bd14aff6fe4d214931fc6bad6b684ab910cd42bb5afdc07b8f8f62330495' in ln,
                 'names_declaration_json': '670caa8c2f29a5d1d95591df0cba3ab80047d0f4b5dc27b8f2568c1da480f479' in ln,
                 'names_nominal_csv': '5433f8c4e88642bad32909a491eb47321a854fad7f2785a188d4ce8d072a3a67' in ln,
                 'names_nominal_json': 'd605db13b6342a283cb5aacb9179c406d529846c3bfc8e152fbf3aef9bd04899' in ln}
assert FPOST and all(FPOST[k] for k in FPOST if k.startswith('names_')), FPOST
SEEN = os.path.join(W, 'out', 'orch', 'discussion-seen-q188.json')
FPOST['own_time_pst'] = None
try:
    for x in json.load(open(SEEN)):
        if isinstance(x, str) and x.startswith('#14|#14.1.1|'):
            t = datetime.datetime.strptime(x.split('|')[2], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
            FPOST['own_epoch'] = t.timestamp()
            FPOST['own_time_pst'] = t.astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
except (OSError, ValueError):
    pass
FPOST['epoch_used'] = max(FPOST['epoch_record'], FPOST.get('own_epoch') or 0)   # the later of the two: a session is BLIND only after both
FPOST['time_used_pst'] = datetime.datetime.fromtimestamp(FPOST['epoch_used'], TZ).strftime('%Y-%m-%d %H:%M:%S')
REL = os.path.join(W, 'out', 'orch', 'e219-releases.txt')
claims, releases = {}, {}
for ln in open(REL).read().splitlines():
    mm = re.match(r'#([\d.]+) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST: (CLAIM|RELEASE)', ln)
    if not mm:
        continue
    t = f'{mm.group(2)} {mm.group(3)}'
    ep = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ).timestamp()
    if mm.group(4) == 'CLAIM':
        k = re.search(r'\((a1c[01]-S\d)', ln)
        if k:
            claims[k.group(1)] = {'post': '#' + mm.group(1), 'time_pst': t, 'epoch': ep}
    else:
        k = re.search(r'sessions/(\d{10})-(a1c[01]-S\d)/', ln)
        if k:
            releases[k.group(2)] = {'post': '#' + mm.group(1), 'time_pst': t, 'session_id': f'{k.group(1)}-{k.group(2)}', 'epoch': ep}
labels = {}
for s, d in sorted(CONDJ['sessions'].items()):
    t0 = d['session_id_epoch']
    t0s = datetime.datetime.fromtimestamp(t0, TZ).strftime('%Y-%m-%d %H:%M:%S') if t0 else None
    tf = QUEUE[s].get('t_first_ms')
    tfs = datetime.datetime.fromtimestamp(tf / 1000.0, TZ).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] if tf else None
    fcc = 'STAND-IN (no README)'
    if STANDIN is None:
        try:
            rd = git('show', f"{COMMIT}:{d['folder']}/README.md", text=True)
            mm = re.search(r'first card command[^0-9]{0,40}(\d{1,2}:\d{2}:\d{2}(?:\.\d+)?)', rd)
            fcc = mm.group(1) if mm else 'NOT FOUND in the README'
        except subprocess.CalledProcessError:
            fcc = 'README NOT READ'
    first = (tf / 1000.0) if tf else t0   # the first card command (the queue's t_first_ms), else the session's T0 (its id)
    cl = claims.get(s)
    if first is not None and first > FPOST['epoch_used'] and (cl is None or cl['epoch'] > FPOST['epoch_used']):
        lab = 'BLIND'
    elif first is not None:
        lab = 'UNREAD (provided no lab lane read its data before the post; else POST-READ)'
    else:
        lab = 'NOT DECIDED (no first datum time)'
    labels[s] = {'label': lab, 'session_T0_pst': t0s, 'first_card_command_pst_queue': tfs, 'first_card_command_pst_README': fcc,
                 'claim': cl, 'release': releases.get(s), 'freeze_post': FPOST['post'], 'freeze_post_time_used_pst': FPOST['time_used_pst'],
                 'margin_minutes_first_datum_after_post': (round((first - FPOST['epoch_used']) / 60.0, 1) if first else None),
                 'release_session_id_equals_data': (releases.get(s, {}).get('session_id') == d['session'])}
ALL_BLIND = all(v['label'] == 'BLIND' for v in labels.values())

# ------------------------------------------------------------------ write
out = {'label': ('BLIND (every session: its first datum after the freeze post)' if ALL_BLIND else 'MIXED: see labels'), 'labels': labels,
       'freeze_post': FPOST, 'e219_releases_sha256_at_read': sha(REL), 'lane': 'blind-e219', 'round': 'Q232', 'started_pst': T_START,
       'read_pst': T_READ, 'python': sys.version.split()[0], 'sources': srcs, 'loader_check': lchk, 'standin': STANDIN,
       'VERDICT': PRIM['VERDICT'], 'part_A_verdict': PRIM['part_A_verdict'], 'part_A_fails': PRIM['part_A_fails'],
       'part_S_verdict': PRIM['part_S_verdict'],
       'primary_footing': {k: v for k, v in PRIM.items() if not k.startswith('_')},
       'nominal_footing_REPORTED': {k: v for k, v in NOMI.items() if not k.startswith('_')},
       'watts_set_differs_between_footings_cases': watts_diff,
       'R_ladder_REPORTED': {'rows': ladder, 'summary': lad_sum, 'R_in_a_fit': R_IN_FIT, 'R_never_in_a_fit': R_NEVER},
       'gemmc4s_gemmc8s_pair_REPORTED': pair,
       'CTRL_tie_to_E217_REPORTED': e217,
       'OUT_OF_DOMAIN_REPORTED': {'by_class': ood_by_class, 'cases': ood_cases,
                                  'note': 'measured values only: no frozen MM1 has a form for these arm tokens; in no rule, comparison or headline'},
       'models': MN, 'twin_flags_of': TWIN_OF, 'bands': BANDS, 'ties': TIES,
       'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E219; not scored',
       'MM1-v3.2': 'NOT DECLARED (NOT_ON_MAIN at the declaration): not scored'}
json.dump(out, open(os.path.join(S3, 'scores-blind-e219.json'), 'w'), indent=1, sort_keys=True)


def fmtv(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float):
        return f'{v:.6g}'
    return '' if v is None else v


ccols = ['case', 'card', 'token', 'fmt', 'kind', 'kind_energy', 'mask', 'class', 'group_mask', 'kernel', 'n_runs', 'n_time', 'n_energy',
         'f_mean_mhz', 'f25', 'meas_cyc_wall', 'meas_cyc_mean', 'meas_T_op_us', 'meas_t_pass_s', 'meas_w', 'meas_rest', 'watts_case', 'factor_contention']
for mo in MODELS:
    ccols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg_mean', f'{mo}_e_E1', f'{mo}_d_E1', f'{mo}_e_E2', f'{mo}_d_E2', f'{mo}_e_E3', f'{mo}_e_E4']
tcols = ['twin_time_v31', 'twin_energy_v31', 'twin_time_v3', 'twin_energy_v3', 'twin_time_v2', 'twin_energy_v2']
ncols = ['nominal_v31_e_wall', 'nominal_v31_e_sec', 'nominal_v31_e_E1', 'nominal_v31_e_E3', 'nominal_v3_e_wall', 'nominal_v3_e_E1', 'nominal_v2_e_wall',
         'nominal_v2_e_E1']
with open(os.path.join(S3, 'scores-blind-e219-cases.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(ccols + tcols + ncols)
    for cid, c in PRIM['_crow'].items():
        nc = NOMI['_crow'][cid]
        row = [fmtv(c.get(k)) for k in ccols]
        row += [int(c['twin_time'][x.rsplit('_', 1)[1]]) if 'time' in x else int(c['twin_energy'][x.rsplit('_', 1)[1]]) for x in tcols]
        row += [fmtv(nc.get(k.replace('nominal_', ''))) for k in ncols]
        w.writerow(row)
rcols = ['id', 'session', 'card', 'fmt', 'kind', 'class', 'group_mask', 'token', 'time_ok', 'energy_ok', 'capped', 'meas_f', 'meas_T_op_us',
         'meas_cyc_wall', 'meas_cyc_mean', 'meas_t_pass_s', 'meas_w', 'meas_rest']
for mo in MODELS:
    rcols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg', f'{mo}_e_E1', f'{mo}_e_E2', f'{mo}_e_E3', f'{mo}_e_E4']
with open(os.path.join(S3, 'scores-blind-e219-runs.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(rcols)
    for r in PRIM['_rrows'].values():
        w.writerow([fmtv(r.get(k)) for k in rcols])
ocols = ['case', 'class', 'token', 'card', 'fmt', 'kind', 'mask', 'ops_per_minion_pass', 'n_runs', 'n_time', 'n_energy', 'meas_f_mhz', 'meas_cyc_wall',
         'meas_cyc_mean', 'meas_T_op_us', 'meas_t_pass_s', 'meas_w', 'forecast']
with open(os.path.join(S3, 'scores-blind-e219-out-of-domain.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(ocols)
    for cid, o in ood_cases.items():
        w.writerow([fmtv(cid if k == 'case' else o.get(k)) for k in ocols])

# a readable summary
P = PRIM
TX = []
A = TX.append
A(f"blind-e219 (Q232): MM1's frozen models scored on E219, as decl-e219 declared. Read {T_READ}; label {out['label']}.")
A(f"Freeze post {FPOST['post']}: record line {FPOST['record_time_pst']} PST, the post's own time {FPOST['own_time_pst']} PST; the later used: {FPOST['time_used_pst']}.")
for s, v in labels.items():
    A(f"  {s}: {v['label']}; claim {(v['claim'] or {}).get('time_pst')}, T0 {v['session_T0_pst']}, first card command {v['first_card_command_pst_queue']} "
      f"(README {v['first_card_command_pst_README']}), {v['margin_minutes_first_datum_after_post']} min after the post; release {(v['release'] or {}).get('time_pst')}")
A(f"Loader check (MM1-v3.1's data_v31.mms_runs_all on the same bytes, gemmL runs): {json.dumps(lchk)[:400]}")
A(f"VERDICT {P['VERDICT']} | part A {P['part_A_verdict']} {P['part_A_fails']} | part S {P['part_S_verdict']}")
A('counts ' + json.dumps(P['counts']))
for card in CARDS:
    A(f"part A {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in P['part_A']['v31'][card].items()))
    for r, x in P['part_A']['v31'][card].items():
        if x['misses']:
            A(f"    {r} misses ({len(x['misses'])}): " + '; '.join(m.replace('aifoundry1 ', '') for m in x['misses']))
for mo in MODELS:
    t = P['tables_per_case'][mo]
    A(f"{MN[mo]} no twin, pooled: wall {t['wall']['pooled']['no_twin']} | mean {t['mean']['pooled']['no_twin']} | sec {t['sec']['pooled']['no_twin']} | "
      f"E1 {t['E1']['pooled']['no_twin']} | E2 {t['E2']['pooled']['no_twin']} | E3 {t['E3']['pooled']['no_twin']} | E4 {t['E4']['pooled']['no_twin']}")
for k in CLASSES:
    A(f"  class {k}: " + ' | '.join(f"{MN[mo]} wall {P['splits'][mo][k + '|pooled']['wall']['no_twin']} E1 {P['splits'][mo][k + '|pooled']['E1']['no_twin']} "
                                    f"E3 {P['splits'][mo][k + '|pooled']['E3']['no_twin']}" for mo in ('v31', 'v3', 'v2')))
for key, x in P['comparisons'].items():
    if key == 'D3 layout':
        for k2, y in x.items():
            A(f"{k2}: " + '; '.join(f"{r} " + ', '.join(f"{sc.replace('aifoundry1 ', '')} {z['verdict']} {z['closer_A']}/{z['closer_B']}/{z['ties']} p={z['p'] if z['p'] is None else round(z['p'], 4)}"
                                                       for sc, z in y[r].items()) for r in y))
    elif key.startswith('D4'):
        A(f"{key}: {x}")
    elif 'per class' in key:
        for k2, y in x.items():
            A(f"{key} {k2}: " + '; '.join(f"{r} pooled {y[r]['pooled']['verdict']} {y[r]['pooled']['closer_A']}/{y[r]['pooled']['closer_B']}/{y[r]['pooled']['ties']}" for r in y))
    else:
        A(f"{key}: " + '; '.join(f"{r} " + ', '.join(f"{sc.replace('aifoundry1 ', '')} {z['verdict']} {z['closer_A']}/{z['closer_B']}/{z['ties']} p={z['p'] if z['p'] is None else round(z['p'], 6)}"
                                                    for sc, z in x[r].items()) for r in x))
N = NOMI
A(f"NOMINAL footing (REPORTED): VERDICT {N['VERDICT']} | part A {N['part_A_verdict']} {N['part_A_fails']}; watts set differs in {watts_diff} cases")
for card in CARDS:
    A(f"  nominal part A {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in N['part_A']['v31'][card].items()))
for mo in ('v31', 'v3', 'v2'):
    t = N['tables_per_case'][mo]
    A(f"  nominal {MN[mo]} no twin, pooled: wall {t['wall']['pooled']['no_twin']} | sec {t['sec']['pooled']['no_twin']} | E1 {t['E1']['pooled']['no_twin']} | "
      f"E3 {t['E3']['pooled']['no_twin']}")
A("R ladder (REPORTED), MM1-v3.1 / v3 / v2 wall rms by group: " + '; '.join(
    f"{k.replace('aifoundry1 ', '')} n{v['cases']} " + '/'.join(str((v[mo]['wall'] or {}).get('rms_pct')) for mo in ('v31', 'v3', 'v2')) for k, v in lad_sum.items()))
A('gemmc4s/gemmc8s pair (REPORTED): ' + json.dumps({k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if not kk.endswith('_case')}
                                                     for k, v in pair.items()}))
A(f"CTRL beside E217 (REPORTED): {e217['ran_in_E217']} of {len(e217['cases'])} CTRL cases ran in E217 (the same card, arm, format, kind, mask): " + json.dumps(
    {k.replace('aifoundry1 ', ''): {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk.startswith('ratio') or kk.endswith('_n_time')}
     for k, v in e217['cases'].items()}))
A(f"  POST HOC: {e217['POST_HOC_ran_in_E217_on_the_other_card']} of {len(e217['cases'])} ran in E217 on aifoundry1's other card: " + json.dumps(
    {k.replace('aifoundry1 ', ''): {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v['POST_HOC_other_card_E217'].items() if kk != 'runs'}
     for k, v in e217['cases'].items() if v['POST_HOC_other_card_E217']['n_time']}))
for k in CLASSES:
    A(f"part A beside, class {k} (REPORTED): " + '; '.join(f"{card.replace('aifoundry1 ', '')} " + ', '.join(
        f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in P['part_A_beside_REPORTED'][k][card].items()) for card in CARDS))
A('OUT OF DOMAIN (REPORTED, measured only): ' + json.dumps(ood_by_class))
A(f"'v3.1+both' equals 'v3.1+contention' on every case and quantity: {P['both_equals_contention_every_case']}; "
  f"'v3.1+contention' equals MM1-v3.1 on every case and quantity: {P['contention_equals_v31_every_case']}")
open(os.path.join(S3, 'scores-blind-e219.txt'), 'w').write('\n'.join(TX) + '\n')
for n in ('scores-blind-e219.json', 'scores-blind-e219.txt', 'scores-blind-e219-cases.csv', 'scores-blind-e219-runs.csv',
          'scores-blind-e219-out-of-domain.csv'):
    print(sha(os.path.join(S3, n)), os.path.relpath(os.path.join(S3, n), L))
print('\n'.join(TX))
