#!/usr/bin/env python3
"""E190's kit (Q169, Fri 13 Nov 2026, before any E190 datum): what the box runner, the doubles, the reducer, the collector and the desk
tests share. Python's own modules only (it runs on aifoundry2 and aifoundry1 under the system python3, and at the desk under
/usr/bin/python3 -I -B).

It reads the registration's plan-e190.json (the order, the runs a cell, the process form, the gates, the stops, the card-time rule and cap)
and forecast-e190.json (each format's --values, the stop lines, the speed points R0's tie reads) and never changes them. It adds:
  - THE TWO ARMS' IDENTITIES: the box, the card's lock, ET_DEVICES, the box tree (k6's rb_tree), the telemetry reader each arm's guard runs
    and its pin, the start config each arm's line rests on, the clock band a launch is counted in (E190.md section 6);
  - THE BUILD'S PINS: rgm136 built from tools/claims-v3/e136/rgm136 (the registration's subtree 30da3ec3...) into build/e190rgm on each box;
    the kernel ELF at the registration's pin aace138c... (E136's build record, reproduced on aifoundry2 by reg-e190 and on aifoundry1 by
    this kit's desk build, Fri 13 Nov 2026 12:36 PST: byte-identical); the host read from its behaviour (build_e190.sh), never by its bytes,
    which carry its build path;
  - THE STOP LINES, under the keys run_hpl.py's watcher reads (E190.md section 8; E146's finding): board_cap_w on cap_consecutive samples
    in a row (board strictly above it), abs_stop_c on one sample of the shires' mean or the hottest shire sensor (at or above it);
  - THE GATES (E190.md section 7): arm A a burst from at or below 55 C, a sustained run from at or below 57 C; arm B from at or below
    min(63, the session's rest die + 3) and min(64, rest + 4); at most 300 s, else that run is skipped (NO DATA);
  - the sequence of the registered order with each run's cell and repeat, and each run's planned seconds;
  - the counted launch (E190.md section 6): an fma launch with launch >= 0, ok, wall_s >= 0.1 s and a kernel clock (cycles_max / wall_s)
    at or above 790 MHz (arm A) or in 590-610 MHz (arm B).
    python3 -I -B tools/claims-v3/e190/e190_common.py        the self-check (E190-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e190.json")
FC_F = os.path.join(HERE, "forecast-e190.json")
FMTS = ("fp32", "fp16", "int8")
KINDS = ("burst", "sus")

# ---- the build (build_e190.sh writes it on each box, from the box tree's root)
BUILD_DIR = "build/e190rgm"
HOST = BUILD_DIR + "/host/sparsity_host"
ELF = BUILD_DIR + "/kernel/sparsity.elf"
BUILD_REC = BUILD_DIR + "/BUILD-e190.json"
RGM_SRC = "tools/claims-v3/e136/rgm136"
RGM_SUBTREE = "30da3ec36d2085b9e8c441387fb945029d3caaf6"        # the registration's sim check names it (desk/sim-check-e190.txt)
KERNEL_PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"   # E136's build record; E190.md section 2
GUARD = "tools/claims-v3/e190/ettelem_guard_e190.sh"
TILES = {"fp32": ("tools/claims-v3/kinds/tiles/fp32/randn.bin", "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa"),
         "fp16": ("tools/claims-v3/kinds/tiles/fp16/randn.bin", "2ab30f0f335cbe8aa87fe7a7cf27f66458deb6e34d04d5633a61d3fd96b0c974"),
         "int8": ("tools/claims-v3/kinds/tiles/int8/full.bin", "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9")}

# ---- the two arms (E190.md section 3; plan-e190.json arms)
ARMS = {
    "A": {"box": "aifoundry2", "card": "aifoundry2 card 0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "claude/et-soc1-prototyping", "data_dir": "aifoundry2",
          "ettelem": "build/ettelem-hpl/ettelem",
          "ettelem_sha256": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",   # E136's, E146's and E169's sampler
          "config": {"tdp_w": 65, "temp_threshold_c": 65}, "clock_mhz": 800, "count_mhz": (790.0, None)},
    "B": {"box": "aifoundry1", "card": "aifoundry1 card 1", "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "tree": "nekko", "data_dir": "aifoundry1-c1",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",   # E157's, E164's and E172's pin on card 1
          "config": {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0)},
}

# ---- the session's timing: the registration's numbers, and the kit's own (marked)
REST_READ_S = 10.0          # E190.md 7: "Before each run, 10 s at rest are read"
SMOKE_REST_S = 30.0         # E190.md 7: the smoke's 30 s at rest (the session's rest reading)
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # E190.md 7: "one 2 s process per format"; the budget is E146's smoke's (the kit's reading)
TAIL_S = 4.0                # the kit's: 4 s read after a run's last process (E136's and E146's tail_s); the reducer does not use it
GATE_WAIT_S = 300.0         # E190.md 7
CARD_RULE_S = 35 * 60.0     # E190.md 7: no run starts once the arm's card time passes 35 minutes
CAP_S = 40 * 60.0           # E190.md 7: at 40 minutes the session ends
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
EVERY_MS = 100              # the sampler's rate (10 Hz; E190.md 6's "10 Hz samples")
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process
SUS_WINDOW_S = 40.0         # E190.md 6: a sustained run is read over its last 40 s
REST_WINDOW_S = 5.0         # E190.md 6: p_rest over the last 5 s of rest before the run's first process
CYC_LO, CYC_HI = 0.5, 2.5   # E190.md 6, R0: the smoke's cycles an op within 50-250% of the point


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


def forecast():
    return load(FC_F)


def stops_of(arm, fc=None):
    """The arm's stop lines under the watcher's keys, from the frozen forecast's constants (stop_A / stop_B)."""
    fc = fc or forecast()
    s = fc["constants"]["stop_" + arm]
    return {"board_cap_w": float(s["board_w"]), "cap_consecutive": int(s["board_samples"]), "abs_stop_c": float(s["die_c"])}


