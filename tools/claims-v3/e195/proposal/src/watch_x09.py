#!/usr/bin/env python3
"""x09's board-power stop: a port of the public lab repo's tools/claims-v3/e139/watch_e139.py. It opens no device and
sends no command: it reads the live telemetry file each pass's own sampler writes (<root>/p<pass>/telemetry.jsonl.raw,
and telemetry.jsonl once the block has closed it). Every second it reads the new lines of the newest two passes; when
the board reads at or above the stop on --n samples in a row (the heater's highest bursts are about 54 W on the card
this request is for), it writes that pass's STOP file (runitems.py ends the pass before its next item, exit 8) and the
session's stop file (no further pass starts; the host launches nothing more once it exists), and logs the samples. It
exits when --end-flag exists or after --max-s. A file that goes while it is read (every block's end removes
telemetry.jsonl.raw, then gzip removes telemetry.jsonl) is skipped, and any other error is logged and the watch goes
on: it never ends early on its own, and session_x09.sh starts no block while it is not running.

    python3 tools/claims-v3/x09/watch_x09.py --root build/claims-v3/$(hostname)/x09 --stop-w 70 --n 3 \\
        --session-stop build/x09-STOP --end-flag build/x09/session-end.time --max-s 3600 >> build/x09/watch.log
"""
import argparse
import glob
import json
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--stop-w", type=float, default=70.0)
parser.add_argument("--n", type=int, default=3)
parser.add_argument("--max-s", type=float, default=3600.0)
parser.add_argument("--end-flag", default="build/x09/session-end.time")
parser.add_argument("--session-stop", default="build/x09-STOP")
parser.add_argument("--every-s", type=float, default=1.0)
a = parser.parse_args()
t_end = time.time() + a.max_s
pos, peak, run = {}, {}, {}


def say(m):
    print(time.strftime("%T"), m, flush=True)


def mtime(p):
    """The file's mtime, or -1 when it went between the glob and the sort."""
    try:
        return os.path.getmtime(p)
    except OSError:
        return -1.0


def scan():
    files = sorted(glob.glob(os.path.join(a.root, "p*", "telemetry.jsonl.raw")) +
                   glob.glob(os.path.join(a.root, "p*", "telemetry.jsonl")), key=mtime)[-2:]
    for f in files:
        try:
            with open(f, "rb") as fh:
                fh.seek(pos.get(f, 0))
                data = fh.read()
        except OSError:
            continue
        cut = data.rfind(b"\n")
        if cut < 0:
            continue
        pos[f] = pos.get(f, 0) + cut + 1
        for line in data[:cut].decode("utf-8", "replace").splitlines():
            if not line.startswith("{"):
                continue
            try:
                w = float(json.loads(line)["board_w"])
            except (ValueError, KeyError, TypeError):
                continue
            peak[f] = max(peak.get(f, 0.0), w)
            run[f] = run.get(f, 0) + 1 if w >= a.stop_w else 0
            if run[f] >= a.n:
                d = os.path.dirname(f)
                for s in (os.path.join(d, "STOP"), a.session_stop):
                    with open(s, "a") as fh:
                        fh.write(f"board {w:.2f} W >= {a.stop_w:.1f} W on {a.n} samples at {time.strftime('%T')}\n")
                say(f"STOP: {os.path.basename(d)} board {w:.2f} W >= {a.stop_w:.1f} W on {a.n} samples in a row")
                run[f] = 0


say(f"watch: board stop {a.stop_w:.1f} W on {a.n} samples in a row, on {a.root}")
while time.time() < t_end and not os.path.exists(a.end_flag):
    try:
        scan()
    except Exception as e:   # logged, never fatal: the board stop must outlive any one bad read
        say(f"watch: {type(e).__name__}: {e} (still watching)")
    time.sleep(a.every_s)
for f, w in peak.items():
    say(f"peak board {os.path.basename(os.path.dirname(f))} {w:.2f} W")
say("watch: end")
