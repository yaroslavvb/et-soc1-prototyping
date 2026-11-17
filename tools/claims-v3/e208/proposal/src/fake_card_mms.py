#!/usr/bin/env python3
"""1116-mmsweep: the doubles the session runner uses under --dry (no device is opened; Python's own modules only).

    fake_card_mms.py config                          the start or end config read: JSON on stdout, the identity block on stderr
    fake_card_mms.py etwho                           holder lines for the stand-in nodes and lock, read from /proc
    fake_card_mms.py sample --seconds N --every-ms M  the sampler: ettelem's sample lines from a toy card
    fake_card_mms.py host <sparsity_host argv...>    the host: its SPARSITY lines from a toy timing law, the stop file honoured

THE TOY CARD IS A TEST DOUBLE, NOT A FORECAST: its rest, lifts, cycles and clock ratios are arbitrary round numbers chosen to
exercise the runner and the reducer. What it imitates, so the desk tests can see the reduction's rules work: a die that warms
under work and cools at rest with leakage in the board (the rest drifts after every burst, as on the cards); rails that reach the
host through a first-order filter (tau per card, src/mms_common.py) one service-processor pass late, a pass every two samples;
on the governed cards, a clock that starts each process at 600 MHz and steps to 800 MHz 1 s in, and a burst power cap (CAP_W) the
clock dithers under (an arm whose power at 800 MHz would pass it runs at 760 MHz after its first 3 s). The identity values
(card 1's minion rail below 510 mV, card 0's at or above) are E190's dated note 1's rule, which the identity gate reads.

Environment (set by run_mms.py --dry): MMS_FAKE_CARD (a2c0, a1c1, a1c0), MMS_FAKE_DIR (the dry session's stand-in folder:
nodes et<N>_ops and et<N>_mgmt, the state file, a lock file), MMS_FAKE_SCALE (every wait and every launch's real time x this;
the SPARSITY records keep the toy card's own seconds, so the reducer reads them at any scale), and for the desk tests
MMS_FAKE_TRIP (board W added from the first launch of the run whose arm id holds MMS_FAKE_TRIP_ARM, to trip a stop line),
MMS_FAKE_CONFIG_FAIL (the first config read fails: a collision with a collector), MMS_FAKE_WRONG_CARD (the host names card 1
on a card-0 session, or 0 on a card-1 one), MMS_FAKE_HOST_HANG_ARM (the host of that arm ignores SIGTERM and lives 75 s past its
end, real time), MMS_FAKE_SAMPLER_STALL (the sampler stops sending after that many samples, ignores SIGTERM, ends 25 s later),
MMS_FAKE_WRONG_CONFIG (the config read names the other card), MMS_FAKE_HOST_FAIL_AFTER (every host process after that many
exits 3 with its check of C not ok), MMS_FAKE_CONFIG_HANG (start: the first config read, end: every later one, holds the
stand-in mgmt node, ignores SIGTERM and lives 70 s, real time), MMS_FAKE_HOLDER_AFTER and MMS_FAKE_CLOSING_HOLDER (et-who shows
a holder of another login on the card: from a given call on, or at the closing).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import random
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mms_common as C  # noqa: E402

CARD = os.environ.get("MMS_FAKE_CARD", "a1c1")
FD = os.environ.get("MMS_FAKE_DIR", ".")
SCALE = float(os.environ.get("MMS_FAKE_SCALE", "1"))
STATE = os.path.join(FD, "state.json")
NUM = C.CARDS[CARD]["card"]
GOV = C.CARDS[CARD]["governed"]
# arbitrary test values (not a forecast)
REST_W = {"a2c0": 20.0, "a1c1": 30.0, "a1c0": 20.0}[CARD]
REST_DIE = 50.0
MV = {"a2c0": 519, "a1c1": 499, "a1c0": 519}[CARD]           # the identity gate's rule values (E190's dated note 1)
CYC600 = {"l2": {"fp32": 500.0, "fp16": 500.0, "int8": 250.0}, "l3": 1000.0, "dram": 1500.0}
X = {"l2": 1.3, "l3": 1.1, "dram": 1.1}                      # T600 / T800
LIFT600 = {"rnd": {"fp32": 20.0, "fp16": 20.0, "int8": 10.0}, "ones": {"fp32": 10.0, "fp16": 10.0, "int8": 5.0},
           "zeros": {"fp32": 5.0, "fp16": 5.0, "int8": 5.0}}
BASE800_W = 8.0                                              # the governed cards' extra at 800 MHz
CAP_W = 45.0                                                 # the governed cards' burst power cap
LEAK_W_C = 0.4                                               # board W a degree of die over its rest
HEAT_C_W = 0.15                                              # die degrees a watt of board over rest, at the end of a long warm-up
DIE_TAU_S = 8.0
RAIL_SHARE = {"minion": (12.0, 0.45), "sram": (3.0, 0.10), "noc": (2.0, 0.05)}     # rest W, share of the lift
IDENT = ("LOGGER NOT INITIALIZED:\n\t\tET [DEVICE_LAYER][TH:1]: \nPCIe target:                         /dev/et{c}_{k}       \n"
         "Physical device ID:                  {c}                    (0x{c})\n")


def nap(s):
    time.sleep(max(0.0, s * SCALE))


def now_ms():
    return int(time.time() * 1000)


def read_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_state(d):
    tmp = STATE + f".tmp{os.getpid()}"
    with open(tmp, "w") as f:
        json.dump(d, f)
    os.replace(tmp, STATE)


def parse_values(v):
    arm, gen, files = v.split(":", 2)
    mb, nb, kb = (int(x) for x in arm[5:].split("x"))
    kind = "rnd" if gen == "randn" else ("zeros" if files.endswith("zeros.bin") else "ones")
    return mb, nb, kb, kind


def regime(mb, nb, kb):
    if (mb, nb, kb) == (1, 1, 1):
        return "l2"
    return "l3" if 2 * mb * kb + nb * kb + 2 * mb * nb <= 32 else "dram"


def lift_at(st, f):
    """the toy card's board lift over its rest for the running arm at the clock f"""
    lift = st["lift600"] * st["share"]
    if f >= 790:
        lift = lift * (1.0 + 0.9 * (st["regime"] == "l2")) + BASE800_W
    elif f >= 690:
        lift = lift * 1.2 + BASE800_W / 2
    return lift


