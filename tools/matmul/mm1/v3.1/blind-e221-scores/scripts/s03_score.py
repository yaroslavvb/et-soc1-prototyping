#!/usr/bin/env python3
"""blind-e221 (Q235) step 3: THE READ AND THE SCORE, exactly as decl-e221's DECLARED-blind-e221.json says (sections 0, a-i; declared 06:15:39
PST, FROZEN.txt 06:17:38, posted #15.2.1.1) on the measured-conditions forecasts frozen in forecasts-blind-e221.json (hashed in
logs/step2-sha256.txt) and, beside it (REPORTED, deciding nothing), the NOMINAL footing frozen by decl-e221 (forecasts-nominal-e221.json).
This script is hashed before its first read of any E221 measurement, with READINGS-blind-e221.md (the readings it makes where the
declaration is silent: run selection, the 90% arithmetic, the test's NO DATA line, the label times, the REPORTED tables' forms).
Reads E221's committed data-e221-<s>.json (GitHub main, `git show` of work/lab-commit.txt's commit; copied to work/step3/data/ and hashed),
each session's queue (session/queue.json: ran, rc 0, check exact or approx; t_first_ms) and README (its stated first card command): the
measurement fields now. Scores per run and per case: T1 wall cycles, T2 counter mean, T3 seconds a pass (64 MB NB KB ops a minion x the
op time), E1 J over idle given t (watts at a watts case), E2 J over idle with t forecast, E3 J at rest given t, E4 J at rest with t forecast;
per card and pooled; twins apart (no-twin cases carry the pass rule and the headline); splits per class (MASK, CELL1, KB1, L2I8, MQ3, DK,
HLD, BW, NB1, ANCHOR), FULL / SUB, format and kind; THE PASS RULE (part A: MM1-v3.2 on the primary footing by E215's rule form on each card
over its no-twin cases; part S NOT APPLICABLE; MM1-v3.1's part A REPORTED); the comparisons D0 (MM1-v3.2 vs MM1-v3.1), D1 (MM1-v3.1 vs MM1-v3),
D2 (MM1-v3.1 vs MM1-v2), D3 (the layout term and verify-lay's controls vs MM1-v3.1 on the 461 subset-mask cases), D3c (the MM1-v3.3
candidates, REPORTED), D4 NOT APPLICABLE; REPORTED beside: the classes, the mask ladders (each placement family against its whole-chip
twin), the governed clocks; the label per session (BLIND / UNREAD / POST-READ by the freeze post's time and the session's first card
command). Checks first that its own run selection and readings equal MM1-v3.1's loader (data_v31.mms_runs_all) on the same bytes.
Desk; stdlib (the loader imports numpy). Run: /usr/bin/python3 -I -B s03_score.py <lane dir>
   (a stand-in test: ... <lane dir> --standin <dir>, outputs in work/step3-standin-<name>/; never E221's data)
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
STANDIN = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == '--standin' else None   # a stand-in day, never E221
LAB = '<LAB>'
W = '<WF>'
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


def git(*a, text=False):
    return subprocess.run(['git', '-C', LAB] + list(a), check=True, capture_output=True, text=text, env=ENV).stdout


T_START = ts()
# ------------------------------------------------------------------ the frozen inputs, by their logged sha256
PINS = {os.path.join(DEC, 'DECLARED-blind-e221.json'): 'b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4',
        os.path.join(DEC, 'DECLARED-blind-e221.md'): '9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b',
        os.path.join(DEC, 'FROZEN.txt'): '2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b',
        os.path.join(DEC, 'forecasts-nominal-e221.json'): 'f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831',
        os.path.join(DEC, 'forecasts-nominal-e221.csv'): 'e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a',
        os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json'): '3a686510a43c453ac85588d5e649c7fe2e8554c3a98357e79047784e5165fe98',
        os.path.join(DEC, 'inputs', 'step1', 'bands.json'): '57cc5faf6aa88b97023b7c8a3ef7c6200c6f75de90943b9b40e7da2825e91ef8',
        os.path.join(L, 'forecasts-blind-e221.json'): '10dac66160a871ac39453ebf4d7ac42d29c824beca59b2d079bcbbf9878dbebe',
        os.path.join(L, 'forecasts-blind-e221.csv'): '962252bd28c9a6184580a38fd2dad87f4790fab62097cd651d5b602f814bf844',
        os.path.join(L, 'work', 'step2', 'conditions-e221.json'): 'd28706e7a13d7a06c351ac1310bc599cca7c95eed435a3047b3845e2ae6e7e84'}
for p, h in PINS.items():
    assert sha(p) == h, p
DECL = json.load(open(os.path.join(DEC, 'DECLARED-blind-e221.json')))
DD = DECL['declaration']
FCJ = json.load(open(os.path.join(L, 'forecasts-blind-e221.json')))
FCN = json.load(open(os.path.join(DEC, 'forecasts-nominal-e221.json')))['cases']
RL = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'runs-listed.json')))
BJ = json.load(open(os.path.join(DEC, 'inputs', 'step1', 'bands.json')))
CONDJ = json.load(open(os.path.join(L, 'work', 'step2', 'conditions-e221.json')))
MODELS = ('v32', 'v31', 'v3', 'v2', 'v31c', 'v31b', 'cn12', 'cg1', 'cg1n1', 'cf1b', 'v32p', 'v32l')
MN = {'v32': 'MM1-v3.2', 'v31': 'MM1-v3.1', 'v3': 'MM1-v3', 'v2': 'MM1-v2', 'v31c': 'v3.1+contention', 'v31b': 'v3.1+both',
      'cn12': 'ctrl N1+N2', 'cg1': 'ctrl G1', 'cg1n1': 'ctrl G1+N1', 'cf1b': 'ctrl F1-layout-blind', 'v32p': 'MM1-v3.2+posimb', 'v32l': 'MM1-v3.2+L3S'}
assert FCJ['models'] == MN and [MN[m] for m in MODELS] == DECL['models']
REPORTED_MODELS = ('v32p', 'v32l')
assert [MN[m] for m in REPORTED_MODELS] == DECL['models_reported']
TWIN_OF = FCJ['twin_flags_of']
C1, C0, A2 = 'aifoundry1 card 1', 'aifoundry1 card 0', 'aifoundry2 card 0'
CARDS = (C1, C0, A2)
SHORT = {C1: 'a1c1', C0: 'a1c0', A2: 'a2c0'}
LOW = 3.0
BANDS = DD['pass_rule']['bands']
TIES = {c: BJ['cards'][c]['ties'] for c in CARDS}
assert TIES == {C1: {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.1},
                C0: {'cycles_ln': 0.005, 'joules_ln': 0.01, 'seconds_ln': 0.005, 'watts_W': 0.15},
                A2: {'cycles_ln': 0.005, 'joules_ln': 0.02, 'seconds_ln': 0.005, 'watts_W': 0.4}}, TIES   # the declaration's ties_how, literally
assert all(BANDS[c] == {r: BJ['cards'][c]['bands'][r]['band'] for r in ('E1', 'E2', 'E3', 'E4', 'T1', 'T2', 'T3')} | {'watts_W': BJ['cards'][c]['band_w']['band_W']}
           for c in CARDS)
PASS_NUM, PASS_DEN, TOO_FEW, ALPHA = 9, 10, 10, 0.05     # 'at least 90%': 10 x passed >= 9 x n (integer arithmetic, READINGS R3)
SHAPE = re.compile(r'gemmL(\d+)x(\d+)x(\d+):')
CLASSES = ('MASK', 'CELL1', 'KB1', 'L2I8', 'MQ3', 'DK', 'HLD', 'BW', 'NB1', 'ANCHOR')
FAMS = ('PLA', 'PLB', 'PLC', 'PLD', 'PLE', 'PLH', 'PLK', 'PLK3', 'PLL', 'PLM', 'PLN', 'PLX')
OKCHK = ('exact', 'approx')
FULLM = '0xffffffff'

# ------------------------------------------------------------------ the read
DATA, QUEUE, README, srcs = {}, {}, {}, {}
for s, d in sorted(CONDJ['sessions'].items()):
    path = d['file']
    qpath = f"{d['folder']}/session/queue.json"
    if STANDIN is None:
        raw = git('show', f'{COMMIT}:{path}')
        qraw = git('show', f'{COMMIT}:{qpath}')
        try:
            README[s] = git('show', f"{COMMIT}:{d['folder']}/README.md", text=True)
        except subprocess.CalledProcessError:
            README[s] = None
    else:
        path = os.path.join(STANDIN, f'data-e221-{s}.json')
        qpath = os.path.join(STANDIN, f'queue-{s}.json')
        raw = open(path, 'rb').read()
        qraw = open(qpath, 'rb').read()
        README[s] = None
    dst = os.path.join(S3, 'data', f'data-e221-{s}.json')
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
        x = byrun.get(r['run'])
        if x is None:      # a listed run that did not run: no data (never imputed)
            meas[r['id']] = {'time_ok': False, 'energy_ok': False, 'capped': False, 'loader_form_ok': False, 'queue_ok': False, 'base_ok': False,
                             'absent': True}
            continue
        v = (x.get('views') or {}).get(pv) or {}
        vals = str(x.get('values') or '')
        gl = bool(SHAPE.match(vals))
        base = bool(x.get('ran') and x.get('role') not in (None, 'null') and x.get('arm') and x.get('shires') and gl and
                    v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1)
        q = queue_entry(s, r['run'])
        rcs = (q or {}).get('rcs') or [(q or {}).get('rc')]
        chks = (q or {}).get('checks') or [(q or {}).get('check')]
        queue_ok = bool(q and q.get('ran') and q.get('rc') == 0 and all(c == 0 for c in rcs) and q.get('check') in OKCHK and all(c in OKCHK for c in chks))
        qsel['queue ok' if queue_ok else 'queue NOT ok'] += 1
        tv = base and queue_ok
        m = {'time_ok': tv, 'energy_ok': False, 'capped': bool(x.get('capped')), 'loader_form_ok': base, 'queue_ok': queue_ok, 'base_ok': base,
             'checks': chks, 'no_step': bool(x.get('no_step')), 'absent': False}
        if tv:
            m.update({'T': float(v['T_op_us']), 'cw': float(v['cyc_op_max']), 'cm': float(v['cyc_op_mean']), 'tp': float(v['t_pass_s']),
                      'f': float(v['kclock_mhz']), 'n_launch': v.get('n_launch'), 'thin': bool(v.get('thin'))})
            if v.get('dP_w') is not None and v.get('p_mean_w') and not x.get('capped') and x.get('role') != 'time':
                m.update({'energy_ok': True, 'w': float(v['dP_w']), 'pm': float(v['p_mean_w']), 'rest': float(v['p_mean_w']) - float(v['dP_w'])})
        meas[r['id']] = m

# ------------------------------------------------------------------ the loader check: MM1-v3.1's own reader on the same bytes
sys.path.insert(0, os.path.join(MM1, 'v3.1'))
import data_v31 as DV  # noqa: E402
D3 = DV.D
RL_BY_ID = {r['id']: r for r in RL['runs']}
lchk = {'card_diffs': 0, 'runs_loader_listed': 0, 'runs_loader_not_listed': 0, 'runs_mine_loader_form_ok': sum(1 for m in meas.values() if m['loader_form_ok']),
        'field_diffs': 0, 'missing': [], 'energy_flag_diffs': 0, 'not_listed_ids': []}
for s in DATA:
    got = DV.mms_runs_all((os.path.join(S3, 'data', f'data-e221-{s}.json'),), 'E221', D3.e212_kind)
    for g in got:
        rid = f"E221|{s}|{g['run']}"
        m = meas.get(rid)
        if m is None:
            lchk['runs_loader_not_listed'] += 1   # a run the declaration does not list (none expected: nulls are skipped by both)
            lchk['not_listed_ids'].append(rid)
            continue
        lchk['runs_loader_listed'] += 1
        if not m['loader_form_ok']:
            lchk['missing'].append(rid)
            continue
        if not m['time_ok']:   # the loader's form holds but the queue condition does not: no fields to compare (counted below)
            continue
        for a, b in (('T', 'T'), ('cyc_wall', 'cw'), ('cyc_mean', 'cm'), ('t_gemm', 'tp'), ('f', 'f')):
            lchk['field_diffs'] += (g[a] != m[b])
        if ('w' in g) != m['energy_ok']:
            lchk['energy_flag_diffs'] += 1
        elif 'w' in g:
            lchk['field_diffs'] += (g['w'] != m['w']) + (g['p_rest'] != m['rest'])
        lchk['card_diffs'] += (g['card'] != RL_BY_ID[rid]['card'])
lchk['equal'] = (lchk['field_diffs'] == 0 and lchk['card_diffs'] == 0 and not lchk['missing'] and lchk['energy_flag_diffs'] == 0 and
                 lchk['runs_loader_listed'] == lchk['runs_mine_loader_form_ok'] and lchk['runs_loader_not_listed'] == 0)
lchk['queue_condition'] = dict(qsel)
lchk['runs_time_ok_all'] = sum(1 for m in meas.values() if m['time_ok'])
lchk['runs_energy_ok_all'] = sum(1 for m in meas.values() if m['energy_ok'])
lchk['runs_capped'] = sum(1 for m in meas.values() if m['capped'])
lchk['runs_absent'] = sum(1 for m in meas.values() if m.get('absent'))
lchk['runs_loader_form_but_queue_not_ok'] = sum(1 for m in meas.values() if m['loader_form_ok'] and not m['queue_ok'])

# ------------------------------------------------------------------ the two footings: each run's forecast per model
RUNS = FCJ['runs']
CASES = FCJ['cases']


def primary_fc(rid, m):
    return RUNS[rid][m]


def nominal_fc(rid, m):
    """decl-e221's frozen nominal forecast of the run's case (every run of a case at the same nominal conditions)"""
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
    return {'n': n, 'rms_pct': 100 * math.sqrt(sum(x * x for x in v) / n), 'bias_pct': 100 * sum(v) / n}


def sta(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    n = len(v)
    return {'n': n, 'rms_W': math.sqrt(sum(x * x for x in v) / n), 'bias_W': sum(v) / n}


def sign_p(k, n):
    if n == 0:
        return None
    lo = min(k, n - k)
    tail = sum(math.comb(n, i) for i in range(lo + 1)) / 2.0 ** n
    return min(1.0, 2.0 * tail)


def decide(npos, nneg, na, nb, n_cases, too_few=TOO_FEW):
    """the declared test (section d): NO DATA with no case compared; TOO FEW under 10 untied cases; else the exact two-sided sign test
    (READINGS R4: blind-e219's reading, verified by verify-blind-e219)"""
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
SCOPES = (('pooled', lambda c: True), (C1, lambda c: c['card'] == C1), (C0, lambda c: c['card'] == C0), (A2, lambda c: c['card'] == A2))
SC4 = ('pooled', C1, C0, A2)


def score_footing(FC):
    """every declared figure on one footing (every listed run and case); FC(rid, model) gives the run's forecast"""
    rrows = {}
    for rid, fr in RUNS.items():
        m = meas[rid]
        o = {'id': rid, 'session': fr['session'], 'card': fr['card'], 'fmt': fr['fmt'], 'kind': fr['kind'], 'case': fr['case'], 'class': fr['class'],
             'subfamily': fr.get('subfamily'), 'group_mask': fr['group_mask'], 'arm': fr['arm'], 'mask': fr['mask'], 'role': fr['role'],
             'time_ok': m['time_ok'], 'energy_ok': m['energy_ok'], 'capped': m['capped']}
        if m['time_ok']:
            o.update({'meas_T_op_us': m['T'], 'meas_cyc_wall': m['cw'], 'meas_cyc_mean': m['cm'], 'meas_t_pass_s': m['tp'], 'meas_f': m['f'],
                      'f_cond_equal': (fr['f_mhz'] is not None and m['f'] == float(fr['f_mhz']))})
            for mo in MODELS:
                F = FC(rid, mo)
                o[f'{mo}_e_wall'] = F['cyc_wall'] / m['cw'] - 1
                o[f'{mo}_e_mean'] = F['cyc_mean'] / m['cm'] - 1
                o[f'{mo}_e_sec'] = F['sec_pass'] / m['tp'] - 1
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
    for cid, c in CASES.items():
        rs = [rrows[r] for r in c['runs']]
        tr = [r for r in rs if r['time_ok']]
        er = [r for r in rs if r['energy_ok']]
        o = {'case': cid, 'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'kind_energy': c['kind_energy'], 'mask': c['mask'],
             'class': c['class'], 'subfamily': c.get('subfamily'), 'group_mask': c['group_mask'], 'kernel': c['kernel'], 'n_shires': c['n_shires'],
             'n_runs': c['n_runs'], 'n_time': len(tr), 'n_energy': len(er), 'f_mean_mhz': c['f_mean_mhz'], 'f25': c['f25'],
             'twin_time': {mo: c['twin_time'][mo] for mo in MODELS}, 'twin_energy': {mo: c['twin_energy'][mo] for mo in MODELS},
             'factor_contention': c['factors']['v31c'], 'posimb_in_scope': c['posimb_in_scope'], 'l3s_in_domain': c['l3s_in_domain'],
             'sessions': c['sessions']}
        if tr:
            o['meas_cyc_wall'] = mean([r['meas_cyc_wall'] for r in tr])
            o['meas_cyc_mean'] = mean([r['meas_cyc_mean'] for r in tr])
            o['meas_T_op_us'] = mean([r['meas_T_op_us'] for r in tr])
            o['meas_t_pass_s'] = mean([r['meas_t_pass_s'] for r in tr])
            o['meas_f_mhz'] = mean([r['meas_f'] for r in tr])
            for mo in MODELS:
                for q in QT:
                    o[f'{mo}_e_{q}'] = mean([r[f'{mo}_e_{q}'] for r in tr])
        if er:
            o['meas_w'] = mean([r['meas_w'] for r in er])
            o['meas_rest'] = mean([r['meas_rest'] for r in er])
            v32g = mean([r.get('v32_Wg') for r in er]) if all('v32_Wg' in r for r in er) else None
            o['v32_Wg_mean'] = v32g
            o['watts_case'] = (v32g is None) or v32g < LOW or o['meas_w'] < LOW
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

    tables = {}
    for mo in MODELS:
        T = {}
        for q in QT + QE:
            T[q] = {}
            for scope, fn in SCOPES:
                cs = [c for c in CL if fn(c)]
                T[q][scope] = {'all': cell(cs, mo, q, None), 'no_twin': cell(cs, mo, q, False), 'twin': cell(cs, mo, q, True)}
        tables[mo] = T
    # the declared splits (each model, no twin and all): per class, FULL / SUB, per format, per kind; the classes are the REPORTED 'classes'
    SPL = {**{k: (lambda c, k=k: c['class'] == k) for k in CLASSES},
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
    for mo in ('v32', 'v31', 'v3', 'v2'):
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
                                  'E3': st([r.get(f'{mo}_e_E3') for r in rs if r['energy_ok']])} for mo in ('v32', 'v31', 'v3', 'v2')}
        persession[s]['runs'] = len(rs)
        persession[s]['time_ok'] = sum(1 for r in rs if r['time_ok'])
        persession[s]['energy_ok'] = sum(1 for r in rs if r['energy_ok'])

    # -------------------------------------------------------------- the pass rule, part A (MM1-v3.2, its no-twin cases, every class)
    def rule_cells(mo, card, rule, cs_all, twin_mo=None, twin_sel=False):
        q = RULEQ[rule]
        band = BANDS[card][rule]
        bw = BANDS[card]['watts_W']
        tm = twin_mo or mo
        cs = [c for c in cs_all if c['card'] == card and (twin_sel is None or twin_of(c, q, tm) == twin_sel)]
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
            v = 'PASS' if PASS_DEN * passed >= PASS_NUM * n else 'FAIL'
        return {'verdict': v, 'pass': passed, 'n': n, 'band': band, 'band_W': bw if q in ('E1', 'E2') else None, 'misses': sorted(miss)}

    # each model's cells over its own no-twin cases (its base model's twin flags); only MM1-v3.2's decide (MM1-v3.1's and the rest REPORTED)
    partA = {mo: {card: {rule: rule_cells(mo, card, rule, CL) for rule in RULEQ} for card in CARDS} for mo in MODELS}
    fails = [f'{card} {rule}' for card in CARDS for rule, x in partA['v32'][card].items() if x['verdict'] == 'FAIL']
    passes = [f'{card} {rule}' for card in CARDS for rule, x in partA['v32'][card].items() if x['verdict'] == 'PASS']
    A_verdict = 'FAIL' if fails else ('PASS' if passes else 'NOT DECIDED')
    fails31 = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'FAIL']
    passes31 = [f'{card} {rule}' for card in CARDS for rule, x in partA['v31'][card].items() if x['verdict'] == 'PASS']
    A31 = 'FAIL' if fails31 else ('PASS' if passes31 else 'NOT DECIDED')
    beside = {}
    for nm, fn in SPL.items():
        cs = [c for c in CL if fn(c)]
        beside[nm] = {card: {rule: {k: v for k, v in rule_cells('v32', card, rule, cs).items() if k != 'misses'} for rule in RULEQ} for card in CARDS}
    beside['twins (the twin cases only)'] = {card: {rule: {k: v for k, v in rule_cells('v32', card, rule, CL, twin_sel=True).items() if k != 'misses'}
                                                    for rule in RULEQ} for card in CARDS}
    beside['all cases (twins included)'] = {card: {rule: {k: v for k, v in rule_cells('v32', card, rule, CL, twin_sel=None).items() if k != 'misses'}
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
    L3D = lambda c: bool(c['l3s_in_domain'])  # noqa: E731
    D = {}
    for key, (a, b) in (('D0 MM1-v3.2 vs MM1-v3.1', ('v32', 'v31')), ('D1 MM1-v3.1 vs MM1-v3', ('v31', 'v3')), ('D2 MM1-v3.1 vs MM1-v2', ('v31', 'v2'))):
        D[key] = {rule: {scope: hh(a, b, rule, scope) for scope in SC4} for rule in HQ}
        D[key + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, b, rule, scope, neither_twin=True) for scope in SC4} for rule in HQ}
        D[key + ' per class (REPORTED)'] = {k: {rule: {scope: hh(a, b, rule, scope, lambda c, k=k: c['class'] == k) for scope in SC4} for rule in HQ}
                                            for k in CLASSES}
    D3 = {}
    for a in ('v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b'):
        nm = f'D3 {MN[a]} vs MM1-v3.1 (the subset masks)'
        D3[nm] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM) for scope in SC4} for rule in ('H1', 'H2')}
        D3[nm + ' (cases twin for neither, REPORTED)'] = {rule: {scope: hh(a, 'v31', rule, scope, SUBM, True) for scope in SC4} for rule in ('H1', 'H2')}
        D3[nm + ' per class (REPORTED)'] = {k: {rule: {scope: hh(a, 'v31', rule, scope, lambda c, k=k: SUBM(c) and c['class'] == k) for scope in SC4}
                                                for rule in ('H1', 'H2')} for k in ('MASK', 'CELL1', 'L2I8')}
    D['D3 layout'] = D3
    D3c = {}
    for a, b, sel, rules, what in (('v32p', 'v32', SUBM, ('H1', 'H2'), 'the subset masks'), ('v32l', 'v32', L3D, tuple(HQ), "L3S's full-mask cases"),
                                   ('v32p', 'v31', SUBM, ('H1', 'H2'), 'the subset masks'), ('v32l', 'v31', L3D, tuple(HQ), "L3S's full-mask cases")):
        nm = f'D3c {MN[a]} vs {MN[b]} ({what}; REPORTED)'
        D3c[nm] = {rule: {scope: hh(a, b, rule, scope, sel) for scope in SC4} for rule in rules}
        D3c[nm + ' per class'] = {k: {rule: {scope: hh(a, b, rule, scope, lambda c, k=k: sel(c) and c['class'] == k) for scope in SC4} for rule in rules}
                                  for k in CLASSES if any(sel(c) and c['class'] == k for c in CL)}
    D['D3c candidates (REPORTED, deciding nothing)'] = D3c
    D['D4 switch'] = 'NOT APPLICABLE: E221 has no operand-pattern arm (no designed tile; its kinds are zeros, ones and random)'
    both_equal = all(c.get(f'v31b_e_{q}') == c.get(f'v31c_e_{q}') for c in CL for q in QT + QE)
    posimb_equal_off_scope = all(c.get(f'v32p_e_{q}') == c.get(f'v32_e_{q}') for c in CL if not c['posimb_in_scope'] for q in QT + QE)
    l3s_equal_off_domain = all(c.get(f'v32l_e_{q}') == c.get(f'v32_e_{q}') for c in CL if not c['l3s_in_domain'] for q in QT + QE)
    return {'VERDICT': VERDICT, 'part_A_verdict': A_verdict, 'part_A_fails': fails, 'part_A_passes': passes,
            'part_S_verdict': 'NOT APPLICABLE (no operand-pattern arm)', 'part_A': partA, 'part_A_beside_REPORTED': beside,
            'part_A_MM1_v3_1_REPORTED': {'verdict': A31, 'fails': fails31, 'passes': passes31}, 'comparisons': D,
            'tables_per_case': tables, 'splits': splits, 'by_card_format_kind': bykind, 'per_run_REPORTED': perrun,
            'per_session_REPORTED': persession, 'both_equals_contention_every_case': both_equal,
            'posimb_equals_v32_off_its_scope': posimb_equal_off_scope, 'l3s_equals_v32_off_its_domain': l3s_equal_off_domain,
            'counts': {'runs': len(rrows), 'time_ok': sum(1 for r in RR if r['time_ok']), 'energy_ok': sum(1 for r in RR if r['energy_ok']),
                       'capped': sum(1 for r in RR if r['capped']), 'cases': len(CL), 'cases_with_time': sum(1 for c in CL if c['n_time']),
                       'cases_with_energy': sum(1 for c in CL if c['n_energy']), 'watts_cases': sum(1 for c in CL if c.get('watts_case')),
                       'f_cond_equal_all': all(r.get('f_cond_equal', True) for r in RR),
                       'no_twin_time_cases_v32': sum(1 for c in CL if c['n_time'] and not c['twin_time']['v32']),
                       'no_twin_energy_cases_v32': sum(1 for c in CL if c['n_energy'] and not c['twin_energy']['v32']),
                       'no_twin_time_cases_v31': sum(1 for c in CL if c['n_time'] and not c['twin_time']['v31']),
                       'no_twin_energy_cases_v31': sum(1 for c in CL if c['n_energy'] and not c['twin_energy']['v31']),
                       'subset_cases': sum(1 for c in CL if SUBM(c)), 'l3s_cases': sum(1 for c in CL if L3D(c))},
            '_rrows': rrows, '_crow': crow}


