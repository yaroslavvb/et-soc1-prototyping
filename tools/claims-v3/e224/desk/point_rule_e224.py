#!/usr/bin/env python3
"""E224 (Q237): THE POINT RULE (POINT-RULE-e224.md), applied mechanically to E224's two arms (A: aifoundry1 card 1 at 600 MHz; B: aifoundry2
card 0 under its governor, priced at 799.0 MHz). Written and hashed (desk/point-rule-e224.sha256, with the clock's time) together with
POINT-RULE-e224.md, desk/models_e224.py and desk/neverrun_e224.py BEFORE any forecast was computed; the scan it reads (desk/scan-e224-reg.json)
holds no forecast.

    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/point_rule_e224.py --scan tools/claims-v3/e224/desk/scan-e224-reg.json \
        --e220-points <OUT/reg-e220/POINTS-e220.csv> --e222-points <OUT/reg-e222/POINTS-e222.csv> --out tools/claims-v3/e224 [--mock]

Writes desk/candidates-e224.json (every candidate walked, with its verdict), points-e224.json and points-e224.csv (the points per arm, their order
and the card-time plan), desk/avoid-e224.json (the shapes avoided and where each is named), desk/l3s-extra-e224.json and
desk/posimb-features-e224.json (the L3S set-model records and posimb features the frozen candidate code made). --mock replaces every forecaster
by deterministic stand-in numbers (the control flow's own desk test, run before the hash into a temporary folder; never a registered output).
numpy through the predictors; single-threaded (the caller sets the thread variables).
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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E224 = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import neverrun_e224 as NRZ  # noqa: E402

E215_POINTS_PY = ("tools/claims-v3/e215/points_e215.py", "a8733593aaf91a3a38284ae4ce177983a8a4f57cc2f0363ceeb38b34a3f88f29")
# THE AVOID LIST's sources (the brief: none among E220's, E221's or E222's registered or scheduled points), each pinned
AVOID_FILES = {
    "tools/claims-v3/e220/points-e220.json": "2451ca9d3763c17b2366a4c1b88e680a15a30a01a7a93e0cbf1c041d9f87bd28",
    "tools/claims-v3/e220/plan-e220.json": "6d63318734f61bc6b9c9fa7550b52434b2d309e9f1182a6964413fb3a6ef79d9",
    "tools/claims-v3/e221/proposal/src/arms.json": None,
    "tools/claims-v3/e221/proposal/src/sched/a1c0-S1.json": None, "tools/claims-v3/e221/proposal/src/sched/a1c0-S2.json": None,
    "tools/claims-v3/e221/proposal/src/sched/a1c0-S3.json": None, "tools/claims-v3/e221/proposal/src/sched/a1c1-S1.json": None,
    "tools/claims-v3/e221/proposal/src/sched/a1c1-S2.json": None, "tools/claims-v3/e221/proposal/src/sched/a1c1-S3.json": None,
    "tools/claims-v3/e221/proposal/src/sched/a2c0-S1.json": None, "tools/claims-v3/e221/proposal/src/sched/a2c0-S2.json": None,
    "tools/claims-v3/e221/proposal/src/sched/a2c0-S3.json": None,
}
E220_POINTS_CSV_SHA = "64a7c99a90a2d899db44dc0c3790dfd840cd02b49c9d12f24396f4691125afc4"   # OUT/reg-e220/POINTS-e220.csv (POINTS.txt 058984a0...)
E222_POINTS_CSV_SHA = "8b709d4bf80ba98bd90728b492f7f6aca4edcc516615c194de1da65b38f69809"   # OUT/reg-e222/POINTS-e222.csv (POINTS.txt fe996c15...)
E222_POINTS_JSON = ("W/out/reg-e222/frozen/points-e222.json", "55d41a4b3d3e7035e424e3006e8d83079bf33adca80c2205d11a378600202a61")
E220_POINTS_TXT_SHA = "058984a04b90cd8585cb41cc6618430306d7bf1c7e230159e7719b9e9e1e9bdc"   # OUT/reg-e220/POINTS.txt (the brief's E220 file)
E222_POINTS_TXT_SHA = "fe996c15de2793e9470690f8c1c820ad1c65df2c2cc15777a4e747c131941976"   # OUT/reg-e222/POINTS.txt (the brief's E222 file)
SHAPE_RX = re.compile(r"gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)(?![0-9x])")
ARMNAME_RX = re.compile(r"(?<![0-9x])(\d+)x(\d+)x(\d+)-(?:fp32|fp16|int8)")
FULLM = "0xffffffff"
DROP_MARGIN_W = 3.0
SEC_CAP_S = 0.40
GRID = {"MB": range(1, 17), "NB": range(1, 17), "KB": range(1, 49)}
C1, A2 = "aifoundry1 card 1", "aifoundry2 card 0"
CARD = {"A": C1, "B": A2}
F_REG = {"A": 600.0, "B": 799.0}
STOP = {"A": 72.0, "B": 70.0}
# FAMILY D: 30 slots per arm (id, regions in order (the first, then its fallback), format, kind, shires); regions by MM1-v3's full-chip
# footprint d (MB) against MM1-v3.2's edges x1 and x2 and by KB (MM1's shire-cache regime at KB <= 2)
D_SLOTS = (("d01", ("L2",), "fp32", "random", 32), ("d02", ("L2",), "fp16", "random", 32), ("d03", ("L2",), "int8", "random", 32),
           ("d04", ("L2",), "fp32", "ones", 32), ("d05", ("L2",), "int8", "zeros", 32),
           ("d06", ("L3", "mid"), "fp32", "random", 32), ("d07", ("L3", "mid"), "fp16", "random", 32),
           ("d08", ("x1-below",), "fp32", "random", 32), ("d09", ("x1-above",), "fp32", "random", 32), ("d10", ("x1-below",), "fp16", "random", 32),
           ("d11", ("x1-above",), "int8", "random", 32),
           ("d12", ("mid",), "fp32", "random", 32), ("d13", ("mid",), "fp16", "random", 32), ("d14", ("mid",), "int8", "random", 32),
           ("d15", ("mid",), "fp32", "zeros", 32), ("d16", ("mid",), "fp16", "ones", 32), ("d17", ("mid",), "fp32", "random", 32),
           ("d18", ("x2-below",), "fp32", "random", 32), ("d19", ("x2-above",), "fp32", "random", 32), ("d20", ("x2-above",), "fp16", "random", 32),
           ("d21", ("x2-below",), "int8", "random", 32),
           ("d22", ("beyond",), "fp32", "random", 32), ("d23", ("beyond",), "fp16", "random", 32), ("d24", ("beyond",), "int8", "ones", 32),
           ("d25", ("subset",), "fp32", "random", 1), ("d26", ("subset",), "fp16", "random", 4), ("d27", ("subset",), "fp32", "random", 8),
           ("d28", ("subset",), "int8", "random", 16),
           ("d29", ("G-mid", "G-L3"), "fp32", "random", 32), ("d30", ("G-L2",), "int8", "random", 32))
# FAMILY P: four shapes, each with two operand patterns the RTL bench counted (one of E212's, one of E217's), a zeros twin and a random twin
P_SLOTS = (("p1", "fp32"), ("p2", "fp32"), ("p3", "fp16"), ("p4", "int8"))
E212_KINDS = {"fp32": ["bf16trunc", "den16", "den21", "den4", "den8", "fld_mant", "fld_sign", "fp16grid", "lanes2", "pow2"],
              "fp16": ["den16_10", "den16_4", "fld16_exp", "fld16_mant", "fld16_sign"], "int8": ["i8_den1", "i8_den3", "i8_den6", "i8_pm1"]}
E217_KINDS = {"fp32": ["rt16", "rt32", "rt32b", "rt64", "sg_kk", "sgm1", "th_top"], "fp16": ["h_rt32", "h_rt64", "h_sg", "h_th_in"],
              "int8": ["i8_t06", "i8_t1", "i8_t2", "i8_t3", "i8_t46", "i8_t5"]}
E212_TILES = "tools/claims-v3/e212/proposal/src/tiles"
E217_TILES = "tools/claims-v3/e217/proposal/src/tiles"
# FAMILY L
L3S_SUBS = {"L3S-1": {"quota": 3, "min_side": 1, "NB": (1, 2), "d_x1": (0.8, 1.3)}, "L3S-2": {"quota": 3, "NB": tuple(range(3, 17)), "d": (32.0, 48.0)}}
POS_SOURCES = (("y1", "gemmL1x8x8", "E216 y01"), ("y2", "gemmL1x8x12", "E216 y02"), ("y3", "gemmL1x4x16", "E216 y03"))
POS_GRID = {"MB": range(1, 5), "NB": range(2, 17), "KB": range(2, 33)}
AF4_MB = tuple(range(1, 9))
AF4_NB = (1, 2, 3, 5, 6)
AF4_KB = (1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48)
AF4_QUOTA = {"L2": 1, "NB56": 2}
# THE ORDER AND THE CARD TIME (E220's pace on each card, E220.md section 6)
PACE = {"A": ("E215 arm B (docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1): 71 runs, 5 smoke processes and the stop-path test in "
              "28.55 card-minutes (E220.md section 6)", 24.13),
        "B": ("E216 (docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2): 69 runs with the opening rest, the smoke and the stop-path test in "
              "27.55 card-minutes (E220.md section 6)", 23.96)}
TARGET_MIN, RULE_MIN, CAP_MIN = 50.0, 65.0, 75.0
TIE = ("t01", "gemmL2x4x4", "fp32", "random")
SMOKE = {"A": {"s01": [("gemmL2x2x2", "fp32", "random")], "s03": [("gemmLnc2x1x37", "fp32", "random")]},
         "B": {"s01": [("gemmL1x1x4", "fp16", "ones"), ("gemmL1x1x4", "fp32", "zeros"), ("gemmL1x1x4", "int8", "random")],
               "s03": [("gemmLnc6x5x10", "fp32", "random")]}}


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tok(pre, MB, NB, KB):
    return f"{pre}{MB}x{NB}x{KB}"


def footprint(MB, NB, KB):
    """MM1-v3's mm1_core_v3.footprint at the full chip (E220's, E222's): MB of distinct tiles a pass touches (A 2 MB, B 1 MB, C 2 MB a block)"""
    return 2.0 * MB * KB + NB * KB + 2.0 * MB * NB


