#!/usr/bin/env python3
"""E182 (Q153, E182.md's dated note 1): the desk checks behind the note's figures, from committed files only. No card. Every figure is
arithmetic on the registration's own frozen files or a POST HOC reading of committed data that existed before E182's registration; none
is a measurement of E182, and nothing here changes a rule, a forecast or a threshold.

  H  (the verifier's MINOR 3) the trains' forecast half-width under the REGISTERED statistic, t(0.975, n - 1) sd / sqrt(n) over units
     (E182.md section 5.1), against the z = 1.96 the sizing rule and section 0 quote; BASE and DOUBLED, from noise-e182.json's sigma_q and
     plan-e182.json's process counts; beside it power-e182.json's simulated median half-widths;
  L  (MINOR 4) which E182 kinds each forecast was fitted on: arm E's two lines (forecast-e182.json > arm_E_lines), M10's 959 rows
     (rows-m10.json) and M10-ACC's frozen fit's rows (rows-m10acc.json: M10's rows, pool 8 and E178's 40 kinds);
  G  (MINOR 5) the kinds checked against M10-ACC's frozen grid, and the two fp32 swap kinds' term from the predictor's own trace;
  B  (MINOR 6) the die reading (temp_c.minshire[0], whole degrees) at the start and the end of every kept run of E78's random anchors
     int8.full and fp32.randn in E178's committed passes: the end is where a train's first process starts (block_e182.sh runs the train
     right after its opening random anchor), post hoc;
  R  (MINOR 8) E182-R-int8's false-PASS rate at its registered line 0.4421 for n = 20, by 2,000,000 random permutations (numpy, seed
     18282), and the null's 97.5% point;
  Q  (MINOR 9) the float quad sd split by format, under noise_e182.py's own rule (it pools fp32 and fp16), post hoc.

    /usr/bin/python3 -B tools/claims-v3/e182/note1_checks_e182.py [--out tools/claims-v3/e182/note1-checks-e182.json]
SPDX-License-Identifier: Apache-2.0
"""
import bisect
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "noise"))
import e182_stats as S  # noqa: E402
import noise_e182 as NZ  # noqa: E402  (its rules and readers, unchanged)

E178 = os.path.join(TOP, "docs/reports/data/2026-11-06-e178-one-number-aifoundry3")
M10ROWS = "docs/reports/data/2026-11-04-q142m-m10/rows-m10.json"
ACCROWS = "docs/reports/data/2026-11-07-q153-m10acc/rows-m10acc.json"
INPUTS = ["tools/claims-v3/e182/forecast-e182.json", "tools/claims-v3/e182/plan-e182.json", "tools/claims-v3/e182/power-e182.json",
          "tools/claims-v3/e182/noise/noise-e182.json", "tools/claims-v3/e182/kinds-e182.json", M10ROWS, ACCROWS]
CHECKS = []


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def check(ok, what):
    CHECKS.append((bool(ok), what))
    print(("PASS " if ok else "FAIL ") + what, flush=True)


def load(rel):
    return json.load(open(os.path.join(TOP, rel)))


def halfwidths():
    nz, pl, pw = load(INPUTS[3]), load(INPUTS[1]), load(INPUTS[2])
    sig = nz["sigma_q_w"]
    out = {}
    for ty, key in (("int8", "int8"), ("fp32", "float")):
        tr = [t for t in pl["trains"] if t["type"] == ty]
        procs = tr[0]["processes"]
        units = procs // 2
        quads = procs * 3
        for case, m in (("BASE", 1.0), ("DOUBLED", 2.0)):
            sd_unit = m * sig[key] / math.sqrt(6)
            out[f"{ty}|{case}"] = {"sigma_q_w": m * sig[key], "processes": procs, "units": units, "quads": quads,
                                   "z_halfwidth_w": 1.96 * sd_unit / math.sqrt(units),
                                   "t_halfwidth_w": S.t975(units - 1) * sd_unit / math.sqrt(units), "t975": S.t975(units - 1)}
    med = {nm: c["median_halfwidth_w"] for nm, c in pw["cases"].items() if nm.startswith("T1|") and "median_halfwidth_w" in c}
    return out, med


