#!/usr/bin/env python3
"""E185 (M11's session 3), dated amendment A1 (E185.md.dated-note-A1.md, before any E185 datum): every figure A1 states, computed from
committed files only, desk only (the Intel). Nothing here opens a device, a box or the network. Nothing is fitted except the
re-derivation of the frozen gains from the rows the train stage itself committed. Every input's sha256 is written into the output.

  gains   the frozen gains re-derived from arms-e185-train.json's own rows, on both readings: G = sum(R P) / sum(P^2) over the 11
          training holds (P = P_F for arm B, P_Rl1 for arm Rl); one-pass from `holds`, two-pass from `two_pass` > `holds` (the e181
          stage of arms_e185.py re-derives the one-pass gains only)
  e181    E185's rules (E185.md section 6: RF, BF, RB and BEST at tau = sigma_c / sqrt(n)) read on E181's five held-out misses, on
          the two-pass reading (A10's) and on the one-pass reading (stated at 20:03 PST): a stand-in only, post hoc, deciding nothing
  cool    E185-C's statistic per arm, d = (the cool-down window's miss) - (the plateau's miss), on the three committed cool-down windows
          (E144's H_H, in-sample for B and Rl; E181's H_E and L1, held out), both readings; and the part of d_B and d_Rl that is each
          arm's own scaling at E185's frozen forecasts, d_arm - d_F when R follows the frozen chain exactly
  hm_lg   M11's HM-LG at k = 2 as design_e185.simulate_lg reads it (E181's two-pass points fixed; E185's simulated at sigma_c), with
          E185 counted over its six holds (the registration's figure) and over the four M11's decision code counts (score_m11.NAMES_A3:
          H_E, L1, S and L2)
  bykind  E185-BEST when each hold's R is P_F plus one of the frozen chain's committed misses on the same item (two-pass; training
          and E181) plus normal(0, sigma_c / 2): a planning scenario, post hoc in its inputs, deciding nothing
  smoke   M6's residue at R0's window by A8's method (residue_a8.py's filter, reader and window, unchanged) for E185's planned smoke:
          E181's committed smoke pass cut at its marks and laid in E185's order (H_E, L1, L2, H_E2 = H_E again, S, S2 = S again; Z
          left out; the rests to within a second; the stop tests E181's, since E185's sixth opens no launch), then E181's committed
          R0; beside it the same code on E176's trace unspliced (A8's own E181 prediction) and on E181's own, as checks
  timing  the measured pass's timeline from run_e185.py's DESIGNS (where the two int8.neg_ones holds sit)

    /usr/bin/python3 -B tools/claims-v3/e185/a1_e185.py <out.json> [<out.txt>]
Run from the lab clone's top. Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import ast  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M11 = os.path.join(TREE, "tools", "claims-v3", "m11")
sys.path.insert(0, HERE)
sys.path.insert(0, M11)
import design_e185 as DE  # noqa: E402  (98fe28b7, unchanged; it imports score_m11, which checks M11's lists on import)
import residue_a8 as R8  # noqa: E402  (80b92990, unchanged: M6's filter, the telemetry reader, the marks)

V1, np = DE.V1, DE.np
SIGMA_C = DE.SIGMA_C
E185D = "tools/claims-v3/e185"
INPUTS = [E185D + "/arms-e185-train.json", E185D + "/arms-e185-e181.json", E185D + "/design-e185.json", E185D + "/run_e185.py",
          "tools/claims-v3/m11/residue-a8.json", R8.M6]
E181D = "docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3"
SMOKE181, MEAS181 = E181D + "/aifoundry3/e181-smoke/p18101", E181D + "/aifoundry3/e181/p18120"
for rel in (SMOKE181, MEAS181, R8.SESSIONS[3][1], R8.SESSIONS[3][2]):
    INPUTS += [rel + "/telemetry.jsonl.gz", rel + "/marks.jsonl"]
OUT = {}
TXT = []


def P(s=""):
    TXT.append(s)
    print(s)


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(TREE, rel), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def r4(x):
    return None if x is None else round(float(x), 4)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


# ------------------------------------------------------------------------------------------------ gains
def gains(tr):
    out = {}
    for lab, rows, frozen in (("one_pass", tr["holds"], tr["gains"]), ("two_pass", tr["two_pass"]["holds"], tr["two_pass"]["gains"])):
        sb = sum(h["R_C"] * h["P_F_C"] for s in rows.values() for h in s.values())
        qb = sum(h["P_F_C"] ** 2 for s in rows.values() for h in s.values())
        sr = sum(h["R_C"] * h["P_Rl1_C"] for s in rows.values() for h in s.values())
        qr = sum(h["P_Rl1_C"] ** 2 for s in rows.values() for h in s.values())
        n = sum(len(s) for s in rows.values())
        gb, gr = sb / qb, sr / qr
        # the rows are committed to 4 decimals, so the re-derivation is checked as arms_e185.py's stage e181 checks it (2e-4)
        out[lab] = {"n_holds": n, "G_B": gb, "G_Rl": gr, "frozen_G_B": frozen["G_B"], "frozen_G_Rl": frozen["G_Rl"],
                    "abs_diff": [abs(gb - frozen["G_B"]), abs(gr - frozen["G_Rl"])],
                    "within_2e-4": abs(gb - frozen["G_B"]) <= 2e-4 and abs(gr - frozen["G_Rl"]) <= 2e-4}
    return out


# ------------------------------------------------------------------------------------------------ E185's rules on E181 (a stand-in)
def e181_rules(e1):
    out = {}
    for lab, ms in (("two_pass (A10's reading)", e1["two_pass"]["held_out"]["misses"]["E181"]),
                    ("one_pass (the reading stated at 20:03 PST)", e1["held_out"]["misses"]["E181"])):
        names = sorted(ms)
        e = {a: [ms[nm][f"e_{a}_C"] for nm in names] for a in ("F", "B", "Rl")}
        tau = SIGMA_C / math.sqrt(len(names))
        v = {"holds": names, "tau_C": r4(tau), "rms_C": {a: r4(rms(x)) for a, x in e.items()}}
        for k, (x, y) in (("E185-RF", ("Rl", "F")), ("E185-BF", ("B", "F")), ("E185-RB", ("Rl", "B"))):
            verdict, d = DE.rule_pair(e[x], e[y], tau)
            v[k] = {"verdict": verdict, "D_C": r4(d)}
        b, _ = DE.rule_best(e, tau)
        v["E185-BEST"] = b
        out[lab] = v
    one, two = out["one_pass (the reading stated at 20:03 PST)"], out["two_pass (A10's reading)"]
    out["B_rms_change_pct"] = r4(100.0 * (two["rms_C"]["B"] - one["rms_C"]["B"]) / one["rms_C"]["B"])
    return out


# ------------------------------------------------------------------------------------------------ E185-C per arm
def cool(tr, e1, de):
    out = {}
    for lab, trh, e1h, G in (("two_pass", tr["two_pass"]["holds"], e1["two_pass"]["holds"], tr["two_pass"]["gains"]),
                             ("one_pass", tr["holds"], e1["holds"], tr["gains"])):
        rows = []
        for src, hs in (("E144 (training: in-sample for B and Rl)", trh["E144"]), ("E181 (held out)", e1h["E181"])):
            for nm, h in sorted(hs.items()):
                if not h.get("cool_window_s"):
                    continue
                eF, eB, eR = h["R_C"] - h["P_F_C"], h["R_C"] - G["G_B"] * h["P_F_C"], h["R_C"] - G["G_Rl"] * h["P_Rl1_C"]
                cF = h["cool_R_C"] - h["cool_P_F_C"]
                cB = h["cool_R_C"] - G["G_B"] * h["cool_P_F_C"]
                cR = h["cool_R_C"] - G["G_Rl"] * h["cool_P_Rl1_C"]
                rows.append({"session": src, "hold": nm, "item": h["item"], "d_F_C": r4(cF - eF), "d_B_C": r4(cB - eB), "d_Rl_C": r4(cR - eR)})
        st = {}
        for a in ("F", "B", "Rl"):
            v = [x[f"d_{a}_C"] for x in rows]
            m = sum(v) / len(v)
            st[a] = {"mean_C": r4(m), "sd_C": r4(math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)))}
        out[lab] = {"windows": rows, "by_arm": st}
    # each arm's own scaling in d at E185's frozen forecasts (50.8 C, two-pass constants): if R follows the frozen chain exactly
    # (d_F = 0), then d_B = (G_B - 1)(P_F - cool_P_F) and d_Rl = (P_Rl - P_F) - (cool_P_Rl - cool_P_F)
    plan = []
    for h in de["plans"]["50.8"]["holds"]:
        if h.get("cool_P_F_C") is None:
            continue
        plan.append({"hold": h["hold"], "item": h["item"], "d_B_less_d_F_C": r4((h["P_B_C"] - h["P_F_C"]) - (h["cool_P_B_C"] - h["cool_P_F_C"])),
                     "d_Rl_less_d_F_C": r4((h["P_Rl_C"] - h["P_F_C"]) - (h["cool_P_Rl_C"] - h["cool_P_F_C"]))})
    out["own_scaling_at_E185_forecasts"] = plan
    rb = [x["d_B_less_d_F_C"] for x in plan]
    rr = [x["d_Rl_less_d_F_C"] for x in plan]
    out["own_scaling_summary"] = {
        "B": {"mean_C": r4(sum(rb) / len(rb)), "sd_C": r4(math.sqrt(sum((x - sum(rb) / len(rb)) ** 2 for x in rb) / (len(rb) - 1)))},
        "Rl": {"mean_C": r4(sum(rr) / len(rr)), "sd_C": r4(math.sqrt(sum((x - sum(rr) / len(rr)) ** 2 for x in rr) / (len(rr) - 1)))}}
    # what E185-C reads on each arm with R exactly the frozen chain's plus normal(0, s) on each d, by the registered rule
    rng = np.random.default_rng(1851)
    sim = {}
    for s_lab, s in (("sigma_c/2", SIGMA_C / 2), ("sigma_c", SIGMA_C)):
        for arm, off in (("F", [0.0] * len(plan)), ("B", rb), ("Rl", rr)):
            cnt = {}
            for _ in range(DE.DRAWS):
                v, _, _ = DE.rule_cool([o + float(rng.normal(0.0, s)) for o in off])
                cnt[v] = cnt.get(v, 0) + 1
            sim[f"{arm} | the chain's shape exact | {s_lab}"] = {k: round(100.0 * c / DE.DRAWS, 1) for k, c in sorted(cnt.items())}
    out["reads_when_the_shape_is_exact"] = sim
    return out


# ------------------------------------------------------------------------------------------------ HM-LG at k = 2
def hm_lg(de, e1):
    fc = de["plans"]["50.8"]["holds"]
    PF = np.array([h["P_F_C"] for h in fc])
    truths = {"none (the chain right)": PF, "arm B's gain": np.array([h["P_B_C"] for h in fc]),
              "the rail chain (arm Rl)": np.array([h["P_Rl_C"] for h in fc]), "a level of +0.27 C": PF + 0.27}
    e181_pts = [(h["P_F_C"], h["e_F_C"]) for h in e1["two_pass"]["held_out"]["misses"]["E181"].values()]
    keep = [i for i, h in enumerate(fc) if h["hold"] in V1.NAMES_A3]
    out = {"E185_holds_counted": {"six (the registration's figure)": [h["hold"] for h in fc],
                                  "four (M11's decision code: score_m11.NAMES_A3)": [fc[i]["hold"] for i in keep]}, "cells": {}}
    rng = np.random.default_rng(1852)
    for lab, Pt in truths.items():
        cnt6, cnt4 = {}, {}
        for _ in range(5000):
            R = Pt + rng.normal(0.0, SIGMA_C, len(PF))
            for cnt, idx in ((cnt6, range(len(PF))), (cnt4, keep)):
                g = {"E181": e181_pts, "E185": [(float(PF[i]), float(R[i] - PF[i])) for i in idx]}
                v = V1.DPG.lg_test(g, min_tiles=V1.D.MIN_HOLDS, min_span_w=V1.D.MIN_SPAN_C, min_df=V1.D.MIN_DF)["verdict"]
                cnt[v] = cnt.get(v, 0) + 1
        out["cells"][lab] = {"six": {k: round(100.0 * c / 5000, 1) for k, c in sorted(cnt6.items())},
                             "four": {k: round(100.0 * c / 5000, 1) for k, c in sorted(cnt4.items())}}
    return out


# ------------------------------------------------------------------------------------------------ BEST with the noise by item
def bykind(tr, e1, de):
    fc = de["plans"]["50.8"]["holds"]
    by = {}
    for src, rows in (("train", tr["two_pass"]["holds"]), ("E181", e1["two_pass"]["holds"])):
        for sid, hs in rows.items():
            for nm, h in hs.items():
                if h["item"] in DE.ITEM.values():
                    by.setdefault(h["item"], []).append({"session": sid, "hold": nm, "e_F_C": r4(h["R_C"] - h["P_F_C"])})
    PF = np.array([h["P_F_C"] for h in fc])
    PB = np.array([h["P_B_C"] for h in fc])
    PR = np.array([h["P_Rl_C"] for h in fc])
    tau = SIGMA_C / math.sqrt(len(fc))
    rng = np.random.default_rng(1853)
    cnt = {}
    for _ in range(DE.DRAWS):
        R = np.array([h["P_F_C"] + by[h["item"]][int(rng.integers(0, len(by[h["item"]])))]["e_F_C"] for h in fc]) + \
            rng.normal(0.0, SIGMA_C / 2, len(fc))
        b, _ = DE.rule_best({"F": list(R - PF), "B": list(R - PB), "Rl": list(R - PR)}, tau)
        cnt[b] = cnt.get(b, 0) + 1
    return {"misses_by_item": by, "BEST_pct": {k: round(100.0 * c / DE.DRAWS, 1) for k, c in sorted(cnt.items())}, "tau_C": r4(tau)}


# ------------------------------------------------------------------------------------------------ the smoke's residue (A8's method)
def m6():
    j = json.load(open(os.path.join(TREE, R8.M6)))["heat"]
    return {"tau_s": j["step_response"]["tau_s"], "weights": j["step_response"]["weights"],
            "gain": j["steady_c_per_board_w"]["aifoundry3"]["value"]}


def segs(smoke):
    a = R8.tel(smoke)
    mk = R8.marks(smoke)
    hs = {m["name"]: m["t_start_ms"] / 1000.0 for m in mk if m.get("kind") == "hold"}
    rs = {m["name"]: m["t_start_ms"] / 1000.0 for m in mk if m.get("kind") == "rest"}
    end = a[-1][0] + 1e-6
    return a, {"pre": (a[0][0], hs["H_E"]), "H_E": (hs["H_E"], hs["Z"]), "Z": (hs["Z"], hs["L1"]), "L1": (hs["L1"], hs["S"]),
               "S": (hs["S"], hs["L2"]), "L2": (hs["L2"], rs["T0"]), "tail": (rs["T0"], end)}


def splice(a, sg, order):
    out, cur = [], a[0][0]
    for k in order:
        lo, hi = sg[k]
        out += [(cur + (t - lo), w, m) for t, w, m in a if lo <= t < hi]
        cur += hi - lo
    return out, cur - sg["tail"][1]          # the shift the measured pass takes (the gap between the passes kept)


def predict(sm, meas_rel, shift, M):
    """run_session's arithmetic (residue_a8.py, unchanged in substance) on a given smoke list and the measured pass shifted by `shift`"""
    b = [(t + shift, w, m) for t, w, m in R8.tel(meas_rel)]
    t_first = sm[0][0]
    f0 = [r for r in sm if r[0] < t_first + R8.F0_S]
    F0 = sum(r[2] for r in f0 if r[2] is not None) / sum(1 for r in f0 if r[2] is not None)
    P0 = sum(r[1] for r in f0) / len(f0)
    r0 = [m for m in R8.marks(meas_rel) if m.get("kind") == "rest" and m.get("name") == "R0"][0]
    t0r, t1r = r0["t_start_ms"] / 1000.0 + shift, r0["t_end_ms"] / 1000.0 + shift
    allp = [r for r in sorted(sm + b, key=lambda r: r[0]) if r[0] < t1r]
    f = R8.M6Filter(M["tau_s"], M["weights"], M["gain"])
    pred = [(allp[0][0], 0.0)]
    for (tp, Pp, _), (t, Pw, _) in zip(allp, allp[1:]):
        f.step(t - tp, Pp - P0, Pw - P0)
        pred.append((t, f.total()))
    lo, hi = t0r + 300.0 - R8.WINDOW_S, t0r + 300.0
    pres, _ = R8.window_mean(pred, lo, hi)
    mres, n = R8.window_mean([(t, m) for t, _, m in allp], lo, hi)
    # the smoke pass's own part: its excess alone, 0 from its last sample (run_session_smoke_only's arithmetic)
    g = R8.M6Filter(M["tau_s"], M["weights"], M["gain"])
    pts = sorted([(r[0], r[1] - P0) for r in sm] + [(r[0], 0.0) for r in b if r[0] < t1r])
    vals = []
    for (tp, up), (t, u) in zip(pts, pts[1:]):
        g.step(t - tp, up, u)
        if t1r - R8.WINDOW_S <= t < t1r:
            vals.append(g.total())
    return {"predicted_C": pres, "smoke_pass_part_C": sum(vals) / len(vals), "measured_C": None if mres is None else mres - F0,
            "F0_C": F0, "P0_W": P0, "smoke_span_s": round(sm[-1][0] - t_first, 2), "R0_length_s": round(t1r - t0r, 1)}


