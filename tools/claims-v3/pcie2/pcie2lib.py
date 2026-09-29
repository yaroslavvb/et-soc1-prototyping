#!/usr/bin/env python3
"""PCIE2 (hub rungs 34 and 35): the helpers block.sh calls. No device access anywhere in this file.

    pcie2lib.py plan --pass P [--smoke]          the pass's device processes, one JSON line each, in run order
    pcie2lib.py telsum FILE                      "<hottest die C> <minion MHz>" from an ettelem sample (or "none")
    pcie2lib.py stub <pciebench_host args>       V3_DRY's stand-in for pciebench_host: synthetic PCIE lines

The stub follows a model chosen by the environment, so the whole chain (block, check, reduction, verdicts) can be
exercised off the card: PCIE2_DRY_R35 = B (default: a rate that halves while two H2D commands overlap), A (a fixed
cost per overlapping command), E (the loss sets in only after a long overlap), X (elements, not commands, overlap);
PCIE2_DRY_CMD_MS (default 0.15): each command's device-side fixed cost, paid in turn with the barrier and overlapped
when two are in flight (the review's case against h(1)); PCIE2_DRY_R34 = A (default: host writes through the L3 homes,
allocating), B (through the homes, no allocation), C (to the memory shires, the L3 copy invalidated), D (to the memory
shires, stale L3 copies), N (as A, but the flush launch does not empty the L3: the instrument's own failure, which
the reduction must call invalid). PCIE2_DRY_FAIL=conc|touch makes that test fail (exit 1, message PCIE2_DRY_FAILMSG);
PCIE2_DRY_HANG=conc|touch makes it exit 124, as `timeout 10` would. Its numbers are invented from the 27 September
data and E36's latencies; they are never data.
"""
import json
import math
import os
import random
import sys
import zlib

# ---- the plan ------------------------------------------------------------------------------------------------------
# R35: 2 commands of N MB per stream (k = 2), DMA-only (the API's no-op bounce copy), five configurations per process:
# h2d and d2h with both commands in flight, the same with the barrier (one in flight), and two streams with one each.
CONC_CFGS = "h2d,h2d/ser,d2h,d2h/ser,2xh2d/ser"
# (MB per command, elements per command: 0 = the plain call, E >= 1 = a MemcpyList of E elements, trials)
CONC_SWEEP = [(1, 0, 25), (4, 0, 25), (16, 0, 11), (64, 0, 9), (64, 1, 9), (64, 8, 9), (16, 8, 11), (4, 8, 25),
              (1, 8, 25)]
TOUCH = {"touch_mb": 4, "lines": 4096, "reps": 5}
SMOKE_CONC = [(1, 0, 3), (64, 8, 1)]
SMOKE_TOUCH = {"touch_mb": 4, "lines": 512, "reps": 1}
TEL_AFTER = 5          # a telemetry sample (the 90 C gate) after this many processes, and before and after the pass


def plan(pass_no, smoke):
    procs = []
    sweep, touch = (SMOKE_CONC, SMOKE_TOUCH) if smoke else (CONC_SWEEP, TOUCH)
    for mb, el, trials in sweep:
        procs.append({"id": f"conc-{mb}m-e{el}", "kind": "conc", "mb": mb, "elements": el, "trials": trials,
                      "args": ["--test", "conc", "--copy", "dma", "--cfgs", CONC_CFGS, "--mb", str(mb),
                               "--elements", str(el), "--trials", str(trials), "--shuffle", "--seed", str(pass_no),
                               "--budget", "8.5"]})
    procs.append({"id": "touch", "kind": "touch", **touch,
                  "args": ["--test", "touch", "--touch-mb", str(touch["touch_mb"]), "--lines", str(touch["lines"]),
                           "--reps", str(touch["reps"]), "--seed", str(pass_no), "--budget", "8.5"]})
    if not smoke:
        random.Random(1000 + pass_no).shuffle(procs)   # a new order per pass, the same on every card
    return procs


