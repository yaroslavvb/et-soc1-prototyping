#!/usr/bin/env python3
"""E224 (Q237): THE SCORER of MM1-v3.3's blind day in two arms, frozen with the registration. Reads THE PICK from E222's committed scores alone,
each arm's measured side, the frozen points, forecasts and rules (refusing if a file it reads changed), and writes every registered verdict per arm
and pooled, with the REPORTED readings. Standard library only (E220's frozen scorer imported at its pin for its readers and helpers).

    python3 -I -B tools/claims-v3/e224/score_e224.py --lab <the lab at GitHub main> --a <arm A data JSON> [--a-tag A] --b <arm B data JSON>
        [--b <more>] [--labels <json>] --out <dir>
    python3 -I -B tools/claims-v3/e224/score_e224.py --selftest-standins      writes selftest-standins.json (every rule both ways; exit 0 = PASS)
    python3 -I -B tools/claims-v3/e224/score_e224.py --selftest-real          writes selftest-real.json (the readers on real committed bytes)

THE PICK (registered): MM1-v3.3 := the composition E222's registered SELECTION RULE picks, read ONLY from E222's committed scores: every file
named scores-e222*.json in a docs/reports/data folder whose name holds 'e222', as committed at the lab's HEAD (git ls-files, git show HEAD:path),
its 'verdicts' > 'SEL' (E222's score_e222.py: 'MM1-v3.3 = MM1-v3.2' + ' + <term>' per joining term). 'MM1-v3.3 = MM1-v3.2' -> MM1-v3.2 (E224 is
MM1-v3.2's second two-card day: H1-H9 NOT APPLICABLE); each other string -> its composition; 'NO DATA', no committed file, an unknown string or
two files that disagree -> NO PICK (the MM1-v3.3 rules read PENDING; the rest are scored). E222's own label (R0 or S6 FAIL) rides with the pick.
THE MEASURED SIDE: E220's readers (score_e220.read_a: arm A in E215 arm B's reducer form; score_e220.read_b: arm B in E208's reducer form, route c
at 790-810 MHz against the 799.0 MHz column, route m REPORTED against the nearest column), unchanged. A point labelled 'ran before' (the card
lane's step 6n) leaves every rule. R0 (every check of C exact or approx; the smoke good) and, arm A, S6 (every kept run at 590-610 MHz): a FAIL
labels every other verdict of its arm.
THE RULES (rules-e224.json): per arm T1-T3, E1-E4 for MM1-v3.3 (its band at 90% of the scored cases or points; TOO FEW under 10; time at the
time-scored points only); H1-H9 per arm and HP1-HP9 pooled (MM1-v3.3 vs MM1-v3.2 on all points, family D, family L; wall cycles, W over idle given
t, J at rest given t); H10-H12 and HP10-HP12 (MM1-v3.2 vs MM1-v3); family P's switch-count rule SW (pooled, MM1-v3.2 with its counts against the
null N; per arm REPORTED). REPORTED: every composition's bands and head-to-heads, per family errors, route m, the switch rule for every model.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import fnmatch
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
S220_PIN = ("tools/claims-v3/e220/score_e220.py", "3c7719904cd3265b65c409475186f757fb00041cdab0a2e237c91ca665ac341f")
V32 = "MM1-v3.2"
COMPOS = ("MM1-v3.2", "MM1-v3.2 + posimb", "MM1-v3.2 + AF4", "MM1-v3.2 + L3S", "MM1-v3.2 + posimb + AF4", "MM1-v3.2 + posimb + L3S",
          "MM1-v3.2 + AF4 + L3S", "MM1-v3.2 + all three")
SIDE = ("MM1-v3.1", "MM1-v3", "MM1-v2")
TERM_ORDER = ("posimb", "AF4", "L3S")
H33 = (("H1", "all", "wall"), ("H2", "all", "Wg"), ("H3", "all", "JRg"), ("H4", "D", "wall"), ("H5", "D", "Wg"), ("H6", "D", "JRg"),
       ("H7", "L", "wall"), ("H8", "L", "Wg"), ("H9", "L", "JRg"))
H32 = (("H10", "wall"), ("H11", "Wg"), ("H12", "JRg"))
RULES_T = ("T1", "T2", "T3", "E1", "E2", "E3", "E4")
COL = {"A": "600.0", "B": "799.0"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_s220():
    p = os.path.join(REPO, S220_PIN[0])
    if sha(p) != S220_PIN[1]:
        print(f"score_e224: REFUSED, {S220_PIN[0]} is not at its pin")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("score_e220_pinned", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S220 = load_s220()
mean, rms, sign_p, decide, predicted, watts_point = S220.mean, S220.rms, S220.sign_p, S220.decide, S220.predicted, S220.watts_point


def sel_string(terms):
    return "MM1-v3.3 = MM1-v3.2" + "".join(" + " + t for t in TERM_ORDER if t in terms)


SEL_TO = {sel_string(()): "MM1-v3.2", sel_string(("posimb",)): "MM1-v3.2 + posimb", sel_string(("AF4",)): "MM1-v3.2 + AF4",
          sel_string(("L3S",)): "MM1-v3.2 + L3S", sel_string(("posimb", "AF4")): "MM1-v3.2 + posimb + AF4",
          sel_string(("posimb", "L3S")): "MM1-v3.2 + posimb + L3S", sel_string(("AF4", "L3S")): "MM1-v3.2 + AF4 + L3S",
          sel_string(("posimb", "AF4", "L3S")): "MM1-v3.2 + all three"}


def load_frozen(check=True):
    sums = {}
    sp = os.path.join(HERE, "SHA256SUMS-e224-registration")
    if os.path.exists(sp):
        for ln in open(sp):
            if ln.strip() and not ln.startswith("#"):
                h, f = ln.split(None, 1)
                f = f.strip()
                if f.startswith("tools/claims-v3/e224/"):
                    f = f[len("tools/claims-v3/e224/"):]
                sums[f] = h
    elif check:
        print("score_e224: REFUSED, SHA256SUMS-e224-registration is missing")
        sys.exit(4)
    for f in ("points-e224.json", "forecast-e224.json", "rules-e224.json"):
        if check and sha(os.path.join(HERE, f)) != sums.get(f):
            print(f"score_e224: REFUSED, {f} differs from SHA256SUMS-e224-registration")
            sys.exit(4)
    P = json.load(open(os.path.join(HERE, "points-e224.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e224.json")))
    R = json.load(open(os.path.join(HERE, "rules-e224.json")))
    return P, F, R


# ------------------------------------------------------------------ THE PICK: E222's committed scores, and nothing else
def pick_from_texts(texts):
    """texts: [(path, committed text)] -> the pick record"""
    if not texts:
        return {"verdict": "NO PICK", "why": "no committed scores-e222*.json in a docs/reports/data folder naming e222", "composition": None,
                "files": []}
    sels, labels, bad = {}, {}, []
    for path, txt in texts:
        try:
            S = json.loads(txt)
        except ValueError:
            bad.append(f"{path}: not JSON")
            continue
        v = (S.get("verdicts") or {}).get("SEL")
        if v is None:
            v = (S.get("selection") or {}).get("verdict")
        if v is None:
            bad.append(f"{path}: no SEL verdict")
            continue
        sels[path] = v
        labels[path] = (S.get("selection") or {}).get("label") or S.get("label")
    if not sels:
        return {"verdict": "NO PICK", "why": "UNREADABLE: " + "; ".join(bad), "composition": None, "files": [p for p, _ in texts]}
    distinct = sorted(set(sels.values()))
    if len(distinct) > 1:
        return {"verdict": "NO PICK", "why": f"AMBIGUOUS: committed files disagree: {sels}", "composition": None, "files": sorted(sels)}
    s = distinct[0]
    if s == "NO DATA":
        return {"verdict": "NO PICK", "why": "E222's SEL reads NO DATA", "composition": None, "files": sorted(sels), "sel": s}
    if s not in SEL_TO:
        return {"verdict": "NO PICK", "why": f"UNREADABLE: SEL string {s!r} is none of the eight", "composition": None, "files": sorted(sels), "sel": s}
    lab = sorted({str(x) for x in labels.values() if x})
    return {"verdict": "PICKED", "sel": s, "composition": SEL_TO[s], "files": sorted(sels), "label_from_E222": lab,
            "why": "E222's committed SEL" + (f" (E222's label: {lab})" if lab else "")}


def read_pick(lab):
    """every committed scores-e222*.json under docs/reports/data/<a folder naming e222>/ at the lab's HEAD, read with git show HEAD:path"""
    try:
        ls = subprocess.run(["git", "-C", lab, "ls-files", "-z", "--", "docs/reports/data"], capture_output=True, check=True).stdout.decode()
    except (OSError, subprocess.CalledProcessError) as e:
        return {"verdict": "NO PICK", "why": f"the lab cannot be read ({e})", "composition": None, "files": []}
    paths = []
    for p in ls.split("\0"):
        parts = p.split("/")
        if len(parts) >= 4 and "e222" in parts[3].lower() and fnmatch.fnmatch(parts[-1], "scores-e222*.json"):
            paths.append(p)
    head = subprocess.run(["git", "-C", lab, "rev-parse", "HEAD"], capture_output=True).stdout.decode().strip()
    texts = []
    for p in sorted(paths):
        txt = subprocess.run(["git", "-C", lab, "show", f"HEAD:{p}"], capture_output=True).stdout.decode("utf-8", "ignore")
        texts.append((p, txt))
    rec = pick_from_texts(texts)
    rec["lab_head"] = head
    return rec


