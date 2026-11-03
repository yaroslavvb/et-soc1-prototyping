#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q139(m), corrections after verification (Tue 3 Nov 2026): every number that the README's dated notes and its section
"Corrections after verification" quote, from committed inputs only. M8's frozen code is imported unchanged (fit_m8.py and,
through it, fit_m7.py, reduce_footing.py, make_blind5.py, posthoc_m7_e147.py and E119's dither), and predict_blind6.py is
run unchanged on blind pool 5 into a scratch dir. Post hoc: nothing here is registered or frozen, nothing is refitted into
M8, and no frozen file is written. It checks itself against the committed nested-m8.json and m8.json first.

    python3 -B corrections-numbers.py <scratch dir>     # a few minutes; writes corrections-numbers.json and .txt beside it

K1  aifoundry2 end to end with the cap held out per kind as well (verification fault 1)
K2  the peak's 95% value as registered and as frozen (D5); aifoundry2's scale over all bursts and pinned only (D6)
K3  aifoundry2's measured scale under a steeper s(f), approximately (fault 3)
K4  where M8's gain over M7 and M6 as frozen comes from (fault 4)
K5  the peak rule's coverage on pool 5, in sample (fault 5)
K6  int8's named pool-5 misses, M8 against M7's form (fault 6)
K7  the card term: chosen once on all rows (fault 7)
K8  A2's dips on aifoundry2 against a minion clock change (fault 8)
K9  the files predict_blind6.py reads at run time, against 122da8b6 (fault 9)
K10 the git times of the registration and the freeze (fault 10)

SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import os  # noqa: E402

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "6")
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FREEZE, REGISTRATION = "122da8b6", "f640fb7a"


def trace_run(out_json, args):
    """Run predict_blind6.py unchanged in this process and record every file it opens and every module it imports."""
    seen = set()

    def hook(ev, a):
        if ev == "open" and a and isinstance(a[0], (str, bytes)):
            p = a[0].decode(errors="replace") if isinstance(a[0], bytes) else a[0]
            seen.add(os.path.abspath(p))
    sys.addaudithook(hook)
    import runpy
    target = os.path.join(HERE, "predict_blind6.py")
    sys.argv = [target] + list(args)
    code = 0
    try:
        runpy.run_path(target, run_name="__main__")
    except SystemExit as e:  # predict_blind6 exits 2 without counts
        code = e.code
    mods = sorted({os.path.abspath(m.__file__) for m in list(sys.modules.values()) if getattr(m, "__file__", None)})
    with open(out_json, "w") as fh:
        json.dump({"opened": sorted(seen), "modules": mods, "exit": code}, fh, indent=1)


if len(sys.argv) > 2 and sys.argv[1] == "--trace-run":
    trace_run(sys.argv[2], sys.argv[3:])
    sys.exit(0)

import numpy as np  # noqa: E402

sys.path.insert(0, HERE)
import fit_m8 as M8  # noqa: E402  (unchanged; imports fit_m7, fit_m6, fit_m5, reduce_footing, make_blind5, posthoc_m7_e147)
import make_predictions_e119 as M119  # noqa: E402  (fit_m8 put tools/claims-v3/e119 on the path)

M7, RF = M8.M7, M8.RF
ROOT, DD, CV, FOOT, B5, M7D = M8.ROOT, M8.DD, M8.CV, M8.FOOT, M8.B5, M8.M7D
load = M8.load
rms = M8.rms
rel_ = lambda p: os.path.relpath(p, ROOT)  # noqa: E731
r4 = lambda x: None if x is None else round(float(x), 4)  # noqa: E731
LINES = []


def say(s):
    LINES.append(s)
    print(s, flush=True)


def git(*a, env=None, binary=False):
    r = subprocess.run(["git", *a], cwd=ROOT, capture_output=True, env=env)
    return r.returncode, (r.stdout if binary else r.stdout.decode())


# ------------------------------------------------------------------ the committed numbers this script must reproduce
NM8 = load(os.path.join(HERE, "nested-m8.json"))
FM8 = load(os.path.join(HERE, "m8.json"))
ROWS = load(os.path.join(HERE, "rows-m8.json"))
M6J = load(os.path.join(M7.M6D, "m6.json"))
M7J = load(os.path.join(M7D, "m7.json"))
CHECKS = []


def check(name, got, want, tol=1e-9):
    ok = (got is None and want is None) or (got is not None and want is not None and abs(float(got) - float(want)) <= tol)
    CHECKS.append({"check": name, "got": got, "committed": want, "ok": bool(ok)})
    if not ok:
        say(f"SELF-CHECK FAILED: {name}: {got} against the committed {want}")
    return ok


