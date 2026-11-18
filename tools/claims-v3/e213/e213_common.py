#!/usr/bin/env python3
"""E213's kit (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): what the box runner, the doubles, the reducer, the collector and
the desk tests share, for E213's TWO ARMS: arm A on aifoundry3 card 0 and arm B on aifoundry1 card 1. E206's kit form for its two arms
(tools/claims-v3/e206/e206_common.py, landed in 906699ea; arm A run FULL by E206 on aifoundry3, data d7e4f35e; arm B run FULL on card 1, data
79340bfa), with E211's two kernels, its identity gate per process and its walk check (tools/claims-v3/e211/e211_common.py, landed in 2b7f261f; run
FULL by E211 on aifoundry3, data 38aaf004), and one arm family new to a card: rgm211's own gemmL loop. Python's own modules only: it runs on
aifoundry3 and aifoundry1 under the system python3 (3.12.3, read on both at 21:39 PST Tue 17 Nov 2026) and at the desk under /usr/bin/python3
-I -B (3.12.3).

It reads the registration's files and never changes them: points-e213.json (every point's host arguments, its loop, host, ELF, the smoke's points,
the ties and the order, per arm), plan-e213.json (per arm: the card, its clock and config, the line, the stops, the die gate, the card time), and
the frozen forecasts the doubles drive their toy card with (arm A: MM1-v3's tools/matmul/mm1/v3/out/mm1_v3_e213.csv, frozen in b1493082; arm B:
forecast-e213b-v3.csv, frozen by the registration; each read only at its sha256). It adds:
  - THE TWO ARMS' IDENTITIES (E213.md 6): arm A aifoundry3 card 0 (its one card: /dev/et0_*, the lock etsoc-shire0.lock, ET_DEVICES unset, the
    box tree ~/aifoundry, the box's reader build/ettelem/ettelem at 16037641..., E206's, E207's and E211's pin, read there again at 21:39 PST);
    arm B aifoundry1 card 1 (ET_DEVICES=1 on every device process, the lock etsoc-shire1.lock, the box tree ~/nekko, the lab's card-1 reader
    build/ettelem/ettelem at 8008f96f..., E206 arm B's pin, read there again at 21:39 PST); the start config gates (arm A TDP 0 W / 65 C /
    600 MHz; arm B 65 W / 65 C / 600 MHz, read as found, nothing set) and the clock band (590-610 MHz);
  - THE TWO BUILDS on each arm's box (kernel-e213.json): rgm136 from tools/claims-v3/e136/rgm136 (unchanged) into build/e213rgm/rgm136, and rgm211
    from tools/claims-v3/e211/rgm211 (E211's, unchanged) into build/e213rgm/rgm211 (new folders of ours); THE KERNEL GATE on each (ident_e213.py:
    the .text always the pin, and the whole ELF the pinned one or else its loadable identity the pinned one; aifoundry3's riscv gcc prints
    "(g1b306039a) 15.1.0" into a section the card never loads, aifoundry1's and this desk's "() 15.1.0"); the hosts read by their behaviour;
  - THE FOUR ARM FAMILIES (kernel-e213.json > arm_families; each point's "loop"): "rgm136 gemmL" runs rgm136's ELF on rgm136's host (both arms);
    "rgm136 gemmLnc" rgm136's ELF on rgm211's host (both arms; arm B's k37-k40 and smoke s14); "rgm211 gemmLn" rgm211's ELF on rgm211's host (arm
    A); and NEW, "rgm211 gemmL": rgm211's own copy of gemmL's walk, rgm211's ELF on rgm211's host (arm A's a074, a078, a081, a085). A family is a
    point's LOOP, never its arm token (rgm211's gemmL spells its arm like rgm136's: gemmL<MB>x<NB>x<KB>); host_argv names each point's own host
    and ELF, and THE IDENTITY GATE PER PROCESS is the runner's (ident_e213.gate on the point's loop);
  - THE WALK CHECK's reading (E211's): every launch record of rgm211's host carries "walk", "walk_tagged" and "walk_ok", its check record "walk"
    and "walk_launches_bad"; a "rgm211 gemmLn" process wants walk nm (the tag on every hart), a "rgm136 gemmLnc" or "rgm211 gemmL" process walk mn
    (the tag on none), on every launch, walk_ok true on every launch and walk_launches_bad 0. rgm136's host prints no walk. The walk check cannot
    tell rgm211's ELF from rgm136's for a gemmL arm (neither tags a gemmL launch): for "rgm211 gemmL" only the identity gate can (KIT.md 4);
  - THE TILES: every file the points' --values name, at the sha256 kinds.json records;
  - THE STOP LINES (plan-e213.json > arms > stops: arm A the board above 70 W on 3 samples in a row, the die at or above 70 C; arm B above 72 W on 3,
    at or above 80 C; E206.md A1 items 1 and 2), with THE LATCH READING (the telemetry's minshire[2] is a latch held since the card's last
    statistics reset, not the hottest sensor now: it trips only when it has RISEN during the session above the lowest value it read since the
    session's first sample and reads at or above the line), the board line counting only samples that carry a board reading;
  - THE GATES (plan-e213.json): the die gate (arm A min(60, rest die + 4) C, arm B min(63, rest die + 3) C; at most 300 s, else that run is NO
    DATA), THE CARD-TIME RULE (arm A no run after 60 card-minutes, the session ends at 70; arm B 42 and 48) and the window's last end;
  - THE ORDER: points-e213.json > arms > <arm> > order > sequence (arm A 105 runs, arm B 85: a tie run, pass 1, a tie run, pass 2, a tie run),
    each run one host process `timeout 10 <the point's host> <the point's host_args> --kernel <the point's ELF> --stop-file <STOP>`, never
    `timeout -k`; the smoke (arm A s01-s04, arm B s11-s14) the runner's own, first;
  - AMENDMENT A1 (E213.md; fix-e213, before any datum): THE FAMILY SMOKE, arm A's s04 (gemmL2x2x2 fp32 random on rgm211's host and ELF, the
    family 'rgm211 gemmL''s own: that loop never ran on a card), with ITS OWN STOP PATH (FAMILY_SMOKE; rules-e213.json > A1, which the self-check
    reads): a failure that is the family's (a GATE FAILED, a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok,
    an exit not 0 but 124, the counter's mean outside R0's band, the board's rise short on a live sampler) DROPS THE FAMILY - its points never
    start, NO DATA - and the session goes on; a failure that is the session's (a1_session_level: K1, HUNG, a launch timeout rc 124, the host not
    shown on the arm's card, the sampler not live after it) or any stop raised during it still stops the session, as at s01-s03;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E206's functions, line for line): runtime
    lines ("Opening device N", aifoundry1's runtime prints them on a host's stdout) removed pass after pass until none is left; runtime_cards
    names the cards they open (another card than the arm's is an identity trip); each "SPARSITY {...}" line must parse whole and carry its
    command's own fields, else it is NOT read;
  - the counted launch (E213.md 7): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz.
    python3 -I -B tools/claims-v3/e213/e213_common.py        the self-check (E213-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e213.json")
PTS_F = os.path.join(HERE, "points-e213.json")
KJ_F = os.path.join(HERE, "kernel-e213.json")
FC = {      # the frozen forecasts the doubles read (E213.md section 0), each at its pin
    "A": ("tools/matmul/mm1/v3/out/mm1_v3_e213.csv", "01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49"),
    "B": ("tools/claims-v3/e213/forecast-e213b-v3.csv", "e529bbb24de26bc68c50279945c31a0da384e1f6c01cddc1f510cd2e1c0c4ed0"),
}
FMTS = ("fp32", "fp16", "int8")

# ---- the builds (build_e213.sh writes them on each arm's box, from the box tree's root)
BUILD_DIR = "build/e213rgm"
BUILD_REC = BUILD_DIR + "/BUILD-e213.json"
GUARD = "tools/claims-v3/e213/ettelem_guard_e213.sh"
BUILDER = "build_e213.sh"
ETDEV_YES = "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"
KERNELS = {     # kernel-e213.json, repeated here and checked against it by the self-check
    "rgm136": {"src": "tools/claims-v3/e136/rgm136", "dir": BUILD_DIR + "/rgm136",
               "elf": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
               "text": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
               "load": "649d40793e459e51db9a590ca90dd1363da3a00398f98938c3ef6e190514e2b7"},
    "rgm211": {"src": "tools/claims-v3/e211/rgm211", "dir": BUILD_DIR + "/rgm211",
               "elf": "00402801a1a53a9330898ef023297d8967a2c655472a40e0f1cd65dea04f09ae",
               "text": "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069",
               "load": "1351a569e4a200cb4cd916c4c6af822b45ce6e1cac9b7aa8b71c945a1f5bd847"},
}
# THE FOUR ARM FAMILIES, keyed by the registration's "loop" (kernel-e213.json > arm_families): the host, the ELF, the arm's prefix as the host
# spells it, and the walk rgm211's host must report on every launch (None: rgm136's host prints no walk)
LOOPS = {
    "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "prefix": "gemmL", "walk": None},
    "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "prefix": "gemmLnc", "walk": "mn"},
    "rgm211 gemmLn": {"host": "rgm211", "elf": "rgm211", "prefix": "gemmLn", "walk": "nm"},
    "rgm211 gemmL": {"host": "rgm211", "elf": "rgm211", "prefix": "gemmL", "walk": "mn"},
}


def host_rel(kind):
    return KERNELS[kind]["dir"] + "/host/sparsity_host"


def elf_rel(kind):
    return KERNELS[kind]["dir"] + "/kernel/sparsity.elf"


# ---- the two arms (E213.md 6; plan-e213.json arms; the stop and gate numbers checked against the plan's words by the self-check)
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "card_index": "0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3", "jobs": "a3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # E206's, E207's, E211's; read there 21:39 PST Tue
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0, "stops": (70.0, 3, 70.0),
          "rule_s": 60 * 60.0, "cap_s": 70 * 60.0, "smoke": ("s01", "s02", "s03", "s04"), "tie": "t01",     # s04: Amendment A1
          "loops": ("rgm136 gemmL", "rgm136 gemmLnc", "rgm211 gemmLn", "rgm211 gemmL")},
    "B": {"box": "aifoundry1", "card": "aifoundry1 card 1", "card_index": "1", "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "tree": "nekko", "data_dir": "aifoundry1-c1", "jobs": "a1",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",   # E206 arm B's (E190's, E198's); read there 21:39 PST Tue
          "config": {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 63.0, "gate_add_c": 3.0, "stops": (72.0, 3, 80.0),
          "rule_s": 42 * 60.0, "cap_s": 48 * 60.0, "smoke": ("s11", "s12", "s13", "s14"), "tie": "t02",
          "loops": ("rgm136 gemmL", "rgm136 gemmLnc")},
}

# ---- AMENDMENT A1: THE FAMILY SMOKE (rules-e213.json > A1 > family_smoke; the self-check reads it): a smoke point whose failure that is not the
# session's (a1_session_level) drops its family - the family's points never start (NO DATA) - instead of stopping the session
FAMILY_SMOKE = {"s04": "rgm211 gemmL"}
RULES_F = os.path.join(HERE, "rules-e213.json")


def a1_session_level(proc, id_ok, sampler_live=True):
    """Amendment A1: the failures of a family smoke's process that still stop the session (as at s01-s03): '' when none, else why. K1 (a launch
    that did not finish), a HUNG host (alive past its timeout's TERM), a launch timeout (rc 124: the host ended by its timeout's TERM), the host
    not shown on the arm's card (its stderr, its open files, or a runtime line naming another card), the sampler not live after the process (its
    board rise cannot be read: the sampler is the session's, never the family's). Any stop raised during the process (a stop line, the operator's
    STOP file, a holder, an identity trip) is the runner's own and stops the session too."""
    why = []
    if not sampler_live:
        why.append("the sampler not live after it (its board rise unreadable)")
    if proc.get("k1"):
        why.append("K1 (a launch did not finish)")
    if proc.get("hung") or proc.get("rc") is None:
        why.append("HUNG (alive past its timeout's TERM)")
    if proc.get("rc") == 124:
        why.append("a launch timeout (rc 124: ended by its timeout's TERM)")
    if not id_ok:
        why.append("the host not shown on the arm's card")
    return "; ".join(why)


