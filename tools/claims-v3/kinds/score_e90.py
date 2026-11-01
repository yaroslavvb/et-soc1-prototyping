#!/usr/bin/env python3
"""E90 scorer (Q130): every registered rule of tools/claims-v3/kinds/E90.md, thresholds and frozen numbers read from
predictions-e90.json, on reduce_e90.py's output (E78's reduction, unchanged, with E90's items). Standard library only.
Written after the registration commit (6f737d61) and before any pass was read; it changes no rule.

    python3 tools/claims-v3/kinds/score_e90.py --e90 e90.json [--e90-arm leak0.1994=e90-leak0.1994.json ...]
        --json scored.json --md results.md [--label <arm name>]

It refuses to score if E78's e78.json or e90.json differs from the sha256 predictions-e90.json records. The unit of
replication is the pass; fewer than 3 kept passes make every rule NOT SCORED in this input (E90.md: the dips-removed
arm is then the registered reading). Every step is paired per pass. Verdicts at the leakage arms are reported beside
the primary; a verdict that moves between arms (NOT SCORED aside) is marked slope-sensitive.
"""
import argparse
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MIN_PASSES = 3


def mean_ci(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not v:
        return {"mean": None, "se": None, "n": 0, "ci95": None}
    m = statistics.fmean(v)
    if len(v) < 2:
        return {"mean": m, "se": None, "n": 1, "ci95": None}
    se = statistics.stdev(v) / math.sqrt(len(v))
    return {"mean": m, "se": se, "n": len(v), "ci95": se * T95.get(len(v) - 1, 1.96)}


def combine(vs):
    vs = list(vs)
    if any(v == "FAIL" for v in vs):
        return "FAIL"
    if any(v in ("NOT SCORED", "UNRESOLVED") for v in vs):
        return "NOT SCORED"
    if all(v == "PASS" for v in vs):
        return "PASS"
    return "INCONCLUSIVE"


def pp(res, p, name, key="D"):
    e = res["per_pass"].get(str(p), {}).get(name)
    return None if e is None else e.get(key)


def diffs(res, passes, hi, lo):
    out = []
    for p in passes:
        a, b = pp(res, p, hi), pp(res, p, lo)
        if a is not None and b is not None:
            out.append(a - b)
    return out


def below_threshold(mc, thr):
    if mc["n"] < MIN_PASSES or mc["ci95"] is None:
        return "UNRESOLVED"
    lo, hi = mc["mean"] - mc["ci95"], mc["mean"] + mc["ci95"]
    return "PASS" if hi <= thr else ("FAIL" if lo > thr else "INCONCLUSIVE")


def inside_band(mc, band):
    if mc["n"] < MIN_PASSES or mc["ci95"] is None:
        return "UNRESOLVED"
    lo, hi = mc["mean"] - mc["ci95"], mc["mean"] + mc["ci95"]
    if -band <= lo and hi <= band:
        return "PASS"
    if lo > band or hi < -band:
        return "FAIL"
    return "INCONCLUSIVE"


def item_mean(res, name, key="D"):
    it = res["items"].get(name) or {}
    v = it.get(key)
    return v.get("mean") if isinstance(v, dict) else v


def flips(reg, spec, name):
    """Designed sign flips per op (A + B) of an item: E90's tiles from the freeze, E78's from e90.json's references,
    and 0 for a constant (every element the same: ones, anchor_pi)."""
    t = reg["tiles"].get(name) or spec["e78_references"].get(name)
    if t is None:
        return 0
    st = t.get("stats", t)
    return st["sign_flips_per_op_a"] + st["sign_flips_per_op_b"]


def score(res, reg, spec):
    passes = res.get("passes", [])
    enough = len(passes) >= MIN_PASSES
    out = {"passes": passes, "enough_passes": enough, "steps": {}, "draws": {}, "spread": {}, "tiles": {},
           "rules": {}}
    # ---- the sign steps (R1, R2, R3)
    for k, s in reg["steps"].items():
        mc = mean_ci(diffs(res, passes, s["hi"], s["lo"]))
        if s["rule"] == "E90-R3":
            v = inside_band(mc, s["band_w"])
        else:
            v = below_threshold(mc, s["threshold_w"])
        if not enough:
            v = "NOT SCORED"
        # per flipped sign bit, at the measured op rate of the higher tile
        fl = None
        f_hi, f_lo = flips(reg, spec, s["hi"]), flips(reg, spec, s["lo"])
        rate = item_mean(res, s["hi"], "rate")
        if f_hi is not None and rate and mc["mean"] is not None and (f_hi - f_lo) > 0:
            fl = 1e15 * mc["mean"] / ((f_hi - f_lo) * rate)
        out["steps"][k] = {"rule": s["rule"], "hi": s["hi"], "lo": s["lo"], "step_w": mc,
                           "P_bits_w": s["P_bits_w"], "threshold_w": s.get("threshold_w"), "band_w": s.get("band_w"),
                           "step_over_P_bits": (mc["mean"] / s["P_bits_w"]) if (mc["mean"] is not None and s["P_bits_w"]) else None,
                           "fJ_per_flipped_sign_bit": fl, "verdict": v,
                           "P_bits_w_E67_clean_arm": s.get("P_bits_w_E67_clean_arm")}
    R = out["rules"]
    for rule in ("E90-R1", "E90-R2", "E90-R3"):
        vs = [out["steps"][k]["verdict"] for k in reg["rules"][rule]["steps"]]
        R[rule] = {"verdict": "NOT SCORED" if not enough else combine(vs),
                   "steps": {k: out["steps"][k]["verdict"] for k in reg["rules"][rule]["steps"]}}
    # ---- the redraws (R4, R5) and the spread report
    band = reg["rules"]["E90-R4"]["band_w"]
    per_kind = {}
    sq, opposite = [], []
    for name, t in reg["tiles"].items():
        if t["group"] != "redraw":
            continue
        c = t["committed"]
        mc = mean_ci(diffs(res, passes, name, c))
        pred = t["q130n_delta_vs_committed_w"]
        if mc["mean"] is not None:
            sq.append((mc["mean"] - pred) ** 2)
            if abs(pred) >= 0.30 and mc["n"] >= MIN_PASSES and mc["ci95"] is not None:
                lo, hi = mc["mean"] - mc["ci95"], mc["mean"] + mc["ci95"]
                if (pred > 0 and hi < 0) or (pred < 0 and lo > 0):
                    opposite.append(name)
        out["draws"][name] = {"committed": c, "minus_committed_w": mc, "q130n_delta_w": pred,
                              "D": (res["items"].get(name) or {}).get("D"),
                              "gated_lane_frac": t["stats"]["gated_lane_frac"],
                              "bus_bits_per_op": t["stats"]["bus_bits_per_op"]}
        per_kind.setdefault(c, []).append(name)
    kv = {}
    for c, names in per_kind.items():
        per_pass_mean = []
        for p in passes:
            vals = [pp(res, p, n) for n in names]
            b = pp(res, p, c)
            if b is not None and all(v is not None for v in vals):
                per_pass_mean.append(statistics.fmean(vals) - b)
        mc = mean_ci(per_pass_mean)
        v = inside_band(mc, band) if enough else "NOT SCORED"
        kv[c] = v
        # spread: four tiles (the committed one and three draws), pass means; one tile's between-pass sd
        tiles4 = [c] + sorted(names)
        means = [item_mean(res, n) for n in tiles4]
        sds = []
        for n in tiles4:
            vals = [pp(res, p, n) for p in passes]
            vals = [x for x in vals if x is not None]
            if len(vals) >= 2:
                sds.append(statistics.stdev(vals))
        sp = {"tiles": tiles4, "D_means_w": means, "draws_minus_committed_mean_w": mc, "verdict_R4": v}
        if all(m is not None for m in means) and len(means) >= 2:
            var_t = statistics.variance(means)
            s_pass = statistics.fmean(sds) if sds else None
            npass = len(passes)
            sp["sd_between_tiles_w"] = math.sqrt(var_t)
            sp["sd_between_passes_one_tile_w"] = s_pass
            sp["sd_tile_component_w"] = (math.sqrt(max(0.0, var_t - (s_pass ** 2) / npass))
                                         if s_pass is not None and npass else None)
            sp["range_w"] = max(means) - min(means)
        out["spread"][c] = sp
    R["E90-R4"] = {"verdict": "NOT SCORED" if not enough else combine(kv.values()), "kinds": kv}
    rms = math.sqrt(statistics.fmean(sq)) if sq else None
    if not enough or rms is None:
        v5 = "NOT SCORED"
    elif rms <= 0.50 and not opposite:
        v5 = "PASS"
    elif rms > 1.00 or opposite:
        v5 = "FAIL"
    else:
        v5 = "INCONCLUSIVE"
    R["E90-R5"] = {"verdict": v5, "rms_w": rms, "opposite_resolved": opposite}
    # ---- S1, S2
    e78 = reg["e78_reference"]
    cells = reg["rules"]["E90-S1"]["cells"]
    s1 = {}
    for c, b in cells.items():
        m = item_mean(res, c)
        d = (m - e78[c]["D_w"]) if m is not None else None
        s1[c] = {"D_w": m, "e78_D_w": e78[c]["D_w"], "diff_w": d, "band_w": b,
                 "inside": bool(d is not None and abs(d) <= b)}
    R["E90-S1"] = {"verdict": "NOT SCORED" if not enough else ("PASS" if all(x["inside"] for x in s1.values()) else "FAIL"),
                   "cells": s1}
    inside, rows = 0, {}
    for name, t in reg["tiles"].items():
        m = item_mean(res, name)
        lo, hi = t["q130n_predictor"]["pi95_w"]
        ok = m is not None and lo <= m <= hi
        inside += int(ok)
        rows[name] = {"D_w": m, "q130n_point_w": t["q130n_predictor"]["point_w"], "pi95_w": [lo, hi], "inside": ok}
    R["E90-S2"] = {"verdict": "NOT SCORED" if not enough else ("PASS" if inside >= 14 else "FAIL"),
                   "inside": inside, "of": len(rows), "tiles": rows}
    # ---- every E90 tile and the E78 kinds beside them, reported
    for name in list(reg["tiles"]) + list(reg["e78_reference"]):
        it = res["items"].get(name)
        if it is None:
            continue
        out["tiles"][name] = {k: it.get(k) for k in ("D", "S", "D32", "Drail", "dT_win", "pj_op_S", "pj_op_D",
                                                     "pj_mac_S", "pj_mac_D", "rate", "duty", "gated_lane_frac",
                                                     "bus_bits_per_op")}
        out["tiles"][name]["D_pred_w"] = (reg["tiles"].get(name) or {}).get("D_pred_w")
    return out


def fmt(mc, nd=3):
    if not mc or mc.get("mean") is None:
        return "n/a"
    if mc.get("ci95") is None:
        return f"{mc['mean']:.{nd}f}"
    return f"{mc['mean']:.{nd}f} ± {mc['ci95']:.{nd}f}"


def write_md(sc, arms, path, label):
    L = [f"# E90 scored ({label})", "",
         f"Kept passes: {sc['passes']} ({'enough' if sc['enough_passes'] else 'FEWER THAN 3: NOT SCORED'}).", "",
         "## Rules", "", "| rule | verdict | " + " | ".join(arms) + " | slope-sensitive |", "|---|---|" + "---|" * len(arms) + "---|"]
    for r, v in sc["rules"].items():
        av = [arms[a]["rules"].get(r, {}).get("verdict", "n/a") for a in arms]
        L.append(f"| {r} | **{v['verdict']}** | " + " | ".join(av) + f" | {v.get('slope_sensitive', False)} |")
    L += ["", "## Sign steps (paired per pass, board W over the type's zeros)", "",
          "| step | rule | measured | P_bits | threshold / band | step / P_bits | fJ per flipped sign bit | verdict |",
          "|---|---|---|---|---|---|---|---|"]
    for k, s in sc["steps"].items():
        thr = s["threshold_w"] if s["threshold_w"] is not None else f"±{s['band_w']}"
        ratio = f"{s['step_over_P_bits']:.2f}" if s["step_over_P_bits"] is not None else "n/a"
        fj = f"{s['fJ_per_flipped_sign_bit']:.0f}" if s["fJ_per_flipped_sign_bit"] is not None else "n/a"
        L.append(f"| `{k}` | {s['rule']} | {fmt(s['step_w'])} | {s['P_bits_w']:.3f} | {thr} | {ratio} | {fj} | **{s['verdict']}** |")
    L += ["", "## Redraws (D(draw) − D(committed), paired per pass)", "",
          "| draw | gated | bus bits/op | measured | Q130(n) delta |", "|---|---|---|---|---|"]
    for n, d in sc["draws"].items():
        L.append(f"| `{n}` | {d['gated_lane_frac']:.4f} | {d['bus_bits_per_op']} | {fmt(d['minus_committed_w'])} | {d['q130n_delta_w']:+.3f} |")
    L += ["", "## Tile spread per rule (pass means)", "",
          "| rule | D of committed, d1, d2, d3 (W) | sd between tiles | one tile's between-pass sd | tile component | R4 |",
          "|---|---|---|---|---|---|"]
    for c, s in sc["spread"].items():
        dm = ", ".join(f"{x:.3f}" if x is not None else "n/a" for x in s["D_means_w"])
        g = lambda k: f"{s[k]:.3f}" if s.get(k) is not None else "n/a"  # noqa: E731
        L.append(f"| `{c}` | {dm} | {g('sd_between_tiles_w')} | {g('sd_between_passes_one_tile_w')} | {g('sd_tile_component_w')} | {s['verdict_R4']} |")
    L += ["", "## Every E90 tile and the E78 kinds beside it", "", "| item | D (W) | S (W) | pJ/MAC (S) | dT (C) | predicted D |",
          "|---|---|---|---|---|---|"]
    for n, t in sc["tiles"].items():
        pj = t.get("pj_mac_S")
        pjs = fmt(pj, 4) if isinstance(pj, dict) else "n/a"
        dt = t.get("dT_win")
        dts = fmt(dt, 2) if isinstance(dt, dict) else "n/a"
        pr = t.get("D_pred_w")
        L.append(f"| `{n}` | {fmt(t.get('D'))} | {fmt(t.get('S'))} | {pjs} | {dts} | {pr if pr is not None else ''} |")
    open(path, "w").write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e90", required=True)
    ap.add_argument("--e90-arm", action="append", default=[])
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    ap.add_argument("--label", default="primary: leakage slope auto")
    a = ap.parse_args()
    reg = json.load(open(os.path.join(HERE, "predictions-e90.json")))
    bad = []
    for key in ("e78_reduction", "e90_json"):
        f = reg["inputs_frozen"][key]
        have = hashlib.sha256(open(os.path.join(ROOT, f["path"]), "rb").read()).hexdigest()
        if have != f["sha256"]:
            bad.append(f"{f['path']}: {have} != {f['sha256']}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    res = json.load(open(a.e90))
    e90spec = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e90_json"]["path"])))
    sc = score(res, reg, e90spec)
    arms = {}
    for arm in a.e90_arm:
        name, path = arm.split("=", 1)
        arms[name] = score(json.load(open(path)), reg, e90spec)
    for r, v in sc["rules"].items():
        vs = {v["verdict"]} | {arms[x]["rules"][r]["verdict"] for x in arms}
        vs.discard("NOT SCORED")
        v["slope_sensitive"] = len(vs) > 1
        v["arms"] = {x: arms[x]["rules"][r]["verdict"] for x in arms}
    sc["arms_steps"] = {x: {k: {"step_w": s["step_w"], "verdict": s["verdict"]} for k, s in arms[x]["steps"].items()}
                        for x in arms}
    sc["label"] = a.label
    json.dump(sc, open(a.json, "w"), indent=1)
    write_md(sc, arms, a.md, a.label)
    print(json.dumps({r: v["verdict"] for r, v in sc["rules"].items()}))


if __name__ == "__main__":
    main()
