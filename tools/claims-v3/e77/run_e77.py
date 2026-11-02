#!/usr/bin/env python3
"""E77 (Q133): the rail launched and read at one temperature, at two rail voltages, on aifoundry2 card 0.

    python3 run_e77.py plan    [--protocol protocol.json]                 # the launch list and a time estimate
    python3 run_e77.py gates   --out <dir> [--protocol ...] [--dry]       # G0 reads under the lock; no write
    python3 run_e77.py smoke   --out <dir> [--protocol ...] [--dry]       # the sampler and one 2 s launch; no write
    python3 run_e77.py session --out <dir> --gates <gates.json> [--protocol ...] [--dry] [--max-card-min 47]

The design is E77-PLAN.md's (docs/reports/data/2026-10-27-q129-rail-ledger/), pre-registered in
docs/reports/data/2026-11-01-e77-rail-one-temperature/README.md: fp32 randn on per-shire hart counts, 4 s launches,
arm B at 800 MHz under the card's own governor (544/416/288/160 harts), arm A at 600 MHz with the static TDP level at 0
(1,024/768/544/288 harts), every launch from one die gate (preheat to 59 C, launch at <= 58 C once the rails have
settled), three passes per arm, one 8 s settling rung, the restore, a return burst that must show normal stepping, and
arm B's third pass after the restore.

What this runner writes to the card: ONE field, the static TDP level (DM_CMD_SET_MODULE_STATIC_TDP_LEVEL, 26), to the
literal 0 and back to the literal 65 that the gate read. Nothing else: never the threshold, never a clock, voltage,
power-management flag, log level, statistics reset or reset of any kind. Every read goes through ettelem-e77, which
cannot send a request that reaches the PMIC (its header lists what it sends), except the one DM_CMD_GET_VMIN_LUT read at
the gate (a copy out of the service processor's RAM, driver/flashfs.c:2073), sent by the vendor tool.

Lab etiquette (lab AGENT.md sections 4-5, E69's run_knob.py, which this is adapted from):
  * the card lock /run/lock/etsoc-shire0.lock, NON-blocking, held for the whole session (and for the gate reads);
  * before the session and before every launch: another logged-in user blocks unless every one of their sessions has
    been idle >= 120 min (E111's amendment A1, the same rule, fails closed); another user's device process, a stale one of
    ours, or the et_soc1 use count over the baseline blocks; a block ends the session (exit 3);
  * every device process is `timeout 10 ... < /dev/null` with --kernel and --stop-file, in its own session, never
    signalled; the sampler gets SIGTERM only;
  * the safety watcher: ANY single board reading >= 85.0 W, a die mean >= 72 C, the die high-water latch >= 80 C, and,
    while the TDP is 0, any minion clock other than 600 MHz during a measurement launch, touches the stop-file and ends
    the session (exit 4) - the governor is restored in `finally` whatever the exit;
  * a deadline watchdog (E72's), armed before the set, writes 65 back if the session has not released it by the
    deadline (75 min, or 18:55 PST if sooner);
  * the time gates: the session refuses to start after 18:00 PST and stops at 18:55 PST (restore included).

--dry touches no device: a toy card (TDP-0 pin at 600 MHz, rails with tau 1.05 s, a die) feeds a synthetic sampler, so
every gate, cut and safety path, and reduce_e77.py, can be exercised end to end.

Exit codes: 0 done; 1 error; 2 refused (protocol, preflight, host, time gate, NO-GO at the gate); 3 the card is not
ours; 4 a safety stop; 5 a signal; 6 RESTORE FAILED (the claim stays; never reset the card).
"""
import argparse
import errno
import fcntl
import hashlib
import json
import math
import os
import random
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

EXIT_OK, EXIT_ERR, EXIT_REFUSE, EXIT_CARD, EXIT_SAFETY, EXIT_SIGNAL, EXIT_RESTORE = 0, 1, 2, 3, 4, 5, 6
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
OTHER_COMM = re.compile(DEV_COMM.pattern + r"|^Runner\.Worker$")
CARD_HOST = "aifoundry2"
LOCK_PATH = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
DEVMNGT = "/opt/et/bin/dev_mngt_service"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_DEFAULT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

TDP_PIN_W, TDP_ORIG_W, THR_ORIG_C = 0, 65, 65          # the only two values ever written: 0, then the original 65
ALLOWED_TDP = (TDP_PIN_W, TDP_ORIG_W)
PIN_MHZ, FREE_MHZ = 600, 800
BOARD_ABORT_W = 85.0          # any single 10 Hz reading at or above it (the owner's envelope, as written)
DIE_ABORT_C = 72              # the die mean on any reading (minshire[0])
HIGH_ABORT_C = 80             # the high-water latch (minshire[2]; not a live reading: E69 A1)
HOLD_S, HOLD_GRACE_S = 10, 5
SAMPLER_TERM_WAIT_S = 30
MIN_IDLE_MIN = 120            # E111 A1
PST = "America/Los_Angeles"


def now_ms():
    return int(time.time() * 1000)


def iso_ms(ms=None):
    ms = now_ms() if ms is None else ms
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ms / 1000.0)) + f".{int(ms) % 1000:03d}" \
        + time.strftime("%z", time.localtime(ms / 1000.0))


def sha256_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError as e:
        return f"unreadable: {e.strerror}"


def me_user():
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:  # noqa: BLE001
        return os.environ.get("USER") or os.environ.get("LOGNAME") or ""


def run_out(cmd, timeout=15, env=None, cwd=None):
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL, close_fds=True,
                           env=env, cwd=cwd)
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as e:
        return -1, b"", str(e).encode()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def local_epoch(hhmm, tz=PST):
    """Today's HH:MM in the lab's zone as epoch seconds (the box runs in PST; the zone is checked at preflight)."""
    h, m = (int(x) for x in hhmm.split(":"))
    lt = time.localtime()
    return time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, h, m, 0, 0, 0, -1))


def parse_tel(line):
    """One sampler line -> dict(t, die, high, board, mhz, minion, sram, noc, mv) or None."""
    try:
        d = json.loads(line)
    except ValueError:
        return None
    try:
        ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
        sp = d.get("sp") or {}
        return {"t": int(d["t_ms"]), "die": num(ms[0]), "high": num(ms[2]) if len(ms) > 2 else None,
                "board": num(d.get("board_w")), "mhz": num((d.get("mhz") or {}).get("minion")),
                "minion": num((sp.get("minion_w") or [None])[0]), "mv": num((sp.get("minion_mv") or [None])[0])}
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


class EndSession(Exception):
    def __init__(self, reason, code):
        super().__init__(reason)
        self.reason, self.code = reason, code


class Refuse(Exception):
    pass


# ---------------------------------------------------------------------------------------------- idle logins (E111 A1)
_HHMM = re.compile(r"^\d{1,2}:\d\d$")


def blocking_users():
    """Other users who block: any whose some session reads idle under 120 min (or unreadable). Counts only are logged."""
    rc, out, _ = run_out(["who", "-u"], timeout=10)
    if rc != 0:
        return ["<who -u unreadable>"], {"unreadable": True}
    me, users = me_user(), {}
    for ln in out.decode(errors="replace").splitlines():
        f = ln.split()
        if not f or f[0] == me:
            continue
        idle = None
        for i in range(2, len(f) - 1):
            if _HHMM.match(f[i]):
                tok = f[i + 1]
                idle = 0 if tok == "." else 24 * 60 if tok == "old" else \
                    (int(tok.split(":")[0]) * 60 + int(tok.split(":")[1])) if _HHMM.match(tok) else None
                break
        users.setdefault(f[0], []).append(idle)
    blocking = sorted(u for u, ids in users.items() if any(i is None or i < MIN_IDLE_MIN for i in ids))
    rec = {"other_users": len(users), "blocking_users": len(blocking), "ignored_idle_users": len(users) - len(blocking),
           "rule_min_idle_min": MIN_IDLE_MIN}
    return blocking, rec


# ---------------------------------------------------------------------------------------------- protocol
class Launch:
    def __init__(self, arm, pas, rnd, rung, per_shire, seconds, budget, kind="work"):
        self.arm, self.pas, self.rnd, self.rung = arm, pas, rnd, rung
        self.per_shire, self.seconds, self.budget, self.kind = int(per_shire), float(seconds), float(budget), kind
        self.harts = 32 * self.per_shire
        self.name = f"{arm}{pas}-r{rnd}-g{rung}-{self.harts}h" if kind == "work" else f"{kind}-{self.harts}h"


