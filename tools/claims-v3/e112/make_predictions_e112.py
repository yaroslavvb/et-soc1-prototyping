#!/usr/bin/env python3
"""E112 (Q133): write E112's freeze, before the claim of aifoundry1 card 1 and the first launch.

    python3 tools/claims-v3/e112/make_predictions_e112.py          # writes predictions-e112.json and predictions-real2-card1.json

E112 adds no new prediction for any tile. It freezes:
  (a) that E91's registration (tools/claims-v3/kinds/E91.md, eb72ce5d, A1 7f007f53) is re-run UNCHANGED on new passes:
      predictions-e91.json, reduce_e91.py and score_e91.py by sha256, the pass, the minimum of four kept passes;
  (b) the card-1 view of Q132(r)'s frozen file (real2/predictions-real2.json, 6ae4c3d5): every number in watts that a
      frozen claim of E95 reads, divided by E82's per-type card scale (E82 scored.json > cross_card.primary.x3 >
      per_type_median), written to predictions-real2-card1.json; E112b's cross-card rules (X1, X4, X5) against E95's
      committed reductions, their thresholds, and their power simulated from E95's own per-pass scatter;
  and the session's plan and budget, and the sha256 of every file the session runs or the desk reduces with.
Every number is read from a committed file named here (checked by sha256), never retyped. Standard library only.
"""
import copy
import hashlib
import json
import math
import os
import random
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = "tools/claims-v3/kinds"
E = "tools/claims-v3/e112"
D95 = "docs/reports/data/2026-11-01-e95-real-tensors-energy"
D82 = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1"
D86 = "docs/reports/data/2026-10-31-e86-real-tensors-energy"
D91 = "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1"
TYPES = ("fp32", "fp16", "int8")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}


