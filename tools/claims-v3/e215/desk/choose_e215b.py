#!/usr/bin/env python3
"""E215 (Q224) desk: ARM B's POINTS - DECLARED-v31.md item 10's point rule applied to aifoundry1 card 1 at 600 MHz, by MM1-v3.1's and MM1-v3's
frozen predictors as landed, on this registration's never-run scan. Written before any E215 datum. numpy through the predictors, single-threaded.

    /usr/bin/python3 -I -B tools/claims-v3/e215/desk/choose_e215b.py --scan <scan-e215.json>     writes desk/choice-e215b.json
    /usr/bin/python3 -I -B tools/claims-v3/e215/desk/choose_e215b.py --scan <scan-e215.json> --check   rebuilds it and compares (exit 0 = PASS)
    ... --tie-rel 1e-12 --out desk/choice-e215b-alt-tie.json   the REPORTED alternative of D2 (one tie class within 1e-12 relative), never used

THE RULE (item 10, registered with MM1-v3.1's declaration, 7375bc9c), arm B's quotas L 8, P 6, C 6, R 6, S 6:
  1. Candidates = the family's grid (MM1-v3.1's e215_v31.py grids, imported unchanged: L rgm136 gemmL fp32 zeros and random at 40-160 MB whose
     full-chip configuration ran on THIS card, every row-group x column-group mask with 2-28 shires; P the one-stream shapes of rgm211 gemmLn,
     rgm211 gemmL, rgm136 gemmLnc and rgm136 gemmL at 5-200 MB; C one and two K blocks; R the two-edge retention at 36-140 MB; S the kinds
     v31-counts counted, at gemmL3x1x3) less every token E213's shape-level never-run scan finds for this card (desk/neverrun_e215.py's
     literal reading for arm B: no hit counted for card 1, no MM1-v3.1 point on card 1).
  2. Score = |ln(F_v3.1 / F_v3)| of the wall cycles (S: of W over idle, F_v3 being MM1-v3's energy form at its landed constants with item 7's
     counts and phi, MM1-v3.1's e215_v31.py construction, here on card 1); a candidate either model cannot price leaves S.
  3. ceil(q / 2) by descending score (ties by the sorted token), the rest by random.Random("v3.1-blind|B|<family>").sample of the remaining
     candidates sorted by token.
  4. Fewer candidates than the quota: all of them. Over arm B's 48 card-minutes by the plan: drop from the random half first, reverse draw order.
FAMILIES L AND S (E215.md, dated departure D1, the orchestrator's ruling): by the literal shape-level rule L and S have no candidate on card 1
(every L shape's full chip ran on card 1 by the grid's own condition; S's gemmL3x1x3 ran on card 1 in E213 arm B). Beside the literal list,
as for arm A, L and S are chosen by the post hoc readings MM1-v3.1's land named - L a configuration (shape, mask) never run on card 1, S a
counted kind never run in a GEMM on card 1 (desk/neverrun_e215.py) - by the same score, draw and quotas; labelled 'points chosen post hoc
after the fit; forecasts frozen before any E215 datum' and reported apart from P, C and R in every verdict.
THE THREE READINGS (E215.md, dated departure D2, the orchestrator's answer to verify-fit-v31's findings 2 and 3): as MM1-v3.1's land applied them -
(i) a tie is an exact tie of the computed scores (TIE_REL = 0; the REPORTED alternative with one tie class within 1e-12 relative is written by
--tie-rel 1e-12 --out desk/choice-e215b-alt-tie.json and never used); (ii) family P's "(int8 at KB <= 2)" reads int8 beside fp32 (e215_v31's
grid_P); (iii) inside a shared shape token the order (arm token, loop, format, kind, mask) (e215_v31's sort_key).
THE L REPRESENTATIVE MASK (e215_v31.py's, checked here too): at a product mask both models' op times depend on (shape, |G|, |C|) only; one
representative mask a (shape, |G|, |C|) is priced and every chosen point is re-priced at its own mask (equal to 1e-12, or REFUSED).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
C1 = "aifoundry1 card 1"
FULL = "0xffffffff"
QUOTA_B = {"L": 8, "P": 6, "C": 6, "R": 6, "S": 6}
# the tie reading (E215.md D2): 0.0 = MM1-v3.1's land's reading (scores ordered as computed; only exactly equal scores tie)
TIE_REL = 0.0
OUT = os.path.join(HERE, "choice-e215b.json")
sys.path.insert(0, HERE)
import neverrun_e215 as NR  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build(scan_path, tie_rel=None):
    global TIE_REL
    if tie_rel is not None:
        TIE_REL = tie_rel
    sys.path.insert(0, V31)
    import numpy as np  # noqa: E402
    import data_v31 as DV  # noqa: E402
    import e215_v31 as G  # noqa: E402  (the grids, unchanged)
    import mm1_v31 as M31  # noqa: E402
    import energy_v31 as EV  # noqa: E402
    sys.path.insert(0, V3)
    import mm1_v3 as MV3  # noqa: E402
    import engine_v3 as E3  # noqa: E402
    import energy_v3 as EN3  # noqa: E402
    S = json.load(open(scan_path))
    p31_path = os.path.join(V31, "out", "mm1_v31_params.json")
    p3_path = os.path.join(V3, "out", "mm1_v3_params.json")
    P31, v3p = json.load(open(p31_path)), json.load(open(p3_path))
    M = M31.Model(P31)
    MV3m = MV3.Model(v3p)
    full_runs = set()
    for p in DV.time_points() + DV.energy_points():
        if p["card"] == C1 and p["kernel"] == "rgm136" and p["arm"].startswith("gemmL") and not p["arm"].startswith("gemmLn") \
                and p["fmt"] == "fp32" and p["mask"].lower() == FULL:
            b = DV.D.blocks(p["arm"])
            kinds = set(str(p.get("kind", "")).split("+"))
            for k in ("zeros", "random"):
                if k in kinds and max(b) <= 16 and 40.0 <= G.footprint(*b) <= 160.0:
                    full_runs.add((b, k))
    grids = {"L": G.grid_L(full_runs), "P": G.grid_P(), "C": G.grid_C(), "R": G.grid_R(), "S": G.grid_S()}

    def pt(c, fam_reading):
        return dict(c, arm_tag="B", id=G.token_str(c), format=c["fmt"], reading=fam_reading, role="point")

    lit, dep = {}, {}
    for fam, cs in grids.items():
        lit[fam] = [c for c in cs if NR.verdict(S, pt(c, "literal"))["never_run"]]
    dep["L"] = [c for c in grids["L"] if NR.verdict(S, pt(c, "posthoc"))["never_run"]]
    dep["S"] = [c for c in grids["S"] if NR.verdict(S, pt(c, "posthoc"))["never_run"]]

    def v3_wall(cs):
        pts = [{"arm": c["arm"], "kernel": c["kernel"], "fmt": c["fmt"], "mask": c["mask"], "f": 600.0} for c in cs]
        if not pts:
            return np.array([])
        return E3.TimeEngine(pts).predict(v3p["time"]["theta"], v3p["time"]["form"]) * 600.0

    def v31_wall(cs):
        pts = [{"arm": c["arm"], "kernel": c["kernel"], "fmt": c["fmt"], "mask": c["mask"], "f": 600.0} for c in cs]
        if not pts:
            return np.array([])
        T_, _, _, _ = M.time_many(pts)
        return T_ * 600.0

    def score_time(cs, rep_masks=False):
        if not cs:
            return []
        if rep_masks:
            reps = {}
            for c in cs:
                k = (c["arm"], c["G"], c["C"])
                if k not in reps:
                    reps[k] = dict(c, mask=G.mask_of(range(c["G"]), range(c["C"])))
            keys = sorted(reps)
            rl = [reps[k] for k in keys]
            f31 = dict(zip(keys, v31_wall(rl)))
            f3 = dict(zip(keys, v3_wall(rl)))
            for c in cs:
                k = (c["arm"], c["G"], c["C"])
                c["F31_wall"], c["F3_wall"] = float(f31[k]), float(f3[k])
                c["score"] = abs(math.log(c["F31_wall"] / c["F3_wall"]))
            return cs
        a, b = v31_wall(cs), v3_wall(cs)
        for c, x, y in zip(cs, a, b):
            c["F31_wall"], c["F3_wall"] = float(x), float(y)
            c["score"] = abs(math.log(x / y))
        return cs

    def score_S(cs):
        out_ = []
        for c in cs:
            r31 = M.predict(C1, c["arm"], c["fmt"], c["kind"], c["mask"], 600.0, c["kernel"])
            t3 = float(v3_wall([c])[0]) / 600.0
            q = {"card": C1, "fmt": c["fmt"], "kind": c["kind"], "arm": c["arm"], "kernel": c["kernel"], "minions": 1024, "mask": FULL,
                 "f": 600.0, "T": t3, "w": 0.0, "idle_w": None, "G": 0.0, "die_start": None, "s": (EV.C.volts(C1, 600.0) / 0.517) ** 2}
            X = EV.Features31([q])
            if "W_over_idle" not in r31 or not X.usable3[0]:
                continue
            tq = MV3m.time(c["arm"], c["kernel"], c["fmt"], c["mask"], 600.0)
            n2, n3, nF = (float(v) for v in EV.C.lines(0.5 * (tq[1] + tq[2])))
            rC = EV.rC_of(X.Ffull, v3p["time"]["theta"], v3p["time"]["form"])
            W3 = float(EN3.W_v3(v3p["energy"]["theta"], X, np.array([0]), np.array([n2]), np.array([n3]), np.array([nF]), np.array([t3]), rC, "v3")[0])
            c["F31_W"], c["F3_W"] = float(r31["W_over_idle"]), W3
            c["score"] = abs(math.log(c["F31_W"] / W3))
            out_.append(c)
        return out_

    def ranked(cs):
        """descending score, ties by the sorted token; scores within TIE_REL (relative) of a tie class's first score are one class"""
        by = sorted(cs, key=lambda c: (-c["score"], G.sort_key(c)))
        cls, out_ = -1, []
        first = None
        for c in by:
            if first is None or abs(c["score"] - first) > TIE_REL * abs(first):
                cls += 1
                first = c["score"]
            out_.append((cls, c))
        return [c for _, c in sorted(out_, key=lambda x: (x[0], G.sort_key(x[1])))]

    def pick(fam, cs, q):
        cs = sorted(cs, key=G.sort_key)
        if len(cs) <= q:
            return [dict(c, how="all (fewer candidates than the quota)") for c in cs]
        h = math.ceil(q / 2)
        by = ranked(cs)
        top = [dict(c, how=f"by score ({i + 1} of {h})") for i, c in enumerate(by[:h])]
        topk = {G.token_str(c) for c in by[:h]}
        rest = [c for c in cs if G.token_str(c) not in topk]
        rnd = random.Random(f"v3.1-blind|B|{fam}").sample(rest, q - h)
        return top + [dict(c, how=f"random draw {i + 1} of {q - h}") for i, c in enumerate(rnd)]

    res = {"experiment": "E215", "request": "Q224", "arm": "B", "card": C1, "f_mhz": 600.0, "quota_B": QUOTA_B, "tie_rel": TIE_REL,
           "rule": "DECLARED-v31.md item 10 (7375bc9c), applied to aifoundry1 card 1; L and S by the post hoc readings (E215.md D1)",
           "scan_sha256": sha(scan_path), "params_v31_sha256": sha(p31_path), "params_v3_sha256": sha(p3_path),
           "e215_v31_sha256": sha(os.path.join(V31, "e215_v31.py")), "neverrun_e215_sha256": sha(os.path.join(HERE, "neverrun_e215.py")),
           "L_full_chip_shapes_on_card1": sorted([list(b), k] for b, k in full_runs), "families": {}}
    chosen = {}
    for fam in ("L", "P", "C", "R", "S"):
        q = QUOTA_B[fam]
        rec = {"grid_n": len(grids[fam]), "literal_candidates_n": len(lit[fam])}
        cl = score_S([dict(c) for c in lit[fam]]) if fam == "S" else score_time([dict(c) for c in lit[fam]], rep_masks=(fam == "L"))
        rec["literal_chosen"] = [dict(c, reading="literal") for c in pick(fam, cl, q)] if cl else []
        if fam in dep:
            rec["posthoc_candidates_n"] = len(dep[fam])
            cd = score_S([dict(c) for c in dep[fam]]) if fam == "S" else score_time([dict(c) for c in dep[fam]], rep_masks=(fam == "L"))
            rec["posthoc_priced_n"] = len(cd)
            rec["posthoc_chosen"] = [dict(c, reading="posthoc") for c in pick(fam, cd, q)] if cd else []
            if fam == "S":
                rec["posthoc_candidates"] = [{"token": G.token_str(c), "score": c.get("score"), "F31_W": c.get("F31_W"), "F3_W": c.get("F3_W")}
                                             for c in sorted(cd, key=G.sort_key)]
        res["families"][fam] = rec
        chosen[fam] = rec["literal_chosen"] + rec.get("posthoc_chosen", [])
    chk = []
    for c in res["families"]["L"].get("posthoc_chosen") or []:
        a = float(v31_wall([c])[0])
        b = float(v3_wall([c])[0])
        ok = abs(a / c["F31_wall"] - 1) < 1e-12 and abs(b / c["F3_wall"] - 1) < 1e-12
        chk.append({"token": G.token_str(c), "representative_v31": c["F31_wall"], "at_its_mask_v31": a, "representative_v3": c["F3_wall"],
                    "at_its_mask_v3": b, "equal": ok})
        if not ok:
            raise SystemExit(f"choose_e215b: REFUSED, the representative mask does not price {G.token_str(c)} as its own mask does")
    res["L_representative_mask_check"] = chk
    res["chosen"] = [{"family": f, "reading": c["reading"], "how": c["how"], "token": G.token_str(c), "loop": c["loop"], "kernel": c["kernel"],
                      "arm": c["arm"], "fmt": c["fmt"], "kind": c["kind"], "mask": c["mask"], "score": c.get("score"),
                      "F31": c.get("F31_wall", c.get("F31_W")), "F3": c.get("F3_wall", c.get("F3_W"))}
                     for f in ("L", "P", "C", "R", "S") for c in chosen[f]]
    return json.loads(json.dumps(res, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--tie-rel", type=float, default=None, help="REPORTED alternative only (D2): a relative tie tolerance; writes --out")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = build(a.scan, a.tie_rel)
    dest = a.out or OUT
    if a.tie_rel is not None and dest == OUT:
        raise SystemExit("choose_e215b: a --tie-rel alternative is REPORTED only: give --out (never desk/choice-e215b.json)")
    if a.check:
        same = json.load(open(dest)) == out
        print(f"choose_e215b --check: desk/choice-e215b.json rebuilt == committed: {same}")
        print("PASS" if same else "FAIL")
        sys.exit(0 if same else 1)
    json.dump(out, open(dest, "w"), indent=1, sort_keys=True)
    for fam, r in out["families"].items():
        print(fam, "grid", r["grid_n"], "literal", r["literal_candidates_n"], "chosen", len(r["literal_chosen"]),
              "posthoc", r.get("posthoc_candidates_n"), len(r.get("posthoc_chosen") or []))
    for c in out["chosen"]:
        print(f"{c['family']} {c['reading']:7s} {c['how']:24s} {c['token']:60s} score {c['score']:.6f}" if c["score"] is not None else c)
    print(sha(dest), os.path.relpath(dest, HERE))


if __name__ == "__main__":
    main()
