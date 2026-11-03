#!/usr/bin/env python3
"""E160 (Q139): writes predictions-e160.json, everything E160 scores, frozen before the claim and the first launch. No card. NOTHING IS FITTED OR
REFITTED HERE: every predicted number is Q139(x)'s (predictions-blind6-aifoundry2.json, commit d98d2e34, from Q139(m)'s predict_blind6.py at 122da8b6),
copied by key after its sha256 is checked; the reference errors the rules bootstrap from are M8's own committed out-of-sample rows.

    python3 tools/claims-v3/e160/make_predictions_e160.py > tools/claims-v3/e160/predictions-e160.txt

WHAT IT WRITES
  tiles      the pool's 50 tiles: type, priority, anchor, class (blind6.json's case letter), real, the run value and label, the manifest's sha256, and
             M8's, M7's and M6's frozen burst predictions on aifoundry2 (burst_mhz, burst_board_w, burst_D_w, burst_die_rise_c, each with its 95% band;
             D600_a3_footing_w), M8's P800 and peak (expected peak_board_w, 95% upper peak_board_hi95_w, the 82 W flag); the group: GOVERNED if M8's
             burst clock is below 795 MHz (Q139(x)'s split), else PINNED; and DROPPED: a tile whose M8 95% upper peak exceeds 82 W (section 22 of the
             brief: "no tile ... whose predicted peak board power exceeds 82 W runs as designed (duty-cycle it or drop it)"): E160 drops it.
  replicate  E80's own kinds tiles fp16/randn and int8/full, run once a pass beside the pool (E143's R0 drift check): E80's and E83's mean cell (E143's
             reference, copied) and E143's own measured cell of 2 Nov. E80's fp32/randn is DROPPED: its highest board sample in E143 was 84.30-84.97 W.
  reference  the errors the rules draw from: M8's end-to-end rows on E80's, E83's and E143's 92 kinds bursts (nested-m8.json aifoundry2
             end_to_end_from_M8_nested_D.rows: measured minus predicted clock and board W, M8's nested D through its frozen relation and cap),
             split by M8's PREDICTED clock as E160's groups are; and the burst heat law's 112 leave-one-kind-out residuals (M8 carries M7's law
             unchanged: E143's frozen predictions-e143.json reference.heat, checked against m8.json's 0.6845 C).
  admission  run_e105.py's table: per label the frozen estimate is M8's 95% upper peak board sample (peak_board_hi95_w) for a pool tile; for a
             replicate the larger of its highest board sample in E143 and P800 from E143's measured c plus M8's q95 peak excess (2.95 W).
  dma        the C log's extra DMA (Q139(k) step 6): E143's own launch gaps and device-held times, from its committed launches, for the smoke's rule.
  scale      rank 5: card-scale-blind6.json's predicted scales for aifoundry2, the g M8 applies, and the measured training scale (m8.json).
  rules      E160's decision rules (E160.md), the stops, the admission limits, the C check's rule and the DMA rule.
"""
import gzip
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e160_common as C  # noqa: E402

ROOT = C.ROOT
NESTED_REL = "docs/reports/data/2026-11-03-q139m-model/nested-m8.json"
SCALE_REL = f"{C.POOL_REL}/card-scale-blind6.json"
P143_REL = "tools/claims-v3/e143/predictions-e143.json"
R143_REL = "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/results.json"
L143 = {"smoke": "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/aifoundry2/smoke/launches.jsonl.gz",
        "s1": "docs/reports/data/2026-11-02-e143-blind5-aifoundry2/aifoundry2/s1/launches.jsonl.gz"}
KINDS_REL = "tools/claims-v3/kinds/kinds.json"
REPLICATES = (("fp16", "randn"), ("int8", "full"))
DROPPED_REPLICATES = (("fp32", "randn"),)
STOPS = {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3}   # section 22: every registered board stop at most 85 W; E159's die stop
LIMIT_W = 82.0        # section 22: no tile whose predicted peak board power exceeds 82 W runs as designed
PEAK_LOCK_W = 82.0    # E159's lock: after a run whose highest board sample reached 82 W, nothing at or above its estimate runs


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def sha(rel):
    return C.sha256_file(os.path.join(ROOT, rel))


