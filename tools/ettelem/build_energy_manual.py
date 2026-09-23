#!/usr/bin/env python3
"""Assemble the energy manual's tables from the data files that hold each measurement.

    build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json

Every number in the manual comes through here, and every table records the file it was read from, so the
published page and the markdown are two renderings of one JSON. Nothing is fitted in this script; it reads
fits and measurements other tools produced (docs/findings/03-experiments.md says which).
"""
import argparse
import csv
import json
import math
import os
import statistics

D = "docs/reports/data"
MODEL = f"{D}/2026-09-21-horace-aifoundry2/model.json"
DVFS = f"{D}/2026-09-22-dvfs-aifoundry2/dvfs.json"
ABL = f"{D}/2026-09-21-horace-aifoundry2/ablation.json"
HOR = f"{D}/2026-09-21-horace-aifoundry2/horace3.json"
MEMH = f"{D}/2026-09-18-memhier-aifoundry2/energy/results.json"
NOC = [f"{D}/2026-09-18-nocbench-aifoundry2/energy-a/results.json", f"{D}/2026-09-18-nocbench-aifoundry2/energy-b/results.json"]
HOT = f"{D}/2026-09-22-hotline-aifoundry2/hotline.json"
RELAY = f"{D}/2026-09-22-onchip-aifoundry2/onchip.json"
CARDS = f"{D}/2026-09-22-cards/cards-report.json"
ENER = f"{D}/2026-09-23-energy-manual/enercat.json"
CAT = f"{D}/2026-09-23-energy-manual/catalogue.json"
CONFIG = f"{D}/2026-09-22-cards/config.json"
RERUNS = f"{D}/2026-09-23-energy-manual/reruns.json"
UNMET = f"{D}/2026-09-23-energy-manual/unmetered_fit.json"


