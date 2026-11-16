#!/usr/bin/env python3
"""Reduce a regfile session: every train's D(F) - D(S), the per-bit prices, electrons. Registered before any datum.

    python3 -B reduce_regfile.py OUT [OUT ...] --out regfile.json [--prediction prediction.json] [--participants 1024]

Inputs per OUT dir: runs.jsonl and marks.jsonl (run_trains.py), telemetry.jsonl (the session's sampler, one JSON object
per line; other lines are skipped), trains.tsv beside this file. Several OUT dirs (a second sitting) pool by unit.
Standard library only.

The train statistic is the public lab repo's train form (E182's registered statistics), written out here:
  a launch's reading: the mean of the board samples (board_w) in [its start + 170 ms, its end] after the dip rules
    over the session's whole sample sequence: the lab's (a sample is dropped when it is more than 4.0 W below both of
    the samples two before and two after it) and, because a low reading is held for a whole meter pass (2 or 3
    samples), this one too: a sample is dropped when it is more than 4.0 W below the median of the 11 samples centred
    on it; fewer than 2 samples left: no reading;
  a quad (launches 4q+1..4q+4, q = 0, 1, 2; launch 0 settles): s (L2 + L3 - L1 - L4) / 2, s = +1 in an SFFS process,
    -1 in an FSSF one, so every quad reads D(F) - D(S);
  a process's value: the mean of its complete quads; a unit: processes 2j and 2j+1 of a train within one block of one
    session (opposite orientations by the plan), the mean of the two, made only when both give a value; the train's
    estimate: the mean over units (every block, every session) with the t(0.975, n-1) interval; fewer than 8 units:
    NOT SCORED.
Processes are keyed by (session, block, process number), and only the blocks of trains.tsv count: the smoke block's
processes (labelled "smoke" by run_trains.py, block "smoke") never enter a train.

Gates (registered; a failed gate drops what it names, and the reason is counted):
  a process gives no value when: it has other than 13 launch records, a launch is not ok (a failed launch or a failed
  register check: check_bad > 0), a launch's participants are not --participants (1,024 harts: hart 0 of every
  minion), its letters are not the plan's, its exit code is not 0, a launch's device rate departs from the train's
  median by more than 0.5 %, a telemetry sample in its span is off the session's clock by more than 1 MHz, or a STOP
  was written before its last launch ended (the STOP's time: the t_ms of its JSON line, which the scripts write; a
  STOP made by hand, `touch OUT/STOP`, carries none, and its time is the file's modification time as run_trains.py
  read it on the box when it saw the file, a mark "stop_seen", else the file's own modification time);
  a train is NOT SCORED (its estimate printed beside, with no interval and no verdict) when it has fewer than 8 units,
  or when the median device rate of its F launches and of its S launches differ by more than 0.05 % (the rate ratio
  F / S is reported beside every train and every price: an issue-rate difference between the two kinds would change
  the power without changing the event the train prices);
  a derived price is NOT SCORED when any train in it is.

Reported beside, never a gate: retired instructions over body instructions per kind (expected 131/128 = 1.0234 plus
the entry and exit; flagged beyond 0.5 %), L1 data misses in the loop (expected 0), instruction-cache misses per loop
iteration for F and S, launches where a hart's iterations fall more than 1 % below the mean hart's (a hart that left
its loop early or ran slow), the rail voltage samples beyond 3 mV of the session median in the trains' spans, the
anchors' first and last bursts of each block (flagged beyond 0.3 W apart), each train's carry-over c, and the train
gain g (flagged outside 0.95-1.05).

Energy per instruction: D / R, R = the train's median device rate (body instructions a second over all harts:
instr_body x clock / cycles_max, at the session's median clock). Board energy; electrons through the 12 V input
E / (e x 12 V) (the input's voltage is not metered: 12 V nominal). The core rail: a 0.4 s alternation is smeared by
the rail's 1 s filter, so the trains read the board only; the rail's share of a data-dependent difference is taken
from the anchors (res.k64 against nop.z bursts, the rail read over each burst's last 1.5 s, divided by the fraction
(about 0.87 for a 3 s burst) that a first-order filter with tau 1.05 s reaches there after a step at the burst's first
launch, over the last 5 s of the nearer of the block's two 10 s idle periods (the 4.5 s gaps are too short for the
rail's filter to forget the burst before); the board over [first launch + 0.5 s, last launch's end], over the last
3 s of the gap before it), and E_rail / (e x V_rail) gives electrons through the core rail at its measured voltage.

Derived prices (each a linear combination of independent trains, Welch-Satterthwaite):
  cell           T1 / 64                       one stored bit that changes on a write
  cell_ctrl      (T1 - T2) / 64                the same, with the check T2 subtracted
  order          T2                            the destination order alone: zero by design (bounded)
  result_bit     T3 / 64                       one result bit along the result path into the file, sources fixed
  result_bit32   T4 / 32                       the same at 32 bits; lin_result = T4 - T3 / 2 (0 if linear; bounded)
  write          T5                            one register write against a write to x0, value unchanged
  dest_switch    T6                            two destinations in turn against one, per instruction
  dest_n8        T7                            eight destinations against two (bounded; second sitting)
  read2_field    T8 / 64                       one bit on read port 2 when bits 24:20 name the register, operand unused
  read2_net      (T8 - T9 / 2) / 64            the same less the share of held ones that T9 prices (T8's F kind holds
                                               32 ones in each named register, half of T9's)
  held_one       T9 / 128                      one held 1-bit of the two named registers, per read switch
  read2_operand  T10 / 64                      one bit on read port 2 used as the operand, result masked
  operand_path   (T10 - T8) / 64               the operand's path past the register file, per bit
  read1_field    T11 / 64                      one bit on read port 1 when bits 19:15 name the register
  field_bit      T12 / 4                       one more bit of the second source field (5 against 1)
  field_bit3     T15 / 2                       the same from 3 against 1; lin_field = T15 - T12 / 2 (0 if linear; bounded)
  field_first    T13                           the first field bit (one bit and the change of register)
  field_base     T13 - T12 / 4                 a change of the register read, beyond its field bits
  read_n8        T14                           eight source registers against two (bounded; second sitting)
Verdicts: POSITIVE / NEGATIVE (the 95 % interval excludes 0), else NOT RESOLVED; for the prices that are zero by
design or by a linear law (order, lin_result, lin_field, dest_n8, read_n8): BOUNDED when the interval holds 0, the
bound being the interval itself, printed in W and in fJ an instruction; else POSITIVE / NEGATIVE.
Reading rule (registered): cell (T1 / 64) is the stored-bit price when order (T2) reads BOUNDED; when T2 reads
POSITIVE or NEGATIVE, cell_ctrl is read first and the reason is printed. When the train gain lies outside 0.95-1.05,
the gain-corrected prices are read first.
With --prediction: SIZE PASS / FAIL HIGH / FAIL LOW against each forecast line (the line inside, above or below the
interval).
"""
import argparse
import bisect
import json
import math
import os
import statistics

