#!/usr/bin/env python3
"""Assemble the three-machine block and merge it into the report data files.

    build_cards_data.py --cards cards.json --transfer transfer.json --leak leakage_crosscard.json \
        --config config.json --driver driver_config.json --sptrace sptrace-aifoundry3.bin \
        --out cards-report.json --merge dvfs.json report.json

    # the Horace page's section 10 and pricer on the version-3 check's three cards (the 22 September block kept
    # under "history"); merges into report.json only, so the DVFS page and cards-report.json keep the block above
    build_cards_data.py ... --v3 docs/reports/data/2026-09-25-claims-v3/results --model model.json \
        --toggles-all toggles_all.json --out cards-v3.json --merge report.json

Nothing is fitted here. The per-pattern switching powers come from each card's own strict session; the model
coefficients come from the aifoundry2 fit and are used unchanged; the single scale factor is the least-squares
ratio between the two, reported alongside the leave-one-out check that calibrates it on one run.
"""
import argparse
import json
import re

import numpy as np

REF = "aifoundry2"
# the check's fp32 operand patterns (V3-ABL-A configurations) and the Horace page's names for them
V3_PATTERNS = [("fp32_zeros", "zeros"), ("fp32_ones", "ones"), ("fp32_signs", "signs"), ("fp32_pow2", "pow2"),
               ("fp32_arb1", "a_randn_b_ones"), ("fp32_a1br", "a_ones_b_randn"), ("fp32_mant", "mant"),
               ("fp32_randn", "randn")]
V3_STRUCTURED = [("m_butterfly", "butterfly"), ("m_negzero", "negzero"), ("m_fft_cos", "fft_cos"),
                 ("m_hadamard", "hadamard"), ("m_relu", "relu"), ("m_kaleidoscope", "kaleidoscope")]


def _mean_sd(v):
    v = np.asarray(v, float)
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None, "n": int(len(v))}


def _transfer(names, m, a):
    """transfer_cards.py's transfer() for any card: the least-squares scale, the unscaled and scaled residuals,
    and the scale calibrated on one pattern at a time (rms over the others, and the largest single error)."""
    s = float(m @ a / (m @ m))
    e = a - m
    loo, worst, pair = [], 0.0, None
    for i in range(len(m)):
        oth = [j for j in range(len(m)) if j != i]
        ee = a[oth] - a[i] / m[i] * m[oth]
        loo.append(float(np.sqrt(np.mean(ee ** 2))))
        j = int(np.argmax(np.abs(ee)))
        if float(np.abs(ee[j])) > worst:
            worst, pair = float(np.abs(ee[j])), (names[i], names[oth[j]])
    iw, ie = int(np.argmax(loo)), int(np.argmax(np.abs(e)))
    return {"scale": s, "rms_raw": float(np.sqrt(np.mean(e ** 2))), "max_raw": float(np.abs(e).max()),
            "max_raw_pattern": names[ie], "rms_scaled": float(np.sqrt(np.mean((a - s * m) ** 2))),
            "ratio": dict(zip(names, (a / m).tolist())),
            "loo": {"per_pattern": dict(zip(names, loo)), "median_rms": float(np.median(loo)),
                    "worst_rms": loo[iw], "worst_rms_calibrated_on": names[iw],
                    "worst_single": worst, "worst_single_pair": list(pair)}}


