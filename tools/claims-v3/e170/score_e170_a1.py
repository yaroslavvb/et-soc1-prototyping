#!/usr/bin/env python3
"""E170 (Q141(w)): the scorer of record, amendment A1 (E170.md.dated-note.md), written before any E170 data and before the claim.

score_e170.py (lab 574dc5b5) stays as committed and is imported unchanged: its reduction, its card term, its rules and its report. Its main()
reads every session against the full registered order. run_hpl.py gives a run the index it has in ITS protocol, so a session of the registered
subset (protocol-subset.json: passes 1, 2, 4 and 5) or of the dry twin (protocol-dry.json: passes 1 and 4) would be refused at its first run of a
later pass ("not the registered order's run at that idx"): the kit's dry pass on the Intel found it. This main() reads each session against the
registered order filtered to the passes of the protocol that session ran (its e170.json names it) and re-indexed, which is how
make_protocol_e170.py lists them. Nothing else differs: no rule, number, line, statistic or verdict.

    python3 -B tools/claims-v3/e170/score_e170_a1.py <RUNDIR> [<RUNDIR> ...] --ccheck <ccheck-<session>.json> [...] [--out results.json] [--md results.md]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e170 as SC  # noqa: E402  (unchanged)

C, S = SC.C, SC.S
PROTOCOL_PASSES = {"protocol.json": None, "protocol-subset.json": (1, 2, 4, 5), "protocol-dry.json": (1, 4)}


def order_for(P, keep=None):
    return [o for o in P["order"] if keep is None or o["pass"] in keep]


def protocol_passes(rundir):
    """the passes of the protocol a session ran (its e170.json names it); any other protocol is refused"""
    try:
        name = json.load(open(os.path.join(rundir, "e170.json")))["protocol"]
    except (OSError, ValueError, KeyError):
        raise SystemExit(f"refused: {rundir} has no readable e170.json naming its protocol")
    if name not in PROTOCOL_PASSES:
        raise SystemExit(f"refused: {rundir} ran {name}, not one of {sorted(PROTOCOL_PASSES)}")
    return PROTOCOL_PASSES[name]


def pass_by_order(P, keep=None):
    order = order_for(P, keep)

    def f(r):
        i = r.get("idx")
        if not isinstance(i, int) or not 0 <= i < len(order) or order[i]["label"] != r.get("label"):
            raise SystemExit(f"refused: run {r.get('run')} (idx {i}, label {r.get('label')}) is not its protocol's run at that idx")
        return order[i]["pass"]
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--pred", default=SC.PRED_REL)
    ap.add_argument("--ccheck", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--md")
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    P = SC.load_pred(a.pred)
    cc = S.load_ccheck(a.ccheck)
    runs = []
    for rd in a.rundirs:                        # A1: each session against its own protocol's order
        runs += S.collect([rd], cc, pass_of=pass_by_order(P, protocol_passes(rd)))
    why = SC.stray_left_out(runs, P)
    if why:
        raise SystemExit(f"refused: {why}")
    prim = SC.scoring(runs, P, "counted", a.rundirs)
    comp = SC.scoring(runs, P, "complete", a.rundirs)
    res = {"experiment": "E170", "scorer": "score_e170_a1.py (A1) over score_e170.py", "predictions_sha256": C.sha256_file(a.pred),
           "scorer_sha256": C.sha256_file(SC.__file__), "scorer_a1_sha256": C.sha256_file(__file__), "common_sha256": C.sha256_file(C.__file__),
           "score_e165_sha256": C.sha256_file(S.__file__), "m9_a2_sha256": C.m9a2().M9_SHA256, "kappa0": C.KAPPA0,
           "sessions": [os.path.basename(os.path.normpath(r)) for r in a.rundirs], "session_protocol_passes": {os.path.basename(os.path.normpath(r)): protocol_passes(r) for r in a.rundirs},
           "ccheck_files": {os.path.basename(p): C.sha256_file(p) for p in a.ccheck},
           "dry": any(m["dry"] for m in runs), "runs": len(runs), "runs_complete": sum(1 for m in runs if m["complete"]),
           "runs_counted": sum(1 for m in runs if m["counted"]), "runs_not_complete": [m["run"] for m in runs if not m["complete"]],
           "budget_stops": [m["run"] for m in runs if m["budget_stop"]], "passes": prim["passes"], "c_check": S.c_rule(runs, bool(a.ccheck)),
           "safety": SC.safety(runs, a.rundirs, P), "score": prim["score"], "as_complete_runs": comp["score"].get("rules", comp["score"]),
           "peaks": S.peaks(a.rundirs), "cells": prim["cells"],
           "run_rows": [{k: m.get(k) for k in ("session", "run", "idx", "label", "pass", "complete", "counted", "c_pass", "c_lines", "c_verdicts", "budget_stop",
                                                "burst_mhz", "burst_w", "die_start", "die_max", "p800_w", "peak_w", "c_w")} for m in runs]}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    if a.md:
        open(a.md, "w").write(SC.md(res))
    print(f"E170 scoring (A1): {res['runs']} burst runs, {res['runs_complete']} complete, {res['runs_counted']} counted, passes {res['passes']}; dry {res['dry']}; "
          f"protocols {res['session_protocol_passes']}")
    print("  E170-C:", json.dumps({k: v for k, v in res["c_check"].items() if k not in ("by_tile", "runs_not_all_pass")})[:400])
    print("  E170-S:", json.dumps(res["safety"])[:400])
    sc = res["score"]
    if "rules" in sc and "note" not in sc["rules"]:
        print(f"  tiles scored {sc['tiles_scored']}; left out {sc['left_out_fewer_than_2_passes']}")
        for k, v in sc["rules"].items():
            print(f"  {k:8s} {json.dumps(v)}")
        for k in ("arms_board", "loo_scale", "models_D", "models_board", "by_format", "by_half", "zeros_levels"):
            print(f"  [{k}] {json.dumps(sc['reported'][k])[:600]}")
    else:
        print("  " + (sc.get("note") or json.dumps(sc.get("rules"))))
    if a.md:
        print(f"results.md written: {a.md}")


if __name__ == "__main__":
    main()