def labels():
    F = load(INPUTS[0])
    ks = F["kinds"]
    e182 = {"int8": sorted(k for k in ks if k.startswith("int8.")), "fp32": sorted(k for k in ks if k.startswith("fp32."))}
    fitE = {ty: sorted(set(F["arm_E_lines"][ty]["kinds"]) & set(e182[ty])) for ty in ("int8", "fp32")}
    m10 = load(M10ROWS)
    fitP = sorted({r["kind"] for r in m10 if r.get("kind") in ks})
    m10p = {k: sorted({f"{r['exp']} {r['card']}" for r in m10 if r.get("kind") == k}) for k in fitP}
    acc = load(ACCROWS)
    rows = acc["rows"] if isinstance(acc, dict) and "rows" in acc else acc
    fitA = sorted({r.get("kind") for r in rows if isinstance(r, dict) and r.get("kind") in ks})
    return {"e182_kinds": e182, "arm_E_fit_kinds_among_e182": fitE, "m10_fit_kinds_among_e182": fitP, "m10_fit_rows_of_them": m10p,
            "m10acc_frozen_fit_kinds_among_e182": fitA,
            "blind_for_E": {ty: sorted(set(e182[ty]) - set(fitE[ty])) for ty in e182},
            "blind_for_P": {ty: sorted(set(e182[ty]) - set(fitP)) for ty in e182},
            "blind_for_PACC": {ty: sorted(set(e182[ty]) - set(fitA)) for ty in e182}}


def grid():
    F = load(INPUTS[0])
    g = F["check_ACC_against_grid"]
    checked = sorted(k for k, v in g.items() if v.get("abs_diff_w_a3") is not None)
    own = sorted(k for k, v in g.items() if v.get("abs_diff_w_a3") is None)
    terms = {k: F["kinds"][k]["PACC_w"]["a3"] - F["kinds"][k]["P_w"]["a3"] for k in own}
    return {"checked_against_grid": len(checked), "of": len(g), "max_abs_diff_w": max(g[k]["abs_diff_w_a3"] for k in checked),
            "not_in_grid": own, "their_term_w_a3": terms}


def band():
    out = {}
    for item in ("int8.full", "fp32.randn"):
        starts, ends, rise = [], [], []
        for p in NZ.PASSES:
            pd = os.path.join(E178, "aifoundry3", "e178", p)
            tel = []
            with gzip.open(os.path.join(pd, "telemetry.jsonl.gz"), "rt") as f:
                for line in f:
                    try:
                        o = json.loads(line)
                    except ValueError:
                        continue
                    ms = ((o.get("temp_c") or {}).get("minshire") or [None])[0]
                    if isinstance(o.get("t_ms"), (int, float)) and isinstance(ms, (int, float)):
                        tel.append((int(o["t_ms"]), float(ms)))
            tel.sort()
            ts = [t for t, _ in tel]
            runs = {}
            for line in open(os.path.join(pd, "runs.jsonl")):
                r = json.loads(line)
                if r.get("item") == item and r.get("ok", True):
                    runs.setdefault(r["pos"], []).append(r)
            for pos, L in runs.items():
                real = sorted((r for r in L if r["launch"] >= 0), key=lambda r: r["launch"])
                if not real:
                    continue
                i0 = bisect.bisect_right(ts, real[0]["t_start_ms"]) - 1
                j0 = bisect.bisect_left(ts, real[-1]["t_end_ms"])
                win = [c for t, c in tel[j0:] if t <= real[-1]["t_end_ms"] + 1000]
                if i0 < 0 or not win:
                    continue
                starts.append(tel[i0][1])
                ends.append(max(win))
                rise.append(max(win) - tel[i0][1])
        out[item] = {"runs": len(starts), "start_c": {"min": min(starts), "median": st.median(starts), "max": max(starts)},
                     "end_c": {"min": min(ends), "median": st.median(ends), "max": max(ends)},
                     "rise_c": {"min": min(rise), "median": st.median(rise), "max": max(rise)}}
    return out


