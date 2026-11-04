#!/usr/bin/env python3
"""Q140(x): rank 4's paired-anchor rule (rank4_rule.json beside this file), scored on one session pair.

    python3 -B score_rank4.py --a3 <aifoundry3 session> --c1 <card-1 session> [--pair E163/E164] [--pool <dir>] [--rule <json>]
                              [--out <json>]
    python3 -B score_rank4.py --selftest <lab repo> [--out <json>]

A session file is either a D table, {"tiles": {name: {"mean": W, "per_pass": [W, ...]}}} ("per_pass" optional; "n_passes" and
"sd" may stand in for it), or a scored.json in E153's / E157's layout (primary[.primary].power_rows.<model>.<tile>.measured,
n_passes, sd; pool_anchors.<tile>.measured_D; e78_anchors_D.<tile>.mean, per_pass). D is the session's registered primary
reduction on Q139(u)'s footing; this script only reads it. The pool dir's manifest (blind7.json, else blind6.json, else
blind5.json) gives each tile's type and anchor flag. Standard library only.

The rule, per family (floats = fp32 + fp16; int8): s_anchor = the median over the family's random anchors of D(card 1) /
D(aifoundry3); s_pool = the median of the same ratio over the pool's non-anchor tiles of the family measured in both sessions
with D at or above the family's floor on both cards (E157's X1 / X2 selection); PASS if |s_anchor / s_pool - 1| is within the
family's line (1% floats, 2% int8), FAIL if not, NOT SCORED if too few anchors or tiles. The pair passes if both families do.

--selftest runs the same code on pool 6's committed sessions (E153 on aifoundry3, E157 on card 1) with the random anchors the
critic used there (E78's and pool 6's, per format: pool 6 held one random anchor per format), and checks it against Q140(c)'s
committed check 3 (check3-anchor-card-scale.json) and E157's registered X1 / X2 (scored-e153.json): the same tiles, medians,
offsets and per-tile spread.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load_manifest(pool):
    for nm in ("blind7.json", "blind6.json", "blind5.json"):
        p = os.path.join(pool, nm)
        if os.path.exists(p):
            man = json.load(open(p))
            return nm, {m["name"]: {"type": m["type"], "anchor": bool(m.get("anchor"))} for m in man["tiles"]}
    raise SystemExit(f"no blind7.json / blind6.json / blind5.json in {pool}")


def _rec(mean, per_pass=None, n=None, sd=None):
    r = {"mean": float(mean), "per_pass": [float(x) for x in per_pass] if per_pass else None,
         "n": len(per_pass) if per_pass else (int(n) if n else None), "sd": None}
    if per_pass and len(per_pass) > 1:
        r["sd"] = st.stdev(r["per_pass"])
    elif sd is not None:
        r["sd"] = float(sd)
    return r


def load_session(path):
    """{tile: {mean, per_pass, n, sd}} from a D table or an E153 / E157 scored.json."""
    d = json.load(open(path))
    if isinstance(d.get("tiles"), dict):
        return {k: _rec(v["mean"], v.get("per_pass"), v.get("n_passes"), v.get("sd")) for k, v in d["tiles"].items()}, "D table"
    p = d.get("primary", d)
    if isinstance(p.get("primary"), dict) and "power_rows" in p["primary"]:
        p = p["primary"]
    if "power_rows" not in p:
        raise SystemExit(f"{path}: neither a D table nor a scored.json with power_rows")
    out = {}
    models = sorted(p["power_rows"])
    for lab in models:
        for k, v in p["power_rows"][lab].items():
            if k in out:
                if abs(out[k]["mean"] - float(v["measured"])) > 1e-9:
                    raise SystemExit(f"{path}: power_rows disagree on {k}'s measured D between models")
                continue
            out[k] = _rec(v["measured"], v.get("per_pass"), v.get("n_passes"), v.get("sd"))
    for k, v in (p.get("pool_anchors") or {}).items():
        rec = _rec(v["measured_D"], v.get("per_pass"), v.get("n_passes"), v.get("sd"))
        if k in out and abs(out[k]["mean"] - rec["mean"]) > 1e-9:
            raise SystemExit(f"{path}: pool_anchors and power_rows disagree on {k}")
        out.setdefault(k, rec)
    for k, v in (p.get("e78_anchors_D") or {}).items():
        out.setdefault(k, _rec(v["mean"], v.get("per_pass")))
    return out, "scored.json (" + "/".join(models) + ")"


def rel_se(r):
    if r["sd"] is None or not r["n"]:
        return None
    return r["sd"] / math.sqrt(r["n"]) / r["mean"]


def boot_median(vals, draws, seed):
    rng = random.Random(seed)
    n = len(vals)
    meds = sorted(st.median([vals[rng.randrange(n)] for _ in range(n)]) for _ in range(draws))
    return meds[int(0.025 * draws)], meds[int(0.975 * draws) - 1]


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def anchor_scale(names, A, C):
    got = [n for n in names if n in A and n in C]
    rat = {n: C[n]["mean"] / A[n]["mean"] for n in got}
    se = {}
    for n in got:
        a, c = rel_se(A[n]), rel_se(C[n])
        se[n] = rat[n] * math.hypot(a, c) if a is not None and c is not None else None
    return got, rat, se


def score_family(fam, cfg, rule, man, A, C):
    got, rat, se = anchor_scale(cfg["anchors"], A, C)
    res = {"anchors_registered": cfg["anchors"], "anchors_measured_on_both": got, "anchor_ratio": rat, "anchor_ratio_se": se,
           "line_rel": cfg["line_rel"], "pool_min_D_w": cfg["pool_min_D_w"]}
    sel = sorted(n for n, m in man.items() if not m["anchor"] and m["type"] in cfg["types"] and n in A and n in C
                 and A[n]["mean"] >= cfg["pool_min_D_w"] and C[n]["mean"] >= cfg["pool_min_D_w"])
    ratios = {n: C[n]["mean"] / A[n]["mean"] for n in sel}
    res.update({"pool_tiles": sel, "n_pool": len(sel), "pool_ratios": ratios})
    if len(got) < cfg["min_anchors"] or len(sel) < rule["min_pool_tiles"]:
        res["verdict"] = "NOT SCORED"
        res["why"] = f"{len(got)} of {len(cfg['anchors'])} anchors and {len(sel)} pool tiles measured on both cards " \
                     f"(needs {cfg['min_anchors']} and {rule['min_pool_tiles']})"
        return res
    s_anchor = st.median(rat.values())
    s_pool = st.median(ratios.values())
    bs = rule["bootstrap"]
    lo, hi = boot_median([ratios[n] for n in sel], bs["draws"], bs["seed"] + sum(map(ord, fam)))
    off = s_anchor / s_pool - 1
    res.update({"s_anchor": s_anchor, "s_anchor_mean": st.mean(rat.values()), "s_pool": s_pool, "s_pool_95": [lo, hi],
                "offset_rel": off, "verdict": "PASS" if abs(off) <= cfg["line_rel"] else "FAIL"})
    ses = [se[n] for n in got]
    res["s_anchor_mean_se_from_passes"] = math.sqrt(sum(s * s for s in ses)) / len(ses) if all(s is not None for s in ses) else None
    res["each_anchor_vs_pool_rel"] = {n: rat[n] / s_pool - 1 for n in got}
    res["per_tile_rel_rms_about_s_anchor"] = rms([ratios[n] / s_anchor - 1 for n in sel])
    res["per_tile_rel_rms_about_s_pool"] = rms([ratios[n] / s_pool - 1 for n in sel])
    res["vs_card_terms"] = {lab: {"term": t[cfg["types"][0]], "s_anchor_vs_term_rel": s_anchor / t[cfg["types"][0]] - 1,
                                  "s_pool_vs_term_rel": s_pool / t[cfg["types"][0]] - 1}
                            for lab, t in sorted(rule["card_terms_applied"].items())}
    e78 = rule["e78_arm_anchors"][fam]
    g2, r2, _ = anchor_scale(cfg["anchors"] + e78, A, C)
    if any(n in g2 for n in e78):
        s2 = st.median(r2.values())
        res["arm_with_E78_anchors"] = {"anchors": g2, "s_anchor": s2, "offset_rel": s2 / s_pool - 1,
                                       "within_line": abs(s2 / s_pool - 1) <= cfg["line_rel"]}
    else:
        res["arm_with_E78_anchors"] = "not run (E78's anchors not measured in both sessions)"
    if len(cfg["types"]) > 1:
        per = {}
        for t in cfg["types"]:
            an = [n for n in got if man.get(n, {}).get("type", n.split(".")[0]) == t]
            tl = [n for n in sel if man[n]["type"] == t]
            if an and tl:
                sa, sp = st.median([rat[n] for n in an]), st.median([ratios[n] for n in tl])
                per[t] = {"anchors": an, "s_anchor": sa, "n_pool": len(tl), "s_pool": sp, "offset_rel": sa / sp - 1}
        res["per_format"] = per
    return res


def score(rule, man, A, C, label):
    out = {"_note": "Q140(x) score_rank4.py: rank 4's paired-anchor rule on one session pair", "pair": label, "rule": rule["rule"],
           "families": {}}
    for fam, cfg in rule["families"].items():
        out["families"][fam] = score_family(fam, cfg, rule, man, A, C)
    v = [r["verdict"] for r in out["families"].values()]
    out["verdict"] = "FAIL" if "FAIL" in v else ("PASS" if all(x == "PASS" for x in v) else "NOT SCORED")
    return out


def lines(out):
    L = [f"RANK 4, paired-anchor card scale, pair {out['pair']}: {out['verdict']}"]
    for fam, r in out["families"].items():
        if r["verdict"] == "NOT SCORED":
            L.append(f"  {fam}: NOT SCORED ({r['why']})")
            continue
        se = r["s_anchor_mean_se_from_passes"]
        L.append(f"  {fam}: anchors {', '.join(f'{n} {x:.4f}' for n, x in r['anchor_ratio'].items())} -> s_anchor {r['s_anchor']:.4f} "
                 f"(mean {r['s_anchor_mean']:.4f}{f' +- {se:.4f} from passes' if se is not None else ''}); s_pool {r['s_pool']:.4f} "
                 f"[{r['s_pool_95'][0]:.4f}, {r['s_pool_95'][1]:.4f}] over {r['n_pool']} tiles; offset {100 * r['offset_rel']:+.2f}% "
                 f"against +-{100 * r['line_rel']:.0f}%: {r['verdict']}")
        L.append(f"     per tile about s_anchor {100 * r['per_tile_rel_rms_about_s_anchor']:.2f}% rms, about s_pool "
                 f"{100 * r['per_tile_rel_rms_about_s_pool']:.2f}%; s_anchor vs M9/M8's {r['vs_card_terms']['M9']['term']:.4f}: "
                 f"{100 * r['vs_card_terms']['M9']['s_anchor_vs_term_rel']:+.2f}%; vs M7/M6's {r['vs_card_terms']['M7']['term']:.4f}: "
                 f"{100 * r['vs_card_terms']['M7']['s_anchor_vs_term_rel']:+.2f}%")
        arm = r["arm_with_E78_anchors"]
        L.append("     E78 arm: " + (arm if isinstance(arm, str) else f"{len(arm['anchors'])} anchors, s_anchor {arm['s_anchor']:.4f}, "
                                      f"offset {100 * arm['offset_rel']:+.2f}%, within the line: {arm['within_line']}"))
        for t, q in (r.get("per_format") or {}).items():
            L.append(f"     {t}: anchors' median {q['s_anchor']:.4f} against its own {q['n_pool']} tiles' {q['s_pool']:.4f} "
                     f"({100 * q['offset_rel']:+.2f}%)")
    return L


def selftest(repo, outp):
    rule = json.load(open(os.path.join(HERE, "rank4_rule.json")))
    t = json.loads(json.dumps(rule))
    t["families"]["floats"]["anchors"] = ["fp32.randn", "fp32.anchor6_randn", "fp16.randn", "fp16.anchor6_randn"]
    t["families"]["int8"]["anchors"] = ["int8.full", "int8.anchor6_full"]
    t["e78_arm_anchors"] = {"floats": [], "int8": []}
    _, man = load_manifest(os.path.join(repo, "tools", "claims-v3", "kinds", "blind6"))
    for n, ty in (("fp32.randn", "fp32"), ("fp16.randn", "fp16"), ("int8.full", "int8")):
        man[n] = {"type": ty, "anchor": True}
    A, srcA = load_session(os.path.join(repo, "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/scored.json"))
    C, srcC = load_session(os.path.join(repo, "docs/reports/data/2026-11-03-e157-blind6-card1/scored.json"))
    out = score(t, man, A, C, "selftest: pool 6, E153/E157, the critic's anchors (E78's and pool 6's)")
    ref = json.load(open(os.path.join(repo, "docs/reports/data/2026-11-04-q140c-critic-checks/check3-anchor-card-scale.json")))
    X = json.load(open(os.path.join(repo, "docs/reports/data/2026-11-03-e157-blind6-card1/scored-e153.json")))["primary"]["rules"]
    checks = []

    def eq(what, a, b, tol=1e-12):
        ok = (a == b) if not isinstance(a, float) else abs(a - b) <= tol
        checks.append((what, a, b, ok))

    for fam, xid, ck in (("floats", "E157-X1", "floats"), ("int8", "E157-X2", "int8")):
        r = out["families"][fam]
        eq(f"{fam}: pool tiles = {xid}'s", sorted(r["pool_tiles"]), sorted(X[xid]["ratios"]))
        eq(f"{fam}: s_pool = {xid}'s median_ratio", r["s_pool"], X[xid]["median_ratio"])
        eq(f"{fam}: s_anchor = check 3's median", r["s_anchor"], ref["scale"][ck]["median"])
        eq(f"{fam}: s_anchor mean = check 3's mean", r["s_anchor_mean"], ref["scale"][ck]["mean"])
        eq(f"{fam}: offset = check 3's median_vs_pool_rel", r["offset_rel"], ref["scale"][ck]["median_vs_pool_rel"])
        eq(f"{fam}: verdict = check 3's rank4_rule_met", r["verdict"] == "PASS", ref["scale"][ck]["rank4_rule_met"])
        eq(f"{fam}: per-tile rms about s_anchor = check 3's", r["per_tile_rel_rms_about_s_anchor"],
           ref["per_tile_transfer"][ck]["rel_rms_about_anchor_scale"])
        eq(f"{fam}: per-tile rms about s_pool = check 3's", r["per_tile_rel_rms_about_s_pool"],
           ref["per_tile_transfer"][ck]["rel_rms_about_pool_median"])
    L = lines(out) + ["", f"inputs: aifoundry3 {srcA}, card 1 {srcC}; pool manifest blind6.json"]
    for what, a, b, ok in checks:
        show = (lambda v: f"{len(v)} tiles" if isinstance(v, list) else (f"{v:.12g}" if isinstance(v, float) else str(v)))
        L.append(f"  {'ok  ' if ok else 'FAIL'} {what}: {show(a)} / {show(b)}")
    bad = sum(not c[3] for c in checks)
    L.append(f"SELFTEST {'PASS' if not bad else 'FAIL'}: {len(checks)} checks, {bad} differ")
    print("\n".join(L))
    if outp:
        json.dump({"selftest": out, "checks": [{"what": w, "ok": ok} for w, _, _, ok in checks], "pass": not bad},
                  open(outp, "w"), indent=1, sort_keys=True)
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a3")
    ap.add_argument("--c1")
    ap.add_argument("--pair", default="E163/E164")
    ap.add_argument("--pool", default=HERE)
    ap.add_argument("--rule", default=os.path.join(HERE, "rank4_rule.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", default=None, metavar="REPO")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(os.path.abspath(a.selftest), a.out))
    if not (a.a3 and a.c1):
        ap.error("--a3 and --c1 are required (or --selftest)")
    rule = json.load(open(a.rule))
    mname, man = load_manifest(a.pool)
    A, srcA = load_session(a.a3)
    C, srcC = load_session(a.c1)
    out = score(rule, man, A, C, a.pair)
    out["inputs"] = {"aifoundry3": [os.path.basename(a.a3), srcA], "aifoundry1c1": [os.path.basename(a.c1), srcC], "manifest": mname}
    print("\n".join(lines(out)))
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
