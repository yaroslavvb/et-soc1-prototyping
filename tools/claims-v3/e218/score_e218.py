#!/usr/bin/env python3
"""E218 (Q230): the frozen scorer of MM1-v3.2's BLIND MATMUL DAY on aifoundry3 card 0 at its pinned 600 MHz, one arm. It reads the kit's reduced
data (E215 arm A's run form and reducer form, below), the frozen forecasts (every declared model's: tools/matmul/mm1/v3.2/out/e218/
forecasts-e218.json, frozen by MM1-v3.2's land 4e386f75; 'MM1-v3.2 without its gemmLnc term' in forecast-e218-reg.json, frozen by this
registration), this folder's rules and points, and refuses to run (exit 4) if any of those files' bytes changed. Standard library only.

    python3 -I -B tools/claims-v3/e218/score_e218.py DATA.json [--labels LABELS.json] [--out SCORED.json]
    python3 -I -B tools/claims-v3/e218/score_e218.py --selftest-standins OUT.json   stand-in days whose verdicts are stated before the run (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e218/score_e218.py --selftest-real OUT.json       E215 arm A's committed runs on this card through this reader
    python3 -I -B tools/claims-v3/e218/score_e218.py --forecasts                    every point's forecasts and the given() self-check; writes nothing

THE DATA (one JSON; E215's and E213's reducer form): {"experiment": "E218", "arms": {"A": ARM}}; the arm missing or empty is NO DATA.
  ARM = {"smoke": {"runs": [RUN, ...]}, "points": {pid: {"runs": [RUN, ...]}}, "ties": {"runs": [RUN, ...]}}
  RUN = {"t_gemm_s" (seconds a GEMM over the run's counted launches), "cycles_per_op" (the counter's mean over minions / ops, the launches'
         median), "cycles_gemm" (the slowest minion's counter a GEMM, the launches' median), "p_work_w", "p_rest_w" (board W medians: inside the
         counted launches; the last 5 s of the run's rest), "die_start_c", "mhz_min", "mhz_max" (the counted samples' minion clock), "checks"
         (every check of C of the run: "exact" / "approx" / "wrong"), "record": {"arm", "type", "minions", "shire_mask"} as the host prints them,
         "block", "n", and for a process of rgm211's host (family G's gemmLnc and its smoke s03): "walk": {"ok": [...], "launches_bad"} and "gate"
         (the identity gate's words); a smoke RUN carries "point" (its smoke id)}
MEASURED, per run: the wall cycles an op = cycles_gemm / ops a minion a GEMM; the counter's mean = cycles_per_op; seconds = t_gemm_s; W over idle =
  p_work - p_rest; J over idle = W t_gemm; J with the card at rest = p_work t_gemm. A run whose record differs from its point (arm, type, minions,
  or the shire mask read as a number), or whose rgm211-host walk or gate is not good, is SET ASIDE and flagged. A POINT is the mean of its kept
  runs; every E218 point is its own CASE (its kernel loop, arm token, format and mask are unique).
THE RULES (E218.md section 7; numbers from rules-e218.json; one group: every registered point, families G, Gt, Y, F):
  R0 every check of C exact or approx (smoke, points, ties); the smoke's counter mean 200-4,000 cycles an op; every rgm211-host process's walk
      good and its gate GATE OK. Family G's smoke s03 failing while NO G point has a run (the family dropped by its own stop path) is not an
      R0 failure: flagged and REPORTED, the G points NO DATA (E213's Amendment A1 form). A FAIL labels every other verdict.
  S6 every kept run's counted samples at 590-610 MHz. A FAIL labels every other verdict.
  MM1-v3.2 PER CASE: T1 the wall cycles, T2 the counter's mean, T3 seconds: |measured / MM1-v3.2 - 1| <= the band.
  MM1-v3.2 PER POINT: E1 J over idle given the measured op time (MM1-v3.2's W = A + B / t_op at t_op = the measured wall cycles an op / 600 MHz in
      us, times the measured seconds); E2 J over idle with the seconds forecast (its frozen J); E3 J at rest given t (the measured rest x t + E1's
      J); E4 J at rest with the seconds forecast (the measured rest x MM1-v3.2's seconds + its frozen J); at a WATTS POINT (MM1-v3.2's frozen W or
      the measured W under 3 W) E1 and E2 read |W measured - W forecast| <= band_w.
  A rule's verdict: PASS if at least 90% of its scored cases or points pass; FAIL otherwise; TOO FEW under 10; NO DATA with none.
  HEAD TO HEAD (rules-e218.json > head_to_head; first against second): H1-H5 MM1-v3.2 against MM1-v3 (wall, the counter's mean, seconds per
      case; J over idle given t, J over idle with t forecast per point) and H6-H10 against MM1-v3.1, over every registered point; HG1, HG2
      MM1-v3.2 against 'MM1-v3.2 without its gemmLnc term' on family G (given t; with t forecast); HG3, HG4 against 'v3.1 + gemmLnc term' on G;
      HY1 MM1-v3.2 against 'MM1-v3.2 without its layout term' on Y (the same model: a tie at every case by construction); HY2 against 'v3.1 +
      contention' on Y (wall). d = |ln(measured / second)| - |ln(measured / first)| (in watts of W at a watts point); first closer where d > the
      tie, second where d < -tie; the exact two-sided sign test at 0.05 on the decided: '<first> BETTER' / '<second> BETTER' / NOT DECIDED;
      TOO FEW under the rule's minimum decided (10; 8 for family G's tests); NO DATA with none.
  THE PAIR RULE P1 (MM1-v3.2's claim on Y: no within-pair difference): over the complete Y pairs with data, a pair SEPARATED when |ln(wall_a /
      wall_b)| > theta; PASS with at least 5 pairs and at most one separated; FAIL with at least 5 and two or more separated; TOO FEW under 5.
  LABELS (--labels): {"A": {"ran_before_points": [...]}}: those points leave every rule (the card lane's step 6n); a label naming no point is
      refused (exit 10); the output names every label applied.
REPORTED (never verdicts): every other model's cells at MM1-v3.2's bands and every model's rms and bias by family (MM1-v3.1, MM1-v3, MM1-v2, the
  two '+ term' forms, 'v3.1 + both terms', 'v3.1 with T7', MM1-v3 refitted, verify-lay's five controls in time); P1 in E216's form for each frozen
  layout candidate; the G / Gt pairs (the gemmLnc excess measured against each model's); the bootstrap 95% interval of each head-to-head's mean d;
  the day offset of the tie t01 against E215 arm A's.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
D = "tools/claims-v3/e218/"
LANDJ = "tools/matmul/mm1/v3.2/out/e218/forecasts-e218.json"
PINS = {
    LANDJ: "1236dd9953b853a59293fc00377ff451b85756319cc80934c60208a7334d6209",
    "tools/matmul/mm1/v3.2/out/e218/forecasts-e218.csv": "52e78762af1f833cd778b54ff89210ed49bcc39af49ccca1ca65a500a94d018a",
    "tools/matmul/mm1/v3.2/out/e218/points-e218.csv": "1771826ee5a05327a2516b51345f9f0ef198c029b072e3d587e3d490cac54936",
    D + "forecast-e218-reg.json": "0a8a7d5764b2b4a06ad07c47613009fa27f88b381a784fa3982d0cf6bc8632df", D + "rules-e218.json": "b8037cd69374f25a792924356cd4558680774daea1bea79f43e3832b98b11ba8", D + "points-e218.json": "9a5f252f58a25db0b3fe0e78fdc699e597c607442e8090b85e8c795e5da606b3",
}
FAMS = ("G", "Gt", "Y", "F")
TIME_RULES = ("T1", "T2", "T3")
ENERGY_RULES = ("E1", "E2", "E3", "E4")
LANDED_KEY = {"v32": "MM1-v3.2", "v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "lnc31": "v3.1 + gemmLnc term", "cont": "v3.1 + contention",
              "t7": "REPORTED v3.1 with T7", "both": "REPORTED v3.1 + both terms", "v3r": "REPORTED MM1-v3 refitted"}
NAMES = {"v32": "MM1-v3.2", "v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "nolnc": "MM1-v3.2 without its gemmLnc term",
         "nolay": "MM1-v3.2 without its layout term", "lnc31": "v3.1 + gemmLnc term", "cont": "v3.1 + contention", "t7": "v3.1 with T7",
         "both": "v3.1 + both terms", "v3r": "MM1-v3 refitted"}
KEY_OF = {v: k for k, v in NAMES.items()}
CONTROLS = ("N3", "N1+N2", "G1", "G1+N1", "fresh24")
OTHERS = ("v31", "v3", "v2", "nolnc", "lnc31", "cont", "t7", "both", "v3r")
LOW = 3.0
SESSION_SMOKE = ("s01",)
QKEY = {"wall": "cw", "mean": "cm", "seconds": "t"}


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


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
                print(f"score_e218: REFUSED, {rel} is {got}, pinned {want}")
                sys.exit(4)
    rules = json.load(open(os.path.join(REPO, D + "rules-e218.json")))
    P = json.load(open(os.path.join(REPO, D + "points-e218.json")))
    L = json.load(open(os.path.join(REPO, LANDJ)))["forecasts"]
    G = json.load(open(os.path.join(REPO, D + "forecast-e218-reg.json")))

    def fp(x):
        x = x or {}
        return {"cw": x.get("cycles_per_op_wall"), "cm": x.get("cycles_per_op_mean"), "t": x.get("seconds_per_gemm"), "W": x.get("W_over_idle"),
                "A": x.get("A_W"), "B": x.get("B_W_us"), "J": x.get("J_over_idle_per_gemm"), "F3": x.get("F3_W_at_own_t")}
    fc = {}
    for p in P["points"]:
        o = {k: fp(L[p["id"]].get(lk)) for k, lk in LANDED_KEY.items()}
        o["nolnc"] = fp(G["nolnc"][p["id"]])
        o["nolay"] = dict(o["v32"])
        for c in CONTROLS:
            x = (L[p["id"]].get("verify-lay controls") or {}).get(c) or {}
            o["ctl " + c] = {"cw": x.get("cycles_per_op_wall"), "t": x.get("seconds_per_gemm")}
        fc[p["id"]] = o
    return rules, P, fc, G


def given(m, cw, t_gemm):
    """a model's W over idle at the measured op time by its frozen affine form, and its J over idle given t: t_op = the measured wall cycles an
    op / 600 MHz (the slowest minion's counter time, MM1-v3.2's fit footing for this run form); J = W x the measured seconds"""
    if m is None or m.get("A") is None or m.get("B") is None or not cw:
        return None, None
    W = m["A"] + m["B"] / (cw / 600.0)
    return W, W * t_gemm


# ------------------------------------------------------------------ the measured side
def reduce_arm(arm, P, labels):
    pts = {p["id"]: p for p in P["points"]}
    out, flags, r0, s6 = {}, [], [], []

    def run_ok(r, p):
        rec = r.get("record") or {}
        try:
            same = (rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == p["minions"]
                    and int(str(rec.get("shire_mask")), 16) == int(p["shire_mask"], 16))
        except (TypeError, ValueError):
            same = False
        good = True
        if p["host"] == "rgm211":
            w = r.get("walk") or {}
            good = bool(w.get("ok")) and all(w.get("ok")) and w.get("launches_bad") == 0 and str(r.get("gate", "")).startswith("GATE OK")
        return same, good

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
            same, good = run_ok(r, p)
            if p["host"] == "rgm211" and not good:
                r0.append(f"{pid} run {r.get('n')}: walk or gate not good")
            if not same:
                flags.append(f"{pid} run {r.get('n')}: SET ASIDE (record {r.get('record')})")
                continue
            if not good:
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
        en = [r for r in kept if r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
        out[pid] = {"n_runs": len(kept), "cw": mean([r["cycles_gemm"] / ops for r in kept]), "cm": mean([r["cycles_per_op"] for r in kept]),
                    "t": mean([r["t_gemm_s"] for r in kept]), "W": mean([r["p_work_w"] - r["p_rest_w"] for r in en]) if en else None,
                    "J": mean([(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in en]) if en else None,
                    "Jrest": mean([r["p_work_w"] * r["t_gemm_s"] for r in en]) if en else None,
                    "prest": mean([r["p_rest_w"] for r in en]) if en else None, "die": mean([r.get("die_start_c") for r in kept]),
                    "family": p["family"], "role": "point", "arm": p["arm"], "mask": p["shire_mask"], "format": p["format"], "ops": ops}
    g_fail = []
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
        if r.get("block") == "smoke" and r.get("point") == "s03":
            g_fail.extend(f"s03 ({x})" for x in why)
        else:
            r0.extend(why)
    if g_fail:
        ran = sorted(pid for pid in out if out[pid]["family"] == "G")
        if ran:
            r0.extend(g_fail + [f"family G's smoke s03 failed, yet {ran} ran: counted in R0 (a family that ran past its failed smoke)"])
        else:
            flags.append(f"family G's smoke s03 failed ({'; '.join(g_fail)}): the family was dropped, its points NO DATA; not an R0 failure "
                         "(E213's Amendment A1 form), REPORTED")
    for pid in labels.get("ran_before_points", []):
        if pid in out:
            out[pid]["role"] = "ran before"
    return out, flags, r0, s6


def verdict_frac(cells, minimum=10):
    n = len(cells)
    if n == 0:
        return "NO DATA"
    if n < minimum:
        return "TOO FEW"
    k = sum(1 for c in cells if c["pass"])
    return "PASS" if k >= math.ceil(0.9 * n - 1e-9) else "FAIL"


def cells_for(M, fc, rules, mdl="v32"):
    """a model's per-case (time) and per-point (energy) cells at MM1-v3.2's bands"""
    band = {q: rules["bands"][q]["band"] for q in TIME_RULES + ENERGY_RULES}
    bw = rules["band_w"]["band_W"]
    cells = {q: [] for q in TIME_RULES + ENERGY_RULES}
    for pid, v in sorted(M.items()):
        if v["role"] != "point":
            continue
        F = fc[pid].get(mdl) or {}
        for q, key in (("T1", "cw"), ("T2", "cm"), ("T3", "t")):
            if F.get(key) and v.get(key):
                e = v[key] / F[key] - 1
                cells[q].append({"case": pid, "measured": v[key], "forecast": F[key], "err": e, "pass": abs(e) <= band[q]})
        if v["W"] is None or F.get("W") is None or F.get("A") is None:
            continue
        watts = fc[pid]["v32"]["W"] < LOW or v["W"] < LOW
        Wg, Jg = given(F, v["cw"], v["t"])
        e1 = abs(v["W"] - Wg) if watts else v["J"] / Jg - 1
        cells["E1"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "forecast": Wg if watts else Jg, "err": e1,
                            "pass": (e1 <= bw) if watts else abs(e1) <= band["E1"]})
        e2 = abs(v["W"] - F["W"]) if watts else v["J"] / F["J"] - 1
        cells["E2"].append({"point": pid, "watts": watts, "measured": v["W"] if watts else v["J"], "forecast": F["W"] if watts else F["J"], "err": e2,
                            "pass": (e2 <= bw) if watts else abs(e2) <= band["E2"]})
        e3 = v["Jrest"] / (v["prest"] * v["t"] + Jg) - 1
        cells["E3"].append({"point": pid, "measured": v["Jrest"], "forecast": v["prest"] * v["t"] + Jg, "err": e3, "pass": abs(e3) <= band["E3"]})
        e4 = v["Jrest"] / (v["prest"] * F["t"] + F["J"]) - 1
        cells["E4"].append({"point": pid, "measured": v["Jrest"], "forecast": v["prest"] * F["t"] + F["J"], "err": e4, "pass": abs(e4) <= band["E4"]})
    return cells


def h_cells(M, fc, rules, x, y, q, fams):
    ties = rules["ties"]
    out = []
    for pid, v in sorted(M.items()):
        if v["role"] != "point" or v["family"] not in fams:
            continue
        fx, fy = fc[pid].get(x) or {}, fc[pid].get(y) or {}
        if q in QKEY:
            k = QKEY[q]
            if fx.get(k) and fy.get(k) and v.get(k):
                tk = "seconds_ln" if q == "seconds" else "cycles_ln"
                out.append({"id": pid, "d": abs(math.log(v[k] / fy[k])) - abs(math.log(v[k] / fx[k])), "tie": ties[tk], "watts": False,
                            "family": v["family"]})
            continue
        if v["W"] is None or fx.get("W") is None or fy.get("W") is None:
            continue
        watts = fc[pid]["v32"]["W"] < LOW or v["W"] < LOW
        if q == "Wg":
            Wx, Jx = given(fx, v["cw"], v["t"])
            Wy, Jy = given(fy, v["cw"], v["t"])
            if Wx is None or Wy is None:
                continue
            d = (abs(v["W"] - Wy) - abs(v["W"] - Wx)) if watts else abs(math.log(v["J"] / Jy)) - abs(math.log(v["J"] / Jx))
        else:
            d = (abs(v["W"] - fy["W"]) - abs(v["W"] - fx["W"])) if watts else abs(math.log(v["J"] / fy["J"])) - abs(math.log(v["J"] / fx["J"]))
        out.append({"id": pid, "d": d, "tie": ties["watts_W"] if watts else ties["joules_ln"], "watts": watts, "family": v["family"]})
    return out


def decide(hc, first, second, minimum):
    npos = sum(1 for c in hc if c["d"] > c["tie"])
    nneg = sum(1 for c in hc if c["d"] < -c["tie"])
    n = len(hc)
    if n == 0:
        return {"verdict": "NO DATA", "n": 0}
    if npos + nneg < minimum:
        return {"verdict": "TOO FEW", "n": n, "first_closer": npos, "second_closer": nneg, "ties": n - npos - nneg}
    p = sign_p(npos, nneg)
    v = (f"{first} BETTER" if npos > nneg else f"{second} BETTER") if p < 0.05 else "NOT DECIDED"
    return {"verdict": v, "n": n, "first_closer": npos, "second_closer": nneg, "ties": n - npos - nneg, "p_two_sided": p}


def boot(hc, seed):
    d = [c["d"] for c in hc if not c["watts"]]
    if len(d) < 2:
        return None
    rnd = random.Random(seed)
    n = len(d)
    ms = sorted(sum(d[rnd.randrange(n)] for _ in range(n)) / n for _ in range(10000))
    return {"mean_d": sum(d) / n, "ci95": [ms[249], ms[9749]], "n": n, "REPORTED": True}


def p1(M, P, rules, pred_of=None):
    """THE PAIR RULE: registered for MM1-v3.2 (pred_of None); E216's ordering form for a candidate (pred_of: pair -> predicted ln(a / b)), REPORTED"""
    R = rules["pair_rule"]["P1"]
    theta = R["theta_ln"]
    rows = []
    for pid, ids in sorted(P["pairs"].items()):
        if len(ids) != 2:
            continue
        a, b = sorted(ids)
        if a in M and b in M and M[a]["role"] == "point" and M[b]["role"] == "point" and M[a]["cw"] and M[b]["cw"]:
            m = math.log(M[a]["cw"] / M[b]["cw"])
            rows.append({"pair": pid, "points": [a, b], "measured_ln_a_over_b": m, "separated": abs(m) > theta})
    n = len(rows)
    if pred_of is None:
        sep = sum(1 for r in rows if r["separated"])
        if n == 0:
            v = "NO DATA"
        elif n < R["min_pairs"]:
            v = "TOO FEW"
        else:
            v = "PASS" if sep <= R["max_separated_for_PASS"] else "FAIL"
        return {"verdict": v, "pairs_with_data": n, "separated": sep, "theta_ln": theta, "rows": rows}
    dec = [r for r in rows if r["separated"]]
    for r in rows:
        s = pred_of.get(r["pair"])
        r["predicted_ln_a_over_b"] = s
        r["ordered_right"] = bool(r["separated"] and s and (r["measured_ln_a_over_b"] > 0) == (s > 0))
    k = sum(1 for r in dec if r["ordered_right"])
    if not rows:
        v = "NO DATA"
    elif len(dec) < 5:
        v = "TOO FEW"
    else:
        pval = sum(math.comb(len(dec), i) for i in range(k, len(dec) + 1)) / 2 ** len(dec)
        v = "PASS" if (k > len(dec) / 2 and pval <= 0.05) else "FAIL"
    return {"verdict": v, "pairs_with_data": n, "decided": len(dec), "ordered_right": k, "theta_ln": theta, "rows": rows, "REPORTED": True}


