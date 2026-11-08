#!/usr/bin/env python3
"""E186 (Q158): the self-test of note M2's reader (arm_m2_read_e186.py), on SYNTHETIC sessions only: scorer files in E182's scored.json
form made here from the frozen figures and E186's registered lines, never a card and never a real run's data (no E182 or other session's
data is read or presented as E186's).

    /usr/bin/python3 -B tools/claims-v3/e186/selftest_arm_m2_e186.py <a scratch dir outside the repository>

Cases:
  (P) E186 as planned: the ten session trains at M12's registered lines, nothing else run;
  (A) for each arm, every train at that arm's centres (M12's line where it covers none) and every kind at its levels;
  (H) and (L) every train 0.1 W above (below) v7's centres and every kind 0.3 W above (below) v7's levels;
  (F) the fallback as the scorer writes it: every session train NOT SCORED ("no train block"), the fifteen fallback kinds at v5's levels;
  (N) one covered train NOT SCORED;
  (T) the model's file with one digit changed (exit 2); (K) E186's list with one byte changed (exit 2); (X) a scorer's file with no trains
  (exit 3); (W) the reader writes its two outputs and nothing else.
In each, the reader's words and errors must equal this test's own placement and arithmetic. Exit 0 only if every case passes.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
READER = os.path.join(HERE, "arm_m2_read_e186.py")
M2 = json.load(open(os.path.join(HERE, "m2-october-forecast-model-e186.json")))
PLAN = json.load(open(os.path.join(HERE, "plan-e186.json")))
FC = json.load(open(os.path.join(HERE, "forecast-e186.json")))
LST = json.load(open(os.path.join(TOP, "tools", "claims-v3", "m12", "kinds-m12-e186.json")))
KEY = {k["e186_id"]: k["key"] for k in LST["kinds"]}
ARMS = M2["arm_order"]
SE = 0.0025
HW = 2.04 * SE


def iv(m):
    return {"mean": m, "lo": m - HW, "hi": m + HW, "se": SE, "n": 32, "df": 31, "hw": HW}


def nsc(why="no train block"):
    return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "hw": None, "why": why}


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def sign_word(m, est):
    if m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def run(scored, d, name, model=None, lst=None):
    p = os.path.join(d, f"{name}-scored.json")
    json.dump(scored, open(p, "w"))
    cmd = ["/usr/bin/python3", "-B", READER, "--scored", p, "--out", os.path.join(d, f"{name}-arm")]
    if model:
        cmd += ["--model", model]
    if lst:
        cmd += ["--list", lst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    o = json.load(open(os.path.join(d, f"{name}-arm.json"))) if r.returncode == 0 else None
    return r.returncode, o


def expect(scored, arm):
    """this test's own placement: every word and error the reader should write for one arm"""
    a = M2["arms"][arm]
    tr = scored.get("trains", {})
    kd = (scored.get("reported") or {}).get("kinds") or {}
    want = {"trains": {}, "kinds": {}}
    te, ke = [], []
    for tid, v in a["trains"].items():
        if not v["covered"]:
            want["trains"][tid] = ("not covered",)
        elif tid not in tr:
            want["trains"][tid] = ("not run",)
        elif tr[tid].get("lo") is None:
            want["trains"][tid] = ("not read",)
        else:
            t = tr[tid]
            want["trains"][tid] = ("read", where(v["W"], t["lo"], t["hi"]), sign_word(v["W"], t["mean"]), where(t["mean"], *v["band_W"]))
            te.append(v["W"] - t["mean"])
    for kid, v in a["kinds"].items():
        r = kd.get(KEY[kid])
        if not v["covered"]:
            want["kinds"][kid] = ("not covered",)
        elif r is None or r.get("D_w") is None:
            want["kinds"][kid] = ("not run",)
        else:
            want["kinds"][kid] = ("read", where(r["D_w"], *v["band_W"]))
            ke.append(v["W"] - r["D_w"])
    rms = lambda e: math.sqrt(sum(x * x for x in e) / len(e)) if e else None
    return want, rms(te), rms(ke), len(te), len(ke)


