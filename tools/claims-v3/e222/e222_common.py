#!/usr/bin/env python3
"""E222's kit (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum): what the box runner, the doubles, the reducer, the collector and
the desk tests share, for E222's ONE ARM, aifoundry3 card 0 at its pinned 600 MHz. E218's kit form (tools/claims-v3/e218/e218_common.py, kit
5582edfc, landed with E218's registration 1b853bac, which ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST Fri 20 Nov 2026: 107 of 107
runs, the opening smoke, the stop-path test and the gemmLnc smoke s03 in its place, data b445b0f5), itself E215 arm A's (8bde0182), line for
line but for E222's registration: its points, its order, its forecasts, its card-time rule and cap. Python's own modules only: it runs on
aifoundry3 under the system python3 (3.12.3) and at the desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e222.json (every point's host arguments, its loop, host, ELF and family),
plan-e222.json (the card, its clock and config, the drop line, the stops, the die gate, the card time and THE ORDER, plan > order > runs),
kernel-e222.json (the kernel's pins and the two arm families), the frozen forecasts the doubles drive their toy card with (forecast-e222.csv,
MM1-v3.2's rows: every point, the tie t01 and the two smokes, frozen by FROZEN.txt and the registration; read only at its sha256), and E218's
registered points-e218.json for the tie and the two smokes alone (E222.md 3: "The tie t01 (E218's gemmL2x4x4 fp32 random, the full chip ...).
The smoke (one checked process each, never a point; E218's): s01 gemmL2x2x2 fp32 at the opening ...; s03 gemmLnc2x2x2 fp32 right before the G
block"; read at its registered sha256, their tokens checked against points-e222.json > extra_rows). It adds:
  - THE ARM'S IDENTITY (E222.md 6): aifoundry3 card 0 (its one card: /dev/et0_*, the lock etsoc-shire0.lock, ET_DEVICES unset, the box tree
    ~/aifoundry, the box's reader build/ettelem/ettelem at 16037641..., E206's, E207's, E211's, E213 arm A's, E215 arm A's and E218's pin); the
    start config gate (TDP 0 W / 65 C / 600 MHz, read as found, nothing set) and the clock band (590-610 MHz);
  - THE TWO BUILDS on the box (kernel-e222.json): rgm136 from tools/claims-v3/e136/rgm136 (unchanged: the ELF every E222 process runs) into
    build/e222rgm/rgm136, and rgm211 from tools/claims-v3/e211/rgm211 (E211's, unchanged: ITS HOST runs rgm136's ELF for the gemmLnc branch) into
    build/e222rgm/rgm211 (new folders of ours); THE KERNEL GATE on rgm136's ELF (ident_e222.py: the .text always the pin, and the whole ELF the
    pinned one or else its loadable identity the pinned one; aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0" into a section the card never
    loads) and THE TREE GATE on rgm211's ELF (its whole ELF or its loadable identity at kernel-e222.json's rgm211_host pins: the tree the host comes
    from is E211's; that ELF runs no E222 point); the hosts read by their behaviour;
  - THE TWO ARM FAMILIES (kernel-e222.json > arm_families; each point's "loop"): "rgm136 gemmL" runs rgm136's ELF on rgm136's host (families T-L3,
    T-Y2, T-G2t, L3b, Y3, G3t, R's ry01a, ry01b and rg01t, the tie t01 and the session's smoke s01); "rgm136 gemmLnc" rgm136's ELF on rgm211's host
    (R's rg01, T-G2 wn01-wn07 and G3 k01-k07: the G block, and its own smoke s03). A family is a point's LOOP, never its arm token; host_argv names
    each point's own host and ELF, and THE IDENTITY GATE PER PROCESS is the runner's (ident_e222.gate on the point's loop: rgm136's ELF for both);
  - THE WALK CHECK's reading (E211's): every launch record of rgm211's host carries "walk", "walk_tagged" and "walk_ok", its check record "walk"
    and "walk_launches_bad"; a "rgm136 gemmLnc" process wants walk mn (the tag on none), on every launch, walk_ok true on every launch and
    walk_launches_bad 0. rgm136's host prints no walk. The walk cannot tell rgm211's ELF from rgm136's for a gemmLnc arm (neither tags it): only the
    identity gate can (KIT.md 4);
  - THE TILES: every file the points' --values name (E222's points are all fp32 random: kinds/tiles/fp32/randn.bin), at the sha256 the
    registration records (points-e222.json > tile_sha256) and its manifest records (kinds/kinds.json);
  - THE STOP LINES (plan-e222.json > card > live_stops: the board strictly above 70 W on 3 samples in a row, the die at or above 70 C; E218's
    lines), with THE LATCH READING (the telemetry's minshire[2] is a latch held since the card's last statistics reset, not the hottest sensor now:
    it trips only when it has RISEN during the session above the lowest value it read since the session's first sample and reads at or above the
    line), the board line counting only samples that carry a board reading;
  - THE GATES (plan-e222.json): the die gate (min(60, rest die + 4) C; at most 300 s, else that run is NO DATA), THE CARD-TIME RULE (no run after
    70 card-minutes, the session ends at 80) and the window's last end;
  - THE ORDER (plan-e222.json > order > runs, 122 entries, the opening smoke s01 the first, the runner's own and not in the kit's sequence): the
    kit's sequence is the other 121 in the registered order, numbered 1..121 (the registered place less one, kept as "reg_n") - a tie run, pass 1
    (55), a tie run, pass 2 (40), a tie run, then THE G BLOCK, LAST: its family smoke s03 (the registered block "smoke", the kit's "G-smoke") and
    its 22 runs (the registered "G block", 15 runs, the kit's G-pass1; "G block reversed (G3 only)", 7, the kit's G-pass2) (E222.md 6); each run one
    host process `timeout 10 <the point's host> <the point's host_args> --kernel <the point's ELF> --stop-file <STOP>`, never `timeout -k`;
  - THE FAMILY SMOKE (E222.md 3 and 6; E213's Amendment A1 form, as E215 arm A and E218 ran it): s03 is the G block's own, with ITS OWN STOP PATH:
    a failure that is the family's (a GATE FAILED, a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an exit
    not 0 but 124, the counter's mean outside R0's band, the board's rise short on a live sampler; or the smoke not starting by the die gate) DROPS
    THE FAMILY - its points never start, NO DATA - and the session goes on; a failure that is the session's (a1_session_level: K1, HUNG, a launch
    timeout rc 124, the host not shown on the card, the sampler not live after it) or any stop raised during it stops the session. s01 is the
    session's gate (SESSION_SMOKE): any failure there is the smoke gate, no run;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; E206's functions, line for line): runtime
    lines ("Opening device N") removed pass after pass until none is left; runtime_cards names the cards they open (another card than card 0 is an
    identity trip); each "SPARSITY {...}" line must parse whole and carry its command's own fields, else it is NOT read;
  - the counted launch (E222.md 7, E218's): an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz.
    python3 -I -B tools/claims-v3/e222/e222_common.py        the self-check (E222-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e222.json")
PTS_F = os.path.join(HERE, "points-e222.json")
KJ_F = os.path.join(HERE, "kernel-e222.json")
# the frozen forecasts the doubles read (E222.md sections 0 and 5), at their pin: MM1-v3.2's rows of forecast-e222.csv (every point, the tie t01
# and the two smokes; frozen by FROZEN.txt 13:50:25 PST Fri 20 Nov 2026, posted 13:51:12, and by the registration's commit)
FC = ("tools/claims-v3/e222/forecast-e222.csv", "223f943e32c01544063de6b1dc925712e0701ba43f4c99f97ff622e8c5b835cb")
FC_MODEL = "MM1-v3.2"
# the tie and the two smokes are E218's registered records (E222.md 3), read from E218's points-e218.json at its registered sha256
E218_PTS = ("tools/claims-v3/e218/points-e218.json", "9a5f252f58a25db0b3fe0e78fdc699e597c607442e8090b85e8c795e5da606b3")
EXTRA_IDS = ("s01", "s03", "t01")
FMTS = ("fp32", "fp16", "int8")

# ---- the builds (build_e222.sh writes them on aifoundry3, from the box tree's root)
BUILD_DIR = "build/e222rgm"
BUILD_REC = BUILD_DIR + "/BUILD-e222.json"
GUARD = "tools/claims-v3/e222/ettelem_guard_e222.sh"
BUILDER = "build_e222.sh"
KERNELS = {     # kernel-e222.json, repeated here and checked against it by the self-check (rgm211: its host's tree; kernel-e222.json "rgm211_host")
    "rgm136": {"src": "tools/claims-v3/e136/rgm136", "dir": BUILD_DIR + "/rgm136",
               "elf": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
               "text": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
               "load": "649d40793e459e51db9a590ca90dd1363da3a00398f98938c3ef6e190514e2b7"},
    "rgm211": {"src": "tools/claims-v3/e211/rgm211", "dir": BUILD_DIR + "/rgm211",
               "elf": "00402801a1a53a9330898ef023297d8967a2c655472a40e0f1cd65dea04f09ae",
               "text": "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069",
               "load": "1351a569e4a200cb4cd916c4c6af822b45ce6e1cac9b7aa8b71c945a1f5bd847"},
}
KJ_KEY = {"rgm136": "rgm136", "rgm211": "rgm211_host"}    # each build's entry in kernel-e222.json > kernels
# THE TWO ARM FAMILIES, keyed by the registration's "loop" (kernel-e222.json > arm_families): the host, the ELF, the arm's prefix as the host
# spells it, and the walk rgm211's host must report on every launch (None: rgm136's host prints no walk)
LOOPS = {
    "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "prefix": "gemmL", "walk": None},
    "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "prefix": "gemmLnc", "walk": "mn"},
}


def host_rel(kind):
    return KERNELS[kind]["dir"] + "/host/sparsity_host"


def elf_rel(kind):
    return KERNELS[kind]["dir"] + "/kernel/sparsity.elf"


# ---- the arm (E222.md 6; plan-e222.json card; the stop and gate numbers checked against the plan's words by the self-check). One arm, "A":
# the runbook's and the runner's word for it, as in E215 arm A's kit, so every RB_OUT file and every session folder carries it
ARMS = {
    "A": {"box": "aifoundry3", "card": "aifoundry3 card 0", "card_index": "0", "lock": "/run/lock/etsoc-shire0.lock", "et_devices": None,
          "tree": "aifoundry", "data_dir": "aifoundry3", "jobs": "a3",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "16037641ab75bdbe1209f323641e269c9b897468091243173bfaaaf0b21686e2",   # E206's, E207's, E211's, E213 arm A's, E215 arm A's
          "config": {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 60.0, "gate_add_c": 4.0, "stops": (70.0, 3, 70.0),
          "rule_s": 70 * 60.0, "cap_s": 80 * 60.0,
          "smoke": ("s01", "s03"), "opening": ("s01",), "lnc_smoke": ("s03",), "tie": "t01",
          "loops": ("rgm136 gemmL", "rgm136 gemmLnc")},
}

# ---- THE FAMILY SMOKE (E222.md 3 names E218's smoke s03 "right before the G block"; its own stop path is E218's, E218.md 3: "s03 ... family G's
# own smoke and stop path", E213's Amendment A1 form, which E222's frozen scorer's reader reads: score_e220.read_a): a smoke point whose failure that is
# not the session's (a1_session_level) drops its family - the family's points never start (NO DATA) - instead of stopping the session. The
# session's gate (any failure: the smoke gate, no run) is SESSION_SMOKE, the frozen scorer's (score_e222.SESSION_SMOKE).
FAMILY_SMOKE = {"s03": "rgm136 gemmLnc"}
SESSION_SMOKE = ("s01",)
LNC_BLOCKS = ("G-pass1", "G-pass2")
LNC_SMOKE_BLOCK = "G-smoke"
RULES_F = os.path.join(HERE, "rules-e222.json")
N_LNC_POINTS = 15               # the G block's points: R's rg01, T-G2 wn01-wn07, G3 k01-k07 (each once in G-pass1)
N_G3_POINTS = 7                 # G3 k01-k07 again in G-pass2 (E222.md 6: "then the G3 points again in reverse")
# the registered blocks (plan-e222.json > order > runs > block) and the kit's names for them (the run folders' names: no space)
BLOCK_KIT = {"tie": "tie", "pass1": "pass1", "pass2": "pass2", "G block": "G-pass1", "G block reversed (G3 only)": "G-pass2"}


def a1_session_level(proc, id_ok, sampler_live=True):
    """A family smoke's failures that still stop the session (E213's Amendment A1 form, E222.md 3, E215's reading): '' when none, else why. K1 (a
    launch that did not finish), a HUNG host (alive past its timeout's TERM), a launch timeout (rc 124: the host ended by its timeout's TERM), the
    host not shown on the card (its stderr, its open files, or a runtime line naming another card), the sampler not live after the process (its
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


# ---- every file a point's --values names, at the sha256 the registration records (points-e222.json > tile_sha256) and its manifest records
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
}
TILE_MANIFEST = "tools/claims-v3/kinds/kinds.json"
# the manifest each tile is checked against: (the tiles' folder, the manifest's path, its form, the prefix its lines name the tile under)
TILE_MANIFESTS = (
    ("tools/claims-v3/kinds/tiles/", TILE_MANIFEST, "kinds.json", ""),
)


