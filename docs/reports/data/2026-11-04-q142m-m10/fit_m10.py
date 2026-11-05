#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(m): M10, M9's frozen forms refitted on every committed 600 MHz kinds row (M9's 855 and pool 7's 104) with the five
candidate terms of tools/claims-v3/m10/REGISTRATION.md (committed e9367b66 before this file existed), each judged by its
registered entry rule on leave-one-kind-out errors; plus the heat and card-0 terms (c1, c2, d, e). Held out, not blind.

    python3 -B fit_m10.py [--out <dir>] [--counts-dir <dir>] [--skip-b]   # writes heldout-m10.json, m10.json, rows-m10.json, fit-output.txt

Everything fitted is re-derived inside each fold without the held-out kind: the prices, the card term (M9's C0) and, for term a,
every session's scale (two passes: pass 1 with every scale 1 reads the card term and the scales; pass 2 refits the prices on
D / s). The forms are M9's frozen ones; there is no inner choice of form. Standard library and numpy 1.26.
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M9D = os.path.join(DD, "2026-11-04-q140m-m9")
REG = os.path.join(ROOT, "tools", "claims-v3", "m10")
KD = os.path.join(ROOT, "tools", "claims-v3", "kinds")
B6, B7 = os.path.join(KD, "blind6"), os.path.join(KD, "blind7")
S7D = os.path.join(DD, "2026-11-04-q141t-s7-recount")
for p in (M9D, os.path.join(M9D, "recount-rule"), os.path.join(ROOT, "rtl-sim", "fma_toggle_v2")):
    if p not in sys.path:
        sys.path.insert(0, p)
import fit_m9 as M9  # noqa: E402  (imports fit_m8, fit_m7, fit_m6, m6_rows, fit_m5, reduce_footing unchanged)
import recount_rule as RR  # noqa: E402  (its functions only: points, prices, point_w, err)
import run_kinds as RK  # noqa: E402  (the bench's own mean_rows)

M8, M7, F, M6 = M9.M8, M9.M7, M9.F, M9.M6
load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
rms = lambda e: float(math.sqrt(np.nanmean(np.square(np.asarray(e, float))))) if np.sum(~np.isnan(np.asarray(e, float))) else float("nan")  # noqa: E731
SEED, NB = 142, 2000
CARD_TERM = "C0_M5_E78E82_family"
ANCHORS = ("fp32.randn", "fp16.randn", "int8.full", "fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full",
           "fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp16.anchor7_randn_a", "fp16.anchor7_randn_b",
           "int8.anchor7_full_a", "int8.anchor7_full_b")
S6 = ("fp32.b_onebit_b12_third", "fp32.b_onebit_b20_third", "fp32.a_onebit_b5_third", "fp32.a_onebit_b16_half", "fp16.b_onebit_b6_third")
S7 = ("fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh", "fp32.b_onebit_b22_third",
      "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi", "fp32.b_onebit_b20_third_a1p5")
TWINS = {"fp32.b_onebit_b12_third": "fp32.cal_third_b12", "fp32.b_onebit_b20_third": "fp32.cal_third_b20",
         "fp32.b_onebit_b20_pi": "fp32.cal_pi_b20"}
BOUND_W, NS = 0.10, (9, 27, 81, 243)
POOL_EXPS = ("E115", "E140", "E141", "E142", "E153", "E157", "E163", "E164")
FOOTING = {"E153": os.path.join(DD, "2026-11-03-e153-blind6-aifoundry3", "e153.json"),
           "E157": os.path.join(DD, "2026-11-03-e157-blind6-card1", "e157.json"),
           "E163": os.path.join(DD, "2026-11-04-e163-blind7-aifoundry3", "e163.json"),
           "E164": os.path.join(DD, "2026-11-04-e164-blind7-card1", "e164.json")}
fam_of = lambda t: "int8" if t == "int8" else "float"  # noqa: E731


def stop(msg):
    raise SystemExit("M10 STOPPED: " + msg)


# ------------------------------------------------------------------ inputs
def check_inputs():
    bad, n = [], 0
    for line in open(os.path.join(REG, "SHA256SUMS")):
        if line.strip():
            h, rel = line.split(None, 1)
            n += 1
            if fsha(os.path.join(ROOT, rel.strip())) != h:
                bad.append(rel.strip())
    if bad:
        stop("registered inputs changed: " + ", ".join(bad))
    return n


def footing_items(exp):
    p = FOOTING.get(exp) or os.path.join(DD, "2026-11-03-q139u-footing", "reduced", f"{exp.lower()}-footing.json")
    return load(p)["items"] if os.path.exists(p) else None


def chain_feats(crow, path, t, zeros, zr):
    """predict_blind7.py's feature chain on one counts row and tile, unchanged"""
    f = M7.feats_from_counts(crow, path, t, zeros)
    f8 = dict(f)
    f8.update(M8.m8_extra(path, t))
    M8.finish(f8)
    f9 = dict(f8)
    f9.update(M9.m9_extra(f8, t, crow, path, zr))
    return f9


def assemble():
    rows = load(os.path.join(M9D, "rows-m9.json"))
    for r in rows:
        r["src"] = "rows-m9.json"
    man7 = load(os.path.join(B7, "blind7.json"))["tiles"]
    f7 = load(os.path.join(B7, "predictions-blind7-aifoundry3.json"))["tiles"]
    missing = []
    for exp, card in (("E163", "a3"), ("E164", "c1")):
        items = load(FOOTING[exp])["items"]
        for meta in man7:
            if meta.get("anchor"):
                continue
            name, t = meta["name"], meta["type"]
            it = items.get(name)
            if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                missing.append(f"{exp}:{name}")
                continue
            p = os.path.join(B7, meta["file"])
            if fsha(p) != meta["sha256"]["whole"]:
                stop(f"{name} does not hash as blind7.json says")
            rows.append({"exp": exp, "card": card, "key": name, "type": t, "kind": f"{t}.blind7:{name.split('.', 1)[1]}",
                         "tile_sha256": meta["sha256"]["whole"], "tile_path": os.path.relpath(p, ROOT), "D": float(it["D"]["mean"]),
                         "D_se": it["D"].get("se"), "rate": float(it["rate"]["mean"]), "f": dict(f7[name]["features"]),
                         "dT_win": (it.get("dT_win") or {}).get("mean"), "case": meta.get("case"), "priority": meta.get("priority"),
                         "src": f"{os.path.relpath(FOOTING[exp], ROOT)} items.{name}"})
    for r in rows:
        r["sess"] = f"{r['exp']}|{r['card']}"
        r["S_class"] = r["key"] in S6 + S7 and r["exp"] in ("E153", "E157", "E163", "E164")
    return rows, missing


