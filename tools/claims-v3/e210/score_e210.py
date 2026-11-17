#!/usr/bin/env python3
"""E210 (Q202): the frozen scorer of the switch test. It refuses to run if forecast-e210.json or points-e210.json differ from their frozen bytes.

RE-FROZEN BEFORE ANY E210 DATUM by E210.md amendment A1 (Q202, lane fix-e210, Tue 17 Nov 2026; verify-e210's findings 2, 3 and 5). The first
freeze (sha256 b3aff4943af4f33a72865a14f821e2701b06e26fb95836052450bc43a3fa27e1) crashed on a run with counted launches but no telemetry sample
inside them (mhz_min / mhz_max None: TypeError), on a non-finite power, and on a random run with no power reading (the random-drift report).
What changed, and nothing else: (1) a run whose clock or power reading is missing, None or not finite is set aside (incomplete), never a crash;
the random-drift report reads the random runs with finite powers only; (2) R0 reads the checks the processes printed (A1 item 5): FAIL on any
printed check not exact or approx; a process that printed none is REPORTED apart by name (R0.missing_REPORTED), never a FAIL; NO DATA when no
check was read at all; (3) a REPORTED pattern-level sign test beside H1-H4 (A1 item 3). Every other rule, band, threshold and output field is
the first freeze's, and on every input on which the first freeze did not crash it gives the same verdicts, cells and numbers but R0's (the
fix-e210 lane's equivalence check: logs in the lane's folder; A1 item 6).

    /usr/bin/python3 -I -B tools/claims-v3/e210/score_e210.py DATA.json --out SCORED.json [--txt SCORED.txt]
    /usr/bin/python3 -I -B tools/claims-v3/e210/score_e210.py --selftest <out dir>      (the stand-in self-test: every rule made to PASS and FAIL)

DATA.json (the kit's reducer writes it): {"experiment": "E210", "runs": {"<run id of points-e210.json>": RUN, ...}} with, per run that ran:
  RUN = {"ran": true, "case": "<kind>@<S1|S2>", "p_work_w", "p_rest_w", "t_gemm_s", "cycles_per_op" (the median over the counted launches of the
         host's cycles_per_op: the kernel counter's mean over minions), "mhz_min", "mhz_max" (the lowest and highest counted sample),
         "checks": [every check of C of the run: "exact" | "approx" | "wrong"], "n_launch_counted", "record": {"arm", "type", "minions", "shire_mask"}}
  counted launches: launch >= 0, ok, wall_s >= 0.1 s and the kernel clock (cycles_max / wall) in 590-610 MHz (the check launches never count).
  J over idle a GEMM of a run = (p_work - p_rest) t_gemm.
THE RULES (registered in E210.md section 7; a case with no complete block is NO DATA, never a failure):
  R0  every check of C of every run (blocks, ties, the probe) exact or approx: one verdict; a FAIL labels every other verdict. (A1 item 5:
      FAIL when any check a process printed is not exact or approx; PASS when checks were read and all are good; NO DATA when none was read;
      a process that printed no check is REPORTED by name in R0.missing_REPORTED: its run is already out of its block by Q.)
  Q   a block (R, P, P, R) is complete when its four runs ran, each with at least one counted launch, every check of C good, its record the
      case's (arm, fp32, 1,024 minions, 0xffffffff) and every counted sample at 590-610 MHz; a test case needs 2 complete blocks, a control or
      a reported case 1; else NO DATA.
  T   time equality, per complete block: the pattern runs' mean cycles an op within +-0.1% of the flanking random runs' mean, and their mean
      t_gemm within +-0.1% of the random runs'; a case passes when every complete block does. A case that fails T is reported, not scored
      for switches (out of B5, B10 and H).
  the case's measured dJ = the mean over its complete blocks of mean(J(P1), J(P2)) - mean(J(R1), J(R2)); SE = max(sd of the block values /
      sqrt(n), 0.11 W x t_gemm / sqrt(n)), n its complete blocks.
  B5  the switch route's band, per scored test case: |dJ_R1 - dJ| <= max(0.05 D_S, 2 SE) (D_S the committed D at the shape, in J; every band
      absolute, so a pattern under about 3 W is treated as any other); the rule PASSES when at least 75% of the scored test cases pass (at
      least 6 scored, else TOO FEW). B10 (10% of D) the same, REPORTED.
  H   head to head, R1 against R4 (H1), R3 (H2), R3L (H3) and R2 (H4, the cases it forecasts): per scored test case both routes forecast,
      e = dJ - forecast; decided when ||e_R1| - |e_k|| >= 2 SE, else a tie (dropped); the exact two-sided sign test at 0.05 over the decided
      cases: R1 BETTER, <k> BETTER or UNDECIDED (under 6 decided cases it cannot decide).
REPORTED (no verdict): each route's rms and mean error over the scored test cases (W and fractions of D); a paired bootstrap of mean |e_R1| -
  mean |e_k| (10,000 resamples of the cases, seed "E210|bootstrap", the 2.5-97.5% interval); R1's high column and R1pure; the card's own b
  (least squares of dJ - dL on dS over the scored test cases, through the origin) against the calibrated b_S, as kappa; the controls (zeros,
  ones, sparse50) against E206 and against ones' transfer; the reported case (arow50) by every route that forecasts it; the random runs' drift.
  A1 item 3, the PATTERN-LEVEL SIGN TEST (REPORTED beside H1-H4; the registered verdicts stay): per pattern (kind) with a scored test case both
  routes forecast, d_p = the mean over its such cases of (|e_R1| - |e_k|) / D_S and SE_p = sqrt(sum of (SE_J / D_S)^2) / n_p; decided when
  |d_p| >= 2 SE_p, else a tie (dropped); the exact two-sided sign test at 0.05 over the decided patterns (8 patterns: it decides only at 6 of 6,
  7 of 7 or 8 of 8): R1 BETTER, <k> BETTER or UNDECIDED (reported.pattern_level_sign_test_REPORTED.H1p ... H4p).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = {'forecast-e210.json': 'dbc2d3f3b1d4796f1504424bc30cf40648840c1064754a6f8012d926be93fe67', 'points-e210.json': '5773671b3cc6af8aff29c3332d4644bb3e28200f344e940da46474945cc4dd6a'}
SIGMA_FLOOR_W = 0.11
BAND, BAND_REP, PASS_SHARE, MIN_SCORED = 0.05, 0.10, 0.75, 6
T_BAND = 0.001
MHZ = (590.0, 610.0)
ROUTES_H = [('H1', 'R4'), ('H2', 'R3'), ('H3', 'R3L'), ('H4', 'R2')]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def num(x):
    """A1 item 6: a reading the rules can use - an int or a float (not a bool), finite."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def crit_two_sided(n, alpha=0.05):
    if n == 0:
        return 1
    tail = 0.0
    for w in range(n, -1, -1):
        tail += math.comb(n, w) / 2 ** n
        if tail > alpha / 2:
            return w + 1
    return 0


