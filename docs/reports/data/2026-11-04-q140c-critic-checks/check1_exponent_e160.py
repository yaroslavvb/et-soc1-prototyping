#!/usr/bin/env python3
"""Q140(c) check 1 (post hoc, desk only; nothing registered): Q139(s)'s board exponent n = 2.28 on E160, through Q139(s)'s
committed chain, scored on E160's registered groups.

    python3 -I -B check1_exponent_e160.py <lab repo root> --out check1-exponent-e160.json > check1-exponent-e160.txt

Needs numpy (Q139(s)'s fit_clock_voltage.py imports it). Written for Q140(c) independently of Q139's final critic's own
script: the critic's work/ files were read only after this script's numbers were printed (see the README).

What is imported unchanged (the object under test, never edited): Q139(s)'s fit_clock_voltage.py (Chain, sf) and its
corrections-numbers.py (load_runs, rerefer_chain, SETS: the E66-slope re-referral that defines arm A5c); through them the
lab's tools/claims-v3/hpl/surface_hpl.py and tools/claims-v3/e119/make_predictions_e119.py. Bytecode writing is off, so the
lab tree stays clean.

What this script does itself:
  * the inputs: Q139(s)'s reads (clock-voltage.json: aifoundry2's PVT busy means without E143, and xfer the same way; the
    survey's tree predates E160, so no voltage here saw E160); pool 6's frozen M7 D per tile
    (tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json, M7.D600_a3_footing_w); E160's measured per-tile means
    and its registered groups (results.json score.reported.tiles: group, burst_mhz, burst_w; governed = M8's frozen clock
    below 795 MHz, 17 tiles; pinned 31);
  * a reproduction check: arm A0 (M7 as frozen in m7.json) must give E160's own M7 columns (M7_mhz, M7_w) per tile;
  * the arms: A0 M7 frozen; A2 s(f) from the reads at n = 2, the chain refitted (B on E64's rows, each E80/E83 cell's c,
    the cap W*, c_zeros from E64's zeros runs); A3 n = 2.43; A5 n = 2.28 on the committed 0.442-referred powers; A5c
    n = 2.28 on powers re-referred at E66's slope set; A4c the ramp slopes at E66's slope (corrections-numbers.json
    C1 fits, common intercept, as Q139(s)'s A4c); plus M8 as frozen (E160's own M8 columns, no chain);
  * scores (measured - predicted): rms and mean of the burst clock, the board W and the die's rise (M7's frozen burst heat law on each arm's board W), governed / pinned / all, with a
    bootstrap over tiles (inside one session) and a paired bootstrap of rms(arm) - rms(A2) on the governed tiles;
  * the same arms on E143 (pool 5's 36 tiles, E143's frozen M7 D, its registered groups), so the two sessions can be read
    side by side: each arm's per-session mean error (the offset) and its sd about that mean (what an offset cannot move),
    and the two sessions' governed tiles pooled.
"""
import argparse
import importlib.util
import json
import math
import os
import random
import statistics as st
import sys

sys.dont_write_bytecode = True

QS_DIR = "docs/reports/data/2026-11-03-q139s-clock-voltage"
E160_DIR = "docs/reports/data/2026-11-03-e160-blind6-aifoundry2"
E143_DIR = "docs/reports/data/2026-11-02-e143-blind5-aifoundry2"
P6_FILE = "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json"
P5_FILE = "tools/claims-v3/e143/predictions-e143.json"
E66_SET = "E66_0.2936_at_600, 0.3678_at_700, E60_0.442_at_800"
BOOT = 5000
SEED = 140


def rms(e):
    return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


def mean(e):
    return sum(e) / len(e) if e else None


def sd0(e):
    """sd about the sample's own mean (ddof 0): the part of the rms a per-session offset cannot remove."""
    if not e:
        return None
    m = mean(e)
    return math.sqrt(sum((x - m) ** 2 for x in e) / len(e))