def v3_block(res, model, toggles, history):
    """Section 10's data from the version-3 check (docs/reports/data/2026-09-25-claims-v3/results): each card's
    switching power over idle per pattern (V3-ABL-A's kept runs, the busy rule, each card reduced as registered),
    the aifoundry2 model's prediction for the same pattern (compare_cards.model_switching), and per card the
    scale and transfer statistics; the flip-model refit (ABL-R), the structured matrices, the temperature arm (X5),
    the catalogue's temperature panel (CAT-a) and the idle cycles (IDLE-a, IDLE-b). Nothing is fitted here."""
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from compare_cards import model_switching
    J = lambda f: json.load(open(os.path.join(res, f)))
    runs = J("abla.runs.json")
    item = lambda d, k: next(x for x in d if x["item"] == k)
    by = {}
    for card, rs in runs["runs"].items():
        for r in rs:
            if r.get("kept_busy"):
                by.setdefault(card, {}).setdefault(r["config"], []).append(r)
    cards = [c for c in runs["cards_all"] if c in by]
    names = [p for _, p in V3_PATTERNS]
    m = np.array([model_switching(model, toggles, p) for p in names])
    out = {"source": "version-3 check, 26 September 2026: docs/reports/data/2026-09-25-claims-v3/results "
                     "(abla.runs.json kept runs, busy rule; abla.json, x5.json, idle.json, cat.json)",
           "patterns": [{"values": p, "model": float(m[i]),
                         "per_card": {c: _mean_sd([r["switching"] for r in by[c][cfg]]) for c in cards}}
                        for i, (cfg, p) in enumerate(V3_PATTERNS)]}
    cfgs = [cfg for cfg, _ in V3_PATTERNS]
    allr = {c: [r for cfg in cfgs for r in by[c][cfg]] for c in cards}
    P = runs["params_by_card"]
    out["launch"] = {c: {"T": P[c]["launch"], "leak_w_per_c": P[c]["leak"],
                         "reading": float(np.mean([r["t_launch"] for r in allr[c]]))} for c in cards}
    out["idle"] = {c: float(np.mean([r["p_before"] for r in allr[c]])) for c in cards}
    out["mv"] = {c: runs["idle_by_card"][c]["busy_mv"] for c in cards}
    out["runs_per_pattern"] = {c: sorted({len(by[c][cfg]) for cfg in cfgs}) for c in cards}
    out["fit"] = {c: _transfer(names, m, np.array([p["per_card"][c]["mean"] for p in out["patterns"]]))
                  for c in cards}
    out["scale"] = {c: 1.0 if c == REF else out["fit"][c]["scale"] for c in cards}
    # each card against aifoundry2's own runs of the same check: the least-squares ratio of switching powers
    ref = np.array([p["per_card"][REF]["mean"] for p in out["patterns"]])
    out["ratio_to_ref"] = {c: float(np.array([p["per_card"][c]["mean"] for p in out["patterns"]]) @ ref / (ref @ ref))
                           for c in cards}
    # Post-data note C2 (AMENDMENTS.md): the registered switching references each run to a fixed launch temperature
    # (80.9 C aifoundry2 and aifoundry1-c1, 55.8 C aifoundry3), but the runs launched at 80.0-81.0 / 57.0-58.0 C, so each
    # value is off by leak x (t_launch - launch). "at_launch" re-states every run at its own launch temperature
    # (switching + leak x (t_launch - launch)); it is descriptive, not a registered outcome.
    atl = {c: np.array([float(np.mean([r["switching"] + P[c]["leak"] * (r["t_launch"] - P[c]["launch"]) for r in by[c][cfg]]))
                        for cfg in cfgs]) for c in cards}
    out["at_launch"] = {
        "note": "post-data note C2: each run at its own launch temperature, switching + leak x (t_launch - launch); descriptive",
        "offset_w": {c: float(np.mean([P[c]["leak"] * (r["t_launch"] - P[c]["launch"]) for r in allr[c]])) for c in cards},
        "fit": {c: _transfer(names, m, atl[c]) for c in cards},
        "ratio_to_ref": {c: float(atl[c] @ atl[REF] / (atl[REF] @ atl[REF])) for c in cards}}
    # C2, revised: if each launch was at a downward step of the whole-degree reading, as the references' were, the die
    # was at reading + 0.96 C (the 21 September thermal network at the 81 -> 80 step)
    STEP = 0.96
    ats = {c: np.array([float(np.mean([r["switching"] + P[c]["leak"] * (r["t_launch"] + STEP - P[c]["launch"])
                                       for r in by[c][cfg]])) for cfg in cfgs]) for c in cards}
    out["at_launch_step"] = {
        "note": f"C2 revised: launches at a downward step of the reading, die = reading + {STEP} C; descriptive",
        "offset_w": {c: float(np.mean([P[c]["leak"] * (r["t_launch"] + STEP - P[c]["launch"]) for r in allr[c]])) for c in cards},
        "fit": {c: _transfer(names, m, ats[c]) for c in cards},
        "ratio_to_ref": {c: float(ats[c] @ ats[REF] / (ats[REF] @ ats[REF])) for c in cards}}
    # board power per pattern and card (p80_d: the registered dropout rule, as in switching = p80_d - idle), at each
    # card's reduction temperature, for the text
    out["board"] = {c: {p: float(np.mean([r["p80_d"] for r in by[c][cfg]])) for cfg, p in V3_PATTERNS} for c in cards}
    abla = J("abla.json")
    R = item(abla, "ABL-R")["per_card"]
    out["refit"] = {c: {"fJ": R[c]["refit_p80"]["fJ_per_event"], "constant_W": R[c]["refit_p80"]["constant_W"],
                        "rms": R[c]["refit_p80"]["rms"], "loo_rms": R[c]["refit_p80"]["loo_rms"],
                        "loo": R[c]["refit_p80"]["loo"], "patterns": R[c]["refit_p80"]["patterns"],
                        "drift_w_per_c": {k: R[c]["drift_w_per_c"][k] for k in ("n", "mean", "lo", "hi")}}
                    for c in cards}
    out["structured"] = {c: {p: dict(_mean_sd([r["p80_d"] for r in by[c][cfg]]),
                                     switching=float(np.mean([r["switching"] for r in by[c][cfg]])))
                             for cfg, p in V3_STRUCTURED if cfg in by[c]} for c in cards}
    # the temperature arm: hot - cool switching per card and pattern, the registered 99.75% interval
    x5 = J("x5.json")[0]
    out["x5"] = {"verdict": x5["verdict"], "all_cards": x5["all_cards"]["verdict"], "per_card": {}}
    # the registered test, its interval level and its band (27 September 2026: for the page's chart of this block)
    band = re.search(r"inside \+-([\d.]+) W", x5["test"])
    alphas = {t["ci_hot_minus_cool"]["alpha"] for pc in x5["per_card"].values() for t in pc["tests"].values()}
    out["x5"].update(test=x5["test"], band_w=float(band.group(1)) if band else None,
                     level=(1 - alphas.pop()) if len(alphas) == 1 else None)
    for c, pc in x5["per_card"].items():
        lt = pc["launch_temperatures"]
        out["x5"]["per_card"][c] = {
            "outcome": pc["outcome"],
            "launch": {arm: {"target": v["target_c"], "reading": v["measured_launch_c"]["mean"]} for arm, v in lt.items()},
            "hot_minus_cool": {p: dict({k: t["ci_hot_minus_cool"][k] for k in ("point", "lo", "hi", "values_x", "values_y")},
                                       in_decision=t.get("in_decision"))
                               for p, t in pc["tests"].items()},
            "own_launch": {p: {k: v for k, v in list(dg.values())[0].items() if k in ("point", "lo", "hi")}
                           for p, dg in pc.get("diagnostics", {}).items()}}
    # the idle power in the two seconds before each run (subtracted from it), per arm: uniform data runs first in
    # every arm (the runner's fixed shuffle), the other four patterns after it
    xr = J("x5.runs.json")["runs"]
    rng = lambda v: [float(min(v)), float(max(v))]
    for c, rs in xr.items():
        ib = {}
        for arm in ("hi", "lo"):
            ar = [r for r in rs if r.get("arm") == arm and r.get("kept_busy")]
            ib[arm] = {"all": rng([r["p_before"] for r in ar]),
                       "uniform": rng([r["p_before"] for r in ar if r["config"] == "fp32_uniform"]),
                       "others": rng([r["p_before"] for r in ar if r["config"] != "fp32_uniform"])}
        out["x5"]["per_card"][c]["idle_before"] = ib
    cat = item(J("cat.json")["items"], "CAT-a")["per_card"]
    out["cat_temperature"] = {c: {"beta_pct_per_c": v["beta_pct_per_c"], "dT_c": v["dT_c"], "decision": v["decision"]}
                              for c, v in cat.items()}
    # the idle cycles: each card's idle minus aifoundry2's law, by whole-degree bin (mean over the cycles in it)
    idl = J("idle.json")
    ia, ib = item(idl["items"], "IDLE-a")["per_card"], item(idl["items"], "IDLE-b")["per_card"]
    lk = {"law": idl["constants"]["law"], "per_card": {}}
    for c in cards:
        if c in ia and ia[c].get("cycles"):
            bins = {}
            for cy in ia[c]["cycles"]:
                for T, v in cy["resid_by_bin"].items():
                    bins.setdefault(int(T), []).append(v)
            lk["per_card"][c] = {"bins": {T: {"mean": float(np.mean(v)), "n_cycles": len(v)} for T, v in sorted(bins.items())},
                                 "offset": {"mean": ia[c]["offset_W"]["mean"], "ci99": ia[c]["offset_W"]["ci99"]},
                                 "slope": {"mean": ia[c]["resid_slope_W_per_C"]["mean"], "ci99": ia[c]["resid_slope_W_per_C"]["ci99"]},
                                 "cycles": ia[c]["n"], "item": "IDLE-a"}
        elif c in ib and ib[c].get("bins"):
            lk["per_card"][c] = {"bins": {int(T): {"mean": v["mean"], "n_cycles": v["n_cycles"]} for T, v in ib[c]["bins"].items()},
                                 "offset": {"mean": ib[c]["info_cycle_offset_W"]["mean"], "ci99": ib[c]["info_cycle_offset_W"]["ci99"]},
                                 "cycles": ib[c]["n"], "item": "IDLE-b"}
    out["leakage_v3"] = lk
    # the 22 September block: aifoundry3's one strict session (section 10's first test) and its idle table
    out["history"] = history
    out["leakage"] = history["leakage"]
    for k in ("config", "driver_tdp", "driver_cards", "voltage", "sptrace_aifoundry3"):
        if k in history:
            out[k] = history[k]
    return out


