#!/usr/bin/env python3
"""unread-e214 (Q225) step 3: THE READ AND THE SCORE, exactly as DECLARED-unread-e214.json says (hashed 10:42:41 PST) on the forecasts frozen
in forecasts-unread-e214.json (hashed 10:46:42 PST). This script is hashed before it runs. Label: UNREAD (frozen models; not blind).
Reads E214's committed data-e214-<s>.json (GitHub main 8bde0182, `git show`, copied to work/step3/data/ and hashed) - the measurement fields
now - and scores per run and per case: T1 wall, T2 counter mean, T3 seconds, E1 J over idle given t (watts at a watts case), E2 J over idle with
t forecast, E3 J at rest given t, E4 J at rest with t forecast; per card, format and kind, twins apart; the pass rule (parts A and S); the
head-to-heads (H1-H5, three pairs). Checks first that its own run selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all) on
the same bytes. Desk; numpy not needed (stdlib). Run: /usr/bin/python3 -I -B s03_score.py <lane dir>   (a stand-in test: ... <lane dir> --standin <dir>, outputs in work/step3-standin/)
"""
import collections
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time

L = os.path.abspath(sys.argv[1])
STANDIN = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == '--standin' else None   # a stand-in day (the scorer's own test), never E214
LAB = '<LAB>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
S3 = os.path.join(L, 'work', 'step3' if STANDIN is None else 'step3-standin')
os.makedirs(os.path.join(S3, 'data'), exist_ok=True)
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
DECL = json.load(open(os.path.join(L, 'DECLARED-unread-e214.json')))
FCJ = json.load(open(os.path.join(L, 'forecasts-unread-e214.json')))
RL = json.load(open(os.path.join(L, 'work', 'step1', 'runs-listed.json')))
MODELS = ('v31', 'v3', 'v2')
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2'}
C0, C1 = 'aifoundry1 card 0', 'aifoundry1 card 1'
CARDS = (C1, C0)
LOW = 3.0
BANDS = DECL['f_pass_rule']['bands']
TIES = DECL['d_comparisons']['ties']
PASS_FRAC, TOO_FEW, ALPHA = 0.9, 10, 0.05
TIE_S, MIN_S = 0.01, 6


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S %Z', time.localtime())


T_START = ts()
# ------------------------------------------------------------------ the frozen inputs, by their logged sha256
assert sha(os.path.join(L, 'DECLARED-unread-e214.json')) == 'ef311b7186e849928c7b0394415f75426d8d36e6dc6ba0bb5402410eb36bbd88'
assert sha(os.path.join(L, 'DECLARED-unread-e214.md')) == '82288925fc8b44a1cb645fbf751c60a16a86ff482d872ba16642209f9cc75e1d'
assert sha(os.path.join(L, 'forecasts-unread-e214.json')) == '60cd9d208ba4734fca3c5360d8f79b2af4f12c82fcf50b592206ced82bb38ece'
assert sha(os.path.join(L, 'forecasts-unread-e214.csv')) == '0d15bd2beaad7978cf277bcb3f49be38c426267f04213db53b83d89c41470870'

# ------------------------------------------------------------------ the read
DATA = {}
srcs = {}
for s, d in sorted(RL['sessions'].items()):
    path = f"{d['folder']}/data-e214-{s}.json"
    if STANDIN is None:
        raw = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{path}'], check=True, capture_output=True, env=ENV).stdout
    else:
        path = os.path.join(STANDIN, f'data-e214-{s}.json')
        raw = open(path, 'rb').read()
    dst = os.path.join(S3, 'data', f'data-e214-{s}.json')
    open(dst, 'wb').write(raw)
    srcs[s] = {'path': path, 'sha256': hashlib.sha256(raw).hexdigest()}
    DATA[s] = json.loads(raw)
T_READ = ts()

meas = {}
for s, Dj in DATA.items():
    pv = Dj['primary_view']
    byrun = {r['run']: r for r in Dj['runs']}
    for r in [x for x in RL['runs'] if x['session'] == s]:
        x = byrun[r['run']]
        v = (x.get('views') or {}).get(pv) or {}
        tv = bool(x.get('ran') and x.get('role') not in (None, 'null') and x.get('arm') and x.get('shires') and
                  str(x.get('values') or '').startswith('gemmL') and v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1)
        m = {'time_ok': tv, 'energy_ok': False, 'capped': bool(x.get('capped'))}
        if tv:
            m.update({'T': float(v['T_op_us']), 'cw': float(v['cyc_op_max']), 'cm': float(v['cyc_op_mean']), 'tp': float(v['t_pass_s']),
                      'f': float(v['kclock_mhz'])})
            if v.get('dP_w') is not None and v.get('p_mean_w') and not x.get('capped') and x.get('role') != 'time':
                m.update({'energy_ok': True, 'w': float(v['dP_w']), 'pm': float(v['p_mean_w']), 'rest': float(v['p_mean_w']) - float(v['dP_w'])})
        meas[r['id']] = m

