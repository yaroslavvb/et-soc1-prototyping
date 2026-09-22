#!/usr/bin/env python3
"""Turn run_onchip.sh sweeps and run_onchip_power.sh telemetry into the numbers the brief quotes.

    analyze_onchip.py <sweep.jsonl> [more...] [--power <dir>] --out onchip.json

Nothing is fitted. Rates come from the on-device cycle counter at the 600 MHz the card is pinned to, because
a launch costs a few hundred microseconds either way. Every relay run verifies its own output: each element
must equal the value its slab started with plus one per stage, and for the hop medium the slab it must have
started from is the one belonging to the shire `stages` places back round the ring.
"""
import argparse
import collections
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
    if not os.path.exists(tp):
        return None
    tel = [json.loads(l) for l in open(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(dirname, "runs.jsonl"))]
    t = np.array([s["t_ms"] for s in tel]) / 1000.0
    f = {k: np.array([s[p][k] if p else s[k] for s in tel])
         for k, p in (("board_w", None), ("minion_w", "sp"), ("sram_w", "sp"), ("noc_w", "sp"))}
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
    out["distance"] = sorted([{"hop_distance": r["hop_distance"], "gb_s": r["gb_s"], "ok": r["ok"]}
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
