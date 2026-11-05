#!/usr/bin/env python3
"""E175 (Q143(g) fix pass; dated note A2 beside E175.md): dated note A2's reading of E175-A2-M1, run at the desk after the registered scorer
(score_e175.py, unchanged) has written its results.json. It changes no verdict and no rule. It re-derives E175-A2-M1 and the clock beside it
from the scorer's own per-tile blocks (score.reported.tiles: the measured means and both models' recomputed predictions) with the registered
engine (E173's p8gov.paired, unchanged; the scorer's tiles in name order; minimum A2_all) and refuses unless both equal the scorer's. Then it
adds what dated note A2 registers beside them:

  * E175-A2-M1c (reported, never a verdict): the same engine with its own rule id's seed (80,000 + the sum of the character codes of
    "E175-A2-M1c"), on each model's board errors less that model's own mean in each frozen group (governed, pinned), so each group's level is
    removed and only the tile-to-tile pattern of the two predictions is compared; and its clock form beside;
  * Bg's and Bp's means (measured - M10 carried, governed and pinned) and on which side of the predictions they lie;
  * delta = M9's part - M10 carried on each tile, the session's delta-weighted board error abar_delta = sum(delta a) / sum(delta), theta =
    sum(delta^2) / (2 sum(delta)), and the identity mean(a^2) - mean(b^2) = 2 mean(delta) (abar_delta - theta), by which M1's point is below 0
    exactly when abar_delta < theta; the pinned tiles' share of sum(delta);
  * the sentence dated note A2's reading gives: a resolved M1 with the session's board on its own side (BETTER with the board below both
    models' predictions in both groups, WORSE with it above both, when M10 carried's predictions are the lower on average, as on E175's tiles)
    is the session's board level, not evidence on D; any other resolved M1 is evidence on D only when M1c resolves the same way, else a group's
    board level; NOT RESOLVED is read as a board level too small against the errors' spread, never as "the part's own error hides the D
    difference". The clock beside is read the same way, and reported.

    /usr/bin/python3 -B tools/claims-v3/e175/m1_reading_e175.py <data dir>/results.json --out <data dir>/m1-reading.json > <data dir>/m1-reading.txt

Exit: 0 read (also when M1 reads NOT SCORED: then nothing is read); 2 refused (the results' M1 or its clock beside is not the registered engine's
on the results' own tiles, a tile's group is not the frozen one, or a frozen input differs); 3 not score_e175.py's results.
Standard library, and the frozen predictor (numpy) for the rule seeds, as the scorer. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import e175_common as C  # noqa: E402
import p8gov as G  # noqa: E402  (E173's, imported unchanged: the paired engine)

PRED_PATH = os.path.join(HERE, "predictions-e175.json")
RULE_M1, RULE_M1C = "E175-A2-M1", "E175-A2-M1c"
SAME_KEYS = ("rule", "n", "minimum", "seed", "verdict", "point", "ci95", "rms_a", "rms_b")
NOTE = "dated note A2 beside E175.md (Q143(g) fix pass): reported, never a verdict; no rule, line, set, stop or order changes"


class Refused(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def mean(v):
    return sum(v) / len(v) if v else None


def centred(v, groups):
    out = list(v)
    for g in set(groups):
        idx = [i for i, h in enumerate(groups) if h == g]
        m = sum(v[i] for i in idx) / len(idx)
        for i in idx:
            out[i] = v[i] - m
    return out


def same(r, want):
    return {k: (r.get(k), want.get(k)) for k in SAME_KEYS if r.get(k) != want.get(k)}


def side_of(ga, gb):
    """ga, gb: {group: mean of M10 carried's errors}, {group: mean of M9's part's errors}, over the scored groups. "below" if, in every group,
    both models' errors average below 0 (the board below both predictions); "above" if both average above 0 in every group; else "mixed"."""
    gs = [g for g in ga if ga[g] is not None and gb.get(g) is not None]
    if gs and all(max(ga[g], gb[g]) < 0 for g in gs):
        return "below"
    if gs and all(min(ga[g], gb[g]) > 0 for g in gs):
        return "above"
    return "mixed"


def sentence(v, vc, side, ga, gb, abar, theta, dbar):
    ms = (f"Bg's mean {ga['governed']:+.3f} W, Bp's mean {ga['pinned']:+.3f} W; M9's part's means {gb['governed']:+.3f} and {gb['pinned']:+.3f} W"
          if ga.get("governed") is not None and ga.get("pinned") is not None else f"the groups' means, M10 carried {ga}, M9's part {gb}")
    lvl = f"abar_delta {abar:+.4f} W against theta {theta:.4f} W" if abar is not None else "abar_delta not defined"
    if v.startswith("NOT SCORED"):
        return "NOT SCORED", f"E175-A2-M1 {v}: nothing to read"
    if v == "NOT RESOLVED":
        return ("NOT RESOLVED: no reading on D",
                f"E175-A2-M1 NOT RESOLVED: the session's board level ({ms}; {lvl}) is too small against the errors' spread for the paired test to "
                f"resolve the two models' near-constant difference; it says nothing on D (E175-A2-M1c, reported: {vc})")
    m10_low = dbar is not None and dbar > 0          # M9's part above M10 carried on average (delta = M9's part - M10 carried)
    own_side = ("below" if m10_low else "above") if v == "BETTER" else ("above" if m10_low else "below")
    nearer = (("M10 carried's lower" if m10_low else "M10 carried's higher") if v == "BETTER"
              else ("M9's part's higher" if m10_low else "M9's part's lower"))
    where = {"below": "below both models' predictions in both groups", "above": "above both models' predictions in both groups",
             "mixed": "on different sides of the predictions in the two groups, or between them"}[side]
    if side == own_side:
        return (f"{v}: the session's board level, not evidence on D",
                f"E175-A2-M1 {v}: the session's board read {where} ({ms}; {lvl}), where {nearer} predictions are nearer: the session's board "
                f"level, not evidence on D (dated note A2), and the registration's sentence for {v} is not written; E175-A2-M1c (each group's level "
                f"removed), reported: {vc}")
    if vc == v:
        return (f"{v}: evidence on D",
                f"E175-A2-M1 {v} with the session's board {where} ({ms}; {lvl}), and E175-A2-M1c {vc} with each group's level removed: "
                + ("M10's D (its refit and term b's counts) does better than M9's on these kinds under the governor" if v == "BETTER"
                   else "M10's D does worse than M9's here")
                + " (dated note A2: a weak reading at this design, which resolves the two models' D in few sessions)")
    return (f"{v}: the session's board level, not evidence on D",
            f"E175-A2-M1 {v}: the session's board read {where} ({ms}; {lvl}); E175-A2-M1c (each group's level removed) reads {vc}, so this is a "
            f"group's board level, not evidence on D (dated note A2), and the registration's sentence for {v} is not written")


def read(res, P, A):
    sc = res.get("score", res) if isinstance(res, dict) else None
    if not isinstance(sc, dict):
        raise Refused(3, "refused: not score_e175.py's results (no score)")
    if "rules" not in sc:
        if "note" in sc:
            return {"note": NOTE, "verdict": "NOT SCORED", "why": sc["note"], "reading": "NOT SCORED"}
        raise Refused(3, "refused: not score_e175.py's results (no rules)")
    rules, rep = sc["rules"], sc.get("reported") or {}
    M1 = rules.get(RULE_M1)
    if M1 is None or "tiles" not in rep or "E175-A2-M1_clock_beside" not in rep:
        raise Refused(3, "refused: not score_e175.py's results (no E175-A2-M1, reported tiles or clock beside)")
    mn = P["rules"]["minimum_tiles"]["A2_all"]
    T = rep["tiles"]
    names = sorted(n for n in T if T[n].get("burst_w") is not None and T[n].get("M10") and T[n].get("M9"))
    for n in names:
        if n not in P["tiles"] or T[n].get("group") != P["tiles"][n]["group"]:
            raise Refused(2, f"refused: {n}'s group is not the frozen file's")
    groups = [P["tiles"][n]["group"] for n in names]
    a = [float(T[n]["burst_w"]) - float(T[n]["M10"]["burst_board_w"]) for n in names]
    b = [float(T[n]["burst_w"]) - float(T[n]["M9"]["burst_board_w"]) for n in names]
    namesm = sorted(n for n in names if T[n].get("burst_mhz") is not None)
    am = [float(T[n]["burst_mhz"]) - float(T[n]["M10"]["burst_mhz"]) for n in namesm]
    bm = [float(T[n]["burst_mhz"]) - float(T[n]["M9"]["burst_mhz"]) for n in namesm]
    r1 = G.paired(RULE_M1, a, b, mn, A)
    d1 = same(r1, M1)
    if d1:
        raise Refused(2, f"refused: E175-A2-M1 re-derived from the results' own tiles is not the scorer's: {d1}")
    rk = G.paired(RULE_M1, am, bm, mn, A)
    dk = same(rk, rep["E175-A2-M1_clock_beside"])
    if dk:
        raise Refused(2, f"refused: the clock beside E175-A2-M1, re-derived, is not the scorer's: {dk}")
    gi = [i for i, g in enumerate(groups) if g == "governed"]
    pi = [i for i, g in enumerate(groups) if g == "pinned"]
    mg = mean([a[i] for i in gi]) if gi else None
    mp = mean([a[i] for i in pi]) if pi else None
    out = {"note": NOTE, "M1": M1, "M1_rederived_equal": True, "M1_clock_beside": rep["E175-A2-M1_clock_beside"], "M1_clock_beside_rederived_equal": True,
           "n": len(names), "governed": len(gi), "pinned": len(pi), "Bg_mean_w": G.r4(mg), "Bp_mean_w": G.r4(mp),
           "Bg_rule_mean_w": (rules.get("E175-A2-Bg") or {}).get("mean"), "Bp_rule_mean_w": (rules.get("E175-A2-Bp") or {}).get("mean")}
    if M1["verdict"].startswith("NOT SCORED"):
        out.update(verdict=M1["verdict"], reading="NOT SCORED", sentence=f"E175-A2-M1 {M1['verdict']}: nothing to read",
                   M1c={"rule": RULE_M1C, "verdict": M1["verdict"]})
        return out
    delta = [x - y for x, y in zip(a, b)]
    sd = sum(delta)
    abar = sum(d * x for d, x in zip(delta, a)) / sd if sd else None
    theta = sum(d * d for d in delta) / (2.0 * sd) if sd else None
    lhs = sum(x * x for x in a) / len(a) - sum(y * y for y in b) / len(b)
    rhs = 2.0 * (sd / len(a)) * (abar - theta) if sd else None
    ac, bc = centred(a, groups), centred(b, groups)
    gm = [P["tiles"][n]["group"] for n in namesm]
    acm, bcm = centred(am, gm), centred(bm, gm)
    rc = G.paired(RULE_M1C, ac, bc, mn, A)
    rck = G.paired(RULE_M1C, acm, bcm, mn, A)
    ga = {"governed": mg, "pinned": mp}
    gb = {"governed": mean([b[i] for i in gi]) if gi else None, "pinned": mean([b[i] for i in pi]) if pi else None}
    ga = {k: v for k, v in ga.items() if v is not None}
    gb = {k: v for k, v in gb.items() if v is not None}
    sd_ = side_of(ga, gb)
    reading, sent = sentence(M1["verdict"], rc["verdict"], sd_, ga, gb, abar, theta, mean(delta))
    out.update(verdict=M1["verdict"], M1c=rc, M1c_clock_beside=rck, side=sd_, M9_group_means_w={k: G.r4(v) for k, v in gb.items()},
               delta_w={"mean": G.r4(mean(delta)), "governed_mean": G.r4(mean([delta[i] for i in gi])) if gi else None,
                        "pinned_mean": G.r4(mean([delta[i] for i in pi])) if pi else None, "min": G.r4(min(delta)), "max": G.r4(max(delta)),
                        "pinned_share_of_sum": G.r4(sum(delta[i] for i in pi) / sd) if sd and pi else None},
               abar_delta_w=G.r4(abar, 5), theta_w=G.r4(theta, 5),
               identity={"mean_a2_minus_mean_b2": G.r4(lhs, 7), "two_mean_delta_times_abar_minus_theta": G.r4(rhs, 7) if rhs is not None else None,
                         "point_below_0": bool(r1["point"] < 0) if r1.get("point") is not None else None,
                         "abar_below_theta": bool(abar < theta) if abar is not None else None},
               reading=reading, sentence=sent,
               clock_beside_reading=(f"the clock beside reads {rk['verdict']}, its centred form {rck['verdict']} (reported; dated note A2 reads it the "
                                     "same way: a resolved clock beside is the session's governed clock level unless its centred form resolves the same way)"))
    return out


def run(path, out=None):
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise Refused(2, "refused: " + "; ".join(bad))
    A = C.a2p()
    with open(PRED_PATH) as f:
        P = json.load(f)
    with open(path) as f:
        res = json.load(f)
    r = read(res, P, A)
    r["inputs_sha256"] = {"results": C.sha256_file(path), "predictions-e175.json": C.sha256_file(PRED_PATH), "m1_reading_e175.py": C.sha256_file(__file__),
                          "p8gov.py": C.sha256_file(G.__file__)}
    if out:
        with open(out, "w") as f:
            json.dump(r, f, indent=1, sort_keys=True)
            f.write("\n")
    return r


def report(r):
    L = [f"E175-A2-M1, read by dated note A2 ({NOTE})"]
    if r.get("reading") == "NOT SCORED" and "M1" not in r:
        L.append(f"  NOT SCORED: {r.get('why')}")
        return "\n".join(L)
    m = r["M1"]
    L.append(f"  E175-A2-M1 (the registered verdict, re-derived equal: {r['M1_rederived_equal']}): {m['verdict']} {m.get('ci95')} point {m.get('point')} "
             f"(n {m.get('n')})")
    if r["reading"] == "NOT SCORED":
        L.append("  " + r["sentence"])
        return "\n".join(L)
    L.append(f"  E175-A2-M1c (reported): {r['M1c']['verdict']} {r['M1c'].get('ci95')} point {r['M1c'].get('point')}")
    L.append(f"  Bg's mean {r['Bg_mean_w']:+.4f} W, Bp's mean {r['Bp_mean_w']:+.4f} W: {r['side']}; delta mean {r['delta_w']['mean']:+.4f} W "
             f"(governed {r['delta_w']['governed_mean']}, pinned {r['delta_w']['pinned_mean']}; the pinned share of sum(delta) {r['delta_w']['pinned_share_of_sum']})")
    L.append(f"  abar_delta {r['abar_delta_w']} W, theta {r['theta_w']} W; identity: {r['identity']}")
    L.append(f"  READING: {r['reading']}")
    L.append(f"  {r['sentence']}")
    L.append(f"  clock beside: {r['M1_clock_beside']['verdict']} {r['M1_clock_beside'].get('ci95')}; centred {r['M1c_clock_beside']['verdict']} "
             f"{r['M1c_clock_beside'].get('ci95')}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        r = run(a.results, a.out)
    except Refused as e:
        print(str(e))
        return e.code
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"refused: not score_e175.py's results ({type(e).__name__}: {e})")
        return 3
    print(report(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
