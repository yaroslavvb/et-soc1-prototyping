#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q133(b): the desk check behind the README's "Corrections after verification" (C1-C7): every number they cite, from
committed files. Nothing here is measured and nothing here writes a file: m5.json, loko.json, the predictions and the
counts are read, never changed.

    python3 corrections-check.py > corrections-check.txt      # a python with numpy; a few minutes on one core

C1 reruns fit_m5.py's own code (imported, unmodified, from this directory) with the candidate set of the first fit
(F0-F8, written before any fit ran) and with the row rule as it stood until 11:17:14 PST (E91's three anchor rows kept).
That rule is applied to an in-memory copy of fit_m5.py's source with one line changed back; the file on disk is not
touched. Everything else reads loko.json, m5.json, rows.json, check-e102.json and E102's committed inputs. Bootstraps
resample kinds with fixed seeds, so the output reproduces exactly. Everything here was computed after the data and after
the freeze: post hoc, at the desk.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m5 as F  # noqa: E402  (the committed fit, unmodified)

load = F.load
L = load(os.path.join(HERE, "loko.json"))
M5 = load(os.path.join(HERE, "m5.json"))
PRE_LOOK = ("F0_M4", "F1_split", "F2_stages", "F3_split_fft", "F4_M4_abits", "F5_split_abits", "F6_split_abits_gtr",
            "F7_M4_gtr", "F8_stages_abits_gtr")
RULE_NOW = 'if e not in ("E78", "E82") and n in ("randn", "full"):'
RULE_FIRST = 'if e not in ("E78", "E82") and n in ("randn", "full") and e != "E91":'


def rms(v):
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    return float(np.sqrt(np.mean(v ** 2))) if len(v) else float("nan")


def fit_module(e91_kept):
    """fit_m5.py as committed, or (e91_kept) with its row rule as it stood until 11:17:14 PST."""
    if not e91_kept:
        return F
    src = open(os.path.join(HERE, "fit_m5.py")).read()
    assert src.count(RULE_NOW) == 1
    mod = types.ModuleType("fit_m5_first_row_rule")
    mod.__file__ = os.path.join(HERE, "fit_m5.py")
    exec(compile(src.replace(RULE_NOW, RULE_FIRST), mod.__file__, "exec"), mod.__dict__)
    return mod


def nested(mod, fam, forms):
    """fit_m5.main's nested procedure: per held-out kind, every form scored by leave-one-kind-out on the rest, the best
    refitted on the rest, the held-out kind predicted."""
    outer = np.full(len(fam.y), np.nan)
    picks = {}
    for k in range(len(fam.kinds)):
        score = {fn: mod.rms(fam.loko(fn, (k,))) for fn in forms}
        best = min(score, key=score.get)
        b, s = fam.fit(best, {k})
        m = fam.kid == k
        outer[m] = fam.y[m] - fam.pred(best, b, s, m)
        picks[best] = picks.get(best, 0) + 1
    return outer, picks


def pools(fam, err):
    tys = np.array([r["type"] for r in fam.rows])
    out = {}
    for t in sorted(set(tys)):
        for cd, cm in (("a3", ~fam.c1), ("c1", fam.c1)):
            e = err[(tys == t) & cm]
            e = e[~np.isnan(e)]
            if len(e):
                out[f"{t}|{cd}"] = f"{rms(e):.4f} (n {len(e)})"
    return out


def boot_rms_by_kind(errs, kinds, seed, n=10000):
    by = {}
    for e, k in zip(errs, kinds):
        by.setdefault(k, []).append(e * e)
    ks = sorted(by)
    S = np.array([sum(by[k]) for k in ks])
    N = np.array([len(by[k]) for k in ks])
    rng = np.random.default_rng(seed)
    bs = np.empty(n)
    for i in range(n):
        ix = rng.integers(0, len(ks), len(ks))
        bs[i] = math.sqrt(S[ix].sum() / N[ix].sum())
    return math.sqrt(S.sum() / N.sum()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), len(ks)


def main():
    P = print
    RF = L["families"]["float"]["row_errors"]
    RI = L["families"]["int8"]["row_errors"]

    # ------------------------------------------------------------------ C1
    P("== C1. The model search, as first run and as committed (fit_m5.py's own code; post hoc)")
    P("   the first fit, 11:05:47-11:10:07 PST: forms F0-F8, E91's anchors kept, 258 float / 75 int8 rows (the 31 tiles of")
    P("   counts-q133b-train.json not yet counted): nested 0.216 W, picks F7_M4_gtr 120 / F2_stages 4, F0 plain 0.215 W")
    P("   (its printed output; the run is not repeated here because its rows no longer exist on disk)")
    variants = (("committed: F0-F12, committed rows (a check of this code against loko.json)", False, None),
                ("A: F0-F8 only (the forms written before any fit ran), committed rows", False, PRE_LOOK),
                ("B: F0-F12, E91's three anchor rows kept (the row rule before 11:17:14)", True, None),
                ("C: F0-F8, E91's anchor rows kept (the first fit's procedure on the final tiles)", True, PRE_LOOK))
    fams = {}
    for lab, e91, keep in variants:
        mod = fit_module(e91)
        if e91 not in fams:
            rows, _ = mod.assemble()
            fams[e91] = (mod, rows)
        mod, rows = fams[e91]
        fr = [r for r in rows if r["type"] != "int8"]
        forms = {fn: t for fn, t in mod.FORMS["float"].items() if keep is None or fn in keep}
        fam = mod.Family(fr, forms)
        outer, picks = nested(mod, fam, forms)
        f0 = rms(fam.loko("F0_M4"))
        extra = f", F10 plain {rms(fam.loko('F10_add_by_format')):.4f}" if "F10_add_by_format" in forms else ""
        P(f"   {lab}")
        P(f"      rows {len(fr)}, kinds {len(fam.kinds)}: nested {rms(outer):.4f} W, picks {picks}; F0 plain {f0:.4f} W{extra}")
        P(f"      nested pools by format|card: {pools(fam, outer)}")
        if lab.startswith("committed"):
            assert abs(rms(outer) - L["families"]["float"]["nested_loko"]["all"]) < 1e-9, "nested() does not reproduce loko.json"
            P("      reproduces loko.json's nested_loko.all exactly")
    for e91 in (False, True):
        mod, rows = fams[e91]
        fr = [r for r in rows if r["type"] == "int8"]
        fam = mod.Family(fr, mod.FORMS["int8"])
        outer, picks = nested(mod, fam, mod.FORMS["int8"])
        P(f"   int8, {'E91 int8.full kept' if e91 else 'committed rows'}: rows {len(fr)}, nested {rms(outer):.4f} W, picks {picks}, I0 plain {rms(fam.loko('I0_I3')):.4f} W")
    extra_rows = [(e, r["key"], r["D"]) for e, r in ((r["exp"], r) for r in fams[True][1])
                  if not any(q["exp"] == e and q["key"] == r["key"] for q in fams[False][1])]
    P(f"   E91's rows the 11:17:14 change removed: {extra_rows}")
    # the float rows first counted after the forms changed (counts-q133b-train.json, counted 11:35-12:00)
    T = load(os.path.join(HERE, "counts-q133b-train.json"))["rows"]
    shas = set()
    for v in T.values():
        pre, base = v["kind"].split("_", 1)
        shas.add(F.sha(open(os.path.join(F.K, pre, "tiles", v["type"], base + ".bin"), "rb").read()))
    ROWS = load(os.path.join(HERE, "rows.json"))
    late = {(r["exp"], r["key"]) for r in ROWS if r["tile_sha256"] in shas}
    for fname, R in (("float", RF), ("int8", RI)):
        rr = [r for r in R if (r["exp"], r["key"]) in late]
        P(f"   {fname} rows whose tiles were counted after the forms changed (11:35-12:00): n {len(rr)}; nested {rms([r['nested_err_w'] for r in rr]):.3f}, "
          f"M4's form refitted (plain) {rms([r['m4_form_loko_err_w'] for r in rr]):.3f}, chosen form plain {rms([r['chosen_form_loko_err_w'] for r in rr]):.3f}, M4 frozen {rms([r['m4_frozen_err_w'] for r in rr]):.3f} W")

    # ------------------------------------------------------------------ C2
    P("\n== C2. What the per-format term buys (loko.json, m5.json, check-e102.json; post hoc)")
    kid = [r["kind"] for r in RF]
    ks = sorted(set(kid))
    ki = {k: i for i, k in enumerate(ks)}
    s1 = np.zeros(len(ks)); s0 = np.zeros(len(ks)); nk = np.zeros(len(ks))
    for r in RF:
        i = ki[r["kind"]]
        s1[i] += r["nested_err_w"] ** 2
        s0[i] += r["m4_form_loko_err_w"] ** 2
        nk[i] += 1
    pt = math.sqrt(s1.sum() / nk.sum()) - math.sqrt(s0.sum() / nk.sum())
    rng = np.random.default_rng(1)
    d = np.empty(20000)
    for i in range(len(d)):
        ix = rng.integers(0, len(ks), len(ks))
        d[i] = math.sqrt(s1[ix].sum() / nk[ix].sum()) - math.sqrt(s0[ix].sum() / nk[ix].sum())
    P(f"   rms(M5's nested) - rms(M4's form refitted, plain LOKO): {pt:+.4f} W; paired bootstrap over {len(ks)} kinds (20,000, seed 1): "
      f"95% CI [{np.percentile(d, 2.5):+.4f}, {np.percentile(d, 97.5):+.4f}] W, P(d >= 0) = {np.mean(d >= 0):.3f}")
    f = M5["families"]["float"]
    terms, C, c = f["terms"], np.array(f["cov_J2"]) * 1e30, f["coef_fJ"]
    i32, i16 = terms.index("add32"), terms.index("add16")
    var = C[i32, i32] + C[i16, i16] - 2 * C[i32, i16]
    P(f"   add32 {c[i32]:.4f}, add16 {c[i16]:.4f} fJ: difference {c[i32] - c[i16]:.4f} +- {math.sqrt(var):.4f} fJ (1 s.e., jackknife by kind), "
      f"z {(c[i32] - c[i16]) / math.sqrt(var):.2f}, correlation {C[i32, i16] / math.sqrt(C[i32, i32] * C[i16, i16]):.3f}; add16 / add32 = {c[i16] / c[i32]:.4f}")
    groups = (
        ("E103, all", lambda r: r["exp"] == "E103"),
        ("E103's A-side tiles (h_a_*, o_a_*)", lambda r: r["exp"] == "E103" and r["key"].split(".", 1)[1][:4] in ("h_a_", "o_a_")),
        ("real tensors (E86, E91, E95)", lambda r: r["exp"] in ("E86", "E91", "E95")),
        ("fp16 sign tiles, E92", lambda r: r["exp"] == "E92" and r["key"].startswith("fp16")),
        ("fp16 sign tiles, E104", lambda r: r["exp"] == "E104" and r["key"].startswith("fp16")),
        ("fp32 sign tiles, E92", lambda r: r["exp"] == "E92" and r["key"].startswith("fp32")),
        ("fp32 sign tiles, E104", lambda r: r["exp"] == "E104" and r["key"].startswith("fp32")),
        ("E106", lambda r: r["exp"] == "E106"),
        ("E94's draws", lambda r: r["exp"] == "E94"),
        ("all fp32", lambda r: r["key"].startswith("fp32")),
        ("all fp16", lambda r: r["key"].startswith("fp16")),
        ("all floats", lambda r: True),
        ("floats outside E78 (M4 never fitted on them)", lambda r: r["exp"] != "E78"),
        ("floats outside E78 and E82 (nor its card scale)", lambda r: r["exp"] not in ("E78", "E82")),
    )
    P(f"   {'group':48s} {'n':>4s} {'M5 nested':>10s} {'F10 plain':>10s} {'M4 form refit':>14s} {'M4 frozen':>10s}")
    for g, sel in groups:
        rr = [r for r in RF if sel(r)]
        P(f"   {g:48s} {len(rr):4d} {rms([r['nested_err_w'] for r in rr]):10.3f} {rms([r['chosen_form_loko_err_w'] for r in rr]):10.3f} "
          f"{rms([r['m4_form_loko_err_w'] for r in rr]):14.3f} {rms([r['m4_frozen_err_w'] for r in rr]):10.3f}")
    # E102 with M4's form refitted on all rows beside M5 and M4 as frozen (check_e102.py's own reading of E102)
    E102 = os.path.join(F.DD, "2026-11-01-e102-balanced-bit-prices")
    sc = load(os.path.join(E102, "scored.json"))["primary"]
    c102 = load(os.path.join(E102, "bench", "counts-e102.json"))["rows"]
    t102 = load(os.path.join(F.K, "e102", "e102.json"))["tiles"]
    zc = load(os.path.join(F.B, "counts-v2.json"))["rows"]
    sys.path.insert(0, HERE)
    import check_e102 as CE  # noqa: E402
    from predict_blind3 import m4_reproduced  # noqa: E402
    m4 = m4_reproduced(fams[False][1])
    f0 = L["families"]["float"]["coef_fJ_fit_on_all_by_form"]["F0_M4"]
    models = {
        "M5": {"float": (np.array(f["coef_J"]), f["terms"], f["card1_scale"]),
               "int8": (np.array(M5["families"]["int8"]["coef_J"]), M5["families"]["int8"]["terms"], M5["families"]["int8"]["card1_scale"])},
        "F0 refit": {"float": (np.array([f0[q] * 1e-15 for q in F.FORMS["float"]["F0_M4"]]), F.FORMS["float"]["F0_M4"], f["card1_scale"]),
                     "int8": (np.array(M5["families"]["int8"]["coef_J"]), M5["families"]["int8"]["terms"], M5["families"]["int8"]["card1_scale"])},
        "M4 frozen": {fam: (m4[fam]["b"], m4[fam]["terms"], m4[fam]["scale"]) for fam in ("float", "int8")},
    }

    def feats(kind, t):
        z = c102[f"{t}.zeros"]["mean"] if f"{t}.zeros" in c102 else zc[f"{t}.zeros"]["mean"]
        ff = F.fmt_feats(F.bench_feats(c102[kind]["mean"], z), t)
        ff.update({k: v for k, v in F.tile_feats(os.path.join(F.K, "e102", "tiles", t, kind.split(".", 1)[1] + ".bin"), t).items() if k != "sha256"})
        return ff

    P("   E102's single-bit prices (check_e102.py's reading; neither model fitted on them), rms W: M5 / M4's form refitted on all rows / M4 frozen")
    chk = load(os.path.join(HERE, "check-e102.json"))
    for g, want in CE.GROUPS.items():
        y, p = [], {w: [] for w in models}
        for name, e in sc["prices"].items():
            if not want(e) or e["board"]["W"]["mean"] is None:
                continue
            t = e["type"]
            kind = f"{t}.{name.split('@')[0].split('.', 1)[1]}"
            z = t102[kind].get("zero")
            if z is None or kind not in c102:
                continue
            zk = z if "." in z else f"{t}.{z}"
            if zk not in c102:
                continue
            fa, fz = feats(kind, t), feats(zk, t)
            fam = "int8" if t == "int8" else "float"
            y.append(e["board"]["W"]["mean"])
            for w, M in models.items():
                b, tt, s = M[fam]
                p[w].append(float(np.array([F.RATE[t] * (fa[q] - fz[q]) for q in tt]) @ b) * s)
        y = np.array(y)
        r = {w: rms(y - np.array(v)) for w, v in p.items()}
        assert abs(r["M5"] - chk[g]["M5"]["rms_w"]) < 1e-9 and abs(r["M4 frozen"] - chk[g]["M4"]["rms_w"]) < 1e-9
        P(f"      {g:16s} n {len(y):2d}: {r['M5']:.3f} / {r['F0 refit']:.3f} / {r['M4 frozen']:.3f}  (M5 - M4 frozen {r['M5'] - r['M4 frozen']:+.3f})")
    P("      M5 and M4 frozen reproduce check-e102.json exactly; int8's 'refit' is M5's own int8 (I3 refitted)")

    # ------------------------------------------------------------------ C3
    P("\n== C3. Figures the blog points need")
    for fname, R in (("float", RF), ("int8", RI)):
        D = [r["D"] for r in R]
        P(f"   {fname}: D over the type's zeros runs {min(D):.2f} to {max(D):.2f} W over {len(D)} rows")
    P(f"   M5's float constants: {len(f['terms'])} ({', '.join(f['terms'])}) plus the card-1 scale {f['card1_scale']:.4f}; "
      f"int8: {len(M5['families']['int8']['terms'])} plus {M5['families']['int8']['card1_scale']:.4f}")
    want = {("E104", "fp32.w_h_add"), ("E104", "fp16.w_h_add"), ("E92", "fp32.w_h_add"), ("E92", "fp16.w_h_add"), ("E88", "int8.r_cancel"),
            ("E103", "fp32.c_near_rand"), ("E103", "fp32.s_bhalf_alt"), ("E103", "fp32.x_e_g"), ("E103", "int8.i_a127_bfull")}
    for R in (RF, RI):
        for r in R:
            if (r["exp"], r["key"]) in want:
                P(f"   {r['exp']:5s} {r['key']:22s} D {r['D']:6.2f}  nested {r['nested_err_w']:+.3f}  M4 frozen {r['m4_frozen_err_w']:+.3f} W (D - prediction)")
    int8_worst = max(RI, key=lambda r: abs(r["nested_err_w"]))
    P(f"   int8's largest nested miss: {int8_worst['exp']} {int8_worst['key']} {int8_worst['nested_err_w']:+.3f} W")

    # ------------------------------------------------------------------ C4
    P("\n== C4. int8 out of sample (loko.json row_errors): M5 nested / I3's form refitted, plain LOKO / M4 frozen")
    for lab, sel in (("all", lambda r: True), ("outside E78 (M4 never fitted on them)", lambda r: r["exp"] != "E78"),
                     ("outside E78 and E82 (nor its card scale)", lambda r: r["exp"] not in ("E78", "E82")), ("E78 only (M4 in-sample)", lambda r: r["exp"] == "E78")):
        rr = [r for r in RI if sel(r)]
        P(f"   {lab:42s} n {len(rr):3d}: {rms([r['nested_err_w'] for r in rr]):.3f} / {rms([r['m4_form_loko_err_w'] for r in rr]):.3f} / {rms([r['m4_frozen_err_w'] for r in rr]):.3f} W")

    # ------------------------------------------------------------------ C5
    P("\n== C5. The contrast intervals' stand-in, tried on the training rows (nested errors, pairs of kinds in one experiment, type and card)")
    pool = {**M5["families"]["float"]["interval_pool_by_format_card"], **M5["families"]["int8"]["interval_pool_by_format_card"]}
    card = {r["exp"]: r["card"] for r in ROWS}
    for fname, R in (("float", RF), ("int8", RI)):
        grp = {}
        for r in R:
            t = r["key"].split(".", 1)[0]
            grp.setdefault((r["exp"], t, card[r["exp"]]), []).append(r)
        inside = tot = 0
        sd = se = 0.0
        for (e, t, cd), rr in grp.items():
            pl = pool[f"{t}|{cd}"]
            half = F.t975(pl["n"] - 2) * math.sqrt(2) * pl["rms_w"]
            for i in range(len(rr)):
                for j in range(i + 1, len(rr)):
                    if rr[i]["kind"] == rr[j]["kind"]:
                        continue
                    dd = rr[i]["nested_err_w"] - rr[j]["nested_err_w"]
                    tot += 1
                    inside += abs(dd) <= half
                    sd += dd * dd
                    se += rr[i]["nested_err_w"] ** 2 + rr[j]["nested_err_w"] ** 2
        P(f"   {fname}: {tot} pairs; the difference inside t x sqrt(pool_i^2 + pool_j^2) for {inside} ({inside / tot:.3f}); "
          f"rms(difference) / rms(quadrature of the two errors) = {math.sqrt(sd / se):.3f} (1 = uncorrelated, below 1 = positively correlated)")

    # ------------------------------------------------------------------ C7
    P("\n== C7. Intervals: the constants' 1 s.e. and 1.96 s.e. (jackknife by kind), and the nested rms with a 95% bootstrap over kinds")
    for fname in ("float", "int8"):
        ff = M5["families"][fname]
        se = np.sqrt(np.diag(np.array(ff["cov_J2"]))) * 1e15
        P(f"   {fname}: " + "; ".join(f"{q} {v:.3f} +- {s:.3f} (95% +- {1.96 * s:.3f})" for q, v, s in zip(ff["terms"], ff["coef_fJ"], se)) + " fJ")
        P(f"   {fname}: card-1 scale {ff['card1_scale']:.4f} +- {ff['card1_scale_se']:.4f} (1 s.e.)")
    for lab, R, pre in (("floats", RF, None), ("fp32", RF, "fp32"), ("fp16", RF, "fp16"), ("int8", RI, None)):
        rr = [r for r in R if pre is None or r["key"].startswith(pre)]
        pt, lo, hi, nk_ = boot_rms_by_kind([r["nested_err_w"] for r in rr], [r["kind"] for r in rr], seed=7)
        P(f"   {lab:6s}: nested rms {pt:.3f} W, 95% bootstrap over {nk_} kinds (10,000, seed 7) [{lo:.3f}, {hi:.3f}], n {len(rr)} rows")

    # ------------------------------------------------------------------ C8
    P("\n== C8. M4's forms refitted on E78's rows alone (rows.json), against M4 as frozen (predictions-blind3.json models.M4)")
    PM4 = load(os.path.join(F.K, "blind3", "predictions-blind3.json"))["models"]["M4"]
    for fam, want, fn in (("float", lambda r: r["type"] != "int8", "F0_M4"), ("int8", lambda r: r["type"] == "int8", "I0_I3")):
        fr = [r for r in ROWS if want(r) and r["exp"] == "E78"]
        fa = F.Family(fr, {fn: F.FORMS[fam][fn]})
        b, _ = fa.fit(fn, set())
        P(f"   {fam}: {len(fr)} E78 rows -> " + ", ".join(f"{q} {x * 1e15:.3f}" for q, x in zip(F.FORMS[fam][fn], b))
          + " fJ; M4 as frozen " + ", ".join(f"{x:.3f}" for x in PM4[fam]["coef_fJ"]) + " fJ")


if __name__ == "__main__":
    main()
