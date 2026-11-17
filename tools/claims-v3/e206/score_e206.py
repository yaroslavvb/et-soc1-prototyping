#!/usr/bin/env python3
"""E206 (Q198): the frozen scorer. It reads the kit's reduced data (the form below) and the frozen forecast, and refuses to run if the forecast's
bytes changed. Standard library only.

    python3 -I -B tools/claims-v3/e206/score_e206.py DATA.json [--out SCORED.json]
    python3 -I -B tools/claims-v3/e206/score_e206.py --selftest-standins OUT.json   twelve stand-in cases with verdicts stated before the run (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e206/score_e206.py --selftest-e190 OUT.json       E190's committed card-1 bursts (8,192^3) through this scorer's arithmetic

AMENDED BEFORE ANY DATUM (E206.md, Amendments, A1; Q198 lane fix-e206, Mon 16 Nov 2026, before this registration landed; verify-e206's findings
5 and 6): R0 reads EVERY check of C of the day - the smoke's, every point run's (counted or not, kept or set aside) and every tie run's - where
the first version read only the checks of the runs a point's means were made of; S6 reads the HIGHEST counted sample (mhz_max, added to the run
form) where the first version read the mean (a run with no mhz_max, as E190's committed runs, is read by its mean, and the cell says so). The
forecast file, the points, the bands, the thresholds and every other rule are unchanged.

THE DATA (one JSON; the kit's reducer writes it from the session's records):
  {"experiment": "E206", "arms": {"A": ARM, "B": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"checks": [..], "cycles_per_op": {pid: x}}, "points": {pid: {"runs": [RUN, ...]}}, "ties": {"runs": [RUN, ...]}}
  RUN = {"t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (launch >= 0, ok, wall_s >= 0.1 s, the kernel clock
         cycles_max / wall in 590-610 MHz; the calibration launch -1 and the check launch -3 never count),
         "cycles_per_op": the median over the counted launches of the host's cycles_per_op (the kernel's counter: its mean over minions / ops),
         "cycles_gemm": the median over the counted launches of cycles_max / passes (the slowest minion's counter, a GEMM),
         "n_gemm": passes counted, "n_launch_counted": launches counted,
         "p_work_w": the median board W of the 10 Hz samples inside the counted launches, "p_rest_w": the median board W of the last 5 s of the run's
         rest read, "die_start_c": the shires' mean then, "die_c": the highest shires' mean in the work window, "mhz": the mean minion clock of the
         samples inside the counted launches, "mhz_min": the lowest such sample, "mhz_max": the highest such sample (A1), "checks": every check
         of C of the run ("exact" / "approx" / "wrong"),
         "record": {"arm", "type", "minions", "shire_mask"} as the host's SPARSITY records print them, "block": "pass1" / "pass2" / "tie", "n": its
         position in the arm's sequence}
THE MEASURED JOULES of a run: over idle J = (p_work - p_rest) t_gemm; with the card at rest J = p_work t_gemm. A point is the mean of its runs. A run
whose record differs from its point (arm, type, minions or shire mask) is set aside (never counted) and flagged.
THE RULES (E206.md section 7; per point and arm; a point with no run is NO DATA, never a failure):
  R0 the ties: every check of C exact or approx (the smoke and every run: every point run, counted or not, kept or set aside, and every tie
     run, A1); the smoke's cycles an op within 50-250% of F1's point. A FAIL labels every other verdict.
  C1 cycles an op (the counter) inside F1's band.          S1 seconds a GEMM inside F1's band.
  S2 J over idle given the measured seconds within 10% of each model's given() (F1, F2).
  S3 J with the card at rest given the measured seconds and rest within 5% (F1, F2).
  S4 J over idle, the whole forecast (seconds forecast), inside each model's band (F1, F2).
  S6 the clock: every counted sample in 590-610 MHz (mhz_min >= 590 and mhz_max <= 610, A1; a run with no mhz_max is read by its mean mhz, and
     the cell's S6_reading says so).
  A rule's verdict per model and arm: PASS if at least 90% of its scored points pass, FAIL otherwise; TOO FEW (counts only) under 10 scored
  points; NO DATA with none. R0 is one verdict for the day.
THE SUMMARIES (REPORTED, the headline numbers): per model (F1, F2, P0), arm, family, format, kind and regime, the rms and the mean of
  ln(measured / forecast) for cycles an op, seconds, J over idle given the seconds and with the seconds forecast, and J with the card at rest given
  and forecast. THE READINGS (REPORTED): contention, the stride step, the zeros gap, card 1 over aifoundry3, gemmL1x1x1 against gemmc1, the tie's
  drift, the timing simulation and the tensor floor beside the measured cycles.
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
FC_PATH = os.path.join(HERE, "forecast-e206.json")
FORECAST_SHA256 = "d8f3a8b1e3d22f515581aab1a9cc43ca30fbb6e1c61c96d7cc14bf32697bd888"
ARMS = ("A", "B")
MODELS_J = ("F1", "F2")
S2_REL, S3_REL = 0.10, 0.05
VERDICT_SHARE, MIN_SCORED = 0.90, 10
SMOKE_CPO = (0.5, 2.5)
MHZ_BAND = (590.0, 610.0)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def inside(x, band):
    return x is not None and band[0] <= x <= band[1]


def ln_err(meas, fc):
    return math.log(meas / fc) if (meas and fc and meas > 0 and fc > 0) else None


def regime(lines32):
    nl, nf = lines32
    if nl + nf == 0:
        return "L2-resident"
    if nf == 0:
        return "L3-served"
    if nl == 0:
        return "all fresh"
    return "mixed"


def record_ok(run, pt):
    rc = run.get("record")
    if rc is None:
        return True, None
    want = {"arm": pt["arm"], "type": pt["format"], "minions": pt["minions"], "shire_mask": pt["shire_mask"]}
    bad = {k: (rc.get(k), v) for k, v in want.items() if str(rc.get(k)) != str(v)}
    return not bad, bad or None


def cell_stats(runs, pt):
    kept, aside = [], []
    for r in runs:
        ok, bad = record_ok(r, pt)
        if not ok:
            aside.append({"n": r.get("n"), "mismatch": bad})
            continue
        if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None:
            kept.append(r)
    if not kept:
        return None, aside
    jo = [(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in kept]
    jr = [r["p_work_w"] * r["t_gemm_s"] for r in kept]
    st = {"n_runs": len(kept), "t": mean([r["t_gemm_s"] for r in kept]), "cycles_per_op": mean([r.get("cycles_per_op") for r in kept]),
          "cycles_gemm": mean([r.get("cycles_gemm") for r in kept]), "p_work": mean([r["p_work_w"] for r in kept]),
          "p_rest": mean([r["p_rest_w"] for r in kept]), "die_start": mean([r.get("die_start_c") for r in kept]), "die": mean([r.get("die_c") for r in kept]),
          "mhz": mean([r.get("mhz") for r in kept]), "mhz_min": min([r["mhz_min"] for r in kept if r.get("mhz_min") is not None], default=None),
          # A1 (S6 reads the highest sample): a run's mhz_max, or its mean where the run carries no mhz_max (counted in mhz_max_from_mean)
          "mhz_max": max([r["mhz_max"] if r.get("mhz_max") is not None else r["mhz"] for r in kept
                          if r.get("mhz_max") is not None or r.get("mhz") is not None], default=None),
          "mhz_max_from_mean": sum(1 for r in kept if r.get("mhz_max") is None and r.get("mhz") is not None),
          "j_over": mean(jo), "j_rest": mean(jr), "j_over_runs": jo, "j_rest_runs": jr,
          "checks": sorted({c for r in kept for c in r.get("checks", [])})}
    return st, aside


def fe():
    sys.path.insert(0, HERE)
    import forecast_e206 as FE6
    return FE6


def score(data, fc):
    FE6 = fe()
    pts = {p["id"]: p for p in FE6.PTS["points"]}
    out = {"cells": {}, "rules": {}, "summaries": {}, "readings": {}, "set_aside": {}}
    arms = data.get("arms") or {}
    r0 = {"checks": [], "cycles": {}, "by_source": {"smoke": 0, "point_runs": 0, "tie_runs": 0}, "wrong_at": []}

    def r0_add(src, where, checks):
        """A1: every check of C of the day counts in R0 - the smoke's, every point run's (counted or not, kept or set aside), every tie run's."""
        for chk in checks or []:
            r0["checks"].append(chk)
            r0["by_source"][src] += 1
            if chk not in ("exact", "approx"):
                r0["wrong_at"].append({"where": where, "check": chk})
    for arm in ARMS:
        A = arms.get(arm) or {}
        sm = A.get("smoke") or {}
        r0_add("smoke", f"{arm}.smoke", sm.get("checks", []))
        for i, r in enumerate(((A.get("ties") or {}).get("runs")) or []):
            r0_add("tie_runs", f"{arm}.tie.run{r.get('n', i)}", r.get("checks"))
        for pid in sorted((A.get("points") or {})):
            for i, r in enumerate((((A.get("points") or {}).get(pid)) or {}).get("runs") or []):
                r0_add("point_runs", f"{arm}.{pid}.run{r.get('n', i)}", r.get("checks"))
        for pid, cpo in (sm.get("cycles_per_op") or {}).items():
            pt = fc["points"][pid]["F1_speed"]["cycles_per_op"]["point"]
            r0["cycles"][f"{arm}.{pid}"] = {"measured": cpo, "point": pt, "ratio": cpo / pt, "ok": SMOKE_CPO[0] <= cpo / pt <= SMOKE_CPO[1]}
        for pid, fp in fc["points"].items():
            if arm not in fp["arms"]:
                continue
            key = f"{arm}.{pid}"
            st, aside = cell_stats(((A.get("points") or {}).get(pid) or {}).get("runs") or [], pts[pid])
            if aside:
                out["set_aside"][key] = aside
            if st is None:
                out["cells"][key] = {"verdict": "NO DATA", "set_aside": aside}
                continue
            c = fp["arms"][arm]
            sp = fp["F1_speed"]
            rec = {"n_runs": st["n_runs"], "measured": {k: st[k] for k in ("t", "cycles_per_op", "cycles_gemm", "p_work", "p_rest", "die_start", "die",
                                                                             "mhz", "mhz_min", "mhz_max", "j_over", "j_rest")},
                   "family": fp["family"], "format": fp["format"], "kind": fp["kind"], "regime": regime(fp["lines"]["32MB"]), "models": {}}
            # C1, S1 (F1's speed)
            rec["C1"] = ("PASS" if inside(st["cycles_per_op"], sp["cycles_per_op"]["band"]) else "FAIL") if st["cycles_per_op"] else "NO DATA"
            rec["S1"] = "PASS" if inside(st["t"], sp["t_gemm_s"]["band"]) else "FAIL"
            rec["err_speed"] = {"ln_cycles_per_op": ln_err(st["cycles_per_op"], sp["cycles_per_op"]["point"]),
                                "ln_cycles_gemm": ln_err(st["cycles_gemm"], sp["cycles_gemm"]["point"]),
                                "ln_t": ln_err(st["t"], sp["t_gemm_s"]["point"]),
                                "ln_cycles_per_op_P0": ln_err(st["cycles_per_op"], c["P0"]["cycles_per_op"])}
            # F1
            g1 = FE6.given_f1(fc, arm, pid, st["t"], st["p_rest"])
            f1 = c["F1"]
            m1 = {"given": g1, "frozen": {"J_over": f1["J_over"]["point"], "J_rest": f1["J_rest"]["point"], "W_over": f1["W_over"]["point"]},
                  "err": {"j_over_given": st["j_over"] / g1["j_over"] - 1, "j_rest_given": st["j_rest"] / g1["j_rest"] - 1,
                          "ln_j_over_given": ln_err(st["j_over"], g1["j_over"]), "ln_j_rest_given": ln_err(st["j_rest"], g1["j_rest"]),
                          "ln_j_over_forecast": ln_err(st["j_over"], f1["J_over"]["point"]), "ln_j_rest_forecast": ln_err(st["j_rest"], f1["J_rest"]["point"])}}
            m1["S2"] = "PASS" if abs(m1["err"]["j_over_given"]) <= S2_REL else "FAIL"
            m1["S3"] = "PASS" if abs(m1["err"]["j_rest_given"]) <= S3_REL else "FAIL"
            m1["S4"] = "PASS" if inside(st["j_over"], f1["J_over"]["band"]) else "FAIL"
            m1["S4_rest_reported"] = "INSIDE" if inside(st["j_rest"], f1["J_rest"]["band"]) else "OUTSIDE"
            rec["models"]["F1"] = m1
            # F2
            f2 = c["F2"]
            if f2["priced"]:
                T0m = st["die_start"] if st["die_start"] is not None else fc["constants"]["t0_c"]
                g2 = FE6.given_f2(arm, pid, st["t"], T0m, st["p_rest"])
                m2 = {"given": g2, "frozen": {"J_over": f2["J_over"]["point"], "J_rest": f2["J_rest"]["point"]},
                      "err": {"j_over_given": st["j_over"] / g2["j_over"] - 1, "j_rest_given": st["j_rest"] / g2["j_rest"] - 1,
                              "ln_j_over_given": ln_err(st["j_over"], g2["j_over"]), "ln_j_rest_given": ln_err(st["j_rest"], g2["j_rest"]),
                              "ln_j_over_forecast": ln_err(st["j_over"], f2["J_over"]["point"]), "ln_j_rest_forecast": ln_err(st["j_rest"], f2["J_rest"]["point"])}}
                m2["S2"] = "PASS" if abs(m2["err"]["j_over_given"]) <= S2_REL else "FAIL"
                m2["S3"] = "PASS" if abs(m2["err"]["j_rest_given"]) <= S3_REL else "FAIL"
                m2["S4"] = "PASS" if inside(st["j_over"], f2["J_over"]["band"]) else "FAIL"
                m2["S4_rest_reported"] = "INSIDE" if inside(st["j_rest"], f2["J_rest"]["band"]) else "OUTSIDE"
            else:
                m2 = {"S2": "NOT PRICED", "S3": "NOT PRICED", "S4": "NOT PRICED", "why": f2["why"]}
            rec["models"]["F2"] = m2
            # P0 (REPORTED)
            rec["models"]["P0"] = {"err": {"ln_j_over_forecast": ln_err(st["j_over"], c["P0"]["J_over"])}}
            # S6 (A1: the lowest and the highest counted sample; a run with no mhz_max is read by its mean, and the cell says so)
            if st["mhz"] is not None:
                lo = st["mhz_min"] if st["mhz_min"] is not None else st["mhz"]
                hi = st["mhz_max"] if st["mhz_max"] is not None else st["mhz"]
                rec["S6"] = "PASS" if (MHZ_BAND[0] <= lo and hi <= MHZ_BAND[1]) else "FAIL"
                rec["S6_reading"] = ("the lowest and the highest counted sample" if not st["mhz_max_from_mean"] else
                                     f"the lowest counted sample and the highest; {st['mhz_max_from_mean']} run(s) with no mhz_max read by the mean")
            out["cells"][key] = rec
    r0_ok = bool(r0["checks"]) and all(c in ("exact", "approx") for c in r0["checks"]) and all(v["ok"] for v in r0["cycles"].values())
    out["rules"]["R0"] = {"verdict": "PASS" if r0_ok else ("NO DATA" if not r0["checks"] else "FAIL"), "n_checks": len(r0["checks"]),
                          "wrong": sum(1 for c in r0["checks"] if c not in ("exact", "approx")), "by_source": r0["by_source"],
                          "wrong_at": r0["wrong_at"][:60], "cycles": r0["cycles"],
                          "note": "a FAIL labels every other verdict; every check of C of the day is read (A1)"}

    def verdict(v):
        sc = [x for x in v.values() if x in ("PASS", "FAIL")]
        n, k = len(sc), sum(1 for x in sc if x == "PASS")
        if n == 0:
            return {"scored": 0, "pass": 0, "verdict": "NO DATA"}
        if n < MIN_SCORED:
            return {"scored": n, "pass": k, "verdict": "TOO FEW"}
        return {"scored": n, "pass": k, "share": k / n, "verdict": "PASS" if k / n >= VERDICT_SHARE else "FAIL"}
    for arm in ARMS:
        cells = {k: c for k, c in out["cells"].items() if k.startswith(arm + ".") and "measured" in c}
        for rule in ("C1", "S1", "S6"):
            v = {k: c.get(rule) for k, c in cells.items() if c.get(rule)}
            out["rules"][f"{rule}.{arm}"] = dict(verdict(v), cells=v)
        for m in MODELS_J:
            for rule in ("S2", "S3", "S4"):
                v = {k: c["models"][m][rule] for k, c in cells.items()}
                out["rules"][f"{rule}.{m}.{arm}"] = dict(verdict(v), cells=v)
    out["summaries"] = summaries(out["cells"])
    out["readings"] = readings(out["cells"], fc, data)
    out["headline"] = {k: {"t_s": c["measured"]["t"], "cycles_per_op": c["measured"]["cycles_per_op"], "j_over": c["measured"]["j_over"],
                           "j_rest": c["measured"]["j_rest"], "F1_t_s": fc["points"][k.split(".")[1]]["F1_speed"]["t_gemm_s"]["point"],
                           "F1_j_over": c["models"]["F1"]["frozen"]["J_over"], "F1_j_rest": c["models"]["F1"]["frozen"]["J_rest"],
                           "F2_j_over": (c["models"]["F2"].get("frozen") or {}).get("J_over")}
                       for k, c in out["cells"].items() if "measured" in c}
    return out


