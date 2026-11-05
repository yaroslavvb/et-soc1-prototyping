#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(p) fix pass: predict_pool8_a2.py, pool 8's predictor after its verifier, as dated note A2 beside
tools/claims-v3/m10/POOL8-REGISTRATION.md registers it (lab 68a7c322, committed before this file existed). predict_pool8.py (lab
9d81d254) stays frozen and byte-identical: this file checks it against its SHA256SUMS, imports it, and changes three things only.
  1. predict and plan exit 3, writing nothing, when a point carries a check_mismatch or is counted twice with different records
     (registration section 2; A2-2). predict_pool8.py exits 1 there. The predictions are predict_pool8.py's own, byte for byte.
  2. burst on card 0 writes M10's own 95% die-rise band, the rise +- the 95th percentile of |term c2's 39 leave-one-tile-out residuals
     on E170| (A2-1). predict_pool8.py's M10 burst_die_rise_95 there is M9's law's band; it is kept as burst_die_rise_95_M9_law.
  3. intervals prints every section-7 bootstrap and coverage line at the pool's own n, and LG's groups with its power at the pool's
     own D_ref (A2-3, A2-4).

  python3 -B predict_pool8_a2.py predict <pool_dir> <card> --counts <counts.json> [...] [--roles <roles.json>] [--no-reuse] [--out <dir>]
  python3 -B predict_pool8_a2.py plan <pool_dir> --counts <counts.json> [...] [--no-reuse]
  python3 -B predict_pool8_a2.py scale | primary | heat-minutes ...      predict_pool8.py's own, unchanged
  python3 -B predict_pool8_a2.py burst <predictions.json> --anchors <reads.json> --die-starts <die-starts.json> [--out <file.json>]
  python3 -B predict_pool8_a2.py intervals <predictions-pool8-<card>.json> [...] [--out <file.json>]
  python3 -B predict_pool8_a2.py selftest [--out <file>]     the frozen T1-T9 re-run and compared, then U0-U7

Standard library and numpy 1.26 (the Intel's system python 3.9). SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import builtins  # noqa: E402
import copy  # noqa: E402
import glob  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FROZEN_PY = os.path.join(HERE, "predict_pool8.py")
OWN_SUMS = os.path.join(HERE, "SHA256SUMS")
A2_SUMS = os.path.join(HERE, "SHA256SUMS-a2")
FROZEN_SELFTEST = os.path.join(HERE, "selftest-pool8.json")
REGD = os.path.join(ROOT, "tools", "claims-v3", "m10")
REG_SUMS = os.path.join(REGD, "POOL8-SHA256SUMS")
DPG_DIR = os.path.join(REGD, "pool8")
E165_PRED = os.path.join(ROOT, "tools", "claims-v3", "e165", "predictions-e165.json")
E164D = os.path.join(ROOT, "tools", "claims-v3", "e164")
E170_RES = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-e170-blind7-card0", "results.json")
A2_COMMIT = "68a7c322"
FROZEN_COMMIT = "9d81d254"
REFUSAL_STOPS = ("check_mismatch", "counted twice")
T9_NAMES = ["fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh",
            "fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi", "fp32.b_onebit_b20_third_a1p5",
            "int8.bheld_33", "int8.b_line_0f_f0"]
RULES_600 = ["P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1", "P8-M1", "P8-M1f", "P8-M1i", "P8-A1", "P8-KA", "P8-H1", "P8-H2",
             "P8-H3", "P8-H4", "P8-LG", "P8-G", "P8-HM"]
RULES_A2 = ["P8-A2-G", "P8-A2-Bg", "P8-A2-Bp", "P8-A2-R2", "P8-A2-F1", "P8-A2-F2", "P8-A2-W1", "P8-A2-W2", "P8-A2-M1", "P8-A2-H1"]
RULES_C0 = ["P8-C0-W", "P8-C0-B", "P8-C0-M1", "P8-C0-F", "P8-C0-H1", "P8-C0-HK"]
load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
_M = {}


def stop(msg):
    raise SystemExit("POOL8-A2 STOPPED: " + msg)


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else os.path.basename(a)


def read_sums(path, base=ROOT):
    out = {}
    for line in open(path):
        if line.strip():
            h, p = line.split(None, 1)
            out[os.path.normpath(os.path.join(base, p.strip().lstrip("*")))] = h
    return out


def check_lists():
    """the frozen predictor's own list (predict_pool8.py among its 16) and this file's list, before anything is imported"""
    bad, n = [], {}
    for lst in (OWN_SUMS, A2_SUMS):
        if not os.path.exists(lst):
            bad.append(f"{rel(lst)} is missing")
            continue
        s = read_sums(lst)
        n[os.path.basename(lst)] = len(s)
        bad += [rel(p) for p, h in s.items() if not os.path.isfile(p) or fsha(p) != h]
    if bad:
        stop("files differ from SHA256SUMS or SHA256SUMS-a2: " + ", ".join(bad))
    return n


def P():
    """predict_pool8.py, frozen, after check_lists()"""
    if "P" not in _M:
        check_lists()
        if HERE not in sys.path:
            sys.path.insert(0, HERE)
        import predict_pool8 as m  # noqa: E402
        _M["P"] = m
    return _M["P"]


def DPG():
    """tools/claims-v3/m10/pool8/design_power_groups.py (A2-4), after check_lists()"""
    if "D" not in _M:
        check_lists()
        if DPG_DIR not in sys.path:
            sys.path.insert(0, DPG_DIR)
        import design_power_groups as d  # noqa: E402
        _M["D"] = d
    return _M["D"]


# ------------------------------------------------------------------ A2-2: the two stops exit 3, nothing written
def mapped(fn, *a, **k):
    """registration section 2 and A2-2: a point with a check_mismatch, or one counted twice with different records, refuses the run
    as a tile short of its convergence-rule N does (exit 3, nothing written). Every other stop stays a stop (exit 1)."""
    try:
        return fn(*a, **k), None
    except P().Refused as e:
        return None, str(e)
    except SystemExit as e:
        c = e.code
        if isinstance(c, str) and c.startswith("POOL8 STOPPED: ") and any(s in c for s in REFUSAL_STOPS):
            return None, json.dumps({"refused_point": c[len("POOL8 STOPPED: "):],
                                     "rule": "registration section 2 (dated note A2-2): the tile gets no prediction and the run exits 3"}, indent=1)
        raise


# ------------------------------------------------------------------ A2-1: card 0's die-rise band under M10
def q95_abs(v):
    """fit_m9_a2.q95's form: numpy.quantile of the sorted absolute values at 0.95, numpy's default linear interpolation"""
    import numpy as np
    return float(np.quantile(np.sort(np.abs(np.asarray(v, float))), 0.95))


def c0_band():
    if "c0" not in _M:
        p = P()
        p.check_inputs()
        t6 = p.t6_card0()
        r = [float(x) for x in t6["c0_h1_reference_residuals_c"]]
        _M["c0"] = {"residuals_c": r, "n": len(r), "hw_c": q95_abs(r), "loto_rms_c": t6["loto_rms_c"], "k_all_tiles": t6["k_all_tiles"]}
    return _M["c0"]


def burst(pred, anchors, die_starts):
    """predict_pool8.burst unchanged; on card 0 the M10 block's burst_die_rise_95 becomes M10's own band (A2-1)"""
    p = P()
    out = p.burst(pred, anchors, die_starts)
    if p.CARDS[pred["card"]] != "c0":
        return out
    b = c0_band()
    g = p.frozen()
    for rec in out["tiles"].values():
        m = rec.get("M10")
        if not m:
            continue
        R = g["P10"].rise_card0_burst(m["burst_board_w"], g["m10"])
        m["burst_die_rise_95_M9_law"] = m["burst_die_rise_95"]
        m["burst_die_rise_95"] = [round(R - b["hw_c"], 3), round(R + b["hw_c"], 3)]
        m["rise_band"] = (f"M10's own (dated note A2-1): the rise +- {b['hw_c']:.4f} C, the 95th percentile of |term c2's {b['n']} "
                          f"leave-one-tile-out residuals on E170|; burst_die_rise_95_M9_law is M9's law's band, never read")
    out["_note_a2"] = (f"predict_pool8_a2.py burst (dated note A2-1, lab {A2_COMMIT}): predict_pool8.py's burst, unchanged except the M10 block's "
                       "burst_die_rise_95 on card 0, which is M10's own band")
    out["m10_card0_rise_band"] = {"hw_c": b["hw_c"], "n_residuals": b["n"], "loto_rms_c": b["loto_rms_c"],
                                  "rule": "rise +- numpy.quantile(sorted |c2's leave-one-tile-out residuals on E170|, 0.95); ends rounded to 0.001 C"}
    return out


# ------------------------------------------------------------------ A2-3: every section-7 line
def rms(v):
    v = [float(x) for x in v]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v]
    return sum(v) / len(v) if v else None


