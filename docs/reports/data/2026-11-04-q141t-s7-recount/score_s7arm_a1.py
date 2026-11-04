#!/usr/bin/env python3
"""Q141(t), amendment A1: the reported arm M9_27pt's readings with REGISTRATION.md.dated-note-2.md applied (written and committed
before any pool-7 data). score_s7arm.py, frozen in 67d5e44f, is imported unchanged; this file changes only what A1 names. The frozen
scorer and its committed self-test stay as they are.

    python3 -B score_s7arm_a1.py --a3 <E163 scored.json> --c1 <E164 scored.json> [--out score-s7arm-a1.json]   # either card, or both
    python3 -B score_s7arm_a1.py --selftest [--work <scratch dir>] [--out selftest-score-s7arm-a1.json] > selftest-score-s7arm-a1.txt

A1-1  R5's gate. R5 is read only on a card whose R2-R4 are read (at least 5 of the 7 S7 tiles measured, REGISTRATION.md section 3)
      and where all four fp32 bit-20 tiles are measured: the registered statistic, four tiles, 3 df, chi2 > 7.815. Where R2-R4 are
      read and exactly 3 of the 4 are measured, R5 is "not read", and the same statistic over the three (2 df) is reported beside it
      as the named departure R5-3: reported only, never read as a base-word price.
A1-2  Heat's R1 and R2, registered in section 3 as "the same R1 and R2 on M9's dT_win at 3 and 27 points".
      R1 per tile adds k_dT = dT3 - dT27 +- u_dT, with u_dT = g x u (g = M7's frozen coefficient on S for the card: the heat law M9
      carries is dT_win = g x S, and S - D does not depend on the counts), sigma_dT = sqrt(u_dT^2 + se^2), the flag
      |r27| <= 2 sigma_dT, and the run's M9 dT_win pred checked against dT3.
      R2 per card and pooled: n; rms and mean of r3 and r27; d_rms = rms(r27) - rms(r3) and mean(r27), each with a 95% percentile
      interval from power R2's paired bootstrap over tiles (score_s7arm.boot: 20,000 draws, seed 141 on aifoundry3, 142 on card 1,
      143 pooled), with at least 5 of the 7 S7 tiles carrying a measured rise.
A1-3  R5m, reported beside R5 and never in place of it: the same statistic on the same tiles under the same gate, with M9's frozen
      fp32 band pool rms for the card (m9.json interval_pool_by_format_card: 0.2001 W on aifoundry3, 0.2112 W on card 1) added in
      quadrature to each sigma. It asks whether the bit-20 tiles' r27 scatter beyond counting, measurement AND M9's ordinary per-tile
      error. The self-test (T4) reports how often R5 and R5m read a base-word price when none exists, and how often for a 0.6 W one.
Everything else is score_s7arm.py's output, unchanged: R1 (power), R2-R4 per card and pooled, R6, the missing list and the flags.
Reported only: no verdict on M9, no PASS or FAIL on any reading; M9's frozen predictions stay primary. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_s7arm as S  # noqa: E402  (frozen in 67d5e44f; imported unchanged)

TOP, DD = S.TOP, S.DD
M9J = os.path.join(DD, "2026-11-04-q140m-m9", "m9.json")
ROWS9 = os.path.join(DD, "2026-11-04-q140m-m9", "rows-m9.json")
M7J = os.path.join(DD, "2026-11-02-q138m-model", "m7.json")
REL = lambda p: os.path.relpath(p, TOP)  # noqa: E731
FROZEN = {  # sha256 of every committed input this file reads, with the commit that froze it
    os.path.join(HERE, "score_s7arm.py"): ("fa8c8cf6fbde1e14e9900888938b68c58bcb8ebf3fc4c756aac8718e05e116df", "67d5e44f"),
    os.path.join(HERE, "arm-s7.json"): ("bac7c2c3b6994f6bfee12d66f1be7f4a08a9aec3635a25950e156762f23ca546", "67d5e44f"),
    os.path.join(HERE, "selftest-score-s7arm.txt"): ("508ab30e965f4c783a1148edcb423b8cfa3fb9ce3f6dcf624a2d34ca7690d36a", "67d5e44f"),
    os.path.join(HERE, "arm", "arm27-aifoundry3.json"): ("8db1a78e0e5d570ca52028f92ee7e1afdd03d24884b3b458b30293b7603ff05e", "67d5e44f"),
    os.path.join(HERE, "arm", "arm27-aifoundry1c1.json"): ("46c43c1aae1a0bf796027322361e4e47175a0d73b00c79faa567861a2bc17026", "67d5e44f"),
    M9J: ("322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835", "1f244140"),
    ROWS9: ("96ec405065257a543f7385711ad1841eb37316cc0148c362f35727534d05d41e", "1f244140"),
    M7J: ("bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2", "3a210f2b"),
    S.E153: ("207d4d5418f4a79f7cbf5944368af166e4f6d53eac47c05c236de543bdab2727", "8e18eb67"),
    S.E157: ("0d0c19aa2ff58ea6c58029a05d2ab33762925bc8a3bfd84c9f3d75cb522612e3", "fb2e5c6e"),
}
SCORE_INPUTS = ("score_s7arm.py", "arm-s7.json", "m9.json", "m7.json", "scored.json")
ROUTE = {  # the E163 and E164 files the route check (T5) runs, as committed (read only; nothing is written beside them)
    "tools/claims-v3/e163/score_e163.py": ("da92a03de17ba157c0d952607ba65c3d47c05e85f7b3c2b319d8be5a06d9e561", "442474d5"),
    "tools/claims-v3/e163/selftest_e163.py": ("0b43036ad54df8887f85ca2017ae5b90c77287c1abbf606845883b52f4b44589", "442474d5"),
    "tools/claims-v3/e163/predictions-e163.json": ("b4e4d3cef730f750ed9d2289a3c97d9ae6a7a7fc4656e259e13d90f79b6e8b4b", "442474d5"),
    "tools/claims-v3/e164/score_e164.py": ("ab491a8948cc17aab818600185ea6f718b62f3160408e0c7c1890d39832d4330", "f4e75c95"),
    "tools/claims-v3/e164/selftest_e164.py": ("2140ac2f4f1040d857b788f7b6d407510f4a70178c6d9f20d831b796b667cdc5", "f4e75c95"),
    "tools/claims-v3/e164/predictions-e164.json": ("b25de9a84788e2b414f34509c7af6a3514ce3797f01e277f25a72dc2f4e28e40", "f4e75c95"),
}
POOL = {"aifoundry3": "a3", "aifoundry1c1": "c1"}
HEAT_KEY = {"aifoundry3": "S|aifoundry3", "aifoundry1c1": "S|aifoundry1-c1"}
R5_LINE = 0.05
A1_NOTE = ("Q141(t) score_s7arm_a1.py: the arm M9_27pt's readings with amendment A1 (REGISTRATION.md.dated-note-2.md) applied to "
           "score_s7arm.py's output (frozen, 67d5e44f, unchanged): A1-1 R5's gate, A1-2 heat's R1 and R2, A1-3 R5m beside R5. "
           "Reported only; no verdict on M9.")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def frozen_check(names=None):
    """[(path, ok)] over FROZEN (or the entries whose basename is in names); a scoring run refuses on any mismatch"""
    out = []
    for p, (h, _c) in FROZEN.items():
        if names is None or os.path.basename(p) in names:
            out.append((p, sha(p) == h))
    return out


def m_pool():
    """M9's frozen fp32 band pool rms per card (m9.json families.float.interval_pool_by_format_card)"""
    ip = S.load(M9J)["families"]["float"]["interval_pool_by_format_card"]
    return {c: ip[f"fp32|{pc}"]["rms_w"] for c, pc in POOL.items()}


