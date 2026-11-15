#!/usr/bin/env python3
"""x04clock on a card: the arms of arms.tsv, in blocks, nine passes, bracketed by idle, telemetry throughout.

    python3 run_x04.py OUT --host build/x04clock/host/x04clock_host
                       (--sampler build/ettelem/ettelem | --telemetry FILE --telemetry-pid PID)
                       [--device N] [--blocks S,D,W,T] [--passes 9] [--burst 4] [--gap 5] [--pass-gap 30]
                       [--lock /run/lock/etsoc-shire<N>.lock] [--deadline EPOCH_S] [--stop-file PATH]
                       [--smoke] [--dry]

Two sessions are registered: --blocks S,D,W,T (session A) and --blocks C (session B); each stands alone.

One card only. --device N (default: $ET_DEVICES, else 0) is exported as ET_DEVICES to every program started here,
and names the card lock (/run/lock/etsoc-shire<N>.lock unless --lock is given). Before anything is opened the
device nodes are counted: the session refuses to start unless /dev/et<N>_ops exists and is the only ops node on the
host (the host program opens the device layer, which takes every node it finds).

Card free: before the sampler starts (or, with --telemetry, before the first run) and again before every block, the
lab's holder check (`et-who --check`) must find nobody, and then the card lock must be free (a non-blocking flock on
the lock file, opened read-only as flock(1) and the lab's tools open it, created only if missing, never truncated).
Between blocks this runner holds nothing: the lock file is closed, not only unlocked, so it is not listed. The one
holder the check exempts is the session's sampler, by its process id and only on this card's management node: the
sampler this runner started, or with --telemetry the process named by --telemetry-pid, which must have the
telemetry file open for writing (checked again at every holder check). Any other holder, of any user (the relay
and the lab session use the same lab account), means the card is taken. If the card is not free the runner waits
(polling every 30 s) for at most 10 minutes, then stops. Nothing here opens the management node before that check.

Layout of one pass: the anchor arm (spin2) at every block boundary (first in each block, and once more at the end of
the pass), the block's arms in a seeded shuffled order between. Every run is one device process under
`timeout -k 1 10` after `--gap` seconds of idle: `--burst` seconds of 0.4 s launches, or, for a train (block T),
A B B A segments of three launches each. Pass 0 is the warm-up pass: run, kept, and set aside by the reduction. The
card lock is taken per block and released (the file closed) between blocks; between passes nothing is launched for
`--pass-gap` seconds with the lock released and closed (the session's sampler keeps the management node, so other
users' holder checks still list the card as held) before the holder check of the next pass.

Temperature: no heater. Before each run the die is let idle down to the session's own idle reading + 2 C (at most
30 s; every wait is logged to OUT/events.jsonl). The session's idle reading is the median of the 20 s of telemetry
before the first run.

Telemetry: either this script starts one sampler for the whole session (--sampler; always stopped with SIGTERM at
the end, also when the runner itself is stopped by SIGTERM, SIGINT or SIGHUP), or the lab session's own sampler is
already writing a file (--telemetry FILE --telemetry-pid PID): then nothing here opens the management node, and that
one process's hold on the management node is not counted as a holder. Per-sensor temperature codes, if the lab session records them, are
read by the reduction (reduce_x04.py --pvt FILE); this script does not open the node for them.

Stops (registered; each touches OUT/STOPPED and the stop file with the reason and ends the session):
  - a device process that exits with status 1 or any other unexpected status, or is killed by `timeout` (124/137);
    a launch that did not finish is also a call for the lab admin (a hung hart needs a card reset);
  - three device processes in one session that exit with status 3 (a launch returned incomplete: nothing blocked);
  - on the telemetry since the last check: board above 65 W on three samples in a row, die reading at or above
    70 C, or a minion clock other than 600 MHz (or missing) on three samples in a row;
  - the telemetry file not growing for 5 s (a stalled sampler);
  - the card not free for 10 minutes before a block;
  - the stop file present (default OUT/STOP), or the deadline passed (checked before every run).
A train whose segments did not all get their three launches (a slow device opening) is kept in OUT/runs.jsonl with
"ok": false and "short_train": true, so the reduction drops it.
Stopped by SIGTERM, SIGINT or SIGHUP: the handler first sets all three to be ignored (a second signal cannot cut the
clean-up short), and the clean-up runs with them blocked. A device process still running is ended first: SIGTERM to
its `timeout`, which passes it on and kills the program 1 s later, and the runner waits for it (15 s, then once more
60 s) before it releases the card lock; then the sampler is stopped with SIGTERM and waited for. Children are started
with the signals blocked, so none can start unrecorded.
--smoke runs one short pass (the anchor, tk, duty33, faddps_p1 and one train; 2 s bursts) and stops.
--dry opens nothing and prints every device call and every check it would make.

One line per launch goes to OUT/runs.jsonl ("pass", "block", "pos", "arm" and the host program's X04 fields); the
session log to OUT/run.log; waits and stops to OUT/events.jsonl.
"""
import argparse
import collections
import fcntl
import glob
import json
import os
import random
import re
import signal
import socket
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OPEN_S = 1.5          # device opening and closing, seconds a process (counted in the card-time estimate)
TRAIN_LAUNCHES = 12   # A B B A x 3 launches
SEG_LAUNCHES = 3
BOARD_STOP_W, DIE_STOP_C, CLOCK_MHZ = 65.0, 70.0, 600.0
IN_A_ROW = 3          # board and clock stops need this many samples in a row
FREE_WAIT_S, FREE_POLL_S = 600, 30
SMOKE = ("spin2", "tk", "duty33", "faddps_p1", "tr_tk_spin1")