# ---- every file a point's --values names, at the sha256 kinds.json records (kinds.json > kinds > <fmt> > <name> > sha256)
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/fp16/randn.bin": "2ab30f0f335cbe8aa87fe7a7cf27f66458deb6e34d04d5633a61d3fd96b0c974",
    "tools/claims-v3/kinds/tiles/int8/full.bin": "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9",
    "tools/claims-v3/kinds/tiles/fp32/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/int8/zeros.bin": "e5a00aa9991ac8a5ee3109844d84a55583bd20572ad3ffcd42792f3c36b183ad",
    "tools/claims-v3/kinds/tiles/fp32/ones.bin": "fef951e6c76ad6a01b208af650ca6d95769bec840e009981c5ae1316a42c90b1",
    "tools/claims-v3/kinds/tiles/int8/ones.bin": "7c7d2eb358671b401d2a5e59bf56e7163e16994a170d4788faad9be5d82363b2",
    "tools/claims-v3/kinds/tiles/fp32/sparse50.bin": "43ababfe5f3fed0963600a119a5ec805b433636594616042cac4fbab1fd69530",
}
TILE_MANIFEST = "tools/claims-v3/kinds/kinds.json"

# ---- the session's timing: the registration's numbers (E213.md 3 and 6; plan-e213.json), and the kit's own (marked)
REST_READ_S = 10.0          # E213.md 3, a run: "10 s at rest (p_rest = the median of its last 5 s)"
REST_WINDOW_S = 5.0         # the same
SMOKE_REST_S = 30.0         # the kit's (E206's and E211's smoke form): 30 s at rest first, the session's rest reading; the die gates are formed from it
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # E213.md 3: "one checked 2 s process each"; the budget E146's, E190's, E206's and E211's smoke's
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E213.md 3: "--seconds 6 --budget 7.5"
TAIL_S = 4.0                # E213.md 3: "a 4 s tail"
GATE_WAIT_S = 300.0         # plan-e213.json die_gate: "waited at most 300 s, else that run is NO DATA"
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's, E211's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz, E213.md 7's "10 Hz samples")
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
SMOKE_CYC = (200.0, 4000.0)  # E213.md 7, R0: "the smoke's counter mean 200-4,000 cycles an op" (the runner's smoke gate reads R0's band)
MHZ_BAND = (590.0, 610.0)   # E213.md 7: the kernel clock a counted launch is in, and S6's band
LINE_W = 65.0               # plan-e213.json line_W, both arms: no point whose planning peak passes it runs (none does: the self-check reads it)
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # aifoundry1's runtime, on a host's or a reader's stdout
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


