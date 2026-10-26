#!/usr/bin/env python3
"""E62 heat movies: the session runner. Executes a protocol.json on the local card, or dry.

    python3 run_hm.py --protocol <protocol.json> --out <RUNDIR> [--dry] [--only BLOCK ...]
                      [--max-card-min N] [--list] [--cam-url URL] [--no-cam] [--root <tree>]

It drives one session: the card lock, one telemetry sampler, one camera recorder, and a wall-clock
schedule of launch and idle phases.  It writes the RUNDIR that reduce_hm.py reads (INTERFACES.md):
session.json, launches.jsonl, phases.jsonl, blocks.jsonl, tel.jsonl, marks.jsonl, cam/ and
logs/launch-<n>.err, plus run.log, the protocol verbatim as protocol.json, and the session's own
stop-files STOP (the heater's) and CAMSTOP (the recorder's).

Lab etiquette, ported from tools/claims-v3/lib.sh, hp/hplib.sh and dtf/block.sh:

  * the machine's advisory card lock /run/lock/etsoc-shire0.lock is taken with a NON-blocking flock
    (lib.sh:183-186) and held by this process for the whole session.  Held by someone else -> exit 3
    at once.  Nothing here ever waits for a person (lib.sh's wait_free is deliberately not used).
  * the lock's fd is non-inheritable and every child is spawned with close_fds, so no sampler, heater
    or recorder holds it (hplib.sh:86-87 "8>&- 9>&-", and launch.md 2 on dtf's poller inheriting fd 9).
  * the other-user checks run BEFORE the session and BETWEEN EVERY LAUNCH (hp rule O1, hplib.sh:384):
    another logged-in user or another user's device process by executable name (lib.sh:58-80), a
    foreign/our own stale device process (hplib.sh:112-129), and the et_soc1 module use count against
    the baseline taken with only our sampler open (hplib.sh:429-431).  A hit ends the session cleanly:
    exit 3, stop_reason other_user:<who>.
  * every heater process is one `timeout 10 ... < /dev/null` (lib.sh:100 hold10) with an explicit
    --kernel and --stop-file, --seconds/--budget from the protocol (8 / 9.5: --budget defaults to 8.0
    and would silently truncate --seconds 8, launch.md 1), and LD_LIBRARY_PATH=/opt/et/lib (lib.sh:16).
    A dwell is built by chaining launch processes, never by one long --seconds.  A heater is never
    signalled: the stop-file ends its loop at the next ~0.5 s launch boundary (main.cpp:577-580) and
    `timeout 10` is the only hard cap.  Every device child is started in its own session, so a
    Ctrl-C or a group-wide TERM aimed at this runner cannot signal a heater, and cannot kill the
    sampler mid-request (lib.sh:9-10 "a sampler killed mid-request poisons the management queue").
    The runner's own wait on a heater is bounded at hold10 + 5 s: `timeout` without -k waits for
    ever on a child that blocks SIGTERM or sits in the driver, and the main loop must not.  A
    process that outlives hold10 is left alone (never SIGKILLed), reported, and ends the session.
  * the stop-file is also an input: an operator who touches RUNDIR/STOP stops the session (exit 4),
    rather than leaving the heater to be relaunched and truncated in ~0.3 s over and over.
  * one `ettelem sample --every-ms 100 --reset-ms 1000` sampler for the whole session (lib.sh:150-162:
    six start attempts, one management-queue drain after the second).  Nothing else ever opens the
    management node while it runs, so the die reading comes from its output file (run_dtf.py:21-22).
    It is stopped with SIGTERM only and waited for up to 30 s; SIGKILL (then one drain) only if it
    ignores TERM for 30 s (lib.sh:163-176).
  * a safety watcher thread reads the sampler's lines and, on a trip, touches the stop-file and ends
    the session: die (temp_c.minshire mean or peak-high) >= safety.abs_stop_c on one sample, as
    hplib's sticky ABS90; board_w > safety.board_cap_w on safety.cap_consecutive (2) consecutive
    samples, as hplib's CAP_W; optional cap_mean_c / cap_high_c the same way; PMIC >= abs_stop_c + 10
    (run_dtf.py:191).  The lab's 90 C rule stands: a protocol with abs_stop_c > 90 is refused.
    Every field is coerced to a number first, so one malformed sample cannot kill the watcher.
    The watcher also owns the fast path for telemetry it can no longer trust: no sample, or no die
    reading, for safety.sampler_stale_s on the HOST clock (never on the sampler's own t_ms, which
    could be stamped ahead) touches the stop-file at once, as does the watcher's own death.  Heat
    stops within one ~0.5 s launch boundary instead of waiting up to a whole launch for the main
    loop.  The main loop still checks the watcher's liveness independently (thread alive + its own
    heartbeat + sample age), because a dead watcher leaves a state that still looks fresh
    (hplib.sh review note F11); it then restarts a sampler that merely exited (lib.sh:147, up to 3
    times, clearing the stop-file) or ends the session.
  * record_cam.py is started at session start under `nice -n 19` into RUNDIR/cam and stopped at the
    end through its stop-file (dtf/block.sh:110-115, 125).

Schedule.  Phases are scheduled by wall clock.  A launch phase keeps launching back to back while
`now + expected launch wall <= the phase's planned end`; the expected wall is learnt from the launches
already run (an EWMA seeded with heater.expected_launch_s, 8.4 s measured) and only successful
launches teach it.  An idle phase sleeps in short steps, still running the safety and other-user
checks.  Each phase's planned end is its own start + dwell_s (a rolling grid), so every arm of a swap
gets the same dwell even when one launch overruns; both the planned and the realised span are logged.

Protocol (written by the synthesizer; see design/DECISIONS.md).  Unknown keys are kept in the copy in
session.json and otherwise ignored:

    {"experiment": "E62",
     "sets": {"W12": {"mask": "0x03076616", "shires": [1,2,4,...], "per_shire": 32, "harts": 384},
              "IDLE": {"idle": true}},
     "blocks": [{"name": "we12", "title": "West vs East, 12 shires",
                 "phases": [{"set": "W12", "dwell_s": 45}, {"set": "E12", "dwell_s": 45}],
                 "cycles": 6, "warmup_cycles": 1, "order": "alternate",
                 "movie": true, "predicted": {...}, "pass_rule": "..."}],
     "session": {"pre_idle_s": 60, "post_idle_s": 60, "block_gap_s": 0,
                 "block_order": ["we12", ...]},
     "heater": {"bin": "build/sparsity_t2/host/sparsity_host",
                "kernel": "build/sparsity_t2/kernel/sparsity.elf",
                "seconds": 8, "budget": 9.5, "seed": 1, "expected_launch_s": 8.4},
     "safety": {"abs_stop_c": 85, "board_cap_w": 95, "cap_consecutive": 2, "sampler_stale_s": 3},
     "camera": {"url": "http://p3-phone:8080/stream.raw.z"},
     "caps": {"max_card_min": 75, "max_wall_min": 120}}

A phase is idle when it names an idle set, names no set, or sets "idle": true.  `order`: "as-given"
(default), "alternate" (the phase order is reversed on odd cycles, dtf's alternating side order), or
"reverse".  Sanity checks that refuse the protocol (exit 2): a set that does not exist; a mask that
disagrees with its shire list, or harts != popcount(mask) * per_shire; unequal harts among a block's
non-idle phases (a swap must be constant total power, DECISIONS 4) unless the block says
allow_unequal_harts; a launch phase shorter than one launch; budget <= seconds, or either outside
`timeout 10`; abs_stop_c outside 40..90 or board_cap_w outside 0..100; a cap_mean_c / cap_high_c
above abs_stop_c, which would never fire; a duplicate block name.  A real session is refused too
(exit 2) when the host is not the card, when `timeout` is missing (hold10 could not be enforced),
when the heater is the non-aifoundry2 build or its kernel comes from a different build
(lib.sh:35-43), when the kernel is not an ELF file, or when free space is under the recording plus
record_cam.py's own --min-free-mb floor.

--dry touches no device at all: no lock, no heater, no ettelem.  A launch becomes a sleep of about
expected_launch_s and the sampler becomes a synthetic line generator of the same shape (fed by a small
thermal model, so the safety paths are exercisable); the camera is still recorded for real.  The three
functions that open the card (_take_lock, _spawn_heater, _spawn_sampler) refuse outright when dry, so
no future edit can reach the card through them.  HM_HEATER / HM_ETTELEM / HM_KERNEL / HM_RECORD_CAM
override those paths in dry mode only; set in a real session they are refused (hplib.sh:364 F1/F15).
Dry test hooks: HM_DRY_INTRUDE=<file> makes the other-user check report an intrusion once that file
exists (hplib.sh:80) and HM_DRY_INTRUDE_AFTER_S=<s> after that many seconds of session, so the
between-launch exit-3 path is testable; HM_DRY_HOT_AFTER_S / HM_DRY_HOT_W_AFTER_S push the synthetic
die or board power over the caps; HM_DRY_SAMPLER_FREEZE_AFTER_S stops the synthetic lines.

Exit codes: 0 done (including done:max_card_min and done:max_wall_min); 1 error (telemetry lost, the
watcher gone, the heater failing or outliving hold10); 2 refused (bad protocol, preflight, wrong
host); 3 the card is not ours (lock held, another user); 4 a safety stop, including an operator's
RUNDIR/STOP; 5 a signal.
"""
import argparse
import errno
import fcntl
import hashlib
import json
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

# Device processes are recognised by executable name (ps comm), never by command line (lib.sh:57-60).
DEV_COMM = re.compile(r"_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$")
OTHER_COMM = re.compile(DEV_COMM.pattern + r"|^Runner\.Worker$")

CARD_HOST = "aifoundry2"                      # E62's card (DECISIONS 2), and the default when a protocol names none
# E65 amendment A1 (26 Oct 2026): a protocol may name its own card in its top-level "card" field, so the one runner
# serves E62 on aifoundry2 and E65's hart ladder on aifoundry3. A protocol without the field keeps CARD_HOST, so
# E62's own protocol.json runs exactly as before. The build pairing below (lib.sh:35-43) is aifoundry2's rule and is
# checked only on aifoundry2: every other host builds sparsity into build/sparsity.
HOST_HEATER_DIR = {"aifoundry2": "sparsity_t2"}   # lib.sh:35-43; every other card: "sparsity"
LOCK_PATH = "/run/lock/etsoc-shire0.lock"     # single-card host: V3_DEVICE is unset (lib.sh:183)
ET_LIB = "/opt/et/lib"
DEVMNGT = "/opt/et/bin/dev_mngt_service"
DEFAULT_CAM_URL = "http://p3-phone:8080/stream.raw.z"
DEFAULT_HEATER = "build/sparsity_t2/host/sparsity_host"   # aifoundry2's build (lib.sh:35-38)
DEFAULT_KERNEL = "build/sparsity_t2/kernel/sparsity.elf"
DEFAULT_ETTELEM = "build/ettelem/ettelem"

ABS_STOP_CEILING_C = 90.0   # the lab's 90 C rule (hplib.sh:12): a protocol may only be stricter
BOARD_CAP_CEILING_W = 100.0  # the full-card heater measures 84-86 W (launch.md 4); above this is a typo
HOLD_S = 10                  # hold10: timeout 10 on every device process (lib.sh:100)
HOLD_GRACE_S = 5             # how long past hold10 we wait before calling the heater wedged
SAMPLER_MARGIN_S = 900       # the sampler's --seconds beyond the plan (dtf/block.sh:107)
SAMPLER_TERM_WAIT_S = 30     # SIGTERM then up to 30 s before a SIGKILL + drain (lib.sh:167-172)
CAM_MIN_FREE_MB = 5000       # record_cam.py's own floor: it stops below this (camera.md 7)
MAX_SAMPLER_RESTARTS = 3     # ettelem is flaky at start (lib.sh:147); a fourth loss ends the session


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


def popcount(x):
    return bin(x).count("1")


def as_mask(v):
    """A mask as int, from 3435973836 or "0xcccccccc"."""
    if isinstance(v, bool):
        raise ValueError("mask must be a number or a hex string")
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        return int(v, 16) if v.lower().startswith("0x") else int(v, 0)
    raise ValueError(f"mask of type {type(v).__name__}")


def hexmask(m):
    return f"0x{m:08x}"


def me_user():
    """This session's user name. $USER is not always set under ssh, and an empty one would make
    every logged-in user look like somebody else and stop the session at once."""
    u = os.environ.get("USER") or os.environ.get("LOGNAME")
    if not u:
        try:
            import pwd
            u = pwd.getpwuid(os.getuid()).pw_name
        except Exception:
            u = ""
    return u