# ------------------------------------------------------------------ the rules
def scope_ok(p, scope):
    return scope == "all" or p["family"] == scope


def cells_of(M, F, R, P, arm, model):
    """E220's cells_of with E224's time rule: time at time-scored points only"""
    a = R["arms"][arm]
    B = {q: a["bands"][q]["band"] for q in RULES_T}
    BW = a["band_w"]["band_W"]
    pts = {p["id"]: p for p in P["points"][arm]}
    cells = {q: {} for q in RULES_T}
    for pid, m in M.items():
        if m.get("ran_before") or pid not in pts:
            continue
        fc = predicted(F, arm, pid, m["col"], model, m)
        if pts[pid].get("time_scored", True):
            for q, mk, fk in (("T1", "wall", "wall"), ("T2", "mean", "mean"), ("T3", "t", "seconds")):
                if m.get(mk) and fc.get(fk):
                    e = m[mk] / fc[fk] - 1.0
                    cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
        if m.get("W") is None or fc.get("Wg") is None:
            continue
        if watts_point(F, arm, pid, m["col"], m):
            for q, fk in (("E1", "Wg"), ("E2", "Wf")):
                d = m["W"] - fc[fk]
                cells[q][pid] = {"err_W": d, "pass": abs(d) <= BW + 1e-12, "watts": True}
        else:
            for q, fk in (("E1", "Jg"), ("E2", "Jf")):
                e = m["J"] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
        for q, fk in (("E3", "JRg"), ("E4", "JRf")):
            if fc.get(fk) and m.get("Jrest"):
                e = m["Jrest"] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
    return cells


