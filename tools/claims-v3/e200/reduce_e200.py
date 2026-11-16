#!/usr/bin/env python3
"""E200's reduction, registered before any E200 datum (E200.md sections 4 and 6). Standard library only.

    python3 -I -B tools/claims-v3/e200/reduce_e200.py OUT [OUT ...] --out regfile-e200.json [--participants 1024]

E197's registered reducer, tools/claims-v3/e197/proposal/src/reduce_regfile.py (sha256 f325bd0e..., E197.md section 7), is
loaded by its path in the tree this file sits in, from the bytes whose sha256 is checked first (a different file is refused,
exit 3), and its main() runs as registered: the plan from its trains.tsv, the dip rules, the launch reading, the quads, the
units, the intervals, every gate but the clock's, the derived prices and verdicts, the anchors' arithmetic, the gain, the rail
share, its JSON and its printed lines. Nothing of it is copied here. Three of its functions, the three the clock touches, are
replaced while it runs (E200.md section 4, C1 and C2):

  1. off_clock(S, t0, t1), E197's gate "a telemetry sample in its span is off the session's clock by more than 1 MHz", becomes
     THE CLOCK RULE for a train process (t0, t1: its first launch's start and its last launch's end, as E197's train_result
     passes them): every telemetry sample at or after t0 + 1.5 s and at or before t1 reads 800 MHz within 1 MHz, and the
     process's last launch ran at 780-810 MHz by its own count (cycles_max / wall_s, both from its REGFILE line). Otherwise the
     process gives no value, counted under E197's own reason "clock". Every process of a session whose median clock (E197's
     S['clk'], the clock E197's rate R uses) is not 800 MHz within 1 MHz is set aside the same way.
  2. reading(S, t0, t1), E197's launch reading, reads nothing before the process's first launch's start + 2.0 s (THE CLOCK
     RULE's 1.5 s for the governor's climb and half a second more for the board meter's pass to follow the step): a train
     launch that starts earlier gives no reading; a later one is read as E197 reads it, unchanged. A quad holding a launch with
     no reading is incomplete and does not count, and a process's value is the mean of its complete quads (both E197's own
     rules). Under E200's window (320,000,000 cycles: 0.4 s a launch at 800 MHz, E200.md section 4) launches 0-4 start before
     that point and launches 5-12 after it, whatever the climb up to 1.5 s, so a train process is read on its quads 2 and 3
     (launches 5-12) and never on quad 1 (launches 1-4).
  3. anchors(S), E197's anchors, read each burst's board level over [its first launch's start + 2.0 s, its last launch's end]
     in place of [+ 0.5 s, end], for the same reason; its idle reads, its rail window, its filter fraction, its shares and its
     drift lines are E197's, unchanged.

A telemetry sample with no clock field is not judged, as in E197's gate. E200 never passes --prediction (E200.md section 0: its
forecast is sealed); this file refuses it (exit 2). The output is E197's JSON form with one key added, "e200": the constants
above, E197's reducer by path and sha256, and per session its median clock and the three replacements' tallies.
"""
import argparse
import bisect
import hashlib
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
E197_REDUCER = os.path.normpath(os.path.join(HERE, os.pardir, 'e197', 'proposal', 'src', 'reduce_regfile.py'))
E197_REDUCER_SHA256 = 'f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87'

CLOCK_MHZ = 800.0         # the registered clock: the governor's top point on aifoundry2 card 0 (E200.md section 3)
TOL_MHZ = 1.0             # E197's own tolerance for a sample against the session's clock
ALLOW_MS = 1500.0         # THE CLOCK RULE's allowance for the governor's climb from a process's first launch (E194's)
OWN_LO_MHZ, OWN_HI_MHZ = 780.0, 810.0   # the last launch's own count (E194's band)
READ_FROM_MS = 2000.0     # nothing inside a device process is read before its first launch's start + 2.0 s
ANCHOR_E197_MS = 500      # E197's anchors: the board over [first launch + 0.5 s, last launch's end]


def load_e197(path=E197_REDUCER, want=E197_REDUCER_SHA256):
    """E197's reducer as a module, made from the very bytes whose sha256 was checked."""
    with open(path, 'rb') as f:
        raw = f.read()
    got = hashlib.sha256(raw).hexdigest()
    if got != want:
        print('REFUSED: %s has sha256 %s, not E197\'s registered %s' % (path, got, want), file=sys.stderr)
        sys.exit(3)
    mod = types.ModuleType('reduce_regfile_e197')
    mod.__file__ = path
    exec(compile(raw, path, 'exec'), mod.__dict__)
    return mod, got