def model_stats(M, fc):
    out = {}
    fams = {}
    for pid, v in M.items():
        if v["role"] == "point":
            fams.setdefault(v["family"], []).append(pid)
    fams["all"] = [pid for pid, v in M.items() if v["role"] == "point"]
    for fam, ids in sorted(fams.items()):
        row = {}
        for mdl in ("v32",) + OTHERS + tuple("ctl " + c for c in CONTROLS):
            cw = [math.log(M[i]["cw"] / fc[i][mdl]["cw"]) for i in ids if (fc[i].get(mdl) or {}).get("cw")]
            J = [math.log(M[i]["J"] / fc[i][mdl]["J"]) for i in ids if (fc[i].get(mdl) or {}).get("J") and M[i].get("J")
                 and (M[i]["W"] or 0) >= LOW and (fc[i][mdl].get("W") or 0) >= LOW]
            Ww = [M[i]["W"] - fc[i][mdl]["W"] for i in ids if (fc[i].get(mdl) or {}).get("W") is not None and M[i].get("W") is not None
                  and ((M[i]["W"] or 0) < LOW or (fc[i][mdl].get("W") or 0) < LOW)]
            row[NAMES.get(mdl, mdl)] = {
                "wall_cycles": {"n": len(cw), "rms_pct": round(100 * rms(cw), 3), "bias_pct": round(100 * sum(cw) / len(cw), 3)} if cw else None,
                "J_over_idle_3W_and_above": {"n": len(J), "rms_pct": round(100 * rms(J), 3), "bias_pct": round(100 * sum(J) / len(J), 3)} if J else None,
                "W_watts_points": {"n": len(Ww), "rms_W": round(rms(Ww), 4), "bias_W": round(sum(Ww) / len(Ww), 4)} if Ww else None}
        out[fam] = row
    return out


