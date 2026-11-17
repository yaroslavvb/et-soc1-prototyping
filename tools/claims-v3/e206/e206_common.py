#!/usr/bin/env python3
"""E206's kit (Q198, lane kit-e206, Mon 16 Nov 2026, before any E206 datum): what the box runner, the doubles, the reducer, the collector
and the desk tests share. E190's kit form (tools/claims-v3/e190/e190_common.py and its note 1's e190_note1.py; E206.md section 6 names
E190's watcher, its gates and its card-1 form) for E206's two arms. Python's own modules only: it runs on aifoundry3 and aifoundry1 under
the system python3 (3.12.3 on both by their reads) and at the desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e206.json (every point's host arguments and both arms' order),
plan-e206.json (the arms' cards, clocks, configs, lines, stops, gates and card-time rules) and forecast-e206.json (F1's cycles an op a
smoke process is read against). It adds:
  - THE TWO ARMS' IDENTITIES (E206.md 6): arm A aifoundry3 card 0 (its one card: /dev/et0_*, the lock etsoc-shire0.lock, ET_DEVICES unset,
    the box tree ~/aifoundry, the box's reader build/ettelem/ettelem at the sha256 read there on Mon 16 Nov 2026 12:02 PST); arm B aifoundry1
    card 1 (ET_DEVICES=1 on every device process, the lock etsoc-shire1.lock, the box tree ~/nekko, the lab's card-1 reader build/ettelem/
    ettelem at E157's, E164's, E172's, E190's and E198's pin); each arm's start config gate (A: TDP 0 W / 65 C / 600 MHz; B: 65 W / 65 C /
    600 MHz) and its clock band (590-610 MHz, both arms);
  - THE BUILD'S PINS (kernel-e206.json): rgm136 from tools/claims-v3/e136/rgm136 into build/e206rgm on each box; THE KERNEL GATE (E191's
    kit fix, check_e206.py): the .text always the registered 61315bf6..., and the whole ELF the registered aace138c... or else its loadable
    identity the pinned one (aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0" where aifoundry1's and this desk's print "() 15.1.0", and
    the string lands in a section the card never loads); the host read by its behaviour, never by its bytes;
  - THE TILES: every file a point's --values names (20), at the sha256 kinds.json and real2.json record;
  - THE STOP LINES, E190's watcher (E206.md 6: "the shires' mean or the hottest shire sensor (E190's watcher)"), with THE LATCH READING
    stated before any datum (KIT.md section 4, item 1; registered by E206.md's amendment A1, item 1, before the land): the telemetry's
    minshire[2] is a latch held since the card's last statistics reset
    (docs/findings/14-card-behaviour.md, its dated note of Tue 3 Nov 2026; E190's kit note 1, item 4.1), not the hottest sensor now: on
    aifoundry3 card 0 it read 87 C in every committed sample of E189, E195, E196 and E197, on card 1 66 C in E198's and E199's. Read as a
    level it would trip arm A's 70 C line at its first sample. So the die line trips on the shires' mean (minshire[0]) at or above the line,
    or on the latch only when it has RISEN during the session above the lowest value it read since the session's first sample and reads at
    or above the line (a new maximum since the session started is the one live reading of the hottest sensor the telemetry carries). The
    board line: strictly above the line on 3 samples in a row that carry a board reading, a sample with no board reading neither counting nor
    breaking the row (fix-e206, before any datum, for the verifier's finding 7: the first version restarted the count at such a sample, so a
    reading over the line on every other sample, with none between, never tripped it; E206.md A1, item 2);
  - THE GATES: the die gate (A min(60, rest die + 4) C, B min(63, rest die + 3) C; at most 300 s, else that run is NO DATA), the rest die
    the median of the shires' mean over the smoke's 30 s rest; the card-time rule (no run starts once the card time passes 112 minutes;
    the session ends at 120 after the run in progress) and the window's last end;
  - THE ORDER: each arm's sequence (points-e206.json > order > <arm> > sequence: tie, pass 1, tie, pass 2, tie), each run one host process
    `timeout 10 <host> <the point's host_args> --kernel <ELF> --stop-file <STOP>`, never `timeout -k`;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E191's kit note 2): rgm136's host
    prints its SPARSITY records on stdout and has no result file of its own; aifoundry1's runtime prints "Opening device 1" on the same
    stdout (E190 arm B's committed proc.out files: 87 such lines, each at a line's start). drop_runtime removes every such runtime line
    wherever it fell, pass after pass until none is left (a runtime line printed inside another one comes out on the second pass: fix-e206,
    the verifier's finding 9), and a JSON string cannot hold a raw newline, so the removal never cuts the host's own text; runtime_cards
    names the cards those lines open (the runner treats a line naming another card than the arm's as an identity trip: fix-e206, the
    verifier's finding 10); then each "SPARSITY {...}"
    line must parse whole as a JSON object and carry its command's own fields (test, arm, type, values, shire mask, minions), else it is
    NOT read (counted, never a datum). The config read is read the same way (drop_runtime, then the last whole JSON line);
  - the counted launch (E206.md 7): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, and its kernel clock
    (cycles_max / wall_s) in 590-610 MHz.
    python3 -I -B tools/claims-v3/e206/e206_common.py        the self-check (E206-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e206.json")
FC_F = os.path.join(HERE, "forecast-e206.json")
PTS_F = os.path.join(HERE, "points-e206.json")
FMTS = ("fp32", "fp16", "int8")

# ---- the build (build_e206.sh writes it on each box, from the box tree's root)
BUILD_DIR = "build/e206rgm"
HOST = BUILD_DIR + "/host/sparsity_host"
ELF = BUILD_DIR + "/kernel/sparsity.elf"
BUILD_REC = BUILD_DIR + "/BUILD-e206.json"
RGM_SRC = "tools/claims-v3/e136/rgm136"
KERNEL_PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"   # kernel-e206.json kernel_elf_sha256 (E136's build record)
TEXT_PIN = "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763"     # kernel-e206.json kernel_text_sha256
GUARD = "tools/claims-v3/e206/ettelem_guard_e206.sh"
BUILDER = "build_e206.sh"
ETDEV_YES = "the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"

# ---- the two arms (E206.md 6; plan-e206.json arms)
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # read on aifoundry3, Mon 16 Nov 2026 12:02 PST
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0},
    "B": {"box": "aifoundry1", "card": "aifoundry1 card 1", "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "tree": "nekko", "data_dir": "aifoundry1-c1",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",   # E157's, E164's, E172's, E190's, E198's pin
          "config": {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 63.0, "gate_add_c": 3.0},
}

# ---- every file a point's --values names, at the sha256 its manifest records (kinds.json > kinds > <fmt> > <name> > sha256; real2.json >
# tiles > <fmt> > <name> > sha256); the self-check reads both manifests
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/fp16/randn.bin": "2ab30f0f335cbe8aa87fe7a7cf27f66458deb6e34d04d5633a61d3fd96b0c974",
    "tools/claims-v3/kinds/tiles/int8/full.bin": "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9",
    "tools/claims-v3/kinds/tiles/fp32/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/fp16/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/int8/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/fp32/sparse50.bin": "43ababfe5f3fed0963600a119a5ec805b433636594616042cac4fbab1fd69530",
    "tools/claims-v3/kinds/tiles/int8/sparse50.bin": "e235ed609c58b069f36412099d8d2fa890cae07bf5599f77b65904b6802d38a8",
    "tools/claims-v3/kinds/real2/tiles/fp32/gpt2_l9_attn_qk.bin": "a7a67f4aa8d9835e44ccacca0c9c49345c4fa15e527196651ff5097e44e87d2e",
    "tools/claims-v3/kinds/real2/tiles/fp32/gpt2_l3_mlp_down.bin": "08bef955e7e835a9d934a07b60c5ad1c50b77e2dae69adf157b8875aa7bc9cb1",
    "tools/claims-v3/kinds/real2/tiles/fp32/bert_l6_up.bin": "312c34d32261d6519992fb1fff797a31bee0e92c72f95f2f2913bea629783b91",
    "tools/claims-v3/kinds/real2/tiles/fp32/vit_l5_down.bin": "4f77d357a4d97a7f6e2326e0314dfd0e9343ea13be188489609037d4707105ce",
    "tools/claims-v3/kinds/real2/tiles/fp16/gpt2_l9_attn_qk.bin": "6cfef807543dba6c3aa26caf37a0a6b72d3fd309bd579d7330742d0c7e4b7b86",
    "tools/claims-v3/kinds/real2/tiles/fp16/bert_l6_up.bin": "a8c708293b5c8cd369ccefd8c4374f1a2aee907d971b7f6494731dd674a6aac0",
    "tools/claims-v3/kinds/real2/tiles/fp16/vit_l5_down.bin": "64985e6c2bd5457c70d050daa0bdcde6a3c1e8f5a48ad9f958c15801f8ea617b",
    "tools/claims-v3/kinds/real2/tiles/fp16/gpt2_l6_mlp_down_fp16fwd.bin": "8d75f3fdee196fe9d4e099927488c1b4d421d8a7275a8926bb788b02ab9a7f87",
    "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p999.bin": "fda41dd9f32e7d439a9d765cfd5cdf223684b45d05178ce06efef4337be9e799",
    "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p9999.bin": "deefd9cab63f5be939c3bb0093205cd977dcc398dc77941d8619339fcbd608f6",
    "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_per_token.bin": "9f7daf2842262797dc1c9ed41dd882a324c7645eb41377e143a6c02990e60da7",
    "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l11_down_p999.bin": "eea7ce0a6f183100f9fd4781e34e368b6e795b21e4bb601d32075d8c64e3224e",
}

# ---- the session's timing: the registration's numbers (E206.md 6 and 7; plan-e206.json run and rules), and the kit's own (marked)
REST_READ_S = 10.0          # E206.md 7: "10 s at rest (p_rest = the median of its last 5 s)"
REST_WINDOW_S = 5.0         # E206.md 7
SMOKE_REST_S = 30.0         # E206.md 7: the smoke's 30 s at rest (the session's rest reading: the die gates are formed from it)
SMOKE_PIDS = ("p001", "p046", "p021")                         # E206.md 7: one checked 2 s process each, in this order
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # "a 2 s process"; the budget is E146's and E190's smoke's (the kit's reading, KIT.md 4)
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E206.md 7: "--seconds 6 --budget 7.5"
TAIL_S = 4.0                # E206.md 7: "a 4 s tail"
GATE_WAIT_S = 300.0         # E206.md 6: "at most 300 s, else that run is NO DATA"
CARD_RULE_S = 112 * 60.0    # E206.md 6: no run starts after 112 card-minutes
CAP_S = 120 * 60.0          # E206.md 6: the session ends at 120 after the run in progress
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz, E206.md 7's "10 Hz samples")
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
CYC_LO, CYC_HI = 0.5, 2.5   # E206.md 7, R0: the smoke's cycles an op within 50-250% of F1's point
MHZ_BAND = (590.0, 610.0)   # E206.md 7: the kernel clock a counted launch is in, and S6's band
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # aifoundry1's runtime, on a host's or a reader's stdout
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (fix-e206: another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


def forecast():
    return load(FC_F)


_PTS = {}


def points():
    if "p" not in _PTS:
        _PTS["p"] = load(PTS_F)
    return _PTS["p"]


def point(pid):
    for p in points()["points"]:
        if p["id"] == pid:
            return p
    raise KeyError(pid)


def stops_of(arm, p=None):
    """The arm's stop lines under the watcher's keys, from plan-e206.json (arms > <arm> > stop)."""
    s = (p or plan())["arms"][arm]["stop"]
    return {"board_cap_w": float(s["board_w_above"]), "cap_consecutive": int(s["samples_in_a_row"]), "abs_stop_c": float(s["die_c_at_or_above"])}


def gate_c(arm, rest_die):
    """The die gate a run starts under (E206.md 6): A min(60, rest die + 4), B min(63, rest die + 3); None with no rest die (no run starts)."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The arm's registered order: [{"n", "block", "id", "name"}, ...] (points-e206.json > order > <arm> > sequence)."""
    return [dict(x) for x in points()["order"][arm]["sequence"]]


