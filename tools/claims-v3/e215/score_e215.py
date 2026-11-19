#!/usr/bin/env python3
"""E215 (Q224): the frozen scorer of MM1-v3.1's BLIND MATMUL DAY, two arms. It reads the kits' reduced data (E206's and E213's run form, below), the
frozen forecasts (arm A: MM1-v3.1's and MM1-v3's in tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.json, frozen in MM1-v3.1's land; MM1-v2's
beside in forecast-e215a-v2.csv; arm B: forecast-e215b-v31.csv, -v3.csv, -v2.csv; both arms: 'v3.1 with T7' in forecast-e215-t7.csv; the
references in forecast-e215-refs.csv), and this folder's rules and points, and refuses to run (exit 4) if any of those files' bytes changed.
Standard library only.

    python3 -I -B tools/claims-v3/e215/score_e215.py DATA.json [--labels LABELS.json] [--out SCORED.json]
    python3 -I -B tools/claims-v3/e215/score_e215.py --selftest-standins OUT.json   stand-in days whose verdicts are stated before the run (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e215/score_e215.py --selftest-real OUT.json       E213's committed runs (both arms) through this reader
    python3 -I -B tools/claims-v3/e215/score_e215.py --forecasts                    every point's forecasts and the given() self-check

THE DATA (one JSON; E213's reducer form): {"experiment": "E215", "arms": {"A": ARM, "B": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"runs": [RUN, ...]}, "points": {pid: {"runs": [RUN, ...]}}, "ties": {"runs": [RUN, ...]}}   (references are points)
  RUN = {"t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (launch >= 0, ok, wall_s >= 0.1 s, the kernel clock
         cycles_max / wall in 590-610 MHz; calibration and check launches never count), "cycles_per_op": the median over the counted launches of
         the host's cycles_per_op (the counter's mean over minions / ops), "cycles_gemm": the median of cycles_max / passes (the slowest minion's
         counter, a GEMM), "p_work_w": the median board W of the 10 Hz samples inside the counted launches, "p_rest_w": the median board W of the
         last 5 s of the run's rest read, "die_start_c", "mhz_min", "mhz_max" (the counted samples' minion clock), "checks" (every check of C of
         the run: "exact" / "approx" / "wrong"), "record": {"arm", "type", "minions", "shire_mask"} as the host prints them, "block", "n": its
         place in the session, and for a process of rgm211's host (gemmLn, gemmLnc, rgm211's gemmL): "walk": {"ok": [walk_ok of every counted
         launch], "launches_bad": the check line's walk_launches_bad} and "gate": the identity gate's words ("GATE OK: ..." or "GATE FAILED: ...");
         a smoke RUN carries "point" (its smoke point's id)}
MEASURED, per run: the wall cycles an op = cycles_gemm / ops a minion a GEMM; the counter's mean = cycles_per_op; seconds = t_gemm_s; W over idle =
  p_work - p_rest; J over idle = W t_gemm; J with the card at rest = p_work t_gemm. A run whose record differs from its point (arm, type, minions,
  or the shire mask read as a number), or whose rgm211-host walk or gate is not good, is SET ASIDE and flagged. A POINT is the mean of its kept
  runs; a CASE (kernel loop, arm, format, mask: time is kind-blind in every model) the mean of its points (families P, C, R and L; family S's
  points share their case with their random partner, a reference, so S is scored in energy only).
THE GROUPS: 'registered' = families P, C, R (DECLARED-v31.md item 10's literal rule); 'posthoc' = families L, S (E215.md's dated departure D1:
  points chosen post hoc after the fit; forecasts frozen before any E215 datum). Every rule below is scored per group and REPORTED APART; only the
  registered group carries E215's registered answer.
THE RULES (E215.md section 7; numbers from rules-e215.json; per arm and group):
  R0 (per arm) every check of C of the arm exact or approx (smoke, points, references, ties); the smoke's counter mean 200-4,000 cycles an op;
      every rgm211-host process's walk good and its gate GATE OK. A family smoke (every smoke but s01 and s11-s13: rules-e215 > family_smoke)
      that fails while NO point of its family has a run (the family dropped by its own stop path) is not an R0 failure: flagged and REPORTED, its
      points NO DATA; if any point of that family has a run, its failures count (E213's Amendment A1 form). A FAIL labels every other verdict.
  S6 (per arm) every kept run's counted samples at 590-610 MHz. A FAIL labels every other verdict of the arm.
  MM1-v3.1 PER CASE: T1 the wall cycles, T2 the counter's mean, T3 seconds: |measured / MM1-v3.1 - 1| <= the arm's band.
  MM1-v3.1 PER POINT: E1 J over idle given the measured seconds (MM1-v3.1's W = A + B / t_op at t_op = the measured wall cycles an op / 600 MHz in
      us, times t_gemm); E2 J over idle with the seconds forecast (its frozen J); E3 J at rest given t (p_rest t + E1's J); E4 J at rest with the
      seconds forecast (p_rest t_v3.1 + its frozen J); at a WATTS POINT (MM1-v3.1's frozen W or the measured W under 3 W) E1 and E2 read
      |W measured - W forecast| <= band_w.
  A rule's verdict: PASS if at least 90% of its scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none.
  HEAD TO HEAD, MM1-v3.1 against MM1-v3: H1 the wall per case, H2 the counter's mean per case, H3 seconds per case, H4 J over idle given the
      measured seconds per point both price, H5 J over idle with the seconds forecast per point both price; d = |ln(measured / v3)| - |ln(measured
      / v3.1)| (in watts of W at a watts point); MM1-v3.1 closer where d > the arm's tie, MM1-v3 where d < -tie; the exact two-sided sign test at
      0.05 on the untied decides: MM1-v3.1 BETTER / MM1-v3 BETTER / NOT DECIDED; TOO FEW under 10 untied; NO DATA with none. HP1-HP5: H1-H5
      pooled over both arms per group (each case or point once, with its own arm's tie); NO DATA unless both arms scored that group.
  LABELS (--labels): {"A": {"ran_before_points": [...], "ran_before_cases": [...]}, "B": {...}}: those points (and cases) leave every rule; the
      output names every label applied; a label naming no point or case is refused (exit 10).
REPORTED (never verdicts): MM1-v2's and 'v3.1 with T7''s cells at MM1-v3.1's bands and every model's rms and bias by family; the same sign
  test, cases and ties for MM1-v3.1 against MM1-v2 and for 'v3.1 with T7' against MM1-v3.1 (the walk's layout term at never-run layouts); the bootstrap 95%
  interval of the mean d (B = 10,000, seeded "E215|bootstrap|<group>|<arm>|<rule>"); the family check; the day offset from the ties against the
  committed reference (H4n, H5n); the readings (the census path, the layout spread at one shire count, the switch route's kind / random from the
  A B B A blocks, the card transfer at configurations both arms run, the timing simulation's two columns).
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
D = "tools/claims-v3/e215/"
LANDJ = "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.json"
PINS = {
    LANDJ: "90742cddce9a355ddf53e85eb80a8075bc67613d36e804d12a8d422d342fd4d4",
    "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv": "f8fe39b4fb847791352d5ccbcc92406f32cf28347fb3af1bca96b851bc8bc2cc",
    D + "forecast-e215b-v31.csv": "06541b49e7b86b510aa711bbda7da147806ef05c4c2b42be9c94b1447778cf80", D + "forecast-e215b-v3.csv": "12a91f344edc28184fefb6af131cee31e8a78dd47d86cd030f2ad695114a2c62", D + "forecast-e215b-v2.csv": "0f1c6297722de759e68386650a60afef2525f63c93d8a35b425ffbabc15b47a0", D + "forecast-e215a-v2.csv": "c220d569deb5ff5b54687e2ea012b6c291a493e0db9710481c69a7af89cdba1e",
    D + "forecast-e215-t7.csv": "be96d94ac263bfd6c378c8dfb05cc00abf229f734aa7e2241f32a190d8b934bf", D + "forecast-e215-refs.csv": "8eea6857bd7d0ba5a493b8262efe0b4e422707fd24dd2c0653f9de1a5f066bfe", D + "rules-e215.json": "e6d5c55421d890510a67db3d0de0453a44bfb9e0e12349e252b42c514bf6c5be", D + "points-e215.json": "d2bf8dddefdd0a565b531c55962cefe84ee1ef77618670ccbcd8e875f0646624",
}
ARMS = ("A", "B")
GROUPS = {"registered": ("P", "C", "R"), "posthoc": ("L", "S")}
TIME_RULES = ("T1", "T2", "T3")
ENERGY_RULES = ("E1", "E2", "E3", "E4")
H2H = ("H1", "H2", "H3", "H4", "H5")
MODELS = ("v31", "v3", "v2", "t7")
NAMES = {"v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "t7": "v3.1 with T7"}
SESSION_SMOKE = ("s01", "s11", "s12", "s13")
LOW = 3.0
FLOOR = {"fp32": 529.0, "fp16": 529.0, "int8": 270.0}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def fnum(x):
    return None if x in ("", None, "NOT FORECAST") else float(x)


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


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
                print(f"score_e215: REFUSED, {rel} is {got}, pinned {want}")
                sys.exit(4)
    rules = json.load(open(os.path.join(REPO, D + "rules-e215.json")))
    pts = json.load(open(os.path.join(REPO, D + "points-e215.json")))
    land = {q["token"]: q for q in json.load(open(os.path.join(REPO, LANDJ)))["points"]}

    def from_pred(r):
        wa = r.get("W_affine") or {}
        return {"cw": r.get("cycles_per_op_wall"), "cm": r.get("cycles_per_op_mean"), "t": r.get("seconds_per_gemm"), "W": r.get("W_over_idle"),
                "A": wa.get("A_W"), "B": wa.get("B_W_us"), "J": r.get("J_over_idle_per_gemm"), "Prest": (r.get("rest_law") or {}).get("P_rest_W"),
                "sim": r.get("sim_steps_per_minion_per_gemm")}

    def from_row(r):
        return {"cw": fnum(r.get("cycles_per_op_wall")), "cm": fnum(r.get("cycles_per_op_mean")), "t": fnum(r.get("seconds_per_gemm")),
                "W": fnum(r.get("W_over_idle")), "A": fnum(r.get("A_W")), "B": fnum(r.get("B_W_us")), "J": fnum(r.get("J_over_idle_per_gemm")),
                "Prest": fnum(r.get("P_rest_W_REPORTED")), "sim": fnum(r.get("sim_steps_per_minion_per_gemm"))}

    def rows(name):
        return list(csv.DictReader(open(os.path.join(REPO, D + name), newline="")))
    fc = {t: {} for t in ARMS}
    for r in rows("forecast-e215b-v31.csv"):
        fc["B"].setdefault(r["id"], {})["v31"] = from_row(r)
    for r in rows("forecast-e215b-v3.csv"):
        fc["B"].setdefault(r["id"], {})["v3"] = from_row(r)
    for r in rows("forecast-e215b-v2.csv"):
        fc["B"].setdefault(r["id"], {})["v2"] = from_row(r)
    for r in rows("forecast-e215a-v2.csv"):
        fc["A"].setdefault(r["id"], {})["v2"] = from_row(r)
    for p in pts["arms"]["A"]["points"]:
        q = land[p["source_token"]]
        fc["A"].setdefault(p["id"], {}).update({"v31": from_pred(q["v31"]), "v3": from_pred(q["v3"])})
    for r in rows("forecast-e215-t7.csv"):
        tag = "A" if r["card"] == "aifoundry3 card 0" else "B"
        fc[tag].setdefault(r["id"], {})["t7"] = from_row(r)
    name = {"MM1-v3.1": "v31", "MM1-v3": "v3", "MM1-v2": "v2"}
    for r in rows("forecast-e215-refs.csv"):
        tag = "A" if r["card"] == "aifoundry3 card 0" else "B"
        fc[tag].setdefault(r["id"], {})[name[r["model"]]] = from_row(r)
    return rules, pts, fc


def given(m, cw, t_gemm):
    """a model's W over idle at the measured op time by its frozen affine form, and its J over idle given t: t_op = the measured wall cycles an
    op / 600 MHz (the slowest minion's counter time, MM1-v3.1's fit footing for this run form); J = W x the measured seconds"""
    if m is None or m.get("A") is None or m.get("B") is None or not cw:
        return None, None
    W = m["A"] + m["B"] / (cw / 600.0)
    return W, W * t_gemm


# ------------------------------------------------------------------ the measured side
def reduce_arm(tag, arm, P, labels, fam_smoke=None):
    """per point (references included): the kept runs' mean figures; flags; R0 and S6 inputs; fam_smoke: {smoke id: its family's loop}"""
    A = P["arms"][tag]
    pts = {p["id"]: p for p in A["points"] + A.get("references", [])}
    out, flags, r0, s6 = {}, [], [], []
    fam_smoke = fam_smoke or {}
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
        Wl = [r["p_work_w"] - r["p_rest_w"] for r in kept if r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        out[pid] = {"n_runs": len(kept), "cw": mean([r["cycles_gemm"] / ops for r in kept]), "cm": mean([r["cycles_per_op"] for r in kept]),
                    "t": mean([r["t_gemm_s"] for r in kept]), "W": mean(Wl) if Wl else None,
                    "J": mean([(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in kept if r.get("p_work_w") is not None]) if Wl else None,
                    "Jrest": mean([r["p_work_w"] * r["t_gemm_s"] for r in kept if r.get("p_work_w") is not None]) if Wl else None,
                    "prest": mean([r["p_rest_w"] for r in kept if r.get("p_rest_w") is not None]),
                    "die": mean([r.get("die_start_c") for r in kept]), "case": p["case"], "role": p["role"], "family": p["family"],
                    "reading": p["reading"], "time_scored": p["time_scored"], "ops": ops, "format": p["format"], "loop": p["loop"],
                    "kind": p["kind"], "arm": p["arm"], "mask": p["shire_mask"]}
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
        fam = fam_smoke.get(r.get("point")) if r.get("block") == "smoke" else None
        if fam:
            fam_fail.setdefault(fam, []).extend(f"{r.get('point')} ({x})" for x in why)
        else:
            r0.extend(why)
    for fam, why in sorted(fam_fail.items()):
        if not why:
            continue
        members = sorted(pid for pid, p in pts.items() if p["loop"] == fam and p["role"] == "point")
        ran = [pid for pid in members if ((arm.get("points") or {}).get(pid) or {}).get("runs")]
        if ran:
            r0.extend(why + [f"the family smoke of '{fam}' failed, yet {ran} ran: counted in R0 (a family that ran past its failed smoke)"])
        else:
            flags.append(f"the family smoke of '{fam}' failed ({'; '.join(why)}): the family was dropped, its points {members} NO DATA; "
                         "not an R0 failure (E213's Amendment A1 form), REPORTED")
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


def score_group(tag, M, fc, rules, fams):
    """MM1-v3.1's rules and the head-to-head cells of one arm and group (REPORTED cells of the other models beside)"""
    R = rules["arms"][tag]
    band = {q: R["bands"][q]["band"] for q in TIME_RULES + ENERGY_RULES}
    band_w = R["band_w"]["band_W"]
    ties = R["ties"]
    scored = {pid: v for pid, v in M.items() if v["role"] == "point" and v["family"] in fams}
    cases = {}
    for pid, v in scored.items():
        if v["time_scored"]:
            cases.setdefault(v["case"], []).append(pid)
    cells = {q: [] for q in TIME_RULES + ENERGY_RULES}
    other = {m: {q: [] for q in TIME_RULES + ENERGY_RULES} for m in ("v3", "v2", "t7")}
    h = {k: [] for k in H2H}
    for case, ids in sorted(cases.items()):
        F = fc[ids[0]]
        meas = {"cw": mean([M[i]["cw"] for i in ids]), "cm": mean([M[i]["cm"] for i in ids]), "t": mean([M[i]["t"] for i in ids])}
        for q, key in (("T1", "cw"), ("T2", "cm"), ("T3", "t")):
            e = meas[key] / F["v31"][key] - 1
            cells[q].append({"case": case, "measured": meas[key], "v31": F["v31"][key], "err": e, "pass": abs(e) <= band[q]})
            for m in ("v3", "v2", "t7"):
                f = (F.get(m) or {}).get(key)
                if f:
                    e2 = meas[key] / f - 1
                    other[m][q].append({"case": case, "err": e2, "pass": abs(e2) <= band[q]})
        for hk, key, tk in (("H1", "cw", "cycles_ln"), ("H2", "cm", "cycles_ln"), ("H3", "t", "seconds_ln")):
            if (F.get("v3") or {}).get(key):
                d = abs(math.log(meas[key] / F["v3"][key])) - abs(math.log(meas[key] / F["v31"][key]))
                h[hk].append({"id": case, "d": d, "tie": ties[tk], "watts": False, "family": M[ids[0]]["family"]})
    for pid, v in sorted(scored.items()):
        F = fc[pid]
        f31, f3 = F["v31"], F.get("v3") or {}
        if v["W"] is None or f31.get("W") is None:
            continue
        watts = f31["W"] < LOW or v["W"] < LOW
        Wg, Jg = given(f31, v["cw"], v["t"])
        e1 = (abs(v["W"] - Wg) if watts else v["J"] / Jg - 1)
        cells["E1"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "v31": Wg if watts else Jg, "err": e1,
                            "pass": (e1 <= band_w) if watts else abs(e1) <= band["E1"]})
        e2 = (abs(v["W"] - f31["W"]) if watts else v["J"] / f31["J"] - 1)
        cells["E2"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "v31": f31["W"] if watts else f31["J"], "err": e2,
                            "pass": (e2 <= band_w) if watts else abs(e2) <= band["E2"]})
        e3 = v["Jrest"] / (v["prest"] * v["t"] + Jg) - 1
        cells["E3"].append({"point": pid, "measured": v["Jrest"], "v31": v["prest"] * v["t"] + Jg, "err": e3, "pass": abs(e3) <= band["E3"]})
        e4 = v["Jrest"] / (v["prest"] * f31["t"] + f31["J"]) - 1
        cells["E4"].append({"point": pid, "measured": v["Jrest"], "v31": v["prest"] * f31["t"] + f31["J"], "err": e4, "pass": abs(e4) <= band["E4"]})
        for m in ("v3", "v2", "t7"):
            fm = F.get(m) or {}
            if fm.get("W") is None:
                continue
            Wgm, Jgm = given(fm, v["cw"], v["t"])
            if Wgm is None:
                continue
            x1 = abs(v["W"] - Wgm) if watts else v["J"] / Jgm - 1
            other[m]["E1"].append({"point": pid, "err": x1, "pass": (x1 <= band_w) if watts else abs(x1) <= band["E1"]})
            x2 = abs(v["W"] - fm["W"]) if watts else v["J"] / fm["J"] - 1
            other[m]["E2"].append({"point": pid, "err": x2, "pass": (x2 <= band_w) if watts else abs(x2) <= band["E2"]})
        if f3.get("W") is not None:
            Wg3, Jg3 = given(f3, v["cw"], v["t"])
            if watts:
                d4 = abs(v["W"] - Wg3) - abs(v["W"] - Wg)
                d5 = abs(v["W"] - f3["W"]) - abs(v["W"] - f31["W"])
            else:
                d4 = abs(math.log(v["J"] / Jg3)) - abs(math.log(v["J"] / Jg))
                d5 = abs(math.log(v["J"] / f3["J"])) - abs(math.log(v["J"] / f31["J"]))
            tie = ties["watts_W"] if watts else ties["joules_ln"]
            h["H4"].append({"id": pid, "d": d4, "tie": tie, "watts": watts, "family": v["family"]})
            h["H5"].append({"id": pid, "d": d5, "tie": tie, "watts": watts, "family": v["family"]})
    return cells, h, other