def spearman():
    import numpy as np
    n, line, draws = 20, 0.4421, 2_000_000
    rng = np.random.default_rng(18282)
    idx = np.arange(n)
    hits = 0
    rhos = []
    for _ in range(draws // 200_000):
        perm = np.argsort(rng.random((200_000, n)), axis=1)
        d = ((perm - idx) ** 2).sum(axis=1)
        rho = 1.0 - 6.0 * d / (n * (n * n - 1))
        hits += int((rho >= line).sum())
        rhos.append(rho)
    allr = np.sort(np.concatenate(rhos))
    p = hits / draws
    return {"n": n, "line": line, "draws": draws, "seed": 18282, "p_rho_ge_line": p, "se": math.sqrt(p * (1 - p) / draws),
            "null_975_point": float(allr[int(0.975 * draws)]),
            "line_as_sum_d2": "rho = 1 - 6 D / (n (n^2 - 1)); rho >= 0.4421 is D <= 742 (rho 0.44211); the 97.5% point is D = 738 (0.44511)"}


def quads_by_format():
    by = {"int8": [], "fp32": [], "fp16": []}
    for p in NZ.PASSES:
        pd = os.path.join(E178, "aifoundry3", "e178", p)
        tel, _ = NZ.load_tel(os.path.join(pd, "telemetry.jsonl.gz"))
        ts = [t for t, _ in tel]
        runs = {}
        for line in open(os.path.join(pd, "runs.jsonl")):
            r = json.loads(line)
            if r.get("ok", True):
                runs.setdefault((r["pos"], r["item"]), []).append(r)
        for (pos, item), L in runs.items():
            k = NZ.klass(item)
            if k not in ("int8_one_number", "float_one_number"):
                continue
            real = [r for r in sorted(L, key=lambda r: r["launch"]) if r["launch"] >= 0]
            rd = {}
            for r in real:
                v, _ = NZ.launch_reading(ts, tel, r["t_start_ms"], r["t_end_ms"])
                if v is not None:
                    rd[r["launch"]] = v
            for q in NZ.QUADS:
                if all(i in rd for i in q):
                    by[item.split(".", 1)[0]].append((rd[q[1]] + rd[q[2]] - rd[q[0]] - rd[q[3]]) / 2)
    out = {ty: {"quads": len(v), "sd_w": st.stdev(v)} for ty, v in by.items()}
    out["float_pooled"] = {"quads": len(by["fp32"]) + len(by["fp16"]), "sd_w": st.stdev(by["fp32"] + by["fp16"])}
    return out


def main():
    outp = os.path.join(HERE, "note1-checks-e182.json")
    if "--out" in sys.argv:
        outp = sys.argv[sys.argv.index("--out") + 1]
    res = {"_what": "E182.md's dated note 1: the desk checks behind its figures (note1_checks_e182.py); arithmetic on frozen files and "
                    "POST HOC readings of committed data; nothing here is an E182 measurement",
           "inputs_sha256": {rel: sha(rel) for rel in INPUTS}}
    hw, med = halfwidths()
    res["H_halfwidths"] = {"registered_statistic": hw, "power_e182_medians": med}
    check(abs(hw["int8|BASE"]["z_halfwidth_w"] - 0.0049) < 0.00005 and abs(hw["fp32|BASE"]["z_halfwidth_w"] - 0.0049) < 0.00005,
          f"H the quoted +-0.0049 W is z: int8 {hw['int8|BASE']['z_halfwidth_w']:.5f}, fp32 {hw['fp32|BASE']['z_halfwidth_w']:.5f}")
    check(0.0050 < hw["int8|BASE"]["t_halfwidth_w"] < 0.0052 and 0.0050 < hw["fp32|BASE"]["t_halfwidth_w"] < 0.0052,
          f"H the registered statistic's t half-width: int8 {hw['int8|BASE']['t_halfwidth_w']:.5f} (t {hw['int8|BASE']['t975']:.4f}, "
          f"{hw['int8|BASE']['units']} units), fp32 {hw['fp32|BASE']['t_halfwidth_w']:.5f} ({hw['fp32|BASE']['units']} units); DOUBLED "
          f"{hw['int8|DOUBLED']['t_halfwidth_w']:.5f} and {hw['fp32|DOUBLED']['t_halfwidth_w']:.5f}")
    lb = labels()
    res["L_labels"] = lb
    check(lb["arm_E_fit_kinds_among_e182"]["int8"] == sorted(["int8.ones", "int8.neg_ones", "int8.e178_v4", "int8.e178_v5", "int8.e178_a4_b5",
                                                                "int8.e178_a5_b4"]) and len(lb["blind_for_E"]["int8"]) == 14,
          f"L arm E's int8 line was fitted on 6 of E182's 20 int8 kinds {lb['arm_E_fit_kinds_among_e182']['int8']}; blind for 14")
    check(lb["m10_fit_kinds_among_e182"] == ["int8.neg_ones", "int8.ones"],
          f"L M10's fit rows hold 2 of E182's 24 kinds: {lb['m10_fit_rows_of_them']}")
    check(sorted(lb["arm_E_fit_kinds_among_e182"]["fp32"]) == ["fp32.e178_v4", "fp32.e178_v5"],
          f"L arm E's fp32 line was fitted on 2 of E182's 4 fp32 kinds: {lb['arm_E_fit_kinds_among_e182']['fp32']}")
    check(set(lb["m10acc_frozen_fit_kinds_among_e182"]) == set(lb["arm_E_fit_kinds_among_e182"]["int8"] + lb["arm_E_fit_kinds_among_e182"]["fp32"]),
          f"L M10-ACC's frozen fit holds the same 8 kinds (E178's, and M10's ones and neg_ones): {lb['m10acc_frozen_fit_kinds_among_e182']}")
    g = grid()
    res["G_grid"] = g
    check(g["checked_against_grid"] == 22 and g["of"] == 24 and all(abs(v - 0.0011315) < 1e-6 for v in g["their_term_w_a3"].values()),
          f"G {g['checked_against_grid']} of {g['of']} kinds checked against the grid (largest difference {g['max_abs_diff_w']:.1e} W); "
          f"the two swap kinds' term from the predictor's own trace: {', '.join(f'{v:.7f}' for v in g['their_term_w_a3'].values())} W")
    b = band()
    res["B_band"] = b
    check(b["int8.full"]["runs"] >= 8 and b["fp32.randn"]["runs"] >= 8,
          f"B the random anchors' die readings, post hoc: int8.full {b['int8.full']['runs']} runs, start median {b['int8.full']['start_c']['median']} "
          f"C, end median {b['int8.full']['end_c']['median']} C (max {b['int8.full']['end_c']['max']}); fp32.randn {b['fp32.randn']['runs']} runs, "
          f"start {b['fp32.randn']['start_c']['median']}, end {b['fp32.randn']['end_c']['median']} (max {b['fp32.randn']['end_c']['max']})")
    r = spearman()
    res["R_spearman"] = r
    check(0.0250 < r["p_rho_ge_line"] < 0.0270, f"R P(rho >= 0.4421 | n 20, no association) = {r['p_rho_ge_line']:.5f} (se {r['se']:.5f}); "
          f"the null's 97.5% point {r['null_975_point']:.5f}")
    q = quads_by_format()
    res["Q_quads"] = q
    nz = load(INPUTS[3])["sigma_q_w"]
    check(round(q["float_pooled"]["sd_w"], 5) == nz["float"] and round(q["int8"]["sd_w"], 5) == nz["int8"],
          f"Q noise_e182's rule reproduced: int8 {q['int8']['sd_w']:.5f} ({q['int8']['quads']}), floats pooled {q['float_pooled']['sd_w']:.5f} "
          f"({q['float_pooled']['quads']}); split: fp32 {q['fp32']['sd_w']:.5f} ({q['fp32']['quads']}), fp16 {q['fp16']['sd_w']:.5f} ({q['fp16']['quads']})")
    res["checks"] = [{"ok": ok, "what": w} for ok, w in CHECKS]
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    open(outp, "a").write("\n")
    k = sum(ok for ok, _ in CHECKS)
    print(f"NOTE1-CHECKS-E182 {k} of {len(CHECKS)} {'PASS' if k == len(CHECKS) else 'FAIL'}")
    return 0 if k == len(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
