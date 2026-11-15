#!/usr/bin/env python3
"""E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum): THE STAND-INS for the real-path desk test
(desk/desktest_realpath_e192.sh) and the runbook desk test's stand-in box. NOTHING HERE OPENS A DEVICE OR SENDS A COMMAND; nothing here
is measured or forecast. Each role answers the session's real path the way the box's tool does, in the tool's own output form, from a
small card model shared through a state directory (E192_STANDIN_DIR):

  sampler  the box's `build/ettelem/ettelem sample --seconds T --every-ms 100` (and `config`): 10 Hz JSON lines in ettelem's keys
           (board_w; sp.minion_w, sp.minion_mv; temp_c.minshire whole degrees; mhz.minion), until T or SIGTERM (logged: the session must
           stop it with SIGTERM, never SIGKILL);
  pvt      E89's `pvt_sample.py --seconds T --every-ms 100` and `--probe` (three ticks and its verdict line): the same keys and "pvt"
           {st, f, c: 34 raw codes, 0.061 C a code, the reducer's own conversion inverted};
  heater   E78's heater `build/sparsity/host/sparsity_host --test fma ... --seconds 2 --seed 1 --stop-file F`: its option parser (an
           unknown option exits 2 before anything), no launch once F exists, 2 s "active" (the die model heats);
  host     the intbits host `--arm A --seconds S --window W --stop-file F` (and `--list --json`): the real host's node count first
           (/dev/et<N>_ops: none is "FAIL: no card node", exit 1), then 0.4 s launches until S, the budget (8.5 s) or F, each printing
           one INTBITS line in the host's form (the arm's fields from the registered table desk/arm-table-e192.jsonl);
  etwho    `et-who [--check]`: "No process holds an ET-SoC-1 device node or card lock" (exit 0), or one holder line per running sampler
           stand-in ("/dev/et0_mgmt <login> <pid> <comm>": the session's own sampler, as et-who shows it) and any foreign holder the
           scenario names (exit 1 with --check);
  ps       /usr/bin/ps, plus another user's device process when the scenario names one.
Every call is appended to E192_STANDIN_DIR/calls/<role>.log (one JSON line: times, argv, whether the card lock was held by another
open file at the call, whether the stop file existed). The scenario (E192_STANDIN_DIR/scenario.json) sets the model's numbers and the
faults: heater_w, host_w, host_tss, host_w_from {n, w} (the n-th host process and later), host_tss_from {n, tss}, check_bad_arm with
check_bad_upto (host processes 1..upto), participants, stall_after_s, pvt_probe_fail, etwho ("foreign", "foreign_after_pass0"),
foreign_proc, scale (the host's seconds and launch length times this: a shorter stand-in run), mhz.
Added in place by fix-e192 (Q176, Sat 14 Nov 2026 evening, before the land) for the branches verify-e192 found unrun (its break knobs,
ported from its standin_brk.py, and four more): heater_rc with heater_rc_n (the n-th heater call exits so, launching nothing);
participants_bad with participants_upto; host_lines_max with host_lines_upto (at most that many INTBITS lines); bad_json_at (that host
process prints a malformed INTBITS line); host_rc with host_rc_upto (host processes 1..upto exit so); etwho_foreign_on_call (a foreign
holder from that et-who call on); foreign_proc_after_pass0; and fix-e192's own: etwho_fail_on_call (that et-who call fails, exit 2),
foreign_proc_on_call (another user's device process from that `ps -eo uid=,pid=,comm=` call on), etwho_takes_lock_on_call (that et-who
call answers free AFTER a holder has taken the card lock: the lock taken between a free et-who and the lock probe; the holder is
E192_STANDIN_DIR/holder.py, its pid in holder.pid, held lock_hold_s seconds), board_w_absent (no board reading in any sample), and
lock_on_sha256_of (the role sha256sum, a stand-in for coreutils' sha256sum put first on PATH by one case only: given a path ending so, it
takes the card lock by the same holder before it hashes; every other call is the real /usr/bin/sha256sum).
    python3 -I -B standin_e192.py <role> [args...]          (or E192_STANDIN_ROLE=<role>)
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import math
import os
import pwd
import random
import signal
import subprocess
import sys
import time

SD = os.environ.get("E192_STANDIN_DIR", "")
LOCK = "/run/lock/etsoc-shire0.lock"
G_TS, H_TS, CAL5 = 57400, 249400, 4096       # the reducer's per-sensor conversion (reduce_intbits.py line 64), inverted below
_stop = False


def scen():
    try:
        return json.load(open(os.path.join(SD, "scenario.json")))
    except (OSError, ValueError):
        return {}


def lock_held():
    """True when another open file holds the card lock (the session's fd 9, or flock(1)); None when there is no lock file."""
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


def active(kind, **kw):
    d = os.path.join(SD, "active")
    os.makedirs(d, exist_ok=True)
    kw["kind"] = kind
    p = os.path.join(d, "%s-%d.json" % (kind, os.getpid()))
    with open(p, "w") as f:
        json.dump(kw, f)
    return p


def _on_term(sig, frm):
    global _stop
    _stop = True


def take_lock_by_holder(seconds):
    """fix-e192: start a holder of the card lock (E192_STANDIN_DIR/holder.py, its own session) and return once it holds the lock."""
    hp = os.path.join(SD, "holder.py")
    flag = os.path.join(SD, "holder.flag")
    with open(hp, "w") as f:
        f.write("import fcntl, os, time\nfd = os.open(%r, os.O_RDONLY)\nfcntl.flock(fd, fcntl.LOCK_EX)\nopen(%r, 'w').write('held')\n"
                "time.sleep(%d)\n" % (LOCK, flag, int(seconds)))
    if os.path.exists(flag):
        os.unlink(flag)
    p = subprocess.Popen(["/usr/bin/python3", "-I", "-B", hp], start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open(os.path.join(SD, "holder.pid"), "w").write("%d\n" % p.pid)
    t0 = time.time()
    while not os.path.exists(flag) and time.time() - t0 < 10:
        time.sleep(0.02)
    return os.path.exists(flag)


# ---- the samplers ------------------------------------------------------------------------------------------------------------
def sample_loop(role, seconds, every_ms, probe=False, argv=None):
    s = scen()
    signal.signal(signal.SIGTERM, _on_term)
    signal.signal(signal.SIGINT, _on_term)
    rng = random.Random(os.getpid())
    T = float(s.get("t_idle", 56.0))
    k = 0.5
    t0 = time.time()
    last = t0
    n = 0
    period = every_ms / 1000.0
    record(role, event="start", argv=list(argv if argv is not None else sys.argv[1:]), lock_held=lock_held())
    stalled = False
    while not _stop and time.time() - t0 < seconds:
        now = time.time()
        dt = now - last
        last = now
        tss, w = float(s.get("t_idle", 56.0)), 30.0
        acts = []
        try:
            for fn in os.listdir(os.path.join(SD, "active")):
                try:
                    acts.append(json.load(open(os.path.join(SD, "active", fn))))
                except (OSError, ValueError):
                    pass
        except OSError:
            pass
        heat = [x for x in acts if x.get("kind") == "heater"]
        host = [x for x in acts if x.get("kind") == "host"]
        if heat:
            tss, w = heat[0]["tss"], heat[0]["w"]
        elif host:
            tss, w = host[0]["tss"], host[0]["w"]
        T += (tss - T) * (1.0 - math.exp(-k * dt))
        board = w + 0.3 * (T - 56.0) + rng.gauss(0, 0.05)
        rail = 0.79 * (board - 22.0) + rng.gauss(0, 0.02)
        rec = {"t_ms": int(now * 1000), "board_w": round(board, 3),
               "sp": {"minion_w": [round(rail, 3)], "minion_mv": [522 + rng.choice((-1, 0, 0, 1))]},
               "temp_c": {"pmic": 41, "ioshire": [int(T) - 3], "minshire": [int(round(T)), int(round(T)) + 2, int(round(T)) - 1]},
               "mhz": {"minion": int(s.get("mhz", 600)), "noc": 400, "ddr": 800}, "since_reset_ms": -1}
        if s.get("board_w_absent"):
            del rec["board_w"]
        if role == "pvt":
            codes = []
            for i in range(34):
                c = T + 0.2 * math.sin(i)
                codes.append(int(round((c * 1000.0 - G_TS + H_TS / 2.0) * CAL5 / H_TS)))
            rec["pvt"] = {"st": 0, "f": 0, "c": codes}
        if s.get("stall_after_s") is not None and now - t0 > float(s["stall_after_s"]):
            if not stalled:
                record(role, event="stall", lines=n)
                stalled = True
        else:
            sys.stdout.write(json.dumps(rec, separators=(",", ":")) + "\n")
            sys.stdout.flush()
            n += 1
        if probe and n >= 3:
            break
        time.sleep(max(0.0, period - (time.time() - now)))
    if probe:
        ok = not s.get("pvt_probe_fail")
        print(json.dumps({"probe": "pvt_sample", "ticks": n, "cmd74_ok_ticks": n if ok else 0, "cmd74": ok, "skipped_stale": 0}))
        record(role, event="probe_end", lines=n, cmd74=ok)
        return 0 if ok else 5
    record(role, event="exit_on_sigterm" if _stop else "exit_at_seconds", lines=n)
    return 0


def role_sampler(args):
    if args and args[0] == "config":
        record("sampler", event="config", argv=args, lock_held=lock_held())
        print(json.dumps({"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523, "power_state": "standin"},
                         separators=(",", ":")))
        return 0
    if not args or args[0] != "sample":
        print("standin ettelem: unknown subcommand %s" % args[:1], file=sys.stderr)
        return 2
    if "--reset-ms" in args or "--reset-once-file" in args:
        print("standin ettelem: a statistics reset was asked for: refused (the kit never sends one)", file=sys.stderr)
        record("sampler", event="refused_reset", argv=args)
        return 2
    sec = float(args[args.index("--seconds") + 1]) if "--seconds" in args else 10.0
    ev = int(args[args.index("--every-ms") + 1]) if "--every-ms" in args else 100
    return sample_loop("sampler", sec, ev, argv=args)


def role_pvt(args):
    probe = "--probe" in args
    sec = float(args[args.index("--seconds") + 1]) if "--seconds" in args else 10.0
    ev = int(args[args.index("--every-ms") + 1]) if "--every-ms" in args else 100
    return sample_loop("pvt", sec, ev, probe=probe, argv=args)


# ---- the device programs -----------------------------------------------------------------------------------------------------
HEATER_OPTS_VAL = {"--sim-args", "--test", "--type", "--pattern", "--values", "--dump-tiles", "--stop-file", "--sweep", "--b-sparsity",
                   "--row-mask", "--where", "--masks", "--gemv", "--variant", "--alpha", "--mean-k", "--kmax", "--items", "--harts",
                   "--iters", "--shires", "--per-shire", "--seconds", "--seed", "--budget", "--kernel"}
HEATER_OPTS_FLAG = {"--sysemu", "--b-stream", "--gemv-tree"}


def role_heater(args):
    o, i = {}, 0
    while i < len(args):
        a = args[i]
        if a in HEATER_OPTS_FLAG:
            o[a] = True
        elif a in HEATER_OPTS_VAL:
            if i + 1 >= len(args):
                print("%s needs a value" % a, file=sys.stderr)
                return 2
            o[a] = args[i + 1]
            i += 1
        else:
            print("unknown option %s (see the comment at the top of host/main.cpp)" % a, file=sys.stderr)
            return 2
        i += 1
    s = scen()
    stop = o.get("--stop-file", "")
    n = bump("heater")
    if s.get("heater_rc") is not None and n == int(s.get("heater_rc_n", 1)):
        record("heater", event="call", argv=args, n=n, forced_rc=int(s["heater_rc"]), lock_held=lock_held(), launched=False)
        print("FAIL: the stand-in heater's forced exit (desk test)", file=sys.stderr)
        return int(s["heater_rc"])
    rec = dict(event="call", argv=args, n=n, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop))
    if stop and os.path.exists(stop):
        record("heater", launched=False, **rec)
        return 0
    t0 = time.time()
    p = active("heater", tss=float(s.get("heater_tss", 66.0)), w=float(s.get("heater_w", 49.0)))
    secs = float(o.get("--seconds", 2.0))
    while time.time() - t0 < secs:
        if stop and os.path.exists(stop):
            break
        time.sleep(0.1)
    os.unlink(p)
    t1 = time.time()
    print('SPARSITY {"test":"fma","standin":true,"wall_s":%.3f,"t_start_ms":%d,"t_end_ms":%d,"ok":true}' % (t1 - t0, t0 * 1000, t1 * 1000))
    record("heater", launched=True, t0=t0, t1=t1, **rec)
    return 0


def card_nodes():
    v = []
    try:
        for n in os.listdir("/dev"):
            if n.startswith("et") and n.endswith("_ops") and n[2:-4].isdigit():
                v.append(int(n[2:-4]))
    except OSError:
        pass
    return sorted(v)


def role_host(args):
    o, i = {}, 0
    flags = {"--list", "--json"}
    while i < len(args):
        a = args[i]
        if a in flags:
            o[a] = True
        elif a.startswith("--"):
            if i + 1 >= len(args):
                print("%s needs a value" % a, file=sys.stderr)
                return 2
            o[a] = args[i + 1]
            i += 1
        else:
            print("unknown option %s" % a, file=sys.stderr)
            return 2
        i += 1
    table = os.environ.get("E192_STANDIN_TABLE") or os.path.join(SD, "arm-table.jsonl")
    rows = {}
    for ln in open(table):
        if ln.startswith("{"):
            r = json.loads(ln)
            rows[r["arm"]] = r
    if o.get("--list"):
        for ln in open(table):
            sys.stdout.write(ln)
        return 0
    nodes = card_nodes()
    if not nodes:
        print("FAIL: no card node /dev/et<N>_ops on this host", file=sys.stderr)
        record("host", event="refused_no_node", argv=args)
        return 1
    if len(nodes) > 1 and not os.environ.get("ET_DEVICES"):
        print("FAIL: %d cards on this host and ET_DEVICES unset: refusing to open every card" % len(nodes), file=sys.stderr)
        return 1
    arm = o.get("--arm")
    if arm not in rows:
        print("FAIL: unknown arm %s (see --list)" % arm, file=sys.stderr)
        return 1
    s = scen()
    n = bump("host")
    scale = float(s.get("scale", 1.0))
    seconds = float(o.get("--seconds", 4.0))
    budget = float(o.get("--budget", 8.5))
    window = int(o.get("--window", 240000000))
    stop = o.get("--stop-file", "")
    w, tss = float(s.get("host_w", 40.0)), float(s.get("host_tss", 64.0))
    if s.get("host_w_from") and n >= int(s["host_w_from"]["n"]):
        w = float(s["host_w_from"]["w"])
    if s.get("host_tss_from") and n >= int(s["host_tss_from"]["n"]):
        tss = float(s["host_tss_from"]["tss"])
    cb_arm, cb_upto = s.get("check_bad_arm"), int(s.get("check_bad_upto", 0))
    part = int(s.get("participants", 1024))
    if s.get("participants_bad") is not None and n <= int(s.get("participants_upto", 0)):
        part = int(s["participants_bad"])
    max_lines = int(s["host_lines_max"]) if (s.get("host_lines_max") is not None and n <= int(s.get("host_lines_upto", 0))) else None
    rec = dict(event="call", argv=args, n=n, arm=arm, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop))
    t_open = time.time()
    t_start = t_open
    launch_s = 0.4 * scale
    k = 0
    p = None
    r = rows[arm]
    keys = ("arm", "form", "op", "a0", "b0", "a1", "b1", "r0", "r1", "n_port_a", "n_port_b", "n_result", "n_carry", "n_cell", "n_enc")
    while (time.time() - t_start < seconds * scale and time.time() - t_open + launch_s + 1.0 <= budget
           and not (stop and os.path.exists(stop))):
        if p is None:
            p = active("host", arm=arm, tss=tss, w=w)
        l0 = time.time()
        time.sleep(launch_s)
        l1 = time.time()
        iters = int(window * 0.95 / 259) * 1024
        instr = iters * 256
        cyc = window + 77
        bad = 1 if (cb_arm == arm and n <= cb_upto) else 0
        line = "INTBITS {" + ",".join('"%s":%s' % (key, json.dumps(r[key])) for key in keys) + (
            ',"harts":1,"participants":%d,"iters":%d,"instr_body":%.0f,"retired_counter":%d,"icache_req":%d,"icache_miss":128,'
            '"l1d_miss":0,"cycles_max":%d,"cycles_mean":%.0f,"instr_per_cycle_per_hart":%.4f,"instr_per_s_600":%.4e,"window":%d,'
            '"wall_s":%.4f,"t_start_ms":%d,"t_end_ms":%d,"check_bad":%d,"ok":%s}') % (
            part, iters, float(instr), instr * 259 // 256, iters // 4, cyc, cyc - 50.0, instr / cyc / part, instr / (cyc / 0.6e9),
            window, l1 - l0, int(l0 * 1000), int(l1 * 1000), bad, "false" if bad else "true")
        if s.get("bad_json_at") is not None and n == int(s["bad_json_at"]):
            line = 'INTBITS {"arm": "' + arm + '", "broken'
        print(line, flush=True)
        k += 1
        if max_lines is not None and k >= max_lines:
            break
    if p:
        os.unlink(p)
    record("host", launches=k, t0=t_start, t1=time.time(), stop_at_end=bool(stop) and os.path.exists(stop), **rec)
    if s.get("host_rc") is not None and n <= int(s.get("host_rc_upto", 0)):
        return int(s["host_rc"])
    return 0


# ---- the readers ---------------------------------------------------------------------------------------------------------------
def our_samplers():
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == os.getpid():
            continue
        try:
            cl = open("/proc/%s/cmdline" % d, "rb").read().split(b"\0")
        except OSError:
            continue
        words = [w.decode(errors="ignore") for w in cl if w]
        if any(w.endswith("pvt_standin.py") for w in words) and "--probe" not in words:
            out.append(int(d))
        elif any(w.endswith("standin_e192.py") for w in words) and "sampler" in words and "sample" in words:
            out.append(int(d))
    return sorted(out)


def role_etwho(args):
    s = scen()
    me = pwd.getpwuid(os.getuid()).pw_name
    kcall = bump("etwho")
    if s.get("etwho_fail_on_call") is not None and kcall == int(s["etwho_fail_on_call"]):
        record("etwho", argv=args, holders=None, call=kcall, failed=True)
        print("et-who: cannot read /proc (desk-test stand-in)", file=sys.stderr)
        return 2
    if s.get("etwho_takes_lock_on_call") is not None and kcall == int(s["etwho_takes_lock_on_call"]):
        held = take_lock_by_holder(float(s.get("lock_hold_s", 20)))
        record("etwho", event="lock_taken_by_holder", call=kcall, held=held)
    lines = ["/dev/et0_mgmt %s %d python3" % (me, p) for p in our_samplers()]
    if s.get("etwho_foreign_on_call") is not None and kcall >= int(s["etwho_foreign_on_call"]):
        lines.append("/dev/et0_ops otheruser 4242 foo_host")
    fo = s.get("etwho")
    if fo == "foreign":
        lines.append("/dev/et0_ops otheruser 4242 foo_host")
    elif fo == "foreign_after_pass0":
        rd = open(os.path.join(SD, "rundir")).read().strip() if os.path.exists(os.path.join(SD, "rundir")) else ""
        try:
            for ln in open(os.path.join(rd, "marks.jsonl")):
                m = json.loads(ln)
                if m.get("kind") == "idle" and m.get("label") == "after" and m.get("pass") == 0:
                    lines.append("/dev/et0_ops otheruser 4242 foo_host")
                    break
        except (OSError, ValueError):
            pass
    record("etwho", argv=args, holders=len(lines))
    if not lines:
        print("No process holds an ET-SoC-1 device node or card lock")
        return 0
    print("NODE          USER        PID    COMMAND")
    for ln in lines:
        print(ln)
    return 1 if "--check" in args else 0


def role_ps(args):
    s = scen()
    r = subprocess.run(["/usr/bin/ps"] + args, capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    holder_query = args == ["-eo", "uid=,pid=,comm="]
    kcall = bump("ps") if holder_query else 0
    if s.get("foreign_proc") and holder_query:
        print(" 4242   99999 foo_host")
    elif s.get("foreign_proc_on_call") is not None and holder_query and kcall >= int(s["foreign_proc_on_call"]):
        print(" 4242   99999 foo_host")
    elif s.get("foreign_proc_after_pass0") and holder_query:
        rd = open(os.path.join(SD, "rundir")).read().strip() if os.path.exists(os.path.join(SD, "rundir")) else ""
        try:
            for ln in open(os.path.join(rd, "marks.jsonl")):
                m = json.loads(ln)
                if m.get("kind") == "idle" and m.get("label") == "after" and m.get("pass") == 0:
                    print(" 4242   99999 foo_host")
                    break
        except (OSError, ValueError):
            pass
    record("ps", argv=args, call=kcall)
    return r.returncode


def role_sha256sum(args):
    """fix-e192: put first on PATH by one desk case only. Given a path ending in the scenario's lock_on_sha256_of, it first has the card
    lock taken by a holder (the lock taken between the wrapper's own lock probe and its probe's flock); then, always, the real
    /usr/bin/sha256sum with the same arguments."""
    s = scen()
    want = s.get("lock_on_sha256_of")
    if want and any(a.endswith(want) for a in args):
        held = take_lock_by_holder(float(s.get("lock_hold_s", 20)))
        record("sha256sum", event="lock_taken_by_holder", argv=args, held=held)
    sys.stdout.flush()
    os.execv("/usr/bin/sha256sum", ["sha256sum"] + list(args))


ROLES = {"sampler": role_sampler, "pvt": role_pvt, "heater": role_heater, "host": role_host, "etwho": role_etwho, "ps": role_ps,
         "sha256sum": role_sha256sum}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ROLES:
        role, rest = sys.argv[1], sys.argv[2:]
    else:
        role, rest = os.environ.get("E192_STANDIN_ROLE", ""), sys.argv[1:]
    if role not in ROLES:
        print("standin_e192.py: give a role: " + ", ".join(ROLES), file=sys.stderr)
        sys.exit(2)
    sys.exit(ROLES[role](rest))