def e143_gaps():
    """E143's launch gaps (next launch's t_start_ms - this launch's t_end_ms, inside one process), launches per process and the host's
    'device held for' times, from its committed launch records (E80's host, no C log)."""
    out = {}
    for name, rel in L143.items():
        gaps, held, nl = [], [], []
        for ln in gzip.open(os.path.join(ROOT, rel), "rt"):
            r = json.loads(ln)
            if r.get("role") != "work":
                continue
            sp = r.get("sparsity") or []
            nl.append(len([s for s in sp if s.get("launch", 0) >= 0]))
            gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(sp, sp[1:])]
            m = re.search(r"device held for ([0-9.]+) s", r.get("stderr_tail") or "")
            if m:
                held.append(float(m.group(1)))
        out[name] = {"processes": len(nl), "launch_gap_ms_median": statistics.median(gaps), "launch_gap_ms_max": max(gaps), "n_gaps": len(gaps),
                     "launches_per_process_median": statistics.median(nl), "launches_per_process_max": max(nl),
                     "device_held_s_median": statistics.median(held), "device_held_s_max": max(held), "source": rel}
    return out


def heat_reference():
    P143 = load(P143_REL)
    h = P143["reference"]["heat"]
    return {"n": h["n"], "rise_err_c": h["rise_err_c"], "rms_c": h["rms_c"],
            "source": f"{P143_REL} reference.heat (E143's frozen copy of the burst heat law's 112 leave-one-kind-out residuals on E80's and E83's kinds bursts; "
                      f"M8 carries M7's law: m8.json aifoundry2.burst_heat)"}