def manifest_sha(tile):
    """The sha256 a tile's own manifest records (TILE_MANIFESTS), or None when it records none."""
    for pre, man, form, base in TILE_MANIFESTS:
        if not tile.startswith(pre):
            continue
        p = os.path.join(REPO, man)
        if form == "kinds.json":
            kk = load(p)["kinds"]
            fmt, name = tile.split("/")[-2], os.path.basename(tile)[:-4]
            return ((kk.get(fmt) or {}).get(name) or {}).get("sha256")
        return None
    return None


# ---- the session's timing: the registration's numbers (E222.md 3 and 6; plan-e222.json), and the kit's own (marked)
REST_READ_S = 10.0          # E222.md 6, a run: "its die gate, 10 s at rest, one host process ... a 4 s tail" (p_rest = the median of its last 5 s)
REST_WINDOW_S = 5.0         # the reducer's p_rest: the last 5 s of the run's rest (E215's form, which E222.md 7 adopts)
SMOKE_REST_S = 30.0         # the kit's (E206's, E211's and E215's smoke form): 30 s at rest first, the session's rest reading; the die gates are formed from it
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # E222.md 3: "one checked process each"; the 2 s process E146's, E190's, E206's, E211's and E215's smoke ran
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E222.md 6: "'--seconds 6 --budget 7.5'"
TAIL_S = 4.0                # E222.md 6: "a 4 s tail"
GATE_WAIT_S = 300.0         # plan-e222.json die_gate: "waited at most 300 s, else that run is NO DATA"
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's, E211's, E215's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz)
HOST_TIMEOUT_S = 10         # `timeout 10` on every device-opening process (plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # the longest a run can last once its gate has passed (28 s)
SMOKE_CYC = (200.0, 4000.0)  # E222.md 7, R0: "the smoke's counter mean 200-4,000 cycles an op" (the runner's smoke gate reads R0's band)
MHZ_BAND = (590.0, 610.0)   # E222.md 7: S6's band, and the kernel clock a counted launch is in
LINE_W = 67.0               # plan-e222.json drop_line_W: no point whose planning peak reaches it runs (none does: the self-check reads it)
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # a runtime's line, on a host's or a reader's stdout (aifoundry1's form; read on any box)
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


