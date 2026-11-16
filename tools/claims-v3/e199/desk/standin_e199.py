#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum): THE STAND-INS for the real-path desk test
(desk/desktest_realpath_e199.sh) and the runbook desk test's stand-in aifoundry1. E192's stand-ins (tools/claims-v3/e192/desk/standin_e192.py,
a6fe5c20, unchanged beside it) made aifoundry1 card 1's. NOTHING HERE OPENS A CARD OR SENDS A COMMAND; nothing here is measured or forecast.
The desk test's private /dev holds aifoundry1's four node names as stand-ins (each a bind of /dev/null: a character node that is no card);
every role answers in the tool's own form, from a small card model shared through a state directory (E199_STANDIN_DIR):
  sampler  the reader `build/ettelem/ettelem sample --seconds T --every-ms 100`: it opens and HOLDS /dev/et<ET_DEVICES>_mgmt (so /proc shows
           the node, as et-who's fuser and the gate's watch read it), then 10 Hz JSON lines in ettelem's keys; and `config` (through
           E199's guard): aifoundry1's runtime line "Opening device <n>" on stdout, then the JSON line (card 1: TDP 65 W, 65 C, 600 MHz,
           minion_mv 499), and the device layer's identity block for card <n> on stderr (E191's committed read's form);
  pvt      E89's `pvt_sample.py --seconds T --every-ms 100` and `--probe`: as the sampler, with the "pvt" codes; holds the same node;
  heater   E78's heater: its option parser (an unknown option exits 2 before anything); the real host's selection rule (two card nodes and
           ET_DEVICES unset: refused); "Opening device <n>" on stdout and the identity block on stderr; it holds /dev/et<n>_ops while active;
  host     the intbits host `--arm A --seconds S --window W --stop-file F` (and `--list --json`): the real host's node count and selection
           first, then "Opening device <n>" on stdout (aifoundry1's runtime: the host prints nothing before it opens the card), the identity
           block on stderr, the node held, 0.4 s launches each printing one INTBITS line in the host's form;
  etwho    `et-who [--check]`: like et-holders, every open /dev/et*_ops|mgmt of any process (its /proc fds: "<node> <login> <pid> <comm>"),
           plus the holders the scenario adds; "No process holds an ET-SoC-1 device node or card lock." when none (exit 0);
  ps       /usr/bin/ps, plus another user's device process when the scenario names one;
  sha256sum  E192's (one case only).
E192's knobs are kept; E199's added: sampler_no_hold (the sampler holds no node), config_card, config_mv, config_tdp, config_split, config_fail_on_call (no config: exit 1);
heater_card, host_card_from {n, card} (the n-th host process on names that card on its stderr), host_hold_from {n, node} (it also holds
that node), runtime_inside {n, offset} (that host process prints the runtime line INSIDE its first INTBITS line at that byte offset),
etwho_lines (extra holder lines, "{me}" for our login), etwho_lines_on_call {k: [...]} (from the k-th et-who call on), etwho_rc.
    python3 -I -B standin_e199.py <role> [args...]
SPDX-License-Identifier: Apache-2.0
"""
import fcntl
import json
import math
import os
import pwd
import re
import random
import signal
import subprocess
import sys
import time

SD = os.environ.get("E199_STANDIN_DIR", "")
LOCK = "/run/lock/etsoc-shire1.lock"
ME = pwd.getpwuid(os.getuid()).pw_name
G_TS, H_TS, CAL5 = 57400, 249400, 4096       # the reducer's per-sensor conversion (reduce_intbits.py line 64), inverted below
_stop = False


BLOCK = ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \n"
         "PCIe target:                                               /dev/et{c}_{k}       \n"
         "PCIBUS device name:                                        0000:02:00.0        \n"
         "Physical device ID:                                        {c}                    (0x{c})\n"
         "TDP (W):                                                   65                  \n")


def card_nodes():
    v = []
    try:
        for n in os.listdir("/dev"):
            if n.startswith("et") and n.endswith("_ops") and n[2:-4].isdigit():
                v.append(int(n[2:-4]))
    except OSError:
        pass
    return sorted(v)


def selected_card():
    """The card the device layer opens: ET_DEVICES when set, else the only card; None when it would refuse (the real rule)."""
    nodes = card_nodes()
    sel = os.environ.get("ET_DEVICES", "")
    if sel:
        return int(sel) if sel.isdigit() and int(sel) in nodes else None
    return nodes[0] if len(nodes) == 1 else None


def hold(node):
    """Open a stand-in node and keep it open (the fd stays until the process ends), as a real opener holds it."""
    try:
        return os.open(node, os.O_RDONLY)
    except OSError:
        return None


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
    card = selected_card()
    held = hold("/dev/et%s_mgmt" % card) if (card is not None and not s.get("sampler_no_hold")) else None
    record(role, event="start", argv=list(argv if argv is not None else sys.argv[1:]), lock_held=lock_held(), card=card,
           held=held is not None, et_devices=os.environ.get("ET_DEVICES"))
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
        s = scen()
        k = bump("config")
        card = selected_card()
        record("sampler", event="config", argv=args, lock_held=lock_held(), card=card, call=k, et_devices=os.environ.get("ET_DEVICES"))
        if s.get("config_fail_on_call") is not None and k in ([int(x) for x in s["config_fail_on_call"]] if isinstance(s["config_fail_on_call"], list) else [int(s["config_fail_on_call"])]):
            print("ettelem: cannot open the management node (busy) (desk-test stand-in)", file=sys.stderr)
            return 1
        if card is None:
            print("ettelem: the device layer refused: more than one card and no selection (desk-test stand-in)", file=sys.stderr)
            return 1
        bc = int(s.get("config_card", card))
        j = json.dumps({"tdp_w": int(s.get("config_tdp", 65)), "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power",
                        "minion_mhz": 600, "minion_mv": int(s.get("config_mv", 499 if bc == 1 else 519))})
        rt = "Opening device %d\n" % card
        if s.get("config_split"):
            i = j.index('"minion_mhz"')
            sys.stdout.write(j[:i] + rt + j[i:] + "\n")
        else:
            sys.stdout.write(rt + j + "\n")
        sys.stderr.write(BLOCK.format(c=bc, k="mgmt"))
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
    rec = dict(event="call", argv=args, n=n, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop),
               et_devices=os.environ.get("ET_DEVICES"))
    card = selected_card()
    if card is None:
        print("FAIL: more than one card and no selection (the device layer would open every card) (desk-test stand-in)", file=sys.stderr)
        record("heater", launched=False, refused_selection=True, **rec)
        return 1
    if stop and os.path.exists(stop):
        record("heater", launched=False, **rec)
        return 0
    sys.stdout.write("Opening device %d\n" % card)
    sys.stdout.flush()
    sys.stderr.write(BLOCK.format(c=int(s.get("heater_card", card)), k="ops"))
    sys.stderr.flush()
    hfd = hold("/dev/et%d_ops" % card)
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
    table = os.environ.get("E199_STANDIN_TABLE") or os.path.join(SD, "arm-table.jsonl")
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
    sel = os.environ.get("ET_DEVICES", "")
    if sel and (not sel.isdigit() or int(sel) not in nodes):
        print("FAIL: ET_DEVICES=%s: no such card node" % sel, file=sys.stderr)
        record("host", event="refused_selection", argv=args)
        return 1
    if len(nodes) > 1 and not sel:
        print("FAIL: %d cards on this host and ET_DEVICES unset: refusing to open every card" % len(nodes), file=sys.stderr)
        record("host", event="refused_selection", argv=args)
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
    rec = dict(event="call", argv=args, n=n, arm=arm, lock_held=lock_held(), stop_present=bool(stop) and os.path.exists(stop),
               et_devices=os.environ.get("ET_DEVICES"))
    card = selected_card()
    bcard = card
    if s.get("host_card_from") and n >= int(s["host_card_from"]["n"]):
        bcard = int(s["host_card_from"]["card"])
    rin = s.get("runtime_inside") if (s.get("runtime_inside") and n == int(s["runtime_inside"]["n"])) else None
    if not rin and not s.get("no_runtime"):
        sys.stdout.write("Opening device %d\n" % card)
        sys.stdout.flush()
    sys.stderr.write(BLOCK.format(c=bcard, k="ops"))
    sys.stderr.flush()
    hfd = hold("/dev/et%d_ops" % card)
    if s.get("host_hold_from") and n >= int(s["host_hold_from"]["n"]):
        hold(s["host_hold_from"]["node"])
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
        if rin and k == 0:
            off = int(rin["offset"])
            line = line[:off] + "Opening device %d\n" % card + line[off:]
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
def node_holders():
    """Every process with a /dev/et*_ops|mgmt open (its /proc fds), as et-holders' fuser lists it: [(node, login, pid, comm)]."""
    out = []
    for d in os.listdir("/proc"):
        if not d.isdigit() or int(d) == os.getpid():
            continue
        try:
            fds = os.listdir("/proc/%s/fd" % d)
        except OSError:
            continue
        seen = set()
        for fd in fds:
            try:
                t = os.readlink("/proc/%s/fd/%s" % (d, fd))
            except OSError:
                continue
            if re.match(r"^/dev/et\d+_(ops|mgmt)$", t) and t not in seen:
                seen.add(t)
                try:
                    c = open("/proc/%s/comm" % d).read().strip()
                    u = pwd.getpwuid(os.stat("/proc/%s" % d).st_uid).pw_name
                except (OSError, KeyError):
                    continue
                out.append((t, u, int(d), c))
    return sorted(out)


def role_etwho(args):
    s = scen()
    kcall = bump("etwho")
    if s.get("etwho_fail_on_call") is not None and kcall == int(s["etwho_fail_on_call"]):
        record("etwho", argv=args, holders=None, call=kcall, failed=True)
        print("et-who: sudo: a password is required (desk-test stand-in)", file=sys.stderr)
        return 2
    if s.get("etwho_takes_lock_on_call") is not None and kcall == int(s["etwho_takes_lock_on_call"]):
        held = take_lock_by_holder(float(s.get("lock_hold_s", 20)))
        record("etwho", event="lock_taken_by_holder", call=kcall, held=held)
    lines = ["%s %s %d %s" % h for h in node_holders()]
    for ln in s.get("etwho_lines", []):
        lines.append(ln.replace("{me}", ME))
    for k, extra in sorted((s.get("etwho_lines_on_call") or {}).items(), key=lambda x: int(x[0])):
        if kcall >= int(k):
            lines += [ln.replace("{me}", ME) for ln in extra]
    if s.get("etwho_foreign_on_call") is not None and kcall >= int(s["etwho_foreign_on_call"]):
        lines.append("/dev/et1_ops otheruser 4242 foo_host")
    fo = s.get("etwho")
    if fo == "foreign":
        lines.append("/dev/et1_ops otheruser 4242 foo_host")
    elif fo == "foreign_after_pass0":
        rd = open(os.path.join(SD, "rundir")).read().strip() if os.path.exists(os.path.join(SD, "rundir")) else ""
        try:
            for ln in open(os.path.join(rd, "marks.jsonl")):
                m = json.loads(ln)
                if m.get("kind") == "idle" and m.get("label") == "after" and m.get("pass") == 0:
                    lines.append("/dev/et1_ops otheruser 4242 foo_host")
                    break
        except (OSError, ValueError):
            pass
    record("etwho", argv=args, holders=len(lines), call=kcall, lines=lines)
    if "--check" in args:
        if not lines:
            return 0
        for ln in lines:
            print(ln)
        return 1
    if not lines:
        print("No process holds an ET-SoC-1 device node or card lock.")
        return int(s.get("etwho_rc", 0))
    print("NODE          USER        PID    COMMAND")
    for ln in lines:
        print(ln)
    return int(s.get("etwho_rc", 0))


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

def own_name():
    """A stand-in run through its shim (`exec -a <the tool's path>`) takes the tool's name as its comm, as the real binary's process has
    it (intbits_host, sparsity_host, ettelem): ps, et-who's lines and the gate's watch then see the name the box shows."""
    try:
        a0 = open("/proc/self/cmdline", "rb").read().split(b"\0")[0].decode(errors="ignore")
        nm = os.path.basename(a0)[:15]
        if nm and not nm.startswith("python"):
            with open("/proc/self/comm", "w") as f:
                f.write(nm)
    except OSError:
        pass


if __name__ == "__main__":
    own_name()
    if len(sys.argv) > 1 and sys.argv[1] in ROLES:
        role, rest = sys.argv[1], sys.argv[2:]
    else:
        role, rest = os.environ.get("E199_STANDIN_ROLE", ""), sys.argv[1:]
    if role not in ROLES:
        print("standin_e199.py: give a role: " + ", ".join(ROLES), file=sys.stderr)
        sys.exit(2)
    sys.exit(ROLES[role](rest))
