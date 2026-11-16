#!/usr/bin/env python3
"""E197 registration desk check (reg-e197, Q185): a synthetic regfile session for the registered reducer.

    python3 -I -B synth_session_e197.py TRAINS.tsv HOST-LIST.jsonl OUT --plan full|short|ext [--variant exact|noisy|stop]
                                        [--t0-ms EPOCH_MS] [--seed N]

Writes OUT/telemetry.jsonl, OUT/runs.jsonl, OUT/marks.jsonl and OUT/SESSION_DONE in the forms the reference scripts write them
(the host's REGFILE fields plus run_trains.py's additions; the sampler's t_ms, board_w, mhz.minion, sp.minion_w[0],
sp.minion_mv[0], temp_c.minshire[0]), on the reference session's order (run_trains.py and run_session.sh: the sampler's 10 s,
the smoke block, the blocks of trains.tsv with their idles, anchors and 30 s gaps), and OUT/injected.json, the values put in.

THE INJECTED VALUES ARE ARBITRARY TEST VALUES: NOT A FORECAST AND NOT A MEASUREMENT. They are chosen to exercise the reducer
(two zero trains, two linear pairs) and are unrelated to any number of the proposal or of its sealed forecast.

The card model: board = idle + the active kind's level over idle (instantaneous, no meter hold, in the exact variant); a train's F
kind sits its injected difference above its S kind; the core rail = its idle + a fixed share of the board's level over idle,
passed through a first-order filter (tau 1.05 s, the meter law the reducer assumes); 600 MHz; 523 mV; every launch 0.4 s,
launches back to back inside a device process (0.5 s opening and 0.3 s closing at idle); samples every 100 ms at 50 ms past
the launch grid, so no sample falls on a launch edge. Every kind issues at one rate, so F / S is exactly 1.
Variants: exact (no noise); noisy (board noise, held readings, dips, and four faults: one launch with check_bad 1 in a T6
process, one 601.5 MHz sample in a T9 process, T11's F kind issuing 0.3 % slower, rail voltage off 4 mV for 30 s); stop (exact,
plus an empty STOP file timed by a stop_seen mark in the middle of T9: what ends after it must be dropped).
Standard library only.
"""
import argparse
import json
import math
import os
import random

INJ_D = {  # train: F - S, W (ARBITRARY TEST VALUES, not a forecast, not a measurement)
    'T1': 0.0500, 'T2': 0.0, 'T3': 0.7000, 'T4': 0.3500, 'T5': 0.0300, 'T6': 0.1500, 'T7': 0.0, 'T8': 0.4000, 'T9': 0.0500,
    'T10': 0.9000, 'T11': 0.6000, 'T12': 0.6400, 'T13': 0.2500, 'T14': 0.0, 'T15': 0.3200}
ROOTS = {  # W over idle of the kinds no train sets from another (ARBITRARY TEST VALUES)
    'nop.z': 0.80, 'rot2.x0': 1.60, 'rot2.x64': 2.00, 'res.k0': 1.50, 'resz.k0': 1.20, 'wn1.z': 1.00, 'rd2i.e0': 1.10,
    'rd2r.e0': 1.30, 'rd1u.e0': 1.05, 'idx0.z': 0.95}
IDLE_W, RAIL_IDLE_W, RAIL_SHARE, TAU, MV = 23.6, 8.0, 0.60, 1.05, 523.0
WINDOW = 240000000
IPH = 1648351            # loop iterations a hart in one 0.4 s launch (arbitrary, the same for every kind)
ENTRY = 1400             # retired instructions of a hart's entry and exit (arbitrary)


def plan_rows(path):
    rows = []
    for ln in open(path):
        if ln.strip() and not ln.startswith('#'):
            b, tr, f, s, n, first, short, role = ln.rstrip('\n').split('\t')
            rows.append({'block': b, 'train': tr, 'F': f, 'S': s, 'n': int(n), 'first': first, 'short': short == '1'})
    return rows


