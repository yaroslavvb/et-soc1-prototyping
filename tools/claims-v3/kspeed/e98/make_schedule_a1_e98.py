#!/usr/bin/env python3
"""E98, amendment A1 (Q132): from the queue's first schedule.json and amendment-1.json, writes the restarted queue's schedule (P2, P3, P6, P7, with E101's slot and P3's
new latest start) and the box's slots file. P4 and P5 are gone. Nothing else moves.

    python3 make_schedule_a1_e98.py --first <schedule.json> --schedule <schedule-a1.json> --slots <slots.txt> --rest-from <epoch s>
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_schedule_e98 import hm  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--first", required=True)
ap.add_argument("--schedule", required=True)
ap.add_argument("--slots", required=True)
ap.add_argument("--rest-from", type=int, required=True)
a = ap.parse_args()
S = json.load(open(a.first))
A = json.load(open(os.path.join(HERE, "amendment-1.json")))
E = A["slot_E101"]
probes = {p["name"]: p for p in S["probes"]}
probes["P3"]["latest_start_ms"] = A["p3_latest_start_epoch"] * 1000
slots = S["slots"] + [{"name": "E101", "start_ms": E["start_epoch"] * 1000, "end_ms": E["end_epoch"] * 1000}]
new = dict(S, rest_from_ms=a.rest_from * 1000, slots=slots, probes=[probes[n] for n in ("P2", "P3", "P6", "P7")], amendment="A1")
json.dump(new, open(a.schedule, "w"), indent=1)
NOTE = {"E100": "the idle-reset test, int8 zeros, about 20 card-minutes", "E96": "real tensors' speed, about 60 card-minutes", "E101": E["what"]}
with open(a.slots, "w") as f:
    f.write("Q132: aifoundry2's card tonight, under one Discord claim. E98's probes, and the slots of the only three other experiments under that claim, E100, E96 and E101 (E98's amendment A1).\n")
    f.write("The card lock is free between probes: E98's queue takes it only for a probe, and launches nothing inside a slot. No second post; the release is E98's lane's.\n")
    f.write("Clocks go back at 02:00 PDT (09:00 UTC): trust the epoch seconds.\n\n")
    for sl in slots:
        s0, s1 = sl["start_ms"] // 1000, sl["end_ms"] // 1000
        f.write(f"SLOT {sl['name']}: start {s0} ({hm(s0)}), end {s1} ({hm(s1)}): {NOTE[sl['name']]}.\n")
    f.write("A slot's experiment must have ended by its slot's end, and must not start before its start: a probe may be running until then. Check first:\n")
    f.write("  python3 -m json.tool ~/claude/et-soc1-prototyping/build/e98/runs/status.json ; et-who\n")
    f.write("Do not rebuild or replace build/sparsity_t2, build/ettelem-hpl or tools/claims-v3/kspeed/e98 on this box: every E98 probe runs them, and a changed binary breaks the night's comparison. Build what you need elsewhere.\n")
    f.write("If an experiment overruns, E98's queue waits for the lock, rests 15 min, and drops the next probe at its latest start. Any launch in the 15 min before a probe's rest reading moves that probe.\n\n")
    t1 = S["probes"][0]["rest_read_ms"] // 1000
    f.write(f"E98 P1: rest reading started {t1} ({hm(t1)}).\n")
    for n in ("P2", "P3", "P6", "P7"):
        t, l = probes[n]["rest_read_ms"] // 1000, probes[n]["latest_start_ms"] // 1000
        f.write(f"E98 {n}: rest reading starts {t} ({hm(t)}); the card is busy about 24 min from then; latest start {l} ({hm(l)}).\n")
    f.write("E98 P4 and P5: dropped by amendment A1, for E101.\n")
    f.write(f"\nE98 ends by {S['cutoff_ms'] // 1000} ({hm(S['cutoff_ms'] // 1000)}) whatever happens.\n")
print(open(a.slots).read())
print(json.dumps({k: new[k] for k in ("rest_from_ms", "slots", "probes", "max_card_min", "cutoff_ms")}, indent=None))
