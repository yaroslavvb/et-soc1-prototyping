#!/usr/bin/env python3
"""E193 desk check of code (registration, before any datum): a synthetic session for the unchanged reducer.

    python3 -I -B synth_session_e193.py <arms.tsv> <OUT> --session A|B [--passes 9] [--realistic] [--seed 7]

Writes OUT/telemetry.jsonl (the sampler's form: t_ms, board_w, sp.{minion,sram,noc}_{w,mv} lists, temp_c.minshire, mhz.minion),
OUT/runs.jsonl (run_x04.py's rows: pass, block, pos, arm, train, rc and the host's X04 fields), OUT/injected.json (what was put
in) and, with --realistic, OUT/pvt.jsonl (t_ms, mean_c). The order and the timing follow run_x04.py's real path: 20 s of idle
first; per run the 5 s gap, a device opening of 1.5 s, 0.4 s launches for 4 s (whole periods, as the host cuts them; the
host's budget rule) or a train's 12 launches, a closing of 0.2 s; 30 s between passes; the arm order drawn with the runner's
own seed rule (random.Random(1113 * 100 + pass * 10 + block index)).

EVERY INJECTED NUMBER IS AN ARBITRARY TEST VALUE: NOT A FORECAST AND NOT A MEASUREMENT. They are linear laws chosen so that
each registered quantity has a known answer: board W over idle per arm (tk over shires 0.05 W a shire; tk over launches
0.02 W per launch a second; duty 0.5 W + 1.0 W x the awake fraction, plus 100 pJ a wake; workers 0.075 W a worker a shire
+ 0.075 W; class instructions 10, 7.5 and 6 pJ an op over spin2 for fadd.ps, fsgnj.s and fadd.s; mask lanes 0.2 W a lane;
train contrasts B - A as listed), the minion rail 0.8 x the board's W over idle, SRAM 0.1 x, NoC 0.05 x.
Exact mode (default): the board reads the input at the sample's instant, the rails are the exact first-order filter (tau
1.05 s) of a piecewise-constant input, read 1.5 meter passes late (0.395 s), the die holds 50 C, the clock reads 600 MHz,
no noise, no dip, every launch ok: the reducer should return the injected values exactly.
Realistic mode (--realistic): the board refreshes once per 0.263 s meter pass with 0.05 W of noise and reads in 10 mW
steps, 1 burst reading in 40 is a dip 6 W low, the rails are sample-and-hold of the filter one pass late with 5 mW of
noise, in 1 mW steps, launches are 2 ms apart within a process, the die follows the power
(0.6 C a watt over idle, a 20 s first-order lag) and reads whole degrees, leakage moves the board (the lab's idle law) and
the minion rail (0.10 W a degree), one run in pass 2 has a failed launch ("ok": false) and one burst in pass 3 has one busy
sample at 700 MHz: the reducer should drop exactly those two runs and return values near the injected ones.
With --subms (exact mode otherwise), the launch edges fall between milliseconds, as a card's do, while the records carry them
rounded to whole milliseconds, as the host stamps them: it shows how far that rounding moves the reduced values.
"""
import argparse
import bisect
import json
import math
import os
import random

ap = argparse.ArgumentParser()
ap.add_argument("arms")
ap.add_argument("out")
ap.add_argument("--session", choices=("A", "B"), required=True)
ap.add_argument("--passes", type=int, default=9)
ap.add_argument("--realistic", action="store_true")
ap.add_argument("--subms", action="store_true", help="launch edges between milliseconds (the host's stamps then round them)")
ap.add_argument("--seed", type=int, default=7)
a = ap.parse_args()
rng = random.Random(a.seed)
os.makedirs(a.out, exist_ok=True)

arms = []
for ln in open(a.arms):
    if ln.strip() and not ln.startswith("#"):
        name, block, opts = ln.rstrip("\n").split("\t")
        arms.append({"arm": name, "block": block, "args": opts.split(), "train": "--then" in opts.split()})