# ------------------------------------------------------------------ K4 (and nested D for K1): the power families, M8's code
def power_family(famname):
    fr = [r for r in ROWS if (r["type"] == "int8") == (famname == "int8")]
    out, frozen, outer = M8.run_family(fr, famname, M6J, M7J)
    forms = {**M8.FORMS8[famname], **M8.REFFORMS[famname]}
    fam = M7.Fam(fr, forms, out["card_term_chosen"])
    e7 = fam.y - M8.frozen_pred(fr, M7J["families"][famname], True)
    e6 = fam.y - M8.frozen_pred(fr, M6J["families"][famname], False)
    p7 = fam.loko(M8.M7FORM[famname])
    com = NM8["families"][famname]
    check(f"{famname}: M8 nested rms", out["same_folds"]["all"]["M8_nested"]["rms_w"], com["same_folds"]["all"]["M8_nested"]["rms_w"])
    check(f"{famname}: M7's form rms", rms(p7), com["same_folds"]["all"]["M7_form_loko"]["rms_w"])
    check(f"{famname}: M7 frozen rms", rms(e7), com["same_folds"]["all"]["M7_frozen"]["rms_w"])
    for lab in ("M7_form_loko", "M7_frozen", "M6_frozen"):
        for q in ("d_rms_w", "lo95", "hi95"):
            check(f"{famname}: paired M8 - {lab} {q}", out["paired_bootstrap_over_kinds_M8_minus"][lab][q],
                  com["paired_bootstrap_over_kinds_M8_minus"][lab][q])
    check(f"{famname}: frozen c coefficients", float(np.max(np.abs(np.array(frozen["coef_J"]) - np.array(FM8["families"][famname]["coef_J"])))), 0.0, 1e-24)
    return fr, out, frozen, outer, fam, e7, e6, p7


def k4(fams):
    res = {}
    for famname, (fr, out, frozen, outer, fam, e7, e6, p7) in fams.items():
        b = lambda ea, eb: M8.boot_diff(fam.kid, ea, eb)  # noqa: E731
        res[famname] = {
            "rms_w": {"M8_nested": rms(outer), "M7_form_loko": rms(p7), "M7_frozen": rms(e7), "M6_frozen": rms(e6)},
            "M8_minus_M7_form": b(outer, p7), "M7_form_minus_M7_frozen": b(p7, e7), "M7_form_minus_M6_frozen": b(p7, e6),
            "M8_minus_M7_frozen": b(outer, e7), "M8_minus_M6_frozen": b(outer, e6),
            "note": "paired bootstrap over kinds, 2,000 draws, seed 139 (fit_m8.boot_diff); M8 - M7 frozen = (M8 - M7's form) + (M7's form - M7 frozen)",
        }
        if famname == "float":
            terms = frozen["terms"]
            j = terms.index("c_end")
            cj = frozen["coef_J"][j]
            s1 = frozen["card1_scale_by_format"]
            w = np.array([r["rate"] * float(r["f"]["c_end"]) * cj * (s1[r["type"]] if r["card"] == "c1" else 1.0) for r in fr])
            res[famname]["c_end_term_w"] = {"n_rows": len(w), "mean_w": float(np.mean(w)), "mean_abs_w": float(np.mean(np.abs(w))),
                                            "max_abs_w": float(np.max(np.abs(w))), "mean_D_w": float(np.mean([r["D"] for r in fr]))}
    f = res["float"]
    say("K4 floats: rms M8 %.4f, M7's form %.4f, M7 frozen %.4f, M6 frozen %.4f W" % tuple(f["rms_w"][k] for k in ("M8_nested", "M7_form_loko", "M7_frozen", "M6_frozen")))
    for k in ("M8_minus_M7_form", "M7_form_minus_M7_frozen", "M7_form_minus_M6_frozen", "M8_minus_M7_frozen", "M8_minus_M6_frozen"):
        v = f[k]
        say(f"   {k}: {v['d_rms_w']:+.4f} [{v['lo95']:+.4f}, {v['hi95']:+.4f}] resolved {v['resolved']}")
    c = f["c_end_term_w"]
    say(f"   the C term on the {c['n_rows']} float rows: mean {c['mean_w']:.4f} W, mean |.| {c['mean_abs_w']:.4f}, at most {c['max_abs_w']:.3f} W (mean D {c['mean_D_w']:.2f} W)")
    i8 = res["int8"]
    for k in ("M8_minus_M7_form", "M7_form_minus_M7_frozen", "M8_minus_M7_frozen"):
        v = i8[k]
        say(f"K4 int8 {k}: {v['d_rms_w']:+.4f} [{v['lo95']:+.4f}, {v['hi95']:+.4f}] resolved {v['resolved']}")
    return res


