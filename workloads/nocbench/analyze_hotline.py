#!/usr/bin/env python3
"""Turn run_hotline.sh sweeps into the numbers the brief quotes.

    D=docs/reports/data; DATA=$D/2026-09-22-hotline-aifoundry2; DATA3=$D/2026-09-22-hotline-aifoundry3
    analyze_hotline.py $DATA/sweep.jsonl $DATA3/sweep.jsonl --power $DATA/power.json --context $DATA/context.json \
        --barrier $D/2026-09-18-nocbench-aifoundry2/barrier-chip1.jsonl --out $DATA/hotline.json

Nothing is fitted except the one-per-shire round trip against mesh hops. Every other number is a count of
completed operations in a common, barrier-aligned window, or a ratio of two such counts. The host shire is the
one that homes the contended line; "alone" is the same shire doing the same local work with no other shire
launched.

The 'context' block: the remote atomic's round trip (the window over the ops of the one-requester row), the
bank's service time (the median cycles per op of the placement rows with a single home) and the window are
computed from the sweeps; the chip-wide barrier is read from --barrier (NOCBENCH cycles_per_iter_max, one
minion per shire); the errata text and the window table (whose 5, 40 and 100 ms runs are in no raw data file)
are hand-kept in --context. 'layout' and 'empty' are marty1885's shire map from workloads/nocbench/analyze.py,
and 'share_fit' fits each card's one-per-shire round trip (window / ops) against Manhattan hops from shire 0.
"""
import argparse
import collections
import importlib.util
import json
import os

import numpy as np


def nocbench():
    """workloads/nocbench/analyze.py: marty1885's shire map (MARTY, EMPTY), hops() and load() of NOCBENCH lines."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analyze.py")
    spec = importlib.util.spec_from_file_location("nocbench_analyze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


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
    ap.add_argument("--context", help="hand-kept context.json (errata, window_independence, note) to merge")
    ap.add_argument("--barrier", help="nocbench barrier-chip1.jsonl: the chip-wide barrier, one minion per shire")
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

    nb = nocbench()
    ctx = {}
    if a.barrier:
        b = nb.load(a.barrier)[0]
        ctx["barrier_cycles_chip"] = int(round(b["cycles_per_iter_max"]))
    # the round trip of one remote atomic: the one-requester row of the first card, window over its ops
    r1 = next(r for r in rows if r["host"] == first and r["group"] == "requesters"
              and sum(s_["minions"] for s_ in r["shire"] if s_["s"] != host_shire(r)) == 1)
    rem1 = [s_["ops"] for s_ in r1["shire"] if s_["s"] != host_shire(r1)]
    ctx["remote_atomic_latency_cycles"] = round(r1["window_cycles"] / float(np.mean(rem1)), 1)
    single = [r["cycles_per_op"] for r in rows if r["group"] == "placement" and not r["home"].endswith("own")]
    ctx["bank_service_cycles"] = float(np.median(single))
    if a.context:
        c = json.load(open(a.context))
        ctx.update({k: c[k] for k in ("window_independence", "errata") if k in c})
    wins = sorted({r["window_cycles"] for r in rows})
    ctx["window_cycles"] = wins[0] if len(wins) == 1 else wins
    if a.barrier:
        ctx["barrier_source"] = (f"{os.path.relpath(a.barrier)}: NOCBENCH cycles_per_iter_max {b['cycles_per_iter_max']}, "
                                 f"{b['participants']} participants ({b['per_shire']} per shire)")
    if a.context:
        ctx["note"] = json.load(open(a.context)).get("note")
    out["context"] = ctx

    # the mesh the charts draw, and the per-shire shares with one request each on every card
    out["layout"] = {str(k): list(v) for k, v in nb.MARTY.items()}
    out["empty"] = [list(e) for e in nb.EMPTY]
    out["shares_home0_by_card"] = {}
    out["share_fit"] = {}
    for card in out["cards"]:
        sh0 = []
        for r in rows:
            if r["host"] == card and r["group"] == "fairness" and r["home"] == "0":
                kind = "full" if r["per_shire"] == 32 else "one"
                sh0 += [{"s": s_["s"], "share": s_["share"], "kind": kind, "hops": nb.hops(s_["s"], 0)} for s_ in r["shire"]]
                if r["per_shire"] == 1:
                    h = np.array([nb.hops(s_["s"], 0) for s_ in r["shire"]], float)
                    rt = r["window_cycles"] / np.array([s_["ops"] for s_ in r["shire"]], float)
                    shares = np.array([s_["share"] for s_ in r["shire"]])
                    A = np.vstack([np.ones_like(h), h]).T
                    coef, *_ = np.linalg.lstsq(A, rt, rcond=None)
                    hm = float(1 / np.mean(1 / rt))
                    out["share_fit"][card] = {
                        "round_trip_cycles_0_hops": round(float(coef[0]), 2), "cycles_per_hop": round(float(coef[1]), 3),
                        "harmonic_mean_cycles": round(hm, 1),
                        "max_share_error": round(float(np.abs(hm / (A @ coef) - shares).max()), 4),
                        "r_share_hops": round(float(np.corrcoef(h, shares)[0, 1]), 3), "n": int(len(h)),
                        "model": "share = harmonic_mean_cycles / (round_trip_cycles_0_hops + cycles_per_hop * hops); "
                                 "round trip = window / ops, one minion per shire, home 0, hops = Manhattan distance on the shire map"}
        out["shares_home0_by_card"][card] = sh0
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
    c = out["context"]
    print(f"\nCONTEXT: remote atomic {c['remote_atomic_latency_cycles']} cycles, bank {c['bank_service_cycles']} cycles per op, "
          f"window {c['window_cycles']} cycles" + (f", chip barrier {c['barrier_cycles_chip']} cycles" if "barrier_cycles_chip" in c else ""))
    for card, f in out["share_fit"].items():
        print(f"  {card}: one per shire, round trip {f['round_trip_cycles_0_hops']} + {f['cycles_per_hop']} cycles per hop; "
              f"shares within {f['max_share_error']} of {f['harmonic_mean_cycles']}/(round trip), r = {f['r_share_hops']}")
    print("\nPACE: cycles a remote waits between atomics")
    for r in out["pace"]:
        print(f"  {r['card']:11s} pace {r['pace']:6d}  host {100 * r['frac_of_alone']:7.3f}% of alone"
              f"  remotes {r['remote_ops_per_shire']:8.0f}/shire")


if __name__ == "__main__":
    main()
