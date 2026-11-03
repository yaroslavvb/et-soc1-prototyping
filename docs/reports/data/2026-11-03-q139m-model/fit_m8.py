#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q139(m): M8 = M7's structure on Q139(u)'s one footing, refitted on every public kinds row (M7u's 637, blind pool 5 on
aifoundry3 (E141) and card 1 (E142), E147's single-bit steps), plus only the candidate terms that lower the nested error;
aifoundry2's governed bursts (E80, E83, E143) with its zeros level, a D scale per format and a cap rising with overshoot, each
kept only if it lowers both the clock and the board leave-one-kind-out rms; the peak board power; and the card-scale
predictor from cheap reads, tested leave one card out. Everything follows M8-REGISTRATION.md (committed f640fb7a before this
file existed). Frozen before blind pool 6 exists.

    python3 fit_m8.py <scratch dir>     # writes m8.json, nested-m8.json, rows-m8.json beside it (a few minutes)

SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "6")
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M7D = os.path.join(DD, "2026-11-02-q138m-model")
FOOT = os.path.join(DD, "2026-11-03-q139u-footing")
B5 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind5")
E147D = os.path.join(DD, "2026-11-02-e147-bit-prices-rest")
CV = os.path.join(ROOT, "tools", "claims-v3")
for _p in (M7D, FOOT, B5, E147D, os.path.join(CV, "e119")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import fit_m7 as M7  # noqa: E402  (imports fit_m6, m6_rows, fit_m5 unchanged)
import reduce_footing as RF  # noqa: E402
import make_blind5 as MB  # noqa: E402
import posthoc_m7_e147 as P147  # noqa: E402

F, mk, M6 = M7.F, M7.mk, M7.M6
MB.mk = mk
load = lambda p: json.load(open(p))  # noqa: E731
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha(open(p, "rb").read())  # noqa: E731
rms = F.rms
K_A3 = RF.K_FROZEN["a3"]
HEAT_A3 = 0.1186                     # M7's frozen die rise per board W on aifoundry3 (m7.json heat.coef S|aifoundry3, 0.11855)
E147_FOOTING_FACTOR = 1.0 - K_A3 * HEAT_A3
POOL_EXPS = ("E115", "E140", "E141", "E142")

# ------------------------------------------------------------------ candidate features (M8-REGISTRATION.md section 3)
_P145 = load(os.path.join(CV, "e145", "predictions-e145.json"))["card0_prices_rail_fJ"]["B"]
_W = [float(_P145[f"b1_{j}"]) for j in range(7)]
_W.append((_W[1] + _W[3] + _W[5]) / 3.0)
W_BPOS = [w / (sum(_W) / 8.0) for w in _W]
_CACHE = {}


def c_feats(raw, t):
    """Q138(b)'s C-register descriptors (make_blind5.c_check's c_start and c_launch_end_est, the same code path)."""
    A, B = mk.decode(raw, t)
    a, b = (A.astype(np.int64), B.astype(np.int64)) if t == "int8" else (A.astype(np.float64), B.astype(np.float64))
    steps, applies = MB.steps_of(a, b, t)
    zero = np.zeros((MB.N, MB.N), dtype=np.int64 if t == "int8" else np.float32)
    with np.errstate(over="ignore", invalid="ignore"):
        c1, _, _ = MB.run_op(zero, steps, applies, t)
        _, _, fs = MB.run_op(c1, steps, applies, t)
        n = MB.N_END[t]
        if t == "int8":
            d = sum(steps).astype(np.int64)
            c0 = ((d * n + (1 << 31)) % (1 << 32) - (1 << 31)).astype(np.int64)
        else:
            d = sum(steps) if applies is None else sum(np.where(ap, s, 0.0) for s, ap in zip(steps, applies))
            c0 = (d * float(n)).astype(np.float32)
        _, _, fe = MB.run_op(c0, steps, applies, t)
    return {"c_start": float(fs), "c_end": float(fe)}


def byte_feats(raw, t):
    if t != "int8":
        return {"bpos": 0.0, "bsat": 0.0, "absat": 0.0}
    aw, bw = mk.words_of(raw)
    a, b = mk.issue_streams_fast(aw, bw, t)
    a64, b64 = a.astype(np.uint64), b.astype(np.uint64)
    da = a64 ^ np.roll(a64, -1)
    db = b64 ^ np.roll(b64, -1, axis=0)
    pc = lambda x: mk.popcount32(np.asarray(x, dtype=np.uint64).astype(np.uint32))  # noqa: E731
    slots = mk.COLUMN_SLOTS[t]
    bpos = sum(W_BPOS[j] * float(pc(db & np.uint64(0x01010101 << j)).sum()) for j in range(8))

    def sat(x):
        s = 0.0
        for e in range(4):
            p = pc((x >> np.uint64(8 * e)) & np.uint64(0xFF))
            s += float(np.where(p >= 7, p, 0).sum())
        return s
    sb = sat(db)
    return {"bpos": bpos, "bsat": sb, "absat": sb + sat(da) * slots}


def m8_extra(path, t):
    raw = open(path, "rb").read()
    h = sha(raw)
    if (h, t) not in _CACHE:
        f = c_feats(raw, t)
        f.update(byte_feats(raw, t))
        _CACHE[(h, t)] = f
    return dict(_CACHE[(h, t)])


def finish(f):
    f["xfld"] = float(f.get("a_exp", 0.0)) + float(f.get("b_exp", 0.0))
    return f


# ------------------------------------------------------------------ rows (section 2)
def assemble(scratch):
    rows = load(os.path.join(FOOT, "rows-m7u.json"))
    missing = []
    for r in rows:
        r["f"].update(m8_extra(os.path.join(ROOT, r["tile_path"]), r["type"]))
        finish(r["f"])
    by_sha = {}
    for r in rows:
        by_sha.setdefault(r["tile_sha256"], r)
    man = load(os.path.join(B5, "blind5.json"))["tiles"]
    feats5 = load(os.path.join(B5, "predictions-blind5-aifoundry3.json"))["tiles"]
    for exp, card, red in (("E141", "a3", "e141-footing.json"), ("E142", "c1", "e142-footing.json")):
        items = load(os.path.join(FOOT, "reduced", red))["items"]
        for meta in man:
            if meta.get("anchor"):
                continue
            name, t = meta["name"], meta["type"]
            it = items.get(name)
            if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                missing.append(f"{exp}:{name} (no D at the footing)")
                continue
            p = os.path.join(B5, meta["file"])
            h = fsha(p)
            f = dict(feats5[name]["features"])
            f.update(m8_extra(p, t))
            finish(f)
            lab = by_sha[h]["kind"] if h in by_sha else f"{t}.blind5:{name.split('.', 1)[1]}"
            rows.append({"exp": exp, "card": card, "key": name, "type": t, "kind": lab, "tile_sha256": h,
                         "tile_path": os.path.relpath(p, ROOT), "D": float(it["D"]["mean"]), "D_se": it["D"].get("se"),
                         "rate": float(it["rate"]["mean"]), "f": f, "dT_win": (it.get("dT_win") or {}).get("mean"),
                         "case": meta.get("case")})
    # E147: steps over each item's own zero, A2's 4 W line, the footing's leakage on the step
    pool = os.path.join(scratch, "e147-pool")
    P147.build_pool(pool)
    spec = {m["name"]: m for m in load(os.path.join(pool, "blind5.json"))["tiles"]}
    counts = load(os.path.join(pool, "counts-e147-merged.json"))["rows"]
    pr = load(os.path.join(CV, "e147", "predictions-e147.json"))["items"]
    sc = load(os.path.join(E147D, "scored.json"))["arms"]["dips_4w"]["prices"]
    red = load(os.path.join(E147D, "e147-dips4.json"))["items"]
    zeros = M7.zeros_counts()
    fcache = {}

    def fvec(name):
        if name not in fcache:
            p = os.path.normpath(os.path.join(pool, spec[name]["file"]))
            crow = counts.get(name) or counts.get(P147.bare(name))
            f = M7.feats_from_counts(crow, p, "fp32", zeros)
            f.update(m8_extra(p, "fp32"))
            fcache[name] = (finish(f), p)
        return fcache[name]
    for item, v in sorted(sc.items()):
        name = "fp32." + item
        if name not in pr or v.get("W", {}).get("mean") is None:
            missing.append(f"E147:{item} (no step)")
            continue
        z = pr[name]["zero"]
        (fi, p), (fz, _) = fvec(name), fvec(z)
        f = {k: float(fi[k]) - float(fz[k]) for k in fi if k in fz and isinstance(fi[k], (int, float)) and not isinstance(fi[k], bool)}
        rate = float(red[name]["rate"]["mean"]) if name in red and red[name].get("rate", {}).get("mean") else F.RATE["fp32"]
        h147 = fsha(p)
        rows.append({"exp": "E147", "card": "a3", "key": name, "type": "fp32",
                     "kind": by_sha[h147]["kind"] if h147 in by_sha else f"fp32.e147:{item}",
                     "tile_sha256": h147, "tile_path": os.path.relpath(p, ROOT) if p.startswith(ROOT) else p,
                     "D": float(v["W"]["mean"]) * E147_FOOTING_FACTOR, "D_se": v["W"].get("se"), "rate": rate, "f": f,
                     "zero": z, "step_W_dips4w": float(v["W"]["mean"])})
    return rows, missing


# ------------------------------------------------------------------ forms (section 4)
BF, BI = M7.BASE_F, M7.BASE_I
FORMS8 = {
    "float": {"G8_gtr_glive": BF + ["gtr", "glive"], "G11_gtr_glive_exp": BF + ["gtr", "glive", "a_exp", "b_exp"],
              "G12_xfld": BF + ["gtr", "glive", "xfld"], "G13_cend": BF + ["gtr", "glive", "c_end"],
              "G14_cstart": BF + ["gtr", "glive", "c_start"], "G15_xfld_cend": BF + ["gtr", "glive", "xfld", "c_end"]},
    "int8": {"J8_b138": BI + ["b138"], "J12_bpos": BI + ["bpos"], "J13_bsat": BI + ["b138", "bsat"],
             "J14_absat": BI + ["b138", "absat"], "J15_cend": BI + ["b138", "c_end"], "J16_bpos_bsat": BI + ["bpos", "bsat"]},
}
M7FORM = {"float": "G8_gtr_glive", "int8": "J8_b138"}
REFFORMS = {"float": {"M6_form": M7.FORMS["float"]["G6_M6"], "M5_form": M7.FORMS["float"]["G0_M5"]},
            "int8": {"M6_form": M7.FORMS["int8"]["J1_M6"], "M5_form": M7.FORMS["int8"]["J0_M5"]}}


def frozen_pred(rows, mod, by_format):
    X = F.X_of(rows, mod["terms"])
    s = np.array([(mod["card1_scale_by_format"][r["type"]] if by_format else mod["card1_scale"]) if r["card"] == "c1" else 1.0
                  for r in rows])
    return X @ np.array(mod["coef_J"]) * s


def boot_diff(kid, ea, eb, n=2000, seed=139):
    """rms(ea) - rms(eb) with a bootstrap over kinds (95%)"""
    kid = np.unique(kid, return_inverse=True)[1]
    K = int(kid.max()) + 1
    sa, sb, nn = np.zeros(K), np.zeros(K), np.zeros(K)
    ok = ~np.isnan(ea) & ~np.isnan(eb)
    np.add.at(sa, kid[ok], ea[ok] ** 2)
    np.add.at(sb, kid[ok], eb[ok] ** 2)
    np.add.at(nn, kid[ok], 1)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(n):
        i = rng.integers(0, K, K)
        d.append(math.sqrt(sa[i].sum() / nn[i].sum()) - math.sqrt(sb[i].sum() / nn[i].sum()))
    pt = math.sqrt(sa.sum() / nn.sum()) - math.sqrt(sb.sum() / nn.sum())
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"d_rms_w": pt, "lo95": float(lo), "hi95": float(hi), "resolved": bool(hi < 0 or lo > 0)}