# ------------------------------------------------------------------ K1, K2(b), K3: aifoundry2's bursts (fit_m8.a2_fit's cells and relation)
def a2_cells():
    P136 = load(os.path.join(CV, "e136", "predictions-e136.json"))
    rel = P136["relation"]
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
                          "burst_w": float(c["burst_w"]), "c_w": float(c["c_w"]), "D600_meas": Dm, "zero": n == "zeros"})
    r143 = load(os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "results.json"))
    for lab, c in r143["cells"].items():
        if "name" in c:
            name, t = c["name"], c["type"]
            it = d141.get(name) or {}
        else:
            _, t, n = lab.split("-", 2)
            name = f"{t}.{n}"
            it = d78.get(name) or {}
        z = name.endswith("zeros")
        Dm = 0.0 if z else ((it.get("D") or {}).get("mean"))
        cells.append({"exp": "E143", "type": t, "kind": name, "src_key": name, "burst_mhz": float(c["burst_mhz"]),
                      "burst_w": float(c["burst_w"]), "c_w": float(statistics.mean(c["c_w_runs"])), "D600_meas": Dm, "zero": z})
    cells = [c for c in cells if c["D600_meas"] is not None]
    return rel, cells


def k1(nested_D):
    rel, cells = a2_cells()
    B = {int(k): v for k, v in rel["B"].items()}
    SF = {int(k): v for k, v in rel["s_f"].items()}
    CZ7, XFER, SB = dict(rel["c_zeros_w"]), rel["xfer"], rel["burst"][1]
    W7 = M7J["aifoundry2"]["burst_cap"]["W_star_used_w"]
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
    curves = np.array([[clock(c["c_w"], W) for W in WG] for c in cells])
    P8m = np.array([B[800] + c["c_w"] * SF[800] for c in cells])
    meas_f = np.array([c["burst_mhz"] for c in cells])

    def clk_at(idx, Wv):
        u = (np.clip(Wv, WG[0], WG[-1]) - WG[0]) / 0.1
        j = np.clip(u.astype(int), 0, len(WG) - 2)
        fr = u - j
        return curves[idx, j] * (1.0 - fr) + curves[idx, j + 1] * fr

    def fit_W0(train):            # fit_m8's fit_cap for the kept configuration (gamma 0)
        idx = np.array(train)
        best = None
        for W0 in np.arange(55.0, 75.0001, 0.1):
            e = np.sum((clk_at(idx, W0 + 0.0 * np.maximum(0.0, P8m[idx] - W0)) - meas_f[idx]) ** 2)
            if best is None or e < best[0]:
                best = (e, W0)
        return best[1]

    def predict(t, D, W0, cz=None, g=None):
        cz = CZ7 if cz is None else cz
        g = (1.0 / XFER) if g is None else g
        c = cz[t] + g * D
        f = clock(c, W0)
        return f, p_at(levels(c), f)

    def score(W0_of_kind, cz=None, g=None):
        rows = []
        for c in cells:
            Dp = 0.0 if c["zero"] else nested_D.get(c["src_key"])
            if Dp is None:
                continue
            f, P = predict(c["type"], Dp, W0_of_kind(c["kind"]), cz, g)
            rows.append((c["exp"], c["burst_mhz"] < 795, c["burst_mhz"] - f, c["burst_w"] - P))
        em, ew = np.array([x[2] for x in rows]), np.array([x[3] for x in rows])
        gov = np.array([x[1] for x in rows])
        exps = np.array([x[0] for x in rows])
        out = {"n": len(rows), "rms_mhz": rms(em), "rms_board_w": rms(ew), "q95_abs_mhz": M7.q95(em), "q95_abs_board_w": M7.q95(ew),
               "governed_below_795": {"n": int(gov.sum()), "rms_mhz": rms(em[gov]), "rms_board_w": rms(ew[gov]), "bias_board_meas_minus_pred_w": float(np.mean(ew[gov]))},
               "pinned_795_800": {"n": int((~gov).sum()), "rms_mhz": rms(em[~gov]), "rms_board_w": rms(ew[~gov])}}
        for e in ("E80", "E83", "E143"):
            m = exps == e
            out[e] = {"n": int(m.sum()), "rms_mhz": rms(em[m]), "rms_board_w": rms(ew[m])}
        m = np.isin(exps, ["E80", "E83"])
        out["E80+E83"] = {"n": int(m.sum()), "rms_mhz": rms(em[m]), "rms_board_w": rms(ew[m])}
        return out
    W0_all = fit_W0(list(range(len(cells))))
    check("aifoundry2: W0 on all bursts", W0_all, FM8["aifoundry2"]["params"]["W0"])
    cap_all = score(lambda k: W0_all)
    com = NM8["aifoundry2"]["end_to_end_from_M8_nested_D"]
    check("aifoundry2 e2e: clock rms (cap on all bursts)", cap_all["rms_mhz"], com["rms_mhz"])
    check("aifoundry2 e2e: board rms (cap on all bursts)", cap_all["rms_board_w"], com["rms_board_w"])
    check("aifoundry2 e2e: q95 clock", cap_all["q95_abs_mhz"], com["q95_abs_mhz"])
    W0k = {k: fit_W0([i for i, c in enumerate(cells) if c["kind"] != k]) for k in kinds}
    cap_kind = score(lambda k: W0k[k])
    m7f = score(lambda k: W7)
    check("aifoundry2 e2e: M7 frozen clock rms", m7f["rms_mhz"], NM8["aifoundry2"]["M7_frozen_relation_same_cells"]["rms_mhz"])
    w0v = np.array(list(W0k.values()))
    res = {"n_bursts": len(cells), "n_kinds": len(kinds), "by_exp": {e: sum(c["exp"] == e for c in cells) for e in ("E80", "E83", "E143")},
           "W0_all_bursts_w": W0_all, "W0_per_kind_fold_w": {"min": float(w0v.min()), "max": float(w0v.max()), "median": float(np.median(w0v))},
           "e2e_M8_cap_on_all_bursts": cap_all, "e2e_M8_cap_held_out_per_kind": cap_kind, "e2e_M7_frozen_relation": m7f,
           "note": "end to end through M8's nested D (out of kind); 'cap on all bursts' is the frozen m8.json figure (the cap in sample); "
                   "'cap held out per kind' refits W0 without the scored kind; M7's frozen relation was fitted on E80's and E83's bursts "
                   "(in sample there) and never saw E143's"}
    a, b, m = cap_all, cap_kind, m7f
    say(f"K1 aifoundry2, all {a['n']} bursts end to end: M8 cap on all bursts {a['rms_mhz']:.3f} MHz / {a['rms_board_w']:.3f} W (q95 {a['q95_abs_mhz']:.2f} / {a['q95_abs_board_w']:.2f}); "
        f"cap held out per kind {b['rms_mhz']:.3f} / {b['rms_board_w']:.3f} (q95 {b['q95_abs_mhz']:.2f} / {b['q95_abs_board_w']:.2f}); M7 frozen {m['rms_mhz']:.3f} / {m['rms_board_w']:.3f}")
    for lab, o in (("cap all", a), ("cap per kind", b), ("M7 frozen", m)):
        say(f"   {lab}: governed (<795 MHz, {o['governed_below_795']['n']}) {o['governed_below_795']['rms_mhz']:.2f} MHz / {o['governed_below_795']['rms_board_w']:.2f} W, bias {o['governed_below_795']['bias_board_meas_minus_pred_w']:+.2f}; "
            f"pinned ({o['pinned_795_800']['n']}) {o['pinned_795_800']['rms_mhz']:.2f} / {o['pinned_795_800']['rms_board_w']:.2f}; "
            f"E80+E83 ({o['E80+E83']['n']}) {o['E80+E83']['rms_mhz']:.2f} / {o['E80+E83']['rms_board_w']:.2f}; E143 ({o['E143']['n']}) {o['E143']['rms_mhz']:.2f} / {o['E143']['rms_board_w']:.2f}")
    say(f"   W0 per kind fold {res['W0_per_kind_fold_w']['min']:.1f}-{res['W0_per_kind_fold_w']['max']:.1f} W (all bursts {W0_all:.2f})")
    return res, rel, cells, CZ7


