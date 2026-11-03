#!/usr/bin/env python3
"""E160 (Q139): the session's queue, detached on aifoundry2. It is E143's queue_e143.py (E146's, E136's, E126's, E119's), stop-path tests included,
with E160's names, runner (run_e160.py, which runs E119's run_e119.py unchanged after checking that the heater is Q139(k)'s wrapper with the pinned
C-logging host, that the kernel and the sampler are E80's, that the protocol names the watcher's stop keys with a board stop at most 85 W, and that every
pool tile is blind6.json's) and protocol, and two more smoke checks (step 5): the C log of every smoke launch, and the C log's extra DMA time against
the launch budget. The slot file's line is "SLOT E160: ...", the session command is tools/claims-v3/e160/run_e160.py, the default protocol
tools/claims-v3/e160/protocol.json. Started before the slot, it needs nothing from outside: no ssh, no person.

    setsid nohup python3 tools/claims-v3/e160/queue_e160.py --slots ~/claude/work/q139-a2-e160-slot.txt --runs build/e160/runs > build/e160/queue.out 2>&1 < /dev/null &

Every time is epoch ms.

  1. Reads E160's slot from the slot file: SLOT E160's start and end.
  2. Sleeps until the slot's start. It launches nothing before it. Then it waits, polling every 20 s and taking no lock, until the card
     lock is free (`flock -n`), `et-who` names no holder, and no other user blocks by E111's rule (as the runner checks). It gives up at
     the slot's end minus 25 min and launches nothing.
  3. Records the box's state before anything of ours touches the card: `sensors -j` (host sensors only), `uptime`, the load, `ettelem config` under a
     non-blocking lock with timeout 10 (snapshot-start), and the last 40 min of the box's own 5 s history (history-before.jsonl).
  4. Runs the smoke session (block SMOKE: the rest reading, then three 2 s launches, one per type). A session refused at its start because the
     collector's reader was open at that instant (exit 3, no run recorded) is retried up to 5 times.
  5. Checks the smoke: exit 0, every launch rc 0 and ok, the cycles per op within 10% of the kinds kernel's (protocol.json smoke_cycles: 546 / 546 / 318),
     the config 65 W / 65 C; THE C LOG (E160): smoke/c-log.jsonl holds, before each work process, a host record naming the pinned C-logging host and
     E80's kernel (sha256), and for every SPARSITY line of every smoke launch a C record with the same t_start_ms and t_end_ms, ok, the poison written,
     no mask and no B stream, one group holding every participating minion, whose C is +0 in all 256 words (the zeros anchors' C in closed form: Q139(k)
     V1; a cheap string check, no reference computed on the box); THE DMA RULE (E160): delta = the smoke's median launch gap less E143's smoke median
     (1 ms) is the C log's extra time per launch, and the session runs only if E143's longest device-held time (6.57 s) + 17 x delta <= 7.2 s of the
     7.5 s budget. A failure ends the queue with QUEUE-HALT and no session. Under --dry (the toy card writes no C log) both are recorded as skipped.
  5b. THE STOP-PATH TESTS (E146's; the brief of 2 Nov 2026: "registered stops must read live samples ... test the stop path in the smoke").
     Session stoptest-board runs protocol-stoptest-board.json (the same runner, watcher and sampler; board_cap_w 30 W on 3 samples; one 6 s burst of the
     pool's fp32.anchor6_zeros); it passes only if it ended with exit 4 for "board", the watcher's safety_trip mark came while the work launch ran and within 1.5 s
     of the third live sampler line over 30 W, and the launch ended within 3 s of the trip. Session stoptest-die runs protocol-stoptest-die.json
     (abs_stop_c 30 C); it passes only if it ended with exit 4 for "die" within 1.5 s of the first live sampler line, before any work launch. Either
     failing ends the queue with QUEUE-HALT and no session.
  6. Runs the session (block BURST, 3 passes; run_e105.py's admission rule decides each cell, run_e119.py cuts the tail at the cap), with --max-card-min set so
     that it ends by itself cap-margin before the slot's end (the runner's own cap: exit 0, the end queries run). A login by another user ends a session
     at once, by E64's own check (exit 3): what it recorded stays, the run in flight is lost. The queue then waits again as in step 2, until nobody else is
     logged in, and starts the next session, s2, s3, with the runs already recorded skipped (E101_SKIP_DONE); nothing starts after the slot's end minus 25
     min. No login name goes in a record of the queue's; E64's end reason holds one, scrubbed at collection.
  7. Records snapshot-end, the same as snapshot-start, and exits.

The hard stop, as E98's queue: at slot_end - 120 s a running session's stop-file is touched (the launch loop ends at its next ~0.5 s
launch boundary), at slot_end - 30 s it gets SIGTERM if still alive (its handler ends the session; a device process is never
signalled). RUNS/QUEUE-STOP stops the queue at its next look before a session. Nothing is set on the card, so nothing is restored.
Every record goes to RUNS/queue.jsonl; RUNS/status.json holds the current state. A login never goes in a record, only a count.
"""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "e111"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import idle_logins_e111 as IL  # noqa: E402
import e160_common as EC  # noqa: E402
import statistics  # noqa: E402

