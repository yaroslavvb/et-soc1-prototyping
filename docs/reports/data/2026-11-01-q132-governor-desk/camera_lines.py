#!/usr/bin/env python3
"""Q132(g): the long camera sessions as near-steady points of the heat path. POST HOC, desk only, no card.

E63, E73 and E85 hold the card in one 10 s on-off pattern for 30-45 minutes at 34-42 W. The die has time to settle there, unlike a 76 s
sustained run, so if the room drives the heat path, their die should follow the room about 1:1. For each block of each session: mean die and W
(whole sampler window of the block, after the block's warm-up), and the rest reading before the session.

    camera_lines.py <repo> <hist-dir> > camera-lines.txt
"""
import json
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import die_lines as DL
import ir_lib as L

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()
SESS = [("E63-s1", "2026-10-23-e63-camera-hamming-ladder/s1/session"), ("E63-s2", "2026-10-23-e63-camera-hamming-ladder/s2/session"),
        ("E73", "2026-10-27-e73-camera-frequencies/session"), ("E85", "2026-10-31-e85-camera-kinds/session")]


def main():
    repo, hist = sys.argv[1], sys.argv[2]
    K = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "die-lines.json")))["pooled_k_c_per_w"]
    data = os.path.join(repo, "docs/reports/data")
    H = DL.Hist(os.path.join(hist, "aifoundry2"))
    A3 = DL.Hist(os.path.join(hist, "aifoundry3"))
    rows = []
    print(f"session  block       start        harts  W     die    die - {K} W   | rest before the session: a2 W, die, NIC, NVMe (30-5 min before its first launch)")
    for name, rel in SESS:
        d = os.path.join(data, rel)
        T = L.tel(os.path.join(d, "tel.jsonl"))
        blocks = L.jl(os.path.join(d, "blocks.jsonl"))
        launches = L.jl(os.path.join(d, "launches.jsonl"))
        first = min(x["t_start_ms"] for x in launches if x.get("t_start_ms"))
        rest = H.proxy(first - 30 * 60000, first - 5 * 60000)
        rest3 = A3.proxy(first - 30 * 60000, first - 5 * 60000)
        rc = rest["cards"].get(0) or {}
        for b in blocks:
            if b.get("status") != "ok":
                continue
            a0, a1 = b["t_start_ms"], b["t_end_ms"]
            # after a 2 minute settle inside the block
            S = [x for x in T if a0 + 120000 <= x[0] <= a1 and x[1] is not None and x[3] is not None]
            if len(S) < 200:
                continue
            w, die = st.mean(x[3] for x in S), st.mean(x[1] for x in S)
            harts = next((x.get("harts") for x in launches if x.get("block") == b["block"]), None)
            rows.append({"session": name, "block": b["block"], "t0": a0, "harts": harts, "w": round(w, 2), "die": round(die, 2), "off": round(die - K * w, 2),
                         "rest_w": rc.get("w"), "rest_die": rc.get("die"), "rest_nic": rest["nic"], "rest_nvme": rest["nvme"], "a3_nic": rest3["nic"]})
            print(f"{name:7s} {b['block']:12s} {DL.fmt(a0)[-11:]} {harts:5d} {w:6.2f} {die:6.2f} {die - K * w:7.2f}     | {rc.get('w')} {rc.get('die')} {rest['nic']} {rest['nvme']}")
    # the same blocks' names across sessions: E85's reference rung against E73's and E63's
    print("\nSession means (blocks with 192 harts):")
    by = {}
    for r in rows:
        if r["harts"] == 192:
            by.setdefault(r["session"], []).append(r)
    means = {}
    for s, v in by.items():
        means[s] = {"off": round(st.mean(x["off"] for x in v), 3), "w": round(st.mean(x["w"] for x in v), 2), "die": round(st.mean(x["die"] for x in v), 2),
                    "rest_w": v[0]["rest_w"], "rest_die": v[0]["rest_die"], "rest_nic": v[0]["rest_nic"], "n": len(v)}
        print(f"  {s}: {means[s]}")
    print("\nSession means (blocks with 256 harts):")
    by2 = {}
    for r in rows:
        if r["harts"] == 256:
            by2.setdefault(r["session"], []).append(r)
    for s, v in by2.items():
        print(f"  {s}: off {st.mean(x['off'] for x in v):.3f} W {st.mean(x['w'] for x in v):.2f} die {st.mean(x['die'] for x in v):.2f} rest die {v[0]['rest_die']} n {len(v)}")
    json.dump({"rows": rows, "means_192": means}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "camera-lines.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
