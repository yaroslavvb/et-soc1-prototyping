#!/usr/bin/env python3
"""E67's two random-word closures re-priced at one measured leakage slope — E71's sensitivity.

    python3 closure_refit.py [--out closure-sensitivity.json]

E67's closure compares a measured random-word step against the step its own single-bit price list predicts:

    predicted_W = (sum_i flips_i * price_i[fJ] * 1e-15) * rate_ops_s      (closure.json's J_*_per_op * rate)
    ratio       = measured_W / predicted_W

Both sides are de-leaked prices, so both move when k moves, and the *ratio* is what E70's verdict on the ~2x
over-count rests on. This script moves both sides together, from the committed per-item shifts only:

- the A-side list, position by position, by `sensitivity-e67.json`'s `abit_<i>` shift (E67's registered reduction,
  which is the reduction `closure.json` was built in);
- the B-side list by `sensitivity-e65-ab.json`'s `bit_<i>` shift (closure.json's `b_price_fJ` IS E65's published
  B-side list);
- the measured side by the same reduction's `nrd_a` / `nrd_b` shift.

fJ per flipped bit is a price divided by designed flips and the measured rate, and neither moves with k, so the
relative price shift IS the relative fJ shift. The script refuses to report anything unless it first reproduces
closure.json's own published `predicted_W` and `ratio_measured_over_predicted` from the committed histograms
(checked to 1e-9 W / 1e-9), exactly as `leak_sensitivity.py` reproduces a published price before re-pricing it.

Nothing published is rewritten: E67's `closure.json` is read-only here and the output is a labelled sensitivity.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E67 = os.path.join(HERE, "..", "2026-10-27-e67-a-side-bit-prices")
TOL = 1e-9


def pct(name, sens):
    """the committed relative shift of one item's price, as a factor"""
    return 1.0 + sens["items"][name]["shift_pct"] / 100.0


def energy(hist, price_fJ):
    return sum(hist[i] * price_fJ[str(i)] * 1e-15 for i in range(len(hist)))


def main(out):
    clo = json.load(open(os.path.join(E67, "closure.json")))
    s67 = json.load(open(os.path.join(HERE, "sensitivity-e67.json")))
    s65 = json.load(open(os.path.join(HERE, "sensitivity-e65-ab.json")))
    a_old = clo["a_price_fJ"]
    b_old = clo["b_price_fJ"]
    a_new = {k: v * pct("abit_%s" % k, s67) for k, v in a_old.items()}
    b_new = {k: v * pct("bit_%s" % k, s65) for k, v in b_old.items()}

    res = {"k_new": s67["summary"]["k_new"],
           "k_old_e67": s67["summary"]["k_old"], "k_old_e65_ab": s65["summary"]["k_old"],
           "source": "docs/reports/data/2026-10-27-e67-a-side-bit-prices/closure.json",
           "check": {"ok": True, "worst_predicted_err_W": 0.0, "worst_ratio_err": 0.0},
           "items": {}}
    for name, it in clo["items"].items():
        rate = it["rate_ops_s"]
        pred_old = (energy(it["A_hist"], a_old) + energy(it["B_hist"], b_old)) * rate
        pred_new = (energy(it["A_hist"], a_new) + energy(it["B_hist"], b_new)) * rate
        ratio_old = it["measured_W"] / pred_old
        err_p = abs(pred_old - it["predicted_W"])
        err_r = abs(ratio_old - it["ratio_measured_over_predicted"])
        res["check"]["worst_predicted_err_W"] = max(res["check"]["worst_predicted_err_W"], err_p)
        res["check"]["worst_ratio_err"] = max(res["check"]["worst_ratio_err"], err_r)
        if err_p > TOL or err_r > TOL:
            res["check"]["ok"] = False
        meas_new = s67["items"][name]["price_new_W"]
        meas_old = s67["items"][name]["price_old_W"]
        side = "A" if it["A_bits"] else "B"
        res["items"][name] = {
            "side": side,
            "predicted_W_published": it["predicted_W"], "predicted_W_at_e71_k": pred_new,
            "predicted_pct": 100 * (pred_new - pred_old) / pred_old,
            "measured_W_published": it["measured_W"], "measured_W_at_e71_k": meas_new,
            "measured_pct": 100 * (meas_new - meas_old) / meas_old,
            "ratio_published": it["ratio_measured_over_predicted"], "ratio_at_e71_k": meas_new / pred_new,
        }
    if not res["check"]["ok"]:
        print("REFUSED: closure.json's published predicted_W / ratio did not reproduce "
              "(worst %.3e W, %.3e)" % (res["check"]["worst_predicted_err_W"], res["check"]["worst_ratio_err"]))
        return 1
    for name in sorted(res["items"]):
        r = res["items"][name]
        print("%-6s %s-side  predicted %8.4f -> %8.4f W (%+.2f %%)  measured %7.4f -> %7.4f W (%+.2f %%)  "
              "ratio %.4f -> %.4f" % (name, r["side"], r["predicted_W_published"], r["predicted_W_at_e71_k"],
                                      r["predicted_pct"], r["measured_W_published"], r["measured_W_at_e71_k"],
                                      r["measured_pct"], r["ratio_published"], r["ratio_at_e71_k"]))
    print("check: published predicted_W and ratio reproduced to %.1e W / %.1e"
          % (res["check"]["worst_predicted_err_W"], res["check"]["worst_ratio_err"]))
    if out:
        json.dump(res, open(out, "w"), indent=1, sort_keys=True)
        print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    out = a[a.index("--out") + 1] if "--out" in a else None
    sys.exit(main(out))
