#!/usr/bin/env python3
"""E99: freeze the predictions. Fits E75's and E81's measured watts (posthoc_desk.py's json) with six count models, predicts
every new image and every registered contrast with an interval from those fits' residuals, and writes predictions.json.

    python3 tools/claims-v3/dm/make_predictions_e99.py --desk posthoc-desk.json --counts <gen>/counts.json --out predictions.json

The interval on an image: +- t(n - p) s sqrt(1 + x'(X'X)^-1 x), s from the residuals over the 18 measured points. On a
contrast of images, with weights c: +- t(n - p) s sqrt(sum c^2 + d'(X'X)^-1 d), d = sum c x. A count the fit could not
separate shows as a wide interval, on purpose.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from reduce_dm import CONTRASTS  # noqa: E402

MODELS = {
    "bits": ["w", "k"],                               # counting bits: E75's two prices and a floor
    "dbi": ["hi", "t_enc"],                           # the brief's simplest: high pins, encoded pin toggles, a floor
    "dbi_chan": ["hi", "t_enc", "k_chan"],            # the same with the channel's line changes
    "w_hi_chan": ["w", "hi", "k_chan"],               # ones on a path, high pins, the channel's line changes
    "w_tenc_chan": ["w", "t_enc", "k_chan"],          # ones, encoded toggles instead of high pins
    "w_traw_chan": ["w", "t_raw", "k_chan"],          # no read DBI at all: ones and raw toggles
}
T975 = {18 - 3: 2.131, 18 - 4: 2.145}                 # t quantiles for 15 and 14 degrees of freedom


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desk", required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--registered-utc", default="")
    a = ap.parse_args()
    d = json.load(open(a.desk))
    N = json.load(open(a.counts))
    C = d["counts"]
    # the two anchors with no image of their own in the counts file
    N.setdefault("dp_bern", C["dp_bern"])
    N.setdefault("dp_zeros", {t: 0.0 for t in ("w", "k", "hi", "t_enc", "t_raw", "half", "k_chan", "k_shire", "k_bank")})
    names = list(d["measured_W_over_zeros"])
    y = np.array([d["measured_W_over_zeros"][n] for n in names])
    lps = d["line_rate_per_s"]
    out = {"models": {}, "items": {}, "contrasts": {}}
    fits = {}
    for mname, terms in MODELS.items():
        X = np.vstack([np.ones(len(names))] + [[C[n][t] for n in names] for t in terms]).T
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ coef
        df = len(names) - X.shape[1]
        s = float(np.sqrt((r ** 2).sum() / df))
        XtXi = np.linalg.pinv(X.T @ X)
        fits[mname] = (terms, coef, s, XtXi, T975[df])
        out["models"][mname] = {"terms": terms, "floor_W": float(coef[0]),
                                "prices_pJ": {t: float(v / lps * 1e12) for t, v in zip(terms, coef[1:])},
                                "residual_sd_W": s, "df": df, "rms_W": float(np.sqrt((r ** 2).mean()))}

    def x_of(n, terms):
        return np.array([0.0 if n == "dp_zeros" else 1.0] + [float(N[n].get(t, 0.0)) for t in terms])

    for n in N:
        row = {}
        for mname, (terms, coef, s, XtXi, t) in fits.items():
            x = x_of(n, terms)
            if n == "dp_zeros":
                row[mname] = {"pred_W": 0.0, "pi95_W": 0.0}
                continue
            row[mname] = {"pred_W": float(x @ coef), "pi95_W": float(t * s * np.sqrt(1 + x @ XtXi @ x))}
        out["items"][n] = {"counts": {k: N[n].get(k) for k in ("w", "k", "hi", "t_enc", "t_raw", "half", "k_chan", "k_shire", "k_bank")},
                           "pred_W_over_zeros": row}
    for cn, (spec, what) in CONTRASTS.items():
        row = {}
        for mname, (terms, coef, s, XtXi, t) in fits.items():
            dv = sum(c * x_of(it, terms) for it, c in spec.items())
            sum_c2 = sum(c * c for c in spec.values())
            row[mname] = {"pred_W": float(dv @ coef), "pi95_W": float(t * s * np.sqrt(sum_c2 + dv @ XtXi @ dv))}
        out["contrasts"][cn] = {"what": what, "items": spec, "pred": row}

    main_m = out["contrasts"]
    hw = lambda c: main_m[c]["pred"]["w_hi_chan"]["pred_W"]
    frozen = {
        "exp": "E99",
        "title": "which mechanism carries the DRAM pattern effect: pins driven high after read DBI, pin toggles, and the channels' line changes",
        "question": "the part of the kinds page's section 11 item 12 that asks which mechanism carries E81's DRAM pattern effect",
        "registered_by": "a3-e99-dram (Q132), on the Intel; no card opened for this file",
        "registered_utc": a.registered_utc,
        "card": "aifoundry3 card 0 (600 MHz, nothing set)",
        "command": "E75's and E81's DRAM command unchanged: enercat_host --pattern flw_pat --harts 1 --seconds 4 --window 240000000 --operands <op> --stride 64 --slice-bytes 131072 --region 131072",
        "binary": "build/enercat-e99/host/enercat_host: E81's main.cpp with one added operand (make_host_src.py), linked as enercat-hl was, launching enercat-hl's kernel ELF unchanged",
        "decision": {
            "warmup_pass": 9910,
            "headline_passes": "9911 onward (the warm-up 9910 is reduced and reported, never in the headline)",
            "pass_gates": "E81's: anchor_pi first-to-last drift above 0.3 W sets a pass aside; so does a pass in which more than a third of its DRAM runs fail a run gate",
            "run_gates": "E81's: one clock; voltage within 3 mV of the pass median; an on-protocol launch within 0.5 C of 58 C after a 59 C preheat; window median took_ms <= 60 ms; an ok device record",
            "estimator": "E81's: per kept pass each item's leakage-corrected board power p80 over [t0+1 s, t0+3 s); every contrast a within-pass difference; the mean over headline passes with a two-sided t interval on their scatter (df = n - 1); W to pJ per 64 B line with the measured line rate",
            "primary_arm": "dips removed: dp/posthoc_dips.py's definition (E82 A2's), board_w[i] < min(board_w[i-2], board_w[i+2]) - 4 W, registered here before any data; the unfiltered arm is reported beside it, and any verdict that differs between the two is named",
            "leak": "E81's auto (median within-run slope); 0.2936 and 0.3803 W/C reported as sensitivities",
            "min_headline_passes": 3,
            "present_min_W": 0.25,
            "absent_half_W": 0.30,
            "classes": "E81's: PRESENT when the mean is >= 0.25 W and the 95 % interval excludes 0; ABSENT when the 95 % interval lies inside +-0.30 W; otherwise UNRESOLVED",
            "budget": "at most 33 card-minutes in all: a smoke of about 2 min, then up to six passes of about 5 min; no pass starts once the session's card clock has passed 27 min, or after 01:50 PDT (the next lane on this card), by touching build/mf-STOP; a pass that has started finishes. Fewer than three headline passes: every verdict UNRESOLVED",
            "order": "runitems.py's: anchor_pi first and last, the DRAM items shuffled per pass by Random('aifoundry3|<pass>|<pass>')"
        },
        "bands": {
            "tie": {"tie_total": {"e81": 1.636, "within": 0.35}, "tie_c2": {"e81": 1.866, "within": 0.35},
                    "tie_bern": {"e81": 3.501, "within": 0.35}, "tie_c1": {"e81": 2.046, "within": 0.40}},
            "hi_t0": [round(0.5 * hw("hi_t0"), 2), round(2 * hw("hi_t0"), 2)],
            "hi_ta": [round(0.5 * hw("hi_ta"), 2), round(2 * hw("hi_ta"), 2)],
            "tent_S": [round(0.5 * hw("tent_S"), 2), round(2 * hw("tent_S"), 2)],
            "tie_ones": {"tie27": 320, "tie45": 64, "tie18": 448},
            "h32_fraction": [0.15, 0.85],
            "closure_within_W": 0.30,
            "rail_within_W": 0.10
        },
        "fits": out["models"],
        "items": out["items"],
        "contrasts": out["contrasts"],
    }
    json.dump(frozen, open(a.out, "w"), indent=1)
    print("bands:", json.dumps({k: frozen["bands"][k] for k in ("hi_t0", "hi_ta", "tent_S")}))
    for m_, v in out["models"].items():
        print("%-12s floor %+.3f W  %s  sd %.3f W rms %.3f" % (m_, v["floor_W"], "  ".join("%s %.3f pJ" % kv for kv in v["prices_pJ"].items()), v["residual_sd_W"], v["rms_W"]))
    show = ["w_hi_chan", "dbi", "w_tenc_chan", "w_traw_chan", "bits"]
    print("%-14s " % "contrast" + " ".join("%-18s" % s for s in show))
    for cn, c in out["contrasts"].items():
        print("%-14s " % cn + " ".join("%+6.2f +-%-9.2f" % (c["pred"][s]["pred_W"], c["pred"][s]["pi95_W"]) for s in show))


if __name__ == "__main__":
    main()
