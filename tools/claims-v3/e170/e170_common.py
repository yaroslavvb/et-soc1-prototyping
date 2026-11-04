#!/usr/bin/env python3
"""E170 (Q141(w)): the constants and helpers every E170 file shares. Standard library only.

E170 is blind pool 7 on aifoundry1 card 0 under its own governor, in E165's governed-burst form (6 s bursts from a cool die, the zeros anchors
first), at the 800 MHz cap: card 0 holds 600 MHz under load only with its static TDP set to 0 (E118), and this round sets nothing, so E164's
600 MHz design cannot run there (E170.md, "Why not E164's 600 MHz design").

It reuses E165's shared module (tools/claims-v3/e165/e165_common.py, Q141(g), lab 3ef06839) unchanged for pool 7's frozen inputs, the tile
checks, the bootstraps and the frozen predictor of M9's aifoundry2 part, and adds what is card 0's:
  * the pins of aifoundry1's binaries (E157's C-logging host, the kernel, E84's ettelem build) and E170's ettelem guard;
  * E84's identity read of card 0 (31 Oct 2026, 15:42:00 PDT, module uptime 7,240 min), which the uptime-continuity gate carries;
  * the card term (E170.md, "The card term"): kappa0, card 0's switching scale against M9's aifoundry2 relation, frozen from committed card-0
    and aifoundry2 reads at one operating point (E118 against E72), and the session's own zeros level entering in full;
  * the admission estimate on card 0, the admission line, the stops, the tiers and the order's seed.

    python3 -B tools/claims-v3/e170/e170_common.py        # the frozen inputs and every pool tile, checked (desk or box)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e165"))
import e165_common as C165  # noqa: E402  (E165's shared module, unchanged)

EXPERIMENT = "E170"
REQUEST = "Q141(w)"
CARD = "aifoundry1-c0"
DEVICE = "0"
LOCK0 = "/run/lock/etsoc-shire0.lock"
LOCK1 = "/run/lock/etsoc-shire1.lock"

# ---- pool 7 and the frozen predictor: E165's, by name (lab 75802201, notes 3c9bb2ba; M9's aifoundry2 part 5b98bd5c / 245caffe / 5c98c0c5)
POOL_REL = C165.POOL_REL
MAN_REL = C165.MAN_REL
PRED_A2_REL = C165.PRED_REL                       # predictions-blind7-aifoundry2.json: M9.a2_q140l, M8, M7, M6 as frozen, and every D600
FROZEN = dict(C165.FROZEN)
CCHECK_FROZEN = dict(C165.CCHECK_FROZEN)
LABEL_PREFIX = C165.LABEL_PREFIX
ZEROS_ANCHORS = C165.ZEROS_ANCHORS
MODELS = C165.MODELS
check_frozen = C165.check_frozen
manifest = C165.manifest
tile_value = C165.tile_value
label_of = C165.label_of
name_of = C165.name_of
is_pool_value = C165.is_pool_value
check_tile = C165.check_tile
rms = C165.rms
mean = C165.mean
boot_rms_range = C165.boot_rms_range
paired_rms_diff = C165.paired_rms_diff
coverage_line = C165.coverage_line
m9a2 = C165.m9a2
sha256_file = C165.sha256_file

# ---- the parents' committed files this registration reads (sha256 checked by make_predictions_e170.py)
E165_PRED_REL = "tools/claims-v3/e165/predictions-e165.json"          # E165's references (Q140(l)'s end-to-end cells; the heat residuals)
E165_PRED_SHA256 = "7235109379f9a8f6af5057a205ea5b41c18049045706801ee46b8325380555a2"  # lab 3ef06839 (E165's registration)
E84_RESULTS_REL = "docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/results.json"
E84_RESULTS_SHA256 = "69c76c753a76a0e4b31dd7949a6dd9610c5a86f5aad82a0769d314664249c2ce"
E118_README_REL = "docs/reports/data/2026-11-01-e118-two-clock-card0/README.md"
E118_README_SHA256 = "88c559004b3f34ba494e6925fd6a42f6fbb5a615c7841b7a67828a27f150711a"
ADM_A2_REL = C165.ADM_REL                          # admission-aifoundry2-82w.json: per tile the largest of its three frozen 95% upper peaks
PARENT_SHA256 = {E165_PRED_REL: E165_PRED_SHA256, E84_RESULTS_REL: E84_RESULTS_SHA256, E118_README_REL: E118_README_SHA256}

# ---- aifoundry1's binaries in ~/nekko (E164's harness-e164.json box_binaries_sha256; E114's logs/e114-start.json for E84's ettelem build)
CC_HOST_REL = "build/ccheck/b/host/sparsity_host"   # Q139(k)'s C-logging host as E157 built it on aifoundry1 (E164 pins the same bytes)
CC_HOST_SHA256 = "4f0956ceabb107337c2996636ad712946aa135ecf33f72fb833bae72c8c5e585"
KERNEL_REL = "build/sparsity/kernel/sparsity.elf"   # E78's kernel on aifoundry1; the same bytes as E80's build/sparsity_t2 kernel on aifoundry2
KERNEL_SHA256 = "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24"
ETTELEM_REL = "build/ettelem-e84/ettelem"            # tools/claims-v3/dv2/ettelem-dv2 built on aifoundry1 for E84 (it honours ET_DEVICES)
ETTELEM_SHA256 = "87c1c38c995f0e3c6f442f361398dfc561ef1d4ed8b2304b9e9242d4a133dcc8"
GUARD_REL = "tools/claims-v3/e170/ettelem_guard_e170.sh"   # E170's allow-list in front of ETTELEM_REL (config, sample, sptrace, uptime only)
WRAPPER_REL = C165.WRAPPER_REL                       # tools/claims-v3/ccheck/sparsity_ccheck.sh (Q139(k), pinned in CCHECK_FROZEN)
BOX_BINARIES = {CC_HOST_REL: CC_HOST_SHA256, KERNEL_REL: KERNEL_SHA256, ETTELEM_REL: ETTELEM_SHA256}

# ---- card 0's identity, by continuity (E118's rule D2; never the firmware-revisions query, which writes the PMIC's firmware-management register)
E84_READ_EPOCH = 1793486520.286          # 2026-10-31 15:42:00.286 PDT: E84's ident/ident-154200.out, the uptime line's t_ms (E118's gov_e118.py)
E84_UPTIME_MIN = 5 * 1440 + 0 * 60 + 40  # 5 d 0 h 40 m on that read
E84_IDENTITY = "release 1.4.0, BL1 0.22.0, BL2 0.22.0, PMIC 1.6.1, minions 0.25.1 (E84 amendment A1; E114's start read; E118's continuity)"
UPTIME_TOL_MIN = 2.0                     # minute resolution on both reads (E118)
HOST_BOOT_BEFORE = "2026-10-31 15:42:00 PDT"   # the host must have booted before E84's read
WANT_CONFIG = {"tdp_w": 65, "temp_threshold_c": 65}   # E84, E114, E118 and E118's verifier (1 Nov 15:48:23 PST) all read 65 W / 65 C
WANT_IDLE_MHZ = 600                                   # the idle clock E84, E114 and E118 read between runs

# ---- the card term (E170.md, "The card term"), frozen before any E170 data
# kappa0: card 0's switching against aifoundry2's at one operating point (600 MHz, 0.518 V), the median of the five committed ratios in E118's
# README table "Three cards at 600 MHz now" (E118 on card 0 against E72 on aifoundry2, the same items and harness): the lq and lb full ladders,
# and the ones, pi and randn anchors over each card's zeros anchor.
KAPPA0_SOURCES = {
    "lq_full_ladder_fJ": [106.74, 113.22],
    "lb_full_ladder_fJ": [120.22, 125.45],
    "anchor_ones_over_zeros_w": [29.83 - 22.10, 35.16 - 27.06],
    "anchor_pi_over_zeros_w": [29.86 - 22.10, 35.26 - 27.06],
    "anchor_randn_over_zeros_w": [44.69 - 22.10, 51.05 - 27.06],
}


def kappa0_ratios():
    return {k: a / b for k, (a, b) in KAPPA0_SOURCES.items()}


def _median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


KAPPA0 = round(_median(list(kappa0_ratios().values())), 4)      # 0.9463
# card 0's 800 MHz zeros level, measured (E84 results.json cells.<type>/zeros.p800_w): used ONLY for the admission estimate, never to predict
E84_ZEROS_P800_KEYS = {"fp32": "fp32/zeros", "fp16": "fp16/zeros", "int8": "int8/zeros"}
SWITCH_CEIL = 0.95      # the admission estimate takes card 0's switching at 0.95 of aifoundry2's (every committed ratio is 0.88-0.96)

# ---- admission, stops, tiers, order (E170.md "Safety"; the round's brief, section 30: stops at least as strict as E164's 66 W / 72 C)
ADMIT_LINE_W = 60.0     # a tile runs only if its card-0 estimate (a 95% upper peak) is at most 60 W: 6 W under the board stop
PEAK_LOCK_W = 62.0      # after any run whose highest board sample reached 62 W, nothing at or above that run's estimate runs (E105's lock)
TIER_B_ABOVE_W = 52.0   # the hottest admitted kinds (estimate above 52 W) run last, in their own half of the session
SAFETY = {"abs_stop_c": 72, "board_cap_w": 65.9, "cap_consecutive": 1}   # one die reading >= 72 C, or one board sample > 65.9 W
MIN_MHZ_ALARM = 590.0   # any sampler line of a run under 590 MHz (the PMIC alarm's 300 MHz POWER_SAFE point) halts the session
ORDER_SEED = 170
PASSES = (1, 2, 3)
BOOT_DRAWS = 20000
BOOT_SEED = 170
PAIRED_DRAWS = 20000
PAIRED_SEED = 1701
RATIO_DRAWS = 5000
RATIO_SEED = 1702
MIN_TILES = 8           # a rule over fewer scored tiles is NOT SCORED
MIN_TILES_M1 = 10       # rank 1's comparison needs at least 10 priority-1 new kinds
CAP_CARD_MIN = 40       # the session's cap (run_e119's: a run starts only if it fits)
SLOT_MIN = 45


def est_card0(adm_a2_w, p800_a2_w, pz_a2_w, z0_w):
    """The admission estimate on card 0 (conservative, never a prediction): aifoundry2's frozen 95% upper peak (E165's admission value), less the
    gap between aifoundry2's predicted 800 MHz zeros level and card 0's measured one (E84), less 5% of the tile's predicted switching at 800 MHz
    (card 0 switches at 0.88-0.96 of aifoundry2 in every committed pair, so 0.95 over-states it)."""
    return adm_a2_w - (pz_a2_w - z0_w) - (1.0 - SWITCH_CEIL) * (p800_a2_w - pz_a2_w)


def zeros_level(anchors, t, die_starts, kT, T_ref, min_mhz=795.0):
    """The card term's level (E170.md): the session's own zeros level for format t at a tile's die starts. Per format the mean over the
    format's counted anchor bursts at >= min_mhz of burst_w referred to T_ref by kT; a format with none takes the mean of the other formats'
    levels; then referred to the mean of the tile's die starts. None if no anchor burst exists."""
    lev = {}
    for f, rr in (anchors or {}).items():
        rr = [r for r in rr if float(r["burst_mhz"]) >= min_mhz]
        if rr:
            lev[f] = sum(float(r["burst_w"]) - kT * (float(r["die_start"]) - T_ref) for r in rr) / len(rr)
    if not lev:
        return None
    L = lev.get(t, sum(lev.values()) / len(lev))
    Ts = [float(x) for x in die_starts] if die_starts else [T_ref]
    return L + kT * (sum(Ts) / len(Ts) - T_ref)


