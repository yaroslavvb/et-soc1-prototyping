#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(k6): the P8 scorer at 600 MHz, for E171 (aifoundry3) and E172 (aifoundry1 card 1), as their registrations register it
(tools/claims-v3/e171/E171.md and tools/claims-v3/e172/E172.md, "How the scorer computes them"), on pool 8's rules
(tools/claims-v3/m10/POOL8-REGISTRATION.md section 7, with dated notes A1 and A2). Nothing here is fitted or tuned, and no line is
written here: every line comes from predict_pool8_a2.py's functions (the frozen predictor's entry point, lab 97765c0a), which this file
imports after their hash lists pass, at the scored n and with the registered seeds.

  score     python3 -B score_p8_600.py score --run E171|E172 --reduction <primary reduction json> --raw <raw copy of the run's dirs>
                --ccheck <ccheck --out json> [--arm name=<reduction json> ...] [--since <epoch s>] [--json scored.json] [--md results.md]
  ka-pooled python3 -B score_p8_600.py ka-pooled <E171 scored.json> <E172 scored.json> [--json out]

Order, enforced: (1) the predictor's hash lists and the freeze's sha256 of this card's predictions file; (2) every session that must carry
a C log (ccsessions_p8.check) has a finished check, else exit 4 and nothing written; (3) the frozen predict_pool8.scale on the reduction's
anchor items only, then the scale's anchors are checked (exit 5 and nothing written if any is not M10's float anchor or pool 8's scale
anchor, or is a check or zeros anchor); (4) the frozen predict_pool8.primary; (5) the C status per tile (E163's c_status, copied);
(6) the rules. Fewer than 2 kept passes: every rule NOT SCORED. Exit 0 when scored.json is written, 9 when a frozen input differs.

The pieces copied from tools/claims-v3/e163/score_e163.py (frozen, 442474d5; E153's statistics) are marked "E163's, copied": measured,
c_status and the paired form of compare_rule (here with the P8 registration's 20,000 draws and seeds). Python 3.9 with numpy (the
predictor's chain needs it): the Intel's /usr/bin/python3. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import gzip
import hashlib
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PRED_DIR = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142p-pool8-predictor")
FREEZE_SUMS = os.path.join(TOP, "docs", "reports", "data", "2026-11-05-q142x-pool8-freeze", "SHA256SUMS")
B8 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind8")
RUN_CARD = {"E171": "aifoundry3", "E172": "aifoundry1c1"}
FLOATS = ("fp32", "fp16")
FORMATS = ("fp32", "fp16", "int8")
RULES = ["P8-KC", "P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1", "P8-M1", "P8-M1f", "P8-M1i", "P8-A1", "P8-KA", "P8-H1", "P8-H2",
         "P8-H3", "P8-H4", "P8-LG", "P8-G", "P8-HM"]
EXIT_FROZEN, EXIT_NO_C, EXIT_SCALE = 9, 4, 5
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
_M = {}


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def A2():
    """predict_pool8_a2.py (its own check_lists runs before predict_pool8 is imported, in A2.P())"""
    if "A2" not in _M:
        if PRED_DIR not in sys.path:
            sys.path.insert(0, PRED_DIR)
        import predict_pool8_a2 as a2  # noqa: E402
        _M["A2"] = a2
    return _M["A2"]


def P():
    return A2().P()


def CS():
    if "CS" not in _M:
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import ccsessions_p8 as c  # noqa: E402
        _M["CS"] = c
    return _M["CS"]


def welch():
    if "W" not in _M:
        p = os.path.join(TOP, "tools", "claims-v3", "ccheck")
        if p not in sys.path:
            sys.path.insert(0, p)
        import pick6  # noqa: E402  (Q139(k)'s, unchanged)
        _M["W"] = pick6.welch
    return _M["W"]


# ------------------------------------------------------------------------------------------------- statistics
def rms(v):
    v = [float(x) for x in v]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v]
    return sum(v) / len(v) if v else None


def measured(res, tiles, key, min_tile_passes):
    """E163's, copied: a tile's mean over the kept passes it ran in, from the reduction's per-pass values; short tiles named"""
    out, short = {}, []
    for t in tiles:
        vals = []
        for p in res.get("passes", []):
            r = res.get("per_pass", {}).get(str(p), {}).get(t)
            if not r:
                continue
            v = r.get(key)
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                vals.append(float(v))
        if len(vals) >= min_tile_passes:
            out[t] = {"mean": sum(vals) / len(vals), "n": len(vals), "sd": statistics.stdev(vals) if len(vals) > 1 else None,
                      "per_pass": vals}
        else:
            short.append(t)
    return out, short


def c_status(want, res, ccheck_files, passes_dir):
    """E163's, copied (the tile list given): per tile, over every launch record of the tile in the kept passes' runs.jsonl, the ccheck
    verdict of the C record with the same t_start_ms and t_end_ms. all_pass only if every launch has a PASS record."""
    verdict = {}
    for f in ccheck_files:
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            for v in json.load(fh)["launches"]:
                verdict[(v.get("t_start_ms"), v.get("t_end_ms"))] = v["verdict"]
    per = {}
    for p in res.get("passes", []):
        rp = os.path.join(passes_dir, f"p{p}", "runs.jsonl")
        if not os.path.exists(rp):
            for t in want:
                per.setdefault(t, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "passes_without_log": []})
                per[t]["passes_without_log"].append(p)
            continue
        for line in open(rp):
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            t = r.get("item")
            if t not in want:
                continue
            s = per.setdefault(t, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "passes_without_log": []})
            s["launches"] += 1
            v = verdict.get((r.get("t_start_ms"), r.get("t_end_ms")))
            if v is None:
                s["missing"] += 1
            elif v == "PASS":
                s["PASS"] += 1
            else:
                s["other"][v] = s["other"].get(v, 0) + 1
    for t, s in per.items():
        s["all_pass"] = s["launches"] > 0 and s["PASS"] == s["launches"] and not s["passes_without_log"]
        s["pass_or_rounding"] = s["launches"] > 0 and (s["PASS"] + s["other"].get("ROUNDING", 0)) == s["launches"] and \
            not s["passes_without_log"]
    return per


