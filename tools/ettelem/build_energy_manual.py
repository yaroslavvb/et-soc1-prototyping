#!/usr/bin/env python3
"""Assemble the energy manual's tables from the data files that hold each measurement.

    build_energy_manual.py --out docs/reports/data/2026-09-23-energy-manual/manual.json

Every number in the manual comes through here, and every table records the file it was read from, so the
published page and the markdown are two renderings of one JSON. Nothing is fitted in this script; it reads
fits and measurements other tools produced (docs/findings/03-experiments.md says which), except the idle law's
refits with its e-folding held (rest.profile over a window of e-foldings on aifoundry2's bins; rest.per_card, each other
card's own law on its version-3 idle bins). Two more things are derived here rather than read: the mean mesh distance of each ring, from marty1885's shire map in
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
# The version-3 claims check (26 September 2026, three cards): its results files, read as they are
V3 = f"{D}/2026-09-25-claims-v3/results"
ABLA_RUNS = f"{V3}/abla.runs.json"                 # V3-ABL-A: the tensor unit, the integer loop, the active minions
CARD_ORDER = ["aifoundry2", "aifoundry3", "aifoundry1-c1", "aifoundry1-c0"]   # the pages' card registry order


def in_order(cards):
    return sorted(cards, key=lambda c: CARD_ORDER.index(c) if c in CARD_ORDER else len(CARD_ORDER))


def item(results, name, part=None):
    """One item of a version-3 results file (a list of items, or a dict with "items")."""
    its = results if isinstance(results, list) else results["items"]
    return next(i for i in its if i["item"] == name and (part is None or i.get("part") == part))


def j(p):
    return json.load(open(p))


def v3_block(m):
    """The version-3 check's results, as far as the manual quotes them, per card. Every value is read from
    docs/reports/data/2026-09-25-claims-v3/results/<exp>.json (the reducers' own output); nothing is refitted here
    except each card's idle bins, which are the law plus the item's own per-bin residuals."""
    r3 = lambda v: None if v is None else round(float(v), 4)
    law = lambda t: m["P_fix"] + m["A_leak_at_80"] * math.exp((t - 80) / m["T_L"])
    ci = lambda d: {"mean": r3(d.get("mean")), "ci99": [r3(x) for x in d.get("ci99", [None, None])], "n": d.get("n")}
    out = {"date": "2026-09-26", "source": V3,
           "record": "https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-09-25-claims-v3"}

    # ---- idle (V3-IDLE): three heat-and-cool cycles per card, every sample at 600 MHz
    idl = j(f"{V3}/idle.json")
    I = {i["item"]: i for i in idl["items"]}
    clocks = {c: {"mhz": v["used_mhz"], "mv": v["minion_mv_median_at_used"], "firmware": v["firmware"]}
              for c, v in idl["idle_clocks"].items()}
    bins = {}
    for c in in_order(idl["cards"]):
        pc_b, pc_a = I["IDLE-b"]["per_card"].get(c, {}), I["IDLE-a"]["per_card"].get(c, {})
        if pc_a.get("cycles"):          # every bin of every kept cycle (IDLE-a: bins 51 C up to the cycle's top)
            acc = {}
            for cy in pc_a["cycles"]:
                for t, v in cy["resid_by_bin"].items():
                    acc.setdefault(int(t), []).append(v)
            rows = [(t, statistics.fmean(v), len(v)) for t, v in sorted(acc.items())]
            rule = "IDLE-a: each kept cycle's whole-degree bins, the residual to the law averaged over cycles"
        elif pc_b.get("bins"):          # aifoundry2: IDLE-b's bins (each cycle's first and last bin left out, A1)
            rows = [(int(t), v["mean"], v["n_cycles"]) for t, v in sorted(pc_b["bins"].items(), key=lambda kv: int(kv[0]))]
            rule = "IDLE-b: whole-degree bins, each cycle's first and last left out (amendment A1), averaged over cycles"
        else:
            continue
        bins[c] = {"bins": [{"T": t, "W": r3(law(t) + v), "resid": r3(v), "cycles": n} for t, v, n in rows], "rule": rule}
    a_pc, b_pc, c_pc = I["IDLE-a"]["per_card"], I["IDLE-b"]["per_card"], I["IDLE-c"]["per_card"]
    d_pc, e_pc, f_pc, k_pc = (I[k]["per_card"] for k in ("IDLE-d", "IDLE-e", "IDLE-f", "IDLE-k"))
    out["idle"] = {
        "clocks": clocks, "bins": bins,
        "law_residual": {c: ci(a_pc[c]["offset_W"]) | {"slope_w_per_c": ci(a_pc[c]["resid_slope_W_per_C"]),
                                                       "T": [min(b["T"] for b in bins[c]["bins"]), max(b["T"] for b in bins[c]["bins"])]}
                         for c in a_pc if a_pc[c].get("offset_W")},
        "law_residual_a2": ci(b_pc["aifoundry2"]["info_cycle_offset_W"]) | {
            "bins_78_82": {t: {"mean": r3(v["mean"]), "ci99": [r3(x) for x in v["ci99"]]} for t, v in b_pc["aifoundry2"]["bins"].items()
                           if v["testable"]},
            "T": [min(min(v) for v in b_pc["aifoundry2"]["cycles_T_range"].values()), max(max(v) for v in b_pc["aifoundry2"]["cycles_T_range"].values())]},
        "unsensed_slope_74_88": {c: ci(v["unsensed_slope_W_per_C_74_88"]) for c, v in c_pc.items() if v.get("unsensed_slope_W_per_C_74_88")},
        "unsensed_slope_a3_cycles": c_pc["aifoundry3"].get("info_unsensed_slope_per_cycle"),
        "rails_slope_75_80": {c: ci(v["info_metered_rail_slope_W_per_C_75_80"]) for c, v in c_pc.items() if v.get("info_metered_rail_slope_W_per_C_75_80")},
        "split_73c": {c: {k: ci(x) for k, x in v["components_W"].items()} | {"board": ci(v["info_board_W"])}
                      for c, v in d_pc.items() if v.get("components_W")},
        "sram_slope": {c: ci(v["sram_slope_W_per_C"]) | {
            "excess_over_a2_law": [r3(min(x["mean"] for x in v["excess_over_a2_sram_law_by_bin"].values() if x["testable"])),
                                   r3(max(x["mean"] for x in v["excess_over_a2_sram_law_by_bin"].values() if x["testable"]))],
            "T": [min(int(t) for t, x in v["excess_over_a2_sram_law_by_bin"].items() if x["testable"]),
                  max(int(t) for t, x in v["excess_over_a2_sram_law_by_bin"].items() if x["testable"])]}
            for c, v in e_pc.items() if v.get("sram_slope_W_per_C")},
        "sram_law_a2_registered": idl["constants"]["sram_law_a2"],
        "unsensed_70c": {c: ci(v["unsensed_70C_W"]) for c, v in f_pc.items() if v.get("unsensed_70C_W")},
        "unsensed_own": {c: ci(v["own_temperature"]["unsensed_W_mean_over_own_bins"]) | {"T": v["own_temperature"]["T_range"]}
                         for c, v in f_pc.items() if v.get("own_temperature")},
        "cooling": {c: {"best_T_L": [x["best_T_L"] for x in v["per_cycle"]],
                        "share_range": [r3(min(x["share_range"][0] for x in v["per_cycle"])), r3(max(x["share_range"][1] for x in v["per_cycle"]))],
                        "law_resid_70_85": ci(v["law_resid_70_85_W"])} for c, v in k_pc.items() if v.get("per_cycle")},
        "heater_top_c": {c: v.get("tmax_per_cycle") for c, v in I["IDLE-0"]["per_card"].items() if v.get("tmax_per_cycle")},
        "outcomes": {k: {"registered": I[k]["outcome"], "all_cards": I[k]["all_cards"]["outcome"]} for k in I},
    }

    # ---- the catalogue across cards (V3-CAT and V3-CATFULL)
    cat = j(f"{V3}/cat.json")
    C = {i["item"]: i for i in cat["items"]}
    cf = j(f"{V3}/catfull.json")
    F = {i["item"]: i for i in cf["items"]}
    gap = F["CF-GAP"]
    out["catalogue"] = {
        "gap_a3_a2": {k: r3(gap["test"][k]) for k in ("ratio", "lo", "hi")},
        "gap_vs_a2": {c: ({k: r3(v["vs_aifoundry2"][k]) for k in ("ratio", "lo", "hi")} if v.get("vs_aifoundry2") else None)
                      for c, v in gap["per_card"].items() if v.get("present", True) and c != "aifoundry2"},
        "committed_23sep": cf["ratios"]["committed_cross_card"],
        "vs_committed_23sep": cf["vs_committed_23sep"],
        "rep_pct": {c: {"median": r3(v["median_pct"]), "p90": r3(v["p90_pct"])} for c, v in F["CF-REP"]["per_card"].items() if v.get("median_pct") is not None},
        "temperature": {c: {"beta_pct_per_c": {k: r3(v["beta_pct_per_c"][k]) for k in ("beta", "lo", "hi")}, "dT_c": r3(v["dT_c"]),
                            "hot_c": r3(statistics.fmean(x["die_c"] for x in v["hot"])), "cool_c": r3(statistics.fmean(x["die_c"] for x in v["cool"])),
                            "decision": v["decision"]} for c, v in C["CAT-a"]["per_card"].items()},
        "cool_a3_warm_a2": {k: r3(C["CAT-b"]["per_card"]["ratio"][k]) for k in ("ratio", "lo", "hi")},
        "a1c1_warm_a2_warm": {k: r3(C["CAT-b"]["per_card"]["aifoundry1-c1"]["ratio_vs_aifoundry2_W"][k]) for k in ("ratio", "lo", "hi")},
        "dram_rows": {c: {o: {"anova_p": r3(v[o]["anova"]["p"]), "rows_minus_tload": {k: r3(v[o]["rows_minus_tload"][k]) for k in ("diff", "lo", "hi")},
                              "pct": r3(100 * v[o]["excess_over_tload"]), "decision": v[o]["decision"]} for o in ("zeros", "random")}
                      for c, v in C["CAT-c"]["per_card"].items()},
        "dram_write_read": {c: {"diff": r3(v["tstore_minus_tload"]["diff"]), "lo": r3(v["tstore_minus_tload"]["lo"]),
                                "hi": r3(v["tstore_minus_tload"]["hi"]), "pct": r3(v["pct"])} for c, v in C["CAT-e"]["per_card"].items()},
        "fill_vs_tload": {c: {"ratio": r3(v["ratio"]), "ci99": [r3(x) for x in v["ratio_ci99_approx"]], "decision": v["decision"]}
                          for c, v in C["CAT-f"]["per_card"].items()},
        "outcomes": {k: {"registered": C[k]["outcome"], "all_cards": C[k]["all_cards"]["outcome"]} for k in C}
                    | {k: {"registered": F[k]["outcome"], "all_cards": F[k]["all_cards"]["outcome"]} for k in F},
    }

    # ---- the tensor unit and the awake core (V3-ABL-A); switching hot against cool (X5)
    ab = j(f"{V3}/abla.json")
    A = {i["item"]: i for i in ab}
    def sub(itm, card, name):
        pc = A[itm]["per_card"][card]
        subs = pc.get("subtests") or (pc.get("vs_aifoundry2_values") or {}).get("subtests") or []
        return next((x for x in subs if x["test"] == name), None)
    t7 = {c: {"ratio_1024_256": r3(sub("ABL-T7", c, "per-minion switching 1024 / 256 in [0.98, 1.10]")["ci"]["point"]),
              "ci": [r3(sub("ABL-T7", c, "per-minion switching 1024 / 256 in [0.98, 1.10]")["ci"][k]) for k in ("lo", "hi")],
              "intercept_w": r3(next(x for x in A["ABL-T7"]["per_card"][c]["subtests"] if x["kind"] == "bound")["fit"]["intercept"])}
          for c in A["ABL-T7"]["per_card"]}
    t6 = {c: {k: r3(sub("ABL-T6", c, "spin over idle")["ci"][k]) for k in ("mean", "lo", "hi")} for c in A["ABL-T6"]["per_card"]}
    out["tensor"] = {"spin_w": t6, "active_minions": t7,
                     "outcomes": {k: {"registered": A[k]["outcome"], "all_cards": A[k]["all_cards"]["outcome"]} for k in A},
                     "cycles_per_op": {c: v.get("values_by_type") for c, v in A["ABL-EM4c"]["per_card"].items()}}
    x5 = j(f"{V3}/x5.json")[0]
    out["x5"] = {c: {t: {"hot_minus_cool_w": r3(v["tests"][t]["ci_hot_minus_cool"]["point"]),
                         "ci": [r3(v["tests"][t]["ci_hot_minus_cool"]["lo"]), r3(v["tests"][t]["ci_hot_minus_cool"]["hi"])]}
                     for t in ("fp32_randn", "fp32_uniform") if t in v.get("tests", {})}
                 | {"launch_c": {arm: r3(v["launch_temperatures"][arm]["measured_launch_c"]["mean"]) for arm in ("hi", "lo")}
                    if v.get("launch_temperatures") else None}
                 for c, v in x5["per_card"].items()} | {"outcome": x5["outcome"], "all_cards": x5["all_cards"]["outcome"]}

    # ---- the board-power meter (V3-TEL, TEL-S): the refresh period under the manual's 10 Hz sampler and a lighter poller
    tel = j(f"{V3}/tel.json")
    ts = next(i for i in tel["items"] if i["item"] == "TEL-S")
    out["refresh_ms"] = {c: {"sampler_10hz": r3(statistics.fmean(p["P_H"] for p in v["passes"])),
                             "sampler_10hz_range": [min(p["P_H"] for p in v["passes"]), max(p["P_H"] for p in v["passes"])],
                             "light_poller": [min(p["P_L"] for p in v["passes"]), max(p["P_L"] for p in v["passes"])],
                             "lengthens": v["interval"], "passes": len(v["passes"])} for c, v in ts["per_card"].items()}

    # ---- rings, levels and the relay (V3-RL): the items the manual quotes
    rl = j(f"{V3}/rl.json")
    R = {(i["item"], i.get("part")): i for i in rl["items"]}
    get = lambda name, part: R[(name, part)]
    # each card's configuration as `ettelem config` read it at the start of its first V3-RL pass (TDP, power state, mV)
    out["card_state"] = {c: ps[0]["card_state"][0]["config"] for c, ps in rl["passes"].items() if ps and ps[0].get("card_state")}
    out["rl"] = {
        "mesh_slope": get("RL-a", "mesh slope (five 1 KB xshire rings)")["all_cards"]["per_card_mean"]
                      | {"pooled": get("RL-a", "mesh slope (five 1 KB xshire rings)")["all_cards"]["pooled"]},
        "exit_step": {c: {"mean": r3(v["mean"]), "ci99": [r3(x) for x in v["ci99"]]} for c, v in get("RL-b", "leaving-the-shire step, aifoundry2")["per_card"].items()},
        "small_messages": {part: {c: {"mean": r3(v["mean"]), "ci99": [r3(x) for x in v["ci99"]]} for c, v in get("RL-c", part)["per_card"].items()}
                           for part in ("shire-c4 - shire", "xshire1-c4 - xshire1")},
        "relay_ratio": get("RL-d", "relay DRAM / next shire")["all_cards"]["per_card_mean"] | {"pooled": get("RL-d", "relay DRAM / next shire")["all_cards"]["pooled"]},
        # RL-f (energy-manual-153) is being re-reduced with its --low-edge input (coordinator, 26 September): read defensively
        "relay_scp_low_edge": {c: {"measured": ci(v["measured"]) if v.get("measured") else None, "low_edge": r3(v.get("low_edge_mean"))}
                               for c, v in (R.get(("RL-f", "relay own scratchpad vs bracket low edge")) or {"per_card": {}})["per_card"].items()},
        "scp_by_contents": {c: {o: ci(v[o]) for o in ("zeros", "random")} for c, v in get("RL-h", "scp-local level follows the prefill")["per_card"].items()},
        "outcomes": {f"{k[0]} {k[1]}": {"registered": v["outcome"], "all_cards": (v.get("all_cards") or {}).get("outcome")} for k, v in R.items()
                     if k[0] in ("RL-a", "RL-b", "RL-c", "RL-d", "RL-f", "RL-g", "RL-h")},
    }
    return out


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
    # How well the idle bins pin the law down. The fit's idle samples cover 64-67 and 81-88 C and fit equally well
    # (rms within 0.007 W) with the leakage e-folding anywhere from 30 to 45 C (the version-3 check,
    # docs/reports/data/2026-09-25-claims-v3/: horace-lowpower-084/087, dvfs-05; decision D3), so the split into
    # fixed and leakage is given as the range over that window, and the slope at 80 C, which barely moves, is the
    # measured number. Each fit here is the law refitted to model.json's whole-degree idle bins, weighted by their
    # sample counts, with T_L held; at T_L = 36 C it reproduces the published law to 0.05 W.
    tl_window = (30, 45)
    bins = m["idle_curve"]
    wsum = sum(b["n"] for b in bins)
    fits = []
    for tl in range(tl_window[0], tl_window[1] + 1):
        xs = [math.exp((b["T"] - 80) / tl) for b in bins]
        mx = sum(b["n"] * x for b, x in zip(bins, xs)) / wsum
        my = sum(b["n"] * b["P"] for b in bins) / wsum
        A = (sum(b["n"] * (x - mx) * (b["P"] - my) for b, x in zip(bins, xs)) /
             sum(b["n"] * (x - mx) ** 2 for b, x in zip(bins, xs)))
        fits.append({"T_L_c": tl, "P_fix_w": my - A * mx, "A_leak_80_w": A, "lambda_80_w_per_c": A / tl})
    span = lambda k: [min(f_[k] for f_ in fits), max(f_[k] for f_ in fits)]
    def share(f_, t):
        lk = f_["A_leak_80_w"] * math.exp((t - 80) / f_["T_L_c"])
        return lk / (f_["P_fix_w"] + lk)
    def idle(f_, t):
        return f_["P_fix_w"] + f_["A_leak_80_w"] * math.exp((t - 80) / f_["T_L_c"])
    out["rest"]["profile"] = {
        "T_L_window_c": list(tl_window), "P_fix_w": span("P_fix_w"), "A_leak_80_w": span("A_leak_80_w"),
        "lambda_80_w_per_c": span("lambda_80_w_per_c"),
        "doubling_c": [tl_window[0] * math.log(2), tl_window[1] * math.log(2)],
        "leak_frac": {str(t): [min(share(f_, t) for f_ in fits), max(share(f_, t) for f_ in fits)] for t in T},
        # how far the idle total itself moves between those fits, 45-95 C (the calculator's range)
        "idle_spread_w_45_95": max(max(idle(f_, t) for f_ in fits) - min(idle(f_, t) for f_ in fits) for t in range(45, 96)),
        "fits": fits,
        "rule": "P = P_fix + A_leak_80 * exp((T - 80) / T_L) refitted with T_L held, weighted least squares on model.json idle_curve (weights n)",
        "source": MODEL,
    }

    # --- 3. instructions: the tensor unit. Until 25 September the rows were the 21 September ablation (two runs on
    # aifoundry2) and the bars added the 22 September card transfer (fp32 on both cards). Since 26 September both come
    # from the version-3 check's V3-ABL-A: every tensor configuration four times on each of three cards, each run 7 s
    # from a set launch temperature (80 C on the governor-free aifoundry2 and aifoundry1-c1, 55-58 C on the pinned
    # aifoundry3), the registered "switching" (board power over the idle before the launch, early samples corrected for
    # the die's warming) per run. rows: aifoundry2's means (the idle law's card); bars: every run on every card. -------
    def abl_row(k, label):
        c = abl[k]
        return {"config": k, "label": label, "unit": c["unit"], "per_s": c["per_s"], "over_idle_w": c["dyn"],
                "pj_marginal": c["pj_per_unit_dyn"], "pj_loaded": c["pj_per_unit_board"], "idle_w": c["idle"],
                "minions": c["minions"], "cycles_per_op": c.get("cycles_per_op")}
    ar = j(ABLA_RUNS)
    arun = {c: [r for r in ar["runs"][c] if r.get("kept") and r["pass"] in ar["passes_used"][c]] for c in in_order(ar["runs"])}
    fm = statistics.fmean
    def v3_runs(card, cfg):
        return [r for r in arun.get(card, []) if r["config"] == cfg]
    def v3_row(k, label, card="aifoundry2"):
        rs = v3_runs(card, k)
        return {"config": k, "label": label, "unit": rs[0]["unit"], "per_s": fm(r["per_s"] for r in rs),
                "over_idle_w": fm(r["switching"] for r in rs),
                "pj_marginal": fm(r["switching"] / r["per_s"] * 1e12 for r in rs),
                "pj_loaded": fm((r["p_before"] + r["switching"]) / r["per_s"] * 1e12 for r in rs),
                "idle_w": fm(r["p_before"] for r in rs), "minions": rs[0]["minions"],
                "cycles_per_op": fm(r["cycles_per_op"] for r in rs) if rs[0].get("cycles_per_op") else None,
                "runs": len(rs), "launch_c": fm(r["t_launch"] for r in rs), "card": card}
    def v3_bar(k, per_unit=True):
        """pJ per unit (per_unit) or W over idle, pooled over every kept run on every card, with each card's mean ± se."""
        vals = {c: [(r["switching"] / r["per_s"] * 1e12) if per_unit else r["switching"] for r in v3_runs(c, k)] for c in arun}
        vals = {c: v for c, v in vals.items() if v}
        allv = [x for v in vals.values() for x in v]
        return {"mean": fm(allv), "lo": min(allv), "hi": max(allv), "n": len(allv), "cards": len(vals),
                "per_card": {c: {"mean": fm(v), "se": (statistics.stdev(v) / math.sqrt(len(v))) if len(v) > 1 else 0.0,
                                 "n": len(v)} for c, v in vals.items()},
                "unit": ("pJ/" + ("MAC" if k != "spin" else "instruction")) if per_unit else "W"}
    out["tensor"] = {
        "rows": [v3_row(f"{t}_{v}", f"TensorFMA {t}, {v}") for t in ("fp32", "fp16", "int8") for v in ("zeros", "ones", "randn")],
        "launch_c": {c: fm(r["t_launch"] for r in arun[c] if r["config"] != "spin") for c in arun},
        # every card's own means per configuration: idle before the launch, W over it, launch temperature (section 7.1)
        "per_card_rows": {c: {k: {"idle_w": fm(r["p_before"] for r in v3_runs(c, k)), "over_idle_w": fm(r["switching"] for r in v3_runs(c, k)),
                                  "launch_c": fm(r["t_launch"] for r in v3_runs(c, k)), "runs": len(v3_runs(c, k))}
                              for k in (f"{t}_{v}" for t in ("fp32", "fp16", "int8") for v in ("zeros", "ones", "randn")) if v3_runs(c, k)}
                          for c in arun},
        "idle_w_at_launch": {c: fm(r["p_before"] for r in arun[c]) for c in arun},
        "minion_mv": {c: fm(r["busy_mv"] for r in arun[c] if r.get("busy_mv")) for c in arun},
        "flips": {"e_fJ": m["e_fJ"], "p_sm_full_chip_w": m["p_sm_full_chip"],
                  "classes": {"ffclk": "register bit clocked", "mult": "net toggle in the multiplier tree",
                              "rest": "other net toggle in the unit", "bus": "operand-word bit toggled outside the unit"}},
        "activity_term_mw_per_minion": dv["activity_term"]["mw_per_minion"],
        # the active-minion series per card (mW per minion over idle at 256, 512 and 1,024 minions; ABL-T7)
        "activity_v3_mw_per_minion": {c: {str(n): fm(r["switching"] for r in v3_runs(c, k)) / n * 1e3
                                          for k, n in (("fp32_randn_8", 256), ("fp32_randn_16", 512), ("fp32_randn", 1024))
                                          if v3_runs(c, k)} for c in arun},
        "structured": [abl_row(k, k.replace("m_", "TensorFMA fp32, ")) for k in sorted(abl) if k.startswith("m_")],
        "source": {"rows": ABLA_RUNS, "bars": ABLA_RUNS, "structured": ABL, "flips": MODEL, "activity_term": DVFS},
        "runs_per_card": {c: len(ar["passes_used"][c]) for c in arun},
    }
    # AMENDMENTS.md C2 (26 September, after the data): the registered switching is referenced to a fixed launch temperature
    # per card (abla.runs.json params_by_card: 80.9 C for aifoundry2 and aifoundry1-c1, 55.8 C for aifoundry3) while each
    # run's idle is read at its actual launch, so every run is off by leak x (t_launch - reference). The registered values
    # stay in rows and bars; this block gives each card's offset and each configuration's mean at the actual launch
    # (switching + leak x (t_launch - reference)), for the text that shows or compares cards' switching.
    # C2 as revised the same day: t_launch is the die sensor's whole-degree reading, while the references are thermal-model
    # temperatures at launches made on a downward step of the reading (the 21 September thermal network puts the die at
    # 80.96 C when the reading first shows 80). If each version-3 launch was likewise on a downward step, the die was at
    # the reading + STEP; the *_step fields give that reading, the others take the reading as the die temperature.
    STEP = 0.96
    PB = ar.get("params_by_card") or {}
    out["tensor"]["launch_offset"] = {}
    for c in arun:
        if c not in PB:
            continue
        pb = PB[c]
        off = lambda r, pb=pb, s=0.0: pb["leak"] * (r["t_launch"] + s - pb["launch"])
        os_ = [off(r) for r in arun[c]]
        oss = [off(r, s=STEP) for r in arun[c]]
        cfgs = sorted({r["config"] for r in arun[c]})
        out["tensor"]["launch_offset"][c] = {
            "leak_w_per_c": pb["leak"], "ref_c": pb["launch"], "launch_c": fm(r["t_launch"] for r in arun[c]),
            "mean_w": fm(os_), "range_w": [min(os_), max(os_)], "runs": len(os_),
            "at_launch_w": {k: fm(r["switching"] + off(r) for r in v3_runs(c, k)) for k in cfgs},
            "step_c": STEP, "mean_w_step": fm(oss), "range_w_step": [min(oss), max(oss)],
            "at_launch_step_w": {k: fm(r["switching"] + off(r, s=STEP) for r in v3_runs(c, k)) for k in cfgs}}
    out["tensor"]["launch_offset_note"] = ("AMENDMENTS.md C2 (revised): a per-run value at the die temperature of its launch is switching + "
                                           "leak x (die - reference), with die = the whole-degree reading t_launch (at_launch_w) or "
                                           "t_launch + step_c, a launch on a downward step of the reading as the references' were "
                                           "(at_launch_step_w); the registered values and outcomes stand")
    out["tensor"]["bars"] = {t["config"]: v3_bar(t["config"]) for t in out["tensor"]["rows"]}
    # the transfer of 22 September (fp32 on both cards, one session) stays as history: cards-report.json, section 8
    out["awake"] = {
        # aifoundry2's four V3-ABL-A runs (the 21 September ablation's two runs gave 1.46 W, 8.1 pJ)
        "spin_hart0_1024": v3_row("spin", "four addi and a branch per iteration, hart 0 of 1,024 minions"),
        "spin_hart0_256": abl_row("spin_8", "the same on 256 minions"),
        # the same loop on every card: W over idle and pJ per instruction, each card's mean ± se over its runs (ABL-T6)
        "spin_v3_w": v3_bar("spin", per_unit=False), "spin_v3_pj": v3_bar("spin"),
        "source": {"spin_hart0_1024": ABLA_RUNS, "spin_hart0_256": ABL, "spin_v3": ABLA_RUNS},
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
        # Per card, from the idle stretches that bracket every burst (sections 1 and 8): the unsensed remainder
        # (board idle less the three rails' idle), the idle's residual against the section 1 law at the same die
        # temperature, and the die temperature the bursts ran at. Pass means, so the unit is the pass.
        law = lambda t: m["P_fix"] + m["A_leak_at_80"] * math.exp((t - 80) / m["T_L"])
        def per_pass(bs, fn):
            by = {}
            for b in bs:
                by.setdefault(b["pass"], []).append(fn(b))
            pm = [statistics.fmean(v) for _, v in sorted(by.items())]
            return {"mean": statistics.fmean(pm), "passes": pm}
        c["idle_unsensed"] = {h: per_pass(bs, lambda b: b["p_idle_w"] - b["minion_idle_w"] - b["sram_idle_w"] - b["noc_idle_w"])
                              | {"die_c": [min(b["die_c_idle"] for b in bs), max(b["die_c_idle"] for b in bs)]}
                              for h, bs in bursts.items() if bs}
        c["idle_law_residual"] = {h: per_pass(bs, lambda b: b["p_idle_w"] - law(b["die_c_idle"]))
                                  | {"die_c": [min(b["die_c_idle"] for b in bs), max(b["die_c_idle"] for b in bs)]}
                                  for h, bs in bursts.items() if bs}
        c["die_c_busy_median"] = {h: statistics.median(b["die_c_busy"] for b in bs) for h, bs in bursts.items() if bs}
        # the sampler's own latency over each burst (section 9): its median over the bursts, the slowest burst, and how
        # many bursts ran over 60 ms (kept, as analyze_catalogue.py keeps them)
        c["sampler"] = {h: {"median_ms": statistics.median(b["sampler_median_ms"] for b in bs),
                            "max_ms": max(b["sampler_median_ms"] for b in bs),
                            "over_60ms": sum(1 for b in bs if b["sampler_median_ms"] > 60), "bursts": len(bs)}
                        for h, bs in bursts.items() if bs}
        # each card's idle split by rail in the same idle stretches (pass means): which component is the largest
        c["idle_split"] = {h: {k: per_pass(bs, fn)["mean"] for k, fn in (
            ("minion", lambda b: b["minion_idle_w"]), ("sram", lambda b: b["sram_idle_w"]), ("noc", lambda b: b["noc_idle_w"]),
            ("unsensed", lambda b: b["p_idle_w"] - b["minion_idle_w"] - b["sram_idle_w"] - b["noc_idle_w"]),
            ("board", lambda b: b["p_idle_w"]))} for h, bs in bursts.items() if bs}
        # every card against aifoundry2, configuration by configuration (analyze_catalogue.py's cross_card rule: the
        # pJ/B mean where the entry moves bytes, else the pJ/op mean): median and 10th-90th percentile per card
        import numpy as np
        ref = c["cards"].get("aifoundry2", {}).get("summary", {})
        val = lambda e: e["pj_per_byte"] or e["pj_per_op"]
        c["cross_cards"] = {}
        for h in in_order(c["cards"]):
            if h == "aifoundry2" or not ref:
                continue
            sm = c["cards"][h]["summary"]
            r = [val(sm[k])["mean"] / val(ref[k])["mean"] for k in ref if k in sm and val(ref[k]) and val(sm[k]) and val(ref[k])["mean"]]
            c["cross_cards"][h] = {"vs": "aifoundry2", "median": float(np.median(r)), "p10": float(np.percentile(r, 10)),
                                   "p90": float(np.percentile(r, 90)), "n": len(r)}
        # Which entries depart from a card's common scale against aifoundry2 beyond the noise of three passes: per entry, a
        # Welch interval on the log values (the card's passes less its median log ratio, against aifoundry2's passes), at
        # 99% with a Bonferroni correction over the entries (the t quantiles of tools/claims-v3/catfull/cflib.py)
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "claims-v3", "catfull"))
        import cflib
        bval = lambda b: b.get("value", b["pj_per_byte"] if b["bytes"] else b["pj_per_op"])
        vals = {h: {} for h in bursts}
        for h, bs in bursts.items():
            for b in bs:
                vals[h].setdefault(b["cfg"], []).append(bval(b))
        c["scale_outliers"] = {}
        for h in in_order(vals):
            if h == "aifoundry2" or "aifoundry2" not in vals:
                continue
            r2 = vals["aifoundry2"]
            ok = [k for k in r2 if k in vals[h] and min(r2[k]) > 0 and min(vals[h][k]) > 0]
            med = statistics.median(math.log(statistics.fmean(vals[h][k]) / statistics.fmean(r2[k])) for k in ok)
            out_ = []
            for k in ok:
                w = cflib.welch([math.log(v) - med for v in vals[h][k]], [math.log(v) for v in r2[k]], conf=1 - 0.01 / len(ok))
                if w and (w["lo"] > 0 or w["hi"] < 0):
                    out_.append({"cfg": k, "vs_scale": math.exp(w["diff"])})
            c["scale_outliers"][h] = {"entries": len(ok), "scale": math.exp(med), "outliers": out_,
                                      "rule": "Welch on log values, 99% with Bonferroni over the entries, against the card's median log ratio"}
        # each card's three metered rails' voltages over the catalogue (the PMIC's reading, sp.<rail>_mv average): the median
        # over every telemetry sample of its V3-CATFULL blocks (fit_unmetered.catalogue_telemetry)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import gzip
        import fit_unmetered
        c["rail_mv"] = {}
        for h in in_order(c["cards"]):
            vs = {k: [] for k in ("minion", "sram", "noc")}
            for f in fit_unmetered.catalogue_telemetry(h):
                for line in gzip.open(f, "rt"):
                    if line.startswith("{"):
                        sp_ = json.loads(line)["sp"]
                        for k in vs:
                            vs[k].append(sp_[k + "_mv"][0])
            if vs["sram"]:
                c["rail_mv"][h] = {k: statistics.median(v) for k, v in vs.items()} | {"samples": len(vs["sram"])}
        c["cards"] = {h: c["cards"][h] for h in in_order(c["cards"])}
        # the pooled sets catfull/reduce.py adds beside "combined" (every card's idle is at 600 MHz here, so
        # combined_600idle equals combined; combined_registered is aifoundry2 + aifoundry3): catalogue.json only
        c.pop("combined_600idle", None)
        c.pop("combined_registered", None)
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
        for blk in u.values():
            blk.pop("per_config", None)          # the per-configuration rows are the hub's charts' (unmetered_fit.json)
            blk.pop("per_config_fields", None)
        out["unmetered"] = u | {"source": UNMET}

    # --- 8. cards ---------------------------------------------------------------------------------------------
    try:
        out["cards"] = j(CARDS) | {"source": CARDS}
    except Exception:
        pass

    # --- the version-3 check (26 September 2026): what it measured that the manual states per card ----------------
    out["v3"] = v3_block(m)
    # Each other card's own idle law, for pricing on that card (section 7.1): the law's form with its e-folding held at
    # section 1's 36 C, refitted by weighted least squares (weights: the kept cycles in each bin) to that card's idle bins
    # of the version-3 cycles. Like section 1's law it pins the total and the slope, not the split into fixed and leakage.
    per_card = {}
    for c, b in out["v3"]["idle"]["bins"].items():
        if c == "aifoundry2":
            continue                       # the section 1 law is aifoundry2's
        pts = [(x["T"], x["W"], x["cycles"]) for x in b["bins"]]
        tl = m["T_L"]
        xs = [math.exp((t - 80) / tl) for t, _, _ in pts]
        wsum = sum(n for _, _, n in pts)
        mx = sum(n * x for (_, _, n), x in zip(pts, xs)) / wsum
        my = sum(n * w for _, w, n in pts) / wsum
        A = sum(n * (x - mx) * (w - my) for (_, w, n), x in zip(pts, xs)) / sum(n * (x - mx) ** 2 for (_, _, n), x in zip(pts, xs))
        P = my - A * mx
        rms = math.sqrt(sum(n * (w - P - A * x) ** 2 for (_, w, n), x in zip(pts, xs)) / wsum)
        per_card[c] = {"P_fix_w": P, "A_leak_80_w": A, "T_L_c": tl, "lambda_80_w_per_c": A / tl, "rms_w": rms,
                       "T": [min(t for t, _, _ in pts), max(t for t, _, _ in pts)], "bins": len(pts),
                       "rule": "section 1's form, T_L held at its 36 C, weighted least squares (weights: kept cycles per bin) "
                               "on the card's version-3 idle bins (v3.idle.bins)", "source": V3 + "/idle.json"}
    out["rest"]["per_card"] = per_card

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out, "sections:", ", ".join(k for k in out))


if __name__ == "__main__":
    main()
