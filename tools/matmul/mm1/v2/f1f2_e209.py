#!/usr/bin/env python3
"""Today's models F1 and F2 beside MM1-v2 on E209's points (aifoundry2 card 0 under its governor). Desk.

    /usr/bin/python3 -I -B f1f2_e209.py --repo <the lab at GitHub main> --points <e209_points.csv> --out <dir>
        writes <dir>/f1f2_e209.json and <dir>/f1f2_e209.csv

WHERE E206'S REGISTERED ROUTES CAN BE CALLED FOR aifoundry2, AND WHERE NOT (stated):
  - E206's F1 and F2 are registered for its two arms only (A: aifoundry3, B: aifoundry1 card 1, both at 600 MHz). Neither arm is aifoundry2,
    and neither has an 800 MHz route. They are NOT callable as registered for E209's runs at the top point.
  - F1's watts are built ON aifoundry2 (E190's watts_A at 600 MHz: the anchor bursts were aifoundry2's, E136 and E146) and its seconds by
    aifoundry2's E119/E126 fits at 600 MHz; kappa (E37) only carries them to another card. So E206's F1 IS callable for aifoundry2 at 600
    MHz, unchanged, with kappa = 1 (the route's own card): column F1@600. E209 does not score at 600 MHz (its scored window holds the top point).
  - F1 AT 800 MHz: E190's own arm-A route (tools/claims-v3/e190/forecast_e190.py, the source of E206's F1), which forecast aifoundry2 at its
    800 MHz bursts: T800 = T800(anchor) x law(point, 800 MHz) / law(anchor, 800 MHz) on the c16s footing, and W800 = W(anchor) + P_levels(cE,
    T600, T800)[800] - P(anchor), cE by E136's kind law at the point's lines; a subset x shires / 32 (F1's rule); the lines by E206's
    generalization (E136's LRU desk model at 32 MB; E206's masked subset function). Column F1@800: the same formulas, a new generalization
    (E190 forecast three shapes), labelled.
  - F2 AT 800 MHz: ledger v3 (landed 50795847, unchanged) priced as E206's F2 prices a GEMM (its ledger_load form), with the card aifoundry2
    and the clock 800 MHz in the load: ledger v3's rule 7 adds the governed base above the idle clock; its seconds F1@800's. Column F2@800.
  - KINDS: random, zeros and real (E206's four tiles a format; F1's real rule; F2's real rows, carried by ledger v3's carried() where aifoundry2
    has none) are priced; ones has no F1 rule and no ledger row: NOT PRICED by either.
THE ROUTE IS NOT VENDORED: it imports E206's forecast_e206.py (and through it E190's route and ledger v3) from --repo at run time; PIN holds
  the full sha256 of the files it names and the run stops on any difference. Ledger v3 also reads the lab's data folders at run time (docs/
  reports/data and workloads/ledger): run it at the lab's top in a full checkout.
FAILS LOUDLY (fix-mm1v2, Tue 17 Nov 2026, answering verify-mm1v2's finding 5: a missing input folder had left F2 unpriced on 42 points with
  no error): a missing or unreadable file raises (never 'NOT PRICED'), and the run stops before writing anything if F2 prices fewer points
  than have a ledger row (E209: 42 of 45; ones have none), unless --allow-unpriced is given.
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
RECORD = ['tools/claims-v3/e190/forecast_e190.py', 'tools/ledger/ledger_v3.py', 'tools/ledger/frozen-v3.json', 'tools/ledger/ledger_v2.py']
REAL_TILES = {'fp32': ['gpt2_l9_attn_qk', 'gpt2_l3_mlp_down', 'bert_l6_up', 'vit_l5_down'],
              'fp16': ['gpt2_l9_attn_qk', 'bert_l6_up', 'vit_l5_down', 'gpt2_l6_mlp_down_fp16fwd'],
              'int8': ['gpt2_l6_down_p999', 'gpt2_l6_down_p9999', 'gpt2_l6_down_per_token', 'gpt2_l11_down_p999']}


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--points', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--allow-unpriced', action='store_true', help='write the outputs even if F2 leaves a point with a ledger row unpriced')
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    pins = {k: sha(os.path.join(repo, k)) for k in PIN}
    for k, v in PIN.items():
        if pins[k] != v:
            sys.exit(f'pin mismatch: {k} {pins[k]} (pinned {v})')
    rec = {k: sha(os.path.join(repo, k)) for k in RECORD}
    sys.path.insert(0, os.path.join(repo, 'tools', 'claims-v3', 'e206'))
    sys.path.insert(0, os.path.join(repo, 'tools', 'claims-v3', 'e206', 'desk'))
    import forecast_e206 as F
    import reuse_e206 as RE
    FE = F.FE
    M136 = F.M136
    R = RE.R
    pts = list(csv.DictReader(open(a.points)))
    reuse = {'shapes': {}, 'law_arms': F.REUSE['law_arms']}
    l2c = {}
    for p in pts:
        MB, NB, KB = (int(x) for x in p['arm'][5:].split('x'))
        m = int(p['mask'], 16)
        key = f"gemmL{MB}x{NB}x{KB}@{p['mask']}"
        if key in reuse['shapes']:
            continue
        if (MB, NB, KB) not in l2c:
            l2c[(MB, NB, KB)] = R.l2_model(('large', MB, NB, KB))
        l2 = l2c[(MB, NB, KB)]
        if m == 0xFFFFFFFF:
            l3 = {f'{c}MB': R.l3_model(('large', MB, NB, KB), c * 1024) for c in (32, 28, 24)}
        else:
            l3 = {f'{c}MB': RE.l3_model_masked(('large', MB, NB, KB), c * 1024, m) for c in (32, 28, 24)}
        reuse['shapes'][key] = {'blocks': [MB, NB, KB], 'shire_mask': p['mask'], 'L2': l2, 'L3': l3,
                                'lines': {k: RE.lines_of(l2['steady_missing_lines_per_op'], v) for k, v in l3.items()}}
    F.REUSE = reuse
    p_rest = FE.idle('aifoundry2', F.T0)
    rows = []
    f2_eligible = 0
    for p in pts:
        MB, NB, KB = (int(x) for x in p['arm'][5:].split('x'))
        n = int(p['shires'])
        t = p['fmt']
        ops = int(p['ops'])
        kind = p['kind']
        pt = {'id': p['id'], 'shape': {'kind': 'gemmL', 'blocks': [MB, NB, KB]}, 'format': t, 'kind': kind, 'arm': p['arm'], 'shire_mask': p['mask'],
              'shires': n, 'minions': 32 * n, 'ops_per_minion_per_gemm': ops}
        nl, nf = F.lines(pt)
        sp = F.speed(pt)
        T6 = sp['T600_us']['point']
        an = FE.anchor(t)
        T8 = an['T800'] * FE.law_T(nl, nf, t, 800.0, 'c16s') / FE.law_T(an['lines'][0], an['lines'][1], t, 800.0, 'c16s')
        row = {'id': p['id'], 'case': p['case'], 'lines_32MB_L3': round(nl, 3), 'lines_32MB_fresh': round(nf, 3),
               'F1_cycles_per_op@600': round(T6 * 600.0, 3), 'F1_seconds_per_gemm@600': ops * T6 * 1e-6,
               'F1_cycles_per_op@800': round(T8 * 800.0, 3), 'F1_seconds_per_gemm@800': ops * T8 * 1e-6, 'F1_P_rest_W@50C': round(p_rest, 4)}
        if kind in F.KIND_E136:
            if kind == 'real':
                pt['kind'] = 'real'
            w6 = F.watts600(pt)
            frac = n / 32.0
            Pm = w6['anchor_burst_mean_w']
            Wm = w6['anchor_w_over_idle_mean']
            cE = w6['c600_point']
            L = FE.P_levels(cE, T6, T8)
            W8 = (Wm + L[800] - Pm) * frac
            row.update({'F1_W_over@600': round(w6['point'] * frac, 4), 'F1_W_over@800': round(W8, 4),
                        'F1_J_over@800': W8 * ops * T8 * 1e-6, 'F1_J_rest@800': (p_rest + W8) * ops * T8 * 1e-6, 'F1_kind_law': w6['kind_law']})
        else:
            row['F1_energy'] = 'NOT PRICED: F1 has no kind rule for ' + kind
        if (t, kind) in F.LEDGER_KIND or kind == 'real':
            f2_eligible += 1
            t8 = ops * T8 * 1e-6
            g = F.gemms_a_launch(pt, t8)
            ld = F.ledger_load(pt, 'A', t8, g)
            ld['card'] = 'aifoundry2'
            ld['f_mhz'] = 800.0
            try:
                o = F.LV3.predict_v2load(ld, F.F3, rules=None, die_c=None)
                pr = o['v2_prediction']
                jo = pr['j_over_idle_with_heat'] / g
                row.update({'F2_J_over@800': jo, 'F2_W_over@800': jo / t8, 'F2_J_rest@800': o['j_total'] / g, 'F2_rule7': json.dumps(o.get('rule7'), default=float)[:300]})
            except SystemExit as e:
                row['F2_energy'] = f'NOT PRICED: ledger v3 refused the load ({e})'
            except OSError:
                raise       # a missing or unreadable input is an error, never 'NOT PRICED'
            except Exception as e:  # noqa: BLE001
                row['F2_energy'] = f'NOT PRICED: ledger v3 raised {type(e).__name__}: {e}'
        else:
            row['F2_energy'] = 'NOT PRICED: no ledger row for ' + kind + ' ' + t
        rows.append(row)
        print(p['id'], p['case'], 'F1 cyc@800 %.1f' % row['F1_cycles_per_op@800'], 'W@800', row.get('F1_W_over@800'), 'F2 W@800', row.get('F2_W_over@800'), row.get('F2_energy', ''))
    f2_priced = sum(1 for r in rows if 'F2_J_over@800' in r)
    print(f'F2 priced {f2_priced} of {f2_eligible} points with a ledger row ({len(rows)} points)')
    if f2_priced < f2_eligible and not a.allow_unpriced:
        sys.exit(f'F2 priced {f2_priced} of {f2_eligible} points with a ledger row: an input is missing or ledger v3 refused; nothing written')
    res = {'what': "F1 and F2 beside MM1-v2 on E209's points (aifoundry2 card 0): F1@600 E206's route unchanged for aifoundry2 (kappa 1); F1@800 "
                   "E190's arm-A route at 800 MHz generalized with E206's lines; F2@800 ledger v3 with card aifoundry2 at 800 MHz (rule 7)",
           'pins_sha256': pins, 'recorded_sha256': rec, 'p_rest_aifoundry2_50C': p_rest, 'reuse': reuse, 'rows': rows, 'python': sys.version.split()[0]}
    json.dump(res, open(os.path.join(out, 'f1f2_e209.json'), 'w'), indent=1, default=float)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(os.path.join(out, 'f1f2_e209.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for fn in ('f1f2_e209.json', 'f1f2_e209.csv'):
        print(sha(os.path.join(out, fn)), fn)


if __name__ == '__main__':
    main()
