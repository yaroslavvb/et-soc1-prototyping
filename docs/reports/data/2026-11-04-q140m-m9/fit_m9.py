#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q140(m): M9, M8's structure refitted on every committed kinds row plus blind pool 6's 44 new kinds on both 600 MHz cards
(E153, E157), with only the registered candidate features that lower the nested error. Everything follows M9-REGISTRATION.md
(committed 8dfafae3 before this file existed): rows, features, forms, the fixed card term, the nested leave-one-kind-out procedure
with M6, M7, M8 and M9 on the same folds, the rule that a feature stays only if it lowers the nested error, the band rule on
blind pools 3-6, heat carried from M7, and aifoundry2 left to M8's frozen relation or Q140(l)'s part.

    python3 fit_m9.py <scratch dir> [--out <dir>]    # writes m9.json, nested-m9.json, rows-m9.json to <dir> (default: beside it)

SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M8D = os.path.join(DD, "2026-11-03-q139m-model")
E153D = os.path.join(DD, "2026-11-03-e153-blind6-aifoundry3")
E157D = os.path.join(DD, "2026-11-03-e157-blind6-card1")
KD = os.path.join(ROOT, "tools", "claims-v3", "kinds")
B4, B5, B6 = (os.path.join(KD, f"blind{i}") for i in (4, 5, 6))
if M8D not in sys.path:
    sys.path.insert(0, M8D)
import fit_m8 as M8  # noqa: E402  (imports fit_m7, fit_m6, m6_rows, fit_m5, reduce_footing, make_blind5, posthoc_m7_e147 unchanged)

M7, F, mk, M6 = M8.M7, M8.F, M8.mk, M8.M6
R = M6.R
P147 = M8.P147
load = lambda p: json.load(open(p))  # noqa: E731
sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
fsha = lambda p: sha(open(p, "rb").read())  # noqa: E731
rms = F.rms
CARD_TERM = "C0_M5_E78E82_family"          # M8's card term, kept (registration section 3): family fixed, value refitted per fold
SEED = 140
POOL_EXPS = ("E115", "E140", "E141", "E142", "E153", "E157")   # blind pools 3-6 (band rule, registration section 7)
POOL6 = ("E153", "E157")
SIX = ("fp32.b_onebit_b20_third", "int8.a_zeros_b_lineflip", "int8.b_line_zero_ff",
       "int8.bheld_bit1", "int8.bheld_bit4", "int8.bheld_bit7")     # the Q139 critic's six named-miss tiles
BSAT_CAP = 1024.0                          # bits an op (registration section 2, item 5)


# ------------------------------------------------------------------ candidate features (registration section 2)
def _pts(crow):
    p = sorted(crow["points"], key=lambda q: q.get("n0", 0))
    assert len(p) == 3, "three launch points expected"
    return p


def lq_shape(crow):
    """whole-VPU nets_map at the first launch point minus the mean of the other two"""
    p = _pts(crow)
    v = [q["vpu"]["nets_map"] for q in p]
    return float(v[0] - 0.5 * (v[1] + v[2]))


def exp_stage(crow):
    return float(crow["mean"]["vpu"]["by_stage"]["exponent"])


def zeros_rows():
    zc = load(os.path.join(DD, "2026-11-01-q132-rtl-bench", "counts-v2.json"))["rows"]
    return {t: zc[f"{t}.zeros"] for t in F.CPO}


def bench_extra(crow, t, zr):
    """the float candidates that come from the bench's counts (0 for int8): xstage32, xstage, lq1; tile minus its type's zeros"""
    if t == "int8":
        return {"xstage32": 0.0, "xstage": 0.0, "lq1": 0.0}
    xs = exp_stage(crow) - exp_stage(zr[t])
    return {"xstage32": xs if t == "fp32" else 0.0, "xstage": xs, "lq1": lq_shape(crow) - lq_shape(zr[t])}


_DIG_CACHE = {}
PC11 = np.array([bin(v).count("1") for v in range(2048)], dtype=np.int64)