def g_heat():
    """M7's frozen heat coefficient on S per card (m7.json heat.coef), which M9 carries: dT_win = g x S"""
    co = S.load(M7J)["heat"]["coef"]
    return {c: co[k] for c, k in HEAT_KEY.items()}


# ------------------------------------------------------------------ A1-1 and A1-3: R5's gate, R5-3, R5m
def chi2_over(R1, tiles, key, m_w=0.0):
    """score_s7arm.r5's statistic over `tiles`, each sigma widened in quadrature by m_w (m_w = 0 gives r5's own figure)"""
    v = [R1[t][key] for t in tiles]
    mu = S.mean(v)
    c2 = sum((R1[t][key] - mu) ** 2 / max(math.sqrt(R1[t]["sigma_w"] ** 2 + m_w ** 2), 1e-9) ** 2 for t in tiles)
    return {"chi2": c2, "p": S.chi2_sf(c2, len(tiles) - 1), "mean_w": mu}


def r5_a1(R1, r2_read, m_w):
    t = [x for x in S.BIT20 if R1[x].get("measured") is not None]
    out = {"R5": None, "R5m": None, "R5_3_departure": None}
    if not r2_read:
        why = f"R2-R4 are not read on this card (fewer than {S.MIN_S7} of the 7 S7 tiles measured), so R5 is not read (A1-1)"
        out["R5"] = {"read": False, "why": why, "tiles": t}
        out["R5m"] = {"read": False, "why": why, "tiles": t}
        return out
    if len(t) == len(S.BIT20):
        r = S.r5(R1)                                   # the frozen function: the four tiles, 3 df, as registered
        r["gate"] = "A1-1: R2-R4 read and all four bit-20 tiles measured"
        out["R5"] = r
        rm = {"read": True, "tiles": t, "df": len(t) - 1, "m_w": m_w}
        for lab, key in (("r27", "r27_w"), ("r3", "r3_w")):
            rm[lab] = chi2_over(R1, t, key, m_w)
        rm["base_word_price_read"] = rm["r27"]["p"] < R5_LINE
        rm["rule"] = ("A1-3, reported beside R5: chi2 = sum (r27_i - mean)^2 / (sigma_i^2 + m^2) over the four bit-20 tiles, df 3, "
                      "with m = M9's frozen fp32 band pool rms for the card; a base-word price beyond M9's ordinary error is read if p < 0.05")
        out["R5m"] = rm
        return out
    why = f"{len(t)} of the 4 bit-20 tiles measured; R5 is registered over all four (3 df), so it is not read (A1-1)"
    out["R5"] = {"read": False, "why": why, "tiles": t}
    out["R5m"] = {"read": False, "why": why, "tiles": t}
    if len(t) == 3:
        d = {"name": "R5-3", "reported_only": True, "tiles": t, "df": 2,
             "note": "A1-1's named departure: the registered statistic over the three measured bit-20 tiles, 2 df; never read as a "
                     "base-word price"}
        for lab, key, mw in (("r27", "r27_w", 0.0), ("r3", "r3_w", 0.0), ("r27_m", "r27_w", m_w)):
            d[lab] = chi2_over(R1, t, key, mw)
        out["R5_3_departure"] = d
    return out


# ------------------------------------------------------------------ A1-2: heat's R1 and R2
def heat_r1(card, rows, arm, g):
    A = arm["cards"][card]
    out = {}
    for t in S.TILES:
        a = A[t]
        rec = {"in_S7": t in S.S7, "dT3_c": a["dT3_c"], "dT27_c": a["dT27_c"], "k_dT_c": a["k_dT_c"], "u_dT_c": g * a["u_w"],
               "g_c_per_w": g}
        h = rows["heat"].get(t)
        if h is None:
            rec["measured_c"] = None
            rec["why"] = "no measured 4.5 s rise in the run's rows (set aside, excluded by the run's own rules, or not run)"
            out[t] = rec
            continue
        se = h["se"] if h["se"] is not None else 0.0
        sig = math.sqrt(rec["u_dT_c"] ** 2 + se ** 2)
        r3, r27 = h["measured"] - a["dT3_c"], h["measured"] - a["dT27_c"]
        rec.update({"measured_c": h["measured"], "se_c": h["se"], "n_passes": h["n"], "se_missing": h["se"] is None, "r3_c": r3,
                    "r27_c": r27, "sigma_dT_c": sig, "r27_inside_2sigma": abs(r27) <= 2 * sig})
        rp = rows["run_pred"].get("heat", {}).get("M9", {}).get(t)
        if rp is not None and rp.get("pred") is not None:
            rec["run_M9_pred_c"] = rp["pred"]
            rec["run_M9_pred_equals_dT3"] = abs(rp["pred"] - a["dT3_c"]) < 5e-4
        out[t] = rec
    return out


