#!/usr/bin/env python3
"""unread-e212sw (Q218) step 3: THE READ AND THE SCORE, exactly as declared (declared-unread.json, sha256 5eb2c93d...) with the forecasts
frozen in step 2 (forecasts-unread.json, sha256 8938bbeb...). Label of every figure: UNREAD.

Reads, for the first time in this lane, the test runs' measurements:
  - E212: each committed session's data-e212-<s>.json at GitHub main (git show of the lane's commit 8e91dda6), checked byte for byte against
    MM1-v3's vendored copy where it has one; each run reduced by the declared rule (data_v3.mms_runs's own selection, the energy condition
    widened from the kinds random, zeros and ones to the listed test runs; cross-checked against data_v3.mms_runs on every reference run);
  - E206 and E207: MM1-v3's own loader records (data_v3.energy_points()), its vendored inputs checked against the committed data folders.
Then evaluates each model's frozen formula at each run's measured conditions, cross-checks MM1-v3's formula against its predictor called
there (the same added rows and phi), and scores Q1 (W over idle given t), Q2 (the share of D), Q3 (J at rest given t, REPORTED) and Q4
(J over idle with the seconds forecast, REPORTED); per run, per case, per group, per card, per format, by configuration twins and by the
design lanes' sight; then the pass rule (P1-P4 against N) and the same against N2, V1, V3phi1, and E212 and E206/E207 apart (REPORTED).
Desk; no device. Run: /usr/bin/python3 -I -B s03_score.py <lane dir>
"""
import collections
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time

import numpy as np

L = os.path.abspath(sys.argv[1])
V3 = os.path.join(L, 'work', 'lab', 'tools', 'matmul', 'mm1', 'v3')
CNT = os.path.join(L, 'work', 'counts')
LAB = '<LAB>'
OUTD = os.path.join(L, 'work', 'step3')
DATAD = os.path.join(OUTD, 'data')
os.makedirs(DATAD, exist_ok=True)
ENV = dict(os.environ, GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='url.https://github.com/.insteadOf', GIT_CONFIG_VALUE_0='git@github.com:')
LOW = 3.0


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def ts():
    return time.strftime('%a %d %b %Y %H:%M:%S PST', time.localtime())


DECL_P = os.path.join(L, 'declared-unread.json')
FC_P = os.path.join(L, 'forecasts-unread.json')
assert sha(DECL_P) == '5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc', 'declaration changed'
assert sha(FC_P) == '8938bbebd1a6db028d55602773e7c2bce7286f6e378f2bcede948f82deb79f01', 'forecasts changed'
DECL = json.load(open(DECL_P))
FC = json.load(open(FC_P))
COMMIT = DECL['lab_commit']
start = ts()
print('step 3 start', start)

# ---------------------------------------------------------------- MM1-v3 as landed: its loaders, its priced points' configurations (before any row is added)
sys.path.insert(0, V3)
import data_v3 as D  # noqa: E402
import energy_v3 as EN  # noqa: E402
import mm1_core_v3 as C  # noqa: E402
import mm1_v3  # noqa: E402
import postcheck_v3 as PC  # noqa: E402

EP = D.energy_points()
X = EN.Features(EP)
erung = PC.rung_of(EP)
fit_cfg = {PC.cfg_t(e) for e, r, u in zip(EP, erung, X.usable3) if u and not r}
EPID = {e['id']: e for e in EP}
print('MM1-v3 energy points', len(EP), '; priced (usable3, rungs out)', int(sum(1 for r, u in zip(erung, X.usable3) if u and not r)),
      '; their configurations', len(fit_cfg))

# ---------------------------------------------------------------- the reads: the committed files, checked against MM1-v3's vendored copies
src_check = {}
SESS = sorted({r['session'] for k in ('group_A_pass_rule_pool', 'group_C_reported_sparse50') for r in DECL['a_runs'][k]['e212_runs']})
DATA = {}
for s in SESS:
    rel = f'docs/reports/data/2026-11-17-e212-mmsweep2-{s}/data-e212-{s}.json'
    b = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{rel}'], check=True, capture_output=True, env=ENV).stdout
    p = os.path.join(DATAD, f'data-e212-{s}.json')
    open(p, 'wb').write(b)
    vend = [os.path.join(V3, 'inputs', d, f'{s}__data-e212-{s}.json') for d in ('e212', 'e212-unread')]
    vend = [v for v in vend if os.path.exists(v)]
    src_check[rel] = {'sha256': sha(p), 'mm1_v3_vendored_equal': (sha(vend[0]) == sha(p)) if vend else 'not vendored'}
    DATA[s] = json.load(open(p))