def cmd_config():
    n_file = os.path.join(FD, "config.count")
    n = int(open(n_file).read()) if os.path.exists(n_file) else 0
    with open(n_file, "w") as f:
        f.write(str(n + 1))
    if os.environ.get("MMS_FAKE_CONFIG_FAIL") and n == 0:
        sys.stderr.write("FAIL: the management node is busy (a test double's collision)\n")
        return 1
    hang = os.environ.get("MMS_FAKE_CONFIG_HANG")
    if (hang == "start" and n == 0) or (hang == "end" and n >= 1):
        node = open(os.path.join(FD, f"et{NUM}_mgmt"), "a")     # held, as a reader stuck in the driver would hold its node
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.stderr.write("a test double that ignores SIGTERM in a config read: alive 70 s\n")
        sys.stderr.flush()
        time.sleep(70.0)
        node.close()
        open(os.path.join(FD, f"config-hang-{hang}.ended"), "a").close()      # it ended by itself (nothing killed it)
        return 1
    num = NUM if not os.environ.get("MMS_FAKE_WRONG_CONFIG") else ("1" if NUM == "0" else "0")
    sys.stderr.write(IDENT.format(c=num, k="mgmt"))
    j = {"tdp_w": 65, "temp_threshold_c": 65, "power_state": 3, "power_state_name": "low_power", "minion_mhz": 600, "minion_mv": MV}
    print(json.dumps(j))
    return 0


def cmd_etwho():
    """Holder lines for the stand-in nodes and lock, as et-who prints them: <node> <login> <pid> <time> <command>. For the desk
    tests, a line of another login on the card: MMS_FAKE_HOLDER_AFTER=N from this double's (N+1)-th call on;
    MMS_FAKE_CLOSING_HOLDER once a config read has been made and no process holds the stand-in mgmt node (the closing)."""
    me = os.environ.get("USER") or str(os.getuid())
    d = os.path.realpath(FD)
    n_file = os.path.join(FD, "etwho.count")
    n = (int(open(n_file).read()) if os.path.exists(n_file) else 0) + 1
    with open(n_file, "w") as f:
        f.write(str(n))
    mgmt_held = False
    for p in sorted(x for x in os.listdir("/proc") if x.isdigit()):
        try:
            fds = os.listdir(f"/proc/{p}/fd")
        except OSError:
            continue
        for fd in fds:
            try:
                tgt = os.readlink(f"/proc/{p}/fd/{fd}")
            except OSError:
                continue
            if tgt.startswith(d + "/et") and (tgt.endswith("_ops") or tgt.endswith("_mgmt")):
                print(f"/dev/{os.path.basename(tgt)} {me} {p} 00:00 stand-in")
                mgmt_held = mgmt_held or tgt == os.path.join(d, f"et{NUM}_mgmt")
            elif tgt == os.path.join(d, "card.lock"):
                print(f"lock:etsoc-shire{NUM}.lock {me} {p} 00:00 stand-in")
    after = int(os.environ.get("MMS_FAKE_HOLDER_AFTER") or 0)
    if after and n > after:
        print(f"/dev/et{NUM}_ops other 4242 00:01 stand-in")
    n_cfg = int(open(os.path.join(FD, "config.count")).read()) if os.path.exists(os.path.join(FD, "config.count")) else 0
    if os.environ.get("MMS_FAKE_CLOSING_HOLDER") and n_cfg >= 1 and not mgmt_held:
        print(f"/dev/et{NUM}_ops other 4243 00:01 stand-in")
    return 0