def assemble_anchors(rows, zeros, zr):
    """each session's random anchors (registration 3a): measured D and rate from its own footing reduction, features by tile"""
    feat = {}
    for r in rows:
        if r["exp"] == "E78" and r["key"] in ("fp32.randn", "fp16.randn", "int8.full"):
            feat[r["key"]] = (r["f"], r["kind"])
    man6 = {m["name"]: m for m in load(os.path.join(B6, "blind6.json"))["tiles"]}
    c6 = load(os.path.join(B6, "counts-blind6.json"))["rows"]
    p6 = load(os.path.join(B6, "predictions-blind6-aifoundry3.json"))["tiles"]
    chk = {}
    for n in ("fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full"):
        m = man6[n]
        path = os.path.join(B6, m["file"])
        f9 = chain_feats(c6[n], path, m["type"], zeros, zr)
        d = max(abs(float(f9[q]) - float(v)) for q, v in p6[n]["features"].items())
        chk[n] = d
        if d > 1e-9:
            stop(f"pool 6's {n}: the chain does not reproduce Q139(x)'s frozen features ({d})")
        feat[n] = (f9, None)
    f7 = load(os.path.join(B7, "predictions-blind7-aifoundry3.json"))["tiles"]
    for n in ANCHORS[6:]:
        feat[n] = (f7[n]["features"], None)
    out = {}
    for sess in sorted({r["sess"] for r in rows}):
        exp, card = sess.split("|")
        items = footing_items(exp)
        out[sess] = []
        if items is None:
            continue
        for n in ANCHORS:
            it = items.get(n)
            if not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                continue
            f, kind = feat[n]
            rate = it["rate"]["mean"] if isinstance(it.get("rate"), dict) and it["rate"].get("mean") else F.RATE[n.split(".")[0]]
            out[sess].append({"name": n, "type": n.split(".")[0], "D": float(it["D"]["mean"]), "rate": float(rate), "f": f, "kind": kind})
    return out, chk


def footing_consistency(rows):
    """each row's D equals its session's footing reduction's item D (the anchors' source is the rows' own footing)"""
    worst, n = 0.0, 0
    cache = {}
    for r in rows:
        if r["exp"] == "E147":
            continue
        it = cache.setdefault(r["exp"], footing_items(r["exp"]))
        if it is None or r["key"] not in it or not isinstance(it[r["key"]].get("D"), dict):
            continue
        worst = max(worst, abs(it[r["key"]]["D"]["mean"] - r["D"]))
        n += 1
    return {"rows_compared": n, "largest_abs_diff_w": worst}


# ------------------------------------------------------------------ term b: the S class at more launch points
def counts_points(paths, key):
    pts = {}
    for p in paths:
        if not os.path.exists(p):
            continue
        rows = load(p)["rows"]
        r = rows.get(key)
        if r is None:
            continue
        for q in r["points"]:
            if q.get("check_mismatch"):
                stop(f"{key} n0={q['n0']} check_mismatch in {p}")
            old = pts.get(q["n0"])
            if old is not None and json.dumps(old, sort_keys=True) != json.dumps(q, sort_keys=True):
                stop(f"{key} n0={q['n0']} counted twice with different records")
            pts[q["n0"]] = q
    return pts


def recount(counts_dir, zeros, zr):
    """per S tile: every committed point merged, e(N) by RECOUNT-RULE.md, N, and the N-point features through the chain"""
    pr = RR.prices()
    man = {m["name"]: (m, B6) for m in load(os.path.join(B6, "blind6.json"))["tiles"]}
    man.update({m["name"]: (m, B7) for m in load(os.path.join(B7, "blind7.json"))["tiles"]})
    cal = {m["name"]: m for m in load(os.path.join(M9D, "bench-check", "cal-tiles.json"))["tiles"]}
    calfiles = ([os.path.join(M9D, "bench-check", "counts-cal.json"), os.path.join(M9D, "recount-rule", "counts-pilot27.json")]
                + sorted(p for p in glob.glob(os.path.join(S7D, "step81", "counts-cal81-*.json")) if not p.endswith("-run.json"))
                + sorted(glob.glob(os.path.join(S7D, "step243", "counts-cal243-*-p[12].json"))))
    newfiles = sorted(glob.glob(os.path.join(counts_dir, "counts-m10-*.json")))
    newfiles = [p for p in newfiles if not p.endswith("-run.json")]
    out = {}
    for name in S6 + S7:
        m, d = man[name]
        t = m["type"]
        path = os.path.join(d, m["file"])
        base = os.path.join(d, "counts-blind6.json" if d == B6 else "counts-blind7.json")
        crow3 = load(base)["rows"][name]
        pts = counts_points([base] + ([os.path.join(S7D, "counts-s7-27.json")] if name in S7 else []) + newfiles, name)
        src = "pool counts + this lane's"
        if name in TWINS:
            c = cal[TWINS[name]]
            if c["sha256"] != m["sha256"]["whole"]:
                stop(f"{name}'s twin {TWINS[name]} does not hold the same bytes")
            tp = counts_points(calfiles, TWINS[name])
            for n0, q in tp.items():
                if n0 in pts and pts[n0]["vpu"]["nets_map"] != q["vpu"]["nets_map"]:
                    stop(f"{name} n0={n0}: the twin's count differs")
                pts.setdefault(n0, q)
            src = f"byte twin {TWINS[name]}'s committed counts"
        rec = {"type": t, "source": src, "by_N": {}}
        N = None
        for n in NS:
            pn = RR.points(n)
            if not all(p in pts for p in pn):
                break
            ws = [RR.point_w(pts[p], t, pr) for p in pn]
            e = RR.err(ws)
            rec["by_N"][str(n)] = {"e_w": e["e_w"], "mean_w": e["mean_w"], "met": e["e_w"] <= BOUND_W}
            N = n
            if e["e_w"] <= BOUND_W:
                break
        rec["N_counted"] = max((n for n in NS if all(p in pts for p in RR.points(n))), default=3)
        rec["N"] = N
        rec["met"] = bool(N and rec["by_N"][str(N)]["met"])
        rec["complete"] = bool(N and (rec["met"] or N == 243))
        if N:
            ws3 = [RR.point_w(pts[p], t, pr) for p in RR.points(3)]
            rec["three_point_minus_N_w"] = sum(ws3) / 3 - rec["by_N"][str(N)]["mean_w"]
            crowN = {"type": t, "kind": name.split(".", 1)[1], "points": [pts[p] for p in RR.points(3)],
                     "mean": RK.mean_rows([pts[p] for p in RR.points(N)])}
            f3 = chain_feats(crow3, path, t, zeros, zr)
            fN = chain_feats(crowN, path, t, zeros, zr)
            rec["f3"], rec["fN"] = f3, fN
        out[name] = rec
    return out


