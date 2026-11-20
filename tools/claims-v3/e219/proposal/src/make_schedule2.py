#!/usr/bin/env python3
"""1119-mmsweep5: the arm table and the session schedules from the sweep's plan, written at the desk (Python's own modules
only). The plan (plan.json in the request's folder, beside src/; its format is the request's PLAN-FORMAT) names the tiles,
the arms and each card's sessions as blocks of arm ids; this generator applies the first sweep's laws (1116-mmsweep's
src/make_schedule.py, copied here unchanged where marked) to make the schedules the unchanged runner reads.

    python3 -I -B src/make_schedule2.py [--plan P]           writes src/arms.json, src/sched/<card>-<S>.json and the plan's
                                                             tiles src/tiles/<type>/<name>.bin (src/tiles_gen.py), prints a
                                                             summary; removes schedules and plan tiles the plan no longer makes
    python3 -I -B src/make_schedule2.py --check [--plan P]   re-makes them in memory and compares with the files (MAKE CHECK
                                                             PASS); with no plan.json and nothing made: PASS (nothing to make)
    python3 -I -B src/make_schedule2.py --plan P --out DIR   writes into DIR/src/ instead (the desk tests' toy plan)
    ... [--priors LIST]                                      also pairs the plan's tiles with the prior tile files LIST names
                                                             (THE WIDER CHECK; the plan's own "priors" are read either way)

The laws, as in the first sweep:
  - est_peak_w: the arm's estimated board peak on the card, from the lab's measured bursts of this binary by regime, type and
    kind on aifoundry2 at 800 MHz, scaled by its shire share and moved to the other cards by their rest and clock factor, +3 W.
    A plan tile is estimated as the row its est_as names (default rnd), and never under zeros + (rnd - zeros) x h, h its toggle
    ratio to the lab's randn tile (src/tiles_gen.py): a pattern that flips more bits than random data is estimated above it.
  - the planning lines (aifoundry2 80 W, card 1 70 W, card 0 52 W): an arm whose estimate is above the card's line is REFUSED
    (the plan is not made); card 0 takes zeros, ones, int8 rnd and plan tiles only (low power), a tile of a drawn gen counting
    as rnd;
  - the time role: on aifoundry2 an arm estimated at or over 69.8 W runs at the governor's burst cap: role `time`;
  - the forms: burst (10 s at rest, one 6 s process, 5 s after) and sus3 (20 s, three processes, 20 s) as the plan says; null
    (20 s, a 6.5 s window with no process, 20 s);
  - the order: the anchor (4 x 8 x 8 int8 rnd) first, after every block and last; a null after the opening anchor (unless the
    first block opens with its own), right after the session's hottest arm, and through every block with a small-signal (sus3)
    unit (one before every two small units, the small units first, one at the block's end; a block may say "nulls": "none");
    a session left with fewer than 4 nulls gets one more before each block's closing anchor, from the last block back;
    inside a block, units (one shape's kinds back to back) in a seeded shuffle; each unit's own seeded order; a session with
    "reverse": true runs its blocks in reverse order and each unit's kinds mirrored (the first sweep's S2);
  - the planned length (each run's die gate at 12 s, the opening rest, the smoke and the stop-path test), the rule (the next 5
    minutes past planned + 5) and the cap (rule + 7); a session over this sweep's size (rule 65, cap 72) is REFUSED.
The plan's tiles (src/tiles_gen.py): each made, read back and its check of C meaningful at every K an arm runs it at; and THE
PAIR CHECK: a tile set with two tiles of one type at equal input toggles whose counted switches differ, or are not given, is
REFUSED (the stopped glitch-contrast form; nothing is made). With the plan's "priors" ({"path", "sha256"}: a desk list of
the tile files run before, never in src/) or --priors LIST, the pair check is also THE WIDER CHECK (X15 read wider: each plan
tile against the lab's nine kind files and every prior of its type; src/tiles_gen.py). The summary prints the pair check's
last lines. The made files are as before: the priors are read at the desk and written nowhere.
THE BLOCK ARMS (this sweep): a plan arm with an "arm" field runs the host's own block, stream or TenB arm through the same
command line (the host's grammar, src/mms_common.py arm_of: gemm<B>, gemmc<B>, gemmh<B> with r<R> and s; mm<N>; tenb), on the
whole chip, with the lab's kinds only; gemmv, gemmnc and mmp are refused (no bound or no price for them here), as is B or R
past 32 and N past 256 (one pass at most 65,536 ops a minion: every launch stays about 0.5 s and the process a 6 s burst under
`timeout 10`). Its estimate is the l2 row's (E105's by-column block): every measured by-column and packed walk's mean in work
reads under it; gemmh's power was never measured, and the gemmc1 walk's largest board sample on card 1 passed it, so for random
block arms the binding gate is the desk's band-top gate, outside `src/`. It is never under the lab's measured burst of the
stream and TenB loops on card 1 (E37, E39, E101; every kind taken as random data's), and a block arm over 66.6 W on card 1 is
refused. The anchor, the smoke, the null and order laws and every gemmL arm are as before.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tiles_gen as TG  # noqa: E402
import mms_common as MC  # noqa: E402   (the arm grammar only: arm_of)

KIT = "1119-mmsweep5"
RULE_MAX_MIN, CAP_MAX_MIN = 65.0, 72.0     # this sweep's session size: at most 65 planned card-minutes by the rule, cap 72
MIN_NULLS = 4                              # null runs a session holds at least (the first sweep's schedule check)
FIRST_SWEEP_K = {"fp32": 16384, "fp16": 8192, "int8": 32768}   # the first sweep's largest K a type (printed past it, not refused)
SESSION_RE = re.compile(r"^S[1-9]$")
FAMILY_RE = re.compile(r"^[A-Za-z0-9_.+-]{1,24}$")
MASK_RE = re.compile(r"^0x[0-9a-f]{1,8}$")

# ---- copied unchanged from the first sweep's src/make_schedule.py (sha256 b939b5c6...): the types, kinds, the lab's tiles
TYPES = ("fp32", "fp16", "int8")
KINDS = ("rnd", "zeros", "ones")
FULL = "0xffffffff"
TILE = {("fp32", "rnd"): "randn:src/tiles/fp32/randn.bin", ("fp32", "zeros"): "tiles:src/tiles/fp32/zeros.bin",
        ("fp32", "ones"): "tiles:src/tiles/fp32/ones.bin",
        ("fp16", "rnd"): "randn:src/tiles/fp16/randn.bin", ("fp16", "zeros"): "tiles:src/tiles/fp16/zeros.bin",
        ("fp16", "ones"): "tiles:src/tiles/fp16/ones.bin",
        ("int8", "rnd"): "randn:src/tiles/int8/full.bin", ("int8", "zeros"): "tiles:src/tiles/int8/zeros.bin",
        ("int8", "ones"): "tiles:src/tiles/int8/ones.bin"}
K_PER_KB = {"fp32": 512, "fp16": 1024, "int8": 2048}
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}

# the cards: planning line, rest, kinds (the first sweep's CARDS, its fixed session lists left out: the plan names them)
CARDS = {"a2c0": {"line_w": 80.0, "rest_w": 22.5, "kinds_ok": KINDS},
         "a1c1": {"line_w": 70.0, "rest_w": 31.0, "kinds_ok": KINDS},
         "a1c0": {"line_w": 52.0, "rest_w": 18.5, "kinds_ok": ("zeros", "ones"), "int8_rnd_ok": True}}
CAP_EST_W = 69.8      # aifoundry2: an arm estimated at or over this runs at the governor's burst cap (E146: 70.3-70.5 W): role `time`
ANCHOR = (4, 8, 8, "int8", "rnd", FULL)
SMOKE = [(1, 1, 4, "fp32", "zeros", FULL), (1, 1, 4, "fp16", "ones", FULL), (1, 1, 4, "int8", "rnd", FULL)]
FORMS = {"burst": {"rest_s": 10.0, "tail_s": 5.0, "nproc": 1},
         "sus3": {"rest_s": 20.0, "tail_s": 20.0, "nproc": 3},
         "null": {"rest_s": 20.0, "tail_s": 20.0, "nproc": 0, "window_s": 6.5}}
GATE_PLAN_S = 12.0    # the planned die-gate wait a run
OPEN_PLAN_S = 60.0 + 3 * 13.0 + 20.0   # the opening rest, the smoke and the stop-path test


def footprint_mb(mb, nb, kb):
    """A + B + C in MB on the whole chip (the same in every type: an A block is 2 MB, a B block 1 MB, a C block 2 MB)."""
    return 2 * mb * kb + nb * kb + 2 * mb * nb


def regime(mb, nb, kb):
    """Where the lab's runs of this binary put a full-chip shape: 'l2' (1 x 1 x 1: E105's by-column block), 'l3' (footprint
    up to 32 MB: E146's L1-L8, E136's 2,048 x 1,024 x 1,024), else 'dram' (E136's 4,096^3, E146's D2-D8, E190)."""
    if (mb, nb, kb) == (1, 1, 1):
        return "l2"
    return "l3" if footprint_mb(mb, nb, kb) <= 32 else "dram"


# aifoundry2 card 0, 800 MHz, measured board W in the burst's first second at 800 MHz (E105 by-column block; E136, E146 and
# E190 bursts), taken high; (regime, type, kind) -> W. ones: E105's by-column fp32 ones (55.7 W) and vendor-stride ones
# (46.5 W); fp16 and int8 ones are not measured in this binary: taken between zeros and rnd, high.
A2_W = {("l2", "fp32", "rnd"): 95.2, ("l2", "fp16", "rnd"): 89.3, ("l2", "int8", "rnd"): 66.8,
        ("l2", "fp32", "ones"): 55.7, ("l2", "fp16", "ones"): 58.0, ("l2", "int8", "ones"): 55.0,
        ("l2", "fp32", "zeros"): 38.8, ("l2", "fp16", "zeros"): 38.8, ("l2", "int8", "zeros"): 41.0,
        ("l3", "fp32", "rnd"): 70.3, ("l3", "fp16", "rnd"): 70.0, ("l3", "int8", "rnd"): 47.0,
        ("l3", "fp32", "ones"): 50.0, ("l3", "fp16", "ones"): 52.0, ("l3", "int8", "ones"): 45.0,
        ("l3", "fp32", "zeros"): 38.0, ("l3", "fp16", "zeros"): 38.0, ("l3", "int8", "zeros"): 38.0,
        ("dram", "fp32", "rnd"): 61.0, ("dram", "fp16", "rnd"): 61.0, ("dram", "int8", "rnd"): 47.0,
        ("dram", "fp32", "ones"): 50.0, ("dram", "fp16", "ones"): 50.0, ("dram", "int8", "ones"): 45.0,
        ("dram", "fp32", "zeros"): 38.0, ("dram", "fp16", "zeros"): 38.0, ("dram", "int8", "zeros"): 38.0}
A2_BASE_W = 30.0      # aifoundry2 at rest (22-24 W) plus its 800 MHz busy base (about 8 W): the part a lift sits on
A1C1_FACTOR = {"l2": 0.50, "l3": 0.65, "dram": 0.75}   # card 1 at 600 MHz: lift over a2's base x this (E190: 0.70-0.77 in dram)


def shires_of(mask):
    return bin(int(mask, 16)).count("1")


def est_peak_w(card, mb, nb, kb, t, kind, mask):
    """The arm's estimated board peak on the card, W (rounded up to 0.1 W), with 3 W of margin."""
    w = A2_W[(regime(mb, nb, kb), t, kind)]
    lift = (w - A2_BASE_W) * shires_of(mask) / 32.0
    if card == "a2c0":
        p = A2_BASE_W + lift
    elif card == "a1c1":
        p = CARDS["a1c1"]["rest_w"] + lift * A1C1_FACTOR[regime(mb, nb, kb)]
    else:   # a1c0: its own governor as a2, its rest about 4 W lower
        p = A2_BASE_W - (CARDS["a2c0"]["rest_w"] - CARDS["a1c0"]["rest_w"]) + lift
    return round(p + 3.0 + 0.049, 1)