def values(fmt, fc=None):
    return (fc or forecast())["gemm"][fmt]["values"]


def proc_form(kind, p=None):
    """(seconds, budget, processes) of a run of this kind, as plan-e190.json's process block writes them; the smoke's is the kit's."""
    p = p or plan()
    pr = p["process"]
    if kind == "smoke":
        return SMOKE_SECONDS, SMOKE_BUDGET, 1
    if kind == "burst":
        return float(pr["seconds_burst"]), float(pr["budget_s"]), 1
    return float(pr["seconds_sus_proc"]), float(pr["budget_s"]), int(pr["sus_processes"])


def host_argv(root, fmt, seconds, budget, stop_file, fc=None):
    """One process's command line (without `timeout 10`), E136's form: absolute host and kernel, --values relative to the tree's root."""
    return [os.path.join(root, HOST), "--test", "fma", "--type", fmt, "--pattern", "none", "--values", values(fmt, fc),
            "--shires", "0xffffffff", "--per-shire", "32", "--seconds", f"{seconds:g}", "--budget", f"{budget:g}", "--seed", "1",
            "--kernel", os.path.join(root, ELF), "--stop-file", stop_file]


def sequence(p=None):
    """The registered order after the smoke: (i, block, kind, format, repeat) with i the order's index (1-18)."""
    p = p or plan()
    seen, out = {}, []
    for i, (blk, kind, fmt) in enumerate(p["order"]):
        if blk == "SMOKE":
            continue
        k = f"{fmt}.{kind}"
        seen[k] = seen.get(k, 0) + 1
        out.append((i, blk, kind, fmt, seen[k]))
    return out


def run_plan_s(kind, fmt, p=None):
    """A run's planned seconds once its gate is passed: the rest read, its processes at the plan's estimate, the tail (the kit's)."""
    p = p or plan()
    est = float(p["process"]["est_s"][fmt])
    _, _, n = proc_form(kind, p)
    return REST_READ_S + n * (est + 0.3) + TAIL_S


