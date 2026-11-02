#!/usr/bin/env python3
"""E135: show that each rule of reduce_e135.py can hold and can fail, on made-up units (no GPU data is read).

    python3 selftest_e135.py > selftest.txt

The made-up GPU: max SM clock 1410 MHz, a 400 W limit, TFLOPS = 0.2 per MHz, and each kind's power at the full clock
D (W); a kind over the limit runs at the clock where 60 + (D - 60) (f / 1410)^2 = 400, with the SW power cap set."""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reduce_e135 as R  # noqa: E402

PREDS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions-e135.json")))
FMAX, L, P0 = 1410.0, 400.0, 60.0
DEMAND = {"bf16": {"zeros": 300, "randn": 520, "twos": 340, "rand": 500, "pi": 345, "sparse75": 470, "onebit": 380,
                   "checker": 490, "ternary": 430},
          "fp16": {"zeros": 300, "randn": 540, "twos": 340, "rand": 510},
          "tf32": {"zeros": 330, "randn": 560, "twos": 360, "rand": 540},
          "int8": {"zeros": 280, "rand_full": 500, "twos": 320, "randn_q": 470}}
PEAK = {"bf16": 0.2, "fp16": 0.2, "tf32": 0.1, "int8": 0.4}


def operating(d, lim=L):
    if d <= lim:
        return FMAX, float(d), 0
    f = FMAX * ((lim - P0) / (d - P0)) ** 0.5
    return f, lim, R.BITS["sw_power"]


def make_unit(name, tweaks=None, lowcap=None, protocol_gap=None):
    tw = tweaks or {}
    steps, samples = [], []
    t = 1000.0
    steps.append({"op": "static", "static": {"name": "NVIDIA A100-SXM4-40GB", "max_clock_sm": 1410, "power_default_mw": 400000,
                                             "power_enforced_mw": 400000}})
    energy = [0.0]

    def emit(t_lo, t_hi, f, p, rsn, lim, thermal=0):
        tt = t_lo + 0.05
        while tt < t_hi:
            energy[0] += p * 100.0
            samples.append({"t": tt, "tb": tt + 0.002, "sm": f, "mem": 1215, "p_mw": p * 1000, "e_mj": energy[0], "temp": 55,
                            "rsn": rsn | thermal, "plim_mw": lim * 1000, "pstate": 0, "util": [100, 60]})
            tt += 0.1

    def cell(dt, kind, p, cap="default", lim=L):
        nonlocal t
        d = DEMAND[dt][kind] + tw.get(("demand", dt, kind), 0)
        f, pw, rsn = operating(d, lim)
        f_b = f * tw.get(("burst_clock", dt, kind), 1.0)
        tf = PEAK[dt] * f * tw.get(("eff", dt, kind), 1.0)
        tf_b = PEAK[dt] * f_b * tw.get(("eff", dt, kind), 1.0)
        rsn = tw.get(("rsn", dt, kind), rsn)
        thermal = tw.get(("thermal", dt, kind), 0)
        pw = pw * tw.get(("power", dt, kind), 1.0)
        flop = 2 * 8192 ** 3
        cum, c = [], 0.0
        while c < 3000.0:
            c += flop / (tf_b * 1e12) * 1e3
            cum.append(round(c, 3))
        while c < 63000.0:
            c += flop / (tf * 1e12) * 1e3
            cum.append(round(c, 3))
        t0 = t
        emit(t0, t0 + 3.0, f_b, pw, rsn, lim, thermal)
        emit(t0 + 3.0, t0 + 63.0, f, pw, rsn, lim, thermal)
        steps.append({"op": "cell", "cap": cap, "label": f"{dt}-{kind}-p{p}",
                      "step": {"op": "cell", "dtype": dt, "kind": kind, "pass": p, "size": 8192, "burst_s": 3.0, "sus_s": 60.0},
                      "flop_per_mm": flop, "group": 1, "run": {"t0": t0, "group": 1, "cum_ms": cum},
                      "wait": {"T_start": 35, "target": 38, "reached": True},
                      "check": {"C_absmax": 0.0 if kind == "zeros" else 1.0}, "stats": {}})
        t = t0 + 100.0

    for dt, ks in DEMAND.items():
        for k in ks:
            cell(dt, k, 1)
    cell("bf16", "zeros", 2)
    cell("bf16", "randn", 2)
    # the protocol arm: its gap equals the sustained cells' unless told otherwise
    fz = operating(DEMAND["bf16"]["zeros"])[0]
    fr = operating(DEMAND["bf16"]["randn"])[0]
    g = protocol_gap if protocol_gap is not None else fz / fr
    rows = []
    for it in range(10):
        for k, tf in (("zeros", 0.2 * fz), ("randn", 0.2 * fz / g)):
            rows.append({"kind": k, "tflops": tf, "t_a": t, "t_b": t + 0.2})
            t += 0.3
    steps.append({"op": "protocol", "cap": "default", "label": "gist6", "rows": rows})
    if lowcap is not None:
        applied, lim2, widen = lowcap
        if applied:
            for k in ("zeros", "randn", "twos", "rand"):
                d = DEMAND["bf16"][k]
                if k == "randn" and not widen:
                    d = 345    # a made-up unit whose random data barely reaches the new cap
                f, pw, rsn = operating(d, lim2)
                tw2 = dict(tw)
                old = DEMAND["bf16"][k]
                DEMAND["bf16"][k] = d
                tweaks_backup = tw
                cell("bf16", k, 1, cap=f"{lim2:g}W", lim=lim2)
                DEMAND["bf16"][k] = old
                tw = tweaks_backup
        steps.append({"op": "lowcap", "applied": applied, "target_w": lim2, "set": {"rc": 0 if applied else 6}, "restore": {"restored": True}})
    return {"steps": steps, "samples": samples, "status": [], "done": {"skipped": []}, "static": steps[0]["static"], "idle0": None}