for rel, vend in (('docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3/data-e206.json', 'inputs/v2/v1/data-e206.json'),
                  ('docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json', 'inputs/e206b/data-e206.json'),
                  ('docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json', 'inputs/e207/data-e207.json')):
    b = subprocess.run(['git', '-C', LAB, 'show', f'{COMMIT}:{rel}'], check=True, capture_output=True, env=ENV).stdout
    h = hashlib.sha256(b).hexdigest()
    src_check[rel] = {'sha256': h, 'mm1_v3_vendored_equal': h == sha(os.path.join(V3, vend)), 'vendored_as': vend}
print('sources:', json.dumps({k.split('/')[-1] + ' ' + k.split('/')[-2][-12:]: v['mm1_v3_vendored_equal'] for k, v in src_check.items()}))


def e212_records(s, want_runs):
    """data_v3.mms_runs's selection, the energy condition widened to the listed runs (want_runs: run ids that may carry energy)"""
    Dd = DATA[s]
    ck = Dd['card']
    card = D.CARDS[ck]
    pv = Dd['primary_view']
    out = {}
    for r in Dd['runs']:
        if not r.get('ran') or r.get('role') in (None, 'null') or not r.get('arm'):
            continue
        mask = r.get('shires')
        vals = r.get('values') or ''
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', vals)
        if not m or not mask:
            continue
        MB, NB, KB = (int(x) for x in m.groups())
        kind = D.e212_kind(r)
        if kind is None:
            continue
        v = (r.get('views') or {}).get(pv) or {}
        rec = {'run': r['run'], 'session': s, 'card': card, 'arm': f'gemmL{MB}x{NB}x{KB}', 'fmt': r.get('type'), 'kind': kind, 'mask': mask,
               'role': r['role'], 'capped': bool(r.get('capped')), 'view': pv, 'die_start_c': r.get('die_start_c'), 'why': None}
        if not (v.get('T_op_us') and v.get('cyc_op_max') and (v.get('n_launch') or 0) >= 1):
            rec['why'] = 'no time figure in the primary view'
            out[r['run']] = rec
            continue
        rec.update({'f': float(v['kclock_mhz']), 'T': float(v['T_op_us']), 'cyc_wall': float(v['cyc_op_max'])})
        energy_ok = (v.get('dP_w') is not None and v.get('p_mean_w') and not r.get('capped') and r['role'] != 'time')
        if (kind in D.ENERGY_KINDS or r['run'] in want_runs) and energy_ok:
            mv = ((v.get('rails') or {}).get('minion') or {}).get('mV')
            rec.update({'w': float(v['dP_w']), 'p_mean': float(v['p_mean_w']), 'p_rest': float(v['p_mean_w']) - float(v['dP_w']),
                        'V_mv': (float(mv) if mv is not None else None)})
        elif not energy_ok:
            rec['why'] = ('capped' if r.get('capped') else ('role time' if r['role'] == 'time' else 'no dP_w / p_mean_w in the primary view'))
        out[r['run']] = rec
    return out


TEST212 = {}
for grp, k in (('A', 'group_A_pass_rule_pool'), ('C', 'group_C_reported_sparse50')):
    for r in DECL['a_runs'][k]['e212_runs']:
        TEST212[r['id']] = dict(r, group=grp)
REC = {}
loader_check = {'runs_compared': 0, 'max_abs_diff': 0.0}
for s in SESS:
    want = {r['run'] for r in TEST212.values() if r['session'] == s}
    REC[s] = e212_records(s, want)
    # cross-check against MM1-v3's own data_v3.mms_runs on the same file (every record it makes: time for all, energy for random/zeros/ones)
    mine = REC[s]
    vdir = 'e212' if os.path.exists(os.path.join(V3, 'inputs', 'e212', f'{s}__data-e212-{s}.json')) else 'e212-unread'
    for q in D.mms_runs((vdir, f'{s}__data-e212-{s}.json'), 'E212', D.e212_kind):
        m = mine[q['run']]
        for fld in ('T', 'f', 'w', 'p_rest', 'V_mv'):
            if fld in q and q[fld] is not None:
                loader_check['runs_compared'] += 1
                loader_check['max_abs_diff'] = max(loader_check['max_abs_diff'], abs(q[fld] - m[fld]))
