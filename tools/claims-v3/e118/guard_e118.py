#!/usr/bin/env python3
"""E118's envelope guard: tails the live telemetry of whichever E118 pass is running and stops it at the envelope.

    python3 tools/claims-v3/e118/guard_e118.py --root <tree> --session <build/e118> [--board-max 85] [--die-max 72]

Run detached for the whole session; stopped with SIGTERM. Every 0.2 s it reads the new lines of the newest
build/claims-v3/aifoundry1-c0/e118*/p*/telemetry.jsonl.raw (the 10 Hz sampler's live file, lib.sh start_sampler) and
trips on ANY single reading of:
  - board_w >= 85 W (the owner's envelope, as written: one reading, not three in a row);
  - the die reading (temp_c.minshire[0], the reading run_hl.py and lib.sh use) >= 72 C;
  - while <session>/pinned exists (TDP 0 is set): a minion clock other than 600 MHz (a 300 MHz reading is card 0's
    PMIC over-power safe state; 700/800 would mean the pin did not hold).
A trip writes STOP into that pass's directory (run_hl.py stops at its next check and every sparsity launch carries
--stop-file <pass>/STOP), and <session>/STOP and build/hl-STOP (no further pass starts), and appends the reading to
<session>/guard.jsonl. 300 MHz readings outside the pinned half are logged, not tripped (the reducer's clock gate
voids those runs). It opens no device and sends nothing to the card.
"""
import argparse
import glob
import json
import os
import signal
import time

STOP = False


def on_term(*_):
    global STOP
    STOP = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--session", required=True)
    ap.add_argument("--board-max", type=float, default=85.0)
    ap.add_argument("--die-max", type=float, default=72.0)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    pat = os.path.join(a.root, "build/claims-v3/aifoundry1-c0/e118*/p*/telemetry.jsonl.raw")
    log = open(os.path.join(a.session, "guard.jsonl"), "a")

    def note(rec):
        rec["t_iso"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        log.write(json.dumps(rec) + "\n")
        log.flush()

    note({"event": "guard_start", "board_max": a.board_max, "die_max": a.die_max, "pid": os.getpid()})
    offs = {}
    stats = {"lines": 0, "max_board_w": 0.0, "max_die_c": 0.0, "mhz": {}}
    last_beat = 0.0
    while not STOP:
        files = sorted(glob.glob(pat), key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)
        for path in files[-2:]:
            try:
                with open(path, "rb") as f:
                    f.seek(offs.get(path, 0))
                    data = f.read()
            except OSError:
                continue
            cut = data.rfind(b"\n")
            if cut < 0:
                continue
            offs[path] = offs.get(path, 0) + cut + 1
            for line in data[:cut].decode(errors="ignore").splitlines():
                if not line.startswith("{"):
                    continue
                try:
                    s = json.loads(line)
                except ValueError:
                    continue
                stats["lines"] += 1
                w = s.get("board_w")
                try:
                    die = float(s["temp_c"]["minshire"][0])
                except (KeyError, IndexError, TypeError, ValueError):
                    die = None
                mhz = (s.get("mhz") or {}).get("minion")
                stats["mhz"][str(mhz)] = stats["mhz"].get(str(mhz), 0) + 1
                if w is not None:
                    stats["max_board_w"] = max(stats["max_board_w"], w)
                if die is not None:
                    stats["max_die_c"] = max(stats["max_die_c"], die)
                pinned = os.path.exists(os.path.join(a.session, "pinned"))
                why = None
                if w is not None and w >= a.board_max:
                    why = f"board {w} W >= {a.board_max}"
                elif die is not None and die >= a.die_max:
                    why = f"die {die} C >= {a.die_max}"
                elif pinned and mhz is not None and mhz != 600:
                    why = f"clock {mhz} MHz while pinned"
                elif mhz == 300:
                    note({"event": "safe_state_reading", "file": path, "t_ms": s.get("t_ms"), "board_w": w})
                if why:
                    d = os.path.dirname(path)
                    for stop in (os.path.join(d, "STOP"), os.path.join(a.session, "STOP"), os.path.join(a.root, "build/hl-STOP")):
                        with open(stop, "a") as f:
                            f.write(f"guard_e118: {why}\n")
                    note({"event": "TRIP", "why": why, "file": path, "t_ms": s.get("t_ms"), "board_w": w, "die_c": die,
                          "mhz": mhz, "pinned": pinned})
        if time.time() - last_beat > 60:
            note({"event": "beat", **stats})
            last_beat = time.time()
        time.sleep(0.2)
    note({"event": "guard_stop", **stats})


if __name__ == "__main__":
    main()