def scale_of(cells, cz, keep):
    out = {}
    for fam, lo in (("floats", 5.0), ("int8", 1.0)):
        v = [(c["c_w"] - cz[c["type"]]) / c["D600_meas"] for c in cells
             if not c["zero"] and ("int8" if c["type"] == "int8" else "floats") == fam and c["D600_meas"] >= lo and keep(c)]
        out[fam] = {"median": float(np.median(v)), "n": len(v)}
    return out


def k3(rel, cells, CZ7):
    SF = {int(k): v for k, v in rel["s_f"].items()}
    vr = {f: math.sqrt(SF[f] / (f / 600.0)) for f in (600, 700, 800)}     # V_f / V_600 implied by s(f) = (V/V600)^2 f/600

    def s_n(f, n):
        pt = lambda ff: vr[ff] ** n * ff / 600.0  # noqa: E731
        if f >= 800:
            return pt(800)
        if f >= 700:
            return pt(700) + (pt(800) - pt(700)) * (f - 700) / 100.0
        return pt(600) + (pt(700) - pt(600)) * (f - 600) / 100.0
    res = {"V800_over_V600": vr[800], "method": "approximate: c_w' = c_w x s(f)/s'(f) at the burst's mean clock (linear between 600/700/800 "
                                                "MHz, as p_at), c_zeros' = c_zeros x s(800)/s'(800) (zeros run at 800 MHz); the kspeed reduction's "
                                                "dither weighting is not re-run", "by_n": {}}
    base = None
    for n in (2.0, 2.28, 2.3, 2.45):
        v = []
        for c in cells:
            if c["zero"] or c["type"] == "int8" or c["D600_meas"] < 5.0:
                continue
            r = s_n(c["burst_mhz"], 2.0) / s_n(c["burst_mhz"], n)
            rz = s_n(800, 2.0) / s_n(800, n)
            v.append((c["c_w"] * r - CZ7[c["type"]] * rz) / c["D600_meas"])
        med = float(np.median(v))
        base = med if n == 2.0 else base
        res["by_n"][str(n)] = {"median_float_scale": med, "n": len(v), "change_vs_n2": med / base - 1.0,
                               "factor_at_800_MHz": vr[800] ** (2.0 - n)}
    say("K3 aifoundry2's float scale by the board exponent n (approximate): " + "; ".join(
        f"n {k}: {o['median_float_scale']:.4f} ({o['change_vs_n2'] * 100:+.1f}%; at 800 MHz x{o['factor_at_800_MHz']:.4f})" for k, o in res["by_n"].items()))
    return res