anchor = [x for x in arms if x["block"] == "anchor"][0]
blocks = ["S", "D", "W", "T"] if a.session == "A" else ["C"]


def segments(args):
    """host/main.cpp's parseSegments + run(), the fields this synthetic needs (session defaults first, as the runner does)."""
    parts = [[]]
    for w in ["--window", "240000000"] + args:
        if w == "--then":
            parts.append([])
        else:
            parts[-1].append(w)
    base = dict(arm="spin", cls="none", t1="same", every=1, mask=0xff, shires=0xffffffff, minions=0xfffffffe,
                window=240000000, period=65536, duty=50, cluster=0, seg=0)
    keys = {"--arm": "arm", "--cls": "cls", "--t1": "t1", "--every": "every", "--mask": "mask", "--shires": "shires",
            "--minions": "minions", "--window": "window", "--period": "period", "--duty-pct": "duty",
            "--seg-launches": "seg"}

    def apply(o, ws):
        o = dict(o)
        i = 0
        while i < len(ws):
            if ws[i] == "--cluster":
                o["cluster"] = 1
                i += 1
                continue
            k, v = keys[ws[i]], ws[i + 1]
            o[k] = v if k in ("arm", "cls", "t1") else int(v, 0)
            i += 2
        return o
    b = apply(base, parts[0])
    segs = [b] + [apply(b, p) for p in parts[1:]]
    for o in segs:
        o["window"] = o["window"] // o["period"] * o["period"]
        o["nshires"] = bin(o["shires"] & 0xffffffff).count("1")
        o["workers"] = bin(o["minions"] & 0xfffffffe).count("1")
        o["duty_cycles"] = o["period"] * o["duty"] // 100
    return segs


SPC = 0.39   # slots a hart-cycle in the spin and mix arms (an arbitrary test value)


def records(o, seg):
    """The host's X04 fields for one launch of segment o (ok, before any fault)."""
    cyc = o["window"]
    sh = o["nshires"]
    t0w = 0 if o["arm"] == "tk" else o["workers"] * sh
    t1w = 0 if (o["arm"] == "tk" or o["t1"] == "off") else o["workers"] * sh
    harts = t0w + t1w
    periods = cyc // o["period"]
    duty_waits = o["arm"] == "duty" and o["duty_cycles"] < o["period"]
    waits = o["arm"] == "wait" or duty_waits
    if o["arm"] in ("spin", "mix"):
        slots = SPC * cyc * harts
        spc = SPC
    elif o["arm"] == "duty":
        f = (o["duty_cycles"] / o["period"]) if duty_waits else 1.0
        slots = 0.39 * f * cyc * harts
        spc = 0.39 * f
    elif o["arm"] == "stall":
        slots = 0.02 * cyc * harts
        spc = 0.02
    else:
        slots, spc = 0.0, 0.0
    awake = 0
    if o["arm"] == "duty":
        f = (o["duty_cycles"] / o["period"]) if duty_waits else 1.0
        awake = int(round(f * harts * cyc))
    return {"label": None, "seg": seg, "arm": o["arm"], "cls": o["cls"], "every": o["every"], "cluster": o["cluster"],
            "mask": "0x%x" % (o["mask"] & 0xff), "t1": o["t1"], "duty_pct": o["duty"], "period": o["period"],
            "window": cyc, "shire_mask": "0x%x" % (o["shires"] & 0xffffffff), "minion_mask": "0x%x" % (o["minions"] & 0xfffffffe),
            "shires": sh, "workers_t0": t0w, "workers_t1": t1w, "slots": float(round(slots)),
            "slots_per_cycle_per_hart": spc, "awake_cycles": awake, "credits_taken": periods * harts if waits else 0,
            "credits_drained": 0, "tk_credits_sent": periods * sh if waits else 0, "tk_cycles": cyc,
            "hs_cycles_max": 1043 if waits else 0, "late": 0, "hs_bailouts": 0, "ctr_unsynced": 0,
            "cycles_max": cyc if harts else 0, "cycles_mean": float(cyc) if harts else 0.0, "readers": 4 * sh,
            "retired0": 0, "retired1": 0, "icache_req": 0, "icache_miss": 0, "complete": True, "credits_ok": True, "ok": True}


