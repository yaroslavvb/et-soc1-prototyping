#!/usr/bin/env python3
"""E186 (Q158): the self-test of note M2's reader v2 (arm_m2_read_e186_v2.py; E186.md.dated-note-M2.md.dated-note-1.md, section 2), on
SYNTHETIC sessions only: scorer files in E182's scored.json form made here from the frozen figures and E186's registered lines, never a
card and never a real run's data (no E182 or other session's data is read or presented as E186's). It is the self-test of note M2's
reader v1 (selftest_arm_m2_e186.py, which stays as committed) with v1's eleven cases run on v2, and five more for v2's three changes.

    /usr/bin/python3 -B tools/claims-v3/e186/selftest_arm_m2_e186_v2.py <a scratch dir outside the repository>

Cases (v1's): (P) E186 as planned, the ten session trains at M12's registered lines, nothing else run (two checks); (A) for each arm,
every train at that arm's centres and every kind at its levels; (H) and (L) every train 0.1 W above (below) v7's centres and every kind
0.3 W above (below) v7's levels; (F) the fallback as the scorer writes it (every session train NOT SCORED, the fifteen fallback kinds at
v5's levels, each with c_kept true); (N) one covered train NOT SCORED; (T) the model's file with one digit changed (exit 2); (K) E186's
list with one byte changed (exit 2); (X) a scorer's file with no trains (exit 3); (W) the reader writes its two outputs and nothing else.
Cases (v2's): (NT) one session train's mean, lo and hi NaN, in a file written with NaN tokens as Python's json writes them; (IT) one
session train's hi infinite; (NK) in the fallback, one kind's D_w NaN; (CK) in the fallback, one kind with c_kept false; each reads "not
read" in every arm that covers it, the other items as placed here, every arm's errors over the items read only; (S) every output this
test made parses as strict json (no NaN or Infinity token) and every error in it is finite.
In each, the reader's words and errors must equal this test's own placement and arithmetic. Exit 0 only if every case passes.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import glob
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
READER = os.path.join(HERE, "arm_m2_read_e186_v2.py")
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


def fin(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def sign_word(m, est):
    if m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def run(scored, d, name, model=None, lst=None):
    p = os.path.join(d, f"{name}-scored.json")
    json.dump(scored, open(p, "w"))       # Python's own json: a NaN or an infinity is written as a NaN or Infinity token
    cmd = ["/usr/bin/python3", "-B", READER, "--scored", p, "--out", os.path.join(d, f"{name}-arm")]
    if model:
        cmd += ["--model", model]
    if lst:
        cmd += ["--list", lst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    o = json.load(open(os.path.join(d, f"{name}-arm.json"))) if r.returncode == 0 else None
    return r.returncode, o


def expect(scored, arm):
    """this test's own placement, by note M2's words with its dated note 1: every word and error the reader should write for one arm"""
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
        elif tr[tid].get("lo") is None or tr[tid].get("hi") is None or tr[tid].get("mean") is None:
            want["trains"][tid] = ("not read",)
        elif not all(fin(tr[tid][k]) for k in ("mean", "lo", "hi")):
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
        elif r.get("c_kept") is False or not fin(r["D_w"]):
            want["kinds"][kid] = ("not read",)
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


def covering(section, item):
    return [a for a in ARMS if M2["arms"][a][section][item]["covered"]]


def strict_ok(path):
    """the reader's json parses with no NaN or Infinity token, and every error and rms in it is a finite number or null"""
    def bad(c):
        raise ValueError(f"a {c} token")
    try:
        o = json.loads(open(path).read(), parse_constant=bad)
    except ValueError:
        return False
    for a in o["arms"].values():
        for sec in ("trains", "kinds"):
            for v in a[sec].values():
                if "error_W" in v and not fin(v["error_W"]):
                    return False
            for k in ("mean_error_W", "rms_error_W"):
                x = a["errors"][sec][k]
                if x is not None and not fin(x):
                    return False
    return True


