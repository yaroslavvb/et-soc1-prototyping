#!/usr/bin/env python3
"""E111 (Q133): the queue's schedule, in epoch ms, from local clock times on the box (PST on 1 Nov 2026; the zone is recorded).

    python3 make_schedule_e111.py --date 2026-11-01 --w1-not-before 15:00 --w1-latest 16:15 --no-start-after 18:00 \
        --cutoff 18:55 --rest-from-ms <smoke end, epoch ms> --card-min-before 1.0 --out build/e111/schedule.json

W1's rest reading may start at --w1-not-before at the earliest (the warm afternoon), and not after --w1-latest. No step starts after
--no-start-after (the workflow's 18:00 PST); the queue's hard stop is --cutoff (every run ends by 19:00 PST). The card-minute budget is
120 minus what the smoke used.
"""
import argparse
import json
import time


def ms(date, hhmm):
    return int(time.mktime(time.strptime(f"{date} {hhmm}", "%Y-%m-%d %H:%M")) * 1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--w1-not-before", required=True)
    ap.add_argument("--w1-latest", required=True)
    ap.add_argument("--no-start-after", required=True)
    ap.add_argument("--cutoff", required=True)
    ap.add_argument("--rest-from-ms", type=int, default=0)
    ap.add_argument("--card-min-before", type=float, default=0.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    s = {"experiment": "E111", "zone": time.strftime("%Z"), "date": a.date,
         "w1_not_before_ms": ms(a.date, a.w1_not_before), "w1_latest_ms": ms(a.date, a.w1_latest),
         "no_start_after_ms": ms(a.date, a.no_start_after), "cutoff_ms": ms(a.date, a.cutoff),
         "rest_from_ms": a.rest_from_ms, "budget_card_min": 120.0, "card_min_before": a.card_min_before,
         "local": {"w1_not_before": a.w1_not_before, "w1_latest": a.w1_latest, "no_start_after": a.no_start_after, "cutoff": a.cutoff}}
    json.dump(s, open(a.out, "w"), indent=1)
    print(json.dumps(s))


if __name__ == "__main__":
    main()