def booth_feats(raw):
    """int8: radix-4 Booth partial-product flips with B recoded (bpp_r4) and A's flips weighted by B's non-zero digits (bnz_a),
    over make_kinds' int8 issue stream, the F2 operand registers holding through gated micro-ops (registration items 6, 7)."""
    h = sha(raw)
    if h in _DIG_CACHE:
        return dict(_DIG_CACHE[h])
    aw, bw = mk.words_of(raw)
    a_seq, b_seq = mk.issue_streams_fast(aw, bw, "int8")           # (256,), (256, 16)
    g = mk.gate_mask(a_seq, b_seq, "int8")                          # (256, 8), True = gated
    T, S = b_seq.shape
    valid = ~g[:, np.arange(S) % 8]                                 # (256, 16)
    # the last valid micro-op at or before t, cyclic (the F2 registers load only on a valid micro-op)
    ar = np.arange(T)
    w = np.where(valid, ar[:, None], -1)
    w2 = np.concatenate([w, w + np.where(w >= 0, T, 0)], axis=0)
    last = np.maximum.accumulate(w2, axis=0)[T:] % T                # (256, 16); a slot never valid keeps index -1 % T
    never = ~valid.any(axis=0)
    A = np.stack([((a_seq >> np.uint64(8 * e)) & np.uint64(0xFF)).astype(np.int64) for e in range(4)], axis=-1)   # (256, 4)
    Bb = np.stack([((b_seq >> np.uint64(8 * e)) & np.uint64(0xFF)).astype(np.int64) for e in range(4)], axis=-1)  # (256, 16, 4)
    a_eff = A[last]                                                 # (256, 16, 4)
    b_eff = np.take_along_axis(Bb, last[:, :, None].repeat(4, axis=2), axis=0)
    a_eff[:, never, :] = 0
    b_eff[:, never, :] = 0
    a_s = np.where(a_eff >= 128, a_eff - 256, a_eff)               # signed
    b_bits = [(b_eff >> j) & 1 for j in range(8)]
    pp_flips = np.zeros(a_s.shape, dtype=np.int64)
    nz = np.zeros(a_s.shape, dtype=np.int64)
    prev = lambda x: np.roll(x, 1, axis=0)  # noqa: E731
    for m in range(4):
        bm1 = b_bits[2 * m - 1] if m > 0 else np.zeros_like(b_eff)
        d = -2 * b_bits[2 * m + 1] + b_bits[2 * m] + bm1
        mag = np.where(np.abs(d) == 2, (2 * a_s) & 0x3FF, np.where(np.abs(d) == 1, a_s & 0x3FF, 0))
        neg = (d < 0).astype(np.int64)
        pp = np.where(neg == 1, (~mag) & 0x3FF, mag) | (neg << 10)
        x = pp ^ prev(pp)
        pp_flips += PC11[x]
        nz += (d != 0).astype(np.int64)
    a_fl = PC11[(a_eff ^ prev(a_eff)) & 0xFF]
    out = {"bpp_r4": float(pp_flips.sum()), "bnz_a": float((a_fl * nz).sum())}
    _DIG_CACHE[h] = out
    return dict(out)


def m9_extra(f, t, crow, path, zr):
    """every M9 candidate feature of one tile: f = its M8 features, crow = its bench counts row, path = its tile file"""
    e = {"xfld32": (float(f.get("a_exp", 0.0)) + float(f.get("b_exp", 0.0))) if t == "fp32" else 0.0}
    e.update(bench_extra(crow, t, zr) if crow is not None else {"xstage32": None, "xstage": None, "lq1": None})
    if t == "int8":
        e["bsat_cap"] = min(float(f.get("bsat", 0.0)), BSAT_CAP)
        e.update(booth_feats(open(path, "rb").read()))
    else:
        e.update({"bsat_cap": 0.0, "bpp_r4": 0.0, "bnz_a": 0.0})
    return e


# ------------------------------------------------------------------ rows (registration section 1)
COUNTS_FILES = [f for _, f in R.COUNTS] + [os.path.join(M7.M6D, "counts-blind4.json"), os.path.join(B5, "counts-blind5.json"),
                                           os.path.join(B6, "counts-blind6.json"),
                                           os.path.join(DD, "2026-11-02-e147-bit-prices-rest", "bench", "counts-e147.json")]
QB = ("mult", "add32", "add16", "bus", "rest", "clk", "nets_nobus")


def counts_lookup():
    """every counts row of this bench committed in the tree (M6's list, pools 4-6, E147), indexed by the M5 bench features it
    gives: a training row's counts row is the one whose recomputed features equal the row's own (names differ between files)"""
    zeros = M7.zeros_counts()

    def bf(crow, t):
        return F.fmt_feats(F.bench_feats(crow["mean"], zeros[t]), t)

    def key(f, t):
        return (t,) + tuple(round(float(f[q]), 2) for q in QB)
    index = {}
    for fpath in COUNTS_FILES:
        if not os.path.exists(fpath):
            continue
        for k, v in load(fpath)["rows"].items():
            t = v["type"]
            index.setdefault(key(bf(v, t), t), []).append((os.path.relpath(fpath, ROOT), k, v))
    return index, key, bf