def load_frozen(check=True):
    if check:
        for f, want in FROZEN.items():
            got = sha(os.path.join(HERE, f))
            if got != want:
                print(f'REFUSED: {f} sha256 {got} is not the frozen {want}')
                sys.exit(4)
    return json.load(open(os.path.join(HERE, 'forecast-e210.json'))), json.load(open(os.path.join(HERE, 'points-e210.json')))


def run_ok(r, case, pts_case):
    """(complete?, why)"""
    if not r or not r.get('ran'):
        return False, 'not run'
    if r.get('case') != case:
        return False, f"case {r.get('case')} is not {case}"
    if (r.get('n_launch_counted') or 0) < 1:
        return False, 'no counted launch'
    ch = r.get('checks') or []
    if not ch or any(c not in ('exact', 'approx') for c in ch):
        return False, f'check of C {ch}'
    rec = r.get('record') or {}
    if rec.get('arm') != pts_case['arm'] or rec.get('type') != 'fp32' or rec.get('minions') != 1024 or rec.get('shire_mask') != '0xffffffff':
        return False, f'record {rec}'
    lo, hi = r.get('mhz_min'), r.get('mhz_max')       # A1 item 6: missing, None or not finite is a clock not read: the run is set aside
    if not (num(lo) and num(hi) and MHZ[0] <= lo and hi <= MHZ[1]):
        return False, f"clock {lo}-{hi} MHz"
    for k in ('p_work_w', 'p_rest_w', 't_gemm_s', 'cycles_per_op'):
        if not num(r.get(k)):
            return False, f'no {k}'
    return True, ''


def J(r):
    return (r['p_work_w'] - r['p_rest_w']) * r['t_gemm_s']


