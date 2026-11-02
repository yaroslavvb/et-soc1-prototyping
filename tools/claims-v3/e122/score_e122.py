#!/usr/bin/env python3
"""E122 (Q134): score E108's frozen rules on E122's reduction (E108's tiles on aifoundry3 card 0) and read-back, plus the
cross-card rules of predictions-e122.json. Registration: E122.md. Written with the pre-registration, before any pass exists.

    python3 tools/claims-v3/e122/score_e122.py --e122 e122.json --readback readback.jsonl [--arm name=<json> ...]
        [--md results.md] [--json scored.json]

It reuses score_e108.py's own functions unchanged (read_rows, score_read, score_power, write_md; its sha256 is checked
against predictions-e122.json first), on a copy of predictions-e108.json in which only this card's references are
substituted (predictions-e122.json > substitutions: R2's step references, S1's tie cells, M4's predictions without E108's
card-1 scale). Every line and threshold is E108's. It adds:
  X  the cross-card rules: d = Q122 - s*Q108 (s = E82's per-type card scale for W contrasts, 1 for ratios),
     h = sqrt(h122^2 + (s*h108)^2); PASS if |d| + h <= w, FAIL if |d| - h > w, else INCONCLUSIVE. Aggregate: PASS if no
     X rule FAILs and at least half PASS; FAIL if 3 or more FAIL; else INCONCLUSIVE.
  =  how many of E108's thirteen verdicts come out the same here.
The unit of replication is the pass. Fewer than 2 kept passes: every power rule NOT SCORED (E108's rule). Every verdict
is also computed at each registered arm, and a verdict that moves is marked arm-sensitive. Standard library only.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SL = os.path.join(ROOT, "tools", "claims-v3", "signloc")
REG_PATH = os.path.join(HERE, "predictions-e122.json")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


REG = json.load(open(REG_PATH))
_hd = REG["harness"]
for _rel, _want in list(_hd["desk_code_unchanged_sha256"].items()) + [
        (k, v) for k, v in _hd["card_code_unchanged_sha256"].items() if k.endswith(("predictions-e108.json", "e108.json"))]:
    if sha(os.path.join(ROOT, _rel)) != _want:
        raise SystemExit(f"refusing to score: {_rel} differs from the sha256 E122 froze")
sys.path.insert(0, SL)
import score_e108 as s108  # noqa: E402  (after the check)

REG108 = json.load(open(s108.REG))
SPEC = json.load(open(s108.SPEC))


def reg_for_card(reg108=REG108, reg122=REG):
    """predictions-e108.json with this card's references substituted; nothing else changes."""
    r = copy.deepcopy(reg108)
    sub = reg122["substitutions"]
    r["rules"]["E108-R2"]["e106_w"] = dict(sub["rules.E108-R2.e106_w"]["value"])
    r["session_tie"] = {"reference": sub["session_tie.reference"],
                        "cells": {c: {"ref_w": v["ref_w"], "band_w": v["band_w"]} for c, v in sub["session_tie.cells"].items()}}
    for n, v in sub["tiles.pred"].items():
        r["tiles"][n]["pred"].update({"M": v["M"], "lo95": v["lo95"], "hi95": v["hi95"]})
    for n, v in sub["quantities.M"].items():
        r["quantities"][n]["M"] = v["M"]
        r["quantities"][n]["half95"] = v["half95"]
    r["card"] = {"name": reg122["card"]["name"], "device": 0, "clock_mhz": 600,
                 "config_gate": {"expected": reg122["card"]["config_expected"]}}
    return r


REGC = reg_for_card()


def x_verdict(q, x, min_n):
    if q is None or q.get("mean") is None or q.get("ci95") is None or (q.get("n") or 0) < min_n:
        return "UNRESOLVED", None, None
    s = x["scale"]
    d = q["mean"] - s * x["e108"]["mean"]
    h = math.sqrt(q["ci95"] ** 2 + (s * x["e108"]["ci95"]) ** 2)
    w = x["w"]
    return ("PASS" if abs(d) + h <= w else "FAIL" if abs(d) - h > w else "INCONCLUSIVE"), d, h


