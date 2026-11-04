#!/usr/bin/env python3
"""Q141(t2), ../REGISTRATION-step243.md section 3: the convergence rule's 243-point step, scored by Q140(m)'s recount_rule.py main(),
unchanged, with its output directory pointed here, on the committed nine-, 27- and 81-point counts and this step's counts. Then
summary243.json / .txt apply section 4's fallback mechanically.

    /usr/bin/python3 -B run_recount_rule_243.py                    # writes recount-rule.json/.txt, summary243.json/.txt here
    /usr/bin/python3 -B run_recount_rule_243.py --selfcheck <dir>  # this step's counts left out, output in <dir>: must rewrite
                                                                   # step81/recount-rule.json and .txt byte for byte

Inputs: ../../2026-11-04-q140m-m9/bench-check/counts-cal.json, ../../2026-11-04-q140m-m9/recount-rule/counts-pilot27.json,
../step81/counts-cal81-<n>.json and counts-cal243-<tile>-p<k>.json beside this file. main() stops on a point counted twice with
different nets or a C mismatch. Its cost lines read a pilot-run.json beside its output, which this directory does not have, so the
summary gives this step's own bench time from the run records.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
M9D = os.path.abspath(os.path.join(D, "..", "2026-11-04-q140m-m9"))
RRD = os.path.join(M9D, "recount-rule")
sys.path.insert(0, RRD)
import recount_rule as RR  # noqa: E402

TILES8 = ("fp32.cal_third_b21", "fp32.cal_pi_b21", "fp32.cal_third_b20", "fp32.cal_w67_b21", "fp32.cal_w79_b21",
          "fp32.cal_w67_b20", "fp32.cal_w79_b20", "fp32.cal_pi_b20")
CAP = RR.N_MAX
BASE = [os.path.join(M9D, "bench-check", "counts-cal.json"), os.path.join(RRD, "counts-pilot27.json")] + sorted(
    glob.glob(os.path.join(D, "step81", "counts-cal81-[0-9].json")))
STEP = sorted(glob.glob(os.path.join(HERE, "counts-cal243-*-p[12].json")))


def run_main(outdir, files):
    RR.HERE = outdir
    sys.argv = [os.path.join(RRD, "recount_rule.py")] + files
    RR.main()


def selfcheck(outdir):
    os.makedirs(outdir, exist_ok=True)
    run_main(outdir, BASE)
    ok = all(open(os.path.join(outdir, f), "rb").read() == open(os.path.join(D, "step81", f), "rb").read()
             for f in ("recount-rule.json", "recount-rule.txt"))
    print(f"SELFCHECK {'PASS' if ok else 'FAIL'}: main() on the committed 9-, 27- and 81-point counts alone "
          f"{'rewrites' if ok else 'does not rewrite'} step81/recount-rule.json and .txt byte for byte")
    sys.exit(0 if ok else 1)


def outcome(t):
    """A calibration tile's outcome under the registered rule, read at the cap (REGISTRATION-step243.md section 3)."""
    if t["first_N_meeting_bound"]:
        return f"met at {t['first_N_meeting_bound']}"
    if t["N_counted"] >= CAP:
        return "above the bound at the cap"
    return f"not counted to {CAP}"