def h_cases(M, F, R, P, arm, first, second, q, scope):
    ties = R["arms"][arm]["ties"]
    pts = {p["id"]: p for p in P["points"][arm]}
    out = []
    for pid, m in M.items():
        p = pts.get(pid)
        if m.get("ran_before") or p is None or not scope_ok(p, scope):
            continue
        a, b = predicted(F, arm, pid, m["col"], first, m), predicted(F, arm, pid, m["col"], second, m)
        if q == "wall":
            if p.get("time_scored", True) and m.get("wall") and a.get("wall") and b.get("wall"):
                out.append((abs(math.log(m["wall"] / b["wall"])) - abs(math.log(m["wall"] / a["wall"])), ties["cycles_ln"], f"{arm}:{pid}"))
            continue
        if m.get("W") is None or a.get("Wg") is None or b.get("Wg") is None:
            continue
        if q == "Wg":
            if watts_point(F, arm, pid, m["col"], m):
                out.append((abs(m["W"] - b["Wg"]) - abs(m["W"] - a["Wg"]), ties["watts_W"], f"{arm}:{pid}"))
            elif m["W"] > 0 and a["Wg"] > 0 and b["Wg"] > 0:
                out.append((abs(math.log(m["W"] / b["Wg"])) - abs(math.log(m["W"] / a["Wg"])), ties["joules_ln"], f"{arm}:{pid}"))
            continue
        if m.get("Jrest") and a.get("JRg") and b.get("JRg"):
            out.append((abs(math.log(m["Jrest"] / b["JRg"])) - abs(math.log(m["Jrest"] / a["JRg"])), ties["joules_ln"], f"{arm}:{pid}"))
    return out


def sw_rule(M, F, P, arm, model):
    """family P's switch-count rule on one arm (cases) for one model: Q1 and Q2 cases"""
    pts = {p["id"]: p for p in P["points"][arm]}
    q1, q2 = [], []
    for pid, p in pts.items():
        if p["family"] != "P" or p["pattern_role"] not in ("a", "b"):
            continue
        m = M.get(pid)
        if not m or m.get("ran_before") or m.get("W") is None or not m.get("Top_e"):
            continue
        col = m["col"]
        nr = (F["null_rows"][arm][p["pattern_shape"]]["clocks"].get(col) or {})
        v = ((F["arms"][arm]["points"][pid]["clocks"].get(col) or {}).get(model) or {})
        if v.get("A_W") is None or any((nr.get(k) or {}).get(model, {}).get("A_W") is None for k in ("zeros", "ones", "random")):
            continue
        t = m["Top_e"]
        V = v["A_W"] + v["B_W_us"] / t
        N = sum(nr[k][model]["A_W"] + nr[k][model]["B_W_us"] / t for k in ("zeros", "ones", "random")) / 3.0
        if m["W"] >= 3.0 and V > 0 and N > 0:
            q1.append({"id": f"{arm}:{pid}", "eV": math.log(m["W"] / V), "eN": math.log(m["W"] / N)})
        r, z = M.get(p["pattern_shape"] + "r"), M.get(p["pattern_shape"] + "z")
        if r and z and not r.get("ran_before") and not z.get("ran_before") and r.get("W") is not None and z.get("W") is not None and r.get("Top_e"):
            D = r["W"] - z["W"]
            vr = ((F["arms"][arm]["points"][p["pattern_shape"] + "r"]["clocks"].get(r["col"]) or {}).get(model) or {})
            if D > 0 and vr.get("A_W") is not None:
                VR = vr["A_W"] + vr["B_W_us"] / r["Top_e"]
                q2.append({"id": f"{arm}:{pid}", "eD": ((V - VR) - (m["W"] - r["W"])) / D, "eDN": ((N - VR) - (m["W"] - r["W"])) / D, "D_W": D})
    return q1, q2


def sw_verdict(q1, q2, tie, minimum):
    if not q1 and not q2:
        return {"verdict": "NO DATA", "n_q1": 0, "n_q2": 0}
    out = {"n_q1": len(q1), "n_q2": len(q2)}
    r1v, r1n = rms([c["eV"] for c in q1]), rms([c["eN"] for c in q1])
    r2v, r2n = rms([c["eD"] for c in q2]), rms([c["eDN"] for c in q2])
    out.update({"rms_Q1_counts": r1v, "rms_Q1_null": r1n, "rms_Q2_counts_share_of_D": r2v, "rms_Q2_null_share_of_D": r2n})
    p1 = (r1v is not None and r1n is not None and r1v < r1n)
    p3 = (r2v is not None and r2n is not None and r2v < r2n)
    d2 = decide([(abs(c["eN"]) - abs(c["eV"]), tie, c["id"]) for c in q1], "counts", "null", minimum=minimum)
    d4 = decide([(abs(c["eDN"]) - abs(c["eD"]), tie, c["id"]) for c in q2], "counts", "null", minimum=minimum)
    out.update({"P1": "HOLDS" if p1 else ("NO DATA" if r1v is None else "FAILS"), "P2": d2, "P3": "HOLDS" if p3 else ("NO DATA" if r2v is None else "FAILS"),
                "P4": d4})
    if p1 and p3 and d2["verdict"] == "counts BETTER" and d4["verdict"] == "counts BETTER":
        out["verdict"] = "PASS"
    elif (r1v is not None and not p1) or (r2v is not None and not p3) or d2["verdict"] == "null BETTER" or d4["verdict"] == "null BETTER":
        out["verdict"] = "FAIL"
    else:
        out["verdict"] = "NOT DECIDED"
    return out


def fam_stats(M, F, P, arm, models):
    pts = {p["id"]: p for p in P["points"][arm]}
    out = {}
    for fam in ("D", "P", "L"):
        for mdl in models:
            ew, eg = [], []
            for pid, m in M.items():
                p = pts.get(pid)
                if p is None or p["family"] != fam or m.get("ran_before"):
                    continue
                fc = predicted(F, arm, pid, m["col"], mdl, m)
                if p.get("time_scored", True) and m.get("wall") and fc.get("wall"):
                    ew.append(math.log(m["wall"] / fc["wall"]))
                if m.get("W") and fc.get("Wg") and m["W"] >= 3.0 and fc["Wg"] > 0:
                    eg.append(math.log(m["W"] / fc["Wg"]))
            out[f"{fam}|{mdl}"] = {"n_wall": len(ew), "rms_ln_wall": rms(ew), "bias_ln_wall": mean(ew), "n_Wg": len(eg), "rms_ln_Wg": rms(eg),
                                   "bias_ln_Wg": mean(eg)}
    return out