# ------------------------------------------------------------------ the loader check: MM1-v3.1's own reader on the same bytes
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import data_v31 as DV  # noqa: E402
D3 = DV.D
lchk = {'runs_loader': 0, 'runs_mine_time_ok': sum(1 for m in meas.values() if m['time_ok']), 'field_diffs': 0, 'missing': [], 'energy_flag_diffs': 0}
for s in DATA:
    got = DV.mms_runs_all((os.path.join(S3, 'data', f'data-e214-{s}.json'),), 'E214', D3.e212_kind)
    lchk['runs_loader'] += len(got)
    for g in got:
        rid = f"E214|{s}|{g['run']}"
        m = meas.get(rid)
        if m is None or not m['time_ok']:
            lchk['missing'].append(rid)
            continue
        for a, b in (('T', 'T'), ('cyc_wall', 'cw'), ('cyc_mean', 'cm'), ('t_gemm', 'tp'), ('f', 'f')):
            lchk['field_diffs'] += (g[a] != m[b])
        if ('w' in g) != m['energy_ok']:
            lchk['energy_flag_diffs'] += 1
        elif 'w' in g:
            lchk['field_diffs'] += (g['w'] != m['w']) + (g['p_rest'] != m['rest'])
lchk['equal'] = (lchk['field_diffs'] == 0 and not lchk['missing'] and lchk['energy_flag_diffs'] == 0 and lchk['runs_loader'] == lchk['runs_mine_time_ok'])

# ------------------------------------------------------------------ per run errors
RUNS = FCJ['runs']
CASES = FCJ['cases']


def lnabs(e):
    return abs(math.log(1.0 + e))


rrows = {}
for rid, fr in RUNS.items():
    m = meas[rid]
    o = {'id': rid, 'card': fr['card'], 'fmt': fr['fmt'], 'kind': fr['kind'], 'case': fr['case'], 'group': fr['group'], 'time_ok': m['time_ok'],
         'energy_ok': m['energy_ok']}
    if m['time_ok']:
        o.update({'meas_T_op_us': m['T'], 'meas_cyc_wall': m['cw'], 'meas_cyc_mean': m['cm'], 'meas_t_pass_s': m['tp'], 'meas_f': m['f'],
                  'f_cond_equal': abs(m['f'] - fr['f_mhz']) == 0.0})
        for mo in MODELS:
            F = fr[mo]
            o[f'{mo}_e_wall'] = F['cyc_wall'] / m['cw'] - 1
            o[f'{mo}_e_mean'] = F['cyc_mean'] / m['cm'] - 1
            o[f'{mo}_e_sec'] = F['sec_gemm'] / m['tp'] - 1
    if m['energy_ok']:
        o.update({'meas_w': m['w'], 'meas_rest': m['rest']})
        for mo in MODELS:
            F = fr[mo]
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
            if 'null_zeros' in F:
                Nk = {k: F[f'null_{k}']['W_A'] + F[f'null_{k}']['W_B'] / m['T'] for k in ('zeros', 'ones', 'random')}
                o[f'{mo}_N_Wg'] = (Nk['zeros'] + Nk['ones'] + Nk['random']) / 3.0
                o[f'{mo}_N2_Wg'] = (Nk['ones'] + Nk['random']) / 2.0
            if 'gate_none_REPORTED' in F:
                o[f'{mo}_gate_none_Wg'] = F['gate_none_REPORTED']['W_A'] + F['gate_none_REPORTED']['W_B'] / m['T']
    rrows[rid] = o


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