def main():
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    pred = load(C.PRED_REL)
    man = C.manifest()
    m8 = load(C.M8_REL)
    nested = load(NESTED_REL)
    scale = load(SCALE_REL)
    a2 = m8["aifoundry2"]
    B800, S800 = a2["relation"]["B_w"]["800"], a2["relation"]["s_f"]["800"]
    pk = a2["peak"]
    assert pred["m8_sha256"] == C.FROZEN[C.M8_REL] and pred["manifest_sha256"] == C.FROZEN[C.MAN_REL]

    tiles, admission, dry_c, dropped = {}, {}, {}, []
    keys = ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_D_w", "burst_D_95", "burst_die_rise_c", "burst_die_rise_95", "D600_a3_footing_w")
    for name in sorted(pred["tiles"]):
        rec = pred["tiles"][name]
        t = man[name]
        why = C.check_tile(ROOT, t)
        if why:
            raise SystemExit(f"refused: {why}")
        assert rec["type"] == t["type"] and rec["sha256"] == t["sha256"]["whole"] and rec["sha256_matches_manifest"]
        models = {m: {k: rec[m][k] for k in keys} for m in C.MODELS}
        for k in ("P800_w", "peak_board_w", "peak_board_hi95_w", "peak_over_82w"):
            models["M8"][k] = rec["M8"][k]
        group = "governed" if rec["M8"]["burst_mhz"] < C.GOVERNED_BELOW_MHZ else "pinned"
        lab = C.label_of(name)
        est = rec["M8"]["peak_board_hi95_w"]
        drop = est > LIMIT_W
        c_exp = (rec["M8"]["P800_w"] - B800) / S800
        admission[lab] = {"c_ref_w": round(c_exp, 3), "fixed_p800_w": est, "what": "M8's frozen 95% upper peak board sample (peak_board_hi95_w)"}
        dry_c[C.tile_value(t)] = round(c_exp, 3)
        cls = (t.get("case") or "?").split(" ")[0]
        tiles[name] = {"type": t["type"], "priority": t["priority"], "anchor": bool(t.get("anchor")), "class": cls, "case": t.get("case"),
                       "real": cls == "R", "hold_candidate": bool(t.get("hold_candidate")), "label": lab, "values": C.tile_value(t), "sha256": t["sha256"],
                       "group": group, "dropped": drop, "models": models}
        if drop:
            tiles[name]["dropped_why"] = (f"M8's 95% upper peak {est} W (expected {rec['M8']['peak_board_w']} W) exceeds the 82 W line of section 22: dropped, "
                                          "not duty-cycled (M8's frozen predictions are for a continuous 6 s burst; a duty-cycled burst has none)")
            dropped.append(name)

    # the replicates: E80's own tiles, against E80's and E83's mean cell (E143's reference) and E143's own cell
    P143 = load(P143_REL)
    R143 = load(R143_REL)
    K = load(KINDS_REL)
    peaks143 = {}
    for p in nested["aifoundry2"]["peaks"]:
        m = re.match(r"BURST-\d+-(k-\w+-\w+)-r\d+$", p["run"])
        if m:
            peaks143.setdefault(m.group(1), []).append(p)
    rep, rep_dropped = {}, {}
    for ty, kd in REPLICATES + DROPPED_REPLICATES:
        lab = f"k-{ty}-{kd}"
        val = f"file:tools/claims-v3/kinds/tiles/{ty}/{kd}.bin"
        r143 = P143["replicate"][lab]
        meas = R143["replicate"]["tiles"][lab]
        ps = peaks143[lab]
        hi = max(p["peak_w"] for p in ps)
        p800c = statistics.mean(p["P800_pred_from_c_w"] for p in ps)
        est = round(max(hi, p800c + pk["excess_q95_w"]), 2)
        assert K["kinds"][ty][kd]["sha256"] == r143["sha256"] == C.sha256_file(os.path.join(ROOT, val[5:]))
        row = {"type": ty, "kind": kd, "values": val, "sha256": r143["sha256"], "ref_burst_mhz": r143["ref_burst_mhz"], "ref_burst_w": r143["ref_burst_w"],
               "ref_source": f"{P143_REL} replicate.{lab} (E80's and E83's mean cell)", "e143_burst_mhz": meas["burst_mhz"], "e143_burst_w": meas["burst_w"],
               "e143_rise_c": meas["rise_c"], "e143_source": f"{R143_REL} replicate.tiles.{lab}", "e143_peak_w_runs": [p["peak_w"] for p in ps],
               "e143_p800_from_c_w": round(p800c, 3), "estimate_w": est}
        if est > LIMIT_W:
            row["dropped_why"] = f"its estimate {est} W (E143's highest board sample {hi} W) exceeds 82 W: dropped"
            rep_dropped[lab] = row
            continue
        rep[lab] = row
        admission[lab] = {"c_ref_w": round((p800c - B800) / S800, 3), "fixed_p800_w": est,
                          "what": "the larger of E143's highest board sample on this tile and P800 from E143's c plus M8's q95 peak excess"}
        dry_c[val] = round((p800c - B800) / S800, 3)
    admission["rest"] = {"c_ref_w": 0.0, "fixed_p800_w": round(B800, 2), "what": "the idle card (no launch)"}

    rows = nested["aifoundry2"]["end_to_end_from_M8_nested_D"]["rows"]
    e2e = a2["end_to_end_from_M8_nested_D"]
    assert len(rows) == e2e["n"] == 92
    gov = [r for r in rows if r["mhz_pred"] < C.GOVERNED_BELOW_MHZ]
    pin = [r for r in rows if r["mhz_pred"] >= C.GOVERNED_BELOW_MHZ]
    ref = {"source": f"{NESTED_REL} aifoundry2.end_to_end_from_M8_nested_D.rows (M8's end to end from its nested D, its frozen relation and cap 65.20 W), "
                     "split by M8's predicted clock (below 795 MHz: governed), as E160's groups are",
           "split_by_measured_clock_for_information": {"governed": e2e["governed"], "pinned": e2e["pinned"], "source": f"{C.M8_REL} aifoundry2.end_to_end_from_M8_nested_D"}}
    for g, rr in (("governed", gov), ("pinned", pin)):
        ref[g] = {"n": len(rr), "mhz_err": [round(r["mhz_meas"] - r["mhz_pred"], 3) for r in rr], "w_err": [round(r["w_meas"] - r["w_pred"], 3) for r in rr],
                  "cells": [f"{r['exp']}:{r['kind']}" for r in rr]}
        ref[g]["rms_mhz"] = round(C.rms(ref[g]["mhz_err"]), 4)
        ref[g]["rms_w"] = round(C.rms(ref[g]["w_err"]), 4)
    ref["heat"] = heat_reference()
    assert abs(ref["heat"]["rms_c"] - a2["burst_heat"]["loko_rms_c_kinds_refit"]) < 1e-3, (ref["heat"]["rms_c"], a2["burst_heat"])
    # the peak rule's own reference: the highest board sample of each of E143's 117 traces less the P800 its measured c gives (m8.json aifoundry2.peak)
    ref["peak"] = {"excess_w": [round(p["excess_w"], 3) for p in nested["aifoundry2"]["peaks"]], "median_w": pk["excess_median_w"], "q95_w": pk["excess_q95_w"],
                   "source": f"{NESTED_REL} aifoundry2.peaks (E143's 117 traces); {C.M8_REL} aifoundry2.peak"}

    run_tiles = [n for n in tiles if not tiles[n]["dropped"]]
    ng = sum(1 for n in run_tiles if tiles[n]["group"] == "governed")
    npn = len(run_tiles) - ng
    plan_bars = {
        "F1_governed_clock_rms_mhz": C.boot_rms_range(ref["governed"]["mhz_err"], ng),
        "F2_pinned_clock_rms_mhz": C.boot_rms_range(ref["pinned"]["mhz_err"], npn),
        "W1_governed_board_rms_w": C.boot_rms_range(ref["governed"]["w_err"], ng),
        "W2_pinned_board_rms_w": C.boot_rms_range(ref["pinned"]["w_err"], npn),
        "H1_die_rise_rms_c": C.boot_rms_range(ref["heat"]["rise_err_c"], len(run_tiles)),
        "coverage_line_all": C.coverage_line(len(run_tiles)), "coverage_line_governed": C.coverage_line(ng), "coverage_line_pinned": C.coverage_line(npn),
    }
    plan_bars = {k: ([round(x, 3) for x in v] if isinstance(v, tuple) else v) for k, v in plan_bars.items()}

    sa = scale["cards"]["aifoundry2"] if "cards" in scale else scale["aifoundry2"]
    out = {
        "experiment": "E160", "request": "Q139", "card": "aifoundry2 card 0, under its own governor (65 W static TDP, 65 C threshold: read, never set)",
        "_note": "frozen before the claim and the first launch; nothing fitted or refitted: every prediction is Q139(x)'s, copied by key after its sha256 check",
        "inputs_sha256": {**{r: sha(r) for r in (C.PRED_REL, C.MAN_REL, C.MANIFEST_REL, C.M8_REL, NESTED_REL, SCALE_REL, P143_REL, R143_REL, KINDS_REL,
                                                 L143["smoke"], L143["s1"])},
                          "tools/claims-v3/e160/e160_common.py": sha("tools/claims-v3/e160/e160_common.py"),
                          "tools/claims-v3/e160/make_predictions_e160.py": sha("tools/claims-v3/e160/make_predictions_e160.py")},
        "q139x_commit": "d98d2e34e1de004bb49a8e728c19b8f7b5f5bb70", "m8_commit": "122da8b6", "q139k_commit": "4946a99272472c72e8e5a54b96f402fd7bd73eff",
        "relation": {"B800": B800, "s800": S800, "W0_w": a2["params"]["W0"], "g": a2["params"]["g"], "c_zeros_w": a2["params"]["c_zeros_w"],
                     "heat_k_c_per_w": a2["burst_heat"]["k_used_c_per_w"], "P_idle_w": a2["burst_heat"]["P_idle_w"], "source": f"{C.M8_REL} aifoundry2"},
        "frozen_bands": {"M8": {"mhz": round(a2["bands"]["q95_abs_mhz_e2e"], 2), "board_w": round(a2["bands"]["q95_abs_board_w_e2e"], 2), "die_c": round(a2["burst_heat"]["q95_abs_c"], 2)},
                         "M7_M6": {"mhz": 21.3, "board_w": 3.37, "die_c": 1.41},
                         "source": "m8.json aifoundry2.bands and burst_heat.q95_abs_c; m7.json for M7 and M6; as each tile's _95 in the predictions file"},
        "tiles": tiles, "dropped": dropped, "n_run": len(run_tiles), "n_governed": ng, "n_pinned": npn,
        "replicate": rep, "replicate_dropped": rep_dropped, "reference": ref, "plan_bars_at_full_n": plan_bars,
        "admission": admission, "dry_c_w": dry_c, "dma": {"e143": e143_gaps()},
        "scale": {"predicted": sa, "M8_applies_g": a2["params"]["g"], "measured_in_training": a2["scale_vs_a3"], "source": f"{SCALE_REL}; {C.M8_REL} aifoundry2"},
        "rules": {"safety": STOPS, "limit_w": LIMIT_W, "peak_lock_w": PEAK_LOCK_W, "min_passes": 2,
                  "min_tiles": {"F1": 8, "F2": 8, "W1": 8, "W2": 8, "H1": 10, "coverage": 10, "PK": 10}, "replicate_mhz": 25.0, "replicate_w": 3.37,
                  "boot": {"draws": C.BOOT_DRAWS, "seed": C.BOOT_SEED, "form": "e160_common.boot_rms_range"},
                  "c_check": "a burst counts for the registered scores only if every launch of it (the calibration launch included) has a C record and reads "
                             "PASS in ccheck.py check (bit-exact against Q139(k)'s reference); ROUNDING, UNMODELLED, FAIL and a missing record are not checked",
                  "dma": {"projected_held_max_s": 7.2, "budget_s": 7.5, "launches": 17,
                          "rule": "the smoke's median launch gap less E143's smoke median is the C log's extra time per launch (delta); the session runs only if "
                                  "E143's longest device-held time (s1) + 17 x delta <= 7.2 s, else QUEUE-HALT"},
                  "scale_1pct": 0.01},
    }
    p = os.path.join(HERE, "predictions-e160.json")
    json.dump(out, open(p, "w"), indent=1, sort_keys=False)
    print(f"predictions-e160.json sha256 {C.sha256_file(p)}")
    print(f"{len(tiles)} tiles; dropped (M8 95% peak > {LIMIT_W} W): {dropped}; run {len(run_tiles)}: {ng} governed (M8 < 795 MHz), {npn} pinned")
    print(f"replicates {list(rep)}; dropped replicates {list(rep_dropped)} ({[v['dropped_why'] for v in rep_dropped.values()]})")
    print(f"reference: governed {ref['governed']['n']} rows, {ref['governed']['rms_mhz']} MHz, {ref['governed']['rms_w']} W; pinned {ref['pinned']['n']} rows, "
          f"{ref['pinned']['rms_mhz']} MHz, {ref['pinned']['rms_w']} W; heat {ref['heat']['n']} runs, {ref['heat']['rms_c']} C; peak excess median "
          f"{ref['peak']['median_w']:.3f} W, q95 {ref['peak']['q95_w']:.3f} W")
    print("bars at full n (2.5%, 97.5% of the bootstrap rms):", json.dumps(plan_bars))
    top = sorted(((v["fixed_p800_w"], k) for k, v in admission.items() if not (C.name_of(k) in tiles and tiles[C.name_of(k)]["dropped"])), reverse=True)[:6]
    print(f"admission (run tiles): highest estimates {top}; limit {LIMIT_W} W, lock {PEAK_LOCK_W} W; stops {STOPS}")
    print("dma (E143's launches):", json.dumps(out["dma"]["e143"]))
    for name, t in sorted(tiles.items(), key=lambda kv: (kv[1]["dropped"], kv[1]["group"], kv[1]["type"], kv[0])):
        m = t["models"]["M8"]
        print(f"  {'DROPPED ' if t['dropped'] else ''}{t['group']:8s} p{t['priority']} {t['class']} {name:32s} M8 {m['burst_mhz']:6.1f} MHz {m['burst_board_w']:6.2f} W "
              f"D {m['burst_D_w']:6.2f} rise {m['burst_die_rise_c']:5.2f} C peak {m['peak_board_w']:6.2f}/{m['peak_board_hi95_w']:6.2f} W"
              f"  M7 {t['models']['M7']['burst_mhz']:6.1f}/{t['models']['M7']['burst_board_w']:6.2f}  M6 {t['models']['M6']['burst_mhz']:6.1f}/{t['models']['M6']['burst_board_w']:6.2f}")


if __name__ == "__main__":
    main()
