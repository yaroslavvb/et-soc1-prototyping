#!/usr/bin/env python3
"""E220's kit, ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): what arm A's box runner, the doubles, the reducer, the
collector and the desk tests share, for E220's ARM A, aifoundry1 card 1 at its 600 MHz as found. E218's kit form (tools/claims-v3/e218/
e218_common.py, landed in 5582edfc, which ran E218 FULL on aifoundry3 card 0: 107 of 107 runs, the opening smoke s01, the stop-path test and
the G block's smoke s03 in its place, data b445b0f5), with E215 ARM B's identity for aifoundry1 card 1 (tools/claims-v3/e215/e215_common.py,
landed in 8bde0182, whose arm B ran E215 FULL on this card: 71 of 71 runs, data 4f648f24) in place of aifoundry3's. Python's own modules only:
it runs on aifoundry1 under the system python3 (3.12.3) and at the desk under /usr/bin/python3 -I -B (3.12.3).

It reads the registration's files and never changes them: points-e220.json (every point's host arguments, its loop, host, ELF; arm A's 84),
plan-e220.json (arm A's card, clock, config, drop line, stops, die gate, card time, and THE ORDER: arms > A > runs, 114 entries - the opening
smoke s01, the tie, pass 1, the tie, pass 2, the tie, the G block's smoke s03, the G block), kernel-e220.json (the kernel's pins and the two arm
families), and the frozen forecasts the doubles drive their toy card with (forecast-e220.csv's MM1-v3.2 rows at 600.0 MHz, by point id, at its
sha256: the registration's freeze line), and the kit's own timeout table (desk/timeouts-e220.json, at its sha256). It adds:
  - THE ARM'S IDENTITY (E220.md 6, arm A): aifoundry1 card 1 (the card's nodes /dev/et1_*, the lock etsoc-shire1.lock, ET_DEVICES=1 on every
    device process, the box tree ~/nekko, the lab's card-1 reader build/ettelem/ettelem at 8008f96f..., E206 arm B's, E213 arm B's and E215 arm
    B's pin); the start config gate (TDP 65 W / 65 C / 600 MHz, read as found, nothing set; minion_mv below 510: the identity module) and the clock
    band (590-610 MHz); nothing on card 0 (aifoundry1 has two cards: one session of ours on the box at a time);
  - THE TWO BUILDS on the box (kernel-e220.json): rgm136 from tools/claims-v3/e136/rgm136 (unchanged: the ELF every E220 process runs) into
    build/e220argm/rgm136, and rgm211 from tools/claims-v3/e211/rgm211 (E211's, unchanged: ITS HOST runs rgm136's ELF for the gemmLnc branch) into
    build/e220argm/rgm211 (new folders of ours); THE KERNEL GATE on rgm136's ELF at THE WHOLE ELF (E215 arm B's gate words on aifoundry1: "the
    whole ELF and its .text, the pinned ones"; E213 arm B's and E215 arm B's builds on aifoundry1 read the whole ELF the pin) and THE TREE GATE on
    rgm211's ELF (its whole ELF at kernel-e220.json's rgm211_host pins: the tree the host comes from is E211's; that ELF runs no E220 point);
    the hosts read by their behaviour, and "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES" (E215 arm B's build reading);
  - THE TWO ARM FAMILIES (kernel-e220.json > arm_families; each point's "loop"): "rgm136 gemmL" runs rgm136's ELF on rgm136's host (XGt, XY, XF,
    L3, Y2, G2t, the tie t01 and the session's smoke s01); "rgm136 gemmLnc" rgm136's ELF on rgm211's host (XG, G2 and the G block's smoke s03);
  - THE WALK CHECK's reading (E211's): a "rgm136 gemmLnc" process wants walk mn on every launch, walk_ok true and walk_launches_bad 0;
  - THE TILES at the sha256 the registration records (points-e220.json > tile_sha256) and their manifest (kinds/kinds.json);
  - THE STOP LINES (plan-e220.json > arms > A > live_stops: the board strictly above 72 W on 3 samples in a row, the die at or above 80 C; E215
    arm B's lines on this card) with THE LATCH READING (minshire[2] trips only when it has RISEN during the session), the board line counting
    only samples that carry a board reading;
  - THE GATES (plan-e220.json > arms > A): the die gate (min(63, rest die + 3) C; at most 300 s, else that run is NO DATA), THE CARD-TIME RULE
    (no run after 60 card-minutes, the session ends at 70) and the window's last end;
  - THE ORDER (plan-e220.json > arms > A > runs; the opening smoke s01 the runner's own and not in the sequence): 113 entries - the tie, pass 1
    (65), the tie, pass 2 (18), the tie, then THE G BLOCK, LAST: its family smoke s03 (block "G-smoke", D1's gemmLnc2x1x37) and its 26 runs
    (G-pass1: the 19 gemmLnc points by planning peak ascending; G-pass2: the 7 G2 points again, reversed); each run one host process
    `timeout <T> <the point's host> <the point's host_args> --kernel <the point's ELF> --stop-file <STOP>`, never `timeout -k`, T the kit's
    sized plain timeout (10 s; 13 s for xf04: desk/timeouts-e220.json, E218's R0 lesson);
  - THE FAMILY SMOKE (E220.md 3, E213's Amendment A1 form as E218 ran it): s03 is the G block's own gate and stop path: a failure that is the
    family's DROPS THE FAMILY (its points never start, NO DATA) and the session goes on; a failure that is the session's stops the session. s01
    is the session's gate: any failure there is the smoke gate, no run;
  - THE HOST'S RECORDS, READ FROM A SOURCE NO RUNTIME PRINT CAN SPLIT (CONTEXT section 116's lesson; aifoundry1's runtime prints "Opening
    device N" on a host's stdout): runtime lines removed pass after pass; a runtime line naming another card than card 1 is an identity trip;
  - the counted launch: an fma launch with launch >= 0, ok, wall_s >= 0.1 s, at least one pass, its kernel clock in 590-610 MHz.
    python3 -I -B tools/claims-v3/e220/e220a_common.py        the self-check (E220A-COMMON SELF-CHECK PASS)
SPDX-License-Identifier: Apache-2.0
"""
import csv
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PLAN_F = os.path.join(HERE, "plan-e220.json")
PTS_F = os.path.join(HERE, "points-e220.json")
KJ_F = os.path.join(HERE, "kernel-e220.json")
TIMEOUTS_F = os.path.join(HERE, "desk", "timeouts-e220.json")
TIMEOUTS_SHA = "36b86f86620fe65397b4393cb13ed6a952dc64e2230bb84728aa04509939a96b"     # desk/timeouts-e220.json (desk/timeout_e220.py --check)
# the frozen forecasts the doubles read (E220.md sections 0 and 5): forecast-e220.csv at its pin (the registration's freeze line), MM1-v3.2's
# rows of arm A at 600.0 MHz by point id (the tie t01 and the smoke row s01 among them; s03's row is the rule's gemmLnc2x2x2, which D1 replaced:
# the doubles give s03 toy figures)
FC = ("tools/claims-v3/e220/forecast-e220.csv", "082e3d9c8c1c32353438fe8e2930ad3d900049f5f1b3181c48d1897d373227fa")
FC_MODEL = "MM1-v3.2"
FC_ARM, FC_MHZ = "A", "600.0"
FMTS = ("fp32", "fp16", "int8")