# ------------------------------------------------------------------ per case
crow = {}
for cid, c in CASES.items():
    rs = [rrows[r] for r in c['runs']]
    tr = [r for r in rs if r['time_ok']]
    er = [r for r in rs if r['energy_ok']]
    o = {'case': cid, 'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'], 'mask': c['mask'],
         'group': c['group'], 'n_runs': c['n_runs'], 'n_time': len(tr), 'n_energy': len(er), 'f_mean_mhz': c['f_mean_mhz'],
         'twin_time': c['twin_time'], 'twin_energy': c['twin_energy']}
    if tr:
        o['meas_cyc_wall'] = mean([r['meas_cyc_wall'] for r in tr])
        for mo in MODELS:
            for q in ('wall', 'mean', 'sec'):
                o[f'{mo}_e_{q}'] = mean([r[f'{mo}_e_{q}'] for r in tr])
    if er:
        o['meas_w'] = mean([r['meas_w'] for r in er])
        v31g = mean([r.get('v31_Wg') for r in er])
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
            if all(f'{mo}_N_Wg' in r for r in er):
                o[f'{mo}_N_Wg_mean'] = mean([r[f'{mo}_N_Wg'] for r in er])
                o[f'{mo}_N2_Wg_mean'] = mean([r[f'{mo}_N2_Wg'] for r in er])
                o[f'{mo}_N_e_E1'] = mean([r[f'{mo}_N_Wg'] / r['meas_w'] - 1 for r in er])
                o[f'{mo}_N2_e_E1'] = mean([r[f'{mo}_N2_Wg'] / r['meas_w'] - 1 for r in er])
            if all(f'{mo}_gate_none_Wg' in r for r in er):
                o[f'{mo}_gate_none_e_E1'] = mean([r[f'{mo}_gate_none_Wg'] / r['meas_w'] - 1 for r in er])
                o[f'{mo}_gate_none_Wg_mean'] = mean([r[f'{mo}_gate_none_Wg'] for r in er])
    crow[cid] = o


# ------------------------------------------------------------------ statistics
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


QT = ('wall', 'mean', 'sec')
QE = ('E1', 'E2', 'E3', 'E4')


def twin_of(c, q, mo):
    return c['twin_time'][mo] if q in QT else c['twin_energy'][mo]


def cell(cs, mo, q, twin_sel, twin_mo=None):
    """stats of model mo's case errors for quantity q over cases cs; twin_sel None (all), False (no twin), True (twins); twin flags of twin_mo"""
    tm = twin_mo or mo
    sel = [c for c in cs if (twin_sel is None or twin_of(c, q, tm) == twin_sel)]
    if q in ('E1', 'E2'):
        rel = [c.get(f'{mo}_e_{q}') for c in sel if c.get('n_energy') and not c.get('watts_case')]
        wat = [c.get(f'{mo}_d_{q}') for c in sel if c.get('n_energy') and c.get('watts_case')]
        return {'relative': st(rel), 'watts': sta(wat)}
    if q in QE:
        return st([c.get(f'{mo}_e_{q}') for c in sel if c.get('n_energy')])
    return st([c.get(f'{mo}_e_{q}') for c in sel if c.get('n_time')])


CL = list(crow.values())
tables = {}
for mo in MODELS:
    T = {}
    for q in QT + QE:
        T[q] = {}
        for scope, cs in (('pooled', CL), (C1, [c for c in CL if c['card'] == C1]), (C0, [c for c in CL if c['card'] == C0])):
            T[q][scope] = {'all': cell(cs, mo, q, None), 'no_twin': cell(cs, mo, q, False), 'twin': cell(cs, mo, q, True)}
    tables[mo] = T
# by card x format x kind (no twin and all), each model, the headline quantities
bykind = {}
for mo in MODELS:
    B = {}
    for card in CARDS:
        for fmt in ('fp32', 'fp16', 'int8'):
            cs = [c for c in CL if c['card'] == card and c['fmt'] == fmt]
            if not cs:
                continue
            kinds = sorted({c['kind'] for c in cs})
            for k in ['ALL'] + kinds:
                cc = cs if k == 'ALL' else [c for c in cs if c['kind'] == k]
                B[f'{card}|{fmt}|{k}'] = {q: {'all': cell(cc, mo, q, None), 'no_twin': cell(cc, mo, q, False)} for q in ('wall', 'mean', 'E1', 'E3')}
    bykind[mo] = B
# per run (REPORTED)
RR = list(rrows.values())
perrun = {}
for mo in MODELS:
    P = {}
    for scope, rs in (('pooled', RR), (C1, [r for r in RR if r['card'] == C1]), (C0, [r for r in RR if r['card'] == C0])):
        P[scope] = {q: st([r.get(f'{mo}_e_{q}') for r in rs if r['time_ok']]) for q in QT}
        P[scope].update({q: st([r.get(f'{mo}_e_{q}') for r in rs if r['energy_ok'] and r.get('meas_w', 0) >= LOW]) for q in ('E1', 'E2')})
        P[scope].update({q: st([r.get(f'{mo}_e_{q}') for r in rs if r['energy_ok']]) for q in ('E3', 'E4')})
        P[scope]['E1_watts_under_3W'] = sta([r.get(f'{mo}_d_E1') for r in rs if r['energy_ok'] and r.get('meas_w', 99) < LOW])
    perrun[mo] = P


