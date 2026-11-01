#!/usr/bin/env python3
"""E98 (Q132): writes the queue's schedule.json and the slot file for the night's two other experiments, E100 and E96, from one number: when P1's
rest reading starts (epoch s). E100's slot starts 30 min after it and lasts 40; P2 is 90 min after it; P3-P7 and E96's slot are frozen in
predictions.json. latest_start_ms keeps the later probes' places: a probe that has slipped too far is dropped rather than push the last one out.

    python3 make_schedule_e98.py --p1 <epoch s> --schedule <file> --slots <file>
"""
import argparse
import calendar
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_MIN = 24       # the expected card time of one probe
REST_MIN = 15
LAST_MIN = 27        # the last probe's start before the cutoff (the queue's stop at the cutoff bounds it)
GAP_MIN = 90


def ep(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


def hm(t):
    """UTC, and the clock as the box reads it (America/Los_Angeles rules by hand: 02:00 PDT goes back at 09:00 UTC)."""
    off, z = (7, "PDT") if t < ep("2026-11-01T09:00:00Z") else (8, "PST")
    return time.strftime("%H:%M UTC", time.gmtime(t)) + " = " + time.strftime("%H:%M", time.gmtime(t - off * 3600)) + " " + z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p1", type=int, required=True)
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--slots", required=True)
    ap.add_argument("--rest-from", type=int, default=0, help="epoch s of the last launch before the queue (the smoke's end)")
    a = ap.parse_args()
    P = json.load(open(os.path.join(HERE, "predictions.json")))
    sc = P["schedule"]
    cutoff = ep(sc["cutoff_utc"])
    fixed = sorted((k, ep(v)) for k, v in sc["fixed_rest_read_utc"].items())
    p2 = a.p1 + 90 * 60
    p2_latest = ep(sc["p2_latest_utc"])
    probes = [("P1", a.p1), ("P2", p2)] + fixed
    e100 = (a.p1 + 30 * 60, a.p1 + 70 * 60)
    e96 = (ep(sc["slots"]["E96"]["start"]), ep(sc["slots"]["E96"]["end"]))
    latest = {}
    nxt = None
    for name, t in reversed(probes):
        if nxt is None:
            latest[name] = cutoff - LAST_MIN * 60
        else:
            latest[name] = min(t + 30 * 60, nxt - (PROBE_MIN + REST_MIN) * 60)
        nxt = latest[name]
    latest["P2"] = min(latest["P2"], p2_latest)
    latest["P1"] = e100[0] - PROBE_MIN * 60
    if p2 > p2_latest:
        print("note: P2 cannot start before its latest start; it will be skipped")
    sched = {"cutoff_ms": cutoff * 1000, "rest_from_ms": a.rest_from * 1000, "max_card_min": 28, "probe_min": PROBE_MIN,
             "slots": [{"name": "E100", "start_ms": e100[0] * 1000, "end_ms": e100[1] * 1000}, {"name": "E96", "start_ms": e96[0] * 1000, "end_ms": e96[1] * 1000}],
             "probes": [{"name": n, "rest_read_ms": t * 1000, "latest_start_ms": latest[n] * 1000} for n, t in probes]}
    json.dump(sched, open(a.schedule, "w"), indent=1)
    with open(a.slots, "w") as f:
        f.write("Q132: aifoundry2's card tonight, under one Discord claim. E98's probes, and the slots of the only two other experiments under that claim, E100 and E96.\n")
        f.write("The card lock is free between probes: E98's queue takes it only for a probe, and launches nothing inside a slot. No second post; the release is E98's lane's.\n")
        f.write("Clocks go back at 02:00 PDT (09:00 UTC): trust the epoch seconds.\n\n")
        for tag, (s0, s1), note in (("E100", e100, "the idle-reset test, int8 zeros, about 20 card-minutes"), ("E96", e96, "real tensors' speed, about 60 card-minutes")):
            f.write(f"SLOT {tag}: start {s0} ({hm(s0)}), end {s1} ({hm(s1)}): {note}.\n")
        f.write("A slot's experiment must have ended by its slot's end, and must not start before its start: a probe may be running until then. Check first:\n")
        f.write("  python3 -m json.tool ~/claude/et-soc1-prototyping/build/e98/runs/status.json ; et-who\n")
        f.write("Do not rebuild or replace build/sparsity_t2, build/ettelem-hpl or tools/claims-v3/kspeed/e98 on this box: every E98 probe runs them, and a changed binary breaks the night's comparison. Build what you need elsewhere.\n")
        f.write("If an experiment overruns, E98's queue waits for the lock, rests 15 min, and drops the next probe at its latest start. Any launch in the 15 min before a probe's rest reading moves that probe.\n\n")
        for n, t in probes:
            f.write(f"E98 {n}: rest reading starts {t} ({hm(t)}); the card is busy about {PROBE_MIN} min from then; latest start {latest[n]} ({hm(latest[n])}).\n")
        f.write(f"\nE98 ends by {cutoff} ({hm(cutoff)}) whatever happens.\n")
    print(open(a.slots).read())
    print(f"E100 ends {(p2 - e100[1]) / 60:.0f} min before P2's rest reading; P2's expected end leaves {(dict(probes)['P3'] - p2 - PROBE_MIN * 60) / 60:.0f} min to P3's (>= {GAP_MIN} wanted); "
          f"at P2's latest start {(dict(probes)['P3'] - latest['P2'] - PROBE_MIN * 60) / 60:.0f} min; E96 ends {(dict(probes)['P3'] - e96[1]) / 60:.0f} min before P3's rest reading")


if __name__ == "__main__":
    main()