def score(res, rows=None, reg122=REG, regc=REGC):
    prim = s108.score_power(res, regc)
    if rows is not None:
        rr, rt = s108.score_read(rows, regc)
        prim["rules"] = {**rr, **prim["rules"]}
        prim["readback_tiles"] = rt
    min_n = reg122["plan"]["min_kept_passes_scored"]
    scored = len(prim.get("passes", [])) >= min_n
    xs, tx = {}, {}
    for x in reg122["cross_card"]["rules"]:
        q = prim.get("quantities", {}).get(x["of"])
        v, d, h = x_verdict(q, x, min_n) if scored else ("NOT SCORED", None, None)
        xs[x["id"]] = {"verdict": v, "q122": None if q is None else q.get("mean"), "q122_ci95": None if q is None else q.get("ci95"),
                       "e108": x["e108"]["mean"], "e108_ci95": x["e108"]["ci95"], "scale": x["scale"],
                       "predicted": x["predicted"], "difference": d, "h": h, "w": x["w"], "unit": x["unit"]}
        tx[v] = tx.get(v, 0) + 1
    if not scored:
        agg = "NOT SCORED"
    elif tx.get("FAIL", 0) == 0 and tx.get("PASS", 0) >= reg122["cross_card"]["aggregate_min_pass"]:
        agg = "PASS"
    elif tx.get("FAIL", 0) >= 3:
        agg = "FAIL"
    else:
        agg = "INCONCLUSIVE"
    prim["cross_card"] = {"rules": xs, "tally": tx, "aggregate": agg}
    e108v = reg122["e108_verdicts"]
    same = [r for r, v in prim["rules"].items() if r in e108v and v.get("verdict") == e108v[r]]
    prim["same_verdict_as_e108"] = f"{len(same)} of {len(e108v)}"
    prim["differs_from_e108"] = {r: {"e122": prim["rules"][r]["verdict"], "e108": e108v[r]}
                                 for r in e108v if r in prim["rules"] and r not in same}
    t = {}
    for v in prim["rules"].values():
        t[v["verdict"]] = t.get(v["verdict"], 0) + 1
    prim["tally"] = t
    return prim


def f3(x, d=3):
    return "—" if x is None else f"{x:+.{d}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e122", required=True)
    ap.add_argument("--readback", default=None)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--md")
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = s108.read_rows(a.readback, SPEC)
    prim = score(json.load(open(a.e122)), rows)
    arms = {}
    for x in a.arm:
        nm, p = x.split("=", 1)
        arms[nm] = score(json.load(open(p)))
        arms[nm]["file"] = os.path.basename(p)
    for r in prim["rules"]:
        moved = {n: arms[n]["rules"].get(r, {}).get("verdict") for n in arms
                 if r in arms[n]["rules"] and arms[n]["rules"][r].get("verdict") != prim["rules"][r]["verdict"]}
        if moved:
            prim["rules"][r]["arm_sensitive"] = moved
    for xid, v in prim["cross_card"]["rules"].items():
        v["at_arms"] = {n: arms[n]["cross_card"]["rules"][xid]["verdict"] for n in arms}
        v["arm_sensitive"] = any(y != v["verdict"] for y in v["at_arms"].values())
    out = {"experiment": "E122", "predictions_sha256": sha(REG_PATH), "scorer_sha256": sha(os.path.abspath(__file__)),
           "score_e108_sha256": sha(os.path.join(SL, "score_e108.py")),
           "primary": prim, "arms": arms, "readback": {"rows": rows}}
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, default=lambda o: None)
    if a.md:
        s108.write_md(prim, arms, rows, REGC, a.md)
        body = open(a.md).read().replace("# E108 results", "# E122 results: E108's rules on aifoundry3 card 0 "
                                         "(score_e108.write_md unchanged; references substituted for this card)", 1)
        L = ["", f"**The same verdict as E108 on card 1:** {prim['same_verdict_as_e108']}; differing: "
                 f"{prim['differs_from_e108'] or 'none'}.", "",
             f"## The cross-card rules: **{prim['cross_card']['aggregate']}** {prim['cross_card']['tally']}", "",
             "| X rule | E122 | E108 × scale | difference | ± h | w | verdict | at the arms |", "|---|---|---|---|---|---|---|---|"]
        for x in REG["cross_card"]["rules"]:
            v = prim["cross_card"]["rules"][x["id"]]
            q = "—" if v["q122"] is None else (f"{v['q122']:.3f}" + ("" if v["q122_ci95"] is None else f" ± {v['q122_ci95']:.3f}"))
            mv = {k: y for k, y in v.get("at_arms", {}).items() if y != v["verdict"]}
            L.append(f"| {x['id']} | {q} | {x['e108']['mean']:.3f} × {x['scale']:.4f} = {x['predicted']:.3f} | {f3(v['difference'])} | "
                     f"{'—' if v['h'] is None else '%.3f' % v['h']} | {x['w']} | **{v['verdict']}** | "
                     f"{'; '.join(f'{k} {y}' for k, y in mv.items()) or ('same at all' if arms else '—')} |")
        open(a.md, "w").write(body + "\n".join(L) + "\n")
    print(json.dumps({r: v["verdict"] for r, v in prim["rules"].items()}, indent=0))
    print("tally", prim["tally"], "| same as E108:", prim["same_verdict_as_e108"], "| X:", prim["cross_card"]["aggregate"],
          prim["cross_card"]["tally"])


if __name__ == "__main__":
    main()
