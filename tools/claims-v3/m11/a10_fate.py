#!/usr/bin/env python3
"""M11's dated amendment A10 (Sat 7 Nov 2026, before any E185 datum): A9's arm's fate by the stated rule A10-R, read from E181's committed
score. Desk only; it reads committed files and writes one JSON file and its printout. It fits nothing and reads no verdict, rms or HM
reading of either chain: only the four validity checks A10-R names, each stated in A9 (cd5bed77) before E181's first datum.

  A10-R  A9's arm becomes M11's registered reading for every M11 aifoundry3 session read after this amendment (E185 on), and the
         measured-pass-only reading a reported arm beside it, if and only if E181's committed arm passes all four:
           V1  the arm read SCORED on E181 (A9-1's refusals not met): the smoke's telemetry there with at least 10 readable samples, and
               the gap between the passes in (0, 600] s;
           V2  every grid point inside the measured pass the registered reading's own (measured_points_identical), and R the registered
               R in every hold (A9-1);
           V3  delta e under 0.001 C in size on every hold after the first (A9-4: "A larger delta e there means the arm's grid or input is
               wrong"), at the committed score's printed precision;
           V4  delta e on the first hold of the mechanism's sign (positive: A9-4) and inside a factor of two of A9-5's expectation for
               E181's smoke, the chain's own account of E176's planned smoke at R0's anchor (a9-posthoc.json > sessions > E176 >
               R0_anchor_window > pred_two_less_one_C, +0.147 C): in [0.5, 2] x that.
         Any one failing: the arm is retired (its grid or its input is wrong), and the registered reading stays.

    /usr/bin/python3 -B tools/claims-v3/m11/a10_fate.py <lab repo top> <out.json> [<out.txt>]
Python 3.9, standard library only. SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402

E181D = "docs/reports/data/2026-11-06-e181-m11-session2-aifoundry3"
SESSION = "S2:p18120"
A9_POSTHOC = "tools/claims-v3/m11/a9-posthoc.json"
LISTS = ((E181D + "/SHA256SUMS", E181D, "scored-m11.json"), ("tools/claims-v3/m11/SHA256SUMS-a9", ".", A9_POSTHOC))
V3_LINE_C = 0.001
V4_FACTORS = (0.5, 2.0)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def listed(top, lst, base, name):
    """the file's sha256 against its committed list's line, or a problem"""
    want = None
    for line in open(os.path.join(top, lst)):
        parts = line.split()
        if len(parts) == 2 and os.path.normpath(os.path.join(base, parts[1])) == os.path.normpath(name if base == "." else os.path.join(base, name)):
            want = parts[0]
    got = sha(os.path.join(top, name if base == "." else os.path.join(base, name)))
    return got, want, (None if want == got else f"{name}: sha256 {got[:12]} against the list's {str(want)[:12]}")


def main():
    if len(sys.argv) not in (3, 4):
        print(__doc__)
        return 2
    top, out = os.path.abspath(sys.argv[1]), sys.argv[2]
    res = {"amendment": "A10", "rule": "A10-R", "inputs": {}, "problems": []}
    for lst, base, name in LISTS:
        got, want, bad = listed(top, lst, base, name)
        res["inputs"][(name if base == "." else base + "/" + name)] = {"sha256": got, "list": lst, "listed": want}
        if bad:
            res["problems"].append(bad)
    if res["problems"]:
        json.dump(res, open(out, "w"), indent=1, sort_keys=True)
        print("REFUSED: " + "; ".join(res["problems"]))
        return 1
    sc = json.load(open(os.path.join(top, E181D, "scored-m11.json")))
    arm = sc["arm_A9"]
    s = arm["sessions"][SESSION]
    info, holds = s["info"], s["holds"]
    reg = sc["sessions"][SESSION]["holds"]
    order = [nm for nm in sc["sessions"][SESSION]["order"]["by_first_launch"]]
    first, later = order[0], order[1:]
    ph = json.load(open(os.path.join(top, A9_POSTHOC)))
    expect = ph["sessions"]["E176"]["R0_anchor_window"]["pred_two_less_one_C"]
    lo, hi = V4_FACTORS[0] * expect, V4_FACTORS[1] * expect
    v1 = {"pass": s.get("reads") == "SCORED" and info["smoke_readable_samples"] >= 10 and 0.0 < info["gap_s"] <= 600.0,
          "reads": s.get("reads"), "smoke_readable_samples": info["smoke_readable_samples"], "gap_s": info["gap_s"]}
    sameR = {nm: holds[nm]["R_C"] == reg[nm]["R_C"] for nm in order}
    v2 = {"pass": bool(info["measured_points_identical"]) and all(sameR.values()),
          "measured_points_identical": info["measured_points_identical"], "R_the_registered_R": sameR}
    d_later = {nm: holds[nm]["delta_e_C"] for nm in later}
    v3 = {"pass": all(abs(x) < V3_LINE_C for x in d_later.values()), "line_C": V3_LINE_C, "delta_e_C": d_later,
          "precision": "the committed score's three decimals"}
    d1 = holds[first]["delta_e_C"]
    v4 = {"pass": d1 > 0 and lo <= d1 <= hi, "first_hold": first, "delta_e_C": d1, "expected_C": expect, "band_C": [lo, hi],
          "sign_by_mechanism": "positive (A9-4)"}
    checks = {"V1": v1, "V2": v2, "V3": v3, "V4": v4}
    ok = all(c["pass"] for c in checks.values())
    res.update({"session": SESSION, "order": order, "checks": checks, "all_pass": ok,
                "fate": ("ADOPTED: A9's arm is M11's registered reading for every M11 aifoundry3 session read after A10 (E185 on); the "
                         "measured-pass-only reading is a reported arm beside it") if ok else
                        "RETIRED: a validity check failed (A10-R); the registered reading stays and the arm is no longer read",
                "not_read": "no verdict, rms or HM reading of either chain enters A10-R (E181's HM-CAL reads BETTER on the arm and NOT "
                            "RESOLVED on the registered reading; neither is an input)"})
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    lines = [f"A10-R on E181 ({SESSION}), from {E181D}/scored-m11.json (sha256 {res['inputs'][E181D + '/scored-m11.json']['sha256'][:16]}..., as listed)",
             f"  V1 SCORED: {v1['reads']}; smoke samples {v1['smoke_readable_samples']}; gap {v1['gap_s']} s -> {'PASS' if v1['pass'] else 'FAIL'}",
             f"  V2 grid identical {v2['measured_points_identical']}; R the registered R in {sum(sameR.values())} of {len(sameR)} holds -> "
             f"{'PASS' if v2['pass'] else 'FAIL'}",
             f"  V3 later holds' delta e {d_later} (line {V3_LINE_C} C) -> {'PASS' if v3['pass'] else 'FAIL'}",
             f"  V4 {first}'s delta e {d1:+.3f} C in [{lo:+.4f}, {hi:+.4f}] C (expected {expect:+.4f} C) -> {'PASS' if v4['pass'] else 'FAIL'}",
             f"FATE: {res['fate']}"]
    txt = "\n".join(lines)
    print(txt)
    if len(sys.argv) == 4:
        open(sys.argv[3], "w").write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