def rms_bias(v):
    v = [x for x in v if x is not None]
    if not v:
        return None
    return {"n": len(v), "rms": math.sqrt(sum(x * x for x in v) / len(v)), "bias": sum(v) / len(v)}


def summaries(cells):
    keys = {"cycles_per_op": ("F1", "err_speed", "ln_cycles_per_op"), "cycles_per_op_P0": ("P0", "err_speed", "ln_cycles_per_op_P0"),
            "t": ("F1", "err_speed", "ln_t"), "cycles_gemm": ("F1", "err_speed", "ln_cycles_gemm")}
    out = {}
    groups = {"all": lambda c: True}
    for dim in ("family", "format", "kind", "regime"):
        for val in sorted({c[dim] for c in cells.values() if "measured" in c}):
            groups[f"{dim}={val}"] = (lambda d, x: (lambda c: c[d] == x))(dim, val)
    for arm in ARMS:
        for gname, grp in groups.items():
            cs = [c for k, c in cells.items() if k.startswith(arm + ".") and "measured" in c and grp(c)]
            if not cs:
                continue
            rec = {}
            for name, (_, sec, fld) in keys.items():
                rec[name] = rms_bias([c[sec][fld] for c in cs])
            for m in ("F1", "F2"):
                for fld in ("ln_j_over_given", "ln_j_over_forecast", "ln_j_rest_given", "ln_j_rest_forecast"):
                    rec[f"{m}.{fld[3:]}"] = rms_bias([(c["models"][m].get("err") or {}).get(fld) for c in cs])
            rec["P0.j_over_forecast"] = rms_bias([c["models"]["P0"]["err"]["ln_j_over_forecast"] for c in cs])
            out[f"{arm}.{gname}"] = rec
    return out


