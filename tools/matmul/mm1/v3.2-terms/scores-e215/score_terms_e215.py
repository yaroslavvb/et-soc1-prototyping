#!/usr/bin/env python3
"""score_terms_e215.py (round Q231, lane score-terms-e215, Thu 19 Nov 2026): THE FIRST BLIND TEST OF MM1-v3.1's TWO FROZEN CANDIDATE TERMS on
E215's committed data - the gemmLnc term F3 ('MM1-v3.1 + gemmLnc term', frozen 09:30:36 PST, posted #1.29) and the contention term F1
('MM1-v3.1 + contention', frozen 09:31:34 PST, posted #1.29.1) - with verify-lay's five layout controls (written 10:22:51 PST, posted
#1.29.1.1) and 'v3.1 + both terms' beside. Every comparison is REPORTED: never a registered rule of E215. The candidates were frozen before any
E215 datum and are scored after the data. Standard library only. The scoring was declared before any term was scored
(DECLARED-scoring-terms-e215.md, in this folder).

    /usr/bin/python3 -I -B score_terms_e215.py [--lab LAB] [--out DIR]

LAB (default: the lab checkout holding this folder, five levels up, or $ET_LAB) must hold, at their committed bytes:
  tools/claims-v3/e215/                       E215's registration and kit (4cb2c2ad, 8bde0182): its frozen scorer score_e215.py is imported and
                                              its load_frozen(check=True) refuses (exit 4) any changed pinned file
  tools/matmul/mm1/v3.1/out/e215/             MM1-v3.1's land (2c971828): arm A's frozen MM1-v3.1 and MM1-v3 forecasts
  tools/matmul/mm1/v3.2-terms/gemmlnc/        the gemmLnc term's land (aaeaa495)
  tools/matmul/mm1/v3.2-terms/layout/         the layout term's land with verify-lay's controls (595fcb59)
  docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/      E215 arm A's data (8355db15)
  docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/   E215 arm B's data (4f648f24)
Every frozen candidate file is checked against its posted sha256 (exit 4 on a difference), and each arm's data-e215.json against its data
directory's SHA256SUMS line.

THE ERROR CONVENTION (E215's scorer's): signed error = 100 (measured / forecast - 1), positive where the model under-forecasts; rms over the set.
At a WATTS POINT (MM1-v3.1's frozen W over idle under 3 W, or the measured one) the energy errors are measured - forecast in watts, outside the
% rms. Head to head (E215's rule): d = |ln(measured / other)| - |ln(measured / candidate)| (watts at a watts point), the candidate closer where
d > the arm's registered tie, the other where d < -tie; the exact two-sided sign test on the untied cases, decided at p < 0.05, TOO FEW under
10 untied (its p printed beside, REPORTED).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TERMS = "tools/matmul/mm1/v3.2-terms/"
GL = TERMS + "gemmlnc/"
LY = TERMS + "layout/"
POSTED = {  # the freeze lines: post, time (PST), sha256
    GL + "forecasts-gemmlnc-e215.csv": ("#1.29", "2026-11-19 09:32:02", "00fcaf5dd05e7af5a95ce1b783b68588a416dde91d0434f4f82ba6bdee6f5a7c"),
    GL + "forecasts-gemmlnc-e215.json": ("#1.29", "2026-11-19 09:32:02", "feba7e5e70829854169bb3671947767c56c2303c20a74b83c7949bcd6b024e7c"),
    GL + "term-gemmlnc.json": ("#1.29", "2026-11-19 09:32:02", "2ee478f80aa1182aeb5d00e07fc302cffa668e66964ca7ebc2e61362128f3ee4"),
    LY + "forecast-e215-v31-layout.csv": ("#1.29.1", "2026-11-19 09:32:47", "50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754"),
    LY + "forecast-e215-v31-layout.json": ("#1.29.1", "2026-11-19 09:32:47", "f09f9e1abe8acdb4995e9945b75628637e6cf61487cf561818091ee673814259"),
    LY + "controls-e215/v02_e215_controls.csv": ("#1.29.1.1", "2026-11-19 10:31:36", "c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d"),
}
DATA = {"A": "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3", "B": "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1"}
DATA_COMMIT = {"A": "8355db15", "B": "4f648f24"}
ARMS = ("A", "B")
LNC_POINTS = {"A": ("a024", "a026", "a031", "a032"), "B": ("b013",)}
TWINS = {"a024": "a021", "a026": "a022"}  # E215's cooperative points at the gemmLnc points' shapes (rgm211 gemmLn: cooperative loads)
ANALOG = {"a024": (22.42, 22.42), "a026": (22.33, 22.33), "a031": (22.80, 22.80), "a032": (22.66, 22.66), "b013": (25.7, 26.5)}  # verify-lnc's
CONTROLS = (("N3", "REPORTED_N3_cycles_per_op_wall"), ("N1+N2", "REPORTED_N1+N2_cycles_per_op_wall"), ("G1", "REPORTED_G1_cycles_per_op_wall"),
            ("G1+N1", "REPORTED_G1+N1_cycles_per_op_wall"), ("fresh24", "REPORTED_fresh24_cycles_per_op_wall"))
LAYOUT_SETS = {"A": [("gemmL1x9x6, 28 shires (one row group off)", ["a001", "a002", "a003", "a004", "a005", "a006", "a007", "a008"]),
                     ("gemmL1x9x6, 24 shires (spread)", ["a009", "a010"])],
               "B": [("gemmL1x15x4, 28 shires (one row group off)", ["b001", "b002", "b003", "b004"])]}
NAME = {"v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "t7": "v3.1 with T7", "lnc": "v3.1 + gemmLnc term (F3)",
        "lncF1": "gemmLnc form F1 (REPORTED)", "lncF2": "gemmLnc form F2 (REPORTED)", "lncF4": "gemmLnc form F4 (REPORTED)",
        "cont": "v3.1 + contention (F1)", "both": "v3.1 + both terms", "N3": "control N3", "N1+N2": "control N1+N2", "G1": "control G1",
        "G1+N1": "control G1+N1", "fresh24": "control fresh24"}
FULL = "0xffffffff"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def r6(x):
    return None if x is None else (round(x, 6) if isinstance(x, float) else x)


def pct(x):
    return None if x is None else round(100.0 * x, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", default=os.environ.get("ET_LAB") or os.path.normpath(os.path.join(HERE, *[".."] * 5)))
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()
    LAB = os.path.abspath(a.lab)
    OUT = os.path.abspath(a.out)
    os.makedirs(OUT, exist_ok=True)
    t_start = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    res = {"what": "the first blind test of MM1-v3.1's two frozen candidate terms (gemmLnc F3; contention F1) and verify-lay's controls on "
                   "E215's committed data; REPORTED, never a registered rule of E215; frozen before any E215 datum, scored after it",
           "lane": "score-terms-e215 (round Q231)", "made": t_start,
           "interpreter": f"/usr/bin/python3 {sys.version.split()[0]}", "convention": "signed error = measured / forecast - 1 (in %); watts "
           "points in watts (measured - forecast)", "checks": {}}

    # ---- 0. the frozen files against their posted sha256; the data files against their SHA256SUMS
    chk = {}
    for rel, (post, when, want) in POSTED.items():
        got = sha(os.path.join(LAB, rel))
        chk[rel] = {"post": post, "posted_PST": when, "sha256": got, "equal_to_post": got == want}
        if got != want:
            print(f"score_terms_e215: REFUSED, {rel} is {got}, posted {want}")
            sys.exit(4)
    for tag in ARMS:
        d = os.path.join(LAB, DATA[tag])
        sums = {}
        for line in open(os.path.join(d, "SHA256SUMS")):
            h, _, f = line.strip().partition("  ")
            sums[f] = h
        for f in ("data-e215.json", "labels-e215.json"):
            got = sha(os.path.join(d, f))
            ok = sums.get(f) == got
            chk[DATA[tag] + "/" + f] = {"sha256": got, "equal_to_SHA256SUMS": ok, "data_commit": DATA_COMMIT[tag]}
            if not ok:
                print(f"score_terms_e215: REFUSED, {DATA[tag]}/{f} differs from its SHA256SUMS")
                sys.exit(4)
    res["checks"]["sha256"] = chk

    # ---- 1. E215's frozen scorer, inputs and reader (imported from its committed folder)
    sys.path.insert(0, os.path.join(LAB, "tools", "claims-v3", "e215"))
    import score_e215 as sc  # noqa: E402
    if os.path.normpath(sc.REPO) != os.path.normpath(LAB):
        print(f"score_terms_e215: REFUSED, score_e215 resolves the lab at {sc.REPO}, not {LAB}")
        sys.exit(4)
    rules, P, fc = sc.load_frozen(check=True)  # exits 4 on any changed pin
    res["checks"]["e215_pins"] = "load_frozen(check=True): every pinned file equal (no exit 4)"
    res["checks"]["e215_scorer_sha256"] = sha(os.path.join(LAB, "tools/claims-v3/e215/score_e215.py"))
    M, runs_by, flags_all = {}, {}, {}
    for tag in ARMS:
        dj = json.load(open(os.path.join(LAB, DATA[tag], "data-e215.json")))
        lab = json.load(open(os.path.join(LAB, DATA[tag], "labels-e215.json")))
        arm = dj["arms"][tag]
        fsm = {s["id"]: s["loop"] for s in P["arms"][tag]["smoke"] if s["id"] not in sc.SESSION_SMOKE}
        m, flags, r0, s6 = sc.reduce_arm(tag, arm, P, lab.get(tag, {}), fsm)
        M[tag] = m
        flags_all[tag] = {"flags": flags, "R0_failures": r0, "S6_failures": s6, "labels": lab.get(tag, {})}
        # the per-run wall cycles an op, by the reader's keep rule (re-checked: their means equal the reader's to the last bit)
        pts = {p["id"]: p for p in P["arms"][tag]["points"] + P["arms"][tag].get("references", [])}
        runs_by[tag] = {}
        for pid, pt in (arm.get("points") or {}).items():
            p = pts[pid]
            kept = []
            for r in pt.get("runs", []):
                rec = r.get("record") or {}
                same = (rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == p["minions"]
                        and int(str(rec.get("shire_mask")), 16) == int(p["shire_mask"], 16))
                wg = True
                if p["host"] == "rgm211":
                    w = r.get("walk") or {}
                    wg = bool(w.get("ok")) and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")
                if same and wg and r.get("t_gemm_s") is not None and r.get("cycles_gemm") is not None:
                    kept.append({"n": r.get("n"), "cw": r["cycles_gemm"] / p["ops_per_minion_per_gemm"], "t": r["t_gemm_s"]})
            runs_by[tag][pid] = kept
            if pid in m:
                assert len(kept) == m[pid]["n_runs"] and sc.mean([k["cw"] for k in kept]) == m[pid]["cw"], pid
    res["checks"]["reader"] = {t: {"points_read": len(M[t]), **{k: v for k, v in flags_all[t].items()}} for t in ARMS}
    res["checks"]["per_run_keep_rule"] = "every point's kept runs re-made here; their mean wall cycles equal the frozen reader's bit for bit"

    # ---- 2. the candidate models, from their frozen files only
    gj = json.load(open(os.path.join(LAB, GL, "forecasts-gemmlnc-e215.json")))
    lrow = {r["id"]: r for r in gj["rows"]}
    gcsv = {r["id"]: r for r in csv.DictReader(open(os.path.join(LAB, GL, "forecasts-gemmlnc-e215.csv"), newline=""))}
    lay = {r["id"]: r for r in csv.DictReader(open(os.path.join(LAB, LY, "forecast-e215-v31-layout.csv"), newline=""))}
    ctl = {r["id"]: r for r in csv.DictReader(open(os.path.join(LAB, LY, "controls-e215/v02_e215_controls.csv"), newline=""))}
    layj = json.load(open(os.path.join(LAB, LY, "forecast-e215-v31-layout.json")))
    term = json.load(open(os.path.join(LAB, GL, "term-gemmlnc.json")))
    fx = {t: copy.deepcopy(fc[t]) for t in ARMS}
    pinfo = {t: {p["id"]: p for p in P["arms"][t]["points"] + P["arms"][t].get("references", [])} for t in ARMS}
    cks = {"lnc_csv_equals_json": 0, "lnc_base_equals_e215_v31_max_rel": 0.0, "layout_rows": 0, "full_mask_rows": 0, "full_mask_factor_exactly_1": 0,
           "full_mask_controls_equal_v31": 0, "subset_rows": 0, "subset_F1_csv_vs_base_x_g_max_abs_cycles": 0.0,
           "controls_v31_vs_e215_v31_max_abs_cycles": 0.0, "controls_F1_vs_frozen_F1_max_abs_cycles": 0.0, "v31_seconds_vs_cycles_x_ops_max_rel": 0.0,
           "both_equals_lnc_on_gemmlnc": 0, "both_equals_cont_on_subset": 0, "both_equals_v31_elsewhere": 0}
    for tag in ARMS:
        for pid, F in fx[tag].items():
            if pid not in pinfo[tag]:  # the ties (t01, t02): never scored
                continue
            b = F["v31"]
            p = pinfo[tag][pid]
            ops = p["ops_per_minion_per_gemm"]
            rel_t = abs(b["t"] / (b["cw"] / 600e6 * ops) - 1)
            cks["v31_seconds_vs_cycles_x_ops_max_rel"] = max(cks["v31_seconds_vs_cycles_x_ops_max_rel"], rel_t)
            # gemmLnc term (F3) and its frozen sibling forms
            if pid in lrow and not pid.startswith("s"):
                r = lrow[pid]
                c = gcsv[pid]
                assert abs(float(c["lnc_W_over_idle"]) - r["lnc_W_over_idle"]) < 1e-6 and abs(float(c["lnc_B_W_us"]) - r["lnc_B_W_us"]) < 1e-6
                cks["lnc_csv_equals_json"] += 1
                for kk, bb in (("A", r["v31_A_W"]), ("B", r["v31_B_W_us"]), ("cw", r["v31_cycles_wall"]), ("t", r["v31_seconds_per_gemm"])):
                    cks["lnc_base_equals_e215_v31_max_rel"] = max(cks["lnc_base_equals_e215_v31_max_rel"], abs(bb / b[kk] - 1))
                F["lnc"] = {"cw": b["cw"], "cm": b["cm"], "t": b["t"], "A": r["lnc_A_W"], "B": r["lnc_B_W_us"], "W": r["lnc_W_over_idle"],
                            "J": r["lnc_J_over_idle"], "dB": r["lnc_B_W_us"] - r["v31_B_W_us"], "term_W_at_v31_t": r["lnc_term_W"],
                            "NB": r["NB"], "dup": r["dup"], "first": r["first"], "Jrest_frozen_rest_law": r["lnc_J_at_rest"],
                            "rest_law_W": r["rest_law_W"]}
                for form in ("F1", "F2", "F4", "F3"):
                    F["lnc" + form] = {"cw": b["cw"], "cm": b["cm"], "t": b["t"], "A": r["lnc_A_W"], "B": r[form + "_B_W_us"],
                                       "W": r[form + "_W_over_idle"], "J": r[form + "_J_over_idle"], "dB": r[form + "_B_W_us"] - r["v31_B_W_us"]}
                assert F["lncF3"]["B"] == F["lnc"]["B"] and F["lncF3"]["W"] == F["lnc"]["W"]
            else:
                F["lnc"] = dict(b, dB=0.0)
            # contention term (F1): the frozen layout factor; full mask exactly 1
            L = lay[pid]
            assert L["e215_arm"] == tag and L["mask"] == p["shire_mask"] and int(L["ops_per_minion_per_gemm"]) == ops
            cks["layout_rows"] += 1
            g = float(L["layout_factor"])
            cr = ctl[pid]
            assert cr["mask"] == p["shire_mask"]
            cks["controls_v31_vs_e215_v31_max_abs_cycles"] = max(cks["controls_v31_vs_e215_v31_max_abs_cycles"], abs(float(cr["v31_cycles_per_op_wall"]) - b["cw"]))
            cks["controls_F1_vs_frozen_F1_max_abs_cycles"] = max(cks["controls_F1_vs_frozen_F1_max_abs_cycles"],
                                                                 abs(float(cr["F1_frozen_cycles_per_op_wall"]) - float(L["v31c_cycles_per_op_wall"])))
            if p["shire_mask"] == FULL:
                cks["full_mask_rows"] += 1
                if g == 1.0 and float(L["phi_fresh"]) == 0.0 and L["v31c_cycles_per_op_wall"] == L["v31_cycles_per_op_wall"]:
                    cks["full_mask_factor_exactly_1"] += 1
                if all(cr[col] == cr["v31_cycles_per_op_wall"] for _, col in CONTROLS) and cr["F1_frozen_cycles_per_op_wall"] == cr["v31_cycles_per_op_wall"]:
                    cks["full_mask_controls_equal_v31"] += 1
                F["cont"] = dict(b, g=1.0)
                for nm, _ in CONTROLS:
                    F[nm] = {"cw": b["cw"], "t": b["t"], "g": 1.0}
            else:
                cks["subset_rows"] += 1
                cw1 = float(L["v31c_cycles_per_op_wall"])
                t1 = float(L["v31c_seconds_per_gemm"])
                cks["subset_F1_csv_vs_base_x_g_max_abs_cycles"] = max(cks["subset_F1_csv_vs_base_x_g_max_abs_cycles"], abs(cw1 - b["cw"] * g))
                Wc = b["A"] + b["B"] / (cw1 / 600.0) if b.get("A") is not None else None
                F["cont"] = {"cw": cw1, "cm": b["cm"] * g if b.get("cm") else None, "t": t1, "A": b.get("A"), "B": b.get("B"),
                             "W": Wc, "J": (Wc * t1) if Wc is not None else None, "g": g, "phi_fresh": float(L["phi_fresh"])}
                for nm, col in CONTROLS:
                    cwc = float(cr[col])
                    F[nm] = {"cw": cwc, "t": cwc / 600e6 * ops, "g": cwc / float(cr["v31_cycles_per_op_wall"])}
            # 'v3.1 + both terms': E216's declared composition. On E215 it reduces to one model at every point (no point carries both terms), so
            # 'both' takes that model's frozen values exactly; the composition's formula is evaluated beside and its worst relative difference
            # from the chosen values recorded (rounding of arm B's 6-decimal CSV columns only).
            gb = F["cont"].get("g", 1.0)
            cwb = F["cont"]["cw"]
            tb = F["cont"]["t"]
            if b.get("A") is not None:
                Bb = b["B"] + F["lnc"].get("dB", 0.0)
                Wb = b["A"] + Bb / (cwb / 600.0)
                formula = {"cw": cwb, "t": tb, "W": Wb, "J": Wb * tb}
            else:
                formula = {"cw": cwb, "t": tb, "W": None, "J": None}
            if pid in LNC_POINTS[tag]:
                assert gb == 1.0 and p["shire_mask"] == FULL
                F["both"] = dict(F["lnc"], g=1.0, reduces_to="lnc")
                cks["both_equals_lnc_on_gemmlnc"] += 1
            elif p["shire_mask"] != FULL:
                assert F["lnc"].get("dB", 0.0) == 0.0
                F["both"] = dict(F["cont"], reduces_to="cont")
                cks["both_equals_cont_on_subset"] += 1
            else:
                assert gb == 1.0 and F["lnc"].get("dB", 0.0) == 0.0
                F["both"] = dict(b, g=1.0, reduces_to="v31")
                cks["both_equals_v31_elsewhere"] += 1
            for kk in ("cw", "t", "W", "J"):
                if formula[kk] is not None and F["both"].get(kk):
                    key = "both_formula_vs_chosen_max_rel_" + kk
                    cks[key] = max(cks.get(key, 0.0), abs(formula[kk] / F["both"][kk] - 1))
    cks["a_fresh_frozen"] = layj["meta"]["a_fresh"]
    cks["term_constants_pJ"] = term.get("constants_pJ_per_line")
    res["checks"]["models"] = cks

    # ---- 3. the per-point and per-case arithmetic
    def is_watts(tag, pid):
        v = M[tag][pid]
        return fc[tag][pid]["v31"]["W"] < sc.LOW or (v["W"] is not None and v["W"] < sc.LOW)

    def energy_errs(tag, pid, f):
        v = M[tag][pid]
        if f is None or f.get("A") is None or f.get("B") is None or v["W"] is None:
            return None
        Wg, Jg = sc.given(f, v["cw"], v["t"])
        w = is_watts(tag, pid)
        out = {"W_given_t": Wg, "err_W_given_t": v["W"] / Wg - 1, "watts": w,
               "E1": (v["W"] - Wg) if w else v["J"] / Jg - 1,
               "E2": (v["W"] - f["W"]) if w else v["J"] / f["J"] - 1,
               "E3": v["Jrest"] / (v["prest"] * v["t"] + Jg) - 1,
               "E4": v["Jrest"] / (v["prest"] * f["t"] + f["J"]) - 1,
               "J_given_t": Jg, "Jrest_given_t": v["prest"] * v["t"] + Jg, "Jrest_t_forecast": v["prest"] * f["t"] + f["J"]}
        return out

    def time_errs(v, f):
        out = {}
        for k in ("cw", "cm", "t"):
            out[k] = (v[k] / f[k] - 1) if (f and f.get(k)) else None
        return out

    def dpair(meas, fx_, fy_, watts=False, Wm=None):
        """d = |ln(meas / y)| - |ln(meas / x)|: x the candidate, y the other (watts: |W - Wy| - |W - Wx|)"""
        if fx_ is None or fy_ is None:
            return None
        if watts:
            return abs(Wm - fy_) - abs(Wm - fx_)
        return abs(math.log(meas / fy_)) - abs(math.log(meas / fx_))

    def decide(cells, label):
        npos = sum(1 for c in cells if c["d"] > c["tie"])
        nneg = sum(1 for c in cells if c["d"] < -c["tie"])
        n = len(cells)
        o = {"n": n, "candidate_closer": npos, "other_closer": nneg, "ties": n - npos - nneg}
        if n == 0:
            o["verdict"] = "NO DATA"
            return o
        o["p_two_sided_REPORTED"] = sc.sign_p(npos, nneg)
        if npos + nneg < 10:
            o["verdict"] = "TOO FEW"
        elif o["p_two_sided_REPORTED"] < 0.05:
            o["verdict"] = (label[0] + " CLOSER") if npos > nneg else (label[1] + " CLOSER")
        else:
            o["verdict"] = "NOT DECIDED"
        return o

    def h_cells(tag, pids, x, y, quantities=("H1", "H2", "H3", "H4", "H5", "R3", "R4")):
        """E215's h_pair arithmetic over the given points (time per case; energy per point), plus R3/R4: J at rest given t / with t forecast"""
        ties = rules["arms"][tag]["ties"]
        F = fx[tag]
        out = {q: [] for q in quantities}
        cases = {}
        for pid in pids:
            v = M[tag].get(pid)
            if v is None or v["role"] != "point":
                continue
            if v["time_scored"]:
                cases.setdefault(v["case"], []).append(pid)
        for case, ids in sorted(cases.items()):
            Fx, Fy = F[ids[0]].get(x) or {}, F[ids[0]].get(y) or {}
            for q, key, tk in (("H1", "cw", "cycles_ln"), ("H2", "cm", "cycles_ln"), ("H3", "t", "seconds_ln")):
                if q not in out:
                    continue
                m = sc.mean([M[tag][i][key] for i in ids])
                if Fx.get(key) and Fy.get(key):
                    out[q].append({"id": case, "points": ids, "d": dpair(m, Fx[key], Fy[key]), "tie": ties[tk], "watts": False})
        for pid in pids:
            v = M[tag].get(pid)
            if v is None or v["role"] != "point" or v["W"] is None:
                continue
            fxp, fyp = F[pid].get(x) or {}, F[pid].get(y) or {}
            ex, ey = energy_errs(tag, pid, fxp), energy_errs(tag, pid, fyp)
            if ex is None or ey is None:
                continue
            w = ex["watts"]
            tie = ties["watts_W"] if w else ties["joules_ln"]
            if "H4" in out:
                out["H4"].append({"id": pid, "d": dpair(v["J"], ex["J_given_t"], ey["J_given_t"], w, v["W"]) if not w else
                                  abs(v["W"] - ey["W_given_t"]) - abs(v["W"] - ex["W_given_t"]), "tie": tie, "watts": w})
            if "H5" in out:
                out["H5"].append({"id": pid, "d": dpair(v["J"], fxp["J"], fyp["J"]) if not w else abs(v["W"] - fyp["W"]) - abs(v["W"] - fxp["W"]),
                                  "tie": tie, "watts": w})
            if "R3" in out:
                out["R3"].append({"id": pid, "d": dpair(v["Jrest"], ex["Jrest_given_t"], ey["Jrest_given_t"]), "tie": ties["joules_ln"], "watts": False})
            if "R4" in out:
                out["R4"].append({"id": pid, "d": dpair(v["Jrest"], ex["Jrest_t_forecast"], ey["Jrest_t_forecast"]), "tie": ties["joules_ln"],
                                  "watts": False})
        return out

    def hh(tag_pids, x, y, quantities=("H1", "H2", "H3", "H4", "H5", "R3", "R4")):
        """pooled over arms: tag_pids = [(tag, [pids]), ...]"""
        allc = {q: [] for q in quantities}
        per = {}
        for tag, pids in tag_pids:
            c = h_cells(tag, pids, x, y, quantities)
            per[tag] = {q: decide(c[q], (NAME[x], NAME[y])) for q in quantities}
            for q in quantities:
                allc[q] += [dict(cc, arm=tag) for cc in c[q]]
        pooled = {q: decide(allc[q], (NAME[x], NAME[y])) for q in quantities}
        cells = {q: [{"arm": cc["arm"], "id": cc["id"], "d": round(cc["d"], 6), "tie": cc["tie"], "watts": cc["watts"]} for cc in allc[q]] for q in quantities}
        return {"candidate": NAME[x], "other": NAME[y], "pooled": pooled, "per_arm": per, "cells": cells}

    def stats_set(tag_pids, model, kinds=("cw", "cm", "t")):
        """rms and bias (signed %) of time per case and energy per point (watts points apart, in W)"""
        tl = {k: [] for k in kinds}
        el = {q: [] for q in ("W_given_t", "E1", "E2", "E3", "E4")}
        wl = {q: [] for q in ("W_given_t", "E1", "E2")}
        for tag, pids in tag_pids:
            cases = {}
            for pid in pids:
                v = M[tag].get(pid)
                if v is None or v["role"] != "point":
                    continue
                if v["time_scored"]:
                    cases.setdefault(v["case"], []).append(pid)
            for case, ids in cases.items():
                f = fx[tag][ids[0]].get(model) or {}
                for k in kinds:
                    if f.get(k):
                        tl[k].append(sc.mean([M[tag][i][k] for i in ids]) / f[k] - 1)
            for pid in pids:
                v = M[tag].get(pid)
                if v is None or v["role"] != "point":
                    continue
                e = energy_errs(tag, pid, fx[tag][pid].get(model))
                if e is None:
                    continue
                if e["watts"]:
                    wl["W_given_t"].append(v["W"] - e["W_given_t"])
                    wl["E1"].append(e["E1"])
                    wl["E2"].append(e["E2"])
                else:
                    for q in ("W_given_t", "E1", "E2"):
                        el[q].append(e["err_W_given_t"] if q == "W_given_t" else e[q])
                el["E3"].append(e["E3"])
                el["E4"].append(e["E4"])
        o = {}
        for k, v in tl.items():
            o[{"cw": "wall_cycles", "cm": "counter_mean", "t": "seconds"}[k]] = {"n": len(v), "rms_pct": pct(rms(v)), "bias_pct": pct(mean(v))}
        names = {"W_given_t": "W_over_idle_given_t", "E1": "J_over_idle_given_t", "E2": "J_over_idle_t_forecast", "E3": "J_at_rest_given_t",
                 "E4": "J_at_rest_t_forecast"}
        for q, v in el.items():
            o[names[q]] = {"n": len(v), "rms_pct": pct(rms(v)), "bias_pct": pct(mean(v))}
        for q, v in wl.items():
            if v:
                o[names[q] + "_watts_points"] = {"n": len(v), "rms_W": r6(rms(v)), "bias_W": r6(mean(v))}
        return o

    # ---- PART 1: the gemmLnc term on E215's gemmLnc points and their cooperative twins
    p1 = {"points": [], "twins": [], "readings": {}}
    lnc_tp = [(t, list(LNC_POINTS[t])) for t in ARMS]
    for tag in ARMS:
        for pid in LNC_POINTS[tag]:
            v = M[tag][pid]
            F = fx[tag][pid]
            row = {"arm": tag, "id": pid, "token": pinfo[tag][pid]["arm"], "NB": F["lnc"]["NB"], "n_runs": v["n_runs"],
                   "measured": {"wall_cycles": r6(v["cw"]), "counter_mean": r6(v["cm"]), "seconds": v["t"], "W_over_idle": r6(v["W"]),
                                "J_over_idle": v["J"], "J_at_rest": v["Jrest"], "p_rest": r6(v["prest"]), "die_start_c": r6(v["die"])},
                   "time_err_pct": {}, "models": {}}
            for mdl in ("v31", "v3", "lnc", "lncF1", "lncF2", "lncF4"):
                f = F.get(mdl)
                e = energy_errs(tag, pid, f)
                te = time_errs(v, f)
                row["models"][mdl] = {"W_frozen_own_t": r6(f["W"]), "W_given_t": r6(e["W_given_t"]), "err_W_given_t_pct": pct(e["err_W_given_t"]),
                                      "err_J_over_idle_given_t_pct": pct(e["E1"]), "err_J_over_idle_t_forecast_pct": pct(e["E2"]),
                                      "err_J_at_rest_given_t_pct": pct(e["E3"]), "err_J_at_rest_t_forecast_pct": pct(e["E4"]),
                                      "err_wall_cycles_pct": pct(te["cw"]), "err_seconds_pct": pct(te["t"]),
                                      "dB_over_v31_W_us": r6(f.get("dB", 0.0) if mdl != "v3" else None)}
            # the term's direction and size, given the measured op time
            t_op = v["cw"] / 600.0
            b = F["v31"]
            Wg31 = b["A"] + b["B"] / t_op
            dB_meas = (v["W"] - b["A"]) * t_op - b["B"]
            row["term"] = {"measured_excess_over_v31_given_t_W": r6(v["W"] - Wg31), "term_given_t_W": r6(F["lnc"]["dB"] / t_op),
                           "term_at_v31_t_W_frozen": r6(F["lnc"]["term_W_at_v31_t"]), "measured_excess_energy_an_op_step_W_us": r6(dB_meas),
                           "term_energy_an_op_step_W_us": r6(F["lnc"]["dB"]), "measured_over_term": r6(dB_meas / F["lnc"]["dB"]),
                           "direction_held": (v["W"] - Wg31) > 0, "dup": F["lnc"]["dup"], "first": r6(F["lnc"]["first"]),
                           "forms_measured_over_predicted_excess": {fm: r6(dB_meas / F["lnc" + fm]["dB"]) for fm in ("F1", "F2", "F3", "F4")}}
            c1, c2 = term["constants_pJ_per_line"]
            dup_share = c1 * F["lnc"]["dup"] / (c1 * F["lnc"]["dup"] + c2 * F["lnc"]["first"])
            row["term"]["F3_duplicate_read_part_W_us"] = r6(F["lnc"]["dB"] * dup_share)
            row["term"]["measured_over_F3_duplicate_read_part"] = r6(dB_meas / (F["lnc"]["dB"] * dup_share))
            row["analog_verify_lnc_W"] = ANALOG[pid]
            eL = energy_errs(tag, pid, F["lnc"])
            row["analog_reading"] = {"F3_frozen_own_t_minus_measured_W": r6(F["lnc"]["W"] - v["W"]),
                                     "F3_given_t_minus_measured_W": r6(eL["W_given_t"] - v["W"]),
                                     "analog_minus_measured_W": [r6(ANALOG[pid][0] - v["W"]), r6(ANALOG[pid][1] - v["W"])],
                                     "F3_frozen_own_t_minus_analog_W": [r6(F["lnc"]["W"] - ANALOG[pid][1]), r6(F["lnc"]["W"] - ANALOG[pid][0])]}
            row["J_at_rest_frozen_rest_law_REPORTED"] = {"lnc": F["lnc"]["Jrest_frozen_rest_law"], "measured": v["Jrest"],
                                                         "err_pct": pct(v["Jrest"] / F["lnc"]["Jrest_frozen_rest_law"] - 1),
                                                         "rest_law_W": r6(F["lnc"]["rest_law_W"]), "measured_rest_W": r6(v["prest"])}
            p1["points"].append(row)
    for g, tw in TWINS.items():
        vg, vt = M["A"][g], M["A"][tw]
        Fg, Ft = fx["A"][g], fx["A"][tw]
        eg = {m: energy_errs("A", g, Fg[m]) for m in ("v31", "v3", "lnc")}
        et = {m: energy_errs("A", tw, Ft[m]) for m in ("v31", "v3", "lnc")}
        p1["twins"].append({"gemmLnc": g, "twin": tw, "twin_token": pinfo["A"][tw]["arm"], "twin_loop": pinfo["A"][tw]["loop"],
                            "twin_measured": {"wall_cycles": r6(vt["cw"]), "W_over_idle": r6(vt["W"]), "n_runs": vt["n_runs"]},
                            "twin_err_W_given_t_pct": {m: pct(et[m]["err_W_given_t"]) for m in et},
                            "twin_err_wall_cycles_pct": {m: pct(vt["cw"] / Ft[m]["cw"] - 1) for m in ("v31", "v3")},
                            "ratio_W_gemmLnc_over_twin": {"measured": r6(vg["W"] / vt["W"]),
                                                          **{m: r6(eg[m]["W_given_t"] / et[m]["W_given_t"]) for m in ("v31", "v3", "lnc")}},
                            "ratio_wall_cycles_gemmLnc_over_twin": {"measured": r6(vg["cw"] / vt["cw"]), "v31": r6(Fg["v31"]["cw"] / Ft["v31"]["cw"]),
                                                                    "v3": r6(Fg["v3"]["cw"] / Ft["v3"]["cw"])},
                            "term_on_twin": "0 by construction (dup = 0 on a cooperative loop): 'v3.1 + gemmLnc term' = MM1-v3.1 there"})
    p1["stats"] = {mdl: stats_set(lnc_tp, mdl, kinds=("cw", "t")) for mdl in ("v31", "v3", "lnc", "lncF1", "lncF2", "lncF4")}
    p1["stats_per_arm"] = {tag: {mdl: stats_set([(tag, list(LNC_POINTS[tag]))], mdl, kinds=("cw", "t")) for mdl in ("v31", "v3", "lnc")} for tag in ARMS}
    p1["head_to_head"] = {"lnc vs v31": hh(lnc_tp, "lnc", "v31", ("H4", "H5", "R3", "R4")),
                          "lnc vs v3": hh(lnc_tp, "lnc", "v3", ("H4", "H5", "R3", "R4"))}
    for fm in ("lncF1", "lncF2", "lncF4"):
        p1["head_to_head"][f"lnc vs {fm} (REPORTED)"] = hh(lnc_tp, "lnc", fm, ("H4", "H5"))
    p1["twins_stats"] = {mdl: stats_set([("A", list(TWINS.values()))], mdl, kinds=("cw", "t")) for mdl in ("v31", "v3", "lnc")}

    # ---- PART 2: the contention term and the controls on the subset-mask points
    sub_tp = [(t, [p["id"] for p in P["arms"][t]["points"] if p["shire_mask"] != FULL]) for t in ARMS]
    full_tp = [(t, [p["id"] for p in P["arms"][t]["points"] if p["shire_mask"] == FULL]) for t in ARMS]
    cands = ["cont"] + [nm for nm, _ in CONTROLS] + ["t7"]
    p2 = {"subset_points": [], "stats": {}, "stats_per_arm": {}, "head_to_head": {}, "pairs": {}, "noise": {}}
    for tag, pids in sub_tp:
        for pid in pids:
            v = M[tag][pid]
            F = fx[tag][pid]
            row = {"arm": tag, "id": pid, "token": pinfo[tag][pid]["arm"], "mask": pinfo[tag][pid]["shire_mask"],
                   "shires": pinfo[tag][pid]["shires"], "n_runs": v["n_runs"], "measured_wall_cycles": r6(v["cw"]), "measured_seconds": v["t"],
                   "F1_factor": F["cont"].get("g"), "phi_fresh": F["cont"].get("phi_fresh"), "models": {}}
            for mdl in ["v31", "v3"] + cands:
                f = F.get(mdl) or {}
                row["models"][mdl] = {"wall_cycles": r6(f.get("cw")), "err_wall_cycles_pct": pct(v["cw"] / f["cw"] - 1) if f.get("cw") else None,
                                      "seconds": f.get("t"), "err_seconds_pct": pct(v["t"] / f["t"] - 1) if f.get("t") else None}
            p2["subset_points"].append(row)
    for mdl in ["v31", "v3"] + cands:
        p2["stats"][mdl] = stats_set(sub_tp, mdl, kinds=("cw", "t"))
        p2["stats_per_arm"][mdl] = {tag: stats_set([(tag, pids)], mdl, kinds=("cw", "t")) for tag, pids in sub_tp}
        p2["stats"][mdl] = {k: v for k, v in p2["stats"][mdl].items() if k in ("wall_cycles", "seconds")}
        p2["stats_per_arm"][mdl] = {t: {k: v for k, v in s.items() if k in ("wall_cycles", "seconds")} for t, s in p2["stats_per_arm"][mdl].items()}
    for mdl in cands:
        p2["head_to_head"][f"{mdl} vs v31"] = hh(sub_tp, mdl, "v31", ("H1", "H3"))
    p2["head_to_head"]["cont vs v3"] = hh(sub_tp, "cont", "v3", ("H1", "H3"))
    # POST HOC reading beyond the declaration (REPORTED): at the rows where a candidate moves MM1-v3.1's wall cycles at all, is it closer to the
    # measurement (no tie)? And the rms of MM1-v3.1 and the candidate on those rows only.
    p2["moved_rows_POST_HOC"] = {}
    for mdl in cands:
        closer = farther = 0
        ids, e31, ec = [], [], []
        for tag, pids in sub_tp:
            for pid in pids:
                v = M[tag][pid]
                b, f = fx[tag][pid]["v31"], fx[tag][pid][mdl]
                if abs(math.log(f["cw"] / b["cw"])) <= 1e-6:  # above the 4-decimal printing of the frozen cycles (<= 5e-8 relative)
                    continue
                ids.append(pid)
                dd = abs(math.log(v["cw"] / b["cw"])) - abs(math.log(v["cw"] / f["cw"]))
                closer += dd > 0
                farther += dd < 0
                e31.append(v["cw"] / b["cw"] - 1)
                ec.append(v["cw"] / f["cw"] - 1)
        p2["moved_rows_POST_HOC"][mdl] = {"rows_moved": len(ids), "candidate_closer_no_tie": closer, "v31_closer_no_tie": farther,
                                          "p_two_sided_sign_test_no_tie": sc.sign_p(closer, farther) if ids else None,
                                          "rms_wall_pct_on_moved_rows": {"v31": pct(rms(e31)), mdl: pct(rms(ec))}, "rows": ids,
                                          "label": "post hoc reading (not in the declaration): REPORTED"}
    # POST HOC split by shire count (REPORTED): the 14 rows of 24-28 shires (one value a shape for F1: 0.999505 or 1.0) and the 14 rows of
    # 2-15 shires, where the layout term's dated note says F1 moves (by -0.6% to +1.4%)
    p2["by_shire_count_POST_HOC"] = {}
    for lab_, cond in (("24-28 shires", lambda n: n >= 24), ("2-15 shires", lambda n: n < 24)):
        tp = [(t, [pid for pid in pids if cond(pinfo[t][pid]["shires"])]) for t, pids in sub_tp]
        blk = {"points": {t: ids for t, ids in tp}, "stats": {}, "sign_test_vs_v31": {}, "closer_no_tie_vs_v31": {}}
        for mdl in ["v31", "v3"] + cands:
            s = stats_set(tp, mdl, kinds=("cw", "t"))
            blk["stats"][mdl] = {k: v for k, v in s.items() if k in ("wall_cycles", "seconds")}
            if mdl == "v31":
                continue
            h = hh(tp, mdl, "v31", ("H1",))
            blk["sign_test_vs_v31"][mdl] = h["pooled"]["H1"]
            c = f_ = 0
            for t, ids in tp:
                for pid in ids:
                    v = M[t][pid]
                    b, f = fx[t][pid]["v31"], fx[t][pid][mdl]
                    dd = abs(math.log(v["cw"] / b["cw"])) - abs(math.log(v["cw"] / f["cw"]))
                    if abs(math.log(f["cw"] / b["cw"])) <= 1e-6:
                        continue
                    c += dd > 0
                    f_ += dd < 0
            blk["closer_no_tie_vs_v31"][mdl] = {"candidate_closer": c, "v31_closer": f_, "p_two_sided": sc.sign_p(c, f_) if (c + f_) else None}
        p2["by_shire_count_POST_HOC"][lab_] = blk
    # the full-chip points: F1 and every control are MM1-v3.1 exactly there
    p2["full_chip"] = {"points": sum(len(x) for _, x in full_tp), "F1_equals_v31": all(fx[t][pid]["cont"]["cw"] == fx[t][pid]["v31"]["cw"]
                                                                                      for t, x in full_tp for pid in x),
                       "controls_equal_v31": all(fx[t][pid][nm]["cw"] == fx[t][pid]["v31"]["cw"] for t, x in full_tp for pid in x for nm, _ in CONTROLS),
                       "reading": "the terms and controls are 0 at the full mask by construction: nothing to score there (MM1-v3.1's own score)"}
    # noise: the pooled within-point sd of ln(per-run wall cycles) over each arm's points with two or more kept runs
    for tag in ARMS:
        ss, dof, npts = 0.0, 0, 0
        for pid, kept in runs_by[tag].items():
            if len(kept) >= 2:
                xs = [math.log(k["cw"]) for k in kept]
                mu = sum(xs) / len(xs)
                ss += sum((x_ - mu) ** 2 for x_ in xs)
                dof += len(xs) - 1
                npts += 1
        sd = math.sqrt(ss / dof) if dof else None
        p2["noise"][tag] = {"pooled_within_point_sd_ln_wall_cycles": r6(sd), "points": npts, "dof": dof,
                            "registered_time_tie_ln": rules["arms"][tag]["ties"]["cycles_ln"]}
        sets = []
        for label, ids in LAYOUT_SETS[tag]:
            prs = []
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    a_, b_ = ids[i], ids[j]
                    va, vb = M[tag][a_], M[tag][b_]
                    dm = math.log(va["cw"] / vb["cw"])
                    thr = 1.96 * sd * math.sqrt(1.0 / va["n_runs"] + 1.0 / vb["n_runs"])
                    beyond = abs(dm) > thr
                    pr = {"pair": f"{a_}/{b_}", "masks": f"{pinfo[tag][a_]['shire_mask']}/{pinfo[tag][b_]['shire_mask']}",
                          "measured_ln_ratio": r6(dm), "noise_threshold_ln": r6(thr), "beyond_noise": beyond,
                          "beyond_registered_tie": abs(dm) > rules["arms"][tag]["ties"]["cycles_ln"], "models": {}}
                    for mdl in ["v31", "v3"] + cands:
                        fa, fb = fx[tag][a_].get(mdl) or {}, fx[tag][b_].get(mdl) or {}
                        if not (fa.get("cw") and fb.get("cw")):
                            continue
                        dp = math.log(fa["cw"] / fb["cw"])
                        if 1e-9 < abs(dp) <= 1e-6:
                            p2.setdefault("pairs_predicted_in_rounding_band", []).append([tag, a_, b_, mdl, dp])
                        pr["models"][mdl] = {"predicted_ln_ratio": r6(dp), "orders": (None if abs(dp) <= 1e-9 else (dp * dm > 0))}
                    prs.append(pr)
            summ = {}
            for mdl in ["v31", "v3"] + cands:
                bn = [p_ for p_ in prs if p_["beyond_noise"] and mdl in p_["models"]]
                summ[mdl] = {"pairs_beyond_noise": len(bn), "ordered": sum(1 for p_ in bn if p_["models"][mdl]["orders"] is True),
                             "misordered": sum(1 for p_ in bn if p_["models"][mdl]["orders"] is False),
                             "cannot_order": sum(1 for p_ in bn if p_["models"][mdl]["orders"] is None)}
            spread = [math.log(M[tag][i]["cw"]) for i in ids]
            sets.append({"set": label, "points": ids, "measured_wall_cycles": {i: r6(M[tag][i]["cw"]) for i in ids},
                         "measured_spread_ln_max_min": r6(max(spread) - min(spread)), "pairs": prs, "summary": summ})
        p2["pairs"][tag] = sets

    # ---- PART 3: 'v3.1 + both terms' over every E215 point (REPORTED)
    p3 = {"stats": {}, "head_to_head": {}}
    groups = {"registered": ("P", "C", "R"), "posthoc": ("L", "S")}
    for gname, fams in groups.items():
        tp = [(t, [p["id"] for p in P["arms"][t]["points"] if p["family"] in fams]) for t in ARMS]
        p3["stats"][gname] = {"pooled": {m: stats_set(tp, m) for m in ("v31", "v3", "both")},
                              "per_arm": {t: {m: stats_set([(t, ids)], m) for m in ("v31", "v3", "both")} for t, ids in tp}}
        p3["head_to_head"][gname] = {"both vs v31": hh(tp, "both", "v31"), "both vs v3": hh(tp, "both", "v3")}
    tp_all = [(t, [p["id"] for p in P["arms"][t]["points"]]) for t in ARMS]
    p3["stats"]["all"] = {"pooled": {m: stats_set(tp_all, m) for m in ("v31", "v3", "both")}}
    p3["head_to_head"]["all"] = {"both vs v31": hh(tp_all, "both", "v31"), "both vs v3": hh(tp_all, "both", "v3")}

    # ---- self-check: this code's v3.1-vs-v2 and T7-vs-v3.1 head-to-heads equal the frozen scorer's h_pair
    agree = []
    for tag in ARMS:
        for gname, fams in groups.items():
            ref = sc.h_pair(M[tag], fc[tag], rules["arms"][tag], fams, "v31", "v2")
            ids = [p["id"] for p in P["arms"][tag]["points"] if p["family"] in fams]
            mine = h_cells(tag, ids, "v31", "v2", ("H1", "H2", "H3", "H4", "H5"))
            for q in ("H1", "H2", "H3", "H4", "H5"):
                dd = decide(mine[q], ("x", "y"))
                agree.append((ref[q].get("x_closer"), ref[q].get("y_closer"), ref[q].get("ties")) == (dd["candidate_closer"], dd["other_closer"], dd["ties"])
                             or (ref[q]["verdict"] == "NO DATA" and dd["verdict"] == "NO DATA"))
    res["checks"]["h_pair_self_check"] = {"agree": sum(agree), "of": len(agree)}
    # and this code's v3.1 cells equal the frozen scorer's E1-E4 and T1-T3 cells
    nce, worst = 0, 0.0
    for tag in ARMS:
        for gname, fams in groups.items():
            cells, _, _ = sc.score_group(tag, M[tag], fc[tag], rules, fams)
            for q in ("E1", "E2", "E3", "E4"):
                for c in cells[q]:
                    e = energy_errs(tag, c["point"], fx[tag][c["point"]]["v31"])
                    got = abs(e[q]) if (c.get("watts") and q in ("E1", "E2")) else e[q]
                    worst = max(worst, abs(got - c["err"]))
                    nce += 1
    res["checks"]["v31_cells_vs_frozen_scorer"] = {"cells": nce, "worst_abs_diff": worst}
    res["part1_gemmlnc"] = p1
    res["part2_contention_and_controls"] = p2
    res["part3_both_terms"] = p3
    res["measured"] = {t: {pid: {k: (r6(v[k]) if isinstance(v[k], float) else v[k]) for k in ("n_runs", "cw", "cm", "t", "W", "J", "Jrest", "prest", "die",
                                                                                              "family", "role", "loop", "arm", "format", "kind", "mask")}
                           for pid, v in sorted(M[t].items())} for t in ARMS}
    with open(os.path.join(OUT, "scores-terms-e215.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=False, default=lambda o: None)
    write_tables(OUT, res, fx, M, pinfo, cands)
    txt = summary(res)
    with open(os.path.join(OUT, "scores-terms-e215.txt"), "w") as fh:
        fh.write(txt + "\n")
    print(txt)


def write_tables(OUT, res, fx, M, pinfo, cands):
    p1 = res["part1_gemmlnc"]
    with open(os.path.join(OUT, "part1-gemmlnc-points.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "id", "token", "NB", "n_runs", "measured_wall_cycles", "measured_seconds", "measured_W_over_idle", "measured_p_rest_W", "model",
                    "W_frozen_own_t", "W_given_t", "err_W_given_t_pct", "err_J_over_idle_given_t_pct", "err_J_over_idle_t_forecast_pct",
                    "err_J_at_rest_given_t_pct", "err_J_at_rest_t_forecast_pct", "err_wall_cycles_pct", "err_seconds_pct"])
        for r in p1["points"]:
            for mdl, m in r["models"].items():
                w.writerow([r["arm"], r["id"], r["token"], r["NB"], r["n_runs"], r["measured"]["wall_cycles"], r["measured"]["seconds"],
                            r["measured"]["W_over_idle"], r["measured"]["p_rest"], mdl, m["W_frozen_own_t"], m["W_given_t"], m["err_W_given_t_pct"],
                            m["err_J_over_idle_given_t_pct"], m["err_J_over_idle_t_forecast_pct"], m["err_J_at_rest_given_t_pct"],
                            m["err_J_at_rest_t_forecast_pct"], m["err_wall_cycles_pct"], m["err_seconds_pct"]])
    p2 = res["part2_contention_and_controls"]
    with open(os.path.join(OUT, "part2-subset-points.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        mdls = ["v31", "v3"] + cands
        w.writerow(["arm", "id", "token", "mask", "shires", "n_runs", "measured_wall_cycles", "measured_seconds", "F1_factor"]
                   + [f"{m}_wall_cycles" for m in mdls] + [f"err_wall_{m}_pct" for m in mdls] + [f"err_seconds_{m}_pct" for m in mdls])
        for r in p2["subset_points"]:
            w.writerow([r["arm"], r["id"], r["token"], r["mask"], r["shires"], r["n_runs"], r["measured_wall_cycles"], r["measured_seconds"], r["F1_factor"]]
                       + [r["models"][m]["wall_cycles"] for m in mdls] + [r["models"][m]["err_wall_cycles_pct"] for m in mdls]
                       + [r["models"][m]["err_seconds_pct"] for m in mdls])
    with open(os.path.join(OUT, "part2-layout-pairs.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        mdls = ["v31", "v3"] + cands
        w.writerow(["arm", "set", "pair", "masks", "measured_ln_ratio", "noise_threshold_ln", "beyond_noise", "beyond_registered_tie"]
                   + [f"{m}_predicted_ln_ratio" for m in mdls] + [f"{m}_orders" for m in mdls])
        for tag, sets in p2["pairs"].items():
            for s in sets:
                for pr in s["pairs"]:
                    w.writerow([tag, s["set"], pr["pair"], pr["masks"], pr["measured_ln_ratio"], pr["noise_threshold_ln"], pr["beyond_noise"],
                                pr["beyond_registered_tie"]] + [(pr["models"].get(m) or {}).get("predicted_ln_ratio") for m in mdls]
                               + [(pr["models"].get(m) or {}).get("orders") for m in mdls])
    with open(os.path.join(OUT, "part3-all-points.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "id", "family", "reading", "loop", "token", "format", "kind", "mask", "n_runs", "measured_wall_cycles", "measured_counter_mean",
                    "measured_seconds", "measured_W_over_idle", "watts_point", "model", "wall_cycles", "seconds", "W_given_t", "err_wall_cycles_pct",
                    "err_counter_mean_pct", "err_seconds_pct", "err_W_given_t", "err_J_over_idle_given_t", "err_J_over_idle_t_forecast",
                    "err_J_at_rest_given_t_pct", "err_J_at_rest_t_forecast_pct", "energy_unit"])
        import score_e215 as sc
        for tag in ARMS:
            for pid in sorted(M[tag]):
                v = M[tag][pid]
                if v["role"] != "point":
                    continue
                watts = fx[tag][pid]["v31"]["W"] < sc.LOW or (v["W"] is not None and v["W"] < sc.LOW)
                for mdl in ("v31", "v3", "both"):
                    f = fx[tag][pid].get(mdl) or {}
                    Wg = Jg = None
                    if f.get("A") is not None and f.get("B") is not None and v["W"] is not None:
                        Wg, Jg = sc.given(f, v["cw"], v["t"])
                    def e(a_, b_):
                        return None if (a_ is None or not b_) else round(100 * (a_ / b_ - 1), 3)
                    if Wg is not None:
                        eW = round(v["W"] - Wg, 4) if watts else e(v["W"], Wg)
                        e1 = round(v["W"] - Wg, 4) if watts else e(v["J"], Jg)
                        e2 = round(v["W"] - f["W"], 4) if watts else e(v["J"], f["J"])
                        e3 = e(v["Jrest"], v["prest"] * v["t"] + Jg)
                        e4 = e(v["Jrest"], v["prest"] * f["t"] + f["J"])
                    else:
                        eW = e1 = e2 = e3 = e4 = None
                    w.writerow([tag, pid, v["family"], pinfo[tag][pid]["reading"], v["loop"], v["arm"], v["format"], v["kind"], v["mask"], v["n_runs"],
                                round(v["cw"], 4), round(v["cm"], 4), v["t"], None if v["W"] is None else round(v["W"], 4), watts, mdl,
                                None if not f.get("cw") else round(f["cw"], 4), f.get("t"), None if Wg is None else round(Wg, 4),
                                e(v["cw"], f.get("cw")) if v["time_scored"] else None, e(v["cm"], f.get("cm")) if v["time_scored"] else None,
                                e(v["t"], f.get("t")) if v["time_scored"] else None, eW, e1, e2, e3, e4, "W (measured - forecast)" if watts else "%"])


def summary(res):
    L = []
    p1 = res["part1_gemmlnc"]
    L.append("score-terms-e215 (Q231): the frozen candidate terms on E215's committed data - REPORTED (frozen before any E215 datum; scored after)")
    L.append(f"checks: posted sha256 {sum(1 for v in res['checks']['sha256'].values() if v.get('equal_to_post') or v.get('equal_to_SHA256SUMS'))} of "
             f"{len(res['checks']['sha256'])} equal; {res['checks']['e215_pins']}; h_pair self-check {res['checks']['h_pair_self_check']}; "
             f"v3.1 cells vs the frozen scorer {res['checks']['v31_cells_vs_frozen_scorer']}")
    L.append("PART 1, the gemmLnc term F3 (signed % = measured / forecast - 1; W over idle given t, J over idle given t / with t forecast, J at rest given t / t forecast):")
    for r in p1["points"]:
        m = r["models"]
        L.append(f"  {r['arm']} {r['id']} {r['token']} NB {r['NB']}: measured W {r['measured']['W_over_idle']:.3f} (wall {r['measured']['wall_cycles']:.1f}); "
                 + "; ".join(f"{k} W|t {m[k]['W_given_t']:.2f} ({m[k]['err_W_given_t_pct']:+.1f}%), J|t {m[k]['err_J_over_idle_given_t_pct']:+.1f}, "
                             f"J tf {m[k]['err_J_over_idle_t_forecast_pct']:+.1f}, Jr|t {m[k]['err_J_at_rest_given_t_pct']:+.1f}, Jr tf {m[k]['err_J_at_rest_t_forecast_pct']:+.1f}"
                             for k in ("v31", "v3", "lnc")))
        t = r["term"]
        L.append(f"      term: measured excess given t {t['measured_excess_over_v31_given_t_W']:+.2f} W vs term {t['term_given_t_W']:+.2f} W "
                 f"(energy an op step {t['measured_excess_energy_an_op_step_W_us']:.3f} vs {t['term_energy_an_op_step_W_us']:.3f} W us, ratio "
                 f"{t['measured_over_term']:.3f}); forms measured/predicted excess {t['forms_measured_over_predicted_excess']}; analog {r['analog_verify_lnc_W']}")
    for mdl in ("v31", "v3", "lnc", "lncF1", "lncF2", "lncF4"):
        s = p1["stats"][mdl]
        L.append(f"  rms over the 5 ({NAME[mdl]}): W|t {s['W_over_idle_given_t']['rms_pct']}% (bias {s['W_over_idle_given_t']['bias_pct']}), "
                 f"J|t {s['J_over_idle_given_t']['rms_pct']}, J tf {s['J_over_idle_t_forecast']['rms_pct']}, Jr|t {s['J_at_rest_given_t']['rms_pct']}, "
                 f"Jr tf {s['J_at_rest_t_forecast']['rms_pct']}")
    for k, hh_ in p1["head_to_head"].items():
        L.append(f"  sign test {k}: " + "; ".join(f"{q} {d['verdict']} ({d['candidate_closer']}/{d['other_closer']}/{d['ties']}, p {d.get('p_two_sided_REPORTED')})"
                                                   for q, d in hh_["pooled"].items()))
    for tw in p1["twins"]:
        L.append(f"  twin {tw['gemmLnc']}/{tw['twin']} ({tw['twin_token']}): twin W|t err {tw['twin_err_W_given_t_pct']}; W ratio {tw['ratio_W_gemmLnc_over_twin']}; "
                 f"wall ratio {tw['ratio_wall_cycles_gemmLnc_over_twin']}")
    p2 = res["part2_contention_and_controls"]
    L.append("PART 2, the contention term F1 and the controls on the 28 subset-mask points (wall cycles / seconds rms %, bias):")
    for mdl, s in p2["stats"].items():
        pa = p2["stats_per_arm"][mdl]
        L.append(f"  {NAME[mdl]}: pooled wall {s['wall_cycles']['rms_pct']} ({s['wall_cycles']['bias_pct']:+}) seconds {s['seconds']['rms_pct']} "
                 f"({s['seconds']['bias_pct']:+}); A wall {pa['A']['wall_cycles']['rms_pct']}, B wall {pa['B']['wall_cycles']['rms_pct']}")
    for k, hh_ in p2["head_to_head"].items():
        L.append(f"  sign test {k}: pooled " + "; ".join(f"{q} {d['verdict']} ({d['candidate_closer']}/{d['other_closer']}/{d['ties']}, p {d.get('p_two_sided_REPORTED')})"
                                                          for q, d in hh_["pooled"].items())
                 + " | A " + "; ".join(f"{q} {d['verdict']} ({d['candidate_closer']}/{d['other_closer']}/{d['ties']})" for q, d in hh_["per_arm"]["A"].items())
                 + " | B " + "; ".join(f"{q} {d['verdict']} ({d['candidate_closer']}/{d['other_closer']}/{d['ties']})" for q, d in hh_["per_arm"]["B"].items()))
    L.append(f"  full chip: {p2['full_chip']}")
    for tag, nz in p2["noise"].items():
        L.append(f"  noise {tag}: {nz}")
        for s in p2["pairs"][tag]:
            L.append(f"   set {s['set']}: spread ln {s['measured_spread_ln_max_min']}; pairs beyond noise / ordered / misordered / cannot: "
                     + "; ".join(f"{mdl} {v['pairs_beyond_noise']}/{v['ordered']}/{v['misordered']}/{v['cannot_order']}" for mdl, v in s["summary"].items()))
    p3 = res["part3_both_terms"]
    L.append("PART 3, 'v3.1 + both terms' over every E215 point (REPORTED):")
    for g in ("registered", "posthoc", "all"):
        for mdl, s in p3["stats"][g]["pooled"].items():
            L.append(f"  {g} pooled {NAME[mdl]}: wall {s['wall_cycles']['rms_pct']} (n {s['wall_cycles']['n']}), seconds {s['seconds']['rms_pct']}, "
                     f"W|t {s['W_over_idle_given_t']['rms_pct']} (n {s['W_over_idle_given_t']['n']}), J|t {s['J_over_idle_given_t']['rms_pct']}, "
                     f"J tf {s['J_over_idle_t_forecast']['rms_pct']}, Jr|t {s['J_at_rest_given_t']['rms_pct']}, Jr tf {s['J_at_rest_t_forecast']['rms_pct']}")
        for k, hh_ in p3["head_to_head"][g].items():
            L.append(f"  {g} sign test {k}: " + "; ".join(f"{q} {d['verdict']} ({d['candidate_closer']}/{d['other_closer']}/{d['ties']}, p "
                                                           f"{None if d.get('p_two_sided_REPORTED') is None else round(d['p_two_sided_REPORTED'], 4)})"
                                                           for q, d in hh_["pooled"].items()))
    return "\n".join(L)


if __name__ == "__main__":
    main()
