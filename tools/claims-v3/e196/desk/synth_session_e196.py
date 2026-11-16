#!/usr/bin/env python3
"""E196 (Q185, lane reg-e196): a small synthetic session in the reference session's layout, for a desk check of the reduction.

    /usr/bin/python3 -I -B synth_session_e196.py GEN OUT [--passes 5] [--noise 0.0] [--seed 1] [--pass-host x14|lab]
                                                  [--fault-launch] [--fault-readback] [--dips N] [--drop F.Ae,Z.b50,I.H.mFFFF]
                                                  [--no-tail]

GEN holds make_x14.py's arms.json; OUT gets what run_block.py writes (telemetry.jsonl, runs.jsonl, train.jsonl, checks.jsonl,
marks.jsonl) and OUT/gen/arms.json (a copy), plus OUT/injected.json: the values put in. Standard library only; it opens nothing.

THE VALUES PUT IN ARE ARBITRARY TEST VALUES, chosen only to exercise the code: not a forecast, not a measurement, and not
derived from any forecast. Each pass arm has a board level S (W over a 25.000 W idle) from a simple rule (a floor, a step per
issued row by tile, a data term per tile; see arm_level()); the two trains have a fixed F - S difference; the die reading is
held at 58 C, so every leakage term is zero; the minion rail carries 0.8 of the board's step through a first-order filter
(tau 1.05 s) read 0.26 s late, as the reducer models it.

Timing follows run_block.py: per run, a 1.5 s pause, an approach (a heater burst of 3 s at +26 W, then idle), at least 2 s
quiet, then one device process: a calibration launch (launch -1) of 20,000 ops a minion, then 0.5 s launches for 4 s. The
board's input holds each launch's level through the short gap after it and the last launch's level 5 ms past its end (the
real meter lags far more), so a 10 Hz sample stamped within a launch's millisecond rounding reads that launch. A pass: 10 s idle, two
burn-in anchors, the anchor, the pass arms in run_block.py's own order for the host name 'aifoundry3' ("hostname|pass"), the
anchor, 10 s idle. A train block (passes 101 and 102): 10 s idle, the anchor, 24 processes of a calibration launch and 13
launches (SFFS, FSSF, ...), the anchor, 10 s idle. The smoke (pass -1) is written too (the reducer skips it).

--pass-host x14: every pass run is the request's host: two read-backs of C each (checks.jsonl), as the reference session.
--pass-host lab: every pass run and every train-block anchor is the lab's unchanged sparsity host: no read-back of C, and each
  launch record carries "readback": "none" (E196's registered marking); the train processes stay the request's host (with
  their read-backs). The telemetry and every launch are the same bytes in both modes for the same seed.
"""
import argparse
import json
import math
import os
import random

IDLE = 25.0
T_DIE = 58.0
RAIL_FRAC, TAU, DELAY = 0.8, 1.05, 0.26
HZ = 10
CAL_OPS = 20000


def arm_level(arm):
    """An arbitrary test level (W over idle) for a pass arm: a floor, a per-row step by tile, a data term by tile."""
    t, m = arm["tile"], arm["row_mask"]
    rows = 16 if m is None else bin(int(m, 16)).count("1")
    base = {"lab:zeros": (0.40, 0.10, 0.00), "h.bin": (0.40, 0.60, 0.00), "lab:randn": (0.85, 0.60, 0.80),
            "lab:a_zeros_b_randn": (0.62, 0.11, 0.00), "lab:ones": (0.40, 0.62, 0.00), "lab:sparse50": (0.85, 0.30, 0.25),
            "builtin:pi": (0.40, 0.64, 0.00), "za50.bin": (0.85, 0.35, 0.30), "zb50.bin": (0.85, 0.36, 0.28),
            "fb0.bin": (0.40, 0.61, 0.00), "fbs.bin": (0.40, 0.61, 0.02), "fbe.bin": (0.40, 0.61, 0.10),
            "fa0.bin": (0.40, 0.61, 0.00), "fae.bin": (0.40, 0.61, 0.05)}[t]
    floor, per_row, data = base
    extra = 0.0
    if arm["name"] == "I.H.mFFFF":
        extra = 0.013          # the MSK bit alone (a test value)
    if arm["name"] in ("I.H.m5555", "I.H.m3333", "I.H.m0F0F"):
        extra = {"I.H.m5555": 0.031, "I.H.m3333": 0.017, "I.H.m0F0F": 0.007}[arm["name"]]
    return round(floor + per_row * rows + data * rows + extra, 6)