def assemble(scratch):
    rows = load(os.path.join(M8D, "rows-m8.json"))
    for r in rows:
        r["src"] = "M8 rows-m8.json"
    man6 = load(os.path.join(B6, "blind6.json"))["tiles"]
    feats6 = load(os.path.join(B6, "predictions-blind6-aifoundry3.json"))["tiles"]
    missing = []
    for exp, card, red in (("E153", "a3", os.path.join(E153D, "e153.json")), ("E157", "c1", os.path.join(E157D, "e157.json"))):
        items = load(red)["items"]
        for meta in man6:
            if meta.get("anchor"):
                continue
            name, t = meta["name"], meta["type"]
            it = items.get(name)
            if it is None or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
                missing.append(f"{exp}:{name} (no D)")
                continue
            p = os.path.join(B6, meta["file"])
            h = fsha(p)
            assert h == meta["sha256"]["whole"], name
            rows.append({"exp": exp, "card": card, "key": name, "type": t, "kind": f"{t}.blind6:{name.split('.', 1)[1]}",
                         "tile_sha256": h, "tile_path": os.path.relpath(p, ROOT), "D": float(it["D"]["mean"]),
                         "D_se": it["D"].get("se"), "rate": float(it["rate"]["mean"]), "f": dict(feats6[name]["features"]),
                         "dT_win": (it.get("dT_win") or {}).get("mean"), "case": meta.get("case"), "priority": meta.get("priority"),
                         "src": f"{os.path.relpath(red, ROOT)} items.{name}"})
    # bench counts for every row (the float candidates need them): the counts row whose M5 bench features equal the row's own
    index, key, bf = counts_lookup()
    zr = zeros_rows()
    pool = os.path.join(scratch, "e147-pool")
    P147.build_pool(pool)
    c147 = load(os.path.join(pool, "counts-e147-merged.json"))["rows"]
    unmatched, ambiguous = [], []
    for r in rows:
        t = r["type"]
        r["f"] = dict(r["f"])
        if r["exp"] == "E147":
            ci = c147.get(r["key"]) or c147.get(P147.bare(r["key"]))
            cz = c147.get(r["zero"]) or c147.get(P147.bare(r["zero"]))
            fi, fz = bf(ci, t), bf(cz, t)
            if key({q: fi[q] - fz[q] for q in QB}, t) != key(r["f"], t):
                unmatched.append(f"E147:{r['key']}")
            ei, ez = bench_extra(ci, t, zr), bench_extra(cz, t, zr)
            e = {k: ei[k] - ez[k] for k in ei}
            e["xfld32"] = (float(r["f"].get("a_exp", 0.0)) + float(r["f"].get("b_exp", 0.0)))
            e.update({"bsat_cap": 0.0, "bpp_r4": 0.0, "bnz_a": 0.0})
            r["f"].update(e)
            r["counts_src"] = "E147 merged counts (posthoc_m7_e147.build_pool): item minus its own zero"
            continue
        cands = index.get(key(r["f"], t), [])
        if not cands:
            unmatched.append(f"{r['exp']}:{r['key']}")
            crow, src = None, None
        else:
            crow, src = cands[0][2], f"{cands[0][0]} rows.{cands[0][1]}"
            if t != "int8":
                ex = {json.dumps(bench_extra(c[2], t, zr), sort_keys=True) for c in cands}
                if len(ex) > 1:
                    ambiguous.append(f"{r['exp']}:{r['key']} ({len(cands)} counts rows disagree on the launch points)")
        path = os.path.join(ROOT, r["tile_path"])
        r["f"].update(m9_extra(r["f"], t, crow, path, zr))
        r["counts_src"] = src
    unmatched += ambiguous
    return rows, missing, unmatched


# ------------------------------------------------------------------ forms (registration section 3)
BF, BI = M7.BASE_F, M7.BASE_I
FL_FEATS = ("c_end", "xfld32", "xstage32", "xstage", "lq1")
I8_FEATS = ("bsat", "bsat_cap", "bpp_r4", "bnz_a")