def agrees(o, scored, arm):
    want, rt, rk, nt, nk = expect(scored, arm)
    r = o["arms"][arm]
    for tid, w in want["trains"].items():
        g = r["trains"][tid]
        got = (g["reading"],) if g["reading"] != "read" else ("read", g["model_in_interval"], g["sign"], g["estimate_in_model_band"])
        if got != w:
            return False, f"{arm} {tid}: {got} != {w}"
        if g["reading"] == "read" and abs(g["error_W"] - (M2["arms"][arm]["trains"][tid]["W"] - scored["trains"][tid]["mean"])) > 1e-12:
            return False, f"{arm} {tid}: error"
    for kid, w in want["kinds"].items():
        g = r["kinds"][kid]
        got = (g["reading"],) if g["reading"] != "read" else ("read", g["measured_in_model_band"])
        if got != w:
            return False, f"{arm} {kid}: {got} != {w}"
    et, ek = r["errors"]["trains"], r["errors"]["kinds"]
    if et["n"] != nt or ek["n"] != nk:
        return False, f"{arm}: counts {et['n']}/{nt} {ek['n']}/{nk}"
    for got, want_ in ((et["rms_error_W"], rt), (ek["rms_error_W"], rk)):
        if (got is None) != (want_ is None) or (got is not None and abs(got - want_) > 1e-12):
            return False, f"{arm}: rms {got} != {want_}"
    return True, ""


def all_agree(o, scored):
    for arm in ARMS:
        ok, why = agrees(o, scored, arm)
        if not ok:
            return False, why
    return True, ""


