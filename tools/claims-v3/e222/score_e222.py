#!/usr/bin/env python3
"""E222 (Q236): THE SCORER of the MM1-v3.3 candidates' blind day on aifoundry3 card 0, frozen with the registration. Reads the measured side, the
frozen points, forecasts and rules (refusing if a file it reads changed), and writes every registered verdict, the selection, and the REPORTED
readings. Standard library only (E220's frozen scorer's readers imported at its pin).

    python3 -I -B tools/claims-v3/e222/score_e222.py --a <E222 data JSON> [--a-tag A] [--labels <json>] --out <dir>
            [--e220-a <E220 arm A data JSON> --e220-b <E220 arm B data JSON> [--e220-b ...] --e220-verified <the verify lane's result file>]
    python3 -I -B tools/claims-v3/e222/score_e222.py --selftest-standins      writes selftest-standins.json (every rule both ways; exit 0 = PASS)
    python3 -I -B tools/claims-v3/e222/score_e222.py --selftest-real          writes selftest-real.json (the reader on E218's committed bytes)

THE MEASURED SIDE: E218's run form (E215 arm A's reducer form, the kit's reducer writes it), read by E220's frozen scorer's read_a at its pin
(score_e220.py 3c771990...) exactly as E218's and E220's arm A: a run kept when its record equals its point (arm, type, minions, the shire mask
read as a number), it has t_gemm_s and cycles_gemm, and - a run of rgm211's host (the gemmLnc branch) - its walk and identity gate are good; per
point the mean of its kept runs. R0 (every check of C exact or approx; the smoke good) and S6 (every kept run at 590-610 MHz): a FAIL labels every
other verdict and the selection. A point labelled 'ran before' by the card lane's step 6n leaves every rule (said).
THE RULES (rules-e222.json; E222.md section 7): T1-T3, E1-E4 (MM1-v3.2 within its band at 90% of the registered points); H1-H10 (MM1-v3.2 against
MM1-v3 and MM1-v3.1); HC-posimb, HC-AF4, HC-L3S (each candidate against MM1-v3.2 on its own family); NH-posimb, NH-AF4, NH-L3S (no harm on every
other family); SEL (which terms join MM1-v3.3); CX (the cross-card rule on T: PENDING until E220's data are committed and verified). REPORTED: per
family and forecaster errors, the pairs, the gemmLnc excess, the L3b deltas, family R's repeats against E218.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
S220_PIN = ("tools/claims-v3/e220/score_e220.py", "3c7719904cd3265b65c409475186f757fb00041cdab0a2e237c91ca665ac341f")
E220_PINS = {"tools/claims-v3/e220/points-e220.json": "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28",
             "tools/claims-v3/e220/forecast-e220.json": "dd31766796bc281ed47a56b8caf12465662e363eb2ec7dfaafd324a05fa78675",
             "tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.json": "3010f28c7e47e754a8bc4da5d0742e0d515c85da8d59e70a4ee3b798ccca1034",
             "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/forecasts-e220-af4.json": "37ace71c028a707ef07e9658cfdb2a4b3743ec0498b20b3bae93f79ac6af93e4",
             "tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.json": "ac65c9596f5611c95899b1c5105eee137602d5afbe00dfa316582ea651b753a8"}
E218_SCORES = ("docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/scores-e218-A.json", "b386d14a4a0e5094d779013323a7b34e4564ca843d1aa9b645c3dca76f56eba4")
E218_DATA = ("docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json", "31597c6025a732d3e541b2e8923ddd1b0a7b666fd7879987b74bd7132d982d8c")
POSIMB, AF4, L3S, COMBO = "MM1-v3.2 + posimb", "MM1-v3.2 + AF4", "MM1-v3.2 + L3S", "MM1-v3.2 + all three"
CANDS = (POSIMB, AF4, L3S)
MODELS = ("MM1-v3.2", "MM1-v3.1", "MM1-v3", "MM1-v2")
RULES_T = ("T1", "T2", "T3", "E1", "E2", "E3", "E4")
H2H = (("H1", "MM1-v3.2", "MM1-v3", "wall"), ("H2", "MM1-v3.2", "MM1-v3", "mean"), ("H3", "MM1-v3.2", "MM1-v3", "seconds"),
       ("H4", "MM1-v3.2", "MM1-v3", "Wg"), ("H5", "MM1-v3.2", "MM1-v3", "Jf"),
       ("H6", "MM1-v3.2", "MM1-v3.1", "wall"), ("H7", "MM1-v3.2", "MM1-v3.1", "mean"), ("H8", "MM1-v3.2", "MM1-v3.1", "seconds"),
       ("H9", "MM1-v3.2", "MM1-v3.1", "Wg"), ("H10", "MM1-v3.2", "MM1-v3.1", "Jf"))
HC = {"HC-posimb": POSIMB, "HC-AF4": AF4, "HC-L3S": L3S}
NH = {"NH-posimb": POSIMB, "NH-AF4": AF4, "NH-L3S": L3S}
CX_MODELS = ("MM1-v3.2", POSIMB, AF4, L3S, "MM1-v3.1", "MM1-v3", "MM1-v2")
CX_COL = {"A": "600.0", "B": "799.0"}
CX_F = {"A": 600.0, "B": 799.0}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_pinned(name, rel, want):
    p = os.path.join(REPO, rel)
    if sha(p) != want:
        print(f"score_e222: REFUSED, {rel} is not at its pin {want[:12]}")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


S220 = load_pinned("score_e220_pinned", *S220_PIN)
mean, rms, sign_p, verdict = S220.mean, S220.rms, S220.sign_p, S220.verdict


def load_frozen(check=True):
    sums = {}
    sp = os.path.join(HERE, "SHA256SUMS-e222-registration")
    if os.path.exists(sp):
        for ln in open(sp):
            if ln.strip() and not ln.startswith("#"):
                h, f = ln.split(None, 1)
                f = f.strip()
                if f.startswith("tools/claims-v3/e222/"):
                    f = f[len("tools/claims-v3/e222/"):]
                sums[f] = h
    for f in ("points-e222.json", "forecast-e222.json", "rules-e222.json"):
        if check and f in sums and sha(os.path.join(HERE, f)) != sums[f]:
            print(f"score_e222: REFUSED, {f} differs from SHA256SUMS-e222-registration")
            sys.exit(4)
    P = json.load(open(os.path.join(HERE, "points-e222.json")))
    F = json.load(open(os.path.join(HERE, "forecast-e222.json")))
    R = json.load(open(os.path.join(HERE, "rules-e222.json")))
    return P, F, R


def group(p):
    return p["subfamily"] if p["family"] == "T" else p["family"]


def plike(P):
    return {"points": {"A": P["points"], "B": []}}


# ------------------------------------------------------------------ the model side
def fcv(F, pid, model):
    return ((F["points"].get(pid) or {}).get("models") or {}).get(model) or {}


def predicted(x, m):
    o = {"wall": x.get("cycles_per_op_wall"), "mean": x.get("cycles_per_op_mean"), "seconds": x.get("seconds_per_gemm"), "W": x.get("W_over_idle")}
    if x.get("A_W") is not None and m.get("Top_e"):
        Wg = x["A_W"] + x["B_W_us"] / m["Top_e"]
        o.update({"Wg": Wg, "Jg": Wg * m["t_e"], "Wf": x["W_over_idle"], "Jf": x["J_over_idle_per_gemm"]})
        if m.get("prest") is not None:
            o["JRg"] = m["prest"] * m["t_e"] + Wg * m["t_e"]
            o["JRf"] = m["prest"] * x["seconds_per_gemm"] + x["J_over_idle_per_gemm"]
    return o


def watts_point(F, pid, m):
    w32 = fcv(F, pid, "MM1-v3.2").get("W_over_idle")
    return (w32 is not None and w32 < 3.0) or (m.get("W") is not None and m["W"] < 3.0)


def registered(P, M):
    reg = set(P_REG(P))
    return {pid: m for pid, m in M.items() if pid in reg and not m.get("ran_before")}


def P_REG(P):
    return [p["id"] for p in P["points"] if p["family"] in ("T", "L3b", "Y3", "G3", "G3t")]


def cells_of(M, F, R, model="MM1-v3.2"):
    B = {q: R["bands"][q]["band"] for q in RULES_T}
    BW = R["band_w"]["band_W"]
    cells = {q: {} for q in RULES_T}
    for pid, m in M.items():
        fc = predicted(fcv(F, pid, model), m)
        for q, mk, fk in (("T1", "wall", "wall"), ("T2", "mean", "mean"), ("T3", "t", "seconds")):
            if m.get(mk) and fc.get(fk):
                e = m[mk] / fc[fk] - 1.0
                cells[q][pid] = {"err": e, "pass": abs(e) <= B[q] + 1e-12}
        if m.get("W") is None or fc.get("Wg") is None:
            continue
        if watts_point(F, pid, m):
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


def h_cases(M, F, R, first, second, q, pids=None):
    ties = R["ties"]
    out = []
    for pid, m in M.items():
        if pids is not None and pid not in pids:
            continue
        a, b = predicted(fcv(F, pid, first), m), predicted(fcv(F, pid, second), m)
        if q in ("wall", "mean", "seconds"):
            mk = {"wall": "wall", "mean": "mean", "seconds": "t"}[q]
            if m.get(mk) and a.get(q) and b.get(q):
                out.append((abs(math.log(m[mk] / b[q])) - abs(math.log(m[mk] / a[q])), ties["seconds_ln" if q == "seconds" else "cycles_ln"], pid))
            continue
        if m.get("W") is None or a.get("Wg") is None or b.get("Wg") is None:
            continue
        fk = "Wg" if q == "Wg" else "Wf"
        if watts_point(F, pid, m):
            out.append((abs(m["W"] - b[fk]) - abs(m["W"] - a[fk]), ties["watts_W"], pid))
        elif q == "Wg":
            out.append((abs(math.log(m["W"] / b["Wg"])) - abs(math.log(m["W"] / a["Wg"])), ties["joules_ln"], pid))
        else:
            out.append((abs(math.log(m["J"] / b["Jf"])) - abs(math.log(m["J"] / a["Jf"])), ties["joules_ln"], pid))
    return out


def decide(cases, first, second, minimum=10, names=None):
    if not cases:
        return {"verdict": "NO DATA", "n": 0}
    npos = sum(1 for d, t, _ in cases if d > t)
    nneg = sum(1 for d, t, _ in cases if d < -t)
    res = {"n": len(cases), "first_closer": npos, "second_closer": nneg, "ties": len(cases) - npos - nneg, "minimum_decided": minimum}
    if npos + nneg < minimum:
        res["verdict"] = "TOO FEW"
        return res
    p = sign_p(npos, nneg)
    res["p"] = p
    nm = names or (first + " BETTER", second + " BETTER")
    res["verdict"] = (nm[0] if npos > nneg else nm[1]) if p < 0.05 else "NOT DECIDED"
    return res


def pairs(P, groups):
    by = {}
    for p in P["points"]:
        if group(p) in groups and p.get("pair"):
            by.setdefault(p["pair"], {})[p["pair_role"]] = p["id"]
    return {k: v for k, v in sorted(by.items()) if set(v) == {"a", "b"}}


def pair_cases(M, F, R, cand, groups):
    out, rows = [], []
    for pr, d in pairs(P_GLOBAL[0], groups).items():
        a, b = d["a"], d["b"]
        if a not in M or b not in M:
            continue
        r = math.log(M[a]["wall"] / M[b]["wall"])
        dv = math.log(fcv(F, a, "MM1-v3.2")["cycles_per_op_wall"] / fcv(F, b, "MM1-v3.2")["cycles_per_op_wall"])
        dc = math.log(fcv(F, a, cand)["cycles_per_op_wall"] / fcv(F, b, cand)["cycles_per_op_wall"])
        out.append((abs(r - dv) - abs(r - dc), R["ties"]["cycles_ln"], pr))
        rows.append({"pair": pr, "a": a, "b": b, "measured_ln_a_over_b": r, "v32_ln_a_over_b": dv, "cand_ln_a_over_b": dc})
    return out, rows


P_GLOBAL = [None]


def nh_rule(M, F, R, P, cand):
    nh = [v for v in R["no_harm"].values() if v["candidate"] == cand][0]
    margin, nmin = nh["margin_pct"], nh["min_points"]
    out = {"margin_pct": margin, "min_points": nmin, "groups": {}}
    grp = {p["id"]: group(p) for p in P["points"]}
    worst = None
    evaluated = 0
    for g in nh["other_families"]:
        ids = [pid for pid in M if grp.get(pid) == g]
        ew_c, ew_v, ee_c, ee_v = [], [], [], []
        for pid in ids:
            m = M[pid]
            c, v = predicted(fcv(F, pid, cand), m), predicted(fcv(F, pid, "MM1-v3.2"), m)
            if m.get("wall") and c.get("wall") and v.get("wall"):
                ew_c.append(math.log(m["wall"] / c["wall"]))
                ew_v.append(math.log(m["wall"] / v["wall"]))
            if m.get("W") and c.get("Wg") and v.get("Wg") and m["W"] >= 3.0 and v["Wg"] >= 3.0 and c["Wg"] >= 3.0:
                ee_c.append(math.log(m["W"] / c["Wg"]))
                ee_v.append(math.log(m["W"] / v["Wg"]))
        rec = {"n_wall": len(ew_c), "n_Wg": len(ee_c)}
        fails = []
        for q, xc, xv in (("wall", ew_c, ew_v), ("Wg", ee_c, ee_v)):
            if len(xc) >= nmin:
                dc, dv = 100 * rms(xc), 100 * rms(xv)
                rec[f"{q}_rms_cand_pct"], rec[f"{q}_rms_v32_pct"], rec[f"{q}_excess_pct"] = dc, dv, dc - dv
                evaluated += 1
                if dc - dv > margin + 1e-12:
                    fails.append(q)
                worst = max(worst if worst is not None else -1e9, dc - dv)
        rec["fails"] = fails
        out["groups"][g] = rec
    any_fail = any(r["fails"] for r in out["groups"].values())
    out["verdict"] = "NO DATA" if evaluated == 0 else ("FAIL" if any_fail else "PASS")
    out["worst_excess_pct"] = worst
    return out


# ------------------------------------------------------------------ the cross-card rule (E220's side read at scoring only)
def e220_side():
    for rel, want in E220_PINS.items():
        if sha(os.path.join(REPO, rel)) != want:
            print(f"score_e222: REFUSED, {rel} is not at its pin")
            sys.exit(4)
    P220 = json.load(open(os.path.join(REPO, "tools/claims-v3/e220/points-e220.json")))
    F220 = json.load(open(os.path.join(REPO, "tools/claims-v3/e220/forecast-e220.json")))
    cand = {}
    J = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.3-cands/posimb/forecasts-e220-posimb.json")))
    for r in J["rows"]:
        cand[(POSIMB, r["arm"], float(r["f_mhz"]), r["id"])] = {k.split("|", 1)[1]: v for k, v in r.items() if k.startswith(J["label"] + "|")}
    J = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.3-cands/gemmlnc-af4/forecasts-e220-af4.json")))
    for r in J["rows"]:
        cand[(AF4, r["arm"], float(r["f_mhz"]), r["id"])] = {"cycles_per_op_wall": r["cycles_per_op_wall"], "cycles_per_op_mean": r["cycles_per_op_mean"],
                                                           "seconds_per_gemm": r["seconds_per_gemm"], "W_over_idle": r["W_over_idle"], "A_W": r["A_W"],
                                                           "B_W_us": r["B_W_us"], "J_over_idle_per_gemm": r["J_over_idle_per_gemm_t_forecast"]}
    J = json.load(open(os.path.join(REPO, "tools/matmul/mm1/v3.3-cands/l3s/forecasts-e220-l3s.json")))
    lab = [k for k in J["rows"][0]["models"] if k != "MM1-v3.2"][0]
    for r in J["rows"]:
        x = r["models"][lab]
        cand[(L3S, r["arm"], float(r["f_mhz"]), r["id"])] = {"cycles_per_op_wall": x["cycles_per_op_wall"], "cycles_per_op_mean": x["cycles_per_op_mean"],
                                                           "seconds_per_gemm": x["seconds_per_gemm"], "W_over_idle": x["W_over_idle"], "A_W": x["A_W"],
                                                           "B_W_us": x["B_W_us"], "J_over_idle_per_gemm": x["J_over_idle_per_gemm"]}
    return P220, F220, cand


def f220(F220, cand, arm, e220_id, model):
    if model in CANDS:
        return cand.get((model, arm, CX_F[arm], e220_id)) or {}
    return ((F220["arms"][arm]["points"].get(e220_id) or {}).get("clocks", {}).get(CX_COL[arm]) or {}).get(model) or {}


def cx_rule(M, F, R, P, e220):
    if e220 is None:
        return {"verdict": "PENDING E220 DATA", "why": "scored only once E220's data are committed and verified (rules-e222.json > cross_card)"}
    P220, F220, cand, MX = e220
    ties = R["ties"]
    twins = [p for p in P["points"] if p["family"] == "T"]
    out = {}
    for model in CX_MODELS:
        pooled = {"wall": [], "Wg": []}
        for arm in ("A", "B"):
            cs = {"wall": [], "Wg": []}
            for p in twins:
                pid, xid = p["id"], p["e220_id"]
                ma, mx = M.get(pid), MX[arm].get(xid)
                if not ma or not mx:
                    continue
                fa, fx = predicted(fcv(F, pid, model), ma), predicted(f220(F220, cand, arm, xid, model), mx)
                if ma.get("wall") and mx.get("wall") and fa.get("wall") and fx.get("wall"):
                    cs["wall"].append((abs(math.log(ma["wall"] / fa["wall"])) - abs(math.log(mx["wall"] / fx["wall"])), ties["cycles_ln"], f"{arm}:{pid}"))
                if (ma.get("W") and mx.get("W") and fa.get("Wg") and fx.get("Wg") and ma["W"] >= 3.0 and mx["W"] >= 3.0 and fa["Wg"] >= 3.0
                        and fx["Wg"] >= 3.0):
                    cs["Wg"].append((abs(math.log(ma["W"] / fa["Wg"])) - abs(math.log(mx["W"] / fx["Wg"])), ties["joules_ln"], f"{arm}:{pid}"))
            for q in ("wall", "Wg"):
                out[f"CX-{'T' if q == 'wall' else 'E'}|{model}|{arm}"] = decide(cs[q], "a3", "x", minimum=10,
                                                                                names=("LARGER ON aifoundry3", "SMALLER ON aifoundry3"))
                pooled[q] += cs[q]
        for q in ("wall", "Wg"):
            out[f"CXP-{'T' if q == 'wall' else 'E'}|{model}"] = decide(pooled[q], "a3", "x", minimum=10, names=("LARGER ON aifoundry3", "SMALLER ON aifoundry3"))
    return out


# ------------------------------------------------------------------ the REPORTED readings
def family_stats(M, F, P, names):
    grp = {p["id"]: (p["family"], group(p)) for p in P["points"]}
    out = {}
    for model in names:
        acc = {}
        for pid, m in M.items():
            f, g = grp.get(pid, ("?", "?"))
            fc = predicted(fcv(F, pid, model), m)
            for k in sorted({f, g, "all registered" if f != "R" else "R"}):
                d = acc.setdefault(k, {"wall": [], "Wg": []})
                if m.get("wall") and fc.get("wall"):
                    d["wall"].append(math.log(m["wall"] / fc["wall"]))
                if m.get("W") and fc.get("Wg") and m["W"] >= 3 and fc["Wg"] >= 3:
                    d["Wg"].append(math.log(m["W"] / fc["Wg"]))
        out[model] = {k: {q: {"n": len(v), "rms_pct": (100 * rms(v) if v else None), "bias_pct": (100 * mean(v) if v else None)} for q, v in d.items()}
                      for k, d in sorted(acc.items())}
    return out


def readings(M, F, P):
    pts = {p["id"]: p for p in P["points"]}
    rd = {}
    g = []
    for pid, p in pts.items():
        if p["family"] in ("G3",) or p["subfamily"] in ("T-G2", "R-G"):
            t = p.get("twin")
            if pid in M and t in M and M[pid].get("W") is not None and M[t].get("W") is not None:
                x32, xa = fcv(F, pid, "MM1-v3.2"), fcv(F, pid, AF4)
                g.append({"id": pid, "twin": t, "token": p["token"], "measured_excess_W": M[pid]["W"] - M[t]["W"],
                          "F3_W_MM1_v32": (xa.get("term") or {}).get("MM1-v3.2_F3_W"), "AF4_W": (xa.get("term") or {}).get("term_AF4_W")})
    rd["gemmLnc_excess"] = {"points": g, "how": "per gemmLnc point the measured W over idle less its twin's against MM1-v3.2's F3 and AF4's term; REPORTED"}
    l3 = []
    for pid, p in pts.items():
        if p["family"] == "L3b" or p["subfamily"] == "T-L3":
            if pid in M:
                a, b = fcv(F, pid, "MM1-v3.2"), fcv(F, pid, L3S)
                l3.append({"id": pid, "token": p["token"], "subfamily": p["subfamily"], "ln_err_wall_v32": math.log(M[pid]["wall"] / a["cycles_per_op_wall"]),
                           "ln_err_wall_L3S": math.log(M[pid]["wall"] / b["cycles_per_op_wall"]), "L3S_delta_ln": math.log(b["cycles_per_op_wall"] / a["cycles_per_op_wall"])})
    rd["L3"] = {"points": l3, "how": "ln(measured / forecast) of the wall cycles at L3b and T-L3, MM1-v3.2 and L3S; REPORTED"}
    return rd


def repeats_r(M, P):
    if sha(os.path.join(REPO, E218_SCORES[0])) != E218_SCORES[1]:
        return {"verdict": "REFUSED: E218's scores not at their pin"}
    S = json.load(open(os.path.join(REPO, E218_SCORES[0])))["measured"]
    out = {}
    for p in P["points"]:
        if p["family"] != "R":
            continue
        m, e = M.get(p["id"]), S.get(p["e218_id"])
        if not m or not e:
            out[p["id"]] = "NO DATA"
            continue
        out[p["id"]] = {"e218_id": p["e218_id"], "ln_wall_E222_over_E218": math.log(m["wall"] / e["cw"]) if e.get("cw") else None,
                        "ln_mean_E222_over_E218": math.log(m["mean"] / e["cm"]) if (e.get("cm") and m.get("mean")) else None,
                        "ln_W_E222_over_E218": math.log(m["W"] / e["W"]) if (e.get("W") and m.get("W") and m["W"] > 0 and e["W"] > 0) else None}
    return out


def score(dA, P, F, R, labels=None, tag="A", e220=None):
    labels = labels or {}
    P_GLOBAL[0] = P
    Mall, _, flags, r0, s6, has = S220.read_a(dA or {}, plike(P), tag, labels)
    M = registered(P, Mall)
    out = {"experiment": "E222", "flags": flags, "measured": Mall, "rules": {}, "head_to_head": {}, "candidates": {}, "no_harm": {}}
    out["rules"]["R0"] = {"verdict": ("NO DATA" if not has else ("PASS" if not r0 else "FAIL")), "failures": r0}
    out["rules"]["S6"] = {"verdict": ("NO DATA" if not has else ("PASS" if not s6 else "FAIL")), "failures": s6}
    label = None
    if out["rules"]["R0"]["verdict"] == "FAIL" or out["rules"]["S6"]["verdict"] == "FAIL":
        label = "labelled: " + ("R0 FAIL" if out["rules"]["R0"]["verdict"] == "FAIL" else "S6 FAIL")
    cells = cells_of(M, F, R)
    for q in RULES_T:
        v = verdict(cells[q])
        if label and v["verdict"] != "NO DATA":
            v["label"] = label
        out["rules"][q] = v
    out["cells"] = cells
    for hid, x, y, q in H2H:
        v = decide(h_cases(M, F, R, x, y, q), x, y, minimum=R["head_to_head"][hid]["minimum_decided"])
        if label:
            v["label"] = label
        out["head_to_head"][hid] = v
    grp = {p["id"]: group(p) for p in P["points"]}
    for rid, cand in HC.items():
        hr = R["candidate_head_to_head"][rid]
        if hr["quantity"] == "pair":
            cs, rows = pair_cases(M, F, R, cand, hr["own_family"])
            v = decide(cs, cand, "MM1-v3.2", minimum=hr["minimum_decided"])
            v["pairs"] = rows
        else:
            ids = {pid for pid in M if grp.get(pid) in hr["own_family"]}
            v = decide(h_cases(M, F, R, cand, "MM1-v3.2", hr["quantity"], ids), cand, "MM1-v3.2", minimum=hr["minimum_decided"])
        if label:
            v["label"] = label
        out["candidates"][rid] = v
    for rid, cand in NH.items():
        v = nh_rule(M, F, R, P, cand)
        if label:
            v["label"] = label
        out["no_harm"][rid] = v
    joins = [c for c in CANDS if out["candidates"]["HC-" + c.split("+ ")[1]]["verdict"] == f"{c} BETTER"
             and out["no_harm"]["NH-" + c.split("+ ")[1]]["verdict"] == "PASS"]
    out["selection"] = {"verdict": ("MM1-v3.3 = MM1-v3.2" + "".join(" + " + c.split("+ ")[1] for c in joins)) if (has and M) else "NO DATA",
                        "joining_terms": joins, "composition": ("the registered combination restricted to the joining terms (desk/models_e222.compose)"
                                                                if len(joins) >= 2 else ("one term" if joins else "none: MM1-v3.3 = MM1-v3.2 unchanged")),
                        "label": label}
    out["cross_card"] = cx_rule(M, F, R, P, e220)
    out["family_stats_REPORTED"] = family_stats(Mall, F, P, F["forecasters"])
    out["readings_REPORTED"] = readings(M, F, P)
    out["family_R_repeats_REPORTED"] = repeats_r(Mall, P)
    out["label"] = label
    out["verdicts"] = {k: v["verdict"] for k, v in out["rules"].items()}
    out["verdicts"].update({k: v["verdict"] for k, v in out["head_to_head"].items()})
    out["verdicts"].update({k: v["verdict"] for k, v in out["candidates"].items()})
    out["verdicts"].update({k: v["verdict"] for k, v in out["no_harm"].items()})
    out["verdicts"]["SEL"] = out["selection"]["verdict"]
    if isinstance(out["cross_card"], dict) and "verdict" in out["cross_card"]:
        out["verdicts"]["CX"] = out["cross_card"]["verdict"]
    else:
        out["verdicts"].update({k: v["verdict"] for k, v in out["cross_card"].items()})
    return out


# ------------------------------------------------------------------ the self-tests: stand-in days in the reader's form
def truth_of(F, pid, model):
    x = fcv(F, pid, model)
    return {"wall": x["cycles_per_op_wall"], "mean": x["cycles_per_op_mean"], "t": x["seconds_per_gemm"], "T": x["T_op_us"], "W": x.get("W_over_idle"),
            "prest": fcv(F, pid, "MM1-v3.2").get("rest_law_W"), "A": x.get("A_W"), "B": x.get("B_W_us")}


def make(P, F, fn, mutate=None):
    return S220.make_a(plike(P), F, (lambda arm, p: fn(p)), mutate)


def selftest_standins(out_path):
    P, F, R = load_frozen(check=False)
    P_GLOBAL[0] = P
    grp = {p["id"]: group(p) for p in P["points"]}

    def model_truth(model, tscale=1.0, wscale=1.0, per=None):
        def fn(p):
            mdl = (per or {}).get(grp.get(p["id"]), model)
            tr = truth_of(F, p["id"], mdl)
            if tr["W"] is None:
                return None
            if tscale != 1.0:
                for q in ("wall", "mean", "t", "T"):
                    tr[q] *= tscale
                t32 = truth_of(F, p["id"], "MM1-v3.2")
                tr["W"] = t32["A"] + t32["B"] / tr["T"]
            tr["W"] *= wscale
            return tr
        return fn

    def nh_fail_truth(p):
        """L3S right on its own family; at G3 and G3t the truth moves AWAY from L3S's direction by L3S's own move (so L3S's rms there rises
        by about twice its move, past the margin), MM1-v3.2's energy kept"""
        g = grp.get(p["id"])
        if g in ("L3b", "T-L3"):
            return model_truth(L3S)(p)
        tr = model_truth("MM1-v3.2")(p)
        if g in ("G3", "G3t") and tr:
            k = fcv(F, p["id"], L3S)["cycles_per_op_wall"] / fcv(F, p["id"], "MM1-v3.2")["cycles_per_op_wall"]
            for q in ("wall", "mean", "t", "T"):
                tr[q] /= k
            tr["W"] = tr["A"] + tr["B"] / tr["T"]
        return tr

    def badcheck(d):
        k = sorted(d["arms"]["A"]["points"])[0]
        d["arms"]["A"]["points"][k]["runs"][0]["checks"] = ["wrong"]

    def at700(p):
        tr = model_truth("MM1-v3.2")(p)
        if tr:
            tr["mhz"] = 700
        return tr
    all_h = {f"H{i}": "MM1-v3.2 BETTER" for i in range(1, 11)}
    days = {
        "v32": ("every point at MM1-v3.2's frozen forecast, the rest at its rest law", make(P, F, model_truth("MM1-v3.2")),
                dict({q: "PASS" for q in ("R0", "S6") + RULES_T}, **all_h, **{"HC-posimb": "MM1-v3.2 BETTER", "HC-AF4": "MM1-v3.2 BETTER",
                     "HC-L3S": "MM1-v3.2 BETTER", "NH-posimb": "PASS", "NH-AF4": "PASS", "NH-L3S": "FAIL", "SEL": "MM1-v3.3 = MM1-v3.2",
                     "CX": "PENDING E220 DATA"})),
        "all3": ("every point at 'MM1-v3.2 + all three' (the registered combination)", make(P, F, model_truth(COMBO)),
                 {"HC-posimb": f"{POSIMB} BETTER", "HC-AF4": f"{AF4} BETTER", "HC-L3S": f"{L3S} BETTER", "NH-posimb": "PASS", "NH-AF4": "PASS",
                  "NH-L3S": "PASS", "SEL": "MM1-v3.3 = MM1-v3.2 + posimb + AF4 + L3S"}),
        "posimb": ("every point at 'MM1-v3.2 + posimb'", make(P, F, model_truth(POSIMB)),
                   {"HC-posimb": f"{POSIMB} BETTER", "HC-AF4": "MM1-v3.2 BETTER", "HC-L3S": "MM1-v3.2 BETTER", "NH-posimb": "PASS",
                    "SEL": "MM1-v3.3 = MM1-v3.2 + posimb"}),
        "af4": ("every point at 'MM1-v3.2 + AF4'", make(P, F, model_truth(AF4)),
                {"HC-AF4": f"{AF4} BETTER", "HC-posimb": "MM1-v3.2 BETTER", "NH-AF4": "PASS", "SEL": "MM1-v3.3 = MM1-v3.2 + AF4"}),
        "l3s": ("every point at 'MM1-v3.2 + L3S'", make(P, F, model_truth(L3S)),
                {"HC-L3S": f"{L3S} BETTER", "HC-AF4": "MM1-v3.2 BETTER", "NH-L3S": "PASS", "SEL": "MM1-v3.3 = MM1-v3.2 + L3S"}),
        "nhfail": ("L3S right on its own family, harmful past the margin at G3 and G3t", make(P, F, nh_fail_truth),
                   {"HC-L3S": f"{L3S} BETTER", "NH-L3S": "FAIL", "SEL": "MM1-v3.3 = MM1-v3.2"}),
        "v3": ("every point at MM1-v3's", make(P, F, model_truth("MM1-v3")), {f"H{i}": "MM1-v3 BETTER" for i in range(1, 6)}),
        "v31": ("every point at MM1-v3.1's", make(P, F, model_truth("MM1-v3.1")), {f"H{i}": "MM1-v3.1 BETTER" for i in range(6, 11)}),
        "t150": ("MM1-v3.2's cycles and seconds x 1.5, its energy exact given the op time", make(P, F, model_truth("MM1-v3.2", tscale=1.5)),
                 {"T1": "FAIL", "T2": "FAIL", "T3": "FAIL", "E1": "PASS", "E3": "PASS", "E4": "FAIL"}),
        "w150": ("MM1-v3.2's W over idle x 1.5", make(P, F, model_truth("MM1-v3.2", wscale=1.5)), {"T1": "PASS", "E1": "FAIL", "E2": "FAIL", "E3": "FAIL", "E4": "FAIL"}),
        "badcheck": ("one run's check of C wrong", make(P, F, model_truth("MM1-v3.2"), badcheck), {"R0": "FAIL", "SEL": "MM1-v3.3 = MM1-v3.2"}),
        "at700": ("every run at 700 MHz", make(P, F, at700), {"S6": "FAIL"}),
        "nodata": ("no data", {}, {"R0": "NO DATA", "T1": "NO DATA", "E1": "NO DATA", "H1": "NO DATA", "HC-posimb": "NO DATA", "HC-AF4": "NO DATA",
                                   "HC-L3S": "NO DATA", "NH-L3S": "NO DATA", "SEL": "NO DATA"}),
    }
    res, ok = {}, True
    for name, (what, dA, want) in days.items():
        S = score(dA, P, F, R)
        got = {k: S["verdicts"].get(k) for k in want}
        good = {k: (got[k] == w) for k, w in want.items()}
        day_ok = all(good.values())
        ok &= day_ok
        res[name] = {"what": what, "ok": day_ok, "checks": {k: {"got": got[k], "want": w, "ok": good[k]} for k, w in want.items()},
                     "selection": S["selection"]}
    # the cross-card rule: E220's side as stand-ins in E220's readers' forms (its frozen scorer's make_a and make_b), E222's beside
    P220, F220, cand = e220_side()
    twins = {p["e220_id"]: p["id"] for p in P["points"] if p["family"] == "T"}

    def e_of(i):
        return 0.03 * (1 + (i % 5)) * (1 if i % 2 else -1)
    idx = {x: i for i, x in enumerate(sorted(twins))}

    def x_truth(arm, p):
        x = f220(F220, cand, arm, p["id"], "MM1-v3.2")
        if not x or x.get("W_over_idle") is None:
            return None
        g = math.exp(e_of(idx[p["id"]])) if p["id"] in idx else 1.0
        T = x["T_op_us"] * g if "T_op_us" in x else (x["cycles_per_op_wall"] * g / CX_F[arm])
        W = (x["A_W"] + x["B_W_us"] / T) * g
        rest = (((F220["arms"][arm]["points"].get(p["id"]) or {}).get("clocks", {}).get(CX_COL[arm]) or {}).get("MM1-v3.2") or {}).get("rest_law_W") or 25.0
        return {"wall": x["cycles_per_op_wall"] * g, "mean": x["cycles_per_op_mean"] * g, "t": x["seconds_per_gemm"] * g, "T": T, "W": W, "prest": rest,
                "mhz": 600 if arm == "A" else 799.0}

    def a3_truth(k):
        def fn(p):
            tr = model_truth("MM1-v3.2")(p)
            if tr and p["family"] == "T":
                g = math.exp(k * e_of(idx[p["e220_id"]]))
                for q in ("wall", "mean", "t", "T"):
                    tr[q] *= g
                tr["W"] = (tr["A"] + tr["B"] / tr["T"]) * g
            return tr
        return fn
    dXa = S220.make_a(P220, F220, x_truth)
    dXb = S220.make_b(P220, F220, x_truth)
    MXa = S220.read_a(dXa, P220, "A", {})[0]
    MXb = S220.read_b(dXb, P220, {})[0]
    cx_days = {"cx_equal": (1.0, {f"CXP-T|MM1-v3.2": "TOO FEW", f"CX-T|MM1-v3.2|A": "TOO FEW", f"CX-T|MM1-v3.2|B": "TOO FEW"}),
               "cx_larger": (3.0, {f"CXP-T|MM1-v3.2": "LARGER ON aifoundry3", f"CX-T|MM1-v3.2|A": "LARGER ON aifoundry3",
                                   f"CX-T|MM1-v3.2|B": "LARGER ON aifoundry3", f"CXP-E|MM1-v3.2": "LARGER ON aifoundry3"}),
               "cx_smaller": (0.2, {f"CXP-T|MM1-v3.2": "SMALLER ON aifoundry3", f"CX-T|MM1-v3.2|A": "SMALLER ON aifoundry3",
                                    f"CXP-E|MM1-v3.2": "SMALLER ON aifoundry3"})}
    for name, (k, want) in cx_days.items():
        S = score(make(P, F, a3_truth(k)), P, F, R, e220=(P220, F220, cand, {"A": MXa, "B": MXb}))
        got = {q: S["verdicts"].get(q) for q in want}
        good = {q: got[q] == w for q, w in want.items()}
        day_ok = all(good.values()) and all(f"CXP-T|{m}" in S["verdicts"] for m in CX_MODELS)
        ok &= day_ok
        res[name] = {"what": f"aifoundry3's MM1-v3.2 error {k} x E220's at every T twin (E220's side: stand-ins in its readers' forms)", "ok": day_ok,
                     "checks": {q: {"got": got[q], "want": w, "ok": good[q]} for q, w in want.items()}}
    covered = {}
    for r in res.values():
        for kk, c in r["checks"].items():
            covered.setdefault(kk.split("|")[0], set()).add(c["got"])
    rec = {"what": "score_e222.py's self-test on stand-in days in E218's reader form (E215 arm A's), the cross-card rule's E220 side in E220's readers' forms",
           "verdict": "PASS" if ok else "FAIL", "days": res, "verdicts_seen_by_rule": {k: sorted(v) for k, v in covered.items()}}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-standins: {rec['verdict']} ({sum(1 for r in res.values() if r['ok'])} of {len(res)} days)")
    for name, r in res.items():
        if not r["ok"]:
            print("  FAILED", name, {k: v for k, v in r["checks"].items() if not v["ok"]})
    return ok


