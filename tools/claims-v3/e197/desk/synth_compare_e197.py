#!/usr/bin/env python3
"""E197 registration desk check (reg-e197, Q185): the registered reducer's output on a synthetic session, set beside what was put in.

    python3 -I -B synth_compare_e197.py REGFILE.json INJECTED.json [INJECTED2.json] --mode exact|noisy|stop|pooled

The injected values are ARBITRARY TEST VALUES (synth_session_e197.py): not a forecast and not a measurement. Prints each train and
each derived price beside its injected value and ends with "CONSISTENT" or "INCONSISTENT (n)". What each mode requires:
  exact   every train scored, its D equal to the injected value within 1e-9 W, units = processes / 2, F / S = 1, nothing dropped;
          every derived price's board pJ equal to the injected combination over the rate (1e-9 relative); the verdicts implied by a
          noise-free session (POSITIVE where the value is above 0; the five zero-by-design prices BOUNDED, or, on a zero-width
          interval within 1e-12 W of 0, the sign of the rounding residue, printed as a note); the train gain 1 within
          1e-9; the rail share within 2 % of the injected 0.60 (the rail filter's residue over the 4.5 s gaps moves it slightly);
          electrons through the 12 V input and the rail from their formulas; the cell reading "cell".
  noisy   T6 drops exactly one process for "launch not ok" and T9 one for "clock"; T11 is NOT SCORED for its F / S rate ratio, and so
          is every derived price that uses it; every other train is scored and lies within 5 SE + 3 % of its injected value; the rail
          voltage samples off 3 mV are counted where the injected 30 s span crosses a train.
  stop    the reducer times the hand-made STOP by its stop_seen mark; every process ending at or after it is dropped for "stop";
          the trains that ended before it are scored and exact; T9 (cut in its 13th process), T11, T13, T12 and T15 are NOT SCORED.
  pooled  two exact sessions (the full plan and the second sitting): T1 pools its units from both (67 + 115), exact; T7 and T14
          scored, their derived prices BOUNDED; every other train as in exact.
"""
import argparse
import json

E_CH = 1.602176634e-19
DERIV = {'cell': ([('T1', 1)], 64), 'cell_ctrl': ([('T1', 1), ('T2', -1)], 64), 'order': ([('T2', 1)], 1),
         'result_bit': ([('T3', 1)], 64), 'result_bit32': ([('T4', 1)], 32), 'lin_result': ([('T4', 1), ('T3', -0.5)], 1),
         'write': ([('T5', 1)], 1), 'dest_switch': ([('T6', 1)], 1), 'dest_n8': ([('T7', 1)], 1),
         'read2_field': ([('T8', 1)], 64), 'read2_net': ([('T8', 1), ('T9', -0.5)], 64), 'held_one': ([('T9', 1)], 128),
         'read2_operand': ([('T10', 1)], 64), 'operand_path': ([('T10', 1), ('T8', -1)], 64), 'read1_field': ([('T11', 1)], 64),
         'field_bit': ([('T12', 1)], 4), 'field_bit3': ([('T15', 1)], 2), 'lin_field': ([('T15', 1), ('T12', -0.5)], 1),
         'field_first': ([('T13', 1)], 1), 'field_base': ([('T13', 1), ('T12', -0.25)], 1), 'read_n8': ([('T14', 1)], 1)}
BOUNDED = ('order', 'lin_result', 'lin_field', 'dest_n8', 'read_n8')
PLANNED = {'T2': 18, 'T1': 134, 'T3': 18, 'T5': 52, 'T6': 18, 'T4': 18, 'T8': 18, 'T10': 18, 'T9': 26, 'T11': 18, 'T13': 26,
           'T12': 18, 'T15': 18, 'T7': 18, 'T14': 18}
EXT = {'T1': 230, 'T7': 18, 'T14': 18}
bad = 0