# ------------------------------------------------------------------ the pass rule, part A (MM1-v3.1; v3 and v2 at v3.1's bands REPORTED)
RULEQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}


def rule_cells(mo, card, rule, twin_mo='v31'):
    q = RULEQ[rule]
    band = BANDS[card][rule]
    bw = BANDS[card]['watts_W']
    cs = [c for c in CL if c['card'] == card and not twin_of(c, q, twin_mo)]
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


partA = {mo: {card: {rule: rule_cells(mo, card, rule) for rule in RULEQ} for card in CARDS} for mo in MODELS}
fails = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'FAIL']
passes = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'PASS']
A_verdict = 'FAIL' if fails else ('PASS' if passes else 'NOT DECIDED')


# ------------------------------------------------------------------ sign test
def sign_p(k, n):
    if n == 0:
        return None
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2.0 ** n
    return min(1.0, 2.0 * tail)


def decide(npos, nneg, na, nb, too_few=TOO_FEW):
    n = npos + nneg
    if n == 0:
        return 'NO DATA', None
    p = sign_p(npos, n)
    if n < too_few:
        return 'TOO FEW', p
    if p < ALPHA and npos > nneg:
        return f'{na} BETTER', p
    if p < ALPHA and nneg > npos:
        return f'{nb} BETTER', p
    return 'NOT DECIDED', p


# ------------------------------------------------------------------ part S (the switch test, Q218's P1-P4) for MM1-v3.1 (MM1-v3 REPORTED)
def partS(mo):
    S = [c for c in CL if c['group'] == 'S' and c.get('n_energy') and c.get(f'{mo}_N_e_E1') is not None]
    q1 = [c for c in S if c['meas_w'] >= LOW]
    eV = [c[f'{mo}_e_E1'] for c in q1]
    eN = [c[f'{mo}_N_e_E1'] for c in q1]
    eN2 = [c[f'{mo}_N2_e_E1'] for c in q1]
    d = [abs(n) - abs(v) for v, n in zip(eV, eN)]
    k, nn = sum(1 for x in d if x >= TIE_S), sum(1 for x in d if x <= -TIE_S)
    ties = len(d) - k - nn
    p2 = sign_p(k, k + nn)
    # Q2: the share of D, with the random and zeros cases of the same card, arm, format and mask
    q2 = []
    for c in S:
        base = (c['card'], c['arm'], c['fmt'], c['mask'])
        Rc = [x for x in CL if (x['card'], x['arm'], x['fmt'], x['mask']) == base and x['kind'] == 'random' and x.get('n_energy') and x.get(f'{mo}_Wg_mean') is not None]
        Zc = [x for x in CL if (x['card'], x['arm'], x['fmt'], x['mask']) == base and x['kind'] == 'zeros' and x.get('n_energy')]
        if not Rc or not Zc:
            continue
        WR, WZ = Rc[0]['meas_w'], Zc[0]['meas_w']
        Dd = WR - WZ
        if Dd <= 0:
            continue
        FR = Rc[0][f'{mo}_Wg_mean']
        eD = ((c[f'{mo}_Wg_mean'] - FR) - (c['meas_w'] - WR)) / Dd
        eDN = ((c[f'{mo}_N_Wg_mean'] - FR) - (c['meas_w'] - WR)) / Dd
        eDN2 = ((c[f'{mo}_N2_Wg_mean'] - FR) - (c['meas_w'] - WR)) / Dd
        q2.append({'case': c['case'], 'D_W': Dd, 'e_D': eD, 'e_D_N': eDN, 'e_D_N2': eDN2, 'R': Rc[0]['case'], 'Z': Zc[0]['case']})
    d2 = [abs(x['e_D_N']) - abs(x['e_D']) for x in q2]
    k2, n2 = sum(1 for x in d2 if x >= TIE_S), sum(1 for x in d2 if x <= -TIE_S)
    p4 = sign_p(k2, k2 + n2)

    def rms(v):
        return math.sqrt(sum(x * x for x in v) / len(v)) if v else None
    P1 = (rms(eV) is not None and rms(eV) < rms(eN))
    P2 = (p2 is not None and p2 < ALPHA and k > nn)
    P3 = (bool(q2) and rms([x['e_D'] for x in q2]) < rms([x['e_D_N'] for x in q2]))
    P4 = (p4 is not None and p4 < ALPHA and k2 > n2)
    if (k + nn) < MIN_S or (k2 + n2) < MIN_S:
        v = 'NOT DECIDED'
    else:
        v = 'PASS' if (P1 and P2 and P3 and P4) else 'FAIL'
    failed = [n for n, ok in (('P1', P1), ('P2', P2), ('P3', P3), ('P4', P4)) if not ok]
    return {'verdict': v, 'failed': failed if v == 'FAIL' else [],
            'Q1': {'cases': len(q1), 'model': st(eV), 'N': st(eN), 'N2_REPORTED': st(eN2), 'closer_model': k, 'closer_N': nn, 'ties': ties, 'p': p2},
            'Q2': {'cases': len(q2), 'model_pct_of_D': st([x['e_D'] for x in q2]), 'N_pct_of_D': st([x['e_D_N'] for x in q2]),
                   'N2_pct_of_D_REPORTED': st([x['e_D_N2'] for x in q2]), 'closer_model': k2, 'closer_N': n2, 'ties': len(d2) - k2 - n2, 'p': p4,
                   'rows': q2},
            'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4, 'S_cases_with_energy': len(S),
            'by_format_Q1': {f: st([c[f'{mo}_e_E1'] for c in q1 if c['fmt'] == f]) for f in ('fp32', 'fp16', 'int8')},
            'by_card_Q1': {cd: st([c[f'{mo}_e_E1'] for c in q1 if c['card'] == cd]) for cd in CARDS},
            'under_3W_watts_REPORTED': sta([c[f'{mo}_d_E1'] for c in S if c['meas_w'] < LOW])}


