#!/usr/bin/python3 -I
"""E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): THE STAND-INS for the real-path desk test
(desk/desktest_realpath_e200.sh) and the runbook desk test's stand-in box (rb/selftest_rb_e200.sh). E197's stand-ins
(tools/claims-v3/e197/fake_card_e197.py, unchanged beside it) for this card under its governor. NEVER ON THE BOX: it is in no sync list.
NOTHING HERE OPENS A DEVICE OR SENDS A COMMAND; nothing here is measured or forecast: every watt, degree, clock and rate is an arbitrary
test value. Each role answers the session's real path the way the box's tool does, in the tool's own output form, from a small card model
shared through a state directory (E200_STANDIN_DIR), and logs every call (E200_STANDIN_DIR/calls/<role>.log, one JSON line each: argv,
time, whether the card lock was held by another open file, whether the stop file existed, its parent's command name):

  sampler  the box's build/ettelem-hpl/ettelem behind E200's guard: `sample --seconds T --every-ms N` writes JSON lines in the reader's
           keys (t_ms, board_w, sp.minion_w[0], sp.minion_mv[0], temp_c.minshire [the shires' mean, a low sensor, the latch] whole
           degrees, mhz.minion) until T or SIGTERM (logged: the session must stop it with SIGTERM, never SIGKILL); A SHORT SAMPLE (--seconds
           5 or less: the wrapper's die gate) reads its die from the scenario's die_gate list, one value a call; `config` prints the reader's
           JSON line on stdout (tdp_w 65, temp_threshold_c 65, minion_mhz 600, minion_mv 519) and the device layer's identity block on stderr
           (PCIe target /dev/et0_mgmt, Physical device ID 0), as E194's committed config-start.json and .err read. While a long sample runs
           its pid is listed in E200_STANDIN_DIR/active/ (et-who reads it);
  THE CLOCK (mhz.minion), the governor's climb: "clock" "climb" (the default): 600 MHz while no host runs; when a host process starts,
           600 MHz for its climb (climb_s, 0.9 s by default; climb_proc {"<n>": s} per process) then 800 MHz while it runs, with
           dip_proc [{"proc": n, "at_s": a, "for_s": b, "mhz": m}, ...] (a step inside process n, a s after its start); "climb_hold": the
           same climbs, but 800 MHz between host processes once the first has started (so that a short desk session's median clock is
           800 MHz, as a whole sitting's is: its trains fill it); "hold": 600 MHz until
           the first host process starts, 800 MHz after (the fast pace's whole sittings, whose reported spans run ahead of real time);
           "flat600": 600 MHz throughout (a governor that never steps up); E197's mhz_from {"t", "mhz", "n"} kept;
  etwho    `et-who [--check]`: "No process holds an ET-SoC-1 device node or card lock." (exit 0), or one holder line per running long
           sampler stand-in ("/dev/et0_mgmt <login> <pid> ettelem", et-who's form) and any foreign holder the scenario names (exit 1
           with --check); etwho_ours_reads n: the first n `et-who --check` calls also show a reader of ours on /dev/et0_mgmt (our live
           collector's read in flight);
  ps       /usr/bin/ps, plus another user's device process ("0 4242 other_host") when the scenario names one;
  host     the regfile host: its option parser, its refusals before the device, then launches of LAUNCH_S seconds, each printing ONE
           REGFILE line in the real host's printf form (main.cpp lines 289-300, the kind's fields copied from E197's registered table byte
           for byte) and flushing; the stop file read before every launch, the 8.5 s budget, exactly --launches in a train. ITS REPORTED
           SPANS: launch k of a process reports [T + k x report_span_s, T + (k + 1) x report_span_s] (T its first launch's start, 0.4 s by
           default: a card's launch at 800 MHz under W1), its cycles_max and cycles_mean the --window it was given, and its wall_s the
           span, so its own count reads window / span (800 MHz at 320,000,000 cycles and 0.4 s); at the fast pace T is the process's start on
           a 400 ms grid plus its number mod 400 ms, so no two overlapping processes report one launch start (E200's reduction matches a
           launch to its process by its start, as a card's never overlap); own_mhz_proc {"proc": n, "mhz": m}: that
           process's last launch reports the wall seconds of m MHz.
The scenario (E200_STANDIN_DIR/scenario.json) sets the model and the faults (E197's keys, and the clock's above, die_gate, latch_from {"t",
"c"}, board_w_samples {"t", "w"} (a board value held on every sample from t: the 85 W line's case), etwho_ours_reads).
    python3 -I -B fake_card_e200.py <role> [args...]        (or run as a file named for its role: et-who, ps, ettelem, regfile_host)
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import os
import signal
import subprocess
import sys
import time

SD = os.environ.get("E200_STANDIN_DIR", "")
LOCK = "/run/lock/etsoc-shire0.lock"
HERE = os.path.dirname(os.path.realpath(__file__))
_stop = False


def scen():
    try:
        return json.load(open(os.path.join(SD, "scenario.json")))
    except (OSError, ValueError):
        return {}


def lock_held():
    try:
        fd = os.open(LOCK, os.O_RDONLY)
    except OSError:
        return None
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    finally:
        os.close(fd)


def parent_comm():
    try:
        with open("/proc/%d/comm" % os.getppid()) as f:
            return f.read().strip()
    except OSError:
        return None


def record(role, **kw):
    if not SD:
        return
    os.makedirs(os.path.join(SD, "calls"), exist_ok=True)
    kw.update(role=role, pid=os.getpid(), t_ms=int(time.time() * 1000))
    with open(os.path.join(SD, "calls", role + ".log"), "a") as f:
        f.write(json.dumps(kw) + "\n")


def bump(name):
    p = os.path.join(SD, "count-" + name)
    fd = os.open(p, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        raw = os.read(fd, 64).decode() or "0"
        n = int(raw.strip() or 0) + 1
        os.lseek(fd, 0, 0)
        os.ftruncate(fd, 0)
        os.write(fd, str(n).encode())
        return n
    finally:
        os.close(fd)


def hosts_active():
    d = os.path.join(SD, "active")
    n = 0
    for f in os.listdir(d) if os.path.isdir(d) else []:
        if f.startswith("host-"):
            try:
                os.kill(int(f.split("-")[1].split(".")[0]), 0)
                n += 1
            except (OSError, ValueError):
                pass
    return n


def _on_term(sig, frm):
    global _stop
    _stop = True


# ---- the governor's clock -------------------------------------------------------------------------------------------------------------
def active_hosts():
    """[(t0, proc)] of the host stand-ins running now"""
    d = os.path.join(SD, "active")
    out = []
    for f in os.listdir(d) if os.path.isdir(d) else []:
        if not f.startswith("host-"):
            continue
        try:
            os.kill(int(f.split("-")[1].split(".")[0]), 0)
            j = json.load(open(os.path.join(d, f)))
            out.append((float(j["t0"]), int(j["proc"])))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def clock_now(s):
    mode = s.get("clock", "climb")
    if mode == "flat600":
        return 600
    if mode == "hold":
        if os.path.exists(os.path.join(SD, "first-host")):
            return 800
        return 600
    hs = active_hosts()
    if not hs:
        return 800 if (mode == "climb_hold" and os.path.exists(os.path.join(SD, "first-host"))) else 600
    t0, proc = max(hs)
    el = time.time() - t0
    climb = float((s.get("climb_proc") or {}).get(str(proc), s.get("climb_s", 0.9)))
    if el < climb:
        return 600
    for dp in s.get("dip_proc") or []:
        if dp.get("proc") == proc and dp.get("at_s", 0) <= el < dp.get("at_s", 0) + dp.get("for_s", 0.5):
            return dp.get("mhz", 700)
    return 800


# ---- the sampler -------------------------------------------------------------------------------------------------------------------
def sampler(argv):
    s = scen()
    if argv[:1] == ["config"]:
        record("sampler", argv=argv, mode="config", lock_held=lock_held())
        cfg = {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": 519}
        cfg.update(s.get("config", {}))
        sys.stderr.write("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \n")
        sys.stderr.write("PCIe target:                                               %-20s\n" % s.get("config_node", "/dev/et0_mgmt"))
        sys.stderr.write("Physical device ID:                                        %-20s (0x%x)\n" % (s.get("config_id", 0), s.get("config_id", 0)))
        sys.stderr.write("TDP (W):                                                   %-20s\n" % cfg["tdp_w"])
        if s.get("config_none"):
            return 1
        print(json.dumps(cfg))
        return 0
    if argv[:1] != ["sample"]:
        print("stand-in ettelem: unknown subcommand", file=sys.stderr)
        return 2
    secs, every = 60.0, 100
    a = argv[1:]
    for i, x in enumerate(a):
        if x == "--seconds":
            secs = float(a[i + 1])
        if x == "--every-ms":
            every = int(a[i + 1])
        if x.startswith("--reset"):
            record("sampler", argv=argv, refused="reset")
            return 97
    signal.signal(signal.SIGTERM, _on_term)
    signal.signal(signal.SIGINT, _on_term)
    short = secs <= 5
    if short:   # the wrapper's die gate: a short read, its die from the scenario's die_gate list, one value a call
        k = bump("diegate")
        dg = s.get("die_gate") or [s.get("die_idle", 46)]
        dval = dg[min(k - 1, len(dg) - 1)]
        record("sampler", argv=argv, mode="diegate", call=k, die=dval, lock_held=lock_held(), parent=parent_comm())
        if dval is None:
            return 1
        t0 = time.time()
        while time.time() - t0 < secs and not _stop:
            rec = {"t_ms": int(time.time() * 1000), "board_w": 22.4, "sp": {"minion_w": [6.0], "minion_mv": [519]},
                   "temp_c": {"minshire": [dval, dval - 6, dval + 2]}, "mhz": {"minion": 600}}
            sys.stdout.write(json.dumps(rec) + "\n")
            sys.stdout.flush()
            time.sleep(every / 1000.0)
        return 0
    os.makedirs(os.path.join(SD, "active"), exist_ok=True)
    ap = os.path.join(SD, "active", "sampler-%d.json" % os.getpid())
    open(ap, "w").write("{}")
    record("sampler", argv=argv, mode="sample", lock_held=lock_held(), parent=parent_comm())
    t0 = time.time()
    n = 0
    how = "its --seconds"
    try:
        while time.time() - t0 < secs:
            if _stop:
                how = "SIGTERM"
                break
            el = time.time() - t0
            if s.get("quiet_after_s") is not None and el > s["quiet_after_s"]:
                time.sleep(every / 1000.0)
                continue
            w = s.get("idle_w", 24.0) + s.get("host_w", 4.0) * min(1, hosts_active()) + 0.01 * (n % 7)
            bf = s.get("board_w_from")
            if bf and el >= bf["t"]:
                vals = bf["w"]
                w = vals[n % len(vals)]
            bs = s.get("board_w_samples")
            if bs and el >= bs["t"]:
                w = bs["w"]
            d = s.get("die_idle", 46)
            df = s.get("die_from")
            if df and el >= df["t"]:
                d = df["c"]
            latch = d + 2
            lf = s.get("latch_from")
            if lf and el >= lf["t"]:
                latch = lf["c"]
            m = clock_now(s)
            mf = s.get("mhz_from")
            if mf and el >= mf["t"]:
                k = int((el - mf["t"]) / (every / 1000.0))
                if k < mf.get("n", 10 ** 9):
                    m = mf["mhz"]
            rec = {"t_ms": int(time.time() * 1000), "board_w": round(w, 2), "sp": {"minion_w": [round(w * 0.3, 3)],
                   "minion_mv": [519]}, "temp_c": {"minshire": [d, d - 6, latch]}, "mhz": {"minion": m}}
            if s.get("no_mhz"):
                rec.pop("mhz")
            if s.get("no_temp_after_s") is not None and el > s["no_temp_after_s"]:
                rec.pop("temp_c")
            sys.stdout.write(json.dumps(rec) + "\n")
            sys.stdout.flush()
            n += 1
            time.sleep(every / 1000.0)
    finally:
        try:
            os.unlink(ap)
        except OSError:
            pass
        record("sampler", argv=argv, mode="end", how=how, samples=n)
    return 0


# ---- et-who and ps -----------------------------------------------------------------------------------------------------------------
HOLD = """import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], 'w').write('held')
time.sleep(float(sys.argv[3]))
"""


def etwho(argv):
    s = scen()
    k = bump("etwho")
    if s.get("lock_on_etwho_call") == k:   # a holder takes the card lock now; this et-who still answers free (the race between checks)
        hp, flag = os.path.join(SD, "holder2.py"), os.path.join(SD, "holder2.flag")
        open(hp, "w").write(HOLD)
        subprocess.Popen(["/usr/bin/python3", "-I", "-B", hp, LOCK, flag, "20"], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        t0 = time.time()
        while not os.path.exists(flag) and time.time() - t0 < 10:
            time.sleep(0.02)
    lines = []
    d = os.path.join(SD, "active")
    me = os.environ.get("USER") or "user"
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.startswith("sampler-"):
            pid = int(f.split("-")[1].split(".")[0])
            try:
                os.kill(pid, 0)
            except OSError:
                continue
            lines.append("/dev/et0_mgmt %s %d ettelem" % (me, pid))
    fh = s.get("foreign_holder")
    if fh and k >= fh.get("from_call", 1):
        lines.append("/dev/et0_ops otheruser 4242 other_host")
    if "--check" in argv and s.get("etwho_check_sleep_s"):   # a holder check that takes its time (the runbook test's launch case)
        time.sleep(float(s["etwho_check_sleep_s"]))
    if "--check" in argv and s.get("etwho_check_held"):
        lines.append("/dev/et0_ops otheruser 4242 other_host")
    if "--check" in argv and s.get("etwho_ours_reads"):
        kc = bump("etwho-check")
        if kc <= int(s["etwho_ours_reads"]):
            lines.append("/dev/et0_mgmt %s 4343 ettelem" % me)
    record("etwho", argv=argv, call=k, holders=len(lines))
    if not lines:
        print("No process holds an ET-SoC-1 device node or card lock.")
        return 0
    print("NODE           USER        PID  COMMAND")
    for ln in lines:
        print(ln)
    return 1 if "--check" in argv else 0


def ps(argv):
    s = scen()
    k = bump("ps")
    r = subprocess.run(["/usr/bin/ps"] + argv, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    fp = s.get("foreign_proc")
    if fp and k >= fp.get("from_call", 1) and argv[:2] == ["-eo", "uid=,pid=,comm="]:
        sys.stdout.write("    0    4242 other_host\n")
    record("ps", argv=argv, call=k, foreign=bool(fp and k >= fp.get("from_call", 1)))
    return r.returncode


# ---- the host -----------------------------------------------------------------------------------------------------------------------
def table():
    p = os.environ.get("E200_STANDIN_TABLE") or os.path.join(HERE, os.pardir, "e197", "desk", "host-list-e197.jsonl")
    rows = {}
    order = []
    for ln in open(p):
        ln = ln.rstrip("\n")
        if not ln:
            continue
        j = json.loads(ln)
        head = ln[1:ln.index(',"regs":')]          # the host's kindJson text, byte for byte
        rows[j["kind"]] = head
        order.append((j["kind"], ln))
    return rows, order


def regfile_line(head, idx, letter, orient, s, n_proc, t0, t1, wall, bad, ok, window):
    rj = s.get("rate_jitter")
    if rj and rj.get("proc") == n_proc:
        s = dict(s, rate=float(s.get("rate", 5.0e11)) * float(rj.get("factor", 1.05)))
    if s.get("bad_letters_proc") == n_proc and letter in "FS":
        letter = "S" if letter == "F" else "F"
    parts = 1024
    pb = s.get("participants_bad")
    if pb and pb.get("proc") == n_proc:
        parts = pb.get("value", 1023)
    rate = float(s.get("rate", 5.0e11))
    iters = int(rate * 0.4 / 128)
    return ("REGFILE {%s,\"launch\":%d,\"letter\":\"%s\",\"orient\":\"%s\",\"harts\":%d,\"participants\":%d,"
            "\"iters\":%d,\"iters_min\":%d,\"iters_max\":%d,\"instr_body\":%.0f,\"retired_counter\":%d,\"icache_req\":%d,\"icache_miss\":%d,"
            "\"l1d_miss\":%d,\"cycles_max\":%d,\"cycles_mean\":%.0f,\"instr_per_cycle_per_hart\":%.4f,"
            "\"instr_per_s_600\":%.4e,\"ra\":\"%s\",\"gp\":\"%s\",\"deadline\":\"%s\",\"ra_gp_differ\":%d,"
            "\"window\":%d,\"wall_s\":%.4f,\"t_start_ms\":%d,\"t_end_ms\":%d,\"check_bad\":%d,\"ok\":%s}"
            % (head, idx, letter, "" if letter == "-" else orient, 1, parts, iters, iters // parts, iters // parts + 1,
               iters * 128.0, iters * 131, 4000, 40, 8300, window, float(window), 0.8331, rate * (1.0 + 1e-6 * (idx % 3)),
               "0x0000008005801234", "0x0000008005900000", "0x000000000e4e1c00", 0, window, wall, t0, t1, bad,
               "true" if ok else "false"))


def host(argv):
    s = scen()
    rows, order = table()
    o = {"kind": "", "kinds": "", "train": "", "orient": "SFFS", "launches": 0, "seconds": 4.0, "budget": 8.5, "window": 240000000,
         "stop": "", "list": False, "json": False, "kernel": ""}
    i = 0
    while i < len(argv):
        a = argv[i]
        need = a in ("--kind", "--kinds", "--train", "--orient", "--harts", "--shires", "--minions", "--window", "--seconds", "--budget",
                     "--launches", "--kernel", "--stop-file")
        if need and i + 1 >= len(argv):
            sys.stderr.write("%s needs a value\n" % a)
            return 2
        v = argv[i + 1] if need else None
        if a == "--kind": o["kind"] = v
        elif a == "--kinds": o["kinds"] = v
        elif a == "--train": o["train"] = v
        elif a == "--orient": o["orient"] = v
        elif a == "--window": o["window"] = int(v, 0)
        elif a == "--seconds": o["seconds"] = float(v)
        elif a == "--budget": o["budget"] = float(v)
        elif a == "--launches": o["launches"] = int(v, 0)
        elif a == "--kernel": o["kernel"] = v
        elif a == "--stop-file": o["stop"] = v
        elif a in ("--harts", "--shires", "--minions"): pass
        elif a == "--list": o["list"] = True
        elif a == "--json": o["json"] = True
        else:
            sys.stderr.write("unknown option %s\n" % a)
            return 2
        i += 2 if need else 1
    if o["list"]:
        for k, ln in order:
            if o["json"]:
                print(ln)
            else:
                print("(the stand-in's --list prints the json form only)")
                return 2
        return 0
    n_proc = bump("host")
    rec = dict(argv=argv, proc=n_proc, lock_held=lock_held(), parent=parent_comm(),
               stop_existed=bool(o["stop"]) and os.path.exists(o["stop"]))
    try:
        modes = sum(1 for k in ("kind", "kinds", "train") if o[k])
        if modes != 1:
            raise ValueError("give exactly one of --kind, --kinds, --train (or --list)")
        todo = []
        for name in ([o["kind"]] if o["kind"] else (o["train"] or o["kinds"]).split(",")):
            if name not in rows:
                raise ValueError("unknown kind %s (see --list)" % name)
            todo.append(name)
        if o["train"] and len(todo) != 2:
            raise ValueError("--train takes two kinds: F,S")
        if o["train"] and o["orient"] not in ("SFFS", "FSSF"):
            raise ValueError("--orient must be SFFS or FSSF")
        if o["window"] == 0 or o["window"] > 1200000000:
            raise ValueError("--window must be 1 .. 1200000000 cycles")
        if not (0 < o["budget"] <= 9.0):
            raise ValueError("--budget must be in (0, 9] seconds")
        nodes = sorted(int(n[2:-4]) for n in os.listdir("/dev") if n.startswith("et") and n.endswith("_ops") and n[2:-4].isdigit())
        if not nodes:
            raise ValueError("no card node /dev/et<N>_ops on this host")
        sel = os.environ.get("ET_DEVICES", "")
        if sel:
            if not sel.isdigit():
                raise ValueError("ET_DEVICES must be one card index, not '%s'" % sel)
            if int(sel) not in nodes:
                raise ValueError("ET_DEVICES=%s: no such card node" % sel)
        if len(nodes) > 1 and not sel:
            raise ValueError("%d cards on this host and ET_DEVICES unset: refusing to open every card" % len(nodes))
        if o["kernel"] and not os.path.exists(o["kernel"]):
            raise ValueError("cannot read kernel %s" % o["kernel"])
    except ValueError as e:
        sys.stderr.write("FAIL: %s\n" % e)
        rec.update(refused=str(e))
        record("host", **rec)
        return 1
    hr = s.get("host_rc")
    if hr and (hr.get("proc") == n_proc or n_proc in hr.get("procs", [])):
        rec.update(rc=hr.get("rc", 1), launches=0)
        record("host", **rec)
        sys.stderr.write("FAIL: the stand-in's fault: exit %d\n" % hr.get("rc", 1))
        return hr.get("rc", 1)
    got = []
    hg = s.get("hang_proc")
    if hg and hg.get("proc") == n_proc:
        def _note(sig, frm):
            got.append((sig, time.time()))
            record("host", proc=n_proc, signal=sig, note="ignored: the stand-in hangs in teardown")
        signal.signal(signal.SIGTERM, _note)
    os.makedirs(os.path.join(SD, "active"), exist_ok=True)
    ap = os.path.join(SD, "active", "host-%d.json" % os.getpid())
    open(ap, "w").write(json.dumps({"proc": n_proc, "t0": time.time()}))
    open(os.path.join(SD, "first-host"), "a").close()
    t_open = time.time()
    launch_s = float(s.get("launch_s", 0.02))
    time.sleep(float(s.get("open_s", 0.0)))
    sys.stderr.write("device ready in %.2f s\n" % (time.time() - t_open))
    nl = 0
    rc = 0
    out = sys.stdout

    span = float(s.get("report_span_s", 0.4))
    base = []

    def emit(idx, letter, kind):
        nonlocal nl
        if not base:
            now_ms = int(time.time() * 1000)
            if launch_s < span:   # the fast pace: reported spans run ahead and overlap the next processes'; a per-process offset
                # (the process's number mod 400 ms on a 400 ms grid) keeps every launch's reported start unique among them, as a card's are
                now_ms = (now_ms // 400) * 400 + (n_proc % 400)
            base.append(now_ms)
        t0 = base[0] + int(round(1000 * span * idx))          # the span it reports: launch idx of a card's 0.4 s launches
        t1 = base[0] + int(round(1000 * span * (idx + 1)))
        time.sleep(launch_s)
        wall = span
        om = s.get("own_mhz_proc")
        if om and om.get("proc") == n_proc and o["train"] and idx == (o["launches"] or 13) - 1:
            wall = o["window"] / (float(om.get("mhz", 600)) * 1e6)
        bad = 1 if s.get("check_bad_proc") == n_proc else 0
        line = regfile_line(rows[kind], idx, letter, o["orient"], s, n_proc, t0, t1, wall, bad, not bad, o["window"])
        sp = s.get("split_proc")
        bp = s.get("between_proc")
        if s.get("notdict_proc") == n_proc and idx == 0:
            out.write("REGFILE 5\n")
        elif sp and sp.get("proc") == n_proc and sp.get("launch", 0) == idx:
            at = int(sp.get("at", len(line) // 2))
            out.write(line[:at] + sp.get("runtime", "Opening device 1\n") + line[at:] + "\n")
        else:
            if bp and bp.get("proc") == n_proc and idx == 1:
                out.write(bp.get("runtime", "Opening device 0\n"))
            out.write(line + "\n")
        out.flush()
        nl += 1
        return not bad

    def fits():  # main.cpp's launchFits: the time held + one launch at the slowest clock (1.2 x the 600 MHz launch) + 1 s <= budget
        return time.time() - t_open + launch_s * 1.2 + 1.0 <= o["budget"]

    def stopped():
        return bool(o["stop"]) and os.path.exists(o["stop"])

    try:
        if o["train"]:
            L = o["launches"] or 13
            for n in range(L):
                if stopped() or not fits():
                    sys.stderr.write("train ended early at launch %d (stop file or --budget): this process gives no value\n" % n)
                    rc = 3
                    break
                letter = o["orient"][0] if n == 0 else o["orient"][(n - 1) % 4]
                if not emit(n, letter, todo[0] if letter == "F" else todo[1]):
                    rc = 1
                    break
        else:
            t_start = time.time()
            n = 0
            while (n < o["launches"] if o["launches"] else time.time() - t_start < o["seconds"] * (launch_s / 0.4)) and fits() \
                    and not stopped():
                if not emit(n, "-", todo[0]):
                    rc = 1
                    break
                n += 1
        if hg and hg.get("proc") == n_proc:
            t_end = time.time() + float(hg.get("live_s", 14))
            while time.time() < t_end:
                time.sleep(0.1)
        sys.stderr.write("device held for %.2f s\n" % (time.time() - t_open))
        time.sleep(float(s.get("teardown_s", 0.0)))
    finally:
        try:
            os.unlink(ap)
        except OSError:
            pass
        rec.update(rc=rc, launches=nl, signals=[g[0] for g in got], stop_at_end=bool(o["stop"]) and os.path.exists(o["stop"]))
        record("host", **rec)
    return rc


def main():
    role = os.environ.get("E200_STANDIN_ROLE")
    argv = sys.argv[1:]
    base = os.path.basename(sys.argv[0])
    if not role:
        role = {"et-who": "etwho", "ps": "ps", "ettelem": "sampler", "regfile_host": "host"}.get(base)
    if not role and argv:
        role, argv = argv[0], argv[1:]
    fn = {"sampler": sampler, "etwho": etwho, "ps": ps, "host": host}.get(role)
    if not fn:
        print(__doc__)
        return 2
    return fn(argv)


if __name__ == "__main__":
    sys.exit(main())
