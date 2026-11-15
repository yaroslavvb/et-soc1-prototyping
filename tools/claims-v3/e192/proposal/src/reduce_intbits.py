#!/usr/bin/env python3
"""Reduce an intbits session: energy and electrons per instruction for every arm, the contrasts, the ladders.

    python3 -B reduce_intbits.py OUT [OUT ...] --out intbits.json

Inputs per OUT dir: runs.jsonl and marks.jsonl (run_block.py) and telemetry.jsonl (the session's sampler, one JSON
object per line; other lines are skipped). Everything below is registered before any datum; nothing is tuned.

Per run (one device process of 0.4 s launches):
  t0 = start of its first launch, t1 = end of its last.
  Board power: the board samples from t0+1 s to min(t0+3 s, t1). Dip rule: a sample more than 2 W below the
    window's median is dropped (a reading caught between two launches); the number dropped is reported per run and
    per arm. P_board = mean of the rest.
  Core-rail power: the rail's samples from t0+2.5 s to t1, over idle, divided by the fraction a first-order average
    with tau = 1.05 s reaches over that window after a step at t0 (about 0.95 for a 4 s run):
    P_rail_over_idle = (mean - P_rail_idle) / frac.
  Rate: instructions in the loop bodies over the wall time from t0 to t1 (the gaps between launches are in both the
    power window and the time), the lab's basis. The device rate (cycles over the clock) is reported beside it.
  Temperature: the mean over the board window of the per-sensor raw codes when the sampler gives them ("pvt.c",
    converted with the firmware's published formula), else of the whole-degree die reading.
  Gates: every window sample at the pass's clock (within 1 MHz of the median), at least 5 board samples left, ok and
    check_bad = 0 on every launch, the same participant count on every launch. A failed run is reported and dropped.

Per pass: idle = the board and rail means over the marked idle periods of the pass (the last 7 s of the 10 s before
the first run and the first 7 s of the 10 s after the last). Anchor drift (last minus first anchor) is taken out
linearly in run order. Each arm then has E = (P - P_idle) / rate (pJ per instruction over idle), on the board and on
the core rail.

Temperature (rule 4): the pooled slope beta (W per C) of (P_arm - P_control) on (T_arm - T_control) over every
arm-control pair of every used pass, with one intercept per pair, is fitted once per meter; every arm's power is then
corrected to its control's temperature, P' = P - beta (T - T_control). Both the corrected (primary) and the raw
values are reported. The per-arm energy over idle carries the lab's leakage correction instead,
leak_slope(T) = 23.257/36 * exp((T - 80)/36) W per C times (T_run - T_idle) (board; rail x 0.79).

Contrasts: arm minus control in the same pass, E_arm - E_control (each over idle at its own rate), in pJ and
electrons per instruction (core rail at its measured voltage; board at 12 V), mean and standard error over the used
passes (the first pass is the warm-up and is reported but not used). A lone A-B contrast is reported as measured with
its SE, or as a bound when its 95 % interval contains zero.

Ladders, per pass, then mean and SE over passes (fJ per bit or per position):
  hamming_f2: slope and quadratic term of E(add.a.f2.kK) - E(add.z) on K = 0, 4, 8, 16.
  fields:     (E(add.a.fN) - E(add.z)) / 16 for N = 0..3; a12 = (E(add.a.f12) - E(add.z)) / 32;
              additivity: E(add.a.all) - E(add.z) - sum of the four fields.
  and_fields: (E(and.a.fN) - E(and.z)) / 16 for N = 1..3; and12 = mean of N = 1, 2.
  d12 = a12 - and12; f2 - f3 per bit for add and for and.
  carry ladders: S_cr = slope of E(add.cr.lL) on L = 0, 8, 16, 24, 31; S_crb the same for add.crb.lL; quadratic terms.
  combinations: C1 = (S_cr + S_crb - a12) / 2 (under a model linear in the flips of each port, of the result and of
    the carry vector, C1 is the price of one carry position); C2 = ((S_crb - d12) - (S_cr - and12)) / 2;
    C3 = and12 - C2.
  add.ripple and the field-0 arms are reported alone, outside every fit.
"""
import argparse
import collections
import json
import math
import os

import numpy as np