def pred_card0(D, t, anchors, die_starts, D_band_hw=0.0, kappa=None, full_level=True):
    """THE PRIMARY (E170.md "The primary, exactly"): M9's aifoundry2 part, recomputed through its frozen burst() (E165's call, unchanged), and the
    card term: burst D = kappa0 x burst()'s burst_D_w, board = the session's own zeros level at the tile's die starts + that D. The clock and the
    die rise are burst()'s, the rise taken on the card-0 board through the frozen burst heat law. full_level False gives E165's form unchanged
    (burst()'s own board, beta 0.648 of the anchor offset), reported beside."""
    A2 = m9a2()
    k = KAPPA0 if kappa is None else kappa
    b = A2.burst(D, t, anchors=anchors, die_starts=die_starts, D_band_hw=D_band_hw)
    out = {"burst_mhz": b["burst_mhz"], "group": b["group"], "a2_burst_D_w": b["burst_D_w"], "a2_board_w": b["burst_board_w"],
           "a2_zeros_board_w": b["zeros_board_w"], "kappa": k}
    if not full_level:
        out["burst_board_w"] = b["burst_board_w"]
        out["burst_D_w"] = b["burst_D_w"]
    else:
        Z = zeros_level(anchors, t, die_starts, A2.KT, A2.TREF)
        if Z is None:
            return None
        out["zeros_level_w"] = round(Z, 3)
        out["burst_D_w"] = round(k * b["burst_D_w"], 3)
        out["burst_board_w"] = round(Z + k * b["burst_D_w"], 3)
    H = A2.HEAT
    out["burst_die_rise_c"] = round(H["k_used_c_per_w"] * (out["burst_board_w"] - H["P_idle_w"]), 3)
    bd = A2.BANDS[b["group"]]
    out["burst_board_95"] = [round(out["burst_board_w"] - bd["q95_abs_board_w"], 3), round(out["burst_board_w"] + bd["q95_abs_board_w"], 3)]
    out["burst_mhz_95"] = [round(b["burst_mhz"] - bd["q95_abs_mhz"], 2), round(min(800.0, b["burst_mhz"] + bd["q95_abs_mhz"]), 2)]
    out["burst_die_rise_95"] = [round(out["burst_die_rise_c"] - H["q95_abs_c"], 3), round(out["burst_die_rise_c"] + H["q95_abs_c"], 3)]
    return out


def boot_ratio_ci(meas, pred, draws=RATIO_DRAWS, seed=RATIO_SEED):
    """the median over tiles of meas/pred and its 95% percentile interval over tiles drawn with replacement; None under 2 tiles"""
    r = [m / p for m, p in zip(meas, pred) if p]
    if len(r) < 2:
        return None
    import random
    rng = random.Random(seed + 104729 * len(r))
    vals = []
    for _ in range(draws):
        vals.append(_median([r[rng.randrange(len(r))] for _ in range(len(r))]))
    vals.sort()
    return {"median": _median(r), "ci95": [vals[int(0.025 * (draws - 1))], vals[int(0.975 * (draws - 1))]], "n": len(r)}


if __name__ == "__main__":
    bad = check_frozen()
    M = manifest()
    for t in M.values():
        why = check_tile(ROOT, t)
        if why:
            bad.append(why)
    print(f"{len(M)} tiles; frozen inputs, Q139(k)'s files and tiles: {'OK' if not bad else 'BAD'}")
    print(f"kappa0 {KAPPA0} from {json.dumps({k: round(v, 6) for k, v in kappa0_ratios().items()})}")
    for b in bad:
        print("  ", b)
    sys.exit(1 if bad else 0)
