#!/usr/bin/env python3
"""blind-e217 (Q228) step 3: THE READ AND THE SCORE, exactly as decl-e217's DECLARED-blind-e217.json says (sections a-g; hashed 11:35:59
PST, FROZEN.txt 11:37:53, posted #13.1.1) on the measured-conditions forecasts frozen in forecasts-blind-e217.json (hashed 21:00:04 PST,
logs/step2-sha256.txt) and, beside it (REPORTED, deciding nothing), the NOMINAL footing frozen by decl-e217 (forecasts-nominal-e217.json and
forecasts-nominal-e217-counts.json). This script is hashed before its first read of any E217 measurement.
Reads E217's committed data-e217-<s>.json (GitHub main, `git show` of work/lab-commit.txt's commit; copied to work/step3/data/ and hashed):
the measurement fields now. Scores per run and per case: T1 wall cycles, T2 counter mean, T3 seconds, E1 J over idle given t (watts at a
watts case), E2 J over idle with t forecast, E3 J at rest given t, E4 J at rest with t forecast; per card and pooled; twins apart (no-twin
cases carry the pass rule and the headline); splits X1 / MG / SUB / FULL, S / C / K, format and kind; the pass rule (part A: MM1-v3.1 on the
primary footing by E215's rule form per card over the no-twin cases; part S: Q218's P1-P4 on group S pooled); the comparisons D1 (MM1-v3.1
vs MM1-v3), D2 (MM1-v3.1 vs MM1-v2), D3 (the layout term and verify-lay's controls vs MM1-v3.1 on the subset masks), D4 (the switch route vs
the null); the label per session (BLIND / UNREAD / POST-READ by the freeze post's time and the session's first datum). Checks first that its
own run selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all) on the same bytes. Desk; stdlib (the loader imports numpy).
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
import time
import zoneinfo

L = os.path.abspath(sys.argv[1])
STANDIN = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--standin' else None   # a stand-in day, never E217
LAB = '<LAB>'
W = '<W>'
COMMIT = open(os.path.join(L, 'work', 'lab-commit.txt')).read().strip()
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='<GITHUB_SSH_PREFIX>')
S3 = os.path.join(L, 'work', 'step3' if STANDIN is None else 'step3-standin-' + os.path.basename(STANDIN))
os.makedirs(os.path.join(S3, 'data'), exist_ok=True)
MM1 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1')
DEC = os.path.join(L, 'work', 'decl')
TZ = zoneinfo.ZoneInfo('America/Los_Angeles')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return datetime.datetime.now(TZ).strftime('%a %d %b %Y %H:%M:%S %Z')


T_START = ts()
# ------------------------------------------------------------------ the frozen inputs, by their logged sha256
PINS = {os.path.join(DEC, 'DECLARED-blind-e217.json'): '633d725620d06295a144312956579fabc54462f109ea3a29e8026d992bdd4eb7',
        os.path.join(DEC, 'DECLARED-blind-e217.md'): '099806dc1a5cb6c53ed7ea0645d5e2b3ae55e0d7734872a467019222da324405',
        os.path.join(DEC, 'FROZEN.txt'): '32311daf2e0ace10d4efdce2be7a3248fb82b2ab852c0acc45fa6c6f37bd42a8',
        os.path.join(DEC, 'COUNTS-FROZEN.txt'): '4867c1d0be500da2f2d2a7a8fd757a1b893b92d802616b2195f10a34bcc89e01',
        os.path.join(DEC, 'forecasts-nominal-e217.json'): '611ca08d27c81f0972e5d2b1f23ac24d0455a602cfe87a665963d83af1fdc97c',
        os.path.join(DEC, 'forecasts-nominal-e217-counts.json'): '590c0be2ebb30bd07fd89b6d22bd182eb5415134807ca8afde06d67952065353',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '25154e5dedd47519a145c693273e3ac3f3cbcabc4e82581a30ebaef34d0d4bc1',
        os.path.join(L, 'forecasts-blind-e217.json'): '74aa5a0314cc5d30f2b0b1e884e8114affe9dd8d24a064bccd5a2191cd4c3581',
        os.path.join(L, 'forecasts-blind-e217.csv'): 'ed81a5dbfe3c18a4e744302cd98f59da5853825270cfbd5e9431537aba1e2ed1',
        os.path.join(L, 'work', 'step2', 'conditions-e217.json'): 'ae9af0e5b64e8b0b1141d2bdcfe166c08af0ffd1c734041b7e5d60cceee1292b'}
for p, h in PINS.items():
    assert sha(p) == h, p
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e217.json')))
FCJ = json.load(open(os.path.join(L, 'forecasts-blind-e217.json')))
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e217.json')))['cases']
FCC = json.load(open(os.path.join(DEC, 'forecasts-nominal-e217-counts.json')))
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
CONDJ = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e217.json')))
MODELS = ('v31', 'v3', 'v2', 'v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b')
MN = {'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'v3.1+contention', 'v31b': 'v3.1+both', 'cn12': 'ctrl N1+N2', 'cg1': 'ctrl G1',
      'cg1n1': 'ctrl G1+N1', 'cf1b': 'ctrl F1-layout-blind'}
TWIN_OF = {'v31': 'v31', 'v3': 'v3', 'v2': 'v2', 'v31c': 'v31', 'v31b': 'v31', 'cn12': 'v31', 'cg1': 'v31', 'cg1n1': 'v31', 'cf1b': 'v31'}
C0, C1 = 'aifoundry1 card 0', 'aifoundry1 card 1'
CARDS = (C1, C0)
LOW = 3.0
BANDS = DECL['f_pass_rule']['bands']
TIES = DECL['d_comparisons']['ties']
PASS_FRAC, TOO_FEW, ALPHA = 0.9, 10, 0.05
TIE_S, MIN_S = 0.01, 6
NULLK = ('zeros', 'ones', 'random')
SHAPE = re.compile(r'gemmL(\d+)x(\d+)x(\d+):')

# ------------------------------------------------------------------ the read
DATA = {}
srcs = {}
for s, d in sorted(CONDJ['sessions'].items()):
    path = d['file']
    if STANDIN is None:
        raw = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{path}'], check=True, capture_output=True, env=ENV).stdout
    else:
        path = os.path.join(STANDIN, f'data-e217-{s}.json')
        raw = open(path, 'rb').read()
    dst = os.path.join(S3, 'data', f'data-e217-{s}.json')
    open(dst, 'wb').write(raw)
    h = hashlib.sha256(raw).hexdigest()
    srcs[s] = {'path': path, 'sha256': h, 'equal_to_step2a_conditions_read': h == d['sha256']}
    if STANDIN is None:
        assert h == d['sha256'], (s, 'the committed file differs from the one step 2a read')
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
                  SHAPE.match(str(x.get('values') or '')) and v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1)
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
lchk = {'runs_loader_listed': 0, 'runs_loader_not_listed': 0, 'runs_mine_time_ok': sum(1 for m in meas.values() if m['time_ok']), 'field_diffs': 0,
        'missing': [], 'energy_flag_diffs': 0}
for s in DATA:
    got = DV.mms_runs_all((os.path.join(S3, 'data', f'data-e217-{s}.json'),), 'E217', D3.e212_kind)
    for g in got:
        rid = f"E217|{s}|{g['run']}"
        m = meas.get(rid)
        if m is None:
            lchk['runs_loader_not_listed'] += 1   # a run the declaration does not list (none expected: nulls are skipped by both)
            continue
        lchk['runs_loader_listed'] += 1
        if not m['time_ok']:
            lchk['missing'].append(rid)
            continue
        for a, b in (('T', 'T'), ('cyc_wall', 'cw'), ('cyc_mean', 'cm'), ('t_gemm', 'tp'), ('f', 'f')):
            lchk['field_diffs'] += (g[a] != m[b])
        if ('w' in g) != m['energy_ok']:
            lchk['energy_flag_diffs'] += 1
        elif 'w' in g:
            lchk['field_diffs'] += (g['w'] != m['w']) + (g['p_rest'] != m['rest'])
lchk['equal'] = (lchk['field_diffs'] == 0 and not lchk['missing'] and lchk['energy_flag_diffs'] == 0 and
                 lchk['runs_loader_listed'] == lchk['runs_mine_time_ok'] and lchk['runs_loader_not_listed'] == 0)

# ------------------------------------------------------------------ the two footings: each run's forecast per model
RUNS = FCJ['runs']
CASES = FCJ['cases']
FCCc = FCC['cases']


def primary_fc(rid, m):
    return RUNS[rid][m]


def nominal_fc(rid, m):
    """decl-e217's frozen nominal forecast of the run's case (every run of a case at the same nominal conditions); group S's energy from
    forecasts-nominal-e217-counts.json; group S's null kinds from forecasts-nominal-e217.json's null_kinds"""
    r = RUNS[rid]
    c = r['case']
    base = FCN[c][MN[m]]
    o = {k: base[k] for k in ('T_op_us', 'cyc_wall', 'cyc_mean', 'sec_gemm')}
    src = base
    if r['group_kind'] == 'S':
        src = FCCc[c].get(MN[m], {'energy': 'NOT FORECAST'})
        if src.get('energy') == 'FORECAST':
            assert src['T_op_us'] == base['T_op_us'], (c, m)
    if src.get('energy') == 'FORECAST':
        o.update({'energy': 'FORECAST', 'W_A': src['W_A'], 'W_B': src['W_B'], 'W_fc': src['W_fc']})
    else:
        o['energy'] = src.get('energy') or 'NOT FORECAST'
    if r['group_kind'] == 'S' and m in ('v31', 'v3'):
        for k in NULLK:
            o[f'null_{k}'] = FCN[c]['null_kinds'][f'{MN[m]}|{k}']
        if f'{MN[m]} literal gate (REPORTED)' in FCCc[c]:
            o['gate_literal_REPORTED'] = FCCc[c][f'{MN[m]} literal gate (REPORTED)']
            o['gate_count_REPORTED'] = FCCc[c][f'{MN[m]} count gate (REPORTED)']
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


QT = ('wall', 'mean', 'sec')
QE = ('E1', 'E2', 'E3', 'E4')
RULEQ = {'T1': 'wall', 'T2': 'mean', 'T3': 'sec', 'E1': 'E1', 'E2': 'E2', 'E3': 'E3', 'E4': 'E4'}
HQ = {'H1': 'wall', 'H2': 'mean', 'H3': 'sec', 'H4': 'E1', 'H5': 'E2'}


def score_footing(FC):
    """every declared figure on one footing; FC(rid, model) gives the run's forecast"""
    rrows = {}
    for rid, fr in RUNS.items():
        m = meas[rid]
        o = {'id': rid, 'session': fr['session'], 'card': fr['card'], 'fmt': fr['fmt'], 'kind': fr['kind'], 'case': fr['case'],
             'group_kind': fr['group_kind'], 'group_mask': fr['group_mask'], 'group_shape': fr['group_shape'], 'time_ok': m['time_ok'],
             'energy_ok': m['energy_ok'], 'capped': m['capped']}
        if m['time_ok']:
            o.update({'meas_T_op_us': m['T'], 'meas_cyc_wall': m['cw'], 'meas_cyc_mean': m['cm'], 'meas_t_pass_s': m['tp'], 'meas_f': m['f'],
                      'f_cond_equal': (fr['f_mhz'] is not None and m['f'] == float(fr['f_mhz']))})
            for mo in MODELS:
                F = FC(rid, mo)
                o[f'{mo}_e_wall'] = F['cyc_wall'] / m['cw'] - 1
                o[f'{mo}_e_mean'] = F['cyc_mean'] / m['cm'] - 1
                o[f'{mo}_e_sec'] = F['sec_gemm'] / m['tp'] - 1
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
                if 'null_zeros' in F:
                    Nk = {k: F[f'null_{k}']['W_A'] + F[f'null_{k}']['W_B'] / m['T'] for k in NULLK}
                    o[f'{mo}_N_Wg'] = (Nk['zeros'] + Nk['ones'] + Nk['random']) / 3.0
                    o[f'{mo}_N2_Wg'] = (Nk['ones'] + Nk['random']) / 2.0
                for tag in ('gate_literal_REPORTED', 'gate_count_REPORTED'):
                    if tag in F:
                        o[f'{mo}_{tag}_Wg'] = F[tag]['W_A'] + F[tag]['W_B'] / m['T']
        rrows[rid] = o

    crow = {}
    for cid, c in CASES.items():
        rs = [rrows[r] for r in c['runs']]
        tr = [r for r in rs if r['time_ok']]
        er = [r for r in rs if r['energy_ok']]
        o = {'case': cid, 'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'], 'mask': c['mask'],
             'group_kind': c['group_kind'], 'group_mask': c['group_mask'], 'group_shape': c['group_shape'], 'n_runs': c['n_runs'],
             'n_time': len(tr), 'n_energy': len(er), 'f_mean_mhz': c['f_mean_mhz'], 'f25': c['f25'],
             'twin_time': {mo: c['twin_time'][TWIN_OF[mo]] for mo in MODELS}, 'twin_energy': {mo: c['twin_energy'][TWIN_OF[mo]] for mo in MODELS},
             'factor_contention': c['factors']['v31c'], 'sessions': c['sessions']}
        if tr:
            o['meas_cyc_wall'] = mean([r['meas_cyc_wall'] for r in tr])
            o['meas_T_op_us'] = mean([r['meas_T_op_us'] for r in tr])
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
                if all(f'{mo}_N_Wg' in r for r in er):
                    o[f'{mo}_N_Wg_mean'] = mean([r[f'{mo}_N_Wg'] for r in er])
                    o[f'{mo}_N2_Wg_mean'] = mean([r[f'{mo}_N2_Wg'] for r in er])
                    o[f'{mo}_N_e_E1'] = mean([r[f'{mo}_N_Wg'] / r['meas_w'] - 1 for r in er])
                    o[f'{mo}_N2_e_E1'] = mean([r[f'{mo}_N2_Wg'] / r['meas_w'] - 1 for r in er])
                for tag in ('gate_literal_REPORTED', 'gate_count_REPORTED'):
                    if all(f'{mo}_{tag}_Wg' in r for r in er):
                        o[f'{mo}_{tag}_e_E1'] = mean([r[f'{mo}_{tag}_Wg'] / r['meas_w'] - 1 for r in er])
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
    # the declared splits (each model, no twin and all): X1 / not X1, MG / SUB / FULL, S / C / K, per format, per card x format x kind
    SPL = {'X1': lambda c: c['group_shape'] == 'X1', 'notX1': lambda c: c['group_shape'] != 'X1', 'MG': lambda c: c['group_mask'] == 'MG',
           'SUB': lambda c: c['group_mask'] == 'SUB', 'FULL': lambda c: c['group_mask'] == 'FULL', 'S': lambda c: c['group_kind'] == 'S',
           'C': lambda c: c['group_kind'] == 'C', 'K': lambda c: c['group_kind'] == 'K', 'fp32': lambda c: c['fmt'] == 'fp32',
           'fp16': lambda c: c['fmt'] == 'fp16', 'int8': lambda c: c['fmt'] == 'int8'}
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

    # -------------------------------------------------------------- the pass rule, part A
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

    # -------------------------------------------------------------- part S (Q218's P1-P4), MM1-v3.1 + counts-e217 vs N; MM1-v3 REPORTED
    def partS(mo):
        S = [c for c in CL if c['group_kind'] == 'S' and c.get('n_energy') and c.get(f'{mo}_N_e_E1') is not None and c.get(f'{mo}_e_E1') is not None]
        q1 = [c for c in S if c['meas_w'] >= LOW]
        eV = [c[f'{mo}_e_E1'] for c in q1]
        eN = [c[f'{mo}_N_e_E1'] for c in q1]
        eN2 = [c[f'{mo}_N2_e_E1'] for c in q1]
        d = [abs(n) - abs(v) for v, n in zip(eV, eN)]
        k, nn = sum(1 for x in d if x >= TIE_S), sum(1 for x in d if x <= -TIE_S)
        p2 = sign_p(k, k + nn)
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
        counts_frozen_before_read = os.path.exists(os.path.join(DEC, 'COUNTS-FROZEN.txt'))
        if (k + nn) < MIN_S or (k2 + n2) < MIN_S or not counts_frozen_before_read:
            v = 'NOT DECIDED'
        else:
            v = 'PASS' if (P1 and P2 and P3 and P4) else 'FAIL'
        failed = [n for n, ok in (('P1', P1), ('P2', P2), ('P3', P3), ('P4', P4)) if not ok]
        return {'verdict': v, 'failed': failed if v == 'FAIL' else [], 'counts_frozen_before_read': counts_frozen_before_read,
                'Q1': {'cases': len(q1), 'model': st(eV), 'N': st(eN), 'N2_REPORTED': st(eN2), 'closer_model': k, 'closer_N': nn,
                       'ties': len(d) - k - nn, 'p': p2, 'rows': [{'case': c['case'], 'e_model': c[f'{mo}_e_E1'], 'e_N': c[f'{mo}_N_e_E1'],
                                                                   'meas_w': c['meas_w']} for c in q1]},
                'Q2': {'cases': len(q2), 'model_pct_of_D': st([x['e_D'] for x in q2]), 'N_pct_of_D': st([x['e_D_N'] for x in q2]),
                       'N2_pct_of_D_REPORTED': st([x['e_D_N2'] for x in q2]), 'closer_model': k2, 'closer_N': n2, 'ties': len(d2) - k2 - n2,
                       'p': p4, 'rows': q2},
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
    zero_row = {c['case']: {'meas_w': c.get('meas_w'), **{f'{mo}_{g}': c.get(k) for mo in ('v31', 'v3')
                                                           for g, k in (('e_E1_declared_gate', f'{mo}_e_E1'),
                                                                        ('e_E1_literal_gate', f'{mo}_gate_literal_REPORTED_e_E1'),
                                                                        ('e_E1_count_gate', f'{mo}_gate_count_REPORTED_e_E1'))}}
                for c in CL if c.get(f'v31_gate_literal_REPORTED_e_E1') is not None}
    groupC = {mo: {'E1': cell([c for c in CL if c['group_kind'] == 'C'], mo, 'E1', None),
                   'E3': cell([c for c in CL if c['group_kind'] == 'C'], mo, 'E3', None),
                   'wall': cell([c for c in CL if c['group_kind'] == 'C'], mo, 'wall', None)} for mo in ('v31', 'v3')}

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
        v, p = decide(npos, nneg, MN[a], MN[b])
        return {'verdict': v, 'p': p, 'closer_A': npos, 'closer_B': nneg, 'ties': nt, 'n': len(dl), 'mean_d': (sum(dl) / len(dl) if dl else None)}

    SUBM = lambda c: c['group_mask'] in ('MG', 'SUB')  # noqa: E731
    MGO = lambda c: c['group_mask'] == 'MG'  # noqa: E731
    SC3 = ('pooled', C1, C0)
    D = {}
    for key, (a, b) in (('D1 MM1-v3.1 vs MM1-v3', ('v31', 'v3')), ('D2 MM1-v3.1 vs MM1-v2', ('v31', 'v2'))):
        D[key] = {rule: {scope: hh(a, b, rule, scope) for scope in SC3} for rule in HQ}
        D[key + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, b, rule, scope, neither_twin=True) for scope in SC3} for rule in HQ}
    D3 = {}
    for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
        nm = f'D3 {MN[a]} vs MM1-v3.1 (MG and SUB)'
        D3[nm] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM) for scope in SC3} for rule in ('H1', 'H2')}
        D3[nm + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM, True) for scope in SC3} for rule in ('H1', 'H2')}
        D3[nm.replace('(MG and SUB)', '(MG alone, REPORTED)')] = {rule: {scope: hh(a, 'v31', rule, scope, MGO) for scope in SC3} for rule in ('H1', 'H2')}
        D3[nm.replace('(MG and SUB)', '(MG and SUB) H5 J over idle with t forecast, REPORTED')] = {'H5': {scope: hh(a, 'v31', 'H5', scope, SUBM) for scope in SC3}}
    for b in ('cn12', 'cg1', 'cg1n1', 'cf1b'):
        nm = f'D3 v3.1+contention vs {MN[b]} (MG and SUB, REPORTED)'
        D3[nm] = {rule: {scope: hh('v31c', b, rule, scope, SUBM) for scope in SC3} for rule in ('H1', 'H2')}
    D['D3 layout'] = D3
    D['D4 switch (part S P2 and P4)'] = {'P2': S_res['v31']['P2'], 'P4': S_res['v31']['P4'],
                                         'Q1 sign test (P2)': {k: S_res['v31']['Q1'][k] for k in ('closer_model', 'closer_N', 'ties', 'p')},
                                         'Q2 sign test (P4)': {k: S_res['v31']['Q2'][k] for k in ('closer_model', 'closer_N', 'ties', 'p')},
                                         'Q1 verdict': decide(S_res['v31']['Q1']['closer_model'], S_res['v31']['Q1']['closer_N'], 'MM1-v3.1 + counts-e217', 'the null N', MIN_S)[0],
                                         'Q2 verdict': decide(S_res['v31']['Q2']['closer_model'], S_res['v31']['Q2']['closer_N'], 'MM1-v3.1 + counts-e217', 'the null N', MIN_S)[0]}
    both_equal = all(c.get(f'v31b_e_{q}') == c.get(f'v31c_e_{q}') for c in CL for q in QT + QE)
    return {'VERDICT': VERDICT, 'part_A_verdict': A_verdict, 'part_A_fails': fails, 'part_A_passes': passes, 'part_S_verdict': S_verdict,
            'part_A': partA, 'part_A_beside_REPORTED': beside, 'part_S': S_res, 'comparisons': D, 'tables_per_case': tables, 'splits': splits,
            'by_card_format_kind': bykind, 'per_run_REPORTED': perrun, 'per_session_REPORTED': persession, 'zero_row_gates_REPORTED': zero_row,
            'group_C_REPORTED': groupC, 'both_equals_contention_every_case': both_equal,
            'counts': {'runs': len(rrows), 'time_ok': sum(1 for r in RR if r['time_ok']), 'energy_ok': sum(1 for r in RR if r['energy_ok']),
                       'capped': sum(1 for r in RR if r['capped']), 'cases': len(CL), 'cases_with_time': sum(1 for c in CL if c['n_time']),
                       'cases_with_energy': sum(1 for c in CL if c['n_energy']), 'watts_cases': sum(1 for c in CL if c.get('watts_case')),
                       'f_cond_equal_all': all(r.get('f_cond_equal', True) for r in RR)},
            '_rrows': rrows, '_crow': crow}