def score(dA, dB, P, F, R, pick, labels=None, tagA="A"):
    labels = labels or {}
    mdl_all = COMPOS + SIDE
    out = {"experiment": "E224", "the_pick": pick, "arms": {}, "verdicts": {}, "reported": {}}
    MA, MmA, fa, r0a, s6a, hasA = S220.read_a(dA, P, tagA, labels) if dA else ({}, {}, [], [], [], False)
    MB, MmB, fb, r0b, _, hasB = S220.read_b(dB, P, labels) if dB else ({}, {}, [], [], [], False)
    M = {"A": MA, "B": MB}
    has = {"A": hasA, "B": hasB}
    lab = {}
    v33 = pick.get("composition") if pick.get("verdict") == "PICKED" else None
    for arm, flags, r0, s6 in (("A", fa, r0a, s6a), ("B", fb, r0b, [])):
        x = {"flags": flags, "R0": "NO DATA" if not has[arm] else ("FAIL" if r0 else "PASS"), "R0_failures": r0}
        if arm == "A":
            x["S6"] = "NO DATA" if not has[arm] else ("FAIL" if s6 else "PASS")
            x["S6_failures"] = s6
        lab[arm] = (" [labelled: R0 FAIL]" if r0 else "") + (" [labelled: S6 FAIL]" if s6 else "")
        x["n_points_measured"] = len(M[arm])
        x["route_m_REPORTED"] = sorted((MmB if arm == "B" else {}).keys())
        # the bands for MM1-v3.3 (registered) and every model (REPORTED)
        bands = {}
        for mdl in mdl_all:
            cells = cells_of(M[arm], F, R, P, arm, mdl)
            bands[mdl] = {q: dict(S220.verdict(cells[q]), cells=cells[q]) for q in RULES_T}
        x["bands_REPORTED_every_model"] = {mdl: {q: {k: v for k, v in b.items() if k != "cells"} for q, b in bs.items()} for mdl, bs in bands.items()}
        for q in RULES_T:
            if v33 is None:
                x[q] = {"verdict": "PENDING (NO PICK)" if has[arm] else "NO DATA"}
            else:
                x[q] = dict(bands[v33][q])
                x[q]["model"] = v33
                x[q]["verdict"] = x[q]["verdict"] + lab[arm] if x[q]["verdict"] not in ("NO DATA",) else x[q]["verdict"]
        # the head-to-heads per arm
        for hid, scope, q in H33:
            if v33 is None:
                x[hid] = {"verdict": "PENDING (NO PICK)" if has[arm] else "NO DATA"}
            elif v33 == V32:
                x[hid] = {"verdict": "NOT APPLICABLE (MM1-v3.3 = MM1-v3.2)"}
            else:
                x[hid] = decide(h_cases(M[arm], F, R, P, arm, v33, V32, q, scope), "MM1-v3.3", V32, minimum=R["minimum_decided"])
                x[hid]["first_model"] = v33
                if x[hid]["verdict"] not in ("NO DATA",):
                    x[hid]["verdict"] += lab[arm]
            x[hid].update({"scope": scope, "quantity": q})
        for hid, q in H32:
            x[hid] = decide(h_cases(M[arm], F, R, P, arm, V32, "MM1-v3", q, "all"), V32, "MM1-v3", minimum=R["minimum_decided"])
            if x[hid]["verdict"] not in ("NO DATA",):
                x[hid]["verdict"] += lab[arm]
            x[hid].update({"scope": "all", "quantity": q})
        # every composition's head-to-heads against MM1-v3.2 (REPORTED)
        x["compositions_vs_v32_REPORTED"] = {c: {hid: decide(h_cases(M[arm], F, R, P, arm, c, V32, q, scope), c, V32, minimum=R["minimum_decided"])["verdict"]
                                                 for hid, scope, q in H33} for c in COMPOS[1:]}
        # the switch rule per arm (REPORTED), every model
        x["SW_by_arm_REPORTED"] = {mdl: sw_verdict(*sw_rule(M[arm], F, P, arm, mdl), R["p_tie"], R["p_min_decided"]) for mdl in mdl_all}
        x["family_stats_REPORTED"] = fam_stats(M[arm], F, P, arm, mdl_all)
        out["arms"][arm] = x
    # pooled
    pooled = {}
    lab_any = lab["A"] + lab["B"]
    for hid, scope, q in H33:
        k = "HP" + hid[1:]
        if v33 is None:
            pooled[k] = {"verdict": "PENDING (NO PICK)" if (has["A"] or has["B"]) else "NO DATA"}
        elif v33 == V32:
            pooled[k] = {"verdict": "NOT APPLICABLE (MM1-v3.3 = MM1-v3.2)"}
        else:
            pooled[k] = decide(h_cases(M["A"], F, R, P, "A", v33, V32, q, scope) + h_cases(M["B"], F, R, P, "B", v33, V32, q, scope), "MM1-v3.3", V32,
                               minimum=R["minimum_decided"])
            pooled[k]["first_model"] = v33
            if pooled[k]["verdict"] != "NO DATA":
                pooled[k]["verdict"] += lab_any
        pooled[k].update({"scope": scope, "quantity": q})
    for hid, q in H32:
        k = "HP" + hid[1:]
        pooled[k] = decide(h_cases(M["A"], F, R, P, "A", V32, "MM1-v3", q, "all") + h_cases(M["B"], F, R, P, "B", V32, "MM1-v3", q, "all"), V32, "MM1-v3",
                           minimum=R["minimum_decided"])
        if pooled[k]["verdict"] != "NO DATA":
            pooled[k]["verdict"] += lab_any
        pooled[k].update({"scope": "all", "quantity": q})
    sw = {}
    for mdl in mdl_all:
        a1, a2 = sw_rule(M["A"], F, P, "A", mdl)
        b1, b2 = sw_rule(M["B"], F, P, "B", mdl)
        sw[mdl] = sw_verdict(a1 + b1, a2 + b2, R["p_tie"], R["p_min_decided"])
    pooled["SW"] = dict(sw[V32], model=V32)
    if pooled["SW"]["verdict"] != "NO DATA":
        pooled["SW"]["verdict"] += lab_any
    out["pooled"] = pooled
    out["reported"]["SW_pooled_every_model"] = sw
    if v33 is not None:
        out["reported"]["SW_pooled_MM1-v3.3"] = dict(sw[v33], model=v33)
    for arm in ("A", "B"):
        x = out["arms"][arm]
        out["verdicts"][f"{arm}:R0"] = x["R0"]
        if arm == "A":
            out["verdicts"]["A:S6"] = x["S6"]
        for k in RULES_T + tuple(h for h, _, _ in H33) + tuple(h for h, _ in H32):
            out["verdicts"][f"{arm}:{k}"] = x[k]["verdict"]
    for k, v in pooled.items():
        out["verdicts"][f"P:{k}"] = v["verdict"]
    out["verdicts"]["PICK"] = pick["verdict"] + (f": MM1-v3.3 = {pick['composition']}" if pick.get("composition") else f" ({pick.get('why')})")
    return out


