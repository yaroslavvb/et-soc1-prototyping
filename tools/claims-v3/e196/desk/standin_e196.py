#!/usr/bin/env python3
"""E196's kit (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE STAND-INS for the real-path desk test
(desk/desktest_realpath_e196.sh) and the runbook desk test's stand-in box. E192's stand-ins' form (tools/claims-v3/e192/desk/
standin_e192.py), with E196's two hosts. NOTHING HERE OPENS A DEVICE OR SENDS A COMMAND; nothing here is measured or forecast. Each role
answers the session's real path the way the box's tool does, in the tool's own output form, from a small card model shared through a
state directory (E196_STANDIN_DIR):

  sampler  the box's build/ettelem/ettelem behind E128's guard: `sample --seconds T --every-ms 100` (10 Hz JSON lines in ettelem's keys:
           board_w; sp.minion_w, sp.minion_mv; temp_c.minshire whole degrees; mhz.minion; until T or SIGTERM, logged: the session must
           stop it with SIGTERM) and `config` (one JSON line: tdp_w, temp_threshold_c, minion_mhz, ...);
  lab      the lab's unchanged sparsity host (build/sparsity-lab/host/sparsity_host): its option parser (an unknown option exits 2 before
           anything; --label is unknown to it), the node count first (/dev/et<N>_ops: none is "FAIL", exit 1), a calibration launch then
           launches of about 0.5 s for --seconds, never past its 8 s budget, none once the stop file exists; each prints one SPARSITY line
           in main.cpp's printf form (line 617: the keys and their order), 546 cycles an op unmasked or with every row enabled, 544 with a
           row masked; --values randn is the heater (the die model heats);
  x14      the request's x14_host (build/x14/host/x14_host): its option parser and refusals (--abba, --launches, --budget, 16-bit masks),
           the node count; a calibration launch, its read-back of C (X14CHECK), launches (--seconds, or a train's --launches with the
           A B B A kinds), the read-back after the last launch; X14 and X14CHECK lines in main.cpp's printf forms (lines 454 and 473);
  etwho    `et-who [--check]`: "No process holds an ET-SoC-1 device node or card lock" (exit 0), or a holder line per running sampler
           stand-in (our own sampler, as et-who shows it) and any foreign holder the scenario names (exit 1 with --check);
  ps       /usr/bin/ps, plus another user's device process when the scenario names one.
Every call is appended to E196_STANDIN_DIR/calls/<role>.log (one JSON line: times, argv, whether the card lock was held by another open
file at the call, whether the stop file existed). The scenario (E196_STANDIN_DIR/scenario.json) sets the numbers and the faults:
  t_idle, heater_tss, heater_w, host_w, host_tss, host_w_from {n, w, role} (the n-th call of that role and later), host_tss_from;
  scale (the launch length times this); mhz; config_tdp, config_mhz; stall_after_s; board_w_absent;
  runtime_every (every n-th host process prints "Opening device 0" INSIDE its second line, at a seeded offset: aifoundry1's form);
  bad_line_lab_at / bad_line_x14_at (that call prints a line with unknown text inside it: unreadable), bad_line_values with
  bad_line_nth (the nth lab run whose --values holds that text does so); lab_rc_at, heater_rc_at;
  check_bad_arm (a premise run of that arm reads its C back not ok); lab_cycles_546_arm (that arm's lab runs read 546 cycles though masked);
  tensor_err_arm; etwho ("foreign", "foreign_after_block": block number in the run's marks), etwho_foreign_on_call; foreign_proc,
  foreign_proc_after_block; x14_scale (the x14 host's launch length times this, for short train blocks).
    python3 -I -B standin_e196.py <role> [args...]
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

SD = os.environ.get("E196_STANDIN_DIR", "")
LOCK = "/run/lock/etsoc-shire0.lock"
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


def run_marks_blocks():
    """the blocks whose 'after' idle mark is in the session's marks.jsonl (the rundir the test recorded)"""
    rd = open(os.path.join(SD, "rundir")).read().strip() if os.path.exists(os.path.join(SD, "rundir")) else ""
    out = set()
    try:
        for ln in open(os.path.join(rd, "marks.jsonl")):
            m = json.loads(ln)
            if m.get("kind") == "idle" and m.get("label") == "after":
                out.add(m.get("pass"))
    except (OSError, ValueError):
        pass
    return out