E_CH = 1.602176634e-19
LAG_MS = 170
DIP_W = 4.0
MIN_UNITS = 8
RATE_GATE = 0.005
RATIO_GATE = 0.0005
TAU = 1.05
LAUNCHES = 13
RETIRED_PER_BODY = 131.0 / 128.0
HERE = os.path.dirname(os.path.abspath(__file__))
DERIVED = {  # name: ([(train, coefficient)], divisor, unit of the result)
    'cell': ([('T1', 1)], 64, 'bit'), 'cell_ctrl': ([('T1', 1), ('T2', -1)], 64, 'bit'), 'order': ([('T2', 1)], 1, 'instr'),
    'result_bit': ([('T3', 1)], 64, 'bit'), 'result_bit32': ([('T4', 1)], 32, 'bit'),
    'lin_result': ([('T4', 1), ('T3', -0.5)], 1, 'instr'), 'write': ([('T5', 1)], 1, 'instr'),
    'dest_switch': ([('T6', 1)], 1, 'instr'), 'dest_n8': ([('T7', 1)], 1, 'instr'),
    'read2_field': ([('T8', 1)], 64, 'bit'), 'read2_net': ([('T8', 1), ('T9', -0.5)], 64, 'bit'),
    'held_one': ([('T9', 1)], 128, 'bit'),
    'read2_operand': ([('T10', 1)], 64, 'bit'), 'operand_path': ([('T10', 1), ('T8', -1)], 64, 'bit'),
    'read1_field': ([('T11', 1)], 64, 'bit'), 'field_bit': ([('T12', 1)], 4, 'bit'),
    'field_bit3': ([('T15', 1)], 2, 'bit'), 'lin_field': ([('T15', 1), ('T12', -0.5)], 1, 'instr'),
    'field_first': ([('T13', 1)], 1, 'instr'), 'field_base': ([('T13', 1), ('T12', -0.25)], 1, 'instr'),
    'read_n8': ([('T14', 1)], 1, 'instr'),
}
BOUNDED = ('order', 'lin_result', 'lin_field', 'dest_n8', 'read_n8')