def h_pair(M, fc, rules_arm, fams, x, y):
    """REPORTED head-to-heads beside the registered one (never verdicts): model x against model y with the arm's ties, H1-H5 as registered"""
    ties = rules_arm["ties"]
    scored = {pid: v for pid, v in M.items() if v["role"] == "point" and v["family"] in fams}
    cases = {}
    for pid, v in scored.items():
        if v["time_scored"]:
            cases.setdefault(v["case"], []).append(pid)
    h = {k: [] for k in H2H}
    for case, ids in sorted(cases.items()):
        F = fc[ids[0]]
        fx, fy = F.get(x) or {}, F.get(y) or {}
        for hk, key, tk in (("H1", "cw", "cycles_ln"), ("H2", "cm", "cycles_ln"), ("H3", "t", "seconds_ln")):
            m = mean([M[i][key] for i in ids])
            if fx.get(key) and fy.get(key):
                h[hk].append({"id": case, "d": abs(math.log(m / fy[key])) - abs(math.log(m / fx[key])), "tie": ties[tk], "watts": False,
                              "family": M[ids[0]]["family"]})
    for pid, v in sorted(scored.items()):
        fx, fy = fc[pid].get(x) or {}, fc[pid].get(y) or {}
        if v["W"] is None or fx.get("W") is None or fy.get("W") is None:
            continue
        watts = fc[pid]["v31"]["W"] < LOW or v["W"] < LOW
        Wx, Jx = given(fx, v["cw"], v["t"])
        Wy, Jy = given(fy, v["cw"], v["t"])
        if Wx is None or Wy is None:
            continue
        if watts:
            d4, d5 = abs(v["W"] - Wy) - abs(v["W"] - Wx), abs(v["W"] - fy["W"]) - abs(v["W"] - fx["W"])
        else:
            d4 = abs(math.log(v["J"] / Jy)) - abs(math.log(v["J"] / Jx))
            d5 = abs(math.log(v["J"] / fy["J"])) - abs(math.log(v["J"] / fx["J"]))
        tie = ties["watts_W"] if watts else ties["joules_ln"]
        h["H4"].append({"id": pid, "d": d4, "tie": tie, "watts": watts, "family": v["family"]})
        h["H5"].append({"id": pid, "d": d5, "tie": tie, "watts": watts, "family": v["family"]})
    out = {}
    for k in H2H:
        dd = decide(h[k])
        if "verdict" in dd:
            dd["verdict"] = dd["verdict"].replace("MM1-v3.1 BETTER", f"{NAMES[x]} CLOSER").replace("MM1-v3 BETTER", f"{NAMES[y]} CLOSER")
        dd["x_closer"], dd["y_closer"] = dd.pop("v31_closer", None), dd.pop("v3_closer", None)
        dd["REPORTED"] = True
        out[k] = dd
    return out


