#!/usr/bin/env python3
"""E131 scorer (Q136): E95's frozen claims C1-C12 on E131's passes (E95's pass on aifoundry1 card 1), on the card-1 view E112 froze, and the
cross-card rules X1, X4, X5 against E95's committed reductions of aifoundry3, with E131's set-aside rule (E131.md; predictions-e131.json >
set_aside_rule) choosing the reading that carries the verdicts.

    python3 tools/claims-v3/e131/score_e131.py --primary e131.json --relaxed e131-relaxed.json [--arm auto=e131-auto.json ...]
        --json scored.json --md results.md

Reused UNCHANGED (sha256 checked against predictions-e131.json): score_e95.py's own functions (score_e95.score, View, mc, write_md) and
score_e112b.py's (score_claims, with its C7 and C8 ports; cross, the cross-card rules), exactly as E112b scored the same pass on this card.
E131's own code here: the set-aside rule (S1 the primary; S2 the tie's drift lifted; S3 per format), the per-format NOT SCORED rule, the
readings' report, the arms' pairings, the session tie against E82's card-1 cells and the reported comparison with E112b's two kept passes.
It refuses to score if a frozen input differs from predictions-e131.json's sha256 (a frozen file that changed in the working copy is read
from its recorded commit). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
E112 = os.path.join(ROOT, "tools", "claims-v3", "e112")
sys.path.insert(0, K)
sys.path.insert(0, E112)
REG = os.path.join(HERE, "predictions-e131.json")
TYPES = ("fp32", "fp16", "int8")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
PASS, FAIL, INC, UNDER, NOTSC = "PASS", "FAIL", "INCONCLUSIVE", "UNDER-RESOLVED", "NOT SCORED"
KEYS = ("p80", "idle80", "D", "D32", "S", "Drail", "Srail", "Dmean", "rate", "dT_win")


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


# ---- the set-aside rule ----------------------------------------------------------------------------------------------

def classify(why):
    """A primary's set-aside reasons -> (hard, tie, failing formats). hard: a reason no step restores (failed runs, an unknown text)."""
    hard, tie, fmts = False, False, set()
    for w in why:
        if w.startswith("anchor_pi drifts"):
            tie = True
            continue
        m = re.match(r"^(fp32|fp16|int8)\.\S+ (departs|spans) ", w)
        if m:
            fmts.add(m.group(1))
        else:
            hard = True
    return hard, tie, fmts


def item_type(res, n):
    it = res.get("items", {}).get(n) or {}
    return it.get("type") or (n.split(".", 1)[0] if "." in n else "fp32")


def recompute_items(R, mc):
    """The over-pass means of a reading built from per-pass values (S2, S3), with score_e95's mc: the same mean, t and SE as reduce_e78's."""
    items = {}
    for n, it in R["items"].items():
        e = {k: v for k, v in it.items() if k not in KEYS and not k.startswith("pj_")}
        rows = [R["per_pass"][str(p)][n] for p in R["passes"] if n in R["per_pass"].get(str(p), {})]
        for k in KEYS:
            e[k] = mc([r.get(k) for r in rows])
        for src in ("S", "D"):
            pj = [1e12 * r[src] / r["rate"] for r in rows if r.get(src) is not None and r.get("rate")]
            e["pj_op_" + src] = mc(pj)
            m = it.get("macs_per_op") or 1
            e["pj_mac_" + src] = mc([x / m for x in pj])
            if it.get("type") in ("fp32", "fp16"):
                e["pj_flop_" + src] = mc([x / (2 * m) for x in pj])
        items[n] = e
    return items


def per_type_passes(R):
    return {ty: sum(1 for p in R["passes"] if REF[ty] in R["per_pass"].get(str(p), {})) for ty in TYPES}


