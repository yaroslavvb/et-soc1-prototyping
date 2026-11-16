#!/usr/bin/env python3
"""E194's test doubles (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): no device, no
management node, no lock, no box. E191's doubles (tools/claims-v3/e191/fake_card_e191.py, eb1ac923, unchanged beside it) with aifoundry2's
card 0 and its governor: the config read and both hosts print the device layer's identity block on stderr as the real reader and hosts do
(card 0's: /dev/et0_*, device ID 0), the sampler and the hosts hold stand-in nodes, et-who reads who holds them from /proc, and the sampler's
minion clock reads 600 MHz at rest and through a climb at each burst's start, 800 MHz from there to the burst's end (E194.md 3.1).

    fake_card_e194.py config          stands in for `ettelem config`: card 0's block on stderr and TDP 65 W, threshold 65 C, minion 600 MHz,
                                      minion_mv 519 (E194_FAKE_CONFIG=ok); card1 (a second card's form: card 1's block, 499 mV), noident
                                      (a missing node's form: no block), mv0 (a failed voltage read), tdp0, thr70, mhz800, fail (no line,
                                      rc 1), split (its line split by a runtime line, as aifoundry1's runtime split a host's)
    fake_card_e194.py etwho           stands in for `et-who`: every process holding a stand-in node (E194_FAKE_DEVDIR) or the stand-in lock
                                      (E194_FAKE_LOCK, printed as lock:etsoc-shire0.lock), read from /proc as et-who's fuser reads it;
                                      plus E194_FAKE_ETWHO=other (another login on card 0), other1 (another login on a second card),
                                      ours1 (ours on a second card's node), ops (ours on /dev/et0_ops: a stray host), mgmt (ours on
                                      /dev/et0_mgmt: a stray reader, as our live collector's read in flight), fail (rc 1, nothing on
                                      stdout), garbled (rc 0, neither a holder line nor the no-holder sentence); E194_FAKE_ETWHO_FROM=N
                                      applies the mode from the N-th call on, E194_FAKE_ETWHO_UNTIL=N before the N-th call only (counted
                                      in <E194_FAKE_SCHED>.etwho)
    fake_card_e194.py sample --seconds T --every-ms M
                                      stands in for `ettelem sample`, holding <DEVDIR>/et0_mgmt open (E194_FAKE_SAMPLER=card1 holds et1_mgmt
                                      instead; dead; stubborn; hangs:N, dies:N, hangs-all:N, noboard:N, noboard-all:N, pause:N:S as E191's;
                                      fix-e194: malformed:N prints six lines of other shapes once, at the N-th launch, among its samples):
                                      a card at aifoundry2's idle near its law at 55 C (24.3 W) plus the dynamic power of the launches the
                                      host doubles announce in $E194_FAKE_SCHED, in real time; the minion clock 600 MHz at rest, 800 MHz in a
                                      burst from its first launch's start + E194_FAKE_CLIMB_S (default 0.9 s times E194_FAKE_SCALE) to its
                                      last launch's end; E194_FAKE_BASE=alt|base puts energy_stub.py's simulated card under the same
                                      injections and the same clock; E194_FAKE_INJECT names injections (E189's form: board_w, die, latch,
                                      mhz, with from_s, to_s, during, after_pass_launches, for_s, count; "during": "busy" holds only after
                                      a burst's climb; burst_after_s: only that long after the burst's first launch's start)
    fake_card_e194.py host-ledger <the ledger host's arguments>
    fake_card_e194.py host-spp <sparse parity host's arguments>
                                      stand in for the two hosts (a card run sleeps through set-up and K launches under the host's own
                                      budget rule, announcing each launch at its start with its burst's id), each printing card 0's
                                      block on stderr when it "opens" its ops node and holding <DEVDIR>/et0_ops while it runs.
                                      E194_FAKE_HOST=ok|fail|short|nojson|crash|fail-pass (E189's), card1 (names and holds a second card),
                                      noident (names and holds nothing), hang, wedge (E191's), split (the ledger host's line split between
                                      its two parts by the runtime line "Opening device 0", as on aifoundry1), splitjunk (split by a line
                                      no lab box printed: fix-e194, read 'none', a FAILED RUN), splitdigit (split by the line "42", which
                                      a number-continuing reader would merge into the head's last number: 'none'), splitbrace (split by a
                                      lone "}" line: 'none'), replay (the ledger host's stdout replaced, after
                                      its run, by the bytes of the file E194_FAKE_HOST_FILE names, verbatim: the REAL bytes a card's host
                                      printed, for the real-path test's RH3); E194_FAKE_HOST_FROM=N, E194_FAKE_HOST_COUNT=M;
                                      E194_FAKE_SCALE scales every duration.
The launch times and watts are the frozen forecast's points (forecast-e194.json): nothing here is a measurement. The process names stay
python3, so no double is ever counted as a device process in a --dry session (the real-path test runs the reader double under the name
ettelem on purpose). SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FC = os.path.join(HERE, "forecast-e194.json")
STUB = os.path.join(REPO, "workloads", "sparseparity", "tools", "energy_stub.py")
IDLE_W = 24.3                     # aifoundry2 at rest near its law at 55 C (E194.md 5: 24.31 W): the double's number, not a forecast
F_HZ = 800e6                      # the hosts' cycles at the forecast's clock (E194.md 3.1)


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def scale():
    return float(os.environ.get("E194_FAKE_SCALE", "1"))


def climb():
    return float(os.environ.get("E194_FAKE_CLIMB_S", str(0.9 * scale())))


def forecast():
    with open(FC) as f:
        return json.load(f)["configs"]


def ident_block(card, node):
    """The device layer's identity block, as the real reader and hosts print it on stderr (the two lines the runner reads)."""
    return ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:0]: \n"
            f"PCIe target:                                               /dev/et{card}_{node}        \n"
            "PCIBUS device name:                                        0000:02:00.0        \n"
            f"Physical device ID:                                        {card}                    (0x{card})\n"
            "Form Factor:                                               PCIE                 (0x0)\n")