def run_family(rows, famname, m6, m7):
    out = {}
    base = M7.FORMS[famname][M7.BASE_FORM[famname]]
    card, rel = {}, []
    ref = M7.Fam(rows, {"G": base}, "C1_allpairs_family")
    for ct in M7.CARD_TERMS:
        fam = M7.Fam(rows, {"G": base}, ct)
        errs = []
        for k in range(ref.K):
            for j, f in enumerate(ref.fmts):
                if ref.npair[k, j]:
                    s = fam.scales(np.array([k]))[0, j]
                    a = math.sqrt(ref.Dn[k, j])
                    errs.append(ref.N[k, j] / a - s * a)
                    if ct == M7.CARD_TERMS[0]:
                        rel.append(ref.N[k, j] / a / a)
        card[ct] = {"loko_rms_w": rms(errs), "n_pairs_scored": len(errs), "n_pairs_fitted": int(fam.npair.sum()),
                    "scale_by_format": dict(zip([str(x) for x in fam.fmts], [float(x) for x in fam.scales()[0]]))}
    card["_pair_ratio_c1_over_a3"] = {"mean": float(np.mean(rel)), "sd": float(np.std(rel)), "median": float(np.median(rel)), "n": len(rel)}
    best_ct = min(M7.CARD_TERMS, key=lambda c: card[c]["loko_rms_w"])
    out["card_terms"], out["card_term_chosen"] = card, best_ct
    forms = {**FORMS8[famname], **REFFORMS[famname]}
    fam = M7.Fam(rows, forms, best_ct)
    e6 = fam.y - frozen_pred(rows, m6["families"][famname], False)
    e7 = fam.y - frozen_pred(rows, m7["families"][famname], True)
    plain = {fn: fam.loko(fn) for fn in forms}
    outer = np.full(len(fam.y), np.nan)
    picks = {}
    for k in range(fam.K):
        sc = {fn: rms(fam.loko(fn, k)) for fn in FORMS8[famname]}
        best = min(sc, key=sc.get)
        b, s = fam.fit_all(best, [k])
        m = fam.kid == k
        outer[m] = fam.y[m] - fam.pred_rows(best, b, s, m)
        picks[best] = picks.get(best, 0) + 1
    sel = {fn: rms(plain[fn]) for fn in FORMS8[famname]}
    chosen = min(sel, key=sel.get)
    nested_rms, m7form_rms = rms(outer), rms(plain[M7FORM[famname]])
    kept_rule = "chosen form (the procedure's nested error is below M7's form on the same folds)"
    if not nested_rms < m7form_rms:
        chosen = M7FORM[famname]
        kept_rule = "M7's form (the procedure did not lower the nested error below M7's form on the same folds)"
    drops = {}
    for q in FORMS8[famname][chosen]:
        if q in FORMS8[famname][M7FORM[famname]]:
            continue
        sub = [x for x in FORMS8[famname][chosen] if x != q]
        drops[q] = {"plain_loko_without_w": rms(M7.Fam(rows, {"S": sub}, best_ct).loko("S")), "plain_loko_with_w": sel[chosen]}
    b, s = fam.fit_all(chosen, [])
    C = fam.jackknife_cov(chosen)
    coefJ = fam.coef_J(chosen, b)
    exps = np.array([r["exp"] for r in rows])
    cards = np.array([r["card"] for r in rows])
    errsets = {"M8_nested": outer, "M7_form_loko": plain[M7FORM[famname]], "M6_form_loko": plain["M6_form"],
               "M5_form_loko": plain["M5_form"], "M7_frozen": e7, "M6_frozen": e6}

    def by(mask):
        return {lab: {"rms_w": rms(e[mask]), "bias_meas_minus_pred_w": float(np.nanmean(e[mask])) if mask.any() else None,
                      "n": int(np.sum(mask & ~np.isnan(e)))} for lab, e in errsets.items()}
    rep = {"all": by(np.ones(len(rows), bool))}
    for t in fam.fmts:
        rep[t] = by(fam.tys == t)
        for cd in ("a3", "c1"):
            rep[f"{t}|{cd}"] = by((fam.tys == t) & (cards == cd))
    for e in sorted(set(exps)):
        rep[f"exp {e}"] = by(exps == e)
    rep["rows outside E141/E142/E147"] = by(~np.isin(exps, ["E141", "E142", "E147"]))
    paired = {lab: boot_diff(fam.kid, outer, e) for lab, e in errsets.items() if lab != "M8_nested"}
    paired_pool = {}
    for lab in ("M7_form_loko", "M6_form_loko", "M7_frozen", "M6_frozen"):
        msk = np.isin(exps, ["E141", "E142"])
        paired_pool[lab] = boot_diff(fam.kid[msk], outer[msk], errsets[lab][msk]) if msk.any() else None
    # bands (section 4): pools by format and card, k = max(q95 over all rows, q95 over pools 3-5's rows)
    pools = {}
    for t in fam.fmts:
        for cd in ("a3", "c1"):
            e = outer[(fam.tys == t) & (cards == cd)]
            pools[f"{t}|{cd}"] = {"rms_w": rms(e), "n": int(np.sum(~np.isnan(e))), "q95_abs_w": M7.q95(e)}
    z = np.array([abs(outer[i]) / pools[f"{fam.tys[i]}|{cards[i]}"]["rms_w"] if pools[f"{fam.tys[i]}|{cards[i]}"]["rms_w"] else np.nan
                  for i in range(len(rows))])
    pm = np.isin(exps, POOL_EXPS)
    ki, kii = float(np.nanquantile(z, 0.95)), float(np.nanquantile(z[pm], 0.95))
    kband = max(ki, kii)
    loo_in = 0
    for i in np.where(pm & ~np.isnan(z))[0]:
        zz = np.delete(z, i)
        pp = np.delete(pm, i)
        kk = max(float(np.nanquantile(zz, 0.95)), float(np.nanquantile(zz[pp], 0.95)))
        loo_in += int(z[i] <= kk)
    cover = {lab: {"inside": int(np.sum(z[m] <= kband)), "n": int(np.sum(m & ~np.isnan(z)))}
             for lab, m in (("all", np.ones(len(rows), bool)), ("pool rows (E115, E140, E141, E142)", pm),
                            ("E141", exps == "E141"), ("E142", exps == "E142"), ("E147", exps == "E147"))}
    cover["pool rows, each left out of k"] = {"inside": loo_in, "n": int(np.sum(pm & ~np.isnan(z)))}
    misses = sorted([{"exp": r["exp"], "card": r["card"], "key": r["key"], "D": r["D"], "M8_nested_err_w": float(outer[i]),
                      "M7_frozen_err_w": float(e7[i]), "M7_form_loko_err_w": float(plain[M7FORM[famname]][i])}
                     for i, r in enumerate(rows)], key=lambda x: -abs(x["M8_nested_err_w"]))[:20]
    watch = [{"exp": r["exp"], "card": r["card"], "key": r["key"], "D": round(r["D"], 4),
              **{lab: round(float(e[i]), 4) for lab, e in errsets.items()}}
             for i, r in enumerate(rows) if r["exp"] in ("E141", "E142") or r["key"] in ("int8.b_line_flipflop",)]
    out.update({
        "n_rows": len(rows), "n_kinds": fam.K, "forms": forms,
        "plain_loko_by_form": {fn: M7.split(fam, e) for fn, e in plain.items()},
        "M8_nested": {**M7.split(fam, outer), "inner_picks": picks},
        "same_folds": rep, "paired_bootstrap_over_kinds_M8_minus": paired,
        "paired_bootstrap_pool5_rows_M8_minus": paired_pool,
        "chosen_form": chosen, "kept_rule": kept_rule, "chosen_terms": FORMS8[famname][chosen], "drop_one_term": drops,
        "band": {"pools": pools, "k_i_all_rows_q95": ki, "k_ii_pool_rows_q95": kii, "k": kband, "coverage": cover},
        "largest_nested_misses": misses, "pool5_rows": watch,
    })
    frozen = {"form": chosen, "terms": FORMS8[famname][chosen], "coef_J": [float(x) for x in coefJ],
              "coef_fJ": dict(zip(FORMS8[famname][chosen], [float(x) * 1e15 for x in coefJ])),
              "coef_jackknife_se_fJ": dict(zip(FORMS8[famname][chosen], [float(x) * 1e15 for x in np.sqrt(np.diag(C))])),
              "cov_J2": C.tolist(), "card_term": best_ct, "card1_scale_by_format": dict(zip(fam.fmts, [float(x) for x in s])),
              "interval_pool_by_format_card": pools, "band_k": kband, "n_rows": len(rows), "n_kinds": fam.K}
    return out, frozen, outer


