#!/usr/bin/env python3
"""E220 (Q233): THE SCORER of MM1-v3.2's card-transfer blind day, frozen with the registration. Reads each arm's measured side, the frozen points,
forecasts and rules (refusing if a file it reads changed), and writes every registered verdict per arm and pooled, with the REPORTED readings.
Standard library only.

    python3 -I -B tools/claims-v3/e220/score_e220.py --a <arm A data JSON> [--a-tag A] --b <arm B data JSON> [--b <more>] [--labels <json>] --out <dir>
    python3 -I -B tools/claims-v3/e220/score_e220.py --selftest-standins      writes selftest-standins.json (every rule both ways; exit 0 = PASS)
    python3 -I -B tools/claims-v3/e220/score_e220.py --selftest-real          writes selftest-real.json (the readers on real committed bytes)

THE MEASURED SIDE. Arm A (aifoundry1 card 1): E215 arm B's reducer form (the kit's reducer writes it: {"arms": {<tag>: {"points": {<id>: {"runs":
[...]}}, "ties": {...}, "smoke": {...}}}}), read as E218's scorer reads E215's form: a run is kept when its record equals its point (arm, type,
minions, the shire mask read as a number), it has t_gemm_s and cycles_gemm, and - a run of rgm211's host (the gemmLnc branch) - its walk and identity
gate are good; per point the mean of its kept runs: wall cycles an op = cycles_gemm / ops a minion, the counter's mean = cycles_per_op, seconds =
t_gemm_s, W over idle = p_work_w - p_rest_w, J over idle = W x t, J at rest = p_work_w x t, the rest p_rest_w; t_op = wall / 600 MHz. Arm B (aifoundry2
card 0): E208's registered reducer's form (E216's measured side, the kit's reducer writes it: {"runs": [...], "smoke": [...], "anchors": [...]}), read as
E216's scorer reads it: per run in its primary view, ROUTE c (registered) when the view clock reads 790-810 MHz with no step and not NO STEP, scored
against the frozen 799.0 MHz column; ROUTE m (REPORTED) otherwise, against the column nearest its clock; a capped or thin run carries no energy.
A point or case with no kept run is NO DATA, never a failure. A point labelled 'ran before' (the card lane's step 6n) leaves every rule (said).
R0 (every check of C exact or approx; the smoke good) and, arm A, S6 (every kept run at 590-610 MHz): a FAIL labels every other verdict of its arm.
THE RULES (rules-e220.json): per arm T1-T3, E1-E4 (MM1-v3.2 within its band at 90% of its cases or points; TOO FEW under 10); H1-H10 per arm and
HP1-HP10 pooled (MM1-v3.2 against MM1-v3 and MM1-v3.1, the exact two-sided sign test with the ties); CX-T, CX-E per arm and CXP-T, CXP-E pooled (the
cross-card rule: MM1-v3.2's error on this card against its frozen error on aifoundry3 card 0, per X twin). REPORTED: per family and model errors,
the L3, Y2 and G2 readings, route m, the twins' card offset.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
MODELS = ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2")
COL = {"A": "600.0", "B": "799.0"}
CLOCKS_B = {799.0: "799.0", 700.0: "700.0", 600.0: "600.0"}
H2H = (("H1", "MM1-v3.2", "MM1-v3", "wall"), ("H2", "MM1-v3.2", "MM1-v3", "mean"), ("H3", "MM1-v3.2", "MM1-v3", "seconds"),
       ("H4", "MM1-v3.2", "MM1-v3", "Wg"), ("H5", "MM1-v3.2", "MM1-v3", "Jf"),
       ("H6", "MM1-v3.2", "MM1-v3.1", "wall"), ("H7", "MM1-v3.2", "MM1-v3.1", "mean"), ("H8", "MM1-v3.2", "MM1-v3.1", "seconds"),
       ("H9", "MM1-v3.2", "MM1-v3.1", "Wg"), ("H10", "MM1-v3.2", "MM1-v3.1", "Jf"))
RULES_T = ("T1", "T2", "T3", "E1", "E2", "E3", "E4")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def load_frozen(check=True):
    """the frozen files, refused if any differs from the sha256 the registration's SHA256SUMS records"""
    sums = {}
    sp = os.path.join(HERE, "SHA256SUMS-e220-registration")
    if os.path.exists(sp):
        for ln in open(sp):
            if ln.strip() and not ln.startswith("#"):
                h, f = ln.split(None, 1)
                f = f.strip()
                if f.startswith("tools/claims-v3/e220/"):          # the sums list paths from the lab's top (E218's form)
                    f = f[len("tools/claims-v3/e220/"):]
                sums[f] = h
    for f in ("points-e220.json", "forecast-e220.json", "rules-e220.json"):
        if check and f in sums and sha(os.path.join(HERE, f)) != sums[f]:
            print(f"score_e220: REFUSED, {f} differs from SHA256SUMS-e220-registration")
            sys.exit(4)
    P = json.load(open(os.path.join(HERE, "points-e220.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e220.json")))
    R = json.load(open(os.path.join(HERE, "rules-e220.json")))
    return P, F, R


