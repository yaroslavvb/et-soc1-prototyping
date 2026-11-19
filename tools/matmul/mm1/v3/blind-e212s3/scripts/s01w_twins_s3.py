#!/usr/bin/env python3
"""blind-v3-e212s3 step 1 (desk, before any S3 datum): the registered a2c0-S3 schedule's 46 non-null arms against MM1-v3's frozen S3
forecast rows (out/mm1_v3_e212_s3s4.csv, b1493082), each arm's case key as MM1-v3's loader will form it (data_v3.e212_kind), and its
configuration-twin flags against MM1-v3's frozen fit data (postcheck_v3.cfg_t / cfg_e), at the 799-800 MHz the forecast assumes (the
scorer re-decides each flag at the case's measured clock, to 25 MHz). Reads no S3 datum (none exists).

    /usr/bin/python3 -I -B s01w_twins_s3.py --v3 <tools/matmul/mm1/v3 from b1493082> --sched <claims-v3/e212/proposal/src/sched/a2c0-S3.json> --out <file.json>
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v3', required=True)
    ap.add_argument('--sched', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    V3 = os.path.abspath(a.v3)
    sys.path.insert(0, V3)
    import data_v3 as D  # noqa: E402
    import energy_v3 as EN  # noqa: E402
    import postcheck_v3 as PC  # noqa: E402
    sched = json.load(open(a.sched))
    runs = sched['runs']
    arms = {}
    order = []
    for r in runs:
        if r['role'] == 'null':
            continue
        if r['arm'] not in arms:
            order.append(r['arm'])
            arms[r['arm']] = {'arm_label': r['arm'], 'role': r['role'], 'n_runs': 0, 'type': r['type'], 'shires': r['shires'], 'values': r['values'],
                              'block': r['block'], 'first_i': r['i']}
        arms[r['arm']]['n_runs'] += 1
    lit = {q['arm_label']: q for q in csv.DictReader(open(os.path.join(V3, 'out', 'mm1_v3_e212_s3s4.csv'))) if q['session'] == 'a2c0-S3'}
    P = D.time_points()
    rung = PC.rung_of(P)
    fit_t = {PC.cfg_t(p) for p, rg in zip(P, rung) if not rg}
    EP = D.energy_points()
    XP = EN.Features(EP)
    erung = PC.rung_of(EP)
    fit_e = {PC.cfg_e(e) for e, rg, u in zip(EP, erung, XP.usable3) if u and not rg}
    out = []
    for lab in order:
        x = arms[lab]
        m = re.match(r'gemmL(\d+)x(\d+)x(\d+):', x['values'])
        arm = 'gemmL%sx%sx%s' % m.groups()
        kind = D.e212_kind({'arm': lab})
        q = lit.get(lab)
        rec = dict(x)
        rec.update({'arm': arm, 'fmt': x['type'], 'kind': kind, 'mask': x['shires'], 'forecast_row': q is not None})
        for f in (800.0, 775.0):
            qq = {'card': 'aifoundry2 card 0', 'kernel': 'rgm136', 'arm': arm, 'fmt': x['type'], 'mask': x['shires'], 'f': f, 'kind': kind}
            rec[f'twin_time_{int(f)}'] = PC.cfg_t(qq) in fit_t
            rec[f'twin_energy_{int(f)}'] = PC.cfg_e(qq) in fit_e
        if q:
            rec['row_matches'] = (q['arm'] == arm and q['fmt'] == x['type'] and q['kind'] == kind and q['mask'].lower() == x['shires'].lower())
            for k in ('f_mhz', 'v3_cycles_per_op_wall', 'v3_cycles_per_op_mean', 'v3_A_W', 'v3_B_W_us', 'v3_W_over_idle',
                      'v2_cycles_per_op_wall', 'v2_cycles_per_op_mean', 'v2_A_W', 'v2_B_W_us', 'v2_W_over_idle'):
                rec['frozen_' + k] = q[k]
            rec['energy_forecast'] = q['v3_A_W'] != ''
        out.append(rec)
    cfg_kb = {(r['arm'], r['fmt'], r['mask'].lower()) for r in out}
    res = {'what': ('E212 a2c0-S3: the registered schedule\'s non-null arms, their case keys, MM1-v3\'s frozen forecast rows and the '
                    'configuration-twin flags against MM1-v3\'s frozen fit data (desk, before any S3 datum)'),
           'interpreter': sys.version.split()[0], 'sched_sha256': sha(a.sched), 'forecast_csv_sha256': sha(os.path.join(V3, 'out', 'mm1_v3_e212_s3s4.csv')),
           'n_runs': len(runs), 'n_null': sum(1 for r in runs if r['role'] == 'null'), 'n_anchor_runs': sum(1 for r in runs if r['role'] == 'anchor'),
           'n_arm_runs': sum(1 for r in runs if r['role'] == 'arm'), 'n_arms_nonnull': len(out),
           'arms_without_forecast': [r['arm_label'] for r in out if not r['forecast_row']],
           'forecasts_without_arm': sorted(set(lit) - set(arms)), 'rows_not_matching_key': [r['arm_label'] for r in out if r.get('row_matches') is False],
           'n_energy_forecast': sum(1 for r in out if r.get('energy_forecast')),
           'distinct_time_configurations_kind_blind': len(cfg_kb),
           'twin_time_800_cases': sum(1 for r in out if r['twin_time_800']), 'twin_energy_800_cases_with_energy_forecast':
               sum(1 for r in out if r['twin_energy_800'] and r.get('energy_forecast')),
           'twin_time_800_distinct_configurations': len({(r['arm'], r['fmt'], r['mask'].lower()) for r in out if r['twin_time_800']}),
           'arms': out}
    json.dump(res, open(a.out, 'w'), indent=1, sort_keys=True)
    print(sha(a.out), a.out)
    print(json.dumps({k: v for k, v in res.items() if k != 'arms'}, sort_keys=True))
    for r in out:
        print(r['first_i'], r['arm_label'], r['kind'], r['mask'], r['n_runs'], 'twinT800' if r['twin_time_800'] else '-',
              'twinE800' if r['twin_energy_800'] else '-', 'E' if r.get('energy_forecast') else 't-only')


if __name__ == '__main__':
    main()