def float_forms():
    out = {}
    for ce in (0, 1):
        for xf in (0, 1):
            for xs in (None, "xstage32", "xstage"):
                for lq in (0, 1):
                    add = (["c_end"] if ce else []) + (["xfld32"] if xf else []) + ([xs] if xs else []) + (["lq1"] if lq else [])
                    out["G8" + "".join("+" + a for a in add)] = BF + ["gtr", "glive"] + add
    return out


def int8_forms():
    out = {}
    for bs in (None, "bsat", "bsat_cap"):
        for bp in (0, 1):
            for bn in (0, 1):
                add = ([bs] if bs else []) + (["bpp_r4"] if bp else []) + (["bnz_a"] if bn else [])
                out["J8" + "".join("+" + a for a in add)] = BI + ["b138"] + add
    return out


FORMS9 = {"float": float_forms(), "int8": int8_forms()}
BASE9 = {"float": "G8", "int8": "J8"}
M8FORM = {"float": "G8+c_end", "int8": "J8+bsat"}
M7FORM = {"float": "G8", "int8": "J8"}
FEATS = {"float": FL_FEATS, "int8": I8_FEATS}
REFFORMS = {"float": {"M6_form": M7.FORMS["float"]["G6_M6"], "M5_form": M7.FORMS["float"]["G0_M5"]},
            "int8": {"M6_form": M7.FORMS["int8"]["J1_M6"], "M5_form": M7.FORMS["int8"]["J0_M5"]}}


def added(fam_name, fn):
    base = set(FORMS9[fam_name][BASE9[fam_name]])
    return [q for q in FORMS9[fam_name][fn] if q not in base]


# ------------------------------------------------------------------ scoring helpers
def boot_diff(kid, ea, eb, n=2000, seed=SEED):
    """rms(ea) - rms(eb) with a bootstrap over kinds (95%)"""
    ok = ~np.isnan(ea) & ~np.isnan(eb)
    if not ok.any():
        return None
    kid = np.unique(kid[ok], return_inverse=True)[1]
    ea, eb = ea[ok], eb[ok]
    K = int(kid.max()) + 1
    sa, sb, nn = np.zeros(K), np.zeros(K), np.zeros(K)
    np.add.at(sa, kid, ea ** 2)
    np.add.at(sb, kid, eb ** 2)
    np.add.at(nn, kid, 1)
    rng = np.random.default_rng(seed)
    d = []
    for _ in range(n):
        i = rng.integers(0, K, K)
        d.append(math.sqrt(sa[i].sum() / nn[i].sum()) - math.sqrt(sb[i].sum() / nn[i].sum()))
    pt = math.sqrt(sa.sum() / nn.sum()) - math.sqrt(sb.sum() / nn.sum())
    lo, hi = np.quantile(d, [0.025, 0.975])
    return {"d_rms_w": pt, "lo95": float(lo), "hi95": float(hi), "resolved": bool(hi < 0 or lo > 0), "n_kinds": K, "n_rows": int(ok.sum())}


def stats(e):
    e = np.asarray(e, float)
    e = e[~np.isnan(e)]
    return {"n": int(len(e)), "rms_w": rms(e), "bias_meas_minus_pred_w": float(np.mean(e)) if len(e) else None}


def frozen_pred(rows, mod, by_format, rate=None):
    X = np.array([[(rate[i] if rate is not None else r["rate"]) * r["f"][q] for q in mod["terms"]] for i, r in enumerate(rows)], float)
    s = np.array([(mod["card1_scale_by_format"][r["type"]] if by_format else mod["card1_scale"]) if r["card"] == "c1" else 1.0
                  for r in rows])
    return X @ np.array(mod["coef_J"]) * s


