#!/usr/bin/env python3
"""E67 (Q128): the constant-operand spread, a pass-health diagnostic the registered gates do not have.

    python3 tools/claims-v3/ha/constspread.py <runs.csv> [--limit 0.40] [--json out.json]

Every pass of E67 runs several items whose operands never change from one micro-op to the next — `aq_h0`,
`aq_e64`, `ap_h0`, `lq_h0`, `lb_h0`, `ix_z` and the two `anchor_pi` runs. They are the same physical state
reached by different routes, so within one pass they should read the same board power to within the meter's
noise. The spread of those runs is therefore a direct, assumption-free measure of how trustworthy the pass is.

The registered pass gate (E60's, inherited) is `anchor_pi` first-versus-last drifting more than 0.3 W. That
catches a pass that warms monotonically. It does **not** catch a pass in which individual runs dip, because
`anchor_pi`'s own two runs can both be fine. On E67 the two diagnostics disagree: pass 754 trips the registered
gate at a 0.62 W spread, and passes 755-757, at 0.97-2.02 W, do not trip it at all.

This script is a diagnostic and a lesson, not a gate: nothing here re-scores a registered rule. Pure Python.
"""
import argparse
import csv
import json
import statistics

CONST = ("aq_h0", "aq_e64", "ap_h0", "lq_h0", "lb_h0", "ix_z", "anchor_pi")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs")
    ap.add_argument("--limit", type=float, default=0.40,
                    help="the spread at or below which a pass is called clean (a post-hoc sensitivity cut, "
                         "never a registered gate)")
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(a.runs)) if not r["fail"] or r["fail"] == "[]"]
    passes = {}
    for r in rows:
        passes.setdefault(int(r["pass"]), []).append(r)
    out = {"limit_W": a.limit, "passes": {}}
    print(f"{'pass':>5} {'const':>5} {'spread W':>9} {'median W':>9} {'worst dip':>10} "
          f"{'pi drift':>9} {'rate Ge/s':>10}  clean?")
    for p in sorted(passes):
        rs = passes[p]
        c = [float(r["p80"]) for r in rs if r["item"] in CONST]
        if len(c) < 2:
            continue
        pis = sorted((r for r in rs if r["item"] == "anchor_pi"), key=lambda r: int(r["pos"]))
        drift = (float(pis[-1]["p80"]) - float(pis[0]["p80"])) if len(pis) > 1 else None
        med, spread = statistics.median(c), max(c) - min(c)
        rate = statistics.mean(float(r["rate"]) for r in rs)
        clean = spread <= a.limit
        out["passes"][p] = {"n_const": len(c), "spread_W": spread, "median_W": med,
                            "worst_dip_W": med - min(c), "anchor_pi_drift_W": drift,
                            "mean_rate_ops_s": rate, "clean": clean,
                            "low_runs": [r["item"] for r in rs
                                         if r["item"] in CONST and float(r["p80"]) < med - 0.8]}
        print(f"{p:>5} {len(c):>5} {spread:>9.2f} {med:>9.2f} {med-min(c):>10.2f} "
              f"{(drift if drift is not None else float('nan')):>+9.3f} {rate/1e9:>10.3f}  "
              f"{'yes' if clean else 'NO'}")
    clean = sorted(p for p, d in out["passes"].items() if d["clean"])
    out["clean_passes"] = clean
    print(f"\nclean passes (spread <= {a.limit} W): {clean}")
    print("not clean: " + str(sorted(set(out["passes"]) - set(clean))))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
