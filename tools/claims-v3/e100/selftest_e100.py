#!/usr/bin/env python3
"""E100: the scorer's self-test, no card. Two synthetic sessions, laid out as run_hpl.py writes them, from the prediction model of make_predictions_e100.py:

  CHAIN   heartbeats read the kernel slot, as the chain says: D1, D2, D3 and D4 must read PASS (D5 is reported).
  RANDOM  falls come at the same mean rate as A0's whatever the gap, at random times inside kernels too: D1 must FAIL, D2 must FAIL, D3 must FAIL.

    python3 selftest_e100.py <scratch dir>        exit 0 when every expectation holds
"""
import json
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_predictions_e100 as M

PROTO = json.load(open(os.path.join(HERE, "protocol.json")))
EPOCH = 1793522100000.0


def clock_at(trans, t):
    c = trans[0][1]
    for tt, m in trans:
        if tt <= t:
            c = m
        else:
            break
    return c


def session(out, mode, seed):
    rng = random.Random(seed)
    os.makedirs(os.path.join(out, "tel"), exist_ok=True)
    runs_f = open(os.path.join(out, "runs.jsonl"), "w")
    launch_f = open(os.path.join(out, "launches.jsonl"), "w")
    t = EPOCH
    phi = EPOCH + 123.4
    q = M.Q_MS + 0.0003
    for b in PROTO["blocks"]:
        if not b["name"].startswith("R"):
            continue
        cfg = b["runs"][0]
        la = cfg["launch"]
        for rep in range(1, b.get("passes", 1) + 1):
            name = f"{b['name']}-00-{cfg['label']}-r{rep}"
            tel_rows = []
            t0_run = t
            t += 1500.0
            clock, busy = 600, False
            prev_end = None
            sim = []
            for pi in range(la["processes"]):
                if pi:
                    t += rng.uniform(0, 1000.0)
                if la.get("one_kernel_iters"):
                    p = M.sim_process(rng, t, phi if mode == "chain" else rng.uniform(0, 1000), 0.0, 2.0, one_kernel=True, clock0=clock, sp_busy0=busy, q=q)
                else:
                    p = M.sim_process(rng, t, phi if mode == "chain" else rng.uniform(0, 1000) + t, la.get("gap_ms", 0.0) if mode == "chain" else 0.0, 2.0, clock0=clock, sp_busy0=busy, q=q)
                if mode != "chain":
                    # the gap is still taken, in the launch log only, so the arms look alike to the scorer's bookkeeping
                    pass
                sim.append(p)
                clock, busy = p["clock"], p["sp_busy"]
                # the gap to the next process: a heartbeat there reads idle and the clock falls, as the chain says
                gap_end = p["t1"] + 197.0
                k = math.ceil((p["t1"] - phi) / q)
                if phi + q * k < gap_end and pi + 1 < la["processes"]:
                    if busy and clock > 600:
                        p["trans"].append((phi + q * k, 600))
                    clock, busy = 600, False
                recs = []
                for j, (s, e, cyc) in enumerate(p["kernels"]):
                    wall = (e - s) / 1000.0
                    recs.append({"launch": j - 1, "cycles_max": cyc, "wall_s": wall, "t_start_ms": int(s), "t_end_ms": int(e), "ghz": cyc / wall / 1e9})
                launch_f.write(json.dumps({"run": name, "role": "work", "proc": pi, "rc": 0, "t_start_ms": int(p["t0"]), "t_end_ms": int(p["t1"]), "sparsity": recs}) + "\n")
                t = p["t1"] + 197.0
            t_end = t + 2000.0
            trans = [x for p in sim for x in p["trans"]]
            trans.sort()
            ts = t0_run
            while ts < t_end:
                c = clock_at(trans, ts) if trans else 600
                tel_rows.append(json.dumps({"t_ms": int(ts), "board_w": 35.0, "temp_c": {"minshire": [58, 50, 60]}, "mhz": {"minion": c}}))
                ts += 100.0
            open(os.path.join(out, "tel", name + ".jsonl"), "w").write("\n".join(tel_rows) + "\n")
            runs_f.write(json.dumps({"run": name, "block": b["name"]}) + "\n")
            t = t_end + 3000.0
    runs_f.close()
    launch_f.close()


def score(out):
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e100.py"), out, "--out", os.path.join(out, "results.json")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("the scorer failed")
    print(r.stdout[:1800])
    return json.load(open(os.path.join(out, "results.json")))


def inject_random(out):
    """RANDOM: every arm gets falls at A20's mean rate inside kernels, regardless of its gap: rewrite the telemetry's clock."""
    rng = random.Random(7)
    for f in os.listdir(os.path.join(out, "tel")):
        p = os.path.join(out, "tel", f)
        rows = [json.loads(x) for x in open(p)]
        for r in rows:
            r["mhz"]["minion"] = 800
        i = 30
        while i < len(rows) - 20:
            if rng.random() < 0.0053:
                for j in range(i, min(i + 11, len(rows))):
                    rows[j]["mhz"]["minion"] = 600
                i += 13
            i += 1
        open(p, "w").write("\n".join(json.dumps(x) for x in rows) + "\n")


def main():
    base = sys.argv[1]
    a = os.path.join(base, "chain")
    b = os.path.join(base, "random")
    for d in (a, b):
        os.makedirs(d, exist_ok=True)
    session(a, "chain", 11)
    R = score(a)["rules"]
    session(b, "chain", 12)
    inject_random(b)
    Q = score(b)["rules"]
    want = [("CHAIN D1", R["D1"]["verdict"], "PASS"), ("CHAIN D2", R["D2"]["verdict"], "PASS"), ("CHAIN D3", R["D3"]["verdict"], "PASS"), ("CHAIN D4", R["D4"]["verdict"], "PASS"),
            ("RANDOM D1", Q["D1"]["verdict"], "FAIL"), ("RANDOM D2", Q["D2"]["verdict"], "FAIL"), ("RANDOM D3", Q["D3"]["verdict"], "FAIL")]
    bad = 0
    for name, got, exp in want:
        print(f"{name}: {got} (want {exp})")
        bad += got != exp
    print("CHAIN D3:", {k: R["D3"][k] for k in ("table_tp_fn_fp_tn", "sensitivity", "specificity", "lattice_round1", "lattice_round2")}, "; D4:", R["D4"], "; D5:", R["D5"]["verdict"])
    print("selftest", "ok" if not bad else f"FAILED {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