# ------------------------------------------------------------------ the self-tests on stand-ins
def truth_fn(F, model, tscale=1.0, wscale=1.0, null_at_patterns=False, P=None, mhz=None):
    pts = {arm: {p["id"]: p for p in P["points"][arm]} for arm in ("A", "B")}

    def fn(arm, p):
        tr = S220.truth_of(F, arm, p["id"], COL[arm], model)
        t32 = S220.truth_of(F, arm, p["id"], COL[arm], V32)
        tr["prest"] = t32["prest"]
        if tr["W"] is None:
            return None
        if null_at_patterns and p["family"] == "P" and p["pattern_role"] in ("a", "b"):
            nr = F["null_rows"][arm][p["pattern_shape"]]["clocks"][COL[arm]]
            t = tr["T"]
            tr["W"] = sum(nr[k][model]["A_W"] + nr[k][model]["B_W_us"] / t for k in ("zeros", "ones", "random")) / 3.0
        tr["wall"] *= tscale
        tr["mean"] *= tscale
        tr["t"] *= tscale
        tr["T"] *= tscale
        tr["W"] *= wscale
        if mhz:
            tr["mhz"] = mhz
        return tr
    return fn


def make_lab(tmp, sels):
    """a stand-in lab: a git repository holding stand-in E222 scores files committed at HEAD (sels: [(folder, file, text)])"""
    if os.path.exists(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp)
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", HOME=tmp)
    subprocess.run(["git", "init", "-q", tmp], check=True, env=env)
    os.makedirs(os.path.join(tmp, "docs", "reports", "data"), exist_ok=True)
    open(os.path.join(tmp, "docs", "reports", "data", "README.md"), "w").write("stand-in\n")
    for folder, fn, txt in sels:
        d = os.path.join(tmp, "docs", "reports", "data", folder)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, fn), "w").write(txt)
    subprocess.run(["git", "-C", tmp, "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", tmp, "-c", "user.name=stand-in", "-c", "user.email=stand-in", "-c", "core.hooksPath=/dev/null",
                    "commit", "-q", "-m", "stand-in E222 scores"], check=True, env=env)
    return tmp


def e222_text(sel, label=None):
    return json.dumps({"verdicts": {"SEL": sel}, "selection": {"verdict": sel, "label": label}})


def expect_h(F, R, P, arm_list, first, second, q, scope, truth):
    """the expected verdict of a head-to-head on a stand-in day whose measurement IS one forecaster's (truth), computed apart from the scorer:
    every case where the two forecasters differ by more than the tie is decided toward the truth"""
    n_pos = n_neg = n = 0
    for arm in arm_list:
        ties = R["arms"][arm]["ties"]
        for p in P["points"][arm]:
            if not scope_ok(p, scope):
                continue
            col = COL[arm]
            a = (F["arms"][arm]["points"][p["id"]]["clocks"][col].get(first) or {})
            b = (F["arms"][arm]["points"][p["id"]]["clocks"][col].get(second) or {})
            t = (F["arms"][arm]["points"][p["id"]]["clocks"][col].get(truth) or {})
            if t.get("W_over_idle") is None:
                continue
            if q == "wall":
                if not p.get("time_scored", True):
                    continue
                g = abs(math.log(t["cycles_per_op_wall"] / b["cycles_per_op_wall"])) - abs(math.log(t["cycles_per_op_wall"] / a["cycles_per_op_wall"]))
                tie = ties["cycles_ln"]
            else:
                if a.get("A_W") is None or b.get("A_W") is None:
                    continue
                T = t["T_op_us"]
                wt = t["A_W"] + t["B_W_us"] / T
                wa, wb = a["A_W"] + a["B_W_us"] / T, b["A_W"] + b["B_W_us"] / T
                if q == "Wg":
                    w32 = F["arms"][arm]["points"][p["id"]]["clocks"][col][V32]["W_over_idle"]
                    if w32 < 3.0 or wt < 3.0:
                        g, tie = abs(wt - wb) - abs(wt - wa), ties["watts_W"]
                    else:
                        g, tie = abs(math.log(wt / wb)) - abs(math.log(wt / wa)), ties["joules_ln"]
                else:
                    pr = F["arms"][arm]["points"][p["id"]]["clocks"][col][V32]["rest_law_W"]      # the stand-in day's rest: MM1-v3.2's (truth_fn's)
                    g = abs(math.log((pr + wt) / (pr + wb))) - abs(math.log((pr + wt) / (pr + wa)))
                    tie = ties["joules_ln"]
            n += 1
            n_pos += g > tie
            n_neg += g < -tie
    if n == 0:
        return "NO DATA"
    if n_pos + n_neg < R["minimum_decided"]:
        return "TOO FEW"
    pv = sign_p(n_pos, n_neg)
    return (("MM1-v3.3" if first != V32 else V32) + " BETTER" if n_pos > n_neg else (second if second != V32 else V32) + " BETTER") if pv < 0.05 \
        else "NOT DECIDED"