S_res = {mo: partS(mo) for mo in ('v31', 'v3')}
S_verdict = S_res['v31']['verdict']
if A_verdict == 'FAIL' or S_verdict == 'FAIL':
    VERDICT = 'FAIL'
elif A_verdict == 'PASS' and S_verdict == 'PASS':
    VERDICT = 'PASS'
else:
    VERDICT = 'NOT DECIDED'
sp_gate = {c['case']: {'v31_e_E1_arow50_gate': c.get('v31_e_E1'), 'v31_e_E1_literal_no_gate': c.get('v31_gate_none_e_E1'),
                       'v3_e_E1_arow50_gate': c.get('v3_e_E1'), 'v3_e_E1_literal_no_gate': c.get('v3_gate_none_e_E1'), 'meas_w': c.get('meas_w')}
           for c in CL if c['kind'] == 'pattern:sp_ar4'}
groupC = {mo: {'E1': cell([c for c in CL if c['group'] == 'C'], mo, 'E1', None), 'E3': cell([c for c in CL if c['group'] == 'C'], mo, 'E3', None)}
          for mo in ('v31', 'v3')}


# ------------------------------------------------------------------ head to head
HQ = {'H1': 'wall', 'H2': 'mean', 'H3': 'sec', 'H4': 'E1', 'H5': 'E2'}


def hh(a, b, rule, scope, neither_twin=False):
    q = HQ[rule]
    cs = [c for c in CL if (scope == 'pooled' or c['card'] == scope)]
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
    v, p = decide(npos, nneg, MN[a], MN[b])
    return {'verdict': v, 'p': p, 'closer_A': npos, 'closer_B': nneg, 'ties': nt, 'n': len(dl), 'mean_d': (sum(dl) / len(dl) if dl else None)}


H = {}
for a, b in (('v31', 'v3'), ('v31', 'v2'), ('v3', 'v2')):
    key = f'{MN[a]} vs {MN[b]}'
    H[key] = {rule: {scope: hh(a, b, rule, scope) for scope in ('pooled', C1, C0)} for rule in HQ}
    H[key + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, b, rule, scope, True) for scope in ('pooled', C1, C0)} for rule in HQ}

