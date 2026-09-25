#!/usr/bin/env python3
"""Assemble the energy manual's tables from the data files that hold each measurement.

    build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json

Every number in the manual comes through here, and every table records the file it was read from, so the
published page and the markdown are two renderings of one JSON. Nothing is fitted in this script; it reads
fits and measurements other tools produced (docs/findings/03-experiments.md says which). Two things are derived
here rather than read: the mean mesh distance of each ring, from marty1885's shire map in
workloads/nocbench/analyze.py, and the median and largest leakage correction over the catalogue's bursts.
"""
import argparse
import csv
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "workloads", "nocbench"))
from analyze import MARTY, hops  # noqa: E402  marty1885's shire map, the one On-chip communication uses

D = "docs/reports/data"
MODEL = f"{D}/2026-09-21-horace-aifoundry2/model.json"
DVFS = f"{D}/2026-09-22-dvfs-aifoundry2/dvfs.json"
ABL = f"{D}/2026-09-21-horace-aifoundry2/ablation.json"
HOR = f"{D}/2026-09-21-horace-aifoundry2/horace3.json"
MEMH = f"{D}/2026-09-18-memhier-aifoundry2/energy/results.json"
NOC = [f"{D}/2026-09-18-nocbench-aifoundry2/energy-a/results.json", f"{D}/2026-09-18-nocbench-aifoundry2/energy-b/results.json"]
HOT = f"{D}/2026-09-22-hotline-aifoundry2/hotline.json"
BARRIER = f"{D}/2026-09-18-nocbench-aifoundry2/barrier-chip32.jsonl"
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
                                                   "die_c": dv["idle_check"]["die_c"],
                                                   # the sample was taken after this long with no workload
                                                   "hours_idle": dv["idle_check"].get("hours_idle"),
                                                   "samples": dv["idle_check"].get("samples"),
                                                   "board_sd": dv["idle_check"].get("board_sd")},
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
        "spin_hart0_1024": abl_row("spin", "four addi and a branch per iteration, hart 0 of 1,024 minions"),
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
        "recheck_600mhz": {"tload_scp_local": abl_row("tload_l2", "tensor load, L2 cache"),
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
                  "pj_spread": abs(nocs[0][k]["pj_per_byte_vs_idle"] - nocs[1][k]["pj_per_byte_vs_idle"]) / 2,
                  # against the idle measured next to each configuration: the figure On-chip communication publishes
                  "pj_per_byte_local": statistics.mean(n[k]["pj_per_byte_vs_local_idle"] for n in nocs)}
                 for k in keys],
        # Shire IDs do not follow the mesh: the mean, least and greatest number of mesh hops between shire s and
        # shire s + k over all 32 compute shires, on marty1885's map (k from the ring's name; 0 inside a shire).
        "mesh_hops": {k: ({"mean": statistics.mean(hops(s_, (s_ + kk) % 32) for s_ in range(32)),
                           "min": min(hops(s_, (s_ + kk) % 32) for s_ in range(32)),
                           "max": max(hops(s_, (s_ + kk) % 32) for s_ in range(32))}
                          if (kk := int(k[6:].split("-")[0]) if k.startswith("xshire") else 0) else {"mean": 0, "min": 0, "max": 0})
                      for k in keys},
        "hop_map": "marty1885's shire map (workloads/nocbench/analyze.py MARTY), Manhattan distance",
        "clock": "600 MHz, 518 mV in every sample of both runs",
        "source": NOC,
    }
    rel = j(RELAY)
    out["relay"] = {"power": rel["power"], "headline": rel["headline"], "source": RELAY}

    # --- 6. synchronisation --------------------------------------------------------------------------------
    hot = j(HOT)
    # the chip-wide barrier with all 1,024 minions taking part (nocbench, 18 September); barrier-chip1.jsonl is the
    # same barrier with one minion per shire (4,995 cycles), which the hot-line page quotes
    bar = json.loads(open(BARRIER).read().split(" ", 1)[1])
    out["sync"] = {"atomics": hot["power"], "barrier_cycles_chip": int(round(bar["cycles_per_iter_mean"])),
                   "barrier_participants": bar["participants"],
                   "barrier_source": f"{BARRIER}: NOCBENCH cycles_per_iter_mean {bar['cycles_per_iter_mean']}",
                   "remote_atomic_latency_cycles": hot["context"]["remote_atomic_latency_cycles"],
                   "bank_service_cycles": hot["context"]["bank_service_cycles"], "source": HOT}

    # --- 3/4 continued: the instruction catalogue and the write paths, from enercat ----------------------
    if os.path.exists(ENER):
        out["enercat"] = j(ENER)
        out["enercat"]["source"] = ENER

    # --- 3.1 / 4.3: the comprehensive catalogue and the fine grain, from three shuffled passes on two cards --
    if os.path.exists(CAT):
        c = j(CAT)
        bursts = c.pop("bursts", None) or {}   # per-burst detail stays in catalogue.json; the page needs the summaries
        # the leakage correction each burst received (section 9): its median and largest size, per card
        lc = {h: sorted(abs(b["leak_correction_w"]) for b in bs) for h, bs in bursts.items()}
        c["leak_correction"] = {h: {"median_w": statistics.median(v), "max_w": v[-1], "bursts": len(v)} for h, v in lc.items() if v}
        # the sampler's latency per configuration is a record of the meter, not an energy: it stays in catalogue.json
        for card in c["cards"].values():
            for row in card["summary"].values():
                row.pop("sampler_median_ms", None)
                row.pop("sampler_max_ms", None)
        out["catalogue"] = c | {"source": CAT}

    # --- 5, 6, 4.2: the reruns of the relay, the hot line, the rings and the levels, pooled over passes and cards --
    if os.path.exists(RERUNS):
        out["reruns"] = j(RERUNS) | {"source": RERUNS}

    # --- 4.3: the unmetered remainder attributed, and the DDR rail's droop as a DRAM-power proxy ----------------
    if os.path.exists(UNMET):
        u = j(UNMET)
        for blk in (u.get("aifoundry2", {}), u.get("aifoundry3", {}), u.get("ddr_droop", {})):
            blk.pop("per_config", None)          # the per-configuration rows are the hub's charts' (unmetered_fit.json)
            blk.pop("per_config_fields", None)
        out["unmetered"] = u | {"source": UNMET}

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