def j(p):
    return json.load(open(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = j(MODEL)["power"]
    dv = j(DVFS)
    abl = j(ABL)["configs"]
    hor = j(HOR)
    out = {"operating_point": {"mhz": 600, "volts": 0.517, "note": "the point the governor pins a warm card to"}}

    # --- 1. the card at rest ---------------------------------------------------------------------------
    T = list(range(40, 96, 5))
    out["rest"] = {
        "P_fix_w": m["P_fix"], "A_leak_80_w": m["A_leak_at_80"], "T_L_c": m["T_L"], "lambda_80_w_per_c": m["lambda_at_80"],
        "law": "P_idle(T) = P_fix + A_leak_80 * exp((T - 80) / T_L)",
        "curve": [{"T": t, "P_idle": m["P_fix"] + m["A_leak_at_80"] * math.exp((t - 80) / m["T_L"]),
                   "leak_frac": m["A_leak_at_80"] * math.exp((t - 80) / m["T_L"]) /
                                (m["P_fix"] + m["A_leak_at_80"] * math.exp((t - 80) / m["T_L"]))} for t in T],
        "measured_idle": m["idle_curve"],
        "rails_73c": dv["idle_check"]["rails"] | {"board": dv["idle_check"]["board_w"],
                                                   "unsensed": dv["idle_check"]["board_minus_rails"],
                                                   "die_c": dv["idle_check"]["die_c"]},
        "operating_points": dv["operating_points"],
        "leak_fraction": dv["leak_fraction"],
        "source": {"law": MODEL, "rails": DVFS, "points": DVFS},
    }
    try:
        cfg = j(CONFIG)
        out["rest"]["cards"] = cfg
    except Exception:
        pass

    # --- 3. instructions: the tensor unit, from the ablation (80 C, 600 MHz) ---------------------------
    def abl_row(k, label):
        c = abl[k]
        return {"config": k, "label": label, "unit": c["unit"], "per_s": c["per_s"], "over_idle_w": c["dyn"],
                "pj_marginal": c["pj_per_unit_dyn"], "pj_loaded": c["pj_per_unit_board"], "idle_w": c["idle"],
                "minions": c["minions"], "cycles_per_op": c.get("cycles_per_op")}
    out["tensor"] = {
        "rows": [abl_row(f"{t}_{v}", f"TensorFMA {t}, {v}") for t in ("fp32", "fp16", "int8") for v in ("zeros", "ones", "randn")],
        "flips": {"e_fJ": m["e_fJ"], "p_sm_full_chip_w": m["p_sm_full_chip"],
                  "classes": {"ffclk": "register bit clocked", "mult": "net toggle in the multiplier tree",
                              "rest": "other net toggle in the unit", "bus": "operand-word bit toggled outside the unit"}},
        "activity_term_mw_per_minion": dv["activity_term"]["mw_per_minion"],
        "structured": [abl_row(k, k.replace("m_", "TensorFMA fp32, ")) for k in sorted(abl) if k.startswith("m_")],
        "source": {"rows": ABL, "flips": MODEL},
    }
    # Confidence bars for the tensor rows: the ablation ran each configuration twice (p80_sd), and the card
    # transfer of 22 September ran the fp32 patterns on both cards (W over idle, with run-to-run sd).
    try:
        cr = j(CARDS)
        tw = {p["values"]: p for p in cr["patterns"]}
    except Exception:
        tw = {}
    bars = {}
    for t in out["tensor"]["rows"]:
        c = abl[t["config"]]
        vals = {"aifoundry2": [c["dyn"] / c["per_s"] * 1e12]}
        rng = [(c["dyn"] - c["p80_sd"]) / c["per_s"] * 1e12, (c["dyn"] + c["p80_sd"]) / c["per_s"] * 1e12]
        kind, v = t["config"].split("_")
        if kind == "fp32" and v in tw:   # the transfer measured the same pattern on both cards
            vals["aifoundry2"].append(tw[v]["a2"] / c["per_s"] * 1e12)
            vals["aifoundry3"] = [tw[v]["a3"] / c["per_s"] * 1e12]
            rng += [tw[v]["a2"] / c["per_s"] * 1e12, (tw[v]["a3"] - tw[v]["a3_sd"]) / c["per_s"] * 1e12,
                    (tw[v]["a3"] + tw[v]["a3_sd"]) / c["per_s"] * 1e12]
        allv = [x for vs in vals.values() for x in vs]
        bars[t["config"]] = {"mean": statistics.mean(allv), "lo": min(rng), "hi": max(rng), "n": len(allv) + 1,
                             "cards": len(vals), "per_card": {h: {"mean": statistics.mean(vs), "n": len(vs)} for h, vs in vals.items()},
                             "unit": "pJ/MAC", "note": "aifoundry2: ablation (2 runs) and the 22 September transfer; aifoundry3: the transfer"}
    out["tensor"]["bars"] = bars
    out["awake"] = {
        "spin_hart0_1024": abl_row("spin", "8 addi per iteration, hart 0 of 1,024 minions"),
        "spin_hart0_256": abl_row("spin_8", "the same on 256 minions"),
        "source": ABL,
    }

    # --- 4. bytes: reads from memhier, re-measured levels from the ablation -----------------------------
    mh = j(MEMH)["results"]
    out["memory_reads"] = {
        "rows": [{"level": k, "what": v["what"], "gb_s": v["gb_per_s"], "over_idle_w": v["above_idle_w"],
                  "pj_per_byte": v["pj_per_byte_vs_idle"], "pj_vs_spin": v.get("pj_per_byte_vs_spin"),
                  "implied_ghz": v.get("implied_ghz")} for k, v in mh.items() if k != "spin"],
        "spin_over_idle_w": mh["spin"]["above_idle_w"],
        "caveat": "measured on 2026-09-18 with the governor free to move the clock; implied_ghz says where it sat",
        "recheck_600mhz": {"tload_scp_local": abl_row("tload_l2", "tensor load, local scratchpad"),
                           "tload_dram": abl_row("tload_dram", "tensor load, DRAM")},
        "source": {"rows": MEMH, "recheck": ABL},
    }

    # --- 5. bytes between cores: nocbench, two runs averaged ---------------------------------------------
    nocs = [j(p)["results"] for p in NOC]
    keys = [k for k in nocs[0] if k in nocs[1] and k != "spin"]
    out["comm"] = {
        "rows": [{"ring": k, "what": nocs[0][k]["what"], "gb_s": statistics.mean(n[k]["gb_per_s"] for n in nocs),
                  "over_idle_w": statistics.mean(n[k]["above_idle_w"] for n in nocs),
                  "pj_per_byte": statistics.mean(n[k]["pj_per_byte_vs_idle"] for n in nocs),
                  "pj_spread": abs(nocs[0][k]["pj_per_byte_vs_idle"] - nocs[1][k]["pj_per_byte_vs_idle"]) / 2}
                 for k in keys],
        "clock": "600 MHz, 518 mV in every sample of both runs",
        "source": NOC,
    }
    rel = j(RELAY)
    out["relay"] = {"power": rel["power"], "headline": rel["headline"], "source": RELAY}

    # --- 6. synchronisation --------------------------------------------------------------------------------
    hot = j(HOT)
    out["sync"] = {"atomics": hot["power"], "barrier_cycles_chip": hot["context"]["barrier_cycles_chip"],
                   "remote_atomic_latency_cycles": hot["context"]["remote_atomic_latency_cycles"],
                   "bank_service_cycles": hot["context"]["bank_service_cycles"], "source": HOT}

    # --- 3/4 continued: the instruction catalogue and the write paths, from enercat ----------------------
    if os.path.exists(ENER):
        out["enercat"] = j(ENER)
        out["enercat"]["source"] = ENER

    # --- 3.1 / 4.3: the comprehensive catalogue and the fine grain, from three shuffled passes on two cards --
    if os.path.exists(CAT):
        c = j(CAT)
        c.pop("bursts", None)   # per-burst detail stays in catalogue.json; the page needs the summaries
        out["catalogue"] = c | {"source": CAT}

    # --- 5, 6, 4.2: the reruns of the relay, the hot line, the rings and the levels, pooled over passes and cards --
    if os.path.exists(RERUNS):
        out["reruns"] = j(RERUNS) | {"source": RERUNS}

    # --- 4.3: the unmetered remainder attributed, and the DDR rail's droop as a DRAM-power proxy ----------------
    if os.path.exists(UNMET):
        out["unmetered"] = j(UNMET) | {"source": UNMET}

    # --- 8. cards ---------------------------------------------------------------------------------------------
    try:
        out["cards"] = j(CARDS) | {"source": CARDS}
    except Exception:
        pass

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out, "sections:", ", ".join(k for k in out))


if __name__ == "__main__":
    main()