def score(data, fc, pts):
    runs = data.get('runs', {})
    cases = {c['case']: c for c in pts['cases']}
    out = {'experiment': 'E210', 'frozen': FROZEN, 'R0': None, 'cases': {}, 'rules': {}, 'reported': {}}
    # R0 as amended by A1 item 5: the checks the processes printed; a process that printed none is REPORTED apart, never a FAIL
    bad_checks, missing, n_read = [], [], 0
    srcs = [(k, r) for k, r in runs.items() if isinstance(r, dict) and r.get('ran')]
    for k in ('probe', 'smoke'):
        srcs += [(f'{k}:{nm}', r) for nm, r in (data.get(k) or {}).items()]
    for k, r in srcs:
        ch = (r.get('checks') if isinstance(r, dict) else None) or []
        if not ch:
            missing.append(k)
            continue
        n_read += len(ch)
        if any(c not in ('exact', 'approx') for c in ch):
            bad_checks.append(k)
    out['R0'] = {'verdict': 'FAIL' if bad_checks else ('PASS' if n_read else 'NO DATA'), 'bad': sorted(bad_checks),
                 'missing_REPORTED': sorted(missing), 'checks_read': n_read}
    for cid, c in cases.items():
        if c['kind'] == 'random':
            continue
        f = fc['cases'][cid]
        cal = fc['calibration'][c['shape']]
        D = cal['D_J']
        blocks = [b for b in pts['blocks'] if b['kind'] == c['kind'] and b['shape'] == c['shape']]
        vals, bl = [], []
        for b in blocks:
            rr = [runs.get(x) for x in b['runs']]
            oks = [run_ok(rr[i], (c['case'] if i in (1, 2) else f"random@{c['shape']}"), cases[c['case'] if i in (1, 2) else f"random@{c['shape']}"])
                   for i in range(4)]
            rec = {'block': b['block'], 'runs': b['runs']}
            if not all(o[0] for o in oks):
                rec['complete'] = False
                rec['why'] = '; '.join(f'{b["runs"][i]}: {o[1]}' for i, o in enumerate(oks) if not o[0])
                bl.append(rec)
                continue
            R1, P1, P2, R2 = rr
            dj = (J(P1) + J(P2)) / 2 - (J(R1) + J(R2)) / 2
            cp = (P1['cycles_per_op'] + P2['cycles_per_op']) / (R1['cycles_per_op'] + R2['cycles_per_op']) - 1
            tg = (P1['t_gemm_s'] + P2['t_gemm_s']) / (R1['t_gemm_s'] + R2['t_gemm_s']) - 1
            rec.update({'complete': True, 'dJ': dj, 'dW': dj / ((P1['t_gemm_s'] + P2['t_gemm_s']) / 2), 'cycles_rel': cp, 't_gemm_rel': tg,
                        'T': abs(cp) <= T_BAND and abs(tg) <= T_BAND, 't_gemm_s': (P1['t_gemm_s'] + P2['t_gemm_s']) / 2})
            vals.append(rec)
            bl.append(rec)
        need = 2 if c['role'] == 'test' else 1
        rec = {'case': cid, 'role': c['role'], 'shape': c['shape'], 'blocks': bl, 'n_complete': len(vals)}
        if len(vals) < need:
            rec['Q'] = 'NO DATA'
            out['cases'][cid] = rec
            continue
        n = len(vals)
        t = statistics.mean(v['t_gemm_s'] for v in vals)
        dj = statistics.mean(v['dJ'] for v in vals)
        sd = statistics.stdev([v['dJ'] for v in vals]) if n > 1 else 0.0
        se = max(sd / math.sqrt(n), SIGMA_FLOOR_W * t / math.sqrt(n))
        rec.update({'Q': 'OK', 'dJ': dj, 'dW': dj / t, 'SE_J': se, 'SE_W': se / t, 'frac_of_D': dj / D, 'T': all(v['T'] for v in vals)})
        errs = {}
        for q, v in f['routes'].items():
            if isinstance(v, (int, float)):
                errs[q] = {'forecast_J': v, 'error_J': dj - v, 'error_W': (dj - v) / t, 'error_frac_of_D': (dj - v) / D}
        rec['errors'] = errs
        rec['scored'] = c['role'] == 'test' and rec['T']
        if rec['scored'] and 'R1' in errs:
            band = max(BAND * D, 2 * se)
            rec['B5'] = {'band_J': band, 'pass': abs(errs['R1']['error_J']) <= band}
            band10 = max(BAND_REP * D, 2 * se)
            rec['B10'] = {'band_J': band10, 'pass': abs(errs['R1']['error_J']) <= band10}
        out['cases'][cid] = rec
    scored = [r for r in out['cases'].values() if r.get('scored') and 'B5' in r]
    for name, key in (('B5', 'B5'), ('B10_REPORTED', 'B10')):
        n = len(scored)
        k = sum(1 for r in scored if r[key]['pass'])
        need = math.ceil(PASS_SHARE * n) if n else 0
        verdict = 'NO DATA' if n == 0 else ('TOO FEW' if n < MIN_SCORED else ('PASS' if k >= need else 'FAIL'))
        out['rules'][name] = {'verdict': verdict, 'pass': k, 'scored': n, 'needed': need, 'cases': {r['case']: r[key]['pass'] for r in scored}}
    hs = [r for r in out['cases'].values() if r.get('scored')]
    for h, other in ROUTES_H:
        w1 = wk = ties = 0
        per = {}
        pairs = []
        for r in hs:
            e = r['errors']
            if 'R1' not in e or other not in e:
                continue
            a, b = abs(e['R1']['error_J']), abs(e[other]['error_J'])
            pairs.append((a, b, r['shape']))
            if abs(a - b) < 2 * r['SE_J']:
                ties += 1
                per[r['case']] = 'tie'
            elif a < b:
                w1 += 1
                per[r['case']] = 'R1'
            else:
                wk += 1
                per[r['case']] = other
        nd = w1 + wk
        cr = crit_two_sided(nd)
        verdict = 'R1 BETTER' if nd and w1 >= cr else (f'{other} BETTER' if nd and wk >= cr else 'UNDECIDED')
        boot = None
        if pairs:
            rng = random.Random('E210|bootstrap')
            diffs = []
            for _ in range(10000):
                smp = [pairs[rng.randrange(len(pairs))] for _ in pairs]
                diffs.append(sum(a - b for a, b, _ in smp) / len(smp))
            diffs.sort()
            boot = {'mean_abs_e_R1_minus_other_J': sum(a - b for a, b, _ in pairs) / len(pairs), 'p2_5': diffs[249], 'p97_5': diffs[9749]}
        out['rules'][h] = {'verdict': verdict, 'other': other, 'R1_wins': w1, 'other_wins': wk, 'ties': ties, 'decided': nd,
                           'wins_needed': cr if nd else None, 'cases': per, 'bootstrap_REPORTED': boot}
    rep = out['reported']
    # A1 item 3 (verify-e210's finding 3): the same head to head with a PATTERN as the unit (a pattern's S1 and S2 cases are not independent
    # coins); REPORTED beside H1-H4, never a verdict
    pl = {}
    for h, other in ROUTES_H:
        units = {}
        for r in hs:
            e = r['errors']
            if 'R1' not in e or other not in e:
                continue
            ds = fc['calibration'][r['shape']]['D_J']
            u = units.setdefault(cases[r['case']]['kind'], {'d': [], 's2': [], 'cases': []})
            u['d'].append((abs(e['R1']['error_J']) - abs(e[other]['error_J'])) / ds)
            u['s2'].append((r['SE_J'] / ds) ** 2)
            u['cases'].append(r['case'])
        w1 = wk = ties = 0
        per = {}
        for kd, u in units.items():
            n = len(u['d'])
            dp, sp = sum(u['d']) / n, math.sqrt(sum(u['s2'])) / n
            if abs(dp) < 2 * sp:
                ties += 1
                res = 'tie'
            elif dp < 0:
                w1 += 1
                res = 'R1'
            else:
                wk += 1
                res = other
            per[kd] = {'cases': u['cases'], 'd_frac_of_D': dp, 'SE_frac_of_D': sp, 'result': res}
        nd = w1 + wk
        cr = crit_two_sided(nd)
        pl[h + 'p'] = {'verdict': 'R1 BETTER' if nd and w1 >= cr else (f'{other} BETTER' if nd and wk >= cr else 'UNDECIDED'), 'other': other,
                       'units': len(units), 'R1_wins': w1, 'other_wins': wk, 'ties': ties, 'decided': nd, 'wins_needed': cr if nd else None,
                       'patterns': per}
    rep['pattern_level_sign_test_REPORTED'] = pl
    for q in ('R1', 'R1_hi', 'R1pure', 'R3', 'R3L', 'R2', 'R4', 'R1g'):
        es = [r['errors'][q] for r in hs if q in r.get('errors', {})]
        if es:
            rep[f'{q}_over_scored'] = {'n': len(es), 'rms_W': math.sqrt(sum(e['error_W'] ** 2 for e in es) / len(es)),
                                       'mean_W': sum(e['error_W'] for e in es) / len(es),
                                       'rms_frac_of_D': math.sqrt(sum(e['error_frac_of_D'] ** 2 for e in es) / len(es))}
    for s in ('S1', 'S2'):
        xs, ys = [], []
        for r in hs:
            if r['shape'] != s:
                continue
            f = fc['cases'][r['case']]
            macs = pts['shapes'][s]['macs_per_gemm']
            if f.get('ungated_all_valid'):
                xs.append(f['dS_lo_per_mac'] * macs)
                ys.append(r['dJ'] - f['dL_J'])
        if len(xs) >= 2:
            b = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
            rep[f'card_b_{s}_POST_HOC'] = {'b_J_per_switch': b, 'kappa_switches_per_J': 1 / b if b else None, 'n': len(xs),
                                           'calibrated_kappa': fc['calibration'][s]['kappa_S_switches_per_J']}
    ctl = {}
    for cid, r in out['cases'].items():
        if r['role'] in ('control', 'reported') and r.get('Q') == 'OK':
            ctl[cid] = {'dW': r['dW'], 'frac_of_D': r['frac_of_D'], 'errors_W': {q: e['error_W'] for q, e in r['errors'].items()}}
    rep['controls_and_reported'] = ctl
    rs = [(k, v) for k, v in sorted(runs.items()) if isinstance(v, dict) and v.get('ran') and str(v.get('case', '')).startswith('random@')
          and num(v.get('p_work_w')) and num(v.get('p_rest_w')) and k.split('-')[0].isdigit()]     # A1 item 6: finite powers only
    if len(rs) >= 3:
        by = {}
        for k, v in rs:
            by.setdefault(v['case'], []).append((int(k.split('-')[0]), (v['p_work_w'] - v['p_rest_w'])))
        rep['random_drift'] = {c: {'n': len(x), 'first_W': x[0][1], 'last_W': x[-1][1]} for c, x in by.items()}
    return out


