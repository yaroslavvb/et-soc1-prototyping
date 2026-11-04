#!/usr/bin/env python3
"""E170 (Q141(w)): the session's queue, detached on aifoundry1 for card 0. It is E165's queue_e165.py (E160's, E143's, E136's, E126's, E119's) with
E170's runner (run_e170.py), protocols and pins, ET_DEVICES=0 and card 0's lock, and three changes, each marked E170:

    setsid nohup python3 tools/claims-v3/e170/queue_e170.py --slots build/e170/slot.txt --runs build/e170/runs --cap 40 > build/e170/queue.out 2>&1 < /dev/null &

  1. Reads E170's slot (SLOT E170: start ... end ...) and waits for it, then for the card: card 0's lock free (flock -n), et-who naming no holder on
     EITHER card, and no other user blocking by E111's rule (an idle login does not block). It gives up at the slot's end minus 25 min.
  2. E170-A  CARD 0'S STATE, READ FIRST, READ PATHS ONLY (E170.md, "Card 0's state, read first"); any failure ends the queue with QUEUE-HALT
     before any launch:
       a. et-holders: nothing on card 0's lines; nothing of ours on either card (E164 has ended; never two sessions of ours on aifoundry1);
          et-holders unreadable fails closed;
       b. the host booted before E84's identity read (2026-10-31 15:42:00 PDT);
       c. card 0's module uptime (ettelem uptime through E170's guard, card 0's lock, timeout 10; DM_CMD_GET_MODULE_UPTIME, a RAM read) at least
          E84's 7,240 min plus the minutes since its read, less 2: no service-processor reset since E84 named the image; the reader's banner must
          name /dev/et0_mgmt. A shorter uptime is NO-GO (an image may have changed: the fix), never retried;
       d. ettelem config: TDP 65 W, threshold 65 C, minion clock 600 MHz (the idle point).
     The firmware-revisions query is never sent. Under --dry nothing is read and the gate is recorded as skipped.
  3. Records the box's state (sensors, uptime, ettelem config: snapshot-start) and the last 40 min of the box's 5 s history.
  4. E170-B  THE STOP-PATH TESTS FIRST, then the smoke (E164's order: the stop path is proved on live samples before any launch above the idle
     card's zeros). stoptest-die (abs_stop_c 30 C) must end exit 4 for "die" within 1.5 s of the first live line, before any work launch;
     stoptest-board (25 W on one sample; a 6 s burst of int8.anchor7_zeros) must end exit 4 for "board" while the launch runs, within 1.5 s of the
     first live line over 25 W, the launch ending within 3 s of the trip. Either failing: QUEUE-HALT, no smoke, no session.
  5. E170-C  THE SMOKE, RAMPED (the idle card 30 s; 2 s of int8.anchor7_zeros; 2 s of fp32.randn_a24k), under the session's stops (72 C; one sample
     over 65.9 W) and the alarm check. Checked as E165's: exit 0, every launch rc 0 and ok, cycles per op within 10% of 318 / 546, the config 65 W /
     65 C, the C log (a host record naming the pinned host and kernel before each work process; a C record for every SPARSITY line, ok, poisoned, no
     mask or B stream, one group of every minion; the zeros tile's C +0 in all 256 words), E160's DMA rule; and E170's: no smoke sampler line under
     590 MHz or over 65.9 W. A failure: QUEUE-HALT, no session.
  6. The session (block BURST, the 135 runs of the registered order; E105's admission decides each run, E119's cap cuts the tail), its cap set so
     it ends by itself before the slot's end. A session that ends exit 3 (another user, the module's use count) is resumed as E165's (s2, s3, ...,
     the recorded runs skipped); a safety stop or the alarm (exit 4) ends the queue: nothing after it runs.
  7. Records snapshot-end and exits.

The hard stop is E165's: at slot_end - 120 s the running session's stop file is touched, at slot_end - 30 s it gets SIGTERM. RUNS/QUEUE-STOP stops the
queue before its next session. Nothing is set on the card, so nothing is restored. A login never goes in a record, only a count.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import re
import shutil
import signal
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
sys.path.insert(0, HERE)
import idle_logins_e111 as IL  # noqa: E402
import e170_common as EC  # noqa: E402

LOCK = EC.LOCK0
ET_LIB = "/opt/et/lib"
POLL_S = 20
CYC_LO, CYC_HI = 0.90, 1.10
ZERO_C_HEX = "0" * 2048
HOLDERS = ["sudo", "-n", "/usr/local/sbin/et-holders"]


def now_ms():
    return int(time.time() * 1000)


def out(cmd, timeout=30, env=None, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, env=env, cwd=cwd)
        return r.returncode, r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", str(e)


def parse_slots(path, name="E170"):
    txt = open(path).read()
    m = re.search(rf"SLOT {name}: start (\d+) .*?end (\d+) ", txt)
    if not m:
        raise SystemExit(f"refused: no SLOT {name} in {path}")
    return int(m.group(1)) * 1000, int(m.group(2)) * 1000


def last_json(text):
    for ln in reversed(text.strip().splitlines()):
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return None
    return None


def continuity(u, tol=EC.UPTIME_TOL_MIN):
    """(ok, why): card 0's module uptime u ({t_ms, rc, day, hours, mins}) carries E84's identity read (E118's rule D2)"""
    if not u or u.get("rc") != 0 or None in (u.get("day"), u.get("hours"), u.get("mins"), u.get("t_ms")):
        return False, f"uptime unreadable: {u}"
    now_min = u["day"] * 1440 + u["hours"] * 60 + u["mins"]
    expect = EC.E84_UPTIME_MIN + (u["t_ms"] / 1000.0 - EC.E84_READ_EPOCH) / 60.0
    ok = now_min >= expect - tol
    return ok, f"module uptime {now_min} min; E84's {EC.E84_UPTIME_MIN} min + {expect - EC.E84_UPTIME_MIN:.1f} min since its read = {expect:.1f} (tolerance {tol:g})"


def holders_why(text, me):
    """None if nothing holds card 0 and nothing of ours holds either card; else why not (no login is returned, only node kinds and counts)"""
    c0, ours = 0, 0
    for ln in text.splitlines():
        f = ln.split()
        if len(f) < 2 or not (f[0].startswith("/dev/et") or f[0].startswith("lock:")):
            continue
        if f[0].startswith("/dev/et0_") or f[0] == "lock:etsoc-shire0.lock":
            c0 += 1
        if f[1] == me:
            ours += 1
    if c0:
        return f"card 0's node or lock is held ({c0} lines)"
    if ours:
        return f"{ours} node or lock lines of ours on aifoundry1: never two sessions of ours there"
    return None


def read_clog(path):
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


def check_smoke_clog(rd, launches, runs, proto):
    """E165's smoke C-log checks with E170's pins; the +0 check on the zeros tile only (the ramp's fp32 random tile has a nonzero C); the DMA rule"""
    p = os.path.join(rd, "c-log.jsonl")
    if not os.path.exists(p):
        return "smoke: no C log (c-log.jsonl)"
    recs = read_clog(p)
    if any(r is None for r in recs):
        return "smoke: a C log line is cut short or not JSON"
    hosts = [r for r in recs if r.get("kind") == "host"]
    crec = {(r.get("t_start_ms"), r.get("t_end_ms")): r for r in recs if r.get("kind") == "c"}
    work = [L for L in launches if L.get("role") == "work"]
    lab_of = {r["run"]: r["label"] for r in runs}
    if len(hosts) < len(work):
        return f"smoke: {len(hosts)} host records in the C log for {len(work)} work processes"
    for h in hosts:
        if h.get("host_sha256") != EC.CC_HOST_SHA256 or h.get("kernel_sha256") != EC.KERNEL_SHA256 or h.get("kernel_from") != "runner":
            return f"smoke: the C log's host record names {h.get('host_sha256')} / {h.get('kernel_sha256')} ({h.get('kernel_from')}), not the pinned host and kernel"
    n_lines, gaps, why = 0, [], None
    for L in work:
        sp = L.get("sparsity") or []
        zeros = lab_of.get(L.get("run"), "").endswith("anchor7_zeros")
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
            elif zeros and g[0].get("hex") != ZERO_C_HEX:
                why = why or f"smoke: {L.get('run')} launch {s.get('launch')}: a zeros tile's C is not +0 (first bytes {str(g[0].get('hex'))[:24]})"
    dma = proto.get("dma") or {}
    res = {"c_records": len(crec), "sparsity_lines": n_lines, "host_records": len(hosts), "gaps_ms": gaps}
    if why is None and gaps:
        med = statistics.median(gaps)
        delta = med - float(dma["e143_smoke_gap_ms_median"])
        proj = float(dma["e143_s1_held_s_max"]) + int(dma["launches"]) * max(0.0, delta) / 1000.0
        res.update(gap_ms_median=med, delta_ms=round(delta, 3), projected_held_max_s=round(proj, 3), limit_s=dma["projected_held_max_s"])
        if proj > float(dma["projected_held_max_s"]):
            why = f"smoke: the C log adds {delta:.1f} ms a launch; E143's longest run would hold the device {proj:.2f} s, over {dma['projected_held_max_s']} s"
    elif why is None:
        why = "smoke: no launch gap to time the C log's DMA"
    res["why"] = why
    json.dump(res, open(os.path.join(rd, "smoke-ccheck.json"), "w"), indent=1)
    return why


def tel_lines(rd):
    rows = []
    tdir = os.path.join(rd, "tel")
    for p in sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []:
        for ln in open(os.path.join(tdir, p), errors="replace"):
            if ln.startswith("{"):
                try:
                    d = json.loads(ln)
                except ValueError:
                    continue
                ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                rows.append((d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None, (d.get("mhz") or {}).get("minion")))
    return [x for x in rows if x[0] is not None]


class Queue:
    def __init__(self, a):
        self.a = a
        self.root = os.path.abspath(a.root)
        self.runs = os.path.abspath(a.runs)
        os.makedirs(self.runs, exist_ok=True)
        self.start_ms, self.end_ms = parse_slots(a.slots)
        self.stop_ms = self.end_ms - a.cap_margin_s * 1000
        self.give_up_ms = self.end_ms - a.give_up_min * 60000
        self.guard = os.path.join(self.root, EC.GUARD_REL)
        self.env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB, ET_DEVICES="0", V3_DEVICE="0")
        os.environ["E111_IDLE_LOG"] = os.path.join(self.runs, "idle_logins.jsonl")
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

    def why_not_free(self):
        if self.a.dry:
            return None
        rc, _, _ = out(["flock", "-n", LOCK, "true"], timeout=5)
        if rc != 0:
            return "card 0's lock is held"
        rc, so, _ = out(["timeout", "10", "et-who"], timeout=15)
        if rc == 0 and so.strip() and not so.strip().splitlines()[0].startswith("No process holds"):
            return "et-who names a holder (either card)"
        n = IL.others_count()
        if n:
            return f"{n} other user(s) block (E111's rule)"
        return None

    def wait_for_slot(self):
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

    def state_gate(self):
        """E170-A: None if card 0's state reads as registered, else why not. Reads only; writes the reads to RUNS/state-gate.json."""
        g = {"t_ms": now_ms(), "zone": time.strftime("%Z")}
        if self.a.dry:
            g["skipped"] = "dry: nothing read (et-holders, uptime -s, ettelem uptime, ettelem config)"
            json.dump(g, open(os.path.join(self.runs, "state-gate.json"), "w"), indent=1)
            return None
        why = None
        rc, so, _ = out(HOLDERS, timeout=20)
        if rc != 0:
            why = f"et-holders unreadable (rc {rc}): fails closed"
        else:
            why = holders_why(so, os.environ.get("USER", ""))
        g["holders"] = why or "card 0 free; nothing of ours on either card"
        if why is None:
            rc, so, _ = out(["uptime", "-s"], timeout=5)
            rc2, b, _ = out(["date", "-d", so.strip(), "+%s"], timeout=5)
            try:
                boot = int(b.strip())
            except ValueError:
                boot = None
            g["host_boot"] = so.strip()
            g["host_boot_epoch"] = boot
            if boot is None or boot >= EC.E84_READ_EPOCH:
                why = f"the host booted {so.strip()}, not before E84's identity read ({EC.HOST_BOOT_BEFORE}): the image cannot be carried"
        if why is None:
            rc, so, se = out(["flock", "-n", LOCK, "timeout", "10", self.guard, "uptime"], timeout=15, env=self.env, cwd=self.root)
            u = last_json(so)
            g["uptime_rc"], g["uptime"] = rc, u
            g["uptime_node_card0"] = ("/dev/et0_mgmt" in so + se) and ("0000:01:00.0" in so + se)
            ok, msg = continuity(u)
            g["continuity"] = msg
            if not ok:
                why = f"identity by continuity: {msg}: NO-GO (a service-processor reset since E84's read; the running image cannot be named)"
            elif not g["uptime_node_card0"]:
                why = "the uptime read's banner does not name /dev/et0_mgmt at 0000:01:00.0"
        if why is None:
            rc, so, se = out(["flock", "-n", LOCK, "timeout", "10", self.guard, "config"], timeout=15, env=self.env, cwd=self.root)
            c = last_json(so)
            g["config_rc"], g["config"] = rc, c
            if not c or c.get("tdp_w") != EC.WANT_CONFIG["tdp_w"] or c.get("temp_threshold_c") != EC.WANT_CONFIG["temp_threshold_c"] \
                    or c.get("minion_mhz") != EC.WANT_IDLE_MHZ:
                why = f"config {c}: not TDP 65 W / 65 C at a 600 MHz idle: the governor E170's predictions assume is not the one running"
        g["verdict"] = "GO" if why is None else f"NO-GO: {why}"
        json.dump(g, open(os.path.join(self.runs, "state-gate.json"), "w"), indent=1)
        return why

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
        for attempt in range(1, 6):
            rc, so, se = out(["flock", "-n", LOCK, "timeout", "10", self.guard, "config"], timeout=15, env=self.env, cwd=self.root)
            if rc == 0:
                break
            time.sleep(2)
        snap["config_rc"], snap["config_attempts"] = rc, attempt
        open(os.path.join(self.runs, f"config-{tag}.txt"), "w").write(so + (("\nstderr: " + se[-300:]) if rc else ""))
        snap["config"] = last_json(so)
        json.dump(snap, open(os.path.join(self.runs, f"snapshot-{tag}.json"), "w"), indent=1)
        return snap

    def copy_history(self, name, a_ms, b_ms):
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

    def session(self, name, only=None, cap_min=None, protocol=None):
        rd = os.path.join(self.runs, name)
        cmd = [sys.executable, os.path.join(self.root, "tools/claims-v3/e170/run_e170.py"), "--protocol", protocol or self.a.protocol, "--out", rd]
        if only:
            cmd += ["--only"] + only
        if cap_min is not None:
            cmd += ["--max-card-min", f"{cap_min:.2f}"]
        if self.a.dry:
            cmd.append("--dry")
        self.rec("session_start", name=name, cap_min=cap_min)
        self.status(state="running", session=name, t0_ms=now_ms())
        env = dict(self.env)
        if self.skip_done and name.startswith("s"):
            env["E101_SKIP_DONE"] = ",".join(os.path.join(self.runs, n) for n in self.skip_done)
        with open(os.path.join(self.runs, f"{name}.out"), "ab") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=self.root, start_new_session=True, env=env)
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
        rd = os.path.join(self.runs, "smoke")
        try:
            end = json.load(open(os.path.join(rd, "end.json")))
            runs = [json.loads(x) for x in open(os.path.join(rd, "runs.jsonl"))]
            launches = [json.loads(x) for x in open(os.path.join(rd, "launches.jsonl"))]
        except (OSError, ValueError) as e:
            return f"smoke records unreadable: {e}"
        if end.get("exit") != 0:
            return f"smoke exit {end.get('exit')}: {end.get('reason')}"
        proto = json.load(open(self.a.protocol))
        sm = next(b for b in proto["blocks"] if b["name"] == "SMOKE")
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
            want = proto["smoke_cycles"].get(lab)
            cyc = sp[-1].get("cycles_per_op")
            if not self.a.dry and (cyc is None or want is None or not CYC_LO <= cyc / want <= CYC_HI):
                return f"smoke: {L.get('run')} {cyc} cycles per op, the frozen law's {want}"
        tl = tel_lines(rd)
        low = [x for x in tl if x[4] is not None and x[4] < EC.MIN_MHZ_ALARM]
        hot = [x for x in tl if x[1] is not None and x[1] > EC.SAFETY["board_cap_w"]]
        self.rec("smoke_tel", lines=len(tl), board_max_w=max((x[1] for x in tl if x[1] is not None), default=None),
                 die_max_c=max((x[3] or x[2] for x in tl if (x[3] or x[2]) is not None), default=None), under_590=len(low), over_stop=len(hot))
        if not self.a.dry and (low or hot):
            return f"smoke: {len(low)} sampler lines under {EC.MIN_MHZ_ALARM:g} MHz, {len(hot)} over {EC.SAFETY['board_cap_w']} W"
        if self.a.dry:
            self.rec("smoke_ccheck", skipped="dry: the toy card runs no host and writes no C log")
            return None
        return check_smoke_clog(rd, launches, runs, proto)

    def check_stoptest(self, name, kind):
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
        tel = [(t, w, d, h) for t, w, d, h, _ in tel_lines(rd)]
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
            run, t_line = 0, None
            for t, w, _, _ in tel:
                run = run + 1 if (w is not None and w > cap) else 0
                if run >= need:
                    t_line = t
                    break
            if t_line is None:
                return f"{name}: no {need} sampler line(s) over {cap:g} W"
            if not -200 <= t_trip - t_line <= 1500:
                return f"{name}: the trip at {t_trip} is {t_trip - t_line} ms from the live line over {cap:g} W"
            if not work:
                return f"{name}: no work launch recorded"
            L = work[0]
            if not (L["t_start_ms"] <= t_trip <= L["t_start_ms"] + 6500):
                return f"{name}: the trip at {t_trip} is not inside the work launch {L['t_start_ms']}-{L['t_end_ms']}"
            if L["t_end_ms"] - t_trip > 3000:
                return f"{name}: the launch ended {L['t_end_ms'] - t_trip} ms after the trip"
            self.rec("stoptest_detail", name=name, stop=kind, t_trip_ms=t_trip, t_line_ms=t_line, launch=[L["t_start_ms"], L["t_end_ms"]],
                     trip_after_line_ms=t_trip - t_line, launch_end_after_trip_ms=L["t_end_ms"] - t_trip, lines=len(tel))
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
        self.rec("queue_start", slot_start_ms=self.start_ms, slot_end_ms=self.end_ms, python=sys.version.split()[0],
                 sensors=bool(shutil.which("sensors")), protocol=self.a.protocol, dry=self.a.dry)
        if not self.wait_for_slot():
            self.status(state="ended", why="no launch")
            return 0
        why = self.state_gate()                                       # E170-A
        self.rec("state_gate", verdict="GO" if why is None else f"NO-GO: {why}")
        if why is not None:
            self.halt(f"state gate: {why}")
            return 0
        t0 = now_ms()
        s0 = self.snapshot("start")
        n = self.copy_history("history-before.jsonl", t0 - 40 * 60000, t0 + 1)
        self.rec("before_first_launch", snapshot=s0, history_rows=n)
        for kind in ("die", "board"):                                 # E170-B
            name = f"stoptest-{kind}"
            rc = self.session_retry(name, ["STOPTEST"], lambda: 2.0, self.a.stoptest[kind])
            bad = self.check_stoptest(name, kind)
            self.rec("stoptest_check", name=name, rc=rc, bad=bad)
            if bad is not None:
                self.halt(bad)
                self.snapshot("end")
                return 0
        rc = self.session_retry("smoke", ["SMOKE"], lambda: 3.0)      # E170-C
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
    ap.add_argument("--protocol", default="tools/claims-v3/e170/protocol.json")
    ap.add_argument("--stoptest-board", default="tools/claims-v3/e170/protocol-stoptest-board.json")
    ap.add_argument("--stoptest-die", default="tools/claims-v3/e170/protocol-stoptest-die.json")
    ap.add_argument("--cap", default=float(EC.CAP_CARD_MIN), type=float)
    ap.add_argument("--give-up-min", default=25.0, type=float)
    ap.add_argument("--cap-margin-s", default=180.0, type=float)
    ap.add_argument("--root", default=os.path.join(HERE, "..", "..", ".."))
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
