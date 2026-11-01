#!/usr/bin/env python3
"""E112b scorer (Q133): E95's frozen claims C1-C12 on E112's (b) passes (E95's pass on aifoundry1 card 1), on the card-1
view of Q132(r)'s frozen file, and E112b's cross-card rules X1, X4 and X5 against E95's committed reductions of aifoundry3.

    python3 tools/claims-v3/e112/score_e112b.py --e112b e112b.json [--arm dips_kept=e112b-dipskept.json ...]
        [--e112a <(a)'s primary reduction, for the same-session tie>] --json scored.json --md results.md

The claims are scored by score_e95.py's own functions (score_e95.score) UNCHANGED, fed the card-1 view
(predictions-real2-card1.json: every watt figure a claim reads divided by E82's per-type card scale) and a session tie
against E82's card-1 cells. C7 and C8 carry a threshold in score_e95.py's code (+-0.40 W, 0.5 W): they are re-scored here by
ports whose only change is that threshold, scaled the same way (the view's e112_threshold_w). Beside every verdict, labelled
and never a verdict: the same claim at the frozen file's thresholds unscaled. Fewer than 3 kept passes: every claim NOT
SCORED. It refuses to score if a frozen input differs from predictions-e112.json's sha256 (a frozen file that changed in the
working copy is read from its recorded commit). Standard library only.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, K)
REG = os.path.join(HERE, "predictions-e112.json")
TYPES = ("fp32", "fp16", "int8")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
PASS, FAIL, INC, UNDER, NOTSC = "PASS", "FAIL", "INCONCLUSIVE", "UNDER-RESOLVED", "NOT SCORED"


def sha_b(b):
    return hashlib.sha256(b).hexdigest()


def frozen_bytes(v):
    p = os.path.join(ROOT, v["path"])
    if os.path.exists(p):
        b = open(p, "rb").read()
        if sha_b(b) == v["sha256"]:
            return b, "working copy"
    if v.get("commit"):
        r = subprocess.run(["git", "-C", ROOT, "show", f"{v['commit']}:{v['path']}"], capture_output=True)
        if r.returncode == 0 and sha_b(r.stdout) == v["sha256"]:
            return r.stdout, f"git show {v['commit']}"
    return None, "missing or changed"


def load_frozen(v):
    b, _ = frozen_bytes(v)
    return json.loads(b)


# ---- the two ports: score_e95.c7 and .c8 with the threshold read from the view, nothing else changed --------------

def c7_port(s95, V, c, F):
    thr = c["e112_threshold_w"]
    ref = c["reference"]
    offs = {t: s95.mc(V.diff_series(s95.e95.item_of(t), ref)) for t in c["predicted_offsets_w"]}
    tok, p999, p9999 = offs["int8/gpt2_l6_down_per_token"], offs["int8/gpt2_l6_down_p999"], offs["int8/gpt2_l6_down_p9999"]
    ok = s95.ok
    if not (ok(tok) and ok(p999) and ok(p9999)):
        v = UNDER
    elif tok["hi"] < 0 or p999["hi"] < 0 or p9999["lo"] > thr or p9999["hi"] < -thr:
        v = FAIL
    elif tok["lo"] > 0 and p999["lo"] > 0 and p9999["lo"] >= -thr and p9999["hi"] <= thr:
        v = PASS
    else:
        v = INC
    names = list(c["predicted_offsets_w"])
    pred = [0.0] + [c["predicted_offsets_w"][t] for t in names]
    meas = [0.0] + [offs[t]["mean"] for t in names] if all(ok(offs[t]) for t in names) else None
    return {"offsets_w": offs, "predicted_offsets_w": c["predicted_offsets_w"], "threshold_w": thr, "verdict": v,
            "spearman_over_four_reported": None if meas is None else s95.spearman(pred, meas),
            "r_reported": {t: s95.mc(V.r_series(s95.e95.item_of(t))) for t in names} | {ref: s95.mc(V.r_series(ref))},
            "D_reported": {t: V.D(s95.e95.item_of(t)) for t in names} | {ref: V.D(ref)}}


def c8_port(s95, V, c, F):
    thr = c["e112_threshold_w"]
    a, b = (s95.e95.item_of(t) for t in c["pair"])
    m = s95.mc(V.diff_series(a, b))
    v = UNDER if not s95.ok(m) else (PASS if m["lo"] > thr else (FAIL if m["hi"] < 0 else INC))
    return {"diff_w": m, "predicted_w": c["predicted_w"], "threshold_w": thr, "verdict": v}


PORTS = {"C7": ("C7_calibration_rank", c7_port), "C8": ("C8_asym_turns_the_gate_off", c8_port)}


def score_claims(s95, res, G, F, reg95):
    """score_e95.score on the card-1 view G, then C7 and C8 by the ports; beside, the verdicts at the frozen file F."""
    sc = s95.score(res, G, reg95)
    V = s95.View(res)
    enough = len(V.passes) >= s95.MIN_PASSES
    for short, (key, fn) in PORTS.items():
        rv = fn(s95, V, G["claims"]["E95"][key], G)
        rv["claim"] = G["claims"]["E95"][key]["claim"]
        if not enough:
            rv["verdict_from_too_few_passes"] = rv["verdict"]
            rv["verdict"] = NOTSC
        sc["claims"][short] = rv
    un = s95.score(res, F, reg95)
    for k, v in sc["claims"].items():
        v["at_frozen_thresholds_unscaled_labelled"] = un["claims"][k]["verdict"]
    return sc


# ---- the cross-card rules ------------------------------------------------------------------------------------------

def item_mean(s95, res, n):
    return s95.View(res).D(n)


def r_mean(s95, res, n):
    return s95.mc(s95.View(res).r_series(n))


def cross(s95, c1, a3, X, pool):
    enough = len(c1.get("passes", [])) >= X["min_passes_each"] and len(a3.get("passes", [])) >= X["min_passes_each"]
    rows = {}
    for n in sorted(set(pool) | set(REF.values())):
        d1, d3 = item_mean(s95, c1, n), item_mean(s95, a3, n)
        res_ = s95.ok(d1) and s95.ok(d3)
        row = {"D_card1": d1, "D_aifoundry3": d3, "resolved": res_,
               "ratio_a3_over_c1": (d3["mean"] / d1["mean"]) if res_ and d1["mean"] else None}
        if n in pool:
            r1, r3 = r_mean(s95, c1, n), r_mean(s95, a3, n)
            ty = n.split(".", 1)[0]
            rr = s95.ok(r1) and s95.ok(r3)
            row.update({"r_card1": r1, "r_aifoundry3": r3, "r_resolved": rr,
                        "r_diff": (r1["mean"] - r3["mean"]) if rr else None,
                        "r_diff_ci95_quadrature": math.hypot(r1["ci95"], r3["ci95"]) if rr else None,
                        "r_band": X["X5"]["band"][ty],
                        "r_agrees": bool(rr and abs(r1["mean"] - r3["mean"]) <= X["X5"]["band"][ty])})
        rows[n] = row
    x1 = {}
    for ty in TYPES:
        names = X["X1"]["sets"][ty]
        have = [n for n in names if rows[n]["resolved"]]
        if len(have) < math.ceil(X["X1"]["min_resolved_frac"] * len(names)) or len(have) < 3:
            x1[ty] = {"rho": None, "n": len(have), "of": len(names), "verdict": NOTSC}
            continue
        rho = s95.spearman([rows[n]["D_card1"]["mean"] for n in have], [rows[n]["D_aifoundry3"]["mean"] for n in have])
        x1[ty] = {"rho": rho, "n": len(have), "of": len(names), "verdict": PASS if rho >= X["X1"]["threshold"] else FAIL}
    vs = [v["verdict"] for v in x1.values()]
    x1v = FAIL if FAIL in vs else (NOTSC if NOTSC in vs else PASS)
    el = [n for n in X["X4"]["eligible"] if rows[n]["resolved"]]
    rat = sorted(rows[n]["ratio_a3_over_c1"] for n in el)
    med = statistics.median(rat) if rat else None
    lo, hi = X["X4"]["band"]
    x4v = NOTSC if med is None or len(el) < X["X4"]["min_resolved"] else (PASS if lo <= med <= hi else FAIL)
    per_type = {ty: (statistics.median([rows[n]["ratio_a3_over_c1"] for n in el if n.startswith(ty + ".")])
                     if any(n.startswith(ty + ".") for n in el) else None) for ty in TYPES}
    rr = [n for n in pool if rows[n]["r_resolved"]]
    agree = sum(1 for n in rr if rows[n]["r_agrees"])
    frac = agree / len(rr) if rr else None
    x5v = NOTSC if len(rr) < X["X5"]["min_resolved"] else (
        PASS if frac >= X["X5"]["pass_frac"] else (FAIL if frac < X["X5"]["fail_frac"] else INC))
    out = {"rows": rows,
           "x1": {"by_type": x1, "verdict": x1v},
           "x4": {"median_ratio": med, "n": len(el), "of": len(X["X4"]["eligible"]), "band": [lo, hi], "per_type_median": per_type,
                  "iqr": [rat[len(rat) // 4], rat[(3 * len(rat)) // 4]] if len(rat) >= 4 else None, "verdict": x4v},
           "x5": {"agree": agree, "resolved": len(rr), "of": len(pool), "frac": frac,
                  "disagree": [n for n in rr if not rows[n]["r_agrees"]], "verdict": x5v}}
    if not enough:
        for k in ("x1", "x4", "x5"):
            out[k]["verdict_from_too_few_passes"] = out[k]["verdict"]
            out[k]["verdict"] = NOTSC
    out["verdicts"] = {"E112b-X1": out["x1"]["verdict"], "E112b-X4": out["x4"]["verdict"], "E112b-X5": out["x5"]["verdict"]}
    return out


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def pm(m, d=3):
    return "—" if m is None or m.get("mean") is None else f"{m['mean']:.{d}f} ± {f(m.get('ci95'), d)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e112b", required=True)
    ap.add_argument("--arm", action="append", default=[], help="name=path of an arm's reduction")
    ap.add_argument("--e112a", help="(a)'s primary reduction (E91's format), for the same-session tie of E86's tiles")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    reg = json.load(open(REG))
    B = reg["b"]
    bad, src = [], {}
    frozen = dict(reg["inputs_frozen"])
    frozen["card1_view"] = B["card1_view"]
    for k, v in frozen.items():
        b, how = frozen_bytes(v)
        src[k] = how
        if b is None:
            bad.append(f"{k}: {v['path']} {how} (frozen {v['sha256']})")
    for rel in ("tools/claims-v3/kinds/score_e95.py", "tools/claims-v3/kinds/predictions-e95.json"):
        w = reg["harness"]["desk_code_unchanged_sha256"].get(rel) or reg["harness"]["card_code_unchanged_sha256"].get(rel)
        have = sha_b(open(os.path.join(ROOT, rel), "rb").read())
        if have != w:
            bad.append(f"{rel}: {have} != {w}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    import score_e95 as s95  # noqa: E402  (after the hash checks)
    G = load_frozen(B["card1_view"])
    F = load_frozen(reg["inputs_frozen"]["real2_predictions"])
    reg95 = copy.deepcopy(json.load(open(os.path.join(K, "predictions-e95.json"))))
    tie = B["session_tie"]
    reg95["session_tie"] = {n: {"D_w": v["D_w"], "ref": "E82 (card 1)", "band_w": v["band_w"]} for n, v in tie["e82_cells"].items()}
    pool = list(s95.e95.POOL)
    X = B["cross_card"]
    a3 = {"nodips": load_frozen(reg["inputs_frozen"]["e95_nodips"]), "primary": load_frozen(reg["inputs_frozen"]["e95_reduction"]),
          "leak0.1994": load_frozen(reg["inputs_frozen"]["e95_leak0.1994"]),
          "leak0.3803": load_frozen(reg["inputs_frozen"]["e95_leak0.3803"]), "leak0": load_frozen(reg["inputs_frozen"]["e95_leak0"])}
    pair_of = {"primary": "nodips", "dips_kept": "primary", "leak0.1994": "leak0.1994", "leak0.3803": "leak0.3803",
               "leak0": "leak0", "leak0.545": "nodips"}

    res = json.load(open(a.e112b))
    sc = score_claims(s95, res, G, F, reg95)
    sc["cross_card"] = {"primary": cross(s95, res, a3["nodips"], X, pool)}
    sc["cross_card"]["primary"]["pairing"] = "E112b primary (dips removed, auto) against E95's dips-removed arm (auto)"
    arms = {}
    for spec in a.arm:
        nm, path = spec.split("=", 1)
        r_ = json.load(open(path))
        s = score_claims(s95, r_, G, F, reg95)
        s["cross_card"] = cross(s95, r_, a3[pair_of.get(nm, "nodips")], X, pool)
        s["cross_card"]["pairing"] = f"E112b {nm} against E95's {pair_of.get(nm, 'nodips')}"
        arms[nm] = s
    for k, v in sc["claims"].items():
        v["at_arms"] = {nm: s["claims"][k]["verdict"] for nm, s in arms.items()}
        vs = ({v["verdict"]} | set(v["at_arms"].values())) - {NOTSC, UNDER}
        v["arm_sensitive"] = len(vs) > 1
    xv = sc["cross_card"]["primary"]["verdicts"]
    sc["cross_card"]["at_arms"] = {nm: s["cross_card"]["verdicts"] for nm, s in arms.items()}
    sc["cross_card"]["arm_sensitive"] = {k: len(({v} | {s["cross_card"]["verdicts"][k] for s in arms.values()}) - {NOTSC, UNDER}) > 1
                                         for k, v in xv.items()}
    # the same-session tie of E86's three tiles against (a)
    same = {}
    if a.e112a and os.path.exists(a.e112a):
        ra = json.load(open(a.e112a))
        for n, v in tie["same_session_e86_tiles"].items():
            mb = s95.View(res).D(n)
            ma = (ra.get("items", {}).get(n) or {}).get("D")
            good = s95.ok(mb) and ma and ma.get("mean") is not None and (ma.get("n") or 0) >= 3
            d = (mb["mean"] - ma["mean"]) if good else None
            same[n] = {"D_b": mb, "D_a": ma, "diff_w": d, "band_w": v["band_w"],
                       "verdict": (PASS if abs(d) <= v["band_w"] else FAIL) if good else NOTSC}
    sc["same_session_tie_reported"] = same
    tally = {}
    for v in sc["claims"].values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    xt = {}
    for v in xv.values():
        xt[v] = xt.get(v, 0) + 1
    sc["tally"] = tally
    sc["tally_cross_card"] = xt
    sc["experiment"] = "E112b"
    sc["registration"] = "tools/claims-v3/e112/E112.md"
    sc["frozen_sources"] = src
    sc["predictions_e112_sha256"] = sha_b(open(REG, "rb").read())
    sc["arms"] = {nm: {"leak": s["checks"]["leak"], "passes": s["passes"], "claims": {k: v["verdict"] for k, v in s["claims"].items()},
                       "cross_card": s["cross_card"]["verdicts"], "pairing": s["cross_card"]["pairing"]} for nm, s in arms.items()}
    json.dump(sc, open(a.json, "w"), indent=1, default=lambda o: None)

    # results.md: score_e95's own tables (on the card-1 view), then the cross-card rules and the ties
    s95.write_md(sc, arms, a.md, "E112b primary: aifoundry1 card 1, dips removed, leakage auto; the card-1 view")
    body = open(a.md).read().split("\n", 1)[1]
    cc = sc["cross_card"]["primary"]
    L = ["# E112b results (score_e112b.py; registration tools/claims-v3/e112/E112.md): E95's pass on aifoundry1 card 1", "",
         "The tables below are score_e95.py's own (write_md), on the card-1 view of the frozen file; C7 and C8 by the ports with "
         "the scaled thresholds. 'at the arms' lists the arms' verdicts; a claim's verdict at the frozen thresholds unscaled is in "
         "scored.json (claims.<C>.at_frozen_thresholds_unscaled_labelled).", "",
         "## Cross-card rules (E112b-X1, X4, X5)", "",
         f"Primary pairing: {cc['pairing']}.", "",
         "| rule | verdict | at the arms | detail |", "|---|---|---|---|"]
    at = sc["cross_card"]["at_arms"]

    def arms_of(rule):
        return ", ".join(nm + " " + v[rule] for nm, v in at.items())

    x1d = "; ".join(t + " rho " + f(v["rho"]) + " (n " + str(v["n"]) + " of " + str(v["of"]) + ") " + v["verdict"]
                    for t, v in cc["x1"]["by_type"].items())
    x4t = ", ".join(t + " " + f(v, 4) for t, v in cc["x4"]["per_type_median"].items())
    x5d = ", ".join(cc["x5"]["disagree"]) or "none"
    L.append(f"| E112b-X1 rank | **{cc['x1']['verdict']}** | {arms_of('E112b-X1')} | {x1d} |")
    L.append(f"| E112b-X4 scale | **{cc['x4']['verdict']}** | {arms_of('E112b-X4')} | "
             f"median D(aifoundry3)/D(card 1) {f(cc['x4']['median_ratio'], 4)} over {cc['x4']['n']} of {cc['x4']['of']} eligible tiles, "
             f"band {cc['x4']['band']}; per type {x4t} |")
    L.append(f"| E112b-X5 tile ratios | **{cc['x5']['verdict']}** | {arms_of('E112b-X5')} | "
             f"{cc['x5']['agree']} of {cc['x5']['resolved']} resolved agree (of {cc['x5']['of']}); disagree: {x5d} |")
    L += ["", "| tile | D card 1 W | D aifoundry3 W | ratio a3/c1 | r card 1 | r aifoundry3 | r diff | ± (quadrature) | band | agrees |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in cc["rows"].items():
        L.append(f"| {n} | {pm(v['D_card1'])} | {pm(v['D_aifoundry3'])} | {f(v['ratio_a3_over_c1'], 4)} | {pm(v.get('r_card1'), 4)} | "
                 f"{pm(v.get('r_aifoundry3'), 4)} | {f(v.get('r_diff'), 4)} | {f(v.get('r_diff_ci95_quadrature'), 4)} | {v.get('r_band', '—')} | "
                 f"{v.get('r_agrees', '—')} |")
    if same:
        L += ["", "## The same-session tie: E86's three tiles in (b) against (a) (reported)", "",
              "| tile | (b) D W | (a) D W | diff W | band | verdict |", "|---|---|---|---|---|---|"]
        for n, v in same.items():
            L.append(f"| {n} | {pm(v['D_b'])} | {pm(v['D_a'])} | {f(v['diff_w'])} | ±{v['band_w']} | {v['verdict']} |")
    L += ["", f"Claims tally: {tally}; cross-card tally: {xt}", ""]
    open(a.md, "w").write("\n".join(L) + body)
    print(json.dumps({"tally": tally, "cross": xv, **{k: v["verdict"] for k, v in sc["claims"].items()}}))


if __name__ == "__main__":
    main()