# ---- the timeline (seconds from an arbitrary epoch), following run_x04.py's real path and the host's launch loop
T0 = 1800000000.0
GAP, OPEN, CLOSE, PASS_GAP, BURST, BUDGET = 5.0, 1.5, 0.2, 30.0, 4.0, 9.5
LGAP = 0.002 if a.realistic else 0.0       # host time between two launches of one process


def edge(x):
    """x on a whole millisecond, and off the samples' 100 ms grid (with --subms: x as it is, between milliseconds)."""
    if a.subms:
        return x
    ms = int(round(x * 1000))
    if ms % 100 == 0:
        ms += 1
    return ms / 1000.0


runs_out, plan = [], []
t = T0 + 20.0
for p in range(a.passes):
    for bi, b in enumerate(blocks):
        items = [x for x in arms if x["block"] == b]
        random.Random(1113 * 100 + p * 10 + bi).shuffle(items)
        seq = [anchor] + items + ([anchor] if bi == len(blocks) - 1 else [])
        for k, x in enumerate(seq):
            t += GAP
            t_open = t
            t += OPEN
            segs = segments(x["args"])
            launches = []
            # every launch edge on a whole millisecond: the host stamps t_start_ms and t_end_ms in whole ms, and the
            # power here changes at those stamps, so the reducer reads the same edges the input has; an edge that would
            # fall on a sample's instant (a multiple of 100 ms) moves 1 ms later, so no sample sits on an edge
            if x["train"]:
                for s_i, o in enumerate(segs):
                    for _ in range(segs[0]["seg"]):
                        L = o["window"] / 6.0e8
                        l0 = edge(t)
                        l1 = edge(l0 + L)
                        launches.append((s_i, o, l0, l1))
                        t = l1 + LGAP
            else:
                o = segs[0]
                L = o["window"] / 6.0e8
                t_start = t
                while (t - t_start) < BURST and (t - t_open) + L + math.ceil(L + 1.0) < BUDGET:
                    l0 = edge(t)
                    l1 = edge(l0 + L)
                    launches.append((-1, o, l0, l1))
                    t = l1 + LGAP
            t += CLOSE
            plan.append({"pass": p, "block": b, "pos": k, "x": x, "launches": launches})
    if p < a.passes - 1:
        t += PASS_GAP
t_end = t + GAP + 3.0

# ---- the truth (ARBITRARY TEST VALUES)
LPS = {}
for r in plan:
    if not r["x"]["train"]:
        lo, hi = r["launches"][0][2], r["launches"][-1][3]
        LPS.setdefault(r["x"]["arm"], len(r["launches"]) / (hi - lo))
WMC = {}     # worker minion-cycles a second, as the reducer computes it
for r in plan:
    if not r["x"]["train"]:
        lo, hi = r["launches"][0][2], r["launches"][-1][3]
        rec = records(r["launches"][0][1], -1)
        WMC.setdefault(r["x"]["arm"], rec["workers_t0"] * rec["cycles_mean"] * len(r["launches"]) / (hi - lo))
SPIN2 = 2.400
EOP = {"fadd_ps": 10.0e-12, "fsgnj_s": 7.5e-12, "fadd_s": 6.0e-12}
CONTRAST = {"tr_tk_spin1": 0.300, "tr_spin1_spin2": 0.200, "tr_tk_stall2": 0.700, "tr_faddps_fadds": -0.400,
            "tr_packed_spread": 0.050, "tr_spread_cluster": -0.020}
TRAIN_A = 1.000