def text(out):
    r0 = out['R0']
    L = [f"E210 scored: R0 {r0['verdict']}" + (f" (wrong: {', '.join(r0['bad'])})" if r0['bad'] else '')
         + (f"; printed no check (REPORTED, A1 item 5): {', '.join(r0['missing_REPORTED'])}" if r0.get('missing_REPORTED') else ''), '']
    for name, r in out['rules'].items():
        if name.startswith('H'):
            L.append(f"{name} R1 against {r['other']}: {r['verdict']} (R1 {r['R1_wins']}, {r['other']} {r['other_wins']}, ties {r['ties']}; needed {r['wins_needed']})")
        else:
            L.append(f"{name}: {r['verdict']} ({r['pass']} of {r['scored']} scored test cases; needed {r['needed']})")
    for name, r in out['reported'].get('pattern_level_sign_test_REPORTED', {}).items():
        L.append(f"{name} (REPORTED, A1 item 3: the pattern as the unit) R1 against {r['other']}: {r['verdict']} (R1 {r['R1_wins']}, {r['other']} "
                 f"{r['other_wins']}, ties {r['ties']} of {r['units']} patterns; needed {r['wins_needed']})")
    L.append('')
    for cid, r in out['cases'].items():
        if r.get('Q') != 'OK':
            L.append(f"{cid:16s} {r['role']:9s} {r.get('Q')} ({r['n_complete']} complete blocks)")
            continue
        e = r['errors']
        g = lambda q: f"{e[q]['error_W']:+7.3f}" if q in e else '    n/f'  # noqa: E731
        L.append(f"{cid:16s} {r['role']:9s} dW {r['dW']:+8.3f} W (SE {r['SE_W']:.3f}; {r['frac_of_D']:+.4f} D) T {'PASS' if r['T'] else 'FAIL'} "
                 f"B5 {('PASS' if r['B5']['pass'] else 'FAIL') if 'B5' in r else '-':4s} | errors W: R1 {g('R1')} R3 {g('R3')} R3L {g('R3L')} R2 {g('R2')} R4 {g('R4')}")
    return '\n'.join(L) + '\n'


