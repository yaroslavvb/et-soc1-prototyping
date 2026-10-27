#!/usr/bin/env python3
"""E64 (Q123), Horace: power limit. The session runner: which of the governor's two limits, the 65 W power
test or the 65 C thermal test, sets the speed of the Horace matmul on aifoundry2, and when.

    python3 run_hpl.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...]
                       [--max-card-min N] [--list] [--root <tree>]

A run is: a start gate (a cool die, or a heated die caught on its falling edge), one or more matmul launch
processes back to back, an idle tail, then three read-only management queries once the sampler has stopped:
the service processor's trace ring (`ettelem sptrace`, which names every governor decision and its cause),
its throttle residencies (`ettelem residency 2 3 4 5 6`) and its static configuration (`ettelem config`: TDP,
threshold). The management node is single-opener (14-card-behaviour.md), so the sampler runs from the gate to
the tail and is stopped before the queries.

The sampler runs WITHOUT --reset-ms. E63's runner resets the SP statistics every second, and the reset also
restarts the PMIC's running average (E41); the governor's power loops exit on that average (thermal_pwr_mgmt.c
at ffca4cbb4, power_throttling()), so a reset would change the behaviour this experiment measures.

Lab etiquette, as E62's and E63's runners (tools/claims-v3/hm/run_hm.py, hlc/run_hlc.py), ported from lib.sh:
  * the card lock /run/lock/etsoc-shire0.lock with a NON-blocking flock, held for the whole session; held by
    someone else -> exit 3 at once. Nothing here waits for a person.
  * the other-user checks (another logged-in user, another user's device process, a stale one of ours, the
    et_soc1 use count over the baseline) before the session and before every launch process: a hit ends the
    session, exit 3.
  * every device process is one `timeout 10 ... < /dev/null` with an explicit --kernel and --stop-file and
    LD_LIBRARY_PATH=/opt/et/lib, in its own session; never signalled. The wait on it is bounded at hold10 + 5 s;
    one that outlives that is left alone, reported, and ends the session.
  * the sampler is stopped with SIGTERM only (30 s), SIGKILL and one management-queue drain only if it ignores
    TERM; six start attempts, one drain after the second (lib.sh:150-176).
  * a safety watcher reads the sampler's lines: die mean or hottest sensor >= safety.abs_stop_c on one sample,
    or board_w > safety.board_cap_w on cap_consecutive samples, touches the stop-file (the launch loop ends at
    its next ~0.5 s launch boundary) and ends the session (exit 4). A protocol with abs_stop_c > 90 is refused.
  * E69 DOES set two of the governor's fields - the static TDP level (DM 26) and the software temperature
    threshold (DM 22) - because that is the experiment; it sets NOTHING else: no clock, no voltage, no active
    power management flag, no log level, no reset. Every set is logged with its read-back in gov.jsonl, and the
    originals are restored and read back in the session's `finally`, whatever the exit.

--dry touches no device: no lock, no kernel, no ettelem. The sampler becomes a synthetic generator fed by a toy
die-and-governor model (the 0.20.0 rules as 16-dvfs-and-leakage.md and 14-card-behaviour.md read them), so the
gates, the safety paths and reduce_hpl.py can be exercised end to end.

Exit codes: 0 done; 1 error; 2 refused (bad protocol, preflight, wrong host); 3 the card is not ours;
4 a safety stop (or RUNDIR/STOP); 5 a signal.
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
import subprocess
import sys
import threading
import time

EXIT_OK, EXIT_ERR, EXIT_REFUSE, EXIT_CARD, EXIT_SAFETY, EXIT_SIGNAL = 0, 1, 2, 3, 4, 5
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
OTHER_COMM = re.compile(DEV_COMM.pattern + r"|^Runner\.Worker$")
CARD_HOST = "aifoundry2"
LOCK_PATH = "/run/lock/etsoc-shire0.lock"
ET_LIB = "/opt/et/lib"
DEVMNGT = "/opt/et/bin/dev_mngt_service"

# E69's governor bounds. The cap is never RAISED above the card's own default (the archive's incident
# record: the governor's no-hysteresis dither hung the service processor with card power pinned just above
# the 75 W catastrophic threshold), and never set to 0 or near it (TDP 0 latched aifoundry3's governor). The
# threshold's ceiling is the 70 C the owner's brief allows; its floor keeps the thermal loop's exit reachable.
GOV_TDP_MIN_W, GOV_TDP_MAX_W = 30, 65
GOV_THR_MIN_C, GOV_THR_MAX_C = 60, 70
GOV_SET_CMD = {"tdp_w": ("DM_CMD_SET_MODULE_STATIC_TDP_LEVEL", "-l"),
               "threshold_c": ("DM_CMD_SET_MODULE_TEMPERATURE_THRESHOLDS", "-e")}
HOLD_S = 10
HOLD_GRACE_S = 5
ABS_STOP_CEILING_C = 90.0
SAMPLER_TERM_WAIT_S = 30
TYPES = ("fp32", "fp16", "int8")
FP32_VALUES = {"zeros", "ones", "twos", "pi", "checker", "ternary", "onebit", "uniform", "randn", "sparse75",
               "sparse50", "signs", "pow2", "mant", "a_randn_b_ones", "a_ones_b_randn"}
OTHER_VALUES = {"zeros", "ones", "uniform", "randn"}


def iso_ms(ms):
    """A host-clock millisecond as an ISO 8601 local timestamp, for the change record's log."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ms / 1000.0)) + f".{int(ms) % 1000:03d}" \
        + time.strftime("%z", time.localtime(ms / 1000.0))


