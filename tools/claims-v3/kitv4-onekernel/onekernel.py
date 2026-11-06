#!/usr/bin/env python3
"""Kit v4's one-kernel-per-burst option (README.md here): each work process of a burst runs as ONE kernel, so no gap opens inside
the burst and the governor's idle reset has nothing to fall into (E100's N arm: 0 falls in 126 heartbeats inside kernels).

The host already does this: `sparsity_host --seconds 0 --iters N` runs only its first launch (workloads/sparsity/host/main.cpp
repeatFor, "if (o.sysemu || o.seconds <= 0) return;"), and the C-logging host keeps that loop (ccheck/patch_host_ccheck.py patches
the launch's body, not repeatFor). Every launch waits at most 6 s on silicon (main.cpp Session::launch, timeoutS = 6) before the
host aborts the stream, so N is sized to finish in 5.5 s even if the clock never leaves the 600 MHz boot point.

    import onekernel as OK
    OK.iters_for("fp32")                  6,043,956 iterations: 5.5 s at 600 MHz, about 4.1-4.4 s at the 800 MHz cap
    OK.command(v3_cmd, "fp32")            a v3 burst command with --seconds X replaced by --seconds 0 --iters N
    OK.install(H)                         run_hpl (H) spawns every WORK process as one kernel; heaters and gates unchanged;
                                          --dry simulates the one kernel on run_hpl's toy card (one SPARSITY line)
    OK.burst_extra_v4(m, procs, B)        reduce_kspeed.burst_extra, plus the window's rate from the sampled clock: with one
                                          kernel no launch starts 1.5 s in, so burst_rate and burst_ghz_kernel read None

No file of a v3 kit and no committed runner is edited: install() patches the imported run_hpl module in memory only, after
checking it is the committed file. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CPO = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}     # cycles per TensorFMA op (surface_hpl.py CYC; E173-E175's records)
OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}      # operations per op (reduce_hpl OPS)
HOST_TIMEOUT_S = 6.0      # main.cpp: a launch waits at most 6 s on silicon, then the host aborts the stream
FLOOR_MHZ = 600.0         # the boot point, and the lowest point the governor sets
T600_S = 5.5              # the kernel must finish in 5.5 s at 600 MHz: 0.5 s under the host's 6 s
RUN_HPL_SHA256 = "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227"   # tools/claims-v3/hpl/run_hpl.py at 1a899d8f


def iters_for(typ, t600_s=T600_S):
    """The iterations of one kernel that ends in t600_s seconds at 600 MHz (the worst case: the clock never climbs)."""
    if t600_s >= HOST_TIMEOUT_S:
        raise ValueError(f"t600_s {t600_s} is not under the host's {HOST_TIMEOUT_S} s launch timeout")
    return int(math.floor(t600_s * FLOOR_MHZ * 1e6 / CPO[typ]))


def wall_at(typ, n, first_beat_s=0.5, c7=0.12, c8=0.31, cap_mhz=800.0):
    """The kernel's wall time if the clock sits at 600 MHz until the first heartbeat inside it, 700 MHz for c8 - c7, then
    cap_mhz (the climb of the dip term's state machine, aifoundry2's c7 and c8)."""
    cyc = n * CPO[typ]
    seg = [(first_beat_s + c7, 600.0), (c8 - c7, 700.0)]
    t = 0.0
    for d, f in seg:
        c = d * f * 1e6
        if cyc <= c:
            return t + cyc / (f * 1e6)
        cyc -= c
        t += d
    return t + cyc / (cap_mhz * 1e6)


def command(cmd, typ, n=None):
    """A v3 burst command (run_hpl's spawn_kernel form) as one kernel: --seconds <x> becomes --seconds 0 and --iters <n> is
    added after it. Refuses a command that already names --iters or lacks --seconds, --budget or --stop-file."""
    n = n if n is not None else iters_for(typ)
    cmd = list(cmd)
    if "--iters" in cmd:
        raise ValueError("refused: the command already names --iters")
    for flag in ("--seconds", "--budget", "--stop-file", "--type"):
        if flag not in cmd:
            raise ValueError(f"refused: the command has no {flag}")
    if cmd[cmd.index("--type") + 1] != typ:
        raise ValueError("refused: the command's --type is not the one sized for")
    i = cmd.index("--seconds")
    cmd[i + 1] = "0"
    cmd[i + 2:i + 2] = ["--iters", str(int(n))]
    return cmd


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def install(H):
    """Replace H.Session.spawn_kernel so that a WORK launch (no override arguments) runs as one kernel. A heater or gate
    launch (values, seconds or the type given) goes to the original method unchanged. Idempotent. Refuses a run_hpl that is
    not the committed file."""
    S = H.Session
    if getattr(S, "_onekernel", False):
        return record(H)
    got = _sha(H.__file__)
    if got != RUN_HPL_SHA256:
        raise RuntimeError(f"onekernel: {H.__file__} is not the committed run_hpl.py (sha256 {got[:12]}): nothing installed")
    orig = S.spawn_kernel

    def spawn_kernel(self, r, values=None, seconds=None, budget=None, mask=None, per_shire=None, typ=None):
        if any(x is not None for x in (values, seconds, budget, mask, per_shire, typ)):
            return orig(self, r, values=values, seconds=seconds, budget=budget, mask=mask, per_shire=per_shire, typ=typ)
        n = iters_for(r.type)
        base = ["timeout", str(H.HOLD_S), self.heater, "--test", "fma", "--type", r.type, "--pattern", "none",
                "--values", r.values, "--shires", f"0x{r.mask:08x}", "--per-shire", str(r.per_shire),
                "--seconds", f"{r.seconds:g}", "--budget", f"{r.budget:g}", "--seed", str(r.seed), "--kernel", self.kernel,
                "--stop-file", self.stop_file]
        cmd = command(base, r.type, n)
        t0 = H.now_ms()
        if self.dry:
            frac = r.per_shire * bin(r.mask).count("1") / 1024.0
            self.card.set_busy(True, r.values, frac)
            need = n * CPO[r.type]
            cyc, a0, ts = 0.0, H.now_ms(), time.time()
            last = ts
            while cyc < need and time.time() - ts < HOST_TIMEOUT_S:
                time.sleep(0.02)
                now = time.time()
                f = self.card.PTS[self.card.pt][0]
                cyc += f * 1e6 * (now - last)
                last = now
            wall = time.time() - ts
            ok = cyc >= need
            self.card.set_busy(False)
            rec = {"test": "fma", "type": r.type, "values": r.values, "minions": r.minions, "iters": n, "launch": -1,
                   "cycles_max": int(min(cyc, need)), "cycles_per_op": CPO[r.type], "wall_s": round(wall, 6),
                   "t_start_ms": a0, "t_end_ms": H.now_ms(), "ghz": round(min(cyc, need) / wall / 1e9, 4), "ok": ok,
                   "result": "unchecked"}
            err = "" if ok else "kernel did not finish within 6 s, aborting the stream\n"
            return cmd, 0 if ok else 1, "SPARSITY " + json.dumps(rec), err, t0, H.now_ms()
        env = dict(os.environ, LD_LIBRARY_PATH=H.ET_LIB)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
                             text=True, env=env, close_fds=True, cwd=self.root, start_new_session=True)
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

    S.spawn_kernel = spawn_kernel
    S._onekernel = True
    return record(H)


def record(H):
    return {"option": "one kernel per burst", "file": "tools/claims-v3/kitv4-onekernel/onekernel.py",
            "onekernel_sha256": _sha(os.path.abspath(__file__)), "run_hpl_sha256": _sha(H.__file__),
            "installed": bool(getattr(H.Session, "_onekernel", False)), "t600_s": T600_S,
            "iters": {t: iters_for(t) for t in CPO}}


def burst_extra_v4(m, procs, B, rk=None):
    """reduce_kspeed.burst_extra (rk) unchanged, with the one-kernel fields beside it: launches in the window, gaps in the
    window, the window's rate from the sampled clock (minions x ops per op / cycles per op x burst_mhz), and the one
    kernel's own whole-kernel clock (cycles over wall, the climb included)."""
    if rk is None:
        import sys
        sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
        import reduce_kspeed as rk  # noqa: E402
    out = rk.burst_extra(m, procs, B)
    work = [p for p in procs if p.get("role") == "work"]
    L = sorted((k for p in work for k in p.get("sparsity", []) if k.get("t_start_ms")), key=lambda k: k["t_start_ms"])
    t0 = min((p["t_start_ms"] for p in work), default=None)
    t1 = max((p["t_end_ms"] for p in work), default=None)
    w0 = t0 + rk.BURST_FROM_S * 1000 if t0 is not None else None
    inwin = [k for k in L if w0 is not None and k["t_end_ms"] > w0]
    gaps = [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(L, L[1:]) if w0 is not None and b["t_start_ms"] > w0]
    out["v4_one_kernel"] = len(L) == len(work)
    out["v4_launches_in_window"] = len(inwin)
    out["v4_gaps_in_window"] = len(gaps)
    typ = m.get("type")
    mhz = out.get("burst_mhz")
    out["v4_burst_rate_from_clock"] = (round(m.get("minions", 1024) * OPS[typ] / CPO[typ] * mhz * 1e6 / 1e12, 3)
                                       if (mhz and typ in CPO) else None)
    cyc = sum(k.get("cycles_max", 0) for k in L)
    wall = sum(k.get("wall_s", 0) for k in L)
    out["v4_whole_kernel_ghz"] = round(cyc / wall / 1e9, 4) if wall else None
    out["v4_work_s"] = round((t1 - t0) / 1000.0, 3) if t0 is not None else None
    return out
