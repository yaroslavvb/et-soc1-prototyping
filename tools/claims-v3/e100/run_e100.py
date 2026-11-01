#!/usr/bin/env python3
"""E100 (Q132): the session runner. It IS E80's runner, ../kspeed/run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus `file:` tiles checked against
kinds.json), imported and run unchanged, with these additions and nothing else:

  1. a run's launch may carry `fixed_iters`, `gap_ms` or `one_kernel_iters`, which become the patched host's --fixed-iters and --gap-ms (a random sleep after each kernel,
     uniform in 0 to 2 x gap_ms), or `--seconds 0 --iters N`: one kernel and nothing else (host-gap.patch; the kernel ELF is the same file);
  2. a run may carry `sampler_reset_ms`, which adds `--reset-ms` to the sampler (arm R only; allowed by the owner's ruling of 31 October 2026; zeros
     at 35 W never meet the power loop, the reason other runs sample without it);
  3. a seeded random pause before every process of a run but its first, so no process keeps one phase against the 1 s heartbeat; each is a mark;
  4. the slot: --slot-start and --slot-end (epoch seconds). No launch before the start. A run that could not finish, read and release 60 s before the end is
     not started, and a process is not started in the last 60 s: the session ends "done:slot_end", exit 0, with the end queries inside the slot.

Everything else that touches the card is run_hpl.py's own code: the non-blocking card lock held for the session, the other-user checks before every launch
process, `timeout 10` on every device process, the trace ring, residencies and `ettelem config` after every run with the sampler stopped, the safety stops (85 C; 97 W
on three samples), the end of the session unless the TDP and the threshold read back 65. Nothing is set on the card.

    python3 run_e100.py --protocol protocol.json --out <RUNDIR> --slot-start S --slot-end E [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import random
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# On the box this file runs from build/e100/code/, so the shared tree is not touched: E100_ROOT names the checkout whose kspeed and hpl runners it imports.
sys.path.insert(0, os.path.join(os.environ.get("E100_ROOT") or os.path.join(HERE, "..", "..", ".."), "tools", "claims-v3", "kspeed"))
import run_kspeed as K  # noqa: E402

H = K.H
SLOT = {"start": None, "end": None}
RESERVE_S = 60.0
_base_init = H.Run.__init__
_base_spawn = H.Session.spawn_kernel
_base_run_one = H.Session.run_one
_base_start_sampler = H.Session.start_sampler
PROTO = {}
PAUSE_RNG = [random.Random(100)]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _init(self, block, idx, rep, cfg, bdefaults):
    _base_init(self, block, idx, rep, cfg, bdefaults)
    g = dict(bdefaults)
    g.update(cfg)
    la = g.get("launch") or {}
    self.fixed_iters = la.get("fixed_iters")
    self.gap_ms = la.get("gap_ms")
    self.one_kernel_iters = la.get("one_kernel_iters")
    self.reset_ms = g.get("sampler_reset_ms")


def _slot_check(sess, where, need_s=0.0):
    now = time.time()
    if SLOT["start"] and now < SLOT["start"]:
        raise H.EndSession(f"error:before_slot:{where}", H.EXIT_ERR)
    if SLOT["end"] and now + need_s > SLOT["end"] - RESERVE_S:
        sess.mark("slot_end", f"{where}: {now + need_s:.0f} > {SLOT['end'] - RESERVE_S:.0f}")
        raise H.EndSession("done:slot_end", H.EXIT_OK)


def _spawn(self, r, values=None, seconds=None, budget=None, mask=None, per_shire=None, typ=None):
    _slot_check(self, r.name)
    # (3) a pause before every process of a run but its first
    if getattr(self, "_procs_in_run", 0) > 0:
        lo, hi = PROTO.get("pause_s", [0.0, 1.0])
        s = PAUSE_RNG[0].uniform(lo, hi)
        self.mark("pause", f"{s:.3f}")
        time.sleep(s)
    self._procs_in_run = getattr(self, "_procs_in_run", 0) + 1
    if self.dry:
        return _base_spawn(self, r, values, seconds, budget, mask, per_shire, typ)
    cmd = ["timeout", str(H.HOLD_S), self.heater, "--test", "fma", "--type", typ or r.type, "--pattern", "none",
           "--values", values or r.values, "--shires", f"0x{(mask or r.mask):08x}", "--per-shire", str(per_shire or r.per_shire)]
    if r.one_kernel_iters:
        cmd += ["--seconds", "0", "--iters", str(int(r.one_kernel_iters))]
    else:
        cmd += ["--seconds", f"{seconds or r.seconds:g}"]
        if r.fixed_iters:
            cmd += ["--fixed-iters", str(int(r.fixed_iters))]
        if r.gap_ms:
            cmd += ["--gap-ms", f"{r.gap_ms:g}"]
    cmd += ["--budget", f"{budget or r.budget:g}", "--seed", str(r.seed), "--kernel", self.kernel, "--stop-file", self.stop_file]
    t0 = H.now_ms()
    env = dict(os.environ, LD_LIBRARY_PATH=H.ET_LIB)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, text=True, env=env, close_fds=True, cwd=self.root, start_new_session=True)
    self.heater_pids.add(p.pid)
    try:
        out, err = p.communicate(timeout=H.HOLD_S + H.HOLD_GRACE_S)
    except subprocess.TimeoutExpired:
        self.touch(self.stop_file)
        self.mark("error", f"kernel pid {p.pid} outlived timeout {H.HOLD_S} s: left alone")
        raise H.EndSession(f"error:kernel_overran_hold10:{p.pid}", H.EXIT_ERR)
    finally:
        self.heater_pids.discard(p.pid)
    return cmd, p.returncode, out, err, t0, H.now_ms()


def _run_one(self, r, k, n):
    # (4) a run that could not finish before the reserve is not started: its planned length with a gate and the queries
    need = r.processes * (r.seconds + 1.2 + 1.0) + r.tail_s + 15.0
    _slot_check(self, r.name, need)
    self._cur_run = r
    self._procs_in_run = 0
    return _base_run_one(self, r, k, n)


def _start_sampler(self, path, seconds):
    r = getattr(self, "_cur_run", None)
    if self.dry or r is None or not r.reset_ms:
        return _base_start_sampler(self, path, seconds)
    # (2) run_hpl's start_sampler with one more flag, the first attempt's shape and its six tries
    self.watcher.follow(path)
    env = dict(os.environ, LD_LIBRARY_PATH=H.ET_LIB)
    for attempt in range(1, 7):
        since = os.path.getsize(path) if os.path.exists(path) else 0
        out = open(path, "ab", buffering=0)
        try:
            self.sampler = subprocess.Popen([self.ettelem, "sample", "--seconds", str(int(seconds)), "--every-ms", str(self.every_ms), "--reset-ms", str(int(r.reset_ms))],
                                            stdout=out, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env, close_fds=True, cwd=self.root, start_new_session=True)
        finally:
            out.close()
        t0 = time.time()
        while time.time() - t0 < 10:
            try:
                with open(path, "rb") as f:
                    f.seek(since)
                    if b"{" in f.read(8192):
                        self.mark("sampler_start", f"attempt {attempt}, pid {self.sampler.pid}, reset_ms {r.reset_ms}")
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


H.Run.__init__ = _init
H.Session.spawn_kernel = _spawn
H.Session.run_one = _run_one
H.Session.start_sampler = _start_sampler


def main():
    argv = list(sys.argv)
    for flag, key in (("--slot-start", "start"), ("--slot-end", "end")):
        if flag in argv:
            i = argv.index(flag)
            SLOT[key] = float(argv[i + 1])
            del argv[i:i + 2]
    sys.argv = argv
    if "--list" not in argv and not (SLOT["start"] and SLOT["end"]):
        print("refused: --slot-start and --slot-end are required", file=sys.stderr)
        return H.EXIT_REFUSE
    if "--protocol" in argv:
        PROTO.update(json.load(open(argv[argv.index("--protocol") + 1])))
        PAUSE_RNG[0] = random.Random(PROTO.get("pause_seed", 100))
    if "--dry" in argv:
        H.DryCard.DYN600["file:tools/claims-v3/kinds/tiles/int8/zeros.bin"] = 2.1
    if "--out" in argv and "--list" not in argv:
        rd = os.path.abspath(argv[argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            pr = argv[argv.index("--protocol") + 1]
            json.dump({"experiment": "E100", "wrapper": "tools/claims-v3/e100/run_e100.py", "wrapper_sha256": sha256(__file__), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions.json")), "patch_sha256": sha256(os.path.join(HERE, "host-gap.patch")),
                       "run_kspeed_sha256": sha256(K.__file__), "slot": SLOT, "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": argv},
                      open(os.path.join(rd, "e100.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