# ---- the sampler ---------------------------------------------------------------------------------------------------------------
def sample_loop(seconds, every_ms, argv):
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
    record("sampler", event="start", argv=list(argv), lock_held=lock_held())
    stalled = False
    while not _stop and time.time() - t0 < seconds:
        now = time.time()
        dt = now - last
        last = now
        tss, w = float(s.get("t_idle", 56.0)), 26.0
        acts = []
        try:
            for fn in os.listdir(os.path.join(SD, "active")):
                try:
                    acts.append(json.load(open(os.path.join(SD, "active", fn))))
                except (OSError, ValueError):
                    pass
        except OSError:
            pass
        if acts:
            a = max(acts, key=lambda x: x.get("w", 0))
            tss, w = a["tss"], a["w"]
        T += (tss - T) * (1.0 - math.exp(-k * dt))
        board = w + 0.2 * (T - 56.0) + rng.gauss(0, 0.04)
        rail = 0.79 * (board - 22.0) + rng.gauss(0, 0.02)
        rec = {"t_ms": int(now * 1000), "board_w": round(board, 3),
               "sp": {"minion_w": [round(rail, 3)], "minion_mv": [522 + rng.choice((-1, 0, 0, 1))]},
               "temp_c": {"pmic": 41, "ioshire": [int(T) - 3], "minshire": [int(round(T)), int(round(T)) + 2, int(round(T)) - 1]},
               "mhz": {"minion": int(s.get("mhz", 600)), "noc": 400, "ddr": 800}, "since_reset_ms": -1}
        if s.get("board_w_absent"):
            del rec["board_w"]
        if s.get("stall_after_s") is not None and now - t0 > float(s["stall_after_s"]):
            if not stalled:
                record("sampler", event="stall", lines=n)
                stalled = True
        else:
            sys.stdout.write(json.dumps(rec, separators=(",", ":")) + "\n")
            sys.stdout.flush()
            n += 1
        time.sleep(max(0.0, period - (time.time() - now)))
    record("sampler", event="exit_on_sigterm" if _stop else "exit_at_seconds", lines=n)
    return 0


def role_sampler(args):
    s = scen()
    if args and args[0] == "config":
        record("sampler", event="config", argv=args, lock_held=lock_held())
        print("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: (stand-in)", file=sys.stderr)
        print(json.dumps({"tdp_w": int(s.get("config_tdp", 0)), "temp_threshold_c": 65, "power_state": 0,
                          "power_state_name": "max_power", "minion_mhz": int(s.get("config_mhz", 600)), "minion_mv": 523},
                         separators=(",", ":")))
        return 0
    if not args or args[0] != "sample":
        print("standin ettelem: unknown subcommand %s" % args[:1], file=sys.stderr)
        return 2
    if "--reset-ms" in args or "--reset-once-file" in args:
        record("sampler", event="refused_reset", argv=args)
        return 2
    sec = float(args[args.index("--seconds") + 1]) if "--seconds" in args else 10.0
    ev = int(args[args.index("--every-ms") + 1]) if "--every-ms" in args else 100
    return sample_loop(sec, ev, args)


# ---- the two hosts -------------------------------------------------------------------------------------------------------------
LAB_VAL = {"--sim-args", "--test", "--type", "--pattern", "--values", "--dump-tiles", "--stop-file", "--sweep", "--b-sparsity", "--row-mask",
           "--where", "--masks", "--gemv", "--variant", "--alpha", "--mean-k", "--kmax", "--items", "--harts", "--iters", "--shires",
           "--per-shire", "--seconds", "--seed", "--budget", "--kernel"}
LAB_FLAG = {"--sysemu", "--b-stream", "--gemv-tree"}
X14_VAL = {"--values", "--label", "--dump-tiles", "--stop-file", "--row-mask", "--zero-rows", "--live-rows", "--values-b", "--label-b",
           "--row-mask-b", "--zero-rows-b", "--live-rows-b", "--abba", "--launches", "--iters", "--shires", "--per-shire", "--seconds",
           "--seed", "--budget", "--kernel"}


