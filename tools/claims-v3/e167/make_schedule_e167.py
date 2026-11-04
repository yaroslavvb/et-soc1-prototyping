#!/usr/bin/env python3
"""E167 (Q141(h)): the queue's schedule, in epoch ms, from local clock times on the box (the zone is recorded). It is E161's
make_schedule_e161.py with E167's name; the day's gates are set at the owner's go (E167.md), never defaulted:

    python3 make_schedule_e167.py --date YYYY-MM-DD --smoke-not-before HH:MM --smoke-latest HH:MM --no-start-after HH:MM \
        --cutoff HH:MM --out build/e167/schedule.json

The smoke, which opens the session, starts by smoke-latest; the queue's hard stop holds every step inside the cutoff (the stop file at
cutoff - 120 s, SIGTERM at cutoff - 30 s), and a step that could not end 3 minutes before the cutoff does not start (so a late session runs
the registered subset, G1Q and END). The card-minute budget is 40, the smoke and the stop tests included.
"""
import argparse
import json
import time


def ms(date, hhmm):
    return int(time.mktime(time.strptime(f"{date} {hhmm}", "%Y-%m-%d %H:%M")) * 1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--smoke-not-before", required=True)
    ap.add_argument("--smoke-latest", required=True)
    ap.add_argument("--no-start-after", required=True)
    ap.add_argument("--cutoff", required=True)
    ap.add_argument("--budget", type=float, default=40.0)
    ap.add_argument("--rest-from-ms", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = {"experiment": "E167", "zone": time.strftime("%Z"), "date": a.date,
         "smoke_not_before_ms": ms(a.date, a.smoke_not_before), "smoke_latest_ms": ms(a.date, a.smoke_latest),
         "no_start_after_ms": ms(a.date, a.no_start_after), "cutoff_ms": ms(a.date, a.cutoff),
         "rest_from_ms": a.rest_from_ms, "budget_card_min": a.budget,
         "local": {"smoke_not_before": a.smoke_not_before, "smoke_latest": a.smoke_latest, "no_start_after": a.no_start_after,
                   "cutoff": a.cutoff}}
    assert s["smoke_not_before_ms"] <= s["smoke_latest_ms"] < s["no_start_after_ms"] < s["cutoff_ms"]
    assert a.budget <= 40.0
    json.dump(s, open(a.out, "w"), indent=1)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