def paired(err_a, err_b, sel, rule=None, draws=None, seed=None):
    """the registered paired form (E171.md / E172.md): E163's compare_rule, copied, with the P8 registration's draws and seed:
    d = rms(a) - rms(b) over sel; each draw takes len(sel) tiles with replacement; [int(0.025 x draws)], [int(0.975 x draws) - 1]"""
    draws = draws or P().frozen()["reg"]["scoring"]["paired_draws"]
    seed = P().seed_of(rule) if seed is None else seed
    d0 = rms([err_a[t] for t in sel]) - rms([err_b[t] for t in sel])
    rng = random.Random(seed)
    ds = []
    for _ in range(draws):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(rms([err_a[t] for t in s]) - rms([err_b[t] for t in s]))
    ds.sort()
    lo, hi = ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds)) - 1]
    v = "BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED")
    return {"verdict": v, "d_rms": d0, "lo95": lo, "hi95": hi, "n": len(sel), "draws": draws, "seed": seed}


def line_of(refs, mix, rule, stat, draws=None, seed=None):
    """the line at the scored n: predict_pool8_a2.mix_range (for one format it equals predict_pool8.boot_range, A2's U4)"""
    return A2().mix_range(refs, mix, rule, stat, draws, seed)


def rms_rule(rule, err, sel, refs, minimum, unit, draws=None, seed=None):
    sel = [t for t in sel if err.get(t) is not None]
    if len(sel) < minimum:
        return {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {minimum}", "n": len(sel), "tiles": sel}
    mix = {}
    for t in sel:
        mix[t.split(".")[0]] = mix.get(t.split(".")[0], 0) + 1
    lo, hi = line_of({k: refs[k] for k in mix}, mix, rule, "rms", draws, seed)
    r = rms([err[t] for t in sel])
    return {"verdict": "PASS" if r <= hi else "FAIL", "rms": r, "line": [lo, hi], "n": len(sel), "mix": mix, "tiles": sel, "unit": unit,
            "below_line": r < lo}


def bias_rule(rule, err, sel, refs, minimum, draws=None, seed=None):
    sel = [t for t in sel if err.get(t) is not None]
    if len(sel) < minimum:
        return {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {minimum}", "n": len(sel), "tiles": sel}
    mix = {}
    for t in sel:
        mix[t.split(".")[0]] = mix.get(t.split(".")[0], 0) + 1
    lo, hi = line_of({k: refs[k] for k in mix}, mix, rule, "mean", draws, seed)
    b = mean([err[t] for t in sel])
    v = "PASS" if lo <= b <= hi else ("FAIL HIGH" if b < lo else "FAIL LOW")
    return {"verdict": v, "mean": b, "line": [lo, hi], "n": len(sel), "mix": mix, "tiles": sel, "unit": "W",
            "reading": "HIGH = the model predicts more power than measured (measured - model below the line); LOW = less"}


def coverage_rule(inside, sel, minimum):
    have = [t for t in sel if inside.get(t) is not None]
    n = len(have)
    if n < minimum:
        return {"verdict": "NOT SCORED", "why": f"{n} tiles, fewer than {minimum}", "n": n}
    k = sum(1 for t in have if inside[t])
    low = A2().binom_low(n)
    return {"verdict": "PASS" if k >= low else "FAIL", "inside": k, "n": n, "inside_at_least": low,
            "outside": sorted(t for t in have if not inside[t])}


def paired_rule(rule, ea, eb, sel, minimum, draws=None, seed=None):
    sel = sorted(t for t in sel if ea.get(t) is not None and eb.get(t) is not None)
    if len(sel) < minimum:
        return {"verdict": "NOT SCORED", "why": f"{len(sel)} tiles, fewer than {minimum}", "n": len(sel)}
    return dict(paired(ea, eb, sel, rule, draws, seed), tiles=sel)


def ka_test(rows):
    """P8-KA: sum e_p^2 < sum e_0^2 and every measured D inside M10's primary 95% band"""
    ep = [r["e_primary"] for r in rows]
    e0 = [r["e_a_priori"] for r in rows]
    inside = [r["inside_power"] for r in rows]
    ok = sum(x * x for x in ep) < sum(x * x for x in e0) and all(inside)
    return {"verdict": "PASS" if ok else "FAIL", "n": len(rows), "sum_e_primary_sq": sum(x * x for x in ep),
            "sum_e_a_priori_sq": sum(x * x for x in e0), "all_inside": all(inside)}


def lg_rule(pred, meas, sel):
    """P8-LG: delta = this session's D - the tile's lg_reference D (the entry whose tile is the re-run's name, else the first), grouped by
    that entry's session; design_power_groups.lg_test, as registered (A2-4's function, the same one intervals-pool8.json's block used)"""
    D = A2().DPG()
    groups, tiles, noref = {}, {}, []
    W = welch()
    for t in sorted(sel):
        refs = pred["tiles"][t].get("lg_reference") or []
        if not refs or t not in meas:
            if not refs:
                noref.append(t)
            continue
        pick = next((r for r in refs if r.get("tile") == t), refs[0])
        x = meas[t]
        delta = x["mean"] - float(pick["D_w"])
        groups.setdefault(pick["session"], []).append((float(pick["D_w"]), delta))
        rec = {"session": pick["session"], "D_ref_w": pick["D_w"], "D_w": x["mean"], "delta_w": delta}
        se_new = (x["sd"] / math.sqrt(x["n"])) if x.get("sd") is not None and x["n"] > 1 else None
        if se_new and pick.get("se_w") and pick.get("n") and int(pick["n"]) > 1:
            rec["welch"] = W(float(pick["D_w"]), float(pick["se_w"]), int(pick["n"]), x["mean"], se_new, x["n"])
        tiles[t] = rec
    out = D.lg_test(groups, detail=True)
    out.update({"tiles": tiles, "no_reference": noref, "groups_n": {s: len(v) for s, v in groups.items()}})
    return out


def g_rule(V):
    parts = {r: V[r] for r in ("P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1")}
    m1 = V["P8-M1"]
    fail = any(v.startswith("FAIL") for v in parts.values()) or m1 == "WORSE"
    ok = all(v == "PASS" for v in parts.values()) and m1 in ("BETTER", "NOT RESOLVED")
    return {"verdict": "FAIL" if fail else ("PASS" if ok else "NOT SCORED"), "parts": dict(parts, **{"P8-M1": m1})}


# ------------------------------------------------------------------------------------------------- inputs
def freeze_sums():
    out = {}
    for line in open(FREEZE_SUMS):
        if line.strip():
            h, p = line.split(None, 1)
            out[p.strip().lstrip("*")] = h
    return out


def load_pred(card):
    rel = f"tools/claims-v3/kinds/blind8/predictions-pool8-{card}.json"
    path = os.path.join(TOP, rel)
    want = freeze_sums().get(rel)
    have = sha(path) if os.path.exists(path) else "missing"
    if not want or have != want:
        raise Refuse(EXIT_FROZEN, f"{rel}: sha256 {have[:12]} is not the freeze's {str(want)[:12]} (Q142(x) SHA256SUMS)")
    iv = "tools/claims-v3/kinds/blind8/intervals-pool8.json"
    if sha(os.path.join(TOP, iv)) != freeze_sums().get(iv):
        raise Refuse(EXIT_FROZEN, f"{iv} is not the freeze's")
    return path, json.load(open(path))


def check_scale(sc, pred):
    """'the check anchors never enter s': every anchor the scale used is M10's float anchor or pool 8's scale anchor, and none is a
    check anchor, a zeros anchor or a non-anchor tile"""
    allowed = set(P().m10_anchor_names()) | set(pred["sets"]["scale_anchors_pool8"])
    roles = pred.get("roles") or {}
    bad = []
    for n in sc.get("anchors_used", []):
        role = (roles.get(n) or {}).get("role")
        if n in pred["sets"]["KA"] or role == "check":
            bad.append(f"{n}: a check anchor")
        elif n in pred["sets"]["zeros_anchors"] or role == "zeros":
            bad.append(f"{n}: a zeros anchor")
        elif n not in allowed:
            bad.append(f"{n}: neither M10's float anchor nor pool 8's scale anchor")
    if bad:
        raise Refuse(EXIT_SCALE, "the scale read an anchor it must not (registration section 3; E171/E172.md): " + "; ".join(bad))
    return {"anchors_used": sc.get("anchors_used"), "allowed": sorted(allowed), "ok": True}


# ------------------------------------------------------------------------------------------------- one reduction's rules
def score_reduction(pred_path, pred, card, red_path, cstat=None, tiles_c_ok=None, draws=None):
    p = P()
    res = json.load(open(red_path))
    out = {"reduction": os.path.relpath(red_path, TOP) if red_path.startswith(TOP + os.sep) else os.path.basename(red_path),
           "reduction_sha256": sha(red_path), "kept_passes": res.get("passes", []), "set_aside": res.get("passes_set_aside")}
    reg = p.frozen()["reg"]
    mins = reg["scoring"]["minimum_tiles"]
    sc = p.scale(pred, red_path)
    out["scale"] = {k: sc[k] for k in ("s_float", "anchors_used", "anchors_missing", "anchors_at_nominal_rate", "ratios", "reduction_sha256")}
    out["scale_check"] = check_scale(sc, pred)
    pr = p.primary(pred, red_path, sc)
    S = pred["sets"]
    names = sorted(pred["tiles"])
    if len(res.get("passes", [])) < 2:
        out["verdicts"] = {r: "NOT SCORED" for r in RULES}
        out["NOT SCORED"] = f"{len(res.get('passes', []))} kept passes, fewer than 2"
        return out
    mD, shortD = measured(res, names, "D", 2)
    mT, shortT = measured(res, names, "dT_win", 2)
    out["short_tiles"] = {"power": shortD, "heat": shortT}
    items = res.get("items", {})
    out["measured_vs_items_max_abs_w"] = max([abs(mD[t]["mean"] - items[t]["D"]["mean"]) for t in mD if t in items and
                                              isinstance(items[t].get("D"), dict)] or [0.0])
    rows = {}
    for t in names:
        r, q = pred["tiles"][t], pr["tiles"][t]
        x, h = mD.get(t), mT.get(t)
        row = {"type": r["type"], "case": r.get("case"), "priority": r.get("priority"), "real": r.get("real"), "role": r.get("anchor_role"),
               "rerun_of": r.get("rerun_of"), "M10_primary_w": q["M10_primary_w"], "M10_primary_95": q["M10_primary_95"],
               "M10_a_priori_w": q["M10_a_priori_w"], "M10_stated_w": r["M10"]["D_stated_w"], "M9_w": q["M9_w"], "M9_95": q["M9_95"],
               "M9_nominal_w": q["M9_nominal_w"], "rate_per_s": q["rate_per_s"], "rate_source": q["rate_source"],
               "M10_heat_c": q["M10_heat"]["dT_win_c"], "M10_heat_95": q["M10_heat"]["dT_win_95"], "M9_heat_c": q["M9_heat"]["dT_win_c"]}
        if x:
            row.update(D_w=x["mean"], n_passes=x["n"], per_pass=x["per_pass"], e_primary=x["mean"] - q["M10_primary_w"],
                       e_a_priori=x["mean"] - q["M10_a_priori_w"], e_stated=x["mean"] - r["M10"]["D_stated_w"], e_M9=x["mean"] - q["M9_w"],
                       e_M9_nominal=x["mean"] - q["M9_nominal_w"],
                       inside_power=q["M10_primary_95"][0] <= x["mean"] <= q["M10_primary_95"][1],
                       inside_M9=q["M9_95"][0] <= x["mean"] <= q["M9_95"][1])
        if h:
            row.update(dT_w=h["mean"], e_heat=h["mean"] - q["M10_heat"]["dT_win_c"],
                       inside_heat=q["M10_heat"]["dT_win_95"][0] <= h["mean"] <= q["M10_heat"]["dT_win_95"][1])
        if cstat is not None:
            row["c"] = cstat.get(t)
        rows[t] = row
    out["rows"] = rows
    ok = set(names) if tiles_c_ok is None else set(tiles_c_ok)
    out["rules"] = rules_of(pred, card, rows, mD, ok, sc, mins, draws)
    out["verdicts"] = {r: v.get("verdict") for r, v in out["rules"].items()}
    if tiles_c_ok is not None and set(tiles_c_ok) != set(names):
        b = rules_of(pred, card, rows, mD, set(names), sc, mins, draws)
        out["rules_all_tiles_beside"] = {r: {k: v.get(k) for k in ("verdict", "rms", "mean", "line", "n", "inside", "d_rms", "lo95", "hi95")}
                                         for r, v in b.items()}
    out["reported"] = reported(pred, rows, ok)
    return out


def rules_of(pred, card, rows, mD, ok, sc, mins, draws=None):
    p = P()
    cd = p.CARDS[card]
    S = pred["sets"]
    refs = p.ref_errors(cd)
    href = {t: A2().heat_ref(card, t) for t in FORMATS}
    sel = lambda name: [t for t in S[name] if t in ok and t in mD]  # noqa: E731
    bf = {t: [x for x in S["by_format"][t] if x in ok and x in mD] for t in FORMATS}
    ep = {t: r["e_primary"] for t, r in rows.items() if "e_primary" in r}
    e9 = {t: r["e_M9"] for t, r in rows.items() if "e_M9" in r}
    e0 = {t: r["e_a_priori"] for t, r in rows.items() if "e_a_priori" in r}
    eh = {t: r["e_heat"] for t, r in rows.items() if "e_heat" in r and t in ok}
    ip = {t: r["inside_power"] for t, r in rows.items() if "inside_power" in r}
    ih = {t: r["inside_heat"] for t, r in rows.items() if "inside_heat" in r and t in ok}
    R = {}
    for rule, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8")):
        R[rule] = rms_rule(rule, ep, bf[t], refs, mins[rule[3:]], "W", draws)
    R["P8-B1"] = bias_rule("P8-B1", ep, sel("F1"), refs, mins["B1"], draws)
    R["P8-B2"] = bias_rule("P8-B2", ep, sel("I1"), refs, mins["B2"], draws)
    R["P8-C1"] = coverage_rule(ip, sel("N1"), mins["C1"])
    R["P8-M1"] = paired_rule("P8-M1", ep, e9, sel("N1"), mins["M1"], draws)
    R["P8-M1f"] = paired_rule("P8-M1f", ep, e9, sel("F1"), mins["M1f"], draws)
    R["P8-M1i"] = paired_rule("P8-M1i", ep, e9, sel("I1"), mins["M1i"], draws)
    R["P8-A1"] = paired_rule("P8-A1", ep, e0, sel("F1"), mins["A1"], draws)
    ka = [dict(rows[t], tile=t) for t in sorted(S["KA"]) if t in ok and "e_primary" in rows[t]]
    if float(sc["s_float"]) == 1.0:
        R["P8-KA"] = {"verdict": "NOT SCORED", "why": "s = 1: no float scale anchor measured", "n": len(ka)}
    elif len(ka) < mins["KA_session"]:
        R["P8-KA"] = {"verdict": "NOT SCORED", "why": f"{len(ka)} check anchors scored, fewer than {mins['KA_session']}", "n": len(ka)}
    else:
        R["P8-KA"] = dict(ka_test(ka), tiles={r["tile"]: {k: r[k] for k in ("D_w", "M10_primary_w", "M10_a_priori_w", "e_primary", "e_a_priori",
                                                                            "inside_power", "M10_primary_95")} for r in ka})
    for rule, t in (("P8-H1", "fp32"), ("P8-H2", "fp16"), ("P8-H3", "int8")):
        R[rule] = rms_rule(rule, eh, [x for x in bf[t] if x in eh], href, mins[rule[3:]], "C", draws)
    R["P8-H4"] = coverage_rule(ih, sel("N1"), mins["H4"])
    rr = [t for t in S["RR"] if t in ok and t in mD]
    R["P8-LG"] = lg_rule(pred, {t: mD[t] for t in rr}, rr)
    R["P8-LG"]["power_at_design"] = json.load(open(os.path.join(B8, "intervals-pool8.json")))["cards"][card]["rules"]["P8-LG"]["power_pct"]
    V = {r: v["verdict"] for r, v in R.items()}
    R["P8-G"] = g_rule(V)
    R["P8-HM"] = {"verdict": "NOT SCORED", "why": "no hold ran in this session (registration section 7, HM)"}
    return R


def reported(pred, rows, ok):
    """reported beside, never a verdict: M10's frozen a-priori arm at the stated rate, M9 at the nominal rate, per class and over all
    measured tiles, the anchors and the priority-2 kinds"""
    S = pred["sets"]
    out = {}
    for lab, names in (("N1", S["N1"]), ("priority2_kinds", S["other_priorities"]), ("RR", S["RR"]), ("KA", S["KA"]),
                       ("scale_anchors_pool8", S["scale_anchors_pool8"]), ("zeros_anchors", S["zeros_anchors"])):
        have = [t for t in names if t in ok and "e_primary" in rows[t]]
        out[lab] = {"n": len(have)}
        for k in ("e_primary", "e_a_priori", "e_stated", "e_M9", "e_M9_nominal"):
            v = [rows[t][k] for t in have]
            out[lab][k] = {"rms": rms(v), "mean": mean(v)}
    by = {}
    for t in S["N1"]:
        if t in ok and "e_primary" in rows[t]:
            by.setdefault(str(rows[t]["case"]), []).append(t)
    out["N1_by_case"] = {c: {"n": len(v), "M10_rms": rms([rows[t]["e_primary"] for t in v]), "M9_rms": rms([rows[t]["e_M9"] for t in v]),
                             "M10_mean": mean([rows[t]["e_primary"] for t in v])} for c, v in sorted(by.items())}
    rate = [rows[t]["rate_per_s"] for t in S["N1"] if t in ok and rows[t].get("rate_source") == "measured"]
    out["measured_rates"] = len(rate)
    return out


# ------------------------------------------------------------------------------------------------- the session
def score_session(run, red_path, raw, ccheck, arms=(), since=None, draws=None, skip_c_gate=False):
    card = RUN_CARD[run]
    a2 = A2()
    lists = a2.check_lists()
    p = P()
    n_in = p.check_inputs()
    pred_path, pred = load_pred(card)
    out = {"_note": f"Q142(k6) score_p8_600.py: {run} on {card}, pool 8's P8 rules at 600 MHz (E171.md / E172.md; POOL8-REGISTRATION section 7)",
           "run": run, "card": card, "scorer_sha256": sha(os.path.abspath(__file__)),
           "predictor_lists": lists, "pool8_inputs_checked": n_in,
           "predictions": os.path.relpath(pred_path, TOP), "predictions_sha256": sha(pred_path)}
    if not skip_c_gate:
        g = CS().check(run, raw, ccheck, since)
        # paths inside the tree are kept repo-relative (the data directory is public; the runbook's desk-path gate reads it)
        g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
        out["c_sessions"] = {k: g[k] for k in ("sessions", "stoptest", "ccdone", "ok", "listed")}
        if not g["ok"]:
            raise Refuse(EXIT_NO_C, "a session that must carry a C log has no finished check of C (registration, 'The sessions that must carry "
                                    "a C log'); every rule reads NOT SCORED and nothing is written:\n  " + "\n  ".join(g["lines"]))
    res = json.load(open(red_path))
    want = list(pred["tiles"])
    passes_dir = os.path.join(raw, CS().RUNS[run]["dir"]) if raw else None
    cstat = c_status(want, res, [ccheck] if os.path.exists(ccheck) else [ccheck + ".gz"], passes_dir) if (ccheck and passes_dir) else None
    if cstat is not None:
        unmeasured = sorted(t for t in want if not (cstat.get(t) or {}).get("passes_without_log") and (cstat.get(t) or {}).get("launches", 0) == 0)
        cfail = sorted(t for t in want if t not in unmeasured and not (cstat.get(t) or {}).get("all_pass"))
        ok = [t for t in want if t not in cfail]
        kc = {"verdict": "FAIL" if cfail else ("PASS" if any((cstat.get(t) or {}).get("launches") for t in want) else "NOT SCORED"),
              "c_excluded": cfail, "not_measured": unmeasured,
              "launches": sum((cstat.get(t) or {}).get("launches", 0) for t in want), "PASS": sum((cstat.get(t) or {}).get("PASS", 0) for t in want)}
    else:
        ok, kc = None, {"verdict": "NOT SCORED", "why": "no check of C given"}
    prim = score_reduction(pred_path, pred, card, red_path, cstat, ok, draws)
    prim["rules"] = dict({"P8-KC": kc}, **prim.get("rules", {}))
    prim["verdicts"] = dict({"P8-KC": kc["verdict"]}, **prim.get("verdicts", {}))
    out["primary"] = prim
    out["verdicts"] = {r: prim["verdicts"].get(r, "NOT SCORED") for r in RULES}
    out["arms"] = {}
    for nm, path in arms:
        try:
            a = score_reduction(pred_path, pred, card, path, cstat, ok, draws)
            out["arms"][nm] = {"reduction_sha256": a["reduction_sha256"], "kept_passes": a["kept_passes"], "s_float": a["scale"]["s_float"],
                               "verdicts": a["verdicts"], "rules": {r: {k: v.get(k) for k in ("verdict", "rms", "mean", "line", "n", "inside",
                                                                                              "d_rms", "lo95", "hi95")} for r, v in a.get("rules", {}).items()}}
        except Refuse:
            raise
        except Exception as e:  # noqa: BLE001  (an arm that cannot be scored is reported, never the verdict)
            out["arms"][nm] = {"error": f"{type(e).__name__}: {e}"[:400]}
    return out


def markdown(o):
    pr = o["primary"]
    L = [f"# {o['run']} on {o['card']}: P8's rules at 600 MHz (score_p8_600.py)", "",
         f"Predictions `{o['predictions']}` ({o['predictions_sha256'][:12]}); reduction `{pr['reduction']}` ({pr['reduction_sha256'][:12]}); "
         f"kept passes {pr.get('kept_passes')}; the session's float scale s = {pr['scale']['s_float']:.5f} from {pr['scale']['anchors_used']}.", ""]
    if "c_sessions" in o:
        L.append(f"Sessions that must carry a C log: {o['c_sessions']['listed']}, all checked to the end: {o['c_sessions']['ok']}; the stop-path "
                 f"test {o['c_sessions']['stoptest']}.")
        L.append("")
    L += ["| rule | verdict | reading | line | n |", "|---|---|---|---|---|"]
    for r in RULES:
        v = pr.get("rules", {}).get(r, {})
        rd = v.get("rms", v.get("mean", v.get("d_rms", v.get("inside"))))
        if r == "P8-LG":
            rd = f"F_slope {v.get('F_slope', float('nan')):.3f}, F_level {v.get('F_level', float('nan')):.3f}" if "F_slope" in v else ""
        line = v.get("line") or ([v.get("lo95"), v.get("hi95")] if "lo95" in v else (f">= {v['inside_at_least']}" if "inside_at_least" in v else ""))
        if isinstance(line, list):
            line = f"[{line[0]:+.4f}, {line[1]:+.4f}]"
        rd = f"{rd:+.4f}" if isinstance(rd, float) else rd
        L.append(f"| {r} | {o['verdicts'].get(r)} | {rd if rd is not None else ''} | {line} | {v.get('n', '')} |")
    if o.get("arms"):
        L += ["", "Arms (reported beside, never the verdict):", ""]
        for nm, a in o["arms"].items():
            L.append(f"- {nm}: " + (a.get("error") or ", ".join(f"{r} {v}" for r, v in a["verdicts"].items())))
    return "\n".join(L) + "\n"


def ka_pooled(paths):
    rows, s1 = [], []
    for q in paths:
        o = json.load(open(q))
        pr = o["primary"]
        s1.append(float(pr["scale"]["s_float"]) == 1.0)
        ka = pr.get("rules", {}).get("P8-KA", {}).get("tiles", {})
        for t, r in ka.items():
            rows.append(dict(r, tile=t, run=o["run"]))
    mins = P().frozen()["reg"]["scoring"]["minimum_tiles"]["KA_pooled"]
    if any(s1):
        return {"verdict": "NOT SCORED", "why": "a session took s = 1", "n": len(rows)}
    if len(rows) < mins:
        return {"verdict": "NOT SCORED", "why": f"{len(rows)} check anchors, fewer than {mins}", "n": len(rows)}
    return dict(ka_test(rows), rows=rows)


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--run", required=True, choices=sorted(RUN_CARD))
    s.add_argument("--reduction", required=True)
    s.add_argument("--raw", required=True)
    s.add_argument("--ccheck", required=True)
    s.add_argument("--arm", action="append", default=[])
    s.add_argument("--since", type=float)
    s.add_argument("--json")
    s.add_argument("--md")
    k = sub.add_parser("ka-pooled")
    k.add_argument("scored", nargs=2)
    k.add_argument("--json")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "ka-pooled":
            o = ka_pooled(a.scored)
            txt = json.dumps(o, indent=1, sort_keys=True, default=str)
            if a.json:
                open(a.json, "w").write(txt + "\n")
            print(json.dumps({k_: o[k_] for k_ in ("verdict", "n") if k_ in o}))
            return 0
        arms = [tuple(x.split("=", 1)) for x in a.arm]
        o = score_session(a.run, os.path.abspath(a.reduction), os.path.abspath(a.raw), os.path.abspath(a.ccheck), arms, a.since)
    except Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    if a.json:
        open(a.json, "w").write(json.dumps(o, indent=1, sort_keys=True, default=str) + "\n")
    if a.md:
        open(a.md, "w").write(markdown(o))
        print("results.md written")
    print(json.dumps(o["verdicts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