SIGS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)


class Signalled(SystemExit):
    pass


def on_signal(signum, _frame):
    for sig in SIGS:                    # first thing: a second signal must not cut the clean-up short
        signal.signal(sig, signal.SIG_IGN)
    raise Signalled(128 + signum)


def start_child(kids, key, cmd, **kw):
    """Popen with the stop signals blocked until the child is recorded in kids[key] (so a signal cannot leave a child
    unrecorded); the child itself starts with the runner's earlier signal mask."""
    old = signal.pthread_sigmask(signal.SIG_BLOCK, SIGS)
    try:
        kids[key] = subprocess.Popen(cmd, preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, old), **kw)
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, old)
    return kids[key]


def writes_file(pid, path):
    """True when process pid has path open for writing (read from /proc/<pid>/fd and fdinfo)."""
    real = os.path.realpath(path)
    try:
        fds = os.listdir("/proc/%d/fd" % pid)
    except OSError:
        return False
    for fd in fds:
        try:
            if os.readlink("/proc/%d/fd/%s" % (pid, fd)) != real:
                continue
            with open("/proc/%d/fdinfo/%s" % (pid, fd)) as f:
                flags = int(f.read().split("flags:")[1].split()[0], 8)
            if (flags & os.O_ACCMODE) in (os.O_WRONLY, os.O_RDWR):
                return True
        except (OSError, ValueError, IndexError):
            continue
    return False


def load_arms(path):
    arms = []
    for line in open(path):
        if not line.strip() or line.startswith("#"):
            continue
        name, block, opts = line.rstrip("\n").split("\t")
        arms.append({"arm": name, "block": block, "args": opts.split(), "train": "--then" in opts.split()})
    return arms


def ops_nodes():
    """Device nodes the device layer would open: /dev/et<N>_ops."""
    return sorted(p for p in glob.glob("/dev/et*_ops") if re.fullmatch(r"/dev/et\d+_ops", p))


def open_lock(path):
    """The card lock file, opened read-only as flock(1) and the lab's tools open it; created only if missing (as
    flock(1) does), never truncated."""
    try:
        return os.open(path, os.O_RDONLY | os.O_CLOEXEC)
    except FileNotFoundError:
        return os.open(path, os.O_RDONLY | os.O_CREAT | os.O_CLOEXEC, 0o666)


