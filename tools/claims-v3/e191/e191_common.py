#!/usr/bin/env python3
"""E191's kit (Q178, Sat 14 Nov 2026, written after E189's data commit fa9098c4 and before any E191 datum): what the box runner, the
doubles, the collector and the desk tests share. It is E189's common module (tools/claims-v3/e189/e189_common.py, b42dc95c, unchanged
beside it) ported to aifoundry1 card 1 by E191's dated note 1 (8c8f825f), and nothing else changed:
  - the plan is E191's registered plan-e191.json (K, the order, the stops, the die gate, the cap), read and never changed; its six
    configurations' host arguments and K equal E189's (E191.md 4; step 2 checks it), so E189's host check reads E191's hosts unchanged;
  - THE CARD: aifoundry1 card 1, selected by ET_DEVICES=1 (and V3_DEVICE=1, lib.sh's word for it) in the environment of EVERY process that
    may open a device (note 1, item 1); its lock /run/lock/etsoc-shire1.lock (item 2); the box tree ~/nekko (k6's rb_tree for aifoundry1);
    the telemetry reader build/ettelem/ettelem there at its pin (E157's, E164's, E172's and E190 arm B's on card 1), through E191's guard,
    which refuses any box but aifoundry1 and any ET_DEVICES but 1;
  - the start config's line: TDP 65 W, threshold 65 C, minion 600 MHz (E191.md 2, as E137 and E184 arm B read card 1), and THE IDENTITY
    GATE's bounds (note 1, item 3; e191_ident.py): minion_mv below 510, the read's stderr naming /dev/et1_mgmt and device ID 1;
  - the build directories build/e191ledger and build/e191spp; everything else (the commands, the ramped smoke, THE ADAPTER, THE STOP LINES,
    the cap and the die gate) is E189's, word for word;
  - three kit constants after verify-e191k (fix-e191k): the sampler's freshness (2 s), the stop file's name, the BOUND wait's poll;
  - after verify-e191k2 (fix-e191k2, Sun 15 Nov 2026, before any E191 datum; kit mechanics): sample_live(), what makes a sample LIVE for
    the freshness rule: it carries every reading THE STOP LINES read (board_w, minshire[0] and the minion clock, each a number); a line
    without one of them is kept in the telemetry and fed to the stop lines, but it never keeps the sampler live (verify-e191k2's nit 1).
Python's own modules only (it runs on aifoundry1 under the system python3, and on the desk under /usr/bin/python3 -I -B).
    python3 -I -B tools/claims-v3/e191/e191_common.py        the self-check (E191-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN = os.path.join(HERE, "plan-e191.json")
ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
LEDGER = ORDER[:5]
PROGRAM = {k: ("ledger" if k in LEDGER else "spp") for k in ORDER}
# ---- the card (E191.md 2; note 1, items 1-3)
BOX = "aifoundry1"
TREE = "nekko"                                             # k6's rb_tree for aifoundry1 (E164's, E172's and E190 arm B's tree)
CARD = "1"
ET_DEVICES = "1"                                           # every device-opening process carries it (note 1, item 1)
LOCK = "/run/lock/etsoc-shire1.lock"                       # card 1's lock, held for the session; never card 0's (item 2)
READER = "build/ettelem/ettelem"                           # the lab's telemetry reader on card 1 (in ~/nekko)
READER_SHA256 = "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325"   # E157's, E164's, E172's and E190 arm B's pin
GUARD = "tools/claims-v3/e191/ettelem_guard_e191.sh"      # E128's allow-list in E190's form: aifoundry1 and ET_DEVICES=1 only
CONFIG_LINE = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}   # E191.md 2 (E137, E184 arm B); a different start: the gate
MV_BELOW = 510                                             # note 1, item 3(a): card 1 read 499-500 in every committed read, card 0 519
# ---- the box's build directories (build_e191.sh writes them in ~/nekko)
LEDGER_DIR = "build/e191ledger"
SPP_DIR = "build/e191spp"
LEDGER_HOST = LEDGER_DIR + "/host/ledger_host"
LEDGER_ELF = LEDGER_DIR + "/kernel/ledger.elf"
SPP_HOST = SPP_DIR + "/host/sparseparity_host"
SPP_ELF = SPP_DIR + "/kernel/sparseparity.elf"
BUILD_REC = {"ledger": LEDGER_DIR + "/BUILD-e191.json", "spp": SPP_DIR + "/BUILD-e191.json"}
EXPECT_SMOKE = "docs/reports/data/2026-11-12-q166-progs/digests/expect-b2048-r1-2048.txt"
# ---- E189's numbers, unchanged (E191.md 9-11 register the same)
IDLE_BEFORE_S, IDLE_AFTER_S, EVERY_MS = 8.0, 10.0, 100      # energy.sh's form (E191.md 9)
HOST_TIMEOUT_S = 10                                         # every device-opening process under `timeout 10`
HOST_BOUND_S = HOST_TIMEOUT_S + 20                          # the runner's own bound around it; past it the QUEUE STOPS (run_e191.py)
ANCHOR_S = 120                                              # three 2-minute idle anchors (E191.md 10)
CAP_PASS_START_S = 108 * 60                                 # no pass starts after 108 card-minutes (E191.md 10)
CAP_S = 110 * 60
DIE_GATE_C, DIE_GATE_WAIT_S, DIE_LOW_C = 60, 600, 52        # E191.md 11; below 52 C does not block, it is labelled
STOP_BOARD_W, STOP_DIE_C, CLOCK_MHZ = 65.0, 70.0, 600
CLOSE_CONFIG_S = 15                                         # the end bound: the closing config read's share of the last seconds
# ---- kit mechanics and gates made stricter for safety after verify-e191k (fix-e191k, Sat 14 Nov 2026, before any E191 datum)
SAMPLE_FRESH_S = 2.0          # finding 2 (E190's kit note 1's rule): a pass, a smoke process and the die gate need a sample under 2 s old
STOP_FILE = "STOP"            # finding 5: the session's early stop, a file of this name in its own directory (or SIGTERM to the runner)
BOUND_POLL_S = 1.0            # finding 4: after a BOUND the runner keeps card 1's lock and polls the host's end (nothing is killed)


def plan():
    with open(PLAN) as f:
        return json.load(f)


def device_env(base=None):
    """The environment of every process the runner starts: card 1 selected (ET_DEVICES=1, V3_DEVICE=1), the runtime's libraries."""
    env = dict(os.environ if base is None else base)
    env["LD_LIBRARY_PATH"] = "/opt/et/lib"
    env["ET_DEVICES"] = ET_DEVICES
    env["V3_DEVICE"] = ET_DEVICES
    return env


