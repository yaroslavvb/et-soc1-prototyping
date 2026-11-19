#!/usr/bin/env python3
"""E215 (Q224): the registered points and order of MM1-v3.1's BLIND MATMUL DAY, two arms. Written before any E215 datum. Standard library only.

    python3 -I -B tools/claims-v3/e215/points_e215.py candidates   writes desk/candidates-e215.json (every candidate point of both arms)
    python3 -I -B tools/claims-v3/e215/points_e215.py              reads desk/neverrun-e215.json, writes points-e215.json and points-e215.csv
    python3 -I -B tools/claims-v3/e215/points_e215.py --check      rebuilds all three and compares them with the committed files (exit 0 = PASS)

ARM A (aifoundry3 card 0 at its pinned 600 MHz): MM1-v3.1's frozen list, read from tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv (sha256 pinned
below and checked first; exit 4 if it differs) and never re-chosen here: its 60 rows in its own order, ids a001-a060 - families P 12, C 10, R 10
(DECLARED-v31.md item 10's literal rule) and L 20, S 8 (chosen beside them by MM1-v3.1's post hoc readings; ADOPTED by E215.md's dated
departure D1, the orchestrator's ruling, labelled 'points chosen post hoc after the fit; forecasts frozen before any E215 datum' and reported apart
from P, C and R in every verdict). A point this registration's never-run scan finds run (desk/neverrun-e215.json) is DROPPED and said.
ARM B (aifoundry1 card 1 at 600 MHz, ET_DEVICES=1): the points desk/choose_e215b.py chose by item 10's rule applied to card 1 (desk/choice-e215b.json,
sha256 pinned in points-e215.json), ids b001-... in its order (L, P, C, R, S).
REFERENCES (run and read, never in a rule): family S's random partners at gemmL3x1x3, one a format an arm (arm A r01 fp32, r02 int8; arm B r11, r12
where its S has that format): item 10's 'each beside random in A B B A blocks'. THE TIES (E213's): arm A t01 = E206's p001 (gemmL2x4x4 fp32
random, the full chip), arm B t02 = gemmL4x8x8 int8 random, the full chip (E208's anchor arm; E212's and E213 arm B's ties on card 1).
A CASE (time is kind-blind in all four models) is a distinct (kernel loop, arm token, format, shire mask); time is scored on the cases of families
P, C, R and L, energy on the points; family S's points share their case with their random partner, a reference (its configuration ran on the
arm's card), so S is scored in energy only.
THE SMOKE (one checked 2 s process each, never a point): arm A E213's s01 (rgm136 gemmL), s02 (rgm211 gemmLn), s04 (rgm211 gemmL) at the
opening and s03 (gemmLnc, rgm211's host with rgm136's ELF) right before its gemmLnc block; arm B E213's s11-s13 (E206's p001, p046, p021) at the
opening, s15 (rgm211 gemmLn) and s16 (rgm211 gemmL) at the opening where arm B has that family (rgm211's ELF never ran on card 1), and s14
(gemmLnc) right before its gemmLnc block. Every smoke but s01 and s11-s13 has its family's own stop path (E213's Amendment A1 form).
THE ORDER (E213's, with its lesson: every gemmLnc point LAST in its arm, E213 arm B's Amendment A3 form), per arm: a tie run; pass 1 = tier 1
(the registered families' points, P, C and R, but gemmLnc, in Python's random.Random("E215|<arm>|pass1") shuffle of their sorted ids), tier 2
(family L, the same generator's next shuffle), tier 3 (family S, its kinds' A B B A blocks in the generator's next shuffle: kind, random,
random, kind); a tie run; pass 2 = arm A: tier 1 reversed; arm B: tiers 1 and 2 reversed (every point but S twice; a linear drift cancels);
a tie run; then the gemmLnc block: its smoke, its points in the generator's next shuffle, then reversed.
THE MASK is written as the host prints it ("0x%llx"); MM1's spelling kept as mm1_mask.
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
V31_POINTS = "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv"
V31_POINTS_SHA256 = "f8fe39b4fb847791352d5ccbcc92406f32cf28347fb3af1bca96b851bc8bc2cc"
E206_POINTS = "tools/claims-v3/e206/points-e206.json"
E206_POINTS_SHA256 = "121cada61673aabd7f2deaadbb37cb1164c772737cbe1085c6c9f3ff3ac77a1e"
CHOICE_B = os.path.join(HERE, "desk", "choice-e215b.json")
TILES = "tools/claims-v3/kinds/tiles"
E212_TILES = "tools/claims-v3/e212/proposal/src/tiles"
MiB = 2 ** 20
KBLK = {"fp32": 512, "fp16": 1024, "int8": 2048}
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MT, NT, KT = 64, 32, 32
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024
FULL = 0xFFFFFFFF
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
CAND = os.path.join(HERE, "desk", "candidates-e215.json")
NEVER = os.path.join(HERE, "desk", "neverrun-e215.json")
POSTHOC_LABEL = "points chosen post hoc after the fit; forecasts frozen before any E215 datum"


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def mask_geometry(mask):
    sh = [s for s in range(32) if mask >> s & 1]
    rg = sorted({s >> 2 for s in sh})
    cg = sorted({s & 3 for s in sh})
    if len(rg) * len(cg) != len(sh):
        raise SystemExit(f"points_e215: mask 0x{mask:x} is not a product of row groups and column groups")
    return {"shires": len(sh), "row_groups": rg, "column_groups": cg, "rows": 128 * len(rg), "cols": 128 * len(cg)}


def parse_arm(arm):
    for pre in ("gemmLnc", "gemmLn", "gemmL"):
        if arm.startswith(pre):
            return pre, tuple(int(x) for x in arm[len(pre):].split("x"))
    raise SystemExit(f"points_e215: unknown arm {arm}")


def loop_hosts(loop):
    """the kernel loop (MM1's census names) -> (kernel, host, ELF) (E211's arm families, E213's fourth)"""
    return {"rgm136 gemmL": ("rgm136", "rgm136", "rgm136"), "rgm211 gemmLn": ("rgm211", "rgm211", "rgm211"),
            "rgm211 gemmL": ("rgm211", "rgm211", "rgm211"), "rgm136 gemmLnc": ("rgm136", "rgm211", "rgm136")}[loop]


def tiles_of(fmt, kind):
    """the E101 grammar's generator and tile files for a kind (E213's for random, zeros, ones; the S kinds' as E207 and E212 ran them)"""
    if kind == "random":
        return "randn", [f"{TILES}/{fmt}/{'full.bin' if fmt == 'int8' else 'randn.bin'}"]
    if kind in ("zeros", "ones"):
        return "tiles", [f"{TILES}/{fmt}/{kind}.bin"]
    if kind.startswith("pattern:"):
        return "tiles", [f"{E212_TILES}/{fmt}/{kind.split(':', 1)[1]}.bin"]
    if kind == "real:blind4":
        if fmt == "fp32":
            return "tiles", ["tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_pythia_embed_qkv.bin",
                             "tools/claims-v3/kinds/blind4/tiles/fp32/fp32.real_qwen_q_down.bin"]
        if fmt == "int8":
            return "tiles", ["tools/claims-v3/kinds/blind4/tiles/int8/int8.real_pythia_embed_mlpout.bin",
                             "tools/claims-v3/kinds/blind4/tiles/int8/int8.real_qwen_q_down.bin"]
    if kind == "designed:blind3 a_colconst_b_randn" and fmt == "fp32":
        return "tiles", ["tools/claims-v3/kinds/blind3/tiles/fp32/a_colconst_b_randn.bin"]
    if kind == "e37" and fmt == "fp32":
        return "e37", [f"{TILES}/fp32/randn.bin"]
    raise SystemExit(f"points_e215: no tile for kind {kind} ({fmt})")


def describe(pid, arm_tag, family, reading, arm, fmt, kind, mm1_mask, loop, role, why, card, extra=None):
    pre, (MB, NB, KB) = parse_arm(arm)
    kernel, host, elf = loop_hosts(loop)
    if (pre == "gemmLn") != (loop == "rgm211 gemmLn") or (pre == "gemmLnc") != (loop == "rgm136 gemmLnc"):
        raise SystemExit(f"points_e215: {pid} arm {arm} does not match its loop {loop}")
    mask = int(mm1_mask, 16)
    g = mask_geometry(mask)
    M, N, K = 1024 * MB, 512 * NB, KBLK[fmt] * KB
    ops = MB * NB * 2 * KB * 32
    Ab, Bb, Cb = MB * KB * ABLK, KB * NB * BBLK, MB * NB * CBLK
    Meff, Neff = g["rows"] * MB, g["cols"] * NB
    macs = Meff * Neff * K
    if mask == FULL and macs != 1024 * ops * MACS_PER_OP[fmt]:
        raise SystemExit(f"points_e215: {pid} MAC count does not close")
    smask = f"0x{mask:x}"
    gen, files = tiles_of(fmt, kind)
    v = f"{arm}:{gen}:{','.join(files)}"
    p = {"id": pid, "arm_tag": arm_tag, "card": card, "f_mhz": 600.0, "family": family, "reading": reading, "role": role, "arm": arm,
         "loop": loop, "kernel": kernel, "host": host, "elf": elf, "shape": [MB, NB, KB], "format": fmt, "kind": kind, "shire_mask": smask,
         "mm1_mask": mm1_mask, "shires": g["shires"], "minions": 32 * g["shires"], "row_groups": g["row_groups"],
         "column_groups": g["column_groups"], "M": M, "N": N, "K": K, "M_computed": Meff, "N_computed": Neff,
         "gemm_computed": f"{Meff:,} x {Neff:,} x {K:,}" + ("" if mask == FULL else f" (rows {g['rows']} and columns {g['cols']} of each 1,024 x 512 C block)"),
         "ops_per_minion_per_gemm": ops, "macs_per_gemm": macs, "bytes_MB": {"A": Ab / MiB, "B": Bb / MiB, "C": Cb / MiB, "all": (Ab + Bb + Cb) / MiB},
         "case": f"{loop}|{arm}|{fmt}|{smask}", "time_scored": role == "point" and family != "S", "values": v,
         "tile_sha256": {f: sha_rel(f) for f in files},
         "host_args": ["--test", "fma", "--type", fmt, "--pattern", "none", "--values", v, "--shires", smask, "--per-shire", "32",
                       "--seconds", "6", "--budget", "7.5", "--seed", "1"],
         "why": why}
    if reading == "posthoc":
        p["label"] = POSTHOC_LABEL
    if extra:
        p.update(extra)
    p["name"] = f"{arm}.{fmt}.{kind}" + ("" if loop == "rgm136 gemmL" else f".{loop.replace(' ', '-')}") + ("" if mask == FULL else f".m{smask}")
    return p


def arm_a_rows():
    if sha_rel(V31_POINTS) != V31_POINTS_SHA256:
        print(f"points_e215: REFUSED, {V31_POINTS} is not MM1-v3.1's frozen file (sha256 {sha_rel(V31_POINTS)})")
        sys.exit(4)
    rows = list(csv.DictReader(open(os.path.join(REPO, V31_POINTS), newline="")))
    if len(rows) != 60:
        raise SystemExit("points_e215: want MM1-v3.1's 60 frozen rows")
    out = []
    for i, r in enumerate(rows, 1):
        why = f"MM1-v3.1's {r['family']} {r['reading']} pick, {r['how']}; |ln(v3.1 / v3)| {r['score_abs_ln_v31_over_v3']}"
        out.append(describe(f"a{i:03d}", "A", r["family"], r["reading"], r["arm"], r["fmt"], r["kind"], r["mask"], r["loop"], "point", why, A3,
                            {"source_token": r["token"]}))
    return out


def arm_b_rows():
    ch = json.load(open(CHOICE_B))
    out = []
    for i, c in enumerate(ch["chosen"], 1):
        why = f"item 10 on card 1: {c['family']} {c['reading']} pick, {c['how']}; |ln(v3.1 / v3)| {c['score']:.6f}"
        out.append(describe(f"b{i:03d}", "B", c["family"], c["reading"], c["arm"], c["fmt"], c["kind"], c["mask"], c["loop"], "point", why, C1,
                            {"source_token": c["token"]}))
    return out


def references(pts, tag, card):
    """family S's random partners at gemmL3x1x3, one a format the arm's S holds"""
    out = []
    fmts = sorted({p["format"] for p in pts if p["family"] == "S"}, key=lambda f: ("fp32", "int8").index(f))
    for j, fmt in enumerate(fmts, 1):
        rid = f"r{'0' if tag == 'A' else '1'}{j}"
        out.append(describe(rid, tag, "S-ref", "reference", "gemmL3x1x3", fmt, "random", "0xffffffff", "rgm136 gemmL", "reference",
                            f"family S's {fmt} random partner (A B B A blocks); its configuration ran on this card before (a reference, never scored)",
                            card))
    return out


def candidates():
    A, B = arm_a_rows(), arm_b_rows()
    RA, RB = references(A, "A", A3), references(B, "B", C1)

    def brief(p):
        return {k: p[k] for k in ("id", "family", "reading", "role", "arm", "kernel", "loop", "format", "kind", "mm1_mask")} | {"mask": p["mm1_mask"]}
    return {"experiment": "E215", "what": "every candidate point of both arms, for the never-run report (desk/neverrun_e215.py report)",
            "arms": {"A": [brief(p) for p in A + RA], "B": [brief(p) for p in B + RB]}}


def smoke_tie(e206, A, B):
    by = {p["id"]: p for p in e206["points"]}
    loopsA = {p["loop"] for p in A}
    loopsB = {p["loop"] for p in B}
    sA = [describe("s01", "A", "smoke", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm136 gemmL", "smoke",
                   "E213's s01: rgm136's host and ELF (the session gate)", A3)]
    if "rgm211 gemmLn" in loopsA:
        sA.append(describe("s02", "A", "smoke", "smoke", "gemmLn2x2x2", "fp32", "random", "0xffffffff", "rgm211 gemmLn", "smoke",
                           "E213's s02: rgm211's host and ELF (family 'rgm211 gemmLn': its own stop path)", A3))
    if "rgm211 gemmL" in loopsA:
        sA.append(describe("s04", "A", "smoke", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm211 gemmL", "smoke",
                           "E213's s04: rgm211's own gemmL loop (family 'rgm211 gemmL': its own stop path)", A3))
    if "rgm136 gemmLnc" in loopsA:
        sA.append(describe("s03", "A", "smoke", "smoke", "gemmLnc2x2x2", "fp32", "random", "0xffffffff", "rgm136 gemmLnc", "smoke",
                           "E213's s03: rgm211's host with rgm136's ELF (family 'rgm136 gemmLnc': its own stop path), right before the gemmLnc block",
                           A3))
    sB = []
    for i, pid in enumerate(("p001", "p046", "p021"), 1):
        q = by[pid]
        sB.append(describe(f"s1{i}", "B", "smoke", "smoke", q["arm"], q["format"], q["kind"], q["shire_mask"], "rgm136 gemmL", "smoke",
                           f"E206's {pid} (E206 and E213 arm B's smoke; it ran on card 1): the session gate", C1))
    if "rgm211 gemmLn" in loopsB:
        sB.append(describe("s15", "B", "smoke", "smoke", "gemmLn2x2x2", "fp32", "random", "0xffffffff", "rgm211 gemmLn", "smoke",
                           "rgm211's host and ELF on card 1 (never ran there): family 'rgm211 gemmLn''s own smoke and stop path", C1))
    if "rgm211 gemmL" in loopsB:
        sB.append(describe("s16", "B", "smoke", "smoke", "gemmL2x2x2", "fp32", "random", "0xffffffff", "rgm211 gemmL", "smoke",
                           "rgm211's own gemmL loop on card 1 (never ran there): family 'rgm211 gemmL''s own smoke and stop path", C1))
    if "rgm136 gemmLnc" in loopsB:
        sB.append(describe("s14", "B", "smoke", "smoke", "gemmLnc2x2x2", "fp32", "random", "0xffffffff", "rgm136 gemmLnc", "smoke",
                           "E213's s14: rgm211's host with rgm136's ELF on card 1 (family 'rgm136 gemmLnc': its own stop path), right before the "
                           "gemmLnc block (E213 arm B read about 66-68.5 W there against its 72 W x3 stop)", C1))
    p001 = by["p001"]
    tA = describe("t01", "A", "tie", "tie", p001["arm"], p001["format"], p001["kind"], p001["shire_mask"], "rgm136 gemmL", "tie",
                  "E206's p001: E206 arm A, E207 and E213 arm A ran it on this card (the bridge)", A3)
    tB = describe("t02", "B", "tie", "tie", "gemmL4x8x8", "int8", "random", "0xffffffff", "rgm136 gemmL", "tie",
                  "E208's anchor arm 4x8x8-int8-rnd: E208's, E212's and E213 arm B's ties on card 1 (the bridge)", C1)
    return sA, sB, tA, tB


def order(tag, pts, refs, smoke):
    rnd = random.Random(f"E215|{tag}|pass1")
    nc = [p for p in pts if p["loop"] == "rgm136 gemmLnc"]
    t1 = sorted(p["id"] for p in pts if p["family"] in ("P", "C", "R") and p["loop"] != "rgm136 gemmLnc")
    t2 = sorted(p["id"] for p in pts if p["family"] == "L" and p["loop"] != "rgm136 gemmLnc")
    t3k = sorted(p["id"] for p in pts if p["family"] == "S")
    rnd.shuffle(t1)
    rnd.shuffle(t2)
    rnd.shuffle(t3k)
    ref_of = {r["format"]: r["id"] for r in refs}
    by = {p["id"]: p for p in pts}
    t3 = []
    for k in t3k:
        r = ref_of[by[k]["format"]]
        t3 += [k, r, r, k]
    ncids = sorted(p["id"] for p in nc)
    rnd.shuffle(ncids)
    p1 = t1 + t2 + t3
    p2 = list(reversed(t1)) if tag == "A" else list(reversed(t1 + t2))
    tie = "t01" if tag == "A" else "t02"
    nc_smoke = [s["id"] for s in smoke if s["loop"] == "rgm136 gemmLnc"]
    open_smoke = [s["id"] for s in smoke if s["loop"] != "rgm136 gemmLnc"]
    seq = [("tie", tie)] + [("pass1", i) for i in p1] + [("tie", tie)] + [("pass2", i) for i in p2] + [("tie", tie)]
    seq += [("gemmLnc-smoke", i) for i in (nc_smoke if ncids else [])] + [("gemmLnc-pass1", i) for i in ncids] + \
           [("gemmLnc-pass2", i) for i in reversed(ncids)]
    every = set(p["id"] for p in pts)
    if set(t1 + t2 + t3k + ncids) != every:
        raise SystemExit(f"points_e215: arm {tag}'s order does not hold every point")
    return {"seed": f"E215|{tag}|pass1", "tie": tie, "opening_smoke": open_smoke, "gemmLnc_smoke": nc_smoke if ncids else [],
            "tiers": {"1": t1, "2": t2, "3_S_blocks": t3, "gemmLnc": ncids}, "pass1": p1, "pass2": p2,
            "gemmLnc_block": ncids + list(reversed(ncids)), "sequence_blocks": seq}


def build():
    if sha_rel(E206_POINTS) != E206_POINTS_SHA256:
        print(f"points_e215: REFUSED, {E206_POINTS} changed")
        sys.exit(4)
    nr = json.load(open(NEVER))
    cand_sha = hashlib.sha256(open(CAND, "rb").read()).hexdigest()
    if nr.get("candidates_sha256") != cand_sha:
        raise SystemExit("points_e215: desk/neverrun-e215.json was made from another candidates list")
    A, B = arm_a_rows(), arm_b_rows()
    verdict = {(arm, r["id"]): r for arm in ("A", "B") for r in nr["arms"][arm]["points"]}
    dropped = [p["id"] for p in A if not verdict[("A", p["id"])]["never_run"]]
    A = [p for p in A if p["id"] not in dropped]
    bad_b = [p["id"] for p in B if not verdict[("B", p["id"])]["never_run"]]
    if bad_b:
        raise SystemExit(f"points_e215: arm B points found run on card 1: {bad_b} (re-choose before any freeze)")
    RA, RB = references(A, "A", A3), references(B, "B", C1)
    for p in A + B + RA + RB:
        v = verdict[(p["arm_tag"], p["id"])]
        p["never_run_scan"] = {k: v[k] for k in v if k not in ("id", "token", "family", "reading", "kernel", "role")}
    e206 = json.load(open(os.path.join(REPO, E206_POINTS)))
    sA, sB, tA, tB = smoke_tie(e206, A, B)
    arms = {}
    for tag, pts, refs, smk, tie, card in (("A", A, RA, sA, tA, A3), ("B", B, RB, sB, tB, C1)):
        od = order(tag, pts, refs, smk)
        names = {p["id"]: p["name"] for p in pts + refs + smk}
        names[tie["id"]] = tie["name"]
        od["sequence"] = [{"n": n, "block": b, "id": i, "name": names[i]} for n, (b, i) in enumerate(od.pop("sequence_blocks"), 1)]
        od["runs"] = sum(1 for s in od["sequence"] if s["block"] != "gemmLnc-smoke")
        reg = [p for p in pts if p["family"] in ("P", "C", "R")]
        ph = [p for p in pts if p["family"] in ("L", "S")]
        fam = {}
        for p in pts:
            fam[p["family"]] = fam.get(p["family"], 0) + 1
        arms[tag] = {"card": card, "clock": ("600 MHz (aifoundry3: pinned by a boot-time TDP of 0; card 1: as found since September), read, never set"),
                     "n_points": len(pts), "n_registered_points": len(reg), "n_posthoc_points": len(ph), "n_references": len(refs),
                     "registered_cases": sorted({p["case"] for p in reg if p["time_scored"]}),
                     "posthoc_cases": sorted({p["case"] for p in ph if p["time_scored"]}),
                     "families": fam, "by_format": {t: sum(1 for p in pts if p["format"] == t) for t in ("fp32", "int8")},
                     "by_kind": {k: sum(1 for p in pts if p["kind"] == k) for k in sorted({p["kind"] for p in pts})},
                     "by_loop": {k: sum(1 for p in pts if p["loop"] == k) for k in sorted({p["loop"] for p in pts})},
                     "dropped_ran_since": dropped if tag == "A" else [], "points": pts, "references": refs, "smoke": smk, "tie": tie, "order": od}
        arms[tag]["n_registered_cases"] = len(arms[tag]["registered_cases"])
        arms[tag]["n_posthoc_cases"] = len(arms[tag]["posthoc_cases"])
    return {"experiment": "E215", "request": "Q224", "what": "the registered points and order of MM1-v3.1's blind matmul day, two arms (frozen before any E215 datum)",
            "posthoc_label": POSTHOC_LABEL,
            "source_arm_A": {"path": V31_POINTS, "sha256": V31_POINTS_SHA256, "what": "MM1-v3.1's frozen E215 list (60 rows, arm A)"},
            "source_arm_B": {"path": "tools/claims-v3/e215/desk/choice-e215b.json", "sha256": hashlib.sha256(open(CHOICE_B, "rb").read()).hexdigest(),
                             "what": "item 10's rule on card 1 (desk/choose_e215b.py)"},
            "neverrun": {"path": "tools/claims-v3/e215/desk/neverrun-e215.json", "candidates_sha256": cand_sha, "scan_sha256": nr["scan_sha256"]},
            "arms": arms}


def csv_text(out):
    s = io.StringIO()
    w = csv.writer(s, lineterminator="\n")
    w.writerow(["arm", "id", "role", "family", "reading", "case", "time_scored", "name", "loop", "host", "elf", "arm_token", "format", "kind",
                "shire_mask", "shires", "minions", "M", "N", "K", "gemm_computed", "ops_per_minion_per_gemm", "bytes_MB_all", "pass1_position",
                "pass2", "values"])
    for tag in ("A", "B"):
        a = out["arms"][tag]
        pos = {}
        for s_ in a["order"]["sequence"]:
            pos.setdefault(s_["id"], s_["n"])
        p2 = set(a["order"]["pass2"]) | set(a["order"]["tiers"]["gemmLnc"])
        for p in a["points"] + a["references"]:
            w.writerow([tag, p["id"], p["role"], p["family"], p["reading"], p["case"], p["time_scored"], p["name"], p["loop"], p["host"], p["elf"],
                        p["arm"], p["format"], p["kind"], p["shire_mask"], p["shires"], p["minions"], p["M"], p["N"], p["K"], p["gemm_computed"],
                        p["ops_per_minion_per_gemm"], f"{p['bytes_MB']['all']:.1f}", pos.get(p["id"], ""), p["id"] in p2, p["values"]])
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
            print(f"points_e215 candidates --check: desk/candidates-e215.json rebuilt == committed: {same}")
            sys.exit(0 if same else 1)
        json.dump(c, open(CAND, "w"), indent=1)
        print(f"candidates: arm A {len(c['arms']['A'])}, arm B {len(c['arms']['B'])} -> {CAND}")
        return
    out = build()
    jp, cp = os.path.join(HERE, "points-e215.json"), os.path.join(HERE, "points-e215.csv")
    if a.check:
        same_c = json.load(open(CAND)) == json.loads(json.dumps(candidates()))
        same_j = json.load(open(jp)) == json.loads(json.dumps(out))
        same_v = open(cp).read() == csv_text(out)
        ok = same_c and same_j and same_v
        print(f"points_e215 --check: candidates {same_c}; points-e215.json {same_j}; points-e215.csv {same_v}")
        print("PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    json.dump(out, open(jp, "w"), indent=1)
    open(cp, "w").write(csv_text(out))
    for tag in ("A", "B"):
        a_ = out["arms"][tag]
        print(f"arm {tag} ({a_['card']}): {a_['n_points']} points ({a_['n_registered_points']} registered P/C/R, {a_['n_posthoc_points']} post hoc L/S) + "
              f"{a_['n_references']} references; cases registered {a_['n_registered_cases']}, post hoc {a_['n_posthoc_cases']}; {a_['order']['runs']} runs; "
              f"families {a_['families']}; loops {a_['by_loop']}; dropped (ran since) {a_['dropped_ran_since']}")
        print(f"  pass 1: {' '.join(a_['order']['pass1'])}")
        print(f"  pass 2: {' '.join(a_['order']['pass2'])}")
        print(f"  gemmLnc block: {' '.join(a_['order']['gemmLnc_block'])}")


if __name__ == "__main__":
    main()
