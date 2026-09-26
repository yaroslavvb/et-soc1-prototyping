#!/usr/bin/env python3
"""V3-ABL-B reduction: the pre-registered items ABLB-2a, 2b, 2c, 3ab, 3c, 3d, 3e, 3f, 3g of PLAN3 §2 V3-ABL-B
(E2 + E3 of matmul-sparse-testdrive), exactly as registered.

    reduce.py --data <dir with one directory per card, laid out like DATA_ROOT> --out verdicts.json
              [--mmb-values mmb_int8.json] [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

Reads <data>/<card>/ablb/p<N>/ (passes whose block.json says ok) for every card directory present; writes the item
list to --out and the per-run table to <out without .json>.runs.json. Partial data (one card, fewer passes) gives
INSUFFICIENT where a card has fewer than 3 kept blocks.

Each item keeps its REGISTERED outcome from aifoundry2 and aifoundry3 (registered clock rule) and adds `all_cards`
(the busy clock rule on every card; ../abla/README.md "Four cards"): tested on every card where the item is
registered for each card (2a, 2b, 3ab, 3d, 3f, 3g), REPORTED on aifoundry1's cards where the band is given per
registered card (2c, 3c, 3e). per_card holds every card; items about energy over idle carry each card's idle clock.

Metric (registered): above-idle power = analyze_ablation.py's p80 - p_before ("dyn"; no dropout rule for this
experiment), leak and launch per card: aifoundry2 0.81 W/C at 80.9 C, aifoundry3 0.55 W/C at 55.8 C. Runs with any
mhz.minion != 600 sample are dropped. Unit = block (n = 3): per-block values, and within-block paired differences
(both runs of the pair kept in the same block); 99% t intervals with df n-1 (9.925 at n = 3).
Layer energy: above-idle power / layers per s, layers per s = sum(iters) / (t_end - t_start) from runs.jsonl.

--mmb-values: V3-MMB's pass-level mmbench int8 above-idle power per card, {"aifoundry2": [W, ...], "aifoundry3": [...],
"aifoundry1-c0": [...], ...}, for ABLB-2b's second clause ("the difference is the kernel"); without it that clause is
reported as pending.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "abla"))
import ablcore as C  # noqa: E402
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)

EXP = "ablb"
REG = [1, 2, 3]
PAR = {"aifoundry2": {"leak": 0.81, "launch": 80.9}, "aifoundry3": {"leak": 0.55, "launch": 55.8}}
ALPHA = 0.01
MIN_N = 3
A2, A3 = "aifoundry2", "aifoundry3"
CLAIMS = {
    "ABLB-2a": ["matmul-sparse-testdrive-29", "matmul-sparse-testdrive-V09"],
    "ABLB-2b": ["matmul-sparse-testdrive-13", "matmul-sparse-testdrive-15"],
    "ABLB-2c": ["matmul-sparse-testdrive-13"],
    "ABLB-3ab": ["matmul-sparse-testdrive-50", "horace-lowpower-004", "horace-lowpower-132", "hub-019"],
    "ABLB-3c": ["matmul-sparse-testdrive-98", "matmul-sparse-testdrive-101"],
    "ABLB-3d": ["matmul-sparse-testdrive-57"],
    "ABLB-3e": ["matmul-sparse-testdrive-73", "matmul-sparse-testdrive-74"],
    "ABLB-3f": ["matmul-sparse-testdrive-75"],
    "ABLB-3g": ["matmul-sparse-testdrive-99", "matmul-sparse-testdrive-100"],
}
SIX = ["fma-dense", "fma-50", "fma-rowmask", "fma-col50", "fma-875", "fma-zero"]


def par(card):
    """Reduction parameters of a card: its own for the registered cards, aifoundry2's for aifoundry1's cards."""
    return PAR[C.params_card(card)]


def v(rs, key="dyn"):
    return [r[key] for r in rs if r.get(key) is not None]


def inband(x, lo, hi):
    return None if x is None else bool(lo <= x <= hi)


def one(values, alpha=ALPHA):
    return C.one_sample(values, alpha)


def paired(runs, a, b, key="dyn"):
    blocks = C.pick_blocks(runs, [a, b], REG, key)
    d = [blk[a][key] - blk[b][key] for blk in blocks]
    ci = one(d)
    ci["passes"] = [blk[a]["pass"] for blk in blocks]
    return ci


def pos(ci):
    return None if ci.get("n", 0) < MIN_N or "lo" not in ci else bool(ci["lo"] > 0)


def item(name, test, per_card, reading, outcome=None, extra=None):
    d = {"item": name, "claims": CLAIMS[name], "per_card": per_card, "test": test, "outcome": outcome or C.combine(per_card),
         "reading": reading}
    if extra:
        d.update(extra)
    return d


def f(ci, unit="W", k=2):
    return C.fmt_ci(ci, unit, k)


def load_card(data, card):
    runs = []
    oks, skipped = C.pass_dirs(data, card, EXP)
    for p, d in oks:
        runs += C.session_runs(d, par(card)["leak"], par(card)["launch"], {"pass": p, "card": card})
    return runs, [p for p, _ in oks], skipped


def reported(fn, rs, why):
    """A card on which the item is not tested: its values against both registered cards' bands (REPORTED)."""
    out = {"outcome": "REPORTED", "why": why, "rule": "busy"}
    for pc in C.CARDS:
        res = dict(fn(rs, pc))
        res["would_be"] = res.pop("outcome", None)
        out[f"vs_{pc}_values"] = res
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mmb-values", default=None)
    ap.add_argument("--expect", default=",".join(campaign.CAMPAIGN), help="cards the all-cards outcome needs (comma list)")
    a = ap.parse_args()
    expect = [c for c in a.expect.split(",") if c]
    present = C.cards_present(a.data, EXP)
    ALL = C.card_list(a.data, EXP, expect)
    EXTRA = [c for c in ALL if c not in C.CARDS]
    R, passes, skipped = {}, {}, {}
    for c in list(C.CARDS) + EXTRA:
        R[c], passes[c], skipped[c] = load_card(a.data, c)
    RB = {c: C.busy_view(R[c]) for c in R}
    IDLE = {c: C.idle_summary(R[c]) for c in R}
    mmb = json.load(open(a.mmb_values)) if a.mmb_values and os.path.exists(a.mmb_values) else None
    items = []

    def per_card(fn):
        return {c: fn(R[c], c) for c in C.CARDS}

    def four(it, fn, kind, effect=None, why=None, note=None):
        """per_card for the other cards and all_cards (see ../abla/reduce.py four): kind "each" or "specific"."""
        pc = it["per_card"]
        for c in EXTRA:
            pc[c] = dict(fn(RB[c], C.params_card(c)), rule="busy") if kind == "each" else \
                reported(fn, RB[c], why or "the registered band is given for aifoundry2 / aifoundry3 only")
        status = {c: (fn(RB[c], c)["outcome"] if c in C.CARDS else pc[c]["outcome"]) for c in ALL}
        # a tested card whose runs idled in more than one state: the item on each state's runs alone (reported)
        by_state = {c: {s: fn(C.state_view(R[c], s), c if c in C.CARDS else C.params_card(c))["outcome"]
                        for s in C.mixed_states(IDLE.get(c))}
                    for c in (ALL if effect else []) if status.get(c) in C.TESTED and C.mixed_states(IDLE.get(c))}
        it["all_cards"] = C.all_cards_block(status, present, expect, registered={c: pc[c]["outcome"] for c in C.CARDS if c in ALL},
                                            idle=(IDLE if effect else None), idle_effect=effect, note=note, by_state=by_state)
        it["reading_all_cards"] = C.reading_all(it["all_cards"])
        return it

    # ---- 2a cycles per op (deterministic, every timed launch of every kept run)
    BANDS = {"fp16_randn_l1": (545.9, 546.1), "int8_randn_l1": (317.9, 318.1), "int8_ones_l1": (317.9, 318.1),
             "fp16_randn_tenb": (527.0, 531.0), "int8_randn_tenb": (265.0, 300.0), "int8_ones_tenb": (265.0, 300.0)}

    def c2a(rs, pc):
        per, bad, ok_all = {}, [], True
        for cfg, (lo, hi) in BANDS.items():
            x = [r for r in rs if r["config"] == cfg and r["kept"]]
            cyc = [y for r in x for y in r.get("cycles_timed", [])]
            out = [y for y in cyc if not lo <= y <= hi]
            per[cfg] = {"runs": len(x), "launches": len(cyc), "min": min(cyc) if cyc else None, "max": max(cyc) if cyc else None,
                        "mean": float(np.mean(cyc)) if cyc else None, "band": [lo, hi], "outside": len(out),
                        "calibration": sorted({round(y, 3) for r in x for y in r.get("cycles_calib", [])})}
            if len(x) < MIN_N:
                ok_all = None if ok_all is not False else False
            if out:
                ok_all = False
                bad.append(cfg)
        return {"outcome": "INSUFFICIENT" if ok_all is None else ("PASS" if ok_all else "FAIL"), "configs": C.rnd(per, 4), "outside": bad,
                "_means": {cfg: per[cfg]["mean"] for cfg in BANDS}}
    pc = per_card(c2a)
    means = {}
    for c in C.CARDS:
        m = pc[c].pop("_means")
        for cfg in BANDS:
            means[(c, cfg)] = m[cfg]
    oc = C.combine(pc)
    cross = {}
    for cfg in BANDS:
        m2, m3 = means.get((A2, cfg)), means.get((A3, cfg))
        cross[cfg] = C.rnd(abs(m2 - m3), 4) if m2 is not None and m3 is not None else None
    tenb_int8 = [cross[k] for k in ("int8_randn_tenb", "int8_ones_tenb")]
    if oc == "PASS" and any(x is None or x > 0.5 for x in tenb_int8):
        oc = "CARD-DIFFERENT"
    it = item("ABLB-2a", "deterministic: every timed launch (launch >= 0) of every kept run inside its band: L1 fp16 546.0 "
              "+-0.1, L1 int8 318.0 +-0.1, TenB fp16 529 +-2, TenB int8 265-300; and TenB int8 (A resident) identical on "
              "the two cards within 0.5 cycle (card means)", pc,
              "cycles/op: " + "; ".join(f"{C.SHORT[c]} " + ", ".join(f"{k} {vv['mean']:.2f}" for k, vv in pc[c]['configs'].items()
                                                                     if vv['mean'] is not None) + f" -> {pc[c]['outcome']}" for c in C.CARDS)
              + f"; cross-card |diff| TenB int8 {tenb_int8}", outcome=oc, extra={"cross_card_abs_diff": cross})
    # all cards: the bands on every card, and TenB int8 identical on all cards within 0.5 cycle (spread of card means)
    for c in EXTRA:
        res = c2a(RB[c], C.params_card(c))
        res.pop("_means")
        pc[c] = dict(res, rule="busy")
    stat, bm = {}, {}
    for c in ALL:
        res = c2a(RB[c], c)
        bm[c] = res.pop("_means")
        stat[c] = res["outcome"]
    spread = {}
    for k in ("int8_randn_tenb", "int8_ones_tenb"):
        ms = [bm[c][k] for c in ALL if bm[c][k] is not None]
        spread[k] = C.rnd(max(ms) - min(ms), 4) if len(ms) == len(ALL) else None
    ac = C.all_cards_block(stat, present, expect, registered={c: pc[c]["outcome"] for c in C.CARDS if c in ALL})
    if ac["outcome"] == "PASS" and any(x is None or x > 0.5 for x in spread.values()):
        ac["outcome"] = "CARD-DIFFERENT"
    ac["tenb_int8_spread_of_card_means"] = spread
    ac["card_means"] = {c: C.rnd(bm[c], 4) for c in ALL}
    it["all_cards"] = ac
    it["reading_all_cards"] = C.reading_all(ac) + f"; TenB int8 spread over cards {spread}"
    items.append(it)

    # ---- 2b TenB - L1 paired, and the kernel clause
    def c2b(rs, pc):
        rnd_ci, ones_ci = paired(rs, "int8_randn_tenb", "int8_randn_l1"), paired(rs, "int8_ones_tenb", "int8_ones_l1")
        fp16_ci = paired(rs, "fp16_randn_tenb", "fp16_randn_l1")
        ok = [pos(rnd_ci), pos(ones_ci)]
        return {"outcome": C.card_outcome(ok), "int8_randn_tenb_minus_l1": C.rnd(rnd_ci), "int8_ones_tenb_minus_l1": C.rnd(ones_ci),
                "fp16_randn_tenb_minus_l1 (reported)": C.rnd(fp16_ci),
                "in_pred_band": {"randn +4..+10": inband(rnd_ci.get("mean"), 4, 10), "ones +3..+8": inband(ones_ci.get("mean"), 3, 8)}}
    pc = per_card(c2b)
    oc = C.combine(pc)

    def kernel_clause(runs_by_card, cards, streaming_ok):
        if not mmb:
            return {"status": "pending V3-MMB (pass --mmb-values)"}
        kk = {}
        for c in cards:
            l1 = v(C.pick(runs_by_card[c], "int8_randn_l1", REG))
            m = mmb.get(c, [])
            w = C.welch(m, l1, 2 * 0.01)  # two-sided 98% -> its lower end is the one-sided 99% bound
            kk[c] = {"welch": C.rnd(w), "exceeds_by_10W": (bool(w["lo"] > 10.0) if "lo" in w and len(m) >= MIN_N and len(l1) >= MIN_N else None)}
        allk = [kk[c]["exceeds_by_10W"] for c in cards]
        return {"per_card": kk, "status": "insufficient" if None in allk else
                ("'the difference is the kernel' kept" if all(allk) and streaming_ok else "'probably the kernel'")}
    kernel = kernel_clause(R, C.CARDS, oc == "PASS")
    it = item("ABLB-2b", "within-block paired TenB - L1 above-idle power (n = 3 blocks), 99% t (df 2) excludes 0 with positive "
              "sign for int8 randn and int8 ones on both cards -> 'streaming B through TenB costs X W' per card; "
              "'the difference is the kernel' kept only if also V3-MMB's mmbench int8 above-idle exceeds this "
              "session's int8_randn_l1 by > 10 W on each card (Welch, one-sided alpha 0.01)", pc,
              "TenB - L1: " + "; ".join(f"{C.SHORT[c]} randn {f(pc[c]['int8_randn_tenb_minus_l1'])}, ones {f(pc[c]['int8_ones_tenb_minus_l1'])} -> {pc[c]['outcome']}"
                                        for c in C.CARDS) + f"; kernel clause: {kernel['status']}", outcome=oc, extra={"kernel_clause": kernel})
    four(it, c2b, "each", "difference")
    it["all_cards"]["kernel_clause"] = kernel_clause(RB, ALL, it["all_cards"]["outcome"] == "PASS")
    items.append(it)

    # ---- 2c int8_randn_l1 above idle: a2 9.5-10.5 W; a3 0.92 x a2 mean +- 1 W (the band needs aifoundry2's mean,
    # taken under the same clock rule as the card judged)
    def make_2c(a2_runs):
        c2 = one(v(C.pick(a2_runs, "int8_randn_l1", REG)))
        bands = {A2: (9.5, 10.5), A3: ((0.92 * c2["mean"] - 1.0, 0.92 * c2["mean"] + 1.0) if "mean" in c2 else None)}

        def c2c(rs, pc):
            ci = one(v(C.pick(rs, "int8_randn_l1", REG)))
            b = bands[pc]
            ok = None if ci.get("n", 0) < MIN_N or "lo" not in ci or b is None or (pc == A3 and c2.get("n", 0) < MIN_N) else \
                bool(C.difference_ok(ci | {"point": ci["mean"]}, band=b))
            return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "ci": C.rnd(ci), "band": C.rnd(b)}
        return c2c
    c2c_reg, c2c_busy = make_2c(R[A2]), make_2c(RB[A2])
    pc = per_card(c2c_reg)
    it = item("ABLB-2c", "per-block int8_randn_l1 above idle, 99% t (df 2): excludes 0 and the mean inside a2 9.5-10.5 W, "
              "a3 0.92 x a2 +- 1 W", pc,
              "int8 randn in L1: " + "; ".join(f"{C.SHORT[c]} {f(pc[c]['ci'])} band {pc[c]['band']} -> {pc[c]['outcome']}" for c in C.CARDS))
    for c in EXTRA:
        pc[c] = reported(c2c_busy, RB[c], "the band is given for aifoundry2 (9.5-10.5 W) and aifoundry3 (0.92 x aifoundry2) only")
    st = {c: (c2c_busy(RB[c], c)["outcome"] if c in C.CARDS else "REPORTED") for c in ALL}
    it["all_cards"] = C.all_cards_block(st, present, expect, registered={c: pc[c]["outcome"] for c in C.CARDS if c in ALL},
                                        idle=IDLE, idle_effect="absolute")
    it["reading_all_cards"] = C.reading_all(it["all_cards"])
    items.append(it)

    # ---- 3ab dense vs zero, saving
    PD = {A2: (18.8, 2.5, 2.6, 0.8), A3: (17.3, 2.0, 2.4, 0.7)}

    def c3ab(rs, pc):
        blocks = C.pick_blocks(rs, ["fma-dense", "fma-zero"], REG)
        sav = [1 - b["fma-zero"]["dyn"] / b["fma-dense"]["dyn"] for b in blocks if b["fma-dense"]["dyn"]]
        ci = one(sav)
        dense, zero = one(v(C.pick(rs, "fma-dense", REG))), one(v(C.pick(rs, "fma-zero", REG)))
        ok = None if len(sav) < MIN_N else bool(ci["lo"] >= 0.80 and ci["hi"] <= 0.92)
        p = PD[pc]
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "saving": C.rnd(ci), "dense_W": C.rnd(dense),
                "zero_W": C.rnd(zero), "in_pred_band": {"dense": inband(dense.get("mean"), p[0] - p[1], p[0] + p[1]),
                                                        "zero": inband(zero.get("mean"), p[2] - p[3], p[2] + p[3]),
                                                        "saving 0.86+-0.04": inband(ci.get("mean"), 0.82, 0.90)}}
    pc = per_card(c3ab)
    items.append(four(item("ABLB-3ab", "per-block saving 1 - zero/dense (n = 3), 99% t (df 2) inside 0.80-0.92 on both cards -> PROVEN-BOTH, "
                           "watts per card", pc,
                           "power saved dense -> zero: " + "; ".join(f"{C.SHORT[c]} {f(pc[c]['saving'], '', 3)} (dense {pc[c]['dense_W'].get('mean')} W, "
                                                                     f"zero {pc[c]['zero_W'].get('mean')} W) -> {pc[c]['outcome']}" for c in C.CARDS)),
                      c3ab, "each", "absolute", note="aifoundry1's cards: in_pred_band is against aifoundry2's watt predictions (informational)"))

    # ---- 3c six-point line
    PS = {A2: (16.1, 2.5), A3: (14.8, 2.0)}

    def c3c(rs, pc):
        blocks = C.pick_blocks(rs, SIX, REG)

        def frac(r):
            return r["nnz_a"] / r["a_elems"] * bin(int(r["row_mask"], 16)).count("1") / 16.0
        fits = [C.linfit([frac(b[k]) for k in SIX], [b[k]["dyn"] for k in SIX], ALPHA) for b in blocks]
        slopes = one([ft["slope"] for ft in fits if "slope" in ft])
        mean_fit = C.linfit([float(np.mean([frac(b[k]) for b in blocks])) for k in SIX],
                            [float(np.mean([b[k]["dyn"] for b in blocks])) for k in SIX], ALPHA) if blocks else {}
        ok = None if len(blocks) < MIN_N else bool(C.difference_ok(slopes | {"point": slopes["mean"]}, PS[pc][0], PS[pc][1]) and mean_fit["rms"] <= 0.6)
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "slope": C.rnd(slopes),
                "fit_on_block_means": C.rnd(mean_fit), "per_block_rms": C.rnd([ft.get("rms") for ft in fits]),
                "x_mean": {k: C.rnd(float(np.mean([frac(b[k]) for b in blocks]))) for k in SIX} if blocks else {}}
    pc = per_card(c3c)
    items.append(four(item("ABLB-3c", "per block, least-squares line of above-idle power on the useful-slot fraction (nnz_a / a_elems x "
                           "rows on / 16) through the six fma points; 99% t (df 2) of the per-block slopes excludes 0 with the mean in "
                           "a2 16.1 +- 2.5, a3 14.8 +- 2.0 W; rms residual of the line through the block-mean points <= 0.6 W", pc,
                           "power vs nonzero fraction: " + "; ".join(f"{C.SHORT[c]} slope {f(pc[c]['slope'])}, rms {pc[c]['fit_on_block_means'].get('rms')} W -> {pc[c]['outcome']}"
                                                                     for c in C.CARDS)),
                      c3c, "specific", "difference", why="the slope band is given for aifoundry2 / aifoundry3 only"))

    # ---- 3d row mask vs zeros
    def c3d(rs, pc):
        blocks = C.pick_blocks(rs, ["fma-dense", "fma-rowmask", "fma-50"], REG)
        rat = [(b["fma-dense"]["dyn"] - b["fma-rowmask"]["dyn"]) / (b["fma-dense"]["dyn"] - b["fma-50"]["dyn"]) for b in blocks
               if b["fma-dense"]["dyn"] != b["fma-50"]["dyn"]]
        ci = one(rat)
        ok = None if len(rat) < MIN_N else bool(ci["lo"] >= 0.7 and ci["hi"] <= 1.5)
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "ratio": C.rnd(ci),
                "in_pred_band_0.9_1.4": inband(ci.get("mean"), 0.9, 1.4),
                "dense_minus_rowmask_W": C.rnd(paired(rs, "fma-dense", "fma-rowmask")),
                "dense_minus_50_W": C.rnd(paired(rs, "fma-dense", "fma-50"))}
    pc = per_card(c3d)
    items.append(four(item("ABLB-3d", "per-block ratio (dense - rowmask) / (dense - fma-50), 99% t (df 2) inside 0.7-1.5 on both cards -> "
                           "keep 'cuts power like zeros do'; otherwise both cuts per card", pc,
                           "row mask vs half zeros: " + "; ".join(f"{C.SHORT[c]} {f(pc[c]['ratio'], '', 2)} -> {pc[c]['outcome']}" for c in C.CARDS)),
                      c3d, "each", "difference"))

    # ---- 3e layer energy (above idle, and board incl. idle, per card with its temperature)
    PL = {"gemv-skip-0": (70, 10), "gemv-skip-90": (19, 5), "gemv-skip-99": (7, 3)}

    def c3e_card(rs):
        cfgs, m = {}, {}
        for k in list(PL) + ["gemv-dense-90", "gemv-dense-0"]:
            x = C.pick(rs, k, REG, "dyn")
            above = one([r["dyn"] / r["per_s"] * 1e6 for r in x if r.get("per_s")])
            board = one([r["p80"] / r["per_s"] * 1e6 for r in x if r.get("per_s")])
            us = one([1e6 / r["per_s"] for r in x if r.get("per_s")])
            cfgs[k] = {"uJ_above_idle": C.rnd(above), "uJ_board_incl_idle": C.rnd(board), "us_per_layer": C.rnd(us)}
            m[k] = above.get("mean") if above.get("n", 0) >= MIN_N else None
        te = [r["t_early"] for r in rs if r["kept"] and str(r["config"]).startswith("gemv") and r.get("t_early") is not None]
        return {"configs": cfgs, "die_c_at_launch_window": C.rnd(float(np.mean(te))) if te else None}, m

    def c3e_joint(m3, m2):
        checks = {}
        for k, (mm, tol) in PL.items():
            a3m, a2m = m3.get(k), m2.get(k)
            checks[k] = {"a3_in_band": inband(a3m, mm - tol, mm + tol), "a2_over_a3": C.rnd(a2m / a3m) if a2m and a3m else None,
                         "ratio_in_1.08+-0.15": inband(a2m / a3m if a2m and a3m else None, 0.93, 1.23)}
        flags = [x for ch in checks.values() for x in (ch["a3_in_band"], ch["ratio_in_1.08+-0.15"])]
        return checks, ("INSUFFICIENT" if None in flags else ("PASS" if all(flags) else "FAIL"))
    pc, means = {}, {}
    for c in C.CARDS:
        pc[c], means[c] = c3e_card(R[c])
    checks, oc = c3e_joint(means[A3], means[A2])
    for c in C.CARDS:
        pc[c]["outcome"] = oc
    it = item("ABLB-3e", "stated per card: above-idle energy per layer (per-block values, 99% t) for gemv-skip-0/90/99 against "
              "a3 70+-10, 19+-5, 7+-3 uJ and a2 = a3 x 1.08+-0.15; board energy including idle stated per card with its die "
              "temperature; no CARD-DIFFERENT is drawn from it (PASS = every band met, FAIL otherwise)", pc,
              "uJ per layer above idle: " + "; ".join(f"{C.SHORT[c]} " + ", ".join(f"{k[5:]} {pc[c]['configs'][k]['uJ_above_idle'].get('mean')}" for k in PL)
                                                      + f" at {pc[c]['die_c_at_launch_window']} C" for c in C.CARDS) + f" -> {oc}",
              outcome=oc, extra={"band_checks": checks})
    # all cards: the registered joint check under the busy rule; the other cards are stated (REPORTED) with their
    # ratio to aifoundry3, as aifoundry2 is registered
    bvals, bmeans = {}, {}
    for c in ALL:
        bvals[c], bmeans[c] = c3e_card(RB[c])
    for c in EXTRA:
        pc[c] = dict(bvals[c], outcome="REPORTED", rule="busy",
                     why="the bands are given for aifoundry3 (and aifoundry2 = aifoundry3 x 1.08) only; stated per card",
                     over_aifoundry3={k: (C.rnd(bmeans[c][k] / bmeans[A3][k]) if bmeans[c].get(k) and bmeans.get(A3, {}).get(k) else None)
                                      for k in PL})
    _, boc = c3e_joint(bmeans.get(A3, {}), bmeans.get(A2, {}))
    st = {c: (boc if c in C.CARDS else "REPORTED") for c in ALL}
    ac = C.all_cards_block(st, present, expect, registered={c: oc for c in C.CARDS if c in ALL}, idle=IDLE, idle_effect="absolute",
                           note="a joint check over aifoundry2 and aifoundry3 as registered (never CARD-DIFFERENT); aifoundry1's cards are stated")
    it["all_cards"] = ac
    it["reading_all_cards"] = C.reading_all(ac)
    items.append(it)

    # ---- 3f gating alone
    def c3f(rs, pc):
        g = paired(rs, "gemv-dense-0", "gemv-dense-90")
        s_ = paired(rs, "gemv-skip-0", "gemv-dense-90")
        ok = pos(g)
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "dense0_minus_dense90": C.rnd(g),
                "skip0_minus_dense90": C.rnd(s_), "in_pred_band": {"dense0-dense90 +0.3..+1.5": inband(g.get("mean"), 0.3, 1.5),
                                                                   "skip0-dense90 1.1+-0.6": inband(s_.get("mean"), 0.5, 1.7)},
                "gating_pct_of_dense0": C.rnd(100 * g["mean"] / float(np.mean(v(C.pick(rs, "gemv-dense-0", REG)))))
                if "mean" in g and v(C.pick(rs, "gemv-dense-0", REG)) else None}
    pc = per_card(c3f)
    items.append(four(item("ABLB-3f", "within-block paired gemv-dense-0 - gemv-dense-90 (same kernel: the gating alone), 99% t (df 2) "
                           "excludes 0 (positive) on both cards -> a 'gating alone' percentage is kept; skip-0 - dense-90 reported", pc,
                           "gating alone: " + "; ".join(f"{C.SHORT[c]} {f(pc[c]['dense0_minus_dense90'])} -> {pc[c]['outcome']}" for c in C.CARDS)),
                      c3f, "each", "difference"))

    # ---- 3g tensor unit with zeros vs the integer loop
    SP = {A2: (1.3, 1.7), A3: (1.4, 2.1)}

    def c3g(rs, pc):
        d = paired(rs, "fma-zero", "spin")
        sp = one(v(C.pick(rs, "spin", REG)))
        ok = pos(d)
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"), "zero_minus_spin": C.rnd(d), "spin_W": C.rnd(sp),
                "in_pred_band": {"spin": inband(sp.get("mean"), *SP[pc]), "zero-spin +0.3..+0.9": inband(d.get("mean"), 0.3, 0.9)}}
    pc = per_card(c3g)
    items.append(four(item("ABLB-3g", "within-block paired fma-zero - spin, 99% t (df 2) excludes 0 on both cards -> keep 'about 0.5 W'; "
                           "else 'under 1 W, not separated from the spin baseline'", pc,
                           "tensor unit on zeros over the integer loop: " + "; ".join(f"{C.SHORT[c]} {f(pc[c]['zero_minus_spin'])} (spin {pc[c]['spin_W'].get('mean')} W) -> {pc[c]['outcome']}"
                                                                                     for c in C.CARDS)),
                      c3g, "each", "difference", note="aifoundry1's cards: the spin in_pred_band is against aifoundry2's band (informational)"))

    json.dump(C.jsonable(items), open(a.out, "w"), indent=1)
    diag = {"exp": EXP, "data": os.path.abspath(a.data), "registered_passes": REG, "passes_used": passes, "passes_skipped": skipped,
            "alpha": ALPHA, "params": PAR, "params_by_card": {c: par(c) for c in R}, "cards_present": present, "cards_all": ALL,
            "idle_by_card": IDLE,
            "runs": {c: [{k: C.rnd(x) for k, x in r.items() if k not in ("cycles_timed", "cycles_calib")} for r in R[c]] for c in R}}
    json.dump(C.jsonable(diag), open(os.path.splitext(a.out)[0] + ".runs.json", "w"), indent=1)
    for it in items:
        print(f"{it['item']:9s} {it['outcome']:14s} {it['reading'][:230]}")
        print(f"{'':9s} {it['all_cards']['outcome']:14s} {it['reading_all_cards'][:230]}")


if __name__ == "__main__":
    main()
