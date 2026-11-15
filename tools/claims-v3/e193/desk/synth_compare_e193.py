#!/usr/bin/env python3
"""E193 desk check of code: the unchanged reducer's output beside what synth_session_e193.py put in.

    python3 -I -B synth_compare_e193.py <injected.json> <x04.json> [--exact]

Prints, per arm, the board W over idle and the minion rail's W over idle, reduced against injected (ARBITRARY TEST VALUES:
not a forecast and not a measurement); the fits' slopes and intercepts against the injected laws; the train contrasts;
the registered checks' verdicts against the verdicts the injected values imply; the dropped runs against the injected
faults. With --exact (a noise-free session) every reduced value must equal the injected one within 1e-6 W (1e-6 relative
for the per-op and per-wake prices in pJ): CONSISTENT or NOT CONSISTENT. Without it (a realistic session) it reports the
errors and checks only that exactly the injected faults were dropped.
"""
import json
import math
import sys

inj = json.load(open(sys.argv[1]))
red = json.load(open(sys.argv[2]))
exact = "--exact" in sys.argv[3:]
TOL = 1e-6
bad = []
errs = {"board": [], "minion": [], "fits": [], "trains": []}


def cmp(kind, name, got, want, tol=TOL):
    if "pJ" in name:
        tol = TOL * max(1.0, abs(want))     # prices in pJ: 1e-6 relative (the per-wake law is set from the first run's
                                            # wakes a second, the reducer averages its runs': they differ by about 1e-8)
    d = got - want if (got is not None and want is not None) else float("nan")
    errs[kind].append(abs(d) if d == d else float("inf"))
    ok = d == d and abs(d) <= tol
    if exact and not ok:
        bad.append("%s %s: reduced %r, injected %r" % (kind, name, got, want))
    return d


rf = inj["rail_factor"]["minion_w"]
mode = "realistic" if inj["realistic"] else ("exact, launch edges between milliseconds" if inj.get("subms") else "exact")
print("session %s (%s); injected values: %s" % (inj["session"], mode, inj["note"]))
print("\nper arm: n kept, board W over idle reduced / injected / difference; minion rail reduced / injected / difference")
for name, v in sorted(inj["arms"].items()):
    r = red["arms"].get(name)
    if r is None:
        bad.append("arm %s missing from the reduction" % name)
        print("  %-14s MISSING" % name)
        continue
    db = cmp("board", name, r["board_w"], v["board_w"])
    dm = cmp("minion", name, r["minion_w"], rf * v["board_w"])
    print("  %-14s n %2d  board %8.4f / %8.4f / %+.2e   minion %8.4f / %8.4f / %+.2e" % (
        name, r["n"], r["board_w"], v["board_w"], db, r["minion_w"], rf * v["board_w"], dm))

print("\ntrains: contrast B - A, board and minion rail, reduced / injected / difference")
for name, v in sorted(inj["trains"].items()):
    r = red["trains"].get(name)
    if r is None:
        bad.append("train %s missing from the reduction" % name)
        print("  %-18s MISSING" % name)
        continue
    db = cmp("trains", name, r["contrast_board_w"], v["contrast_board_w"])
    dm = cmp("trains", name + " minion", r["contrast_minion_w"], rf * v["contrast_board_w"])
    print("  %-18s n %2d  board %+8.4f / %+8.4f / %+.2e   minion %+8.4f / %+8.4f / %+.2e" % (
        name, r["n"], r["contrast_board_w"], v["contrast_board_w"], db, r["contrast_minion_w"], rf * v["contrast_board_w"], dm))

L = inj["laws"]
F = red["fits"]
print("\nfits: reduced / injected / difference")
want = []
if "tk_shires" in F:
    want += [("tk_shires slope", F["tk_shires"]["slope_w"], L["tk_shires_slope_w"]),
             ("tk_shires intercept", F["tk_shires"]["intercept_w"], L["tk_shires_intercept_w"])]
if "tk_launches" in F:
    want += [("tk_launches slope", F["tk_launches"]["slope_w"], L["tk_launches_slope_w"])]
if "duty" in F:
    want += [("duty slope", F["duty"]["slope_w"], L["duty_slope_w"]), ("duty intercept", F["duty"]["intercept_w"], L["duty_intercept_w"])]
    for n in ("duty33f", "duty33k"):
        if n + "_pj_per_wake" in F["duty"]:
            want.append(("%s pJ a wake" % n, F["duty"][n + "_pj_per_wake"], L["pj_per_wake"]))
if "workers" in F:
    want += [("workers slope", F["workers"]["slope_w"], L["workers_slope_w"]),
             ("workers intercept", F["workers"]["intercept_w"], L["workers_intercept_w"])]
