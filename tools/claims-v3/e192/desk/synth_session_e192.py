"""E192 desk check of code (reg-e192, Q176): a small SYNTHETIC intbits session in the exact form the proposal's run_block.py
writes and reduce_intbits.py reads (runs.jsonl, marks.jsonl, telemetry.jsonl), with injected per-instruction energies, so the
registered reducer can be run unchanged and its printed quantities set beside what was injected.

NOTHING HERE IS MEASURED AND NOTHING HERE IS A FORECAST. The injected prices are arbitrary test values (prime numbers of fJ)
chosen only so the reducer's arithmetic can be traced; they say nothing about the card.

    /usr/bin/python3 -I -B synth_session_e192.py ARM_TABLE.jsonl OUTDIR [--no-pvt] [--seed 192] [--passes 9] [--noise 1] [--trise 0.04]

ARM_TABLE.jsonl: the host's `intbits_host --list --json` (one JSON object per arm: values and designed counts), which supplies
each fake INTBITS line's arm fields exactly as the host prints them. OUTDIR gets runs.jsonl, marks.jsonl, telemetry.jsonl and
injected.json (the test values and the quantities the registered formulas give for them).

The fake session: host "synthbox"; a smoke block (pass -1: nop, add.a.f2, add.cr.l31, 2 s each) and passes 0 to PASSES-1
(default 9, as registered: pass 0 the warm-up); each pass as run_block.py makes it: 10 s idle (marked 'before'), two burn-in runs of the anchor, the anchor, the 32
arms of arms.txt shuffled by random.Random("synthbox|<pass>") as run_block.py shuffles them, the anchor, 10 s idle (marked
'after'); every run 10 launches of 0.40 s with 12 ms between them, 5 s of approach before it, a 30 s gap between passes. The
fake telemetry is 10 Hz for the whole session: board_w = idle + E x rate + k_T (T - T_idle) + noise (a sample that falls in a
gap between launches reads idle: a dip); the minion rail 0.79 of the same, through a first-order filter of tau 1.05 s;
temp_c.minshire[0] whole degrees; 34 raw per-sensor codes (pvt.c) unless --no-pvt; mhz.minion 600; minion_mv 522 +- 1.
--noise scales every random term (0: a noise-free session, whose reduction must match the injected values to rounding);
--trise is the die's rise in C per W of the run's dynamic power (0: every run at the same die reading).
"""
import json
import math
import os
import random
import sys

table_path, out = sys.argv[1], sys.argv[2]
NO_PVT = '--no-pvt' in sys.argv
SEED = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 192
PASSES = int(sys.argv[sys.argv.index('--passes') + 1]) if '--passes' in sys.argv else 9
NOISE = float(sys.argv[sys.argv.index('--noise') + 1]) if '--noise' in sys.argv else 1.0
TRISE = float(sys.argv[sys.argv.index('--trise') + 1]) if '--trise' in sys.argv else 0.04
rng = random.Random(SEED)
HOST = 'synthbox'

# --- injected test values (arbitrary; NOT a forecast, NOT a measurement) ---
E0 = {('nop', 'nop'): 4.003, ('same', 'add'): 4.507, ('pair', 'add'): 4.613, ('pair', 'xor'): 4.591, ('pair', 'and'): 4.583}
P_A, P_B, P_R, P_C = 0.011, 0.013, 0.017, 0.007     # pJ per flipped port-A bit, port-B bit, result bit, carry position
K_T = 0.29          # W per C: the synthetic card's leakage slope (the reducer's own leak law gives about 0.35 at 58 C)
RAIL = 0.79         # the synthetic rail's share of the board's dynamic power
TAU = 1.05
IDLE_B, IDLE_R = 30.0, 8.0
NOISE_B, NOISE_R = 0.15 * NOISE, 0.05 * NOISE
HARTS, WINDOW, IPC = 1024, 240000000, 0.95
ITERS = int(WINDOW * IPC / 259)           # per hart per launch
LAUNCH_S, GAP_S, N_LAUNCH = 0.40, 0.012, 10

table = [json.loads(l) for l in open(table_path) if l.startswith('{')]
T = {a['arm']: a for a in table}
arms_txt = [a['arm'] for a in table]       # the 32 arms in the table's order (arms.txt's order is the same)
ANCHOR = 'add.a.f2'


def energy(arm):
    a = T[arm]
    return (E0[(a['form'], a['op'])] + P_A * a['n_port_a'] + P_B * a['n_port_b'] + P_R * a['n_result']
            + P_C * a['n_carry'])


os.makedirs(out, exist_ok=True)
runs_f = open(os.path.join(out, 'runs.jsonl'), 'w')
marks_f = open(os.path.join(out, 'marks.jsonl'), 'w')
segments = []       # (t0, t1, P_dyn, T_run, launch gaps) for the telemetry

t = 1794700000.0    # an arbitrary epoch second
pass_T = {}
pass_span = []     # (t_first, t_last, pass): from the start of its idle 'before' to the end of its idle 'after'


def mark(kind, p, t0, t1, **extra):
    marks_f.write(json.dumps(dict(kind=kind, host=HOST, **{'pass': p}, t0_ms=int(t0 * 1000), t1_ms=int(t1 * 1000), **extra)) + '\n')