def now_ms():
    return int(time.time() * 1000)


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
    u = os.environ.get("USER") or os.environ.get("LOGNAME")
    if not u:
        try:
            import pwd
            u = pwd.getpwuid(os.getuid()).pw_name
        except Exception:
            u = ""
    return u


def run_out(cmd, timeout=15, env=None, cwd=None):
    """A bounded helper command. Nothing waits for a person."""
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL,
                           close_fds=True, env=env, cwd=cwd)
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as e:
        return -1, b"", str(e).encode()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_tel(line):
    """One sampler line -> (t_ms, die mean, die high, board W, minion MHz), or None."""
    try:
        d = json.loads(line)
    except ValueError:
        return None
    try:
        ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
        return (int(d["t_ms"]), num(ms[0]), num(ms[2]) if len(ms) > 2 else None, num(d.get("board_w")),
                num(d.get("mhz", {}).get("minion")))
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


class EndSession(Exception):
    def __init__(self, reason, code):
        super().__init__(reason)
        self.reason, self.code = reason, code


class Refuse(Exception):
    pass


# ---------------------------------------------------------------------------------------------- protocol
class Run:
    def __init__(self, block, idx, rep, cfg, bdefaults):
        g = dict(bdefaults)
        g.update(cfg)
        self.block, self.idx, self.rep = block, idx, rep
        self.type = g.get("type", "fp32")
        self.values = g["values"]
        self.mask = int(str(g.get("mask", "0xffffffff")), 16)
        self.per_shire = int(g.get("per_shire", 32))
        self.minions = bin(self.mask).count("1") * self.per_shire
        self.start = dict(g.get("start") or {"mode": "cool", "max_c": 55, "max_wait_s": 300})
        la = g.get("launch") or {}
        self.seconds = float(la.get("seconds", 6))
        self.budget = float(la.get("budget", self.seconds + 1.5))
        self.processes = int(la.get("processes", 1))
        self.tail_s = float(g.get("tail_s", 4))
        self.seed = int(g.get("seed", 1))
        self.label = g.get("label") or f"{self.type}-{self.values}-{self.minions}"
        self.name = f"{block}-{idx:02d}-{self.label}-r{rep}"
        gov = dict(g.get("governor") or {})
        self.gov_tdp = int(gov.get("tdp_w", 65))
        self.gov_thr = int(gov.get("threshold_c", 65))

    def check(self):
        bad = []
        if self.type not in TYPES:
            bad.append(f"{self.name}: type {self.type}")
        ok = FP32_VALUES if self.type == "fp32" else OTHER_VALUES
        if self.values not in ok:
            bad.append(f"{self.name}: values {self.values} not allowed for {self.type}")
        if not (0 < self.seconds < self.budget < HOLD_S):
            bad.append(f"{self.name}: need 0 < seconds < budget < {HOLD_S} (got {self.seconds}, {self.budget})")
        if not (1 <= self.per_shire <= 32) or self.mask == 0 or self.mask >> 32:
            bad.append(f"{self.name}: mask/per_shire")
        m = self.start.get("mode")
        if m not in ("cool", "edge", "hot"):
            bad.append(f"{self.name}: start.mode {m}")
        if m == "hot" and not (num(self.start.get("hot_c")) and 60 <= num(self.start["hot_c"]) <= 75):
            bad.append(f"{self.name}: a hot start needs hot_c between 60 and 75")
        if m == "edge" and not (num(self.start.get("heat_to_c")) and num(self.start.get("edge_c"))):
            bad.append(f"{self.name}: an edge start needs heat_to_c and edge_c")
        if m == "edge" and num(self.start.get("heat_to_c")) and num(self.start["heat_to_c"]) > 80:
            bad.append(f"{self.name}: heat_to_c above 80")
        # E69's governor bounds (the owner's brief for Q129, and the archive's own incident record)
        if not (GOV_TDP_MIN_W <= self.gov_tdp <= GOV_TDP_MAX_W):
            bad.append(f"{self.name}: governor.tdp_w {self.gov_tdp} outside {GOV_TDP_MIN_W}-{GOV_TDP_MAX_W} W")
        if not (GOV_THR_MIN_C <= self.gov_thr <= GOV_THR_MAX_C):
            bad.append(f"{self.name}: governor.threshold_c {self.gov_thr} outside "
                       f"{GOV_THR_MIN_C}-{GOV_THR_MAX_C} C")
        return bad

    def plan_s(self):
        return self.processes * (self.seconds + 1.2) + self.tail_s + 25


def load_protocol(path, only=None):
    """The runs in session order. Every block is planned (the shuffles use one seeded generator over all
    blocks), so --only runs exactly the runs a full session would have run in those blocks. A block with
    "default": false (the smoke) runs only when --only names it."""
    raw = json.load(open(path))
    runs, bad = [], []
    rng = random.Random(raw.get("order_seed", 64))
    safety = raw.get("safety", {})
    if num(safety.get("abs_stop_c", 85)) > ABS_STOP_CEILING_C:
        bad.append("safety.abs_stop_c above the lab's 90 C rule")
    for b in raw["blocks"]:
        cfgs = b["runs"]
        defaults = {k: v for k, v in b.items()
                    if k not in ("runs", "name", "title", "passes", "shuffle", "default", "note")}
        keep = (b["name"] in only) if only else b.get("default", True)
        for rep in range(1, int(b.get("passes", 1)) + 1):
            order = list(range(len(cfgs)))
            if b.get("shuffle"):
                rng.shuffle(order)
            for i in order:
                r = Run(b["name"], i, rep, cfgs[i], defaults)
                bad += r.check()
                if keep:
                    runs.append(r)
    return raw, runs, bad