E_CH = 1.602176634e-19
TAU = 1.05
DIP_W = 2.0
RAIL_SHARE = 0.79
G_TS, H_TS, CAL5 = 57400, 249400, 4096      # the firmware's per-sensor conversion (public lab repo, E89)
CONTROL = {'add.same': 'nop', 'add.z': 'add.same', 'xor.z': 'add.z', 'and.z': 'add.z',
           'xor.a.f2': 'xor.z', 'and.a.f1': 'and.z', 'and.a.f2': 'and.z', 'and.a.f3': 'and.z',
           'add.cr.l8': 'add.cr.l0', 'add.cr.l16': 'add.cr.l0', 'add.cr.l24': 'add.cr.l0', 'add.cr.l31': 'add.cr.l0',
           'add.crb.l8': 'add.crb.l0', 'add.crb.l16': 'add.crb.l0', 'add.crb.l24': 'add.crb.l0',
           'add.crb.l31': 'add.crb.l0'}
LS = [0, 8, 16, 24, 31]
KS = [0, 4, 8, 16]


def control_of(a):
    if a == 'nop':
        return None
    return CONTROL.get(a, 'add.z')


def jl(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path) as f:
        for l in f:
            l = l.strip()
            if l.startswith('{') and l.endswith('}'):
                try:
                    out.append(json.loads(l))
                except ValueError:
                    pass
    return out


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def tel_arrays(tel):
    def g(s, *keys):
        for k in keys:
            if isinstance(s, dict) and k in s:
                s = s[k]
            elif isinstance(s, list) and isinstance(k, int) and k < len(s):
                s = s[k]
            else:
                return float('nan')
        return s if isinstance(s, (int, float)) else float('nan')
    t = np.array([s.get('t_ms', 0) for s in tel], float) / 1000.0
    board = np.array([g(s, 'board_w') for s in tel], float)
    rail = np.array([g(s, 'sp', 'minion_w', 0) for s in tel], float)
    mv = np.array([g(s, 'sp', 'minion_mv', 0) for s in tel], float)
    mhz = np.array([g(s, 'mhz', 'minion') for s in tel], float)
    temp = np.array([g(s, 'temp_c', 'minshire', 0) for s in tel], float)
    fine = np.full(len(tel), float('nan'))
    for i, s in enumerate(tel):
        pv = s.get('pvt') or {}
        c = pv.get('c') if isinstance(pv, dict) else None
        if isinstance(c, list) and len(c) == 34 and not pv.get('st') and not pv.get('f'):
            fine[i] = float(np.mean([code_to_c(x) for x in c]))
    return t, board, rail, mv, mhz, temp, fine


def rail_fraction(span):
    """mean over [2.5, span] s of a first-order response (tau TAU) to a step at 0"""
    w = span - 2.5
    if w <= 0.05:
        return float('nan')
    return 1.0 - TAU / w * (math.exp(-2.5 / TAU) - math.exp(-span / TAU))


def leak_slope(T):
    return 23.257 / 36.0 * math.exp((T - 80.0) / 36.0)


