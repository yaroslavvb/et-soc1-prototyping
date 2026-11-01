#!/usr/bin/env python3
"""E107's board watcher, started by queue_e107.sh: it reads the newest pass's live sampler file (<root>/p*/telemetry.jsonl.raw, lib.sh's) twice a second,
and if board_w reads at or above --watts on --samples consecutive samples it writes that pass's STOP file (run_e78.py and the host's --stop-file end the
pass within a launch) and --stop (the queue starts nothing more). It opens no device. Standard library only."""
import argparse
import glob
import json
import os
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--stop", required=True)
    ap.add_argument("--watts", type=float, default=80.0)
    ap.add_argument("--samples", type=int, default=3)
    a = ap.parse_args()
    seen = None
    while True:
        files = glob.glob(os.path.join(a.root, "p*", "telemetry.jsonl.raw"))
        if files:
            f = max(files, key=os.path.getmtime)
            try:
                with open(f, "rb") as h:
                    h.seek(0, 2)
                    h.seek(max(0, h.tell() - 6000))
                    lines = [x for x in h.read().decode(errors="ignore").splitlines() if x.startswith("{")]
            except OSError:
                lines = []
            w = []
            for x in lines[-(a.samples + 1):]:
                try:
                    d = json.loads(x)
                    w.append((d["t_ms"], float(d.get("board_w") or 0)))
                except (ValueError, KeyError, TypeError):
                    pass
            w = w[-a.samples:]
            if len(w) == a.samples and all(v >= a.watts for _, v in w) and w[-1][0] != seen:
                seen = w[-1][0]
                msg = f"{time.strftime('%H:%M:%S')} board {[v for _, v in w]} W >= {a.watts} W on {a.samples} samples in {f}: STOP"
                for s in (os.path.join(os.path.dirname(f), "STOP"), a.stop):
                    open(s, "a").write(msg + "\n")
                print(msg, flush=True)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