def hold_node(card, node):
    """Hold <E194_FAKE_DEVDIR>/et<card>_<node> open (a stand-in for the device node), or nothing without E194_FAKE_DEVDIR."""
    d = os.environ.get("E194_FAKE_DEVDIR")
    if not d:
        return None
    os.makedirs(d, exist_ok=True)
    return open(os.path.join(d, f"et{card}_{node}"), "a")


def sched_add(t0, t1, dp, tag, burst):
    p = os.environ.get("E194_FAKE_SCHED")
    if p:
        with open(p, "a") as f:
            f.write(json.dumps({"t0": t0, "t1": t1, "dp": dp, "tag": tag, "burst": burst}) + "\n")


class InPass:
    """While a pass's host double runs, the file <E194_FAKE_SCHED>.inpass exists (the sampler's "during": "pass" reads it)."""

    def __init__(self, on):
        self.p = (os.environ.get("E194_FAKE_SCHED", "") + ".inpass") if on and os.environ.get("E194_FAKE_SCHED") else ""

    def __enter__(self):
        if self.p:
            open(self.p, "w").close()

    def __exit__(self, *a):
        if self.p and os.path.exists(self.p):
            os.remove(self.p)


def read_sched():
    p = os.environ.get("E194_FAKE_SCHED")
    out = []
    if p and os.path.exists(p):
        with open(p) as f:
            for ln in f:
                if ln.startswith("{"):
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    return out


def bursts(sch):
    """{burst id: (first launch's start, last launch's end so far)} from the schedule."""
    out = {}
    for s in sch:
        b = s.get("burst")
        if b is None:
            continue
        a, z = out.get(b, (s["t0"], s["t1"]))
        out[b] = (min(a, s["t0"]), max(z, s["t1"]))
    return out


END_GRACE_S = 0.05                # the double's governor keeps the clock this long past a burst's planned end (the host's own end mark
                                  # comes a millisecond or so after the planned end; a real governor does not drop at once either)


def clock_at(tick, sch):
    """(minion MHz, busy after the climb): 800 MHz in a burst from its start + climb() to its end (and END_GRACE_S past it), else 600 MHz
    (the idle point)."""
    for a, z in bursts(sch).values():
        if a <= tick <= z + END_GRACE_S:
            return (800, True) if tick >= a + climb() else (600, False)
    return 600, False