# ------------------------------------------------------------------ the fitter (fit_m7.Fam's equations, with session scales)
class Fit10:
    def __init__(self, rows, terms, anchors, use_scale, feats_override=None):
        self.rows, self.terms, self.use_scale = rows, terms, use_scale
        fo = feats_override or {}
        X = np.array([[r["rate"] * float(fo.get(i, r["f"])[q]) for q in terms] for i, r in enumerate(rows)], float)
        self.sc = np.where(np.abs(X).max(axis=0) == 0, 1.0, np.abs(X).max(axis=0))
        self.X = X / self.sc
        self.y = np.array([r["D"] for r in rows], float)
        self.c1 = np.array([r["card"] == "c1" for r in rows])
        self.tys = np.array([r["type"] for r in rows])
        self.kinds = sorted({r["kind"] for r in rows})
        ki = {k: i for i, k in enumerate(self.kinds)}
        self.kid = np.array([ki[r["kind"]] for r in rows])
        self.K, p = len(self.kinds), X.shape[1]
        self.sessions = sorted({r["sess"] for r in rows} | set(anchors))
        si = {s: i for i, s in enumerate(self.sessions)}
        self.sid = np.array([si[r["sess"]] for r in rows])
        self.S = len(self.sessions)
        self.sess_c1 = np.array([s.endswith("|c1") for s in self.sessions])
        self.G = np.zeros((self.K, p, p))
        np.add.at(self.G, self.kid, self.X[:, :, None] * self.X[:, None, :])
        self.Gt = self.G.sum(0)
        self.lam = 1e-9 * np.trace(self.Gt) / p
        xy = self.X * self.y[:, None]
        self.Hs = np.zeros((self.S, p))
        np.add.at(self.Hs, self.sid, xy)
        self.Hks = {}
        for i in range(len(rows)):
            key = (self.kid[i], self.sid[i])
            self.Hks[key] = self.Hks.get(key, 0.0) + xy[i]
        self.k_sess = {}
        for (k, s), v in self.Hks.items():
            self.k_sess.setdefault(k, []).append((s, v))
        # M9's card term C0: E78's and E82's same kinds, per format; a family value
        ex = np.array([r["exp"] for r in rows])
        fmts = sorted(set(self.tys))
        self.N = np.zeros(self.K)
        self.Dn = np.zeros(self.K)
        self.npair = np.zeros(self.K)
        for k in range(self.K):
            m = self.kid == k
            for f in fmts:
                a = self.y[m & (ex == "E78") & (self.tys == f)]
                b = self.y[m & (ex == "E82") & (self.tys == f)]
                if len(a) and len(b) and a.mean() > 0.5:
                    self.N[k] += a.mean() * b.mean()
                    self.Dn[k] += a.mean() ** 2
                    self.npair[k] += 1
        # anchors: (session index, scaled features, measured D, kind id of the tile if it is a row kind, else -1)
        self.anc = []
        for s, lst in anchors.items():
            for a in lst:
                xa = np.array([a["rate"] * float(a["f"][q]) for q in terms]) / self.sc
                self.anc.append((si[s], xa, a["D"], ki.get(a["kind"], -1) if a["kind"] else -1, a["name"]))

    def c0(self, k=None):
        N, Dn, C = self.N.sum(), self.Dn.sum(), self.npair.sum()
        if k is not None:
            N, Dn, C = N - self.N[k], Dn - self.Dn[k], C - self.npair[k]
        return N / Dn if C >= 3 else 1.0

    def solve(self, k, c, s):
        """prices with kind k left out (k None: all rows); card-1 rows' D / c, each session's D / s"""
        w = 1.0 / (np.where(self.sess_c1, c, 1.0) * s)
        h = (self.Hs * w[:, None]).sum(0)
        GG = self.Gt.copy()
        if k is not None:
            GG -= self.G[k]
            for si_, v in self.k_sess.get(k, []):
                h -= v * w[si_]
        return np.linalg.solve(GG + self.lam * np.eye(len(h)), h)

    def scales(self, b, c, k=None):
        rat = {}
        for si_, xa, D, ak, _ in self.anc:
            if k is not None and ak == k:
                continue
            dh = float(xa @ b) * (c if self.sess_c1[si_] else 1.0)
            if dh > 0:
                rat.setdefault(si_, []).append(D / dh)
        s = np.ones(self.S)
        for si_, v in rat.items():
            s[si_] = statistics.median(v)
        return s

    def fit(self, k=None):
        c = self.c0(k)
        b0 = self.solve(k, c, np.ones(self.S))
        if not self.use_scale:
            return {"c": c, "b0": b0, "b": b0, "s": np.ones(self.S)}
        s = self.scales(b0, c, k)
        return {"c": c, "b0": b0, "b": self.solve(k, c, s), "s": s}

    def pred(self, m, fit):
        return fit["s"][self.sid[m]] * np.where(self.c1[m], fit["c"], 1.0) * (self.X[m] @ fit["b"])

    def loko(self):
        err = np.full(len(self.y), np.nan)
        pred = np.full(len(self.y), np.nan)
        betas, scs, cs = np.zeros((self.K, self.X.shape[1])), np.zeros((self.K, self.S)), np.zeros(self.K)
        for k in range(self.K):
            fit = self.fit(k)
            m = self.kid == k
            pred[m] = self.pred(m, fit)
            err[m] = self.y[m] - pred[m]
            betas[k], scs[k], cs[k] = fit["b"], fit["s"], fit["c"]
        return err, pred, betas, scs, cs


