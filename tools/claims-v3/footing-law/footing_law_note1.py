#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(a), the footing law's dated note 1: FL2's check and FL5's checks read in ONE die coordinate (post hoc reads of committed data).

FL1 is a law in the firmware's whole-degree die reading (temp_c.minshire[0]). E97's law, the one the heat chain closes through, is in
the 34-sensor mean of the raw codes (E97's code_to_c). FOOTING-LAW.md and footing_law.py's selftest compared the two at the same
number of degrees. This file reads them in one coordinate:
  (1) E97's rests (pass p9720, its marks of kind "rest", R0-R2; rule F: from 20 s after each rest's start, minion clock 600 MHz, a
      clean 34-code record, as rederive_e97.py selects them) per whole FIRMWARE degree, by FL1's own method (footing_law._quad:
      whole degrees with at least 100 samples, a quadratic weighted by the samples), inside FL1's aifoundry3 band (52-66 C), and
      over every such degree; its slope against FL1's at 52-62 C;
  (2) the offset, the 34-sensor mean less the firmware reading, over the same samples: the mean and per firmware degree; and E97's
      committed law evaluated at T + offset(T), against FL1 at T;
  (3) FL1's own sources apart, on one sensor and one method: E44's three September cycles alone against E71's six October cycles
      alone (the quasi-static law's between-session spread);
  (4) FL2's registered line (0.01 W/C over 55-62 C) per degree, in one coordinate; the differences' rms over 55-62 C and 52-58 C
      beside the rms of FL1's two sources apart, and FL1's bootstrap half-width;
  (5) FL5(c)'s estimator, as dated note 1 fixes it, dry-run on E97's committed rests (seen data; a check of the check's
      specification, not a test of the law): a straight line weighted by the samples through the per-degree means of the rests'
      firmware degrees inside the band with at least 100 samples, against the same estimator applied to FL1's law at the same
      degrees with the same weights;
  (6) FL5(a), as dated note 1 fixes it, for E171 and E172 (seen data): k_s against FL1's bootstrap interval at T_mid (footing_law's
      bootstrap, 2,000 draws over cycles, seed 145, evaluated also at T_mid), and on aifoundry3 against (1) at T_mid.