def boot_rms(e, rng, n=BOOT):
    k = len(e)
    v = sorted(rms([e[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    return [v[int(0.025 * n)], v[int(0.975 * n) - 1]]


def boot_paired(ea, eb, rng, n=BOOT):
    """rms(a) - rms(b) over the same tiles resampled together: 95% interval and the share of draws at or below 0."""
    k = len(ea)
    d = []
    for _ in range(n):
        idx = [rng.randrange(k) for _ in range(k)]
        d.append(rms([ea[i] for i in idx]) - rms([eb[i] for i in idx]))
    d.sort()
    return {"lo95": d[int(0.025 * n)], "hi95": d[int(0.975 * n) - 1], "share_le_0": sum(1 for x in d if x <= 0) / n}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def chain_terms(ch, S, X):
    """Q139(s)'s chain refitted at the s(f) given (the code path of corrections-numbers.py chain_arm, without its scorer)."""
    B, c, _, _ = ch.fit_B(S)
    cz = {t: st.mean([v for k, v in c.items() if f"-{t}-zeros" in k]) for t in ("fp32", "fp16", "int8")}
    cl = [x for x in ch.cells(S, B) if x["c_w"] is not None]
    W = ch.fit_W(cl, B, S)
    return {"B": B, "S": S, "CZ": cz, "X": X, "W": W}


def predict_all(ch, terms, D_by_tile, type_by_tile):
    out = {}
    for n in D_by_tile:
        f, P = ch.predict(D_by_tile[n], type_by_tile[n], terms["B"], terms["S"], terms["CZ"], terms["X"], terms["W"])
        out[n] = (f, P, ch.kh * (P - ch.p_idle))
    return out


def score(pred, meas, groups, rng):
    res = {}
    for g in ("governed", "pinned", "all"):
        sel = sorted(n for n in meas if g == "all" or groups[n] == g)
        ef = [meas[n][0] - pred[n][0] for n in sel]
        ew = [meas[n][1] - pred[n][1] for n in sel]
        er = [meas[n][2] - pred[n][2] for n in sel]
        res[g] = {"n": len(sel), "rise_rms": rms(er), "rise_mean": mean(er), "mhz_rms": rms(ef), "mhz_mean": mean(ef), "mhz_sd_about_mean": sd0(ef),
                  "mhz_rms_95_over_tiles": boot_rms(ef, rng), "w_rms": rms(ew), "w_mean": mean(ew),
                  "w_sd_about_mean": sd0(ew), "w_rms_95_over_tiles": boot_rms(ew, rng)}
    return res


def errors(pred, meas, groups, g):
    sel = sorted(n for n in meas if groups[n] == g)
    return sel, [meas[n][0] - pred[n][0] for n in sel], [meas[n][1] - pred[n][1] for n in sel]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    qs = os.path.join(root, QS_DIR)
    sys.path.insert(0, qs)
    import fit_clock_voltage as FCV  # noqa: E402  Q139(s)'s committed chain, unchanged
    CN = load_module("q139s_corrections_numbers", os.path.join(qs, "corrections-numbers.py"))
    cv = json.load(open(os.path.join(qs, "clock-voltage.json")))
    cn = json.load(open(os.path.join(qs, "corrections-numbers.json")))
    V = {int(k): v for k, v in cv["V_aifoundry2_v"]["pvt_busy_mean_no_E143"].items()}
    Xr = cv["xfer"]["pvt_busy_mean_no_E143"]
    rng = random.Random(SEED)
    L = []
    out = {"_note": "Q140(c) check 1: post hoc desk check, nothing registered, nothing on a card. Q139(s)'s board exponent "
                    "through Q139(s)'s committed chain, scored on E160 (pool 6, aifoundry2, run 06:41-07:12 PST Tue 3 Nov 2026, "
                    "after the exponent's commit c944ff99 at 05:25:25 PST) and on E143 (pool 5) beside it.",
           "inputs": {"V_aifoundry2_v": V, "xfer": Xr, "q139s_dir": QS_DIR, "e160": E160_DIR + "/results.json score.reported.tiles",
                      "pool6_M7_D": P6_FILE + " tiles.*.M7.D600_a3_footing_w", "e143": E143_DIR + "/results.json score.reported.tiles",
                      "pool5_M7_D": P5_FILE + " tiles.*.models.M7.D600_a3_footing_w"}}

    # ---- E160's measured means, groups, frozen M7 D; E143's the same way
    R160 = json.load(open(os.path.join(root, E160_DIR, "results.json")))
    T160 = R160["score"]["reported"]["tiles"]
    P6 = json.load(open(os.path.join(root, P6_FILE)))["tiles"]
    meas160 = {n: (float(v["burst_mhz"]), float(v["burst_w"]), float(v["rise_c"])) for n, v in T160.items()}
    grp160 = {n: v["group"] for n, v in T160.items()}
    D160 = {n: float(P6[n]["M7"]["D600_a3_footing_w"]) for n in T160}
    ty160 = {n: P6[n]["type"] for n in T160}
    gov_rule = all((T160[n]["M8_mhz"] < 795.0) == (grp160[n] == "governed") for n in T160)
    R143 = json.load(open(os.path.join(root, E143_DIR, "results.json")))
    T143 = R143["score"]["reported"]["tiles"]
    P5 = json.load(open(os.path.join(root, P5_FILE)))["tiles"]
    meas143 = {n: (float(v["burst_mhz"]), float(v["burst_w"]), float(v["rise_c"])) for n, v in T143.items()}
    grp143 = {n: P5[n]["group"] for n in T143}
    D143 = {n: float(P5[n]["models"]["M7"]["D600_a3_footing_w"]) for n in T143}
    ty143 = {n: P5[n]["type"] for n in T143}
    out["sets"] = {"E160": {"n": len(T160), "governed": sum(1 for g in grp160.values() if g == "governed"),
                            "pinned": sum(1 for g in grp160.values() if g == "pinned"), "governed_is_M8_below_795": gov_rule,
                            "dropped_by_E160": R160["score"]["dropped"]},
                   "E143": {"n": len(T143), "governed": sum(1 for g in grp143.values() if g == "governed"),
                            "pinned": sum(1 for g in grp143.values() if g == "pinned")}}
    L.append("CHECK 1. Q139(s)'s BOARD EXPONENT ON E160, THROUGH Q139(s)'s COMMITTED CHAIN (post hoc; measured - predicted)")
    L.append(f"  E160: {len(T160)} tiles scored ({out['sets']['E160']['governed']} governed, {out['sets']['E160']['pinned']} pinned; "
             f"governed == M8's frozen clock < 795 MHz: {gov_rule}); dropped by E160 (predicted over 82 W): {R160['score']['dropped']}")
    L.append(f"  E143: {len(T143)} tiles ({out['sets']['E143']['governed']} governed, {out['sets']['E143']['pinned']} pinned)")
    L.append(f"  reads (aifoundry2, PVT busy means without E143; the survey's tree predates E160): V = {V[600]:.4f} / {V[700]:.4f} / {V[800]:.4f} V; xfer {Xr:.5f}")

    # ---- the arms
    ch = FCV.Chain(root)
    terms = {"A0_M7_frozen": {"B": ch.B7, "S": ch.S7, "CZ": ch.CZ7, "X": ch.X7, "W": ch.W7}}
    terms["A2_n2.00_chain_refit"] = chain_terms(ch, FCV.sf(V, 2.0), Xr)
    terms["A5_n2.28_chain_on_committed_powers"] = chain_terms(ch, FCV.sf(V, 2.28), Xr)
    runs = CN.load_runs(root)
    ch2, n64, nk = CN.rerefer_chain(ch, runs, CN.SETS[E66_SET])
    terms["A5c_n2.28_chain_on_E66_rereferred_powers"] = chain_terms(ch2, FCV.sf(V, 2.28), Xr)
    f66 = cn["C1"][E66_SET]["fits"]
    S4c = {600: 1.0, 700: f66["all_runs.common@700"]["s"], 800: f66["all_runs.common@800"]["s"]}
    terms["A4c_ramp_slopes_at_E66_slope_rereferred"] = chain_terms(ch2, S4c, Xr)
    terms["A3_n2.43_chain_refit"] = chain_terms(ch, FCV.sf(V, 2.43), Xr)
    order = list(terms)
    out["terms"] = {k: {"s800": v["S"][800], "s700": v["S"][700], "B800_w": v["B"][800], "W_star_w": v["W"],
                        "c_zeros_w": v["CZ"], "xfer": v["X"]} for k, v in terms.items()}
    out["rereferral"] = {"E64_runs": n64, "E80_E83_runs": nk}

    pred160 = {k: predict_all(ch, terms[k], D160, ty160) for k in order}
    pred143 = {k: predict_all(ch, terms[k], D143, ty143) for k in order}
    # M8 as frozen: E160's own columns (no chain; M8's own terms)
    pred160["M8_frozen_E160_columns"] = {n: (float(T160[n]["M8_mhz"]), float(T160[n]["M8_w"]), float(T160[n]["M8_rise"])) for n in T160}

    # ---- reproduction: A0 against E160's M7 columns, and against E143's registered rules
    dm = max(abs(pred160["A0_M7_frozen"][n][0] - float(T160[n]["M7_mhz"])) for n in T160)
    dw = max(abs(pred160["A0_M7_frozen"][n][1] - float(T160[n]["M7_w"])) for n in T160)
    rep143 = R143["score"]["rules"]
    out["reproduction"] = {"A0_vs_E160_M7_columns_max_abs_mhz": dm, "A0_vs_E160_M7_columns_max_abs_w": dw,
                           "E160_M7_columns_rounding": "M7_mhz to 0.1 MHz, M7_w to 0.01 W"}
    L.append(f"  reproduction: A0 (M7 as frozen in m7.json) against E160's own M7 columns, max |d| {dm:.3f} MHz and {dw:.4f} W over 48 tiles")

    # ---- scores
    sc160 = {k: score(pred160[k], meas160, grp160, rng) for k in pred160}
    sc143 = {k: score(pred143[k], meas143, grp143, rng) for k in order}
    out["E160"] = sc160
    out["E143"] = sc143
    out["E143_registered"] = {k: {"rms": rep143[k]["rms"], "mean_err": rep143[k]["mean_err"]} for k in ("E143-F1", "E143-F2", "E143-W1", "E143-W2")}
    reg160 = R160["score"]["rules"]
    out["E160_registered_M8"] = {k: {"rms": reg160[k]["rms"], "mean_err": reg160[k]["mean_err"]} for k in ("E160-F1", "E160-F2", "E160-W1", "E160-W2")}
    L.append(f"  E160's registered M8 scores: F1 {reg160['E160-F1']['rms']} MHz (mean {reg160['E160-F1']['mean_err']:+}), F2 {reg160['E160-F2']['rms']} "
             f"({reg160['E160-F2']['mean_err']:+}), W1 {reg160['E160-W1']['rms']} W ({reg160['E160-W1']['mean_err']:+}), W2 {reg160['E160-W2']['rms']} ({reg160['E160-W2']['mean_err']:+})")
    L.append("")
    L.append("  E160 (pool 6, run after the exponent was committed): rms (mean) [95% over tiles, one session]")
    L.append(f"  {'arm':44s} {'s800':>7s} {'W*':>7s} | {'governed clock MHz':28s} | {'governed board W':26s} | {'pinned clock':14s} | {'pinned board W':16s}")
    for k in pred160:
        s = sc160[k]
        t = terms.get(k)
        L.append(f"  {k:44s} {t['S'][800] if t else float('nan'):7.4f} {t['W'] if t else float('nan'):7.3f} | "
                 f"{s['governed']['mhz_rms']:6.2f} ({s['governed']['mhz_mean']:+6.2f}) [{s['governed']['mhz_rms_95_over_tiles'][0]:5.2f}, {s['governed']['mhz_rms_95_over_tiles'][1]:5.2f}] | "
                 f"{s['governed']['w_rms']:6.3f} ({s['governed']['w_mean']:+6.3f}) [{s['governed']['w_rms_95_over_tiles'][0]:4.2f}, {s['governed']['w_rms_95_over_tiles'][1]:4.2f}] | "
                 f"{s['pinned']['mhz_rms']:5.2f} ({s['pinned']['mhz_mean']:+5.2f}) | {s['pinned']['w_rms']:5.3f} ({s['pinned']['w_mean']:+6.3f}) | rise all {s['all']['rise_rms']:.3f} C")
    L.append("")
    L.append("  E143 (pool 5) through the same arms, for comparison (A0 must equal E143's registered F1/W1/F2/W2 to rounding):")
    L.append(f"    registered: F1 {rep143['E143-F1']['rms']} ({rep143['E143-F1']['mean_err']:+}), W1 {rep143['E143-W1']['rms']} ({rep143['E143-W1']['mean_err']:+}), "
             f"F2 {rep143['E143-F2']['rms']} ({rep143['E143-F2']['mean_err']:+}), W2 {rep143['E143-W2']['rms']} ({rep143['E143-W2']['mean_err']:+})")
    for k in order:
        s = sc143[k]
        L.append(f"  {k:44s} governed clock {s['governed']['mhz_rms']:6.2f} ({s['governed']['mhz_mean']:+6.2f}) board {s['governed']['w_rms']:6.3f} ({s['governed']['w_mean']:+6.3f}) | "
                 f"pinned clock {s['pinned']['mhz_rms']:5.2f} ({s['pinned']['mhz_mean']:+5.2f}) board {s['pinned']['w_rms']:5.3f} ({s['pinned']['w_mean']:+6.3f})")

    # ---- the shift the exponent makes, and offset against shape
    L.append("")
    L.append("  WHAT THE EXPONENT CHANGES (governed tiles): the per-tile shift of the predicted clock, arm minus A2 (MHz)")
    shifts = {}
    for k in ("A5_n2.28_chain_on_committed_powers", "A5c_n2.28_chain_on_E66_rereferred_powers", "A3_n2.43_chain_refit", "A0_M7_frozen"):
        for sess, pr, gr in (("E160", pred160, grp160), ("E143", pred143, grp143)):
            sel = [n for n in gr if gr[n] == "governed"]
            d = [pr[k][n][0] - pr["A2_n2.00_chain_refit"][n][0] for n in sel]
            dwp = [pr[k][n][1] - pr["A2_n2.00_chain_refit"][n][1] for n in sel]
            shifts[f"{k}|{sess}"] = {"mean_mhz": mean(d), "min_mhz": min(d), "max_mhz": max(d), "mean_w": mean(dwp)}
            L.append(f"    {k:44s} {sess}: mean {mean(d):+6.2f} MHz (range {min(d):+6.2f} to {max(d):+6.2f}), board {mean(dwp):+6.3f} W")
    out["shift_vs_A2_governed"] = shifts

    L.append("")
    L.append("  OFFSET AGAINST SHAPE (governed clock): each session's mean error, its sd about that mean, and both sessions pooled (36 tiles)")
    pooled = {}
    for k in order:
        _, e160, w160 = errors(pred160[k], meas160, grp160, "governed")
        _, e143, w143 = errors(pred143[k], meas143, grp143, "governed")
        pooled[k] = {"E160_mean_mhz": mean(e160), "E160_sd_mhz": sd0(e160), "E143_mean_mhz": mean(e143), "E143_sd_mhz": sd0(e143),
                     "pooled_rms_mhz": rms(e160 + e143), "pooled_n": len(e160) + len(e143),
                     "pooled_rms_w": rms(w160 + w143), "E160_w_mean": mean(w160), "E143_w_mean": mean(w143),
                     "sessions_mean_gap_mhz": mean(e160) - mean(e143)}
        L.append(f"    {k:44s} E143 mean {mean(e143):+6.2f} sd {sd0(e143):5.2f} | E160 mean {mean(e160):+6.2f} sd {sd0(e160):5.2f} | "
                 f"gap {mean(e160) - mean(e143):+6.2f} | pooled rms {rms(e160 + e143):6.2f} MHz, board {rms(w160 + w143):5.3f} W")
    out["offset_vs_shape_governed"] = pooled

    # paired bootstraps on E160's governed tiles, arm against A2 and against A0
    _, eA2, wA2 = errors(pred160["A2_n2.00_chain_refit"], meas160, grp160, "governed")
    _, eA0, wA0 = errors(pred160["A0_M7_frozen"], meas160, grp160, "governed")
    pb = {}
    L.append("")
    L.append("  PAIRED BOOTSTRAP over E160's 17 governed tiles (one session): rms(arm) - rms(reference), 95% interval")
    for k in pred160:
        if k in ("A2_n2.00_chain_refit",):
            continue
        _, ek, wk = errors(pred160[k], meas160, grp160, "governed")
        pb[k] = {"vs_A2_mhz": boot_paired(ek, eA2, rng), "vs_A0_mhz": boot_paired(ek, eA0, rng),
                 "vs_A2_w": boot_paired(wk, wA2, rng)}
        L.append(f"    {k:44s} clock vs A2 [{pb[k]['vs_A2_mhz']['lo95']:+6.2f}, {pb[k]['vs_A2_mhz']['hi95']:+6.2f}] MHz; vs A0 "
                 f"[{pb[k]['vs_A0_mhz']['lo95']:+6.2f}, {pb[k]['vs_A0_mhz']['hi95']:+6.2f}]; board vs A2 [{pb[k]['vs_A2_w']['lo95']:+6.3f}, {pb[k]['vs_A2_w']['hi95']:+6.3f}] W")
    out["paired_bootstrap_E160_governed"] = pb

    # per-tile table for E160's governed tiles
    rows = []
    for n in sorted(T160):
        rows.append({"tile": n, "group": grp160[n], "type": ty160[n], "D600_M7_w": D160[n], "mhz_meas": meas160[n][0], "w_meas": meas160[n][1],
                     **{f"{k}_mhz": pred160[k][n][0] for k in pred160}, **{f"{k}_w": pred160[k][n][1] for k in pred160}})
    out["E160_tiles"] = rows
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
