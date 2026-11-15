#!/usr/bin/env python3
"""E193's stand-ins for every device tool (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum), for the desk tests ONLY: the
real-path desk test (desk/desktest_realpath_e193.py) and the runbook's desk test (rb/selftest_rb_e193.sh) put small wrappers named as
the box's tools in front of the session (each `exec python3 -I -B fake_card_e193.py <role> "$@"`, so a wrapper keeps its process id):

    ettelem config                               the card's static config: one JSON line in ettelem's form (TDP 0 W, 65 C, 600 MHz)
    ettelem sample --seconds N --every-ms M      10 Hz JSON lines in the sampler's form (t_ms, board_w, sp.{minion,sram,noc}_{w,mv},
                                                 temp_c.minshire, mhz.minion) until N s or SIGTERM; its pid in STATE/sampler.pid
    etwho [--check]                              et-who's two forms: the holders (the stand-in sampler on /dev/et0_mgmt while it runs;
                                                 every process of the sandbox (its mount namespace) holding the card lock file open; STATE/foreign's lines)
    host <x04clock_host's options>               x04clock_host's command line and output: one "X04 {json}" line per launch with the
                                                 real host's keys, a launch every window/6e8 s, the 9.5 s budget and its fit rule, the
                                                 trains' segments, exit 0, 3 or 1; refuses unless /dev/et<ET_DEVICES>_ops is the only
                                                 ops node (as checkOneCard); while it launches it tells the sampler its watts

STATE (E193_FAKE_STATE) holds the knobs the tests set: board66 (every sample 66 W), die70 (every sample 70 C), mhz500 (a count: that many
samples at 500 MHz), stall (the sampler stops writing, alive), config.json (another config line), foreign (holder lines), host-mode
(lines "<mode> <count>": rc1, rc3, hang, notok, short, garble; each call takes one; "short", the next train's last segment
one launch short with exit 0; "garble", the call's first launch printed as a malformed X04 line, then exit 0: the runner's parser
raises, a crash with no stop recorded), host-sleep (seconds before the first launch), etwho-sleep (seconds
the next et-who call waits, once). EVERY WATT AND DEGREE HERE IS AN ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT: board 30 W
at idle, plus per launch 1.25 W x busy harts / 1,984, a class's 2-4 W x its density, 0.3 W x shires / 32 for tk, 0.4 W for a wait,
0.4 + 1.6 x duty for duty, 1.0 W for the divide chain; the die 50 C, 53 C while a launch of 2 W or more runs and 2 s after.
Nothing here opens a device, a network or a lock of its own. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import re
import signal
import sys
import time

STATE = os.environ.get("E193_FAKE_STATE", "")
LOCK = "/run/lock/etsoc-shire0.lock"


def st(name):
    return os.path.join(STATE, name)


def log(msg):
    if STATE:
        with open(st("calls.log"), "a") as f:
            f.write(f"{time.time():.3f} {msg}\n")


def read(name, default=""):
    try:
        with open(st(name)) as f:
            return f.read()
    except OSError:
        return default


CONFIG = {"tdp_w": 0, "temp_threshold_c": 65, "power_state": "managed_power", "minion_mhz": 600, "noc_mhz": 400,
          "minion_mv": 523, "stand_in": True}


def ettelem(argv):
    if argv == ["config"]:
        log("ettelem config" + (" ET_DEVICES=" + os.environ["ET_DEVICES"] if "ET_DEVICES" in os.environ else ""))
        line = read("config.json").strip() or json.dumps(CONFIG, separators=(",", ":"))
        print(line)
        return 0
    if not argv or argv[0] != "sample":
        print("stand-in ettelem: only config and sample", file=sys.stderr)
        return 2
    secs, every = 10.0, 100
    a = argv[1:]
    while a:
        if a[0] == "--seconds":
            secs = float(a[1]); a = a[2:]
        elif a[0] == "--every-ms":
            every = int(a[1]); a = a[2:]
        else:
            print("stand-in ettelem: refused " + a[0], file=sys.stderr)
            return 2
    log(f"ettelem sample --seconds {secs:g} --every-ms {every} pid {os.getpid()}")
    with open(st("sampler.pid"), "w") as f:
        f.write(str(os.getpid()))
    stop = {"now": False}
    signal.signal(signal.SIGTERM, lambda *_: stop.__setitem__("now", True))
    t0 = time.time()
    hot_until = 0.0
    k = 0
    while not stop["now"] and time.time() - t0 < secs:
        now = time.time()
        b = read("burst.json").strip()
        extra = 0.0
        if b:
            try:
                extra = float(json.loads(b)["w"])
            except (ValueError, KeyError):
                extra = 0.0
        if extra >= 2.0:
            hot_until = now + 2.0
        die = 53 if now < hot_until else 50
        board = 30.0 + extra + 0.02 * math.sin(k / 3.0)
        mhz = 600
        if os.path.exists(st("board66")):
            board = 66.0
        if os.path.exists(st("die70")):
            die = 70
        m5 = read("mhz500").strip()
        if m5.isdigit() and int(m5) > 0:
            mhz = 500
            with open(st("mhz500"), "w") as f:
                f.write(str(int(m5) - 1))
        if not os.path.exists(st("stall")):
            s = {"t_ms": int(now * 1000), "took_ms": 21, "board_w": round(board, 3),
                 "sp": {"minion_w": [round(9.0 + 0.8 * extra, 4)], "sram_w": [round(3.0 + 0.1 * extra, 4)],
                        "noc_w": [round(4.0 + 0.05 * extra, 4)], "minion_mv": [523], "sram_mv": [698], "noc_mv": [484]},
                 "temp_c": {"minshire": [die]}, "mhz": {"minion": mhz, "noc": 400}, "stand_in": True}
            sys.stdout.write(json.dumps(s) + "\n")
            sys.stdout.flush()
        k += 1
        time.sleep(max(0.0, t0 + k * every / 1000.0 - time.time()))
    log(f"ettelem sample pid {os.getpid()} ended ({'SIGTERM' if stop['now'] else 'its seconds'})")
    return 0


def etwho(argv):
    log("et-who " + " ".join(argv))
    w = read("etwho-sleep").strip()
    if w:
        os.remove(st("etwho-sleep"))
        time.sleep(float(w))
    user = os.environ.get("USER") or "boxuser"
    held = []
    pid = read("sampler.pid").strip()
    if pid.isdigit() and os.path.exists(f"/proc/{pid}"):
        try:
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().split(b"\0")
        except OSError:
            cmd = []
        if any(c.endswith(b"fake_card_e193.py") for c in cmd) and b"sample" in cmd:
            held.append(f"/dev/et0_mgmt {user} {pid} 00:01 ettelem sample")
    try:
        myns = os.readlink("/proc/self/ns/mnt")
    except OSError:
        myns = ""
    for p in glob.glob("/proc/[0-9]*/fd/*"):
        try:
            if os.readlink(p) == LOCK:
                q = p.split("/")[2]
                if os.readlink(f"/proc/{q}/ns/mnt") != myns:
                    continue                   # another sandbox's own /run/lock: not this box's card lock
                comm = open(f"/proc/{q}/comm").read().strip()
                held.append(f"lock:etsoc-shire0.lock {user} {q} 00:00 {comm}")
        except OSError:
            continue
    held += [x for x in read("foreign").splitlines() if x.strip()]
    if argv == ["--check"]:
        if held:
            print("\n".join(held))
            return 1
        return 0
    print("\n".join(held) if held else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


def segments(args):
    """x04clock_host's parseSegments, the fields its X04 line carries (session defaults are on the command line already)."""
    parts = [[]]
    for w in args:
        if w == "--then":
            parts.append([])
        else:
            parts[-1].append(w)
    base = dict(arm="spin", cls="none", t1="same", every=1, mask=0xff, shires=0xffffffff, minions=0xfffffffe, window=240000000,
                period=65536, duty=50, cluster=0, seg=0, seconds=3.0, budget=9.5, label="")
    keys = {"--arm": "arm", "--cls": "cls", "--t1": "t1", "--every": "every", "--mask": "mask", "--shires": "shires",
            "--minions": "minions", "--window": "window", "--period": "period", "--duty-pct": "duty",
            "--seg-launches": "seg", "--seconds": "seconds", "--budget": "budget", "--label": "label", "--kernel": "kernel",
            "--hs-limit": "hs"}

    def apply(o, ws):
        o = dict(o)
        i = 0
        while i < len(ws):
            if ws[i] == "--cluster":
                o["cluster"] = 1
                i += 1
                continue
            if ws[i] not in keys:
                raise SystemExit(f"unknown option {ws[i]}")
            k, v = keys[ws[i]], ws[i + 1]
            o[k] = v if k in ("arm", "cls", "t1", "label", "kernel") else (float(v) if k in ("seconds", "budget") else int(v, 0))
            i += 2
        return o
    b = apply(base, parts[0])
    return [b] + [apply(b, p) for p in parts[1:]]