Reads committed files only; imports footing_law.py (the registration's own code) for FL1's tables, method and bootstrap.
Of each cycle's marks it reads the cool_start mark alone (through footing_law.raw_cycle).

    python3 -B footing_law_note1.py <lab repo top> <out.json>
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import sys

import numpy as np

TOP = sys.argv[1]
sys.path.insert(0, os.path.join(TOP, "tools/claims-v3/footing-law"))
import footing_law as fl  # noqa: E402  (the registration's own code)

E97_PASS = "docs/reports/data/2026-11-01-e97-heat-low-power-steady/aifoundry3/e97/p9720"
G_TS, H_TS, CAL5 = 57400, 249400, 4096       # E97's code_to_c, as smoke_gate_e176.py has it
DEG = (52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def e97_rest_samples(top):
    d = os.path.join(top, E97_PASS)
    rests = [json.loads(x) for x in open(os.path.join(d, "marks.jsonl")) if x.startswith("{") and '"rest"' in x]
    rests = [r for r in rests if r.get("kind") == "rest"]
    fw, m34, W = [], [], []
    with gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                s = json.loads(line)
            except ValueError:
                continue
            t = s.get("t_ms")
            if t is None or (s.get("mhz") or {}).get("minion") != 600:
                continue
            if not any(r["t_start_ms"] + 20000 <= t < r["t_end_ms"] for r in rests):
                continue
            pv = s.get("pvt") or {}
            cs = pv.get("c") or []
            if pv.get("st") != 0 or pv.get("f") or len(cs) != 34:
                continue
            fw.append(float(s["temp_c"]["minshire"][0]))
            m34.append(sum(code_to_c(c) for c in cs) / 34.0)
            W.append(float(s["board_w"]))
    return [r.get("name") for r in rests], np.array(fw), np.array(m34), np.array(W)


def table(fw, W):
    """footing_law's table form: per whole degree the mean board W and the dwell (samples x 0.1 s, so _quad's weight = samples)."""
    pdw, pds = {}, {}
    for t in sorted(set(fw.tolist())):
        q = fw == t
        pdw[str(int(t))] = float(W[q].mean())
        pds[str(int(t))] = round(float(q.sum()) * 0.1, 1)
    return pdw, pds


def slope(q, T):
    return 2 * q[0] * T + q[1]


def wline_points(Ts, Ws, ns):
    T, Wv, n = np.asarray(Ts, float), np.asarray(Ws, float), np.asarray(ns, float)
    mx = (n * T).sum() / n.sum()
    my = (n * Wv).sum() / n.sum()
    return float((n * (T - mx) * (Wv - my)).sum() / (n * (T - mx) ** 2).sum()), float(mx)


def boot_at(tabs, lo, hi, at):
    """footing_law.law's bootstrap (2,000 draws over cycles, seed 145), evaluated at the points `at` (same draws)."""
    rng = np.random.default_rng(145)
    bs = {x: [] for x in at}
    for _ in range(2000):
        cc, _ = fl._quad([tabs[i] for i in rng.integers(0, len(tabs), len(tabs))], lo, hi)
        if cc is not None:
            for x in at:
                bs[x].append(2 * cc[0] * x + cc[1])
    return {str(x): [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for x, v in bs.items()}


def main():
    out_path = sys.argv[2]
    res = {"what": "Q145(a) footing law, dated note 1: FL2 and FL5 in one die coordinate (post hoc reads of committed data)"}
    lawj = json.load(open(os.path.join(TOP, "tools/claims-v3/footing-law/footing-law.json")))["laws"]
    qa3 = lawj["aifoundry3"]["quad_w"]
    lo, hi = fl.CARDS["aifoundry3"]["band"]
    # (1) E97's rests on the firmware degree, FL1's method
    names, fw, m34, W = e97_rest_samples(TOP)
    pdw, pds = table(fw, W)
    q_band, (Tb, Wb, nb) = fl._quad([(pdw, pds)], lo, hi)
    q_all, (Ta, Wa, na) = fl._quad([(pdw, pds)], -999, 999)
    res["1_E97_rests_on_firmware_degree"] = {
        "rests": names, "samples": int(len(W)), "degrees_band": [int(Tb.min()), int(Tb.max())], "degrees_all": [int(Ta.min()), int(Ta.max())],
        "quad_band_52_66": [float(x) for x in q_band], "quad_all_degrees": [float(x) for x in q_all],
        "slope_band": {str(T): slope(q_band, T) for T in DEG}, "slope_all": {str(T): slope(q_all, T) for T in DEG},
        "FL1_slope": {str(T): slope(qa3, T) for T in DEG},
        "band_minus_FL1": {str(T): slope(q_band, T) - slope(qa3, T) for T in DEG},
        "all_minus_FL1": {str(T): slope(q_all, T) - slope(qa3, T) for T in DEG},
        "level_W_at_58": {"FL1": qa3[0] * 58 * 58 + qa3[1] * 58 + qa3[2], "E97_rests_fw_band": q_band[0] * 58 * 58 + q_band[1] * 58 + q_band[2],
                          "E97_committed_law_at_the_number_58": fl.E97[0] * 58 * 58 + fl.E97[1] * 58 + fl.E97[2]}}
    # (2) the offset, and E97's committed law at T + offset(T)
    off = m34 - fw
    by = {}
    for t in sorted(set(fw.tolist())):
        q = fw == t
        if q.sum() >= 100:
            by[str(int(t))] = float(off[q].mean())
    k97 = lambda T: 2 * fl.E97[0] * T + fl.E97[1]
    res["2_offset_34_minus_firmware"] = {
        "mean_over_samples": float(off.mean()), "by_firmware_degree": by,
        "range_by_degree": [min(by.values()), max(by.values())],
        "E97_law_at_T_plus_offset_minus_FL1": {str(T): k97(T + by[str(T)]) - slope(qa3, T) for T in DEG if str(T) in by},
        "E97_law_at_the_same_number_minus_FL1": {str(T): k97(T) - slope(qa3, T) for T in DEG}}
    # (3) FL1's sources apart: E44 (Sep) alone, E71 (Oct) alone
    t44 = fl.tables(TOP, fl.E71 + "/sep-p1p3.json")
    t71 = fl.tables(TOP, fl.E71 + "/slopes.json")
    q44, _ = fl._quad(t44, lo, hi)
    q71, _ = fl._quad(t71, lo, hi)
    res["3_FL1_sources_apart"] = {
        "E44_cycles": len(t44), "E71_cycles": len(t71),
        "E44_slope": {str(T): slope(q44, T) for T in DEG}, "E71_slope": {str(T): slope(q71, T) for T in DEG},
        "E71_minus_E44": {str(T): slope(q71, T) - slope(q44, T) for T in DEG}}
    # (4) FL2's line, per degree, in one coordinate (the band fit is FL1's method exactly)
    res["4_FL2_line_0.01_one_coordinate"] = {
        str(T): {"diff_band": res["1_E97_rests_on_firmware_degree"]["band_minus_FL1"][str(T)],
                 "diff_all": res["1_E97_rests_on_firmware_degree"]["all_minus_FL1"][str(T)],
                 "within_0.01_band": abs(res["1_E97_rests_on_firmware_degree"]["band_minus_FL1"][str(T)]) <= 0.01,
                 "within_0.01_all": abs(res["1_E97_rests_on_firmware_degree"]["all_minus_FL1"][str(T)]) <= 0.01,
                 "between_sessions_E71_minus_E44": res["3_FL1_sources_apart"]["E71_minus_E44"][str(T)]}
        for T in range(55, 63)}
    rmsf = lambda d_, lo_, hi_: float(np.sqrt(np.mean([d_[str(T)] ** 2 for T in range(lo_, hi_ + 1)])))
    res["4b_rms_and_bootstrap"] = {
        f"{a}-{b}": {"rms_band_minus_FL1": rmsf(res["1_E97_rests_on_firmware_degree"]["band_minus_FL1"], a, b),
                     "rms_all_minus_FL1": rmsf(res["1_E97_rests_on_firmware_degree"]["all_minus_FL1"], a, b),
                     "rms_E71_minus_E44": rmsf(res["3_FL1_sources_apart"]["E71_minus_E44"], a, b)} for a, b in ((55, 62), (52, 58))}
    res["4b_rms_and_bootstrap"]["FL1_boot95_halfwidth"] = {
        x: (lawj["aifoundry3"]["slope_ci95"][x][1] - lawj["aifoundry3"]["slope_ci95"][x][0]) / 2 for x in ("55", "58", "62")}
    # (5) FL5(c)'s corrected estimator, dry-run on E97's rests: degrees inside [52, 58] with >= 100 samples
    pts = [(int(t), pdw[t], round(pds[t] / 0.1)) for t in pdw if 52 <= int(t) <= 58 and round(pds[t] / 0.1) >= 100]
    pts.sort()
    Ts, Ws, ns = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
    k_obs, Tw = wline_points(Ts, Ws, ns)
    k_law, _ = wline_points(Ts, [qa3[0] * T * T + qa3[1] * T + qa3[2] for T in Ts], ns)
    res["5_FL5c_dry_run_on_E97_rests"] = {
        "degrees": Ts, "samples": ns, "weighted_mean_T_fw": Tw, "slope_rests": k_obs, "slope_FL1_same_estimator": k_law,
        "diff": k_obs - k_law, "line": 0.02, "reads": "PASS" if abs(k_obs - k_law) <= 0.02 else "FAIL",
        "note": "seen data (E97 was read before the rule): a check of the corrected estimator's specification, never a test of the law"}
    # (6) FL5(a) for E171 and E172 (seen data)
    res["6_FL5a"] = {}
    for run, card in (("E171", "aifoundry3"), ("E172", "aifoundry1c1")):
        kj = json.load(open(os.path.join(TOP, "tools/claims-v3/footing-law", f"k-{run.lower()}.json")))
        tm, ks = kj["T_mid"], kj["k_w_per_c"]
        tabs = fl.card_tables(TOP, card)
        blo, bhi = fl.CARDS[card]["band"]
        ci = boot_at(tabs, blo, bhi, (tm,))[str(tm)]
        row = {"T_mid_fw": tm, "k_s": ks, "FL1_boot95_at_T_mid": ci, "inside": ci[0] <= ks <= ci[1]}
        if card == "aifoundry3":
            row["E97_rests_fw_band_at_T_mid"] = slope(q_band, tm)
            row["k_s_minus_E97_rests_fw"] = ks - slope(q_band, tm)
            row["as_registered_E97_committed_law_at_the_number"] = k97(tm)
        res["6_FL5a"][run] = row
    json.dump(res, open(out_path, "w"), indent=1, sort_keys=True, default=lambda o: o.item())
    r1, r2, r3 = res["1_E97_rests_on_firmware_degree"], res["2_offset_34_minus_firmware"], res["3_FL1_sources_apart"]
    print(f"(1) E97 rests {r1['samples']} samples, firmware degrees {r1['degrees_all']}; band fit minus FL1 at 55-62:",
          [round(r1["band_minus_FL1"][str(T)], 4) for T in range(55, 63)], "; all-degree fit:", [round(r1["all_minus_FL1"][str(T)], 4) for T in range(55, 63)])
    print(f"(2) 34-sensor mean minus firmware: mean {r2['mean_over_samples']:.3f} C, by degree {r2['range_by_degree'][0]:.3f}-{r2['range_by_degree'][1]:.3f} C;"
          " E97's law at T + offset minus FL1 at 55-62:", [round(v, 4) for k, v in r2["E97_law_at_T_plus_offset_minus_FL1"].items() if 55 <= int(k) <= 62])
    print("(3) E71 alone minus E44 alone at 55-62:", [round(r3["E71_minus_E44"][str(T)], 4) for T in range(55, 63)])
    print("(4) FL2's 0.01 line, one coordinate, band fit:", {T: v["within_0.01_band"] for T, v in res["4_FL2_line_0.01_one_coordinate"].items()})
    print("(4b)", {k: ({kk: round(vv, 4) for kk, vv in v.items()}) for k, v in res["4b_rms_and_bootstrap"].items()})
    r5 = res["5_FL5c_dry_run_on_E97_rests"]
    print(f"(5) FL5(c) dry run on E97's rests, degrees {r5['degrees'][0]}-{r5['degrees'][-1]}: rests {r5['slope_rests']:.4f}, FL1 same estimator "
          f"{r5['slope_FL1_same_estimator']:.4f}, diff {r5['diff']:+.4f} -> {r5['reads']} (seen data)")
    for run, row in res["6_FL5a"].items():
        print(f"(6) {run}: k_s {row['k_s']:.4f} at T_mid {row['T_mid_fw']}; FL1 boot95 {[round(x, 4) for x in row['FL1_boot95_at_T_mid']]} inside {row['inside']}"
              + (f"; E97 rests (firmware) {row['E97_rests_fw_band_at_T_mid']:.4f}, k_s minus it {row['k_s_minus_E97_rests_fw']:+.4f}" if "E97_rests_fw_band_at_T_mid" in row else ""))


if __name__ == "__main__":
    main()