def g_pairs(M, fc, P):
    """REPORTED: the gemmLnc excess, each G point's W over idle over its cooperative twin's, measured beside each model's"""
    out = []
    for g, t in sorted(P["twins"].items()):
        if g in M and t in M and M[g]["W"] and M[t]["W"]:
            out.append({"G": g, "twin": t, "measured_W_ratio": M[g]["W"] / M[t]["W"], "measured_cw_ratio": M[g]["cw"] / M[t]["cw"],
                        "models_W_ratio": {NAMES[m]: (fc[g][m]["W"] / fc[t][m]["W"]) if (fc[g][m].get("W") and fc[t][m].get("W")) else None
                                           for m in ("v32", "nolnc", "v31", "lnc31", "v3", "v2")}})
    return out


FLOOR = {"fp32": 529.0, "fp16": 529.0, "int8": 270.0}


def timing(M):
    """REPORTED, his question (E215's reading): the measured cycles an op against the resident tensor op's floor (E215's FLOOR: the measured TenB
    floor a format, cycles an op), the counter's mean and the wall"""
    return {pid: {"counter_mean_over_floor": v["cm"] / FLOOR[v["format"]], "wall_over_floor": v["cw"] / FLOOR[v["format"]]}
            for pid, v in sorted(M.items()) if v.get("cm") and v.get("cw")}