assert loader_check['max_abs_diff'] == 0.0, loader_check
print('E212 loader = data_v3.mms_runs on every field it makes:', json.dumps(loader_check))

# ---------------------------------------------------------------- MM1-v3's predictor with the frozen rows (as step 2), for the cross-check and Q4
C32 = json.load(open(os.path.join(CNT, 'counts-fp32-gemm-states.json')))['shapes']
C16 = json.load(open(os.path.join(CNT, 'counts-fp16-int8-launch.json')))['rows']
for S in ('S1', 'S2'):
    for kind, row in C32[S].items():
        assert kind not in EN.E210C[S]
        EN.E210C[S][kind] = row
for key, row in C16.items():
    assert key not in EN.SWT
    EN.SWT[key] = row
for k, v in DECL['e_phi']['values'].items():
    fmt, kind = k.split('|', 1)
    if kind.startswith('pattern:sparse50'):
        continue
    for kb1 in (True, False):
        EN._PHI[(fmt, kind, kb1)] = float(v)
params = json.load(open(os.path.join(V3, 'out', 'mm1_v3_params.json')))
M3 = mm1_v3.Model(params)
g3, xi = FC['g'], FC['xi']
FCR = {r['id']: r for r in FC['rows']}


def W_form(k, card, t, f, V, T0):
    sV = (V / 0.517) ** 2
    return (k['K0'] + g3 * C.G_of_f(card, f) + (1e6 / t) * (sV * k['K1'] + (1.0 + xi * (sV - 1.0)) * k['K2'])) * (1.0 + 0.0048 * (T0 - 50.0))


def W_v1(k, card, t, f, V):
    sV = (V / 0.517) ** 2
    return k['A0'] + k['g1'] * C.G_of_f(card, f) + sV * k['B1'] / t


V_FOOT = {'aifoundry1 card 1': 0.517, 'aifoundry3 card 0': 0.522}
xcheck = {'n': 0, 'max_rel': 0.0}


def conditions_e212(rec):
    card = rec['card']
    if card in V_FOOT:
        V = V_FOOT[card]
    else:
        V = rec['V_mv'] / 1000.0 if rec.get('V_mv') else float(C.volts(card, rec['f']))
    T0 = rec['die_start_c'] if rec.get('die_start_c') is not None else 50.0
    return {'f': rec['f'], 'V': V, 'T0': T0, 't': rec['T']}


def conditions_pt(e):
    V = 0.517 * math.sqrt(e['s'])
    T0 = e['die_start'] if e.get('die_start') is not None else 50.0
    return {'f': e['f'], 'V': V, 'T0': T0, 't': e['T']}


def forecast(fid, card, arm, fmt, priced, mask, cond):
    """every model's W given t at cond (frozen K's), the predictor cross-check for V3, and V3's W at its own forecast op time (Q4)"""
    fr = FCR[fid]
    out = {'V3': W_form(fr['V3'], card, cond['t'], cond['f'], cond['V'], cond['T0'])}
    p = M3.predict(card, arm, fmt, priced, mask, cond['f'], kernel='rgm136', V=cond['V'], t0_c=cond['T0'])
    Wp = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / cond['t']
    rel = abs(Wp / out['V3'] - 1.0)
    xcheck['n'] += 1
    xcheck['max_rel'] = max(xcheck['max_rel'], rel)
    out['t_fc'] = p['T_op_us']
    out['V3_at_tfc'] = p['W_affine']['A_W'] + p['W_affine']['B_W_us'] / p['T_op_us']
    for m in ('N', 'N2', 'V3phi1'):
        if isinstance(fr.get(m), dict):
            out[m] = W_form(fr[m], card, cond['t'], cond['f'], cond['V'], cond['T0'])
    if isinstance(fr.get('V1'), dict):
        out['V1'] = W_v1(fr['V1'], card, cond['t'], cond['f'], cond['V'])
    return out