def run_key(r):
    return f"{r['n']:03d}-{r['block']}-{r['id']}"


def host_argv(root, pid, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the point's registered host_args, --seconds and --budget set to the process
    form, then the kit's --kernel and --stop-file (kernel-e206.json: "the kit adds --kernel, --stop-file and its absolute paths")."""
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
    """E206.md 7's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


# ---- the host's records and the config read, from a source no runtime print can split
def drop_runtime(text):
    """(the text without runtime lines, [the runtime lines dropped, in the order removed]): every RUNTIME_LINE removed wherever it fell,
    pass after pass until none is left (fix-e206, the verifier's finding 9: a runtime line printed INSIDE another runtime line leaves a whole
    one behind after the first pass; the second pass removes it). Each pass removes at least one line, so the loop ends."""
    text = text or ""
    found = []
    while True:
        hits = [m.group(0)[:-1] for m in RUNTIME_LINE.finditer(text)]
        if not hits:
            return text, found
        found += hits
        text = RUNTIME_LINE.sub("", text)


def runtime_cards(lines):
    """The cards the runtime lines open, as strings in order ("Opening device 1" -> "1"); fix-e206, the verifier's finding 10: the runner
    treats a line naming another card than the arm's (IDENT[arm]["card"]) as an identity trip, on a host's, a config read's or the sampler's
    stdout."""
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
    """The start config each arm's line rests on (plan-e206.json start_config_gate), read as found, nothing set."""
    if not j:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (E206.md 6; E190's watcher; THE LATCH READING in the module docstring): the shires' mean at or above
    abs_stop_c trips at once; the latch (minshire[2]) trips only when it has risen above the lowest value it read since the first sample and
    reads at or above abs_stop_c; a board reading above board_cap_w on cap_consecutive samples in a row trips (a reading at or under the line
    starts the count again; a sample with no board reading neither counts nor breaks the row: fix-e206, E206.md A1 item 2). The first trip is
    kept; trip_file, if given, is touched at the trip (the real
    lines' file is the hosts' --stop-file, so a running host ends at its next launch boundary, about 0.5 s; nothing is ever killed)."""

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
        if bw is None:              # no board reading: neither counted nor breaking the row (fix-e206; the verifier's finding 7)
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
    p, fc, pts = plan(), forecast(), points()
    # the arms against the plan
    for arm, want in (("A", (70.0, 3, 70.0)), ("B", (72.0, 3, 80.0))):
        st = stops_of(arm, p)
        if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != want:
            bad.append(f"arm {arm}'s stops {st}, not {want}")
        if (fc["constants"]["stop"][arm]["board_w_above"], fc["constants"]["stop"][arm]["die_c_at_or_above"]) != (want[0], want[2]):
            bad.append(f"arm {arm}'s stops differ between the plan and the forecast")
        pa = p["arms"][arm]
        g = f"min({ARMS[arm]['gate_cap_c']:g}, rest die + {ARMS[arm]['gate_add_c']:g}) C"
        if not pa["gate"].startswith(g) or pa["gate_max_wait_s"] != GATE_WAIT_S:
            bad.append(f"arm {arm}'s gate {pa['gate']!r} / {pa['gate_max_wait_s']} (want {g!r}, {GATE_WAIT_S:g})")
        cfg = ARMS[arm]["config"]
        if not pa["start_config_gate"].startswith(f"TDP {cfg['tdp_w']} W, {cfg['temp_threshold_c']} C, {cfg['minion_mhz']} MHz"):
            bad.append(f"arm {arm}'s start config {pa['start_config_gate']!r}")
        if ARMS[arm]["box"] not in pa["card"] and not (arm == "A" and "aifoundry3 card 0" in pa["card"]):
            bad.append(f"arm {arm}'s card {pa['card']!r}")
        if (pa["card_minutes"]["no_new_run_after_min"], pa["card_minutes"]["cap_min"]) != (CARD_RULE_S / 60, CAP_S / 60):
            bad.append(f"arm {arm}'s card-time rule and cap")
        seq = sequence(arm)
        if len(seq) != pa["runs"] or [r["n"] for r in seq] != list(range(1, len(seq) + 1)) or \
                [(r["n"], r["block"], r["id"]) for r in seq] != [(r["n"], r["block"], r["id"]) for r in pa["rows"]]:
            bad.append(f"arm {arm}'s sequence is not the plan's rows ({len(seq)} against {pa['runs']})")
        ids = {r["id"] for r in seq if r["block"] != "tie"}
        if len(ids) != pa["points"] or [r["block"] for r in seq].count("tie") != 3 or seq[0]["id"] != "p001" or seq[-1]["id"] != "p001":
            bad.append(f"arm {arm}'s points or ties")
        p1 = [r["id"] for r in seq if r["block"] == "pass1"]
        p2 = [r["id"] for r in seq if r["block"] == "pass2"]
        if p2 != list(reversed(p1)):
            bad.append(f"arm {arm}'s pass 2 is not pass 1 reversed")
        if any(not point(i)["on_arm"][arm] for i in ids):
            bad.append(f"arm {arm} runs a point not on it")
    if p["run"]["rest_read_s"] != REST_READ_S or p["run"]["tail_s"] != TAIL_S or "--seconds 6 --budget 7.5" not in p["run"]["process"] \
            or "never -k" not in p["run"]["process"]:
        bad.append("the run form")
    if not p["smoke"].startswith("30 s at rest") or not all(x in p["smoke"] for x in SMOKE_PIDS) or "then the stop-path test" not in p["smoke"]:
        bad.append("the smoke's form")
    # the argv
    a = host_argv("/T", "p094", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if a[:2] != ["/T/build/e206rgm/host/sparsity_host", "--test"] or arg_of(a, "--values") != "gemmL4x8x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" \
            or arg_of(a, "--shires") != "0x1" or arg_of(a, "--per-shire") != "32" or arg_of(a, "--seconds") != "6" or arg_of(a, "--budget") != "7.5" \
            or arg_of(a, "--kernel") != "/T/build/e206rgm/kernel/sparsity.elf" or arg_of(a, "--stop-file") != "/T/STOP" or "-k" in a:
        bad.append(f"the argv {a}")
    s = host_argv("/T", "p046", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp16":
        bad.append(f"the smoke's argv {s}")
    if expect_of(a) != {"arm": "gemmL4x8x4", "type": "fp32", "values": "gemmL4x8x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
                        "shire_mask": "0x1", "minions": 32}:
        bad.append(f"expect_of {expect_of(a)}")
    for q in pts["points"]:
        e = expect_of(host_argv("/T", q["id"], 6, 7.5, "/S"))
        if (e["shire_mask"], e["minions"], e["arm"], e["type"]) != (q["shire_mask"], q["minions"], q["arm"], q["format"]):
            bad.append(f"{q['id']}: expect_of {e} against the point")
            break
    # the tiles: every file a point names, at its manifest's sha256
    named = set()
    for q in pts["points"]:
        named |= set(q["values"].split(":", 2)[2].split(","))
    if named != set(TILES):
        bad.append(f"TILES is not the points' files ({len(named)} named, {len(TILES)} pinned)")
    try:
        kj = load(os.path.join(REPO, "tools/claims-v3/kinds/kinds.json"))["kinds"]
        rj = load(os.path.join(REPO, "tools/claims-v3/kinds/real2/real2.json"))["tiles"]
        for f, h in TILES.items():
            fmt, name = f.split("/")[-2], os.path.basename(f)[:-4]
            m = (rj if "/real2/" in f else kj)[fmt][name]["sha256"]
            if m != h:
                bad.append(f"{f}: pinned {h[:12]}, its manifest {m[:12]}")
    except (OSError, KeyError, ValueError) as e:
        bad.append(f"the tile manifests could not be read ({type(e).__name__})")
    # the stop lines: the watcher's semantics, the latch reading
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
    st = Stops(70, 3, 70)
    r = [st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(70.0)), st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(71))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or ""):
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(70, 3, 70)
    if [st.feed(smp(die=69, high=87)) for _ in range(5)] != [[]] * 5 or st.feed(smp(die=70, high=87)) != ["stop"] or "shires' mean" not in st.stop:
        bad.append("arm A's die line: the 87 C latch must not trip it, the mean at 70 C must")
    st = Stops(70, 3, 70)
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=88)) != ["stop"] or "latch rose" not in st.stop:
        bad.append("arm A's latch rising past its session value")
    st = Stops(72, 3, 80)
    if st.feed(smp(die=60, high=66)) != [] or st.feed(smp(die=60, high=79)) != [] or st.feed(smp(die=60, high=80)) != ["stop"]:
        bad.append("arm B's latch rising to 80 C")
    st = Stops(72, 3, 80)
    if st.feed(smp(die=60, high=66)) != [] or st.feed(smp(die=60, high=50)) != [] or st.feed(smp(die=60, high=81)) != ["stop"]:
        bad.append("the latch after a drop (a statistics reset by another) rising past the line")
    st = Stops(72, 3, 80)       # fix-e206: a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 73}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 73}) != [] or \
            st.feed({"t_ms": 4, "board_w": 73}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(70, 3, 70)       # the verifier's case: 95 W on every other sample, no reading between, trips at the third reading
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
    rec = {"test": "fma", "arm": "gemmL4x8x4", "gen": "randn", "type": "fp32", "pattern": "none",
           "values": "gemmL4x8x4:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin", "b_stream": 0, "minions": 32, "shire_mask": "0x1",
           "iters": 8192, "passes": 1, "launch": 0, "cycles_max": 300000000, "cycles_per_op": 1300.0, "wall_s": 0.5, "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in range(0, len(line) + 1, 7):
        f_, c_, inf = host_records(line[:k] + "Opening device 1\n" + line[k:] + "\n", a)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 1"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    # fix-e206 (the verifier's finding 9): a runtime line printed INSIDE another runtime line, the pair inside a record, at every 7th offset
    for k in range(0, len(line) + 1, 7):
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
    f_, c_, inf = host_records(line.replace('"0x1"', '"0x3"') + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another mask was read")
    if config_json("Opening device 1\n" + '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":0,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("B", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) or not config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}):
        bad.append("the start config")
    if gate_c("A", 50.0) != 54.0 or gate_c("A", 58.0) != 60.0 or gate_c("B", 57.0) != 60.0 or gate_c("B", 61.0) != 63.0 or gate_c("A", None) is not None:
        bad.append("the die gates")
    if abs(RUN_MAX_S - 28.0) > 1e-9:
        bad.append("RUN_MAX_S")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E206-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
