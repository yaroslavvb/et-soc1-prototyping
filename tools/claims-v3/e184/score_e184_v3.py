#!/usr/bin/env python3
"""E184's scorer, v3 (kit note 2, KIT.md.dated-note-2.md section 1; dated amendment A3, A3-4): score_e184_v2.py (v2, which stays as
committed, and whose readings this file runs) with two corrections and nothing else:

    python3 -B tools/claims-v3/e184/score_e184_v3.py [--s reduced-e184s-v3.json] [--b reduced-e184b-v3.json] --out <dir>
        writes <dir>/scored-e184-v3.json and <dir>/scored-e184-v3.md; an arm whose file is not given is NOT SCORED in every rule.

  1. (the verifier's fault 1) E184-L and E184-P carry the reading that GOVERNS their verdict at the top level: governing_rule, governing_R
     and governing_ci95 (A2-2: the registered R, or the null-corrected R when the part's own null reads OFFSET), and E184-P's METER is read
     on governing_ci95's lower end, as v2 read it. The registered statistic is kept beside it, labelled: registered_R, registered_ci95 and
     registered_verdict, and the null-corrected one as null_corrected_R and null_corrected_ci95. The bare "R" and "ci95" keys v1 and v2
     wrote (always the registered statistic's, even when it did not govern) are not written, and the md prints the governing interval
     beside the verdict, the registered one on its own labelled line.
  2. (the verifier's fault 2; A3-4) E184-C reads A2-4 as written: a scan level besides the reference with fewer than 4 kept quads is left
     out of A2-1's fit, out of the reference reading's median and out of the reported registered statistic, and only the levels kept count
     toward A2-4's 10 (left out: E184-C.levels_left_out). The reference level's quads are set aside by A2-1 whatever their number; the
     reported registered statistic, whose fit uses the reference level, keeps it only with 4 or more.
Its inputs are reduce_e184_v3.py's files (A3-3's session gate; v2's files read the same way). Everything else is v2's: the session gate
(no rule of an arm whose gate does not hold), v1's score_s and score_b on the kept passes, A2-1's statistic and words, A2-2's governing
rule, A2-3's attribution and A2-4's other gates. The md also prints the session gate's departures (A3-3).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import score_e184 as s1  # noqa: E402
import score_e184_v2 as s2  # noqa: E402

A2, T_A2, DS, CARRY, r6 = s2.A2, s2.T_A2, s2.DS, s2.CARRY, s2.r6
MIN_QUADS = s1.MIN_QUADS


def governing_fields(reg):
    """fault 1: the governing reading at the top level, the registered one labelled"""
    a = reg.get("a2")
    if not a:
        return
    nc = a.get("null_corrected") or {}
    by_nc = a["governing_rule"].startswith("the null-corrected")
    reg["registered_verdict"] = a["registered_R_verdict"]
    reg["registered_R"] = reg.pop("R")
    reg["registered_ci95"] = reg.pop("ci95")
    reg["null_corrected_R"] = nc.get("R")
    reg["null_corrected_ci95"] = nc.get("ci95")
    reg["governing_rule"] = a["governing_rule"]
    reg["governing_R"] = nc["R"] if by_nc else reg["registered_R"]
    reg["governing_ci95"] = nc["ci95"] if by_nc else reg["registered_ci95"]
    if "meter" in reg:
        reg["meter_read_on"] = "governing_ci95's lower end (%s) against %s" % (reg["governing_ci95"][0], s1.TH["exclude_P_lower_end"])


def score_c(red):
    """fault 2 (A3-4): E184-C on the scan levels with at least 4 kept quads"""
    cq_all = [q for q in s1.quads_of(red, (18417, 18418), "C") if q.get("y") is not None]
    ref = DS["C"]["ref"]
    per = {}
    for q in cq_all:
        per[q["n"]] = per.get(q["n"], 0) + 1
    left = {str(n): k for n, k in sorted(per.items()) if n != ref and k < MIN_QUADS}
    cq = [q for q in cq_all if q["n"] == ref or per[q["n"]] >= MIN_QUADS]
    ns = sorted(set(q["n"] for q in cq if q["n"] != ref))
    # the registered statistic (v1's scan_fit), reported only, on the same levels; its fit uses the reference level when it has 4 quads
    cl = [q for q in cq if q["n"] != ref or per.get(ref, 0) >= MIN_QUADS]
    nl = sorted(set(q["n"] for q in cl))
    if len(nl) >= 10:                     # v1's E184-C block (score_e184.score_s), line for line, on these quads
        fr = c.scan_fit([{"n": q["n"], "y": q["y"]} for q in cl], ref)
        br = fr["best"]["b_w_per_minion"]
        rw = c.median([q["base"] for q in cl])
        base0 = rw - ref * br
        reg_c = {"verdict": "SEEN" if fr["max_abs_t"] > s1.T_CRIT else "NONE SEEN", "t_crit": s1.T_CRIT, "max_abs_t": r6(fr["max_abs_t"]),
                 "best_break_n": fr["best"]["break_n"], "best_break_board_w": r6(base0 + fr["best"]["break_n"] * br),
                 "best_d_w": r6(fr["best"]["d_w"]), "best_se_d_w": r6(fr["best"]["se_d_w"]), "scan_zeros_base_w": r6(base0),
                 "scan_top_w": r6(base0 + max(nl) * br), "band_w": [CARRY[0], CARRY[2]],
                 "bound_w": r6(max(abs(r["d_w"]) + 1.96 * r["se_d_w"] for r in fr["rows"])), "levels": len(nl), "quads": len(cl)}
    else:
        reg_c = {"verdict": "NOT SCORED", "why": "%d scan levels" % len(nl)}
    if len(ns) < 10:
        return {"verdict": "NOT SCORED", "why": "%d scan levels besides the reference with at least %d kept quads (A2-4 and A3-4: at least 10)"
                % (len(ns), MIN_QUADS), "levels_left_out": left, "reported_registered_statistic": reg_c}
    fit = A2["scan_fit_a2"]([{"n": q["n"], "y": q["y"]} for q in cq], ref)
    best = fit["best"]
    b = best["b_w_per_minion"]
    ref_w = c.median([q["base"] for q in cq])
    brk_w = ref_w + (best["break_n"] - ref) * b
    lo_band, hi_band = CARRY[0] - 12 * b, CARRY[2] + 12 * b
    seen = fit["max_abs_t"] > T_A2
    reading = None
    if seen:
        reading = "a step near code 1024" if lo_band <= brk_w <= hi_band else "a step at %.3f W, outside the carry band" % brk_w
    nul = fit["reference_null"]
    return {"verdict": "SEEN" if seen else "NONE SEEN", "statistic": "A2-1 (an intercept; the reference level set aside), on A2-4's levels (A3-4)",
            "t_crit": T_A2, "max_abs_t": r6(fit["max_abs_t"]), "best_break_n": best["break_n"], "best_break_board_w": r6(brk_w),
            "best_d_w": r6(best["d_w"]), "best_se_d_w": r6(best["se_d_w"]), "reading": reading,
            "band_w_widened_one_level": [r6(lo_band), r6(hi_band)], "reference_reading_w": r6(ref_w),
            "scan_levels": len(ns), "quads": sum(1 for q in cq if q["n"] != ref), "levels_left_out": left,
            "reference_null": {"quads": nul["quads"], "mean_w": r6(nul["mean_w"]), "ci95": [r6(x) for x in nul["ci95"]]} if nul else None,
            "bound_w": r6(max(abs(r["d_w"]) + 1.96 * r["se_d_w"] for r in fit["rows"])),
            "reported_registered_statistic": reg_c}


def score_s(red):
    res = s2.score_s(red)
    if not (red.get("session") or {}).get("gate_ok"):
        return res
    res["E184-C"] = score_c(red)
    for rule in ("E184-L", "E184-P"):
        if res.get(rule, {}).get("a2"):
            governing_fields(res[rule])
    return res


def score_b(red):
    return s2.score_b(red)


TOP_KEYS = ("governing_R", "governing_ci95", "mean_w", "max_abs_t", "best_break_board_w", "best_d_w", "meter", "reading", "f", "f_ci95",
            "spread_min_over_avg", "why", "scan_levels", "levels_left_out")


def md(out):
    L = ["# E184 scored (score_e184_v3.py: dated amendments A2 and A3, kit notes 1 and 2)", ""]
    for arm in ("S", "B"):
        a = out.get("arm_" + arm)
        L.append("## Arm %s" % arm)
        if not isinstance(a, dict):
            L.append("NOT SCORED (no reduced file)")
            L.append("")
            continue
        sg = a.get("session") or {}
        L.append("- session gate: %s (T0 %s)%s" % ("holds" if sg.get("gate_ok") else "DOES NOT HOLD", sg.get("t0"),
                                                  "" if sg.get("gate_ok") else ": " + "; ".join(sg.get("reasons", []))))
        for d in sg.get("departures") or []:
            L.append("  - departure: %s" % d)
        if a.get("set_aside_passes"):
            L.append("- passes set aside: %s" % json.dumps({p: v["why"] for p, v in a["set_aside_passes"].items()}, sort_keys=True))
        for k in sorted(a):
            v = a[k]
            if isinstance(v, dict) and "verdict" in v:
                extra = {kk: vv for kk, vv in v.items() if kk in TOP_KEYS}
                if "governing_rule" in v:
                    extra["governing_rule"] = v["governing_rule"]
                L.append("- **%s**: %s %s" % (k, v["verdict"], json.dumps(extra, sort_keys=True)))
                if "registered_R" in v:
                    L.append("  - registered R (reported, A2-2): %s %s reads %s; null-corrected R: %s %s; own null %s; disagree %s" % (
                        v["registered_R"], json.dumps(v["registered_ci95"]), v["registered_verdict"], v.get("null_corrected_R"),
                        json.dumps(v.get("null_corrected_ci95")), v["a2"].get("own_null"), v["a2"].get("disagree")))
                if v.get("a2"):
                    L.append("  - A2-3: %s" % v["a2"].get("words"))
                if k == "E184-C" and v.get("reported_registered_statistic"):
                    rr = v["reported_registered_statistic"]
                    L.append("  - registered statistic (reported only): %s %s" % (rr.get("verdict"), json.dumps(
                        {x: rr[x] for x in ("max_abs_t", "t_crit", "best_break_board_w", "levels", "why") if x in rr}, sort_keys=True)))
            elif isinstance(v, dict) and k == "E184-T":
                for kk, vv in sorted(v.items()):
                    L.append("- **%s %s**: %s %s" % (k, kk, vv["verdict"], json.dumps({x: vv[x] for x in vv if x in ("mean_s", "ci95")})))
        L.append("- reported: `%s`" % json.dumps(a.get("reported"), sort_keys=True)[:1500])
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s")
    ap.add_argument("--b")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {"what": "E184 scored (score_e184_v3.py): the registration's rules under dated amendments A1, A2 and A3, kit notes 1 and 2",
           "arm_S": None, "arm_B": None, "t_crit_a2": T_A2}
    if a.s:
        out["arm_S"] = score_s(json.load(open(a.s)))
    if a.b:
        out["arm_B"] = score_b(json.load(open(a.b)))
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "scored-e184-v3.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(a.out, "scored-e184-v3.md"), "w").write(md(out))
    print(md(out))


if __name__ == "__main__":
    main()