def arm_points(arm):
    """Every point of an arm the runner may start: its points (scored and references), its smoke and its tie."""
    A = points()["arms"][arm]
    return A["points"] + A["smoke"] + [A["tie"]]


def point(pid):
    """A point of points-e213.json by its id, in either arm (the ids are distinct: a###, s01-s04, t01 in arm A; k###, s11-s14, t02 in arm B)."""
    for arm in ARMS:
        for p in arm_points(arm):
            if p["id"] == pid:
                return p
    raise KeyError(pid)


def arm_of(pid):
    for arm in ARMS:
        if any(p["id"] == pid for p in arm_points(arm)):
            return arm
    raise KeyError(pid)


def family(pid):
    """A point's arm family: its LOOP ('rgm136 gemmL', 'rgm136 gemmLnc', 'rgm211 gemmLn', 'rgm211 gemmL'), never its arm token."""
    return point(pid)["loop"]


def fam_host(fam):
    return LOOPS[fam]["host"]


def fam_elf(fam):
    return LOOPS[fam]["elf"]


def rgm211_host(pid):
    return LOOPS[family(pid)]["host"] == "rgm211"


_FC = {}


def forecast_rows(arm):
    """The arm's frozen MM1-v3 forecast rows by id (FC[arm], at its pin; else ValueError: the box check's harness read refuses first)."""
    if arm not in _FC:
        rel, pin = FC[arm]
        with open(os.path.join(REPO, rel), "rb") as f:
            raw = f.read()
        if hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError(f"{rel} is not E213's frozen file {pin[:12]}")
        _FC[arm] = {r["id"]: r for r in csv.DictReader(raw.decode().splitlines())}
    return _FC[arm]