LOCK = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
POLL_S = 20
GRACE_MIN_BEFORE_NEXT_REST = 20
CYC_LO, CYC_HI = 0.90, 1.10


def now_ms():
    return int(time.time() * 1000)


def out(cmd, timeout=30, env=None, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env, cwd=cwd)
        return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", str(e)


def parse_slots(path, name="E160"):
    """(start_ms, end_ms, the first E98 rest reading after the end in ms, or None)."""
    txt = open(path).read()
    m = re.search(rf"SLOT {name}: start (\d+) .*?end (\d+) ", txt)
    if not m:
        raise SystemExit(f"refused: no SLOT {name} in {path}")
    a, b = int(m.group(1)) * 1000, int(m.group(2)) * 1000
    rests = sorted(int(x) * 1000 for x in re.findall(r"rest reading starts (\d+)", txt))
    nxt = next((x for x in rests if x >= b), None)
    return a, b, nxt


ZERO_C_HEX = "0" * 2048


def read_clog(path):
    """the C log's records (the wrapper's host records, the host's tiles and C records); a line cut short is returned as None"""
    recs = []
    for ln in open(path, errors="replace"):
        ln = ln.strip()
        if not ln:
            continue
        try:
            recs.append(json.loads(ln))
        except ValueError:
            recs.append(None)
    return recs


