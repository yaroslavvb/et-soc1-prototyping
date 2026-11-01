#!/usr/bin/env python3
"""E98 (Q132): the scorer's self-test, no card. (1) The verdict functions on hand-made intervals, every branch. (2) A synthetic night written in the
runner's own file shapes, with planted slopes and no noise: the reducer must recover them to the rounding, read the gates, leave out a probe whose
rest was broken, flag a planted idle dip, and call the verdicts. (3) The same night with the rest die flat: UNDER-RESOLVED.

    python3 selftest_e98.py > selftest.txt
"""
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e98 as X  # noqa: E402

PRED = json.load(open(os.path.join(HERE, "predictions.json")))
K, WPC = PRED["constants"]["k_line_c_per_w"], PRED["constants"]["rest_w_per_c"]
fails = []


def check(name, got, want, tol=None):
    ok = (abs(got - want) <= tol) if tol is not None else (got == want)
    print(("ok  " if ok else "FAIL"), name, "got", got, "want", want)
    if not ok:
        fails.append(name)


# ---- 1. the verdict partition
for (lo, hi), want in {(0.05, 0.45): "SUPPORTS", (-0.1, 0.5): "INCONCLUSIVE", (-0.2, 0.2): "BELOW_TARGET", (0.05, 0.2): "POSITIVE_BELOW_TARGET",
                       (0.3, 0.6): "ABOVE_TARGET", (-0.6, -0.1): "OPPOSITE"}.items():
    check(f"line {lo} {hi}", X.verdict_target({"lo": lo, "hi": hi}, 0.25), want)
for (lo, hi), want in {(-30, -5): "SUPPORTS", (-30, 5): "INCONCLUSIVE", (-10, 5): "BELOW_TARGET", (-10, -2): "POSITIVE_BELOW_TARGET", (-40, -20): "ABOVE_TARGET", (2, 9): "OPPOSITE"}.items():
    check(f"trip {lo} {hi}", X.verdict_target({"lo": lo, "hi": hi}, -12.0), want)
for (lo, hi), want in {(0.5, 1.7): "SUPPORTS", (0.1, 1.2): "INCONCLUSIVE", (0.1, 0.8): "BELOW_BAND", (1.4, 2.4): "ABOVE_BAND"}.items():
    check(f"hold {lo} {hi}", X.verdict_band({"lo": lo, "hi": hi}, [1.0, 1.25], 0.25), want)
for (r1, r2), want in {("SUPPORTS", "SUPPORTS"): "SUPPORTED", ("INCONCLUSIVE", "SUPPORTS"): "PARTLY", ("ABOVE_TARGET", "SUPPORTS"): "PARTLY", ("BELOW_TARGET", "SUPPORTS"): "REFUTED",
                       ("OPPOSITE", "INCONCLUSIVE"): "REFUTED", ("SUPPORTS", "BELOW_BAND"): "REFUTED", ("SUPPORTS", "ABOVE_BAND"): "REFUTED", ("SUPPORTS", "INCONCLUSIVE"): "INCONCLUSIVE",
                       ("INCONCLUSIVE", "INCONCLUSIVE"): "INCONCLUSIVE", ("UNDER-RESOLVED", "UNDER-RESOLVED"): "UNDER-RESOLVED"}.items():
    check(f"room {r1} {r2}", X.verdict_room(r1, r2), want)
f = X.ols([0, 1, 2, 3], [1.0, 1.25, 1.5, 1.75], PRED["t975"])
check("ols exact slope", f["slope"], 0.25)
check("ols exact se", f["se"], 0.0)
f = X.ols([0, 1, 2, 3, 4], [0.0, 1.0, 1.0, 3.0, 4.0], PRED["t975"])
check("ols slope by hand", f["slope"], 1.0)                  # sxx 10, sxy 10
check("ols se by hand", f["se"], 0.1633, 0.0001)             # sse 0.8 -> sqrt(0.8 / 3 / 10)
check("ols lo", f["lo"], 1.0 - 3.182 * 0.1633, 0.001)


# ---- 2. the synthetic night
KINDS = [("fp32", "zeros", "fp32-zeros-fromrest", 35.6, 57.9), ("fp16", "zeros", "fp16-zeros", 35.8, 58.0), ("int8", "zeros", "int8-zeros", 36.6, 58.2),
         ("int8", "neg_ones", "int8-neg_ones", 41.0, 60.0), ("int8", "sparse50", "int8-sparse50", 49.0, 63.5), ("fp16", "ones", "fp16-ones", 53.0, 65.2),
         ("int8", "full", "int8-full", 52.0, 65.0), ("fp32", "randn", "fp32-randn", 54.0, 66.0), ("fp16", "ones", "fp16-ones-rep2", 53.0, 65.2)]
L = PRED["constants"]["l_800_w_per_c"]


def samples(t0, t1, w, die, mhz=800, io=None):
    out, t = [], t0
    while t <= t1:
        out.append(json.dumps({"t_ms": t, "board_w": round(w, 4), "temp_c": {"minshire": [die, 40, 70], "ioshire": [io if io is not None else die, 40, 70], "pmic": die},
                               "mhz": {"minion": mhz, "noc": 400, "ddr": 933}}))
        t += 100
    return out