class Telemetry:
    """Reads the sampler's JSON lines incrementally."""

    def __init__(self, path):
        self.path, self.pos, self.samples, self.t_grow = path, 0, [], time.time()

    def poll(self):
        new = []
        try:
            with open(self.path, "rb") as f:
                f.seek(self.pos)
                data = f.read()
        except OSError:
            return new
        cut = data.rfind(b"\n")
        if cut < 0:
            return new
        self.pos += cut + 1
        self.t_grow = time.time()
        for line in data[:cut].decode(errors="replace").splitlines():
            if line.startswith("{"):
                try:
                    new.append(json.loads(line))
                except ValueError:
                    pass
        self.samples.extend(new)
        return new

    @staticmethod
    def die(s):
        try:
            return float(s["temp_c"]["minshire"][0])
        except (KeyError, IndexError, TypeError, ValueError):
            return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--host", required=True)
    ap.add_argument("--sampler", default="")
    ap.add_argument("--telemetry", default="", help="an existing sampler's output file: start no sampler")
    ap.add_argument("--telemetry-pid", type=int, default=0,
                    help="with --telemetry: the process id of the sampler writing that file (the one exempt holder)")
    ap.add_argument("--device", default=os.environ.get("ET_DEVICES") or "0", help="the card (ET_DEVICES)")
    ap.add_argument("--arms", default=os.path.join(HERE, "arms.tsv"))
    ap.add_argument("--passes", type=int, default=9)
    ap.add_argument("--burst", type=float, default=4.0)
    ap.add_argument("--gap", type=float, default=5.0)
    ap.add_argument("--pass-gap", type=float, default=30.0, help="seconds between passes with the lock released, nothing launched")
    ap.add_argument("--blocks", default="S,D,W,T")
    ap.add_argument("--lock", default="", help="default /run/lock/etsoc-shire<device>.lock")
    ap.add_argument("--holder-check", default="et-who", help="the lab's holder check program (run with --check)")
    ap.add_argument("--idle-margin-c", type=float, default=2.0)
    ap.add_argument("--deadline", type=float, default=0.0, help="epoch seconds: start no run after this")
    ap.add_argument("--stop-file", default="", help="default OUT/STOP")
    ap.add_argument("--seed", type=int, default=1113)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if not a.device.isdigit():
        ap.error("--device must be one card number")
    if not a.dry and bool(a.sampler) == bool(a.telemetry):
        ap.error("give exactly one of --sampler and --telemetry")
    if not a.dry and a.telemetry and a.telemetry_pid <= 0:
        ap.error("--telemetry needs --telemetry-pid: the process id of the sampler writing that file")
    if a.sampler and a.telemetry_pid:
        ap.error("--telemetry-pid goes only with --telemetry")
    a.lock = a.lock or "/run/lock/etsoc-shire%s.lock" % a.device
    a.stop_file = a.stop_file or os.path.join(a.out, "STOP")
    for sig in SIGS:
        signal.signal(sig, on_signal)
    env = dict(os.environ, LD_LIBRARY_PATH="/opt/et/lib", ET_DEVICES=a.device)
    os.makedirs(a.out, exist_ok=True)
    arms = load_arms(a.arms)
    anchor = [x for x in arms if x["block"] == "anchor"][0]
    blocks = [b for b in a.blocks.split(",") if b]
    if a.smoke:
        a.passes, a.burst = 1, 2.0
    host = socket.gethostname()
    log = open(os.path.join(a.out, "run.log"), "a")
    events = open(os.path.join(a.out, "events.jsonl"), "a")
    tel_path = a.telemetry or os.path.join(a.out, "telemetry.jsonl")

    def block_items(b):
        items = [x for x in arms if x["block"] == b]
        if a.smoke:
            items = [x for x in items if x["arm"] in SMOKE]
        return items

    def run_s(x):
        return a.gap + OPEN_S + (TRAIN_LAUNCHES * 0.4 + 0.2 if x["train"] else a.burst)

    per_pass = sum(run_s(anchor) + sum(run_s(x) for x in block_items(b)) for b in blocks) + run_s(anchor)
    est = per_pass * a.passes
    wall = est + a.pass_gap * max(a.passes - 1, 0) + 20
    nruns = sum(1 + len(block_items(b)) for b in blocks) + 1

    def say(msg):
        print(msg, file=log, flush=True)
        if a.dry:
            print(msg)

    def event(kind, **kw):
        events.write(json.dumps({"t": time.time(), "kind": kind, **kw}) + "\n")
        events.flush()

    say(f"{nruns} runs a pass x {a.passes} passes, about {est / 60:.0f} card-minutes (lock held), "
        f"about {wall / 60:.0f} minutes of wall time, blocks {blocks}, card {a.device}, lock {a.lock}")

    def device(x, seconds):
        # session defaults first, then the arm's own options (an arm's --window or --label wins)
        cmd = ["timeout", "-k", "1", "10", a.host, "--window", "240000000", "--seconds", str(seconds),
               "--label", x["arm"]]
        cmd += x["args"]
        if a.dry:
            print(f"DRY ET_DEVICES={a.device} " + " ".join(cmd))
            return 0, ""
        # output to files, not pipes: a child ended at a signal never blocks on a pipe nobody reads
        so, se = os.path.join(a.out, "device-stdout.txt"), os.path.join(a.out, "device-stderr.txt")
        with open(so, "w") as fo, open(se, "w") as fe:
            p = start_child(kids, "device", cmd, env=env, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL)
        rc = p.wait()
        kids["device"] = None
        with open(so, errors="replace") as f:
            out = f.read()
        if rc not in (0, 3):
            with open(se, errors="replace") as f:
                err = f.read()
            with open(os.path.join(a.out, "stderr-%d.txt" % int(time.time())), "w") as f:
                f.write(err[-20000:])
        return rc, out

    def end_device():
        """End a device process still running (the runner was stopped by a signal): SIGTERM to its `timeout`, which
        passes it on and kills the program 1 s later; wait for it. True when no device process is left."""
        p = kids.get("device")
        if p is None:
            return True
        if p.poll() is None:
            say("ending the running device process: SIGTERM to its timeout, then waiting")
            p.send_signal(signal.SIGTERM)
            for wait_s in (15, 60):
                try:
                    p.wait(timeout=wait_s)
                    break
                except subprocess.TimeoutExpired:
                    say("device process still running %d s after SIGTERM: tell the lab admin" % wait_s)
                    event("device_not_ended", seconds=wait_s)
                    p.send_signal(signal.SIGTERM)
            else:
                return False
        event("device_ended", rc=p.returncode)
        kids["device"] = None
        return True

    tel = Telemetry(tel_path)
    state = {"run3": 0, "board_hi": 0, "clock_off": 0, "idle_ref": None}
    kids = {"device": None, "sampler": None}
    mgmt_node = "/dev/et%s_mgmt" % a.device

    def stop(reason):
        say("STOP: " + reason)
        event("stop", reason=reason)
        with open(os.path.join(a.out, "STOPPED"), "w") as f:
            f.write(reason + "\n")
        open(a.stop_file, "a").close()
        return 1

    def check_live():
        """Registered live stops on the telemetry since the last check. Returns a reason, or ''."""
        if a.dry:
            return ""
        new = tel.poll()
        if not new and time.time() - tel.t_grow > 5.0:
            return "telemetry not growing for 5 s"
        for s in new:
            w = s.get("board_w")
            state["board_hi"] = state["board_hi"] + 1 if (w is not None and w > BOARD_STOP_W) else 0
            if state["board_hi"] >= IN_A_ROW:
                return "board above %.0f W on three samples in a row" % BOARD_STOP_W
            T = Telemetry.die(s)
            if T is not None and T >= DIE_STOP_C:
                return "die reading %.0f C" % T
            mhz = (s.get("mhz") or {}).get("minion")
            off = mhz is None or float(mhz) != CLOCK_MHZ
            state["clock_off"] = state["clock_off"] + 1 if off else 0
            if state["clock_off"] >= IN_A_ROW:
                return "minion clock %s, not %.0f MHz, on three samples in a row" % (mhz, CLOCK_MHZ)
        return ""

    def stopped():
        if os.path.exists(a.stop_file):
            say("stop file present: stopping")
            event("stop", reason="stop file")
            return True
        if a.deadline and time.time() > a.deadline:
            say("deadline passed: stopping")
            event("stop", reason="deadline")
            return True
        return False

    def one_card():
        """'' if exactly one ops node is on the host and it is the selected card; else the reason."""
        nodes = ops_nodes()
        want = "/dev/et%s_ops" % a.device
        if nodes != [want]:
            return "device nodes %s: need exactly %s (the host program opens every node it finds)" % (nodes, want)
        return ""

    def sampler_pid():
        """The one holder the check exempts: the session's sampler, by process id (0 when there is none yet)."""
        if kids["sampler"] is not None:
            return kids["sampler"].pid                  # the sampler this runner started
        if a.telemetry and a.telemetry_pid > 0 and writes_file(a.telemetry_pid, tel_path):
            return a.telemetry_pid                      # the lab session's sampler, writing the file we read
        return 0

    def others_holding():
        """The lab's holder check. '' when nobody but the session's sampler (on this card's management node) holds a
        device node or a card lock; else who (or why the check failed)."""
        try:
            p = subprocess.run([a.holder_check, "--check"], capture_output=True, text=True, timeout=30,
                               stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as e:
            return "holder check failed: %s" % e
        if p.returncode == 0:
            return ""
        if p.returncode != 1:
            return "holder check failed (exit %d)" % p.returncode
        exempt = sampler_pid()
        others = []
        for line in p.stdout.splitlines():
            f = line.split()
            if not f or not (f[0].startswith("/dev/et") or f[0].startswith("lock:")):
                continue
            if exempt and f[0] == mgmt_node and len(f) >= 3 and f[2].isdigit() and int(f[2]) == exempt:
                continue                                    # the session's sampler, by its process id only
            others.append(line.strip())                     # anyone else, of any user, means the card is taken
        if p.stdout.strip() and not others:
            return ""
        return "; ".join(others) or "holder check exit 1 with no holder listed"

    def take_card(why):
        """Wait (at most 10 minutes) until the holder check is clear and the card lock is ours. True when held.
        The lock file is opened only after the holder check, so this runner is never among the holders it sees."""
        if a.dry:
            print(f"DRY {a.holder_check} --check; flock -n {a.lock} ({why})")
            return True
        t0 = time.time()
        while True:
            if stopped():
                return False
            who = others_holding()
            if not who:
                lk["fd"] = open_lock(a.lock)
                try:
                    fcntl.flock(lk["fd"], fcntl.LOCK_EX | fcntl.LOCK_NB)
                    if time.time() - t0 > 1:
                        event("card_wait", why=why, seconds=round(time.time() - t0))
                    return True
                except OSError:
                    release_card()
                    who = "card lock %s held" % a.lock
            if time.time() - t0 >= FREE_WAIT_S:
                stop("card not free for 10 minutes (%s): %s" % (why, who))
                return False
            event("card_busy", why=why, who=who)
            say("card not free (%s): %s; waiting" % (why, who))
            time.sleep(FREE_POLL_S)

    def release_card():
        """Unlock and close the lock file, so this runner is not listed as a holder between blocks."""
        fd, lk["fd"] = lk["fd"], None
        if fd is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def idle_down():
        """Wait, idle, until the die reads at most the session's idle reference + margin (at most 30 s)."""
        if a.dry or state["idle_ref"] is None:
            return ""
        t0 = time.time()
        while time.time() - t0 < 30.0:
            r = check_live()
            if r:
                return r
            T = Telemetry.die(tel.samples[-1]) if tel.samples else None
            if T is not None and T <= state["idle_ref"] + a.idle_margin_c:
                break
            time.sleep(0.5)
        waited = time.time() - t0
        if waited > 0.6:
            event("idle_down", seconds=round(waited, 1),
                  die=Telemetry.die(tel.samples[-1]) if tel.samples else None)
        return ""

    def short_train(x, recs):
        """True when a train's segments did not all get their launches."""
        if not x["train"]:
            return False
        n = collections.Counter(r.get("seg") for r in recs)
        nseg = 1 + x["args"].count("--then")
        return any(n.get(s, 0) != SEG_LAUNCHES for s in range(nseg))

    def cleanup():
        """Idempotent. A running device process first (ended and waited for), then the lock, then the sampler."""
        if not end_device():
            say("device process not ended: the card lock goes only when this runner exits")
            return
        release_card()
        s = kids["sampler"]
        if s is not None:
            if s.poll() is None:
                s.send_signal(signal.SIGTERM)
                try:
                    s.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    say("sampler did not stop within 10 s of SIGTERM")
            kids["sampler"] = None

    lk = {"fd": None}
    runs = open(os.path.join(a.out, "runs.jsonl"), "a")
    try:
        if a.dry:
            print(f"DRY count /dev/et*_ops: need exactly /dev/et{a.device}_ops")
        else:
            r = one_card()
            if r:
                return stop(r)
            if stopped():
                return 1
            if a.telemetry and not writes_file(a.telemetry_pid, tel_path):
                return stop("process %d does not have %s open for writing: not the session's sampler"
                            % (a.telemetry_pid, tel_path))
        # the card must be free before the sampler opens the management node (or before the first run)
        if not take_card("session start"):
            return 1
        if not a.dry:
            if a.sampler:
                with open(tel_path, "a") as out:
                    start_child(kids, "sampler", [a.sampler, "sample", "--seconds", str(int(wall * 1.5 + 600)),
                                                  "--every-ms", "100"], stdout=out, stderr=subprocess.DEVNULL,
                                stdin=subprocess.DEVNULL, env=env)
            time.sleep(20)
            tel.poll()
            temps = [Telemetry.die(s) for s in tel.samples[-200:]]
            temps = [T for T in temps if T is not None]
            if not temps:
                return stop("no telemetry in the first 20 s")
            state["idle_ref"] = statistics.median(temps)
            event("idle_ref", die=state["idle_ref"], n=len(temps))
            r = check_live()
            if r:
                return stop(r)
        held = True                                     # the lock taken at session start covers the first block
        for p in range(a.passes):
            for bi, b in enumerate(blocks):
                items = block_items(b)
                random.Random(a.seed * 100 + p * 10 + bi).shuffle(items)
                seq = [anchor] + items + ([anchor] if bi == len(blocks) - 1 else [])
                if not held and not take_card("pass %d block %s" % (p, b)):
                    return 1
                held = True
                try:
                    for k, x in enumerate(seq):
                        if stopped():
                            return 1
                        r = idle_down()
                        if r:
                            return stop(r)
                        if not a.dry:
                            time.sleep(a.gap)
                        r = check_live()
                        if r:
                            return stop(r)
                        rc, out = device(x, a.burst)
                        recs = []
                        for line in out.splitlines():
                            if line.startswith("X04 {"):
                                recs.append(json.loads(line[4:]))
                        short = rc == 0 and short_train(x, recs)
                        if short:
                            event("short_train", arm=x["arm"], launches=len(recs))
                        for rec in recs:
                            row = {"host": host, "pass": p, "block": b, "pos": k, "arm": x["arm"],
                                   "train": x["train"], "rc": rc, **rec}
                            if short:
                                row["ok"], row["short_train"] = False, True
                            runs.write(json.dumps(row) + "\n")
                        runs.flush()
                        say(f"pass {p} block {b} {x['arm']}: {len(recs)} launches, exit {rc}"
                            + (" (short train: dropped)" if short else ""))
                        if rc in (124, 137):
                            return stop(f"{x['arm']}: device process killed by timeout (tell the lab admin)")
                        if rc == 3:
                            state["run3"] += 1
                            event("incomplete", arm=x["arm"], count=state["run3"])
                            if state["run3"] >= 3:
                                return stop("three device processes returned an incomplete launch")
                        elif rc != 0:
                            return stop(f"{x['arm']}: device process exit {rc} (a launch that did not finish: "
                                        "tell the lab admin)")
                        r = check_live()
                        if r:
                            return stop(r)
                finally:
                    if kids["device"] is None:          # with a device process still running (a signal), the
                        release_card()                  # session's clean-up ends it first, then releases the lock
                    held = False
            if p < a.passes - 1:
                # a gap between passes: nothing launched, the lock released and its file closed (the session's
                # sampler keeps the management node), then the next block's holder check runs
                say(f"pass {p} done: {a.pass_gap:.0f} s with the lock released, nothing launched")
                if a.dry:
                    print(f"DRY pass gap {a.pass_gap:.0f} s, lock released and closed")
                else:
                    t_end = time.time() + a.pass_gap
                    while time.time() < t_end:
                        r = check_live()
                        if r:
                            return stop(r)
                        time.sleep(min(1.0, max(0.0, t_end - time.time())))
        if not a.dry:
            time.sleep(a.gap + 3)
    except Signalled as e:
        say("runner stopped by signal %d" % (e.code - 128))
        event("stop", reason="signal %d" % (e.code - 128))
        return e.code
    finally:
        # the stop signals blocked and ignored for the whole clean-up; the clean-up is idempotent, so a signal that
        # arrived just before the first line here (its handler has set the ignores) only runs it once more
        for _attempt in (1, 2):
            try:
                signal.pthread_sigmask(signal.SIG_BLOCK, SIGS)
                for sig in SIGS:
                    signal.signal(sig, signal.SIG_IGN)
                cleanup()
                break
            except Signalled:
                continue
    say("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