def check_smoke_clog(rd, launches, proto):
    """E160's two smoke checks (step 5): the C log of every smoke launch, and the DMA rule. None if both hold, else why not. Writes rd/smoke-ccheck.json."""
    p = os.path.join(rd, "c-log.jsonl")
    if not os.path.exists(p):
        return "smoke: no C log (c-log.jsonl)"
    recs = read_clog(p)
    if any(r is None for r in recs):
        return "smoke: a C log line is cut short or not JSON"
    hosts = [r for r in recs if r.get("kind") == "host"]
    crec = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in recs if r.get("kind") == "c"}
    work = [L for L in launches if L.get("role") == "work"]
    if len(hosts) < len(work):
        return f"smoke: {len(hosts)} host records in the C log for {len(work)} work processes"
    for h in hosts:
        if h.get("host_sha256") != EC.CC_HOST_SHA256 or h.get("kernel_sha256") != EC.E80_SHA256[EC.KERNEL_REL] or h.get("kernel_from") != "runner":
            return f"smoke: the C log's host record names {h.get('host_sha256')} / {h.get('kernel_sha256')} ({h.get('kernel_from')}), not the pinned host and E80's kernel"
    n_lines, gaps, why = 0, [], None
    for L in work:
        sp = L.get("sparsity") or []
        gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(sp, sp[1:])]
        for s in sp:
            n_lines += 1
            r = crec.get((s.get("t_start_ms"), s.get("t_end_ms")))
            if r is None:
                why = why or f"smoke: {L.get('run')} launch {s.get('launch')} has no C record"
                continue
            g = r.get("groups") or []
            if not (r.get("ok") and r.get("poison") and r.get("use_mask") == 0 and r.get("b_stream") == 0):
                why = why or f"smoke: {L.get('run')} launch {s.get('launch')}: C record ok {r.get('ok')} poison {r.get('poison')} mask {r.get('use_mask')} stream {r.get('b_stream')}"
            elif len(g) != 1 or g[0].get("count") != r.get("participants") or r.get("participants") != s.get("minions"):
                why = why or f"smoke: {L.get('run')} launch {s.get('launch')}: {len(g)} C groups, {[x.get('count') for x in g]} of {r.get('participants')} minions"
            elif g[0].get("hex") != ZERO_C_HEX:
                why = why or f"smoke: {L.get('run')} launch {s.get('launch')}: a zeros tile's C is not +0 (first bytes {str(g[0].get('hex'))[:24]})"
    dma = proto.get("dma") or {}
    out = {"c_records": len(crec), "sparsity_lines": n_lines, "host_records": len(hosts), "gaps_ms": gaps}
    if why is None and gaps:
        med = statistics.median(gaps)
        delta = med - float(dma["e143_smoke_gap_ms_median"])
        proj = float(dma["e143_s1_held_s_max"]) + int(dma["launches"]) * max(0.0, delta) / 1000.0
        out.update(gap_ms_median=med, delta_ms=round(delta, 3), projected_held_max_s=round(proj, 3), limit_s=dma["projected_held_max_s"])
        if proj > float(dma["projected_held_max_s"]):
            why = f"smoke: the C log adds {delta:.1f} ms a launch; E143's longest run would hold the device {proj:.2f} s, over {dma['projected_held_max_s']} s of the {dma['budget_s']} s budget"
    elif why is None:
        why = "smoke: no launch gap to time the C log's DMA"
    out["why"] = why
    json.dump(out, open(os.path.join(rd, "smoke-ccheck.json"), "w"), indent=1)
    return why