def run(arm, role, p, seq, secs=4.0):
    global t
    t += 5.0                                # the approach: idle, heater, quiet (not modelled)
    n_l = N_LAUNCH if secs >= 4.0 else 5
    a = T[arm]
    instr = ITERS * 256 * HARTS
    launches, ts = [], t
    for k in range(n_l):
        l0, l1 = ts, ts + LAUNCH_S
        launches.append((l0, l1))
        ts = l1 + GAP_S
    t0, t1 = launches[0][0], launches[-1][1]
    rate = instr * n_l / (t1 - t0)
    E = energy(arm)
    P_dyn = E * 1e-12 * rate
    T_run = pass_T[p] + 0.2 + TRISE * P_dyn + rng.gauss(0.0, 0.15) * NOISE
    segments.append((t0, t1, P_dyn, T_run, launches, p))
    rc = 0
    ap = {'start_c': 58.0, 'start_hot_c': 59.2, 'heats': 1, 'wait_s': 4.8, 'quiet_s': 2.1, 'timed_out': False,
          'on_protocol': True}
    mark('run', p, t0 - 0.9, t1 + 0.2, rc=rc, arm=arm, role=role, seq=seq)
    for (l0, l1) in launches:
        cyc = WINDOW + rng.randint(30, 400)
        line = ('INTBITS {' + ','.join('"%s":%s' % (k, json.dumps(a[k])) for k in (
            'arm', 'form', 'op', 'a0', 'b0', 'a1', 'b1', 'r0', 'r1', 'n_port_a', 'n_port_b', 'n_result', 'n_carry', 'n_cell',
            'n_enc')) + ',"harts":1,"participants":%d,"iters":%d,"instr_body":%.0f,"retired_counter":%d,"icache_req":%d,'
                '"icache_miss":%d,"l1d_miss":0,"cycles_max":%d,"cycles_mean":%.0f,"instr_per_cycle_per_hart":%.4f,'
                '"instr_per_s_600":%.4e,"window":%d,"wall_s":%.4f,"t_start_ms":%d,"t_end_ms":%d,"check_bad":0,"ok":true}') % (
            HARTS, ITERS * HARTS, float(instr), instr * 259 // 256, ITERS * HARTS // 4, 128, cyc, cyc - 50.0,
            instr / cyc / HARTS, instr / (cyc / 0.6e9), WINDOW, l1 - l0, int(l0 * 1000), int(l1 * 1000))
        rec = json.loads(line[len('INTBITS '):])          # as run_block.py reads the host's stdout
        rec.update({'host': HOST, 'pass': p, 'seq': seq, 'role': role, 'approach': ap, 'rc': rc})
        runs_f.write(json.dumps(rec) + '\n')
    t = t1


def idle(p, label):
    global t
    t0 = t
    t += 10.0
    mark('idle', p, t0, t, label=label)


t_start = t
for p in [-1] + list(range(PASSES)):
    pass_T[p] = 57.7 + rng.gauss(0.0, 0.2) * NOISE
    if p >= 0:
        t += 30.0
    span0 = t
    idle(p, 'before')
    seq = 0
    if p < 0:
        for arm in ('nop', 'add.a.f2', 'add.cr.l31'):
            run(arm, 'smoke', p, seq, secs=2.0)
            seq += 1
    else:
        for _ in range(2):
            run(ANCHOR, 'burnin', p, seq)
            seq += 1
        run(ANCHOR, 'anchor_first', p, seq)
        seq += 1
        arms = list(arms_txt)
        random.Random('%s|%d' % (HOST, p)).shuffle(arms)
        for arm in arms:
            run(arm, 'arm', p, seq)
            seq += 1
        run(ANCHOR, 'anchor_last', p, seq)
        seq += 1
    idle(p, 'after')
    pass_span.append((span0, t, p))
t_end = t + 5.0
runs_f.close()
marks_f.close()

# --- the telemetry: 10 Hz over the whole session ---
segs = sorted(segments)
TS0, TS1 = t_start - 5.0, t_end


tel = open(os.path.join(out, 'telemetry.jsonl'), 'w')
tel.write('# synthetic telemetry (E192 desk check; not a measurement)\n')
idx = 0


def rail_response(ts):
    """the rail's dynamic part at time ts: the continuous first-order (tau TAU) response to every run's power box"""
    v = 0.0
    for t0, t1, P_dyn, T_run, launches, p in segs[max(0, idx - 6):idx + 1]:
        if ts < t0:
            continue
        if ts <= t1:
            v += RAIL * P_dyn * (1.0 - math.exp(-(ts - t0) / TAU))
        else:
            v += RAIL * P_dyn * (1.0 - math.exp(-(t1 - t0) / TAU)) * math.exp(-(ts - t1) / TAU)
    return v