def cycles_per_op(arm):
    m = arm["row_mask"]
    return 546.0 if m is None or int(m, 16) == 0xFFFF else 544.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gen")
    ap.add_argument("out")
    ap.add_argument("--passes", type=int, default=5)
    ap.add_argument("--noise", type=float, default=0.0, help="board noise sd per sample, W (0: exact)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--pass-host", choices=("x14", "lab"), default="x14")
    ap.add_argument("--fault-launch", action="store_true", help="pass 1's I.R.full: launch 2 not ok")
    ap.add_argument("--fault-readback", action="store_true", help="pass 2's I.H.m00FF: a read-back not ok (x14 pass host only)")
    ap.add_argument("--dips", type=int, default=0, help="inject this many 6 W single-sample board dips inside pass windows")
    ap.add_argument("--drop", default="", help="pass arms left out of every pass (the cut order)")
    ap.add_argument("--no-tail", action="store_true", help="the board drops to idle exactly at the last launch's end (shows the\n"
                    "                    readers' millisecond edge: a sample stamped within the end's rounding is counted in that launch)")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    manifest = json.load(open(os.path.join(a.gen, "arms.json")))
    table = {x["name"]: x for x in manifest["arms"]}
    trains = {t["name"]: t for t in manifest["trains"]}
    os.makedirs(os.path.join(a.out, "gen"), exist_ok=True)
    json.dump(manifest, open(os.path.join(a.out, "gen", "arms.json"), "w"), indent=1, sort_keys=True)
    drop = [x for x in a.drop.split(",") if x]
    D_TRAIN = {"T1": 0.0300, "T2": -0.0200}       # arbitrary test values (F - S, W)
    segs = []          # (t0, t1, level over idle) of the board's input, in time order
    runs, trecs, checks, marks = [], [], [], []
    t = [1_800_000_000.0]
    host = "aifoundry3"

    def idle(sec, p, label):
        t0 = t[0]
        t[0] += sec
        marks.append({"kind": "idle", "host": host, "pass": p, "t0_ms": int(t0 * 1000), "t1_ms": int(t[0] * 1000), "label": label})

    def approach():
        t[0] += 1.5                           # the runner's own pause before the first heater launch
        h0 = t[0]
        segs.append((h0, h0 + 3.0, 26.0))     # the heater
        t[0] = h0 + 3.0 + 2.5                 # back to the launch reading, then quiet
        return {"start_c": T_DIE, "start_hot_c": 59.0, "heats": 1, "heater_fails": 0, "preheat_c": 59.0, "target_c": 58.0,
                "wait_s": 5.5, "quiet_s": 2.5, "timed_out": False, "on_protocol": True}

    def launches(level_of, cpo_of, n_launch, first_kind_seq=None):
        """a device process: the calibration launch then n launches; level_of(n) the board level of launch n. The board's
        input holds each launch's level through the short gap after it (4 ms after the calibration launch, 2 ms between
        launches), so a 10 Hz sample never lands on an unmetered gap: launch-gap dips are injected only by --dips."""
        out = []
        t[0] += 1.2                           # the process's device setup (no load)
        seq_n = [-1] + list(range(n_launch))
        for i, n in enumerate(seq_n):
            cpo = cpo_of(n)
            if n < 0:
                iters, wall = CAL_OPS, CAL_OPS * cpo / 600e6
            else:
                iters = int(0.5 * 600e6 / cpo)
                wall = iters * cpo / 600e6
            t0 = t[0]
            t1 = t0 + wall
            gap = 0.0 if i == len(seq_n) - 1 else (0.004 if n < 0 else 0.002)  # the read-back after launch -1, else the launch gap
            tail = 0.005 if i == len(seq_n) - 1 and not a.no_tail else 0.0   # the meter holds the last launch's level 5 ms past its end
            segs.append((t0, t1 + gap + tail, level_of(n)))
            out.append({"launch": n, "iters": iters, "ops": iters * 1024, "cycles_per_op": cpo, "cycles_mean": cpo * iters,
                        "cycles_max": int(cpo * iters), "wall_s": round(wall, 6), "t_start_ms": int(round(t0 * 1000)),
                        "t_end_ms": int(round(t1 * 1000)), "ghz": 0.6, "tensor_errors": 0, "ok": True})
            t[0] = t1 + gap
        t[0] += 0.3                           # process exit
        return out

    def run(arm, role, p, seq, lab_host):
        ap_ = approach()
        lvl = arm_level(table[arm])
        recs = launches(lambda n: lvl, lambda n: cycles_per_op(table[arm]), 8)
        for r in recs:
            r.update({"label": arm, "values": table[arm]["tile"], "row_mask": table[arm]["row_mask"] or "none", "kind": "-",
                      "abba": "", "minions": 1024, "shire_mask": "0xffffffff", "arm": arm, "host": host, "pass": p, "seq": seq,
                      "role": role, "approach": ap_, "rc": 0})
            if lab_host:
                r["readback"] = "none"
            if a.fault_launch and p == 1 and arm == "I.R.full" and r["launch"] == 2:
                r["ok"] = False
        runs.extend(recs)
        if not lab_host:
            for k in (-1, recs[-1]["launch"]):
                ok = not (a.fault_readback and p == 2 and arm == "I.H.m00FF" and k >= 0)
                checks.append({"label": arm, "kind": "-", "after_launch": k, "zero_rows": table[arm]["zero_rows"] or "none",
                               "live_rows": table[arm]["live_rows"] or "none", "zero_rows_bad": 0 if ok else 3,
                               "live_rows_zero": 0, "ok": ok, "arm": arm, "host": host, "pass": p, "seq": seq, "role": role})
        return lvl

    def train(name, p, seq, nproc):
        tr = trains[name]
        F, S = tr["F"], tr["S"]
        sF = arm_level(table[S]) + D_TRAIN[name]
        sS = arm_level(table[S])
        for k in range(nproc):
            order = "SFFS" if k % 2 == 0 else "FSSF"
            drift = 0.004 * (k % 3)           # a slow drift inside each process (W a launch)
            kind = lambda n: order[0] if n < 1 else order[(n - 1) % 4]
            recs = launches(lambda n: (sF if kind(n) == "F" else sS) + drift * (n + 1),
                            lambda n: 544.0, tr["launches"])
            for r in recs:
                kk = kind(r["launch"])
                arm = F if kk == "F" else S
                r.update({"label": arm, "values": table[arm]["tile"], "row_mask": table[arm]["row_mask"], "kind": kk,
                          "abba": order, "minions": 1024, "shire_mask": "0xffffffff", "train": name, "process": k,
                          "order": order, "host": host, "pass": p, "seq": seq, "role": "train", "rc": 0})
            trecs.extend(recs)
            for la in (-1, recs[-1]["launch"]):
                kk = kind(la)
                arm = F if kk == "F" else S
                checks.append({"label": arm, "kind": kk, "after_launch": la, "zero_rows": "0xFFFF", "live_rows": "none",
                               "zero_rows_bad": 0, "live_rows_zero": -1, "ok": True, "train": name, "process": k,
                               "order": order, "host": host, "pass": p, "seq": seq, "role": "train"})
            t[0] += 0.05

    # the smoke (never reduced)
    idle(10, -1, "before")
    for s, arm in enumerate(["I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"]):
        run(arm, "smoke", -1, s, False)
    idle(10, -1, "after")
    t[0] += 30
    # the trains, then the passes (run_session.sh's order)
    for i, name in enumerate(("T1", "T2")):
        p = 101 + i
        idle(10, p, "before")
        run("K.pi", "train_anchor_first", p, 0, a.pass_host == "lab")
        train(name, p, 1, trains[name]["processes"])
        run("K.pi", "train_anchor_last", p, 2, a.pass_host == "lab")
        idle(10, p, "after")
        t[0] += 30
    injected = {"note": "arbitrary test values: not a forecast, not a measurement", "idle_W": IDLE, "die_C": T_DIE,
                "S_W": {}, "trains_D_W": D_TRAIN, "passes": a.passes, "pass_host": a.pass_host, "dropped": drop}
    pass_arms = [x for x in table if x != "K.pi" and table[x].get("in_passes", True) and x not in drop]
    for p in range(a.passes):
        arms = list(pass_arms)
        random.Random("%s|%d" % (host, p)).shuffle(arms)
        marks.append({"kind": "plan", "host": host, "pass": p, "t_ms": int(t[0] * 1000), "anchor": "K.pi", "arms": arms,
                      "dropped": drop})
        idle(10, p, "before")
        seq = 0
        for _ in range(2):
            run("K.pi", "burnin", p, seq, a.pass_host == "lab"); seq += 1
        run("K.pi", "anchor_first", p, seq, a.pass_host == "lab"); seq += 1
        for arm in arms:
            injected["S_W"][arm] = run(arm, "arm", p, seq, a.pass_host == "lab"); seq += 1
        run("K.pi", "anchor_last", p, seq, a.pass_host == "lab"); seq += 1
        idle(10, p, "after")
        t[0] += 30
    injected["S_W"]["K.pi"] = arm_level(table["K.pi"])
    t_end = t[0] + 5
    # the telemetry: 10 Hz, board = idle + the input level; the rail = 0.8 x the input step through tau, read DELAY late
    segs.sort()
    t0 = 1_800_000_000.0 - 20
    n = int((t_end - t0) * HZ)
    j = 0
    rail_state = 0.0
    dt = 1.0 / HZ
    level_at = []
    for i in range(n):
        tt = t0 + i * dt
        while j < len(segs) and segs[j][1] <= tt:
            j += 1
        lvl = segs[j][2] if j < len(segs) and segs[j][0] <= tt < segs[j][1] else 0.0
        level_at.append(lvl)
    # the rail filter on a fine grid (exact first order, 1 ms steps), then sampled DELAY late
    tel = []
    dip_at = set()
    if a.dips:
        cand = [i for i in range(n) if level_at[i] > 0 and level_at[i - 1] > 0 and level_at[i + 1] > 0
                and i % 37 == 5][: a.dips]
        dip_at = set(cand)
    fine = 0.001
    decay = 1 - math.exp(-fine / TAU)
    ft = t0 - 1.0
    js = 0
    rail_samples = {}
    target_times = [t0 + i * dt - DELAY for i in range(n)]
    for i in range(n):
        tt = target_times[i]
        while ft < tt:
            while js < len(segs) and segs[js][1] <= ft:
                js += 1
            lv = segs[js][2] if js < len(segs) and segs[js][0] <= ft < segs[js][1] else 0.0
            rail_state += (RAIL_FRAC * lv - rail_state) * decay
            ft += fine
        rail_samples[i] = rail_state
    for i in range(n):
        tt = t0 + i * dt
        bw = IDLE + level_at[i] + (rng.gauss(0, a.noise) if a.noise > 0 else 0.0)
        if i in dip_at:
            bw -= 6.0
        tel.append({"t_ms": int(round(tt * 1000)), "board_w": round(bw, 6), "temp_c": {"minshire": [T_DIE]},
                    "mhz": {"minion": 600}, "sp": {"minion_w": [round(8.0 + rail_samples[i], 6)], "minion_mv": [522]}})
    injected["dips_injected"] = len(dip_at)

    def dump(name, rows):
        with open(os.path.join(a.out, name), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    dump("telemetry.jsonl", tel)
    dump("runs.jsonl", runs)
    dump("train.jsonl", trecs)
    dump("checks.jsonl", checks)
    dump("marks.jsonl", marks)
    json.dump(injected, open(os.path.join(a.out, "injected.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps({"samples": len(tel), "pass_launches": len(runs), "train_launches": len(trecs), "checks": len(checks),
                      "passes": a.passes, "pass_host": a.pass_host, "dips": len(dip_at)}))


if __name__ == "__main__":
    main()
