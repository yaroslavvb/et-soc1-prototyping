#!/usr/bin/env python3
"""E184's dated amendment A2: its checks on the lab's committed data (desk only; post hoc reads of data that existed before E184's
registration; nothing here is an E184 datum, and nothing decides a verdict).

    /usr/bin/python3 -B tools/claims-v3/e184/a2_check_e184.py <repository top> > tools/claims-v3/e184/a2-check-e184.json

1. A2-5's robust refresh rule on E180's committed fadd.ps bursts (docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/raw/e180/,
   6 passes). Each 8-launch burst is read as E184 reads a quad's blocks: the distinct refreshes of the burst and 1 s either side, E82
   amendment A2's dip rule over that whole series (e184_common.dip_keep), then two pseudo-blocks of four launches each (the window from
   0.35 s after the block's first launch to the end of its last, e184_common.DISCARD_S). Counted: (a) the verifier's measure, kept refreshes
   from 0.5 s after the first launch more than 1.0 W below the burst's own line; (b) what A2-5's rule sets aside: a kept refresh of a
   block more than 0.5 W from the median of that block's kept refreshes; (c) blocks the rule would leave with fewer than 4 refreshes.
   The rule's contamination model for the power (power_e184_a2.py) is read from (b): the rate per block refresh and the depths.
2. A1's step-response reader (tau_a1_e184.fit_burst) burst by burst on E58's card-1 D bursts at the 100 ms sampler, against E58's
   committed per-burst SRAM tau (report.json > sram_w > 100 > per_burst_tau, the same twelve bursts in the same order).
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import tau_a1_e184 as tau  # noqa: E402

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
E180 = os.path.join(TOP, "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3/raw/e180")
E58 = os.path.join(TOP, "docs/reports/data/2026-09-29-tau-aifoundry1-c1")
ROBUST_W = 0.5


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


def jl(path):
    out = []
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def robust_keep(vals):
    """A2-5: the indexes of a block's kept refreshes within ROBUST_W of the block's median (board watts)."""
    m = c.median(vals)
    return [i for i, v in enumerate(vals) if abs(v - m) <= ROBUST_W]


def e180_bursts():
    res = {"passes": 0, "bursts": 0, "kinds": {}, "window_refreshes": 0, "below_line_over_1w": [], "block_refreshes": 0,
           "set_aside_by_a2_5": [], "blocks": 0, "blocks_left_under_4": 0, "zeros_bursts": 0, "zeros_set_aside": 0}
    for pdir in sorted(glob.glob(os.path.join(E180, "p180[1-9]*"))):
        res["passes"] += 1
        pn = os.path.basename(pdir)
        tel = jl(os.path.join(pdir, "telemetry.jsonl.gz"))
        runs = jl(os.path.join(pdir, "runs.jsonl.gz"))
        by = {}
        for r in runs:
            by.setdefault(r["cfg"], []).append(r)
        for cfg, lns in sorted(by.items()):
            kind = lns[0].get("kind", "")
            if not kind.startswith("fadd.ps/"):
                continue
            lns.sort(key=lambda x: x["t_start_ms"])
            if len(lns) != 8:
                continue
            t0, t1 = lns[0]["t_start_ms"], lns[-1]["t_end_ms"]
            ref = c.refreshes([d for d in tel if t0 - 1000 <= d.get("t_ms", -1) <= t1 + 1000])
            xs = [d["board_w"] for d in ref]
            kept = set(c.dip_keep(xs))
            win = [i for i, d in enumerate(ref) if t0 + 500 <= d["t_ms"] <= t1 and i in kept]
            if len(win) < 8:
                continue
            res["bursts"] += 1
            res["kinds"][kind] = res["kinds"].get(kind, 0) + 1
            res["window_refreshes"] += len(win)
            ts = [(ref[i]["t_ms"] - t0) / 1000.0 for i in win]
            ys = [xs[i] for i in win]
            mt, my = c.fmean(ts), c.fmean(ys)
            b = math.fsum((t - mt) * (y - my) for t, y in zip(ts, ys)) / math.fsum((t - mt) ** 2 for t in ts)
            for t, y in zip(ts, ys):
                if y - my - b * (t - mt) < -1.0:
                    res["below_line_over_1w"].append({"pass": pn, "kind": kind, "t_s": round(t, 3), "below_w": round(-(y - my - b * (t - mt)), 3)})
            zeros = kind == "fadd.ps/zeros"
            res["zeros_bursts"] += 1 if zeros else 0
            for blk in (lns[0:4], lns[4:8]):
                lo, hi = blk[0]["t_start_ms"] + c.DISCARD_S * 1000.0, blk[-1]["t_end_ms"]
                idx = [i for i, d in enumerate(ref) if i in kept and lo <= d["t_ms"] <= hi]
                vals = [xs[i] for i in idx]
                if len(vals) < c.MIN_REFRESHES:
                    continue
                res["blocks"] += 1
                res["block_refreshes"] += len(vals)
                keep = robust_keep(vals)
                m = c.median(vals)
                for j, v in enumerate(vals):
                    if j not in keep:
                        res["set_aside_by_a2_5"].append({"pass": pn, "kind": kind, "t_s": round((ref[idx[j]]["t_ms"] - t0) / 1000.0, 3),
                                                         "board_w": v, "block_median_w": m, "off_median_w": round(v - m, 3)})
                        res["zeros_set_aside"] += 1 if zeros else 0
                if len(keep) < c.MIN_REFRESHES:
                    res["blocks_left_under_4"] += 1
    n_aside = len(res["set_aside_by_a2_5"])
    res["rate_set_aside_per_block_refresh"] = r6(n_aside / res["block_refreshes"]) if res["block_refreshes"] else None
    res["depths_w"] = sorted(round(-x["off_median_w"], 3) for x in res["set_aside_by_a2_5"])
    res["refreshes_per_block_median"] = None
    return res


def e58_per_burst():
    rep = json.load(open(os.path.join(E58, "report.json")))
    want = rep["sram_w"]["100"]["per_burst_tau"]
    got = []
    for pdir in sorted(glob.glob(os.path.join(E58, "p[0-9]"))):
        bl = [json.loads(line) for line in open(os.path.join(pdir, "bursts.jsonl"))]
        for b in bl:
            if b.get("rate_ms") != 100 or b.get("status") != "ok" or b.get("kind") != "D":
                continue
            tel = [json.loads(line) for line in open(os.path.join(pdir, "tel-%02d.jsonl" % b["win"])) if line.startswith("{")]
            tp, refd = tau.passes(tel)
            f = tau.fit_burst(tp, [d["sp"]["sram_w"][0] for d in refd], b["t_on_ms"] / 1000.0, b["t_off_ms"] / 1000.0, None,
                              rep["sram_w"]["100"]["one_pass"]["d_s"])
            got.append({"pass": os.path.basename(pdir), "win": b["win"], "tau_shared": f["tau_shared"] if f else None,
                        "tau_rise": f["tau_rise"] if f else None, "tau_fall": f["tau_fall"] if f else None})
    rows = []
    for k, g in enumerate(got):
        e = want[k] if k < len(want) else None
        rows.append(dict(g, e58_per_burst_tau=e, diff_s=r6(g["tau_shared"] - e) if (e is not None and g["tau_shared"] is not None) else None))
    off = [x for x in rows if x["diff_s"] is not None and abs(x["diff_s"]) > 0.0101]
    return {"bursts": len(rows), "e58_per_burst_n": len(want), "rows": rows, "over_0p01_s": off,
            "median_a1": r6(c.median([x["tau_shared"] for x in rows if x["tau_shared"] is not None])), "median_e58": r6(c.median(want))}


out = {"what": "E184 dated amendment A2's checks on committed data (a2_check_e184.py), post hoc, deciding nothing",
       "robust_rule_w": ROBUST_W, "e180_fadd_bursts": e180_bursts(), "e58_sram_per_burst": e58_per_burst()}
print(json.dumps(out, indent=1, sort_keys=True))