def config():
    mode = os.environ.get("E194_FAKE_CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node (double)", file=sys.stderr)
        return 1
    card, mv = "0", 519
    if mode == "card1":
        card, mv = "1", 499
    elif mode == "mv0":
        mv = 0
    if mode != "noident":
        sys.stderr.write(ident_block(card, "mgmt"))
    j = {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": mv,
         "fake": True}
    if mode == "tdp0":
        j["tdp_w"] = 0
    elif mode == "thr70":
        j["temp_threshold_c"] = 70
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    line = json.dumps(j, separators=(",", ":"))
    if mode == "split":
        k = line.index(',"minion_mhz"')
        sys.stdout.write(line[:k] + "Opening device 0\n" + line[k:] + "\n")
        return 0
    print(line)
    return 0


def holders():
    """et-who's lines for the stand-in nodes and lock: every process (of any user) whose open files include them, read from /proc/*/fd as
    et-who's fuser reads it; a node printed under its real name (/dev/etN_...), the lock as lock:etsoc-shire0.lock."""
    import pwd
    d = os.environ.get("E194_FAKE_DEVDIR")
    lk = os.environ.get("E194_FAKE_LOCK")
    d = os.path.realpath(d) if d else None
    lk = os.path.realpath(lk) if lk else None
    out = []
    for pid in sorted((int(x) for x in os.listdir("/proc") if x.isdigit())):
        try:
            fds = os.listdir(f"/proc/{pid}/fd")
            uid = os.stat(f"/proc/{pid}").st_uid
        except OSError:
            continue
        names = set()
        for fd in fds:
            try:
                t = os.readlink(f"/proc/{pid}/fd/{fd}")
            except OSError:
                continue
            if d and t.startswith(d + "/") and t[len(d) + 1:].startswith("et"):
                names.add("/dev/" + t[len(d) + 1:])
            elif lk and t == lk:
                names.add("lock:etsoc-shire0.lock")
        if names:
            try:
                user = pwd.getpwuid(uid).pw_name
            except KeyError:
                user = str(uid)
            try:
                comm = open(f"/proc/{pid}/comm").read().strip()
            except OSError:
                comm = "?"
            for n in sorted(names):
                out.append(f"{n:<14s} {user:<14s} {pid:>7d}       00:01 {comm}")
    return out


