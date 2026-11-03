#!/usr/bin/env python3
"""E144b (Q138): the queue's schedule, in epoch ms, from local clock times on the box (PST on 2 Nov 2026; the zone is recorded).

    python3 make_schedule_e144b.py --date 2026-11-02 --smoke-not-before 22:20 --smoke-latest 22:44 --no-start-after 23:40 \
        --cutoff 23:50 --out build/e144b/schedule.json

The workflow's gates (section 21 of its brief): no new card session after 23:00 PST and every run ends by 23:50 PST. The smoke, which
opens the session, starts by 22:44, so that G1, 15 minutes of rest later, starts by about 23:00; the queue's hard stop holds every step
inside 23:50 (the stop file at 23:48, SIGTERM at 23:49:30), and a step that could not end 3 minutes before the cutoff does not start. The
card-minute budget is 40 (the task's "at most 40 card-minutes"), the smoke and the stop tests included.
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
    s = {"experiment": "E144b", "zone": time.strftime("%Z"), "date": a.date,
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