# ------------------------------------------------------------------ t quantiles (regularized incomplete beta)
def _betacf(a, b, x):
    tiny = 1e-300
    c, d = 1.0, 1.0 - (a + b) * x / (a + 1.0)
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        for aa in (m * (b - m) * x / ((a - 1.0 + m2) * (a + m2)), -(a + m) * (a + b + m) * x / ((a + m2) * (a + 1.0 + m2))):
            d = 1.0 + aa * d
            d = 1.0 / (d if abs(d) > tiny else tiny)
            c = 1.0 + aa / c if abs(c) > tiny else 1e300
            h *= d * c
        if abs(d * c - 1.0) < 1e-15:
            break
    return h


def _ibeta(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lb) * _betacf(b, a, 1 - x) / b


def t975(df):
    if df >= 4000:
        return 1.959963984540054
    lo, hi = 0.0, 1e3
    for _ in range(200):
        mid = (lo + hi) / 2
        p = 1.0 - 0.5 * _ibeta(df / 2.0, 0.5, df / (df + mid * mid))
        lo, hi = (mid, hi) if p < 0.975 else (lo, mid)
    return (lo + hi) / 2


def interval(values):
    v = [float(x) for x in values if x is not None]
    n = len(v)
    if n < 2:
        return {'n': n, 'mean': v[0] if v else None, 'se': None, 'df': None, 'lo': None, 'hi': None}
    m = statistics.mean(v)
    se = statistics.stdev(v) / math.sqrt(n)
    hw = t975(n - 1) * se
    return {'n': n, 'mean': m, 'se': se, 'df': n - 1, 'lo': m - hw, 'hi': m + hw, 'hw': hw}


def scored(iv):
    return iv is not None and iv.get('lo') is not None and iv.get('se') is not None


def combine(terms, k):
    """sum(c x) / k over independent intervals x (Welch-Satterthwaite df); NOT SCORED if any term is not scored"""
    if not terms or any(not scored(x) for x, _ in terms):
        return {'mean': None, 'se': None, 'df': None, 'lo': None, 'hi': None, 'note': 'NOT SCORED: a train in it is'}
    m = sum(c * x['mean'] for x, c in terms) / k
    vs = [(c * x['se'] / k) ** 2 for x, c in terms]
    se = math.sqrt(sum(vs))
    den = sum(v * v / x['df'] for v, (x, _) in zip(vs, terms) if v > 0)
    df = sum(vs) ** 2 / den if den > 0 else float(min(x['df'] for x, _ in terms))
    hw = t975(df) * se
    return {'mean': m, 'se': se, 'df': df, 'lo': m - hw, 'hi': m + hw, 'hw': hw}


def sign_of(iv):
    if not scored(iv):
        return 'NOT SCORED'
    return 'POSITIVE' if iv['lo'] > 0 else ('NEGATIVE' if iv['hi'] < 0 else 'NOT RESOLVED')


def bounded_of(iv):
    s = sign_of(iv)
    return 'BOUNDED' if s == 'NOT RESOLVED' else s


def size_of(iv, line):
    if iv.get('lo') is None or line is None:
        return 'NOT SCORED'
    if iv['lo'] <= line <= iv['hi']:
        return 'PASS'
    return 'FAIL HIGH' if line > iv['hi'] else 'FAIL LOW'


# ------------------------------------------------------------------ inputs
def jl(path):
    out = []
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    return out


def num(s, *keys):
    for k in keys:
        if isinstance(s, dict) and k in s:
            s = s[k]
        elif isinstance(s, list) and isinstance(k, int) and k < len(s):
            s = s[k]
        else:
            return None
    return float(s) if isinstance(s, (int, float)) else None


