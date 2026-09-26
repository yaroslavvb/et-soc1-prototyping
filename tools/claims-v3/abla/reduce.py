#!/usr/bin/env python3
"""V3-ABL-A reduction: the pre-registered items ABL-T1..T8 (+ the T5 EM4 rider), ABL-R, ABL-EM4c and ABL-EM4d of
PLAN3 §2 V3-ABL-A, exactly as registered (plan3.json and x1_predictions.json, whose sha256 is checked).

    reduce.py --data <dir with one directory per card, laid out like DATA_ROOT> --out verdicts.json
              [--expect aifoundry2,aifoundry3,aifoundry1-c0,aifoundry1-c1]

Reads <data>/<card>/abla/p<N>/ (passes whose block.json says ok) for every card directory present. Writes the list of
items to --out and the per-run table (kept / dropped and why, every metric) to <out without .json>.runs.json. Works
on partial data (one card, fewer passes): items without 3 kept repeats on a card say INSUFFICIENT.

Each item keeps its REGISTERED outcome, computed as registered from aifoundry2 and aifoundry3 only (registered clock
rule), and adds `all_cards` (README "Four cards"): the busy clock rule on every card of --expect and any other card
with data; per card PASS / FAIL / INSUFFICIENT where the item is registered for each card, REPORTED where its band
is given for aifoundry2 or aifoundry3 only (the card's result is then shown against both cards' values, not tested);
outcome PASS on every tested card, FAIL on every one, CARD-DIFFERENT on some, INSUFFICIENT when a card lacks the kept
repeats or has no data. per_card holds every card: aifoundry2 / aifoundry3 as registered, the others under the busy
rule with aifoundry2's reduction parameters. Items about energy over idle carry each card's idle clock.

Metric (registered, x1 test): switching = p_early' - leak x (t_early - launch) - p_before, p_early' the mean board
power over seconds 1-3 after dropping samples > 2 W below the window median (count reported); leak and launch per
card: aifoundry2 0.81 W/C at 80.9 C, aifoundry3 0.55 W/C at 55.8 C. Unit = one run; runs with any mhz.minion != 600
sample are dropped. Family: the 19 sub-tests of T1-T8 per card, Bonferroni two-sided alpha 0.01/19. Difference
sub-test: the corrected interval excludes 0 with the predicted sign AND the point estimate is inside the tolerance
AND (robustness) the page's p_early metric (dyn) and the run average p_mean - p_before give the same sign.
Equivalence sub-test (T1 vs ones, T4 non-DFT): the corrected interval lies inside +-1.0 W.
"""
import argparse
import hashlib
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ablcore as C  # noqa: E402

EXP = "abla"
REG = [1, 2, 3, 4]                      # registered passes (blocks 0-3)
PAR = {"aifoundry2": {"leak": 0.81, "launch": 80.9}, "aifoundry3": {"leak": 0.55, "launch": 55.8}}
FAMILY = 19
ALPHA = 0.01 / FAMILY                   # t 6.72 at df 6 (Welch, 4 v 4), 16.0 at df 3 (one sample of 4)
MIN_N = 3
PRED_SHA = "9533af32f46eaceeeaae87b5cd91759ff8836ffa9fab686ca35b089ec05c7ec0"
LEGACY_A2 = os.path.join(C.ROOT, "docs/reports/data/2026-09-21-horace-aifoundry2/ablation")
TOGGLES = os.path.join(C.ROOT, "docs/reports/data/2026-09-21-horace-aifoundry2/toggles_all.json")
A2, A3 = "aifoundry2", "aifoundry3"

CLAIMS = {
    "ABL-T1": ["horace-lowpower-107"],
    "ABL-T2": ["horace-lowpower-026", "horace-lowpower-045", "horace-lowpower-049"],
    "ABL-T3": ["horace-lowpower-017", "horace-lowpower-024", "horace-lowpower-025", "horace-lowpower-046", "horace-lowpower-V02"],
    "ABL-T4": ["horace-lowpower-012", "horace-lowpower-102", "horace-lowpower-103", "horace-lowpower-104", "horace-lowpower-105",
               "horace-lowpower-106", "horace-lowpower-108"],
    "ABL-T5": ["horace-lowpower-143", "horace-lowpower-163", "horace-lowpower-166", "horace-lowpower-180", "horace-lowpower-138",
               "horace-lowpower-145", "energy-manual-53", "energy-manual-54", "energy-manual-56", "energy-manual-57", "ridge-83"],
    "ABL-T6": ["horace-lowpower-136", "horace-lowpower-161", "horace-lowpower-167", "horace-lowpower-176", "horace-lowpower-170",
               "energy-manual-25", "dvfs-58"],
    "ABL-T7": ["horace-lowpower-175", "horace-lowpower-155", "horace-lowpower-171", "dvfs-69", "energy-manual-29"],
    "ABL-T8": ["horace-lowpower-006", "horace-lowpower-061", "horace-lowpower-121", "horace-lowpower-125", "energy-manual-51",
               "energy-manual-52", "hub-010", "hub-011"],
    "ABL-R": ["horace-lowpower-040", "horace-lowpower-041", "horace-lowpower-043", "horace-lowpower-056", "horace-lowpower-199",
              "horace-lowpower-030", "horace-lowpower-090", "energy-manual-V01"],
    "ABL-EM4c": ["energy-manual-55"],
    "ABL-EM4d": ["horace-lowpower-128"],
}
EM4_PATTERNS = ["fp16_zeros", "fp16_ones", "fp16_randn", "int8_zeros", "int8_ones", "int8_randn"]
TENSOR9 = ["fp32_zeros", "fp32_ones", "fp32_randn"] + EM4_PATTERNS
FLIP_ROWS = {"fp32_zeros": "zeros", "fp32_ones": "ones", "fp32_randn": "randn", "fp32_signs": "signs", "fp32_pow2": "pow2",
             "fp32_mant": "mant", "fp32_arb1": "a_randn_b_ones", "fp32_a1br": "a_ones_b_randn", "m_negzero": "negzero",
             "m_fft_cos": "fft_cos", "m_butterfly": "butterfly", "m_hadamard": "hadamard", "m_relu": "relu",
             "m_kaleidoscope": "kaleidoscope"}
MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")          # tools/ettelem/analyze_horace_strict.py
F_OP = 600e6 / 546.0                                             # TensorFMA32 ops per second per minion


def par(card):
    """Reduction parameters of a card: its own for the registered cards, aifoundry2's for aifoundry1's cards."""
    return PAR[C.params_card(card)]


def vals(rs, key="switching", per=None):
    out = []
    for r in rs:
        v = r.get(key)
        if v is None:
            continue
        if per:
            if not r.get(per):
                continue
            v = v / r[per] * 1e12
        out.append(v)
    return out


def enough(*groups):
    return all(len(g) >= MIN_N for g in groups)


def robust_same_sign(point, alts):
    return all(a is not None and np.sign(a) == np.sign(point) for a in alts)


def sub_welch(runs, a, b, kind, pred=None, tol=None, band=None, label=None):
    """Welch sub-test of switching(a) - switching(b)."""
    ra, rb = C.pick(runs, a, REG), C.pick(runs, b, REG)
    ci = C.welch(vals(ra), vals(rb), ALPHA)
    st = {"test": label or f"{a} - {b}", "kind": kind, "pred": pred, "tol": tol, "band": band, "ci": C.rnd(ci),
          "passes_used": {a: [r["pass"] for r in ra], b: [r["pass"] for r in rb]}}
    if not enough(ra, rb):
        st["ok"] = None
        return st
    if kind == "equivalence":
        st["ok"] = C.equivalence_ok(ci, tol)
    else:
        alts = [np.mean(vals(ra, k)) - np.mean(vals(rb, k)) for k in ("dyn", "mean_dyn")]
        st["robust"] = {"dyn": C.rnd(float(alts[0])), "mean_dyn": C.rnd(float(alts[1])), "same_sign": robust_same_sign(ci["point"], alts)}
        st["ok"] = bool(C.difference_ok(ci, pred, tol, band) and st["robust"]["same_sign"])
    return st


def sub_one(runs, cfg, kind, mu=0.0, pred=None, tol=None, band=None, per=None, label=None):
    """One-sample sub-test of switching(cfg) (or switching / per_s in pJ) against the constant mu."""
    rs = C.pick(runs, cfg, REG)
    ci = C.one_sample(vals(rs, per=per), ALPHA, mu)
    st = {"test": label or cfg, "kind": kind, "mu": mu, "pred": pred, "tol": tol, "band": band, "ci": C.rnd(ci),
          "passes_used": [r["pass"] for r in rs]}
    if not enough(rs):
        st["ok"] = None
        return st
    if kind == "equivalence":
        st["ok"] = C.equivalence_ok(ci, tol)
    else:
        alts = [float(np.mean(vals(rs, k, per))) - mu for k in ("dyn", "mean_dyn")]
        st["robust"] = {"dyn": C.rnd(alts[0]), "mean_dyn": C.rnd(alts[1]), "same_sign": robust_same_sign(ci["point"], alts)}
        st["ok"] = bool(C.difference_ok(ci, pred, tol, band) and st["robust"]["same_sign"])
    return st


def per_card_result(subs):
    oc = C.card_outcome([s["ok"] for s in subs])
    return {"outcome": oc, "n_subtests": len(subs), "subtests": subs}


def item(name, test, per_card, reading, outcome=None, extra=None):
    d = {"item": name, "claims": CLAIMS.get(name, []), "per_card": per_card, "test": test,
         "outcome": outcome or C.combine(per_card), "reading": reading}
    if extra:
        d.update(extra)
    return d


def short(per_card, fmt):
    return "; ".join(f"{C.SHORT[c]} {fmt(c, per_card[c])}" for c in C.CARDS if c in per_card)