# ---------------------------------------------------------------- per test run (E212) and per test point (E206/E207)
MODELS = ('V3', 'N', 'N2', 'V3phi1', 'V1')
rows = []
notes = []


def q1(Wf, Wm):
    return (Wf / Wm - 1.0) if Wm >= LOW else None


def ref_block(refs_runs, getter):
    """the mean measured W and the mean of each model's forecast over a reference kind's runs (points), at their own conditions"""
    got = [getter(x) for x in refs_runs]
    got = [g for g in got if g is not None]
    if not got:
        return None
    return {'n': len(got), 'W_meas': float(np.mean([g['W_meas'] for g in got])),
            'fc': {m: float(np.mean([g['fc'][m] for g in got])) for m in ('V3', 'V1') if all(m in g['fc'] for g in got)}}


def e212_ref_getter(s):
    def g(run):
        rec = REC[s].get(run)
        if rec is None or 'w' not in rec:
            notes.append(f'E212 {s} {run}: reference without energy ({rec.get("why") if rec else "not in the data"})')
            return None
        fid = f'E212|{s}|{run}'
        cond = conditions_e212(rec)
        return {'W_meas': rec['w'], 'fc': forecast(fid, rec['card'], rec['arm'], rec['fmt'], rec['kind'], rec['mask'], cond)}
    return g


def pt_ref_getter(prefix):
    def g(pid):
        vid = ('E206|' + pid) if prefix == 'E206A' else f'{prefix}|{pid}'
        e = EPID.get(vid)
        if e is None:
            notes.append(f'{prefix} {pid}: reference point not in MM1-v3\'s energy records')
            return None
        cond = conditions_pt(e)
        return {'W_meas': e['w'], 'fc': forecast(f'{prefix}|{pid}', e['card'], e['arm'], e['fmt'], e['kind'], e['mask'], cond)}
    return g


def finish(row, Wm, Prest, fc, cond, R, Z):
    row.update({'f_mhz': cond['f'], 'V': cond['V'], 'die_c': cond['T0'], 't_meas_us': cond['t'], 'W_meas': Wm, 'P_rest': Prest,
                't_fc_us': fc['t_fc']})
    for m in MODELS:
        if m in fc:
            row[f'W_{m}'] = fc[m]
            row[f'e1_{m}'] = q1(fc[m], Wm)
            row[f'dW_low_{m}'] = (fc[m] - Wm) if Wm < LOW else None
    row['e3_V3'] = (Prest + fc['V3']) / (Prest + Wm) - 1.0 if Prest is not None else None
    row['e4_V3'] = (fc['V3_at_tfc'] * fc['t_fc']) / (Wm * cond['t']) - 1.0 if Wm >= LOW else None
    if R and Z:
        Dw = R['W_meas'] - Z['W_meas']
        row.update({'D_W': Dw, 'W_R': R['W_meas'], 'W_Z': Z['W_meas'], 'n_R': R['n'], 'n_Z': Z['n'], 's_meas': (Wm - Z['W_meas']) / Dw})
        for m in MODELS:
            if m not in fc:
                continue
            base = 'V1' if m == 'V1' else 'V3'
            if base not in R['fc']:
                continue
            row[f'e2_{m}'] = ((fc[m] - R['fc'][base]) - (Wm - R['W_meas'])) / Dw
        row['s_V3'] = row['s_meas'] + row.get('e2_V3', float('nan'))
    else:
        row['share_why'] = 'no in-session random and zeros reference with energy' if not (R and Z) else None


