#!/usr/bin/env python3
"""Revision 2 of the Q130(b) predictor: the corrections its verification forced (Sat 31 Oct 2026, week 44).

    predict_r2.py counts.json verification/hier-measured.json verification/fcheck.json --out predictor-r2.json

r1 (predict.py -> predictor.json, sha256 f886b131..., commit e05f2a3b) stays unchanged as the record of what was
frozen, and is WITHDRAWN as E78's prediction. r2 changes four things, each argued in README section 0:

1. NO ABSOLUTE LEVEL. E64's fit P_f = B_f + c_run * s_f (tools/claims-v3/hpl/surface_hpl.py fit_linear) has an
   exact null direction: B_f -> B_f + d * s_f with every c -> c - d leaves every fitted power unchanged. So c has
   no absolute level, and only DIFFERENCES between runs are measured. r2 states every prediction as watts ABOVE
   fp32 zeros (r1's W0 cancels), scores the held-out cells by their error in watts (never by a ratio), and gives
   energy per MAC only above fp32 zeros.
2. INTERVALS. Each fp32 anchor is the mean of three runs. Their standard errors go through the exact fit into
   g, k and every prediction by linear propagation (central differences). A held-out cell is one run, so its
   error also carries the pooled single-run sd of the three anchors (6 degrees of freedom).
3. TOGGLES PER FORMAT. r1 divided every raw coverage count by the toggle recount's whole-unit factor 5.3271.
   Settled VCD counts of this bench's own runs give 4.617 (fp32 randn), 4.193 (fp16 randn) and 2.076 (int8 full)
   names per merged net (hier-measured.json). Variant A keeps one common factor (r1's). Variant B divides each
   format by its own measured factor. A common factor is absorbed by k, so fp32 predictions are the same in
   both; fp16 and int8 move. Both are registered. Neither is blind for E64's six held-out cells (r1's scores
   were known when r2 was written); both are blind for every E78 cell.
4. PROVISIONAL. The bench fails a functional check (fcheck.json): a MADD micro-op returns its addend in fp32,
   adds one of its two products in fp16, and int8's accumulator adds another micro-op's C. Every toggle count,
   k, and the k term of every prediction inherit that. The g term (a lane switched on) needs no toggle count.
"""
import argparse
import hashlib
import json
import math
import os
import statistics as st

HIER_R1 = 5.3271115221865095        # docs/reports/data/2026-10-26-toggle-recount/hier-factors.json `_total`
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
F_HZ = 600e6
MINIONS = 1024

# E64 docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json `fit.c` (the per-run term of the fit)
ANCHORS = {
    ("fp32", "zeros"): [1.406, 1.473, 1.442],      # LAD-00 r1, r2 and SUS-00
    ("fp32", "ones"):  [11.164, 9.648, 9.704],     # LAD-02 r1, r2 and SUS-01
    ("fp32", "randn"): [25.459, 25.593, 25.862],   # LAD-09 r1, r2 and SUS-02
}
HELD_OUT = {                                        # SUS-03 .. SUS-08, one run each
    ("fp16", "zeros"): 1.394, ("fp16", "ones"): 9.702, ("fp16", "randn"): 23.284,
    ("int8", "zeros"): 2.123, ("int8", "ones"): 2.684, ("int8", "full"): 9.101,
}
# the files that hold the multiplier array (Booth partial products, Wallace tree, 4:2 compressors). txfma_csa is
# mostly the compressors' 3:2 cells but also has instances in txfma_f3 and the exponent paths, so the share is
# "array-dominated", not exact.
ARRAY = ("txfma_booth_ppg_32r4", "txfma_booth_ppg_32r4_norm", "txfma_booth_ppg_32r4_msb", "txfma_wallace1",
         "txfma_wallace2", "txfma_4_2_compressor", "txfma_4_2_compressor_array", "txfma_csa")


def unit_nets(row, which="new_bench"):
    """Raw toggle coverage per op inside the unit the format uses (r1's rule, predict.py unit_nets)."""
    bb = row[which]["by_block"]
    if row["type"] == "int8":
        return sum(v for k, v in bb.items() if k.startswith("tima") or k == "et_clk_gate")
    return sum(v for k, v in bb.items() if not k.startswith("tima"))


def solve3(A, b):
    M = [r[:] + [x] for r, x in zip(A, b)]
    for i in range(3):
        pv = max(range(i, 3), key=lambda r: abs(M[r][i]))
        M[i], M[pv] = M[pv], M[i]
        for r in range(3):
            if r != i and M[r][i] != 0.0:
                f = M[r][i] / M[i][i]
                for c in range(i, 4):
                    M[r][c] -= f * M[i][c]
    return [M[i][3] / M[i][i] for i in range(3)]


