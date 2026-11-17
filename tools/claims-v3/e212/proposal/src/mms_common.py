#!/usr/bin/env python3
"""1117-mmsweep2: what the session runner, its doubles, the reducer and the desk tests share (Python's own modules only: it
runs on the lab boxes under the system python3, and at the desk under python3 -I -B).

  - THE CARDS: the box, the card's lock, ET_DEVICES, the card's nodes and physical device ID, the start config each card's
    plan rests on, the clock bands a launch is counted in, the stop lines, the die gate, the planning line;
  - THE LAYOUT of the kit on a box (every path relative to the kit's root, ~/claude/work/ee-1117-mmsweep2 on each box);
  - one process's command line (rgm136's sparsity_host, E136's arm grammar gemmL<MB>x<NB>x<KB>);
  - the counted launch, by clock band; the host's SPARSITY lines; THE STOP LINES on live samples.
    python3 -I -B src/mms_common.py        the self-check (MMS-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))      # the kit's root: src/ is pushed into it, build/, run/, sessions/ beside
KIT = "1117-mmsweep2"

# ---- the layout, relative to ROOT
BUILD = "build"
HOST = "build/rgm/host/sparsity_host"
ELF = "build/rgm/kernel/sparsity.elf"
ETTELEM = "build/ettelem/ettelem"
BUILD_REC = "build/BUILD-mms.json"
GUARD = "src/guard_ettelem.sh"
RUN_DIR = "run"                       # box lock, the current session's pointer, the kit-wide STOP file
BOX_LOCK = "run/box.lock"
KIT_STOP = "run/STOP"
SESSIONS = "sessions"
KERNEL_PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"  # E136's rgm136 build record (both lab boxes)

# ---- the cards
# config: the start config read the card's plan rests on (read at rest: 600 MHz on every card). power_state: low_power (3) on
# aifoundry2 and aifoundry1 card 0 (every start read on record); card 1 reads low_power or managed_power (E190's note 1: 376 of
# its 420 committed reads managed_power), so both are taken there and the closing read records any change.
CARDS = {
    "a2c0": {"box": "aifoundry2", "card": "0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None, "governed": True,
             "config": {"tdp_w": ("eq", 65), "temp_threshold_c": ("eq", 65), "minion_mhz": ("eq", 600), "power_state": ("eq", 3)},
             "mv_rule": None,
             "bands": {"800": (790.0, 810.0), "700": (690.0, 710.0), "600": (590.0, 610.0)}, "main_band": "800",
             "stops": {"board_cap_w": 85.0, "cap_consecutive": 3, "abs_stop_c": 80.0}, "line_w": 80.0,
             "gate": {"ceiling_c": 55.0, "over_rest_c": None},
             "tau_s": {"minion": 1.06, "sram": 1.02, "noc": 1.05}},
    "a1c1": {"box": "aifoundry1", "card": "1", "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1", "governed": False,
             "config": {"tdp_w": ("eq", 65), "temp_threshold_c": ("eq", 65), "minion_mhz": ("eq", 600), "power_state": ("in", (1, 3))},
             "mv_rule": ("lt", 510), "bands": {"600": (590.0, 610.0)}, "main_band": "600",
             "stops": {"board_cap_w": 75.0, "cap_consecutive": 3, "abs_stop_c": 80.0}, "line_w": 70.0,
             "gate": {"ceiling_c": 60.0, "over_rest_c": 3.0},
             "tau_s": {"minion": 1.06, "sram": 0.53, "noc": 1.07}},
    "a1c0": {"box": "aifoundry1", "card": "0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": "0", "governed": True,
             "config": {"tdp_w": ("eq", 65), "temp_threshold_c": ("eq", 65), "minion_mhz": ("eq", 600), "power_state": ("eq", 3)},
             "mv_rule": ("ge", 510),
             "bands": {"800": (790.0, 810.0), "700": (690.0, 710.0), "600": (590.0, 610.0)}, "main_band": "800",
             "stops": {"board_cap_w": 65.0, "cap_consecutive": 3, "abs_stop_c": 80.0}, "line_w": 52.0,
             "gate": {"ceiling_c": 55.0, "over_rest_c": 3.0},
             "tau_s": {"minion": 1.05, "sram": 1.03, "noc": 1.05}},
}
# tau_s: the rails' first-order filter (the lab's tools/ettelem/deconv.py CARD_TAU, its offline fits; aifoundry1 card 0 has no fit
# there and takes that file's default), each rail reaching the host one service-processor pass late (LAG_PASSES)
LAG_PASSES = 1
OTHER_CARD_ON_BOX = {"a1c1": "0", "a1c0": "1", "a2c0": None}
HOST_TIMEOUT_S = 10
EVERY_MS = 100
SAMPLE_FRESH_S = 2.0
RISE_MIN_W = 2.0
CYC_LO, CYC_HI = 200.0, 4000.0       # the smoke's sanity band for cycles an op (any shape, any clock)
CLOSE_S = 60.0
TERM_GRACE_S = 30.0                  # a device read past its bound: SIGTERM to its wrapper, then this long before it is a leftover
ETWHO_GRACE_S = 10.0                 # the same for et-who and the box check (no device behind them)
LEFTOVER_WAIT_S = 600.0              # a device process of ours still alive at the closing: the card's lock is kept up to this long
FAILED_IN_A_ROW = 2                  # this many failed processes in a row (rc not 0, or a check of C not ok) stop the session
# the reduction's registered windows and rules (request.md section 8)
WIN_LO_S, WIN_HI_S = 1.0, 3.5        # governed cards: launches starting 1.0-3.5 s after their process's launch 0 started
CAPPED_FRAC = 0.8                    # governed cards: under this share of a run's launches in the 800 MHz band, the run is capped
MIN_LAUNCH, MIN_SAMPLES = 3, 10      # a view's figure needs this many launches and board samples (the window view: 2 and 8)
MIN_LAUNCH_WIN, MIN_SAMPLES_WIN = 2, 8
SLOW_SAMPLE_MS = 100                 # a sample the reader took longer than this to read is left out of the board figures
DIE_SLOPE = 0.0048                   # the lift's rise with start die, a fraction a degree (the lab's 0.48 %/C on aifoundry2)


def node(card, kind):
    return f"/dev/et{CARDS[card]['card']}_{kind}"


def load(path):
    with open(path) as f:
        return json.load(f)


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rule_ok(rule, v):
    op, want = rule
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return False
    if op == "in":
        return v in want
    return {"eq": v == want, "le": v <= want, "lt": v < want, "ge": v >= want}[op]


def config_ok(card, j):
    """'' when the start config read is the one the card's plan rests on, else why."""
    if not j:
        return "no config JSON"
    bad = [f"{k} {j.get(k)} (want {r[0]} {r[1]})" for k, r in CARDS[card]["config"].items() if not rule_ok(r, j.get(k))]
    return "; ".join(bad)