def reduce_dir(d):
    t, board, rail, mv, mhz, temp, fine = tel_arrays(jl(os.path.join(d, 'telemetry.jsonl')))
    rows = [r for r in jl(os.path.join(d, 'runs.jsonl')) if r.get('pass', -1) >= 0]
    marks = jl(os.path.join(d, 'marks.jsonl'))
    use_fine = bool(np.isfinite(fine).sum() > 0.9 * max(1, len(fine)))
    T_all = fine if use_fine else temp
    by = collections.OrderedDict()
    for r in rows:
        by.setdefault((r['host'], r['pass'], r['seq']), []).append(r)
    out = []
    for (host, p, seq), rs in by.items():
        t0 = min(r['t_start_ms'] for r in rs) / 1000.0
        t1 = max(r['t_end_ms'] for r in rs) / 1000.0
        wb = (t >= t0 + 1.0) & (t <= min(t0 + 3.0, t1))
        wr = (t >= t0 + 2.5) & (t <= t1)
        f = float(np.nanmedian(mhz[wb])) if wb.any() else float('nan')
        clk_ok = bool(wb.any() and np.all(np.abs(mhz[wb] - f) < 1.0))
        b = board[wb]
        b = b[np.isfinite(b)]
        med = float(np.median(b)) if len(b) else float('nan')
        keep = b[b >= med - DIP_W] if len(b) else b
        n_dip = int(len(b) - len(keep))
        instr = sum(r['instr_body'] for r in rs)
        dev_s = sum(r['cycles_max'] for r in rs) / ((f if f == f else 600.0) * 1e6)
        ok = (all(r['ok'] and r['check_bad'] == 0 for r in rs) and len({r['participants'] for r in rs}) == 1
              and clk_ok and len(keep) >= 5)
        ap = rs[0].get('approach') or {}
        out.append({'host': host, 'pass': p, 'seq': seq, 'arm': rs[0]['arm'], 'role': rs[0]['role'],
                    't0': t0, 't1': t1, 'launches': len(rs),
                    'P_board': float(np.mean(keep)) if len(keep) else float('nan'), 'board_dips': n_dip,
                    'P_rail_raw': float(np.nanmean(rail[wr])) if wr.any() else float('nan'),
                    'rail_frac': rail_fraction(t1 - t0),
                    'V_rail': float(np.nanmean(mv[wr]) / 1000.0) if wr.any() else float('nan'),
                    'T': float(np.nanmean(T_all[wb])) if wb.any() else float('nan'), 'T_fine': use_fine,
                    'mhz': f, 'rate': instr / (t1 - t0) if t1 > t0 else float('nan'),
                    'rate_device': instr / dev_s if dev_s > 0 else float('nan'), 'ok': ok,
                    'approach_on_protocol': ap.get('on_protocol'), 'approach_timed_out': ap.get('timed_out'),
                    'counts': {k: rs[0][k] for k in ('n_port_a', 'n_port_b', 'n_result', 'n_carry', 'n_cell', 'n_enc')},
                    'ret_over_body': sum(r['retired_counter'] for r in rs) / instr if instr else float('nan'),
                    'icache_miss': sum(r['icache_miss'] for r in rs), 'l1d_miss': sum(r['l1d_miss'] for r in rs)})
    idle = {}
    for key in {(r['host'], r['pass']) for r in out}:
        host, p = key
        w = np.zeros(len(t), bool)
        for m in marks:
            if m.get('kind') == 'idle' and m.get('host') == host and m.get('pass') == p:
                a, b = m['t0_ms'] / 1000.0, m['t1_ms'] / 1000.0
                if m.get('label') == 'before':
                    w |= (t >= b - 7.0) & (t <= b)
                else:
                    w |= (t >= a) & (t <= a + 7.0)
        idle[key] = {'P_board': float(np.nanmean(board[w])) if w.any() else float('nan'),
                     'P_rail': float(np.nanmean(rail[w])) if w.any() else float('nan'),
                     'T': float(np.nanmean(T_all[w])) if w.any() else float('nan'), 'n': int(w.sum())}
    return out, idle


def per_pass(runs, idle):
    res = collections.defaultdict(dict)
    for key, idl in idle.items():
        host, p = key
        rr = sorted([r for r in runs if r['host'] == host and r['pass'] == p and r['role'] != 'burnin' and r['ok']],
                    key=lambda r: r['seq'])
        anc = [r for r in rr if r['role'].startswith('anchor')]
        db = dr = 0.0
        s0 = rr[0]['seq'] if rr else 0
        if len(anc) == 2 and anc[1]['seq'] > anc[0]['seq']:
            span = anc[1]['seq'] - anc[0]['seq']
            db = (anc[1]['P_board'] - anc[0]['P_board']) / span
            dr = (anc[1]['P_rail_raw'] - anc[0]['P_rail_raw']) / span
            s0 = anc[0]['seq']
        for r in rr:
            if r['role'] != 'arm':
                continue
            pb = r['P_board'] - db * (r['seq'] - s0)
            pr = (r['P_rail_raw'] - dr * (r['seq'] - s0) - idl['P_rail']) / r['rail_frac'] + idl['P_rail']
            res[key][r['arm']] = {'P_board': pb, 'P_rail': pr, 'rate': r['rate'], 'V': r['V_rail'], 'T': r['T'],
                                  'counts': r['counts'], 'dips': r['board_dips'], 'idle': idl,
                                  'on_protocol': r['approach_on_protocol']}
    return res


def fit_beta(res, used, key):
    """pooled slope of (P_arm - P_control) on (T_arm - T_control), one intercept per pair"""
    pairs = collections.defaultdict(list)
    for p in used:
        d = res[p]
        for a in d:
            c = control_of(a)
            if c and c in d:
                dT = d[a]['T'] - d[c]['T']
                dP = d[a][key] - d[c][key]
                if dT == dT and dP == dP:
                    pairs[a].append((dT, dP))
    num = den = 0.0
    for a, v in pairs.items():
        if len(v) < 2:
            continue
        x = np.array([q[0] for q in v])
        y = np.array([q[1] for q in v])
        num += float(((x - x.mean()) * (y - y.mean())).sum())
        den += float(((x - x.mean()) ** 2).sum())
    return num / den if den > 0 else 0.0, den


