#!/usr/bin/env python3
"""lnc-form step 1: every committed rgm136 gemmLnc energy point through E219 and its cooperative gemmL twin, with MM1-v3.2's base
(E1t at MM1-v3.2's all-data constants, F3 removed) given the measured op time, F3 at MM1-v3.2's constants, and the map's level shares.
Desk; reads committed files only (a git-archive copy of LAB's tools/ at main 0f046200 and LAB's committed data folders, read only).

Points:
  - in MM1-v3.2's fit (E211, E213 both arms, E215 both arms): out/points_energy_v32.csv rows with gemmLnc = 1, and the gemmL row of the
    same experiment, card, token, format, kind and mask as the twin (when one exists);
  - E216 (aifoundry2 card 0, governed, 799 MHz): data-e216.json (E208's reducer, primary view 'win'), route c as E216.md section 7 reads
    it: a run of the point (role 'arm') whose win-view clock reads 790-810 MHz, not capped, with dP_w; checked against the frozen scorer's
    measured_route_c W and op time (scored-e216.json); V the win view's minion mV, f its clock, G = G_of_f(card, f), die = die_start_c;
  - E218 (aifoundry3 card 0, 600 MHz): data-e218.json in E215's form, read with E215's rule (data_v32.e215_runs's conditions): a run is
    kept when its record equals the registered point, its walk and identity gate are good (rgm211's host), and it has t_gemm_s, p_work_w,
    p_rest_w and cycles_gemm; W = mean(p_work - p_rest), T = mean(cycles_gemm / ops) / 600, V = 0.522 (MM1's aifoundry3 footing).
  - E217 and E219 hold no gemmLnc arm (E217's and E219's hosts cannot run it): checked by a scan of their registrations' arm lists.
"""
import csv
import json
import os
import sys

import numpy as np

L = os.environ['LNC_FORM_DIR']
REPO = os.path.join(L, 'work', 'repo')
LAB = os.environ['LAB_DIR']
V32 = os.path.join(REPO, 'tools', 'matmul', 'mm1', 'v3.2')
sys.path.insert(0, V32)
import mm1_v32  # noqa: E402

C = mm1_v32.C
P = json.load(open(os.path.join(V32, 'out', 'mm1_v32_params.json')))
M = mm1_v32.Model(P)
C1 = P['energy']['F3']['c1_pJ']
C2 = P['energy']['F3']['c2_pJ']
OUT = os.path.join(L, 'work', 's01_points.json')


def shape(tok):
    import re
    m = re.match(r'gemmL(?:nc)?(\d+)x(\d+)x(\d+)$', tok)
    return tuple(int(x) for x in m.groups())


# ------------------------------------------------------------------ in-fit points
rows = list(csv.DictReader(open(os.path.join(V32, 'out', 'points_energy_v32.csv'))))
trows = {r['id']: r for r in csv.DictReader(open(os.path.join(V32, 'out', 'points_time_v32.csv')))}
pts = []
for r in rows:
    if r['gemmLnc'] != '1':
        continue
    tok = r['arm']
    twin_tok = tok.replace('gemmLnc', 'gemmL')
    tw = [q for q in rows if q['exp'] == r['exp'] and q['card'] == r['card'] and q['arm'] == twin_tok and q['fmt'] == r['fmt']
          and q['kind'] == r['kind'] and q['mask'] == r['mask'] and q['kernel'] == 'rgm136']
    pts.append({'id': r['id'], 'exp': r['exp'], 'card': r['card'], 'arm': tok, 'fmt': r['fmt'], 'kind': r['kind'], 'mask': r['mask'],
                'f': 600.0, 'T': float(r['meas_T_us']), 'w': float(r['meas_W_over_idle']), 'idle_w': float(r['idle_W']),
                'die': float(r['die_start_c']) if r['die_start_c'] else None, 'V': float(r['V']) if r['V'] else None, 'G': 0.0,
                'v32_alldata_csv': float(r['v32_all_data_W_given_t']), 'v32_LOEO_csv': float(r['v32_LOEO_W_given_t']),
                'twin': ({'id': tw[0]['id'], 'arm': twin_tok, 'T': float(tw[0]['meas_T_us']), 'w': float(tw[0]['meas_W_over_idle']),
                          'die': float(tw[0]['die_start_c']) if tw[0]['die_start_c'] else None,
                          'V': float(tw[0]['V']) if tw[0]['V'] else None, 'v32_alldata_csv': float(tw[0]['v32_all_data_W_given_t']),
                          'v32_LOEO_csv': float(tw[0]['v32_LOEO_W_given_t'])} if tw else None),
                'source': 'tools/matmul/mm1/v3.2/out/points_energy_v32.csv'})