PRIM = score_footing(primary_fc)
NOMI = score_footing(nominal_fc)
watts_diff = sum(1 for k in PRIM['_crow'] if PRIM['_crow'][k].get('watts_case') != NOMI['_crow'][k].get('watts_case'))

# ------------------------------------------------------------------ the label per session (the declaration, section g)
FPOST = {}
for ln in open(os.path.join(W, 'out', 'orch', 'q228-frozen-posts.txt')):
    m = re.match(r'#(13\.1\.1) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST', ln)
    if m:
        FPOST = {'post': '#' + m.group(1), 'record_time_pst': f'{m.group(2)} {m.group(3)}',
                 'epoch': datetime.datetime.strptime(f'{m.group(2)} {m.group(3)}', '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ).timestamp(),
                 'names_FROZEN_txt': '32311daf2e0ace10d4efdce2be7a3248fb82b2ab852c0acc45fa6c6f37bd42a8' in ln,
                 'names_COUNTS_FROZEN_txt': '4867c1d0be500da2f2d2a7a8fd757a1b893b92d802616b2195f10a34bcc89e01' in ln}
assert FPOST and FPOST['names_FROZEN_txt'] and FPOST['names_COUNTS_FROZEN_txt'], FPOST
FPOST['context_time_pst'] = '2026-11-19 12:25:56 (CONTEXT 129 and the READMEs; the exact second is NOT CHECKED: verify-e217d finding 5)'
REL = os.path.join(W, 'out', 'orch', 'e217-releases.txt')
rel_lines = open(REL).read().splitlines()
claims, releases = {}, {}
for ln in rel_lines:
    m = re.match(r'#([\d.]+) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST: (CLAIM|RELEASE)', ln)
    if not m:
        continue
    t = f'{m.group(2)} {m.group(3)}'
    if m.group(4) == 'CLAIM':
        k = re.search(r'\((?:schedule )?(a1c[01]-S\d)', ln)
        if k:
            claims[k.group(1)] = {'post': '#' + m.group(1), 'time_pst': t}
    else:
        k = re.search(r'sessions/(\d{10})-(a1c[01]-S\d)/', ln)
        if k:
            releases[k.group(2)] = {'post': '#' + m.group(1), 'time_pst': t, 'session_id': f'{k.group(1)}-{k.group(2)}'}
labels = {}
for s, d in sorted(CONDJ['sessions'].items()):
    t0 = d['session_id_epoch']
    t0s = datetime.datetime.fromtimestamp(t0, TZ).strftime('%Y-%m-%d %H:%M:%S') if t0 else None
    fcc = None
    if STANDIN is None:
        try:
            rd = subprocess.run(['git', '-C', LAB, 'show', f"{COMMIT}:{d['folder']}/README.md"], check=True, capture_output=True, text=True, env=ENV).stdout
            mm = re.search(r'first card command[^0-9]{0,40}(\d{1,2}:\d{2}:\d{2}(?:\.\d+)?)', rd)
            fcc = mm.group(1) if mm else 'NOT FOUND in the README'
        except subprocess.CalledProcessError:
            fcc = 'README NOT READ'
    first = t0   # the session's T0 (its id) precedes or equals its first card command
    lab = 'BLIND' if (first is not None and first > FPOST['epoch']) else 'UNREAD (or POST-READ): see the rule'
    labels[s] = {'label': lab, 'counts_route_label': lab, 'session_T0_pst': t0s, 'first_card_command_pst_README': fcc,
                 'claim': claims.get(s), 'release': releases.get(s), 'freeze_post': FPOST['post'], 'freeze_post_time_pst': FPOST['record_time_pst'],
                 'margin_minutes_T0_after_post': (round((first - FPOST['epoch']) / 60.0, 1) if first else None),
                 'release_session_id_equals_data': (releases.get(s, {}).get('session_id') == d['session'])}
ALL_BLIND = all(v['label'] == 'BLIND' for v in labels.values())

# ------------------------------------------------------------------ write
out = {'label': ('BLIND (every session: its first datum after the freeze post)' if ALL_BLIND else 'MIXED: see labels'), 'labels': labels,
       'freeze_post': FPOST, 'e217_releases_sha256_at_read': sha(REL), 'lane': 'blind-e217', 'round': 'Q228', 'started_pst': T_START,
       'read_pst': T_READ, 'python': sys.version.split()[0], 'sources': srcs, 'loader_check': lchk, 'standin': STANDIN,
       'VERDICT': PRIM['VERDICT'], 'part_A_verdict': PRIM['part_A_verdict'], 'part_A_fails': PRIM['part_A_fails'], 'part_S_verdict': PRIM['part_S_verdict'],
       'primary_footing': {k: v for k, v in PRIM.items() if not k.startswith('_')},
       'nominal_footing_REPORTED': {k: v for k, v in NOMI.items() if not k.startswith('_')},
       'watts_set_differs_between_footings_cases': watts_diff,
       'models': MN, 'twin_flags_of': TWIN_OF, 'bands': BANDS, 'ties': TIES,
       'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E217; not scored'}
json.dump(out, open(os.path.join(S3, 'scores-blind-e217.json'), 'w'), indent=1, sort_keys=True)


def fmtv(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float):
        return f'{v:.6g}'
    return '' if v is None else v


ccols = ['case', 'card', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'group_kind', 'group_mask', 'group_shape', 'n_runs', 'n_time', 'n_energy',
         'f_mean_mhz', 'f25', 'meas_cyc_wall', 'meas_T_op_us', 'meas_w', 'meas_rest', 'watts_case', 'factor_contention']
for mo in MODELS:
    ccols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg_mean', f'{mo}_e_E1', f'{mo}_d_E1', f'{mo}_e_E2', f'{mo}_d_E2', f'{mo}_e_E3', f'{mo}_e_E4']
ccols += ['v31_N_e_E1', 'v31_N2_e_E1', 'v3_N_e_E1', 'v31_gate_literal_REPORTED_e_E1', 'v31_gate_count_REPORTED_e_E1']
tcols = ['twin_time_v31', 'twin_energy_v31', 'twin_time_v3', 'twin_energy_v3', 'twin_time_v2', 'twin_energy_v2']
ncols = ['nominal_v31_e_wall', 'nominal_v31_e_E1', 'nominal_v31_e_E3', 'nominal_v3_e_wall', 'nominal_v3_e_E1', 'nominal_v2_e_wall', 'nominal_v2_e_E1']
with open(os.path.join(S3, 'scores-blind-e217-cases.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(ccols + tcols + ncols)
    for cid, c in PRIM['_crow'].items():
        nc = NOMI['_crow'][cid]
        row = [fmtv(c.get(k)) for k in ccols]
        row += [int(c['twin_time'][x.rsplit('_', 1)[1]]) if 'time' in x else int(c['twin_energy'][x.rsplit('_', 1)[1]]) for x in tcols]
        row += [fmtv(nc.get(k.replace('nominal_', ''))) for k in ncols]
        w.writerow(row)
rcols = ['id', 'session', 'card', 'fmt', 'kind', 'group_kind', 'group_mask', 'time_ok', 'energy_ok', 'capped', 'meas_f', 'meas_T_op_us', 'meas_cyc_wall',
         'meas_cyc_mean', 'meas_t_pass_s', 'meas_w', 'meas_rest']
for mo in MODELS:
    rcols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg', f'{mo}_e_E1', f'{mo}_e_E2', f'{mo}_e_E3', f'{mo}_e_E4']
with open(os.path.join(S3, 'scores-blind-e217-runs.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(rcols)
    for r in PRIM['_rrows'].values():
        w.writerow([fmtv(r.get(k)) for k in rcols])

# a readable summary
P = PRIM
TX = []
A = TX.append
A(f"blind-e217 (Q228): MM1's frozen models scored on E217, as decl-e217 declared. Read {T_READ}; label {out['label']}.")
A(f"Freeze post {FPOST['post']} {FPOST['record_time_pst']} PST (record line; {FPOST['context_time_pst']}).")
for s, v in labels.items():
    A(f"  {s}: {v['label']} (counts route {v['counts_route_label']}); T0 {v['session_T0_pst']} PST, first card command (README) {v['first_card_command_pst_README']}, "
      f"{v['margin_minutes_T0_after_post']} min after the post; claim {(v['claim'] or {}).get('time_pst')}, release {(v['release'] or {}).get('time_pst')}")
A(f"Loader check (MM1-v3.1's data_v31.mms_runs_all on the same bytes): {json.dumps(lchk)[:300]}")
A(f"VERDICT {P['VERDICT']} | part A {P['part_A_verdict']} {P['part_A_fails']} | part S {P['part_S_verdict']} {P['part_S']['v31']['failed']}")
A('counts ' + json.dumps(P['counts']))
for card in CARDS:
    A(f"part A {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in P['part_A']['v31'][card].items()))
for mo in MODELS:
    t = P['tables_per_case'][mo]
    A(f"{MN[mo]} no twin, pooled: wall {t['wall']['pooled']['no_twin']} | mean {t['mean']['pooled']['no_twin']} | sec {t['sec']['pooled']['no_twin']} | "
      f"E1 {t['E1']['pooled']['no_twin']} | E2 {t['E2']['pooled']['no_twin']} | E3 {t['E3']['pooled']['no_twin']} | E4 {t['E4']['pooled']['no_twin']}")
Sv = P['part_S']['v31']
A('part S (MM1-v3.1 + counts-e217 vs N): ' + json.dumps({k: Sv[k] for k in ('verdict', 'P1', 'P2', 'P3', 'P4')}) + ' Q1 ' +
  json.dumps({k: v for k, v in Sv['Q1'].items() if k != 'rows'}) + ' Q2 ' + json.dumps({k: v for k, v in Sv['Q2'].items() if k != 'rows'}))
for key, x in P['comparisons'].items():
    if key == 'D3 layout':
        for k2, y in x.items():
            A(f"{k2}: " + '; '.join(f"{r} " + ', '.join(f"{sc.replace('aifoundry1 ', '')} {z['verdict']} {z['closer_A']}/{z['closer_B']}/{z['ties']} p={z['p'] if z['p'] is None else round(z['p'], 4)}"
                                                       for sc, z in y[r].items()) for r in y))
    elif key.startswith('D4'):
        A(f"{key}: {json.dumps(x)}")
    else:
        A(f"{key}: " + '; '.join(f"{r} " + ', '.join(f"{sc.replace('aifoundry1 ', '')} {z['verdict']} {z['closer_A']}/{z['closer_B']}/{z['ties']} p={z['p'] if z['p'] is None else round(z['p'], 6)}"
                                                    for sc, z in x[r].items()) for r in x))
N = NOMI
A(f"NOMINAL footing (REPORTED): VERDICT {N['VERDICT']} | part A {N['part_A_verdict']} {N['part_A_fails']} | part S {N['part_S_verdict']}; watts set differs in {watts_diff} cases")
for card in CARDS:
    A(f"  nominal part A {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in N['part_A']['v31'][card].items()))
for mo in ('v31', 'v3', 'v2'):
    t = N['tables_per_case'][mo]
    A(f"  nominal {MN[mo]} no twin, pooled: wall {t['wall']['pooled']['no_twin']} | E1 {t['E1']['pooled']['no_twin']} | E3 {t['E3']['pooled']['no_twin']}")
A(f"'v3.1+both' equals 'v3.1+contention' on every case and quantity: {P['both_equals_contention_every_case']}")
open(os.path.join(S3, 'scores-blind-e217.txt'), 'w').write('\n'.join(TX) + '\n')
for n in ('scores-blind-e217.json', 'scores-blind-e217.txt', 'scores-blind-e217-cases.csv', 'scores-blind-e217-runs.csv'):
    print(sha(os.path.join(S3, n)), os.path.relpath(os.path.join(S3, n), L))
print('\n'.join(TX))
