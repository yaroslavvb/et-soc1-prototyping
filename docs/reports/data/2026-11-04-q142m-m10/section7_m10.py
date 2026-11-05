#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(m), dated amendment A2: REGISTRATION.md section 7 ("what would show a term is not wanted, beyond failing its rule"),
read for every term, after a re-run of the registered fit. fit_m10.py did not evaluate section 7; this new file does, by the
reading rules of tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md (A2), committed before this file first ran. fit_m10.py,
m10.json and every committed output stay exactly as they are.

    python3 -B section7_m10.py --rerun-dir <dir> [--out <dir>]   # <dir> must not be this directory; --out defaults to it
    python3 -B section7_m10.py --no-rerun [--out <dir>]          # section 7 on the committed outputs only

1. Checks the registration's 174 inputs (fit_m10.check_inputs) and this directory's SHA256SUMS (68 files) as committed.
2. Re-runs the registered fit (fit_m10.main, unchanged, in this process, every file it opens recorded) into --rerun-dir and
   compares its four outputs with the committed ones: bytes, then every number and every other value.
3. Reads section 7's clauses for every term (A2 § 2): from the committed heldout-m10.json and rows-m10.json, and for (a) and (c1)
   from each anchor's own measurement error in its session's reduction (D se for (a), dT_win se for (c1)), by Monte Carlo of the
   session's median, 2,000 draws, seed 142.