# ------------------------------------------------------------------ E216 (aifoundry2 card 0, route c)
D16 = os.path.join(LAB, 'docs', 'reports', 'data', '2026-11-19-e216-blind-matmul-aifoundry2')
d16 = json.load(open(os.path.join(D16, 'data-e216.json')))
s16 = json.load(open(os.path.join(D16, 'scored-e216.json')))['points']
reg16 = {r['id']: r for r in csv.DictReader(open(os.path.join(REPO, 'tools', 'claims-v3', 'e216', 'points-e216.csv')))}


def e216_point(pid):
    rg = reg16[pid]
    runs = []
    for r in d16['runs']:
        if r.get('arm') != pid or not r.get('ran') or r.get('role') != 'arm':
            continue
        v = (r.get('views') or {}).get('win') or {}
        if r.get('capped') or v.get('dP_w') is None or not v.get('T_op_us'):
            continue
        if not (790.0 <= float(v['kclock_mhz']) <= 810.0):
            continue
        if any('STEP' in str(fl) for fl in (r.get('flags') or [])):
            continue
        runs.append((r, v))
    mr = s16[pid]['measured_route_c']
    w = float(np.mean([v['dP_w'] for _, v in runs]))
    T = float(np.mean([v['T_op_us'] for _, v in runs]))
    chk = {'scorer_W': mr.get('W'), 'scorer_T_op': mr.get('T_op_e', mr.get('T_op')), 'mine_W': w, 'mine_T': T, 'n_runs': len(runs),
           'scorer_n_energy': mr.get('n_energy')}
    mv = [((v.get('rails') or {}).get('minion') or {}).get('mV') for _, v in runs]
    mv = [float(x) for x in mv if x is not None]
    f = float(np.mean([v['kclock_mhz'] for _, v in runs]))
    return {'id': 'E216|a2c0|' + pid, 'pid': pid, 'exp': 'E216', 'card': 'aifoundry2 card 0', 'arm': rg['arm'], 'fmt': rg['fmt'],
            'kind': rg['kind'], 'mask': rg['mask'], 'f': f, 'T': T, 'w': w,
            'idle_w': float(np.mean([v['p_mean_w'] - v['dP_w'] for _, v in runs])),
            'die': float(np.mean([r['die_start_c'] for r, _ in runs if r.get('die_start_c') is not None])),
            'V': (float(np.mean(mv)) / 1000.0 if mv else None), 'G': float(C.G_of_f('aifoundry2 card 0', f)), 'check_vs_scorer': chk,
            'runs': [r['run'] for r, _ in runs], 'source': 'docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/data-e216.json'}


for pid in ['g%02d' % i for i in range(1, 11)]:
    p = e216_point(pid)
    tw = e216_point(pid + 't')
    p['twin'] = {k: tw[k] for k in ('id', 'arm', 'T', 'w', 'die', 'V', 'f', 'G', 'check_vs_scorer', 'runs')}
    pts.append(p)

# ------------------------------------------------------------------ E218 (aifoundry3 card 0, E215's form)
D18 = os.path.join(LAB, 'docs', 'reports', 'data', '2026-11-20-e218-blind-matmul-aifoundry3')
d18 = json.load(open(os.path.join(D18, 'data-e218.json')))['arms']['A']['points']
reg18 = {r['id']: r for r in csv.DictReader(open(os.path.join(REPO, 'tools', 'claims-v3', 'e218', 'points-e218.csv')))}


def e218_point(pid):
    rg = reg18[pid]
    ops = int(rg['ops_per_minion_per_gemm'])
    kept = []
    for r in d18[pid]['runs']:
        rec = r.get('record') or {}
        if (str(rec.get('arm')) != rg['arm'] or str(rec.get('type')) != rg['format'] or str(rec.get('minions')) != rg['minions']
                or int(str(rec.get('shire_mask')), 16) != int(rg['shire_mask'], 16)):
            continue
        if rg['host'] == 'rgm211':
            wk = r.get('walk') or {}
            if not (wk.get('ok') and all(wk['ok']) and wk.get('launches_bad') == 0 and str(r.get('gate', '')).startswith('GATE OK')):
                continue
        if not (r.get('t_gemm_s') and r.get('p_work_w') is not None and r.get('p_rest_w') is not None and r.get('cycles_gemm')):
            continue
        kept.append(r)
    cw = float(np.mean([r['cycles_gemm'] / ops for r in kept]))
    return {'id': 'E218|a3|' + pid, 'pid': pid, 'exp': 'E218', 'card': 'aifoundry3 card 0', 'arm': rg['arm'], 'fmt': rg['format'],
            'kind': rg['kind'], 'mask': rg['shire_mask'], 'f': 600.0, 'T': cw / 600.0,
            'w': float(np.mean([r['p_work_w'] - r['p_rest_w'] for r in kept])), 'idle_w': float(np.mean([r['p_rest_w'] for r in kept])),
            'die': float(np.mean([r['die_start_c'] for r in kept])), 'V': 0.522, 'G': 0.0, 'n_runs': len(kept),
            'runs': [r.get('n') for r in kept], 'source': 'docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json'}


