#!/usr/bin/env python3
"""MM1-v2, step 1: MM1-v1 as landed and MM1-v0 as frozen, UNCHANGED, scored on every committed E208 run, before any v2 fit. Desk.

    /usr/bin/python3 -I -B score_unread.py --out <dir> [--scratch <new dir>]
        writes <dir>/unread_e208.json (every run's arguments, forecasts and errors; the statistics), <dir>/unread_e208.csv (one row a run),
        <dir>/unread_e208.md (the tables). Refuses to run if MM1-v1's SHA256SUMS (../v1) or MM1-v0's frozen predictor (../v0) differ.

LABEL: UNREAD. E208's first five data commits (e99209a5, d40b6fe8, c2d6536c, eed9624f, 76fb5344: 20:32:30-20:33:09 PST Mon 16 Nov 2026) came
before MM1-v1's freeze (25d2e74e, 21:14:55 PST) but MM1-v1 did not read them (its inputs are vendored at d7e4f35e and MANIFEST.json lists no
E208 file); a later session's commit (a1c1-S3) comes after it. MM1-v0's predictor and constants were frozen at 13:04:57 PST, before E208's
first datum (18:25:26 PST), but no forecast for E208's points was frozen then: these forecasts are made now by the frozen code, with the call's
arguments (card, clock, volts, governed base, kind rule) chosen now. Neither column is a registered blind test.

HOW EACH MODEL IS CALLED (the arguments; nothing refitted, no new constant):
  - aifoundry2 card 0 (governed): f = the run's measured kernel clock in its primary view (the reducer's kclock_mhz: about 799 MHz in the
    'win' view), V = the run's measured minion volts (the view's minion rail, rails.minion.mV) or, if absent, the energy manual's line
    0.517 / 0.568 / 0.618 V at 600 / 700 / 800 MHz, G = B(f) - B(600) by the M7 relation (25.456 / 28.243 / 33.610 W at 600 / 700 / 800
    MHz, linear between): exactly how MM1-v1's and MM1-v0's energy fits carried aifoundry2's governed points (design C's table builder).
    Each model handles a clock other than 600 MHz the same way: in time, the fixed latencies (c3, cF; the c1 law's cycles) scale as 1/f while
    the m terms (us) and v1's L2 time T2 (us) do not; in energy, the resident price and the line prices are per op at 0.517 V x s_V = (V /
    0.517 V)^2, the awake powers are watts that do not scale, and g [B(f) - B(600)] adds the governed base's rise. The predictors take V
    and G from the caller; neither computes them from f.
  - aifoundry1 card 1: f = the measured clock (about 600 MHz), V = 0.517 V (s_V = 1: the volts of every card-1 row of both models' energy
    fits, and of MM1-v1's and MM1-v0's frozen E206 arm B forecasts), G = 0.
  - aifoundry1 card 0: neither model has a card-0 term (no awake power, no resident anchor): cycles and seconds at the measured clock; energy
    NOT FORECAST. A side reading, labelled 'borrowed footing', calls each model with aifoundry2's card terms at card 0's own clock, volts and
    G (the other governed card), to show the distance; it is not a forecast of either model.
  - kinds: random and zeros take each model's own ledger v2 rows; 'ones' (a repeated tile of 1.0) has no resident price in ledger v2 or the
    blind files, so its energy is NOT FORECAST by either model (v1 called with e_res_spec {'source': None}; v0's kind key is None); its
    cycles and seconds are forecast (neither model's time depends on the kind).
  - masks: v1 takes the run's mask (its chi and imbalance terms); v0 has no mask (a subset point carries its full-chip per-op time), and
    both take the active minions (32 x the mask's shires) for energy.
SCORES (error = forecast / measured - 1; rms and bias in %): cycles an op, the wall (cyc_op_max) and the counter's mean (cyc_op_mean);
  seconds a GEMM (t_pass_s); W = J over idle given the measured seconds (the affine A + B / t_op at the measured op time); J over idle with
  seconds forecast; J with the card at rest given the measured seconds and with seconds forecast (the run's measured rest = board mean - dP).
  Points under 3 W over idle are scored in watts. Per run and per distinct case (the mean of a case's runs on a card).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data_e208 as D  # noqa: E402

V1 = os.path.normpath(os.path.join(HERE, '..', 'v1'))
V0 = os.path.normpath(os.path.join(HERE, '..', 'v0'))
V0_SHA = '7dabaeac53c67ed52815aa7e11d356e550058085f6f5a83469be38430d5f7971'   # tools/matmul/mm1/v0/mm1_v0.py at 2d1413f5
V0_OUTPUTS = ('mm1_v0_params.json', 'mm1_v0_e206.csv', 'mm1_v0_e206.json', 'blind_day_plan.csv')
LOW = 3.0
B_M7 = [(600.0, 25.456), (700.0, 28.243), (800.0, 33.610)]
V_LAW = [(600.0, 0.517), (700.0, 0.568), (800.0, 0.618)]
V_C1 = 0.517


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def interp(pts, f):
    if f <= pts[0][0]:
        return pts[0][1]
    if f >= pts[-1][0]:
        return pts[-1][1]
    for (f0, y0), (f1, y1) in zip(pts, pts[1:]):
        if f0 <= f <= f1:
            return y0 + (y1 - y0) * (f - f0) / (f1 - f0)


def G_of_f(f):
    return interp(B_M7, f) - interp(B_M7, 600.0)


def check_v1():
    bad, n = [], 0
    for ln in open(os.path.join(V1, 'SHA256SUMS')):
        if not ln.strip():
            continue
        h, p = ln.rstrip('\n').split('  ', 1)
        n += 1
        if not os.path.isfile(os.path.join(V1, p)) or sha(os.path.join(V1, p)) != h:
            bad.append(p)
    return n, bad


def load_v1():
    n, bad = check_v1()
    if bad:
        sys.exit(f'score_unread.py: MM1-v1 is not as landed: {len(bad)} of {n} files differ from its SHA256SUMS: {bad[:5]}')
    sys.path.insert(0, V1)
    spec = importlib.util.spec_from_file_location('mm1_v1_landed', os.path.join(V1, 'mm1_v1.py'))
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    sys.path.remove(V1)
    params = json.load(open(os.path.join(V1, 'out', 'mm1_v1_params.json')))
    return M, M.Model(params), n, params


def load_v0(scratch):
    """MM1-v0's frozen predictor imported as it stands (its module code writes its four outputs into scratch, which must reproduce the
    committed ones byte for byte), as its own arm B wrapper does (tools/matmul/mm1/v0/forecasts-e206-armB.py)"""
    pred = os.path.join(V0, 'mm1_v0.py')
    if sha(pred) != V0_SHA:
        sys.exit('score_unread.py: tools/matmul/mm1/v0/mm1_v0.py is not the committed frozen file')
    sums = dict(reversed(ln.split()) for ln in open(os.path.join(V0, 'SHA256SUMS')) if ln.strip())
    if os.path.exists(scratch) and os.listdir(scratch):
        sys.exit('score_unread.py: --scratch must be new or empty')
    os.makedirs(scratch, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [pred, '--out', scratch]
    buf = io.StringIO()
    spec = importlib.util.spec_from_file_location('mm1_v0_frozen', pred)
    M = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(buf):
        spec.loader.exec_module(M)
    sys.argv = argv0
    for fn in V0_OUTPUTS:
        if sha(os.path.join(scratch, fn)) != sums[fn]:
            sys.exit(f'score_unread.py: the frozen MM1-v0 did not reproduce {fn}')
    return M


def args_for(r, borrowed=False):
    """the call's arguments for a run: (card name, v1/v0 card key, f, V, G, how)"""
    f = r['f']
    ck = r['card_key']
    if ck == 'a2c0' or (ck == 'a1c0' and borrowed):
        V = (r['V_mv'] / 1000.0) if r.get('V_mv') else interp(V_LAW, f)
        return 'aifoundry2 card 0', 'a2', f, V, G_of_f(f), ('measured minion volts' if r.get('V_mv') else 'the volts law')
    if ck == 'a1c1':
        return 'aifoundry1 card 1', 'c1', f, V_C1, 0.0, 's_V = 1 (the footing of the card-1 fit rows)'
    return None, None, f, None, None, 'no card-0 term'


