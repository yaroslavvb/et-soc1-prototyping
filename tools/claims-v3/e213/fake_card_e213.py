#!/usr/bin/env python3
"""E213's test doubles (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): E211's doubles (tools/claims-v3/e211/fake_card_e211.py,
landed in 2b7f261f: its two hosts, the walk fields) with E206's arm B put back (tools/claims-v3/e206/fake_card_e206.py, landed in 906699ea: card 1,
its 499 mV and 66 C latch, aifoundry1's runtime lines), for E213's two cards, its four arm families and its host arguments. No device, no lock, no
box. The process names stay python3, so no double is ever counted as a device process. Nothing here is a measurement: the launch times and watts
are MM1-v3's frozen forecasts (arm A: tools/matmul/mm1/v3/out/mm1_v3_e213.csv; arm B: forecast-e213b-v3.csv; for the smoke and the ties, which no
forecast prices, the toy 900 / 800 cycles an op and 20 W: e213_common.double_of), and the cards' rest values are desk numbers of the double.
Every E213_FAKE_* word below is read as E213_FAKE_*; the arm is E213_FAKE_ARM (A, the default, or B).

    fake_card_e213.py config        stands in for `ettelem config`: the arm's start config (arm A TDP 0 W / 65 C / 600 MHz / 523 mV,
                                    aifoundry3's committed read; arm B 65 W / 65 C / 600 MHz / 499 mV, card 1's) and on stderr the device
                                    layer's identity block as the real reader prints it (arm A /dev/et0_mgmt, ID 0; arm B /dev/et1_mgmt, ID 1).
                                    E213_FAKE_CONFIG = ok | card1 (the OTHER card's block: arm A card 1's, arm B card 0's, 519 mV) |
                                    mv519 (arm B: card 1's block at 519 mV) | noident (no block) | tdp65 | tdp0 | mhz800 | fail (rc 1) |
                                    runtime ("Opening device <the arm's card>" on stdout first: its own) | runtime1 ("Opening device
                                    <the other card>" first: a runtime that opened another card) | hang (ignores SIGTERM and lives
                                    E213_FAKE_HANG_S seconds, default 14: a reader hung past its timeout's TERM)
    fake_card_e213.py etwho         stands in for `et-who`: every process (of any user) whose open files include the stand-in nodes
                                    (E213_FAKE_DEVDIR) or the stand-in lock (E213_FAKE_LOCK), read from /proc as et-who's fuser reads them,
                                    printed under the real names (/dev/etN_..., lock:etsoc-shire<arm's card>.lock); plus E213_FAKE_ETWHO =
                                    other (another login on the arm's card) | ours1 (a line of ours on the OTHER card) | other1 (another
                                    login on the OTHER card) | fail (exit 1: unreadable)
    fake_card_e213.py sample --seconds T --every-ms M
                                    stands in for `ettelem sample`: a toy card whose board power is its idle (rising E213_FAKE_LEAK W a C of
                                    die, default 0.4) plus the over-idle watts of the launches the host double announces in $E213_FAKE_SCHED,
                                    in real time, its die following its power with a first-order lag (E213_FAKE_TAU_S, default 6 s), its
                                    minshire [mean, 46, the latch] with the latch at the committed 87 C (arm A) or 66 C (arm B), holding
                                    <DEVDIR>/et<card>_mgmt open while it runs. E213_FAKE_INJECT names a JSON file of injections, each {"board_w" | "die" | "high": value} with
                                    optional "after_launches", "from_s", "count". E213_FAKE_SAMPLER = dead (prints nothing, exits 1) |
                                    stubborn (ignores its first SIGTERM) | noboard | card1 (holds the OTHER card's mgmt node) | dies:<N> (exits once the
                                    schedule holds N launches) | hangs:<N> (then silent, alive) | deaf:<N> (then silent AND ignoring every
                                    SIGTERM and SIGINT, alive E213_FAKE_DEAF_S seconds, default 40, then <sched>.sampler-deaf-ended and exit
                                    0: a sampler that will not stop, which nothing may kill)
    fake_card_e213.py host --as rgm136|rgm211 <the host's sparsity_host arguments>
                                    stands in for the host named by --as (E213_FAKE_HOSTKIND otherwise; rgm136 by default): rgm136's
                                    records as E136's host prints them; rgm211's with its walk fields (every launch "walk", "walk_tagged",
                                    "walk_ok"; the check record "walk" and "walk_launches_bad"), the walk nm for a gemmLn arm and mn for
                                    gemmLnc and gemmL (rgm211's own gemmL among them), the tag on every hart only when a gemmLn arm runs an
                                    ELF from rgm211's build folder (a gemmLn arm given rgm136's ELF, which ignores the walk bit, reads
                                    walk_ok false and exits 1, as the real host would; a gemmL or gemmLnc arm reads walk mn, tag 0, whichever
                                    ELF it is given: the walk cannot tell, only the identity gate); the point (by --values and --shires: every point and smoke point is one pair), its
                                    set-up time by its bytes, the calibration launch, launches of about 0.5 s for --seconds under the --budget
                                    rule and the --stop-file, the check launch and the check record, each launch ANNOUNCED in $E213_FAKE_SCHED
                                    at its START with its over-idle watts (the toy forecast's W over idle, x E213_FAKE_W_SCALE) and its clock. The
                                    kernel's counters (wall_s, cycles) run on a VIRTUAL clock (passes x the toy forecast's seconds a GEMM, x
                                    E213_FAKE_T_SCALE), so the reducer reads the forecast's seconds at any E213_FAKE_SCALE; the epoch stamps and
                                    the sleeps are real (scaled). It prints the device layer's identity block on stderr and holds
                                    <DEVDIR>/et<card>_ops. E213_FAKE_HOST = ok | wrong (the check reads wrong) | crash (two launches, then exit 134,
                                    no check) | hang (sleeps 30 s; `timeout 10`'s TERM ends it: rc 124) | hang_term (IGNORES SIGTERM and lives
                                    E213_FAKE_HANG_S seconds, default 14, then writes <sched>.hang-ended and exits 0: a host hung past its TERM,
                                    which nothing may kill) | k1 ("kernel did not finish within 8 s, aborting the stream" on stderr, rc 1) |
                                    slowclock (700 MHz) | card1 (names and holds the OTHER card) | noident | norise (no watts) | runtime ("Opening
                                    device <the arm's card>", its own line, printed on stdout at the start AND inside the first record, at
                                    E213_FAKE_SPLIT bytes, default 77) | runtime1 ("Opening device <the other card>" printed on stdout at the
                                    start, the rest as ok: a runtime that opened another card) | mismatch (records naming another shire mask) | cyc3x | cyc6x (the
                                    counter's mean at 3 x or 6 x the toy figure's counter mean, the wall and the watts as forecast); with
                                    E213_FAKE_HOST_FROM_N only once the schedule holds N launches, and with E213_FAKE_HOST_COUNT for at most
                                    that many processes, and with E213_FAKE_HOST_POINTS (a comma list of point ids) for
                                    those points' processes only; E211's added modes: walkbad (rgm211's host: walk_ok false on every launch,
                                    walk_launches_bad, exit 1) | tensor (one tensor error on the first counted launch: that launch not ok,
                                    exit 1).
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
import e213_common as C  # noqa: E402

IDLE_W = {"A": 24.6, "B": 31.0}         # near each card at rest (E206 arm A 24.57 W; card 1's rest law about 31 W): desk numbers of the double
REST_DIE = {"A": 51.0, "B": 53.0}
LATCH = {"A": 87, "B": 66}              # the committed latches (E189-E197, E206 arm A on aifoundry3 card 0; E198, E199, E206 arm B on card 1)
CARD = {"A": "0", "B": "1"}
OTHER = {"A": "1", "B": "0"}            # the other card: card 1 does not exist on aifoundry3, card 0 is aifoundry1's other card
MV = {"A": 523, "B": 499}
CFG = {"A": {"tdp_w": 0, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600},
       "B": {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 0, "power_state_name": "max_power", "minion_mhz": 600}}


def arm():
    return os.environ.get("E213_FAKE_ARM", "A")


def ident_block(card, node):
    return ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:0]: \n"
            f"PCIe target:                                               /dev/et{card}_{node}        \n"
            "PCIBUS device name:                                        0000:02:00.0        \n"
            f"Physical device ID:                                        {card}                    (0x{card})\n"
            "Form Factor:                                               PCIE                 (0x0)\n")


def hold_node(card, node):
    d = os.environ.get("E213_FAKE_DEVDIR")
    if not d:
        return None
    os.makedirs(d, exist_ok=True)
    return open(os.path.join(d, f"et{card}_{node}"), "a")


def scale():
    return float(os.environ.get("E213_FAKE_SCALE", "1"))


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def sched_add(rec):
    p = os.environ.get("E213_FAKE_SCHED")
    if p:
        with open(p, "a") as f:
            f.write(json.dumps(rec) + "\n")


def read_sched():
    p = os.environ.get("E213_FAKE_SCHED")
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
    mode = os.environ.get("E213_FAKE_CONFIG", "ok")
    if mode == "fail":
        print("ettelem: cannot open the management node (double)", file=sys.stderr)
        return 1
    if mode == "hang":
        sys.stderr.write(ident_block(CARD[arm()], "mgmt"))
        sys.stderr.flush()
        ignore_term_and_live(float(os.environ.get("E213_FAKE_HANG_S", "14")),
                             (os.environ.get("E213_FAKE_SCHED") or "/nonexistent") + ".config-hang-ended")
        return 0
    card, mv = CARD[arm()], MV[arm()]
    if mode == "card1":                 # a device layer that opened the other card: the identity gate must refuse it
        card, mv = OTHER[arm()], 519
    elif mode == "mv519":               # arm B: card 1's block at 519 mV (card 0's voltage): the identity gate must refuse it
        mv = 519
    if mode != "noident":
        sys.stderr.write(ident_block(card, "mgmt"))
    j = dict(CFG[arm()], minion_mv=mv, fake=True)
    if mode == "tdp65":
        j["tdp_w"] = 65
    elif mode == "tdp0":
        j["tdp_w"] = 0
    elif mode == "mhz800":
        j["minion_mhz"] = 800
    if mode == "runtime":               # a runtime line naming the arm's own card: dropped and counted
        sys.stdout.write(f"Opening device {CARD[arm()]}\n")
    elif mode == "runtime1":            # a runtime line naming the other card: an identity trip
        sys.stdout.write(f"Opening device {OTHER[arm()]}\n")
    print(json.dumps(j, separators=(",", ":")))
    return 0


def holders():
    import pwd
    d = os.environ.get("E213_FAKE_DEVDIR")
    lk = os.environ.get("E213_FAKE_LOCK")
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
    m = os.environ.get("E213_FAKE_ETWHO", "free")
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
        lines.append(f"/dev/et{OTHER[arm()]}_ops {me} 4343 00:01 sparsity_host")
    elif m == "other1":
        lines.append(f"/dev/et{OTHER[arm()]}_ops someoneelse 4444 00:01 other_host")
    print("\n".join(lines) if lines else "No process holds an ET-SoC-1 device node or card lock.")
    return 0


class Card:
    def __init__(self):
        self.a = arm()
        self.die = REST_DIE[self.a]
        self.tau = float(os.environ.get("E213_FAKE_TAU_S", "6"))
        self.leak = float(os.environ.get("E213_FAKE_LEAK", "0.4"))
        self.rng = random.Random(207)
        inj = os.environ.get("E213_FAKE_INJECT")
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
        if os.environ.get("E213_FAKE_SAMPLER") == "noboard":
            del s["board_w"]
        return s


STOP_REQ = [0]


def sample(argv):
    mode = os.environ.get("E213_FAKE_SAMPLER", "ok")
    if mode == "dead":
        return 1
    seconds = float(arg(argv, "--seconds", "10"))
    every = int(arg(argv, "--every-ms", "100")) / 1000.0
    limit, kind = None, None
    if mode.startswith("dies:") or mode.startswith("hangs:") or mode.startswith("deaf:"):
        kind, n = mode.split(":", 1)
        limit = int(n)
    node = hold_node(OTHER[arm()] if mode == "card1" else CARD[arm()], "mgmt")
    sys.stderr.write(ident_block(OTHER[arm()] if mode == "card1" else CARD[arm()], "mgmt"))
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
            mk = (os.environ.get("E213_FAKE_SCHED") or "/nonexistent") + f".sampler-{kind}"
            if not os.path.exists(mk):
                try:
                    open(mk, "w").close()
                except OSError:
                    pass
                if kind == "dies":
                    print(f"the double's sampler dies at {len(read_sched())} launches (desk case)", file=sys.stderr)
                    return 1
                if kind == "deaf":          # fix-e206: silent, every TERM ignored, the node held; it ends by itself (nothing kills it)
                    ignore_term_and_live(float(os.environ.get("E213_FAKE_DEAF_S", "40")),
                                         (os.environ.get("E213_FAKE_SCHED") or "/nonexistent") + ".sampler-deaf-ended")
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


def point_of(argv, hk=None, kernel=""):
    """The point a host command runs: by --values and --shires in the arm's points, smoke and tie; among points that share both (arm A's
    'rgm211 gemmL' points spell their arm as their 'rgm136 gemmL' twins do), the one whose loop runs on this host (hk) with an ELF from this
    kernel's build folder; then E213_FAKE_POINT (the runner's id for the process, set in --dry only) decides."""
    vals, mask = arg(argv, "--values", ""), int(arg(argv, "--shires", "0"), 0)
    want = os.environ.get("E213_FAKE_POINT")
    hits = [p for p in C.arm_points(arm()) if C.arg_of(p["host_args"], "--values") == vals and int(p["shire_mask"], 16) == mask]
    if hk:
        h2 = [p for p in hits if C.LOOPS[p["loop"]]["host"] == hk and f"/{C.LOOPS[p['loop']]['elf']}/" in (kernel or "")]
        hits = h2 or [p for p in hits if C.LOOPS[p["loop"]]["host"] == hk] or hits
    for p in hits:
        if p["id"] == want:
            return p
    return hits[0] if hits else None


def host(argv):
    a = arm()
    hk = os.environ.get("E213_FAKE_HOSTKIND", "rgm136")
    if argv[:1] == ["--as"]:
        hk, argv = argv[1], argv[2:]
    secs = float(arg(argv, "--seconds", "0"))
    budget = float(arg(argv, "--budget", "8"))
    stopf = arg(argv, "--stop-file", "")
    kernel = arg(argv, "--kernel", "")
    if not kernel:
        print("cannot read kernel ", file=sys.stderr)
        return 1
    pt = point_of(argv, hk, kernel)
    if pt is None:
        print("FAIL: the double knows no point for these --values and --shires", file=sys.stderr)
        return 1
    fc = C.double_of(pt["id"])               # MM1-v3's frozen seconds and W over idle at its seconds (the toy figures for the smoke and ties)
    typ, vals = pt["format"], C.arg_of(pt["host_args"], "--values")
    tok = pt["arm"]
    nm_arm = tok.startswith("gemmLn") and not tok.startswith("gemmLnc")    # the host reads the walk from the ARM it is given (main.cpp)
    walk_name = "nm" if nm_arm else "mn"
    tag_written = nm_arm and "/rgm211/" in kernel     # rgm136's ELF ignores the walk bit and writes no tag; a gemmL or gemmLnc arm tags none
    mask = int(pt["shire_mask"], 16)
    per = int(arg(argv, "--per-shire", "32"))
    minions = bin(mask).count("1") * per
    ops_pass = int(pt["ops_per_minion_per_gemm"])
    tg = fc["t"] * float(os.environ.get("E213_FAKE_T_SCALE", "1"))
    dp = fc["W"] * float(os.environ.get("E213_FAKE_W_SCALE", "1"))
    f = 600
    mode = os.environ.get("E213_FAKE_HOST", "ok")
    if mode != "ok" and os.environ.get("E213_FAKE_HOST_POINTS") and pt["id"] not in os.environ["E213_FAKE_HOST_POINTS"].split(","):
        mode = "ok"                     # E213_FAKE_HOST_POINTS: the mode for those points' processes only
    if mode != "ok" and os.environ.get("E213_FAKE_HOST_FROM_N"):
        if len(read_sched()) < int(os.environ["E213_FAKE_HOST_FROM_N"]):
            mode = "ok"
        elif os.environ.get("E213_FAKE_HOST_COUNT"):
            cp = os.environ.get("E213_FAKE_SCHED", "") + ".modecount"
            n_used = int(open(cp).read() or 0) if os.path.exists(cp) else 0
            if n_used >= int(os.environ["E213_FAKE_HOST_COUNT"]):
                mode = "ok"
            else:
                open(cp, "w").write(str(n_used + 1))
    if mode == "slowclock":
        f = 700
    if mode == "norise":
        dp = 0.0
    sc = scale()
    if secs <= 2.0:                 # the smoke's processes at no less than a quarter of their time, so the 10 Hz sampler sees them
        sc = max(sc, float(os.environ.get("E213_FAKE_SMOKE_SCALE", "0.25")))
    mb = float((pt.get("bytes_MB") or {}).get("all") or 32.0)
    t_open = time.time()
    hcard = OTHER[a] if mode == "card1" else CARD[a]
    node = None
    if mode != "noident":
        sys.stderr.write(ident_block(hcard, "ops"))
        sys.stderr.flush()
        node = hold_node(hcard, "ops")
    if mode == "hang":
        time.sleep(30)
        return 0
    if mode == "hang_term":
        ignore_term_and_live(float(os.environ.get("E213_FAKE_HANG_S", "14")), (os.environ.get("E213_FAKE_SCHED") or "/nonexistent") + ".hang-ended")
        return 0
    time.sleep(min(2.0, 0.167 + 0.002 * mb) * sc)
    print(f"device ready in {time.time() - t_open:.2f} s", file=sys.stderr)
    if mode == "runtime":               # the arm's own card's runtime line, at the start and inside the first record
        sys.stdout.write(f"Opening device {CARD[a]}\n")
        sys.stdout.flush()
    elif mode == "runtime1":            # a runtime line naming the other card: an identity trip
        sys.stdout.write(f"Opening device {OTHER[a]}\n")
        sys.stdout.flush()
    split = [int(os.environ.get("E213_FAKE_SPLIT", "77"))] if mode == "runtime" else []
    shown_mask = "0x%x" % ((mask << 1) or 2) if mode == "mismatch" else "0x%x" % mask
    bad = 0
    gen = vals.split(":")[1]

    def emit(rec):
        line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
        if split:
            k = split.pop()
            line = line[:k] + f"Opening device {CARD[a]}\n" + line[k:]
        print(line, flush=True)

    cpo_mean = fc.get("cyc_mean")       # the toy forecast's counter mean (the host's cycles_per_op)
    if cpo_mean and mode == "cyc3x":    # the counter's mean at 3 x the toy figure (E213: inside R0's absolute band for the smoke's toy 800)
        cpo_mean *= 3.0
    if cpo_mean and mode == "cyc6x":    # E213: 6 x the toy figure (4,800 cycles an op for the smoke: outside R0's 200-4,000, the smoke gate refuses it)
        cpo_mean *= 6.0

    walk_bad = [0]

    def one(passes, n):
        wall = passes * tg
        t0 = time.time()
        sched_add({"t0": t0, "t1": t0 + wall * sc + 0.02, "dp": dp, "mhz": f, "launch": n})
        time.sleep(wall * sc)
        t1 = time.time()
        cyc = int(f * 1e6 * wall * 0.999)
        ops = passes * ops_pass
        cmean = cpo_mean * ops * f / 600.0 if cpo_mean else cyc * 0.9995
        terr = 1 if (mode == "tensor" and n == 0) else 0
        rec = {"test": "fma", "arm": pt["arm"], "gen": gen, "type": typ, "pattern": "none", "values": vals, "b_stream": 0,
               "minions": minions, "shire_mask": shown_mask, "iters": ops, "passes": passes, "launch": n, "cycles_max": cyc,
               "cycles_mean": round(cmean, 1), "cycles_per_op": round(cmean / ops, 3), "wall_s": round(wall, 6),
               "t_start_ms": int(t0 * 1000), "t_end_ms": int(t1 * 1000), "ghz": round(f / 1000.0, 4), "tensor_errors": terr}
        ok = terr == 0
        if hk == "rgm211":          # rgm211's host's walk check (E211.md 2): the tag on every reporting hart for gemmLn, 0 for the others
            tagged = minions if tag_written else 0
            wok = (tagged == minions) if nm_arm else (tagged == 0)
            if mode == "walkbad":
                wok = False
            walk_bad[0] += 0 if wok else 1
            ok = ok and wok
            rec.update({"walk": walk_name, "walk_tagged": tagged, "walk_ok": wok})
        rec.update({"result": "unchecked", "ok": ok})
        emit(rec)
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
    t0 = time.time()
    time.sleep(0.05 * sc)
    res = "wrong" if mode == "wrong" else ("exact" if typ == "int8" else "approx")
    ok = res != "wrong" and (walk_bad[0] == 0 or hk != "rgm211")
    bad += 0 if ok else 1
    bad += 1 if mode == "tensor" else 0
    crec = {"test": "check", "arm": pt["arm"], "gen": gen, "type": typ, "minions": minions, "iters": 0, "launch": -2,
            "cycles_per_op": round(cpo_mean * f / 600.0 if cpo_mean else f * 1e6 * tg * 0.999 * 0.9995 / ops_pass, 3), "wall_s": 0, "t_start_ms": int(t0 * 1000),
            "t_end_ms": int(time.time() * 1000), "ghz": 0, "words": 1024, "exact": 1024 if res == "exact" else 0,
            "within": 1024 if res != "wrong" else 1000}
    if hk == "rgm211":
        crec.update({"walk": walk_name, "walk_launches_bad": walk_bad[0]})
    crec.update({"result": res, "ok": ok})
    emit(crec)
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
    print(f"fake_card_e213: unknown double {w}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
