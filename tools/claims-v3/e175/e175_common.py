#!/usr/bin/env python3
"""E175 (Q143(g)): what E175's predictions writer, protocol writer, runner, queue, scorer and self-tests share. E173's e173_common.py (lab
5a2a9ba0's kit) with E175's names, pool, predictions and plan (tools/claims-v3/e175/E175.md, lab c50ff493). Standard library only at import
(the runner must work on aifoundry2's python without numpy); the scorer's model calls go through Q142(p)'s frozen predictor, which the desk
imports with numpy (a2p()).

E175 is aifoundry2's governed line: 16 new kinds that run governed under aifoundry2's own governor inside the 82 W admission and 8 that run
pinned, drawn by E175.md's committed rule (make_e175_pool.py, the seed from lab 4576fb90), in E165's and E173's form (6 s bursts from a cool die,
each pass opening with the zeros anchors), with M10 carried by rule E (POOL8-REGISTRATION.md section 5) as the primary and M9's aifoundry2 part
on M9's D beside, both recomputed per tile through predict_pool8_a2.py's burst mode with the session's own zeros-anchor reads and each tile's
own die starts.

  * the frozen inputs and their sha256: E175's pool (tools/claims-v3/e175/pool/, its manifest e175.json) and its frozen predictions for
    aifoundry2 (the frozen predictor's own output, tools/claims-v3/e175/frozen/), the design's selection, Q142(p)'s registration and predictor
    (3e97f583, 8a8fa34c, 9d81d254, 68a7c322, 97765c0a), M9's aifoundry2 part (5b98bd5c), E165's references (3ef06839), the watcher fix
    (abe6b0f2, 33661416);
  * Q139(k)'s check of C and the C-logging host E160 built on aifoundry2 (E165's pins, unchanged), E80's kernel and sampler;
  * the pool's tiles as run values (`file:` a tile of tools/claims-v3/e175/pool/tiles/<type>/) and their labels (`e5-<name>`);
  * the tile check against e175.json (2,048 B; sha256 of the whole, of A and of B);
  * the stops, the admission line, the order's seed, the cap and the slot;
  * a2p(): predict_pool8_a2, imported from its committed directory after its sha256 is checked (it then checks its own two lists and
    POOL8-SHA256SUMS before anything is read).

    python3 -B tools/claims-v3/e175/e175_common.py        # the frozen inputs and every pool tile, checked (desk or box)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
import e165_common as C165  # noqa: E402  (E165's shared module, unchanged: Q139(k)'s pins, E80's binaries, the C-logging host)

EXPERIMENT = "E175"
REQUEST = "Q143(g)"
CARD = "aifoundry2"

POOL_REL = "tools/claims-v3/e175/pool"
MAN_REL = f"{POOL_REL}/e175.json"
PRED_REL = "tools/claims-v3/e175/frozen/predictions-pool8-aifoundry2.json"     # the frozen predictor's own output for E175's pool (its own file name)
POOL_SUMS_REL = f"{POOL_REL}/SHA256SUMS"
DESIGN_REL = "docs/reports/data/2026-11-05-q143g-e175-design"
SELECT_REL = f"{DESIGN_REL}/design-e175.json"
REGISTRATION_REL = "tools/claims-v3/e175/E175.md"
REG_SUMS_REL = "tools/claims-v3/e175/SHA256SUMS-e175-registration"
PD_REL = "docs/reports/data/2026-11-05-q142p-pool8-predictor"
A2PY_REL = f"{PD_REL}/predict_pool8_a2.py"
P8PY_REL = f"{PD_REL}/predict_pool8.py"
REG_REL = "tools/claims-v3/m10/POOL8-REGISTRATION.md"
REG_A1_REL = "tools/claims-v3/m10/POOL8-REGISTRATION.md.dated-note-1.md"
REG_A2_REL = "tools/claims-v3/m10/POOL8-REGISTRATION.md.dated-note-2.md"
REG_JSON_REL = "tools/claims-v3/m10/pool8-registration.json"
E165_PRED_REL = "tools/claims-v3/e165/predictions-e165.json"
WATCHER_REL = "tools/claims-v3/hpl/watcher_q142s.py"
RUN_HPL_REL = "tools/claims-v3/hpl/run_hpl.py"
M9A2_REL = C165.M9A2_REL
PM9A2_REL = C165.PM9A2_REL
# the frozen inputs and their sha256 are in frozen-sha256-e175.json (this directory), written by make_predictions_e175.py from the committed
# tree after each sha256 is matched against the committed hash list that already names it (E175's registration list and its design's
# SHA256SUMS, the pool's SHA256SUMS, the predictor's SHA256SUMS and SHA256SUMS-a2, POOL8-SHA256SUMS, the watcher's own pin of run_hpl.py);
# every later file reads it through frozen()
FROZEN_FILE = os.path.join(HERE, "frozen-sha256-e175.json")
CCHECK_FROZEN = dict(C165.CCHECK_FROZEN)
WRAPPER_REL = C165.WRAPPER_REL
CC_HOST_REL = C165.CC_HOST_REL
CC_HOST_SHA256 = C165.CC_HOST_SHA256
KERNEL_REL = C165.KERNEL_REL
ETTELEM_REL = C165.ETTELEM_REL
E80_SHA256 = dict(C165.E80_SHA256)
LABEL_PREFIX = "e5-"
ZEROS_ANCHORS = ("fp32.anchor7_zeros", "fp16.anchor7_zeros", "int8.anchor7_zeros")   # pool 8's floors: pool 7's three zeros anchors, re-run
REPLICATES = ("k-fp16-randn", "k-int8-full")       # E80's own kinds tiles, once a pass (E165-R0's drift check, E165's estimates)
GOVERNED_BELOW_MHZ = 795.0
STOPS = {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3}   # E165's (section 22 of the round's brief: every board stop at most 85 W)
LIMIT_W = 82.0          # the run-time admission line (E105's rule): a run starts only if its frozen estimate is at most 82 W
PEAK_LOCK_W = 82.0      # E159's lock: after a run whose highest board sample reached 82 W, nothing at or above that run's estimate runs
ORDER_SEED = 175
PASSES = 5
RUNS_PER_PASS = 29      # the three zeros anchors, 16 governed, 8 pinned, E80's two replicate tiles
CAP_CARD_MIN = 42       # 145 bursts: 17 governed a pass at E165's 16.2 s and 12 pinned at 13.5 s is 36.5 min; the cap cuts pass 5's tail if the gates run long
SLOT_MIN = 48
SUBSET_PASSES = (1, 2, 3)   # the registered subset for a short window: passes 1-3 (87 bursts, about 22 min)
SUBSET_CAP_MIN = 25
SUBSET_SLOT_MIN = 31
DRY_PASSES = (1, 2)     # the dry twin: passes 1-2 of a short order (dry_order in predictions-e175.json), at 1.5 s, the toy card only
STRATA_MHZ = ((0.0, 745.0), (745.0, 762.0), (762.0, 779.0), (779.0, 795.0))   # E175.md's governed strata, M10 carried's fallback clock
AFTER_E173_S = 600      # E175.md, The window: at least 10 minutes after E173's queue_end
MIN_PASSES = 2
C_LOG_SESSIONS = ("smoke", "stoptest-board", "s1")   # every session the registration requires to carry a C log (and any resume s2-s6 that ran
#                                                       a work launch); stoptest-die runs no launch and carries none


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def frozen(top=TOP):
    """the frozen inputs' registered sha256 (frozen-sha256-e175.json, written once from the committed tree before the kit's commit)"""
    with open(FROZEN_FILE) as f:
        return json.load(f)["files"]


def check_frozen(top=TOP, ccheck=True):
    """[] if every frozen input (and, with ccheck, Q139(k)'s three run-time files) is byte-identical to its registered sha256, else what differs"""
    bad = []
    items = dict(frozen(top))
    if ccheck:
        items.update(CCHECK_FROZEN)
    for rel, want in items.items():
        p = os.path.join(top, rel)
        got = sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, frozen {want}")
    return bad


def manifest(top=TOP):
    with open(os.path.join(top, MAN_REL)) as f:
        return {t["name"]: t for t in json.load(f)["tiles"]}


def tile_value(t):
    return f"file:{POOL_REL}/{t['file']}"


def label_of(name):
    return LABEL_PREFIX + name


def name_of(label):
    return label[len(LABEL_PREFIX):] if str(label).startswith(LABEL_PREFIX) else None


def is_pool_value(values):
    v = str(values)
    return v.startswith(f"file:{POOL_REL}/tiles/") and v.endswith(".bin") and ".." not in v


def check_tile(top, t):
    """None if the tile file is the manifest's (2,048 B; whole, A and B sha256), else why not"""
    p = os.path.join(top, POOL_REL, t["file"])
    if not os.path.isfile(p):
        return f"{t['name']}: {p} missing"
    with open(p, "rb") as f:
        b = f.read()
    if len(b) != 2048:
        return f"{t['name']}: {len(b)} bytes, not 2048"
    s = t["sha256"]
    got = {"whole": sha256_bytes(b), "a": sha256_bytes(b[:1024]), "b": sha256_bytes(b[1024:])}
    for k in ("whole", "a", "b"):
        if got[k] != s[k]:
            return f"{t['name']}: sha256 {k} {got[k]}, manifest {s[k]}"
    return None


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


_A2P = None


def a2p(top=TOP):
    """predict_pool8_a2 (Q142(p)'s entry point, 97765c0a), imported from its committed directory after its sha256 is checked; on import it does
    nothing, and its P() checks predict_pool8.py's SHA256SUMS and its own SHA256SUMS-a2 before importing the frozen predictor (A2-7)"""
    global _A2P
    if _A2P is None:
        want = frozen(top)[A2PY_REL]
        got = sha256_file(os.path.join(top, A2PY_REL))
        if got != want:
            raise SystemExit(f"refused: {A2PY_REL}: sha256 {got}, frozen {want}")
        sys.path.insert(0, os.path.join(top, PD_REL))
        import predict_pool8_a2 as A  # noqa: E402
        A.P().check_inputs()
        _A2P = A
    return _A2P


if __name__ == "__main__":
    bad = check_frozen()
    M = manifest()
    for t in M.values():
        why = check_tile(TOP, t)
        if why:
            bad.append(why)
    print(f"{len(M)} tiles; frozen inputs, Q139(k)'s files and tiles: {'OK' if not bad else 'BAD'}")
    for b in bad:
        print("  ", b)
    sys.exit(1 if bad else 0)