def selftest_real(out_path):
    """the reader on real committed bytes from this card: E218's data (aifoundry3 card 0, E215 arm A's form), its points standing in"""
    if sha(os.path.join(REPO, E218_DATA[0])) != E218_DATA[1]:
        print("selftest-real: REFUSED, E218's data not at its pin")
        return False
    d = json.load(open(os.path.join(REPO, E218_DATA[0])))
    e218 = json.load(open(os.path.join(REPO, "tools", "claims-v3", "e218", "points-e218.json")))["points"]
    PA = {"points": {"A": [{"id": p["id"], "arm": p["arm"], "format": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"],
                            "host": p["host"], "ops_per_minion_per_gemm": p["ops_per_minion_per_gemm"], "loop": p["loop"], "family": p["family"]}
                           for p in e218 if p.get("role", "point") == "point" or p["family"] in ("G", "Gt", "Y", "F")], "B": []}}
    MA, _, fa, r0a, s6a, _ = S220.read_a(d, PA, "A", {})
    n_reg = len(PA["points"]["A"])
    okA = len(MA) >= n_reg - 1 and not s6a and all(m.get("W") is not None for m in MA.values())
    rec = {"what": "score_e222's reader (score_e220.read_a at its pin) on real committed bytes from aifoundry3 card 0", "input": E218_DATA[0], "sha256": E218_DATA[1],
           "points_read": len(MA), "points_registered": n_reg, "R0_failures_REPORTED": r0a, "S6_failures": s6a, "flags": fa[:20],
           "note": "E218's R0 FAIL (f04 run 77: its check of C cut off by the plain timeout) is read here as R0 failures, as E218's own scorer read it",
           "verdict": "OK" if okA else "NOT OK"}
    json.dump(rec, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-real: {rec['verdict']} (reader {len(MA)}/{n_reg} points, R0 failures {len(r0a)} (E218's own), S6 {len(s6a)})")
    return okA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a")
    ap.add_argument("--a-tag", default="A")
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--e220-a")
    ap.add_argument("--e220-b", action="append", default=[])
    ap.add_argument("--e220-labels")
    ap.add_argument("--e220-verified")
    ap.add_argument("--selftest-standins", action="store_true")
    ap.add_argument("--selftest-real", action="store_true")
    a = ap.parse_args()
    if a.selftest_standins:
        sys.exit(0 if selftest_standins(os.path.join(HERE, "selftest-standins.json")) else 1)
    if a.selftest_real:
        sys.exit(0 if selftest_real(os.path.join(HERE, "selftest-real.json")) else 1)
    P, F, R = load_frozen()
    dA = json.load(open(a.a)) if a.a else {}
    labels = json.load(open(a.labels)) if a.labels else {}
    e220 = None
    if a.e220_a or a.e220_b:
        if not (a.e220_a and a.e220_b and a.e220_verified and os.path.exists(a.e220_verified)):
            print("score_e222: the cross-card rule needs both E220 arms' committed data and the verify lane's result (--e220-verified): PENDING")
        else:
            P220, F220, cand = e220_side()
            l220 = json.load(open(a.e220_labels)) if a.e220_labels else {}
            MXa = S220.read_a(json.load(open(a.e220_a)), P220, "A", l220)[0]
            MXb = S220.read_b([json.load(open(x)) for x in a.e220_b], P220, l220)[0]
            e220 = (P220, F220, cand, {"A": MXa, "B": MXb})
    S = score(dA, P, F, R, labels, a.a_tag, e220)
    os.makedirs(a.out, exist_ok=True)
    json.dump(S, open(os.path.join(a.out, "scores-e222.json"), "w"), indent=1, sort_keys=True, default=str)
    lines = [f"{k}: {v}" for k, v in sorted(S["verdicts"].items())]
    open(os.path.join(a.out, "scores-e222.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