class Queue:
    def __init__(self, a):
        self.a = a
        self.root = os.path.abspath(a.root)
        self.runs = os.path.abspath(a.runs)
        os.makedirs(self.runs, exist_ok=True)
        self.start_ms, self.end_ms, self.next_rest_ms = parse_slots(a.slots)
        if self.next_rest_ms is not None and self.next_rest_ms - self.end_ms < GRACE_MIN_BEFORE_NEXT_REST * 60000:
            raise SystemExit(f"refused: the slot ends {(self.next_rest_ms - self.end_ms) / 60000:.0f} min before E98's next rest reading")
        self.stop_ms = self.end_ms - a.cap_margin_s * 1000         # the session's own cap
        self.give_up_ms = self.end_ms - a.give_up_min * 60000
        self.ettelem = os.path.join(self.root, "build/ettelem-hpl/ettelem")
        os.environ["E111_IDLE_LOG"] = os.path.join(self.runs, "idle_logins.jsonl")   # every decision, counts only
        self.skip_done = []

    def rec(self, kind, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), kind=kind, **kw)
        with open(os.path.join(self.runs, "queue.jsonl"), "a") as f:
            f.write(json.dumps(d) + "\n")
        print(time.strftime("%H:%M:%S %Z"), json.dumps(d), flush=True)

    def status(self, **kw):
        d = dict(t_ms=now_ms(), zone=time.strftime("%Z"), pid=os.getpid(), **kw)
        tmp = os.path.join(self.runs, "status.json.tmp")
        json.dump(d, open(tmp, "w"))
        os.replace(tmp, os.path.join(self.runs, "status.json"))

    def stopped(self):
        return os.path.exists(os.path.join(self.runs, "QUEUE-STOP"))

    def halt(self, why):
        open(os.path.join(self.runs, "QUEUE-HALT"), "a").write(json.dumps({"t_ms": now_ms(), "why": why}) + "\n")
        self.rec("queue_halt", why=why)
        self.status(state="halted", why=why)

    # -- may the card be used
    def why_not_free(self):
        """None, or why the card may not be touched yet. Takes no lock beyond a non-blocking probe, which it releases at once."""
        if self.a.dry:
            return None
        rc, _, _ = out(["flock", "-n", LOCK, "true"], timeout=5)
        if rc != 0:
            return "the card lock is held"
        rc, so, _ = out(["timeout", "10", "et-who"], timeout=15)
        if rc == 0 and so.strip() and not so.strip().splitlines()[0].startswith("No process holds"):
            return "et-who names a holder"
        n = IL.others_count()
        if n:
            return f"{n} other user(s) block (E111's rule)"
        return None

    def wait_for_slot(self):
        """True when the card may be used; False when the queue must end."""
        while now_ms() < self.start_ms:
            if self.stopped():
                self.rec("stop", why="QUEUE-STOP before the slot")
                return False
            self.status(state="waiting for the slot", until_ms=self.start_ms)
            time.sleep(min(POLL_S, max(1.0, (self.start_ms - now_ms()) / 1000.0)))
        waits = {}
        while True:
            if self.stopped():
                self.rec("stop", why="QUEUE-STOP in the slot")
                return False
            if now_ms() >= self.give_up_ms:
                self.rec("give_up", why="the card did not come free by slot end - 25 min", waits=waits)
                return False
            why = self.why_not_free()
            if why is None:
                self.rec("card_free", waits=waits, late_s=round((now_ms() - self.start_ms) / 1000.0, 1))
                return True
            waits[why.split(" ")[0]] = waits.get(why.split(" ")[0], 0) + 1
            self.status(state="waiting for the card", why=why)
            time.sleep(POLL_S)

    # -- the record beside the sessions
    def snapshot(self, tag):
        snap = {"tag": tag, "t_ms": now_ms(), "zone": time.strftime("%Z")}
        if self.a.dry:
            json.dump(snap, open(os.path.join(self.runs, f"snapshot-{tag}.json"), "w"))
            return snap
        rc, so, _ = out(["sensors", "-j"], timeout=20)
        if rc == 0:
            open(os.path.join(self.runs, f"sensors-{tag}.json"), "w").write(so)
        snap["sensors_rc"] = rc
        rc, so, _ = out(["uptime"], timeout=5)
        snap["uptime"] = so.strip()
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        for attempt in range(1, 6):
            rc, so, se = out(["flock", "-n", LOCK, "timeout", "10", self.ettelem, "config"], timeout=15, env=env, cwd=self.root)
            if rc == 0:
                break
            time.sleep(2)
        snap["config_rc"], snap["config_attempts"] = rc, attempt
        open(os.path.join(self.runs, f"config-{tag}.txt"), "w").write(so + (("\nstderr: " + se[-300:]) if rc else ""))
        try:
            snap["config"] = json.loads(so.strip().splitlines()[-1])
        except (ValueError, IndexError):
            snap["config"] = None
        json.dump(snap, open(os.path.join(self.runs, f"snapshot-{tag}.json"), "w"), indent=1)
        return snap

    def copy_history(self, name, a_ms, b_ms):
        """The box's own 5 s history rows in [a_ms, b_ms) to RUNS/<name>."""
        if self.a.dry:
            return 0
        n = 0
        days = {time.strftime("%Y-%m-%d", time.gmtime(t / 1000.0)) for t in (a_ms, b_ms)}
        with open(os.path.join(self.runs, name), "w") as f:
            for d in sorted(days):
                p = os.path.expanduser(f"~/live/history/{d}.jsonl")
                try:
                    with open(p) as h:
                        for ln in h:
                            try:
                                t = json.loads(ln).get("t", 0)
                            except ValueError:
                                continue
                            if a_ms <= t < b_ms:
                                f.write(ln)
                                n += 1
                except OSError:
                    pass
        return n

    # -- one session
    def session(self, name, only=None, cap_min=None, protocol=None):
        rd = os.path.join(self.runs, name)
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e160/run_e160.py"), "--protocol", protocol or self.a.protocol, "--out", rd]
        if only:
            cmd += ["--only"] + only
        if cap_min is not None:
            cmd += ["--max-card-min", f"{cap_min:.2f}"]
        if self.a.dry:
            cmd.append("--dry")
        self.rec("session_start", name=name, cap_min=cap_min)
        self.status(state="running", session=name, t0_ms=now_ms())
        os.makedirs(self.runs, exist_ok=True)
        env = dict(os.environ)
        if self.skip_done and name != "smoke":
            env["E101_SKIP_DONE"] = ",".join(os.path.join(self.runs, n) for n in self.skip_done)
        with open(os.path.join(self.runs, f"{name}.out"), "ab") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=self.root,
                                    start_new_session=True, env=env)
        stopped, termed = False, False
        while proc.poll() is None:
            now = now_ms()
            if not stopped and now >= self.end_ms - 120000:
                os.makedirs(rd, exist_ok=True)
                open(os.path.join(rd, "STOP"), "a").close()
                stopped = True
                self.rec("slot_stop", session=name)
            if stopped and not termed and now >= self.end_ms - 30000:
                proc.terminate()
                termed = True
                self.rec("slot_term", session=name)
            time.sleep(1.0)
        try:
            end = json.load(open(os.path.join(rd, "end.json")))
        except (OSError, ValueError):
            end = None
        self.rec("session_end", name=name, rc=proc.returncode, end=end, slot_stopped=stopped)
        return proc.returncode

    def session_retry(self, name, only=None, cap_fn=None, protocol=None):
        """A session refused at the start (exit 3 and no run recorded: the collector's reader, opened in the instant before the lock
        was taken, reads as ours) moves aside and goes again, up to 5 times. Anything else is the session's result."""
        for k in range(1, 6):
            rc = self.session(name, only, cap_fn() if cap_fn else None, protocol)
            rd = os.path.join(self.runs, name)
            if rc == 3 and not os.path.exists(os.path.join(rd, "runs.jsonl")):
                os.rename(rd, f"{rd}.refused{k}")
                self.rec("session_refused_at_start", name=name, moved_to=f"{name}.refused{k}")
                time.sleep(POLL_S)
                why = self.why_not_free()
                while why is not None and now_ms() < self.give_up_ms and not self.stopped():
                    self.status(state="waiting for the card", why=why)
                    time.sleep(POLL_S)
                    why = self.why_not_free()
                if why is not None:
                    return rc
                continue
            return rc
        return rc

    def check_smoke(self):
        """None if the smoke is sound, else why not."""
        rd = os.path.join(self.runs, "smoke")
        try:
            end = json.load(open(os.path.join(rd, "end.json")))
            runs = [json.loads(x) for x in open(os.path.join(rd, "runs.jsonl"))]
            launches = [json.loads(x) for x in open(os.path.join(rd, "launches.jsonl"))]
        except (OSError, ValueError) as e:
            return f"smoke records unreadable: {e}"
        if end.get("exit") != 0:
            return f"smoke exit {end.get('exit')}: {end.get('reason')}"
        sm = next(b for b in json.load(open(self.a.protocol))["blocks"] if b["name"] == "SMOKE")
        n_runs = len(sm["runs"])
        n_work = sum(1 for r in sm["runs"] if (r.get("launch") or sm.get("launch") or {}).get("processes", 1) != 0)
        if len(runs) != n_runs or len([L for L in launches if L.get("role") == "work"]) != n_work:
            return f"smoke: {len(runs)} runs, {len(launches)} launches (the protocol's smoke: {n_runs} runs, {n_work} launches)"
        for r in runs:
            c = (r.get("queries") or {}).get("config") or {}
            if not self.a.dry and (c.get("tdp_w") != 65 or c.get("temp_threshold_c") != 65):
                return f"smoke: config {c}"
        for L in launches:
            if L.get("rc") != 0:
                return f"smoke: {L.get('run')} rc {L.get('rc')}"
            sp = L.get("sparsity") or []
            if not sp or not all(s.get("ok") for s in sp):
                return f"smoke: {L.get('run')} sparsity records {len(sp)}, not all ok"
            lab = next((r["label"] for r in runs if r["run"] == L.get("run")), None)
            want = json.load(open(self.a.protocol))["smoke_cycles"].get(lab)
            cyc = sp[-1].get("cycles_per_op")
            if not self.a.dry and (cyc is None or want is None or not CYC_LO <= cyc / want <= CYC_HI):
                return f"smoke: {L.get('run')} {cyc} cycles per op, the frozen law's {want}"
        if self.a.dry:
            self.rec("smoke_ccheck", skipped="dry: the toy card runs no host and writes no C log")
            return None
        bad = check_smoke_clog(rd, launches, json.load(open(self.a.protocol)))
        if bad is not None:
            return bad
        return None

    def check_stoptest(self, name, kind):
        """None if the stop fired on live samples as registered (step 5b), else why not."""
        rd = os.path.join(self.runs, name)
        try:
            end = json.load(open(os.path.join(rd, "end.json")))
            marks = [json.loads(x) for x in open(os.path.join(rd, "marks.jsonl"))]
        except (OSError, ValueError) as e:
            return f"{name}: records unreadable: {e}"
        if end.get("exit") != 4 or not str(end.get("reason", "")).startswith(f"safety:{'board' if kind == 'board' else 'die'}"):
            return f"{name}: exit {end.get('exit')} ({end.get('reason')}), not a {kind} safety stop"
        trips = [m for m in marks if m.get("kind") == "safety_trip"]
        if not trips:
            return f"{name}: no safety_trip mark"
        t_trip = trips[0]["t_ms"]
        tel = []
        for p in sorted(os.listdir(os.path.join(rd, "tel"))):
            for ln in open(os.path.join(rd, "tel", p), errors="replace"):
                if ln.startswith("{"):
                    try:
                        d = json.loads(ln)
                    except ValueError:
                        continue
                    ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                    tel.append((d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None))
        tel = [x for x in tel if x[0] is not None]
        if not tel:
            return f"{name}: no sampler line"
        work = []
        try:
            work = [json.loads(x) for x in open(os.path.join(rd, "launches.jsonl")) if '"role": "work"' in x]
        except OSError:
            pass
        safety = json.load(open(self.a.stoptest[kind])).get("safety", {})
        if kind == "board":
            cap, need = float(safety["board_cap_w"]), int(safety["cap_consecutive"])
            run, t_third = 0, None
            for t, w, _, _ in tel:
                run = run + 1 if (w is not None and w > cap) else 0
                if run >= need:
                    t_third = t
                    break
            if t_third is None:
                return f"{name}: no {need} sampler lines over {cap:g} W"
            if not -200 <= t_trip - t_third <= 1500:
                return f"{name}: the trip at {t_trip} is {t_trip - t_third} ms from the third live line over {cap:g} W"
            if not work:
                return f"{name}: no work launch recorded"
            L = work[0]
            if not (L["t_start_ms"] <= t_trip <= L["t_start_ms"] + 6500):
                return f"{name}: the trip at {t_trip} is not inside the work launch {L['t_start_ms']}-{L['t_end_ms']}"
            if L["t_end_ms"] - t_trip > 3000:
                return f"{name}: the launch ended {L['t_end_ms'] - t_trip} ms after the trip"
            self.rec("stoptest_detail", name=name, stop=kind, t_trip_ms=t_trip, t_third_line_ms=t_third, launch=[L["t_start_ms"], L["t_end_ms"]],
                     trip_after_line_ms=t_trip - t_third, launch_end_after_trip_ms=L["t_end_ms"] - t_trip, lines=len(tel))
            return None
        stop_c = float(safety["abs_stop_c"])
        first = next(((t, d, h) for t, _, d, h in tel if (d is not None and d >= stop_c) or (h is not None and h >= stop_c)), None)
        if first is None:
            return f"{name}: no sampler line at or above {stop_c:g} C"
        if not -200 <= t_trip - first[0] <= 1500:
            return f"{name}: the trip at {t_trip} is {t_trip - first[0]} ms from the first live line at or above {stop_c:g} C"
        if work:
            return f"{name}: a work launch ran before the die stop"
        self.rec("stoptest_detail", name=name, stop=kind, t_trip_ms=t_trip, t_first_line_ms=first[0], trip_after_line_ms=t_trip - first[0], lines=len(tel))
        return None

    def run(self):
        self.rec("queue_start", slot_start_ms=self.start_ms, slot_end_ms=self.end_ms, next_rest_ms=self.next_rest_ms,
                 python=sys.version.split()[0], sensors=bool(shutil.which("sensors")), protocol=self.a.protocol)
        if not self.wait_for_slot():
            self.status(state="ended", why="no launch")
            return 0
        t0 = now_ms()
        s0 = self.snapshot("start")
        n = self.copy_history("history-before.jsonl", t0 - 40 * 60000, t0 + 1)
        self.rec("before_first_launch", snapshot=s0, history_rows=n)
        rc = self.session_retry("smoke", ["SMOKE"], lambda: 3.0)
        bad = self.check_smoke()
        sc = None
        try:
            sc = json.load(open(os.path.join(self.runs, "smoke", "smoke-ccheck.json")))
            sc.pop("gaps_ms", None)
        except (OSError, ValueError):
            pass
        self.rec("smoke_check", rc=rc, bad=bad, ccheck=sc)
        if bad is not None:
            self.halt(bad)
            self.snapshot("end")
            return 0
        for kind in ("board", "die"):                     # step 5b
            name = f"stoptest-{kind}"
            rc = self.session_retry(name, ["STOPTEST"], lambda: 2.0, self.a.stoptest[kind])
            bad = self.check_stoptest(name, kind)
            self.rec("stoptest_check", name=name, rc=rc, bad=bad)
            if bad is not None:
                self.halt(bad)
                self.snapshot("end")
                return 0

        def cap():
            return min(float(self.a.cap), max(0.5, (self.stop_ms - now_ms()) / 60000.0))
        if now_ms() >= self.stop_ms or self.stopped():
            self.rec("stop", why="no time left, or QUEUE-STOP, before the session")
        else:
            k = 1
            while True:
                name = f"s{k}"
                rc = self.session_retry(name, None, cap)
                self.rec(f"{name}_end", rc=rc)
                self.skip_done.append(name)
                if rc != 3 or k >= 6 or self.stopped():
                    break
                why = self.why_not_free()
                while why is not None and now_ms() < self.give_up_ms and not self.stopped():
                    self.status(state="waiting for the card", why=why)
                    time.sleep(POLL_S)
                    why = self.why_not_free()
                if why is not None or now_ms() >= self.give_up_ms or self.stopped():
                    self.rec("no_resume", why=why)
                    break
                k += 1
                self.rec("resume", name=f"s{k}")
        s1 = self.snapshot("end")
        self.rec("queue_end", snapshot=s1, card_free_ms=now_ms(), before_slot_end_s=round((self.end_ms - now_ms()) / 1000.0, 1))
        self.status(state="ended", why="done")
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", required=True)
    ap.add_argument("--runs", required=True)
    ap.add_argument("--protocol", default="tools/claims-v3/e160/protocol.json")
    ap.add_argument("--stoptest-board", default="tools/claims-v3/e160/protocol-stoptest-board.json")
    ap.add_argument("--stoptest-die", default="tools/claims-v3/e160/protocol-stoptest-die.json")
    ap.add_argument("--cap", default=40.0, type=float)
    ap.add_argument("--give-up-min", default=25.0, type=float, help="minutes before the slot's end after which nothing starts; the dry run of the time cut shortens it")
    ap.add_argument("--cap-margin-s", default=180.0, type=float, help="the session's own cap ends it this long before the slot's end; the dry run of the hard stop shortens it")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    a.protocol = os.path.abspath(a.protocol) if os.path.exists(a.protocol) else os.path.join(os.path.abspath(a.root), a.protocol)
    a.stoptest = {}
    for kind, p in (("board", a.stoptest_board), ("die", a.stoptest_die)):
        a.stoptest[kind] = os.path.abspath(p) if os.path.exists(p) else os.path.join(os.path.abspath(a.root), p)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    return Queue(a).run()


if __name__ == "__main__":
    sys.exit(main())