def mins():
    return P().frozen()["reg"]["scoring"]["minimum_tiles"]


def mix_range(refs, mix, rule=None, stat="rms", draws=None, seed=None, median=False):
    """E164's `interval` form (one stream; each draw takes mix[t] errors from refs[t], the formats in sorted order), with the
    registration's draws and rule seed unless given: [the 2.5% point, (the median,) the 97.5% point] as predict_pool8.boot_range indexes"""
    p = P()
    draws = draws or p.frozen()["reg"]["scoring"]["bootstrap_draws"]
    if sum(mix.values()) < 1:
        return None
    rng = random.Random(p.seed_of(rule) if seed is None else seed)
    vals = []
    for _ in range(draws):
        xs = []
        for t, k in sorted(mix.items()):
            e = refs[t]
            xs += [e[rng.randrange(len(e))] for _ in range(k)]
        vals.append(math.sqrt(sum(x * x for x in xs) / len(xs)) if stat == "rms" else sum(xs) / len(xs))
    vals.sort()
    lo, hi = vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1]
    return [lo, vals[int(0.5 * draws)], hi] if median else [lo, hi]


def heat_ref(card, t):
    """A2-3 (c): 2,000 normal draws at M10's held-out 4.5 s heat rms of the format on the card"""
    p = P()
    r = p.frozen()["reg"]["bands"]["heat_4p5s"]["rms_c"][p.CARDS[card]][t]
    rng = random.Random(f"P8|heat-reference|{card}|{t}")
    return [rng.gauss(0.0, r) for _ in range(2000)]


def binom_low(n, p=0.95, alpha=0.025):
    """the smallest k with P(X <= k) >= 0.025, X ~ Binomial(n, 0.95): E163's and E164's binom_low"""
    c = 0.0
    for k in range(n + 1):
        c += math.comb(n, k) * p ** k * (1 - p) ** (n - k)
        if c >= alpha:
            return k
    return n


def e165_refs():
    r = load(E165_PRED)["reference"]
    e = r["e2e"]
    return {"gov_mhz": [float(x) for x in e["governed"]["mhz_err"]], "gov_w": [float(x) for x in e["governed"]["w_err"]],
            "pin_mhz": [float(x) for x in e["pinned"]["mhz_err"]], "pin_w": [float(x) for x in e["pinned"]["w_err"]],
            "heat_c": [float(x) for x in r["heat"]["rise_err_c"]]}


PASS_RMS = "PASS at or below the 97.5% point, else FAIL"


def boot_line(rule, quantity, set_name, n, ref, ref_src, minimum, stat="rms", unit="W", verdict=PASS_RMS):
    L = {"quantity": quantity, "set": set_name, "n": n, "minimum": minimum, "scored_at_planned_n": n >= minimum, "statistic": stat,
         "unit": unit, "verdict_form": verdict, "seed": P().seed_of(rule),
         "reference": {"source": ref_src, "n": len(ref), "rms": rms(ref), "mean": mean(ref)}}
    L["range_95"] = P().boot_range(ref, n, rule, stat) if n >= 1 and ref else None
    return L


def paired_line(quantity, set_name, n, minimum, a, b):
    return {"quantity": quantity, "set": set_name, "n": n, "minimum": minimum, "scored_at_planned_n": n >= minimum,
            "form": f"paired: the 95% interval of rms({a}) - rms({b}) over the set's tiles drawn with replacement, 20,000 draws",
            "verdict_form": "BETTER if its upper end < 0, WORSE if its lower end > 0, else NOT RESOLVED", "line": "none before the data"}


def fixed_line(quantity, set_name, n, minimum, line):
    return {"quantity": quantity, "set": set_name, "n": n, "minimum": minimum, "scored_at_planned_n": n >= minimum, "line": line,
            "verdict_form": "PASS if the line holds, else FAIL"}


def cover_line(quantity, set_name, n, minimum):
    return {"quantity": quantity, "set": set_name, "n": n, "minimum": minimum, "scored_at_planned_n": n >= minimum,
            "inside_at_least": binom_low(n) if n >= 1 else None, "verdict_form": "PASS if at least that many are inside the band, else FAIL"}