# ------------------------------------------------------------------ the measured side, arm A (E215's form, E218's reader)
def read_a(data, P, tag, labels):
    pts = {p["id"]: p for p in P["points"]["A"]}
    arm = (data.get("arms") or {}).get(tag) or {}
    out, flags, r0, s6 = {}, [], [], []
    for pid, pt in (arm.get("points") or {}).items():
        p = pts.get(pid)
        if p is None:
            flags.append(f"{pid}: not a registered point (ignored)")
            continue
        kept = []
        for r in pt.get("runs", []):
            chk = r.get("checks") or []
            if not chk or any(c not in ("exact", "approx") for c in chk):
                r0.append(f"{pid} run {r.get('n')}: checks {chk}")
            rec = r.get("record") or {}
            try:
                same = (rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == int(p["minions"])
                        and int(str(rec.get("shire_mask")), 16) == int(p["shire_mask"], 16))
            except (TypeError, ValueError):
                same = False
            good = True
            if p["host"] == "rgm211":
                w = r.get("walk") or {}
                good = bool(w.get("ok")) and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")
                if not good:
                    r0.append(f"{pid} run {r.get('n')}: walk or gate not good")
            if not same:
                flags.append(f"{pid} run {r.get('n')}: SET ASIDE (record {rec})")
                continue
            if not good:
                flags.append(f"{pid} run {r.get('n')}: SET ASIDE (walk or gate)")
                continue
            if r.get("t_gemm_s") is None or r.get("cycles_gemm") is None:
                flags.append(f"{pid} run {r.get('n')}: no reading (NO DATA)")
                continue
            if r.get("mhz_min") is None or r.get("mhz_max") is None or r["mhz_min"] < 590 or r["mhz_max"] > 610:
                s6.append(f"{pid} run {r.get('n')}: clock {r.get('mhz_min')}-{r.get('mhz_max')} MHz")
            kept.append(r)
        if not kept:
            flags.append(f"{pid}: NO DATA (no kept run)")
            continue
        ops = p["ops_per_minion_per_gemm"]
        en = [r for r in kept if r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        wall = mean([r["cycles_gemm"] / ops for r in kept])
        out[pid] = {"n_runs": len(kept), "wall": wall, "mean": mean([r.get("cycles_per_op") for r in kept]), "t": mean([r["t_gemm_s"] for r in kept]),
                    "Top": wall / 600.0, "W": mean([r["p_work_w"] - r["p_rest_w"] for r in en]) if en else None,
                    "J": mean([(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in en]) if en else None,
                    "Jrest": mean([r["p_work_w"] * r["t_gemm_s"] for r in en]) if en else None,
                    "prest": mean([r["p_rest_w"] for r in en]) if en else None, "t_e": mean([r["t_gemm_s"] for r in en]) if en else None,
                    "Top_e": (mean([r["cycles_gemm"] / ops for r in en]) / 600.0) if en else None, "route": "A", "col": COL["A"]}
    g_fail = []
    for r in (arm.get("ties") or {}).get("runs", []) + (arm.get("smoke") or {}).get("runs", []):
        why = []
        chk = r.get("checks") or []
        if not chk or any(c not in ("exact", "approx") for c in chk):
            why.append(f"{r.get('block')} run {r.get('n')}: checks {chk}")
        if r.get("block") == "smoke":
            cpo = r.get("cycles_per_op")
            if cpo is None or not (200 <= cpo <= 4000):
                why.append(f"smoke run {r.get('n')}: cycles an op {cpo} outside 200-4,000")
            if r.get("walk") is not None or r.get("gate") is not None:
                w = r.get("walk") or {}
                if not (w.get("ok") and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")):
                    why.append(f"smoke run {r.get('n')}: walk or gate not good")
        if r.get("block") == "smoke" and r.get("point") == "s03":
            g_fail.extend(f"s03 ({x})" for x in why)
        else:
            r0.extend(why)
    if g_fail:
        ran = sorted(pid for pid in out if pts[pid]["loop"] == "rgm136 gemmLnc")
        if ran:
            r0.extend(g_fail + [f"the G block's smoke s03 failed, yet {ran} ran: counted in R0"])
        else:
            flags.append(f"the G block's smoke s03 failed ({'; '.join(g_fail)}): the G block NO DATA; not an R0 failure, REPORTED")
    for pid in labels.get("ran_before_points", {}).get("A", []):
        if pid in out:
            out[pid]["ran_before"] = True
    has_any = bool(out) or bool((arm.get("ties") or {}).get("runs")) or bool((arm.get("smoke") or {}).get("runs"))
    return out, {}, flags, r0, s6, has_any


# ------------------------------------------------------------------ the measured side, arm B (E208's reducer form, E216's reader)
def mask_int(x):
    try:
        return int(str(x), 16)
    except (TypeError, ValueError):
        return None


def read_b_run(r, pts):
    pid = r.get("arm")
    if r.get("role") != "arm" or pid not in pts or r.get("form") == "null":
        return None
    p = pts[pid]
    rec = {"id": pid, "i": r.get("i"), "checks": list(r.get("checks") or []), "capped": bool(r.get("capped")), "flags": [], "set_aside": None,
           "no_step": bool(r.get("no_step")) or r.get("primary_view") == "band600"}
    why = []
    if mask_int(r.get("shires")) != int(p["shire_mask"], 16):
        why.append(f"mask {r.get('shires')}")
    if r.get("type") != p["format"]:
        why.append(f"type {r.get('type')}")
    if r.get("minions") is not None and int(r.get("minions")) != int(p["minions"]):
        why.append(f"minions {r.get('minions')}")
    if not r.get("ran", True) or not r.get("views"):
        rec["set_aside"] = "did not run"
        return rec
    if why:
        rec["set_aside"] = "; ".join(why)
        return rec
    v = (r.get("views") or {}).get(r.get("primary_view")) or {}
    if not (v.get("T_op_us") and v.get("cyc_op_max") and (v.get("n_launch") or 0) >= 1 and v.get("kclock_mhz")):
        rec["set_aside"] = "no time in its view"
        return rec
    rec.update({"f": float(v["kclock_mhz"]), "wall": float(v["cyc_op_max"]), "mean": (None if v.get("cyc_op_mean") in (None, "") else float(v["cyc_op_mean"])),
                "t": float(v["t_pass_s"]), "Top": float(v["T_op_us"])})
    if v.get("dP_w") is not None and v.get("p_mean_w") and not r.get("capped") and not v.get("thin"):
        rec.update({"W": float(v["dP_w"]), "prest": float(v["p_mean_w"]) - float(v["dP_w"]), "J": float(v["J_pass_over"]), "Jrest": float(v["J_pass_with"])})
    fr = r.get("frac_800_after_step")
    step = (fr is not None and fr < 1.0 and not rec["no_step"]) or \
        (v.get("mhz_min") is not None and v.get("mhz_mean") is not None and float(v["mhz_min"]) < float(v["mhz_mean"]) - 0.5)
    rec["step"] = bool(step)
    route_c = (790.0 <= rec["f"] <= 810.0) and not step and not rec["no_step"]
    rec["route"] = "c" if route_c else "m"
    rec["col"] = "799.0" if route_c else CLOCKS_B[min(CLOCKS_B, key=lambda c: abs(c - rec["f"]))]
    if step:
        rec["flags"].append("STEP")
    if rec["no_step"]:
        rec["flags"].append("NO STEP")
    if rec["capped"]:
        rec["flags"].append("CAPPED: no energy")
    if not route_c:
        rec["flags"].append(f"ROUTE m at {rec['col']} MHz")
    return rec


def read_b(datas, P, labels):
    pts = {p["id"]: p for p in P["points"]["B"]}
    runs, anchors, smoke, flags, r0 = [], [], [], [], []
    for D in datas:
        smoke += list(D.get("smoke") or [])
        for r in D.get("runs") or []:
            if r.get("role") == "anchor" or r.get("role") == "tie":
                anchors.append(r)
                continue
            x = read_b_run(r, pts)
            if x is None:
                continue
            runs.append(x)
    for r in runs:
        if r["set_aside"] != "did not run":
            for c in (r["checks"] or [None]):
                if c not in ("exact", "approx"):
                    r0.append(f"{r['id']} run {r['i']}: check {c}")
        if r["flags"] or r["set_aside"]:
            flags.append(f"{r['id']} run {r['i']}: {r['flags']} {r['set_aside'] or ''}".strip())
    for a in anchors:
        if a.get("ran", True):
            for c in (a.get("checks") or [None]):
                if c not in ("exact", "approx"):
                    r0.append(f"tie/anchor {a.get('arm')} run {a.get('i')}: check {c}")
    if smoke and not all(s.get("good") and s.get("rc") == 0 and s.get("check") in ("exact", "approx") for s in smoke):
        r0.append("a smoke process not good (rc, check)")
    by = {}
    for r in runs:
        if r["set_aside"] is None:
            by.setdefault((r["id"], r["route"], r["col"]), []).append(r)
    out, outm = {}, {}
    for (pid, route, col), rs in by.items():
        e = [r for r in rs if "W" in r]
        fig = {"n_runs": len(rs), "wall": mean([r["wall"] for r in rs]), "mean": mean([r["mean"] for r in rs]), "t": mean([r["t"] for r in rs]),
               "Top": mean([r["Top"] for r in rs]), "W": mean([r["W"] for r in e]), "J": mean([r["J"] for r in e]), "Jrest": mean([r["Jrest"] for r in e]),
               "prest": mean([r["prest"] for r in e]), "t_e": mean([r["t"] for r in e]), "Top_e": mean([r["Top"] for r in e]), "route": route, "col": col}
        if route == "c":
            out[pid] = fig
        else:
            outm.setdefault(pid, {})[col] = fig
    for pid in labels.get("ran_before_points", {}).get("B", []):
        if pid in out:
            out[pid]["ran_before"] = True
    has_any = bool(runs) or bool(anchors) or bool(smoke)
    return out, outm, flags, r0, [], has_any


# ------------------------------------------------------------------ the model side
def fcv(F, arm, pid, col, model):
    return ((F["arms"][arm]["points"].get(pid) or {}).get("clocks", {}).get(col) or {}).get(model) or {}


def predicted(F, arm, pid, col, model, m):
    x = fcv(F, arm, pid, col, model)
    o = {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"), "W": x.get("W_over_idle")}
    if x.get("A_W") is not None and m.get("Top_e"):
        Wg = x["A_W"] + x["B_W_us"] / m["Top_e"]
        o.update({"Wg": Wg, "Jg": Wg * m["t_e"], "Wf": x["W_over_idle"], "Jf": x["J_over_idle_per_gemm"]})
        if m.get("prest") is not None:
            o["JRg"] = m["prest"] * m["t_e"] + Wg * m["t_e"]
            o["JRf"] = m["prest"] * x["seconds_per_gemm"] + x["J_over_idle_per_gemm"]
    return o


def watts_point(F, arm, pid, col, m):
    w32 = fcv(F, arm, pid, col, "MM1-v3.2").get("W_over_idle")
    return (w32 is not None and w32 < 3.0) or (m.get("W") is not None and m["W"] < 3.0)


def cells_of(M, F, R, arm, model="MM1-v3.2"):
    a = R["arms"][arm]
    B = {q: a["bands"][q]["band"] for q in RULES_T}
    BW = a["band_w"]["band_W"]
    cells = {q: {} for q in RULES_T}
    for pid, m in M.items():
        if m.get("ran_before"):
            continue
        fc = predicted(F, arm, pid, m["col"], model, m)
        for q, mk, fk in (("T1", "wall", "wall"), ("T2", "mean", "mean"), ("T3", "t", "seconds")):
            if m.get(mk) and fc.get(fk):
                e = m[mk] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
        if m.get("W") is None or fc.get("Wg") is None:
            continue
        if watts_point(F, arm, pid, m["col"], m):
            for q, fk in (("E1", "Wg"), ("E2", "Wf")):
                d = m["W"] - fc[fk]
                cells[q][pid] = {"err_W": d, "pass": abs(d) <= BW + 1e-12, "watts": True}
        else:
            for q, fk in (("E1", "Jg"), ("E2", "Jf")):
                e = m["J"] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
        for q, fk in (("E3", "JRg"), ("E4", "JRf")):
            if fc.get(fk) and m.get("Jrest"):
                e = m["Jrest"] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
    return cells


def verdict(cells, share=0.9, too_few=10):
    c = list(cells.values())
    if not c:
        return {"verdict": "NO DATA", "n": 0}
    k = sum(1 for x in c if x["pass"])
    if len(c) < too_few:
        return {"verdict": "TOO FEW", "n": len(c), "pass": k}
    return {"verdict": "PASS" if k >= math.ceil(share * len(c) - 1e-9) else "FAIL", "n": len(c), "pass": k, "needed": math.ceil(share * len(c) - 1e-9)}


def h_cases(M, F, R, arm, first, second, q):
    ties = R["arms"][arm]["ties"]
    out = []
    for pid, m in M.items():
        if m.get("ran_before"):
            continue
        a, b = predicted(F, arm, pid, m["col"], first, m), predicted(F, arm, pid, m["col"], second, m)
        if q in ("wall", "mean", "seconds"):
            mk = {"wall": "wall", "mean": "mean", "seconds": "t"}[q]
            if m.get(mk) and a.get(q) and b.get(q):
                out.append((math.fabs(math.log(m[mk] / b[q])) - math.fabs(math.log(m[mk] / a[q])), ties["seconds_ln" if q == "seconds" else "cycles_ln"],
                            f"{arm}:{pid}"))
            continue
        if m.get("W") is None or a.get("Wg") is None or b.get("Wg") is None:
            continue
        fk = "Wg" if q == "Wg" else "Wf"
        if watts_point(F, arm, pid, m["col"], m):
            out.append((abs(m["W"] - b[fk]) - abs(m["W"] - a[fk]), ties["watts_W"], f"{arm}:{pid}"))
        else:
            if q == "Wg":
                out.append((abs(math.log(m["W"] / b["Wg"])) - abs(math.log(m["W"] / a["Wg"])), ties["joules_ln"], f"{arm}:{pid}"))
            else:
                out.append((abs(math.log(m["J"] / b["Jf"])) - abs(math.log(m["J"] / a["Jf"])), ties["joules_ln"], f"{arm}:{pid}"))
    return out


def decide(cases, first, second, minimum=10, names=None):
    if not cases:
        return {"verdict": "NO DATA", "n": 0}
    npos = sum(1 for d, t, _ in cases if d > t)
    nneg = sum(1 for d, t, _ in cases if d < -t)
    res = {"n": len(cases), "first_closer": npos, "second_closer": nneg, "ties": len(cases) - npos - nneg}
    if npos + nneg < minimum:
        res["verdict"] = "TOO FEW"
        return res
    p = sign_p(npos, nneg)
    res["p"] = p
    nm = names or (first + " BETTER", second + " BETTER")
    res["verdict"] = (nm[0] if npos > nneg else nm[1]) if p < 0.05 else "NOT DECIDED"
    return res


def cx_cases(M, F, R, arm, q):
    base = R["arms"][arm]["cross_card"]["baseline_aifoundry3_E218"]
    ties = R["arms"][arm]["ties"]
    out, offs = [], []
    for pid, b in base.items():
        m = M.get(pid)
        if not m or m.get("ran_before") or not isinstance(b, dict) or "a3_ln_err_wall" not in b:
            continue
        fc = predicted(F, arm, pid, m["col"], "MM1-v3.2", m)
        if q == "wall":
            if m.get("wall") and fc.get("wall"):
                out.append((abs(math.log(m["wall"] / fc["wall"])) - abs(b["a3_ln_err_wall"]), ties["cycles_ln"], f"{arm}:{pid}"))
                offs.append(math.log(m["wall"] / b["a3_measured"]["cw"]))
        else:
            if (b.get("a3_energy_scored_relative") and b.get("a3_ln_err_Wg") is not None and m.get("W") and fc.get("Wg")
                    and m["W"] >= 3.0 and fc["Wg"] >= 3.0):
                out.append((abs(math.log(m["W"] / fc["Wg"])) - abs(b["a3_ln_err_Wg"]), ties["joules_ln"], f"{arm}:{pid}"))
    return out, offs


# ------------------------------------------------------------------ the REPORTED readings
def family_stats(M, F, P, arm):
    fam = {p["id"]: (p["family"], p.get("subfamily", "")) for p in P["points"][arm]}
    out = {}
    for model in MODELS:
        acc = {}
        for pid, m in M.items():
            f, sf = fam.get(pid, ("?", "?"))
            fc = predicted(F, arm, pid, m["col"], model, m)
            for key in (f, f + "/" + sf, "all"):
                d = acc.setdefault(key, {"wall": [], "Wg": []})
                if m.get("wall") and fc.get("wall"):
                    d["wall"].append(math.log(m["wall"] / fc["wall"]))
                if m.get("W") and fc.get("Wg") and m["W"] >= 3 and fc["Wg"] >= 3:
                    d["Wg"].append(math.log(m["W"] / fc["Wg"]))
        out[model] = {k: {q: {"n": len(v), "rms_pct": (100 * rms(v) if v else None), "bias_pct": (100 * mean(v) if v else None)} for q, v in d.items()}
                      for k, d in sorted(acc.items())}
    return out


def readings(M, F, P, R, arm):
    pts = {p["id"]: p for p in P["points"][arm]}
    rd = {}
    # L3: MM1-v3.2's wall error by edge and side
    l3 = []
    for pid, p in pts.items():
        if p["family"] == "L3" and pid in M:
            fc = predicted(F, arm, pid, M[pid]["col"], "MM1-v3.2", M[pid])
            l3.append({"id": pid, "token": p["token"], "subfamily": p["subfamily"], "footprint_MB": p.get("footprint_MB"), "side": p.get("edge_side"),
                       "ln_err_wall_v32": math.log(M[pid]["wall"] / fc["wall"]) if fc.get("wall") else None})
    rd["L3"] = {"points": l3, "how": "MM1-v3.2's ln(measured / forecast) of the wall cycles per L3 point, by edge (L3-1 x1, L3-2 x2) and side; REPORTED"}
    for sub in ("L3-1", "L3-2"):
        for side in ("below", "above"):
            v = [x["ln_err_wall_v32"] for x in l3 if x["subfamily"] == sub and x["side"] == side and x["ln_err_wall_v32"] is not None]
            rd["L3"][f"{sub} {side}: mean ln err"] = mean(v)
    # Y2: the pairs against E216's
    theta = R["theta_pair_ln"]
    y = []
    for pid, row in R["arms"][arm]["y2_pairs"].items():
        if not row.get("complete"):
            continue
        a, b = row["points"]
        if a in M and b in M:
            mm = math.log(M[a]["wall"] / M[b]["wall"])
            src = row.get("e216_measured_ln_a_over_b_aifoundry2_card0")
            rep = abs(mm) > theta and src is not None and (mm > 0) == (src > 0)
            y.append({"pair": pid, "token": row["token"], "masks": row["masks"], "measured_ln_a_over_b": mm, "e216_source": row["e216_source_pair"],
                      "e216_measured": src, "repeats": rep})
    k = sum(1 for x in y if x["repeats"])
    rd["Y2"] = {"pairs": y, "theta_ln": theta, "repeating": k,
                "reading": ("NO DATA" if not y else ("REPEATS" if k >= 4 else ("DOES NOT REPEAT" if k <= 1 else "MIXED"))) if len(y) >= 4 else ("TOO FEW" if y else "NO DATA"),
                "how": "a pair repeats E216's effect when |ln(wall a / wall b)| > theta with E216's sign; REPEATS at 4 or more of 5, DOES NOT REPEAT at 1 or fewer; REPORTED"}
    # G2: the measured gemmLnc excess against F3's
    g = []
    for pid, p in pts.items():
        if p["family"] == "G2" and pid in M and p.get("twin") in M:
            t = p["twin"]
            x = fcv(F, arm, pid, M[pid]["col"], "MM1-v3.2")
            if M[pid].get("W") is not None and M[t].get("W") is not None:
                dm = M[pid]["W"] - M[t]["W"]
                g.append({"id": pid, "twin": t, "token": p["token"], "measured_excess_W": dm, "F3_predicted_W": x.get("F3_W_at_own_t"),
                          "ratio_measured_over_F3": (dm / x["F3_W_at_own_t"]) if x.get("F3_W_at_own_t") else None})
    over = sum(1 for x in g if x["F3_predicted_W"] is not None and x["measured_excess_W"] < x["F3_predicted_W"])
    rd["G2"] = {"points": g, "F3_over_predicts_at": over, "n": len(g),
                "reading": ("NO DATA" if not g else ("OVER-PREDICTS" if over >= max(5, math.ceil(0.7 * len(g))) else
                                                     ("UNDER-PREDICTS" if (len(g) - over) >= max(5, math.ceil(0.7 * len(g))) else "MIXED"))),
                "how": "per G2 point the measured W over idle less its twin's (each at its own measured seconds) against MM1-v3.2's F3 W; REPORTED"}
    return rd


def score(dA, dB, P, F, R, labels=None, tagA="A"):
    labels = labels or {}
    out = {"experiment": "E220", "arms": {}, "pooled": {}}
    Ms = {}
    for arm in ("A", "B"):
        if arm == "A":
            M, Mm, flags, r0, s6, has = read_a(dA or {}, P, tagA, labels)
        else:
            M, Mm, flags, r0, s6, has = read_b(dB or [], P, labels)
        Ms[arm] = M
        res = {"flags": flags, "measured": M, "route_m_REPORTED": Mm, "rules": {}, "head_to_head": {}, "cross_card": {}}
        res["rules"]["R0"] = {"verdict": ("NO DATA" if not has else ("PASS" if not r0 else "FAIL")), "failures": r0}
        if arm == "A":
            res["rules"]["S6"] = {"verdict": ("NO DATA" if not has else ("PASS" if not s6 else "FAIL")), "failures": s6}
        label = None
        if res["rules"]["R0"]["verdict"] == "FAIL" or (arm == "A" and res["rules"]["S6"]["verdict"] == "FAIL"):
            label = "labelled: " + ("R0 FAIL" if res["rules"]["R0"]["verdict"] == "FAIL" else "S6 FAIL")
        cells = cells_of(M, F, R, arm)
        for q in RULES_T:
            v = verdict(cells[q])
            if label and v["verdict"] not in ("NO DATA",):
                v["label"] = label
            res["rules"][q] = v
        res["cells"] = cells
        for hid, x, y, q in H2H:
            v = decide(h_cases(M, F, R, arm, x, y, q), x, y)
            if label:
                v["label"] = label
            res["head_to_head"][hid] = v
        for cid, q in (("CX-T", "wall"), ("CX-E", "Wg")):
            cs, offs = cx_cases(M, F, R, arm, q)
            v = decide(cs, "here", "a3", names=("LARGER HERE", "SMALLER HERE"))
            if label:
                v["label"] = label
            if q == "wall":
                v["card_offset_REPORTED"] = {"n": len(offs), "median_ln_measured_here_over_a3": (sorted(offs)[len(offs) // 2] if offs else None),
                                             "mean_ln": mean(offs)}
            res["cross_card"][cid] = v
        res["family_stats_REPORTED"] = family_stats(M, F, P, arm)
        res["readings_REPORTED"] = readings(M, F, P, R, arm)
        res["label"] = label
        out["arms"][arm] = res
    lab = [out["arms"][a]["label"] for a in ("A", "B") if out["arms"][a]["label"]]
    for hid, x, y, q in H2H:
        v = decide(h_cases(Ms["A"], F, R, "A", x, y, q) + h_cases(Ms["B"], F, R, "B", x, y, q), x, y)
        if lab:
            v["label"] = "; ".join(f"arm {a} {out['arms'][a]['label']}" for a in ("A", "B") if out["arms"][a]["label"])
        out["pooled"]["HP" + hid[1:]] = v
    for cid, q in (("CXP-T", "wall"), ("CXP-E", "Wg")):
        cs = cx_cases(Ms["A"], F, R, "A", q)[0] + cx_cases(Ms["B"], F, R, "B", q)[0]
        v = decide(cs, "here", "a3", names=("LARGER HERE", "SMALLER HERE"))
        if lab:
            v["label"] = "; ".join(f"arm {a} {out['arms'][a]['label']}" for a in ("A", "B") if out["arms"][a]["label"])
        out["pooled"][cid] = v
    out["verdicts"] = {f"{a}:{k}": v["verdict"] for a in ("A", "B") for k, v in out["arms"][a]["rules"].items()}
    out["verdicts"].update({f"{a}:{k}": v["verdict"] for a in ("A", "B") for k, v in out["arms"][a]["head_to_head"].items()})
    out["verdicts"].update({f"{a}:{k}": v["verdict"] for a in ("A", "B") for k, v in out["arms"][a]["cross_card"].items()})
    out["verdicts"].update({k: v["verdict"] for k, v in out["pooled"].items()})
    return out


# ------------------------------------------------------------------ the self-tests: stand-in days in each arm's reader form
def truth_of(F, arm, pid, col, model):
    x = fcv(F, arm, pid, col, model)
    return {"wall": x["cycles_per_op_wall"], "mean": x["cycles_per_op_mean"], "t": x["seconds_per_gemm"], "T": x["T_op_us"], "W": x.get("W_over_idle"),
            "prest": x.get("rest_law_W"), "A": x.get("A_W"), "B": x.get("B_W_us")}


def make_a(P, F, fn, mutate=None):
    pts = {}
    for p in P["points"]["A"]:
        tr = fn("A", p)
        if tr is None:
            continue
        ops = p["ops_per_minion_per_gemm"]
        runs = []
        for n in (1, 2):
            r = {"n": n, "block": "pass1", "checks": ["approx"], "cycles_gemm": tr["wall"] * ops, "cycles_per_op": tr["mean"], "t_gemm_s": tr["t"],
                 "p_work_w": tr["prest"] + tr["W"], "p_rest_w": tr["prest"], "mhz_min": tr.get("mhz", 600), "mhz_max": tr.get("mhz", 600),
                 "record": {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]}}
            if p["host"] == "rgm211":
                r["walk"] = {"ok": [True], "launches_bad": 0}
                r["gate"] = "GATE OK: rgm136 gemmLnc (stand-in)"
            runs.append(r)
        pts[p["id"]] = {"runs": runs}
    d = {"arms": {"A": {"points": pts, "ties": {"runs": [{"n": 1, "block": "tie", "checks": ["approx"], "cycles_per_op": 1100.0}]},
                        "smoke": {"runs": [{"n": 0, "block": "smoke", "point": "s01", "checks": ["approx"], "cycles_per_op": 1100.0},
                                           {"n": 0, "block": "smoke", "point": "s03", "checks": ["approx"], "cycles_per_op": 1100.0,
                                            "walk": {"ok": [True], "launches_bad": 0}, "gate": "GATE OK: stand-in"}]}}}}
    if mutate:
        mutate(d)
    return d


def make_b(P, F, fn, mutate=None):
    runs = []
    i = 0
    for p in P["points"]["B"]:
        tr = fn("B", p)
        if tr is None:
            continue
        for _ in (1, 2):
            i += 1
            f = tr.get("mhz", 799.0)
            v = {"T_op_us": tr["T"], "cyc_op_max": tr["wall"], "cyc_op_mean": tr["mean"], "t_pass_s": tr["t"], "kclock_mhz": f, "n_launch": 5,
                 "dP_w": tr["W"], "p_mean_w": tr["prest"] + tr["W"], "J_pass_over": tr["W"] * tr["t"], "J_pass_with": (tr["prest"] + tr["W"]) * tr["t"],
                 "mhz_min": f, "mhz_mean": f}
            runs.append({"role": "arm", "arm": p["id"], "i": i, "form": "burst", "shires": p["shire_mask"], "type": p["format"], "minions": p["minions"],
                         "ran": True, "checks": ["approx"], "capped": False, "primary_view": "win", "views": {"win": v},
                         "frac_800_after_step": tr.get("frac", 1.0)})
    d = {"runs": runs, "smoke": [{"good": True, "rc": 0, "check": "approx"}], "anchors": []}
    if mutate:
        mutate(d)
    return [d]


def selftest_standins(out_path):
    P, F, R = load_frozen(check=False)
    base = {arm: R["arms"][arm]["cross_card"]["baseline_aifoundry3_E218"] for arm in ("A", "B")}

    def model_truth(model, tscale=1.0, wscale=1.0):
        def fn(arm, p):
            tr = truth_of(F, arm, p["id"], COL[arm], model)
            t32 = truth_of(F, arm, p["id"], COL[arm], "MM1-v3.2")
            tr["prest"] = t32["prest"]
            if tr["W"] is None:
                return None
            if tscale != 1.0:
                tr["wall"] *= tscale
                tr["mean"] *= tscale
                tr["t"] *= tscale
                tr["T"] *= tscale
                tr["W"] = t32["A"] + t32["B"] / tr["T"]       # energy exact given the measured op time
            tr["W"] *= wscale
            return tr
        return fn

    def cx_truth(k):
        """this card's MM1-v3.2 error = k x its aifoundry3 error (same sign), at the X twins; MM1-v3.2 exact elsewhere"""
        def fn(arm, p):
            tr = truth_of(F, arm, p["id"], COL[arm], "MM1-v3.2")
            b = base[arm].get(p["id"])
            if isinstance(b, dict) and "a3_ln_err_wall" in b:
                g = math.exp(k * b["a3_ln_err_wall"])
                tr["wall"] *= g
                tr["mean"] *= g
                tr["t"] *= g
                tr["T"] *= g
                W0 = tr["A"] + tr["B"] / tr["T"]
                tr["W"] = W0 * math.exp(k * (b.get("a3_ln_err_Wg") or 0.0))
            return tr
        return fn

    def y2_truth(arm, p):
        tr = truth_of(F, arm, p["id"], COL[arm], "MM1-v3.2")
        if p["family"] == "Y2" and p["pair_role"] == "a":
            for q in ("wall", "mean", "t", "T"):
                tr[q] *= math.exp(0.05)
            tr["W"] = tr["A"] + tr["B"] / tr["T"]
        return tr

    def g2_truth(arm, p):
        tr = truth_of(F, arm, p["id"], COL[arm], "MM1-v3.2")
        if p["family"] == "G2":
            x = fcv(F, arm, p["id"], COL[arm], "MM1-v3.2")
            tw = truth_of(F, arm, p["twin"], COL[arm], "MM1-v3.2")
            tr["W"] = tw["W"] + 0.5 * x["F3_W_at_own_t"]
        return tr

    def badcheck_a(d):
        k = sorted(d["arms"]["A"]["points"])[0]
        d["arms"]["A"]["points"][k]["runs"][0]["checks"] = ["wrong"]

    def badcheck_b(d):
        d["runs"][0]["checks"] = ["wrong"]

    def at700_a(arm, p):
        tr = model_truth("MM1-v3.2")(arm, p)
        tr["mhz"] = 700
        return tr

    def at700_b(arm, p):
        tr = model_truth("MM1-v3.2")(arm, p)
        tr["mhz"] = 700.0
        tr["frac"] = 0.5
        return tr
    days = {
        "v32": ("every point at MM1-v3.2's frozen forecast, the rest at its rest law", make_a(P, F, model_truth("MM1-v3.2")), make_b(P, F, model_truth("MM1-v3.2")),
                dict({f"{a}:{q}": "PASS" for a in "AB" for q in ("R0",) + RULES_T}, **{"A:S6": "PASS"},
                     **{f"{a}:H{i}": "MM1-v3.2 BETTER" for a in "AB" for i in range(1, 11)},
                     **{f"HP{i}": "MM1-v3.2 BETTER" for i in range(1, 11)},
                     **{f"{a}:CX-T": "SMALLER HERE" for a in "AB"}, **{f"{a}:CX-E": "SMALLER HERE" for a in "AB"},
                     **{"CXP-T": "SMALLER HERE", "CXP-E": "SMALLER HERE"})),
        "v3": ("every point at MM1-v3's", make_a(P, F, model_truth("MM1-v3")), make_b(P, F, model_truth("MM1-v3")),
               dict({f"{a}:H{i}": "MM1-v3 BETTER" for a in "AB" for i in range(1, 6)}, **{f"HP{i}": "MM1-v3 BETTER" for i in range(1, 6)})),
        "v31": ("every point at MM1-v3.1's", make_a(P, F, model_truth("MM1-v3.1")), make_b(P, F, model_truth("MM1-v3.1")),
                dict({f"{a}:H{i}": "MM1-v3.1 BETTER" for a in "AB" for i in range(6, 11)}, **{f"HP{i}": "MM1-v3.1 BETTER" for i in range(6, 11)})),
        "t150": ("MM1-v3.2's cycles and seconds x 1.5, its energy exact given the op time", make_a(P, F, model_truth("MM1-v3.2", tscale=1.5)),
                 make_b(P, F, model_truth("MM1-v3.2", tscale=1.5)),
                 {f"{a}:{q}": w for a in "AB" for q, w in (("T1", "FAIL"), ("T2", "FAIL"), ("T3", "FAIL"), ("E1", "PASS"), ("E3", "PASS"), ("E4", "FAIL"))}),
        "w150": ("MM1-v3.2's W over idle x 1.5", make_a(P, F, model_truth("MM1-v3.2", wscale=1.5)), make_b(P, F, model_truth("MM1-v3.2", wscale=1.5)),
                 {f"{a}:{q}": w for a in "AB" for q, w in (("T1", "PASS"), ("E1", "FAIL"), ("E2", "FAIL"), ("E3", "FAIL"), ("E4", "FAIL"))}),
        "cx3": ("this card's MM1-v3.2 error 3 x its aifoundry3 error at every X twin", make_a(P, F, cx_truth(3.0)), make_b(P, F, cx_truth(3.0)),
                dict({f"{a}:CX-T": "LARGER HERE" for a in "AB"}, **{f"{a}:CX-E": "LARGER HERE" for a in "AB"}, **{"CXP-T": "LARGER HERE", "CXP-E": "LARGER HERE"})),
        "cx1": ("this card's MM1-v3.2 error equal to its aifoundry3 error at every X twin", make_a(P, F, cx_truth(1.0)), make_b(P, F, cx_truth(1.0)),
                dict({f"{a}:CX-T": "TOO FEW" for a in "AB"}, **{f"{a}:CX-E": "TOO FEW" for a in "AB"})),
        "badcheck": ("one run's check of C wrong on each arm", make_a(P, F, model_truth("MM1-v3.2"), badcheck_a), make_b(P, F, model_truth("MM1-v3.2"), badcheck_b),
                     {"A:R0": "FAIL", "B:R0": "FAIL"}),
        "at700": ("every run at 700 MHz (arm A: S6; arm B: a step, route m only)", make_a(P, F, at700_a), make_b(P, F, at700_b),
                  {"A:S6": "FAIL", "B:T1": "NO DATA", "B:E1": "NO DATA", "B:H1": "NO DATA", "B:CX-T": "NO DATA"}),
        "nodata": ("no data", {}, [], dict({f"{a}:{q}": "NO DATA" for a in "AB" for q in ("R0", "T1", "E1", "H1", "CX-T")}, **{"HP1": "NO DATA", "CXP-T": "NO DATA"})),
        "y2": ("each Y2 pair's first mask 5% slower (in ln) than MM1-v3.2, the rest exact", make_a(P, F, y2_truth), make_b(P, F, y2_truth), {}),
        "g2": ("each G2 point's excess half of F3's predicted", make_a(P, F, g2_truth), make_b(P, F, g2_truth), {}),
    }
    want_read = {"y2": {"A": "REPEATS", "B": "REPEATS"}, "g2": {"A": "OVER-PREDICTS", "B": "OVER-PREDICTS"}, "v32": {"A": "DOES NOT REPEAT", "B": "DOES NOT REPEAT"}}
    res, ok = {}, True
    for name, (what, dA, dB, want) in days.items():
        S = score(dA, dB, P, F, R)
        got = {k: S["verdicts"].get(k) for k in want}
        good = {k: (got[k] == w) for k, w in want.items()}
        rd = {}
        if name in want_read:
            for arm, w in want_read[name].items():
                key = "Y2" if name in ("y2", "v32") else "G2"
                g = S["arms"][arm]["readings_REPORTED"][key]["reading"]
                rd[f"{arm}:{key} reading"] = {"got": g, "want": w, "ok": g == w}
        day_ok = all(good.values()) and all(v["ok"] for v in rd.values())
        ok &= day_ok
        res[name] = {"what": what, "ok": day_ok, "checks": {k: {"got": got[k], "want": w, "ok": good[k]} for k, w in want.items()}, "readings": rd}
    covered = {}
    for name, r in res.items():
        for k, c in r["checks"].items():
            covered.setdefault(k.split(":")[-1], set()).add(c["got"])
    both = {k: sorted(v) for k, v in covered.items()}
    rec = {"what": "score_e220.py's self-test on stand-in days in each arm's reader form (arm A E215's form, arm B E208's reducer form)",
           "verdict": "PASS" if ok else "FAIL", "days": res, "verdicts_seen_by_rule": both}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-standins: {rec['verdict']} ({sum(1 for r in res.values() if r['ok'])} of {len(res)} days)")
    for name, r in res.items():
        if not r["ok"]:
            print("  FAILED", name, {k: v for k, v in r["checks"].items() if not v["ok"]}, r["readings"])
    return ok


def selftest_real(out_path):
    """the two readers on real committed bytes from each arm's card: arm A's reader on E215 arm B's data (aifoundry1 card 1, E215's form, its
    points standing in for E220's), arm B's reader on E216's data (aifoundry2 card 0, E208's reducer form, E216's points standing in)"""
    P, F, R = load_frozen(check=False)
    A_REL = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/data-e215.json"
    B_REL = "docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/data-e216.json"
    dA = json.load(open(os.path.join(REPO, A_REL)))
    dB = json.load(open(os.path.join(REPO, B_REL)))
    e215 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e215", "points-e215.json")))["arms"]["B"]["points"]
    e216 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e216", "points-e216.json")))["points"]
    PA = {"points": {"A": [{"id": p["id"], "arm": p["arm"], "format": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"],
                            "host": p["host"], "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"], "loop": p["loop"], "family": p["family"]}
                           for p in e215], "B": []}}
    PB = {"points": {"A": [], "B": [{"id": p["id"], "arm": p["arm"], "format": p["fmt"], "minions": p["minions"], "shire_mask": p["mask"],
                                     "loop": p["loop"], "family": p["family"]} for p in e216]}}
    MA, _, fa, r0a, s6a, _ = read_a(dA, PA, "B", {})
    MB, MmB, fb, r0b, _, _ = read_b([dB], PB, {})
    okA = len(MA) == len(e215) and not r0a and not s6a and all(m.get("W") is not None for m in MA.values())
    okB = len(MB) >= 0.9 * len(e216) and not r0b
    rec = {"what": "score_e220's readers on real committed bytes from each arm's card", "arm_A_reader": {"input": A_REL, "sha256": sha(os.path.join(REPO, A_REL)),
           "points_read": len(MA), "points_registered": len(e215), "R0_failures": r0a, "S6_failures": s6a, "flags": fa[:20], "ok": okA},
           "arm_B_reader": {"input": B_REL, "sha256": sha(os.path.join(REPO, B_REL)), "points_route_c": len(MB), "points_route_m": len(MmB),
                            "points_registered": len(e216), "R0_failures": r0b, "flags": fb[:20], "ok": okB},
           "verdict": "OK" if (okA and okB) else "NOT OK"}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-real: {rec['verdict']} (arm A reader {len(MA)}/{len(e215)} points, R0 {len(r0a)}, S6 {len(s6a)}; arm B reader route c "
          f"{len(MB)}/{len(e216)}, route m {len(MmB)}, R0 {len(r0b)})")
    return okA and okB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a")
    ap.add_argument("--a-tag", default="A")
    ap.add_argument("--b", action="append", default=[])
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins", action="store_true")
    ap.add_argument("--selftest-real", action="store_true")
    a = ap.parse_args()
    if a.selftest_standins:
        sys.exit(0 if selftest_standins(os.path.join(HERE, "selftest-standins.json")) else 1)
    if a.selftest_real:
        sys.exit(0 if selftest_real(os.path.join(HERE, "selftest-real.json")) else 1)
    P, F, R = load_frozen()
    dA = json.load(open(a.a)) if a.a else {}
    dB = [json.load(open(x)) for x in a.b]
    labels = json.load(open(a.labels)) if a.labels else {}
    S = score(dA, dB, P, F, R, labels, a.a_tag)
    os.makedirs(a.out, exist_ok=True)
    json.dump(S, open(os.path.join(a.out, "scores-e220.json"), "w"), indent=1, sort_keys=True)
    lines = [f"{k}: {v}" for k, v in sorted(S["verdicts"].items())]
    open(os.path.join(a.out, "scores-e220.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