def make_probe(data, name, t, w_rest, slope_line, slope_hold_die, dip=False, rest_broken=False):
    """One probe at epoch ms t. x is W-derived; the line, the fine W and the hold move with x - x0 by the planted slopes."""
    x0 = 22.1 / WPC
    dx = w_rest / WPC - x0
    p = os.path.join(data, name)
    os.makedirs(os.path.join(p, "tel"))
    os.makedirs(os.path.join(p, "sp"))
    json.dump({"dry": True, "experiment": "E98"}, open(os.path.join(p, "session.json"), "w"))
    runs, launches = [], []
    tt = t
    rest = {"run": "REST-00-rest-r1", "block": "REST", "idx": 0, "rep": 1, "label": "rest", "type": "fp32", "values": "zeros", "gate": {"mode": "cool", "held_s": 0.0, "reached": True, "reading": [47, 50, 22.1, 600]},
            "t_first_ms": tt + 1000, "t_last_ms": tt + 1000, "launches": [], "queries": {"sp_events": [], "config": {"tdp_w": 65, "temp_threshold_c": 65}}, "tel": "tel/REST-00-rest-r1.jsonl"}
    open(os.path.join(p, "tel", rest["run"] + ".jsonl"), "w").write("\n".join(samples(tt, tt + 120000, w_rest + 0.5, 47, 600)) + "\n")
    runs.append(rest)
    tt += 125000
    for i, (ty, v, label, w0, die0) in enumerate(KINDS):
        name_r = f"SUS-{i:02d}-{label}-r1"
        # the line moves by slope_line * dx with the die alone, W fixed, for trip kinds; for unclamped ones the fine W moves as the fine rule plants
        dw = L * dx * (slope_line * (1 / (1 - K * L))) if ty != "x" else 0
        w = w0 + dw
        die = die0 + slope_line * dx + K * dw
        recs = []
        tel_lines = []
        a = tt
        for pr in range(9):
            b = a + 8000
            kw = [{"t_start_ms": a + 200 + 500 * j, "t_end_ms": a + 700 + 500 * j, "ok": True, "iters": 1000, "cycles_max": 400000000, "wall_s": 0.5, "minions": 1024, "cycles_per_op": 546.0, "result": "unchecked"} for j in range(15)]
            launches.append({"run": name_r, "role": "work", "proc": pr, "rc": 0, "t_start_ms": a, "t_end_ms": b, "sparsity": kw})
            recs.append({"proc": pr, "rc": 0, "t_start_ms": a, "t_end_ms": b, "n_launch": 15})
            tel_lines += samples(a, b, w, die)
            a = b + 400
        t_last = a - 400
        if dip and i == 2:
            # a planted dip in the last 40 s: clock 600 for 1 s, W 10 lower, in one process
            d0 = t_last - 12000
            new = []
            for ln in tel_lines:
                r = json.loads(ln)
                if d0 <= r["t_ms"] < d0 + 1000:
                    r["mhz"]["minion"] = 600
                    r["board_w"] = round(w - 10, 4)
                new.append(json.dumps(r))
            tel_lines = new
        open(os.path.join(p, "tel", name_r + ".jsonl"), "w").write("\n".join(tel_lines) + "\n")
        runs.append({"run": name_r, "block": "SUS", "idx": i, "rep": 1, "label": label, "type": ty, "values": f"file:tools/claims-v3/kinds/tiles/{ty}/{v}.bin",
                     "gate": {"mode": "cool", "held_s": 10.0, "reached": True, "reading": [57, 60, 25.0, 600]}, "t_first_ms": tt, "t_last_ms": t_last, "launches": recs, "minions": 1024, "seconds": 8, "processes": 9,
                     "queries": {"sp_events": [], "config": {"tdp_w": 65, "temp_threshold_c": 65}, "t_ms": t_last + 6000}, "tel": f"tel/{name_r}.jsonl"})
        tt = t_last + 30000
    # the hold
    name_h = "HOLD-00-int8-neg_ones-hold-r1"
    w = 41.5 + L * dx * slope_hold_die
    die = 62.0 + slope_hold_die * dx
    tel_lines, recs = [], []
    a = tt
    for pr in range(39):
        b = a + 8000
        kw = [{"t_start_ms": a + 200 + 500 * j, "t_end_ms": a + 700 + 500 * j, "ok": True, "iters": 1000, "cycles_max": 400000000, "wall_s": 0.5, "minions": 1024, "cycles_per_op": 318.0, "result": "unchecked"} for j in range(15)]
        launches.append({"run": name_h, "role": "work", "proc": pr, "rc": 0, "t_start_ms": a, "t_end_ms": b, "sparsity": kw})
        recs.append({"proc": pr, "rc": 0, "t_start_ms": a, "t_end_ms": b, "n_launch": 15})
        tel_lines += samples(a, b, w, die)
        a = b + 400
    open(os.path.join(p, "tel", name_h + ".jsonl"), "w").write("\n".join(tel_lines) + "\n")
    runs.append({"run": name_h, "block": "HOLD", "idx": 0, "rep": 1, "label": "int8-neg_ones-hold", "type": "int8", "values": "file:tools/claims-v3/kinds/tiles/int8/neg_ones.bin",
                 "gate": {"mode": "cool", "held_s": 20.0, "reached": True, "reading": [57, 60, 25.0, 600]}, "t_first_ms": tt, "t_last_ms": a - 400, "launches": recs, "minions": 1024, "seconds": 8, "processes": 39,
                 "queries": {"sp_events": [], "config": {"tdp_w": 65, "temp_threshold_c": 65}, "t_ms": a}, "tel": f"tel/{name_h}.jsonl"})
    with open(os.path.join(p, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(p, "launches.jsonl"), "w") as f:
        for r in launches:
            f.write(json.dumps(r) + "\n")
    open(os.path.join(p, "queries.jsonl"), "w").write(json.dumps({"tag": "start", "t_ms": t, "sp_events": []}) + "\n")
    # the box's history: the 40 min before the REST block, at w_rest; a broken rest has a hot row 5 min before it
    hist = []
    for ti in range(t - 40 * 60000, t, 5000):
        c = {"n": 0, "ok": True, "held": False, "die": 47, "max": 70, "w": w_rest}
        if rest_broken and t - 5 * 60000 <= ti < t - 4 * 60000:
            c = {"n": 0, "ok": True, "held": True}
        hist.append({"t": ti, "cpu": 1.0, "mem": 5.0, "load": 0.5, "temps": {"nic": 44.0 + (w_rest - 22.1) / 0.256, "nvme": 37.0, "cpu": 35.0}, "cards": [c]})
    return hist


def night(walls, slope_line, slope_hold, broken=None, dip=None):
    data = tempfile.mkdtemp(prefix="e98-selftest-")
    os.makedirs(os.path.join(data, "history"))
    t = 1793520000000
    hist = []
    for i, w_rest in enumerate(walls):
        name = f"P{i + 1}"
        hist += make_probe(data, name, t, w_rest, slope_line, slope_hold, dip=(dip == name), rest_broken=(broken == name))
        t += 3 * 3600 * 1000
    with gzip.open(os.path.join(data, "history", "aifoundry2-2026-11-01.jsonl.gz"), "wt") as f:
        for r in sorted(hist, key=lambda r: r["t"]):
            f.write(json.dumps(r) + "\n")
    out = os.path.join(data, "results.json")
    rc = subprocess.call([sys.executable, os.path.join(HERE, "reduce_e98.py"), data, "--out", out], stdout=subprocess.DEVNULL)
    res = json.load(open(out)) if rc == 0 else None
    return data, rc, res


walls = [22.11, 22.05, 21.86, 21.76, 21.73, 21.71, 21.67]
d, rc, res = night(walls, 0.25, 1.12, broken="P3", dip="P5")
check("reduce rc", rc, 0)
check("counted probes", len(res["probes_counted"]), 6)
check("broken rest left out", "P3" in res["probes_counted"], False)
check("R1 slope recovered", res["R1"]["fit"]["slope"], 0.25, 0.002 + 0.05)      # the planted dip in P5's int8 zeros moves one kind's line by a little
check("R2 slope recovered", res["R2"]["fit"]["slope"], 1.12, 0.002)
check("S2 hold W per rest W", res["S2"]["fit"]["slope"], L / WPC * 1.12, 0.01)
check("S1 fine W per rest W", res["S1"]["fit"]["slope"], 0.25 * (1 / (1 - K * L)) * L / WPC, 0.01)
check("R0 range", res["R0"]["range_c"], (22.11 - 21.67) / WPC, 0.01)
check("gate", res["R0"]["gate"], "OK")
p5 = next(p for p in res["probes"] if p["probe"] == "P5")
check("the planted dip is flagged", len(p5["runs"]["2"]["dips"]) if "2" in p5["runs"] else len(p5["runs"][2]["dips"]), 1)
check("no dip elsewhere", sum(len(r["dips"]) for p in res["probes"] for r in p["runs"].values()), 1)
print("verdicts on the planted night:", res["R1"]["verdict"], res["R2"]["verdict"], res["V"])
shutil.rmtree(d, ignore_errors=True)
d, rc, res = night(walls, 0.0, 0.25)
check("no-follow night R1", res["R1"]["verdict"] in ("BELOW_TARGET", "POSITIVE_BELOW_TARGET"), True)
check("no-follow night R2", res["R2"]["verdict"], "BELOW_BAND")
check("no-follow night V", res["V"], "REFUTED")
shutil.rmtree(d, ignore_errors=True)
d, rc, res = night([22.1, 22.05, 22.0, 22.05, 22.1, 22.0], 0.25, 1.12)
check("flat night gate", res["R0"]["gate"], "UNDER-RESOLVED")
check("flat night R1", res["R1"]["verdict"], "UNDER-RESOLVED")
check("flat night V", res["V"], "UNDER-RESOLVED")
shutil.rmtree(d, ignore_errors=True)
print("FAILS:", fails)
sys.exit(1 if fails else 0)