CASES = [
    ("the made-up capped GPU", {}, None, None,
     {"R1": "HOLDS", "R2": "HOLDS", "R3": "HOLDS", "R4": "HOLDS", "R5": "N/A", "R7": "HOLDS", "R8": "HOLDS", "R10": "HOLDS"}),
    ("random under the cap: no gap, no cap", {("demand", "bf16", "randn"): -150}, None, None,
     {"R1": "FAILS", "R4": "HOLDS"}),
    ("random 10% slow with no cap reason", {("rsn", "bf16", "randn"): 0, ("demand", "bf16", "randn"): -150,
                                            ("eff", "bf16", "randn"): 0.9}, None, None, {"R4": "FAILS", "R2": "FAILS"}),
    ("one kind 5% slower per MHz", {("eff", "fp16", "rand"): 0.95}, None, None, {"R2": "FAILS"}),
    ("random held by a thermal reason", {("thermal", "bf16", "randn"): R.BITS["sw_thermal"]}, None, None,
     {"R1": "FAILS", "R8": "FAILS"}),
    ("a capped kind 15% under the limit", {("power", "tf32", "rand"): 0.85}, None, None, {"R3": "FAILS"}),
    ("a burst gap far from the sustained one", {("burst_clock", "bf16", "randn"): 1.12}, None, None, {"R7": "FAILS"}),
    ("the protocol 0.1 off the cells", {}, None, 1.30, {"R10": "FAILS"}),
    ("a lower cap that widens the gap", {}, (True, 330.0, True), None, {"R5": "HOLDS"}),
    ("a lower cap whose gap narrows", {}, (True, 330.0, False), None, {"R5": "FAILS"}),
    ("a lower cap refused", {}, (False, 330.0, True), None, {"R5": "N/A"}),
    ("random at 450 W demand: the gap inside the band", {("demand", "bf16", "randn"): -70}, None, None, {"R6": "HOLDS"}),
    ("the made-up GPU's 1.163 gap: above the 400 W band", {}, None, None, {"R6": "FAILS", "R9": "HOLDS"}),
    ("zeros the dearest kind: the chart's order reversed", {("demand", "bf16", "zeros"): 300, ("demand", "bf16", "randn"): -220,
                                                         ("demand", "bf16", "rand"): -200, ("demand", "bf16", "checker"): -190},
     None, None, {"R9": "FAILS"}),
]


def main():
    bad = 0
    for name, tw, lowcap, pg, want in CASES:
        dem = copy.deepcopy(DEMAND)
        units = {"A": make_unit("A", tw, lowcap, pg), "B": make_unit("B", tw, None, pg)}
        DEMAND.clear()
        DEMAND.update(dem)
        _, _, _, gaps, rules = R.score(units, PREDS)
        for k, v in want.items():
            got = rules[k]["verdict"]
            ok = got == v
            bad += not ok
            print(f"{'ok  ' if ok else 'BAD '} {name:<44} {k}: {got} (want {v})")
    # the band itself, and Spearman on a reversed list
    print(f"ok   band at 400 W, n = 1/2/3: {[round(R.band(1.2209, 330, 88, 400, n), 4) for n in (1, 2, 3)]}")
    rho = R.spearman([1, 2, 3, 4], [4, 3, 2, 1])
    print(f"{'ok  ' if rho == -1 else 'BAD '} Spearman of a reversed list: {rho}")
    print(f"{bad} unexpected verdicts")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