def reported(fn, rs, why):
    """A card on which the item is not tested: its values against both registered cards' bands (REPORTED)."""
    out = {"outcome": "REPORTED", "why": why, "rule": "busy"}
    for pc in C.CARDS:
        v = dict(fn(rs, pc))
        v["would_be"] = v.pop("outcome", None)
        out[f"vs_{pc}_values"] = v
    return out


def sub_str(s):
    return f"{s['test']} {C.fmt_ci(s['ci'])}{'' if s['ok'] else (' (n<3)' if s['ok'] is None else ' x')}"


# --------------------------------------------------------------------------------------- the flip-model refit
def nnls(X, y, free=1):
    """Least squares with non-negative coefficients (first `free` columns unconstrained), by subset search
    (tools/ettelem/analyze_horace_strict.py)."""
    n = X.shape[1]
    best = None
    for k in range(n - free + 1):
        for sub in itertools.combinations(range(free, n), k):
            cols = list(range(free)) + list(sub)
            c = np.linalg.lstsq(X[:, cols], y, rcond=None)[0]
            if (c[free:] < 0).any():
                continue
            full = np.zeros(n); full[cols] = c
            err = float(np.sum((X @ full - y) ** 2))
            if best is None or err < best[0] - 1e-12:
                best = (err, full)
    return best[1]


def flip_features():
    tog = json.load(open(TOGGLES))
    out = {}
    for cfg, k in FLIP_ROWS.items():
        m = tog[k]["mean"]
        mult = sum(v for b, v in m["by_block"].items() if any(s in b for s in MULT_BLOCKS))
        out[cfg] = [m["ff_clocked"] / 1e6, mult / 1e6, (m["nets"] - mult) / 1e6, m["bus"] / 1e6]
    return out


def refit(runs, key):
    feats = flip_features()
    rows = []
    for cfg in FLIP_ROWS:
        v = vals(C.pick(runs, cfg, REG), key)
        if len(v) >= MIN_N:
            rows.append((cfg, float(np.mean(v)), feats[cfg]))
    if len(rows) < len(FLIP_ROWS):
        return {"patterns": len(rows), "needed": len(FLIP_ROWS)}
    X = np.array([[1.0] + f for _, _, f in rows]); y = np.array([m for _, m, _ in rows])
    c = nnls(X, y)
    loo = []
    for i in range(len(rows)):
        keep = [j for j in range(len(rows)) if j != i]
        loo.append(float(X[i] @ nnls(X[keep], y[keep])))
    fj = 1e15 / (1e6 * F_OP * 1024)  # W per (million events per op) -> fJ per event on 1,024 minions
    return {"patterns": len(rows), "metric": key, "coef_W": C.rnd(list(map(float, c)), 4),
            "fJ_per_event": dict(zip(["ffclk", "mult", "rest", "bus"], C.rnd([float(x) * fj for x in c[1:]], 3))),
            "constant_W": C.rnd(float(c[0])), "rms": C.rnd(float(np.sqrt(np.mean((X @ c - y) ** 2)))),
            "loo_rms": C.rnd(float(np.sqrt(np.mean((np.array(loo) - y) ** 2)))),
            "loo": {cfg: C.rnd(p - m) for (cfg, m, _), p in zip(rows, loo)}}