# ------------------------------------------------------------------ one family
def run_family(rows, famname, m6, m7, m8, log):
    cands = FORMS9[famname]
    forms = {**cands, **REFFORMS[famname]}
    fam = M7.Fam(rows, forms, CARD_TERM)
    K = fam.K
    exps = np.array([r["exp"] for r in rows])
    cards = np.array([r["card"] for r in rows])
    keys = np.array([r["key"] for r in rows])
    # plain leave-one-kind-out, every form
    plain = {fn: fam.loko(fn) for fn in forms}
    log(f"   plain LOKO done ({len(forms)} forms, {K} kinds)")
    # the inner scores: for each held-out kind k and candidate form, the leave-one-kind-out rms on the remaining kinds
    names = list(cands)
    inner = np.zeros((K, len(names)))
    for k in range(K):
        for j, fn in enumerate(names):
            inner[k, j] = rms(fam.loko(fn, k))
        if k % 50 == 0:
            log(f"   inner scores: kind {k} of {K}")
    # the nested procedure over a set of forms: the outer error of kind k is the plain LOKO error of its inner best
    def nested(subset):
        cols = [names.index(fn) for fn in subset]
        best = [names[cols[int(np.argmin(inner[k, cols]))]] for k in range(K)]
        outer = np.full(len(rows), np.nan)
        for k in range(K):
            m = fam.kid == k
            outer[m] = plain[best[k]][m]
        picks = {}
        for b in best:
            picks[b] = picks.get(b, 0) + 1
        return outer, picks
    outer_all, picks_all = nested(names)
    n_all = rms(outer_all)
    tests = {}
    for q in FEATS[famname]:
        sub = [fn for fn in names if q not in added(famname, fn)]
        o, pk = nested(sub)
        tests[q] = {"nested_without_q_w": rms(o), "nested_all_w": n_all, "lowers_nested_error": bool(n_all < rms(o)),
                    "forms_without_q": len(sub)}
    kept = [q for q in FEATS[famname] if tests[q]["lowers_nested_error"]]
    allowed = [fn for fn in names if set(added(famname, fn)) <= set(kept)]
    sel = {fn: rms(plain[fn]) for fn in names}
    chosen = min(allowed, key=lambda fn: sel[fn])
    drops = {}
    for q in added(famname, chosen):
        sub = [x for x in FORMS9[famname][chosen] if x != q]
        drops[q] = {"plain_loko_without_w": rms(M7.Fam(rows, {"S": sub}, CARD_TERM).loko("S")), "plain_loko_with_w": sel[chosen]}
    # restricted procedure (post hoc beside the registered score: Q was chosen on all rows)
    outer_q, picks_q = nested(allowed)
    # frozen fit
    b, s = fam.fit_all(chosen, [])
    C = fam.jackknife_cov(chosen)
    coefJ = fam.coef_J(chosen, b)
    # the frozen models on the same rows (each row's measured rate, M8's convention)
    e6 = fam.y - frozen_pred(rows, m6["families"][famname], False)
    e7 = fam.y - frozen_pred(rows, m7["families"][famname], True)
    e8 = fam.y - frozen_pred(rows, m8["families"][famname], True)
    errsets = {"M9_nested": outer_all, "M9_frozen_form_loko": plain[chosen], "M9_restricted_nested": outer_q,
               "M8_form_loko": plain[M8FORM[famname]], "M7_form_loko": plain[M7FORM[famname]],
               "M6_form_loko": plain["M6_form"], "M5_form_loko": plain["M5_form"],
               "M8_frozen": e8, "M7_frozen": e7, "M6_frozen": e6}
    p6 = np.isin(exps, POOL6)
    six = np.isin(keys, SIX)
    prio1 = np.array([r.get("priority") == 1 for r in rows])
    masks = {"all": np.ones(len(rows), bool), "M8's rows (outside pool 6)": ~p6, "pool 6 (E153 + E157), all new kinds": p6,
             "pool 6, priority 1": p6 & prio1, "pool 6, without the six named-miss tiles": p6 & ~six,
             "pool 6, priority 1, without the six": p6 & prio1 & ~six}
    for t in fam.fmts:
        masks[t] = fam.tys == t
        for cd in ("a3", "c1"):
            masks[f"{t}|{cd}"] = (fam.tys == t) & (cards == cd)
            masks[f"pool 6 {t}|{cd}"] = p6 & (fam.tys == t) & (cards == cd)
            masks[f"pool 6 {t}|{cd}, priority 1"] = p6 & prio1 & (fam.tys == t) & (cards == cd)
            masks[f"pool 6 {t}|{cd}, without the six"] = p6 & ~six & (fam.tys == t) & (cards == cd)
            masks[f"pool 6 {t}|{cd}, priority 1, without the six"] = p6 & prio1 & ~six & (fam.tys == t) & (cards == cd)
    for cd in ("a3", "c1"):
        masks[f"pool 6 card {cd}"] = p6 & (cards == cd)
        masks[f"pool 6 card {cd}, priority 1"] = p6 & prio1 & (cards == cd)
        masks[f"pool 6 card {cd}, without the six"] = p6 & ~six & (cards == cd)
        masks[f"pool 6 card {cd}, priority 1, without the six"] = p6 & prio1 & ~six & (cards == cd)
    for e in sorted(set(exps)):
        masks[f"exp {e}"] = exps == e
    tables = {lab: {m: stats(e[msk]) for m, e in errsets.items()} for lab, msk in masks.items() if msk.any()}
    boots = {}
    for lab in ("all", "pool 6 (E153 + E157), all new kinds", "pool 6, priority 1", "pool 6, without the six named-miss tiles",
                "pool 6, priority 1, without the six", "pool 6 card a3, priority 1", "pool 6 card c1, priority 1"):
        msk = masks.get(lab)
        if msk is None or not msk.any():
            continue
        boots[lab] = {f"M9_nested - {m}": boot_diff(fam.kid[msk], outer_all[msk], e[msk]) for m, e in errsets.items() if m != "M9_nested"}
    # bands (registration section 7)
    pools = {}
    for t in fam.fmts:
        for cd in ("a3", "c1"):
            e = outer_all[(fam.tys == t) & (cards == cd)]
            pools[f"{t}|{cd}"] = {"rms_w": rms(e), "n": int(np.sum(~np.isnan(e))), "q95_abs_w": M7.q95(e)}
    z = np.array([abs(outer_all[i]) / pools[f"{fam.tys[i]}|{cards[i]}"]["rms_w"] for i in range(len(rows))])
    pm = np.isin(exps, POOL_EXPS)
    ki, kii = float(np.nanquantile(z, 0.95)), float(np.nanquantile(z[pm], 0.95))
    kband = max(ki, kii)
    loo_in = 0
    for i in np.where(pm & ~np.isnan(z))[0]:
        zz, pp = np.delete(z, i), np.delete(pm, i)
        kk = max(float(np.nanquantile(zz, 0.95)), float(np.nanquantile(zz[pp], 0.95)))
        loo_in += int(z[i] <= kk)
    cover = {lab: {"inside": int(np.sum(z[m] <= kband)), "n": int(np.sum(m & ~np.isnan(z)))}
             for lab, m in (("all", np.ones(len(rows), bool)), ("pool rows (E115, E140, E141, E142, E153, E157)", pm),
                            ("pool 6 (E153 + E157)", p6), ("E153", exps == "E153"), ("E157", exps == "E157"))}
    cover["pool rows, each left out of k"] = {"inside": loo_in, "n": int(np.sum(pm & ~np.isnan(z)))}
    misses = sorted([{"exp": r["exp"], "card": r["card"], "key": r["key"], "D": r["D"], "M9_nested_err_w": float(outer_all[i]),
                      "M8_frozen_err_w": float(e8[i]), "M7_frozen_err_w": float(e7[i]), "M6_frozen_err_w": float(e6[i])}
                     for i, r in enumerate(rows)], key=lambda x: -abs(x["M9_nested_err_w"]))[:25]
    pool6_rows = [{"exp": r["exp"], "card": r["card"], "key": r["key"], "case": (r.get("case") or "")[:1], "priority": r.get("priority"),
                   "D": round(r["D"], 4), **{m: round(float(e[i]), 4) for m, e in errsets.items()}}
                  for i, r in enumerate(rows) if r["exp"] in POOL6]
    out = {"n_rows": len(rows), "n_kinds": K, "card_term": CARD_TERM, "forms": forms,
           "plain_loko_by_form": {fn: {**M7.split(fam, e), "rms_all_w": rms(e)} for fn, e in plain.items()},
           "M9_nested": {"rms_w": n_all, "inner_picks": picks_all},
           "feature_tests": tests, "kept_features": kept, "allowed_forms": allowed, "chosen_form": chosen,
           "chosen_terms": FORMS9[famname][chosen], "drop_one_term": drops,
           "M9_restricted_nested": {"rms_w": rms(outer_q), "inner_picks": picks_q,
                                    "note": "post hoc beside the registered score: the procedure over the forms the rule allowed, Q chosen on all rows"},
           "same_folds": tables, "paired_bootstrap_over_kinds": boots,
           "band": {"pools": pools, "k_i_all_rows_q95": ki, "k_ii_pool_rows_q95": kii, "k": kband, "coverage": cover},
           "largest_nested_misses": misses, "pool6_rows": pool6_rows}
    frozen = {"form": chosen, "terms": FORMS9[famname][chosen], "coef_J": [float(x) for x in coefJ],
              "coef_fJ": dict(zip(FORMS9[famname][chosen], [float(x) * 1e15 for x in coefJ])),
              "coef_jackknife_se_fJ": dict(zip(FORMS9[famname][chosen], [float(x) * 1e15 for x in np.sqrt(np.diag(C))])),
              "cov_J2": C.tolist(), "card_term": CARD_TERM, "card1_scale_by_format": dict(zip(fam.fmts, [float(x) for x in s])),
              "interval_pool_by_format_card": pools, "band_k": kband, "n_rows": len(rows), "n_kinds": K, "kept_features": kept}
    return out, frozen, outer_all, e8, e7, e6


