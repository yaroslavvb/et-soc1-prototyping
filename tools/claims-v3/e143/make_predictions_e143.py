#!/usr/bin/env python3
"""E143 (Q138): writes predictions-e143.json, everything E143 scores, frozen before the claim and the first launch. No card. NOTHING IS FITTED OR
REFITTED HERE: every predicted number is Q138(x)'s (predictions-blind5-aifoundry2.json, commit dac39d97, from Q138(m)'s predict_blind5.py at 3a210f2b),
copied by key after its sha256 is checked; the reference errors the rules bootstrap from are M7's own committed out-of-sample rows.

    python3 tools/claims-v3/e143/make_predictions_e143.py > tools/claims-v3/e143/predictions-e143.txt

WHAT IT WRITES
  tiles      the pool's 36 tiles: type, priority, anchor, the run value and label, the manifest's sha256 (whole, A, B), and M7's, M6's and M5's
             frozen burst predictions on aifoundry2 (clock burst_mhz, board burst_board_w, burst D burst_D_w, die rise burst_die_rise_c, each with
             its 95% band), and the group: GOVERNED if M7's burst clock is below 795 MHz (19 tiles), else PINNED (17).
  replicate  E80's own kinds tiles fp32/randn, fp16/randn, int8/full, run once a pass beside the pool (the card's drift check, E80-R4's form):
             E80's and E83's measured cells (burst_mhz, burst_w), the mean of the two experiments.
  reference  the errors the rules draw from: M7's end-to-end rows on E80's and E83's 56 kinds bursts (loko-m7.json, aifoundry2,
             end_to_end_from_M7_nested_D.rows: measured minus predicted clock and board W), split as Q138(m)'s verification split them
             by M7's PREDICTED clock, as E143's tile groups are (governed = predicted below 795 MHz; Q138(m)'s verification split them by the
             measured clock, 21 governed rows at 13.86 MHz and 2.35 W rms, 35 pinned at 0.61 MHz and 1.50 W, which leaves the four bursts
             predicted at 800 MHz that ran at 761-779 MHz out of the pinned set: kept in the file for information); and the burst heat
             law's leave-one-kind-out residuals over E80's and E83's 112 kinds burst runs, recomputed here exactly as fit_m7.py computes them
             (die_max - die_start - k (burst_w - 21.5 W), k refitted without the kind) and checked against m7.json's 0.6845 C.
  admission  run_e105.py's table: per label a fixed estimate of the board W in the first second at 800 MHz, B(800) + s(800) (c_zeros + D / 1.01865)
             with D M7's frozen D on aifoundry3's footing (the relation M7 uses, E136's frozen constants); the kinds replicates at the highest
             first-second reading E80 and E83 measured for that kind.
  rules      E143's decision rules (E143.md), the stops and the admission limits.
"""
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e143_common as C  # noqa: E402

ROOT = C.ROOT
LOKO_REL = "docs/reports/data/2026-11-02-q138m-model/loko-m7.json"
POSTHOC_REL = "docs/reports/data/2026-11-02-q138m-model/posthoc-m7.json"
P136_REL = "tools/claims-v3/e136/predictions-e136.json"
E80_REL = "docs/reports/data/2026-10-31-e80-kinds-speed/results.json"
E83_REL = "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json"
KSPEED_PRED_REL = "tools/claims-v3/kspeed/predictions.json"
KINDS_REL = "tools/claims-v3/kinds/kinds.json"
REPLICATES = (("fp32", "randn"), ("fp16", "randn"), ("int8", "full"))
STOPS = {"abs_stop_c": 80, "board_cap_w": 93, "cap_consecutive": 3}       # E136's registered stops, under the keys run_hpl.py's watcher reads
LIMIT_P800_W = 86.0      # stricter than E101's 88 W: the pool's highest estimate is 84.4 W
PEAK_LOCK_W = 93.0


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def sha(rel):
    return C.sha256_file(os.path.join(ROOT, rel))