def double_of(pid):
    """The doubles' toy figures at a point (desk numbers of the doubles, never a datum): MM1-v3's frozen forecast at the point where it has one
    (cycles an op on the wall and the counter's mean, seconds a GEMM, W over idle, ops a minion a GEMM); for the smoke and the ties, which no
    forecast prices, the ops from the point and the toy 900 / 800 cycles an op and 20 W over idle."""
    p = point(pid)
    arm = arm_of(pid)
    ops = int(p["ops_per_minion_per_gemm"])
    r = forecast_rows(arm).get(pid)
    if r and r.get("cycles_per_op_wall") and r.get("W_over_idle"):
        cw, cm = float(r["cycles_per_op_wall"]), float(r["cycles_per_op_mean"])
        return {"cyc_wall": cw, "cyc_mean": cm, "t": float(r["seconds_per_gemm"]), "W": float(r["W_over_idle"]), "ops": ops}
    cw, cm = 900.0, 800.0
    return {"cyc_wall": cw, "cyc_mean": cm, "t": cw * ops / 600e6, "W": 20.0, "ops": ops}


def stops_of(arm, p=None):
    """The arm's stop lines under the watcher's keys (ARMS; the self-check reads them against plan-e213.json's words)."""
    if arm not in ARMS:
        raise KeyError(arm)
    b, n, d = ARMS[arm]["stops"]
    return {"board_cap_w": float(b), "cap_consecutive": int(n), "abs_stop_c": float(d)}


def gate_c(arm, rest_die):
    """The die gate a run starts under (plan-e213.json die_gate): arm A min(60, rest die + 4), arm B min(63, rest die + 3); None with no rest die."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The registered order's runs: [{"n", "block", "id", "name"}, ...] (points-e213.json > arms > <arm> > order > sequence; the smoke is the
    runner's own, first, and not in it)."""
    if arm not in ARMS:
        raise KeyError(arm)
    return [{"n": x["n"], "block": x["block"], "id": x["id"], "name": x["name"]} for x in points()["arms"][arm]["order"]["sequence"]]


def run_key(r):
    return f"{r['n']:03d}-{r['block']}-{r['id']}"


def host_argv(root, pid, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the point's own host (its loop's: rgm136's for 'rgm136 gemmL', rgm211's for the
    other three), its registered host_args with --seconds and --budget set to the process form, then the kit's --kernel (its loop's ELF:
    rgm211's for 'rgm211 gemmLn' and 'rgm211 gemmL', rgm136's for 'rgm136 gemmL' and 'rgm136 gemmLnc') and --stop-file."""
    p = point(pid)
    fam = p["loop"]
    a = list(p["host_args"])
    for flag, val in (("--seconds", f"{seconds:g}"), ("--budget", f"{budget:g}")):
        a[a.index(flag) + 1] = val
    return [os.path.join(root, host_rel(fam_host(fam)))] + a + ["--kernel", os.path.join(root, elf_rel(fam_elf(fam))), "--stop-file", stop_file]


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
    """E213.md 7's counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


def walk_check(fam, fma, chk):
    """THE WALK CHECK's reading for one process (E211's, by loop): (ok, words, detail). rgm211's host ('rgm211 gemmLn' nm; 'rgm136 gemmLnc' and
    'rgm211 gemmL' mn): every launch record carries walk == the family's and walk_ok true, and the last check record walk == the family's and
    walk_launches_bad 0; a process with no launch record or no check record fails. rgm136's host ('rgm136 gemmL') prints no walk."""
    want = LOOPS[fam]["walk"]
    if want is None:
        return True, "no walk (rgm136's host prints none)", {}
    names = [x.get("walk") for x in fma]
    oks = [x.get("walk_ok") for x in fma]
    tagged = [x.get("walk_tagged") for x in fma]
    c = chk[-1] if chk else {}
    det = {"want": want, "names": names, "ok": oks, "tagged": tagged, "check_walk": c.get("walk"), "launches_bad": c.get("walk_launches_bad")}
    why = []
    if not fma:
        why.append("no launch record")
    if any(n != want for n in names):
        why.append(f"a launch's walk is not {want} ({sorted({str(n) for n in names})})")
    if any(o is not True for o in oks):
        why.append(f"walk_ok not true on {sum(1 for o in oks if o is not True)} launch(es)")
    if not chk:
        why.append("no check record")
    elif c.get("walk") != want or c.get("walk_launches_bad") != 0:
        why.append(f"the check line reads walk {c.get('walk')!r}, walk_launches_bad {c.get('walk_launches_bad')!r}")
    return (not why), ("walk " + want + " on every launch, walk_ok true, walk_launches_bad 0" if not why else "; ".join(why)), det