def etwho():
    import pwd
    m = os.environ.get("E194_FAKE_ETWHO", "free")
    me = pwd.getpwuid(os.getuid()).pw_name
    frm = int(os.environ.get("E194_FAKE_ETWHO_FROM", "1"))
    until = int(os.environ.get("E194_FAKE_ETWHO_UNTIL", "0"))
    if frm > 1 or until:
        cp = os.environ.get("E194_FAKE_SCHED", "") + ".etwho"
        k = 0
        if os.environ.get("E194_FAKE_SCHED"):
            try:
                k = int(open(cp).read().strip() or 0)
            except (OSError, ValueError):
                k = 0
            k += 1
            with open(cp, "w") as f:
                f.write(str(k))
        if k < frm or (until and k >= until):
            m = "free"
    if m == "fail":
        print("et-who: its helper refused (double): nothing to read", file=sys.stderr)
        return 1
    if m == "garbled":
        print("et-holders: fuser: cannot stat (double)")
        return 0
    lines = holders()
    if m == "other":
        lines.append("/dev/et0_ops someoneelse 4242 00:01 other_host")
    elif m == "other1":
        lines.append("/dev/et1_ops someoneelse 4444 00:01 other_host")
    elif m == "ours1":
        lines.append(f"/dev/et1_mgmt {me} 4343 00:01 ettelem")
    elif m == "ops":
        lines.append(f"/dev/et0_ops {me} 4545 00:01 ledger_host")
    elif m == "mgmt":
        lines.append(f"/dev/et0_mgmt {me} 4646 00:01 ettelem")
    print("\n".join(lines) if lines else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Inject:
    """The desk cases' injections (E194_FAKE_INJECT, E189's form): each moves the sampled point the stop lines and the clock rule read."""

    def __init__(self):
        self.inj = []
        p = os.environ.get("E194_FAKE_INJECT")
        if p and os.path.exists(p):
            with open(p) as f:
                self.inj = json.load(f)
        self.first, self.used = {}, {}

    def apply(self, line, tick, el, sch):
        if not self.inj:
            return line
        live = [s for s in sch if s["t0"] <= tick < s["t1"]]
        npass = sum(1 for s in sch if s.get("tag") == "pass")
        inpass = os.path.exists(os.environ.get("E194_FAKE_SCHED", "") + ".inpass")
        busy = clock_at(tick, sch)[1]
        bstart = next((a for a, z in bursts(sch).values() if a <= tick <= z), None)
        for i, x in enumerate(self.inj):
            cond = x.get("from_s", 0) <= el < x.get("to_s", 1e9) and npass >= x.get("after_pass_launches", 0)
            if cond and "burst_after_s" in x:          # only from this many seconds after its burst's first launch's start
                cond = bstart is not None and tick - bstart >= x["burst_after_s"]
            if cond and x.get("during") == "pass":
                cond = inpass
            elif cond and x.get("during") == "busy":
                cond = inpass and busy
            elif cond and x.get("during"):
                cond = any(s.get("tag") == x["during"] for s in live)
            if cond and i not in self.first:
                self.first[i] = tick
            if cond and "for_s" in x and tick - self.first[i] > x["for_s"]:
                cond = False
            if cond and self.used.get(i, 0) >= x.get("count", 1 << 30):
                cond = False
            if cond:
                self.used[i] = self.used.get(i, 0) + 1
                if "board_w" in x:
                    line["board_w"] = x["board_w"]
                if "die" in x:
                    ms = (line.setdefault("temp_c", {}).get("minshire") or [55, 54, 70])
                    line["temp_c"]["minshire"] = [x["die"], x["die"] - 1, ms[2] if len(ms) > 2 else 70]
                if "latch" in x:
                    ms = (line.setdefault("temp_c", {}).get("minshire") or [55, 54, 70])
                    line["temp_c"]["minshire"] = [ms[0], ms[1] if len(ms) > 1 else ms[0], x["latch"]]
                if "mhz" in x:
                    line.setdefault("mhz", {})["minion"] = x["mhz"]
        return line


def sample_on_stub(card, seconds, every_ms, inj):
    """E194_FAKE_BASE=alt|base: energy_stub.py's simulated card (unchanged), its minion clock set by the bursts (clock_at), under the
    injections."""
    child = subprocess.Popen([sys.executable, "-B", STUB, "sample", "--seconds", str(int(seconds)), "--every-ms", str(every_ms),
                              "--sched", os.environ.get("E194_FAKE_SCHED", ""), "--card", card], stdout=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, text=True)

    def term(*_):
        try:
            child.send_signal(signal.SIGTERM)
        except OSError:
            pass

    signal.signal(signal.SIGTERM, term)
    t0 = time.time()
    for raw in child.stdout:
        if not raw.startswith("{"):
            continue
        try:
            line = json.loads(raw)
        except ValueError:
            continue
        tick = line.get("t_ms", 0) / 1000.0
        sch = read_sched()
        line.setdefault("mhz", {})["minion"] = clock_at(tick, sch)[0]
        line = inj.apply(line, tick, time.time() - t0, sch)
        print(json.dumps(line, separators=(",", ":")), flush=True)
    return child.wait()


def sample(argv):
    mode = os.environ.get("E194_FAKE_SAMPLER", "")
    if mode == "dead":
        print("fake sampler: cannot open the management node", file=sys.stderr)
        return 1
    node = hold_node("1" if mode == "card1" else "0", "mgmt")     # held for the sampler's life, as the reader holds its node
    seconds = float(arg(argv, "--seconds", 10))
    every_ms = int(arg(argv, "--every-ms", 100))
    every = every_ms / 1000.0
    inj = Inject()
    base = os.environ.get("E194_FAKE_BASE", "")
    if base in ("alt", "base"):
        rc = sample_on_stub(base, seconds, every_ms, inj)
        if node:
            node.close()
        return rc
    terms = {"n": 0}
    signal.signal(signal.SIGTERM, lambda *_: terms.update(n=terms["n"] + 1))
    need = 2 if mode == "stubborn" else 1
    limit, kind, pause_s = None, None, 0.0
    if mode.split(":", 1)[0] in ("hangs", "dies", "hangs-all", "noboard", "noboard-all", "pause", "malformed") and ":" in mode:
        parts = mode.split(":")
        kind, limit = parts[0], int(parts[1])
        if kind == "pause":
            pause_s = float(parts[2]) if len(parts) > 2 else 3.0
    silent = noboard = False
    pause_until = None
    t0 = time.time()
    while terms["n"] < need and time.time() - t0 < seconds:
        tick = time.time()
        sch = read_sched()
        if limit is not None and not silent and len(sch) >= limit:
            mk = (os.environ.get("E194_FAKE_SCHED") or "/nonexistent") + f".sampler-{kind}"
            if kind.endswith("-all") or not os.path.exists(mk):
                try:
                    open(mk, "a").close()
                except OSError:
                    pass
                if kind == "dies":
                    print(f"the double's sampler dies at {len(sch)} launches (desk case)", file=sys.stderr)
                    if node:
                        node.close()
                    return 1
                if kind in ("noboard", "noboard-all"):
                    noboard = True
                elif kind == "malformed":         # fix-e194 (verify-e194's nit 7): lines of other shapes, once, among the samples
                    for odd in ({"temp_c": [50, 46, 70]}, {"temp_c": {"minshire": 50}}, {"temp_c": "hot"}, {"mhz": [800]},
                                {"board_w": "31.5"}, {"t_ms": "now"}):
                        bad = {"t_ms": int(tick * 1000), "board_w": 30.0, "temp_c": {"minshire": [50, 46, 70]},
                               "mhz": {"minion": 600, "noc": 1000}, "fake": True}
                        bad.update(odd)
                        print(json.dumps(bad, separators=(",", ":")), flush=True)
                elif kind == "pause":
                    pause_until = time.time() + pause_s
                else:
                    silent = True
            limit = None
        if silent:
            time.sleep(every)
            continue
        if pause_until is not None:
            if time.time() < pause_until:
                time.sleep(every)
                continue
            pause_until = None
        live = [s for s in sch if s["t0"] <= tick < s["t1"]]
        dp = sum(s["dp"] for s in live)
        bw, die = IDLE_W + dp, 50 + min(3, int(dp / 8))
        line = {"t_ms": int(tick * 1000), "took_ms": 22, "since_reset_ms": -1, "board_w": round(bw, 2),
                "sp": {"board_avg_w": round(bw, 2), "minion_w": [4.4 + 0.6 * dp] * 3, "sram_w": [2.8 + 0.1 * dp] * 3,
                       "noc_w": [2.2] * 3},
                "temp_c": {"minshire": [die, 46, 70]}, "mhz": {"minion": clock_at(tick, sch)[0], "noc": 1000}, "fake": True}
        line = inj.apply(line, tick, tick - t0, sch)
        if noboard:
            line.pop("board_w", None)
            line.get("sp", {}).pop("board_avg_w", None)
        print(json.dumps(line, separators=(",", ":")), flush=True)
        time.sleep(max(0.0, tick + every - time.time()))
    if node:
        node.close()
    return 0


SELFTEST = """SELFTEST abc x1 ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad OK
SELFTEST  x1 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 OK
SELFTEST abcdbcde... x1 248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1 OK
SELFTEST a x1000000 cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0 OK
SELFTEST PASS"""


SPLITS = {"split": "Opening device 0\n", "splitjunk": "a runtime line no lab box printed\n", "splitdigit": "42\n", "splitbrace": "}\n"}


def parse_size(s):
    """main.cpp's parseSize, as e194_common.parse_size reads it."""
    import re
    m = re.match(r"^\s*([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)([A-Za-z]?)", str(s))
    if not m:
        return None
    return int(float(m.group(1)) * {"K": 1024, "M": 1024 ** 2, "G": 1024.0 ** 3}.get(m.group(2).upper(), 1))


def head_fields(argv):
    """fix-e194: the head fields the real ledger host prints for its command (copy: bytes, passes, data, width; sha256: block, repeat;
    sort: keys, reps, order), the last of them where its head ends."""
    prog = arg(argv, "--prog")
    if prog == "copy":
        return {"bytes": parse_size(arg(argv, "--bytes", "0")), "passes": int(arg(argv, "--passes", 1)), "data": arg(argv, "--data"),
                "width": int(arg(argv, "--width", 32))}
    if prog == "sha256":
        return {"block": parse_size(arg(argv, "--block", "0")), "repeat": int(arg(argv, "--repeat", 1))}
    if prog == "sort":
        return {"keys": int(arg(argv, "--keys", 0)), "reps": int(arg(argv, "--reps", 1)), "order": arg(argv, "--order")}
    return {}


def head_obj(argv):
    h = {"ledger": 1, "prog": arg(argv, "--prog"), "device": "card", "participants": 2048}
    h.update(head_fields(argv))
    return h


def ledger_key(argv):
    prog = arg(argv, "--prog")
    if prog == "copy":
        return "copy-" + ("zeros" if arg(argv, "--data") == "zeros" else "random")
    if prog == "sort":
        return "sort-" + arg(argv, "--order", "shuffled")
    return "sha256"


def host_mode():
    """The host double's mode for this process (E194_FAKE_HOST, from the E194_FAKE_HOST_FROM-th device-opening process on, for at most
    E194_FAKE_HOST_COUNT of them); 'ok' otherwise."""
    mode = os.environ.get("E194_FAKE_HOST", "ok")
    sch = os.environ.get("E194_FAKE_SCHED", "")
    cnt = sch + ".hosts" if sch else ""
    n = 0
    if cnt:
        try:
            n = int(open(cnt).read().strip() or 0)
        except (OSError, ValueError):
            n = 0
        n += 1
        with open(cnt, "w") as f:
            f.write(str(n))
    frm = int(os.environ.get("E194_FAKE_HOST_FROM", "1"))
    lim = os.environ.get("E194_FAKE_HOST_COUNT")
    if n and n < frm:
        return "ok"
    if lim and n and n >= frm + int(lim):
        return "ok"
    return mode


def open_card(mode):
    """The host "opens" its ops node: the identity block on stderr and the stand-in node held (card 0; a second card or nothing by mode)."""
    if mode == "noident":
        return None
    card = "1" if mode == "card1" else "0"
    sys.stderr.write(ident_block(card, "ops"))
    sys.stderr.flush()
    return hold_node(card, "ops")


def wedge(ignore_term=True):
    if ignore_term:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(float(os.environ.get("E194_FAKE_WEDGE_S", "35")))
    return 124


def burst(K, launch_s, dp, setup_s, budget, guard_s, mode, tag):
    """The host's own budget rule (main.cpp): a launch starts only while budget - elapsed >= guard + 0.5. Each launch is announced to
    the sampler AT ITS START, with its burst's id (this process)."""
    start = time.time()
    time.sleep(setup_s)
    walls, spans = [], []
    n_max = K - 2 if mode == "short" else K
    for _ in range(n_max):
        if budget - (time.time() - start) < guard_s * scale() + 0.5 * scale():
            break
        a = time.time()
        sched_add(a, a + launch_s, dp, tag, os.getpid())
        time.sleep(max(0.0, a + launch_s - time.time()))
        b = time.time()
        walls.append(round(b - a, 4))
        spans += [int(a * 1000), int(b * 1000)]
        time.sleep(0.004 * scale())
    return walls, spans


def host_ledger(argv):
    if "--selftest" in argv:
        print(SELFTEST)
        return 0
    mode = host_mode()
    if mode in SPLITS:
        sys.stdout.write(json.dumps(head_obj(argv), separators=(",", ":"))[:-1])     # the head, before the card opens (main.cpp 478-492)
        sys.stdout.write(SPLITS[mode])
        sys.stdout.flush()
    node = open_card(mode)
    if mode in ("wedge", "hang"):
        return wedge(mode == "wedge")
    if mode == "crash":
        print("fake ledger host: crashed before its line", file=sys.stderr)
        return 134
    key = ledger_key(argv)
    f = forecast()[key]
    K = int(arg(argv, "--launches", 1))
    small = K == 1
    launch_s = (0.05 if small else f["seconds"]["point"]) * scale()
    guard = {"copy-zeros": 1.5032, "copy-random": 1.5032, "sha256": 0.76803, "sort-sorted": 1.142784, "sort-shuffled": 1.142784}[key]
    bmode = mode if (not small and mode in ("short",)) else "ok"
    with InPass(not small):
        walls, spans = burst(K, launch_s, f["w_over_idle"], 0.3 * scale(), 9.5 * scale(), 0.0 if small else guard, bmode,
                             "smoke" if small else "pass")
    n = len(walls)
    P = 2048
    cyc = int(round(launch_s / scale() * F_HZ))
    bad = 1 if mode == "fail" or (mode == "fail-pass" and not small) else 0
    j = {"ledger": 1, "prog": arg(argv, "--prog"), "device": "card", "participants": P}
    j.update(head_fields(argv))             # fix-e194: the head fields the real host prints before it opens the card (main.cpp 478-492)
    j.update({"launches": n, "wall_s": walls,
         "launch_epoch_ms": spans, "records_ok": P, "records_bad": 0, "units": 7, "units_expected": 7,
         "hart0_cycles": {"max": cyc, "min": cyc - 1000, "mean": cyc - 500.0, "n": 1024}, "checked": P, "mismatches": bad,
         "expect_checked": P if "--expect" in argv else 0, "expect_mismatches": 0,
         "first_mismatch": "participant 7" if bad else "", "status": "PASS" if (n == K and not bad) else "FAIL", "fake": True})
    if mode == "replay":                # the REAL bytes a card's host printed (E194_FAKE_HOST_FILE), verbatim, in place of its line
        with open(os.environ["E194_FAKE_HOST_FILE"], "rb") as rf:
            sys.stdout.flush()
            sys.stdout.buffer.write(rf.read())
        sys.stdout.flush()
        if node:
            node.close()
        return 0
    if mode == "nojson":
        print('{"ledger":1,"prog":"cut')
        return 124
    if mode in SPLITS:
        full = json.dumps(j, separators=(",", ":"))
        head = json.dumps(head_obj(argv), separators=(",", ":"))[:-1]
        print(full[len(head):] if full.startswith(head) else full)          # the rest, after its launches (main.cpp 621)
    else:
        print(json.dumps(j, separators=(",", ":")))
    if node:
        node.close()
    return 0 if j["status"] == "PASS" else 1


def host_spp(argv):
    mode = host_mode()
    node = open_card(mode)
    if mode in ("wedge", "hang"):
        return wedge(mode == "wedge")
    f = forecast()["sparse-parity"]
    R = int(arg(argv, "--reps", 1))
    launch_s = f["seconds"]["point"] * scale()
    t0 = time.time()
    bmode = mode if (R > 1 and mode in ("short",)) else "ok"
    with InPass(R > 1):
        walls, spans = burst(R, launch_s, f["w_over_idle"], 0.6 * scale(), 9.0 * scale(), 0.784738, bmode,
                             "pass" if R > 1 else "smoke")
    n = len(walls)
    rec = arg(argv, "--records-out")
    if rec:
        with open(rec, "w") as fo:
            fo.write("fake records\n")
    cyc = int(round(launch_s / scale() * F_HZ))
    j = {"workload": "sparseparity", "device": "silicon", "n": 544, "k": 4, "eta": 0.39, "m": 1792, "seed": 3,
         "instance": {"n": 544, "k": 4, "eta": 0.39, "m": 1792, "seed": 3, "hash": "fake"}, "plan": {"slice": "0/1", "model_s": 0.514741},
         "reps_requested": R, "reps_done": n, "reps_consistent": "ok", "launch_s": walls,
         "launch_epoch_ms": [spans[0], spans[-1]] if spans else [0, 0], "kernel": {"cycles_max": cyc},
         "result": {"solved": mode != "fail", "unique": True, "answer": [1, 2, 3, 4]},
         "host_cpu_s": {"burst": [round(0.9 * (time.time() - t0), 3), 0.05]},
         "status": "PASS" if (n == R and mode != "fail") else "FAIL", "fake": True}
    if n < R:
        j["problems"] = [f"reps: {n} of {R} done"]
        j["stop_reason"] = "budget"
    print(json.dumps(j, separators=(",", ":")))
    if node:
        node.close()
    return 0 if j["status"] == "PASS" else 1


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    w, rest = argv[0], argv[1:]
    if w == "config":
        return config()
    if w == "etwho":
        return etwho()
    if w == "sample":
        return sample(rest)
    if w == "host-ledger":
        return host_ledger(rest)
    if w == "host-spp":
        return host_spp(rest)
    print(f"fake_card_e194: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
