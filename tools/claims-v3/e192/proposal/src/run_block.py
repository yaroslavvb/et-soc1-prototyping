#!/usr/bin/env python3
"""One pass (one block) of intbits on one card, in the style of the public lab repo's run_e78.py.

    python3 -B run_block.py OUT PASS [--heater BIN] [--target 58] [--preheat 59] [--dry] [--smoke]

The caller (run_session.sh) holds the card lock for the block and runs one sampler for the whole session, writing
OUT/telemetry.jsonl. A block is: 10 s idle (marked), two unrecorded burn-in runs of the anchor, the anchor, every other
arm of arms.txt in an order shuffled by "hostname|pass", the anchor again, 10 s idle (marked). Each run is one device
process of 4 s of 0.4 s launches under `timeout 10`, with --stop-file OUT/STOP.

Before every run (the approach, as in the lab's E78 kit): if a heater is given and the die reading is below --preheat,
heater launches (2 s each, the lab's E78 heater arguments) until it reaches --preheat; then idle until the reading is at
or below --target; then at least --quiet-s seconds with no device process, the reading staying in [target-0.5, target].
Every run's record carries its approach: start reading, heats, wait, quiet, whether the wait timed out, and whether the
launch was on protocol. Without a heater the approach only waits (at most --max-wait s) for the reading to come down to
--target and records a timeout if it does not.

The smoke block, when a heater is given, first runs one heater launch and reads the highest board reading during it
from the telemetry: above --heater-ceiling (70 W, 10 W under stopwatch.py's board stop) the block ends (exit 9), so the
heater's level on this card is known before any pass, and a preheat cannot trip the live board stop.

Stops: OUT/STOP (written by hand, or by stopwatch.py on the live telemetry) ends the block before the next device
process, and the host checks it before every launch. A die reading at or above --max-c, or telemetry older than
--stale-s, writes OUT/STOP and ends the block. Exit codes: 0 done, 6 hot, 4 telemetry stale or missing, 8 stopped,
9 the heater's board level is too near the board stop.
"""
import argparse
import json
import os
import random
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HEATER_ARGS = ["--test", "fma", "--type", "fp32", "--pattern", "none", "--values", "randn",
               "--shires", "0xffffffff", "--per-shire", "32", "--seconds", "2", "--seed", "1"]
SMOKE_ARMS = ["nop", "add.a.f2", "add.cr.l31"]
EXIT_STALE, EXIT_HOT, EXIT_STOP, EXIT_HEATER = 4, 6, 8, 9


def last_sample(path):
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 16000))
            lines = f.read().decode(errors="ignore").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except ValueError:
                continue
    return None