# ------------------------------------------------------------------ the check of registration section 6
def check_frozen_pool6(rows, m6, m7, m8):
    """M8, M7 and M6 as frozen, at the nominal rate the frozen predictions used, against E153's and E157's power_rows"""
    pr = {"E153": load(os.path.join(E153D, "scored.json"))["primary"]["primary"]["power_rows"],
          "E157": load(os.path.join(E157D, "scored.json"))["primary"]["power_rows"]}
    worst, n, regs = 0.0, 0, {}
    for lab, mods in (("M8", m8), ("M7", m7), ("M6", m6)):
        for fam_name, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
            rr = [r for r in rows if r["exp"] in POOL6 and want(r)]
            if not rr:
                continue
            rate = [F.RATE[r["type"]] for r in rr]
            p = frozen_pred(rr, mods["families"][fam_name], lab != "M6", rate)
            for r, v in zip(rr, p):
                ref = pr[r["exp"]][lab][r["key"]]
                worst = max(worst, abs(float(v) - float(ref["pred"])))
                n += 1
                assert abs(float(ref["measured"]) - r["D"]) < 1e-9, (r["exp"], r["key"])
                regs.setdefault(lab, {}).setdefault(r["exp"], {})[r["key"]] = float(ref["error"])
    return {"n_compared": n, "max_abs_diff_w": worst, "pass": worst <= 0.002, "registered_errors": regs}


