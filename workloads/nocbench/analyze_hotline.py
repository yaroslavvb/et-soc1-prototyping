#!/usr/bin/env python3
"""Turn run_hotline.sh sweeps into the numbers the brief quotes.

    analyze_hotline.py <sweep.jsonl> [more sweeps...] --power power.json --out hotline.json

Nothing is fitted. Every number is a count of completed operations in a common, barrier-aligned window, or a
ratio of two such counts. The host shire is the one that homes the contended line; "alone" is the same shire
doing the same local work with no other shire launched.
"""
import argparse
import collections
import json

import numpy as np


def load(paths):
    rows = []
    for p in paths:
        for line in open(p):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def host_shire(r):
    spec = r["home"].split(":")[-1]
    return None if spec == "own" else int(spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweeps", nargs="+")
    ap.add_argument("--power")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = load(a.sweeps)
    by_card = collections.defaultdict(list)
    for r in rows:
        by_card[r["host"]].append(r)
    out = {"cards": sorted(by_card), "fairness": [], "placement": [], "local": [], "requesters": [],
           "shires": [], "pace": []}

    def shires(r):
        return {s["s"]: s for s in r["shire"]}

    for card, rs in sorted(by_card.items()):
        # The baseline is the same shire doing the same local work with nothing else launched, per minion,
        # because the pressure sweeps vary how many minions the host shire itself contributes.
        alone = {}
        for r in rs:
            if r["group"] == "local" and r["shires"] == 1:
                h0 = shires(r)[host_shire(r)]
                alone[r["home"]] = h0["ops"] / h0["minions"]
        for r in rs:
            g, sh = r["group"], shires(r)
            h = host_shire(r)
            base = {"card": card, "home": r["home"], "per_shire": r["per_shire"], "shires": r["shires"],
                    "total_ops": r["total_ops"], "cycles_per_op": r["cycles_per_op"], "pace": r.get("pace", 0)}
            if g == "fairness":
                sl = [s["share"] for s in r["shire"]]
                out["fairness"].append(base | {"host_share": sh[h]["share"] if h in sh else None,
                                               "min_share": min(sl), "max_share": max(sl),
                                               "sd_share": float(np.std(sl))})
            elif g == "placement":
                out["placement"].append(base)
            elif g in ("local", "requesters", "shires", "pace"):
                got = sh[h]["ops"] if h in sh else 0
                hm = sh[h]["minions"] if h in sh else 0
                b = alone.get(r["home"], 0)
                rem = [s["ops"] for k, s in sh.items() if k != h]
                out[g if g != "local" else "local"].append(
                    base | {"host_ops": got, "host_minions": hm, "host_alone_ops_per_minion": b,
                            "frac_of_alone": (got / hm) / b if (b and hm) else None,
                            "remote_minions": sum(s["minions"] for k, s in sh.items() if k != h),
                            "remote_ops_per_shire": float(np.mean(rem)) if rem else 0.0,
                            "remote_min": min(rem) if rem else 0, "remote_max": max(rem) if rem else 0})
    # the two per-shire share curves the brief plots, from the first card in the sweep
    first = out["cards"][0]
    out["shares_home0"] = []
    for r in rows:
        if r["host"] == first and r["group"] == "fairness" and r["home"] == "0":
            kind = "full" if r["per_shire"] == 32 else "one"
            out["shares_home0"] += [{"s": s_["s"], "share": s_["share"], "kind": kind} for s_ in r["shire"]]
    if a.power:
        out["power"] = json.load(open(a.power))
    json.dump(out, open(a.out, "w"), indent=1)

    print("FAIRNESS: does the shire that homes the line get its share of the atomic?")
    for r in out["fairness"]:
        print(f"  {r['card']:11s} home {r['home']:7s} {r['per_shire']:2d}/shire  host share "
              f"{r['host_share']:.4f}  spread {r['min_share']:.3f}-{r['max_share']:.3f}  sd {r['sd_share']:.4f}")
    print("\nPLACEMENT: throughput of one contended line against 32 separate lines")
    for r in out["placement"]:
        print(f"  {r['card']:11s} home {r['home']:8s} {r['total_ops']:10d} ops  {r['cycles_per_op']:6.2f} cycles/op")
    print("\nLOCAL: the host shire's own memory path while its shire cache is hammered")
    for r in out["local"]:
        if r["shires"] == 1:
            print(f"  {r['card']:11s} {r['home']:12s} alone: {r['host_ops']:9d} local ops "
                  f"({r['host_alone_ops_per_minion']:.0f} per minion)")
        else:
            print(f"  {r['card']:11s} {r['home']:12s} with {r['remote_minions']:4d} remote minions: "
                  f"{r['host_ops']:6d} = {100 * r['frac_of_alone']:.3f}% of alone")
    print("\nREQUESTERS: one other shire, N of its minions hammering")
    for r in out["requesters"]:
        print(f"  {r['card']:11s} {r['remote_minions']:3d} remote minions  remote "
              f"{6e6 / max(r['remote_ops_per_shire'], 1):6.1f} cycles/op  host {100 * r['frac_of_alone']:7.2f}% of alone")
    print("\nPACE: cycles a remote waits between atomics")
    for r in out["pace"]:
        print(f"  {r['card']:11s} pace {r['pace']:6d}  host {100 * r['frac_of_alone']:7.3f}% of alone"
              f"  remotes {r['remote_ops_per_shire']:8.0f}/shire")


if __name__ == "__main__":
    main()