_PTS = {}


def _e218_extra():
    """E218's registered tie and smokes (E222.md 3), from points-e218.json at its pin: {id: record}, the role E218 gave them."""
    with open(os.path.join(REPO, E218_PTS[0]), "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != E218_PTS[1]:
        raise ValueError(f"{E218_PTS[0]} is not E218's registered file {E218_PTS[1][:12]}")
    R8 = json.loads(raw.decode())
    return {q["id"]: q for q in R8["smoke"] + [R8["tie"]] if q["id"] in EXTRA_IDS}


def registration():
    """points-e222.json as registered (its points), with "smoke" and "tie" added from E218's registered records (E222.md 3), and plan-e222.json's
    order (plan > order > runs) as "order"."""
    if "r" not in _PTS:
        R = dict(load(PTS_F))
        ex = _e218_extra()
        R["smoke"] = [ex["s01"], ex["s03"]]
        R["tie"] = ex["t01"]
        R["order"] = plan()["order"]
        _PTS["r"] = R
    return _PTS["r"]


def points():
    """points-e222.json in the kit's arm form (E215's and E218's): {"arms": {"A": {"points", "references" (none), "smoke", "tie", "order":
    {"sequence", "opening_smoke", "gemmLnc_smoke"}}}}; the sequence is the registered order (plan-e222.json > order > runs) without its first
    entry (the opening smoke s01, the runner's own), each entry {"n" (its place in the kit's sequence, 1..121), "reg_n" (its registered place,
    2..122), "block" (the kit's name: tie, pass1, pass2, G-smoke, G-pass1, G-pass2), "reg_block" (the registered name), "id", "name"}."""
    if "p" not in _PTS:
        R = registration()
        by = {q["id"]: q for q in R["points"] + R["smoke"] + [R["tie"]]}
        runs = R["order"]["runs"]
        seq = []
        for i, x in enumerate(runs[1:], start=1):
            b = LNC_SMOKE_BLOCK if (x["block"] == "smoke" and x["id"] in FAMILY_SMOKE) else BLOCK_KIT.get(x["block"], "UNKNOWN:" + x["block"])
            seq.append({"n": i, "reg_n": x["n"], "block": b, "reg_block": x["block"], "id": x["id"], "name": (by.get(x["id"]) or {}).get("name", x["id"])})
        _PTS["p"] = {"arms": {"A": {"points": R["points"], "references": [], "smoke": R["smoke"], "tie": R["tie"],
                                    "order": {"sequence": seq, "opening_smoke": [runs[0]["id"]] if runs and runs[0]["block"] == "smoke" else [],
                                              "gemmLnc_smoke": [x["id"] for x in seq if x["block"] == LNC_SMOKE_BLOCK]}}}}
    return _PTS["p"]


def arm_points(arm):
    """Every point of the arm the runner may start: its points, its smoke and its tie."""
    A = points()["arms"][arm]
    return A["points"] + A.get("references", []) + A["smoke"] + [A["tie"]]


def point(pid):
    """A point of points-e222.json by its id (T: wl01-wl08, wp01a-wp05b, wn01-wn07, wn01t-wn07t; L3b b01-b10; Y3 q01a-q05b; G3 k01-k07; G3t
    k01t-k07t; R ry01a, ry01b, rg01, rg01t), or E218's smoke s01, s03 and tie t01."""
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
    """A point's arm family: its LOOP ('rgm136 gemmL', 'rgm136 gemmLnc'), never its arm token."""
    return point(pid)["loop"]


def fam_host(fam):
    return LOOPS[fam]["host"]


def fam_elf(fam):
    return LOOPS[fam]["elf"]


def rgm211_host(pid):
    return LOOPS[family(pid)]["host"] == "rgm211"


_FC = {}


def _pinned_rows(rel, pin):
    with open(os.path.join(REPO, rel), "rb") as f:
        raw = f.read()
    if hashlib.sha256(raw).hexdigest() != pin:
        raise ValueError(f"{rel} is not E222's frozen file {pin[:12]}")
    return list(csv.DictReader(raw.decode().splitlines()))


def forecast_rows(arm):
    """MM1-v3.2's frozen forecast rows by point id, in one form {id: {cycles_per_op_wall, cycles_per_op_mean, seconds_per_gemm, W_over_idle}}
    (FC at its pin, its MM1-v3.2 rows; every point and the tie t01; the two smokes keep the doubles' toy figures, as in E218's kit; else
    ValueError: the box check's harness read refuses first)."""
    if arm not in _FC:
        if arm not in ARMS:
            raise KeyError(arm)
        out = {}
        A = points()["arms"][arm]
        ids = {q["id"] for q in A["points"]} | {A["tie"]["id"]}
        for r in _pinned_rows(*FC):
            if r.get("model") == FC_MODEL and r["id"] in ids:
                out[r["id"]] = {k: r[k] for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle")}
        _FC[arm] = out
    return _FC[arm]


def arm_of_safe(pid):
    try:
        return arm_of(pid)
    except KeyError:
        return None


def double_of(pid):
    """The doubles' toy figures at a point (desk numbers of the doubles, never a datum): MM1-v3.2's frozen forecast at the point where it has one
    (cycles an op on the wall and the counter's mean, seconds a GEMM, W over idle, ops a minion a GEMM: the points and the tie); for the smoke,
    which no forecast prices, the ops from the point and the toy 900 / 800 cycles an op and 20 W over idle."""
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
    """The arm's stop lines under the watcher's keys (ARMS; the self-check reads them against plan-e222.json's words)."""
    if arm not in ARMS:
        raise KeyError(arm)
    b, n, d = ARMS[arm]["stops"]
    return {"board_cap_w": float(b), "cap_consecutive": int(n), "abs_stop_c": float(d)}


def gate_c(arm, rest_die):
    """The die gate a run starts under (plan-e222.json die_gate): min(60, rest die + 4); None with no rest die."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The registered order: [{"n", "block", "id", "name"}, ...] (points-e222.json > order > sequence_blocks, 108 entries after the opening smoke):
    the runs (blocks tie, pass1, pass2, G-pass1, G-pass2) and family G's smoke (block G-smoke, right before its block). The opening smoke s01 is
    the runner's own, first, and not in it."""
    if arm not in ARMS:
        raise KeyError(arm)
    return [{"n": x["n"], "block": x["block"], "id": x["id"], "name": x["name"]} for x in points()["arms"][arm]["order"]["sequence"]]


def is_lnc_smoke(r):
    """A sequence entry that is family G's smoke (run as a smoke, never as a run)."""
    return r.get("block") == LNC_SMOKE_BLOCK


def run_key(r):
    return f"{r['n']:03d}-{r['block']}-{r['id']}"


def host_argv(root, pid, seconds, budget, stop_file):
    """One process's command line (without `timeout 10`): the point's own host (its loop's: rgm136's for 'rgm136 gemmL', rgm211's for 'rgm136
    gemmLnc'), its registered host_args with --seconds and --budget set to the process form, then the kit's --kernel (rgm136's ELF for both
    families) and --stop-file."""
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
    """The counted launch: an fma launch, launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz."""
    if L.get("test") != "fma" or not isinstance(L.get("launch"), int) or L["launch"] < 0 or not L.get("ok") or \
            (L.get("wall_s") or 0) < 0.1 or not L.get("passes"):
        return False
    f = kclock(L)
    return f is not None and MHZ_BAND[0] <= f <= MHZ_BAND[1]


def walk_check(fam, fma, chk):
    """THE WALK CHECK's reading for one process (E211's, by loop): (ok, words, detail). rgm211's host ('rgm136 gemmLnc': mn): every launch record
    carries walk == the family's and walk_ok true, and the last check record walk == the family's and walk_launches_bad 0; a process with no launch
    record or no check record fails. rgm136's host ('rgm136 gemmL') prints no walk."""
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
    """THE KERNEL STOPS (E211's, the kit's reading for every process of rgm211's host: 'rgm136 gemmLnc'): a check of C wrong (or missing), a tensor
    error, the walk check failed, a launch timeout (K1, or the process ended by its `timeout`'s TERM) or any launch not ok, or the process's exit
    not 0: '' when none, else why (the session stops: nothing more that day). The identity gate is the runner's, before the process starts. A
    'rgm136 gemmL' process (rgm136 on its own host, run FULL on this card by E206, E207, E213 and E215) keeps E206's rules (a failed process
    flagged; two in a row stop)."""
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
    """The start config the arm's line rests on (plan-e222.json config_gate), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (plan-e222.json > card > stops; E206's watcher, line for line): the shires' mean at or above abs_stop_c
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
    p, pts, R = plan(), points(), registration()
    arm = "A"
    a, pc = ARMS[arm], p["card"]
    # the arm against the plan's words (plan-e222.json > card, rule_min, cap_min, drop_line_W, the order)
    st = stops_of(arm)
    if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (70.0, 3, 70.0):
        bad.append(f"the stops {st}")
    if "strictly above 70 W on 3 samples in a row" not in pc["live_stops"] or "at or above 70 C" not in pc["live_stops"] or \
            "never a kill" not in pc["live_stops"] or float(p["stop_W"]) != 70.0 or float(p["die_stop_C"]) != 70.0:
        bad.append(f"the plan's stop words {pc['live_stops'][:80]!r}")
    if not pc["die_gate"].startswith("min(60, the session's rest die + 4) C, waited at most 300 s") or gate_c(arm, 100.0) != 60.0 or \
            gate_c(arm, 40.0) != 44.0:
        bad.append(f"the gate {pc['die_gate']!r}")
    c = a["config"]
    cfg_txt = f"TDP {c['tdp_w']} W, temperature threshold {c['temp_threshold_c']} C, minion {c['minion_mhz']} MHz"
    if not pc["start_config_gate"].startswith(cfg_txt) or cfg_txt != "TDP 0 W, temperature threshold 65 C, minion 600 MHz":
        bad.append(f"the start config {pc['start_config_gate']!r}")
    if not pc["card"].startswith(a["card"]) or a["lock"] not in pc["card"] or not pc["box"].startswith(a["box"]) or p.get("experiment") != "E222":
        bad.append("the card, box or lock")
    if (p["rule_min"], p["cap_min"]) != (a["rule_s"] / 60, a["cap_s"] / 60) or (p["rule_min"], p["cap_min"]) != (70.0, 80.0):
        bad.append("the card-time rule and cap")
    if float(p["drop_line_W"]) != LINE_W or p.get("thinned") or float(p["highest_PP32"][0]) >= LINE_W or \
            any(v is not None and v >= LINE_W for v in p["every_point_PP32_W"].values()):
        bad.append(f"a point's planning peak at or over the {LINE_W:g} W line")
    if "10 s at rest" not in pc["run_form"] or "'--seconds 6 --budget 7.5'" not in pc["run_form"] or "a 4 s tail" not in pc["run_form"] or \
            "plain 'timeout 10'" not in pc["run_form"]:
        bad.append(f"the run's form {pc['run_form'][:80]!r}")
    A = pts["arms"][arm]
    seq = sequence(arm)
    runs = [r for r in seq if not is_lnc_smoke(r)]
    reg = R["order"]["runs"]
    if reg[0] != {"block": "smoke", "id": "s01", "n": 1} or len(reg) != len(seq) + 1 or [x["n"] for x in reg] != list(range(1, len(reg) + 1)):
        bad.append(f"the registered order's first entry {reg[:1]} is not the opening smoke s01, or its places are not 1..{len(reg)}")
    full = points()["arms"][arm]["order"]["sequence"]
    if [r["n"] for r in seq] != list(range(1, len(seq) + 1)) or [x["reg_n"] for x in full] != list(range(2, len(seq) + 2)) or \
            any(x["block"].startswith("UNKNOWN") for x in full):
        bad.append("the kit's places are not 1..121 with the registered places 2..122, or a registered block is unknown")
    if len(runs) != p["n_runs_scored_and_ties"] or len(runs) != 120 or int(p["n_smoke"]) != 2:
        bad.append(f"the order's runs ({len(runs)}) are not the plan's {p['n_runs_scored_and_ties']}")
    ti = [i for i, r in enumerate(seq) if r["block"] == "tie"]
    if len(ti) != 3 or ti[0] != 0 or any(seq[i]["id"] != a["tie"] for i in ti):
        bad.append("the ties")
    # THE G BLOCK LAST (E222.md 6): after the third tie, its family smoke s03, then its runs, nothing after; every gemmLnc run there
    smi = [i for i, r in enumerate(seq) if is_lnc_smoke(r)]
    lnc = [r for r in seq if r["block"] in LNC_BLOCKS]
    if [seq[i]["id"] for i in smi] != list(a["lnc_smoke"]) or (ti and smi != [ti[-1] + 1]) or (smi and seq[smi[0] + 1:] != lnc) or \
            len(lnc) != N_LNC_POINTS + N_G3_POINTS:
        bad.append(f"the G block is not the tie, its smoke {a['lnc_smoke']}, then its {N_LNC_POINTS + N_G3_POINTS} runs, last")
    for r in runs:
        if r["block"] != "tie" and ((point(r["id"])["loop"] == "rgm136 gemmLnc") != (r["block"] in LNC_BLOCKS)):
            bad.append(f"run {r['n']} {r['id']} ({r['block']}) breaks 'the G block LAST'")
            break
    o = R["order"]
    g1 = [r["id"] for r in lnc if r["block"] == "G-pass1"]
    g2 = [r["id"] for r in lnc if r["block"] == "G-pass2"]
    p1 = [r["id"] for r in runs if r["block"] == "pass1"]
    p2 = [r["id"] for r in runs if r["block"] == "pass2"]
    if g1 != o["G_block"] or g2 != o["G_block_reversed"] or p1 != o["pass1"] or p2 != o["pass2"]:
        bad.append("the sequence's blocks are not the registered pass1, pass2, G_block and G_block_reversed")
    # E222.md 6's words: pass 1 every non-gemmLnc point once; pass 2 the L3b, Y3, T-L3, T-Y2 and R-Y points, pass 1's order reversed; the G block
    # every gemmLnc point once (rg01, T-G2, G3) by PP32 ascending; then the G3 points again in reverse
    by = {q["id"]: q for q in A["points"]}
    grp = {pid: (q["subfamily"] if q["family"] in ("T", "R") else q["family"]) for pid, q in by.items()}
    nonlnc = sorted(pid for pid, q in by.items() if q["loop"] != "rgm136 gemmLnc")
    if sorted(p1) != nonlnc or len(p1) != len(set(p1)):
        bad.append("pass 1 is not every non-gemmLnc point once")
    if p2 != [x for x in reversed(p1) if grp[x] in ("L3b", "Y3", "T-L3", "T-Y2", "R-Y")] or len(p2) != 40:
        bad.append("pass 2 is not the L3b, Y3, T-L3, T-Y2 and R-Y points in pass 1's order reversed")
    lncp = sorted(pid for pid, q in by.items() if q["loop"] == "rgm136 gemmLnc")
    pp = p["every_point_PP32_W"]
    if sorted(g1) != lncp or len(g1) != N_LNC_POINTS or any(pp[g1[i]] > pp[g1[i + 1]] for i in range(len(g1) - 1)):
        bad.append("the G block's first pass is not every gemmLnc point once by PP32 ascending")
    if g2 != [x for x in reversed(g1) if grp[x] == "G3"] or len(g2) != N_G3_POINTS:
        bad.append("the G block's second pass is not the G3 points again in reverse")
    ids = {r["id"] for r in runs if r["block"] != "tie"}
    if ids != set(by) or len(A["points"]) != 70 or R["counts"] != {"G3": 7, "G3t": 7, "L3b": 10, "R": 4, "T": 32, "Y3": 10} or \
            R["t_counts"] != {"T-G2": 7, "T-G2t": 7, "T-L3": 8, "T-Y2": 10} or R.get("t_dropped"):
        bad.append(f"the runs' points are not the registered 70 ({len(A['points'])}; {R['counts']})")
    twice = {pid for pid in by if grp[pid] in ("L3b", "Y3", "T-L3", "T-Y2", "R-Y", "G3")}
    if any(sum(1 for r in runs if r["id"] == pid) != (2 if pid in twice else 1) for pid in by):
        bad.append("a registered point does not run its registered number of times (twice: L3b, Y3, T-L3, T-Y2, R-Y, G3; once: the rest)")
    if tuple(q["id"] for q in A["smoke"]) != a["smoke"] or A["tie"]["id"] != a["tie"] or \
            tuple(A["order"]["opening_smoke"]) != a["opening"] or tuple(A["order"]["gemmLnc_smoke"]) != a["lnc_smoke"]:
        bad.append(f"the smoke {[q['id'] for q in A['smoke']]}, its opening and G smoke, or the tie")
    # the smoke and the tie are E218's records, their tokens and formats the registration's extra rows
    ex = R["extra_rows"]
    for q in A["smoke"] + [A["tie"]]:
        x = ex.get(q["id"]) or {}
        if (q["arm"], q["format"]) != (x.get("token"), x.get("fmt")) or q["card"] != a["card"] or q.get("kernel") != "rgm136":
            bad.append(f"{q['id']}: E218's record ({q['arm']} {q['format']}) is not E222's extra row ({x.get('token')} {x.get('fmt')})")
    # THE FAMILY SMOKE: every smoke but the session's gate is its family's own; every family with points but rgm136's gemmL has one
    for q in A["smoke"]:
        if q["id"] in SESSION_SMOKE:
            if q["loop"] != "rgm136 gemmL" or q["id"] in FAMILY_SMOKE:
                bad.append(f"the session's smoke {q['id']} ({q['loop']})")
        elif FAMILY_SMOKE.get(q["id"]) != q["loop"]:
            bad.append(f"the family smoke {q['id']} ({q['loop']}) is not FAMILY_SMOKE's {FAMILY_SMOKE.get(q['id'])}")
        if not (q["arm"].endswith("2x2x2") and q["format"] == "fp32" and q["kind"] == "random" and q["shire_mask"] == "0xffffffff"):
            bad.append(f"the smoke {q['id']} is not a 2x2x2 fp32 random full-chip process ({q['arm']} {q['format']} {q['kind']})")
    for fam in sorted({q["loop"] for q in A["points"]}):
        if fam != "rgm136 gemmL" and not any(q["loop"] == fam and q["id"] in FAMILY_SMOKE for q in A["smoke"]):
            bad.append(f"the family {fam} has points but no family smoke")
    if not any(q["id"] in SESSION_SMOKE for q in A["smoke"]) or A["smoke"][0]["id"] not in SESSION_SMOKE:
        bad.append("the opening smoke does not start with the session's gate")
    for q in arm_points(arm):
        fam = q["loop"]
        if fam not in a["loops"] or (q["host"], q["elf"]) != (LOOPS[fam]["host"], LOOPS[fam]["elf"]):
            bad.append(f"{q['id']}: loop {fam} with host {q['host']} / ELF {q['elf']} is not its family's")
            break
        tok = q["arm"]
        pre = re.match(r"^(gemmL(?:nc|n)?)\d", tok)
        if not pre or pre.group(1) != LOOPS[fam]["prefix"]:
            bad.append(f"{q['id']}: arm {tok} is not of its loop {fam}")
            break
        if q["card"] != a["card"] or q.get("kernel") != "rgm136" or q["format"] != "fp32" or q["kind"] != "random":
            bad.append(f"{q['id']}: card {q['card']}, kernel {q.get('kernel')}, format {q['format']} or kind {q['kind']}")
            break
    byf = {f: sorted(q["id"] for q in A["points"] if q["loop"] == f) for f in a["loops"]}
    want_lnc = sorted(["rg01"] + [f"wn{i:02d}" for i in range(1, 8)] + [f"k{i:02d}" for i in range(1, 8)])
    if byf.get("rgm136 gemmLnc") != want_lnc:
        bad.append(f"the family 'rgm136 gemmLnc''s points {byf.get('rgm136 gemmLnc')}, registered rg01, wn01-wn07, k01-k07")
    # the frozen scorer's reader (score_e220.read_a at score_e222's pin) reads the G block's smoke by its id s03 (at the desk, where it is)
    sc = os.path.join(REPO, "tools", "claims-v3", "e220", "score_e220.py")
    if os.path.exists(sc) and 'r.get("point") == "s03"' not in open(sc).read():
        bad.append("the frozen scorer's reader does not name the G block's smoke s03")
    # the builds and the families against kernel-e222.json
    kj = load(KJ_F)
    k1 = kj["kernels"]["rgm136"]
    v = KERNELS["rgm136"]
    if (k1["elf_sha256"], k1["text_sha256"], k1["loadable_identity_sha256"], k1["tree"]) != (v["elf"], v["text"], v["load"], v["src"]):
        bad.append("rgm136's pins differ from kernel-e222.json")
    k2 = kj["kernels"]["rgm211_host"]
    v = KERNELS["rgm211"]
    if (k2["elf_sha256"], k2["loadable_identity_sha256"], k2["tree"]) != (v["elf"], v["load"], v["src"]):
        bad.append("rgm211's tree pins differ from kernel-e222.json's rgm211_host")
    try:
        e211 = load(os.path.join(REPO, "tools/claims-v3/e211/kernel-e211.json"))["kernels"]["rgm211"]
        if (e211["elf_sha256"], e211["text_sha256"], e211["loadable_identity_sha256"]) != (v["elf"], v["text"], v["load"]):
            bad.append("rgm211's pins differ from E211's kernel-e211.json")
    except (OSError, KeyError, ValueError):
        pass                    # not on the box (the harness syncs E222's files and the sources only): the desk's step 2 reads it
    for fam, v in LOOPS.items():
        f = kj["arm_families"].get(fam)
        if not f or (f["host"], f["elf"]) != (v["host"], v["elf"]):
            bad.append(f"the family {fam} differs from kernel-e222.json")
    if set(kj["arm_families"]) != set(LOOPS):
        bad.append("the families are not kernel-e222.json's two")
    for fam in LOOPS:
        reg_pts = sorted(kj["arm_families"][fam]["points"])
        if reg_pts != sorted(q["id"] for q in A["points"] if q["loop"] == fam):
            bad.append(f"the family {fam}'s points differ from kernel-e222.json's")
    # the frozen forecasts: at their pin, every registered point and the tie there
    try:
        rows = forecast_rows(arm)
        miss = [q["id"] for q in A["points"] + [A["tie"]] if q["id"] not in rows]
        if miss:
            bad.append(f"no frozen forecast for {miss[:5]}")
        for q in arm_points(arm):
            d = double_of(q["id"])
            if not (d["t"] > 0 and d["cyc_mean"] > 0 and d["ops"] > 0):
                bad.append(f"{q['id']}: the doubles' figures")
                break
        if abs(double_of("rg01")["cyc_wall"] - 1169.99922) > 1e-6 or abs(double_of("rg01")["W"] - 23.600548) > 1e-6:
            bad.append("the doubles' rg01 figures are not MM1-v3.2's frozen forecast")
        if abs(double_of("t01")["cyc_wall"] - 1165.72811) > 1e-6 or abs(double_of("k07")["W"] - 24.6454927) > 1e-6:
            bad.append("the doubles' t01 or k07 figures are not the registration's MM1-v3.2 rows")
        if double_of("s01")["cyc_wall"] != 900.0 or double_of("s03")["W"] != 20.0:
            bad.append("the smoke's toy figures")
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"the frozen forecasts ({type(e).__name__}: {str(e)[:80]})")
    # the argv: both families' hosts and kernel
    R32 = "tools/claims-v3/kinds/tiles/fp32/randn.bin"
    g = host_argv("/T", "rg01", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if g[:2] != ["/T/build/e222rgm/rgm211/host/sparsity_host", "--test"] or arg_of(g, "--values") != f"gemmLnc2x6x8:randn:{R32}" or \
            arg_of(g, "--shires") != "0xffffffff" or arg_of(g, "--per-shire") != "32" or arg_of(g, "--seconds") != "6" or \
            arg_of(g, "--budget") != "7.5" or arg_of(g, "--kernel") != "/T/build/e222rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(g, "--stop-file") != "/T/STOP" or "-k" in g or arg_of(g, "--seed") != "1" or arg_of(g, "--type") != "fp32":
        bad.append(f"the rgm136 gemmLnc argv {g}")
    m = host_argv("/T", "rg01t", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if m[0] != "/T/build/e222rgm/rgm136/host/sparsity_host" or arg_of(m, "--kernel") != "/T/build/e222rgm/rgm136/kernel/sparsity.elf" or \
            arg_of(m, "--values") != f"gemmL2x6x8:randn:{R32}":
        bad.append(f"the rgm136 gemmL argv {m}")
    k = host_argv("/T", "k07", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if k[0] != "/T/build/e222rgm/rgm211/host/sparsity_host" or arg_of(k, "--values") != f"gemmLnc6x5x4:randn:{R32}":
        bad.append(f"a G3 argv {k}")
    s = host_argv("/T", "s03", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp32" or \
            arg_of(s, "--kernel") != "/T/build/e222rgm/rgm136/kernel/sparsity.elf" or s[0] != "/T/build/e222rgm/rgm211/host/sparsity_host" or \
            arg_of(s, "--values") != f"gemmLnc2x2x2:randn:{R32}":
        bad.append(f"the G smoke's argv {s}")
    s1 = host_argv("/T", "s01", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if s1[0] != "/T/build/e222rgm/rgm136/host/sparsity_host" or arg_of(s1, "--values") != f"gemmL2x2x2:randn:{R32}":
        bad.append(f"the session's smoke's argv {s1}")
    mk = host_argv("/T", "ry01a", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if expect_of(mk)["shire_mask"] != "0xf000" or expect_of(mk)["minions"] != 128 or point("ry01a")["minions"] != 128:
        bad.append(f"a subset's argv {mk}")
    q2 = host_argv("/T", "q01a", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if expect_of(q2)["shire_mask"] != "0xa0000000" or expect_of(q2)["minions"] != 64:
        bad.append(f"a Y3 subset's argv {q2}")
    if expect_of(g) != {"arm": "gemmLnc2x6x8", "type": "fp32", "values": f"gemmLnc2x6x8:randn:{R32}", "shire_mask": "0xffffffff", "minions": 1024}:
        bad.append(f"expect_of {expect_of(g)}")
    for q in arm_points(arm):
        e = expect_of(host_argv("/T", q["id"], 6, 7.5, "/S"))
        if (int(e["shire_mask"], 16), e["minions"], e["arm"], e["type"]) != (int(q["shire_mask"], 16), q["minions"], q["arm"], q["format"]):
            bad.append(f"{q['id']}: expect_of {e} against the point")
            break
        if q["host_args"].count("--seconds") != 1 or q["host_args"].count("--budget") != 1 or "--kernel" in q["host_args"] or \
                "--stop-file" in q["host_args"]:
            bad.append(f"{q['id']}: its host_args carry the kit's flags or not one --seconds and --budget")
            break
    # the tiles: every file a point names, at the registration's tile_sha256, its manifest's sha256, and (where the file is) its bytes
    named = {}
    for q in arm_points(arm):
        files = arg_of(q["host_args"], "--values").split(":", 2)[2].split(",")
        ts = q.get("tile_sha256") or {}
        for f in files:
            named[f] = ts.get(f) if isinstance(ts, dict) else ts
    if set(named) != set(TILES) or any(named[f] != TILES[f] for f in named):
        bad.append(f"TILES is not the points' files ({len(named)} named, {len(TILES)} pinned)")
    try:
        for f, h in TILES.items():
            ms = manifest_sha(f)
            if ms != h:
                bad.append(f"{f}: pinned {h[:12]}, its manifest {str(ms)[:12]}")
            fp = os.path.join(REPO, f)
            if os.path.exists(fp) and hashlib.sha256(open(fp, "rb").read()).hexdigest() != h:
                bad.append(f"{f}: its bytes are not {h[:12]}")
    except (OSError, KeyError, ValueError, TypeError) as e:
        bad.append(f"a tile manifest could not be read ({type(e).__name__})")
    # the walk check's reading, the two families
    rm = {"test": "fma", "walk": "mn", "walk_tagged": 0, "walk_ok": True}
    cm = {"test": "check", "walk": "mn", "walk_launches_bad": 0}
    rn = dict(rm, walk="nm", walk_tagged=1024)
    if not walk_check("rgm136 gemmLnc", [rm, rm], [cm])[0] or walk_check("rgm136 gemmLnc", [rm, dict(rm, walk_ok=False)], [cm])[0] or \
            walk_check("rgm136 gemmLnc", [rn], [cm])[0] or walk_check("rgm136 gemmLnc", [rm], [dict(cm, walk_launches_bad=1)])[0] or \
            walk_check("rgm136 gemmLnc", [rm], [])[0] or walk_check("rgm136 gemmLnc", [], [cm])[0] or \
            walk_check("rgm136 gemmLnc", [dict(rm, walk_ok=None)], [cm])[0] or walk_check("rgm136 gemmLnc", [rm], [dict(cm, walk="nm")])[0] or \
            not walk_check("rgm136 gemmL", [], [])[0] or not walk_check("rgm136 gemmL", [rn], [])[0]:
        bad.append("the walk check's reading")
    good = {"check": "approx", "check_ok": True, "tensor_errors": 0, "walk_ok": True, "k1": False, "rc": 0, "launches_ok": True}
    if kernel_stop("rgm136 gemmLnc", good) or not kernel_stop("rgm136 gemmLnc", dict(good, check="wrong", check_ok=False)) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, walk_ok=False, walk_words="x")) or not kernel_stop("rgm136 gemmLnc", dict(good, tensor_errors=1)) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, rc=124)) or not kernel_stop("rgm136 gemmLnc", dict(good, k1=True)) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, rc=1)) or kernel_stop("rgm136 gemmL", dict(good, rc=1, check="wrong")) or \
            not kernel_stop("rgm136 gemmLnc", dict(good, launches_ok=False)):
        bad.append("the kernel stops")
    # the stop lines: the watcher's semantics, the latch reading (E206's cases, the arm's lines)
    def smp(bw=40.0, die=50, high=87):
        return {"t_ms": 1, "board_w": bw, "temp_c": {"minshire": [die, 46, high]}}
    st = Stops(**stops_of(arm))
    r = [st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(70.0)), st.feed(smp(71)), st.feed(smp(71)), st.feed(smp(71))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or "") or "above 70 W" not in st.stop:
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(**stops_of(arm))
    if [st.feed(smp(die=69, high=87)) for _ in range(5)] != [[]] * 5 or st.feed(smp(die=70, high=87)) != ["stop"] or "shires' mean" not in st.stop:
        bad.append("the die line: the 87 C latch must not trip it, the mean at 70 C must")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=88)) != ["stop"] or "latch rose" not in st.stop:
        bad.append("the latch rising past its session value")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=50)) != [] or st.feed(smp(die=60, high=71)) != ["stop"]:
        bad.append("the latch after a drop (a statistics reset by another) rising past the line")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=61)) != [] or st.feed(smp(die=60, high=69)) != [] or st.stop:
        bad.append("the latch rising below the line tripped")
    st = Stops(**stops_of(arm))       # a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 73}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 73}) != [] or \
            st.feed({"t_ms": 4, "board_w": 73}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(**stops_of(arm))       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 69.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
        bad.append("a reading under the line between over-line readings did not break the row")
    # the counted launch
    L = {"test": "fma", "launch": 0, "ok": True, "wall_s": 0.5, "passes": 1, "cycles_max": 300e6}
    if not counted(L) or counted(dict(L, cycles_max=400e6)) or counted(dict(L, launch=-1)) or counted(dict(L, launch=-3)) or \
            counted(dict(L, ok=False)) or counted(dict(L, wall_s=0.05, cycles_max=30e6)) or counted(dict(L, passes=0)) or counted(dict(L, test="check")):
        bad.append("the counted launch")
    # the records: runtime lines inside a record (rgm211's host's form), a cut record, records of another command
    rec = {"test": "fma", "arm": "gemmLnc2x6x8", "gen": "randn", "type": "fp32", "pattern": "none",
           "values": f"gemmLnc2x6x8:randn:{R32}", "b_stream": 0, "minions": 1024, "shire_mask": "0xffffffff",
           "iters": 6144, "passes": 1, "launch": 0, "cycles_max": 300000000, "cycles_per_op": 1157.3, "wall_s": 0.5, "walk": "mn",
           "walk_tagged": 0, "walk_ok": True, "result": "unchecked", "ok": True}
    line = "SPARSITY " + json.dumps(rec, separators=(",", ":"))
    for k in range(0, len(line) + 1, 7):
        f_, c_, inf = host_records(line[:k] + "Opening device 0\n" + line[k:] + "\n", g)
        if f_ != [rec] or inf["runtime_lines"] != ["Opening device 0"]:
            bad.append(f"a runtime line at offset {k} of a record")
            break
    for k in range(0, len(line) + 1, 11):      # a runtime line printed INSIDE another runtime line, the pair inside a record
        for j in (0, 3, 9, len("Opening device 0")):
            outer = "Opening device 0\n"
            pair = outer[:j] + "Opening device 1\n" + outer[j:]
            f_, c_, inf = host_records(line[:k] + pair + line[k:] + "\n", g)
            if f_ != [rec] or sorted(inf["runtime_lines"]) != ["Opening device 0", "Opening device 1"] or inf["unparsed"]:
                bad.append(f"two nested runtime lines (the inner at {j}) at offset {k} of a record")
                break
        else:
            continue
        break
    if runtime_cards(["Opening device 1", "Opening device 0", "x"]) != ["1", "0"] or runtime_cards([]) != []:
        bad.append("runtime_cards")
    f_, c_, inf = host_records(line[:40] + "\n", g)
    if f_ or inf["unparsed"] != 1:
        bad.append("a cut record was read")
    f_, c_, inf = host_records(line.replace('"0xffffffff"', '"0xf"') + "\n", g)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another mask was read")
    f_, c_, inf = host_records(line.replace('"gemmLnc2x6x8"', '"gemmL2x6x8"', 1) + "\n", g)
    if f_ or len(inf["mismatched"]) != 1:
        bad.append("a record of another arm token was read")
    if config_json("Opening device 0\n" + '{"tdp_w":0,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":0,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 523}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 70, "minion_mhz": 600}) \
            or config_ok("B", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}):
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
    sq = sequence("A")
    if family("rg01") != "rgm136 gemmLnc" or family("rg01t") != "rgm136 gemmL" or not rgm211_host("k07") or rgm211_host("ry01a") or \
            arm_of("t01") != "A" or family("s01") != "rgm136 gemmL" or family("s03") != "rgm136 gemmLnc" or not rgm211_host("s03") or \
            rgm211_host("wl01") or not rgm211_host("wn04") or rgm211_host("wn04t") or not is_lnc_smoke({"block": "G-smoke"}) or \
            is_lnc_smoke({"block": "pass1"}) or run_key(sq[0]) != "001-tie-t01" or \
            run_key([r for r in sq if is_lnc_smoke(r)][0]) != "099-G-smoke-s03" or run_key(sq[-1]) != "121-G-pass2-k01" or \
            run_key(sq[99]) != "100-G-pass1-wn01":
        bad.append("the family, host, arm and run-key lookups")
    for notapoint in ("g01", "y01a", "f01", "g07t"):
        try:
            point(notapoint)
            bad.append(f"{notapoint} (E218's id) is a point of E222")
        except KeyError:
            pass
    sl = (a1_session_level({"k1": True, "rc": 1}, True), a1_session_level({"rc": 124}, True), a1_session_level({"hung": True, "rc": None}, True),
          a1_session_level({"rc": 0}, False), a1_session_level({"rc": 0}, True, sampler_live=False),
          a1_session_level({"rc": 1, "check": "wrong"}, True), a1_session_level({"rc": 0}, True))
    if not all(sl[:5]) or any(sl[5:]):
        bad.append(f"A1's session-level reading {sl}")
    return bad

if __name__ == "__main__":
    import sys
    b = selfcheck()
    print("E222-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