def gate_c(arm, kind, rest_die):
    """The die gate a run starts under (E190.md section 7); None when arm B has no rest die (no gate can be formed: no run starts)."""
    if arm == "A":
        return 55.0 if kind == "burst" else 57.0
    if rest_die is None:
        return None
    return min(63.0, rest_die + 3.0) if kind == "burst" else min(64.0, rest_die + 4.0)


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


def kclock(L):
    """A launch's kernel clock in MHz: cycles_max / wall_s (E119's clock_x)."""
    w = L.get("wall_s") or 0
    return (L.get("cycles_max") or 0) / w / 1e6 if w > 0 else None


def counted(L, arm):
    """E190.md 6's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in the arm's band."""
    if L.get("test") != "fma" or (L.get("launch") or 0) < 0 or not L.get("ok") or (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    lo, hi = ARMS[arm]["count_mhz"]
    return f is not None and f >= lo and (hi is None or f <= hi)


def parse_sparsity(text):
    """The host's SPARSITY lines, as dicts."""
    out = []
    for ln in text.splitlines():
        if ln.startswith("SPARSITY "):
            try:
                out.append(json.loads(ln[9:]))
            except ValueError:
                pass
    return out


def last_json(text):
    for ln in reversed(text.splitlines()):
        if ln.startswith("{"):
            try:
                return json.loads(ln)
            except ValueError:
                return {}
    return {}


def config_ok(arm, j):
    """The start config each arm's line rests on: 65 W and 65 C (both arms); arm B also its 600 MHz (its 70 W line is reckoned at it)."""
    if not j:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples, run_hpl.py's Watcher in one function (E190.md sections 3 and 8): a sample whose shires' mean or
    hottest shire sensor reads at or above abs_stop_c trips at once; a board reading above board_cap_w on cap_consecutive samples in a row
    trips (a sample with no board reading, or one at or under the line, starts the count again). The first trip is kept; trip_file, if
    given, is touched at the trip (the real lines' file is the hosts' --stop-file, so a running host ends at its next launch boundary)."""

    def __init__(self, board_cap_w, cap_consecutive, abs_stop_c, trip_file=None):
        self.board_cap_w, self.need, self.abs_stop_c = float(board_cap_w), int(cap_consecutive), float(abs_stop_c)
        self.trip_file = trip_file
        self.over = 0
        self.stop = None
        self.t_trip = None

    def feed(self, s):
        if self.stop:
            return []
        bw = s.get("board_w")
        ms = (s.get("temp_c") or {}).get("minshire") or [None, None, None]
        die, high = ms[0], (ms[2] if len(ms) > 2 else None)
        hot = [x for x in (die, high) if x is not None and x >= self.abs_stop_c]
        if hot:
            return self._trip(f"die {max(hot)} C at or above {self.abs_stop_c:g} C (the shires' mean {die}, the hottest {high})", s)
        if bw is not None and bw > self.board_cap_w:
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
    p, fc = plan(), forecast()
    seq = sequence(p)
    cells = {}
    for i, blk, kind, fmt, rep in seq:
        cells[f"{fmt}.{kind}"] = max(cells.get(f"{fmt}.{kind}", 0), rep)
    want = {f"{t}.{k}": p["runs_per_cell"][k] for t in FMTS for k in KINDS}
    if cells != want or len(seq) != 18:
        bad.append(f"the sequence's runs a cell {cells} (want {want}, 18 runs)")
    if [s[1] for s in seq][-3:] != ["S4", "S5", "S6"] or seq[0][1:4] != ("P1", "burst", "fp32"):
        bad.append("the order's ends")
    for arm in ("A", "B"):
        st = stops_of(arm, fc)
        pa = p["arms"][arm]["stops"]
        if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (pa["board_w"], pa["board_samples"], pa["die_c"]):
            bad.append(f"arm {arm}'s stops differ between the forecast and the plan")
        if ARMS[arm]["box"] != p["arms"][arm]["host"]:
            bad.append(f"arm {arm}'s box")
    if stops_of("A", fc) != {"board_cap_w": 85.0, "cap_consecutive": 3, "abs_stop_c": 80.0} or \
            stops_of("B", fc) != {"board_cap_w": 75.0, "cap_consecutive": 3, "abs_stop_c": 80.0}:
        bad.append("the stop lines are not 85 W / 75 W on 3 samples and 80 C")
    if (p["arms"]["A"]["gate"]["burst_die_max_c"], p["arms"]["A"]["gate"]["sus_die_max_c"], p["arms"]["A"]["gate"]["max_wait_s"]) != (55, 57, 300):
        bad.append("arm A's gates")
    if gate_c("B", "burst", 58.0) != 61.0 or gate_c("B", "sus", 58.0) != 62.0 or gate_c("B", "burst", 61.0) != 63.0 or gate_c("B", "sus", 61.0) != 64.0:
        bad.append("arm B's gates")
    if proc_form("burst", p) != (6.0, 7.5, 1) or proc_form("sus", p) != (6.0, 7.5, 12) or p["process"]["timeout_s"] != HOST_TIMEOUT_S:
        bad.append("the process form")
    if (p["budget"]["budget_rule_min"], p["budget"]["cap_min"]) != (CARD_RULE_S / 60, CAP_S / 60):
        bad.append("the card-time rule and cap")
    a = host_argv("/T", "fp32", 6, 7.5, "/T/STOP", fc)
    if a[:2] != ["/T/build/e190rgm/host/sparsity_host", "--test"] or a[a.index("--values") + 1] != "gemmL8x16x16:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" \
            or a[a.index("--kernel") + 1] != "/T/build/e190rgm/kernel/sparsity.elf" or a[a.index("--stop-file") + 1] != "/T/STOP":
        bad.append(f"the argv {a}")
    if [values(t, fc).split(":")[0] for t in FMTS] != ["gemmL8x16x16", "gemmL8x16x8", "gemmL8x16x4"]:
        bad.append("the GEMM arms")
    for t in FMTS:
        if values(t, fc).split(":", 2)[2] != TILES[t][0]:
            bad.append(f"{t}'s tile")
    # the stop lines: the watcher's semantics
    def smp(bw=40.0, die=50, high=None):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, die - 2, die + 3 if high is None else high]}}
    s = Stops(85, 3, 80)
    r = [s.feed(smp(86)), s.feed(smp(86)), s.feed(smp(85.0)), s.feed(smp(86)), s.feed(smp(86)), s.feed(smp(86))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (s.stop or ""):
        bad.append(f"the board line {r} {s.stop}")
    s = Stops(85, 3, 80)
    if s.feed(smp(die=77, high=79)) != [] or s.feed(smp(die=77, high=80)) != ["stop"] or "hottest 80" not in s.stop:
        bad.append("the die line on the hottest sensor")
    s = Stops(75, 3, 80)
    if s.feed(smp(die=80, high=80)) != ["stop"]:
        bad.append("the die line on the shires' mean")
    s = Stops(75, 3, 80)
    if s.feed({"t_ms": 1, "board_w": 76}) != [] or s.feed({"t_ms": 2}) != [] or s.feed({"t_ms": 3, "board_w": 76}) != [] or \
            s.feed({"t_ms": 4, "board_w": 76}) != [] or s.feed({"t_ms": 5, "board_w": 76}) != ["stop"]:
        bad.append("a sample with no board reading starts the count again")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 400e6}
    if not counted(L, "A") or counted(dict(L, cycles_max=300e6), "A") or not counted(dict(L, cycles_max=300e6), "B") or \
            counted(L, "B") or counted(dict(L, launch=-1), "A") or counted(dict(L, ok=False), "A") or counted(dict(L, wall_s=0.05, cycles_max=40e6), "A"):
        bad.append("the counted launch")
    if not config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("A", {"tdp_w": 70, "temp_threshold_c": 65}) \
            or config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}) or not config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}):
        bad.append("the start config")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E190-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