def board_w(name, o):
    """W over idle on the board for a non-train arm (ARBITRARY TEST VALUES)."""
    if name == "spin2":
        return SPIN2
    if name.startswith("tk_s") or name == "tk":
        return 0.05 * o["nshires"]
    if name in ("tk_l100", "tk_l200"):
        return 1.60 + 0.02 * (LPS[name] - LPS["tk"])
    if o["arm"] in ("wait", "duty"):
        rec = records(o, -1)
        f = 0.0 if o["arm"] == "wait" else rec["awake_cycles"] / (rec["cycles_mean"] * (rec["workers_t0"] + rec["workers_t1"]))
        w = 0.5 + 1.0 * f
        if name in ("duty33f", "duty33k"):
            first = [r for r in plan if r["x"]["arm"] == name][0]
            lo, hi = first["launches"][0][2], first["launches"][-1][3]
            w += 100.0e-12 * rec["credits_taken"] * len(first["launches"]) / (hi - lo)     # 100 pJ a wake
        return w
    if name in ("w7", "w15", "w23"):
        return 0.075 * o["workers"] + 0.075
    if o["arm"] == "mix":
        if name.startswith("faddpsm"):
            lanes = bin(o["mask"] & 0xff).count("1")
            return board_w("faddps_p1", o) - 0.2 * (8 - lanes)
        ops = SPC * 2 * WMC[name if name in WMC else "spin2"] / o["every"]
        return SPIN2 + EOP[o["cls"]] * ops
    raise KeyError(name)


inj = {"note": "ARBITRARY TEST VALUES: not a forecast and not a measurement", "session": a.session,
       "realistic": a.realistic, "subms": a.subms, "arms": {}, "trains": {},
       "rail_factor": {"minion_w": 0.8, "sram_w": 0.1, "noc_w": 0.05},
       "laws": {"tk_shires_slope_w": 0.05, "tk_shires_intercept_w": 0.0, "tk_launches_slope_w": 0.02,
                "duty_slope_w": 1.0, "duty_intercept_w": 0.5, "pj_per_wake": 100.0, "workers_slope_w": 0.075,
                "workers_intercept_w": 0.075, "per_op_pj": {"faddps": 10.0, "fsgnjs": 7.5, "fadds": 6.0},
                "mask_slope_w": 0.2}}
for x in arms:
    if x["block"] in blocks or x["block"] == "anchor":
        if x["train"]:
            inj["trains"][x["arm"]] = {"A_w": TRAIN_A, "B_w": TRAIN_A + CONTRAST[x["arm"]], "contrast_board_w": CONTRAST[x["arm"]]}
        else:
            inj["arms"][x["arm"]] = {"board_w": board_w(x["arm"], segments(x["args"])[0])}
inj["laws"]["mask_intercept_w"] = inj["arms"].get("faddps_p1", {}).get("board_w", 0) - 0.2 * 8 if a.session == "B" else None
inj["lps"] = LPS
inj["wmc"] = WMC

# ---- power as a function of time
ivals = []      # (lo, hi, board W over idle, list of launch intervals) per burst segment
for r in plan:
    x = r["x"]
    if x["train"]:
        for s_i in range(4):
            ls = [l for l in r["launches"] if l[0] == s_i]
            w = TRAIN_A if s_i in (0, 3) else TRAIN_A + CONTRAST[x["arm"]]
            ivals.append((ls[0][2], ls[-1][3], w, [(l[2], l[3]) for l in ls]))
    else:
        w = inj["arms"][x["arm"]]["board_w"]
        ls = r["launches"]
        ivals.append((ls[0][2], ls[-1][3], w, [(l[2], l[3]) for l in ls]))
ivals.sort()
STARTS = [v[0] for v in ivals]


def over_at(tt, launches_only=True):
    """Input W over idle at time tt: the board's follows each launch (gaps between launches read idle); the rails' input
    is constant over the whole burst segment (launches_only=False)."""
    i = bisect.bisect_right(STARTS, tt) - 1
    if i < 0:
        return 0.0
    lo, hi, w, ls = ivals[i]
    if not (lo <= tt < hi):
        return 0.0
    if not launches_only:
        return w
    for l0, l1 in ls:
        if l0 <= tt < l1:
            return w
    return 0.0


