#!/usr/bin/env python3
"""Q140(l): M9's aifoundry2 part, the frozen prediction code. Nothing here refits: every number comes from m9_a2.json.

As a module (Q140(m)'s predict_blind7.py imports it for aifoundry2):

    import predict_m9_a2 as A2
    A2.burst(D, t, anchors=None, die_starts=None, D_band_hw=0.0) -> dict

    D           the tile's switching watts over its format's zeros at 600 MHz on aifoundry3's footing (Q139(u)'s), W
    t           'fp32' | 'fp16' | 'int8'
    anchors     the session's own zeros-anchor reads: {format: [{"burst_w": W, "burst_mhz": MHz, "die_start": C}, ...]}, one
                entry per anchor burst (E80's harness, a 6 s burst); only bursts at 795 MHz or more count; a format with
                none takes the mean of the session's other formats; None (no anchor has run) takes m9_a2.json's fallback
    die_starts  the die reading at each of the tile's bursts' starts (C); None takes T_ref (54.38 C) and the result says so
    D_band_hw   the 600 MHz model's 95% half-width on D (W), used only for the 82 W admission value, as predict_blind6.py did

It returns the burst clock (MHz), the board power in the burst (W), the burst D (board less the format's zeros board in
the same session at its own clock), the die rise over a burst (C), each with its frozen 95% band; M8's peak rule
unchanged (expected and 95% upper, the 82 W flag); and the sensitivities of the clock and board to the session's zeros
level (per W of the anchor offset) and to the die start (per C), so a blind protocol can freeze its predictions before
the anchors run and recompute them mechanically afterwards.

As a script:

    python3 predict_m9_a2.py <tiles.json> [--model M9] [--anchors <anchors.json>] [--die-start C] [--out <file.json>]

<tiles.json> is a list of {"name", "type", "D600_a3_footing_w"[, "D_band_hw"]} or a predictions file with a "tiles" dict
whose records carry <model>.D600_a3_footing_w (predict_blind6.py's layout; --model picks the model, M9 by default).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e119"))
import make_predictions_e119 as M119  # noqa: E402  (E83's dither, unchanged)

M9P = os.path.join(HERE, "m9_a2.json")
M9 = json.load(open(M9P))
M9_SHA256 = hashlib.sha256(open(M9P, "rb").read()).hexdigest()
REL, PAR, CFG = M9["relation"], M9["params"], M9["config"]
B = {int(k): v for k, v in REL["B_w"].items()}
S = {int(k): v for k, v in REL["s_f"].items()}
CZ, G, SIG = REL["c_zeros_w"], REL["g"], REL["sigma_w"]
W, DCAP, BETA, KT, TREF = PAR["W"], PAR["dcap_w"], PAR["beta"], PAR["kT_w_per_c"], PAR["T_ref_c"]
BANDS, HEAT, PEAK, M8P = M9["bands"], M9["burst_heat"], M9["peak"], M9["M8_params_for_the_peak"]
MIN_ANCHOR_MHZ = 795.0
TYPES = ("fp32", "fp16", "int8")


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def p_at(L, f):
    if f >= 800:
        return L[800]
    if f >= 700:
        return L[700] + (L[800] - L[700]) * (f - 700) / 100.0
    return L[600] + (L[700] - L[600]) * (f - 600) / 100.0 if f >= 600 else L[600]


def session_delta(anchors):
    """per format: the mean over the anchor's bursts at >= 795 MHz of burst_w - L(800; c_zeros), each referred to T_ref by
    the die-start term when it is kept; formats with none take the mean of the others; no anchors at all: the fallback"""
    if not anchors:
        return dict(M9["fallback_delta_w"]), "fallback (no zeros-anchor read)"
    out = {}
    for t, rr in anchors.items():
        rr = [r for r in rr if float(r["burst_mhz"]) >= MIN_ANCHOR_MHZ]
        if not rr:
            continue
        Lz = B[800] + CZ[t] * S[800]
        out[t] = sum(float(r["burst_w"]) - Lz - (KT * (float(r["die_start"]) - TREF) if CFG["T3"] else 0.0) for r in rr) / len(rr)
    if not out:
        return dict(M9["fallback_delta_w"]), "fallback (no anchor burst at 795 MHz or more)"
    have = dict(out)
    for t in TYPES:
        if t not in out:
            out[t] = sum(have.values()) / len(have)
    return out, "the session's own zeros anchors" + (f" (formats filled from the others: {sorted(set(TYPES) - set(have))})" if len(have) < 3 else "")


def _run(c, t, delta, T):
    sh = (BETA * delta[t] if CFG["T2"] else 0.0) + (KT * (T - TREF) if CFG["T3"] else 0.0)
    L = {f: B[f] + c * S[f] + sh for f in (600, 700, 800)}
    f = M119.dither(L, W, SIG)[0]
    P = p_at(L, f) + (DCAP * phi((L[800] - W) / SIG) if CFG["T1"] else 0.0)
    return f, P


def _cell(c, t, delta, Ts):
    fs, Ps = zip(*[_run(c, t, delta, T) for T in Ts])
    return sum(fs) / len(fs), sum(Ps) / len(Ps)


def burst(D, t, anchors=None, die_starts=None, D_band_hw=0.0):
    delta, dsrc = session_delta(anchors)
    Ts = [float(x) for x in die_starts] if die_starts else [TREF]
    c = CZ[t] + G * D
    f, P = _cell(c, t, delta, Ts)
    fz, Pz = _cell(CZ[t], t, delta, Ts)
    grp = "governed" if f < 795.0 else "pinned"
    bd = BANDS[grp]
    # sensitivities (finite differences, 0.1 W of the anchor offset and 0.5 C of die start)
    d2 = {k: v + 0.1 for k, v in delta.items()}
    f2, P2 = _cell(c, t, d2, Ts)
    f3, P3 = _cell(c, t, delta, [x + 0.5 for x in Ts])
    # M8's peak rule, unchanged (no level shift): the 82 W admission value
    c8 = M8P["c_zeros_w"][t] + M8P["g"] * D
    c8hi = M8P["c_zeros_w"][t] + M8P["g"] * (D + D_band_hw)
    P800 = M8P["B_w"]["800"] + c8 * M8P["s_f"]["800"]
    P800hi = M8P["B_w"]["800"] + c8hi * M8P["s_f"]["800"]
    rise = HEAT["k_used_c_per_w"] * (P - HEAT["P_idle_w"])
    return {"burst_mhz": round(f, 2), "burst_mhz_95": [round(f - bd["q95_abs_mhz"], 2), round(min(800.0, f + bd["q95_abs_mhz"]), 2)],
            "burst_board_w": round(P, 3), "burst_board_95": [round(P - bd["q95_abs_board_w"], 3), round(P + bd["q95_abs_board_w"], 3)],
            "burst_D_w": round(P - Pz, 3), "burst_D_95": [round(P - Pz - bd["q95_abs_board_w"], 3), round(P - Pz + bd["q95_abs_board_w"], 3)],
            "burst_die_rise_c": round(rise, 3), "burst_die_rise_95": [round(rise - HEAT["q95_abs_c"], 3), round(rise + HEAT["q95_abs_c"], 3)],
            "group": grp, "zeros_board_w": round(Pz, 3),
            "P800_w": round(P800, 2), "P800_M8_w": round(P800, 3), "peak_board_w": round(P800 + PEAK["excess_median_w"], 3),
            "clock_term": "M9's (m9_a2.json: " + "+".join(M9["kept_terms"]) + "; peak: M8's rule unchanged)",
            "peak_board_hi95_w": round(P800hi + PEAK["excess_q95_w"], 3), "peak_over_82w": bool(P800hi + PEAK["excess_q95_w"] > 82.0),
            "delta_w": {k: round(v, 4) for k, v in delta.items()}, "delta_source": dsrc,
            "die_starts_c": Ts, "die_start_source": "given" if die_starts else f"T_ref {TREF:.2f} C (none given)",
            "d_mhz_per_w_of_delta": round((f2 - f) / 0.1, 3), "d_board_per_w_of_delta": round((P2 - P) / 0.1, 4),
            "d_mhz_per_c_die_start": round((f3 - f) / 0.5, 3), "d_board_per_c_die_start": round((P3 - P) / 0.5, 4),
            "model": "M9 aifoundry2 part (Q140(l), m9_a2.json)", "m9_a2_sha256": M9_SHA256}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles")
    ap.add_argument("--model", default="M9")
    ap.add_argument("--anchors", default=None)
    ap.add_argument("--die-start", type=float, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    T = json.load(open(a.tiles))
    if isinstance(T, dict) and isinstance(T.get("tiles"), dict):
        items = [{"name": n, "type": r["type"], "D600_a3_footing_w": r[a.model]["D600_a3_footing_w"],
                  "D_band_hw": (r[a.model].get("D_95", [0, 0])[1] - r[a.model].get("D_95", [0, 0])[0]) / 2.0 if r[a.model].get("D_95") else 0.0}
                 for n, r in sorted(T["tiles"].items()) if a.model in r]
    else:
        items = T
    anchors = json.load(open(a.anchors)) if a.anchors else None
    ds = [a.die_start] if a.die_start is not None else None
    out = {"_note": "Q140(l) predict_m9_a2.py: M9's aifoundry2 part, frozen; nothing refitted", "m9_a2_sha256": M9_SHA256,
           "anchors": a.anchors, "tiles": {}}
    for it in items:
        out["tiles"][it["name"]] = dict(burst(float(it["D600_a3_footing_w"]), it["type"], anchors, ds, float(it.get("D_band_hw", 0.0))),
                                        type=it["type"], D600_a3_footing_w=it["D600_a3_footing_w"])
    s = json.dumps(out, indent=1, sort_keys=True)
    if a.out:
        open(a.out, "w").write(s + "\n")
    print(s)


if __name__ == "__main__":
    main()