# ---------------------------------------------------------------------------------------------- dry model
class DryCard:
    """A toy card for --dry: one thermal node per die, the board's power by clock and data, and the 0.20.0
    governor as the lab reads it (thermal first at a mean > 65; a power-down event when the instantaneous
    reading passes the TDP, stepping until the 1 s running average is under 1.05 x TDP, sticky until the
    master minion goes idle; a power-up climbing while the average is under the TDP)."""
    PTS = [(600, 0.517), (700, 0.568), (800, 0.618)]
    DYN600 = {"zeros": 2.0, "sparse75": 4.75, "ones": 10.44, "pi": 10.67, "signs": 15.1, "pow2": 16.3,
              "a_randn_b_ones": 18.0, "a_ones_b_randn": 21.6, "mant": 24.1, "uniform": 25.0, "randn": 27.1,
              "ternary": 9.4, "sparse50": 9.84, "checker": 4.65, "twos": 10.4, "onebit": 9.0}

    def __init__(self):
        self.die = 52.0
        self.avg = 23.0
        self.pt = 0
        self.busy = False
        self.dyn600 = 0.0
        self.state = "idle"
        self.events = []
        self.lock = threading.Lock()

    def power(self):
        f, v = self.PTS[self.pt]
        idle = 22.7 + 0.4 * (self.die - 49) + (5.8 * (v / 0.517) ** 2 * f / 600 - 5.8 if self.busy else 0)
        dyn = self.dyn600 * (v / 0.517) ** 2 * f / 600 if self.busy else 0
        return idle + dyn

    def step(self, dt):
        with self.lock:
            p = self.power()
            self.die += dt * ((51 + 0.6 * (p - 23)) - self.die) / 6.0
            self.avg += dt * (p - self.avg) / 1.05
            d = int(self.die)
            if d > 65:
                if self.pt > 0:
                    self.pt -= 1
                    self.events.append(("thermal_down", d))
                self.state = "thermal"
                return
            if self.state == "thermal":
                self.state = "idle"
                self.pt = 0
                self.events.append(("thermal_idle", d))
                return
            if not self.busy:
                if self.state != "idle":
                    self.events.append(("power_idle", int(p * 1000)))
                self.state, self.pt = "idle", 0
                return
            if p > 65 and self.state in ("idle", "up"):
                self.state = "down"
                self.events.append(("power_down", int(p * 1000)))
                while self.pt > 0:
                    self.pt -= 1
                    if self.avg < 68.25:
                        break
            elif p < 65 and self.state == "idle":
                self.state = "up"
                self.events.append(("power_up", int(p * 1000)))
                while self.pt < 2 and self.avg <= 65:
                    self.pt += 1

    def set_busy(self, busy, values=None, frac=1.0):
        with self.lock:
            self.busy = busy
            if busy:
                self.dyn600 = self.DYN600.get(values, 20.0) * frac

    def sample(self):
        with self.lock:
            p = self.power()
            f = self.PTS[self.pt][0]
            d = int(self.die)
            return {"t_ms": now_ms(), "took_ms": 22, "board_w": round(p + random.gauss(0, 0.15), 2),
                    "temp_c": {"minshire": [d, d - 3, d + 3]}, "mhz": {"minion": f}}


class DrySampler(threading.Thread):
    def __init__(self, path, card, every_ms):
        super().__init__(daemon=True)
        self.path, self.card, self.every = path, card, every_ms / 1000.0
        self.stop_flag = threading.Event()
        self.pid = -1

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
    """Tails the current telemetry file; keeps the latest reading; trips the stop-file on the safety caps."""

    def __init__(self, sess):
        super().__init__(daemon=True)
        self.s = sess
        self.path = None
        self.pos = 0
        self.last = None            # (t_ms, die, high, board, mhz)
        self.last_host_ms = 0
        self.over = 0
        self.trip = None
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()

    def follow(self, path):
        with self.lock:
            self.path, self.pos, self.over = path, 0, 0
            self.last, self.last_host_ms = None, 0

    def snapshot(self):
        with self.lock:
            return self.last, self.last_host_ms

    def run(self):
        sf = self.s.proto.get("safety", {})
        stop_c = num(sf.get("abs_stop_c", 85))
        cap_w = num(sf.get("board_cap_w", 97))
        need = int(sf.get("cap_consecutive", 3))
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
                            with self.lock:
                                self.last, self.last_host_ms = t, now_ms()
                            _, die, high, w, _ = t
                            hot = [x for x in (die, high) if x is not None and x >= stop_c]
                            if hot and not self.trip:
                                self.fire(f"die {max(hot):.0f} C >= {stop_c:g} C")
                            if w is not None and w > cap_w:
                                self.over += 1
                                if self.over >= need and not self.trip:
                                    self.fire(f"board {w:.1f} W > {cap_w:g} W on {need} samples")
                            else:
                                self.over = 0
                except OSError:
                    pass
            time.sleep(0.05)

    def fire(self, why):
        self.trip = why
        self.s.touch(self.s.stop_file)
        self.s.mark("safety_trip", why)