def main():
    d = os.path.abspath(sys.argv[1])
    os.makedirs(d, exist_ok=True)
    res = []

    def check(name, ok, note=""):
        res.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'} {name} {note}")

    order_t = list(M2["trains"])
    sess = PLAN["session_trains"]
    # (P) the session as planned: its ten trains at M12's registered lines
    sc = {"trains": {t: iv(FC["trains"][t]["M12_w"]) for t in sess}, "reported": {"kinds": {}}}
    rc, o = run(sc, d, "P")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    reads = {a: o["arms"][a]["counts"]["trains"].get("read", 0) for a in ARMS} if rc == 0 else {}
    check("P: the planned session, every arm's every word and error as placed here", ok, why or json.dumps(reads, sort_keys=True))
    check("P: v4 (M12's set) reads 9 session trains (H16 not covered), v5, v6 and v7 read all 10, no kind read",
          rc == 0 and reads == {"v4-M12": 9, "v5": 10, "v6": 10, "v7": 10}
          and all(o["arms"][a]["counts"]["kinds"].get("read", 0) == 0 for a in ARMS) and o["arms"]["v4-M12"]["trains"]["H16"]["reading"] == "not covered")
    # (A) each arm's own centres and levels: that arm reads inside on every covered item; every other arm as placed here
    okA, whyA = True, ""
    for arm in ARMS:
        a = M2["arms"][arm]
        sc = {"trains": {t: iv(a["trains"][t]["W"] if a["trains"][t]["covered"] else FC["trains"].get(t, {}).get("M12_w", 0.0)) for t in order_t},
              "reported": {"kinds": {KEY[k]: {"D_w": a["kinds"][k]["W"]} for k in a["kinds"] if a["kinds"][k]["covered"]}}}
        rc, o = run(sc, d, f"A-{arm}")
        if rc != 0:
            okA, whyA = False, f"{arm} rc {rc}"
            break
        own = o["arms"][arm]
        if not all(v["model_in_interval"] == "inside" for v in own["trains"].values() if v["reading"] == "read"):
            okA, whyA = False, f"{arm}: not inside on its own centres"
            break
        if not all(v["measured_in_model_band"] == "inside" for v in own["kinds"].values() if v["reading"] == "read"):
            okA, whyA = False, f"{arm}: a kind not inside its own band"
            break
        if abs(own["errors"]["trains"]["rms_error_W"]) > 1e-12:
            okA, whyA = False, f"{arm}: rms not 0 on its own centres"
            break
        ok, why = all_agree(o, sc)
        if not ok:
            okA, whyA = False, why
            break
    check("A: each arm at its own centres reads inside everywhere with rms error 0, and every other arm as placed here", okA, whyA)
    # (H) and (L): 0.1 W above (below) v7's centres, kinds 0.3 W off
    v7 = M2["arms"]["v7"]
    for name, dx, dk in (("H", 0.1, 0.3), ("L", -0.1, -0.3)):
        sc = {"trains": {t: iv(v7["trains"][t]["W"] + dx) for t in order_t},
              "reported": {"kinds": {KEY[k]: {"D_w": v7["kinds"][k]["W"] + dk} for k in v7["kinds"]}}}
        rc, o = run(sc, d, name)
        ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
        ok = ok and all(v["model_in_interval"] == ("below" if dx > 0 else "above") for v in o["arms"]["v7"]["trains"].values())
        ok = ok and abs(o["arms"]["v7"]["errors"]["trains"]["rms_error_W"] - abs(dx)) < 1e-12
        check(f"{name}: every train {dx:+.1f} W and every kind {dk:+.1f} W off v7's: every arm's words and errors as placed here, v7's rms "
              f"{abs(dx):.1f} W", ok, why)
    # (F) the fallback as the scorer writes it
    v5 = M2["arms"]["v5"]
    fk = M2["fallback_kinds"]
    sc = {"trains": {t: nsc() for t in sess}, "reported": {"kinds": {KEY[k]: {"D_w": v5["kinds"][k]["W"]} for k in fk}}}
    rc, o = run(sc, d, "F")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    kr = {a: o["arms"][a]["counts"]["kinds"].get("read", 0) for a in ARMS} if rc == 0 else {}
    ok = ok and kr == {"v4-M12": 13, "v5": 15, "v6": 15, "v7": 15} and all(o["arms"][a]["counts"]["trains"].get("read", 0) == 0 for a in ARMS)
    check("F: the fallback: no train read (every session train NOT SCORED), the fifteen kinds read by v5-v7 and thirteen by v4 (M12's set)",
          ok, why or json.dumps(kr, sort_keys=True))
    # (N) one covered train NOT SCORED
    sc = {"trains": {t: iv(v7["trains"][t]["W"]) for t in sess}}
    sc["trains"]["S23"] = nsc("E186-C: a launch's C not bit-exact")
    rc, o = run(sc, d, "N")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    ok = ok and all(o["arms"][a]["trains"]["S23"]["reading"] == "not read" for a in ARMS)
    check("N: a NOT SCORED train reads 'not read' in every arm", ok, why)
    # (T) a copy of the model's file with one digit changed
    bad = copy.deepcopy(M2)
    bad["arms"]["v7"]["trains"]["H16"]["W"] = round(bad["arms"]["v7"]["trains"]["H16"]["W"] + 0.0001, 4)
    bp = os.path.join(d, "m2-tampered.json")
    open(bp, "w").write(json.dumps(bad, indent=1, sort_keys=True) + "\n")
    rc, _ = run({"trains": {}}, d, "T", model=bp)
    check("T: a model file with one digit changed is refused (exit 2)", rc == 2)
    # (K) E186's list with one byte changed
    lp = os.path.join(d, "list-tampered.json")
    raw = open(os.path.join(TOP, "tools", "claims-v3", "m12", "kinds-m12-e186.json"), "rb").read()
    open(lp, "wb").write(raw + b"\n")
    rc, _ = run({"trains": {}}, d, "K", lst=lp)
    check("K: E186's list with one byte changed is refused (exit 2)", rc == 2)
    # (X) a scorer's file with no trains
    rc, _ = run({"reported": {}}, d, "X")
    check("X: a scorer's file without trains is refused (exit 3)", rc == 3)
    # (W) the reader writes its two outputs and nothing else, in a directory of its own
    wd = os.path.join(d, "W")
    os.makedirs(wd, exist_ok=True)
    sc = {"trains": {t: iv(FC["trains"][t]["M12_w"]) for t in sess}}
    p = os.path.join(wd, "scored-e186.json")
    json.dump(sc, open(p, "w"))
    before = sorted(os.listdir(wd))
    r = subprocess.run(["/usr/bin/python3", "-B", READER, "--scored", p, "--out", os.path.join(wd, "arm-m2-e186")], capture_output=True, text=True)
    after = sorted(os.listdir(wd))
    check("W: the reader writes arm-m2-e186.json and .txt and nothing else", r.returncode == 0
          and after == sorted(before + ["arm-m2-e186.json", "arm-m2-e186.txt"]))
    n = sum(1 for _, ok in res if ok)
    print(f"SELFTEST-ARM-M2-E186 {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'}")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
