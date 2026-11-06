#!/usr/bin/env python3
"""The dip term's scorer for one governed session (REGISTRATION.md section 4). Frozen with the registration.

    python3 score_dipterm.py --session <session dir> --results <the run's results.json> --card a2|c0
        [--clock-rule <rule id> --clock-set pinned|governed|all] [--board-rule <rule id> --board-set pinned|governed|all]
        [--predictions <frozen predictions json> --relation <m9_a2.json>] [--arms none,count,seq] [--out <file.json>]

It reads the session's launch records (launches.jsonl.gz) and the run's own registered results.json (its run_rows, its
per-tile M10 predictions under score.reported.tiles and its rules' lines under score.rules). It refuses unless the arm
"none" reproduces the committed rule's rms and mean to 0.001. Then:
  DT-N   the count of falls over the eligible gaps (dipterm.count_rule)
  DT-L   the sequential lattice's predictions of the later falls (dipterm.lattice_rule)
  DT-<clock rule>, DT-<board rule>   the run's own rule re-scored with each arm's predicted clock (the tile's M10 clock less
         the mean over its counted passes of the arm's expected deficit) and board (its M10 board less the expected board
         deficit, aifoundry2 only: M9's aifoundry2 relation gives the levels at 600 and 700 MHz), on the rule's own line.
Arm "oracle" (the lattice fitted on all of the session's falls) is post hoc by construction and is labelled so.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dipterm as DT  # noqa: E402


def tile_of(label):
    return label.split("-", 1)[1] if "-" in label else label


def group_of(rec):
    return rec.get("group") or rec.get("set") or "pinned"


def d_of(pred, tile):
    t = (pred or {}).get("tiles", {}).get(tile)
    if not t:
        return None
    m = t.get("M10") or (t.get("models") or {}).get("M10") or {}
    return m.get("D600_a3_footing_w"), t.get("type") or tile.split(".", 1)[0]


def line_verdict(rule, rms, mean):
    if rule.get("range_95"):
        hi = rule["range_95"][1]
        return ("PASS" if rms <= hi else "FAIL"), f"rms <= {hi:.3f} (the rule's own 97.5% point)"
    txt = rule.get("line", "")
    if "rms" in txt and "mean" in txt:
        import re
        a = re.search(r"rms <= ([0-9.]+)", txt)
        b = re.search(r"\|mean\| <= ([0-9.]+)", txt)
        ok = rms <= float(a.group(1)) and abs(mean) <= float(b.group(1))
        return ("PASS" if ok else "FAIL"), txt
    if "mean" in txt:
        import re
        b = re.search(r"\|mean\| <= ([0-9.]+)", txt)
        return ("PASS" if abs(mean) <= float(b.group(1)) else "FAIL"), txt
    return "NOT SCORED", txt


def score(a):
    R = json.load(open(a.results))
    procs = DT.load_session(a.session)
    tiles = R["score"]["reported"]["tiles"]
    rows = [r for r in R["run_rows"] if r.get("counted")]
    by_tile = {}
    for r in rows:
        by_tile.setdefault(tile_of(r["label"]), []).append(r)
    f_ref, dP = {}, {}
    pred = json.load(open(a.predictions)) if a.predictions else None
    rel = json.load(open(a.relation))["relation"] if a.relation else None
    for r in R["run_rows"]:
        t = tile_of(r["label"])
        m = (tiles.get(t) or {}).get("M10") or {}
        f_ref[r["run"]] = float(m.get("burst_mhz", 800.0))
        if rel is not None and a.card == "a2":
            dd = d_of(pred, t)
            if dd and dd[0] is not None:
                dP[r["run"]] = DT.board_drops(rel, dd[1], dd[0], f_ref[r["run"]])
    out = {"session": os.path.basename(os.path.normpath(a.session)), "card": a.card, "dipterm_sha256": DT_SHA,
           "processes": len(procs), "DT-N": DT.count_rule(procs, a.card), "arms": {}}
    arms = a.arms.split(",")
    preds = {}
    for arm in arms:
        preds[arm] = DT.predict(procs, a.card, f_ref, dP if dP else None, arm)
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
                if gset != "all" and group_of(rec) != gset:
                    continue
                rr = by_tile.get(t, [])
                if not rr:
                    continue
                if kind == "clock":
                    meas = sum(float(x["burst_mhz"]) for x in rr) / len(rr)
                    dfc = sum(P[x["run"]]["clock_deficit_mhz"] for x in rr if x["run"] in P) / len(rr)
                    pr = float(rec["M10"]["burst_mhz"]) - dfc
                else:
                    meas = sum(float(x["burst_w"]) for x in rr) / len(rr)
                    dfc = sum(P[x["run"]]["board_deficit_w"] for x in rr if x["run"] in P) / len(rr)
                    pr = float(rec["M10"]["burst_board_w"]) - dfc
                e = meas - pr
                errs.append(e)
                det[t] = {"measured": round(meas, 3), "predicted": round(pr, 3), "term": round(-dfc, 3), "error": round(e, 3),
                          "passes": len(rr)}
            rms, mean = DT.rms(errs), DT.mean(errs)
            v, how = line_verdict(rule, rms, mean)
            if arm == "none":
                if abs(rms - float(rule["rms"])) > 1e-3 or abs(mean - float(rule["mean"])) > 1e-3:
                    raise SystemExit(f"refused: arm none gives {rid} rms {rms:.4f} mean {mean:.4f}; committed {rule['rms']} {rule['mean']}")
            res[f"DT-{rid}"] = {"n": len(errs), "rms": round(rms, 4), "mean": round(mean, 4), "verdict": v, "line": how,
                                "committed": {"rms": rule["rms"], "mean": rule["mean"], "verdict": rule["verdict"]}, "tiles": det}
        out["arms"][arm] = res
    return out


DT_SHA = None


def main():
    global DT_SHA
    import hashlib
    DT_SHA = hashlib.sha256(open(os.path.join(HERE, "dipterm.py"), "rb").read()).hexdigest()
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
    brief = {k: out[k] for k in ("session", "card", "processes") if k in out}
    brief["DT-N"] = {k: out["DT-N"][k] for k in ("eligible_gaps", "expected", "band_95", "observed_falls", "verdict")}
    if "DT-L" in out:
        brief["DT-L"] = {k: out["DT-L"][k] for k in ("later_falls", "sensitivity", "ppv", "verdict")}
    brief["arms"] = {arm: {k: ({kk: v[kk] for kk in ("n", "rms", "mean", "verdict")} if isinstance(v, dict) else v)
                           for k, v in res.items() if k != "label"} for arm, res in out["arms"].items()}
    print(json.dumps(brief, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