# ---- the builds (build_e220a.sh writes them on aifoundry1, from the box tree's root)
BUILD_DIR = "build/e220argm"
BUILD_REC = BUILD_DIR + "/BUILD-e220a.json"
GUARD = "tools/claims-v3/e220/ettelem_guard_e220a.sh"
BUILDER = "build_e220a.sh"
KERNELS = {     # kernel-e220.json, repeated here and checked against it by the self-check (rgm211: its host's tree; kernel-e220.json "rgm211_host")
    "rgm136": {"src": "tools/claims-v3/e136/rgm136", "dir": BUILD_DIR + "/rgm136",
               "elf": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
               "text": "61315bf6a449c2823fbffc33834b4c0a68aa19e8436a29c1124b15c04114b763",
               "load": "649d40793e459e51db9a590ca90dd1363da3a00398f98938c3ef6e190514e2b7"},
    "rgm211": {"src": "tools/claims-v3/e211/rgm211", "dir": BUILD_DIR + "/rgm211",
               "elf": "00402801a1a53a9330898ef023297d8967a2c655472a40e0f1cd65dea04f09ae",
               "text": "82c7980716a0f0cacd24364ef9a23435343eb8f2c35c32b0ec5d60b46c8a4069",
               "load": "1351a569e4a200cb4cd916c4c6af822b45ce6e1cac9b7aa8b71c945a1f5bd847"},
}
KJ_KEY = {"rgm136": "rgm136", "rgm211": "rgm211_host"}    # each build's entry in kernel-e220.json > kernels
# THE TWO ARM FAMILIES, keyed by the registration's "loop" (kernel-e220.json > arm_families): the host, the ELF, the arm's prefix as the host
# spells it, and the walk rgm211's host must report on every launch (None: rgm136's host prints no walk)
LOOPS = {
    "rgm136 gemmL": {"host": "rgm136", "elf": "rgm136", "prefix": "gemmL", "walk": None},
    "rgm136 gemmLnc": {"host": "rgm211", "elf": "rgm136", "prefix": "gemmLnc", "walk": "mn"},
}


def host_rel(kind):
    return KERNELS[kind]["dir"] + "/host/sparsity_host"


def elf_rel(kind):
    return KERNELS[kind]["dir"] + "/kernel/sparsity.elf"


# ---- the arm (E220.md 6, arm A; plan-e220.json > arms > A; the stop and gate numbers checked against the plan's words by the self-check). One
# arm, "A": the runbook's and the runner's word for it (E220's own arm letter), so every RB_OUT file and every session folder carries it
ARMS = {
    "A": {"box": "aifoundry1", "card": "aifoundry1 card 1", "card_index": "1", "lock": "/run/lock/etsoc-shire1.lock", "et_devices": "1",
          "tree": "nekko", "data_dir": "aifoundry1-c1", "jobs": "a1",
          "ettelem": "build/ettelem/ettelem",
          "ettelem_sha256": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325",   # E206 arm B's, E213 arm B's, E215 arm B's (E190's, E198's)
          "config": {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}, "clock_mhz": 600, "count_mhz": (590.0, 610.0),
          "gate_cap_c": 63.0, "gate_add_c": 3.0, "stops": (72.0, 3, 80.0),
          "rule_s": 60 * 60.0, "cap_s": 70 * 60.0,
          "smoke": ("s01", "s03"), "opening": ("s01",), "lnc_smoke": ("s03",), "tie": "t01",
          "loops": ("rgm136 gemmL", "rgm136 gemmLnc")},
}
ETDEV_YES = "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"     # E215 arm B's build reading on aifoundry1