def readings(cells, fc, data):
    FE6 = fe()
    pts = {p["id"]: p for p in FE6.PTS["points"]}

    def m(arm, pid, q):
        c = cells.get(f"{arm}.{pid}")
        return c["measured"][q] if c and "measured" in c else None

    def find(arm_s, t, kind="random", mask="0xffffffff"):
        for p in pts.values():
            if p["arm"] == arm_s and p["format"] == t and p["kind"] == kind and p["shire_mask"] == mask:
                return p["id"]
        return None
    R = {}
    for arm in ARMS:
        # (a) contention: cycles an op against shires (F1 predicts each subset at its own lines' time, the line costs the full chip's)
        con = {}
        for shape in ("gemmL4x8x4", "gemmL1x1x1"):
            for t in ("fp32", "int8"):
                rows = []
                for mask in ("0x1", "0xf", "0xff", "0x11111111", "0xffff", "0xffffffff"):
                    pid = find(shape, t, mask=mask)
                    if pid and m(arm, pid, "cycles_per_op"):
                        rows.append({"id": pid, "shires": pts[pid]["shires"], "mask": mask, "cycles_per_op": m(arm, pid, "cycles_per_op"),
                                     "F1": fc["points"][pid]["F1_speed"]["cycles_per_op"]["point"]})
                if rows:
                    con[f"{shape}.{t}"] = rows
        # (b) the stride step: 1x16x4 over 1x15x4
        st = {}
        for t in ("fp32", "int8"):
            a, b = find("gemmL1x16x4", t), find("gemmL1x15x4", t)
            if a and b and m(arm, a, "cycles_per_op") and m(arm, b, "cycles_per_op"):
                st[t] = {"ratio_cycles_per_op": m(arm, a, "cycles_per_op") / m(arm, b, "cycles_per_op"), "reference": "E169: +27-30% at its power-of-two step"}
        # (c) the zeros gap: J over idle zeros / random at the same shape and format; seconds likewise
        zg = {}
        for p in pts.values():
            if p["kind"] != "zeros":
                continue
            r = find(p["arm"], p["format"])
            if r and m(arm, p["id"], "j_over") and m(arm, r, "j_over"):
                zg[f"{p['arm']}.{p['format']}"] = {"j_over_ratio": m(arm, p["id"], "j_over") / m(arm, r, "j_over"),
                                                    "t_ratio": m(arm, p["id"], "t") / m(arm, r, "t")}
        # (e) gemmL1x1x1 against gemmc1: the same work through two loop codes
        lc = {}
        for t in ("fp32", "fp16", "int8"):
            a, b = find("gemmL1x1x1", t), find("gemmc1", t)
            if a and b and m(arm, a, "cycles_per_op") and m(arm, b, "cycles_per_op"):
                lc[t] = {"ratio_cycles_per_op": m(arm, a, "cycles_per_op") / m(arm, b, "cycles_per_op")}
        # (h) the timing simulation and the tensor floor beside the measured cycles
        sim = {}
        for pid, fp in fc["points"].items():
            cg, cpo = m(arm, pid, "cycles_gemm"), m(arm, pid, "cycles_per_op")
            steps = fp["reported_columns"]["sim_steps_per_minion_per_gemm"]
            if cg and steps:
                sim[pid] = {"cycles_gemm_over_sim_steps": cg / steps,
                            "cycles_per_op_over_tensor_floor": (cpo / fc["constants"]["tensor_floor_cycles_per_op"][fp["format"]]) if cpo else None}
        # (f) the tie's drift
        ties = ((data.get("arms") or {}).get(arm) or {}).get("ties") or {}
        tr = [{"n": r.get("n"), "t": r.get("t_gemm_s"), "p_work": r.get("p_work_w"), "j_over": (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"]}
              for r in ties.get("runs", []) if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        R[arm] = {"a_contention": con, "b_stride_step": st, "c_zeros_gap": zg, "e_loop_codes": lc, "f_tie_drift": tr, "h_timing_simulation": sim}
    # (d) card 1 over aifoundry3 at every shared point
    cb = {}
    for pid in fc["points"]:
        a, b = cells.get(f"A.{pid}"), cells.get(f"B.{pid}")
        if a and b and "measured" in a and "measured" in b:
            cb[pid] = {"t_ratio": b["measured"]["t"] / a["measured"]["t"], "j_over_ratio": b["measured"]["j_over"] / a["measured"]["j_over"]
                       if a["measured"]["j_over"] else None}
    R["d_card1_over_aifoundry3"] = cb
    return R


# ------------------------------------------------------------------ the self-tests
def run_at(fc, arm, pid, rng, scale_t=1.0, scale_w=1.0, w_over=None, noise=0.005, mhz=600.0, record=None, die_start=None, checks=("approx",),
           mhz_max=None):
    FE6 = fe()
    p = next(x for x in FE6.PTS["points"] if x["id"] == pid)
    fp = fc["points"][pid]
    c = fp["arms"][arm]["F1"]
    t = fp["F1_speed"]["t_gemm_s"]["point"] * scale_t * (1 + rng.uniform(-noise, noise))
    pr = c["P_rest_w"]["point"] * (1 + rng.uniform(-noise, noise))
    W = (c["W_over"]["point"] if w_over is None else w_over) * scale_w * (1 + rng.uniform(-noise, noise))
    cpo = fp["F1_speed"]["cycles_per_op"]["point"] * scale_t * (1 + rng.uniform(-noise, noise))
    rec = record or {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]}
    return {"t_gemm_s": t, "cycles_per_op": cpo, "cycles_gemm": cpo * p["ops_per_minion_per_gemm"] * 1.01, "n_gemm": 100, "n_launch_counted": 11,
            "p_work_w": pr + W, "p_rest_w": pr, "die_start_c": fc["constants"]["t0_c"] if die_start is None else die_start, "die_c": 56.0,
            "mhz": mhz, "mhz_min": mhz - 1.0 if mhz >= 600 else mhz, "mhz_max": mhz + 1.0 if mhz_max is None else mhz_max,
            "checks": list(checks), "record": rec, "block": "pass1"}


CASES = {
    "A": "every point on both arms at F1's point (+-0.5%)",
    "B": "F1's seconds, the watts 25% over F1's point",
    "C": "F1's seconds and rest, the watts at F2's price (J over idle with heat / F1's seconds) where F2 prices the point",
    "D": "every point 1.5 x F1's seconds (and cycles), F1's watts",
    "E": "arm B absent",
    "F": "one smoke check of C wrong",
    "G": "p001's runs on arm A carry another shire mask (a record mismatch)",
    "H": "p002's runs on arm A at 700 MHz (the clock rule)",
    "I": "the stand-in of case A, but every run's die start 10 C over the forecast's (F2's given() reads the measured start)",
    "J": "the stand-in of case A, but one tie run's check of C on arm A wrong (R0 reads every tie run's checks, A1)",
    "K": "the stand-in of case A, but p005's first run on arm A has no counted launch and a wrong check of C (R0 reads it, A1; the point is "
         "its other run)",
    "L": "the stand-in of case A, but p003's runs on arm A at a mean of 609 MHz with a counted sample at 700 MHz (S6 reads the highest "
         "sample, A1)",
}


def standin(fc, case, seed=206):
    rng = random.Random(f"{seed}|{case}")
    data = {"experiment": "E206", "standin": case, "arms": {}}
    for arm in ARMS:
        if case == "E" and arm == "B":
            continue
        A = {"smoke": {"checks": ["approx", "approx", "exact"],
                       "cycles_per_op": {pid: fc["points"][pid]["F1_speed"]["cycles_per_op"]["point"] * 1.01 for pid in ("p001", "p046", "p021")}},
             "points": {}, "ties": {"runs": []}}
        if case == "F" and arm == "A":
            A["smoke"]["checks"][0] = "wrong"
        for pid, fp in fc["points"].items():
            if arm not in fp["arms"]:
                continue
            kw = {}
            if case == "B":
                kw["scale_w"] = 1.25
            if case == "C" and fp["arms"][arm]["F2"]["priced"]:
                kw["w_over"] = fp["arms"][arm]["F2"]["J_over"]["point"] / fp["F1_speed"]["t_gemm_s"]["point"]
            if case == "D":
                kw["scale_t"] = 1.5
            if case == "G" and arm == "A" and pid == "p001":
                FE6 = fe()
                p = next(x for x in FE6.PTS["points"] if x["id"] == pid)
                kw["record"] = {"arm": p["arm"], "type": p["format"], "minions": 32, "shire_mask": "0x1"}
            if case == "H" and arm == "A" and pid == "p002":
                kw["mhz"] = 700.0
            if case == "I":
                kw["die_start"] = fc["constants"]["t0_c"] + 10.0
            if case == "L" and arm == "A" and pid == "p003":
                kw["mhz"], kw["mhz_max"] = 609.0, 700.0
            A["points"][pid] = {"runs": [run_at(fc, arm, pid, rng, noise=0.0 if case == "C" else 0.005, **kw) for _ in range(2)]}
            if case == "K" and arm == "A" and pid == "p005":
                A["points"][pid]["runs"][0].update(t_gemm_s=None, checks=["wrong"])
        for _ in range(3):
            A["ties"]["runs"].append(run_at(fc, arm, "p001", rng))
        if case == "J" and arm == "A":
            A["ties"]["runs"][1]["checks"] = ["wrong"]
        data["arms"][arm] = A
    return data


def expected(fc, case):
    """the verdicts stated before the run, derived from the frozen forecast by arithmetic independent of score()"""
    exp = {}
    on = {arm: [pid for pid, fp in fc["points"].items() if arm in fp["arms"]] for arm in ARMS}
    priced = {arm: [pid for pid in on[arm] if fc["points"][pid]["arms"][arm]["F2"]["priced"]] for arm in ARMS}
    if case == "A":
        exp.update({"R0": "PASS", **{f"{r}.{a}": "PASS" for r in ("C1", "S1", "S6") for a in ARMS},
                    **{f"{r}.F1.{a}": "PASS" for r in ("S2", "S3", "S4") for a in ARMS}})
    if case == "B":
        exp.update({"R0": "PASS", "S1.A": "PASS", "S1.B": "PASS", "S2.F1.A": "FAIL", "S2.F1.B": "FAIL"})
        exp["cells"] = {f"{a}.{pid}.F1.S2": "FAIL" for a in ARMS for pid in on[a]}
        # S3 per point: |0.25 W / (P_rest + W)| > 5%, from the frozen point (the noise is +-0.5%: a point within 1% of the threshold is not asserted)
        for a in ARMS:
            for pid in on[a]:
                c = fc["points"][pid]["arms"][a]["F1"]
                e = 0.25 * c["W_over"]["point"] / (c["P_rest_w"]["point"] + c["W_over"]["point"])
                if abs(e - S3_REL) > 0.01:
                    exp["cells"][f"{a}.{pid}.F1.S3"] = "FAIL" if e > S3_REL else "PASS"
    if case == "C":
        exp.update({"R0": "PASS", "S2.F2.A": "PASS", "S2.F2.B": "PASS", "S3.F2.A": "PASS", "S3.F2.B": "PASS"})
        exp["cells"] = {}
        for a in ARMS:
            for pid in on[a]:
                fp = fc["points"][pid]
                c = fp["arms"][a]
                if not c["F2"]["priced"]:
                    exp["cells"][f"{a}.{pid}.F2.S2"] = "NOT PRICED"
                    continue
                exp["cells"][f"{a}.{pid}.F2.S2"] = "PASS"
                e = c["F2"]["J_over"]["point"] / (c["F1"]["W_over"]["point"] * fp["F1_speed"]["t_gemm_s"]["point"]) - 1
                if abs(abs(e) - S2_REL) > 0.005:
                    exp["cells"][f"{a}.{pid}.F1.S2"] = "FAIL" if abs(e) > S2_REL else "PASS"
        exp["F2_not_priced_cells"] = sum(1 for a in ARMS for pid in on[a] if pid not in priced[a])
    if case == "D":
        exp.update({"R0": "PASS"})
        exp["cells"] = {}
        for a in ARMS:
            for pid in on[a]:
                sp = fc["points"][pid]["F1_speed"]
                x, (lo, hi) = 1.5 * sp["t_gemm_s"]["point"], sp["t_gemm_s"]["band"]
                if abs(x / hi - 1) > 0.01:
                    exp["cells"][f"{a}.{pid}.S1"] = "PASS" if lo <= x <= hi else "FAIL"
    if case == "E":
        exp.update({"R0": "PASS", "S1.A": "PASS", "S1.B": "NO DATA", "S2.F1.B": "NO DATA", "C1.B": "NO DATA", "B_cells": "NO DATA"})
    if case == "F":
        exp.update({"R0": "FAIL", "S1.A": "PASS"})
    if case == "G":
        exp.update({"R0": "PASS", "S1.A": "PASS"})
        exp["cells"] = {"A.p001.verdict": "NO DATA"}
        exp["set_aside"] = ["A.p001"]
    if case == "H":
        exp.update({"R0": "PASS", "S6.A": "PASS"})
        exp["cells"] = {"A.p002.S6": "FAIL", "A.p001.S6": "PASS"}
    if case == "I":
        exp.update({"R0": "PASS", "S2.F1.A": "PASS", "S1.A": "PASS"})
        exp["F2_given_moves"] = True
    if case == "J":      # A1: a wrong check in a tie run fails R0 (the first version read no tie run's checks)
        exp.update({"R0": "FAIL", "S1.A": "PASS", "S1.B": "PASS"})
    if case == "K":      # A1: a wrong check in a run with no counted launch fails R0; the point is its other run
        exp.update({"R0": "FAIL", "S1.A": "PASS"})
        exp["cells"] = {"A.p005.n_runs": 1, "A.p005.S1": "PASS"}
    if case == "L":      # A1: S6 reads the highest counted sample, so a 700 MHz sample fails p003 although the mean is 609 MHz
        exp.update({"R0": "PASS", "S6.A": "PASS", "S6.B": "PASS"})
        exp["cells"] = {"A.p003.S6": "FAIL", "A.p001.S6": "PASS", "A.p002.S6": "PASS", "B.p003.S6": "PASS"}
    return exp


def check_case(sc, fc, case, exp, data):
    got, bad = {}, {}
    for k, e in exp.items():
        if k in ("cells", "set_aside", "F2_not_priced_cells", "F2_given_moves", "B_cells"):
            continue
        g = sc["rules"][k]["verdict"]
        got[k] = g
        if g != e:
            bad[k] = (g, e)
    for k, e in (exp.get("cells") or {}).items():
        parts = k.split(".")
        cell = sc["cells"].get(f"{parts[0]}.{parts[1]}", {})
        if parts[2] == "verdict":
            g = cell.get("verdict")
        elif parts[2] in ("F1", "F2"):
            g = (cell.get("models") or {}).get(parts[2], {}).get(parts[3])
        else:
            g = cell.get(parts[2])
        if g != e:
            bad[k] = (g, e)
    if "B_cells" in exp:
        g = "NO DATA" if all(c.get("verdict") == "NO DATA" for k, c in sc["cells"].items() if k.startswith("B.")) else "DATA"
        got["B_cells"] = g
        if g != exp["B_cells"]:
            bad["B_cells"] = (g, exp["B_cells"])
    if "set_aside" in exp:
        g = sorted(sc["set_aside"])
        if g != sorted(exp["set_aside"]):
            bad["set_aside"] = (g, exp["set_aside"])
    if "F2_not_priced_cells" in exp:
        g = sum(1 for c in sc["cells"].values() if (c.get("models") or {}).get("F2", {}).get("S2") == "NOT PRICED")
        if g != exp["F2_not_priced_cells"]:
            bad["F2_not_priced_cells"] = (g, exp["F2_not_priced_cells"])
    if exp.get("F2_given_moves"):
        # F2's given() reads the measured start die: with it 10 C over the forecast's, the given J over idle moves off the frozen point
        c = sc["cells"]["A.p001"]["models"]["F2"]
        moved = abs(c["given"]["j_over"] / c["frozen"]["J_over"] - 1) > 1e-6
        if not moved:
            bad["F2_given_moves"] = (False, True)
    n_cells_asserted = len(exp.get("cells") or {})
    return got, bad, n_cells_asserted


def selftest_standins(fc, out_path):
    res, ok = {}, True
    for case, what in CASES.items():
        data = standin(fc, case)
        sc = score(data, fc)
        exp = expected(fc, case)
        got, bad, n = check_case(sc, fc, case, exp, data)
        rule_summary = {k: v["verdict"] for k, v in sc["rules"].items()}
        res[case] = {"what": what, "expected_rules": {k: v for k, v in exp.items() if k not in ("cells",)}, "cells_asserted": n,
                     "got_rules": rule_summary, "mismatches": {k: list(v) for k, v in bad.items()}, "pass": not bad}
        ok = ok and not bad
    rep = {"selftest": "standins", "interpreter": sys.executable, "version": sys.version.split()[0], "cases": res, "verdict": "PASS" if ok else "FAIL",
           "how": "each case's verdicts are stated before the run by expected(), arithmetic on the frozen forecast independent of score(); cases A, C, "
                  "E, G, H, I and L must give PASS verdicts where stated, B, D, F, G, H, J, K and L FAIL ones where stated (per rule and per point); "
                  "J, K and L were added before any datum (E206.md A1)"}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-standins ({sys.executable} {sys.version.split()[0]}):")
    for c, r in res.items():
        print(f"  {c} ({r['what']}): {'PASS' if r['pass'] else 'FAIL ' + json.dumps(r['mismatches'])[:400]}; rules asserted "
              f"{len([k for k in r['expected_rules'] if not k.startswith(('F2_', 'set_', 'B_'))])}, points asserted {r['cells_asserted']}")
    print(rep["verdict"])
    return ok


def selftest_e190(fc, out_path):
    """E190's committed card-1 burst runs (docs/reports/data/2026-11-13-e190-large-gemm/data-e190.json, arm B: the same binary, the same 8,192^3
    shapes as E206's p055, p056 and p057 on arm B) in this scorer's RUN form: the scorer's measured seconds and joules must equal E190's committed
    scores (scores-e190.json cells B.<fmt>.burst measured) to 1e-12 relative. A check of the measured-side arithmetic on real records; the E206
    verdicts it prints for those three points are not E206's (E190's data are not E206's, and E206's forecasts are not blind to them)."""
    base = os.path.join(REPO, "docs/reports/data/2026-11-13-e190-large-gemm")
    d = json.load(open(os.path.join(base, "data-e190.json")))
    s = json.load(open(os.path.join(base, "scores-e190.json")))
    B = d["arms"]["B"]
    pid_of = {"fp32": "p055", "fp16": "p056", "int8": "p057"}
    FE6 = fe()
    pts = {p["id"]: p for p in FE6.PTS["points"]}
    data = {"experiment": "E206-selftest-e190", "arms": {"B": {"smoke": {"checks": B["smoke"]["checks"],
                                                                         "cycles_per_op": {pid_of[t]: v for t, v in B["smoke"]["cycles_per_op"].items()}},
                                                               "points": {}}}}
    for t, pid in pid_of.items():
        runs = []
        for r in B["cells"][f"{t}.burst"]["runs"]:
            p = pts[pid]
            runs.append({"t_gemm_s": r["t_gemm_s"], "cycles_per_op": B["smoke"]["cycles_per_op"][t], "cycles_gemm": None, "n_gemm": r["n_gemm"],
                         "n_launch_counted": r["n_launch_counted"], "p_work_w": r["p_work_w"], "p_rest_w": r["p_rest_w"], "die_start_c": r["die_start_c"],
                         "die_c": r["die_c"], "mhz": r["mhz"], "mhz_min": r["mhz_min"], "checks": r.get("checks", []),
                         "record": {"arm": p["arm"], "type": t, "minions": 1024, "shire_mask": "0xffffffff"}, "block": "pass1"})
        data["arms"]["B"]["points"][pid] = {"runs": runs}
    sc = score(data, fc)
    res, ok = {}, True
    for t, pid in pid_of.items():
        mine = sc["cells"][f"B.{pid}"]["measured"]
        theirs = s["cells"][f"B.{t}.burst"]["measured"]
        errs = {q: abs(mine[q] / theirs[w] - 1) for q, w in (("t", "t"), ("j_over", "j_over"), ("j_rest", "j_rest"), ("p_work", "p_work"), ("p_rest", "p_rest"))}
        good = all(e <= 1e-12 for e in errs.values())
        res[t] = {"pid": pid, "rel_err_vs_e190_scores": errs, "pass": good, "measured": {k: mine[k] for k in ("t", "j_over", "j_rest")},
                  "e206_F1_frozen": {"t": fc["points"][pid]["F1_speed"]["t_gemm_s"]["point"], "j_over": fc["points"][pid]["arms"]["B"]["F1"]["J_over"]["point"]},
                  "e206_rules_printed_not_e206": {k: sc["cells"][f"B.{pid}"].get(k) for k in ("C1", "S1")}}
        ok = ok and good
    rep = {"selftest": "e190", "interpreter": sys.executable, "version": sys.version.split()[0], "formats": res, "verdict": "PASS" if ok else "FAIL",
           "source_sha256": {"data-e190.json": sha(os.path.join(base, "data-e190.json")), "scores-e190.json": sha(os.path.join(base, "scores-e190.json"))}}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-e190 ({sys.executable} {sys.version.split()[0]}): " + "; ".join(
        f"{t} ({r['pid']}): worst relative difference from E190's committed scores {max(r['rel_err_vs_e190_scores'].values()):.1e}" for t, r in res.items()))
    print(rep["verdict"])
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins")
    ap.add_argument("--selftest-e190")
    a = ap.parse_args()
    got = sha(FC_PATH)
    if FORECAST_SHA256 != "FROZEN-AT-REGISTRATION" and got != FORECAST_SHA256:
        print(f"REFUSED: forecast-e206.json sha256 {got} is not the registered {FORECAST_SHA256}")
        sys.exit(4)
    fc = json.load(open(FC_PATH))
    if a.selftest_standins:
        sys.exit(0 if selftest_standins(fc, a.selftest_standins) else 1)
    if a.selftest_e190:
        sys.exit(0 if selftest_e190(fc, a.selftest_e190) else 1)
    data = json.load(open(a.data))
    sc = score(data, fc)
    sc["forecast_sha256"] = got
    if a.out:
        json.dump(sc, open(a.out, "w"), indent=1, sort_keys=True)
    for k, v in sc["rules"].items():
        print(k, v["verdict"], f"{v.get('pass', '')}/{v.get('scored', '')}" if "scored" in v else "")
    for k in sorted(sc["summaries"]):
        if k.endswith(".all"):
            v = sc["summaries"][k]
            print(k, "; ".join(f"{q} rms {x['rms']:.3f} bias {x['bias']:+.3f} (n {x['n']})" for q, x in v.items() if x))


if __name__ == "__main__":
    main()
