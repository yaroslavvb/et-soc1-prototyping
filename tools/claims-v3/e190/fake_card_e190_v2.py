#!/usr/bin/env python3
"""E190's test doubles v2 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): fake_card_e190.py (the kit,
unchanged beside it) with the card's identity the v2 runner reads, and nothing it does not need. No device, no lock, no box. The additions:
  - config prints the device layer's identity block on stderr as the real readers do (arm A: PCIe target /dev/et0_mgmt, physical device
    ID 0, minion_mv 519; arm B: /dev/et1_mgmt, ID 1, 499 mV); E190_FAKE_CONFIG=card0 (card 0's block and 519 mV: aifoundry1 had ignored
    ET_DEVICES), mv519 (card 1's block, 519 mV), noident (no block);
  - with E190_FAKE_DEVDIR set (a stand-in directory for /dev), sample holds <DEVDIR>/et<card>_mgmt open while it runs and host holds
    <DEVDIR>/et<card>_ops, as the real reader and host hold their nodes; sample E190_FAKE_SAMPLER=card0 holds et0_mgmt instead,
    dies:<N> exits after N samples, hangs:<N> stops printing after N samples and stays alive; host E190_FAKE_HOST=card0 names and holds
    card 0 (stderr block and node), noident names and holds nothing, norise announces no watts (the board does not rise);
  - etwho reads who holds the stand-in nodes and the stand-in lock (E190_FAKE_LOCK) from /proc, as et-who's fuser does, and prints them in
    et-who's form under the real names (/dev/etN_..., lock:etsoc-shireN.lock), plus v1's E190_FAKE_ETWHO lines.
The v1 text that follows still describes everything else.

    fake_card_e190.py config        stands in for `ettelem config` (E190_FAKE_CONFIG=ok|tdp70|thr70|mhz800|fail; E190_FAKE_ARM=A|B)
    fake_card_e190.py etwho         stands in for `et-who` (E190_FAKE_ETWHO=free|other|ours0|other0: another login on the arm's card; ours
                                    on card 0 (arm B: another session of ours on aifoundry1); another login on card 0 (arm B: not a block))
    fake_card_e190.py sample --seconds T --every-ms M
                                    stands in for `ettelem sample`: a toy card whose board power is its idle (rising 0.4 W a C of die) plus
                                    the over-idle watts of the launches the host double announces in $E190_FAKE_SCHED, in real time, and
                                    whose die follows its power with a first-order lag (E190_FAKE_TAU_S, default 6 s; its idle rises
                                    E190_FAKE_LEAK W a C, default 0.4). E190_FAKE_INJECT
                                    names a JSON file of injections the stop cases use: each {"board_w" | "die" | "high": value} with its
                                    conditions, all optional: "after_launches": N (once N launches have started), "from_s" (seconds from
                                    the sampler's start), "count" (at most that many samples). E190_FAKE_SAMPLER=dead prints nothing and
                                    exits 1; =stubborn ignores its first SIGTERM; =noboard
                                    prints no board reading (the stop-path test's own desk case).
    fake_card_e190.py host <rgm136's sparsity_host arguments>
                                    stands in for the host: set-up time by its bytes, the calibration launch, launches of about 0.5 s for
                                    --seconds under the --budget rule and the --stop-file, the check launch and the check record, each
                                    launch ANNOUNCED in $E190_FAKE_SCHED at its START with its over-idle watts and its clock. The seconds a
                                    GEMM and the watts are the frozen forecast's points for the arm (E190_FAKE_ARM) and the run's kind
                                    (E190_FAKE_KIND=burst|sus, which the runner sets under --dry only) unless
                                    E190_FAKE_T_SCALE / E190_FAKE_W_SCALE scale them; E190_FAKE_SCALE scales every duration (a fast desk
                                    case); E190_FAKE_HOST=ok|wrong|crash|hang|slowclock picks the outcome (wrong: the check reads wrong;
                                    crash: two launches, then exit 134 with no check; hang: sleeps past `timeout 10`; slowclock: the
                                    kernel clock 700 MHz); with E190_FAKE_HOST_FROM_N only once the schedule holds N launches, and with
                                    E190_FAKE_HOST_COUNT for at most that many processes.
The launch times and watts are the frozen forecast's points (forecast-e190.json): nothing here is a measurement. The process names stay
python3, so no double is ever counted as a device process. SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e190_common as C  # noqa: E402

IDLE_W = {"A": 22.9, "B": 33.1}         # near the forecast's card at rest (desk numbers of the double, not a forecast)
REST_DIE = {"A": 49.0, "B": 57.0}
REST_MHZ = {"A": 600, "B": 600}
CARD = {"A": "0", "B": "1"}
MV = {"A": 519, "B": 499}               # the committed reads: aifoundry2's card and aifoundry1's card 0 519 mV, card 1 499 or 500


def arm():
    return os.environ.get("E190_FAKE_ARM", "A")


def ident_block(card, node):
    """The device layer's identity block, as the real readers and hosts print it on stderr (its two lines the runner reads)."""
    return ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:0]: \n"
            f"PCIe target:                                               /dev/et{card}_{node}        \n"
            "PCIBUS device name:                                        0000:02:00.0        \n"
            f"Physical device ID:                                        {card}                    (0x{card})\n"
            "Form Factor:                                               PCIE                 (0x0)\n")