def decide(hc):
    npos = sum(1 for c in hc if c["d"] > c["tie"])
    nneg = sum(1 for c in hc if c["d"] < -c["tie"])
    n = len(hc)
    if n == 0:
        return {"verdict": "NO DATA", "n": 0}
    if npos + nneg < 10:
        return {"verdict": "TOO FEW", "n": n, "v31_closer": npos, "v3_closer": nneg, "ties": n - npos - nneg}
    p = sign_p(npos, nneg)
    v = ("MM1-v3.1 BETTER" if npos > nneg else "MM1-v3 BETTER") if p < 0.05 else "NOT DECIDED"
    return {"verdict": v, "n": n, "v31_closer": npos, "v3_closer": nneg, "ties": n - npos - nneg, "p_two_sided": p}


def boot(hc, seed):
    d = [c["d"] for c in hc if not c["watts"]]
    if len(d) < 2:
        return None
    rnd = random.Random(seed)
    n = len(d)
    ms = sorted(sum(d[rnd.randrange(n)] for _ in range(n)) / n for _ in range(10000))
    lo, hi = ms[249], ms[9749]
    return {"mean_d": sum(d) / n, "ci95": [lo, hi], "reading": "MM1-v3.1 BETTER" if lo > 0 else ("MM1-v3 BETTER" if hi < 0 else "NOT DECIDED"),
            "n": n, "REPORTED": True}


def family_check(hc):
    fam = {}
    for c in hc:
        fam.setdefault(c["family"], []).append(c["d"])
    med = {f: statistics.median(v) for f, v in fam.items()}
    npos = sum(1 for v in med.values() if v > 0)
    nneg = sum(1 for v in med.values() if v < 0)
    return {"family_median_d": {f: round(v, 5) for f, v in sorted(med.items())}, "v31": npos, "v3": nneg, "p_two_sided": sign_p(npos, nneg),
            "REPORTED": True}