# ---- THE FAMILY SMOKE (E220.md 3: s03 "the G block's own gate and stop path right before the G block", E213's Amendment A1 form): a smoke
# point whose failure that is not the session's (a1_session_level) drops its family - the family's points never start (NO DATA) - instead of
# stopping the session. The session's gate (any failure: the smoke gate, no run) is SESSION_SMOKE.
FAMILY_SMOKE = {"s03": "rgm136 gemmLnc"}
SESSION_SMOKE = ("s01",)
LNC_BLOCKS = ("G-pass1", "G-pass2")
LNC_SMOKE_BLOCK = "G-smoke"
RULES_F = os.path.join(HERE, "rules-e220.json")
N_G_POINTS = 19                 # arm A's gemmLnc points: XG 12 (xg01-xg12) and G2 7 (n01-n07)
N_G_RUNS = 26                   # the G block: the 19 once (G-pass1), the 7 G2 again reversed (G-pass2)
# the plan's block words (plan-e220.json > arms > A > runs > block) and the kit's
BLOCK_OF = {"tie": "tie", "pass1": "pass1", "pass2": "pass2", "G block": "G-pass1", "G block reversed (G2 only)": "G-pass2"}
# the smoke and the tie as the kit runs them (plan-e220.json > arms > A > runs and departure_D1_smoke): one checked process each, in the points'
# host form; the self-check reads each against the plan's row (s01, t01) or its D1 words (s03)
MADE = {
    "s01": {"token": "gemmL2x2x2", "fmt": "fp32", "mask": "0xffffffff", "loop": "rgm136 gemmL", "family": "smoke"},
    "s03": {"token": "gemmLnc2x1x37", "fmt": "fp32", "mask": "0xffffffff", "loop": "rgm136 gemmLnc", "family": "smoke"},
    "t01": {"token": "gemmL2x4x4", "fmt": "fp32", "mask": "0xffffffff", "loop": "rgm136 gemmL", "family": "tie"},
}
TILE_OF = {"fp32": "tools/claims-v3/kinds/tiles/fp32/randn.bin", "fp16": "tools/claims-v3/kinds/tiles/fp16/randn.bin",
           "int8": "tools/claims-v3/kinds/tiles/int8/full.bin"}