def sequence(p=None):
    """The session's sequence as plan-e191.json writes it: ('anchor', n) and ('pass', config, k, order_index) items, in order."""
    p = p or plan()
    seq, seen, idx = [("anchor", 1)], {}, 0
    rounds = p["order"]["rounds"]
    for r, rnd in enumerate(rounds):
        for cfg in rnd:
            seen[cfg] = seen.get(cfg, 0) + 1
            idx += 1
            seq.append(("pass", cfg, seen[cfg], idx))
        if r == 1:
            seq.append(("anchor", 2))
    seq.append(("anchor", 3))
    return seq


def check_sequence(p=None):
    """The written-out sequence (plan > order > sequence) equals the one built from the rounds: never re-drawn."""
    p = p or plan()
    words = [s for s in p["order"]["sequence"] if s.startswith("pass ")]
    built = [f"pass {it[3]}: {it[1]} p{it[2]}" for it in sequence(p) if it[0] == "pass"]
    return words == built and len(built) == 24


def host_argv(cfg, p=None, pass_dir=None):
    """One pass's host command line (without `timeout 10`), from the box tree's root."""
    p = p or plan()
    c = p["configs"][cfg]
    if PROGRAM[cfg] == "ledger":
        return [LEDGER_HOST, "--card"] + c["args"].split() + ["--kernel", LEDGER_ELF]
    rec = os.path.join(pass_dir, "host.rec") if pass_dir else "host.rec"
    return [SPP_HOST] + c["args"].split() + c["reps_flag"].split() + ["--kernel", SPP_ELF, "--records-out", rec]