def k2_scale_and_loco(cells, CZ7, k3res):
    allc = scale_of(cells, CZ7, lambda c: True)
    pin = scale_of(cells, CZ7, lambda c: c["burst_mhz"] >= 795.0)
    check("aifoundry2: float scale over all bursts", allc["floats"]["median"], NM8["aifoundry2"]["scale_vs_a3"]["floats"]["median"])
    res = {"scale_all_bursts": allc, "scale_pinned_795_800": pin, "loco_V600": {}}
    variants = {"committed (all bursts, V^2)": allc["floats"]["median"], "pinned 795-800 MHz only (as registered)": pin["floats"]["median"],
                "n = 2.28 (approx.)": k3res["by_n"]["2.28"]["median_float_scale"], "n = 2.45 (approx.)": k3res["by_n"]["2.45"]["median_float_scale"]}
    for lab, a2v in variants.items():
        a2s = {"floats": {"median": a2v}, "int8": {"median": allc["int8"]["median"]}}
        meas, reads, rat = M8.card_scale(ROWS, a2s, CZ7)
        lc = M8.loco(meas, reads)["V600_v"]
        V = reads["V600_v"]
        o = {"a2_scale": a2v}
        for h in ("a3", "c1", "a2"):
            x = lc["held_out"][f"floats|{h}"]
            o[h] = {"physical": x["physical"]["rel_err"], "fitted": x["fitted_on_other_two"]["rel_err"]}
        o["c1_V2_from_aifoundry3_alone"] = (V["c1"] / V["a3"]) ** 2 / meas["c1"]["floats"] - 1.0
        o["a2_V2_from_aifoundry3_alone"] = (V["a2"] / V["a3"]) ** 2 / a2v - 1.0
        o["any_card_fails_1pct"] = any(abs(o[h][q]) > 0.01 for h in ("a3", "c1", "a2") for q in ("physical", "fitted"))
        res["loco_V600"][lab] = o
        if lab.startswith("committed"):
            com = NM8["card_scale"]["loco"]["V600_v"]["held_out"]
            for h in ("a3", "c1", "a2"):
                check(f"card scale LOCO V^2 {h}", o[h]["physical"], com[f"floats|{h}"]["physical"]["rel_err"])
    say(f"K2(b) aifoundry2's float scale: all bursts {allc['floats']['median']:.4f} (n {allc['floats']['n']}); pinned 795-800 MHz {pin['floats']['median']:.4f} (n {pin['floats']['n']}); "
        f"int8 {allc['int8']['median']:.4f} (n {allc['int8']['n']}) / {pin['int8']['median']:.4f} (n {pin['int8']['n']})")
    for lab, o in res["loco_V600"].items():
        say(f"   V^2 LOCO with aifoundry2 at {o['a2_scale']:.4f} [{lab}]: physical a3 {o['a3']['physical'] * 100:+.1f}% / c1 {o['c1']['physical'] * 100:+.1f}% / a2 {o['a2']['physical'] * 100:+.1f}%; "
            f"fitted {o['a3']['fitted'] * 100:+.1f} / {o['c1']['fitted'] * 100:+.1f} / {o['a2']['fitted'] * 100:+.1f}%; card 1 from aifoundry3 alone {o['c1_V2_from_aifoundry3_alone'] * 100:+.1f}%; FAIL {o['any_card_fails_1pct']}")
    return res