def parse(args, val, flag=()):
    o, i = {}, 0
    while i < len(args):
        a = args[i]
        if a in flag:
            o[a] = True
        elif a in val:
            if i + 1 >= len(args):
                print("%s needs a value" % a, file=sys.stderr)
                return None
            o[a] = args[i + 1]
            i += 1
        else:
            print("unknown option %s (see the comment at the top of host/main.cpp)" % a, file=sys.stderr)
            return None
        i += 1
    return o


def card_nodes():
    v = []
    try:
        for n in os.listdir("/dev"):
            if n.startswith("et") and n.endswith("_ops") and n[2:-4].isdigit():
                v.append(int(n[2:-4]))
    except OSError:
        pass
    return sorted(v)


def emit(line, split):
    """print one host line; with split, "Opening device 0" goes INSIDE it at a seeded offset (aifoundry1's runtime, 1a4bc1e3)"""
    if split:
        k = random.Random(len(line)).randrange(1, len(line) - 1)
        sys.stdout.write(line[:k])
        sys.stdout.flush()
        sys.stdout.write("Opening device 0\n")
        sys.stdout.write(line[k:] + "\n")
    else:
        sys.stdout.write(line + "\n")
    sys.stdout.flush()


def model_w(s, role, n, values, mask):
    w, tss = float(s.get("host_w", 40.0)), float(s.get("host_tss", 62.0))
    if "randn" in values:
        w, tss = float(s.get("heater_w", 49.0)), float(s.get("heater_tss", 66.0))
    elif "zeros" in values:
        w, tss = 28.0, 58.5
    hf = s.get("host_w_from")
    if hf and n >= int(hf["n"]) and hf.get("role", "lab") == role:
        w = float(hf["w"])
    tf = s.get("host_tss_from")
    if tf and n >= int(tf["n"]) and tf.get("role", "lab") == role:
        tss = float(tf["tss"])
    return w, tss


def role_lab(args):
    o = parse(args, LAB_VAL, LAB_FLAG)
    if o is None:
        return 2
    nodes = card_nodes()
    if not nodes:
        print("FAIL: no card node /dev/et<N>_ops", file=sys.stderr)
        record("lab", event="refused_no_node", argv=args)
        return 1
    s = scen()
    heater = o.get("--values") == "randn"
    n = bump("lab")
    nh = bump("heater") if heater else 0
    stop = o.get("--stop-file", "")
    rec = dict(event="call", argv=args, n=n, heater=heater, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop))
    if heater and s.get("heater_rc_at") is not None and nh == int(s["heater_rc_at"]):
        record("lab", forced_rc=1, launched=False, **rec)
        print("FAIL: the stand-in heater's forced exit (desk test)", file=sys.stderr)
        return 1
    if stop and os.path.exists(stop):
        record("lab", launched=False, **rec)
        print("stopping: %s exists" % stop, file=sys.stderr)
        return 0
    values = o.get("--values", "small")
    rm = o.get("--row-mask")
    mask = (int(rm, 0) & 0xFFFF) if rm is not None else 0xFFFF
    masked = rm is not None and mask != 0xFFFF
    arm = os.path.basename(values).replace("lab_", "").replace(".bin", "")
    cpo = 544.035 if masked else 546.015
    if s.get("lab_cycles_546_arm") and s["lab_cycles_546_arm"] in values and masked:
        cpo = 546.015
    terr = 1 if (s.get("tensor_err_arm") and s["tensor_err_arm"] in values) else 0
    w, tss = model_w(s, "lab", n, values, mask)
    secs = float(o.get("--seconds", 0))
    scale = float(s.get("scale", 1.0))
    every = int(s.get("runtime_every", 0))
    split = every > 0 and n % every == 0
    bad = s.get("bad_line_lab_at") is not None and n == int(s["bad_line_lab_at"])
    if s.get("bad_line_values") and s["bad_line_values"] in values and not heater:
        bad = bad or bump("badv") == int(s.get("bad_line_nth", 1))
    p = active("heater" if heater else "lab", tss=tss, w=w)
    t_open = time.time()
    lines, k = 0, -1
    try:
        while True:
            if k >= 0:
                if not secs or time.time() - t_open - 0.0 >= secs * scale or time.time() - t_open + 0.55 * scale > 8.0:
                    break
                if stop and os.path.exists(stop):
                    print("stopping: %s exists" % stop, file=sys.stderr)
                    break
            l0 = time.time()
            dur = 0.0186 if k < 0 else 0.5 * scale
            time.sleep(dur)
            l1 = time.time()
            iters = 20000 if k < 0 else 536000
            line = ('SPARSITY {"test":"fma","type":"%s","pattern":"%s","values":"%s","sparsity":0.0000,"b_sparsity":0.0000,'
                    '"b_stream":0,"row_mask":"0x%04x","nnz_a":256,"a_elems":256,"fp16_one_sided_pairs":0,"minions":1024,'
                    '"shire_mask":"0xffffffff","iters":%d,"launch":%d,"cycles_max":%d,"cycles_mean":%.1f,"cycles_per_op":%.3f,'
                    '"wall_s":%.6f,"t_start_ms":%d,"t_end_ms":%d,"ghz":0.5870,"tensor_errors":%d,"result":"unchecked","ok":%s}') % (
                o.get("--type", "fp32"), o.get("--pattern", "elem"), values, mask, iters, k, int(cpo * iters) + 300, cpo * iters, cpo,
                l1 - l0, int(l0 * 1000), int(l1 * 1000), terr, "false" if terr else "true")
            if bad and k == 1:
                line = line[:70] + "Opening card 0 (an unknown runtime text)\n" + line[70:]
            emit(line, split and lines == 1)
            lines += 1
            k += 1
    finally:
        os.unlink(p)
    record("lab", launches=lines, t0=t_open, t1=time.time(), stop_at_end=bool(stop) and os.path.exists(stop), **rec)
    if s.get("lab_rc_at") is not None and n == int(s["lab_rc_at"]):
        return 1
    return 0