# ------------------------------------------------------------------ aifoundry2 (section 5)
def a2_fit(nested_D):
    import make_predictions_e119 as M119  # noqa: E402
    P136 = load(os.path.join(CV, "e136", "predictions-e136.json"))
    rel = P136["relation"]
    B = {int(k): v for k, v in rel["B"].items()}
    SF = {int(k): v for k, v in rel["s_f"].items()}
    CZ7, XFER = dict(rel["c_zeros_w"]), rel["xfer"]
    SB = rel["burst"][1]
    m7 = load(os.path.join(M7D, "m7.json"))
    W7 = m7["aifoundry2"]["burst_cap"]["W_star_used_w"]
    d78 = load(os.path.join(FOOT, "reduced", "e78-footing.json"))["items"]
    d141 = load(os.path.join(FOOT, "reduced", "e141-footing.json"))["items"]
    cells = []
    for d in ("2026-10-31-e80-kinds-speed", "2026-10-31-e83-kinds-speed-rest"):
        for lab, c in load(os.path.join(DD, d, "results.json"))["cells"].items():
            if c.get("burst_mhz") is None or c.get("c_w") is None:
                continue
            t, n = lab.split("/")
            key = f"{t}.{n}"
            it = d78.get(key) or {}
            Dm = 0.0 if n == "zeros" else ((it.get("D") or {}).get("mean"))
            cells.append({"exp": d.split("-")[3].upper(), "type": t, "kind": key, "src_key": key, "burst_mhz": float(c["burst_mhz"]),
                          "burst_w": float(c["burst_w"]), "c_w": float(c["c_w"]), "p800_w": c.get("burst_p800_w"),
                          "D600_meas": Dm, "zero": n == "zeros"})
    r143 = load(os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "results.json"))
    for lab, c in r143["cells"].items():
        if "name" in c:
            name, t = c["name"], c["type"]
            it = d141.get(name) or {}
        else:                                   # the session link: E80's own kinds re-run in E143's session (k-<type>-<kind>)
            _, t, n = lab.split("-", 2)
            name = f"{t}.{n}"
            it = d78.get(name) or {}
        z = name.endswith("zeros")
        Dm = 0.0 if z else ((it.get("D") or {}).get("mean"))
        cells.append({"exp": "E143", "type": t, "kind": name, "src_key": name, "burst_mhz": float(c["burst_mhz"]),
                      "burst_w": float(c["burst_w"]), "c_w": float(statistics.mean(c["c_w_runs"])),
                      "p800_w": float(statistics.mean(c["p800_w_runs"])), "D600_meas": Dm, "zero": z,
                      "governed_E143": c.get("group")})
    cells = [c for c in cells if c["D600_meas"] is not None]
    kinds = sorted({c["kind"] for c in cells})
    WG = np.arange(55.0, 80.0001, 0.1)

    def levels(c):
        return {f: B[f] + c * SF[f] for f in (600, 700, 800)}

    def clock(c, W):
        return M119.dither(levels(c), W, SB)[0]

    def p_at(P, f):
        if f >= 800:
            return P[800]
        if f >= 700:
            return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0 if f >= 600 else P[600]
    curves = np.array([[clock(c["c_w"], W) for W in WG] for c in cells])     # each cell's clock against a constant cap
    P8m = np.array([B[800] + c["c_w"] * SF[800] for c in cells])
    meas_f = np.array([c["burst_mhz"] for c in cells])

    def clk_at(idx, Wv):
        u = (np.clip(Wv, WG[0], WG[-1]) - WG[0]) / 0.1
        j = np.clip(u.astype(int), 0, len(WG) - 2)
        fr = u - j
        return curves[idx, j] * (1.0 - fr) + curves[idx, j + 1] * fr

    def capW(P8, W0, g):
        return W0 + g * np.maximum(0.0, P8 - W0)

    def fit_cap(idx, overshoot):
        best = None
        for g in (np.linspace(0.0, 0.6, 25) if overshoot else [0.0]):
            for W0 in np.arange(55.0, 75.0001, 0.1):
                e = np.sum((clk_at(idx, capW(P8m[idx], W0, g)) - meas_f[idx]) ** 2)
                if best is None or e < best[0]:
                    best = (e, W0, g)
        return best[1], best[2]

    def fit_params(train, cfg):
        idx = np.array(train)
        cz = dict(CZ7)
        if cfg["zeros"]:
            for t in ("fp32", "fp16", "int8"):
                v = [cells[i]["c_w"] for i in idx if cells[i]["zero"] and cells[i]["type"] == t]
                if v:
                    cz[t] = float(np.mean(v))
        g = {t: 1.0 / XFER for t in ("fp32", "fp16", "int8")}
        if cfg["dscale"]:
            for t in g:
                q = [(cells[i]["c_w"] - cz[t], cells[i]["D600_meas"]) for i in idx if not cells[i]["zero"] and cells[i]["type"] == t and cells[i]["D600_meas"] > 0.5]
                if q:
                    g[t] = sum(a * d for a, d in q) / sum(d * d for a, d in q)
        W0, gam = fit_cap(idx, cfg["overshoot"])
        return {"c_zeros_w": cz, "g": g, "W0": W0, "gamma": gam}

    def predict(par, t, D):
        c = par["c_zeros_w"][t] + par["g"][t] * D
        P8 = B[800] + c * SF[800]
        W = float(capW(P8, par["W0"], par["gamma"]))
        f = clock(c, W)
        P = p_at(levels(c), f)
        cz = par["c_zeros_w"][t]
        Wz = float(capW(B[800] + cz * SF[800], par["W0"], par["gamma"]))
        fz = clock(cz, Wz)
        return {"c": c, "mhz": f, "board_w": P, "D_burst_w": P - p_at(levels(cz), fz), "P800_w": P8, "W_star": W}
    res = {"n_cells": len(cells), "n_kinds": len(kinds), "by_config": {}}
    loko_err = {}

    def run_cfg(lab, cfg):
        em, ew, rowsout = [], [], []
        for kk in kinds:
            tr = [i for i, c in enumerate(cells) if c["kind"] != kk]
            par = fit_params(tr, cfg)
            for i, c in enumerate(cells):
                if c["kind"] != kk:
                    continue
                pr = predict(par, c["type"], c["D600_meas"])
                em.append(c["burst_mhz"] - pr["mhz"])
                ew.append(c["burst_w"] - pr["board_w"])
                rowsout.append({"exp": c["exp"], "kind": kk, "gov": c["burst_mhz"] < 795, "mhz_err": em[-1], "w_err": ew[-1]})
        em, ew = np.array(em), np.array(ew)
        gov = np.array([x["gov"] for x in rowsout])
        e143 = np.array([x["exp"] == "E143" for x in rowsout])
        res["by_config"][lab] = {"cfg": dict(cfg), "loko_rms_mhz": rms(em), "loko_rms_board_w": rms(ew),
                                 "governed": {"n": int(gov.sum()), "rms_mhz": rms(em[gov]), "rms_board_w": rms(ew[gov]), "bias_board_meas_minus_pred_w": float(np.mean(ew[gov]))},
                                 "pinned": {"n": int((~gov).sum()), "rms_mhz": rms(em[~gov]), "rms_board_w": rms(ew[~gov]), "bias_board_meas_minus_pred_w": float(np.mean(ew[~gov]))},
                                 "E143_cells": {"n": int(e143.sum()), "rms_mhz": rms(em[e143]), "rms_board_w": rms(ew[e143])},
                                 "params_all": fit_params(list(range(len(cells))), cfg)}
        loko_err[lab] = rowsout
        return res["by_config"][lab]
    # selection (section 5): terms added in order; each kept only if it lowers both LOKO rms against the configuration kept so far
    cur_cfg = {"zeros": False, "dscale": False, "overshoot": False}
    kept = "A0_M7_form_refit_cap"
    cur = run_cfg(kept, cur_cfg)
    steps = []
    for term, lab in (("zeros", "zeros_level"), ("dscale", "D_scale_per_format"), ("overshoot", "cap_rising_with_overshoot")):
        cand = dict(cur_cfg, **{term: True})
        clab = "+".join([k for k in ("zeros", "dscale", "overshoot") if cand[k]])
        new = run_cfg(clab, cand)
        ok = new["loko_rms_mhz"] < cur["loko_rms_mhz"] and new["loko_rms_board_w"] < cur["loko_rms_board_w"]
        steps.append({"term": lab, "against": kept, "config": clab, "kept": bool(ok), "loko_rms_mhz": [cur["loko_rms_mhz"], new["loko_rms_mhz"]],
                      "loko_rms_board_w": [cur["loko_rms_board_w"], new["loko_rms_board_w"]]})
        if ok:
            cur_cfg, cur, kept = cand, new, clab
    cfg_kept = dict(cur_cfg)
    par = fit_params(list(range(len(cells))), cfg_kept)
    # end to end from M8's nested D (the cells whose kind has a nested D on aifoundry3)
    e2e = {"mhz": [], "w": [], "rows": []}
    for c in cells:
        Dp = 0.0 if c["zero"] else nested_D.get(c["src_key"])
        if Dp is None:
            continue
        pr = predict(par, c["type"], Dp)
        e2e["mhz"].append(c["burst_mhz"] - pr["mhz"])
        e2e["w"].append(c["burst_w"] - pr["board_w"])
        e2e["rows"].append({"exp": c["exp"], "kind": c["kind"], "mhz_meas": c["burst_mhz"], "mhz_pred": round(pr["mhz"], 1),
                            "w_meas": c["burst_w"], "w_pred": round(pr["board_w"], 2), "gov": c["burst_mhz"] < 795})
    gm = np.array([x["gov"] for x in e2e["rows"]])
    em, ew = np.array(e2e["mhz"]), np.array(e2e["w"])
    # side by side, reported only: M7's frozen relation (c_zeros, 1/1.01865, W* 65.58 W) through the same nested D on the same cells
    par7 = {"c_zeros_w": dict(CZ7), "g": {t: 1.0 / XFER for t in ("fp32", "fp16", "int8")}, "W0": W7, "gamma": 0.0}
    e7m, e7w = [], []
    for c in cells:
        Dp = 0.0 if c["zero"] else nested_D.get(c["src_key"])
        if Dp is None:
            continue
        pr = predict(par7, c["type"], Dp)
        e7m.append(c["burst_mhz"] - pr["mhz"])
        e7w.append(c["burst_w"] - pr["board_w"])
    e7m, e7w = np.array(e7m), np.array(e7w)
    m7_same = {"n": len(e7m), "rms_mhz": rms(e7m), "rms_board_w": rms(e7w),
               "governed": {"rms_mhz": rms(e7m[gm]), "rms_board_w": rms(e7w[gm]), "bias_board_meas_minus_pred_w": float(np.mean(e7w[gm]))},
               "pinned": {"rms_mhz": rms(e7m[~gm]), "rms_board_w": rms(e7w[~gm])},
               "what": "M7's frozen aifoundry2 relation through M8's nested D, same cells (reported, not a selection input)"}
    # M7 as frozen on the same cells, from M7's frozen relation and the same nested D (for the side by side)
    # peak board power: E143's traces
    peaks = []
    rr = {x["run"]: x for x in r143["run_rows"]}
    tdir = os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "aifoundry2", "s1", "tel")
    for fn in sorted(os.listdir(tdir)):
        run = fn.split(".jsonl")[0]
        x = rr.get(run)
        if x is None or x.get("c_w") is None:
            continue
        bw = [json.loads(ln).get("board_w") for ln in gzip.open(os.path.join(tdir, fn), "rt") if ln.startswith("{")]
        bw = [v for v in bw if v is not None]
        if not bw:
            continue
        P8 = B[800] + float(x["c_w"]) * SF[800]
        peaks.append({"run": run, "peak_w": max(bw), "P800_pred_from_c_w": P8, "excess_w": max(bw) - P8, "p800_w": x.get("p800_w")})
    ex = np.array([p["excess_w"] for p in peaks])
    peak = {"n_runs": len(peaks), "excess_median_w": float(np.median(ex)), "excess_q95_w": float(np.quantile(ex, 0.95)),
            "excess_max_w": float(ex.max()), "highest_peak_w": max(p["peak_w"] for p in peaks),
            "rule": "predicted peak = B(800) + c x s(800) + excess (median: expected; q95: the 95% upper value, with c at D's band top)",
            "source": "E143's 117 committed traces (aifoundry2/s1/tel); E80's and E83's traces are not in the tree"}
    q = lambda v: M7.q95(np.array(v))  # noqa: E731
    out = {"relation": {"B_w": B, "s_f": SF, "sigma_w": SB, "source": "tools/claims-v3/e136/predictions-e136.json relation (E101's, through E119)"},
           "footing": "dips kept in training and test alike (E80's, E83's and E143's committed kspeed reductions); Q139(u) F4",
           "configs": res, "selection_steps": steps, "kept_config": kept, "params": par,
           "end_to_end_from_M8_nested_D": {"n": len(em), "rms_mhz": rms(em), "rms_board_w": rms(ew), "q95_abs_mhz": q(em), "q95_abs_board_w": q(ew),
                                            "governed": {"n": int(gm.sum()), "rms_mhz": rms(em[gm]), "rms_board_w": rms(ew[gm]), "bias_board_meas_minus_pred_w": float(np.mean(ew[gm])) if gm.any() else None},
                                            "pinned": {"n": int((~gm).sum()), "rms_mhz": rms(em[~gm]), "rms_board_w": rms(ew[~gm])}, "rows": e2e["rows"]},
           "bands": {"q95_abs_mhz_loko": q([x["mhz_err"] for x in loko_err[kept]]), "q95_abs_board_w_loko": q([x["w_err"] for x in loko_err[kept]]),
                     "q95_abs_mhz_e2e": q(em), "q95_abs_board_w_e2e": q(ew)},
           "M7_frozen_relation_same_cells": m7_same,
           "peak": peak, "peaks": peaks,
           "burst_heat": m7["aifoundry2"]["burst_heat"],
           "M7_frozen": {"c_zeros_w": CZ7, "xfer": XFER, "W_star_w": W7}}
    # the measured aifoundry2 scale for the card-scale test: (c_w - c_zeros) / D600 on cells with D600 >= 5 W (floats) / 1 W (int8)
    sc = {"floats": [], "int8": []}
    for c in cells:
        if c["zero"]:
            continue
        fam = "int8" if c["type"] == "int8" else "floats"
        if c["D600_meas"] >= (1.0 if fam == "int8" else 5.0):
            sc[fam].append((c["c_w"] - par["c_zeros_w"][c["type"]]) / c["D600_meas"])
    out["scale_vs_a3"] = {k: {"median": float(np.median(v)), "n": len(v), "iqr": [float(np.quantile(v, 0.25)), float(np.quantile(v, 0.75))]} for k, v in sc.items() if v}
    return out


