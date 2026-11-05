#!/usr/bin/env python3
"""E175 (Q143(g) fix pass; dated note A2 beside E175.md): E175-A2-M1's outcome shares at the registration's truths, with dated note A2's
reading of a resolved M1 and its reported arm E175-A2-M1c, before any E175 session. Design only: it reads E175's committed kit
(predictions-e175.json), its frozen predictions (frozen/predictions-pool8-aifoundry2.json), Q142(p)'s frozen predictor and E165's committed
references and blind errors (through the registration's own design_power_e175.py); never an E175 datum (none exists), never an E171-E174 file.

  * delta: on each of the 24 kept tiles (the scored set in name order, the scorer's order), delta_i = M9's part on M9's D less M10 carried, on the
    board (W) and on the clock (MHz), so that b = a - delta (a = measured - M10 carried, b = measured - M9's part, E175.md's paired engine). The
    primary delta is the frozen fallback's (predictions-e175.json's a2_fallback blocks, which burst() with no anchor read reproduces); the
    session recomputes both models with its own zeros-anchor reads and die starts, so delta is also recomputed through predict_pool8_a2.burst
    with made-up anchor reads 1 and 0.5 W below and above the fallback zeros level and with die starts 5 C below and above T_ref.
  * a simulated session: 16 governed and 8 pinned cells (a clock error and a board error kept together) drawn with replacement from a truth,
    random.Random("E175-A2|M1-power|<truth>|<sessions>"), assigned to the governed and pinned tiles in name order. The truths: the
    registration's five (design_power_e175.py's e2e, e165, e2e x1.5, e2e level, e2e x0.5, defined there and repeated here), and three more:
    e2e with the opposite level (the clock 3 MHz low on governed bursts, the board 0.5 W low on both groups), e2e centred (each group's own mean
    removed), and e2e with M9's part right (measured = M9's part + the cell, so a = the cell + delta).
  * E175-A2-M1 exactly as registered (E175.md "The paired engine"; p8gov.paired): random.Random(80,000 + the sum of the rule id's character
    codes), the same seed for every session, 20,000 draws of n = 24 tile indices with replacement, the value rms(a[idx]) - rms(b[idx]), the
    interval [vals[500], vals[19499]] of the sorted values; BETTER if its upper end < 0, WORSE if its lower end > 0, else NOT RESOLVED. Since
    vals[19499] < 0 exactly when at least 19,500 of the 20,000 values are below 0, and vals[500] > 0 exactly when at least 19,500 are above 0, and
    rms(a[idx]) - rms(b[idx]) has the sign of mean(a^2 - b^2) over the draw, the verdict is computed from the draws' count matrix (the same
    draws, in the same order); the first sessions of every truth are also scored by p8gov.paired itself and must agree.
  * E175-A2-M1c (dated note A2, reported, never a verdict): the same engine with its own rule id's seed on each model's errors less that model's
    own mean in each frozen group (governed, pinned). The clock beside M1 (E175-A2-M1_clock_beside, reported) and its centred form: the same, on
    the clock.
  * dated note A2's reading: a resolved M1 with the session's board on its side (BETTER with the board below both models' predictions in both
    groups: Bg's and Bp's means, M10 carried's errors, below 0; WORSE with it above both: M9's part's errors' means above 0 in both groups) is
    the session's board level, not evidence on D; any other resolved M1 is evidence on D only when M1c resolves the same way, else the session's
    board level too. Printed per truth: the shares of each verdict, of a resolved M1 on the level's side, of M1c resolving the same way, of the
    reading "evidence on D" (and its direction) and of "the session's board level", and where the board lay when M1 resolved.
  * the identity behind it, checked in every session: mean(a^2) - mean(b^2) = 2 mean(delta) (abar_delta - theta), with abar_delta = sum(delta a)
    / sum(delta) (the session's board error weighted by how far the two models differ on each tile) and theta = sum(delta^2) / (2 sum(delta)), so
    M1's point is below 0 exactly when abar_delta < theta.

    /usr/bin/python3 -B tools/claims-v3/e175/m1_power_e175.py --out tools/claims-v3/e175/m1-power-e175.json > tools/claims-v3/e175/m1-power-e175.txt

Standard library and numpy (the Intel's /usr/bin/python3 3.9, numpy 1.26), at most 2 threads. SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import e175_common as C  # noqa: E402
import numpy as np  # noqa: E402

DRAWS = 20000
LO_I, HI_I = int(0.025 * DRAWS), int(0.975 * DRAWS) - 1      # 500, 19499: p8gov.paired's interval ends
NEED = DRAWS - LO_I                                          # 19,500 draws on one side of 0 resolve the interval
SESSIONS = 4000
SENS_SESSIONS = 2000
CHECK_SESSIONS = 4                                           # per truth and arm, also scored by p8gov.paired itself
CHUNK = 250
RULE_M1, RULE_M1C = "E175-A2-M1", "E175-A2-M1c"
PRED_PATH = os.path.join(HERE, "predictions-e175.json")
OFFSETS_W = (-1.0, -0.5, 0.5, 1.0)
DIE_OFFSETS_C = (-5.0, 5.0)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def count_matrix(seed, n):
    """the draws of p8gov.paired, in its order (random.Random(seed); 20,000 times [rng.randrange(n) for _ in range(n)]), as counts per tile"""
    rng = random.Random(seed)
    M = np.zeros((DRAWS, n))
    for k in range(DRAWS):
        for _ in range(n):
            M[k, rng.randrange(n)] += 1.0
    return M


def verdicts(M, a, b):
    """a, b: sessions x tiles. The registered verdict per session from the count matrix: BETTER / WORSE / NOT RESOLVED"""
    out = np.empty(a.shape[0], dtype=object)
    for s0 in range(0, a.shape[0], CHUNK):
        d = (a[s0:s0 + CHUNK] ** 2 - b[s0:s0 + CHUNK] ** 2).T          # tiles x chunk
        v = M @ d                                                    # draws x chunk: the sign of mean(a^2) - mean(b^2) over each draw
        neg, pos = (v < 0).sum(axis=0), (v > 0).sum(axis=0)
        out[s0:s0 + CHUNK] = np.where(neg >= NEED, "BETTER", np.where(pos >= NEED, "WORSE", "NOT RESOLVED"))
    return out


def centred(x, groups):
    y = x.copy()
    for g in set(groups):
        cols = [i for i, h in enumerate(groups) if h == g]
        y[:, cols] -= y[:, cols].mean(axis=1, keepdims=True)
    return y


def shares(v):
    n = len(v)
    return {k: round(100.0 * float((v == k).sum()) / n, 1) for k in ("BETTER", "WORSE", "NOT RESOLVED")}


def deltas(A, pred_a2, tiles, anchors=None, die=None):
    b = A.burst(pred_a2, anchors, die or {})["tiles"]
    dw = [b[n]["M9"]["burst_board_w"] - b[n]["M10"]["burst_board_w"] for n in tiles]
    dm = [b[n]["M9"]["burst_mhz"] - b[n]["M10"]["burst_mhz"] for n in tiles]
    return dw, dm, b


def dsum(d, idx):
    v = [d[i] for i in idx]
    return {"mean": round(sum(v) / len(v), 4), "min": round(min(v), 4), "max": round(max(v), 4), "n_negative_M10_above": sum(1 for x in v if x < 0),
            "n_zero": sum(1 for x in v if x == 0)}


def simulate(name, cells_g, cells_p, tiles, gi, pi, dw, dm, groups, M1, M1c, sessions, A, G, m9_right=False, check=CHECK_SESSIONS):
    n = len(tiles)
    rng = random.Random(f"E175-A2|M1-power|{name}|{sessions}")
    ew, em = np.zeros((sessions, n)), np.zeros((sessions, n))
    for s in range(sessions):
        for i in gi:
            c = cells_g[rng.randrange(len(cells_g))]
            em[s, i], ew[s, i] = c
        for i in pi:
            c = cells_p[rng.randrange(len(cells_p))]
            em[s, i], ew[s, i] = c
    dW, dM = np.array(dw), np.array(dm)
    a_w = ew + (dW if m9_right else 0.0)
    a_m = em + (dM if m9_right else 0.0)
    b_w, b_m = a_w - dW, a_m - dM
    ac_w, bc_w = centred(a_w, groups), centred(b_w, groups)
    ac_m, bc_m = centred(a_m, groups), centred(b_m, groups)
    v1, v1c = verdicts(M1, a_w, b_w), verdicts(M1c, ac_w, bc_w)
    vk, vkc = verdicts(M1, a_m, b_m), verdicts(M1c, ac_m, bc_m)
    # p8gov.paired itself on the first sessions
    agree, checked = 0, 0
    for s in range(min(check, sessions)):
        for rule, aa, bb, vv in ((RULE_M1, a_w, b_w, v1), (RULE_M1C, ac_w, bc_w, v1c), (RULE_M1, a_m, b_m, vk)):
            r = G.paired(rule, [float(x) for x in aa[s]], [float(x) for x in bb[s]], 10, A)
            checked += 1
            agree += int(r["verdict"] == vv[s])
    # the identity and the reading
    point = np.sqrt((a_w ** 2).mean(axis=1)) - np.sqrt((b_w ** 2).mean(axis=1))
    sd = dW.sum()
    abar = (a_w * dW).sum(axis=1) / sd if sd != 0 else np.full(sessions, np.nan)
    theta = (dW ** 2).sum() / (2.0 * sd) if sd != 0 else float("nan")
    ident_bad = int(((point < 0) != (abar < theta)).sum()) if sd > 0 else None
    mg, mp = a_w[:, gi].mean(axis=1), a_w[:, pi].mean(axis=1)          # Bg's and Bp's means: M10 carried's errors
    mgb, mpb = b_w[:, gi].mean(axis=1), b_w[:, pi].mean(axis=1)        # the same groups' means of M9's part's errors
    below_both = (mg < 0) & (mp < 0)                                   # the board below both models' predictions in both groups
    above_both = (mgb > 0) & (mpb > 0)                                 # above both in both groups
    resolved = (v1 == "BETTER") | (v1 == "WORSE")
    level_side = ((v1 == "BETTER") & below_both) | ((v1 == "WORSE") & above_both)
    same = resolved & (v1c == v1)
    as_d = resolved & ~level_side & same                               # dated note A2's reading: evidence on D
    side = {}
    for verdict in ("BETTER", "WORSE"):
        sel = v1 == verdict
        k = int(sel.sum())
        below = int((sel & below_both).sum())
        above = int((sel & above_both).sum())
        side[verdict] = {"sessions": k, "below_both_predictions": below, "above_both_predictions": above, "mixed": k - below - above}
    return {"sessions": sessions, "M1": shares(v1), "M1c": shares(v1c), "M1_clock_beside": shares(vk), "M1c_clock_beside": shares(vkc),
            "M1_resolved_pct": round(100.0 * float(resolved.sum()) / sessions, 1),
            "M1_resolved_level_side_pct": round(100.0 * float(level_side.sum()) / sessions, 1),
            "M1c_same_pct": round(100.0 * float(same.sum()) / sessions, 1),
            "read_as_D_pct": round(100.0 * float(as_d.sum()) / sessions, 1),
            "read_as_D_BETTER_pct": round(100.0 * float((as_d & (v1 == "BETTER")).sum()) / sessions, 1),
            "read_as_D_WORSE_pct": round(100.0 * float((as_d & (v1 == "WORSE")).sum()) / sessions, 1),
            "read_as_level_pct": round(100.0 * float((resolved & ~as_d).sum()) / sessions, 1),
            "point_median_w": round(float(np.median(point)), 4), "point_below_0_pct": round(100.0 * float((point < 0).sum()) / sessions, 1),
            "theta_w": round(theta, 5), "abar_delta_median_w": round(float(np.median(abar)), 4),
            "identity_mismatches": ident_bad, "side_when_resolved": side,
            "Bg_mean_median_w": round(float(np.median(mg)), 4), "Bp_mean_median_w": round(float(np.median(mp)), 4),
            "checked_by_p8gov_paired": checked, "agree_with_p8gov_paired": agree}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--sessions", type=int, default=SESSIONS)
    a = ap.parse_args()
    bad = C.check_frozen(ccheck=False)
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    A = C.a2p()
    import design_power_e175 as DP  # noqa: E402  (the registration's power script: its e165_blind() and its truths' form)
    import p8gov as G  # noqa: E402  (E173's paired engine, unchanged)
    P = json.load(open(PRED_PATH))
    pred_a2 = json.load(open(os.path.join(C.TOP, C.PRED_REL)))
    tiles = sorted(P["sets"]["scored"])
    groups = [P["tiles"][n]["group"] for n in tiles]
    gi = [i for i, g in enumerate(groups) if g == "governed"]
    pi = [i for i, g in enumerate(groups) if g == "pinned"]
    ng, npn = len(gi), len(pi)
    # delta at the frozen fallback, and burst() with no anchor read must give the same blocks
    fb = {n: (P["tiles"][n]["models"]["M10"]["a2_fallback"], P["tiles"][n]["models"]["M9"]["a2_fallback"]) for n in tiles}
    dw = [fb[n][1]["burst_board_w"] - fb[n][0]["burst_board_w"] for n in tiles]
    dm = [fb[n][1]["burst_mhz"] - fb[n][0]["burst_mhz"] for n in tiles]
    dw0, dm0, _ = deltas(A, pred_a2, tiles)
    fallback_same = (dw0 == dw) and (dm0 == dm)
    # delta under made-up session reads
    M9P = A.P().a2_part()
    lz = {t: M9P.B[800] + M9P.CZ[t] * M9P.S[800] for t in M9P.TYPES}

    def anchors(x):
        return {t: [{"burst_w": lz[t] + M9P.M9["fallback_delta_w"][t] + x, "burst_mhz": 800.0, "die_start": M9P.TREF}] for t in M9P.TYPES}

    sens = {}
    dw_z, dm_z, _ = deltas(A, pred_a2, tiles, anchors(0.0), {n: [M9P.TREF] for n in tiles})
    sens["anchors at the fallback level, die starts T_ref"] = {"board": dsum(dw_z, range(len(tiles))), "same_as_fallback": dw_z == dw and dm_z == dm}
    cases = [(f"anchors {x:+.1f} W from the fallback zeros level, die starts T_ref", anchors(x), {n: [M9P.TREF] for n in tiles}) for x in OFFSETS_W]
    cases += [(f"anchors at the fallback level, die starts T_ref {y:+.0f} C", anchors(0.0), {n: [M9P.TREF + y] for n in tiles}) for y in DIE_OFFSETS_C]
    case_d = {}
    for lab, an, die in cases:
        w, m, _ = deltas(A, pred_a2, tiles, an, die)
        case_d[lab] = (w, m)
        sens[lab] = {"board": dsum(w, range(len(tiles))), "board_governed": dsum(w, gi), "board_pinned": dsum(w, pi),
                     "clock": dsum(m, range(len(tiles))), "max_abs_change_from_fallback_w": round(max(abs(p - q) for p, q in zip(w, dw)), 4)}
    # the truths (design_power_e175.py's five, then three more)
    R = A.e165_refs()
    gov_e2e, pin_e2e = list(zip(R["gov_mhz"], R["gov_w"])), list(zip(R["pin_mhz"], R["pin_w"]))
    g165, p165, _ = DP.e165_blind()

    def cen(cells):
        mx, my = sum(x for x, _ in cells) / len(cells), sum(y for _, y in cells) / len(cells)
        return [(x - mx, y - my) for x, y in cells]
    truths = {
        "e2e": (gov_e2e, pin_e2e, False),
        "e165": (g165, p165, False),
        "e2e x1.5": ([(1.5 * x, 1.5 * y) for x, y in gov_e2e], [(1.5 * x, 1.5 * y) for x, y in pin_e2e], False),
        "e2e level": ([(x + 3.0, y + 0.5) for x, y in gov_e2e], [(x, y + 0.5) for x, y in pin_e2e], False),
        "e2e x0.5": ([(0.5 * x, 0.5 * y) for x, y in gov_e2e], [(0.5 * x, 0.5 * y) for x, y in pin_e2e], False),
        "e2e level low": ([(x - 3.0, y - 0.5) for x, y in gov_e2e], [(x, y - 0.5) for x, y in pin_e2e], False),
        "e2e centred": (cen(gov_e2e), cen(pin_e2e), False),
        "e2e, M9's part right": (gov_e2e, pin_e2e, True),
    }
    seeds = {RULE_M1: A.P().seed_of(RULE_M1), RULE_M1C: A.P().seed_of(RULE_M1C)}
    M1, M1c = count_matrix(seeds[RULE_M1], len(tiles)), count_matrix(seeds[RULE_M1C], len(tiles))
    res = {}
    for t, (cg, cp, m9r) in truths.items():
        res[t] = simulate(t, cg, cp, tiles, gi, pi, dw, dm, groups, M1, M1c, a.sessions, A, G, m9_right=m9r)
        res[t]["truth"] = {"gov_n": len(cg), "gov_mean_w": round(sum(y for _, y in cg) / len(cg), 4), "pin_n": len(cp),
                           "pin_mean_w": round(sum(y for _, y in cp) / len(cp), 4), "gov_rms_w": round(rms([y for _, y in cg]), 4),
                           "pin_rms_w": round(rms([y for _, y in cp]), 4), "measured_is": "M9's part + the cell" if m9r else "M10 carried + the cell"}
    sres = {}
    for lab, (w, m) in case_d.items():
        sres[lab] = {t: simulate(t, truths[t][0], truths[t][1], tiles, gi, pi, w, m, groups, M1, M1c, SENS_SESSIONS, A, G, check=0)["M1"]
                     for t in ("e2e", "e165")}
    wsum = sum(dw)
    pinned_weight = sum(dw[i] for i in pi) / wsum if wsum else None
    out = {"_note": "Q143(g) fix pass: m1_power_e175.py, E175-A2-M1's outcome shares and dated note A2's reading, design only, before any E175 "
                    "session",
           "tiles": tiles, "groups": groups, "n": {"governed": ng, "pinned": npn, "all": len(tiles)},
           "delta_fallback": {"board_w": dw, "clock_mhz": dm, "board": dsum(dw, range(len(tiles))), "board_governed": dsum(dw, gi),
                              "board_pinned": dsum(dw, pi), "clock": dsum(dm, range(len(tiles))), "clock_governed": dsum(dm, gi),
                              "clock_pinned": dsum(dm, pi), "burst_with_no_anchor_read_gives_the_fallback": fallback_same,
                              "pinned_share_of_sum_delta": round(pinned_weight, 4) if pinned_weight is not None else None},
           "delta_sensitivity": sens, "seeds": seeds, "draws": DRAWS, "interval_index": [LO_I, HI_I], "sessions": a.sessions,
           "sens_sessions": SENS_SESSIONS, "truths": res, "sensitivity_M1": sres,
           "inputs_sha256": {"predictions-e175.json": C.sha256_file(PRED_PATH), C.PRED_REL: C.sha256_file(os.path.join(C.TOP, C.PRED_REL)),
                             "design_power_e175.py": C.sha256_file(DP.__file__), "p8gov.py": C.sha256_file(G.__file__),
                             C.A2PY_REL: C.sha256_file(os.path.join(C.TOP, C.A2PY_REL)), "m1_power_e175.py": C.sha256_file(__file__)},
           "numpy": np.__version__, "python": sys.version.split()[0]}
    if a.out:
        with open(a.out, "w") as f:
            f.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    T = ["E175-A2-M1's outcome shares and dated note A2's reading (design only; no E175 session or datum exists)", ""]
    d = out["delta_fallback"]
    T.append(f"delta = M9's part - M10 carried at the frozen fallback, {len(tiles)} kept tiles (burst() with no anchor read gives the same: {fallback_same}):")
    T.append(f"  board: mean {d['board']['mean']:+.4f} W, governed {d['board_governed']['mean']:+.4f}, pinned {d['board_pinned']['mean']:+.4f}, range "
             f"{d['board']['min']:+.3f} to {d['board']['max']:+.3f}; M9's part above M10 carried on {len(tiles) - d['board']['n_negative_M10_above'] - d['board']['n_zero']} "
             f"tiles, equal on {d['board']['n_zero']}, below on {d['board']['n_negative_M10_above']}")
    T.append(f"  clock: mean {d['clock']['mean']:+.3f} MHz, governed {d['clock_governed']['mean']:+.3f}, pinned {d['clock_pinned']['mean']:+.3f}, range "
             f"{d['clock']['min']:+.2f} to {d['clock']['max']:+.2f}")
    T.append(f"  the pinned tiles' share of sum(delta), their weight in abar_delta and so in M1's point: {d['pinned_share_of_sum_delta']:.3f}")
    T.append("delta under the session's own reads (burst() recomputed with made-up zeros-anchor reads and die starts):")
    for lab, v in sens.items():
        if "max_abs_change_from_fallback_w" in v:
            T.append(f"  {lab}: board mean {v['board']['mean']:+.4f} W (governed {v['board_governed']['mean']:+.4f}, pinned {v['board_pinned']['mean']:+.4f}), "
                     f"largest change from the fallback's {v['max_abs_change_from_fallback_w']:.4f} W")
        else:
            T.append(f"  {lab}: equal to the fallback's: {v['same_as_fallback']}")
    T.append("")
    T.append(f"Shares of {a.sessions:,} simulated sessions (%), 16 governed and 8 pinned cells each; M1 by the registered engine (seed {seeds[RULE_M1]}, "
             f"20,000 draws, [vals[{LO_I}], vals[{HI_I}]]), M1c by the same engine on each group's centred errors (seed {seeds[RULE_M1C]}):")
    T.append("  truth                 board mean gov/pin | M1 BETTER WORSE  NR | read as D (B/W)   read as level | M1c BETTER WORSE  NR | clock beside B/W/NR | point median")
    for t, r in res.items():
        tr = r["truth"]
        T.append(f"  {t:21s} {tr['gov_mean_w']:+.3f} / {tr['pin_mean_w']:+.3f} | {r['M1']['BETTER']:6.1f} {r['M1']['WORSE']:5.1f} {r['M1']['NOT RESOLVED']:5.1f} | "
                 f"{r['read_as_D_pct']:5.1f} ({r['read_as_D_BETTER_pct']:.1f}/{r['read_as_D_WORSE_pct']:.1f}) {r['read_as_level_pct']:9.1f} | "
                 f"{r['M1c']['BETTER']:6.1f} {r['M1c']['WORSE']:5.1f} {r['M1c']['NOT RESOLVED']:5.1f} | "
                 f"{r['M1_clock_beside']['BETTER']:5.1f}/{r['M1_clock_beside']['WORSE']:4.1f}/{r['M1_clock_beside']['NOT RESOLVED']:5.1f} | {r['point_median_w']:+.4f} W")
    T.append("")
    T.append("When M1 resolved, where the session's board lay (below both models' predictions: Bg's and Bp's means, M10 carried's errors, below 0;")
    T.append("above both: M9's part's errors' means above 0 in both groups; else mixed). Sessions:")
    for t, r in res.items():
        s = r["side_when_resolved"]
        T.append(f"  {t:21s} BETTER {s['BETTER']['sessions']:4d}: below both {s['BETTER']['below_both_predictions']:4d}, above both "
                 f"{s['BETTER']['above_both_predictions']:3d}, mixed {s['BETTER']['mixed']:4d} | WORSE {s['WORSE']['sessions']:4d}: above both "
                 f"{s['WORSE']['above_both_predictions']:4d}, below both {s['WORSE']['below_both_predictions']:3d}, mixed {s['WORSE']['mixed']:4d}")
    T.append("")
    T.append("Dated note A2's reading, per truth (% of sessions): M1 resolved | with the board on its side (BETTER below both, WORSE above both): "
             "the session's board level | M1c resolving the same way | read as evidence on D (resolved, not on the level's side, M1c the same):")
    for t, r in res.items():
        T.append(f"  {t:21s} resolved {r['M1_resolved_pct']:5.1f} | on the level's side {r['M1_resolved_level_side_pct']:5.1f} | M1c the same "
                 f"{r['M1c_same_pct']:4.1f} | evidence on D {r['read_as_D_pct']:4.1f} (BETTER {r['read_as_D_BETTER_pct']:.1f}, WORSE {r['read_as_D_WORSE_pct']:.1f}) | "
                 f"read as the session's level {r['read_as_level_pct']:5.1f}")
    T.append("")
    T.append("The identity: M1's point is below 0 exactly when abar_delta < theta (mismatching sessions, per truth): "
             + ", ".join(f"{t} {r['identity_mismatches']}" for t, r in res.items()) + f"; theta {res['e2e']['theta_w']:.5f} W")
    T.append("p8gov.paired itself on the first sessions of every truth (board M1, board M1c, clock beside): "
             + ", ".join(f"{t} {r['agree_with_p8gov_paired']} of {r['checked_by_p8gov_paired']}" for t, r in res.items()))
    T.append("")
    T.append(f"M1's shares with delta recomputed under the session's reads ({SENS_SESSIONS:,} sessions; BETTER / WORSE / NOT RESOLVED %):")
    for lab, v in sres.items():
        T.append(f"  {lab}: e2e {v['e2e']['BETTER']:.1f} / {v['e2e']['WORSE']:.1f} / {v['e2e']['NOT RESOLVED']:.1f}; "
                 f"e165 {v['e165']['BETTER']:.1f} / {v['e165']['WORSE']:.1f} / {v['e165']['NOT RESOLVED']:.1f}")
    bad = [t for t, r in res.items() if r["agree_with_p8gov_paired"] != r["checked_by_p8gov_paired"] or r["identity_mismatches"]]
    T.append("")
    T.append("CHECKS: " + ("every check agrees" if not bad and fallback_same else f"FAILED: {bad}, fallback reproduced {fallback_same}"))
    print("\n".join(T))
    return 0 if not bad and fallback_same else 1


if __name__ == "__main__":
    sys.exit(main())