def load_protocol(path):
    p = json.load(open(path))
    bad = []
    arms = p["arms"]
    for a in ("A", "B"):
        if a not in arms:
            bad.append(f"arm {a} missing")
            continue
        ps = arms[a]["per_shire"]
        if len(ps) != 4 or any(not (1 <= int(x) <= 32) for x in ps):
            bad.append(f"arm {a}: four per-shire counts 1..32")
        if int(arms[a]["tdp_w"]) not in ALLOWED_TDP:
            bad.append(f"arm {a}: tdp {arms[a]['tdp_w']} not in {ALLOWED_TDP}")
        h = arms[a]["heater"]
        if not (1 <= int(h["per_shire"]) <= 32):
            bad.append(f"arm {a}: heater per_shire")
    if int(arms["A"]["tdp_w"]) != TDP_PIN_W or int(arms["B"]["tdp_w"]) != TDP_ORIG_W:
        bad.append("arm A must be the TDP-0 pin and arm B the card's own 65 W")
    L = p["launch"]
    if not (0 < float(L["seconds"]) < float(L["budget"]) < HOLD_S):
        bad.append("launch: 0 < seconds < budget < 10")
    S = p["settling"]
    if not (0 < float(S["seconds"]) < float(S["budget"]) < HOLD_S):
        bad.append("settling: 0 < seconds < budget < 10 (the lab's timeout 10)")
    g = p["gate"]
    if not (int(g["preheat_c"]) > int(g["launch_c"])):
        bad.append("gate: preheat above launch")
    if p.get("type") != "fp32" or p.get("values") != "randn":
        bad.append("E77 holds fp32 randn fixed")
    return p, bad


def plan_passes(p):
    """[(phase, arm, pass, [Launch...])] in session order: B1 B2 | set 0 | A1 A2 A3 SETTLE | restore | RETURN B3."""
    out = []
    L = p["launch"]
    for arm, pas in (("B", 1), ("B", 2), ("A", 1), ("A", 2), ("A", 3), ("B", 3)):
        ps = p["arms"][arm]["per_shire"]
        rng = random.Random(f"E77|{arm}|{pas}")
        ls = []
        for rnd in range(1, int(p["rounds_per_pass"]) + 1):
            order = list(range(4))
            rng.shuffle(order)
            for gi in order:
                ls.append(Launch(arm, pas, rnd, gi + 1, ps[gi], L["seconds"], L["budget"]))
        out.append((f"{arm}{pas}", arm, pas, ls))
    return out


# ---------------------------------------------------------------------------------------------- dry card
class DryCard:
    """A toy aifoundry2 for --dry: idle 24 W, the minion rail at 22.3 mW per hart at 600 MHz scaled by f*V^2, rails as
    the PMIC's first-order average (tau 1.05 s), a die with a 6 s node, the 0.22.0 governor as E72 reads it (TDP 0: only
    DOWN, to the 600 MHz floor; otherwise UP while the 1 s average is under the TDP), a 0.25 W conduction term."""
    PTS = [(600, 0.516), (700, 0.567), (800, 0.618)]

    def __init__(self):
        self.die, self.sink = 53.0, 53.0
        self.pt, self.busy, self.harts = 0, False, 0
        self.tdp, self.thr = 65, 65
        self.avg, self.rail_avg, self.sram_avg, self.noc_avg = 24.0, 15.0, 3.0, 4.0
        self.events = []
        self.lock = threading.Lock()

    def loads(self):
        f, v = self.PTS[self.pt]
        k = (f / 600.0) * (v / 0.516) ** 2
        minion_sw = (0.02231 * self.harts * k - 0.45) if self.busy and self.harts else 0.0
        minion_sw = max(minion_sw, 0.0)
        leak = 0.27 * (self.die - 50)
        minion = 15.0 + minion_sw + 0.30 * leak
        sram = 3.0 + 0.03 * minion_sw + 0.06 * leak
        noc = 4.0 + 0.05 * minion_sw + 0.12 * leak
        i = minion / v
        conduction = 0.0012 * i * i
        board = 24.0 + minion_sw * 1.19 + 0.04 * minion_sw + leak + (conduction - 0.0012 * (15.0 / 0.516) ** 2)
        return board, minion, sram, noc, v * 1000

    def step(self, dt):
        with self.lock:
            board, minion, sram, noc, _ = self.loads()
            # E72's own trace on this card: the die reads 58 within ~0.5 s of a heater ending (a fast pole), so the die
            # follows its sink with a 1 s node, and the sink with a 90 s one
            self.die += dt * ((self.sink + 0.25 * (board - 24)) - self.die) / 1.0
            self.sink += dt * ((51 + 0.22 * (board - 24)) - self.sink) / 90.0
            a = dt / 1.05
            self.avg += a * (board - self.avg)
            self.rail_avg += a * (minion - self.rail_avg)
            self.sram_avg += a * (sram - self.sram_avg)
            self.noc_avg += a * (noc - self.noc_avg)
            if not self.busy:
                if self.pt != 0:
                    self.events.append(("power_idle", int(self.avg * 1000)))
                self.pt = 0
                return
            if self.avg * 1000 > self.tdp * 1000 and self.pt > 0:
                self.pt -= 1
                self.events.append(("Power throttle down", int(self.avg * 1000)))
            elif self.avg * 1000 < self.tdp * 1000 and self.pt < 2:
                self.pt += 1
                self.events.append(("Power throttle up", int(self.avg * 1000)))

    def set_busy(self, busy, harts=0):
        with self.lock:
            self.busy, self.harts = busy, harts

    def sample(self):
        with self.lock:
            board, minion, sram, noc, mv = self.loads()
            d = int(self.die)
            f = self.PTS[self.pt][0]
            return {"t_ms": now_ms(), "took_ms": 21, "since_reset_ms": -1,
                    "board_w": round(board + random.gauss(0, 0.2), 2),
                    "sp": {"board_avg_w": round(self.avg, 2), "minion_w": [round(self.rail_avg, 3), 0, 0],
                           "sram_w": [round(self.sram_avg, 3), 0, 0], "noc_w": [round(self.noc_avg, 3), 0, 0],
                           "minion_mv": [int(mv + random.choice((0, 1, 2))), 0, 0], "sram_mv": [750, 0, 0],
                           "noc_mv": [750, 0, 0]},
                    "temp_c": {"pmic": 40, "ioshire": [d - 5, 0, 0], "minshire": [d, d - 3, max(d + 3, 66)]},
                    "mhz": {"minion": f, "noc": 400, "ddr": 1600}, "profile": "no-PMIC-read"}


class DrySampler(threading.Thread):
    def __init__(self, path, card, every_ms):
        super().__init__(daemon=True)
        self.path, self.card, self.every = path, card, every_ms / 1000.0
        self.stop_flag = threading.Event()
        self.pid = -1
        self.returncode = None

    def run(self):
        with open(self.path, "a") as f:
            while not self.stop_flag.is_set():
                self.card.step(self.every)
                f.write(json.dumps(self.card.sample()) + "\n")
                f.flush()
                time.sleep(self.every)

    def poll(self):
        return None if self.is_alive() else 0


