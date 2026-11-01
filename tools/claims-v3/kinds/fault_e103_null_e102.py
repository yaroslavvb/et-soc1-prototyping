#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""POST HOC, exploratory, no rule of E102's or E103's depends on it. E103-R3 tests the model against E92's flop-price refit ("four prices + flops" of posthoc-fit.json, over E82's per-type card scale). That null's prices and its counts on E103's tiles both start
from C = fl((n-1) S). This scores the same null with both from the real accumulators, on E103's own D and M, with E103's own bootstrap. Run from the repo's root, after fault_refit_e102.py has written both fits:

    fault_e103_null_e102.py <fit from fl json> <fit from real json>

The first arm is the control: it should read as E103's scored.json does. FAULT_WORKERS sets the pool."""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools", "claims-v3", "rpath"), os.path.join(ROOT, "tools", "claims-v3", "hlp")]
import fault_refit_e102 as fr      # noqa: E402
import make_e102 as m102           # noqa: E402
import score_e103 as s103          # noqa: E402

D = os.path.join(ROOT, "docs", "reports", "data")


def predict(fit, ty, c):
    mod = fit["models"][f"{ty}: four prices + flops"]
    return mod["F_w"] * c["live"] + sum(mod["prices_fj"][q] * 1e-15 * c[q] * fit["ops_per_s"] for q in ("bus", "prod", "res", "flops"))


def main():
    fits = {"fl": json.load(open(sys.argv[1])), "real": json.load(open(sys.argv[2]))}
    table = json.load(open(os.path.join(D, "2026-11-01-e103-model-blind-test", "scored.json")))["primary"]["table"]
    tiles = json.load(open(os.path.join(HERE, "e103", "e103.json")))["tiles"]
    x82 = json.load(open(os.path.join(D, "2026-10-31-e82-kinds-aifoundry1", "scored.json")))["cross_card"]["primary"]["x3"]["per_type_median"]
    accum = m102.accum_binary()
    keys = [k for k in sorted(table) if table[k]["flop"] is not None]
    jobs = [(os.path.join(HERE, "e103", tiles[k]["file"]), tiles[k]["type"], s, accum) for s in ("fl", "real") for k in keys]
    with ProcessPoolExecutor(int(os.environ.get("FAULT_WORKERS", "3"))) as ex:
        got = list(ex.map(fr.one, jobs))
    n = len(keys)
    cnt = {"fl": dict(zip(keys, (g[1] for g in got[:n]))), "real": dict(zip(keys, (g[1] for g in got[n:])))}
    rows = []
    print(f"{'tile':24s} {'group':26s} {'D':>7s} {'M':>7s} {'flop, scored':>12s} {'flop, fl':>9s} {'flop, real':>10s} {'res fl':>8s} {'res real':>8s} {'flops fl':>8s} {'flops real':>10s}")
    for k in keys:
        ty = tiles[k]["type"]
        t = table[k]
        a = predict(fits["fl"], ty, cnt["fl"][k]) / x82[ty]
        b = predict(fits["real"], ty, cnt["real"][k]) / x82[ty]
        rows.append({"key": k, "D": t["D"], "M": t["M"], "scored": t["flop"], "fl": a, "real": b})
        print(f"{k:24s} {t['group'][:26]:26s} {t['D']:7.2f} {t['M']:7.2f} {t['flop']:12.2f} {a:9.2f} {b:10.2f} {cnt['fl'][k]['res']:8.0f} {cnt['real'][k]['res']:8.0f} {cnt['fl'][k]['flops']:8.0f} {cnt['real'][k]['flops']:10.0f}")
    meas, model = [r["D"] for r in rows], [r["M"] for r in rows]
    print(f"\n{n} float tiles. rms(D - M) = {s103.rms([m - q for m, q in zip(meas, model)]):.3f} W")
    for arm in ("scored", "fl", "real"):
        null = [r[arm] for r in rows]
        g = s103.boot_rms_gap(meas, model, null)
        rest = sorted(rows, key=lambda r: abs(r["D"] - r[arm]))[:-1]
        worst = max(rows, key=lambda r: abs(r["D"] - r[arm]))
        g2 = s103.boot_rms_gap([r["D"] for r in rest], [r["M"] for r in rest], [r[arm] for r in rest])
        print(f"null {arm:7s}: rms {s103.rms([m - q for m, q in zip(meas, null)]):.3f} W, gap to the model {g['gap_w']:+.3f} [{g['lo95']:+.3f}, {g['hi95']:+.3f}] W; without its worst tile ({worst['key']}, {worst['D'] - worst[arm]:+.2f} W) "
              f"{s103.rms([r['D'] - r[arm] for r in rest]):.3f} against the model's {s103.rms([r['D'] - r['M'] for r in rest]):.3f} W, gap {g2['gap_w']:+.3f} [{g2['lo95']:+.3f}, {g2['hi95']:+.3f}] W")
    for ty in ("fp32", "fp16"):
        rs = [r for r in rows if r["key"].startswith(ty)]
        print(f"{ty} ({len(rs)}): rms model {s103.rms([r['D'] - r['M'] for r in rs]):.3f}; null scored {s103.rms([r['D'] - r['scored'] for r in rs]):.3f}, fl {s103.rms([r['D'] - r['fl'] for r in rs]):.3f}, real {s103.rms([r['D'] - r['real'] for r in rs]):.3f} W")


if __name__ == "__main__":
    main()