def smoke_runs(programs):
    """The ramped smoke (E191.md 10, E189's), for the programs built today: (name, argv, what it must show)."""
    out = []
    if "ledger" in programs:
        out.append(("ledger-selftest", [LEDGER_HOST, "--selftest"], "selftest"))
        base = [LEDGER_HOST, "--card", "--kernel", LEDGER_ELF, "--launches", "1"]
        out += [("copy-64m-random", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("copy-64m-zeros", base + ["--prog", "copy", "--bytes", "64M", "--passes", "1", "--data", "zeros", "--width", "32"], "ledger"),
                ("copy-1g-random", base + ["--prog", "copy", "--bytes", "1G", "--passes", "1", "--data", "random", "--width", "32"], "ledger"),
                ("sha256-b2048-r1", base + ["--prog", "sha256", "--block", "2048", "--repeat", "1", "--expect", EXPECT_SMOKE], "ledger"),
                ("sort-shuffled-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "shuffled"], "ledger"),
                ("sort-sorted-r1", base + ["--prog", "sort", "--keys", "512", "--reps", "1", "--order", "sorted"], "ledger")]
    if "spp" in programs:
        c = plan()["configs"]["sparse-parity"]
        out.append(("sparse-parity-r1", [SPP_HOST] + c["args"].split() + ["--reps", "1", "--kernel", SPP_ELF], "spp"))
    return out


def last_json(text):
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def ledger_good(raw):
    """Every check of the ledger host's line but the launch count (main.cpp's pass condition without `launched == launches`)."""
    P = raw.get("participants")
    ok = (raw.get("records_bad") == 0 and P and raw.get("records_ok") == P and raw.get("units") == raw.get("units_expected")
          and (raw.get("checked") or 0) > 0 and raw.get("mismatches") == 0 and raw.get("expect_mismatches", 0) == 0)
    return bool(ok)


def adapt_ledger(raw, K):
    """THE ADAPTER (E191.md 8.1, E189's word for word): the ledger host's line -> the reducer's fields. reps_done = launches;
    reps_requested = K; launch_s = wall_s; launch_epoch_ms = [the first launch's t0, the last launch's t1]; status as the host said it;
    problems ["reps: k of K done"] when the budget cut the burst short with every other check good (SHORT: scored on its launches);
    otherwise, when the host said FAIL, the checks that failed (a FAILED RUN, not a datum)."""
    n = int(raw.get("launches") or 0)
    ep = raw.get("launch_epoch_ms") or []
    good = ledger_good(raw)
    short = good and 0 < n < K and raw.get("status") != "PASS"
    out = {"adapter": "e191_common.adapt_ledger (E191.md section 8.1; E189's adapter)", "ledger_prog": raw.get("prog"),
           "status": raw.get("status"), "reps_requested": K, "reps_done": n,
           "launch_s": [float(x) for x in (raw.get("wall_s") or [])],
           "launch_epoch_ms": [ep[0], ep[-1]] if len(ep) >= 2 else [0, 0],
           "kernel": {"cycles_max": (raw.get("hart0_cycles") or {}).get("max")},
           "problems": [], "stop_reason": ""}
    if raw.get("status") == "PASS":
        out["reps_consistent"] = "ok"
    elif short:
        out["reps_consistent"] = "ok"
        out["problems"] = [f"reps: {n} of {K} done"]
        out["stop_reason"] = "budget"
    else:
        why = (f"records_ok {raw.get('records_ok')} of {raw.get('participants')}, records_bad {raw.get('records_bad')}, "
               f"units {raw.get('units')} of {raw.get('units_expected')}, checked {raw.get('checked')}, mismatches "
               f"{raw.get('mismatches')}, expect_mismatches {raw.get('expect_mismatches')}, first_mismatch "
               f"'{raw.get('first_mismatch')}', launches {n} of {K}")
        out["reps_consistent"] = "bad"
        out["problems"] = ["checks: " + why] if raw else ["no JSON line from the ledger host"]
    return out


def reading(cfg, host_json):
    """The pass's reading in words for the session log (the kit's mechanics, Sat 14 Nov 2026, after E189's day: E189's log said only
    "host rc 1, status FAIL" for its SHORT copy bursts, which read like a FAILED RUN at step 10): PASS, SHORT (k of K launches, the
    host's own budget: scored on its launches) or FAILED RUN (not a datum). Nothing scored reads it."""
    h = host_json or {}
    if h.get("reps_consistent") == "bad" or (not h):
        return "FAILED RUN (not a datum)"
    pr = [str(x).split() for x in (h.get("problems") or []) if str(x).startswith("reps: ")]
    if pr and len(pr[0]) >= 4:
        return f"SHORT ({pr[0][1]} of {pr[0][3]} launches, the host's own budget: scored on its launches)"
    if h.get("status") == "PASS":
        return "PASS"
    return "FAILED RUN (not a datum)"


class Stops:
    """THE STOP LINES on live samples (E191.md 11, E189's word for word). feed(sample, in_pass) returns the actions it implies, in order:
    'set-aside' (the first sample off 600 MHz taken in a pass), 'stop' (board >= 65 W or minshire[0] >= 70 C on any live sample, or a
    second sample off 600 MHz taken in a pass). The clock line counts only the samples taken in a pass; a sample off the clock outside a
    pass is recorded in events with counted False and reported. A test threshold (the stop-path test) is passed in."""

    def __init__(self, board_w=STOP_BOARD_W, die_c=STOP_DIE_C, clock_mhz=CLOCK_MHZ):
        self.board_w, self.die_c, self.clock_mhz = board_w, die_c, clock_mhz
        self.off_clock = 0
        self.stop = None
        self.events = []

    def feed(self, s, in_pass):
        acts = []
        bw = s.get("board_w")
        die = ((s.get("temp_c") or {}).get("minshire") or [None])[0]
        mhz = (s.get("mhz") or {}).get("minion")
        t = s.get("t_ms")
        if bw is not None and bw >= self.board_w and not self.stop:
            self.stop = f"board {bw} W at or above {self.board_w:g} W"
            acts.append("stop")
        if die is not None and die >= self.die_c and not self.stop:
            self.stop = f"minshire[0] {die} C at or above {self.die_c:g} C"
            acts.append("stop")
        if mhz is not None and mhz != self.clock_mhz:
            if in_pass:
                self.off_clock += 1
            self.events.append({"t_ms": t, "minion_mhz": mhz, "n": self.off_clock if in_pass else None,
                                "in_pass": bool(in_pass), "counted": bool(in_pass)})
            if in_pass and self.off_clock == 1:
                acts.append("set-aside")
            if in_pass and self.off_clock >= 2 and not self.stop:
                self.stop = f"a second sample off {self.clock_mhz} MHz in a pass ({mhz} MHz)"
                acts.append("stop")
        return acts


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x     # a number, never a bool or NaN


def sample_live(s):
    """A LIVE sample (verify-e191k2's nit 1; fix-e191k2, kit mechanics): one that carries every reading THE STOP LINES read - board_w, minshire[0]
    and the minion clock, each a number. Only a live sample keeps the sampler live (the freshness rule, SAMPLE_FRESH_S) and passes the die
    gate; a line without one of them is kept in the telemetry and fed to the stop lines all the same, but a reader whose power, temperature
    or clock request fails while it still prints lines no longer reads as live (verify-e191k2's break case: lines without board_w kept a session
    'live' while the 65 W line read nothing). Every one of the 37,101 committed real samples verify-e191k2 read carries all three."""
    if not isinstance(s, dict):
        return False
    return _num(s.get("board_w")) and _num(die_of(s)) and _num((s.get("mhz") or {}).get("minion"))


def config_ok(j):
    """The start config's line (E191.md 2): TDP 65 W, threshold 65 C, minion 600 MHz (the identity's bounds are e191_ident's)."""
    return bool(j) and all(j.get(k) == v for k, v in CONFIG_LINE.items())


if __name__ == "__main__":
    import sys
    p = plan()
    bad = []
    if not check_sequence(p):
        bad.append("the sequence differs from plan-e191.json's written order")
    ks = {k: p["configs"][k]["launches_K"] for k in ORDER}
    if ks != {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}:
        bad.append(f"K {ks}")
    for k in LEDGER:
        a = host_argv(k, p)
        if f"--launches {ks[k]}" not in " ".join(a) or "--card" not in a:
            bad.append(f"{k} argv {a}")
    if "--expect" not in host_argv("sha256", p):
        bad.append("sha256 without --expect")
    a = host_argv("sparse-parity", p, "X")
    if a[a.index("--reps") + 1] != "9" or "--budget" not in a:
        bad.append(f"sparse parity argv {a}")
    if p.get("seed") != 191 or "etsoc-shire1.lock" not in json.dumps(p.get("card", {})) or "ET_DEVICES=1" not in json.dumps(p.get("card", {})):
        bad.append("plan-e191.json's card block or seed")
    raw = {"prog": "copy", "participants": 2048, "records_ok": 2048, "records_bad": 0, "units": 5, "units_expected": 5,
           "checked": 2048, "mismatches": 0, "expect_mismatches": 0, "launches": 6, "wall_s": [0.6] * 6,
           "launch_epoch_ms": [1, 2, 3, 4], "hart0_cycles": {"max": 393600000}, "status": "FAIL"}
    h = adapt_ledger(raw, 8)
    if not (h["problems"] == ["reps: 6 of 8 done"] and h["reps_consistent"] == "ok" and h["launch_epoch_ms"] == [1, 4]):
        bad.append(f"adapter short {h}")
    if not reading("copy-zeros", h).startswith("SHORT (6 of 8 launches"):
        bad.append(f"reading short {reading('copy-zeros', h)}")
    raw2 = dict(raw, mismatches=1, first_mismatch="participant 7", launches=8)
    h2 = adapt_ledger(raw2, 8)
    if not (h2["reps_consistent"] == "bad" and h2["problems"][0].startswith("checks:")) or not reading("x", h2).startswith("FAILED RUN"):
        bad.append(f"adapter fail {h2}")
    h3 = adapt_ledger(dict(raw, launches=8, status="PASS"), 8)
    if not (h3["problems"] == [] and h3["reps_done"] == 8 and h3["status"] == "PASS") or reading("x", h3) != "PASS":
        bad.append(f"adapter pass {h3}")
    if reading("sparse-parity", {"status": "FAIL", "reps_consistent": "ok", "problems": ["reps: 7 of 9 done"]})[:5] != "SHORT" or \
            reading("sparse-parity", {}) != "FAILED RUN (not a datum)":
        bad.append("reading of sparse parity's own host.json")

    def smp(mhz=600, bw=30.0, die=55):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, die - 1, die + 1]}, "mhz": {"minion": mhz}}
    st = Stops()
    acts = [st.feed(smp(800), None), st.feed(smp(800), None), st.feed(smp(800), "copy-zeros/p1"), st.feed(smp(600), "copy-zeros/p1"),
            st.feed(smp(800), None), st.feed(smp(800), "sha256/p1")]
    if not (acts == [[], [], ["set-aside"], [], [], ["stop"]] and st.off_clock == 2 and len(st.events) == 5
            and [e["counted"] for e in st.events] == [False, False, True, False, True] and "in a pass" in (st.stop or "")):
        bad.append(f"clock line {acts} {st.events} {st.stop}")
    st2 = Stops()
    if not (st2.feed(smp(800), "x/p1") == ["set-aside"] and st2.feed(smp(800), "x/p1") == ["stop"]):
        bad.append("clock line: two samples in one pass did not set aside and stop")
    st3 = Stops()
    if not (st3.feed(smp(bw=65.0), None) == ["stop"] and Stops().feed(smp(die=70), None) == ["stop"]
            and Stops().feed(smp(bw=64.99, die=69), "x/p1") == []):
        bad.append("board or die line outside a pass, or a sample under both, read wrong")
    if not config_ok({"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) or config_ok({"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok({}) or config_ok({"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}):
        bad.append("config_ok")
    e = device_env({"PATH": "/usr/bin", "ET_DEVICES": "0"})
    if e.get("ET_DEVICES") != "1" or e.get("V3_DEVICE") != "1" or LOCK != "/run/lock/etsoc-shire1.lock":
        bad.append("device_env or the lock")
    # fix-e191k2 (verify-e191k2's nit 1): a live sample carries board_w, minshire[0] and the minion clock, each a number
    live_ok = sample_live(smp()) and sample_live(dict(smp(), board_w=0))
    no_board = dict(smp())
    no_board.pop("board_w")
    dead = [no_board, dict(smp(), board_w=None), dict(smp(), board_w="31.5"), dict(smp(), board_w=True), dict(smp(), board_w=float("nan")),
            dict(smp(), temp_c={"minshire": []}), dict(smp(), temp_c={}), dict(smp(), temp_c={"minshire": [None, 50, 52]}),
            dict(smp(), mhz={"noc": 1000}), dict(smp(), mhz={"minion": None}), {}, None, "x"]
    if not live_ok or any(sample_live(x) for x in dead):
        bad.append("sample_live: " + ("a whole sample read not live" if not live_ok else
                                      f"a sample without a stop line's reading read live ({[i for i, x in enumerate(dead) if sample_live(x)]})"))
    print("E191-COMMON SELF-CHECK " + ("PASS" if not bad else "FAIL: " + "; ".join(bad)))
    sys.exit(0 if not bad else 1)