def v1_call(M1, r, borrowed=False):
    card, key, f, V, G, how = args_for(r, borrowed)
    es = {'source': None} if r['kind'] == 'ones' else None
    ps = {'gen': 'zeros'} if r['kind'] == 'ones' else None
    o = M1.predict(card or 'aifoundry2 card 0', r['arm'], r['fmt'], r['kind'], r['mask'], f, V or 0.517, G=G or 0.0, e_res_spec=es, phi_spec=ps,
                   ops=r['ops'], minions=r['minions'])
    out = {'cyc_wall': o['cycles_per_op_wall'], 'cyc_mean': o['cycles_per_op_mean'], 't_gemm': o['seconds_per_gemm'], 'T': o['T_op_us']}
    if card is not None and 'W_over_idle' in o:
        A, B = o['W_affine']['A_W'], o['W_affine']['B_W_us']
        out.update({'W': o['W_over_idle'], 'A': A, 'B_us': B})
    else:
        out['energy_note'] = o.get('energy') if card is not None else 'NOT FORECAST: MM1-v1 has no aifoundry1 card 0 term'
    out['args'] = {'card': card, 'f': f, 'V': V, 'G': G, 'how': how, 'mask': r['mask'], 'minions': r['minions'], 'ops': r['ops']}
    return out