def kernel_stop(fam, proc):
    """THE KERNEL STOPS (E211's, the kit's reading for every process of rgm211's host: 'rgm211 gemmLn', 'rgm136 gemmLnc', 'rgm211 gemmL'): a check
    of C wrong (or missing), a tensor error, the walk check failed, a launch timeout (K1, or the process ended by its `timeout`'s TERM) or any
    launch not ok, or the process's exit not 0: '' when none, else why (the session stops: nothing more that day). The identity gate is the
    runner's, before the process starts. A 'rgm136 gemmL' process (rgm136 on its own host, run FULL on both cards by E206) keeps E206's rules (a
    failed process flagged; two in a row stop)."""
    if LOOPS[fam]["host"] != "rgm211":
        return ""
    why = []
    if proc.get("check") not in ("exact", "approx") or not proc.get("check_ok"):
        why.append(f"the check of C reads {proc.get('check')!r} (ok {proc.get('check_ok')})")
    if proc.get("tensor_errors"):
        why.append(f"{proc.get('tensor_errors')} tensor error(s)")
    if not proc.get("walk_ok"):
        why.append(f"the walk check failed ({proc.get('walk_words')})")
    if proc.get("k1"):
        why.append("a launch did not finish (K1)")
    if proc.get("rc") == 124:
        why.append("the process ended by its timeout's TERM (rc 124: a launch timeout)")
    if not proc.get("launches_ok"):
        why.append("a launch not ok")
    if proc.get("rc") not in (0, None) and proc.get("rc") != 124:
        why.append(f"the process rc {proc.get('rc')}")
    return "; ".join(why)


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
    """The cards the runtime lines open, as strings in order ("Opening device 1" -> "1"); the runner treats a line naming another card than the
    arm's as an identity trip, on a host's, a config read's or the sampler's stdout."""
    out = []
    for ln in lines or []:
        m = RUNTIME_CARD.search(ln or "")
        if m:
            out.append(str(int(m.group(1))))
    return out