def host_argv(sched_run, seconds, budget, stop_file, seed=1):
    """One process's command line, relative to ROOT (the runner's cwd), without `timeout 10`: E136's form."""
    return [HOST, "--test", "fma", "--type", sched_run["type"], "--pattern", "none", "--values", sched_run["values"],
            "--shires", sched_run["shires"], "--per-shire", "32", "--seconds", f"{seconds:g}", "--budget", f"{budget:g}",
            "--seed", str(seed), "--kernel", ELF, "--stop-file", stop_file]


def parse_sparsity(text):
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


def kclock(L):
    """A launch's kernel clock in MHz: cycles_max / wall_s (E119's clock_x)."""
    w = L.get("wall_s") or 0
    return (L.get("cycles_max") or 0) / w / 1e6 if w > 0 else None


def band_of(card, L):
    """The clock band a launch falls in ('800', '700', '600' or None), from its kernel clock."""
    f = kclock(L)
    if f is None:
        return None
    for b, (lo, hi) in CARDS[card]["bands"].items():
        if lo <= f <= hi:
            return b
    return None


def ok_launch(L):
    """An fma launch the reduction can use: launch >= 0 (not the sizing launch -1 or the check launch -3), ok, wall_s >= 0.1 s,
    at least one pass."""
    return L.get("test") == "fma" and (L.get("launch") if L.get("launch") is not None else -9) >= 0 and bool(L.get("ok")) \
        and (L.get("wall_s") or 0) >= 0.1 and bool(L.get("passes"))


def counted(L, card, band=None):
    """A counted launch: ok_launch, in the band (default the card's main band: 800 MHz on the governed cards, 600 MHz on card 1)."""
    return ok_launch(L) and band_of(card, L) == (band or CARDS[card]["main_band"])


def die_of(s):
    return ((s.get("temp_c") or {}).get("minshire") or [None])[0]


def latch_of(s):
    ms = (s.get("temp_c") or {}).get("minshire") or []
    return ms[2] if len(ms) > 2 else None


