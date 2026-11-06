#!/usr/bin/env python3
"""The dip term's scorer, v2 (REGISTRATION.md.dated-note-1.md). Identical to score_dipterm.py except in one place: a tile's
MEASURED clock and board are the run's own committed tile means (results.json > score.reported.tiles > burst_mhz, burst_w),
which the run's registered rules read, not means re-taken from run_rows (whose passes are rounded to 0.1 MHz and 0.01 W).
The run_rows still name each tile's counted passes, over which the term's expected deficits are averaged. dipterm.py, the term,
is unchanged and is imported from score_dipterm.py's own directory.

    python3 score_dipterm_v2.py <the same arguments as score_dipterm.py>
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dipterm as DT  # noqa: E402
import score_dipterm as S1  # noqa: E402


def score(a):
    R = json.load(open(a.results))
    procs = DT.load_session(a.session)
    tiles = R["score"]["reported"]["tiles"]
    rows = [r for r in R["run_rows"] if r.get("counted")]
    by_tile = {}
    for r in rows:
        by_tile.setdefault(S1.tile_of(r["label"]), []).append(r)
    f_ref, dP = {}, {}
    pred = json.load(open(a.predictions)) if a.predictions else None
    rel = json.load(open(a.relation))["relation"] if a.relation else None
    for r in R["run_rows"]:
        t = S1.tile_of(r["label"])
        m = (tiles.get(t) or {}).get("M10") or {}
        f_ref[r["run"]] = float(m.get("burst_mhz", 800.0))
        if rel is not None and a.card == "a2":
            dd = S1.d_of(pred, t)
            if dd and dd[0] is not None:
                dP[r["run"]] = DT.board_drops(rel, dd[1], dd[0], f_ref[r["run"]])
    out = {"session": os.path.basename(os.path.normpath(a.session)), "card": a.card, "scorer": "score_dipterm_v2.py",
           "dipterm_sha256": hashlib.sha256(open(os.path.join(HERE, "dipterm.py"), "rb").read()).hexdigest(),
           "processes": len(procs), "DT-N": DT.count_rule(procs, a.card), "arms": {}}
    arms = a.arms.split(",")
    preds = {arm: DT.predict(procs, a.card, f_ref, dP if dP else None, arm) for arm in arms}
    if "seq" in preds:
        out["DT-L"] = DT.lattice_rule(procs, a.card, preds["seq"])
        out["off_lattice"] = preds["seq"]["off_lattice"]
    for arm in arms:
        P = {p["run"]: p for p in preds[arm]["processes"]}
        res = {"label": "POST HOC by construction (the lattice fitted on all of the session's falls)" if arm == "oracle" else arm,
               "late_climbs_expected": round(sum(p["p_late_climb"] for p in preds[arm]["processes"]), 3),
               "falls_expected": round(sum(sum(p["p_fall"].values()) for p in preds[arm]["processes"]), 3)}
        for kind, rid, gset in (("clock", a.clock_rule, a.clock_set), ("board", a.board_rule, a.board_set)):
            if not rid:
                continue
            rule = R["score"]["rules"][rid]
            errs, det = [], {}
            for t, rec in sorted(tiles.items()):
                if gset != "all" and S1.group_of(rec) != gset:
                    continue
                rr = by_tile.get(t, [])
                if not rr:
                    continue
                if kind == "clock":
                    meas = float(rec["burst_mhz"])
                    dfc = sum(P[x["run"]]["clock_deficit_mhz"] for x in rr if x["run"] in P) / len(rr)
                    pr = float(rec["M10"]["burst_mhz"]) - dfc
                else:
                    meas = float(rec["burst_w"])
                    dfc = sum(P[x["run"]]["board_deficit_w"] for x in rr if x["run"] in P) / len(rr)
                    pr = float(rec["M10"]["burst_board_w"]) - dfc
                e = meas - pr
                errs.append(e)
                det[t] = {"measured": round(meas, 3), "predicted": round(pr, 3), "term": round(-dfc, 3), "error": round(e, 3),
                          "passes": len(rr), "runs": [x["run"] for x in rr]}
            rms, mean = DT.rms(errs), DT.mean(errs)
            v, how = S1.line_verdict(rule, rms, mean)
            if arm == "none":
                if abs(rms - float(rule["rms"])) > 1e-3 or abs(mean - float(rule["mean"])) > 1e-3:
                    raise SystemExit(f"refused: arm none gives {rid} rms {rms:.4f} mean {mean:.4f}; committed {rule['rms']} {rule['mean']}")
            res[f"DT-{rid}"] = {"n": len(errs), "rms": round(rms, 4), "mean": round(mean, 4), "verdict": v, "line": how,
                                "committed": {"rms": rule["rms"], "mean": rule["mean"], "verdict": rule["verdict"]}, "tiles": det}
        out["arms"][arm] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--card", required=True, choices=sorted(DT.PERIOD_PRIOR_MS))
    ap.add_argument("--clock-rule")
    ap.add_argument("--clock-set", default="pinned")
    ap.add_argument("--board-rule")
    ap.add_argument("--board-set", default="pinned")
    ap.add_argument("--predictions")
    ap.add_argument("--relation")
    ap.add_argument("--arms", default="none,count,seq")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = score(a)
    s = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(s + "\n")
    print(json.dumps({k: out[k] for k in ("session", "card", "DT-N")}, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