def model_stats(M, fc):
    fam = {}
    for pid, v in M.items():
        if v["role"] != "point":
            continue
        for mdl in MODELS:
            f = fc[pid].get(mdl) or {}
            d = fam.setdefault(v["family"], {}).setdefault(mdl, {"cw": [], "J": [], "W_watts": []})
            if f.get("cw") and v["time_scored"]:
                d["cw"].append(math.log(v["cw"] / f["cw"]))
            if f.get("J") and v.get("J") and (v["W"] or 0) >= LOW and (f.get("W") or 0) >= LOW:
                d["J"].append(math.log(v["J"] / f["J"]))
            elif f.get("W") is not None and v.get("W") is not None:
                d["W_watts"].append(v["W"] - f["W"])
    out = {}
    for fm, dd in sorted(fam.items()):
        out[fm] = {NAMES[mdl]: {k: ({"n": len(x), "rms_pct" if k != "W_watts" else "rms_W": round((100 if k != "W_watts" else 1) * rms(x), 3),
                                     "bias_pct" if k != "W_watts" else "bias_W": round((100 if k != "W_watts" else 1) * sum(x) / len(x), 3)} if x else None)
                                for k, x in q.items()} for mdl, q in dd.items()}
    return out


def readings(tag, M, fc, P, Mother=None, fcother=None):
    """REPORTED: the census path, the layout spread, the switch route, the card transfer, the timing simulation"""
    out = {"census_path": [], "layout_sets": [], "switch_route": [], "card_transfer": [], "timing_simulation": {}}
    A = P["arms"][tag]
    by = {p["id"]: p for p in A["points"] + A.get("references", [])}
    shapes = {}
    for pid, p in by.items():
        if p["role"] == "point" and p["family"] == "P":
            shapes.setdefault((p["shape"][0], p["shape"][1], p["shape"][2], p["format"]), []).append(pid)
    for k, ids in sorted(shapes.items()):
        if len(ids) < 2:
            continue
        base = sorted(ids, key=lambda i: ("rgm136 gemmL", "rgm211 gemmL", "rgm211 gemmLn", "rgm136 gemmLnc").index(by[i]["loop"]))
        a = base[0]
        for b in base[1:]:
            if a in M and b in M:
                out["census_path"].append({"num": b, "den": a, "what": f"{by[b]['loop']} / {by[a]['loop']} at {by[a]['arm'][-5:]}",
                                           "measured_cw": M[b]["cw"] / M[a]["cw"],
                                           "models_cw": {NAMES[m]: (fc[b][m]["cw"] / fc[a][m]["cw"]) if (fc[b].get(m) and fc[a].get(m)) else None
                                                         for m in MODELS},
                                           "measured_W": (M[b]["W"] / M[a]["W"]) if (M[b]["W"] and M[a]["W"]) else None})
    sets = {}
    for pid, p in by.items():
        if p["role"] == "point" and p["family"] == "L":
            sets.setdefault((p["arm"], p["format"], p["kind"], p["shires"]), []).append(pid)
    for k, ids in sorted(sets.items()):
        vals = {i: M[i]["cw"] for i in ids if i in M}
        if len(vals) >= 2:
            out["layout_sets"].append({"points": sorted(ids), "shape_format_kind_shires": list(k), "measured_cw": vals,
                                       "spread": max(vals.values()) / min(vals.values()) - 1,
                                       "v31_spread": (max(fc[i]["v31"]["cw"] for i in vals) / min(fc[i]["v31"]["cw"] for i in vals) - 1),
                                       "t7_spread": (max(fc[i]["t7"]["cw"] for i in vals) / min(fc[i]["t7"]["cw"] for i in vals) - 1)
                                       if all(fc[i].get("t7") for i in vals) else None})
    refs = {r["format"]: r["id"] for r in A.get("references", [])}
    for pid, p in by.items():
        if p["role"] == "point" and p["family"] == "S":
            r = refs.get(p["format"])
            if pid in M and r in M and M[pid]["W"] is not None and M[r]["W"]:
                out["switch_route"].append({"kind": pid, "random": r, "what": f"{p['kind']} / random ({p['format']}, gemmL3x1x3)",
                                            "measured_W_ratio": M[pid]["W"] / M[r]["W"],
                                            "models_W_ratio": {NAMES[m]: ((fc[pid][m] or {}).get("W") / fc[r][m]["W"])
                                                               if ((fc[pid].get(m) or {}).get("W") and (fc[r].get(m) or {}).get("W")) else None
                                                               for m in MODELS}})
    if Mother is not None:
        oth = {(v["loop"], v["arm"], v["format"], v["kind"], int(v["mask"], 16)): (pid, v) for pid, v in Mother.items() if v["role"] == "point"}
        for pid, v in M.items():
            key = (v["loop"], v["arm"], v["format"], v["kind"], int(v["mask"], 16))
            if v["role"] == "point" and key in oth:
                qid, q = oth[key]
                out["card_transfer"].append({"this_arm": pid, "other_arm": qid, "config": list(key[:4]) + [hex(key[4])],
                                             "measured_cw_ratio_this_over_other": v["cw"] / q["cw"],
                                             "measured_W_ratio_this_over_other": (v["W"] / q["W"]) if (v["W"] and q["W"]) else None,
                                             "v31_W_ratio": ((fc[pid]["v31"].get("W") or 0) / fcother[qid]["v31"]["W"]) if fcother[qid]["v31"].get("W") else None})
    for pid, v in M.items():
        f3 = fc[pid].get("v3") or {}
        st_ = f3.get("sim")
        out["timing_simulation"][pid] = {"cycles_gemm_over_sim_steps": (v["cw"] * v["ops"] / st_) if st_ else None,
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


def rescale_h(tag, k, M, fc, rules, fams, s):
    M2 = copy.deepcopy(M)
    for v in M2.values():
        if v["W"] is not None:
            v["W"] /= s
            v["J"] /= s
    cells, h, _ = score_group(tag, M2, fc, rules, fams)
    return decide(h[k])


def score(data, labels=None, frozen=None, quiet=False):
    rules, P, fc = frozen or load_frozen()
    labels = labels or {}
    for tag in ARMS:
        lab = labels.get(tag, {})
        ids = {p["id"] for p in P["arms"][tag]["points"]}
        cases = {p["case"] for p in P["arms"][tag]["points"]}
        bad = [x for x in lab.get("ran_before_points", []) if x not in ids] + [x for x in lab.get("ran_before_cases", []) if x not in cases]
        if bad:
            print(f"score_e215: REFUSED (exit 10), labels naming nothing in arm {tag}: {bad}")
            sys.exit(10)
    res = {"experiment": "E215", "arms": {}, "pooled": {}, "labels_applied": labels, "groups": {g: list(v) for g, v in GROUPS.items()},
           "posthoc_label": P.get("posthoc_label")}
    allh = {g: {k: [] for k in H2H} for g in GROUPS}
    scored = {g: [] for g in GROUPS}
    Ms = {}
    for tag in ARMS:
        arm = (data.get("arms") or {}).get(tag) or {}
        if not arm or not arm.get("points"):
            res["arms"][tag] = {"verdicts": {g: {r: "NO DATA" for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES + H2H} for g in GROUPS},
                                "note": "arm missing or empty: NO DATA"}
            continue
        fsm = {s["id"]: s["loop"] for s in P["arms"][tag]["smoke"] if s["id"] not in SESSION_SMOKE}
        M, flags, r0, s6 = reduce_arm(tag, arm, P, labels.get(tag, {}), fsm)
        Ms[tag] = M
        vg, hd_all, counts, cells_all, other_all = {}, {}, {}, {}, {}
        for g, fams in GROUPS.items():
            cells, h, other = score_group(tag, M, fc[tag], rules, fams)
            v = {"R0": "FAIL" if r0 else "PASS", "S6": "FAIL" if s6 else "PASS"}
            for q in TIME_RULES + ENERGY_RULES:
                v[q] = verdict_frac(cells[q])
            hd = {}
            for k in H2H:
                hd[k] = decide(h[k])
                hd[k]["bootstrap_REPORTED"] = boot(h[k], f"E215|bootstrap|{g}|{tag}|{k}")
                hd[k]["family_check_REPORTED"] = family_check(h[k]) if h[k] else None
                v[k] = hd[k]["verdict"]
                allh[g][k] += h[k]
            if any(cells[q] for q in TIME_RULES + ENERGY_RULES):
                scored[g].append(tag)
            vg[g], hd_all[g], cells_all[g] = v, hd, cells
            counts[g] = {q: {"n": len(cells[q]), "pass": sum(1 for c in cells[q] if c["pass"])} for q in TIME_RULES + ENERGY_RULES}
            other_all[g] = {NAMES[m]: {q: {"n": len(x), "pass": sum(1 for c in x if c["pass"]), "verdict_REPORTED": verdict_frac(x)}
                                       for q, x in o.items()} for m, o in other.items()}
            other_all[g]["head_to_head_REPORTED"] = {"MM1-v3.1 against MM1-v2": h_pair(M, fc[tag], rules["arms"][tag], fams, "v31", "v2"),
                                                     "v3.1 with T7 against MM1-v3.1": h_pair(M, fc[tag], rules["arms"][tag], fams, "t7", "v31")}
        label = []
        if r0:
            label.append("label_R0: R0 FAIL")
        if s6:
            label.append("label_S6: S6 FAIL")
        off = day_offset(tag, arm, rules)
        hn = {}
        if off:
            for g, fams in GROUPS.items():
                for k in ("H4", "H5"):
                    hn[f"{g}:{k}n"] = {"note": "REPORTED: H4 and H5 re-read with every measured J (and W) divided by (1 + offset_W)",
                                       "result": rescale_h(tag, k, M, fc[tag], rules, fams, 1.0 + off["offset_W"])}
        res["arms"][tag] = {"verdicts": vg, "labels": label, "counts": counts, "head_to_head": hd_all, "cells": cells_all, "measured": M,
                            "flags": flags, "R0_failures": r0, "S6_failures": s6, "day_offset_REPORTED": off, "offset_rescaled_REPORTED": hn,
                            "other_models_at_v31_bands_REPORTED": other_all, "by_family_REPORTED": model_stats(M, fc[tag]),
                            "bands": {q: rules["arms"][tag]["bands"][q]["band"] for q in TIME_RULES + ENERGY_RULES},
                            "band_w": rules["arms"][tag]["band_w"]["band_W"], "ties": rules["arms"][tag]["ties"]}
    for tag in ARMS:
        if tag in Ms:
            o = "B" if tag == "A" else "A"
            res["arms"][tag]["readings_REPORTED"] = readings(tag, Ms[tag], fc[tag], P, Ms.get(o), fc[o])
    for g in GROUPS:
        res["pooled"][g] = {}
        for k in H2H:
            if len(scored[g]) == 2:
                res["pooled"][g]["HP" + k[1]] = dict(decide(allh[g][k]), bootstrap_REPORTED=boot(allh[g][k], f"E215|bootstrap|{g}|pooled|{k}"))
            else:
                res["pooled"][g]["HP" + k[1]] = {"verdict": "NO DATA", "note": "HP needs both arms scored in this group"}
    if not quiet:
        print(text(res))
    return res


def text(res):
    L = ["E215 scorer (score_e215.py), the verdicts - registered: families P, C, R; post hoc (reported apart): families L, S, "
         f"'{res.get('posthoc_label')}':"]
    for tag in ARMS:
        a = res["arms"][tag]
        for g in GROUPS:
            v = a["verdicts"][g]
            cnt = a.get("counts", {}).get(g, {})
            L.append(f"ARM {tag} {g.upper()} ({', '.join(GROUPS[g])}): " + "; ".join(
                f"{r} {v[r]}" + (f" {cnt[r]['pass']}/{cnt[r]['n']}" if r in cnt else "") for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES))
            for k in H2H:
                hd = (a.get("head_to_head") or {}).get(g, {}).get(k)
                if hd:
                    b = hd.get("bootstrap_REPORTED") or {}
                    L.append(f"  {g} {k} {hd['verdict']} (v3.1 {hd.get('v31_closer')} / v3 {hd.get('v3_closer')} / ties {hd.get('ties')}; p "
                             f"{hd.get('p_two_sided')}); REPORTED bootstrap {b.get('reading')} {b.get('ci95')}")
                else:
                    L.append(f"  {g} {k} {v[k]}")
        if a.get("labels"):
            L.append(f"  labels: {a['labels']}")
        if a.get("flags"):
            L.append(f"  flags: {a['flags'][:12]}{' ...' if len(a['flags']) > 12 else ''}")
    for g in GROUPS:
        L.append(f"POOLED {g.upper()}: " + "; ".join(f"{k} {v['verdict']}" + (f" ({v.get('v31_closer')}/{v.get('v3_closer')}/{v.get('ties')}, p {v.get('p_two_sided')})"
                                                                           if v.get("v31_closer") is not None else "") for k, v in res["pooled"][g].items()))
    return "\n".join(L)


# ------------------------------------------------------------------ stand-ins and self-tests
def standin_run(p, f, n, block, scale_t=1.0, scale_W=1.0, mhz=600, check="exact", mask=None, walk_bad=False, prest=25.0):
    """a reducer RUN from a model's frozen figures: time scale_t x, W over idle at its own affine form at the run's seconds, x scale_W"""
    ops = p["ops_per_minion_per_gemm"]
    t = f["t"] * scale_t
    W = None
    if f.get("A") is not None:
        W = (f["A"] + f["B"] / (f["cw"] * scale_t / 600.0)) * scale_W
    r = {"t_gemm_s": t, "cycles_gemm": f["cw"] * scale_t * ops, "cycles_per_op": f["cm"] * scale_t, "p_rest_w": prest,
         "p_work_w": (prest + W) if W is not None else None, "die_start_c": 52.0, "mhz_min": mhz, "mhz_max": mhz, "checks": [check],
         "record": {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": mask or p["shire_mask"]}, "block": block, "n": n}
    if p["host"] == "rgm211":
        r["walk"] = {"ok": [not walk_bad] * 13, "launches_bad": 1 if walk_bad else 0}
        r["gate"] = "GATE OK: stand-in"
    return r


def standin_model(fc, tag, p, how, allcases):
    mdl = how.get("model", "v31")
    if how.get("alternate"):
        key = p["case"] if p["time_scored"] else p["id"]
        mdl = "v31" if (allcases.index(key) % 2 == 0) else "v3"
    f = dict(fc[tag][p["id"]].get(mdl) or {})
    f31 = fc[tag][p["id"]]["v31"]
    for k in ("cw", "cm", "t"):
        if f.get(k) is None:
            f[k] = f31[k]
    if f.get("A") is None:          # a model that prices no energy here: the time from it, the energy at MM1-v3.1's
        f["A"], f["B"] = f31["A"], f31["B"]
    return f, mdl


def case_keys(A):
    return sorted({(p["case"] if p["time_scored"] else p["id"]) for p in A["points"]})


def standin_day(frozen, how):
    rules, P, fc = frozen
    data = {"experiment": "E215", "arms": {}}
    for tag in ARMS:
        if how.get("drop_arm") == tag:
            continue
        A = P["arms"][tag]
        allc = case_keys(A)
        arm = {"smoke": {"runs": []}, "points": {}, "ties": {"runs": []}}
        for i, s in enumerate(A["smoke"]):
            sm = {"t_gemm_s": 0.001, "cycles_per_op": 900.0, "checks": ["exact"], "block": "smoke", "n": -i - 1, "point": s["id"],
                  "record": {"arm": s["arm"], "type": s["format"], "minions": s["minions"], "shire_mask": s["shire_mask"]}}
            if s["host"] == "rgm211":
                sm["walk"] = {"ok": [True] * 3, "launches_bad": 0}
                sm["gate"] = "GATE OK: stand-in"
            if how.get("smoke_bad") and s["id"] in SESSION_SMOKE:
                sm["checks"] = ["wrong"]
            if how.get("fam_smoke_bad") and s["id"] == how["fam_smoke_bad"].get(tag):
                sm["checks"] = ["wrong"]
            arm["smoke"]["runs"].append(sm)
        tie = A["tie"]
        ref = rules["day_offset_reference"][tag]
        for j in range(3):
            arm["ties"]["runs"].append({"t_gemm_s": ref.get("t_gemm_s") or 0.01, "cycles_gemm": 1.0, "cycles_per_op": 1000.0, "p_rest_w": 25.0,
                                        "p_work_w": 25.0 + (ref.get("W_over_idle") or 10.0) * how.get("tie_scale", 1.0), "checks": ["exact"],
                                        "mhz_min": 600, "mhz_max": 600, "block": "tie", "n": 1000 + j,
                                        "record": {"arm": tie["arm"], "type": tie["format"], "minions": tie["minions"], "shire_mask": tie["shire_mask"]}})
        ids = [p for p in A["points"] + A["references"] if p["id"] not in how.get("drop_points", [])]
        if how.get("only"):
            ids = [p for p in ids if p["id"] in how["only"]]
        k = 0
        for p in ids:
            if p["role"] == "reference":
                f, _ = dict(fc[tag][p["id"]]["v31"]), "v31"
            else:
                f, _ = standin_model(fc, tag, p, how, allc)
            st, sw = how.get("scale_t", 1.0), how.get("scale_W", 1.0)
            if how.get("scale_W_S") is not None and p["family"] == "S":
                sw = how["scale_W_S"]
            runs = []
            for rr in range(2):
                k += 1
                r = standin_run(p, f, k, "pass1", st, sw, mhz=how.get("mhz", 600) if p["id"] in how.get("mhz_point", []) else 600,
                                check="wrong" if p["id"] == how.get("bad_check") else "exact",
                                mask=("0x1" if p["id"] == how.get("bad_mask") else None), walk_bad=(p["id"] == how.get("walk_bad")))
                if how.get("watts_add") is not None and fc[tag][p["id"]]["v31"].get("W") is not None and fc[tag][p["id"]]["v31"]["W"] < LOW:
                    r["p_work_w"] += how["watts_add"]
                runs.append(r)
            arm["points"][p["id"]] = {"runs": runs}
        data["arms"][tag] = arm
    return data


def expected(frozen, how):
    """the verdicts a stand-in day must give, by arithmetic written apart from the scorer's code path (the frozen columns, bands and ties only)"""
    rules, P, fc = frozen
    lab = how.get("labels", {})
    exp = {}
    pooled_d = {g: {k: [] for k in H2H} for g in GROUPS}
    pooled_ok = {g: 0 for g in GROUPS}
    for tag in ARMS:
        if how.get("drop_arm") == tag:
            exp[tag] = {g: {r: "NO DATA" for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES + H2H} for g in GROUPS}
            continue
        R = rules["arms"][tag]
        A = P["arms"][tag]
        allc = case_keys(A)
        ties = R["ties"]
        fam_drop = set(how.get("drop_points", []))
        smoke_fail_fam = None
        if how.get("fam_smoke_bad") and how["fam_smoke_bad"].get(tag):
            smoke_fail_fam = {s["id"]: s["loop"] for s in A["smoke"]}[how["fam_smoke_bad"][tag]]
        fam_ran = smoke_fail_fam is not None and any(p["loop"] == smoke_fail_fam and p["id"] not in fam_drop for p in A["points"])
        mine = lambda i: bool(i) and i.startswith("a" if tag == "A" else "b")  # noqa: E731
        R0 = "FAIL" if (mine(how.get("bad_check")) or how.get("smoke_bad") or mine(how.get("walk_bad")) or fam_ran) else "PASS"
        S6 = "FAIL" if any(mine(i) for i in how.get("mhz_point", [])) else "PASS"
        exp[tag] = {}
        for g, fams in GROUPS.items():
            pts = [p for p in A["points"] if p["family"] in fams and (not how.get("only") or p["id"] in how["only"])
                   and p["id"] not in lab.get(tag, {}).get("ran_before_points", []) and p["id"] != how.get("bad_mask")
                   and p["id"] != how.get("walk_bad") and p["id"] not in fam_drop]
            st, sw0 = how.get("scale_t", 1.0), how.get("scale_W", 1.0)
            e = {"R0": R0, "S6": S6}
            tc = {}
            for p in pts:
                if p["time_scored"]:
                    tc.setdefault(p["case"], p)
            hd = {k: [] for k in H2H}
            for q, key in (("T1", "cw"), ("T2", "cm"), ("T3", "t")):
                ok = []
                for p in tc.values():
                    f, _ = standin_model(fc, tag, p, how, allc)
                    m = f[key] * st
                    ok.append(abs(m / fc[tag][p["id"]]["v31"][key] - 1) <= R["bands"][q]["band"] + 1e-12)
                    hk = {"T1": "H1", "T2": "H2", "T3": "H3"}[q]
                    tk = "seconds_ln" if q == "T3" else "cycles_ln"
                    f3 = fc[tag][p["id"]]["v3"][key]
                    hd[hk].append((abs(math.log(m / f3)) - abs(math.log(m / fc[tag][p["id"]]["v31"][key])), ties[tk]))
                n = len(ok)
                e[q] = "NO DATA" if n == 0 else ("TOO FEW" if n < 10 else ("PASS" if sum(ok) >= math.ceil(0.9 * n - 1e-9) else "FAIL"))
            Eok = {q: [] for q in ENERGY_RULES}
            for p in pts:
                f31 = fc[tag][p["id"]]["v31"]
                if f31.get("W") is None:
                    continue
                fm, _ = standin_model(fc, tag, p, how, allc)
                sw = how["scale_W_S"] if (how.get("scale_W_S") is not None and p["family"] == "S") else sw0
                t = fm["t"] * st
                top = fm["cw"] * st / 600.0
                W = (fm["A"] + fm["B"] / top) * sw
                if how.get("watts_add") is not None and f31["W"] < LOW:
                    W += how["watts_add"]
                Wg = f31["A"] + f31["B"] / top
                watts = f31["W"] < LOW or W < LOW
                bw = R["band_w"]["band_W"]
                Eok["E1"].append(abs(W - Wg) <= bw + 1e-12 if watts else abs(W / Wg - 1) <= R["bands"]["E1"]["band"] + 1e-12)
                Eok["E2"].append(abs(W - f31["W"]) <= bw + 1e-12 if watts else abs(W * t / f31["J"] - 1) <= R["bands"]["E2"]["band"] + 1e-12)
                pr = 25.0
                Eok["E3"].append(abs((pr + W) * t / (pr * t + Wg * t) - 1) <= R["bands"]["E3"]["band"] + 1e-12)
                Eok["E4"].append(abs((pr + W) * t / (pr * f31["t"] + f31["J"]) - 1) <= R["bands"]["E4"]["band"] + 1e-12)
                f3 = fc[tag][p["id"]].get("v3") or {}
                if f3.get("W") is not None:
                    Wg3 = f3["A"] + f3["B"] / top
                    if watts:
                        hd["H4"].append((abs(W - Wg3) - abs(W - Wg), ties["watts_W"]))
                        hd["H5"].append((abs(W - f3["W"]) - abs(W - f31["W"]), ties["watts_W"]))
                    else:
                        hd["H4"].append((abs(math.log(W / Wg3)) - abs(math.log(W / Wg)), ties["joules_ln"]))
                        hd["H5"].append((abs(math.log(W * t / f3["J"])) - abs(math.log(W * t / f31["J"])), ties["joules_ln"]))
            for q in ENERGY_RULES:
                n = len(Eok[q])
                e[q] = "NO DATA" if n == 0 else ("TOO FEW" if n < 10 else ("PASS" if sum(Eok[q]) >= math.ceil(0.9 * n - 1e-9) else "FAIL"))
            for k in H2H:
                e[k] = sign_verdict(hd[k])
                pooled_d[g][k] += hd[k]
            if any(e[q] != "NO DATA" for q in TIME_RULES + ENERGY_RULES):
                pooled_ok[g] += 1
            exp[tag][g] = e
    exp["pooled"] = {g: {("HP" + k[1]): (sign_verdict(pooled_d[g][k]) if pooled_ok[g] == 2 else "NO DATA") for k in H2H} for g in GROUPS}
    return exp


def sign_verdict(dl):
    npos = sum(1 for d, t in dl if d > t)
    nneg = sum(1 for d, t in dl if d < -t)
    if not dl:
        return "NO DATA"
    if npos + nneg < 10:
        return "TOO FEW"
    p = sign_p(npos, nneg)
    return ("MM1-v3.1 BETTER" if npos > nneg else "MM1-v3 BETTER") if p < 0.05 else "NOT DECIDED"


def standins(P):
    A, B = P["arms"]["A"], P["arms"]["B"]

    def first(arm, cond):
        return next((p["id"] for p in arm["points"] if cond(p)), None)
    fam_a = next((s["id"] for s in A["smoke"] if s["loop"] == "rgm211 gemmLn"), None)
    fam_pts = [p["id"] for p in A["points"] if p["loop"] == "rgm211 gemmLn"]
    nc = [p["id"] for p in A["points"] + B["points"] if p["loop"] == "rgm136 gemmLnc"]
    few = ([p["id"] for p in A["points"] if p["family"] in ("P", "C")][:3] + [p["id"] for p in B["points"] if p["family"] in ("P", "C")][:3]
           + [first(A, lambda p: p["family"] == "L"), first(B, lambda p: p["family"] == "L")])
    return {
        "A": ({"model": "v31"}, "every point at MM1-v3.1's forecast (time; W at its own affine form at the run's seconds), both arms"),
        "B": ({"model": "v3"}, "every point at MM1-v3's (where it prices no energy, MM1-v3.1's W): v3 closer wherever the predicted gap passes the tie"),
        "C": ({"model": "v31", "scale_t": 1.25}, "MM1-v3.1's time x 1.25, W at its affine form at those seconds: the time rules and E4 fail"),
        "D": ({"model": "v31", "scale_W": 1.25}, "MM1-v3.1's time, W 25% over its given W: the energy rules fail, time passes"),
        "E": ({"model": "v31", "bad_check": first(A, lambda p: p["family"] == "C")}, "case A with one check of C wrong in arm A: R0 FAIL in arm A, labels"),
        "F": ({"model": "v31", "mhz_point": [first(A, lambda p: p["family"] == "R"), first(B, lambda p: p["family"] == "R")], "mhz": 620},
              "case A with one point's runs in each arm at 620 MHz: S6 FAIL in both arms"),
        "G": ({"model": "v31", "bad_mask": first(A, lambda p: p["family"] == "C")}, "case A with one point's runs carrying another mask: set aside, NO DATA"),
        "H": ({"model": "v31", "drop_arm": "B"}, "case A with arm B missing: arm B NO DATA; the pooled rules NO DATA"),
        "I": ({"model": "v31", "only": few}, "case A with only a few points: TOO FEW"),
        "J": ({"alternate": True}, "the cases (time) and points (energy) in sorted order alternate between MM1-v3.1's and MM1-v3's figures"),
        "K": ({"model": "v31", "labels": {"A": {"ran_before_points": [first(A, lambda p: p["family"] == "P")]},
                                          "B": {"ran_before_points": [first(B, lambda p: p["family"] == "P")]}}},
              "case A with one point of each arm labelled 'ran before': it leaves every rule"),
        "L": ({"model": "v31", "watts_add": 0.7}, "case A but every point MM1-v3.1 puts under 3 W reads 0.7 W more (over both watts bands): the post hoc "
                                                  "E1, E2 fail"),
        "M": ({"model": "v31", "watts_add": 0.5}, "case A but those points read 0.5 W more (inside both bands): E1, E2 pass"),
        "N": ({"model": "v31", "walk_bad": first(A, lambda p: p["loop"] == "rgm211 gemmLn")}, "case A with a gemmLn run's walk bad: R0 FAIL in arm A, "
                                                                                              "the point set aside"),
        "O": ({"model": "v31", "smoke_bad": True}, "case A with a session-gate smoke check wrong in both arms: R0 FAIL"),
        "P": ({"model": "v31", "tie_scale": 1.05}, "case A with the ties reading 5% more W over idle than the reference: the day offset +5% (REPORTED)"),
        "Q": ({"model": "v31", "fam_smoke_bad": {"A": fam_a}, "drop_points": fam_pts},
              "arm A's family smoke of 'rgm211 gemmLn' failed and its family dropped (its points never ran): R0 PASS, the drop flagged, NO DATA"),
        "R": ({"model": "v31", "fam_smoke_bad": {"A": fam_a}}, "arm A's family smoke failed while its family's points ran anyway (a kit fault): R0 FAIL"),
        "S": ({"model": "v31", "drop_points": nc}, "the gemmLnc block cut (a board stop at the session's end): its points NO DATA, every rule on the rest"),
        "T": ({"model": "v31", "scale_W_S": 1.30}, "case A but every family-S kind reads 30% more W over idle: the post hoc energy rules fail, the "
                                                   "registered ones pass"),
    }


def selftest_standins(outp):
    frozen = load_frozen()
    P = frozen[1]
    res, ok_all = {}, True
    for day, (how, what) in standins(P).items():
        how = dict(how)
        data = standin_day(frozen, how)
        got = score(data, labels=how.get("labels"), frozen=frozen, quiet=True)
        exp = expected(frozen, how)
        row = {"what": what, "got": {}, "expected": {}, "ok": True}
        for tag in ARMS:
            row["got"][tag], row["expected"][tag] = {}, {}
            for g in GROUPS:
                gv = got["arms"][tag]["verdicts"][g]
                ev = exp[tag][g]
                row["got"][tag][g] = gv
                row["expected"][tag][g] = ev
                for kk, vv in ev.items():
                    if gv.get(kk) != vv:
                        row["ok"] = False
        row["pooled"] = {g: {k: v["verdict"] for k, v in got["pooled"][g].items()} for g in GROUPS}
        row["pooled_expected"] = exp["pooled"]
        if row["pooled"] != row["pooled_expected"]:
            row["ok"] = False
        if day == "P":
            off = got["arms"]["A"]["day_offset_REPORTED"]
            row["offset_W"] = off and round(off["offset_W"], 6)
            if not off or abs(off["offset_W"] - 0.05) > 1e-9:
                row["ok"] = False
        if day == "G" and how["bad_mask"] in got["arms"]["A"]["measured"]:
            row["ok"] = False
        if day == "Q":
            fl = got["arms"]["A"]["flags"]
            row["family_flag"] = [x for x in fl if x.startswith("the family smoke")][:1]
            if not row["family_flag"] or any(i in got["arms"]["A"]["measured"] for i in how["drop_points"]) or got["arms"]["A"]["R0_failures"]:
                row["ok"] = False
        if day == "R" and not any("the family smoke" in x for x in got["arms"]["A"]["R0_failures"]):
            row["ok"] = False
        ok_all &= row["ok"]
        res[day] = row
    rules = frozen[0]
    seen, cover = {}, True
    for tag in ARMS:
        for g in GROUPS:
            for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES:
                vals = sorted({res[d]["got"][tag][g][r] for d in res})
                seen[f"{tag} {g} {r}"] = vals
                n_reg = len(P["arms"][tag]["registered_cases" if g == "registered" else "posthoc_cases"]) if r in TIME_RULES else \
                    rules["arms"][tag]["n_energy_points"][g] if r in ENERGY_RULES else 99
                if n_reg >= 10 and not ("PASS" in vals and "FAIL" in vals):
                    cover = False
                if n_reg < 10 and not set(vals) <= {"TOO FEW", "NO DATA"}:
                    cover = False
    hseen, hcover = {}, True
    for tag in ARMS + ("pooled",):
        for g in GROUPS:
            for k in H2H:
                key = k if tag != "pooled" else "HP" + k[1]
                vals = sorted({(res[d]["got"][tag][g][k] if tag != "pooled" else res[d]["pooled"][g][key]) for d in res})
                pw = rules["power_REPORTED"][g][tag][k]
                hseen[f"{tag} {g} {key} (decidable {pw['decidable_cases']})"] = vals
                if pw["decidable_cases"] >= 10:
                    if not ("MM1-v3.1 BETTER" in vals and "MM1-v3 BETTER" in vals):
                        hcover = False
                elif not set(vals) <= {"TOO FEW", "NO DATA"}:
                    hcover = False
    nd_seen = sorted(k for k, v in hseen.items() if "NOT DECIDED" in v)
    out = {"what": "score_e215 stand-in days: verdicts stated before the run by expected() (written apart from the scorer's code path)",
           "days": res, "every_rule_seen": seen, "cover_pass_fail": cover, "head_to_head_seen": hseen, "cover_h2h": hcover,
           "not_decided_seen_in": nd_seen,
           "coverage_rule": ("every rule of every arm and group with 10 or more cases or points seen PASS and FAIL, one with fewer only TOO FEW / NO "
                             "DATA; every head-to-head with 10 or more decidable cases (predicted gap over the tie) seen MM1-v3.1 BETTER and MM1-v3 "
                             "BETTER, one with fewer only TOO FEW / NO DATA (TOO FEW by construction); NOT DECIDED listed where seen"),
           "verdict": "PASS" if (ok_all and cover and hcover) else "FAIL"}
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True, default=float)
    lines = [f"score_e215 --selftest-standins: {out['verdict']} (every day as stated: {ok_all}; coverage of PASS and FAIL: {cover}; head-to-head "
             f"coverage: {hcover}; NOT DECIDED seen in {len(nd_seen)} rules)"]
    for d, r in res.items():
        lines.append(f"day {d} ({'ok' if r['ok'] else 'NOT AS STATED'}): {r['what']}")
        for tag in ARMS:
            for g in GROUPS:
                lines.append(f"   arm {tag} {g}: " + ", ".join(f"{k} {v}" for k, v in sorted(r["got"][tag][g].items())))
        lines.append(f"   pooled: {r['pooled']}")
    open(outp.replace(".json", ".txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:1]))
    return 0 if out["verdict"] == "PASS" else 1


def selftest_real(outp):
    """E213's committed runs (aifoundry3 card 0, arm A; aifoundry1 card 1, arm B) through this scorer's reader: every point's mean figures against
    MM1-v3.1's own reading of the same runs (tools/matmul/mm1/v3.1/inputs/e213, through data_v31's E213 points: a point a (card, configuration))"""
    sys.path.insert(0, os.path.join(REPO, "tools", "matmul", "mm1", "v3.1"))
    import data_v31 as DV  # noqa: E402
    vend_tp = [p for p in DV.time_points() if p["exp"] == "E213"]
    vend_e = {(e["card"], e["arm"], e["fmt"], e["mask"].lower(), e["kind"]): e for e in DV.energy_points() if e["exp"] == "E213"}
    srcs = {"E213 arm A": ("docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/data-e213.json", "A", "aifoundry3 card 0"),
            "E213 arm B": ("docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/data-e213.json", "B", "aifoundry1 card 1")}
    out = {"what": "the reader on real committed bytes (E213's two arms)", "sets": {}}
    ok_all = True
    for name, (rel, armk, card) in srcs.items():
        d = json.load(open(os.path.join(REPO, rel)))["arms"][armk]
        n, worst, miss, n_time, pooled_cases = 0, {"t": 0.0, "W": 0.0, "cw": 0.0, "cm": 0.0}, [], 0, 0
        for pid, pt in d["points"].items():
            runs = pt["runs"]
            if not runs:
                continue
            rec = runs[0]["record"]
            arm_ = rec["arm"]
            pre = "gemmLnc" if arm_.startswith("gemmLnc") else ("gemmLn" if arm_.startswith("gemmLn") else "gemmL")
            body = arm_[len(pre):]
            if not body.replace("x", "").isdigit() or body.count("x") != 2:
                continue
            MB, NB, KB = (int(x) for x in body.split("x"))
            ops = MB * NB * 2 * KB * 32
            loop = {"gemmLnc": "rgm136 gemmLnc", "gemmLn": "rgm211 gemmLn", "gemmL": "rgm136 gemmL"}[pre]
            host = "rgm211" if pre in ("gemmLnc", "gemmLn") else "rgm136"
            p = {"id": pid, "arm": arm_, "format": rec["type"], "minions": rec["minions"], "shire_mask": rec["shire_mask"], "host": host,
                 "ops_per_minion_per_gemm": ops, "case": pid, "role": "point", "family": "real", "reading": "real", "time_scored": True,
                 "loop": loop, "kind": "?"}
            Pfake = {"arms": {"X": {"points": [p], "references": []}}}
            if host == "rgm211":
                for r in runs:
                    r.setdefault("walk", {"ok": [True], "launches_bad": 0})
                    r.setdefault("gate", "GATE OK: (not in E213's reduced runs; the reader's own gate is not under test here)")
            M, flags, r0, s6 = reduce_arm("X", {"points": {pid: pt}}, Pfake, {})
            if pid not in M:
                miss.append(pid)
                continue
            mask = "0x%x" % int(str(rec["shire_mask"]), 16)
            cands_e = [v for k, v in vend_e.items() if k[0] == card and k[1] == arm_ and k[2] == rec["type"] and "0x%x" % int(k[3], 16) == mask]
            ve = [v for v in cands_e if v.get("w") is not None and abs(v["w"] / M[pid]["W"] - 1) < 1e-6] if M[pid]["W"] else []
            # MM1-v3.1's time point of a case pools the case's points (its 'pids'): compared where it holds this point alone
            vt = next((v for v in vend_tp if v["card"] == card and list(v.get("pids") or []) == [pid]), None)
            pooled_cases += 1 if any(pid in (v.get("pids") or []) and len(v.get("pids") or []) > 1 for v in vend_tp if v["card"] == card) else 0
            if vt is None and not ve:
                miss.append(pid)
                continue
            n += 1
            if ve:
                worst["W"] = max(worst["W"], abs(ve[0]["w"] / M[pid]["W"] - 1))
                if ve[0].get("t_meas"):
                    worst["t"] = max(worst["t"], abs(ve[0]["t_meas"] / M[pid]["t"] - 1))
            if vt is not None:
                n_time += 1
                worst["cw"] = max(worst["cw"], abs(vt["cw"] / M[pid]["cw"] - 1))
                if vt.get("cyc_mean"):
                    worst["cm"] = max(worst["cm"], abs(vt["cyc_mean"] / M[pid]["cm"] - 1))
        good = n > 0 and max(worst.values()) < 1e-6
        ok_all &= good
        out["sets"][name] = {"source": rel, "sha256": sha_rel(rel), "points_compared": n, "time_points_compared": n_time,
                             "points_in_pooled_cases_time_not_compared": pooled_cases, "not_compared": miss[:20],
                             "worst_relative_difference": worst, "equal": good,
                             "how": ("W over idle and the seconds against MM1-v3.1's energy point of the same configuration and kind; the wall cycles and "
                                     "the counter's mean against its time point where the configuration holds one point (MM1-v3.1 pools a case's runs)")}
    out["verdict"] = "PASS" if ok_all else "FAIL"
    json.dump(out, open(outp, "w"), indent=1, sort_keys=True)
    txt = [f"score_e215 --selftest-real: {out['verdict']}"] + [f"  {k}: {v['points_compared']} points, worst relative difference "
                                                                f"{ {kk: float('%.1e' % vv) for kk, vv in v['worst_relative_difference'].items()} } "
                                                                f"(equal {v['equal']}); not compared {v['not_compared']}" for k, v in out["sets"].items()]
    open(outp.replace(".json", ".txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))
    return 0 if ok_all else 1


def forecasts_print():
    rules, P, fc = load_frozen()
    L, worst = [], {m: 0.0 for m in MODELS}
    for tag in ARMS:
        for p in P["arms"][tag]["points"] + P["arms"][tag]["references"]:
            f = fc[tag][p["id"]]
            row = f"{tag} {p['id']} {p['role']:9s} {p['family']:5s} {p['name'][:44]:44s}"
            for mdl in MODELS:
                m = f.get(mdl) or {}
                if m.get("A") is not None and m.get("t") and m.get("W"):
                    Wg, Jg = given(m, m["cw"], m["t"])
                    worst[mdl] = max(worst[mdl], abs(Wg / m["W"] - 1))
                row += (f" | {mdl} {m.get('cw', 0):.1f} " + (f"{m['W']:.3f} W" if m.get("W") is not None else "energy n.f.")) if m else f" | {mdl} -"
            L.append(row)
    head = ("score_e215 --forecasts: the frozen forecasts as the scorer reads them; given() at each model's own seconds reproduces its frozen W to "
            + ", ".join(f"{NAMES[m]} {worst[m]:.1e}" for m in MODELS) + " relative (the CSVs print A and B to 6 decimals)")
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
        open(os.path.join(HERE, "forecasts-e215.txt"), "w").write(head + "\n" + "\n".join(L) + "\n")
        return
    data = json.load(open(a.data))
    labels = json.load(open(a.labels)) if a.labels else {}
    res = score(data, labels)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=float)


if __name__ == "__main__":
    main()
