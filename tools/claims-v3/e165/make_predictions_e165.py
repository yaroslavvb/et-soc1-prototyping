#!/usr/bin/env python3
"""E165 (Q141(g)): writes predictions-e165.json, everything E165 scores, frozen before any claim and any launch. No card. NOTHING IS FITTED OR
REFITTED HERE: every predicted number is Q140(x)'s (predictions-blind7-aifoundry2.json, lab 75802201), copied by key after its sha256 is checked,
or the frozen predictor's own output (Q140(l)'s predict_m9_a2.burst, 5b98bd5c), called unchanged.

    python3 -B tools/claims-v3/e165/make_predictions_e165.py > tools/claims-v3/e165/predictions-e165.txt

WHAT IT WRITES
  tiles      pool 7's 61 tiles: type, priority, anchor, class (blind7.json's case letter), real, the run value and label, the manifest's sha256;
             LEFT OUT (by name, from admission-aifoundry2-82w.json: the 6 tiles whose 95% upper peak exceeds 82 W under any of its three models);
             the GROUP, fixed by the frozen file (M9.a2_q140l.group: governed = M9's part predicts the burst below 795 MHz at the fallback offset
             and the reference die); SCORED = run and not a zeros anchor (the zeros anchors are the primary's inputs); the primary's inputs
             (M9's D600 on aifoundry3's footing and its 95% half-band, as predict_blind7.py passed them); the frozen blocks copied by key
             (M9.a2_q140l whole; M8's, M7's and M6's burst predictions and bands; M8's peaks); the admission estimate.
  check      the frozen predictor called with no session read (anchors None, die starts None) on each tile's frozen inputs reproduces the frozen
             M9.a2_q140l block field for field, on all 61 tiles: the primary's recompute is the frozen file's own code path.
  order      the registered run order: 3 passes of 57 runs; each pass opens with the three zeros anchors (Q139 critic rank 2: "a blind burst
             session that runs its zeros anchors first"), in a seeded order, then the other 52 admitted tiles and E80's two replicate tiles in a
             seeded shuffled order (order_seed 165). 171 bursts.
  replicate  E80's own kinds tiles fp16/randn and int8/full, once a pass (E160's R0 drift check): E80's and E83's mean cell, E143's and E160's
             measured cells; the admission estimate the larger of their highest board samples in E143 and E160 and P800 from E143's and E160's
             measured c plus M8's q95 peak excess (2.95 W). E80's fp32/randn stays dropped (E143's highest 84.30-84.97 W).
  reference  (a) the burst heat law's 112 leave-one-kind-out residuals (E143's frozen copy, as E160-H1); (b) Q140(l)'s END-TO-END errors with the
             models' blind D, each session predicted by the fold that held it out (E143: M7's D, 33 cells; E160: M8's D, 45 cells), recomputed
             here through the frozen predictor with the fold's committed parameters (loso.json arms T1+T2+T3+T4 params) and the cells' committed
             runs (rows-m9a2.json): they must reproduce loso.json's end_to_end_blind_D to 1e-9 (E160: 3.683 MHz / 0.663 W / 0.796 W), else
             refused; split by Q140(l)'s group (M8 as frozen with the measured D); (c) the nested widths of A1-3 (reported coverage only).
  bars       the bootstrap lines and coverage lines at the full plan (12 governed, 40 pinned, 52 scored), and a forecast of rank 2's lines from the
             end-to-end reference (registered, information only).
  rules      E165's decision rules (E165.md), the stops, the admission limits, the C check's rule and the DMA rule (E160's, unchanged).
"""
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402