def hkey(*parts):
    """the draw order: sha256 of the joined parts (no forecast, no measurement): a fixed pseudo-random order"""
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()


def product_masks(n):
    """every shire mask of n shires that is a product of row groups (s >> 2, 8 of them) and column groups (s & 3, 4 of them) (E222's)"""
    out = []
    for nr in range(1, 9):
        if n % nr or n // nr > 4:
            continue
        for R in itertools.combinations(range(8), nr):
            for Cc in itertools.combinations(range(4), n // nr):
                out.append(("0x%x" % sum(1 << (4 * r + c) for r in R for c in Cc), nr, n // nr))
    return out


def region_ok(region, MB, NB, KB, x1, x2):
    d = footprint(MB, NB, KB)
    if region in ("L2", "G-L2"):
        return KB <= 2 and d < x1
    if region in ("L3", "G-L3"):
        return KB >= 3 and d < 0.85 * x1
    if region == "x1-below":
        return 0.85 * x1 <= d < x1
    if region == "x1-above":
        return x1 < d <= 1.15 * x1
    if region in ("mid", "G-mid"):
        return KB >= 2 and 1.15 * x1 < d < 0.85 * x2
    if region == "x2-below":
        return 0.85 * x2 <= d < x2
    if region == "x2-above":
        return x2 < d <= 1.15 * x2
    if region == "beyond":
        return d > 1.15 * x2
    if region == "subset":
        return KB >= 2 and d < 0.85 * x2
    if region == "P":
        return KB >= 2 and d < 0.85 * x2
    raise SystemExit(f"point_rule_e224: unknown region {region}")


class Mock:
    """deterministic stand-in numbers for the control flow's own desk test (never a registered output)"""

    def __init__(self, MZ):
        self.MZ = MZ
        self.P32 = json.load(open(os.path.join(REPO, "tools", "matmul", "mm1", "v3.2", "out", "mm1_v32_params.json")))
        self.eps_g = 0.0843
        self.rest = {"A": {"W": 31.76}, "B": {"W": 23.19}}
        self.PS_made = {}
        self.l3s_extra = {}
        self.e217 = {"mock": True}

    def _num(self, *a):
        return int(hashlib.sha256("|".join(map(str, a)).encode()).hexdigest()[:8], 16) / 2.0 ** 32

    def forecast(self, pts, f=600.0, card=C1, models=("MM1-v3.2",), cands=True, which=("posimb", "af4", "l3s")):
        out = {}
        for p in pts:
            u = self._num(p["arm"], p["fmt"], p.get("kind"), p["mask"], f, card)
            T = 1.0 + 3.0 * u
            W = 5.0 + 35.0 * self._num(p["arm"], p["fmt"], p.get("kind"))
            base = {"T_op_us": T, "cycles_per_op_wall": T * f, "cycles_per_op_mean": T * f * 0.98, "seconds_per_gemm": 0.01 + 0.2 * u,
                    "W_over_idle": W, "A_W": W * 0.5, "B_W_us": W * 0.5 * T, "J_over_idle_per_gemm": W * (0.01 + 0.2 * u),
                    "Q_mean": [[0.4, 0.1, 0.0], [0.2, 0.2, 0.0], [0.05, 0.05, 0.0]], "rest_law_W": 30.0}
            o = {m: dict(base) for m in models}
            if cands:
                sh = [int(v) for v in re.findall(r"\d+", p["arm"])[:3]]
                quiet = p["arm"].startswith("gemmL") and not p["arm"].startswith("gemmLn") and p["mask"] == FULLM and sh[2] >= 3 and \
                    footprint(*sh) <= 30.0
                for n in self.MZ.CANDS + (self.MZ.COMBO,) + self.MZ.PAIRS:
                    x = dict(base)
                    if not quiet:
                        x["cycles_per_op_wall"] *= 1.0 + 0.02 * (self._num(n, p["arm"], p["mask"]) - 0.5)
                        x["W_over_idle"] *= 1.0 + 0.05 * (self._num(n, p["arm"]) - 0.5)
                    x["T_op_us"] = x["cycles_per_op_wall"] / f
                    x["in_scope"] = True
                    x["term"] = {"term_AF4_W": 0.1 * W * self._num(n, "af4", p["arm"]), "MM1-v3.2_F3_W": 0.0,
                                 "features": {"R4": 0.0}, "g_wall": 1.0}
                    o[n] = x
            out[p["id"]] = o
        return out

    def planning_peak(self, arm, fc, token):
        x = fc.get("MM1-v3.2")
        w = x["W_over_idle"] * ((1.0 + 2.0 * self.eps_g) if token.startswith("gemmLnc") else 1.0)
        return w + self.rest[arm]["W"] + 2.0, w + self.rest[arm]["W"] + 2.5, "mock"

    def save_l3s_extra(self):
        pass


class Rule:
    def __init__(self, scan_path, e220_csv, e222_csv, out, mock=False):
        self.S = json.load(open(scan_path))
        self.scan_sha = sha(scan_path)
        self.NV = {a: NRZ.Never(self.S, CARD[a]) for a in ("A", "B")}
        for pth, want, what in ((e220_csv, E220_POINTS_CSV_SHA, "E220's POINTS-e220.csv"), (e222_csv, E222_POINTS_CSV_SHA, "E222's POINTS-e222.csv")):
            if sha(pth) != want:
                print(f"point_rule_e224: REFUSED, {pth} is not {what} {want}")
                sys.exit(4)
        self.e220_csv, self.e222_csv = e220_csv, e222_csv
        import models_e224 as MZ  # noqa: E402
        self.MZ = MZ
        self.mock = mock
        self.M = Mock(MZ) if mock else MZ.Models()
        self.P = load("points_e215_pinned", self.pinned(*E215_POINTS_PY))
        self._tiles_orig = self.P.tiles_of
        th = self.M.P32["time"]["theta"]
        self.x1, self.w1, self.x2, self.w2, self.pB = th["x1"], th["w1"], th["x2"], th["w2"], th["pB"]
        self.out = out
        self.cands = {}
        self.cache = {}
        self.line = {a: STOP[a] - DROP_MARGIN_W for a in ("A", "B")}
        self.avoid, self.avoid_src = self.avoid_list()

    @staticmethod
    def pinned(rel, want):
        p = os.path.join(REPO, rel)
        if want is not None and sha(p) != want:
            print(f"point_rule_e224: REFUSED, {rel} is {sha(p)}, pinned {want}")
            sys.exit(4)
        return p

    # ---------------------------------------------------------------- THE AVOID LIST: every shape E220, E221 or E222 registered or scheduled
    def avoid_list(self):
        files = {}
        for rel, want in AVOID_FILES.items():
            files[rel] = self.pinned(rel, want)
        files["OUT/reg-e220/POINTS-e220.csv"] = self.e220_csv
        files["OUT/reg-e222/POINTS-e222.csv"] = self.e222_csv
        w = os.path.normpath(os.path.join(os.path.dirname(self.e222_csv), ".."))
        for name, rel, want in (("OUT/reg-e220/POINTS.txt", os.path.join(w, "reg-e220", "POINTS.txt"), E220_POINTS_TXT_SHA),
                                ("OUT/reg-e222/POINTS.txt", os.path.join(w, "reg-e222", "POINTS.txt"), E222_POINTS_TXT_SHA)):
            if sha(rel) != want:
                print(f"point_rule_e224: REFUSED, {rel} is not {want}")
                sys.exit(4)
            files[name] = rel
        p222 = os.path.join(w, "reg-e222", "frozen", "points-e222.json")
        if sha(p222) != E222_POINTS_JSON[1]:
            print(f"point_rule_e224: REFUSED, {p222} is not E222's frozen points-e222.json")
            sys.exit(4)
        files["OUT/reg-e222/frozen/points-e222.json"] = p222
        shapes, src = set(), {}
        for name, p in files.items():
            txt = open(p, encoding="utf-8", errors="ignore").read()
            for m in itertools.chain(SHAPE_RX.finditer(txt), ARMNAME_RX.finditer(txt)):
                s = tuple(int(x) for x in m.groups()[:3])
                shapes.add(s)
                src.setdefault("%dx%dx%d" % s, set()).add(name)
        rec = {"files_sha256": {k: sha(v) for k, v in files.items()}, "n_shapes": len(shapes),
               "shapes": {k: sorted(v) for k, v in sorted(src.items())}}
        self.cands["avoid"] = {"n_shapes": len(shapes), "files_sha256": rec["files_sha256"]}
        self.avoid_rec = rec
        return shapes, src

    # ---------------------------------------------------------------- forecasts, cached
    def fc(self, arm, items, f=None, models=("MM1-v3.2",), cands=False, which=("posimb", "af4", "l3s")):
        f = F_REG[arm] if f is None else f
        mk = (arm, f, "|".join(models), cands, ",".join(which))
        need, seen = [], set()
        for it in items:
            k = (it["arm"], it["fmt"], it.get("kind", "random"), it["mask"])
            if (k, mk) not in self.cache and k not in seen:
                need.append(it)
                seen.add(k)
        if need:
            pts = [{"id": "|".join([it["arm"], it["fmt"], it.get("kind", "random"), it["mask"]]), "arm": it["arm"], "fmt": it["fmt"],
                    "kind": it.get("kind", "random"), "mask": it["mask"]} for it in need]
            got = self.M.forecast(pts, f=f, card=CARD[arm], models=models, cands=cands, which=which)
            for p in pts:
                self.cache[((p["arm"], p["fmt"], p["kind"], p["mask"]), mk)] = got[p["id"]]
        return [self.cache[((it["arm"], it["fmt"], it.get("kind", "random"), it["mask"]), mk)] for it in items]

    def pp(self, arm, token, fmt, kind, mask):
        x = self.fc(arm, [{"arm": token, "fmt": fmt, "kind": kind, "mask": mask}])[0]
        pp32, ppall, by = self.M.planning_peak(arm, x, token)
        return pp32, ppall, x

    def sec_ok(self, token, fmt, kind, mask):
        """MM1-v3.2's seconds a GEMM at 600 MHz (arm A's clock; arm B's slowest column: MM1-v3.2's time has no per-card term)"""
        x = self.fc("A", [{"arm": token, "fmt": fmt, "kind": kind, "mask": mask}])[0]["MM1-v3.2"]
        s = x.get("seconds_per_gemm")
        return (s is not None and s <= SEC_CAP_S), s

    def never(self, arm, token):
        return self.NV[arm].token(token)[0]

    def never_both(self, token):
        return self.never("A", token) and self.never("B", token)

    def priced(self, arm, token, fmt, kind, mask):
        x = self.fc(arm, [{"arm": token, "fmt": fmt, "kind": kind, "mask": mask}])[0]["MM1-v3.2"]
        return x is not None and x.get("W_over_idle") is not None

    def common(self, arms, shp, token, fmt, kind, mask, used):
        """the checks every point passes: (1) the shape not avoided, (2) not used, (3) never ran (token reading, session records), (4) priced
        by MM1-v3.2 in energy, (5) MM1-v3.2's seconds a GEMM within the cap, (6) PP32 under each arm's drop line -> (ok, why, PP by arm)"""
        if shp in self.avoid:
            return False, "the shape is named by E220, E221 or E222 (avoided)", None
        for a in arms:
            if shp in used[a]:
                return False, f"shape already in E224 (arm {a})", None
        for a in arms:
            if not self.never(a, token):
                return False, f"ran on {CARD[a]} (token reading, session records)", None
        for a in arms:
            if not self.priced(a, token, fmt, kind, mask):
                return False, f"MM1-v3.2 does not price its energy on arm {a} (NOT FORECAST)", None
        ok, s = self.sec_ok(token, fmt, kind, mask)
        if not ok:
            return False, f"MM1-v3.2's seconds a GEMM {s} over the {SEC_CAP_S} s cap", None
        pps = {}
        for a in arms:
            pp32, ppall, _ = self.pp(a, token, fmt, kind, mask)
            pps[a] = (pp32, ppall)
            if pp32 is None or pp32 >= self.line[a]:
                return False, f"planning peak {pp32} on arm {a} within 3 W of its stop", pps
        return True, "", pps

    # ---------------------------------------------------------------- FAMILY L, subfamily L3S: the L3 edges (E222's L3b form, both cards)
    def family_l3s(self, used):
        picked, recs, short = [], {}, 0
        for sub in ("L3S-1", "L3S-2"):
            cfg = L3S_SUBS[sub]
            lo, hi = (cfg["d_x1"][0] * self.x1, cfg["d_x1"][1] * self.x1) if "d_x1" in cfg else cfg["d"]
            cs = []
            for MB in GRID["MB"]:
                for NB in cfg["NB"]:
                    for KB in GRID["KB"]:
                        d = footprint(MB, NB, KB)
                        if not ((lo < d <= hi) if sub == "L3S-2" else (lo <= d <= hi)):
                            continue
                        t = tok("gemmL", MB, NB, KB)
                        cs.append({"sub": sub, "token": t, "shape": [MB, NB, KB], "d_MB": d, "side": ("below" if d < self.x1 else "above"),
                                   "string": f"{t}|fp32|{FULLM}"})
            live = [c for c in cs if tuple(c["shape"]) not in self.avoid and self.never_both(c["token"]) and
                    tuple(c["shape"]) not in used["A"] and tuple(c["shape"]) not in used["B"]]
            fcs = self.fc("A", [{"arm": c["token"], "fmt": "fp32", "mask": FULLM} for c in live], cands=True, which=("l3s",))
            for c, f in zip(live, fcs):
                c["T_v32_us"], c["T_L3S_us"] = f["MM1-v3.2"]["T_op_us"], f[self.MZ.L3S]["T_op_us"]
                c["delta_ln"] = math.log(c["T_L3S_us"] / c["T_v32_us"])
                c["score"] = -abs(c["delta_ln"])
            for c in cs:
                c.setdefault("score", None)
            cs.sort(key=lambda c: ((c["score"] if c["score"] is not None else 1e9), c["string"]))
            chosen, nbs = [], set()
            quota, min_side = cfg["quota"] + (short if sub == "L3S-2" else 0), cfg.get("min_side", 0)
            for c in cs:
                if len(chosen) >= quota:
                    c["verdict"] = "not reached (quota full)"
                    continue
                if c["score"] is None:
                    c["verdict"] = "avoided, used, or ran on a card (token reading, session records)"
                    continue
                if any(abs(c["d_MB"] - x["d_MB"]) < 1e-9 for x in chosen):
                    c["verdict"] = "footprint already drawn in this subfamily"
                    continue
                if sub == "L3S-2" and c["shape"][1] in nbs:
                    c["verdict"] = "NB already drawn in L3S-2"
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
                ok, why, pps = self.common(("A", "B"), tuple(c["shape"]), c["token"], "fp32", "random", FULLM, used)
                if not ok:
                    c["verdict"] = why
                    continue
                c["PP32_W"] = {a: pps[a][0] for a in pps}
                c["PP_all_W"] = {a: pps[a][1] for a in pps}
                c["verdict"] = "drawn"
                chosen.append(c)
                nbs.add(c["shape"][1])
                for a in ("A", "B"):
                    used[a].add(tuple(c["shape"]))
            recs[sub] = [c for c in cs if c.get("verdict") not in (None, "not reached (quota full)") or c in chosen][:300]
            picked += chosen
            if sub == "L3S-1":
                short = quota - len(chosen)        # L3S-1's unfilled quota passes to L3S-2
        self.cands["L-L3S"] = recs
        out = []
        for n, c in enumerate(picked, 1):
            src = {"L3S-1": (f"NB 1-2 around the first L3 edge x1 = {self.x1:.2f} MB (0.8-1.3 x1; gemmL2x1x7's family), ranked by "
                             f"|ln(T_L3S / T_v32)| descending"),
                   "L3S-2": "the set-overflow band (32, 48] MB at NB >= 3, ranked by |ln(T_L3S / T_v32)| descending"}[c["sub"]]
            out.append({"id": f"e{n:02d}", "family": "L", "subfamily": c["sub"], "lead": "L3S", "source": src, "token": c["token"], "fmt": "fp32",
                        "kind": "random", "mask": FULLM, "footprint_MB": c["d_MB"], "edge_side": c["side"], "PP32_W": c["PP32_W"],
                        "PP_all_W": c["PP_all_W"], "rule_delta_ln_L3S_vs_v32": c["delta_ln"], "neverrun_tokens": [c["token"]]})
        return out

    # ---------------------------------------------------------------- FAMILY L, subfamily posimb: equal-count layout pairs (E222's Y3 form)
    def family_posimb(self, used):
        masks = product_masks(2)
        out, recs, mask_used = [], [], set()
        for pid, src, what in POS_SOURCES:
            m0 = self.P.parse_arm(src)[1]
            shapes = []
            for MB in POS_GRID["MB"]:
                for NB in POS_GRID["NB"]:
                    for KB in POS_GRID["KB"]:
                        dist = abs(math.log2(MB / m0[0])) + abs(math.log2(NB / m0[1])) + abs(math.log2(KB / m0[2]))
                        shapes.append((dist, f"{tok('gemmL', MB, NB, KB)}|fp32|{FULLM}", (MB, NB, KB)))
            shapes.sort()
            tried, pick = [], None
            for dist, s, shp in shapes:
                t = tok("gemmL", *shp)
                if shp in self.avoid:
                    tried.append({"token": t, "dist": dist, "verdict": "the shape is named by E220, E221 or E222 (avoided)"})
                    continue
                if shp in used["A"] or shp in used["B"]:
                    tried.append({"token": t, "dist": dist, "verdict": "shape already in E224"})
                    continue
                if not self.never_both(t):
                    tried.append({"token": t, "dist": dist, "verdict": "ran on an E224 card (token reading, session records)"})
                    continue
                avail = [x for x in masks if x[0] not in mask_used]
                fcs = self.fc("A", [{"arm": t, "fmt": "fp32", "mask": m} for m, _, _ in avail], cands=True, which=("posimb",))
                g = {m: (f[self.MZ.POSIMB]["cycles_per_op_wall"], f["MM1-v3.2"]["cycles_per_op_wall"], f) for (m, _, _), f in zip(avail, fcs)}
                ranked = []
                for (ma, ra, ca), (mb, rb, cb) in itertools.combinations(avail, 2):
                    dpos = math.log(g[ma][0] / g[mb][0])
                    d32 = math.log(g[ma][1] / g[mb][1])
                    sep = abs(dpos - d32)
                    a_, b_ = (ma, mb) if dpos >= 0 else (mb, ma)
                    ranked.append((-sep, f"{a_}|{b_}", a_, b_, abs(dpos), abs(d32)))
                ranked.sort()
                got = None
                for _, s2, ma, mb, sep, d32 in ranked[:40]:
                    oka, wa, pa = self.common(("A", "B"), shp, t, "fp32", "random", ma, {"A": set(), "B": set()})
                    okb, wb, pb = self.common(("A", "B"), shp, t, "fp32", "random", mb, {"A": set(), "B": set()})
                    if oka and okb:
                        got = (ma, mb, sep, d32, pa, pb)
                        break
                if got is None:
                    tried.append({"token": t, "dist": dist, "verdict": "no mask pair passes the checks at this shape"})
                    continue
                ma, mb, sep, d32, pa, pb = got
                pick = (t, shp, dist, ma, mb, sep, d32, pa, pb, g[ma][2][self.MZ.POSIMB]["term"], g[mb][2][self.MZ.POSIMB]["term"])
                tried.append({"token": t, "dist": dist, "verdict": "drawn", "pair": [ma, mb], "posimb_ln_a_over_b": sep, "v32_ln_a_over_b": d32})
                break
            recs.append({"pair": pid, "source": src, "what": what, "tried": tried[:60], "n_tried": len(tried)})
            if pick is None:
                continue
            t, shp, dist, ma, mb, sep, d32, pa, pb, ta, tb = pick
            for a in ("A", "B"):
                used[a].add(shp)
            mask_used.update((ma, mb))
            for role, m, pk, term in (("a", ma, pa, ta), ("b", mb, pb, tb)):
                out.append({"id": f"{pid}{role}", "family": "L", "subfamily": "posimb-pair", "lead": "posimb",
                            "source": (f"{what}'s shape neighbourhood ({src}, distance {dist:.3f} in log2 units); the 2-shire product-mask pair with "
                                       f"the largest posimb separation |ln(T_a / T_b)| = {sep:.4f} (MM1-v3.2 {d32:+.1e})"),
                            "token": t, "fmt": "fp32", "kind": "random", "mask": m, "pair": pid, "pair_role": role,
                            "PP32_W": {a: pk[a][0] for a in pk}, "PP_all_W": {a: pk[a][1] for a in pk}, "rule_posimb_g_wall": term.get("g_wall"),
                            "neverrun_tokens": [t]})
        self.cands["L-posimb"] = {"masks": len(masks), "pairs": recs}
        return out

    # ---------------------------------------------------------------- FAMILY L, subfamily AF4: gemmLnc at small predicted excess, with twins
    def family_af4(self, used):
        items = []
        for fmt in ("fp32", "int8"):
            for MB in AF4_MB:
                for NB in AF4_NB:
                    for KB in AF4_KB:
                        items.append({"arm": tok("gemmLnc", MB, NB, KB), "fmt": fmt, "mask": FULLM, "shape": (MB, NB, KB)})
        live0 = [it for it in items if it["shape"] not in self.avoid and it["shape"] not in used["A"] and it["shape"] not in used["B"]
                 and self.never_both(it["arm"]) and self.never_both(tok("gemmL", *it["shape"]))]
        f32 = self.fc("A", live0)
        pre = []
        for it, f in zip(live0, f32):
            x = f["MM1-v3.2"]
            if x.get("W_over_idle") is None:
                continue
            beyond = self.MZ.beyond_of(x["Q_mean"]) if not self.mock else 3.0 * (it["shape"][2] > 2)
            NB = it["shape"][1]
            reg = "L2" if beyond < 2.6 else ("NB56" if NB in (5, 6) else None)
            if reg is None or (it["fmt"] == "int8" and reg != "L2"):
                continue
            pre.append((it, reg, beyond))
        fca = self.fc("A", [p[0] for p in pre], cands=True, which=("af4",))
        cands = []
        for (it, reg, beyond), f in zip(pre, fca):
            a = f[self.MZ.AF4]
            share = a["term"]["term_AF4_W"] / a["W_over_idle"]
            cands.append({"token": it["arm"], "fmt": it["fmt"], "shape": list(it["shape"]), "regime": reg, "beyond": beyond,
                          "R4": a["term"]["features"]["R4"], "AF4_W": a["term"]["term_AF4_W"], "F3_W": a["term"]["MM1-v3.2_F3_W"],
                          "W_af4": a["W_over_idle"], "W_v32": f["MM1-v3.2"]["W_over_idle"], "score_share": share,
                          "string": f"{it['arm']}|{it['fmt']}|{FULLM}"})
        by = {r: sorted([c for c in cands if c["regime"] == r], key=lambda c: (c["score_share"], c["string"])) for r in ("L2", "NB56")}
        quota = dict(AF4_QUOTA)
        drawn, nbkb = [], set()
        for reg in ("L2", "NB56"):
            n_have = 0
            for c in by[reg]:
                if n_have >= quota[reg]:
                    break
                shp = tuple(c["shape"])
                if shp in used["A"] or shp in used["B"]:
                    c["verdict"] = "shape already in E224"
                    continue
                if (shp[1], shp[2]) in nbkb:
                    c["verdict"] = "(NB, KB) already drawn in L-AF4"
                    continue
                okg, wg, pg = self.common(("A", "B"), shp, c["token"], c["fmt"], "random", FULLM, {"A": set(), "B": set()})
                okt, wt, pt = self.common(("A", "B"), shp, tok("gemmL", *shp), c["fmt"], "random", FULLM, {"A": set(), "B": set()})
                if not (okg and okt):
                    c["verdict"] = "the point or its twin: " + (wg or wt)
                    continue
                c["PP32_W"], c["PP_all_W"] = {a: pg[a][0] for a in pg}, {a: pg[a][1] for a in pg}
                c["twin_PP32_W"], c["twin_PP_all_W"] = {a: pt[a][0] for a in pt}, {a: pt[a][1] for a in pt}
                c["verdict"] = "drawn"
                drawn.append(c)
                for a in ("A", "B"):
                    used[a].add(shp)
                nbkb.add((shp[1], shp[2]))
                n_have += 1
            if reg == "L2" and n_have < quota["L2"]:
                quota["NB56"] += quota["L2"] - n_have
        self.cands["L-AF4"] = {"live_both_tokens_never_run": len(live0), "regime_counts": {r: len(v) for r, v in by.items()},
                               "quota_after_pass_on": quota, "walked": {r: [c for c in v if "verdict" in c][:200] for r, v in by.items()}}
        out = []
        for n, c in enumerate(drawn, 1):
            shp = tuple(c["shape"])
            out.append({"id": f"g{n:02d}", "family": "L", "subfamily": f"AF4-{c['regime']}", "lead": "AF4",
                        "source": (f"rgm136 gemmLnc, regime {c['regime']} (beyond {c['beyond']:.3f}, R4 {c['R4']:.3f}), AF4's predicted excess share "
                                   f"of its W over idle {c['score_share']:.4f} (ascending: small predicted excess)"), "token": c["token"], "fmt": c["fmt"],
                        "kind": "random", "mask": FULLM, "twin": f"g{n:02d}t", "PP32_W": c["PP32_W"], "PP_all_W": c["PP_all_W"],
                        "neverrun_tokens": [c["token"], tok("gemmL", *shp)]})
            out.append({"id": f"g{n:02d}t", "family": "L", "subfamily": f"AF4t-{c['regime']}", "lead": "AF4", "source": f"the cooperative twin of g{n:02d}",
                        "token": tok("gemmL", *shp), "fmt": c["fmt"], "kind": "random", "mask": FULLM, "twin_of": f"g{n:02d}",
                        "PP32_W": c["twin_PP32_W"], "PP_all_W": c["twin_PP_all_W"], "neverrun_tokens": [tok("gemmL", *shp), c["token"]]})
        return out

    # ---------------------------------------------------------------- FAMILY P: operand patterns with counted switches, zeros and random twins
    def null_ln(self, f_by_kind, kind):
        """|ln(W_counts / W_null)| at MM1-v3.2's own op time: W_null the mean over zeros, ones and random of MM1-v3.2's W at the configuration"""
        wn = sum(f_by_kind[k]["MM1-v3.2"]["W_over_idle"] for k in ("zeros", "ones", "random")) / 3.0
        w = f_by_kind[kind]["MM1-v3.2"]["W_over_idle"]
        return abs(math.log(w / wn)), w, wn

    def no_term_acts(self, arm, token, fmt, kinds):
        fcs = self.fc(arm, [{"arm": token, "fmt": fmt, "kind": k, "mask": FULLM} for k in kinds], cands=True)
        for k, f in zip(kinds, fcs):
            b = f["MM1-v3.2"]
            for n in self.MZ.CANDS + (self.MZ.COMBO,) + self.MZ.PAIRS:
                if n not in f or not self.MZ._close(f[n], b):
                    return False, f"{n} differs from MM1-v3.2 at {token} {fmt} {k} on arm {arm}"
        return True, ""

    def family_p(self, used):
        out, recs, kinds_used = [], [], set()
        for sid, fmt in P_SLOTS:
            cs = []
            for MB in GRID["MB"]:
                for NB in GRID["NB"]:
                    for KB in GRID["KB"]:
                        if not region_ok("P", MB, NB, KB, self.x1, self.x2):
                            continue
                        t = tok("gemmL", MB, NB, KB)
                        cs.append((hkey("E224", "P", sid, t, fmt), t, (MB, NB, KB)))
            cs.sort()
            tried, pick = [], None
            for _, t, shp in cs:
                if len(tried) >= 400:
                    break
                ok, why, _ = self.common(("A", "B"), shp, t, fmt, "random", FULLM, used)
                if not ok:
                    tried.append({"token": t, "verdict": why})
                    continue
                pool212 = [f"pattern:{k}" for k in E212_KINDS[fmt] if (fmt, k) not in kinds_used]
                pool217 = [f"pattern:{k}" for k in E217_KINDS[fmt] if (fmt, k) not in kinds_used]
                fa = dict(zip(["zeros", "ones", "random"] + pool212 + pool217,
                              self.fc("A", [{"arm": t, "fmt": fmt, "kind": k, "mask": FULLM} for k in ["zeros", "ones", "random"] + pool212 + pool217])))
                if any(fa[k]["MM1-v3.2"].get("W_over_idle") is None for k in ("zeros", "ones", "random")):
                    tried.append({"token": t, "verdict": "MM1-v3.2 does not price zeros, ones and random here"})
                    continue
                score = []
                for k in pool212 + pool217:
                    if fa[k]["MM1-v3.2"].get("W_over_idle") is None:
                        continue
                    s, w, wn = self.null_ln(fa, k)
                    if w < 3.0:
                        continue
                    score.append((-s, k, "E212" if k[8:] in E212_KINDS[fmt] else "E217", w, wn))
                score.sort()
                k212 = next((x for x in score if x[2] == "E212"), None)
                k217 = next((x for x in score if x[2] == "E217"), None)
                if k217 is None:
                    k217 = next((x for x in score if x[2] == "E212" and x is not k212), None)
                if k212 is None or k217 is None:
                    tried.append({"token": t, "verdict": "fewer than two pattern kinds priced at 3 W or more"})
                    continue
                kinds = ["random", "zeros", k212[1], k217[1]]
                bad = None
                for a in ("A", "B"):
                    for k in kinds:
                        if not self.priced(a, t, fmt, k, FULLM):
                            bad = f"{k} not priced on arm {a}"
                            break
                        pp32, ppall, _ = self.pp(a, t, fmt, k, FULLM)
                        if pp32 is None or pp32 >= self.line[a]:
                            bad = f"{k}: planning peak {pp32} on arm {a} within 3 W of its stop"
                            break
                    if bad:
                        break
                if bad:
                    tried.append({"token": t, "verdict": bad})
                    continue
                acts = {a: self.no_term_acts(a, t, fmt, kinds) for a in ("A", "B")}
                pick = (t, shp, kinds, k212, k217)
                tried.append({"token": t, "verdict": "drawn", "kinds": kinds, "scores": [list(x) for x in score[:12]],
                              "no_term_acts_REPORTED": {a: {"none_acts": v[0], "first_difference": v[1]} for a, v in acts.items()}})
                break
            recs.append({"slot": sid, "fmt": fmt, "tried": tried[:80], "n_tried": len(tried)})
            if pick is None:
                continue
            t, shp, kinds, k212, k217 = pick
            for a in ("A", "B"):
                used[a].add(shp)
            kinds_used.update({(fmt, k212[1][8:]), (fmt, k217[1][8:])})
            for role, k in (("r", "random"), ("z", "zeros"), ("a", k212[1]), ("b", k217[1])):
                pps = {a: self.pp(a, t, fmt, k, FULLM)[:2] for a in ("A", "B")}
                srcs = {"r": "the random twin (E210's metric's R)", "z": "the zeros twin (the ungated base; E210's metric's Z)",
                        "a": f"an E212 operand pattern counted on the RTL bench (|ln(W / W_null)| {-k212[0]:.4f} by MM1-v3.2)",
                        "b": f"an {k217[2]} operand pattern counted on the RTL bench (|ln(W / W_null)| {-k217[0]:.4f} by MM1-v3.2)"}
                out.append({"id": f"{sid}{role}", "family": "P", "subfamily": f"P-{role}", "lead": "", "source": srcs[role], "token": t, "fmt": fmt,
                            "kind": k, "mask": FULLM, "pattern_shape": sid, "pattern_role": role, "time_scored": role == "r",
                            "PP32_W": {a: pps[a][0] for a in pps}, "PP_all_W": {a: pps[a][1] for a in pps}, "neverrun_tokens": [t],
                            "pattern_source": ("E212" if role == "a" else (k217[2] if role == "b" else ""))})
        self.cands["P"] = recs
        return out

    # ---------------------------------------------------------------- FAMILY D: the domain, per arm
    def family_d(self, arm, used):
        out, recs = [], []
        for sid, regions, fmt, kind, n in D_SLOTS:
            pre = "gemmLnc" if regions[0].startswith("G-") else "gemmL"
            cs = []
            masks = [FULLM] if n == 32 else [m for m, _, _ in product_masks(n)]
            for ri, region in enumerate(regions):
                part = []
                for MB in GRID["MB"]:
                    for NB in GRID["NB"]:
                        for KB in GRID["KB"]:
                            if not region_ok(region, MB, NB, KB, self.x1, self.x2):
                                continue
                            t = tok(pre, MB, NB, KB)
                            for m in masks:
                                part.append((hkey("E224", "D", sid, t, fmt, kind, m), t, (MB, NB, KB), m, region))
                part.sort()
                cs += part
            tried, pick = [], None
            region = regions[0]
            for _, t, shp, m, region in cs:
                if len(tried) >= 600:
                    break
                ok, why, pps = self.common((arm,), shp, t, fmt, kind, m, used)
                if not ok:
                    tried.append({"token": t, "mask": m, "verdict": why})
                    continue
                pick = (t, shp, m, pps, region)
                tried.append({"token": t, "mask": m, "region": region, "verdict": "drawn"})
                break
            recs.append({"slot": sid, "regions": list(regions), "fmt": fmt, "kind": kind, "shires": n, "n_candidates": len(cs), "tried": tried[-40:],
                         "n_tried": len(tried)})
            if pick is None:
                continue
            t, shp, m, pps, region = pick
            used[arm].add(shp)
            out.append({"id": sid, "family": "D", "subfamily": f"D-{region}", "lead": "", "source": (f"family D slot {sid}: region {region}, {fmt} "
                        f"{kind}, {n} shires; the first eligible candidate in the slot's fixed sha256 order"), "token": t, "fmt": fmt, "kind": kind,
                        "mask": m, "footprint_MB": footprint(*shp), "PP32_W": {arm: pps[arm][0]}, "PP_all_W": {arm: pps[arm][1]},
                        "neverrun_tokens": [t]})
        self.cands.setdefault("D", {})[arm] = recs
        return out

    # ---------------------------------------------------------------- the order and the card-time plan, per arm
    def order(self, arm, pts):
        gnc = [p for p in pts if p["token"].startswith("gemmLnc")]
        rest = [p for p in pts if not p["token"].startswith("gemmLnc")]
        p1 = sorted(p["id"] for p in rest)
        random.Random(f"E224|{arm}|pass1").shuffle(p1)
        fam = {p["id"]: p for p in pts}
        rep = {p["id"] for p in rest if p["family"] in ("L", "P") or p["subfamily"] == "D-subset"}
        p2 = [i for i in reversed(p1) if i in rep]
        gb = [p["id"] for p in sorted(gnc, key=lambda p: (p["PP32_W"][arm], p["id"]))]
        ga = [i for i in reversed(gb) if fam[i]["family"] == "L"]
        what, pace = PACE[arm]

        def build():
            runs = [("smoke", "s01"), ("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in p2] + \
                [("tie", "t01"), ("smoke", "s03")] + [("G block", i) for i in gb] + [("G block reversed (L-AF4 only)", i) for i in ga]
            n = sum(1 for b, _ in runs if b != "smoke")
            return runs, n, n * pace / 60.0
        runs, n_runs, card_min = build()
        thinned = []
        # THE THINNING RULE (stated before any forecast): over the target, pass 2's runs leave one at a time - family P's first, then D-subset's,
        # then family L's - the last in pass 2 first; no point leaves pass 1 by this rule
        while card_min > TARGET_MIN:
            order_out = [i for i in reversed(p2) if fam[i]["family"] == "P"] + [i for i in reversed(p2) if fam[i]["family"] == "D"] + \
                [i for i in reversed(p2) if fam[i]["family"] == "L"]
            if not order_out:
                break
            p2.remove(order_out[0])
            thinned.append(("pass2", order_out[0]))
            runs, n_runs, card_min = build()
        subset = 2 + len(p1)
        return {"pass1": p1, "pass2": p2, "G_block": gb, "G_block_reversed": ga, "runs": [{"n": k + 1, "block": b, "id": i} for k, (b, i) in enumerate(runs)],
                "n_runs_scored_and_ties": n_runs, "n_smoke": sum(1 for b, _ in runs if b == "smoke"), "pace_s_per_run": pace, "pace_source": what,
                "card_minutes_planned": card_min, "target_min": TARGET_MIN, "rule_min": RULE_MIN, "cap_min": CAP_MIN, "thinned": thinned,
                "registered_subset_if_cut": {"what": "the opening smoke, tie 1, pass 1 and tie 2 (every non-gemmLnc point once; the G block not reached)",
                                             "runs": subset, "card_minutes": subset * pace / 60.0}}

    def tiles_of(self, fmt, kind):
        name = kind.split(":", 1)[1] if kind.startswith("pattern:") else None
        if name and name in E217_KINDS.get(fmt, []):
            return "tiles", [f"{E217_TILES}/{fmt}/{name}.bin"]
        return self._tiles_orig(fmt, kind)

    def describe(self, arm, p):
        loop = "rgm136 gemmLnc" if p["token"].startswith("gemmLnc") else "rgm136 gemmL"
        self.P.tiles_of = self.tiles_of                     # E217's tiles beside E212's (points_e215.describe reads tiles_of from its module)
        try:
            d = self.P.describe(p["id"], arm, p["family"], "registered", p["token"], p["fmt"], p["kind"], p["mask"], loop, "point", p["source"],
                                CARD[arm])
        finally:
            self.P.tiles_of = self._tiles_orig
        d["f_mhz"] = F_REG[arm]
        d["time_scored"] = bool(p.get("time_scored", True))
        for k in ("subfamily", "lead", "source", "pair", "pair_role", "twin", "twin_of", "footprint_MB", "edge_side", "rule_delta_ln_L3S_vs_v32",
                  "rule_posimb_g_wall", "pattern_shape", "pattern_role", "pattern_source", "neverrun_tokens"):
            if k in p:
                d[k] = p[k]
        d["PP32_W"] = p["PP32_W"][arm]
        d["PP_all_W"] = p["PP_all_W"][arm]
        d["token"] = p["token"]
        d["footprint_MB_full_chip"] = footprint(*d["shape"])
        d["card"] = CARD[arm]
        d["arm_tag"] = arm
        return d

    def run(self):
        t0 = now()
        res = {"what": "E224's point rule applied (POINT-RULE-e224.md; desk/point_rule_e224.py)", "started": t0, "scan_sha256": self.scan_sha,
               "e220_points_csv_sha256": E220_POINTS_CSV_SHA, "e222_points_csv_sha256": E222_POINTS_CSV_SHA, "x1_MB": self.x1, "w1_MB": self.w1,
               "x2_MB": self.x2, "w2_MB": self.w2, "pB": self.pB, "eps_G": self.M.eps_g, "rest_law": self.M.rest, "cards": CARD, "f_mhz": F_REG,
               "stop_W": STOP, "drop_line_W": self.line, "seconds_cap_s": SEC_CAP_S, "mock": self.mock, "avoid_n_shapes": len(self.avoid)}
        used = {"A": set(), "B": set()}
        l3s = self.family_l3s(used)
        pos = self.family_posimb(used)
        af4 = self.family_af4(used)
        pp = self.family_p(used)
        shared = l3s + pos + af4 + pp
        res["points"], res["plan"] = {}, {}
        for arm in ("A", "B"):
            dd = self.family_d(arm, used)
            pts = shared + dd
            ids = [p["id"] for p in pts]
            assert len(ids) == len(set(ids)), "duplicate ids"
            res["plan"][arm] = self.order(arm, pts)
            res["points"][arm] = [self.describe(arm, p) for p in pts]
        res["counts"] = {arm: {f: sum(1 for p in res["points"][arm] if p["family"] == f) for f in ("D", "P", "L")} for arm in ("A", "B")}
        res["l_counts"] = {s: sum(1 for p in shared if p.get("lead") == s) for s in ("L3S", "posimb", "AF4")}
        res["d_shared_configurations"] = sorted({(p["token"], p["format"], p["kind"], p["shire_mask"]) for p in res["points"]["A"] if p["family"] == "D"} &
                                                {(p["token"], p["format"], p["kind"], p["shire_mask"]) for p in res["points"]["B"] if p["family"] == "D"})
        ex = {}
        for arm in ("A", "B"):
            ex[arm] = {}
            for i, t, f, k in (TIE,):
                pp32, ppall, _ = self.pp(arm, t, f, k, FULLM)
                ex[arm][i] = {"token": t, "fmt": f, "kind": k, "PP32_W": pp32, "PP_all_W": ppall}
            for sid, rows in SMOKE[arm].items():
                ex[arm][sid] = []
                for t, f, k in rows:
                    pp32, ppall, _ = self.pp(arm, t, f, k, FULLM)
                    ex[arm][sid].append({"token": t, "fmt": f, "kind": k, "PP32_W": pp32, "PP_all_W": ppall})
        res["extra_rows"] = ex
        res["highest_PP32"] = {arm: max(p["PP32_W"] for p in res["points"][arm]) for arm in ("A", "B")}
        res["ended"] = now()
        os.makedirs(os.path.join(self.out, "desk"), exist_ok=True)
        cpath = os.path.join(self.out, "desk", "candidates-e224.json")
        json.dump({"what": "every candidate of E224's point rule", "scan_sha256": self.scan_sha, "candidates": self.cands, "started": t0,
                   "ended": res["ended"]}, open(cpath, "w"), indent=1, sort_keys=True, default=str)
        res["candidates_sha256"] = sha(cpath)
        apath = os.path.join(self.out, "desk", "avoid-e224.json")
        json.dump(self.avoid_rec, open(apath, "w"), indent=1, sort_keys=True)
        res["avoid_sha256"] = sha(apath)
        if not self.mock:
            self.M.save_l3s_extra()
            fpath = os.path.join(self.out, "desk", "posimb-features-e224.json")
            json.dump(self.M.PS_made, open(fpath, "w"), indent=1, sort_keys=True)
            res["l3s_extra_sha256"] = sha(self.MZ.L3S_EXTRA)
            res["posimb_features_sha256"] = sha(fpath)
            res["e217_counts"] = self.M.e217
        ppath = os.path.join(self.out, "points-e224.json")
        json.dump(res, open(ppath, "w"), indent=1, sort_keys=True, default=str)
        cols = ["arm_tag", "id", "family", "subfamily", "lead", "pair", "pair_role", "twin", "twin_of", "pattern_shape", "pattern_role", "pattern_source",
                "loop", "kernel", "host", "elf", "token", "format", "kind", "shire_mask", "shires", "minions", "M", "N", "K", "M_computed",
                "N_computed", "ops_per_minion_per_gemm", "macs_per_gemm", "case", "time_scored", "footprint_MB_full_chip", "card", "f_mhz", "PP32_W",
                "PP_all_W", "values", "neverrun_tokens"]
        with open(os.path.join(self.out, "points-e224.csv"), "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(cols)
            for arm in ("A", "B"):
                for d in res["points"][arm]:
                    w.writerow([("+".join(d.get(c)) if c == "neverrun_tokens" else ("" if d.get(c) is None else d.get(c))) for c in cols])
        print(f"point rule: {t0} - {res['ended']} (mock {self.mock})")
        for arm in ("A", "B"):
            pl = res["plan"][arm]
            print(f"arm {arm}: counts {res['counts'][arm]}; highest PP32 {res['highest_PP32'][arm]:.2f} W (line {self.line[arm]:.0f} W); runs "
                  f"{pl['n_runs_scored_and_ties']} + {pl['n_smoke']} smoke, planned {pl['card_minutes_planned']:.1f} card-minutes; thinned {pl['thinned']}")
        print(f"L counts {res['l_counts']}; D configurations shared by both arms {len(res['d_shared_configurations'])}")
        print(f"points-e224.json {sha(ppath)}; points-e224.csv {sha(os.path.join(self.out, 'points-e224.csv'))}; candidates {res['candidates_sha256']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", required=True)
    ap.add_argument("--e220-points", required=True)
    ap.add_argument("--e222-points", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mock", action="store_true")
    a = ap.parse_args()
    Rule(a.scan, os.path.abspath(a.e220_points), os.path.abspath(a.e222_points), a.out, mock=a.mock).run()


if __name__ == "__main__":
    main()
