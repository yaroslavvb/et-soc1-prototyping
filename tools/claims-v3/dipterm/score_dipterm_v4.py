#!/usr/bin/env python3
"""The dip term's scorer, v4 (dated amendment A1, REGISTRATION.md.dated-note-4.md). It is v2's scorer (a tile's measured
clock and board are the run's committed tile means; arm none must reproduce the committed rule to 0.001 or it refuses) on
A1's rules:
  DT-N   on A1-1's fall rule over A1-3's scope (the registered DT-N is printed beside it, for reference only);
  DT-L   from A1-2's calibration (its first fall in a clear process);
  arms   none, count, seq (the term's primary), oracle (POST HOC by construction), each by A1-4's Monte Carlo (8 batches of
         500 draws, seeds 145-152), with each rule figure's Monte Carlo standard error from the batches;
  seq-gc REPORTED, never a verdict: dated note 2's arm (a governed pass's deficits x K_GC), on A1's calibration;
  seq-lag REPORTED, never a verdict: the seq arm's board deficit with the meter lag at 0.17 s (A1-6).
Card 0's climb after a fall is A1-5's. dipterm.py, score_dipterm.py, score_dipterm_v2.py and score_dipterm_v3.py are
imported unchanged.

    python3 score_dipterm_v4.py --session <dir> --results <results.json> --card a2|c0 [--blocks BURST]
        [--clock-rule <id> --clock-set pinned|governed|all] [--board-rule <id> --board-set pinned|governed|all]
        [--predictions <frozen predictions json> --relation <m9_a2.json>] [--arms none,count,seq,oracle,seq-gc,seq-lag]
        [--out <file.json>]
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
import dipterm_a1 as A1  # noqa: E402
import score_dipterm as S1  # noqa: E402
import score_dipterm_v3 as V3  # noqa: E402  (dated note 2's K_GC)

K_GC = V3.K_GC


def _sha(name):
    return hashlib.sha256(open(os.path.join(HERE, name), "rb").read()).hexdigest()


def near_line(rule, rms, mean, se_r, se_m):
    """A1-4: the lines a figure lies within two Monte Carlo standard errors of."""
    import re
    out = []
    if rule.get("range_95"):
        hi = float(rule["range_95"][1])
        if se_r is not None and abs(rms - hi) < 2 * se_r:
            out.append(f"rms {rms:.4f} within 2 se ({se_r:.4f}) of its line {hi:.3f}")
        return out
    txt = rule.get("line", "")
    a = re.search(r"rms <= ([0-9.]+)", txt)
    b = re.search(r"\|mean\| <= ([0-9.]+)", txt)
    if a and se_r is not None and abs(rms - float(a.group(1))) < 2 * se_r:
        out.append(f"rms {rms:.4f} within 2 se ({se_r:.4f}) of its line {float(a.group(1)):.3f}")
    if b and se_m is not None and abs(abs(mean) - float(b.group(1))) < 2 * se_m:
        out.append(f"|mean| {abs(mean):.4f} within 2 se ({se_m:.4f}) of its line {float(b.group(1)):.3f}")
    return out


def figures(rule, kind, gset, tiles, by_tile, P, lag=0, scale=None):
    """The rule's rms and mean on the pooled deficits and on each batch's, with the tiles' detail (pooled)."""
    nb = len(next(iter(P.values()))["clock_batches"]) if P else 1

    def dfc(x, b):
        rec = P[x["run"]]
        if kind == "clock":
            v = rec["clock_deficit_mhz"] if b is None else rec["clock_batches"][b]
        else:
            v = rec["board_deficit_w"][lag] if b is None else rec["board_batches"][lag][b]
        return v * (scale(x["run"]) if scale else 1.0)

    out = {}
    for b in [None] + list(range(nb)):
        errs, det = [], {}
        for t, rec in sorted(tiles.items()):
            if gset != "all" and S1.group_of(rec) != gset:
                continue
            rr = by_tile.get(t, [])
            if not rr:
                continue
            d = sum(dfc(x, b) for x in rr if x["run"] in P) / len(rr)
            if kind == "clock":
                meas, pr = float(rec["burst_mhz"]), float(rec["M10"]["burst_mhz"]) - d
            else:
                meas, pr = float(rec["burst_w"]), float(rec["M10"]["burst_board_w"]) - d
            e = meas - pr
            errs.append(e)
            if b is None:
                det[t] = {"measured": round(meas, 3), "predicted": round(pr, 3), "term": round(-d, 3), "error": round(e, 3),
                          "passes": len(rr), "runs": [x["run"] for x in rr]}
        out[b] = (DT.rms(errs), DT.mean(errs), len(errs), det)
    rms, mean, n, det = out[None]
    v, how = S1.line_verdict(rule, rms, mean)
    br = [out[b][0] for b in range(nb)]
    bm = [out[b][1] for b in range(nb)]
    se_r = A1.mc_se(br) if nb > 1 else None
    se_m = A1.mc_se(bm) if nb > 1 else None
    return {"n": n, "rms": round(rms, 4), "mean": round(mean, 4), "verdict": v, "line": how,
            "mc_se_rms": round(se_r, 4) if se_r is not None else None, "mc_se_mean": round(se_m, 4) if se_m is not None else None,
            "near_line": near_line(rule, rms, mean, se_r, se_m),
            "batches": [[round(x, 4), round(y, 4)] for x, y in zip(br, bm)],
            "committed": {"rms": rule["rms"], "mean": rule["mean"], "verdict": rule["verdict"]}, "tiles": det}