# ---- (end of the copied laws; the functions below that say "as the first sweep's" keep its rules for its kinds)

# ---- THE BLOCK ARMS (this sweep's addition; every gemmL arm, the anchor and the smoke are estimated and made as before)
BLOCK_OK = ("gemm", "gemmc", "gemmh", "mm", "tenb")
BLOCK_REFUSED = {
    "gemmv": "the vendor-stride walk has no price in the sweep's model: left out",
    "gemmnc": "the walk without cooperative loads is not bounded by the lab's measured bursts on these cards: left out",
    "mmp": "the private-pool stream (its pools past the L2) has no price in the sweep's model: left out",
    "gemmL": "a gemmL arm is written with mb, nb, kb (no arm field)"}
BLOCK_MAX_B, BLOCK_MAX_R, BLOCK_MAX_N = 32, 32, 256    # one pass at most 65,536 ops a minion (about 0.16 s at 1,500 cycles an op)
BLOCK_PLAN_W = {"a1c1": 66.6}                          # card 1: a block arm estimated above this is refused (the sweep's plan level)
# the lab's measured bursts of the stream and TenB loops, card 1 at 600 MHz, board W over idle, random data, the highest of
# each type: E37's mm16 (fp32, fp16, int8); E39's tenb (fp16; int8 the highest of its kinds) and E101's tenb fp32 (aifoundry3,
# pinned at the same 600 MHz). Taken for every kind of these loops (no zeros or ones of them measured on these cards).
LOOP_LIFT_A1C1 = {"mm": {"fp32": 27.2, "fp16": 28.6, "int8": 33.1}, "tenb": {"fp32": 28.8, "fp16": 27.4, "int8": 17.2}}