for tid, r in TEST212.items():
    rec = REC[r['session']].get(r['run'])
    row = {'id': tid, 'group': r['group'], 'session': r['session'], 'card': r['card'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
           'priced_as': r['priced_as'], 'mask': r['mask'], 'source': 'E212', 'case': f"{r['card']}|{r['arm']}|{r['fmt']}|{r['kind']}|{r['mask']}",
           'spec_tabulated': r.get('tabulated_by_v3_spec_s02'), 'design_c_printed': r.get('printed_by_v3_design_c_ana1')}
    if rec is None or 'w' not in rec:
        row['not_scored'] = (rec or {}).get('why') or 'not in the data'
        rows.append(row)
        continue
    cond = conditions_e212(rec)
    fc = forecast(tid, r['card'], r['arm'], r['fmt'], r['priced_as'], r['mask'], cond)
    g = e212_ref_getter(r['session'])
    R = ref_block(r['refs'].get('random', []), g)
    Z = ref_block(r['refs'].get('zeros', []), g)
    row['cfg_t'] = PC.cfg_t({'card': r['card'], 'kernel': 'rgm136', 'arm': r['arm'], 'fmt': r['fmt'], 'mask': r['mask'], 'f': cond['f']})
    finish(row, rec['w'], rec['p_rest'], fc, cond, R, Z)
    rows.append(row)

for grp, key, sub in (('A', 'group_A_pass_rule_pool', 'e206_e207_points'), ('B', 'group_B_reported_phi_only', 'e206_points')):
    for x in DECL['a_runs'][key][sub]:
        prefix = x['id'].split('|')[0]
        vid = ('E206|' + x['point']) if prefix == 'E206A' else x['id']
        e = EPID.get(vid)
        row = {'id': x['id'], 'group': grp, 'session': prefix, 'card': x['card'], 'arm': x['arm'], 'fmt': x['fmt'], 'kind': x['kind'],
               'priced_as': x['priced_as'], 'mask': x['mask'], 'source': prefix, 'case': x['id'], 'design_c_printed': x.get('read_by_v3_design_c_ana2'),
               'spec_tabulated': False, 'n_runs_kept': (e or {}).get('n_runs')}
        if e is None:
            row['not_scored'] = 'not in MM1-v3\'s energy records'
            rows.append(row)
            continue
        assert (e['arm'], e['fmt'], e['kind'], e['card']) == (x['arm'], x['fmt'], x['kind'], x['card']), (vid, e['arm'], e['kind'])
        cond = conditions_pt(e)
        fc = forecast(x['id'], x['card'], x['arm'], x['fmt'], x['priced_as'], x['mask'], cond)
        g = pt_ref_getter(prefix)
        R = ref_block(x['refs'].get('random', []), g)
        Z = ref_block(x['refs'].get('zeros', []), g)
        row['cfg_t'] = PC.cfg_t({'card': x['card'], 'kernel': 'rgm136', 'arm': x['arm'], 'fmt': x['fmt'], 'mask': x['mask'], 'f': cond['f']})
        finish(row, e['w'], e.get('idle_w'), fc, cond, R, Z)
        rows.append(row)
assert xcheck['max_rel'] < 1e-9, xcheck
print('V3 frozen formula = the predictor at each measured condition:', json.dumps(xcheck))

# ---------------------------------------------------------------- cases, stats, the pass rule
for r in rows:
    if 'cfg_t' in r:
        r['twin'] = r['cfg_t'] in fit_cfg
cases = collections.OrderedDict()
for r in rows:
    if r.get('not_scored'):
        continue
    cases.setdefault((r['group'], r['case']), []).append(r)
crow = []
for (grp, case), rs in cases.items():
    c = {'group': grp, 'case': case, 'card': rs[0]['card'], 'arm': rs[0]['arm'], 'fmt': rs[0]['fmt'], 'kind': rs[0]['kind'], 'mask': rs[0]['mask'],
         'source': rs[0]['source'], 'n_runs': len(rs), 'runs': [r['id'] for r in rs], 'twin': all(r.get('twin') for r in rs),
         'spec_tabulated': any(bool(r.get('spec_tabulated')) for r in rs), 'design_c_printed': any(bool(r.get('design_c_printed')) for r in rs),
         'W_meas': float(np.mean([r['W_meas'] for r in rs]))}
    for pre in ('e1_', 'e2_', 'dW_low_'):
        for m in MODELS:
            v = [r.get(pre + m) for r in rs if r.get(pre + m) is not None]
            c[pre + m] = float(np.mean(v)) if v else None
    for k in ('e3_V3', 'e4_V3', 's_meas', 's_V3', 'D_W'):
        v = [r.get(k) for r in rs if r.get(k) is not None and not (isinstance(r.get(k), float) and math.isnan(r.get(k)))]
        c[k] = float(np.mean(v)) if v else None
    crow.append(c)


def st(es):
    es = [e for e in es if e is not None and not (isinstance(e, float) and math.isnan(e))]
    if not es:
        return None
    n = len(es)
    return {'n': n, 'rms_pct': round(100 * math.sqrt(sum(e * e for e in es) / n), 3), 'mean_pct': round(100 * sum(es) / n, 3)}


def binom_two_sided(k, n):
    if n == 0:
        return 1.0
    lo = min(k, n - k)
    p = sum(math.comb(n, i) for i in range(0, lo + 1)) / 2 ** n
    return min(1.0, 2 * p)


def head(cs, q, m, base='V3', tie=0.01):
    pairs = [(c[f'{q}_{base}'], c[f'{q}_{m}']) for c in cs if c.get(f'{q}_{base}') is not None and c.get(f'{q}_{m}') is not None]
    a = [x for x, _ in pairs]
    b = [y for _, y in pairs]
    k = n = ties = 0
    for x, y in pairs:
        d = abs(y) - abs(x)
        if abs(d) < tie:
            ties += 1
            continue
        n += 1
        k += d > 0
    sa, sb = st(a), st(b)
    return {'n_cases': len(pairs), f'{base}': sa, m: sb, 'rms_lower': (sa['rms_pct'] < sb['rms_pct']) if sa and sb else None,
            f'{base}_closer': k, f'{m}_closer': n - k, 'ties': ties, 'non_tied': n, 'p_two_sided': binom_two_sided(k, n),
            'sign_holds': (n >= 6 and binom_two_sided(k, n) < 0.05 and k > n - k), 'too_few': n < 6}


def rule(cs, m):
    h1 = head(cs, 'e1', m)
    h2 = head(cs, 'e2', m)
    P = {'P1': h1['rms_lower'], 'P2': h1['sign_holds'], 'P3': h2['rms_lower'], 'P4': h2['sign_holds']}
    if h1['too_few'] or h2['too_few']:
        v = 'NOT DECIDED'
    elif all(P.values()):
        v = 'PASS'
    else:
        v = 'FAIL (' + ', '.join(k for k, x in P.items() if not x) + ')'
    return {'verdict': v, 'conditions': P, 'Q1': h1, 'Q2': h2}


A_cases = [c for c in crow if c['group'] == 'A']
verdict = rule(A_cases, 'N')
reported = {'against_N2': rule(A_cases, 'N2'),
            'against_V1_where_it_applies': rule([c for c in A_cases if c.get('e1_V1') is not None or c.get('e2_V1') is not None], 'V1'),
            'E212_alone_against_N': rule([c for c in A_cases if c['source'] == 'E212'], 'N'),
            'E206_E207_alone_against_N': rule([c for c in A_cases if c['source'] != 'E212'], 'N'),
            'V3phi1_against_N': {'Q1': head(A_cases, 'e1', 'N', base='V3phi1'), 'Q2': head(A_cases, 'e2', 'N', base='V3phi1')},
            'V3_against_V3phi1': {'Q1': head(A_cases, 'e1', 'V3phi1'), 'Q2': head(A_cases, 'e2', 'V3phi1')}}


def block(cs, rs):
    out = {}
    for m in MODELS:
        out[m] = {'Q1_cases': st([c.get('e1_' + m) for c in cs]), 'Q2_cases': st([c.get('e2_' + m) for c in cs]),
                  'Q1_runs': st([r.get('e1_' + m) for r in rs]), 'Q2_runs': st([r.get('e2_' + m) for r in rs])}
    out['V3']['Q3_J_at_rest_given_t_runs'] = st([r.get('e3_V3') for r in rs])
    out['V3']['Q4_J_over_idle_t_forecast_runs'] = st([r.get('e4_V3') for r in rs])
    out['n_cases'] = len(cs)
    out['n_runs'] = len(rs)
    return out


scored = [r for r in rows if not r.get('not_scored')]
groups = {}
for g in ('A', 'B', 'C'):
    cs = [c for c in crow if c['group'] == g]
    rs = [r for r in scored if r['group'] == g]
    groups[g] = {'all': block(cs, rs)}
    for key in ('card', 'fmt', 'source'):
        for val in sorted({c[key] for c in cs}):
            groups[g][f'{key}={val}'] = block([c for c in cs if c[key] == val], [r for r in rs if r[key] == val])
    for lab, fn in (('twin', lambda c: c['twin']), ('new configuration', lambda c: not c['twin']),
                    ('tabulated by an MM1-v3 design/spec lane', lambda c: c['spec_tabulated'] or c['design_c_printed']),
                    ('not tabulated by any MM1-v3 design/spec lane', lambda c: not (c['spec_tabulated'] or c['design_c_printed']))):
        sub = [c for c in cs if fn(c)]
        ids = {i for c in sub for i in c['runs']}
        groups[g][lab] = block(sub, [r for r in rs if r['id'] in ids])
res = {'label': ('UNREAD: MM1-v3 frozen (b1493082) and the switch counts frozen (SHA256SUMS c74c2d49...) before this read; not blind (the data '
                 'existed; data lanes and some MM1-v3 design lanes had read them; declaration section g)'),
       'start_pst': start, 'end_pst': None, 'interpreter': sys.version.split()[0], 'numpy': np.__version__,
       'declaration_sha256': sha(DECL_P), 'forecasts_sha256': sha(FC_P), 'lab_commit': COMMIT, 'sources': src_check,
       'e212_loader_check': loader_check, 'v3_formula_vs_predictor': xcheck, 'mm1_v3_priced_configurations': len(fit_cfg),
       'n_runs_listed': len(rows), 'n_not_scored': sum(1 for r in rows if r.get('not_scored')),
       'not_scored': {r['id']: r['not_scored'] for r in rows if r.get('not_scored')}, 'notes': notes,
       'VERDICT': verdict['verdict'], 'pass_rule_against_N': verdict, 'reported': reported, 'groups': groups}
res['end_pst'] = ts()
json.dump(res, open(os.path.join(OUTD, 'scores-unread.json'), 'w'), indent=1, sort_keys=True, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
rf = ['id', 'group', 'source', 'session', 'card', 'arm', 'fmt', 'kind', 'priced_as', 'mask', 'not_scored', 'f_mhz', 'V', 'die_c', 't_meas_us', 't_fc_us',
      'W_meas', 'P_rest', 'W_V3', 'W_N', 'W_N2', 'W_V3phi1', 'W_V1', 'e1_V3', 'e1_N', 'e1_N2', 'e1_V3phi1', 'e1_V1', 'dW_low_V3', 'D_W', 'W_R', 'W_Z',
      'n_R', 'n_Z', 's_meas', 's_V3', 'e2_V3', 'e2_N', 'e2_N2', 'e2_V3phi1', 'e2_V1', 'e3_V3', 'e4_V3', 'twin', 'spec_tabulated', 'design_c_printed',
      'share_why', 'n_runs_kept']
with open(os.path.join(OUTD, 'scores-unread-runs.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=rf, lineterminator='\n', extrasaction='ignore')
    w.writeheader()
    for r in rows:
        w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})
cf = ['group', 'case', 'source', 'card', 'arm', 'fmt', 'kind', 'mask', 'n_runs', 'W_meas', 'D_W', 's_meas', 's_V3', 'e1_V3', 'e1_N', 'e1_N2',
      'e1_V3phi1', 'e1_V1', 'e2_V3', 'e2_N', 'e2_N2', 'e2_V3phi1', 'e2_V1', 'e3_V3', 'e4_V3', 'twin', 'spec_tabulated', 'design_c_printed']
with open(os.path.join(OUTD, 'scores-unread-cases.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=cf, lineterminator='\n', extrasaction='ignore')
    w.writeheader()
    for c in crow:
        w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()})
for fn in ('scores-unread.json', 'scores-unread-runs.csv', 'scores-unread-cases.csv'):
    print(sha(os.path.join(OUTD, fn)), fn)
print('VERDICT', verdict['verdict'], json.dumps(verdict['conditions']))
print('Q1 vs N', json.dumps(verdict['Q1']))
print('Q2 vs N', json.dumps(verdict['Q2']))
for k, v in reported.items():
    if 'verdict' in v:
        print('REPORTED', k, v['verdict'], json.dumps({q: {kk: v[q][kk] for kk in v[q] if kk in ('n_cases', 'V3', 'N', 'N2', 'V1', 'V3_closer', 'non_tied', 'p_two_sided')} for q in ('Q1', 'Q2')}))
print('not scored', json.dumps(res['not_scored']))
print('notes', len(notes), notes[:5])
