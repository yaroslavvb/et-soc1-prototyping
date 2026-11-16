#!/usr/bin/env python3
"""E200 registration desk check (reg-e200, Q192): a synthetic regfile session ON A GOVERNED CARD, for E197's reducer and E200's.

    python3 -I -B synth_session_e200.py TRAINS.tsv HOST-LIST.jsonl OUT --plan full|short|ext
            [--variant governor|faults|noisy|nogov] [--climbs CLIMB-FILE] [--t0-ms EPOCH_MS] [--seed N]

Writes OUT/telemetry.jsonl, OUT/runs.jsonl, OUT/marks.jsonl, OUT/SESSION_DONE and OUT/injected.json in the forms E197's
reference session writes them (E197's host REGFILE fields plus its runner's additions; the sampler's t_ms, board_w, mhz.minion,
sp.minion_w[0], sp.minion_mv[0], temp_c.minshire[0]), on E197's order (the sampler's 10 s, the smoke block, the blocks of
trains.tsv with their idles, anchors and 30 s gaps): the form of reg-e197's desk/synth_session_e197.py, written anew for a
card whose governor idles at 600 MHz and climbs to 800 MHz inside each device process.

THE INJECTED VALUES ARE ARBITRARY TEST VALUES: NOT A FORECAST AND NOT A MEASUREMENT. They exercise the reductions and are
unrelated to any number of the proposal, of its sealed forecasts or of any card.

The card model, in whole milliseconds: 600 MHz at idle and in each device process's 500 ms opening; inside a process the clock is
600 MHz from its first launch's start until the process's climb time c, then 800 MHz until 120 ms after its last launch's end (the
service processor's idle reset one pass later), then 600 MHz through its 300 ms closing and the idle after. A launch runs E200's
window, 320,000,000 cycles: 400 ms at 800 MHz, 533 ms at 600 MHz, in between when the climb falls inside it (its cycles_max the
window plus 37, its wall_s its span, its t_start_ms and t_end_ms whole ms; the next launch starts at its end). The board reads
idle + the active kind's level over idle at 800 MHz plus a busy base of 2.0 W, or 0.5 x that level at 600 MHz busy (the climb is
a step the reductions must see); a sample on the boundary of two launches reads the earlier, as a launch's reading window [start
+ 170 ms, end] includes its end; the core rail reads its idle plus a fixed share of the board's level over idle through a
first-order filter (tau 1.05 s, integrated in 10 ms steps); a sample every 100 ms at 50 ms past the session's 100 ms grid; every
kind issues at one rate (F / S exactly 1). Climb times: drawn with the seed from CLIMB-FILE's list (E194's committed
desk/climb-e190.txt: E190 arm A's 84 climbs on aifoundry2), else uniform on [0.01, 1.35] s.
Variants:
  governor  every device process climbs at its drawn c; the board exact;
  faults    governor, plus five planted cases: a T5 process stepping to 700 MHz 2.5 s into its launches (one sample), a T6 process
            whose last launch reads 600 MHz by its own count (its wall_s), a T8 process climbing at 1.45 s (inside the
            allowance), a T9 process climbing at 1.60 s (outside it) and a T10 process with one sample lacking its clock field;
  noisy     governor, plus board noise (sd 0.05 W), held readings (a sample repeats the one before, at most twice) and rare 6 W
            dips: reg-e197's noisy board;
  nogov     no climb at all: the card at 600 MHz throughout (a governor that never steps up).
Standard library only.
"""
import argparse
import json
import math
import os
import random
import re

INJ_D = {  # train: F - S at 800 MHz, W (ARBITRARY TEST VALUES, not a forecast, not a measurement)
    'T1': 0.0500, 'T2': 0.0, 'T3': 0.7000, 'T4': 0.3500, 'T5': 0.0300, 'T6': 0.1500, 'T7': 0.0, 'T8': 0.4000, 'T9': 0.0500,
    'T10': 0.9000, 'T11': 0.6000, 'T12': 0.6400, 'T13': 0.2500, 'T14': 0.0, 'T15': 0.3200}