class Model:
    def __init__(self, rows, factors):
        self.rows, self.factors = rows, factors
        self.rate = {}
        for key, r in rows.items():
            typ = key[0]
            ops_s = F_HZ / CYCLES[typ] * MINIONS
            nh = unit_nets(r) / factors[typ]
            self.rate[key] = {"live_s": r["new_bench"]["slot_valid"] * ops_s, "nets_s": nh * ops_s,
                              "nets_hier_per_op": nh, "nets_hier_per_mac": nh / MACS[typ]}

    def fit(self, wz, wo, wn):
        z, o, n = (self.rate[("fp32", k)] for k in ("zeros", "ones", "randn"))
        A = [[1.0, x["live_s"], x["nets_s"]] for x in (z, o, n)]
        return solve3(A, [wz, wo, wn])

    def predict(self, key, w):
        W0, g, k = self.fit(*w)
        r = self.rate[key]
        return W0 + g * r["live_s"] + k * r["nets_s"]


def mean_se(xs):
    return st.mean(xs), (st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("counts")
    ap.add_argument("hier")
    ap.add_argument("fcheck")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    counts = json.load(open(a.counts))
    rows = {(r["type"], r["kind"]): r for r in counts["rows"]}
    hier = {(h["type"], h["kind"]): h for h in json.load(open(a.hier))["rows"]}
    fchk = json.load(open(a.fcheck))

    w = [mean_se(ANCHORS[("fp32", k)])[0] for k in ("zeros", "ones", "randn")]
    se = [mean_se(ANCHORS[("fp32", k)])[1] for k in ("zeros", "ones", "randn")]
    ss = sum(sum((x - st.mean(v)) ** 2 for x in v) for v in ANCHORS.values())
    dof = sum(len(v) - 1 for v in ANCHORS.values())
    sd_run = math.sqrt(ss / dof)                    # pooled single-run sd of the anchors

    measured_factor = {"fp32": hier[("fp32", "randn")]["factor_coverage_raw_over_hier"],
                       "fp16": hier[("fp16", "randn")]["factor_coverage_raw_over_hier"],
                       "int8": hier[("int8", "full")]["factor_coverage_raw_over_hier"]}
    variants = {"A_r1_common_factor": Model(rows, {f: HIER_R1 for f in CYCLES}),
                "B_measured_per_format": Model(rows, measured_factor)}

    def grad(model, fn):
        """d fn / d (wz, wo, wn) by central differences."""
        out = []
        for i in range(3):
            h = 1e-4
            up, dn = list(w), list(w)
            up[i] += h
            dn[i] -= h
            out.append((fn(model, up) - fn(model, dn)) / (2 * h))
        return out

    def sig(gr):
        return math.sqrt(sum((gi * si) ** 2 for gi, si in zip(gr, se)))

    out = {
        "_what": "Q130(b) predictor, revision 2: E78's switching watts per kind ABOVE fp32 zeros, with intervals",
        "_status": "PROVISIONAL. The bench fails a functional check (verification/fcheck.json): every toggle count, "
                   "k, and the k term of each prediction inherit that. Variant A and B are both registered for E78. "
                   "Neither is blind for E64's six held-out cells; both are blind for every E78 cell.",
        "_supersedes": "predictor.json (r1, sha256 f886b131f07406cfe25b784bff972603b16d70abb01ed3ef827829f7cb46aa83, "
                       "commit e05f2a3b), WITHDRAWN as E78's prediction and kept unchanged as the record",
        "_model": "dW(kind) = W(kind) - W(fp32 zeros) = g*(live_s(kind) - live_s(zeros)) + k*(nets_s(kind) - "
                  "nets_s(zeros)); W0 cancels, because E64's fit gives no absolute level (README section 0)",
        "_gauge": "E64's P_f = B_f + c*s_f is unchanged by B_f -> B_f + d*s_f, c -> c - d. Three starting points of "
                  "surface_hpl.py's own fit give rms 0.8242 W each with fp32 zeros c = 1.440, 7.953 and -5.072 W. "
                  "So W0 = 1.440 W is not a floor, pJ per MAC has no absolute level, and a ratio of two c values "
                  "means nothing; differences and errors in watts are unchanged.",
        "_inputs": {"anchors_W_fit_c": {f"{k[0]}.{k[1]}": v for k, v in ANCHORS.items()},
                    "anchor_means_W": dict(zip(("fp32.zeros", "fp32.ones", "fp32.randn"), [round(x, 4) for x in w])),
                    "anchor_se_W": dict(zip(("fp32.zeros", "fp32.ones", "fp32.randn"), [round(x, 4) for x in se])),
                    "pooled_single_run_sd_W": round(sd_run, 4), "pooled_sd_dof": dof,
                    "held_out_W_fit_c": {f"{k[0]}.{k[1]}": v for k, v in HELD_OUT.items()},
                    "cycles_per_op": CYCLES, "macs_per_op": MACS, "f_hz": F_HZ, "minions": MINIONS,
                    "factor_r1_common": HIER_R1, "factor_measured_per_format": measured_factor},
        "variants": {},
    }

    for vname, m in variants.items():
        W0, g, k = m.fit(*w)
        gW0 = grad(m, lambda mm, ww: mm.fit(*ww)[0])
        gg = grad(m, lambda mm, ww: mm.fit(*ww)[1])
        gk = grad(m, lambda mm, ww: mm.fit(*ww)[2])
        v = {"calibration": {
            "g_W_per_live_slot_cycle_per_s": g, "g_sigma": sig(gg),
            "k_fJ_per_merged_net_toggle": k * 1e15, "k_sigma_fJ": sig(gk) * 1e15,
            "k_note": "k is the fJ per merged-net toggle only under this variant's factor, on a bench whose "
                      "accumulate path is wrong: a fitting constant, not a physical energy per net",
            "W0_gauge_W": W0, "W0_note": "the gauge's zero, not a floor: it cancels from every dW and every error"},
            "predictions": {}, "held_out_scoring": {}}
        for key in sorted(m.rate):
            fn = (lambda kk: (lambda mm, ww: mm.predict(kk, ww) - mm.predict(("fp32", "zeros"), ww)))(key)
            dw = fn(m, w)
            sdw = sig(grad(m, fn))
            r = m.rate[key]
            mac_s = F_HZ / CYCLES[key[0]] * MINIONS * MACS[key[0]]
            v["predictions"][f"{key[0]}.{key[1]}"] = {
                "dW_above_fp32_zeros": round(dw, 3), "sigma_W": round(sdw, 3),
                "dpJ_per_MAC_above_fp32_zeros": round(dw / mac_s * 1e12, 4),
                "nets_hier_per_MAC_provisional": round(r["nets_hier_per_mac"], 2),
                "is_anchor": key in ANCHORS, "is_held_out": key in HELD_OUT,
            }
        errs = []
        for key, meas in HELD_OUT.items():
            fn = (lambda kk: (lambda mm, ww: mm.predict(kk, ww)))(key)
            pr = fn(m, w)
            sp = sig(grad(m, fn))
            se_err = math.sqrt(sp ** 2 + sd_run ** 2)
            err = pr - meas
            errs.append(err)
            v["held_out_scoring"][f"{key[0]}.{key[1]}"] = {
                "measured_dW_above_fp32_zeros": round(meas - w[0], 3),
                "predicted_dW_above_fp32_zeros": round(pr - w[0], 3),
                "err_W": round(err, 3), "sigma_err_W": round(se_err, 3), "z": round(err / se_err, 2),
                "z_with_noisiest_anchor_sd": round(err / math.sqrt(sp ** 2 + st.stdev(ANCHORS[("fp32", "ones")]) ** 2), 2),
                "verdict": ("consistent within noise (|z| < 2)" if abs(err / se_err) < 2 else
                            "misses by more than 2 sigma"),
            }
        v["held_out_scoring"]["_rms_err_W"] = round(math.sqrt(sum(e * e for e in errs) / len(errs)), 3)
        out["variants"][vname] = v

    # what each format's own zeros/ones pair says a lane switched on costs (gauge-free, toggle-free)
    m = variants["A_r1_common_factor"]
    g32 = (w[1] - w[0]) / m.rate[("fp32", "ones")]["live_s"]
    g32s = math.sqrt(se[1] ** 2 + se[0] ** 2) / m.rate[("fp32", "ones")]["live_s"]
    pg = {"_what": "g_fmt = (W(ones) - W(zeros)) / live slot-cycles per s of ones; uses held-out cells, NOT frozen",
          "fp32": {"dW_ones_minus_zeros": round(w[1] - w[0], 3),
                   "sigma_W": round(math.sqrt(se[1] ** 2 + se[0] ** 2), 3), "g": g32, "g_sigma": g32s}}
    for f in ("fp16", "int8"):
        d = HELD_OUT[(f, "ones")] - HELD_OUT[(f, "zeros")]
        ds = math.sqrt(2) * sd_run
        lv = m.rate[(f, "ones")]["live_s"]
        ratio = (d / lv) / g32
        rs = abs(ratio) * math.sqrt((ds / d) ** 2 + (g32s / g32) ** 2) if d else float("nan")
        pg[f] = {"dW_ones_minus_zeros": round(d, 3), "sigma_W": round(ds, 3), "g": d / lv, "g_sigma": ds / lv,
                 "ratio_to_fp32_g": round(ratio, 4), "ratio_sigma": round(rs, 4),
                 "ratio_2sigma_upper": round(ratio + 2 * rs, 4)}
    out["per_format_g_from_held_out"] = pg

    # E64's gauge-free differences, the numbers that do mean something
    def c(fk):
        return st.mean(ANCHORS[fk]) if fk in ANCHORS else HELD_OUT[fk]

    def csd(fk):
        return (st.stdev(ANCHORS[fk]) / math.sqrt(3)) if fk in ANCHORS else sd_run

    pairs = [(("fp32", "ones"), ("fp32", "zeros")), (("fp32", "randn"), ("fp32", "ones")),
             (("fp32", "randn"), ("fp32", "zeros")), (("fp16", "randn"), ("fp32", "randn")),
             (("fp16", "ones"), ("fp32", "ones")), (("fp16", "zeros"), ("fp32", "zeros")),
             (("int8", "zeros"), ("fp32", "zeros")), (("int8", "ones"), ("int8", "zeros")),
             (("int8", "full"), ("int8", "zeros")), (("fp16", "randn"), ("fp16", "ones"))]
    out["e64_gauge_free_differences_W"] = {
        f"{x[0]}.{x[1]} - {y[0]}.{y[1]}": {"dW": round(c(x) - c(y), 3), "sigma": round(math.hypot(csd(x), csd(y)), 3)}
        for x, y in pairs}

    # toggles, every kind, both conventions, provisional
    tg = {}
    for key, r in sorted(rows.items()):
        raw = unit_nets(r)
        typ = key[0]
        bb = r["new_bench"]["by_block"]
        arr = sum(bb.get(b, 0.0) for b in ARRAY) if typ != "int8" else None
        e = {"raw_coverage_per_op": round(raw, 1),
             "nets_hier_per_MAC_A_factor_5.327": round(raw / HIER_R1 / MACS[typ], 2),
             "nets_hier_per_MAC_B_format_factor": round(raw / measured_factor[typ] / MACS[typ], 2),
             "gated_slot_frac": round(1.0 - r["new_bench"]["slot_valid"] / 4096.0, 4),
             "bus_ab_per_op": r["new_bench"]["bus_ab"]}
        if key in hier:
            f = hier[key]["factor_coverage_raw_over_hier"]
            e["kind_factor_measured"] = round(f, 4)
            e["nets_hier_per_MAC_kind_factor"] = round(raw / f / MACS[typ], 2)
        if arr is not None:
            e["array_dominated_share"] = round(arr / raw, 4) if raw else None
            e["array_dominated_raw_per_MAC"] = round(arr / MACS[typ], 2)
        tg[f"{typ}.{key[1]}"] = e
    out["toggles_provisional"] = tg

    rr = lambda t, k, f: unit_nets(rows[(t, k)]) / f / MACS[t]
    out["cross_format_ratios_provisional"] = {
        "fp32_over_fp16_per_MAC_randn": {"A": round(rr("fp32", "randn", HIER_R1) / rr("fp16", "randn", HIER_R1), 3),
                                         "B": round(rr("fp32", "randn", measured_factor["fp32"]) /
                                                    rr("fp16", "randn", measured_factor["fp16"]), 3)},
        "fp32_over_fp16_per_op_randn": {"A": round(rr("fp32", "randn", HIER_R1) * 4096 / (rr("fp16", "randn", HIER_R1) * 8192), 3),
                                        "B": round(rr("fp32", "randn", measured_factor["fp32"]) * 4096 /
                                                   (rr("fp16", "randn", measured_factor["fp16"]) * 8192), 3)},
        "fp32_randn_over_int8_full_per_MAC": {"A": round(rr("fp32", "randn", HIER_R1) / rr("int8", "full", HIER_R1), 1),
                                              "B": round(rr("fp32", "randn", measured_factor["fp32"]) /
                                                         rr("int8", "full", measured_factor["int8"]), 1),
                                              "comparable": False,
                                              "why": "int8's multiply, product sum and add are behavioural RTL "
                                                     "(tima_top.v:89, :94; tima_adder.v:17), so coverage sees no "
                                                     "nets inside them, while txfma's array is structural"},
        "array_dominated_fp32_over_fp16_raw_per_MAC_randn": round(
            sum(rows[("fp32", "randn")]["new_bench"]["by_block"].get(b, 0) for b in ARRAY) / 4096 /
            (sum(rows[("fp16", "randn")]["new_bench"]["by_block"].get(b, 0) for b in ARRAY) / 8192), 3),
        "randn_sorted_over_randn_whole_unit": {f: round(unit_nets(rows[(f, "randn_sorted")]) / unit_nets(rows[(f, "randn")]), 3)
                                               for f in ("fp32", "fp16")},
        "randn_sorted_over_randn_array_dominated": {
            f: round(sum(rows[(f, "randn_sorted")]["new_bench"]["by_block"].get(b, 0) for b in ARRAY) /
                     sum(rows[(f, "randn")]["new_bench"]["by_block"].get(b, 0) for b in ARRAY), 3) for f in ("fp32", "fp16")},
        "kind_factor_spread": {f"{t}.{k}": round(h["factor_coverage_raw_over_hier"], 3) for (t, k), h in hier.items()},
    }

    # the fp32 cross-check against rtl-sim/fma_toggle, which r1 reported as a pass
    xc = {}
    for key, r in sorted(rows.items()):
        if key[0] != "fp32" or "old_bench" not in r:
            continue
        new, old = unit_nets(r), r["old_bench"]["nets"]
        xc[key[1]] = {"gated_slot_frac": round(1.0 - r["new_bench"]["slot_valid"] / 4096.0, 4),
                      "new_over_old_nets": round(new / old, 5) if old else None,
                      "new_ff_toggles": r["new_bench"]["ff_toggles"], "old_ff_toggles": r["old_bench"]["ff_toggles"]}
    out["crosscheck_fp32_new_vs_old_bench"] = xc

    # the functional check, summarised: the share of MADD results that equal the multiply-add of their operands
    fc = {}
    for run in fchk["runs"]:
        madd_ops = range(0 if run["mul"] == 0 else 1, run["warm"] + run["ops"])
        mul_ops = range(0, 1) if run["mul"] == 1 else range(0)
        s = {"madd_results": 0, "equal_to_a_times_b_plus_c": 0, "equal_to_c_alone": 0,
             "equal_to_a_times_b_alone": 0, "equal_to_neither_term": 0, "mul_results": 0, "mul_equal_to_a_times_b": 0}
        for kk, n in run["tally"].items():
            op, _, flags = kk.split("|")
            f = dict(x.split("=") for x in flags.split(","))
            if int(op[2:]) in madd_ops:
                s["madd_results"] += n
                if f["madd"] == "1":
                    s["equal_to_a_times_b_plus_c"] += n
                elif f["c"] == "1":
                    s["equal_to_c_alone"] += n
                elif f["ab"] == "1":
                    s["equal_to_a_times_b_alone"] += n
                else:
                    s["equal_to_neither_term"] += n
            elif int(op[2:]) in mul_ops:
                s["mul_results"] += n
                s["mul_equal_to_a_times_b"] += n if f["ab"] == "1" else 0
        s["final_C_top"] = run["final_C_distinct_top5"][0][1]
        s["final_C_expected"] = run["final_C_expected_if_accumulating"]
        fc[run["label"]] = s
    out["functional_check"] = fc

    json.dump(out, open(a.out, "w"), indent=1)
    print("sha256", hashlib.sha256(open(a.out, "rb").read()).hexdigest(), os.path.basename(a.out))
    for vname, v in out["variants"].items():
        cal = v["calibration"]
        print(f"{vname}: g={cal['g_W_per_live_slot_cycle_per_s']:.4e}+-{cal['g_sigma']:.2e}  "
              f"k={cal['k_fJ_per_merged_net_toggle']:.4f}+-{cal['k_sigma_fJ']:.4f} fJ")
        for kk, s in v["held_out_scoring"].items():
            if isinstance(s, dict):
                print(f"   {kk:12s} err {s['err_W']:+7.3f} W  sigma {s['sigma_err_W']:.3f}  z {s['z']:+6.2f}  "
                      f"(noisiest-sd z {s['z_with_noisiest_anchor_sd']:+.2f})")


if __name__ == "__main__":
    main()