def plan():
    """trains.tsv -> {train: {F, S, role, blocks: {block: processes}, processes}}"""
    rows = {}
    for line in open(os.path.join(HERE, 'trains.tsv')):
        if line.strip() and not line.startswith('#'):
            b, tr, f, s, n, first, short, role = line.rstrip('\n').split('\t')
            r = rows.setdefault(tr, {'F': f, 'S': s, 'role': role, 'blocks': {}, 'processes': 0})
            if (r['F'], r['S']) != (f, s):
                raise SystemExit('trains.tsv: train %s has two different kind pairs' % tr)
            r['blocks'][b] = int(n)
            r['processes'] += int(n)
    return rows


def dips_kept(samples):
    v = [w for _, w in samples]
    keep = [True] * len(v)
    for i in range(2, len(v) - 2):
        if v[i] < min(v[i - 2], v[i + 2]) - DIP_W:
            keep[i] = False
    for i in range(len(v)):
        if v[i] < statistics.median(v[max(0, i - 5):i + 6]) - DIP_W:
            keep[i] = False
    return [s for s, k in zip(samples, keep) if k]


def stop_time(out, marks):
    """(epoch ms, its source) of the session's STOP, or (None, None): the t_ms of the file's JSON line; for a STOP made
    by hand (empty, or not JSON with a t_ms) the file's modification time as run_trains.py read it on the box (the
    earliest mark "stop_seen": a copy of OUT need not keep the file's own time), else the file's own modification
    time"""
    path = os.path.join(out, 'STOP')
    if not os.path.exists(path):
        return None, None
    try:
        with open(path) as f:
            t = json.loads(f.readline()).get('t_ms')
        if isinstance(t, (int, float)) and not isinstance(t, bool):
            return float(t), 'file t_ms'
    except (ValueError, AttributeError, OSError):
        pass
    seen = [m['stop_mtime_ms'] for m in marks if m.get('kind') == 'stop_seen'
            and isinstance(m.get('stop_mtime_ms'), (int, float)) and not isinstance(m.get('stop_mtime_ms'), bool)]
    if seen:
        return float(min(seen)), 'stop_seen mark'
    return os.path.getmtime(path) * 1000.0, 'file mtime'


def session(out, idx):
    tel = jl(os.path.join(out, 'telemetry.jsonl'))
    runs = jl(os.path.join(out, 'runs.jsonl'))
    marks = jl(os.path.join(out, 'marks.jsonl'))
    bs = sorted((s['t_ms'], num(s, 'board_w')) for s in tel if 't_ms' in s and num(s, 'board_w') is not None)
    kept = dips_kept(bs)
    ts = [t for t, _ in kept]
    ws = [w for _, w in kept]
    mhz = sorted(x for x in (num(s, 'mhz', 'minion') for s in tel) if x)
    mvs = sorted((s['t_ms'], num(s, 'sp', 'minion_mv', 0)) for s in tel if 't_ms' in s and num(s, 'sp', 'minion_mv', 0))
    rail = sorted((s['t_ms'], num(s, 'sp', 'minion_w', 0)) for s in tel if 't_ms' in s and num(s, 'sp', 'minion_w', 0) is not None)
    clk = statistics.median(mhz) if mhz else 600.0
    stop_t, stop_from = stop_time(out, marks)
    mv_med = statistics.median([v for _, v in mvs]) if mvs else None
    return {'idx': idx, 'dir': os.path.basename(os.path.abspath(out)), 'tel': tel, 'runs': runs, 'marks': marks,
            'ts': ts, 'ws': ws, 'clk': clk, 'v_rail': mv_med / 1000.0 if mv_med else None, 'mv': mvs, 'mv_med': mv_med,
            'rail': rail, 'stop_t': stop_t, 'stop_from': stop_from, 'dips': len(bs) - len(kept), 'samples': len(bs)}


def reading(S, t0, t1):
    i0 = bisect.bisect_left(S['ts'], t0 + LAG_MS)
    i1 = bisect.bisect_right(S['ts'], t1)
    w = S['ws'][i0:i1]
    return sum(w) / len(w) if len(w) >= 2 else None


def off_clock(S, t0, t1):
    for s in S['tel']:
        t = s.get('t_ms')
        if t is not None and t0 <= t <= t1:
            f = num(s, 'mhz', 'minion')
            if f is not None and abs(f - S['clk']) > 1.0:
                return True
    return False