ROOT = C.ROOT
LOSO_REL = f"{C.Q140L_REL}/loso.json"
ROWS_REL = f"{C.Q140L_REL}/rows-m9a2.json"
CORR_REL = f"{C.Q140L_REL}/corrections.json"
P6_REL = "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json"
P143_REL = "tools/claims-v3/e143/predictions-e143.json"
P160_REL = "tools/claims-v3/e160/predictions-e160.json"
R160_REL = "docs/reports/data/2026-11-03-e160-blind6-aifoundry2/results.json"
Q160_REL = "docs/reports/data/2026-11-03-e160-blind6-aifoundry2/aifoundry2/queue.jsonl"
KINDS_REL = "tools/claims-v3/kinds/kinds.json"
FOLD_ARM = "T1+T2+T3+T4"          # Q140(l)'s registered final configuration (m9_a2.json kept_terms)
REPLICATES = (("fp16", "randn"), ("int8", "full"))
STOPS = {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3}   # E160's (section 22: every registered board stop at most 85 W)
LIMIT_W = 82.0        # E160's run-time admission line (section 22)
PEAK_LOCK_W = 82.0    # E159's lock, E160's: after a run whose highest board sample reached 82 W, nothing at or above its estimate runs
ORDER_SEED = 165
PASSES = 3
NESTED_WIDTHS = {  # README-predictions.md A1-3 (Q140(l) corrections.txt C4): the bands' rule on the nested errors, inner rule 2 of 3 / 3 of 3
    "governed": {"mhz": [9.77, 11.97], "board_w": [2.06, 1.84]},
    "pinned": {"mhz": [15.35, 15.20], "board_w": [1.75, 1.48]},
}
R2_LINES = {"G_rms_max_mhz": 4.0, "G_abs_mean_max_mhz": 2.0, "Bg_abs_mean_max_w": 0.5, "Bp_abs_mean_max_w": 0.5, "Bp_rms_max_w": 1.0}
FROZEN_KEYS = ("burst_mhz", "burst_mhz_95", "burst_board_w", "burst_board_95", "burst_D_w", "burst_D_95", "burst_die_rise_c", "burst_die_rise_95")


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


def sha(rel):
    return C.sha256_file(os.path.join(ROOT, rel))


def d_band_hw(m9):
    """M9's 95% half-band on D at 600 MHz, as predict_blind7.py passed it to burst() (Q140(x))"""
    lo, hi = m9["D600_a3_95"]
    return (hi - lo) / 2.0


class Injected:
    """the frozen predictor with one held-out fold's committed parameters in place of m9_a2.json's (a context manager; the code path is the
    frozen file's, unchanged). Used only to recompute Q140(l)'s committed end-to-end errors, never for a prediction E165 scores."""
    KEYS = ("B", "S", "CZ", "G", "W", "DCAP", "BETA", "KT", "TREF", "CFG")

    def __init__(self, A2, p):
        self.A2, self.p = A2, p

    def __enter__(self):
        A2, p, ch = self.A2, self.p, self.p["chain"]
        self.saved = {k: getattr(A2, k) for k in self.KEYS}
        A2.B = {int(k): v for k, v in ch["B"].items()}
        A2.S = {int(k): v for k, v in ch["s"].items()}
        A2.CZ, A2.G = dict(ch["cz"]), ch["g"]
        A2.W, A2.DCAP, A2.BETA, A2.KT, A2.TREF, A2.CFG = p["W"], p["dcap"], p["beta"], p["kT"], p["T_ref"], dict(p["cfg"])
        return A2

    def __exit__(self, *a):
        for k, v in self.saved.items():
            setattr(self.A2, k, v)
        return False