def v0_call(M0, r, borrowed=False):
    card, key, f, V, G, how = args_for(r, borrowed)
    kind = None if r['kind'] == 'ones' else r['kind']
    pr = M0.predict(key or 'a2', card or 'aifoundry2 card 0', r['arm'], r['fmt'], kind if kind else 'ones', f, V or 0.517, r['minions'], G=G or 0.0)
    out = {'cyc_wall': pr['cycles_per_op_wall'], 'cyc_mean': pr['cycles_per_op_mean'], 't_gemm': pr['seconds_per_gemm'], 'T': pr['T_op_us']}
    if card is not None and 'W_over_idle' in pr:
        A = M0.TH['Paw|' + card] * r['minions'] / 1024.0 + M0.TH['g'] * G
        Bus = (pr['W_over_idle'] - A) * pr['T_op_us']
        out.update({'W': pr['W_over_idle'], 'A': A, 'B_us': Bus})
    else:
        out['energy_note'] = pr.get('energy') if card is not None else 'NOT FORECAST: MM1-v0 has no aifoundry1 card 0 term'
    out['args'] = {'card': card, 'f': f, 'V': V, 'G': G, 'how': how, 'mask': 'none (v0 has no mask)', 'minions': r['minions'], 'ops': r['ops']}
    return out


def errors(r, p):
    """per-run errors of one model's forecast p against run r"""
    e = {'cyc_wall': p['cyc_wall'] / r['cyc_wall'] - 1, 'cyc_mean': p['cyc_mean'] / r['cyc_mean'] - 1, 't_gemm': p['t_gemm'] / r['t_gemm'] - 1}
    if 'W' in p and 'w' in r:
        wg = p['A'] + p['B_us'] / r['T']
        jt_fc = p['W'] * p['t_gemm']
        e['w_given_t_pred'] = wg
        if r['w'] >= LOW:
            e['W_given_t'] = wg / r['w'] - 1
            e['J_over_t_fc'] = jt_fc / r['J_over'] - 1
        else:
            e['W_given_t_watts'] = wg - r['w']
            e['J_over_t_fc_watts_equiv'] = jt_fc / r['t_gemm'] - r['w']
        e['J_rest_given_t'] = (r['p_rest'] + wg) * r['t_gemm'] / r['J_rest'] - 1
        e['J_rest_t_fc'] = (r['p_rest'] + p['W']) * p['t_gemm'] / r['J_rest'] - 1
    return e


def st(x):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) == 0:
        return None
    return {'n': int(len(x)), 'rms_pct': round(float(np.sqrt(np.mean(x ** 2))) * 100, 2), 'bias_pct': round(float(np.mean(x)) * 100, 2),
            'worst_pct': round(float(x[np.argmax(np.abs(x))]) * 100, 1)}


def sta(x):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) == 0:
        return None
    return {'n': int(len(x)), 'rms_W': round(float(np.sqrt(np.mean(x ** 2))), 3), 'bias_W': round(float(np.mean(x)), 3)}


QTY = [('cyc_wall', 'cycles an op, wall'), ('cyc_mean', "cycles an op, the counter's mean"), ('t_gemm', 'seconds a GEMM'),
       ('W_given_t', 'W = J over idle given t (>= 3 W)'), ('J_over_t_fc', 'J over idle, seconds forecast (>= 3 W)'),
       ('J_rest_given_t', 'J at rest given t'), ('J_rest_t_fc', 'J at rest, seconds forecast')]


def groups():
    g = collections.OrderedDict()
    g['all'] = lambda r: True
    for c in ('aifoundry2 card 0', 'aifoundry1 card 1', 'aifoundry1 card 0'):
        g[c] = (lambda c: lambda r: r['card'] == c)(c)
    return g