PRIM = score_footing(primary_fc)
NOMI = score_footing(nominal_fc)
watts_diff = sum(1 for k in PRIM['_crow'] if PRIM['_crow'][k].get('watts_case') != NOMI['_crow'][k].get('watts_case'))

# ------------------------------------------------------------------ REPORTED beside (deciding nothing)
CR = PRIM['_crow']
# (1) the mask ladders: each MASK subset case against its whole-chip twin (same card, arm, format, kind at 0xffffffff), per family
ladder = {}
for cid, c in CR.items():
    if c['class'] != 'MASK' or c['group_mask'] == 'FULL':
        continue
    tw = f"{c['card']}|{c['arm']}|{c['fmt']}|{c['kind']}|{FULLM}"
    t = CR.get(tw)
    row = {'case': cid, 'family': c['subfamily'], 'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'],
           'n_shires': c['n_shires'], 'twin_case': tw if t else None}
    if t and c.get('n_time') and t.get('n_time'):
        row['meas_ratio_wall'] = c['meas_cyc_wall'] / t['meas_cyc_wall']
        row['meas_ratio_mean'] = c['meas_cyc_mean'] / t['meas_cyc_mean']
        for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b', 'v32p', 'v32l'):
            fs = mean([RUNS[r][mo]['cyc_wall'] for r in CASES[cid]['runs'] if meas[r]['time_ok']])
            ft = mean([RUNS[r][mo]['cyc_wall'] for r in CASES[tw]['runs'] if meas[r]['time_ok']])
            fsm = mean([RUNS[r][mo]['cyc_mean'] for r in CASES[cid]['runs'] if meas[r]['time_ok']])
            ftm = mean([RUNS[r][mo]['cyc_mean'] for r in CASES[tw]['runs'] if meas[r]['time_ok']])
            row[f'{mo}_fc_ratio_wall'] = fs / ft
            row[f'{mo}_ratio_err_wall'] = (fs / ft) / row['meas_ratio_wall'] - 1
            row[f'{mo}_fc_ratio_mean'] = fsm / ftm
            row[f'{mo}_ratio_err_mean'] = (fsm / ftm) / row['meas_ratio_mean'] - 1
    ladder.setdefault(f"{c['card']}|{c['subfamily']}", []).append(row)