def cmd_sample(argv):
    secs = float(argv[argv.index("--seconds") + 1]) if "--seconds" in argv else 1e9
    every = float(argv[argv.index("--every-ms") + 1]) if "--every-ms" in argv else 100.0
    stall = int(os.environ.get("MMS_FAKE_SAMPLER_STALL") or 0)
    node = open(os.path.join(FD, f"et{NUM}_mgmt"), "a")        # held while the sampler runs, as the real reader holds its node
    rng = random.Random(7)
    die, t0 = REST_DIE, time.time()
    latch = 70
    trip_w = float(os.environ.get("MMS_FAKE_TRIP") or 0)
    trip_arm = os.environ.get("MMS_FAKE_TRIP_ARM") or ""
    taus = C.CARDS[CARD]["tau_s"]
    rail = {r: v[0] for r, v in RAIL_SHARE.items()}            # the filter's state
    prev_true = dict(rail)                                     # the true power one pass ago (the one-pass lag)
    n, t_pass = 0, time.time()
    while time.time() - t0 < secs * SCALE:
        st = read_state()
        f = 600
        lift = 0.0
        if st.get("running"):
            f = st.get("f", 600)
            lift = lift_at(st, f)
            if GOV and f >= 790:
                lift = min(lift, CAP_W - REST_W)
            if trip_w and trip_arm and trip_arm in st.get("arm", ""):
                lift += trip_w
        board = REST_W + LEAK_W_C * (die - REST_DIE) + lift + rng.gauss(0, 0.15)
        target = REST_DIE + HEAT_C_W * (board - REST_W)
        die += (target - die) * min(1.0, every / 1000.0 / DIE_TAU_S)
        if n % 2 == 0:                                         # a service-processor pass every two samples
            now = time.time()
            for r, (r0, share) in RAIL_SHARE.items():
                a = math.exp(-(now - t_pass) / (taus[r] * SCALE))
                rail[r] = a * rail[r] + (1 - a) * prev_true[r]
                prev_true[r] = r0 + share * lift + LEAK_W_C * share * (die - REST_DIE)
            t_pass = now
        n += 1
        if stall and n > stall:
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            time.sleep(25.0)                                   # stale and deaf to SIGTERM, then gone
            break
        ms = now_ms()
        s = {"t_ms": ms, "took_ms": 22, "since_reset_ms": -1, "board_w": round(board, 2),
             "sp": {"board_avg_w": round(board, 2), "board_min_w": REST_W - 1, "board_max_w": 60.0,
                    "minion_w": [round(rail["minion"], 3), 5.0, 40.0], "sram_w": [round(rail["sram"], 3), 2.0, 9.0],
                    "noc_w": [round(rail["noc"], 3), 1.0, 6.0], "minion_mv": [MV, MV, MV + 100], "sram_mv": [750, 750, 760],
                    "noc_mv": [750, 750, 760], "minion_c": [int(die), 40, latch], "system_c": [40, 35, 50],
                    "minion_mhz": [f, 600, 800], "noc_mhz": [400, 400, 400]},
             "temp_c": {"pmic": 40, "ioshire": [45, 40, 50], "minshire": [int(die), int(die) - 3, latch]},
             "die_mv": {"ddr": 800 - (2 if st.get("running") and st.get("regime") == "dram" else 0), "sram": 750, "maxion": 750,
                        "minion": MV, "pshire": 750, "noc": 750, "ioshire": 750},
             "mhz": {"minion": f, "noc": 400, "ddr": 1600}}
        print(json.dumps(s), flush=True)
        nap(every / 1000.0)
    node.close()
    return 0