def watts(o):
    nsh = bin(o["shires"] & 0xffffffff).count("1")
    wk = bin(o["minions"] & 0xfffffffe).count("1")
    if o["arm"] == "tk":
        return 0.3 * nsh / 32
    harts = wk * nsh * (1 if o["t1"] == "off" else 2)
    if o["arm"] in ("spin", "mix"):
        w = 1.25 * harts / 1984
        if o["arm"] == "mix":
            w += {"fadd_ps": 4.0, "fsgnj_s": 2.0, "fadd_s": 3.0}.get(o["cls"], 1.0) / o["every"] * (bin(o["mask"] & 0xff).count("1") / 8.0
                                                                                                if o["cls"] == "fadd_ps" else 1.0)
        return w
    if o["arm"] == "wait":
        return 0.4
    if o["arm"] == "duty":
        return 0.4 + 1.6 * o["duty"] / 100.0
    return 1.0


def record(o, seg, t0, t1, wall, ok=True):
    win = o["window"] // o["period"] * o["period"]
    nsh = bin(o["shires"] & 0xffffffff).count("1")
    wk = bin(o["minions"] & 0xfffffffe).count("1")
    t0w = 0 if o["arm"] == "tk" else wk * nsh
    t1w = 0 if (o["arm"] == "tk" or o["t1"] == "off") else wk * nsh
    harts = t0w + t1w
    duty_cycles = o["period"] * o["duty"] // 100
    waits = o["arm"] == "wait" or (o["arm"] == "duty" and duty_cycles < o["period"])
    spc = {"spin": 0.39, "mix": 0.39, "stall": 0.02}.get(o["arm"], 0.0)
    if o["arm"] == "duty":
        spc = 0.39 * (duty_cycles / o["period"] if duty_cycles < o["period"] else 1.0)
    awake = int(round((duty_cycles / o["period"] if duty_cycles < o["period"] else 1.0) * harts * win)) if o["arm"] == "duty" else 0
    return {"label": o["label"], "seg": seg, "arm": o["arm"], "cls": o["cls"], "every": o["every"], "cluster": o["cluster"],
            "mask": "0x%x" % (o["mask"] & 0xff), "t1": o["t1"], "duty_pct": o["duty"], "period": o["period"], "window": win,
            "shire_mask": "0x%x" % (o["shires"] & 0xffffffff), "minion_mask": "0x%x" % (o["minions"] & 0xfffffffe), "shires": nsh,
            "workers_t0": t0w, "workers_t1": t1w, "slots": float(round(spc * win * harts)),
            "slots_per_cycle_per_hart": round(spc, 4), "awake_cycles": awake,
            "credits_taken": (win // o["period"]) * harts if waits else 0, "credits_drained": 0,
            "tk_credits_sent": (win // o["period"]) * nsh if waits else 0, "tk_cycles": win, "hs_cycles_max": 1043 if waits else 0,
            "late": 0, "hs_bailouts": 0, "ctr_unsynced": 0, "cycles_max": win if harts else 0,
            "cycles_mean": float(win) if harts else 0.0, "readers": 4 * nsh, "retired0": 0, "retired1": 0, "icache_req": 0,
            "icache_miss": 0, "wall_s": round(wall, 4), "t_start_ms": t0, "t_end_ms": t1, "complete": ok, "credits_ok": True,
            "ok": ok}


def take_mode(train):
    lines = [x.split() for x in read("host-mode").splitlines() if x.strip()]
    if not lines:
        return ""
    mode, n = lines[0][0], int(lines[0][1]) if len(lines[0]) > 1 else 1
    if mode == "short" and not train:
        return ""                      # "short" waits for the next train
    rest = ([[mode, str(n - 1)]] if n > 1 else []) + lines[1:]
    with open(st("host-mode"), "w") as f:
        f.write("".join(" ".join(x) + "\n" for x in rest))
    return mode


def host(argv):
    log("host " + " ".join(argv))
    sel = os.environ.get("ET_DEVICES") or "0"
    nodes = sorted(p for p in glob.glob("/dev/et*_ops") if re.fullmatch(r"/dev/et\d+_ops", p))
    if nodes != ["/dev/et%s_ops" % sel]:
        print(f"FAIL: found {len(nodes)} ops node(s); need exactly /dev/et{sel}_ops (stand-in host): not opening", file=sys.stderr)
        return 1
    try:
        segs = segments(argv)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    mode = take_mode(len(segs) > 1)
    tsleep = read("host-sleep").strip()
    t_open = time.time()
    time.sleep(0.4 + (float(tsleep) if tsleep else 0.0))
    print(f"device ready in {time.time() - t_open:.2f} s (stand-in)", file=sys.stderr)
    if mode == "hang":
        time.sleep(60)
    status = 0
    try:
        for k, o in enumerate(segs):
            seg = k if len(segs) > 1 else -1
            launch_s = (o["window"] // o["period"] * o["period"]) / 6.0e8
            n, t_seg = 0, time.time()
            cap = segs[0]["seg"] - (1 if (mode == "short" and k == len(segs) - 1) else 0)
            while ((n < cap) if len(segs) > 1 else (time.time() - t_seg < o["seconds"])):
                el = time.time() - t_open
                if el > o["budget"] or el + launch_s + math.ceil(launch_s + 1.0) >= o["budget"]:
                    break
                n += 1
                with open(st("burst.json"), "w") as f:
                    f.write(json.dumps({"w": watts(o)}))
                t0 = int(time.time() * 1000)
                a = time.time()
                time.sleep(launch_s)
                wall = time.time() - a
                t1 = int(time.time() * 1000)
                ok = not (mode in ("rc3", "notok") and n == 1)
                if mode == "garble":
                    print('X04 {"label":"garbled by the stand-in', flush=True)     # a malformed line, then a clean exit
                    return 0
                print("X04 " + json.dumps(record(o, seg, t0, t1, wall, ok), separators=(",", ":")), flush=True)
                if mode == "rc1":
                    print("kernel did not finish within 2 s, aborting the stream (stand-in)", file=sys.stderr)
                    return 1
                if not ok:
                    status = 3
                    break
                time.sleep(0.002)
            if status:
                break
    finally:
        try:
            os.remove(st("burst.json"))
        except OSError:
            pass
    time.sleep(0.2)
    print(f"device held for {time.time() - t_open:.2f} s (stand-in)", file=sys.stderr)
    return status


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    role, argv = sys.argv[1], sys.argv[2:]
    if role == "ettelem":
        return ettelem(argv)
    if role == "etwho":
        return etwho(argv)
    if role == "host":
        return host(argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
