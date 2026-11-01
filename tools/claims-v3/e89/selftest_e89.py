#!/usr/bin/env python3
"""E89 (Q130): the reducer's self-test. Builds two synthetic passes in the runner's and the sampler's exact formats,
from the heat model of docs/findings/11-thermal-model.md driven by E78's switching powers on the runner's schedule,
with 34 sensors truncated to whole degrees, then runs reduce_e89.py on them and checks that it recovers what was put
in: every kind heats by the same degC per W (r = 1), H at 1/60 Hz equals the model's, and the rules score PASS.
A second case gives int8 kinds 0.70 of the heat per watt; R2 must then FAIL or be INCONCLUSIVE for them.

    python3 tools/claims-v3/e89/selftest_e89.py <scratch dir>
"""
import gzip
import json
import math
import os
import random
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_e89 as rn  # noqa: E402

TAU = np.array([1.5, 4, 60, 150, 400, 2500.0])
R = np.array([0.106, 0.050, 0.234, 0.136, 0.860, 0.081])
KLEAK = 0.1994
DT = 0.1
E78S = {"int8.full": 9.648, "int8.gauss_q": 9.161, "int8.smallint": 8.628, "int8.sparse50": 8.061,
        "int8.neg_ones": 4.176, "int8.zeros": 2.605, "fp32.ones": 10.288, "fp32.randn": 26.701, "fp32.zeros": 1.986}
TYPE = {k: k.split(".")[0] for k in E78S}