# ---------------------------------------------------------------------------------------------- session
class Session:
    def __init__(self, a, proto, runs):
        self.a, self.proto, self.runs = a, proto, runs
        self.dry = a.dry
        self.root = os.path.abspath(a.root)
        self.rundir = os.path.abspath(a.out)
        self.stop_file = os.path.join(self.rundir, "STOP")
        self.lock_fd = None
        self.sampler = None
        self.heater_pids = set()
        self.ns_baseline = None
        self.orig_cfg = None            # the card's own TDP and threshold, read fresh before the first set
        self.dry_cfg = {"tdp_w": 65, "temp_threshold_c": 65}
        self.gov_restore = None         # the restore record, written in the session's finally
        self.card = DryCard() if self.dry else None
        tools = proto.get("tools", {})
        self.heater = os.path.join(self.root, tools.get("heater", "build/sparsity_t2/host/sparsity_host"))
        self.kernel = os.path.join(self.root, tools.get("kernel", "build/sparsity_t2/kernel/sparsity.elf"))
        self.ettelem = os.path.join(self.root, tools.get("ettelem", "build/ettelem-hpl/ettelem"))
        self.every_ms = int(proto.get("sampler", {}).get("every_ms", 100))
        self.max_card_s = 60 * float(a.max_card_min or proto.get("caps", {}).get("max_card_min", 150))
        self.t0 = None
        self.sampler_t0 = 0
        self.watcher = Watcher(self)
        os.makedirs(self.rundir, exist_ok=True)
        for d in ("tel", "sp", "logs"):
            os.makedirs(os.path.join(self.rundir, d), exist_ok=True)

    # -- records
    def jsonl(self, name, rec):
        with open(os.path.join(self.rundir, name), "a") as f:
            f.write(json.dumps(rec) + "\n")

    def say(self, msg):
        line = time.strftime("%H:%M:%S ") + msg
        print(line, flush=True)
        with open(os.path.join(self.rundir, "run.log"), "a") as f:
            f.write(line + "\n")

    def mark(self, kind, detail="", **kw):
        self.jsonl("marks.jsonl", dict(t_ms=now_ms(), kind=kind, detail=detail, **kw))

    def touch(self, path):
        try:
            with open(path, "a"):
                os.utime(path, None)
        except OSError:
            pass

    # -- preflight
    def preflight(self):
        pf = []
        host = socket.gethostname().split(".")[0]
        if not self.dry:
            if host != CARD_HOST:
                pf.append(f"hostname {host!r} is not {CARD_HOST!r}")
            if not shutil.which("timeout"):
                pf.append("no `timeout` on PATH")
            for label, p in (("heater", self.heater), ("kernel", self.kernel), ("ettelem", self.ettelem)):
                if not os.path.isfile(p):
                    pf.append(f"missing {label} {p}")
            if os.sep + "build" + os.sep + "sparsity" + os.sep in self.heater:
                pf.append("the heater must be aifoundry2's build/sparsity_t2 (lib.sh:35-43)")
            if os.path.dirname(os.path.dirname(self.heater)) != os.path.dirname(os.path.dirname(self.kernel)):
                pf.append("heater and kernel come from different builds")
            if os.path.isfile(self.heater):
                blob = open(self.heater, "rb").read()
                for flag in (b"--stop-file", b"--kernel", b"--budget"):
                    if flag not in blob:
                        pf.append(f"heater has no {flag.decode()}")
            if os.path.isfile(self.ettelem):
                blob = open(self.ettelem, "rb").read()
                for word in (b"residency", b"sptrace", b"config"):
                    if word not in blob:
                        pf.append(f"ettelem {self.ettelem} has no {word.decode()} (build ettelem-dv2)")
            if not os.path.exists(LOCK_PATH):
                pf.append(f"no card lock {LOCK_PATH}")
        if os.path.exists(os.path.join(self.rundir, "session.json")):
            pf.append(f"{self.rundir} already holds a session")
        if pf:
            raise Refuse("; ".join(pf))

    # -- etiquette
    def take_lock(self):
        if self.dry:
            raise RuntimeError("take_lock in dry mode")
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
        rc, out, _ = run_out(["who"])
        users = sorted({ln.split()[0] for ln in out.decode(errors="replace").splitlines() if ln.split()})
        others = [u for u in users if u != me_user()]
        if others:
            hits.append("users:" + ",".join(others))
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
                hits.append(f"proc:{u}:{pid}:{comm}")
            elif u == os.getuid() and DEV_COMM.search(comm):
                hits.append(f"ours:{pid}:{comm}")
        n = self.modcount()
        if n is not None and self.ns_baseline is not None and n > self.ns_baseline:
            hits.append(f"et_soc1_use:{n}>{self.ns_baseline}")
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
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        for attempt in range(1, 7):
            since = os.path.getsize(path) if os.path.exists(path) else 0
            out = open(path, "ab", buffering=0)
            try:
                self.sampler = subprocess.Popen(
                    [self.ettelem, "sample", "--seconds", str(int(seconds)), "--every-ms", str(self.every_ms)],
                    stdout=out, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env, close_fds=True,
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
            if attempt == 2:
                self.drain()
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
                self.mark("error", f"sampler {s.pid} ignored SIGTERM: SIGKILL and drain")
                s.kill()
                try:
                    s.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
                self.drain()
        self.mark("sampler_stop", f"pid {s.pid}, rc {s.returncode}")

    def drain(self):
        if self.dry:
            return
        self.say("draining the management queue")
        run_out(["timeout", "20", DEVMNGT, "-m", "DM_CMD_GET_MODULE_POWER", "-n", "0", "-u", "5000"],
                timeout=25, env=dict(os.environ, LD_LIBRARY_PATH=ET_LIB))

    def reading(self, max_age_s=3.0):
        """(die mean, die high, board W, MHz) from the watcher, or None when stale."""
        last, host_ms = self.watcher.snapshot()
        if last is None or now_ms() - host_ms > max_age_s * 1000:
            return None
        return last[1], last[2], last[3], last[4]

    # -- the management queries, sampler stopped
    def queries(self, tag):
        out = {"tag": tag, "t_ms": now_ms()}
        if self.dry:
            with self.card.lock:
                out["sp_events"] = list(self.card.events)
                self.card.events.clear()
            out["config"] = {"tdp_w": 65, "temp_threshold_c": 65}
            return out
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        dump = os.path.join(self.rundir, "sp", f"{tag}.bin")
        rc, so, se = run_out(["timeout", str(HOLD_S), self.ettelem, "sptrace", dump], timeout=HOLD_S + 5, env=env,
                             cwd=self.root)
        out["sptrace_rc"] = rc
        out["sptrace_sha256"] = sha256_file(dump) if os.path.exists(dump) else None
        rc, so, se = run_out(["timeout", str(HOLD_S), self.ettelem, "residency", "2", "3", "4", "5", "6"],
                             timeout=HOLD_S + 5, env=env, cwd=self.root)
        out["residency_rc"] = rc
        out["residency"] = [json.loads(l) for l in so.decode(errors="replace").splitlines() if l.startswith("{")]
        rc, so, se = run_out(["timeout", str(HOLD_S), self.ettelem, "config"], timeout=HOLD_S + 5, env=env,
                             cwd=self.root)
        out["config_rc"] = rc
        try:
            out["config"] = json.loads(so.decode(errors="replace").strip().splitlines()[-1])
        except (ValueError, IndexError):
            out["config"] = None
        return out

    # -- device processes
    def spawn_kernel(self, r, values=None, seconds=None, budget=None, mask=None, per_shire=None, typ=None):
        cmd = ["timeout", str(HOLD_S), self.heater, "--test", "fma", "--type", typ or r.type, "--pattern", "none",
               "--values", values or r.values, "--shires", f"0x{(mask or r.mask):08x}",
               "--per-shire", str(per_shire or r.per_shire), "--seconds", f"{seconds or r.seconds:g}",
               "--budget", f"{budget or r.budget:g}", "--seed", str(r.seed), "--kernel", self.kernel,
               "--stop-file", self.stop_file]
        t0 = now_ms()
        if self.dry:
            frac = (per_shire or r.per_shire) * bin(mask or r.mask).count("1") / 1024.0
            self.card.set_busy(True, values or r.values, frac)
            end = time.time() + (seconds or r.seconds) + 0.4
            lines = []
            while time.time() < end and not os.path.exists(self.stop_file):
                a0 = now_ms()
                time.sleep(0.5)
                f = self.card.PTS[self.card.pt][0]
                cyc = int(f * 1e6 * 0.5)
                lines.append(json.dumps({"test": "fma", "type": typ or r.type, "values": values or r.values,
                                         "minions": r.minions, "iters": cyc // 546, "cycles_max": cyc,
                                         "cycles_per_op": 546.0, "wall_s": 0.5, "t_start_ms": a0,
                                         "t_end_ms": now_ms(), "ghz": f / 1000.0, "ok": True,
                                         "result": "unchecked"}))
            self.card.set_busy(False)
            return cmd, 0, "\n".join("SPARSITY " + l for l in lines), "", t0, now_ms()
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                             text=True, env=env, close_fds=True, cwd=self.root, start_new_session=True)
        self.heater_pids.add(p.pid)
        try:
            out, err = p.communicate(timeout=HOLD_S + HOLD_GRACE_S)
        except subprocess.TimeoutExpired:
            self.touch(self.stop_file)
            self.mark("error", f"kernel pid {p.pid} outlived timeout {HOLD_S} s: left alone")
            raise EndSession(f"error:kernel_overran_hold10:{p.pid}", EXIT_ERR)
        finally:
            self.heater_pids.discard(p.pid)
        return cmd, p.returncode, out, err, t0, now_ms()

    def guard(self, where):
        if self.watcher.trip:
            raise EndSession(f"safety:{self.watcher.trip}", EXIT_SAFETY)
        if os.path.exists(self.stop_file):
            raise EndSession("stop_file", EXIT_SAFETY)
        if self.t0 and (time.time() - self.t0) > self.max_card_s:
            raise EndSession("done:max_card_min", EXIT_OK)
        if self.sampler is not None and self.sampler.poll() is not None:
            raise EndSession(f"error:sampler_exited:{where}", EXIT_ERR)
        if self.sampler is not None and self.reading(5.0) is None and now_ms() - self.sampler_t0 > 8000:
            self.touch(self.stop_file)
            raise EndSession(f"error:telemetry_stale:{where}", EXIT_ERR)

    def wait_until(self, cond, max_s, where, step=0.2):
        """Poll cond(reading) until true or max_s; the guard and the other-user check keep running."""
        t0 = time.time()
        last_check = 0
        while time.time() - t0 < max_s:
            self.guard(where)
            if time.time() - last_check > 10:
                self.check_others(where)
                last_check = time.time()
            rd = self.reading()
            if rd is not None and rd[0] is not None and cond(rd):
                return True, round(time.time() - t0, 1), rd
            time.sleep(step)
        return False, round(time.time() - t0, 1), self.reading()

    # -- one run
    def gate(self, r):
        st = r.start
        ok, _, _ = self.wait_until(lambda x: True, 10, f"{r.name} first reading")
        if not ok:
            raise EndSession(f"error:no_reading:{r.name}", EXIT_ERR)
        if st["mode"] == "cool":
            ok, held, rd = self.wait_until(lambda x: x[0] <= num(st["max_c"]), num(st.get("max_wait_s", 300)),
                                           f"{r.name} cool gate")
            return {"mode": "cool", "max_c": st["max_c"], "reached": ok, "held_s": held, "reading": rd}
        if st["mode"] == "hot":
            # A2: heat with back-to-back full-card random launches of heat_s seconds until the die reads hot_c or
            # more (the governor is then in its thermal loop), then launch the work at once, with no edge to wait for
            hot, heats, t0 = num(st["hot_c"]), 0, time.time()
            hs = num(st.get("heat_s", 8)) or 8.0
            rd = self.reading()
            while rd is not None and rd[0] is not None and rd[0] < hot and heats < int(st.get("max_heats", 8)):
                self.guard(f"{r.name} heat")
                self.check_others(f"{r.name} heat")
                cmd, rc, out, err, a, b = self.spawn_kernel(r, values=st.get("heater_values", "randn"), seconds=hs,
                                                           budget=hs + 1.5, mask=0xffffffff, per_shire=32, typ="fp32")
                heats += 1
                self.jsonl("launches.jsonl", {"run": r.name, "role": "heat", "cmd": cmd, "rc": rc, "t_start_ms": a,
                                              "t_end_ms": b, "stderr_tail": err[-300:] if err else ""})
                if rc != 0:
                    raise EndSession(f"error:heater_rc_{rc}", EXIT_ERR)
                rd = self.reading()
            return {"mode": "hot", "hot_c": hot, "reached": bool(rd and rd[0] is not None and rd[0] >= hot),
                    "heats": heats, "heat_s": round(time.time() - t0, 1), "reading": rd}
        heat_to, edge = num(st["heat_to_c"]), num(st["edge_c"])
        heats = 0
        t0 = time.time()
        rd = self.reading()
        hv = st.get("heater_values", "randn")
        while rd is not None and rd[0] is not None and rd[0] < heat_to and heats < int(st.get("max_heats", 12)):
            self.guard(f"{r.name} heat")
            self.check_others(f"{r.name} heat")
            cmd, rc, out, err, a, b = self.spawn_kernel(r, values=hv, seconds=3.0, budget=4.5, mask=0xffffffff,
                                                       per_shire=32, typ="fp32")
            heats += 1
            self.jsonl("launches.jsonl", {"run": r.name, "role": "heat", "cmd": cmd, "rc": rc, "t_start_ms": a,
                                          "t_end_ms": b, "stderr_tail": err[-300:] if err else ""})
            if rc != 0:
                raise EndSession(f"error:heater_rc_{rc}", EXIT_ERR)
            time.sleep(0.3)
            rd = self.reading()
        heated = {"heats": heats, "heat_s": round(time.time() - t0, 1), "peak_reading": rd}
        ok, held, rd2 = self.wait_until(lambda x: x[0] <= edge, num(st.get("max_wait_s", 240)),
                                        f"{r.name} edge {edge:g}")
        return {"mode": "edge", "heat_to_c": heat_to, "edge_c": edge, "reached": ok, "held_s": held,
                "reading": rd2, **heated}

    # -- the governor: one set, one read-back, one line in gov.jsonl, every time
    def read_config(self):
        """(tdp_w, threshold_c, power_state, minion_mhz) straight from the firmware, or None."""
        if self.dry:
            return dict(self.dry_cfg)
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        rc, so, _ = run_out(["timeout", str(HOLD_S), self.ettelem, "config"], timeout=HOLD_S + 5, env=env,
                            cwd=self.root)
        if rc != 0:
            return None
        try:
            return json.loads(so.decode(errors="replace").strip().splitlines()[-1])
        except (ValueError, IndexError):
            return None

    def set_governor(self, tdp_w, threshold_c, why):
        """Send only the fields that differ from what the firmware reports, then read back and prove it took.

        Refuses anything outside E69's bounds even if a protocol slipped past the planner, and refuses to run
        at all if the read-back disagrees with what was asked: a governor whose state we cannot read is a
        governor we must not leave moved."""
        for name, val, lo, hi in (("tdp_w", tdp_w, GOV_TDP_MIN_W, GOV_TDP_MAX_W),
                                  ("threshold_c", threshold_c, GOV_THR_MIN_C, GOV_THR_MAX_C)):
            if not (lo <= int(val) <= hi):
                raise EndSession(f"error:governor_out_of_bounds:{name}={val}", EXIT_ERR)
        before = self.read_config()
        if before is None:
            raise EndSession("error:governor_config_unreadable", EXIT_ERR)
        want = {"tdp_w": int(tdp_w), "temp_threshold_c": int(threshold_c)}
        sent = []
        for key, wkey in (("tdp_w", "tdp_w"), ("threshold_c", "temp_threshold_c")):
            target = want[wkey]
            if before.get(wkey) == target:
                continue
            cmd, flag = GOV_SET_CMD[key]
            argv = ["timeout", "20", DEVMNGT, "-m", cmd, "-n", "0", flag, str(target), "-u", "5000"]
            t0 = now_ms()
            rc, so, se = run_out(argv, timeout=25, env=dict(os.environ, LD_LIBRARY_PATH=ET_LIB))
            sent.append({"key": key, "to": target, "cmd": argv, "rc": rc, "t_ms": t0,
                         "t_iso": iso_ms(t0), "stdout_tail": so.decode(errors="replace")[-600:],
                         "stderr_tail": se.decode(errors="replace")[-400:] if se else ""})
            if rc != 0:
                self.jsonl("gov.jsonl", {"event": "set_failed", "why": why, "before": before, "sent": sent})
                raise EndSession(f"error:governor_set_failed:{key}:{target}:rc{rc}", EXIT_ERR)
        after = self.read_config()
        rec = {"event": "set", "why": why, "asked": want, "before": before, "after": after, "sent": sent,
               "t_ms": now_ms(), "t_iso": iso_ms(now_ms())}
        self.jsonl("gov.jsonl", rec)
        if after is None or after.get("tdp_w") != want["tdp_w"] \
                or after.get("temp_threshold_c") != want["temp_threshold_c"]:
            raise EndSession(f"error:governor_readback_mismatch:asked{want}:got{after}", EXIT_ERR)
        if sent:
            self.say(f"    governor: TDP {before.get('tdp_w')}->{after['tdp_w']} W, threshold "
                     f"{before.get('temp_threshold_c')}->{after['temp_threshold_c']} C, read back")
        return rec

    def restore_governor(self):
        """Put the originals back and read them back. Never raises: it runs in the session's `finally`."""
        if self.orig_cfg is None:
            self.mark("restore_skipped", "no original configuration was read")
            return {"event": "restore", "ok": False, "why": "no original configuration was read"}
        tdp = int(self.orig_cfg.get("tdp_w"))
        thr = int(self.orig_cfg.get("temp_threshold_c"))
        sent, err = [], None
        for key, target in (("tdp_w", tdp), ("threshold_c", thr)):
            cmd, flag = GOV_SET_CMD[key]
            argv = ["timeout", "20", DEVMNGT, "-m", cmd, "-n", "0", flag, str(target), "-u", "5000"]
            try:
                rc, so, se = run_out(argv, timeout=25, env=dict(os.environ, LD_LIBRARY_PATH=ET_LIB))
            except Exception as e:  # noqa: BLE001
                rc, so, se, err = -1, b"", str(e).encode(), f"{key}: {e}"
            sent.append({"key": key, "to": target, "rc": rc, "t_iso": iso_ms(now_ms()),
                         "stderr_tail": se.decode(errors="replace")[-400:] if se else ""})
            if rc != 0:
                err = err or f"{key}: rc {rc}"
        after = self.read_config()
        ok = bool(after) and after.get("tdp_w") == tdp and after.get("temp_threshold_c") == thr
        rec = {"event": "restore", "ok": ok, "original": self.orig_cfg, "after": after, "sent": sent,
               "error": err, "t_iso": iso_ms(now_ms())}
        self.jsonl("gov.jsonl", rec)
        self.say(f"    RESTORE {'ok' if ok else 'FAILED'}: TDP {after.get('tdp_w') if after else '?'} W, "
                 f"threshold {after.get('temp_threshold_c') if after else '?'} C "
                 f"(originals {tdp} W / {thr} C)")
        return rec

    def run_one(self, r, k, n):
        tag = r.name
        tel = os.path.join(self.rundir, "tel", f"{tag}.jsonl")
        self.say(f"[{k}/{n}] {tag}: {r.processes} x {r.seconds:g} s, {r.minions} minions, start {r.start}, "
                 f"governor TDP {r.gov_tdp} W / threshold {r.gov_thr} C")
        self.check_others(tag)
        if not self.dry:
            self.set_governor(r.gov_tdp, r.gov_thr, f"run {tag}")
        else:
            self.dry_cfg = {"tdp_w": r.gov_tdp, "temp_threshold_c": r.gov_thr}
        if not self.start_sampler(tel, r.plan_s() + 900):
            raise EndSession("error:sampler_would_not_start", EXIT_ERR)
        self.sampler_t0 = now_ms()
        if not self.dry:
            # A0: the et_soc1 use count's baseline is taken with only our sampler open, as E63's runner does
            # (run_hlc.py take_ns_baseline); taken before it, our own sampler read as another user (exit 3).
            self.ns_baseline = self.modcount()
            self.mark("use_count_baseline", str(self.ns_baseline))
        time.sleep(1.0)
        g = self.gate(r)
        self.say(f"    gate: {g}")
        launches = []
        t_first = now_ms()
        for p in range(r.processes):
            self.guard(tag)
            self.check_others(tag)
            cmd, rc, out, err, a, b = self.spawn_kernel(r)
            recs = []
            for ln in (out or "").splitlines():
                if ln.startswith("SPARSITY "):
                    try:
                        recs.append(json.loads(ln[9:]))
                    except ValueError:
                        pass
            launches.append({"proc": p, "rc": rc, "t_start_ms": a, "t_end_ms": b, "n_launch": len(recs)})
            self.jsonl("launches.jsonl", {"run": tag, "role": "work", "proc": p, "cmd": cmd, "rc": rc,
                                          "t_start_ms": a, "t_end_ms": b, "sparsity": recs,
                                          "stderr_tail": err[-400:] if err else ""})
            if rc != 0:
                self.say(f"    process {p} rc {rc}: {err[-200:] if err else ''}")
                if sum(1 for x in launches if x["rc"] != 0) >= 2:
                    raise EndSession(f"error:kernel_failed:{tag}", EXIT_ERR)
        t_last = now_ms()
        tail_end = time.time() + r.tail_s
        while time.time() < tail_end:
            self.guard(tag)
            time.sleep(0.2)
        self.stop_sampler()
        q = self.queries(tag)
        rec = {"run": tag, "block": r.block, "idx": r.idx, "rep": r.rep, "label": r.label, "type": r.type,
               "values": r.values, "mask": f"0x{r.mask:08x}", "per_shire": r.per_shire, "minions": r.minions,
               "seconds": r.seconds, "processes": r.processes, "gate": g, "t_first_ms": t_first,
               "t_last_ms": t_last, "launches": launches, "queries": q, "tel": os.path.relpath(tel, self.rundir)}
        self.jsonl("runs.jsonl", rec)
        cfg = q.get("config") or {}
        if not self.dry and cfg and (cfg.get("tdp_w") != r.gov_tdp
                                     or cfg.get("temp_threshold_c") != r.gov_thr):
            self.mark("config_drifted", json.dumps(cfg))
            raise EndSession(f"error:config_drifted:asked{r.gov_tdp}W/{r.gov_thr}C:got{cfg}", EXIT_ERR)
        return rec

    # -- the session
    def run(self):
        self.preflight()
        sess = {"experiment": self.proto.get("experiment", "E69"),
                "governor_grid": sorted({(r.gov_tdp, r.gov_thr) for r in self.runs}),
                "governor_bounds": {"tdp_w": [GOV_TDP_MIN_W, GOV_TDP_MAX_W],
                                    "threshold_c": [GOV_THR_MIN_C, GOV_THR_MAX_C]}, "host": socket.gethostname(),
                "dry": self.dry, "user": me_user(), "t_start_ms": now_ms(), "protocol": self.proto,
                "runs_planned": [r.name for r in self.runs],
                "sha256": {k: sha256_file(p) for k, p in (("heater", self.heater), ("kernel", self.kernel),
                                                         ("ettelem", self.ettelem),
                                                         ("runner", os.path.abspath(__file__)))},
                "argv": sys.argv}
        rc, out, _ = run_out(["git", "rev-parse", "HEAD"], cwd=self.root)
        sess["git_head"] = out.decode().strip()
        rc, out, _ = run_out(["git", "status", "--porcelain", "--", "tools/claims-v3/knob",
                              "tools/claims-v3/hpl"], cwd=self.root)
        sess["git_dirty_tools"] = out.decode().strip()
        if not self.dry:
            rc, out, _ = run_out(["et-lab-manifest"], timeout=60)
            open(os.path.join(self.rundir, "manifest.txt"), "wb").write(out)
        json.dump(sess, open(os.path.join(self.rundir, "session.json"), "w"), indent=1)
        self.watcher.start()
        code, reason = EXIT_OK, "done"
        try:
            if not self.dry:
                self.check_others("start")
                self.take_lock()
                self.ns_baseline = self.modcount()
                self.orig_cfg = self.read_config()
                self.jsonl("gov.jsonl", {"event": "original", "config": self.orig_cfg,
                                         "t_iso": iso_ms(now_ms())})
                if self.orig_cfg is None:
                    raise EndSession("error:original_config_unreadable", EXIT_ERR)
                self.say(f"original governor: TDP {self.orig_cfg.get('tdp_w')} W, threshold "
                         f"{self.orig_cfg.get('temp_threshold_c')} C, power state "
                         f"{self.orig_cfg.get('power_state_name')}")
            self.t0 = time.time()
            q0 = self.queries("start")
            self.jsonl("queries.jsonl", q0)
            for k, r in enumerate(self.runs, 1):
                self.run_one(r, k, len(self.runs))
        except EndSession as e:
            code, reason = e.code, e.reason
            self.say(f"session ends: {reason}")
        except Exception as e:  # noqa: BLE001 -- record anything unexpected, then clean up
            code, reason = EXIT_ERR, f"error:{type(e).__name__}:{e}"
            self.say(f"session error: {reason}")
        finally:
            self.touch(self.stop_file) if code not in (EXIT_OK,) else None
            self.stop_sampler()
            if not self.dry and self.orig_cfg is not None:
                try:
                    self.gov_restore = self.restore_governor()
                except Exception as e:  # noqa: BLE001 -- a failed restore must still be recorded, not raised
                    self.gov_restore = {"event": "restore", "ok": False, "error": f"{type(e).__name__}: {e}"}
                    self.mark("error", f"restore: {e}")
                if not self.gov_restore.get("ok"):
                    code, reason = EXIT_ERR, f"RESTORE FAILED: {self.gov_restore}"
                    self.say("*** THE GOVERNOR WAS NOT RESTORED. The claim stays. Do not reset the card. "
                             "Alert the owner at once.")
            if code == EXIT_OK:
                try:
                    self.jsonl("queries.jsonl", self.queries("end"))
                except Exception as e:  # noqa: BLE001
                    self.mark("error", f"end queries: {e}")
            self.release_lock()
            self.watcher.stop_flag.set()
            end = {"t_end_ms": now_ms(), "exit": code, "reason": reason,
                   "card_min": round((time.time() - (self.t0 or time.time())) / 60, 1),
                   "governor_original": self.orig_cfg, "governor_restore": self.gov_restore}
            json.dump(end, open(os.path.join(self.rundir, "end.json"), "w"))
            self.say(f"exit {code} ({reason})")
        return code


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--max-card-min", type=float)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
    a = ap.parse_args()
    proto, runs, bad = load_protocol(a.protocol, a.only)
    if bad:
        print("protocol refused:\n  " + "\n  ".join(bad), file=sys.stderr)
        return EXIT_REFUSE
    if a.list:
        tot = 0
        for r in runs:
            tot += r.plan_s()
            print(f"{r.name:44s} {r.type} {r.values:15s} {r.minions:5d} {r.processes}x{r.seconds:g}s "
                  f"start {r.start}")
        print(f"{len(runs)} runs, about {tot / 60:.0f} min plus gates")
        return EXIT_OK
    s = Session(a, proto, runs)

    def on_signal(signum, frame):
        s.touch(s.stop_file)
        raise EndSession(f"signal:{signum}", EXIT_SIGNAL)

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    try:
        return s.run()
    except Refuse as e:
        print(f"refused: {e}", file=sys.stderr)
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
