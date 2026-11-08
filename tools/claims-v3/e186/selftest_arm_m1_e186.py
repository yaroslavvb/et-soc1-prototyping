#!/usr/bin/env python3
"""E186 (Q158): the self-test of october-forecast-model's reader (arm_m1_read_e186.py), on SYNTHETIC sessions only: scorer files in E182's
scored.json form made here from the frozen figures, never a card and never a real run's data.

    /usr/bin/python3 -B tools/claims-v3/e186/selftest_arm_m1_e186.py <a scratch dir outside the repository>

Cases: (P) E186 as planned: the ten session trains at M12's lines, nothing else run; (A) all 22 trains run at v4's centres, every covered
kind at v4's level; (H) every covered train 0.1 W above v4's centre and every covered kind 0.3 W above; (L) the same below; (N) one covered
train NOT SCORED; (T) the model's file with one digit changed (exit 2); (X) a scorer's file with no trains (exit 3). In each, the reader's
words must equal this test's own placement. Exit 0 only if every case passes.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
READER = os.path.join(HERE, "arm_m1_read_e186.py")
M1 = json.load(open(os.path.join(HERE, "m1-october-forecast-model-e186.json")))
PLAN = json.load(open(os.path.join(HERE, "plan-e186.json")))
FC = json.load(open(os.path.join(HERE, "forecast-e186.json")))
SE = 0.0025
HW = 2.04 * SE


def iv(m):
    return {"mean": m, "lo": m - HW, "hi": m + HW, "se": SE, "n": 32, "df": 31, "hw": HW}


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def run(scored, d, name, model=None):
    p = os.path.join(d, f"{name}-scored.json")
    json.dump(scored, open(p, "w"))
    cmd = ["/usr/bin/python3", "-B", READER, "--scored", p, "--out", os.path.join(d, f"{name}-arm")]
    if model:
        cmd += ["--model", model]
    r = subprocess.run(cmd, capture_output=True, text=True)
    o = json.load(open(os.path.join(d, f"{name}-arm.json"))) if r.returncode == 0 else None
    return r.returncode, o


def main():
    d = os.path.abspath(sys.argv[1])
    os.makedirs(d, exist_ok=True)
    res = []

    def check(name, ok, note=""):
        res.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'} {name} {note}")

    cov_t = [t for t, v in M1["trains"].items() if v["covered"]]
    cov_k = [k for k, v in M1["kinds"].items() if v["covered"]]
    # (P) the session as planned: its ten trains at M12's lines
    sc = {"trains": {t: iv(FC["trains"][t]["M12_w"]) for t in PLAN["session_trains"]}, "reported": {"kinds": {}}}
    rc, o = run(sc, d, "P")
    want = {t: ("not covered" if not M1["trains"][t]["covered"] else ("read" if t in PLAN["session_trains"] else "not run")) for t in M1["trains"]}
    check("P: the planned session, every train's reading", rc == 0 and all(o["trains"][t]["reading"] == want[t] for t in want),
          json.dumps(o["counts"]) if o else rc)
    check("P: no covered train is in the session (nothing read)", rc == 0 and o["counts"]["trains"].get("read", 0) == 0)
    # (A) every train run, at v4's centre where covered (M12's line elsewhere); covered kinds at v4's level
    sc = {"trains": {t: iv(M1["trains"][t]["v4_W"] if M1["trains"][t]["covered"] else FC["trains"][t]["M12_w"]) for t in M1["trains"]},
          "reported": {"kinds": {M1["kinds"][k]["key"]: {"D_w": M1["kinds"][k]["v4_W"]} for k in cov_k}}}
    rc, o = run(sc, d, "A")
    ok = rc == 0 and all(o["trains"][t]["reading"] == "read" and o["trains"][t]["model_in_interval"] == "inside" for t in cov_t)
    ok = ok and all(o["trains"][t]["reading"] == "not covered" for t in M1["trains"] if t not in cov_t)
    ok = ok and all(o["kinds"][k]["reading"] == "read" and o["kinds"][k]["measured_in_model_band"] == "inside" for k in cov_k)
    check("A: all 22 run at v4's centres: inside on the 8 covered, 'not covered' on the 14 others; covered kinds inside the band", ok)
    # (H) and (L): every covered train 0.1 W above (below) v4's centre; covered kinds 0.3 W above (below)
    for name, dx, dk in (("H", 0.1, 0.3), ("L", -0.1, -0.3)):
        sc = {"trains": {t: iv(M1["trains"][t]["v4_W"] + dx) for t in cov_t},
              "reported": {"kinds": {M1["kinds"][k]["key"]: {"D_w": M1["kinds"][k]["v4_W"] + dk} for k in cov_k}}}
        rc, o = run(sc, d, name)
        ok = rc == 0
        for t in cov_t:
            v, m = o["trains"][t], M1["trains"][t]
            e = m["v4_W"] + dx
            ok = ok and v["model_in_interval"] == where(m["v4_W"], e - HW, e + HW) == ("below" if dx > 0 else "above")
            ok = ok and v["estimate_in_model_band"] == where(e, *m["v4_band"])
            ok = ok and v["sign"] == ("no sign to compare" if m["v4_W"] == 0 or e == 0 else
                                      ("the estimate's sign" if (m["v4_W"] > 0) == (e > 0) else "the other sign"))
        for k in cov_k:
            ok = ok and o["kinds"][k]["measured_in_model_band"] == where(M1["kinds"][k]["v4_W"] + dk, *M1["kinds"][k]["v4_band"])
        check(f"{name}: every covered train {dx:+.1f} W off: the reader's words equal the test's own placement", ok)
    # (N) one covered train NOT SCORED
    sc = {"trains": {t: iv(M1["trains"][t]["v4_W"]) for t in cov_t}}
    sc["trains"][cov_t[0]] = {"mean": None, "lo": None, "hi": None, "se": None, "n": 3, "df": None}
    rc, o = run(sc, d, "N")
    check("N: a NOT SCORED train reads 'not read'", rc == 0 and o["trains"][cov_t[0]]["reading"] == "not read"
          and all(o["trains"][t]["reading"] == "read" for t in cov_t[1:]))
    # (T) a copy of the model's file with one digit changed
    bad = copy.deepcopy(M1)
    bad["trains"][cov_t[0]]["v4_W"] = round(bad["trains"][cov_t[0]]["v4_W"] + 0.0001, 4)
    bp = os.path.join(d, "m1-tampered.json")
    open(bp, "w").write(json.dumps(bad, indent=1, sort_keys=True) + "\n")
    rc, _ = run({"trains": {}}, d, "T", model=bp)
    check("T: a model file with one digit changed is refused (exit 2)", rc == 2)
    # (X) a scorer's file with no trains
    rc, _ = run({"reported": {}}, d, "X")
    check("X: a scorer's file without trains is refused (exit 3)", rc == 3)
    n = sum(1 for _, ok in res if ok)
    print(f"SELFTEST-ARM-M1-E186 {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'}")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