def boot(kid, ea, eb, seed=SEED):
    r = M9.boot_diff(np.asarray(kid), np.asarray(ea, float), np.asarray(eb, float), n=NB, seed=seed)
    return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()} if r else None


def stat(e):
    e = np.asarray(e, float)
    e = e[~np.isnan(e)]
    return {"n": int(len(e)), "rms_w": round(rms(e), 5) if len(e) else None, "bias_meas_minus_pred_w": round(float(np.mean(e)), 5) if len(e) else None}


def split(rows, e, mask=None):
    e = np.asarray(e, float)
    sel = np.ones(len(rows), bool) if mask is None else mask
    out = {"all": stat(e[sel])}
    tys = np.array([r["type"] for r in rows])
    cds = np.array([r["card"] for r in rows])
    for c in ("a3", "c1"):
        out[f"card {c}"] = stat(e[sel & (cds == c)])
        for t in sorted(set(tys[sel])):
            out[f"{t}|{c}"] = stat(e[sel & (cds == c) & (tys == t)])
    for t in sorted(set(tys[sel])):
        out[t] = stat(e[sel & (tys == t)])
    return out


# ------------------------------------------------------------------ heat
HEAT_EXTRA = {"E141": "2026-11-02-e141-blind5-aifoundry3", "E142": "2026-11-02-e142-blind5-card1", "E153": "2026-11-03-e153-blind6-aifoundry3",
              "E157": "2026-11-03-e157-blind6-card1", "E163": "2026-11-04-e163-blind7-aifoundry3", "E164": "2026-11-04-e164-blind7-card1"}


def heat_c1(rows, log, dpred=None):
    """dpred: {(exp, key): M10's held-out D} for the end-to-end figure (S moved by predicted D - measured D, reported beside)"""
    dpred = dpred or {}
    M6.EXPDIR.update(HEAT_EXTRA)
    hr = M7.heat_rows(rows)
    for r in hr:
        r["sess"] = f"{r['exp']}|{r['card']}"
    cards = sorted({r["card"] for r in hr})
    terms = ["S|card", "ST|card"]
    X = M6.hX(hr, terms, cards)
    names = [f"S|{c}" for c in cards] + [f"ST|{c}" for c in cards]
    y = np.array([r["dT"] for r in hr])
    kinds = sorted({r["kind"] for r in hr})
    kid = np.array([kinds.index(r["kind"]) for r in hr])
    m7 = load(os.path.join(DD, "2026-11-02-q138m-model", "m7.json"))["heat"]
    frozen = X @ np.array([m7["coef"].get(n, 0.0) for n in names])
    anc = [i for i, r in enumerate(hr) if r["key"] in ANCHORS]
    sess = sorted({r["sess"] for r in hr})
    e_base, e_sess, e_e2e = (np.full(len(y), np.nan) for _ in range(3))
    hs_folds = {}
    for k in range(len(kinds)):
        m = kid != k
        b = np.linalg.lstsq(X[m], y[m], rcond=None)[0]
        law = X @ b
        rat = {}
        for i in anc:
            if kid[i] == k or law[i] <= 0:
                continue
            rat.setdefault(hr[i]["sess"], []).append(y[i] / law[i])
        h = {s: statistics.median(v) for s, v in rat.items()}
        mk = kid == k
        e_base[mk] = y[mk] - law[mk]
        e_sess[mk] = y[mk] - np.array([h.get(hr[i]["sess"], 1.0) for i in np.where(mk)[0]]) * law[mk]
        for i in np.where(mk)[0]:
            dp = dpred.get((hr[i]["exp"], hr[i]["key"]))
            if dp is not None and hr[i]["D"] is not None and hr[i]["S"] > 0:
                e_e2e[i] = y[i] - law[i] * (hr[i]["S"] - hr[i]["D"] + dp) / hr[i]["S"]
        hs_folds[k] = h
    b_all = np.linalg.lstsq(X, y, rcond=None)[0]
    law_all = X @ b_all
    rat = {}
    for i in anc:
        if law_all[i] > 0:
            rat.setdefault(hr[i]["sess"], []).append(y[i] / law_all[i])
    h_all = {s: statistics.median(v) for s, v in rat.items()}
    cds = np.array([r["card"] for r in hr])
    tys = np.array([r["type"] for r in hr])

    def sp(e):
        o = {"all": {"n": int(len(e)), "rms_c": round(rms(e), 4), "bias_c": round(float(np.mean(e)), 4)}}
        for c in cards:
            o[c] = {"n": int(np.sum(cds == c)), "rms_c": round(rms(e[cds == c]), 4), "bias_c": round(float(np.mean(e[cds == c])), 4)}
            for t in ("fp32", "fp16", "int8"):
                mm = (cds == c) & (tys == t)
                o[f"{t}|{c}"] = {"n": int(mm.sum()), "rms_c": round(rms(e[mm]), 4)} if mm.any() else None
        return o
    d = boot(kid, e_sess, e_base)
    per_card = {c: boot(kid[cds == c], e_sess[cds == c], e_base[cds == c]) for c in cards}
    rule = (d is not None and d["d_rms_w"] <= -0.010 and d["hi95"] < 0 and all(per_card[c]["d_rms_w"] < 0 for c in cards))
    log(f"  heat rows {len(hr)} ({len(kinds)} kinds, {len(sess)} sessions, {len(anc)} anchor rows)")
    return {"n_rows": len(hr), "n_kinds": len(kinds), "n_sessions": len(sess), "n_anchor_rows": len(anc),
            "rows_by_session": {s: int(sum(1 for r in hr if r["sess"] == s)) for s in sess},
            "M7_law_as_frozen": sp(y - frozen), "base_refit_loko": sp(e_base), "with_session_heat_scale_loko": sp(e_sess),
            "end_to_end_base_law_at_M10_heldout_D": (lambda m: {"n": int(m.sum()), "rms_c": round(rms(e_e2e[m]), 4),
                                                                "bias_c": round(float(np.mean(e_e2e[m])), 4),
                                                                "by_card": {c: round(rms(e_e2e[m & (cds == c)]), 4) for c in cards},
                                                                "base_law_on_the_same_rows_rms_c": round(rms(e_base[m]), 4)})(~np.isnan(e_e2e)),
            "refit_coef_all_rows": dict(zip(names, [round(float(v), 6) for v in b_all])), "M7_coef": m7["coef"],
            "session_heat_scales_all_rows": {s: round(v, 4) for s, v in h_all.items()},
            "paired_bootstrap_sessscale_minus_base": d, "per_card": per_card, "enters": bool(rule),
            "rule": "pooled d <= -0.010 C, 95% interval below 0, d < 0 on each card"}, hr, e_base, e_sess