lad_sum = {}
for k, rows in sorted(ladder.items()):
    ok_rows = [r for r in rows if 'meas_ratio_wall' in r]
    lad_sum[k] = {'pairs': len(rows), 'pairs_scored': len(ok_rows),
                  'meas_ratio_wall_range': ([min(r['meas_ratio_wall'] for r in ok_rows), max(r['meas_ratio_wall'] for r in ok_rows)] if ok_rows else None)}
    for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'v32p'):
        lad_sum[k][MN[mo]] = {'wall': st([r.get(f'{mo}_ratio_err_wall') for r in ok_rows]), 'mean': st([r.get(f'{mo}_ratio_err_mean') for r in ok_rows])}
lad_fam = {}
for fam in FAMS:
    rows = [r for k, v in ladder.items() if k.endswith('|' + fam) for r in v if 'meas_ratio_wall' in r]
    lad_fam[fam] = {'pairs_scored': len(rows), **{MN[mo]: {'wall': st([r.get(f'{mo}_ratio_err_wall') for r in rows]),
                                                         'mean': st([r.get(f'{mo}_ratio_err_mean') for r in rows])}
                                                 for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'cn12', 'cg1', 'cg1n1', 'cf1b', 'v32p')}}
# (2) the governed clocks: each run's measured clock on the governed cards beside the nominal 800 MHz and the nominal-footing error
gov = {}
NR = NOMI['_rrows']
PRR = PRIM['_rrows']
for card in (C0, A2):
    rs = [r for r in PRR.values() if r['card'] == card and r['time_ok']]
    fs = [r['meas_f'] for r in rs]
    gov[card] = {'runs_time_ok': len(rs), 'clock_min_mhz': min(fs) if fs else None, 'clock_mean_mhz': mean(fs), 'clock_max_mhz': max(fs) if fs else None,
                 'runs_within_25_MHz_of_800': sum(1 for f in fs if abs(f - 800.0) <= 25.0), 'nominal_mhz': 800.0,
                 'MM1-v3.2 wall per run: primary': st([r['v32_e_wall'] for r in rs]),
                 'MM1-v3.2 wall per run: nominal 800 MHz footing': st([NR[r['id']]['v32_e_wall'] for r in rs]),
                 'MM1-v3.2 E1 per run (dP >= 3 W): primary': st([r.get('v32_e_E1') for r in rs if r['energy_ok'] and r['meas_w'] >= LOW]),
                 'MM1-v3.2 E1 per run (dP >= 3 W): nominal footing': st([NR[r['id']].get('v32_e_E1') for r in rs if r['energy_ok'] and r['meas_w'] >= LOW]),
                 'runs': [{'id': r['id'], 'clock_mhz': r['meas_f'], 'nominal_mhz': 800.0, 'v32_e_wall_primary': r['v32_e_wall'],
                           'v32_e_wall_nominal': NR[r['id']]['v32_e_wall']} for r in rs]}