def sha(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()


def last_commit(rel):
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h", "--", rel], capture_output=True, text=True)
    return r.stdout.strip() or None


def frozen(rel, want=None):
    h = sha(rel)
    if want and h != want:
        raise SystemExit(f"{rel}: sha256 {h} != the recorded {want}")
    return {"path": rel, "sha256": h, "commit": last_commit(rel)}


def load(rel):
    return json.load(open(os.path.join(ROOT, rel)))


# ---- the inputs, checked against the values earlier registrations recorded ---------------------------------------
INPUTS = {
    "e91_predictions": frozen(f"{K}/predictions-e91.json", "56efe2e752f8de8bebb870f1c34ea153f49b0ebc2de90762b74372ef76a10e09"),
    "real2_predictions": frozen(f"{K}/real2/predictions-real2.json", "0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a"),
    "real2_json": frozen(f"{K}/real2/real2.json", "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715"),
    "real_json": frozen(f"{K}/real/real.json", "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"),
    "e82_scored": frozen(f"{D82}/scored.json"),
    "e82_reduction": frozen(f"{D82}/e82.json", "4794f5ac4ccfde95f45535aa855fa06c8d85b7d7716c9b63bd508ded1ade8601"),
    "e95_reduction": frozen(f"{D95}/e95.json"),
    "e95_nodips": frozen(f"{D95}/dips-arm/e95-nodips.json"),
    "e95_scored": frozen(f"{D95}/scored.json"),
    "e95_nodips_scored": frozen(f"{D95}/dips-arm/scored-nodips.json"),
    "e95_leak0.1994": frozen(f"{D95}/e95-leak0.1994.json"),
    "e95_leak0.3803": frozen(f"{D95}/e95-leak0.3803.json"),
    "e95_leak0": frozen(f"{D95}/e95-leak0.json"),
    "e86_reduction": frozen(f"{D86}/e86.json", "e5cc743acdc6bd47ec0b32603ed433ef09daf3f9d08c3163d66c1854eaedca40"),
    "e91_reduction": frozen(f"{D91}/e91.json"),
}

# the card code both halves run, unchanged (E91's and E95's freezes list the same E78 files)
CARD_CODE = [
    "tools/claims-v3/lib.sh", f"{K}/e78_common.py", f"{K}/run_e78.py", f"{K}/reduce_e78.py", f"{K}/kinds.json",
    f"{K}/e86_common.py", f"{K}/run_e86.py", f"{K}/block_e86.sh", f"{K}/predictions-e86.json",
    f"{K}/e95_common.py", f"{K}/run_e95.py", f"{K}/block_e95.sh", f"{K}/predictions-e95.json",
    f"{K}/real/real.json", f"{K}/real2/real2.json", f"{K}/real2/predictions-real2.json",
]
# the desk code (a) reduces and scores with, unchanged, and what (b) reuses
DESK_CODE = [
    f"{K}/reduce_e91.py", f"{K}/score_e91.py", f"{K}/score_e86.py", f"{K}/score_e82.py", f"{K}/score_e78.py",
    f"{K}/collect_e91.sh", f"{K}/score_e95.py", f"{K}/selftest_e78.py", f"{K}/selftest_e91.py", f"{K}/predictions-e91.json",
]
E112_FILES = [f"{E}/run_e112.sh", f"{E}/queue_e112.sh", f"{E}/reduce_e112b.py", f"{E}/score_e112b.py",
              f"{E}/collect_e112.sh", f"{E}/selftest_e112.py", f"{E}/predictions-real2-card1.json"]


def check_e91_harness(reg91):
    """E91 recorded the sha256 of the card code it ran; (a) runs the same bytes."""
    bad = [r for r, w in reg91["harness"]["reused_unchanged_sha256"].items() if sha(r) != w]
    if bad:
        raise SystemExit(f"E91's card code changed since its freeze: {bad}")
    return reg91["harness"]["reused_unchanged_sha256"]


def check_e95_harness():
    reg95 = load(f"{K}/predictions-e95.json")
    bad = [r for r, w in reg95["harness"]["reused_unchanged_sha256"].items() if sha(r) != w]
    bad += [r for r, w in reg95["harness"].get("e95_files_sha256", {}).items()
            if os.path.exists(os.path.join(ROOT, r)) and sha(r) != w]
    if bad:
        raise SystemExit(f"E95's code changed since its freeze: {bad}")
    return reg95["harness"]


# ---- (b): the card-1 view of the frozen file -----------------------------------------------------------------------

def card1_view(F, scale):
    """Q132(r)'s frozen file with every watt figure a frozen E95 claim reads divided by E82's scale of the tile's type.
    Ratios, live shares, bus counts, clocks and the claims' r thresholds are unchanged. known_misses stays as frozen
    (aifoundry3's history, reported beside C12 only). Two thresholds that score_e95.py writes in its code, not in the
    file (C7's +-0.40 W, C8's 0.5 W), are added here, scaled, as e112_threshold_w for score_e112b.py's ports."""
    G = copy.deepcopy(F)
    s = lambda ty: scale[ty]

    def div(x, ty):
        if isinstance(x, list):
            return [div(v, ty) for v in x]
        return None if x is None else round(x / s(ty), 4)

    for key, t in G["tiles"].items():
        ty = key.split("/", 1)[0]
        a = t["a_aifoundry3_600mhz"]
        for k in ("D_w", "scoring_interval_w", "scoring_halfwidth_w", "e86_only_arm_w", "bias_arm_w",
                  "amendment1_halfwidth_w", "nearest_e78_kind_D_w"):
            if k in a:
                a[k] = div(a[k], ty)
        a["terms_w"] = {k: div(v, ty) for k, v in a["terms_w"].items()}
        for blk in ("c_gate_law", "c_if_gate_took_numeric_zero"):
            if blk in t:
                for k in ("D_w", "scoring_interval_w", "halfwidth_w", "D_w_with_L_from_e86_real_tiles"):
                    if k in t[blk]:
                        t[blk][k] = div(t[blk][k], ty)
        if "a_prime_offset" in t:
            o = t["a_prime_offset"]
            for k in ("offset_w", "interval_w", "halfwidth_w", "anchored_on_e86_measured_partner_w"):
                if k in o:
                    o[k] = div(o[k], ty)
    for ty, g in G["gate_law"]["per_type"].items():
        g["L_w"], g["G_w"] = div(g["L_w"], ty), div(g["G_w"], ty)
        for m in g.get("known_misses", {}).values():
            for k in ("D_w", "law_w", "miss_w"):
                if k in m:
                    m[k] = div(m[k], ty)
    for ty, r in G["references_e78"].items():
        r["D_measured_w"], r["D_model_fit_w"] = div(r["D_measured_w"], ty), div(r["D_model_fit_w"], ty)
    for n, t in G["e86_tiles_rerun"].items():
        ty = n.split(".", 1)[0]
        for k in ("frozen_point_w", "e86_measured_D_w", "e86_measured_ci95_w"):
            if k in t:
                t[k] = div(t[k], ty)
    c = G["claims"]["E95"]
    for t, v in c["C5_int8_bits_or_gate"]["predicted"].items():
        v["a_w"], v["c_w"] = div(v["a_w"], "int8"), div(v["c_w"], "int8")
    c6 = c["C6_calibration_lever"]
    c6["threshold_w"], c6["predicted_w"] = div(c6["threshold_w"], "int8"), div(c6["predicted_w"], "int8")
    c7 = c["C7_calibration_rank"]
    c7["predicted_offsets_w"] = {k: div(v, "int8") for k, v in c7["predicted_offsets_w"].items()}
    c7["e112_threshold_w"] = div(0.40, "int8")
    c8 = c["C8_asym_turns_the_gate_off"]
    c8["predicted_w"] = div(c8["predicted_w"], "int8")
    c8["e112_threshold_w"] = div(0.5, "int8")
    c9 = c["C9_negative_zero"]
    c9["prediction_gate_blind_w"] = div(c9["prediction_gate_blind_w"], "fp32")
    g = c9["prediction_if_gate_took_numeric_zero"]
    g["D_w"], g["scoring_interval_w"] = div(g["D_w"], "fp32"), div(g["scoring_interval_w"], "fp32")
    c11 = c["C11_fp16_forward"]
    c11["band_w"], c11["predicted_w"] = div(c11["band_w"], "fp16"), div(c11["predicted_w"], "fp16")
    G["experiment"] = "E112b (Q133): the card-1 view of Q132(r)'s frozen file"
    G["e112_card1_view"] = {
        "of": {"path": INPUTS["real2_predictions"]["path"], "sha256": INPUTS["real2_predictions"]["sha256"],
               "commit": "6ae4c3d5"},
        "rule": "every watt figure a frozen E95 claim reads, divided by E82's per-type card scale of the tile's type "
                "(Q130(n)'s Amendment 1 did the same for E91); ratios, live shares, bus counts, clocks and r thresholds "
                "unchanged; known_misses as frozen (reported only); C7's +-0.40 W and C8's 0.5 W, which score_e95.py "
                "writes in its code, added scaled as e112_threshold_w",
        "scale": scale, "scale_source": f"{D82}/scored.json cross_card.primary.x3.per_type_median",
        "excludes": "the card-scale spread (E82's per-kind ratios: IQR 1.025-1.034 over 32 kinds; X3 FAIL)",
        "b_aifoundry2_governor": "aifoundry2's clock predictions are untouched and not used by E112",
    }
    return G


# ---- (b): the cross-card rules' power, simulated from E95's own scatter ----------------------------------------------

def per_pass(res, item, key="D"):
    out = []
    for p in res["passes"]:
        e = res["per_pass"].get(str(p), {}).get(item)
        out.append(None if e is None else e.get(key))
    return out


def mean_sd(v):
    v = [x for x in v if x is not None]
    return (statistics.fmean(v), statistics.stdev(v) if len(v) > 1 else 0.0, len(v))


def spearman(x, y):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for i, j in enumerate(o):
            r[j] = i + 1.0
        return r
    rx, ry = rk(x), rk(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy)


def simulate(nod, pool, scale, X, n_pass=3, n_sim=4000, seed=112):
    """Card 1 drawn as E95's dips-removed means / scale (or x factor for 'unshared') with E95's per-pass scatter at
    n_pass passes; E95's own means fixed (they are the committed reference)."""
    rng = random.Random(seed)
    st = {}
    for n in pool + list(REF.values()):
        m, sd, k = mean_sd(per_pass(nod, n))
        st[n] = (m, sd)
    rst = {}
    for n in pool:
        ty = n.split(".", 1)[0]
        rv = [a / b for a, b in zip(per_pass(nod, n), per_pass(nod, REF[ty])) if a is not None and b]
        rst[n] = (statistics.fmean(rv), statistics.stdev(rv) if len(rv) > 1 else 0.0)
    elig = X["X4"]["eligible"]
    out = {}
    worlds = {
        # world: (factor on every tile's D beyond the card scale, apply the card scale, shift of every tile's r)
        "shared": (1.0, True, 0.0),
        "unshared_x1.03": (1.03, True, 0.0),
        "scale_1.00": (1.0, False, 0.0),
        "tile_ratios_shift_0.02": (1.0, True, 0.02),
        "tile_ratios_shift_0.04": (1.0, True, 0.04),
    }
    for world, (fac, scaled, shift) in worlds.items():
        p1 = {ty: 0 for ty in TYPES}
        p1all = p4 = p5 = 0
        for _ in range(n_sim):
            c1 = {}
            for n, (m, sd) in st.items():
                ty = n.split(".", 1)[0]
                base = (m / scale[ty] if scaled else m) * (fac if n in pool else 1.0)
                c1[n] = base + rng.gauss(0, sd / math.sqrt(n_pass))
            ok1 = True
            for ty in TYPES:
                names = X["X1"]["sets"][ty]
                rho = spearman([c1[n] for n in names], [st[n][0] for n in names])
                if rho >= X["X1"]["threshold"]:
                    p1[ty] += 1
                else:
                    ok1 = False
            p1all += ok1
            rat = sorted(st[n][0] / c1[n] for n in elig)
            med = statistics.median(rat)
            p4 += X["X4"]["band"][0] <= med <= X["X4"]["band"][1]
            agree = 0
            for n in pool:
                ty = n.split(".", 1)[0]
                m, sd = rst[n]
                rc = m * fac + shift + rng.gauss(0, sd / math.sqrt(n_pass))
                agree += abs(rc - m) <= X["X5"]["band"][ty]
            p5 += agree / len(pool) >= X["X5"]["pass_frac"]
        out[world] = {"X1_all": round(p1all / n_sim, 3), "X1_by_type": {t: round(v / n_sim, 3) for t, v in p1.items()},
                      "X4": round(p4 / n_sim, 3), "X5": round(p5 / n_sim, 3)}
    return out


def main():
    reg91 = load(INPUTS["e91_predictions"]["path"])
    e91_card = check_e91_harness(reg91)
    h95 = check_e95_harness()
    F = load(INPUTS["real2_predictions"]["path"])
    scale = {t: round(v, 6) for t, v in load(INPUTS["e82_scored"]["path"])["cross_card"]["primary"]["x3"]["per_type_median"].items()}
    G = card1_view(F, scale)
    view_rel = f"{E}/predictions-real2-card1.json"
    with open(os.path.join(ROOT, view_rel), "w") as f:
        json.dump(G, f, indent=1)
        f.write("\n")

    sys.path.insert(0, os.path.join(ROOT, K))
    import e95_common as e95  # noqa: E402
    pool = list(e95.POOL)
    nod = load(INPUTS["e95_nodips"]["path"])
    prim = load(INPUTS["e95_reduction"]["path"])
    d95 = {n: prim["items"][n]["D"]["mean"] for n in pool}
    elig = sorted(n for n in pool if d95[n] >= 5.0)
    X = {
        "against": "E95's committed reductions of aifoundry3 card 0 (frozen by sha256 and commit): the PRIMARY PAIRING is "
                   "E112b's primary (dips removed, leakage auto) against E95's registered dips-removed arm "
                   "(dips-arm/e95-nodips.json: dips removed, leakage auto, five passes), like with like; reported pairings: "
                   "E112b's dips-kept arm against E95's registered primary (both dips kept, own auto slopes), and both "
                   "at 0.1994 W/C (E112b's leak0.1994 arm, dips removed, against E95's e95-leak0.1994.json, dips kept)",
        "min_passes_each": 3,
        "X1": {"name": "rank", "what": "Spearman rho of D(card 1) against D(aifoundry3) within each type, over E95's tiles of "
               "that type and the type's random kind", "threshold": 0.90, "min_resolved_frac": 0.75,
               "sets": {ty: sorted([n for n in pool if n.startswith(ty + ".")] + [REF[ty]]) for ty in TYPES},
               "pass_if": "rho >= 0.90 in each type (E82's threshold); X1 passes only if all three do; a type with fewer "
                          "than 75% of its set resolved on both cards is NOT SCORED"},
        "X4": {"name": "the real2 tiles share E82's card scale", "what": "median over the eligible tiles of D(aifoundry3, "
               "E95) / D(card 1, E112b), E82's orientation", "band": [1.0008, 1.0608],
               "band_source": "E91-X4's band: E82's measured median 1.0308 +- 0.030 (2.5x the 1.2% sd of E82's per-kind ratios)",
               "eligible_rule": "tiles whose D in E95's registered primary is >= 5 W (E82's eligibility was a predicted >= 5 W); "
                                "chosen from aifoundry3's committed numbers only", "eligible": elig, "min_resolved": 18},
        "X5": {"name": "each tile's ratio to random replicates", "what": "per tile, r = D(tile)/D(random) per pass (E95's "
               "convention), mean over kept passes on each card; a tile agrees if |r(card 1) - r(aifoundry3)| <= its band",
               "band": {"fp32": 0.03, "fp16": 0.03, "int8": 0.06}, "pass_frac": 0.8, "fail_frac": 0.6,
               "band_source": "about 3x (floats) and 2.3x (int8) the largest |difference| of E91's nine GPT-2 tiles between "
                              "card 1 and aifoundry3 (fp32 0.011, fp16 0.005, int8 0.026; E91 README result 1)",
               "pass_if": ">= 80% of resolved tiles agree; FAIL if < 60%; else INCONCLUSIVE; NOT SCORED with fewer than 26 of "
                          "the 33 tiles resolved on card 1", "min_resolved": 26},
    }
    power = simulate(nod, pool, scale, X)
    X["power"] = {"what": "P(PASS) simulated: card 1 = E95's dips-removed means divided by E82's per-type scale ('shared'), "
                          "the real2 tiles at x1.03 of that, i.e. card 1 reading them at aifoundry3's own D ('unshared_x1.03'), no card "
                          "scale at all ('scale_1.00'), or every tile's r shifted by +0.02 or +0.04, with E95's per-pass scatter "
                          "at 3 passes (the base plan; 4 if the spare runs); "
                          "4,000 draws, seed 112. E95's means are held fixed", "by_world": power}

    tie = {
        "what": "reported, never a verdict (E95-S1's form): the session's anchors against E82's card-1 cells (E91-R5's cells "
                "and bands), and E86's three tiles in (b) against (a)'s same-session D of the same tiles",
        "e82_cells": {n: {"D_w": load(INPUTS["e82_reduction"]["path"])["items"][n]["D"]["mean"],
                          "band_w": 0.25 if n.startswith("int8") else 0.5}
                      for n in ("fp32.randn", "fp16.randn", "anchor_pi", "int8.full")},
        "same_session_e86_tiles": {n: {"band_w": 0.5} for n in e95.E86_NAMES},
    }

    plan = {
        "card": "aifoundry1 card 1 only: V3_DEVICE=1, so lib.sh exports ET_DEVICES=1, names the card aifoundry1-c1 and takes "
                "/run/lock/etsoc-shire1.lock; 600 MHz, about 499 mV, TDP 65 W and threshold 65 C as read, never set; "
                "firmware release 1.4.0 (E82 A1)",
        "smoke": {"pass": 11201, "block": f"{K}/block_e86.sh --smoke", "items": "E86's seven 2 s runs (e86_common.SMOKE_ITEMS)",
                  "also": "the session-start ettelem config read (the block's config_start.json, under the lock, timeout 10)"},
        "queue": ["a:11210", "a:11211", "a:11212", "a:11213", "b:11250", "b:11251", "b:11252", "a:11214", "b:11253"],
        "kinds": {"a": {"block": f"{K}/block_e86.sh", "runs_per_pass": 32, "launches_per_pass": 34,
                        "order": "e86_common.pass_order, Random('E86|aifoundry1-c1|<pass>')", "first_estimate_s": 390},
                  "b": {"block": f"{K}/block_e95.sh", "runs_per_pass": 53, "launches_per_pass": 55,
                        "order": "e95_common.pass_order, Random('E95|aifoundry1-c1|<pass>')", "first_estimate_s": 560, "first_estimate_why": "E95's longest pass on aifoundry3, 537 s, plus a margin"}},
        "base": {"a": [11210, 11211, 11212, 11213], "b": [11250, 11251, 11252]},
        "spares": ["a:11214 (E91's registered minimum is four kept passes; on card 1 the first pass of two of the eight "
                   "experiments since E88 was set aside, against one of their 38 later passes)", "b:11253"],
        "data": "build/claims-v3/aifoundry1-c1/kinds/p112<nn>/ and kinds-smoke/p11201/ on aifoundry1 (~/nekko)",
    }
    budget = {
        "card_seconds": 3600, "from": "the claim post's time (E112_T0, epoch seconds)", "to": "the release edit",
        "rule": "queue_e112.sh starts an entry only if now + projected <= E112_T0 + 3600 - 120 (the release reserve: the "
                "session-end read and the release edit) and now + projected <= 2026-11-01 18:45 PST. projected = the longest "
                "measured pass OF THAT KIND so far in this queue, else the kind's first estimate (a 390 s, b 560 s). Exact "
                "integer seconds, no rounding (E91's lesson). An entry that does not fit is skipped and the next tried. A pass "
                "in flight is never cut",
        "reserve_s": 120, "deadline": "2026-11-01 18:45 PST", "no_session_after": "18:00 PST", "runs_end_by": "19:00 PST",
        "claim_text": "using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST (60 min plus a margin, rounded up to the half hour)",
    }

    out = {
        "experiment": "E112", "request": "Q133", "date": "2026-11-01",
        "title": "Replicates on aifoundry1 card 1: E91 re-run so that it scores, and E95's real tiles on a second card",
        "registration": f"{E}/E112.md",
        "answers": {"page": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open",
                    "as_of": "1fe8377a18af",
                    "items": "item 7 ('More real tensors': 'Still open: another card'), and the final critic's replicates "
                             "(its item 8: 'E91 ... not re-run')"},
        "inputs_frozen": INPUTS,
        "harness": {
            "card_code_unchanged_sha256": {r: sha(r) for r in CARD_CODE},
            "e91_card_code_sha256_as_e91_froze_it": e91_card,
            "e95_harness_as_e95_froze_it": h95["reused_unchanged_sha256"],
            "desk_code_unchanged_sha256": {r: sha(r) for r in DESK_CODE},
            "e112_files_sha256": {r: sha(r) for r in E112_FILES if os.path.exists(os.path.join(ROOT, r))},
            "binary": "build/sparsity/host/sparsity_host in aifoundry1's ~/nekko (28 Sep 20:56), the one E82, E88, E91 and "
                      "E108 ran; no rebuild",
        },
        "plan": plan, "card_budget": budget,
        "a": {
            "what": "E91's registration re-run UNCHANGED on new passes: E86's 32-run pass and card code, E78's reduction via "
                    "reduce_e91.py (dips removed, leakage auto; arms dips kept, 0.1994, 0.545, 0.3803, 0), score_e91.py and "
                    "predictions-e91.json, all byte-identical; every rule (R1-R5, S1, X1-X4) and threshold as E91 froze them",
            "registration": {"file": f"{K}/E91.md", "commit": "eb72ce5d", "amendment_A1": "7f007f53"},
            "predictions": INPUTS["e91_predictions"],
            "passes": plan["base"]["a"] + [11214], "min_kept_passes": 4,
            "departures_from_e91": [
                "new pass numbers (11210-11214, smoke 11201)",
                "the budget is E112's, in exact seconds and anchored on the claim (queue_e112.sh), not queue_e86.sh's whole "
                "card-minutes; A1's second queue is replaced by the registered spare a:11214",
                "the session also runs (b); (a)'s four base passes come first, so its first pass is the session's first",
                "E91's 35 card-minutes become E112's 60 for both halves",
            ],
        },
        "b": {
            "what": "E95's 53-run pass and card code on card 1, unchanged, its order seeded with this card's name; E78's "
                    "reduction via reduce_e112b.py (E95's items, card 1's 65/65 config read accepted, dips removed as the "
                    "primary, E88's and E91's registered primary on this card); E95's frozen claims C1-C12 on the card-1 view; "
                    "cross-card rules X1, X4, X5",
            "frozen_claims": "claims.E95 of real2/predictions-real2.json, scored by score_e95.py's own functions on the card-1 "
                             "view (C7 and C8 by ports whose only change is the scaled threshold); conventions as frozen: fewer "
                             "than 3 kept passes NOT SCORED, a claim short of its population UNDER-RESOLVED",
            "card1_view": {"path": view_rel, "sha256": sha(view_rel)},
            "card_scale_e82": scale,
            "passes": plan["base"]["b"] + [11253], "min_kept_passes": 3,
            "arms": ["dips kept", "leakage 0.1994", "leakage 0.545", "leakage 0.3803", "leakage 0"],
            "beside": "each claim also at the frozen thresholds unscaled (a sensitivity, never the verdict)",
            "cross_card": X,
            "session_tie": tie,
        },
    }
    p = os.path.join(HERE, "predictions-e112.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print("wrote", p, "and", view_rel)
    print("scale", scale)
    print("X4 eligible", len(elig), elig)
    print("power", json.dumps(power, indent=1))


if __name__ == "__main__":
    main()