def role_x14(args):
    o = parse(args, X14_VAL)
    if o is None:
        return 2
    if float(o.get("--budget", 8)) <= 0 or float(o.get("--budget", 8)) > 9:
        print("--budget must be in (0, 9] seconds", file=sys.stderr)
        return 2
    train = "--abba" in o
    if train and o["--abba"] not in ("SFFS", "FSSF"):
        print("a train needs --abba SFFS or FSSF", file=sys.stderr)
        return 2
    if train and not (1 <= int(o.get("--launches", "0"), 0) <= 16):
        print("a train needs --launches N (1..16)", file=sys.stderr)
        return 2
    nodes = card_nodes()
    if len(nodes) != 1:
        print("refused: %d card nodes (the one-card rule)" % len(nodes), file=sys.stderr)
        record("x14", event="refused_nodes", argv=args, nodes=len(nodes))
        return 1
    s = scen()
    n = bump("x14")
    stop = o.get("--stop-file", "")
    rec = dict(event="call", argv=args, n=n, train=train, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop))
    if stop and os.path.exists(stop):
        record("x14", launched=False, **rec)
        return 0
    kinds = {"F": (o.get("--label", ""), o.get("--values", ""), o.get("--row-mask")),
             "S": (o.get("--label-b", o.get("--label", "")), o.get("--values-b", o.get("--values", "")), o.get("--row-mask-b", o.get("--row-mask")))}
    zr = {"F": o.get("--zero-rows"), "S": o.get("--zero-rows-b", o.get("--zero-rows"))}
    lr = {"F": o.get("--live-rows"), "S": o.get("--live-rows-b", o.get("--live-rows"))}
    abba = o.get("--abba", "")
    nl = int(o.get("--launches", "0"), 0)
    secs = float(o.get("--seconds", 0))
    scale = float(s.get("x14_scale", s.get("scale", 1.0)))
    every = int(s.get("runtime_every", 0))
    split = every > 0 and n % every == 0
    bad = s.get("bad_line_x14_at") is not None and n == int(s["bad_line_x14_at"])
    w, tss = model_w(s, "x14", n, kinds["F"][1], 0)
    p = active("x14", tss=tss, w=w)

    def kind_of(m):
        if not train:
            return "F"
        return abba[0] if m < 1 else abba[(m - 1) % 4]

    def hexm(v):
        return "none" if v in (None, "none") else "0x%04x" % (int(v, 0) & 0xFFFF)

    def check(m):
        kk = kind_of(m)
        lab = kinds[kk][0]
        badc = 1 if (s.get("check_bad_arm") and s["check_bad_arm"] == lab) else 0
        z = hexm(zr[kk]); lv = hexm(lr[kk])
        line = ('X14CHECK {"label":"%s","kind":"%s","after_launch":%d,"zero_rows":"%s","live_rows":"%s","zero_rows_bad":%d,'
                '"live_rows_zero":%d,"ok":%s}') % (lab, kk if train else "-", m, z, lv, badc if z != "none" else -1,
                                                   0 if lv != "none" else -1, "false" if badc else "true")
        emit(line, False)

    t_open = time.time()
    lines, m, last = 0, -1, -1
    try:
        while True:
            if m >= 0:
                if train and m >= nl:
                    break
                if not train and (not secs or time.time() - t_open >= secs * scale):
                    break
                if time.time() - t_open + 0.6 * scale > 8.0:
                    break
                if stop and os.path.exists(stop):
                    break
            kk = kind_of(m)
            lab, val, rm = kinds[kk]
            masked = rm not in (None, "none") and (int(rm, 0) & 0xFFFF) != 0xFFFF
            cpo = 544.031 if masked else 546.012
            l0 = time.time()
            time.sleep(0.0186 if m < 0 else 0.5 * scale)
            l1 = time.time()
            iters = 20000 if m < 0 else 536000
            line = ('X14 {"label":"%s","values":"%s","row_mask":"%s","kind":"%s","abba":"%s","minions":1024,"shire_mask":"0xffffffff",'
                    '"iters":%d,"launch":%d,"ops":%d,"cycles_max":%d,"cycles_mean":%.1f,"cycles_per_op":%.3f,"wall_s":%.6f,'
                    '"t_start_ms":%d,"t_end_ms":%d,"ghz":0.5870,"tensor_errors":0,"ok":true}') % (
                lab, val, hexm(rm), kk if train else "-", abba, iters, m, iters * 1024, int(cpo * iters) + 300, cpo * iters, cpo,
                l1 - l0, int(l0 * 1000), int(l1 * 1000))
            if bad and m == 1:
                line = line[:60] + "Opening card 0 (an unknown runtime text)\n" + line[60:]
            emit(line, split and lines == 1)
            lines += 1
            last = m
            if m == -1:
                check(-1)
            m += 1
        if last >= 0:
            check(last)
    finally:
        os.unlink(p)
    record("x14", launches=lines, t0=t_open, t1=time.time(), stop_at_end=bool(stop) and os.path.exists(stop), **rec)
    return 0