def heat_r2(groups, seed):
    names = sorted(groups)
    if len(names) < S.MIN_S7:
        return {"read": False, "why": f"{len(names)} of 7 S7 tiles carry a measured rise (at least {S.MIN_S7} needed)", "tiles": names}
    a3 = [r[0] for t in names for r in groups[t]]
    a27 = [r[1] for t in names for r in groups[t]]
    d_rms, m27 = S.boot([groups[t] for t in names], seed)         # power R2's bootstrap, unchanged
    return {"read": True, "tiles": names, "n_rows": len(a3), "rms3_c": S.rms(a3), "rms27_c": S.rms(a27), "mean3_c": S.mean(a3),
            "mean27_c": S.mean(a27), "d_rms_c": S.rms(a27) - S.rms(a3), "d_rms_95": [S.pct(d_rms, 0.025), S.pct(d_rms, 0.975)],
            "mean27_95": [S.pct(m27, 0.025), S.pct(m27, 0.975)], "draws": S.DRAWS, "seed": seed}


# ------------------------------------------------------------------ the amended score
def score_a1(cards, arm):
    res = S.score(cards, arm)                                       # score_s7arm.py's readings, unchanged
    mw, g = m_pool(), g_heat()
    pooled = {}
    for card, rows in cards.items():
        c = res["cards"][card]
        r = r5_a1(c["R1"], c["R2_R4"]["read"], mw[card])
        c["R5"], c["R5m"], c["R5_3_departure"] = r["R5"], r["R5m"], r["R5_3_departure"]
        h1 = heat_r1(card, rows, arm, g[card])
        groups = {t: [(h1[t]["r3_c"], h1[t]["r27_c"])] for t in S.S7 if h1[t].get("measured_c") is not None}
        for t, gg in groups.items():
            pooled.setdefault(t, []).extend(gg)
        c["heat"] = {"R1": h1, "R2": heat_r2(groups, S.SEED[card]),
                     "missing": [t for t in S.TILES if h1[t].get("measured_c") is None],
                     "run_pred_mismatch": [t for t in S.TILES if h1[t].get("run_M9_pred_equals_dT3") is False]}
    if len(cards) == 2:
        both = {t: gg for t, gg in pooled.items() if len(gg) == 2}
        res["pooled_heat"] = heat_r2(both, S.SEED["pooled"])
        res["pooled_heat"]["note"] = "tiles with a measured rise on both cards; a draw carries both cards' rows of a tile together"
    res["_note"] = A1_NOTE
    res["amendment"] = {"file": "REGISTRATION.md.dated-note-2.md", "applies": ["A1-1", "A1-2", "A1-3"], "m_w": mw, "g_c_per_w": g,
                        "frozen_scorer": {"file": "score_s7arm.py", "sha256": FROZEN[os.path.join(HERE, "score_s7arm.py")][0],
                                          "commit": "67d5e44f"}}
    return res


def text_a1(res):
    shown = copy.deepcopy(res)
    for c in shown["cards"].values():
        c["heat"] = {"read": False}                                 # the frozen heat line is replaced by A1-2's below
    L = [S.text(shown), "", "Amendment A1 (REGISTRATION.md.dated-note-2.md): R5 above is gated by A1-1; R5m (A1-3), R5-3 and heat's R1 "
         "and R2 (A1-2) follow. Reported only."]
    for card, c in res["cards"].items():
        L.append(f"{card}:")
        v = c["R5m"]
        if v["read"]:
            L.append(f"  R5m (sigma widened by M9's fp32 band pool rms {v['m_w']:.4f} W): chi2 {v['r27']['chi2']:.2f} on {v['df']} df, "
                     f"p {v['r27']['p']:.3f} (r3: chi2 {v['r3']['chi2']:.2f}, p {v['r3']['p']:.3f}); base-word price beyond M9's "
                     f"ordinary error {'READ' if v['base_word_price_read'] else 'not read'}")
        else:
            L.append(f"  R5m: not read ({v['why']})")
        d = c["R5_3_departure"]
        if d:
            L.append(f"  R5-3, departure, reported only ({', '.join(d['tiles'])}): chi2 {d['r27']['chi2']:.2f} on 2 df, p {d['r27']['p']:.3f}; "
                     f"widened by m: chi2 {d['r27_m']['chi2']:.2f}, p {d['r27_m']['p']:.3f}; r3: chi2 {d['r3']['chi2']:.2f}, p {d['r3']['p']:.3f}")
        h = c["heat"]
        L.append(f"  heat R1 (C): {'tile':32s} {'dT':>7s} {'se':>6s} {'dT3':>7s} {'dT27':>7s} {'k_dT':>7s} {'u_dT':>6s} {'r3':>7s} {'r27':>7s}  in 2 sigma")
        for t, r in h["R1"].items():
            if r.get("measured_c") is None:
                L.append(f"               {t:32s} {'-':>7s}  ({r['why']})")
                continue
            se = f"{r['se_c']:6.3f}" if r["se_c"] is not None else "     -"
            L.append(f"               {t:32s} {r['measured_c']:7.3f} {se} {r['dT3_c']:7.3f} {r['dT27_c']:7.3f} {r['k_dT_c']:+7.3f} "
                     f"{r['u_dT_c']:6.3f} {r['r3_c']:+7.3f} {r['r27_c']:+7.3f}  {'yes' if r['r27_inside_2sigma'] else 'no'}")
        q = h["R2"]
        if q["read"]:
            L.append(f"  heat R2 (S7, n {len(q['tiles'])}): rms r3 {q['rms3_c']:.3f} -> r27 {q['rms27_c']:.3f} C (d {q['d_rms_c']:+.3f}, 95% "
                     f"[{q['d_rms_95'][0]:+.3f}, {q['d_rms_95'][1]:+.3f}]); mean r3 {q['mean3_c']:+.3f} -> r27 {q['mean27_c']:+.3f} C "
                     f"(95% [{q['mean27_95'][0]:+.3f}, {q['mean27_95'][1]:+.3f}])")
        else:
            L.append(f"  heat R2: not read ({q['why']})")
        if h["run_pred_mismatch"]:
            L.append(f"  FLAG: the run's M9 dT_win pred differs from the frozen dT3 on {h['run_pred_mismatch']}")
    if "pooled_heat" in res:
        q = res["pooled_heat"]
        if q["read"]:
            L.append(f"pooled heat (tiles on both cards, n {len(q['tiles'])}): rms r3 {q['rms3_c']:.3f} -> r27 {q['rms27_c']:.3f} C (d "
                     f"{q['d_rms_c']:+.3f}, 95% [{q['d_rms_95'][0]:+.3f}, {q['d_rms_95'][1]:+.3f}]); mean r27 {q['mean27_c']:+.3f} C (95% "
                     f"[{q['mean27_95'][0]:+.3f}, {q['mean27_95'][1]:+.3f}])")
        else:
            L.append(f"pooled heat: not read ({q['why']})")
    return "\n".join(L)