def board_max(path, t0, t1):
    """The highest board reading (W) of the telemetry samples taken between epoch seconds t0 and t1, and their count."""
    top, n = None, 0
    try:
        with open(path, "rb") as f:
            for raw in f:
                line = raw.decode(errors="ignore").strip()
                if not (line.startswith("{") and line.endswith("}")):
                    continue
                try:
                    s = json.loads(line)
                except ValueError:
                    continue
                t = s.get("t_ms", 0) / 1000.0
                w = s.get("board_w")
                if t0 <= t <= t1 and isinstance(w, (int, float)):
                    n += 1
                    top = w if top is None else max(top, w)
    except OSError:
        pass
    return top, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("pass_", type=int, metavar="PASS")
    ap.add_argument("--host-bin", default=os.environ.get("H", os.path.join(HERE, "build/host/intbits_host")))
    ap.add_argument("--tel", default=None, help="the session's telemetry file (default OUT/telemetry.jsonl)")
    ap.add_argument("--heater", default=os.environ.get("HEATER", ""))
    ap.add_argument("--target", type=float, default=58.0)
    ap.add_argument("--preheat", type=float, default=59.0, help="0: never heat")
    ap.add_argument("--max-heats", type=int, default=15)
    ap.add_argument("--max-wait", type=float, default=120.0)
    ap.add_argument("--quiet-s", type=float, default=2.0)
    ap.add_argument("--max-c", type=float, default=70.0)
    ap.add_argument("--stale-s", type=float, default=5.0)
    ap.add_argument("--secs", type=float, default=4.0)
    ap.add_argument("--idle", type=float, default=10.0)
    ap.add_argument("--burnin", type=int, default=2)
    ap.add_argument("--dry", action="store_true", help="print the device calls, open nothing")
    ap.add_argument("--smoke", action="store_true",
                    help="one heater check (with a heater), then three arms, 2 s each, no preheat, no burn-in")
    ap.add_argument("--heater-ceiling", type=float, default=70.0)
    a = ap.parse_args()
    out, p = a.out, a.pass_
    os.makedirs(out, exist_ok=True)
    tel = a.tel or os.path.join(out, "telemetry.jsonl")
    stop_file = os.path.join(out, "STOP")
    host = socket.gethostname()
    smoke_heater = a.smoke and bool(a.heater)
    if not a.heater:
        a.preheat = 0.0
    if a.smoke:
        a.preheat, a.burnin, a.secs = 0.0, 0, 2.0

    lines = [l.split() for l in open(os.path.join(HERE, "arms.txt")) if l.strip() and not l.startswith("#")]
    anchor = [x[1] for x in lines if x[0] == "anchor"][0]
    arms = [x[0] for x in lines if x[0] != "anchor"]
    random.Random("%s|%d" % (host, p)).shuffle(arms)
    if a.smoke:
        arms = list(SMOKE_ARMS)
    last_end = [time.time() - 3600.0]

    def jwrite(name, rec):
        with open(os.path.join(out, name), "a") as f:
            f.write(json.dumps(rec) + "\n")

    def mark(kind, t0, t1, **extra):
        jwrite("marks.jsonl", dict(kind=kind, host=host, **{"pass": p}, t0_ms=int(t0 * 1000), t1_ms=int(t1 * 1000),
                                   **extra))

    def stop(code, why):
        if not os.path.exists(stop_file):
            with open(stop_file, "w") as f:
                f.write(json.dumps({"by": "run_block", "pass": p, "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        print("pass %d: stop: %s" % (p, why), file=sys.stderr, flush=True)
        sys.exit(code)

    def check_stop():
        if os.path.exists(stop_file):
            stop(EXIT_STOP, "STOP file present")

    def reading():
        if a.dry:
            return a.target
        s = last_sample(tel)
        if s is None:
            stop(EXIT_STALE, "no telemetry line")
        age = time.time() - s.get("t_ms", 0) / 1000.0
        if age > a.stale_s:
            stop(EXIT_STALE, "newest telemetry line %.1f s old" % age)
        try:
            t = float(s["temp_c"]["minshire"][0])
        except (KeyError, IndexError, TypeError, ValueError):
            stop(EXIT_STALE, "telemetry line without temp_c.minshire")
        if t >= a.max_c:
            stop(EXIT_HOT, "die reading %g C >= %g C" % (t, a.max_c))
        return t

    def device(cmd, kind, **extra):
        check_stop()
        if a.dry:
            print("DRY: " + " ".join(cmd), flush=True)
            return None
        t0 = time.time()
        with open(os.path.join(out, "stderr.txt"), "a") as err:
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=err, text=True)
        t1 = time.time()
        last_end[0] = t1
        mark(kind, t0, t1, rc=r.returncode, **extra)
        return r

    def in_band(t):
        return a.target - 0.5 <= t <= a.target

    def approach():
        if a.dry:
            return {"start_c": a.target, "heats": 0, "wait_s": 0.0, "timed_out": False, "on_protocol": True}
        t = reading()
        heats, w0, timed_out = 0, time.time(), False
        while True:
            while a.preheat > 0 and t < a.preheat and heats < a.max_heats:
                device(["timeout", "10", a.heater] + HEATER_ARGS + ["--stop-file", stop_file], "heater", die_c=t)
                heats += 1
                time.sleep(0.4)
                t = reading()
            hot = t
            c0 = time.time()
            while t > a.target:
                if time.time() - c0 > a.max_wait:
                    timed_out = True
                    break
                time.sleep(0.1)
                check_stop()
                t = reading()
            while time.time() - last_end[0] < a.quiet_s and (a.preheat <= 0 or in_band(t)):
                time.sleep(0.1)
                t = reading()
            if a.preheat > 0 and t < a.target - 0.5 and heats < a.max_heats and not timed_out:
                continue
            break
        quiet = time.time() - last_end[0]
        on = (not timed_out and t <= a.target and quiet >= a.quiet_s
              and (a.preheat <= 0 or (hot >= a.preheat and in_band(t))))
        return {"start_c": t, "start_hot_c": hot, "heats": heats, "wait_s": round(time.time() - w0, 2),
                "quiet_s": round(quiet, 2), "timed_out": timed_out, "on_protocol": on}

    def run(arm, role, seq):
        ap_ = approach()
        cmd = ["timeout", "10", a.host_bin, "--arm", arm, "--seconds", "%g" % a.secs, "--window", "240000000",
               "--stop-file", stop_file]
        r = device(cmd, "run", arm=arm, role=role, seq=seq)
        if r is None:
            return
        n = 0
        for line in r.stdout.splitlines():
            if line.startswith("INTBITS "):
                rec = json.loads(line[len("INTBITS "):])
                rec.update({"host": host, "pass": p, "seq": seq, "role": role, "approach": ap_, "rc": r.returncode})
                jwrite("runs.jsonl", rec)
                n += 1
        if r.returncode != 0 or n == 0:
            print("pass %d seq %d %s: rc %d, %d launches" % (p, seq, arm, r.returncode, n), file=sys.stderr, flush=True)

    def idle(label):
        if a.dry:
            print("DRY: idle %g s (%s)" % (a.idle, label), flush=True)
            return
        t0 = time.time()
        while time.time() - t0 < a.idle:
            check_stop()
            reading()
            time.sleep(0.5)
        mark("idle", t0, time.time(), label=label)

    def heater_check():
        t = reading()
        r = device(["timeout", "10", a.heater] + HEATER_ARGS + ["--stop-file", stop_file], "heater_check", die_c=t)
        if r is None:
            return
        t1 = last_end[0]
        time.sleep(1.0)  # the meter's reading of the heater's last pass
        top, n = board_max(tel, t1 - 2.5, t1 + 0.8)
        jwrite("marks.jsonl", dict(kind="heater_level", host=host, **{"pass": p}, board_max_w=top, samples=n,
                                   ceiling_w=a.heater_ceiling))
        print("pass %d: heater check: highest board reading %s W over %d samples" % (p, top, n), flush=True)
        if top is None:
            stop(EXIT_STALE, "no board reading during the heater check")
        if top > a.heater_ceiling:
            stop(EXIT_HEATER, "heater board reading %.2f W above the %g W ceiling" % (top, a.heater_ceiling))

    check_stop()
    idle("before")
    seq = 0
    if smoke_heater:
        heater_check()
    for _ in range(a.burnin):
        run(anchor, "burnin", seq)
        seq += 1
    if not a.smoke:
        run(anchor, "anchor_first", seq)
        seq += 1
    for arm in arms:
        run(arm, "smoke" if a.smoke else "arm", seq)
        seq += 1
    if not a.smoke:
        run(anchor, "anchor_last", seq)
        seq += 1
    idle("after")
    print("pass %d: %d runs" % (p, seq), flush=True)


if __name__ == "__main__":
    main()