for pid in ['g%02d' % i for i in range(1, 13)]:
    p = e218_point(pid)
    twid = reg18[pid]['twin']
    if twid and twid in d18:
        tw = e218_point(twid)
        p['twin'] = {k: tw[k] for k in ('id', 'arm', 'T', 'w', 'die', 'V', 'f', 'G', 'n_runs')}
    else:
        p['twin'] = None
    pts.append(p)


# ------------------------------------------------------------------ MM1-v3.2 at every point and twin
def spec(p, arm=None, T=None, die=None, V=None):
    return {'card': p['card'], 'arm': arm or p['arm'], 'fmt': p['fmt'], 'kind': p['kind'], 'mask': p['mask'], 'f': p['f'],
            'kernel': 'rgm136', 't0_c': die if die is not None else p['die'], 'V': V if V is not None else p['V'],
            'G': p['G']}


specs = []
for p in pts:
    specs.append(spec(p))
    if p.get('twin'):
        tw = p['twin']
        specs.append(spec(p, arm=tw['arm'], die=tw['die'], V=tw['V']))
pr = M.predict_many(specs)
k = 0
for p in pts:
    o = pr[k]
    k += 1
    A, B = o['W_affine']['A_W'], o['W_affine']['B_W_us']
    Wv = A + B / p['T']
    f3_own = o['F3_W_at_own_t']
    f3 = f3_own * o['T_op_us'] / p['T']
    S = f3 / (C1 * o['F3_dup'] + C2 * o['F3_first'])          # D sL n / t x 1e-12, W per pJ a minion-op, at the measured t
    Q = 0.5 * (np.array(o['Q0']) + np.array(o['Q1']))
    qA, qB = Q.sum(axis=1), Q.sum(axis=0)
    MB, NB, KB = shape(p['arm'])
    p.update({'MB': MB, 'NB': NB, 'KB': KB, 'v32_W_given_t': Wv, 'v32_F3_W': f3, 'base_W': Wv - f3, 'S': S,
              'first': o['F3_first'], 'dup': o['F3_dup'], 'qA_L2_L3_F': qA.tolist(), 'qB_L2_L3_F': qB.tolist(),
              'v32_T_pred_us': o['T_op_us'], 'footprint_MB': o['footprint_MB'], 'lines_L2_L3_F_per_shire_op': o['lines_L2_L3_F_per_shire_op'],
              'e_meas_pJ': (p['w'] - (Wv - f3)) / S, 'e_F3_v32_pJ': C1 * o['F3_dup'] + C2 * o['F3_first']})
    if 'v32_alldata_csv' in p:
        p['check_v32_vs_csv'] = Wv - p['v32_alldata_csv']
    if p.get('twin'):
        o2 = pr[k]
        k += 1
        tw = p['twin']
        Wt = o2['W_affine']['A_W'] + o2['W_affine']['B_W_us'] / tw['T']
        tw.update({'v32_W_given_t': Wt, 'v32_T_pred_us': o2['T_op_us'], 'F3_W_at_own_t': o2['F3_W_at_own_t']})
        if 'v32_alldata_csv' in tw:
            tw['check_v32_vs_csv'] = Wt - tw['v32_alldata_csv']
json.dump({'points': pts, 'C1': C1, 'C2': C2, 'params': 'tools/matmul/mm1/v3.2/out/mm1_v32_params.json'}, open(OUT, 'w'), indent=1)

print('%-22s %-15s %-17s %5s %7s %7s %7s %7s %7s %6s %6s %6s | %6s %6s %6s %6s' % (
    'id', 'card', 'arm', 'f', 'W', 'v32', 'base', 'e_meas', 'e_F3', 'err%', 'Tm/Tp', 'tw', 'twW', 'twv32', 'twT', 'chk'))
for p in pts:
    tw = p.get('twin') or {}
    err = 100 * (p['v32_W_given_t'] / p['w'] - 1)
    twr = (tw.get('w') / tw.get('v32_W_given_t')) if tw else float('nan')
    twT = (p['T'] / tw['T']) if tw else float('nan')
    print('%-22s %-15s %-17s %5.0f %7.2f %7.2f %7.2f %7.0f %7.0f %6.1f %6.3f %6.3f | %6.2f %6.2f %6.3f %8.1e' % (
        p['id'][:22], p['card'][:15], p['arm'], p['f'], p['w'], p['v32_W_given_t'], p['base_W'], p['e_meas_pJ'], p['e_F3_v32_pJ'], err,
        p['T'] / p['v32_T_pred_us'], twr, tw.get('w', float('nan')), tw.get('v32_W_given_t', float('nan')), twT,
        p.get('check_v32_vs_csv', 0.0)))
for p in pts:
    if p['exp'] == 'E216':
        print(p['pid'], p['check_vs_scorer'], (p['twin'] or {}).get('check_vs_scorer'))
