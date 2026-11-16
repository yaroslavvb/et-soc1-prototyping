#!/usr/bin/env python3
"""E196's kit (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE LAB'S LIVE STOPS ON aifoundry3, beside the
proposal's stopwatch.py (E196.md section 9: "the lab's 65 W and 70 C stops on aifoundry3 (the lab's choice; E178's and E182's limits,
worded here as E193's runner words them: board at or above 65 W on three samples in a row, or a die reading at or above 70 C)"), and the
cap's end-stop (KIT.md section 4). run_session_e196.sh starts it with stopwatch.py after the sampler and checks that both are running
before every block (its S4). It follows the session's telemetry file as stopwatch.py does and writes OUT/STOP with its reason when

  - board_w is at or above --board-w (65 W) on --n (3) telemetry samples in a row (every sample with a board reading counts, a repeated
    meter value included: the stricter reading of "three samples in a row"; a sample below resets the run),
  - temp_c.minshire[0], the die, is at or above --max-c (70 C),
  - with --end-epoch E, the clock reaches E (the session wrapper passes the first card command + the cap - 60 s: the run in flight
    finishes, nothing more starts, and the sampler's stop and the closing read fit inside the cap).

It writes STOP only when none exists (the first writer's reason stands), then exits; it exits too when OUT/SESSION_DONE appears. It never
touches a device and never kills a process: the hosts read STOP before every launch (about 0.5 s) and run_block_e196.py before every
device process.
    python3 -B stops_e196.py TEL OUT [--board-w 65] [--n 3] [--max-c 70] [--end-epoch E]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tel")
    ap.add_argument("out")
    ap.add_argument("--board-w", type=float, default=65.0)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--max-c", type=float, default=70.0)
    ap.add_argument("--end-epoch", type=float, default=None)
    a = ap.parse_args()
    stop_file = os.path.join(a.out, "STOP")
    done_file = os.path.join(a.out, "SESSION_DONE")

    def stop(why):
        if not os.path.exists(stop_file):
            with open(stop_file, "w") as f:
                f.write(json.dumps({"by": "stops_e196", "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        print("stops_e196: " + why, file=sys.stderr, flush=True)
        sys.exit(0)

    pos, buf, run = 0, "", 0
    while not os.path.exists(done_file):
        if a.end_epoch is not None and time.time() >= a.end_epoch:
            stop("the cap's end-stop: %s reached (the first card command + the cap - 60 s)" %
                 time.strftime("%H:%M:%S %Z", time.localtime(a.end_epoch)))
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
            w = s.get("board_w")
            if isinstance(w, (int, float)) and not isinstance(w, bool):
                run = run + 1 if w >= a.board_w else 0
                if run >= a.n:
                    stop("board %.2f W at or above %g W on %d samples in a row" % (w, a.board_w, run))
            try:
                t = float(s["temp_c"]["minshire"][0])
            except (KeyError, IndexError, TypeError, ValueError):
                t = None
            if t is not None and t >= a.max_c:
                stop("die reading %g C at or above %g C" % (t, a.max_c))
        time.sleep(0.2)


if __name__ == "__main__":
    main()