# ------------------------------------------------------------------ the self-test
def sf3(x):
    """chi-square survival at 3 df in closed form, independent of score_s7arm.chi2_sf"""
    return math.erfc(math.sqrt(x / 2.0)) + math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0)


def sf2(x):
    return math.exp(-x / 2.0)


def fake_rows(arm, card, d_of, h_of=None, drop=(), drop_h=(), se=0.05, se_h=0.02, heat_pred_shift=None):
    """rows in score_s7arm.read_rows' shape, built from the arm's own numbers (nothing here is a measurement)"""
    A = arm["cards"][card]
    pw, ht, rpp, rph = {}, {}, {}, {}
    for t in S.TILES:
        if t not in drop:
            pw[t] = {"measured": d_of(t), "n": 4, "sd": 2 * se, "se": se}
            rpp[t] = {"pred": A[t]["P3_w"]}
        if h_of is not None and t not in drop and t not in drop_h:
            ht[t] = {"measured": h_of(t), "n": 4, "sd": 2 * se_h, "se": se_h}
            rph[t] = {"pred": A[t]["dT3_c"] + (heat_pred_shift or {}).get(t, 0.0)}
    return {"file": "known-answer", "form": "scored", "power": pw, "heat": ht, "run_pred": {"power": {"M9": rpp}, "heat": {"M9": rph}},
            "disagree": []}


def block_path(d):
    """where score_s7arm.scored_block finds the rows: E163's form (primary.primary) or E164's (primary)"""
    p = d.get("primary")
    if isinstance(p, dict) and isinstance(p.get("primary"), dict) and "power_rows" in p["primary"]:
        return "primary.primary"
    if isinstance(p, dict) and "power_rows" in p:
        return "primary"
    return None


def indep_chi2(arm, card, tiles, r, se, m_w=0.0):
    A = arm["cards"][card]
    mu = sum(r[t] for t in tiles) / len(tiles)
    return sum((r[t] - mu) ** 2 / (A[t]["u_w"] ** 2 + se ** 2 + m_w ** 2) for t in tiles)