# ---- the readers ---------------------------------------------------------------------------------------------------------------
def our_samplers():
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == os.getpid():
            continue
        try:
            words = [w.decode(errors="ignore") for w in open("/proc/%s/cmdline" % d, "rb").read().split(b"\0") if w]
        except OSError:
            continue
        if any(w.endswith("standin_e196.py") for w in words) and "sampler" in words and "sample" in words:
            out.append(int(d))
    return sorted(out)


def role_etwho(args):
    s = scen()
    me = pwd.getpwuid(os.getuid()).pw_name
    kcall = bump("etwho")
    lines = ["/dev/et0_mgmt %s %d ettelem" % (me, p) for p in our_samplers()]
    if s.get("etwho_foreign_on_call") is not None and kcall >= int(s["etwho_foreign_on_call"]):
        lines.append("/dev/et0_ops otheruser 4242 foo_host")
    fo = s.get("etwho")
    if fo == "foreign":
        lines.append("/dev/et0_ops otheruser 4242 foo_host")
    elif fo == "foreign_after_block" and int(s.get("after_block", 101)) in run_marks_blocks():
        lines.append("/dev/et0_ops otheruser 4242 foo_host")
    record("etwho", argv=args, holders=len(lines), call=kcall)
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
    if holder_query and (s.get("foreign_proc") or (s.get("foreign_proc_after_block") is not None
                                                    and int(s["foreign_proc_after_block"]) in run_marks_blocks())):
        print(" 4242   99999 foo_host")
    record("ps", argv=args)
    return r.returncode


ROLES = {"sampler": role_sampler, "lab": role_lab, "x14": role_x14, "etwho": role_etwho, "ps": role_ps}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ROLES:
        sys.exit(ROLES[sys.argv[1]](sys.argv[2:]))
    print("standin_e196.py: give a role: " + ", ".join(ROLES), file=sys.stderr)
    sys.exit(2)
