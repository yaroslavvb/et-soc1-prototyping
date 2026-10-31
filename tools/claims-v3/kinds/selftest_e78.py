#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E78 self-test: the analysis run on SYNTHETIC passes with known answers, before any card data exist.

    python3 tools/claims-v3/kinds/selftest_e78.py <scratch dir> [--passes 6] [--seed 1]

It writes fake pass directories in the exact layout block_e78.sh / run_e78.py write (configs.json, plan.json,
marks.jsonl, runs.jsonl, telemetry.jsonl.gz at 10 Hz, tiles/ dumps, config_*.json, block.json), with every run in
the registered order of e78_common.pass_order. The injected truth is Q130(c)'s frozen prediction for each kind's
switching over its type's zeros, on top of a zero-data level per type, an idle that drifts 0.3 W a pass, a leakage
term, integer die readings, launch gaps, heaters, and a minion rail that lags board power (tau 1.00 s, 0.2 s,
the top of E79's measured range, against the reducer's registered 0.95 s).
Then it runs reduce_e78.py and score_e78.py on them and checks what they recover. NOTHING HERE IS A MEASUREMENT;
the output is never data. Exit 0 if every check holds.
"""
import argparse
import gzip
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e78_common as ec  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ZERO_LEVEL = {"fp32": 1.9, "fp16": 1.9, "int8": 2.5}   # synthetic switching of each type's zeros over idle (W)
K_TRUE = 0.15        # synthetic leakage, W per C
HEAT = 0.025         # synthetic die heating, C per W per s
TAU, DELAY, C_RB = 1.00, 0.2, 0.81   # the synthetic truth: the top of E79's measured range


def truth():
    pc = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-q130-kinds-model/predictions.json")))
    d = {}
    for key, v in pc["predictions"].items():
        ty, k = key.split("/", 1)
        d[f"{ty}.{k}"] = v["switching_w_600mhz_a3"]
    d[ec.TIE] = d["fp32.pi"]
    return d


def make_pass(out, p, D, rng, items):
    by = {it["name"]: it for it in items}
    order = ec.pass_order(items, "aifoundry3", p)
    os.makedirs(os.path.join(out, "tiles"), exist_ok=True)
    t = 1_793_500_000_000.0 + (p - 7810) * 900_000.0    # ms
    t_block0 = t
    segs = []          # (start, end, watts over idle, kind)  - launches and heaters
    marks, recs = [], []
    prev_end = t

    def heater():
        nonlocal t, prev_end
        h0 = t + 50
        h1 = h0 + 2700
        segs.append((h0 + 100, h1 - 50, 26.0, "heater"))
        marks.append({"kind": "heater", "item": "x", "block": p, "t_start_ms": int(h0), "t_end_ms": int(h1),
                      "die_c": 58.0, "rc": 0})
        t = h1 + 400
        prev_end = h1

    def run(name, pos, seg, burn=False):
        nonlocal t, prev_end
        it = by[name]
        ty = it["type"]
        if rng.random() < 0.35 and not burn:
            heater()
            t = prev_end + rng.uniform(2100, 3400)            # the cool-down to 58 C after a heater
        else:
            t = max(t, prev_end + rng.uniform(2000, 2900))    # the quiet rule
        spawn = t
        t0 = spawn + 184
        level = ZERO_LEVEL[ty] + D[name]
        cpo = ec.CPO[ty]
        lrecs = []
        cal_end = t0 + 19
        lrecs.append({"launch": -1, "t_start_ms": int(t0), "t_end_ms": int(cal_end), "iters": 20000})
        s = cal_end + 1
        for n in range(8):
            e = s + 491
            lrecs.append({"launch": n, "t_start_ms": int(s), "t_end_ms": int(e), "iters": int(0.491 * 600e6 / cpo)})
            s = e + 3
            if s - t0 > 4000:
                break
        for r in lrecs:
            segs.append((r["t_start_ms"], r["t_end_ms"], level, name))
            if not burn:
                recs.append({"card": "aifoundry3", "block": p, "pos": pos, "segment": seg, "item": name, "type": ty,
                             "kind_name": it["kind"], "attempt": 1, "start_c": 58.0, "start_hot_c": 59.0, "heats": 0,
                             "wait_s": 0.3, "quiet_s": round((spawn - prev_end) / 1000, 2), "prev_end_ms": int(prev_end),
                             "test": "fma", "type_": ty, "minions": 1024, "iters": r["iters"], "launch": r["launch"],
                             "cycles_per_op": cpo * (1 + rng.normal(0, 2e-5)), "t_start_ms": r["t_start_ms"],
                             "t_end_ms": r["t_end_ms"], "result": "unchecked", "ok": True})
        end = lrecs[-1]["t_end_ms"] + 40
        m = {"kind": "burnin" if burn else "run", "item": name, "block": -1 if burn else p, "t_start_ms": int(spawn),
             "t_end_ms": int(end), "start_c": 58.0, "start_hot_c": 59.0, "heats": 0, "wait_s": 0.3,
             "quiet_s": round((spawn - prev_end) / 1000, 2), "prev_end_ms": int(prev_end), "on_protocol": True}
        if not burn:
            m.update({"pos": pos, "segment": seg, "attempt": 1, "rc": 0, "launches": len(lrecs)})
            if not os.path.exists(os.path.join(out, "tiles", f"{name}.b{p}.bin")):
                src = os.path.join(ROOT, by["fp32.pi"]["tile"] if name == ec.TIE else it["tile"])
                shutil.copy(src, os.path.join(out, "tiles", f"{name}.b{p}.bin"))
        marks.append(m)
        prev_end = end
        t = end + 300

    for _ in range(2):
        run(ec.TIE, -1, -1, burn=True)
    for r in order:
        run(r["item"], r["pos"], r["segment"])
    t_end = t + 3000
    # ---- telemetry at 10 Hz
    ts = np.arange(t_block0 - 3000, t_end, 100.0)
    sw = np.zeros_like(ts)
    for a, b, lv, _ in segs:     # a sample reports the mean over the 100 ms before it, as a sensor integrates
        sw += lv * np.clip(np.minimum(ts, b) - np.maximum(ts - 100.0, a), 0, None) / 100.0
    # the die: 58.3 C at idle, heating while a launch runs, relaxing between
    T = np.empty_like(ts)
    x = 58.3
    for i, s_ in enumerate(sw):
        x += HEAT * s_ * 0.1 - (x - 58.3) * 0.1 / 1.5
        T[i] = x
    idle = 26.0 + 0.30 * (ts - t_block0) / (t_end - t_block0)
    board = idle + sw + K_TRUE * (T - 58.3) + rng.normal(0, 0.08, len(ts))
    rail_true = 9.0 + C_RB * (board - idle)
    al = 1 - math.exp(-0.1 / TAU)
    rail = np.empty_like(ts)
    acc = rail_true[0]
    dn = int(round(DELAY / 0.1))
    for i in range(len(ts)):
        acc += al * (rail_true[max(0, i - dn)] - acc)
        rail[i] = acc + rng.normal(0, 0.03)
    with gzip.open(os.path.join(out, "telemetry.jsonl.gz"), "wt") as f:
        for i in range(len(ts)):
            f.write(json.dumps({"t_ms": int(ts[i]), "board_w": round(float(board[i]), 2),
                                "sp": {"minion_w": [round(float(rail[i]), 3), 0, 0]},
                                "mhz": {"minion": 600}, "die_mv": {"minion": 522 + int(rng.integers(-1, 2))},
                                "temp_c": {"minshire": [int(math.floor(T[i])), 0, 0], "pmic": 50}}) + "\n")
    with open(os.path.join(out, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    with open(os.path.join(out, "runs.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    json.dump({"card": "aifoundry3", "experiment": "E78", "order": order,
               "args": {"target": 58.0, "preheat": 59.0, "quiet_s": 2.0}}, open(os.path.join(out, "configs.json"), "w"))
    json.dump(order, open(os.path.join(out, "plan.json"), "w"))
    for nm in ("config_start", "config_end"):
        json.dump({"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 522},
                  open(os.path.join(out, nm + ".json"), "w"))
    json.dump({"exp": "kinds", "pass": p, "card": "aifoundry3", "status": "ok", "note": "SYNTHETIC selftest"},
              open(os.path.join(out, "block.json"), "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    items = ec.load_items()
    D = truth()
    base = os.path.join(a.scratch, "synthetic", "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    for i in range(a.passes):
        d = os.path.join(base, f"p{ec.FIRST_PASS + i}")
        os.makedirs(d)
        make_pass(d, ec.FIRST_PASS + i, D, rng, items)
        dirs.append(d)
    py = sys.executable
    e78 = os.path.join(a.scratch, "synthetic-e78.json")
    r = subprocess.run([py, os.path.join(HERE, "reduce_e78.py"), *dirs, "--out", e78,
                        "--txt", os.path.join(a.scratch, "synthetic-reduce.txt"),
                        "--csv", os.path.join(a.scratch, "synthetic-runs.csv")], capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit("reduce_e78.py failed")
    r2 = subprocess.run([py, os.path.join(HERE, "score_e78.py"), "--e78", e78,
                         "--json", os.path.join(a.scratch, "synthetic-scored.json"),
                         "--md", os.path.join(a.scratch, "synthetic-results.md")], capture_output=True, text=True)
    if r2.returncode:
        print(r2.stdout[-2000:], r2.stderr[-3000:])
        sys.exit("score_e78.py failed")
    e = json.load(open(e78))
    sc = json.load(open(os.path.join(a.scratch, "synthetic-scored.json")))
    worst_d = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in e["items"] if n != ec.TIE)
    worst_s = max(abs(e["items"][n]["S"]["mean"] - (D[n] + ZERO_LEVEL[e["items"][n]["type"]]))
                  for n in e["items"] if n != ec.TIE and e["items"][n]["S"]["mean"] is not None)
    worst_32 = max(abs(e["items"][n]["D32"]["mean"] - (D[n] + ZERO_LEVEL[e["items"][n]["type"]] - ZERO_LEVEL["fp32"]))
                   for n in e["items"] if n != ec.TIE)
    rail_ratio = [e["items"][n]["Drail"]["mean"] / e["items"][n]["D"]["mean"] for n in e["items"]
                  if n != ec.TIE and e["items"][n]["D"]["mean"] and e["items"][n]["D"]["mean"] > 5]
    pj = e["items"]["fp32.randn"]["pj_op_S"]["mean"]
    pj_true = 1e12 * (D["fp32.randn"] + ZERO_LEVEL["fp32"]) / e["items"]["fp32.randn"]["rate"]["mean"]
    checks = {
        "passes_kept": (len(e["passes"]) == a.passes, len(e["passes"])),
        "runs_kept_all": (e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "D_recovered_within_0.15W": (worst_d <= 0.15, round(worst_d, 4)),
        "S_recovered_within_0.20W": (worst_s <= 0.20, round(worst_s, 4)),
        "D32_recovered_within_0.15W": (worst_32 <= 0.15, round(worst_32, 4)),
        "rail_over_board_near_c_rb": (all(0.75 <= x <= 0.87 for x in rail_ratio),
                                      (round(min(rail_ratio), 3), round(max(rail_ratio), 3))),
        # the within-run slope is ATTENUATED by the reading's 1 C steps (the true rise inside a window is smaller
        # than one step): it must come out between 0 and the truth, never above it
        "leak_slope_attenuated_not_inflated": (0 <= e["leak"]["k_w_per_c"] <= K_TRUE, round(e["leak"]["k_w_per_c"], 4)),
        "pj_op_matches_truth_2pct": (abs(pj / pj_true - 1) < 0.02, (round(pj, 1), round(pj_true, 1))),
        "duty_in_band": (all(0.99 <= v <= 1.0 for v in e["checks"]["duty"].values() if v is not None),
                         round(min(v for v in e["checks"]["duty"].values() if v is not None), 4)),
        "tie_dump_check": (all(e["checks"]["tie_dump_equals_fp32_pi_tile"].values()), None),
        "rail_tau_refit": (abs((e["checks"]["rail_refit"]["tau_median_s"] or 0) - TAU) <= 0.1,
                           e["checks"]["rail_refit"]["tau_median_s"]),
        "q130c_R1_self_rho_1": (all(v["rho"] is not None and v["rho"] > 0.99
                                    for v in sc["rules"]["E78-R1"]["by_model"]["q130c"].values()), None),
        "q130c_R2_self_rms_small": (all(v["rms_w"] < 0.15 for v in sc["rules"]["E78-R2"]["by_model"]["q130c"].values()),
                                    None),
        "idle_consistency_small": ((e["checks"]["idle_consistency"]["median_abs_w"] or 9) < 0.15,
                                   e["checks"]["idle_consistency"]["median_abs_w"]),
    }
    for k, (ok, v) in checks.items():
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print("tally on synthetic data (meaningless as a result):", sc["tally"])
    sys.exit(0 if all(ok for ok, _ in checks.values()) else 1)


if __name__ == "__main__":
    main()
