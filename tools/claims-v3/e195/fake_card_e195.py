#!/usr/bin/env python3
"""E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): THE STAND-INS for the desk tests, never on the box. Every
watt, degree and count here is an ARBITRARY TEST VALUE, not a forecast and not a measurement. They open no device: the "card" is a few
files in $E195_FAKE_STATE.

    fake_card_e195.py ettelem config | sample --seconds N --every-ms M     the sampler and its config read (behind E128's guard)
    fake_card_e195.py host <x09mem_host's arguments>                      the host: --list [--json]; --item NAME ... (X09MEM lines)
    fake_card_e195.py sparsity <sparsity_host's arguments>                the anchor (--values pi: SPARSITY lines) and the heater (randn)
    fake_card_e195.py holders                                             et-holders' form: "<node or lock:name> <user> <pid> <etime> <args>"
    fake_card_e195.py etwho [--check]                                     et-who's form and exit codes (0 free, 1 held, 2 failed)

The card model ($E195_FAKE_STATE): heat.json holds the end of the last heater burst and whether a heater or a host runs; the sampler
reads it: board 22 W idle, +23 W while the heater runs, +8 W while a host launches; the die 57.0 C, 59.5 C for 0.6 s after a heater
burst (so runitems.py's approach heats once and launches about a second later). Knobs (files in the state directory, read live):
  fast                 launches of 0.05 s (10 a run) and heater bursts of 0.2 s; without it the hosts' real timing (0.4 s launches for
                       --seconds, 2 s heater bursts)
  board_hot=<W>@<t0>   board_w = W from <t0> (epoch s) on for 2 s (a live board stop)
  heater_w=<W>         the heater's board reading (default 45)
  die_hot=<C>@<t0>     the die at C from <t0> on
  stale=<t0>           the sampler stops writing at <t0> (epoch s; it stays alive until SIGTERM)
  stuck                a sampler ignores SIGTERM (it exits by itself 40 s after the first one it ignored)
  config=<json>        the config read's line
  foreign=<lines>      et-holders' lines of another user (a holder)
  runtime=split|line|twice|garble|none   what the host's stdout carries beside its records (split: aifoundry1's runtime line,
                       "Opening device <n>" and its newline, inside each X09MEM line at the byte the committed 1a4bc1e3 smoke stdout
                       had it; line: on its own line before the records; twice: split with two runtime lines; garble: an unknown text
                       inside the first record: the runner must fail the parse, never read a wrong datum)
  participants=<n>     the participants every X09MEM record reports (default 1024)
  host_exit=<item>:<rc> the host exits rc after its records for that item
  slow_host            the host and the anchor at their real timing even with fast (the heater stays fast)
Every call is appended to calls.log ("<epoch> <tool> <args> | lock=held|FREE"); the signals a sampler receives to signals.log.
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import os
import re
import signal
import sys
import time

ST = os.environ.get("E195_FAKE_STATE", "/nonexistent")
LOCK = "/run/lock/etsoc-shire0.lock"
HERE = os.path.dirname(os.path.abspath(__file__))


def knob(name, default=None):
    p = os.path.join(ST, name)
    try:
        with open(p) as f:
            return f.read().strip()
    except OSError:
        return default


def log(tool, args, extra=""):
    try:
        with open(os.path.join(ST, "calls.log"), "a") as f:
            f.write(f"{time.time():.3f} {tool} {' '.join(args)}{(' | ' + extra) if extra else ''}\n")
    except OSError:
        pass


def lock_state():
    """held: another process (the block) holds the card lock; FREE: nobody (a device process would run without it)."""
    try:
        fd = os.open(LOCK, os.O_RDWR)
    except OSError:
        return "nolockfile"
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return "FREE"
    except OSError:
        return "held"
    finally:
        os.close(fd)


def model():
    try:
        with open(os.path.join(ST, "heat.json")) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def set_model(**kw):
    m = model()
    m.update(kw)
    tmp = os.path.join(ST, "heat.json.%d" % os.getpid())
    with open(tmp, "w") as f:
        json.dump(m, f)
    os.replace(tmp, os.path.join(ST, "heat.json"))


def at_knob(name):
    """<value>@<t0> knobs: the value once the clock has passed t0, else None."""
    v = knob(name)
    if not v or "@" not in v:
        return None
    val, t0 = v.split("@", 1)
    return float(val) if time.time() >= float(t0) else None


def sample_line():
    m, now = model(), time.time()
    board = 22.0 + (float(knob("heater_w", "45")) - 22.0 if m.get("heater_until", 0) > now else 0.0) + \
        (8.0 if m.get("host_until", 0) > now else 0.0)
    bh = at_knob("board_hot")
    if bh is not None and now - float(knob("board_hot").split("@")[1]) < 2.0:
        board = bh
    die = 59.5 if now - m.get("heat_end", 0) < 0.6 else 57.0
    dh = at_knob("die_hot")
    if dh is not None:
        die = dh
    rail = round(board * 0.30, 3)
    return {"t_ms": int(now * 1000), "took_ms": 21, "since_reset_ms": -1, "board_w": round(board, 2),
            "sp": {"minion_w": [rail, rail, rail], "sram_w": [2.16, 2.16, 2.16], "noc_w": [2.45, 2.45, 2.45],
                   "minion_mv": [523, 523, 523], "sram_mv": [698, 698, 698], "noc_mv": [484, 484, 484],
                   "minion_mhz": [600, 600, 600], "noc_mhz": [400, 400, 400]},
            "temp_c": {"pmic": 50, "ioshire": [int(die), int(die) - 5, int(die) + 20], "minshire": [int(die), int(die) - 5, int(die) + 20]},
            "die_mv": {"ddr": 767, "sram": 698, "minion": 523, "noc": 484},
            "mhz": {"minion": 600, "noc": 400, "ddr": 933}}


def ettelem(argv):
    log("ettelem", argv)
    if argv == ["config"]:
        print(knob("config", '{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}'))
        return 0
    if not argv or argv[0] != "sample":
        print("stand-in ettelem: only config and sample", file=sys.stderr)
        return 2
    secs, every = 10.0, 100.0
    a = argv[1:]
    for i in range(0, len(a) - 1, 2):
        if a[i] == "--seconds":
            secs = float(a[i + 1])
        elif a[i] == "--every-ms":
            every = float(a[i + 1])
    stop = {"term": False, "ignored_at": None}

    def on_term(sig, frm):
        with open(os.path.join(ST, "signals.log"), "a") as f:
            f.write(f"{time.time():.3f} {os.getpid()} ettelem got signal {sig}\n")
        if knob("stuck") is not None:
            stop["ignored_at"] = stop["ignored_at"] or time.time()
            return
        stop["term"] = True
    signal.signal(signal.SIGTERM, on_term)
    t_end = time.time() + secs
    import atexit
    atexit.register(lambda: log("ettelem-end", ["sample"]))
    while time.time() < t_end and not stop["term"]:
        if stop["ignored_at"] and time.time() - stop["ignored_at"] > 40:
            break
        sv = knob("stale")
        if not (sv is not None and time.time() >= float(sv or 0)):
            print(json.dumps(sample_line(), separators=(",", ":")), flush=True)
        time.sleep(every / 1000.0)
    return 0


RUNTIME = None


def runtime_line():
    """The runtime line and the byte it fell at, from the committed 1a4bc1e3 smoke stdout (aifoundry1, Sun 15 Nov 2026), if present."""
    global RUNTIME
    if RUNTIME is None:
        p = knob("realbytes")
        txt, off = "Opening device 1\n", 233
        if p and os.path.exists(p):
            b = open(p, "rb").read().decode()
            m = re.search(r"Opening device [0-9]+\n", b)
            if m:
                txt, off = m.group(0), m.start()
        RUNTIME = (txt, off)
    return RUNTIME


def host(argv):
    a = list(argv)
    if "--list" in a:
        print(open(os.path.join(HERE, "desk", "arm-table-e195.json" if "--json" in a else "arm-table-e195.txt")).read(), end="")
        return 0
    item = a[a.index("--item") + 1] if "--item" in a else "?"
    secs = float(a[a.index("--seconds") + 1]) if "--seconds" in a else 4.0
    stopf = a[a.index("--stop-file") + 1] if "--stop-file" in a else ""
    noms = "--no-ms" in a
    log("x09mem_host", argv, "lock=" + lock_state())
    ops = [n for n in os.listdir("/dev") if re.fullmatch(r"et[0-9]+_ops", n)]
    if len(ops) != 1:
        print(f"FAIL: {len(ops)} card nodes on this host: this host program is for a host with one card and refuses to run here"
              if ops else "FAIL: no card node /dev/et<N>_ops on this host", file=sys.stderr)
        return 1
    for sg in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sg, lambda s, f: open(os.path.join(ST, "signals.log"), "a").write(f"{time.time():.3f} {os.getpid()} x09mem_host got signal {s}\n") or sys.exit(143))
    fast = knob("fast") is not None and knob("slow_host") is None
    dt = 0.05 if fast else 0.4
    n = int(round(secs / 0.4))
    rt = knob("runtime", "none")
    parts = int(knob("participants", "1024"))
    print("device ready in 0.18 s", file=sys.stderr, flush=True)
    t_open = time.time()
    if rt == "line":
        sys.stdout.write(runtime_line()[0])
    mode = {"r": "rd", "w": "wr"}[item[0]] if item[0] in "rw" else "rd"
    unit = "access" if item.endswith(("l1", "scp", "nst")) else "line"
    for k in range(n):
        if stopf and os.path.exists(stopf):
            break
        t0 = time.time()
        set_model(host_until=t0 + dt + 0.05)
        time.sleep(dt)
        t1 = time.time()
        lines = 468000000 // 10 if unit == "line" else 0
        rec = {"arm": item, "mode": mode, "image": "z", "period": 0, "unit": unit, "participants": parts, "ops": float(lines or 1000000),
               "lines": lines, "accesses": lines or 1000000, "bytes": lines * 64, "iters": 1000, "cycles_max": 240000000,
               "cycles_mean": 239990000, "ops_per_s": 1.1700e9, "bytes_per_s": 7.4880e10, "ret_t0": 1000000, "l1_miss": 8000,
               "ms": False if noms else True, "ms_rd": 0, "ms_wr": 0, "ms_cyc": 0, "ms_bad": 0, "spins": 0, "late": 0, "phase": 1,
               "region": 131072, "slice_bytes": 139264, "seed": 1, "image_crc": "00000000", "wall_s": round(t1 - t0, 4),
               "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), "ok": True}
        line = "X09MEM " + json.dumps(rec, separators=(",", ":")) + "\n"
        if rt in ("split", "twice"):
            txt, off = runtime_line()
            off = min(off, len(line) - 2)
            line = line[:off] + txt + (("Opening device 0\n") if rt == "twice" else "") + line[off:]
        elif rt == "garble" and k == 0:
            line = line[:120] + "SOMETHING ELSE ON STDOUT\n" + line[120:]
        sys.stdout.write(line)
        sys.stdout.flush()
    print(f"device held for {time.time() - t_open:.2f} s", file=sys.stderr)
    log("x09mem_host-end", [item], "lock=" + lock_state())
    he = knob("host_exit")
    if he and he.split(":")[0] == item:
        return int(he.split(":")[1])
    return 0


def sparsity(argv):
    a = list(argv)
    vals = a[a.index("--values") + 1] if "--values" in a else "pi"
    secs = float(a[a.index("--seconds") + 1]) if "--seconds" in a else 2.0
    stopf = a[a.index("--stop-file") + 1] if "--stop-file" in a else ""
    for x in a:
        if x.startswith("--no-such-option"):
            print(f"unknown option {x}", file=sys.stderr)
            return 2
    log("sparsity_host", argv, "lock=" + lock_state())
    import atexit
    atexit.register(lambda: log("sparsity_host-end", [vals]))
    fast = knob("fast") is not None
    if vals == "randn":   # the heater
        d = 0.2 if fast else secs
        set_model(heater_until=time.time() + d)
        time.sleep(d)
        set_model(heat_end=time.time())
        print('SPARSITY {"test":"fma","values":"randn","ok":true}')
        return 0
    dt = 0.05 if fast and knob("slow_host") is None else 0.4      # the anchor at the host's real timing with slow_host
    for k in range(int(round(secs / 0.4))):
        if stopf and os.path.exists(stopf):
            break
        t0 = time.time()
        time.sleep(dt)
        t1 = time.time()
        print("SPARSITY " + json.dumps({"test": "fma", "type": "fp32", "values": vals, "minions": 1024, "iters": 20000, "launch": k,
                                        "cycles_max": 10920691, "wall_s": round(t1 - t0, 4), "t_start_ms": int(t0 * 1000),
                                        "t_end_ms": int(t1 * 1000), "ok": True}, separators=(",", ":")), flush=True)
    return 0


def holders():
    """et-holders' form: another user's lines from the knob, then our own lock holders and stand-in device processes."""
    out = []
    f = knob("foreign")
    if f:
        out += [ln for ln in f.splitlines() if ln.strip()]
    me = os.environ.get("E195_FAKE_LOGIN", "boxuser")
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            comm = open(f"/proc/{p}/comm").read().strip()
            fds = os.listdir(f"/proc/{p}/fd")
        except OSError:
            continue
        for fd in fds:
            try:
                if os.readlink(f"/proc/{p}/fd/{fd}") == LOCK:
                    out.append(f"lock:etsoc-shire0.lock {me} {p} 00:01 {comm}")
                    break
            except OSError:
                continue
        if comm in ("ettelem",):
            out.append(f"/dev/et0_mgmt  {me} {p} 00:01 {comm}")
        elif comm.endswith("_host"):
            out.append(f"/dev/et0_ops   {me} {p} 00:01 {comm}")
    if not out:
        print("No process holds an ET-SoC-1 device node or card lock.")
    for ln in out:
        print(ln)
    return 0


def etwho(argv):
    log("et-who", argv)
    if knob("etwho_fail") is not None:
        print("et-who: the holder helper could not be run (desk-test stand-in)", file=sys.stderr)
        return 2
    if not argv:
        return holders()
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        holders()
    held = [ln for ln in buf.getvalue().splitlines() if ln.startswith("/dev/et") or ln.startswith("lock:")]
    if not held:
        return 0
    print("\n".join(held))
    return 1


def set_comm(name):
    """The stand-in's process name (ps comm) as the real tool's: lib.sh's DEV_COMM rules read it."""
    try:
        import ctypes
        ctypes.CDLL(None).prctl(15, name.encode()[:15], 0, 0, 0)
    except Exception:
        pass


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    tool, rest = argv[0], argv[1:]
    set_comm({"ettelem": "ettelem", "host": "x09mem_host", "sparsity": "sparsity_host"}.get(tool, "fake_" + tool))
    if tool == "holders":
        return holders()
    fn = {"ettelem": ettelem, "host": host, "sparsity": sparsity, "etwho": etwho}.get(tool)
    return fn(rest) if fn else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
