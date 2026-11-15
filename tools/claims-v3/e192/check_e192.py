#!/usr/bin/env python3
"""E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE CHECKER FOR E192.md SECTION 7, run after the data commit by
step 13 (rb/s24_reduce_e192.sh) on the registered reducer's output and the session's raw records. E192.md section 7: "computed after the
data from the reducer's output and the raw records by the kit's checker, with these thresholds and no other". Each check is reported
PASS or FAIL with its numbers (or NOT DECIDED where a quantity has no SE, or REPORTED where section 7 registers a report, not a test).
It removes no datum: a failed check is reported beside the prices it qualifies (E192.md section 11).
  1. check_bad 0 and 1,024 participants on every launch (passes 0-8); retired / body within 0.1% of 259/256 on every run;
  2. every board sample in a run's window (the reducer's [t0 + 1 s, min(t0 + 3 s, t1)]) at 600 MHz; every rail-voltage sample in a run's
     rail window ([t0 + 2.5 s, t1]) within +-3 mV of its pass's median; L1 data misses 0 on every run;
  3. instruction-cache misses per iteration equal across arms (the arms' means over the measured passes; no threshold is registered, so
     EQUAL means identical, and anything else is reported as NOT EQUAL with its spread);
  4. rates equal across arms within 0.5% (each arm's mean rate against the median arm's); a slower arm named; runs off protocol counted;
  5. additivity within 2 SE: add.a.all - add.z - the four field rungs, and add.a.f12 - add.z - (f1 + f2), each against zero, per meter;
  6. linearity within 2 SE of zero: the f2 count ladder's and both carry ladders' quadratic terms, per meter;
  7. the zero rungs xor.z and and.z against add.z: REPORTED (the opcode alone);
  8. charge per instruction (energy / V on the rail, / 12 V at the board): REPORTED, both splits.
Standard library only; it reads, never writes beside --out. Nothing here is a forecast or scores one.
    /usr/bin/python3 -I -B check_e192.py <the session's run directory> <intbits.json> [--out checks-e192.json]
Prints one line per check and "CHECKS-E192: ..." last; exit 0 when it ran (the verdicts are reports), 2 when an input is missing.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics
import sys

RET = 259 / 256


def jl(p):
    out = []
    with open(p, errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def within2se(rec):
    if not rec:
        return "NOT DECIDED", "no value"
    if rec.get("se") is None:
        return "NOT DECIDED", "%.4g, no SE (fewer than two measured passes)" % rec["mean"]
    ok = abs(rec["mean"]) <= 2 * rec["se"]
    return ("PASS" if ok else "FAIL"), "%.4g +- %.4g (2 SE %.4g)" % (rec["mean"], rec["se"], 2 * rec["se"])


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    rd, ij = argv[0], argv[1]
    out = argv[argv.index("--out") + 1] if "--out" in argv else None
    for p in (os.path.join(rd, "runs.jsonl"), os.path.join(rd, "telemetry.jsonl"), ij):
        if not os.path.exists(p):
            print("CHECKS-E192: missing input %s" % p)
            return 2
    raw = [r for r in jl(os.path.join(rd, "runs.jsonl")) if r.get("pass", -1) >= 0]
    tel = jl(os.path.join(rd, "telemetry.jsonl"))
    red = json.load(open(ij))
    runs = [r for r in red.get("runs", []) if r.get("pass", -1) >= 0]
    used = {tuple(p)[1] if isinstance(p, list) else p for p in red.get("passes", [])}
    warm = red.get("warmup")
    used.discard(warm[1] if isinstance(warm, list) else warm)
    res = {}

    # 1
    nb = sum(1 for r in raw if r.get("check_bad") != 0)
    np_ = sum(1 for r in raw if r.get("participants") != 1024)
    bad_ret = [r for r in runs if not (r.get("ret_over_body") == r.get("ret_over_body") and abs(r["ret_over_body"] / RET - 1) <= 0.001)]
    v = "PASS" if (raw and nb == 0 and np_ == 0 and not bad_ret) else "FAIL"
    res["1"] = {"verdict": v, "launches": len(raw), "check_bad_launches": nb, "participants_not_1024": np_, "runs": len(runs),
                "runs_ret_over_body_outside_0.1pct": len(bad_ret),
                "ret_over_body_range": [min((r["ret_over_body"] for r in runs), default=None), max((r["ret_over_body"] for r in runs), default=None)]}
    # 2
    t = [s.get("t_ms", 0) / 1000.0 for s in tel]
    off600, nwin = 0, 0
    mv_bad, mv_n = 0, 0
    l1 = sum(1 for r in runs if r.get("l1d_miss", 0) != 0)
    by_pass = {}
    for r in runs:
        by_pass.setdefault(r["pass"], []).append(r)
    for p, rs in by_pass.items():
        vs = []
        for r in rs:
            for s, ts in zip(tel, t):
                if r["t0"] + 2.5 <= ts <= r["t1"]:
                    mv = ((s.get("sp") or {}).get("minion_mv") or [None])[0]
                    if isinstance(mv, (int, float)):
                        vs.append(mv)
        med = statistics.median(vs) if vs else None
        for r in rs:
            for s, ts in zip(tel, t):
                if r["t0"] + 1.0 <= ts <= min(r["t0"] + 3.0, r["t1"]):
                    nwin += 1
                    mhz = (s.get("mhz") or {}).get("minion")
                    if not (isinstance(mhz, (int, float)) and abs(mhz - 600) < 0.5):
                        off600 += 1
                if med is not None and r["t0"] + 2.5 <= ts <= r["t1"]:
                    mv = ((s.get("sp") or {}).get("minion_mv") or [None])[0]
                    if isinstance(mv, (int, float)):
                        mv_n += 1
                        mv_bad += abs(mv - med) > 3
    v = "PASS" if (nwin and off600 == 0 and mv_bad == 0 and l1 == 0) else "FAIL"
    res["2"] = {"verdict": v, "board_window_samples": nwin, "off_600_MHz": off600, "rail_mv_samples": mv_n, "rail_mv_beyond_3mV": mv_bad,
                "runs_with_l1d_misses": l1}
    # 3
    per = {}
    for (p, seq) in sorted({(r["pass"], r["seq"]) for r in raw}):
        if p not in used:
            continue
        rs = [r for r in raw if r["pass"] == p and r["seq"] == seq]
        if not rs or rs[0].get("role") == "burnin":
            continue
        it = sum(r["iters"] for r in rs)
        if it:
            per.setdefault(rs[0]["arm"], []).append(sum(r["icache_miss"] for r in rs) / it)
    means = {a: statistics.mean(v) for a, v in per.items()}
    if means:
        lo, hi = min(means.values()), max(means.values())
        res["3"] = {"verdict": "EQUAL" if lo == hi else "NOT EQUAL", "min": lo, "max": hi, "spread": hi - lo,
                    "note": "no threshold is registered: EQUAL means identical", "per_arm": means}
    else:
        res["3"] = {"verdict": "NOT DECIDED", "note": "no measured pass"}
    # 4
    rates = {}
    for r in runs:
        if r["pass"] in used and r.get("role") != "burnin" and r.get("rate") == r.get("rate"):
            rates.setdefault(r["arm"], []).append(r["rate"])
    rm = {a: statistics.mean(v) for a, v in rates.items()}
    offp = sum(1 for r in runs if r["pass"] in used and r.get("approach_on_protocol") is False)
    if rm:
        med = statistics.median(rm.values())
        dev = {a: v / med - 1 for a, v in rm.items()}
        slow = sorted((a for a, d in dev.items() if d < -0.005), key=lambda a: dev[a])
        fast = sorted(a for a, d in dev.items() if d > 0.005)
        res["4"] = {"verdict": "PASS" if not slow and not fast else "FAIL", "median_rate": med, "slower_arms": slow,
                    "faster_arms": fast, "max_abs_dev": max(abs(d) for d in dev.values()), "runs_off_protocol": offp}
    else:
        res["4"] = {"verdict": "NOT DECIDED", "note": "no measured pass", "runs_off_protocol": offp}
    # 5 and 6
    for key, names in (("5", ("additivity_all_minus_fields_pJ", "f12_minus_f1_f2_pJ")),
                       ("6", ("hamming_f2_quad_fJ", "S_cr_quad_fJ", "S_crb_quad_fJ"))):
        d = {}
        for meter in ("board", "rail"):
            for n in names:
                d["%s.%s" % (meter, n)] = within2se((red.get("ladders") or {}).get(meter, {}).get(n))
        vs = [x[0] for x in d.values()]
        res[key] = {"verdict": "FAIL" if "FAIL" in vs else ("NOT DECIDED" if "NOT DECIDED" in vs else "PASS"),
                    "items": {k: {"verdict": a, "value": b} for k, (a, b) in d.items()}}
    # 7 and 8
    arms = red.get("arms") or {}
    res["7"] = {"verdict": "REPORTED", "xor.z_vs_add.z_pJ_board": (arms.get("xor.z") or {}).get("contrast_pJ_board"),
                "and.z_vs_add.z_pJ_board": (arms.get("and.z") or {}).get("contrast_pJ_board"),
                "xor.z_vs_add.z_pJ_rail": (arms.get("xor.z") or {}).get("contrast_pJ_rail"),
                "and.z_vs_add.z_pJ_rail": (arms.get("and.z") or {}).get("contrast_pJ_rail")}
    res["8"] = {"verdict": "REPORTED", "arms_with_electrons_rail": sum(1 for a in arms.values() if "contrast_electrons_rail" in a),
                "arms_with_electrons_12V": sum(1 for a in arms.values() if "contrast_electrons_12V" in a)}
    for k in sorted(res):
        print("check %s: %s %s" % (k, res[k]["verdict"], json.dumps({x: y for x, y in res[k].items() if x not in ("verdict", "per_arm", "items")})[:300]))
    if out:
        with open(out, "w") as f:
            json.dump({"python": sys.version.split()[0], "used_passes": sorted(used), "checks": res}, f, indent=1)
    print("CHECKS-E192: " + "; ".join("%s %s" % (k, res[k]["verdict"]) for k in sorted(res)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