# ------------------------------------------------------------------ K5, K2(a), K9: predict_blind6.py run unchanged on pool 5 (aifoundry2)
def run_predictor(scratch):
    od = os.path.join(scratch, "pool5-aifoundry2")
    tr = os.path.join(scratch, "trace-predict-blind6.json")
    cmd = [sys.executable, "-B", os.path.abspath(__file__), "--trace-run", tr, B5, "aifoundry2",
           "--counts", os.path.join(B5, "counts-blind5.json"), "--out", od]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=env)
    if r.returncode:
        raise SystemExit("predict_blind6.py failed: " + r.stderr[-1500:])
    return load(os.path.join(od, "predictions-aifoundry2.json")), load(tr), od


def k5(pred):
    tiles = pred["tiles"]
    pk = FM8["aifoundry2"]["peak"]
    r143 = load(os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "results.json"))
    tdir = os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "aifoundry2", "s1", "tel")
    hi = {}
    for x in r143["run_rows"]:
        fn = os.path.join(tdir, x["run"] + ".jsonl.gz")
        if not os.path.exists(fn) or not str(x.get("label", "")).startswith("b5-"):
            continue
        bw = [json.loads(ln).get("board_w") for ln in gzip.open(fn, "rt") if ln.startswith("{")]
        bw = [v for v in bw if v is not None]
        if bw:
            hi[x["label"][3:]] = max(hi.get(x["label"][3:], 0.0), max(bw))
    rows = []
    for t, h in sorted(hi.items()):
        if t not in tiles or "M8" not in tiles[t]:
            continue
        m = tiles[t]["M8"]
        reg95 = round(m["P800_w"] + pk["excess_q95_w"], 2)       # the registered rule: P800(c) + q95, c at the predicted D
        rows.append({"tile": t, "highest_sample_w": h, "expected_w": m["peak_board_w"], "frozen_hi95_w": m["peak_board_hi95_w"],
                     "registered_95_w": reg95, "frozen_flag": bool(m["peak_over_82w"]), "registered_flag": bool(reg95 > 82.0)})
    over_f = [r for r in rows if r["highest_sample_w"] > r["frozen_hi95_w"]]
    over_r = [r for r in rows if r["highest_sample_w"] > r["registered_95_w"]]
    d = np.array([r["frozen_hi95_w"] - r["registered_95_w"] for r in rows])
    res = {"n_tiles": len(rows), "in_sample": "pool 5 is in M8's fit (E143's traces set the excess)",
           "frozen_rule": {"covered": len(rows) - len(over_f), "over": [[r["tile"], r["highest_sample_w"], r["frozen_hi95_w"]] for r in over_f],
                           "flagged_over_82w": [[r["tile"], r["frozen_hi95_w"], r["highest_sample_w"]] for r in rows if r["frozen_flag"]]},
           "registered_rule": {"covered": len(rows) - len(over_r), "over": [[r["tile"], r["highest_sample_w"], r["registered_95_w"]] for r in over_r],
                               "flagged_over_82w": [[r["tile"], r["registered_95_w"], r["highest_sample_w"]] for r in rows if r["registered_flag"]]},
           "frozen_minus_registered_w": {"median": float(np.median(d)), "min": float(d.min()), "max": float(d.max())},
           "expected_vs_highest_rms_w": rms(np.array([r["highest_sample_w"] - r["expected_w"] for r in rows])),
           "measured_over_82w": [[r["tile"], r["highest_sample_w"]] for r in rows if r["highest_sample_w"] > 82.0],
           "rows": rows, "flag_lists_are": "[tile, the rule's 95% value W, the measured highest sample W]"}
    f, g = res["frozen_rule"], res["registered_rule"]
    say(f"K5 peak on pool 5 (in sample, {len(rows)} tiles): frozen 95% value covers {f['covered']}, over: {f['over']}; flags {len(f['flagged_over_82w'])}: {f['flagged_over_82w']}")
    say(f"   registered P800(c) + q95: covers {g['covered']}, flags {len(g['flagged_over_82w'])}: {g['flagged_over_82w']}; frozen minus registered median {res['frozen_minus_registered_w']['median']:.2f} W "
        f"({res['frozen_minus_registered_w']['min']:.2f}-{res['frozen_minus_registered_w']['max']:.2f}); expected vs highest {res['expected_vs_highest_rms_w']:.2f} W rms; measured over 82 W: {res['measured_over_82w']}")
    return res