def heat_residuals(m7):
    """fit_m7.py's (c) aifoundry2 burst heat, leave one kind out, recomputed from E80's and E83's committed cells (no number changes)."""
    P_IDLE = m7["aifoundry2"]["burst_heat"]["P_idle_w"]
    kin = []
    for rel in (E80_REL, E83_REL):
        for lab, c in load(rel)["cells"].items():
            if c.get("burst_mhz") is None or c.get("c_w") is None:
                continue
            t, n = lab.split("/")
            for dmx, dst in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or []):
                if dmx is not None and dst is not None:
                    kin.append((f"{t}.{n}", float(c["burst_w"]) - P_IDLE, dmx - dst))
    res = []
    for kn in sorted({h[0] for h in kin}):
        tr = [h for h in kin if h[0] != kn]
        k = sum(x * y for _, x, y in tr) / sum(x * x for _, x, y in tr)
        res += [round(y - k * x, 6) for n_, x, y in kin if n_ == kn]
    return res, len(kin)


def main():
    bad = C.check_frozen()
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    pred = load(C.PRED_REL)
    man = C.manifest()
    m7 = load(C.M7_REL)
    loko = load(LOKO_REL)
    P136 = load(P136_REL)
    rel = P136["relation"]
    B800, S800, CZ, XFER = rel["B"]["800"], rel["s800"], rel["c_zeros_w"], rel["xfer"]
    # every frozen relation constant must be the one M7 froze
    mr = m7["aifoundry2"]["relation"]
    assert abs(mr["B_w"]["800"] - B800) < 1e-9 and abs(mr["s_f"]["800"] - S800) < 1e-9 and mr["c_zeros_w"] == CZ and abs(mr["xfer"] - XFER) < 1e-12

    tiles, admission, dry_c = {}, {}, {}
    for name in sorted(pred["tiles"]):
        rec = pred["tiles"][name]
        t = man[name]
        why = C.check_tile(ROOT, t)
        if why:
            raise SystemExit(f"refused: {why}")
        assert rec["type"] == t["type"] and rec["sha256"] == t["sha256"]["whole"] and rec["sha256_matches_manifest"]
        keys = ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_D_w", "burst_D_95", "burst_die_rise_c", "burst_die_rise_95",
                "D600_a3_footing_w")
        models = {m: {k: rec[m][k] for k in keys} for m in ("M7", "M6", "M5")}
        group = "governed" if rec["M7"]["burst_mhz"] < C.GOVERNED_BELOW_MHZ else "pinned"
        lab = C.label_of(name)
        D = rec["M7"]["D600_a3_footing_w"]
        c = CZ[t["type"]] + D / XFER
        est = round(B800 + S800 * c, 2)
        admission[lab] = {"c_ref_w": round(c, 3), "fixed_p800_w": est}
        dry_c[C.tile_value(t)] = round(c, 3)
        tiles[name] = {"type": t["type"], "priority": t["priority"], "anchor": bool(t.get("anchor")), "case": rec.get("case"), "label": lab,
                       "values": C.tile_value(t), "sha256": t["sha256"], "group": group, "models": models}

    # the replicates: E80's own tiles, against E80's and E83's measured cells
    K = load(KINDS_REL)
    e80, e83 = load(E80_REL)["cells"], load(E83_REL)["cells"]
    rep = {}
    for ty, kd in REPLICATES:
        k = f"{ty}/{kd}"
        a, b = e80[k], e83[k]
        p8 = [x for x in (a.get("burst_p800_w_runs") or []) + (b.get("burst_p800_w_runs") or []) if x is not None]
        lab = f"k-{ty}-{kd}"
        val = f"file:tools/claims-v3/kinds/tiles/{ty}/{kd}.bin"
        rep[lab] = {"type": ty, "kind": kd, "values": val, "sha256": K["kinds"][ty][kd]["sha256"],
                    "e80_burst_mhz": a["burst_mhz"], "e83_burst_mhz": b["burst_mhz"], "ref_burst_mhz": round((a["burst_mhz"] + b["burst_mhz"]) / 2, 2),
                    "e80_burst_w": a["burst_w"], "e83_burst_w": b["burst_w"], "ref_burst_w": round((a["burst_w"] + b["burst_w"]) / 2, 3),
                    "max_p800_w_measured": max(p8)}
        admission[lab] = {"c_ref_w": round((max(p8) - B800) / S800, 3), "fixed_p800_w": round(max(p8), 2)}
        dry_c[val] = round((a["c_w"] + b["c_w"]) / 2, 3)
    admission["rest"] = {"c_ref_w": 0.0, "fixed_p800_w": round(B800, 2)}

    rows = loko["aifoundry2"]["end_to_end_from_M7_nested_D"]["rows"]
    # split by M7's PREDICTED clock, as E143's tile groups are (the only split known before the data); Q138(m)'s verification split by the
    # measured clock, which puts the four bursts predicted at 800 MHz that ran at 761-779 MHz among the governed (kept below for information)
    gov = [r for r in rows if r["mhz_pred"] < C.GOVERNED_BELOW_MHZ]
    pin = [r for r in rows if r["mhz_pred"] >= C.GOVERNED_BELOW_MHZ]
    gm = [r for r in rows if r["mhz_meas"] < C.GOVERNED_BELOW_MHZ]
    pm = [r for r in rows if r["mhz_meas"] >= C.GOVERNED_BELOW_MHZ]
    ref = {
        "source": f"{LOKO_REL} aifoundry2.end_to_end_from_M7_nested_D.rows (M7's end to end from its nested D, the frozen cap 65.58 W), split by M7's predicted clock (below 795 MHz: governed)",
        "split_by_measured_clock_for_information": {"definition": f"{POSTHOC_REL} aifoundry2_split.definition", "governed_n": len(gm), "pinned_n": len(pm),
                                                    "governed_rms_mhz": round(C.rms([r["mhz_meas"] - r["mhz_pred"] for r in gm]), 4),
                                                    "governed_rms_w": round(C.rms([r["w_meas"] - r["w_pred"] for r in gm]), 4),
                                                    "pinned_rms_mhz": round(C.rms([r["mhz_meas"] - r["mhz_pred"] for r in pm]), 4),
                                                    "pinned_rms_w": round(C.rms([r["w_meas"] - r["w_pred"] for r in pm]), 4)},
        "governed": {"n": len(gov), "mhz_err": [round(r["mhz_meas"] - r["mhz_pred"], 3) for r in gov], "w_err": [round(r["w_meas"] - r["w_pred"], 3) for r in gov],
                     "cells": [r["cell"] for r in gov]},
        "pinned": {"n": len(pin), "mhz_err": [round(r["mhz_meas"] - r["mhz_pred"], 3) for r in pin], "w_err": [round(r["w_meas"] - r["w_pred"], 3) for r in pin],
                   "cells": [r["cell"] for r in pin]},
    }
    for g in ("governed", "pinned"):
        ref[g]["rms_mhz"] = round(C.rms(ref[g]["mhz_err"]), 4)
        ref[g]["rms_w"] = round(C.rms(ref[g]["w_err"]), 4)
    hres, nk = heat_residuals(m7)
    hr = C.rms(hres)
    assert abs(hr - m7["aifoundry2"]["burst_heat"]["loko_rms_c_kinds_refit"]) < 1e-6, (hr, m7["aifoundry2"]["burst_heat"])
    ref["heat"] = {"n": len(hres), "rise_err_c": hres, "rms_c": round(hr, 4),
                   "source": f"fit_m7.py (c), the burst heat law's leave-one-kind-out residuals on {E80_REL} and {E83_REL}, recomputed; m7.json aifoundry2.burst_heat.loko_rms_c_kinds_refit {m7['aifoundry2']['burst_heat']['loko_rms_c_kinds_refit']}"}

    ng = sum(1 for t in tiles.values() if t["group"] == "governed")
    npn = len(tiles) - ng
    plan_bars = {
        "F1_governed_clock_rms_mhz": C.boot_rms_range(ref["governed"]["mhz_err"], ng),
        "F2_pinned_clock_rms_mhz": C.boot_rms_range(ref["pinned"]["mhz_err"], npn),
        "W1_governed_board_rms_w": C.boot_rms_range(ref["governed"]["w_err"], ng),
        "W2_pinned_board_rms_w": C.boot_rms_range(ref["pinned"]["w_err"], npn),
        "H1_die_rise_rms_c": C.boot_rms_range(hres, len(tiles)),
        "coverage_line_36": C.coverage_line(len(tiles)),
        "coverage_line_governed": C.coverage_line(ng), "coverage_line_pinned": C.coverage_line(npn),
    }
    plan_bars = {k: ([round(x, 3) for x in v] if isinstance(v, tuple) else v) for k, v in plan_bars.items()}

    out = {
        "experiment": "E143", "request": "Q138", "card": "aifoundry2 card 0, under its own governor (65 W static TDP, 65 C threshold: read, never set)",
        "_note": "frozen before the claim and the first launch; nothing fitted or refitted: every prediction is Q138(x)'s, copied by key after its sha256 check",
        "inputs_sha256": {**{r: sha(r) for r in (C.PRED_REL, C.MAN_REL, C.M7_REL, LOKO_REL, POSTHOC_REL, P136_REL, E80_REL, E83_REL, KSPEED_PRED_REL, KINDS_REL)},
                          "tools/claims-v3/e143/e143_common.py": sha("tools/claims-v3/e143/e143_common.py"),
                          "tools/claims-v3/e143/make_predictions_e143.py": sha("tools/claims-v3/e143/make_predictions_e143.py")},
        "q138x_commit": "dac39d97eca93e41bff28bdf3dbc4fa2550d11f2", "m7_commit": "3a210f2bef4356d97c7b55c4ba40e2620a11dc3a",
        "relation": {"B800": B800, "s800": S800, "c_zeros_w": CZ, "xfer": XFER, "W_star_w": m7["aifoundry2"]["burst_cap"]["W_star_used_w"],
                     "heat_k_c_per_w": m7["aifoundry2"]["burst_heat"]["k_used_c_per_w"], "P_idle_w": m7["aifoundry2"]["burst_heat"]["P_idle_w"]},
        "frozen_bands": {"mhz": 21.3, "board_w": 3.37, "die_c": 1.41, "source": "m7.json aifoundry2.end_to_end_band and burst_heat.q95_abs_c, as each tile's _95 in the predictions file"},
        "tiles": tiles, "n_governed": ng, "n_pinned": npn, "replicate": rep, "reference": ref, "plan_bars_at_full_n": plan_bars,
        "admission": admission, "dry_c_w": dry_c,
        "rules": {"safety": STOPS, "limit_p800_w": LIMIT_P800_W, "peak_lock_w": PEAK_LOCK_W, "min_passes": 2,
                  "min_tiles": {"F1": 8, "F2": 8, "W1": 8, "W2": 8, "H1": 10, "coverage": 10}, "replicate_mhz": 25.0, "replicate_w": 3.37,
                  "boot": {"draws": C.BOOT_DRAWS, "seed": C.BOOT_SEED, "form": "e143_common.boot_rms_range"}},
    }
    p = os.path.join(HERE, "predictions-e143.json")
    json.dump(out, open(p, "w"), indent=1, sort_keys=False)
    print(f"predictions-e143.json sha256 {C.sha256_file(p)}")
    print(f"{len(tiles)} tiles: {ng} governed (M7 < 795 MHz), {npn} pinned; replicates {list(rep)}")
    print(f"reference: governed {ref['governed']['n']} rows, {ref['governed']['rms_mhz']} MHz, {ref['governed']['rms_w']} W; pinned {ref['pinned']['n']} rows, "
          f"{ref['pinned']['rms_mhz']} MHz, {ref['pinned']['rms_w']} W; heat {ref['heat']['n']} runs ({nk}), {ref['heat']['rms_c']} C")
    print("bars at full n (2.5%, 97.5% of the bootstrap rms):", json.dumps(plan_bars))
    top = sorted(((v["fixed_p800_w"], k) for k, v in admission.items()), reverse=True)[:5]
    print(f"admission: highest estimates {top}; limit {LIMIT_P800_W} W, lock {PEAK_LOCK_W} W; stops {STOPS}")
    for name, t in sorted(tiles.items(), key=lambda kv: (kv[1]["group"], kv[1]["type"], kv[0])):
        m = t["models"]["M7"]
        print(f"  {t['group']:8s} p{t['priority']} {name:34s} M7 {m['burst_mhz']:6.1f} MHz {m['burst_board_w']:6.2f} W D {m['burst_D_w']:6.2f} rise {m['burst_die_rise_c']:5.2f} C"
              f"  M6 {t['models']['M6']['burst_mhz']:6.1f}/{t['models']['M6']['burst_board_w']:6.2f}  M5 {t['models']['M5']['burst_mhz']:6.1f}/{t['models']['M5']['burst_board_w']:6.2f}"
              f"  est800 {admission[t['label']]['fixed_p800_w']} W")


if __name__ == "__main__":
    main()