ts = TS0
dt = 0.1
while ts < TS1:
    while idx < len(segs) and segs[idx][1] < ts:     # runs that ended before this sample
        idx += 1
    P, Tnow, gap, p_now = 0.0, None, False, None
    for s in segs[idx:idx + 1]:
        t0, t1, P_dyn, T_run, launches, p = s
        if t0 <= ts <= t1:
            P, Tnow, p_now = P_dyn, T_run, p
            gap = not any(l0 <= ts <= l1 for l0, l1 in launches)
            break
    if p_now is None:     # idle: the pass whose span holds this time, else the last pass begun
        inside = [q for a0, a1, q in pass_span if a0 <= ts <= a1]
        begun = [q for a0, a1, q in pass_span if a0 <= ts]
        p_now = inside[0] if inside else (begun[-1] if begun else -1)
        Tnow = pass_T[p_now]
    rail_dyn = rail_response(ts)
    Tidle = pass_T[p_now]
    board = IDLE_B + (0.0 if gap else P) + K_T * (Tnow - Tidle) + rng.gauss(0.0, NOISE_B)
    rail = IDLE_R + rail_dyn + RAIL * K_T * (Tnow - Tidle) + rng.gauss(0.0, NOISE_R)
    s = {'t_ms': int(ts * 1000), 'board_w': round(board, 2 if NOISE else 9), 'sp': {'minion_w': [round(rail, 3 if NOISE else 9)],
         'minion_mv': [522 + (rng.choice((-1, 0, 0, 1)) if NOISE else 0)]}, 'mhz': {'minion': 600.0},
         'temp_c': {'minshire': [int(round(Tnow))]}}
    if not NO_PVT:
        s['pvt'] = {'c': [int(round((Tnow + rng.gauss(0.0, 0.3) * NOISE) * 1000 - 57400 + 124700) * 4096 // 249400)
                          for _ in range(34)], 'st': 0, 'f': 0}
    tel.write(json.dumps(s) + '\n')
    ts += dt
tel.close()

# --- what the registered formulas give for the injected values (a check of arithmetic, before the reducer runs) ---
E = {a: energy(a) for a in T}
fJ = lambda pj: pj * 1000.0
z, az = E['add.z'], E['and.z']
fields = [fJ(E['add.a.f%d' % n] - z) / 16 for n in range(4)]
a12 = fJ(E['add.a.f12'] - z) / 32
andf = [fJ(E['and.a.f%d' % n] - az) / 16 for n in (1, 2, 3)]
and12 = (andf[0] + andf[1]) / 2
d12 = a12 - and12
S_cr = P_A * 1000 + P_C * 1000
S_crb = P_R * 1000 + P_C * 1000
inj = {
    'note': 'synthetic test values for the E192 desk check of reduce_intbits.py: NOT a forecast, NOT a measurement',
    'seed': SEED, 'pvt': not NO_PVT, 'passes': PASSES, 'noise': NOISE, 'trise_C_per_W': TRISE, 'E0_pJ': {'%s %s' % k: v for k, v in E0.items()},
    'P_A_fJ': P_A * 1000, 'P_B_fJ': P_B * 1000, 'P_R_fJ': P_R * 1000, 'P_C_fJ': P_C * 1000, 'K_T_W_per_C': K_T,
    'rail_share': RAIL, 'E_arm_pJ': E,
    'expected_ladders_fJ': {
        'hamming_f2_slope_fJ': P_A * 1000 + P_R * 1000, 'hamming_f2_quad_fJ': 0.0,
        'add_f0_fJ_per_bit': fields[0], 'add_f1_fJ_per_bit': fields[1], 'add_f2_fJ_per_bit': fields[2],
        'add_f3_fJ_per_bit': fields[3], 'add_f12_fJ_per_bit': a12,
        'additivity_all_minus_fields_pJ': (E['add.a.all'] - z) - sum(f * 16 / 1000 for f in fields),
        'f12_minus_f1_f2_pJ': (E['add.a.f12'] - z) - (fields[1] + fields[2]) * 16 / 1000,
        'and_f1_fJ_per_bit': andf[0], 'and_f2_fJ_per_bit': andf[1], 'and_f3_fJ_per_bit': andf[2], 'and12_fJ_per_bit': and12,
        'd12_a12_minus_and12_fJ_per_bit': d12, 'add_f2_minus_f3_fJ_per_bit': fields[2] - fields[3],
        'and_f2_minus_f3_fJ_per_bit': andf[1] - andf[2], 'S_cr_fJ_per_position': S_cr, 'S_crb_fJ_per_position': S_crb,
        'S_cr_quad_fJ': 0.0, 'S_crb_quad_fJ': 0.0, 'C1_carry_fJ_per_position': (S_cr + S_crb - a12) / 2,
        'C2_fJ_per_bit': ((S_crb - d12) - (S_cr - and12)) / 2,
        'C3_fJ_per_bit': and12 - ((S_crb - d12) - (S_cr - and12)) / 2,
        'ripple_minus_add_z_pJ': E['add.ripple'] - z},
}
json.dump(inj, open(os.path.join(out, 'injected.json'), 'w'), indent=1, sort_keys=True)
print('synthetic session written: %d runs lines, %d segments, telemetry %.0f s at 10 Hz, pvt %s' % (
    sum(1 for _ in open(os.path.join(out, 'runs.jsonl'))), len(segments), TS1 - TS0, not NO_PVT))