# ------------------------------------------------------------------ main
def main():
    scratch = os.path.abspath(sys.argv[1])
    os.makedirs(scratch, exist_ok=True)
    od = os.path.abspath(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE
    os.makedirs(od, exist_ok=True)
    log = lambda s: print(s, flush=True)  # noqa: E731
    rows, missing, unmatched = assemble(scratch)
    log(f"rows {len(rows)}; missing {missing}; unmatched counts {unmatched}")
    if unmatched:
        raise SystemExit(f"rows whose bench counts could not be matched to their features: {unmatched}")
    m6 = load(os.path.join(M7.M6D, "m6.json"))
    m7 = load(os.path.join(M8.M7D, "m7.json"))
    m8 = load(os.path.join(M8D, "m8.json"))
    chk = check_frozen_pool6(rows, m6, m7, m8)
    log(f"check (registration section 6): {chk['n_compared']} frozen predictions, max |diff| {chk['max_abs_diff_w']:.5f} W, pass {chk['pass']}")
    if not chk["pass"]:
        raise SystemExit("the frozen models do not reproduce E153/E157's registered predictions; stopping")
    # the frozen models' registered blind errors on pool 6 (their predictions at the nominal rate, as E153 and E157 scored them)
    by_key = {(r["exp"], r["key"]): r for r in rows if r["exp"] in POOL6}
    reg_tab = {}
    for lab, by_exp in chk["registered_errors"].items():
        for sub, keep in (("all 44 new kinds", lambda r: True), ("priority 1", lambda r: r.get("priority") == 1),
                          ("without the six", lambda r: r["key"] not in SIX),
                          ("priority 1, without the six", lambda r: r.get("priority") == 1 and r["key"] not in SIX)):
            for t in ("fp32", "fp16", "int8", "all"):
                for cd, ex in (("a3", "E153"), ("c1", "E157"), ("both", None)):
                    e = [err for x in by_exp for k, err in by_exp[x].items()
                         if (ex is None or x == ex) and (t == "all" or by_key[(x, k)]["type"] == t) and keep(by_key[(x, k)])]
                    reg_tab.setdefault(lab, {}).setdefault(sub, {})[f"{t}|{cd}"] = stats(e)
    chk["registered_blind_tables"] = reg_tab
    res = {"_note": "Q140(m) fit_m9.py: D in W over the type's zeros at 600 MHz on Q139(u)'s footing; errors are measured - predicted",
           "registration": "M9-REGISTRATION.md (lab 8dfafae3, committed before this fit)", "n_rows": len(rows),
           "experiments": sorted({r["exp"] for r in rows}), "missing": missing, "check_frozen_pool6": chk, "families": {}}
    frozen = {"_model": "M9 (Q140(m)): M8's structure on Q139(u)'s footing, refitted on M8's rows plus blind pool 6 on both 600 MHz "
                        "cards, with only the registered candidate features that lowered the nested error; M8's card term; heat "
                        "carried from M7; aifoundry2 through M8's frozen relation or Q140(l)'s part",
              "registration": "M9-REGISTRATION.md (lab 8dfafae3, committed before this fit)",
              "units": "power: W over the type's own zeros at 600 MHz on aifoundry3 card 0's footing (card 1: x card1_scale_by_format)",
              "footing": dict(M8.load(os.path.join(M8D, "m8.json"))["footing"]),
              "features": {"xfld32": "a_exp + b_exp on fp32 rows (0 on fp16)",
                           "xstage32": "bench vpu by_stage exponent, mean of 3 launch points, minus fp32 zeros', fp32 rows only",
                           "xstage": "the same on both float formats (each minus its type's zeros')",
                           "lq1": "bench vpu nets_map at the first launch point minus the mean of the other two, minus the type's zeros'",
                           "bsat_cap": f"min(bsat, {BSAT_CAP:.0f})",
                           "bpp_r4": "radix-4 Booth partial-product flips, B recoded, F2 registers holding through gated micro-ops",
                           "bnz_a": "A-byte flips x the number of non-zero radix-4 digits of the B byte they meet",
                           "M8's": "c_end, bsat and the rest as m8.json features"},
              "families": {}}
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        log(f"== {famname}: {len(fr)} rows")
        a, b, outer, e8, e7, e6 = run_family(fr, famname, m6, m7, m8, log)
        res["families"][famname] = a
        frozen["families"][famname] = b
        for i, r in enumerate(fr):
            r["M9_nested_err_w"] = float(outer[i])
        s = a["same_folds"]
        log(f"   kept {a['kept_features']}; chosen {a['chosen_form']}; tests " +
            json.dumps({q: (round(v['nested_all_w'], 4), round(v['nested_without_q_w'], 4)) for q, v in a["feature_tests"].items()}))
        for lab in ("all", "pool 6 (E153 + E157), all new kinds", "pool 6, priority 1", "pool 6, without the six named-miss tiles"):
            if lab in s:
                log(f"   {lab}: " + "  ".join(f"{m} {v['rms_w']:.3f}" for m, v in s[lab].items() if v["rms_w"] is not None))
        log("   coef fJ " + json.dumps({k: round(v, 3) for k, v in b["coef_fJ"].items()}) + " se " +
            json.dumps({k: round(v, 3) for k, v in b["coef_jackknife_se_fJ"].items()}))
        log(f"   card1 scale {b['card1_scale_by_format']}; band k {b['band_k']:.3f}; coverage {a['band']['coverage']}")
    frozen["heat"] = dict(m7["heat"])
    frozen["heat"]["_carried"] = "M7's frozen heat law and band (m7.json heat), unchanged, as M8; M9's D gives S"
    frozen["memory_path_E139"] = m7["memory_path_E139"]
    frozen["aifoundry2_default"] = {"_what": "M8's frozen aifoundry2 relation, peak rule and bands (m8.json aifoundry2), applied to M9's D600 "
                                             "when predict_blind7.py has no --a2-terms", "m8_aifoundry2": m8["aifoundry2"]}
    frozen["band_rule"] = ("power: half-width = k x sqrt(pool^2 + s^2 x C x), pool = M9's nested rms for the tile's format and card, C the "
                           "frozen form's jackknife covariance by kind, s the card scale; k = max(q95 of |nested residual| / pool over all M9 "
                           "rows, the same over the rows of blind pools 3-6 (E115, E140, E141, E142, E153, E157)); heat: M7's (k_h x pool_h); "
                           "aifoundry2: M8's frozen bands and peak rule, or Q140(l)'s with --a2-terms")
    json.dump(res, open(os.path.join(od, "nested-m9.json"), "w"), indent=1, default=float)
    json.dump(frozen, open(os.path.join(od, "m9.json"), "w"), indent=1, sort_keys=True, default=float)
    json.dump(rows, open(os.path.join(od, "rows-m9.json"), "w"), indent=0, default=float)
    log(f"written m9.json, nested-m9.json, rows-m9.json to {os.path.relpath(od, ROOT) if od.startswith(ROOT) else 'the --out dir'}")


if __name__ == "__main__":
    main()