TAU, LAG, PASS = 1.05, 1.5 * 0.263, 0.263
IDLE_W, IDLE_T = 23.5, 50.0
RAIL_IDLE = {"minion_w": 6.7, "sram_w": 1.9, "noc_w": 2.06}
MV = {"minion_mv": 523, "sram_mv": 698, "noc_mv": 484}
RF = inj["rail_factor"]


def leak(T):
    return 23.257 * math.exp((T - 80.0) / 36.0)


def rails_exact(queries):
    """Exact mode: the rails' first-order filter (tau) of the piecewise-constant input, evaluated exactly at each query
    time (event-driven: the input changes only at a burst segment's edges)."""
    edges = sorted({v[0] for v in ivals} | {v[1] for v in ivals})
    out = {}
    y_ = {k: RAIL_IDLE[k] for k in RAIL_IDLE}
    tcur = T0 - 60.0
    ei = 0
    for q in sorted(set(queries)):
        while True:
            nxt = edges[ei] if ei < len(edges) else float("inf")
            stop = min(nxt, q)
            w_in = over_at(0.5 * (tcur + stop), launches_only=False) if stop > tcur else 0.0
            for k in y_:
                lvl = RAIL_IDLE[k] + RF[k] * w_in
                y_[k] = lvl + (y_[k] - lvl) * math.exp(-(stop - tcur) / TAU)
            tcur = stop
            if nxt <= q:
                ei += 1
                continue
            break
        out[q] = dict(y_)
    return out


# realistic mode: the rails' filter and the die on a fine grid (10 ms steps; the die moves the rails' leakage)
dt = 0.01
grid_y, grid_T = [], []
if a.realistic:
    n = int((t_end - T0) / dt) + 1
    y = {k: RAIL_IDLE[k] for k in RAIL_IDLE}
    Tdie = IDLE_T
    for i in range(n):
        tt = T0 + i * dt
        grid_y.append(dict(y))
        grid_T.append(Tdie)
        w_in = over_at(tt + dt / 2, launches_only=False)
        for k in y:
            lvl = RAIL_IDLE[k] + RF[k] * w_in + (0.10 if k == "minion_w" else 0.0) * (Tdie - IDLE_T)
            y[k] = lvl + (y[k] - lvl) * math.exp(-dt / TAU)
        Tt_target = IDLE_T + 0.6 * w_in
        Tdie = Tt_target + (Tdie - Tt_target) * math.exp(-dt / 20.0)


def at(grid, tt):
    i = int(round((tt - T0) / dt))
    return grid[max(0, min(i, len(grid) - 1))]


# ---- faults (realistic): one failed launch in pass 2, one 700 MHz busy sample in pass 3
fault_dev = fault_clk = None
if a.realistic:
    cand2 = [r for r in plan if r["pass"] == 2 and not r["x"]["train"] and r["x"]["arm"] != "spin2"]
    cand3 = [r for r in plan if r["pass"] == 3 and not r["x"]["train"] and r["x"]["arm"] != "spin2"]
    fault_dev, fault_clk = cand2[0], cand3[0]
    inj["faults"] = {"device": [fault_dev["pass"], fault_dev["block"], fault_dev["pos"], fault_dev["x"]["arm"]],
                     "clock": [fault_clk["pass"], fault_clk["block"], fault_clk["pos"], fault_clk["x"]["arm"]]}

# ---- the sampler's lines at 10 Hz
tel = open(os.path.join(a.out, "telemetry.jsonl"), "w")
pvt = open(os.path.join(a.out, "pvt.jsonl"), "w") if a.realistic else None
clk_t = None
if fault_clk is not None:
    lo, hi = fault_clk["launches"][0][2], fault_clk["launches"][-1][3]
    clk_t = round(lo + 0.5 * (hi - lo), 1)
