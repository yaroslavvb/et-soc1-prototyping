#!/usr/bin/env python3
"""Merges the Horace-experiment analyses into the JSON the report embeds.

    build_horace_report_data.py --strict horace3.json --toggles toggles.json --cold cold.json [cold2.json] \
        [--before predictions_before.json] [--earlier summary.json] --out report.json
"""
import argparse
import json


def rnd(x, n=3):
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, list):
        return [rnd(v, n) for v in x]
    if isinstance(x, dict):
        return {k: rnd(v, n) for k, v in x.items()}
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", required=True)
    ap.add_argument("--toggles", required=True)
    ap.add_argument("--cold", required=True, nargs="+")
    ap.add_argument("--before")
    ap.add_argument("--earlier")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = json.load(open(a.strict))
    tog = json.load(open(a.toggles))
    cold = {"runs": [r for c in a.cold for r in json.load(open(c))["runs"]]}
    cold["runs"].sort(key=lambda r: ("zeros", "ones", "randn").index(r["values"]) if r["values"] in ("zeros", "ones", "randn") else 9)
    out = {
        "grid": s["grid"], "patterns": s["patterns"], "session": s["session"], "leak_w_per_c": s.get("leak_w_per_c"),
        "runs": [{k: r[k] for k in ("values", "block", "dur", "tflops", "start_temp", "p_before", "p_early", "p80", "p_late", "dT_end",
                                    "approach_s", "curve_T", "curve_P", "mhz_min", "mhz_max", "a_thermal", "a_electrical", "rise_fit", "curve_fit") if k in r} for r in s["runs"]],
        "thermal": s["thermal"], "power_model": s.get("power_model"), "chain": s.get("chain"), "chain_rms": s.get("chain_rms"),
        "toggles": {p: {"mean": {k: v for k, v in t["mean"].items() if k != "by_block"},
                        "blocks": dict(sorted(t["mean"]["by_block"].items(), key=lambda kv: -kv[1])[:8]),
                        "tiles": t.get("tiles")} for p, t in tog.items()},
        "cold": [{k: r[k] for k in ("run", "values", "dur", "tflops", "start_temp", "end_temp", "p_mean", "p_max", "s_at_800", "launches")}
                 | {"trace": r["trace"][::2]} for r in cold["runs"]],
    }
    if a.before:
        out["before"] = json.load(open(a.before))
    if a.earlier:
        out["earlier"] = json.load(open(a.earlier))["horace2"]["mean"]
    json.dump(rnd(out), open(a.out, "w"), separators=(",", ":"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