# ------------------------------------------------------------------ the label per session (the declaration, section g)
FPOST = {}
for ln in open(os.path.join(W, 'out', 'orch', 'q235-frozen-posts.txt')):
    mm = re.match(r'#(15\.2\.1\.1) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST', ln)
    if mm:
        FPOST = {'post': '#' + mm.group(1), 'record_time_pst': f'{mm.group(2)} {mm.group(3)}',
                 'epoch_record': datetime.datetime.strptime(f'{mm.group(2)} {mm.group(3)}', '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ).timestamp(),
                 'names_FROZEN_txt': '2df06f06b7d4c16caca6ceb56cff8d6c47abcb6fec6e6671ce72c700378b299b' in ln,
                 'names_declaration_md': '9cd8256bbc9a40b2850094bf936c02d2efd8fe65b886e95b92774dd1d5bc9f1b' in ln,
                 'names_declaration_json': 'b483f46cdcc0138d912e445a01fadb84a113cce0967f80e2b3f0ebe1f08c8ec4' in ln,
                 'names_nominal_csv': 'e3361847c4d1600b1b3deeaac3a42131b26f7bcb6434450bd8094c4965cbe59a' in ln,
                 'names_nominal_json': 'f787561175410898cca55f223652307ed5799062f18165b02f88285e3cf30831' in ln}
assert FPOST and all(FPOST[k] for k in FPOST if k.startswith('names_')), FPOST
SEEN = os.path.join(W, 'out', 'orch', 'discussion-seen-q188.json')
FPOST['own_time_pst'] = None
try:
    for x in json.load(open(SEEN)):
        if isinstance(x, str) and x.startswith('#15|#15.2.1.1|'):
            t = datetime.datetime.strptime(x.split('|')[2], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
            FPOST['own_epoch'] = t.timestamp()
            FPOST['own_time_pst'] = t.astimezone(TZ).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
except (OSError, ValueError):
    pass
FPOST['epoch_used'] = max(FPOST['epoch_record'], FPOST.get('own_epoch') or 0)   # the later of the two: a session is BLIND only after both
FPOST['time_used_pst'] = datetime.datetime.fromtimestamp(FPOST['epoch_used'], TZ).strftime('%Y-%m-%d %H:%M:%S')
FROZEN_TXT_PST = '2026-11-20 06:17:38'
REL = os.path.join(W, 'out', 'orch', 'e221-releases.txt')
claims, releases = collections.defaultdict(list), {}
for ln in open(REL).read().splitlines():
    mm = re.match(r'#([\d.]+) (\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST: (CLAIM|RELEASE)', ln)
    if not mm:
        continue
    t = f'{mm.group(2)} {mm.group(3)}'
    ep = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZ).timestamp()
    if mm.group(4) == 'CLAIM':
        k = re.search(r'\((a[12]c[01]-S\d)', ln)
        if k:
            claims[k.group(1)].append({'post': '#' + mm.group(1), 'time_pst': t, 'epoch': ep})
    else:
        k = re.search(r'sessions/(\d{10})-(a[12]c[01]-S\d)/', ln)
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
        if README[s] is None:
            fcc = 'README NOT READ'
        else:
            mm = re.search(r'first card command[^0-9]{0,60}(\d{1,2}:\d{2}:\d{2}(?:\.\d+)?)', README[s])
            fcc = mm.group(1) if mm else 'NOT FOUND in the README'
    first = (tf / 1000.0) if tf else t0   # the first card command (the queue's t_first_ms), else the session's T0 (its id)
    cls = [c for c in claims.get(s, []) if t0 is None or c['epoch'] <= t0 + 1]   # the claim this session ran under: the last one before its T0
    cl = cls[-1] if cls else None
    if first is not None and first > FPOST['epoch_used'] and (cl is None or cl['epoch'] > FPOST['epoch_used']):
        lab = 'BLIND'
    elif first is not None:
        lab = 'UNREAD (provided no lab lane read its data before the post; else POST-READ)'
    else:
        lab = 'NOT DECIDED (no first datum time)'
    labels[s] = {'label': lab, 'session_id': d['session'], 'session_T0_pst': t0s, 'first_card_command_pst_queue': tfs,
                 'first_card_command_pst_README': fcc, 'claim': cl, 'claims_for_this_key': claims.get(s, []), 'release': releases.get(s),
                 'freeze_post': FPOST['post'], 'freeze_post_time_used_pst': FPOST['time_used_pst'],
                 'margin_minutes_first_datum_after_post': (round((first - FPOST['epoch_used']) / 60.0, 2) if first else None),
                 'release_session_id_equals_data': (releases.get(s, {}).get('session_id') == d['session'])}
ALL_BLIND = all(v['label'] == 'BLIND' for v in labels.values())

# ------------------------------------------------------------------ write
out = {'label': ('BLIND (every session: its first datum after the freeze post)' if ALL_BLIND else 'MIXED: see labels'), 'labels': labels,
       'freeze_post': FPOST, 'frozen_txt_time_pst': FROZEN_TXT_PST, 'e221_releases_sha256_at_read': sha(REL), 'lane': 'blind-e221', 'round': 'Q235',
       'started_pst': T_START, 'read_pst': T_READ, 'python': sys.version.split()[0], 'sources': srcs, 'loader_check': lchk, 'standin': STANDIN,
       'VERDICT': PRIM['VERDICT'], 'part_A_verdict': PRIM['part_A_verdict'], 'part_A_fails': PRIM['part_A_fails'],
       'part_S_verdict': PRIM['part_S_verdict'], 'part_A_MM1_v3_1_REPORTED': PRIM['part_A_MM1_v3_1_REPORTED'],
       'primary_footing': {k: v for k, v in PRIM.items() if not k.startswith('_')},
       'nominal_footing_REPORTED': {k: v for k, v in NOMI.items() if not k.startswith('_')},
       'watts_set_differs_between_footings_cases': watts_diff,
       'mask_ladders_REPORTED': {'by_card_family': lad_sum, 'by_family': lad_fam, 'pairs': ladder,
                                 'form': 'each MASK subset case / its whole-chip twin (same card, arm, format, kind at 0xffffffff): measured ratio of '
                                         'the case-mean cycles an op (wall; counter mean) and each model\'s forecast ratio; error = forecast ratio / '
                                         'measured ratio - 1'},
       'governed_clock_REPORTED': gov,
       'models': MN, 'models_reported': list(REPORTED_MODELS), 'twin_flags_of': TWIN_OF, 'bands': BANDS, 'ties': TIES,
       'not_applicable': {'v3.1+gemmLnc': 'NOT APPLICABLE: no gemmLnc arm in E221; not scored',
                          'MM1-v3.2+AF4': 'NOT APPLICABLE: no gemmLnc arm in E221; not scored',
                          'part S and D4': 'NOT APPLICABLE: no operand-pattern arm'}}
json.dump(out, open(os.path.join(S3, 'scores-blind-e221.json'), 'w'), indent=1, sort_keys=True)


def fmtv(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, float):
        return repr(v)
    return '' if v is None else v


ccols = ['case', 'card', 'arm', 'fmt', 'kind', 'kind_energy', 'mask', 'class', 'subfamily', 'group_mask', 'n_shires', 'n_runs', 'n_time', 'n_energy',
         'f_mean_mhz', 'f25', 'meas_f_mhz', 'meas_cyc_wall', 'meas_cyc_mean', 'meas_T_op_us', 'meas_t_pass_s', 'meas_w', 'meas_rest', 'watts_case',
         'factor_contention', 'posimb_in_scope', 'l3s_in_domain']
for mo in MODELS:
    ccols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg_mean', f'{mo}_e_E1', f'{mo}_d_E1', f'{mo}_e_E2', f'{mo}_d_E2', f'{mo}_e_E3', f'{mo}_e_E4']
tcols = [f'twin_{q}_{mo}' for mo in ('v32', 'v31', 'v3', 'v2') for q in ('time', 'energy')]
ncols = [f'nominal_{mo}_e_{q}' for mo in ('v32', 'v31', 'v3', 'v2') for q in ('wall', 'sec', 'E1', 'E3')] + ['nominal_watts_case']
with open(os.path.join(S3, 'scores-blind-e221-cases.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(ccols + tcols + ncols)
    for cid, c in PRIM['_crow'].items():
        nc = NOMI['_crow'][cid]
        row = [fmtv(c.get(k)) for k in ccols]
        row += [int(c['twin_' + x.split('_')[1]][x.split('_')[2]]) for x in tcols]
        row += [fmtv(nc.get(k.replace('nominal_', ''))) for k in ncols]
        w.writerow(row)
rcols = ['id', 'session', 'card', 'fmt', 'kind', 'class', 'subfamily', 'group_mask', 'arm', 'mask', 'role', 'time_ok', 'energy_ok', 'capped', 'meas_f',
         'meas_T_op_us', 'meas_cyc_wall', 'meas_cyc_mean', 'meas_t_pass_s', 'meas_w', 'meas_rest']
for mo in MODELS:
    rcols += [f'{mo}_e_wall', f'{mo}_e_mean', f'{mo}_e_sec', f'{mo}_Wg', f'{mo}_e_E1', f'{mo}_e_E2', f'{mo}_e_E3', f'{mo}_e_E4']
with open(os.path.join(S3, 'scores-blind-e221-runs.csv'), 'w', newline='') as fh:
    w = csv.writer(fh, lineterminator='\n')
    w.writerow(rcols)
    for r in PRIM['_rrows'].values():
        w.writerow([fmtv(r.get(k)) for k in rcols])


def f2(x, nd=2):
    return 'None' if x is None else f'{x:.{nd}f}'


def stx(x):
    if x is None:
        return 'NO DATA'
    if 'relative' in x:
        a, b = x['relative'], x['watts']
        return (f"{f2(a['rms_pct'])}% ({f2(a['bias_pct'], 2)}) n{a['n']}" if a else 'rel NO DATA') + (f"; watts {f2(b['rms_W'], 3)} W n{b['n']}" if b else '')
    return f"{f2(x['rms_pct'])}% ({f2(x['bias_pct'], 2)}) n{x['n']}"


# a readable summary
P = PRIM
TX = []
A = TX.append
A(f"blind-e221 (Q235): MM1's frozen models scored on E221, as decl-e221 declared. Read {T_READ}; label {out['label']}.")
A(f"Freeze post {FPOST['post']}: record line {FPOST['record_time_pst']} PST, the post's own time {FPOST['own_time_pst']} PST; the later used: {FPOST['time_used_pst']} (FROZEN.txt {FROZEN_TXT_PST}).")
for s, v in labels.items():
    A(f"  {s} ({v['session_id']}): {v['label']}; claim {(v['claim'] or {}).get('post')} {(v['claim'] or {}).get('time_pst')}, T0 {v['session_T0_pst']}, "
      f"first card command {v['first_card_command_pst_queue']} (README {v['first_card_command_pst_README']}), {v['margin_minutes_first_datum_after_post']} min after the post; "
      f"release {(v['release'] or {}).get('post')} {(v['release'] or {}).get('time_pst')}")
A(f"Loader check (MM1-v3.1's data_v31.mms_runs_all on the same bytes): {json.dumps({k: v for k, v in lchk.items() if k not in ('missing', 'not_listed_ids')})}")
A(f"VERDICT {P['VERDICT']} | part A (MM1-v3.2) {P['part_A_verdict']} {P['part_A_fails']} | part S {P['part_S_verdict']} | MM1-v3.1's part A (REPORTED) "
  f"{P['part_A_MM1_v3_1_REPORTED']['verdict']} {P['part_A_MM1_v3_1_REPORTED']['fails']}")
A('counts ' + json.dumps(P['counts']))
for mo in ('v32', 'v31'):
    for card in CARDS:
        A(f"part A {MN[mo]} {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in P['part_A'][mo][card].items()))
        if mo == 'v32':
            for r, x in P['part_A'][mo][card].items():
                if x['misses']:
                    A(f"    {r} misses ({len(x['misses'])}): " + '; '.join(m.split('|', 1)[1] for m in x['misses']))
for mo in MODELS:
    t = P['tables_per_case'][mo]
    A(f"{MN[mo]} no twin, pooled: wall {stx(t['wall']['pooled']['no_twin'])} | mean {stx(t['mean']['pooled']['no_twin'])} | sec {stx(t['sec']['pooled']['no_twin'])} | "
      f"E1 {stx(t['E1']['pooled']['no_twin'])} | E2 {stx(t['E2']['pooled']['no_twin'])} | E3 {stx(t['E3']['pooled']['no_twin'])} | E4 {stx(t['E4']['pooled']['no_twin'])}")
for mo in ('v32', 'v31', 'v3', 'v2'):
    t = P['tables_per_case'][mo]
    for card in CARDS:
        A(f"  {MN[mo]} {card} no twin: wall {stx(t['wall'][card]['no_twin'])} | mean {stx(t['mean'][card]['no_twin'])} | E1 {stx(t['E1'][card]['no_twin'])} | "
          f"E3 {stx(t['E3'][card]['no_twin'])}")
for k in CLASSES:
    A(f"  class {k} (pooled, no twin): " + ' | '.join(f"{MN[mo]} wall {stx(P['splits'][mo][k + '|pooled']['wall']['no_twin'])} E1 {stx(P['splits'][mo][k + '|pooled']['E1']['no_twin'])}"
                                                    for mo in ('v32', 'v31', 'v3', 'v2')))


def hline(key, x):
    return f"{key}: " + '; '.join(f"{r} " + ', '.join(f"{sc.replace('aifoundry', 'a')} {z['verdict']} {z['closer_A']}/{z['closer_B']}/{z['ties']} p={'None' if z['p'] is None else format(z['p'], '.3g')}"
                                                    for sc, z in x[r].items()) for r in x)


for key, x in P['comparisons'].items():
    if key in ('D3 layout', 'D3c candidates (REPORTED, deciding nothing)'):
        for k2, y in x.items():
            if k2.endswith('per class') or 'per class' in k2:
                continue
            A(hline(k2, y))
    elif key.startswith('D4'):
        A(f"{key}: {x}")
    elif 'per class' in key:
        for k2, y in x.items():
            A(f"{key} {k2}: " + '; '.join(f"{r} pooled {y[r]['pooled']['verdict']} {y[r]['pooled']['closer_A']}/{y[r]['pooled']['closer_B']}/{y[r]['pooled']['ties']}" for r in y))
    else:
        A(hline(key, x))
N = NOMI
A(f"NOMINAL footing (REPORTED): VERDICT {N['VERDICT']} | part A {N['part_A_verdict']} {N['part_A_fails']}; watts set differs in {watts_diff} cases")
for card in CARDS:
    A(f"  nominal part A {card}: " + ', '.join(f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in N['part_A']['v32'][card].items()))
for mo in ('v32', 'v31', 'v3', 'v2'):
    t = N['tables_per_case'][mo]
    A(f"  nominal {MN[mo]} no twin, pooled: wall {stx(t['wall']['pooled']['no_twin'])} | sec {stx(t['sec']['pooled']['no_twin'])} | E1 {stx(t['E1']['pooled']['no_twin'])} | "
      f"E3 {stx(t['E3']['pooled']['no_twin'])}")
A('mask ladders (REPORTED), ratio error rms % wall (MM1-v3.2 / v3.1 / v3 / v2 / +contention / posimb) by family: ' + '; '.join(
    f"{fam} n{v['pairs_scored']} " + '/'.join(f2((v[MN[mo]]['wall'] or {}).get('rms_pct')) for mo in ('v32', 'v31', 'v3', 'v2', 'v31c', 'v32p'))
    for fam, v in lad_fam.items()))
for card, g in gov.items():
    A(f"governed clock (REPORTED) {card}: runs {g['runs_time_ok']}, clock {f2(g['clock_min_mhz'], 2)}-{f2(g['clock_max_mhz'], 2)} MHz (mean {f2(g['clock_mean_mhz'], 2)}), "
      f"MM1-v3.2 wall per run primary {stx(g['MM1-v3.2 wall per run: primary'])}, nominal {stx(g['MM1-v3.2 wall per run: nominal 800 MHz footing'])}")
for k in CLASSES:
    A(f"part A beside, class {k} (REPORTED): " + '; '.join(f"{SHORT[card]} " + ', '.join(
        f"{r} {x['verdict']} {x['pass']}/{x['n']}" for r, x in P['part_A_beside_REPORTED'][k][card].items()) for card in CARDS))
A(f"'v3.1+both' equals 'v3.1+contention' on every case and quantity: {P['both_equals_contention_every_case']}; "
  f"posimb equals MM1-v3.2 off its scope: {P['posimb_equals_v32_off_its_scope']}; L3S equals MM1-v3.2 off its domain: {P['l3s_equals_v32_off_its_domain']}")
open(os.path.join(S3, 'scores-blind-e221.txt'), 'w').write('\n'.join(TX) + '\n')
for n in ('scores-blind-e221.json', 'scores-blind-e221.txt', 'scores-blind-e221-cases.csv', 'scores-blind-e221-runs.csv'):
    print(sha(os.path.join(S3, n)), os.path.relpath(os.path.join(S3, n), L))
print('\n'.join(TX))