def selftest(arm, work):
    L = ["Q141(t) score_s7arm_a1.py --selftest: amendment A1 (REGISTRATION.md.dated-note-2.md) on the frozen score_s7arm.py. Known answers on",
         "rows built from the arm's own numbers (nothing here is a measurement), the calibration of R5 and R5m when no base-word price",
         f"exists, and the route through E163's and E164's own scorers on their simulated sessions. Python {sys.version.split()[0]}.", ""]
    res = {}
    ok_all = True
    mw, g = m_pool(), g_heat()
    cards = ("aifoundry3", "aifoundry1c1")

    # T0: the frozen inputs and the frozen self-test
    fc = frozen_check()
    st_res, st_txt = S.selftest(arm)
    st_same = (st_txt + "\n") == open(os.path.join(HERE, "selftest-score-s7arm.txt")).read()
    t0 = all(x for _p, x in fc) and st_res["ok"] and st_same
    res["T0"] = {"frozen_inputs": {REL(p): x for p, x in fc}, "frozen_selftest_pass": st_res["ok"],
                 "frozen_selftest_text_equals_committed": st_same, "ok": t0}
    ok_all &= t0
    L.append(f"T0 the frozen inputs: {sum(x for _p, x in fc)} of {len(fc)} hash as committed (score_s7arm.py, arm-s7.json, the two arm27 "
             f"files, m9.json, rows-m9.json, m7.json, E153's and E157's scored.json, the committed self-test text); score_s7arm.py "
             f"--selftest re-run in this process: {'PASS' if st_res['ok'] else 'FAIL'}, its text identical to the committed "
             f"selftest-score-s7arm.txt: {st_same}")
    L.append(f"   M9's fp32 band pool rms (A1-3's m): aifoundry3 {mw['aifoundry3']:.4f} W, card 1 {mw['aifoundry1c1']:.4f} W; M7's heat "
             f"coefficient on S (A1-2's g): aifoundry3 {g['aifoundry3']:.5f} C/W, card 1 {g['aifoundry1c1']:.5f} C/W")
    L.append("")

    # T1: R5's gate (A1-1), its values, R5-3, and R5m (A1-3), on known answers
    v = {"fp32.b_onebit_b20_one": 1.0, "fp32.b_onebit_b20_full": -1.0, "fp32.b_onebit_b20_pi": 1.0, "fp32.b_onebit_b20_seventh": -1.0}
    lam = {}
    for c in cards:
        A = arm["cards"][c]
        Q = sum(v[t] ** 2 / (A[t]["u_w"] ** 2 + 0.05 ** 2) for t in S.BIT20)       # the mean of v is 0
        lam[c] = {"above": math.sqrt(7.815 * 1.02 / Q), "below": math.sqrt(7.815 * 0.98 / Q)}

    def d_const(c, x):
        return lambda t: arm["cards"][c][t]["P27_w"] + x

    def d_bw(c, which):
        return lambda t: arm["cards"][c][t]["P27_w"] + lam[c][which] * v.get(t, 0.0)

    S7_OTHER = ("fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi")
    cases = (("a: all measured, r27 = +0.20 W on every tile", lambda c: d_const(c, 0.20), (), "read", None),
             ("b1: a base-word pattern at chi2 = 1.02 x 7.815", lambda c: d_bw(c, "above"), (), "read", True),
             ("b2: the same pattern at chi2 = 0.98 x 7.815", lambda c: d_bw(c, "below"), (), "read", False),
             ("c: only the four bit-20 tiles of S7 measured (4 of 7)", lambda c: d_bw(c, "above"), S7_OTHER, "gated_r2", None),
             ("d: 5 of 7, three bit-20 (b20_full and fp16 b8_pi set aside)", lambda c: d_bw(c, "above"),
              ("fp32.b_onebit_b20_full", "fp16.b_onebit_b8_pi"), "three", None),
             ("e: 6 of 7, all four bit-20 (fp16 b8_pi set aside)", lambda c: d_bw(c, "above"), ("fp16.b_onebit_b8_pi",), "read", True),
             ("f: 5 of 7, two bit-20 (b20_full and b20_pi set aside)", lambda c: d_bw(c, "above"),
              ("fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi"), "two", None))
    res["T1"] = {}
    t1 = True
    for lab, mk, drop, expect, price in cases:
        rows = {c: fake_rows(arm, c, mk(c), drop=drop) for c in cards}
        r = score_a1(rows, arm)
        got = {}
        good = True
        for c in cards:
            cc = r["cards"][c]
            R1 = cc["R1"]
            bit = [t for t in S.BIT20 if t not in drop]
            r27 = {t: R1[t]["r27_w"] for t in bit}
            r3 = {t: R1[t]["r3_w"] for t in bit}
            e27, e3 = indep_chi2(arm, c, bit, r27, 0.05), indep_chi2(arm, c, bit, r3, 0.05)
            e27m = indep_chi2(arm, c, bit, r27, 0.05, mw[c])
            frozen_reads = S.r5(R1)["read"]
            x = {"R2_R4_read": cc["R2_R4"]["read"], "R5_read": cc["R5"]["read"], "R5m_read": cc["R5m"]["read"],
                 "R5_3": cc["R5_3_departure"] is not None, "frozen_r5_reads": frozen_reads}
            if expect == "read":
                q, qm = cc["R5"], cc["R5m"]
                x.update({"df": q["df"], "chi2": q["r27"]["chi2"], "p": q["r27"]["p"], "price": q["base_word_price_read"],
                          "chi2_m": qm["r27"]["chi2"], "p_m": qm["r27"]["p"], "price_m": qm["base_word_price_read"]})
                good &= (cc["R2_R4"]["read"] and q["read"] and qm["read"] and q["df"] == 3 and cc["R5_3_departure"] is None
                         and abs(q["r27"]["chi2"] - e27) < 1e-9 and abs(q["r3"]["chi2"] - e3) < 1e-9 and abs(qm["r27"]["chi2"] - e27m) < 1e-9
                         and abs(q["r27"]["p"] - sf3(e27)) < 1e-9 and abs(q["r3"]["p"] - sf3(e3)) < 1e-9 and abs(qm["r27"]["p"] - sf3(e27m)) < 1e-9
                         and q["base_word_price_read"] == (sf3(e27) < R5_LINE) and qm["base_word_price_read"] == (sf3(e27m) < R5_LINE))
                if price is not None:
                    good &= q["base_word_price_read"] == price
                if lab.startswith("a"):
                    good &= q["r27"]["chi2"] < 1e-20 and abs(q["r27"]["p"] - 1.0) < 1e-12 and not q["base_word_price_read"]
            elif expect == "gated_r2":
                good &= (not cc["R2_R4"]["read"]) and (not cc["R5"]["read"]) and (not cc["R5m"]["read"]) and cc["R5_3_departure"] is None \
                    and frozen_reads                                  # the fault A1-1 fixes: the frozen r5() reads it here
            elif expect == "three":
                d = cc["R5_3_departure"]
                x.update({"R5_3_chi2": d["r27"]["chi2"], "R5_3_p": d["r27"]["p"]})
                good &= (cc["R2_R4"]["read"] and not cc["R5"]["read"] and not cc["R5m"]["read"] and d["df"] == 2 and d["reported_only"]
                         and "base_word_price_read" not in d and abs(d["r27"]["chi2"] - e27) < 1e-9 and abs(d["r27"]["p"] - sf2(e27)) < 1e-9
                         and abs(d["r3"]["chi2"] - e3) < 1e-9 and abs(d["r27_m"]["chi2"] - e27m) < 1e-9 and frozen_reads)
            elif expect == "two":
                good &= cc["R2_R4"]["read"] and not cc["R5"]["read"] and not cc["R5m"]["read"] and cc["R5_3_departure"] is None \
                    and not frozen_reads
            got[c] = x
        res["T1"][lab] = {"cards": got, "as_expected": good}
        t1 &= good
        a = got["aifoundry3"]
        extra = ""
        if "chi2" in a:
            extra = (f"; aifoundry3 R5 chi2 {a['chi2']:.4f} on {a['df']} df, p {a['p']:.4f} ({'READ' if a['price'] else 'not read'}); "
                     f"R5m chi2 {a['chi2_m']:.4f}, p {a['p_m']:.4f} ({'READ' if a['price_m'] else 'not read'})")
        elif "R5_3_chi2" in a:
            extra = f"; aifoundry3 R5-3 chi2 {a['R5_3_chi2']:.4f} on 2 df, p {a['R5_3_p']:.4f} (reported only)"
        L.append(f"T1 {lab}: R2-R4 read {a['R2_R4_read']}, R5 read {a['R5_read']}, R5m read {a['R5m_read']}, R5-3 {a['R5_3']}, the frozen "
                 f"r5() alone would read: {a['frozen_r5_reads']}{extra}; both cards as expected: {good}")
    L.append("   (the statistics equal an independent sum to 1e-9 and the p values the closed forms Q(3/2, x/2) = erfc(sqrt(x/2)) + "
             "sqrt(2x/pi) exp(-x/2) and exp(-x/2) to 1e-9)")
    ok_all &= t1
    L.append("")

    # T2: R6's known answers (unchanged by A1; the brief's fault 2 asks for them)
    e6 = {c: S.scored_block(S.load(S.PARENT[c]))["power_rows"]["M8"][S.B20T] for c in cards}
    res["T2"] = {}
    t2 = True
    for lab, mk, drop in (("a: D(a1p5) = P27 + 0.25 W, everything measured", lambda c: d_const(c, 0.25), ()),
                          ("b: a1p5 not measured", lambda c: d_const(c, 0.25), (S.A1P5,)),
                          ("c: a1p5 alone measured (no S7 tile)", lambda c: d_const(c, 0.25), S.S7)):
        rows = {c: fake_rows(arm, c, mk(c), drop=drop) for c in cards}
        r = score_a1(rows, arm)
        good = True
        got = {}
        for c in cards:
            q = r["cards"][c]["R6"]
            a, tw, m6 = arm["cards"][c][S.A1P5], arm["pool6_twins_posthoc"][c][S.B20T], e6[c]
            se6 = m6["sd"] / math.sqrt(m6["n_passes"])
            s6 = math.sqrt(tw["u_w"] ** 2 + se6 ** 2)
            sa = math.sqrt(a["u_w"] ** 2 + 0.05 ** 2)
            p6 = m6["measured"] - tw["P27_w"]
            if S.A1P5 in drop:
                good &= (not q["read"]) and abs(q["pool6_r27_w"] - p6) < 1e-12
                got[c] = {"read": q["read"], "why": q.get("why")}
            else:
                D = a["P27_w"] + 0.25
                good &= (q["read"] and abs(q["a1p5_r27_w"] - 0.25) < 1e-9 and abs(q["a1p5_r3_w"] - (0.25 - a["k_w"])) < 2e-4
                         and abs(q["pool6_r27_w"] - p6) < 1e-12 and abs(q["d_r27_w"] - (0.25 - p6)) < 1e-9
                         and abs(q["d_r27_pm_w"] - math.sqrt(sa ** 2 + s6 ** 2)) < 1e-12
                         and abs(q["measured_A15_minus_A10_w"] - (D - m6["measured"])) < 1e-9
                         and abs(q["P27_A15_minus_A10_w"] - (a["P27_w"] - tw["P27_w"])) < 1e-12
                         and abs(q["P3_A15_minus_A10_w"] - (a["P3_w"] - tw["P3_w"])) < 1e-12)
                got[c] = {"read": q["read"], "a1p5_r27_w": q["a1p5_r27_w"], "pool6_r27_w": q["pool6_r27_w"], "d_r27_w": q["d_r27_w"],
                          "d_r27_pm_w": q["d_r27_pm_w"]}
            if lab.startswith("c"):
                good &= not r["cards"][c]["R2_R4"]["read"] and not r["cards"][c]["R5"]["read"]
        res["T2"][lab] = {"cards": got, "as_expected": good}
        t2 &= good
        a = got["aifoundry3"]
        desc = (f"aifoundry3 r27 {a['a1p5_r27_w']:+.4f} vs pool 6's {a['pool6_r27_w']:+.4f} W, d {a['d_r27_w']:+.4f} +- {a['d_r27_pm_w']:.4f}"
                if a.get("read") else f"not read ({a.get('why')})")
        L.append(f"T2 R6 {lab}: {desc}; both cards as expected: {good}")
    ok_all &= t2
    L.append("")

    # T3: heat (A1-2): the law's link, R1's added fields, R2 with intervals per card and pooled, the gate, the pred flag
    law, kd = [], []
    for c in cards:
        for t in S.TILES:
            a = arm["cards"][c][t]
            law.append(max(abs(g[c] * a["S3_w"] - a["dT3_c"]), abs(g[c] * a["S27_w"] - a["dT27_c"])))
            kd.append(abs(g[c] * a["k_w"] - a["k_dT_c"]))
    t3 = max(law) <= 0.000506 and max(kd) <= 0.00101
    L.append(f"T3 heat's law: dT3 = g x S3 and dT27 = g x S27 to their 3-decimal rounding on all 16 tile-cards (worst {max(law):.5f} C), "
             f"and k_dT = g x k to the rounding of two rises (worst {max(kd):.5f} C): {t3}")
    res["T3"] = {"law_link_ok": t3, "law_worst_c": max(law), "k_dT_worst_c": max(kd)}

    def h_const(c, x):
        return lambda t: arm["cards"][c][t]["dT27_c"] + x
    for lab, hk, drop, shift in (("a: rise = dT27 + 0.10 C everywhere", 0.10, (), None),
                                 ("b: rises on 4 of 7 S7 tiles only (D on all)", 0.10, S7_OTHER, None),
                                 ("c: the run's M9 rise pred off by 0.01 C on fp16 b9_one", 0.10, (), {"fp16.b_onebit_b9_one": 0.01})):
        rows = {c: fake_rows(arm, c, d_const(c, 0.2), h_of=h_const(c, hk), drop_h=drop, heat_pred_shift=shift) for c in cards}
        r = score_a1(rows, arm)
        good = True
        got = {}
        for c in cards:
            h = r["cards"][c]["heat"]
            q = h["R2"]
            for t, x in h["R1"].items():
                if t in drop:
                    good &= x["measured_c"] is None
                    continue
                a = arm["cards"][c][t]
                good &= (abs(x["r27_c"] - hk) < 1e-9 and abs(x["r3_c"] - (hk - (a["dT3_c"] - a["dT27_c"]))) < 1e-9
                         and abs(x["u_dT_c"] - g[c] * a["u_w"]) < 1e-15
                         and abs(x["sigma_dT_c"] - math.sqrt((g[c] * a["u_w"]) ** 2 + 0.02 ** 2)) < 1e-12
                         and x["r27_inside_2sigma"] == (abs(x["r27_c"]) <= 2 * x["sigma_dT_c"]))
                fr = r["cards"][c]["R1"][t].get("heat")
                if fr is not None:
                    good &= abs(fr["r27_c"] - x["r27_c"]) < 1e-12 and abs(fr["r3_c"] - x["r3_c"]) < 1e-12
            if lab.startswith("b"):
                good &= not q["read"]
            else:
                ts = [t for t in S.S7]
                r3 = [arm["cards"][c][t]["dT27_c"] + hk - arm["cards"][c][t]["dT3_c"] for t in ts]
                good &= (q["read"] and q["seed"] == S.SEED[c] and q["draws"] == 20000 and abs(q["rms27_c"] - hk) < 1e-9
                         and abs(q["mean27_c"] - hk) < 1e-9 and abs(q["mean27_95"][0] - hk) < 1e-9 and abs(q["mean27_95"][1] - hk) < 1e-9
                         and abs(q["rms3_c"] - S.rms(r3)) < 1e-12 and abs(q["d_rms_c"] - (hk - S.rms(r3))) < 1e-9
                         and q["d_rms_95"][0] <= q["d_rms_95"][1])
            mism = h["run_pred_mismatch"]
            good &= mism == (["fp16.b_onebit_b9_one"] if shift else [])
            got[c] = {"R2_read": q["read"], "rms3_c": q.get("rms3_c"), "d_rms_c": q.get("d_rms_c"), "d_rms_95": q.get("d_rms_95"),
                      "mean27_95": q.get("mean27_95"), "run_pred_mismatch": mism}
        pq = r.get("pooled_heat", {})
        good &= (not pq.get("read")) if lab.startswith("b") else (pq.get("read") and pq["n_rows"] == 14 and pq["seed"] == 143)
        res["T3"][lab] = {"cards": got, "pooled_read": pq.get("read"), "as_expected": good}
        t3 &= good
        a = got["aifoundry3"]
        desc = (f"aifoundry3 rms r3 {a['rms3_c']:.4f} -> r27 0.1000 C, d {a['d_rms_c']:+.4f} (95% [{a['d_rms_95'][0]:+.4f}, "
                f"{a['d_rms_95'][1]:+.4f}]), mean r27 95% [{a['mean27_95'][0]:+.4f}, {a['mean27_95'][1]:+.4f}]" if a["R2_read"]
                else "R2 not read")
        L.append(f"T3 {lab}: {desc}; pooled read {pq.get('read')}; pred flags {a['run_pred_mismatch']}; both cards as expected: {good}")
    ok_all &= t3
    L.append("")

    # T4: R5's and R5m's read rates when no base-word price exists, and with a 0.6 W one (fixed seeds; 20,000 draws a world)
    rows9 = S.load(ROWS9)
    ref = {c: [r["M9_nested_err_w"] for r in rows9 if r["type"] == "fp32" and r["card"] == POOL[c] and r.get("M9_nested_err_w") is not None]
           for c in cards}
    N, SE = 20000, 0.03
    res["T4"] = {"draws": N, "se_w": SE, "worlds": {}}
    L.append(f"T4 how often R5 (and R5m) read a base-word price (p < 0.05), {N:,} draws a world, se {SE} W a tile, the arm's u; M9's "
             f"ordinary error = a draw from M9's nested fp32 errors on the card (rows-m9.json, {len(ref['aifoundry3'])} rows on aifoundry3, "
             f"{len(ref['aifoundry1c1'])} on card 1):")
    t4 = True
    for c in cards:
        A = arm["cards"][c]
        sig = [math.sqrt(A[t]["u_w"] ** 2 + SE ** 2) for t in S.BIT20]
        sbar = sum(sig) / 4
        n = 4
        e_chi = n - 2 + sum(s * s for s in sig) * sum(1 / (s * s) for s in sig) / n ** 2
        out = {}
        for world in ("equal_sigma", "counting_and_measurement", "plus_M9_ordinary_error", "plus_M9_error_and_0.6W_on_one_tile"):
            rng = random.Random(f"Q141t-A1|T4|{c}|{world}")
            hit = hit_m = 0
            for _ in range(N):
                s = [sbar] * 4 if world == "equal_sigma" else sig
                x = [rng.gauss(0.0, s[i]) for i in range(4)]
                if world.startswith("plus"):
                    x = [x[i] + rng.choice(ref[c]) for i in range(4)]
                if world.endswith("one_tile"):
                    x[rng.randrange(4)] += 0.6
                mu = sum(x) / 4
                hit += S.chi2_sf(sum((x[i] - mu) ** 2 / s[i] ** 2 for i in range(4)), 3) < R5_LINE
                hit_m += S.chi2_sf(sum((x[i] - mu) ** 2 / (s[i] ** 2 + mw[c] ** 2) for i in range(4)), 3) < R5_LINE
            out[world] = {"R5_rate": hit / N, "R5m_rate": hit_m / N}
        lo, hi = 0.05 - 4 * math.sqrt(0.05 * 0.95 / N), 0.05 + 4 * math.sqrt(0.05 * 0.95 / N)
        good = lo <= out["equal_sigma"]["R5_rate"] <= hi
        t4 &= good
        res["T4"]["worlds"][c] = {"rates": out, "R5_expected_chi2_unweighted_mean": e_chi, "equal_sigma_known_answer_band": [lo, hi],
                                  "equal_sigma_ok": good}
        L.append(f"   {c}: equal sigma (the exact chi2(3) case, known answer {lo:.4f}-{hi:.4f}): R5 {out['equal_sigma']['R5_rate']:.4f}, "
                 f"{'as expected' if good else 'NOT as expected'}; the arm's sigma, counting and measurement only: R5 "
                 f"{out['counting_and_measurement']['R5_rate']:.4f} (its centring on the unweighted mean gives E[chi2] {e_chi:.3f}, "
                 f"not 3), R5m {out['counting_and_measurement']['R5m_rate']:.4f}")
        L.append(f"   {c}: plus M9's ordinary error, no base-word price: R5 {out['plus_M9_ordinary_error']['R5_rate']:.4f}, R5m "
                 f"{out['plus_M9_ordinary_error']['R5m_rate']:.4f}; plus a 0.6 W price on one bit-20 tile: R5 "
                 f"{out['plus_M9_error_and_0.6W_on_one_tile']['R5_rate']:.4f}, R5m {out['plus_M9_error_and_0.6W_on_one_tile']['R5m_rate']:.4f}")
    res["T4"]["ok"] = t4
    ok_all &= t4
    L.append("   So a READ of R5 by itself does not separate a base-word price from M9's ordinary per-tile error; R5m does, at about "
             "the stated rate. Both stay reported only.")
    L.append("")

    # T5: the route through E163's and E164's own scorers (their simulated sessions), then this file
    rt = {k: sha(os.path.join(TOP, k)) == h for k, (h, _c) in ROUTE.items()}
    t5 = all(rt.values())
    got = {}
    if t5:
        sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "e163"))
        import score_e163 as S3  # noqa: E402
        import selftest_e163 as T3  # noqa: E402
        sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "e164"))
        import score_e164 as S4  # noqa: E402
        import selftest_e164 as T4m  # noqa: E402
        reg3 = copy.deepcopy(S.load(os.path.join(TOP, "tools", "claims-v3", "e163", "predictions-e163.json")))
        reg3["spec"]["bootstrap"]["draws"] = 2000
        a27_3 = S.load(os.path.join(HERE, "arm", "arm27-aifoundry3.json"))
        a27_1 = S4.load_recount(os.path.join(HERE, "arm", "arm27-aifoundry1c1.json"))
        r3 = S3.run(reg3, T3.fake(reg3, random.Random("Q141t-A1|T5|E163"), 1.0, 0.0), arm27=a27_3)
        r4 = S4.run(T4m.REG, T4m.session(random.Random("Q141t-A1|T5|E164"), "as_good"), s_recount=a27_1)
        p3, p4 = os.path.join(work, "route-e163-scored.json"), os.path.join(work, "route-e164-scored.json")
        json.dump(r3, open(p3, "w"), indent=1, default=lambda o: None)
        json.dump(r4, open(p4, "w"), indent=1, default=lambda o: None)
        rows = {"aifoundry3": S.read_rows(p3), "aifoundry1c1": S.read_rows(p4)}
        sc = score_a1(rows, arm)
        ra = (r3["primary"]["primary"].get("reported_arm27") or {}).get("rows") or {}
        rs = (r4["primary"].get("reported_s_recount_arm") or {}).get("tiles") or {}
        j3, j4 = S.load(p3), S.load(p4)
        for c, rw, j in (("aifoundry3", rows["aifoundry3"], j3), ("aifoundry1c1", rows["aifoundry1c1"], j4)):
            cc = sc["cards"][c]
            blk = S.scored_block(j)
            got[c] = {"form": rw["form"], "block": block_path(j),
                      "tiles_read": sum(1 for t in S.TILES if cc["R1"][t].get("measured") is not None),
                      "power_pred_mismatch": cc["run_pred_mismatch"], "heat_pred_mismatch": cc["heat"]["run_pred_mismatch"],
                      "R2_R4": cc["R2_R4"]["read"], "R5": cc["R5"]["read"], "R5m": cc["R5m"]["read"], "R6": cc["R6"]["read"],
                      "heat_R2": cc["heat"]["R2"]["read"],
                      "measured_equal": all(abs(cc["R1"][t]["measured"] - blk["power_rows"]["M9"][t]["measured"]) < 1e-12 for t in S.TILES)}
        got["E163_reported_arm27_rows"] = len(ra)
        got["E163_arm27_values_equal"] = all(abs(ra[t]["arm27_D"] - a27_3[t]) < 1e-12 for t in a27_3) if len(ra) == 8 else False
        got["E164_reported_s_recount_tiles"] = len(rs)
        got["E164_recount_values_equal"] = all(abs(rs[t]["recount_pred"] - a27_1[t]) < 1e-12 for t in a27_1) if len(rs) == 8 else False
        got["pooled_power_read"] = sc["pooled"]["read"]
        got["pooled_heat_read"] = sc["pooled_heat"]["read"]
        for c in cards:
            x = got[c]
            t5 &= (x["form"] == "scored" and x["tiles_read"] == 8 and not x["power_pred_mismatch"] and not x["heat_pred_mismatch"]
                   and x["R2_R4"] and x["R5"] and x["R5m"] and x["R6"] and x["heat_R2"] and x["measured_equal"])
        t5 &= got["E163_arm27_values_equal"] and got["E164_recount_values_equal"] and got["pooled_power_read"] and got["pooled_heat_read"]
        t5 &= got["aifoundry3"]["block"] == "primary.primary" and got["aifoundry1c1"]["block"] == "primary"
    res["T5"] = {"route_files_hash_as_committed": rt, "result": got, "ok": t5}
    ok_all &= t5
    if got:
        L.append(f"T5 the route: a simulated E163 session through score_e163.run (arm27 = arm/arm27-aifoundry3.json, the collector's second "
                 f"argument) and a simulated E164 session through score_e164.run (s_recount = arm/arm27-aifoundry1c1.json, the collector's "
                 f"E164_S_RECOUNT), each from its own committed self-test simulator, written as scored.json and read by this file:")
        for c in cards:
            x = got[c]
            L.append(f"   {c}: {x['form']} form under {x['block']}; {x['tiles_read']} of 8 arm tiles read, D equal to the run's power_rows: "
                     f"{x['measured_equal']}; the run's M9 power pred = P3 on all 8: {not x['power_pred_mismatch']}, its rise pred = dT3 on all "
                     f"8: {not x['heat_pred_mismatch']}; R2-R4 {x['R2_R4']}, R5 {x['R5']}, R5m {x['R5m']}, R6 {x['R6']}, heat R2 {x['heat_R2']}")
        L.append(f"   E163's reported_arm27: {got['E163_reported_arm27_rows']} rows, arm27_D = the file's values: {got['E163_arm27_values_equal']}; "
                 f"E164's reported_s_recount_arm: {got['E164_reported_s_recount_tiles']} tiles, recount_pred = the file's values: "
                 f"{got['E164_recount_values_equal']}; pooled power read {got['pooled_power_read']}, pooled heat read {got['pooled_heat_read']}")
    else:
        L.append(f"T5 the route: not run, a route file differs from its committed bytes: {rt}")
    L.append(f"   the six route files hash as committed (score_e163.py, selftest_e163.py, predictions-e163.json at 442474d5; score_e164.py, "
             f"selftest_e164.py, predictions-e164.json at f4e75c95): {all(rt.values())}; route as expected: {t5}")
    L += ["", f"selftest: {'PASS' if ok_all else 'FAIL'}"]
    res["ok"] = ok_all
    return res, "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a3", default=None, help="E163's rows (aifoundry3): scored.json, or the reduced items form")
    ap.add_argument("--c1", default=None, help="E164's rows (aifoundry1 card 1): scored.json, or the reduced items form")
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--work", default=None, help="the self-test's scratch directory for T5's two simulated scored.json (default: a temporary one)")
    a = ap.parse_args()
    arm = S.load(os.path.join(HERE, "arm-s7.json"))
    if a.selftest:
        tmp = None
        work = a.work
        if work is None:
            tmp = tempfile.TemporaryDirectory()
            work = tmp.name
        os.makedirs(work, exist_ok=True)
        res, txt = selftest(arm, work)
        print(txt)
        if a.out:
            json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
        if tmp:
            tmp.cleanup()
        sys.exit(0 if res["ok"] else 1)
    bad = [REL(p) for p, x in frozen_check(SCORE_INPUTS) if not x]
    if bad:
        raise SystemExit(f"refused: these frozen inputs differ from their committed bytes: {bad}")
    cards = {}
    if a.a3:
        cards["aifoundry3"] = S.read_rows(a.a3)
    if a.c1:
        cards["aifoundry1c1"] = S.read_rows(a.c1)
    if not cards:
        raise SystemExit("give --a3 and/or --c1 (or --selftest)")
    res = score_a1(cards, arm)
    print(text_a1(res))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
