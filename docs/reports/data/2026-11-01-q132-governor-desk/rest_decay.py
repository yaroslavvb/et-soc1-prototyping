#!/usr/bin/env python3
"""Q132(g): how long after a card session do aifoundry2's rest readings stop remembering it? POST HOC, desk only.

For each session end: the card's idle W and die, NIC, NVMe, CPU in 5-minute steps afterwards, each minus its value at
60-70 min (or the last value before the next session), so the printed number is what is left of the session's heat.

    rest_decay.py <hist-dir> > rest-decay.txt
"""
import os
import statistics as st
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import die_lines as DL

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()
ENDS = {"E64": 1793, "E80": None}


def main():
    hist = sys.argv[1]
    H = DL.Hist(os.path.join(hist, "aifoundry2"))
    # session ends on aifoundry2 from the 5 s history itself: the last held=True reading followed by 40+ min not held
    held = [(x[0], (x[5].get(0) or {}).get("held")) for x in H.rows]
    ends = []
    last_held = None
    for t, h in held:
        if h:
            last_held = t
        elif last_held and t - last_held > 40 * 60000:
            ends.append(last_held)
            last_held = None
    print("session ends (card held, then free for 40+ min):", [DL.fmt(e) for e in ends])
    print("minutes after the end:   5    10   15   20   30   40   50  (each minus its 55-65 min value; card W in W, others in C)")
    agg = {}
    for e in ends:
        ref = H.proxy(e + 55 * 60000, e + 65 * 60000)
        if not ref["cards"].get(0):
            continue
        line = {"w": [], "die": [], "nic": [], "nvme": [], "cpu": []}
        for m in (5, 10, 15, 20, 30, 40, 50):
            p = H.proxy(e + (m - 1) * 60000, e + (m + 1) * 60000)
            c = p["cards"].get(0)
            line["w"].append(None if not c else round(c["w"] - ref["cards"][0]["w"], 2))
            line["die"].append(None if not c else round(c["die"] - ref["cards"][0]["die"], 1))
            line["nic"].append(None if p["nic"] is None else round(p["nic"] - ref["nic"], 2))
            line["nvme"].append(None if p["nvme"] is None else round(p["nvme"] - ref["nvme"], 2))
            line["cpu"].append(None if p["cpu"] is None else round(p["cpu"] - ref["cpu"], 1))
        print(DL.fmt(e))
        for k, v in line.items():
            print(f"   {k:5s}", v)
            agg.setdefault(k, []).append(v)
    print("medians over the ends")
    for k, vv in agg.items():
        med = []
        for i in range(7):
            q = [v[i] for v in vv if v[i] is not None]
            med.append(round(st.median(q), 2) if q else None)
        print(f"   {k:5s}", med)


if __name__ == "__main__":
    main()