def lg_block(pred):
    """A2-4: LG's groups by reference session, k, n, span, df, F points, and its power at the pool's own D_ref"""
    D = DPG()
    tiles = pred["tiles"]
    groups, multi, none_ = {}, [], []
    for n in pred["sets"]["RR"]:
        refs = tiles[n].get("lg_reference") or []
        if not refs:
            none_.append(n)
            continue
        pick = next((r for r in refs if r.get("tile") == n), refs[0])
        if len(refs) > 1:
            multi.append(n)
        groups.setdefault(pick["session"], []).append((n, float(pick["D_w"])))
    desc = {}
    for s, v in sorted(groups.items()):
        ds = [d for _, d in v]
        desc[s] = {"tiles": [x for x, _ in v], "n": len(v), "D_ref_min_w": min(ds), "D_ref_max_w": max(ds), "span_w": max(ds) - min(ds),
                   "counts": len(v) >= 4 and max(ds) - min(ds) >= 8.0}
    k = sum(1 for d in desc.values() if d["counts"])
    nn = sum(d["n"] for d in desc.values() if d["counts"])
    out = {"quantity": "the float re-runs' level or gain (F tests, registration section 7)", "set": "RR", "n_rr": len(pred["sets"]["RR"]),
           "groups": desc, "k": k, "n": nn, "df": [k, nn - 2 * k], "tiles_with_more_than_one_reference": multi,
           "tiles_with_no_reference": none_, "noise_w": D.NOISE_W,
           "verdict_form": "GAIN / LEVEL / BOTH / NOT SEPARATED (with the null beside); NOT SCORED if no group counts or n - 2k < 4"}
    if k and nn - 2 * k >= 4:
        out["F_point_5pct"] = D.f_ppf(0.95, k, nn - 2 * k)
        out["F_null_point_5pct"] = D.f_ppf(0.95, 2 * k, nn - 2 * k)
        out["power_pct"] = D.power_at({s: [d for _, d in v] for s, v in groups.items()}, D.NOISE_W, D.TRUTHS, 5000,
                                      f"P8-LG|power|{pred['card']}")
        out["power_under_50pct_for"] = [t for t, key in (("gain 0.6%", "GAIN"), ("level 0.11 W", "LEVEL")) if out["power_pct"][t][key] < 50.0]
        out["scored_at_planned_n"] = True
    else:
        out["scored_at_planned_n"] = False
        out["at_the_planned_design"] = "NOT SCORED"
    return out


def lines_600(pred):
    p = P()
    cd = p.CARDS[pred["card"]]
    S, mn, ref = pred["sets"], mins(), p.ref_errors(cd)
    bf = S["by_format"]
    src = {t: f"rows-m10.json err_w[{'B' if t == 'int8' else 'B+a+b'}], {t} rows on {cd}" for t in ("fp32", "fp16", "int8")}
    L = {}
    for rule, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8")):
        L[rule] = boot_line(rule, f"rms(D - M10 primary), {t}", f"N1's {t}", len(bf[t]), ref[t], src[t], mn[rule[3:]], "rms", "W",
                            PASS_RMS + "; below the 2.5% point: better than held out says")
    n32 = sum(1 for n in S["F1"] if pred["tiles"][n]["type"] == "fp32")
    n16 = len(S["F1"]) - n32
    b1 = {"quantity": "mean(D - M10 primary), floats", "set": "F1", "n": len(S["F1"]), "mix": {"fp32": n32, "fp16": n16},
          "minimum": mn["B1"], "scored_at_planned_n": len(S["F1"]) >= mn["B1"], "statistic": "mean", "unit": "W", "seed": p.seed_of("P8-B1"),
          "reference": {"source": "fp32 and fp16 as P8-P1 and P8-P2, the same format mix", "n": {"fp32": len(ref["fp32"]), "fp16": len(ref["fp16"])}},
          "range_95": mix_range({"fp32": ref["fp32"], "fp16": ref["fp16"]}, {"fp32": n32, "fp16": n16}, "P8-B1", "mean"),
          "verdict_form": "PASS inside; FAIL HIGH below (M10 predicts too much); FAIL LOW above"}
    L["P8-B1"] = b1
    L["P8-B2"] = boot_line("P8-B2", "mean(D - M10 primary), int8", "I1", len(S["I1"]), ref["int8"], src["int8"], mn["B2"], "mean", "W",
                           "PASS inside; FAIL HIGH below (M10 predicts too much); FAIL LOW above")
    L["P8-C1"] = cover_line("M10's 95% power band", "N1", len(S["N1"]), mn["C1"])
    L["P8-M1"] = paired_line("M10 primary against M9, both at the measured rate", "N1", len(S["N1"]), mn["M1"], "M10 primary", "M9")
    L["P8-M1f"] = paired_line("the same", "F1", len(S["F1"]), mn["M1f"], "M10 primary", "M9")
    L["P8-M1i"] = paired_line("the same", "I1", len(S["I1"]), mn["M1i"], "M10 primary", "M9")
    L["P8-A1"] = paired_line("the session-scale arm against the a-priori arm (s = 1)", "F1", len(S["F1"]), mn["A1"], "M10 primary", "M10 a priori")
    L["P8-KA"] = {"quantity": "the check anchors: sum e_p^2 < sum e_0^2, and every |e_p| inside M10's 95% band", "set": "KA", "n": len(S["KA"]),
                  "minimum": {"session": mn["KA_session"], "pooled": mn["KA_pooled"]}, "line": "none before the data",
                  "verdict_form": "PASS / FAIL; NOT SCORED if s = 1"}
    rc = p.frozen()["reg"]["bands"]["heat_4p5s"]["rms_c"][cd]
    for rule, t in (("P8-H1", "fp32"), ("P8-H2", "fp16"), ("P8-H3", "int8")):
        L[rule] = boot_line(rule, f"rms(dT_win - M10's 4.5 s rise at its primary D), {t}", f"N1's {t}", len(bf[t]), heat_ref(pred["card"], t),
                            f"2,000 normal draws, Random('P8|heat-reference|{pred['card']}|{t}'), sd {rc[t]} C", mn[rule[3:]], "rms", "C")
    L["P8-H4"] = cover_line("M10's 4.5 s heat band", "N1", len(S["N1"]), mn["H4"])
    L["P8-LG"] = lg_block(pred)
    L["P8-G"] = {"quantity": "M10 generalises on this card", "components": ["P8-P1", "P8-P2", "P8-P3", "P8-B1", "P8-B2", "P8-C1", "P8-M1"],
                 "verdict_form": "PASS if P1, P2, P3, B1, B2 and C1 PASS and M1 is not WORSE; FAIL if any FAILs or M1 is WORSE; else NOT SCORED"}
    L["P8-HM"] = hm_line()
    return L


def hm_line():
    return {"quantity": "heat over minutes: rms(primary, 1.0 x the chain) - rms(arm, 1.032 x), holds rising 10 C or more",
            "minimum": mins()["HM_large_rises"], "planned_holds": 0, "line": "none before the data (paired)",
            "verdict_form": "PRIMARY BETTER / ARM BETTER / NOT RESOLVED; NOT SCORED under 4 such holds (expected: pool 8's sessions hold nothing)"}


def governed_sets(pred):
    """A2-3 (f): N1 less aifoundry2's 82 W admissions; groups by the frozen M10-carried a2_fallback group"""
    S, tiles = pred["sets"], pred["tiles"]
    out82 = sorted(n for n in S["N1"] if tiles[n].get("admission_82w_out"))
    scored = [n for n in S["N1"] if n not in set(out82)]
    gov = [n for n in scored if tiles[n]["M10"]["a2_fallback"]["group"] == "governed"]
    pin = [n for n in scored if tiles[n]["M10"]["a2_fallback"]["group"] == "pinned"]
    return scored, gov, pin, out82