# ---- telemetry -----------------------------------------------------------------------------------------------------
def telsum(path):
    """The hottest current die reading (minion shires, I/O shire, PMIC) and the minion clock, from the last JSON line."""
    last = None
    try:
        with open(path) as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("{"):
                    last = json.loads(ln)
    except (OSError, ValueError):
        last = None
    if not last or "temp_c" not in last:
        return "none"
    t = last["temp_c"]
    hot = max([(t.get(k) or [0])[0] for k in ("minshire", "ioshire")] + [t.get("pmic", 0)])
    if not hot or hot <= 0:
        return "none"      # a sample with no die in it is no reading: the 90 C gate cannot pass on it
    mhz = (last.get("mhz") or {}).get("minion", 0)
    return f"{math.ceil(hot)} {round(mhz or 0)}"   # whole numbers for the shell's tests (rounded up: the gate's side)


# ---- the DRY stub --------------------------------------------------------------------------------------------------
def _args(argv):
    o = {"test": "bw", "mb": 64, "elements": 0, "trials": 3, "cfgs": "", "seed": 1, "touch_mb": 4, "lines": 4096,
         "reps": 5, "copy": "both"}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--shuffle", "--verify"):
            i += 1
            continue
        k = a.lstrip("-").replace("-", "_")
        v = argv[i + 1]
        o[k] = v if k in ("test", "cfgs", "copy") else int(float(v))
        i += 2
    return o


def _emit(t_ms, body):
    print("PCIE " + json.dumps({"t_ms": t_ms, **body}, separators=(",", ":")))


def stub_conc(o, rng, t_ms):
    model = os.environ.get("PCIE2_DRY_R35", "B")
    n = o["mb"] << 20
    k = 2
    B1, D1, HALF, D2GAIN, PAIR = 12.4e9, 10.4e9, 0.49, 1.08, 11.2e-3
    F = 0.25e-3                                  # the fixed part of a trial, in s
    C = float(os.environ.get("PCIE2_DRY_CMD_MS", "0.15")) * 1e-3   # a command's device-side fixed part, in s
    el = o["elements"]
    # configuration -> (h2d?, streams, commands in flight at once)
    shape = {"h2d/ser": (True, 1, 1), "d2h/ser": (False, 1, 1), "h2d": (True, 1, 2), "d2h": (False, 1, 2),
             "2xh2d/ser": (True, 2, 2), "2xd2h/ser": (False, 2, 2), "2xh2d": (True, 2, 4), "2xd2h": (False, 2, 4)}
    cfgs = o["cfgs"].split(",") if o["cfgs"] else list(shape)

    def trial_s(h2d, streams, inflight):
        tot = k * n * streams                    # bytes the trial moves
        cmds = k * streams
        if inflight == 1:
            rate = (B1 if h2d else D1) * (HALF if (model == "X" and h2d and el >= 2) else 1)
            return F + cmds * C + tot / rate
        if not h2d:
            return F + C * streams + tot / (D1 * D2GAIN)
        if model == "A":                         # the serial time plus a fixed loss per overlapping pair
            return F + cmds * C + tot / B1 + PAIR * cmds / 2
        if model == "E":                         # full rate until 16 MB have moved in overlap, then half
            onset = 16 << 20
            return F + C * streams + min(tot, onset) / B1 + max(0, tot - onset) / (B1 * HALF)
        rate = B1 * HALF * (HALF if (model == "X" and el >= 2) else 1)
        return F + C * streams + tot / rate

    for trial in range(o["trials"]):
        for cfg in cfgs:
            h2d, streams, inflight = shape[cfg]
            wall = int(trial_s(h2d, streams, inflight) * math.exp(rng.gauss(0, 0.01)) * 1e9)
            _emit(t_ms, {"test": "conc", "trial": trial, "copy": "dma", "cfg": cfg, "legs": streams,
                         "bytes_per_leg": n * k, "leg_ns": [wall - rng.randint(0, 20000) for _ in range(streams)],
                         "wall_ns": wall, "stream_errors": 0, "mb": o["mb"], "cmds_per_leg": k, "elements": el})


