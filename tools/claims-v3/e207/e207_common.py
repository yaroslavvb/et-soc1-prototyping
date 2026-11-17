#!/usr/bin/env python3
"""E207's kit (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum): what the box runner, the doubles, the reducer, the collector
and the desk tests share. E206's kit form for its arm A (tools/claims-v3/e206/e206_common.py, landed in 906699ea and run FULL on this card by
E206 arm A, data d7e4f35e), for E207's one card, aifoundry3 card 0; E190's kit form behind it. Python's own modules only: it runs on aifoundry3
under the system python3 (3.12.3 by its read on Mon 16 Nov 2026 22:19 PST) and at the desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e207.json (every point's host arguments, the tie t01's, the smoke's three
points and the order), plan-e207.json (the card, its clock and config, the line, the stops, the gate and the card-time rules) and MM1-v1's
frozen blind-day forecasts (tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv, sha256 90dffe94..., the file E207.md section 0 freezes: the
smoke's cycles an op is read against MM1-v1's counter-mean forecast there, E207.md section 7, R0). It adds:
  - THE ARM'S IDENTITY (E207.md 6; one arm, A, E206's word for it, so the scorer's data form {"arms": {"A": ...}} holds): aifoundry3 card 0
    (its one card: /dev/et0_*, the lock etsoc-shire0.lock, ET_DEVICES unset, the box tree ~/aifoundry, the box's reader build/ettelem/ettelem at
    the sha256 read there on Mon 16 Nov 2026 12:02 PST by E206's kit and again 22:19 PST by this kit), the start config gate (TDP 0 W / 65 C /
    600 MHz, read as found) and the clock band (590-610 MHz);
  - THE BUILD'S PINS (kernel-e207.json, equal to E206's): rgm136 from tools/claims-v3/e136/rgm136 into build/e207rgm (a new folder of ours);
    THE KERNEL GATE (E191's kit fix, check_e207.py): the .text always the registered 61315bf6..., and the whole ELF the registered aace138c...
    or else its loadable identity the pinned one (aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0", read there again on Mon 16 Nov 2026
    22:19 PST, and the string lands in a section the card never loads); the host read by its behaviour, never by its bytes;
  - THE TILES: every file a point's (or the tie's) --values names (10), at the sha256 its manifest records (kinds.json, blind4.json,
    blind3.json);
  - THE STOP LINES (E207.md 6, plan-e207.json "stop": E206 arm A's as amended by E206.md A1 items 1 and 2), with THE LATCH READING: the
    telemetry's minshire[2] is a latch held since the card's last statistics reset (docs/findings/14-card-behaviour.md, its dated note of Tue 3
    Nov 2026), not the hottest sensor now: on aifoundry3 card 0 it read 87 C in every committed sample of E189, E195, E196, E197 and E206 arm A.
    Read as a level it would trip the 70 C line at the first sample. So the die line trips on the shires' mean (minshire[0]) at or above the
    line, or on the latch only when it has RISEN during the session above the lowest value it read since the session's first sample and reads
    at or above the line. The board line: strictly above 70 W on 3 samples in a row that carry a board reading, a sample with no board reading
    neither counting nor breaking the row;
  - THE GATES: the die gate min(60, rest die + 4) C (at most 300 s, else that run is NO DATA), the rest die the median of the shires' mean over
    the smoke's 30 s rest; THE CARD-TIME RULE (E207.md 6: no run starts once the card time passes 60 minutes; the session ends at 70 after the
    run in progress) and the window's last end;
  - THE ORDER: points-e207.json > order > sequence (tie t01, pass 1, tie, pass 2, tie: 109 runs), each run one host process
    `timeout 10 <host> <the point's host_args> --kernel <ELF> --stop-file <STOP>`, never `timeout -k`;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E191's kit note 2; E206's form, line for
    line): rgm136's host prints its SPARSITY records on stdout and has no result file of its own; a runtime may print "Opening device N" on the
    same stdout (aifoundry1's does; aifoundry3's printed none in E206 arm A's 244 committed stdouts). drop_runtime removes every such line
    wherever it fell, pass after pass until none is left, and a JSON string cannot hold a raw newline, so the removal never cuts the host's own
    text; runtime_cards names the cards those lines open (a line naming another card than card 0 is an identity trip); then each
    "SPARSITY {...}" line must parse whole as a JSON object and carry its command's own fields (test, arm, type, values, shire mask, minions),
    else it is NOT read (counted, never a datum). The config read is read the same way (drop_runtime, then the last whole JSON line);
  - the counted launch (E207.md 7): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, and its kernel clock
    (cycles_max / wall_s) in 590-610 MHz.
    python3 -I -B tools/claims-v3/e207/e207_common.py        the self-check (E207-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e207.json")
PTS_F = os.path.join(HERE, "points-e207.json")
MM1_REL = "tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv"
MM1_F = os.path.join(REPO, MM1_REL)
MM1_PIN = "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6"   # E207.md section 0 (MM1-v1's freeze, 25d2e74e)
FMTS = ("fp32", "fp16", "int8")

# ---- the build (build_e207.sh writes it on the box, from the box tree's root)
BUILD_DIR = "build/e207rgm"
HOST = BUILD_DIR + "/host/sparsity_host"
ELF = BUILD_DIR + "/kernel/sparsity.elf"
BUILD_REC = BUILD_DIR + "/BUILD-e207.json"
RGM_SRC = "tools/claims-v3/e136/rgm136"
KERNEL_PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"   # kernel-e207.json kernel_elf_sha256 (E136's build record)
TEXT_PIN = "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763"     # kernel-e207.json kernel_text_sha256
GUARD = "tools/claims-v3/e207/ettelem_guard_e207.sh"
BUILDER = "build_e207.sh"

# ---- the one arm (E207.md 6; plan-e207.json): A, as E206 arm A's form names it
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # read on aifoundry3 Mon 16 Nov 2026 12:02 and 22:19 PST
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0},
}

# ---- every file a point's (or the tie's) --values names, at the sha256 its manifest records (kinds.json > kinds > <fmt> > <name> > sha256;
# blind4.json > tiles[] > sha256 > whole; blind3.json > tiles > <fmt>.<name> > sha256); the self-check reads the three manifests
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/fp16/randn.bin": "2ab30f0f335cbe8aa87fe7a7cf27f66458deb6e34d04d5633a61d3fd96b0c974",
    "tools/claims-v3/kinds/tiles/int8/full.bin": "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9",
    "tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_pythia_embed_qkv.bin": "964235353646465858567706933edea3f8019afd7bc19136315058a575bf005a",
    "tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_qwen_q_down.bin": "67cb6ae7071a69769395b5d6befe16b8dd7d6bba942ef66f83a396d89d21fb80",
    "tools/claims-v3/kinds/blind4/tiles/fp16/fp16.real_pythia_embed_qkv.bin": "ea1bcc457b9e8d8bc0f98941202a2845498961636c77168252e459cf728b6dd6",
    "tools/claims-v3/kinds/blind4/tiles/fp16/fp16.real_qwen_ln_down.bin": "ad684a5b644e7ae0662a278bfcfd4f3467bf77931c3ae1bd3433c56f6e35fc7c",
    "tools/claims-v3/kinds/blind4/tiles/int8/int8.real_pythia_embed_mlpout.bin": "a95314aa8da340de1856aca7663648f8cf1a9670d776388f64c6fb30b1b5ecde",
    "tools/claims-v3/kinds/blind4/tiles/int8/int8.real_qwen_q_down.bin": "9d3841187aa90190483b68f7a86de7cfe3b11c5a110f6e8ebed5b9db29922a10",
    "tools/claims-v3/kinds/blind3/tiles/fp32/a_colconst_b_randn.bin": "d6e283259e0dbe08364d5ba7db9018b41b341ce93850f4d787564f1daec28c2b",
}
TILE_MANIFESTS = ("tools/claims-v3/kinds/kinds.json", "tools/claims-v3/kinds/blind4/blind4.json", "tools/claims-v3/kinds/blind3/blind3.json")

# ---- the session's timing: the registration's numbers (E207.md 6 and 7; plan-e207.json), and the kit's own (marked)
REST_READ_S = 10.0          # E207.md 7: "10 s at rest (p_rest = the median of its last 5 s)"
REST_WINDOW_S = 5.0         # E207.md 7
SMOKE_REST_S = 30.0         # plan-e207.json smoke: "30 s at rest (the session's rest reading; the die gate from it)"
SMOKE_PIDS = ("b01", "b02", "b03")                            # E207.md 3: one checked 2 s process each, in this order
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # "a checked 2 s process"; the budget is E146's, E190's and E206's smoke's (the kit's reading, KIT.md 4)
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E207.md 7: "--seconds 6 --budget 7.5"
TAIL_S = 4.0                # E207.md 7: "a 4 s tail"
GATE_WAIT_S = 300.0         # E207.md 6: "at most 300 s, else that run is NO DATA"
CARD_RULE_S = 60 * 60.0     # E207.md 6: no run starts after 60 card-minutes
CAP_S = 70 * 60.0           # E207.md 6: the session ends at 70 after the run in progress
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz, E207.md 7's "10 Hz samples")
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
CYC_LO, CYC_HI = 0.5, 2.5   # E207.md 7, R0: the smoke's cycles an op within 50-250% of MM1-v1's counter-mean forecast
MHZ_BAND = (590.0, 610.0)   # E207.md 7: the kernel clock a counted launch is in, and S6's band
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # a runtime's line on a host's or a reader's stdout (aifoundry1's form)
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


_PTS = {}


def points():
    if "p" not in _PTS:
        _PTS["p"] = load(PTS_F)
    return _PTS["p"]


def point(pid):
    """A point of points-e207.json by its id, or the tie (points-e207.json > tie: t01, E206's p001), which has host arguments but no forecast."""
    P = points()
    if pid == P["tie"]["id"]:
        return P["tie"]
    for p in P["points"]:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


_MM1 = {}


def mm1():
    """MM1-v1's frozen blind-day forecasts {id: {"cyc_wall", "cyc_mean", "t", "W", "J", "ops"}} from its CSV, which must be at its pin
    (E207.md section 0); else ValueError (the box check's harness read refuses first)."""
    if "m" not in _MM1:
        with open(MM1_F, "rb") as f:
            raw = f.read()
        if hashlib.sha256(raw).hexdigest() != MM1_PIN:
            raise ValueError(f"{MM1_REL} is not MM1-v1's frozen file {MM1_PIN[:12]}")
        rows = {}
        for r in csv.DictReader(raw.decode().splitlines()):
            rows[r["id"]] = {"cyc_wall": float(r["cycles_per_op_wall"]), "cyc_mean": float(r["cycles_per_op_mean"]),
                             "t": float(r["seconds_per_gemm"]), "W": float(r["W_over_idle"]), "J": float(r["J_over_idle_per_gemm"]),
                             "ops": int(r["ops_per_minion_per_gemm"])}
        _MM1["m"] = rows
    return _MM1["m"]


def stops_of(arm, p=None):
    """The arm's stop lines under the watcher's keys, from plan-e207.json ("stop")."""
    if arm not in ARMS:
        raise KeyError(arm)
    s = (p or plan())["stop"]
    return {"board_cap_w": float(s["board_w_above"]), "cap_consecutive": int(s["samples_in_a_row"]), "abs_stop_c": float(s["die_c_at_or_above"])}


def gate_c(arm, rest_die):
    """The die gate a run starts under (E207.md 6): min(60, rest die + 4); None with no rest die (no run starts)."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The registered order: [{"n", "block", "id", "name"}, ...] (points-e207.json > order > sequence); one arm, A."""
    if arm not in ARMS:
        raise KeyError(arm)
    return [dict(x) for x in points()["order"]["sequence"]]


def run_key(r):
    return f"{r['n']:03d}-{r['block']}-{r['id']}"


def host_argv(root, pid, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the point's (or the tie's) registered host_args, --seconds and --budget set to the
    process form, then the kit's --kernel and --stop-file (kernel-e207.json: "the kit adds --kernel, --stop-file and its absolute paths")."""
    a = list(point(pid)["host_args"])
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
    """E207.md 7's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


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
    """The start config the arm's line rests on (plan-e207.json start_config_gate), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (E207.md 6; E206's watcher, line for line): the shires' mean at or above abs_stop_c trips at once; the
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
    p, pts = plan(), points()
    # the arm against the plan (E207.md 6)
    st = stops_of("A", p)
    if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (70.0, 3, 70.0):
        bad.append(f"the stops {st}, not (70, 3, 70)")
    if not p["gate"].startswith("min(60, the session's rest die + 4) C") or p["gate_max_wait_s"] != GATE_WAIT_S or \
            (ARMS["A"]["gate_cap_c"], ARMS["A"]["gate_add_c"]) != (60.0, 4.0):
        bad.append(f"the gate {p['gate']!r} / {p['gate_max_wait_s']}")
    cfg = ARMS["A"]["config"]
    if not p["start_config_gate"].startswith(f"TDP {cfg['tdp_w']} W, {cfg['temp_threshold_c']} C, {cfg['minion_mhz']} MHz"):
        bad.append(f"the start config {p['start_config_gate']!r}")
    if "aifoundry3 card 0" not in p["card"] or "etsoc-shire0.lock" not in p["card"]:
        bad.append(f"the card {p['card']!r}")
    if (p["card_minutes"]["no_new_run_after_min"], p["card_minutes"]["cap_min"]) != (CARD_RULE_S / 60, CAP_S / 60):
        bad.append("the card-time rule and cap")
    seq = sequence("A")
    if len(seq) != p["runs"] or len(seq) != 109 or [r["n"] for r in seq] != list(range(1, len(seq) + 1)) or \
            [(r["n"], r["block"], r["id"]) for r in seq] != [(r["n"], r["block"], r["id"]) for r in p["rows"]]:
        bad.append(f"the sequence is not the plan's rows ({len(seq)} against {p['runs']})")
    ids = {r["id"] for r in seq if r["block"] != "tie"}
    tie = pts["tie"]["id"]
    if len(ids) != p["points"] or ids != {q["id"] for q in pts["points"]} or [r["block"] for r in seq].count("tie") != 3 or \
            seq[0]["id"] != tie or seq[-1]["id"] != tie or [r["id"] for r in seq if r["block"] == "tie"] != [tie] * 3 or tie != "t01":
        bad.append("the points or the ties")
    p1 = [r["id"] for r in seq if r["block"] == "pass1"]
    p2 = [r["id"] for r in seq if r["block"] == "pass2"]
    if p2 != list(reversed(p1)) or p1 != pts["order"]["pass1"] or len(p1) != 53:
        bad.append("pass 2 is not pass 1 reversed, or pass 1 is not the registered list")
    if tuple(pts["smoke"]) != SMOKE_PIDS:
        bad.append(f"the smoke's points {pts['smoke']}")
    if p["run"]["rest_read_s"] != REST_READ_S or p["run"]["tail_s"] != TAIL_S or "--seconds 6 --budget 7.5" not in p["run"]["process"] \
            or "never -k" not in p["run"]["process"]:
        bad.append("the run form")
    if not p["smoke"].startswith("30 s at rest") or not all(x in p["smoke"] for x in SMOKE_PIDS) or "then the stop-path test" not in p["smoke"] \
            or "MM1-v1's counter-mean forecast" not in p["smoke"]:
        bad.append("the smoke's form")
    # MM1-v1's frozen file: at its pin, every point there, the smoke's forecasts readable
    try:
        m = mm1()
        if set(m) != {q["id"] for q in pts["points"]} or any(not (m[x]["cyc_mean"] > 0) for x in SMOKE_PIDS):
            bad.append("MM1-v1's file does not hold the registered points")
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"MM1-v1's file ({type(e).__name__}: {str(e)[:80]})")
    # the argv
    a = host_argv("/T", "b34", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if a[:2] != ["/T/build/e207rgm/host/sparsity_host", "--test"] or arg_of(a, "--values") != "gemmL3x6x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" \
            or arg_of(a, "--shires") != "0x3" or arg_of(a, "--per-shire") != "32" or arg_of(a, "--seconds") != "6" or arg_of(a, "--budget") != "7.5" \
            or arg_of(a, "--kernel") != "/T/build/e207rgm/kernel/sparsity.elf" or arg_of(a, "--stop-file") != "/T/STOP" or "-k" in a:
        bad.append(f"the argv {a}")
    s = host_argv("/T", "b03", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp16":
        bad.append(f"the smoke's argv {s}")
    if expect_of(a) != {"arm": "gemmL3x6x4", "type": "fp32", "values": "gemmL3x6x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
                        "shire_mask": "0x3", "minions": 64}:
        bad.append(f"expect_of {expect_of(a)}")
    t = host_argv("/T", "t01", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if arg_of(t, "--values") != "gemmL2x4x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" or arg_of(t, "--shires") != "0xffffffff":
        bad.append(f"the tie's argv {t}")
    for q in pts["points"] + [pts["tie"]]:
        e = expect_of(host_argv("/T", q["id"], 6, 7.5, "/S"))
        if (int(e["shire_mask"], 16), e["minions"], e["arm"], e["type"]) != (int(q["shire_mask"], 16), q["minions"], q["arm"], q["format"]):
            bad.append(f"{q['id']}: expect_of {e} against the point")
            break
    if expect_of(host_argv("/T", "b37", 6, 7.5, "/S"))["shire_mask"] != "0xf0f0f0f":
        bad.append("b37's mask in the host's own spelling")
    # the tiles: every file a point names, at its manifest's sha256
    named = set()
    for q in pts["points"] + [pts["tie"]]:
        named |= set(q["values"].split(":", 2)[2].split(","))
    if named != set(TILES):
        bad.append(f"TILES is not the points' files ({len(named)} named, {len(TILES)} pinned)")
    try:
        kj = load(os.path.join(REPO, TILE_MANIFESTS[0]))["kinds"]
        b4 = {os.path.basename(x["file"]): x["sha256"]["whole"] for x in load(os.path.join(REPO, TILE_MANIFESTS[1]))["tiles"]}
        b3 = load(os.path.join(REPO, TILE_MANIFESTS[2]))["tiles"]
        for f, h in TILES.items():
            fmt, base = f.split("/")[-2], os.path.basename(f)
            if "/blind4/" in f:
                m_ = b4[base]
            elif "/blind3/" in f:
                m_ = b3[f"{fmt}.{base[:-4]}"]["sha256"]
            else:
                m_ = kj[fmt][base[:-4]]["sha256"]
            if m_ != h:
                bad.append(f"{f}: pinned {h[:12]}, its manifest {m_[:12]}")
    except (OSError, KeyError, ValueError, TypeError) as e:
        bad.append(f"the tile manifests could not be read ({type(e).__name__})")
    # the stop lines: the watcher's semantics, the latch reading (E206's cases, arm A)
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
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
        bad.append("the latch after a drop (a statistics reset by another) rising past the line")
    st = Stops(70, 3, 70)       # a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 73}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 73}) != [] or \
            st.feed({"t_ms": 4, "board_w": 73}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(70, 3, 70)       # 95 W on every other sample, no reading between, trips at the third reading
    r = [st.feed({"t_ms": k, "board_w": 95.0} if k % 2 else {"t_ms": k}) for k in range(1, 8)]
    if r != [[], [], [], [], ["stop"], [], []] or "95.0 W above 70 W" not in (st.stop or ""):
        bad.append(f"95 W on every other sample with no reading between {r}")
    st = Stops(70, 3, 70)       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 69.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
        bad.append("a reading under the line between over-line readings did not break the row")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 300e6}
    if not counted(L) or counted(dict(L, cycles_max=400e6)) or counted(dict(L, launch=-1)) or counted(dict(L, launch=-3)) or \
            counted(dict(L, ok=False)) or counted(dict(L, wall_s=0.05, cycles_max=30e6)) or counted(dict(L, passes=0)) or counted(dict(L, test="check")):
        bad.append("the counted launch")
    # the records: runtime lines inside a record, a cut record, a record of another command
    rec = {"test": "fma", "arm": "gemmL3x6x4", "gen": "randn", "type": "fp32", "pattern": "none",
           "values": "gemmL3x6x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin", "b_stream": 0, "minions": 64, "shire_mask": "0x3",
           "iters": 6144, "passes": 1, "launch": 0, "cycles_max": 300000000, "cycles_per_op": 980.0, "wall_s": 0.5, "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in range(0, len(line) + 1, 7):
        f_, c_, inf = host_records(line[:k] + "Opening device 1\n" + line[k:] + "\n", a)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 1"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    for k in range(0, len(line) + 1, 7):      # a runtime line printed INSIDE another runtime line, the pair inside a record
        for j in (0, 3, 9, len("Opening device 1")):
            outer = "Opening device 1\n"
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            f_, c_, inf = host_records(line[:k] + pair + line[k:] + "\n", a)
            if f_ != [rec] or sorted(inf["runtime_lines"]) != ["Opening device 0", "Opening device 1"] or inf["unparsed"]:
                bad.append(f"two nested runtime lines (the inner at {j}) at offset {k} of a record")
                break
        else:
            continue
        break
    if runtime_cards(["Opening device 1", "Opening device 0", "x"]) != ["1", "0"] or runtime_cards([]) != []:
        bad.append("runtime_cards")
    f_, c_, inf = host_records(line[:40] + "\n", a)
    if f_ or inf["unparsed"] != 1:
        bad.append("a cut record was read")
    f_, c_, inf = host_records(line.replace('"0x3"', '"0xf"') + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another mask was read")
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
    print("E207-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