def sub_groups():
    keys = collections.OrderedDict()
    keys['shape class'] = lambda r: r['shape_class']
    keys['format'] = lambda r: r['fmt']
    keys['data kind'] = lambda r: r['kind']
    keys['mask'] = lambda r: r['mask']
    keys['family'] = lambda r: '+'.join(r['families'] or ['?'])
    keys['role'] = lambda r: r['role'] + (' capped' if r['capped'] else '')
    return keys


def stats_block(R, E, model):
    out = collections.OrderedDict()
    for gname, fn in groups().items():
        sel = [r for r in R if fn(r)]
        blk = {}
        for q, lab in QTY:
            blk[lab] = st([E[r['id']][model].get(q) for r in sel])
        blk['W over idle under 3 W (watts)'] = sta([E[r['id']][model].get('W_given_t_watts') for r in sel])
        out[gname] = blk
        for kname, kf in sub_groups().items():
            for kv in sorted({kf(r) for r in sel}):
                ss = [r for r in sel if kf(r) == kv]
                out[f'{gname} | {kname} = {kv}'] = {lab: st([E[r['id']][model].get(q) for r in ss]) for q, lab in QTY}
    return out


def case_stats(R, E, model):
    """per distinct case on a card: the mean of the runs' log errors, then the statistics over cases"""
    out = collections.OrderedDict()
    for gname, fn in groups().items():
        cases = collections.defaultdict(list)
        for r in R:
            if fn(r):
                cases[(r['card'], r['case'])].append(r)
        blk = {}
        for q, lab in QTY:
            vals = []
            for k, rs in cases.items():
                v = [E[r['id']][model].get(q) for r in rs if E[r['id']][model].get(q) is not None]
                if v:
                    vals.append(float(np.exp(np.mean(np.log1p(v)))) - 1)
            blk[lab] = st(vals)
        blk['n_cases'] = len(cases)
        out[gname] = blk
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--scratch', default=None)
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    if out in (HERE, V1, V0):
        sys.exit('--out must be another folder')
    os.makedirs(out, exist_ok=True)
    scratch = a.scratch or os.path.join(out, 'v0-scratch')
    M1mod, M1, n1, P1 = load_v1()
    M0 = load_v0(scratch)
    R = [r for r in D.runs() if 'T' in r]
    E = {}
    rows = []
    for r in R:
        p1 = v1_call(M1, r)
        p0 = v0_call(M0, r)
        e1 = errors(r, p1)
        e0 = errors(r, p0)
        rec = {'v1': e1, 'v0': e0, 'v1_pred': p1, 'v0_pred': p0}
        if r['card_key'] == 'a1c0' and 'w' in r:
            b1 = v1_call(M1, r, borrowed=True)
            b0 = v0_call(M0, r, borrowed=True)
            rec['v1_borrowed'] = errors(r, b1)
            rec['v0_borrowed'] = errors(r, b0)
        E[r['id']] = rec
        row = {'id': r['id'], 'card': r['card'], 'session': r['session'], 'arm_e208': r['arm_e208'], 'arm': r['arm'], 'fmt': r['fmt'], 'kind': r['kind'],
               'mask': r['mask'], 'role': r['role'], 'form': r['form'], 'capped': r['capped'], 'shape_class': r['shape_class'], 'f_mhz': round(r['f'], 3),
               'meas_cyc_wall': round(r['cyc_wall'], 3), 'meas_cyc_mean': round(r['cyc_mean'], 3), 'meas_t_gemm': r['t_gemm'],
               'meas_w_over': (round(r['w'], 4) if 'w' in r else ''), 'meas_p_rest': (round(r['p_rest'], 4) if 'w' in r else ''),
               'V': (round(p1['args']['V'], 4) if p1['args']['V'] else ''), 'G': (round(p1['args']['G'], 4) if p1['args']['G'] is not None else ''),
               'v1_cyc_wall': round(p1['cyc_wall'], 3), 'v1_cyc_mean': round(p1['cyc_mean'], 3), 'v1_t_gemm': p1['t_gemm'],
               'v1_W': (round(p1['W'], 4) if 'W' in p1 else ''), 'v1_W_given_t': (round(e1['w_given_t_pred'], 4) if 'w_given_t_pred' in e1 else ''),
               'v0_cyc_wall': round(p0['cyc_wall'], 3), 'v0_cyc_mean': round(p0['cyc_mean'], 3), 'v0_t_gemm': p0['t_gemm'],
               'v0_W': (round(p0['W'], 4) if 'W' in p0 else ''), 'v0_W_given_t': (round(e0['w_given_t_pred'], 4) if 'w_given_t_pred' in e0 else ''),
               'energy_note': p1.get('energy_note', '') or p0.get('energy_note', '')}
        rows.append(row)
    res = {'label': 'UNREAD (see the head of this file): MM1-v1 as landed (25d2e74e) and MM1-v0 as frozen (2d1413f5), unchanged, on every '
                    'committed E208 run with a time figure', 'python': sys.version.split()[0], 'numpy': np.__version__,
           'v1_sha256sums_checked': n1, 'v0_frozen_sha256': V0_SHA, 'sessions': [s for s, _ in D.sessions()], 'n_runs': len(R),
           'n_runs_energy': sum(1 for r in R if 'w' in r),
           'stats v1 per run': stats_block(R, E, 'v1'), 'stats v0 per run': stats_block(R, E, 'v0'),
           'stats v1 per case': case_stats(R, E, 'v1'), 'stats v0 per case': case_stats(R, E, 'v0')}
    c0 = [r for r in R if r['card_key'] == 'a1c0' and 'w' in r]
    res['aifoundry1 card 0, borrowed footing (aifoundry2 card terms; NOT a forecast of either model)'] = {
        m: {lab: st([E[r['id']][m].get(q) for r in c0]) for q, lab in QTY} for m in ('v1_borrowed', 'v0_borrowed')}
    res['rows'] = [{'id': r['id'], 'errors_v1': E[r['id']]['v1'], 'errors_v0': E[r['id']]['v0'], 'args_v1': E[r['id']]['v1_pred']['args'],
                    'args_v0': E[r['id']]['v0_pred']['args'], 'notes': {'v1': E[r['id']]['v1_pred'].get('energy_note'), 'v0': E[r['id']]['v0_pred'].get('energy_note')}}
                   for r in R]
    json.dump(res, open(os.path.join(out, 'unread_e208.json'), 'w'), indent=1, default=float)
    with open(os.path.join(out, 'unread_e208.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for x in rows:
            w.writerow(x)
    # the tables
    L = ['# MM1-v1 and MM1-v0 on E208, UNREAD (desk; error = forecast / measured - 1, rms % (bias %))', '',
         f"Sessions {', '.join(res['sessions'])}; {res['n_runs']} runs with a time figure, {res['n_runs_energy']} with an energy figure.", '']
    for model in ('v1', 'v0'):
        S = res[f'stats {model} per run']
        C = res[f'stats {model} per case']
        L += [f'## MM1-{model} per run (per case beside)', '', '| group | ' + ' | '.join(lab for _, lab in QTY) + ' | under 3 W (W rms) |', '|---' * (len(QTY) + 2) + '|']
        for g in groups():
            b = S[g]
            c = C[g]
            cells = []
            for _, lab in QTY:
                x, y = b.get(lab), c.get(lab)
                cells.append((f"{x['rms_pct']} ({x['bias_pct']:+}) n={x['n']}" if x else 'NOT FORECAST') + (f" / case {y['rms_pct']} n={y['n']}" if y else ''))
            u = b.get('W over idle under 3 W (watts)')
            L.append(f'| {g} | ' + ' | '.join(cells) + f" | {u['rms_W'] if u else '-'} |")
        L.append('')
        for g in groups():
            if g == 'all':
                continue
            L += [f'### MM1-{model}, {g}, by class', '', '| class | ' + ' | '.join(lab for _, lab in QTY) + ' |', '|---' * (len(QTY) + 1) + '|']
            for k, b in S.items():
                if k.startswith(g + ' | '):
                    L.append(f"| {k[len(g) + 3:]} | " + ' | '.join((f"{b[lab]['rms_pct']} ({b[lab]['bias_pct']:+}) n={b[lab]['n']}" if b.get(lab) else '-') for _, lab in QTY) + ' |')
            L.append('')
    open(os.path.join(out, 'unread_e208.md'), 'w').write('\n'.join(L) + '\n')
    for model in ('v1', 'v0'):
        for g in groups():
            b = res[f'stats {model} per run'][g]
            print(model, g, {lab: (b[lab]['rms_pct'], b[lab]['bias_pct'], b[lab]['n']) if b.get(lab) else None for _, lab in QTY})
    for fn in ('unread_e208.json', 'unread_e208.csv', 'unread_e208.md'):
        print(sha(os.path.join(out, fn)), fn)


if __name__ == '__main__':
    main()
