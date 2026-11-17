#!/usr/bin/env python3
"""E210's test doubles (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; ported from kit-e207's E207 kit, its local commit 4bd6e38c):
E206's doubles (tools/claims-v3/e206/fake_card_e206.py, landed in 906699ea; E190's v2 doubles behind them) for E210's one card and E210's
host arguments. No device, no lock, no box. The process names stay python3, so no double is ever counted as a device process. Nothing here is
a measurement: a launch's seconds a GEMM and the counter's cycles an op are E206 arm A's measured random at the shape (forecast-e210.json >
calibration > S: t_gemm_s; e206_points > random > cycles_per_op), the same for every case at a shape (the time equality E210 registers); its
watts over idle are E206's random W at the shape plus one frozen route's dJ for the case (E210_FAKE_TRUTH = R1 (default) | R3L | R3 | R4 |
R1pure | R1g: forecast-e210.json > cases > routes_W; a case the route does not forecast takes R4's, as score_e210.py's own stand-ins do);
the card's rest values are desk numbers of the double.

    fake_card_e210.py config        stands in for `ettelem config`: the start config (TDP 0 W / 65 C / 600 MHz / 523 mV, aifoundry3's committed
                                    read) and on stderr the device layer's identity block as the real reader prints it (/dev/et0_mgmt, ID 0).
                                    E210_FAKE_CONFIG = ok | card1 (card 1's block: a device layer that opened another card) | noident (no
                                    block) | tdp65 | tdp0 | mhz800 | fail (rc 1) | runtime ("Opening device 0" on stdout first: card 0's,
                                    its own) | runtime1 ("Opening device 1" first: a runtime that opened another card) | hang (ignores
                                    SIGTERM and lives E210_FAKE_HANG_S seconds, default 14: a reader hung past its timeout's TERM)
    fake_card_e210.py etwho         stands in for `et-who`: every process (of any user) whose open files include the stand-in nodes
                                    (E210_FAKE_DEVDIR) or the stand-in lock (E210_FAKE_LOCK), read from /proc as et-who's fuser reads them,
                                    printed under the real names (/dev/etN_..., lock:etsoc-shire0.lock); plus E210_FAKE_ETWHO = other
                                    (another login on card 0) | ours1 (a line of ours on card 1) | other1 (another login on card 1) | fail
                                    (exit 1: unreadable)
    fake_card_e210.py sample --seconds T --every-ms M
                                    stands in for `ettelem sample`: a toy card whose board power is its idle (rising E210_FAKE_LEAK W a C of
                                    die, default 0.4) plus the over-idle watts of the launches the host double announces in $E210_FAKE_SCHED,
                                    in real time, its die following its power with a first-order lag (E210_FAKE_TAU_S, default 6 s), its
                                    minshire [mean, 46, the latch] with the latch at the committed 87 C, holding <DEVDIR>/et0_mgmt open while
                                    it runs. E210_FAKE_INJECT names a JSON file of injections, each {"board_w" | "die" | "high": value} with
                                    optional "after_launches", "from_s", "count". E210_FAKE_SAMPLER = dead (prints nothing, exits 1) |
                                    stubborn (ignores its first SIGTERM) | noboard | card1 (holds et1_mgmt) | dies:<N> (exits once the
                                    schedule holds N launches) | hangs:<N> (then silent, alive) | deaf:<N> (then silent AND ignoring every
                                    SIGTERM and SIGINT, alive E210_FAKE_DEAF_S seconds, default 40, then <sched>.sampler-deaf-ended and exit
                                    0: a sampler that will not stop, which nothing may kill)
    fake_card_e210.py host <rgm136's sparsity_host arguments>
                                    stands in for the host: the case (by --values: every case is one string), the device opened FIRST (the
                                    identity block on stderr, <DEVDIR>/et0_ops held) and THEN, for gen tiles, every tile file of --values
                                    read as rgm136's fillPools reads it, relative to the working directory (2 x 1,024 bytes each; a file
                                    missing or short: "FAIL: cannot read 2 x 1024 bytes of tiles from <p>", rc 1, as the real host after
                                    its device Session opened); its set-up time by the shape's footprint, the calibration launch, launches
                                    of about 0.5 s for --seconds under the --budget rule and the --stop-file, the check launch and the check
                                    record, each launch ANNOUNCED in $E210_FAKE_SCHED at its START with its over-idle watts (above, x
                                    E210_FAKE_W_SCALE; E210_FAKE_HOTCASE=<case> adds E210_FAKE_HOT_W, default 40, to that case's) and its
                                    clock. The kernel's counters (wall_s, cycles) run on a VIRTUAL clock (passes x the shape's seconds a
                                    GEMM, x E210_FAKE_T_SCALE), so the reducer reads those seconds at any E210_FAKE_SCALE; the epoch stamps
                                    and the sleeps are real (scaled). E210_FAKE_HOST = ok | wrong (the check reads wrong) | crash (two
                                    launches, then exit 134, no check) | hang (sleeps 30 s; `timeout 10`'s TERM ends it: rc 124) |
                                    hang_term (IGNORES SIGTERM and lives E210_FAKE_HANG_S seconds, default 14, then writes
                                    <sched>.hang-ended and exits 0: a host hung past its TERM, which nothing may kill) | k1 ("kernel did not
                                    finish within 8 s, aborting the stream" on stderr, rc 1) | slowclock (700 MHz) | card1 (names and holds
                                    card 1) | noident | norise (no watts) | runtime ("Opening device 0", card 0's own line, printed on stdout
                                    at the start AND inside the first record, at E210_FAKE_SPLIT bytes, default 77) | runtime1 ("Opening
                                    device 1" printed on stdout at the start, the rest as ok: a runtime that opened another card) | mismatch
                                    (records naming another shire mask) | cyc3x (the counter's mean at 3 x the shape's) | cyc1001 (the
                                    counter's mean 0.2% over the shape's: the time equality's case) | nocheck (no check record printed); with
                                    E210_FAKE_HOST_FROM_N only once the schedule holds N launches, with E210_FAKE_HOST_CASE only for that
                                    case, and with E210_FAKE_HOST_COUNT for at most that many processes.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import random
import signal
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e210_common as C  # noqa: E402

IDLE_W = {"A": 24.6}                    # near aifoundry3 card 0 at rest (E206 arm A read 24.57 W): a desk number of the double, not a forecast
REST_DIE = {"A": 51.0}
LATCH = {"A": 87}                       # the committed latch (E189-E197 and E206 arm A on aifoundry3 card 0)
CARD = {"A": "0"}
MV = {"A": 523}
CFG = {"A": {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600}}


def arm():
    return os.environ.get("E210_FAKE_ARM", "A")


def ident_block(card, node):
    return ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:0]: \n"
            f"PCIe target:                                               /dev/et{card}_{node}        \n"
            "PCIBUS device name:                                        0000:02:00.0        \n"
            f"Physical device ID:                                        {card}                    (0x{card})\n"
            "Form Factor:                                               PCIE                 (0x0)\n")


def hold_node(card, node):
    d = os.environ.get("E210_FAKE_DEVDIR")
    if not d:
        return None
    os.makedirs(d, exist_ok=True)
    return open(os.path.join(d, f"et{card}_{node}"), "a")


def scale():
    return float(os.environ.get("E210_FAKE_SCALE", "1"))


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def sched_add(rec):
    p = os.environ.get("E210_FAKE_SCHED")
    if p:
        with open(p, "a") as f:
            f.write(json.dumps(rec) + "\n")


def read_sched():
    p = os.environ.get("E210_FAKE_SCHED")
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


def ignore_term_and_live(seconds, marker=None):
    """A process hung past its TERM: SIGTERM and SIGINT ignored, alive for `seconds`, then (marker) a file saying it ended by itself."""
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    t = time.time()
    while time.time() - t < seconds:
        time.sleep(0.2)
    if marker:
        try:
            with open(marker, "w") as f:
                f.write(f"the hung double ended by itself after {time.time() - t:.1f} s (pid {os.getpid()}); nothing killed it\n")
        except OSError:
            pass


def config():
    mode = os.environ.get("E210_FAKE_CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node (double)", file=sys.stderr)
        return 1
    if mode == "hang":
        sys.stderr.write(ident_block(CARD[arm()], "mgmt"))
        sys.stderr.flush()
        ignore_term_and_live(float(os.environ.get("E210_FAKE_HANG_S", "14")),
                             (os.environ.get("E210_FAKE_SCHED") or "/nonexistent") + ".config-hang-ended")
        return 0
    card, mv = CARD[arm()], MV[arm()]
    if mode == "card1":                 # a device layer that opened card 1 (another card than E210's): the identity gate must refuse it
        card, mv = "1", 499
    if mode != "noident":
        sys.stderr.write(ident_block(card, "mgmt"))
    j = dict(CFG[arm()], minion_mv=mv, fake=True)
    if mode == "tdp65":
        j["tdp_w"] = 65
    elif mode == "tdp0":
        j["tdp_w"] = 0
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    if mode == "runtime":               # a runtime line naming card 0 (E210's own card): dropped and counted
        sys.stdout.write("Opening device 0\n")
    elif mode == "runtime1":            # a runtime line naming card 1 (another card): an identity trip
        sys.stdout.write("Opening device 1\n")
    print(json.dumps(j, separators=(",", ":")))
    return 0


def holders():
    import pwd
    d = os.environ.get("E210_FAKE_DEVDIR")
    lk = os.environ.get("E210_FAKE_LOCK")
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
    m = os.environ.get("E210_FAKE_ETWHO", "free")
    if m == "fail":
        print("et-who: the holders read failed (double)", file=sys.stderr)
        return 1
    import pwd
    me = pwd.getpwuid(os.getuid()).pw_name
    card = CARD[arm()]
    lines = holders()
    if m == "other":
        lines.append(f"/dev/et{card}_ops someoneelse 4242 00:01 other_host")
    elif m == "ours1":
        lines.append(f"/dev/et1_ops {me} 4343 00:01 sparsity_host")
    elif m == "other1":
        lines.append("/dev/et1_ops someoneelse 4444 00:01 other_host")
    print("\n".join(lines) if lines else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Card:
    def __init__(self):
        self.a = arm()
        self.die = REST_DIE[self.a]
        self.tau = float(os.environ.get("E210_FAKE_TAU_S", "6"))
        self.leak = float(os.environ.get("E210_FAKE_LEAK", "0.4"))
        self.rng = random.Random(210)
        inj = os.environ.get("E210_FAKE_INJECT")
        self.inj = json.load(open(inj)) if inj and os.path.exists(inj) else []
        self.used = [0] * len(self.inj)
        self.t_start = time.time()

    def sample(self, dt):
        t = time.time()
        sched = read_sched()
        busy = [x for x in sched if x["t0"] <= t < x["t1"]]
        started = sum(1 for x in sched if x["t0"] <= t)
        dp = max([x["dp"] for x in busy], default=0.0)
        mhz = max([x["mhz"] for x in busy], default=600)
        idle = IDLE_W[self.a] + self.leak * (self.die - REST_DIE[self.a])
        bw = idle + dp + self.rng.gauss(0, 0.05)
        eq = REST_DIE[self.a] + 0.25 * (idle + dp - IDLE_W[self.a])
        self.die += (eq - self.die) * min(1.0, dt / max(0.05, self.tau))
        die = int(round(self.die))
        high = LATCH[self.a]
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
            if "high" in j:
                high = int(j["high"])
        s = {"t_ms": int(t * 1000), "took_ms": 21, "since_reset_ms": -1, "board_w": round(bw, 2),
             "temp_c": {"pmic": die - 5, "ioshire": [die - 8, die - 9, die - 7], "minshire": [die, 46, high]},
             "mhz": {"minion": mhz, "noc": 1000, "ddr": 1600}, "fake": True}
        if os.environ.get("E210_FAKE_SAMPLER") == "noboard":
            del s["board_w"]
        return s


STOP_REQ = [0]


def sample(argv):
    mode = os.environ.get("E210_FAKE_SAMPLER", "ok")
    if mode == "dead":
        return 1
    seconds = float(arg(argv, "--seconds", "10"))
    every = int(arg(argv, "--every-ms", "100")) / 1000.0
    limit, kind = None, None
    if mode.startswith("dies:") or mode.startswith("hangs:") or mode.startswith("deaf:"):
        kind, n = mode.split(":", 1)
        limit = int(n)
    node = hold_node("1" if mode == "card1" else CARD[arm()], "mgmt")
    sys.stderr.write(ident_block("1" if mode == "card1" else CARD[arm()], "mgmt"))
    sys.stderr.flush()

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
            mk = (os.environ.get("E210_FAKE_SCHED") or "/nonexistent") + f".sampler-{kind}"
            if not os.path.exists(mk):
                try:
                    open(mk, "w").close()
                except OSError:
                    pass
                if kind == "dies":
                    print(f"the double's sampler dies at {len(read_sched())} launches (desk case)", file=sys.stderr)
                    return 1
                if kind == "deaf":          # fix-e206: silent, every TERM ignored, the node held; it ends by itself (nothing kills it)
                    ignore_term_and_live(float(os.environ.get("E210_FAKE_DEAF_S", "40")),
                                         (os.environ.get("E210_FAKE_SCHED") or "/nonexistent") + ".sampler-deaf-ended")
                    del node
                    return 0
                silent = True
            limit = None
        if silent:
            time.sleep(every)
            continue
        s = card.sample(every)
        sys.stdout.write(json.dumps(s, separators=(",", ":")) + "\n")
        sys.stdout.flush()
        time.sleep(every)
    del node
    return 0


def case_of(argv):
    vals = arg(argv, "--values", "")
    for c in C.points()["cases"]:
        if c["values"] == vals:
            return c
    return None


def watts_of(case):
    """The double's over-idle watts for a case: E206's random W at the shape plus the frozen route's dJ in W (E210_FAKE_TRUTH; R4's where
    the route has no number, as score_e210.py's stand-ins do); random: E206's random W."""
    fc = C.forecast()
    cal = fc["calibration"][case["shape"]]
    if case["kind"] == "random":
        return float(cal["W_random"])
    route = os.environ.get("E210_FAKE_TRUTH", "R1")
    rw = fc["cases"][case["case"]]["routes_W"]
    v = rw.get(route)
    if not isinstance(v, (int, float)):
        v = rw["R4"]
    return float(cal["W_random"]) + float(v)


def host(argv):
    a = arm()
    secs = float(arg(argv, "--seconds", "0"))
    budget = float(arg(argv, "--budget", "8"))
    stopf = arg(argv, "--stop-file", "")
    kernel = arg(argv, "--kernel", "")
    if not kernel:
        print("cannot read kernel ", file=sys.stderr)
        return 1
    cs = case_of(argv)
    if cs is None:
        print("FAIL: the double knows no case for these --values", file=sys.stderr)
        return 1
    shape = C.points()["shapes"][cs["shape"]]
    cal = C.forecast()["calibration"][cs["shape"]]
    typ, vals = "fp32", cs["values"]
    mask = int(arg(argv, "--shires", "0"), 0)
    per = int(arg(argv, "--per-shire", "32"))
    minions = bin(mask).count("1") * per
    ops_pass = int(shape["ops_per_minion_per_gemm"])
    tg = float(cal["t_gemm_s"]) * float(os.environ.get("E210_FAKE_T_SCALE", "1"))
    dp = watts_of(cs) * float(os.environ.get("E210_FAKE_W_SCALE", "1"))
    if os.environ.get("E210_FAKE_HOTCASE") == cs["case"]:
        dp += float(os.environ.get("E210_FAKE_HOT_W", "40"))
    cpo_mean = float(cal["e206_points"]["random"]["cycles_per_op"])     # E206's measured random at the shape, every case alike
    f = 600
    mode = os.environ.get("E210_FAKE_HOST", "ok")
    if mode != "ok" and os.environ.get("E210_FAKE_HOST_CASE") and os.environ["E210_FAKE_HOST_CASE"] != cs["case"]:
        mode = "ok"
    if mode != "ok" and os.environ.get("E210_FAKE_HOST_FROM_N") and len(read_sched()) < int(os.environ["E210_FAKE_HOST_FROM_N"]):
        mode = "ok"
    if mode != "ok" and os.environ.get("E210_FAKE_HOST_COUNT"):
        cp = os.environ.get("E210_FAKE_SCHED", "") + ".modecount"
        n_used = int(open(cp).read() or 0) if os.path.exists(cp) else 0
        if n_used >= int(os.environ["E210_FAKE_HOST_COUNT"]):
            mode = "ok"
        else:
            open(cp, "w").write(str(n_used + 1))
    if mode == "slowclock":
        f = 700
    if mode == "norise":
        dp = 0.0
    if mode == "cyc3x":                 # the counter's mean at 3 x the shape's (the smoke's 50-250% window must refuse it)
        cpo_mean *= 3.0
    if mode == "cyc1001":               # 0.2% over (the time equality's +-0.1% must see it)
        cpo_mean *= 1.002
    sc = scale()
    if secs <= 2.0:                 # the smoke's and the probe's processes at no less than a quarter of their time, so the 10 Hz sampler sees them
        sc = max(sc, float(os.environ.get("E210_FAKE_SMOKE_SCALE", "0.25")))
    mb = float(shape["footprint_MB"])
    t_open = time.time()
    hcard = "1" if mode == "card1" else CARD[a]
    node = None
    if mode != "noident":
        sys.stderr.write(ident_block(hcard, "ops"))
        sys.stderr.flush()
        node = hold_node(hcard, "ops")
    if mode == "hang":
        time.sleep(30)
        return 0
    if mode == "hang_term":
        ignore_term_and_live(float(os.environ.get("E210_FAKE_HANG_S", "14")), (os.environ.get("E210_FAKE_SCHED") or "/nonexistent") + ".hang-ended")
        return 0
    gen = vals.split(":")[1]
    files = [x for x in vals.split(":", 2)[2].split(",") if x]
    for p_ in files:                    # rgm136's fillPools, after its device Session: 2 x 1,024 bytes from each file, from the working directory
        try:
            with open(p_, "rb") as fh:
                ok_read = len(fh.read(2048)) == 2048
        except OSError:
            ok_read = False
        if not ok_read:
            print(f"FAIL: cannot read 2 x 1024 bytes of tiles from {p_}", file=sys.stderr)
            return 1
        if gen != "tiles":              # randn and sparse50 read their first file only (pair 0)
            break
    time.sleep(min(2.0, 0.167 + 0.002 * mb) * sc)
    print(f"device ready in {time.time() - t_open:.2f} s", file=sys.stderr)
    if mode == "runtime":               # card 0's runtime line (E210's own card), at the start and inside the first record
        sys.stdout.write("Opening device 0\n")
        sys.stdout.flush()
    elif mode == "runtime1":            # a runtime line naming card 1 (another card): an identity trip
        sys.stdout.write("Opening device 1\n")
        sys.stdout.flush()
    split = [int(os.environ.get("E210_FAKE_SPLIT", "77"))] if mode == "runtime" else []
    shown_mask = "0x%x" % ((mask << 1) or 2) if mode == "mismatch" else "0x%x" % mask
    bad = 0

    def emit(rec):
        line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
        if split:
            k = split.pop()
            line = line[:k] + "Opening device 0\n" + line[k:]
        print(line, flush=True)

    def one(passes, n):
        wall = passes * tg
        t0 = time.time()
        sched_add({"t0": t0, "t1": t0 + wall * sc + 0.02, "dp": dp, "mhz": f, "launch": n, "case": cs["case"]})
        time.sleep(wall * sc)
        t1 = time.time()
        cyc = int(f * 1e6 * wall * 0.999)
        ops = passes * ops_pass
        cmean = cpo_mean * ops * f / 600.0
        emit({"test": "fma", "arm": cs["arm"], "gen": gen, "type": typ, "pattern": "none", "values": vals, "b_stream": 0,
              "minions": minions, "shire_mask": shown_mask, "iters": ops, "passes": passes, "launch": n, "cycles_max": cyc,
              "cycles_mean": round(cmean, 1), "cycles_per_op": round(cmean / ops, 3), "wall_s": round(wall, 6),
              "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), "ghz": round(f / 1000.0, 4), "tensor_errors": 0,
              "result": "unchecked", "ok": True})
        return wall
    if mode == "k1":
        one(1, -1)
        print("kernel did not finish within 8 s, aborting the stream", file=sys.stderr)
        return 1
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
    one(1, -3)
    if mode == "nocheck":
        print(f"device held for {time.time() - t_open:.2f} s (no check record: desk case)", file=sys.stderr)
        del node
        return 0
    t0 = time.time()
    time.sleep(0.05 * sc)
    res = "wrong" if mode == "wrong" else ("exact" if cs["kind"] in ("negzero", "signs", "zeros", "ones") else "approx")
    ok = res != "wrong"
    bad += 0 if ok else 1
    emit({"test": "check", "arm": cs["arm"], "gen": gen, "type": typ, "minions": minions, "iters": 0, "launch": -2,
          "cycles_per_op": round(cpo_mean * f / 600.0, 3), "wall_s": 0, "t_start_ms": int(t0 * 1000),
          "t_end_ms": int(time.time() * 1000), "ghz": 0, "words": 16384, "exact": 16384 if res == "exact" else 0,
          "within": 16384 if ok else 16000, "result": res, "ok": ok})
    print(f"device held for {time.time() - t_open:.2f} s", file=sys.stderr)
    del node
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
    print(f"fake_card_e210: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
