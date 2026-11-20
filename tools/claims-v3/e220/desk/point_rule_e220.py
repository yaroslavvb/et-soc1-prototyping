#!/usr/bin/env python3
"""E220 (Q233): THE POINT RULE (POINT-RULE-e220.md), applied mechanically to both arms. Written and hashed (desk/point-rule-e220.sha256, with
the clock's time) together with POINT-RULE-e220.md and desk/models_e220.py BEFORE any forecast was computed; the scan it reads
(desk/scan-e220-reg.json, desk/neverrun_e220.py) holds no forecast.

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/point_rule_e220.py --scan tools/claims-v3/e220/desk/scan-e220-reg.json --out tools/claims-v3/e220

Writes desk/candidates-e220.json (every candidate with its features, scores, verdicts and reasons), points-e220.json and points-e220.csv (both
arms' points, their order and the card-time plan's run list). numpy through the predictors; single-threaded (the caller sets the thread variables).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E220 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import models_e220 as MZ  # noqa: E402
import neverrun_e220 as NRZ  # noqa: E402

E218_POINTS = ("tools/claims-v3/e218/points-e218.csv", "9971b83179b7e2c56a71a8c51429b017902f4139b2d795096b7ca51e01507de4")
E215_POINTS_PY = ("tools/claims-v3/e215/points_e215.py", "a8733593aaf91a3a38284ae4ce177983a8a4f57cc2f0363ceeb38b34a3f88f29")
FULLM = "0xffffffff"
FULL = 0xFFFFFFFF
DROP_MARGIN_W = 3.0
D_MISS = 39.0                         # the retention miss gemmL2x1x7's footprint, MB (2 MB KB + NB KB + 2 MB NB at 2x1x7)
L3_1 = {"NB": 1, "d_lo": 30.0, "d_hi": 45.0, "quota": 5, "min_side": 2}
L3_2 = {"half_width": 15.0, "quota": 3, "min_side": 1, "min_MB": 2, "min_NB": 2, "min_KB": 2}
L3_GRID = {"MB": range(1, 17), "NB": range(1, 17), "KB": range(1, 49)}
Y2_SOURCES = (("p01", "gemmL1x8x8", "0x3", "0x10001", "E216 y01 (0x3 vs 0x10001)"),
              ("p02", "gemmL1x8x12", "0x3", "0x10001", "E216 y02 (0x3 vs 0x10001)"),
              ("p03", "gemmL1x4x16", "0x3", "0x10001", "E216 y03 (0x3 vs 0x10001)"),
              ("p04", "gemmL1x4x24", "0x101", "0x10001", "E216 y07, control (0x101 vs 0x10001)"),
              ("p05", "gemmL1x8x24", "0x101", "0x10001", "E216 y08, control (0x101 vs 0x10001)"))
Y2_GRID = {"MB": range(1, 5), "NB": range(2, 17), "KB": range(2, 33)}
G2_MB = tuple(range(1, 9))
G2_NB = (1, 2, 3, 5, 6)
G2_KB = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48)
G2_QUOTA = {"L2": 3, "NB56": 4}
G2_MIN = 6
PACE_S = {"A": ("E215 arm B (docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1): 71 runs, 5 smoke processes and the stop-path test "
                "in 28.55 card-minutes", 28.55 * 60.0 / 71.0),
          "B": ("E216 (docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2): 69 runs with the opening rest, the smoke and the stop-path test "
                "in 27.55 card-minutes", 27.55 * 60.0 / 69.0)}
RULE_MIN, CAP_MIN = 60.0, 70.0


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(rel, want):
    p = os.path.join(REPO, rel)
    if sha(p) != want:
        print(f"point_rule_e220: REFUSED, {rel} is {sha(p)}, pinned {want}")
        sys.exit(4)
    return p


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tok(pre, MB, NB, KB):
    return f"{pre}{MB}x{NB}x{KB}"


def footprint(MB, NB, KB):
    """MM1-v3's mm1_core_v3.footprint at the full chip: MB of distinct tiles a pass touches (A 2 MB, B 1 MB, C 2 MB a block)"""
    return 2.0 * MB * KB + NB * KB + 2.0 * MB * NB