def gate_c(card, rest_die):
    """The die gate a run starts under: at or below the card's ceiling, and (cards 1 and 0 of aifoundry1) at or below the
    session's rest die + over_rest_c (3 C, E190's); None when that needs a rest die and there is none (no run starts)."""
    g = CARDS[card]["gate"]
    if g["over_rest_c"] is None:
        return g["ceiling_c"]
    if rest_die is None:
        return None
    return min(g["ceiling_c"], rest_die + g["over_rest_c"])


class Stops:
    """THE STOP LINES on live samples: the board strictly above board_cap_w on cap_consecutive samples in a row (a sample with
    no board reading, or at or under the line, starts the count again); the shires' mean at or above abs_stop_c on one sample;
    the hottest-sensor latch at or above abs_stop_c once it has risen above its first reading of the session (a latch holds its
    maximum since the last statistics reset, so only a rise is today's). The first trip is kept; trip_file, if given, is
    touched at the trip (the real lines' file is the hosts' --stop-file: a running host ends at its next launch boundary)."""

    def __init__(self, board_cap_w, cap_consecutive, abs_stop_c, trip_file=None):
        self.board_cap_w, self.need, self.abs_stop_c = float(board_cap_w), int(cap_consecutive), float(abs_stop_c)
        self.trip_file = trip_file
        self.over = 0
        self.stop = None
        self.t_trip = None
        self.latch0 = None

    def feed(self, s):
        if self.stop:
            return []
        bw = s.get("board_w")
        die, latch = die_of(s), latch_of(s)
        if latch is not None and self.latch0 is None:
            self.latch0 = latch
        if die is not None and die >= self.abs_stop_c:
            return self._trip(f"die {die} C (the shires' mean) at or above {self.abs_stop_c:g} C", s)
        if latch is not None and self.latch0 is not None and latch > self.latch0 and latch >= self.abs_stop_c:
            return self._trip(f"the hottest-sensor latch rose to {latch} C (first {self.latch0} C), at or above "
                              f"{self.abs_stop_c:g} C", s)
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


ROLES = ("anchor", "arm", "time", "null")
FORM_KEYS = {"burst": 1, "sus3": 3, "null": 0}


def load_sched(path):
    s = load(path)
    if s.get("kit") != KIT or s.get("card") not in CARDS or not s.get("runs"):
        raise ValueError(f"not a {KIT} schedule: {path}")
    line = CARDS[s["card"]]["line_w"]
    over = [r["arm"] for r in s["runs"] + s["smoke"] if r["est_peak_w"] > line]
    if over or s.get("line_w") != line:
        raise ValueError(f"schedule {path}: arms over the card's line {line} W: {over}")
    forms = s.get("forms") or {}
    bad = [r["arm"] for r in s["runs"] if r.get("role") not in ROLES or r.get("form") not in FORM_KEYS or r["form"] not in forms
           or forms[r["form"]].get("nproc") != FORM_KEYS[r["form"]] or (r["role"] == "null") != (r["form"] == "null")
           or (r["form"] != "null" and r.get("test") != "fma")]
    if bad:
        raise ValueError(f"schedule {path}: runs with an unknown role or form: {bad[:5]}")
    return s