def own_mhz(r):
    """a launch's clock by its own count: its slowest hart's cycles over its wall seconds"""
    c, w = r.get('cycles_max'), r.get('wall_s')
    if isinstance(c, bool) or isinstance(w, bool) or not isinstance(c, (int, float)) or not isinstance(w, (int, float)):
        return None
    return c / w / 1e6 if c > 0 and w > 0 else None


def install(R):
    """replace E197's off_clock, reading and anchors in the loaded module R by E200's forms; return the tallies' reader"""
    orig_session, orig_reading, orig_anchors, orig_wm = R.session, R.reading, R.anchors, R.window_mean
    seen = []

    def tally(S):
        return S.setdefault('_e200', {
            'median_clock_mhz': S.get('clk'), 'median_clock_ok': None, 'samples_with_t': 0, 'samples_without_clock': 0,
            'samples_off_800': 0, 'processes_judged': 0, 'set_aside_median_clock': 0, 'set_aside_samples_after_allowance': 0,
            'set_aside_no_last_launch': 0, 'set_aside_own_count': 0, 'processes_kept_by_clock': 0, 'launches_asked': 0,
            'launches_before_2s_not_read': 0, 'launches_read_as_e197': 0, 'launches_unmatched': 0, 'anchor_groups': 0,
            'anchor_board_windows_moved': 0, 'anchor_bursts_off_800_after_allowance': 0})

    def clock_index(S):
        ix = S.get('_e200_ix')
        if ix is None:
            T = tally(S)
            pts = []
            for s in S['tel']:
                t = s.get('t_ms')
                if isinstance(t, bool) or not isinstance(t, (int, float)):
                    continue
                f = R.num(s, 'mhz', 'minion')
                pts.append((t, f))
            pts.sort(key=lambda p: p[0])
            ts, off = [], [0]
            for t, f in pts:
                ts.append(t)
                bad = f is not None and abs(f - CLOCK_MHZ) > TOL_MHZ
                off.append(off[-1] + (1 if bad else 0))
                T['samples_with_t'] += 1
                T['samples_without_clock'] += 1 if f is None else 0
                T['samples_off_800'] += 1 if bad else 0
            ix = S['_e200_ix'] = (ts, off)
        return ix

    def off800(S, t0, t1):
        """does any telemetry sample in [t0, t1] read off 800 MHz by more than 1 MHz?"""
        ts, off = clock_index(S)
        i0, i1 = bisect.bisect_left(ts, t0), bisect.bisect_right(ts, t1)
        return off[i1] - off[i0] > 0

    def last_launch(S, t1):
        ix = S.get('_e200_last')
        if ix is None:
            ix = {}
            for r in S['runs']:
                if r.get('train') is not None and r.get('t_end_ms') is not None:
                    ix.setdefault(r['t_end_ms'], []).append(r)
            S['_e200_last'] = ix
        c = [r for r in ix.get(t1, []) if r.get('launch') == R.LAUNCHES - 1]
        return c[0] if len(c) == 1 else None

    def launch_index(S):
        ix = S.get('_e200_lx')
        if ix is None:
            first, by_start = {}, {}
            for r in S['runs']:
                if r.get('train') is None or r.get('t_start_ms') is None:
                    continue
                key = (r.get('train'), r.get('block'), r.get('proc'))
                by_start.setdefault(r['t_start_ms'], []).append((key, r))
                if r.get('launch') == 0:
                    first.setdefault(key, []).append(r['t_start_ms'])
            ix = S['_e200_lx'] = (first, by_start)
        return ix

    def session_e200(out, idx):
        S = orig_session(out, idx)
        T = tally(S)
        T['median_clock_mhz'] = S['clk']
        T['median_clock_ok'] = abs(S['clk'] - CLOCK_MHZ) <= TOL_MHZ
        clock_index(S)
        seen.append(S)
        return S

    def off_clock_e200(S, t0, t1):
        """THE CLOCK RULE for one train process; True sets it aside (E197's reason 'clock')"""
        T = tally(S)
        T['processes_judged'] += 1
        if not T['median_clock_ok']:
            T['set_aside_median_clock'] += 1
            return True
        if off800(S, t0 + ALLOW_MS, t1):
            T['set_aside_samples_after_allowance'] += 1
            return True
        r = last_launch(S, t1)
        if r is None:
            T['set_aside_no_last_launch'] += 1
            return True
        f = own_mhz(r)
        if f is None or not (OWN_LO_MHZ <= f <= OWN_HI_MHZ):
            T['set_aside_own_count'] += 1
            return True
        T['processes_kept_by_clock'] += 1
        return False

    def reading_e200(S, t0, t1):
        """E197's reading of a train launch, or None when it starts before its process's first launch + 2.0 s"""
        T = tally(S)
        T['launches_asked'] += 1
        first, by_start = launch_index(S)
        c = by_start.get(t0, [])
        lo = first.get(c[0][0], []) if len(c) == 1 else []
        if len(lo) != 1:
            T['launches_unmatched'] += 1
            return None
        if t0 < lo[0] + READ_FROM_MS:
            T['launches_before_2s_not_read'] += 1
            return None
        T['launches_read_as_e197'] += 1
        return orig_reading(S, t0, t1)

    def anchors_e200(S):
        T = tally(S)
        groups = {}
        for r in S['runs']:
            if r.get('role') in ('anchor_first', 'anchor_last') and r.get('ok'):
                groups.setdefault((r.get('block'), r.get('role'), r.get('kind_run')), []).append(r)
        spans = {}
        for recs in groups.values():
            t_a = min(r['t_start_ms'] for r in recs)
            t_b = max(r['t_end_ms'] for r in recs)
            spans[(t_a + ANCHOR_E197_MS, t_b)] = t_a
            if off800(S, t_a + ALLOW_MS, t_b):
                T['anchor_bursts_off_800_after_allowance'] += 1
        T['anchor_groups'] = len(spans)

        def wm(series, t0, t1):
            t_a = spans.get((t0, t1))
            if t_a is not None and series is not S['rail']:
                T['anchor_board_windows_moved'] += 1
                return orig_wm(series, t_a + READ_FROM_MS, t1)
            return orig_wm(series, t0, t1)

        R.window_mean = wm
        try:
            return orig_anchors(S)
        finally:
            R.window_mean = orig_wm

    R.session, R.off_clock, R.reading, R.anchors = session_e200, off_clock_e200, reading_e200, anchors_e200
    return seen


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if any(a == '--prediction' or a.startswith('--prediction=') for a in argv):
        print('REFUSED: E200 never runs the reducer with a forecast (E200.md sections 0 and 6)', file=sys.stderr)
        return 2
    ap = argparse.ArgumentParser(description='E200: E197\'s reducer with THE CLOCK RULE (E200.md sections 4 and 6)')
    ap.add_argument('outs', nargs='+')
    ap.add_argument('--out', default='regfile.json')
    ap.add_argument('--participants', type=int, default=1024)
    a = ap.parse_args(argv)
    R, sha = load_e197()
    seen = install(R)
    saved = sys.argv
    sys.argv = [os.path.join(HERE, 'reduce_e200.py')] + argv
    try:
        R.main()
    finally:
        sys.argv = saved
    with open(a.out) as f:
        res = json.load(f)
    res['e200'] = {
        'what': 'E197\'s reducer, run unchanged but for off_clock, reading and anchors (E200.md sections 4 and 6)',
        'e197_reducer': 'tools/claims-v3/e197/proposal/src/reduce_regfile.py', 'e197_reducer_sha256': sha,
        'clock_mhz': CLOCK_MHZ, 'tolerance_mhz': TOL_MHZ, 'allowance_ms': ALLOW_MS,
        'last_launch_own_count_mhz': [OWN_LO_MHZ, OWN_HI_MHZ], 'read_from_ms': READ_FROM_MS,
        'sessions': [dict({'session': S['dir']}, **{k: v for k, v in S.get('_e200', {}).items()}) for S in seen]}
    with open(a.out, 'w') as f:
        json.dump(res, f, indent=1, default=lambda x: None)
    for S in seen:
        T = S.get('_e200', {})
        print('e200 %s: median clock %s MHz (%s); train processes judged %d, kept by the clock %d, set aside: median %d, '
              'samples after 1.5 s %d, no last launch %d, own count %d; launches asked %d, before 2.0 s not read %d, read %d, '
              'unmatched %d; anchor groups %d, board windows moved %d, off 800 MHz after 1.5 s %d; samples %d (%d without a '
              'clock, %d off 800 MHz)' % (
                  S['dir'], T.get('median_clock_mhz'), 'ok' if T.get('median_clock_ok') else 'NOT 800',
                  T.get('processes_judged', 0), T.get('processes_kept_by_clock', 0), T.get('set_aside_median_clock', 0),
                  T.get('set_aside_samples_after_allowance', 0), T.get('set_aside_no_last_launch', 0),
                  T.get('set_aside_own_count', 0), T.get('launches_asked', 0), T.get('launches_before_2s_not_read', 0),
                  T.get('launches_read_as_e197', 0), T.get('launches_unmatched', 0),
                  T.get('anchor_groups', 0), T.get('anchor_board_windows_moved', 0),
                  T.get('anchor_bursts_off_800_after_allowance', 0), T.get('samples_with_t', 0),
                  T.get('samples_without_clock', 0), T.get('samples_off_800', 0)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
