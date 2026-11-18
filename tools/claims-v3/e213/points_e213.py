#!/usr/bin/env python3
"""E213 (Q216): the registered points and order of MM1-v3's BLIND MATMUL DAY, two arms. Written before any E213 datum. Standard library only.

    python3 -I -B tools/claims-v3/e213/points_e213.py candidates   writes desk/candidates-e213.json (every candidate point of both arms)
    python3 -I -B tools/claims-v3/e213/points_e213.py              reads desk/neverrun-e213.json, writes points-e213.json and points-e213.csv
    python3 -I -B tools/claims-v3/e213/points_e213.py --check      rebuilds all three and compares them with the committed files (exit 0 = PASS)

ARM A (aifoundry3 card 0 at its pinned 600 MHz): MM1-v3's frozen arm-A list, read from tools/matmul/mm1/v3/out/e213_points.csv (sha256 pinned
below and checked first; exit 4 if it differs) and never re-chosen here: its 90 rows on aifoundry3 card 0, ids a001-a090, six families (I the
int8 L3 factor, R the two-edge retention, C one K block, M the subset layout, P the kernels' operations, E deep K and the anchor). Its three rows
MM1-v3 marks as run before (a088 gemmL1x1x1 int8, the twin of a087; a089 and a090, the anchor gemmL4x8x8 int8 at two die gates) are REFERENCES:
run, never in a blind rule. A point the never-run scan finds run anywhere since MM1-v3's scan is DROPPED here (desk/neverrun-e213.json).
ARM B (aifoundry1 card 1 at 600 MHz; MOVED off aifoundry2 by Q216's brief: aifoundry2's host went down at about 15:45 PST Tue 17 Nov 2026):
chosen by this registration, 40 points never run on card 1 and one reference, in six families that test MM1-v3's new terms - BI the int8 L3
factor (int8 / fp32 pairs inside the L3 and past its first edge; the KB = 2 pairs also read the shire-cache share r2), BR the two-edge retention
past the L3 (44-104 MB), BK one and two K blocks with MB x NB >= 2 (r2 and the C store), BE deep K in zeros and random (the switch route's data
term past the L3), BS the switch route's energy at one shape (zeros, ones, sparse50 beside BI's random), BP the census path (rgm136's own
non-cooperative gemmLnc branch, run by rgm211's host, beside each one's gemmL twin), and k41 gemmL1x1x1 int8 random, the reference twin of k40.
A CASE (time is kind-blind in both models) is a distinct (kernel loop, arm, format, shire mask); energy is scored per point.
THE MASK is written as the host prints it ("0x%llx": MM1-v3's 0x01010101 is 0x1010101); MM1-v3's spelling kept as mm1_mask.
THE TIES: arm A E206's p001 (gemmL2x4x4 fp32 random, the full chip; E206 arm A ran it five times and E207 three on this card), arm B E208's
anchor arm (gemmL4x8x8 int8 random, the full chip; 23 runs in E208's three card-1 sessions and 28 in E212's four). Never scored as points.
THE SMOKE: arm A E211's three (gemmL2x2x2 on rgm136, gemmLn2x2x2 on rgm211, gemmLnc2x2x2 on rgm211's host with rgm136's ELF; fp32 random; they
ran on this card in E211) and, by Amendment A1 (E213.md, before any datum), s04: gemmL2x2x2 fp32 random on rgm211's host and ELF, the family
'rgm211 gemmL''s own smoke (that loop never ran on a card) with its own stop path; arm B E206 arm B's three (p001, p046, p021: they ran on card 1)
and gemmLnc2x2x2 fp32 random (rgm211's host).
THE ORDER, per arm: a tie run, pass 1 (tiers, each in the order of Python's random.Random("E213|<arm>|pass1") shuffle of its sorted ids; the
kernels' tier in shape blocks), a tie run, pass 2, a tie run. Arm A: tier 1 rgm136's full-chip random and deep-K points (families I, R, C, E),
tier 2 the subsets (M), tier 3 the kernels (P: per shape, rgm136 gemmL, rgm211 gemmLn, rgm211 gemmL, rgm136 gemmLnc; then a088, a087), tier 4
the anchor references; pass 2 = 12 points drawn by random.Random("E213|A|pass2").sample of the sorted scored ids, in reverse pass-1 order.
Arm B: tier 1 rgm136's full-chip random points, tier 2 the kinds (zeros, ones, sparse50), tier 3 the census block (k41, k40, k37, k38, k39);
pass 2 = pass 1 reversed (every point twice: a linear drift cancels).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V3_POINTS = "tools/matmul/mm1/v3/out/e213_points.csv"
V3_POINTS_SHA256 = "be9049299641ccaf764225c9b390997cc53a2885d9bf350ae12212d14503ee21"
E206_POINTS = "tools/claims-v3/e206/points-e206.json"
E206_POINTS_SHA256 = "121cada61673aabd7f2deaadbb37cb1164c772737cbe1085c6c9f3ff3ac77a1e"
TILES = "tools/claims-v3/kinds/tiles"
MiB = 2 ** 20
KBLK = {"fp32": 512, "fp16": 1024, "int8": 2048}
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MT, NT, KT = 64, 32, 32
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024
FULL = 0xFFFFFFFF
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
CAND = os.path.join(HERE, "desk", "candidates-e213.json")
NEVER = os.path.join(HERE, "desk", "neverrun-e213.json")

# ARM B: (id, family, arm, format, kind, kernel, role, why)
ARM_B = [
    ("k01", "BI", "gemmL2x1x2", "int8", "random", "rgm136", "point", "int8 inside the L3 (14 MB); KB = 2, MB x NB = 2 (r2)"),
    ("k02", "BI", "gemmL2x1x2", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k03", "BI", "gemmL4x1x2", "int8", "random", "rgm136", "point", "int8 inside the L3 (26 MB); KB = 2, MB x NB = 4 (r2)"),
    ("k04", "BI", "gemmL4x1x2", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k05", "BI", "gemmL3x1x3", "int8", "random", "rgm136", "point", "int8 inside the L3 (27 MB)"),
    ("k06", "BI", "gemmL3x1x3", "fp32", "random", "rgm136", "point", "its fp32 pair; k37's gemmL twin; BS's random"),
    ("k07", "BI", "gemmL1x2x7", "int8", "random", "rgm136", "point", "int8 at the L3's size (32 MB)"),
    ("k08", "BI", "gemmL1x2x7", "fp32", "random", "rgm136", "point", "its fp32 pair; k38's gemmL twin"),
    ("k09", "BI", "gemmL1x2x11", "int8", "random", "rgm136", "point", "int8 past the first edge (48 MB)"),
    ("k10", "BI", "gemmL1x2x11", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k11", "BR", "gemmL2x1x8", "fp32", "random", "rgm136", "point", "the retention ladder: 44 MB"),
    ("k12", "BR", "gemmL3x1x7", "fp32", "random", "rgm136", "point", "55 MB"),
    ("k13", "BR", "gemmL1x1x18", "fp32", "random", "rgm136", "point", "56 MB (the K ladder at 1x1)"),
    ("k14", "BR", "gemmL4x1x6", "fp32", "random", "rgm136", "point", "62 MB; k39's gemmL twin"),
    ("k15", "BR", "gemmL3x1x9", "fp32", "random", "rgm136", "point", "69 MB, the plateau's end (x2 72.3 MB)"),
    ("k16", "BR", "gemmL3x1x9", "int8", "random", "rgm136", "point", "int8 on the plateau (d8 past the L3)"),
    ("k17", "BR", "gemmL1x1x26", "fp32", "random", "rgm136", "point", "80 MB, past the plateau"),
    ("k18", "BR", "gemmL1x1x26", "int8", "random", "rgm136", "point", "int8 past the plateau"),
    ("k19", "BR", "gemmL1x1x34", "fp32", "random", "rgm136", "point", "104 MB"),
    ("k20", "BK", "gemmL2x3x1", "int8", "random", "rgm136", "point", "one K block, MB x NB = 6 (r2; C 6 MiB)"),
    ("k21", "BK", "gemmL2x3x1", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k22", "BK", "gemmL4x4x1", "int8", "random", "rgm136", "point", "one K block, MB x NB = 16 (C 32 MiB)"),
    ("k23", "BK", "gemmL4x4x1", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k24", "BK", "gemmL7x3x1", "int8", "random", "rgm136", "point", "one K block, MB x NB = 21 (C 42 MiB; arm A's a041 on aifoundry3)"),
    ("k25", "BK", "gemmL7x3x1", "fp32", "random", "rgm136", "point", "its fp32 pair (arm A's a042)"),
    ("k26", "BK", "gemmL4x3x2", "int8", "random", "rgm136", "point", "two K blocks, MB x NB = 12 (r2)"),
    ("k27", "BK", "gemmL4x3x2", "fp32", "random", "rgm136", "point", "its fp32 pair"),
    ("k28", "BE", "gemmL1x3x40", "fp32", "zeros", "rgm136", "point", "deep K (206 MB), zeros (arm A's a031)"),
    ("k29", "BE", "gemmL1x3x40", "fp32", "random", "rgm136", "point", "deep K, random (arm A's a032)"),
    ("k30", "BE", "gemmL2x2x44", "fp32", "zeros", "rgm136", "point", "deep K (272 MB), zeros (arm A's a033)"),
    ("k31", "BE", "gemmL2x2x44", "fp32", "random", "rgm136", "point", "deep K, random (arm A's a034)"),
    ("k32", "BS", "gemmL3x1x3", "fp32", "zeros", "rgm136", "point", "the switch route at one shape: zeros (k06 its random)"),
    ("k33", "BS", "gemmL3x1x3", "fp32", "ones", "rgm136", "point", "the constant one"),
    ("k34", "BS", "gemmL3x1x3", "fp32", "sparse50", "rgm136", "point", "half zeros (MM1-v2 prices no sparse50: its energy NOT FORECAST)"),
    ("k35", "BS", "gemmL3x1x3", "int8", "zeros", "rgm136", "point", "int8 zeros (k05 its random)"),
    ("k36", "BS", "gemmL3x1x3", "int8", "ones", "rgm136", "point", "int8 ones"),
    ("k37", "BP", "gemmLnc3x1x3", "fp32", "random", "rgm136", "point", "the census path: gemmLnc beside k06"),
    ("k38", "BP", "gemmLnc1x2x7", "fp32", "random", "rgm136", "point", "gemmLnc beside k08"),
    ("k39", "BP", "gemmLnc4x1x6", "fp32", "random", "rgm136", "point", "gemmLnc beside k14"),
    ("k40", "BP", "gemmLnc1x1x1", "int8", "random", "rgm136", "point", "gemmLnc at the L2 (k41 its twin)"),
    ("k41", "BP", "gemmL1x1x1", "int8", "random", "rgm136", "reference", "k40's twin; gemmL1x1x1 int8 ran on card 1 before (a reference)"),
]


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def mask_geometry(mask):
    sh = [s for s in range(32) if mask >> s & 1]
    rg = sorted({s >> 2 for s in sh})
    cg = sorted({s & 3 for s in sh})
    if len(rg) * len(cg) != len(sh):
        raise SystemExit(f"points_e213: mask 0x{mask:x} is not a product of row groups and column groups")
    return {"shires": len(sh), "row_groups": rg, "column_groups": cg, "rows": 128 * len(rg), "cols": 128 * len(cg)}


def parse_arm(arm):
    for pre in ("gemmLnc", "gemmLn", "gemmL"):
        if arm.startswith(pre):
            return pre, tuple(int(x) for x in arm[len(pre):].split("x"))
    raise SystemExit(f"points_e213: unknown arm {arm}")


def loop_of(pre, kernel):
    """the kernel's loop (MM1-v3's census names, engine_v3.loop_of) and the host and ELF that run it (E211's arm families)"""
    if pre == "gemmLn":
        return "rgm211 gemmLn", "rgm211", "rgm211"
    if pre == "gemmLnc":
        return "rgm136 gemmLnc", "rgm211", "rgm136"
    if kernel == "rgm211":
        return "rgm211 gemmL", "rgm211", "rgm211"
    return "rgm136 gemmL", "rgm136", "rgm136"


def values_of(arm, fmt, kind):
    if kind == "random":
        return f"{arm}:randn:{TILES}/{fmt}/{'full.bin' if fmt == 'int8' else 'randn.bin'}"
    if kind in ("zeros", "ones"):
        return f"{arm}:tiles:{TILES}/{fmt}/{kind}.bin"
    if kind == "sparse50":
        return f"{arm}:sparse50:{TILES}/{fmt}/sparse50.bin"
    raise SystemExit(f"points_e213: no tile for kind {kind}")


def describe(pid, arm_tag, family, arm, fmt, kind, mm1_mask, kernel, role, why, t0_c=None, card=A3):
    pre, (MB, NB, KB) = parse_arm(arm)
    mask = int(mm1_mask, 16)
    g = mask_geometry(mask)
    M, N, K = 1024 * MB, 512 * NB, KBLK[fmt] * KB
    ops = MB * NB * 2 * KB * 32
    Ab, Bb, Cb = MB * KB * ABLK, KB * NB * BBLK, MB * NB * CBLK
    Meff, Neff = g["rows"] * MB, g["cols"] * NB
    macs = Meff * Neff * K
    if mask == FULL and macs != 1024 * ops * MACS_PER_OP[fmt]:
        raise SystemExit(f"points_e213: {pid} MAC count does not close")
    loop, host, elf = loop_of(pre, kernel)
    smask = f"0x{mask:x}"
    v = values_of(arm, fmt, kind)
    tile = v.split(":", 2)[2]
    p = {"id": pid, "arm_tag": arm_tag, "card": card, "f_mhz": 600.0, "family": family, "role": role, "arm": arm, "loop": loop,
         "kernel": kernel, "host": host, "elf": elf, "shape": [MB, NB, KB], "format": fmt, "kind": kind, "shire_mask": smask, "mm1_mask": mm1_mask,
         "shires": g["shires"], "minions": 32 * g["shires"], "row_groups": g["row_groups"], "column_groups": g["column_groups"],
         "M": M, "N": N, "K": K, "M_computed": Meff, "N_computed": Neff,
         "gemm_computed": f"{Meff:,} x {Neff:,} x {K:,}" + ("" if mask == FULL else f" (rows {g['rows']} and columns {g['cols']} of each 1,024 x 512 C block)"),
         "ops_per_minion_per_gemm": ops, "macs_per_gemm": macs, "bytes_MB": {"A": Ab / MiB, "B": Bb / MiB, "C": Cb / MiB, "all": (Ab + Bb + Cb) / MiB},
         "case": f"{loop}|{arm}|{fmt}|{smask}", "values": v, "tile_sha256": sha_rel(tile),
         "host_args": ["--test", "fma", "--type", fmt, "--pattern", "none", "--values", v, "--shires", smask, "--per-shire", "32",
                       "--seconds", "6", "--budget", "7.5", "--seed", "1"],
         "t0_c_forecast": t0_c, "why": why}
    p["name"] = f"{arm}.{fmt}.{kind}" + ("" if loop.startswith("rgm136") else f".{kernel}") + ("" if mask == FULL else f".m{smask}")
    return p


def arm_a_rows():
    if sha_rel(V3_POINTS) != V3_POINTS_SHA256:
        print(f"points_e213: REFUSED, {V3_POINTS} is not MM1-v3's frozen file (sha256 {sha_rel(V3_POINTS)})")
        sys.exit(4)
    rows = [r for r in csv.DictReader(open(os.path.join(REPO, V3_POINTS), newline="")) if r["card"] == A3]
    if len(rows) != 90:
        raise SystemExit("points_e213: want MM1-v3's 90 arm-A rows")
    out = []
    for r in rows:
        role = "point" if r["never_run_on_card"] == "True" else "reference"
        t0 = float(r["t0_c"]) if r["t0_c"] else None
        out.append(describe(r["id"], "A", r["family"], r["arm"], r["fmt"], r["kind"], r["mask"], r["kernel"], role, r["note"], t0_c=t0))
    return out


def arm_b_rows():
    return [describe(r[0], "B", r[1], r[2], r[3], r[4], "0xffffffff", r[5], r[6], r[7], card=C1) for r in ARM_B]


def candidates():
    A, B = arm_a_rows(), arm_b_rows()
    return {"experiment": "E213", "what": "every candidate point of both arms, for the never-run scan (desk/neverrun_e213.py report)",
            "arms": {"A": [{"id": p["id"], "arm": p["arm"], "kernel": p["kernel"], "role": p["role"]} for p in A],
                     "B": [{"id": p["id"], "arm": p["arm"], "kernel": p["kernel"], "role": p["role"]} for p in B]}}


def smoke_tie(e206):
    by = {p["id"]: p for p in e206["points"]}
    sA = [describe("s01", "A", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm136", "smoke", "E211's s01: rgm136's host"),
          describe("s02", "A", "smoke", "gemmLn2x2x2", "fp32", "random", "0xffffffff", "rgm211", "smoke", "E211's s02: rgm211's host and ELF"),
          describe("s03", "A", "smoke", "gemmLnc2x2x2", "fp32", "random", "0xffffffff", "rgm136", "smoke", "E211's s03: rgm211's host, rgm136's ELF"),
          describe("s04", "A", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm211", "smoke",
                   "Amendment A1: the family 'rgm211 gemmL' (rgm211's own gemmL loop, never run on a card), rgm211's host and ELF; its own stop path")]
    sB = []
    for i, pid in enumerate(("p001", "p046", "p021"), 1):
        q = by[pid]
        sB.append(describe(f"s1{i}", "B", "smoke", q["arm"], q["format"], q["kind"], q["shire_mask"], "rgm136", "smoke",
                           f"E206's {pid} (E206 arm B's smoke; it ran on card 1)", card=C1))
    sB.append(describe("s14", "B", "smoke", "gemmLnc2x2x2", "fp32", "random", "0xffffffff", "rgm136", "smoke",
                       "E211's s03 config: rgm211's host with rgm136's ELF (first gemmLnc process on card 1)", card=C1))
    p001 = by["p001"]
    tA = describe("t01", "A", "tie", p001["arm"], p001["format"], p001["kind"], p001["shire_mask"], "rgm136", "tie",
                  "E206's p001: E206 arm A ran it five times and E207 three times on this card (the bridge)")
    tB = describe("t02", "B", "tie", "gemmL4x8x8", "int8", "random", "0xffffffff", "rgm136", "tie",
                  "E208's anchor arm 4x8x8-int8-rnd: 23 runs in E208's three card-1 sessions and 28 in E212's four (the bridge)", card=C1)
    return sA, sB, tA, tB


def order_a(pts):
    by = {p["id"]: p for p in pts}
    rnd = random.Random("E213|A|pass1")
    t1 = sorted(p["id"] for p in pts if p["family"].split(":")[1] in ("I", "R", "C", "E") and "P" not in p["family"] and p["role"] == "point")
    t2 = sorted(p["id"] for p in pts if p["family"] == "A:M")
    rnd.shuffle(t1)
    rnd.shuffle(t2)
    shapes = ["3x1x3", "1x6x5", "4x1x6", "1x1x44"]
    rnd.shuffle(shapes)
    t3 = []
    for s in shapes:
        blk = [p for p in pts if "P" in p["family"] and p["arm"].endswith(s) and p["shape"] == [int(x) for x in s.split("x")]]
        key = {"rgm136 gemmL": 0, "rgm211 gemmLn": 1, "rgm211 gemmL": 2, "rgm136 gemmLnc": 3}
        t3 += [p["id"] for p in sorted(blk, key=lambda p: key[p["loop"]])]
    t3 += ["a088", "a087"]
    t4 = ["a089", "a090"]
    p1 = t1 + t2 + t3 + t4
    if sorted(p1) != sorted(by):
        raise SystemExit(f"points_e213: arm A's pass 1 does not hold every point once ({len(p1)} of {len(by)})")
    scored = sorted(p["id"] for p in pts if p["role"] == "point")
    pick = set(random.Random("E213|A|pass2").sample(scored, 12))
    p2 = [i for i in reversed(p1) if i in pick]
    return {"seed": "E213|A|pass1", "seed_pass2": "E213|A|pass2", "tie": "t01", "tiers": {"1": t1, "2": t2, "3": t3, "4": t4},
            "pass1": p1, "pass2": p2}


def order_b(pts):
    by = {p["id"]: p for p in pts}
    rnd = random.Random("E213|B|pass1")
    t1 = sorted(p["id"] for p in pts if p["kind"] == "random" and p["loop"] == "rgm136 gemmL" and p["role"] == "point")
    t2 = sorted(p["id"] for p in pts if p["kind"] != "random")
    rnd.shuffle(t1)
    rnd.shuffle(t2)
    t3 = ["k41", "k40", "k37", "k38", "k39"]
    p1 = t1 + t2 + t3
    if sorted(p1) != sorted(by):
        raise SystemExit(f"points_e213: arm B's pass 1 does not hold every point once ({len(p1)} of {len(by)})")
    return {"seed": "E213|B|pass1", "tie": "t02", "tiers": {"1": t1, "2": t2, "3": t3}, "pass1": p1, "pass2": list(reversed(p1))}


def build():
    if sha_rel(E206_POINTS) != E206_POINTS_SHA256:
        print(f"points_e213: REFUSED, {E206_POINTS} changed")
        sys.exit(4)
    nr = json.load(open(NEVER))
    cand_sha = hashlib.sha256(open(CAND, "rb").read()).hexdigest()
    if nr.get("candidates_sha256") != cand_sha:
        raise SystemExit("points_e213: desk/neverrun-e213.json was made from another candidates list")
    A, B = arm_a_rows(), arm_b_rows()
    verdict = {(arm, r["id"]): r for arm in ("A", "B") for r in nr["arms"][arm]["points"]}
    dropped = [p["id"] for p in A if p["role"] == "point" and not verdict[("A", p["id"])]["never_run"]]
    A = [p for p in A if p["id"] not in dropped]
    bad_b = [p["id"] for p in B if p["role"] == "point" and not verdict[("B", p["id"])]["never_run"]]
    if bad_b:
        raise SystemExit(f"points_e213: arm B points found run on card 1: {bad_b} (re-choose before any freeze)")
    for p in A + B:
        v = verdict[(p["arm_tag"], p["id"])]
        p["never_run_scan"] = {"never_run": v["never_run"], "counted_hits_on_card": v["counted_hits_on_card"],
                               "other_card_hits": v["other_card_hits"]}
    e206 = json.load(open(os.path.join(REPO, E206_POINTS)))
    sA, sB, tA, tB = smoke_tie(e206)
    oA, oB = order_a(A), order_b(B)
    arms = {}
    for tag, pts, smk, tie, od, card in (("A", A, sA, tA, oA, A3), ("B", B, sB, tB, oB, C1)):
        seq = [("tie", od["tie"])] + [("pass1", i) for i in od["pass1"]] + [("tie", od["tie"])] + [("pass2", i) for i in od["pass2"]] + \
              [("tie", od["tie"])]
        names = {p["id"]: p["name"] for p in pts}
        names[tie["id"]] = tie["name"]
        od["sequence"] = [{"n": n, "block": b, "id": i, "name": names[i]} for n, (b, i) in enumerate(seq, 1)]
        od["runs"] = len(seq)
        cases = sorted({p["case"] for p in pts if p["role"] == "point"})
        fam = {}
        for p in pts:
            fam[p["family"]] = fam.get(p["family"], 0) + 1
        arms[tag] = {"card": card, "clock": "600 MHz (aifoundry3: pinned by a boot-time TDP of 0; card 1: as found since September), read, never set",
                     "n_points": sum(1 for p in pts if p["role"] == "point"), "n_references": sum(1 for p in pts if p["role"] == "reference"),
                     "n_cases": len(cases), "cases": cases, "families": fam,
                     "by_format": {t: sum(1 for p in pts if p["format"] == t and p["role"] == "point") for t in ("fp32", "int8")},
                     "by_kind": {k: sum(1 for p in pts if p["kind"] == k and p["role"] == "point") for k in sorted({p["kind"] for p in pts})},
                     "by_loop": {k: sum(1 for p in pts if p["loop"] == k and p["role"] == "point") for k in sorted({p["loop"] for p in pts})},
                     "dropped_ran_since": dropped if tag == "A" else [], "points": pts, "smoke": smk, "tie": tie, "order": od}
    return {"experiment": "E213", "request": "Q216", "what": "the registered points and order of MM1-v3's blind matmul day, two arms (frozen before any E213 datum)",
            "source_arm_A": {"path": V3_POINTS, "sha256": V3_POINTS_SHA256, "what": "MM1-v3's frozen E213 candidate list (arm A's 90 rows read)"},
            "neverrun": {"path": "tools/claims-v3/e213/desk/neverrun-e213.json", "candidates_sha256": cand_sha, "scan_sha256": nr["scan_sha256"]},
            "arms": arms}


def csv_text(out):
    s = io.StringIO()
    w = csv.writer(s, lineterminator="\n")
    w.writerow(["arm", "id", "role", "family", "case", "name", "loop", "host", "elf", "arm_token", "format", "kind", "shire_mask", "shires", "minions",
                "M", "N", "K", "gemm_computed", "ops_per_minion_per_gemm", "bytes_MB_all", "pass1_position", "pass2", "values"])
    for tag in ("A", "B"):
        a = out["arms"][tag]
        pos = {i: n for n, i in enumerate(a["order"]["pass1"], 1)}
        p2 = set(a["order"]["pass2"])
        for p in a["points"]:
            w.writerow([tag, p["id"], p["role"], p["family"], p["case"], p["name"], p["loop"], p["host"], p["elf"], p["arm"], p["format"], p["kind"],
                        p["shire_mask"], p["shires"], p["minions"], p["M"], p["N"], p["K"], p["gemm_computed"], p["ops_per_minion_per_gemm"],
                        f"{p['bytes_MB']['all']:.1f}", pos.get(p["id"], ""), p["id"] in p2, p["values"]])
    return s.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="points", choices=("points", "candidates"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.cmd == "candidates":
        c = candidates()
        if a.check:
            same = json.load(open(CAND)) == json.loads(json.dumps(c))
            print(f"points_e213 candidates --check: desk/candidates-e213.json rebuilt == committed: {same}")
            sys.exit(0 if same else 1)
        json.dump(c, open(CAND, "w"), indent=1)
        print(f"candidates: arm A {len(c['arms']['A'])}, arm B {len(c['arms']['B'])} -> {CAND}")
        return
    out = build()
    jp, cp = os.path.join(HERE, "points-e213.json"), os.path.join(HERE, "points-e213.csv")
    if a.check:
        same_c = json.load(open(CAND)) == json.loads(json.dumps(candidates()))
        same_j = json.load(open(jp)) == json.loads(json.dumps(out))
        same_v = open(cp).read() == csv_text(out)
        ok = same_c and same_j and same_v
        print(f"points_e213 --check: candidates {same_c}; points-e213.json {same_j}; points-e213.csv {same_v}; arm A {out['arms']['A']['n_points']} points "
              f"({out['arms']['A']['n_cases']} cases, {out['arms']['A']['order']['runs']} runs), arm B {out['arms']['B']['n_points']} points "
              f"({out['arms']['B']['n_cases']} cases, {out['arms']['B']['order']['runs']} runs)")
        print("PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    json.dump(out, open(jp, "w"), indent=1)
    open(cp, "w").write(csv_text(out))
    for tag in ("A", "B"):
        a = out["arms"][tag]
        print(f"arm {tag} ({a['card']}): {a['n_points']} points + {a['n_references']} references, {a['n_cases']} cases, {a['order']['runs']} runs; "
              f"families {a['families']}; loops {a['by_loop']}; kinds {a['by_kind']}; dropped (ran since) {a['dropped_ran_since']}")
        print(f"  pass 1: {' '.join(a['order']['pass1'])}")
        print(f"  pass 2: {' '.join(a['order']['pass2'])}")


if __name__ == "__main__":
    main()
