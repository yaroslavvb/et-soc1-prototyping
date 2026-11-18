#!/usr/bin/env python3
"""E213 (Q216): the frozen scorer of MM1-v3's BLIND MATMUL DAY, two arms. It reads the kits' reduced data (E206's run form, below), MM1-v3's and
MM1-v2's frozen forecasts (arm A: tools/matmul/mm1/v3/out/mm1_v3_e213.csv and mm1_v2_e213.csv, frozen in MM1-v3's land b1493082; arm B:
forecast-e213b-v3.csv and forecast-e213b-v2.csv, frozen by this registration), and this folder's rules and points, and refuses to run (exit 4)
if any of those files' bytes changed. Standard library only.

    python3 -I -B tools/claims-v3/e213/score_e213.py DATA.json [--labels LABELS.json] [--out SCORED.json]
    python3 -I -B tools/claims-v3/e213/score_e213.py --selftest-standins OUT.json   stand-in days whose verdicts are stated before the run (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e213/score_e213.py --selftest-real OUT.json       E207's and E206 arm B's committed runs through this reader
    python3 -I -B tools/claims-v3/e213/score_e213.py --forecasts                    every point's two forecasts and the given() self-check

THE DATA (one JSON; E206's reducer form): {"experiment": "E213", "arms": {"A": ARM, "B": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"runs": [RUN, ...]}, "points": {pid: {"runs": [RUN, ...]}}, "ties": {"runs": [RUN, ...]}}   (references are points)
  RUN = {"t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (launch >= 0, ok, wall_s >= 0.1 s, the kernel clock
         cycles_max / wall in 590-610 MHz; calibration and check launches never count), "cycles_per_op": the median over the counted launches of
         the host's cycles_per_op (the counter's mean over minions / ops), "cycles_gemm": the median of cycles_max / passes (the slowest minion's
         counter, a GEMM), "p_work_w": the median board W of the 10 Hz samples inside the counted launches, "p_rest_w": the median board W of the
         last 5 s of the run's rest read, "die_start_c", "mhz_min", "mhz_max" (the counted samples' minion clock), "checks" (every check of C of
         the run: "exact" / "approx" / "wrong"), "record": {"arm", "type", "minions", "shire_mask"} as the host prints them, "block": "smoke" /
         "pass1" / "pass2" / "tie", "n": its place in the session, and for a process of rgm211's host (gemmLn, gemmLnc, rgm211's gemmL): "walk":
         {"ok": [walk_ok of every counted launch], "launches_bad": the check line's walk_launches_bad} and "gate": the identity gate's words
         ("GATE OK: ..." or "GATE FAILED: ...") (E211's form); a smoke RUN carries "point" (its smoke point's id), as the reducer writes it}
MEASURED, per run: the wall cycles an op = cycles_gemm / ops a minion a GEMM; the counter's mean = cycles_per_op; seconds = t_gemm_s; W over idle =
  p_work - p_rest; J over idle = W t_gemm; J with the card at rest = p_work t_gemm. A run whose record differs from its point (arm, type, minions,
  or the shire mask read as a number), or whose rgm211-host walk or gate is not good, is SET ASIDE and flagged. A POINT is the mean of its kept
  runs; a CASE (kernel loop, arm, format, mask: time is kind-blind in both models) the mean of its points.
THE RULES (E213.md section 7; numbers from rules-e213.json; per arm):
  R0  every check of C of the arm exact or approx (smoke, points, references, ties); the smoke's counter mean 200-4,000 cycles an op; every
      rgm211-host process's walk good (launches_bad 0, every ok true) and its gate GATE OK. A FAIL labels every other verdict of the arm.
      AMENDMENT A1 (E213.md, before any datum): a FAMILY SMOKE (rules-e213.json > A1 > family_smoke: arm A's s04, the family 'rgm211 gemmL')
      that fails any of those checks while NO point of its family has a run in the data (the runner dropped the family: its points never
      started, NO DATA) is not an R0 failure: the drop is flagged and REPORTED; if any point of that family has a run, its failures count in R0
      as registered (a family that ran past its failed smoke is a kit fault). The other smoke points (s01-s03, s11-s14) read as registered.
  S6  every kept run's counted samples at 590-610 MHz (mhz_min, mhz_max). A FAIL labels every other verdict of the arm.
  MM1-v3 PER CASE: T1 the wall cycles, T2 the counter's mean, T3 seconds: |measured / MM1-v3 - 1| <= the arm's band.
  MM1-v3 PER POINT: E1 J over idle given the measured seconds (MM1-v3's W = A + B / t_op, t_op = the measured wall cycles an op / 600 MHz in us,
      given()'s reading: the slowest minion's counter time, E213.md section 5; times t_gemm; corrected by Amendment A1 from the frozen
      docstring's "t_gemm / ops", which the code never used); E2 J over idle
      with the seconds forecast (its frozen J); E3 J at rest given t (p_rest t + E1's J); E4 J at rest with the seconds forecast (p_rest t_v3 +
      its frozen J); at a WATTS POINT (MM1-v3's frozen W or the measured W under 3 W) E1 and E2 read |W measured - W forecast| <= band_w.
  A rule's verdict: PASS if at least 90% of its scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none.
  HEAD TO HEAD, MM1-v3 against MM1-v2: H1 the wall cycles per case, H2 the counter's mean per case, H3 seconds per case, H4 J over idle given the
      measured seconds per point both price, H5 J over idle with the seconds forecast per point both price; d = |ln(measured / v2)| - |ln(measured
      / v3)| (in watts of W at a watts point); MM1-v3 closer where d > the arm's tie, MM1-v2 where d < -tie; the exact two-sided sign test at 0.05
      on the untied decides: MM1-v3 BETTER / MM1-v2 BETTER / NOT DECIDED; TOO FEW under 10 untied; NO DATA with none.
  HP1-HP5: H1-H5 pooled over both arms (each case or point once, with its own arm's tie); NO DATA unless both arms scored.
  LABELS (--labels): {"A": {"ran_before_points": [...], "ran_before_cases": [...]}, "B": {...}}: those points (and cases) leave every rule; the
      output names every label applied; a label naming no point or case is refused (exit 10).
REPORTED (never verdicts): the bootstrap 95% interval of the mean d (B = 10,000, seeded "E213|bootstrap|<arm>|<rule>"); the family check (the
  sign test over the families' median d); every model's rms and bias by family; the ratio readings (int8 / fp32, gemmLnc / gemmL, gemmLn / gemmL,
  rgm211's gemmL / rgm136's, kind / random, masks of one shire count); the day offset from the ties against the committed reference (H4n, H5n);
  the anchor's die reading (a089, a090); the timing simulation's two columns.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
D = "tools/claims-v3/e213/"
V3 = "tools/matmul/mm1/v3/out/"
PINS = {
    V3 + "mm1_v3_e213.csv": "01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49",
    V3 + "mm1_v2_e213.csv": "e1b99f682f303eaeaa818bc09a95e6484d8db5811c43991ae9d1b078476a43af",
    V3 + "e213_points.csv": "be9049299641ccaf764225c9b390997cc53a2885d9bf350ae12212d14503ee21",
    V3 + "mm1_v3_e213.json": "932c5a18472fd5a16ddcc0338f481b6227409c1fd276606eb604480154f0bd4b",
    D + "forecast-e213b-v3.csv": "e529bbb24de26bc68c50279945c31a0da384e1f6c01cddc1f510cd2e1c0c4ed0", D + "forecast-e213b-v2.csv": "297762ebbbed7186631716b45aca33af73fd6f56ff769509d1d0c68ef0c411f4", D + "forecast-e213b-v3.json": "fc7ac54276cc5db385c88da1bb488e9bc0e76ad5c69f408bb626e807759479d9",
    D + "rules-e213.json": "43963ca6b358e2136d62ecf253280f112ed27970039979242fa4fd2440deccc3", D + "points-e213.json": "f122b62500ce7d0f5e924f7454adb074d9ca673c328fe3c98c64a9b906d65d15",
}
ARMS = ("A", "B")
TIME_RULES = ("T1", "T2", "T3")
ENERGY_RULES = ("E1", "E2", "E3", "E4")
H2H = ("H1", "H2", "H3", "H4", "H5")
LOW = 3.0
FLOOR = {"fp32": 529.0, "fp16": 529.0, "int8": 270.0}
RATIOS = {
    "A": [("int8/fp32", "a001", "a002"), ("int8/fp32", "a003", "a004"), ("int8/fp32", "a005", "a006"), ("int8/fp32", "a007", "a008"),
          ("int8/fp32", "a009", "a010"), ("int8/fp32", "a011", "a012"), ("int8/fp32", "a013", "a014"), ("int8/fp32", "a015", "a016"),
          ("int8/fp32", "a037", "a038"), ("int8/fp32", "a039", "a040"), ("int8/fp32", "a041", "a042"), ("int8/fp32", "a043", "a044"),
          ("int8/fp32", "a045", "a046"), ("int8/fp32", "a047", "a048"),
          ("gemmLn/gemmL", "a073", "a006"), ("gemmLn/gemmL", "a077", "a076"), ("gemmLn/gemmL", "a080", "a030"), ("gemmLn/gemmL", "a084", "a083"),
          ("rgm211 gemmL/rgm136 gemmL", "a074", "a006"), ("rgm211 gemmL/rgm136 gemmL", "a078", "a076"), ("rgm211 gemmL/rgm136 gemmL", "a081", "a030"),
          ("rgm211 gemmL/rgm136 gemmL", "a085", "a083"),
          ("gemmLnc/gemmL", "a075", "a006"), ("gemmLnc/gemmL", "a079", "a076"), ("gemmLnc/gemmL", "a082", "a030"), ("gemmLnc/gemmL", "a086", "a083"),
          ("gemmLnc/gemmL", "a087", "a088"),
          ("zeros/random", "a031", "a032"), ("zeros/random", "a033", "a034"), ("zeros/random", "a035", "a036"),
          ("mask/full chip", "a050", "a049"), ("mask/full chip", "a051", "a049"), ("mask/full chip", "a054", "a049"), ("mask/full chip", "a059", "a049"),
          ("mask/full chip", "a062", "a061"), ("mask/full chip", "a063", "a061"), ("mask/full chip", "a066", "a061"), ("mask/full chip", "a071", "a061")],
    "B": [("int8/fp32", "k01", "k02"), ("int8/fp32", "k03", "k04"), ("int8/fp32", "k05", "k06"), ("int8/fp32", "k07", "k08"), ("int8/fp32", "k09", "k10"),
          ("int8/fp32", "k16", "k15"), ("int8/fp32", "k18", "k17"), ("int8/fp32", "k20", "k21"), ("int8/fp32", "k22", "k23"), ("int8/fp32", "k24", "k25"),
          ("int8/fp32", "k26", "k27"),
          ("gemmLnc/gemmL", "k37", "k06"), ("gemmLnc/gemmL", "k38", "k08"), ("gemmLnc/gemmL", "k39", "k14"), ("gemmLnc/gemmL", "k40", "k41"),
          ("zeros/random", "k28", "k29"), ("zeros/random", "k30", "k31"), ("zeros/random", "k32", "k06"), ("ones/random", "k33", "k06"),
          ("sparse50/random", "k34", "k06"), ("zeros/random", "k35", "k05"), ("ones/random", "k36", "k05")],
}
MASK_SETS = [["a050", "a051"], ["a052", "a053"], ["a054", "a055", "a056"], ["a057", "a058"], ["a059", "a060"],
             ["a062", "a063"], ["a064", "a065"], ["a066", "a067", "a068"], ["a069", "a070"], ["a071", "a072"]]


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def fnum(x):
    return None if x in ("", None) else float(x)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def ln_err(m, f):
    return math.log(m / f) if (m is not None and f is not None and m > 0 and f > 0) else None


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


# ------------------------------------------------------------------ the frozen inputs
def load_frozen(check=True):
    if check:
        for rel, want in PINS.items():
            got = sha_rel(rel)
            if got != want:
                print(f"score_e213: REFUSED, {rel} is {got}, pinned {want}")
                sys.exit(4)
    rules = json.load(open(os.path.join(REPO, D + "rules-e213.json")))
    pts = json.load(open(os.path.join(REPO, D + "points-e213.json")))
    src = {"A": (V3 + "mm1_v3_e213.csv", V3 + "mm1_v2_e213.csv"), "B": (D + "forecast-e213b-v3.csv", D + "forecast-e213b-v2.csv")}
    fc = {}
    for tag in ARMS:
        r3 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, src[tag][0]), newline=""))}
        r2 = {r["id"]: r for r in csv.DictReader(open(os.path.join(REPO, src[tag][1]), newline=""))}
        fc[tag] = {}
        for i in r3:
            a, b = r3[i], r2.get(i, {})
            fc[tag][i] = {"v3": {"cw": fnum(a["cycles_per_op_wall"]), "cm": fnum(a["cycles_per_op_mean"]), "t": fnum(a["seconds_per_gemm"]),
                                 "W": fnum(a.get("W_over_idle")), "A": fnum(a.get("A_W")), "B": fnum(a.get("B_W_us")),
                                 "J": fnum(a.get("J_over_idle_per_gemm")), "Prest": fnum(a.get("P_rest_W_REPORTED"))},
                          "v2": {"cw": fnum(b.get("cycles_per_op_wall")), "cm": fnum(b.get("cycles_per_op_mean")), "t": fnum(b.get("seconds_per_gemm")),
                                 "W": fnum(b.get("W_over_idle")), "A": fnum(b.get("A_W")), "B": fnum(b.get("B_W_us")),
                                 "J": fnum(b.get("J_over_idle_per_gemm"))}}
    v3j = json.load(open(os.path.join(REPO, V3 + "mm1_v3_e213.json")))["points"]
    v3bj = json.load(open(os.path.join(REPO, D + "forecast-e213b-v3.json")))["points"]
    sim = {}
    for tag, J in (("A", v3j), ("B", v3bj)):
        sim[tag] = {i: (r.get("sim_steps_per_minion_per_gemm"), r.get("ops_per_minion_per_gemm")) for i, r in J.items()}
    return rules, pts, fc, sim


def given(m, cw, t_gemm):
    """a model's W over idle at the measured op time by its frozen affine form, and its J over idle given t: t_op = the measured wall cycles an
    op / 600 MHz (the slowest minion's counter time, MM1-v3's 'measured op time (the slowest minion)' and its fit's footing for E206's run
    form, data_v3.e206_style: T = cw / 600); J = W x the measured seconds"""
    if m["A"] is None or m["B"] is None or not cw:
        return None, None
    W = m["A"] + m["B"] / (cw / 600.0)
    return W, W * t_gemm


# ------------------------------------------------------------------ the measured side
def reduce_arm(tag, arm, P, labels, fsm=None):
    """per point: the kept runs' mean figures; flags; R0 and S6 inputs. fsm: Amendment A1's family smoke of this arm ({smoke point: family},
    rules-e213.json > A1 > family_smoke > <arm>): that smoke's failures leave R0 when its family has no run (the family dropped), else count."""
    pts = {p["id"]: p for p in P["arms"][tag]["points"]}
    out, flags, r0, s6 = {}, [], [], []
    fsm = fsm or {}
    fam_fail = {}

    def run_ok(r, p):
        rec = r.get("record") or {}
        try:
            same = (rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == p["minions"]
                    and int(str(rec.get("shire_mask")), 16) == int(p["shire_mask"], 16))
        except (TypeError, ValueError):
            same = False
        walk_good = True
        if p["host"] == "rgm211":
            w = r.get("walk") or {}
            walk_good = bool(w.get("ok")) and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")
        return same, walk_good

    for pid, pt in (arm.get("points") or {}).items():
        p = pts.get(pid)
        if p is None:
            flags.append(f"{pid}: not a registered point (ignored)")
            continue
        kept = []
        for r in pt.get("runs", []):
            chk = r.get("checks") or []
            if not chk or any(c not in ("exact", "approx") for c in chk):
                r0.append(f"{pid} run {r.get('n')}: checks {chk}")
            same, walk_good = run_ok(r, p)
            if p["host"] == "rgm211" and not walk_good:
                r0.append(f"{pid} run {r.get('n')}: walk or gate not good")
            if not same:
                flags.append(f"{pid} run {r.get('n')}: SET ASIDE (record {r.get('record')})")
                continue
            if not walk_good:
                flags.append(f"{pid} run {r.get('n')}: SET ASIDE (walk or gate)")
                continue
            if r.get("t_gemm_s") is None or r.get("cycles_gemm") is None:
                flags.append(f"{pid} run {r.get('n')}: no reading (NO DATA)")
                continue
            if r.get("mhz_min") is None or r.get("mhz_max") is None or r["mhz_min"] < 590 or r["mhz_max"] > 610:
                s6.append(f"{pid} run {r.get('n')}: clock {r.get('mhz_min')}-{r.get('mhz_max')} MHz")
            kept.append(r)
        if not kept:
            flags.append(f"{pid}: NO DATA (no kept run)")
            continue
        ops = p["ops_per_minion_per_gemm"]
        W = [r["p_work_w"] - r["p_rest_w"] for r in kept if r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        out[pid] = {"n_runs": len(kept), "cw": mean([r["cycles_gemm"] / ops for r in kept]), "cm": mean([r["cycles_per_op"] for r in kept]),
                    "t": mean([r["t_gemm_s"] for r in kept]), "W": mean(W) if W else None,
                    "J": mean([(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in kept if r.get("p_work_w") is not None]) if W else None,
                    "Jrest": mean([r["p_work_w"] * r["t_gemm_s"] for r in kept if r.get("p_work_w") is not None]) if W else None,
                    "prest": mean([r["p_rest_w"] for r in kept if r.get("p_rest_w") is not None]),
                    "die": mean([r.get("die_start_c") for r in kept]), "case": p["case"], "role": p["role"], "family": p["family"], "ops": ops,
                    "format": p["format"], "loop": p["loop"]}
    for r in (arm.get("ties") or {}).get("runs", []) + (arm.get("smoke") or {}).get("runs", []):
        why = []
        chk = r.get("checks") or []
        if not chk or any(c not in ("exact", "approx") for c in chk):
            why.append(f"{r.get('block')} run {r.get('n')}: checks {chk}")
        if r.get("block") == "smoke":
            cpo = r.get("cycles_per_op")
            if cpo is None or not (200 <= cpo <= 4000):
                why.append(f"smoke run {r.get('n')}: cycles an op {cpo} outside 200-4,000")
            if r.get("walk") is not None or r.get("gate") is not None:
                w = r.get("walk") or {}
                if not (w.get("ok") and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")):
                    why.append(f"smoke run {r.get('n')}: walk or gate not good")
        fam = fsm.get(r.get("point")) if r.get("block") == "smoke" else None
        if fam:                     # Amendment A1: a family smoke's failures, read below against its family's runs
            fam_fail.setdefault(fam, []).extend(f"{r.get('point')} ({x})" for x in why)
        else:
            r0.extend(why)
    for fam, why in sorted(fam_fail.items()):
        if not why:
            continue
        members = sorted(pid for pid, p in pts.items() if p["loop"] == fam)
        ran = [pid for pid in members if ((arm.get("points") or {}).get(pid) or {}).get("runs")]
        if ran:
            r0.extend(why + [f"A1: the family smoke of '{fam}' failed, yet {ran} ran: counted in R0 (a family that ran past its failed smoke)"])
        else:
            flags.append(f"A1: the family smoke of '{fam}' failed ({'; '.join(why)}): the family was dropped, its points {members} NO DATA; "
                         "not an R0 failure (Amendment A1), REPORTED")
    for pid in labels.get("ran_before_points", []):
        if pid in out:
            out[pid]["role"] = "ran before"
    for pid, v in out.items():
        if v["case"] in labels.get("ran_before_cases", []):
            v["role"] = "ran before"
    return out, flags, r0, s6


def verdict_frac(cells):
    n = len(cells)
    if n == 0:
        return "NO DATA"
    if n < 10:
        return "TOO FEW"
    k = sum(1 for c in cells if c["pass"])
    return "PASS" if k >= math.ceil(0.9 * n - 1e-9) else "FAIL"


def score_arm(tag, M, fc, rules, P):
    """MM1-v3's rules and the head-to-head cells of one arm"""
    R = rules["arms"][tag]
    band = {q: R["bands"][q]["band"] for q in TIME_RULES + ENERGY_RULES}
    band_w = R["band_w"]["band_W"]
    ties = R["ties"]
    scored = {pid: v for pid, v in M.items() if v["role"] == "point"}
    cases = {}
    for pid, v in scored.items():
        cases.setdefault(v["case"], []).append(pid)
    cells = {q: [] for q in TIME_RULES + ENERGY_RULES}
    h = {k: [] for k in H2H}
    for case, ids in sorted(cases.items()):
        f3, f2 = fc[ids[0]]["v3"], fc[ids[0]]["v2"]
        meas = {"cw": mean([M[i]["cw"] for i in ids]), "cm": mean([M[i]["cm"] for i in ids]), "t": mean([M[i]["t"] for i in ids])}
        for q, key in (("T1", "cw"), ("T2", "cm"), ("T3", "t")):
            e = meas[key] / f3[key] - 1
            cells[q].append({"case": case, "measured": meas[key], "v3": f3[key], "err": e, "pass": abs(e) <= band[q]})
        for hk, key, tk in (("H1", "cw", "cycles_ln"), ("H2", "cm", "cycles_ln"), ("H3", "t", "seconds_ln")):
            if f2.get(key):
                d = abs(math.log(meas[key] / f2[key])) - abs(math.log(meas[key] / f3[key]))
                h[hk].append({"id": case, "d": d, "tie": ties[tk], "watts": False, "family": M[ids[0]]["family"]})
    for pid, v in sorted(scored.items()):
        f3, f2 = fc[pid]["v3"], fc[pid]["v2"]
        if v["W"] is None or f3["W"] is None:
            continue
        watts = f3["W"] < LOW or v["W"] < LOW
        Wg3, Jg3 = given(f3, v["cw"], v["t"])
        e1 = (abs(v["W"] - Wg3) if watts else v["J"] / Jg3 - 1)
        cells["E1"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "v3": Wg3 if watts else Jg3, "err": e1,
                            "pass": (e1 <= band_w) if watts else abs(e1) <= band["E1"]})
        e2 = (abs(v["W"] - f3["W"]) if watts else v["J"] / f3["J"] - 1)
        cells["E2"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "v3": f3["W"] if watts else f3["J"], "err": e2,
                            "pass": (e2 <= band_w) if watts else abs(e2) <= band["E2"]})
        e3 = v["Jrest"] / (v["prest"] * v["t"] + Jg3) - 1
        cells["E3"].append({"point": pid, "measured": v["Jrest"], "v3": v["prest"] * v["t"] + Jg3, "err": e3, "pass": abs(e3) <= band["E3"]})
        e4 = v["Jrest"] / (v["prest"] * f3["t"] + f3["J"]) - 1
        cells["E4"].append({"point": pid, "measured": v["Jrest"], "v3": v["prest"] * f3["t"] + f3["J"], "err": e4, "pass": abs(e4) <= band["E4"]})
        if f2["W"] is not None:
            Wg2, Jg2 = given(f2, v["cw"], v["t"])
            if watts:
                d4 = abs(v["W"] - Wg2) - abs(v["W"] - Wg3)
                d5 = abs(v["W"] - f2["W"]) - abs(v["W"] - f3["W"])
            else:
                d4 = abs(math.log(v["J"] / Jg2)) - abs(math.log(v["J"] / Jg3))
                d5 = abs(math.log(v["J"] / f2["J"])) - abs(math.log(v["J"] / f3["J"]))
            tie = ties["watts_W"] if watts else ties["joules_ln"]
            h["H4"].append({"id": pid, "d": d4, "tie": tie, "watts": watts, "family": v["family"]})
            h["H5"].append({"id": pid, "d": d5, "tie": tie, "watts": watts, "family": v["family"]})
    return cells, h


def decide(hc):
    npos = sum(1 for c in hc if c["d"] > c["tie"])
    nneg = sum(1 for c in hc if c["d"] < -c["tie"])
    n = len(hc)
    if n == 0:
        return {"verdict": "NO DATA", "n": 0}
    if npos + nneg < 10:
        return {"verdict": "TOO FEW", "n": n, "v3_closer": npos, "v2_closer": nneg, "ties": n - npos - nneg}
    p = sign_p(npos, nneg)
    v = ("MM1-v3 BETTER" if npos > nneg else "MM1-v2 BETTER") if p < 0.05 else "NOT DECIDED"
    return {"verdict": v, "n": n, "v3_closer": npos, "v2_closer": nneg, "ties": n - npos - nneg, "p_two_sided": p}


def boot(hc, seed):
    d = [c["d"] for c in hc if not c["watts"]]
    if len(d) < 2:
        return None
    rnd = random.Random(seed)
    n = len(d)
    ms = sorted(sum(d[rnd.randrange(n)] for _ in range(n)) / n for _ in range(10000))
    lo, hi = ms[249], ms[9749]
    return {"mean_d": sum(d) / n, "ci95": [lo, hi], "reading": "MM1-v3 BETTER" if lo > 0 else ("MM1-v2 BETTER" if hi < 0 else "NOT DECIDED"),
            "n": n, "REPORTED": True}


def family_check(hc):
    fam = {}
    for c in hc:
        fam.setdefault(c["family"], []).append(c["d"])
    med = {f: statistics.median(v) for f, v in fam.items()}
    npos = sum(1 for v in med.values() if v > 0)
    nneg = sum(1 for v in med.values() if v < 0)
    return {"family_median_d": {f: round(v, 5) for f, v in sorted(med.items())}, "v3": npos, "v2": nneg, "p_two_sided": sign_p(npos, nneg),
            "REPORTED": True}


def readings(tag, M, fc, sim, rules):
    out = {"ratios": [], "masks": [], "timing_simulation": {}, "anchor_die": None}
    for name, a, b in RATIOS[tag]:
        if a in M and b in M:
            key = "W" if ("random" in name and "/" in name and name.split("/")[0] in ("zeros", "ones", "sparse50")) else "cw"
            ma, mb = M[a].get(key), M[b].get(key)
            f3a, f3b, f2a, f2b = fc[a]["v3"].get(key), fc[b]["v3"].get(key), fc[a]["v2"].get(key), fc[b]["v2"].get(key)
            out["ratios"].append({"what": name, "num": a, "den": b, "quantity": key,
                                  "measured": (ma / mb) if (ma and mb) else None, "v3": (f3a / f3b) if (f3a and f3b) else None,
                                  "v2": (f2a / f2b) if (f2a and f2b) else None})
    if tag == "A":
        for s in MASK_SETS:
            vals = {i: M[i]["cw"] for i in s if i in M}
            if len(vals) >= 2:
                out["masks"].append({"points": s, "measured_cw": vals, "spread": max(vals.values()) / min(vals.values()) - 1,
                                     "v3_spread": 0.0, "note": "MM1-v3 and MM1-v2 forecast one value for the set (no layout model)"})
        an = {i: M[i] for i in ("a089", "a090") if i in M}
        if an:
            w48, w56 = fc["a089"]["v3"]["W"], fc["a090"]["v3"]["W"]
            out["anchor_die"] = [{"point": i, "die_start_c": v["die"], "W_measured": v["W"],
                                  "v3_at_die": (w48 + (w56 - w48) * ((v["die"] or 52.0) - 48.0) / 8.0)} for i, v in an.items()]
    for pid, v in M.items():
        st, ops = sim.get(pid, (None, None))
        out["timing_simulation"][pid] = {"cycles_gemm_over_sim_steps": (v["cw"] * v["ops"] / st) if st else None,
                                         "counter_mean_over_floor": v["cm"] / FLOOR[v["format"]]}
    return out


def day_offset(tag, arm, rules):
    ref = rules["day_offset_reference"][tag]
    runs = [r for r in (arm.get("ties") or {}).get("runs", []) if r.get("p_work_w") is not None and r.get("t_gemm_s")]
    if not runs or not ref.get("W_over_idle"):
        return None
    W = mean([r["p_work_w"] - r["p_rest_w"] for r in runs])
    T = mean([r["t_gemm_s"] for r in runs])
    return {"n_runs": len(runs), "W_over_idle": W, "offset_W": W / ref["W_over_idle"] - 1,
            "offset_t": (T / ref["t_gemm_s"] - 1) if ref.get("t_gemm_s") else None, "reference": ref}


def model_stats(M, fc):
    fam = {}
    for pid, v in M.items():
        if v["role"] != "point":
            continue
        for mdl in ("v3", "v2"):
            f = fc[pid][mdl]
            d = fam.setdefault(v["family"], {}).setdefault(mdl, {"cw": [], "J": []})
            if f.get("cw"):
                d["cw"].append(v["cw"] / f["cw"] - 1)
            if f.get("J") and v.get("J") and (v["W"] or 0) >= LOW:
                d["J"].append(v["J"] / f["J"] - 1)
    out = {}
    for fm, dd in sorted(fam.items()):
        out[fm] = {mdl: {k: ({"n": len(x), "rms_pct": round(100 * rms(x), 2), "bias_pct": round(100 * sum(x) / len(x), 2)} if x else None)
                         for k, x in q.items()} for mdl, q in dd.items()}
    return out


def score(data, labels=None, frozen=None, quiet=False):
    rules, P, fc, sim = frozen or load_frozen()
    labels = labels or {}
    for tag in ARMS:
        lab = labels.get(tag, {})
        ids = {p["id"] for p in P["arms"][tag]["points"]}
        cases = {p["case"] for p in P["arms"][tag]["points"]}
        bad = [x for x in lab.get("ran_before_points", []) if x not in ids] + [x for x in lab.get("ran_before_cases", []) if x not in cases]
        if bad:
            print(f"score_e213: REFUSED (exit 10), labels naming nothing in arm {tag}: {bad}")
            sys.exit(10)
    res = {"experiment": "E213", "arms": {}, "pooled": {}, "labels_applied": labels}
    allh = {k: [] for k in H2H}
    scored_arms = []
    for tag in ARMS:
        arm = (data.get("arms") or {}).get(tag) or {}
        if not arm or not arm.get("points"):
            res["arms"][tag] = {"verdicts": {r: "NO DATA" for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES + H2H}, "note": "arm missing or empty: NO DATA"}
            continue
        M, flags, r0, s6 = reduce_arm(tag, arm, P, labels.get(tag, {}), ((rules.get("A1") or {}).get("family_smoke") or {}).get(tag))
        cells, h = score_arm(tag, M, {i: fc[tag][i] for i in fc[tag]}, rules, P)
        v = {"R0": "FAIL" if r0 else "PASS", "S6": "FAIL" if s6 else "PASS"}
        for q in TIME_RULES + ENERGY_RULES:
            v[q] = verdict_frac(cells[q])
        hd = {}
        for k in H2H:
            hd[k] = decide(h[k])
            hd[k]["bootstrap_REPORTED"] = boot(h[k], f"E213|bootstrap|{tag}|{k}")
            hd[k]["family_check_REPORTED"] = family_check(h[k]) if h[k] else None
            v[k] = hd[k]["verdict"]
            allh[k] += h[k]
        label = []
        if v["R0"] == "FAIL":
            label.append("label_R0: R0 FAIL")
        if v["S6"] == "FAIL":
            label.append("label_S6: S6 FAIL")
        off = day_offset(tag, arm, rules)
        hn = {}
        if off:
            for k in ("H4", "H5"):
                hn[k + "n"] = {"note": "REPORTED: H4 and H5 re-read with every measured J (and W) divided by (1 + offset_W)",
                               "result": rescale_h(tag, k, M, fc[tag], rules, 1.0 + off["offset_W"])}
        res["arms"][tag] = {"verdicts": v, "labels": label, "counts": {q: {"n": len(cells[q]), "pass": sum(1 for c in cells[q] if c["pass"])}
                                                                         for q in TIME_RULES + ENERGY_RULES},
                            "head_to_head": hd, "cells": cells, "measured": M, "flags": flags, "R0_failures": r0, "S6_failures": s6,
                            "day_offset_REPORTED": off, "offset_rescaled_REPORTED": hn, "by_family_REPORTED": model_stats(M, fc[tag]),
                            "readings_REPORTED": readings(tag, M, fc[tag], sim[tag], rules),
                            "bands": {q: rules["arms"][tag]["bands"][q]["band"] for q in TIME_RULES + ENERGY_RULES},
                            "band_w": rules["arms"][tag]["band_w"]["band_W"], "ties": rules["arms"][tag]["ties"]}
        scored_arms.append(tag)
    for k in H2H:
        if len(scored_arms) == 2:
            res["pooled"]["HP" + k[1]] = dict(decide(allh[k]), bootstrap_REPORTED=boot(allh[k], f"E213|bootstrap|pooled|{k}"))
        else:
            res["pooled"]["HP" + k[1]] = {"verdict": "NO DATA", "note": "HP needs both arms scored"}
    if not quiet:
        print(text(res))
    return res


def rescale_h(tag, k, M, fc, rules, s):
    M2 = copy.deepcopy(M)
    for v in M2.values():
        if v["W"] is not None:
            v["W"] /= s
            v["J"] /= s
    cells, h = score_arm(tag, M2, fc, rules, None)
    return decide(h[k])


def text(res):
    L = ["E213 scorer (score_e213.py), the registered verdicts:"]
    for tag in ARMS:
        a = res["arms"][tag]
        L.append(f"ARM {tag}: " + "; ".join(f"{r} {a['verdicts'][r]}" + (f" {a['counts'][r]['pass']}/{a['counts'][r]['n']}" if r in a.get("counts", {}) else "")
                                            for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES))
        for k in H2H:
            hd = (a.get("head_to_head") or {}).get(k)
            if hd:
                b = hd.get("bootstrap_REPORTED") or {}
                L.append(f"  {k} {hd['verdict']} (v3 {hd.get('v3_closer')} / v2 {hd.get('v2_closer')} / ties {hd.get('ties')}; p {hd.get('p_two_sided')}); "
                         f"REPORTED bootstrap {b.get('reading')} {b.get('ci95')}")
            else:
                L.append(f"  {k} {a['verdicts'][k]}")
        if a.get("labels"):
            L.append(f"  labels: {a['labels']}")
        if a.get("flags"):
            L.append(f"  flags: {a['flags'][:12]}{' ...' if len(a['flags']) > 12 else ''}")
    L.append("POOLED: " + "; ".join(f"{k} {v['verdict']}" + (f" ({v.get('v3_closer')}/{v.get('v2_closer')}/{v.get('ties')}, p {v.get('p_two_sided')})"
                                                           if v.get("v3_closer") is not None else "") for k, v in res["pooled"].items()))
    return "\n".join(L)


# ------------------------------------------------------------------ stand-ins and self-tests
def standin_run(p, f, n, block, scale_t=1.0, scale_W=1.0, mhz=600, check="exact", mask=None, walk_bad=False, prest=25.0):
    """a reducer RUN from a model's frozen figures: time scale_t x, W over idle at its own affine form at the run's seconds, x scale_W"""
    ops = p["ops_per_minion_per_gemm"]
    t = f["t"] * scale_t
    W = None
    if f["A"] is not None:
        W = (f["A"] + f["B"] / (f["cw"] * scale_t / 600.0)) * scale_W
    r = {"t_gemm_s": t, "cycles_gemm": f["cw"] * scale_t * ops, "cycles_per_op": f["cm"] * scale_t, "p_rest_w": prest,
         "p_work_w": (prest + W) if W is not None else None, "die_start_c": 52.0, "mhz_min": mhz, "mhz_max": mhz, "checks": [check],
         "record": {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": mask or p["shire_mask"]}, "block": block, "n": n}
    if p["host"] == "rgm211":
        r["walk"] = {"ok": [not walk_bad] * 13, "launches_bad": 1 if walk_bad else 0}
        r["gate"] = "GATE OK: stand-in"
    return r


def standin_day(frozen, how):
    rules, P, fc, sim = frozen
    data = {"experiment": "E213", "arms": {}}
    for tag in ARMS:
        if how.get("drop_arm") == tag:
            continue
        A = P["arms"][tag]
        arm = {"smoke": {"runs": []}, "points": {}, "ties": {"runs": []}}
        for i, s in enumerate(A["smoke"]):
            sm = {"t_gemm_s": 0.001, "cycles_per_op": 900.0, "checks": ["exact"], "block": "smoke", "n": -i - 1, "point": s["id"],
                  "record": {"arm": s["arm"], "type": s["format"], "minions": s["minions"], "shire_mask": s["shire_mask"]}}
            if s["host"] == "rgm211":
                sm["walk"] = {"ok": [True] * 3, "launches_bad": 0}
                sm["gate"] = "GATE OK: stand-in"
            if how.get("smoke_bad") and i == 0:
                sm["checks"] = ["wrong"]
            if how.get("fam_smoke_bad") and s["id"] in ((rules.get("A1") or {}).get("family_smoke") or {}).get(tag, {}):
                sm["checks"] = ["wrong"]            # A1's days Q and R: the family smoke's check of C wrong
            arm["smoke"]["runs"].append(sm)
        tie = A["tie"]
        ref = rules["day_offset_reference"][tag]
        for j in range(3):
            arm["ties"]["runs"].append({"t_gemm_s": ref.get("t_gemm_s") or 0.01, "cycles_gemm": 1.0, "cycles_per_op": 1000.0, "p_rest_w": 25.0,
                                        "p_work_w": 25.0 + (ref.get("W_over_idle") or 10.0) * how.get("tie_scale", 1.0), "checks": ["exact"],
                                        "mhz_min": 600, "mhz_max": 600, "block": "tie", "n": 1000 + j,
                                        "record": {"arm": tie["arm"], "type": tie["format"], "minions": tie["minions"], "shire_mask": tie["shire_mask"]}})
        ids = [p for p in A["points"] if p["id"] not in how.get("drop_points", [])]      # A1's day Q: the dropped family's points never ran
        if how.get("only"):
            ids = [p for p in ids if p["id"] in how["only"]]
        k = 0
        for p in ids:
            mdl = how.get("model", "v3")
            if how.get("alternate"):
                mdl = "v3" if (sorted({q["case"] for q in A["points"]}).index(p["case"]) % 2 == 0) else "v2"
            f = dict(fc[tag][p["id"]][mdl])
            if f["A"] is None:      # a model that prices no energy here: the time from it, the energy at MM1-v3's
                f["A"], f["B"] = fc[tag][p["id"]]["v3"]["A"], fc[tag][p["id"]]["v3"]["B"]
            st, sw = how.get("scale_t", 1.0), how.get("scale_W", 1.0)
            runs = []
            for rr in range(2 if tag == "B" else 1):
                k += 1
                r = standin_run(p, f, k, "pass1", st, sw, mhz=how.get("mhz", 600) if p["id"] in how.get("mhz_point", []) else 600,
                                check="wrong" if p["id"] == how.get("bad_check") else "exact",
                                mask=("0x1" if p["id"] == how.get("bad_mask") else None), walk_bad=(p["id"] == how.get("walk_bad")))
                if how.get("watts_add") is not None and fc[tag][p["id"]]["v3"]["W"] is not None and fc[tag][p["id"]]["v3"]["W"] < LOW:
                    r["p_work_w"] += how["watts_add"]
                runs.append(r)
            arm["points"][p["id"]] = {"runs": runs}
        data["arms"][tag] = arm
    return data


def expected(frozen, how):
    """the verdicts a stand-in day must give, by arithmetic written apart from the scorer's code path (the frozen columns and the bands only)"""
    rules, P, fc, sim = frozen
    lab = how.get("labels", {})
    exp = {}
    for tag in ARMS:
        if how.get("drop_arm") == tag:
            exp[tag] = {r: "NO DATA" for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES + H2H}
            continue
        R = rules["arms"][tag]
        A = P["arms"][tag]
        pts = [p for p in A["points"] if p["role"] == "point" and (not how.get("only") or p["id"] in how["only"])
               and p["id"] not in lab.get(tag, {}).get("ran_before_points", []) and p["id"] != how.get("bad_mask") and p["id"] != how.get("walk_bad")
               and p["id"] not in how.get("drop_points", [])]
        allcases = sorted({q["case"] for q in A["points"]})
        st, sw = how.get("scale_t", 1.0), how.get("scale_W", 1.0)
        tc = {}
        for p in pts:
            mdl = how.get("model", "v3")
            if how.get("alternate"):
                mdl = "v3" if allcases.index(p["case"]) % 2 == 0 else "v2"
            tc.setdefault(p["case"], (p, mdl))
        mine = lambda i: bool(i) and i.startswith("a" if tag == "A" else "k")  # noqa: E731
        fam_ran = tag == "A" and how.get("fam_smoke_bad") and not how.get("drop_points")   # A1: the family smoke failed and its family ran
        e = {"R0": "FAIL" if (mine(how.get("bad_check")) or how.get("smoke_bad") or mine(how.get("walk_bad")) or fam_ran) else "PASS",
             "S6": "FAIL" if any(i.startswith("a" if tag == "A" else "k") for i in how.get("mhz_point", [])) else "PASS"}
        for q, key in (("T1", "cw"), ("T2", "cm"), ("T3", "t")):
            ok = [abs(fc[tag][p["id"]][m][key] * st / fc[tag][p["id"]]["v3"][key] - 1) <= R["bands"][q]["band"] + 1e-12 for p, m in tc.values()]
            exp_n = len(ok)
            e[q] = "NO DATA" if exp_n == 0 else ("TOO FEW" if exp_n < 10 else ("PASS" if sum(ok) >= math.ceil(0.9 * exp_n - 1e-9) else "FAIL"))
        Eok = {q: [] for q in ENERGY_RULES}
        for p in pts:
            m = how.get("model", "v3")
            if how.get("alternate"):
                m = "v3" if allcases.index(p["case"]) % 2 == 0 else "v2"
            f3 = fc[tag][p["id"]]["v3"]
            fm = dict(fc[tag][p["id"]][m])
            if fm["A"] is None:
                fm["A"], fm["B"] = f3["A"], f3["B"]
            if f3["W"] is None:
                continue
            t = fm["t"] * st
            top = fm["cw"] * st / 600.0
            W = (fm["A"] + fm["B"] / top) * sw
            if how.get("watts_add") is not None and f3["W"] < LOW:
                W += how["watts_add"]
            Wg3 = f3["A"] + f3["B"] / top
            watts = f3["W"] < LOW or W < LOW
            bw = R["band_w"]["band_W"]
            Eok["E1"].append(abs(W - Wg3) <= bw + 1e-12 if watts else abs(W / Wg3 - 1) <= R["bands"]["E1"]["band"] + 1e-12)
            Eok["E2"].append(abs(W - f3["W"]) <= bw + 1e-12 if watts else abs(W * t / f3["J"] - 1) <= R["bands"]["E2"]["band"] + 1e-12)
            pr = 25.0
            Eok["E3"].append(abs((pr + W) * t / (pr * t + Wg3 * t) - 1) <= R["bands"]["E3"]["band"] + 1e-12)
            Eok["E4"].append(abs((pr + W) * t / (pr * f3["t"] + f3["J"]) - 1) <= R["bands"]["E4"]["band"] + 1e-12)
        for q in ENERGY_RULES:
            n = len(Eok[q])
            e[q] = "NO DATA" if n == 0 else ("TOO FEW" if n < 10 else ("PASS" if sum(Eok[q]) >= math.ceil(0.9 * n - 1e-9) else "FAIL"))
        for k in H2H:
            e[k] = how.get("expect_h", {}).get(tag, {}).get(k)
        exp[tag] = e
    return exp


STANDINS = {
    "A": ({"model": "v3"}, "every point at MM1-v3's forecast (time; W at its own affine form at the run's seconds), both arms"),
    "B": ({"model": "v2"}, "every point at MM1-v2's (where it prices no energy, MM1-v3's W): the bands decide by the gaps; v2 closer"),
    "C": ({"model": "v3", "scale_t": 1.25}, "MM1-v3's time x 1.25, W at its affine form at those seconds: the time rules and E4 fail; E2 holds "
                                            "where the per-op energy (B / t) dominates W, as it does at most points"),
    "D": ({"model": "v3", "scale_W": 1.25}, "MM1-v3's time, W 25% over its given W: energy rules fail, time passes"),
    "E": ({"model": "v3", "bad_check": "a001"}, "case A with one check of C wrong in arm A: R0 FAIL in arm A, labels"),
    "F": ({"model": "v3", "mhz_point": ["a002", "k02"], "mhz": 620}, "case A with one run in each arm at 620 MHz: S6 FAIL in both arms"),
    "G": ({"model": "v3", "bad_mask": "a002"}, "case A with a002's run carrying another mask: set aside, a002 NO DATA"),
    "H": ({"model": "v3", "drop_arm": "B"}, "case A with arm B missing: arm B NO DATA; the pooled rules NO DATA"),
    "I": ({"model": "v3", "only": ["a001", "a002", "a003", "a004", "a005", "a006", "k01", "k02", "k03", "k04", "k05"]},
          "case A with only a few points: TOO FEW"),
    "J": ({"alternate": True}, "the time cases in sorted order alternate between MM1-v3's and MM1-v2's figures: the head-to-head not decided"),
    "K": ({"model": "v3", "labels": {"A": {"ran_before_points": ["a001"]}, "B": {"ran_before_points": ["k01"]}}},
          "case A with a001 and k01 labelled 'ran before': they leave every rule"),
    "L": ({"model": "v3", "watts_add": 0.7}, "case A but every point MM1-v3 puts under 3 W reads 0.7 W more (over the 0.60 W band): E1, E2 fail in arm A"),
    "M": ({"model": "v3", "watts_add": 0.5}, "case A but those points read 0.5 W more (inside the band): E1, E2 pass"),
    "N": ({"model": "v3", "walk_bad": "a073"}, "case A with a gemmLn run's walk bad: R0 FAIL in arm A, a073 set aside"),
    "O": ({"model": "v3", "smoke_bad": True}, "case A with a smoke check wrong in both arms: R0 FAIL"),
    "P": ({"model": "v3", "tie_scale": 1.05}, "case A with the ties reading 5% more W over idle than the reference: the day offset +5% (REPORTED)"),
    "Q": ({"model": "v3", "fam_smoke_bad": True, "drop_points": ["a074", "a078", "a081", "a085"]},
          "Amendment A1: case A with arm A's family smoke s04 failed (its check of C wrong) and its family 'rgm211 gemmL' dropped (a074, a078, a081 "
          "and a085 never ran): R0 PASS, the drop flagged, the four NO DATA"),
    "R": ({"model": "v3", "fam_smoke_bad": True},
          "Amendment A1: case A with s04 failed while its family's points ran anyway (a kit fault): R0 FAIL in arm A"),
}
H_EXPECT = {
    "A": {"A": dict.fromkeys(H2H, "MM1-v3 BETTER"), "B": dict.fromkeys(H2H, "MM1-v3 BETTER")},
    "Q": {"A": dict.fromkeys(H2H, "MM1-v3 BETTER"), "B": dict.fromkeys(H2H, "MM1-v3 BETTER")},
    "R": {"A": dict.fromkeys(H2H, "MM1-v3 BETTER"), "B": dict.fromkeys(H2H, "MM1-v3 BETTER")},
    "B": {"A": dict.fromkeys(H2H, "MM1-v2 BETTER"), "B": dict.fromkeys(H2H, "MM1-v2 BETTER")},
}


def selftest_standins(outp):
    frozen = load_frozen()
    res, ok_all = {}, True
    for day, (how, what) in STANDINS.items():
        how = dict(how)
        data = standin_day(frozen, how)
        got = score(data, labels=how.get("labels"), frozen=frozen, quiet=True)
        exp = expected(frozen, how)
        row = {"what": what, "got": {}, "expected": {}, "ok": True}
        for tag in ARMS:
            g = got["arms"][tag]["verdicts"]
            row["got"][tag] = g
            row["expected"][tag] = {k: v for k, v in exp[tag].items() if v is not None}
            for kk, vv in exp[tag].items():
                if vv is not None and g.get(kk) != vv:
                    row["ok"] = False
            hx = H_EXPECT.get(day, {}).get(tag)
            if hx:
                for kk, vv in hx.items():
                    row["expected"][tag][kk] = vv
                    if g.get(kk) != vv:
                        row["ok"] = False
        row["pooled"] = {k: v["verdict"] for k, v in got["pooled"].items()}
        if day == "H" and any(v != "NO DATA" for v in row["pooled"].values()):
            row["ok"] = False
        if day == "J":
            hv = [got["arms"][t]["verdicts"][k] for t in ARMS for k in ("H1", "H2", "H3")]
            row["J_time_h2h"] = hv
            if any(v in ("MM1-v3 BETTER", "MM1-v2 BETTER") for v in hv):
                row["ok"] = False
        if day == "P":
            off = got["arms"]["A"]["day_offset_REPORTED"]
            row["offset_W"] = off and round(off["offset_W"], 6)
            if not off or abs(off["offset_W"] - 0.05) > 1e-9:
                row["ok"] = False
        if day == "G" and "a002" in got["arms"]["A"]["measured"]:
            row["ok"] = False
        if day == "K":
            if got["arms"]["A"]["counts"]["T1"]["n"] != standin_counts(frozen, "A") - 1:
                row["ok"] = False
        if day == "Q":              # A1: the drop flagged, the four points NO DATA (absent from the measured), four cases fewer
            fl = got["arms"]["A"]["flags"]
            row["A1_flag"] = [x for x in fl if x.startswith("A1: ")][:1]
            if not row["A1_flag"] or any(i in got["arms"]["A"]["measured"] for i in how["drop_points"]) or \
                    got["arms"]["A"]["counts"]["T1"]["n"] != standin_counts(frozen, "A") - 4 or got["arms"]["A"]["R0_failures"]:
                row["ok"] = False
        if day == "R" and not any("A1: the family smoke" in x for x in got["arms"]["A"]["R0_failures"]):
            row["ok"] = False
        ok_all &= row["ok"]
        res[day] = row
    seen = {}
    for tag in ARMS:
        for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES:
            seen[f"{tag} {r}"] = sorted({res[d]["got"][tag][r] for d in res})
    cover = all(("PASS" in v and "FAIL" in v) for v in seen.values())
    hseen = {f"{tag} {k}": sorted({res[d]["got"][tag][k] for d in res}) for tag in ARMS for k in H2H}
    hcover = all(("MM1-v3 BETTER" in v and "MM1-v2 BETTER" in v and "NOT DECIDED" in v) for v in hseen.values())
    out = {"what": "score_e213 stand-in days: verdicts stated before the run by expected() (written apart from the scorer's code path)",
           "days": res, "every_rule_seen_pass_and_fail": seen, "cover_pass_fail": cover, "head_to_head_seen": hseen, "cover_h2h": hcover,
           "verdict": "PASS" if (ok_all and cover and hcover) else "FAIL"}
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True, default=float)
    lines = [f"score_e213 --selftest-standins: {out['verdict']} (every day as stated: {ok_all}; every rule seen PASS and FAIL: {cover}; every "
             f"head-to-head seen v3 / v2 / not decided: {hcover})"]
    for d, r in res.items():
        lines.append(f"day {d} ({'ok' if r['ok'] else 'NOT AS STATED'}): {r['what']}")
        for tag in ARMS:
            lines.append(f"   arm {tag}: " + ", ".join(f"{k} {v}" for k, v in sorted(r["got"][tag].items())))
        lines.append(f"   pooled: {r['pooled']}")
    open(outp.replace(".json", ".txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:1]))
    return 0 if out["verdict"] == "PASS" else 1


def standin_counts(frozen, tag):
    P = frozen[1]
    return len({p["case"] for p in P["arms"][tag]["points"] if p["role"] == "point"})


def selftest_real(outp):
    """E207's (aifoundry3) and E206 arm B's (card 1) committed runs through this scorer's reader: every point's mean figures against MM1-v3's own
    vendored reading of the same runs (tools/matmul/mm1/v3/inputs, read by its data loader's records in data_v3's e207_points / e206b_points)"""
    sys.path.insert(0, os.path.join(REPO, "tools", "matmul", "mm1", "v3"))
    import data_v3 as DV  # noqa: E402
    srcs = {"E207": ("docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/data-e207.json", "A", DV.e207_points()),
            "E206 arm B": ("docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/data-e206.json", "B", DV.e206b_points())}
    out = {"what": "the reader on real committed bytes", "sets": {}}
    ok_all = True
    for name, (rel, armk, vend) in srcs.items():
        d = json.load(open(os.path.join(REPO, rel)))["arms"][armk]
        byv = {}
        for r in vend:
            byv.setdefault(r["id"].split("|")[-1] if "|" in r["id"] else r["id"], r)
        n, worst, miss = 0, 0.0, []
        for pid, pt in d["points"].items():
            runs = pt["runs"]
            arm_ = runs[0]["record"]["arm"] if runs else ""
            if not arm_.startswith("gemmL") or not arm_[5:].replace("x", "").isdigit():
                continue
            MB, NB, KB = (int(x) for x in arm_[5:].split("x"))
            ops = MB * NB * 2 * KB * 32
            p = {"id": pid, "arm": arm_, "format": runs[0]["record"]["type"], "minions": runs[0]["record"]["minions"],
                 "shire_mask": runs[0]["record"]["shire_mask"], "host": "rgm136", "ops_per_minion_per_gemm": ops, "case": arm_, "role": "point",
                 "family": "real", "loop": "rgm136 gemmL"}
            Pfake = {"arms": {"X": {"points": [p]}}}
            M, flags, r0, s6 = reduce_arm("X", {"points": {pid: pt}}, Pfake, {})
            v = byv.get(pid)
            if pid not in M or v is None:
                miss.append(pid)
                continue
            n += 1
            for key_s, key_v in (("t", "t_gemm"), ("W", "w_over"), ("cm", "cyc_mean"), ("cw", "cw")):
                a, b = M[pid].get(key_s), v.get(key_v)
                if a is None or b is None:
                    continue
                worst = max(worst, abs(a / b - 1))
        good = n > 0 and worst < 1e-9
        ok_all &= good
        out["sets"][name] = {"source": rel, "sha256": sha_rel(rel), "points_compared": n, "not_compared": miss[:20],
                             "worst_relative_difference": worst, "equal": good}
    out["verdict"] = "PASS" if ok_all else "FAIL"
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True)
    txt = [f"score_e213 --selftest-real: {out['verdict']}"] + [f"  {k}: {v['points_compared']} points, worst relative difference "
                                                                f"{v['worst_relative_difference']:.1e} (equal {v['equal']}); not compared {v['not_compared']}"
                                                                for k, v in out["sets"].items()]
    open(outp.replace(".json", ".txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))
    return 0 if ok_all else 1


def forecasts_print():
    rules, P, fc, sim = load_frozen()
    L, worst = [], {"v3": 0.0, "v2": 0.0}
    for tag in ARMS:
        for p in P["arms"][tag]["points"]:
            f = fc[tag][p["id"]]
            row = f"{tag} {p['id']} {p['role']:9s} {p['name']:36s}"
            for mdl in ("v3", "v2"):
                m = f[mdl]
                if m["A"] is not None and m["t"]:
                    Wg, Jg = given(m, m["cw"], m["t"])
                    worst[mdl] = max(worst[mdl], abs(Wg / m["W"] - 1))
                row += f" | {mdl} {m['cw']:.1f} {m['cm']:.1f} {1e3 * m['t']:.4f} ms " + (f"{m['W']:.3f} W {1e3 * m['J']:.3f} mJ" if m["W"] is not None else "energy n.f.")
            L.append(row)
    head = (f"score_e213 --forecasts: the frozen forecasts as the scorer reads them; given() at each model's own seconds reproduces its frozen W "
            f"to {worst['v3']:.1e} (MM1-v3) and {worst['v2']:.1e} (MM1-v2) relative (the CSVs print A and B to 5 decimals)")
    print(head)
    print("\n".join(L))
    return head, L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins")
    ap.add_argument("--selftest-real")
    ap.add_argument("--forecasts", action="store_true")
    a = ap.parse_args()
    if a.selftest_standins:
        sys.exit(selftest_standins(a.selftest_standins))
    if a.selftest_real:
        sys.exit(selftest_real(a.selftest_real))
    if a.forecasts:
        head, L = forecasts_print()
        open(os.path.join(HERE, "forecasts-e213.txt"), "w").write(head + "\n" + "\n".join(L) + "\n")
        return
    data = json.load(open(a.data))
    labels = json.load(open(a.labels)) if a.labels else {}
    res = score(data, labels)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=float)


if __name__ == "__main__":
    main()