def hold_node(card, node):
    """Hold <E190_FAKE_DEVDIR>/et<card>_<node> open (a stand-in for the device node), or nothing without E190_FAKE_DEVDIR."""
    d = os.environ.get("E190_FAKE_DEVDIR")
    if not d:
        return None
    os.makedirs(d, exist_ok=True)
    return open(os.path.join(d, f"et{card}_{node}"), "a")


def scale():
    return float(os.environ.get("E190_FAKE_SCALE", "1"))


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def sched_add(rec):
    p = os.environ.get("E190_FAKE_SCHED")
    if p:
        with open(p, "a") as f:
            f.write(json.dumps(rec) + "\n")


def read_sched():
    p = os.environ.get("E190_FAKE_SCHED")
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


def config():
    mode = os.environ.get("E190_FAKE_CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node (double)", file=sys.stderr)
        return 1
    card, mv = CARD[arm()], MV[arm()]
    if mode == "card0":
        card, mv = "0", 519
    elif mode == "mv519":
        mv = 519
    if mode != "noident":
        sys.stderr.write(ident_block(card, "mgmt"))
    j = {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": REST_MHZ[arm()],
         "minion_mv": mv, "fake": True}
    if mode == "tdp70":
        j["tdp_w"] = 70
    elif mode == "thr70":
        j["temp_threshold_c"] = 70
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    print(json.dumps(j, separators=(",", ":")))
    return 0