def lines_a2(pred):
    mn, R = mins(), e165_refs()
    scored, gov, pin, out82 = governed_sets(pred)
    src = "tools/claims-v3/e165/predictions-e165.json reference"
    L = {"_sets": {"scored": len(scored), "governed": len(gov), "pinned": len(pin), "left_out_82w": out82}}
    L["P8-A2-G"] = fixed_line("burst clock, M10 carried", "governed", len(gov), mn["A2_group"], "rms <= 4.0 MHz AND |mean| <= 2.0 MHz")
    L["P8-A2-Bg"] = fixed_line("board W", "governed", len(gov), mn["A2_group"], "|mean| <= 0.5 W")
    L["P8-A2-Bp"] = fixed_line("board W", "pinned", len(pin), mn["A2_group"], "|mean| <= 0.5 W AND rms <= 1.0 W")
    L["P8-A2-R2"] = {"quantity": "rank 2 on M10 carried", "components": ["P8-A2-G", "P8-A2-Bg", "P8-A2-Bp"],
                     "verdict_form": "PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED"}
    L["P8-A2-F1"] = boot_line("P8-A2-F1", "burst clock", "governed", len(gov), R["gov_mhz"], src + ".e2e.governed.mhz_err", mn["A2_group"], "rms", "MHz")
    L["P8-A2-F2"] = boot_line("P8-A2-F2", "burst clock", "pinned", len(pin), R["pin_mhz"], src + ".e2e.pinned.mhz_err", mn["A2_group"], "rms", "MHz")
    L["P8-A2-W1"] = boot_line("P8-A2-W1", "board W", "governed", len(gov), R["gov_w"], src + ".e2e.governed.w_err", mn["A2_group"], "rms", "W")
    L["P8-A2-W2"] = boot_line("P8-A2-W2", "board W", "pinned", len(pin), R["pin_w"], src + ".e2e.pinned.w_err", mn["A2_group"], "rms", "W")
    L["P8-A2-M1"] = paired_line("board W: M10 carried against M9's part on M9's D", "all scored", len(scored), mn["A2_all"], "M10 carried", "M9")
    L["P8-A2-H1"] = boot_line("P8-A2-H1", "burst die rise, aifoundry2's own law", "all scored", len(scored), R["heat_c"], src + ".heat.rise_err_c",
                              mn["A2_all"], "rms", "C")
    L["P8-HM"] = hm_line()
    return L


def lines_c0(pred):
    mn, R = mins(), e165_refs()
    scored = list(pred["sets"]["N1"])
    src = "tools/claims-v3/e165/predictions-e165.json reference"
    b = c0_band()
    L = {"_sets": {"scored": len(scored)}, "_m10_card0_rise_band": {"hw_c": b["hw_c"], "n_residuals": b["n"], "reported": "no rule reads it (A2-1)"}}
    L["P8-C0-W"] = boot_line("P8-C0-W", "board W, M10 carried through the card term", "every scored tile", len(scored), R["pin_w"],
                             src + ".e2e.pinned.w_err", mn["C0"], "rms", "W")
    L["P8-C0-B"] = fixed_line("the same errors", "every scored tile", len(scored), mn["C0"], "|mean| <= 0.5 W AND rms <= 1.0 W")
    L["P8-C0-M1"] = paired_line("burst D: M10 carried against M9 carried", "every scored tile", len(scored), mn["C0_M1"], "M10 carried", "M9 carried")
    L["P8-C0-F"] = boot_line("P8-C0-F", "burst clock", "every scored tile", len(scored), R["pin_mhz"], src + ".e2e.pinned.mhz_err", mn["C0"], "rms", "MHz",
                             PASS_RMS + " (dated note A2-5)")
    L["P8-C0-H1"] = boot_line("P8-C0-H1", "die rise, M10's 0.2415 C/W on the predicted board", "every scored tile", len(scored), b["residuals_c"],
                              "term c2's 39 leave-one-tile-out residuals on E170 (predict_pool8.t6_card0)", mn["C0"], "rms", "C")
    L["P8-C0-HK"] = paired_line("die rise at the measured board: M10's k against M9's 0.1400", "every scored tile", len(scored), mn["C0"],
                                "M10's k", "M9's k")
    L["P8-HM"] = hm_line()
    return L


def intervals_for(pred):
    p = P()
    cd = p.CARDS[pred["card"]]
    L = lines_600(pred) if cd in ("a3", "c1") else lines_a2(pred) if cd == "a2" else lines_c0(pred)
    return {"card": pred["card"], "rules": L}


def intervals(paths):
    p = P()
    p.check_inputs()
    out = {"_note": f"Q142(p) predict_pool8_a2.py intervals: every section-7 line at the pool's own n (dated note A2-3, A2-4; lab {A2_COMMIT}). "
                    "A verdict reads the line at its scored n, from the same function and seed; these are the forecasts at the planned n.",
           "a2_commit": A2_COMMIT, "predictor_commit": FROZEN_COMMIT, "this_file_sha256": fsha(os.path.abspath(__file__)), "cards": {}}
    for q in paths:
        pred = load(q)
        out["cards"][pred["card"]] = dict(intervals_for(pred), predictions=rel(q), predictions_sha256=fsha(q))
    return out


# ------------------------------------------------------------------ self-test
def _pool(tmp, label, names, anchors=()):
    p = P()
    man7 = {m["name"]: m for m in load(os.path.join(p.B7, "blind7.json"))["tiles"]}
    d = os.path.join(tmp, label)
    for n in names:
        os.makedirs(os.path.join(d, os.path.dirname(man7[n]["file"])), exist_ok=True)
        shutil.copyfile(os.path.join(p.B7, man7[n]["file"]), os.path.join(d, man7[n]["file"]))
    json.dump({"tiles": [dict(man7[n], anchor=True) if n in anchors else man7[n] for n in names]}, open(os.path.join(d, "blind8.json"), "w"))
    return d