def est_block_w(card, a):
    """A block, stream or TenB arm's estimated board peak on the card, W (rounded up to 0.1 W, with 3 W of margin): the l2
    row's (est_peak_w at 1 x 1 x 1 on the whole chip: E105's by-column block, gemmc1, measured on aifoundry2 at 800 MHz by type
    and kind; every measured by-column and packed walk's mean in work reads under it; gemmh's power was never measured, and the
    gemmc1 walk's largest board sample on card 1 passed it, so for random block arms the binding gate is the desk's band-top
    gate, outside src/), and for the stream and TenB loops never under the lab's measured burst (LOOP_LIFT_A1C1 over card 1's
    rest; on the governed cards its lift over the l2 factor, as the l2 row moves between the cards)."""
    w = est_peak_w(card, 1, 1, 1, a["type"], a["kind"], FULL)
    lift = LOOP_LIFT_A1C1.get(a["family"], {}).get(a["type"])
    if lift is not None:
        if card == "a1c1":
            p = CARDS["a1c1"]["rest_w"] + lift
        elif card == "a2c0":
            p = A2_BASE_W + lift / A1C1_FACTOR["l2"]
        else:
            p = A2_BASE_W - (CARDS["a2c0"]["rest_w"] - CARDS["a1c0"]["rest_w"]) + lift / A1C1_FACTOR["l2"]
        w = max(w, round(p + 3.0 + 0.049, 1))
    return w