def heat_c2_e():
    e = load(os.path.join(DD, "2026-11-04-e170-blind7-card0", "results.json"))
    tiles = e["score"]["reported"]["tiles"]
    names = sorted(tiles)
    r = np.array([tiles[n]["rise_c"] for n in names], float)
    P = np.array([tiles[n]["burst_w"] for n in names], float)
    k0 = load(os.path.join(DD, "2026-11-04-q140l-a2-session-terms", "m9_a2.json"))["burst_heat"]
    x = P - k0["P_idle_w"]
    e_base = r - k0["k_used_c_per_w"] * x
    ks, e_loto = np.zeros(len(names)), np.zeros(len(names))
    for i in range(len(names)):
        m = np.arange(len(names)) != i
        ks[i] = float(np.sum(r[m] * x[m]) / np.sum(x[m] ** 2))
        e_loto[i] = r[i] - ks[i] * x[i]
    kid = np.arange(len(names))
    d = boot(kid, e_loto, e_base)
    c2 = {"n": len(names), "k_frozen_c_per_w": k0["k_used_c_per_w"], "P_idle_w": k0["P_idle_w"],
          "frozen_law": {"rms_c": round(rms(e_base), 4), "bias_c": round(float(np.mean(e_base)), 4)},
          "loto": {"rms_c": round(rms(e_loto), 4), "bias_c": round(float(np.mean(e_loto)), 4)},
          "k_loto_range": [round(float(ks.min()), 4), round(float(ks.max()), 4)],
          "k_all_tiles": round(float(np.sum(r * x) / np.sum(x ** 2)), 4), "paired_bootstrap": d}
    c2["enters"] = bool(d and d["d_rms_w"] <= -0.25 and d["hi95"] < 0)
    # (e): kappa per family on the die-start-referred footing, leave one tile out
    pr = {n: tiles[n]["primary"] for n in names}
    bw = np.array([tiles[n]["burst_w"] for n in names], float)
    zl = np.array([pr[n]["zeros_level_w"] for n in names], float)
    aD = np.array([pr[n]["a2_burst_D_w"] for n in names], float)
    kap0 = e["kappa0"]
    base_board = np.array([pr[n]["burst_board_w"] for n in names], float)
    e0 = bw - (zl + kap0 * aD)
    famv = np.array([fam_of(tiles[n]["type"]) for n in names])
    kap = np.zeros(len(names))
    for i in range(len(names)):
        m = (np.arange(len(names)) != i) & (famv == famv[i]) & (aD > 1.0)
        kap[i] = statistics.median(((bw - zl) / aD)[m])
    e1 = bw - (zl + kap * aD)
    d = boot(kid, e1, e0)
    ee = {"n": len(names), "kappa0": kap0, "base_board_reproduces_primary_w": round(float(np.max(np.abs(base_board - (zl + kap0 * aD)))), 6),
          "kappa0_board": {"rms_w": round(rms(e0), 4), "bias_w": round(float(np.mean(e0)), 4)},
          "loto_kappa_board": {"rms_w": round(rms(e1), 4), "bias_w": round(float(np.mean(e1)), 4)},
          "kappa_loto_by_family": {f: [round(float(kap[famv == f].min()), 4), round(float(kap[famv == f].max()), 4)] for f in ("float", "int8")},
          "kappa_all_tiles_by_family": {f: round(statistics.median(((bw - zl) / aD)[(famv == f) & (aD > 1.0)]), 4) for f in ("float", "int8")},
          "paired_bootstrap": d}
    ee["enters"] = bool(d and d["d_rms_w"] <= -0.05 and d["hi95"] < 0)
    return c2, ee


