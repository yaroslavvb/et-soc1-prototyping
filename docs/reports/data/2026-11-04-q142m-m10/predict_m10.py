#!/usr/bin/env python3
"""Q142(m): M10's frozen predictor, from m10.json alone (the prices, the card term, the session-scale rule and the heat terms that
entered by tools/claims-v3/m10/REGISTRATION.md). No fit. No pool and no prediction for any tile that has not run is made here:
the only run is the self-test, on committed rows.

    python3 -B predict_m10.py selftest      # pool 7's 104 rows: D from m10.json, each tile's features and its session's anchors,
                                           # against fit_m10.py's in-sample predictions in rows-m10.json (every row within 1e-9 W)

As a module:
  d600(f, t, rate, card, m10, s=1.0)        D at 600 MHz (W): s x card term (card 1) x rate x sum(price x feature); f = M9's feature dict
                                           (for a case-S tile, from its N-point counts by RECOUNT-RULE.md, if term b entered)
  session_scale(anchors, fam, card, m10)    s for one session and family: the median over the session's random anchors (dicts with
                                           f, type, rate and the measured D) of D / (rate x pass-1 prices x features x card term); 1 if none
  rise_4p5s(S, T_run, card, m10)            the 4.5 s window rise (C): M7's form with M10's refitted per-card coefficients
  rise_card0_burst(P_board, m10)            card 0's 6 s burst rise (C) at a board power (W)
  chain_gain(m10)                           1 + gamma, the factor on Q138(t)'s chain's rise (None if term d did not enter)
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
fam_of = lambda t: "int8" if t == "int8" else "float"  # noqa: E731
HEAT_CARD = {"a3": "aifoundry3", "c1": "aifoundry1-c1"}


def load_m10(path=None):
    return json.load(open(path or os.path.join(HERE, "m10.json")))


def _dot(f, terms, coef, rate):
    return rate * sum(float(f[q]) * c for q, c in zip(terms, coef))


def d600(f, t, rate, card, m10, s=1.0):
    fm = m10["families"][fam_of(t)]
    c = fm["card1_scale"] if card == "c1" else 1.0
    return s * c * _dot(f, fm["terms"], fm["coef_J"], rate)


def session_scale(anchors, fam, card, m10):
    fm = m10["families"][fam]
    if not fm.get("session_scale"):
        return 1.0
    c = fm["card1_scale"] if card == "c1" else 1.0
    rat = []
    for a in anchors:
        if fam_of(a["type"]) != fam or a["name"] not in fm["session_scale"]["anchors"]:
            continue
        dh = c * _dot(a["f"], fm["terms"], fm["pass1_coef_J"], a["rate"])
        if dh > 0:
            rat.append(a["D"] / dh)
    return statistics.median(rat) if rat else 1.0


def rise_4p5s(S, T_run, card, m10):
    co = m10["heat_4p5s"]["coef"]
    hc = HEAT_CARD[card]
    return co[f"S|{hc}"] * S + co[f"ST|{hc}"] * S * (T_run - 4.5)


def rise_card0_burst(P_board, m10, P_idle=21.5):
    return m10["card0_burst_heat_k_c_per_w"] * (P_board - P_idle)


def chain_gain(m10):
    g = m10.get("heat_chain_gain")
    if not g:
        return None
    return 1.0 + (g["gamma"]["all"] if g["variant"] == "common" else None)


def selftest():
    sys.path.insert(0, HERE)
    import fit_m10 as FM  # noqa: E402  (its assembly and feature chain only; nothing is fitted)
    m10 = load_m10()
    rows, _ = FM.assemble()
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    anchors, _ = FM.assemble_anchors(rows, zeros, zr)
    rc = FM.recount(os.path.join(HERE, "bench"), zeros, zr) if m10["entered"].get("b") else {}
    ref = {(r["exp"], r["key"]): r["M10_insample_pred_w"] for r in json.load(open(os.path.join(HERE, "rows-m10.json")))}
    worst, n = 0.0, 0
    for r in rows:
        if r["exp"] not in ("E163", "E164"):
            continue
        fam = fam_of(r["type"])
        f = rc[r["key"]]["fN"] if (fam == "float" and r["S_class"] and r["key"] in rc) else r["f"]
        s = session_scale(anchors.get(r["sess"], []), fam, r["card"], m10)
        d = d600(f, r["type"], r["rate"], r["card"], m10, s)
        worst = max(worst, abs(d - ref[(r["exp"], r["key"])]))
        n += 1
    ok = n == 104 and worst <= 1e-9
    print(json.dumps({"selftest": "PASS" if ok else "FAIL", "rows": n, "max_abs_diff_w": worst}))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    print(__doc__)
