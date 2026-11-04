#!/usr/bin/env python3
"""E161 (Q139): the queue's schedule, in epoch ms, from local clock times on the box (PST on 3 Nov 2026; the zone is recorded). It is
E144b's make_schedule_e144b.py with E161's name and tonight's gates.

    python3 make_schedule_e161.py --date 2026-11-03 --smoke-not-before 17:30 --smoke-latest 20:45 --no-start-after 21:40 \
        --cutoff 22:00 --out build/e161/schedule.json

The workflow's gates (section 23 of its brief): no new card session after 21:00 PST and every run ends by 22:00 PST. The smoke, which
opens the session, starts by 20:45 at the latest; the queue's hard stop holds every step inside 22:00 (the stop file at 21:58, SIGTERM at
21:59:30), and a step that could not end 3 minutes before the cutoff does not start (so a late session runs the registered subset, G1Q
and END). The card-minute budget is 40 (the task's "at most 40 card-minutes"), the smoke and the stop tests included.
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
    s = {"experiment": "E161", "zone": time.strftime("%Z"), "date": a.date,
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
