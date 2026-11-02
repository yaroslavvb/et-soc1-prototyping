#!/usr/bin/env python3
"""E121 (Q134): score the frozen rules of predictions-e121.json on E121's reduction (E93's tiles on aifoundry3 card 0).
Registration: E121.md. Written with the pre-registration, before any pass exists; nothing here reads a line from the data.

    python3 tools/claims-v3/e121/score_e121.py --e121 e121.json [--arm name=e121-arm.json ...] [--md results.md] [--json scored.json]

It reuses score_e93.py's own functions unchanged (stats, contrast, verdict, band_verdict, reading, reported; its sha256 is
checked against predictions-e121.json first) and adds three things E93 did not need:
  G  E93's 24 rules with E93's lines; where E93 subtracted E82's fixed number of card 1, E78's number for the same cell on
     aifoundry3. The gate summary: PASS if all 22 gate rules (R1-R4, R6a-c, R7) PASS, FAIL if any FAILs.
  X  the cross-card rules: d = C121 - s*C93 (s = E82's per-type card scale), h = sqrt(h121^2 + (s*h93)^2); PASS if |d| + h
     <= w, FAIL if |d| - h > w, else INCONCLUSIVE. Aggregate: PASS if no X rule FAILs and >= 12 of 24 PASS; FAIL if >= 3
     FAIL; else INCONCLUSIVE.
  T  the session tie against E78's cells on aifoundry3 (E93's bands); E95's dips-removed anchors are printed beside it.
The unit of replication is the pass. Fewer than min_kept_passes kept passes: every rule NOT SCORED. Every verdict is also
computed at each registered arm, and a verdict that moves is marked arm-sensitive. Standard library only.
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
KINDS = os.path.join(ROOT, "tools", "claims-v3", "kinds")
REG_PATH = os.path.join(HERE, "predictions-e121.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


REG = json.load(open(REG_PATH))
_want = REG["harness"]["desk_code_unchanged_sha256"]["tools/claims-v3/kinds/score_e93.py"]
if sha(os.path.join(KINDS, "score_e93.py")) != _want:
    raise SystemExit("refusing to score: tools/claims-v3/kinds/score_e93.py differs from the sha256 E121 froze")
sys.path.insert(0, KINDS)
import score_e93 as s93  # noqa: E402  (after the check)


def gate_summary(rules, ids):
    v = [rules[i]["verdict"] for i in ids]
    if all(x == "NOT SCORED" for x in v):
        return "NOT SCORED"
    if any(x == "FAIL" for x in v):
        return "FAIL"
    if all(x == "PASS" for x in v):
        return "PASS"
    return "INCONCLUSIVE"


def x_verdict(c121, x, min_cell):
    if c121["n"] < min_cell or c121["ci95"] is None:
        return "UNRESOLVED", None, None
    s = x["scale"]
    d = c121["mean"] - s * x["e93"]["mean"]
    h = math.sqrt(c121["ci95"] ** 2 + (s * x["e93"]["ci95"]) ** 2)
    w = x["w"]
    v = "PASS" if abs(d) + h <= w else "FAIL" if abs(d) - h > w else "INCONCLUSIVE"
    return v, d, h


def score(res, reg):
    pr = reg["passes"]
    min_pass, min_cell = pr["min_kept_passes"], pr["min_cell_passes"]
    kept = len(res["passes"])
    scored_ok = kept >= min_pass
    rules, cs = {}, {}
    for r in reg["rules"]:
        fx = r["fixed"]["value_w"] if r.get("fixed") else None
        c = s93.contrast(res, r["a"], r.get("b"), fx)
        cs[r["id"]] = c
        rules[r["id"]] = {"verdict": s93.verdict(r, c, min_cell) if scored_ok else "NOT SCORED", "contrast": c,
                          "a": r["a"], "b": r.get("b"), "fixed_w": fx, "test": r["test"],
                          "e93_verdict": reg["e93_verdicts"][r["id"]],
                          **{k: r[k] for k in ("pass", "fail", "thr", "w") if k in r}}
    xs = {}
    tally_x = {}
    for x in reg["cross_card"]["rules"]:
        c = cs[x["of"]]
        v, d, h = x_verdict(c, x, min_cell)
        v = v if scored_ok else "NOT SCORED"
        xs[x["id"]] = {"verdict": v, "c121": c["mean"], "c121_ci95": c["ci95"], "e93": x["e93"]["mean"],
                       "e93_ci95": x["e93"]["ci95"], "scale": x["scale"], "predicted_w": x["predicted_w"],
                       "difference_w": d, "h_w": h, "w": x["w"],
                       "ratio": None if (c["mean"] is None or not x["e93"]["mean"]) else c["mean"] / x["e93"]["mean"]}
        tally_x[v] = tally_x.get(v, 0) + 1
    nfail, npass = tally_x.get("FAIL", 0), tally_x.get("PASS", 0)
    if not scored_ok:
        xagg = "NOT SCORED"
    elif nfail == 0 and npass >= 12:
        xagg = "PASS"
    elif nfail >= 3:
        xagg = "FAIL"
    else:
        xagg = "INCONCLUSIVE"
    tie = {}
    for n, e in reg["e78_reference"].items():
        c = s93.contrast(res, n)
        ok = None if c["mean"] is None else abs(c["mean"] - e["D_w"]) <= e["band_w"]
        tie[n] = {"D": c["mean"], "ci95": c["ci95"], "n": c["n"], "ref_D": e["D_w"], "band_w": e["band_w"],
                  "difference_w": None if c["mean"] is None else c["mean"] - e["D_w"],
                  "verdict": "UNRESOLVED" if ok is None else "PASS" if ok else "FAIL"}
    tv = "UNRESOLVED" if any(x["verdict"] == "UNRESOLVED" for x in tie.values()) else \
        "PASS" if all(x["verdict"] == "PASS" for x in tie.values()) else "FAIL"
    tiles = {}
    for n, t in reg["tiles_e93"].items():
        c = s93.contrast(res, n)
        tiles[n] = {"D": c, "e93_D_w": t["e93_D_w"], "scaled_w": t["scaled_w"],
                    "difference_w": None if c["mean"] is None else c["mean"] - t["scaled_w"],
                    "ratio_to_e93": None if (c["mean"] is None or not t["e93_D_w"]) else c["mean"] / t["e93_D_w"]}
    tally = {}
    for v in rules.values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    same = sum(1 for v in rules.values() if v["verdict"] == v["e93_verdict"])
    return {"kept_passes": kept, "passes": res["passes"], "set_aside": res.get("passes_set_aside"),
            "leak": res.get("leak"), "rules": rules, "tally": tally,
            "gate_summary": gate_summary(rules, reg["gate_rules"]) if scored_ok else "NOT SCORED",
            "same_verdict_as_e93": f"{same} of {len(rules)}",
            "pairing_reading": s93.reading(cs) if scored_ok else "NOT SCORED",
            "cross_card": {"rules": xs, "tally": tally_x, "aggregate": xagg},
            "tie_e78": {"verdict": tv, "cells": tie}, "tiles": tiles}


def session_scale(res, reg):
    """Reported: this session's D over E93's D for the three random anchors and the constant (card 1 -> aifoundry3)."""
    out = {}
    for n, ty in (("fp32.randn", "fp32"), ("fp16.randn", "fp16"), ("int8.full", "int8"), ("anchor_pi", "fp32")):
        c = s93.contrast(res, n)
        e = reg["tiles_e93"].get(n, {}).get("e93_D_w")
        out[n] = {"D": c["mean"], "ci95": c["ci95"], "e93_D_w": e,
                  "ratio": None if (c["mean"] is None or not e) else c["mean"] / e,
                  "e82_scale": reg["card_scale"]["per_type"][ty]}
    return out


def fmt(s, d=3):
    if s is None or s.get("mean") is None:
        return "—"
    return f"{s['mean']:.{d}f} ± {s['ci95']:.{d}f}" if s.get("ci95") is not None else f"{s['mean']:.{d}f}"


def f3(x, d=3):
    return "—" if x is None else f"{x:+.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e121", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    reg = REG
    res = json.load(open(a.e121))
    prim = score(res, reg)
    arms = {}
    for x in a.arm:
        nm, p = x.split("=", 1)
        arms[nm] = score(json.load(open(p)), reg)
        arms[nm]["file"] = os.path.basename(p)
    for rid, v in prim["rules"].items():
        v["at_arms"] = {nm: s["rules"][rid]["verdict"] for nm, s in arms.items()}
        v["arm_sensitive"] = any(x != v["verdict"] for x in v["at_arms"].values())
    for xid, v in prim["cross_card"]["rules"].items():
        v["at_arms"] = {nm: s["cross_card"]["rules"][xid]["verdict"] for nm, s in arms.items()}
        v["arm_sensitive"] = any(x != v["verdict"] for x in v["at_arms"].values())
    rep_reg = {"tiles": {n: {} for n in reg["tiles_e93"] if "." in n and n.split(".")[0] in ("fp32", "fp16", "int8")
                         and n not in ("fp32.sparse50", "fp32.a_zeros_b_randn", "fp32.randn", "fp32.zeros", "fp16.randn",
                                       "fp16.zeros", "int8.a_zeros_b_full", "int8.full", "int8.zeros")},
               "prices": {"F_w": reg["prices_e93_card1"]["F_w"]}}
    out = {"experiment": "E121", "predictions_sha256": sha(REG_PATH), "scorer_sha256": sha(os.path.abspath(__file__)),
           "score_e93_sha256": sha(os.path.join(KINDS, "score_e93.py")),
           "primary": prim, "arms": {k: {kk: vv for kk, vv in v.items() if kk != "tiles"} for k, v in arms.items()},
           "reported": {"e93_reported_block": s93.reported(res, rep_reg) if res["passes"] else None,
                        "session_scale": session_scale(res, reg),
                        "e95_beside": reg["e95_beside"]},
           "checks": {"cycles_per_op": res.get("cycles_per_op"), "clock_mhz": res.get("clock_mhz"), "v_mean": res.get("v_mean"),
                      "idle_level": res.get("idle_level"),
                      "idle_consistency": res.get("checks", {}).get("idle_consistency"),
                      "carryover": res.get("checks", {}).get("carryover"),
                      "rail_tau_median_s": res.get("checks", {}).get("rail_refit", {}).get("tau_median_s"),
                      "failed_runs": res.get("failed"), "runs": res.get("runs"), "kept": res.get("kept"),
                      "dip_samples_removed": {k: v.get("samples_removed") for k, v in (res.get("reducer", {}).get("dip_samples_removed") or {}).items()},
                      "config_flags": res.get("passes_config_flags"),
                      "config_reads_raw": res.get("reducer", {}).get("config_reads_raw")}}
    L = [f"# E121 scored (kept passes {prim['passes']}, set aside {prim['set_aside']}, leak {prim['leak']})", "",
         f"Gate rules (22): **{prim['gate_summary']}**. Tally of E93's 24 rules: {prim['tally']}; the same verdict as E93 "
         f"on card 1: {prim['same_verdict_as_e93']}. Int8 pairing: **{prim['pairing_reading']}**. Cross-card: "
         f"**{prim['cross_card']['aggregate']}** {prim['cross_card']['tally']}. Session tie to E78: **{prim['tie_e78']['verdict']}**.", "",
         "| rule | contrast | W, 95% | threshold | verdict | E93 (card 1) | at the arms |", "|---|---|---|---|---|---|---|"]
    for r in reg["rules"]:
        v = prim["rules"][r["id"]]
        lhs = r["a"] + (f" − {r['b']}" if r.get("b") else f" − {v['fixed_w']:.3f} (E78)" if v["fixed_w"] is not None else "")
        thr = {"above": f"low > {r.get('pass')}, high < {r.get('fail')} fails", "below": f"high < {r.get('thr')}",
               "within": f"inside ±{r.get('w')}"}[r["test"]]
        moved = {k: x for k, x in v["at_arms"].items() if x != v["verdict"]}
        ms = ("; ".join(f"{k} {y}" for k, y in moved.items()) or "same at all") if arms else "—"
        L.append(f"| {r['id']} | {lhs} | {fmt(v['contrast'])} | {thr} | **{v['verdict']}** | {v['e93_verdict']} | {ms} |")
    L += ["", "| cross-card rule | E121, W | E93 × scale, W | difference | ± h | w | verdict | ratio E121/E93 | at the arms |",
          "|---|---|---|---|---|---|---|---|---|"]
    for x in reg["cross_card"]["rules"]:
        v = prim["cross_card"]["rules"][x["id"]]
        moved = {k: y for k, y in v["at_arms"].items() if y != v["verdict"]}
        c121 = "—" if v["c121"] is None else f"{v['c121']:.3f} ± {v['c121_ci95']:.3f}" if v["c121_ci95"] is not None else f"{v['c121']:.3f}"
        hs = "—" if v["h_w"] is None else "%.3f" % v["h_w"]
        rs = "—" if v["ratio"] is None else "%.3f" % v["ratio"]
        ms = ("; ".join(f"{k} {y}" for k, y in moved.items()) or "same at all") if arms else "—"
        L.append(f"| {x['id']} | {c121} | {x['e93']['mean']:.3f} × {x['scale']:.4f} = {x['predicted_w']:.3f} | "
                 f"{f3(v['difference_w'])} | {hs} | {x['w']} | **{v['verdict']}** | {rs} | {ms} |")
    L += ["", "| tie cell | D | E78 (aifoundry3) | difference | band | verdict |", "|---|---|---|---|---|---|"]
    for n, v in prim["tie_e78"]["cells"].items():
        d = v["difference_w"]
        L.append(f"| {n} | {'—' if v['D'] is None else round(v['D'], 3)} | {v['ref_D']} | {'—' if d is None else round(d, 3)} | ±{v['band_w']} | {v['verdict']} |")
    L += ["", "| tile | D over the type's zeros, W | E93 on card 1, W | E93 × scale, W | difference | ratio |", "|---|---|---|---|---|---|"]
    for n, v in sorted(prim["tiles"].items()):
        L.append(f"| {n} | {fmt(v['D'])} | {v['e93_D_w']:.3f} | {v['scaled_w']:.3f} | {f3(v['difference_w'])} | "
                 f"{'—' if v['ratio_to_e93'] is None else round(v['ratio_to_e93'], 4)} |")
    txt = "\n".join(L) + "\n"
    print(txt)
    if a.md:
        open(a.md, "w").write(txt)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=lambda o: None)


if __name__ == "__main__":
    main()
