#!/usr/bin/env python3
"""E198's stand-ins for every device tool (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum), for the desk tests ONLY
(desk/desktest_realpath_e198.py, rb/selftest_rb_e198.sh): E193's stand-ins (fake_card_e193.py, unchanged beside it) in aifoundry1 card 1's
forms. Small wrappers named as the box's tools exec `python3 -I -B fake_card_e198.py <role> "$@"`, so a wrapper keeps its process ID.

    ettelem config                          card 1's static config in ettelem's form (TDP 65 W, 65 C, 600 MHz, minion_mv 499), after the
                                            runtime's line on stdout (the REAL committed bytes, E198_FAKE_RTFILE); its stderr the REAL
                                            committed aifoundry1 card-1 config stderr (E198_FAKE_CFGERR) or STATE/config-err; it holds
                                            /dev/et<ET_DEVICES>_mgmt open while it runs (exit 1 if that node cannot be opened)
    ettelem sample --seconds N --every-ms M 10 Hz JSON samples until N s or SIGTERM, holding /dev/et<ET_DEVICES>_mgmt open throughout
    etwho [--check]                         et-who's (et-holders') two forms, FROM THE CASE'S OWN /proc: every process whose fd links name a
                                            /dev/et<N>_ops or /dev/et<N>_mgmt node or a card lock file /run/lock/etsoc-shire<N>.lock, one
                                            line each ('%-14s user pid etime args'), plus STATE/foreign's lines; STATE/etwho-fail: exit 2
                                            (sudo refused); STATE/etwho-sleep: wait once
    host <x04clock_host's options>          x04clock_host's command line, its one-card refusal (checkOneCard: exactly one /dev/et<N>_ops,
                                            N = ET_DEVICES or 0) and output: the runtime's line (STATE/runtime: 'line', the default, at
                                            the start as aifoundry1 prints it; 'inside <k>' inside the k-th call's first X04 line; 'none'),
                                            one "X04 {json}" line per launch with the real host's keys, at the real timing; the device-layer
                                            block on stderr; it holds /dev/et<N>_ops open while it launches
STATE (E198_FAKE_STATE) holds the knobs (E193's: board66, die70, mhz500, stall, host-mode with rc1, rc3, hang, notok, short, garble;
host-sleep) and calls.log. EVERY WATT AND DEGREE HERE IS AN ARBITRARY TEST VALUE, NOT A FORECAST AND NOT A MEASUREMENT. Nothing here opens a
device: the desk tests bind /dev/null at the card nodes' paths inside a sandbox with no card. SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import math
import os
import pwd
import re
import signal
import sys
import time

STATE = os.environ.get("E198_FAKE_STATE", "")
HERE = os.path.dirname(os.path.abspath(__file__))
E193_FAKE = os.path.join(HERE, "..", "e193", "fake_card_e193.py")


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


def runtime_bytes():
    p = os.environ.get("E198_FAKE_RTFILE", "")
    try:
        with open(p, "rb") as f:
            b = f.read()
        if re.fullmatch(rb"Opening device [0-9]+\n", b):
            return b.replace(b"device 1", b"device " + (os.environ.get("ET_DEVICES") or "0").encode())
    except OSError:
        pass
    return ("Opening device %s\n" % (os.environ.get("ET_DEVICES") or "0")).encode()


CONFIG = {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600,
          "minion_mv": 499, "stand_in": True}


def hold_mgmt():
    sel = os.environ.get("ET_DEVICES") or "0"
    try:
        return os.open("/dev/et%s_mgmt" % sel, os.O_RDONLY)
    except OSError as e:
        print(f"stand-in ettelem: cannot open /dev/et{sel}_mgmt: {e}", file=sys.stderr)
        return None


def ettelem(argv):
    if argv == ["config"]:
        log("ettelem config" + (" ET_DEVICES=" + os.environ["ET_DEVICES"] if "ET_DEVICES" in os.environ else ""))
        fd = hold_mgmt()
        if fd is None:
            return 1
        err = read("config-err") or open(os.environ.get("E198_FAKE_CFGERR", os.devnull), errors="replace").read()
        sys.stderr.write(err)
        sys.stdout.buffer.write(runtime_bytes())
        line = read("config.json").strip() or json.dumps(CONFIG)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        time.sleep(0.2)
        os.close(fd)
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
    fd = hold_mgmt()
    if fd is None:
        return 1
    log(f"ettelem sample --seconds {secs:g} --every-ms {every} pid {os.getpid()} ET_DEVICES={os.environ.get('ET_DEVICES', '')}")
    with open(st("sampler.pid"), "a") as f:
        f.write(f"{os.getpid()}\n")
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
                        "noc_w": [round(4.0 + 0.05 * extra, 4)], "minion_mv": [499], "sram_mv": [751], "noc_mv": [486]},
                 "temp_c": {"minshire": [die]}, "mhz": {"minion": mhz, "noc": 400}, "stand_in": True}
            sys.stdout.write(json.dumps(s) + "\n")
            sys.stdout.flush()
        k += 1
        time.sleep(max(0.0, t0 + k * every / 1000.0 - time.time()))
    log(f"ettelem sample pid {os.getpid()} ended ({'SIGTERM' if stop['now'] else 'its seconds'})")
    os.close(fd)
    return 0


NODE = re.compile(r"^/dev/et[0-9]+_(ops|mgmt)$")
LOCKF = re.compile(r"^/run/lock/(etsoc-shire[0-9]+\.lock)$")


def etwho(argv):
    log("et-who " + " ".join(argv))
    if os.path.exists(st("etwho-fail")):
        print("et-who: sudo: The \"no new privileges\" flag is set (stand-in)", file=sys.stderr)
        return 2
    w = read("etwho-sleep").strip()
    if w:
        os.remove(st("etwho-sleep"))
        time.sleep(float(w))
    held = []
    for p in sorted(glob.glob("/proc/[0-9]*"), key=lambda x: int(x.split("/")[2])):
        pid = p.split("/")[2]
        try:
            links = [os.readlink(x) for x in glob.glob(p + "/fd/*")]
        except OSError:
            continue
        hits = []
        for ln in links:
            if NODE.match(ln) and ln not in hits:
                hits.append(ln)
            m = LOCKF.match(ln)
            if m and ("lock:" + m.group(1)) not in hits:
                hits.append("lock:" + m.group(1))
        if not hits:
            continue
        try:
            user = pwd.getpwuid(os.stat(p).st_uid).pw_name
            args = open(p + "/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
            args = re.sub(r"\S*/", "", args)[:100]     # basenames only: the desk's scratch paths stay out of the holder lines
        except (OSError, KeyError):
            continue
        for h in hits:
            held.append("%-14s %-14s %7s %11s %s" % (h, user, pid, "00:01", args))
    held += [x for x in read("foreign").splitlines() if x.strip()]
    if argv == ["--check"]:
        if held:
            print("\n".join(held))
            return 1
        return 0
    print("\n".join(held) if held else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


def load_e193():
    import importlib.util
    spec = importlib.util.spec_from_file_location("fake_card_e193_for_e198", E193_FAKE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.STATE = STATE
    return m


def host(argv):
    F = load_e193()
    log("host " + " ".join(argv))
    sel = os.environ.get("ET_DEVICES") or "0"
    nodes = sorted(p for p in glob.glob("/dev/et*_ops") if re.fullmatch(r"/dev/et\d+_ops", p))
    if nodes != ["/dev/et%s_ops" % sel]:
        print(f"FAIL: found {len(nodes)} ops node(s); need exactly /dev/et{sel}_ops (the device layer opens every node it finds): "
              "not opening (stand-in host)", file=sys.stderr)
        return 1
    try:
        segs = F.segments(argv)
    except SystemExit as e:
        print(str(e), file=sys.stderr)
        return 2
    mode = F.take_mode(len(segs) > 1)
    n_call = int(read("host-calls").strip() or 0) + 1
    with open(st("host-calls"), "w") as f:
        f.write(str(n_call))
    rt = (read("runtime").strip() or "line").split()
    inside = rt[0] == "inside" and len(rt) > 1 and int(rt[1]) == n_call
    fd = os.open("/dev/et%s_ops" % sel, os.O_RDONLY)
    t_open = time.time()
    out = sys.stdout.buffer
    if rt[0] == "line" or (rt[0] == "inside" and not inside):
        out.write(runtime_bytes())        # aifoundry1's form: the runtime's line when the device opens, at a line's start
        out.flush()
    print(f"PCIe target:                                               /dev/et{sel}_ops\n"
          f"Physical device ID:                                        {sel}                    (0x{sel})", file=sys.stderr)
    time.sleep(0.4 + (float(read("host-sleep").strip()) if read("host-sleep").strip() else 0.0))
    print(f"device ready in {time.time() - t_open:.2f} s (stand-in)", file=sys.stderr)
    if mode == "hang":
        time.sleep(60)
    status = 0
    first = True
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
                    f.write(json.dumps({"w": F.watts(o)}))
                t0 = int(time.time() * 1000)
                a = time.time()
                time.sleep(launch_s)
                wall = time.time() - a
                t1 = int(time.time() * 1000)
                ok = not (mode in ("rc3", "notok") and n == 1)
                if mode == "garble":
                    out.write(b'X04 {"label":"garbled by the stand-in\n')
                    out.flush()
                    return 0
                line = ("X04 " + json.dumps(F.record(o, seg, t0, t1, wall, ok), separators=(",", ":")) + "\n").encode()
                if inside and first:
                    cut = line.index(b'"cls":') + 6       # the runtime's line inside the record, as it fell inside E191's host line
                    out.write(line[:cut])
                    out.flush()
                    out.write(runtime_bytes())
                    out.flush()
                    out.write(line[cut:])
                else:
                    out.write(line)
                out.flush()
                first = False
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
        os.close(fd)
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
