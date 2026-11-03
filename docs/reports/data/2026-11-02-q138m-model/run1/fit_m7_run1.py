#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q138(m): M7 = the power model refitted on every public kinds row (M6's 22 experiments plus blind pool 4 / E140 and E137),
its structure chosen by NESTED leave-one-kind-out with M5's, M6's and M7's procedures scored on the same folds, its 95% bands
sized on held-out residuals (nested, and blind pools 3 and 4), plus (a) a card term for aifoundry1 card 1, (b) a clock and
voltage term for aifoundry2 under its own governor in bursts, (c) a heat term per card. Frozen before blind pool 5 exists.

    python3 fit_m7.py      # writes m7.json, loko-m7.json, rows-m7.json, heat-rows-m7.json beside it (about a minute)

Power rows: M6's rows (rows-m6.json, byte for byte M6's assembly) + E137 (aifoundry1 card 1; E128's fp16 tiles, counted in
E128's desk counts) + E140 (aifoundry3; blind pool 4, counted in Q137(m)'s counts-blind4.json). E134 and E138 carry no
per-tile board D (their items' D is null: bit ladders reduced on the rail), so they enter as TERMS, not rows: E138's
per-position B price (B's odd bits 1.91x its even bits) as int8 candidate features; E134's A low-bit result (the flip alone
is the price at A's low bits) as the float candidate a_lo. E139's encoded term prices DRAM-streamed images, which a kinds
tile (a resident loop) never moves: it is frozen beside the model as a separate component and is zero for a kinds tile.
New candidate features from the tile bytes (make_kinds' issue stream, as M5/M6):
  b_odd, b_even : B-side bit flips between consecutive micro-ops at odd / even bit positions of each byte (int8, E138)
  b138          : b_even + 1.91 b_odd, E138's measured odd/even ratio as one priced feature (int8)
  a_lo          : A-side flips in the low 8 mantissa bits (floats; E134), broadcast to the column slots as abits
  glive         : the live (ungated) share of the gate slots, make_kinds' gate rule (the six E140 misses: gated lanes)
Fitting: per-kind normal equations, batched (numerically the least-squares solution of M5's Family, with a 1e-9 relative
ridge on column-scaled features); the card-1 rows divided by the chosen card term inside every fold.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import math
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M6D = os.path.join(DD, "2026-11-02-q137m-model")
M5D = os.path.join(DD, "2026-11-01-q133b-power-model")
sys.path.insert(0, M6D)
import fit_m6 as M6  # noqa: E402  (imports m6_rows and fit_m5, unchanged)
R = M6.R
F = M6.F
mk = F.mk
POOL4 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind4")
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.load(open(p))
rms = F.rms

E138_ODD_OVER_EVEN = 1.91          # E138 README Results: B odd bits cost 1.91x [1.71, 2.16] its even bits (board-equivalent)
E139_W_PER_IMAGE = 0.185           # E139: E132's frozen +0.185 W per encoded image predicted E139 to 0.028 W rms
E139_PJ_PER_ENCODED_TOGGLE = 0.46  # E139 README: 0.46 pJ an encoded toggle (primary arm)


# ------------------------------------------------------------------ features
def extra_feats(path, t):
    raw = open(path, "rb").read()
    aw, bw = mk.words_of(raw)
    a, b = mk.issue_streams_fast(aw, bw, t)
    g = mk.gate_mask(a, b, t)
    a64 = a.astype(np.uint64)
    b64 = b.astype(np.uint64)
    da = a64 ^ np.roll(a64, -1)
    db = b64 ^ np.roll(b64, -1, axis=0)
    pc = lambda x: mk.popcount32(np.asarray(x, dtype=np.uint64).astype(np.uint32))
    slots = mk.COLUMN_SLOTS[t]
    lo = {"fp32": 0x000000FF, "fp16": 0x00FF00FF, "int8": 0x0F0F0F0F}[t]
    bo = float(pc(db & np.uint64(0xAAAAAAAA)).sum())
    be = float(pc(db & np.uint64(0x55555555)).sum())
    return {"b_odd": bo, "b_even": be, "b138": be + E138_ODD_OVER_EVEN * bo,
            "a_lo": float(pc(da & np.uint64(lo)).sum() * slots), "glive": float(1.0 - np.mean(g))}


def feats_from_counts(crow, p, t, zeros):
    f = F.fmt_feats(F.bench_feats(crow["mean"], zeros[t]), t)
    f.update({k: v for k, v in F.tile_feats(p, t).items() if k != "sha256"})
    f.update(M6.flip_feats(p, t))
    f.update(extra_feats(p, t))
    return f


# ------------------------------------------------------------------ rows
def zeros_counts():
    zc = load(os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-v2.json"))["rows"]
    return {t: zc[f"{t}.zeros"]["mean"] for t in F.CPO}


def assemble():
    rows = load(os.path.join(M6D, "rows-m6.json"))
    for r in rows:
        r["f"].update(extra_feats(os.path.join(ROOT, r["tile_path"]), r["type"]))
    zeros = zeros_counts()
    by_sha = {}
    for r in rows:
        by_sha.setdefault(r["tile_sha256"], r)
    missing = []
    # E137, aifoundry1 card 1: E128's fp16 tiles (counted in E128's desk counts) and E78's fp16.ones
    idx = R.count_index()
    d = load(os.path.join(DD, "2026-11-02-e137-fp16-sign-rest", "e137.json"))
    for key, it in d["items"].items():
        if key == "anchor_pi" or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            continue
        t = it["type"]
        n = key.split(".", 1)[1]
        if n in F.ANCHOR_NAMES or n in ("randn", "full"):
            continue
        p = R.tile_for("E137", t, n)
        if p is None:
            missing.append(f"E137:{key} (no tile)")
            continue
        h = sha(open(p, "rb").read())
        if h in by_sha:
            f, lab = dict(by_sha[h]["f"]), by_sha[h]["kind"]
        elif h in idx:
            f, lab = feats_from_counts(idx[h], p, t, zeros), f"{t}.e137:{n}"
        else:
            missing.append(f"E137:{key} (no counts)")
            continue
        rows.append({"exp": "E137", "card": "c1", "key": key, "type": t, "kind": lab, "tile_sha256": h, "tile_path": os.path.relpath(p, ROOT),
                     "D": float(it["D"]["mean"]), "D_se": it["D"].get("se"), "rate": float(it["rate"]["mean"]), "f": f,
                     "dT_win": (it.get("dT_win") or {}).get("mean")})
    # E140, aifoundry3 card 0: blind pool 4 (Q137(m)'s counts-blind4.json, 0 mismatches)
    man = load(os.path.join(POOL4, "blind4.json"))
    c4 = load(os.path.join(M6D, "counts-blind4.json"))["rows"]
    d = load(os.path.join(DD, "2026-11-02-e140-blind4", "e140.json"))
    for meta in man["tiles"]:
        name, t = meta["name"], meta["type"]
        it = d["items"].get(name)
        if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            missing.append(f"E140:{name} (no D)")
            continue
        p = os.path.join(POOL4, meta["file"])
        h = sha(open(p, "rb").read())
        if h in by_sha:
            f, lab = dict(by_sha[h]["f"]), by_sha[h]["kind"]
        else:
            f, lab = feats_from_counts(c4[name], p, t, zeros), f"{t}.blind4:{name.split('.', 1)[1]}"
        rows.append({"exp": "E140", "card": "a3", "key": name, "type": t, "kind": lab, "tile_sha256": h, "tile_path": os.path.relpath(p, ROOT),
                     "D": float(it["D"]["mean"]), "D_se": it["D"].get("se"), "rate": float(it["rate"]["mean"]), "f": f,
                     "dT_win": (it.get("dT_win") or {}).get("mean"), "case": meta.get("case")})
    return rows, missing


# ------------------------------------------------------------------ forms (written before any M7 fit ran)
BASE_F = M6.BASE_F
BASE_I = M6.BASE_I
FLD = M6.FLD
FORMS = {
    "float": {
        "G0_M5": BASE_F,
        "G1_gtr": BASE_F + ["gtr"],
        "G6_M6": BASE_F + ["gtr", "psgn"] + FLD,
        "G8_gtr_glive": BASE_F + ["gtr", "glive"],
        "G9_gtr_exp": BASE_F + ["gtr", "a_exp", "b_exp"],
        "G10_gtr_alo": BASE_F + ["gtr", "a_lo"],
        "G11_gtr_glive_exp": BASE_F + ["gtr", "glive", "a_exp", "b_exp"],
    },
    "int8": {
        "J0_M5": BASE_I,
        "J1_M6": BASE_I + ["gtr"],
        "J6_bpos": BASE_I + ["b_odd", "b_even"],
        "J7_gtr_bpos": BASE_I + ["gtr", "b_odd", "b_even"],
        "J8_b138": BASE_I + ["b138"],
        "J9_glive": BASE_I + ["glive"],
    },
}
BASE_FORM = {"float": "G0_M5", "int8": "J0_M5"}
M6_FORM = {"float": "G6_M6", "int8": "J1_M6"}

# card terms (a): how aifoundry1 card 1's D relates to aifoundry3 card 0's on the same tile
CARD_TERMS = ("C0_M5_E78E82_family", "C1_allpairs_family", "C2_allpairs_format")


# ------------------------------------------------------------------ batched normal-equation family
class Fam:
    def __init__(self, rows, forms, card_term):
        self.rows = rows
        self.forms = forms
        self.card_term = card_term
        self.y = np.array([r["D"] for r in rows], float)
        self.c1 = np.array([r["card"] == "c1" for r in rows])
        self.tys = np.array([r["type"] for r in rows])
        self.fmts = sorted(set(self.tys))
        self.kinds = sorted({r["kind"] for r in rows})
        ki = {k: i for i, k in enumerate(self.kinds)}
        self.kid = np.array([ki[r["kind"]] for r in rows])
        self.K = len(self.kinds)
        self.X, self.sc, self.G, self.ha, self.hc = {}, {}, {}, {}, {}
        for fn, terms in forms.items():
            X = F.X_of(rows, terms)
            sc = np.where(np.abs(X).max(axis=0) == 0, 1.0, np.abs(X).max(axis=0))
            Xs = X / sc
            p = Xs.shape[1]
            G = np.zeros((self.K, p, p))
            ha = np.zeros((self.K, p))
            hc = {f: np.zeros((self.K, p)) for f in self.fmts}
            for i in range(len(rows)):
                k = self.kid[i]
                x = Xs[i]
                G[k] += np.outer(x, x)
                if self.c1[i]:
                    hc[self.tys[i]][k] += x * self.y[i]
                else:
                    ha[k] += x * self.y[i]
            self.X[fn], self.sc[fn], self.G[fn], self.ha[fn], self.hc[fn] = Xs, sc, G, ha, hc
        # card pairs: kinds with rows on both cards; per kind the mean D on each card
        self.N = np.zeros((self.K, len(self.fmts)))
        self.Dn = np.zeros((self.K, len(self.fmts)))
        self.npair = np.zeros((self.K, len(self.fmts)))
        for k in range(self.K):
            m = self.kid == k
            for j, f in enumerate(self.fmts):
                a = self.y[m & ~self.c1 & (self.tys == f)]
                b = self.y[m & self.c1 & (self.tys == f)]
                if card_term == "C0_M5_E78E82_family":
                    ex = np.array([r["exp"] for r in rows])
                    a = self.y[m & (ex == "E78") & (self.tys == f)]
                    b = self.y[m & (ex == "E82") & (self.tys == f)]
                if len(a) and len(b) and a.mean() > 0.5:
                    self.N[k, j] = a.mean() * b.mean()
                    self.Dn[k, j] = a.mean() ** 2
                    self.npair[k, j] = 1
        self.fidx = np.array([self.fmts.index(t) for t in self.tys])

    def scales(self, ex1=None, ex2=None):
        """card-1 scale per format, excluding up to two kind-id arrays (broadcast): shape (n, n_fmt)."""
        N, Dn, C = self.N.sum(0), self.Dn.sum(0), self.npair.sum(0)
        N = np.broadcast_to(N, (1, len(self.fmts))).copy()
        Dn = np.broadcast_to(Dn, (1, len(self.fmts))).copy()
        C = np.broadcast_to(C, (1, len(self.fmts))).copy()
        for ex in (ex1, ex2):
            if ex is None:
                continue
            ex = np.atleast_1d(ex)
            N = N - self.N[ex]
            Dn = Dn - self.Dn[ex]
            C = C - self.npair[ex]
        if self.card_term in ("C0_M5_E78E82_family", "C1_allpairs_family"):
            s = np.where(C.sum(1) >= 3, N.sum(1) / np.maximum(Dn.sum(1), 1e-12), 1.0)
            return np.repeat(s[:, None], len(self.fmts), axis=1)
        return np.where(C >= 3, N / np.maximum(Dn, 1e-12), 1.0)

    def fit_many(self, fn, ex1, ex2=None):
        """Fit form fn once for each entry of ex1 (kind ids), every fit excluding that kind (and ex2's, if given)."""
        G, ha, hc = self.G[fn], self.ha[fn], self.hc[fn]
        Gt = G.sum(0)
        GG = Gt[None] - G[ex1]
        h = ha.sum(0)[None] - ha[ex1]
        if ex2 is not None:
            GG = GG - G[ex2][None] if np.ndim(ex2) == 0 else GG - G[ex2]
            h = h - (ha[ex2][None] if np.ndim(ex2) == 0 else ha[ex2])
        s = self.scales(ex1, ex2)
        for j, f in enumerate(self.fmts):
            hcf = hc[f].sum(0)[None] - hc[f][ex1]
            if ex2 is not None:
                hcf = hcf - (hc[f][ex2][None] if np.ndim(ex2) == 0 else hc[f][ex2])
            h = h + hcf / s[:, j:j + 1]
        p = GG.shape[1]
        lam = 1e-9 * np.trace(Gt) / p
        b = np.linalg.solve(GG + lam * np.eye(p)[None], h[..., None])[..., 0]
        return b, s

    def fit_all(self, fn, excl=()):
        excl = list(excl)
        G, ha, hc = self.G[fn], self.ha[fn], self.hc[fn]
        keep = np.ones(self.K, bool)
        keep[excl] = False
        GG = G[keep].sum(0)
        h = ha[keep].sum(0)
        N, Dn, C = self.N[keep].sum(0), self.Dn[keep].sum(0), self.npair[keep].sum(0)
        if self.card_term in ("C0_M5_E78E82_family", "C1_allpairs_family"):
            s = np.full(len(self.fmts), N.sum() / Dn.sum() if C.sum() >= 3 else 1.0)
        else:
            s = np.where(C >= 3, N / np.maximum(Dn, 1e-12), 1.0)
        for j, f in enumerate(self.fmts):
            h = h + hc[f][keep].sum(0) / s[j]
        p = GG.shape[0]
        b = np.linalg.solve(GG + 1e-9 * np.trace(G.sum(0)) / p * np.eye(p), h)
        return b, s

    def pred_rows(self, fn, b, s, mask):
        """b: (p,) or per-row (n_mask, p); s: (n_fmt,) or per-row (n_mask, n_fmt)"""
        X = self.X[fn][mask]
        v = np.sum(X * b, axis=1) if b.ndim == 2 else X @ b
        sf = s[np.arange(len(v)), self.fidx[mask]] if s.ndim == 2 else s[self.fidx[mask]]
        return v * np.where(self.c1[mask], sf, 1.0)

    def loko(self, fn, outer=None):
        """leave-one-kind-out errors (D - prediction); with outer, every fit also leaves out kind `outer` (NaN there)."""
        ks = np.arange(self.K)
        if outer is not None:
            ks = ks[ks != outer]
        b, s = self.fit_many(fn, ks, outer)
        pos = np.full(self.K, -1)
        pos[ks] = np.arange(len(ks))
        err = np.full(len(self.y), np.nan)
        m = pos[self.kid] >= 0
        rb = b[pos[self.kid[m]]]
        rs = s[pos[self.kid[m]]]
        err[m] = self.y[m] - self.pred_rows(fn, rb, rs, m)
        return err

    def coef_J(self, fn, b):
        return b / self.sc[fn]

    def jackknife_cov(self, fn):
        b, _ = self.fit_many(fn, np.arange(self.K))
        b = b / self.sc[fn][None]
        d = b - b.mean(0)
        return d.T @ d * (self.K - 1) / self.K


def split(fam, err, extra=None):
    o = {"all": rms(err), "n": int(np.sum(~np.isnan(err)))}
    for t in fam.fmts:
        m = fam.tys == t
        e = err[m]
        e = e[~np.isnan(e)]
        o[t] = {"n": int(len(e)), "rms_w": rms(e), "bias_pred_minus_meas_w": -float(np.mean(e)) if len(e) else None}
    for lab, m in (("card a3", ~fam.c1), ("card c1", fam.c1)):
        e = err[m]
        e = e[~np.isnan(e)]
        o[lab] = {"n": int(len(e)), "rms_w": rms(e)}
    return o


def frozen_pred(rows, mod, fam_c1):
    X = F.X_of(rows, mod["terms"])
    return X @ np.array(mod["coef_J"]) * np.where(fam_c1, mod["card1_scale"], 1.0)


def q95(v):
    v = np.sort(np.abs(np.asarray(v, float)[~np.isnan(np.asarray(v, float))]))
    return float(np.quantile(v, 0.95)) if len(v) else None


# ------------------------------------------------------------------ the power family
def run_family(rows, famname, m5, m6):
    out = {}
    # (a) the card term, chosen first: leave-one-kind-out over the paired kinds of each card term
    card = {}
    for ct in CARD_TERMS:
        fam = Fam(rows, {"G": FORMS[famname][BASE_FORM[famname]]}, ct)
        errs = []
        for k in range(fam.K):
            for j, f in enumerate(fam.fmts):
                if fam.npair[k, j]:
                    s = fam.scales(np.array([k]))[0, j]
                    a = math.sqrt(fam.Dn[k, j])
                    errs.append(fam.N[k, j] / a - s * a)
        s_all = fam.scales()[0]
        card[ct] = {"loko_rms_w": rms(errs), "n_pairs": len(errs), "scale_by_format": dict(zip(fam.fmts, [float(x) for x in s_all]))}
    best_ct = min(card, key=lambda c: card[c]["loko_rms_w"] if card[c]["n_pairs"] >= 10 else 9e9)
    out["card_terms"] = card
    out["card_term_chosen"] = best_ct
    fam = Fam(rows, FORMS[famname], best_ct)
    # M5, M6 as frozen (no refit) on these rows
    e5 = fam.y - frozen_pred(rows, m5["families"][famname], fam.c1)
    e6 = fam.y - frozen_pred(rows, m6["families"][famname], fam.c1)
    plain = {fn: fam.loko(fn) for fn in fam.forms}
    outer = np.full(len(fam.y), np.nan)
    picks = {}
    for k in range(fam.K):
        sc = {fn: rms(fam.loko(fn, k)) for fn in fam.forms}
        best = min(sc, key=sc.get)
        b, s = fam.fit_all(best, [k])
        m = fam.kid == k
        outer[m] = fam.y[m] - fam.pred_rows(best, b, s, m)
        picks[best] = picks.get(best, 0) + 1
    sel = {fn: rms(e) for fn, e in plain.items()}
    chosen = min(sel, key=sel.get)
    # keep only terms that lower the error: the procedure must beat M5's form on the same folds, else M5's form is frozen
    nested_rms, base_rms = rms(outer), rms(plain[BASE_FORM[famname]])
    kept_rule = "chosen form (the procedure's nested error is below M5's form on the same folds)"
    if not nested_rms < base_rms:
        chosen = BASE_FORM[famname]
        kept_rule = "M5's form (the procedure did not lower the nested error below M5's form on the same folds)"
    # each added term dropped in turn, plain LOKO (reported)
    drops = {}
    base_terms = FORMS[famname][BASE_FORM[famname]]
    for q in FORMS[famname][chosen]:
        if q in base_terms:
            continue
        sub = [x for x in FORMS[famname][chosen] if x != q]
        f2 = Fam(rows, {"S": sub}, best_ct)
        drops[q] = {"plain_loko_without_w": rms(f2.loko("S")), "plain_loko_with_w": sel[chosen]}
    b, s = fam.fit_all(chosen, [])
    C = fam.jackknife_cov(chosen)
    coefJ = fam.coef_J(chosen, b)
    exps = np.array([r["exp"] for r in rows])
    by_exp = {e: {"n": int(np.sum(exps == e)), "M7_nested_rms_w": rms(outer[exps == e]), "M6_form_loko_rms_w": rms(plain[M6_FORM[famname]][exps == e]),
                  "M5_form_loko_rms_w": rms(plain[BASE_FORM[famname]][exps == e]), "M5_frozen_rms_w": rms(e5[exps == e]), "M6_frozen_rms_w": rms(e6[exps == e])}
              for e in sorted(set(exps))}
    # band calibration (1): nested residuals of M7, scaled by the format-and-card pool
    pools = {}
    for t in fam.fmts:
        for cd, cm in (("a3", ~fam.c1), ("c1", fam.c1)):
            e = outer[(fam.tys == t) & cm]
            pools[f"{t}|{cd}"] = {"rms_w": rms(e), "n": int(np.sum(~np.isnan(e))), "q95_abs_w": q95(e)}
    z_nested = []
    for i in range(len(rows)):
        pl = pools[f"{fam.tys[i]}|{'c1' if fam.c1[i] else 'a3'}"]
        if pl["rms_w"] and not math.isnan(outer[i]):
            z_nested.append(abs(outer[i]) / pl["rms_w"])
    # band calibration (2): blind residuals of the models that predicted pools 3 and 4 blind, on their own pools
    z_blind = []
    blind_sets = {"pool3_E115_M5": ("E115", e5, m5), "pool4_E140_M5": ("E140", e5, m5), "pool4_E140_M6": ("E140", e6, m6)}
    blind_rep = {}
    for lab, (ex, err, mod) in blind_sets.items():
        zz = []
        for i in np.where(exps == ex)[0]:
            pl = mod["families"][famname]["interval_pool_by_format_card"].get(f"{fam.tys[i]}|{'c1' if fam.c1[i] else 'a3'}")
            if pl and pl.get("rms_w"):
                zz.append(abs(err[i]) / pl["rms_w"])
        z_blind += zz
        blind_rep[lab] = {"n": len(zz), "rms_w": rms(err[exps == ex]), "bias_pred_minus_meas_w": -float(np.mean(err[exps == ex])) if np.any(exps == ex) else None,
                          "z_q95": float(np.quantile(zz, 0.95)) if zz else None, "inside_1p96": int(sum(1 for z in zz if z <= 1.96))}
    out.update({
        "n_rows": len(rows), "n_kinds": fam.K,
        "side_by_side_same_folds": {
            "M5_frozen_no_refit": split(fam, e5), "M6_frozen_no_refit": split(fam, e6),
            "M5_form_refit_plain_loko": split(fam, plain[BASE_FORM[famname]]),
            "M6_form_refit_plain_loko": split(fam, plain[M6_FORM[famname]]),
            "M7_nested_loko": {**split(fam, outer), "inner_picks": picks}},
        "plain_loko_by_form": {fn: split(fam, e) for fn, e in plain.items()},
        "chosen_form": chosen, "kept_rule": kept_rule, "chosen_terms": FORMS[famname][chosen], "drop_one_term": drops,
        "fit_on_all": {"coef_fJ": dict(zip(FORMS[famname][chosen], [float(x) * 1e15 for x in coefJ])),
                       "coef_jackknife_se_fJ": dict(zip(FORMS[famname][chosen], [float(x) * 1e15 for x in np.sqrt(np.diag(C))])),
                       "card1_scale_by_format": dict(zip(fam.fmts, [float(x) for x in s]))},
        "by_experiment": by_exp,
        "band_calibration": {"pools": pools, "z_nested_q95": float(np.quantile(z_nested, 0.95)), "n_nested": len(z_nested),
                             "z_blind_q95": float(np.quantile(z_blind, 0.95)) if z_blind else None, "n_blind": len(z_blind), "blind_sets": blind_rep},
        "largest_nested_misses": sorted([{"exp": r["exp"], "key": r["key"], "D": r["D"], "err_w": float(outer[i]), "m5_frozen_err_w": float(e5[i]), "m6_frozen_err_w": float(e6[i])}
                                         for i, r in enumerate(rows)], key=lambda x: -abs(x["err_w"]))[:15],
    })
    kband = max(out["band_calibration"]["z_nested_q95"], out["band_calibration"]["z_blind_q95"] or 0.0)
    # the band rule, applied back: coverage on M7's own nested residuals overall and on the two blind pools' rows
    cover = {}
    for lab, msk in (("all", np.ones(len(rows), bool)), ("E115 rows", exps == "E115"), ("E140 rows", exps == "E140")):
        ins = tot = 0
        for i in np.where(msk)[0]:
            if math.isnan(outer[i]):
                continue
            pl = pools[f"{fam.tys[i]}|{'c1' if fam.c1[i] else 'a3'}"]["rms_w"]
            x = fam.X[chosen][i] / 1.0
            tot += 1
            ins += int(abs(outer[i]) <= kband * pl)
        cover[lab] = {"inside": ins, "n": tot}
    out["band_calibration"]["k"] = kband
    out["band_calibration"]["coverage_of_rule_on_M7_nested"] = cover
    frozen = {"form": chosen, "terms": FORMS[famname][chosen], "coef_J": [float(x) for x in coefJ], "coef_fJ": [float(x) * 1e15 for x in coefJ],
              "cov_J2": C.tolist(), "card_term": best_ct, "card1_scale_by_format": dict(zip(fam.fmts, [float(x) for x in s])),
              "interval_pool_by_format_card": pools, "band_k": kband, "n_rows": len(rows), "n_kinds": fam.K}
    return out, frozen, outer, e5, e6


# ------------------------------------------------------------------ heat (c), aifoundry3 and aifoundry1 card 1: the kinds window
HFORMS7 = {
    "H1_per_card": ["S|card"],
    "H2_per_card_runlength": ["S|card", "ST|card"],
    "H4_per_card_int8": ["S|card", "S_int8"],
}


def heat_rows(rows):
    M6.EXPDIR["E137"] = "2026-11-02-e137-fp16-sign-rest"
    M6.EXPDIR["E140"] = "2026-11-02-e140-blind4"
    return M6.heat_rows(rows)


def heat_fit(hr):
    cards = sorted({r["card"] for r in hr})
    y = np.array([r["dT"] for r in hr])
    kinds = sorted({r["kind"] for r in hr})
    kid = np.array([kinds.index(r["kind"]) for r in hr])
    X = {fn: M6.hX(hr, t, cards) for fn, t in HFORMS7.items()}

    def fit(fn, excl):
        m = ~np.isin(kid, list(excl))
        return np.linalg.lstsq(X[fn][m], y[m], rcond=None)[0]

    def loko(fn, outer=()):
        e = np.full(len(y), np.nan)
        for k in range(len(kinds)):
            if k in outer:
                continue
            b = fit(fn, set(outer) | {k})
            m = kid == k
            e[m] = y[m] - X[fn][m] @ b
        return e

    plain = {fn: loko(fn) for fn in HFORMS7}
    outer = np.full(len(y), np.nan)
    picks = {}
    for k in range(len(kinds)):
        sc = {fn: rms(loko(fn, (k,))) for fn in HFORMS7}
        best = min(sc, key=sc.get)
        b = fit(best, {k})
        m = kid == k
        outer[m] = y[m] - X[best][m] @ b
        picks[best] = picks.get(best, 0) + 1
    sel = {fn: rms(e) for fn, e in plain.items()}
    best = min(sel, key=sel.get)
    if not rms(outer) < sel["H1_per_card"]:
        best = "H1_per_card"
    b = fit(best, set())
    tys = np.array([r["type"] for r in hr])
    cds = np.array([r["card"] for r in hr])
    exps = np.array([r["exp"] for r in hr])
    prior = y - M6.PRIOR_C_PER_W * np.array([r["S"] for r in hr])
    m6c = {"aifoundry3": 0.1184, "aifoundry1-c1": 0.1155}

    def by(e):
        o = {"all": rms(e), "n": int(np.sum(~np.isnan(e)))}
        for t in ("fp32", "fp16", "int8"):
            o[t] = {"n": int(np.sum(tys == t)), "rms_c": rms(e[tys == t]), "q95_abs_c": q95(e[tys == t])}
        for c in cards:
            o[c] = {"n": int(np.sum(cds == c)), "rms_c": rms(e[cds == c]), "q95_abs_c": q95(e[cds == c])}
        return o
    names = []
    for q in HFORMS7[best]:
        names += [f"{q[:-5]}|{c}" for c in cards] if q.endswith("|card") else [q]
    m6e = y - np.array([m6c.get(r["card"], 0.118) * r["S"] for r in hr])
    pools = {f"{t}|{c}": {"rms_c": rms(outer[(tys == t) & (cds == c)]), "q95_abs_c": q95(outer[(tys == t) & (cds == c)]), "n": int(np.sum((tys == t) & (cds == c)))}
             for t in ("fp32", "fp16", "int8") for c in cards}
    z = []
    for i in range(len(hr)):
        pl = pools[f"{tys[i]}|{cds[i]}"]["rms_c"]
        if pl and not math.isnan(outer[i]):
            z.append(abs(outer[i]) / pl)
    return {"cards": cards, "n_rows": len(hr), "n_kinds": len(kinds),
            "before_prior_rule_0118": by(prior), "M6_frozen_coefficients": by(m6e),
            "plain_loko_by_form": {fn: by(e) for fn, e in plain.items()},
            "nested_loko": {**by(outer), "inner_picks": picks},
            "E140_rows_nested": {"n": int(np.sum(exps == "E140")), "rms_c": rms(outer[exps == "E140"]), "M6_frozen_rms_c": rms(m6e[exps == "E140"])},
            "chosen_form": best, "coef": dict(zip(names, [float(x) for x in b])),
            "pools": pools, "band_k": float(np.quantile(z, 0.95))}, outer


# ------------------------------------------------------------------ (b) aifoundry2 under its own governor, bursts; (c) its burst heat
def a2_governor(row_pred_a3):
    """E136's frozen relation (E101's B(f), s(f) = (V_f/V_600)^2 f/600 with aifoundry2's telemetry voltages 0.517/0.568/0.618 V,
    c_zeros, transfer 1.01865) and E83's dither through E119's module. The burst cap: E101's 66.15 +- 2.75 W (E136's frozen burst
    footing) against a cap refitted, leave-one-kind-out, on E80's and E83's kinds bursts (E126 ran no burst: every cell n_burst 0,
    so the cap E126 refitted, G2, is the sustained one and is carried as such). c per kind: from the measured c_w (calibration)
    and end to end from M7's nested D on aifoundry3 (the test)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e119"))
    import make_predictions_e119 as M119  # noqa: E402
    P136 = load(os.path.join(ROOT, "tools", "claims-v3", "e136", "predictions-e136.json"))
    rel = P136["relation"]
    B = {int(k): v for k, v in rel["B"].items()}
    SF = {int(k): v for k, v in rel["s_f"].items()}
    CZ, XFER = rel["c_zeros_w"], rel["xfer"]
    WB, SB = rel["burst"]
    G2 = P136["governor"]["G2"]
    heat136 = P136["heat"]
    cells = []
    for d in ("2026-10-31-e80-kinds-speed", "2026-10-31-e83-kinds-speed-rest"):
        for lab, c in load(os.path.join(DD, d, "results.json"))["cells"].items():
            if c.get("burst_mhz") is None or c.get("c_w") is None:
                continue
            t, n = lab.split("/")
            cells.append({"exp": d.split("-")[3].upper(), "type": t, "kind": n, "burst_mhz": float(c["burst_mhz"]), "burst_w": float(c["burst_w"]),
                          "c_w": float(c["c_w"]), "die_start": c.get("burst_die_start") or [], "die_max": c.get("burst_die_max") or []})
    n126 = sum(1 for c in load(os.path.join(DD, "2026-11-02-e126-gemm-arms", "results.json"))["cells"].values() if c.get("n_burst"))

    def levels(c):
        return {f: B[f] + c * SF[f] for f in (600, 700, 800)}

    def p_at(P, f):
        if f >= 800:
            return P[800]
        if f >= 700:
            return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]

    def clock(c, W, sig=SB):
        return M119.dither(levels(c), W, sig)[0]

    def fitW(sub):
        lo, hi = 50.0, 90.0
        e = lambda W: sum((clock(x["c_w"], W) - x["burst_mhz"]) ** 2 for x in sub)
        for _ in range(60):
            a, b = lo + (hi - lo) * 0.382, lo + (hi - lo) * 0.618
            if e(a) < e(b):
                hi = b
            else:
                lo = a
        return (lo + hi) / 2
    keys = sorted({(x["type"], x["kind"]) for x in cells})
    loo = {"E101_cap": [], "refit_cap": []}
    for kk in keys:
        tr = [x for x in cells if (x["type"], x["kind"]) != kk]
        W = fitW(tr)
        for x in cells:
            if (x["type"], x["kind"]) == kk:
                loo["E101_cap"].append(x["burst_mhz"] - clock(x["c_w"], WB))
                loo["refit_cap"].append(x["burst_mhz"] - clock(x["c_w"], W))
    W_all = fitW(cells)
    cap_choice = "refit_cap" if rms(loo["refit_cap"]) < rms(loo["E101_cap"]) else "E101_cap"
    W_use = W_all if cap_choice == "refit_cap" else WB
    # end to end: c from M7's nested D of the same kind on aifoundry3 (E78's row), then clock and board power
    e2e = {"mhz": [], "board_w": [], "rows": []}
    for x in cells:
        key = f"{x['type']}.{x['kind']}"
        Dp = row_pred_a3.get(key)
        if x["kind"] == "zeros":
            Dp = 0.0
        if Dp is None:
            continue
        c = CZ[x["type"]] + Dp / XFER
        f = clock(c, W_use)
        P = p_at(levels(c), f)
        e2e["mhz"].append(x["burst_mhz"] - f)
        e2e["board_w"].append(x["burst_w"] - P)
        e2e["rows"].append({"cell": f"{x['exp']}:{key}", "mhz_meas": x["burst_mhz"], "mhz_pred": round(f, 1), "w_meas": x["burst_w"], "w_pred": round(P, 2)})
    # (c) aifoundry2's burst heat: die_max - die_start = k (P_burst - P_idle), through the origin; the kinds bursts and E136's law
    P_IDLE = heat136["P_idle_w"]
    hb = []
    for x in cells:
        for dmx, dst in zip(x["die_max"], x["die_start"]):
            if dmx is not None and dst is not None:
                hb.append((f"{x['type']}.{x['kind']}", x["burst_w"] - P_IDLE, dmx - dst))
    for d in ("2026-11-01-e119-gemm-speed", "2026-11-02-e136-large-gemm"):
        for lab, c in load(os.path.join(DD, d, "results.json"))["cells"].items():
            for dmx, dst in zip(c.get("burst_die_max") or [], c.get("burst_die_start") or []):
                if None not in (dmx, dst, c.get("burst_w")):
                    hb.append((f"{d.split('-')[3]}:{lab}", c["burst_w"] - P_IDLE, dmx - dst))
    kin = [h for h in hb if not h[0].startswith("e1")]
    kk_all = sum(x * y for _, x, y in kin) / sum(x * x for _, x, y in kin)
    lk = []
    for kn in sorted({h[0] for h in kin}):
        tr = [h for h in kin if h[0] != kn]
        k = sum(x * y for _, x, y in tr) / sum(x * x for _, x, y in tr)
        lk += [y - k * x for n_, x, y in kin if n_ == kn]
    e136_on_kinds = [y - heat136["k_burst_c_per_w"] * x for _, x, y in kin]
    k_choice = "kinds_refit" if rms(lk) < rms(e136_on_kinds) else "E136_frozen"
    return {
        "relation": {"B_w": B, "s_f": SF, "V_v": {"600": 0.517, "700": 0.568, "800": 0.618}, "c_zeros_w": CZ, "xfer": XFER,
                     "source": "tools/claims-v3/e136/predictions-e136.json relation (E101's, through E119); V from E64's aifoundry2 telemetry (surface_hpl.py)"},
        "burst_cap": {"E101_W_star_w": WB, "sigma_w": SB, "refit_W_star_w": W_all, "loko_rms_mhz": {k: rms(v) for k, v in loo.items()},
                      "n_cells": len(cells), "n_kinds": len(keys), "chosen": cap_choice, "W_star_used_w": W_use,
                      "e126_cells_with_bursts": n126},
        "sustained_cap_G2": G2,
        "end_to_end_from_M7_nested_D": {"n": len(e2e["mhz"]), "rms_mhz": rms(e2e["mhz"]), "rms_board_w": rms(e2e["board_w"]),
                                         "q95_abs_mhz": q95(e2e["mhz"]), "q95_abs_board_w": q95(e2e["board_w"]),
                                         "bias_pred_minus_meas_w": -float(np.mean(e2e["board_w"])), "rows": e2e["rows"]},
        "burst_heat": {"P_idle_w": P_IDLE, "law": "die_max - die_start = k (P_burst - P_idle) over a kinds burst", "k_kinds_c_per_w": kk_all,
                       "k_E136_frozen_c_per_w": heat136["k_burst_c_per_w"], "loko_rms_c_kinds_refit": rms(lk), "rms_c_E136_frozen_on_kinds": rms(e136_on_kinds),
                       "q95_abs_c": q95(lk if k_choice == "kinds_refit" else e136_on_kinds), "n_runs_kinds": len(kin), "n_runs_gemm": len(hb) - len(kin),
                       "chosen": k_choice, "k_used_c_per_w": kk_all if k_choice == "kinds_refit" else heat136["k_burst_c_per_w"]},
    }


# ------------------------------------------------------------------ main
def main():
    rows, missing = assemble()
    m5 = load(os.path.join(M5D, "m5.json"))
    m6 = load(os.path.join(M6D, "m6.json"))
    res = {"_note": "Q138(m), fit_m7.py. Power: D in W over the type's zeros at 600 MHz; heat: die rise over the kinds window, C. Errors are measured - predicted.",
           "n_rows": len(rows), "experiments": sorted({r["exp"] for r in rows}), "missing": missing, "families": {}}
    frozen = {"_model": "M7 (Q138(m)): power = the bench terms of M5 plus the terms nested leave-one-kind-out kept; card term; aifoundry2's governed burst clock and power; heat per card",
              "units": "power: W over the type's own zeros at 600 MHz on aifoundry3 card 0's footing (card 1: x card1_scale_by_format); heat: C over the run's launch reading, S = board W over idle",
              "families": {}}
    nested_pred = {}
    errs = {}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        a, b, outer, e5, e6 = run_family(fr, famname, m5, m6)
        res["families"][famname] = a
        frozen["families"][famname] = b
        for i, r in enumerate(fr):
            errs[(r["exp"], r["key"])] = (float(outer[i]), float(e5[i]), float(e6[i]))
            if r["exp"] == "E78" and r["card"] == "a3":
                nested_pred[r["key"]] = r["D"] - float(outer[i])
    hr = heat_rows(rows)
    hres, hout = heat_fit(hr)
    res["heat"] = hres
    a2 = a2_governor(nested_pred)
    res["aifoundry2"] = a2
    frozen["heat"] = {"form": hres["chosen_form"], "coef": hres["coef"], "terms": HFORMS7[hres["chosen_form"]],
                      "window": "the kinds harness: a run of T_run s (4.5 s typical) from launch; ST = S x (T_run - 4.5)",
                      "interval_pool_by_format_card_c": hres["pools"], "band_k": hres["band_k"],
                      "step_response_M6": load(os.path.join(M6D, "m6.json"))["heat"]["step_response"],
                      "steady_c_per_board_w_M6": load(os.path.join(M6D, "m6.json"))["heat"]["steady_c_per_board_w"]}
    frozen["aifoundry2"] = {k: v for k, v in a2.items() if k != "end_to_end_from_M7_nested_D"}
    frozen["aifoundry2"]["end_to_end_band"] = {q: a2["end_to_end_from_M7_nested_D"][q] for q in ("q95_abs_mhz", "q95_abs_board_w", "rms_mhz", "rms_board_w", "n")}
    frozen["memory_path_E139"] = {"w_per_encoded_image": E139_W_PER_IMAGE, "pj_per_encoded_toggle": E139_PJ_PER_ENCODED_TOGGLE,
                                  "scope": "DRAM-streamed images (E132/E139's memory-path harness); zero for a kinds tile, which is a resident loop and moves no image",
                                  "out_of_sample": "E132's frozen +0.185 W per image predicted E139 to 0.028 W rms (E139 README)"}
    frozen["e138_int8_b_ratio"] = E138_ODD_OVER_EVEN
    frozen["band_rule"] = ("power: half-width = k x sqrt(pool^2 + x C x), pool = M7's nested rms for the tile's format and card, k = max(the 95th percentile of "
                           "|nested residual| / pool over M7's rows, the 95th percentile of |blind residual| / that model's own pool over blind pools 3 (M5) and 4 (M5, M6)); "
                           "heat: k_h x pool_h with k_h the 95th percentile of |nested heat residual| / pool_h; aifoundry2: the 95th percentiles of |measured - predicted| "
                           "end to end over E80's and E83's kinds bursts (clock, board W) and of the burst heat law's leave-one-kind-out residuals")
    json.dump(res, open(os.path.join(HERE, "loko-m7.json"), "w"), indent=1, default=float)
    json.dump(frozen, open(os.path.join(HERE, "m7.json"), "w"), indent=1, sort_keys=True, default=float)
    json.dump(rows, open(os.path.join(HERE, "rows-m7.json"), "w"), indent=0)
    json.dump(hr, open(os.path.join(HERE, "heat-rows-m7.json"), "w"), indent=0)
    for fam, v in res["families"].items():
        s = v["side_by_side_same_folds"]
        print(f"== {fam}: {v['n_rows']} rows {v['n_kinds']} kinds; card term {v['card_term_chosen']} {v['card_terms']}")
        for lab, x in s.items():
            print(f"  {lab:28s} all {x['all']:.3f} " + " ".join(f"{t} {x[t]['rms_w']:.3f}" for t in ("fp32", "fp16", "int8") if t in x)
                  + f" | a3 {x['card a3']['rms_w']:.3f} c1 {x['card c1']['rms_w']}")
        for fn, x in v["plain_loko_by_form"].items():
            print(f"    plain {fn:22s} {x['all']:.4f}")
        print("  picks", s["M7_nested_loko"]["inner_picks"], "chosen", v["chosen_form"], v["kept_rule"])
        print("  coef fJ", {k: round(c, 3) for k, c in v["fit_on_all"]["coef_fJ"].items()}, "se", {k: round(c, 3) for k, c in v["fit_on_all"]["coef_jackknife_se_fJ"].items()})
        print("  drops", v["drop_one_term"])
        print("  E115/E140 by exp", {e: v["by_experiment"][e] for e in ("E115", "E140", "E137") if e in v["by_experiment"]})
        bc = v["band_calibration"]
        print("  band k", round(bc["k"], 3), "z_nested_q95", round(bc["z_nested_q95"], 3), "z_blind_q95", bc["z_blind_q95"], bc["blind_sets"], bc["coverage_of_rule_on_M7_nested"])
        print("  pools", {k: (round(p["rms_w"], 3) if p["rms_w"] else None, p["n"]) for k, p in bc["pools"].items()})
    h = res["heat"]
    print("== heat", h["n_rows"], "rows; prior", {t: round(h["before_prior_rule_0118"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")},
          "M6", {t: round(h["M6_frozen_coefficients"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")},
          "nested", {t: round(h["nested_loko"][t]["rms_c"], 3) for t in ("fp32", "fp16", "int8")}, h["nested_loko"]["inner_picks"], h["chosen_form"], h["coef"], "k", round(h["band_k"], 3))
    print("   E140 rows", h["E140_rows_nested"], "cards", {c: h["nested_loko"][c] for c in h["cards"]})
    a = res["aifoundry2"]
    print("== aifoundry2 burst cap", {k: v for k, v in a["burst_cap"].items()})
    print("   end to end", {k: v for k, v in a["end_to_end_from_M7_nested_D"].items() if k != "rows"})
    print("   heat", a["burst_heat"])
    print("missing", len(missing), missing[:20])


if __name__ == "__main__":
    main()