def stub_touch(o, rng, t_ms):
    model = os.environ.get("PCIE2_DRY_R34", "A")
    nl = (o["touch_mb"] << 20) // 64
    m = o["lines"]
    a = (int(nl * 0.6180339887) | 1) & (nl - 1)
    _emit(t_ms, {"test": "touch", "kind": "setup", "buf": "0x8040000000", "bytes": o["touch_mb"] << 20, "n_lines": nl,
                 "m": m, "a_mul": a, "reps": o["reps"], "hart": 0, "shire_mask": 4294967295, "elf_bytes": 6048})
    hops = [(i * 5) % 9 for i in range(32)]      # invented hop counts from shire 0 to the 32 L3 homes
    mhops = [(i * 3) % 6 for i in range(8)]      # and from a home to the 8 memory shires

    def lat(i, where):
        base = 115 + 12 * hops[i & 31]
        if where == "dram":
            base += 91 + 12 * mhops[i & 7] + rng.choice([0, 0, 11, 38])
        base += rng.randint(-2, 2)
        if where == "dram" and rng.random() < 0.09:
            base += rng.randint(0, 208)           # caught in a refresh (E36: every 3.88 us, up to 208 cycles)
        if rng.random() < 1 / 70:
            base += rng.choice([-128, 128])       # the counter's carry glitch, after the correction
        return base % (1 << 32)                   # the kernel's interval is a u32

    # (arm, a flush launch between the last write and this arm): no timed launch carries the flush itself
    arms = [("dram_ref", True), ("l3_ref", False), ("h2d_warm", False), ("h2d_cold", False), ("l3_ref2", False)]
    where = {"dram_ref": "l3" if model == "N" else "dram", "l3_ref": "l3", "l3_ref2": "l3",
             "h2d_warm": {"A": "l3", "B": "l3", "C": "dram", "D": "l3", "N": "l3"}[model],
             "h2d_cold": {"A": "l3", "B": "dram", "C": "dram", "D": "dram", "N": "l3"}[model]}
    for rep in range(o["reps"]):
        b = rng.randrange(nl)
        for name, after_flush in arms:
            lines = [(a * k + b) & (nl - 1) for k in range(m)]
            d1 = [lat(i, where[name]) for i in lines]
            d2 = [47 + rng.randint(-1, 1) for _ in lines]
            stale = m if (model == "D" and name == "h2d_warm") else 0
            _emit(t_ms, {"test": "touch", "kind": "arm", "rep": rep, "arm": name, "flush": False,
                         "after_flush": after_flush, "b_off": b,
                         "seed_expect": 1, "seed_prev": 0, "h2d_ns": 400000, "launch_ns": 900000, "valid": True,
                         "cycles": sum(d1) + sum(d2), "ok": m - stale, "stale": stale, "other": 0,
                         "first_bad": 0 if stale else -1, "dt1": d1, "dt2": d2, "stream_errors": 0})


def stub(argv):
    o = _args(argv)
    key = f'{o["test"]}/{o["seed"]}/{o["mb"]}/{o["elements"]}/{os.environ.get("PCIE2_DRY_R35", "B")}/' \
          f'{os.environ.get("PCIE2_DRY_R34", "A")}'
    rng = random.Random(zlib.crc32(key.encode()))   # deterministic (str hashes are salted per process)
    t_ms = 1790600000000
    print("Opening device (DRY stub: no device)")
    _emit(t_ms, {"test": "open", "open_ns": 130000000, "src": "DRY", "link": [], "dry": True})
    if os.environ.get("PCIE2_DRY_HANG") == o["test"]:
        print("DRY: a planted hang (exit 124, as timeout 10 gives)", file=sys.stderr)
        return 124
    if os.environ.get("PCIE2_DRY_FAIL") == o["test"]:
        _emit(t_ms, {"test": "error", "which": o["test"],
                     "what": os.environ.get("PCIE2_DRY_FAILMSG", "DRY: a planted failure")})
        return 1
    if o["test"] == "conc":
        stub_conc(o, rng, t_ms)
    elif o["test"] == "touch":
        stub_touch(o, rng, t_ms)
    else:
        print(f"stub: test {o['test']} not modelled", file=sys.stderr)
        return 2
    _emit(t_ms, {"test": "done", "which": o["test"], "elapsed_s": "1.0", "dry": True})
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "plan":
        p = int(sys.argv[sys.argv.index("--pass") + 1])
        for x in plan(p, "--smoke" in sys.argv):
            print(json.dumps(x, separators=(",", ":")))
        return 0
    if cmd == "telsum":
        print(telsum(sys.argv[2]))
        return 0
    if cmd == "stub":
        return stub(sys.argv[2:])
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