def selftest_standins(out_path):
    P, F, R = load_frozen(check=False)
    tmp_root = tempfile.mkdtemp(prefix="e224-selftest-")
    results, ok_all = [], True
    seen = {}

    def note(rule, verdict):
        seen.setdefault(rule, set()).add(verdict.split(" [labelled")[0])

    def run_day(name, pick_rec, truth, mutate_a=None, mutate_b=None, labels=None):
        dA = S220.make_a(P, F, truth, mutate_a)
        dB = S220.make_b(P, F, truth, mutate_b)
        S = score(dA, dB, P, F, R, pick_rec, labels or {})
        for k, v in S["verdicts"].items():
            note(k.split(":", 1)[-1] if ":" in k else k, v)
        return S

    # (1) THE PICK: each of the eight stand-in E222 outcomes, read through a stand-in lab's committed files, and the refusals
    picks = {}
    for terms, comp in [((), "MM1-v3.2"), (("posimb",), "MM1-v3.2 + posimb"), (("AF4",), "MM1-v3.2 + AF4"), (("L3S",), "MM1-v3.2 + L3S"),
                        (("posimb", "AF4"), "MM1-v3.2 + posimb + AF4"), (("posimb", "L3S"), "MM1-v3.2 + posimb + L3S"),
                        (("AF4", "L3S"), "MM1-v3.2 + AF4 + L3S"), (("posimb", "AF4", "L3S"), "MM1-v3.2 + all three")]:
        s = sel_string(terms)
        lab = make_lab(os.path.join(tmp_root, "lab-" + (("-".join(terms)) or "none")),
                       [("2026-11-21-e222-blind-matmul-aifoundry3", "scores-e222.json", e222_text(s))])
        rec = read_pick(lab)
        good = rec["verdict"] == "PICKED" and rec["composition"] == comp
        ok_all &= good
        picks[comp] = rec
        results.append({"test": f"pick: stand-in E222 SEL {s!r}", "want": comp, "got": rec.get("composition"), "pass": good})
    for name, sels, want in (
            ("no committed file", [], "NO PICK"),
            ("NO DATA", [("2026-11-21-e222-x", "scores-e222.json", e222_text("NO DATA"))], "NO PICK"),
            ("an unknown string", [("2026-11-21-e222-x", "scores-e222.json", e222_text("MM1-v3.3 = MM1-v3.2 + T7"))], "NO PICK"),
            ("two files disagreeing", [("2026-11-21-e222-x", "scores-e222.json", e222_text(sel_string(("AF4",)))),
                                       ("2026-11-21-e222-x", "scores-e222-A.json", e222_text(sel_string(("L3S",))))], "NO PICK"),
            ("a folder not naming e222", [("2026-11-21-e218-x", "scores-e222.json", e222_text(sel_string(("AF4",))))], "NO PICK"),
            ("two files agreeing, E222 labelled R0 FAIL", [("2026-11-21-e222-x", "scores-e222.json", e222_text(sel_string(("AF4",)), "R0 FAIL")),
                                                          ("2026-11-21-e222-x", "scores-e222-A.json", e222_text(sel_string(("AF4",)), "R0 FAIL"))],
             "PICKED")):
        lab = make_lab(os.path.join(tmp_root, "lab-x"), sels)
        rec = read_pick(lab)
        good = rec["verdict"] == want
        ok_all &= good
        results.append({"test": f"pick: {name}", "want": want, "got": rec["verdict"], "why": rec.get("why"), "pass": good})
    # (2) every rule both ways on stand-in days, for each pick
    exp_fail = []
    for comp, rec in picks.items():
        # the day whose measurement is the pick's own forecast: its bands PASS; each H test reads as the independent expectation says
        S = run_day(f"truth {comp}", rec, truth_fn(F, comp, P=P))
        for arm in ("A", "B"):
            for q in RULES_T:
                v = S["arms"][arm][q]["verdict"]
                good = v.startswith("PASS")
                ok_all &= good
                results.append({"test": f"{comp} exact, arm {arm} {q}", "want": "PASS", "got": v, "pass": good})
            for hid, scope, q in H33:
                v = S["arms"][arm][hid]["verdict"]
                want = "NOT APPLICABLE (MM1-v3.3 = MM1-v3.2)" if comp == V32 else expect_h(F, R, P, [arm], comp, V32, q, scope, comp)
                good = v == want
                ok_all &= good
                results.append({"test": f"truth {comp}, arm {arm} {hid}", "want": want, "got": v, "pass": good})
        for hid, scope, q in H33:
            k = "HP" + hid[1:]
            v = S["pooled"][k]["verdict"]
            want = "NOT APPLICABLE (MM1-v3.3 = MM1-v3.2)" if comp == V32 else expect_h(F, R, P, ["A", "B"], comp, V32, q, scope, comp)
            good = v == want
            ok_all &= good
            results.append({"test": f"truth {comp}, pooled {k}", "want": want, "got": v, "pass": good})
        # the day whose measurement is MM1-v3.2's: the H tests read MM1-v3.2 BETTER where they can decide
        if comp != V32:
            S2 = run_day(f"truth MM1-v3.2 with pick {comp}", rec, truth_fn(F, V32, P=P))
            for hid, scope, q in H33:
                k = "HP" + hid[1:]
                v = S2["pooled"][k]["verdict"]
                want = expect_h(F, R, P, ["A", "B"], comp, V32, q, scope, V32)
                good = v == want
                ok_all &= good
                results.append({"test": f"truth MM1-v3.2 (pick {comp}), pooled {k}", "want": want, "got": v, "pass": good})
    # (3) the bands FAIL, H10-H12 both ways, the switch rule both ways, R0 and S6, the labels, NO DATA
    rec = picks["MM1-v3.2 + all three"]
    S = run_day("time 1.3x", rec, truth_fn(F, "MM1-v3.2 + all three", tscale=1.3, P=P))
    for arm in ("A", "B"):
        for q in ("T1", "T2", "T3"):
            v = S["arms"][arm][q]["verdict"]
            good = v.startswith("FAIL")
            ok_all &= good
            results.append({"test": f"time 1.3x, arm {arm} {q}", "want": "FAIL", "got": v, "pass": good})
    S = run_day("energy 1.3x", rec, truth_fn(F, "MM1-v3.2 + all three", wscale=1.3, P=P))
    for arm in ("A", "B"):
        for q in ("E1", "E2"):
            v = S["arms"][arm][q]["verdict"]
            good = v.startswith("FAIL")
            ok_all &= good
            results.append({"test": f"energy 1.3x, arm {arm} {q}", "want": "FAIL", "got": v, "pass": good})
    S = run_day("energy 0.5x", rec, truth_fn(F, "MM1-v3.2 + all three", wscale=0.5, P=P))
    for arm in ("A", "B"):
        for q in ("E3", "E4"):
            v = S["arms"][arm][q]["verdict"]
            good = v.startswith("FAIL")
            ok_all &= good
            results.append({"test": f"energy 0.5x, arm {arm} {q}", "want": "FAIL", "got": v, "pass": good})
    for truth, want in ((V32, "MM1-v3.2 BETTER"), ("MM1-v3", "MM1-v3 BETTER")):
        S = run_day(f"truth {truth}", picks[V32], truth_fn(F, truth, P=P))
        for hid, q in H32:
            k = "HP" + hid[1:]
            v = S["pooled"][k]["verdict"]
            w = expect_h(F, R, P, ["A", "B"], V32, "MM1-v3", q, "all", truth)
            good = v == w
            ok_all &= good
            results.append({"test": f"truth {truth}, pooled {k}", "want": w, "got": v, "pass": good})
            for arm in ("A", "B"):
                v = S["arms"][arm][hid]["verdict"]
                w = expect_h(F, R, P, [arm], V32, "MM1-v3", q, "all", truth)
                good = v == w
                ok_all &= good
                results.append({"test": f"truth {truth}, arm {arm} {hid}", "want": w, "got": v, "pass": good})
        if truth == V32:
            v = S["pooled"]["SW"]["verdict"]
            good = v == "PASS"
            ok_all &= good
            results.append({"test": "SW: the counts exact (truth MM1-v3.2 with its counts)", "want": "PASS", "got": v, "pass": good})
    S = run_day("SW null", picks[V32], truth_fn(F, V32, null_at_patterns=True, P=P))
    v = S["pooled"]["SW"]["verdict"]
    good = v == "FAIL"
    ok_all &= good
    results.append({"test": "SW: the patterns at the null N (truth N)", "want": "FAIL", "got": v, "pass": good})

    def bad_a(d):
        pid = sorted(d["arms"]["A"]["points"])[0]
        d["arms"]["A"]["points"][pid]["runs"][0]["checks"] = ["wrong"]

    def bad_b(d):
        d["runs"][0]["checks"] = ["wrong"]
    S = run_day("bad check", picks[V32], truth_fn(F, V32, P=P), mutate_a=bad_a, mutate_b=bad_b)
    for arm in ("A", "B"):
        v = S["arms"][arm]["R0"]
        good = v == "FAIL" and S["arms"][arm]["T1"]["verdict"].endswith("[labelled: R0 FAIL]")
        ok_all &= good
        results.append({"test": f"R0, arm {arm}: one check wrong (and the label on T1)", "want": "FAIL", "got": v, "pass": good})
    S = run_day("700 MHz on arm A", picks[V32], truth_fn(F, V32, P=P, mhz=700))
    v = S["arms"]["A"]["S6"]
    good = v == "FAIL"
    ok_all &= good
    results.append({"test": "S6, arm A: runs at 700 MHz", "want": "FAIL", "got": v, "pass": good})
    S = run_day("good day", picks[V32], truth_fn(F, V32, P=P))
    for arm in ("A", "B"):
        good = S["arms"][arm]["R0"] == "PASS" and (arm == "B" or S["arms"]["A"]["S6"] == "PASS")
        ok_all &= good
        results.append({"test": f"R0 (and S6) arm {arm} on a good day", "want": "PASS", "got": S["arms"][arm]["R0"], "pass": good})
    lbl = {"ran_before_points": {"A": [p["id"] for p in P["points"]["A"]][:70], "B": [p["id"] for p in P["points"]["B"]][:70]}}
    S = run_day("every point labelled ran before", picks["MM1-v3.2 + AF4"], truth_fn(F, "MM1-v3.2 + AF4", P=P), labels=lbl)
    v = S["arms"]["A"]["T1"]["verdict"]
    good = v == "NO DATA"
    ok_all &= good
    results.append({"test": "labels: every arm A point 'ran before' leaves every rule", "want": "NO DATA", "got": v, "pass": good})
    S = score({}, [], P, F, R, {"verdict": "NO PICK", "why": "stand-in", "composition": None, "files": []})
    good = all(v.startswith("NO DATA") or v.startswith("NO PICK") or v.startswith("PENDING") for v in S["verdicts"].values())
    ok_all &= good
    results.append({"test": "no data and no pick: every verdict NO DATA, PENDING or NO PICK", "got": sorted(set(S["verdicts"].values())), "pass": good})
    dA = S220.make_a(P, F, truth_fn(F, V32, P=P))
    dB = S220.make_b(P, F, truth_fn(F, V32, P=P))
    S = score(dA, dB, P, F, R, {"verdict": "NO PICK", "why": "stand-in", "composition": None, "files": []})
    good = S["arms"]["A"]["T1"]["verdict"].startswith("PENDING") and S["pooled"]["HP1"]["verdict"].startswith("PENDING") and \
        S["pooled"]["HP10"]["verdict"] != "NO DATA"
    ok_all &= good
    results.append({"test": "data and no pick: the MM1-v3.3 rules PENDING, H10-H12 and SW scored", "got": [S["arms"]["A"]["T1"]["verdict"],
                    S["pooled"]["HP1"]["verdict"], S["pooled"]["HP10"]["verdict"], S["pooled"]["SW"]["verdict"]], "pass": good})
    shutil.rmtree(tmp_root, ignore_errors=True)
    both_ways = {k: sorted(v) for k, v in sorted(seen.items())}
    rec = {"what": "score_e224's self-test on stand-ins (THE PICK from stand-in E222 outcomes, each of the eight, through stand-in labs' committed "
                   "files; every rule both ways where its frozen forecasts allow)", "verdict": "PASS" if ok_all else "FAIL", "n_tests": len(results),
           "n_pass": sum(1 for r in results if r["pass"]), "tests": results, "verdicts_seen_by_rule": both_ways}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True, default=str)
    print(f"selftest-standins: {rec['verdict']} ({rec['n_pass']} of {rec['n_tests']} tests)")
    for r in results:
        if not r["pass"]:
            print("  FAILED:", r)
    return ok_all


