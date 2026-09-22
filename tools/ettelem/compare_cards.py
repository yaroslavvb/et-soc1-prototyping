#!/usr/bin/env python3
"""Compare two ET-SoC-1 cards: switching power per operand pattern, and the leakage curve.

    compare_cards.py --card NAME=strict.json [--card NAME=strict.json ...] --model model.json --out cards.json

The switching power of a pattern is its board power at the session's own launch temperature minus the idle
power measured just before each run, so the leakage of that card at that temperature cancels. The flip model
fitted on one card predicts that number from RTL event counts alone:

    P_switching = p_sm * active/1024 + sum_j e_j * N_j * ops_per_second

Nothing is refitted here; the model's coefficients are read from `model.json` as they were fitted.
"""
import argparse
import json

import numpy as np

F_OP = 600e6 / 546.0
CLASSES = ["ffclk", "mult", "rest", "bus"]
MULT = ("csa", "compressor", "wallace", "booth")


def model_switching(model, toggles, pattern, active=1024):
    m = toggles[pattern]["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(s in k for s in MULT))
    counts = {"ffclk": m["ff_clocked"], "mult": mult, "rest": m["nets"] - mult, "bus": m["bus"]}
    pw = model["power"]
    return pw["p_sm_full_chip"] * active / 1024.0 + sum(
        pw["e_fJ"][c] * counts[c] * F_OP * active / 1e15 for c in CLASSES)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", action="append", required=True, help="NAME=path/to/horace3.json")
    ap.add_argument("--model", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    model = json.load(open(a.model))
    tog = json.load(open(a.toggles))
    cards = {}
    for spec in a.card:
        name, path = spec.split("=", 1)
        d = json.load(open(path))
        cards[name] = {
            "launch_temp": d["thermal"]["model_T_at_launch"]["mean"],
            "launch_temp_sd": d["thermal"]["model_T_at_launch"]["sd"],
            "leak_w_per_c": d["leak_w_per_c"],
            "patterns": {v: {"p80": p["p80"], "p80_sd": p["p80_sd"], "idle": p["p_before"],
                             "switching": p["p80"] - p["p_before"], "n": p["n"],
                             "tflops": p["tflops"], "rise": p.get("rise_fit"),
                             "mhz": p["mhz"], "mv": p["mv"]}
                         for v, p in d["patterns"].items()},
        }
    common = sorted(set.intersection(*[set(c["patterns"]) for c in cards.values()]),
                    key=lambda v: list(cards.values())[0]["patterns"][v]["p80"])
    rows = []
    for v in common:
        row = {"values": v, "model_switching": model_switching(model, tog, v) if v in tog else None}
        for name, c in cards.items():
            row[name] = c["patterns"][v]
        rows.append(row)
    names = list(cards)
    out = {"cards": {n: {k: v for k, v in c.items() if k != "patterns"} for n, c in cards.items()},
           "rows": rows, "names": names}
    # agreement between cards, and of each card against the model
    if len(names) == 2:
        a_, b_ = names
        d = [r[a_]["switching"] - r[b_]["switching"] for r in rows]
        out["card_diff"] = {"rms": float(np.sqrt(np.mean(np.square(d)))), "max": float(np.max(np.abs(d)))}
    for n in names:
        e = [r[n]["switching"] - r["model_switching"] for r in rows if r["model_switching"] is not None]
        out.setdefault("model_error", {})[n] = {"rms": float(np.sqrt(np.mean(np.square(e)))),
                                                "max": float(np.max(np.abs(e))), "n": len(e)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{'pattern':16s} " + "".join(f"{n+' switching':>20s}" for n in names) + f"{'model':>9s}")
    for r in rows:
        line = f"{r['values']:16s} " + "".join(f"{r[n]['switching']:12.2f} W (T={r[n]['p80'] - r[n]['switching']:4.1f}W idle)" for n in names)
        line += f"{r['model_switching']:8.2f}W" if r["model_switching"] is not None else "        -"
        print(line)
    for n in names:
        c = out["cards"][n]
        print(f"{n}: launch {c['launch_temp']:.2f} +- {c['launch_temp_sd']:.2f} C, leakage slope {c['leak_w_per_c']:.3f} W/C")
    if "card_diff" in out:
        print("card-to-card switching-power difference: rms %.2f W, max %.2f W" % (out["card_diff"]["rms"], out["card_diff"]["max"]))
    for n, e in out["model_error"].items():
        print(f"model (fitted on aifoundry2) vs {n}: rms {e['rms']:.2f} W, max {e['max']:.2f} W over {e['n']} patterns")


if __name__ == "__main__":
    main()
