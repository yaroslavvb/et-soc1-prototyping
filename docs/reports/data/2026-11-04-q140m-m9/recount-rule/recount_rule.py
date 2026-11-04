#!/usr/bin/env python3
"""Q140(m) fix pass: RECOUNT-RULE.md, the convergence rule for the bench's launch average, as code (committed with the rule,
before any bench count at more than nine launch points existed).

The bench counts one op at op index n0 of a 0.5 s launch at 600 MHz, with C at its value there (rtl-sim/fma_toggle_v2,
run_kinds.py). A tile's launch average at N points is the mean over the N midpoints of N equal parts of the launch,
n_j = int(ops (2j + 1) / 2N), ops = 0.5 x 600e6 / 546, for N = 3^m: each set holds the one before, so a step reuses every point.

At M9's frozen float prices (m9.json; the stage mapping of benchcheck_m9.py: multiplier at mult, adder_norm at add32 (fp32) or
add16 (fp16), lane_operand_bus at bus, every other stage at rest, and the exponent stage at rest + xstage; times the type's op
rate), each point is a number of watts of D. Two estimates of the error of the N-point mean:
  se_sample(N)      = sd of the N points (ddof 1) / sqrt(N)
  se_interleaved(N) = sd of the three interleaved N/3-point rules' means (points j = 0, 1, 2 mod 3) / sqrt(3)
and e(N) = the larger of the two. The bound: e(N) <= 0.10 W. A tile is counted at N = 9, then at 3N while e(N) > 0.10 W, up to
N = 243. N* = the largest of the 16 calibration tiles' first N meeting the bound; undetermined while any tile has not met it.

    python3 -B recount_rule.py [<counts.json> ...]    # default: ../bench-check/counts-cal.json plus counts-pilot27.json if present
Writes recount-rule.json and recount-rule.txt beside this file.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
M9D = os.path.dirname(HERE)
sys.path.insert(0, M9D)
import fit_m9 as M9  # noqa: E402

BOUND_W = 0.10
N_START, N_MAX = 9, 243
OPS = 0.5 * 600e6 / 546
CAL = os.path.join(M9D, "bench-check", "cal-tiles.json")
POOL6_TWINS = (("fp32.cal_third_b20", "fp32.b_onebit_b20_third"), ("fp32.cal_third_b12", "fp32.b_onebit_b12_third"))


def points(n):
    return [int(OPS * (2 * j + 1) / (2 * n)) for j in range(n)]


def prices():
    f = json.load(open(os.path.join(M9D, "m9.json")))["families"]["float"]
    return dict(zip(f["terms"], f["coef_J"]))


def point_w(p, typ, pr):
    s = p["vpu"]["by_stage"]
    add = pr["add32"] if typ == "fp32" else pr["add16"]
    w = 0.0
    for st, v in s.items():
        if st == "multiplier":
            w += v * pr["mult"]
        elif st == "adder_norm":
            w += v * add
        elif st == "lane_operand_bus":
            w += v * pr["bus"]
        else:
            w += v * pr["rest"]
    w += s.get("exponent", 0) * pr["xstage"]
    return M9.F.RATE[typ] * w


def sd(x):
    m = sum(x) / len(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def err(ws):
    n = len(ws)
    sub = [sum(ws[i::3]) / (n // 3) for i in range(3)]
    se_s = sd(ws) / math.sqrt(n)
    se_i = sd(sub) / math.sqrt(3)
    return {"mean_w": sum(ws) / n, "se_sample_w": se_s, "se_interleaved_w": se_i, "e_w": max(se_s, se_i), "subrule_means_w": sub}


def merged(files):
    rows = {}
    for f in files:
        for k, r in json.load(open(f))["rows"].items():
            d = rows.setdefault(k, {"type": r["type"], "points": {}})
            for p in r["points"]:
                old = d["points"].get(p["n0"])
                if old is not None and old["vpu"]["nets_map"] != p["vpu"]["nets_map"]:
                    raise SystemExit(f"STOP: {k} n0={p['n0']} counted twice with different nets ({f})")
                if p.get("check_mismatch"):
                    raise SystemExit(f"STOP: {k} n0={p['n0']} check_mismatch {p['check_mismatch']} ({f})")
                d["points"][p["n0"]] = p
    return rows


def main():
    files = sys.argv[1:] or [os.path.join(M9D, "bench-check", "counts-cal.json")] + (
        [os.path.join(HERE, "counts-pilot27.json")] if os.path.exists(os.path.join(HERE, "counts-pilot27.json")) else [])
    cal = [t["name"] for t in json.load(open(CAL))["tiles"]]
    rows = merged(files)
    pr = prices()
    std3 = points(3)
    out = {"_note": "Q140(m) fix pass, RECOUNT-RULE.md: e(N) per calibration tile at M9's frozen prices; bound 0.10 W",
           "bound_w": BOUND_W, "inputs": [os.path.relpath(f, M9D) for f in files], "tiles": {}}
    L = ["Q140(m) RECOUNT-RULE.md: the bench's launch average at N points, error e(N) = max(se_sample, se_interleaved) at M9's prices",
         f"bound e(N) <= {BOUND_W:.2f} W; inputs: " + ", ".join(out["inputs"]), "",
         f"{'tile':20s} {'N':>4s} {'mean W':>7s} {'3pt-N W':>8s} {'se_samp':>8s} {'se_intl':>8s} {'e(N)':>6s}  met"]
    first_met = {}
    for name in cal:
        r = rows[name]
        typ = r["type"]
        rec = {"by_N": {}}
        n = N_START
        while n <= N_MAX and all(x in r["points"] for x in points(n)):
            ws = [point_w(r["points"][x], typ, pr) for x in points(n)]
            m3 = sum(point_w(r["points"][x], typ, pr) for x in std3) / 3
            e = err(ws)
            e["three_point_minus_N_w"] = m3 - e["mean_w"]
            e["met"] = e["e_w"] <= BOUND_W
            rec["by_N"][str(n)] = e
            L.append(f"{name:20s} {n:4d} {e['mean_w']:7.3f} {m3 - e['mean_w']:+8.3f} {e['se_sample_w']:8.3f} {e['se_interleaved_w']:8.3f} "
                     f"{e['e_w']:6.3f}  {'yes' if e['met'] else 'no'}")
            if e["met"]:
                first_met[name] = n
                break
            n *= 3
        last = max(int(k) for k in rec["by_N"])
        rec["N_counted"] = last
        rec["first_N_meeting_bound"] = first_met.get(name)
        el = rec["by_N"][str(last)]["e_w"]
        rec["projected_N_by_inverse_sqrt_law"] = None if first_met.get(name) else int(math.ceil(last * (el / BOUND_W) ** 2))
        if "9" in rec["by_N"] and "27" in rec["by_N"]:
            rec["e9_over_e27"] = rec["by_N"]["9"]["e_w"] / rec["by_N"]["27"]["e_w"]
        out["tiles"][name] = rec
    unmet = [t for t in cal if t not in first_met]
    out["N_star"] = max(first_met.values()) if not unmet else None
    out["tiles_not_yet_meeting_bound"] = unmet
    out["next_step"] = (f"count the {len(unmet)} tiles not yet meeting the bound at 3 x their N" if unmet else "none: N* is set")
    ratios = [out["tiles"][t]["e9_over_e27"] for t in cal if "e9_over_e27" in out["tiles"][t]]
    if ratios:
        out["e9_over_e27_range"] = [min(ratios), max(ratios)]
        out["e9_over_e27_median"] = sorted(ratios)[len(ratios) // 2]
    proj = [out["tiles"][t]["projected_N_by_inverse_sqrt_law"] for t in unmet]
    out["projected_N_range_by_inverse_sqrt_law"] = [min(proj), max(proj)] if proj else None
    L += ["", f"N* = {out['N_star'] if out['N_star'] else 'not yet determined'}; tiles not yet meeting the bound: {len(unmet)} of {len(cal)}"]
    if ratios:
        L.append(f"e(9)/e(27) over the tiles counted at 27: {min(ratios):.2f}-{max(ratios):.2f} (median {out['e9_over_e27_median']:.2f}; "
                 f"1/sqrt(N) gives {math.sqrt(3):.2f})")
    if proj:
        L.append(f"projected N to meet the bound by the 1/sqrt(N) law (planning only): {min(proj)}-{max(proj)}")
    # post hoc: the two calibration tiles that are pool 6's own tiles, M9's errors with the launch average at the largest N counted
    nested = json.load(open(os.path.join(M9D, "nested-m9.json")))
    p6 = {(r["key"], r["card"]): r for r in nested["families"]["float"]["pool6_rows"]}
    s1 = json.load(open(os.path.join(M9D, "m9.json")))["families"]["float"]["card1_scale_by_format"]["fp32"]
    out["posthoc_pool6_twins"] = {}
    L.append("")
    L.append("post hoc: pool 6's two twins of calibration tiles, M9's error with the three-point launch average replaced by the N-point one")
    for cal_t, p6n in POOL6_TWINS:
        rec = out["tiles"][cal_t]
        n = rec["N_counted"]
        e = rec["by_N"][str(n)]
        corr = -e["three_point_minus_N_w"]
        tw = {"N": n, "correction_w": corr, "e_w": e["e_w"]}
        for cd, sc in (("a3", 1.0), ("c1", s1)):
            for m in ("M9_nested", "M9_frozen_form_loko"):
                er = p6[(p6n, cd)][m]
                tw[f"{m}|{cd}"] = {"err_w": er, "err_with_N_point_average_w": er - sc * corr, "pm_1se_w": sc * e["e_w"]}
        out["posthoc_pool6_twins"][p6n] = tw
        L.append(f"   {p6n} (N = {n}): correction {corr:+.3f} +- {e['e_w']:.3f} W (1 s.e.); M9 nested {tw['M9_nested|a3']['err_w']:+.3f} -> "
                 f"{tw['M9_nested|a3']['err_with_N_point_average_w']:+.3f} (aifoundry3), {tw['M9_nested|c1']['err_w']:+.3f} -> "
                 f"{tw['M9_nested|c1']['err_with_N_point_average_w']:+.3f} W (card 1); the frozen form's own leave one kind out "
                 f"{tw['M9_frozen_form_loko|a3']['err_w']:+.3f} -> {tw['M9_frozen_form_loko|a3']['err_with_N_point_average_w']:+.3f} / "
                 f"{tw['M9_frozen_form_loko|c1']['err_w']:+.3f} -> {tw['M9_frozen_form_loko|c1']['err_with_N_point_average_w']:+.3f} W")
    run = os.path.join(HERE, "pilot-run.json")
    if os.path.exists(run):
        rr = json.load(open(run))
        sec = rr["wall_s"] * rr["jobs"] / rr["points"]
        out["seconds_per_point_one_core"] = sec
        rc = out.setdefault("recount_cost", {})
        for n in (9, 27, 81, 243):
            rc[str(n)] = {"bench_hours_per_tile_at_4_jobs": (n - 3) * sec / 4 / 3600}
        L.append("")
        L.append(f"bench time: {sec:.1f} s a point on one core (the pilot: {rr['points']} points, {rr['jobs']} jobs, {rr['wall_s']:.0f} s); "
                 "a tile counted at N from its three points costs " + ", ".join(
                     f"N {n}: {rc[str(n)]['bench_hours_per_tile_at_4_jobs'] * 60:.1f} min" for n in (9, 27, 81, 243)) + " at 4 jobs")
    json.dump(out, open(os.path.join(HERE, "recount-rule.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "recount-rule.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