def levels(plan):
    lv = dict(ROOTS)
    pairs = {(p['train'], p['F'], p['S']) for p in plan}
    for _ in range(10):
        for tr, f, s in pairs:
            if s in lv and f not in lv:
                lv[f] = lv[s] + INJ_D[tr]
    for tr, f, s in pairs:
        assert abs(lv[f] - lv[s] - INJ_D[tr]) < 1e-12, (tr, f, s)
    return lv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tsv')
    ap.add_argument('hostlist')
    ap.add_argument('out')
    ap.add_argument('--plan', default='full', choices=['full', 'short', 'ext'])
    ap.add_argument('--variant', default='exact', choices=['exact', 'noisy', 'stop'])
    ap.add_argument('--t0-ms', type=int, default=1795000000000)
    ap.add_argument('--seed', type=int, default=197)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    plan = plan_rows(a.tsv)
    kinds = {}
    for ln in open(a.hostlist):
        if ln.strip():
            d = json.loads(ln)
            kinds[d['kind']] = d
    lv = levels(plan)
    os.makedirs(a.out, exist_ok=False)
    host, runs, marks = 'synthetic', [], []
    segs = []          # (t0_ms, t1_ms, level over idle) of every launch, for the board and the rail
    special = {}       # faults placed in the noisy and stop variants
    t = [a.t0_ms]      # the session clock, ms (multiples of 100)

    def mark(kind, t0, t1, blk, **extra):
        marks.append(dict(kind=kind, host=host, block=blk, t0_ms=t0, t1_ms=t1, **extra))

    def idle(secs, label, blk):
        t0 = t[0]
        t[0] += int(round(secs * 1000))
        mark('idle', t0, t[0], blk, label=label)

    def device(blk, launches, info, kind_of, letter_of, orient, mkind):
        """one device process: 0.5 s opening, the launches back to back, 0.3 s closing"""
        t0 = t[0]
        t[0] += 500
        for n in range(launches):
            k = kind_of(n)
            ts, te = t[0], t[0] + 400
            slow = 1.0
            if a.variant == 'noisy' and info.get('train') == 'T11' and letter_of(n) == 'F':
                slow = 0.997          # T11's F kind issues 0.3 % slower: the F / S rate gate must refuse T11
            iters = int(IPH * slow) * 1024
            cyc = WINDOW + 37
            rate600 = iters * 128 / (cyc / 0.6e9)
            bad = 0
            if a.variant == 'noisy' and info.get('train') == 'T6' and info.get('proc') == 5 and n == 7:
                bad = 1               # one failed register check: that process gives no value
            rec = {'kind': k, 'form_id': kinds[k]['form_id'], 'per_instr': kinds[k]['per_instr'], 'launch': n,
                   'letter': letter_of(n), 'orient': orient, 'harts': 1, 'participants': 1024, 'iters': iters,
                   'iters_min': iters // 1024, 'iters_max': iters // 1024, 'instr_body': iters * 128,
                   'retired_counter': (iters // 1024) * 1024 * 131 + 1024 * ENTRY, 'icache_req': 2 * (iters // 1024) * 128,
                   'icache_miss': 128 * 9, 'l1d_miss': 4096, 'cycles_max': cyc, 'cycles_mean': cyc,
                   'instr_per_cycle_per_hart': iters * 128 / cyc / 1024, 'instr_per_s_600': rate600, 'ra': '0x0',
                   'gp': '0x0', 'deadline': '0x0', 'ra_gp_differ': 0, 'window': WINDOW, 'wall_s': 0.4, 't_start_ms': ts,
                   't_end_ms': te, 'check_bad': bad, 'ok': bad == 0}
            rec.update({'host': host, 'block': blk, 'rc': 0}, **info)
            runs.append(rec)
            segs.append((ts, te, lv[k]))
            if a.variant == 'noisy' and info.get('train') == 'T9' and info.get('proc') == 3 and n == 6:
                special['clock_t'] = ts + 250      # one sample at 601.5 MHz inside this launch
            if a.variant == 'stop' and info.get('train') == 'T9' and info.get('proc') == 12 and n == 6:
                special['stop_t'] = ts + 200       # the hand-made STOP's time
            t[0] = te
        t[0] += 300
        mark(mkind, t0, t[0], blk, rc=0, **info)

    def anchor(k, secs, role, blk):
        idle(4.5, 'before ' + k, blk)
        nl = int(math.ceil(secs / 0.4 - 1e-9))
        device(blk, nl, {'kind_run': k, 'role': role}, lambda n: k, lambda n: '-', '', 'anchor')

    def train_proc(p, j, o, blk, label=None):
        info = {'train': label or p['train'], 'proc': j, 'orient': o, 'F': p['F'], 'S': p['S']}
        if label:
            info['of'] = p['train']
        letter = lambda n: o[0] if n == 0 else o[(n - 1) % 4]
        device(blk, 13, info, lambda n: p['F'] if letter(n) == 'F' else p['S'], letter, o, 'train')

    other = {'SFFS': 'FSSF', 'FSSF': 'SFFS'}
    t[0] += 10000                                         # run_session.sh: the sampler's first 10 s (nap 10)
    idle(5.0, 'before', 'smoke')                          # the smoke block
    for k in ('nop.z', 'res.k0', 'res.k64'):
        anchor(k, 1.0, 'smoke_anchor', 'smoke')
    t8 = [p for p in plan if p['train'] == 'T8'][0]
    train_proc(t8, 0, t8['first'], 'smoke', 'smoke')
    train_proc(t8, 1, other[t8['first']], 'smoke', 'smoke')
    marks.append(dict(kind='smoke_gate', host=host, block='smoke', ok=True, launches=26))
    blocks = ['E'] if a.plan == 'ext' else ['A', 'B', 'C', 'D']
    for bi, b in enumerate(blocks):
        if bi:
            t[0] += 30000                                 # the 30 s gap between blocks, the lock released
        idle(10.0, 'before', b)
        for k in ('nop.z', 'res.k0', 'res.k64'):
            anchor(k, 3.0, 'anchor_first', b)
        for p in plan:
            if p['block'] != b or (a.plan == 'short' and not p['short']):
                continue
            o = p['first']
            for j in range(p['n']):
                train_proc(p, j, o, b)
                o = other[o]
        for k in ('res.k64', 'res.k0', 'nop.z'):
            anchor(k, 3.0, 'anchor_last', b)
        idle(10.0, 'after', b)
    t[0] += 8000                                          # the closing 8 s (nap 8)
    t_end = t[0]
    # ---------------------------------------------------------------- telemetry: board, rail through the filter, clock, volts
    segs.sort()
    tel = []
    si = 0
    y = RAIL_IDLE_W                                       # the rail filter's state
    t_prev = a.t0_ms
    lvl_now = 0.0
    held, nheld = None, 0
    mv_off = (a.t0_ms + 600000, a.t0_ms + 630000)         # noisy: rail volts off 4 mV for 30 s
    for ts in range(a.t0_ms + 50, t_end, 100):
        # advance the rail filter from t_prev to ts through the piecewise-constant input
        tt = t_prev
        while tt < ts:
            while si < len(segs) and segs[si][1] <= tt:
                si += 1
            if si < len(segs) and segs[si][0] <= tt < segs[si][1]:
                lvl, nxt = segs[si][2], min(segs[si][1], ts)
            else:
                lvl, nxt = 0.0, min(segs[si][0], ts) if si < len(segs) else ts
            if nxt <= tt:
                nxt = ts
            target = RAIL_IDLE_W + RAIL_SHARE * lvl
            y = target + (y - target) * math.exp(-(nxt - tt) / 1000.0 / TAU)
            tt = nxt
        t_prev = ts
        while si < len(segs) and segs[si][1] <= ts:
            si += 1
        lvl_now = segs[si][2] if (si < len(segs) and segs[si][0] <= ts < segs[si][1]) else 0.0
        board = IDLE_W + lvl_now
        mhz = 600
        mv = MV
        if a.variant == 'noisy':
            board += rng.gauss(0.0, 0.05)
            if held is not None and nheld < 2 and rng.random() < 0.5:   # the board meter repeats a reading (2-3 samples)
                board, nheld = held, nheld + 1
            else:
                nheld = 0
            held = board
            if rng.random() < 0.004:
                board -= 6.0                               # a low reading: the dip rules must drop it
            if special.get('clock_t') is not None and abs(ts - special['clock_t']) < 50:
                mhz = 601.5
            if mv_off[0] <= ts < mv_off[1]:
                mv = MV + 4.0
        tel.append({'t_ms': ts, 'board_w': round(board, 4), 'mhz': {'minion': mhz},
                    'sp': {'minion_w': [round(y, 6)], 'minion_mv': [mv]}, 'temp_c': {'minshire': [50]}})
    with open(os.path.join(a.out, 'telemetry.jsonl'), 'w') as f:
        f.write('# a synthetic sampler: arbitrary test values\n')
        for s in tel:
            f.write(json.dumps(s) + '\n')
    with open(os.path.join(a.out, 'runs.jsonl'), 'w') as f:
        for r in runs:
            f.write(json.dumps(r) + '\n')
    if a.variant == 'stop':
        marks.append(dict(kind='stop_seen', host=host, block='C', t_ms=special['stop_t'] + 300,
                          stop_mtime_ms=special['stop_t']))
        open(os.path.join(a.out, 'STOP'), 'w').close()   # made by hand: empty, no t_ms of its own
    with open(os.path.join(a.out, 'marks.jsonl'), 'w') as f:
        for m in marks:
            f.write(json.dumps(m) + '\n')
    open(os.path.join(a.out, 'SESSION_DONE'), 'w').close()
    inj = {'note': 'ARBITRARY TEST VALUES: not a forecast and not a measurement', 'variant': a.variant, 'plan': a.plan,
           'D_W': INJ_D, 'levels_over_idle_W': lv, 'idle_W': IDLE_W, 'rail_share': RAIL_SHARE, 'v_rail': MV / 1000.0,
           'rate': 1024 * IPH * 128 / ((WINDOW + 37) / 0.6e9), 'special': special,
           'launches': len(runs), 'samples': len(tel), 'session_s': (t_end - a.t0_ms) / 1000.0}
    json.dump(inj, open(os.path.join(a.out, 'injected.json'), 'w'), indent=1)
    print('synthetic %s session (%s plan): %d launch records, %d samples, %.1f s, faults %s' % (
        a.variant, a.plan, len(runs), len(tel), inj['session_s'], special or 'none'))


if __name__ == '__main__':
    main()
