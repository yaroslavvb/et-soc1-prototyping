#!/usr/bin/env python3
"""E216 (Q227): THE SCORER, registered before any datum. Standard library only. It refuses to run (exit 4) if a pinned registration file changed.

    python3 -I -B tools/claims-v3/e216/score_e216.py <data.json> [<data.json> ...] [--labels L.json] --out scores-e216.json
        THE DATA: one or more outputs of E208's registered reducer (tools/claims-v3/e208/proposal/src/reduce_mms.py, E209's measured side):
        {"smoke": [...], "runs": [...]}, each run with arm (the E216 point id), role, form, checks, capped, no_step, shires, type, minions, ran,
        primary_view, frac_800_after_step and views (kclock_mhz, cyc_op_max, cyc_op_mean, T_op_us, t_pass_s, n_launch, dP_w, p_mean_w,
        J_pass_over, J_pass_with, thin, mhz_min, mhz_mean). --labels: {"ran_before_points": [ids]} (the card lane's step 6n), never scored.
    python3 -I -B tools/claims-v3/e216/score_e216.py --forecasts
        PRINTS the frozen columns the scorer reads, checks them against the pinned bytes; writes nothing
    python3 -I -B tools/claims-v3/e216/score_e216.py --selftest-standins <out.json>
        builds reducer-form stand-in days from the frozen forecasts and checks that every rule PASSES and FAILS where it must

THE RULES (E216.md section 7; every number in rules-e216.json):
  R0       every check of C of the day exact or approx (every point run's and anchor's) and the smoke good: a FAIL labels every other verdict.
  ROUTES   route c (registered): a run whose primary view's kernel clock reads 790-810 MHz, not STEP and not NO STEP, scored against the frozen
           799.0 MHz column; route m (REPORTED): every other run, against the frozen column nearest its view clock (700 or 600 MHz), flagged.
           A capped or thin run carries no energy (the reducer's rule). A point is the mean of its kept runs; a time case is its point.
  T1 T2 T3 MM1-v3.1's wall cycles, counter mean, seconds per point: |measured / forecast - 1| <= the band; E1 J over idle given the measured
           op time (W = A + B / T_op measured, x the measured seconds); E2 J over idle with the seconds forecast (the frozen J); E3 J at rest
           given t (the run's measured rest x t + E1's J); E4 J at rest with t forecast (the measured rest x the forecast seconds + E2's J). A
           point whose forecast W given t or measured W over idle is under 3 W is scored in watts in E1 and E2 (|W - W| <= band_W). A rule
           PASSES with at least 90% of its scored points within band; FAIL otherwise; TOO FEW under 10; NO DATA with none. Scored over the
           REGISTERED points (families G, Gt, Y and F's new points); F's card-transfer twins are scored apart (the same rules, own lines).
  H1t H1w H2w H2f H3 H4   exact two-sided sign tests (rules-e216.json > ties): FIRST BETTER / SECOND BETTER at p < 0.05 with >= 10 decided,
           NOT DECIDED, TOO FEW (< 10 decided), NO DATA. H2j = H2w by arithmetic (asserted).
  P1       the pair rule (rules-e216.json > pair_rule).
Every figure the scorer prints is measured (from the data) or frozen (from the registration); none is fitted here.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# fix-e216 (Q227, Thu 19 Nov 2026, before any E216 datum; E216-amendment-1.md A1, verify-e216's F1): rules-e216.json re-frozen (P1's minimum
# 5 decided pairs, was 4) and re-pinned below; no other line of this scorer changed (the A2 and A4 readings are report_e216.py's, REPORTED).
PINS = {"points-e216.json": "63899cae4e7122cf665f9ab37d146bb209d2294669f20c89ac87dbd689753e3c", "forecast-e216.json": "92c9444a7a0d72a0198fd3581a72c2a05b00969d08b024d09c90eab4f3dda5dc", "rules-e216.json": "c6a8f10c88445b2cca72ece73168d247e5fd10e40d02e7de4cd721f070c1806e"}
MODELS = ("MM1-v3.1", "MM1-v3", "MM1-v2", "v3.1+lnc", "v3.1+contention", "v3.1+both", "v3.1 with T7")
CLOCKS = {799.0: "799.0", 700.0: "700.0", 600.0: "600.0"}
H2H = {"H1t": ("MM1-v3.1", "MM1-v3", "wall", "registered"), "H1w": ("MM1-v3.1", "MM1-v3", "Wg", "registered"),
       "H1t-twins": ("MM1-v3.1", "MM1-v3", "wall", "twins"), "H1w-twins": ("MM1-v3.1", "MM1-v3", "Wg", "twins"),
       "H2w": ("v3.1+lnc", "MM1-v3.1", "Wg", "G"), "H2f": ("v3.1+lnc", "MM1-v3.1", "Jf", "G"),
       "H3": ("v3.1+contention", "MM1-v3.1", "wall", "Y"), "H4": ("v3.1+both", "MM1-v3.1", "mixed", "registered")}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_pins():
    bad = {k: sha(os.path.join(HERE, k)) for k, v in PINS.items() if sha(os.path.join(HERE, k)) != v}
    if bad:
        print("score_e216: REFUSED, a pinned registration file changed:", sorted(bad))
        sys.exit(4)


def load():
    P = {p["id"]: p for p in json.load(open(os.path.join(HERE, "points-e216.json")))["points"]}
    FC = json.load(open(os.path.join(HERE, "forecast-e216.json")))["points"]
    R = json.load(open(os.path.join(HERE, "rules-e216.json")))
    return P, FC, R


def mask_int(x):
    try:
        return int(str(x), 16)
    except (TypeError, ValueError):
        return None


def fnum(x):
    return None if x in (None, "") else float(x)


def read_run(r, P):
    pid = r.get("arm")
    if r.get("role") != "arm" or pid not in P or r.get("form") == "null":
        return None
    p = P[pid]
    rec = {"id": pid, "i": r.get("i"), "checks": list(r.get("checks") or []), "capped": bool(r.get("capped")), "flags": [], "set_aside": None,
           "no_step": bool(r.get("no_step")) or r.get("primary_view") == "band600"}
    why = []
    if mask_int(r.get("shires")) != int(p["mask"], 16):
        why.append(f"mask {r.get('shires')}")
    if r.get("type") != p["fmt"]:
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
    rec.update({"f": float(v["kclock_mhz"]), "wall": float(v["cyc_op_max"]), "mean": fnum(v.get("cyc_op_mean")), "t": float(v["t_pass_s"]),
                "T_op": float(v["T_op_us"])})
    if v.get("dP_w") is not None and v.get("p_mean_w") and not r.get("capped") and not v.get("thin"):
        rec.update({"W": float(v["dP_w"]), "p_rest": float(v["p_mean_w"]) - float(v["dP_w"]), "J_over": float(v["J_pass_over"]),
                    "J_rest": float(v["J_pass_with"])})
    fr = r.get("frac_800_after_step")
    step = (fr is not None and fr < 1.0 and not rec["no_step"]) or \
        (v.get("mhz_min") is not None and v.get("mhz_mean") is not None and float(v["mhz_min"]) < float(v["mhz_mean"]) - 0.5)
    rec["step"] = bool(step)
    route_c = (790.0 <= rec["f"] <= 810.0) and not step and not rec["no_step"]
    rec["route"] = "c" if route_c else "m"
    rec["col"] = "799.0" if route_c else CLOCKS[min(CLOCKS, key=lambda c: abs(c - rec["f"]))]
    if step:
        rec["flags"].append("STEP")
    if rec["no_step"]:
        rec["flags"].append("NO STEP")
    if rec["capped"]:
        rec["flags"].append("CAPPED: no energy")
    if not route_c:
        rec["flags"].append(f"ROUTE m at {rec['col']} MHz")
    return rec


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def point_figures(P, runs):
    """per point and route: the mean of its kept runs (time; energy where read)"""
    by = {}
    for r in runs:
        if r["set_aside"] is None:
            by.setdefault((r["id"], r["route"], r["col"]), []).append(r)
    out = {}
    for (pid, route, col), rs in by.items():
        e = [r for r in rs if "W" in r]
        out.setdefault(pid, {})[route if route == "c" else "m@" + col] = {"col": col, "n_runs": len(rs), "wall": mean([r["wall"] for r in rs]), "mean": mean([r["mean"] for r in rs]),
                                          "t": mean([r["t"] for r in rs]), "T_op": mean([r["T_op"] for r in rs]), "n_energy": len(e),
                                          "W": mean([r["W"] for r in e]), "J_over": mean([r["J_over"] for r in e]),
                                          "J_rest": mean([r["J_rest"] for r in e]), "p_rest": mean([r["p_rest"] for r in e]),
                                          "t_e": mean([r["t"] for r in e]), "T_op_e": mean([r["T_op"] for r in e])}
    return out


def fcv(FC, pid, col, model):
    return FC[pid][col]["forecasts"][model]


def predicted(FC, pid, col, model, m):
    """the model's forecasts at the point's measured figures (given t) and at its own (t forecast)"""
    x = fcv(FC, pid, col, model)
    o = {"wall": x["cycles_per_op_wall"], "mean": x.get("cycles_per_op_mean"), "seconds": x["seconds_per_gemm"]}
    if x.get("A_W") is not None and m.get("T_op_e"):
        Wg = x["A_W"] + x["B_W_us"] / m["T_op_e"]
        o.update({"Wg": Wg, "Jg": Wg * m["t_e"], "Wf": x["W_over_idle"], "Jf": x["J_over_idle_per_gemm"]})
        if m.get("p_rest") is not None:
            o["JRg"] = m["p_rest"] * m["t_e"] + Wg * m["t_e"]
            o["JRf"] = m["p_rest"] * x["seconds_per_gemm"] + x["J_over_idle_per_gemm"]
    return o


def cell(meas, fc, band):
    if meas is None or fc is None:
        return None
    e = meas / fc - 1.0
    return {"err": e, "pass": abs(e) <= band + 1e-12}


def verdict(cells, share=0.9, too_few=10):
    c = [x for x in cells if x is not None]
    if not c:
        return {"verdict": "NO DATA", "n": 0, "pass": 0}
    k = sum(1 for x in c if x["pass"])
    if len(c) < too_few:
        return {"verdict": "TOO FEW", "n": len(c), "pass": k}
    need = math.ceil(share * len(c) - 1e-9)
    return {"verdict": "PASS" if k >= need else "FAIL", "n": len(c), "pass": k, "need": need}


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n)


def group_ids(P, g):
    if g == "registered":
        return sorted(i for i, p in P.items() if p.get("subfamily") != "card-transfer twin")
    if g == "twins":
        return sorted(i for i, p in P.items() if p.get("subfamily") == "card-transfer twin")
    return sorted(i for i, p in P.items() if p["family"] == g)


def score(datas, P, FC, R, labels=None):
    labels = labels or {}
    rb = set(labels.get("ran_before_points") or [])
    runs, anchors, smoke, other = [], [], [], []
    for D in datas:
        smoke += list(D.get("smoke") or [])
        for r in D.get("runs") or []:
            if r.get("role") == "anchor":
                anchors.append(r)
                continue
            x = read_run(r, P)
            if x is None:
                if r.get("form") != "null":
                    other.append(r.get("arm"))
                continue
            if x["id"] in rb:
                x["set_aside"] = "labelled ran before (step 6n)"
            runs.append(x)
    out = {"experiment": "E216", "rules": {}, "head_to_head": {}, "points": {}, "flags": {}, "other_runs": other,
           "labels_applied": sorted(rb)}
    chk = [c for r in runs if r["set_aside"] != "did not run" for c in (r["checks"] or [None])] + \
        [c for a in anchors if a.get("ran", True) for c in (a.get("checks") or [None])]
    sm_ok = bool(smoke) and all(s.get("good") and s.get("rc") == 0 and s.get("check") in ("exact", "approx") for s in smoke)
    if not runs and not anchors and not smoke:
        r0 = "NO DATA"
    else:
        r0 = "PASS" if (sm_ok and all(c in ("exact", "approx") for c in chk)) else "FAIL"
    out["rules"]["R0"] = {"verdict": r0, "checks_read": len(chk), "checks_not_ok": sum(1 for c in chk if c not in ("exact", "approx")),
                          "smoke_records": len(smoke), "smoke_ok": sm_ok}
    PF = point_figures(P, runs)
    for r in runs:
        if r["flags"] or r["set_aside"]:
            out["flags"].setdefault(r["id"], []).append({"i": r["i"], "flags": r["flags"], "set_aside": r["set_aside"]})
    B = {q: R["bands"][q]["band"] for q in ("T1", "T2", "T3", "E1", "E2", "E3", "E4")}
    BW = R["band_w"]["band_W"]
    LOW = R["low_W"]
    cells = {}
    for pid in P:
        m = (PF.get(pid) or {}).get("c")
        rec = {"measured_route_c": m, "measured_route_m_REPORTED": {k: v for k, v in (PF.get(pid) or {}).items() if k.startswith("m@")}}
        if m:
            fp = predicted(FC, pid, "799.0", "MM1-v3.1", m)
            c = {"T1": cell(m["wall"], fp["wall"], B["T1"]), "T2": cell(m["mean"], fp["mean"], B["T2"]), "T3": cell(m["t"], fp["seconds"], B["T3"])}
            if m.get("W") is not None and fp.get("Wg") is not None:
                low = (m["W"] < LOW) or (fp["Wg"] < LOW)
                if low:
                    c["E1"] = {"err_W": m["W"] - fp["Wg"], "pass": abs(m["W"] - fp["Wg"]) <= BW + 1e-12, "watts": True}
                    c["E2"] = {"err_W": m["W"] - fp["Wf"], "pass": abs(m["W"] - fp["Wf"]) <= BW + 1e-12, "watts": True}
                else:
                    c["E1"] = cell(m["J_over"], fp["Jg"], B["E1"])
                    c["E2"] = cell(m["J_over"], fp["Jf"], B["E2"])
                c["E3"] = cell(m["J_rest"], fp.get("JRg"), B["E3"])
                c["E4"] = cell(m["J_rest"], fp.get("JRf"), B["E4"])
            rec["cells_MM1-v3.1"] = c
            rec["REPORTED_cells_other_models"] = {}
            for mod in MODELS[1:]:
                fo = predicted(FC, pid, "799.0", mod, m)
                rec["REPORTED_cells_other_models"][mod] = {"T1": cell(m["wall"], fo["wall"], B["T1"]),
                                                           "E1": (cell(m["J_over"], fo.get("Jg"), B["E1"]) if (m.get("W") and fo.get("Jg")) else None)}
            cells[pid] = c
        out["points"][pid] = rec
    for g in ("registered", "twins"):
        ids = group_ids(P, g)
        for q in ("T1", "T2", "T3", "E1", "E2", "E3", "E4"):
            v = verdict([cells[i].get(q) for i in ids if i in cells])
            out["rules"][f"{q}" if g == "registered" else f"{q}-twins"] = v
    # head-to-heads
    T = R["ties"]
    for h, (a, b, q, g) in H2H.items():
        ids = group_ids(P, g)
        rows = []
        for pid in ids:
            m = (PF.get(pid) or {}).get("c")
            if not m:
                continue
            fa, fb = predicted(FC, pid, "799.0", a, m), predicted(FC, pid, "799.0", b, m)
            if q == "mixed":
                fam = P[pid]["family"]
                qq = "Wg" if fam == "G" else "wall"
            else:
                qq = q
            meas = {"wall": m["wall"], "Wg": m.get("W"), "Jf": m.get("J_over")}[qq]
            if meas is None or fa.get(qq) is None or fb.get(qq) is None:
                continue
            watts = qq == "Wg" and (meas < LOW or fa[qq] < LOW)
            if watts:
                d = abs(meas - fb[qq]) - abs(meas - fa[qq])
                tie = T["watts_W"]
            else:
                d = abs(math.log(meas / fb[qq])) - abs(math.log(meas / fa[qq]))
                tie = T["cycles_ln"] if qq == "wall" else T["joules_ln"]
            rows.append({"id": pid, "q": qq, "d": d, "tie": tie, "watts": watts})
        npos = sum(1 for r in rows if r["d"] > r["tie"])
        nneg = sum(1 for r in rows if r["d"] < -r["tie"])
        nt = len(rows) - npos - nneg
        mind = R["h2h_min_decided"][h]
        if not rows:
            vd = "NO DATA"
        elif npos + nneg < mind:
            vd = "TOO FEW"
        else:
            pv = sign_p(npos, nneg)
            vd = (f"{a} BETTER" if npos > nneg else f"{b} BETTER") if pv < 0.05 else "NOT DECIDED"
        out["head_to_head"][h] = {"first": a, "second": b, "group": g, "verdict": vd, "first_closer": npos, "second_closer": nneg, "ties": nt,
                                  "min_decided": mind,
                                  "p": sign_p(npos, nneg) if rows else None, "n": len(rows)}
    out["head_to_head"]["H2j"] = dict(out["head_to_head"]["H2w"], note="J over idle given t = W given t x the measured seconds: H2w's test")
    # the pair rule
    PR = R["pair_rule"]
    pairs = {}
    for pid, p in P.items():
        if p["family"] == "Y":
            pairs.setdefault(p["pair"], []).append(pid)
    prow = []
    for k in sorted(pairs):
        ida, idb = sorted(pairs[k])
        ma, mb = (PF.get(ida) or {}).get("c"), (PF.get(idb) or {}).get("c")
        if not ma or not mb:
            continue
        dm = math.log(ma["wall"] / mb["wall"])
        dp = math.log(fcv(FC, ida, "799.0", "v3.1+contention")["cycles_per_op_wall"] / fcv(FC, idb, "799.0", "v3.1+contention")["cycles_per_op_wall"])
        dec = abs(dm) > PR["threshold_ln"]
        right = dec and dp != 0.0 and (dm > 0) == (dp > 0)
        prow.append({"pair": k, "measured_ln_a_over_b": dm, "predicted_ln_a_over_b": dp, "decided": dec, "ordered_right": right})
    m_ = sum(1 for r in prow if r["decided"])
    k_ = sum(1 for r in prow if r["ordered_right"])
    pb = sum(math.comb(m_, i) for i in range(k_, m_ + 1)) / 2 ** m_ if m_ else None
    if not prow:
        pv = "NO DATA"
    elif m_ < PR["min_decided"]:
        pv = "TOO FEW"
    else:
        pv = "PASS" if (2 * k_ > m_ and pb <= 0.05) else "FAIL"
    out["rules"]["P1"] = {"verdict": pv, "pairs_measured": len(prow), "decided": m_, "ordered_right": k_,
                          "share": (k_ / m_) if m_ else None, "p_one_sided": pb, "MM1-v3.1": "orders none (equal forecasts within every pair)",
                          "pairs": prow}
    if r0 == "FAIL":
        out["label"] = "R0 FAILED: every other verdict is labelled by it"
    return out


# ------------------------------------------------------------------ stand-ins and the self-test
def standin_days(P, FC, case):
    """reducer-form days made from the frozen columns: the truth a named forecaster (or a distortion of one)"""
    smoke = [{"arm": a, "rc": 0, "check": "exact", "good": True} for a in ("1x1x4-fp32-zeros", "1x1x4-fp16-ones", "1x1x4-int8-rnd")]
    runs = []
    n = 0
    for pid in sorted(P):
        p = P[pid]
        fam = p["family"]
        truth_t, truth_w = "MM1-v3.1", "MM1-v3.1"
        kt, kw, f = 1.0, 1.0, 799.0
        if case == "v3":
            truth_t = truth_w = "MM1-v3"
        elif case == "both":
            truth_t = truth_w = "v3.1+both"
        elif case == "t125":
            kt = 1.25
        elif case == "w125":
            kw = 1.25
        elif case == "at700":
            f = 700.0
        col = CLOCKS[f]
        x = fcv(FC, pid, col, truth_t)
        y = fcv(FC, pid, col, truth_w)
        wall, mn, s = x["cycles_per_op_wall"] * kt, x["cycles_per_op_mean"] * kt, x["seconds_per_gemm"] * kt
        if case in ("pairs_reversed", "pairs_right") and fam == "Y":
            # MM1-v3.1's time, each pair's two points moved 1% apart in ln, in the contention term's predicted order (pairs_right) or against it
            pr_ = sorted(q for q in P if P[q].get("pair") == p["pair"])
            dp = math.log(fcv(FC, pr_[0], col, "v3.1+contention")["cycles_per_op_wall"] / fcv(FC, pr_[1], col, "v3.1+contention")["cycles_per_op_wall"])
            sg = (1.0 if dp > 0 else (-1.0 if dp < 0 else 0.0)) * (1.0 if case == "pairs_right" else -1.0)
            r_ = math.exp((0.01 if pid == pr_[0] else -0.01) * sg)
            wall, mn, s = wall * r_, mn * r_, s * r_
        T = s / p["ops_per_minion_per_gemm"] * 1e6
        W = (y["A_W"] + y["B_W_us"] / T) * kw
        rest = 23.19
        v = {"kclock_mhz": f, "cyc_op_max": wall, "cyc_op_mean": mn, "T_op_us": T, "t_pass_s": s, "n_launch": 12, "mhz_min": f, "mhz_mean": f,
             "dP_w": W, "p_mean_w": rest + W, "J_pass_over": W * s, "J_pass_with": (rest + W) * s}
        n += 1
        checks = ["exact"]
        if case == "badcheck" and n == 3:
            checks = ["wrong"]
        runs.append({"arm": pid, "role": "arm", "form": "burst", "i": n, "ran": True, "shires": p["mask"], "type": p["fmt"], "minions": p["minions"],
                     "checks": checks, "capped": False, "frac_800_after_step": (0.9 if case == "at700" else 1.0), "no_step": False,
                     "primary_view": "win", "views": {"win": v}})
    if case == "nodata":
        return []
    return [{"card": "a2c0", "smoke": smoke, "runs": runs}]


def expected(R):
    """what each stand-in day must read: the per-point rules by construction; each head-to-head by the frozen gaps (rules-e216.json >
    predicted_gaps: a winner when at least its minimum of cases is decidable, else TOO FEW)"""
    G = R["predicted_gaps"]

    def win(h, who):
        return who if G[h]["decidable_gap_over_tie"] >= R["h2h_min_decided"][h] else "TOO FEW"
    return {
        "v31": {"R0": "PASS", "T1": "PASS", "T2": "PASS", "T3": "PASS", "E1": "PASS", "E2": "PASS", "E3": "PASS", "E4": "PASS",
                "H1t": win("H1t", "MM1-v3.1 BETTER"), "H1w": win("H1w", "MM1-v3.1 BETTER"), "H2w": win("H2w", "MM1-v3.1 BETTER"),
                "H2f": win("H2f", "MM1-v3.1 BETTER"), "H3": win("H3", "MM1-v3.1 BETTER"), "H4": win("H4", "MM1-v3.1 BETTER")},
        "v3": {"R0": "PASS", "H1t": win("H1t", "MM1-v3 BETTER"), "H1w": win("H1w", "MM1-v3 BETTER")},
        "both": {"R0": "PASS", "T1": "PASS", "H2w": win("H2w", "v3.1+lnc BETTER"), "H2f": win("H2f", "v3.1+lnc BETTER"),
                 "H3": win("H3", "v3.1+contention BETTER"), "H4": win("H4", "v3.1+both BETTER")},
        "t125": {"T1": "FAIL", "T2": "FAIL", "T3": "FAIL", "E1": "PASS", "E3": "PASS", "E4": "FAIL|PASS"},
        "w125": {"T1": "PASS", "E1": "FAIL", "E2": "FAIL", "E3": "FAIL|PASS"},
        "pairs_right": {"P1": "PASS", "T1": "PASS"},
        "pairs_reversed": {"P1": "FAIL"},
        "at700": {"T1": "NO DATA", "E1": "NO DATA", "H1t": "NO DATA", "P1": "NO DATA"},
        "badcheck": {"R0": "FAIL"},
        "nodata": {"R0": "NO DATA", "T1": "NO DATA", "E1": "NO DATA", "H1t": "NO DATA", "P1": "NO DATA"},
    }


def selftest(P, FC, R, outp):
    res, ok = {}, True
    for case, want in expected(R).items():
        o = score(standin_days(P, FC, case), P, FC, R)
        got = {}
        for k in want:
            got[k] = (o["rules"].get(k) or o["head_to_head"].get(k) or {}).get("verdict")
        good = {k: (got[k] in want[k].split("|")) for k in want}
        ok &= all(good.values())
        res[case] = {"want": want, "got": got, "ok": all(good.values()),
                     "P1": {k: o["rules"]["P1"][k] for k in ("pairs_measured", "decided", "ordered_right")},
                     "h2h": {k: (v["first_closer"], v["second_closer"], v["ties"]) for k, v in o["head_to_head"].items()}}
        print(f"{case:15s} {'OK ' if all(good.values()) else 'BAD'} " + "; ".join(f"{k} {got[k]}" for k in want))
    # every rule seen both PASS (or a winner) and FAIL somewhere
    seen = {}
    for case, r in res.items():
        for k, v in r["got"].items():
            seen.setdefault(k, set()).add(v)
    json.dump({"ok": ok, "cases": res, "seen": {k: sorted(x for x in v if x) for k, v in seen.items()}}, open(outp, "w"), indent=1)
    print("SELFTEST", "PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="*")
    ap.add_argument("--out")
    ap.add_argument("--labels")
    ap.add_argument("--forecasts", action="store_true")
    ap.add_argument("--selftest-standins")
    a = ap.parse_args()
    check_pins()
    P, FC, R = load()
    if a.forecasts:
        for pid in sorted(P):
            x = FC[pid]["799.0"]["forecasts"]
            print(pid, P[pid]["family"], P[pid]["arm"], P[pid]["fmt"], P[pid]["mask"],
                  " ".join(f"{m}={x[m]['cycles_per_op_wall']:.4f}/{x[m].get('W_over_idle', float('nan')):.4f}" for m in MODELS))
        print("pins OK:", {k: v[:12] for k, v in PINS.items()})
        return
    if a.selftest_standins:
        sys.exit(0 if selftest(P, FC, R, a.selftest_standins) else 1)
    if not a.data:
        print("usage: score_e216.py <data.json>... --out <scores.json>")
        sys.exit(10)
    datas = [json.load(open(d)) for d in a.data]
    labels = json.load(open(a.labels)) if a.labels else None
    o = score(datas, P, FC, R, labels)
    o["inputs_sha256"] = {os.path.basename(d): sha(d) for d in a.data}
    if a.out:
        json.dump(o, open(a.out, "w"), indent=1, default=float)
    for k, v in o["rules"].items():
        print(k, v["verdict"], {x: v[x] for x in v if x in ("n", "pass", "need", "decided", "ordered_right")})
    for k, v in o["head_to_head"].items():
        print(k, v["verdict"], f"{v['first_closer']}/{v['second_closer']}/{v['ties']}", "p", v["p"])


if __name__ == "__main__":
    main()