def window_mean(series, t0, t1):
    v = [w for t, w in series if t0 <= t <= t1]
    return sum(v) / len(v) if v else None


def anchors(S):
    """each anchor burst (its launch records): board and rail over the last 3 s of the idle before; the rail's share of
    res.k64 - nop.z per block and position"""
    marks = sorted(S['marks'], key=lambda m: m.get('t0_ms', 0))
    idles = [m for m in marks if m.get('kind') == 'idle']
    groups = {}
    for r in S['runs']:
        if r.get('role') in ('anchor_first', 'anchor_last') and r.get('ok'):
            groups.setdefault((r.get('block'), r.get('role'), r.get('kind_run')), []).append(r)
    out = []
    board = list(zip(S['ts'], S['ws']))
    for (blk, role, kind), recs in sorted(groups.items(), key=lambda kv: min(r['t_start_ms'] for r in kv[1])):
        t_a = min(r['t_start_ms'] for r in recs)
        t_b = max(r['t_end_ms'] for r in recs)
        before = [m for m in idles if m.get('t1_ms', 0) <= t_a]
        if not before:
            continue
        il = before[-1]
        b_idle = window_mean(board, il['t1_ms'] - 3000, il['t1_ms'])
        long_idle = [m for m in idles if m.get('block') == blk and m.get('label') in ('before', 'after')]
        r_idle = None
        if long_idle:
            li = min(long_idle, key=lambda m: min(abs(m['t1_ms'] - t_a), abs(m['t0_ms'] - t_b)))
            r_idle = window_mean(S['rail'], li['t1_ms'] - 5000, li['t1_ms'])
        b = window_mean(board, t_a + 500, t_b)
        r = window_mean(S['rail'], t_b - 1500, t_b)
        dur = (t_b - t_a) / 1000.0
        frac = 1.0 - (TAU / 1.5) * (math.exp(-(dur - 1.5) / TAU) - math.exp(-dur / TAU)) if dur > 1.5 else None
        out.append({'session': S['dir'], 'block': blk, 'kind': kind, 'role': role, 't0_ms': t_a, 'launches': len(recs),
                    'frac': frac, 'board_over_idle_w': (b - b_idle) if None not in (b, b_idle) else None,
                    'rail_over_idle_w': ((r - r_idle) / frac) if None not in (r, r_idle, frac) else None})
    shares = []
    drift = []
    for blk in sorted({x['block'] for x in out}):
        for role in ('anchor_first', 'anchor_last'):
            hi = [x for x in out if x['block'] == blk and x['role'] == role and x['kind'] == 'res.k64']
            lo = [x for x in out if x['block'] == blk and x['role'] == role and x['kind'] == 'nop.z']
            if hi and lo and None not in (hi[0]['board_over_idle_w'], lo[0]['board_over_idle_w'],
                                          hi[0]['rail_over_idle_w'], lo[0]['rail_over_idle_w']):
                db = hi[0]['board_over_idle_w'] - lo[0]['board_over_idle_w']
                dr = hi[0]['rail_over_idle_w'] - lo[0]['rail_over_idle_w']
                if db > 0.2:
                    shares.append(dr / db)
        for kind in ('nop.z', 'res.k0', 'res.k64'):
            a = [x for x in out if x['block'] == blk and x['kind'] == kind and x['role'] == 'anchor_first']
            z = [x for x in out if x['block'] == blk and x['kind'] == kind and x['role'] == 'anchor_last']
            if a and z and None not in (a[0]['board_over_idle_w'], z[0]['board_over_idle_w']):
                d = z[0]['board_over_idle_w'] - a[0]['board_over_idle_w']
                drift.append({'session': S['dir'], 'block': blk, 'kind': kind, 'last_minus_first_w': d, 'flag': abs(d) > 0.3})
    return out, shares, drift


def _rate(S, r):
    return r.get('instr_body', 0) * S['clk'] * 1e6 / r['cycles_max'] if r.get('cycles_max') else None