def day_offset(arm, rules):
    ref = rules.get("pair_rule", {}).get("t01_between_days_REPORTED", {}).get("t01_wall_cycles_by_day", {})
    runs = [r for r in (arm.get("ties") or {}).get("runs", []) if r.get("cycles_gemm")]
    if not runs or not ref:
        return None
    cw = mean([r["cycles_gemm"] / 2048 for r in runs])
    return {"n_runs": len(runs), "t01_wall_cycles": cw, "against": {k: cw / v - 1 for k, v in ref.items()}, "REPORTED": True}


def score(data, labels=None, frozen=None):
    rules, P, fc, G = frozen or load_frozen()
    labels = labels or {}
    lab = labels.get("A", {})
    ids = {p["id"] for p in P["points"]}
    bad = [x for x in lab.get("ran_before_points", []) if x not in ids]
    if bad:
        print(f"score_e218: REFUSED (exit 10), labels naming no point: {bad}")
        sys.exit(10)
    res = {"experiment": "E218", "labels_applied": labels, "group": "registered: every point of families G, Gt, Y, F as registered"}
    arm = (data.get("arms") or {}).get("A") or {}
    hids = list(rules["head_to_head"].keys())
    if not arm or not arm.get("points"):
        res["verdicts"] = {r: "NO DATA" for r in ("R0", "S6") + TIME_RULES + ENERGY_RULES + tuple(hids) + ("P1",)}
        res["note"] = "the arm is missing or empty: NO DATA"
        return res
    M, flags, r0, s6 = reduce_arm(arm, P, lab)
    cells = cells_for(M, fc, rules, "v32")
    v = {"R0": "FAIL" if r0 else "PASS", "S6": "FAIL" if s6 else "PASS"}
    for q in TIME_RULES + ENERGY_RULES:
        v[q] = verdict_frac(cells[q])
    hres = {}
    for hid, h in rules["head_to_head"].items():
        x, y = KEY_OF[h["first"]], KEY_OF[h["second"]]
        hc = h_cells(M, fc, rules, x, y, h["quantity"], tuple(h["families"]))
        dd = decide(hc, h["first"], h["second"], h["minimum_decided"])
        dd.update({"first": h["first"], "second": h["second"], "quantity": h["quantity"], "families": h["families"], "cells": hc,
                   "bootstrap_REPORTED": boot(hc, f"E218|bootstrap|{hid}")})
        hres[hid] = dd
        v[hid] = dd["verdict"]
    pr = p1(M, P, rules)
    v["P1"] = pr["verdict"]
    if r0 or s6:
        v = {k: (val if k in ("R0", "S6") else f"{val} (labelled: {'R0' if r0 else ''}{' ' if r0 and s6 else ''}{'S6' if s6 else ''} FAIL)")
             for k, val in v.items()}
    cand = {}
    tab = rules["pair_rule"]["pairs"]
    for name in ("v3.1 + contention", "v3.1 with T7") + CONTROLS:
        key = name if name in ("v3.1 + contention", "v3.1 with T7") else "ctl " + name
        pred = {pid: (row.get("pred_ln_a_over_b") or {}).get(key) for pid, row in tab.items() if row.get("complete")}
        cand[name] = p1(M, P, rules, pred_of=pred)
    others = {}
    for mdl in OTHERS:
        oc = cells_for(M, fc, rules, mdl)
        others[NAMES[mdl]] = {q: {"verdict_REPORTED": verdict_frac(oc[q]), "n": len(oc[q]), "pass": sum(1 for c in oc[q] if c["pass"])}
                              for q in TIME_RULES + ENERGY_RULES}
    res.update({"verdicts": v, "flags": flags, "R0_failures": r0, "S6_failures": s6, "cells": cells, "head_to_head": hres, "P1": pr,
                "P1_candidates_REPORTED": cand, "others_at_v32_bands_REPORTED": others, "model_stats_REPORTED": model_stats(M, fc),
                "G_twin_pairs_REPORTED": g_pairs(M, fc, P), "day_offset_REPORTED": day_offset(arm, rules), "timing_REPORTED": timing(M),
                "measured": {pid: {k: v2 for k, v2 in m.items()} for pid, m in M.items()}})
    return res