# ------------------------------------------------------------------ card-scale predictor (section 6)
def card_scale(rows, a2scale, a2cz):
    sv = load(os.path.join(DD, "2026-11-03-q139s-clock-voltage", "clock-voltage.json"))["cross_card_v2_at_600"]["V600_v"]
    fp = load(os.path.join(FOOT, "footing.json"))["slopes"]
    e141 = load(os.path.join(FOOT, "reduced", "e141-footing.json"))
    e142 = load(os.path.join(FOOT, "reduced", "e142-footing.json"))
    P136 = load(os.path.join(CV, "e136", "predictions-e136.json"))["relation"]
    # measured scale card 1 / aifoundry3: paired kinds on the footing
    by = {}
    for r in rows:
        if r["exp"] == "E147":
            continue
        by.setdefault((r["kind"], r["type"]), {}).setdefault(r["card"], []).append(r["D"])
    rat = {"floats": [], "int8": []}
    for (k, t), d in by.items():
        if "a3" in d and "c1" in d:
            a, c = float(np.mean(d["a3"])), float(np.mean(d["c1"]))
            fam = "int8" if t == "int8" else "floats"
            if a >= (1.0 if fam == "int8" else 5.0):
                rat[fam].append(c / a)
    meas = {"a3": {"floats": 1.0, "int8": 1.0},
            "c1": {k: float(np.median(v)) for k, v in rat.items()},
            "a2": {k: v["median"] for k, v in a2scale.items()}}
    zl = lambda e, t: e["items"][f"{t}.anchor_zeros"]["S"]["mean"]  # noqa: E731
    reads = {
        "V600_v": {"a3": sv["aifoundry3"], "c1": sv["aifoundry1c1"], "a2": sv["aifoundry2"], "_src": "q139s clock-voltage.json cross_card_v2_at_600"},
        "idle_w": {"a3": e141["idle_level"]["mean"], "c1": e142["idle_level"]["mean"], "a2": P136["B"]["600"], "_src": "E141/E142 footing idle_level; aifoundry2 B(600) from E136's relation"},
        "zeros_level_fp32_w": {"a3": zl(e141, "fp32"), "c1": zl(e142, "fp32"), "a2": a2cz["fp32"], "_src": "pool-5 fp32.anchor_zeros S (board over idle); aifoundry2: c_zeros"},
        "leak_w_per_c": {"a3": fp["a3"]["k_w_per_c"], "c1": fp["c1"]["k_w_per_c"], "a2": 0.2936, "_src": "footing F1 (a3, c1); aifoundry2 E66's dedicated idle cycles (another method)"},
    }
    return meas, reads, rat


