#!/usr/bin/env python3
"""E174 (Q142(kg)): the constants and helpers every E174 file shares. Standard library only at import (the runner works on aifoundry1's python
without numpy); the scorer's model calls go through Q142(p)'s frozen predictor (e173_common.a2p()), at the desk.

E174 is blind pool 8 on aifoundry1 card 0 under its own governor, in E170's governed-burst form at the 800 MHz cap (6 s bursts from a cool die,
each pass opening with the zeros anchors, the hottest kinds last), with M10 carried by rule E through M9's aifoundry2 part and E170's card term
(kappa0 0.9463, the session's zeros level in full) as the primary, M9 carried the same way beside, and card 0's burst rise by M10's term c2
(0.2415 C per board W over 21.5 W). It runs only after E172 (pool 8 on card 1) has ended: never two sessions of ours on aifoundry1.

It reuses, unchanged:
  * E170's shared module (tools/claims-v3/e170/e170_common.py, lab b5ca3e78): the card term (kappa0, the zeros level, pred_card0, which
    Q142(p)'s predictor calls), E170's admission estimate formula, its stops, the alarm line, card 0's identity by continuity (E84's read),
    aifoundry1's three pinned binaries and E170's ettelem guard;
  * E173's shared module (tools/claims-v3/e173/e173_common.py): pool 8's paths, labels (b8-), the tile check and the predictor's import.

    python3 -B tools/claims-v3/e174/e174_common.py        # the frozen inputs and every pool tile, checked (desk or box)
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e170"))
sys.path.insert(0, os.path.join(HERE, "..", "e173"))
import e170_common as C170  # noqa: E402  (unchanged)
import e173_common as C173  # noqa: E402  (pool 8's paths, labels, tile check, the predictor's import)

EXPERIMENT = "E174"
REQUEST = "Q142(kg)"
CARD = "aifoundry1-c0"
DEVICE = "0"
LOCK0, LOCK1 = C170.LOCK0, C170.LOCK1

POOL_REL = C173.POOL_REL
MAN_REL = C173.MAN_REL
PRED_REL = f"{POOL_REL}/predictions-pool8-aifoundry1c0.json"
INTERVALS_REL = C173.INTERVALS_REL
LABEL_PREFIX = C173.LABEL_PREFIX
ZEROS_ANCHORS = C173.ZEROS_ANCHORS
manifest = C173.manifest
tile_value = C173.tile_value
label_of = C173.label_of
name_of = C173.name_of
is_pool_value = C173.is_pool_value
check_tile = C173.check_tile
rms = C173.rms
mean = C173.mean
sha256_file = C173.sha256_file
a2p = C173.a2p

# ---- aifoundry1's binaries and E170's guard, unchanged (E170.md, "What runs"; harness-e170.json)
CC_HOST_REL, CC_HOST_SHA256 = C170.CC_HOST_REL, C170.CC_HOST_SHA256
KERNEL_REL, KERNEL_SHA256 = C170.KERNEL_REL, C170.KERNEL_SHA256
ETTELEM_REL, ETTELEM_SHA256 = C170.ETTELEM_REL, C170.ETTELEM_SHA256
GUARD_REL = C170.GUARD_REL                 # tools/claims-v3/e170/ettelem_guard_e170.sh: config, sample, sptrace, uptime only; ET_DEVICES=0 only
WRAPPER_REL = C170.WRAPPER_REL
BOX_BINARIES = dict(C170.BOX_BINARIES)
CCHECK_FROZEN = dict(C170.CCHECK_FROZEN)

# ---- card 0's identity by continuity (E170's rule, unchanged: E84's read, never the firmware-revisions query)
E84_READ_EPOCH = C170.E84_READ_EPOCH
E84_UPTIME_MIN = C170.E84_UPTIME_MIN
UPTIME_TOL_MIN = C170.UPTIME_TOL_MIN
HOST_BOOT_BEFORE = C170.HOST_BOOT_BEFORE
WANT_CONFIG = dict(C170.WANT_CONFIG)
WANT_IDLE_MHZ = C170.WANT_IDLE_MHZ

# ---- the card term, the admission, the stops: E170's, unchanged
KAPPA0 = C170.KAPPA0
SWITCH_CEIL = C170.SWITCH_CEIL
E84_ZEROS_P800_KEYS = dict(C170.E84_ZEROS_P800_KEYS)
est_card0 = C170.est_card0
ADMIT_LINE_W = C170.ADMIT_LINE_W        # 60 W on the card-0 estimate
PEAK_LOCK_W = C170.PEAK_LOCK_W          # 62 W: E105's lock
TIER_B_ABOVE_W = C170.TIER_B_ABOVE_W    # 52 W: the hottest admitted kinds run last, in their own half
SAFETY = dict(C170.SAFETY)              # one die reading >= 72 C, or one board sample > 65.9 W
MIN_MHZ_ALARM = C170.MIN_MHZ_ALARM      # any sampler line under 590 MHz ends the session (the PMIC alarm's 300 MHz safe state)
CAP_CARD_MIN = C170.CAP_CARD_MIN        # 40
SLOT_MIN = C170.SLOT_MIN                # 45
SUBSET_PASSES = (1, 2, 4, 5)
SUBSET_CAP_MIN = 25
SUBSET_SLOT_MIN = 30
DRY_PASSES = (1, 2, 4)                  # the dry twin's short order (dry_order in predictions-e174.json), the toy card only
MIN_PASSES = 2
REST_W = 21.2                           # card 0's highest idle reading between E84's runs (E170's rest estimate)
SMOKE_TILES = ("int8.anchor7_zeros", "fp32.b_onebit_b20_one")   # the ramp: the low-power floor, then a tile E170 measured on this card
STOPTEST_TILE = "int8.anchor7_zeros"
C_LOG_SESSIONS = ("smoke", "stoptest-board", "s1")   # and any resume s2-s6 that ran a work launch; stoptest-die runs no launch
FROZEN_FILE = os.path.join(HERE, "frozen-sha256-e174.json")


def frozen(top=TOP):
    with open(FROZEN_FILE) as f:
        return json.load(f)["files"]


def check_frozen(top=TOP, ccheck=True):
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


if __name__ == "__main__":
    bad = check_frozen()
    M = manifest()
    for t in M.values():
        why = check_tile(TOP, t)
        if why:
            bad.append(why)
    print(f"{len(M)} tiles; frozen inputs, Q139(k)'s files and tiles: {'OK' if not bad else 'BAD'}")
    print(f"kappa0 {KAPPA0}")
    for b in bad:
        print("  ", b)
    sys.exit(1 if bad else 0)
