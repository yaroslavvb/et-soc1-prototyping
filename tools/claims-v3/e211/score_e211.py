#!/usr/bin/env python3
"""E211 (Q204): the frozen scorer of THE SECOND KERNEL. It reads the kit's reduced data (E206's run form, below), E211's frozen forecasts
(forecast-e211.json), rules (rules-e211.json) and points (points-e211.json), and refuses to run (exit 4) if any of those files' bytes changed.
Standard library only.

    python3 -I -B tools/claims-v3/e211/score_e211.py DATA.json [--out SCORED.json]
    python3 -I -B tools/claims-v3/e211/score_e211.py --selftest-standins OUT.json   stand-in days whose verdicts are stated before the run (exit 0 = PASS)

THE DATA (one JSON, one arm): {"experiment": "E211", "arms": {"A": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"runs": [RUN, ...]}, "runs": [RUN, ...]}
  RUN = {"point": its point id, "block": "smoke" / "X" / "W" / "C", "pair": its pair id (or null), "n": its place in the session,
         "t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (launch >= 0, ok, wall_s >= 0.1 s, the kernel clock
         cycles_max / wall in 590-610 MHz; the calibration and check launches never count), "cycles_per_op": the median over the counted launches
         of the host's cycles_per_op (the counter's mean over minions / ops), "cycles_gemm": the median of cycles_max / passes (the slowest
         minion's counter, a GEMM), "p_work_w": the median board W of the 10 Hz samples inside the counted launches, "p_rest_w": the median board W
         of the last 5 s of the run's rest read, "die_start_c", "mhz_min", "mhz_max", "checks" (every check of C of the run: "exact" / "approx" /
         "wrong"), "record": {"arm", "type", "minions", "shire_mask"} as the host prints them, "walk": {"names": [the walk of every counted launch],
         "ok": [walk_ok of every counted launch], "launches_bad": the check line's walk_launches_bad} (rgm211's host; null for rgm136's host, which
         prints no walk), "gate": the identity gate's words for the process (ident_e211.py --gate <family> <elf>: "GATE OK: ..." or "GATE FAILED: ...")}
MEASURED: a run's wall cycles an op = cycles_gemm / ops a minion a GEMM; the counter's mean = cycles_per_op; W over idle = p_work - p_rest;
  J over idle = (p_work - p_rest) t_gemm; J with the card at rest = p_work t_gemm. A run whose record differs from its point (arm, type, minions,
  or the shire mask read as a number) is set aside and flagged. A POINT (its own case) is the mean of its kept runs, every block. A PAIR's ratio
  (rgm211 / rgm136) uses the pair's own W- or X-block runs: the mean of its gemmLn runs over the mean of its gemmL runs. FAMILY C's ratio uses the
  C block's runs: the mean of the gemmLnc runs over the mean of the twin's C-block runs.
THE RULES (E211.md section 7; the numbers from rules-e211.json): R0 (checks, walk tags, identity gates, the smoke's cycles), S6 (the clock), T4
  (the controls), MM1's absolute rules T1-T3 and E1-E4 at rgm211's 12 points, W1 (the ratio, THE QUESTION), W2 (the direction), H1-H3 (the ratio
  head to head: MM1 against F1, NC, N0), H4-H5 (the wall cycles at rgm211's points: MM1 against F1, NC), H6 (J over idle given the measured
  seconds: MM1 against MM1-S), SR (the stride reading), CT and CE (family C). REPORTED beside, never verdicts: the twins' absolute errors, every
  model's own ratio count, bootstrap intervals of d, family C's C0 and C2, the timing simulation's two columns.
AMENDMENT A1 (Tue 17 Nov 2026, Q204's lane fix-e211, before any E211 datum; verify-e211's findings 1, 2 and 7; rules-e211.json > "A1"):
  (1) THE CONTROL-CORRECTED READING: T4 is unchanged; when T4 reads FAIL and the two controls' ln ratios a (x01) and b (x02) lie on the same
  side of 0 with |a - b| <= consistency_ln and |c_hat| <= max_abs_c_ln (c_hat = (a + b) / 2), W1, W2 and H1-H3 are scored on each W pair's
  measured wall ratio over exp(c_hat) and labelled so, the raw-ratio verdicts REPORTED beside (T4's record carries "A1"); otherwise as
  registered, the control-corrected verdicts REPORTED beside. (2) R0's label: when R0 reads FAIL, every other rule carries "label_R0" (the
  registered "a FAIL labels every other verdict"). (3) The timing simulation's column is labelled: MM1's column is rgm136's gemmL step law at
  every point; beside it, the measured wall cycles an op over the kit's sys_emu steps an op for the point's own ELF and walk (2x2x1, mask 0x1;
  a small shape's count, not a law). No verdict of any other rule, no forecast, band or tolerance changes.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
D = "tools/claims-v3/e211/"
PINS = {
    D + "forecast-e211.json": "90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5",
    D + "rules-e211.json": "53c54fbe278fb9aa9e1a3875cdea0782339b25bd831a55f48f3fd912b26d37ca",
    D + "points-e211.json": "234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537",
}
# Amendment A1 (3): the kit's simulator check (Q204 kit-e211, sys_emu on aifoundry3, 00:25-00:34 PST Tue 17 Nov 2026, mask 0x1, fp32, 2x2x1;
# its record logs/simcheck-e211.txt lands with the kit): steps a minion an op for each arm family's own ELF and walk. Simulator steps, not time
# and not instruction counts (verify-e211: about 5 steps for each stack load); a small shape's count, not a law. REPORTED only.
SIM_STEPS_OP_KIT = {"gemmL": 47.742, "gemmLn": 32.762, "gemmLnc": 40.566}
SIM_COLUMN = "rgm136's gemmL step law (46.625 an op + 24.25 a C-tile row + 92 a launch), MM1-v1's column, at every point"
W_RULES = ("W1", "W2", "H1", "H2", "H3")
ABS_RULES = ("T1", "T2", "T3", "E1", "E2", "E3", "E4")
H_ORDER = ("H1", "H2", "H3", "H4", "H5", "H6", "H7")
ALL_RULES = ("R0", "S6", "T4") + ABS_RULES + ("W1", "W2") + H_ORDER + ("SR", "CT", "CE")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def load_frozen():
    for rel, want in PINS.items():
        got = sha_rel(rel)
        if got != want:
            print(f"score_e211: REFUSED, {rel} is {got}, pinned {want}")
            sys.exit(4)
    fc = json.load(open(os.path.join(REPO, D + "forecast-e211.json")))
    rules = json.load(open(os.path.join(REPO, D + "rules-e211.json")))
    pts = json.load(open(os.path.join(REPO, D + "points-e211.json")))
    return fc, rules, pts


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def lnr(a, b):
    return math.log(a / b) if (a is not None and b is not None and a > 0 and b > 0) else None


def rate_verdict(oks, share, min_n):
    n = len(oks)
    k = sum(1 for x in oks if x)
    if n == 0:
        return "NO DATA", k, n
    if n < min_n:
        return "TOO FEW", k, n
    return ("PASS" if k >= math.ceil(share * n - 1e-9) else "FAIL"), k, n


def sign_test(ds, tie, alpha, min_untied, first, second):
    a = sum(1 for d in ds if d > tie)
    b = sum(1 for d in ds if d < -tie)
    n = a + b
    if not ds:
        return {"verdict": "NO DATA", "first_closer": a, "second_closer": b, "ties": 0, "p": None}
    if n < min_untied:
        return {"verdict": "TOO FEW", "first_closer": a, "second_closer": b, "ties": len(ds) - n, "p": None}
    k = max(a, b)
    p = min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n)
    v = (f"{first} BETTER" if a > b else f"{second} BETTER") if p <= alpha else "NOT DECIDED"
    return {"verdict": v, "first_closer": a, "second_closer": b, "ties": len(ds) - n, "p": p}


def boot(ds, tag):
    if len(ds) < 3:
        return None
    rng = random.Random(f"E211|bootstrap|{tag}")
    ms, md = [], []
    for _ in range(10000):
        s = [ds[rng.randrange(len(ds))] for _ in ds]
        ms.append(sum(s) / len(s))
        md.append(statistics.median(s))
    ms.sort()
    md.sort()
    return {"mean_ci95": [ms[249], ms[9749]], "median_ci95": [md[249], md[9749]]}


# ------------------------------------------------------------------ the measured side
def run_values(run, ops):
    t = run.get("t_gemm_s")
    cg = run.get("cycles_gemm")
    pw, pr = run.get("p_work_w"), run.get("p_rest_w")
    W = (pw - pr) if (pw is not None and pr is not None) else None
    return {"wall": (cg / ops) if cg is not None else None, "mean": run.get("cycles_per_op"), "t": t, "W": W, "p_rest": pr,
            "J": (W * t) if (W is not None and t is not None) else None, "Jr": (pw * t) if (pw is not None and t is not None) else None,
            "die": run.get("die_start_c")}


def record_ok(run, p):
    rec = run.get("record") or {}
    try:
        mask_ok = int(str(rec.get("shire_mask")), 16) == int(p["shire_mask"], 16)
    except ValueError:
        mask_ok = False
    return rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == p["minions"] and mask_ok


def gather(arm, pts):
    P = {p["id"]: p for p in pts["points"] + pts["smoke"]}
    kept, aside = {}, []
    runs = (arm.get("runs") or [])
    for run in runs:
        p = P.get(run.get("point"))
        if p is None or not record_ok(run, p):
            aside.append({"n": run.get("n"), "point": run.get("point"), "why": "unknown point" if p is None else "record differs from its point"})
            continue
        v = run_values(run, p["ops_per_minion_per_gemm"])
        v.update({"block": run.get("block"), "pair": run.get("pair"), "n": run.get("n")})
        kept.setdefault(p["id"], []).append(v)
    point = {}
    for pid, vs in kept.items():
        point[pid] = {k: mean([v[k] for v in vs]) for k in ("wall", "mean", "t", "W", "J", "Jr", "p_rest", "die")}
        point[pid]["runs"] = len(vs)
    return P, kept, point, aside


def pair_ratio(kept, pair, block, num_id, den_id, key="wall"):
    a = mean([v[key] for v in kept.get(num_id, []) if v["block"] == block and v["pair"] == pair])
    b = mean([v[key] for v in kept.get(den_id, []) if v["block"] == block and v["pair"] == pair])
    return (a / b) if (a is not None and b is not None and b > 0) else None


# ------------------------------------------------------------------ family W's ratio rules on one set of ratios (raw, or A1's corrected)
def family_w(fc, rules, wpairs, rho, caveat):
    """W1, W2, H1, H2, H3 on the wall ratios rho {pair: ratio or None}, each carrying the caveat (the registered code, on given ratios)"""
    res = {}
    W1 = rules["W1"]
    oks, w1d = [], {}
    counts = {"F1": 0, "NC": 0, "N0": 0}
    for pair in wpairs:
        r = rho.get(pair)
        if r is None:
            continue
        fr = fc["pairs"][pair]["ratio_wall"]
        e = math.log(r / fr["MM1"])
        oks.append(abs(e) <= W1["tol_ln"])
        w1d[pair] = {"measured": r, "MM1": fr["MM1"], "ln_error": e}
        for mdl in counts:
            counts[mdl] += abs(math.log(r / fr[mdl])) <= W1["tol_ln"]
    v, k, n = rate_verdict(oks, W1["pass_share"], W1["min_n"])
    res["W1"] = {"verdict": v, "pass": k, "scored": n, "tol_ln": W1["tol_ln"], "pairs": w1d, "caveat": caveat,
                 "reported_other_models_inside_tol": counts}
    W2 = rules["W2"]
    dec = miss = 0
    w2d = {}
    for pair in wpairs:
        r = rho.get(pair)
        fm = fc["pairs"][pair]["ratio_wall"]["MM1"]
        if r is None or abs(math.log(fm)) < W2["apply_ln"]:
            continue
        if abs(math.log(r)) >= W2["decide_ln"]:
            dec += 1
            bad = (math.log(r) > 0) != (math.log(fm) > 0)
            miss += bad
            w2d[pair] = "miss" if bad else "holds"
        else:
            w2d[pair] = "not decided"
    v = "NO DATA" if not w2d else ("FAIL" if miss else ("PASS" if dec >= W2["min_decided"] else "NOT DECIDED"))
    res["W2"] = {"verdict": v, "decided": dec, "missed": miss, "pairs": w2d, "caveat": caveat}
    H = rules["H"]
    for rule, other in (("H1", "F1"), ("H2", "NC"), ("H3", "N0")):
        ds = []
        for pair in wpairs:
            r = rho.get(pair)
            if r is None:
                continue
            fr = fc["pairs"][pair]["ratio_wall"]
            ds.append(abs(math.log(r / fr[other])) - abs(math.log(r / fr["MM1"])))
        x = sign_test(ds, H["tie_ln_cycles"], H["alpha"], H["min_untied"], "MM1", other)
        x["bootstrap_REPORTED"] = boot(ds, rule)
        x["caveat"] = caveat
        res[rule] = x
    return res


# ------------------------------------------------------------------ the rules
def score(data, fc, rules, pts):
    arm = (data.get("arms") or {}).get("A") or {}
    out = {"experiment": "E211", "rules": {}, "reported": {}, "set_aside": []}
    if not arm or not (arm.get("runs") or (arm.get("smoke") or {}).get("runs")):
        for r in ALL_RULES:
            out["rules"][r] = {"verdict": "NO DATA"}
        out["rules"]["H7"] = {"verdict": "NOT REGISTERED"}
        return out
    P, kept, point, aside = gather(arm, pts)
    out["set_aside"] = aside
    FP = fc["points"]
    smoke_runs = (arm.get("smoke") or {}).get("runs") or []
    all_runs = smoke_runs + (arm.get("runs") or [])
    # ---- R0
    why = []
    for run in all_runs:
        if any(c not in ("exact", "approx") for c in (run.get("checks") or ["missing"])):
            why.append(f"run {run.get('n')} {run.get('point')}: a check of C not exact or approx: {run.get('checks')}")
        p = P.get(run.get("point"))
        if p is None:
            continue
        if not str(run.get("gate", "")).startswith("GATE OK"):
            why.append(f"run {run.get('n')} {run.get('point')}: identity gate not OK: {run.get('gate')}")
        if p["host"] == "rgm211":
            wk = run.get("walk") or {}
            want = "nm" if p["arm_family"] == "gemmLn" else "mn"
            if not wk.get("ok") or not all(wk.get("ok")) or any(x != want for x in (wk.get("names") or [None])) or wk.get("launches_bad") != 0:
                why.append(f"run {run.get('n')} {run.get('point')}: walk check failed (want {want} on every launch): {wk}")
    sm = rules["R0"]["smoke_band"]
    for s in pts["smoke"]:
        rs = [r for r in smoke_runs if r.get("point") == s["id"]]
        if not rs:
            why.append(f"smoke {s['id']}: no run")
            continue
        c = mean([r.get("cycles_per_op") for r in rs])
        f = FP[s["id"]]["MM1"]["cycles_per_op_mean"]
        if c is None or not (sm[0] * f <= c <= sm[1] * f):
            why.append(f"smoke {s['id']}: cycles an op {c} outside {sm[0]}-{sm[1]} x MM1's {f:.1f}")
    out["rules"]["R0"] = {"verdict": "FAIL" if why else "PASS", "why": why}
    # ---- S6
    lo, hi = rules["S6"]["mhz"]
    s6 = {}
    for run in arm.get("runs") or []:
        pid = run.get("point")
        if pid in point:
            ok = run.get("mhz_min") is not None and run.get("mhz_max") is not None and lo <= run["mhz_min"] and run["mhz_max"] <= hi
            s6[pid] = s6.get(pid, True) and ok
    out["rules"]["S6"] = {"verdict": "NO DATA" if not s6 else ("PASS" if all(s6.values()) else "FAIL"),
                          "points_outside": sorted(k for k, v in s6.items() if not v)}
    # ---- T4, the controls
    tol = rules["T4"]["tol_ln"]
    t4 = {}
    for x in ("x01", "x02"):
        rho = pair_ratio(kept, x, "X", x + "n", x + "m")
        t4[x] = {"ratio": rho, "holds": (abs(math.log(rho)) <= tol) if rho else None}
    vals = [v["holds"] for v in t4.values() if v["holds"] is not None]
    out["rules"]["T4"] = {"verdict": "NO DATA" if not vals else ("TOO FEW" if len(vals) < 2 else ("PASS" if all(vals) else "FAIL")), "pairs": t4}
    # ---- Amendment A1 (1): does the control-corrected reading apply?
    A1 = rules["A1"]
    la = math.log(t4["x01"]["ratio"]) if t4["x01"]["ratio"] else None
    lb = math.log(t4["x02"]["ratio"]) if t4["x02"]["ratio"] else None
    chat = (la + lb) / 2.0 if (la is not None and lb is not None) else None
    t4v = out["rules"]["T4"]["verdict"]
    a1_applies = False
    if t4v != "FAIL":
        a1_why = f"T4 reads {t4v}: A1 applies only when T4 reads FAIL"
    elif chat is None:
        a1_why = "a control has no measured ratio"
    elif not la * lb > 0:
        a1_why = "the two controls do not lie on the same side of 1"
    elif abs(la - lb) > A1["consistency_ln"]:
        a1_why = f"the two controls differ by {abs(la - lb):.5f} in ln, more than consistency_ln {A1['consistency_ln']}"
    elif abs(chat) > A1["max_abs_c_ln"]:
        a1_why = f"the controls' mean offset c_hat {chat:+.5f} in ln passes max_abs_c_ln {A1['max_abs_c_ln']}"
    else:
        a1_applies = True
        a1_why = (f"T4 FAIL with both controls on one side (x01 {la:+.5f}, x02 {lb:+.5f} in ln) and within {A1['consistency_ln']} of each other: "
                  f"W1, W2 and H1-H3 scored on the control-corrected ratios (each W pair's measured wall ratio over exp(c_hat), c_hat {chat:+.5f})")
    out["rules"]["T4"]["A1"] = {"applies": a1_applies, "why": a1_why, "x01_ln": la, "x02_ln": lb, "c_hat_ln": chat,
                                "consistency_ln": A1["consistency_ln"], "max_abs_c_ln": A1["max_abs_c_ln"]}
    if t4v == "PASS":
        caveat = ""
    elif a1_applies:
        caveat = f"{A1['label_applied']} (c_hat {chat:+.5f} in ln)"
    else:
        caveat = A1["label_not_a_model_test"]
    # ---- MM1's absolute rules at rgm211's points
    AB = rules["absolute"]
    nids = [p["id"] for p in pts["points"] if p["arm_family"] == "gemmLn"]
    per = {r: [] for r in ABS_RULES}
    detail = {}
    for pid in nids:
        if pid not in point:
            continue
        m, f = point[pid], FP[pid]["MM1"]
        ops = FP[pid]["ops_per_minion_per_gemm"]
        dd = {}
        for r, mv, fv in (("T1", m["wall"], f["cycles_per_op_wall"]), ("T2", m["mean"], f["cycles_per_op_mean"]), ("T3", m["t"], f["seconds_per_gemm"])):
            if mv is not None:
                e = mv / fv - 1.0
                per[r].append(abs(e) <= AB["bands"][r])
                dd[r] = e
        if m["t"] is not None and m["J"] is not None:
            t_us = m["t"] / ops * 1e6
            Wg = f["W_affine"]["A_W"] + f["W_affine"]["B_W_us"] / t_us
            watts = FP[pid]["scored_in_watts"]
            Jg, Jf = Wg * m["t"], f["J_over_idle_per_gemm"]
            if watts:
                e1 = (m["W"] - Wg)
                e2 = (m["W"] - f["W_over_idle"])
                per["E1"].append(abs(e1) <= AB["band_w"])
                per["E2"].append(abs(e2) <= AB["band_w"])
            else:
                e1, e2 = m["J"] / Jg - 1.0, m["J"] / Jf - 1.0
                per["E1"].append(abs(e1) <= AB["bands"]["E1"])
                per["E2"].append(abs(e2) <= AB["bands"]["E2"])
            e3 = m["Jr"] / (m["p_rest"] * m["t"] + Jg) - 1.0
            e4 = m["Jr"] / (m["p_rest"] * f["seconds_per_gemm"] + Jf) - 1.0
            per["E3"].append(abs(e3) <= AB["bands"]["E3"])
            per["E4"].append(abs(e4) <= AB["bands"]["E4"])
            dd.update({"E1": e1, "E2": e2, "E3": e3, "E4": e4})
        detail[pid] = dd
    for r in ABS_RULES:
        v, k, n = rate_verdict(per[r], AB["pass_share"], AB["min_n"])
        out["rules"][r] = {"verdict": v, "pass": k, "scored": n, "band": AB["bands"][r]}
    out["reported"]["absolute_errors_rgm211"] = detail
    # ---- the pairs
    wpairs = [p["pair"] for p in pts["points"] if p["family"] == "W" and p["arm_family"] == "gemmLn"]
    meas = {}
    for pair in wpairs:
        rho = pair_ratio(kept, pair, "W", pair + "n", pair + "m")
        meas[pair] = {"wall": rho, "mean": pair_ratio(kept, pair, "W", pair + "n", pair + "m", "mean"),
                      "t": pair_ratio(kept, pair, "W", pair + "n", pair + "m", "t"), "J": pair_ratio(kept, pair, "W", pair + "n", pair + "m", "J")}
    # ---- W1, W2, H1-H3: on the raw ratios as registered, or on A1's control-corrected ratios when A1 applies; the other reading REPORTED
    raw = {pair: meas[pair]["wall"] for pair in wpairs}
    cor = None
    if chat is not None:
        cor = {pair: (raw[pair] / math.exp(chat) if raw[pair] is not None else None) for pair in wpairs}
    prim = family_w(fc, rules, wpairs, cor if a1_applies else raw, caveat)
    alt, altkey = None, None
    if a1_applies:
        alt = family_w(fc, rules, wpairs, raw, "REPORTED, never a verdict: the raw ratios (A1 applies: the control-corrected ratios decide)")
        altkey = "raw_REPORTED"
    elif cor is not None:
        alt = family_w(fc, rules, wpairs, cor, f"REPORTED, never a verdict: the control-corrected ratios (c_hat {chat:+.5f}; A1 does not apply: {a1_why})")
        altkey = "control_corrected_REPORTED"
    for rule in W_RULES:
        prim[rule]["basis"] = "A1 control-corrected" if a1_applies else "raw"
        if alt is not None:
            prim[rule][altkey] = alt[rule]
        out["rules"][rule] = prim[rule]
    # ---- head to head on the absolute cycles and joules
    H = rules["H"]
    for rule, key in (("H4", "F1_cycles_per_op"), ("H5", "NC_cycles_per_op")):
        ds = []
        for pid in nids:
            if pid in point and point[pid]["wall"] is not None:
                w = point[pid]["wall"]
                ds.append(abs(math.log(w / FP[pid]["F"][key])) - abs(math.log(w / FP[pid]["MM1"]["cycles_per_op_wall"])))
        res = sign_test(ds, H["tie_ln_abs_cycles"], H["alpha"], H["min_untied"], "MM1", {"H4": "F1", "H5": "NC"}[rule])
        res["bootstrap_REPORTED"] = boot(ds, rule)
        out["rules"][rule] = res
    ds = []
    for pid in nids:
        if pid in point and point[pid]["J"] is not None and point[pid]["t"] is not None:
            m = point[pid]
            t_us = m["t"] / FP[pid]["ops_per_minion_per_gemm"] * 1e6
            f, s = FP[pid]["MM1"]["W_affine"], FP[pid]["MM1_S"]
            Jm = (f["A_W"] + f["B_W_us"] / t_us) * m["t"]
            Js = (s["A_W"] + s["B_W_us"] / t_us) * m["t"]
            if m["J"] > 0:
                ds.append(abs(math.log(m["J"] / Js)) - abs(math.log(m["J"] / Jm)))
    res = sign_test(ds, H["tie_ln_joules"], H["alpha"], H["min_untied"], "MM1", "MM1-S")
    res["bootstrap_REPORTED"] = boot(ds, "H6")
    out["rules"]["H6"] = res
    out["rules"]["H7"] = {"verdict": "NOT REGISTERED", "why": rules["H"]["rules"]["H7"]["what"]}
    # ---- SR, the stride reading
    a, b = meas.get("w04", {}).get("wall"), meas.get("w05", {}).get("wall")
    if a and b:
        s_m = math.log(a / b)
        reads = {}
        r05 = fc["pairs"]["w05"]["ratio_wall"]["MM1"]
        for name, val in fc["pairs"]["w04"]["stride_readings_ratio_wall"].items():
            reads[name] = math.log(val / r05)
        close = min(reads, key=lambda k: abs(reads[k] - s_m))
        out["rules"]["SR"] = {"verdict": "READ", "s_measured": s_m, "readings_s": reads, "closest": close}
    else:
        out["rules"]["SR"] = {"verdict": "NO DATA"}
    # ---- family C
    C = rules["C"]
    ct, ce, crep = [], [], {}
    for pair, x in fc["family_C"].items():
        if pair == "s03":
            continue
        cid, twin = x["point"], x["twin"]
        rw = pair_ratio(kept, pair, "C", cid, twin, "wall")
        rj = pair_ratio(kept, pair, "C", cid, twin, "J")
        rmn = pair_ratio(kept, pair, "C", cid, twin, "mean")
        if rw is not None:
            ct.append(abs(math.log(rw / x["ratio_C1_wall"])) <= C["CT"]["tol_ln"])
        if rj is not None and rj > 0:
            ce.append(abs(math.log(rj / x["ratio_C1_J_over_idle"])) <= C["CE"]["tol_ln"])
        crep[pair] = {"wall": rw, "mean": rmn, "J": rj, "C1_wall": x["ratio_C1_wall"], "C1_mean": x["ratio_C1_mean"], "C1_J": x["ratio_C1_J_over_idle"],
                      "C2_J_REPORTED": x["ratio_C2_J_over_idle_REPORTED"],
                      "closer_in_wall": (None if rw is None else ("C1" if abs(math.log(rw / x["ratio_C1_wall"])) < abs(math.log(rw)) else "C0")),
                      "closer_in_J": (None if not rj else ("C1" if abs(math.log(rj / x["ratio_C1_J_over_idle"])) < abs(math.log(rj)) else "C0"))}
    for rule, vals in (("CT", ct), ("CE", ce)):
        out["rules"][rule] = {"verdict": "NO DATA" if not vals else ("TOO FEW" if len(vals) < 2 else ("PASS" if all(vals) else "FAIL")),
                              "holds": sum(vals), "scored": len(vals)}
    out["reported"]["family_C"] = crep
    # ---- REPORTED: the twins, the timing simulation's columns, the rest law
    tw = {}
    for p in pts["points"]:
        pid = p["id"]
        if p["arm_family"] != "gemmL" or pid not in point:
            continue
        m, f = point[pid], FP[pid]["MM1"]
        tw[pid] = {"history": p["history"], "wall_err": (m["wall"] / f["cycles_per_op_wall"] - 1) if m["wall"] else None,
                   "J_err": (m["J"] / f["J_over_idle_per_gemm"] - 1) if m["J"] else None}
    out["reported"]["twins"] = tw
    sim = {}
    for pid, m in point.items():
        f = FP[pid]["MM1"]
        fam = P[pid]["arm_family"]
        if m["wall"] is not None:
            sim[pid] = {"measured_cycles_gemm_over_sim_steps": m["wall"] * FP[pid]["ops_per_minion_per_gemm"] / f["sim_steps_per_minion_per_gemm"],
                        "measured_mean_over_floor_tenb": (m["mean"] / f["floor_cycles_measured_tenb"]) if m["mean"] else None,
                        "sim_column": SIM_COLUMN, "sim_column_is_this_points_elf_and_walk": fam == "gemmL",
                        "kit_sim_steps_op_this_elf_and_walk": SIM_STEPS_OP_KIT[fam],
                        "measured_wall_op_over_kit_sim_steps_op": m["wall"] / SIM_STEPS_OP_KIT[fam]}
    out["reported"]["timing_simulation"] = sim
    out["reported"]["timing_simulation_note"] = ("Amendment A1 (3): measured_cycles_gemm_over_sim_steps reads MM1's column, " + SIM_COLUMN + "; at the "
                                                 "gemmLn and gemmLnc points that is not the count of the point's ELF and walk. "
                                                 "measured_wall_op_over_kit_sim_steps_op reads the kit's sys_emu steps an op for the point's own ELF and "
                                                 "walk (2x2x1, mask 0x1; a small shape's count, not a law). Simulator steps: not time, and not instruction counts.")
    out["reported"]["rest_law_error_W"] = {pid: (m["p_rest"] - FP[pid]["MM1"]["rest_law_P_W"]) for pid, m in point.items() if m["p_rest"] is not None}
    out["reported"]["pairs_measured"] = meas
    # ---- Amendment A1 (2): R0's label on every other verdict
    if out["rules"]["R0"]["verdict"] == "FAIL":
        for r, x in out["rules"].items():
            if r != "R0":
                x["label_R0"] = "R0 FAIL: a FAIL of R0 labels every other verdict (E211.md section 7; Amendment A1, clause 2)"
    return out


# ------------------------------------------------------------------ the stand-in days (self-test)
def synth_run(fc, pts, pid, block, pair, n, wall=None, mean_=None, t=None, W=None, p_rest=24.0, mhz=600.0, checks=None, walk=None, gate=None,
              record=None):
    p = {x["id"]: x for x in pts["points"] + pts["smoke"]}[pid]
    f = fc["points"][pid]["MM1"]
    wall = f["cycles_per_op_wall"] if wall is None else wall
    mean_ = f["cycles_per_op_mean"] if mean_ is None else mean_
    t = f["seconds_per_gemm"] if t is None else t
    W = f["W_over_idle"] if W is None else W
    run = {"point": pid, "block": block, "pair": pair, "n": n, "t_gemm_s": t, "cycles_per_op": mean_, "cycles_gemm": wall * p["ops_per_minion_per_gemm"],
           "p_work_w": p_rest + W, "p_rest_w": p_rest, "die_start_c": 50.0, "mhz_min": mhz, "mhz_max": mhz, "checks": checks or ["exact"],
           "record": record or {"arm": p["arm"], "type": p["format"], "minions": 1024, "shire_mask": "0xffffffff"},
           "walk": walk if walk is not None else ({"names": ["nm" if p["arm_family"] == "gemmLn" else "mn"] * 3, "ok": [True] * 3, "launches_bad": 0}
                                                    if p["host"] == "rgm211" else None),
           "gate": gate or f"GATE OK: {p['arm_family']}: {p['kernel']}"}
    return run


def day(fc, pts, how):
    """a stand-in day: how(pid, family_of_point) -> dict of overrides (wall, mean_, t, W, ...) for every run of that point"""
    runs = []
    smoke = []
    for o in pts["order"]:
        ov = how(o["point"]) or {}
        r = synth_run(fc, pts, o["point"], o["block"], o["pair"], o["n"], **ov)
        (smoke if o["block"] == "smoke" else runs).append(r)
    return {"experiment": "E211", "arms": {"A": {"smoke": {"runs": smoke}, "runs": runs}}}


def expected(fc, rules, pts, name):
    """the verdicts each stand-in day must give, stated by arithmetic on the frozen files apart from score()'s code path"""
    P = fc["pairs"]
    W = [k for k, v in P.items() if v["family"] == "W"]
    H = rules["H"]

    def st(models_first, models_second, measured_from, tie):
        a = b = 0
        for k in W:
            m = P[k]["ratio_wall"][measured_from] if isinstance(measured_from, str) else measured_from[k]
            d = abs(math.log(m / P[k]["ratio_wall"][models_second])) - abs(math.log(m / P[k]["ratio_wall"][models_first]))
            a += d > tie
            b += d < -tie
        n = a + b
        if n < H["min_untied"]:
            return "TOO FEW"
        p = 2 * sum(math.comb(n, i) for i in range(max(a, b), n + 1)) / 2 ** n
        return ((models_first if a > b else models_second) + " BETTER") if p <= H["alpha"] else "NOT DECIDED"
    e = {}
    # Amendment A1's stand-in days: the offset each gives the gemmLn runs' wall cycles of families X and W (ln), and what A1 must then read
    a1days = {"S_offset": ({"*": -0.02}, "APPLIES"), "T_split": ({"x01n": -0.015, "x02n": 0.015}, "NOT APPLIED"),
              "U_apart": ({"x01n": -0.015, "x02n": -0.008}, "NOT APPLIED"), "V_big": ({"*": -0.06}, "NOT APPLIED")}
    if name == "A_MM1":
        e = {"R0": "PASS", "S6": "PASS", "T4": "PASS", "T1": "PASS", "T2": "PASS", "T3": "PASS", "E1": "PASS", "E2": "PASS", "E3": "PASS", "E4": "PASS",
             "W1": "PASS", "W2": "PASS", "H1": st("MM1", "F1", "MM1", H["tie_ln_cycles"]), "H2": st("MM1", "NC", "MM1", H["tie_ln_cycles"]),
             "H3": st("MM1", "N0", "MM1", H["tie_ln_cycles"]), "H4": "MM1 BETTER", "H5": "MM1 BETTER", "CT": "PASS", "CE": "PASS", "SR": "READ",
             "A1": "NOT APPLIED", "W_basis": "raw", "R0_label": "NONE"}
    elif name in a1days:
        offs, want = a1days[name]
        x01 = offs.get("x01n", offs.get("*", 0.0))
        x02 = offs.get("x02n", offs.get("*", 0.0))
        t4 = "PASS" if (abs(x01) <= rules["T4"]["tol_ln"] and abs(x02) <= rules["T4"]["tol_ln"]) else "FAIL"
        a1 = (t4 == "FAIL" and x01 * x02 > 0 and abs(x01 - x02) <= rules["A1"]["consistency_ln"]
              and abs((x01 + x02) / 2) <= rules["A1"]["max_abs_c_ln"])
        assert ("APPLIES" if a1 else "NOT APPLIED") == want, name
        e = {"R0": "PASS", "T4": t4, "A1": want, "W_basis": "A1 control-corrected" if a1 else "raw", "T1": "PASS", "R0_label": "NONE"}
        common = offs.get("*", 0.0)          # the W pairs' raw ratios are MM1's x exp(common); A1's correction divides by exp(c_hat)
        shift = 0.0 if a1 else common
        meas = {k: P[k]["ratio_wall"]["MM1"] * math.exp(shift) for k in W}
        w1 = sum(1 for k in W if abs(math.log(meas[k] / P[k]["ratio_wall"]["MM1"])) <= rules["W1"]["tol_ln"])
        e["W1"] = "PASS" if w1 >= math.ceil(rules["W1"]["pass_share"] * len(W) - 1e-9) else "FAIL"
        if a1:
            e.update({"W2": "PASS", "H1": st("MM1", "F1", "MM1", H["tie_ln_cycles"]), "H2": st("MM1", "NC", "MM1", H["tie_ln_cycles"]),
                      "H3": st("MM1", "N0", "MM1", H["tie_ln_cycles"])})
    elif name == "B_F1":
        e = {"R0": "PASS", "T4": "PASS", "W1": "FAIL", "H1": st("MM1", "F1", "F1", H["tie_ln_cycles"]), "H4": "F1 BETTER", "T1": "FAIL"}
    elif name == "C_NC":
        e = {"R0": "PASS", "W1": "FAIL", "W2": "PASS", "H2": st("MM1", "NC", "NC", H["tie_ln_cycles"]), "H5": "NC BETTER"}
    elif name == "D_N0":
        e = {"R0": "PASS", "W1": "FAIL", "W2": "NOT DECIDED", "H3": st("MM1", "N0", "N0", H["tie_ln_cycles"])}
    elif name == "E_controls":
        e = {"T4": "FAIL", "R0": "PASS", "A1": "NOT APPLIED", "W_basis": "raw"}
    elif name == "F_check":
        e = {"R0": "FAIL", "R0_label": "LABELLED"}
    elif name == "G_wrong_elf":
        e = {"R0": "FAIL", "R0_label": "LABELLED"}
    elif name == "H_gate":
        e = {"R0": "FAIL", "R0_label": "LABELLED"}
    elif name == "I_clock":
        e = {"S6": "FAIL", "R0": "PASS"}
    elif name == "J_C0":
        e = {"CT": "FAIL", "CE": "FAIL", "W1": "PASS"}
    elif name == "K_none":
        e = {r: "NO DATA" for r in ALL_RULES if r != "H7"}
    elif name == "L_MM1S":
        e = {"H6": "MM1-S BETTER", "T1": "PASS", "W1": "PASS"}
    elif name == "M_opposite":
        e = {"W2": "FAIL", "W1": "FAIL"}
    elif name == "N_few":
        e = {"W1": "TOO FEW", "T1": "TOO FEW", "H1": "TOO FEW"}
    elif name == "O_stride136":
        e = {"SR_closest": "stride_on_rgm136_only", "W1": "PASS"}
    elif name == "P_energy":
        e = {"E1": "FAIL", "E2": "FAIL", "T1": "PASS", "H6": "MM1-S BETTER"}
    elif name == "Q_smoke":
        e = {"R0": "FAIL", "R0_label": "LABELLED"}
    elif name == "R_aside":
        e = {"R0": "PASS", "W1": "PASS", "T1": "PASS", "aside": 2}
    return e