def holders():
    """et-who's lines for the stand-in nodes and lock: every process (of any user) whose open files include them, read from /proc/*/fd as
    et-who's fuser reads it; the node printed under its real name (/dev/etN_...), the lock as lock:etsoc-shire<card>.lock."""
    import pwd
    d = os.environ.get("E190_FAKE_DEVDIR")
    lk = os.environ.get("E190_FAKE_LOCK")
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
                names.add(f"lock:etsoc-shire{CARD[arm()]}.lock")
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
    m = os.environ.get("E190_FAKE_ETWHO", "free")
    import pwd
    me = pwd.getpwuid(os.getuid()).pw_name      # our login as et-who would print it (the runner resolves it the same way)
    card = "1" if arm() == "B" else "0"
    lines = holders()
    if m == "other":
        lines.append(f"/dev/et{card}_ops someoneelse 4242 other_host")
    elif m == "ours0":
        lines.append(f"/dev/et0_ops {me} 4343 sparsity_host")
    elif m == "other0":
        lines.append("/dev/et0_ops someoneelse 4444 other_host")
    print("\n".join(lines) if lines else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Card:
    def __init__(self):
        self.a = arm()
        self.die = REST_DIE[self.a]
        self.tau = float(os.environ.get("E190_FAKE_TAU_S", "6"))
        self.leak = float(os.environ.get("E190_FAKE_LEAK", "0.4"))
        self.rng = random.Random(190)
        inj = os.environ.get("E190_FAKE_INJECT")
        self.inj = json.load(open(inj)) if inj and os.path.exists(inj) else []
        self.used = [0] * len(self.inj)
        self.t_start = time.time()

    def sample(self, dt):
        t = time.time()
        sched = read_sched()
        busy = [x for x in sched if x["t0"] <= t < x["t1"]]
        started = sum(1 for x in sched if x["t0"] <= t)
        dp = max([x["dp"] for x in busy], default=0.0)      # one launch runs at a time; a window's 20 ms tail may overlap the next
        mhz = max([x["mhz"] for x in busy], default=REST_MHZ[self.a])
        idle = IDLE_W[self.a] + self.leak * (self.die - REST_DIE[self.a])
        bw = idle + dp + self.rng.gauss(0, 0.05)
        eq = REST_DIE[self.a] + 0.25 * (idle + dp - IDLE_W[self.a])
        self.die += (eq - self.die) * min(1.0, dt / max(0.05, self.tau))
        die = int(round(self.die))
        high = die + 3
        for i, j in enumerate(self.inj):
            if "after_launches" in j and started < j["after_launches"]:
                continue
            if "from_s" in j and t - self.t_start < j["from_s"]:
                continue
            if "count" in j and self.used[i] >= j["count"]:
                continue
            self.used[i] += 1
            if "board_w" in j:
                bw = float(j["board_w"])
            if "die" in j:
                die = int(j["die"])
                high = max(high, die)
            if "high" in j:
                high = int(j["high"])
        s = {"t_ms": int(t * 1000), "took_ms": 21, "since_reset_ms": -1, "board_w": round(bw, 2),
                "temp_c": {"pmic": die - 5, "ioshire": [die - 8, die - 9, die - 7], "minshire": [die, die - 2, high]},
                "mhz": {"minion": mhz, "noc": 1000, "ddr": 1600}, "fake": True}
        if os.environ.get("E190_FAKE_SAMPLER") == "noboard":
            del s["board_w"]
        return s


STOP_REQ = [0]


def sample(argv):
    mode = os.environ.get("E190_FAKE_SAMPLER", "ok")
    if mode == "dead":
        return 1
    seconds = float(arg(argv, "--seconds", "10"))
    every = int(arg(argv, "--every-ms", "100")) / 1000.0
    # note 1: dies:<N> exits once the schedule holds N launches; hangs:<N> then stops printing and stays alive (each once a session: a
    # marker file beside the schedule, so the restarted sampler is a good one); card0 holds card 0's mgmt node
    limit, kind = None, None
    if mode.startswith("dies:") or mode.startswith("hangs:"):
        kind, n = mode.split(":", 1)
        limit = int(n)
    node = hold_node("0" if mode == "card0" else CARD[arm()], "mgmt")

    def on_term(signum, frame):
        STOP_REQ[0] += 1
    signal.signal(signal.SIGTERM, on_term)
    signal.signal(signal.SIGINT, on_term)
    card = Card()
    t0 = time.time()
    silent = False
    while time.time() - t0 < seconds:
        if STOP_REQ[0] >= (2 if mode == "stubborn" else 1):
            break
        if limit is not None and not silent and len(read_sched()) >= limit:
            mk = (os.environ.get("E190_FAKE_SCHED") or "/nonexistent") + f".sampler-{kind}"
            if not os.path.exists(mk):
                try:
                    open(mk, "w").close()
                except OSError:
                    pass
                if kind == "dies":
                    print(f"the double's sampler dies at {len(read_sched())} launches (desk case)", file=sys.stderr)
                    return 1
                silent = True
            limit = None
        if silent:
            time.sleep(every)          # hangs: alive, silent until SIGTERM
            continue
        s = card.sample(every)
        sys.stdout.write(json.dumps(s, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        time.sleep(every)
    del node
    return 0


def host(argv):
    a = arm()
    typ = arg(argv, "--type", "fp32")
    vals = arg(argv, "--values", "")
    secs = float(arg(argv, "--seconds", "0"))
    budget = float(arg(argv, "--budget", "8"))
    stopf = arg(argv, "--stop-file", "")
    kernel = arg(argv, "--kernel", "")
    if not kernel:
        print("cannot read kernel ", file=sys.stderr)
        return 1
    arm_name = vals.split(":")[0]
    mb, nb, kb = (int(x) for x in arm_name[len("gemmL"):].split("x"))
    ops_pass = mb * nb * 2 * kb * 32
    fc = C.forecast()
    f = C.ARMS[a]["clock_mhz"]
    tg = fc["speed"][typ][f"t{f}_s"]["point"] * float(os.environ.get("E190_FAKE_T_SCALE", "1"))
    kind = "sus" if os.environ.get("E190_FAKE_KIND") == "sus" else "burst"
    dp = fc["cells"][f"{a}.{typ}.{kind}"]["W_over"]["point"] * float(os.environ.get("E190_FAKE_W_SCALE", "1"))
    mode = os.environ.get("E190_FAKE_HOST", "ok")
    if mode != "ok" and os.environ.get("E190_FAKE_HOST_FROM_N"):
        # the mode only once the schedule holds N launches (the runs, not the smoke), and for at most E190_FAKE_HOST_COUNT processes
        if len(read_sched()) < int(os.environ["E190_FAKE_HOST_FROM_N"]):
            mode = "ok"
        elif os.environ.get("E190_FAKE_HOST_COUNT"):
            cp = os.environ.get("E190_FAKE_SCHED", "") + ".modecount"
            n_used = int(open(cp).read() or 0) if os.path.exists(cp) else 0
            if n_used >= int(os.environ["E190_FAKE_HOST_COUNT"]):
                mode = "ok"
            else:
                open(cp, "w").write(str(n_used + 1))
    if mode == "slowclock":
        f = 700
    if mode == "norise":            # note 1: launches that announce no watts (the board does not rise over its rest)
        dp = 0.0
    sc = scale()
    if secs <= 2.0:                 # note 1: the smoke's processes at no less than a quarter of their time, so the 10 Hz sampler sees
        sc = max(sc, float(os.environ.get("E190_FAKE_SMOKE_SCALE", "0.25")))   # enough of their launches for the board's rise
        # (the launch counts are the virtual clock's, so a scale changes no count)
    ab_mb = {"fp32": 512, "fp16": 256, "int8": 128}[typ]
    t_open = time.time()
    # note 1: the device layer's identity block on stderr and the ops node held, as the real host's (card0: card 0's; noident: neither)
    hcard = "0" if mode == "card0" else CARD[a]
    node = None
    if mode != "noident":
        sys.stderr.write(ident_block(hcard, "ops"))
        sys.stderr.flush()
        node = hold_node(hcard, "ops")
    if mode == "hang":
        time.sleep(30)
        return 0
    time.sleep((0.167 + 0.00095 * ab_mb) * sc)
    print(f"device ready in {time.time() - t_open:.2f} s", file=sys.stderr)
    bad = 0
    nlaunch = [0]

    def one(passes, n):
        """One launch: the kernel's own counters (wall_s, cycles) on the double's VIRTUAL clock (passes x the GEMM's seconds, unscaled),
        so the reducer reads the forecast's seconds and the arm's clock at any E190_FAKE_SCALE; the epoch stamps and the sleep are real
        (the virtual wall x the scale), so the sampler's real samples fall inside the launch's real window."""
        wall = passes * tg
        t0 = time.time()
        sched_add({"t0": t0, "t1": t0 + wall * sc + 0.02, "dp": dp, "mhz": f, "launch": n})
        time.sleep(wall * sc)
        t1 = time.time()
        cyc = int(f * 1e6 * wall * 0.999)
        ops = passes * ops_pass
        rec = {"test": "fma", "arm": arm_name, "gen": "randn", "type": typ, "pattern": "none", "values": vals, "b_stream": 0,
               "minions": 1024, "shire_mask": "0xffffffff", "iters": ops, "passes": passes, "launch": n, "cycles_max": cyc,
               "cycles_mean": cyc * 0.9995, "cycles_per_op": round(cyc * 0.9995 / ops, 3), "wall_s": round(wall, 6),
               "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), "ghz": round(f / 1000.0, 4), "tensor_errors": 0,
               "result": "unchecked", "ok": True}
        print("SPARSITY " + json.dumps(rec, separators=(",", ":")), flush=True)
        nlaunch[0] += 1
        return wall
    wall = one(1, -1)
    iters = max(1, int(1 * 0.5 / max(wall, 1e-4)))
    spent, n = 0.0, 0
    while spent < secs:
        if time.time() - t_open > budget * sc:
            print(f"stopping: device-time budget of {budget:.1f} s used", file=sys.stderr)
            break
        if stopf and os.path.exists(stopf):
            print(f"stopping: {stopf} exists", file=sys.stderr)
            break
        if mode == "crash" and n == 2:
            print("FAIL: the double crashed (desk case)", file=sys.stderr)
            return 134
        spent += one(iters, n)
        n += 1
    last = one(1, -3)
    t0 = time.time()
    time.sleep(0.05 * sc)
    res = "wrong" if mode == "wrong" else ("exact" if typ == "int8" else "approx")
    ok = res != "wrong"
    bad += 0 if ok else 1
    rec = {"test": "check", "arm": arm_name, "gen": "randn", "type": typ, "minions": 1024, "iters": 0, "launch": -2,
           "cycles_per_op": round(f * 1e6 * tg / ops_pass * 0.9995, 3), "wall_s": 0, "t_start_ms": int(t0 * 1000),
           "t_end_ms": int(time.time() * 1000), "ghz": 0, "words": 16384, "exact": 16384 if res == "exact" else 0,
           "within": 16384 if ok else 16000, "result": res, "ok": ok}
    print("SPARSITY " + json.dumps(rec, separators=(",", ":")), flush=True)
    print(f"device held for {time.time() - t_open:.2f} s", file=sys.stderr)
    del last, node
    return 1 if bad else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    w = argv[0]
    if w == "config":
        return config()
    if w == "etwho":
        return etwho()
    if w == "sample":
        return sample(argv[1:])
    if w == "host":
        return host(argv[1:])
    print(f"fake_card_e190: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
