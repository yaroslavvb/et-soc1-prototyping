#!/usr/bin/env python3
"""E210's kit (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum): what the box runner, the doubles, the reducer, the collector and
the desk tests share. E206's kit form for its arm A (tools/claims-v3/e206/e206_common.py, landed in 906699ea and run FULL on this card by E206
arm A, data d7e4f35e), as kit-e207 ported it for E207 on the same card (its local commit 4bd6e38c, under verification when this was written),
for E210's one card, aifoundry3 card 0, and E210's registered order. Python's own modules only: it runs on aifoundry3 under the system python3
(3.12.3 by kit-e207's read there on Mon 16 Nov 2026 22:19 PST) and at the desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e210.json (every case, every run with its host argv, the blocks, the order:
E210.md section 6) and forecast-e210.json (the smoke's reference: E206's measured cycles an op at the shape, calibration > S > e206_points;
E210.md section 6: "cycles an op 50-250% of E206's at the shape"), each at its frozen sha256 (score_e210.py's FROZEN); and the registration's
list SHA256SUMS-e210-registration (the sha256 of each of E210's 489 tile files). It adds:
  - THE ARM'S IDENTITY (E210.md 6; one arm, "A", E206's word for it): aifoundry3 card 0 (its one card: /dev/et0_*, the lock
    etsoc-shire0.lock, ET_DEVICES unset, the box tree ~/aifoundry, the box's reader build/ettelem/ettelem at the sha256 E206's kit read there
    on Mon 16 Nov 2026 12:02 PST and kit-e207 again at 22:19 PST), the start config gate (TDP 0 W / 65 C / 600 MHz, read as found) and the
    clock band (590-610 MHz);
  - THE BUILD'S PINS (kernel-e210.json, equal to E206's): rgm136 from tools/claims-v3/e136/rgm136 into build/e210rgm (a new folder of ours);
    THE KERNEL GATE (check_e210.py): the .text always the registered 61315bf6..., and the whole ELF the registered aace138c... or else its
    loadable identity the pinned one (E206's pin, which E206 arm A's build on this box met); the host read by its behaviour, never its bytes;
  - THE TILES: every file a run's --values names (493: the four kinds tiles at kinds.json's sha256, E210's 489 at the registration list's);
  - THE STOP LINES (E210.md 6: E206 arm A's as amended there): the board above 70 W on 3 samples in a row that carry a board reading; the die
    (the shires' mean, or the hottest sensor's latch once it has risen during the session) at or above 70 C. THE LATCH READING: the telemetry's
    minshire[2] is a latch held since the card's last statistics reset (docs/findings/14-card-behaviour.md, its dated note of Tue 3 Nov 2026):
    on aifoundry3 card 0 it read 87 C in every committed sample of E189, E195, E196, E197 and E206 arm A, so it trips only once it has RISEN
    during the session above the lowest value it read since the session's first sample and reads at or above the line;
  - THE OPENING (E210.md 6): 60 s at rest (the session's rest reading: the die gate is formed from it); THE SMOKE: one checked 2 s process
    each of random@S1, zeros@S1 and random@S2 (rc 0, every launch ok, the check of C exact or approx, cycles an op 50-250% of E206's at the
    shape, the board at least 2 W over the rest, the host on card 0); THE PROBE: one checked 2 s process of maxalte@S2 (every board sample at
    or under 64 W and the die under 63 C, else maxalte leaves the session: a registered rule, not a stop); then the stop-path test (no launch);
  - THE GATES: the die gate min(60, rest die + 4) C (at most 300 s, else that run is NO DATA); THE CARD-TIME RULE (E210.md 6: no run starts
    after 85 card-minutes; the session ends at 95 after the run in progress) and the window's last end;
  - THE ORDER: points-e210.json > runs (171: two random@S1 warm-up ties, six passes of chained A B B A blocks, a closing random@S1 tie), each run
    one host process `timeout 10 <host> <the run's host_args> --kernel <ELF> --stop-file <STOP>`, never `timeout -k`; the tile paths in
    --values stay as registered, relative to the box tree's root, the host's working directory (E206 arm A's form);
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E206's form, line for line): rgm136's
    host prints its SPARSITY records on stdout; a runtime may print "Opening device N" on the same stdout. drop_runtime removes every such line
    wherever it fell, pass after pass until none is left; runtime_cards names the cards those lines open (another card than card 0 is an
    identity trip); each "SPARSITY {...}" line must parse whole and carry its command's own fields, else it is NOT read (counted);
  - the counted launch (E210.md 6): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, and its kernel clock
    (cycles_max / wall_s) in 590-610 MHz.
    python3 -I -B tools/claims-v3/e210/e210_common.py        the self-check (E210-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PTS_F = os.path.join(HERE, "points-e210.json")
FC_F = os.path.join(HERE, "forecast-e210.json")
REG_LIST_F = os.path.join(HERE, "SHA256SUMS-e210-registration")
FROZEN = {"points-e210.json": "5773671b3cc6af8aff29c3332d4644bb3e28200f344e940da46474945cc4dd6a",     # E210.md section 0 (score_e210.py)
          "forecast-e210.json": "dbc2d3f3b1d4796f1504424bc30cf40648840c1064754a6f8012d926be93fe67"}

# ---- the build (build_e210.sh writes it on the box, from the box tree's root)
BUILD_DIR = "build/e210rgm"
HOST = BUILD_DIR + "/host/sparsity_host"
ELF = BUILD_DIR + "/kernel/sparsity.elf"
BUILD_REC = BUILD_DIR + "/BUILD-e210.json"
RGM_SRC = "tools/claims-v3/e136/rgm136"
KERNEL_PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"   # kernel-e210.json kernel_elf_sha256 (E136's build record)
TEXT_PIN = "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763"     # kernel-e210.json kernel_text_sha256
GUARD = "tools/claims-v3/e210/ettelem_guard_e210.sh"
BUILDER = "build_e210.sh"

# ---- the one arm (E210.md 6): A, as E206 arm A's form names it
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # read on aifoundry3 Mon 16 Nov 2026 12:02 and 22:19 PST
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0},
}

# ---- the kinds tiles (kinds.json > kinds > fp32 > <name> > sha256); E210's own 489 are read from the registration's list (tiles())
KINDS_TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/fp32/sparse50.bin": "43ababfe5f3fed0963600a119a5ec805b433636594616042cac4fbab1fd69530",
    "tools/claims-v3/kinds/tiles/fp32/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/fp32/ones.bin": "fef951e6c76ad6a01b208af650ca6d95769bec840e009981c5ae1316a42c90b1",
}
KINDS_MANIFEST = "tools/claims-v3/kinds/kinds.json"
E210_TILE_PREFIX = "tools/claims-v3/e210/tiles/fp32/"

# ---- the session's timing: the registration's numbers (E210.md 6; points-e210.json > plan), and the kit's own (marked)
REST_READ_S = 10.0          # E210.md 6: "10 s at rest (p_rest = the median of its last 5 s)"
REST_WINDOW_S = 5.0         # E210.md 6
OPEN_REST_S = 60.0          # E210.md 6: "the opening - 60 s at rest" (the session's rest reading; the die gate from it)
SMOKE_CASES = ("random@S1", "zeros@S1", "random@S2")         # E210.md 6: one checked 2 s process each, in this order
PROBE_CASE = "maxalte@S2"   # E210.md 6 and points-e210.json > probe_first
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # "a checked 2 s process"; the budget is E146's, E190's, E206's and E207's smoke's (the kit's reading)
PROBE_SECONDS, PROBE_BUDGET = 2.0, 3.5     # "one checked 2 s process of maxalte@S2"; the smoke's budget (the kit's reading)
PROBE_BOARD_MAX_W = 64.0    # E210.md 6: "every board sample at or under 64 W"
PROBE_DIE_BELOW_C = 63.0    # E210.md 6: "and the die under 63 C"
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E210.md 6: "--seconds 6 --budget 7.5"
TAIL_S = 4.0                # E210.md 6: "a 4 s tail"
GATE_WAIT_S = 300.0         # E210.md 6: "at most 300 s, else that run is NO DATA"
CARD_RULE_S = 85 * 60.0     # E210.md 6: no run starts after 85 card-minutes
CAP_S = 95 * 60.0           # E210.md 6: the session ends at 95 after the run in progress (the round's cap is 100)
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's, E207's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz, E210.md 6's "10 Hz samples")
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
CYC_LO, CYC_HI = 0.5, 2.5   # E210.md 6: the smoke's cycles an op within 50-250% of E206's at the shape
MHZ_BAND = (590.0, 610.0)   # E210.md 6: the kernel clock a counted launch is in, and the scorer's clock band
STOP_BOARD_W, STOP_IN_ROW, STOP_DIE_C = 70.0, 3, 70.0          # E210.md 6: the board above 70 W on 3 samples in a row; the die at 70 C
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # a runtime's line on a host's or a reader's stdout (aifoundry1's form)
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


_CACHE = {}


def _frozen(name, path):
    if name not in _CACHE:
        with open(path, "rb") as f:
            raw = f.read()
        got = hashlib.sha256(raw).hexdigest()
        if got != FROZEN[os.path.basename(path)]:
            raise ValueError(f"{os.path.basename(path)} is not its frozen bytes ({got[:12]}, want {FROZEN[os.path.basename(path)][:12]})")
        _CACHE[name] = json.loads(raw.decode())
    return _CACHE[name]


def points():
    """points-e210.json at its frozen sha256 (else ValueError: the box check's harness read refuses first)."""
    return _frozen("pts", PTS_F)


def forecast():
    """forecast-e210.json at its frozen sha256 (read for the smoke's reference only: E206's measured cycles an op at the shape)."""
    return _frozen("fc", FC_F)


def tiles():
    """Every file a run's --values names, with its sha256: the four kinds tiles (kinds.json's) and E210's 489 (the registration's list)."""
    if "tiles" not in _CACHE:
        t = dict(KINDS_TILES)
        with open(REG_LIST_F) as f:
            for ln in f:
                parts = ln.rstrip("\n").split("  ", 1)
                if len(parts) == 2 and parts[1].startswith(E210_TILE_PREFIX):
                    t[parts[1]] = parts[0]
        _CACHE["tiles"] = t
    return _CACHE["tiles"]


def cases():
    return {c["case"]: c for c in points()["cases"]}


def sequence(arm):
    """The registered order: [{"n", "run", "case", "kind", "shape", "role", "pass", "host_args"}, ...] (points-e210.json > runs, 171)."""
    if arm not in ARMS:
        raise KeyError(arm)
    return [dict(x) for x in points()["runs"]]


def run_key(r):
    return r["run"]


def case_args(case):
    """The host arguments of a case: those of its first run in the registered order (the smoke's and the probe's processes use them with
    --seconds 2 --budget 3.5)."""
    for r in points()["runs"]:
        if r["case"] == case:
            return list(r["host_args"])
    raise KeyError(case)


def host_argv(root, host_args, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the registered host_args, --seconds and --budget set to the process form, then the
    kit's --kernel and --stop-file (kernel-e210.json: "the kit adds --kernel, --stop-file and its absolute paths"). The --values string is the
    registered one: its tile paths are read relative to the box tree's root (the host's working directory), as E206 arm A ran."""
    a = list(host_args)
    for flag, val in (("--seconds", f"{seconds:g}"), ("--budget", f"{budget:g}")):
        a[a.index(flag) + 1] = val
    return [os.path.join(root, HOST)] + a + ["--kernel", os.path.join(root, ELF), "--stop-file", stop_file]


def arg_of(argv, name):
    argv = list(argv or [])
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else None


def expect_of(argv):
    """The record fields a process's command line fixes: what every SPARSITY record of that process must carry."""
    vals = arg_of(argv, "--values") or ""
    mask = int(arg_of(argv, "--shires") or "0", 0)
    per = int(arg_of(argv, "--per-shire") or "0", 0)
    return {"arm": vals.split(":")[0], "type": arg_of(argv, "--type"), "values": vals, "shire_mask": "0x%x" % mask,
            "minions": bin(mask).count("1") * per}


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


def latch_of(s):
    ms = (s.get("temp_c") or {}).get("minshire") or []
    return ms[2] if len(ms) > 2 else None


def kclock(L):
    """A launch's kernel clock in MHz: cycles_max / wall_s (E119's clock_x)."""
    w = L.get("wall_s") or 0
    return (L.get("cycles_max") or 0) / w / 1e6 if w > 0 else None


def counted(L, arm=None):
    """E210.md 6's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


def smoke_ref(case):
    """E206's measured cycles an op at the case's shape and kind (forecast-e210.json > calibration > S > e206_points > kind > cycles_per_op:
    random@S1 p029, zeros@S1 p080, random@S2 p034): the smoke's 50-250% reads against it."""
    kind, shape = case.split("@")
    p = forecast()["calibration"][shape]["e206_points"][kind]
    return float(p["cycles_per_op"]), p["point"]


def gate_c(arm, rest_die):
    """The die gate a run starts under (E210.md 6): min(60, rest die + 4); None with no rest die (no run starts)."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def stops_of(arm):
    """The arm's stop lines under the watcher's keys (E210.md 6)."""
    if arm not in ARMS:
        raise KeyError(arm)
    return {"board_cap_w": STOP_BOARD_W, "cap_consecutive": STOP_IN_ROW, "abs_stop_c": STOP_DIE_C}


def probe_verdict(window, latch_low):
    """THE PROBE's rule (E210.md 6) on the live samples inside its process window: IN when there is at least one sample with a board reading
    and one with a die reading, every board reading at or under 64 W and every die reading under 63 C; the die read as the stop line reads
    it (the shires' mean; the latch only once it has risen above the session's lowest latch reading, latch_low). (verdict, board max, die max,
    why)."""
    bws = [s.get("board_w") for s in window if s.get("board_w") is not None]
    dies = []
    for s in window:
        d = die_of(s)
        if d is not None:
            dies.append(d)
        h = latch_of(s)
        if h is not None and latch_low is not None and h > latch_low:
            dies.append(h)
    bmax = max(bws) if bws else None
    dmax = max(dies) if dies else None
    why = []
    if not bws:
        why.append("no board reading in the probe's window")
    elif bmax > PROBE_BOARD_MAX_W:
        why.append(f"the board read {bmax} W, above {PROBE_BOARD_MAX_W:g} W")
    if not dies:
        why.append("no die reading in the probe's window")
    elif dmax >= PROBE_DIE_BELOW_C:
        why.append(f"the die read {dmax} C, not under {PROBE_DIE_BELOW_C:g} C")
    return ("OUT" if why else "IN"), bmax, dmax, "; ".join(why)


# ---- the host's records and the config read, from a source no runtime print can split (E206's functions, line for line)
def drop_runtime(text):
    """(the text without runtime lines, [the runtime lines dropped, in the order removed]): every RUNTIME_LINE removed wherever it fell,
    pass after pass until none is left (a runtime line printed INSIDE another runtime line leaves a whole one behind after the first pass;
    the second pass removes it). Each pass removes at least one line, so the loop ends."""
    text = text or ""
    found = []
    while True:
        hits = [m.group(0)[:-1] for m in RUNTIME_LINE.finditer(text)]
        if not hits:
            return text, found
        found += hits
        text = RUNTIME_LINE.sub("", text)


def runtime_cards(lines):
    """The cards the runtime lines open, as strings in order ("Opening device 1" -> "1"); the runner treats a line naming another card than
    card 0 as an identity trip, on a host's, a config read's or the sampler's stdout."""
    out = []
    for ln in lines or []:
        m = RUNTIME_CARD.search(ln or "")
        if m:
            out.append(str(int(m.group(1))))
    return out


def host_records(text, argv=None):
    """(fma records, check records, info): the host's SPARSITY records from its stdout, runtime lines dropped first; each must parse whole
    as a JSON object and, with argv, carry its command's own fields (an fma record: test, arm, type, values, shire_mask, minions; a check
    record: test, arm, type, minions), else it is not read (info counts it: unparsed, mismatched; any other line is 'other')."""
    body, rt = drop_runtime(text)
    want = expect_of(argv) if argv else None
    fma, chk, info = [], [], {"runtime_lines": rt, "unparsed": 0, "mismatched": [], "other": 0}
    for ln in body.split("\n"):
        if not ln.strip():
            continue
        if not ln.startswith("SPARSITY "):
            info["other"] += 1
            continue
        try:
            j = json.loads(ln[9:])
        except ValueError:
            info["unparsed"] += 1
            continue
        if not isinstance(j, dict) or j.get("test") not in ("fma", "check"):
            info["unparsed"] += 1
            continue
        if want:
            keys = ("arm", "type", "values", "shire_mask", "minions") if j["test"] == "fma" else ("arm", "type", "minions")
            bad = {k: (j.get(k), want[k]) for k in keys if j.get(k) != want[k]}
            if bad:
                info["mismatched"].append({"launch": j.get("launch"), "test": j["test"], "differs": {k: list(v) for k, v in bad.items()}})
                continue
        (fma if j["test"] == "fma" else chk).append(j)
    return fma, chk, info


def last_json(text):
    """The last line that parses whole as a JSON object, else {} (a cut line is no reading)."""
    for ln in reversed((text or "").splitlines()):
        s = ln.strip()
        if s.startswith("{") and s.endswith("}"):
            try:
                j = json.loads(s)
            except ValueError:
                continue
            if isinstance(j, dict):
                return j
    return {}


def config_json(text):
    """The config read's JSON line, its runtime lines dropped first."""
    return last_json(drop_runtime(text)[0])


def config_ok(arm, j):
    """The start config the arm's line rests on (TDP 0 W / 65 C / 600 MHz: E210.md 6 "at its pinned 600 MHz (a boot-time TDP of 0 latches
    the governor), as found"), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (E210.md 6; E206's watcher, line for line): the shires' mean at or above abs_stop_c trips at once; the
    latch (minshire[2]) trips only when it has risen above the lowest value it read since the first sample and reads at or above abs_stop_c; a
    board reading above board_cap_w on cap_consecutive samples in a row trips (a reading at or under the line starts the count again; a sample
    with no board reading neither counts nor breaks the row). The first trip is kept; trip_file, if given, is touched at the trip (the real
    lines' file is the host's --stop-file, so a running host ends at its next launch boundary, about 0.5 s; nothing is ever killed)."""

    def __init__(self, board_cap_w, cap_consecutive, abs_stop_c, trip_file=None):
        self.board_cap_w, self.need, self.abs_stop_c = float(board_cap_w), int(cap_consecutive), float(abs_stop_c)
        self.trip_file = trip_file
        self.over = 0
        self.stop = None
        self.t_trip = None
        self.latch_low = None       # the lowest latch read since the first sample

    def feed(self, s):
        if self.stop:
            return []
        bw = s.get("board_w")
        die, high = die_of(s), latch_of(s)
        if die is not None and die >= self.abs_stop_c:
            return self._trip(f"die {die} C (the shires' mean) at or above {self.abs_stop_c:g} C", s)
        if high is not None:
            if self.latch_low is not None and high > self.latch_low and high >= self.abs_stop_c:
                return self._trip(f"the hottest sensor's latch rose to {high} C (from {self.latch_low} C this session), at or above "
                                  f"{self.abs_stop_c:g} C", s)
            self.latch_low = high if self.latch_low is None else min(self.latch_low, high)
        if bw is None:              # no board reading: neither counted nor breaking the row
            return []
        if bw > self.board_cap_w:
            self.over += 1
            if self.over >= self.need:
                return self._trip(f"board {bw} W above {self.board_cap_w:g} W on {self.need} samples in a row", s)
        else:
            self.over = 0
        return []

    def _trip(self, why, s):
        self.stop = why
        self.t_trip = s.get("t_ms")
        if self.trip_file:
            try:
                with open(self.trip_file, "a"):
                    os.utime(self.trip_file, None)
            except OSError:
                pass
        return ["stop"]


def selfcheck():
    bad = []
    try:
        pts, fc = points(), forecast()
    except (OSError, ValueError) as e:
        return [f"the registration's files ({type(e).__name__}: {str(e)[:100]})"]
    seq = sequence("A")
    # the order (E210.md 6): 171 runs, n 1..171, ties at 1, 2 and 171, six passes, every block's runs in the order
    if len(seq) != 171 or pts["n_runs"] != 171 or [r["n"] for r in seq] != list(range(1, 172)):
        bad.append(f"the sequence is not 171 runs numbered in order ({len(seq)})")
    if [r["run"] for r in seq if r["role"] == "tie"] != ["001-open-random-S1", "002-open-random-S1", "171-close-random-S1"]:
        bad.append("the ties are not 001, 002 (the opening's warm-ups) and 171 (the closing)")
    order = [r["run"] for r in seq]
    for b in pts["blocks"]:
        idx = [order.index(x) for x in b["runs"]]
        if idx != sorted(idx) or idx[3] - idx[0] != 3 or [seq[i]["role"] for i in idx] != ["R", "P", "P", "R"]:
            bad.append(f"block {b['block']} is not a chained R P P R in the order")
            break
    if len(pts["blocks"]) != 54 or sorted({r["pass"] for r in seq}) != ["close", "open", "pass1", "pass2", "pass3", "pass4", "pass5", "pass6"]:
        bad.append("the blocks or the passes")
    want_kinds = {"pass1": "sparse50 bhalfeq highmant8 arow50 badjeq ones lowmant8 negzero signs hd4 zeros",
                  "pass2": "highmant8 hd4 maxalte bhalfeq zeros lowmant8 negzero ones sparse50",
                  "pass3": "zeros hd4 signs negzero lowmant8 ones badjeq arow50 highmant8 bhalfeq sparse50",
                  "pass4": "sparse50 ones negzero lowmant8 zeros bhalfeq maxalte hd4 highmant8",
                  "pass5": "bhalfeq negzero hd4 badjeq arow50 signs highmant8 lowmant8",
                  "pass6": "maxalte negzero lowmant8 bhalfeq highmant8 hd4"}
    for ps, ks in want_kinds.items():
        got = []
        for r in seq:
            if r["pass"] == ps and r["role"] == "P" and (not got or got[-1] != r["kind"]):
                got.append(r["kind"])
        if " ".join(got) != ks:
            bad.append(f"{ps}'s kinds {got} are not E210.md section 6's")
    if pts["probe_first"] != [PROBE_CASE] or not cases()[PROBE_CASE]["probe_first"]:
        bad.append("the probe's case")
    for c in SMOKE_CASES:
        if c not in cases():
            bad.append(f"the smoke's case {c}")
    pl = pts["plan"]
    if (pl["no_run_starts_after_card_minutes"], pl["session_ends_by_card_minutes"]) != (CARD_RULE_S / 60, CAP_S / 60):
        bad.append("the card-time rule and cap against points-e210.json's plan")
    # every run's argv: E206's host string, the case's values, fp32, the full mask
    for r in seq:
        a = r["host_args"]
        c = cases()[r["case"]]
        if a[:6] != ["--test", "fma", "--type", "fp32", "--pattern", "none"] or arg_of(a, "--values") != c["values"] or \
                arg_of(a, "--shires") != "0xffffffff" or arg_of(a, "--per-shire") != "32" or arg_of(a, "--seconds") != "6" or \
                arg_of(a, "--budget") != "7.5" or arg_of(a, "--seed") != "1" or len(a) != 18 or "-k" in a:
            bad.append(f"run {r['run']}'s host_args")
            break
        if arg_of(a, "--values").split(":")[0] != pts["shapes"][r["shape"]]["arm"]:
            bad.append(f"run {r['run']}'s arm is not its shape's")
            break
    a = host_argv("/T", case_args("random@S1"), RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if a[:2] != ["/T/build/e210rgm/host/sparsity_host", "--test"] or arg_of(a, "--values") != "gemmL1x1x1:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" \
            or arg_of(a, "--kernel") != "/T/build/e210rgm/kernel/sparsity.elf" or arg_of(a, "--stop-file") != "/T/STOP" or arg_of(a, "--seconds") != "6":
        bad.append(f"the argv {a[:4]}")
    s = host_argv("/T", case_args(PROBE_CASE), PROBE_SECONDS, PROBE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or not arg_of(s, "--values").startswith("gemmL1x1x4:tiles:tools/claims-v3/e210/tiles/fp32/maxalte/maxalte_00.bin,"):
        bad.append("the probe's argv")
    if expect_of(a) != {"arm": "gemmL1x1x1", "type": "fp32", "values": "gemmL1x1x1:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
                        "shire_mask": "0xffffffff", "minions": 1024}:
        bad.append(f"expect_of {expect_of(a)}")
    # the tiles: every file a run names, at its sha256 (the kinds tiles against kinds.json)
    named = set()
    for r in seq:
        named |= set(arg_of(r["host_args"], "--values").split(":", 2)[2].split(","))
    T = tiles()
    if named != set(T) or len(T) != 493 or sum(1 for x in T if x.startswith(E210_TILE_PREFIX)) != 489:
        bad.append(f"the tiles: {len(named)} named, {len(T)} pinned")
    try:
        kj = load(os.path.join(REPO, KINDS_MANIFEST))["kinds"]
        for f, h in KINDS_TILES.items():
            if kj["fp32"][os.path.basename(f)[:-4]]["sha256"] != h:
                bad.append(f"{f}: not kinds.json's sha256")
    except (OSError, KeyError, ValueError, TypeError) as e:
        bad.append(f"kinds.json could not be read ({type(e).__name__})")
    # the smoke's reference: E206's measured cycles an op at the shape
    want_ref = {"random@S1": (537.9815, "p029"), "zeros@S1": (537.9895, "p080"), "random@S2": (831.723, "p034")}
    for c in SMOKE_CASES:
        if smoke_ref(c) != want_ref[c]:
            bad.append(f"the smoke's reference for {c}: {smoke_ref(c)}")
    # the probe's rule
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
    if probe_verdict([smp(63.9), smp(64.0)], 87)[0] != "IN" or probe_verdict([smp(64.01)], 87)[0] != "OUT" or \
            probe_verdict([smp(die=62.9)], 87)[0] != "IN" or probe_verdict([smp(die=63)], 87)[0] != "OUT" or \
            probe_verdict([smp(high=88)], 87)[0] != "OUT" or probe_verdict([smp(high=87)], 87)[0] != "IN" or probe_verdict([], 87)[0] != "OUT" or \
            probe_verdict([{"t_ms": 1, "board_w": 50}], 87)[0] != "OUT":
        bad.append("the probe's rule (64 W at or under, the die under 63 C, the latch as it rises)")
    # the stop lines: the watcher's semantics, the latch reading (E206's cases)
    st = Stops(70, 3, 70)
    r = [st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(70.0)), st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(71))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or ""):
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(70, 3, 70)
    if [st.feed(smp(die=69, high=87)) for _ in range(5)] != [[]] * 5 or st.feed(smp(die=70, high=87)) != ["stop"] or "shires' mean" not in st.stop:
        bad.append("the die line: the 87 C latch must not trip it, the mean at 70 C must")
    st = Stops(70, 3, 70)
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=88)) != ["stop"] or "latch rose" not in st.stop:
        bad.append("the latch rising past its session value")
    st = Stops(70, 3, 70)
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=50)) != [] or st.feed(smp(die=60, high=71)) != ["stop"]:
        bad.append("the latch after a drop rising past the line")
    st = Stops(70, 3, 70)       # a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 73}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 73}) != [] or \
            st.feed({"t_ms": 4, "board_w": 73}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(70, 3, 70)       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 69.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
        bad.append("a reading under the line between over-line readings did not break the row")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 300e6}
    if not counted(L) or counted(dict(L, cycles_max=400e6)) or counted(dict(L, launch=-1)) or counted(dict(L, launch=-3)) or \
            counted(dict(L, ok=False)) or counted(dict(L, wall_s=0.05, cycles_max=30e6)) or counted(dict(L, passes=0)) or counted(dict(L, test="check")):
        bad.append("the counted launch")
    # the records: runtime lines inside a record, a cut record, a record of another command (a pattern's long --values string)
    pv = case_args("signs@S1")
    ap = host_argv("/T", pv, RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    rec = {"test": "fma", "arm": "gemmL1x1x1", "gen": "tiles", "type": "fp32", "pattern": "none", "values": arg_of(pv, "--values"), "b_stream": 0,
           "minions": 1024, "shire_mask": "0xffffffff", "iters": 1024, "passes": 1, "launch": 0, "cycles_max": 34500000, "cycles_per_op": 538.0,
           "wall_s": 0.0575, "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in list(range(0, 400, 7)) + list(range(len(line) - 300, len(line) + 1, 7)):
        f_, c_, inf = host_records(line[:k] + "Opening device 1\n" + line[k:] + "\n", ap)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 1"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    for k in range(0, 400, 13):      # a runtime line printed INSIDE another runtime line, the pair inside a record
        for j in (0, 3, 9, len("Opening device 1")):
            outer = "Opening device 1\n"
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            f_, c_, inf = host_records(line[:k] + pair + line[k:] + "\n", ap)
            if f_ != [rec] or sorted(inf["runtime_lines"]) != ["Opening device 0", "Opening device 1"] or inf["unparsed"]:
                bad.append(f"two nested runtime lines (the inner at {j}) at offset {k} of a record")
                break
        else:
            continue
        break
    if runtime_cards(["Opening device 1", "Opening device 0", "x"]) != ["1", "0"] or runtime_cards([]) != []:
        bad.append("runtime_cards")
    f_, c_, inf = host_records(line[:40] + "\n", ap)
    if f_ or inf["unparsed"] != 1:
        bad.append("a cut record was read")
    f_, c_, inf = host_records(line.replace("signs_07.bin", "signs_08.bin", 1) + "\n", ap)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another --values (one tile file changed) was read")
    f_, c_, inf = host_records(line + "\n", host_argv("/T", case_args("lowmant8@S1"), 6, 7.5, "/S"))
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another pattern was read")
    if config_json("Opening device 0\n" + '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":0,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("B", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}):
        bad.append("the start config")
    if gate_c("A", 50.0) != 54.0 or gate_c("A", 58.0) != 60.0 or gate_c("A", None) is not None:
        bad.append("the die gate")
    try:
        sequence("B")
        bad.append("an arm B sequence")
    except KeyError:
        pass
    if abs(RUN_MAX_S - 28.0) > 1e-9:
        bad.append("RUN_MAX_S")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E210-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