# ---------------------------------------------------------------------------------------------- watcher
class Watcher(threading.Thread):
    """Tails the current telemetry file; keeps a short history; trips the stop-file on the envelope."""

    def __init__(self, sess):
        super().__init__(daemon=True)
        self.s = sess
        self.path, self.pos = None, 0
        self.hist = []               # recent parsed samples (host receipt ms added)
        self.trip = None
        self.check_pin = False       # set while a measurement launch runs at TDP 0
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.max_board = None

    def follow(self, path):
        with self.lock:
            self.path, self.pos, self.hist = path, 0, []

    def last(self, max_age_s=3.0):
        with self.lock:
            if not self.hist:
                return None
            r = self.hist[-1]
            return r if now_ms() - r["rx"] <= max_age_s * 1000 else None

    def window(self, lo_ms, hi_ms):
        with self.lock:
            return [r for r in self.hist if lo_ms <= r["t"] <= hi_ms]

    def run(self):
        while not self.stop_flag.is_set():
            path = self.path
            if path and os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        f.seek(self.pos)
                        chunk = f.read()
                    nl = chunk.rfind(b"\n")
                    if nl >= 0:
                        with self.lock:
                            self.pos += nl + 1
                        for ln in chunk[:nl].splitlines():
                            if not ln.startswith(b"{"):
                                continue
                            t = parse_tel(ln)
                            if t is None:
                                continue
                            t["rx"] = now_ms()
                            with self.lock:
                                self.hist.append(t)
                                if len(self.hist) > 1200:
                                    del self.hist[:200]
                            self.check(t)
                except OSError:
                    pass
            time.sleep(0.05)

    def check(self, t):
        if t["board"] is not None:
            self.max_board = t["board"] if self.max_board is None else max(self.max_board, t["board"])
        if self.trip:
            return
        if t["board"] is not None and t["board"] >= BOARD_ABORT_W:
            self.fire(f"board {t['board']:.2f} W >= {BOARD_ABORT_W:g} W (one reading)")
        elif t["die"] is not None and t["die"] >= DIE_ABORT_C:
            self.fire(f"die mean {t['die']:.0f} C >= {DIE_ABORT_C} C")
        elif t["high"] is not None and t["high"] >= HIGH_ABORT_C:
            self.fire(f"die high-water {t['high']:.0f} C >= {HIGH_ABORT_C} C")
        elif self.check_pin and t["mhz"] is not None and int(t["mhz"]) != PIN_MHZ:
            self.fire(f"minion clock {t['mhz']:.0f} MHz during a launch at TDP 0 (the pin must read {PIN_MHZ})")

    def fire(self, why):
        self.trip = why
        self.s.touch(self.s.stop_file)
        self.s.mark("safety_trip", why)