def run_out(cmd, timeout=15, env=None):
    """A read-only helper command (who, ps, git, et-who), plus the management-queue drain, which is
    the one caller that needs LD_LIBRARY_PATH. Every call is bounded: nothing waits for a person."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           stdin=subprocess.DEVNULL, close_fds=True, env=env)
        return r.returncode, r.stdout, r.stderr
    except (OSError, subprocess.SubprocessError) as e:
        return -1, "", str(e)


class EndSession(Exception):
    """Raised anywhere to end the session cleanly with a reason and an exit code."""

    def __init__(self, reason, code):
        super().__init__(reason)
        self.reason = reason
        self.code = code


class Refuse(Exception):
    """A preflight or protocol refusal: nothing has been started yet."""


# ---------------------------------------------------------------------------- protocol


class Phase:
    __slots__ = ("set_name", "dwell_s", "idle", "mask", "per_shire", "harts", "launches")

    def __init__(self, set_name, dwell_s, idle, mask, per_shire, harts, launches=None):
        self.set_name, self.dwell_s, self.idle = set_name, dwell_s, idle
        self.mask, self.per_shire, self.harts = mask, per_shire, harts
        # protocol v2: a launch phase is a launch COUNT, not a time target (the red team's first
        # blocker: at the measured 8.31-8.49 s a time rule adds a launch to every phase)
        self.launches = launches


class Block:
    __slots__ = ("name", "title", "phases", "cycles", "warmup_cycles", "order", "movie", "raw",
                 "laps", "kind")

    def __init__(self, name, title, phases, cycles, warmup_cycles, order, movie, raw, laps=None,
                 kind=None):
        self.name, self.title, self.phases = name, title, phases
        self.cycles, self.warmup_cycles, self.order = cycles, warmup_cycles, order
        self.movie, self.raw = movie, raw
        # protocol v2: lap_phase_orders, one list of set names per lap (warm-up laps included), the
        # sequence the runner executes; resolved to phase indices by Protocol._parse
        self.laps, self.kind = laps, kind

    def total_laps(self):
        """Laps the runner executes. Protocol v2 (lap_phase_orders present): `cycles` is the TOTAL
        lap count with the warm-up laps included (conventions.cycles_rule), one lap order per lap.
        Version 1: `cycles` analysed laps plus `warmup_cycles`."""
        if self.laps:
            return len(self.laps)
        return self.warmup_cycles + self.cycles

    def cycle_phases(self, cycle):
        """The phase order for one cycle (dtf alternates the side order between passes).
        Returns (arm index into self.phases, phase) pairs in execution order."""
        if self.laps:
            return [(i, self.phases[i]) for i in self.laps[cycle % len(self.laps)]]
        if self.order == "alternate" and cycle % 2 == 1:
            return list(reversed(list(enumerate(self.phases))))
        if self.order == "reverse":
            return list(reversed(list(enumerate(self.phases))))
        return list(enumerate(self.phases))


class Protocol:
    def __init__(self, raw, path):
        self.raw, self.path = raw, path
        self.experiment = str(raw.get("experiment") or "E62")
        self.sets = {}
        self.blocks = []
        self.problems = []
        self._parse()

    # -- parsing is forgiving; _check() is where a protocol is refused
    def _parse(self):
        sets = self.raw.get("sets") or {}
        if not isinstance(sets, dict):
            self.problems.append("sets must be an object of name -> set")
            sets = {}
        for name, s in sets.items():
            if not isinstance(s, dict):
                self.problems.append(f"set {name}: not an object")
                continue
            idle = bool(s.get("idle")) or (s.get("mask") in (None, 0, "0", "0x0"))
            if not idle:                    # protocol v2 spells IDLE as mask 0x00000000, harts 0
                try:
                    idle = as_mask(s["mask"]) == 0
                except (KeyError, ValueError):
                    pass
            mask = per = harts = None
            if not idle:
                try:
                    mask = as_mask(s["mask"])
                except (KeyError, ValueError) as e:
                    self.problems.append(f"set {name}: bad mask ({e})")
                    continue
                per = int(s.get("per_shire", 32))
                harts = popcount(mask) * per if mask is not None else None
            self.sets[name] = {"name": name, "idle": idle, "mask": mask, "per_shire": per,
                               "harts": harts, "shires": s.get("shires"), "raw": s}
        blocks = self.raw.get("blocks") or []
        if not isinstance(blocks, list) or not blocks:
            self.problems.append("blocks must be a non-empty list")
            blocks = []
        for i, b in enumerate(blocks):
            if not isinstance(b, dict):
                self.problems.append(f"block {i}: not an object")
                continue
            name = str(b.get("name") or b.get("id") or f"block{i}")
            phases = []
            for j, ph in enumerate(b.get("phases") or []):
                if not isinstance(ph, dict):
                    self.problems.append(f"block {name} phase {j}: not an object")
                    continue
                sn = ph.get("set")
                try:
                    dwell = float(ph.get("dwell_s"))
                except (TypeError, ValueError):
                    self.problems.append(f"block {name} phase {j}: bad dwell_s {ph.get('dwell_s')!r}")
                    continue
                st = self.sets.get(sn) if sn is not None else None
                idle = bool(ph.get("idle")) or sn is None or (st is not None and st["idle"])
                if sn is not None and st is None:
                    self.problems.append(f"block {name} phase {j}: set {sn!r} does not exist")
                    continue
                nl = ph.get("launches")
                if nl is not None and not idle:
                    try:
                        nl = int(nl)
                    except (TypeError, ValueError):
                        self.problems.append(f"block {name} phase {j}: bad launches {nl!r}")
                        continue
                else:
                    nl = None
                phases.append(Phase(sn, dwell, idle,
                                    None if idle else st["mask"],
                                    None if idle else st["per_shire"],
                                    None if idle else st["harts"], nl))
            order = str(b.get("order") or "as-given")
            laps = None
            lpo = b.get("lap_phase_orders")
            if lpo is not None:
                # resolve each lap's set names to arm indices: positionally when a lap lists the
                # phases exactly as given (E62-CAL repeats sets), else by the set's unique name
                laps = []
                names = [ph.set_name for ph in phases]
                for k, lap in enumerate(lpo if isinstance(lpo, list) else []):
                    if list(lap) == names:
                        laps.append(list(range(len(phases))))
                        continue
                    idx = []
                    for sname in lap:
                        hits = [m for m, nm in enumerate(names) if nm == sname]
                        if len(hits) != 1:
                            self.problems.append(f"block {name} lap {k}: set {sname!r} matches "
                                                 f"{len(hits)} phases (needs exactly one)")
                            break
                        idx.append(hits[0])
                    laps.append(idx)
                if not isinstance(lpo, list) or not lpo:
                    self.problems.append(f"block {name}: lap_phase_orders must be a non-empty list")
                    laps = None
            self.blocks.append(Block(name, str(b.get("title") or name), phases,
                                     int(b.get("cycles", 1)), int(b.get("warmup_cycles", 0)),
                                     order, bool(b.get("movie", True)), b, laps,
                                     str(b.get("kind") or "")))
        sess = self.raw.get("session") or {}
        self.pre_idle_s = float(sess.get("pre_idle_s", 60))
        self.post_idle_s = float(sess.get("post_idle_s", 60))
        self.block_gap_s = float(sess.get("block_gap_s", sess.get("between_blocks_idle_s", 0)))
        self.block_order = sess.get("block_order") or self.raw.get("order")
        # protocol v2: the cool-down gate (bounded, never an unbounded wait) and the full-card
        # per-cycle die gate of E62-BLOOM / E62-CAL's UNI32 rung
        self.cooldown = self.raw.get("cooldown_gate") or None
        h = self.raw.get("heater") or {}
        self.heater = {
            "bin": h.get("bin") or DEFAULT_HEATER,
            "kernel": h.get("kernel") or DEFAULT_KERNEL,
            "test": h.get("test") or "fma", "type": h.get("type") or "fp32",
            "pattern": h.get("pattern") or "none", "values": h.get("values") or "randn",
            "seconds": float(h.get("seconds", 8)), "budget": float(h.get("budget", 9.5)),
            "seed": int(h.get("seed", 1)),
            "expected_launch_s": float(h.get("expected_launch_s", 8.4)),
        }
        s = self.raw.get("safety") or {}
        self.safety = {
            "abs_stop_c": float(s.get("abs_stop_c", 85)),
            "board_cap_w": float(s.get("board_cap_w", 95)),
            "cap_consecutive": int(s.get("cap_consecutive", 2)),
            "die_consecutive": int(s.get("die_consecutive", 1)),
            "sampler_stale_s": float(s.get("sampler_stale_s", 3)),
            "cap_mean_c": (float(s["cap_mean_c"]) if s.get("cap_mean_c") else None),
            "cap_high_c": (float(s["cap_high_c"]) if s.get("cap_high_c") else None),
            "pmic_margin_c": float(s.get("pmic_margin_c", 10)),
            "bloom_cycle_stop_c": (float(s["bloom_cycle_stop_c"]) if s.get("bloom_cycle_stop_c")
                                   else None),
        }
        caps = self.raw.get("caps") or {}
        bud = self.raw.get("budget") or {}
        self.caps = {"max_card_min": float(caps.get("max_card_min",
                                                    bud.get("card_held_cap_min", 75))),
                     "max_wall_min": float(caps.get("max_wall_min",
                                                    bud.get("card_session_wall_cap_min", 120)))}
        cam = self.raw.get("camera") or {}
        self.camera = {"url": cam.get("url") or None}
        self.tools = self.raw.get("tools") or {}

    def check(self, allow_short_phases=False):
        """Every sanity check that refuses a protocol. Returns a list of problems."""
        p = list(self.problems)
        names = [b.name for b in self.blocks]
        for n in sorted(set(names)):
            if names.count(n) > 1:
                p.append(f"block name {n!r} appears {names.count(n)} times")
        for name, s in self.sets.items():
            if s["idle"]:
                continue
            m = s["mask"]
            if m == 0 or m >> 32:
                p.append(f"set {name}: mask {hexmask(m)} is zero or wider than 32 bits "
                         f"(sparsity_host main.cpp:1010 refuses it)")
            if not 1 <= (s["per_shire"] or 0) <= 32:
                p.append(f"set {name}: per_shire {s['per_shire']} outside 1..32")
            shires = s["shires"]
            if shires is not None:
                try:
                    want = sorted(int(x) for x in shires)
                except (TypeError, ValueError):
                    p.append(f"set {name}: shires is not a list of numbers")
                    want = None
                if want is not None:
                    got = sorted(i for i in range(32) if m >> i & 1)
                    if want != got:
                        p.append(f"set {name}: mask {hexmask(m)} lights shires {got} but the set "
                                 f"lists {want}")
            declared = s["raw"].get("harts")
            if declared is not None and int(declared) != s["harts"]:
                p.append(f"set {name}: harts {declared} but popcount({hexmask(m)}) * per_shire "
                         f"{s['per_shire']} = {s['harts']}")
        exp = self.heater["expected_launch_s"]
        for b in self.blocks:
            if not b.phases:
                p.append(f"block {b.name}: no phases")
            if b.cycles < 1:
                p.append(f"block {b.name}: cycles {b.cycles} < 1")
            if b.warmup_cycles < 0:
                p.append(f"block {b.name}: warmup_cycles {b.warmup_cycles} < 0")
            if b.order not in ("as-given", "alternate", "reverse"):
                p.append(f"block {b.name}: order {b.order!r} is not as-given|alternate|reverse")
            harts = sorted({ph.harts for ph in b.phases if not ph.idle})
            # calibration and bloom blocks change total power on purpose (DECISIONS 4: the bloom is
            # the one pattern-vs-idle movie); every swap, sequence and control stays hart-matched
            unequal_ok = b.raw.get("allow_unequal_harts") or b.kind in ("calibration", "bloom")
            if len(harts) > 1 and not unequal_ok:
                p.append(f"block {b.name}: a swap must be constant total power (DECISIONS 4) but its "
                         f"arms have harts {harts}; set allow_unequal_harts to run it anyway")
            if b.kind not in ("calibration", "bloom") and any(ph.idle for ph in b.phases):
                p.append(f"block {b.name}: an IDLE phase in a {b.kind or 'swap'} block breaks "
                         f"constant total power")
            if b.laps is not None:
                if len(b.laps) != b.cycles or b.warmup_cycles >= b.cycles:
                    p.append(f"block {b.name}: {len(b.laps)} lap orders for {b.cycles} cycles "
                             f"(total, {b.warmup_cycles} of them warm-up)")
                for k, lap in enumerate(b.laps):
                    if sorted(lap) != list(range(len(b.phases))) and b.kind != "calibration":
                        p.append(f"block {b.name} lap {k}: runs arms {lap}, not each of the "
                                 f"{len(b.phases)} phases once")
            for j, ph in enumerate(b.phases):
                if ph.dwell_s <= 0:
                    p.append(f"block {b.name} phase {j}: dwell_s {ph.dwell_s} <= 0")
                elif ph.launches is not None:
                    if ph.launches < 1:
                        p.append(f"block {b.name} phase {j}: launches {ph.launches} < 1")
                elif not ph.idle and ph.dwell_s < exp and not allow_short_phases:
                    p.append(f"block {b.name} phase {j}: dwell_s {ph.dwell_s} is shorter than one "
                             f"launch ({exp} s), so the phase would run no launches")
        h = self.heater
        if h["budget"] <= h["seconds"]:
            p.append(f"heater: --budget {h['budget']} <= --seconds {h['seconds']}: the device-time "
                     f"budget would silently truncate the dwell (launch.md 1, main.cpp:1007)")
        if h["seconds"] <= 0 or h["seconds"] > HOLD_S - 1.5:
            p.append(f"heater: --seconds {h['seconds']} outside 0..{HOLD_S - 1.5} (timeout {HOLD_S})")
        if h["budget"] > HOLD_S - 0.4:
            p.append(f"heater: --budget {h['budget']} leaves no room inside timeout {HOLD_S}")
        if h["expected_launch_s"] <= 0 or h["expected_launch_s"] > HOLD_S:
            p.append(f"heater: expected_launch_s {h['expected_launch_s']} outside 0..{HOLD_S}")
        s = self.safety
        if not 40 <= s["abs_stop_c"] <= ABS_STOP_CEILING_C:
            p.append(f"safety: abs_stop_c {s['abs_stop_c']} outside 40..{ABS_STOP_CEILING_C} "
                     f"(the lab's 90 C rule stands, hplib.sh:12)")
        if not 0 < s["board_cap_w"] <= BOARD_CAP_CEILING_W:
            p.append(f"safety: board_cap_w {s['board_cap_w']} outside 0..{BOARD_CAP_CEILING_W}")
        if s["cap_consecutive"] < 1 or s["die_consecutive"] < 1:
            p.append("safety: cap_consecutive and die_consecutive must be >= 1")
        if s["sampler_stale_s"] <= 0:
            p.append("safety: sampler_stale_s must be > 0")
        for k in ("cap_mean_c", "cap_high_c"):       # a cap above the hard stop is not a cap
            if s[k] and s[k] > s["abs_stop_c"]:
                p.append(f"safety: {k} {s[k]:g} is above abs_stop_c {s['abs_stop_c']:g}, so it "
                         f"would never fire (hplib.sh:12: the run caps end the run long before)")
        if s["pmic_margin_c"] < 0:
            p.append("safety: pmic_margin_c must be >= 0")
        if self.pre_idle_s < 0 or self.post_idle_s < 0 or self.block_gap_s < 0:
            p.append("session: pre_idle_s, post_idle_s and block_gap_s must be >= 0")
        if self.block_order is not None:
            if not isinstance(self.block_order, list):
                p.append("session.block_order must be a list of block names")
            else:
                known = {b.name for b in self.blocks}
                for n in self.block_order:
                    if n not in known:
                        p.append(f"session.block_order names unknown block {n!r}")
        return p

    def ordered_blocks(self, only=None):
        bs = {b.name: b for b in self.blocks}
        order = [n for n in (self.block_order or [b.name for b in self.blocks]) if n in bs]
        for b in self.blocks:                       # blocks the order forgot still run, last
            if b.name not in order:
                order.append(b.name)
        if only:
            order = [n for n in order if n in set(only)]
        return [bs[n] for n in order]


def estimate(proto, blocks, exp_wall):
    """The plan and its estimated seconds, with no clock involved (--list, and the sampler's span)."""
    plan = {"pre_idle_s": proto.pre_idle_s, "post_idle_s": proto.post_idle_s, "blocks": []}
    total = proto.pre_idle_s + proto.post_idle_s
    for i, b in enumerate(blocks):
        cycles = b.total_laps()
        per_cycle, launches = 0.0, 0
        for _, ph in b.cycle_phases(0):
            if ph.idle:
                per_cycle += ph.dwell_s
            else:
                n = ph.launches if ph.launches is not None else int(ph.dwell_s // exp_wall)
                launches += n
                per_cycle += n * exp_wall + n * 0.05      # the between-launch checks
        gap = proto.block_gap_s if i < len(blocks) - 1 else 0.0
        secs = per_cycle * cycles + gap
        total += secs
        plan["blocks"].append({"block": b.name, "title": b.title, "cycles": b.cycles,
                               "warmup_cycles": b.warmup_cycles, "order": b.order,
                               "phases": [{"set": ph.set_name, "idle": ph.idle,
                                           "dwell_s": ph.dwell_s, "mask": None if ph.idle else hexmask(ph.mask),
                                           "harts": ph.harts} for _, ph in b.cycle_phases(0)],
                               "launches": launches * cycles, "s": round(secs, 1),
                               "block_gap_s": gap})
    plan["total_s"] = round(total, 1)
    plan["total_min"] = round(total / 60.0, 2)
    plan["expected_launch_s"] = exp_wall
    plan["launches"] = sum(b["launches"] for b in plan["blocks"])
    return plan


# ---------------------------------------------------------------------------- telemetry


def num(v):
    """A telemetry field as a float, or None. One malformed field must never kill the watcher:
    a TypeError inside the caps would leave the heat running until the main loop noticed."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


class Watcher(threading.Thread):
    """Reads the sampler's lines, keeps the newest state, applies the caps.

    It is a thread rather than hplib's separate process, so its liveness is checked by the main loop
    through is_alive() and the heartbeat below (hplib.sh F11: a dead watcher leaves a state line that
    still looks fresh).  It never opens a device: it only reads the file the sampler writes.

    The watcher owns the fast path to stopping the heat: on a cap trip, on telemetry going stale or
    losing its die reading, and on its own death, it calls back to touch the heater's stop-file, so
    an in-flight heater ends at its next ~0.5 s launch boundary (main.cpp:577-580) instead of
    running to the end of its `timeout 10`.  The main loop sees `trip`/`lost` at its next guard()
    and ends the session; the stopping does not wait for it.
    """

    def __init__(self, raw_path, safety, on_trip, on_lost=None):
        super().__init__(name="hm-watcher", daemon=True)
        self.raw_path, self.safety, self.on_trip = raw_path, safety, on_trip
        self.on_lost = on_lost
        self.lock = threading.Lock()
        self.state = {"t_ms": None, "recv_ms": None, "first_recv_ms": None, "die_c": None,
                      "die_low_c": None, "die_high_c": None, "pmic_c": None, "board_w": None,
                      "mhz_minion": None, "n": 0, "bad": 0, "no_die": 0, "die_recv_ms": None,
                      "skew_ms": None}
        self.heartbeat_ms = now_ms()
        self.stop_flag = threading.Event()
        self.trip = None
        self.lost = None
        self.armed = True          # disarm() at teardown: see disarm()
        self.skew_seen = None
        self._consec = {}
        self._pos = 0
        self._buf = b""
        self.error = None
        self._stale_ms = max(200.0, float(safety.get("sampler_stale_s") or 3) * 1000.0)

    def snapshot(self):
        with self.lock:
            s = dict(self.state)
        t = now_ms()
        s["heartbeat_ms"] = self.heartbeat_ms
        # freshness is measured on the host's own clock, at the moment the line was read, never on
        # the sampler's own t_ms: a stamp in the future would make stale telemetry look fresh for
        # ever (hplib.sh F11 is explicit that the liveness check is on the real clock)
        s["age_ms"] = (t - s["recv_ms"]) if s["recv_ms"] else None
        s["stamp_age_ms"] = (t - s["t_ms"]) if s["t_ms"] else None
        s["die_age_ms"] = (t - s["die_recv_ms"]) if s["die_recv_ms"] else None
        s["trip"], s["lost"] = self.trip, self.lost
        return s

    def disarm(self):
        """Teardown: the session is ending, the heat is already stopped and the sampler is about to
        be sent SIGTERM.  The watcher keeps reading its last lines (and still applies the caps, for
        the record) but stops calling the sampler's death stale telemetry."""
        self.armed = False

    def clear_lost(self):
        """After the sampler has been restarted: forget the gap, start the clock again."""
        self.lost = None
        self._consec.clear()
        with self.lock:
            self.state["recv_ms"] = None
            self.state["first_recv_ms"] = None
            self.state["die_recv_ms"] = None

    def run(self):
        try:
            while not self.stop_flag.is_set():
                self._read_new()
                self._check_live()
                self.heartbeat_ms = now_ms()
                time.sleep(0.05)
            self._read_new()
        except Exception as e:                        # a watcher that dies must be visible, not silent
            self.error = f"{type(e).__name__}: {e}"
            self._lose(f"watcher_died:{type(e).__name__}")   # stop the heat on the way out

    def _read_new(self):
        try:
            with open(self.raw_path, "rb") as f:
                f.seek(self._pos)
                data = f.read()
                self._pos = f.tell()
        except OSError:
            return
        if not data:
            return
        self._buf += data
        *lines, self._buf = self._buf.split(b"\n")
        for ln in lines:
            if ln.startswith(b"{"):
                self._sample(ln)

    def _check_live(self):
        """Telemetry that stops arriving, or stops carrying a die temperature, is unwatched heat:
        stop it here rather than at the main loop's next guard(), which during a launch is up to one
        launch away.  Only armed once a first sample has been seen; the session start has its own
        'the watcher saw no sample' gate."""
        if self.lost or self.trip or not self.armed:
            return
        with self.lock:
            recv, die_recv = self.state["recv_ms"], self.state["die_recv_ms"]
            first, n = self.state["first_recv_ms"], self.state["n"]
        t = now_ms()
        if recv and t - recv > self._stale_ms:
            self._lose(f"telemetry_stale:{t - recv}ms")
        elif die_recv and t - die_recv > self._stale_ms:
            # lines still arriving, but none of them carries a die temperature any more: the die
            # cap cannot fire on a sample it cannot read, so this is unwatched heat too
            self._lose(f"telemetry_no_die:{t - die_recv}ms")
        elif first and die_recv is None and t - first > self._stale_ms:
            self._lose(f"telemetry_no_die:{n} samples, none with a die temperature")

    def _sample(self, ln):
        try:
            s = json.loads(ln.decode("utf-8", "replace"))
            if not isinstance(s, dict):
                raise ValueError("not an object")
            t = s.get("temp_c")
            t = t if isinstance(t, dict) else {}
            mins = t.get("minshire")
            mins = mins if isinstance(mins, (list, tuple)) else []
            die = num(mins[0]) if len(mins) > 0 else None
            low = num(mins[1]) if len(mins) > 1 else None
            high = num(mins[2]) if len(mins) > 2 else None
            pmic = num(t.get("pmic"))
            w = num(s.get("board_w"))
            stamp = num(s.get("t_ms"))
            mhz = s.get("mhz")
            mhz = num(mhz.get("minion")) if isinstance(mhz, dict) else None
        except (ValueError, TypeError, AttributeError, IndexError):
            with self.lock:
                self.state["bad"] += 1
            return
        recv = now_ms()
        with self.lock:
            st = self.state
            st["t_ms"] = int(stamp) if stamp else recv
            st["recv_ms"] = recv
            st["first_recv_ms"] = st["first_recv_ms"] or recv
            st["skew_ms"] = (recv - int(stamp)) if stamp else None
            st["die_c"], st["die_low_c"], st["die_high_c"] = die, low, high
            st["pmic_c"] = pmic
            st["board_w"] = w
            st["mhz_minion"] = mhz
            st["n"] += 1
            if die is None and high is None:
                st["no_die"] += 1
            else:
                st["die_recv_ms"] = recv
            skew = st["skew_ms"]
        if skew is not None and abs(skew) > 2000 and self.skew_seen is None:
            self.skew_seen = skew        # the host clock is the session's clock: a big skew is news
        self._apply_caps(die, high, w, pmic)

    def _bump(self, key, bad):
        self._consec[key] = self._consec.get(key, 0) + 1 if bad else 0
        return self._consec[key]

    def _apply_caps(self, die, high, w, pmic):
        sf = self.safety
        abs_c = sf["abs_stop_c"]
        hot = max([v for v in (die, high) if v is not None], default=None)
        if self._bump("die", hot is not None and hot >= abs_c) >= sf["die_consecutive"]:
            return self._fire(f"die {hot:g} C >= abs_stop_c {abs_c:g} C")
        if pmic is not None and self._bump("pmic", pmic >= abs_c + sf["pmic_margin_c"]) >= sf["cap_consecutive"]:
            return self._fire(f"pmic {pmic:g} C >= abs_stop_c + {sf['pmic_margin_c']:g} C")
        if self._bump("board", w is not None and w > sf["board_cap_w"]) >= sf["cap_consecutive"]:
            return self._fire(f"board power {w:g} W > board_cap_w {sf['board_cap_w']:g} W on "
                              f"{sf['cap_consecutive']} consecutive samples")
        if sf["cap_mean_c"] and self._bump("mean", die is not None and die >= sf["cap_mean_c"]) >= sf["cap_consecutive"]:
            return self._fire(f"die mean {die:g} C >= cap_mean_c {sf['cap_mean_c']:g} C")
        if sf["cap_high_c"] and self._bump("high", high is not None and high >= sf["cap_high_c"]) >= sf["cap_consecutive"]:
            return self._fire(f"die high {high:g} C >= cap_high_c {sf['cap_high_c']:g} C")
        return None

    def _fire(self, why):
        if self.trip is None:
            self.trip = why
            try:
                self.on_trip(why)                     # touches the stop-file, marks, ends the session
            except Exception as e:
                self.error = f"on_trip: {type(e).__name__}: {e}"

    def _lose(self, why):
        """Telemetry lost, or the watcher itself gone: stop the heat now, let the main loop decide
        whether to restart the sampler or end the session."""
        if self.lost is None and self.trip is None:
            self.lost = why
            if self.on_lost is not None:
                try:
                    self.on_lost(why)
                except Exception as e:
                    self.error = f"on_lost: {type(e).__name__}: {e}"


class DrySampler(threading.Thread):
    """The synthetic sampler: ettelem-shaped lines at 10 Hz from a small thermal model. Dry only."""

    def __init__(self, path, session, every_ms=100):
        super().__init__(name="hm-dry-sampler", daemon=True)
        self.path, self.session, self.every = path, session, every_ms / 1000.0
        self.stop_flag = threading.Event()
        self.n = 0
        self.die = 51.0
        self.w = 24.0
        self.rng = random.Random(20261021)
        self.freeze_after = float(os.environ.get("HM_DRY_SAMPLER_FREEZE_AFTER_S") or 0)
        self.hot_after = float(os.environ.get("HM_DRY_HOT_AFTER_S") or 0)
        self.hot_w_after = float(os.environ.get("HM_DRY_HOT_W_AFTER_S") or 0)

    def run(self):
        t0 = time.time()
        with open(self.path, "ab", buffering=0) as f:
            while not self.stop_flag.is_set():
                el = time.time() - t0
                if self.freeze_after and el >= self.freeze_after:
                    time.sleep(self.every)
                    continue
                harts = self.session.harts_in_flight
                w_t = 24.0 + 0.0406 * harts                      # 1.3 W per shire at per-shire 32
                self.w += (w_t - self.w) * min(1.0, self.every / 0.3)
                die_t = 51.0 + 0.68 * (self.w - 24.0)            # 0.68 C/W (gyroscope, 9 Oct)
                self.die += (die_t - self.die) * min(1.0, self.every / 20.0)
                die = self.die + self.rng.gauss(0, 0.05)
                w = self.w + self.rng.gauss(0, 0.4)
                if self.hot_after and el >= self.hot_after:
                    die = float(os.environ.get("HM_DRY_HOT_C") or 99)
                if self.hot_w_after and el >= self.hot_w_after:
                    w = float(os.environ.get("HM_DRY_HOT_W") or 120)
                mhz = 800 if die < 65 else (700 if die < 72 else 600)
                d = int(round(die))
                line = {
                    "t_ms": now_ms(), "took_ms": 22, "since_reset_ms": 1000,
                    "board_w": round(w, 2),
                    "sp": {"board_avg_w": round(w, 2), "board_min_w": 20.47, "board_max_w": round(w, 2),
                           "minion_w": [round(w * 0.3, 3), 4.703, round(w * 0.8, 3)],
                           "minion_c": [d, d - 14, d + 11], "system_c": [0, 0, 0],
                           "minion_mhz": [mhz, mhz, mhz], "noc_mhz": [400, 400, 400]},
                    "temp_c": {"pmic": d, "ioshire": [d + 1, d - 13, d + 10],
                               "minshire": [d, d - 11, d + 4]},
                    "die_mv": {"minion": 519, "sram": 704, "noc": 485},
                    "mhz": {"minion": mhz, "noc": 400, "ddr": 933},
                    "dry": True,
                }
                f.write((json.dumps(line) + "\n").encode())
                self.n += 1
                time.sleep(self.every)


# ---------------------------------------------------------------------------- the session


class Session:
    def __init__(self, args, proto, blocks, plan):
        self.a, self.proto, self.blocks, self.plan = args, proto, blocks, plan
        self.dry = bool(args.dry)
        self.rundir = os.path.abspath(args.out)
        self.code_dir = os.path.dirname(os.path.abspath(__file__))
        self.root = args.root
        self.stop_file = os.path.join(self.rundir, "STOP")
        self.cam_stop = os.path.join(self.rundir, "CAMSTOP")
        self.tel_raw = os.path.join(self.rundir, "tel.jsonl.raw")
        self.lock_fd = None
        self.sampler = None            # subprocess.Popen (real) or DrySampler (dry)
        self.sampler_restarts = 0
        self.watcher = None
        self.cam = None
        self.harts_in_flight = 0       # read by DrySampler's model
        self.exp_wall = proto.heater["expected_launch_s"]
        self.launch_n = 0
        self.launch_wall_s = 0.0
        self.ns_baseline = None        # the et_soc1 use count with only our sampler open
        self.t_start_ms = None
        self.t_pre_idle_end_ms = None
        self.t_post_idle_start_ms = None
        self.card_t0 = None
        self.stop_reason = None
        self.exit_code = EXIT_OK
        self.signalled = None
        self.notes = []
        self.checks = []
        self.fin = {}
        self.rng = random.Random(1021)
        self._f = {}
        # marks.jsonl and run.log are written by the main loop AND by the watcher thread: one lock
        # over the handle table and the writes, so no line is interleaved and finish() can close
        # them while the watcher is still running
        self._io_lock = threading.RLock()
        self._heater_pids = set()      # our own live device children, excluded from the ps check
        self.orphans = []              # device processes that outlived hold10: never killed, reported
        self.max_card_s = (args.max_card_min if args.max_card_min is not None
                           else proto.caps["max_card_min"]) * 60.0

    # -- small io helpers (thread-safe: the watcher writes marks too) -------
    def _open(self, name):
        if name not in self._f:
            self._f[name] = open(os.path.join(self.rundir, name), "a", buffering=1)
        return self._f[name]

    def jsonl(self, name, rec):
        line = json.dumps(rec) + "\n"
        with self._io_lock:
            try:
                self._open(name).write(line)
            except (OSError, ValueError):             # ValueError: closed in finish()
                pass

    def say(self, msg):
        line = f"{time.strftime('%H:%M:%S')} [{'dry' if self.dry else 'card'}] {msg}"
        with self._io_lock:
            print(line, flush=True)
            try:
                self._open("run.log").write(line + "\n")
            except (OSError, ValueError):
                pass

    def mark(self, kind, detail="", **data):
        rec = {"t_ms": now_ms(), "kind": kind, "detail": str(detail)}
        if data:
            rec["data"] = data
        self.jsonl("marks.jsonl", rec)

    def touch(self, path):
        try:
            with open(path, "a"):
                os.utime(path, None)
        except OSError as e:
            self.say(f"could not touch {path}: {e}")

    # -- preflight ----------------------------------------------------------
    def preflight(self):
        """Everything checked before the card is opened. Raises Refuse."""
        host = socket.gethostname().split(".")[0]
        want_host = str(self.proto.raw.get("card") or CARD_HOST).split("-c")[0]   # A1: the protocol names its card
        pf = []
        if not self.dry and host != want_host:
            pf.append(f"hostname is {host!r}, not {want_host!r}: a real session runs only on the card its "
                      f"protocol names")
        for env in ("HM_HEATER", "HM_ETTELEM", "HM_KERNEL", "HM_RECORD_CAM"):
            if os.environ.get(env) and not self.dry:
                pf.append(f"{env} is set: binary overrides are honoured in dry mode only "
                          f"(hplib.sh F1/F15)")
        self.heater_bin = self._tool("HM_HEATER", self.proto.heater["bin"])
        self.kernel = self._tool("HM_KERNEL", self.proto.heater["kernel"])
        self.ettelem = self._tool("HM_ETTELEM", self.proto.tools.get("ettelem") or DEFAULT_ETTELEM)
        self.devmngt = self.proto.tools.get("devmngt") or DEVMNGT
        self.record_cam = (os.environ.get("HM_RECORD_CAM") if self.dry else None) \
            or self.proto.tools.get("record_cam") or os.path.join(self.code_dir, "record_cam.py")
        if not self.dry:
            # hold10 is the only hard cap on a device process (lib.sh:100): without `timeout` on
            # the PATH there is no cap at all, so a real session does not start.
            if not shutil.which("timeout"):
                pf.append("no `timeout` on PATH: hold10 (lib.sh:100) is the only hard cap on a "
                          "device process and it cannot be enforced without it")
            # lib.sh:35-43 picks build/sparsity_t2 on this card and build/sparsity elsewhere; the
            # wrong one here would run a different binary against this card (launch.md 8.1)
            want_dir = HOST_HEATER_DIR.get(want_host, "sparsity")
            if os.sep + "build" + os.sep + want_dir + os.sep not in self.heater_bin:
                pf.append(f"heater {self.heater_bin} is not {want_host}'s build: lib.sh:35-43 "
                          f"uses build/{want_dir} on this card (launch.md 8.1)")
            for label, path, x in (("heater", self.heater_bin, True), ("kernel", self.kernel, False),
                                   ("ettelem", self.ettelem, True)):
                if not os.path.isfile(path):
                    pf.append(f"missing {label} {path}")
                elif x and not os.access(path, os.X_OK):
                    pf.append(f"{label} {path} is not executable")
            if os.path.isfile(self.heater_bin):
                with open(self.heater_bin, "rb") as f:
                    blob = f.read()
                for flag in (b"--stop-file", b"--kernel", b"--budget"):
                    if flag not in blob:
                        pf.append(f"{self.heater_bin} has no {flag.decode()} "
                                  f"(dtf/block.sh:84 gates on exactly this)")
            # The heater and its kernel must come from the same build: lib.sh:35-43 picks
            # build/sparsity_t2 on this card and build/sparsity elsewhere, and a mixed pair would
            # silently load the wrong kernel (launch.md 8.1, the first thing a runner must get right).
            hb = os.path.dirname(os.path.dirname(os.path.abspath(self.heater_bin)))
            kb = os.path.dirname(os.path.dirname(os.path.abspath(self.kernel)))
            if hb != kb:
                pf.append(f"heater {self.heater_bin} and kernel {self.kernel} come from different "
                          f"builds ({hb} vs {kb}): lib.sh:35-43 pairs them (launch.md 8.1)")
            if os.path.isfile(self.kernel):
                with open(self.kernel, "rb") as f:
                    if f.read(4) != b"\x7fELF":
                        pf.append(f"kernel {self.kernel} is not an ELF file")
            if not os.path.exists(LOCK_PATH):
                pf.append(f"no card lock {LOCK_PATH}: not starting without it (hplib.sh:359-362)")
            if not os.path.isdir(ET_LIB):
                pf.append(f"no {ET_LIB}: LD_LIBRARY_PATH would be wrong (lib.sh:16)")
        self.cam_url = self.a.cam_url or self.proto.camera["url"] or DEFAULT_CAM_URL
        if not self.a.no_cam:
            if not os.path.isfile(self.record_cam):
                msg = f"no camera recorder at {self.record_cam}"
                if self.dry:
                    self.notes.append(msg + " (dry: the session runs without the camera)")
                else:
                    pf.append(msg + " (pass --no-cam to run without it)")
        free_mb = shutil.disk_usage(self.rundir).free / 1e6
        # the stream is ~1.0 MB/s (camera.md 7), and record_cam.py stops when free space falls
        # below its own --min-free-mb floor, so that floor is part of what the session needs: an
        # admission test without it lets a session start that the recorder abandons minutes in
        need_mb = 500.0 if self.a.no_cam else 1.05 * self.plan["total_s"] + 500 + CAM_MIN_FREE_MB
        if free_mb < need_mb:
            pf.append(f"free space {free_mb:.0f} MB under the {need_mb:.0f} MB this session needs "
                      f"(recording plus the recorder's own {CAM_MIN_FREE_MB} MB floor)")
        if self.plan["total_s"] > self.max_card_s:
            self.notes.append(f"the plan is {self.plan['total_min']:.1f} min, over the "
                              f"{self.max_card_s / 60:g} min card cap: later blocks will be skipped")
        if self.plan["total_s"] > self.proto.caps["max_wall_min"] * 60:
            pf.append(f"the plan is {self.plan['total_min']:.1f} min, over caps.max_wall_min "
                      f"{self.proto.caps['max_wall_min']:.0f} min")
        if os.path.exists(os.path.join(self.rundir, "session.json")) and not self.a.force:
            pf.append(f"{self.rundir} already holds a session.json (pass --force to overwrite)")
        if pf:
            raise Refuse("; ".join(pf))

    def _tool(self, env, path):
        p = (os.environ.get(env) if self.dry else None) or path
        return p if os.path.isabs(p) else os.path.join(self.root, p)

    # -- card etiquette -----------------------------------------------------
    def _take_lock(self):
        """The machine's advisory card lock, non-blocking, held for the session (lib.sh:183-186)."""
        if self.dry:
            raise RuntimeError("_take_lock must never run in dry mode")
        fd = os.open(LOCK_PATH, os.O_RDWR)
        os.set_inheritable(fd, False)        # no child ever holds the lock (hplib.sh:86-87)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            os.close(fd)
            if e.errno in (errno.EACCES, errno.EAGAIN):
                raise EndSession(f"other_user:lock_held:{LOCK_PATH}", EXIT_CARD)
            raise
        self.lock_fd = fd
        self.say(f"card lock {LOCK_PATH} held (fd {fd}, flock -n)")

    def _release_lock(self):
        if self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(self.lock_fd)
            self.lock_fd = None

    def _logged_in_others(self):
        if not shutil.which("who"):
            return []
        rc, out, _ = run_out(["who"])
        users = sorted({ln.split()[0] for ln in out.splitlines() if ln.split()})
        return [u for u in users if u != me_user()]

    def _own_pids(self):
        """Our own live children that are allowed to be on the card: the sampler and any heater
        still being waited on.  Without this, our own in-flight device process would read as a
        stale one of ours and end the session (hplib.sh:112 excludes the sampler for the same
        reason).  The camera recorder opens no device but is excluded too, for clarity."""
        pids = {os.getpid()}
        if self.sampler is not None and not self.dry:
            pids.add(self.sampler.pid)
        if self.cam is not None:
            pids.add(self.cam.pid)
        pids |= self._heater_pids
        return pids

    def _procs(self):
        """(foreign, ours): device processes by executable name, our own live children excluded
        (hplib.sh:112).  A zombie is not on the card: ps still shows its comm, so it is skipped."""
        rc, out, _ = run_out(["ps", "-eo", "uid=,pid=,state=,comm="])
        uid = os.getuid()
        mine = self._own_pids()
        foreign, ours = [], []
        for ln in out.splitlines():
            f = ln.split(None, 3)
            if len(f) != 4:
                continue
            try:
                u, pid = int(f[0]), int(f[1])
            except ValueError:
                continue
            if f[2].strip().upper().startswith("Z"):      # reaped-but-not-waited: holds nothing
                continue
            comm = os.path.basename(f[3].strip())
            if pid in mine:
                continue
            if u != uid and OTHER_COMM.search(comm):
                foreign.append(f"{u}:{pid}:{comm}")
            elif u == uid and DEV_COMM.search(comm):
                ours.append(f"{u}:{pid}:{comm}")
        return foreign, ours

    def _modcount(self):
        """The et_soc1 use count: lsmod's third column, read from /proc/modules."""
        try:
            with open("/proc/modules") as f:
                for ln in f:
                    p = ln.split()
                    if p and p[0] == "et_soc1":
                        return int(p[2])
        except (OSError, ValueError, IndexError):
            return None
        return None

    def check_others(self, where, enforce=True):
        """lib.sh others_present + hplib.sh foreign_procs + the use count. Runs before the session
        and between every launch (hp rule O1). A hit ends the session: exit 3, other_user."""
        hits = []
        intrude = os.environ.get("HM_DRY_INTRUDE")          # dry test hooks (hplib.sh:80)
        after = float(os.environ.get("HM_DRY_INTRUDE_AFTER_S") or 0)
        if self.dry and intrude and os.path.exists(intrude):
            hits.append(f"dry-hook:{intrude}")
        if self.dry and after and self.t_start_ms and now_ms() - self.t_start_ms >= after * 1000:
            hits.append(f"dry-hook:after_{after:g}s")
        users = self._logged_in_others()
        if users:
            hits.append("users:" + ",".join(users))
        foreign, ours = self._procs()
        if foreign:
            hits.append("procs:" + ",".join(foreign))
        if ours:
            hits.append("ours:" + ",".join(ours))
        n = self._modcount()
        if n is not None and self.ns_baseline is not None and n > self.ns_baseline:
            hits.append(f"et_soc1_use:{n}>{self.ns_baseline}")
        # A real session enforces every hit. A dry run touches no card, so it only records what it
        # saw -- except the dry intrusion hook, which exists to exercise the exit-3 path.
        hooked = any(h.startswith("dry-hook:") for h in hits)
        rec = {"where": where, "hits": hits, "use_count": n, "baseline": self.ns_baseline,
               "enforced": bool(enforce and (not self.dry or hooked))}
        self.checks.append(rec)
        if not hits:
            return
        detail = f"{where}: " + "; ".join(hits)
        self.mark("other_user", detail, enforced=rec["enforced"])
        self.say(("others present (" if rec["enforced"] else "others present, not enforced in dry (")
                 + detail + ")")
        if rec["enforced"]:
            raise EndSession("other_user:" + ";".join(hits)[:200], EXIT_CARD)

    # -- the sampler --------------------------------------------------------
    def _spawn_sampler(self, seconds):
        if self.dry:
            raise RuntimeError("_spawn_sampler must never run in dry mode")
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        out = open(self.tel_raw, "ab", buffering=0)
        try:
            return subprocess.Popen(
                [self.ettelem, "sample", "--seconds", str(int(seconds)), "--every-ms", "100",
                 "--reset-ms", "1000"],
                stdout=out, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                env=env, close_fds=True, cwd=self.root,
                # its own session, so a Ctrl-C or a `timeout`-style TERM aimed at this runner's
                # process group cannot reach it: "a sampler killed mid-request poisons the
                # management queue" (lib.sh:9-10).  It is stopped with SIGTERM by stop_sampler.
                start_new_session=True)
        finally:
            out.close()

    def start_sampler(self, seconds):
        """One sampler for the whole session. lib.sh:150-162: six attempts, each waiting for the
        first JSON line, one management-queue drain after the second failure."""
        # a restart appends to the same raw file, so "its first line" means a line past what is
        # already there -- otherwise a dead sampler's output would pass for the new one's
        since = os.path.getsize(self.tel_raw) if os.path.exists(self.tel_raw) else 0
        if self.dry:
            self.sampler = DrySampler(self.tel_raw, self)
            self.sampler.start()
            for _ in range(200):
                if self._tel_has_line(since):
                    break
                time.sleep(0.02)
            self.mark("sampler_start", "dry synthetic sampler")
            return True
        for attempt in range(1, 7):
            self.sampler = self._spawn_sampler(seconds)
            t0 = time.time()
            while time.time() - t0 < 10:
                if self._tel_has_line(since):
                    self.mark("sampler_start", f"attempt {attempt}, pid {self.sampler.pid}")
                    self.say(f"sampler pid {self.sampler.pid} ({int(seconds)} s, 10 Hz, --reset-ms 1000)")
                    return True
                if self.sampler.poll() is not None:
                    break
                time.sleep(0.25)
            self.stop_sampler(quiet=True)
            if attempt == 2:
                self.drain_mgmt()
            self.say(f"sampler attempt {attempt} did not produce a line")
            time.sleep(2)
        return False

    def _tel_has_line(self, since=0):
        try:
            with open(self.tel_raw, "rb") as f:
                f.seek(since)
                return b"{" in f.read(8192)
        except OSError:
            return False

    def stop_sampler(self, quiet=False):
        """SIGTERM only; up to 30 s; SIGKILL and one drain only if it ignores TERM (lib.sh:163-176)."""
        s, self.sampler = self.sampler, None
        if s is None:
            return
        if self.dry:
            s.stop_flag.set()
            s.join(timeout=5)
            if not quiet:
                self.mark("sampler_stop", f"dry, {s.n} synthetic samples")
            return
        if s.poll() is None:
            s.terminate()
            t0 = time.time()
            while time.time() - t0 < SAMPLER_TERM_WAIT_S and s.poll() is None:
                time.sleep(0.1)
            if s.poll() is None:
                self.say(f"sampler {s.pid} ignored SIGTERM for {SAMPLER_TERM_WAIT_S} s: SIGKILL and drain")
                self.mark("error", f"sampler {s.pid} ignored SIGTERM for {SAMPLER_TERM_WAIT_S} s")
                s.kill()
                try:
                    s.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
                self.drain_mgmt()
        if not quiet:
            self.mark("sampler_stop", f"pid {s.pid}, rc {s.returncode}")

    def drain_mgmt(self):
        """One stale reply off the management queue (lib.sh:131-144). Never in dry mode."""
        if self.dry:
            return
        self.say("draining the management queue")
        # lib.sh:16 exports LD_LIBRARY_PATH for the whole framework, so lib.sh:143's drain inherits
        # it; here it has to be passed, or the drain fails to load /opt/et/lib and silently does
        # nothing -- and a silent drain means the next sampler start fails for the same reason.
        run_out(["timeout", "20", self.devmngt, "-m", "DM_CMD_GET_MODULE_POWER", "-n", "0",
                 "-u", "5000"], timeout=25, env=dict(os.environ, LD_LIBRARY_PATH=ET_LIB))

    def sampler_alive(self):
        if self.sampler is None:
            return False
        return self.sampler.is_alive() if self.dry else (self.sampler.poll() is None)

    def restart_sampler(self):
        """Only ever called between launches, with no heat in flight: ettelem exiting early is a
        known flakiness (lib.sh:147).  The watcher will have stopped the heat through the stop-file
        when the lines dried up, so the file is cleared here before launching resumes."""
        self.sampler_restarts += 1
        self.mark("sampler_restart", f"restart {self.sampler_restarts}")
        self.say(f"the sampler stopped: restart {self.sampler_restarts}")
        self.stop_sampler(quiet=True)
        used = time.time() - (self.t_start_ms or now_ms()) / 1000.0
        left = max(60.0, self.plan["total_s"] - used) + SAMPLER_MARGIN_S
        if self.sampler_restarts > MAX_SAMPLER_RESTARTS or not self.start_sampler(left):
            raise EndSession("error:sampler_gone", EXIT_ERR)
        if self.watcher is not None:
            self.watcher.clear_lost()
            t0 = time.time()
            while time.time() - t0 < 15 and self.watcher.snapshot()["recv_ms"] is None:
                time.sleep(0.05)
            if self.watcher.snapshot()["recv_ms"] is None:
                raise EndSession("error:watcher_saw_no_sample_after_restart", EXIT_ERR)
        self._clear_stop_file(f"sampler restart {self.sampler_restarts}")
        self.take_ns_baseline()

    def take_ns_baseline(self):
        """The et_soc1 use count with only our sampler open: the intrusion baseline (hplib.sh:429)."""
        best = 0
        for _ in range(3):
            n = self._modcount()
            if n is not None:
                best = max(best, n)
            time.sleep(0.05)
        self.ns_baseline = best
        self.say(f"et_soc1 use-count baseline {best}")

    # -- the camera ---------------------------------------------------------
    def start_camera(self):
        if self.a.no_cam or not os.path.isfile(self.record_cam):
            self.notes.append("no camera recording in this session")
            return
        os.makedirs(os.path.join(self.rundir, "cam"), exist_ok=True)
        max_s = int(self.plan["total_s"] * 1.15 + 300)   # the recording outlives a slow session
        cmd = ["nice", "-n", "19", sys.executable, self.record_cam,
               "--url", self.cam_url, "--out", os.path.join(self.rundir, "cam"),
               "--stop-file", self.cam_stop, "--max-s", str(max_s),
               "--status-every", "5", "--min-free-mb", "5000", "--no-nice"]
        log = open(os.path.join(self.rundir, "logs", "record_cam.log"), "ab", buffering=0)
        try:
            # its own session: a Ctrl-C at the terminal must not kill the recorder before it has
            # written done.json.  It is stopped through its stop-file, SIGTERM only as a fallback.
            self.cam = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, close_fds=True, cwd=self.root,
                                        start_new_session=True)
        except OSError as e:
            self.mark("error", f"camera recorder would not start: {e}")
            self.say(f"camera recorder would not start: {e}")
            self.cam = None
            return
        finally:
            log.close()
        self.fin["cam_recorded"] = True
        self.fin["cam_pid"] = self.cam.pid
        self.fin["cam_cmd"] = cmd
        self.mark("recorder_start", f"pid {self.cam.pid}, max_s {max_s}", url=self.cam_url)
        self.say(f"camera recorder pid {self.cam.pid} -> {self.rundir}/cam (max {max_s} s)")

    def stop_camera(self):
        if self.cam is None:
            return
        self.touch(self.cam_stop)
        t0 = time.time()
        while time.time() - t0 < 30 and self.cam.poll() is None:
            time.sleep(0.2)
        if self.cam.poll() is None:
            self.say(f"camera recorder {self.cam.pid} ignored the stop-file for 30 s: SIGTERM")
            self.cam.terminate()
            try:
                self.cam.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.say(f"camera recorder {self.cam.pid} ignored SIGTERM: SIGKILL")
                self.cam.kill()
        self.fin["cam_rc"] = self.cam.returncode
        self.mark("recorder_stop", f"pid {self.cam.pid}, rc {self.cam.returncode}")
        self.cam = None

    # -- guards -------------------------------------------------------------
    def guard(self, where):
        """The checks every loop makes: the signal flag, the watcher's liveness and freshness, the
        safety trip, the stop-file, the recorder, and the card- and wall-time caps. Cheap: it reads
        the watcher's state, never the device."""
        if self.signalled:
            self.mark("signal", f"signal {self.signalled} at {where}")
            raise EndSession("signal", EXIT_SIGNAL)
        w = self.watcher
        stale = self.proto.safety["sampler_stale_s"] * 1000
        if w is not None:
            if w.trip:
                raise EndSession(f"safety:{w.trip}", EXIT_SAFETY)
            if not w.is_alive():
                raise EndSession(f"error:watcher_gone:{w.error or 'thread exited'}", EXIT_ERR)
            if now_ms() - w.heartbeat_ms > stale:
                raise EndSession("error:watcher_stalled", EXIT_ERR)
            if w.lost:
                # the watcher has already stopped the heat; a sampler that merely exited is
                # restarted (lib.sh:147), anything else ends the session
                if not self.sampler_alive() and self.sampler_restarts < MAX_SAMPLER_RESTARTS:
                    self.restart_sampler()
                else:
                    raise EndSession("error:" + w.lost, EXIT_ERR)
            elif not self.sampler_alive():
                self.restart_sampler()
            else:
                st = w.snapshot()
                age = st["age_ms"]
                if age is None or age > stale:
                    raise EndSession(f"error:telemetry_stale:{age}ms", EXIT_ERR)
            if w.skew_seen is not None and not self.fin.get("skew_marked"):
                self.fin["skew_marked"] = w.skew_seen
                self.mark("clock_skew", f"the sampler's t_ms is {w.skew_seen} ms off the host clock")
                self.say(f"the sampler's t_ms is {w.skew_seen} ms off this host's clock: launch "
                         f"times are the host clock, telemetry alignment should use host_ms")
        elif not self.sampler_alive():
            self.restart_sampler()
        # The stop-file is the lab's own way to stop a session from outside (hplib.sh:134-141's
        # session STOP).  Without this check, the heater would keep being launched and would keep
        # returning in ~0.3 s because the file exists (main.cpp:577-580): a storm of truncated
        # device opens instead of a stop.
        if os.path.exists(self.stop_file):
            self.mark("stop_file", f"{where}: STOP exists")
            raise EndSession("safety:stop_file", EXIT_SAFETY)
        if self.cam is not None and self.cam.poll() is not None and not self.fin.get("cam_early"):
            self.fin["cam_early"] = True
            self.fin["cam_rc_early"] = self.cam.returncode
            self.mark("error", f"the camera recorder exited early, rc {self.cam.returncode}")
            self.say(f"the camera recorder exited early (rc {self.cam.returncode}): the rest of "
                     f"this session is not being filmed")
        if self.card_t0 is not None and time.time() - self.card_t0 > self.max_card_s:
            self.mark("cap_card_min", f"{where}: {self.max_card_s / 60:g} min of card time used")
            raise EndSession("done:max_card_min", EXIT_OK)
        wall_cap = self.proto.caps["max_wall_min"] * 60.0
        if self.t_start_ms is not None and (now_ms() - self.t_start_ms) / 1000.0 > wall_cap:
            self.mark("cap_wall_min", f"{where}: {wall_cap / 60:g} min of wall time used")
            raise EndSession("done:max_wall_min", EXIT_OK)

    def card_s(self):
        return 0.0 if self.card_t0 is None else time.time() - self.card_t0

    def on_safety_trip(self, why):
        """Called from the watcher thread: stop the heat first, then let the main loop end."""
        self.touch(self.stop_file)
        self.mark("safety_stop", why)
        self.say(f"SAFETY STOP: {why} (stop-file touched)")

    def on_telemetry_lost(self, why):
        """Also from the watcher thread: unwatched heat is stopped at once, through the same
        stop-file, whatever the main loop then decides (restart, or end the session)."""
        self.touch(self.stop_file)
        self.mark("telemetry_lost", why)
        self.say(f"TELEMETRY LOST: {why} (stop-file touched)")

    def _clear_stop_file(self, why):
        """Remove the stop-file so launching can resume.  Only between launches, and never over a
        safety trip or a signal (hplib.sh:419 clears the run's stop-file the same way)."""
        if (self.watcher is not None and self.watcher.trip) or self.signalled:
            return
        try:
            os.remove(self.stop_file)
            self.mark("stop_file_cleared", why)
        except OSError:
            pass

    # -- launching ----------------------------------------------------------
    def _spawn_heater(self, mask, per_shire):
        """One heater process: timeout 10, stdin /dev/null, explicit --kernel and --stop-file,
        LD_LIBRARY_PATH=/opt/et/lib (hplib.sh:396-409 + lib.sh:100). Never in dry mode.

        The wait is bounded.  `timeout 10` is the device process's hard cap, but it cannot be the
        runner's only one: timeout with no -k waits for ever on a child that blocks SIGTERM or sits
        in an uninterruptible driver call, and a grandchild holding the stdout pipe would hold the
        read open after the child exited.  Either way the main loop would be stuck here with the
        card lock held, no guard() running and no cap enforceable.  So: wait hold10 + a grace, and
        if the process is still there, leave it alone (a device process is never SIGKILLed here,
        lib.sh:9-10), report it and let the session end.
        """
        if self.dry:
            raise RuntimeError("_spawn_heater must never run in dry mode")
        h = self.proto.heater
        cmd = ["timeout", str(HOLD_S), self.heater_bin,
               "--test", h["test"], "--type", h["type"], "--pattern", h["pattern"],
               "--values", h["values"], "--shires", hexmask(mask), "--per-shire", str(per_shire),
               "--seconds", f"{h['seconds']:g}", "--budget", f"{h['budget']:g}",
               "--seed", str(h["seed"]), "--kernel", self.kernel, "--stop-file", self.stop_file]
        env = dict(os.environ, LD_LIBRARY_PATH=ET_LIB)
        # its own session, so a Ctrl-C or a group-wide TERM aimed at this runner cannot signal a
        # device process: the stop-file ends its launch loop, `timeout 10` is the only hard cap
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, text=True, env=env, close_fds=True,
                             cwd=self.root, start_new_session=True)
        self._heater_pids.add(p.pid)
        try:
            out, err = p.communicate(timeout=HOLD_S + HOLD_GRACE_S)
        except subprocess.TimeoutExpired:
            self.touch(self.stop_file)               # ends its launch loop if it is still looping
            self.orphans.append({"pid": p.pid, "cmd": cmd, "t_ms": now_ms()})
            self.mark("error", f"heater pid {p.pid} outlived timeout {HOLD_S} s by "
                               f"{HOLD_GRACE_S} s: left alone, not signalled")
            self.say(f"heater pid {p.pid} is still alive {HOLD_S + HOLD_GRACE_S} s in: `timeout "
                     f"{HOLD_S}` did not end it. Not killing a device process; the session ends "
                     f"now and this pid needs a human (et-who, dmesg).")
            return cmd, None, "", f"outlived timeout {HOLD_S}"
        finally:
            self._heater_pids.discard(p.pid)
        return cmd, p.returncode, out, err

    def launch_once(self, blk, cycle, pidx, ph):
        """One heater launch (or, dry, one sleep of about expected_launch_s), fully recorded."""
        self.launch_n += 1
        n = self.launch_n
        st = self.watcher.snapshot() if self.watcher else {}
        t0 = now_ms()
        if self.dry:
            self.harts_in_flight = ph.harts
            # a launch is a sleep of about the nominal wall; the jitter is around the nominal, not
            # the learnt estimate, so the learning has a stable truth to converge on
            wall = self.proto.heater["expected_launch_s"] + self.rng.uniform(-0.12, 0.12)
            end = time.time() + wall
            while time.time() < end:
                time.sleep(min(0.1, max(0.0, end - time.time())))
                if self.watcher is not None and (self.watcher.trip or self.watcher.lost):
                    break                                 # the stop-file would have ended the loop
            self.harts_in_flight = 0
            cmd, rc, out, err = ["dry-sleep", f"{wall:.3f}"], 0, "", ""
        else:
            cmd, rc, out, err = self._spawn_heater(ph.mask, ph.per_shire)
        t1 = now_ms()
        wall_s = (t1 - t0) / 1000.0
        try:
            os.makedirs(os.path.join(self.rundir, "logs"), exist_ok=True)
            with open(os.path.join(self.rundir, "logs", f"launch-{n}.err"), "w") as f:
                f.write(err)                      # one file per launch, empty when it said nothing
            if out:
                with open(os.path.join(self.rundir, "logs", f"launch-{n}.out"), "w") as f:
                    f.write(out)
        except OSError as e:
            self.mark("error", f"launch {n} log: {e}")
        rec = {"n": n, "block": blk.name, "cycle": cycle, "phase": pidx, "set": ph.set_name,
               "mask": hexmask(ph.mask) if ph.mask is not None else None,
               "per_shire": ph.per_shire, "harts": ph.harts,
               "seconds": self.proto.heater["seconds"], "budget": self.proto.heater["budget"],
               "t_start_ms": t0, "t_end_ms": t1, "wall_s": round(wall_s, 3), "rc": rc,
               "stderr_tail": err[-400:] if err else "",
               "dry": self.dry, "cmd": cmd,
               "die_c": st.get("die_c"), "die_high_c": st.get("die_high_c"),
               "board_w": st.get("board_w"), "mhz_minion": st.get("mhz_minion")}
        # A launch that returned far too quickly did not heat anything: the heater's own --budget
        # cut it (launch.md trap 1), the stop-file exists, or it failed on the way in.  It must not
        # teach the expected wall, and it counts against the strike rule, or a truncating condition
        # turns a 45 s phase into a hundred short device opens.
        short = bool(rc == 0 and wall_s < max(1.0, 0.5 * self.exp_wall))
        rec["short"] = short
        self.jsonl("launches.jsonl", rec)
        rec["bad"] = bool(rc != 0 or short)          # in-memory only: the strike rule's input
        self.launch_wall_s += wall_s
        if not rec["bad"]:
            # the expected launch wall, learnt from the launches already run (EWMA, alpha 0.5)
            self.exp_wall = max(0.5, min(float(HOLD_S), 0.5 * self.exp_wall + 0.5 * wall_s))
        else:
            self.mark("launch_fail", f"launch {n} rc {rc} wall {wall_s:.2f}s: {err[-160:]}",
                      short=short)
            self.say(f"launch {n} rc {rc} after {wall_s:.2f} s: {err[-160:]!r}")
        return rec

    # -- phases, blocks, the session ---------------------------------------
    def idle_until(self, end_ms, where, check_every_s=10.0):
        """Sleep in short steps, still running the safety and other-user checks (hp_edge_wait)."""
        last = 0.0
        while now_ms() < end_ms:
            self.guard(where)
            if time.time() - last >= check_every_s:
                self.check_others(where)
                last = time.time()
            time.sleep(min(0.2, max(0.0, (end_ms - now_ms()) / 1000.0)))
        self.guard(where)

    def _switched_harts(self, blk):
        """A block's dwell-weighted switched harts over its first lap (idle phases count zero)."""
        tot = w = 0.0
        for _, ph in blk.cycle_phases(0):
            d = ph.launches * self.exp_wall if (ph.launches is not None and not ph.idle) else ph.dwell_s
            tot += d * (0 if ph.idle else (ph.harts or 0))
            w += d
        return tot / w if w else 0.0

    def cooldown_gate(self, prev, nxt):
        """Protocol v2's bounded cool-down gate: only where the next block's dwell-weighted switched
        power exceeds the previous block's, wait for the die to drop below enter_below_c, never
        longer than max_gap_s counting the block gap already idled; then proceed and log. Never an
        unbounded wait (lib.sh's wait_free is forbidden here)."""
        g = self.proto.cooldown
        if not g or self.watcher is None:
            return
        try:
            enter = float(g.get("enter_below_c"))
            max_gap = float(g.get("max_gap_s", 75))
        except (TypeError, ValueError):
            return
        hp, hn = self._switched_harts(prev), self._switched_harts(nxt)
        if hn <= hp:
            return
        extra = max(0.0, max_gap - self.proto.block_gap_s)
        t_end = now_ms() + int(extra * 1000)
        t0 = time.time()
        die = self.watcher.snapshot().get("die_c")
        while die is not None and die >= enter and now_ms() < t_end:
            self.idle_until(min(t_end, now_ms() + 1000), f"cool-down before {nxt.name}")
            die = self.watcher.snapshot().get("die_c")
        held = time.time() - t0
        self.mark("cooldown_gate", f"before {nxt.name}: switched harts {hp:.0f} -> {hn:.0f}, die "
                                   f"{die} C, held {held:.1f} s of at most {extra:g} s",
                  enter_below_c=enter, held_s=round(held, 1))
        if held > 0.5:
            self.say(f"cool-down gate before {nxt.name}: held {held:.0f} s, die {die} C")

    def _bloom_gate(self, ph):
        """Protocol v2's full-card per-cycle die gate (safety.bloom_cycle_stop_c, 64 C): before each
        launch of a full-card phase, end the phase early if the die is within a degree of the gate,
        so the one more ~8.5 s launch cannot carry it past the gate and the governor's 65 C step.
        Returns the reason string when the phase must end, else None."""
        lim = self.proto.safety.get("bloom_cycle_stop_c")
        # A full-card phase is one that lights every shire, at any --per-shire: E62 keyed this on 1,024 harts, and
        # amendment A1 ran the full card at 768 (per-shire 24), so the gate never armed and the die reached 69 C.
        if (lim is None or ph.idle or ph.mask is None or popcount(ph.mask) < 32
                or self.watcher is None):
            return None
        die = self.watcher.snapshot().get("die_c")
        if die is not None and die >= lim - 1.0:
            return f"bloom_gate:{die:.1f}C>={lim - 1.0:g}C"
        return None

    def run_phase(self, blk, cycle, pidx, ph, warmup, slot=None):
        where = f"{blk.name} c{cycle} p{pidx} {ph.set_name or 'idle'}"
        t_plan0 = now_ms()
        t_plan1 = t_plan0 + int(round(ph.dwell_s * 1000))
        self.mark("phase_start", where, idle=ph.idle, dwell_s=ph.dwell_s, warmup=warmup,
                  mask=hexmask(ph.mask) if ph.mask is not None else None,
                  launches=ph.launches, slot=slot)
        first = last = None
        n = nfail = nshort = consec_bad = 0
        stopped = None
        truncated = None
        try:
            if ph.idle:
                self.idle_until(t_plan1, where)
            else:
                while True:
                    self.guard(where)
                    if ph.launches is not None:       # protocol v2: exactly this many launches
                        if n >= ph.launches:
                            break
                    elif now_ms() + int(self.exp_wall * 1000) > t_plan1:
                        break
                    gate = self._bloom_gate(ph)
                    if gate:
                        truncated = gate
                        self.mark("phase_truncated", f"{where}: {gate} after {n} launches")
                        self.say(f"{where}: {gate}, ending the on-phase after {n} launches")
                        break
                    self.check_others(where)          # between every launch (rule O1)
                    rec = self.launch_once(blk, cycle, pidx, ph)
                    n += 1
                    nfail += 0 if rec["rc"] == 0 else 1
                    nshort += 1 if rec["short"] else 0
                    consec_bad = consec_bad + 1 if rec["bad"] else 0
                    first = first or rec["t_start_ms"]
                    last = rec["t_end_ms"]
                    if rec["rc"] is None:             # it outlived hold10: nothing more is launched
                        raise EndSession(
                            f"error:heater_overran_hold10:{self.orphans[-1]['pid']}", EXIT_ERR)
                    if consec_bad >= 3:
                        raise EndSession("error:heater_failed_3x", EXIT_ERR)
                self.guard(where)
        except EndSession as e:
            stopped = e.reason
            raise
        finally:
            # The line is written even when the session ends inside the phase, so no launch is left
            # belonging to no phase line (the analyzer indexes launches by block/cycle/phase).
            # The one exception is a launch phase that ran NO launch: a consumer that falls back to
            # the planned span for a missing realised one (analyze_hm.py:119) would then average an
            # unloaded window into that arm.  No line means the analyzer drops the cycle, which is
            # what an arm that never ran deserves; marks.jsonl and blocks.jsonl still record it.
            if ph.idle or n:
                self.jsonl("phases.jsonl", {
                    "block": blk.name, "cycle": cycle, "phase": pidx, "set": ph.set_name,
                    "idle": ph.idle, "planned_start_ms": t_plan0, "planned_end_ms": t_plan1,
                    "t_first_start_ms": first, "t_last_end_ms": last, "n_launches": n,
                    "warmup": warmup, "dwell_s": ph.dwell_s, "n_launch_fail": nfail,
                    "n_launch_short": nshort, "stopped": stopped,
                    "slot": slot, "launches_planned": ph.launches, "truncated": truncated,
                    "mask": hexmask(ph.mask) if ph.mask is not None else None, "harts": ph.harts})
            else:
                self.mark("phase_no_load", f"{where}: no launch ran, so no phases.jsonl line "
                                           f"(the cycle is dropped by the analyzer)")
            self.mark("phase_end", f"{where}: {n} launches"
                                   + (f", stopped: {stopped}" if stopped else ""), n_launches=n)
        return n

    def run_block(self, blk):
        t0 = now_ms()
        cycles = blk.total_laps()
        self.mark("block_start", f"{blk.name}: {cycles} cycles ({blk.warmup_cycles} warmup), "
                                f"order {blk.order}")
        self.say(f"block {blk.name}: {cycles} cycles x {len(blk.phases)} phases, order {blk.order}")
        status, note, n, done = "ok", "", 0, 0
        try:
            for c in range(cycles):
                warmup = c < blk.warmup_cycles
                for slot, (pidx, ph) in enumerate(blk.cycle_phases(c)):
                    n += self.run_phase(blk, c, pidx, ph, warmup, slot=slot)
                done += 1                     # cycles actually completed, not the planned count
        except EndSession as e:
            why = e.reason.split(":")
            status = "stopped:" + (why[1] if why[0] == "done" and len(why) > 1 else why[0])
            note = e.reason
            raise
        except Exception as e:                # the block still gets its line, whatever went wrong
            status, note = "stopped:error", f"{type(e).__name__}: {e}"
            raise
        finally:
            self.jsonl("blocks.jsonl", {"block": blk.name, "t_start_ms": t0, "t_end_ms": now_ms(),
                                        "status": status, "n_launches": n, "n_cycles_run": done,
                                        "n_cycles_planned": cycles,
                                        "warmup_cycles": blk.warmup_cycles, "note": note})
            self.mark("block_end", f"{blk.name}: {status}, {n} launches")
        return n

    def run(self):
        os.makedirs(os.path.join(self.rundir, "logs"), exist_ok=True)
        self.t_start_ms = now_ms()
        try:
            self.preflight()
        except Refuse as e:
            self.say(f"preflight refused: {e}")
            self.mark("error", f"preflight refused: {e}")
            self.notes.append(f"refused: {e}")
            self.stop_reason, self.exit_code = "error:refused", EXIT_REFUSE
            return self.finish()
        self.say(f"RUNDIR {self.rundir}")
        self.say(f"plan: {self.plan['total_min']:.1f} min, {self.plan['launches']} launches, "
                 f"{len(self.blocks)} blocks" + (" [DRY]" if self.dry else ""))
        # A stop-file left by an earlier session would stop every heater at its first launch
        # (hplib.sh:419 rm -f "$RUN_SF"): clear both before anything is started.
        for p in (self.stop_file, self.cam_stop):
            try:
                os.remove(p)
                self.notes.append(f"removed a stale {os.path.basename(p)}")
            except OSError:
                pass
        # the protocol verbatim beside the session, so the RUNDIR stands on its own (reduce_hm.py
        # copies a RUNDIR/protocol.json into the RED when it finds one); byte-for-byte, so its
        # sha256 is session.json's protocol_sha256
        try:
            shutil.copyfile(self.proto.path, os.path.join(self.rundir, "protocol.json"))
        except OSError as e:
            self.mark("error", f"protocol.json copy: {e}")
        self.mark("session_start", f"{self.proto.experiment} {'dry' if self.dry else 'card'}")
        self.fin["et_who"] = self.et_who()
        try:
            # inside the try: a held lock or another user here must end the session cleanly (exit 3
            # with a session.json), not escape as a traceback
            self.check_others("before the session")
            if not self.dry:
                self._take_lock()
            self.card_t0 = time.time()
            if not self.start_sampler(self.plan["total_s"] + SAMPLER_MARGIN_S):
                raise EndSession("error:sampler_did_not_start", EXIT_ERR)
            self.watcher = Watcher(self.tel_raw, self.proto.safety, self.on_safety_trip,
                                   on_lost=self.on_telemetry_lost)
            self.watcher.start()
            t0 = time.time()
            while time.time() - t0 < 15 and self.watcher.snapshot()["recv_ms"] is None:
                time.sleep(0.1)
            if self.watcher.snapshot()["recv_ms"] is None:
                raise EndSession("error:watcher_saw_no_sample", EXIT_ERR)
            if self.watcher.snapshot()["die_recv_ms"] is None:
                raise EndSession("error:telemetry_carries_no_die_temperature", EXIT_ERR)
            self.take_ns_baseline()
            self.start_camera()
            self.check_others("after the sampler")
            if self.proto.pre_idle_s > 0:
                self.mark("pre_idle_start", f"{self.proto.pre_idle_s} s")
                self.say(f"pre-session idle {self.proto.pre_idle_s:g} s (the movies' background)")
                self.idle_until(now_ms() + int(self.proto.pre_idle_s * 1000), "pre-idle")
                self.mark("pre_idle_end", "")
            self.t_pre_idle_end_ms = now_ms()
            for i, blk in enumerate(self.blocks):
                est = next((b["s"] for b in self.plan["blocks"] if b["block"] == blk.name), 0)
                if self.card_s() + est > self.max_card_s:
                    self.jsonl("blocks.jsonl", {"block": blk.name, "t_start_ms": None,
                                                "t_end_ms": None, "status": "skipped:max_card_min",
                                                "n_launches": 0, "n_cycles_run": 0,
                                                "n_cycles_planned": blk.total_laps(),
                                                "warmup_cycles": blk.warmup_cycles,
                                                "note": f"{est:.0f} s would pass the "
                                                        f"{self.max_card_s / 60:g} min card cap"})
                    self.mark("cap_card_min", f"{blk.name} skipped: {est:.0f} s would pass the cap")
                    self.say(f"block {blk.name} skipped: the {self.max_card_s / 60:g} min card cap")
                    continue
                self.run_block(blk)
                if self.proto.block_gap_s > 0 and i < len(self.blocks) - 1:
                    self.mark("block_gap", f"{self.proto.block_gap_s} s")
                    self.idle_until(now_ms() + int(self.proto.block_gap_s * 1000), "block gap")
                if i < len(self.blocks) - 1:
                    self.cooldown_gate(blk, self.blocks[i + 1])
            self.t_post_idle_start_ms = now_ms()
            if self.proto.post_idle_s > 0:
                self.mark("post_idle_start", f"{self.proto.post_idle_s} s")
                self.say(f"post-session idle {self.proto.post_idle_s:g} s")
                self.idle_until(now_ms() + int(self.proto.post_idle_s * 1000), "post-idle")
                self.mark("post_idle_end", "")
            self.stop_reason, self.exit_code = "done", EXIT_OK
        except EndSession as e:
            self.stop_reason, self.exit_code = e.reason, e.code
            if e.reason.startswith("done"):
                self.say(f"session ends: {e.reason}")
            else:
                self.say(f"session ends early: {e.reason} (exit {e.code})")
        except Exception as e:
            self.stop_reason = f"error:{type(e).__name__}:{e}"
            self.exit_code = EXIT_ERR
            self.mark("error", self.stop_reason)
            self.say("unhandled error: " + self.stop_reason)
            import traceback
            traceback.print_exc()
        return self.finish()

    def et_who(self):
        """et-who is read-only and safe to call from a runner (launch.md 2)."""
        if not shutil.which("et-who"):
            return None
        rc, out, err = run_out(["timeout", "10", "et-who"], timeout=15)
        return (out or err).strip()[:400]

    def finish(self):
        """Always runs: stop the heat, the camera and the sampler, write session.json, drop the
        lock.  Every step is wrapped: one failing teardown step must not leave the next undone."""
        self.touch(self.stop_file)             # any heater still in flight ends at its next launch
        if self.watcher is not None:
            self.watcher.disarm()              # the sampler is about to be stopped on purpose
        try:
            self.stop_camera()
        except Exception as e:
            self.say(f"stopping the camera: {e}")
        try:
            self.stop_sampler()          # the watcher keeps watching until the sampler is stopped
        except Exception as e:
            self.say(f"stopping the sampler: {e}")
        try:
            if self.watcher is not None:
                self.watcher.stop_flag.set()
                self.watcher.join(timeout=5)
        except Exception:
            pass
        try:
            self._write_tel()
        except Exception as e:
            self.say(f"writing tel.jsonl: {e}")
        # every file the contract names exists, even for a session that stopped before it wrote
        # one (a refused preflight, an intruder before the first phase): a consumer should find an
        # empty file, not a missing one
        for name in ("launches.jsonl", "phases.jsonl", "blocks.jsonl", "marks.jsonl"):
            try:
                with open(os.path.join(self.rundir, name), "a"):
                    pass
            except OSError:
                pass
        t_end = now_ms()
        self.mark("session_stop", f"{self.stop_reason} (exit {self.exit_code})")
        sess = {
            "experiment": self.proto.experiment,
            "protocol_path": os.path.abspath(self.proto.path),
            "protocol_sha256": sha256_file(self.proto.path),
            "protocol": self.proto.raw,
            "host": socket.gethostname().split(".")[0],
            "user": me_user(),
            "dry": self.dry,
            "argv": sys.argv,
            "python": sys.version.split()[0],
            "root": self.root,
            "git": self.git_head(),
            "sha256": self.hashes(),
            "caps": {"max_card_min": self.max_card_s / 60.0,
                     "max_wall_min": self.proto.caps["max_wall_min"]},
            "t_start_ms": self.t_start_ms,
            "t_end_ms": t_end,
            "stop_reason": self.stop_reason or "error:no_reason",
            "exit_code": self.exit_code,
            "plan": self.plan,
            "pre_idle_s": self.proto.pre_idle_s,
            "post_idle_s": self.proto.post_idle_s,
            "t_pre_idle_end_ms": self.t_pre_idle_end_ms,
            "t_post_idle_start_ms": self.t_post_idle_start_ms,
            "card_s": round(self.card_s(), 1),
            "n_launches": self.launch_n,
            "launch_wall_s": round(self.launch_wall_s, 1),
            "expected_launch_s_final": round(self.exp_wall, 3),
            "safety": self.proto.safety,
            "heater": dict(self.proto.heater, bin=getattr(self, "heater_bin", None),
                           kernel=getattr(self, "kernel", None)),
            "sampler": {"restarts": self.sampler_restarts, "tel_raw": self.tel_raw,
                        "ettelem": getattr(self, "ettelem", None),
                        "args": "sample --every-ms 100 --reset-ms 1000"},
            "camera": {"url": getattr(self, "cam_url", None),
                       "recorder": getattr(self, "record_cam", None),
                       "recorded": bool(self.fin.get("cam_recorded")),
                       "pid": self.fin.get("cam_pid"), "rc": self.fin.get("cam_rc"),
                       "exited_early": bool(self.fin.get("cam_early")),
                       "rc_early": self.fin.get("cam_rc_early"),
                       "cmd": self.fin.get("cam_cmd")},
            "watcher": {"trip": self.watcher.trip if self.watcher else None,
                        "lost": self.watcher.lost if self.watcher else None,
                        "error": self.watcher.error if self.watcher else None,
                        "clock_skew_ms": self.watcher.skew_seen if self.watcher else None,
                        "samples": self.watcher.snapshot()["n"] if self.watcher else 0,
                        "bad_samples": self.watcher.snapshot()["bad"] if self.watcher else 0,
                        "no_die_samples": self.watcher.snapshot()["no_die"] if self.watcher else 0,
                        "last": self.watcher.snapshot() if self.watcher else None},
            "orphans": self.orphans,     # device processes that outlived hold10: never signalled
            "etiquette": {"checks": len(self.checks), "use_count_baseline": self.ns_baseline,
                          "hits": [c for c in self.checks if c["hits"]],
                          "lock": None if self.dry else LOCK_PATH},
            "et_who": self.fin.get("et_who"),
            "notes": self.notes,
        }
        try:
            tmp = os.path.join(self.rundir, "session.json.tmp")
            with open(tmp, "w") as f:
                json.dump(sess, f, indent=1, sort_keys=False, default=str)
                f.write("\n")
            os.replace(tmp, os.path.join(self.rundir, "session.json"))
        except (OSError, TypeError, ValueError) as e:
            print(f"session.json could not be written: {e}", file=sys.stderr)
            self.exit_code = self.exit_code or EXIT_ERR
        finally:
            # the lock goes last and always: nothing below it may be able to raise first
            self.say(f"stop_reason {self.stop_reason}, {self.launch_n} launches, "
                     f"{self.card_s() / 60:.1f} min of card time -> exit {self.exit_code}")
            if self.orphans:
                self.say(f"LEFT BEHIND: {len(self.orphans)} device process(es) that outlived "
                         f"timeout {HOLD_S}: {[o['pid'] for o in self.orphans]} - check et-who")
            with self._io_lock:
                for f in self._f.values():
                    try:
                        f.close()
                    except OSError:
                        pass
                self._f.clear()
            self._release_lock()
        return self.exit_code

    def _write_tel(self):
        """The sampler's JSON lines into tel.jsonl, wrapped as {host_ms, line} only if the sampler
        did not stamp its own host time (INTERFACES.md). lib.sh:174 does the same filter."""
        src, dst = self.tel_raw, os.path.join(self.rundir, "tel.jsonl")
        n = 0
        open(dst, "a").close()          # the contract's file exists even for a session that stopped
        if not os.path.exists(src):     # before the sampler started (no telemetry to carry over)
            self.say("tel.jsonl: 0 samples (the sampler never wrote)")
            return
        try:
            with open(src, "rb") as fi, open(dst, "ab") as fo:
                for ln in fi:
                    ln = ln.strip()
                    if not ln.startswith(b"{"):
                        continue
                    try:
                        o = json.loads(ln.decode("utf-8", "replace"))
                    except ValueError:
                        continue
                    if "t_ms" in o:
                        fo.write(ln + b"\n")
                    else:
                        fo.write((json.dumps({"host_ms": now_ms(),
                                              "line": ln.decode("utf-8", "replace")}) + "\n").encode())
                    n += 1
        except OSError as e:
            self.say(f"tel.jsonl: {e}")
        self.say(f"tel.jsonl: {n} samples")
        try:
            os.remove(src)
        except OSError:
            pass

    def git_head(self):
        rc, out, _ = run_out(["git", "-C", self.root, "rev-parse", "HEAD"])
        head = out.strip() if rc == 0 else None
        rc2, out2, _ = run_out(["git", "-C", self.root, "status", "--porcelain"])
        return {"head": head, "dirty_files": len(out2.splitlines()) if rc2 == 0 else None}

    def hashes(self):
        h = {k: (sha256_file(p) if p else None) for k, p in
             (("heater", getattr(self, "heater_bin", None)),
              ("kernel", getattr(self, "kernel", None)),
              ("ettelem", getattr(self, "ettelem", None)),
              ("record_cam", getattr(self, "record_cam", None)))}
        for name in sorted(os.listdir(self.code_dir)):
            if name.endswith((".py", ".md", ".json")):
                h["hm/" + name] = sha256_file(os.path.join(self.code_dir, name))
        return h