# ------------------------------------------------------------------ self-tests
def run_of(p, cw, cm, t, W, rest=24.7, n=0, block="pass1", mhz=600, check="approx"):
    r = {"t_gemm_s": t, "cycles_per_op": cm, "cycles_gemm": cw * p["ops_per_minion_per_gemm"], "p_work_w": rest + W, "p_rest_w": rest,
         "die_start_c": 50.0, "mhz_min": mhz, "mhz_max": mhz, "checks": [check],
         "record": {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]}, "block": block, "n": n}
    if p["host"] == "rgm211":
        r["walk"] = {"ok": [True, True], "launches_bad": 0}
        r["gate"] = "GATE OK: stand-in"
    return r


def standin_day(P, fc, vals):
    """every point measured twice at vals(p, fc[p]) = (wall cycles, counter mean, seconds, W over idle); the smoke and tie good"""
    arm = {"points": {}, "smoke": {"runs": []}, "ties": {"runs": []}}
    for i, p in enumerate(P["points"]):
        cw, cm, t, W = vals(p, fc[p["id"]])
        arm["points"][p["id"]] = {"runs": [run_of(p, cw, cm, t, W, n=2 * i), run_of(p, cw, cm, t, W, n=2 * i + 1, block="pass2")]}
    for s in P["smoke"]:
        r = run_of(s, 900.0, 820.0, 1e-3, 20.0, block="smoke")
        r["point"] = s["id"]
        arm["smoke"]["runs"].append(r)
    t = P["tie"]
    for k in range(3):
        arm["ties"]["runs"].append(run_of(t, 1100.0, 950.0, 2e-3, 20.0, block="tie", n=900 + k))
    return {"experiment": "E218", "arms": {"A": arm}}