def selftest_real(out_path):
    """E220's readers (imported unchanged) on real committed bytes from each arm's card, E215's and E216's points standing in for E224's (E220's
    own real-bytes test, re-run here in E224's scorer); and THE PICK's reader on the real lab at its HEAD (E222's scores not yet committed: NO PICK)"""
    A_REL = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/data-e215.json"
    B_REL = "docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/data-e216.json"
    dA = json.load(open(os.path.join(REPO, A_REL)))
    dB = json.load(open(os.path.join(REPO, B_REL)))
    e215 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e215", "points-e215.json")))["arms"]["B"]["points"]
    e216 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e216", "points-e216.json")))["points"]
    PA = {"points": {"A": [{"id": p["id"], "arm": p["arm"], "format": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"],
                            "host": p["host"], "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"], "loop": p["loop"], "family": p["family"]}
                           for p in e215], "B": []}}
    PB = {"points": {"A": [], "B": [{"id": p["id"], "arm": p["arm"], "format": p["fmt"], "minions": p["minions"], "shire_mask": p["mask"],
                                     "loop": p["loop"], "family": p["family"]} for p in e216]}}
    MA, _, fa, r0a, s6a, _ = S220.read_a(dA, PA, "B", {})
    MB, MmB, fb, r0b, _, _ = S220.read_b([dB], PB, {})
    okA = len(MA) == len(e215) and not r0a and not s6a and all(m.get("W") is not None for m in MA.values())
    okB = len(MB) >= 0.9 * len(e216) and not r0b
    pk = read_pick(REPO)
    okP = pk["verdict"] == "NO PICK" or (pk["verdict"] == "PICKED" and pk.get("composition") in COMPOS)
    rec = {"what": "score_e224's readers on real committed bytes", "arm_A_reader": {"input": A_REL, "sha256": sha(os.path.join(REPO, A_REL)),
           "points_read": len(MA), "points_registered": len(e215), "R0_failures": r0a, "S6_failures": s6a, "ok": okA},
           "arm_B_reader": {"input": B_REL, "sha256": sha(os.path.join(REPO, B_REL)), "points_route_c": len(MB), "points_route_m": len(MmB),
                            "points_registered": len(e216), "R0_failures": r0b, "ok": okB},
           "pick_reader_on_the_lab": {"lab_head": pk.get("lab_head"), "verdict": pk["verdict"], "why": pk.get("why"), "ok": okP,
                                      "note": ("at the registration E222's scores are not committed: NO PICK is the right reading then; a later run "
                                               "reads the committed pick")},
           "verdict": "OK" if (okA and okB and okP) else "NOT OK"}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-real: {rec['verdict']} (arm A reader {len(MA)}/{len(e215)}, arm B route c {len(MB)}/{len(e216)}, the pick reader {pk['verdict']})")
    return okA and okB and okP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab")
    ap.add_argument("--a")
    ap.add_argument("--a-tag", default="A")
    ap.add_argument("--b", action="append", default=[])
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--selftest-standins", action="store_true")
    ap.add_argument("--selftest-real", action="store_true")
    a = ap.parse_args()
    if a.selftest_standins:
        sys.exit(0 if selftest_standins(os.path.join(HERE, "selftest-standins.json")) else 1)
    if a.selftest_real:
        sys.exit(0 if selftest_real(os.path.join(HERE, "selftest-real.json")) else 1)
    if not a.lab or not a.out:
        print("score_e224: --lab and --out are required")
        sys.exit(10)
    P, F, R = load_frozen()
    pick = read_pick(os.path.abspath(a.lab))
    dA = json.load(open(a.a)) if a.a else {}
    dB = [json.load(open(x)) for x in a.b]
    labels = json.load(open(a.labels)) if a.labels else {}
    S = score(dA, dB, P, F, R, pick, labels, a.a_tag)
    os.makedirs(a.out, exist_ok=True)
    json.dump(S, open(os.path.join(a.out, "scores-e224.json"), "w"), indent=1, sort_keys=True, default=str)
    lines = [f"{k}: {v}" for k, v in sorted(S["verdicts"].items())]
    open(os.path.join(a.out, "scores-e224.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