def heat_d():
    """the chain's gain: per hold R (measured rise) and e (arm A's plateau error), the trip regime and K_OL_long left out"""
    H = []
    s = load(os.path.join(DD, "2026-11-02-e144-heat-minutes", "scored.json"))
    for h in s["holds"]:
        H.append(("E144", "aifoundry3", h["hold"], h["b"]["measured"]["plateau_rise_C"], h["a"]["plateau_err_C"], True))
    s = load(os.path.join(DD, "2026-11-02-e144-heat-minutes-aifoundry2", "results.json"))
    for h in s["score"]["holds"]:
        R = h["b"].get("plateau_rise_C")
        H.append(("E144b", "aifoundry2", h["G"], R, h["a"]["plateau_err_C"], h["G"] != "G2"))
    s = load(os.path.join(DD, "2026-11-03-e154-heat-e2e-aifoundry3", "scored.json"))
    for n, h in s["holds"].items():
        H.append(("E154", "aifoundry3", n, h["measured"]["plateau_rise_C"], h["A_given_watts"]["plateau_err_C"], True))
    s = load(os.path.join(DD, "2026-11-03-e161-heat-e2e-aifoundry2", "results.json"))
    for n, h in s["holds"].items():
        H.append(("E161", "aifoundry2", n, h["E_end_to_end"]["plateau_rise_measured_C"], h["A_given_watts"]["plateau_err_C"], n != "G2Q"))
    s = load(os.path.join(DD, "2026-11-04-e166-heat-replicate-aifoundry3", "scored.json"))
    for n, h in s["readings"].items():
        H.append(("E166", "aifoundry3", n, h["measured_rise_C"], h["A_plateau_err_C"], n != "K_OL_long"))
    s = load(os.path.join(DD, "2026-11-04-e167-heat-replicate-aifoundry2", "scored.json"))
    for n, h in s["holds"].items():
        H.append(("E167", "aifoundry2", n, h["measured_rise_C"], h["A_plateau_err_C"], n != "G2Q"))
    rows = [{"session": a, "card_kind": b, "hold": c, "R_C": None if R is None else float(R), "e_C": None if e is None else float(e),
             "fitted": bool(f and R is not None and e is not None)} for a, b, c, R, e, f in H]
    fit = [r for r in rows if r["fitted"]]
    for r in fit:
        r["P_C"] = r["R_C"] - r["e_C"]
    out = {"holds": rows, "variants": {}}
    for var in ("common", "per_card_kind"):
        for r in fit:
            tr = [q for q in fit if q["session"] != r["session"] and (var == "common" or q["card_kind"] == r["card_kind"])]
            g = sum(q["e_C"] * q["P_C"] for q in tr) / sum(q["P_C"] ** 2 for q in tr) if tr else 0.0
            r[f"gamma_{var}"] = g
            r[f"e_{var}"] = r["e_C"] - g * r["P_C"]
        big = [r for r in fit if r["R_C"] >= 10.0]
        kid = np.arange(len(big))
        d = boot(kid, [r[f"e_{var}"] for r in big], [r["e_C"] for r in big])
        ck = {c: (rms([r[f"e_{var}"] for r in big if r["card_kind"] == c]) - rms([r["e_C"] for r in big if r["card_kind"] == c]))
              for c in ("aifoundry3", "aifoundry2") if any(r["card_kind"] == c for r in big)}
        g_all = {}
        for c in (("all",) if var == "common" else ("aifoundry3", "aifoundry2")):
            tr = [q for q in fit if c == "all" or q["card_kind"] == c]
            g_all[c] = round(sum(q["e_C"] * q["P_C"] for q in tr) / sum(q["P_C"] ** 2 for q in tr), 5)
        out["variants"][var] = {"large_rise_n": len(big), "large_rise_without_rms_c": round(rms([r["e_C"] for r in big]), 4),
                                "large_rise_with_rms_c": round(rms([r[f"e_{var}"] for r in big]), 4),
                                "all_fitted_without_rms_c": round(rms([r["e_C"] for r in fit]), 4),
                                "all_fitted_with_rms_c": round(rms([r[f"e_{var}"] for r in fit]), 4),
                                "paired_bootstrap_large_rise": d, "d_rms_by_card_kind_c": {c: round(v, 4) for c, v in ck.items()},
                                "gamma_all_holds": g_all,
                                "passes": bool(d and d["d_rms_w"] <= -0.10 and d["hi95"] < 0 and all(v < 0 for v in ck.values()))}
    p = {v: out["variants"][v] for v in out["variants"] if out["variants"][v]["passes"]}
    if len(p) == 2:
        a, b = p["common"]["large_rise_with_rms_c"], p["per_card_kind"]["large_rise_with_rms_c"]
        out["enters"] = "per_card_kind" if b < a else "common"
    else:
        out["enters"] = next(iter(p)) if p else None
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--counts-dir", default=os.path.join(HERE, "bench"))
    ap.add_argument("--skip-b", action="store_true")
    a = ap.parse_args()
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)
    n_in = check_inputs()
    log(f"M10 refit: {n_in} registered inputs hash as tools/claims-v3/m10/SHA256SUMS")
    m9 = load(os.path.join(M9D, "m9.json"))
    rows, missing = assemble()
    log(f"rows: {len(rows)} ({sum(1 for r in rows if r['exp'] in ('E163', 'E164'))} pool 7); missing {missing}")
    if len(rows) != 959:
        stop(f"{len(rows)} rows, not 959")
    zeros, zr = M7.zeros_counts(), M9.zeros_rows()
    anchors, chk6 = assemble_anchors(rows, zeros, zr)
    fc = footing_consistency(rows)
    log(f"footing consistency: {fc}; pool 6 anchors' chain check {chk6}")
    # pool 7's features through the chain on its committed counts (the S rows' three-point check is in recount())
    c7 = load(os.path.join(B7, "counts-blind7.json"))["rows"]
    man7 = {m["name"]: m for m in load(os.path.join(B7, "blind7.json"))["tiles"]}
    f7 = load(os.path.join(B7, "predictions-blind7-aifoundry3.json"))["tiles"]
    worst7 = 0.0
    for n in S7:
        f9 = chain_feats(c7[n], os.path.join(B7, man7[n]["file"]), man7[n]["type"], zeros, zr)
        worst7 = max(worst7, max(abs(float(f9[q]) - float(v)) for q, v in f7[n]["features"].items() if v is not None))
    if worst7 > 1e-9:
        stop(f"the chain does not reproduce pool 7's frozen S features ({worst7})")
    res = {"_note": "Q142(m): M10's held-out refit (registered tools/claims-v3/m10/REGISTRATION.md, e9367b66); held out, not blind",
           "inputs_checked": n_in, "rows": len(rows), "missing": missing, "footing_consistency": fc, "pool6_anchor_chain_check": chk6,
           "pool7_S_chain_check_max_abs": worst7,
           "anchors_by_session": {s: [x["name"] for x in v] for s, v in anchors.items()}}
    # term b's counts
    rc = recount(a.counts_dir, zeros, zr)
    worst3 = 0.0
    idx = {}
    for i, r in enumerate(rows):
        if r["S_class"]:
            idx.setdefault(r["key"], []).append(i)
            f3 = rc[r["key"]].get("f3")
            if f3 is not None:
                worst3 = max(worst3, max(abs(float(f3[q]) - float(r["f"][q])) for q in m9["families"]["float"]["terms"]))
    log(f"S class: {len(idx)} tiles, {sum(len(v) for v in idx.values())} rows; three-point chain vs committed rows: max {worst3:.3g}")
    if worst3 > 1e-9:
        stop("the chain on the three-point counts does not reproduce the S rows' committed features")
    res["S_recount"] = {n: {k: v for k, v in rc[n].items() if k not in ("f3", "fN")} for n in rc}
    b_ready = all(rc[n]["complete"] for n in rc) and not a.skip_b
    log("S tiles: " + "; ".join(f"{n.split('.', 1)[1]} N={rc[n]['N']} e={rc[n]['by_N'][str(rc[n]['N'])]['e_w']:.3f}"
                                for n in rc if rc[n]["N"]))
    res["term_b_counts_complete"] = b_ready
    # self-test: the fitter on M9's own rows against fit_m7.Fam, and against nested-m9.json's aggregates
    nm9 = load(os.path.join(M9D, "nested-m9.json"))
    st = {}
    for fam in ("float", "int8"):
        r9 = [r for r in rows if fam_of(r["type"]) == fam and r["src"] == "rows-m9.json"]
        terms = m9["families"][fam]["terms"]
        ref = M7.Fam(r9, {"f": terms}, CARD_TERM).loko("f")
        mine = Fit10(r9, terms, {}, False).loko()[0]
        agg = nm9["families"][fam]["plain_loko_by_form"][m9["families"][fam]["form"]]["rms_all_w"]
        st[fam] = {"max_abs_row_diff_vs_Fam_w": float(np.nanmax(np.abs(ref - mine))), "rms_mine": rms(mine), "rms_nested_m9": agg}
        if st[fam]["max_abs_row_diff_vs_Fam_w"] > 1e-9 or abs(rms(mine) - agg) > 1e-9:
            stop(f"self-test {fam}: {st[fam]}")
    res["selftest"] = st
    log(f"self-test PASS: {st}")
    # power variants
    res["power"] = {}
    final = {}
    allrows_err = {}
    for fam in ("float", "int8"):
        fr = [r for r in rows if fam_of(r["type"]) == fam]
        terms = m9["families"][fam]["terms"]
        anc = {s: [x for x in v if fam_of(x["type"]) == fam] for s, v in anchors.items()}
        over = {}
        if fam == "float" and b_ready:
            for i, r in enumerate(fr):
                if r["S_class"]:
                    over[i] = rc[r["key"]]["fN"]
        variants = {"B": (False, None), "B+a": (True, None)}
        if fam == "float" and b_ready:
            variants.update({"B+b": (False, over), "B+a+b": (True, over)})
        fits, errs = {}, {}
        for vn, (us, ov) in variants.items():
            ft = Fit10(fr, terms, anc, us, ov)
            e, p, betas, scs, cs = ft.loko()
            fits[vn], errs[vn] = (ft, p, betas, scs, cs), e
            log(f"  {fam} {vn}: held-out rms {rms(e):.4f} W over {len(e)} rows, {ft.K} kinds")
        ft0 = fits["B"][0]
        kid = ft0.kid
        cds = np.array([r["card"] for r in fr])
        frozen = np.array([r["rate"] * sum(float(r["f"][q]) * c for q, c in zip(terms, m9["families"][fam]["coef_J"]))
                           * (m9["families"][fam]["card1_scale_by_format"][r["type"]] if r["card"] == "c1" else 1.0) for r in fr])
        e_m9 = np.array([r["D"] for r in fr]) - frozen
        pool7 = np.array([r["exp"] in ("E163", "E164") for r in fr])
        p1 = pool7 & np.array([r.get("priority") == 1 for r in fr])
        scl = np.array([r["S_class"] for r in fr])
        m9rows = np.array([r["src"] == "rows-m9.json" for r in fr])
        fam_out = {"n_rows": len(fr), "n_kinds": ft0.K, "variants": {}, "M9_as_frozen": {}}
        for lab, msk in (("all", None), ("pool 7, all 52", pool7), ("pool 7, priority 1", p1), ("S class", scl), ("M9's 855 rows", m9rows)):
            if msk is not None and not msk.any():
                continue
            fam_out["M9_as_frozen"][lab] = split(fr, e_m9, msk)
            for vn, e in errs.items():
                fam_out["variants"].setdefault(vn, {})[lab] = split(fr, e, msk)
        tests = {}
        if True:
            e0 = errs["B"]
            for vn in [v for v in errs if v != "B"]:
                d = boot(kid, errs[vn], e0)
                pc = {c: boot(kid[cds == c], errs[vn][cds == c], e0[cds == c]) for c in ("a3", "c1")}
                t = {"pooled": d, "per_card": pc}
                if scl.any() and "b" in vn:
                    t["S_class"] = boot(kid[scl], errs[vn][scl], e0[scl])
                    t["S_class_per_card"] = {c: boot(kid[scl & (cds == c)], errs[vn][scl & (cds == c)], e0[scl & (cds == c)]) for c in ("a3", "c1")}
                t["pool7_vs_M9_as_frozen"] = boot(kid[pool7], errs[vn][pool7], e_m9[pool7])
                tests[vn] = t
            tests["B"] = {"pool7_vs_M9_as_frozen": boot(kid[pool7], e0[pool7], e_m9[pool7])}
        fam_out["paired_bootstrap"] = tests
        # the entry rules
        ent = {}
        ta = tests["B+a"]
        ent["a"] = bool(ta["pooled"]["d_rms_w"] <= -0.005 and ta["pooled"]["hi95"] < 0 and all(ta["per_card"][c]["d_rms_w"] < 0 for c in ("a3", "c1")))
        if "B+b" in tests:
            tb = tests["B+b"]
            ent["b"] = bool(tb["S_class"]["d_rms_w"] <= -0.05 and tb["S_class"]["hi95"] < 0
                            and all(tb["S_class_per_card"][c]["d_rms_w"] < 0 for c in ("a3", "c1")) and tb["pooled"]["d_rms_w"] <= 0.001)
        fam_out["entry"] = ent
        vfinal = "B" + ("+a" if ent.get("a") else "") + ("+b" if ent.get("b") else "")
        fam_out["frozen_variant"] = vfinal
        log(f"  {fam}: entry {ent} -> {vfinal}")
        # sessions' scales (all rows, the frozen variant's rule) for the record
        ftF, pF, betasF, scsF, csF = fits[vfinal]
        fall = ftF.fit(None)
        fam_out["session_scales_all_rows"] = {s: round(float(v), 5) for s, v in zip(ftF.sessions, fall["s"])}
        fa = fits["B+a"][0].fit(None)
        fam_out["session_scales_term_a_all_rows"] = {s: round(float(v), 5) for s, v in zip(fits["B+a"][0].sessions, fa["s"])}
        fam_out["session_scale_anchor_counts"] = {s: len(anc.get(s, [])) for s in ftF.sessions}
        # the frozen form: prices (pass 2) and pass-1 prices, jackknife covariance by kind, card term, pools, band k
        Kk = ftF.K
        bJ = fall["b"] / ftF.sc
        b0J = fall["b0"] / ftF.sc
        bj = betasF / ftF.sc
        C = (Kk - 1) / Kk * ((bj - bj.mean(0)).T @ (bj - bj.mean(0)))
        eF = errs[vfinal]
        pools = {}
        for t in sorted(set(r["type"] for r in fr)):
            for c in ("a3", "c1"):
                mm = (np.array([r["type"] for r in fr]) == t) & (cds == c)
                pools[f"{t}|{c}"] = {"n": int(mm.sum()), "rms_w": rms(eF[mm])}
        Xraw = ftF.X * ftF.sc
        z, zpool = [], []
        for i, r in enumerate(fr):
            pl = pools[f"{r['type']}|{r['card']}"]["rms_w"]
            s = fall["c"] if r["card"] == "c1" else 1.0
            hw0 = math.sqrt(pl ** 2 + s * s * float(Xraw[i] @ C @ Xraw[i]))
            z.append(abs(eF[i]) / hw0)
            if r["exp"] in POOL_EXPS:
                zpool.append(abs(eF[i]) / hw0)
        kband = max(float(np.quantile(z, 0.95)), float(np.quantile(zpool, 0.95)))
        inside = sum(1 for v in z if v <= kband)
        final[fam] = {"form": m9["families"][fam]["form"], "variant": vfinal, "terms": terms, "coef_J": [float(v) for v in bJ],
                      "coef_fJ": [float(v) * 1e15 for v in bJ], "pass1_coef_J": [float(v) for v in b0J], "cov_J2": C.tolist(),
                      "card_term": CARD_TERM, "card1_scale": float(fall["c"]), "interval_pool_by_format_card": pools,
                      "band_k": kband, "band_coverage_all_rows": [inside, len(z)],
                      "session_scale": ({"anchors": [x for x in ANCHORS if fam_of(x.split('.')[0]) == fam],
                                         "statistic": "median of measured D / (rate x pass-1 prices x features x card term)",
                                         "no_anchor": 1.0} if "+a" in vfinal else None),
                      "S_class_counts": ("RECOUNT-RULE.md N-point mean_rows for case-S tiles" if "+b" in vfinal else None),
                      "n_rows": len(fr), "n_kinds": Kk}
        fam_out["band"] = {"k": kband, "coverage_all_rows": [inside, len(z)]}
        res["power"][fam] = fam_out
        insample = ftF.pred(np.ones(len(fr), bool), fall)
        final[fam]["session_scales_training"] = fam_out["session_scales_all_rows"]
        allrows_err[fam] = (fr, errs, e_m9, insample)
    # heat and card 0
    log("heat (c1):")
    dpred = {}
    for fam, (fr, errs, e_m9, insample) in allrows_err.items():
        ev = errs[res["power"][fam]["frozen_variant"]]
        for i, r in enumerate(fr):
            if not np.isnan(ev[i]):
                dpred[(r["exp"], r["key"])] = r["D"] - float(ev[i])
    c1, hr, eb, es = heat_c1(rows, log, dpred)
    res["heat_c1"] = c1
    log(f"  base {c1['base_refit_loko']['all']}; with session scale {c1['with_session_heat_scale_loko']['all']}; enters {c1['enters']}")
    c2, ee = heat_c2_e()
    res["heat_c2_card0_burst"] = c2
    res["kappa_e_card0"] = ee
    log(f"c2: frozen {c2['frozen_law']} loto {c2['loto']} enters {c2['enters']}")
    log(f"e: kappa0 {ee['kappa0_board']} loto {ee['loto_kappa_board']} enters {ee['enters']}")
    d = heat_d()
    res["heat_d_chain_gain"] = d
    log(f"d: {json.dumps({v: {k: d['variants'][v][k] for k in ('large_rise_without_rms_c', 'large_rise_with_rms_c', 'passes', 'gamma_all_holds')} for v in d['variants']})} enters {d['enters']}")
    # write
    os.makedirs(a.out, exist_ok=True)
    m10 = {"_model": "M10 (Q142(m)): M9's forms refitted on 959 rows with the terms that entered by tools/claims-v3/m10/REGISTRATION.md",
           "registration": "tools/claims-v3/m10/REGISTRATION.md (e9367b66)", "footing": m9["footing"], "families": final,
           "heat_4p5s": {"form": "H2_per_card_runlength", "coef": c1["refit_coef_all_rows"], "session_heat_scale": c1["enters"],
                         "M7_coef_as_frozen": c1["M7_coef"]},
           "card0_burst_heat_k_c_per_w": c2["k_all_tiles"] if c2["enters"] else c2["k_frozen_c_per_w"],
           "card0_kappa": ee["kappa_all_tiles_by_family"] if ee["enters"] else {"float": ee["kappa0"], "int8": ee["kappa0"]},
           "heat_chain_gain": ({"variant": d["enters"], "gamma": d["variants"][d["enters"]]["gamma_all_holds"]} if d["enters"] else None),
           "entered": {"a_float": res["power"]["float"]["entry"].get("a"), "a_int8": res["power"]["int8"]["entry"].get("a"),
                       "b": res["power"]["float"]["entry"].get("b"), "c1": c1["enters"], "c2": c2["enters"], "d": d["enters"], "e": ee["enters"]}}
    json.dump(m10, open(os.path.join(a.out, "m10.json"), "w"), indent=1, sort_keys=True)
    json.dump(res, open(os.path.join(a.out, "heldout-m10.json"), "w"), indent=1, sort_keys=True)
    rowsout = []
    for fam, (fr, errs, e_m9, insample) in allrows_err.items():
        for i, r in enumerate(fr):
            rowsout.append({"exp": r["exp"], "card": r["card"], "key": r["key"], "kind": r["kind"], "type": r["type"], "D": r["D"],
                            "S_class": r["S_class"], "priority": r.get("priority"), "M10_insample_pred_w": float(insample[i]),
                            "err_w": {vn: (None if np.isnan(e[i]) else round(float(e[i]), 6)) for vn, e in errs.items()},
                            "M9_as_frozen_err_w": round(float(e_m9[i]), 6)})
    json.dump(rowsout, open(os.path.join(a.out, "rows-m10.json"), "w"), indent=0)
    open(os.path.join(a.out, "fit-output.txt"), "w").write("\n".join(lines) + "\n")
    log("wrote m10.json, heldout-m10.json, rows-m10.json, fit-output.txt")


if __name__ == "__main__":
    main()