def train_result(sessions, tr, P, participants):
    want = P[tr]
    procs = []
    for S in sessions:
        bykey = {}
        for r in S['runs']:
            if r.get('train') == tr and r.get('block') in want['blocks']:
                bykey.setdefault((r.get('block'), r.get('proc')), []).append(r)
        for (blk, j) in sorted(k for k in bykey if k[1] is not None):
            recs = sorted(bykey[(blk, j)], key=lambda r: r.get('launch', 0))
            o = recs[0].get('orient')
            letters = [o[0]] + [o[(n - 1) % 4] for n in range(1, LAUNCHES)] if o in ('SFFS', 'FSSF') else None
            why = None
            if len(recs) != LAUNCHES:
                why = 'launches %d' % len(recs)
            elif not all(r.get('ok') for r in recs) or any(r.get('check_bad') for r in recs):
                why = 'launch not ok'
            elif participants and any(r.get('participants') != participants for r in recs):
                why = 'participants'
            elif [r.get('letter') for r in recs] != letters:
                why = 'letters'
            elif any(r.get('rc') != 0 for r in recs):
                why = 'exit code'
            t0, t1 = recs[0].get('t_start_ms', 0), recs[-1].get('t_end_ms', 0)
            if why is None and off_clock(S, t0, t1):
                why = 'clock'
            if why is None and S['stop_t'] is not None and S['stop_t'] <= t1:
                why = 'stop'
            rr = [_rate(S, r) for r in recs if r.get('cycles_max')]
            procs.append({'S': S, 'block': blk, 'proc': j, 'orient': o, 'recs': recs, 'why': why, 'rates': rr})
    rates = [x for p in procs for x in p['rates']]
    med = statistics.median(rates) if rates else None
    dropped = {}
    carry = {'SFFS': [], 'FSSF': []}
    value = {}
    for p in procs:
        if p['why'] is None and med and any(abs(x - med) / med > RATE_GATE for x in p['rates']):
            p['why'] = 'rate'
        if p['why'] is not None:
            dropped[p['why']] = dropped.get(p['why'], 0) + 1
            continue
        rd = {r['launch']: reading(p['S'], r['t_start_ms'], r['t_end_ms']) for r in p['recs']}
        sg = 1.0 if p['orient'] == 'SFFS' else -1.0
        quads = []
        for q in range(3):
            ix = [4 * q + 1, 4 * q + 2, 4 * q + 3, 4 * q + 4]
            if all(rd.get(i) is not None for i in ix):
                L1, L2, L3, L4 = (rd[i] for i in ix)
                quads.append(sg * (L2 + L3 - L1 - L4) / 2)
                carry[p['orient']].append(L3 - L2)
        if quads:
            value[(p['S']['idx'], p['block'], p['proc'])] = (p['orient'], sum(quads) / len(quads))
        else:
            dropped['no reading'] = dropped.get('no reading', 0) + 1
    units = []
    for (si, blk, j) in sorted(value):
        if j % 2 == 0 and (si, blk, j + 1) in value:
            (o1, v1), (o2, v2) = value[(si, blk, j)], value[(si, blk, j + 1)]
            if o1 != o2:
                units.append((v1 + v2) / 2)
    # the two kinds' issue rates, over the kept processes' launches
    kept = [p for p in procs if p['why'] is None]
    rF = [_rate(p['S'], r) for p in kept for r in p['recs'] if r.get('letter') == 'F' and r.get('cycles_max')]
    rS = [_rate(p['S'], r) for p in kept for r in p['recs'] if r.get('letter') == 'S' and r.get('cycles_max')]
    ratio = statistics.median(rF) / statistics.median(rS) if rF and rS else None
    iv = interval(units)
    note = None
    if not procs:
        note = 'NOT SCORED: not run'
    elif len(units) < MIN_UNITS:
        note = 'NOT SCORED: %d units' % len(units)
    elif ratio is None or abs(ratio - 1.0) > RATIO_GATE:
        note = 'NOT SCORED: rate ratio F/S %s' % ('%.5f' % ratio if ratio else 'missing')
    if note:
        iv = dict(iv, lo=None, hi=None, note=note)
    c = None
    if iv.get('mean') is not None and abs(iv['mean']) > 0.1 and carry['SFFS'] and carry['FSSF']:
        c = (statistics.mean(carry['SFFS']) - statistics.mean(carry['FSSF'])) / (2 * iv['mean'])
    # reported beside: the denominators by kind
    rep = {}
    for L, name in (('F', want['F']), ('S', want['S'])):
        recs = [r for p in kept for r in p['recs'] if r.get('letter') == L]
        ret = [r['retired_counter'] / r['instr_body'] for r in recs if r.get('instr_body') and r.get('retired_counter') is not None]
        icm = [r['icache_miss'] / r['iters'] for r in recs if r.get('iters') and r.get('icache_miss') is not None]
        l1m = [r.get('l1d_miss') for r in recs if r.get('l1d_miss') is not None]
        slow = sum(1 for r in recs if r.get('iters_min') is not None and r.get('participants')
                   and r['iters_min'] < 0.99 * r['iters'] / r['participants'])
        rep[L] = {'kind': name, 'launches': len(recs),
                  'retired_per_body': statistics.median(ret) if ret else None,
                  'retired_flag': bool(ret) and abs(statistics.median(ret) / RETIRED_PER_BODY - 1) > 0.005,
                  'icache_miss_per_iter': statistics.median(icm) if icm else None,
                  'l1d_miss_median': statistics.median(l1m) if l1m else None,
                  'launches_with_a_slow_hart': slow}
    mv_off = 0
    mv_n = 0
    for p in kept:
        S = p['S']
        if S['mv_med'] is None:
            continue
        t0, t1 = p['recs'][0].get('t_start_ms', 0), p['recs'][-1].get('t_end_ms', 0)
        for t, v in S['mv']:
            if t0 <= t <= t1:
                mv_n += 1
                mv_off += abs(v - S['mv_med']) > 3.0
    return {'train': tr, 'F': want['F'], 'S': want['S'], 'role': want['role'], 'planned': want['processes'],
            'processes': len(procs), 'dropped': dropped, 'units': len(units), 'rate_median': med,
            'rate_ratio_F_over_S': ratio, 'D_W': iv, 'sign': sign_of(iv), 'carry_over': c, 'by_kind': rep,
            'rail_mv_samples_off_3mV': [mv_off, mv_n]}