def loco(meas, reads):
    out = {}
    cards = ("a3", "c1", "a2")
    for rd, beta0 in (("V600_v", 2.0), ("idle_w", 1.0), ("zeros_level_fp32_w", 1.0), ("leak_w_per_c", 1.0)):
        r = reads[rd]
        if any(r.get(c) is None for c in cards):
            out[rd] = {"note": "a read is missing for a card", "values": r}
            continue
        o = {"values": {c: r[c] for c in cards}, "physical_beta": beta0, "held_out": {}}
        for fam in ("floats", "int8"):
            if any(meas[c].get(fam) is None for c in cards):
                continue
            for h in cards:
                i, j = [c for c in cards if c != h]
                ls = math.log(meas[i][fam] / meas[j][fam])
                lr = math.log(r[i] / r[j])
                bfit = ls / lr if abs(lr) > 1e-9 else None
                res = {}
                for lab, bb in (("physical", beta0), ("fitted_on_other_two", bfit)):
                    if bb is None:
                        res[lab] = None
                        continue
                    # held-out card's scale relative to the other two (geometric mean of the two references)
                    pred = 0.5 * (math.log(meas[i][fam]) + bb * math.log(r[h] / r[i]) + math.log(meas[j][fam]) + bb * math.log(r[h] / r[j]))
                    err = math.exp(pred - math.log(meas[h][fam])) - 1.0
                    res[lab] = {"beta": bb, "pred_scale": math.exp(pred), "meas_scale": meas[h][fam], "rel_err": err, "within_1pct": abs(err) <= 0.01}
                o["held_out"][f"{fam}|{h}"] = res
        out[rd] = o
    return out