def _cli(script, args, timeout=600):
    r = subprocess.run([sys.executable, "-B", script] + args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()


def _msg(txt):
    ls = [x.strip() for x in txt.splitlines() if x.strip()]
    for key in ("refused_point", "POOL8 STOPPED", "POOL8-A2 STOPPED", "anchor roles", "convergence rule", "REFUSED"):
        for x in ls:
            if key in x:
                return x[:220]
    return ls[-1][:220] if ls else ""


def u1_frozen_rerun():
    """the frozen self-test, T1-T9, re-run in its own process, unchanged; its output must equal the committed selftest-pool8.json"""
    tmp = tempfile.mkdtemp(prefix="pool8-a2-u1-")
    try:
        o = os.path.join(tmp, "selftest-pool8.json")
        rc, txt = _cli(FROZEN_PY, ["selftest", "--out", o], timeout=900)
        got = load(o) if os.path.exists(o) else {}
        want = load(FROZEN_SELFTEST)
        diff = sorted(k for k in set(got) | set(want) if got.get(k) != want.get(k))
        return {"rc": rc, "summary": txt.splitlines()[-1] if txt else "", "identical_to_committed": not diff, "keys_differing": diff,
                "pass": rc == 0 and not diff and bool(got.get("PASS"))}
    finally:
        shutil.rmtree(tmp)


def u2_exit_codes():
    """A2-2 and fault 11: both files' command lines on temporary pools with writes enabled; each exit status, and no predictions file"""
    p = P()
    tmp = tempfile.mkdtemp(prefix="pool8-a2-u2-")
    try:
        c7 = os.path.join(p.B7, "counts-blind7.json")
        row = load(c7)["rows"]["fp32.b_onebit_b20_one"]
        cm, tw = copy.deepcopy(row), copy.deepcopy(row)
        cm["points"][0]["check_mismatch"] = True
        tw["points"][0]["counted_again"] = True
        f_cm, f_tw = os.path.join(tmp, "counts-mismatch.json"), os.path.join(tmp, "counts-twice.json")
        json.dump({"rows": {"fp32.b_onebit_b20_one": cm}}, open(f_cm, "w"))
        json.dump({"rows": {"fp32.b_onebit_b20_one": tw}}, open(f_tw, "w"))
        A = _pool(tmp, "pool-a", ["fp32.b_onebit_b20_one", "int8.bheld_33"])
        I8 = _pool(tmp, "pool-i", ["int8.bheld_33"])
        R = _pool(tmp, "pool-r", ["fp32.anchor7_zeros", "fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp32.uniform_pm1"], {"fp32.uniform_pm1"})
        me = os.path.abspath(__file__)
        cases = [("points short of the convergence rule's N", "predict", A, [c7], {"frozen": 3, "a2": 3}),
                 ("a point with a check_mismatch", "predict", A, [c7, f_cm], {"frozen": 1, "a2": 3}),
                 ("a point counted twice with different records", "predict", A, [c7, f_tw], {"frozen": 1, "a2": 3}),
                 ("random anchors' roles unreadable", "predict", R, [c7], {"frozen": 3, "a2": 3}),
                 ("plan: a point with a check_mismatch", "plan", A, [c7, f_cm], {"frozen": 1, "a2": 3}),
                 ("an int8 tile with its three points (control)", "predict", I8, [c7], {"frozen": 0, "a2": 0})]
        out, ok = {}, True
        for i, (lab, mode, pool, counts, want) in enumerate(cases):
            out[lab] = {}
            for who, script in (("frozen", FROZEN_PY), ("a2", me)):
                od = os.path.join(tmp, f"out-{i}-{who}")
                os.makedirs(od)
                args = [mode, pool] + (["aifoundry3"] if mode == "predict" else [])
                for c in counts:
                    args += ["--counts", c]
                args += ["--no-reuse"] + (["--out", od] if mode == "predict" else [])
                rc, txt = _cli(script, args)
                wrote = sorted(os.path.basename(x) for x in glob.glob(os.path.join(od, "*")) + glob.glob(os.path.join(pool, "predictions-*")))
                out[lab][who] = {"rc": rc, "expected_rc": want[who], "files_written": wrote, "message": _msg(txt)}
                good = rc == want[who] and (bool(wrote) == (rc == 0 and mode == "predict"))
                out[lab][who]["ok"] = good
                ok = ok and good
        ctl = [os.path.join(tmp, "out-5-frozen", "predictions-pool8-aifoundry3.json"), os.path.join(tmp, "out-5-a2", "predictions-pool8-aifoundry3.json")]
        same = all(os.path.exists(x) for x in ctl) and fsha(ctl[0]) == fsha(ctl[1])
        out["control: predictions bytes identical between the two files"] = same
        rc, txt = _cli(me, ["heat-minutes", "10.0"])
        hm = json.loads(txt.splitlines()[-1]) if rc == 0 else {}
        hok = rc == 0 and hm.get("primary_c") == [10.0] and abs(hm.get("arm_c", [0])[0] - 10.3199) < 1e-9
        out["pass-through: heat-minutes 10.0"] = {"rc": rc, "primary_c": hm.get("primary_c"), "arm_c": hm.get("arm_c"), "ok": hok}
        return {"cases": out, "pass": bool(ok and same and hok)}
    finally:
        shutil.rmtree(tmp)


def u3_card0_band():
    """A2-1: on E170's committed reads, burst through this file against predict_pool8.burst"""
    p = P()
    g = p.frozen()
    tmp = tempfile.mkdtemp(prefix="pool8-a2-u3-")
    try:
        pool = _pool(tmp, "pool", T9_NAMES)
        c7 = [os.path.join(p.B7, "counts-blind7.json")]
        p.predict(pool, "aifoundry1c0", c7, reuse=True, out_dir=tmp)
        pj = load(os.path.join(tmp, "predictions-pool8-aifoundry1c0.json"))
        e = load(E170_RES)
        tiles = e["score"]["reported"]["tiles"]
        ds = {n: tiles[n]["die_starts"] for n in T9_NAMES if n in tiles}
        fr = p.burst(pj, e["score"]["anchors"], ds)
        mine = burst(pj, e["score"]["anchors"], ds)
        b = c0_band()
        committed = load(FROZEN_SELFTEST)["T6"]["c0_h1_reference_residuals_c"]
        s = sorted(abs(x) for x in b["residuals_c"])
        h = (len(s) - 1) * 0.95
        lo = int(math.floor(h))
        hw_lin = s[lo] + (h - lo) * (s[min(lo + 1, len(s) - 1)] - s[lo])
        bad, rows = [], {}
        for n in ds:
            a, f = mine["tiles"][n], fr["tiles"][n]
            if a["M9"] != f["M9"]:
                bad.append(f"{n}: M9 block differs")
            m10, f10 = a["M10"], f["M10"]
            for k, v in f10.items():
                if k != "burst_die_rise_95" and m10.get(k) != v:
                    bad.append(f"{n}: M10.{k} differs")
            if m10["burst_die_rise_95_M9_law"] != f10["burst_die_rise_95"]:
                bad.append(f"{n}: the M9-law band is not the frozen field")
            R = g["P10"].rise_card0_burst(m10["burst_board_w"], g["m10"])
            band = m10["burst_die_rise_95"]
            if band != [round(R - b["hw_c"], 3), round(R + b["hw_c"], 3)] or not band[0] <= m10["burst_die_rise_c"] <= band[1]:
                bad.append(f"{n}: M10's band")
            if not (f10["burst_die_rise_95"][0] <= f10["burst_die_rise_c"] <= f10["burst_die_rise_95"][1]):
                rows[n] = {"M10_rise_c": m10["burst_die_rise_c"], "M10_band": band, "frozen_band_M9_law": f10["burst_die_rise_95"],
                           "frozen_band_contains_the_rise": False}
            else:
                rows[n] = {"M10_rise_c": m10["burst_die_rise_c"], "M10_band": band, "frozen_band_M9_law": f10["burst_die_rise_95"],
                           "frozen_band_contains_the_rise": True}
        inside = sum(1 for r in b["residuals_c"] if abs(r) <= b["hw_c"])
        ok = (not bad and len(ds) >= 6 and b["residuals_c"] == [float(x) for x in committed] and b["n"] == 39
              and abs(b["hw_c"] - hw_lin) < 1e-12 and round(b["loto_rms_c"], 4) == 0.3385)
        return {"tiles": len(ds), "hw_c": b["hw_c"], "hw_c_stdlib_linear": hw_lin, "residuals_n": b["n"], "loto_rms_c": b["loto_rms_c"],
                "residuals_equal_committed_T6": b["residuals_c"] == [float(x) for x in committed],
                "in_sample_inside_hw_at_measured_board": f"{inside} of {b['n']}",
                "frozen_band_excludes_M10_rise_on": sorted(n for n, r in rows.items() if not r["frozen_band_contains_the_rise"]),
                "by_tile": rows, "faults": bad, "pass": bool(ok)}
    finally:
        shutil.rmtree(tmp)


REGISTERED_REFS = {("a3", "fp32"): (260, 0.2019), ("a3", "fp16"): (133, 0.1476), ("a3", "int8"): (114, 0.1696),
                   ("c1", "fp32"): (190, 0.2004), ("c1", "fp16"): (154, 0.1651), ("c1", "int8"): (108, 0.1849)}


def _as_all_new(pred):
    """a test copy of a predictions dict whose every non-anchor tile is put in N1 (the self-test's committed tiles are all pool-7
    re-runs, so the real N1 is empty); both intervals functions then read the same sets"""
    q = copy.deepcopy(pred)
    names = sorted(n for n, r in q["tiles"].items() if not r["anchor_role"])
    q["sets"]["N1"] = names
    q["sets"]["F1"] = [n for n in names if q["tiles"][n]["type"] in ("fp32", "fp16")]
    q["sets"]["I1"] = [n for n in names if q["tiles"][n]["type"] == "int8"]
    q["sets"]["by_format"] = {t: [n for n in names if q["tiles"][n]["type"] == t] for t in ("fp32", "fp16", "int8")}
    return q


def u4_intervals():
    """A2-3: every rule's line on four cards' predictions of committed tiles; P1-P3 equal predict_pool8.intervals; the references
    equal the registered figures; the heat references; LG's block on the real sets"""
    p = P()
    tmp = tempfile.mkdtemp(prefix="pool8-a2-u4-")
    try:
        pool = _pool(tmp, "pool", T9_NAMES)
        c7 = [os.path.join(p.B7, "counts-blind7.json")]
        out, ok = {"cards": {}}, True
        for card in ("aifoundry3", "aifoundry1c1", "aifoundry2", "aifoundry1c0"):
            p.predict(pool, card, c7, reuse=True, out_dir=tmp)
            real = load(os.path.join(tmp, f"predictions-pool8-{card}.json"))
            test = _as_all_new(real)
            L = intervals_for(test)["rules"]
            want = RULES_600 if card in ("aifoundry3", "aifoundry1c1") else RULES_A2 + ["P8-HM"] if card == "aifoundry2" else RULES_C0 + ["P8-HM"]
            missing = [r for r in want if r not in L]
            rec = {"rules": len([k for k in L if not k.startswith("_")]), "missing": missing,
                   "lines": {r: (L[r].get("range_95") or L[r].get("inside_at_least")) for r in L if not r.startswith("_") and isinstance(L[r], dict)
                             and (L[r].get("range_95") is not None or L[r].get("inside_at_least") is not None)},
                   "n": {r: L[r].get("n") for r in L if not r.startswith("_") and isinstance(L[r], dict) and "n" in L[r]}}
            good = not missing
            if card in ("aifoundry3", "aifoundry1c1"):
                cd = p.CARDS[card]
                fz = p.intervals(test)
                same = all(fz[r]["rms_95"] == L[r]["range_95"] and fz[r]["n"] == L[r]["n"] for r in ("P8-P1", "P8-P2", "P8-P3") if r in fz)
                refs = {t: (L[r]["reference"]["n"], round(L[r]["reference"]["rms"], 4)) for r, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8"))}
                refok = all(refs[t] == REGISTERED_REFS[(cd, t)] for t in refs)
                h = {t: heat_ref(card, t) for t in ("fp32", "fp16", "int8")}
                hrc = p.frozen()["reg"]["bands"]["heat_4p5s"]["rms_c"][cd]
                hok = all(abs(rms(h[t]) / hrc[t] - 1.0) < 0.06 and h[t] == heat_ref(card, t) and len(h[t]) == 2000 for t in h)
                one = mix_range({"fp32": p.ref_errors(cd)["fp32"]}, {"fp32": 6}, "P8-P1") == p.boot_range(p.ref_errors(cd)["fp32"], 6, "P8-P1")
                lg = lines_600(real)["P8-LG"]
                rec.update({"P1_P3_equal_predict_pool8_intervals": same and len(fz) == 3, "references": refs, "references_as_registered": refok,
                            "heat_reference_rms_over_registered": {t: rms(h[t]) / hrc[t] for t in h}, "heat_reference_ok": hok,
                            "single_format_mix_equals_boot_range": one,
                            "LG_on_the_real_sets": {k: lg[k] for k in ("n_rr", "k", "n", "df", "groups", "power_pct", "F_point_5pct",
                                                                         "tiles_with_no_reference") if k in lg}})
                good = good and same and len(fz) == 3 and refok and hok and one and lg["n_rr"] == 8
            elif card == "aifoundry2":
                R = e165_refs()
                eok = (len(R["gov_mhz"]) == 36 and round(rms(R["gov_mhz"]), 2) == 4.50 and round(rms(R["gov_w"]), 2) == 0.78
                       and len(R["pin_mhz"]) == 42 and round(rms(R["pin_mhz"]), 2) == 2.33 and round(rms(R["pin_w"]), 2) == 0.82
                       and len(R["heat_c"]) == 112 and round(rms(R["heat_c"]), 4) == 0.6845)
                sc, gov, pin, out82 = governed_sets(test)
                rec.update({"e165_references_as_registered": eok, "groups": {"governed": len(gov), "pinned": len(pin), "left_out_82w": out82}})
                good = good and eok and len(gov) + len(pin) + len(out82) == len(test["sets"]["N1"])
            else:
                R = e165_refs()
                b = c0_band()
                cok = round(rms(R["pin_w"]), 4) == 0.8214 and round(rms(R["pin_mhz"]), 3) == 2.334 and b["n"] == 39 and round(rms(b["residuals_c"]), 4) == 0.3385
                rec["c0_references_as_registered"] = cok
                good = good and cok
            iv = intervals([os.path.join(tmp, f"predictions-pool8-{card}.json")])
            ivk = sorted(k for k in iv["cards"][card]["rules"] if not k.startswith("_"))
            rec["intervals_end_to_end_rules"] = len(ivk)
            good = good and ivk == sorted(want) and iv["cards"][card]["predictions_sha256"] == fsha(os.path.join(tmp, f"predictions-pool8-{card}.json"))
            rec["pass"] = bool(good)
            out["cards"][card] = rec
            ok = ok and good
        out["pass"] = bool(ok)
        return out
    finally:
        shutil.rmtree(tmp)


def u5_engine():
    """the bootstrap engine against committed outputs: E164's registered precision (its references, seeds and draws) reproduced by
    mix_range, and the coverage line against E164's committed one and E165's coverage_line"""
    p = P()
    pre = load(os.path.join(E164D, "predictions-e164.json"))["precision_before_data"]
    rer = load(os.path.join(E164D, "ref-errors-m9.json"))
    F = ("fp32", "fp16", "int8")
    p_ref = {f: rer["card1_by_format"][f] for f in F}
    m9 = load(os.path.join(p.M9D, "m9.json"))
    hp = m9["heat"]["interval_pool_by_format_card_c"]
    h_rms = {f: hp[f"{f}|aifoundry1-c1"]["rms_c"] for f in F}
    rng = random.Random("E164|heat-reference")
    h_ref = {f: [rng.gauss(0.0, h_rms[f]) for _ in range(2000)] for f in F}
    got = {}
    for rid, f, seed in (("E164-P1", "fp32", 1), ("E164-P2", "fp16", 1), ("E164-P3", "int8", 1)):
        got[rid] = [round(x, 4) for x in mix_range(p_ref, {f: pre[rid]["tiles"]}, stat="rms", draws=4000, seed=seed, median=True)]
    got["E164-B1"] = [round(x, 4) for x in mix_range(p_ref, {"fp32": pre["E164-P1"]["tiles"], "fp16": pre["E164-P2"]["tiles"]}, stat="mean",
                                                    draws=4000, seed=2, median=True)]
    got["E164-B2"] = [round(x, 4) for x in mix_range(p_ref, {"int8": pre["E164-B2"]["tiles"]}, stat="mean", draws=4000, seed=3, median=True)]
    for rid, f in (("E164-H1", "fp32"), ("E164-H2", "fp16"), ("E164-H3", "int8")):
        got[rid] = [round(x, 4) for x in mix_range(h_ref, {f: pre[rid]["tiles"]}, stat="rms", draws=4000, seed=4, median=True)]
    want = {r: pre[r].get("rms_interval_W") or pre[r].get("mean_interval_W") or pre[r].get("rms_interval_C") for r in got}
    same = {r: got[r] == want[r] for r in got}
    if str(os.path.join(ROOT, "tools", "claims-v3", "e165")) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e165"))
    import e165_common as C165  # noqa: E402  (already imported by the predictor's aifoundry2 path; its sha256 is in POOL8-SHA256SUMS)
    cov = all(binom_low(n) == C165.coverage_line(n) for n in range(0, 201))
    return {"E164_precision_reproduced": same, "got": got, "committed": want, "binom_low_equals_e165_coverage_line_n_0_200": cov,
            "binom_low_48": binom_low(48), "E164_committed_48": pre["E164-C1"]["binomial_low_2p5"],
            "pass": all(same.values()) and len(same) == 8 and cov and binom_low(48) == pre["E164-C1"]["binomial_low_2p5"] == 42}


def u6_lg():
    """A2-4: the registered F tests in closed form against numpy's least squares; the F points; design_power.py's n = 8 block replayed;
    the groups read from a predictions file"""
    import numpy as np
    D = DPG()

    def np_F(groups):
        cnt = {r: g for r, g in groups.items() if len(g) >= 4 and max(x for x, _ in g) - min(x for x, _ in g) >= 8.0}
        rs = sorted(cnt)
        x = np.array([d for r in rs for d, _ in cnt[r]])
        y = np.array([v for r in rs for _, v in cnt[r]])
        gi = np.array([i for i, r in enumerate(rs) for _ in cnt[r]])
        A = np.stack([(gi == i).astype(float) for i in range(len(rs))], 1)
        Gm = np.stack([(gi == i) * x for i in range(len(rs))], 1)

        def rss(X):
            b = np.linalg.lstsq(X, y, rcond=None)[0]
            e = y - X @ b
            return float(e @ e)
        k, n = len(rs), len(y)
        full = rss(np.hstack([A, Gm]))
        s2 = full / (n - 2 * k)
        return {"F_slope": (rss(A) - full) / k / s2, "F_level": (rss(Gm) - full) / k / s2, "F_null": (float(y @ y) - full) / (2 * k) / s2}

    sig, ntile, _, sets = D.noise_from_reruns(ROOT)
    tests = {"committed re-runs (E163 vs E141 and E152, E164 vs E157)": {nm: [(r[1], r[2]) for r in rows] for nm, rows in sets.items()}}
    rng = random.Random(1428)
    for k in (1, 2, 3):
        gr = {}
        for i in range(k):
            m = 6 + 2 * i
            gr[f"g{i}"] = [(5.0 + 20.0 * (j + rng.random()) / m, rng.gauss(0.05, 0.04) + 0.002 * i * j) for j in range(m)]
        tests[f"random, k {k}"] = gr
    worst = 0.0
    fstats = {}
    for lab, gr in tests.items():
        a = D.lg_test(gr, detail=True)
        b = np_F(gr)
        for key in ("F_slope", "F_level", "F_null"):
            worst = max(worst, abs(a[key] - b[key]) / max(1.0, abs(b[key])))
        fstats[lab] = {"k": a["k"], "n": a["n"], "verdict": a["verdict"], "F_slope": a["F_slope"], "F_level": a["F_level"]}
    tab = {(1, 6): 5.9874, (1, 10): 4.9646, (2, 8): 4.4590, (3, 6): 4.7571, (2, 10): 4.1028, (4, 8): 3.8379, (6, 6): 4.2839}
    ftab = max(abs(D.f_ppf(0.95, a_, b_) - v) for (a_, b_), v in tab.items())
    # design_power.py's n = 8 block, its own stream and its t point at 6 df (2.447) squared
    lines = []
    r2 = random.Random(142)
    for noise in (sig, 1.5 * sig):
        for lab, a0, g0 in (("none", 0.0, 0.0), ("gain 0.3%", 0.0, 0.003), ("gain 0.6%", 0.0, 0.006), ("gain 1.0%", 0.0, 0.010),
                            ("level 0.05 W", 0.05, 0.0), ("level 0.11 W", 0.11, 0.0), ("level 0.15 W", 0.15, 0.0)):
            c = D.power([("even", 8, 5.0, 25.0)], a0, g0, noise, 5000, r2, crit=2.447 ** 2)
            cnt = {"GAIN": c["GAIN"], "LEVEL": c["LEVEL"], "BOTH": c["BOTH"], "NEITHER": c["NOT SEPARATED"] + c["NOT SCORED"]}
            lines.append(f"   n  8, noise {noise:.4f} W, truth {lab:13s}: " + ", ".join(f"{k} {v / 50:.0f}%" for k, v in cnt.items()))
    committed = [ln for ln in open(os.path.join(DPG_DIR, "design-power.txt")).read().splitlines() if ln.startswith("   n  8,")]
    replay = lines == committed
    # the groups read from a predictions file
    fake = {"card": "aifoundry3", "sets": {"RR": [f"fp32.r{i}" for i in range(10)]}, "tiles": {}}
    for i in range(6):
        fake["tiles"][f"fp32.r{i}"] = {"lg_reference": [{"session": "E163", "tile": f"fp32.r{i}", "D_w": 8.0 + 2.5 * i}]}
    for i in (6, 7):
        fake["tiles"][f"fp32.r{i}"] = {"lg_reference": [{"session": "E153", "tile": f"fp32.r{i}", "D_w": 15.0 + i}]}
    fake["tiles"]["fp32.r8"] = {"lg_reference": [{"session": "E153", "tile": "fp32.other", "D_w": 20.0},
                                                 {"session": "E163", "tile": "fp32.r8", "D_w": 21.0}]}
    fake["tiles"]["fp32.r9"] = {"lg_reference": []}
    lb = lg_block(fake)
    gok = (lb["groups"]["E163"]["n"] == 7 and lb["groups"]["E153"]["n"] == 2 and not lb["groups"]["E153"]["counts"] and lb["k"] == 1
           and lb["n"] == 7 and lb["df"] == [1, 5] and lb["tiles_with_more_than_one_reference"] == ["fp32.r8"]
           and lb["tiles_with_no_reference"] == ["fp32.r9"] and "power_pct" in lb)
    ok = worst < 1e-9 and ftab < 5e-5 and replay and len(committed) == 14 and gok and round(sig, 4) == 0.0368 and ntile == 17
    return {"noise_w": sig, "noise_tiles": ntile, "closed_form_vs_numpy_max_rel_diff": worst, "F_tests": fstats, "F_points_max_diff_vs_table": ftab,
            "design_power_n8_block_replayed_identical": replay, "replayed_lines": len(lines),
            "groups_from_predictions": {k: lb[k] for k in ("groups", "k", "n", "df", "tiles_with_more_than_one_reference", "tiles_with_no_reference", "power_pct")},
            "pass": bool(ok)}


def selftest():
    opened = set()
    _open, _gz = builtins.open, gzip.open

    def note(p):
        try:
            a = os.path.abspath(os.fspath(p))
            if a.startswith(ROOT + os.sep) and os.path.isfile(a):
                opened.add(os.path.relpath(a, ROOT))
        except TypeError:
            pass

    def topen(p, *a, **k):
        note(p)
        return _open(p, *a, **k)

    def tgz(p, *a, **k):
        note(p)
        return _gz(p, *a, **k)
    builtins.open, io.open, gzip.open = topen, topen, tgz
    res = {}
    try:
        lists = check_lists()
        p = P()
        res["U0"] = {"lists": lists, "POOL8-SHA256SUMS": p.check_inputs(), "frozen_predictor_sha256": fsha(FROZEN_PY), "pass": True}
        res["U1"] = u1_frozen_rerun()
        res["U2"] = u2_exit_codes()
        res["U3"] = u3_card0_band()
        res["U4"] = u4_intervals()
        res["U5"] = u5_engine()
        res["U6"] = u6_lg()
    finally:
        builtins.open, io.open, gzip.open = _open, _open, _gz
    mods = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and os.path.abspath(f).startswith(ROOT + os.sep):
            mods.add(os.path.relpath(os.path.abspath(f), ROOT))
    seen = sorted((opened | mods) - {rel(A2_SUMS), rel(OWN_SUMS), rel(REG_SUMS)})
    listed = {}
    for lst in (REG_SUMS, OWN_SUMS, A2_SUMS):
        listed.update({os.path.relpath(q, ROOT): h for q, h in read_sums(lst).items()})
    unlisted = [q for q in seen if q not in listed]
    badh = [q for q, h in listed.items() if not os.path.isfile(os.path.join(ROOT, q)) or fsha(os.path.join(ROOT, q)) != h]
    res["U7"] = {"files_opened_or_imported": len(seen), "unlisted": unlisted, "listed_entries": len(listed), "listed_bad": badh,
                 "pass": not unlisted and not badh}
    res["PASS"] = all(v.get("pass") for k, v in res.items() if k.startswith("U"))
    return res


# ------------------------------------------------------------------ main
def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("scale", "primary", "heat-minutes"):
        return P().main()
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predict")
    p.add_argument("pool")
    p.add_argument("card", choices=["aifoundry1c0", "aifoundry1c1", "aifoundry2", "aifoundry3"])
    p.add_argument("--counts", action="append", required=True)
    p.add_argument("--roles")
    p.add_argument("--no-reuse", action="store_true")
    p.add_argument("--out")
    q = sub.add_parser("plan")
    q.add_argument("pool")
    q.add_argument("--counts", action="append", default=[])
    q.add_argument("--no-reuse", action="store_true")
    b = sub.add_parser("burst")
    b.add_argument("predictions")
    b.add_argument("--anchors", required=True)
    b.add_argument("--die-starts", required=True)
    b.add_argument("--out")
    i = sub.add_parser("intervals")
    i.add_argument("predictions", nargs="+")
    i.add_argument("--out")
    t = sub.add_parser("selftest")
    t.add_argument("--out")
    a = ap.parse_args()
    if a.cmd in ("predict", "plan"):
        fz = P()
        if a.cmd == "predict":
            o, why = mapped(fz.predict, os.path.abspath(a.pool), a.card, [os.path.abspath(c) for c in a.counts], a.roles, not a.no_reuse, a.out)
        else:
            o, why = mapped(fz.plan, os.path.abspath(a.pool), [os.path.abspath(c) for c in a.counts], not a.no_reuse)
        if why is not None:
            print("REFUSED (registration sections 2-3; dated note A2-2); nothing written:\n" + why)
            return 3
        print(fz.summary_md(o) if a.cmd == "predict" else json.dumps(o, indent=1, sort_keys=True))
        return 0
    if a.cmd in ("burst", "intervals"):
        o = burst(load(a.predictions), load(a.anchors), load(a.die_starts)) if a.cmd == "burst" else intervals(a.predictions)
        s_ = json.dumps(o, indent=1, sort_keys=True)
        if a.out:
            open(a.out, "w").write(s_ + "\n")
        print(s_)
        return 0
    res = selftest()
    s_ = json.dumps(res, indent=1, sort_keys=True, default=str)
    if a.out:
        open(a.out, "w").write(s_ + "\n")
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) and "pass" in v else v) for k, v in res.items()}, sort_keys=True))
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
