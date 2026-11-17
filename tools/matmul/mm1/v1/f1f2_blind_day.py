#!/usr/bin/env python3
"""Today's models F1 and F2, generalized to the blind matmul day's points WITH THE MASKED MAP, frozen beside MM1-v1. Desk.

    /usr/bin/python3 -I -B f1f2_blind_day.py --repo <the lab at GitHub main> --out <dir>      writes f1f2_blind_day.json and .csv into <dir>

F1 and F2 are E206's registered routes, run unchanged (tools/claims-v3/e206/forecast_e206.py imported from the repo, its sha256 pinned below):
  F1, E190's route: seconds from E190's anchors and E119/E126's line-cost law at the point's lines; watts by E136's power law re-read from the
      anchor's burst, the data kind by E136's kind law, x kappa (E37) for aifoundry3, x shires / 32 for a subset; the card at rest by the ledger's
      idle law at 50 C; J over idle = W t, J at rest = (P_rest + W) t.
  F2, ledger v3's tensor terms (F1's seconds): the ledger load of each GEMM (tensor ops by kind, the L3 and DRAM bytes of the point's lines).
THE ROUTE IS NOT VENDORED (MM1-v1's inputs are): forecast_e206.py imports E190's route (forecast_e190) and ledger v3 (tools/ledger/ledger_v3) and
  reads their data from --repo at run time. PIN holds the full sha256 of the three files this script names and the run stops on any difference
  (verify-mm1v1 finding 4, Mon 16 Nov 2026: forecast_e206.py was unpinned and the other two were 16-hex prefixes); every other file the route
  reads under --repo is recorded with its sha256 in out/f1f2_route.json by f1f2_route.py, which also checks a lab copy against that record.
THE LINES (the generalization, mm-critic F2): E136's LRU desk model unchanged (reuse_e136.l2_model, l3_model) at 32, 28 and 24 MB on every point,
  and E206's subset function (reuse_e206.l3_model_masked) for a shire subset: the masked map, as E206 registered it.
KINDS: F1's kind law has rules for random, zeros, sparse50 and real (real = zeros + r (random - zeros), E95's r): the blind day's blind4 real
  tiles take its real rule; e37 and the designed blind3 tile have no F1 rule (F1 energy NOT PRICED there). F2 prices a kind the ledger has: random,
  zeros and e37 (ledger v2's fp32.small_int, whose own text names E37's fill; the one extension, stated); blind4 and blind3 tiles have no ledger row
  (F2 NOT PRICED). Seconds and cycles (kind-blind) are priced at every point by F1.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PIN = {'tools/claims-v3/e206/forecast_e206.py': 'd46e2bc6711da556cde4fdc9e3a35103b3d7fe41b818819e40bd80877f1754ed',
       'tools/claims-v3/e206/desk/reuse_e206.py': '2f6edc4eec5e97e67ecd2855cf59b4797bdb8ad4517bd3a8a31784155b5aef8a',
       'tools/claims-v3/e136/desk/reuse_e136.py': 'f24978d51463db18bbf059ddb47f224d57f218435769e422e001236430f06471'}


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    out = os.path.abspath(a.out)
    if out == HERE:
        sys.exit('f1f2_blind_day.py: --out must not be this folder')
    os.makedirs(out, exist_ok=True)
    pins = {k: sha(os.path.join(repo, k)) for k in PIN}
    for k, v in PIN.items():
        if pins[k] != v:
            sys.exit(f'pin mismatch: {k} {pins[k]} (pinned {v})')
    sys.path.insert(0, os.path.join(repo, 'tools', 'claims-v3', 'e206'))
    sys.path.insert(0, os.path.join(repo, 'tools', 'claims-v3', 'e206', 'desk'))
    sys.path.insert(0, HERE)
    import forecast_e206 as F
    import reuse_e206 as RE
    import blind_day_v1 as BD
    import mm1_core as C
    R = RE.R
    CAPS = (32, 28, 24)
    reuse = {'shapes': {}, 'law_arms': F.REUSE['law_arms']}
    l2c = {}
    for p in BD.POINTS:
        MB, NB, KB = C.parse_arm(p['arm'])
        m = int(p['mask'], 16)
        key = f"gemmL{MB}x{NB}x{KB}@{p['mask']}"
        if key in reuse['shapes']:
            continue
        if (MB, NB, KB) not in l2c:
            l2c[(MB, NB, KB)] = R.l2_model(('large', MB, NB, KB))
        l2 = l2c[(MB, NB, KB)]
        if m == 0xFFFFFFFF:
            l3 = {f'{c}MB': R.l3_model(('large', MB, NB, KB), c * 1024) for c in CAPS}
        else:
            l3 = {f'{c}MB': RE.l3_model_masked(('large', MB, NB, KB), c * 1024, m) for c in CAPS}
        reuse['shapes'][key] = {'blocks': [MB, NB, KB], 'shire_mask': p['mask'], 'L2': l2, 'L3': l3,
                                'lines': {k: RE.lines_of(l2['steady_missing_lines_per_op'], v) for k, v in l3.items()}}
        print(key, {k: (v['n_L3'], v['n_fresh']) for k, v in reuse['shapes'][key]['lines'].items()}); sys.stdout.flush()
    F.REUSE = reuse      # the generalization: E206's route reads its lines from this table
    F.LEDGER_KIND[('fp32', 'e37')] = 'fp32.small_int'
    F.RHO_TAU['e37'] = (0.1406, 0.1406)   # e37 fp32's set-bit and change shares (kinds_v1.gen_stats); F2's table has no e37 row
    rest = F.rest('A')
    rows = []
    for p in BD.POINTS:
        MB, NB, KB = C.parse_arm(p['arm'])
        mi = C.mask_info(p['mask'])
        ops = 64 * MB * NB * KB
        kind_f1 = {'random': 'random', 'real:blind4': 'real'}.get(p['kind'])
        pt = {'id': p['id'], 'name': f"{p['arm']}.{p['fmt']}.{p['kind']}", 'shape': {'kind': 'gemmL', 'blocks': [MB, NB, KB]}, 'format': p['fmt'],
              'kind': kind_f1 or p['kind'], 'arm': p['arm'], 'shire_mask': p['mask'], 'shires': mi['n'], 'minions': 32 * mi['n'],
              'ops_per_minion_per_gemm': ops}
        sp = F.speed(pt)
        t = sp['t_gemm_s']['point']
        row = {'id': p['id'], 'arm': p['arm'], 'fmt': p['fmt'], 'kind': p['kind'], 'mask': p['mask'],
               'lines_32MB_L3': reuse['shapes'][f"gemmL{MB}x{NB}x{KB}@{p['mask']}"]['lines']['32MB']['n_L3'],
               'lines_32MB_fresh': reuse['shapes'][f"gemmL{MB}x{NB}x{KB}@{p['mask']}"]['lines']['32MB']['n_fresh'],
               'F1_cycles_per_op': sp['cycles_per_op']['point'], 'F1_cycles_per_op_band': sp['cycles_per_op']['band'], 'F1_seconds_per_gemm': t,
               'F1_seconds_band': sp['t_gemm_s']['band'], 'F1_P_rest_W': rest['point']}
        if kind_f1 is not None:
            w6 = F.watts600(pt)
            k = F.KAPPA['A']
            frac = mi['n'] / 32.0
            W = k * w6['point'] * frac
            row.update({'F1_W_over_idle': W, 'F1_W_band': [w6['band'][0] * F.KAPPA_BAND[0] * frac, w6['band'][1] * F.KAPPA_BAND[1] * frac],
                        'F1_J_over_idle_per_gemm': W * t, 'F1_J_at_rest_per_gemm': (rest['point'] + W) * t, 'F1_kind_law': w6['kind_law']})
        else:
            row['F1_energy'] = 'NOT PRICED: F1 has no kind rule for ' + p['kind']
        if p['kind'] in ('random', 'e37') and (p['fmt'], 'random' if p['kind'] == 'random' else 'e37') in F.LEDGER_KIND:
            pt2 = dict(pt, kind='random' if p['kind'] == 'random' else 'e37')
            f2 = F.f2_price(pt2, 'A', t)
            if f2['priced']:
                row.update({'F2_J_over_idle_per_gemm': f2['J_over']['point'], 'F2_J_over_band': f2['J_over']['band'], 'F2_W_over_idle': f2['W_over']['point'],
                            'F2_J_at_rest_per_gemm': f2['J_rest']['point'], 'F2_wall_s_a_gemm': f2['wall_s_a_gemm']})
            else:
                row['F2_energy'] = f2['why']
        else:
            row['F2_energy'] = 'NOT PRICED: no ledger row for ' + p['kind'] + ' ' + p['fmt']
        rows.append(row)
        print(p['id'], p['arm'], p['fmt'], p['kind'], p['mask'], 'F1 cyc %.1f' % row['F1_cycles_per_op'], 'W', row.get('F1_W_over_idle'), 'F2 J', row.get('F2_J_over_idle_per_gemm'))
    res = {'what': "F1 and F2 (E206's registered routes, unchanged) generalized to the blind day's points with the masked map, frozen beside MM1-v1",
           'pins_sha256': pins, 'rest_A': rest, 'kappa_A': F.KAPPA['A'], 'extension': "F2's ledger kind for e37 in fp32: fp32.small_int (the ledger's own text names E37's fill)",
           'reuse': reuse, 'rows': rows, 'python': sys.version.split()[0]}
    json.dump(res, open(os.path.join(out, 'f1f2_blind_day.json'), 'w'), indent=1, default=float)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(out, 'f1f2_blind_day.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == '__main__':
    main()