def e2e_errors(A2, loso, rows, p6, p143):
    """Q140(l)'s end-to-end cells (loso.json end_to_end_blind_D), recomputed: (per-session errors, checks against loso.json)"""
    out, checks = {}, {}
    getD = {"E160": lambda n: p6[n]["M8"]["D600_a3_footing_w"], "E143": lambda n: p143[n]["models"]["M7"]["D600_a3_footing_w"]}
    src = {"E160": p6, "E143": p143}
    for h in ("E143", "E160"):
        p = loso["arms"][FOLD_ARM]["params"][h]
        anc = {t: [{"burst_w": r["w"], "burst_mhz": r["mhz"], "die_start": r["T"]} for r in rr] for t, rr in rows["anchors"][h].items()}
        cs = [r for r in rows["rows"] if r["session"] == h and r["name"] in src[h]]
        cells = []
        with Injected(A2, p) as M:
            delta, dsrc = M.session_delta(anc)
            for r in cs:
                c = M.CZ[r["type"]] + M.G * getD[h](r["name"])
                f, P = M._cell(c, r["type"], delta, [float(x["T"]) for x in r["runs"]])
                cells.append({"session": h, "name": r["name"], "type": r["type"], "group": r["group"], "mhz_meas": r["mhz"], "w_meas": r["w"],
                              "mhz_pred": f, "w_pred": P, "mhz_err": r["mhz"] - f, "w_err": r["w"] - P, "die_starts": [x["T"] for x in r["runs"]]})
        gov = [c for c in cells if c["group"] == "governed"]
        pin = [c for c in cells if c["group"] == "pinned"]
        got = {"G": (C.rms([c["mhz_err"] for c in gov]), C.mean([c["mhz_err"] for c in gov])),
               "Bg": (C.rms([c["w_err"] for c in gov]), C.mean([c["w_err"] for c in gov])),
               "Bp": (C.rms([c["w_err"] for c in pin]), C.mean([c["w_err"] for c in pin]))}
        want = loso["end_to_end_blind_D"][h][FOLD_ARM]
        worst = max(max(abs(got[q][0] - want[q]["rms"]), abs(got[q][1] - want[q]["mean"])) for q in got)
        checks[h] = {"n": len(cells), "n_governed": len(gov), "n_pinned": len(pin), "worst_abs_diff": worst,
                     "got": {q: {"rms": round(v[0], 6), "mean": round(v[1], 6)} for q, v in got.items()},
                     "committed": {q: {"rms": round(want[q]["rms"], 6), "mean": round(want[q]["mean"], 6)} for q in got},
                     "fold_params": {k: p[k] for k in ("W", "dcap", "beta", "kT", "T_ref")}, "anchor_delta_w": delta, "delta_source": dsrc}
        if worst > 1e-9 or len(cells) != want["n"]:
            raise SystemExit(f"refused: {h}'s end-to-end cells do not reproduce loso.json (worst {worst}, n {len(cells)} vs {want['n']})")
        out[h] = cells
    return out, checks


def forecast(gov_mhz, gov_w, pin_w, ng, npn, draws=20000, seed=1652):
    """registered, information only: the share of draws of ng governed and npn pinned errors (with replacement, from the end-to-end reference)
    that meet each of rank 2's lines"""
    rng = random.Random(seed)
    hit = {k: 0 for k in ("G_rms", "G_mean", "G_both", "Bg_mean", "Bp_mean", "Bp_rms", "Bp_both", "all_lines")}
    for _ in range(draws):
        gi = [rng.randrange(len(gov_mhz)) for _ in range(ng)]
        pi = [rng.randrange(len(pin_w)) for _ in range(npn)]
        g = [gov_mhz[i] for i in gi]
        bg = [gov_w[i] for i in gi]
        bp = [pin_w[i] for i in pi]
        a = C.rms(g) <= R2_LINES["G_rms_max_mhz"]
        b = abs(C.mean(g)) <= R2_LINES["G_abs_mean_max_mhz"]
        c = abs(C.mean(bg)) <= R2_LINES["Bg_abs_mean_max_w"]
        d = abs(C.mean(bp)) <= R2_LINES["Bp_abs_mean_max_w"]
        e = C.rms(bp) <= R2_LINES["Bp_rms_max_w"]
        for k, v in (("G_rms", a), ("G_mean", b), ("G_both", a and b), ("Bg_mean", c), ("Bp_mean", d), ("Bp_rms", e), ("Bp_both", d and e),
                     ("all_lines", a and b and c and d and e)):
            hit[k] += int(v)
    return {k: round(v / draws, 4) for k, v in hit.items()}