def energies(res, used, beta, corrected):
    """E[p][arm] = (board, rail) pJ per instruction over idle, temperature-corrected to the control or leak-corrected"""
    E = {}
    for p in used:
        d = res[p]
        E[p] = {}
        for a, v in d.items():
            idl = v['idle']
            pb, pr = v['P_board'], v['P_rail']
            if corrected:
                c = control_of(a)
                # chain to the root of the control tree so every arm sits at the same reference temperature
                Tref = v['T']
                cc, seen = c, set()
                while cc and cc in d and cc not in seen:
                    seen.add(cc)
                    Tref = d[cc]['T']
                    cc = control_of(cc)
                if Tref == Tref and v['T'] == v['T']:
                    pb -= beta[0] * (v['T'] - Tref)
                    pr -= beta[1] * (v['T'] - Tref)
            else:
                if v['T'] == v['T'] and idl['T'] == idl['T']:
                    lk = leak_slope(v['T']) * (v['T'] - idl['T'])
                    pb -= lk
                    pr -= lk * RAIL_SHARE
            E[p][a] = ((pb - idl['P_board']) / v['rate'] * 1e12, (pr - idl['P_rail']) / v['rate'] * 1e12)
    return E


def mse(vals):
    v = np.array([x for x in vals if x == x], float)
    if len(v) == 0:
        return None
    se = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else None
    m = float(v.mean())
    rec = {'mean': m, 'se': se, 'n': int(len(v))}
    if se is not None:
        rec['reading'] = 'measured' if abs(m) > 2 * se else 'bound |x| < %.4g' % (abs(m) + 2 * se)
    return rec


def ladder(E, p, arms_x, idx):
    xs, ys = [], []
    for name, x in arms_x:
        if name in E[p]:
            xs.append(x)
            ys.append(E[p][name][idx])
    if len(xs) < 3:
        return float('nan'), float('nan')
    xs, ys = np.array(xs, float), np.array(ys, float)
    s1 = np.polyfit(xs, ys, 1)[0]
    q = np.polyfit(xs, ys, 2)[0] if len(xs) >= 4 else float('nan')
    return float(s1), float(q)


def ladders(E, used):
    out = {}
    for idx, meter in ((0, 'board'), (1, 'rail')):
        per = collections.defaultdict(list)
        for p in used:
            e = E[p]
            g = lambda a: e[a][idx] if a in e else float('nan')
            z, az = g('add.z'), g('and.z')
            ham = [('add.z', 0), ('add.a.f2.k4', 4), ('add.a.f2.k8', 8), ('add.a.f2', 16)]
            s, q = ladder(E, p, ham, idx)
            per['hamming_f2_slope_fJ'].append(s * 1000)
            per['hamming_f2_quad_fJ'].append(q * 1000)
            fld = [(g('add.a.f%d' % n) - z) / 16 * 1000 for n in range(4)]
            for n in range(4):
                per['add_f%d_fJ_per_bit' % n].append(fld[n])
            a12 = (g('add.a.f12') - z) / 32 * 1000
            per['add_f12_fJ_per_bit'].append(a12)
            per['additivity_all_minus_fields_pJ'].append(g('add.a.all') - z - sum(f * 16 / 1000 for f in fld))
            per['f12_minus_f1_f2_pJ'].append(g('add.a.f12') - z - (fld[1] + fld[2]) * 16 / 1000)
            andf = [(g('and.a.f%d' % n) - az) / 16 * 1000 for n in (1, 2, 3)]
            for n, v in zip((1, 2, 3), andf):
                per['and_f%d_fJ_per_bit' % n].append(v)
            and12 = (andf[0] + andf[1]) / 2
            per['and12_fJ_per_bit'].append(and12)
            r12 = a12 - and12
            per['d12_a12_minus_and12_fJ_per_bit'].append(r12)
            per['add_f2_minus_f3_fJ_per_bit'].append(fld[2] - fld[3])
            per['and_f2_minus_f3_fJ_per_bit'].append(andf[1] - andf[2])
            scr, qcr = ladder(E, p, [('add.cr.l%d' % L, L) for L in LS], idx)
            scb, qcb = ladder(E, p, [('add.crb.l%d' % L, L) for L in LS], idx)
            scr, scb, qcr, qcb = scr * 1000, scb * 1000, qcr * 1000, qcb * 1000
            per['S_cr_fJ_per_position'].append(scr)
            per['S_crb_fJ_per_position'].append(scb)
            per['S_cr_quad_fJ'].append(qcr)
            per['S_crb_quad_fJ'].append(qcb)
            per['C1_carry_fJ_per_position'].append((scr + scb - a12) / 2)
            per['C2_fJ_per_bit'].append(((scb - r12) - (scr - and12)) / 2)
            per['C3_fJ_per_bit'].append(and12 - ((scb - r12) - (scr - and12)) / 2)
            per['ripple_minus_add_z_pJ'].append(g('add.ripple') - z)
        out[meter] = {k: mse(v) for k, v in per.items()}
    return out


