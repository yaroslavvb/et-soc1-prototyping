#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q133(b): 95% intervals for the seven contrasts built into blind pool 3, a dated addendum to the frozen predictions.

    python3 contrasts_blind3.py     # writes tools/claims-v3/kinds/blind3/contrasts-blind3.json and .md

Written after verification on Sun 1 Nov 2026, after predictions-blind3.json was frozen (64b4124e) and before any card had
run a pool tile or E115 had claimed a card. It reads the frozen predictions and changes nothing in them: each contrast's
point is the difference of the two tiles' frozen predictions, and its interval on a3 and c1 is the two tiles' frozen 95%
half-widths combined in quadrature. That is the stand-in the verifier asked for. It treats the two tiles' errors as
independent; where they are positively correlated (constants shared by both tiles, one session) it is conservative, and
corrections-check.py C5 tries it on pairs of training kinds. On `new` (a card with no scale of its own) the tiles' own
rule is applied to the contrast: a3's interval widened by one card's step on the contrast, t x |1 - s| x D, in
quadrature; the two tiles' `new` half-widths in quadrature, which count the step on each tile's whole D, are kept beside it
as the most conservative figure. Beside them, for M5 on a3 and as a check: the tiles' own formula applied to the
difference, so the constants' share cancels, t x sqrt(pool^2 + pool^2 + (x1 - x2)' C (x1 - x2) + m1^2 + m2^2). Also each
contrast's split by M5's terms, on a3.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit_m5 as F  # noqa: E402  (t975 and the paths only)

POOL = os.path.join(F.K, "blind3")
sha_file = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
CONTRASTS = (
    ("fp32.g_blanes_alt", "fp32.g_blanes_steady", "gate switching every cycle against a steady gate, same gated fraction"),
    ("fp32.a_lo8_b_randn", "fp32.a_lo8_b_pi", "the same A side with a busy and a quiet partner"),
    ("fp32.m_blines_eq", "fp32.m_bpair_eq", "B alternating in-lane with no line changes, against lines changing with no in-lane alternation"),
    ("fp32.s_drift12", "fp32.s_pair0", "a sum that drifts up against one that returns to 0"),
    ("fp32.s_bridge", "fp32.s_pair0", "a sum that climbs and walks back against one that returns every step"),
    ("fp32.x_logu_s50", "fp32.x_logu_bsteady", "exponents spread: a random 50% word gate against a steady lane gate"),
    ("fp16.s_wpair0", "fp16.s_inword0", "fp16: cancelling across k-groups against inside the two-term update"),
)
DESCRIPTORS = ("a_line_bits", "a_halfline_bits", "b_line_bits", "b_halfline_bits", "a_bus_bits_per_op", "b_bus_bits_per_op")