def k9(trace, scratch, pool_out):
    files = set(trace["opened"]) | set(trace["modules"])
    rows = []
    me = os.path.abspath(__file__)            # this script ran predict_blind6.py (the tracer): not one of its inputs
    for p in sorted(files):
        if not p.startswith(ROOT + os.sep) or "__pycache__" in p or p.startswith(os.path.abspath(scratch)) or p.startswith(pool_out) or p == me:
            continue
        rel = rel_(p)
        if not os.path.isfile(p):
            continue
        now = hashlib.sha256(open(p, "rb").read()).hexdigest()
        rc, blob = git("show", f"{FREEZE}:{rel}", binary=True)
        then = hashlib.sha256(blob).hexdigest() if rc == 0 else None
        rc2, _ = git("diff", "--quiet", FREEZE, "--", rel)
        rows.append({"path": rel, "sha256": now, "sha256_at_122da8b6": then, "unchanged_since_122da8b6": bool(then == now and rc2 == 0),
                     "kind": ("pool 5 (the pool's own files)" if rel.startswith("tools/claims-v3/kinds/blind5/") and not rel.endswith(".py")
                              else "code or model data")})
    code = [r for r in rows if r["kind"] == "code or model data"]
    res = {"exit": trace["exit"], "n_files": len(rows), "n_code_or_model_data": len(code), "all_unchanged": all(r["unchanged_since_122da8b6"] for r in code),
           "files": rows, "check_command": "git diff --stat 122da8b6 -- " + " ".join(r["path"] for r in code)}
    say(f"K9 predict_blind6.py read {len(code)} code/model files under the tree (plus {len(rows) - len(code)} of pool 5's); every one unchanged since {FREEZE}: {res['all_unchanged']}")
    for r in code:
        say(f"   {r['path']} {r['sha256'][:12]} {'unchanged' if r['unchanged_since_122da8b6'] else 'CHANGED'}")
    return res


# ------------------------------------------------------------------ K6, K7: read from the committed nested-m8.json
def k6():
    want = ("int8.b_line_flipflop_nogate", "int8.b_line_zero_one", "int8.a_word_flipflop", "int8.powerlaw_w",
            "int8.real_pythia_w8a8_down", "int8.real_pythia_w8a8_up")
    rows = [{"exp": r["exp"], "key": r["key"], "D": r["D"], "M8_nested": r["M8_nested"], "M7_form_loko": r["M7_form_loko"], "M7_frozen": r["M7_frozen"]}
            for r in NM8["families"]["int8"]["pool5_rows"] if r["key"] in want and r["exp"] in ("E141", "E142")]
    for r in rows:
        r["M8_worse_by_w"] = abs(r["M8_nested"]) - abs(r["M7_form_loko"])
    say("K6 int8 pool-5 misses (measured - predicted, W), M8 against M7's form: " + "; ".join(
        f"{r['exp']} {r['key'].split('.', 1)[1]} {r['M8_nested']:+.3f} vs {r['M7_form_loko']:+.3f}" for r in rows))
    return {"rows": rows, "source": "nested-m8.json families.int8.pool5_rows (out of kind, nested)"}


def k7():
    res = {}
    for fam in ("float", "int8"):
        ct = NM8["families"][fam]["card_terms"]
        res[fam] = {k: ct[k]["loko_rms_w"] for k in ct if not k.startswith("_")}
        res[fam]["chosen"] = NM8["families"][fam]["card_term_chosen"]
    res["where"] = "fit_m8.py run_family: best_ct (line 250) is chosen before the fold loop (line 259), on every paired kind; fit_m7.Fam then refits its value without the held-out kind in every fold"
    say("K7 card terms, LOKO rms on the paired kinds (W): " + "; ".join(f"{f}: " + ", ".join(f"{k} {v:.4f}" for k, v in o.items() if k != "chosen") + f" -> {o['chosen']}" for f, o in res.items() if f != "where"))
    return res