def host_records(text, argv=None):
    """(fma records, check records, info): the host's SPARSITY records from its stdout, runtime lines dropped first; each must parse whole
    as a JSON object and, with argv, carry its command's own fields (an fma record: arm, type, values, shire_mask, minions; a check record:
    arm, type, minions), else it is not read (info counts it: unparsed, mismatched; any other line is 'other')."""
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
    """The start config the arm's line rests on (plan-e213.json config_gate), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (plan-e213.json > arms > stops; E206's watcher, line for line): the shires' mean at or above abs_stop_c
    trips at once; the latch (minshire[2]) trips only when it has risen above the lowest value it read since the first sample and reads at or
    above abs_stop_c; a board reading above board_cap_w on cap_consecutive samples in a row trips (a reading at or under the line starts the
    count again; a sample with no board reading neither counts nor breaks the row). The first trip is kept; trip_file, if given, is touched at
    the trip (the real lines' file is the host's --stop-file, so a running host ends at its next launch boundary, about 0.5 s; nothing is ever
    killed)."""

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
    # each arm against the plan's words (plan-e213.json > arms)
    for arm, (bw, n, dc), gate_txt, cfg_txt in (("A", (70.0, 3, 70.0), "min(60, the session's rest die + 4) C, waited at most 300 s",
                                                "TDP 0 W, temperature threshold 65 C, minion 600 MHz"),
                                               ("B", (72.0, 3, 80.0), "min(63, the session's rest die + 3) C, waited at most 300 s",
                                                "TDP 65 W, temperature threshold 65 C, minion 600 MHz")):
        pa, a = p["arms"][arm], ARMS[arm]
        st = stops_of(arm)
        if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (bw, n, dc):
            bad.append(f"arm {arm}: the stops {st}")
        if f"strictly above {bw:g} W on {n} samples in a row" not in pa["stops"] or f"{dc:g} C" not in pa["stops"]:
            bad.append(f"arm {arm}: the plan's stop words {pa['stops'][:80]!r}")
        if not pa["die_gate"].startswith(gate_txt) or gate_c(arm, 100.0) != a["gate_cap_c"] or gate_c(arm, 40.0) != 40.0 + a["gate_add_c"]:
            bad.append(f"arm {arm}: the gate {pa['die_gate']!r}")
        c = a["config"]
        if not pa["config_gate"].startswith(cfg_txt) or cfg_txt != f"TDP {c['tdp_w']} W, temperature threshold {c['temp_threshold_c']} C, minion {c['minion_mhz']} MHz":
            bad.append(f"arm {arm}: the start config {pa['config_gate']!r}")
        if pa["card"] != a["card"] or pa["box"] != a["box"] or pa["lock"] != a["lock"] or pa["et_devices"] != a["et_devices"]:
            bad.append(f"arm {arm}: the card, box, lock or ET_DEVICES")
        if (pa["rule_min"], pa["cap_min"]) != (a["rule_s"] / 60, a["cap_s"] / 60):
            bad.append(f"arm {arm}: the card-time rule and cap")
        if float(pa["line_W"]) != LINE_W or pa["points_over_line"] or pa["planning_peak"]["W"] > LINE_W:
            bad.append(f"arm {arm}: a point's planning peak over the 65 W line")
        A = pts["arms"][arm]
        seq = sequence(arm)
        if len(seq) != pa["runs"] or [r["n"] for r in seq] != list(range(1, pa["runs"] + 1)):
            bad.append(f"arm {arm}: the order's runs ({len(seq)}) are not the plan's {pa['runs']}")
        if [r["block"] for r in seq].count("tie") != 3 or seq[0]["block"] != "tie" or seq[-1]["block"] != "tie" or \
                any(r["id"] != a["tie"] for r in seq if r["block"] == "tie"):
            bad.append(f"arm {arm}: the ties")
        ids = {r["id"] for r in seq if r["block"] != "tie"}
        if ids != {q["id"] for q in A["points"]}:
            bad.append(f"arm {arm}: the runs' points are not the registered {len(A['points'])}")
        if tuple(q["id"] for q in A["smoke"]) != a["smoke"] or A["tie"]["id"] != a["tie"]:
            bad.append(f"arm {arm}: the smoke {[q['id'] for q in A['smoke']]} or the tie")
        for q in arm_points(arm):
            fam = q["loop"]
            if fam not in a["loops"] or (q["host"], q["elf"]) != (LOOPS[fam]["host"], LOOPS[fam]["elf"]):
                bad.append(f"{q['id']}: loop {fam} with host {q['host']} / ELF {q['elf']} is not its family's, or not arm {arm}'s")
                break
            tok = q["arm"]
            pre = re.match(r"^(gemmL(?:nc|n)?)\d", tok)
            if not pre or pre.group(1) != LOOPS[fam]["prefix"]:
                bad.append(f"{q['id']}: arm {tok} is not of its loop {fam}")
                break
            if q["card"] != a["card"]:
                bad.append(f"{q['id']}: card {q['card']}")
                break
        rgm211_gl = sorted(q["id"] for q in A["points"] if q["loop"] == "rgm211 gemmL")
        if arm == "A" and rgm211_gl != ["a074", "a078", "a081", "a085"]:
            bad.append(f"arm A: rgm211's own gemmL points {rgm211_gl}")
        # Amendment A1: the family smoke, against rules-e213.json > A1 (at the desk) and points-e213.json (everywhere). rules-e213.json is a desk
        # file, not in the harness a box receives (step 6 runs this self-check on the box): there the comparison with it is left to the desk's
        # step 2, which runs this self-check with the registration whole (and the frozen scorer, which pins rules-e213.json)
        if os.path.exists(RULES_F):
            try:
                a1 = load(RULES_F)["A1"]
                fsm_rules, fam_pts = a1["family_smoke"].get(arm, {}), a1["family_points"]
            except (OSError, ValueError, KeyError, AttributeError):
                fsm_rules, fam_pts = "unreadable", {}
        else:
            fsm_rules, fam_pts = None, {"rgm211 gemmL": ["a074", "a078", "a081", "a085"]}
        mine = {k: v for k, v in FAMILY_SMOKE.items() if k in a["smoke"]}
        if fsm_rules is not None and mine != fsm_rules:
            bad.append(f"arm {arm}: the family smoke {mine} is not rules-e213.json's A1 {fsm_rules}")
        for sid, fam in mine.items():
            q = next((x for x in A["smoke"] if x["id"] == sid), None)
            if q is None or q["loop"] != fam or q["arm"] != "gemmL2x2x2" or q["format"] != "fp32" or q["kind"] != "random" or \
                    sorted(x["id"] for x in A["points"] if x["loop"] == fam) != sorted(fam_pts.get(fam, [])) or a["smoke"][-1] != sid:
                bad.append(f"arm {arm}: the family smoke {sid} is not A1's (its loop, shape, place last in the smoke, or its family's points)")
        if arm == "B" and sorted(q["id"] for q in A["points"] if q["loop"] == "rgm136 gemmLnc") != ["k37", "k38", "k39", "k40"]:
            bad.append("arm B: the gemmLnc points")
    # the families against kernel-e213.json
    kj = load(KJ_F)
    for k, v in KERNELS.items():
        kk = kj["kernels"][k]
        if (kk["elf_sha256"], kk["text_sha256"], kk["loadable_identity_sha256"], kk["tree"]) != (v["elf"], v["text"], v["load"], v["src"]):
            bad.append(f"{k}'s pins differ from kernel-e213.json")
    for fam, v in LOOPS.items():
        f = kj["arm_families"].get(fam)
        if not f or (f["host"], f["elf"]) != (v["host"], v["elf"]):
            bad.append(f"the family {fam} differs from kernel-e213.json")
    if set(kj["arm_families"]) != set(LOOPS):
        bad.append("the families are not kernel-e213.json's four")
    # the frozen forecasts: at their pins, every scored point there
    try:
        for arm in ARMS:
            rows = forecast_rows(arm)
            miss = [q["id"] for q in pts["arms"][arm]["points"] if q["id"] not in rows]
            if miss:
                bad.append(f"arm {arm}: no frozen forecast for {miss[:5]}")
            for q in arm_points(arm):
                d = double_of(q["id"])
                if not (d["t"] > 0 and d["cyc_mean"] > 0 and d["ops"] > 0):
                    bad.append(f"{q['id']}: the doubles' figures")
                    break
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"the frozen forecasts ({type(e).__name__}: {str(e)[:80]})")
    # the argv: every family's host and kernel
    a = host_argv("/T", "a073", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if a[:2] != ["/T/build/e213rgm/rgm211/host/sparsity_host", "--test"] or \
            arg_of(a, "--values") != "gemmLn3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin" or arg_of(a, "--shires") != "0xffffffff" \
            or arg_of(a, "--per-shire") != "32" or arg_of(a, "--seconds") != "6" or arg_of(a, "--budget") != "7.5" \
            or arg_of(a, "--kernel") != "/T/build/e213rgm/rgm211/kernel/sparsity.elf" or arg_of(a, "--stop-file") != "/T/STOP" or "-k" in a:
        bad.append(f"the rgm211 gemmLn argv {a}")
    g = host_argv("/T", "a074", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if g[0] != "/T/build/e213rgm/rgm211/host/sparsity_host" or arg_of(g, "--kernel") != "/T/build/e213rgm/rgm211/kernel/sparsity.elf" or \
            arg_of(g, "--values") != "gemmL3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin":
        bad.append(f"the rgm211 gemmL argv {g}")
    m = host_argv("/T", "a006", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if m[0] != "/T/build/e213rgm/rgm136/host/sparsity_host" or arg_of(m, "--kernel") != "/T/build/e213rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(m, "--values") != "gemmL3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin":
        bad.append(f"the rgm136 gemmL argv {m}")
    c = host_argv("/T", "k37", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if c[0] != "/T/build/e213rgm/rgm211/host/sparsity_host" or arg_of(c, "--kernel") != "/T/build/e213rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(c, "--values") != "gemmLnc3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin":
        bad.append(f"the rgm136 gemmLnc argv {c}")
    s = host_argv("/T", "s14", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp32" or \
            arg_of(s, "--kernel") != "/T/build/e213rgm/rgm136/kernel/sparsity.elf" or s[0] != "/T/build/e213rgm/rgm211/host/sparsity_host":
        bad.append(f"the smoke's argv {s}")
    mk = host_argv("/T", "a050", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if expect_of(mk)["shire_mask"] != "0x%x" % int(point("a050")["shire_mask"], 16) or expect_of(mk)["minions"] != point("a050")["minions"]:
        bad.append(f"a subset's argv {mk}")
    if expect_of(a) != {"arm": "gemmLn3x1x3", "type": "fp32", "values": "gemmLn3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
                        "shire_mask": "0xffffffff", "minions": 1024}:
        bad.append(f"expect_of {expect_of(a)}")
    for arm in ARMS:
        for q in arm_points(arm):
            e = expect_of(host_argv("/T", q["id"], 6, 7.5, "/S"))
            if (int(e["shire_mask"], 16), e["minions"], e["arm"], e["type"]) != (int(q["shire_mask"], 16), q["minions"], q["arm"], q["format"]):
                bad.append(f"{q['id']}: expect_of {e} against the point")
                break
    # the tiles: every file a point names, at its manifest's sha256 and the point's own tile_sha256
    named = {}
    for arm in ARMS:
        for q in arm_points(arm):
            for f in arg_of(q["host_args"], "--values").split(":", 2)[2].split(","):
                named[f] = q.get("tile_sha256")
    if set(named) != set(TILES) or any(named[f] != TILES[f] for f in named):
        bad.append(f"TILES is not the points' files ({len(named)} named, {len(TILES)} pinned)")
    try:
        kk = load(os.path.join(REPO, TILE_MANIFEST))["kinds"]
        for f, h in TILES.items():
            fmt, base = f.split("/")[-2], os.path.basename(f)
            if kk[fmt][base[:-4]]["sha256"] != h:
                bad.append(f"{f}: pinned {h[:12]}, its manifest {kk[fmt][base[:-4]]['sha256'][:12]}")
    except (OSError, KeyError, ValueError, TypeError) as e:
        bad.append(f"the tile manifest could not be read ({type(e).__name__})")
    # the walk check's reading, the four families
    rn = {"test": "fma", "walk": "nm", "walk_tagged": 1024, "walk_ok": True}
    cn = {"test": "check", "walk": "nm", "walk_launches_bad": 0}
    rm = dict(rn, walk="mn", walk_tagged=0)
    cm = dict(cn, walk="mn")
    if not walk_check("rgm211 gemmLn", [rn, rn], [cn])[0] or walk_check("rgm211 gemmLn", [rn, dict(rn, walk_ok=False)], [cn])[0] or \
            walk_check("rgm211 gemmLn", [rm], [cn])[0] or walk_check("rgm211 gemmLn", [rn], [dict(cn, walk_launches_bad=1)])[0] \
            or walk_check("rgm211 gemmLn", [rn], [])[0] or walk_check("rgm211 gemmLn", [], [cn])[0] or walk_check("rgm136 gemmLnc", [rn], [cn])[0] or \
            not walk_check("rgm136 gemmLnc", [rm], [cm])[0] or not walk_check("rgm136 gemmL", [], [])[0] or \
            walk_check("rgm211 gemmLn", [dict(rn, walk_ok=None)], [cn])[0] or not walk_check("rgm211 gemmL", [rm, rm], [cm])[0] or \
            walk_check("rgm211 gemmL", [rn], [cn])[0] or walk_check("rgm211 gemmL", [dict(rm, walk_ok=False)], [cm])[0] or \
            walk_check("rgm211 gemmL", [rm], [dict(cm, walk_launches_bad=2)])[0]:
        bad.append("the walk check's reading")
    good = {"check": "approx", "check_ok": True, "tensor_errors": 0, "walk_ok": True, "k1": False, "rc": 0, "launches_ok": True}
    if kernel_stop("rgm211 gemmLn", good) or not kernel_stop("rgm211 gemmLn", dict(good, check="wrong", check_ok=False)) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, walk_ok=False, walk_words="x")) or not kernel_stop("rgm211 gemmLn", dict(good, tensor_errors=1)) or \
            not kernel_stop("rgm211 gemmL", dict(good, rc=124)) or not kernel_stop("rgm211 gemmL", dict(good, k1=True)) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, rc=1)) or kernel_stop("rgm136 gemmL", dict(good, rc=1, check="wrong")) or \
            kernel_stop("rgm211 gemmL", good) or not kernel_stop("rgm211 gemmL", dict(good, launches_ok=False)):
        bad.append("the kernel stops")
    # the stop lines: the watcher's semantics, the latch reading (E206's cases, both arms' lines)
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
    st = Stops(70, 3, 70)
    r = [st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(70.0)), st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(71))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or ""):
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(**stops_of("B"))
    r = [st.feed(smp(72.0, high=66)), st.feed(smp(72.5, high=66)), st.feed(smp(73, high=66)), st.feed(smp(73, high=66))]
    if r != [[], [], [], ["stop"]] or "above 72 W" not in (st.stop or ""):
        bad.append(f"arm B's board line {r} {st.stop}")
    st = Stops(**stops_of("B"))
    if st.feed(smp(die=79, high=66)) != [] or st.feed(smp(die=80, high=66)) != ["stop"]:
        bad.append("arm B's die line at 80 C")
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
    st = Stops(70, 3, 70)       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 69.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
        bad.append("a reading under the line between over-line readings did not break the row")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 300e6}
    if not counted(L) or counted(dict(L, cycles_max=400e6)) or counted(dict(L, launch=-1)) or counted(dict(L, launch=-3)) or \
            counted(dict(L, ok=False)) or counted(dict(L, wall_s=0.05, cycles_max=30e6)) or counted(dict(L, passes=0)) or counted(dict(L, test="check")):
        bad.append("the counted launch")
    # the records: runtime lines inside a record (rgm211's host's form), a cut record, records of another command
    rec = {"test": "fma", "arm": "gemmLn3x1x3", "gen": "randn", "type": "fp32", "pattern": "none",
           "values": "gemmLn3x1x3:randn:tools/claims-v3/kinds/tiles/fp32/randn.bin", "b_stream": 0, "minions": 1024, "shire_mask": "0xffffffff",
           "iters": 6720, "passes": 1, "launch": 0, "cycles_max": 300000000, "cycles_per_op": 1434.5, "wall_s": 0.5, "walk": "nm",
           "walk_tagged": 1024, "walk_ok": True, "result": "unchecked", "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in range(0, len(line) + 1, 7):
        f_, c_, inf = host_records(line[:k] + "Opening device 1\n" + line[k:] + "\n", a)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 1"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    for k in range(0, len(line) + 1, 11):      # a runtime line printed INSIDE another runtime line, the pair inside a record
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
    f_, c_, inf = host_records(line.replace('"0xffffffff"', '"0xf"') + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another mask was read")
    f_, c_, inf = host_records(line.replace('"gemmLn3x1x3"', '"gemmL3x1x3"', 1) + "\n", a)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another arm token was read")
    if config_json("Opening device 0\n" + '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":0,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("B", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or not config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) or config_ok("C", {"tdp_w": 65}):
        bad.append("the start config")
    if gate_c("A", 50.0) != 54.0 or gate_c("A", 58.0) != 60.0 or gate_c("B", 57.0) != 60.0 or gate_c("B", 61.0) != 63.0 or gate_c("A", None) is not None:
        bad.append("the die gate")
    try:
        sequence("C")
        bad.append("an arm C sequence")
    except KeyError:
        pass
    if abs(RUN_MAX_S - 28.0) > 1e-9:
        bad.append("RUN_MAX_S")
    if family("a074") != "rgm211 gemmL" or family("a006") != "rgm136 gemmL" or not rgm211_host("a074") or rgm211_host("k41") or \
            arm_of("k37") != "B" or arm_of("s03") != "A" or arm_of("t02") != "B" or family("s04") != "rgm211 gemmL" or family("s01") != "rgm136 gemmL":
        bad.append("the family, host and arm lookups")
    sl = (a1_session_level({"k1": True, "rc": 1}, True), a1_session_level({"rc": 124}, True), a1_session_level({"hung": True, "rc": None}, True),
          a1_session_level({"rc": 0}, False), a1_session_level({"rc": 0}, True, sampler_live=False),
          a1_session_level({"rc": 1, "check": "wrong"}, True), a1_session_level({"rc": 0}, True))
    if not all(sl[:5]) or any(sl[5:]):
        bad.append(f"A1's session-level reading {sl}")
    return bad


if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E213-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
