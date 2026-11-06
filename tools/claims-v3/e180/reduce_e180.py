#!/usr/bin/env python3
"""E180's reduction: every pass's bursts by the energy catalogue's own reduction, then each kind's D per pass.

    python3 tools/claims-v3/e180/reduce_e180.py --data <card data dir: .../e180> --out reduced-e180.json [--card aifoundry3]

For each pass directory p<P> (runs.jsonl[.gz], telemetry.jsonl[.gz]): workloads/enercat/analyze_catalogue.py's bursts_of(),
imported unchanged (its idle brackets, its busy window from 0.5 s after the burst's start, its leakage correction), gives
one burst per configuration with over_idle_w, ops_per_s and the die temperatures. A burst is kept when the card's clock
read 600 MHz in all its busy samples (mhz_busy_all_600; aifoundry3 is pinned, so a burst off it is a fault, recorded).
A kind's D in a pass is the mean over_idle_w of its kept bursts in that pass (repeats @r2 / @r3 averaged), in watts above
idle; the rules (score_e180.py) read D differences inside a pass. A pass is kept when its block.json reads ok or partial
and every kind of plan-e180.json has at least one kept burst in it; otherwise it is set aside, with the reason.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import importlib
import json
import os
import re
import statistics as st
import sys

sys.dont_write_bytecode = True


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def kind_of(cfg):
    m = re.match(r"^e180/(.+)/h2(@r\d+)?$", cfg)
    return m.group(1) if m else None


def analyzer(root):
    sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
    try:
        return importlib.import_module("analyze_catalogue")
    finally:
        sys.path.pop(0)


def reduce_pass(d, ac):
    tel, runs = jl(os.path.join(d, "telemetry.jsonl")), jl(os.path.join(d, "runs.jsonl"))
    info = {"n_tel": len(tel), "n_runs": len(runs)}
    if len(tel) < 50 or not runs:
        return {}, [], info
    res = ac.bursts_of(tel, runs)
    bursts = res[0] if isinstance(res, tuple) else res
    kept, dropped = {}, []
    cut = {b["cfg"] for b in bursts}
    for cfg in sorted({r["cfg"] for r in runs} - cut):
        dropped.append({"cfg": cfg, "why": "too few telemetry samples in the burst or its brackets (bursts_of)"})
    for b in bursts:
        k = kind_of(b["cfg"])
        if k is None:
            dropped.append({"cfg": b["cfg"], "why": "not an E180 configuration"})
            continue
        if not b["mhz_busy_all_600"]:
            dropped.append({"cfg": b["cfg"], "why": "busy samples off 600 MHz"})
            continue
        kept.setdefault(k, []).append({"cfg": b["cfg"], "w": b["over_idle_w"], "ops_per_s": b["ops_per_s"],
                                       "pj_per_op": b["pj_per_op"], "die_c_busy": b["die_c_busy"],
                                       "leak_w": b["leak_correction_w"], "launches": b["launches"]})
    return kept, dropped, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="the card's e180 directory, holding p<P>/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--plan", default=None)
    a = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    plan = json.load(open(a.plan or os.path.join(here, "plan-e180.json")))
    kinds = sorted({kind_of(c) for c in plan["order"]["18010"]})
    ac = analyzer(a.root)
    out = {"card": a.card, "passes": {}, "set_aside": {}}
    for name in sorted(os.listdir(a.data)):
        m = re.match(r"^p(\d+)$", name)
        if not m or not plan["order"].get(m.group(1)):
            continue
        d = os.path.join(a.data, name)
        blk = {}
        try:
            blk = json.load(open(os.path.join(d, "block.json")))
        except (OSError, ValueError):
            pass
        kept, dropped, info = reduce_pass(d, ac)
        missing = [k for k in kinds if k not in kept]
        rec = {"block_status": blk.get("status"), "dropped": dropped, "missing": missing, **info,
               "D": {k: st.mean(r["w"] for r in v) for k, v in kept.items()}, "runs": kept}
        if blk.get("status") not in ("ok", "partial"):
            out["set_aside"][m.group(1)] = {"why": f"block status {blk.get('status')}", **rec}
        elif missing:
            out["set_aside"][m.group(1)] = {"why": f"{len(missing)} kinds with no kept burst: {', '.join(missing[:6])}", **rec}
        else:
            out["passes"][m.group(1)] = rec
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    aside = ", ".join("%s (%s)" % (p, v["why"]) for p, v in out["set_aside"].items()) or "none"
    print(f"{len(out['passes'])} kept passes ({', '.join(out['passes'])}); set aside: {aside}")


if __name__ == "__main__":
    main()