def own(m):
    """a day at forecaster m's own frozen values (its cycles, counter mean, seconds and W over idle at its own seconds)"""
    def f(p, F):
        x = F[m]
        return x["cw"], (x["cm"] or x["cw"] / 1.2), x["t"], x["W"]
    return f


def given_t(m):
    """a day at MM1-v3.2's op time and seconds, and forecaster m's W over idle at that op time (its affine form): the given-t tests' footing"""
    def f(p, F):
        a, x = F["v32"], F[m]
        return a["cw"], a["cm"], a["t"], x["A"] + x["B"] / (a["cw"] / 600.0)
    return f


def selftest_standins(out_path):
    frozen = load_frozen()
    rules, P, fc, G = frozen
    H = rules["head_to_head"]
    tooconst = {hid for hid, h in H.items() if "verdict_by_construction" in h["power_REPORTED"]}

    def want(m, quantities):
        """on a day whose truth is forecaster m: every decidable head-to-head of the given quantities that m is a side of reads m BETTER"""
        w = {}
        for hid, h in H.items():
            if h["quantity"] not in quantities:
                continue
            if hid in tooconst:
                w[hid] = "TOO FEW"
            elif NAMES[m] in (h["first"], h["second"]):
                w[hid] = f"{NAMES[m]} BETTER"
        return w

    def scale(fa, ft):
        def f(p, F):
            x = F["v32"]
            cw, cm, t = x["cw"] * ft, x["cm"] * ft, x["t"] * ft
            W = (x["A"] + x["B"] / (cw / 600.0)) * fa
            return cw, cm, t, W
        return f

    def sep(p, F):
        x = F["v32"]
        k = 1.03 if (p["family"] == "Y" and p["id"].endswith("a")) else 1.0
        return x["cw"] * k, x["cm"] * k, x["t"] * k, x["A"] + x["B"] / (x["cw"] * k / 600.0)

    ALL_T = ("wall", "mean", "seconds", "Jf")
    days = [("v32", "every point at MM1-v3.2's frozen forecasts", own("v32"),
             dict({"R0": "PASS", "S6": "PASS", "T1": "PASS", "T2": "PASS", "T3": "PASS", "E1": "PASS", "E2": "PASS", "E3": "PASS", "E4": "PASS",
                   "P1": "PASS"}, **want("v32", ALL_T + ("Wg",))))]
    for m in ("v3", "v31", "nolnc", "lnc31", "cont"):
        days.append((m + " own", f"every point at {NAMES[m]}'s own frozen values", own(m),
                     dict({"R0": "PASS", "S6": "PASS"}, **want(m, ALL_T), **({"P1": "FAIL"} if m == "cont" else {}))))
        if m != "cont":
            days.append((m + " given t", f"MM1-v3.2's op time and seconds, {NAMES[m]}'s W over idle at that op time", given_t(m),
                         dict({"R0": "PASS"}, **want(m, ("Wg",)))))
    days += [("t125", "MM1-v3.2's cycles, counter mean and seconds x 1.25 (W over idle by its affine form at that op time)", scale(1.0, 1.25),
              {"T1": "FAIL", "T2": "FAIL", "T3": "FAIL", "E1": "PASS", "E3": "PASS", "E4": "FAIL", "P1": "PASS"}),
             ("w125", "MM1-v3.2's values, W over idle x 1.25", scale(1.25, 1.0),
              {"T1": "PASS", "T2": "PASS", "T3": "PASS", "E1": "FAIL", "E2": "FAIL", "E3": "FAIL", "E4": "FAIL"}),
             ("pairs_sep", "MM1-v3.2's values with each Y pair's first point 3% slower", sep, {"P1": "FAIL", "R0": "PASS"})]
    rep = {"what": "E218's scorer on stand-in days; every verdict's want stated before the run", "days": [], "pass": True}
    for name, what, vals, wnt in days:
        got = score(standin_day(P, fc, vals), frozen=frozen)["verdicts"]
        rows = {k: {"got": got.get(k), "want": w, "ok": got.get(k) == w} for k, w in wnt.items()}
        ok = all(r["ok"] for r in rows.values())
        rep["days"].append({"day": name, "truth": what, "ok": ok, "verdicts": rows})
        rep["pass"] &= ok
    d = standin_day(P, fc, own("v32"))
    d["arms"]["A"]["points"][P["points"][0]["id"]]["runs"][0]["checks"] = ["wrong"]
    got = score(d, frozen=frozen)["verdicts"]
    rep["days"].append({"day": "badcheck", "truth": "one run's check of C wrong", "ok": got["R0"] == "FAIL",
                        "verdicts": {"R0": {"got": got["R0"], "want": "FAIL", "ok": got["R0"] == "FAIL"}}})
    rep["pass"] &= got["R0"] == "FAIL"
    d = standin_day(P, fc, own("v32"))
    r = d["arms"]["A"]["points"][P["points"][1]["id"]]["runs"][0]
    r["mhz_min"] = r["mhz_max"] = 700
    got = score(d, frozen=frozen)["verdicts"]
    rep["days"].append({"day": "clock", "truth": "one run at 700 MHz", "ok": got["S6"] == "FAIL",
                        "verdicts": {"S6": {"got": got["S6"], "want": "FAIL", "ok": got["S6"] == "FAIL"}}})
    rep["pass"] &= got["S6"] == "FAIL"
    d = standin_day(P, fc, own("v32"))
    for pid in [p["id"] for p in P["points"] if p["family"] == "G"]:
        d["arms"]["A"]["points"].pop(pid)
    for r in d["arms"]["A"]["smoke"]["runs"]:
        if r.get("point") == "s03":
            r["checks"] = ["wrong"]
    sc = score(d, frozen=frozen)
    got = sc["verdicts"]
    wnt = {"R0": "PASS", "HG1": "NO DATA", "HG2": "NO DATA", "HG3": "NO DATA", "HG4": "NO DATA"}
    rows = {k: {"got": got[k], "want": w, "ok": got[k] == w} for k, w in wnt.items()}
    ok = all(r["ok"] for r in rows.values()) and any("family G's smoke s03 failed" in f for f in sc["flags"])
    rep["days"].append({"day": "g_smoke_dropped", "truth": "family G's smoke fails and no G point runs", "ok": ok, "verdicts": rows})
    rep["pass"] &= ok
    got = score({"experiment": "E218", "arms": {}}, frozen=frozen)["verdicts"]
    rows = {k: {"got": x, "want": "NO DATA", "ok": x == "NO DATA"} for k, x in got.items()}
    ok = all(r["ok"] for r in rows.values())
    rep["days"].append({"day": "nodata", "truth": "no data", "ok": ok, "verdicts": rows})
    rep["pass"] &= ok
    seen = {}
    for dd in rep["days"]:
        for k, r in dd["verdicts"].items():
            seen.setdefault(k, set()).add(r["got"])
    rep["verdicts_seen_by_rule"] = {k: sorted(s) for k, s in sorted(seen.items())}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    lines = [f"score_e218 --selftest-standins: {'PASS' if rep['pass'] else 'FAIL'}"]
    for dd in rep["days"]:
        lines.append(f"  {dd['day']:16s} {'ok' if dd['ok'] else 'NOT OK'}: " + "; ".join(
            f"{k} {r['got']}" + ("" if r["ok"] else f" (want {r['want']})") for k, r in dd["verdicts"].items()))
    lines.append("  verdicts seen by rule: " + "; ".join(f"{k} {v}" for k, v in rep["verdicts_seen_by_rule"].items()))
    print("\n".join(lines))
    return 0 if rep["pass"] else 1