def per_instr(iv, rate, scale=1.0):
    """W -> pJ per instruction (x scale)"""
    if iv.get('mean') is None or not rate:
        return None
    f = 1e12 / rate * scale
    return {k: (iv[k] * f if iv.get(k) is not None else None) for k in ('mean', 'se', 'lo', 'hi')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outs', nargs='+')
    parser.add_argument('--out', default='regfile.json')
    parser.add_argument('--prediction', default=None, help='a frozen forecast (prediction.json), for the SIZE words')
    parser.add_argument('--participants', type=int, default=1024, help='harts a launch must report (0: not checked)')
    a = parser.parse_args()
    P = plan()
    sessions = [session(o, i) for i, o in enumerate(a.outs)]
    anc, shares, drift = [], [], []
    for S in sessions:
        x, shs, dr = anchors(S)
        anc += x
        shares += shs
        drift += dr
    share = statistics.median(shares) if shares else None
    v_rail = statistics.median([S['v_rail'] for S in sessions if S['v_rail']]) if any(S['v_rail'] for S in sessions) else None
    trains = {tr: train_result(sessions, tr, P, a.participants) for tr in P}
    bursts = []
    for sess in sorted({x['session'] for x in anc}):
        for blk in sorted({x['block'] for x in anc if x['session'] == sess}):
            for role in ('anchor_first', 'anchor_last'):
                hi = [x for x in anc if x['session'] == sess and x['block'] == blk and x['role'] == role and x['kind'] == 'res.k64']
                lo = [x for x in anc if x['session'] == sess and x['block'] == blk and x['role'] == role and x['kind'] == 'res.k0']
                if hi and lo and None not in (hi[0]['board_over_idle_w'], lo[0]['board_over_idle_w']):
                    bursts.append(hi[0]['board_over_idle_w'] - lo[0]['board_over_idle_w'])
    gain = None
    if bursts and trains.get('T3', {}).get('D_W', {}).get('mean') is not None:
        gain = trains['T3']['D_W']['mean'] / statistics.median(bursts)
    pred = json.load(open(a.prediction)) if a.prediction else None
    res = {'trains': trains, 'derived': {}, 'anchors': anc, 'anchor_drift': drift, 'rail_share': share,
           'rail_shares': shares, 'v_rail': v_rail, 'burst_res64_minus_res0_W': bursts, 'train_gain': gain,
           'train_gain_flag': gain is not None and not (0.95 <= gain <= 1.05),
           'clock_mhz': [S['clk'] for S in sessions], 'samples': [S['samples'] for S in sessions],
           'dips': [S['dips'] for S in sessions], 'participants_gate': a.participants,
           'stops': [{'session': S['dir'], 't_ms': S['stop_t'], 'from': S['stop_from']} for S in sessions]}
    for name, (terms, k, unit) in DERIVED.items():
        if not all(t in trains for t, _ in terms):
            continue
        ivs = [(trains[t]['D_W'], c) for t, c in terms]
        iv = combine(ivs, k)
        rates = [trains[t]['rate_median'] for t, _ in terms if trains[t]['rate_median']]
        rate = statistics.median(rates) if rates else None
        board_pj = per_instr(iv, rate)
        d = {'W': iv, 'per': unit, 'board_pJ': board_pj, 'sign': sign_of(iv),
             'rate_ratio_F_over_S': {t: trains[t]['rate_ratio_F_over_S'] for t, _ in terms}}
        if name in BOUNDED:
            d['verdict'] = bounded_of(iv)
            if scored(iv):
                d['bound_W'] = [iv['lo'], iv['hi']]
                d['bound_fJ_per_instr'] = [iv['lo'] / rate * 1e15 * k, iv['hi'] / rate * 1e15 * k] if rate else None
        else:
            d['verdict'] = d['sign']
        if gain and board_pj and board_pj.get('mean') is not None:
            d['board_pJ_gain_corrected'] = {kk: (v / gain if v is not None else None) for kk, v in board_pj.items()}
        if board_pj and board_pj['mean'] is not None:
            d['electrons_12V'] = board_pj['mean'] * 1e-12 / (E_CH * 12.0)
            if share and v_rail:
                d['rail_pJ'] = board_pj['mean'] * share
                d['electrons_rail'] = d['rail_pJ'] * 1e-12 / (E_CH * v_rail)
        if pred and board_pj:
            lines = (pred.get('derived', {}).get(name) or {}).get('board_pJ_lines', {})
            if board_pj.get('lo') is not None:
                pj_iv = {'lo': board_pj['lo'], 'hi': board_pj['hi']}
                d['size'] = {m: size_of(pj_iv, v) for m, v in lines.items()}
        res['derived'][name] = d
    o = res['derived'].get('order', {}).get('verdict')
    if o == 'BOUNDED':
        res['cell_reading'] = {'read': 'cell', 'why': 'order (T2) reads BOUNDED'}
    elif o in ('POSITIVE', 'NEGATIVE'):
        res['cell_reading'] = {'read': 'cell_ctrl', 'why': 'order (T2) reads %s' % o}
    else:
        res['cell_reading'] = {'read': None, 'why': 'order (T2) %s' % o}
    json.dump(res, open(a.out, 'w'), indent=1, default=lambda x: None)
    for tr, t in trains.items():
        iv = t['D_W']
        print('%-4s %-9s - %-9s units %3d  D %s W  [%s, %s]  %s  F/S %s  dropped %s%s' % (
            tr, t['F'], t['S'], t['units'], '%+.4f' % iv['mean'] if iv.get('mean') is not None else '   -   ',
            '%+.4f' % iv['lo'] if iv.get('lo') is not None else '-', '%+.4f' % iv['hi'] if iv.get('hi') is not None else '-',
            t['sign'], '%.5f' % t['rate_ratio_F_over_S'] if t['rate_ratio_F_over_S'] else '-', t['dropped'] or '',
            ('  (' + iv['note'] + ')') if iv.get('note') else ''))
    for n, d in res['derived'].items():
        b = d['board_pJ']
        print('%-14s %s per %s board  %s' % (n, ('%+.4f pJ [%+.4f, %+.4f]' % (b['mean'], b['lo'], b['hi'])) if b and b.get('lo') is not None
                                           else '-', d['per'], d['verdict']))
    print('cell reading: %s (%s); train gain %s%s' % (res['cell_reading']['read'], res['cell_reading']['why'],
                                                      '%.3f' % gain if gain else '-', ' (outside 0.95-1.05)' if res['train_gain_flag'] else ''))


if __name__ == '__main__':
    main()
