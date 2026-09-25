#!/usr/bin/env python3
"""Data for docs/reports: why-low-power.
    build_lowpower_report_data.py --ablation a.json --model model.json --toggles t.json [--vf vf.json] [--second-card horace3.json] --out r.json"""
import argparse
import json

MULT = ("csa", "compressor", "wallace", "booth")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ablation", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--vf")
    ap.add_argument("--second-card", help="the second card's analyze_horace_strict.py output (horace3.json): its values beside this card's")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ab = json.load(open(a.ablation))
    m = json.load(open(a.model))
    tog = json.load(open(a.toggles))
    flips = {}
    for p in ("zeros", "ones", "randn"):
        mm = tog[p]["mean"]
        mult = sum(v for k, v in mm["by_block"].items() if any(s in k for s in MULT))
        flips[p] = {"ffclk": mm["ff_clocked"], "mult": mult, "rest": mm["nets"] - mult, "bus": mm["bus"]}
    c = ab["configs"]
    # the thermal network's settled (R_total) and open-loop step response and the leakage loop gain, for the page's
    # "each watt held for hours adds 1.47 degrees (1.2 after ten minutes)" sentence
    model = {"power": m["power"], "R_total": m["R_total"], "step_open": m["step_open"], "loop_gain_at_80": m["loop_gain_at_80"]}
    out = {"ablation": {"configs": c}, "model": model, "flips": flips,
           "facts": {"a100": {"transistors_b": 54.2, "die_mm2": 826, "tflops": 257, "watts": 330, "idle": 88, "volts": 0.85, "mhz": 1410, "mem_gbs": 1555},
                     "et": {"transistors_b": 24, "die_mm2": 570, "tflops": c["fp32_randn"]["per_s"] * 2 / 1e12, "watts": c["fp32_randn"]["p80"],
                            "idle62": 26.7, "idle80": c["fp32_randn"]["idle"], "volts": 0.52, "mhz": 600, "mem_gbs": 137}}}
    if a.vf:
        out["vf"] = json.load(open(a.vf))
    if a.second_card:
        # aifoundry3's strict session (the Horace experiment's section 10): the fp32 matmul on zeros, ones and random
        # normal at its own launch temperature, so the page can set that card's values beside this one's
        s2 = json.load(open(a.second_card))
        pat = {}
        for p in ("zeros", "ones", "randn"):
            v = s2["patterns"][p]
            pat[p] = {"n": v["n"], "p80": round(v["p80"], 3), "idle": round(v["p_before"], 3), "dyn": round(v["p80"] - v["p_before"], 3),
                      "tflops": round(v["tflops"], 4), "mv": round(v["mv"], 1), "p_late": round(v["p_late"], 3),
                      "rails_late": round(sum(v["rails_late"].values()), 3)}
        out["second_card"] = {"card": "aifoundry3", "launch_T": round(s2["thermal"]["model_T_at_launch"]["mean"], 2), "patterns": pat}
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