def main():
    d = os.path.abspath(sys.argv[1])
    os.makedirs(d, exist_ok=True)
    res = []

    def check(name, ok, note=""):
        res.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'} {name} {note}")

    order_t = list(M2["trains"])
    sess = PLAN["session_trains"]
    # ---- v1's eleven cases, on v2 ----
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
              "reported": {"kinds": {KEY[k]: {"D_w": a["kinds"][k]["W"], "c_kept": True} for k in a["kinds"] if a["kinds"][k]["covered"]}}}
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
              "reported": {"kinds": {KEY[k]: {"D_w": v7["kinds"][k]["W"] + dk, "c_kept": True} for k in v7["kinds"]}}}
        rc, o = run(sc, d, name)
        ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
        ok = ok and all(v["model_in_interval"] == ("below" if dx > 0 else "above") for v in o["arms"]["v7"]["trains"].values())
        ok = ok and abs(o["arms"]["v7"]["errors"]["trains"]["rms_error_W"] - abs(dx)) < 1e-12
        check(f"{name}: every train {dx:+.1f} W and every kind {dk:+.1f} W off v7's: every arm's words and errors as placed here, v7's rms "
              f"{abs(dx):.1f} W", ok, why)
    # (F) the fallback as the scorer writes it
    v5 = M2["arms"]["v5"]
    fk = M2["fallback_kinds"]
    fsc = {"trains": {t: nsc() for t in sess}, "reported": {"kinds": {KEY[k]: {"D_w": v5["kinds"][k]["W"], "c_kept": True} for k in fk}}}
    rc, o = run(fsc, d, "F")
    ok, why = all_agree(o, fsc) if rc == 0 else (False, f"rc {rc}")
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
    # ---- v2's cases ----
    # (NT) a session train's interval NaN (mean, lo, hi), written with NaN tokens
    sc = {"trains": {t: iv(v7["trains"][t]["W"]) for t in sess}, "reported": {"kinds": {}}}
    sc["trains"]["S23"] = dict(iv(float("nan")), lo=float("nan"), hi=float("nan"))
    rc, o = run(sc, d, "NT")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    nread = {a: o["arms"][a]["errors"]["trains"]["n"] for a in ARMS} if rc == 0 else {}
    ok = ok and all(o["arms"][a]["trains"]["S23"]["reading"] == "not read" for a in ARMS) and nread == {"v4-M12": 8, "v5": 9, "v6": 9, "v7": 9}
    ok = ok and all(o["arms"][a]["errors"]["trains"]["rms_error_W"] is not None and fin(o["arms"][a]["errors"]["trains"]["rms_error_W"]) for a in ARMS)
    ok = ok and "NaN" in open(os.path.join(d, "NT-scored.json")).read()
    check("NT: a train whose mean, lo and hi are NaN reads 'not read' in every arm; the arms' errors over the other trains (v4 8, v5-v7 9), "
          "finite", ok, why or json.dumps(nread, sort_keys=True))
    # (IT) a session train's hi infinite
    sc = {"trains": {t: iv(v7["trains"][t]["W"]) for t in sess}, "reported": {"kinds": {}}}
    sc["trains"]["Q3-swap"]["hi"] = float("inf")
    rc, o = run(sc, d, "IT")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    ok = ok and all(o["arms"][a]["trains"]["Q3-swap"]["reading"] == "not read" for a in covering("trains", "Q3-swap"))
    ok = ok and "Infinity" in open(os.path.join(d, "IT-scored.json")).read()
    check("IT: a train whose hi is infinite reads 'not read' in every arm that covers it; every other word and error as placed here", ok, why)
    # (NK) the fallback, one kind's D_w NaN
    k_nan = "K11"
    sc = copy.deepcopy(fsc)
    sc["reported"]["kinds"][KEY[k_nan]]["D_w"] = float("nan")
    rc, o = run(sc, d, "NK")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    kr = {a: o["arms"][a]["errors"]["kinds"]["n"] for a in ARMS} if rc == 0 else {}
    ok = ok and all(o["arms"][a]["kinds"][k_nan]["reading"] == "not read" for a in covering("kinds", k_nan)) and kr == {"v4-M12": 12, "v5": 14, "v6": 14, "v7": 14}
    ok = ok and all(fin(o["arms"][a]["errors"]["kinds"]["rms_error_W"]) for a in ARMS)
    check(f"NK: in the fallback, a kind ({k_nan}) whose D_w is NaN reads 'not read' in every arm; the kinds' errors over the others "
          "(v4 12, v5-v7 14), finite", ok, why or json.dumps(kr, sort_keys=True))
    # (CK) the fallback, one kind with c_kept false (its check of C failed; the scorer keeps it out of E186-LV)
    k_c = "K13"
    sc = copy.deepcopy(fsc)
    sc["reported"]["kinds"][KEY[k_c]]["c_kept"] = False
    rc, o = run(sc, d, "CK")
    ok, why = all_agree(o, sc) if rc == 0 else (False, f"rc {rc}")
    kr = {a: o["arms"][a]["errors"]["kinds"]["n"] for a in ARMS} if rc == 0 else {}
    ok = ok and all(o["arms"][a]["kinds"][k_c]["reading"] == "not read" for a in covering("kinds", k_c)) and kr == {"v4-M12": 12, "v5": 14, "v6": 14, "v7": 14}
    ok = ok and all("c_kept false" in o["arms"][a]["kinds"][k_c].get("why", "") for a in covering("kinds", k_c))
    check(f"CK: in the fallback, a kind ({k_c}) with c_kept false reads 'not read' in every arm, the why naming it; the kinds' errors over "
          "the others (v4 12, v5-v7 14)", ok, why or json.dumps(kr, sort_keys=True))
    # (S) every output this test made parses as strict json, with finite errors
    outs = sorted(glob.glob(os.path.join(d, "*-arm.json")) + glob.glob(os.path.join(d, "W", "arm-m2-e186.json")))
    bads = [os.path.basename(p) for p in outs if not strict_ok(p)]
    check(f"S: every output json this test made ({len(outs)}) parses strictly, with no NaN or Infinity token and every error finite",
          len(outs) >= 13 and not bads, ", ".join(bads))
    n = sum(1 for _, ok in res if ok)
    print(f"SELFTEST-ARM-M2-E186-V2 {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'}")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