def cmd_host(argv):
    a = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--") and not argv[i + 1].startswith("--")}
    t = a["--type"]
    mb, nb, kb, kind = parse_values(a["--values"])
    shires = bin(int(a["--shires"], 16)).count("1")
    seconds, budget, stop = float(a["--seconds"]), float(a["--budget"]), a.get("--stop-file")
    num = NUM if not os.environ.get("MMS_FAKE_WRONG_CARD") else ("1" if NUM == "0" else "0")
    n_file = os.path.join(FD, "host.count")
    n_host = (int(open(n_file).read()) if os.path.exists(n_file) else 0) + 1
    with open(n_file, "w") as f:
        f.write(str(n_host))
    fail = int(os.environ.get("MMS_FAKE_HOST_FAIL_AFTER") or 0) and n_host > int(os.environ.get("MMS_FAKE_HOST_FAIL_AFTER"))
    ops_node = open(os.path.join(FD, f"et{num}_ops"), "a")
    sys.stderr.write(IDENT.format(c=num, k="ops"))
    reg = regime(mb, nb, kb)
    c600 = CYC600[reg][t] if reg == "l2" else CYC600[reg]
    T600 = c600 / 600e6
    T800 = T600 / X[reg]
    share = shires / 32.0
    arm_id = f"{mb}x{nb}x{kb}-{t}-{kind}" + ("" if shires == 32 else f"-s{shires}")
    hang = os.environ.get("MMS_FAKE_HOST_HANG_ARM") and os.environ.get("MMS_FAKE_HOST_HANG_ARM") == arm_id
    st = {"running": True, "t0": time.time(), "lift600": LIFT600[kind][t], "regime": reg, "share": share, "arm": arm_id, "f": 600}
    write_state(st)
    nap(0.3)
    sys.stderr.write("device ready in 0.30 s\n")
    ops_pass = mb * nb * 2 * kb * 32
    v_age = 0.3
    first = max(1, 64000 // ops_pass)
    launch, spent = -1, 0.0
    iters = first
    capped = GOV and REST_W + lift_at(st, 800) > CAP_W

    def clock(age):
        if not GOV or age <= 1.0:
            return 600
        return 760 if capped and age > 3.0 else 800

    while True:
        f = clock(v_age)
        st["f"] = f
        write_state(st)
        T = T600 * 600.0 / f if f != 800 else T800
        wall = iters * ops_pass * T + 0.002
        t_s = now_ms()
        nap(wall)
        t_e = now_ms()
        cmax = (wall - 0.002) * f * 1e6
        cmean = cmax * 0.985
        ops = iters * ops_pass
        print("SPARSITY " + json.dumps({"test": "fma", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "minions": 32 * shires,
                                        "iters": ops, "passes": iters, "launch": launch, "cycles_max": int(cmax),
                                        "cycles_mean": round(cmean, 1), "cycles_per_op": round(cmean / ops, 3), "wall_s": round(wall, 6),
                                        "t_start_ms": t_s, "t_end_ms": t_e, "ghz": round(cmax / wall / 1e9, 4),
                                        "tensor_errors": 0, "result": "unchecked", "ok": True}), flush=True)
        v_age += wall
        if launch == -1:
            iters = max(1, int(iters * 0.5 / wall))
        else:
            spent += wall
        launch += 1
        if spent >= seconds:
            break
        if v_age > budget:
            sys.stderr.write(f"stopping: device-time budget of {budget:.1f} s used\n")
            break
        if stop and os.path.exists(stop):
            sys.stderr.write(f"stopping: {stop} exists\n")
            break
    # the check launch and the check record
    f = clock(v_age)
    T = T600 * 600.0 / f if f != 800 else T800
    wall = ops_pass * T + 0.003
    t_s = now_ms()
    nap(wall)
    print("SPARSITY " + json.dumps({"test": "fma", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "iters": ops_pass, "passes": 1,
                                    "launch": -3, "cycles_max": int((wall - 0.003) * f * 1e6), "cycles_mean": 0, "cycles_per_op": 0,
                                    "wall_s": round(wall, 6), "t_start_ms": t_s, "t_end_ms": now_ms(), "ok": True}), flush=True)
    res = "approx" if (kind == "rnd" and t != "int8") else "exact"
    if fail:
        res = "wrong"
    write_state({"running": False})
    nap(0.2)
    print("SPARSITY " + json.dumps({"test": "check", "arm": f"gemmL{mb}x{nb}x{kb}", "type": t, "launch": -2,
                                    "cycles_per_op": round(c600 * (f / 600.0) / (X[reg] if f == 800 else 1.0), 3), "wall_s": 0,
                                    "words": 8192, "exact": 8192 if res == "exact" else 0, "within": 8192 if not fail else 0,
                                    "result": res, "ok": not fail}), flush=True)
    if hang:
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.stderr.write("a test double that ignores SIGTERM: alive 75 s more\n")
        sys.stderr.flush()
        time.sleep(75.0)
    ops_node.close()
    sys.stderr.write(f"device held for {v_age:.2f} s\n")
    return 3 if fail else 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    w = argv[0]
    if w == "config":
        return cmd_config()
    if w == "etwho":
        return cmd_etwho()
    if w == "sample":
        return cmd_sample(argv[1:])
    if w == "host":
        return cmd_host(argv[1:])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
