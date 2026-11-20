#!/usr/bin/env python3
"""data-e208 (Q200): this lane's own re-derivation of every run's time an op in the reduction's primary view, from the raw launch
records (SPARSITY lines), written from the registered rule's words (not from the reducer's code), compared with the reducer's output.
win (governed cards): fma launches ok, launch >= 0, wall >= 0.1 s, passes >= 1, kernel clock (cycles_max / wall_s) 790-810 MHz,
starting 1.0-3.5 s after their own process's launch 0 started, pooled over the run's processes; band600: the same launches with the
kernel clock 590-610 MHz, any start. T_op = sum wall / sum ops a minion (the iters field). Reads only.
    /usr/bin/python3 -I -B spot_time.py <session dir> <reduced json>
"""
import json
import os
import sys


def main(S, redp):
    red = json.load(open(redp))
    pv = red["primary_view"]
    worst = 0.0
    n_cmp = n_missing = 0
    bad = []
    one_sided = []
    for r in red["runs"]:
        if r.get("role") == "null":
            continue
        rj = json.load(open(os.path.join(S, "runs", r["run"], "run.json")))
        W = T = 0.0
        n = 0
        for p in rj["procs"]:
            Ls = [json.loads(ln[9:]) for ln in open(os.path.join(S, "runs", r["run"], p["name"] + ".out")) if ln.startswith("SPARSITY ")]
            t00 = next((x["t_start_ms"] for x in Ls if x.get("launch") == 0), None)
            for x in Ls:
                if x.get("test") != "fma" or (x.get("launch") if x.get("launch") is not None else -9) < 0 or not x.get("ok") \
                        or (x.get("wall_s") or 0) < 0.1 or not x.get("passes"):
                    continue
                f = x["cycles_max"] / x["wall_s"] / 1e6
                if pv == "win":
                    ok = 790 <= f <= 810 and t00 is not None and 1.0 <= (x["t_start_ms"] - t00) / 1000.0 <= 3.5
                else:
                    ok = 590 <= f <= 610
                if ok:
                    W += x["wall_s"]
                    T += x["iters"]
                    n += 1
        v = (r.get("views") or {}).get(pv) or {}
        if v.get("T_op_us") is None or not T:
            n_missing += 1
            if bool(T) != (v.get("T_op_us") is not None):
                one_sided.append(r["run"])
                bad.append(f"{r['run']}: mine n {n}, reducer {v.get('n_launch')} T {v.get('T_op_us')}")
            continue
        mine = W / T * 1e6
        rel = abs(mine - v["T_op_us"]) / v["T_op_us"]
        worst = max(worst, rel)
        n_cmp += 1
        if n != v.get("n_launch") or rel > 1e-9:
            bad.append(f"{r['run']}: mine n {n} T {mine:.9f}; reducer n {v.get('n_launch')} T {v['T_op_us']:.9f}")
    print(f"{os.path.basename(redp)}: view {pv}: {n_cmp} runs compared, worst relative difference {worst:.2e}; "
          f"{n_missing} runs without a figure ({len(one_sided)} of them on one side only); mismatches {len(bad)}")
    for b in bad[:10]:
        print("  ", b)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
