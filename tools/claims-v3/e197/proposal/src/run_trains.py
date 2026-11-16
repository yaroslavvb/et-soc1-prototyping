#!/usr/bin/env python3
"""One block of regfile trains on one card, in the style of the public lab repo's train kits (E182, E183).

    python3 -B run_trains.py OUT BLOCK [--deadline EPOCH_S] [--plan full|short|ext] [--lock-fd N] [--dry]
    python3 -B run_trains.py OUT smoke [--lock-fd N] [--dry]

The caller (run_session.sh) holds the card lock for the block on the descriptor it names with --lock-fd, and runs one
sampler for the whole session, writing OUT/telemetry.jsonl. Every device process is started with that descriptor kept
open, so the lock lasts as long as any process of the block runs. A block (A, B, C or D of trains.tsv in a first
sitting, E in the optional second one) is: 10 s idle (marked); the anchors nop.z, res.k0, res.k64,
each a 3 s burst of 0.4 s launches after 4.5 s of idle; the block's trains in the order of trains.tsv; the anchors again in
the reverse order; 10 s idle (marked). A train is PROCESSES device processes back to back with no gap and no heater,
each one `regfile_host --train F,S --orient O --launches 13` under `timeout -k 1 10` with --stop-file OUT/STOP, the
orientation alternating from the train's FIRST. A train starts only if PROCESSES x 6.2 s + 30 s fits before
--deadline, and each of its processes only if it would end before --deadline even at its timeout's bound (11 s), so
no device process ends after it: a train is cut only when its processes run slower than planned (the train's own
30 s of slack covers the bound otherwise; the block then ends with its closing anchors, recorded as a mark "cut");
nothing is skipped ahead.

The smoke block: 5 s idle; the three anchors as 1 s bursts; then two processes of T8's kinds (one of each
orientation), recorded under the train label "smoke" (never T8: the reducer counts no smoke process in any train);
then the gate: both processes 13 launches, every launch ok with its letter as planned, and every launch's rate within
3 % of the others'. A failed gate ends the session (exit 7) before any train runs.

Stops: OUT/STOP (written by hand, or by stopwatch.py on the live telemetry) ends the block before the next device
process, and the host checks it before every launch; when the block sees it, it records the file's time (a mark
"stop_seen": a STOP made by hand carries no time of its own). A die reading at or above --max-c, or telemetry older
than --stale-s, writes OUT/STOP and ends the block. A device process killed by its timeout, ended by a signal or not
started (an exit of 124 or more, or a signal), or two failed device processes in a row (a non-zero exit, no launch
record, a launch not ok, or a train process with other than 13 launches), write OUT/STOP and end the block. A TERM,
INT or HUP writes OUT/STOP; a device process in flight is left to end after its launch in flight (it sees the STOP)
and is sent TERM if it is still there 5 s later; then the block ends. Exit codes: 0 done, 2 usage, 4 telemetry stale
or missing, 5 device processes failing, 6 hot, 7 smoke gate, 8 stopped, 128 + n signal n.
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHORS = ["nop.z", "res.k0", "res.k64"]
SMOKE_TRAIN = "T8"
PROC_S = 6.2   # one train process: 13 launches of 0.4 s plus the device opening and closing, rounded up
TIMEOUT = ["timeout", "-k", "1", "10"]   # every device process: TERM at 10 s, then KILL 1 s later if it is still there
PROC_MAX_S = 11.0  # the longest a device process can live under TIMEOUT
GRACE_S = 5.0  # after a signal: the time a device process in flight has to see OUT/STOP and end by itself
EXIT_STALE, EXIT_FAIL, EXIT_HOT, EXIT_SMOKE, EXIT_STOP = 4, 5, 6, 7, 8


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


def read_plan():
    rows = []
    for line in open(os.path.join(HERE, "trains.tsv")):
        if not line.strip() or line.startswith("#"):
            continue
        b, tr, f, s, n, first, short, role = line.rstrip("\n").split("\t")
        rows.append({"block": b, "train": tr, "F": f, "S": s, "processes": int(n), "first": first,
                     "short": short == "1", "role": role})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("block", help="A, B, C, D or smoke")
    parser.add_argument("--host-bin", default=os.environ.get("H", os.path.join(HERE, "build/host/regfile_host")))
    parser.add_argument("--tel", default=None, help="the session's telemetry file (default OUT/telemetry.jsonl)")
    parser.add_argument("--plan", default="full", choices=["full", "short", "ext"])
    parser.add_argument("--deadline", type=float, default=0.0, help="epoch seconds; 0: none")
    parser.add_argument("--max-c", type=float, default=70.0)
    parser.add_argument("--stale-s", type=float, default=5.0)
    parser.add_argument("--lock-fd", type=int, default=None,
                        help="the card lock's descriptor, held by the caller: kept open in every device process")
    parser.add_argument("--dry", action="store_true", help="print the device calls, open nothing")
    a = parser.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    tel = a.tel or os.path.join(out, "telemetry.jsonl")
    stop_file = os.path.join(out, "STOP")
    host = socket.gethostname()
    plan = read_plan()
    blk = a.block
    keep_fds = ()
    if a.lock_fd is not None:
        try:
            os.fstat(a.lock_fd)
        except OSError:
            print("--lock-fd %d is not an open descriptor" % a.lock_fd, file=sys.stderr)
            sys.exit(2)
        keep_fds = (a.lock_fd,)
    got = []                                # the signals received: (number, time)
    live = {"p": None, "spawning": False}   # the device process in flight
    fails = [0]                             # failed device processes in a row

    def jwrite(name, rec):
        with open(os.path.join(out, name), "a") as f:
            f.write(json.dumps(rec) + "\n")

    def mark(kind, t0, t1, **extra):
        jwrite("marks.jsonl", dict(kind=kind, host=host, block=blk, t0_ms=int(t0 * 1000), t1_ms=int(t1 * 1000), **extra))

    def write_stop(why):
        try:
            with open(stop_file, "x") as f:   # never over another writer's STOP: the first reason and time stand
                f.write(json.dumps({"by": "run_trains", "block": blk, "why": why, "t_ms": int(time.time() * 1000)}) + "\n")
        except FileExistsError:
            pass

    def stop(code, why):
        write_stop(why)
        print("block %s: stop: %s" % (blk, why), file=sys.stderr, flush=True)
        sys.exit(code)

    def on_signal(sig, frame):
        got.append((sig, time.time()))
        write_stop("signal %d" % sig)
        if live["p"] is not None or live["spawning"]:
            return   # device() waits for the process in flight (it sees the STOP), then ends the block
        stop(128 + sig, "signal %d" % sig)

    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, on_signal)

    def check_stop():
        if got:
            stop(128 + got[0][0], "signal %d" % got[0][0])
        if os.path.exists(stop_file):
            try:
                m = int(os.stat(stop_file).st_mtime * 1000)
            except OSError:
                m = None
            jwrite("marks.jsonl", dict(kind="stop_seen", host=host, block=blk, t_ms=int(time.time() * 1000),
                                       stop_mtime_ms=m))
            stop(EXIT_STOP, "STOP file present")

    def reading():
        if a.dry:
            return 0.0
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

    def device(cmd, kind, info, want=None):
        """one device process; its REGFILE lines go to runs.jsonl with info; returns the records. want: the launches a
        complete process has (13 for a train process)"""
        check_stop()
        reading()
        if a.dry:
            print("DRY: " + " ".join(cmd), flush=True)
            return []
        t0 = time.time()
        with open(os.path.join(out, "stderr.txt"), "a") as err:
            live["spawning"] = True
            try:
                p = live["p"] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, text=True, pass_fds=keep_fds)
            finally:
                live["spawning"] = False
            text, forwarded = "", False
            while True:
                try:
                    text, _ = p.communicate(timeout=0.5)
                    break
                except subprocess.TimeoutExpired:
                    if got and not forwarded and time.time() - got[0][1] > GRACE_S:
                        try:
                            p.send_signal(signal.SIGTERM)   # timeout passes it on, and kills the host 1 s later
                        except OSError:
                            pass
                        forwarded = True
        t1 = time.time()
        rc = p.returncode
        mark(kind, t0, t1, rc=rc, **info)
        recs = []
        for line in (text or "").splitlines():
            if line.startswith("REGFILE "):
                try:
                    rec = json.loads(line[len("REGFILE "):])
                except ValueError:
                    continue
                rec.update({"host": host, "block": blk, "rc": rc, **info})
                jwrite("runs.jsonl", rec)
                recs.append(rec)
        live["p"] = None
        if got:
            stop(128 + got[0][0], "signal %d" % got[0][0])
        check_stop()   # a STOP written while it ran ends the block as a stop, not as a failure
        if rc < 0 or rc >= 124:
            stop(EXIT_FAIL, "device process killed by its timeout, ended by a signal or not started (exit %d)" % rc)
        failed = rc != 0 or not recs or not all(r.get("ok") for r in recs) or (want is not None and len(recs) != want)
        fails[0] = fails[0] + 1 if failed else 0
        if failed:
            print("block %s %s: rc %d, %d launches: a failed device process (%d in a row)"
                  % (blk, json.dumps(info), rc, len(recs), fails[0]), file=sys.stderr, flush=True)
        if fails[0] >= 2:
            stop(EXIT_FAIL, "two failed device processes in a row (the last: exit %d, %d launches)" % (rc, len(recs)))
        return recs

    def idle(secs, label):
        if a.dry:
            print("DRY: idle %g s (%s)" % (secs, label), flush=True)
            return
        t0 = time.time()
        while time.time() - t0 < secs:
            check_stop()
            reading()
            time.sleep(0.25)
        mark("idle", t0, time.time(), label=label)

    def anchor(kind, secs, role):
        idle(4.5, "before " + kind)
        cmd = TIMEOUT + [a.host_bin, "--kind", kind, "--seconds", "%g" % secs, "--window", "240000000",
                         "--stop-file", stop_file]
        device(cmd, "anchor", {"kind_run": kind, "role": role})

    def train_proc(t, j, orient, label=None):
        cmd = TIMEOUT + [a.host_bin, "--train", "%s,%s" % (t["F"], t["S"]), "--orient", orient,
                         "--launches", "13", "--window", "240000000", "--stop-file", stop_file]
        info = {"train": label or t["train"], "proc": j, "orient": orient, "F": t["F"], "S": t["S"]}
        if label:
            info["of"] = t["train"]
        return device(cmd, "train", info, want=13)

    other = {"SFFS": "FSSF", "FSSF": "SFFS"}
    check_stop()
    if blk == "smoke":
        idle(5.0, "before")
        for k in ANCHORS:
            anchor(k, 1.0, "smoke_anchor")
        t = [x for x in plan if x["train"] == SMOKE_TRAIN][0]
        recs = train_proc(t, 0, t["first"], "smoke") + train_proc(t, 1, other[t["first"]], "smoke")
        if a.dry:
            return
        ok = len(recs) == 26 and all(r.get("ok") for r in recs)
        for j, o in ((0, t["first"]), (1, other[t["first"]])):
            mine = [r for r in recs if r.get("proc") == j]
            want = [o[0]] + [o[(n - 1) % 4] for n in range(1, 13)]
            ok = ok and [r.get("letter") for r in mine] == want
        rates = [r.get("instr_per_s_600", 0) for r in recs]
        if rates and min(rates) > 0:
            ok = ok and (max(rates) - min(rates)) / min(rates) <= 0.03
        else:
            ok = False
        jwrite("marks.jsonl", dict(kind="smoke_gate", host=host, block=blk, ok=ok, launches=len(recs),
                                   rate_min=min(rates) if rates else None, rate_max=max(rates) if rates else None))
        if not ok:
            stop(EXIT_SMOKE, "smoke gate failed (launches %d)" % len(recs))
        print("smoke: gate passed", flush=True)
        return
    if (blk == "E") != (a.plan == "ext"):
        print("block %s is not in the %s plan" % (blk, a.plan), file=sys.stderr)
        sys.exit(2)
    trains = [x for x in plan if x["block"] == blk and (a.plan in ("full", "ext") or x["short"])]
    if not trains:
        print("block %s: no trains in the %s plan" % (blk, a.plan), file=sys.stderr)
        sys.exit(2)
    idle(10.0, "before")
    for k in ANCHORS:
        anchor(k, 3.0, "anchor_first")
    for t in trains:
        need = t["processes"] * PROC_S + 30.0
        if a.deadline and time.time() + need > a.deadline:
            jwrite("marks.jsonl", dict(kind="skipped", host=host, block=blk, train=t["train"], need_s=need))
            print("block %s: %s does not fit before the deadline: the block ends here" % (blk, t["train"]), flush=True)
            break
        o = t["first"]
        cut = False
        for j in range(t["processes"]):
            if a.deadline and time.time() + PROC_MAX_S > a.deadline:
                jwrite("marks.jsonl", dict(kind="cut", host=host, block=blk, train=t["train"], proc=j,
                                           processes=t["processes"]))
                print("block %s: %s cut before process %d of %d (the deadline): the block ends here"
                      % (blk, t["train"], j, t["processes"]), flush=True)
                cut = True
                break
            train_proc(t, j, o)
            o = other[o]
        if cut:
            break
    for k in reversed(ANCHORS):
        anchor(k, 3.0, "anchor_last")
    idle(10.0, "after")
    print("block %s: done" % blk, flush=True)


if __name__ == "__main__":
    main()
