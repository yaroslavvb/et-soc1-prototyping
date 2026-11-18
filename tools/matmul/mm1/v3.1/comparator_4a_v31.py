#!/usr/bin/env python3
"""MM1-v3.1's acceptance rule 4(a), with its comparator on the same points (DECLARED-v31.md section 9), frozen before any E213 datum and
before v3.1's fit (round Q217, lane fix-v31decl, Wed 18 Nov 2026, PST). Desk; no card, no simulator. /usr/bin/python3 3.12.3 with numpy
1.26.4, -I -B, single-threaded.

RULE 4(a): v3.1's E212 fold (E212 held out) is under MM1-v2's UNREAD error on EXACTLY THE SAME E212 case records:
  - the records: one a (card, case), the mean over its runs (MM1-v3's data_v3.cases, as v3's and v3.1's points), built here from the runs of
    E212's nine committed sessions (MM1-v3's vendored inputs: the eight under inputs/e212/ and a2c0-S4 under inputs/e212-unread/), so a
    case run in two sessions (for example E212|a2|gemmL16x8x1|fp32|ones|0xffffffff) is one record with the mean of both sessions' runs;
  - MM1-v2's per-case figures: MM1-v2 as frozen (tools/matmul/mm1/v2 at 3ca4b717, checked by MM1-v3's unread_v2_e212.v2_model) called on
    each record exactly as MM1-v3's unread_v2_e212.py calls it (at the record's mean clock; the governed cards at its mean volts; W given t
    = A + B / t_meas), wall cycles an op for time, W over idle given t at 3 W and above for energy;
  - time: every record v3.1's E212 fold scores that is here; energy: those records where both models price W at a measured W of 3 W or more;
    a v3.1 record whose measured value differs from this record's (relative 1e-9: a session this script does not read, for example a later
    a2c0-S3) is outside the comparison and listed; twins included, as MM1-v3's rule 4 was scored; without v3.1's twins REPORTED when the
    input carries is_twin;
  - PASS when v3.1's rms is lower than MM1-v2's in both quantities.
  The eight-session figures (MM1-v3's committed comparator: wall 6.65%, W 7.76%) and a2c0-S4's alone are printed beside, never deciding.

    python3 -I -B comparator_4a_v31.py --desk [--repo R] [--out json] [--cases-out csv]
        MM1-v2's figures on the nine-session records; the check that the same code on the eight sessions alone reproduces MM1-v3's committed
        out/unread_v2_e212_cases.csv exactly
    python3 -I -B comparator_4a_v31.py --score <v31-e212-fold.csv> [--repo R] [--out json]
        the CSV, written by v3.1's fit: columns id (v3's ids, e.g. E212|c1|gemmL4x8x4|int8|random|0xffffffff), meas_cyc_wall, e_wall (v3.1's
        E212-fold forecast / measured - 1 of the wall cycles an op), meas_w (measured W over idle; blank if none), e_w_given_t (v3.1's
        E212-fold W over idle given t / measured - 1; blank where v3.1 prices no W or meas_w < 3), optional is_twin (0 or 1)
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PINS = {'tools/matmul/mm1/v3/data_v3.py': 'a5eb123bf1ba16fca51bf9474904a73919cacbf870e0f37bb5f78126236862be',
        'tools/matmul/mm1/v3/unread_v2_e212.py': '916954ccaf477c3e4c858d1a6f68c2cb5d224339792e33bab4fa81908c7f2028',
        'tools/matmul/mm1/v3/inputs/e212-unread/a2c0-S4__data-e212-a2c0-S4.json': '2e2ed24e13544b322f7b5a1e54952fb3d2f509da204b44eafdfa36a66bdbdc98',
        'tools/matmul/mm1/v3/out/unread_v2_e212_cases.csv': '138758b4e928daa957bf57a4c44c8c1251ae626a73054e282056b2f8f8e3dfab',
        'tools/matmul/mm1/v3/out/unread_v3_e212s4_cases.csv': 'e1b6d0609232abcb957e4201a04b76d9295bf82331b2cbf53382c070912ec305'}
S4 = 'a2c0-S4__data-e212-a2c0-S4.json'


def _f(x):
    return None if x is None or x == '' else float(x)


def load(repo):
    for rel, want in PINS.items():
        got = hashlib.sha256(open(os.path.join(repo, rel), 'rb').read()).hexdigest()
        if got != want:
            sys.exit(f'comparator_4a_v31: REFUSED: {rel} sha256 {got} is not the pinned {want}')
    v3 = os.path.join(repo, 'tools', 'matmul', 'mm1', 'v3')
    sys.path.insert(0, v3)
    import data_v3 as D  # noqa: E402
    import unread_v2_e212 as U2  # noqa: E402
    return D, U2


def v2_cases(D, U2, M, R):
    """MM1-v2's per-case record figures, as unread_v2_e212.py's per-case loop computes them"""
    T, E = D.cases(R, 'E212')
    Em = {e['id']: e for e in E}
    out = {}
    for c in T:
        rr = {'card': c['card'], 'arm': c['arm'], 'fmt': c['fmt'], 'kind': c['kind'], 'mask': c['mask'], 'f': c['f']}
        e = Em.get(c['id'])
        if e and c['card'] != 'aifoundry1 card 1':
            rr['V_mv'] = e['V'] * 1000.0
        pr = U2.call(M, rr)
        row = {'meas_cyc_wall': c['cw'], 'e_wall': pr['cycles_per_op_wall'] / c['cw'] - 1, 'meas_w': None, 'e_w': None, 'n_runs': c['n_runs']}
        if e and 'W_affine' in pr:
            Wg = pr['W_affine']['A_W'] + pr['W_affine']['B_W_us'] / e['T']
            row['meas_w'] = e['w']
            row['e_w'] = (Wg / e['w'] - 1) if e['w'] >= 3.0 else None
        out[c['id']] = row
    return out


def stat(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {'n': 0, 'rms_pct': None, 'bias_pct': None}
    return {'n': len(xs), 'rms_pct': round(100.0 * math.sqrt(sum(x * x for x in xs) / len(xs)), 3),
            'bias_pct': round(100.0 * sum(xs) / len(xs), 3)}


def figures(rows):
    return {'wall': stat([r['e_wall'] for r in rows.values()]),
            'W_given_t_ge3W': stat([r['e_w'] for r in rows.values() if r['meas_w'] is not None and r['meas_w'] >= 3.0])}


def committed(repo):
    a, b = {}, {}
    for r in csv.DictReader(open(os.path.join(repo, 'tools/matmul/mm1/v3/out/unread_v2_e212_cases.csv'))):
        a[r['id']] = {'e_wall': _f(r['e_wall']), 'meas_w': _f(r['meas_w']), 'e_w': _f(r['e_w_given_t'])}
    for r in csv.DictReader(open(os.path.join(repo, 'tools/matmul/mm1/v3/out/unread_v3_e212s4_cases.csv'))):
        b[r['id']] = {'e_wall': _f(r['v2_e_wall']), 'meas_w': _f(r['meas_w']), 'e_w': _f(r['v2_e_w_given_t'])}
    return a, b


def score(v2, path):
    rows = list(csv.DictReader(open(path)))
    ids = [r['id'] for r in rows]
    if len(ids) != len(set(ids)):
        sys.exit('comparator_4a_v31: REFUSED: duplicate ids in the v3.1 CSV')
    both_t, both_w, outside, differ = [], [], [], []
    for r in rows:
        v = v2.get(r['id'])
        e = _f(r.get('e_wall'))
        if v is None or e is None:
            outside.append(r['id'])
            continue
        mc = _f(r.get('meas_cyc_wall'))
        if mc is None or abs(mc / v['meas_cyc_wall'] - 1.0) > 1e-9:
            differ.append(r['id'])
            continue
        tw = r.get('is_twin', '') in ('1', 'True', 'true')
        both_t.append((e, v['e_wall'], tw))
        mw = _f(r.get('meas_w'))
        ew = _f(r.get('e_w_given_t'))
        if mw is not None and mw >= 3.0 and ew is not None and v['e_w'] is not None and abs(mw / v['meas_w'] - 1.0) <= 1e-9:
            both_w.append((ew, v['e_w'], tw))
    res = {'v31_rows': len(rows), 'outside_the_records': outside, 'measured_value_differs': differ,
           'wall': {'v31': stat([a for a, _, _ in both_t]), 'v2_unread': stat([b for _, b, _ in both_t])},
           'W_given_t_ge3W': {'v31': stat([a for a, _, _ in both_w]), 'v2_unread': stat([b for _, b, _ in both_w])}}
    if any('is_twin' in r for r in rows):
        res['REPORTED_without_v31_twins'] = {
            'wall': {'v31': stat([a for a, _, t in both_t if not t]), 'v2_unread': stat([b for _, b, t in both_t if not t])},
            'W_given_t_ge3W': {'v31': stat([a for a, _, t in both_w if not t]), 'v2_unread': stat([b for _, b, t in both_w if not t])}}
    ok = (res['wall']['v31']['n'] > 0 and res['W_given_t_ge3W']['v31']['n'] > 0
          and res['wall']['v31']['rms_pct'] < res['wall']['v2_unread']['rms_pct']
          and res['W_given_t_ge3W']['v31']['rms_pct'] < res['W_given_t_ge3W']['v2_unread']['rms_pct'])
    res['rule_4a'] = 'PASS' if ok else 'FAIL'
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--desk', action='store_true')
    ap.add_argument('--score')
    ap.add_argument('--repo', default=os.environ.get('MM1_REPO') or os.path.normpath(os.path.join(HERE, '..', '..', '..', '..')))
    ap.add_argument('--out')
    ap.add_argument('--cases-out')
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    D, U2 = load(repo)
    M, _ = U2.v2_model()
    R8 = D.e212_runs()
    R9 = R8 + D.mms_runs(('e212-unread', S4), 'E212', D.e212_kind)
    v9 = v2_cases(D, U2, M, R9)
    res = {'what': "MM1-v3.1 acceptance rule 4(a) on the same E212 case records (comparator_4a_v31.py)",
           'comparator_sha256': hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(), 'pins': PINS,
           'interpreter': '/usr/bin/python3 %s' % sys.version.split()[0],
           'runs': {'eight_sessions': len(R8), 'nine_sessions': len(R9)},
           'comparator_nine_session_records': figures(v9)}
    if a.desk:
        v8 = v2_cases(D, U2, M, R8)
        c8, c4 = committed(repo)
        same_ids = sorted(v8) == sorted(c8)
        dw = max(abs(v8[k]['e_wall'] - c8[k]['e_wall']) for k in c8) if same_ids else None
        de = max(abs((v8[k]['e_w'] or 0.0) - (c8[k]['e_w'] or 0.0)) + (0.0 if (v8[k]['e_w'] is None) == (c8[k]['e_w'] is None) else 1.0)
                 for k in c8) if same_ids else None
        res['check_eight_sessions_reproduce_committed'] = {'same_case_ids': same_ids, 'max_abs_diff_e_wall': dw, 'max_abs_diff_e_w': de,
                                                           'pass': bool(same_ids and dw < 1e-6 and de < 1e-6)}
        res['REPORTED_beside'] = {'eight sessions (MM1-v3 rule 4 comparator, committed)': figures(c8),
                                  'a2c0-S4 alone (committed)': figures(c4),
                                  'cases in two sessions (merged here)': sorted(k for k in c4 if k in c8)}
    if a.cases_out:
        with open(a.cases_out, 'w', newline='') as fh:
            w = csv.writer(fh, lineterminator='\n')
            w.writerow(['id', 'n_runs', 'meas_cyc_wall', 'v2_e_wall', 'meas_w', 'v2_e_w_given_t'])
            for k in sorted(v9):
                r = v9[k]
                w.writerow([k, r['n_runs'], repr(r['meas_cyc_wall']), repr(r['e_wall']), '' if r['meas_w'] is None else repr(r['meas_w']),
                            '' if r['e_w'] is None else repr(r['e_w'])])
    if a.score:
        res['score'] = score(v9, a.score)
    s = json.dumps(res, indent=1, sort_keys=True) + '\n'
    if a.out:
        open(a.out, 'w').write(s)
    print(s, end='')
    if a.score:
        sys.exit(0 if res['score']['rule_4a'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