# ---------------------------------------------------------------------------- cli


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(d, ".git")):
            return d
        p = os.path.dirname(d)
        if p == d:
            return os.path.abspath(start)
        d = p


def print_plan(proto, plan, blocks, max_card_min):
    w = max([len(b.name) for b in blocks] + [5])
    print(f"{proto.experiment}: {len(blocks)} blocks, {plan['launches']} launches, "
          f"{plan['total_min']:.1f} min of card time (cap {max_card_min:g} min), "
          f"expected launch {plan['expected_launch_s']:.2f} s")
    print(f"  pre-session idle {proto.pre_idle_s:g} s; post-session idle {proto.post_idle_s:g} s; "
          f"block gap {proto.block_gap_s:g} s")
    print(f"  {'block'.ljust(w)}  cyc+wu  order      min  launches  phases")
    for b, pb in zip(blocks, plan["blocks"]):
        ph = " ".join(f"{p['set'] or 'idle'}:{p['dwell_s']:g}s" for p in pb["phases"])
        print(f"  {b.name.ljust(w)}  {b.cycles:3d}+{b.warmup_cycles:<2d}  {b.order:<9s} "
              f"{pb['s'] / 60:5.1f}  {pb['launches']:8d}  {ph}")
    for s in sorted(proto.sets.values(), key=lambda s: s["name"]):
        if s["idle"]:
            print(f"  set {s['name']:<8s} idle")
        else:
            print(f"  set {s['name']:<8s} {hexmask(s['mask'])}  {popcount(s['mask']):2d} shires x "
                  f"{s['per_shire']:2d} = {s['harts']:4d} harts")
    print(f"  safety: abs_stop_c {proto.safety['abs_stop_c']:g} C, board_cap_w "
          f"{proto.safety['board_cap_w']:g} W, {proto.safety['cap_consecutive']} consecutive samples")