def main():
    pp = os.path.join(POOL, "predictions-blind3.json")
    mp = os.path.join(HERE, "m5.json")
    sp = os.path.join(POOL, "blind3.json")
    PJ = F.load(pp)
    P, PM4 = PJ["tiles"], PJ["models"]["M4"]
    M5 = F.load(mp)["families"]
    spec = F.load(sp)["tiles"]
    out = []
    worst_check = 0.0
    for plus, minus, what in CONTRASTS:
        a, b = P[plus], P[minus]
        t = a["type"]
        assert b["type"] == t
        rec = {"contrast": f"{plus} - {minus}", "plus": plus, "minus": minus, "type": t, "isolates": what,
               "priorities": [a["priority"], b["priority"]]}
        fam_ = "int8" if t == "int8" else "float"
        for w in ("M5", "M4"):
            if w == "M5":
                s1, pa3 = M5[fam_]["card1_scale"], M5[fam_]["interval_pool_by_format_card"][f"{t}|a3"]
            else:
                s1, pa3 = PM4[fam_]["card1_scale"], PM4[fam_]["interval_pool"]
            r = {}
            for foot in ("a3", "c1"):
                d = a[w][foot]["D_w"] - b[w][foot]["D_w"]
                h = math.hypot(a[w][foot]["half95"], b[w][foot]["half95"])
                r[foot] = {"D_w": d, "half95": h, "lo95": d - h, "hi95": d + h}
            # a card with no scale: as the tiles' own 'new' footing, a3's interval widened by one card's step, here on the
            # contrast itself, t x |1 - s| x D(contrast), in quadrature
            d = r["a3"]["D_w"]
            h = math.hypot(r["a3"]["half95"], F.t975(pa3["n"] - 2) * abs(1 - s1) * d)
            hq = math.hypot(a[w]["new"]["half95"], b[w]["new"]["half95"])
            r["new"] = {"D_w": d, "half95": h, "lo95": d - h, "hi95": d + h, "half95_tiles_new_in_quadrature_most_conservative": hq}
            rec[w] = r
        # M5 on a3: the tiles' own interval formula on the difference (constants shared), as a check
        fam = "int8" if t == "int8" else "float"
        M = M5[fam]
        coef, C = np.array(M["coef_J"]), np.array(M["cov_J2"])
        pool = M["interval_pool_by_format_card"][f"{t}|a3"]
        tq = F.t975(pool["n"] - 2)
        xs, ms = [], []
        for r_ in (a, b):
            x = np.array(r_["M5"]["terms_w_a3"]) / coef
            lp = r_["M5"]["launch_points_w_a3"]
            m = float(np.std(lp, ddof=1) / math.sqrt(len(lp)))
            own = tq * math.sqrt(pool["rms_w"] ** 2 + float(x @ C @ x) + m * m)
            worst_check = max(worst_check, abs(own - r_["M5"]["a3"]["half95"]))
            xs.append(x)
            ms.append(m)
        dx = xs[0] - xs[1]
        shared = tq * math.sqrt(2 * pool["rms_w"] ** 2 + float(dx @ C @ dx) + ms[0] ** 2 + ms[1] ** 2)
        rec["M5"]["a3"]["half95_constants_shared_check"] = shared
        rec["M5_terms_w_a3"] = dict(zip(a["M5"]["terms"], [float(u - v) for u, v in zip(a["M5"]["terms_w_a3"], b["M5"]["terms_w_a3"])]))
        rec["descriptors"] = {plus: {k: spec[plus]["stats"].get(k) for k in DESCRIPTORS}, minus: {k: spec[minus]["stats"].get(k) for k in DESCRIPTORS}}
        out.append(rec)
    assert worst_check < 1e-9, worst_check
    doc = {
        "what": "Q133(b): 95% intervals for blind pool 3's seven contrasts, a dated addendum to predictions-blind3.json (which it does not change)",
        "written": "Sun 1 Nov 2026 PST, after verification; after predictions-blind3.json's freeze (64b4124e), before any card ran a pool tile and before E115's claim",
        "answers": "https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open item 6",
        "method": "point = difference of the two tiles' frozen predictions on each footing; half95 on a3 and c1 = the two tiles' frozen 95% half-widths in quadrature "
                  "(errors treated as independent: conservative where they are positively correlated); on new = a3's half95 and t(0.975, n_a3 - 2) x |1 - card-1 scale| x D "
                  "in quadrature (the tiles' own new-card rule applied to the contrast), with the tiles' new half-widths in quadrature kept as the most conservative figure. "
                  "half95_constants_shared_check (M5, a3): "
                  "t(0.975, n - 2) x sqrt(2 pool^2 + (x1 - x2)'C(x1 - x2) + m1^2 + m2^2), a check, not the frozen interval. "
                  "M5_terms_w_a3: the contrast split by M5's terms on a3. descriptors: make_kinds.tile_stats' line and half-line bits from blind3.json",
        "units": "W over the type's own zeros at 600 MHz (E78's reduction); footings a3 / c1 / new as predict_blind3.py says",
        "frozen_inputs": {
            "predictions-blind3.json": {"path": "tools/claims-v3/kinds/blind3/predictions-blind3.json", "sha256": sha_file(pp)},
            "m5.json": {"path": "docs/reports/data/2026-11-01-q133b-power-model/m5.json", "sha256": sha_file(mp)},
            "blind3.json": {"path": "tools/claims-v3/kinds/blind3/blind3.json", "sha256": sha_file(sp)},
            "contrasts_blind3.py": {"path": "docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py", "sha256": sha_file(os.path.abspath(__file__))},
        },
        "tile_half95_reproduced_max_abs_w": worst_check,
        "contrasts": out,
    }
    jp = os.path.join(POOL, "contrasts-blind3.json")
    json.dump(doc, open(jp, "w"), indent=1, sort_keys=True)
    with open(os.path.join(POOL, "contrasts-blind3.md"), "w") as fo:
        w = fo.write
        w("# Blind pool 3: the contrasts' 95% intervals (Q133(b), a dated addendum for E115)\n\n"
          "Written by `docs/reports/data/2026-11-01-q133b-power-model/contrasts_blind3.py` on Sun 1 Nov 2026, after verification: after "
          "`predictions-blind3.json` was frozen (`64b4124e`) and before any card ran a pool tile. D in W over the type's own zeros at 600 MHz. "
          "Each point is the difference of the two tiles' frozen predictions. On a3 and c1 each interval is the two tiles' frozen 95% half-widths in "
          "quadrature (the errors treated as independent). On a new card it is a3's interval widened by one card's step on the contrast, "
          "t × |1 − s| × D, the rule the tiles' own `new` footing uses; the two tiles' `new` half-widths in quadrature, which count the step on "
          "each tile's whole D, are in `contrasts-blind3.json` as the most conservative figure. The last column is a check, not the interval: "
          "the tiles' own formula on the difference, with the constants' share cancelling.\n\n")
        w("| contrast | what it isolates | **M5, a3 [95%]** | M5, c1 [95%] | M5, new card [95%] | M4, a3 [95%] | M5 a3 ± if constants shared |\n|---|---|---:|---:|---:|---:|---:|\n")
        for r in out:
            a3, c1, nw, m4 = r["M5"]["a3"], r["M5"]["c1"], r["M5"]["new"], r["M4"]["a3"]
            w(f"| `{r['contrast']}` | {r['isolates']} | **{a3['D_w']:+.2f}** [{a3['lo95']:+.2f}, {a3['hi95']:+.2f}] | {c1['D_w']:+.2f} [{c1['lo95']:+.2f}, {c1['hi95']:+.2f}] | "
              f"{nw['D_w']:+.2f} [{nw['lo95']:+.2f}, {nw['hi95']:+.2f}] | {m4['D_w']:+.2f} [{m4['lo95']:+.2f}, {m4['hi95']:+.2f}] | ±{a3['half95_constants_shared_check']:.2f} |\n")
        w("\n**Each contrast split by M5's terms** (W, a3):\n\n| contrast | " + " | ".join(out[0]["M5_terms_w_a3"]) + " |\n|---|" + "---:|" * len(out[0]["M5_terms_w_a3"]) + "\n")
        for r in out:
            w(f"| `{r['contrast']}` | " + " | ".join(f"{v:+.2f}" for v in r["M5_terms_w_a3"].values()) + " |\n")
        m = next(r for r in out if r["plus"] == "fp32.m_blines_eq")
        dp, dm = m["descriptors"]["fp32.m_blines_eq"], m["descriptors"]["fp32.m_bpair_eq"]
        w(f"\n**The memory-path pair, by what a path would carry** (bits an op, `make_kinds.tile_stats` in `blind3.json`): B line to line "
          f"{dp['b_line_bits']:,} (`m_blines_eq`) against {dm['b_line_bits']:,} (`m_bpair_eq`); B half-line to half-line {dp['b_halfline_bits']:,} against "
          f"{dm['b_halfline_bits']:,}; A line to line {dp['a_line_bits']:,} against {dm['a_line_bits']:,}. The bench has no memory path, so its "
          f"{m['M5']['a3']['D_w']:+.2f} W is all compute and the operand bus. A card reading below the interval would fit a cost for B lines that "
          "change (only `m_bpair_eq`'s do), one above it a cost for half-lines that change (`m_blines_eq`'s change about twice as often); either "
          "could instead be compute the bench misprices.\n")
    print(json.dumps({"contrasts": len(out), "sha256": sha_file(jp), "tile_half95_reproduced_max_abs_w": worst_check}))


if __name__ == "__main__":
    main()
