#!/usr/bin/env python3
"""E109, POST HOC (written Sun 1 Nov 2026 after the data): readings the registration did not name, from the two reductions' per-pass values and the
RTL bench's counts. Nothing here is registered.

    python3 tools/claims-v3/e109/posthoc_check_e109.py <data dir>        # writes <data dir>/posthoc.json and posthoc.txt

For each reduction - the registered one (e109.json: two kept passes) and the post-hoc one with E78's random-anchor span gate lifted (e109-3pass.json:
three passes) - per pass, then mean and 95% interval over passes:
  1. S over idle of each format's zeros with no micro-op issued (m0), and their difference;
  2. the most a scratchpad read could cost in each format, if all of m0's S were reads (the RTL's reads an op x the measured rate);
  3. what int8's extra reads a second would cost at fp32's ceiling;
  4. the lanes' cost on zeros, U, per register-bit clock edge and per enabled (clocked) bit that the mask removes in the RTL bench;
  5. the register activity a second the bench counts in each format's no-issue loop;
  6. item 15: a live -0 lane with random B over a constant live lane, D(a_nz_b_randn) - T_minus - D(anchor_pi).
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776}
B = json.load(open(os.path.join(HERE, "desk", "bench-arms.json")))["per_op"]


def ci(v):
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "half": None, "n": n, "per_pass": v}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return {"mean": m, "half": T95[n - 1] * sd / math.sqrt(n), "n": n, "per_pass": v}


def fmt(c, unit="W", k=3):
    return f"{c['mean']:+.{k}f}" + ("" if c["half"] is None else f" ± {c['half']:.{k}f}") + f" {unit}"


def reading(path):
    d = json.load(open(path))
    per = d["per_pass"]
    out = {}
    rows = {k: [] for k in ("S_m0_fp32", "S_m0_int8", "S_m0_gap", "read_ceiling_fp32_pj", "read_ceiling_int8_pj", "extra_reads_at_fp32_ceiling_w",
                            "U_fp32", "U_int8", "U_per_edge_fp32_fj", "U_per_edge_int8_fj", "U_per_clocked_fp32_fj", "U_per_clocked_int8_fj",
                            "live_over_constant_w", "S_zeros_fp32", "S_zeros_int8")}
    act = {}
    for p, e in per.items():
        r = {}
        for f in ("fp32", "int8"):
            z, m0 = e[f"{f}.zeros"], e[f"m0.{f}.zeros"]
            rate_m0 = m0["rate"]
            reads = B[f"m0.{f}.zeros"]["scp_reads"] * rate_m0
            r[f] = {"S_m0": m0["S"], "S_zeros": z["S"], "reads_s": reads, "U": -m0["D"],
                    "edges_s": (B[f"base.{f}.zeros"]["ff_present_bits"] - B[f"m0.{f}.zeros"]["ff_present_bits"]) * z["rate"],
                    "clocked_s": (B[f"base.{f}.zeros"]["ff_clocked_bits"] - B[f"m0.{f}.zeros"]["ff_clocked_bits"]) * z["rate"],
                    "m0_rest_edges_s": B[f"m0.{f}.zeros"]["rest_present"] * rate_m0, "m0_rest_clocked_s": B[f"m0.{f}.zeros"]["rest_clocked"] * rate_m0}
        rows["S_m0_fp32"].append(r["fp32"]["S_m0"])
        rows["S_m0_int8"].append(r["int8"]["S_m0"])
        rows["S_m0_gap"].append(r["int8"]["S_m0"] - r["fp32"]["S_m0"])
        rows["S_zeros_fp32"].append(r["fp32"]["S_zeros"])
        rows["S_zeros_int8"].append(r["int8"]["S_zeros"])
        cf = r["fp32"]["S_m0"] / r["fp32"]["reads_s"]
        rows["read_ceiling_fp32_pj"].append(cf * 1e12)
        rows["read_ceiling_int8_pj"].append(r["int8"]["S_m0"] / r["int8"]["reads_s"] * 1e12)
        rows["extra_reads_at_fp32_ceiling_w"].append((r["int8"]["reads_s"] - r["fp32"]["reads_s"]) * cf)
        for f in ("fp32", "int8"):
            rows[f"U_{f}"].append(r[f]["U"])
            rows[f"U_per_edge_{f}_fj"].append(r[f]["U"] / r[f]["edges_s"] * 1e15)
            rows[f"U_per_clocked_{f}_fj"].append(r[f]["U"] / r[f]["clocked_s"] * 1e15)
        t_minus = e["m0.fp32.a_nz_b_randn"]["D"] - e["m0.fp32.zeros"]["D"]
        rows["live_over_constant_w"].append(e["fp32.a_nz_b_randn"]["D"] - t_minus - e["anchor_pi"]["D"])
        act[p] = {f: {"m0_rest_edges_per_s": r[f]["m0_rest_edges_s"], "m0_rest_clocked_per_s": r[f]["m0_rest_clocked_s"], "reads_per_s": r[f]["reads_s"]} for f in ("fp32", "int8")}
    out = {k: ci(v) for k, v in rows.items()}
    out["bench_activity_per_s"] = act
    out["passes"] = list(per.keys())
    return out


def main():
    dd = sys.argv[1]
    res = {"what": "E109 post hoc: readings not registered", "registered_reduction": reading(os.path.join(dd, "e109.json")),
           "three_passes_gate_lifted": reading(os.path.join(dd, "e109-3pass.json"))}
    json.dump(res, open(os.path.join(dd, "posthoc.json"), "w"), indent=1)
    L = ["E109 POST HOC (posthoc_check_e109.py): not registered; per pass, mean ± 95% over passes", ""]
    for key, lab in (("registered_reduction", "the registered reduction (e109.json), passes"), ("three_passes_gate_lifted", "three passes, E78's random-anchor span gate lifted (e109-3pass.json), passes")):
        r = res[key]
        L.append(f"## {lab} {', '.join(r['passes'])}")
        L.append(f"S over idle, zeros: fp32 {fmt(r['S_zeros_fp32'])}, int8 {fmt(r['S_zeros_int8'])}")
        L.append(f"S over idle, zeros with no micro-op issued (m0): fp32 {fmt(r['S_m0_fp32'])}, int8 {fmt(r['S_m0_int8'])}; int8 - fp32 {fmt(r['S_m0_gap'])}")
        L.append(f"the most a scratchpad read could cost if all of m0's S were reads: fp32 {fmt(r['read_ceiling_fp32_pj'], 'pJ', 2)}, int8 {fmt(r['read_ceiling_int8_pj'], 'pJ', 2)}")
        L.append(f"int8's extra reads a second at fp32's ceiling: {fmt(r['extra_reads_at_fp32_ceiling_w'])} (of the m0 gap above)")
        L.append(f"the lanes on zeros, U: fp32 {fmt(r['U_fp32'])}, int8 {fmt(r['U_int8'])}")
        L.append(f"  per register-bit clock edge the mask removes in the bench: fp32 {fmt(r['U_per_edge_fp32_fj'], 'fJ', 3)}, int8 {fmt(r['U_per_edge_int8_fj'], 'fJ', 3)}")
        L.append(f"  per clocked (enabled) bit it removes: fp32 {fmt(r['U_per_clocked_fp32_fj'], 'fJ', 2)}, int8 {fmt(r['U_per_clocked_int8_fj'], 'fJ', 2)} (M4's a: 1.066 fJ)")
        a = next(iter(r["bench_activity_per_s"].values()))
        L.append(f"the bench's register activity a second in the no-issue loop (first pass's rates): fp32 {a['fp32']['m0_rest_edges_per_s']:.3e} edges, {a['fp32']['m0_rest_clocked_per_s']:.3e} clocked; "
                 f"int8 {a['int8']['m0_rest_edges_per_s']:.3e} edges, {a['int8']['m0_rest_clocked_per_s']:.3e} clocked; reads {a['fp32']['reads_per_s']:.3e} and {a['int8']['reads_per_s']:.3e}")
        L.append(f"item 15: a live -0 lane with random B over a constant live lane (pi x pi), transport taken out: {fmt(r['live_over_constant_w'])}")
        L.append("")
    open(os.path.join(dd, "posthoc.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
