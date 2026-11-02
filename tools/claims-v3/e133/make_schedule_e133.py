#!/usr/bin/env python3
"""E133 (Q136): the queue's schedule, in epoch ms, from local clock times on the box (PST on 2 Nov 2026; the zone is recorded).

    python3 make_schedule_e133.py --date 2026-11-02 --smoke-not-before 09:30 --smoke-latest 11:00 --w3-not-before 14:15 \
        --w3-latest 14:45 --no-start-after 15:00 --cutoff 16:00 --out build/e133/schedule.json

The workflow's gates (section 17 of its brief, the owner's rules of 2 November 2026): no step starts after 15:00 PST and every run ends by
16:00 PST. The card-minute budget is 110 (the task's "at most 110 card-minutes"), the smoke included.
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
    ap.add_argument("--w3-not-before", required=True)
    ap.add_argument("--w3-latest", required=True)
    ap.add_argument("--no-start-after", required=True)
    ap.add_argument("--cutoff", required=True)
    ap.add_argument("--budget", type=float, default=110.0)
    ap.add_argument("--rest-from-ms", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = {"experiment": "E133", "zone": time.strftime("%Z"), "date": a.date,
         "smoke_not_before_ms": ms(a.date, a.smoke_not_before), "smoke_latest_ms": ms(a.date, a.smoke_latest),
         "w3_not_before_ms": ms(a.date, a.w3_not_before), "w3_latest_ms": ms(a.date, a.w3_latest),
         "no_start_after_ms": ms(a.date, a.no_start_after), "cutoff_ms": ms(a.date, a.cutoff),
         "rest_from_ms": a.rest_from_ms, "budget_card_min": a.budget, "card_min_before": 0.0,
         "local": {"smoke_not_before": a.smoke_not_before, "smoke_latest": a.smoke_latest, "w3_not_before": a.w3_not_before,
                   "w3_latest": a.w3_latest, "no_start_after": a.no_start_after, "cutoff": a.cutoff}}
    assert s["no_start_after_ms"] < s["cutoff_ms"] and s["w3_latest_ms"] <= s["no_start_after_ms"]
    json.dump(s, open(a.out, "w"), indent=1)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
