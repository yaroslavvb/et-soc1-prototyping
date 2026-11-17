#!/usr/bin/env python3
"""E206 (Q198): the registered point list and each arm's order - every point's shape (blocks MB x NB x KB of rgm136's gemmL arm, or one of the
line-cost law's arms gemmc1 / gemmc8s / gemmc16s), format, data kind, shire mask, M, N and K in elements, the GEMM the participating minions compute,
ops a minion a GEMM, bytes, the host's arguments, and the order of the two arms' runs. Written before any E206 datum. Standard library only.

    python3 -I -B tools/claims-v3/e206/points_e206.py            writes points-e206.json and points-e206.csv
    python3 -I -B tools/claims-v3/e206/points_e206.py --check    rebuilds both and compares them with the committed files (exit 0 = PASS)

THE POINTS are the design lane's (Q198 sweep-design, Mon 16 Nov 2026), rebuilt here by the same rules: 119 points in eight families (star 28,
K ladder 15, square 14, extreme 13, anchor 9, zeros 14, subset 16, kinds 10), one entry per distinct (arm, MB, NB, KB, format, kind, mask).
WHICH ARM RUNS A POINT: arm A (aifoundry3 card 0) runs all 119; arm B (aifoundry1 card 1) runs the 113 whose planning peak sits under its 65 W line:
the design's planning peaks (desk/design-planning-e206.json, copied unchanged, sha256 in the JSON; planning estimates, not forecasts) keep six
L2-resident fp32 and fp16 points off card 1 (p029, p031, p071, p072, p110, p112).
THE ORDER of each arm: a tie run (p001, 2,048^3 fp32 random), pass 1 (tier 1: star, K ladder, square, extreme; tier 2: anchors, zeros; tier 3:
subsets, kinds; each tier in the order of Python's random.Random("E206|A|pass1") / ("E206|B|pass1") shuffle of its ids), a tie run, pass 2 (pass 1
reversed), a tie run: 241 runs on arm A, 229 on arm B. The rebuilt order must equal the design's sequence or this script stops (exit 3).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.join(HERE, "desk", "design-planning-e206.json")
MiB = 2 ** 20
FMTS = ("fp32", "fp16", "int8")
KBLK = {"fp32": 512, "fp16": 1024, "int8": 2048}         # K elements a block (32 k tiles of 16 / 32 / 64)
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MT, NT, KT = 64, 32, 32                                   # a C block's tiles: 64 row tiles x 32 column tiles; 32 k tiles a block
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024    # bytes of an A, B and C block (reuse_e136.py's)
FULL = 0xFFFFFFFF
VALUES = {   # E136's own --values strings (tools/claims-v3/e136/protocol.json); the arm prefix is added per point
    ("fp32", "random"): "randn:tools/claims-v3/kinds/tiles/fp32/randn.bin",
    ("fp16", "random"): "randn:tools/claims-v3/kinds/tiles/fp16/randn.bin",
    ("int8", "random"): "randn:tools/claims-v3/kinds/tiles/int8/full.bin",
    ("fp32", "zeros"): "tiles:tools/claims-v3/kinds/tiles/fp32/zeros.bin",
    ("fp16", "zeros"): "tiles:tools/claims-v3/kinds/tiles/fp16/zeros.bin",
    ("int8", "zeros"): "tiles:tools/claims-v3/kinds/tiles/int8/zeros.bin",
    ("fp32", "sparse50"): "sparse50:tools/claims-v3/kinds/tiles/fp32/sparse50.bin",
    ("fp16", "sparse50"): "sparse50:tools/claims-v3/kinds/tiles/fp16/sparse50.bin",
    ("int8", "sparse50"): "sparse50:tools/claims-v3/kinds/tiles/int8/sparse50.bin",
    ("fp32", "real"): "tiles:tools/claims-v3/kinds/real2/tiles/fp32/gpt2_l9_attn_qk.bin,tools/claims-v3/kinds/real2/tiles/fp32/gpt2_l3_mlp_down.bin,"
                      "tools/claims-v3/kinds/real2/tiles/fp32/bert_l6_up.bin,tools/claims-v3/kinds/real2/tiles/fp32/vit_l5_down.bin",
    ("fp16", "real"): "tiles:tools/claims-v3/kinds/real2/tiles/fp16/gpt2_l9_attn_qk.bin,tools/claims-v3/kinds/real2/tiles/fp16/bert_l6_up.bin,"
                      "tools/claims-v3/kinds/real2/tiles/fp16/vit_l5_down.bin,tools/claims-v3/kinds/real2/tiles/fp16/gpt2_l6_mlp_down_fp16fwd.bin",
    ("int8", "real"): "tiles:tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p999.bin,tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_p9999.bin,"
                      "tools/claims-v3/kinds/real2/tiles/int8/gpt2_l6_down_per_token.bin,tools/claims-v3/kinds/real2/tiles/int8/gpt2_l11_down_p999.bin",
}
REAL_TILES = {t: [x.rsplit("/", 1)[1][:-4] for x in VALUES[(t, "real")].split(":", 1)[1].split(",")] for t in FMTS}
MASKS = {  # shire masks of the subset family: (name, rows of C a block, columns of C a block); shire s holds rows 128 (s >> 2) and columns 128 (s & 3)
    0x1: ("s1", 128, 128), 0xF: ("s4r", 128, 512), 0xFF: ("s8r", 256, 512), 0x11111111: ("s8c", 1024, 128), 0xFFFF: ("s16", 512, 512),
    FULL: ("full", 1024, 512)}
SEEDS = {"A": "E206|A|pass1", "B": "E206|B|pass1"}


def P(group, tier, MB, NB, KB, t, kind, mask=FULL, note="", arm_name=None):
    return {"family": group, "tier": tier, "MB": MB, "NB": NB, "KB": KB, "format": t, "kind": kind, "mask": mask, "note": note, "arm_name": arm_name}


def points():
    pts = []
    star = [(2, 4, 4, "centre"), (1, 4, 4, "M ladder"), (4, 4, 4, "M ladder"), (8, 4, 4, "M ladder"),
            (2, 1, 4, "N ladder"), (2, 2, 4, "N ladder"), (2, 8, 4, "N ladder"), (2, 16, 4, "N ladder"),
            (2, 4, 1, "K ladder"), (2, 4, 2, "K ladder"), (2, 4, 8, "K ladder"), (2, 4, 16, "K ladder")]
    for MB, NB, KB, note in star:
        for t in ("fp32", "int8"):
            pts.append(P("star", 1, MB, NB, KB, t, "random", note=note))
        if (MB, NB, KB) in ((2, 4, 4), (8, 4, 4), (2, 16, 4), (2, 4, 16)):
            pts.append(P("star", 1, MB, NB, KB, "fp16", "random", note=note))
    for KB in (1, 2, 4, 8, 16, 32):
        for t in ("fp32", "int8"):
            pts.append(P("kladder", 1, 1, 1, KB, t, "random", note="K ladder at M 1,024, N 512"))
        if KB in (1, 4, 32):
            pts.append(P("kladder", 1, 1, 1, KB, "fp16", "random", note="K ladder at M 1,024, N 512"))
    sq = {1024: {"fp32": (1, 2, 2), "fp16": (1, 2, 1)}, 2048: {"fp32": (2, 4, 4), "fp16": (2, 4, 2), "int8": (2, 4, 1)},
          3072: {"fp32": (3, 6, 6), "fp16": (3, 6, 3)}, 4096: {"fp32": (4, 8, 8), "fp16": (4, 8, 4), "int8": (4, 8, 2)},
          6144: {"fp32": (6, 12, 12), "fp16": (6, 12, 6), "int8": (6, 12, 3)}, 8192: {"fp32": (8, 16, 16), "fp16": (8, 16, 8), "int8": (8, 16, 4)}}
    for n, d in sq.items():
        for t, (MB, NB, KB) in d.items():
            pts.append(P("square", 1, MB, NB, KB, t, "random", note=f"{n:,}^3 in elements"))
    ext = [((8, 1, 4), ("fp32", "int8"), "tall: 8,192 x 512"), ((1, 16, 4), ("fp32", "int8"), "wide: 1,024 x 8,192; NB 16, a power of two"),
           ((1, 15, 4), ("fp32", "int8"), "wide, NB 15: the stride pair of 1x16x4 (E169's step)"),
           ((8, 16, 1), ("fp32", "int8"), "K short at 8,192 x 8,192: one TensorStore every 32 ops"),
           ((8, 1, 16), ("fp32",), "tall with long K"), ((1, 16, 16), ("fp32",), "wide with long K"),
           ((3, 5, 7), ("fp32", "fp16", "int8"), "irregular: no power of two in M, N or K blocks")]
    for (MB, NB, KB), fm, note in ext:
        for t in fm:
            pts.append(P("extreme", 1, MB, NB, KB, t, "random", note=note))
    for an, note in (("gemmc1", "c1: one block, L2-resident"), ("gemmc8s", "c8s: 8 blocks, C shared, L3-served"),
                     ("gemmc16s", "c16s: 16 blocks, C shared, fresh lines")):
        for t in FMTS:
            pts.append(P("anchor", 2, 1, 1, 1, t, "random", note=note, arm_name=an))
    for (MB, NB, KB), fm in (((1, 1, 1), ("fp32", "int8")), ((1, 1, 4), ("fp32", "fp16")), ((1, 1, 32), ("fp32", "int8")),
                             ((2, 4, 4), ("fp32", "fp16", "int8")), ((8, 16, 16), ("fp32",)), ((8, 16, 4), ("int8",)), ((8, 16, 1), ("fp32",))):
        for t in fm:
            pts.append(P("zeros", 2, MB, NB, KB, t, "zeros", note="zeros at this regime"))
    for an in ("gemmc1", "gemmc16s"):
        pts.append(P("zeros", 2, 1, 1, 1, "fp32", "zeros", note="anchor zeros", arm_name=an))
    for mask in (0x1, 0xF, 0xFF, 0x11111111, 0xFFFF, FULL):
        for t in ("fp32", "int8"):
            pts.append(P("subset", 3, 4, 8, 4, t, "random", mask=mask, note="streaming shape 4x8x4 (E146's D4) on a shire subset"))
    for mask in (0x1, 0xFF):
        for t in ("fp32", "int8"):
            pts.append(P("subset", 3, 1, 1, 1, t, "random", mask=mask, note="warm shape 1x1x1 on a shire subset"))
    for t in FMTS:
        pts.append(P("kinds", 3, 1, 1, 1, t, "real", note="real tensors, warm"))
        pts.append(P("kinds", 3, *sq[2048][t], t, "real", note="real tensors, 2,048^3"))
    for t in ("fp32", "int8"):
        pts.append(P("kinds", 3, 1, 1, 1, t, "sparse50", note="half zeros, warm"))
        pts.append(P("kinds", 3, *sq[2048][t], t, "sparse50", note="half zeros, 2,048^3"))
    seen, out = {}, []
    for p in pts:
        k = (p["arm_name"] or "gemmL", p["MB"], p["NB"], p["KB"], p["format"], p["kind"], p["mask"])
        if k in seen:
            seen[k]["also_in"].append(p["family"])
            continue
        p["also_in"] = []
        seen[k] = p
        out.append(p)
    return out


def describe(p):
    t, MB, NB, KB, mask = p["format"], p["MB"], p["NB"], p["KB"], p["mask"]
    an = p.pop("arm_name")
    if an:
        nblk = {"gemmc1": 1, "gemmc8s": 8, "gemmc16s": 16}[an]
        arm = an
        M, N, K = 1024, 512, KBLK[t]
        ops = nblk * 2 * 32
        Ab, Bb, Cb = nblk * ABLK, nblk * BBLK, (1 if an.endswith("s") else nblk) * CBLK
        gemm = f"{nblk} block(s) of {M:,} x {N:,} x {K:,} a pass" + (", C shared" if an.endswith("s") else "")
        Meff, Neff = M * nblk, N
        macs = nblk * 1024 * 512 * KBLK[t]
        shape = {"kind": "law arm", "blocks_a_pass": nblk, "c_shared": an.endswith("s")}
    else:
        arm = f"gemmL{MB}x{NB}x{KB}"
        M, N, K = 1024 * MB, 512 * NB, KBLK[t] * KB
        ops = MB * NB * 2 * KB * 32
        Ab, Bb, Cb = MB * KB * ABLK, KB * NB * BBLK, MB * NB * CBLK
        name, rows, cols = MASKS[mask]
        Meff, Neff = rows * MB, cols * NB
        gemm = f"{Meff:,} x {Neff:,} x {K:,}" + ("" if mask == FULL else f" (rows {rows} and columns {cols} of each 1,024 x 512 C block)")
        macs = Meff * Neff * K
        shape = {"kind": "gemmL", "blocks": [MB, NB, KB]}
    nsh = bin(mask).count("1")
    vals = f"{arm}:{VALUES[(t, p['kind'])]}"
    p.update({"arm": arm, "shape": shape, "M": M, "N": N, "K": K, "M_computed": Meff, "N_computed": Neff, "gemm_computed": gemm, "shires": nsh,
              "minions": 32 * nsh, "shire_mask": f"0x{mask:x}", "mask_name": MASKS.get(mask, ("?",))[0], "ops_per_minion_per_gemm": ops,
              "macs_per_gemm": macs, "flop_per_gemm": 2 * macs,
              "bytes_MB": {"A": Ab / MiB, "B": Bb / MiB, "C": Cb / MiB, "all": (Ab + Bb + Cb) / MiB},
              "values": vals, "host_args": ["--test", "fma", "--type", t, "--pattern", "none", "--values", vals, "--shires", f"0x{mask:x}",
                                            "--per-shire", "32", "--seconds", "6", "--budget", "7.5", "--seed", "1"]})
    p["mask"] = mask
    return p


def build():
    des = json.load(open(DESIGN))
    pts = [describe(p) for p in points()]
    for i, p in enumerate(pts, 1):
        p["id"] = f"p{i:03d}"
        p["name"] = f"{p['arm']}.{p['format']}.{p['kind']}" + ("" if p["mask"] == FULL else f".{p['mask_name']}")
        dp = des["points"][p["id"]]
        if dp["name"] != p["name"]:
            raise SystemExit(f"points_e206: refused, {p['id']} is {p['name']} here and {dp['name']} in the design")
        p["on_arm"] = {"A": True, "B": bool(dp["arms"]["B"]["under_line"])}
        p["design_planning"] = {"label": "the design lane's desk planning estimate (not a forecast); it decided arm membership only",
                                "cycles_per_op": dp["planning_cycles_per_op"], "board_peak_w": {a: dp["arms"][a]["board_peak_w"] for a in ("A", "B")},
                                "die_peak_c": {a: dp["arms"][a]["die_peak_c"] for a in ("A", "B")}}
        del p["mask"]
    byid = {p["id"]: p for p in pts}
    tie = next(p["id"] for p in pts if p["arm"] == "gemmL2x4x4" and p["format"] == "fp32" and p["kind"] == "random" and p["shires"] == 32)
    order = {}
    for arm, seed in SEEDS.items():
        rnd = random.Random(seed)
        p1 = []
        for tier in (1, 2, 3):
            ids = [p["id"] for p in pts if p["tier"] == tier and p["on_arm"][arm]]
            rnd.shuffle(ids)
            p1 += ids
        p2 = list(reversed(p1))
        seq = [("tie", tie)] + [("pass1", i) for i in p1] + [("tie", tie)] + [("pass2", i) for i in p2] + [("tie", tie)]
        seq = [{"n": n, "block": b, "id": i, "name": byid[i]["name"]} for n, (b, i) in enumerate(seq, 1)]
        if seq != des["order"][arm]["sequence"]:
            print(f"points_e206: the rebuilt order of arm {arm} differs from the design's sequence")
            sys.exit(3)
        order[arm] = {"seed": seed, "tie": tie, "pass1": p1, "pass2": p2, "runs": len(seq), "points": len(p1), "sequence": seq}
    fam = {}
    for p in pts:
        fam[p["family"]] = fam.get(p["family"], 0) + 1
    out = {"experiment": "E206", "request": "Q198", "what": "the registered point list and order (frozen before any E206 datum)",
           "design_planning_sha256": __import__("hashlib").sha256(open(DESIGN, "rb").read()).hexdigest(),
           "families": fam, "by_format": {t: sum(1 for p in pts if p["format"] == t) for t in FMTS},
           "by_kind": {k: sum(1 for p in pts if p["kind"] == k) for k in ("random", "zeros", "real", "sparse50")},
           "on_arm": {a: sum(1 for p in pts if p["on_arm"][a]) for a in ("A", "B")},
           "real_tiles": REAL_TILES, "points": pts, "order": order}
    return out


def csv_text(out):
    s = io.StringIO()
    w = csv.writer(s, lineterminator="\n")
    w.writerow(["id", "name", "family", "tier", "arm", "format", "kind", "shire_mask", "shires", "minions", "M", "N", "K", "M_computed", "N_computed",
                "gemm_computed", "ops_per_minion_per_gemm", "macs_per_gemm", "bytes_MB_all", "on_arm_A", "on_arm_B", "pass1_position_A",
                "pass1_position_B", "values"])
    posA = {i: n for n, i in enumerate(out["order"]["A"]["pass1"], 1)}
    posB = {i: n for n, i in enumerate(out["order"]["B"]["pass1"], 1)}
    for p in out["points"]:
        w.writerow([p["id"], p["name"], p["family"], p["tier"], p["arm"], p["format"], p["kind"], p["shire_mask"], p["shires"], p["minions"], p["M"],
                    p["N"], p["K"], p["M_computed"], p["N_computed"], p["gemm_computed"], p["ops_per_minion_per_gemm"], p["macs_per_gemm"],
                    f"{p['bytes_MB']['all']:.1f}", p["on_arm"]["A"], p["on_arm"]["B"], posA.get(p["id"], ""), posB.get(p["id"], ""), p["values"]])
    return s.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    jp, cp = os.path.join(HERE, "points-e206.json"), os.path.join(HERE, "points-e206.csv")
    if a.check:
        same_j = json.load(open(jp)) == json.loads(json.dumps(out))
        same_c = open(cp).read() == csv_text(out)
        print(f"points_e206 --check: points-e206.json rebuilt == committed: {same_j}; points-e206.csv rebuilt == committed: {same_c}; "
              f"{len(out['points'])} points; arm A {out['on_arm']['A']} points {out['order']['A']['runs']} runs; arm B {out['on_arm']['B']} points "
              f"{out['order']['B']['runs']} runs; the order equals the design's sequence")
        print("PASS" if (same_j and same_c) else "FAIL")
        sys.exit(0 if (same_j and same_c) else 1)
    json.dump(out, open(jp, "w"), indent=1)
    open(cp, "w").write(csv_text(out))
    print(f"E206 points: {len(out['points'])}; families {out['families']}; formats {out['by_format']}; kinds {out['by_kind']}; on arm {out['on_arm']}")
    for arm in ("A", "B"):
        o = out["order"][arm]
        print(f"arm {arm}: seed {o['seed']!r}; {o['points']} points, {o['runs']} runs (tie, pass 1, tie, pass 2 = pass 1 reversed, tie); "
              f"pass 1: {' '.join(o['pass1'])}")


if __name__ == "__main__":
    main()