def selftest_real(out_path):
    """E215 arm A's committed runs (this card, this run form) through this reader: E215's points stand in for E218's, with E218's record check"""
    frozen = load_frozen()
    rel = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/data-e215.json"
    p215 = json.load(open(os.path.join(REPO, "tools/claims-v3/e215/points-e215.json")))["arms"]["A"]
    d = json.load(open(os.path.join(REPO, rel)))
    arm = d["arms"]["A"]
    P = {"points": [], "pairs": {}, "twins": {}, "smoke": [], "tie": None}
    fam = {"P": "F", "C": "F", "R": "F", "L": "Y", "S": "F"}
    for q in p215["points"] + p215.get("references", []):
        P["points"].append({"id": q["id"], "family": fam.get(q["family"], "F"), "arm": q["arm"], "format": q["format"], "minions": q["minions"],
                            "shire_mask": q["shire_mask"], "host": q["host"], "ops_per_minion_per_gemm": q["ops_per_minion_per_gemm"]})
    M, flags, r0, s6 = reduce_arm(arm, P, {})
    n_runs = sum(len(p["runs"]) for p in arm["points"].values())
    rep = {"what": "E215 arm A's committed reducer output on aifoundry3 card 0 through score_e218.reduce_arm (E215's points standing in)",
           "source": rel, "source_sha256": sha_rel(rel), "runs": n_runs, "points_read": len(M), "flags": flags, "R0_failures": r0, "S6_failures": s6,
           "energy_read": sum(1 for v in M.values() if v["W"] is not None), "rgm211_host_points": sum(1 for q in P["points"] if q["host"] == "rgm211"),
           "ok": len(M) == len(arm["points"]) and not r0 and not s6 and not [f for f in flags if "SET ASIDE" in f]}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"score_e218 --selftest-real: {'OK' if rep['ok'] else 'NOT OK'} ({rep['points_read']} points of {len(arm['points'])}, {n_runs} runs, "
          f"energy {rep['energy_read']}, rgm211-host points {rep['rgm211_host_points']}, R0 {len(r0)}, S6 {len(s6)}, flags {len(flags)})")
    return 0 if rep["ok"] else 1