def main():
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    A2 = C.m9a2()
    pred = load(C.PRED_REL)
    man = C.manifest()
    adm = load(C.ADM_REL)
    a2in = load(C.A2IN_REL)
    m9 = load(C.M9A2_REL)
    assert pred["card"] == "aifoundry2" and pred["a2_part"]["primary"] == "a2_q140l" and pred["manifest_sha256"] == C.FROZEN[C.MAN_REL]
    assert pred["a2_part"]["terms_sha256"] == C.FROZEN[C.M9A2_REL] and pred["a2_part"]["predictor_sha256"] == C.FROZEN[C.PM9A2_REL]
    assert adm["source_sha256"] == C.FROZEN[C.PRED_REL] and adm["m9_primary_on_aifoundry2"] == "a2_q140l"
    left = set(adm["left_out"])
    peak = m9["peak"]
    B800, S800 = m9["M8_params_for_the_peak"]["B_w"]["800"], m9["M8_params_for_the_peak"]["s_f"]["800"]

    tiles, admission, dry_c, recheck = {}, {}, {}, {"tiles": 0, "fields": 0, "differ": []}
    for name in sorted(pred["tiles"]):
        rec = pred["tiles"][name]
        t = man[name]
        why = C.check_tile(ROOT, t)
        if why:
            raise SystemExit(f"refused: {why}")
        assert rec["type"] == t["type"] and rec["sha256"] == t["sha256"]["whole"] and rec["sha256_matches_manifest"]
        q = rec["M9"]["a2_q140l"]
        D, hw = rec["M9"]["D600_a3_footing_w"], d_band_hw(rec["M9"])
        assert a2in["tiles"][name]["D600_a3_footing_w"] == D and a2in["tiles"][name]["D600_a3_95"] == rec["M9"]["D600_a3_95"], name
        again = A2.burst(D, rec["type"], anchors=None, die_starts=None, D_band_hw=hw)
        for k, v in q.items():
            recheck["fields"] += 1
            if again.get(k) != v:
                recheck["differ"].append(f"{name}.{k}: {again.get(k)!r} vs frozen {v!r}")
        recheck["tiles"] += 1
        cls = (t.get("case") or "?").split(" ")[0]
        lab = C.label_of(name)
        est = max(adm["per_tile"][name]["peak_hi95_w"].values())
        out_by = adm["per_tile"][name]["left_out_by"]
        models = {"M9": {"a2_q140l": q, "D600_a3_footing_w": D, "D600_a3_95": rec["M9"]["D600_a3_95"], "D_band_hw": round(hw, 6),
                         "m8_relation": {k: rec["M9"][k] for k in FROZEN_KEYS}},
                  "M8": {k: rec["M8"][k] for k in FROZEN_KEYS + ("D600_a3_footing_w", "P800_w", "peak_board_w", "peak_board_hi95_w", "peak_over_82w")},
                  "M7": {k: rec["M7"][k] for k in FROZEN_KEYS + ("D600_a3_footing_w",)},
                  "M6": {k: rec["M6"][k] for k in FROZEN_KEYS + ("D600_a3_footing_w",)}}
        run = name not in left
        tiles[name] = {"type": t["type"], "priority": t["priority"], "anchor": bool(t.get("anchor")), "class": cls, "case": t.get("case"),
                       "real": bool(t.get("real")) or cls == "R", "zeros_anchor": name in C.ZEROS_ANCHORS, "label": lab, "values": C.tile_value(t),
                       "sha256": t["sha256"], "group": q["group"], "left_out": not run, "left_out_by": out_by,
                       "scored": run and name not in C.ZEROS_ANCHORS, "admission_estimate_w": est, "models": models}
        if not run:
            tiles[name]["left_out_why"] = (f"its 95% upper peak exceeds 82 W ({', '.join(out_by)}; at most {est} W): left out by name, as frozen in "
                                           f"admission-aifoundry2-82w.json; not duty-cycled (no frozen prediction exists for a duty-cycled burst)")
            continue
        c_exp = (rec["M8"]["P800_w"] - B800) / S800
        admission[lab] = {"c_ref_w": round(c_exp, 3), "fixed_p800_w": est,
                          "what": "the largest of the tile's three frozen 95% upper peaks (M9_a2_q140l, M9_m8_relation, M8: admission-aifoundry2-82w.json)"}
        dry_c[C.tile_value(t)] = round(c_exp, 3)
    if recheck["differ"]:
        raise SystemExit("refused: the frozen predictor does not reproduce the frozen block: " + "; ".join(recheck["differ"][:5]))

    # the replicates: E80's own tiles, against E80's and E83's mean cell, E143's and E160's measured cells
    P160 = load(P160_REL)
    R160 = load(R160_REL)
    K = load(KINDS_REL)
    rep = {}
    for ty, kd in REPLICATES:
        lab = f"k-{ty}-{kd}"
        r0 = P160["replicate"][lab]
        c160 = R160["cells"][lab]
        val = r0["values"]
        assert K["kinds"][ty][kd]["sha256"] == r0["sha256"] == C.sha256_file(os.path.join(ROOT, val[5:]))
        p800_160 = B800 + statistics.mean(c160["c_w_runs"]) * S800
        cand = {"e143_highest_w": max(r0["e143_peak_w_runs"]), "e160_highest_w": max(c160["peak_w_runs"]),
                "e143_p800_from_c_plus_q95_w": round(r0["e143_p800_from_c_w"] + peak["excess_q95_w"], 3),
                "e160_p800_from_c_plus_q95_w": round(p800_160 + peak["excess_q95_w"], 3)}
        est = round(max(cand.values()), 2)
        if est > LIMIT_W:
            raise SystemExit(f"refused: replicate {lab}'s estimate {est} W exceeds 82 W")
        rep[lab] = {"type": ty, "kind": kd, "values": val, "sha256": r0["sha256"], "ref_burst_mhz": r0["ref_burst_mhz"], "ref_burst_w": r0["ref_burst_w"],
                    "ref_source": r0["ref_source"], "e143_burst_mhz": r0["e143_burst_mhz"], "e143_burst_w": r0["e143_burst_w"],
                    "e160_burst_mhz": c160["burst_mhz"], "e160_burst_w": c160["burst_w"], "e160_rise_c": c160["rise_c"],
                    "e160_source": f"{R160_REL} cells.{lab}", "estimate_candidates_w": cand, "estimate_w": est}
        admission[lab] = {"c_ref_w": round(statistics.mean(c160["c_w_runs"]), 3), "fixed_p800_w": est,
                          "what": "the larger of E143's and E160's highest board samples on this tile and P800 from their measured c plus M8's q95 peak excess"}
        dry_c[val] = round(statistics.mean(c160["c_w_runs"]), 3)
    admission["rest"] = {"c_ref_w": 0.0, "fixed_p800_w": round(B800, 2), "what": "the idle card (no launch)"}

    # the registered order: each pass opens with the zeros anchors, then the rest shuffled; one seeded generator over the three passes
    run_names = [n for n in sorted(tiles) if not tiles[n]["left_out"]]
    zeros = [n for n in C.ZEROS_ANCHORS]
    rest = [C.label_of(n) for n in run_names if n not in C.ZEROS_ANCHORS] + [lab for lab in rep]
    rng = random.Random(ORDER_SEED)
    order = []
    for p in range(1, PASSES + 1):
        z = [C.label_of(n) for n in zeros]
        rng.shuffle(z)
        r = list(rest)
        rng.shuffle(r)
        for lab in z + r:
            order.append({"idx": len(order), "pass": p, "label": lab, "first_of_pass": lab in z})
    per_pass = len(order) // PASSES
    assert per_pass == 57 and len(order) == 171 and all(o["pass"] == o["idx"] // per_pass + 1 for o in order)

    # references
    loso, rows, p6, p143 = load(LOSO_REL), load(ROWS_REL), load(P6_REL)["tiles"], load(P143_REL)
    e2e, e2e_checks = e2e_errors(A2, loso, rows, p6, p143["tiles"])
    allc = e2e["E143"] + e2e["E160"]
    ref = {"e2e": {"source": (f"{LOSO_REL} arms.{FOLD_ARM}.params (each session's held-out fold) and {ROWS_REL} (the cells' runs, groups and anchors), "
                              f"through {C.PM9A2_REL}'s frozen code with the fold's parameters in place of m9_a2.json's; D: E143 M7's frozen D "
                              f"({P143_REL}), E160 M8's frozen D ({P6_REL}); reproduces {LOSO_REL} end_to_end_blind_D.{FOLD_ARM}"),
                   "checks": e2e_checks}}
    for g in ("governed", "pinned"):
        cc = [c for c in allc if c["group"] == g]
        ref["e2e"][g] = {"n": len(cc), "cells": [f"{c['session']}:{c['name']}" for c in cc], "mhz_err": [round(c["mhz_err"], 4) for c in cc],
                         "w_err": [round(c["w_err"], 4) for c in cc], "rms_mhz": round(C.rms([c["mhz_err"] for c in cc]), 4),
                         "rms_w": round(C.rms([c["w_err"] for c in cc]), 4), "mean_mhz": round(C.mean([c["mhz_err"] for c in cc]), 4),
                         "mean_w": round(C.mean([c["w_err"] for c in cc]), 4)}
    h = p143["reference"]["heat"]
    ref["heat"] = {"n": h["n"], "rise_err_c": h["rise_err_c"], "rms_c": h["rms_c"],
                   "source": f"{P143_REL} reference.heat (the burst heat law's 112 leave-one-kind-out residuals; M9 carries M8's law unchanged: m9_a2.json burst_heat)"}
    assert abs(h["rms_c"] - m9["burst_heat"]["loko_rms_c_kinds_refit"]) < 1e-3
    ref["nested_widths"] = dict(NESTED_WIDTHS, source=f"{C.POOL_REL}/README-predictions.md A1-3; {CORR_REL} C4")
    ref["frozen_bands"] = {"governed": {"mhz": round(m9["bands"]["governed"]["q95_abs_mhz"], 4), "board_w": round(m9["bands"]["governed"]["q95_abs_board_w"], 4)},
                           "pinned": {"mhz": round(m9["bands"]["pinned"]["q95_abs_mhz"], 4), "board_w": round(m9["bands"]["pinned"]["q95_abs_board_w"], 4)},
                           "die_rise_c": round(m9["burst_heat"]["q95_abs_c"], 4), "source": f"{C.M9A2_REL} bands, burst_heat.q95_abs_c"}

    scored = [n for n in run_names if tiles[n]["scored"]]
    ng = sum(1 for n in scored if tiles[n]["group"] == "governed")
    npn = len(scored) - ng
    eg, ep = ref["e2e"]["governed"], ref["e2e"]["pinned"]
    bars = {"F1_governed_clock_rms_mhz": C.boot_rms_range(eg["mhz_err"], ng), "F2_pinned_clock_rms_mhz": C.boot_rms_range(ep["mhz_err"], npn),
            "W1_governed_board_rms_w": C.boot_rms_range(eg["w_err"], ng), "W2_pinned_board_rms_w": C.boot_rms_range(ep["w_err"], npn),
            "H1_die_rise_rms_c": C.boot_rms_range(ref["heat"]["rise_err_c"], len(scored)),
            "coverage_line_all": C.coverage_line(len(scored)), "coverage_line_governed": C.coverage_line(ng), "coverage_line_pinned": C.coverage_line(npn)}
    bars = {k: ([round(x, 3) for x in v] if isinstance(v, tuple) else v) for k, v in bars.items()}
    fc = forecast(eg["mhz_err"], eg["w_err"], ep["w_err"], ng, npn)

    # card time from E160's queue (the same harness and burst): its s1 card-minutes per burst
    q = [json.loads(x) for x in open(os.path.join(ROOT, Q160_REL))]
    t_q0 = next(x["t_ms"] for x in q if x["kind"] == "queue_start")
    s1a = next(x["t_ms"] for x in q if x["kind"] == "session_start" and x.get("name") == "s1")
    s1b = next(x["t_ms"] for x in q if x["kind"] == "session_end" and x.get("name") == "s1")
    s_burst = (s1b - s1a) / 1000.0 / 150
    card = {"e160_s1_bursts": 150, "e160_s1_min": round((s1b - s1a) / 60000.0, 2), "s_per_burst": round(s_burst, 2),
            "e160_before_s1_min": round((s1a - t_q0) / 60000.0, 2), "e165_bursts": len(order), "e165_session_min": round(len(order) * s_burst / 60.0, 1),
            "e165_two_pass_subset_bursts": 2 * per_pass, "e165_two_pass_subset_min": round(2 * per_pass * s_burst / 60.0, 1),
            "session_cap_min": 40.0, "slot_min": 45, "subset_cap_min": 25.0, "subset_slot_min": 30, "source": Q160_REL}

    gfix = {g: sorted(n for n in scored if tiles[n]["group"] == g) for g in ("governed", "pinned")}
    out = {
        "experiment": "E165", "request": "Q141(g)", "card": "aifoundry2 card 0, under its own governor (65 W static TDP, 65 C threshold: read, never set), BL2 0.22.0",
        "_note": "frozen before any claim and any launch; nothing fitted or refitted: every prediction is Q140(x)'s, copied by key after its sha256 check, or "
                 "the frozen predictor's own output",
        "inputs_sha256": {**{r: sha(r) for r in (C.PRED_REL, C.MAN_REL, C.MANIFEST_REL, C.ADM_REL, C.A2IN_REL, C.M9A2_REL, C.PM9A2_REL, LOSO_REL, ROWS_REL,
                                                 P6_REL, P143_REL, P160_REL, R160_REL, Q160_REL, KINDS_REL)},
                          "tools/claims-v3/e165/e165_common.py": sha("tools/claims-v3/e165/e165_common.py"),
                          "tools/claims-v3/e165/make_predictions_e165.py": sha("tools/claims-v3/e165/make_predictions_e165.py")},
        "commits": {"pool7_predictions": "75802201", "pool7_notes": "3c9bb2ba", "m9_600": "1f244140", "m9_600_registration": "8dfafae3",
                    "m9_a2": "5b98bd5c", "m9_a2_registration": "245caffe", "m9_a2_corrections": "5c98c0c5", "parent_registration": "2e016917",
                    "parent_data": "6a330635", "parent_corrections": "42ba850f", "ccheck": "4946a992"},
        "primary": {"model": "M9's aifoundry2 part (Q140(l)): predict_m9_a2.burst(D, t, anchors, die_starts, D_band_hw), recomputed per tile",
                    "D": "tiles.<name>.models.M9.D600_a3_footing_w (M9's frozen D at 600 MHz on aifoundry3's footing)",
                    "D_band_hw": "tiles.<name>.models.M9.D_band_hw (half the width of M9.D600_a3_95; it enters only the peak)",
                    "anchors": "the session's zeros-anchor reads: per format, every counted burst of its anchor7_zeros tile ({burst_w, burst_mhz, die_start}, "
                               "as the registered reduction reads them); burst() keeps those at 795 MHz or more, fills a format with none from the "
                               "others, and takes the frozen fallback if none at all",
                    "die_starts": "the tile's own counted bursts' die starts (one per counted pass)",
                    "quantities": "burst_mhz, burst_board_w, burst_die_rise_c and their 95% bands, as burst() returns them (rounded by the frozen code)",
                    "groups": "fixed by the frozen file: tiles.<name>.group = M9.a2_q140l.group (governed below 795 MHz at the fallback and T_ref)",
                    "beside": "the frozen file's M9.a2_q140l block as frozen (fallback offset, T_ref 54.38 C); M8, M7 and M6 as frozen"},
        "recheck_frozen_block": recheck,
        "tiles": tiles, "left_out": sorted(left), "n_run": len(run_names), "n_scored": len(scored), "n_governed": ng, "n_pinned": npn,
        "groups": gfix, "replicate": rep, "order": order, "order_seed": ORDER_SEED, "passes": PASSES, "runs_per_pass": per_pass,
        "reference": ref, "plan_bars_at_full_n": bars, "forecast_rank2_lines_from_e2e_reference": fc,
        "admission": admission, "dry_c_w": dry_c, "dma": {"e143": P160["dma"]["e143"], "source": f"{P160_REL} dma (E143's launches, E160's rule)"},
        "card_time": card,
        "relation": {"B800": B800, "s800": S800, "heat_k_c_per_w": m9["burst_heat"]["k_used_c_per_w"], "P_idle_w": m9["burst_heat"]["P_idle_w"],
                     "kT_w_per_c": m9["params"]["kT_w_per_c"], "T_ref_c": m9["params"]["T_ref_c"], "source": f"{C.M9A2_REL} (M8_params_for_the_peak, burst_heat, params)"},
        "rules": {"safety": STOPS, "limit_w": LIMIT_W, "peak_lock_w": PEAK_LOCK_W, "min_passes": 2, "rank2_lines": R2_LINES,
                  "min_tiles": {"R2_governed": 8, "R2_pinned": 8, "F1": 8, "F2": 8, "W1": 8, "W2": 8, "H1": 10, "coverage": 10},
                  "replicate_mhz": 25.0, "replicate_w": 3.37,
                  "boot": {"draws": C.BOOT_DRAWS, "seed": C.BOOT_SEED, "form": "e165_common.boot_rms_range"},
                  "resolved": {"draws": C.PAIRED_DRAWS, "seed": C.PAIRED_SEED, "form": "e165_common.paired_rms_diff: the 95% interval of rms(M9 primary) - "
                                                                                       "rms(M7 as frozen) over the set's tiles; resolved better if its upper end is below 0"},
                  "c_check": "a burst counts only if every launch of it (the calibration launch included) has a C record that reads PASS in ccheck.py check "
                             "(bit-exact against Q139(k)'s reference); ROUNDING, UNMODELLED, FAIL and a missing record are not checked",
                  "dma": {"projected_held_max_s": 7.2, "budget_s": 7.5, "launches": 17,
                          "rule": "E160's: the smoke's median launch gap less E143's smoke median is the C log's extra time per launch (delta); the session "
                                  "runs only if E143's longest device-held time (s1, 6.57 s) + 17 x delta <= 7.2 s, else QUEUE-HALT"}},
    }
    p = os.path.join(HERE, "predictions-e165.json")
    json.dump(out, open(p, "w"), indent=1, sort_keys=False)
    print(f"predictions-e165.json sha256 {C.sha256_file(p)}")
    print(f"recheck: the frozen predictor with no session read reproduces M9.a2_q140l on {recheck['tiles']} tiles, {recheck['fields']} fields, "
          f"{len(recheck['differ'])} differ")
    print(f"{len(tiles)} tiles; left out by name ({len(left)}): {sorted(left)}; run {len(run_names)}; scored {len(scored)} "
          f"(the zeros anchors are inputs): {ng} governed, {npn} pinned (groups fixed by the frozen file)")
    print(f"order: {len(order)} bursts, {PASSES} passes of {per_pass}, each opening with the zeros anchors; seed {ORDER_SEED}")
    for k, v in e2e_checks.items():
        print(f"reference e2e {k}: n {v['n']} ({v['n_governed']} governed, {v['n_pinned']} pinned); reproduces loso.json to {v['worst_abs_diff']:.1e}: "
              + "; ".join(f"{q} {v['got'][q]['rms']:.3f} ({v['got'][q]['mean']:+.3f})" for q in ("G", "Bg", "Bp")))
    print(f"reference e2e pooled: governed n {eg['n']} {eg['rms_mhz']} MHz ({eg['mean_mhz']:+}) {eg['rms_w']} W ({eg['mean_w']:+}); "
          f"pinned n {ep['n']} {ep['rms_mhz']} MHz {ep['rms_w']} W ({ep['mean_w']:+}); heat {ref['heat']['n']} runs {ref['heat']['rms_c']} C")
    print("bars at the full plan (2.5%, 97.5% of the bootstrap rms):", json.dumps(bars))
    print("forecast of rank 2's lines (share of draws from the e2e reference):", json.dumps(fc))
    print("replicates:", json.dumps({k: (v["estimate_w"], v["estimate_candidates_w"]) for k, v in rep.items()}))
    top = sorted(((v["fixed_p800_w"], k) for k, v in admission.items()), reverse=True)[:6]
    print(f"admission: highest estimates {top}; limit {LIMIT_W} W, lock {PEAK_LOCK_W} W; stops {STOPS}")
    print("card time:", json.dumps(card))
    for name, t in sorted(tiles.items(), key=lambda kv: (kv[1]["left_out"], kv[1]["group"], kv[1]["type"], kv[0])):
        q = t["models"]["M9"]["a2_q140l"]
        m8, m7 = t["models"]["M8"], t["models"]["M7"]
        tag = "LEFT OUT " if t["left_out"] else ("input    " if t["zeros_anchor"] else "")
        print(f"  {tag}{t['group']:8s} p{t['priority']} {t['class']} {name:38s} M9 {q['burst_mhz']:7.2f} MHz {q['burst_board_w']:7.3f} W "
              f"rise {q['burst_die_rise_c']:5.2f} | {q['d_mhz_per_c_die_start']:+.2f} MHz/C {q['d_board_per_w_of_delta']:+.3f} W/W | "
              f"M8 {m8['burst_mhz']:6.1f}/{m8['burst_board_w']:6.2f}  M7 {m7['burst_mhz']:6.1f}/{m7['burst_board_w']:6.2f}  est {t['admission_estimate_w']:6.2f} W")


if __name__ == "__main__":
    main()