# ------------------------------------------------------------------ main
def main():
    scratch = os.path.abspath(sys.argv[1])
    os.makedirs(scratch, exist_ok=True)
    rows, missing = assemble(scratch)
    m6 = load(os.path.join(M7.M6D, "m6.json"))
    m7 = load(os.path.join(M7D, "m7.json"))
    res = {"_note": "Q139(m) fit_m8.py: D in W over the type's zeros at 600 MHz on Q139(u)'s footing; errors are measured - predicted",
           "n_rows": len(rows), "experiments": sorted({r["exp"] for r in rows}), "missing": missing, "families": {}}
    frozen = {"_model": "M8 (Q139(m)): M7's structure on Q139(u)'s footing plus the candidate terms the nested procedure kept; card term; "
                        "aifoundry2's governed burst clock, board and peak power; heat carried from M7",
              "registration": "M8-REGISTRATION.md (lab f640fb7a, committed before this fit)",
              "units": "power: W over the type's own zeros at 600 MHz on aifoundry3 card 0's footing (card 1: x card1_scale_by_format)",
              "footing": {"k_w_per_c": dict(RF.K_FROZEN), "dips": "E82 A2 once", "e147_step_factor": E147_FOOTING_FACTOR,
                          "aifoundry2": "dips kept, training and test alike"},
              "features": {"W_BPOS_rel": W_BPOS, "bpos_source": "tools/claims-v3/e145/predictions-e145.json card0_prices_rail_fJ.B (bit 7 = mean of 1, 3, 5)",
                           "c_end": "make_blind5 c_check's c_launch_end_est c_reg_flips_per_op", "c_start": "make_blind5 c_check's c_start c_reg_flips_per_op",
                           "xfld": "a_exp + b_exp", "bsat": "B bits in byte transitions flipping >= 7 of 8 bits", "absat": "bsat + A's (x column slots)"},
              "families": {}}
    nested_D = {}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        a, b, outer = run_family(fr, famname, m6, m7)
        res["families"][famname] = a
        frozen["families"][famname] = b
        for i, r in enumerate(fr):
            if r["card"] == "a3" and r["exp"] in ("E78", "E141"):
                nested_D[r["key"]] = r["D"] - float(outer[i])
        s = a["same_folds"]
        print(f"== {famname}: {a['n_rows']} rows, {a['n_kinds']} kinds; card term {a['card_term_chosen']}; chosen {a['chosen_form']} ({a['kept_rule']})")
        print("   picks", a["M8_nested"]["inner_picks"])
        for lab in ("M8_nested", "M7_form_loko", "M6_form_loko", "M5_form_loko", "M7_frozen", "M6_frozen"):
            print(f"   {lab:14s} all {s['all'][lab]['rms_w']:.4f}  " + "  ".join(
                f"{k} {s[k][lab]['rms_w']:.3f}" for k in s if (k.startswith('fp') or k.startswith('int8') or k.startswith('exp E14')) and s[k][lab]['rms_w'] is not None))
        print("   paired (M8 - x) over kinds", {k: (round(v["d_rms_w"], 4), round(v["lo95"], 4), round(v["hi95"], 4)) for k, v in a["paired_bootstrap_over_kinds_M8_minus"].items()})
        print("   plain LOKO by form", {fn: round(v["all"], 4) for fn, v in a["plain_loko_by_form"].items()})
        print("   drops", a["drop_one_term"])
        print("   coef fJ", {k: round(v, 3) for k, v in b["coef_fJ"].items()}, "se", {k: round(v, 3) for k, v in b["coef_jackknife_se_fJ"].items()})
        print("   card1 scale", b["card1_scale_by_format"], "band k", round(b["band_k"], 3), a["band"]["coverage"])
        print("   pools", {k: round(v["rms_w"], 3) for k, v in b["interval_pool_by_format_card"].items() if v["rms_w"]})
    a2 = a2_fit(nested_D)
    res["aifoundry2"] = a2
    frozen["aifoundry2"] = {k: v for k, v in a2.items() if k not in ("peaks", "configs")}
    frozen["aifoundry2"]["end_to_end_from_M8_nested_D"] = {k: v for k, v in a2["end_to_end_from_M8_nested_D"].items() if k != "rows"}
    print("== aifoundry2", json.dumps({k: {q: v[q] for q in ("loko_rms_mhz", "loko_rms_board_w", "governed", "pinned")} for k, v in a2["configs"]["by_config"].items()}, default=float))
    print("   steps", a2["selection_steps"], "kept", a2["kept_config"], "params", a2["params"])
    print("   e2e", {k: v for k, v in a2["end_to_end_from_M8_nested_D"].items() if k != "rows"})
    print("   M7 frozen relation, same cells", a2["M7_frozen_relation_same_cells"])
    print("   peak", a2["peak"], "scale", a2["scale_vs_a3"])
    meas, reads, rat = card_scale(rows, a2["scale_vs_a3"], a2["params"]["c_zeros_w"])
    lc = loco(meas, reads)
    res["card_scale"] = {"measured": meas, "reads": reads, "n_pairs": {k: len(v) for k, v in rat.items()}, "loco": lc}
    frozen["card_scale_predictor"] = res["card_scale"]
    print("== card scale measured", meas)
    for rd, o in lc.items():
        print("  ", rd, json.dumps(o.get("held_out", o), default=float)[:900])
    frozen["heat"] = m7["heat"]
    frozen["heat"]["_carried"] = "M7's frozen heat law and band (m7.json heat), unchanged; M8's D gives S"
    frozen["memory_path_E139"] = m7["memory_path_E139"]
    frozen["band_rule"] = ("power: half-width = k x sqrt(pool^2 + s^2 x C x), pool = M8's nested rms for the tile's format and card, C the jackknife "
                           "covariance by kind, s the card scale; k = max(q95 of |nested residual| / pool over all M8 rows, the same over the rows of "
                           "blind pools 3, 4 and 5 (E115, E140, E141, E142)); heat: M7's (k_h x pool_h); aifoundry2: the 95th percentiles of "
                           "|measured - predicted| leave one kind out over E80's, E83's and E143's bursts (clock, board W), peak = B(800) + c s(800) + "
                           "the q95 excess of the highest board sample over E143's traces, with c at D's band top")
    json.dump(res, open(os.path.join(HERE, "nested-m8.json"), "w"), indent=1, default=float)
    json.dump(frozen, open(os.path.join(HERE, "m8.json"), "w"), indent=1, sort_keys=True, default=float)
    json.dump(rows, open(os.path.join(HERE, "rows-m8.json"), "w"), indent=0, default=float)
    print("missing", len(missing), missing[:12])


if __name__ == "__main__":
    main()