def smoke(a8):
    R8.TOP = TREE
    M = m6()
    out = {"M6": M}
    e176 = R8.run_session("E176", R8.SESSIONS[3][1], R8.SESSIONS[3][2], M, (300.0,))
    out["E176 (A8's planned smoke, unspliced; the check of A8's 0.414)"] = {"predicted_C": e176["by_L"]["300"]["predicted_C"],
                                                                          "smoke_pass_part_C": R8.run_session_smoke_only(R8.SESSIONS[3], M)}
    a, sg = segs(SMOKE181)
    own, sh0 = splice(a, sg, ["pre", "H_E", "Z", "L1", "S", "L2", "tail"])
    out["E181 (its own smoke, cut and laid back in its own order: the splice's check)"] = predict(own, MEAS181, sh0, M)
    direct = R8.run_session("E181", SMOKE181, MEAS181, M, (300.0,))
    out["E181 by residue_a8.run_session, unspliced"] = {"predicted_C": direct["by_L"]["300"]["predicted_C"],
                                                        "measured_C": direct["by_L"]["300"].get("measured_C")}
    sp, sh = splice(a, sg, ["pre", "H_E", "L1", "L2", "H_E", "S", "S", "tail"])
    out["E185 (E181's smoke laid in E185's order)"] = e185 = predict(sp, MEAS181, sh, M)
    e185.pop("measured_C")                   # the window's samples there are E181's R0: no E185 datum exists, so none is printed
    e185["what"] = "a prediction only: E181's committed smoke segments in E185's order, then E181's committed R0; nothing of E185 measured"
    e181 = out["E181 (its own smoke, cut and laid back in its own order: the splice's check)"]
    d = e185["smoke_pass_part_C"] - e181["smoke_pass_part_C"]
    pred = a8["E181"]["predicted_residue_C"] + d
    mean, sd = a8["misses_300s"]["mean_C"], a8["misses_300s"]["sd_C"]
    line = R8.LINE_C + a8["E181"]["predicted_residue_C"]          # A8-4's registered line: room - F0 - 0.414 <= 0.50 C
    # post hoc beside: E181's own miss (measured less its own trace's prediction) added to A8's four committed misses
    m5 = list(a8["misses_300s"]["values_C"].values()) + [e181["measured_C"] - e181["predicted_C"]]
    mean5 = sum(m5) / len(m5)
    sd5 = math.sqrt(sum((x - mean5) ** 2 for x in m5) / (len(m5) - 1))
    out["E185_planned"] = {"smoke_part_change_from_E181s_C": d, "predicted_residue_C (A8's 0.414 + that change)": pred,
                           "predicted_residue_C (the splice directly)": e185["predicted_C"],
                           "A8_4_line_on_the_residue_C": line,
                           "P_refuse_settled (A8-R's normal form, at the first figure)": R8.phi_up((line - pred - mean) / sd),
                           "P_refuse_settled at E181's planned 0.414 (A8's figure)": R8.phi_up((line - a8["E181"]["predicted_residue_C"] - mean) / sd),
                           "misses_mean_sd_C": [mean, sd],
                           "post hoc: E181's own miss": e181["measured_C"] - e181["predicted_C"],
                           "post hoc: P_refuse_settled with E181's miss among the five": R8.phi_up((line - pred - mean5) / sd5),
                           "post hoc: five misses' mean_sd_C": [mean5, sd5]}
    return out