def build(d, pass_no, t_start, gain_int8=1.0, seed=0):
    rng = np.random.default_rng(seed)
    os.makedirs(d, exist_ok=True)
    order = rn.pass_order("aifoundry3", pass_no)
    marks, runs = [], []
    seg = []                 # (t0, t1, item or None)
    t = t_start
    marks.append({"kind": "gate", "t_start_ms": int(t * 1000), "t_end_ms": int(t * 1000), "die_c": 55, "reached": True, "gate_c": 62})
    marks.append({"kind": "idle", "t_start_ms": int(t * 1000), "t_end_ms": int((t + 15) * 1000), "die_c": 55})
    seg.append((t, t + 15, None))
    t += 15
    for bi, b in enumerate(order):
        k, z = rn.BLOCKS[b]
        tb = t + 0.3
        marks.append({"kind": "block", "block": b, "pos": bi, "item": k, "ref": z, "t_start_ms": int(tb * 1000),
                      "t_end_ms": int((tb + 140) * 1000), "half_s": 30.0, "cycles": 2, "lead_s": 20.0, "die_c": 55})
        halves = [(z, 20.0, "lead")] + [(k, 30.0, "K"), (z, 30.0, "Z")] * 2
        th = tb
        for hi, (item, L, role) in enumerate(halves):
            marks.append({"kind": "half", "block": b, "half": hi, "role": role, "item": item,
                          "t_start_ms": int(th * 1000), "t_end_ms": int((th + L) * 1000)})
            if item == "idle":
                seg.append((th, th + L, None))
            else:
                tl = th
                while th + L - tl - 0.75 >= 1.0:
                    secs = min(6.8, th + L - tl - 0.75)
                    seg.append((tl, tl + 0.7, None))
                    c0 = tl + 0.7
                    seg.append((c0, c0 + secs, item))
                    marks.append({"kind": "launch", "block": b, "half": hi, "role": role, "item": item, "secs": secs,
                                  "t_start_ms": int(tl * 1000), "t_end_ms": int((c0 + secs + 0.05) * 1000), "rc": 0, "records": 2})
                    for li, (a0, a1) in enumerate([(c0, c0 + 0.02), (c0 + 0.02, c0 + secs)]):
                        runs.append({"card": "aifoundry3", "pass": pass_no, "block": b, "half": hi, "role": role, "item": item,
                                     "type": TYPE[item], "launch": li - 1, "cycles_per_op": 546.0 if TYPE[item] == "fp32" else 318.0,
                                     "t_start_ms": int(a0 * 1000), "t_end_ms": int(a1 * 1000), "ok": True})
                    tl = c0 + secs + 0.05
                seg.append((tl, th + L, None))
            th += L
        t = th
    seg.append((t, t + 5, None))
    t_end = t + 5
    n = int((t_end - t_start) / DT)
    tt = t_start + np.arange(n) * DT
    P = np.zeros(n)
    for a0, a1, item in seg:
        if item is None:
            continue
        m = (tt >= a0) & (tt < a1)
        P[m] = E78S[item]
    # heat: int8 compute heats with gain_int8 per watt (the case where heat does not follow power)
    is8 = np.zeros(n, bool)
    for a0, a1, item in seg:
        if item and item.startswith("int8"):
            is8[(tt >= a0) & (tt < a1)] = True
    x = np.zeros(6)
    T = np.empty(n)
    for i in range(n):
        p_heat = P[i] * (gain_int8 if is8[i] else 1.0) + KLEAK * x.sum()
        x += DT / TAU * (R * p_heat - x)
        T[i] = 52.0 + x.sum()
    offs = rng.uniform(0, 3, 34)
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "wt") as f:
        for i in range(n):
            c = np.floor(T[i] + offs + rng.normal(0, 0.15, 34)).astype(int).tolist()
            fw = int(sum(c) // 34)
            bw = 25.9 + P[i] + KLEAK * (T[i] - 52.0) + rng.normal(0, 0.05)
            f.write(json.dumps({"t_ms": int(tt[i] * 1000), "board_w": round(bw, 2),
                                "temp_c": {"pmic": fw, "ioshire": [fw, 0, 0], "minshire": [fw, 40, 90]},
                                "die_mv": {"minion": 522}, "mhz": {"minion": 600, "noc": 400, "ddr": 933},
                                "pvt": {"st": 0, "f": 0, "c": c}}) + "\n")
    with open(os.path.join(d, "marks.jsonl"), "w") as f:
        for m in marks:
            f.write(json.dumps(m) + "\n")
    with open(os.path.join(d, "runs.jsonl"), "w") as f:
        for r in runs:
            f.write(json.dumps(r) + "\n")
    json.dump({"args": {"pass_no": pass_no}, "order": order}, open(os.path.join(d, "configs.json"), "w"))
    json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
    json.dump({"sampler": "pvt"}, open(os.path.join(d, "sampler.json"), "w"))
    return t_end


def case(scratch, name, gain):
    base = os.path.join(scratch, name)
    t1 = build(os.path.join(base, "p8910"), 8910, 1.79e9, gain, seed=1)
    build(os.path.join(base, "p8911"), 8911, t1 + 40, gain, seed=2)
    out = os.path.join(base, "red")
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    r = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e89.py"), os.path.join(base, "p8910"),
                        os.path.join(base, "p8911"), "--out", out,
                        "--e78", os.path.join(root, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")],
                       capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        raise SystemExit(f"{name}: reducer failed")
    return json.load(open(os.path.join(out, "e89.json")))


def main():
    scratch = sys.argv[1]
    ok = True
    e = case(scratch, "linear", 1.0)
    print("== case 1: heat follows power (every kind 1.00 per W)")
    for b, v in e["blocks"].items():
        rh = v.get("r_H") or {}
        print(f"  {b:9s} laps {v['laps']} H {v['H_proj_ref_phase']['mean']:.4f} +- {v['H_proj_ref_phase']['ci95']:.4f}"
              f"  r {rh.get('r', 1):.3f} [{rh.get('lo', 1):.3f}, {rh.get('hi', 1):.3f}]  T {v['T_fund_C']['mean']:.3f} C"
              f"  int-mean T {v['T_int_fund_C']['mean']:.3f} +- {v['T_int_fund_C']['ci95']:.3f}"
              f"  step2/W {v['step2_C_per_W_E78']['mean']:.4f}  swing30/W {v['swing30_C_per_W_E78']['mean']:.4f}")
        if b != "f32randn" and not (0.93 <= rh.get("r", 0) <= 1.07):
            ok = False
    print("  tally", e["tally"])
    for v in e["verdicts"]:
        if v["rule"] in ("E89-R0", "E89-R1", "E89-R2", "E89-R3") and v["verdict"] != "PASS":
            print("  NOT PASS:", v)
            ok = False
    e2 = case(scratch, "int8_070", 0.70)
    print("== case 2: int8 heats 0.70 per W")
    for v in e2["verdicts"]:
        if v["rule"] == "E89-R2":
            print("  ", v["cell"], v["verdict"], {k: round(x, 3) for k, x in v["measured"].items() if isinstance(x, float)})
            if v["cell"].startswith("i8") and v["verdict"] == "PASS":
                ok = False
    print("SELFTEST", "OK" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