def main():
    ap = argparse.ArgumentParser()
    for k in ("cards", "transfer", "leak", "config", "driver", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--sptrace")
    ap.add_argument("--merge", nargs="*", default=[])
    ap.add_argument("--v3", help="the version-3 check's results directory: section 10 on its cards (history kept)")
    ap.add_argument("--model", help="with --v3: model.json (the flip model the per-pattern predictions use)")
    ap.add_argument("--toggles-all", help="with --v3: toggles_all.json (RTL counts of every pattern)")
    a = ap.parse_args()
    cards = json.load(open(a.cards))
    tr = json.load(open(a.transfer))
    leak = json.load(open(a.leak))
    cfg = json.load(open(a.config))
    drv = json.load(open(a.driver))

    rows = cards["rows"]
    m = np.array([r["model_switching"] for r in rows])
    a3 = np.array([r["aifoundry3"]["switching"] for r in rows])
    scale = float(m @ a3 / (m @ m))
    out = {
        "patterns": [{"values": r["values"], "model": r["model_switching"],
                      "a2": r["aifoundry2"]["switching"], "a3": r["aifoundry3"]["switching"],
                      "a2_sd": r["aifoundry2"]["p80_sd"], "a3_sd": r["aifoundry3"]["p80_sd"]} for r in rows],
        "launch": {k: {"T": v["launch_temp"], "T_sd": v["launch_temp_sd"]} for k, v in cards["cards"].items()},
        "idle": {"aifoundry2": rows[0]["aifoundry2"]["p80"] - rows[0]["aifoundry2"]["switching"],
                 "aifoundry3": rows[0]["aifoundry3"]["p80"] - rows[0]["aifoundry3"]["switching"]},
        "scale": scale,
        "rms_raw": cards["model_error"]["aifoundry3"]["rms"],
        "max_raw": cards["model_error"]["aifoundry3"]["max"],
        "rms_scaled": float(np.sqrt(np.mean((a3 - scale * m) ** 2))),
        "loo": {"median_rms": tr["median_rms"], "worst": tr["worst"],
                "per_pattern": dict(zip(tr["names"], tr["loo_scale_rms"]))},
        "leakage": leak,
        "config": cfg,
        "driver_tdp": {h: v[0]["tdp_w"] for h, v in drv.items()},
        "driver_cards": {h: len(v) for h, v in drv.items()},
    }
    # voltage: the operating point cannot explain the scale, it points the other way
    mv2, mv3 = cfg["aifoundry2"]["minion_mv"], cfg["aifoundry3"]["minion_mv"]
    out["voltage"] = {"a2_mv": mv2, "a3_mv": mv3, "cv2f_ratio": (mv3 / mv2) ** 2}
    if a.sptrace:
        s = open(a.sptrace, "rb").read().decode("latin-1")
        ev = re.findall(r"Power throttle down event, current pwr (\d+)\s+tdp level: (\d+)", s)
        out["sptrace_aifoundry3"] = {"down_events": len(ev), "tdp_levels": sorted({int(t) for _, t in ev}),
                                     "pwr_mw": [int(p) for p, _ in ev][:8],
                                     "up_events": len(re.findall(r"Power throttle up event", s))}
    if a.v3:
        out = v3_block(a.v3, json.load(open(a.model)), json.load(open(a.toggles_all)), out)
        for c, f in out["fit"].items():
            print(f"v3 {c}: scale {f['scale']:.4f}, rms raw {f['rms_raw']:.2f} W -> scaled {f['rms_scaled']:.2f} W, "
                  f"calibrated on random normal {f['loo']['per_pattern']['randn']:.2f} W rms")
    json.dump(out, open(a.out, "w"), indent=1)
    for path in a.merge:
        d = json.load(open(path))
        d["cards"] = out
        json.dump(d, open(path, "w"), separators=(",", ":"))
        print("merged cards block into", path)
    h = out.get("history", out)
    print(f"scale {h['scale']:.4f}, rms raw {h['rms_raw']:.2f} W -> scaled {h['rms_scaled']:.2f} W; "
          f"leave-one-out median {h['loo']['median_rms']:.2f} W; "
          f"sp trace: {h.get('sptrace_aifoundry3',{}).get('down_events','-')} throttle-down events at tdp "
          f"{h.get('sptrace_aifoundry3',{}).get('tdp_levels','-')}")


if __name__ == "__main__":
    main()
