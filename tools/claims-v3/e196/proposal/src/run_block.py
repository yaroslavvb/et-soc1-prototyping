#!/usr/bin/env python3
"""One pass (one block) of x14 on one card, in the style of the public lab repo's run_e78.py, or one A B B A train (the
lab's E182 method).

    python3 -B run_block.py OUT PASS --heater BIN [--gen DIR] [--target 58] [--preheat 59] [--drop ARM,...] [--dry]
                            [--smoke]
    python3 -B run_block.py OUT PASS --heater BIN --train T1 [--processes N] [...]
    python3 -B run_block.py OUT PASS [--drop ARM,...] --plan     (prints the pass's PLAN line; opens nothing)

DIR (default OUT/gen) holds what make_x14.py wrote: arms.json (the arm and train tables) and tiles/. Every arm of
arms.json marked for the passes is one run of a pass, except the arms named by --drop (comma-separated; never the
anchor; the smoke and the trains are not affected); the block anchor is K.pi (the host's built-in pi, the lab's
E60-E79 tie). A pass writes a "plan" mark (its arms in run order, and the dropped ones) before its first run. --plan
prints "PLAN runs=N arms=M dropped=... orphaned=..." (orphaned: kept arms whose reference arm is dropped) and exits.

A train block: 10 s idle (marked), the anchor (one approach, one 4 s run), then the train's processes back to back,
each one host process of a calibration launch and 13 launches of about 0.5 s that alternate the train's two kinds
(SFFS in even processes, FSSF in odd ones), under `timeout 10`; then the anchor again and 10 s idle. Between processes:
the STOP file, the die reading and the telemetry's age are checked. Every launch record goes to train.jsonl with its
process, order and kind.

The smoke block (--smoke): the heater check (below); then the smoke arms (2 s each, no preheat, no burn-in) and the
first 2 processes of train T1; then the smoke gate: every smoke arm and both train processes have launch records;
every launch record is ok with tensor_errors 0; every read-back of C (X14CHECK) is ok; cycles per op within 0.5 % of
the arm's expected count (546 unmasked or with every row enabled, 544 with a row masked); the train records follow
their order. A failed gate exits 10, and run_session.sh runs no pass.

The caller (run_session.sh) holds the card lock for the block and runs one sampler for the whole session, writing
OUT/telemetry.jsonl. A block is: 10 s idle (marked), two unrecorded burn-in runs of the anchor, the anchor, every other
pass arm of arms.json that is not dropped, in an order shuffled by "hostname|pass", the anchor again, 10 s idle
(marked). Each run is one device process of 4 s of launches of about 0.5 s under `timeout 10`, with --stop-file
OUT/STOP.

The heater (--heater, required for every block but --plan): this request's own x14_host, run with HEATER_ARGS (random
values for 2 s, the load of the lab's E78 heater written in this host's arguments; the lab's sparsity host does not
take them and exits 2). A heater launch fails when it exits non-zero or prints no launch record, or a record that is
not ok or has a tensor error; two failed heater launches in a row end the block (exit 11).

Before every run (the approach, as in the lab's E78 kit): if the die reading is below --preheat, heater launches until
it reaches --preheat; then idle until the reading is at or below --target; then at least --quiet-s seconds with no
device process, the reading staying in [target-0.5, target]. Every run's record carries its approach: start reading,
the reading after the heats, heats and failed heats, wait, quiet, whether the wait timed out, the preheat and target
used, and whether the launch was on protocol. On protocol is the registered approach only: a preheat above 0 that was
reached, no timeout, the reading in the band and the quiet time kept; so a run launched with --preheat 0 (the smoke's
arms, which the reduction does not use) is never on protocol.

The smoke block first runs the heater check, one heater launch: it must exit 0 with every launch record ok and no
tensor error, or the smoke gate fails at once (exit 10, nothing more runs); and the highest board reading during it,
from the telemetry, must not exceed --heater-ceiling (70 W, 10 W under stopwatch.py's board stop), or the block ends
(exit 9). So the heater is known to work, and its level on this card is known, before any pass, and a preheat cannot
trip the live board stop.

Stops: OUT/STOP (written by hand, or by stopwatch.py on the live telemetry) ends the block before the next device
process, and the host checks it before every launch. A die reading at or above --max-c, or telemetry older than
--stale-s, writes OUT/STOP and ends the block. Exit codes: 0 done, 2 a refused setting (no heater; a --drop name that
is not a pass arm, or the anchor), 4 telemetry stale or missing, 6 hot, 8 stopped, 9 the heater's board level is too
near the board stop, 10 the smoke gate failed, 11 the heater failed twice in a row.
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
sys.path.insert(0, HERE)
import make_x14  # noqa: E402  (host_args: the host arguments of an arm)
HEATER_ARGS = ["--values", "randn", "--label", "heater", "--seconds", "2", "--seed", "1"]   # x14_host's arguments
ANCHOR = "K.pi"
SMOKE_ARMS = ["I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"]
SMOKE_TRAIN, SMOKE_PROCESSES = "T1", 2
EXIT_REFUSED, EXIT_STALE, EXIT_HOT, EXIT_STOP, EXIT_HEATER, EXIT_SMOKE, EXIT_HEATER_FAIL = 2, 4, 6, 8, 9, 10, 11


def expected_cycles(arm):
    """cycles per op on the card: 546 without a row mask or with every row enabled, 544 with a row masked"""
    m = arm["row_mask"]
    return 546.0 if m is None or int(m, 16) == 0xFFFF else 544.0


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
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("pass_", type=int, metavar="PASS")
    parser.add_argument("--host-bin", default=os.environ.get("H", os.path.join(HERE, "build/host/x14_host")))
    parser.add_argument("--gen", default=None, help="make_x14.py's output dir (default OUT/gen)")
    parser.add_argument("--tel", default=None, help="the session's telemetry file (default OUT/telemetry.jsonl)")
    parser.add_argument("--heater", default=os.environ.get("HEATER", ""),
                        help="the heater binary: this request's x14_host (required)")
    parser.add_argument("--target", type=float, default=58.0)
    parser.add_argument("--preheat", type=float, default=59.0, help="0: never heat (every run is then off protocol)")
    parser.add_argument("--max-heats", type=int, default=15)
    parser.add_argument("--max-wait", type=float, default=120.0)
    parser.add_argument("--quiet-s", type=float, default=2.0)
    parser.add_argument("--max-c", type=float, default=70.0)
    parser.add_argument("--stale-s", type=float, default=5.0)
    parser.add_argument("--secs", type=float, default=4.0)
    parser.add_argument("--idle", type=float, default=10.0)
    parser.add_argument("--burnin", type=int, default=2)
    parser.add_argument("--dry", action="store_true", help="print the device calls, open nothing")
    parser.add_argument("--smoke", action="store_true",
                        help="the heater check, the smoke arms (2 s each, no preheat, no burn-in), 2 train processes, "
                             "the smoke gate")
    parser.add_argument("--heater-ceiling", type=float, default=70.0)
    parser.add_argument("--train", default=None, help="run this train of arms.json instead of a pass")
    parser.add_argument("--processes", type=int, default=None, help="with --train: only the first N processes")
    parser.add_argument("--drop", default="", help="pass arms to leave out of the pass, comma-separated (not K.pi)")
    parser.add_argument("--plan", action="store_true", help="print the pass's PLAN line and exit; opens nothing")
    a = parser.parse_args()
    out, p = a.out, a.pass_
    os.makedirs(out, exist_ok=True)
    tel = a.tel or os.path.join(out, "telemetry.jsonl")
    stop_file = os.path.join(out, "STOP")
    host = socket.gethostname()
    if a.smoke:
        a.preheat, a.burnin, a.secs = 0.0, 0, 2.0

    gen = a.gen or os.path.join(out, "gen")
    manifest = json.load(open(os.path.join(gen, "arms.json")))
    table = {x["name"]: x for x in manifest["arms"]}
    trains = {t["name"]: t for t in manifest.get("trains", [])}
    anchor = ANCHOR
    drop = [x.strip() for x in a.drop.split(",") if x.strip()]
    for x in drop:
        if x == anchor:
            print("refused: --drop %s: the block anchor runs in every pass" % x, file=sys.stderr)
            sys.exit(EXIT_REFUSED)
        if x not in table or not table[x].get("in_passes", True):
            print("refused: --drop %s: not a pass arm of arms.json" % x, file=sys.stderr)
            sys.exit(EXIT_REFUSED)
    arms = [x for x in table if x != anchor and table[x].get("in_passes", True) and x not in drop]
    random.Random("%s|%d" % (host, p)).shuffle(arms)
    if a.plan:
        orphaned = sorted(x for x in arms if table[x].get("ref") in drop)
        print("PLAN runs=%d arms=%d dropped=%s orphaned=%s" % (a.burnin + 2 + len(arms), len(arms),
                                                              ",".join(drop) or "-", ",".join(orphaned) or "-"))
        return
    if not a.heater:
        print("refused: no --heater: the registered approach heats to --preheat before every run", file=sys.stderr)
        sys.exit(EXIT_REFUSED)
    if a.smoke:
        arms = list(SMOKE_ARMS)
    if a.train is not None and a.train not in trains:
        sys.exit("no train %s in arms.json" % a.train)
    last_end = [time.time() - 3600.0]
    heater_streak = [0]   # heater launches failed in a row, over the block

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

    def heater_records(r):
        """a heater process's launch records, and whether it worked: exit 0, at least one record, every record ok
        with no tensor error"""
        recs = []
        for line in r.stdout.splitlines():
            if line.startswith("X14 "):
                try:
                    recs.append(json.loads(line[len("X14 "):]))
                except ValueError:
                    recs.append({})
        good = (r.returncode == 0 and bool(recs) and
                all(x.get("ok") is True and x.get("tensor_errors", 1) == 0 for x in recs))
        return recs, good

    def heat(t):
        """one heater launch of the approach; the second failed one in a row ends the block"""
        r = device(["timeout", "10", a.heater] + HEATER_ARGS + ["--stop-file", stop_file], "heater", die_c=t)
        recs, good = heater_records(r)
        heater_streak[0] = 0 if good else heater_streak[0] + 1
        if heater_streak[0] >= 2:
            stop(EXIT_HEATER_FAIL, "two heater launches in a row failed (the last: exit %d, %d launch records)"
                 % (r.returncode, len(recs)))
        return good

    def approach():
        if a.dry:
            if a.preheat > 0:
                print("DRY: approach: heat to %g C with the heater, idle to %g C, %g s quiet" %
                      (a.preheat, a.target, a.quiet_s), flush=True)
            else:
                print("DRY: approach: no preheat, idle to %g C, %g s quiet" % (a.target, a.quiet_s), flush=True)
            return {"start_c": a.target, "heats": 0, "wait_s": 0.0, "timed_out": False, "on_protocol": True}
        t = reading()
        heats, fails, w0, timed_out = 0, 0, time.time(), False
        while True:
            while a.preheat > 0 and t < a.preheat and heats < a.max_heats:
                if not heat(t):
                    fails += 1
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
        on = not timed_out and a.preheat > 0 and hot >= a.preheat and in_band(t) and quiet >= a.quiet_s
        return {"start_c": t, "start_hot_c": hot, "heats": heats, "heater_fails": fails, "preheat_c": a.preheat,
                "target_c": a.target, "wait_s": round(time.time() - w0, 2), "quiet_s": round(quiet, 2),
                "timed_out": timed_out, "on_protocol": on}

    def run(arm, role, seq):
        ap_ = approach()
        cmd = (["timeout", "10", a.host_bin] + make_x14.host_args(table[arm], gen) +
               ["--seconds", "%g" % a.secs, "--stop-file", stop_file])
        r = device(cmd, "run", arm=arm, role=role, seq=seq)
        if r is None:
            return
        n = 0
        for line in r.stdout.splitlines():
            if line.startswith("X14 "):
                rec = json.loads(line[len("X14 "):])
                rec.update({"arm": arm, "host": host, "pass": p, "seq": seq, "role": role, "approach": ap_,
                            "rc": r.returncode})
                jwrite("runs.jsonl", rec)
                n += 1
            elif line.startswith("X14CHECK "):
                rec = json.loads(line[len("X14CHECK "):])
                rec.update({"arm": arm, "host": host, "pass": p, "seq": seq, "role": role})
                jwrite("checks.jsonl", rec)
        if r.returncode != 0 or n == 0:
            print("pass %d seq %d %s: rc %d, %d launches" % (p, seq, arm, r.returncode, n), file=sys.stderr, flush=True)

    def train_run(name, nproc, seq):
        """the train's processes back to back (no approach between them: the anchor's approach set the launch band)"""
        t = trains[name]
        for k in range(nproc):
            check_stop()
            reading()
            order = "SFFS" if k % 2 == 0 else "FSSF"
            cmd = (["timeout", "10", a.host_bin] + make_x14.train_args(t, table, gen, order) +
                   ["--stop-file", stop_file])
            r = device(cmd, "train", train=name, process=k, order=order, seq=seq)
            if r is None:
                continue
            n = 0
            for line in r.stdout.splitlines():
                if line.startswith("X14 "):
                    rec = json.loads(line[len("X14 "):])
                    rec.update({"train": name, "process": k, "order": order, "host": host, "pass": p, "seq": seq,
                                "role": "smoke" if a.smoke else "train", "rc": r.returncode})
                    jwrite("train.jsonl", rec)
                    n += 1
                elif line.startswith("X14CHECK "):
                    rec = json.loads(line[len("X14CHECK "):])
                    rec.update({"train": name, "process": k, "order": order, "host": host, "pass": p, "seq": seq,
                                "role": "smoke" if a.smoke else "train"})
                    jwrite("checks.jsonl", rec)
            if r.returncode != 0 or n == 0:
                print("pass %d train %s process %d: rc %d, %d launches" % (p, name, k, r.returncode, n),
                      file=sys.stderr, flush=True)

    def smoke_gate():
        """the registered smoke gate (see the module's docstring); exit EXIT_SMOKE when it fails"""
        if a.dry:
            print("DRY: smoke gate", flush=True)
            return
        def load(fn):
            path = os.path.join(out, fn)
            if not os.path.exists(path):
                return []
            return [json.loads(l) for l in open(path) if l.strip() and json.loads(l).get("pass") == p]
        runs, checks, tr = load("runs.jsonl"), load("checks.jsonl"), load("train.jsonl")
        bad = []
        for arm in SMOKE_ARMS:
            rs = [r for r in runs if r.get("arm") == arm and r.get("role") == "smoke"]
            if not rs:
                bad.append("%s: no launch record" % arm)
                continue
            for r in rs:
                if not r.get("ok") or r.get("tensor_errors", 1) != 0:
                    bad.append("%s launch %s: ok %s, tensor errors %s" % (arm, r.get("launch"), r.get("ok"),
                                                                          r.get("tensor_errors")))
            cpo = sorted(r["cycles_per_op"] for r in rs if r.get("launch", -1) >= 0) or [0.0]
            want = expected_cycles(table[arm])
            if abs(cpo[len(cpo) // 2] - want) > 0.005 * want:
                bad.append("%s: cycles per op %.3f, not %.0f" % (arm, cpo[len(cpo) // 2], want))
            cs = [c for c in checks if c.get("arm") == arm]
            if len(cs) < 2 or not all(c.get("ok") for c in cs):
                bad.append("%s: C read-back %s" % (arm, [(c.get("zero_rows_bad"), c.get("live_rows_zero")) for c in cs]))
        for k in range(SMOKE_PROCESSES):
            rs = sorted([r for r in tr if r.get("process") == k], key=lambda r: r["launch"])
            order = "SFFS" if k % 2 == 0 else "FSSF"
            want = [order[0], order[0]] + [order[(n - 1) % 4] for n in range(1, len(rs) - 1)]
            if len(rs) < 2 or [r["kind"] for r in rs] != want or not all(r.get("ok") for r in rs):
                bad.append("train %s process %d: %d records, kinds %s" % (SMOKE_TRAIN, k, len(rs),
                                                                          "".join(r.get("kind", "?") for r in rs)))
            cs = [c for c in checks if c.get("train") == SMOKE_TRAIN and c.get("process") == k]
            if len(cs) < 2 or not all(c.get("ok") for c in cs):
                bad.append("train %s process %d: C read-back not ok" % (SMOKE_TRAIN, k))
        gate_result(bad)

    def gate_result(bad):
        """record the smoke gate; a failed gate exits EXIT_SMOKE"""
        jwrite("marks.jsonl", dict(kind="smoke_gate", host=host, **{"pass": p}, ok=not bad, problems=bad))
        print("SMOKE-GATE %s %s" % ("PASS" if not bad else "FAIL", json.dumps(bad)), flush=True)
        if bad:
            sys.exit(EXIT_SMOKE)

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
        """the smoke's first device process: the heater must work (else the gate fails at once) and its board level
        must stay under the ceiling"""
        t = reading()
        r = device(["timeout", "10", a.heater] + HEATER_ARGS + ["--stop-file", stop_file], "heater_check", die_c=t)
        if r is None:
            return
        recs, good = heater_records(r)
        t1 = last_end[0]
        time.sleep(1.0)  # the meter's reading of the heater's last pass
        top, n = board_max(tel, t1 - 2.5, t1 + 0.8)
        jwrite("marks.jsonl", dict(kind="heater_level", host=host, **{"pass": p}, rc=r.returncode, launches=len(recs),
                                   ok=good, board_max_w=top, samples=n, ceiling_w=a.heater_ceiling))
        print("pass %d: heater check: exit %d, %d launch records, %s; highest board reading %s W over %d samples" %
              (p, r.returncode, len(recs), "ok" if good else "FAILED", top, n), flush=True)
        if not good:
            why = []
            if r.returncode != 0:
                why.append("exit %d" % r.returncode)
            if not recs:
                why.append("no launch record")
            elif not all(x.get("ok") is True and x.get("tensor_errors", 1) == 0 for x in recs):
                why.append("a launch not ok or with tensor errors")
            gate_result(["heater check (%s): %s" % (a.heater, ", ".join(why))])
        if top is None:
            stop(EXIT_STALE, "no board reading during the heater check")
        if top > a.heater_ceiling:
            stop(EXIT_HEATER, "heater board reading %.2f W above the %g W ceiling" % (top, a.heater_ceiling))

    check_stop()
    if a.train is None and not a.smoke:   # a pass: its plan first
        if a.dry:
            print("DRY: plan: %d arms, dropped %s" % (len(arms), ",".join(drop) or "-"), flush=True)
        else:
            jwrite("marks.jsonl", dict(kind="plan", host=host, **{"pass": p}, t_ms=int(time.time() * 1000),
                                       anchor=anchor, arms=arms, dropped=drop))
    idle("before")
    seq = 0
    if a.train is not None and not a.smoke:
        t = trains[a.train]
        nproc = t["processes"] if a.processes is None else min(a.processes, t["processes"])
        run(anchor, "train_anchor_first", seq)
        seq += 1
        train_run(a.train, nproc, seq)
        seq += 1
        run(anchor, "train_anchor_last", seq)
        seq += 1
        idle("after")
        print("pass %d: train %s, %d processes" % (p, a.train, nproc), flush=True)
        return
    if a.smoke:
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
    else:
        train_run(SMOKE_TRAIN, SMOKE_PROCESSES, seq)
        seq += 1
    idle("after")
    print("pass %d: %d runs" % (p, seq), flush=True)
    if a.smoke:
        smoke_gate()


if __name__ == "__main__":
    main()