# ------------------------------------------------------------------ the stand-in self-test
def synth(fc, pts, dj_of, mod=None, sig=0.0, seed='x'):
    """runs whose block differences are dj_of(case) exactly (sig 0) or with noise; random at E206's measured W"""
    rng = random.Random(seed)
    runs = {}
    for r in pts['runs']:
        s = r['shape']
        cal = fc['calibration'][s]
        t = cal['t_gemm_s']
        wr = cal['W_random']
        if r['kind'] == 'random':
            w = wr
        else:
            w = wr + dj_of(r['case']) / t
        runs[r['run']] = {'ran': True, 'case': r['case'], 'p_rest_w': 24.5, 'p_work_w': 24.5 + w + rng.gauss(0, sig), 't_gemm_s': t,
                          'cycles_per_op': 537.98 if s == 'S1' else 831.72, 'mhz_min': 600.0, 'mhz_max': 600.0, 'checks': ['approx'],
                          'n_launch_counted': 13, 'record': {'arm': pts['shapes'][s]['arm'], 'type': 'fp32', 'minions': 1024, 'shire_mask': '0xffffffff'}}
    if mod:
        mod(runs)
    return {'experiment': 'E210', 'runs': runs}


def selftest(outdir):
    fc, pts = load_frozen(check=True)
    os.makedirs(outdir, exist_ok=True)
    tests = [c['case'] for c in pts['cases'] if c['role'] == 'test']
    D = {s: fc['calibration'][s]['D_J'] for s in fc['calibration']}
    t = {s: fc['calibration'][s]['t_gemm_s'] for s in fc['calibration']}

    def route(q):
        def f(cid):
            v = fc['cases'][cid]['routes'].get(q)
            return v if isinstance(v, (int, float)) else fc['cases'][cid]['routes']['R4']
        return f

    def decided_wins(meas, other):
        """independent arithmetic: per test case, the stand-in's measured dJ against R1 and `other` (SE = the floor, sig 0, 3 blocks)"""
        w1 = wk = 0
        for cid in tests:
            r = fc['cases'][cid]['routes']
            if not isinstance(r.get('R1'), (int, float)) or not isinstance(r.get(other), (int, float)):
                continue
            s = fc['cases'][cid]['shape']
            se = SIGMA_FLOOR_W * t[s] / math.sqrt(3)
            a, b = abs(meas(cid) - r['R1']), abs(meas(cid) - r[other])
            if abs(a - b) < 2 * se:
                continue
            if a < b:
                w1 += 1
            else:
                wk += 1
        n = w1 + wk
        cr = crit_two_sided(n)
        return 'R1 BETTER' if n and w1 >= cr else (f'{other} BETTER' if n and wk >= cr else 'UNDECIDED')

    def b5_expect(meas):
        k = sum(1 for cid in tests if abs(meas(cid) - fc['cases'][cid]['routes']['R1']) <=
                max(BAND * D[fc['cases'][cid]['shape']], 2 * SIGMA_FLOOR_W * t[fc['cases'][cid]['shape']] / math.sqrt(3)))
        n = len(tests)
        return 'PASS' if k >= math.ceil(PASS_SHARE * n) else 'FAIL'

    def shift(q, frac):
        return lambda cid: route(q)(cid) + frac * D[fc['cases'][cid]['shape']]

    def pattern_wins(meas, other):
        """A1 item 3, independent arithmetic: the pattern-level sign test on the stand-in's measured dJ (SE = the floor, sig 0, 3 blocks)"""
        units = {}
        for cid in tests:
            r = fc['cases'][cid]['routes']
            if not isinstance(r.get('R1'), (int, float)) or not isinstance(r.get(other), (int, float)):
                continue
            s = fc['cases'][cid]['shape']
            se = SIGMA_FLOOR_W * t[s] / math.sqrt(3)
            u = units.setdefault(fc['cases'][cid]['kind'], [])
            u.append(((abs(meas(cid) - r['R1']) - abs(meas(cid) - r[other])) / D[s], (se / D[s]) ** 2))
        w1 = wk = 0
        for u in units.values():
            dp, sp = sum(x for x, _ in u) / len(u), math.sqrt(sum(y for _, y in u)) / len(u)
            if abs(dp) < 2 * sp:
                continue
            if dp < 0:
                w1 += 1
            else:
                wk += 1
        n = w1 + wk
        cr = crit_two_sided(n)
        return 'R1 BETTER' if n and w1 >= cr else (f'{other} BETTER' if n and wk >= cr else 'UNDECIDED')

    cases = []
    m = route('R1')
    cases.append(('A measured = R1 exactly', synth(fc, pts, m), {'R0': 'PASS', 'B5': 'PASS', 'H1': decided_wins(m, 'R4'), 'H2': decided_wins(m, 'R3'),
                                                                   'H3': decided_wins(m, 'R3L'), 'H4': 'UNDECIDED', 'T:hd4@S1': True,
                                                                   'scored:hd4@S1': True, 'Q:signs@S1': 'OK', 'R0missing': 0,
                                                                   'H1p': pattern_wins(m, 'R4'), 'H2p': pattern_wins(m, 'R3'),
                                                                   'H3p': pattern_wins(m, 'R3L'), 'H4p': 'UNDECIDED'}))
    m = route('R3L')
    cases.append(('B measured = R3L', synth(fc, pts, m), {'B5': b5_expect(m), 'H3': decided_wins(m, 'R3L'), 'H3p': pattern_wins(m, 'R3L')}))
    m = route('R4')
    cases.append(('C measured = the null R4', synth(fc, pts, m), {'B5': b5_expect(m), 'H1': decided_wins(m, 'R4'), 'H1p': pattern_wins(m, 'R4')}))
    m = shift('R1', 0.04)
    cases.append(('D1 measured = R1 + 0.04 D (inside the band)', synth(fc, pts, m), {'B5': 'PASS'}))
    m = shift('R1', 0.06)
    cases.append(('D2 measured = R1 + 0.06 D (outside the band)', synth(fc, pts, m), {'B5': 'FAIL'}))
    m = route('R3')
    cases.append(('E measured = raw R3', synth(fc, pts, m), {'B5': b5_expect(m), 'H2': decided_wins(m, 'R3')}))

    def slow(runs):   # one test case's pattern runs 0.2% slower in cycles: T FAILS there; the case is reported, not scored
        for r in pts['runs']:
            if r['case'] == 'hd4@S1':
                runs[r['run']]['cycles_per_op'] *= 1.002
    cases.append(('F hd4@S1 0.2% slower in cycles', synth(fc, pts, route('R1'), slow), {'T:hd4@S1': False, 'scored:hd4@S1': False, 'B5': 'PASS'}))

    def wrong(runs):
        k = next(r['run'] for r in pts['runs'] if r['case'] == 'signs@S1')
        runs[k]['checks'] = ['approx', 'wrong']
    cases.append(('G one check of C wrong', synth(fc, pts, route('R1'), wrong), {'R0': 'FAIL'}))

    def clock(runs):  # every signs@S1 pattern run at 700 MHz: no complete block: NO DATA
        for r in pts['runs']:
            if r['case'] == 'signs@S1':
                runs[r['run']]['mhz_max'] = 700.0
    cases.append(('H signs@S1 runs at 700 MHz', synth(fc, pts, route('R1'), clock), {'Q:signs@S1': 'NO DATA'}))

    def one_block(runs):  # lowmant8@S1 keeps one complete block: NO DATA (a test case needs 2)
        bl = [b for b in pts['blocks'] if b['kind'] == 'lowmant8' and b['shape'] == 'S1']
        for b in bl[1:]:
            runs[b['runs'][1]]['ran'] = False
    cases.append(('I lowmant8@S1 one complete block', synth(fc, pts, route('R1'), one_block), {'Q:lowmant8@S1': 'NO DATA'}))

    def no_s2(runs):
        for r in pts['runs']:
            if r['shape'] == 'S2':
                runs[r['run']]['ran'] = False
    n_s1 = sum(1 for c in tests if c.endswith('@S1'))
    cases.append(('J S2 never ran', synth(fc, pts, route('R1'), no_s2), {'B5': 'PASS' if n_s1 >= MIN_SCORED else 'TOO FEW', 'Q:maxalte@S2': 'NO DATA'}))

    def noisy_block(runs):  # one hd4@S2 block 3 W off: its SE grows (sd of the blocks), the band widens past 0.05 D, the case still PASSES B5
        b = [b for b in pts['blocks'] if b['kind'] == 'hd4' and b['shape'] == 'S2'][0]
        for x in b['runs'][1:3]:
            runs[x]['p_work_w'] += 3.0
    cases.append(('K one hd4@S2 block 3 W off', synth(fc, pts, route('R1'), noisy_block), {'B5case:hd4@S2': True}))
    m = lambda cid: (route('R1')(cid) + route('R4')(cid)) / 2  # noqa: E731
    cases.append(('M measured halfway between R1 and the null', synth(fc, pts, m), {'H1': 'UNDECIDED', 'H1p': pattern_wins(m, 'R4')}))

    # A1 item 6 (verify-e210's finding 2): runs whose readings are missing, None or not finite are set aside, never a crash; A1 item 5: R0
    def blocks_of(kind, shape):
        return [b for b in pts['blocks'] if b['kind'] == kind and b['shape'] == shape]

    def planned(cid):
        k, s = cid.split('@')
        return len(blocks_of(k, s))
    p1 = blocks_of('lowmant8', 'S1')[0]['runs'][1]

    def quiet(runs, k=p1, none=False):        # no telemetry sample inside the counted launches: the reducer omits the clock keys (A1)
        if none:
            runs[k]['mhz_min'] = runs[k]['mhz_max'] = None
        else:
            del runs[k]['mhz_min'], runs[k]['mhz_max']
        runs[k]['p_work_w'] = None
    cases.append(('Y1 a pattern run with no telemetry sample inside its counted launches (no clock keys, no work power)',
                  synth(fc, pts, route('R1'), quiet), {'nblocks:lowmant8@S1': planned('lowmant8@S1') - 1, 'R0': 'PASS', 'B5': 'PASS'}))
    cases.append(('Y2 the same with mhz_min and mhz_max written as None (the first freeze crashed here)',
                  synth(fc, pts, route('R1'), lambda runs: quiet(runs, none=True)), {'nblocks:lowmant8@S1': planned('lowmant8@S1') - 1}))
    b0 = [b for b in pts['blocks'] if b['shape'] == 'S1'][0]
    rq = b0['runs'][3]                         # the closing random run of the first S1 block, shared with the next block
    shared = [b for b in pts['blocks'] if rq in b['runs']]
    want_n3 = {f"nblocks:{b['kind']}@{b['shape']}": planned(f"{b['kind']}@{b['shape']}") - 1 for b in shared}
    want_n3.update({'drift:random@S1': sum(1 for r in pts['runs'] if r['case'] == 'random@S1') - 1, 'R0': 'PASS'})
    cases.append(('Y3 a random run with no telemetry sample inside its counted launches (its two blocks set aside; the drift report without it)',
                  synth(fc, pts, route('R1'), lambda runs: quiet(runs, k=rq)), want_n3))
    p4 = blocks_of('hd4', 'S2')[0]['runs'][1]

    def nan_power(runs):
        runs[p4]['p_work_w'] = float('nan')
    cases.append(('Y4 a non-finite board power in one pattern run', synth(fc, pts, route('R1'), nan_power), {'nblocks:hd4@S2': planned('hd4@S2') - 1}))
    p5 = blocks_of('signs', 'S1')[0]['runs'][2]

    def no_check(runs):
        runs[p5]['checks'] = []
    cases.append(('Y5 a run whose host printed no check of C (R0 reads it apart; its block set aside by Q)', synth(fc, pts, route('R1'), no_check),
                  {'R0': 'PASS', 'R0missing': 1, 'nblocks:signs@S1': planned('signs@S1') - 1}))

    d6 = synth(fc, pts, route('R1'))
    d6['probe'] = {'maxalte@S2': {'checks': [], 'verdict': 'OUT', 'rc': 1}}
    d6['smoke'] = {c: {'checks': ['exact']} for c in ('random@S1', 'zeros@S1', 'random@S2')}
    cases.append(('Y6 the probe crashed (no check) and the smoke read exact', d6, {'R0': 'PASS', 'R0missing': 1}))
    cases.append(('Y7 an empty data file (no check read)', {}, {'R0': 'NO DATA', 'B5': 'NO DATA'}))
    d8 = synth(fc, pts, route('R1'))
    d8['smoke'] = {'random@S1': {'checks': ['wrong']}}
    cases.append(('Y8 a smoke process with a wrong check', d8, {'R0': 'FAIL'}))
    # H4's arithmetic on a STAND-IN forecast table (in memory; the frozen table gives R2 five cases, so H4 can only read UNDECIDED on E210):
    # every test case given an R2 forecast equal to the null's, then measured at R1 (R1 BETTER) and at that R2 (R2 BETTER)
    fc2 = json.loads(json.dumps(fc))
    for cid in tests:
        fc2['cases'][cid]['routes']['R2'] = fc2['cases'][cid]['routes']['R4']
    alt = []
    alt.append(('V1 stand-in table, R2 on every test case; measured = R1', synth(fc2, pts, route('R1')), {'H4': 'R1 BETTER'}, fc2))
    alt.append(('V2 stand-in table, R2 on every test case; measured = that R2', synth(fc2, pts, route('R4')), {'H4': 'R2 BETTER'}, fc2))
    results = []
    allok = True
    for name, data, want, *tab in cases + alt:
        out = score(data, tab[0] if tab else fc, pts)
        got = {}
        for k in want:
            if k in out['rules']:
                got[k] = out['rules'][k]['verdict']
            elif k == 'R0':
                got[k] = out['R0']['verdict']
            elif k.startswith('T:'):
                got[k] = out['cases'][k[2:]].get('T')
            elif k.startswith('scored:'):
                got[k] = out['cases'][k[7:]].get('scored')
            elif k.startswith('Q:'):
                got[k] = out['cases'][k[2:]].get('Q')
            elif k.startswith('B5case:'):
                got[k] = out['cases'][k[7:]]['B5']['pass']
            elif k == 'R0missing':
                got[k] = len(out['R0']['missing_REPORTED'])
            elif k.startswith('nblocks:'):
                got[k] = out['cases'][k[8:]]['n_complete']
            elif k.startswith('drift:'):
                got[k] = (out['reported'].get('random_drift') or {}).get(k[6:], {}).get('n')
            elif k in ('H1p', 'H2p', 'H3p', 'H4p'):
                got[k] = out['reported']['pattern_level_sign_test_REPORTED'][k]['verdict']
        ok = all(got[k] == want[k] for k in want)
        allok &= ok
        results.append({'case': name, 'want': want, 'got': got, 'ok': ok})
    # the refusal: the scorer run on a copy of this folder whose forecast file has one byte more must exit 4 without scoring
    import shutil
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for fn in ('score_e210.py', 'points-e210.json'):
            shutil.copy(os.path.join(HERE, fn), os.path.join(td, fn))
        open(os.path.join(td, 'forecast-e210.json'), 'wb').write(open(os.path.join(HERE, 'forecast-e210.json'), 'rb').read() + b' ')
        open(os.path.join(td, 'data.json'), 'w').write('{}')
        pr = subprocess.run([sys.executable, '-I', '-B', os.path.join(td, 'score_e210.py'), os.path.join(td, 'data.json'), '--out',
                             os.path.join(td, 'out.json')], capture_output=True, text=True)
        refused = pr.returncode == 4 and not os.path.exists(os.path.join(td, 'out.json'))
    results.append({'case': 'L the scorer on a copy whose forecast file has one byte more', 'got': {'refusal_exit': pr.returncode}, 'want': {'refusal_exit': 4},
                    'ok': refused})
    allok &= refused
    # every rule made to PASS and FAIL at least once
    seen = {}
    for r in results:
        for k, v in r.get('got', {}).items():
            seen.setdefault(k.split(':')[0], set()).add(str(v))
    cover = {k: sorted(v) for k, v in seen.items()}
    res = {'verdict': 'PASS' if allok else 'FAIL', 'python': sys.version.split()[0], 'cases': results, 'verdicts_seen_per_rule': cover}
    json.dump(res, open(os.path.join(outdir, 'selftest-standins-e210.json'), 'w'), indent=1, sort_keys=True)
    L = [f"E210 scorer self-test on stand-ins: {res['verdict']}"]
    for r in results:
        L.append(f"  {'ok ' if r['ok'] else 'BAD'} {r['case']}: " + ', '.join(f'{k} {v}' for k, v in r.get('got', {}).items()))
    L.append('verdicts seen per rule: ' + '; '.join(f'{k} {"/".join(v)}' for k, v in sorted(cover.items())))
    open(os.path.join(outdir, 'selftest-standins-e210.txt'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return 0 if allok else 1


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--selftest':
        return selftest(sys.argv[2])
    if len(sys.argv) < 4 or sys.argv[2] != '--out':
        print(__doc__)
        return 2
    fc, pts = load_frozen(check=True)
    out = score(json.load(open(sys.argv[1])), fc, pts)
    json.dump(out, open(sys.argv[3], 'w'), indent=1, sort_keys=True)
    tx = text(out)
    if '--txt' in sys.argv:
        open(sys.argv[sys.argv.index('--txt') + 1], 'w').write(tx)
    print(tx, end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