# ------------------------------------------------------------------ K8: A2's dips on aifoundry2 against a minion clock change
def k8():
    tdir = os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2", "aifoundry2", "s1", "tel")
    nd = ndc = no = noc = ndip_all = 0
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".jsonl.gz"):
            continue
        recs = [json.loads(ln) for ln in gzip.open(os.path.join(tdir, fn), "rt") if ln.startswith("{")]
        _, bad = RF.drop_dips(recs)
        bad = set(bad)
        ndip_all += len(bad)
        B = [r.get("board_w") for r in recs]
        M = [(r.get("mhz") or {}).get("minion") for r in recs]
        for i in range(2, len(recs) - 2):
            if None in (B[i - 2], B[i], B[i + 2]) or None in M[i - 2:i + 3]:
                continue
            chg = len(set(M[i - 2:i + 3])) > 1
            if i in bad:
                if min(B[i - 2], B[i + 2]) >= 55.0:
                    nd += 1
                    ndc += chg
            elif B[i] >= 55.0:
                no += 1
                noc += chg
    res = {"traces": "E143's committed telemetry (aifoundry2/s1/tel, 117 traces)", "dip_rule": "reduce_footing.drop_dips (E82 A2), unchanged",
           "dips_all": ndip_all, "dips_with_neighbours_at_or_over_55w": nd, "dips_with_clock_change_within_2": ndc,
           "other_samples_at_or_over_55w": no, "other_with_clock_change_within_2": noc,
           "share_dips": ndc / nd if nd else None, "share_other": noc / no if no else None,
           "definition": "a clock change = more than one minion clock value over samples i-2..i+2 (mhz.minion)"}
    say(f"K8 E143: {ndip_all} A2 dips; at >= 55 W {nd}, a minion clock change within +-2 samples at {res['share_dips'] * 100:.0f}% of them against {res['share_other'] * 100:.0f}% of the other {no} samples at >= 55 W")
    return res


def k10():
    env = dict(os.environ, TZ="America/Los_Angeles")
    res = {}
    for sha in (REGISTRATION, FREEZE):
        _, s = git("show", "-s", "--format=%h|%ad|%cd", "--date=format-local:%Y-%m-%d %H:%M:%S", sha, env=env)
        h, ad, cd = s.strip().split("|")
        res[h] = {"author_pst": ad, "committer_pst": cd}
    say("K10 git times (PST): " + "; ".join(f"{h} author {v['author_pst']}, committer {v['committer_pst']}" for h, v in res.items()))
    return res


def main():
    scratch = os.path.abspath(sys.argv[1])
    os.makedirs(scratch, exist_ok=True)
    out = {"_note": "Q139(m) corrections-numbers.py: post hoc, after verification, Tue 3 Nov 2026; committed inputs only; M8's frozen code "
                    "imported unchanged; no frozen file written", "freeze": FREEZE, "registration": REGISTRATION}
    say("== Q139(m) corrections after verification: the numbers (post hoc)")
    fams = {f: power_family(f) for f in ("float", "int8")}
    nested_D = {}
    for f, (fr, o, frozen, outer, fam, e7, e6, p7) in fams.items():
        for i, r in enumerate(fr):
            if r["card"] == "a3" and r["exp"] in ("E78", "E141"):
                nested_D[r["key"]] = r["D"] - float(outer[i])
    out["K4_gain_decomposition"] = k4(fams)
    k1res, rel, cells, CZ7 = k1(nested_D)
    out["K1_aifoundry2_cap_held_out"] = k1res
    k3res = k3(rel, cells, CZ7)
    out["K3_aifoundry2_scale_by_exponent"] = k3res
    out["K2b_D6_aifoundry2_scale_and_loco"] = k2_scale_and_loco(cells, CZ7, k3res)
    pred, trace, pool_out = run_predictor(scratch)
    out["K5_and_K2a_D5_peak_pool5"] = k5(pred)
    out["K9_predictor_inputs"] = k9(trace, scratch, pool_out)
    out["K6_int8_pool5_misses"] = k6()
    out["K7_card_term"] = k7()
    out["K8_a2_dips_vs_clock"] = k8()
    out["K10_git_times"] = k10()
    out["self_checks"] = {"n": len(CHECKS), "all_ok": all(c["ok"] for c in CHECKS), "checks": CHECKS}
    say(f"SELF-CHECKS against the committed nested-m8.json / m8.json: {sum(c['ok'] for c in CHECKS)} of {len(CHECKS)} equal")
    with open(os.path.join(HERE, "corrections-numbers.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=float)
    with open(os.path.join(HERE, "corrections-numbers.txt"), "w") as fh:
        fh.write("\n".join(LINES) + "\n")
    if not out["self_checks"]["all_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