4. Writes section7-m10.json (every reading), m10-s7.json (M10's primary entries after section 7, A2-1) and section7-output.txt
   (this run's log) in --out (this directory unless told otherwise).

Standard library and numpy 1.26. SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import builtins  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402

sys.dont_write_bytecode = True
# every file opened from here to the end of the re-run is recorded: the chain's files read at import and in the fit itself
_OPENED, _REAL_OPEN = set(), builtins.open


def _tracing_open(file, *a, **k):
    try:
        if isinstance(file, (str, bytes, os.PathLike)):
            _OPENED.add(os.path.abspath(os.fsdecode(file)))
    except Exception:  # noqa: BLE001
        pass
    return _REAL_OPEN(file, *a, **k)


builtins.open = _tracing_open
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fit_m10 as FM  # noqa: E402  (the registered fit, unchanged)

SEED, NB = 142, 2000
OUTS = ("m10.json", "heldout-m10.json", "rows-m10.json", "fit-output.txt")
LARGE_RISE_C = 10.0
fam_of = FM.fam_of
LOG = []


def log(s):
    print(s, flush=True)
    LOG.append(s)


def rms(v):
    v = [float(x) for x in v if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v if x is not None]
    return sum(v) / len(v) if v else None


def r6(x):
    return None if x is None else round(float(x), 6)


# ------------------------------------------------------------------ 1. hash lists
def check_sums(listfile, base):
    bad, n = [], 0
    for line in open(listfile):
        if line.strip():
            h, rel = line.split(None, 1)
            n += 1
            if FM.fsha(os.path.join(base, rel.strip())) != h:
                bad.append(rel.strip())
    return n, bad


# ------------------------------------------------------------------ 2. the re-run
def rerun(outdir):
    if os.path.abspath(outdir) == HERE:
        raise SystemExit("section7: --rerun-dir must not be this directory (the committed outputs are never overwritten)")
    os.makedirs(outdir, exist_ok=True)
    argv, t0 = sys.argv, time.time()
    sys.argv = ["fit_m10.py", "--out", outdir]
    try:
        FM.main()
    finally:
        builtins.open = _REAL_OPEN
        sys.argv = argv
    return set(_OPENED), time.time() - t0


def jcmp(a, b, path, acc):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            acc["structure"].append(path + ": keys differ")
        for k in sorted(set(a) & set(b)):
            jcmp(a[k], b[k], f"{path}/{k}", acc)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            acc["structure"].append(path + ": lengths differ")
        for i, (x, y) in enumerate(zip(a, b)):
            jcmp(x, y, f"{path}[{i}]", acc)
    elif isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        if a != b:
            acc["values"].append(f"{path}: {a!r} against {b!r}"[:240])
    else:
        fa, fb = float(a), float(b)
        if math.isnan(fa) and math.isnan(fb):
            return
        d = abs(fa - fb)
        if d > acc["max_abs"]:
            acc["max_abs"], acc["at_abs"] = d, path
        den = max(abs(fa), abs(fb))
        # relative differences of every value but the self-tests' own residuals (differences of near-zero numbers)
        if den > 0 and "/selftest/" not in path and d / den > acc["max_rel"]:
            acc["max_rel"], acc["at_rel"] = d / den, path


def compare(outdir):
    out = {}
    for f in OUTS:
        a, b = os.path.join(HERE, f), os.path.join(outdir, f)
        same = open(a, "rb").read() == open(b, "rb").read()
        rec = {"bytes_identical": same}
        if f.endswith(".json"):
            acc = {"max_abs": 0.0, "at_abs": None, "max_rel": 0.0, "at_rel": None, "structure": [], "values": []}
            jcmp(FM.load(a), FM.load(b), "", acc)
            rec.update({"max_abs_diff": acc["max_abs"], "at": acc["at_abs"], "max_rel_diff": acc["max_rel"], "at_rel": acc["at_rel"],
                        "structure_differences": acc["structure"][:20], "non_numeric_differences": acc["values"][:20],
                        "n_non_numeric_differences": len(acc["values"])})
        else:
            la, lb = open(a).read().splitlines(), open(b).read().splitlines()
            diff = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
            rec.update({"lines": [len(la), len(lb)], "lines_differing": len(diff) + abs(len(la) - len(lb)),
                        "differing": [{"committed": la[i][:200], "rerun": lb[i][:200]} for i in diff[:6]]})
        out[f] = rec
    return out


# ------------------------------------------------------------------ 3. section 7
_items, _reductions = {}, {}


def footing_item(exp, name):
    if exp not in _items:
        _items[exp] = FM.footing_items(exp) or {}
    return _items[exp].get(name) or {}


def reduction_item(exp, key):
    if exp not in _reductions:
        p = os.path.join(FM.DD, FM.M6.EXPDIR[exp], f"{exp.lower()}.json")
        _reductions[exp] = FM.load(p)["items"]
    return _reductions[exp].get(key) or {}


def median_noise(per, rng):
    """per: {session: [(measured, se, model, name), ...]} -> each session's median ratio and its sd under the measurements' own
    errors (Monte Carlo, the measured value drawn as measured + se x N(0, 1), the model value held)"""
    res = {}
    for sess in sorted(per):
        lst = per[sess]
        y = np.array([x[0] for x in lst], float)
        se = np.array([x[1] for x in lst], float)
        m = np.array([x[2] for x in lst], float)
        draws = y[None, :] + se[None, :] * rng.standard_normal((NB, len(y)))
        mc = np.median(draws / m[None, :], axis=1)
        res[sess] = {"scale": float(np.median(y / m)), "n_anchors": len(y), "sd_from_own_errors": float(np.std(mc, ddof=1)),
                     "anchors": [x[3] for x in lst], "se_missing": int(np.sum(np.isnan(se)))}
    return res


def spread_by_card(res, cards):
    """observed sd of the scales over a card's sessions against the sd their anchors' own errors give, both over the sessions
    whose every anchor has a measured se (a session with a single-pass anchor has none: it is named, and left out of both)"""
    out = {}
    for c in cards:
        allss = {k: v for k, v in res.items() if k.endswith("|" + c)}
        ss = [v for v in allss.values() if not v["se_missing"]]
        if len(ss) < 2:
            continue
        obs = float(np.std([v["scale"] for v in ss], ddof=1))
        noise = float(math.sqrt(np.mean([v["sd_from_own_errors"] ** 2 for v in ss])))
        out[c] = {"sessions": len(ss), "observed_sd": obs, "sd_expected_from_own_errors": noise, "ratio": obs / noise if noise else None,
                  "range": [min(v["scale"] for v in ss), max(v["scale"] for v in ss)], "agree_within_own_noise": bool(obs <= noise),
                  "left_out_no_se": sorted(k for k, v in allss.items() if v["se_missing"]),
                  "observed_sd_every_session": float(np.std([v["scale"] for v in allss.values()], ddof=1))}
    return out


def term_a_noise(fam, rows, anchors, rc, m9, held):
    fr = [r for r in rows if fam_of(r["type"]) == fam]
    terms = m9["families"][fam]["terms"]
    anc = {s: [x for x in v if fam_of(x["type"]) == fam] for s, v in anchors.items()}
    variants = {"B+a": None}
    if fam == "float":
        variants["B+a+b"] = {i: rc[r["key"]]["fN"] for i, r in enumerate(fr) if r["S_class"]}
    ref = {"B+a": held["power"][fam]["session_scales_term_a_all_rows"]}
    if fam == "float":
        ref["B+a+b"] = held["power"][fam]["session_scales_all_rows"]
    out = {}
    for vn, over in variants.items():
        ft = FM.Fit10(fr, terms, anc, True, over)
        fit = ft.fit(None)
        per = {}
        for si_, xa, D, ak, name in ft.anc:
            sess = ft.sessions[si_]
            dh = float(xa @ fit["b0"]) * (fit["c"] if ft.sess_c1[si_] else 1.0)
            if dh > 0:
                se = (footing_item(sess.split("|")[0], name).get("D") or {}).get("se")
                per.setdefault(sess, []).append((D, float(se) if se is not None else float("nan"), dh, name))
        res = median_noise(per, np.random.default_rng(SEED))
        worst = max(abs(v["scale"] - float(ref[vn][s])) for s, v in res.items())
        worst_fit = max(abs(v["scale"] - float(fit["s"][ft.sessions.index(s)])) for s, v in res.items())
        by = spread_by_card(res, ("a3", "c1"))
        out[vn] = {"sessions": {s: {k: (r6(x) if isinstance(x, float) else x) for k, x in v.items()} for s, v in res.items()},
                   "sessions_without_an_anchor_scale_1": sorted(s for s in ft.sessions if s not in res),
                   "by_card": by, "scales_reproduce_heldout_rounded": worst, "scales_reproduce_the_fit": worst_fit,
                   "clause_triggered": any(v["agree_within_own_noise"] for v in by.values())}
    return out


def bias_cells(rows, fam, base, cand):
    """bias (measured - predicted) and rms of two variants per card, on every row, pool 7's 52 kinds and its priority-1 kinds,
    for the family and per format"""
    sets = {"all rows": lambda r: True, "pool 7, all 52": lambda r: r["exp"] in ("E163", "E164"),
            "pool 7, priority 1": lambda r: r["exp"] in ("E163", "E164") and r.get("priority") == 1}
    out = {}
    for sn, f in sets.items():
        for c in ("a3", "c1"):
            for t in [None] + sorted({r["type"] for r in rows if fam_of(r["type"]) == fam}):
                sel = [r for r in rows if fam_of(r["type"]) == fam and r["card"] == c and f(r) and (t is None or r["type"] == t)
                       and r["err_w"].get(base) is not None and r["err_w"].get(cand) is not None]
                if not sel:
                    continue
                b0, b1 = mean([r["err_w"][base] for r in sel]), mean([r["err_w"][cand] for r in sel])
                out[f"{sn}|{c}" + (f"|{t}" if t else "")] = {
                    "n": len(sel), "bias_" + base: r6(b0), "bias_" + cand: r6(b1),
                    "rms_" + base: r6(rms([r["err_w"][base] for r in sel])), "rms_" + cand: r6(rms([r["err_w"][cand] for r in sel])),
                    "toward_0": bool(abs(b1) < abs(b0)), "sign_change_and_grows": bool(b0 * b1 < 0 and abs(b1) > abs(b0))}
    return out


def term_a(fam, rows, anchors, rc, m9, held, rowsout, entered):
    noise = term_a_noise(fam, rows, anchors, rc, m9, held)
    cells = bias_cells(rowsout, fam, "B", "B+a")
    extra = bias_cells(rowsout, fam, "B+b", "B+a+b") if fam == "float" else None
    p7 = [k for k in cells if k.startswith("pool 7") and k.count("|") == 1]
    toward = {k: cells[k]["toward_0"] for k in p7}
    fam_cells = [k for k in cells if k.count("|") == 1]
    over = {k: cells[k]["sign_change_and_grows"] for k in fam_cells}
    fmt_over = sorted(k for k in cells if k.count("|") == 2 and cells[k]["sign_change_and_grows"])
    i_noise = noise["B+a+b" if fam == "float" else "B+a"]["clause_triggered"]
    i_bias = not all(toward.values())
    i_over = any(over.values())
    return {"entered_by_section_6": entered,
            "clause_1_scales_within_own_noise": {"read_on": "B+a+b (the frozen variant)" if fam == "float" else "B+a",
                                                 "triggered": i_noise, "variants": noise},
            "clause_2_pool7_bias_toward_0_on_both_cards": {"B_to_B+a": {k: cells[k] for k in p7}, "toward_0": toward,
                                                           "triggered": i_bias},
            "clause_3_overcorrects": {"family_cells": over, "format_cells_with_sign_change_and_growth": fmt_over, "triggered": i_over},
            "cells_B_to_B+a": cells, "cells_B+b_to_B+a+b": extra,
            "triggered": bool(i_noise or i_bias or i_over)}


def term_b(rowsout, held, entered):
    S = [r for r in rowsout if r["S_class"]]
    per = {}
    for c in ("a3", "c1"):
        sel = [r for r in S if r["card"] == c]
        rec = {"n": len(sel)}
        for vn in ("B", "B+b", "B+a", "B+a+b"):
            rec["rms_" + vn] = r6(rms([r["err_w"][vn] for r in sel]))
            rec["bias_" + vn] = r6(mean([r["err_w"][vn] for r in sel]))
        rec["wrong_way_B_to_B+b"] = bool(rec["rms_B+b"] > rec["rms_B"])
        rec["wrong_way_B+a_to_B+a+b"] = bool(rec["rms_B+a+b"] > rec["rms_B+a"])
        per[c] = rec
    tiles = {}
    for n, rec in held["S_recount"].items():
        N = rec["N"]
        e = rec["by_N"][str(N)]["e_w"]
        d = rec["three_point_minus_N_w"]
        tiles[n] = {"N": N, "e_N_w": r6(e), "three_point_minus_N_w": r6(d), "within_pm_e_N": bool(abs(d) <= e)}
    within = sum(1 for v in tiles.values() if v["within_pm_e_N"])
    i1 = any(v["wrong_way_B_to_B+b"] for v in per.values())
    i2 = within > len(tiles) / 2
    return {"entered_by_section_6": entered,
            "clause_1_S_rows_wrong_way_on_a_card": {"per_card": per, "triggered": i1},
            "clause_2_most_tiles_counting_within_e_N": {"tiles": tiles, "within": within, "of": len(tiles),
                                                        "most_means": "more than half", "triggered": i2},
            "triggered": bool(i1 or i2)}


def term_c1(rows, held, entered):
    FM.M6.EXPDIR.update(FM.HEAT_EXTRA)
    hr = FM.M7.heat_rows(rows)
    for r in hr:
        r["sess"] = f"{r['exp']}|{r['card']}"
    cards = sorted({r["card"] for r in hr})
    X = FM.M6.hX(hr, ["S|card", "ST|card"], cards)
    y = np.array([r["dT"] for r in hr])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    law = X @ b
    per = {}
    for i, r in enumerate(hr):
        if r["key"] in FM.ANCHORS and law[i] > 0:
            se = (reduction_item(r["exp"], r["key"]).get("dT_win") or {}).get("se")
            per.setdefault(r["sess"], []).append((float(y[i]), float(se) if se is not None else float("nan"), float(law[i]), r["key"]))
    res = median_noise(per, np.random.default_rng(SEED))
    ref = held["heat_c1"]["session_heat_scales_all_rows"]
    worst = max(abs(v["scale"] - float(ref[s])) for s, v in res.items())
    by = spread_by_card(res, cards)
    hc = held["heat_c1"]
    gain = {"pooled": hc["paired_bootstrap_sessscale_minus_base"], **{c: hc["per_card"][c] for c in cards}}
    unresolved = sorted(k for k, v in gain.items() if not v["resolved"])
    i1 = any(v["agree_within_own_noise"] for v in by.values())
    return {"entered_by_section_6": entered,
            "clause_1_scales_within_the_window_rises_own_noise": {"by_card": by, "scales_reproduce_heldout_rounded": worst,
                                                                    "sessions": {s: {k: (r6(x) if isinstance(x, float) else x) for k, x in v.items()} for s, v in res.items()},
                                                                    "triggered": i1},
            "clause_2_gain_not_resolved": {"paired_bootstrap": gain, "not_resolved_on": unresolved, "triggered": bool(unresolved)},
            "triggered": bool(i1 or unresolved)}


def term_c2(held, entered):
    c2 = held["heat_c2_card0_burst"]
    lo, hi = c2["k_loto_range"]
    inc = bool(lo <= c2["k_frozen_c_per_w"] <= hi)
    return {"entered_by_section_6": entered,
            "clause_1_loto_k_spread_includes_0.14004": {"k_loto_range": [lo, hi], "k_frozen": c2["k_frozen_c_per_w"], "triggered": inc},
            "triggered": inc}


def term_d(held, entered):
    d = held["heat_d_chain_gain"]
    fit = [h for h in d["holds"] if h["fitted"]]
    big = [h for h in fit if h["R_C"] >= LARGE_RISE_C]
    # the committed leave-one-session-out gammas, recomputed from each hold's R and e
    gchk = 0.0
    for h in fit:
        for var, key in (("common", "gamma_common"), ("per_card_kind", "gamma_per_card_kind")):
            tr = [q for q in fit if q["session"] != h["session"] and (var == "common" or q["card_kind"] == h["card_kind"])]
            g = sum(q["e_C"] * (q["R_C"] - q["e_C"]) for q in tr) / sum((q["R_C"] - q["e_C"]) ** 2 for q in tr)
            gchk = max(gchk, abs(g - h[key]), abs((h["e_C"] - g * (h["R_C"] - h["e_C"])) - h["e_" + var]))
    variants = {}
    for var in ("common", "per_card_kind"):
        per = {}
        for h in big:
            per.setdefault(h["session"], []).append(h)
        rd = {}
        for s, hs in sorted(per.items()):
            w0, w1 = rms([h["e_C"] for h in hs]), rms([h["e_" + var] for h in hs])
            rd[s] = {"card_kind": hs[0]["card_kind"], "large_rise_holds": [h["hold"] for h in hs], "n": len(hs),
                     "rms_without_c": r6(w0), "rms_with_c": r6(w1), "gamma_of_its_fold": r6(hs[0]["gamma_" + var]),
                     "reads_worse_with_gamma": bool(w1 > w0)}
        worse = sorted(s for s, v in rd.items() if v["reads_worse_with_gamma"])
        gk = {}
        for c in ("aifoundry3", "aifoundry2"):
            gs = [h["gamma_" + var] for h in fit if h["card_kind"] == c]
            gk[c] = [r6(min(gs)), r6(max(gs))]
        all_g = d["variants"][var]["gamma_all_holds"]
        variants[var] = {"passes_section_6": d["variants"][var]["passes"], "gamma_all_holds": all_g, "per_session_large_rises": rd,
                         "sessions_worse_with_gamma": worse, "fold_gamma_range_by_card_kind": gk,
                         "clause_2_triggered": bool(worse)}
    pk = d["variants"]["per_card_kind"]["gamma_all_holds"]
    sign_differs = (pk["aifoundry3"] > 0) != (pk["aifoundry2"] > 0)
    folds = variants["per_card_kind"]["fold_gamma_range_by_card_kind"]
    fold_sign_differs = any(lo <= 0 <= hi for lo, hi in folds.values()) or (folds["aifoundry3"][0] > 0) != (folds["aifoundry2"][0] > 0)
    e144 = [h for h in big if h["session"] == "E144"]
    note = None
    if e144:
        h = e144[0]
        note = {"hold": h["hold"], "R_C": r6(h["R_C"]), "e_without_C": r6(h["e_C"]), "e_with_common_gamma_C": r6(h["e_common"]),
                "chain_read_to_fraction": r6(abs(h["e_C"]) / h["R_C"]), "worse_by_C": r6(abs(h["e_common"]) - abs(h["e_C"])),
                "gamma_of_its_fold": r6(h["gamma_common"])}
    ent = entered if entered else None
    trig = bool(sign_differs or (ent and variants[ent]["clause_2_triggered"]))
    return {"entered_by_section_6": entered, "large_rise_c": LARGE_RISE_C, "n_fitted": len(fit), "n_large": len(big),
            "committed_gammas_recomputed_max_abs": gchk,
            "clause_1_gamma_sign_differs_between_card_kinds": {"per_card_kind_gamma_all_holds": pk, "fold_ranges": folds,
                                                                "triggered": bool(sign_differs), "fold_sign_differs": bool(fold_sign_differs)},
            "clause_2_a_held_out_session_reads_worse": {v: {k: variants[v][k] for k in ("sessions_worse_with_gamma", "clause_2_triggered")}
                                                        for v in variants},
            "variants": variants, "E144": note,
            "triggered": trig,
            "triggered_for": ent}


def term_e(held, entered):
    k = held["kappa_e_card0"]
    k0 = k["kappa0"]
    straddle = {f: bool(lo <= k0 <= hi) for f, (lo, hi) in k["kappa_loto_by_family"].items()}
    pb = k["paired_bootstrap"]
    return {"entered_by_section_6": entered,
            "clause_1_loto_kappa_straddles_kappa0": {"kappa0": k0, "kappa_loto_by_family": k["kappa_loto_by_family"], "straddles": straddle,
                                                    "triggered": any(straddle.values())},
            "clause_2_board_error_not_resolved": {"paired_bootstrap": pb, "triggered": not pb["resolved"]},
            "triggered": bool(any(straddle.values()) or not pb["resolved"])}


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rerun-dir")
    ap.add_argument("--no-rerun", action="store_true")
    ap.add_argument("--out", default=HERE, help="where the three outputs go (default: this directory)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if not a.no_rerun and not a.rerun_dir:
        raise SystemExit("section7: give --rerun-dir <dir> (outside this directory) or --no-rerun")
    if a.no_rerun:
        builtins.open = _REAL_OPEN
    t0 = time.time()
    log(f"section7_m10 (Q142(m) A2): python {sys.version.split()[0]}, numpy {np.__version__}, {platform.machine()}")
    n_in = FM.check_inputs()
    n_own, bad_own = check_sums(os.path.join(HERE, "SHA256SUMS"), HERE)
    log(f"registered inputs: {n_in} hash as tools/claims-v3/m10/SHA256SUMS; this directory's SHA256SUMS: {n_own} files, changed {bad_own}")
    if bad_own:
        raise SystemExit("section7: the committed M10 files changed: " + ", ".join(bad_own))
    out = {"_note": ("Q142(m) amendment A2: REGISTRATION.md section 7 read for every term (tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md);"
                     " held out, not blind; m10.json is unchanged"),
           "hash_checks": {"registered_inputs": n_in, "m10_sha256sums": n_own, "m10_changed": bad_own},
           "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "machine": platform.machine(),
                           "threads": os.environ.get("OPENBLAS_NUM_THREADS")}}
    if not a.no_rerun:
        log("re-run of the registered fit (fit_m10.main, unchanged) into the re-run directory:")
        opened, wall = rerun(a.rerun_dir)
        cmp_ = compare(a.rerun_dir)
        tops = os.path.join(TOP, "")
        own = {os.path.join("docs/reports/data/2026-11-04-q142m-m10", ln.split(None, 1)[1].strip())
               for ln in open(os.path.join(HERE, "SHA256SUMS")) if ln.strip()}
        reg = {ln.split(None, 1)[1].strip() for ln in open(os.path.join(FM.REG, "SHA256SUMS")) if ln.strip()}
        rel = sorted(p[len(tops):] for p in opened if p.startswith(tops) and not p.startswith(os.path.join(os.path.abspath(a.rerun_dir), "")))
        lists = {"tools/claims-v3/m10/SHA256SUMS", "docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS"}
        data = [p for p in rel if not p.endswith(".py") and p not in lists]
        uncovered = [p for p in data if p not in reg and p not in own]
        out["rerun"] = {"wall_s": round(wall, 1), "compare": cmp_, "files_opened_in_tree": len(rel), "data_files_opened": len(data),
                        "trace": "every file opened from before fit_m10's import to the end of the re-run (the two hash lists left out)",
                        "registered_inputs_not_opened": sorted(reg - set(data)),
                        "data_opened_not_in_either_hash_list": {p: FM.fsha(os.path.join(TOP, p)) for p in uncovered}}
        log(f"  re-run {wall:.1f} s; " + "; ".join(
            f"{f}: bytes {'identical' if v['bytes_identical'] else 'differ'}"
            + (f", max |diff| {v['max_abs_diff']:.2e} at {v['at']}, non-numeric differences {v['n_non_numeric_differences']}" if f.endswith(".json")
               else f", lines differing {v['lines_differing']}") for f, v in cmp_.items()))
        log(f"  data files opened {len(data)}; not in the registration's 174 or M10's 68: {len(uncovered)}")
    m10 = FM.load(os.path.join(HERE, "m10.json"))
    held = FM.load(os.path.join(HERE, "heldout-m10.json"))
    rowsout = FM.load(os.path.join(HERE, "rows-m10.json"))
    m9 = FM.load(os.path.join(FM.M9D, "m9.json"))
    rows, missing = FM.assemble()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    anchors, _ = FM.assemble_anchors(rows, zeros, zr)
    rc = FM.recount(os.path.join(HERE, "bench"), zeros, zr)
    ent = m10["entered"]
    s7 = {"a_float": term_a("float", rows, anchors, rc, m9, held, rowsout, ent["a_float"]),
          "a_int8": term_a("int8", rows, anchors, rc, m9, held, rowsout, ent["a_int8"]),
          "b": term_b(rowsout, held, ent["b"]),
          "c1": term_c1(rows, held, ent["c1"]),
          "c2": term_c2(held, ent["c2"]),
          "d": term_d(held, ent["d"]),
          "e": term_e(held, ent["e"])}
    trig = {k: bool(v["triggered"]) for k, v in s7.items()}
    primary = {}
    for k, v in ent.items():
        primary[k] = ((None if k == "d" else False) if (v and trig[k]) else v)
    gain = m10.get("heat_chain_gain")
    factor = (1.0 + gain["gamma"]["all"]) if gain and gain.get("variant") == "common" else None
    out["section7"] = s7
    out["triggered"] = trig
    out["entered_by_section_6"] = ent
    out["entered_primary_after_section_7"] = primary
    s7file = {"_note": ("Q142(m) amendment A2 (tools/claims-v3/m10/REGISTRATION.md.dated-note-2.md): M10's primary entries after "
                        "REGISTRATION.md section 7, written by section7_m10.py. m10.json (6829c9ba) is unchanged and stays the frozen form; "
                        "this file supersedes its 'entered' and 'heat_chain_gain' as M10's primary, and nothing else."),
              "m10_json_sha256": FM.fsha(os.path.join(HERE, "m10.json")),
              "entered_by_section_6": ent, "section_7_triggered": trig, "entered_primary": primary,
              "heat_chain_gain_primary": (gain if primary.get("d") else None),
              "heat_chain_factor_primary": (factor if primary.get("d") else 1.0),
              "heat_chain_gain_reported_arm": (gain if (ent.get("d") and not primary.get("d")) else None),
              "heat_chain_factor_reported_arm": (factor if (ent.get("d") and not primary.get("d")) else None),
              "unchanged_from_m10_json": ["families", "heat_4p5s", "card0_burst_heat_k_c_per_w", "card0_kappa", "footing"],
              "readings": "section7-m10.json"}
    json.dump(out, open(os.path.join(a.out, "section7-m10.json"), "w"), indent=1, sort_keys=True)
    json.dump(s7file, open(os.path.join(a.out, "m10-s7.json"), "w"), indent=1, sort_keys=True)
    for k in s7:
        log(f"section 7 ({k}): entered by section 6 {ent[k]!r}; triggered {trig[k]}")
    d = s7["d"]
    log(f"  (d) sessions worse with the common gamma: {d['variants']['common']['sessions_worse_with_gamma']}; E144 {d['E144']}")
    log(f"  (d) per-card-kind gamma {d['clause_1_gamma_sign_differs_between_card_kinds']['per_card_kind_gamma_all_holds']}; "
        f"the committed gammas recomputed within {d['committed_gammas_recomputed_max_abs']:.2e}")
    a_ = s7["a_float"]["clause_1_scales_within_own_noise"]["variants"]["B+a+b"]["by_card"]
    log("  (a) floats, sd of s over a card's sessions / from the anchors' own errors: "
        + "; ".join(f"{c} {v['observed_sd']:.5f} / {v['sd_expected_from_own_errors']:.5f} ({v['sessions']} sessions)" for c, v in a_.items()))
    log(f"primary entries after section 7: {primary}; heat chain factor primary {s7file['heat_chain_factor_primary']}, "
        f"reported arm {s7file['heat_chain_factor_reported_arm']}")
    log(f"wrote section7-m10.json, m10-s7.json, section7-output.txt ({time.time() - t0:.1f} s)")
    open(os.path.join(a.out, "section7-output.txt"), "w").write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