def main(argv=None):
    ap = argparse.ArgumentParser(description="E62 heat-movie session runner", add_help=True)
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--out", help="RUNDIR (required unless --list)")
    ap.add_argument("--dry", action="store_true",
                    help="no device access at all: no lock, no heater, no ettelem (the camera is "
                         "still recorded)")
    ap.add_argument("--only", nargs="+", metavar="BLOCK", help="run only these blocks")
    ap.add_argument("--max-card-min", type=float, default=None,
                    help="cap the session's card time (default: the protocol's caps.max_card_min)")
    ap.add_argument("--list", action="store_true", help="print the plan and the estimate; touch nothing")
    ap.add_argument("--cam-url", default=None, help="the camera's /stream.raw.z URL")
    ap.add_argument("--no-cam", action="store_true", help="run without the camera recorder")
    ap.add_argument("--root", default=None, help="the tree the binaries and git HEAD come from")
    ap.add_argument("--allow-short-phases", action="store_true",
                    help="allow a launch phase shorter than one launch (it will run none)")
    ap.add_argument("--force", action="store_true", help="overwrite a RUNDIR that already has a session")
    ap.add_argument("--json", action="store_true", help="with --list: print the plan as JSON")
    a = ap.parse_args(argv)
    a.root = a.root or find_root(os.path.dirname(os.path.abspath(__file__)))

    try:
        with open(a.protocol) as f:
            raw = json.load(f)
    except (OSError, ValueError) as e:
        print(f"protocol {a.protocol}: {e}", file=sys.stderr)
        return EXIT_REFUSE
    proto = Protocol(raw, a.protocol)
    problems = proto.check(allow_short_phases=a.allow_short_phases)
    if a.only:
        known = {b.name for b in proto.blocks}
        for n in a.only:
            if n not in known:
                problems.append(f"--only names unknown block {n!r}")
    if problems:
        print("protocol refused:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        return EXIT_REFUSE
    blocks = proto.ordered_blocks(a.only)
    if not blocks:
        print("no blocks to run", file=sys.stderr)
        return EXIT_REFUSE
    plan = estimate(proto, blocks, proto.heater["expected_launch_s"])
    max_card_min = a.max_card_min if a.max_card_min is not None else proto.caps["max_card_min"]

    if a.list:
        if a.json:
            print(json.dumps({"plan": plan, "max_card_min": max_card_min,
                              "sets": {k: {"mask": None if v["idle"] else hexmask(v["mask"]),
                                           "harts": v["harts"], "idle": v["idle"]}
                                       for k, v in proto.sets.items()}}, indent=1))
        else:
            print_plan(proto, plan, blocks, max_card_min)
        return EXIT_OK
    if not a.out:
        print("--out RUNDIR is required unless --list", file=sys.stderr)
        return EXIT_REFUSE

    os.makedirs(a.out, exist_ok=True)
    s = Session(a, proto, blocks, plan)

    def on_signal(sig, frame):
        # Only os-level work here: the flag and the stop-file (which ends an in-flight heater at its
        # next ~0.5 s launch boundary). The mark and the clean teardown are the main loop's.
        s.signalled = sig
        try:
            with open(s.stop_file, "a"):
                pass
        except OSError:
            pass

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        try:
            signal.signal(sig, on_signal)
        except (OSError, ValueError):
            pass
    return s.run()


if __name__ == "__main__":
    sys.exit(main())