for cls in ("faddps", "fsgnjs"):
    k = "ladder_" + cls
    if k in F:
        for n, pj in zip(F[k]["arms"], F[k]["per_op_pj_board"]):
            want.append(("%s per-op pJ (board)" % n, pj, L["per_op_pj"][cls]))
        for n, pj in zip(F[k]["arms"], F[k]["per_op_pj_minion"]):
            want.append(("%s per-op pJ (minion rail)" % n, pj, rf * L["per_op_pj"][cls]))
if "mask_lanes" in F:
    want += [("mask slope", F["mask_lanes"]["slope_w"], L["mask_slope_w"]),
             ("mask intercept", F["mask_lanes"]["intercept_w"], L["mask_intercept_w"])]
for name, got, w in want:
    d = cmp("fits", name, got, w)
    print("  %-32s %12.6f / %12.6f / %+.2e" % (name, got, w, d))
print("  fits reported by the reducer: %s" % ", ".join(sorted(F)))

C = red["checks"]
print("\nregistered checks (the reducer's verdicts; the verdict the injected values imply):")
CAT = {"spin2": 2.496, "faddps_p1": 10.212, "fsgnjs_p1": 6.122}
for n, cat in CAT.items():
    k = "1_2_catalogue_" + n
    if k in C:
        imp = abs(inj["arms"][n]["board_w"] / (cat * 992 / 1024) - 1) <= 0.15
        ok = C[k]["pass"] == imp
        if not ok:
            bad.append("check %s: reducer %s, implied %s" % (k, C[k]["pass"], imp))
        print("  %-26s reducer pass=%s, implied pass=%s  %s" % (k, C[k]["pass"], imp, "OK" if ok else "DIFF"))
dr = C.get("3_anchor_drift", {})
print("  3_anchor_drift: %d boundaries, flagged %d, largest |drift| %.2e W" % (
    len(dr.get("by_block_w", {})), len(dr.get("flagged", [])),
    max([abs(v) for v in dr.get("by_block_w", {}).values()] or [0])))
if exact and dr.get("flagged"):
    bad.append("anchor drift flagged on a session with no drift")
d4 = C.get("4_device_ok", {})
print("  4_device_ok: runs %s, trains %s, dropped_device %s, dropped_clock %s" % (
    d4.get("runs"), d4.get("trains"), d4.get("dropped_device"), d4.get("dropped_clock")))
want_dev = 1 if "faults" in inj else 0
want_clk = 1 if "faults" in inj else 0
if (d4.get("dropped_device"), d4.get("dropped_clock")) != (want_dev, want_clk):
    bad.append("dropped runs: device %s clock %s, injected %d and %d" % (d4.get("dropped_device"), d4.get("dropped_clock"),
                                                                           want_dev, want_clk))
if "faults" in inj:
    print("  injected faults: %s" % inj["faults"])
if "6_duty_linear" in C:
    print("  6_duty_linear: pass=%s, residuals %s" % (C["6_duty_linear"]["pass"],
                                                       ["%.2e" % x for x in C["6_duty_linear"]["residuals_w"]]))
    if exact and not C["6_duty_linear"]["pass"]:
        bad.append("check 6 failed on an exactly linear duty ladder")
for k, v in sorted(C.get("7_nulls", {}).items()):
    print("  7_nulls %-22s %+.6f W%s" % (k, v["w"], ("  ci95 [%+.4f, %+.4f]" % tuple(v["ci95_w"])) if "ci95_w" in v else ""))
a = inj["arms"]
if "wait2" in a and "tk" in a and "wait2-tk" in C.get("7_nulls", {}):
    cmp("fits", "null wait2-tk", C["7_nulls"]["wait2-tk"]["w"], a["wait2"]["board_w"] - a["tk"]["board_w"])
if "fadds_p16" in a and "faddps_p16" in a and "fadds_p16-faddps_p16" in C.get("7_nulls", {}):
    cmp("fits", "null fadds_p16-faddps_p16", C["7_nulls"]["fadds_p16-faddps_p16"]["w"], a["fadds_p16"]["board_w"] - a["faddps_p16"]["board_w"])

print("\nlargest |reduced - injected|: board %.2e W, minion rail %.2e W, fits %.2e, trains %.2e W" % tuple(
    max(errs[k] or [0]) for k in ("board", "minion", "fits", "trains")))
if exact:
    print("SYNTH CHECK (exact): %s" % ("CONSISTENT" if not bad else "NOT CONSISTENT"))
else:
    print("SYNTH CHECK (%s; errors reported, not judged): dropped runs %s" % (mode, "AS INJECTED" if not bad else "NOT AS INJECTED"))
for b in bad[:40]:
    print("  " + b)
sys.exit(0 if not bad else 1)