def print_forecasts():
    rules, P, fc, G = load_frozen()
    worst = 0.0
    for p in P["points"]:
        f = fc[p["id"]]["v32"]
        W, J = given(f, f["cw"], f["t"])
        worst = max(worst, abs(W / f["W"] - 1))
        print(f"{p['id']:5s} {p['family']:3s} {p['arm']:16s} {p['format']:4s} {p['shire_mask']:10s} v3.2 wall {f['cw']:.1f} mean {f['cm']:.1f} "
              f"s {f['t']:.6f} W {f['W']:.3f} (no lnc {fc[p['id']]['nolnc']['W']:.3f}) J {f['J']:.6f}")
    print(f"given() self-check: MM1-v3.2's W at its own op time = its frozen W, worst relative {worst:.2e} ({'OK' if worst < 1e-9 else 'NOT OK'})")
    return 0 if worst < 1e-9 else 1


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
        sys.exit(print_forecasts())
    if not a.data:
        print(__doc__)
        sys.exit(2)
    data = json.load(open(a.data))
    labels = json.load(open(a.labels)) if a.labels else {}
    res = score(data, labels)
    txt = json.dumps(res, indent=1, sort_keys=True, default=float)
    if a.out:
        open(a.out, "w").write(txt + "\n")
    for k, val in res["verdicts"].items():
        print(f"{k}: {val}")
    sys.exit(0)


if __name__ == "__main__":
    main()