def block_rec(a):
    """A plan arm with an "arm" field: the host's block, stream or TenB arm, checked and completed (the first sweep's arm
    fields, the host's counts beside them)."""
    need = ("id", "arm", "type", "kind", "shires", "form", "families")
    miss = [k for k in need if k not in a]
    if miss:
        raise ValueError(f"arm {a.get('id')}: missing {miss}")
    if any(k in a for k in ("mb", "nb", "kb")):
        raise ValueError(f"arm {a['id']}: a block arm has no mb, nb, kb (its arm token says what runs)")
    tok, t, kind, mask = a["arm"], a["type"], a["kind"], a["shires"]
    if t not in TYPES:
        raise ValueError(f"arm {a['id']}: type {t!r}")
    if kind not in KINDS:
        raise ValueError(f"arm {a['id']}: kind {kind!r}: a block arm runs the lab's kinds only (rnd, zeros, ones)")
    g = MC.arm_of(f"{tok}:x:y") if isinstance(tok, str) and re.fullmatch(r"[A-Za-z0-9]+", tok) else None
    if g is None:
        raise ValueError(f"arm {a['id']}: arm {tok!r} is not the host's grammar as this kit spells it (gemm|gemmc|gemmh<B>[r<R>][s], "
                         f"mm<N>, tenb; digits without a leading zero)")
    fam = g["family"]
    if fam in BLOCK_REFUSED:
        raise ValueError(f"arm {a['id']}: {fam}: {BLOCK_REFUSED[fam]}")
    if fam not in BLOCK_OK:
        raise ValueError(f"arm {a['id']}: family {fam!r}")
    if g["kernel"] == "block":
        if g["repeats"] == 1 and "r" in tok[len(fam):]:
            raise ValueError(f"arm {a['id']}: r1 is the default: write {fam}{g['nblocks']}{'s' if g['c_shared'] else ''}")
        if g["nblocks"] > BLOCK_MAX_B or g["repeats"] > BLOCK_MAX_R:
            raise ValueError(f"arm {a['id']}: blocks {g['nblocks']}, repeats {g['repeats']}: at most {BLOCK_MAX_B} and "
                             f"{BLOCK_MAX_R} here (one pass at most 65,536 ops a minion)")
    if g["kernel"] == "stream" and g["ntiles"] > BLOCK_MAX_N:
        raise ValueError(f"arm {a['id']}: {g['ntiles']} pairs a pool: at most {BLOCK_MAX_N} here (the pool inside the L2)")
    if mask != FULL:
        raise ValueError(f"arm {a['id']}: shires {mask!r}: a block, stream or TenB arm runs on the whole chip ({FULL})")
    if a["form"] not in ("burst", "sus3"):
        raise ValueError(f"arm {a['id']}: form {a['form']!r}")
    fams = a["families"]
    if not isinstance(fams, list) or not fams or not all(isinstance(f, str) and FAMILY_RE.match(f) for f in fams):
        raise ValueError(f"arm {a['id']}: families are short tags ([A-Za-z0-9_.+-], 1-24 characters)")
    if a.get("priority", 1) not in (1, 2, 3):
        raise ValueError(f"arm {a['id']}: priority {a.get('priority')!r}")
    want = f"{tok}-{t}-{kind}"
    if a["id"] != want:
        raise ValueError(f"arm id {a['id']!r} is not its fields' id {want!r}")
    files = TILE[(t, kind)].split(":", 1)[1]
    values = f"{tok}:" + (f"tiles:{files}" if fam == "tenb" else TILE[(t, kind)])   # tenb runs one held pair: gen tiles
    kop = MC.K_OP[t]
    if g["kernel"] == "block":
        M, N_, K = 1024, 512, kop * g["kt"] * g["nblocks"] * g["repeats"]
    else:
        M, N_, K = 16384, 16, kop * (g["ntiles"] if fam == "mm" else 1)
    rec = {"id": want, "test": "fma", "arm": tok, "family": fam, "kernel": g["kernel"], "type": t, "kind": kind, "shires": mask,
           "values": values, "M": M, "N": N_, "K": K, "footprint_mb": round(g["footprint_mb"], 6),
           "ops_per_minion_pass": g["ops_pass"], "macs_per_op": MACS_PER_OP[t], "families": sorted(set(fams)),
           "small": a["form"] == "sus3", "form": a["form"], "priority": a.get("priority", 1),
           "first_passes": g["first_passes"], "check_passes": g["check_passes"]}
    for k in ("nblocks", "repeats", "c_shared", "layout", "coop", "kt", "ntiles", "private"):
        if k in g:
            rec[k] = g[k]
    if M * N_ * K != 1024 * g["ops_pass"] * MACS_PER_OP[t]:
        raise ValueError(f"arm {want}: M N K {M} {N_} {K} are not the host's multiply-adds a pass")
    return rec


