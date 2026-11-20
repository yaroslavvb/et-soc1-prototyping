#!/usr/bin/env python3
"""Lane l3-edge (Q234): the frozen forecasts of 'MM1-v3.2 + L3S' (DECLARED-l3s.md section 7) for every point of E220 in reg-e220's
POINTS.txt (read for its points only; no E220 datum exists or is opened), at the all-data lam of fit-l3s.json, with MM1-v3.2 beside
(the same predictor call: card = the arm's card, arm = token, fmt, kind = random, mask, f = the clock, kernel = rgm136; V, G, t0_c,
minions, ops not given, as POINTS.txt says). Arm A at 600 MHz; arm B at 799 MHz with 700 and 600 MHz columns.
Writes <land>/forecasts-e220-l3s.csv and .json. Desk; numpy.
"""
import csv
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import term_l3s as TL  # noqa: E402

M, E, CO = TL.M, TL.E, TL.CO
POINTS = os.environ['E220_POINTS_TXT']   # reg-e220's POINTS.txt, sha256 058984a04b90cd8585cb41cc6618430306d7bf1c7e230159e7719b9e9e1e9bdc
LAND = os.path.join(HERE, '..')
fit = json.load(open(os.path.join(HERE, '..', 'out', 'fit', 'fit-l3s.json')))
lam = float(fit['lam_all'])
label = 'MM1-v3.2 + L3S' + ('' if fit['kept'] else ' (rejected candidate)')
P = json.load(open(os.path.join(CO.V32, 'out/mm1_v32_params.json')))
cache = TL.load_cache()
base = M.Model(P)
cand = TL.ModelL3S(P, lam, cache)
pts_sha = hashlib.sha256(open(POINTS, 'rb').read()).hexdigest()
rows = []
for line in open(POINTS):
    if not (line.startswith('A\t') or line.startswith('B\t')):
        continue
    c = line.rstrip('\n').split('\t')
    arm, cardn, f0, pid, fam, sub, tok, fmt, kind, mask = c[:10]
    clocks = [float(f0)] if arm == 'A' else [799.0, 700.0, 600.0]
    for f in clocks:
        rows.append({'arm': arm, 'card': cardn, 'id': pid, 'family': fam, 'subfamily': sub, 'token': tok, 'format': fmt, 'kind': kind,
                     'mask': mask, 'f_mhz': f, 'registered_clock': f == float(f0)})
specs = [{'card': r['card'], 'arm': r['token'], 'fmt': r['format'], 'kind': r['kind'], 'mask': r['mask'], 'f': r['f_mhz'], 'kernel': 'rgm136'}
         for r in rows]
out_b = base.predict_many(specs)
out_c = cand.predict_many(specs)
dom, fsa = TL.features([{'arm': s['arm'], 'kernel': ('rgm211' if E.arm_parts(s['arm'])[0] == 'gemmLn' else 'rgm136'), 'mask': s['mask'],
                         'fmt': s['fmt'], 'f': s['f']} for s in specs], cache)
FIELDS = ['T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
          'J_at_rest_per_gemm_REPORTED', 'P_rest_W_REPORTED']


def flat(o):
    d = {k: o.get(k) for k in ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'W_over_idle', 'J_over_idle_per_gemm')}
    wa = o.get('W_affine') or {}
    d['A_W'] = wa.get('A_W')
    d['B_W_us'] = wa.get('B_W_us')
    rl = o.get('rest_law') or {}
    d['J_at_rest_per_gemm_REPORTED'] = rl.get('J_at_rest_per_gemm_REPORTED')
    d['P_rest_W_REPORTED'] = rl.get('P_rest_W')
    if isinstance(o.get('energy'), str):
        d['energy_note'] = o['energy']
    return d


recs = []
for j, r in enumerate(rows):
    fb, fc = flat(out_b[j]), flat(out_c[j])
    rec = dict(r)
    rec['in_L3S_domain'] = bool(dom[j])
    rec['set_model_A_fresh_share'] = [None, None] if not dom[j] else [float(fsa[j][0]), float(fsa[j][1])]
    rec['lines_L2_L3_F_per_shire_op'] = {'MM1-v3.2': out_b[j]['lines_L2_L3_F_per_shire_op'], label: out_c[j]['lines_L2_L3_F_per_shire_op']}
    rec['models'] = {'MM1-v3.2': fb, label: fc}
    recs.append(rec)
final = time.strftime('%Y-%m-%d %H:%M:%S %Z')
meta = {'what': "E220's frozen forecasts of %s (lam %.9f, all-data fit of DECLARED-l3s.md) and MM1-v3.2 beside" % (label, lam),
        'declaration_sha256': fit['declaration_sha256'], 'fit_verdict': fit['verdict'], 'lam_all': lam, 'points_txt_sha256': pts_sha,
        'points_txt': 'reg-e220 POINTS.txt (final 05:24:17 PST); no E220 datum opened', 'final_pst': final,
        'units': 'T_op_us us an op (the slowest minion); cycles an op; seconds a GEMM; W over idle at the forecast t; A_W + B_W_us / t = W given a '
                 'measured t (us); J a GEMM; J at rest with the rest law REPORTED as MM1-v3.2 reports it',
        'interpreter': '/usr/bin/python3 %s' % sys.version.split()[0], 'n_rows': len(recs)}
json.dump({'meta': meta, 'rows': recs}, open(os.path.join(LAND, 'forecasts-e220-l3s.json'), 'w'), indent=1, default=float)
with open(os.path.join(LAND, 'forecasts-e220-l3s.csv'), 'w', newline='') as fo:
    w = csv.writer(fo)
    w.writerow(['arm', 'card', 'id', 'family', 'token', 'format', 'mask', 'f_mhz', 'registered_clock', 'in_L3S_domain', 'model'] + FIELDS)
    for rec in recs:
        for mname, d in rec['models'].items():
            w.writerow([rec['arm'], rec['card'], rec['id'], rec['family'], rec['token'], rec['format'], rec['mask'], rec['f_mhz'],
                        int(rec['registered_clock']), int(rec['in_L3S_domain']), mname] + [('' if d.get(k) is None else repr(float(d[k]))) for k in FIELDS])
print(json.dumps(meta, indent=1))