# ------------------------------------------------------------------------------------------------ the timeline
def timing():
    src = open(os.path.join(TREE, E185D, "run_e185.py")).read()
    node = [n for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "DESIGNS"][0]
    des = ast.literal_eval(node.value)
    t, rows = 0.0, []
    for kind, name, s in des["full"]:
        rows.append({"kind": kind, "name": name, "start_min": round(t / 60, 2), "end_min": round((t + s) / 60, 2)})
        t += s
    sm = sum(s for _, _, s in des["smoke"])
    return {"measured_pass": rows, "measured_pass_min": round(t / 60, 2), "smoke_plan_s (before its stop tests)": sm}


def main():
    a = sys.argv[1:]
    if len(a) not in (1, 2):
        print(__doc__)
        return 2
    os.chdir(TREE)
    OUT["inputs_sha256"] = {p: sha(p) for p in INPUTS}
    tr = json.load(open(INPUTS[0]))
    e1 = json.load(open(INPUTS[1]))
    de = json.load(open(INPUTS[2]))
    a8 = json.load(open(INPUTS[4]))
    if e1.get("train_json_sha256") != OUT["inputs_sha256"][INPUTS[0]]:
        raise SystemExit("REFUSED: the e181 stage was not read with this train json")
    P("E185 dated amendment A1: its figures, from committed files only")
    g = OUT["gains"] = gains(tr)
    for lab, v in g.items():
        P(f"gains, {lab}: re-derived G_B {v['G_B']:.5f}, G_Rl {v['G_Rl']:.5f} over {v['n_holds']} holds (rows to 4 decimals); frozen "
          f"{v['frozen_G_B']:.5f}, {v['frozen_G_Rl']:.5f}; |diff| {v['abs_diff'][0]:.1e}, {v['abs_diff'][1]:.1e}; within 2e-4 {v['within_2e-4']}")
    r = OUT["e181_stand_in"] = e181_rules(e1)
    for lab in ("one_pass (the reading stated at 20:03 PST)", "two_pass (A10's reading)"):
        v = r[lab]
        P(f"E185's rules on E181's held-out misses, {lab}: rms F/B/Rl {v['rms_C']['F']}/{v['rms_C']['B']}/{v['rms_C']['Rl']}; tau {v['tau_C']}; "
          f"RF {v['E185-RF']['verdict']} ({v['E185-RF']['D_C']}), BF {v['E185-BF']['verdict']} ({v['E185-BF']['D_C']}), "
          f"RB {v['E185-RB']['verdict']} ({v['E185-RB']['D_C']}); BEST {v['E185-BEST']}")
    P(f"  B's E181 held-out rms, two-pass against one-pass: {r['B_rms_change_pct']:+.1f}%")
    c = OUT["cool"] = cool(tr, e1, de)
    for lab in ("two_pass", "one_pass"):
        v = c[lab]
        P(f"E185-C's d on the committed windows, {lab}: " + "; ".join(
            f"{w['session'].split(' ')[0]} {w['hold']} F {w['d_F_C']:+.3f} B {w['d_B_C']:+.3f} Rl {w['d_Rl_C']:+.3f}" for w in v["windows"]))
        P("  by arm: " + "; ".join(f"{k} mean {s['mean_C']:+.3f} sd {s['sd_C']:.3f}" for k, s in v["by_arm"].items()))
    P("each arm's own scaling in d at E185's forecasts (d_arm - d_F when R is the frozen chain's): " + "; ".join(
        f"{x['hold']} B {x['d_B_less_d_F_C']:+.3f} Rl {x['d_Rl_less_d_F_C']:+.3f}" for x in c["own_scaling_at_E185_forecasts"]))
    P("  summary: " + json.dumps(c["own_scaling_summary"]))
    for k, v in c["reads_when_the_shape_is_exact"].items():
        P(f"  E185-C, {k}: {v}")
    h = OUT["hm_lg_k2"] = hm_lg(de, e1)
    P("HM-LG at k = 2: E185 counted over " + json.dumps(h["E185_holds_counted"]))
    for lab, v in h["cells"].items():
        P(f"  {lab}: six {v['six']}; four {v['four']}")
    b = OUT["best_noise_by_item"] = bykind(tr, e1, de)
    P("E185-BEST with R = P_F + the chain's committed miss on the same item + normal(0, sigma_c/2): " + json.dumps(b["BEST_pct"]))
    P("  misses by item: " + json.dumps({k: [x["e_F_C"] for x in v] for k, v in b["misses_by_item"].items()}))
    s = OUT["smoke_residue"] = smoke(a8)
    for k, v in s.items():
        if k == "M6":
            continue
        P(f"smoke residue, {k}: " + json.dumps({kk: (f"{vv:.2e}" if "P_refuse" in kk else r4(vv)) if isinstance(vv, float) else
                                                 ([r4(x) for x in vv] if isinstance(vv, list) else vv) for kk, vv in v.items()}))
    t = OUT["timeline"] = timing()
    P("timeline: " + "; ".join(f"{x['name']} {x['start_min']}-{x['end_min']}" for x in t["measured_pass"] if x["kind"] == "hold")
      + f"; the measured pass {t['measured_pass_min']} min; the smoke's plan {t['smoke_plan_s (before its stop tests)']} s before its stop tests")
    json.dump(OUT, open(a[0], "w"), indent=1, sort_keys=True)
    if len(a) == 2:
        open(a[1], "w").write("\n".join(TXT) + "\n")
    return 0 if all(v["within_2e-4"] for v in g.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