def est_of(P, card, a):
    """The arm's estimate on the card: est_arm_w for a gemmL arm (as before), est_block_w for a block, stream or TenB arm."""
    if "arm" in a:
        return est_block_w(card, a)
    return est_arm_w(P, card, a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"])


def mask_suffix(mask):
    """The arm id's shire part: '' on the whole chip; -s<n> for the n low shires (the first sweep's masks 0x1, 0xf, 0xffff);
    -m<hex> for any other mask (two masks of one count are two arms)."""
    if mask == FULL:
        return ""
    n = shires_of(mask)
    return f"-s{n}" if int(mask, 16) == (1 << n) - 1 else f"-m{mask[2:]}"


def arm_id(mb, nb, kb, t, kind, mask):
    """As the first sweep's, with mask_suffix for a mask that is not the low shires."""
    return f"{mb}x{nb}x{kb}-{t}-{kind}{mask_suffix(mask)}"


class Plan:
    """The plan, read and checked: its tiles (built and read by src/tiles_gen.py) and its arms."""

    def __init__(self, plan, root, priors=None):
        if plan.get("kit") != KIT:
            raise ValueError(f"the plan's kit is {plan.get('kit')!r}, not {KIT!r}")
        if not isinstance(plan.get("seed"), str) or not plan["seed"]:
            raise ValueError("the plan's seed is a non-empty string")
        self.seed = plan["seed"]
        self.raw = plan
        self.tiles = {}
        built = TG.build(plan, root, priors=priors)
        for rel, (data, rec) in built.items():
            self.tiles[rec["name"]] = {"data": data, "rec": rec, "spec": next(x for x in plan["tiles"] if x["name"] == rec["name"])}
        self.ref = {t: TG.rnd_ref(t, root) for t in TYPES}


def tile_values(P, t, kind):
    x = P.tiles[kind]
    if x["rec"]["type"] != t:
        raise ValueError(f"tile {kind} is {x['rec']['type']}, the arm {t}")
    return f"{x['spec'].get('gen', 'tiles')}:{TG.tile_rel(t, kind)}"


def est_arm_w(P, card, mb, nb, kb, t, kind, mask):
    """est_peak_w for the first sweep's kinds; a plan tile: the row its est_as names, never under the toggle guard."""
    if kind in KINDS:
        return est_peak_w(card, mb, nb, kb, t, kind, mask)
    x = P.tiles[kind]
    base = est_peak_w(card, mb, nb, kb, t, x["spec"].get("est_as", "rnd"), mask)
    z = est_peak_w(card, mb, nb, kb, t, "zeros", mask)
    r = est_peak_w(card, mb, nb, kb, t, "rnd", mask)
    h = max(x["rec"]["toggle"]["a"], x["rec"]["toggle"]["b"]) / P.ref[t]
    guard = round(z + (r - z) * h + 0.049, 1)
    return max(base, guard)


def arm_rec(P, a):
    """The plan's arm, checked and completed with the first sweep's arm fields (an "arm" field: block_rec)."""
    if "arm" in a:
        return block_rec(a)
    need = ("id", "mb", "nb", "kb", "type", "kind", "shires", "form", "families")
    miss = [k for k in need if k not in a]
    if miss:
        raise ValueError(f"arm {a.get('id')}: missing {miss}")
    mb, nb, kb, t, kind, mask = a["mb"], a["nb"], a["kb"], a["type"], a["kind"], a["shires"]
    if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 1 for v in (mb, nb, kb)):
        raise ValueError(f"arm {a['id']}: mb, nb, kb are whole numbers from 1")
    if t not in TYPES:
        raise ValueError(f"arm {a['id']}: type {t!r}")
    if not isinstance(mask, str) or not MASK_RE.match(mask) or int(mask, 16) == 0 or (mask != FULL and mask != hex(int(mask, 16))):
        raise ValueError(f"arm {a['id']}: shires {mask!r}: a lowercase hex mask with no leading zeros, {FULL} for the whole chip")
    if kind not in KINDS and kind not in P.tiles:
        raise ValueError(f"arm {a['id']}: kind {kind!r} is neither rnd, zeros, ones nor a tile of the plan")
    if a["form"] not in ("burst", "sus3"):
        raise ValueError(f"arm {a['id']}: form {a['form']!r}")
    fams = a["families"]
    if not isinstance(fams, list) or not fams or not all(isinstance(f, str) and FAMILY_RE.match(f) for f in fams):
        raise ValueError(f"arm {a['id']}: families are short tags ([A-Za-z0-9_.+-], 1-24 characters)")
    if a.get("priority", 1) not in (1, 2, 3):
        raise ValueError(f"arm {a['id']}: priority {a.get('priority')!r}")
    want = arm_id(mb, nb, kb, t, kind, mask)
    if a["id"] != want:
        raise ValueError(f"arm id {a['id']!r} is not its fields' id {want!r}")
    if (mb, nb, kb, t, kind, mask) == ANCHOR:
        raise ValueError(f"arm {want}: the anchor is the generator's (first, after every block and last); leave it out")
    values = f"gemmL{mb}x{nb}x{kb}:" + (TILE[(t, kind)] if kind in KINDS else tile_values(P, t, kind))
    rec = {"id": want, "test": "fma", "mb": mb, "nb": nb, "kb": kb, "type": t, "kind": kind, "shires": mask, "values": values,
           "M": 1024 * mb, "N": 512 * nb, "K": K_PER_KB[t] * kb, "footprint_mb": footprint_mb(mb, nb, kb),
           "ops_per_minion_pass": mb * nb * 2 * kb * 32, "macs_per_op": MACS_PER_OP[t], "families": sorted(set(fams)),
           "small": a["form"] == "sus3", "form": a["form"], "priority": a.get("priority", 1)}
    if kind not in KINDS:
        chk = P.tiles[kind]["rec"]["checks"].get(str(rec["K"]))
        if not chk or "bad" in chk:
            raise ValueError(f"arm {want}: tile {kind} at K {rec['K']}: {chk}")
        rec["tile_check"] = chk.get("result")
    return rec


def anchor_rec():
    mb, nb, kb, t, kind, mask = ANCHOR
    return {"id": arm_id(*ANCHOR), "test": "fma", "mb": mb, "nb": nb, "kb": kb, "type": t, "kind": kind, "shires": mask,
            "values": f"gemmL{mb}x{nb}x{kb}:{TILE[(t, kind)]}", "M": 1024 * mb, "N": 512 * nb, "K": K_PER_KB[t] * kb,
            "footprint_mb": footprint_mb(mb, nb, kb), "ops_per_minion_pass": mb * nb * 2 * kb * 32, "macs_per_op": MACS_PER_OP[t],
            "families": ["anchor"], "small": False, "form": "burst", "priority": 1}


def smoke_rec(mb, nb, kb, t, kind, mask):
    return {"id": arm_id(mb, nb, kb, t, kind, mask), "values": f"gemmL{mb}x{nb}x{kb}:{TILE[(t, kind)]}"}


def card_ok(P, card, a):
    """'' when the card takes the arm (as the first sweep's: its estimate at or under the line; card 0 of aifoundry1 takes zeros,
    ones and int8 rnd, and plan tiles, only), else why. A plan tile of a drawn gen (the host draws its pool: random data) counts
    as rnd for the kinds rule, so card 0 takes it in int8 only."""
    c = CARDS[card]
    kind = a["kind"]
    if kind not in KINDS and P.tiles[kind]["spec"].get("gen", "tiles") != "tiles":
        kind = "rnd"
    if kind == "rnd" and kind not in c["kinds_ok"] and not (a["type"] == "int8" and c.get("int8_rnd_ok")):
        return f"{a['id']}: {card} takes no {a['type']} rnd (low power)" + ("" if kind == a["kind"] else
                                                                             f": tile {a['kind']} is a drawn pool")
    w = est_of(P, card, a)
    if w > c["line_w"]:
        return f"{a['id']}: estimated {w} W on {card}, over its planning line {c['line_w']:g} W"
    if "arm" in a and card in BLOCK_PLAN_W and w > BLOCK_PLAN_W[card]:
        return f"{a['id']}: estimated {w} W on {card}, over the block arms' plan level {BLOCK_PLAN_W[card]:g} W there"
    return ""


def role_of(P, card, a):
    if card == "a2c0" and est_of(P, card, a) >= CAP_EST_W:
        return "time"
    return "arm"


def form_of(a):
    return "sus3" if a["small"] else "burst"


