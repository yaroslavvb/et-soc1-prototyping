#!/usr/bin/env python3
"""Data for docs/reports: why-low-power.
    build_lowpower_report_data.py --ablation a.json --model model.json --toggles t.json [--vf vf.json] [--second-card horace3.json]
        [--v3 docs/reports/data/2026-09-25-claims-v3/results] --out r.json

--v3 adds the version-3 check's three cards (26 September 2026, V3-ABL-A: the same ablation configurations, four runs
each per card, reduced as registered) as a "v3" block beside the 21 September session the page is built on."""
import argparse
import json

MULT = ("csa", "compressor", "wallace", "booth")
# post-data note C2, revised: a launch on a downward step of the whole-degree die reading has the die this far above the
# reading (the 21 September thermal network at the 81 -> 80 step; tools/ettelem/build_cards_data.py uses the same)
STEP = 0.96
# the V3-ABL-A configurations the page uses
V3_CFGS = ("spin", "fp32_zeros", "fp32_ones", "fp32_randn", "fp32_randn_8", "fp32_randn_16", "fp16_zeros", "fp16_ones",
           "fp16_randn", "int8_zeros", "int8_ones", "int8_randn")


def v3_block(res):
    """Per card and configuration: board power (p80_d, the registered dropout rule), idle before the runs, switching
    over idle (the registered metric), work per second, and what the page derives from them; plus the intervals of
    the items that test the page's claims (ABL-T5, T6, T7) and the run-to-run spread (ABL-R). Nothing is fitted."""
    import os
    import statistics as st
    J = lambda f: json.load(open(os.path.join(res, f)))
    runs, abla = J("abla.runs.json"), J("abla.json")
    item = lambda k: next(x for x in abla if x["item"] == k)
    by = {}
    for c, rs in runs["runs"].items():
        for r in rs:
            if r.get("kept_busy"):
                by.setdefault(c, {}).setdefault(r["config"], []).append(r)
    cards = [c for c in runs["cards_all"] if c in by]
    out = {"source": "version-3 check, 26 September 2026: docs/reports/data/2026-09-25-claims-v3/results "
                     "(abla.runs.json kept runs, busy rule; abla.json items ABL-T5, T6, T7, R)", "cards": {}}
    P = runs["params_by_card"]
    for c in cards:
        mv = runs["idle_by_card"][c]["busy_mv"]
        cf = {}
        for k in V3_CFGS:
            rs = by[c].get(k)
            if not rs:
                continue
            m = lambda f: float(st.mean(r[f] for r in rs))
            p80, idle, dyn, per_s = m("p80_d"), m("p_before"), m("switching"), m("per_s")
            # post-data note C2 (AMENDMENTS.md, revised): the same runs at the die temperature of each launch,
            # switching + leak x (die - launch), under both readings of the whole-degree launch reading: die = reading
            # (dyn_at_launch) and die = reading + STEP, a launch on a downward step as the references' were
            # (dyn_at_launch_step); descriptive, not registered values
            atl = float(st.mean(r["switching"] + P[c]["leak"] * (r["t_launch"] - P[c]["launch"]) for r in rs))
            atls = float(st.mean(r["switching"] + P[c]["leak"] * (r["t_launch"] + STEP - P[c]["launch"]) for r in rs))
            cf[k] = {"n": len(rs), "minions": rs[0]["minions"], "unit": rs[0]["unit"], "p80": p80, "idle": idle,
                     "dyn": dyn, "dyn_sd": float(st.stdev(r["switching"] for r in rs)), "dyn_at_launch": atl,
                     "dyn_at_launch_step": atls, "per_s": per_s,
                     "pj_per_unit_dyn": dyn / per_s * 1e12, "pj_per_unit_board": p80 / per_s * 1e12,
                     "mw_per_minion": 1000.0 * dyn / rs[0]["minions"],
                     "nf_per_minion": dyn / rs[0]["minions"] / ((mv / 1000.0) ** 2 * 600e6) * 1e9}
        allr = [r for rs in by[c].values() for r in rs]   # every kept run of the card (ABL-R's launch_temp_c)
        out["cards"][c] = {"configs": cf, "busy_mv": mv, "T_reduced": P[c]["launch"], "leak_w_per_c": P[c]["leak"],
                           "launch_reading": float(st.mean(r["t_launch"] for r in allr)),
                           "at_launch_offset_w": float(st.mean(P[c]["leak"] * (r["t_launch"] - P[c]["launch"]) for r in allr)),
                           "at_launch_step_offset_w": float(st.mean(P[c]["leak"] * (r["t_launch"] + STEP - P[c]["launch"])
                                                                    for r in allr))}
    def ci(sub):
        return {k: sub["ci"][k] for k in ("point", "lo", "hi")}
    for k, name in (("ABL-T5", "t5"), ("ABL-T6", "t6"), ("ABL-T7", "t7")):
        it = item(k)
        out[name] = {"outcome": it["outcome"], "all_cards": it["all_cards"]["per_card"], "per_card": {}}
        for c in cards:
            pc = it["per_card"][c]
            subs = pc.get("subtests") or pc.get("vs_aifoundry2_values", {}).get("subtests", [])
            rep = pc.get("reported", {}).get("vs_aifoundry2_values", [])
            d = {s["test"]: ci(s) for s in subs + rep if "ci" in s}
            d.update({"line": s["fit"] for s in subs if "fit" in s})
            out[name]["per_card"][c] = d
    R = item("ABL-R")["per_card"]
    out["spread"] = {c: {"median_half_range_W": float(st.median(v["half_range_W"] for v in R[c]["half_differences"].values())),
                         "max_half_range_W": float(max(v["half_range_W"] for v in R[c]["half_differences"].values())),
                         "max_config": max(R[c]["half_differences"], key=lambda k: R[c]["half_differences"][k]["half_range_W"]),
                         "configs": len(R[c]["half_differences"]), "runs": 4} for c in cards}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ablation", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--vf")
    ap.add_argument("--second-card", help="the second card's analyze_horace_strict.py output (horace3.json): its values beside this card's")
    ap.add_argument("--v3", help="the version-3 check's results directory: its three cards beside this session")
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
    if a.v3:
        out["v3"] = v3_block(a.v3)
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