def selftest(fc, rules, pts, outpath):
    FP = fc["points"]
    Pp = {p["id"]: p for p in pts["points"] + pts["smoke"]}

    def mm1(pid):
        return None

    def at_model(model):
        def how(pid):
            p = Pp[pid]
            f = FP[pid]
            if model == "F1":
                return {"wall": f["F"]["F1_cycles_per_op"], "mean_": f["F"]["F1_cycles_per_op"], "t": f["F"]["F1_seconds_per_gemm"]}
            if model == "NC":
                return {"wall": f["F"]["NC_cycles_per_op"], "mean_": f["F"]["NC_cycles_per_op"], "t": f["F"]["NC_seconds_per_gemm"]}
            if model == "N0" and p["arm_family"] == "gemmLn":
                twin = FP[p["pair"] + "m"]["MM1"] if p["pair"] else f["MM1"]
                return {"wall": twin["cycles_per_op_wall"], "mean_": twin["cycles_per_op_mean"], "t": twin["seconds_per_gemm"]}
            return None
        return how

    def mm1_c1(pid):
        p = Pp[pid]
        if p["arm_family"] == "gemmLnc":
            c1 = FP[pid]["C"]["C1"]
            return {"wall": c1["cycles_per_op_wall"], "mean_": c1["cycles_per_op_mean"], "t": c1["seconds_per_gemm"], "W": c1["W_over_idle"]}
        return None

    def combine(*fs):
        def how(pid):
            d = {}
            for f in fs:
                d.update(f(pid) or {})
            return d
        return how

    days = {}
    days["A_MM1"] = day(fc, pts, mm1_c1)
    days["B_F1"] = day(fc, pts, at_model("F1"))
    days["C_NC"] = day(fc, pts, at_model("NC"))
    days["D_N0"] = day(fc, pts, combine(at_model("N0"), mm1_c1))
    d = day(fc, pts, mm1_c1)
    for r in d["arms"]["A"]["runs"]:
        if r["point"] == "x01n":
            r["cycles_gemm"] *= 1.03
    days["E_controls"] = d
    d = day(fc, pts, mm1_c1)
    d["arms"]["A"]["runs"][5]["checks"] = ["exact", "wrong"]
    days["F_check"] = d
    d = day(fc, pts, mm1_c1)
    for r in d["arms"]["A"]["runs"]:
        if r["point"] == "w06n":          # a gemmLn process on rgm136's ELF: the host's walk check reads mn, walk_ok false
            r["walk"] = {"names": ["nm", "nm", "nm"], "ok": [False, False, False], "launches_bad": 3}
            break
    days["G_wrong_elf"] = d
    d = day(fc, pts, mm1_c1)
    for r in d["arms"]["A"]["runs"]:
        if r["point"] == "w08n":
            r["gate"] = "GATE FAILED: gemmLn needs rgm211's .text 82c7980716a0f0ca...; this ELF's .text is 61315bf6... (rgm136's)"
            break
    days["H_gate"] = d
    d = day(fc, pts, mm1_c1)
    for r in d["arms"]["A"]["runs"]:
        if r["point"] in ("w02m", "w02n"):
            r["mhz_max"] = 700.0
    days["I_clock"] = d
    days["J_C0"] = day(fc, pts, lambda pid: None)
    days["K_none"] = {"experiment": "E211", "arms": {}}

    def mm1s(pid):
        p = Pp[pid]
        if p["arm_family"] == "gemmLn" or p["arm_family"] == "gemmL":
            s = FP[pid]["MM1_S"]
            return {"W": s["W_over_idle"]}
        return mm1_c1(pid)
    days["L_MM1S"] = day(fc, pts, mm1s)

    def opposite(pid):
        p = Pp[pid]
        if p["arm_family"] == "gemmLn" and p["family"] == "W":
            pr = fc["pairs"][p["pair"]]["ratio_wall"]["MM1"]
            twin = FP[p["pair"] + "m"]["MM1"]
            return {"wall": twin["cycles_per_op_wall"] / pr, "mean_": twin["cycles_per_op_mean"] / pr, "t": twin["seconds_per_gemm"] / pr}
        return mm1_c1(pid)
    days["M_opposite"] = day(fc, pts, opposite)
    d = day(fc, pts, mm1_c1)
    keep = {"w01m", "w01n", "w02m", "w02n", "w03m", "w03n", "x01m", "x01n", "x02m", "x02n"}
    d["arms"]["A"]["runs"] = [r for r in d["arms"]["A"]["runs"] if r["point"] in keep]
    days["N_few"] = d

    def stride136(pid):
        if pid == "w04n":
            ratio = fc["pairs"]["w04"]["stride_readings_ratio_wall"]["stride_on_rgm136_only"]
            twin = FP["w04m"]["MM1"]
            return {"wall": twin["cycles_per_op_wall"] * ratio, "mean_": twin["cycles_per_op_mean"] * ratio, "t": twin["seconds_per_gemm"] * ratio}
        return mm1_c1(pid)
    days["O_stride136"] = day(fc, pts, stride136)

    def energy_up(pid):
        d2 = mm1_c1(pid) or {}
        if "W" not in d2:
            d2["W"] = FP[pid]["MM1"]["W_over_idle"] * 1.25
        return d2
    days["P_energy"] = day(fc, pts, energy_up)
    d = day(fc, pts, mm1_c1)
    d["arms"]["A"]["smoke"]["runs"][1]["cycles_per_op"] *= 3.0
    days["Q_smoke"] = d
    d = day(fc, pts, mm1_c1)
    done = set()
    for r in d["arms"]["A"]["runs"]:     # one run each of w09n (another shire mask) and w03m (another type): both set aside
        if r["point"] == "w09n" and "w09n" not in done:
            r["record"] = dict(r["record"], shire_mask="0xff")
            done.add("w09n")
        elif r["point"] == "w03m" and "w03m" not in done:
            r["record"] = dict(r["record"], type="int8")
            done.add("w03m")
    days["R_aside"] = d

    # Amendment A1's days: the gemmLn runs of families X and W given a code-path offset in their wall cycles (ln): every one ("*") or the
    # controls' own; S: one common offset (T4 FAIL, A1 applies); T: the controls on opposite sides; U: on one side but 0.007 apart; V: a common
    # offset past max_abs_c_ln (A1 does not apply)
    def offset(offs):
        def how(pid):
            p = Pp[pid]
            d2 = dict(mm1_c1(pid) or {})
            f = offs.get(pid)
            if f is None and p["arm_family"] == "gemmLn" and p["family"] in ("W", "X"):
                f = offs.get("*")
            if f is not None:
                d2["wall"] = FP[pid]["MM1"]["cycles_per_op_wall"] * math.exp(f)
            return d2
        return how
    days["S_offset"] = day(fc, pts, offset({"*": -0.02}))
    days["T_split"] = day(fc, pts, offset({"x01n": -0.015, "x02n": 0.015}))
    days["U_apart"] = day(fc, pts, offset({"x01n": -0.015, "x02n": -0.008}))
    days["V_big"] = day(fc, pts, offset({"*": -0.06}))
    results, ok_all = {}, True
    for name, dd in days.items():
        got = score(dd, fc, rules, pts)
        exp = expected(fc, rules, pts, name)
        gv = {r: got["rules"][r]["verdict"] for r in got["rules"]}
        if "SR" in got["rules"] and got["rules"]["SR"].get("closest"):
            gv["SR_closest"] = got["rules"]["SR"]["closest"]
        gv["aside"] = len(got["set_aside"])
        a1r = got["rules"].get("T4", {}).get("A1")
        gv["A1"] = ("APPLIES" if a1r["applies"] else "NOT APPLIED") if a1r else "NO DATA"
        gv["W_basis"] = got["rules"].get("W1", {}).get("basis", "NO DATA")
        others = [r for r in got["rules"] if r != "R0"]
        nlab = sum(1 for r in others if "label_R0" in got["rules"][r])
        gv["R0_label"] = "NONE" if nlab == 0 else ("LABELLED" if nlab == len(others) else "PARTIAL")
        bad = {k: (v, gv.get(k)) for k, v in exp.items() if gv.get(k) != v}
        ok_all &= not bad
        results[name] = {"expected": exp, "got": gv, "met": not bad, "unmet": bad}
    seen = {}
    for name, rr in results.items():
        for k, v in rr["got"].items():
            seen.setdefault(k, set()).add(str(v))
    cover = {k: sorted(v) for k, v in seen.items()}
    need = {"R0": {"PASS", "FAIL"}, "S6": {"PASS", "FAIL"}, "T4": {"PASS", "FAIL"}, "T1": {"PASS", "FAIL"}, "E1": {"PASS", "FAIL"},
            "E2": {"PASS", "FAIL"}, "W1": {"PASS", "FAIL"}, "W2": {"PASS", "FAIL"}, "H1": {"MM1 BETTER", "F1 BETTER"},
            "H2": {"MM1 BETTER", "NC BETTER"}, "H3": {"MM1 BETTER", "N0 BETTER"}, "H4": {"MM1 BETTER", "F1 BETTER"},
            "H5": {"MM1 BETTER", "NC BETTER"}, "H6": {"MM1 BETTER", "MM1-S BETTER"}, "CT": {"PASS", "FAIL"}, "CE": {"PASS", "FAIL"},
            "A1": {"APPLIES", "NOT APPLIED"}, "W_basis": {"raw", "A1 control-corrected"}, "R0_label": {"NONE", "LABELLED"}}
    missing = {k: sorted(v - seen.get(k, set())) for k, v in need.items() if not v <= seen.get(k, set())}
    ok_all &= not missing
    res = {"what": "E211's scorer on stand-in days whose verdicts expected() states apart from score(); every listed rule seen passing and failing; "
                   "Amendment A1's reading seen applying and not, and R0's label seen attached and not",
           "verdict": "PASS" if ok_all else "FAIL", "days": results, "coverage": cover, "coverage_missing": missing,
           "interpreter": "/usr/bin/python3 %s" % sys.version.split()[0]}
    open(outpath, "w").write(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    for name, rr in results.items():
        print(f"{name}: {'met' if rr['met'] else 'UNMET ' + str(rr['unmet'])}: " + ", ".join(f"{k} {v}" for k, v in sorted(rr["got"].items())))
    print("coverage missing:", missing or "none")
    print("SELFTEST", res["verdict"])
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins")
    a = ap.parse_args()
    fc, rules, pts = load_frozen()
    if a.selftest_standins:
        return selftest(fc, rules, pts, a.selftest_standins)
    if not a.data:
        print(__doc__)
        return 2
    res = score(json.load(open(a.data)), fc, rules, pts)
    res["inputs_sha256"] = dict(PINS)
    s = json.dumps(res, indent=1, sort_keys=True, default=str) + "\n"
    if a.out:
        open(a.out, "w").write(s)
    for r in ALL_RULES:
        v = res["rules"].get(r, {})
        print(f"{r}: {v.get('verdict')}" + (f" ({v.get('pass')}/{v.get('scored')})" if "pass" in v else "")
              + (f" ({v.get('first_closer')}/{v.get('second_closer')}/{v.get('ties')}, p {v.get('p')})" if "first_closer" in v else ""))
    a1 = res["rules"].get("T4", {}).get("A1")
    if a1:
        print(f"A1: {'APPLIES' if a1['applies'] else 'NOT APPLIED'}: {a1['why']}; W1, W2 and H1-H3 read on the "
              f"{res['rules'].get('W1', {}).get('basis', '-')} ratios")
    if res["rules"].get("R0", {}).get("verdict") == "FAIL":
        print("R0 label: R0 FAIL labels every other verdict (each rule's label_R0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