ROOTS = {  # W over idle at 800 MHz of the kinds no train sets from another (ARBITRARY TEST VALUES)
    'nop.z': 0.80, 'rot2.x0': 1.60, 'rot2.x64': 2.00, 'res.k0': 1.50, 'resz.k0': 1.20, 'wn1.z': 1.00, 'rd2i.e0': 1.10,
    'rd2r.e0': 1.30, 'rd1u.e0': 1.05, 'idx0.z': 0.95}
IDLE_W, RAIL_IDLE_W, RAIL_SHARE, TAU, MV = 23.0, 8.0, 0.60, 1.05, 600.0
BASE_W_800, SCALE600 = 2.0, 0.5
WINDOW = 320000000
MC_LO, MC_HI = 600e3, 800e3    # cycles a millisecond at 600 and 800 MHz
IPH = 1648351                  # loop iterations a hart in one launch (arbitrary; the same for every kind and clock: cycles fixed)
ENTRY = 1400
RESET_MS = 120                 # the governor's idle reset one service-processor pass after a process's last launch


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


def climbs_from(path):
    out = []
    for ln in open(path):
        m = re.match(r'\s*\S+\s+proc-\d+\s+([0-9.]+)\s', ln)
        if m:
            out.append(float(m.group(1)))
    return out