def kind_key(kind):
    return (KINDS.index(kind), "") if kind in KINDS else (len(KINDS), kind)


def shape_of(a):
    """An arm's shape: (0, mb, nb, kb, '') for a gemmL arm, (1, 0, 0, 0, token) for a block, stream or TenB arm (after every
    gemmL shape of its mask and type, by token)."""
    return (1, 0, 0, 0, a["arm"]) if "arm" in a else (0, a["mb"], a["nb"], a["kb"], "")


def unit_name(a):
    """A unit's name (its kind 'u'): the gemmL arm id's form, or <token>-<type>-u."""
    if "arm" in a:
        return f"{a['arm']}-{a['type']}-u"
    return arm_id(a["mb"], a["nb"], a["kb"], a["type"], "u", a["shires"])


def units_of(arms):
    """Units: the data kinds of one arm shape (mb, nb, kb, type, mask; a block arm's token, type, mask) in a block, run back to
    back (as the first sweep's; plan tiles after rnd, zeros, ones, by name). gemmL units sort as before: mask, type, mb, nb, kb."""
    u = {}
    for a in arms:
        u.setdefault((shape_of(a), a["type"], a["shires"]), []).append(a)
    out = []
    for key in sorted(u, key=lambda k: (k[2], k[1], k[0])):
        out.append(sorted(u[key], key=lambda a: kind_key(a["kind"])))
    return out


def process_s(a):
    """A process's planned seconds: setup, 6 s of launches and the last pass, the host's check of C."""
    return 0.3 + 0.002 * a["footprint_mb"] * (2 if a["shires"] == FULL else 1) + 6.5 + 0.5


def est_run_s(form, a=None):
    f = FORMS[form]
    if form == "null":
        return GATE_PLAN_S + f["rest_s"] + f["window_s"] + f["tail_s"]
    return GATE_PLAN_S + f["rest_s"] + f["nproc"] * process_s(a) + f["tail_s"]


def blocks_of(sess, by_id, card, P):
    """[(name, arms, through-nulls)] in the plan's order; every arm checked against the card."""
    out, seen = [], set()
    for n, b in enumerate(sess["blocks"]):
        if isinstance(b, list):
            name, ids, nulls = f"B{n + 1}", b, None
        elif isinstance(b, dict) and set(b) <= {"name", "arms", "nulls"} and isinstance(b.get("arms"), list):
            name, ids, nulls = b.get("name") or f"B{n + 1}", b["arms"], b.get("nulls")
        else:
            raise ValueError(f"{card} {sess['S']}: block {n + 1} is a list of arm ids or {{name, arms, nulls}}")
        if not isinstance(name, str) or not FAMILY_RE.match(name) or name in [x[0] for x in out]:
            raise ValueError(f"{card} {sess['S']}: block name {name!r} (a tag, once a session)")
        if nulls not in (None, "through", "none"):
            raise ValueError(f"{card} {sess['S']}: block {name}: nulls {nulls!r} (through or none)")
        if not ids:
            raise ValueError(f"{card} {sess['S']}: block {name} is empty")
        grp = []
        for i in ids:
            if i not in by_id:
                raise ValueError(f"{card} {sess['S']}: block {name}: no arm {i!r} in the plan")
            if i in seen:
                raise ValueError(f"{card} {sess['S']}: arm {i} twice in the session")
            seen.add(i)
            why = card_ok(P, card, by_id[i])
            if why:
                raise ValueError(f"{card} {sess['S']}: REFUSED: {why}")
            grp.append(by_id[i])
        through = (nulls == "through") or (nulls is None and any(a["small"] for a in grp))
        out.append((name, grp, through))
    if not out:
        raise ValueError(f"{card} {sess['S']}: no block")
    return out