# ------------------------------------------------------------------ write
out = {'label': DECL['label'], 'lane': 'unread-e214', 'round': 'Q225', 'started_pst': T_START, 'read_pst': T_READ, 'python': sys.version.split()[0],
       'sources': srcs, 'loader_check': lchk, 'VERDICT': VERDICT, 'part_A_verdict': A_verdict, 'part_A_fails': fails, 'part_A_passes': passes,
       'part_S_verdict': S_verdict, 'part_A': partA, 'part_S': S_res, 'head_to_head': H, 'tables_per_case': tables, 'by_card_format_kind': bykind,
       'per_run_REPORTED': perrun, 'sp_ar4_gate_REPORTED': sp_gate, 'group_C_REPORTED': groupC,
       'counts': {'runs': len(rrows), 'time_ok': sum(1 for r in RR if r['time_ok']), 'energy_ok': sum(1 for r in RR if r['energy_ok']),
                  'cases': len(CL), 'cases_with_time': sum(1 for c in CL if c['n_time']), 'cases_with_energy': sum(1 for c in CL if c['n_energy']),
                  'watts_cases': sum(1 for c in CL if c.get('watts_case')), 'f_cond_equal_all': all(r.get('f_cond_equal', True) for r in RR)}}
json.dump(out, open(os.path.join(S3, 'scores-unread-e214.json'), 'w'), indent=1, sort_keys=True)
ccols = ['case', 'card', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'group', 'n_runs', 'n_time', 'n_energy', 'f_mean_mhz', 'meas_cyc_wall', 'meas_w',
         'watts_case', 'twin_time_v31', 'twin_energy_v31', 'twin_time_v3', 'twin_energy_v3', 'twin_time_v2', 'twin_energy_v2']
for mo in MODELS:
    ccols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg_mean', f'{mo}_e_E1', f'{mo}_d_E1', f'{mo}_e_E2', f'{mo}_d_E2', f'{mo}_e_E3', f'{mo}_e_E4']
ccols += ['v31_N_e_E1', 'v31_N2_e_E1', 'v3_N_e_E1', 'v31_gate_none_e_E1', 'v3_gate_none_e_E1']


def fmtv(v):
    if isinstance(v, float):
        return f'{v:.6g}'
    if isinstance(v, bool):
        return int(v)
    return '' if v is None else v


with open(os.path.join(S3, 'scores-unread-e214-cases.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(ccols)
    for c in CL:
        row = []
        for k in ccols:
            if k.startswith('twin_'):
                part, mo = k.rsplit('_', 1)
                row.append(int(c['twin_time' if 'time' in part else 'twin_energy'][mo]))
            else:
                row.append(fmtv(c.get(k)))
        w.writerow(row)
rcols = ['id', 'card', 'fmt', 'kind', 'group', 'time_ok', 'energy_ok', 'meas_f', 'meas_T_op_us', 'meas_cyc_wall', 'meas_cyc_mean', 'meas_t_pass_s',
         'meas_w', 'meas_rest']
for mo in MODELS:
    rcols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg', f'{mo}_e_E1', f'{mo}_e_E2', f'{mo}_e_E3', f'{mo}_e_E4']
with open(os.path.join(S3, 'scores-unread-e214-runs.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(rcols)
    for r in RR:
        w.writerow([fmtv(r.get(k)) for k in rcols])
for n in ('scores-unread-e214.json', 'scores-unread-e214-cases.csv', 'scores-unread-e214-runs.csv'):
    print(sha(os.path.join(S3, n)), os.path.relpath(os.path.join(S3, n), L))
print('read', T_READ, 'loader check', json.dumps(lchk)[:300])
print('VERDICT', VERDICT, '| part A', A_verdict, fails, '| part S', S_verdict, S_res['v31']['failed'])
print('counts', json.dumps(out['counts']))
for card in CARDS:
    print(card, {r: f"{x['verdict']} {x['pass']}/{x['n']}" for r, x in partA['v31'][card].items()})
for mo in MODELS:
    t = tables[mo]
    print(MN[mo], 'no twin pooled: wall', t['wall']['pooled']['no_twin'], '| mean', t['mean']['pooled']['no_twin'], '| E1', t['E1']['pooled']['no_twin'],
          '| E2', t['E2']['pooled']['no_twin'], '| E3', t['E3']['pooled']['no_twin'], '| E4', t['E4']['pooled']['no_twin'])
print('S v31', json.dumps({k: S_res['v31'][k] for k in ('verdict', 'P1', 'P2', 'P3', 'P4')}), json.dumps(S_res['v31']['Q1'])[:400])
print('S v31 Q2', json.dumps({k: v for k, v in S_res['v31']['Q2'].items() if k != 'rows'})[:500])
for key in H:
    if 'REPORTED' in key:
        continue
    print(key, {r: f"{x['pooled']['verdict']} {x['pooled']['closer_A']}/{x['pooled']['closer_B']}/{x['pooled']['ties']}" for r, x in H[key].items()})