def summarize(res):
    passes = sorted(res)
    used = passes[1:] if len(passes) > 1 else passes   # the first pass is the warm-up
    out = {'passes': [list(p) for p in passes], 'warmup': list(passes[0]) if passes else None, 'arms': {},
           'registered': {'dip_W': DIP_W, 'tau_s': TAU, 'rate': 'instructions over wall time t0..t1',
                          'temperature': 'pooled arm-control slope, corrected to the control (primary)'}}
    bb, nb = fit_beta(res, used, 'P_board')
    br, nr = fit_beta(res, used, 'P_rail')
    out['beta_W_per_C'] = {'board': bb, 'rail': br, 'sum_dT2': nb}
    Ec = energies(res, used, (bb, br), True)
    El = energies(res, used, (bb, br), False)
    for a in sorted({a for p in used for a in res[p]}):
        rec = {'dips': sum(res[p][a]['dips'] for p in used if a in res[p]),
               'off_protocol_runs': sum(1 for p in used if a in res[p] and res[p][a]['on_protocol'] is False)}
        rec['pJ_board_over_idle'] = mse([El[p][a][0] for p in used if a in El[p]])
        rec['pJ_rail_over_idle'] = mse([El[p][a][1] for p in used if a in El[p]])
        c = control_of(a)
        if c:
            rec['control'] = c
            for tag, E in (('', Ec), ('_uncorrected', El)):
                both = [p for p in used if a in E[p] and c in E[p]]
                rec['contrast_pJ_board' + tag] = mse([E[p][a][0] - E[p][c][0] for p in both])
                rec['contrast_pJ_rail' + tag] = mse([E[p][a][1] - E[p][c][1] for p in both])
            both = [p for p in used if a in res[p] and c in res[p]]
            rec['contrast_W_board'] = mse([res[p][a]['P_board'] - res[p][c]['P_board'] for p in both])
            V = np.nanmean([res[p][a]['V'] for p in both]) if both else float('nan')
            m = rec['contrast_pJ_rail']
            if m and V == V:
                rec['contrast_electrons_rail'] = m['mean'] * 1e-12 / (E_CH * V)
            m = rec['contrast_pJ_board']
            if m:
                rec['contrast_electrons_12V'] = m['mean'] * 1e-12 / (E_CH * 12.0)
        out['arms'][a] = rec
    out['ladders'] = ladders(Ec, used)
    out['ladders_uncorrected'] = ladders(El, used)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--out', default='intbits.json')
    a = ap.parse_args()
    allruns, allidle = [], {}
    for d in a.dirs:
        r, i = reduce_dir(d)
        allruns += r
        allidle.update(i)
    res = per_pass(allruns, allidle)
    s = summarize(res)
    s['runs'] = allruns
    with open(a.out, 'w') as f:
        json.dump(s, f, indent=1)
    for arm, rec in sorted(s['arms'].items()):
        m = rec.get('pJ_board_over_idle') or {}
        c = rec.get('contrast_pJ_board') or {}
        print('%-14s %8s pJ over idle   vs %-11s %8s +- %-7s pJ  dips %d' % (
            arm, '%.3f' % m['mean'] if m else '-', rec.get('control', '-'), '%.3f' % c['mean'] if c else '-',
            '%.3f' % c['se'] if c and c.get('se') is not None else '-', rec['dips']))
    for k, v in s['ladders']['board'].items():
        if v:
            print('%-40s %9.3f +- %s' % (k, v['mean'], '%.3f' % v['se'] if v.get('se') is not None else '-'))
    print('beta W/C', json.dumps(s['beta_W_per_C']))


if __name__ == '__main__':
    main()