def schedule(P, card, sess, by_id, anchor):
    """One session's schedule, in the first sweep's form (every field it carries) and by its laws."""
    session = sess["S"]
    SEED = P.seed
    rng = random.Random(f"{SEED}-{card}-{session}")
    runs = []
    n_null = [0]

    def push(a, block, role, unit=None):
        if role == "null":
            runs.append({"i": len(runs) + 1, "block": block, "role": "null", "arm": f"null-{n_null[0] + 1}", "test": "null",
                         "form": "null", "unit": None, "est_peak_w": CARDS[card]["rest_w"], "est_s": round(est_run_s("null"), 1)})
            n_null[0] += 1
            return
        form = "burst" if role == "anchor" else form_of(a)
        runs.append({"i": len(runs) + 1, "block": block, "role": role, "arm": a["id"], "test": "fma", "type": a["type"],
                     "values": a["values"], "shires": a["shires"], "form": form, "unit": unit,
                     "est_peak_w": est_of(P, card, a),
                     "est_s": round(est_run_s(form, a), 1)})

    blks = blocks_of(sess, by_id, card, P)
    if sess.get("reverse"):
        blks = blks[::-1]
    allowed = [a for _, g, _ in blks for a in g]
    hottest = max(allowed, key=lambda a: (est_of(P, card, a), a["id"]))["id"]
    push(anchor, blks[0][0], "anchor")
    if not blks[0][2]:                                 # (a block with nulls through it opens with its own null)
        push(None, blks[0][0], "null")                 # a null at the session's start (cool, after the opening rest)
    for name, grp, through in blks:
        units = units_of(grp)
        rng.shuffle(units)
        if through:
            # null runs through the block: one before every two small-signal units
            small = [u for u in units if u[0]["small"]]
            other = [u for u in units if not u[0]["small"]]
            units = []
            for j, u in enumerate(small):
                if j % 2 == 0:
                    units.append("null")
                units.append(u)
            units += other
            units.append("null")
        for u in units:
            if u == "null":
                push(None, name, "null")
                continue
            uid = f"{name}:{unit_name(u[0])}"
            order = list(u)
            random.Random(f"{SEED}-{card}-{uid.split(':')[1]}").shuffle(order)    # the unit's own order, the same in every session
            if sess.get("reverse"):
                order = order[::-1]                    # a reverse session mirrors it
            for a in order:
                push(a, name, role_of(P, card, a), uid)
                if a["id"] == hottest:
                    push(None, name, "null")           # a null right after the session's hottest arm (its cooling)
        push(anchor, name, "anchor")
    # fewer than MIN_NULLS null runs (a session with no block of small-signal units): one more null before the anchor that
    # closes each block, from the last block back, until there are MIN_NULLS; then the runs and the nulls are numbered in order
    n_have = sum(1 for r in runs if r["role"] == "null")
    names = [b[0] for b in blks]
    j = 0
    while n_have < MIN_NULLS:
        b = names[::-1][j % len(names)]
        at = max(i for i, r in enumerate(runs) if r["role"] == "anchor" and r["block"] == b)
        runs.insert(at, {"i": 0, "block": b, "role": "null", "arm": "null-0", "test": "null", "form": "null", "unit": None,
                         "est_peak_w": CARDS[card]["rest_w"], "est_s": round(est_run_s("null"), 1)})
        n_have += 1
        j += 1
    k = 0
    for i, r in enumerate(runs):
        r["i"] = i + 1
        if r["role"] == "null":
            k += 1
            r["arm"] = f"null-{k}"
    smoke = []
    for (mb, nb, kb, t, kind, mask) in SMOKE:
        a = smoke_rec(mb, nb, kb, t, kind, mask)
        smoke.append({"arm": a["id"], "type": t, "values": a["values"], "shires": mask,
                      "est_peak_w": est_peak_w(card, mb, nb, kb, t, kind, mask)})
    planned = (sum(r["est_s"] for r in runs) + OPEN_PLAN_S) / 60.0
    rule = 5.0 * math.ceil((planned + 5.0) / 5.0)
    if rule > RULE_MAX_MIN or rule + 7.0 > CAP_MAX_MIN:
        raise ValueError(f"{card} {session}: REFUSED: planned {planned:.1f} card-minutes, rule {rule:g}, cap {rule + 7:g}: over this "
                         f"sweep's session size (rule {RULE_MAX_MIN:g}, cap {CAP_MAX_MIN:g}); split it")
    return {"kit": KIT, "card": card, "session": session, "seed": f"{SEED}-{card}-{session}",
            "process": {"seconds": 6, "budget": 7.5, "timeout_s": 10, "smoke_seconds": 2, "smoke_budget": 3.5},
            "forms": FORMS,
            "timing": {"open_rest_s": 60.0, "gate_wait_s": 180.0, "rule_min": rule, "cap_min": rule + 7.0},
            "line_w": CARDS[card]["line_w"], "cap_est_w": CAP_EST_W if card == "a2c0" else None, "smoke": smoke, "runs": runs,
            "planned_min": round(planned, 1)}


def make(plan, root, priors=None):
    """{rel path under src/: object (json) or bytes (a tile)} for the whole plan; ValueError on anything refused (priors: the
    wider check's prior files, TG.plan_priors(), or None)."""
    for a in plan.get("arms") or []:     # a block arm on a plan tile: refused before the tiles are made (their K are gemmL's)
        if isinstance(a, dict) and "arm" in a and a.get("kind") not in KINDS:
            raise ValueError(f"arm {a.get('id')}: kind {a.get('kind')!r}: a block arm runs the lab's kinds only (rnd, zeros, ones)")
    P = Plan(plan, root, priors)
    extra = set(plan) - {"kit", "seed", "tiles", "arms", "sessions", "note", "priors"}
    if extra:
        raise ValueError(f"the plan has unknown fields {sorted(extra)}")
    arms = [arm_rec(P, a) for a in plan.get("arms") or []]
    ids = [a["id"] for a in arms]
    if len(set(ids)) != len(ids):
        raise ValueError(f"arm ids repeat: {sorted({i for i in ids if ids.count(i) > 1})}")
    anchor = anchor_rec()
    by_id = {a["id"]: a for a in arms}
    all_arms = sorted(arms + [anchor], key=lambda a: a["id"])
    sessions = plan.get("sessions") or {}
    bad_cards = [c for c in sessions if c not in CARDS]
    if bad_cards:
        raise ValueError(f"cards {bad_cards}: this kit runs {sorted(CARDS)}")
    files, names = {}, {}
    for card in sorted(sessions):
        lst = sessions[card]
        ss = [s.get("S") for s in lst]
        if any(not isinstance(s, str) or not SESSION_RE.match(s) for s in ss) or len(set(ss)) != len(ss):
            raise ValueError(f"{card}: sessions {ss}: each S1 to S9, once")
        for s in lst:
            if set(s) - {"S", "blocks", "reverse", "note"}:
                raise ValueError(f"{card} {s['S']}: unknown fields {sorted(set(s) - {'S', 'blocks', 'reverse', 'note'})}")
            files[f"sched/{card}-{s['S']}.json"] = schedule(P, card, s, by_id, anchor)
        names[card] = sorted(ss, key=lambda x: int(x[1:]))
    tiles = {name: {k: v for k, v in x["rec"].items() if k in ("name", "type", "gen", "file", "sha256", "est_as", "toggle", "stats",
                                                              "checks")} for name, x in sorted(P.tiles.items())}
    files["arms.json"] = {"kit": KIT, "seed": P.seed, "arms": all_arms, "tiles": tiles, "sessions": names}
    for name, x in P.tiles.items():
        files[x["rec"]["file"][len("src/"):]] = x["data"]
    return files