def launch_end(ts, c_abs):
    """the end (whole ms) of a launch of WINDOW cycles started at ts (ms): 600 MHz before c_abs (ms), 800 MHz from it"""
    if c_abs is None or c_abs >= ts + WINDOW / MC_LO:
        return ts + int(round(WINDOW / MC_LO))
    if c_abs <= ts:
        return ts + int(round(WINDOW / MC_HI))
    done = MC_LO * (c_abs - ts)
    return int(round(c_abs + (WINDOW - done) / MC_HI))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tsv')
    ap.add_argument('hostlist')
    ap.add_argument('out')
    ap.add_argument('--plan', default='full', choices=['full', 'short', 'ext'])
    ap.add_argument('--variant', default='governor', choices=['governor', 'faults', 'noisy', 'nogov'])
    ap.add_argument('--climbs', default=None)
    ap.add_argument('--t0-ms', type=int, default=1795000000000)
    ap.add_argument('--seed', type=int, default=200)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    pool = climbs_from(a.climbs) if a.climbs else None
    plan = plan_rows(a.tsv)
    kinds = {}
    for ln in open(a.hostlist):
        if ln.strip():
            d = json.loads(ln)
            kinds[d['kind']] = d
    lv = levels(plan)
    os.makedirs(a.out, exist_ok=False)
    host, runs, marks = 'synthetic', [], []
    segs = []          # (start ms, end ms, level over idle at 800 MHz) of every launch
    clk = []           # (from ms, to ms) of every 800 MHz span, both ends included
    p700, nofield = [], []
    special = {}
    t = [a.t0_ms]

    def mark(kind, t0, t1, blk, **extra):
        marks.append(dict(kind=kind, host=host, block=blk, t0_ms=t0, t1_ms=t1, **extra))

    def idle(ms, label, blk):
        t0 = t[0]
        t[0] += ms
        mark('idle', t0, t[0], blk, label=label)

    def draw_c():
        if a.variant == 'nogov':
            return None
        return rng.choice(pool) if pool else rng.uniform(0.01, 1.35)

    def device(blk, launches, info, kind_of, letter_of, orient, mkind, c=None):
        t0 = t[0]
        t[0] += 500
        first = t[0]
        c_abs = first + int(round(c * 1000)) if c is not None else None
        tr, pj = info.get('train'), info.get('proc')
        own600 = a.variant == 'faults' and tr == 'T6' and pj == 7
        for n in range(launches):
            k = kind_of(n)
            ts = t[0]
            te = launch_end(ts, c_abs)
            wall_ms = int(round(WINDOW / MC_LO)) if (own600 and n == launches - 1) else te - ts
            iters = IPH * 1024
            cyc = WINDOW + 37
            rec = {'kind': k, 'form_id': kinds[k]['form_id'], 'per_instr': kinds[k]['per_instr'], 'launch': n,
                   'letter': letter_of(n), 'orient': orient, 'harts': 1, 'participants': 1024, 'iters': iters,
                   'iters_min': IPH, 'iters_max': IPH, 'instr_body': iters * 128,
                   'retired_counter': IPH * 1024 * 131 + 1024 * ENTRY, 'icache_req': 2 * IPH * 128,
                   'icache_miss': 128 * 9, 'l1d_miss': 4096, 'cycles_max': cyc, 'cycles_mean': cyc,
                   'instr_per_cycle_per_hart': iters * 128 / cyc / 1024, 'instr_per_s_600': iters * 128 / (cyc / 0.6e9),
                   'ra': '0x0', 'gp': '0x0', 'deadline': '0x0', 'ra_gp_differ': 0, 'window': WINDOW,
                   'wall_s': wall_ms / 1000.0, 't_start_ms': ts, 't_end_ms': te, 'check_bad': 0, 'ok': True}
            rec.update({'host': host, 'block': blk, 'rc': 0}, **info)
            runs.append(rec)
            segs.append((ts, te, lv[k]))
            t[0] = te
        last_end = t[0]
        if c_abs is not None and c_abs <= last_end:
            clk.append((max(c_abs, first), last_end + RESET_MS))
        if a.variant == 'faults' and tr == 'T5' and pj == 9:
            p700.append(first + 2500)
            special['t5_700_at_ms'] = first + 2500
        if a.variant == 'faults' and tr == 'T10' and pj == 4:
            nofield.append(first + 3000)
            special['t10_nofield_at_ms'] = first + 3000
        if own600:
            special['t6_own600_proc'] = 7
        t[0] += 300
        mark(mkind, t0, t[0], blk, rc=0, **info)

    def anchor(k, secs, role, blk):
        idle(4500, 'before ' + k, blk)
        # E197's host in burst mode: launches while less than secs have passed since its first launch's start
        c = draw_c()
        start = t[0] + 500
        c_abs = start + int(round(c * 1000)) if c is not None else None
        n, tt = 0, start
        while tt - start < secs * 1000:
            tt = launch_end(tt, c_abs)
            n += 1
        device(blk, n, {'kind_run': k, 'role': role}, lambda m: k, lambda m: '-', '', 'anchor', c=c)

    def train_proc(p, j, o, blk, label=None):
        info = {'train': label or p['train'], 'proc': j, 'orient': o, 'F': p['F'], 'S': p['S']}
        if label:
            info['of'] = p['train']
        letter = lambda n: o[0] if n == 0 else o[(n - 1) % 4]
        c = draw_c()
        if a.variant == 'faults' and not label and p['train'] == 'T8' and j == 3:
            c = 1.45
            special['t8_climb_1450_proc'] = 3
        if a.variant == 'faults' and not label and p['train'] == 'T9' and j == 5:
            c = 1.60
            special['t9_climb_1600_proc'] = 5
        device(blk, 13, info, lambda n: p['F'] if letter(n) == 'F' else p['S'], letter, o, 'train', c=c)

    other = {'SFFS': 'FSSF', 'FSSF': 'SFFS'}
    t[0] += 10000
    idle(5000, 'before', 'smoke')
    for k in ('nop.z', 'res.k0', 'res.k64'):
        anchor(k, 1.0, 'smoke_anchor', 'smoke')
    t8 = [p for p in plan if p['train'] == 'T8'][0]
    train_proc(t8, 0, t8['first'], 'smoke', 'smoke')
    train_proc(t8, 1, other[t8['first']], 'smoke', 'smoke')
    marks.append(dict(kind='smoke_gate', host=host, block='smoke', ok=True, launches=26))
    blocks = ['E'] if a.plan == 'ext' else ['A', 'B', 'C', 'D']
    for bi, b in enumerate(blocks):
        if bi:
            t[0] += 30000
        idle(10000, 'before', b)
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
        idle(10000, 'after', b)
    t[0] += 8000
    t_end = t[0]
    segs.sort()
    clk.sort()
    # telemetry: in 10 ms steps the board's level over idle drives the core rail's filter; a sample every 100 ms at 50 ms past
    # the session's grid. A sample on a launch boundary belongs to the earlier launch (closed segments, the earlier first).
    tel = []
    si = ci = 0
    y = RAIL_IDLE_W
    held, nheld = None, 0
    p700s, nofs = set(p700), set(nofield)
    for tm in range(a.t0_ms, t_end, 10):
        while si < len(segs) and segs[si][1] < tm:
            si += 1
        while ci < len(clk) and clk[ci][1] < tm:
            ci += 1
        busy = si < len(segs) and segs[si][0] <= tm <= segs[si][1]
        hi = ci < len(clk) and clk[ci][0] <= tm <= clk[ci][1]
        over = (segs[si][2] + BASE_W_800 if hi else SCALE600 * segs[si][2]) if busy else 0.0
        target = RAIL_IDLE_W + RAIL_SHARE * over
        y = target + (y - target) * math.exp(-0.01 / TAU)
        if (tm - a.t0_ms) % 100 != 50:
            continue
        board = IDLE_W + over
        mhz = 800 if hi else 600
        if any(abs(tm - p) < 50 for p in p700s):
            mhz = 700
        if a.variant == 'noisy':
            board += rng.gauss(0.0, 0.05)
            if held is not None and nheld < 2 and rng.random() < 0.5:
                board, nheld = held, nheld + 1
            else:
                nheld = 0
            held = board
            if rng.random() < 0.004:
                board -= 6.0
        s = {'t_ms': tm, 'board_w': round(board, 4), 'mhz': {'minion': mhz},
             'sp': {'minion_w': [round(y, 6)], 'minion_mv': [MV]}, 'temp_c': {'minshire': [50]}}
        if any(abs(tm - p) < 50 for p in nofs):
            s['mhz'] = {}
        tel.append(s)
    with open(os.path.join(a.out, 'telemetry.jsonl'), 'w') as f:
        f.write('# a synthetic sampler on a governed card: arbitrary test values\n')
        for s in tel:
            f.write(json.dumps(s) + '\n')
    with open(os.path.join(a.out, 'runs.jsonl'), 'w') as f:
        for r in runs:
            f.write(json.dumps(r) + '\n')
    with open(os.path.join(a.out, 'marks.jsonl'), 'w') as f:
        for m in marks:
            f.write(json.dumps(m) + '\n')
    open(os.path.join(a.out, 'SESSION_DONE'), 'w').close()
    procs = [r for r in runs if r.get('train') and r.get('train') != 'smoke' and r['launch'] == 0]
    inj = {'note': 'ARBITRARY TEST VALUES: not a forecast and not a measurement', 'variant': a.variant, 'plan': a.plan,
           'D_W': INJ_D, 'levels_over_idle_W_800': lv, 'idle_W': IDLE_W, 'base800_W': BASE_W_800, 'scale600': SCALE600,
           'rail_share': RAIL_SHARE, 'v_rail': MV / 1000.0, 'rate_800': 1024 * IPH * 128 / ((WINDOW + 37) / 0.8e9),
           'special': special, 'climbs_from': 'list' if pool else ('none' if a.variant == 'nogov' else 'uniform'),
           'launches': len(runs), 'train_processes': len(procs), 'samples': len(tel),
           'session_s': (t_end - a.t0_ms) / 1000.0}
    json.dump(inj, open(os.path.join(a.out, 'injected.json'), 'w'), indent=1)
    print('synthetic %s session (%s plan): %d launch records, %d train processes, %d samples, %.1f s, planted %s' % (
        a.variant, a.plan, len(runs), len(procs), len(tel), inj['session_s'], special or 'none'))


if __name__ == '__main__':
    main()