def readings(P, Q, mc):
    """S1 = the primary; S2 = S1 plus passes set aside only by the tie; S3 = S2 plus passes set aside only by anchor gates of one or two
    formats, restored for the other formats. Restored values come from Q (the relaxed reduction at the same frozen slope)."""
    sa = {int(x["pass"]): x["why"] for x in P.get("passes_set_aside", [])}
    cfg = {int(x["pass"]) for x in P.get("passes_config_flags", [])}
    qp = {int(p) for p in Q.get("passes", [])}
    out = {"S1": P}
    restored = {"S2": [], "S3": []}
    R2 = copy.deepcopy(P)
    R3 = None
    for p, why in sorted(sa.items()):
        hard, tie, fmts = classify(why)
        if hard or p in cfg or p not in qp:
            continue
        if tie and not fmts:
            R2["passes"] = sorted(set(R2["passes"]) | {p})
            R2["per_pass"][str(p)] = copy.deepcopy(Q["per_pass"][str(p)])
            restored["S2"].append({"pass": p, "why": why, "formats_restored": list(TYPES)})
    R3 = copy.deepcopy(R2)
    for p, why in sorted(sa.items()):
        hard, tie, fmts = classify(why)
        if hard or p in cfg or p not in qp or not fmts or len(fmts) == len(TYPES):
            continue
        keep = [t for t in TYPES if t not in fmts]
        pp = {n: copy.deepcopy(v) for n, v in Q["per_pass"][str(p)].items() if item_type(Q, n) in keep}
        R3["passes"] = sorted(set(R3["passes"]) | {p})
        R3["per_pass"][str(p)] = pp
        restored["S3"].append({"pass": p, "why": why, "formats_restored": keep, "formats_left_out": sorted(fmts)})
    for nm, R in (("S2", R2), ("S3", R3)):
        R["items"] = recompute_items(R, mc) if restored["S2"] or (nm == "S3" and restored["S3"]) else R["items"]
        R["reading"] = nm
        out[nm] = R
    P["reading"] = "S1"
    return out, restored


def carrying(rd, nmin):
    for nm in ("S1", "S2", "S3"):
        if len(rd[nm]["passes"]) >= nmin:
            return nm
    return None


def type_rule(sc, R, ctypes, nmin):
    """A claim reading a format with fewer than nmin passes in the reading is NOT SCORED (its verdict kept beside)."""
    n = per_type_passes(R)
    for short, v in sc["claims"].items():
        short_types = ctypes.get(short) or list(TYPES)
        short_n = {t: n[t] for t in short_types}
        v["passes_by_format"] = short_n
        if any(x < nmin for x in short_n.values()) and v["verdict"] != NOTSC:
            v["verdict_before_format_rule"] = v["verdict"]
            v["verdict"] = NOTSC
    return n


def tally(vs):
    t = {}
    for v in vs:
        t[v] = t.get(v, 0) + 1
    return t


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}"


