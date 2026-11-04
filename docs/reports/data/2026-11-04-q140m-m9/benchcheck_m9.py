#!/usr/bin/env python3
"""Q140(m): M9-REGISTRATION.md section 8, the bench check of the launch-shape term at four base words (bench only; it never changes M9).

16 fp32 tiles (A = 1.0; B = w with bit k flipped in columns 8-15; w in 1/3, E79's and E102's 0x3FBD207C, E67's 0x3FBBC9E4, pi; k in
12, 17, 20, 21), counted by Q133(b)'s bench build at the nine midpoints of ninths of a 0.5 s launch (bench-check/counts-cal.json; the
bench's three launch points are three of the nine). Per tile: m3 = the mean whole-VPU nets_map of the three points the bench uses,
m9 = the mean of all nine, lq1 = the first point minus the mean of the other two (minus fp32 zeros', as fit_m9.lq_shape); per stage
the same. alpha = sum((m3 - m9) lq1) / sum(lq1^2). Registered expectation: alpha > 0. Then, since M9 did not keep lq1 (post hoc,
labelled): lq1's price in the form that holds every float candidate, fitted on all of M9's rows, beside the bench's own correction
-rate x sum_stage price_s (m3_s - m9_s) with M9's frozen float prices, per tile.

    python3 benchcheck_m9.py
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m9 as M9  # noqa: E402
import numpy as np  # noqa: E402

BC = os.path.join(HERE, "bench-check")
_CC = {}
STAGES = ("multiplier", "adder_norm", "lane_operand_bus", "exponent", "operand", "control", "vpu_sequencer", "result", "c_regfile", "other")


def main():
    c = json.load(open(os.path.join(BC, "counts-cal.json")))["rows"]
    man = {m["name"]: m for m in json.load(open(os.path.join(BC, "cal-tiles.json")))["tiles"]}
    std = [int(0.5 * 600e6 / 546 * f) for f in (1 / 6, 1 / 2, 5 / 6)]
    zr = M9.zeros_rows()
    z_lq = M9.lq_shape(zr["fp32"])
    m9 = json.load(open(os.path.join(HERE, "m9.json")))["families"]["float"]
    price = dict(zip(m9["terms"], m9["coef_J"]))
    rate = M9.F.RATE["fp32"]
    out = {"_note": "Q140(m) benchcheck_m9.py: M9-REGISTRATION.md section 8; bench only", "standard_points": std, "tiles": {}}
    L = ["Q140(m) bench check of the launch-shape term (M9-REGISTRATION.md section 8)", "",
         f"{'tile':18s} {'word':>10s} bit {'m3 nets':>10s} {'m9 nets':>10s} {'m3-m9':>9s} {'lq1':>10s}  bench correction W"]
    xs, ys = [], []
    for name in sorted(c, key=lambda k: (man[k]["base_word"], man[k]["bit"])):
        r = c[name]
        pts = sorted(r["points"], key=lambda p: p["n0"])
        n0 = [p["n0"] for p in pts]
        assert len(pts) == 9 and all(s in n0 for s in std), (name, n0)
        p3 = [p for p in pts if p["n0"] in std]
        net = lambda p: p["vpu"]["nets_map"]  # noqa: E731
        m3 = float(np.mean([net(p) for p in p3]))
        mm = float(np.mean([net(p) for p in pts]))
        lq = float(net(p3[0]) - 0.5 * (net(p3[1]) + net(p3[2]))) - z_lq
        st = {s: (float(np.mean([p["vpu"]["by_stage"][s] for p in p3])) - float(np.mean([p["vpu"]["by_stage"][s] for p in pts]))) for s in STAGES}
        # the bench's own correction in W at M9's frozen float prices: core stages at mult / add32, bus at bus, the rest at rest
        corr = -rate * (price["mult"] * st["multiplier"] + price["add32"] * st["adder_norm"] + price["bus"] * st["lane_operand_bus"]
                        + price["rest"] * sum(st[s] for s in STAGES if s not in ("multiplier", "adder_norm", "lane_operand_bus"))
                        + price.get("xstage", 0.0) * st["exponent"])
        out["tiles"][name] = {"base_word": man[name]["base_word"], "bit": man[name]["bit"], "m3_nets": m3, "m9_nets": mm,
                              "m3_minus_m9_nets": m3 - mm, "lq1": lq, "m3_minus_m9_by_stage": st, "bench_correction_w": corr,
                              "points_nets": [net(p) for p in pts], "check_mismatch": r["mean"].get("check_mismatch")}
        xs.append(lq)
        ys.append(m3 - mm)
        L.append(f"{name:18s} {man[name]['base_word']:>10s} {man[name]['bit']:3d} {m3:10.0f} {mm:10.0f} {m3 - mm:+9.0f} {lq:+10.0f}  {corr:+.3f}")
    xs, ys = np.array(xs), np.array(ys)
    alpha = float(np.sum(xs * ys) / np.sum(xs * xs))
    r_ = float(np.corrcoef(xs, ys)[0, 1])
    resid = ys - alpha * xs
    out["alpha"] = alpha
    out["corr_lq1_vs_m3_minus_m9"] = r_
    out["rms_m3_minus_m9_nets"] = float(np.sqrt(np.mean(ys ** 2)))
    out["rms_residual_after_alpha_nets"] = float(np.sqrt(np.mean(resid ** 2)))
    out["expectation"] = "alpha > 0 (registered)"
    out["verdict"] = "alpha > 0" if alpha > 0 else "alpha <= 0"
    L += ["", f"alpha = sum((m3 - m9) lq1) / sum(lq1^2) = {alpha:+.4f} (registered expectation alpha > 0: {'MET' if alpha > 0 else 'NOT MET'}); "
          f"r(lq1, m3 - m9) = {r_:+.3f}; rms(m3 - m9) {out['rms_m3_minus_m9_nets']:.0f} nets, {out['rms_residual_after_alpha_nets']:.0f} after alpha x lq1"]
    # post hoc: lq1's price where it was a candidate, fitted on all of M9's rows
    rows = json.load(open(os.path.join(HERE, "rows-m9.json")))
    fr = [r for r in rows if r["type"] != "int8"]
    full = "G8+c_end+xfld32+xstage+lq1"
    fam = M9.M7.Fam(fr, {full: M9.FORMS9["float"][full]}, M9.CARD_TERM)
    b, s = fam.fit_all(full, [])
    cj = dict(zip(M9.FORMS9["float"][full], fam.coef_J(full, b)))
    c_lq = float(cj["lq1"])
    pbar = float(np.mean([out["tiles"][n]["bench_correction_w"] / (-rate * out["tiles"][n]["m3_minus_m9_nets"])
                          for n in out["tiles"] if abs(out["tiles"][n]["m3_minus_m9_nets"]) > 1000]))
    out["posthoc_lq1_price"] = {"form": full, "lq1_price_fJ_per_net": c_lq * 1e15,
                                "bench_implied_price_fJ_per_net": -alpha * pbar * 1e15, "mean_price_of_overcounted_nets_fJ": pbar * 1e15,
                                "ratio_fitted_over_bench": (c_lq / (-alpha * pbar)) if alpha * pbar else None,
                                "note": "post hoc: lq1 was not kept by the registered rule; this is its price in the form that held every float candidate"}
    L += [f"post hoc: lq1's price in {full} fitted on all of M9's rows {c_lq * 1e15:+.3f} fJ a net; the bench's own -alpha x the mean price of "
          f"the over-counted nets ({pbar * 1e15:.3f} fJ) = {-alpha * pbar * 1e15:+.3f} fJ a net; ratio {out['posthoc_lq1_price']['ratio_fitted_over_bench']:+.2f}"]
    # post hoc: two calibration tiles are pool 6's own S tiles, byte for byte; the bench reproduces their committed counts at its three
    # points, and the nine-point launch average, at M9's frozen prices, is set against M9's errors on them (card 1 x its scale)
    B6 = os.path.join(M9.B6)
    c6 = json.load(open(os.path.join(B6, "counts-blind6.json")))["rows"]
    man6 = {m["name"]: m for m in json.load(open(os.path.join(B6, "blind6.json")))["tiles"]}
    nested = json.load(open(os.path.join(HERE, "nested-m9.json")))
    p6 = {(r["key"], r["card"]): r for r in nested["families"]["float"]["pool6_rows"]}
    s1 = json.load(open(os.path.join(HERE, "m9.json")))["families"]["float"]["card1_scale_by_format"]["fp32"]
    same = {}
    L.append("")
    L.append("post hoc: the calibration tiles that are pool 6's own tiles (byte for byte), M9's errors with the bench's nine-point launch average")
    for cal, p6n in (("fp32.cal_third_b20", "fp32.b_onebit_b20_third"), ("fp32.cal_third_b12", "fp32.b_onebit_b12_third")):
        h_cal = man[cal]["sha256"]
        h_p6 = man6[p6n]["sha256"]["whole"]
        rep = {p["n0"]: p["vpu"]["nets_map"] for p in c6[p6n]["points"]}
        mine = {p["n0"]: p["vpu"]["nets_map"] for p in c[cal]["points"]}
        reproduces = all(mine.get(n) == v for n, v in rep.items())
        corr = out["tiles"][cal]["bench_correction_w"]
        rec = {"pool6_tile": p6n, "bytes_identical": h_cal == h_p6, "bench_reproduces_pool6_counts_at_its_three_points": reproduces,
               "bench_correction_w": corr}
        for cd, sc in (("a3", 1.0), ("c1", s1)):
            r = p6[(p6n, cd)]
            for m in ("M9_nested", "M9_frozen_form_loko", "M8_frozen", "M6_frozen"):
                rec[f"{m}|{cd}"] = {"err_w": r[m], "err_with_nine_point_average_w": r[m] - sc * corr}
        same[cal] = rec
        L.append(f"   {p6n} (= {cal}: bytes {'identical' if rec['bytes_identical'] else 'DIFFER'}; the bench reproduces its committed three points: "
                 f"{reproduces}): correction {corr:+.3f} W; M9 nested {rec['M9_nested|a3']['err_w']:+.3f} -> {rec['M9_nested|a3']['err_with_nine_point_average_w']:+.3f} W "
                 f"(aifoundry3), {rec['M9_nested|c1']['err_w']:+.3f} -> {rec['M9_nested|c1']['err_with_nine_point_average_w']:+.3f} W (card 1); "
                 f"M8 as frozen {rec['M8_frozen|a3']['err_w']:+.3f} -> {rec['M8_frozen|a3']['err_with_nine_point_average_w']:+.3f} / "
                 f"{rec['M8_frozen|c1']['err_w']:+.3f} -> {rec['M8_frozen|c1']['err_with_nine_point_average_w']:+.3f} W")
    out["posthoc_pool6_tiles"] = same
    # post hoc: how many of M9's float rows have a three-point spread like the tiles above (what a nine-point recount would cover)
    spreads, nrow = [], 0
    for r in rows:
        if r["type"] == "int8" or not r.get("counts_src") or " rows." not in r["counts_src"]:
            continue
        fpath, key = r["counts_src"].split(" rows.", 1)
        if fpath not in _CC:
            _CC[fpath] = json.load(open(os.path.join(M9.ROOT, fpath)))["rows"]
        crow = _CC[fpath][key]
        v = [p["vpu"]["nets_map"] for p in sorted(crow["points"], key=lambda p: p["n0"])]
        spreads.append((max(v) - min(v)) / max(1.0, float(np.mean(v))))
        nrow += 1
    spreads = np.array(spreads)
    cal_sp = [(max(t["points_nets"][i] for i in (1, 4, 7)) - min(t["points_nets"][i] for i in (1, 4, 7))) / t["m3_nets"] for t in out["tiles"].values()]
    out["posthoc_launch_spread"] = {"float_rows_with_counts": nrow, "rows_spread_over_10pct": int(np.sum(spreads > 0.10)),
                                    "rows_spread_over_20pct": int(np.sum(spreads > 0.20)), "median_spread": float(np.median(spreads)),
                                    "calibration_tiles_spread_range": [float(min(cal_sp)), float(max(cal_sp))],
                                    "note": "spread = (max - min) / mean of the whole-VPU nets at the bench's three launch points; E147's steps not counted"}
    L.append(f"   post hoc: of M9's {nrow} float rows with a counts row (E147's steps aside), {out['posthoc_launch_spread']['rows_spread_over_10pct']} have a "
             f"three-point spread over 10% of their mean and {out['posthoc_launch_spread']['rows_spread_over_20pct']} over 20% (median "
             f"{out['posthoc_launch_spread']['median_spread']:.3f}); the 16 calibration tiles spread {min(cal_sp):.3f}-{max(cal_sp):.3f}")
    corrs = {n: v["bench_correction_w"] for n, v in out["tiles"].items()}
    out["bench_correction_range_w"] = [min(corrs.values()), max(corrs.values())]
    L.append(f"   the bench's own three-point launch-average error over the 16 tiles, at M9's prices: {min(corrs.values()):+.3f} to {max(corrs.values()):+.3f} W")
    json.dump(out, open(os.path.join(BC, "benchcheck.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(BC, "benchcheck.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