def summary():
    r = json.load(open(os.path.join(HERE, "recount-rule.json")))
    runs = {}
    for p in sorted(glob.glob(os.path.join(HERE, "counts-cal243-*-p[12]-run.json"))):
        runs[os.path.basename(p)] = json.load(open(p))
    ok = [x for x in runs.values() if x.get("exit") == 0]
    pts = sum(x["points"] for x in ok)
    core_s = sum(x["wall_s"] * x["jobs"] for x in ok)
    S = {"_note": "Q141(t2): the convergence rule's 243-point step (REGISTRATION-step243.md), from recount-rule.json beside this file",
         "bound_w": r["bound_w"], "cap_N": CAP, "N_star_by_main": r["N_star"], "tiles": {}, "inputs": r["inputs"],
         "bench": {"runs": len(runs), "runs_exit_0": len(ok), "points": pts, "core_seconds": core_s,
                   "seconds_per_point_one_core": (core_s / pts) if pts else None, "wall_s": sum(x["wall_s"] for x in ok),
                   "machines": sorted({f"{x['machine']['arch']} {x['machine']['system']}" for x in ok})}}
    L = ["Q141(t2): the convergence rule's 243-point step, by recount_rule.py's main() (recount-rule.json, .txt beside this file)",
         "", f"{'tile':20s} {'e(9)':>6s} {'e(27)':>6s} {'e(81)':>6s} {'e(243)':>6s} {'e81/e243':>8s}  {'outcome':27s} projected N (planning)"]
    for name, t in r["tiles"].items():
        e = {n: t["by_N"][n]["e_w"] for n in t["by_N"]}
        rat = (e["81"] / e["243"]) if ("81" in e and "243" in e) else None
        oc = outcome(t)
        rec = {"e_w": e, "N_counted": t["N_counted"], "first_N_meeting_bound": t["first_N_meeting_bound"], "outcome": oc,
               "e81_over_e243": rat, "projected_N_by_inverse_sqrt_law": t["projected_N_by_inverse_sqrt_law"]}
        last = t["by_N"][str(t["N_counted"])]
        rec["mean_w_at_N_counted"] = last["mean_w"]
        rec["three_point_minus_N_counted_w"] = last["three_point_minus_N_w"]
        if oc == "above the bound at the cap":
            rec["F1_known_counting_error"] = {"N": CAP, "mean_w": last["mean_w"], "e_w": last["e_w"],
                                              "reading": "the 243-point mean, carried with e(243) as its known 1-s.e. counting error"}
        S["tiles"][name] = rec
        cells = " ".join(f"{e[n]:6.3f}" if n in e else f"{'-':>6s}" for n in ("9", "27", "81", "243"))
        rs = f"{rat:8.2f}" if rat else f"{'-':>8s}"
        L.append(f"{name:20s} {cells} {rs}  {oc:27s} {t['projected_N_by_inverse_sqrt_law'] or '-'}")
    at_cap = [n for n, t in S["tiles"].items() if t["outcome"] == "above the bound at the cap"]
    short = [n for n, t in S["tiles"].items() if t["outcome"].startswith("not counted")]
    if r["N_star"]:
        ns = r["N_star"]
    elif short:
        ns = "not yet determined: the step is incomplete"
    else:
        ns = f"not reached by uniform points at the cap ({CAP})"
    S["N_star"] = ns
    S["tiles_above_bound_at_cap"] = at_cap
    S["tiles_not_counted_to_cap"] = short
    S["F1_applies_to"] = at_cap
    S["F2"] = ("not run here: a stratified estimator needs its own registration first (REGISTRATION-step243.md section 4.2)"
               if at_cap else "not needed for the calibration set")
    S["recount_cap_N"] = CAP
    rats = [v["e81_over_e243"] for v in S["tiles"].values() if v["e81_over_e243"]]
    if rats:
        S["e81_over_e243_range"] = [min(rats), max(rats)]
        S["e81_over_e243_median"] = statistics.median(rats)
    L += ["", f"N* = {ns}"]
    L.append(f"tiles above the bound at the cap ({len(at_cap)} of 16): " + (", ".join(at_cap) if at_cap else "none"))
    if short:
        L.append(f"tiles not counted to {CAP} ({len(short)}): " + ", ".join(short))
    for n in at_cap:
        f1 = S["tiles"][n]["F1_known_counting_error"]
        L.append(f"F1: {n} is carried as {f1['mean_w']:.3f} +- {f1['e_w']:.3f} W (its 243-point mean, e(243) its known 1-s.e. "
                 f"counting error)")
    L.append(f"F2: {S['F2']}")
    if rats:
        L.append(f"e(81)/e(243) over the tiles counted at 243: {min(rats):.2f}-{max(rats):.2f} (median {S['e81_over_e243_median']:.2f}; "
                 f"the 1/sqrt(N) law gives {math.sqrt(3):.2f})")
    b = S["bench"]
    if pts:
        L.append(f"bench: {pts} points in {b['wall_s']:.0f} s of wall time over {len(ok)} runs ({', '.join(b['machines'])}), "
                 f"{b['seconds_per_point_one_core']:.1f} s a point on one core")
    json.dump(S, open(os.path.join(HERE, "summary243.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "summary243.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--selfcheck"]:
        selfcheck(os.path.abspath(sys.argv[2]))
    if len(STEP) == 0:
        raise SystemExit("no counts-cal243-*-p[12].json beside this file: nothing to score (use --selfcheck to test)")
    run_main(HERE, BASE + STEP)
    summary()