def pm(m, d=3):
    return "—" if m is None or m.get("mean") is None else f"{m['mean']:.{d}f} ± {f(m.get('ci95'), d)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--primary", required=True)
    ap.add_argument("--relaxed", required=True)
    ap.add_argument("--arm", action="append", default=[], help="name=path of an arm's reduction")
    ap.add_argument("--json", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    reg = json.load(open(REG))
    bad, src = [], {}
    for k, v in reg["inputs_frozen"].items():
        b, how = frozen_bytes(v)
        src[k] = how
        if b is None:
            bad.append(f"{k}: {v['path']} {how} (frozen {v['sha256']})")
    want = dict(reg["harness"]["desk_code_unchanged_sha256"])
    want.update({r: h for r, h in reg["harness"]["card_code_unchanged_sha256"].items() if r.endswith("predictions-e95.json")
                 or r.endswith("e95_common.py")})
    for rel, w in want.items():
        have = sha_b(open(os.path.join(ROOT, rel), "rb").read())
        if have != w:
            bad.append(f"{rel}: {have} != {w}")
    if bad:
        raise SystemExit("refusing to score - a frozen input changed:\n  " + "\n  ".join(bad))
    import score_e95 as s95  # noqa: E402  (after the hash checks)
    import score_e112b as s112  # noqa: E402
    I = reg["inputs_frozen"]
    G = load_frozen(I["card1_view"])
    F = load_frozen(I["real2_predictions"])
    reg95 = copy.deepcopy(json.load(open(os.path.join(K, "predictions-e95.json"))))
    reg95["session_tie"] = {n: {"D_w": v["D_w"], "ref": "E82 (card 1)", "band_w": v["band_w"]}
                            for n, v in reg["session_tie"]["e82_cells"].items()}
    pool = list(s95.e95.POOL)
    X = reg["cross_card"]
    a3 = {"nodips": load_frozen(I["e95_nodips"]), "primary": load_frozen(I["e95_reduction"]),
          "leak0.1994": load_frozen(I["e95_leak0.1994"]), "leak0.3803": load_frozen(I["e95_leak0.3803"]),
          "leak0": load_frozen(I["e95_leak0"])}
    pair_of = {"carrying": "nodips", "auto": "nodips", "dips_kept": "primary", "leak0.1994": "leak0.1994", "leak0.3803": "leak0.3803",
               "leak0": "leak0", "leak0.545": "nodips"}
    nmin = reg["set_aside_rule"]["min_kept_passes"]
    ctypes = reg["set_aside_rule"]["claims_types"]

    P = json.load(open(a.primary))
    Q = json.load(open(a.relaxed))
    rd, restored = readings(P, Q, s95.mc)
    carry = carrying(rd, nmin)
    rep = {}
    for nm in ("S1", "S2", "S3"):
        R = rd[nm]
        s = s112.score_claims(s95, R, G, F, reg95)
        nt = type_rule(s, R, ctypes, nmin)
        x = s112.cross(s95, R, a3["nodips"], X, pool)
        rep[nm] = {"passes": R["passes"], "passes_by_format": nt, "claims": {k: v["verdict"] for k, v in s["claims"].items()},
                   "tally": tally(v["verdict"] for v in s["claims"].values()),
                   "cross_card": {k.replace("E112b", "E131"): v for k, v in x["verdicts"].items()}, "_sc": s, "_x": x}
    use = carry or "S1"
    sc = rep[use]["_sc"]
    xc = rep[use]["_x"]
    xc["pairing"] = (f"E131's reading {use} (dips removed, leakage 0.2414 W/C) against E95's dips-removed arm (dips removed, leakage auto)")
    if carry is None:
        for v in sc["claims"].values():
            if v["verdict"] != NOTSC:
                v["verdict_from_too_few_passes"] = v["verdict"]
                v["verdict"] = NOTSC
        for k in ("x1", "x4", "x5"):
            if xc[k]["verdict"] != NOTSC:
                xc[k]["verdict_from_too_few_passes"] = xc[k]["verdict"]
                xc[k]["verdict"] = NOTSC
        xc["verdicts"] = {k: NOTSC for k in xc["verdicts"]}
    sc["cross_card"] = {"carrying": xc}
    arms = {}
    for spec in a.arm:
        nm, path = spec.split("=", 1)
        r_ = json.load(open(path))
        s = s112.score_claims(s95, r_, G, F, reg95)
        s["cross_card"] = s112.cross(s95, r_, a3[pair_of.get(nm, "nodips")], X, pool)
        s["cross_card"]["pairing"] = f"E131 {nm} against E95's {pair_of.get(nm, 'nodips')}"
        arms[nm] = s
    for k, v in sc["claims"].items():
        v["at_arms"] = {nm: s["claims"][k]["verdict"] for nm, s in arms.items()}
        vs = ({v["verdict"]} | set(v["at_arms"].values())) - {NOTSC, UNDER}
        v["arm_sensitive"] = len(vs) > 1
    xv = {k.replace("E112b", "E131"): v for k, v in xc["verdicts"].items()}
    at = {nm: {k.replace("E112b", "E131"): v for k, v in s["cross_card"]["verdicts"].items()} for nm, s in arms.items()}
    sc["cross_card"]["verdicts"] = xv
    sc["cross_card"]["at_arms"] = at
    sc["cross_card"]["arm_sensitive"] = {k: len(({v} | {s[k] for s in at.values()}) - {NOTSC, UNDER}) > 1 for k, v in xv.items()}
    # reported: E95's verdicts on aifoundry3 beside, and E112b's two kept passes on this card
    e95s = load_frozen(I["e95_scored"])
    e95n = load_frozen(I["e95_nodips_scored"])
    sc["e95_verdicts_beside"] = {k: {"e95_primary": (e95s["claims"].get(k) or {}).get("verdict"),
                                     "e95_dips_removed_arm": (e95n["claims"].get(k) or {}).get("verdict")} for k in sc["claims"]}
    e112b = load_frozen(I["e112b_reduction"])
    V1, Vb = s95.View(rd[use]), s95.View(e112b)
    Va = s95.View(json.load(open(dict(x.split("=", 1) for x in a.arm)["auto"]))) if any(x.startswith("auto=") for x in a.arm) else None
    cs = {}
    for n in pool + list(REF.values()):
        r1, rb = s95.mc(V1.r_series(n)) if n in pool else None, s95.mc(Vb.r_series(n)) if n in pool else None
        da = Va.D(n) if Va else None
        db = Vb.D(n)
        cs[n] = {"r_e131": r1, "r_e112b_two_passes": rb,
                 "r_diff": (r1["mean"] - rb["mean"]) if r1 and rb and r1["mean"] is not None and rb["mean"] is not None else None,
                 "D_e131_auto_arm": da, "D_e112b_two_passes": db,
                 "D_diff_auto_vs_e112b": (da["mean"] - db["mean"]) if da and da["mean"] is not None and db["mean"] is not None else None}
    sc["cross_session_e112b_reported"] = cs
    sc["set_aside"] = {"carrying_reading": carry, "used_for_verdicts": use, "restored": restored,
                       "primary_passes": P["passes"], "primary_set_aside": P.get("passes_set_aside"),
                       "relaxed_passes": Q["passes"], "relaxed_set_aside": Q.get("passes_set_aside"),
                       "readings": {nm: {k: v for k, v in r.items() if not k.startswith("_")} for nm, r in rep.items()}}
    sc["tally"] = tally(v["verdict"] for v in sc["claims"].values())
    sc["tally_cross_card"] = tally(xv.values())
    sc["experiment"] = "E131"
    sc["registration"] = "tools/claims-v3/e131/E131.md"
    sc["frozen_sources"] = src
    sc["predictions_e131_sha256"] = sha_b(open(REG, "rb").read())
    sc["arms"] = {nm: {"leak": s["checks"]["leak"], "passes": s["passes"], "claims": {k: v["verdict"] for k, v in s["claims"].items()},
                       "cross_card": {k.replace("E112b", "E131"): v for k, v in s["cross_card"]["verdicts"].items()},
                       "pairing": s["cross_card"]["pairing"]} for nm, s in arms.items()}
    json.dump(sc, open(a.json, "w"), indent=1, default=lambda o: None)

    s95.write_md(sc, arms, a.md, f"E131 reading {use}: aifoundry1 card 1, dips removed, leakage 0.2414 W/C; the card-1 view")
    body = open(a.md).read().split("\n", 1)[1]
    L = ["# E131 results (score_e131.py; registration tools/claims-v3/e131/E131.md): E95's pass on aifoundry1 card 1", "",
         f"**The reading that carries the verdicts: {carry or 'none (fewer than 3 passes in every reading: NOT SCORED)'}.** Primary (S1) "
         f"passes {P['passes']}; set aside {[(x['pass'], x['why']) for x in P.get('passes_set_aside', [])]}; relaxed reduction's passes "
         f"{Q['passes']}.", "",
         "| reading | passes | passes by format | claims tally | E131-X1 | E131-X4 | E131-X5 |", "|---|---|---|---|---|---|---|"]
    for nm, r in rep.items():
        L.append(f"| {nm} | {r['passes']} | {r['passes_by_format']} | {r['tally']} | {r['cross_card'].get('E131-X1')} | "
                 f"{r['cross_card'].get('E131-X4')} | {r['cross_card'].get('E131-X5')} |")
    L += ["", f"Restored: S2 {restored['S2'] or 'none'}; S3 {restored['S3'] or 'none'}.", "",
          "The claims tables below are score_e95.py's own (write_md) on the carrying reading of the card-1 view; C7 and C8 by score_e112b's "
          "ports. 'at the arms' lists the arms' verdicts; a claim's verdict at the frozen thresholds unscaled is in scored.json "
          "(claims.<C>.at_frozen_thresholds_unscaled_labelled); E95's verdicts on aifoundry3 are in scored.json e95_verdicts_beside.", "",
          "## Cross-card rules (E131-X1, X4, X5; score_e112b.cross unchanged)", "", f"Pairing: {xc['pairing']}.", "",
          "| rule | verdict | at the arms | detail |", "|---|---|---|---|"]

    def arms_of(rule):
        return ", ".join(nm + " " + v[rule] for nm, v in at.items())

    x1d = "; ".join(t + " rho " + f(v["rho"]) + " (n " + str(v["n"]) + " of " + str(v["of"]) + ") " + v["verdict"]
                    for t, v in xc["x1"]["by_type"].items())
    x4t = ", ".join(t + " " + f(v, 4) for t, v in xc["x4"]["per_type_median"].items())
    L.append(f"| E131-X1 rank | **{xv['E131-X1']}** | {arms_of('E131-X1')} | {x1d} |")
    L.append(f"| E131-X4 scale | **{xv['E131-X4']}** | {arms_of('E131-X4')} | median D(aifoundry3)/D(card 1) {f(xc['x4']['median_ratio'], 4)} "
             f"over {xc['x4']['n']} of {xc['x4']['of']} eligible tiles, band {xc['x4']['band']}; per type {x4t} |")
    L.append(f"| E131-X5 tile ratios | **{xv['E131-X5']}** | {arms_of('E131-X5')} | {xc['x5']['agree']} of {xc['x5']['resolved']} resolved "
             f"agree (of {xc['x5']['of']}); disagree: {', '.join(xc['x5']['disagree']) or 'none'} |")
    L += ["", "| tile | D card 1 W | D aifoundry3 W | ratio a3/c1 | r card 1 | r aifoundry3 | r diff | ± (quadrature) | band | agrees |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in xc["rows"].items():
        L.append(f"| {n} | {pm(v['D_card1'])} | {pm(v['D_aifoundry3'])} | {f(v['ratio_a3_over_c1'], 4)} | {pm(v.get('r_card1'), 4)} | "
                 f"{pm(v.get('r_aifoundry3'), 4)} | {f(v.get('r_diff'), 4)} | {f(v.get('r_diff_ci95_quadrature'), 4)} | {v.get('r_band', '—')} | "
                 f"{v.get('r_agrees', '—')} |")
    L += ["", "## E95's verdicts on aifoundry3 beside (reported)", "", "| claim | E131 | E95 primary | E95 dips-removed arm |", "|---|---|---|---|"]
    for k, v in sc["claims"].items():
        L.append(f"| {k} | {v['verdict']} | {sc['e95_verdicts_beside'][k]['e95_primary']} | {sc['e95_verdicts_beside'][k]['e95_dips_removed_arm']} |")
    L += ["", "## Beside E112b's two kept passes on this card (reported, never a verdict)", "",
          "| tile | r E131 | r E112b (2 passes) | r diff | D E131 auto arm W | D E112b W | D diff W |", "|---|---|---|---|---|---|---|"]
    for n, v in cs.items():
        L.append(f"| {n} | {pm(v['r_e131'], 4)} | {pm(v['r_e112b_two_passes'], 4)} | {f(v['r_diff'], 4)} | {pm(v['D_e131_auto_arm'])} | "
                 f"{pm(v['D_e112b_two_passes'])} | {f(v['D_diff_auto_vs_e112b'])} |")
    L += ["", f"Claims tally: {sc['tally']}; cross-card tally: {sc['tally_cross_card']}", ""]
    open(a.md, "w").write("\n".join(L) + body)
    print(json.dumps({"carrying": carry, "tally": sc["tally"], "cross": xv, **{k: v["verdict"] for k, v in sc["claims"].items()}}))


if __name__ == "__main__":
    main()
