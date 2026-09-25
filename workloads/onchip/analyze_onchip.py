#!/usr/bin/env python3
"""Turn run_onchip.sh sweeps and run_onchip_power.sh telemetry into the numbers the relay report quotes.

    analyze_onchip.py <sweep.jsonl> [more...] [--power <dir>] --out onchip.json

Nothing is fitted. Rates come from the on-device cycle counter, converted at 600 MHz, because a launch costs a
few hundred microseconds either way. Every relay run verifies its own output: each element must equal the value
its slab started with plus one per stage, and for the hop medium the slab it must have started from is the one
belonging to the shire `stages` places back round the ring.

The ring runs in shire-ID order (ring_prev in kernel/onchip.c), and shire IDs do not follow the mesh. So
`hop_distance` is an offset in shire ID, not a number of mesh hops: each distance row also carries the mesh hops
that offset actually spans, from marty1885's shire map in workloads/nocbench/analyze.py.
"""
import argparse
import collections
import gzip
import importlib.util
import json
import os

import numpy as np


def load(paths):
    rows = []
    for p in paths:
        for line in open(p):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def shire_map():
    """marty1885's (x, y) of each compute shire on the 6x6 mesh and the Manhattan-distance function, as
    workloads/nocbench/analyze.py holds them (the map the on-chip communication report checks against latency)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nocbench", "analyze.py")
    spec = importlib.util.spec_from_file_location("nocbench_analyze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MARTY, mod.hops


def ring_hops(back):
    """Mesh hops between each of the 32 compute shires and the shire `back` places before it in ID order, which
    is the shire it reads from when all 32 run. Returns the mean and the range over the 32 shires."""
    layout, hops = shire_map()
    ids = sorted(layout)
    h = [hops(s, ids[(i - back) % len(ids)], layout) for i, s in enumerate(ids)]
    return {"mean": float(np.mean(h)), "min": int(min(h)), "max": int(max(h))}


def by_medium(rows, group, key, host=None):
    d = collections.defaultdict(dict)
    for r in rows:
        if r.get("group") == group and r.get("test") == "relay" and (host is None or r["host"] == host):
            d[r[key]][r["medium"]] = r
    out = []
    for k in sorted(d):
        m = d[k]
        if len(m) < 3:
            continue
        out.append({key: k, "ok": all(m[x]["ok"] for x in m),
                    **{x: {"gb_s": m[x]["gb_s"], "cycles": m[x]["cycles_max"], "bytes": m[x]["bytes"]}
                       for x in ("dram", "scp", "hop")},
                    "scp_over_dram": m["scp"]["gb_s"] / m["dram"]["gb_s"],
                    "hop_over_dram": m["hop"]["gb_s"] / m["dram"]["gb_s"]})
    return out


def power(dirname):
    tp = os.path.join(dirname, "telemetry.jsonl")
    if os.path.exists(tp + ".gz"):
        tel = [json.loads(l) for l in gzip.open(tp + ".gz", "rt") if l.startswith("{")]
    elif os.path.exists(tp):
        tel = [json.loads(l) for l in open(tp) if l.startswith("{")]
    else:
        return None
    runs = [json.loads(l) for l in open(os.path.join(dirname, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    f = {k: np.array([(s[p][k][0] if p else s[k]) for s in tel])   # rails are [avg, min, max]
         for k, p in (("board_w", None), ("minion_w", "sp"), ("sram_w", "sp"), ("noc_w", "sp"))}
    f["die_c"] = np.array([float(s["temp_c"]["minshire"][0]) for s in tel])   # whole-degree die reading
    # A single relay launch lasts a few milliseconds, less than one telemetry sample, so the window for a
    # medium is the whole burst of back-to-back launches carrying its label.
    span = {}
    for r in runs:
        a0, b0 = r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0
        lo, hi = span.get(r["label"], (a0, b0))
        span[r["label"]] = (min(lo, a0), max(hi, b0))
    busy = np.zeros(len(t), bool)
    for lo, hi in span.values():
        busy |= (t >= lo - 1.0) & (t <= hi + 1.0)
    idle = ~busy
    out = {"idle": {k: float(v[idle].mean()) for k, v in f.items()}}
    out["idle"]["n"] = int(idle.sum())
    out["media"] = []
    for med in ("dram", "scp", "hop"):
        rs = [r for r in runs if r["label"] == med]
        if not rs:
            continue
        lo, hi = span[med]
        m = (t >= lo + 1.0) & (t <= hi - 0.2)   # skip the first second, while the card settles
        if m.sum() < 3:
            continue
        # Bytes per second on the card, from the cycle counter, not the wall clock.
        total = float(sum(r["bytes"] for r in rs))
        devs = float(sum(r["cycles_max"] for r in rs)) / 0.6e9   # seconds the card was actually working
        wall = hi - lo                                            # wall seconds the burst occupied
        over = float(f["board_w"][m].mean() - out["idle"]["board_w"])
        # Energy above idle per byte moved. The gaps between launches draw idle power and so add nothing to
        # the numerator, which is why the wall span is the right multiplier here even at 83% duty.
        out["media"].append({"medium": med, "runs": len(rs), "bytes": total, "device_s": devs,
                             "wall_s": wall, "duty": devs / wall, "bytes_per_s": total / devs,
                             "over_idle_w": over, "pj_per_byte": over * wall / total * 1e12,
                             "n": int(m.sum()), **{k: float(v[m].mean()) for k, v in f.items()}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweeps", nargs="+")
    ap.add_argument("--power")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = load(a.sweeps)
    out = {"cards": sorted({r["host"] for r in rows if "host" in r})}
    for grp, key in (("headline", "medium"), ("intensity", "work"), ("size", "stage_bytes"),
                     ("stages", "stages"), ("shires", "shires")):
        if grp == "headline":
            out["headline"] = {r["host"]: {x["medium"]: x for x in rows
                                           if x.get("group") == "headline" and x["host"] == r["host"]}
                               for r in rows if r.get("group") == "headline"}
            continue
        out[grp] = by_medium(rows, grp, key, out["cards"][0])
    # hop_distance is how many shire IDs back round the ring a slab comes from; mesh_hops is how far that is
    # on the mesh (every run in this group uses all 32 shires, so the ring is all 32 in ID order).
    out["distance"] = sorted([{"hop_distance": r["hop_distance"], "gb_s": r["gb_s"], "ok": r["ok"],
                               "mesh_hops": ring_hops(r["hop_distance"]) if r["shires"] == 32 else None}
                              for r in rows
                              if r.get("group") == "distance" and r["host"] == out["cards"][0]],
                             key=lambda r: r["hop_distance"])
    out["bigsize"] = sorted([{"stage_bytes": r["stage_bytes"], "gb_s": r["gb_s"]}
                             for r in rows
                             if r.get("group") in ("size", "bigsize") and r.get("medium") == "dram"
                             and r["host"] == out["cards"][0]],
                            key=lambda r: r["stage_bytes"])
    out["probe"] = [{k: r[k] for k in ("method_name", "remote_words_wrong", "ok", "host")}
                    for r in rows if r.get("group") == "probe"]
    if a.power:
        out["power"] = power(a.power)
    json.dump(out, open(a.out, "w"), indent=1)

    h = out["headline"][out["cards"][0]]
    print("headline, 1 MB per shire per stage, 8 stages, one add per element:")
    for m in ("dram", "scp", "hop"):
        print(f"  {m:5s} {h[m]['gb_s']:8.1f} GB/s  shire 0 ends holding {h[m]['shire0_final']:5.1f}  ok={h[m]['ok']}")
    print(f"  own scratchpad {h['scp']['gb_s'] / h['dram']['gb_s']:.1f}x DRAM; "
          f"next shire {h['hop']['gb_s'] / h['dram']['gb_s']:.1f}x DRAM")
    if out.get("power"):
        p = out["power"]
        print(f"\nenergy (idle {p['idle']['board_w']:.2f} W):")
        for m in p["media"]:
            print(f"  {m['medium']:5s} {m['bytes_per_s'] / 1e9:8.1f} GB/s on the card  "
                  f"{m['over_idle_w']:5.2f} W over idle  {m['pj_per_byte']:7.2f} pJ/byte  "
                  f"(duty {100 * m['duty']:.0f}%)")
        d = next(m for m in p["media"] if m["medium"] == "dram")
        for m in p["media"]:
            if m["medium"] != "dram":
                print(f"  {m['medium']} uses {d['pj_per_byte'] / m['pj_per_byte']:.0f}x less energy per byte than DRAM")


if __name__ == "__main__":
    main()