def score(a, cache=None):
    R = json.load(open(a.results))
    blocks = tuple(x for x in (a.blocks or "BURST").split(",") if x) if a.blocks != "all" else None
    procs = A1.load_session(a.session, blocks)
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
    gov = {r["run"] for r in R["run_rows"] if S1.group_of(tiles.get(S1.tile_of(r["label"]), {}) or {"group": "none"}) == "governed"}
    out = {"session": os.path.basename(os.path.normpath(a.session)), "card": a.card, "scorer": "score_dipterm_v4.py",
           "amendment": "A1 (REGISTRATION.md.dated-note-4.md)", "blocks": list(blocks) if blocks else "all",
           "sha256": {f: _sha(f) for f in ("dipterm.py", "dipterm_a1.py", "score_dipterm_v4.py")},
           "processes": len(procs), "DT-N": A1.count_rule(procs, a.card),
           "DT-N_registered_for_reference": {k: v for k, v in DT.count_rule(procs, a.card).items() if k != "form"},
           "scope": {"in_scope": sum(p["a1"]["in_scope"] for p in procs), "clear": sum(p["a1"]["clear"] for p in procs),
                     "alarm": [p["run"] for p in procs if p["a1"]["alarm"]],
                     "not_clear": [{"run": p["run"], "ring": p["a1"]["ring"]} for p in procs if not p["a1"]["clear"]]},
           "arms": {}}
    arms = a.arms.split(",")
    base = sorted({x for x in arms if x in ("none", "count", "seq", "oracle")} | ({"seq"} if ({"seq-gc", "seq-lag"} & set(arms)) else set()))
    cal = A1.calibration(procs, a.card, "a1")
    preds = {}
    for arm in base:
        key = (a.session, a.card, arm, a.blocks)
        if cache is not None and key in cache:
            preds[arm] = cache[key]
        else:
            preds[arm] = A1.predict(procs, a.card, f_ref, dP if dP else None, arm, cal=cal)
            if cache is not None:
                cache[key] = preds[arm]
    if "seq" in preds:
        out["DT-L"] = A1.lattice_rule(procs, a.card, preds["seq"])
        out["calibration"] = {"first_process": preds["seq"]["calibration_first_process"],
                              "first_run": procs[preds["seq"]["calibration_first_process"]]["run"]
                              if preds["seq"]["calibration_first_process"] is not None else None,
                              "first_skipped": preds["seq"]["first_skipped"], "off_lattice": preds["seq"]["off_lattice"]}
    for arm in arms:
        src = "seq" if arm in ("seq-gc", "seq-lag") else arm
        P = {p["run"]: p for p in preds[src]["processes"]}
        label = {"oracle": "POST HOC by construction (the lattice fitted on all of the session's falls)",
                 "seq-gc": f"seq-gc (dated note 2, on A1's calibration): REPORTED, never a verdict; governed passes' deficits x {K_GC}",
                 "seq-lag": f"seq-lag (A1-6): REPORTED, never a verdict; the seq arm's board deficit at a {A1.BOARD_LAG_SENS_S} s meter lag"
                 }.get(arm, arm)
        res = {"label": label, "late_climbs_expected": round(sum(p["p_late_climb"] for p in preds[src]["processes"]), 3),
               "falls_expected": round(sum(sum(p["p_fall"].values()) for p in preds[src]["processes"]), 3)}
        scale = (lambda run: K_GC if run in gov else 1.0) if arm == "seq-gc" else None
        for kind, rid, gset in (("clock", a.clock_rule, a.clock_set), ("board", a.board_rule, a.board_set)):
            if not rid or (arm == "seq-lag" and kind == "clock"):
                continue
            rule = R["score"]["rules"][rid]
            f = figures(rule, kind, gset, tiles, by_tile, P, lag=1 if arm == "seq-lag" else 0, scale=scale)
            if arm == "none" and (abs(f["rms"] - float(rule["rms"])) > 1e-3 or abs(f["mean"] - float(rule["mean"])) > 1e-3):
                raise SystemExit(f"refused: arm none gives {rid} rms {f['rms']:.4f} mean {f['mean']:.4f}; committed {rule['rms']} {rule['mean']}")
            res[f"DT-{rid}"] = f
        out["arms"][arm] = res
    return out


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", required=True)
    ap.add_argument("--results", required=True)
    ap.add_argument("--card", required=True, choices=sorted(DT.PERIOD_PRIOR_MS))
    ap.add_argument("--blocks", default="BURST", help="the session's registered burst block(s), comma-separated, or 'all'")
    ap.add_argument("--clock-rule")
    ap.add_argument("--clock-set", default="pinned")
    ap.add_argument("--board-rule")
    ap.add_argument("--board-set", default="pinned")
    ap.add_argument("--predictions")
    ap.add_argument("--relation")
    ap.add_argument("--arms", default="none,count,seq,oracle,seq-gc,seq-lag")
    ap.add_argument("--out")
    return ap


def main():
    a = parser().parse_args()
    out = score(a)
    s = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(s + "\n")
    brief = {"session": out["session"], "DT-N": {k: out["DT-N"][k] for k in ("eligible_gaps", "expected", "band_95", "observed_falls", "verdict")}}
    if "DT-L" in out:
        brief["DT-L"] = {k: out["DT-L"][k] for k in ("later_falls", "sensitivity", "ppv", "verdict")}
    brief["arms"] = {arm: {k: {kk: v[kk] for kk in ("n", "rms", "mean", "verdict", "mc_se_rms", "mc_se_mean", "near_line")}
                           for k, v in res.items() if k.startswith("DT-")} for arm, res in out["arms"].items()}
    print(json.dumps(brief, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