def selfcheck(src=None):
    """The self-check; src: the src/ folder whose sched/ and arms.json are read (default this kit's; the desk tests pass a toy
    plan's)."""
    bad = []

    def smp(bw=40.0, die=50, latch=70, t=1):
        return {"t_ms": t, "board_w": bw, "temp_c": {"minshire": [die, die - 2, latch]}}
    s = Stops(85, 3, 80)
    r = [s.feed(smp(86)), s.feed(smp(86)), s.feed(smp(85.0)), s.feed(smp(86)), s.feed(smp(86)), s.feed(smp(86))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (s.stop or ""):
        bad.append(f"the board line {r} {s.stop}")
    s = Stops(75, 3, 80)
    if s.feed(smp(die=79)) != [] or s.feed(smp(die=80)) != ["stop"] or "mean" not in s.stop:
        bad.append("the die line on the shires' mean")
    s = Stops(75, 3, 80)       # a latch already at 85 from before the session: no trip until it rises
    if s.feed(smp(latch=85)) != [] or s.feed(smp(latch=85)) != [] or s.feed(smp(latch=86)) != ["stop"]:
        bad.append("the latch rule")
    s = Stops(75, 3, 80)       # a latch rising to 79 does not trip; to 80 does
    if s.feed(smp(latch=70)) != [] or s.feed(smp(latch=79)) != [] or s.feed(smp(latch=80)) != ["stop"]:
        bad.append("the latch's rise to the line")
    s = Stops(65, 3, 80)
    if s.feed({"t_ms": 1, "board_w": 66}) != [] or s.feed({"t_ms": 2}) != [] or s.feed({"t_ms": 3, "board_w": 66}) != [] \
            or s.feed({"t_ms": 4, "board_w": 66}) != [] or s.feed({"t_ms": 5, "board_w": 66}) != ["stop"]:
        bad.append("a sample with no board reading starts the count again")
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 400e6}
    if not counted(L, "a2c0") or counted(L, "a1c1") or not counted(dict(L, cycles_max=300e6), "a1c1") \
            or counted(dict(L, cycles_max=300e6), "a2c0") or not counted(dict(L, cycles_max=300e6), "a2c0", "600") \
            or counted(dict(L, launch=-1), "a2c0") or counted(dict(L, ok=False), "a2c0") \
            or counted(dict(L, wall_s=0.05, cycles_max=40e6), "a2c0") or counted(dict(L, launch=-3), "a1c0") \
            or not ok_launch(dict(L, cycles_max=1e6)) or ok_launch(dict(L, passes=0)) or not rule_ok(("in", (1, 3)), 1) \
            or rule_ok(("in", (1, 3)), 2):
        bad.append("the counted launch")
    c0 = {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "power_state": 3}
    if config_ok("a2c0", c0) or not config_ok("a2c0", dict(c0, tdp_w=70)) or not config_ok("a2c0", dict(c0, power_state=1)) \
            or not config_ok("a2c0", dict(c0, minion_mhz=800)) or \
            not config_ok("a1c1", dict(c0, minion_mhz=800)) or config_ok("a1c1", c0) or config_ok("a1c1", dict(c0, power_state=1)) \
            or not config_ok("a1c1", dict(c0, power_state=2)) or \
            config_ok("a1c0", c0) or not config_ok("a1c0", dict(c0, tdp_w=40)) or not config_ok("a1c0", dict(c0, power_state=1)) \
            or not config_ok("a1c0", {"tdp_w": 65, "temp_threshold_c": 65}):
        bad.append("the start config rules")
    if gate_c("a2c0", None) != 55.0 or gate_c("a1c1", 51.0) != 54.0 or gate_c("a1c1", 58.0) != 60.0 or gate_c("a1c0", None) \
            is not None or gate_c("a1c0", 46.0) != 49.0:
        bad.append("the gates")
    a = host_argv({"type": "int8", "values": "gemmL4x8x8:randn:src/tiles/int8/full.bin", "shires": "0xffffffff"}, 6, 7.5,
                  "sessions/X/STOP")
    if a[0] != HOST or a[a.index("--kernel") + 1] != ELF or a[a.index("--values") + 1] != "gemmL4x8x8:randn:src/tiles/int8/full.bin" \
            or a[a.index("--per-shire") + 1] != "32" or a[a.index("--stop-file") + 1] != "sessions/X/STOP" or any(x.startswith("/") for x in a):
        bad.append(f"the argv {a}")
    src = src or HERE
    have = sorted(n[:-5] for n in os.listdir(os.path.join(src, "sched")) if n.endswith(".json")) \
        if os.path.isdir(os.path.join(src, "sched")) else []
    # the sessions the plan made (src/arms.json, written by src/make_schedule2.py): exactly these schedules, none other
    made = load(os.path.join(src, "arms.json")).get("sessions") or {} if os.path.isfile(os.path.join(src, "arms.json")) else {}
    if sorted(f"{c}-{x}" for c, xs in made.items() for x in xs) != have:
        bad.append(f"the schedules present: {have}")
    for name in have:
        card, sess = name.split("-")
        if True:
            p = os.path.join(src, "sched", f"{card}-{sess}.json")
            try:
                sc = load_sched(p)
            except (OSError, ValueError) as e:
                bad.append(f"{card}-{sess}: {e}")
                continue
            if sc["runs"][0]["role"] != "anchor" or sc["runs"][-1]["role"] != "anchor":
                bad.append(f"{card}-{sess}: the anchor is not first and last")
            for r in [x for x in sc["runs"] if x["form"] != "null"] + sc["smoke"]:
                if any(x.startswith("/") or ".." in x for x in (r["values"],)) or len(r["values"].split(":")) != 3 \
                        or not all(f.startswith("src/tiles/") for f in r["values"].split(":")[2].split(",")):
                    bad.append(f"{card}-{sess}: values {r['values']}")
            if card != "a2c0" and any(r["role"] == "time" for r in sc["runs"]):
                bad.append(f"{card}-{sess}: a time-only run off aifoundry2")
            if sum(1 for r in sc["runs"] if r["role"] == "null") < 4:
                bad.append(f"{card}-{sess}: fewer than 4 null runs")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("MMS-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