# ---------------------------------------------------------------------------------------------- session
class Session:
    def __init__(self, a, proto):
        self.a, self.p = a, proto
        self.dry = a.dry
        self.root = os.path.abspath(a.root)
        self.out = os.path.abspath(a.out)
        self.stop_file = os.path.join(self.out, "STOP")
        self.lock_fd = None
        self.sampler = None
        self.heater_pids = set()
        self.base_idle = None
        self.base_samp = None
        self.card = DryCard() if self.dry else None
        T = proto["tools"]
        self.heater = os.path.join(self.root, T["heater"])
        self.kernel = os.path.join(self.root, T["kernel"])
        self.ettelem = os.path.join(self.root, T["ettelem"])
        self.every_ms = int(proto["sampler"]["every_ms"])
        self.t_lock = None
        self.last_proc_end = 0
        self.moved = False           # TDP 0 written and not yet restored
        self.ever_moved = False      # TDP 0 was sent at some point in this session
        self.restore_rec = None
        self.orig = None
        self.watcher = Watcher(self)
        os.makedirs(self.out, exist_ok=True)
        for d in ("tel", "sp", "logs"):
            os.makedirs(os.path.join(self.out, d), exist_ok=True)

    # -- records
    def jsonl(self, name, rec):
        rec = dict(rec)
        rec.setdefault("t_iso", iso_ms())
        with open(os.path.join(self.out, name), "a") as f:
            f.write(json.dumps(rec) + "\n")
        return rec

    def say(self, msg):
        line = time.strftime("%H:%M:%S ") + msg
        print(line, flush=True)
        with open(os.path.join(self.out, "run.log"), "a") as f:
            f.write(line + "\n")

    def mark(self, kind, detail="", **kw):
        self.jsonl("marks.jsonl", dict(t_ms=now_ms(), kind=kind, detail=detail, **kw))

    def touch(self, path):
        try:
            with open(path, "a"):
                os.utime(path, None)
        except OSError:
            pass

    def card_min(self):
        return 0.0 if self.t_lock is None else (time.time() - self.t_lock) / 60.0

    def env(self):
        return dict(os.environ, LD_LIBRARY_PATH=ET_LIB)

    # -- preflight
    def preflight(self, need_time=True):
        pf = []
        if not self.dry:
            host = socket.gethostname().split(".")[0]
            if host != CARD_HOST:
                pf.append(f"hostname {host!r} is not {CARD_HOST!r}")
            if time.strftime("%Z") not in ("PST", "PDT"):
                pf.append(f"the box's zone reads {time.strftime('%Z')}, not Pacific")
            for label, path in (("heater", self.heater), ("kernel", self.kernel), ("ettelem-e77", self.ettelem),
                                ("dev_mngt_service", DEVMNGT)):
                if not os.path.isfile(path):
                    pf.append(f"missing {label} {path}")
            if os.path.isfile(self.heater):
                blob = open(self.heater, "rb").read()
                for flag in (b"--stop-file", b"--kernel", b"--budget", b"--per-shire"):
                    if flag not in blob:
                        pf.append(f"heater has no {flag.decode()}")
            if os.path.isfile(self.ettelem):
                rc, so, _ = run_out([self.ettelem, "profile"], timeout=5)
                if rc != 0 or b'"no-PMIC-read"' not in so:
                    pf.append("ettelem-e77 profile does not read no-PMIC-read")
                blob = open(self.ettelem, "rb").read()
                if b"--reset-ms" in blob or b"loglevel %s" in blob:
                    pf.append("the ettelem given is not ettelem-e77")
            if not os.path.exists(LOCK_PATH):
                pf.append(f"no card lock {LOCK_PATH}")
            if not shutil.which("timeout") or not shutil.which("flock") or not shutil.which("setsid"):
                pf.append("timeout / flock / setsid missing")
        if need_time and not self.dry:
            if time.time() > local_epoch(self.p["time"]["no_start_after"]):
                pf.append(f"after {self.p['time']['no_start_after']} PST: no new card session (CONTEXT section 11)")
        if pf:
            raise Refuse("; ".join(pf))

    # -- etiquette
    def take_lock(self):
        if self.dry:
            self.t_lock = time.time()
            return
        fd = os.open(LOCK_PATH, os.O_RDWR)
        os.set_inheritable(fd, False)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            os.close(fd)
            if e.errno in (errno.EACCES, errno.EAGAIN):
                raise EndSession(f"other_user:lock_held:{LOCK_PATH}", EXIT_CARD)
            raise
        self.lock_fd = fd
        self.t_lock = time.time()
        self.say(f"card lock {LOCK_PATH} held")

    def release_lock(self):
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(self.lock_fd)
            self.lock_fd = None

    def modcount(self):
        try:
            for ln in open("/proc/modules"):
                p = ln.split()
                if p and p[0] == "et_soc1":
                    return int(p[2])
        except (OSError, ValueError, IndexError):
            return None
        return None

    def check_others(self, where):
        if self.dry:
            return
        hits = []
        blocking, rec = blocking_users()
        self.jsonl("idle_logins.jsonl", dict(rec, where=where))
        if blocking:
            hits.append(f"users:{len(blocking)}")
        rc, out, _ = run_out(["ps", "-eo", "uid=,pid=,state=,comm="])
        mine = {os.getpid()} | self.heater_pids
        if self.sampler is not None:
            mine.add(self.sampler.pid)
        for ln in out.decode(errors="replace").splitlines():
            f = ln.split(None, 3)
            if len(f) != 4:
                continue
            try:
                u, pid = int(f[0]), int(f[1])
            except ValueError:
                continue
            if f[2].strip().upper().startswith("Z") or pid in mine:
                continue
            comm = os.path.basename(f[3].strip())
            if u != os.getuid() and OTHER_COMM.search(comm):
                hits.append(f"proc:other:{comm}")
            elif u == os.getuid() and DEV_COMM.search(comm):
                hits.append(f"ours:{pid}:{comm}")
        n = self.modcount()
        base = self.base_samp if self.sampler is not None else self.base_idle
        if n is not None and base is not None and n > base:
            hits.append(f"et_soc1_use:{n}>{base}")
        if hits:
            self.mark("other_user", f"{where}: " + "; ".join(hits))
            raise EndSession("other_user:" + ";".join(hits)[:200], EXIT_CARD)

    # -- sampler
    def start_sampler(self, path, seconds):
        self.watcher.follow(path)
        if self.dry:
            self.sampler = DrySampler(path, self.card, self.every_ms)
            self.sampler.start()
            time.sleep(0.3)
            return True
        for attempt in range(1, 7):
            since = os.path.getsize(path) if os.path.exists(path) else 0
            out = open(path, "ab", buffering=0)
            try:
                self.sampler = subprocess.Popen(
                    [self.ettelem, "sample", "--seconds", str(int(seconds)), "--every-ms", str(self.every_ms)],
                    stdout=out, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=self.env(), close_fds=True,
                    cwd=self.root, start_new_session=True)
            finally:
                out.close()
            t0 = time.time()
            while time.time() - t0 < 10:
                try:
                    with open(path, "rb") as f:
                        f.seek(since)
                        if b"{" in f.read(8192):
                            self.mark("sampler_start", f"attempt {attempt}, pid {self.sampler.pid}")
                            return True
                except OSError:
                    pass
                if self.sampler.poll() is not None:
                    break
                time.sleep(0.25)
            self.stop_sampler()
            time.sleep(2)
        return False

    def stop_sampler(self):
        s, self.sampler = self.sampler, None
        if s is None:
            return
        if self.dry:
            s.stop_flag.set()
            s.join(timeout=5)
            return
        if s.poll() is None:
            s.terminate()
            t0 = time.time()
            while time.time() - t0 < SAMPLER_TERM_WAIT_S and s.poll() is None:
                time.sleep(0.1)
            if s.poll() is None:
                self.mark("error", f"sampler {s.pid} ignored SIGTERM for {SAMPLER_TERM_WAIT_S} s: left alone")
                raise EndSession("error:sampler_ignored_sigterm", EXIT_ERR)
        self.mark("sampler_stop", f"pid {s.pid}, rc {s.returncode}")

    # -- reads (sampler stopped; ettelem-e77 only)
    def tool(self, *args, timeout=HOLD_S):
        if self.dry:
            return 0, b"", b""
        return run_out(["timeout", str(timeout), self.ettelem, *args], timeout=timeout + 5, env=self.env(),
                       cwd=self.root)

    def read_config(self):
        """The two RAM GETs (TDP, threshold) plus power state and clock, straight from the firmware, or None."""
        if self.dry:
            with self.card.lock:
                return {"t_ms": now_ms(), "tdp_w": self.card.tdp, "temp_threshold_c": self.card.thr,
                        "power_state": 3, "power_state_name": "low_power",
                        "minion_mhz": self.card.PTS[self.card.pt][0], "profile": "no-PMIC-read"}
        rc, so, _ = self.tool("config")
        if rc != 0:
            return None
        try:
            return json.loads(so.decode(errors="replace").strip().splitlines()[-1])
        except (ValueError, IndexError):
            return None

    def read_uptime(self):
        if self.dry:
            return {"rc": 0, "day": 6, "hours": 2, "mins": int(time.time() / 60) % 60, "t_ms": now_ms()}
        rc, so, _ = self.tool("uptime")
        try:
            return json.loads(so.decode(errors="replace").strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"rc": rc}

    def queries(self, tag):
        """The ring (sptrace), the throttle residencies, the config: after a pass, with the sampler stopped."""
        q = {"tag": tag, "t_ms": now_ms(), "t_iso": iso_ms()}
        if self.dry:
            with self.card.lock:
                q["sp_events"] = list(self.card.events)
                self.card.events.clear()
            q["config"] = self.read_config()
            q["throttle_up_lines"] = sum(1 for e in q["sp_events"] if "up" in e[0])
            return q
        dump = os.path.join(self.out, "sp", f"{tag}.bin")
        rc, so, se = self.tool("sptrace", dump)
        q["sptrace_rc"] = rc
        q["sptrace_sha256"] = sha256_file(dump) if os.path.exists(dump) else None
        if os.path.exists(dump):
            blob = open(dump, "rb").read()
            q["throttle_up_lines"] = len(re.findall(rb"[Tt]hrottle [Uu]p", blob))
            q["throttle_down_lines"] = len(re.findall(rb"[Tt]hrottle [Dd]own", blob))
            q["pmic_alarm_lines"] = len(re.findall(rb"Pmic_Controller_Handle_Pmic_Error_Event|POWER_SAFE", blob))
        rc, so, se = self.tool("residency", "2", "3", "4")      # A1: not 5 or 6 (they log SP errors, E69's ring)
        q["residency_rc"] = rc
        q["residency"] = [json.loads(l) for l in so.decode(errors="replace").splitlines() if l.startswith("{")]
        q["config"] = self.read_config()
        return q

    # -- device processes
    def spawn(self, la, harts=None, seconds=None, budget=None, role="work"):
        ps = (harts // 32) if harts else la.per_shire
        sec = seconds if seconds is not None else la.seconds
        bud = budget if budget is not None else la.budget
        cmd = ["timeout", str(HOLD_S), self.heater, "--test", "fma", "--type", self.p["type"], "--pattern", "none",
               "--values", self.p["values"], "--shires", "0xffffffff", "--per-shire", str(ps),
               "--seconds", f"{sec:g}", "--budget", f"{bud:g}", "--seed", "1", "--kernel", self.kernel,
               "--stop-file", self.stop_file]
        t0 = now_ms()
        if self.dry:
            self.card.set_busy(True, 32 * ps)
            end = time.time() + sec + 0.3
            lines = []
            while time.time() < end and not os.path.exists(self.stop_file):
                a0 = now_ms()
                time.sleep(0.5)
                with self.card.lock:
                    f = self.card.PTS[self.card.pt][0]
                lines.append(json.dumps({"test": "fma", "type": "fp32", "values": "randn", "minions": 32 * ps,
                                         "iters": int(f * 1e6 * 0.5 / 546), "t_start_ms": a0, "t_end_ms": now_ms(),
                                         "ok": True}))
            self.card.set_busy(False)
            self.last_proc_end = now_ms()
            return cmd, 0, "\n".join("SPARSITY " + l for l in lines), "", t0, now_ms()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True,
                             env=self.env(), close_fds=True, cwd=self.root, start_new_session=True)
        self.heater_pids.add(p.pid)
        try:
            out, err = p.communicate(timeout=HOLD_S + HOLD_GRACE_S)
        except subprocess.TimeoutExpired:
            self.touch(self.stop_file)
            self.mark("error", f"device process {p.pid} outlived timeout {HOLD_S} s: left alone")
            raise EndSession(f"error:kernel_overran_hold10:{p.pid}", EXIT_ERR)
        finally:
            self.heater_pids.discard(p.pid)
            self.last_proc_end = now_ms()
        return cmd, p.returncode, out, err, t0, now_ms()

    def guard(self, where):
        if self.watcher.trip:
            raise EndSession(f"safety:{self.watcher.trip}", EXIT_SAFETY)
        if os.path.exists(self.stop_file):
            raise EndSession("stop_file", EXIT_SAFETY)
        if self.card_min() > float(self.a.max_card_min):
            raise EndSession("cut:max_card_min", EXIT_OK)
        if not self.dry and time.time() > local_epoch(self.p["time"]["hard_stop"]):
            raise EndSession(f"cut:hard_stop_{self.p['time']['hard_stop']}", EXIT_OK)
        if self.sampler is not None and self.sampler.poll() is not None:
            raise EndSession(f"error:sampler_exited:{where}", EXIT_ERR)

    def reading(self, max_age_s=3.0):
        r = self.watcher.last(max_age_s)
        if r is None and self.sampler is not None:
            raise EndSession("error:telemetry_stale", EXIT_ERR)
        return r

    # -- the gate: preheat to >= preheat_c, then launch at <= launch_c once the rails have settled
    def gate(self, arm, where):
        """Heat with the arm's heater (2 s launches) until the die mean reads >= preheat_c; then idle until it reads
        <= launch_c, at least min_approach_s after the last device process ended, with the minion rail settled by S2's
        own test computed live (|mean over [t-5, t-3] - mean over [t-2, t-0.3]| <= settle_w); if the die falls more
        than max_below_c under launch_c first, heat again (at most max_reheats times). Bounded everywhere."""
        g = self.p["gate"]
        H = self.p["arms"][arm]["heater"]
        pre, lc = int(g["preheat_c"]), int(g["launch_c"])
        heats, reheats, t0 = 0, 0, time.time()
        rec = {"preheat_c": pre, "launch_c_max": lc, "heater_harts": 32 * int(H["per_shire"])}
        rd = self.reading()
        if rd is None or rd["die"] is None:
            raise EndSession(f"error:no_reading:{where}", EXIT_ERR)
        while True:
            while rd["die"] < pre:
                if heats >= int(g["max_heats"]):
                    rec.update(reached=False, why="preheat not reached", heats=heats, reheats=reheats)
                    return rec
                self.guard(f"{where} heat")
                self.check_others(f"{where} heat")
                cmd, rc, out, err, a, b = self.spawn(None, harts=32 * int(H["per_shire"]), seconds=float(H["seconds"]),
                                                     budget=float(H["seconds"]) + 1.5, role="heat")
                heats += 1
                self.jsonl("launches.jsonl", {"role": "heat", "where": where, "arm": arm, "cmd": cmd, "rc": rc,
                                              "t_start_ms": a, "t_end_ms": b,
                                              "stderr_tail": err[-300:] if err else ""})
                if rc != 0:
                    raise EndSession(f"error:heater_rc_{rc}", EXIT_ERR)
                time.sleep(0.3)
                rd = self.reading()
            ta = time.time()
            fell = False
            floor_on = reheats < int(g["max_reheats"])     # after the last re-heat the floor no longer applies
            while time.time() - ta < float(g["max_wait_s"]):
                self.guard(f"{where} approach")
                rd = self.reading()
                app_s = (now_ms() - self.last_proc_end) / 1000.0
                if rd["die"] <= lc and app_s >= float(g["min_approach_s"]):
                    t = rd["t"]
                    far = [r["minion"] for r in self.watcher.window(t - 5000, t - 3000) if r["minion"] is not None]
                    near = [r["minion"] for r in self.watcher.window(t - 2000, t - 300) if r["minion"] is not None]
                    if len(far) >= 3 and len(near) >= 3:
                        settle = sum(far) / len(far) - sum(near) / len(near)
                        if abs(settle) <= float(g["settle_w"]):
                            below = rd["die"] < lc - int(g["max_below_c"])
                            rec.update(reached=True, heats=heats, reheats=reheats, approach_s=round(app_s, 2),
                                       launch_c=rd["die"], settle_w=round(settle, 3), below_floor=below,
                                       gate_s=round(time.time() - t0, 1))
                            return rec
                if floor_on and rd["die"] < lc - int(g["max_below_c"]):
                    fell = True
                    break
                time.sleep(0.2)
            reheats += 1
            rec.setdefault("reheat_why", []).append("fell below the floor" if fell else "approach timed out")
            if reheats > int(g["max_reheats"]):
                rec.update(reached=False, why="the rails did not settle within the wait", heats=heats,
                           reheats=reheats)
                return rec
            rd = self.reading()
            if rd["die"] >= pre:          # still hot after a timeout: wait again rather than heat
                continue

    # -- one launch
    def launch(self, la):
        self.check_others(la.name)
        g = self.gate(la.arm, la.name)
        if not g.get("reached"):
            self.say(f"    {la.name}: gate not reached ({g.get('why')}): skipped")
            self.jsonl("launches.jsonl", {"role": "skip", "name": la.name, "arm": la.arm, "pass": la.pas,
                                          "round": la.rnd, "rung": la.rung, "harts": la.harts, "gate": g})
            return False
        self.guard(la.name)
        self.watcher.check_pin = (la.arm == "A")
        try:
            cmd, rc, out, err, a, b = self.spawn(la)
        finally:
            self.watcher.check_pin = False
        recs = []
        for ln in (out or "").splitlines():
            if ln.startswith("SPARSITY "):
                try:
                    recs.append(json.loads(ln[9:]))
                except ValueError:
                    pass
        self.jsonl("launches.jsonl", {"role": la.kind, "name": la.name, "arm": la.arm, "pass": la.pas,
                                      "round": la.rnd, "rung": la.rung, "per_shire": la.per_shire, "harts": la.harts,
                                      "seconds": la.seconds, "gate": g, "cmd": cmd, "rc": rc, "t_start_ms": a,
                                      "t_end_ms": b, "sparsity": recs, "stderr_tail": err[-400:] if err else ""})
        self.say(f"    {la.name}: launch {g.get('launch_c')} C after {g.get('heats')} heats, approach "
                 f"{g.get('approach_s')} s, rc {rc}, {len(recs)} records")
        if rc != 0:
            self.n_fail = getattr(self, "n_fail", 0) + 1
            if self.n_fail >= 2:
                raise EndSession(f"error:kernel_failed_twice:{la.name}", EXIT_ERR)
        return True

    def run_pass(self, tag, arm, launches, cut_at_min, est_launch_s):
        tel = os.path.join(self.out, "tel", f"{tag}.jsonl")
        self.say(f"[{tag}] arm {arm}: {len(launches)} launches planned (cut at {cut_at_min} card-min)")
        if not self.start_sampler(tel, 3600):
            raise EndSession("error:sampler_would_not_start", EXIT_ERR)
        if not self.dry:
            self.base_samp = self.modcount()
            self.mark("use_count_with_sampler", str(self.base_samp))
            if self.base_idle is not None and self.base_samp is not None and self.base_samp > self.base_idle + 1:
                raise EndSession(f"other_user:use_count_{self.base_samp}>{self.base_idle}+1", EXIT_CARD)
        time.sleep(6.0)              # a settled pre-launch bracket for the first gate
        done, cut = 0, None
        rounds = sorted({la.rnd for la in launches})
        for rnd in rounds:
            batch = [la for la in launches if la.rnd == rnd]
            if self.card_min() + len(batch) * est_launch_s / 60.0 > cut_at_min:
                cut = f"round {rnd} and after: {self.card_min():.1f} card-min + {len(batch)} x {est_launch_s:.0f} s " \
                      f"> {cut_at_min}"
                self.mark("cut", f"{tag}: {cut}")
                self.say(f"    cut: {cut}")
                break
            for la in batch:
                if self.launch(la):
                    done += 1
        time.sleep(4.0)
        self.stop_sampler()
        q = self.queries(tag)
        self.jsonl("queries.jsonl", q)
        self.jsonl("passes.jsonl", {"pass": tag, "arm": arm, "planned": len(launches), "done": done, "cut": cut,
                                    "card_min": round(self.card_min(), 2), "max_board_w": self.watcher.max_board,
                                    "config_after": q.get("config")})
        return done, q

    # -- the governor: one field, two literal values, a read-back every time
    def set_tdp(self, w, why):
        if int(w) not in ALLOWED_TDP:
            raise EndSession(f"error:tdp_not_allowed:{w}", EXIT_ERR)
        before = self.read_config()
        if before is None:
            raise EndSession("error:governor_config_unreadable", EXIT_ERR)
        if before.get("temp_threshold_c") != THR_ORIG_C:
            raise EndSession(f"error:threshold_reads_{before.get('temp_threshold_c')}", EXIT_ERR)
        sent = []
        if before.get("tdp_w") != int(w):
            argv = ["timeout", "20", DEVMNGT, "-m", "DM_CMD_SET_MODULE_STATIC_TDP_LEVEL", "-n", "0", "-l", str(int(w)),
                    "-u", "5000"]
            t0 = now_ms()
            if self.dry:
                with self.card.lock:
                    self.card.tdp = int(w)
                rc, so, se = 0, b"dry", b""
            else:
                rc, so, se = run_out(argv, timeout=25, env=self.env(), cwd=self.root)
            sent.append({"cmd": argv, "rc": rc, "t_ms": t0, "t_iso": iso_ms(t0), "done_iso": iso_ms(),
                         "stdout_tail": so.decode(errors="replace")[-500:],
                         "stderr_tail": se.decode(errors="replace")[-300:] if se else ""})
            if int(w) == TDP_PIN_W:
                self.moved = self.ever_moved = True   # from the moment the request is sent, the finally restores
            if rc != 0:
                self.jsonl("gov.jsonl", {"event": "set_failed", "why": why, "before": before, "sent": sent})
                raise EndSession(f"error:governor_set_failed:{w}:rc{rc}", EXIT_ERR)
        after = self.read_config()
        rec = self.jsonl("gov.jsonl", {"event": "set", "why": why, "asked": {"tdp_w": int(w)}, "before": before,
                                       "after": after, "sent": sent, "readback_iso": iso_ms()})
        if after is None or after.get("tdp_w") != int(w) or after.get("temp_threshold_c") != THR_ORIG_C:
            raise EndSession(f"error:governor_readback_mismatch:asked{w}:got{after}", EXIT_ERR)
        self.say(f"    governor: TDP {before.get('tdp_w')} -> {after['tdp_w']} W, threshold "
                 f"{after['temp_threshold_c']} C, read back")
        return rec

    def restore(self, why):
        """TDP 65 back and read back. Never raises (it also runs in `finally`)."""
        try:
            rec = self.set_tdp(TDP_ORIG_W, why)
            ok = rec["after"]["tdp_w"] == TDP_ORIG_W and rec["after"]["temp_threshold_c"] == THR_ORIG_C
        except EndSession as e:
            rec, ok = {"error": e.reason}, False
        except Exception as e:  # noqa: BLE001
            rec, ok = {"error": f"{type(e).__name__}: {e}"}, False
        self.restore_rec = {"ok": ok, "rec": rec, "t_iso": iso_ms()}
        self.jsonl("gov.jsonl", {"event": "restore", "ok": ok, "why": why})
        if ok:
            self.moved = False
            self.touch(os.path.join(self.out, "release"))
            self.say("    RESTORE ok: TDP 65 W, threshold 65 C, read back; watchdog released")
        else:
            self.touch(os.path.join(self.out, "RESTORE_FAILED"))
            self.say("*** RESTORE FAILED. The claim stays. Never reset the card. Alert the owner.")
        return ok

    def arm_watchdog(self):
        """E72's detached restorer: if `release` has not appeared by the deadline, write 65 back under the lock."""
        cutoff = local_epoch(self.p["time"]["hard_stop"]) if not self.dry else time.time() + 4500
        deadline_s = int(max(60, min(float(self.p["watchdog"]["deadline_min"]) * 60, cutoff - time.time())))
        rel = os.path.join(self.out, "release")
        log = os.path.join(self.out, "watchdog.log")
        sh = os.path.join(self.out, "watchdog.sh")
        with open(sh, "w") as f:
            f.write(f"""#!/usr/bin/env bash
# E77 deadline watchdog (E72's): put TDP {TDP_ORIG_W} W back if the session has not released by the deadline.
set -u
REL={rel!r}
end=$(( $(date +%s) + {deadline_s} ))
while [ "$(date +%s)" -lt "$end" ]; do
  [ -e "$REL" ] && {{ echo "$(date -Is) released by the session, nothing to do" >> {log!r}; exit 0; }}
  sleep 5
done
echo "$(date -Is) DEADLINE reached, restoring TDP {TDP_ORIG_W} W" >> {log!r}
/usr/bin/flock -w 120 {LOCK_PATH!r} env LD_LIBRARY_PATH={ET_LIB} timeout 20 {DEVMNGT} \\
  -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -n 0 -l {TDP_ORIG_W} -u 5000 >> {log!r} 2>&1
echo "$(date -Is) set rc=$?" >> {log!r}
env LD_LIBRARY_PATH={ET_LIB} timeout 20 {self.ettelem!r} config >> {log!r} 2>&1
""")
        if self.dry:
            self.jsonl("gov.jsonl", {"event": "watchdog_armed", "dry": True, "deadline_s": deadline_s})
            return
        p = subprocess.Popen(["setsid", "nohup", "bash", sh], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        self.jsonl("gov.jsonl", {"event": "watchdog_armed", "pid": p.pid, "deadline_s": deadline_s,
                                 "deadline_iso": iso_ms(now_ms() + deadline_s * 1000), "script": sh,
                                 "release_file": rel, "sha256": sha256_file(sh)})
        self.say(f"    watchdog armed: pid {p.pid}, deadline {deadline_s} s")

    # -- the return burst: normal stepping after the restore
    def return_burst(self):
        R = self.p["return_burst"]
        tel = os.path.join(self.out, "tel", "RETURN.jsonl")
        if not self.start_sampler(tel, 600):
            raise EndSession("error:sampler_would_not_start", EXIT_ERR)
        if not self.dry:
            self.base_samp = self.modcount()
        time.sleep(3.0)
        cfg_before = None
        la = Launch("B", 0, 0, 1, int(R["per_shire"]), R["seconds"], R["budget"], kind="return")
        self.check_others("return")
        cmd, rc, out, err, a, b = self.spawn(la)
        recs = [json.loads(l[9:]) for l in (out or "").splitlines() if l.startswith("SPARSITY ")]
        time.sleep(3.0)
        clocks = [r["mhz"] for r in self.watcher.window(a, b) if r["mhz"] is not None]
        self.stop_sampler()
        q = self.queries("RETURN")
        steps = []
        for c in clocks:
            if not steps or steps[-1] != int(c):
                steps.append(int(c))
        ok = (FREE_MHZ in steps) and (q.get("throttle_up_lines", 0) >= 1)
        rec = {"role": "return", "cmd": cmd, "rc": rc, "t_start_ms": a, "t_end_ms": b, "sparsity": recs,
               "clock_steps": steps, "reached_800": FREE_MHZ in steps, "throttle_up_lines": q.get("throttle_up_lines"),
               "normal_stepping": ok, "config_before": cfg_before, "config_after": q.get("config")}
        self.jsonl("launches.jsonl", rec)
        self.jsonl("queries.jsonl", q)
        self.say(f"[RETURN] clock steps {steps}, throttle-up lines in the ring {q.get('throttle_up_lines')}: "
                 f"{'normal stepping' if ok else 'NOT SHOWN'}")
        return rec

    # -- gates (G0, no write)
    def lut_floor(self):
        """DM_CMD_GET_VMIN_LUT (a RAM copy) via the vendor tool, which writes dev0_vmin_lut.bin in its working directory;
        parsed in code: 14 points of 18 bytes, the minion frequency the first little-endian uint16 of each (E72's
        vmin-lut.json). Only the frequency points leave this function; the file stays in build/e77-private/."""
        if self.dry:
            return {"floor_mhz": 600, "points_mhz": [600, 700, 800], "dry": True}
        priv = os.path.join(self.root, "build", "e77-private")
        os.makedirs(priv, exist_ok=True)
        for fn in os.listdir(priv):
            if fn.endswith("vmin_lut.bin"):
                os.replace(os.path.join(priv, fn), os.path.join(priv, fn + f".{int(time.time())}.old"))
        t_call = time.time()
        rc, so, se = run_out(["timeout", "20", DEVMNGT, "-m", "DM_CMD_GET_VMIN_LUT", "-n", "0", "-u", "5000"],
                             timeout=25, env=self.env(), cwd=priv)
        res = {"rc": rc, "t_iso": iso_ms()}
        # the file lands in the tool's working directory (E72's dev0_vmin_lut.bin); look in the other likely places too,
        # for a file written by this call only, and keep it in build/e77-private/
        cand = []
        for d in (priv, self.root, os.path.expanduser("~")):
            try:
                for f in os.listdir(d):
                    fp = os.path.join(d, f)
                    if "vmin_lut" in f and f.endswith(".bin") and os.path.getmtime(fp) >= t_call - 2:
                        cand.append(fp)
            except OSError:
                pass
        if not cand:
            res["error"] = "no *vmin_lut*.bin written by this call"
            res["floor_mhz"] = None
            return res
        path = max(cand, key=os.path.getmtime)
        if os.path.dirname(path) != priv:
            dest = os.path.join(priv, os.path.basename(path))
            os.replace(path, dest)
            res["moved_from"] = os.path.dirname(path) == self.root and "the tree root" or "the home directory"
            path = dest
        blob = open(path, "rb").read()
        res.update(file=os.path.relpath(path, self.root), bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest())
        pts = []
        if len(blob) >= 14 * 18:
            pts = [struct.unpack_from("<H", blob, 18 * i)[0] for i in range(14)]
        nz = [x for x in pts if x]
        sane = bool(nz) and all(100 <= x <= 1600 for x in nz) and pts[:len(nz)] == nz and nz == sorted(nz)
        res.update(points_mhz=nz, zero_points=len(pts) - len(nz), parse_sane=sane,
                   floor_mhz=min(nz) if sane else None, max_mhz=max(nz) if sane else None)
        return res

    def host_reads(self):
        r = {}
        for key, cmd in (("uname", ["uname", "-r"]), ("host_uptime", ["uptime", "-s"]),
                         ("et_who", ["timeout", "10", "et-who"]), ("srcversion", ["cat", "/sys/module/et_soc1/srcversion"]),
                         ("dev_nodes", ["ls", "-l", "/dev/et0_mgmt", "/dev/et0_ops"]),
                         ("bdf", ["ls", "/sys/bus/pci/drivers/et_soc1"]), ("modinfo_path", ["modinfo", "-n", "et_soc1"])):
            rc, so, se = run_out(cmd, timeout=15)
            r[key] = {"rc": rc, "out": (so + se).decode(errors="replace")[-1500:]}
        mp = r["modinfo_path"]["out"].strip().splitlines()
        r["module_sha256"] = sha256_file(mp[-1]) if mp and os.path.isfile(mp[-1]) else None
        rc, so, _ = run_out(["pgrep", "-af", "live-collector"], timeout=10)
        procs = [l for l in so.decode(errors="replace").splitlines() if "pgrep" not in l]
        r["collector_running"] = len(procs)
        paths = sorted({w for l in procs for w in l.split() if w.endswith("live-collector.py")})
        r["collector_sha256"] = {os.path.basename(p): sha256_file(p) for p in paths if os.path.isfile(p)}
        return r

    def gates(self):
        self.preflight()
        g = {"experiment": "E77", "stage": "gates", "host": socket.gethostname(), "user": "<the run's lab account>",
             "dry": self.dry, "t_start_iso": iso_ms(), "profile": "no-PMIC-read"}
        if not self.dry:
            g["host_reads"] = self.host_reads()
            rc, out, _ = run_out(["et-lab-manifest"], timeout=60)
            open(os.path.join(self.out, "manifest-gates.txt"), "wb").write(out)
        g["sha256"] = {k: sha256_file(p) for k, p in (("heater", self.heater), ("kernel", self.kernel),
                                                      ("ettelem_e77", self.ettelem), ("runner", __file__))}
        verdict = []
        try:
            # the lock first, so the owner's collector starts no new read; then 2 s for one already in flight to end
            self.take_lock()
            time.sleep(0 if self.dry else 2.0)
            self.check_others("gates")
            self.base_idle = self.modcount()
            g["use_count_idle"] = self.base_idle
            g["config"] = self.read_config()
            g["uptime"] = self.read_uptime()
            g["lut"] = self.lut_floor()
            q = self.queries("gates")
            g["residency"] = q.get("residency")
            g["ring"] = {k: q.get(k) for k in ("sptrace_rc", "sptrace_sha256", "throttle_up_lines",
                                               "throttle_down_lines", "pmic_alarm_lines")}
        except EndSession as e:
            verdict.append(f"NO-GO: {e.reason}")
        finally:
            self.release_lock()
        cfg = g.get("config") or {}
        if cfg.get("tdp_w") != TDP_ORIG_W:
            verdict.append(f"NO-GO: TDP reads {cfg.get('tdp_w')}, not {TDP_ORIG_W}")
        if cfg.get("temp_threshold_c") != THR_ORIG_C:
            verdict.append(f"NO-GO: threshold reads {cfg.get('temp_threshold_c')}, not {THR_ORIG_C}")
        lut = g.get("lut") or {}
        if lut.get("floor_mhz") != PIN_MHZ:
            verdict.append(f"NO-GO: vmin-LUT floor {lut.get('floor_mhz')} (must parse to {PIN_MHZ} MHz)")
        up = g.get("uptime") or {}
        if up.get("rc") != 0:
            verdict.append("NO-GO: module uptime unreadable")
        else:
            mins = up["day"] * 1440 + up["hours"] * 60 + up["mins"]
            g["uptime_min"] = mins
            anchor = self.p["identity"]
            # the continuity anchor: E69's revisions read at 27 Oct 13:56:26 PDT; the SP must have been up since before it
            need = (time.time() - float(anchor["anchor_epoch"])) / 60.0
            g["minutes_since_anchor"] = round(need, 1)
            if not self.dry and mins < need:
                verdict.append(f"NO-GO: module uptime {mins} min is shorter than the {need:.0f} min since E69's identity "
                               f"read: the service processor has reset since, so the identity is not carried")
        g["verdict"] = verdict or ["GO-able: every live gate read as required"]
        g["t_end_iso"] = iso_ms()
        json.dump(g, open(os.path.join(self.out, "gates.json"), "w"), indent=1)
        print(json.dumps({k: g.get(k) for k in ("config", "uptime", "uptime_min", "minutes_since_anchor", "lut",
                                                "ring", "use_count_idle", "verdict")}, indent=1))
        return EXIT_OK if not verdict else EXIT_REFUSE

    # -- the smoke: the sampler and one short launch at the card's own settings; no governor write
    def smoke(self):
        self.preflight()
        sm = {"experiment": "E77", "stage": "smoke", "t_start_iso": iso_ms(), "dry": self.dry}
        self.watcher.start()
        code = EXIT_OK
        try:
            self.take_lock()
            time.sleep(0 if self.dry else 2.0)
            self.check_others("smoke")
            self.base_idle = self.modcount()
            sm["config_before"] = self.read_config()
            tel = os.path.join(self.out, "tel", "SMOKE.jsonl")
            if not self.start_sampler(tel, 120):
                raise EndSession("error:sampler_would_not_start", EXIT_ERR)
            if not self.dry:
                self.base_samp = self.modcount()
            time.sleep(6.0)
            la = Launch("B", 0, 0, 4, 5, 2.0, 3.0, kind="smoke")
            cmd, rc, out, err, a, b = self.spawn(la)
            recs = [json.loads(l[9:]) for l in (out or "").splitlines() if l.startswith("SPARSITY ")]
            time.sleep(3.0)
            self.stop_sampler()
            rows = [parse_tel(l) for l in open(tel) if l.startswith("{")]
            rows = [r for r in rows if r]
            full = [r for r in rows if None not in (r["board"], r["die"], r["mhz"], r["minion"], r["mv"])]
            raw = [json.loads(l) for l in open(tel) if l.startswith("{")]
            sm.update(launch_rc=rc, records=len(recs), samples=len(rows), complete_samples=len(full),
                      no_pmic_fields=not any(("die_mv" in x or "reg_mv" in x) for x in raw),
                      profile_tag=all(x.get("profile") == "no-PMIC-read" for x in raw) if raw else False,
                      max_board_w=max((r["board"] for r in full), default=None),
                      die_range=[min((r["die"] for r in full), default=None), max((r["die"] for r in full), default=None)],
                      high_water_max=max((r["high"] for r in rows if r["high"] is not None), default=None),
                      watcher_trip=self.watcher.trip,
                      clocks=sorted({int(r["mhz"]) for r in full}), cmd=cmd,
                      stderr_tail=err[-300:] if err else "")
            sm["queries"] = self.queries("smoke")
            ok = rc == 0 and len(recs) > 0 and len(full) >= 50 and sm["no_pmic_fields"] and sm["profile_tag"] \
                and not self.watcher.trip
            sm["verdict"] = "PASS" if ok else "FAIL"
            if not ok:
                code = EXIT_ERR
        except EndSession as e:
            sm["verdict"], code = f"FAIL: {e.reason}", e.code
        finally:
            try:
                self.stop_sampler()
            except EndSession:
                pass
            self.release_lock()
            self.watcher.stop_flag.set()
            sm["t_end_iso"] = iso_ms()
            json.dump(sm, open(os.path.join(self.out, "smoke.json"), "w"), indent=1)
            print(json.dumps({k: sm.get(k) for k in ("verdict", "launch_rc", "records", "samples", "complete_samples",
                                                    "no_pmic_fields", "profile_tag", "max_board_w", "clocks",
                                                    "die_range", "high_water_max", "watcher_trip")}))
        return code

    # -- the session
    def session(self, gates_path):
        self.preflight()
        gates = json.load(open(gates_path))
        if gates.get("verdict", [""])[0].startswith("NO-GO"):
            raise Refuse(f"the gate read NO-GO: {gates['verdict']}")
        if not self.dry and os.path.exists(os.path.join(self.out, "session.json")):
            raise Refuse(f"{self.out} already holds a session")
        P = self.p
        passes = plan_passes(P)
        est = float(P["est_launch_s"])
        sess = {"experiment": "E77", "host": socket.gethostname(), "dry": self.dry, "t_start_iso": iso_ms(),
                "protocol": P, "gates_file": os.path.relpath(gates_path, self.out) if not self.dry else gates_path,
                "gates_sha256": sha256_file(gates_path), "argv": sys.argv, "profile": "no-PMIC-read",
                "sha256": {k: sha256_file(p) for k, p in (("heater", self.heater), ("kernel", self.kernel),
                                                         ("ettelem_e77", self.ettelem), ("runner", __file__))},
                "plan": [[t, arm, pas, [la.name for la in ls]] for t, arm, pas, ls in passes]}
        rc, out, _ = run_out(["git", "rev-parse", "HEAD"], cwd=self.root)
        sess["git_head"] = out.decode().strip()
        if not self.dry:
            rc, out, _ = run_out(["et-lab-manifest"], timeout=60)
            open(os.path.join(self.out, "manifest.txt"), "wb").write(out)
        json.dump(sess, open(os.path.join(self.out, "session.json"), "w"), indent=1)
        self.watcher.start()
        code, reason = EXIT_OK, "done"
        C = P["cuts_card_min"]
        try:
            # the lock first, so the owner's collector starts no new read; then 2 s for one already in flight to end
            self.take_lock()
            time.sleep(0 if self.dry else 2.0)
            self.check_others("start")
            self.base_idle = self.modcount()
            self.orig = self.read_config()
            up0 = self.read_uptime()
            self.jsonl("gov.jsonl", {"event": "original", "config": self.orig, "uptime": up0})
            if self.orig is None or self.orig.get("tdp_w") != TDP_ORIG_W or self.orig.get("temp_threshold_c") != THR_ORIG_C:
                raise EndSession(f"nogo:originals_read_{self.orig}", EXIT_REFUSE)
            gcfg = gates.get("config") or {}
            if (gcfg.get("tdp_w"), gcfg.get("temp_threshold_c")) != (self.orig["tdp_w"], self.orig["temp_threshold_c"]):
                raise EndSession("nogo:originals_differ_from_the_committed_gate_read", EXIT_REFUSE)
            self.say(f"original governor: TDP {self.orig['tdp_w']} W, threshold {self.orig['temp_threshold_c']} C, "
                     f"{self.orig.get('power_state_name')}, {self.orig.get('minion_mhz')} MHz (the two RAM GETs)")
            self.jsonl("queries.jsonl", self.queries("start"))
            by = {t: (arm, ls) for t, arm, pas, ls in passes}
            # arm B, passes 1-2, at the card's own settings
            for t in ("B1", "B2"):
                self.run_pass(t, "B", by[t][1], float(C["before_move"]), est)
            # A2: the GO interlock. The first write waits for the file GO in the run directory, which the operator
            # creates only after the GO commit (the live gates filled) is pushed; bounded by move_by, else no move.
            go = os.path.join(self.out, "GO")
            if self.dry and not os.environ.get("E77_DRY_NO_GO"):
                self.touch(go)
            t_go = time.time()
            while not os.path.exists(go) and self.card_min() <= float(C["move_by"]):
                self.guard("waiting for GO")
                if time.time() - t_go > 10:
                    self.check_others("waiting for GO")
                    t_go = time.time()
                time.sleep(2.0)
            go_ok = os.path.exists(go)
            self.mark("go_file", "present" if go_ok else "absent at move_by")
            # the move
            if not go_ok or self.card_min() > float(C["move_by"]):
                why = "no GO file" if not go_ok else f"{self.card_min():.1f} card-min > {C['move_by']}"
                self.mark("cut", f"no move: {why}")
                self.say(f"    no move ({why}): arm A and arm B's third pass not run")
                raise EndSession(f"done:no_move:{why}", EXIT_OK)
            else:
                self.arm_watchdog()
                self.set_tdp(TDP_PIN_W, "E77 arm A: the TDP-0 pin at the vmin-LUT floor")
                for t in ("A1", "A2", "A3"):
                    self.run_pass(t, "A", by[t][1], float(C["restore_by"]), est)
                S = P["settling"]
                if self.card_min() + 0.6 <= float(C["restore_by"]):
                    sl = [Launch("A", 9, 1, 1, int(S["per_shire"]), S["seconds"], S["budget"], kind="settle")]
                    self.run_pass("SETTLE", "A", sl, float(C["restore_by"]) + 0.6, 25)
                else:
                    self.mark("cut", "settling rung not run: no time before the restore")
                self.restore("E77: the original TDP back after arm A")
                if not self.restore_rec["ok"]:
                    raise EndSession("RESTORE_FAILED", EXIT_RESTORE)
                self.return_burst()
            self.run_pass("B3", "B", by["B3"][1], float(C["b3_by"]), est)
        except EndSession as e:
            code, reason = e.code, e.reason
            self.say(f"session ends: {reason}")
        except Exception as e:  # noqa: BLE001
            code, reason = EXIT_ERR, f"error:{type(e).__name__}:{e}"
            self.say(f"session error: {reason}")
        finally:
            if code not in (EXIT_OK,):
                self.touch(self.stop_file)
            try:
                self.stop_sampler()
            except EndSession as e:
                self.mark("error", e.reason)
            if self.moved:
                if not self.restore("E77: restore in finally"):
                    code, reason = EXIT_RESTORE, f"RESTORE FAILED after: {reason}"
            closing, cc = {"skipped": "the session never read the originals: nothing was set, nothing read now"}, {}
            if self.orig is not None and (self.lock_fd is not None or self.dry):
                closing = {"config": self.read_config(), "uptime": self.read_uptime(), "t_iso": iso_ms()}
                self.jsonl("gov.jsonl", {"event": "closing", **closing})
                cc = closing["config"] or {}
                if self.ever_moved and (cc.get("tdp_w") != TDP_ORIG_W or cc.get("temp_threshold_c") != THR_ORIG_C):
                    code, reason = EXIT_RESTORE, f"CLOSING READ NOT 65/65: {cc}; after: {reason}"
                    self.touch(os.path.join(self.out, "RESTORE_FAILED"))
            self.release_lock()
            self.watcher.stop_flag.set()
            end = {"t_end_iso": iso_ms(), "exit": code, "reason": reason, "card_min": round(self.card_min(), 2),
                   "original": self.orig, "restore": self.restore_rec, "closing": closing,
                   "max_board_w": self.watcher.max_board, "safety_trip": self.watcher.trip}
            json.dump(end, open(os.path.join(self.out, "end.json"), "w"), indent=1)
            self.say(f"exit {code} ({reason}); closing read {cc.get('tdp_w')} W / {cc.get('temp_threshold_c')} C")
        return code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["plan", "gates", "smoke", "session"])
    ap.add_argument("--protocol", default=os.path.join(HERE, "protocol.json"))
    ap.add_argument("--out")
    ap.add_argument("--gates")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--max-card-min", type=float, default=47.0)
    ap.add_argument("--root", default=ROOT_DEFAULT)
    a = ap.parse_args()
    proto, bad = load_protocol(a.protocol)
    if bad:
        print("protocol refused:\n  " + "\n  ".join(bad), file=sys.stderr)
        return EXIT_REFUSE
    if a.stage == "plan":
        n = 0
        for t, arm, pas, ls in plan_passes(proto):
            print(f"{t}: arm {arm}, TDP {proto['arms'][arm]['tdp_w']} W, {len(ls)} launches: "
                  + " ".join(f"{la.harts}" for la in ls))
            n += len(ls)
        est = float(proto["est_launch_s"])
        print(f"{n} launches + 1 settling + 1 return; about {n * est / 60 + 6:.0f} card-min at {est:.0f} s a launch")
        return EXIT_OK
    if not a.out:
        print("--out required", file=sys.stderr)
        return EXIT_REFUSE
    s = Session(a, proto)

    def on_signal(signum, frame):
        s.touch(s.stop_file)
        raise EndSession(f"signal:{signum}", EXIT_SIGNAL)

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    try:
        if a.stage == "gates":
            return s.gates()
        if a.stage == "smoke":
            return s.smoke()
        if not a.gates:
            print("--gates <gates.json> required", file=sys.stderr)
            return EXIT_REFUSE
        return s.session(a.gates)
    except Refuse as e:
        print(f"refused: {e}", file=sys.stderr)
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