def a1_session_level(proc, id_ok, sampler_live=True):
    """A family smoke's failures that still stop the session (E213's Amendment A1 form, E220.md 3, E215's reading): '' when none, else why. K1 (a
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


# ---- every file a point's --values names, at the sha256 the registration records (points-e220.json > tile_sha256) and its manifest records
TILES = {
    "tools/claims-v3/kinds/tiles/fp32/randn.bin": "34b2add3eb5b7b3c83be7ca7286cf1625c0fca7a1ac9957cafe4fd22e1b804fa",
    "tools/claims-v3/kinds/tiles/fp16/randn.bin": "2ab30f0f335cbe8aa87fe7a7cf27f66458deb6e34d04d5633a61d3fd96b0c974",
    "tools/claims-v3/kinds/tiles/int8/full.bin": "f5a5f3bf675fca97e857be3747d5f58b6b3d020f25ed11f5d047a87f161444a9",
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


# ---- the session's timing: the registration's numbers (E220.md 3 and 6; plan-e220.json), and the kit's own (marked)
REST_READ_S = 10.0          # E220.md 6, a run: "its die gate, 10 s at rest, one host process ... a 4 s tail" (p_rest = the median of its last 5 s)
REST_WINDOW_S = 5.0         # the reducer's p_rest: the last 5 s of the run's rest (E215's form, which E220.md 7 adopts)
SMOKE_REST_S = 30.0         # the kit's (E206's, E211's and E215's smoke form): 30 s at rest first, the session's rest reading; the die gates are formed from it
SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5     # E220.md 3: "one checked process each"; the 2 s process E146's, E190's, E206's, E211's and E215's smoke ran
RUN_SECONDS, RUN_BUDGET = 6.0, 7.5         # E220.md 6: "'--seconds 6 --budget 7.5'"
TAIL_S = 4.0                # E220.md 6: "a 4 s tail"
GATE_WAIT_S = 300.0         # plan-e220.json die_gate: "waited at most 300 s, else that run is NO DATA"
CLOSE_S = 60.0              # the kit's: the closing (the sampler's stop, the closing config read) keeps this much of the cap
WINDOW_MARGIN_S = 90.0      # the kit's (E190's, E206's, E211's, E215's): no run starts within its length + 90 s of the window's last end
EVERY_MS = 100              # the sampler's rate (10 Hz)
HOST_TIMEOUT_S = 10         # `timeout 10` on every device call but a run whose frozen GEMM needs more (timeout_of; plain: never -k)
HANG_GRACE_S = 4.0          # the kit's: a host whose `timeout` has not returned 4 s after its 10 s TERM is HUNG (reported and left)
RUN_MAX_S = REST_READ_S + HOST_TIMEOUT_S + HANG_GRACE_S + TAIL_S   # a run of timeout 10 once its gate has passed (28 s); run_max_s(pid) per run
SMOKE_CYC = (200.0, 4000.0)  # E220.md 7, R0: "the smoke's counter mean 200-4,000 cycles an op" (the runner's smoke gate reads R0's band)
MHZ_BAND = (590.0, 610.0)   # E220.md 7: S6's band, and the kernel clock a counted launch is in
LINE_W = 69.0               # plan-e220.json > arms > A > drop_line_W: no point whose planning peak reaches it runs (none does: the self-check reads it)
RUNTIME_LINE = re.compile(r"Opening device [0-9]+\n")         # a runtime's line, on a host's or a reader's stdout (aifoundry1's form; read on any box)
RUNTIME_CARD = re.compile(r"Opening device ([0-9]+)")         # the card such a line opens (another card's is an identity trip)


def load(path):
    with open(path) as f:
        return json.load(f)


def plan():
    return load(PLAN_F)


_PTS = {}


def registration():
    """points-e220.json and plan-e220.json as registered: {"points": points-e220.json, "plan": plan-e220.json}."""
    if "r" not in _PTS:
        _PTS["r"] = {"points": load(PTS_F), "plan": load(PLAN_F)}
    return _PTS["r"]


def _shape(tok):
    m = re.match(r"^gemmL(?:nc|n)?(\d+)x(\d+)x(\d+)$", tok)
    return tuple(int(x) for x in m.groups()) if m else None


def made_point(pid, arm="A"):
    """The smoke s01, s03 and the tie t01 in the points' form (MADE: the plan's rows and D1's words), with the points' host arguments."""
    s = MADE[pid]
    mb, nb, kb = _shape(s["token"])
    fam = s["loop"]
    tile = TILE_OF[s["fmt"]]
    mask = s["mask"]
    return {"id": pid, "arm": s["token"], "format": s["fmt"], "kind": "random", "shire_mask": mask, "shires": mask,
            "minions": bin(int(mask, 16)).count("1") * 32, "loop": fam, "host": LOOPS[fam]["host"], "elf": "rgm136", "kernel": "rgm136",
            "card": ARMS[arm]["card"], "family": s["family"], "name": f"{s['token']}.{s['fmt']}.random.{fam.replace(' ', '-')}",
            "ops_per_minion_per_gemm": 64 * mb * nb * kb, "macs_per_gemm": None,
            "host_args": ["--test", "fma", "--type", s["fmt"], "--pattern", "none", "--values", f"{s['token']}:randn:{tile}", "--shires", mask,
                          "--per-shire", "32", "--seconds", "6", "--budget", "7.5", "--seed", "1"],
            "tile_sha256": {tile: TILES[tile]}}


def points():
    """The registration in the kit's arm form (E215's): {"arms": {"A": {"points", "references" (none), "smoke", "tie", "order": {"sequence",
    "opening_smoke", "gemmLnc_smoke"}}}}; the sequence is plan-e220.json > arms > A > runs without its first entry (the opening smoke s01, the
    runner's own), each entry {"n" (its place, 1..113), "block" (the kit's word, BLOCK_OF; s03 "G-smoke"), "id", "name"}."""
    if "p" not in _PTS:
        R = registration()
        pts = R["points"]["points"]["A"]
        smoke = [made_point(pid) for pid in ARMS["A"]["smoke"]]
        tie = made_point(ARMS["A"]["tie"])
        by = {q["id"]: q for q in pts + smoke + [tie]}
        runs = R["plan"]["arms"]["A"]["runs"]
        seq = []
        for i, r in enumerate(runs[1:], start=1):
            blk = LNC_SMOKE_BLOCK if (r["block"] == "smoke" and r["id"] in FAMILY_SMOKE) else BLOCK_OF.get(r["block"], "?" + r["block"])
            seq.append({"n": i, "block": blk, "id": r["id"], "name": (by.get(r["id"]) or {}).get("name", r["id"])})
        _PTS["p"] = {"arms": {"A": {"points": pts, "references": [], "smoke": smoke, "tie": tie,
                                    "order": {"sequence": seq, "opening_smoke": [runs[0]["id"]] if runs and runs[0]["block"] == "smoke" else [],
                                              "gemmLnc_smoke": [x["id"] for x in seq if x["block"] == LNC_SMOKE_BLOCK]}}}}
    return _PTS["p"]


def arm_points(arm):
    """Every point of the arm the runner may start: its points, its smoke and its tie."""
    A = points()["arms"][arm]
    return A["points"] + A.get("references", []) + A["smoke"] + [A["tie"]]


def point(pid):
    """A point of arm A by its id (the 84 of points-e220.json > points > A, the smoke s01 and s03, the tie t01)."""
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
        raise ValueError(f"{rel} is not E220's frozen file {pin[:12]}")
    return list(csv.DictReader(raw.decode().splitlines()))


def forecast_rows(arm):
    """MM1-v3.2's frozen forecast rows by point id, in one form {id: {cycles_per_op_wall, cycles_per_op_mean, seconds_per_gemm, W_over_idle}}
    (FC at its pin: arm A's MM1-v3.2 rows at 600.0 MHz, the points, the tie and the smoke rows, each kept only where its token is the run's
    own - s03's frozen row is the rule's gemmLnc2x2x2, which D1 replaced; else ValueError: the box check's harness read refuses first)."""
    if arm not in _FC:
        if arm not in ARMS:
            raise KeyError(arm)
        out = {}
        tok = {q["id"]: q["arm"] for q in arm_points(arm)}
        for r in _pinned_rows(*FC):
            if r["arm"] == FC_ARM and r["model"] == FC_MODEL and r["f_mhz"] == FC_MHZ and tok.get(r["id"]) == r["token"]:
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
    (cycles an op on the wall and the counter's mean, seconds a GEMM, W over idle, ops a minion a GEMM: the points, the tie and s01); for s03,
    which no frozen row prices (D1), the ops from the point and the toy 900 / 800 cycles an op and 20 W over idle."""
    p = point(pid)
    arm = arm_of(pid)
    ops = int(p["ops_per_minion_per_gemm"])
    r = forecast_rows(arm).get(pid)
    if r and r.get("cycles_per_op_wall") and r.get("W_over_idle"):
        cw, cm = float(r["cycles_per_op_wall"]), float(r["cycles_per_op_mean"])
        return {"cyc_wall": cw, "cyc_mean": cm, "t": float(r["seconds_per_gemm"]), "W": float(r["W_over_idle"]), "ops": ops}
    cw, cm = 900.0, 800.0
    return {"cyc_wall": cw, "cyc_mean": cm, "t": cw * ops / 600e6, "W": 20.0, "ops": ops}


_TO = {}


def timeouts():
    """The kit's sized plain timeouts by point id (desk/timeouts-e220.json > arms > A > timeouts, at TIMEOUTS_SHA; else ValueError)."""
    if "t" not in _TO:
        raw = open(TIMEOUTS_F, "rb").read()
        if hashlib.sha256(raw).hexdigest() != TIMEOUTS_SHA:
            raise ValueError(f"desk/timeouts-e220.json is not the kit's {TIMEOUTS_SHA[:12]}")
        _TO["t"] = {k: int(v["timeout_s"]) for k, v in json.loads(raw)["arms"]["A"]["timeouts"].items()}
    return _TO["t"]


def timeout_of(pid):
    """A process's plain timeout in seconds (never -k): 10 unless desk/timeouts-e220.json sizes it longer for its frozen GEMM (xf04: 13)."""
    return timeouts().get(pid, HOST_TIMEOUT_S)


def run_max_s(pid):
    """The longest a run can last once its gate has passed: its rest, its process's timeout, the HUNG grace and its tail."""
    return REST_READ_S + timeout_of(pid) + HANG_GRACE_S + TAIL_S


def stops_of(arm, p=None):
    """The arm's stop lines under the watcher's keys (ARMS; the self-check reads them against plan-e220.json's words)."""
    if arm not in ARMS:
        raise KeyError(arm)
    b, n, d = ARMS[arm]["stops"]
    return {"board_cap_w": float(b), "cap_consecutive": int(n), "abs_stop_c": float(d)}


def gate_c(arm, rest_die):
    """The die gate a run starts under (plan-e220.json > arms > A > die_gate): min(63, rest die + 3); None with no rest die."""
    if rest_die is None:
        return None
    a = ARMS[arm]
    return min(a["gate_cap_c"], rest_die + a["gate_add_c"])


def sequence(arm):
    """The registered order: [{"n", "block", "id", "name"}, ...] (plan-e220.json > arms > A > runs, 113 entries after the opening smoke):
    the runs (blocks tie, pass1, pass2, G-pass1, G-pass2) and the G block's smoke (block G-smoke, right before its block). The opening smoke s01
    is the runner's own, first, and not in it."""
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
    """The start config the arm's line rests on (plan-e220.json config_gate), read as found, nothing set."""
    if not j or arm not in ARMS:
        return False
    return all(j.get(k) == v for k, v in ARMS[arm]["config"].items())


class Stops:
    """THE STOP LINES on live samples (plan-e220.json > card > stops; E206's watcher, line for line): the shires' mean at or above abs_stop_c
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
    pts, R = points(), registration()
    arm = "A"
    a = ARMS[arm]
    pa = R["plan"]["arms"][arm]
    # the arm against the plan's words (plan-e220.json > arms > A)
    st = stops_of(arm)
    if (st["board_cap_w"], st["cap_consecutive"], st["abs_stop_c"]) != (72.0, 3, 80.0):
        bad.append(f"the stops {st}")
    if "the board strictly above 72 W on 3 samples in a row" not in pa["live_stops"] or "the die at or above 80 C" not in pa["live_stops"] or \
            float(pa["stop_W"]) != 72.0 or float(pa["die_stop_C"]) != 80.0:
        bad.append(f"the plan's stop words {pa['live_stops'][:80]!r}")
    if not pa["die_gate"].startswith("min(63, the session's rest die + 3) C, waited at most 300 s") or gate_c(arm, 100.0) != 63.0 or \
            gate_c(arm, 40.0) != 43.0:
        bad.append(f"the gate {pa['die_gate']!r}")
    c = a["config"]
    cfg_txt = f"TDP {c['tdp_w']} W, temperature threshold {c['temp_threshold_c']} C, minion {c['minion_mhz']} MHz"
    if not pa["start_config_gate"].startswith(cfg_txt) or cfg_txt != "TDP 65 W, temperature threshold 65 C, minion 600 MHz":
        bad.append(f"the start config {pa['start_config_gate']!r}")
    if not pa["card"].startswith(a["card"] + " ") or a["lock"] not in pa["card"] or "ET_DEVICES=1 on every device process" not in pa["card"] or \
            R["points"]["arms"][arm]["card"] != a["card"] or a["box"] != "aifoundry1" or not pa["window_box"].startswith("aifoundry1 "):
        bad.append("the card, box or lock")
    ct = pa["card_time"]
    if (ct["rule_card_minutes"], ct["cap_card_minutes"]) != (a["rule_s"] / 60, a["cap_s"] / 60) or (a["rule_s"], a["cap_s"]) != (3600.0, 4200.0):
        bad.append("the card-time rule and cap")
    if float(pa["drop_line_W"]) != LINE_W or float(pa["highest_PP_all_W"]) >= LINE_W or \
            any(float(q["PP32_W"]) >= LINE_W for q in pts["arms"][arm]["points"]):
        bad.append(f"a point's planning peak at or over the {LINE_W:g} W line")
    if "10 s at rest" not in pa["run_form"] or "'--seconds 6 --budget 7.5'" not in pa["run_form"] or "a 4 s tail" not in pa["run_form"] or \
            "plain 'timeout 10'" not in pa["run_form"] or "the kit sizes the timeout" not in pa["run_form"]:
        bad.append(f"the run's form {pa['run_form'][:80]!r}")
    A = pts["arms"][arm]
    seq = sequence(arm)
    runs = [r for r in seq if not is_lnc_smoke(r)]
    pr = pa["runs"]
    if pr[0]["id"] != "s01" or pr[0]["block"] != "smoke" or len(pr) != len(seq) + 1 or len(pr) != pa["n_runs"] + pa["n_smoke"]:
        bad.append(f"the registered order's first entry {pr[:1]} is not the opening smoke s01, or its length")
    if len(runs) != pa["n_runs"] or len(runs) != 112 or [r["n"] for r in seq] != list(range(1, len(seq) + 1)) or \
            [r["n"] for r in pr] != list(range(1, len(pr) + 1)):
        bad.append(f"the order's runs ({len(runs)}) are not the plan's {pa['n_runs']}, or its places are not 1..{len(seq)}")
    if [(x["id"], BLOCK_OF.get(x["block"], LNC_SMOKE_BLOCK if x["id"] == "s03" else "?")) for x in pr[1:]] != [(x["id"], x["block"]) for x in seq]:
        bad.append("the sequence is not the plan's runs in order")
    ti = [i for i, r in enumerate(seq) if r["block"] == "tie"]
    if len(ti) != 3 or ti[0] != 0 or any(seq[i]["id"] != a["tie"] for i in ti):
        bad.append("the ties")
    # THE G BLOCK LAST (E220.md 6): after the third tie, its family smoke s03, then its runs, nothing after; every gemmLnc run there
    smi = [i for i, r in enumerate(seq) if is_lnc_smoke(r)]
    lnc = [r for r in seq if r["block"] in LNC_BLOCKS]
    if [seq[i]["id"] for i in smi] != list(a["lnc_smoke"]) or (ti and smi != [ti[-1] + 1]) or (smi and seq[smi[0] + 1:] != lnc) or \
            len(lnc) != N_G_RUNS:
        bad.append(f"the G block is not the tie, its smoke {a['lnc_smoke']}, then its {N_G_RUNS} runs, last")
    for r in runs:
        if r["block"] != "tie" and ((point(r["id"])["loop"] == "rgm136 gemmLnc") != (r["block"] in LNC_BLOCKS)):
            bad.append(f"run {r['n']} {r['id']} ({r['block']}) breaks 'the G block LAST'")
            break
    o = pa["order"]
    if [r["id"] for r in lnc] != o["G_block"] + o["G_block_reversed"] or [r["id"] for r in runs if r["block"] == "pass1"] != o["pass1"] or \
            [r["id"] for r in runs if r["block"] == "pass2"] != o["pass2"] or [r["id"] for r in lnc if r["block"] == "G-pass2"] != o["G_block_reversed"]:
        bad.append("the sequence's blocks are not the registered pass1, pass2, G_block and G_block_reversed")
    ids = {r["id"] for r in runs if r["block"] != "tie"}
    if ids != {q["id"] for q in A["points"]} or len(A["points"]) != pa["n_points"] or pa["n_points"] != 84:
        bad.append(f"the runs' points are not the registered {len(A['points'])}")
    want_n = {q["id"]: (2 if q["family"] in ("L3", "Y2", "G2") else 1) for q in A["points"]}
    if any(sum(1 for r in runs if r["id"] == q) != n for q, n in want_n.items()):
        bad.append("a registered point does not run its registered number of times (L3, Y2 and G2 twice, the rest once)")
    cnt = {}
    for q in A["points"]:
        cnt[q["family"]] = cnt.get(q["family"], 0) + 1
    if cnt != pa["counts"] or cnt != {"X": 52, "L3": 8, "Y2": 10, "G2": 7, "G2t": 7}:
        bad.append(f"the families {cnt}")
    if tuple(q["id"] for q in A["smoke"]) != a["smoke"] or A["tie"]["id"] != a["tie"] or \
            tuple(A["order"]["opening_smoke"]) != a["opening"] or tuple(A["order"]["gemmLnc_smoke"]) != a["lnc_smoke"]:
        bad.append(f"the smoke {[q['id'] for q in A['smoke']]}, its opening and G smoke, or the tie")
    # the made rows against the plan: s01 and t01 by their rows, s03 by D1's words
    rows = {r["id"]: r for r in pr}
    for pid in ("s01", "t01"):
        m = MADE[pid]
        if (rows[pid].get("token"), rows[pid].get("fmt"), rows[pid].get("mask")) != (m["token"], m["fmt"], m["mask"]):
            bad.append(f"{pid}: the kit's {m} is not the plan's row")
    d1 = pa["departure_D1_smoke"]["rows"]
    if not d1["s03"]["run"].startswith("gemmLnc2x1x37 fp32 random, the full chip") or MADE["s03"]["token"] != "gemmLnc2x1x37" or \
            not d1["s01"].get("kept") or not d1["s01"]["run"].startswith("gemmL2x2x2 fp32 random, the full chip"):
        bad.append("the smoke rows are not D1's")
    for q in A["smoke"]:
        if q["id"] in SESSION_SMOKE:
            if q["loop"] != "rgm136 gemmL" or q["id"] in FAMILY_SMOKE:
                bad.append(f"the session's smoke {q['id']} ({q['loop']})")
        elif FAMILY_SMOKE.get(q["id"]) != q["loop"]:
            bad.append(f"the family smoke {q['id']} ({q['loop']}) is not FAMILY_SMOKE's {FAMILY_SMOKE.get(q['id'])}")
        if not (q["format"] == "fp32" and q["kind"] == "random" and q["shire_mask"] == "0xffffffff" and q["minions"] == 1024):
            bad.append(f"the smoke {q['id']} is not an fp32 random full-chip process ({q['arm']} {q['format']} {q['kind']})")
    for fam in sorted({q["loop"] for q in A["points"]}):
        if fam != "rgm136 gemmL" and not any(q["loop"] == fam and q["id"] in FAMILY_SMOKE for q in A["smoke"]):
            bad.append(f"the family {fam} has points but no family smoke")
    if A["smoke"][0]["id"] not in SESSION_SMOKE:
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
        if q["card"] != a["card"] or q.get("kernel") != "rgm136":
            bad.append(f"{q['id']}: card {q['card']} or kernel {q.get('kernel')}")
            break
    lnc_ids = sorted(q["id"] for q in A["points"] if q["loop"] == "rgm136 gemmLnc")
    if lnc_ids != sorted([f"xg{i:02d}" for i in range(1, 13)] + [f"n{i:02d}" for i in range(1, 8)]) or len(lnc_ids) != N_G_POINTS or \
            sorted(q["id"] for q in A["points"] if q.get("subfamily") == "XG" or q["family"] == "G2") != lnc_ids:
        bad.append(f"the family 'rgm136 gemmLnc''s points {lnc_ids}, registered xg01-xg12 and n01-n07")
    # the builds and the families against kernel-e220.json
    kj = load(KJ_F)
    k1 = kj["kernels"]["rgm136"]
    v = KERNELS["rgm136"]
    if (k1["elf_sha256"], k1["text_sha256"], k1["loadable_identity_sha256"], k1["tree"]) != (v["elf"], v["text"], v["load"], v["src"]):
        bad.append("rgm136's pins differ from kernel-e220.json")
    k2 = kj["kernels"]["rgm211_host"]
    v = KERNELS["rgm211"]
    if (k2["elf_sha256"], k2["loadable_identity_sha256"], k2["tree"]) != (v["elf"], v["load"], v["src"]):
        bad.append("rgm211's tree pins differ from kernel-e220.json's rgm211_host")
    try:
        e211 = load(os.path.join(REPO, "tools/claims-v3/e211/kernel-e211.json"))["kernels"]["rgm211"]
        if (e211["elf_sha256"], e211["text_sha256"], e211["loadable_identity_sha256"]) != (v["elf"], v["text"], v["load"]):
            bad.append("rgm211's pins differ from E211's kernel-e211.json")
    except (OSError, KeyError, ValueError):
        pass                    # not on the box (the harness syncs E220's files and the sources only): the desk's step 2 reads it
    for fam, v in LOOPS.items():
        f = kj["arm_families"].get(fam)
        if not f or (f["host"], f["elf"]) != (v["host"], v["elf"]):
            bad.append(f"the family {fam} differs from kernel-e220.json")
    if set(kj["arm_families"]) != set(LOOPS):
        bad.append("the families are not kernel-e220.json's two")
    for fam in LOOPS:
        reg = sorted(kj["arm_families"][fam]["points"][arm])
        if reg != sorted(q["id"] for q in A["points"] if q["loop"] == fam):
            bad.append(f"the family {fam}'s arm A points differ from kernel-e220.json's")
    # the frozen forecasts: at their pins, every registered point, the tie and s01 there; s03 (D1) toy
    try:
        rows_fc = forecast_rows(arm)
        miss = [q["id"] for q in A["points"] + [A["tie"]] + [point("s01")] if q["id"] not in rows_fc]
        if miss:
            bad.append(f"no frozen forecast for {miss[:5]}")
        for q in arm_points(arm):
            d = double_of(q["id"])
            if not (d["t"] > 0 and d["cyc_mean"] > 0 and d["ops"] > 0):
                bad.append(f"{q['id']}: the doubles' figures")
                break
        if abs(double_of("xg01")["cyc_wall"] - 1169.99922) > 1e-6 or abs(double_of("xg01")["W"] - 24.1597449) > 1e-6:
            bad.append("the doubles' xg01 figures are not MM1-v3.2's frozen forecast at 600.0 MHz")
        if abs(double_of("t01")["cyc_wall"] - 1165.72811) > 1e-6 or abs(double_of("s01")["cyc_wall"] - 890.251864) > 1e-6:
            bad.append("the doubles' t01 or s01 figures are not the registration's MM1-v3.2 rows")
        if double_of("s03")["cyc_wall"] != 900.0 or double_of("s03")["W"] != 20.0 or "s03" in rows_fc:
            bad.append("the G smoke's toy figures (D1: no frozen row of gemmLnc2x1x37)")
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"the frozen forecasts ({type(e).__name__}: {str(e)[:80]})")
    # the sized timeouts (desk/timeouts-e220.json): xf04 13 s, every other process 10 s
    try:
        to = timeouts()
        longer = {k: v for k, v in to.items() if v != HOST_TIMEOUT_S}
        if longer != {"xf04": 13} or timeout_of("xf04") != 13 or timeout_of("xg01") != 10 or timeout_of("s01") != 10 or \
                set(to) != {r["id"] for r in pr} or abs(run_max_s("xf04") - 31.0) > 1e-9 or abs(run_max_s("t01") - RUN_MAX_S) > 1e-9:
            bad.append(f"the sized timeouts {longer}")
    except (OSError, ValueError, KeyError) as e:
        bad.append(f"the sized timeouts ({type(e).__name__}: {str(e)[:80]})")
    # the argv: both families' hosts and kernel
    R32 = "tools/claims-v3/kinds/tiles/fp32/randn.bin"
    g = host_argv("/T", "xg01", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if g[:2] != ["/T/build/e220argm/rgm211/host/sparsity_host", "--test"] or arg_of(g, "--values") != f"gemmLnc2x6x8:randn:{R32}" or \
            arg_of(g, "--shires") != "0xffffffff" or arg_of(g, "--per-shire") != "32" or arg_of(g, "--seconds") != "6" or \
            arg_of(g, "--budget") != "7.5" or arg_of(g, "--kernel") != "/T/build/e220argm/rgm136/kernel/sparsity.elf" or \
            arg_of(g, "--stop-file") != "/T/STOP" or "-k" in g or arg_of(g, "--seed") != "1" or arg_of(g, "--type") != "fp32":
        bad.append(f"the rgm136 gemmLnc argv {g}")
    m = host_argv("/T", "xg01t", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if m[0] != "/T/build/e220argm/rgm136/host/sparsity_host" or arg_of(m, "--kernel") != "/T/build/e220argm/rgm136/kernel/sparsity.elf" or \
            arg_of(m, "--values") != f"gemmL2x6x8:randn:{R32}":
        bad.append(f"the rgm136 gemmL argv {m}")
    h = host_argv("/T", "xf05", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if arg_of(h, "--values") != "gemmL11x16x3:randn:tools/claims-v3/kinds/tiles/fp16/randn.bin" or arg_of(h, "--type") != "fp16":
        bad.append(f"an fp16 argv {h}")
    i8 = host_argv("/T", "xf10", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if arg_of(i8, "--values") != "gemmL14x16x3:randn:tools/claims-v3/kinds/tiles/int8/full.bin" or arg_of(i8, "--type") != "int8":
        bad.append(f"an int8 argv {i8}")
    s = host_argv("/T", "s03", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if arg_of(s, "--seconds") != "2" or arg_of(s, "--budget") != "3.5" or arg_of(s, "--type") != "fp32" or \
            arg_of(s, "--kernel") != "/T/build/e220argm/rgm136/kernel/sparsity.elf" or s[0] != "/T/build/e220argm/rgm211/host/sparsity_host" or \
            arg_of(s, "--values") != f"gemmLnc2x1x37:randn:{R32}":
        bad.append(f"the G smoke's argv {s}")
    s1 = host_argv("/T", "s01", SMOKE_SECONDS, SMOKE_BUDGET, "/T/STOP")
    if s1[0] != "/T/build/e220argm/rgm136/host/sparsity_host" or arg_of(s1, "--values") != f"gemmL2x2x2:randn:{R32}":
        bad.append(f"the session's smoke's argv {s1}")
    tt = host_argv("/T", "t01", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if tt[0] != "/T/build/e220argm/rgm136/host/sparsity_host" or arg_of(tt, "--values") != f"gemmL2x4x4:randn:{R32}" or arg_of(tt, "--seconds") != "6":
        bad.append(f"the tie's argv {tt}")
    mk = host_argv("/T", "xy01a", RUN_SECONDS, RUN_BUDGET, "/T/STOP")
    if expect_of(mk)["shire_mask"] != "0xf000" or expect_of(mk)["minions"] != 128 or point("xy01a")["minions"] != 128:
        bad.append(f"a subset's argv {mk}")
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
    r = [st.feed(smp(73)), st.feed(smp(73)), st.feed(smp(72.0)), st.feed(smp(73)), st.feed(smp(73)), st.feed(smp(73))]
    if r != [[], [], [], [], [], ["stop"]] or "board" not in (st.stop or "") or "above 72 W" not in st.stop:
        bad.append(f"the board line {r} {st.stop}")
    st = Stops(**stops_of(arm))
    if [st.feed(smp(die=79, high=87)) for _ in range(5)] != [[]] * 5 or st.feed(smp(die=80, high=87)) != ["stop"] or "shires' mean" not in st.stop:
        bad.append("the die line: the 87 C latch must not trip it, the mean at 80 C must")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=88)) != ["stop"] or "latch rose" not in st.stop:
        bad.append("the latch rising past its session value")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=87)) != [] or st.feed(smp(die=60, high=50)) != [] or st.feed(smp(die=60, high=81)) != ["stop"]:
        bad.append("the latch after a drop (a statistics reset by another) rising past the line")
    st = Stops(**stops_of(arm))
    if st.feed(smp(die=60, high=61)) != [] or st.feed(smp(die=60, high=79)) != [] or st.stop:
        bad.append("the latch rising below the line tripped")
    st = Stops(**stops_of(arm))       # a sample with no board reading neither counts nor breaks the row
    if st.feed({"t_ms": 1, "board_w": 75}) != [] or st.feed({"t_ms": 2}) != [] or st.feed({"t_ms": 3, "board_w": 75}) != [] or \
            st.feed({"t_ms": 4, "board_w": 75}) != ["stop"]:
        bad.append("a sample with no board reading neither counts nor breaks the row")
    st = Stops(**stops_of(arm))       # a reading at or under the line still breaks the row
    if [st.feed({"t_ms": k, "board_w": w}) for k, w in enumerate((95.0, None, 71.0, 95.0, None, 95.0))] != [[]] * 6 or st.stop:
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
    if config_json("Opening device 1\n" + '{"tdp_w":65,"temp_threshold_c":65,"minion_mhz":600}\n') != {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600} \
            or config_json('{"tdp_w":65,"temp_th') != {}:
        bad.append("config_json")
    if not config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600, "minion_mv": 499}) or config_ok("A", {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}) \
            or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 800}) or config_ok("A", {"tdp_w": 65, "temp_threshold_c": 70, "minion_mhz": 600}) \
            or config_ok("B", {"tdp_w": 65, "temp_threshold_c": 65, "minion_mhz": 600}):
        bad.append("the start config")
    if gate_c("A", 50.0) != 53.0 or gate_c("A", 61.0) != 63.0 or gate_c("A", None) is not None:
        bad.append("the die gate")
    try:
        sequence("B")
        bad.append("an arm B sequence")
    except KeyError:
        pass
    if abs(RUN_MAX_S - 28.0) > 1e-9:
        bad.append("RUN_MAX_S")
    if family("xg01") != "rgm136 gemmLnc" or family("xg01t") != "rgm136 gemmL" or not rgm211_host("n07") or rgm211_host("xy01a") or \
            arm_of("t01") != "A" or family("s01") != "rgm136 gemmL" or family("s03") != "rgm136 gemmLnc" or not rgm211_host("s03") or \
            rgm211_host("xf14") or rgm211_host("n07t") or not is_lnc_smoke({"block": "G-smoke"}) or is_lnc_smoke({"block": "pass1"}) or \
            run_key(sequence("A")[0]) != "001-tie-t01" or run_key([r for r in sequence("A") if is_lnc_smoke(r)][0]) != "087-G-smoke-s03":
        bad.append("the family, host and arm lookups")
    for dropped in ("xg07t", "xy03a", "g01", "y03a"):
        try:
            point(dropped)
            bad.append(f"{dropped} (never one of E220 arm A's points) is a point")
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
    print("E220A-COMMON SELF-CHECK " + ("PASS" if not b else "FAIL: " + "; ".join(b)))
    sys.exit(0 if not b else 1)
