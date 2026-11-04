#!/usr/bin/env python3
"""Q140(l): corrections after verification (Wed 4 Nov 2026, from 01:37 PST to its commit). Written after the lane's registered
result (5b98bd5c) and its verifier's report were read. NOT registered: no verdict, no frozen number and nothing in
m9_a2.json depends on it. m9_a2.json, predict_m9_a2.py, fit_m9_a2.py, loso.json, rows-m9a2.json, fit-output.txt and
posthoc.txt are unchanged. Reads committed files only; writes corrections.json beside itself and prints corrections.txt.

    python3 -B corrections_q140l.py > corrections.txt        (numpy; a few minutes on the Intel)

C0  The import path reproduces the committed result: the frozen configuration's leave-one-session-out scores equal
    loso.json's, and the voltage chain with a tuple of left-out dirs equals fit_m9_a2.reads_chain with one.
C1  The handoff for heat over minutes and the large GEMM: M9's level composed with exactly one die law, both ways, on
    E161's G1Q and E159's three zeros holds.
C2  How much of the E143-against-E160 governed-clock offset the terms remove, held out.
C4  The selection's optimism: the registered forward rule run inside each fold, on its three training sessions only
    (each inner fold fitted on two), at 2 of 3 inner sessions and at 3 of 3; the selected terms then fitted on the three
    and scored on the held-out session, as in the registered folds.
C8  How many of the twelve session-format zeros offsets were measured, and their range.
C9  The pinned cells' bursts under 795 MHz, by clock and session.
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import json  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m9_a2 as F  # noqa: E402  (the registered fit's functions; its main() is never called here)
import predict_m9_a2 as A2  # noqa: E402  (the frozen prediction code, unchanged)

LOSO = json.load(open(os.path.join(HERE, "loso.json")))
M9 = json.load(open(os.path.join(HERE, "m9_a2.json")))
ROWS = json.load(open(os.path.join(HERE, "rows-m9a2.json")))
OUT = {"_note": "Q140(l) corrections after verification (post hoc, not registered; nothing frozen depends on them)",
       "m9_a2_sha256": A2.M9_SHA256}
CFG_ALL = {"T1": True, "T2": True, "T3": True, "T4": True}
TERMS = ("T1", "T2", "T3", "T4")


def P(s=""):
    print(s, flush=True)


def label(cfg):
    return "+".join(k for k in TERMS if cfg[k]) or "A0"


def setup():
    """the registered cells, ids, anchors and groups, exactly as fit_m9_a2.main() builds them"""
    allc, _ = F.load_cells()
    for i, c in enumerate(allc):
        c["id"] = i
    anchors = {h: {} for h in F.SESS}
    for c in allc:
        if c["anchor"]:
            anchors[c["session"]][c["type"]] = c["runs"]
    cells = [c for c in allc if not c["anchor"] and c["D"] is not None]
    pm, _, _ = F.predict(F.fixed_W_par(F.REG["reference_lines"]["R8"]["W"]), cells, anchors)
    for c, f in zip(cells, pm):
        c["group"] = "governed" if f < 795.0 else "pinned"
    return cells, anchors


# ------------------------------------------------------------------ T4's chain with several dirs left out
def chain_ex(dirs):
    """fit_m9_a2.reads_chain, with a tuple of data dirs left out (an inner fold leaves out its own and the outer one)"""
    F.reads_chain(None)  # loads and checks the reads once (F._READS, F._CH)
    pm = F.pvt_busy_means(F._READS, tuple(dirs))
    V = {f: pm[f"aifoundry2@{f}"] / 1000.0 for f in F.PTS}
    S = F.FCV.sf(V, 2.0)
    B, c64, r64, n64 = F._CH.fit_B(S)
    cz = {t: float(np.mean([v for k, v in c64.items() if f"-{t}-zeros" in k])) for t in F.TYPES}
    xfer = (pm["aifoundry3@600"] / pm["aifoundry2@600"]) ** 2
    return {"name": f"n = 2 from the reads without {list(dirs)}", "V": V, "B": B, "s": S, "cz": cz, "g": 1.0 / xfer, "xfer": xfer}


_CHAINS = {}


def fold_chain(cfg, left_out):
    if not cfg["T4"]:
        return F.base_chain()
    key = tuple(sorted(left_out))
    if key not in _CHAINS:
        _CHAINS[key] = chain_ex(tuple(F.REG["sessions"][h]["dir"] for h in key))
    return _CHAINS[key]


def scores_over(preds, cells, sess):
    out = {}
    for h in list(sess) + ["pooled"]:
        cs = [c for c in cells if (h == "pooled" and c["session"] in sess) or c["session"] == h]
        out[h] = F.score(cs, np.array([preds[c["id"]][0] for c in cs]), np.array([preds[c["id"]][1] for c in cs]))
    return out


def loso_over(cfg, cells, anchors, sess, also_out=()):
    """leave one of `sess` out, fitting on the others of `sess` only; T4's chain also leaves out `also_out`'s reads"""
    preds = {}
    for h in sess:
        chain = fold_chain(cfg, (h,) + tuple(also_out))
        par = F.fit(cfg, [c for c in cells if c["session"] in sess and c["session"] != h], chain, anchors)
        test = [c for c in cells if c["session"] == h]
        pm, pw, _ = F.predict(par, test, anchors)
        for c, a, b in zip(test, pm, pw):
            preds[c["id"]] = (float(a), float(b))
    return {"cfg": dict(cfg), "scores": scores_over(preds, cells, sess), "preds": preds}


def compare_over(new, cur, sess, kmin):
    """the registered rule (REGISTRATION.md, The rule) over `sess`, with 'at least kmin of them' for '3 of the 4'"""
    tol = {q: F.REG["rule"]["tolerance"][F.QLONG[q]] for q in F.QN}
    per = {}
    for q in F.QN:
        lower = [h for h in sess if new["scores"][h][q]["rms"] < cur["scores"][h][q]["rms"]]
        pl = new["scores"]["pooled"][q]["rms"] < cur["scores"]["pooled"][q]["rms"]
        per[q] = {"n_lower": len(lower), "pooled_cur": cur["scores"]["pooled"][q]["rms"], "pooled_new": new["scores"]["pooled"][q]["rms"],
                  "carries": bool(len(lower) >= kmin and pl), "rise": new["scores"]["pooled"][q]["rms"] - cur["scores"]["pooled"][q]["rms"]}
    car = [q for q in F.QN if per[q]["carries"]]
    harm = [q for q in F.QN if q not in car and per[q]["rise"] > tol[q]]
    return {"per_quantity": per, "carries_on": car, "harms": harm, "kept": bool(car) and not harm}


def c0(cells, anchors):
    fin = F.loso(CFG_ALL, cells, anchors)
    worst = 0.0
    for h in F.SESS + ["pooled"]:
        for q in F.QN:
            for k in ("rms", "mean"):
                worst = max(worst, abs(fin["scores"][h][q][k] - LOSO["arms"]["T1+T2+T3+T4"]["scores"][h][q][k]))
    wch = 0.0
    for h in F.SESS:
        a, b = F.reads_chain(F.REG["sessions"][h]["dir"]), chain_ex((F.REG["sessions"][h]["dir"],))
        wch = max([wch] + [abs(a["B"][f] - b["B"][f]) for f in F.PTS] + [abs(a["s"][f] - b["s"][f]) for f in F.PTS]
                  + [abs(a["cz"][t] - b["cz"][t]) for t in F.TYPES] + [abs(a["g"] - b["g"])])
    ok = worst < 1e-12 and wch < 1e-12
    OUT["C0"] = {"loso_final_vs_loso_json_worst": worst, "chain_ex_vs_reads_chain_worst": wch, "ok": ok}
    P(f"C0. The import path reproduces loso.json's frozen configuration (T1+T2+T3+T4), every session and pooled: worst |diff| {worst:.1e}; "
      f"the chain with a tuple of left-out dirs equals fit_m9_a2.reads_chain: worst {wch:.1e}: {'OK' if ok else 'FAIL'}")
    if not ok:
        raise SystemExit("C0 failed: nothing else is computed")
    return fin


def c1():
    P("")
    P("C1. The handoff: M9's level composed with exactly one die law (post hoc, linear)")
    par, rel = M9["params"], M9["relation"]
    beta, kT, Tref = par["beta"], par["kT_w_per_c"], par["T_ref_c"]
    fb = M9["fallback_delta_w"]
    m8 = F.M8
    # E161 G1Q
    s = open(os.path.join(F.DD, "2026-11-03-e161-heat-e2e-aifoundry2", "corrections.txt")).read()
    g1q = json.loads(s[s.find("{"):])["C1"]["G1Q"]
    T_pl = g1q["registered_readings_unrounded"]["plateau_measured_C"]
    dec = g1q["decomposition_posthoc"]
    lvl = dec["M8_level_offset_in_kernel_launches_ge790MHz_W"]
    fp = dec["fixed_points"]
    e_cont, e_lvl = fp["as registered: continuous work, M8's level"]["plateau_err_C"], fp["M8's level alone (set to the kernel launches' at >= 790 MHz)"]["plateau_err_C"]
    e_duty, e_both = fp["the kernel duty alone"]["plateau_err_C"], fp["both"]["plateau_err_C"]
    gain_cont, gain_duty = (e_lvl - e_cont) / lvl, (e_both - e_duty) / lvl   # C of plateau error gained per W of level removed
    D = json.load(open(os.path.join(F.DD, "2026-11-03-e153-blind6-aifoundry3", "e153.json")))["items"]["int8.b_line_zero_ff"]["D"]["mean"]
    L8_m8 = m8["relation"]["B_w"]["800"] + (m8["params"]["c_zeros_w"]["int8"] + m8["params"]["g"]["int8"] * D) * m8["relation"]["s_f"]["800"]
    L8_m9 = rel["B_w"]["800"] + (rel["c_zeros_w"]["int8"] + rel["g"] * D) * rel["s_f"]["800"]
    shift = beta * fb["int8"]
    q139e_k, q139e_T = 0.442, 56.0   # Q139(e)'s board law and reference die (its README, What this cannot say; D2)
    comp = {
        "shift_alone_on_M8_relation_as_the_lane": lvl + shift,
        "shift_alone": lvl + (L8_m9 - L8_m8) + shift,
        "M9_whole": lvl + (L8_m9 - L8_m8) + shift + kT * (T_pl - Tref) - q139e_k * (T_pl - q139e_T),
    }
    heat = {k: {"continuous_C": e_cont + gain_cont * (lvl - v), "kernel_duty_C": e_duty + gain_duty * (lvl - v)} for k, v in comp.items()}
    OUT["C1"] = {"E161_G1Q": {"tile": "int8.b_line_zero_ff", "D_w": D, "plateau_die_c": T_pl, "M8_level_high_by_w": lvl,
                              "relation_M9_minus_M8_at_800_w": L8_m9 - L8_m8, "M9_shift_w": shift, "kT_w_per_c": kT, "T_ref_c": Tref,
                              "q139e_law": {"w_per_c": q139e_k, "reference_die_c": q139e_T},
                              "level_high_by_w": comp, "plateau_err_c": heat,
                              "M8_plateau_err_c": {"continuous_C": e_cont, "kernel_duty_C": e_duty},
                              "gain_c_per_w": {"continuous": gain_cont, "kernel_duty": gain_duty},
                              "kT_fit_range_of_burst_starts_c": [45.0, 56.0]}}
    P(f"  E161 G1Q (int8.b_line_zero_ff, D {D:.3f} W; plateau die {T_pl:.2f} C): M8's in-work level {lvl:+.3f} W high (E161 corrections C1)")
    P(f"    M9's relation minus M8's at 800 MHz {L8_m9 - L8_m8:+.4f} W; M9's zeros-level shift beta x fallback(int8) {shift:+.4f} W, at T_ref {Tref:.2f} C")
    P(f"    (a) the shift alone, Q139(e)'s 0.442 W/C from its 56.0 C reference die kept: {comp['shift_alone']:+.3f} W "
      f"(the lane's {comp['shift_alone_on_M8_relation_as_the_lane']:+.3f} left out the relation's {L8_m9 - L8_m8:+.4f})")
    P(f"    (b) M9 whole, its k_T {kT:.4f} W/C from {Tref:.2f} C in place of 0.442 from 56.0, at the plateau die: {comp['M9_whole']:+.3f} W "
      f"(k_T was fitted on burst starts of 45-56 C; the plateau is {T_pl - 56.0:.1f} C above the highest)")
    P(f"    plateau error through E161's committed fixed points (linear; {gain_cont:.3f} C per W at continuous work, {gain_duty:.3f} at the kernel duty):")
    P(f"      M8: continuous {e_cont:+.2f} C, kernel duty {e_duty:+.2f} C; (a) {heat['shift_alone']['continuous_C']:+.2f} / {heat['shift_alone']['kernel_duty_C']:+.2f} C; "
      f"(b) {heat['M9_whole']['continuous_C']:+.2f} / {heat['M9_whole']['kernel_duty_C']:+.2f} C")
    # E159's three zeros holds
    rows = []
    for r in LOSO["checks"]["E159"]:
        Ts = r["die_start_c"]
        a = r["G3_plus_M9_shift_miss_w"]
        b = a - kT * (Ts - Tref)
        rows.append({"hold": r["hold"], "die_start_c": Ts, "measured_board_w": r["measured_board_w"], "G3_miss_w": r["G3_miss_meas_minus_pred_w"],
                     "shift_alone_miss_w": a, "with_M9_kT_at_start_die_miss_w": b})
    spread_meas = max(r["measured_board_w"] for r in rows) - min(r["measured_board_w"] for r in rows)
    spread_kT = kT * (max(r["die_start_c"] for r in rows) - min(r["die_start_c"] for r in rows))
    OUT["C1"]["E159_zeros"] = {"holds": rows, "measured_board_spread_w": spread_meas, "kT_start_die_spread_w": spread_kT,
                               "note": "G3's P0 is a first-second law referenced at each run's own start die (0.1 W/C effective in-run constant); "
                                       "(b) adds M9's k_T as a start-die term on P0's level, the role G4's own start-die term (0.44-0.50 W/C) has in Q140's brief"}
    P(f"  E159's zeros GEMMs (measured - predicted, W): hold, start die, G3, (a) G3 + M9's shift, (b) G3 + M9's shift + k_T (T_start - T_ref)")
    for r in rows:
        P(f"    {r['hold']}: start {r['die_start_c']:.0f} C, measured {r['measured_board_w']:.2f} W; G3 {r['G3_miss_w']:+.2f}; (a) {r['shift_alone_miss_w']:+.2f}; (b) {r['with_M9_kT_at_start_die_miss_w']:+.2f}")
    P(f"    the measured window boards spread {spread_meas:.2f} W over starts of 52-57 C; a start-die term at k_T spreads the prediction {spread_kT:.2f} W")
    P(f"  The level referred between 54.38 C (M9's T_ref) and 56.0 C (Q139(e)'s reference): k_T x 1.62 = {kT * (56.0 - Tref):.2f} W, 0.442 x 1.62 = {0.442 * (56.0 - Tref):.2f} W")
    OUT["C1"]["reference_gap_w"] = {"kT": kT * (56.0 - Tref), "q139e": 0.442 * (56.0 - Tref)}


def c2():
    P("")
    P("C2. The E143-against-E160 governed-clock offset, held out (means, MHz; from loso.json)")
    get = lambda s: (s["E143"]["G"]["mean"], s["E160"]["G"]["mean"])  # noqa: E731
    lines = [("R7 (M7 as frozen)", LOSO["reference_lines"]["R7"]["scores"]), ("R8 (M8 as frozen)", LOSO["reference_lines"]["R8"]["scores"])]
    lines += [(k, LOSO["arms"][k]["scores"]) for k in ("A0", "T1+T2", "T1+T2+T3", "T1+T2+T3+T4")]
    tab = {}
    for lab, s in lines:
        a, b = get(s)
        tab[lab] = {"E143": a, "E160": b, "split": b - a}
        P(f"  {lab:20s} E143 {a:+6.2f}  E160 {b:+6.2f}  split {b - a:5.2f}")
    r7, fin, t12, t123 = tab["R7 (M7 as frozen)"], tab["T1+T2+T3+T4"], tab["T1+T2"], tab["T1+T2+T3"]
    rem = {"E143_offset_removed": 1 - abs(fin["E143"]) / abs(r7["E143"]), "E160_offset_removed": 1 - abs(fin["E160"]) / abs(r7["E160"]),
           "split_removed_vs_M7": 1 - fin["split"] / r7["split"], "T3_step_split_removed": 1 - t123["split"] / t12["split"]}
    # the die-start gap and the model's clock sensitivity on the governed cells, from the frozen code
    Tm = {h: np.mean([x["T"] for r in ROWS["rows"] if r["session"] == h for x in r["runs"]]) for h in ("E143", "E160")}
    anch = {h: {t: [{"burst_w": x["w"], "burst_mhz": x["mhz"], "die_start": x["T"]} for x in rr] for t, rr in a.items()} for h, a in ROWS["anchors"].items()}
    sens = [A2.burst(r["D"], r["type"], anch[r["session"]], [x["T"] for x in r["runs"]])["d_mhz_per_c_die_start"]
            for r in ROWS["rows"] if r["group"] == "governed"]
    gap = Tm["E143"] - Tm["E160"]
    rem["die_start_gap_c"], rem["sens_mhz_per_c_range"], rem["sens_mhz_per_c_mean"] = gap, [min(sens), max(sens)], float(np.mean(sens))
    rem["sens_x_gap_share_of_M7_split"] = abs(np.mean(sens)) * gap / r7["split"]
    OUT["C2"] = {"means": tab, "shares": rem}
    P(f"  final against M7 as frozen: E143's offset {100 * rem['E143_offset_removed']:.0f}% removed, E160's {100 * rem['E160_offset_removed']:.0f}%, the split "
      f"{100 * rem['split_removed_vs_M7']:.0f}% ({r7['split']:.2f} -> {fin['split']:.2f} MHz); the sign still flips")
    P(f"  T3's own step (T1+T2 -> T1+T2+T3): split {t12['split']:.2f} -> {t123['split']:.2f} MHz, {100 * rem['T3_step_split_removed']:.0f}% removed")
    P(f"  die starts over the scored bursts: E143 {Tm['E143']:.2f} C, E160 {Tm['E160']:.2f} C (gap {gap:.2f} C); the frozen code's clock change per C of die start on the "
      f"governed cells {min(sens):.2f} to {max(sens):.2f} MHz (mean {np.mean(sens):.2f}); x the gap = {abs(np.mean(sens)) * gap:.2f} MHz, "
      f"{100 * rem['sens_x_gap_share_of_M7_split']:.0f}% of M7's split")


def c4(cells, anchors, fin):
    P("")
    P("C4. The selection's optimism: the forward rule run inside each fold on its three training sessions (each inner fold fitted on two)")
    res = {}
    for kmin in (2, 3):
        preds, sel = {}, {}
        for h in F.SESS:
            inner = [q for q in F.SESS if q != h]
            cache = {}

            def arm(cfg):
                lab = label(cfg)
                if lab not in cache:
                    cache[lab] = loso_over(cfg, cells, anchors, inner, also_out=(h,))
                return cache[lab]
            cur = {k: False for k in TERMS}
            steps = []
            for term in TERMS:
                cand = dict(cur, **{term: True})
                c = compare_over(arm(cand), arm(cur), inner, kmin)
                steps.append({"term": term, "against": label(cur), "kept": c["kept"], "carries_on": c["carries_on"], "harms": c["harms"],
                              "pooled": {q: [c["per_quantity"][q]["pooled_cur"], c["per_quantity"][q]["pooled_new"], c["per_quantity"][q]["n_lower"]] for q in F.QN}})
                if c["kept"]:
                    cur = cand
            sel[h] = {"selected": label(cur), "steps": steps}
            # the selected terms fitted on the three, scored on h: the registered fold for that configuration
            par = F.fit(cur, [c for c in cells if c["session"] != h], fold_chain(cur, (h,)), anchors)
            test = [c for c in cells if c["session"] == h]
            pm, pw, _ = F.predict(par, test, anchors)
            for c, a, b in zip(test, pm, pw):
                preds[c["id"]] = (float(a), float(b))
        sc = F.evaluate(preds, cells)
        d = {q: sc["pooled"][q]["rms"] - fin["scores"]["pooled"][q]["rms"] for q in F.QN}
        # the bands' rule (m9_a2.json bands.rule, D3) applied to the nested errors: information only, the frozen bands stay
        em = np.array([c["mhz"] - preds[c["id"]][0] for c in cells])
        ew = np.array([c["w"] - preds[c["id"]][1] for c in cells])
        gov = np.array([preds[c["id"]][0] < 795.0 for c in cells])
        nb = {"governed": {"n": int(gov.sum()), "q95_abs_mhz": F.q95(em[gov]), "q95_abs_board_w": F.q95(ew[gov])},
              "pinned": {"n": int((~gov).sum()), "q95_abs_mhz": F.q95(em[~gov]), "q95_abs_board_w": F.q95(ew[~gov])}}
        res[f"at_least_{kmin}_of_3"] = {"selected_per_fold": sel, "scores": sc, "nested_minus_quoted_pooled_rms": d, "nested_bands": nb}
        P(f"  rule at {kmin} of 3 inner sessions: selected per held-out session: " + ", ".join(f"{h} {sel[h]['selected']}" for h in F.SESS))
        P(F.fmt_scores(f"nested (selection inside the fold, {kmin}/3)", sc))
        P(F.fmt_scores("quoted (T1+T2+T3+T4, registered)", fin["scores"]))
        P("    nested minus quoted, pooled rms: " + ", ".join(f"{q} {d[q]:+.4f}" for q in F.QN))
        fb_ = M9["bands"]
        P(f"    the bands' rule on the nested errors (information; the frozen bands stay): governed n {nb['governed']['n']} {nb['governed']['q95_abs_mhz']:.2f} MHz / "
          f"{nb['governed']['q95_abs_board_w']:.2f} W, pinned n {nb['pinned']['n']} {nb['pinned']['q95_abs_mhz']:.2f} MHz / {nb['pinned']['q95_abs_board_w']:.2f} W "
          f"(frozen: {fb_['governed']['q95_abs_mhz']:.2f} / {fb_['governed']['q95_abs_board_w']:.2f} and {fb_['pinned']['q95_abs_mhz']:.2f} / {fb_['pinned']['q95_abs_board_w']:.2f})")
        for h in F.SESS:
            P(f"    {h} held out, inner steps: " + "; ".join(f"{s['term']} vs {s['against']} {'kept' if s['kept'] else 'not kept'} (carries on {s['carries_on']})" for s in sel[h]["steps"]))
    OUT["C4"] = res


def c8():
    P("")
    P("C8. The session-format zeros offsets: measured or filled")
    meas, filled = [], []
    for h in F.SESS:
        a = ROWS["anchors"][h]
        for t in F.TYPES:
            ok = [x for x in a.get(t, []) if x["mhz"] >= F.REG["anchor_run_min_mhz"]]
            (meas if ok else filled).append((h, t, M9["session_deltas_w"][h][t]))
    lo, hi = min(abs(v) for _, _, v in meas), max(abs(v) for _, _, v in meas)
    OUT["C8"] = {"measured": len(meas), "filled": [f"{h} {t}" for h, t, _ in filled], "measured_abs_range_w": [lo, hi],
                 "filled_values_w": {f"{h} {t}": v for h, t, v in filled}}
    P(f"  measured {len(meas)} of {len(meas) + len(filled)}; filled: " + ", ".join(f"{h} {t} {v:+.3f} W" for h, t, v in filled)
      + f"; the measured ones, die-referred, sit {lo:.2f}-{hi:.2f} W under the relation's 800 MHz zeros level (m9_a2.json session_deltas_w)")


def c9():
    P("")
    P("C9. The pinned cells' bursts under 795 MHz (rows-m9a2.json; every scored burst)")
    n = sum(len(r["runs"]) for r in ROWS["rows"])
    slow = sorted(((x["mhz"], r["session"], r["name"], x["w"], x["T"]) for r in ROWS["rows"] if r["group"] == "pinned" for x in r["runs"] if x["mhz"] < 795.0))
    OUT["C9"] = {"scored_bursts": n, "slow": [{"mhz": a, "session": b, "tile": c, "board_w": d, "die_start_c": e} for a, b, c, d, e in slow]}
    P(f"  {len(slow)} of {n} scored bursts:")
    for a, b, c, d, e in slow:
        P(f"    {a:6.1f} MHz  {b:5s} {c:24s} board {d:5.1f} W, start {e:.0f} C")


def main():
    cells, anchors = setup()
    P("Q140(l) corrections after verification (post hoc, not registered; nothing frozen depends on them)")
    P(f"m9_a2.json sha256 {A2.M9_SHA256} (unchanged)")
    fin = c0(cells, anchors)
    c1()
    c2()
    c4(cells, anchors, fin)
    c8()
    c9()
    json.dump(OUT, open(os.path.join(HERE, "corrections.json"), "w"), indent=1, sort_keys=True, default=float)


if __name__ == "__main__":
    main()