def fail(msg):
    global bad
    bad += 1
    print('  FAIL: ' + msg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('regfile')
    ap.add_argument('injected', nargs='+')
    ap.add_argument('--mode', required=True, choices=['exact', 'noisy', 'stop', 'pooled'])
    a = ap.parse_args()
    R = json.load(open(a.regfile))
    inj = [json.load(open(p)) for p in a.injected]
    D = inj[0]['D_W']
    rate = inj[0]['rate']
    print('mode %s; sessions %d; injected (ARBITRARY TEST VALUES): %s' % (a.mode, len(inj), inj[0]['note']))
    not_run = set() if a.mode == 'pooled' else ({'T7', 'T14'} if inj[0]['plan'] != 'ext' else set(PLANNED) - set(EXT))
    stopped = {'T9', 'T11', 'T13', 'T12', 'T15'} if a.mode == 'stop' else set()
    noscore = {'T11'} if a.mode == 'noisy' else set()
    for tr in PLANNED:
        t = R['trains'][tr]
        iv = t['D_W']
        m = iv.get('mean')
        exp_units = (PLANNED[tr] // 2) if tr not in EXT or a.mode != 'pooled' else (PLANNED.get(tr, 0) + EXT[tr]) // 2
        if tr in ('T7', 'T14') and a.mode == 'pooled':
            exp_units = EXT[tr] // 2
        line = '%-4s units %3d  D %s  injected %+.4f  %s  F/S %s  dropped %s %s' % (
            tr, t['units'], ('%+.6f' % m) if m is not None else '   -    ', D[tr], t['sign'],
            ('%.6f' % t['rate_ratio_F_over_S']) if t['rate_ratio_F_over_S'] else '-', t['dropped'] or '', iv.get('note') or '')
        print(line)
        if tr in not_run:
            if t['processes'] != 0 or 'not run' not in (iv.get('note') or ''):
                fail('%s should be NOT SCORED: not run' % tr)
            continue
        if tr in stopped:
            if iv.get('lo') is not None or 'NOT SCORED' not in (iv.get('note') or ''):
                fail('%s should be NOT SCORED after the stop' % tr)
            if t['dropped'].get('stop', 0) < 1:
                fail('%s: no process dropped for the stop' % tr)
            continue
        if tr in noscore:
            if iv.get('lo') is not None or 'rate ratio' not in (iv.get('note') or ''):
                fail('%s should be NOT SCORED by its F / S rate ratio' % tr)
            continue
        if iv.get('lo') is None:
            fail('%s not scored' % tr)
            continue
        if a.mode in ('exact', 'stop', 'pooled'):
            if abs(m - D[tr]) > 1e-9:
                fail('%s D %r against %r' % (tr, m, D[tr]))
            if t['units'] != exp_units:
                fail('%s units %d against %d' % (tr, t['units'], exp_units))
            if abs(t['rate_ratio_F_over_S'] - 1.0) > 1e-12 or t['dropped']:
                fail('%s F/S or drops' % tr)
            want = 'POSITIVE' if D[tr] > 0 else 'NOT RESOLVED'
            if t['sign'] != want:
                fail('%s sign %s against %s' % (tr, t['sign'], want))
        else:
            tol = 5 * (iv['se'] or 0) + 0.03 * abs(D[tr])
            if abs(m - D[tr]) > tol + 1e-6:
                fail('%s D %+.5f off the injected %+.5f by more than 5 SE + 3 %% (%.5f)' % (tr, m, D[tr], tol))
    if a.mode == 'noisy':
        if R['trains']['T6']['dropped'].get('launch not ok') != 1:
            fail('T6 should drop exactly one process for "launch not ok"')
        if R['trains']['T9']['dropped'].get('clock') != 1:
            fail('T9 should drop exactly one process for "clock"')
        offs = {tr: R['trains'][tr]['rail_mv_samples_off_3mV'] for tr in PLANNED if R['trains'][tr]['rail_mv_samples_off_3mV'][0]}
        print('rail voltage samples off 3 mV in the trains\' spans (off, of): %s' % (offs or 'none'))
        if not offs:
            fail('the injected rail-voltage span was counted nowhere')
    # derived prices
    print('derived (board pJ per unit; injected combination over the rate):')
    for name, (terms, k) in DERIV.items():
        d = R['derived'].get(name)
        if d is None:
            fail('derived %s missing' % name)
            continue
        uses = {tr for tr, _ in terms}
        want_v = sum(c * D[tr] for tr, c in terms) / k
        want_pj = want_v / rate * 1e12
        b = d['board_pJ']
        got = b['mean'] if b else None
        print('  %-14s %s  injected %+.6f pJ  %s' % (name, ('%+.6f pJ' % got) if got is not None else '    -     ', want_pj,
                                                   d['verdict']))
        blocked = (uses & not_run) or (uses & stopped) or (uses & noscore)
        if blocked:
            if d['verdict'] != 'NOT SCORED':
                fail('%s should be NOT SCORED (a train in it is)' % name)
            continue
        if a.mode in ('exact', 'stop', 'pooled'):
            if got is None or abs(got - want_pj) > 1e-9 * max(1.0, abs(want_pj)):
                fail('%s board pJ %r against %r' % (name, got, want_pj))
            want_verdict = ('BOUNDED' if abs(want_v) < 1e-15 else 'POSITIVE') if name in BOUNDED else \
                ('POSITIVE' if want_v > 0 else ('NEGATIVE' if want_v < 0 else 'NOT RESOLVED'))
            zero_width = d['W'].get('se') == 0 and d['W'].get('mean') is not None and abs(d['W']['mean']) < 1e-12
            if d['verdict'] != want_verdict:
                if want_verdict == 'BOUNDED' and zero_width and d['verdict'] in ('POSITIVE', 'NEGATIVE'):
                    print('  note: %s reads %s on a zero-width interval at %+.1e W, a rounding residue of a noise-free session '
                          '(the sign of 0 to 1e-12 W); accepted as the zero it is' % (name, d['verdict'], d['W']['mean']))
                else:
                    fail('%s verdict %s against %s' % (name, d['verdict'], want_verdict))
            e12 = got * 1e-12 / (E_CH * 12.0)
            if abs(d['electrons_12V'] - e12) > 1e-9 * max(1.0, abs(e12)):
                fail('%s electrons_12V' % name)
            if R.get('rail_share') and R.get('v_rail'):
                er = got * R['rail_share'] * 1e-12 / (E_CH * R['v_rail'])
                if abs(d['electrons_rail'] - er) > 1e-9 * max(1.0, abs(er)):
                    fail('%s electrons_rail' % name)
        elif d['verdict'] == 'NOT SCORED':
            fail('%s not scored' % name)
    g = R.get('train_gain')
    sh = R.get('rail_share')
    print('train gain %s; rail share %s (injected %.2f); v_rail %s; cell reading %s; stops %s; dips %s of samples %s' % (
        g, sh, inj[0]['rail_share'], R.get('v_rail'), R.get('cell_reading'), R.get('stops'), R.get('dips'), R.get('samples')))
    if a.mode in ('exact', 'stop', 'pooled'):
        if g is None or abs(g - 1.0) > 1e-9:
            fail('train gain %r, 1 expected' % g)
        if R.get('dips') and any(R['dips']):
            fail('dips in an exact session')
        if R['cell_reading'].get('read') != 'cell':
            fail('cell reading')
    if sh is None or abs(sh - inj[0]['rail_share']) > 0.02 * inj[0]['rail_share']:
        fail('rail share %r not within 2 %% of %r' % (sh, inj[0]['rail_share']))
    if abs((R.get('v_rail') or 0) - inj[0]['v_rail']) > 1e-9:
        fail('v_rail')
    if a.mode == 'stop':
        st = R['stops'][0]
        if st.get('from') != 'stop_seen mark' or abs(st['t_ms'] - inj[0]['special']['stop_t']) > 0.5:
            fail('stop time or its source: %s' % st)
    print('CONSISTENT' if not bad else 'INCONSISTENT (%d)' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