# --------------------------------------------------------------------------------------------------- main
def load_card(data, card):
    runs = []
    oks, skipped = C.pass_dirs(data, card, EXP)
    for p, d in oks:
        runs += C.session_runs(d, par(card)["leak"], par(card)["launch"], {"pass": p, "card": card})
    return runs, [p for p, _ in oks], skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--legacy-a2", default=LEGACY_A2, help="the 21 Sep aifoundry2 ablation session (ABL-EM4d)")
    ap.add_argument("--expect", default=",".join(C.CAMPAIGN), help="cards the all-cards outcome needs (comma list)")
    a = ap.parse_args()
    pred_path = os.path.join(HERE, "x1_predictions.json")
    X1 = json.load(open(pred_path))["pred"]
    pred_sha = hashlib.sha256(open(pred_path, "rb").read()).hexdigest()
    if pred_sha != PRED_SHA:
        print(f"WARNING: x1_predictions.json sha256 {pred_sha} differs from the registered {PRED_SHA}", file=sys.stderr)

    expect = [c for c in a.expect.split(",") if c]
    present = C.cards_present(a.data, EXP)
    ALL = C.card_list(a.data, EXP, expect)             # the cards of the all-cards outcome
    EXTRA = [c for c in ALL if c not in C.CARDS]        # cards beyond the registered two (aifoundry1's)
    R, passes, skipped = {}, {}, {}
    for card in list(C.CARDS) + EXTRA:
        R[card], passes[card], skipped[card] = load_card(a.data, card)
    RB = {c: C.busy_view(R[c]) for c in R}              # the four-card busy clock rule
    IDLE = {c: C.idle_summary(R[c]) for c in R}
    have = [c for c in R if R[c]]
    items = []

    def per_card(fn):
        """registered per_card (aifoundry2 / aifoundry3, registered rule, their own parameters), as registered"""
        return {c: fn(R[c], c) for c in C.CARDS}

    def four(it, fn, kind, effect=None, why=None, extra_fn=None, note=None):
        """Adds the other cards to per_card and the all_cards block. kind: "each" (registered for each card: tested
        on every card), "specific" (bands given per registered card: REPORTED elsewhere), "a3" / "a2" (decided on
        that card only: REPORTED on the others). fn(rs, param_card) -> per-card result with "outcome"."""
        pc = it["per_card"]
        for c in EXTRA:
            if kind == "each":
                pc[c] = dict(extra_fn(RB[c], C.params_card(c)) if extra_fn else fn(RB[c], C.params_card(c)), rule="busy")
            elif kind in ("a2", "a3"):         # decided on one card: the values stated once, the outcome reported
                v = dict(fn(RB[c], C.params_card(c)), rule="busy", why=why)
                v["would_be"] = v.pop("outcome", None)
                pc[c] = dict({"outcome": "REPORTED"}, **v)
            else:
                pc[c] = reported(fn, RB[c], why or "the registered value is given for aifoundry2 / aifoundry3 only")
        status, reg = {}, {}
        for c in ALL:
            if c in C.CARDS:
                if kind in ("a2", "a3") and c != {"a2": A2, "a3": A3}[kind]:
                    status[c] = "REPORTED"
                else:
                    status[c] = fn(RB[c], c)["outcome"]
                    reg[c] = pc[c]["outcome"]
            else:
                status[c] = pc[c]["outcome"]
        # a tested card whose runs idled in more than one state: the item on each state's runs alone (reported)
        by_state = {}
        for c in (ALL if effect else []):
            if status.get(c) in C.TESTED and C.mixed_states(IDLE.get(c)):
                f_ = extra_fn if (extra_fn and c not in C.CARDS) else fn
                pcard = c if c in C.CARDS else C.params_card(c)
                by_state[c] = {s: f_(C.state_view(R[c], s), pcard)["outcome"] for s in C.mixed_states(IDLE[c])}
        it["all_cards"] = C.all_cards_block(status, present, expect, registered=reg,
                                            idle=(IDLE if effect else None), idle_effect=effect, note=note, by_state=by_state)
        it["reading_all_cards"] = C.reading_all(it["all_cards"])
        return it

    # ---- T1 negative zero
    def t1(rs, pc):
        return per_card_result([sub_welch(rs, "m_negzero", "fp32_zeros", "difference", band=(6.0, None), label="negzero - zeros > +6 W"),
                                sub_welch(rs, "m_negzero", "fp32_ones", "equivalence", tol=1.0, label="negzero - ones within +-1 W")])
    pc = per_card(t1)
    items.append(four(item("ABL-T1", "Welch, Bonferroni 0.01/19; negzero-zeros difference (> +6 W), negzero-ones equivalence (+-1.0 W)", pc,
                           "-0.0 vs +0.0 and vs ones: " + short(pc, lambda c, v: " / ".join(sub_str(s) for s in v["subtests"]) + f" -> {v['outcome']}")),
                      t1, "each", "difference"))

    # ---- T2 operand order
    P2 = {A2: 3.5, A3: 3.2}

    def t2(rs, pc):
        return per_card_result([sub_welch(rs, "fp32_a1br", "fp32_arb1", "difference", pred=P2[pc], tol=1.0,
                                          label="A ones/B randn - A randn/B ones")])
    pc = per_card(t2)
    items.append(four(item("ABL-T2", "Welch, Bonferroni 0.01/19; difference, +3.5 (a2) / +3.2 (a3) +- 1.0 W", pc,
                           "operand order: " + short(pc, lambda c, v: sub_str(v["subtests"][0]) + f" -> {v['outcome']}")),
                      t2, "specific", "difference"))

    # ---- T3 bit fields
    P3 = {A2: (4.7, 9.0, 3.0), A3: (4.3, 8.3, 2.4)}

    def t3(rs, pc):
        return per_card_result([
            sub_welch(rs, "fp32_signs", "fp32_ones", "difference", pred=P3[pc][0], tol=1.0),
            sub_welch(rs, "fp32_mant", "fp32_signs", "difference", pred=P3[pc][1], tol=1.5),
            sub_welch(rs, "fp32_randn", "fp32_mant", "difference", pred=P3[pc][2], tol=1.0)])
    pc = per_card(t3)
    items.append(four(item("ABL-T3", "Welch, Bonferroni 0.01/19; three differences: signs-ones +-1.0, mant-signs +-1.5, randn-mant +-1.0 W "
                           "(tolerances of x1_predictions.json); pow2-signs not in the family", pc,
                           "bit-field ladder: " + short(pc, lambda c, v: ", ".join(sub_str(s) for s in v["subtests"]) + f" -> {v['outcome']}"),
                           extra={"note": "horace-lowpower-025 (exponents cost more than signs) is not tested and stays dropped"}),
                      t3, "specific", "difference"))

    # ---- T4 structured matrices. aifoundry3: switching - 0.924 x model (equivalence for the three non-DFT patterns,
    # difference +2.7 / +1.3 for DFT / ReLU). aifoundry2 "repeats its E15 values": the three equivalences are to its
    # E15 values (a2_measured_E15_W), and DFT / ReLU are the E15 misses above 1.0 x model (the same E15 values, with
    # the difference rule's sign condition).
    SCALE = {A2: 1.0, A3: 0.924}
    P4 = {A2: {"m_fft_cos": X1["m_fft_cos"]["a2_miss_W"], "m_relu": X1["m_relu"]["a2_miss_W"]}, A3: {"m_fft_cos": 2.7, "m_relu": 1.3}}

    def t4(rs, pc):
        subs = []
        for k in ("m_hadamard", "m_butterfly", "m_kaleidoscope"):
            if pc == A2:
                subs.append(sub_one(rs, k, "equivalence", mu=X1[k]["a2_measured_E15_W"], tol=1.0,
                                    label=f"{k} - E15 {X1[k]['a2_measured_E15_W']:.2f} W within +-1 W"))
            else:
                subs.append(sub_one(rs, k, "equivalence", mu=SCALE[pc] * X1[k]["model_switching_W"], tol=1.0,
                                    label=f"{k} - {SCALE[pc]} x model within +-1 W"))
        for k in ("m_fft_cos", "m_relu"):
            subs.append(sub_one(rs, k, "difference", mu=SCALE[pc] * X1[k]["model_switching_W"], pred=P4[pc][k], tol=1.0,
                                label=f"{k} - {SCALE[pc]} x model = {P4[pc][k]:+.2f}"))
        return per_card_result(subs)
    pc = per_card(t4)
    items.append(four(item("ABL-T4", "one-sample t on runs, Bonferroni 0.01/19. aifoundry3: switching - 0.924 x model "
                           "(x1_predictions.json model_switching_W) inside +-1.0 W for Hadamard, butterfly, kaleidoscope; "
                           "DFT pair +2.7 and ReLU +1.3 +-1.0 W above 0.924 x model (difference). aifoundry2 repeats its E15 "
                           "values: switching - E15 inside +-1.0 W for the three, and DFT +2.95 / ReLU +1.38 +-1.0 W above "
                           "1.0 x model (its E15 misses)", pc,
                           "structured matrices vs the flip model: " + short(pc, lambda c, v: ", ".join(sub_str(s) for s in v["subtests"]) + f" -> {v['outcome']}")),
                      t4, "specific", "absolute"))

    # ---- T5 precision (pJ per MAC over idle) and its EM4 rider
    P5 = {A2: (0.32, 2.70), A3: (0.29, 2.49)}

    def t5_ratio(rs):
        r32, r8 = C.pick(rs, "fp32_randn", REG), C.pick(rs, "int8_randn", REG)
        ci = C.ratio(vals(r32, per="per_s"), vals(r8, per="per_s"), ALPHA)
        s3 = {"test": "fp32/int8 pJ per MAC ratio in [15, 23]", "kind": "difference", "band": (15, 23), "ci": C.rnd(ci)}
        if not enough(r32, r8) or "lo" not in ci:
            s3["ok"] = None
        else:
            excl = ci["log_lo"] > 0 if ci.get("method") == "welch on logs" else ci["lo"] > 1
            s3["ok"] = bool(excl and 15 <= ci["point"] <= 23)
        return s3

    def t5_pj(rs, pc):
        return [sub_one(rs, "int8_randn", "difference", pred=P5[pc][0], tol=0.04, per="per_s", label="int8 randn pJ/MAC"),
                sub_one(rs, "fp16_randn", "difference", pred=P5[pc][1], tol=0.2, per="per_s", label="fp16 randn pJ/MAC")]

    def t5(rs, pc):
        return per_card_result(t5_pj(rs, pc) + [t5_ratio(rs)])

    def t5_other(rs, pc):
        # a card beyond the registered two: the ratio band is registered "on each card" and is tested; the int8 / fp16
        # pJ per MAC bands are given per registered card and are reported against both
        r = per_card_result([t5_ratio(rs)])
        r["reported"] = {f"vs_{c}_values": t5_pj(rs, c) for c in C.CARDS}
        r["note"] = "tested: the fp32/int8 ratio (registered on each card); int8 / fp16 pJ per MAC reported against both registered cards' bands"
        return r
    pc = per_card(t5)
    items.append(four(item("ABL-T5", "one-sample t, Bonferroni 0.01/19, of pJ per MAC over idle (switching / MAC per s): int8 randn "
                           "0.32/0.29 +-0.04, fp16 randn 2.70/2.49 +-0.2 (a2/a3); fp32/int8 ratio: Welch on logs, point in [15, 23], "
                           "interval excluding 1", pc,
                           "pJ per MAC: " + short(pc, lambda c, v: ", ".join(f"{s['test']} {C.fmt_ci(s['ci'], '', 3)}" for s in v["subtests"]) + f" -> {v['outcome']}")),
                      t5, "each", "absolute", extra_fn=t5_other,
                      note="aifoundry1's cards: only the fp32/int8 ratio is tested (registered on each card); the pJ per MAC bands are per registered card and are reported"))

    def em4(rs, pc):
        subs = []
        for p in EM4_PATTERNS:
            x = C.pick(rs, p, REG)
            ci = C.one_sample(vals(x), 0.01)
            subs.append({"test": f"{p} switching > 0 (99% t)", "ci": C.rnd(ci), "ok": (bool(ci["lo"] > 0) if enough(x) else None)})
        return per_card_result(subs)
    em = per_card(em4)
    ratios = {}
    for p in EM4_PATTERNS:
        x3, x2 = C.pick(R[A3], p, REG), C.pick(R[A2], p, REG)
        ci = C.ratio(vals(x3), vals(x2), 0.01)
        ratios[p] = {"ci": C.rnd(ci), "in_0.88_0.96": (bool(0.88 <= ci["point"] <= 0.96) if "point" in ci and enough(x3, x2) else None)}
    it = item("ABL-T5-EM4", "EM4 rider of ABL-T5 (energy-manual fp16/int8 rows): per card, 99% t on per-run switching of "
              "fp16/int8 zeros, ones, randn excludes 0 -> the rows hold on that card, printed per card with its launch "
              "temperature; the aifoundry3/aifoundry2 ratio's 99% interval is reported against 0.92 +- 0.04", em,
              "fp16/int8 rows: " + short(em, lambda c, v: f"{sum(1 for s in v['subtests'] if s['ok'])}/6 exclude 0 -> {v['outcome']}")
              + "; a3/a2 " + ", ".join(f"{p} {r['ci'].get('point', float('nan')):.3f}" for p, r in ratios.items() if 'point' in r['ci'])
              + (f" ({sum(1 for r in ratios.values() if r['in_0.88_0.96'])}/6 in the predicted 0.92 +- 0.04)"
                 if all(r["in_0.88_0.96"] is not None for r in ratios.values()) else ""),
              extra={"claims": ["energy-manual-53", "energy-manual-54", "energy-manual-56", "energy-manual-57"], "ratio_a3_over_a2": ratios})
    # reported: each other card over aifoundry2 (busy rule on both), beside the registered a3/a2
    it["ratio_over_aifoundry2_all_cards"] = {c: {p: C.rnd(C.ratio(vals(C.pick(RB[c], p, REG)), vals(C.pick(RB[A2], p, REG)), 0.01))
                                                 for p in EM4_PATTERNS} for c in EXTRA}
    items.append(four(it, em4, "each", "absolute"))

    # ---- T6 integer loop
    P6 = {A2: (1.46, 0.4), A3: (1.35, 0.5)}

    def t6(rs, pc):
        return per_card_result([sub_one(rs, "spin", "difference", pred=P6[pc][0], tol=P6[pc][1], label="spin over idle")])
    pc = per_card(t6)
    items.append(four(item("ABL-T6", "one-sample t, Bonferroni 0.01/19: spin switching excludes 0 and within 1.46 +- 0.4 (a2) / "
                           "1.35 +- 0.5 (a3) W", pc, "integer loop: " + short(pc, lambda c, v: sub_str(v["subtests"][0]) + f" -> {v['outcome']}")),
                      t6, "specific", "absolute"))

    # ---- T7 active minions
    def t7(rs, pc):
        r1, r256 = C.pick(rs, "fp32_randn", REG), C.pick(rs, "fp32_randn_8", REG)
        ci = C.ratio(vals(r1), vals(r256), ALPHA, scale=256.0 / 1024.0)
        s1 = {"test": "per-minion switching 1024 / 256 in [0.98, 1.10]", "kind": "band", "band": (0.98, 1.10), "ci": C.rnd(ci),
              "ok": (bool(0.98 <= ci["point"] <= 1.10) if enough(r1, r256) and "point" in ci else None)}
        pts = [(r["minions"], r["switching"]) for k in ("fp32_randn_8", "fp32_randn_16", "fp32_randn") for r in C.pick(rs, k, REG)]
        n16 = C.pick(rs, "fp32_randn_16", REG)
        lf = C.linfit([m for m, _ in pts], [s for _, s in pts], ALPHA)
        s2 = {"test": "intercept of the line through 256/512/1024 minions <= +0.5 W (upper end of the corrected interval)",
              "kind": "bound", "fit": C.rnd(lf), "ok": (bool(lf["intercept_hi"] <= 0.5) if enough(r1, r256, n16) and "intercept_hi" in lf else None)}
        return per_card_result([s1, s2])
    pc = per_card(t7)
    items.append(four(item("ABL-T7", "per-minion switching ratio 1024 v 256 minions (Welch on logs, Bonferroni 0.01/19): point in "
                           "[0.98, 1.10]; least-squares line of per-run switching on active minions (256, 512, 1024): upper end of "
                           "the Bonferroni interval of the intercept <= +0.5 W", pc,
                           "active minions: " + short(pc, lambda c, v: f"ratio {v['subtests'][0]['ci'].get('point', float('nan')):.3f}, intercept "
                                                      f"{v['subtests'][1]['fit'].get('intercept', float('nan')):+.2f} W (hi {v['subtests'][1]['fit'].get('intercept_hi', float('nan')):+.2f}) -> {v['outcome']}")),
                      t7, "each", "absolute"))

    # ---- T8 anchors
    P8 = {A2: ((8.5, 0.8), (25.2, 1.0)), A3: ((7.8, 0.8), (23.0, 1.5))}

    def t8(rs, pc):
        return per_card_result([
            sub_welch(rs, "fp32_ones", "fp32_zeros", "difference", pred=P8[pc][0][0], tol=P8[pc][0][1]),
            sub_welch(rs, "fp32_randn", "fp32_zeros", "difference", pred=P8[pc][1][0], tol=P8[pc][1][1])])
    pc = per_card(t8)
    items.append(four(item("ABL-T8", "Welch, Bonferroni 0.01/19: ones-zeros +8.5/+7.8 +-0.8, randn-zeros +25.2 +-1.0 / +23.0 +-1.5 W", pc,
                           "anchors: " + short(pc, lambda c, v: ", ".join(sub_str(s) for s in v["subtests"]) + f" -> {v['outcome']}")),
                      t8, "specific", "difference"))

    # ---- ABL-R descriptive: refit per card, half-differences, drift, launch temperatures
    def abl_r(rs, pc):
        fit_s, fit_p = refit(rs, "switching"), refit(rs, "p80_d")
        half = {}
        for cfg in sorted({r["config"] for r in rs}):
            v = vals(C.pick(rs, cfg, REG))
            if len(v) >= 2:
                half[cfg] = {"n": len(v), "half_range_W": C.rnd((max(v) - min(v)) / 2), "sd_W": C.rnd(float(np.std(v, ddof=1)))}
        drift = [r["drift_w_per_c"] for r in rs if r["kept"] and "drift_w_per_c" in r]
        lt = [r["t_launch"] for r in rs if r["kept"] and r.get("t_launch") is not None]
        st = [r["start_temp"] for r in rs if r["kept"] and r.get("start_temp") is not None]
        ok = None if "loo_rms" not in fit_s else bool(fit_s["loo_rms"] <= 0.6)
        return {"outcome": "INSUFFICIENT" if ok is None else ("PASS" if ok else "FAIL"),
                "refit_switching": fit_s, "refit_p80": fit_p, "half_differences": half,
                "drift_w_per_c": C.rnd(C.one_sample(drift, 0.01)), "launch_temp_c": C.rnd(C.one_sample(lt, 0.01)),
                "start_temp_reading_c": C.rnd(C.one_sample(st, 0.01)),
                "dropped_samples": int(sum(r.get("dropped_samples", 0) for r in rs))}
    rr = per_card(abl_r)
    oc = rr[A3]["outcome"]
    it = item("ABL-R", "descriptive: per card, the four flip energies refitted (non-negative least squares, constant "
              "free, RTL counts of toggles_all.json) on the 14 fp32 patterns' mean switching, leave-one-out rms; the p80 "
              "fit beside it; run-to-run half-differences; within-run drift slope (runs heating >= 3 C); launch "
              "temperatures. Decision (aifoundry3 only): leave-one-out rms <= 0.6 W lets 'predicts to 0.5 W rms' read "
              "'on both cards'", rr,
              "flip-model refit: " + short(rr, lambda c, v: f"loo rms {v['refit_switching'].get('loo_rms', 'n/a')} W over "
                                           f"{v['refit_switching'].get('patterns')} patterns, drift {v['drift_w_per_c'].get('mean', float('nan')):.2f} W/C, "
                                           f"launch {v['launch_temp_c'].get('mean', float('nan')):.1f} C")
              + f" -> {oc} (decided on aifoundry3)", outcome=oc)
    items.append(four(it, abl_r, "a3", "difference", why="decided on aifoundry3 only (the 0.6 W leave-one-out bound); each card's own fit is stated",
                      note="the fit's free constant absorbs a card's idle step, so the fitted flip energies and the leave-one-out rms do not depend on the idle state; constant_W does"))

    # ---- EM4c cycles per op (every timed launch, kept runs). Exact: one launch off its value falsifies it (FAIL);
    # PASS needs >= 3 kept runs (separately started processes) of each type on the card, else INSUFFICIENT.
    def em4c(rs, pc):
        bad, n, per, nruns = [], 0, {}, {}
        for r in rs:
            if not r["kept"] or r.get("test") != "fma":
                continue
            want = 318.00 if r["type"] == "int8" else 546.00
            if r.get("cycles_timed"):
                nruns[r["type"]] = nruns.get(r["type"], 0) + 1
            for x in r.get("cycles_timed", []):
                n += 1
                per.setdefault(r["type"], set()).add(round(x, 2))
                if round(x, 2) != want:
                    bad.append({"pass": r["pass"], "config": r["config"], "cycles_per_op": x})
        types = {t: sorted(v) for t, v in per.items()}
        full = all(nruns.get(t, 0) >= MIN_N for t in ("fp32", "fp16", "int8"))
        return {"launches": n, "runs_by_type": nruns, "values_by_type": types, "outside": bad[:20], "n_outside": len(bad),
                "outcome": "FAIL" if bad else ("PASS" if full else "INSUFFICIENT")}
    cyc = per_card(em4c)
    items.append(four(item("ABL-EM4c", "exact: every timed launch (launch >= 0; the 20,000-iteration calibration launch is excluded) of "
                           "every kept fma run reads 546.00 (fp32, fp16) or 318.00 (int8) cycles per op at 2 decimals; any "
                           "launch off -> FAIL, PASS needs >= 3 kept runs of each type on the card", cyc,
                           "cycles per op: " + short(cyc, lambda c, v: f"{v['launches']} launches, {v['n_outside']} off, {v['values_by_type']} -> {v['outcome']}")),
                      em4c, "each"))

    # ---- EM4d aifoundry2 vs 21 Sep (p80, the same reduction applied to the committed session)
    old = []
    if os.path.isdir(a.legacy_a2):
        old = C.session_runs(a.legacy_a2, PAR[A2]["leak"], PAR[A2]["launch"], {"pass": 0, "card": A2})

    def em4d_a2(new_runs, old_runs):
        subs, extra = [], {}
        for p in sorted({r["config"] for r in old_runs if r["kept"]} & {r["config"] for r in new_runs}):
            new_r = C.pick(new_runs, p, REG)
            old_v = [r["p80"] for r in old_runs if r["config"] == p and r["kept"]]
            ci = C.welch(vals(new_r, "p80"), old_v, 0.01)
            rel = 100.0 * ci["point"] / np.mean(old_v) if "point" in ci else None
            s = {"test": f"{p} p80 new - 21 Sep", "ci": C.rnd(ci), "rel_pct": C.rnd(rel), "within_2pct": (abs(rel) <= 2 if rel is not None else None),
                 "ok": (bool(ci["lo"] <= 0 <= ci["hi"]) if len(new_r) >= MIN_N and "lo" in ci else None)}
            (subs if p in TENSOR9 else extra.setdefault("others", [])).append(s)
        if not old_runs or len(subs) < len(TENSOR9):
            res = {"outcome": "INSUFFICIENT", "subtests": subs, "note": f"{len(subs)} of the 9 tensor patterns"}
        else:
            res = per_card_result(subs)
        res["other_patterns"] = extra.get("others", [])
        return res
    em4d = {A3: {"outcome": "N/A", "note": "aifoundry2 only"}, A2: em4d_a2(R[A2], old)}
    oc = em4d[A2]["outcome"]
    it = item("ABL-EM4d", "aifoundry2 only, consistency check: per EM4 tensor pattern (fp32/fp16/int8 x zeros/ones/randn), "
              "Welch 99% of p80 (new) - p80 (21 Sep ablation session, reduced here with the same leak 0.81 and windows) "
              "includes 0; the 2% prediction is reported per pattern", em4d,
              f"a2 vs 21 Sep: {sum(1 for s in em4d[A2].get('subtests', []) if s['ok'])}/{len(em4d[A2].get('subtests', []))} include 0, "
              f"{sum(1 for s in em4d[A2].get('subtests', []) if s.get('within_2pct'))} within 2% -> {oc}", outcome=oc)
    for c in EXTRA:
        em4d[c] = {"outcome": "N/A", "note": "aifoundry2 only (no earlier session of this card to compare with)"}
    st = {c: ("N/A" if c != A2 else em4d_a2(RB[A2], C.busy_view(old))["outcome"]) for c in ALL}
    it["all_cards"] = C.all_cards_block(st, present, expect, registered={A2: oc},
                                        note="aifoundry2 only: a consistency check against its own 21 Sep session")
    it["reading_all_cards"] = C.reading_all(it["all_cards"])
    items.append(it)

    json.dump(C.jsonable(items), open(a.out, "w"), indent=1)
    diag = {"exp": EXP, "data": os.path.abspath(a.data), "registered_passes": REG, "passes_used": passes, "passes_skipped": skipped,
            "x1_predictions_sha256": pred_sha, "alpha": ALPHA, "params": PAR,
            "params_by_card": {c: par(c) for c in R}, "cards_present": present, "cards_all": ALL, "idle_by_card": IDLE,
            "runs": {c: [{k: C.rnd(v) for k, v in r.items() if k not in ("cycles_timed", "cycles_calib")} for r in R[c]] for c in R}}
    json.dump(C.jsonable(diag), open(os.path.splitext(a.out)[0] + ".runs.json", "w"), indent=1)
    for it in items:
        print(f"{it['item']:11s} {it['outcome']:14s} {it['reading'][:230]}")
        print(f"{'':11s} {it['all_cards']['outcome']:14s} {it['reading_all_cards'][:230]}")
    if not have:
        print("no data found under", a.data, file=sys.stderr)


if __name__ == "__main__":
    main()
