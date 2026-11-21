#!/usr/bin/env python3
"""E222 (Q236): THE POINT RULE (POINT-RULE-e222.md), applied mechanically to E222's one arm (aifoundry3 card 0 at its pinned 600 MHz). Written
and hashed (desk/point-rule-e222.sha256, with the clock's time) together with POINT-RULE-e222.md, desk/models_e222.py and desk/neverrun_e222.py
BEFORE any forecast was computed; the scan it reads (desk/scan-e222-reg.json) holds no forecast.

    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/point_rule_e222.py --scan tools/claims-v3/e222/desk/scan-e222-reg.json \
        --e220-points <OUT/reg-e220/POINTS-e220.csv> --out tools/claims-v3/e222

Writes desk/candidates-e222.json (every candidate with its features, scores, verdicts and reasons), points-e222.json and points-e222.csv (the
points, their order and the card-time plan's run list), desk/l3s-extra-e222.json (the L3S set-model records it made) and
desk/posimb-features-e222.json (the posimb features it made). numpy through the predictors; single-threaded (the caller sets the thread variables).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import importlib.util
import itertools
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E222 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import models_e222 as MZ  # noqa: E402
import neverrun_e222 as NRZ  # noqa: E402

E218_POINTS = ("tools/claims-v3/e218/points-e218.csv", "9971b83179b7e2c56a71a8c51429b017902f4139b2d795096b7ca51e01507de4")
E215_POINTS_PY = ("tools/claims-v3/e215/points_e215.py", "a8733593aaf91a3a38284ae4ce177983a8a4f57cc2f0363ceeb38b34a3f88f29")
E220_POINTS_CSV_SHA = "64a7c99a90a2d899db44dc0c3790dfd840cd02b49c9d12f24396f4691125afc4"   # OUT/reg-e220/POINTS-e220.csv (POINTS.txt 058984a0...)
FULLM = "0xffffffff"
DROP_MARGIN_W = 3.0
R_IDS = ("y01a", "y01b", "g01", "g01t")                    # family R: E218's first Y pair and its first G point with its twin (by id)
T_FAMILIES = ("L3", "Y2", "G2", "G2t")
L3B = {"L3b-1": {"quota": 5, "min_side": 2, "NB": (1,), "d": (30.0, 48.0), "rank": "delta"},
       "L3b-3": {"quota": 3, "NB": tuple(range(2, 17)), "d": (32.0, 48.0), "rank": "delta"},
       "L3b-2": {"quota": 2, "min_side": 1, "half_width": 15.0, "min_MB": 2, "min_NB": 2, "min_KB": 2, "rank": "edge"}}
L3B_ORDER = ("L3b-1", "L3b-3", "L3b-2")
L3_GRID = {"MB": range(1, 17), "NB": range(1, 17), "KB": range(1, 49)}
L3B_2_GRID = {"MB": range(2, 9), "NB": range(2, 9), "KB": range(2, 17)}
Y3_SOURCES = (("q01", "gemmL1x8x8", "E216 y01"), ("q02", "gemmL1x8x12", "E216 y02"), ("q03", "gemmL1x4x16", "E216 y03"),
              ("q04", "gemmL1x4x24", "E216 y07"), ("q05", "gemmL1x8x24", "E216 y08"))
Y3_GRID = {"MB": range(1, 5), "NB": range(2, 17), "KB": range(2, 33)}
Y3_SHIRES = 2
G3_MB = tuple(range(1, 9))
G3_NB = (1, 2, 3, 5, 6)
G3_KB = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48)
G3_QUOTA = {"L2": 3, "NB56": 4}
G3_MIN = 6
PACE = ("E218 (docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3, data b445b0f5): its session, the smoke s01, the stop-path test, "
        "107 runs and the G block's smoke s03 in 45.2 card-minutes", 45.2 * 60.0 / 107.0)
TARGET_MIN, RULE_MIN, CAP_MIN = 55.0, 70.0, 80.0
EXTRA = (("t01", "gemmL2x4x4", "fp32"), ("s01", "gemmL2x2x2", "fp32"), ("s03", "gemmLnc2x2x2", "fp32"))


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(rel, want):
    p = os.path.join(REPO, rel)
    if sha(p) != want:
        print(f"point_rule_e222: REFUSED, {rel} is {sha(p)}, pinned {want}")
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
    """MM1-v3's mm1_core_v3.footprint at the full chip (E220's): MB of distinct tiles a pass touches (A 2 MB, B 1 MB, C 2 MB a block)"""
    return 2.0 * MB * KB + NB * KB + 2.0 * MB * NB


def key(token, fmt, mask):
    return f"{token}|{fmt}|{mask}"


def product_masks(n):
    """every shire mask of n shires that is a product of row groups (s >> 2, 8 of them) and column groups (s & 3, 4 of them)"""
    out = []
    for nr in range(1, 9):
        if n % nr or n // nr > 4:
            continue
        for R in itertools.combinations(range(8), nr):
            for C in itertools.combinations(range(4), n // nr):
                out.append(("0x%x" % sum(1 << (4 * r + c) for r in R for c in C), nr, n // nr))
    return out


class Rule:
    def __init__(self, scan_path, e220_csv, out):
        self.S = json.load(open(scan_path))
        self.scan_sha = sha(scan_path)
        self.NV = NRZ.Never(self.S)
        if sha(e220_csv) != E220_POINTS_CSV_SHA:
            print(f"point_rule_e222: REFUSED, {e220_csv} is not E220's POINTS-e220.csv {E220_POINTS_CSV_SHA}")
            sys.exit(4)
        self.e220_csv = e220_csv
        self.M = MZ.Models()
        self.P = load("points_e215_pinned", pinned(*E215_POINTS_PY))
        th = self.M.P32["time"]["theta"]
        self.x1, self.w1, self.x2, self.w2, self.pB = th["x1"], th["w1"], th["x2"], th["w2"], th["pB"]
        self.out = out
        self.cands = {}
        self.cache = {}
        self.line = MZ.STOP_W - DROP_MARGIN_W

    # ---------------------------------------------------------------- forecasts at 600 MHz on aifoundry3 card 0, cached
    def fc(self, items, models=MZ.MODELS, cands=True, which=("posimb", "af4", "l3s")):
        mk = "|".join(models) + ("|cands:" + ",".join(which) if cands else "")
        need = [it for it in items if (key(it["arm"], it["fmt"], it["mask"]), mk) not in self.cache]
        if need:
            pts = [{"id": key(it["arm"], it["fmt"], it["mask"]), "arm": it["arm"], "fmt": it["fmt"], "kind": "random", "mask": it["mask"]} for it in need]
            got = self.M.forecast(pts, models=models, cands=cands, which=which)
            for k, v in got.items():
                self.cache[(k, mk)] = v
        return [self.cache[(key(it["arm"], it["fmt"], it["mask"]), mk)] for it in items]

    def pp(self, token, fmt, mask):
        fcs = self.fc([{"arm": token, "fmt": fmt, "mask": mask}])[0]
        pp32, ppall, by = self.M.planning_peak(fcs, token)
        return pp32, ppall, by, fcs

    def never(self, token, mask, reading):
        ok, ev = self.NV.verdict(reading, token, mask)
        return bool(ok), ev

    # ---------------------------------------------------------------- family R: E218's own points, same-card repeats (REPORTED only)
    def family_r(self):
        rows = {r["id"]: r for r in csv.DictReader(open(pinned(*E218_POINTS)))}
        out, rec = [], []
        for e in R_IDS:
            r = rows[e]
            pp32, ppall, by, _ = self.pp(r["arm"], r["format"], r["shire_mask"])
            drop = None if (pp32 is not None and pp32 < self.line) else f"planning peak {pp32} W at or above the {self.line:.0f} W line"
            rec.append({"e218_id": e, "token": r["arm"], "fmt": r["format"], "mask": r["shire_mask"], "PP32_W": pp32, "PP_all_W": ppall, "dropped": drop})
            if drop:
                continue
            fam_sub = {"Y": "R-Y", "G": "R-G", "Gt": "R-Gt"}[r["family"]]
            out.append({"id": "r" + e, "family": "R", "subfamily": fam_sub, "source": f"E218 {e} (its {r['family']}; a same-card repeat, REPORTED only)",
                        "token": r["arm"], "fmt": r["format"], "kind": "random", "mask": r["shire_mask"], "neverrun_reading": "exempt",
                        "pair": ("ry01" if r["family"] == "Y" else ""), "pair_role": (e[-1] if r["family"] == "Y" else ""),
                        "twin": ("rg01t" if e == "g01" else ""), "twin_of": ("rg01" if e == "g01t" else ""), "e218_id": e, "e220_id": "",
                        "PP32_W": pp32, "PP_all_W": ppall})
        self.cands["R"] = rec
        return out

    # ---------------------------------------------------------------- family T: E220's lead-family points as aifoundry3 twins
    def family_t(self, used):
        rows = [r for r in csv.DictReader(open(self.e220_csv)) if r["arm"] == "A" and r["family"] in T_FAMILIES]
        assert len(rows) == 32, len(rows)
        rec, ok_ids = [], {}
        for r in rows:
            ok, ev = self.never(r["token"], r["shire_mask"], "token")
            pp32, ppall, by, _ = self.pp(r["token"], r["format"], r["shire_mask"])
            why = None
            if not ok:
                why = "ran on aifoundry3 card 0 (token reading, session records)"
            elif pp32 is None:
                why = "MM1-v3.2 does not price its energy"
            elif pp32 >= self.line:
                why = f"planning peak by MM1-v3.2 {pp32:.2f} W within {DROP_MARGIN_W:.0f} W of the {MZ.STOP_W:.0f} W stop"
            rec.append({"e220_id": r["id"], "family": r["family"], "token": r["token"], "fmt": r["format"], "mask": r["shire_mask"], "never_run": ok,
                        "evidence": ev, "PP32_W": pp32, "PP_all_W": ppall, "PP_all_by": by, "alone": why})
            ok_ids[r["id"]] = (why is None, r, pp32, ppall)
        # a Y2 pair keeps both masks or neither; a G2 point and its twin are kept or dropped together
        partner = {}
        for r in rows:
            if r["family"] == "Y2":
                partner[r["id"]] = r["id"][:-1] + ("b" if r["id"].endswith("a") else "a")
            elif r["family"] == "G2":
                partner[r["id"]] = r["id"] + "t"
            elif r["family"] == "G2t":
                partner[r["id"]] = r["id"][:-1]
        out = []
        for c in rec:
            pid = c["e220_id"]
            good = ok_ids[pid][0] and (pid not in partner or ok_ids[partner[pid]][0])
            c["dropped"] = None if good else (c["alone"] or f"its partner {partner[pid]} dropped")
            if not good:
                continue
            r, pp32, ppall = ok_ids[pid][1], ok_ids[pid][2], ok_ids[pid][3]
            fam = r["family"]
            sub = "T-" + fam
            pair = ("w" + r["pair"]) if r.get("pair") else ""
            out.append({"id": "w" + pid, "family": "T", "subfamily": sub, "source": f"E220 {pid} ({fam}; both E220 arms: aifoundry1 card 1 and aifoundry2 card 0)",
                        "token": r["token"], "fmt": r["format"], "kind": "random", "mask": r["shire_mask"], "neverrun_reading": "token",
                        "pair": pair, "pair_role": (pid[-1] if fam == "Y2" else ""), "twin": ("w" + r["twin"]) if r.get("twin") else "",
                        "twin_of": ("w" + r["twin_of"]) if r.get("twin_of") else "", "e218_id": "", "e220_id": pid, "PP32_W": pp32, "PP_all_W": ppall})
            used.add(tuple(self.P.parse_arm(r["token"])[1]))
        self.cands["T"] = rec
        return out

    # ---------------------------------------------------------------- family L3b: L3S's family around the L3 edges
    def family_l3b(self, used):
        picked, recs = [], {}
        for sub in L3B_ORDER:
            cfg = L3B[sub]
            cs = []
            if sub in ("L3b-1", "L3b-3"):
                lo, hi = cfg["d"]
                for MB in L3_GRID["MB"]:
                    for NB in cfg["NB"]:
                        for KB in L3_GRID["KB"]:
                            d = footprint(MB, NB, KB)
                            if not (lo < d <= hi if sub == "L3b-3" else lo <= d <= hi):
                                continue
                            t = tok("gemmL", MB, NB, KB)
                            ok, ev = self.never(t, FULLM, "token")
                            cs.append({"sub": sub, "token": t, "shape": [MB, NB, KB], "d_MB": d, "side": ("below" if d < self.x1 else "above"),
                                       "never_run": ok, "string": key(t, "fp32", FULLM)})
                todo = [c for c in cs if c["never_run"] and tuple(c["shape"]) not in used]
                fcs = self.fc([{"arm": c["token"], "fmt": "fp32", "mask": FULLM} for c in todo], models=("MM1-v3.2",), which=("l3s",))
                for c, f in zip(todo, fcs):
                    c["T_v32_us"], c["T_L3S_us"] = f["MM1-v3.2"]["T_op_us"], f[MZ.L3S]["T_op_us"]
                    c["delta_ln"] = math.log(c["T_L3S_us"] / c["T_v32_us"])
                    c["score"] = -abs(c["delta_ln"])
                for c in cs:
                    c.setdefault("score", None)
                cs.sort(key=lambda c: ((c["score"] if c["score"] is not None else 1e9), c["string"]))
            else:
                G = L3B_2_GRID
                for MB in G["MB"]:
                    for NB in G["NB"]:
                        for KB in G["KB"]:
                            d = footprint(MB, NB, KB)
                            if abs(d - self.x2) > cfg["half_width"]:
                                continue
                            t = tok("gemmL", MB, NB, KB)
                            ok, ev = self.never(t, FULLM, "token")
                            cs.append({"sub": sub, "token": t, "shape": [MB, NB, KB], "d_MB": d, "side": ("below" if d < self.x2 else "above"),
                                       "never_run": ok, "score": abs(d - self.x2), "string": key(t, "fp32", FULLM)})
                cs.sort(key=lambda c: (c["score"], c["string"]))
            chosen, nbs = [], set()
            quota, min_side = cfg["quota"], cfg.get("min_side", 0)
            for c in cs:
                if len(chosen) >= quota:
                    c["verdict"] = "not reached (quota full)"
                    continue
                if not c["never_run"]:
                    c["verdict"] = "ran on aifoundry3 card 0 (token reading, session records)"
                    continue
                if tuple(c["shape"]) in used:
                    c["verdict"] = "shape already in E222"
                    continue
                if any(abs(c["d_MB"] - x["d_MB"]) < 1e-9 for x in chosen):
                    c["verdict"] = "footprint already drawn in this subfamily"
                    continue
                if sub != "L3b-1" and c["shape"][1] in nbs:
                    c["verdict"] = f"NB already drawn in {sub}"
                    continue
                pp32, ppall, by, f = self.pp(c["token"], "fp32", FULLM)
                c["PP32_W"], c["PP_all_W"] = pp32, ppall
                if pp32 is None or pp32 >= self.line:
                    c["verdict"] = "planning peak within 3 W of the stop (or not priced)"
                    continue
                if min_side:
                    below = sum(1 for x in chosen if x["side"] == "below")
                    above = len(chosen) - below
                    if c["side"] == "below" and above < min_side and (quota - len(chosen)) <= (min_side - above):
                        c["verdict"] = "the side balance (room kept for the other side)"
                        continue
                    if c["side"] == "above" and below < min_side and (quota - len(chosen)) <= (min_side - below):
                        c["verdict"] = "the side balance (room kept for the other side)"
                        continue
                if "delta_ln" not in c:
                    c["T_v32_us"], c["T_L3S_us"] = f["MM1-v3.2"]["T_op_us"], f[MZ.L3S]["T_op_us"]
                    c["delta_ln"] = math.log(c["T_L3S_us"] / c["T_v32_us"])
                c["verdict"] = "drawn"
                chosen.append(c)
                nbs.add(c["shape"][1])
                used.add(tuple(c["shape"]))
            recs[sub] = [c for c in cs if c.get("verdict") not in (None, "not reached (quota full)") or c in chosen][:300]
            picked += chosen
        self.cands["L3b"] = recs
        out = []
        for n, c in enumerate(picked, 1):
            src = {"L3b-1": f"NB 1 around the first L3 edge x1 = {self.x1:.2f} MB (gemmL2x1x7's family), ranked by |ln(T_L3S / T_v32)| descending",
                   "L3b-3": "the set-overflow band (32, 48] MB at NB >= 2, ranked by |ln(T_L3S / T_v32)| descending",
                   "L3b-2": f"around the second L3 edge x2 = {self.x2:.2f} MB, ranked by |d - x2|"}[c["sub"]]
            out.append({"id": f"b{n:02d}", "family": "L3b", "subfamily": c["sub"], "source": src, "token": c["token"], "fmt": "fp32", "kind": "random",
                        "mask": FULLM, "neverrun_reading": "token", "footprint_MB": c["d_MB"], "edge_side": c["side"], "pair": "", "pair_role": "",
                        "twin": "", "twin_of": "", "e218_id": "", "e220_id": "", "PP32_W": c["PP32_W"], "PP_all_W": c["PP_all_W"],
                        "rule_delta_ln_L3S_vs_v32": c.get("delta_ln")})
        return out

    # ---------------------------------------------------------------- family Y3: equal-count layout pairs for posimb
    def family_y3(self, used):
        masks = [(m, nr, nc) for (m, nr, nc) in product_masks(Y3_SHIRES) if self.NV.mask(m)[0]]       # masks never run on the card
        out, recs, mask_used = [], [], set()
        for pid, src, what in Y3_SOURCES:
            m0 = self.P.parse_arm(src)[1]
            shapes = []
            for MB in Y3_GRID["MB"]:
                for NB in Y3_GRID["NB"]:
                    for KB in Y3_GRID["KB"]:
                        dist = abs(math.log2(MB / m0[0])) + abs(math.log2(NB / m0[1])) + abs(math.log2(KB / m0[2]))
                        shapes.append((dist, key(tok("gemmL", MB, NB, KB), "fp32", FULLM), (MB, NB, KB)))
            shapes.sort()
            tried, pick = [], None
            for dist, s, shp in shapes:
                t = tok("gemmL", *shp)
                if shp in used:
                    tried.append({"token": t, "dist": dist, "verdict": "shape already in E222"})
                    continue
                ok, ev = self.never(t, FULLM, "token")
                if not ok:
                    tried.append({"token": t, "dist": dist, "verdict": "ran on aifoundry3 card 0 (token reading, session records)"})
                    continue
                avail = [x for x in masks if x[0] not in mask_used]
                fcs = self.fc([{"arm": t, "fmt": "fp32", "mask": m} for m, _, _ in avail], models=("MM1-v3.2",), which=("posimb",))
                g = {m: (f[MZ.POSIMB]["cycles_per_op_wall"], f["MM1-v3.2"]["cycles_per_op_wall"], f) for (m, _, _), f in zip(avail, fcs)}
                best = None
                for (ma, ra, ca), (mb, rb, cb) in itertools.combinations(avail, 2):
                    dpos = math.log(g[ma][0] / g[mb][0])
                    d32 = math.log(g[ma][1] / g[mb][1])
                    sep = abs(dpos - d32)
                    # orient: the first mask is the one posimb puts slower
                    a_, b_ = (ma, mb) if dpos >= 0 else (mb, ma)
                    cand = (-sep, f"{a_}|{b_}", a_, b_, abs(dpos), abs(d32))
                    if best is None or cand < best:
                        best = cand
                if best is None:
                    tried.append({"token": t, "dist": dist, "verdict": "no mask pair left"})
                    continue
                _, s2, ma, mb, sep, d32 = best
                pa = self.pp(t, "fp32", ma)
                pb = self.pp(t, "fp32", mb)
                if pa[0] is None or pb[0] is None or max(pa[0], pb[0]) >= self.line:
                    tried.append({"token": t, "dist": dist, "verdict": "planning peak within 3 W of the stop (or not priced)"})
                    continue
                pick = (t, shp, dist, ma, mb, sep, d32, pa, pb, g[ma][2][MZ.POSIMB]["term"], g[mb][2][MZ.POSIMB]["term"])
                tried.append({"token": t, "dist": dist, "verdict": "drawn", "pair": [ma, mb], "posimb_ln_a_over_b": sep, "v32_ln_a_over_b": d32})
                break
            recs.append({"pair": pid, "source": src, "what": what, "tried": tried[:40], "n_tried": len(tried)})
            if pick is None:
                continue
            t, shp, dist, ma, mb, sep, d32, pa, pb, ta, tb = pick
            used.add(shp)
            mask_used.update((ma, mb))
            for role, m, pk, term in (("a", ma, pa, ta), ("b", mb, pb, tb)):
                out.append({"id": f"{pid}{role}", "family": "Y3", "subfamily": "Y3-pair", "source": (f"{what}'s shape neighbourhood ({src}, distance {dist:.3f} "
                            f"in log2 units); the 2-shire product-mask pair never run on aifoundry3 card 0 with the largest posimb separation "
                            f"|ln(T_a / T_b)| = {sep:.4f} (MM1-v3.2 {d32:+.1e})"), "token": t, "fmt": "fp32", "kind": "random", "mask": m,
                            "neverrun_reading": "token+masks", "pair": pid, "pair_role": role, "twin": "", "twin_of": "", "e218_id": "", "e220_id": "",
                            "PP32_W": pk[0], "PP_all_W": pk[1], "rule_posimb_g_wall": term["g_wall"]})
        self.cands["Y3"] = {"masks_eligible": len(masks), "pairs": recs}
        return out

    # ---------------------------------------------------------------- family G3: gemmLnc at small predicted excess for AF4, with twins
    def family_g3(self, used):
        items = []
        for fmt in ("fp32", "int8"):
            for MB in G3_MB:
                for NB in G3_NB:
                    for KB in G3_KB:
                        items.append({"arm": tok("gemmLnc", MB, NB, KB), "fmt": fmt, "mask": FULLM, "shape": (MB, NB, KB)})
        # MM1-v3.2's map decides the regime (no candidate needed); AF4's share is asked only of the regimes' never-run candidates
        f32 = self.fc(items, models=("MM1-v3.2",), cands=False)
        pre = []
        for it, f in zip(items, f32):
            x = f["MM1-v3.2"]
            beyond = MZ.beyond_of(x["Q_mean"])
            NB = it["shape"][1]
            reg = "L2" if beyond < 2.6 else ("NB56" if NB in (5, 6) else None)
            if reg is None or (it["fmt"] == "int8" and reg != "L2") or "W_over_idle" not in x:
                continue
            n1, _ = self.never(it["arm"], FULLM, "token")
            n2, _ = self.never(tok("gemmL", *it["shape"]), FULLM, "token")
            pre.append((it, reg, beyond, n1, n2))
        live = [p for p in pre if p[3] and p[4] and tuple(p[0]["shape"]) not in used]
        fca = self.fc([p[0] for p in live], models=("MM1-v3.2",), which=("af4",))
        cands = []
        for (it, reg, beyond, n1, n2), f in zip(live, fca):
            a = f[MZ.AF4]
            share = a["term"]["term_AF4_W"] / a["W_over_idle"]
            cands.append({"token": it["arm"], "fmt": it["fmt"], "shape": list(it["shape"]), "regime": reg, "beyond": beyond,
                          "R4": a["term"]["features"]["R4"], "AF4_W": a["term"]["term_AF4_W"], "F3_W": a["term"]["MM1-v3.2_F3_W"],
                          "W_af4": a["W_over_idle"], "W_v32": f["MM1-v3.2"]["W_over_idle"], "score_share": share, "string": key(it["arm"], it["fmt"], FULLM)})
        by = {r: sorted([c for c in cands if c["regime"] == r], key=lambda c: (c["score_share"], c["string"])) for r in ("L2", "NB56")}
        quota = dict(G3_QUOTA)
        drawn, nbkb = [], set()
        for reg in ("L2", "NB56"):
            n_have = 0
            for c in by[reg]:
                if n_have >= quota[reg]:
                    break
                shp = tuple(c["shape"])
                if shp in used:
                    c["verdict"] = "shape already in E222"
                    continue
                if (shp[1], shp[2]) in nbkb:
                    c["verdict"] = "(NB, KB) already drawn in G3"
                    continue
                pg = self.pp(c["token"], c["fmt"], FULLM)
                pt = self.pp(tok("gemmL", *shp), c["fmt"], FULLM)
                c["PP32_W"], c["PP_all_W"], c["twin_PP32_W"], c["twin_PP_all_W"] = pg[0], pg[1], pt[0], pt[1]
                if pg[0] is None or pt[0] is None or pg[0] >= self.line or pt[0] >= self.line:
                    c["verdict"] = "planning peak (the point's or its twin's) within 3 W of the stop"
                    continue
                c["verdict"] = "drawn"
                drawn.append(c)
                used.add(shp)
                nbkb.add((shp[1], shp[2]))
                n_have += 1
            if reg == "L2" and n_have < quota["L2"]:
                quota["NB56"] += quota["L2"] - n_have
        self.cands["G3"] = {"regime_counts_all": {r: sum(1 for p in pre if p[1] == r) for r in ("L2", "NB56")},
                            "never_run_both": {r: sum(1 for p in live if p[1] == r) for r in ("L2", "NB56")}, "quota_after_pass_on": quota,
                            "walked": {r: [c for c in v if "verdict" in c] for r, v in by.items()}, "short": len(drawn) < G3_MIN}
        out = []
        for n, c in enumerate(drawn, 1):
            shp = tuple(c["shape"])
            out.append({"id": f"k{n:02d}", "family": "G3", "subfamily": f"G3-{c['regime']}", "source": (f"rgm136 gemmLnc, regime {c['regime']} (beyond "
                        f"{c['beyond']:.3f}, R4 {c['R4']:.3f}), AF4's predicted excess share of its W over idle {c['score_share']:.4f} (ascending: small "
                        f"predicted excess for AF4)"), "token": c["token"], "fmt": c["fmt"], "kind": "random", "mask": FULLM, "neverrun_reading": "token",
                        "pair": "", "pair_role": "", "twin": f"k{n:02d}t", "twin_of": "", "e218_id": "", "e220_id": "", "PP32_W": c["PP32_W"],
                        "PP_all_W": c["PP_all_W"]})
            out.append({"id": f"k{n:02d}t", "family": "G3t", "subfamily": f"G3t-{c['regime']}", "source": f"the cooperative twin of k{n:02d}",
                        "token": tok("gemmL", *shp), "fmt": c["fmt"], "kind": "random", "mask": FULLM, "neverrun_reading": "token", "pair": "",
                        "pair_role": "", "twin": "", "twin_of": f"k{n:02d}", "e218_id": "", "e220_id": "", "PP32_W": c["twin_PP32_W"],
                        "PP_all_W": c["twin_PP_all_W"]})
        return out

    # ---------------------------------------------------------------- the order and the card-time plan
    def order(self, pts):
        gnc = [p for p in pts if p["token"].startswith("gemmLnc")]
        rest = [p for p in pts if not p["token"].startswith("gemmLnc")]
        p1 = sorted(p["id"] for p in rest)
        random.Random("E222|A|pass1").shuffle(p1)
        rep = {p["id"] for p in rest if p["family"] in ("L3b", "Y3") or p["subfamily"] in ("T-L3", "T-Y2", "R-Y")}
        p2 = [i for i in reversed(p1) if i in rep]
        gb = [p["id"] for p in sorted(gnc, key=lambda p: (p["PP32_W"], p["id"]))]
        g3 = [i for i in reversed(gb) if i.startswith("k")]
        runs = [("smoke", "s01"), ("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in p2] + \
            [("tie", "t01"), ("smoke", "s03")] + [("G block", i) for i in gb] + [("G block reversed (G3 only)", i) for i in g3]
        n_runs = sum(1 for b, _ in runs if b != "smoke")
        what, pace = PACE
        card_min = n_runs * pace / 60.0
        subset = 2 + len(p1)
        thinned = []
        # THE THINNING RULE (stated before the forecasts): over the target, family T's pass-2 runs leave first (T-Y2, then T-L3, last
        # first), then T's points (T-L3 by id descending, then T-Y2 pairs by id descending), until the plan is at or under the target
        while card_min > TARGET_MIN:
            t2 = [i for i in reversed(p2) if i.startswith("wp")] + [i for i in reversed(p2) if i.startswith("wl")]
            if t2:
                p2.remove(t2[0])
                thinned.append(("pass2", t2[0]))
            else:
                break
            runs = [("smoke", "s01"), ("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in p2] + \
                [("tie", "t01"), ("smoke", "s03")] + [("G block", i) for i in gb] + [("G block reversed (G3 only)", i) for i in g3]
            n_runs = sum(1 for b, _ in runs if b != "smoke")
            card_min = n_runs * pace / 60.0
        return {"pass1": p1, "pass2": p2, "G_block": gb, "G_block_reversed": g3, "runs": [{"n": k + 1, "block": b, "id": i} for k, (b, i) in enumerate(runs)],
                "n_runs_scored_and_ties": n_runs, "n_smoke": sum(1 for b, _ in runs if b == "smoke"), "pace_s_per_run": pace, "pace_source": what,
                "card_minutes_planned": card_min, "target_min": TARGET_MIN, "rule_min": RULE_MIN, "cap_min": CAP_MIN, "thinned": thinned,
                "registered_subset_if_cut": {"what": "the opening smoke, tie 1, pass 1 and tie 2 (every non-gemmLnc point once; the G block not reached)",
                                             "runs": subset, "card_minutes": subset * pace / 60.0}}

    def describe(self, p):
        loop = "rgm136 gemmLnc" if p["token"].startswith("gemmLnc") else "rgm136 gemmL"
        d = self.P.describe(p["id"], "A", p["family"], "registered", p["token"], p["fmt"], p["kind"], p["mask"], loop, "point", p["source"], MZ.A3)
        d["f_mhz"] = MZ.F_REG
        for k in ("subfamily", "source", "neverrun_reading", "pair", "pair_role", "twin", "twin_of", "e218_id", "e220_id", "PP32_W", "PP_all_W",
                  "footprint_MB", "edge_side", "rule_delta_ln_L3S_vs_v32", "rule_posimb_g_wall"):
            if k in p:
                d[k] = p[k]
        d["token"] = p["token"]
        d["footprint_MB_full_chip"] = footprint(*d["shape"])
        d["card"] = MZ.A3
        return d

    def run(self):
        t0 = now()
        res = {"what": "E222's point rule applied (POINT-RULE-e222.md; desk/point_rule_e222.py)", "started": t0, "scan_sha256": self.scan_sha,
               "e220_points_csv_sha256": E220_POINTS_CSV_SHA, "x1_MB": self.x1, "w1_MB": self.w1, "x2_MB": self.x2, "w2_MB": self.w2, "pB": self.pB,
               "eps_G": self.M.eps_g, "rest_law": self.M.rest, "card": MZ.A3, "f_mhz": MZ.F_REG, "stop_W": MZ.STOP_W, "drop_line_W": self.line}
        used = set()
        rr = self.family_r()
        tt = self.family_t(used)
        for p in rr:
            used.add(tuple(self.P.parse_arm(p["token"])[1]))
        l3 = self.family_l3b(used)
        y3 = self.family_y3(used)
        g3 = self.family_g3(used)
        pts = rr + tt + l3 + y3 + g3
        ids = [p["id"] for p in pts]
        assert len(ids) == len(set(ids)), "duplicate ids"
        plan = self.order(pts)
        # the extra rows (tie and smoke: never points) priced for the plan
        ex = {}
        for i, t, f in EXTRA:
            pp32, ppall, by, _ = self.pp(t, f, FULLM)
            ex[i] = {"token": t, "fmt": f, "PP32_W": pp32, "PP_all_W": ppall}
        desc = [self.describe(p) for p in pts]
        res.update({"counts": {f: sum(1 for p in pts if p["family"] == f) for f in ("R", "T", "L3b", "Y3", "G3", "G3t")},
                    "t_counts": {s: sum(1 for p in pts if p["subfamily"] == s) for s in ("T-L3", "T-Y2", "T-G2", "T-G2t")},
                    "t_dropped": [c for c in self.cands["T"] if c["dropped"]], "plan": plan, "extra_rows": ex,
                    "highest_PP32": max(p["PP32_W"] for p in pts), "highest_PP_all": max(p["PP_all_W"] for p in pts if p["PP_all_W"] is not None),
                    "g3_short": self.cands["G3"]["short"], "points": desc})
        res["ended"] = now()
        os.makedirs(os.path.join(self.out, "desk"), exist_ok=True)
        cpath = os.path.join(self.out, "desk", "candidates-e222.json")
        json.dump({"what": "every candidate of E222's point rule", "scan_sha256": self.scan_sha, "candidates": self.cands, "started": t0,
                   "ended": res["ended"]}, open(cpath, "w"), indent=1, sort_keys=True, default=str)
        res["candidates_sha256"] = sha(cpath)
        self.M.save_l3s_extra()
        fpath = os.path.join(self.out, "desk", "posimb-features-e222.json")
        json.dump(self.M.PS_made, open(fpath, "w"), indent=1, sort_keys=True)
        res["l3s_extra_sha256"] = sha(MZ.L3S_EXTRA)
        res["posimb_features_sha256"] = sha(fpath)
        ppath = os.path.join(self.out, "points-e222.json")
        json.dump(res, open(ppath, "w"), indent=1, sort_keys=True, default=str)
        cols = ["id", "family", "subfamily", "pair", "pair_role", "twin", "twin_of", "e218_id", "e220_id", "loop", "kernel", "host", "elf", "token",
                "format", "kind", "shire_mask", "shires", "minions", "M", "N", "K", "M_computed", "N_computed", "ops_per_minion_per_gemm", "macs_per_gemm",
                "case", "footprint_MB_full_chip", "neverrun_reading", "f_mhz", "PP32_W", "PP_all_W", "values"]
        with open(os.path.join(self.out, "points-e222.csv"), "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(cols)
            for d in desc:
                w.writerow([("" if d.get(c) is None else d.get(c)) for c in cols])
        print(f"point rule: {t0} - {res['ended']}")
        print(f"counts {res['counts']}; T {res['t_counts']}; T dropped {len(res['t_dropped'])}; highest PP32 {res['highest_PP32']:.2f} W (line "
              f"{self.line:.0f} W); runs {plan['n_runs_scored_and_ties']} + {plan['n_smoke']} smoke, planned {plan['card_minutes_planned']:.1f} "
              f"card-minutes; thinned {plan['thinned']}; G3 short {res['g3_short']}")
        print(f"points-e222.json {sha(ppath)}; points-e222.csv {sha(os.path.join(self.out, 'points-e222.csv'))}; candidates {res['candidates_sha256']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--e220-points", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    Rule(a.scan, os.path.abspath(a.e220_points), a.out).run()


if __name__ == "__main__":
    main()