def key(token, fmt, mask):
    return f"{token}|{fmt}|{mask}"


class Rule:
    def __init__(self, scan_path, out):
        self.S = json.load(open(scan_path))
        self.scan_sha = sha(scan_path)
        self.NV = NRZ.Never(self.S)
        self.M = MZ.Models()
        self.P = load("points_e215_pinned", pinned(*E215_POINTS_PY))
        th = self.M.P32["time"]["theta"]
        self.x1, self.w1, self.x2, self.w2, self.pB = th["x1"], th["w1"], th["x2"], th["w2"], th["pB"]
        self.out = out
        self.cands = {"A": {}, "B": {}}
        self.fc_cache = {"A": {}, "B": {}}

    # ---------------------------------------------------------------- forecasts at the arm's registered clock, cached
    def fc(self, arm, items, models=MZ.MODELS):
        """each model's frozen forecast at the arm's registered clock (the grid of family G2 asks MM1-v3.2 alone; every planning peak asks all four)"""
        f = MZ.ARMS[arm]["f_reg"]
        mk = "|".join(models)
        need = [it for it in items if (key(it["arm"], it["fmt"], it["mask"]), mk) not in self.fc_cache[arm]]
        if need:
            pts = [{"id": key(it["arm"], it["fmt"], it["mask"]), "arm": it["arm"], "fmt": it["fmt"], "kind": "random", "mask": it["mask"]} for it in need]
            got = self.M.forecast(arm, pts, f, models=models)
            for k, v in got.items():
                self.fc_cache[arm][(k, mk)] = v
        return [self.fc_cache[arm][(key(it["arm"], it["fmt"], it["mask"]), mk)] for it in items]

    def line(self, arm):
        return MZ.ARMS[arm]["stop_W"] - DROP_MARGIN_W

    def pp(self, arm, token, fmt, mask):
        fcs = self.fc(arm, [{"arm": token, "fmt": fmt, "mask": mask}])[0]
        pp32, ppall, by = self.M.planning_peak(arm, fcs, token)
        return pp32, ppall, by, fcs

    def never(self, arm, token, mask, reading):
        card = MZ.ARMS[arm]["card"]
        ok, ev = self.NV.verdict(reading, token, mask, card)
        return bool(ok), ev

    # ---------------------------------------------------------------- family X: E218's 52 points as cross-card twins
    def family_x(self, arm):
        rows = [r for r in csv.DictReader(open(pinned(*E218_POINTS))) if r["family"] in ("G", "Gt", "Y", "F")]
        assert len(rows) == 52, len(rows)
        out, rec = [], []
        for r in rows:
            fam = r["family"]
            reading = "config" if fam == "Y" else "token"
            ok, ev = self.never(arm, r["arm"], r["shire_mask"], reading)
            pp32, ppall, by, _ = self.pp(arm, r["arm"], r["format"], r["shire_mask"])
            drop = None
            if not ok:
                drop = f"ran on {MZ.ARMS[arm]['card']} ({reading} reading)"
            elif pp32 is None:
                drop = "MM1-v3.2 does not price its energy"
            elif pp32 >= self.line(arm):
                drop = f"planning peak by MM1-v3.2 {pp32:.2f} W within {DROP_MARGIN_W:.0f} W of the {MZ.ARMS[arm]['stop_W']:.0f} W stop"
            rec.append({"e218_id": r["id"], "family": fam, "token": r["arm"], "fmt": r["format"], "mask": r["shire_mask"], "reading": reading,
                        "never_run": ok, "evidence": (None if ok else ev), "PP32_W": pp32, "PP_all_W": ppall, "PP_all_by": by, "dropped": drop})
            if drop is None:
                sub = {"G": "XG", "Gt": "XGt", "Y": "XY", "F": "XF"}[fam]
                out.append({"id": "x" + r["id"], "family": "X", "subfamily": sub, "source": f"E218 {r['id']} ({fam}, regime {r['regime'] or '-'})",
                            "token": r["arm"], "fmt": r["format"], "kind": "random", "mask": r["shire_mask"], "neverrun_reading": reading,
                            "pair": (("x" + r["pair"]) if r["pair"] else ""), "pair_role": ("a" if r["id"].endswith("a") else ("b" if r["id"].endswith("b") else "")) if fam == "Y" else "",
                            "twin": ("x" + r["twin"]) if r["twin"] else "", "twin_of": ("x" + r["twin_of"]) if r["twin_of"] else "",
                            "e218_id": r["id"], "PP32_W": pp32, "PP_all_W": ppall})
        self.cands[arm]["X"] = rec
        return out

    # ---------------------------------------------------------------- family L3: the L3 edges (MM1-v3.2's retention edges x1, x2)
    def family_l3(self, arm, used):
        recs, picked = [], []
        grid = []
        for MB in L3_GRID["MB"]:
            for NB in L3_GRID["NB"]:
                for KB in L3_GRID["KB"]:
                    d = footprint(MB, NB, KB)
                    sub = None
                    if NB == L3_1["NB"] and L3_1["d_lo"] <= d <= L3_1["d_hi"]:
                        sub = "L3-1"
                    elif abs(d - self.x2) <= L3_2["half_width"] and MB >= L3_2["min_MB"] and NB >= L3_2["min_NB"] and KB >= L3_2["min_KB"]:
                        sub = "L3-2"
                    if sub:
                        grid.append((sub, MB, NB, KB, d))
        for sub_name, quota, center, edge, min_side in (("L3-1", L3_1["quota"], D_MISS, self.x1, L3_1["min_side"]),
                                                        ("L3-2", L3_2["quota"], self.x2, self.x2, L3_2["min_side"])):
            cs = []
            for (sub, MB, NB, KB, d) in grid:
                if sub != sub_name:
                    continue
                t = tok("gemmL", MB, NB, KB)
                ok, ev = self.never(arm, t, FULLM, "token")
                cs.append({"sub": sub, "token": t, "shape": [MB, NB, KB], "d_MB": d, "score": abs(d - center), "side": ("below" if d < edge else "above"),
                           "never_run": ok, "evidence_files": (None if ok else ev.get("files")), "string": key(t, "fp32", FULLM)})
            cs.sort(key=lambda c: (c["score"], c["string"]))
            chosen = []
            nbs = set()

            def fits(c, chosen):
                if not c["never_run"]:
                    return False, "ran on the card (token reading)"
                if tuple(c["shape"]) in used:
                    return False, "shape already in E220 on this arm"
                if any(abs(c["d_MB"] - x["d_MB"]) < 1e-9 for x in chosen):
                    return False, "footprint already drawn in this subfamily"
                if sub_name == "L3-2" and c["shape"][1] in nbs:
                    return False, "NB already drawn in L3-2"
                pp32, ppall, by, _ = self.pp(arm, c["token"], "fp32", FULLM)
                c["PP32_W"], c["PP_all_W"] = pp32, ppall
                if pp32 is None:
                    return False, "MM1-v3.2 does not price its energy"
                if pp32 >= self.line(arm):
                    return False, f"planning peak {pp32:.2f} W within 3 W of the stop"
                # the side balance: leave room for min_side on each side
                below = sum(1 for x in chosen if x["side"] == "below")
                above = len(chosen) - below
                if c["side"] == "below" and above < min_side and (quota - len(chosen)) <= (min_side - above):
                    return False, "the side balance (room kept for the other side)"
                if c["side"] == "above" and below < min_side and (quota - len(chosen)) <= (min_side - below):
                    return False, "the side balance (room kept for the other side)"
                return True, "drawn"
            for c in cs:
                if len(chosen) >= quota:
                    c["verdict"] = "not reached (quota full)"
                    continue
                ok, why = fits(c, chosen)
                c["verdict"] = why
                if ok:
                    chosen.append(c)
                    nbs.add(c["shape"][1])
            recs += cs
            for c in chosen:
                used.add(tuple(c["shape"]))
                picked.append(c)
        self.cands[arm]["L3"] = [c for c in recs if c.get("verdict") != "not reached (quota full)" or c in picked][:400]
        self.cands[arm]["L3_counts"] = {s: sum(1 for c in recs if c["sub"] == s) for s in ("L3-1", "L3-2")}
        out = []
        for n, c in enumerate(sorted(picked, key=lambda c: (c["sub"], c["score"], c["string"])), 1):
            out.append({"id": f"l{n:02d}", "family": "L3", "subfamily": c["sub"], "source": (f"the first L3 edge x1 = {self.x1:.2f} MB (MM1-v3.2), "
                        f"ranked by |d - {D_MISS:.0f} MB| (gemmL2x1x7's footprint)" if c["sub"] == "L3-1" else
                        f"the second L3 edge x2 = {self.x2:.2f} MB (MM1-v3.2), ranked by |d - x2|"),
                        "token": c["token"], "fmt": "fp32", "kind": "random", "mask": FULLM, "neverrun_reading": "token", "footprint_MB": c["d_MB"],
                        "edge_side": c["side"], "pair": "", "pair_role": "", "twin": "", "twin_of": "", "e218_id": "",
                        "PP32_W": c["PP32_W"], "PP_all_W": c["PP_all_W"]})
        return out

    # ---------------------------------------------------------------- family Y2: E216's layout pairs' masks at never-run shapes
    def family_y2(self, arm, used):
        out, recs = [], []
        for pid, src, ma, mb, what in Y2_SOURCES:
            m0 = self.P.parse_arm(src)[1]
            cands = []
            for MB in Y2_GRID["MB"]:
                for NB in Y2_GRID["NB"]:
                    for KB in Y2_GRID["KB"]:
                        t = tok("gemmL", MB, NB, KB)
                        dist = abs(math.log2(MB / m0[0])) + abs(math.log2(NB / m0[1])) + abs(math.log2(KB / m0[2]))
                        cands.append((dist, key(t, "fp32", ma), t, (MB, NB, KB)))
            cands.sort()
            pick = None
            tried = []
            for dist, s, t, shp in cands:
                if shp in used:
                    tried.append({"token": t, "dist": dist, "verdict": "shape already in E220 on this arm"})
                    continue
                ok, ev = self.never(arm, t, ma, "token")
                if not ok:
                    tried.append({"token": t, "dist": dist, "verdict": "ran on the card (token reading)"})
                    continue
                pa = self.pp(arm, t, "fp32", ma)
                pb = self.pp(arm, t, "fp32", mb)
                if pa[0] is None or pb[0] is None:
                    tried.append({"token": t, "dist": dist, "verdict": "MM1-v3.2 does not price its energy"})
                    continue
                if max(pa[0], pb[0]) >= self.line(arm):
                    tried.append({"token": t, "dist": dist, "verdict": "planning peak within 3 W of the stop"})
                    continue
                pick = (t, shp, dist, pa, pb)
                tried.append({"token": t, "dist": dist, "verdict": "drawn"})
                break
            recs.append({"pair": pid, "source": src, "masks": [ma, mb], "what": what, "tried": tried[:60], "n_tried": len(tried)})
            if pick is None:
                continue
            t, shp, dist, pa, pb = pick
            used.add(shp)
            for role, m, p in (("a", ma, pa), ("b", mb, pb)):
                out.append({"id": f"{pid}{role}", "family": "Y2", "subfamily": "Y2-pair" if ma == "0x3" else "Y2-control",
                            "source": f"{what}: source shape {src}, distance {dist:.3f} (log2 units)", "token": t, "fmt": "fp32", "kind": "random",
                            "mask": m, "neverrun_reading": "token", "pair": pid, "pair_role": role, "twin": "", "twin_of": "", "e218_id": "",
                            "PP32_W": p[0], "PP_all_W": p[1]})
        self.cands[arm]["Y2"] = recs
        return out

    # ---------------------------------------------------------------- family G2: gemmLnc at small predicted excess, with cooperative twins
    def family_g2(self, arm, used):
        items = []
        for fmt in ("fp32", "int8"):
            for MB in G2_MB:
                for NB in G2_NB:
                    for KB in G2_KB:
                        items.append({"arm": tok("gemmLnc", MB, NB, KB), "fmt": fmt, "mask": FULLM, "shape": (MB, NB, KB)})
        fcs = self.fc(arm, items, models=("MM1-v3.2",))
        cands = []
        for it, fc in zip(items, fcs):
            x = fc["MM1-v3.2"]
            beyond = MZ.beyond_of(x["Q_mean"])
            NB = it["shape"][1]
            if beyond < 2.6:
                reg = "L2"
            elif NB in (5, 6):
                reg = "NB56"
            else:
                reg = None
            if reg is None or (it["fmt"] == "int8" and reg != "L2"):
                continue
            if "W_over_idle" not in x or "F3_W_at_own_t" not in x:
                continue
            share = x["F3_W_at_own_t"] / x["W_over_idle"]
            cands.append({"token": it["arm"], "fmt": it["fmt"], "shape": list(it["shape"]), "regime": reg, "beyond": beyond, "first": x.get("F3_first"),
                          "F3_W": x["F3_W_at_own_t"], "W_v32": x["W_over_idle"], "score_share": share, "string": key(it["arm"], it["fmt"], FULLM)})
        by = {r: sorted([c for c in cands if c["regime"] == r], key=lambda c: (c["score_share"], c["string"])) for r in ("L2", "NB56")}
        quota = dict(G2_QUOTA)
        drawn = []
        nbkb = set()

        def qualifies(c):
            shp = tuple(c["shape"])
            if shp in used:
                return False, "shape already in E220 on this arm"
            if (shp[1], shp[2]) in nbkb:
                return False, "(NB, KB) already drawn in G2"
            twin = tok("gemmL", *shp)
            n1, ev1 = self.never(arm, c["token"], FULLM, "token")
            n2, ev2 = self.never(arm, twin, FULLM, "token")
            if not n1:
                return False, "the gemmLnc token ran on the card (token reading)"
            if not n2:
                return False, "its cooperative twin's token ran on the card (token reading)"
            pg = self.pp(arm, c["token"], c["fmt"], FULLM)
            pt = self.pp(arm, twin, c["fmt"], FULLM)
            c["PP32_W"], c["PP_all_W"], c["twin_PP32_W"], c["twin_PP_all_W"] = pg[0], pg[1], pt[0], pt[1]
            if pg[0] is None or pt[0] is None:
                return False, "MM1-v3.2 does not price its energy"
            if pg[0] >= self.line(arm) or pt[0] >= self.line(arm):
                return False, "planning peak (the point's or its twin's) within 3 W of the stop"
            return True, "drawn"
        for reg in ("L2", "NB56"):
            n_have = 0
            for c in by[reg]:
                if n_have >= quota[reg]:
                    break
                ok, why = qualifies(c)
                c["verdict"] = why
                if ok:
                    drawn.append(c)
                    used.add(tuple(c["shape"]))
                    nbkb.add((c["shape"][1], c["shape"][2]))
                    n_have += 1
            if reg == "L2" and n_have < quota["L2"]:
                quota["NB56"] += quota["L2"] - n_have          # the L2 regime's unfilled quota passes to NB56
        self.cands[arm]["G2"] = {"counts": {r: len(v) for r, v in by.items()}, "quota_after_pass_on": quota,
                                 "walked": {r: [c for c in v if "verdict" in c] for r, v in by.items()}, "short": len(drawn) < G2_MIN}
        out = []
        for n, c in enumerate(drawn, 1):
            shp = tuple(c["shape"])
            out.append({"id": f"n{n:02d}", "family": "G2", "subfamily": f"G2-{c['regime']}", "source": (f"rgm136 gemmLnc, regime {c['regime']} (beyond "
                        f"{c['beyond']:.3f}), MM1-v3.2's F3 share of W over idle {c['score_share']:.4f} (ascending: small predicted excess)"),
                        "token": c["token"], "fmt": c["fmt"], "kind": "random", "mask": FULLM, "neverrun_reading": "token", "pair": "", "pair_role": "",
                        "twin": f"n{n:02d}t", "twin_of": "", "e218_id": "", "PP32_W": c["PP32_W"], "PP_all_W": c["PP_all_W"]})
            out.append({"id": f"n{n:02d}t", "family": "G2t", "subfamily": f"G2t-{c['regime']}", "source": f"the cooperative twin of n{n:02d}",
                        "token": tok("gemmL", *shp), "fmt": c["fmt"], "kind": "random", "mask": FULLM, "neverrun_reading": "token", "pair": "", "pair_role": "",
                        "twin": "", "twin_of": f"n{n:02d}", "e218_id": "", "PP32_W": c["twin_PP32_W"], "PP_all_W": c["twin_PP_all_W"]})
        return out

    # ---------------------------------------------------------------- the order and the card-time plan
    def order(self, arm, pts):
        gnc = [p for p in pts if p["token"].startswith("gemmLnc")]
        rest = [p for p in pts if not p["token"].startswith("gemmLnc")]
        p1 = sorted(p["id"] for p in rest)
        random.Random(f"E220|{arm}|pass1").shuffle(p1)
        p2 = [i for i in reversed(p1) if any(q["id"] == i and q["family"] in ("L3", "Y2") for q in rest)]
        gb = [p["id"] for p in sorted(gnc, key=lambda p: (p["PP32_W"], p["id"]))]
        g2 = [i for i in reversed(gb) if i.startswith("n")]
        runs = [("smoke", "s01")] + [("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in p2] + \
            [("tie", "t01")] + [("smoke", "s03")] + [("G block", i) for i in gb] + [("G block reversed (G2 only)", i) for i in g2]
        n_runs = sum(1 for b, _ in runs if b != "smoke")
        what, pace = PACE_S[arm]
        card_min = n_runs * pace / 60.0
        subset = sum(1 for b, _ in runs if b in ("tie",)) - 1 + len(p1)
        return {"pass1": p1, "pass2": p2, "G_block": gb, "G_block_reversed": g2, "runs": [{"n": k + 1, "block": b, "id": i} for k, (b, i) in enumerate(runs)],
                "n_runs_scored_and_ties": n_runs, "n_smoke": sum(1 for b, _ in runs if b == "smoke"), "pace_s_per_run": pace, "pace_source": what,
                "card_minutes_planned": card_min, "rule_min": RULE_MIN, "cap_min": CAP_MIN,
                "registered_subset_if_cut": {"what": "the opening smoke, tie 1, pass 1 and tie 2 (every non-gemmLnc point once; the G block not reached)",
                                             "runs": subset, "card_minutes": subset * pace / 60.0}}

    def describe(self, arm, p):
        loop = "rgm136 gemmLnc" if p["token"].startswith("gemmLnc") else "rgm136 gemmL"
        d = self.P.describe(p["id"], arm, p["family"], "registered", p["token"], p["fmt"], p["kind"], p["mask"], loop, "point", p["source"],
                            MZ.ARMS[arm]["card"])
        d["f_mhz"] = MZ.ARMS[arm]["f_reg"]
        for k in ("subfamily", "source", "neverrun_reading", "pair", "pair_role", "twin", "twin_of", "e218_id", "PP32_W", "PP_all_W",
                  "footprint_MB", "edge_side"):
            if k in p:
                d[k] = p[k]
        d["token"] = p["token"]
        d["footprint_MB_full_chip"] = footprint(*d["shape"])
        d["arm_card"] = MZ.ARMS[arm]["card"]
        return d

    def run(self):
        t0 = now()
        res = {"what": "E220's point rule applied (POINT-RULE-e220.md; desk/point_rule_e220.py)", "started": t0, "scan_sha256": self.scan_sha,
               "x1_MB": self.x1, "w1_MB": self.w1, "x2_MB": self.x2, "w2_MB": self.w2, "pB": self.pB, "eps_G": self.M.eps_g,
               "rest_law": self.M.rest, "arms": {}}
        allpts = {}
        for arm in ("A", "B"):
            xs = self.family_x(arm)
            used = {tuple(self.P.parse_arm(p["token"])[1]) for p in xs}
            l3 = self.family_l3(arm, used)
            y2 = self.family_y2(arm, used)
            g2 = self.family_g2(arm, used)
            pts = xs + l3 + y2 + g2
            plan = self.order(arm, pts)
            desc = [self.describe(arm, p) for p in pts]
            allpts[arm] = desc
            res["arms"][arm] = {"card": MZ.ARMS[arm]["card"], "f_reg_mhz": MZ.ARMS[arm]["f_reg"], "stop_W": MZ.ARMS[arm]["stop_W"],
                                "drop_line_W": self.line(arm), "counts": {f: sum(1 for p in pts if p["family"] == f) for f in ("X", "L3", "Y2", "G2", "G2t")},
                                "x_dropped": [c for c in self.cands[arm]["X"] if c["dropped"]], "plan": plan,
                                "highest_PP32": max((p["PP32_W"] for p in pts), default=None),
                                "highest_PP_all": max((p["PP_all_W"] for p in pts if p["PP_all_W"] is not None), default=None),
                                "g2_short": self.cands[arm]["G2"]["short"]}
        res["ended"] = now()
        os.makedirs(os.path.join(self.out, "desk"), exist_ok=True)
        cpath = os.path.join(self.out, "desk", "candidates-e220.json")
        json.dump({"what": "every candidate of E220's point rule, both arms", "scan_sha256": self.scan_sha, "candidates": self.cands,
                   "started": t0, "ended": res["ended"]}, open(cpath, "w"), indent=1, sort_keys=True, default=str)
        res["candidates_sha256"] = sha(cpath)
        res["points"] = allpts
        ppath = os.path.join(self.out, "points-e220.json")
        json.dump(res, open(ppath, "w"), indent=1, sort_keys=True, default=str)
        cols = ["arm", "id", "family", "subfamily", "pair", "pair_role", "twin", "twin_of", "e218_id", "loop", "kernel", "host", "elf", "token", "format",
                "kind", "shire_mask", "shires", "minions", "M", "N", "K", "M_computed", "N_computed", "ops_per_minion_per_gemm", "macs_per_gemm", "case",
                "footprint_MB_full_chip", "neverrun_reading", "f_mhz", "PP32_W", "PP_all_W", "values"]
        with open(os.path.join(self.out, "points-e220.csv"), "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(cols)
            for arm in ("A", "B"):
                for d in allpts[arm]:
                    w.writerow([arm if c == "arm" else ("" if d.get(c) is None else d.get(c)) for c in cols])
        print(f"point rule: {t0} - {res['ended']}")
        for arm in ("A", "B"):
            a = res["arms"][arm]
            print(f"arm {arm} ({a['card']}): {a['counts']}; X dropped {len(a['x_dropped'])}; highest PP32 {a['highest_PP32']:.2f} W (line {a['drop_line_W']:.0f} W); "
                  f"runs {a['plan']['n_runs_scored_and_ties']} + {a['plan']['n_smoke']} smoke, planned {a['plan']['card_minutes_planned']:.1f} card-minutes; "
                  f"G2 short {a['g2_short']}")
        print(f"points-e220.json {sha(ppath)}; points-e220.csv {sha(os.path.join(self.out, 'points-e220.csv'))}; candidates {res['candidates_sha256']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    Rule(a.scan, a.out).run()


if __name__ == "__main__":
    main()
