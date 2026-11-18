#!/usr/bin/env python3
"""v31-trace (Q217): the walk's predictions for every planned traced run, made and hashed BEFORE any trace exists (desk; no simulator).
For each run of traces/plan.json and each hart its sys_emu log selection names: enabled or not, what it should do (the walk's event list:
count and sha256 of its canonical lines), and the run's walk summary (per-minion counts, per-shire and chip request streams, sharing,
footprint, strict-LRU L3 shares at 32, 28 and 24 MB, and the lab's desk L2 model per active shire). Standard library; /usr/bin/python3 3.12.3.

    python3 -I -B predict_v31.py --plan ../traces/plan.json --out walk_predictions.json [--no-l2]
"""
import argparse
import hashlib
import json
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import walk_v31 as W  # noqa: E402


def harts_of(log_sel):
    out = []
    for s in log_sel:
        sh, mask = s.split(",")
        sh, mask = int(sh), int(mask, 16)
        out += [64 * sh + t for t in range(64) if (mask >> t) & 1]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-l2", action="store_true")
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    res = {"what": "the walk's predictions for v31-trace's traced runs, before any trace (desk)", "python": sys.version.split()[0],
           "walk_sha256": hashlib.sha256(open(os.path.join(HERE, "walk_v31.py"), "rb").read()).hexdigest(),
           "plan_sha256": hashlib.sha256(open(a.plan, "rb").read()).hexdigest(), "runs": {}}
    l2_cache = {}
    for r in plan["runs"]:
        MB, NB, KB = W.parse_shape(r["shape"])
        sh = set(W.mask_shires(r["mask"]))
        harts = {}
        for h in harts_of(r["log_sel"]):
            s, m, t = h // 64, (h % 64) // 2, h % 2
            if s not in sh:
                harts[str(h)] = {"enabled": False, "expect": "never launched"}
            elif t == 1:
                harts[str(h)] = {"enabled": True, "expect": "enter and return: no tensor operation"}
            else:
                ev = list(W.minion_events(r["kernel"], MB, NB, KB, s, m))
                harts[str(h)] = {"enabled": True, "expect": "the walk's events", "events": len(ev), "sha256": W.events_sha(ev),
                                 "coords": W.coords(s, m)}
        caps = {}
        for cap in (32, 28, 24):
            caps[str(cap)] = W.summary(r["kernel"], MB, NB, KB, r["mask"], l3_cap_mb=cap)["l3_strict"]
        summ = W.summary(r["kernel"], MB, NB, KB, r["mask"], l3_cap_mb=32)
        summ["l3_strict_by_cap"] = caps
        if not a.no_l2 and W.KERNELS[r["kernel"]]["coop"]:
            l2 = {}
            for s in sorted(sh):
                key = (r["kernel"], r["shape"], s)
                if key not in l2_cache:
                    hits = W.l2_shire(r["kernel"], MB, NB, KB, s)
                    n = len(hits)
                    l2_cache[key] = {"A_L2_lines_per_op": round(sum(x[0] for x in hits) / n, 6),
                                     "B_L2_lines_per_op": round(sum(x[1] for x in hits) / n, 6)}
                l2[str(s)] = l2_cache[key]
            summ["l2_desk"] = l2
        res["runs"][r["name"]] = {"kernel": r["kernel"], "shape": r["shape"], "mask": r["mask"], "harts": harts, "walk_summary": summ}
        print(r["name"], "harts", len(harts), "working", sum(1 for v in harts.values() if v.get("events")), flush=True)
    res["made_pst"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    json.dump(res, open(a.out, "w"), indent=1)
    print("wrote", a.out, hashlib.sha256(open(a.out, "rb").read()).hexdigest(), res["made_pst"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
