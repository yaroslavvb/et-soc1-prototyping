#!/usr/bin/env python3
"""Live stops for a regfile session: follow the session's telemetry file and write OUT/STOP (with the reason) when

  - board power is above --board-w (65 W) on --n (3) distinct readings in a row: the board meter gives a new value
    only once per service-processor pass (every 156-263 ms by the lab's notes), so a sample that repeats the previous
    value is the same reading and neither counts nor resets the run. This workload uses no heater; its kinds draw a
    few watts over the card at rest, so 65 W (the lab's train kits' board stop) is far above any of them,
  - the die reading (temp_c.minshire[0]) is at or above --max-c (70 C),
  - the newest sample is older than --stale-s (10 s) once the sampler has started (the sampler is gone).

The host checks OUT/STOP before every 0.4 s launch and run_trains.py before every device process, so a stop takes
effect within one launch. Exits when OUT/SESSION_DONE appears or after writing STOP. An OUT that already holds
SESSION_DONE when the stopwatch starts is a used one (run_session.sh refuses it; this is the second guard): its
SESSION_DONE would end these stops at once, so the stopwatch writes STOP instead and the session stops.

    python3 -B stopwatch.py TEL OUT [--board-w 65] [--n 3] [--max-c 70] [--stale-s 10]
"""
import argparse
import json
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tel")
    parser.add_argument("out")
    parser.add_argument("--board-w", type=float, default=65.0)
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--max-c", type=float, default=70.0)
    parser.add_argument("--stale-s", type=float, default=10.0)
    a = parser.parse_args()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")

    def stop(why):
        try:
            with open(stop_file, "x") as f:   # never over another writer's STOP: the first reason and time stand
                f.write(json.dumps({"by": "stopwatch", "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        except FileExistsError:
            pass
        print("stopwatch: " + why, file=sys.stderr, flush=True)
        sys.exit(0)

    if os.path.exists(done_file):
        stop("OUT/SESSION_DONE was there when the stopwatch started (a used OUT): no live stops, so no session")
    pos, buf, over, last_t, seen, last_w = 0, "", 0, None, False, None
    t_start = time.time()
    while not os.path.exists(done_file):
        try:
            with open(a.tel, "rb") as f:
                f.seek(pos)
                chunk = f.read()
                pos = f.tell()
        except OSError:
            chunk = b""
        buf += chunk.decode(errors="ignore")
        *lines, buf = buf.split("\n")
        for line in lines:
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                s = json.loads(line)
            except ValueError:
                continue
            seen = True
            last_t = s.get("t_ms", 0) / 1000.0
            w = s.get("board_w")
            if isinstance(w, (int, float)) and w != last_w:  # a new reading of the board meter
                last_w = w
                over = over + 1 if w > a.board_w else 0
                if over >= a.n:
                    stop("board %.2f W above %g W on %d distinct readings in a row" % (w, a.board_w, over))
            try:
                t = float(s["temp_c"]["minshire"][0])
            except (KeyError, IndexError, TypeError, ValueError):
                t = None
            if t is not None and t >= a.max_c:
                stop("die reading %g C at or above %g C" % (t, a.max_c))
        now = time.time()
        if seen and last_t is not None and now - last_t > a.stale_s:
            stop("newest telemetry sample %.1f s old" % (now - last_t))
        if not seen and now - t_start > 60:
            stop("no telemetry sample in the first 60 s")
        time.sleep(0.2)


if __name__ == "__main__":
    main()
