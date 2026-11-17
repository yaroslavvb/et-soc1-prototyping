#!/usr/bin/python3
"""E209 data, dated note 15 (POST HOC; Tue 17 Nov 2026, PST; round Q212, lane fix-e209d): readings computed AFTER the frozen scorer, from the
scorer's own output, by the definitions registered in tools/claims-v3/e209/E209.md section 7. Everything printed is REPORTED, never a verdict:
no rule, band, tie, forecast, label, verdict or scorer is changed, and nothing is re-scored.

  A. Beside every head-to-head (H1-H6), the three readings the registration names ("REPORTED beside every head-to-head, never verdicts: the
     other test's verdict; a family-level check (the sign test over the families' median d, E207's fix); the bootstrap of the median d").
     The frozen scorer stored all three in its output JSON and printed only the other test's verdict. Each is read from the JSON and
     re-derived here from the scorer's own per-case figures (d, the cells, the exact sign test, the registered bootstrap with its seed),
     and the two are compared. Beside them, POST HOC: each family's count, median d and mean d.
  B. The registered readings (a) the stride step, (b) one K block, (c) the subsets and (d) the kinds, which the frozen scorer's readings()
     does not compute (it computes (e)-(j)).
  C. POST HOC: the margins of the registered rules: how many more failing cells each rule could take and still PASS, its failing cells, and
     the three passing cells nearest the band edge; each cell re-derived and compared with the scorer's.
  D. REPORTED: the governor's readings K1 and K2, with the runs they disagree on named.

Inputs (each checked by sha256 first; the run stops, writing nothing, on any mismatch):
  scored      the frozen scorer's output JSON (score_e209.py e522919a..., run by the kit's step 13 on the data commit ea3fa3ce)
  data        the scorer's input: E208's registered reducer's output on this directory's committed session (step 13)
  points      tools/claims-v3/e209/points-e209.json (registered)
  rules       tools/claims-v3/e209/rules-e209.json (registered: ties, bands, the share)
  v2csv       tools/matmul/mm1/v2/out/mm1_v2_e209.csv (MM1-v2's frozen E209 forecasts: the clock forecast's 800 MHz share)
  f1f2        tools/matmul/mm1/v2/out/f1f2_e209.csv (frozen beside MM1-v2: F1@800's J over idle for reading (d))
Standard library only. /usr/bin/python3 3.12.3, run with -I -B, in this data directory (the defaults are paths from here):
  python3 -I -B posthoc_note15_e209.py scored-e209.json data-e209.json --json posthoc-note15-e209.json > posthoc-note15-e209.txt
Exit 0 written; 4 an input's sha256 differs (nothing written); 5 a re-derived figure differs from the scorer's (everything written, the
difference printed).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
import sys

PINS = {
    "scored": "3e53bb3e587b899f44fb5ec5dc4610d704bc332f3997679ae5173d1472620e94",
    "data": "90bc84ab52441f53a6283e5b096a83e02de5ed5979b4c0cd5423fb203a0c2805",
    "points": "cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261",
    "rules": "0d7dfa791573cf00505143a0188dff7ad5e2ce6f95447c66fef89e9d5b8a62bb",
    "v2csv": "fdd018ca9ceb420285746acdc94b2e0fc62a68141d9b0d3990c3cf9777ec3a63",
    "f1f2": "65a98e01868743b4daf4b06be1b1ba4edbd77c47f3d4824353ffdb0bf4ceefce",
}
UP = os.path.join("..", "..", "..", "..")
DEFAULTS = {
    "points": os.path.join(UP, "tools", "claims-v3", "e209", "points-e209.json"),
    "rules": os.path.join(UP, "tools", "claims-v3", "e209", "rules-e209.json"),
    "v2csv": os.path.join(UP, "tools", "matmul", "mm1", "v2", "out", "mm1_v2_e209.csv"),
    "f1f2": os.path.join(UP, "tools", "matmul", "mm1", "v2", "out", "f1f2_e209.csv"),
}
REG_SIDE = ("REPORTED beside every head-to-head, never verdicts: the other test's verdict; a family-level check (the sign test over the "
            "families' median d, E207's fix); the bootstrap of the median d")
SUBSET_MASKS = ("0x1", "0x80000000", "0xf", "0x1111", "0xf000", "0xff", "0xffff", "0xffff0000")
KIND_PAIRS = (("e34", "e18"), ("e35", "e01"), ("e36", "e19"), ("e38", "e20"))


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def fnum(x):
    try:
        return None if x in (None, "") else float(x)
    except (TypeError, ValueError):
        return None


def ln_ratio(a, b):
    if a is None or b is None or a <= 0 or b <= 0:
        return None
    return math.log(a / b)


def ratio(a, b):
    return None if (a is None or b is None or b == 0) else a / b


def sign_p(w, l):
    """the exact two-sided sign test, as registered (E207's form)"""
    n, k = w + l, min(w, l)
    if n == 0:
        return None
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def boot(ds, seed, B=10000):
    """the registered percentile bootstrap (E209.md section 7: B = 10,000, random.Random('E209|bootstrap|<rule>')), mean and median"""
    ds = [d for d in ds if d is not None]
    if len(ds) < 2:
        return None
    rng = random.Random(seed)
    n = len(ds)
    means, meds = [], []
    for _ in range(B):
        s = [ds[rng.randrange(n)] for _ in range(n)]
        means.append(sum(s) / n)
        meds.append(statistics.median(s))
    means.sort()
    meds.sort()
    lo, hi = int(0.025 * B), int(0.975 * B) - 1
    return {"n": n, "mean": sum(ds) / n, "mean_95": [means[lo], means[hi]], "median": statistics.median(ds), "median_95": [meds[lo], meds[hi]],
            "resamples": B}


def side(lo, hi):
    return "above 0" if lo > 0 else ("below 0" if hi < 0 else "spans 0")


def pct(x, nd=2):
    return "n.f." if x is None else f"{100.0 * x:+.{nd}f}%"


def f4(x):
    return "n.f." if x is None else f"{x:.4f}"


def fp_(p):
    return "n.a." if p is None else (f"{p:.3g}" if p < 0.01 else f"{p:.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scored")
    ap.add_argument("data")
    for k, v in DEFAULTS.items():
        ap.add_argument("--" + k, default=v)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    paths = {"scored": a.scored, "data": a.data, "points": a.points, "rules": a.rules, "v2csv": a.v2csv, "f1f2": a.f1f2}
    got = {k: sha(p) for k, p in paths.items()}
    bad = [k for k in PINS if got[k] != PINS[k]]
    if bad:
        for k in bad:
            print(f"REFUSED: {os.path.basename(paths[k])} sha256 {got[k]} is not the pinned {PINS[k]}", file=sys.stderr)
        sys.exit(4)
    S = json.load(open(paths["scored"]))
    D = json.load(open(paths["data"]))
    PJ = json.load(open(paths["points"]))
    R = json.load(open(paths["rules"]))
    V2 = {r["id"]: r for r in csv.DictReader(open(paths["v2csv"]))}
    F12 = {r["id"]: r for r in csv.DictReader(open(paths["f1f2"]))}
    P = {p["id"]: p for p in PJ["points"]}
    porder = [p["id"] for p in PJ["points"]]
    TC = PJ["time_cases"]
    cases, pts = S["cases"], S["points"]
    tie_ln, tie_w = R["head_to_head"]["tie_ln"], R["head_to_head"]["tie_w"]
    share, min_n = R["verdict"]["share"], R["verdict"]["min_scored"]
    # inputs are named by role, never by the path given, so the printout is the same wherever and under whatever names the files sit
    names = {"scored": "the scorer's output JSON", "data": "its input JSON", "points": "points-e209.json", "rules": "rules-e209.json",
             "v2csv": "mm1_v2_e209.csv", "f1f2": "f1f2_e209.csv"}
    out = {"what": "E209 dated note 15 (POST HOC): readings computed after the frozen scorer from its own output; REPORTED, never verdicts",
           "inputs_sha256": {names[k]: got[k] for k in paths}, "python": sys.version.split()[0]}
    L = []
    diffs = []

    def say(s=""):
        L.append(s)

    say("E209, dated note 15 (POST HOC): readings computed after the frozen scorer from its own output, by E209.md section 7's definitions; "
        "REPORTED, never verdicts")
    say("inputs (sha256 checked): " + "; ".join(f"{names[k]} {got[k][:12]}" for k in paths) + f"; python {out['python']}")
    say("data commit of the session: ea3fa3ce; the frozen scorer: score_e209.py e522919a (its output above, read, never re-run here)")

    # ------------------------------------------------------------------ A. beside every head-to-head
    def rows_time(q, other):
        rows = []
        for tc in TC:
            c = cases.get(tc)
            if c is None:
                continue
            fq = "s" if q == "t" else q
            oq = c.get(other)
            if not c.get("v2_m") or not oq or oq.get(fq) is None:
                rows.append({"id": tc, "d": None, "watts": False, "family": c["family"]})
                continue
            m = c["meas"][q]
            x, y = ln_ratio(m, c["v2_m"][fq]), ln_ratio(m, oq[fq])
            rows.append({"id": tc, "d": (abs(y) - abs(x)) if (x is not None and y is not None) else None, "watts": False, "family": c["family"]})
        return rows

    def rows_energy(v2key, v2w, other_get):
        rows = []
        for pid in porder:
            x = pts.get(pid)
            if x is None or x.get("n_energy", 0) == 0:
                continue
            fam = P[pid]["family"]
            v2s, ot = x.get("v2_e"), other_get(x)
            if not v2s or not ot or ot[0] is None:
                rows.append({"id": pid, "d": None, "watts": x["watts"], "family": fam})
                continue
            if x["watts"]:
                mW = x["meas"]["W"]
                rows.append({"id": pid, "d": abs(mW - ot[1]) - abs(mW - v2s[v2w]), "watts": True, "family": fam})
            else:
                m = x["meas"]["J_over"]
                p_, q_ = ln_ratio(m, v2s[v2key]), ln_ratio(m, ot[0])
                rows.append({"id": pid, "d": (abs(q_) - abs(p_)) if (p_ is not None and q_ is not None) else None, "watts": False, "family": fam})
        return rows

    HS = {"H1": (rows_time("cyc_wall", "v1_m"), "MM1-v1", "cycles"), "H2": (rows_time("cyc_mean", "v1_m"), "MM1-v1", "cycles"),
          "H3": (rows_time("t", "v1_m"), "MM1-v1", "cycles"),
          "H4": (rows_energy("J_given", "W_given", lambda x: ((x["v1_e"] or {}).get("J_given"), (x["v1_e"] or {}).get("W_given")) if x.get("v1_e") else None),
                 "MM1-v1", "joules"),
          "H5": (rows_time("cyc_wall", "F1"), "F1@800", "cycles"),
          "H6": (rows_energy("J_fc", "W_fc", lambda x: (x["F2"]["J_fc"], x["F2"]["W_fc"]) if x.get("F2") else None), "F2@800", "joules")}
    say("")
    say("A. BESIDE EVERY HEAD-TO-HEAD. Registered (E209.md section 7): \"" + REG_SIDE + "\".")
    say("   d = |ln(measured / other)| - |ln(measured / MM1-v2)| per time case (H1-H3, H5) or point (H4, H6); MM1-v2 closer where d > the tie "
        f"({tie_ln['cycles']} in ln for cycles and seconds, {tie_ln['joules']} for joules).")
    out["A_beside_head_to_head"] = {"registered_words": REG_SIDE}
    for h, (rows, other, kind) in HS.items():
        J = S["head_to_head"][h]
        tie = tie_ln[kind]
        w = l = t = 0
        cells = {}
        for r in rows:
            if r["d"] is None:
                cells[r["id"]] = "NOT COMPARED"
                continue
            tt = tie_w if r["watts"] else tie
            if r["d"] > tt:
                w += 1
                cells[r["id"]] = "MM1-v2 CLOSER"
            elif r["d"] < -tt:
                l += 1
                cells[r["id"]] = f"{other} CLOSER"
            else:
                t += 1
                cells[r["id"]] = "TIE"
        ds = [r["d"] for r in rows if r["d"] is not None and not r["watts"]]
        p = sign_p(w, l)
        bs = boot(ds, f"E209|bootstrap|{h}")
        fam = {}
        for r in rows:
            if r["d"] is not None and not r["watts"]:
                fam.setdefault(r["family"] or "-", []).append(r["d"])
        fm = {k: statistics.median(v) for k, v in fam.items()}
        fw = sum(1 for v in fm.values() if v > tie)
        fl = sum(1 for v in fm.values() if v < -tie)
        fp = sign_p(fw, fl)
        # the comparison with the scorer's JSON (exact equality expected: the same figures, order, arithmetic and seed)
        jc = {k: ("MM1-v2 CLOSER" if v == "MM1-v2 CLOSER" else ("TIE" if v == "TIE" else ("NOT COMPARED" if v == "NOT COMPARED" else "OTHER CLOSER")))
              for k, v in J["cells"].items()}
        mc = {k: ("OTHER CLOSER" if v.endswith("CLOSER") and not v.startswith("MM1-v2") else v) for k, v in cells.items()}
        jb, jf = J["bootstrap_mean_d"], J["family_check_REPORTED"]
        same = {"cells": jc == mc, "counts": (w, l, t) == (J["v2_closer"], J["other_closer"], J["ties"]), "sign_p": p == J["p_two_sided"],
                "bootstrap": bs == jb, "family_check": (fm == jf["family_median_d"] and fw == jf["v2_closer"] and fl == jf["other_closer"]
                                                         and fp == jf["p_two_sided"])}
        for k, v in same.items():
            if not v:
                diffs.append(f"{h} {k}")
        reg = J["verdict"]
        boot_txt = (f"the bootstrap of the mean d: mean {bs['mean']:+.5f}, 95% [{bs['mean_95'][0]:+.5f}, {bs['mean_95'][1]:+.5f}] "
                    f"({side(*bs['mean_95'])}; n {bs['n']})")
        sign_txt = f"the exact sign test: {w} against {l}, p {fp_(p)}"
        say("")
        say(f"{h}: {J['what']}")
        say(f"   cells: MM1-v2 closer {w}, {other} closer {l}, ties {t} (untied {w + l})")
        if J["decision"] == "bootstrap":
            say(f"   REGISTERED, decides: {boot_txt} -> {J['bootstrap_verdict']}")
            say(f"   REPORTED, the other test's verdict: {sign_txt} -> {J['sign_test_verdict']}")
        else:
            say(f"   REGISTERED, decides: {sign_txt} -> {J['sign_test_verdict']}")
            say(f"   REPORTED, the other test's verdict: {boot_txt} -> {J['bootstrap_verdict']}")
        say(f"   REPORTED, the bootstrap of the median d: median {bs['median']:+.5f}, 95% [{bs['median_95'][0]:+.5f}, {bs['median_95'][1]:+.5f}] "
            f"({side(*bs['median_95'])})")
        fams = sorted(fm.items(), key=lambda kv: -kv[1])
        say(f"   REPORTED, the family-level check (the sign test over the families' median d, the tie {tie}): MM1-v2 closer {fw}, {other} closer "
            f"{fl}, within the tie {len(fm) - fw - fl}; p {fp_(fp)}")
        say("      families' median d: " + "; ".join(f"{k} {v:+.4f}" for k, v in fams))
        fams_tab = {}
        for k in fam:
            v = fam[k]
            fc = [cells[r["id"]] for r in rows if (r["family"] or "-") == k and r["d"] is not None and not r["watts"]]
            fams_tab[k] = {"n": len(v), "v2_closer": sum(1 for c in fc if c == "MM1-v2 CLOSER"), "other_closer": sum(1 for c in fc if c.endswith("CLOSER") and not c.startswith("MM1-v2")),
                           "ties": sum(1 for c in fc if c == "TIE"), "median_d": fm[k], "mean_d": sum(v) / len(v), "sum_d": sum(v)}
        tot = sum(ds)
        say("      POST HOC, by family (n; MM1-v2 closer / other closer / ties; mean d; share of the sum of d): " + "; ".join(
            f"{k} {x['n']}; {x['v2_closer']}/{x['other_closer']}/{x['ties']}; {x['mean_d']:+.4f}; "
            + (f"{x['sum_d'] / tot:+.2f}" if tot else "n.a.") for k, x in sorted(fams_tab.items(), key=lambda kv: -kv[1]["sum_d"])))
        say(f"   re-derived here from the scorer's per-case figures: cells {'EQUAL' if same['cells'] else 'DIFFER'}, counts {'EQUAL' if same['counts'] else 'DIFFER'}, "
            f"sign p {'EQUAL' if same['sign_p'] else 'DIFFERS'}, both bootstrap intervals (seed 'E209|bootstrap|{h}', {bs['resamples']} resamples) "
            f"{'EQUAL' if same['bootstrap'] else 'DIFFER'}, the family check {'EQUAL' if same['family_check'] else 'DIFFERS'} to the scorer's JSON")
        out["A_beside_head_to_head"][h] = {"what": J["what"], "registered_verdict": reg, "decision": J["decision"], "v2_closer": w, "other_closer": l,
                                           "ties": t, "untied": w + l, "sign_p": p, "sign_test_verdict": J["sign_test_verdict"],
                                           "bootstrap_verdict": J["bootstrap_verdict"], "bootstrap": bs, "family_check": {"family_median_d": fm,
                                           "v2_closer": fw, "other_closer": fl, "p_two_sided": fp}, "by_family_POST_HOC": fams_tab,
                                           "d": {r["id"]: r["d"] for r in rows}, "rederived_equal_to_scorer": same}

    # ------------------------------------------------------------------ B. readings (a)-(d)
    say("")
    say("B. THE REGISTERED READINGS (a)-(d) (E209.md section 7; REPORTED; the frozen scorer's readings() computes (e)-(j) only). The scorer's "
        "figures: measured = the mean of a point's kept runs; MM1-v2 and MM1-v1 at each run's measured clock (route m); F1@800 and F2@800 as frozen.")
    B = {}
    # (a) the stride step
    c28, c29 = pts["e28"], pts["e29"]
    a_e28 = {"measured": ratio(c28["meas"]["cyc_wall"], c29["meas"]["cyc_wall"]), "MM1-v2": ratio(c28["v2_m"]["cyc_wall"], c29["v2_m"]["cyc_wall"]),
             "MM1-v1": ratio(c28["v1_m"]["cyc_wall"], c29["v1_m"]["cyc_wall"]), "F1@800": ratio(c28["F1"]["cyc_wall"], c29["F1"]["cyc_wall"]),
             "MM1-v2 route c": ratio(c28["v2_c"]["cyc_wall"], c29["v2_c"]["cyc_wall"])}
    say("(a) the stride step: the wall cycles an op of the power-of-two NB points.")
    say(f"   e28 / e29 = gemmL1x8x6 / gemmL1x7x6, fp32, the full chip (both measured, 2 runs each): measured {f4(a_e28['measured'])}; MM1-v2 "
        f"{f4(a_e28['MM1-v2'])}; MM1-v1 {f4(a_e28['MM1-v1'])}; F1@800 {f4(a_e28['F1@800'])} (wall: e28 {c28['meas']['cyc_wall']:.1f}, e29 "
        f"{c29['meas']['cyc_wall']:.1f} cycles an op)")
    a_nb = {}
    for pid in ("e33", "e30", "e32"):
        x = pts[pid]
        m = x["meas"]["cyc_wall"]
        a_nb[pid] = {"arm": P[pid]["arm"], "fmt": P[pid]["fmt"], "measured_wall": m, "over_MM1-v2": ratio(m, x["v2_m"]["cyc_wall"]),
                     "over_MM1-v1": ratio(m, x["v1_m"]["cyc_wall"]), "over_F1@800": ratio(m, x["F1"]["cyc_wall"]),
                     "named_in_reading_a": pid != "e32"}
    say("   e33 (gemmL1x16x6 fp16) and e30 (gemmL2x8x4 int8), \"against their neighbours' forecasts\": no neighbour of theirs ran on the day and the "
        "registration names none, so each model's step is read against that model's own forecast of the point: (measured / the model's "
        "neighbour forecast) over (the model's forecast / the same neighbour forecast) = measured / the model's forecast, whatever the "
        "neighbour; no new forecast is made.")
    for pid in ("e33", "e30", "e32"):
        z = a_nb[pid]
        say(f"   {pid} ({z['arm']} {z['fmt']}{'' if z['named_in_reading_a'] else '; the family NB 4 point, beside: not named in (a)'}): measured "
            f"{z['measured_wall']:.1f}; measured / MM1-v2 {f4(z['over_MM1-v2'])}, / MM1-v1 {f4(z['over_MM1-v1'])}, / F1@800 {f4(z['over_F1@800'])}")
    B["a_stride_step"] = {"e28_over_e29": a_e28, "against_own_forecast": a_nb}
    # (b) one K block
    say("(b) one K block (int8, the full chip, at the top point): the measured wall and counter's mean against MM1-v1's (its L2 time "
        "clock-free) and MM1-v2's (its L2 time in cycles), both at each run's measured clock.")
    b = {}
    for pid in ("e07", "e08"):
        x = pts[pid]
        mm = x["meas"]
        b[pid] = {"arm": P[pid]["arm"], "runs_time": x["n_time"], "flags": x["flags"], "f_view_mhz": mm["f"], "f_burst_mhz": mm["f_burst"],
                  "measured": {"wall": mm["cyc_wall"], "mean": mm["cyc_mean"]},
                  "MM1-v2": {"wall": x["v2_m"]["cyc_wall"], "mean": x["v2_m"]["cyc_mean"]},
                  "MM1-v1": {"wall": x["v1_m"]["cyc_wall"], "mean": x["v1_m"]["cyc_mean"]},
                  "measured_over": {"MM1-v2 wall": ratio(mm["cyc_wall"], x["v2_m"]["cyc_wall"]), "MM1-v1 wall": ratio(mm["cyc_wall"], x["v1_m"]["cyc_wall"]),
                                    "MM1-v2 mean": ratio(mm["cyc_mean"], x["v2_m"]["cyc_mean"]), "MM1-v1 mean": ratio(mm["cyc_mean"], x["v1_m"]["cyc_mean"])}}
        z = b[pid]
        say(f"   {pid} ({z['arm']}; {z['runs_time']} run(s) read for time; flags {', '.join(z['flags']) or 'none'}; view clock {z['f_view_mhz']:.2f} MHz, "
            f"burst {z['f_burst_mhz']:.1f} MHz): measured wall {mm['cyc_wall']:.1f} / mean {mm['cyc_mean']:.1f}; MM1-v2 {x['v2_m']['cyc_wall']:.1f} / "
            f"{x['v2_m']['cyc_mean']:.1f} (measured x{z['measured_over']['MM1-v2 wall']:.3f} / x{z['measured_over']['MM1-v2 mean']:.3f}); "
            f"MM1-v1 {x['v1_m']['cyc_wall']:.1f} / {x['v1_m']['cyc_mean']:.1f} (x{z['measured_over']['MM1-v1 wall']:.3f} / "
            f"x{z['measured_over']['MM1-v1 mean']:.3f})")
    B["b_one_K_block"] = b
    # (c) the subsets
    say("(c) the subsets: the wall and the counter's mean at each mask, their ratio, and which model is closer on each (the registered tie, "
        f"{tie_ln['cycles']} in ln; the same cells as H1 and H2 at these time cases).")
    sub = []
    sub_ints = {int(m, 16) for m in SUBSET_MASKS}
    for pid in porder:
        p = P[pid]
        if int(p["mask_mm1v2"], 16) not in sub_ints:
            continue
        x = pts[pid]
        tc = p["time_case"]
        mm = x["meas"]
        row = {"id": pid, "mask": f"0x{int(p['mask_mm1v2'], 16):x}", "shires": p["shires"], "arm": p["arm"], "fmt": p["fmt"], "family": p["family"],
               "measured": {"wall": mm["cyc_wall"], "mean": mm["cyc_mean"], "wall_over_mean": ratio(mm["cyc_wall"], mm["cyc_mean"])},
               "MM1-v2": {"wall": x["v2_m"]["cyc_wall"], "mean": x["v2_m"]["cyc_mean"], "wall_over_mean": ratio(x["v2_m"]["cyc_wall"], x["v2_m"]["cyc_mean"])},
               "MM1-v1": {"wall": x["v1_m"]["cyc_wall"], "mean": x["v1_m"]["cyc_mean"], "wall_over_mean": ratio(x["v1_m"]["cyc_wall"], x["v1_m"]["cyc_mean"])}}
        for q in ("wall", "mean"):
            e2 = ln_ratio(row["measured"][q], row["MM1-v2"][q])
            e1 = ln_ratio(row["measured"][q], row["MM1-v1"][q])
            d = abs(e1) - abs(e2)
            row[f"ln_err_{q}"] = {"MM1-v2": e2, "MM1-v1": e1}
            row[f"d_{q}"] = d
            row[f"closer_{q}"] = "MM1-v2" if d > tie_ln["cycles"] else ("MM1-v1" if d < -tie_ln["cycles"] else "TIE")
            hj = S["head_to_head"]["H1" if q == "wall" else "H2"]["cells"].get(tc)
            hj = "MM1-v2" if hj == "MM1-v2 CLOSER" else ("MM1-v1" if hj == "MM1-v1 CLOSER" else hj)
            row[f"scorer_cell_{q}"] = hj
            if hj != row[f"closer_{q}"]:
                diffs.append(f"(c) {pid} {q}")
        sub.append(row)
    sub.sort(key=lambda r: (r["shires"], int(r["mask"], 16)))
    for r in sub:
        say(f"   {r['id']} mask {r['mask']} ({r['shires']} shire{'s' if r['shires'] > 1 else ''}; {r['arm']} {r['fmt']}): measured wall {r['measured']['wall']:.1f}, "
            f"mean {r['measured']['mean']:.1f}, wall/mean {r['measured']['wall_over_mean']:.3f} (MM1-v2 {r['MM1-v2']['wall_over_mean']:.3f}, MM1-v1 "
            f"{r['MM1-v1']['wall_over_mean']:.3f}); ln(measured/forecast) wall MM1-v2 {pct(r['ln_err_wall']['MM1-v2'], 1)}, MM1-v1 {pct(r['ln_err_wall']['MM1-v1'], 1)}"
            f" -> {r['closer_wall']}{' closer' if r['closer_wall'] != 'TIE' else ''}; mean MM1-v2 {pct(r['ln_err_mean']['MM1-v2'], 1)}, MM1-v1 "
            f"{pct(r['ln_err_mean']['MM1-v1'], 1)} -> {r['closer_mean']}{' closer' if r['closer_mean'] != 'TIE' else ''}")
    cnt = {q: {k: sum(1 for r in sub if r[f"closer_{q}"] == k) for k in ("MM1-v2", "MM1-v1", "TIE")} for q in ("wall", "mean")}
    say(f"   on the wall: MM1-v2 closer at {cnt['wall']['MM1-v2']} of {len(sub)}, MM1-v1 at {cnt['wall']['MM1-v1']}, ties {cnt['wall']['TIE']}; "
        f"on the counter's mean: MM1-v2 at {cnt['mean']['MM1-v2']}, MM1-v1 at {cnt['mean']['MM1-v1']}, ties {cnt['mean']['TIE']} "
        f"(these cells equal the scorer's H1 and H2 cells: {'yes' if not any(x.startswith('(c)') for x in diffs) else 'NO'})")
    B["c_subsets"] = {"points": sub, "counts": cnt}
    # (d) the kinds
    say("(d) the kinds: J over idle of each zeros, ones and real point over its time case's random point, measured beside each model's ratio "
        "(each model at its own seconds; MM1-v2 and MM1-v1 also given the measured seconds, beside).")
    dk = []
    for k, r in KIND_PAIRS:
        xk, xr = pts[k], pts[r]
        mk, mr = xk["meas"], xr["meas"]
        f1k, f1r = fnum(F12[k].get("F1_J_over@800")), fnum(F12[r].get("F1_J_over@800"))
        row = {"pair": f"{k}/{r}", "kind": P[k]["kind"], "fmt": P[k]["fmt"], "arm": P[k]["arm"], "n_energy": [xk["n_energy"], xr["n_energy"]],
               "measured": ratio(mk["J_over"], mr["J_over"]), "measured_W_ratio": ratio(mk["W"], mr["W"]), "measured_t_ratio": ratio(mk["t_e"], mr["t_e"]),
               "MM1-v2": ratio((xk.get("v2_e") or {}).get("J_fc"), (xr.get("v2_e") or {}).get("J_fc")),
               "MM1-v1": ratio((xk.get("v1_e") or {}).get("J_fc"), (xr.get("v1_e") or {}).get("J_fc")) if xk.get("v1_e") and xr.get("v1_e") else None,
               "F1@800": ratio(f1k, f1r),
               "F2@800": ratio((xk.get("F2") or {}).get("J_fc"), (xr.get("F2") or {}).get("J_fc")) if xk.get("F2") and xr.get("F2") else None,
               "MM1-v2 given t": ratio((xk.get("v2_e") or {}).get("J_given"), (xr.get("v2_e") or {}).get("J_given")),
               "MM1-v1 given t": ratio((xk.get("v1_e") or {}).get("J_given"), (xr.get("v1_e") or {}).get("J_given")) if xk.get("v1_e") and xr.get("v1_e") else None}
        cand = {m: row[m] for m in ("MM1-v2", "MM1-v1", "F1@800", "F2@800") if row[m] is not None}
        row["nearest_at_own_seconds"] = min(cand, key=lambda m: abs(math.log(cand[m] / row["measured"])))
        dk.append(row)
        say(f"   {k}/{r} ({row['kind']} over random, {row['fmt']}, {row['arm']}): measured {f4(row['measured'])} (W {f4(row['measured_W_ratio'])}, t "
            f"{f4(row['measured_t_ratio'])}); MM1-v2 {f4(row['MM1-v2'])}; MM1-v1 {f4(row['MM1-v1'])}; F1@800 {f4(row['F1@800'])}; F2@800 "
            f"{f4(row['F2@800'])}; nearest {row['nearest_at_own_seconds']}; given the measured seconds MM1-v2 {f4(row['MM1-v2 given t'])}, "
            f"MM1-v1 {f4(row['MM1-v1 given t'])} ('n.f.' = NOT FORECAST)")
    B["d_kinds"] = dk
    out["B_readings_a_to_d"] = B

    # ------------------------------------------------------------------ C. margins
    say("")
    say(f"C. POST HOC: THE MARGINS OF THE REGISTERED RULES (a rule PASSES at a share of at least {share} of its scored cells; 'could take' = "
        "more failing cells it could take and still PASS). Each cell re-derived from the scorer's figures and compared with its cell.")
    bands = {k: v["band_rel"] for k, v in R["bands"].items()}
    tspec = {"T1m": ("cyc_wall", "v2_m", "T1"), "T1c": ("cyc_wall", "v2_c", "T1"), "T2m": ("cyc_mean", "v2_m", "T2"), "T2c": ("cyc_mean", "v2_c", "T2"),
             "T3m": ("t", "v2_m", "T3"), "T3c": ("t", "v2_c", "T3")}
    espec = {"E1": ("J_over", "v2_e", "J_given", "E1"), "E2m": ("J_over", "v2_e", "J_fc", "E2"), "E2c": ("J_over", "v2_ce", "J_fc", "E2"),
             "E3": ("J_rest", "v2_e", "Jrest_given", "E3"), "E4m": ("J_rest", "v2_e", "Jrest_fc", "E4"), "E4c": ("J_rest", "v2_ce", "Jrest_fc", "E4")}
    C = {}
    watts_pts = [pid for pid in porder if pid in pts and pts[pid].get("watts")]

    def margins(rule, rel, band, unit):
        J = S["rules"][rule]
        mine = {k: ("PASS" if abs(v) <= band else "FAIL") for k, v in rel.items()}
        scorer = {k: v for k, v in J["cells"].items() if v in ("PASS", "FAIL")}
        if mine != scorer:
            diffs.append(f"C {rule} cells")
        n, k = len(mine), sum(1 for v in mine.values() if v == "PASS")
        spare = k - math.ceil(share * n - 1e-12)
        fails = sorted([(c, v) for c, v in rel.items() if mine[c] == "FAIL"], key=lambda cv: -abs(cv[1]))
        near = sorted([(c, v) for c, v in rel.items() if mine[c] == "PASS"], key=lambda cv: band - abs(cv[1]))[:3]
        C[rule] = {"band": band, "unit": unit, "scored": n, "pass": k, "verdict": J["verdict"], "could_take": spare,
                   "failing": dict(fails), "nearest_passing": dict(near), "cells_equal_to_scorer": mine == scorer}
        u = (lambda v: f"{100 * v:+.2f}%") if unit == "rel" else (lambda v: f"{v:+.1f} MHz")
        bt = f"{100 * band:.0f}%" if unit == "rel" else f"{band} MHz"
        say(f"   {rule} (band {bt}): {J['verdict']} {k} of {n}; could take {spare} more; failing: "
            + (", ".join(f"{c} {u(v)}" for c, v in fails) or "none") + "; nearest the band: " + ", ".join(f"{c} {u(v)}" for c, v in near)
            + f"; cells {'= the scorer' if mine == scorer else 'DIFFER from the scorer'}")

    for rule, (q, src, bk) in tspec.items():
        fq = "s" if q == "t" else q
        rel = {}
        for tc in TC:
            c = cases.get(tc)
            if c is None or not c.get(src):
                continue
            rel[tc] = c["meas"][q] / c[src][fq] - 1.0
        margins(rule, rel, bands[bk], "rel")
    for rule, (q, src, fk, bk) in espec.items():
        rel = {}
        for pid in porder:
            x = pts.get(pid)
            if x is None or x.get("n_energy", 0) == 0 or not x.get(src) or x.get("watts"):
                continue
            rel[pid] = x["meas"][q] / x[src][fk] - 1.0
        margins(rule, rel, bands[bk], "rel")
    clk = S["readings_REPORTED"]["clock"]
    kd = {pid: clk[pid]["f_burst"] - clk[pid]["fc_burst"] for pid in porder if pid in clk and clk[pid].get("f_burst") is not None
          and clk[pid].get("fc_burst") is not None}
    margins("K1", kd, R["clock"]["band_mhz"], "MHz")
    rep = S["readings_REPORTED"].get("replicate_sd_W_day") or {}
    say(f"   watts points (scored in watts, band {R['watts']['band_w']} W): {len(watts_pts)}, so no cell used the watts band; the day's replicate "
        f"spread of W over idle (reading (h), the scorer's): pooled sd {rep.get('pooled_sd_W', float('nan')):.3f} W over {rep.get('points')} points "
        f"(df {rep.get('df')}) beside the registered SD_rep {R['watts']['SD_rep_W']} W")
    out["C_margins_POST_HOC"] = {"rules": C, "watts_points": watts_pts, "replicate_sd_W_day": rep, "SD_rep_W": R["watts"]["SD_rep_W"]}

    # ------------------------------------------------------------------ D. the governor
    say("")
    say("D. REPORTED: THE GOVERNOR (K1, registered; K2, REPORTED).")
    K1 = S["rules"]["K1"]
    say(f"   K1 (the burst's mean clock within {K1['band_mhz']} MHz of MM1-v2's forecast): {K1['verdict']} {K1['pass']} of {K1['scored']}; rms "
        f"{K1['rms_mhz']:.2f} MHz, mean {K1['mean_mhz']:+.2f} MHz")
    runs = [r for r in D["runs"] if r.get("role") == "arm" and r.get("ran", True)]
    dis = []
    for r in runs:
        pid = r["arm"]
        fcap = bool(P[pid]["forecast_capped_mm1v2"])
        if fcap != bool(r["capped"]):
            v = (r.get("views") or {}).get(r.get("primary_view")) or {}
            dis.append({"run": r["run"], "point": pid, "forecast_capped": fcap, "measured_capped": bool(r["capped"]),
                        "measured_frac_800_after_step": r.get("frac_800_after_step"),
                        "forecast_frac_800_after_1s": fnum(V2[pid]["clock_fc_frac800_after_1s"]),
                        "measured_burst_mhz_point": (clk.get(pid) or {}).get("f_burst"), "forecast_burst_mhz": (clk.get(pid) or {}).get("fc_burst"),
                        "board_mean_w_in_view": v.get("p_mean_w")})
    K2 = S["K2_REPORTED"]
    say(f"   K2 (REPORTED): MM1-v2's capped forecast agrees with {K2['agree']} of {K2['runs']} kept runs' measured capped flags; 'never capped' "
        f"with {K2['never_capped_agrees']} (the reducer's line: a run is capped when fewer than 80% of its launches 1.0 s or more into a process "
        "are in the 800 MHz band)")
    for z in dis:
        say(f"   run {z['run']}: forecast {'capped' if z['forecast_capped'] else 'not capped'} (800 MHz share {z['forecast_frac_800_after_1s']:.2f}), "
            f"measured {'capped' if z['measured_capped'] else 'not capped'} (share {z['measured_frac_800_after_step']:.3f}); the point's burst clock "
            f"{z['measured_burst_mhz_point']:.1f} MHz measured, {z['forecast_burst_mhz']:.1f} forecast; the board's mean in its view "
            f"{z['board_mean_w_in_view']:.2f} W")
    if len(dis) != K2["runs"] - K2["agree"]:
        diffs.append("D K2 disagreements")
    out["D_governor_REPORTED"] = {"K1": {k: K1[k] for k in ("verdict", "pass", "scored", "band_mhz", "rms_mhz", "mean_mhz")}, "K2": K2, "disagreements": dis}

    say("")
    if diffs:
        say("RE-DERIVATION AGAINST THE SCORER'S OUTPUT: DIFFERENCES: " + "; ".join(diffs))
    else:
        say("RE-DERIVATION AGAINST THE SCORER'S OUTPUT: every re-derived cell, count, p value, interval and family check EQUAL (exact)")
    out["rederivation_differences"] = diffs
    print("\n".join(L))
    if a.json:
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
    sys.exit(5 if diffs else 0)


if __name__ == "__main__":
    main()