tt = T0
held_board, last_pass = IDLE_W, -1
EX = {}
if not a.realistic:
    qs, q = [], T0
    while q <= t_end:
        qs.append(round(q - LAG, 6))
        q = round(q + 0.1, 3)
    EX = rails_exact(qs)
while tt <= t_end:
    T_true = at(grid_T, tt) if a.realistic else IDLE_T
    if a.realistic:
        pidx = int((tt - T0) / PASS)
        if pidx != last_pass:          # the meter refreshes once a pass and holds
            last_pass = pidx
            ts = T0 + pidx * PASS
            b = IDLE_W + leak(at(grid_T, ts)) - leak(IDLE_T) + over_at(ts) + rng.gauss(0, 0.05)
            if over_at(ts) > 0 and rng.random() < 1.0 / 40:
                b -= 6.0
            held_board = b
            yy = at(grid_y, ts - PASS)    # one pass late
            held_rail = {k: yy[k] + rng.gauss(0, 0.005) for k in yy}
        board = held_board
        rails = held_rail
    else:
        board = IDLE_W + over_at(tt)
        rails = EX[round(tt - LAG, 6)]
    mhz = 700 if (clk_t is not None and abs(tt - clk_t) < 0.05) else 600
    # exact mode writes full precision; realistic mode the meters' steps (board 10 mW, rails 1 mW)
    qb, qr = (lambda v: round(v, 2), lambda v: round(v, 3)) if a.realistic else (lambda v: v, lambda v: v)
    s = {"t_ms": int(round(tt * 1000)), "took_ms": 21, "board_w": qb(board),
         "sp": {"minion_w": [qr(rails["minion_w"])], "sram_w": [qr(rails["sram_w"])],
                "noc_w": [qr(rails["noc_w"])], "minion_mv": [MV["minion_mv"]], "sram_mv": [MV["sram_mv"]],
                "noc_mv": [MV["noc_mv"]]},
         "temp_c": {"minshire": [int(T_true) if a.realistic else int(IDLE_T)]}, "mhz": {"minion": mhz, "noc": 400}}
    tel.write(json.dumps(s) + "\n")
    if pvt is not None and abs(tt * 10 - round(tt * 10)) < 1e-6 and int(round(tt * 10)) % 10 == 0:
        pvt.write(json.dumps({"t_ms": int(round(tt * 1000)), "mean_c": round(T_true + 0.5, 3)}) + "\n")
    tt = round(tt + 0.1, 3)
tel.close()
if pvt is not None:
    pvt.close()

# ---- runs.jsonl, as run_x04.py writes it
with open(os.path.join(a.out, "runs.jsonl"), "w") as f:
    for r in plan:
        for (s_i, o, l0, l1) in r["launches"]:
            rec = records(o, s_i)
            rec["label"] = r["x"]["arm"]
            rec["wall_s"] = round(l1 - l0, 4)
            rec["t_start_ms"] = int(round(l0 * 1000))
            rec["t_end_ms"] = int(round(l1 * 1000))
            rc = 0
            if r is fault_dev:
                rc = 3                          # the host exits 3 after an incomplete launch (here its last one)
                if l0 == r["launches"][-1][2]:
                    rec["complete"], rec["ok"] = False, False
            row = {"host": "synthetic", "pass": r["pass"], "block": r["block"], "pos": r["pos"], "arm": r["x"]["arm"],
                   "train": r["x"]["train"], "rc": rc}
            row.update(rec)      # the host's fields after the runner's own, as run_x04.py does ("arm" becomes the host's)
            f.write(json.dumps(row) + "\n")
json.dump(inj, open(os.path.join(a.out, "injected.json"), "w"), indent=1)
print("session %s: %d passes, %d runs, %d launches, %.1f minutes of telemetry; injected values: ARBITRARY TEST VALUES" % (
    a.session, a.passes, len(plan), sum(len(r["launches"]) for r in plan), (t_end - T0) / 60))
