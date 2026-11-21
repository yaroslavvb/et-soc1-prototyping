#!/usr/bin/env python3
"""mask-posimb (Q238) h02: 'MM1-v3.2 + AF4 + posimb-mask' BY CONSTRUCTION, no refit (DECLARED-posimb-mask.md section 8), shown on E222's 70
and E224's 127 registered points at their registered clocks (E222 aifoundry3 card 0 at 600 MHz; E224 arm A aifoundry1 card 1 at 600 MHz, arm B
aifoundry2 card 0 at 799, 700 and 600 MHz) through the frozen module (land/.../posimb_mask.py, staged at its repository path in the lane's
clone): per row the one term that acts (exit 5 if both act or one moves a row outside its scope); the module's 'MM1-v3.2' and 'MM1-v3.2 + AF4'
compared with E222's and E224's registered frozen forecasts (tools/claims-v3/e222/forecast-e222.json, e224/forecast-e224.json). POST HOC
(those points' data are in the fit): REPORTED, not a forecast. Desk; numpy; single-threaded.
Output (land): forecasts-compose-e222-e224.json and .csv."""
import csv
import hashlib
import json
import os
import shutil
import sys

LANE = os.environ['MASKPOS_LANE']
LAB = os.path.join(LANE, 'work/lab')
LAND = os.path.join(LANE, 'land/tools/matmul/mm1/v3.4-cands/posimb-mask')
STAGE = os.path.join(LAB, 'tools/matmul/mm1/v3.4-cands/posimb-mask')
CV3 = os.path.join(LAB, 'tools/claims-v3')
if os.path.isdir(STAGE):
    shutil.rmtree(STAGE)
shutil.copytree(LAND, STAGE, ignore=shutil.ignore_patterns('forecasts-compose-*'))
sys.path.insert(0, STAGE)
import posimb_mask as PM  # noqa: E402

MODELS = ('MM1-v3.2', 'MM1-v3.2 + AF4', PM.LABEL, PM.LABEL_AF4)
Q = ('T_op_us', 'cycles_per_op_wall', 'cycles_per_op_mean', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm',
     'J_at_rest_per_gemm')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rel(a, b):
    if a is None or b is None:
        return None
    return abs(a - b) / max(abs(a), abs(b), 1e-300)


def main():
    M = PM.Model()
    jobs = []
    F2 = json.load(open(os.path.join(CV3, 'e222/forecast-e222.json')))
    for pid, x in sorted(F2['points'].items()):
        jobs.append(('E222', '-', F2['card'], float(F2['f_mhz']), pid, x['token'], x['fmt'], x['kind'], x['mask'], x['models']))
    F4 = json.load(open(os.path.join(CV3, 'e224/forecast-e224.json')))
    cards4 = {'A': 'aifoundry1 card 1', 'B': 'aifoundry2 card 0'}
    for arm in ('A', 'B'):
        for pid, x in sorted(F4['arms'][arm]['points'].items()):
            for col, mods in sorted(x['clocks'].items()):
                jobs.append(('E224', arm, cards4[arm], float(col), pid, x['token'], x['format'], x['kind'], x['mask'], mods))
    rows, worst, bad = [], {'MM1-v3.2': 0.0, 'MM1-v3.2 + AF4': 0.0}, []
    acting = {'posimb-mask alone (AF4 equals MM1-v3.2 here)': 0, 'AF4 alone (posimb-mask equals MM1-v3.2 here)': 0, 'MM1-v3.2 (no term acts)': 0}
    groups = {}
    for j in jobs:
        groups.setdefault((j[2], j[3]), []).append(j)
    for (card, f), js in sorted(groups.items()):
        specs = [{'card': card, 'arm': j[5], 'fmt': j[6], 'kind': j[7], 'mask': j[8], 'f': f, 'kernel': 'rgm136'} for j in js]
        try:
            R = M.predict_many_with_af4(specs)
        except SystemExit:
            raise
        except Exception as ex:  # noqa: BLE001
            R = []
            for s in specs:
                try:
                    R.append(M.predict_many_with_af4([s])[0])
                except SystemExit:
                    raise
                except Exception as ex2:  # noqa: BLE001
                    R.append({'error': repr(ex2)})
        for j, s, r in zip(js, specs, R):
            exp, arm, _, _, pid, tok, fmt, kind, mask, frozen = j
            row = {'exp': exp, 'arm': arm, 'card': card, 'f_mhz': f, 'id': pid, 'token': tok, 'format': fmt, 'kind': kind, 'mask': mask}
            if 'error' in r:
                row['error'] = r['error']
                bad.append(row)
                rows.append(row)
                continue
            row.update({'in_scope_posimb_mask': int(r['in_scope']), 'in_scope_AF4': int(r['MM1-v3.2 + AF4']['in_scope']), 'how': r[PM.LABEL_AF4]['how'],
                        'e': r['term']['e'], 'A1': r['term'].get('A1'), 'g_wall': r['term']['g_wall'], 'g_mean': r['term']['g_mean']})
            acting[r[PM.LABEL_AF4]['how']] += 1
            for m in MODELS:
                for q in Q:
                    row['%s|%s' % (m, q)] = r[m].get(q)
            for m in ('MM1-v3.2', 'MM1-v3.2 + AF4'):
                fz = frozen.get(m) or {}
                for q in ('T_op_us', 'cycles_per_op_wall', 'seconds_per_gemm', 'W_over_idle', 'A_W', 'B_W_us', 'J_over_idle_per_gemm'):
                    d = rel(r[m].get(q), fz.get(q))
                    if d is not None:
                        worst[m] = max(worst[m], d)
                        if d > 1e-9:
                            bad.append({'id': pid, 'exp': exp, 'arm': arm, 'f': f, 'model': m, 'q': q, 'mine': r[m].get(q), 'frozen': fz.get(q)})
            rows.append(row)
    import collections
    by = dict(collections.Counter('%s %s %s' % (r['exp'], r['arm'], r['f_mhz']) for r in rows))
    print('rows by exp, arm, clock', by)
    out = {'what': 'MM1-v3.2 + AF4 + posimb-mask by construction (no refit), on E222 and E224 registered points; POST HOC, REPORTED', 'rows_by_exp_arm_clock': by,
           'module_sha256': sha(os.path.join(LAND, 'posimb_mask.py')), 'params_sha256': sha(os.path.join(LAND, 'params-posimb-mask.json')),
           'forecast_e222_sha256': sha(os.path.join(CV3, 'e222/forecast-e222.json')), 'forecast_e224_sha256': sha(os.path.join(CV3, 'e224/forecast-e224.json')),
           'rows': rows, 'n_rows': len(rows), 'acting': acting,
           'max_rel_diff_vs_registered_frozen': worst, 'differences_over_1e-9': bad[:50], 'n_differences_over_1e-9': len(bad)}
    json.dump(out, open(os.path.join(LAND, 'forecasts-compose-e222-e224.json'), 'w'), indent=1)
    cols = list(rows[0].keys())
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(os.path.join(LAND, 'forecasts-compose-e222-e224.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('rows', len(rows), 'acting', acting)
    print('max rel diff vs the registered frozen forecasts', worst, 'differences over 1e-9:', len(bad), bad[:5])


if __name__ == '__main__':
    main()