def dump(obj):
    return json.dumps(obj, indent=1, sort_keys=True) + "\n"


def as_bytes(obj):
    return obj if isinstance(obj, bytes) else dump(obj).encode()


def made_here(src):
    """What the generator has written under src/: arms.json, sched/*.json, and the plan tiles (any .bin under src/tiles that is
    not one of the lab's nine)."""
    out = []
    if os.path.isfile(os.path.join(src, "arms.json")):
        out.append("arms.json")
    d = os.path.join(src, "sched")
    if os.path.isdir(d):
        out += [f"sched/{n}" for n in sorted(os.listdir(d))]
    lab = {r[len("src/"):] for r in TG.lab_files()}
    for t in TYPES:
        d = os.path.join(src, "tiles", t)
        for n in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            rel = f"tiles/{t}/{n}"
            if rel not in lab:
                out.append(rel)
    return out


def main(argv):
    root = os.path.normpath(os.path.join(HERE, ".."))
    plan_p = os.path.join(root, "plan.json")
    out_root = root
    if "--plan" in argv:
        plan_p = argv[argv.index("--plan") + 1]
    if "--out" in argv:
        out_root = os.path.abspath(argv[argv.index("--out") + 1])
    src = os.path.join(out_root, "src")
    if not os.path.exists(plan_p):
        have = made_here(src)
        if "--check" in argv:
            ok = not have
            print("MAKE CHECK " + ("PASS (no plan.json beside src/: nothing to make, nothing made)" if ok else
                                   f"FAIL: no plan.json beside src/, but src/ holds what a plan made: {have}"))
            return 0 if ok else 1
        print(f"no plan at {plan_p}: nothing written")
        return 2
    with open(plan_p) as f:
        plan = json.load(f)
    try:
        priors = TG.plan_priors(plan, plan_p, argv[argv.index("--priors") + 1] if "--priors" in argv else None)
        files = make(plan, root, priors)
    except (OSError, ValueError) as e:
        print(f"MAKE REFUSED: {e}")
        return 3
    if "--check" in argv:
        bad = []
        for rel, obj in files.items():
            p = os.path.join(src, rel)
            if not os.path.isfile(p) or open(p, "rb").read() != as_bytes(obj):
                bad.append(rel)
        bad += [f"{r} (not made by this generator from this plan)" for r in made_here(src) if r not in files]
        print("MAKE CHECK " + ("PASS" if not bad else "FAIL: " + ", ".join(bad)))
        return 0 if not bad else 1
    for r in made_here(src):
        if r not in files:
            p = os.path.join(src, r)
            if os.path.isfile(p) and not os.path.islink(p):
                os.remove(p)
                print(f"removed {r} (the plan no longer makes it)")
    for rel, obj in files.items():
        p = os.path.join(src, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(as_bytes(obj))
    arms = files["arms.json"]["arms"]
    print(f"arms {len(arms)} (with the anchor); tiles {len(files['arms.json']['tiles'])}")
    deep = [a["id"] for a in arms if "arm" not in a and a["K"] > FIRST_SWEEP_K[a["type"]]]
    blk = [a for a in arms if "arm" in a]
    if blk:
        fam = {}
        for a in blk:
            fam[a["family"]] = fam.get(a["family"], 0) + 1
        print(f"block, stream and TenB arms {len(blk)} ({', '.join(f'{k} {v}' for k, v in sorted(fam.items()))}): ops a minion a "
              f"pass {min(a['ops_per_minion_pass'] for a in blk)}-{max(a['ops_per_minion_pass'] for a in blk)}, footprint "
              f"{min(a['footprint_mb'] for a in blk):g}-{max(a['footprint_mb'] for a in blk):g} MB")
    if deep:
        print(f"note: {len(deep)} arm(s) past the first sweep's largest K (fp32 16,384, fp16 8,192, int8 32,768): a process's "
              f"time inside `timeout 10` (the host's check of C over the whole K) is unmeasured there: {', '.join(deep)}")
    for name, x in files["arms.json"]["tiles"].items():
        print(f"tile {name} ({x['type']}, gen {x['gen']}): sha256 {x['sha256'][:16]}; toggle {x['toggle']}; checks "
              + ", ".join(f"K {k} {v.get('result')}" for k, v in x["checks"].items()))
    sw = {x["name"]: x.get("switches") for x in plan.get("tiles") or []}
    print("\n".join(TG.pair_report(TG.pair_check(
        [{"name": n, "type": x["type"], "data": files[x["file"][len("src/"):]], "switches": sw.get(n),
          "kind": x["gen"] if x["gen"] in TG.DRAWN else None} for n, x in files["arms.json"]["tiles"].items()],
        TG.wider_others(priors, root) if priors is not None else ()))[-(3 if priors is not None else 2):]))
    if priors is None:
        print("the wider check (the lab's kinds and the tile files run before): not run, no priors named (--priors LIST)")
    for card, ss in files["arms.json"]["sessions"].items():
        for s in ss:
            sc = files[f"sched/{card}-{s}.json"]
            cnt = {}
            for r in sc["runs"]:
                cnt[r["role"]] = cnt.get(r["role"], 0) + 1
            blk = []
            for r in sc["runs"]:
                if r["block"] not in blk:
                    blk.append(r["block"])
            print(f"{card} {s}: {len(sc['runs'])} runs {cnt} in {len(blk)} blocks {blk}; planned {sc['planned_min']} card-min "
                  f"(rule {sc['timing']['rule_min']:g}, cap {sc['timing']['cap_min']:g}); highest estimate "
                  f"{max(r['est_peak_w'] for r in sc['runs'])} W (line {sc['line_w']} W); sha256 "
                  f"{hashlib.sha256(dump(sc).encode()).hexdigest()[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
