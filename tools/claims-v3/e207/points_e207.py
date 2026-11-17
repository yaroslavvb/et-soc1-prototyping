#!/usr/bin/env python3
"""E207 (Q199): the registered point list and order of THE BLIND MATMUL DAY - MM1-v1's 53 points, read from its frozen forecast file and never
re-chosen here, each with its shape (blocks MB x NB x KB of rgm136's gemmL arm), format, data kind, shire mask, M, N and K in elements, the GEMM
the participating minions compute, ops a minion a GEMM, bytes, the host's arguments, its case and its tier; the tie point; the smoke; and the
session's order. Written before any E207 datum. Standard library only.

    python3 -I -B tools/claims-v3/e207/points_e207.py            writes points-e207.json and points-e207.csv
    python3 -I -B tools/claims-v3/e207/points_e207.py --check    rebuilds both and compares them with the committed files (exit 0 = PASS)

THE POINTS are MM1-v1's blind-day list (tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv, sha256 pinned below and checked first; exit 4 if it
differs): 53 points in eight families (inside the L3 9, the knee 9, past the L3 8, stride 7, subsets 8, kinds 6, int8 one K block 3, long K 3);
their ids, shapes, formats, kinds, masks and --values strings are that file's, unchanged. A CASE is a distinct (shape, format, shire mask): 47
cases (the six kinds points share their case with a random point). The shire mask is written as the host prints it in its records ("0x%llx":
0x0f0f0f0f is 0xf0f0f0f; MM1-v1's own spelling is kept beside as mm1_mask).
THE TIE is E206's p001 (gemmL2x4x4, 2,048^3 fp32 random, the full chip), run on aifoundry3 by E206 arm A three times as its tie and twice as its
point: the bridge to E206's day, never one of the 53 scored points.
THE SMOKE: one checked 2 s process each of b01, b02 and b03 (gemmL1x3x2 in fp32, int8 and fp16), as E206's smoke form.
THE ORDER: a tie run, pass 1 (tier 1: the 39 full-chip random points of the families inside, knee, past, stride, int8 one K block and long K;
tier 2: the 8 subsets; tier 3: the 6 kinds points; each tier in the order of Python's random.Random("E207|A|pass1") shuffle of its ids, sorted
first), a tie run, pass 2 (pass 1 reversed: every point's two runs at the same mean place, so a linear drift cancels), a tie run: 109 runs.
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
MM1_CSV = "tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv"
MM1_CSV_SHA256 = "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6"
E206_POINTS = "tools/claims-v3/e206/points-e206.json"
E206_POINTS_SHA256 = "121cada61673aabd7f2deaadbb37cb1164c772737cbe1085c6c9f3ff3ac77a1e"
MiB = 2 ** 20
FMTS = ("fp32", "fp16", "int8")
KBLK = {"fp32": 512, "fp16": 1024, "int8": 2048}         # K elements a block (32 k tiles of 16 / 32 / 64)
MACS_PER_OP = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MT, NT, KT = 64, 32, 32                                   # a C block's tiles: 64 row tiles x 32 column tiles; 32 k tiles a block
ABLK, BBLK, CBLK = MT * KT * 1024, KT * NT * 1024, MT * NT * 1024    # bytes of an A, B and C block (reuse_e136.py's)
FULL = 0xFFFFFFFF
TIER = {"inside": 1, "knee": 1, "past": 1, "stride": 1, "int8 one K block": 1, "long K": 1, "subset": 2, "kinds": 3}
SEED = "E207|A|pass1"
SMOKE = ("b01", "b02", "b03")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def mask_geometry(mask):
    """shire s holds rows 128 (s >> 2) .. +128 and columns 128 (s & 3) .. +128 of every C block (E206.md section 2)"""
    sh = [s for s in range(32) if mask >> s & 1]
    rg = sorted({s >> 2 for s in sh})
    cg = sorted({s & 3 for s in sh})
    if len(rg) * len(cg) != len(sh):
        raise SystemExit(f"points_e207: mask 0x{mask:x} is not a product of row groups and column groups")
    return {"shires": len(sh), "row_groups": rg, "column_groups": cg, "rows": 128 * len(rg), "cols": 128 * len(cg)}


def describe(r):
    arm = r["arm"]
    MB, NB, KB = (int(x) for x in arm[len("gemmL"):].split("x"))
    t = r["fmt"]
    mask = int(r["mask"], 16)
    g = mask_geometry(mask)
    M, N, K = 1024 * MB, 512 * NB, KBLK[t] * KB
    if (M, N, K) != (int(r["M"]), int(r["N"]), int(r["K"])):
        raise SystemExit(f"points_e207: {r['id']} M N K differ from MM1-v1's file")
    ops = MB * NB * 2 * KB * 32
    if ops != int(r["ops_per_minion_per_gemm"]):
        raise SystemExit(f"points_e207: {r['id']} ops a minion differ from MM1-v1's file")
    if g["shires"] != int(r["shires"]) or 32 * g["shires"] != int(r["minions"]):
        raise SystemExit(f"points_e207: {r['id']} shires differ from MM1-v1's file")
    Ab, Bb, Cb = MB * KB * ABLK, KB * NB * BBLK, MB * NB * CBLK
    Meff, Neff = g["rows"] * MB, g["cols"] * NB
    gemm = f"{Meff:,} x {Neff:,} x {K:,}" + ("" if mask == FULL else f" (rows {g['rows']} and columns {g['cols']} of each 1,024 x 512 C block)")
    macs = Meff * Neff * K
    if mask == FULL and macs != 1024 * ops * MACS_PER_OP[t]:
        raise SystemExit(f"points_e207: {r['id']} MAC count does not close")
    smask = f"0x{mask:x}"
    p = {"id": r["id"], "case": f"{arm}|{t}|{smask}", "mm1_case": r["case"], "family": r["family"], "tier": TIER[r["family"]], "arm": arm,
         "shape": {"kind": "gemmL", "blocks": [MB, NB, KB]}, "format": t, "kind": r["kind"], "M": M, "N": N, "K": K, "M_computed": Meff,
         "N_computed": Neff, "gemm_computed": gemm, "shire_mask": smask, "mm1_mask": r["mask"], "shires": g["shires"], "minions": 32 * g["shires"],
         "row_groups": g["row_groups"], "column_groups": g["column_groups"], "ops_per_minion_per_gemm": ops, "macs_per_gemm": macs,
         "flop_per_gemm": 2 * macs, "bytes_MB": {"A": Ab / MiB, "B": Bb / MiB, "C": Cb / MiB, "all": (Ab + Bb + Cb) / MiB},
         "footprint_MB_mm1": float(r["footprint_MB"]), "power_of_two_NB": r["power_of_two_NB"] == "True",
         "scored_in_watts": r["scored_in_watts"] == "True", "values": r["values"],
         "host_args": ["--test", "fma", "--type", t, "--pattern", "none", "--values", r["values"], "--shires", smask, "--per-shire", "32",
                       "--seconds", "6", "--budget", "7.5", "--seed", "1"],
         "note": r["note"]}
    p["name"] = f"{arm}.{t}.{r['kind'].split(' ')[0]}" + ("" if mask == FULL else f".m{smask}")
    return p


def build():
    if sha_rel(MM1_CSV) != MM1_CSV_SHA256:
        print(f"points_e207: REFUSED, {MM1_CSV} is not the frozen file (sha256 {sha_rel(MM1_CSV)})")
        sys.exit(4)
    if sha_rel(E206_POINTS) != E206_POINTS_SHA256:
        print(f"points_e207: REFUSED, {E206_POINTS} changed")
        sys.exit(4)
    rows = list(csv.DictReader(open(os.path.join(REPO, MM1_CSV), newline="")))
    pts = [describe(r) for r in rows]
    if len(pts) != 53 or len({p["id"] for p in pts}) != 53:
        raise SystemExit("points_e207: want 53 distinct points")
    cases = sorted({p["case"] for p in pts})
    e206 = json.load(open(os.path.join(REPO, E206_POINTS)))
    p001 = next(p for p in e206["points"] if p["id"] == "p001")
    tie = {"id": "t01", "e206_id": "p001", "role": "the tie: E206's p001, run on aifoundry3 by E206 arm A (the bridge to that day); never scored as a point",
           "arm": p001["arm"], "format": p001["format"], "kind": p001["kind"], "shire_mask": p001["shire_mask"], "shires": p001["shires"],
           "minions": p001["minions"], "M": p001["M"], "N": p001["N"], "K": p001["K"], "ops_per_minion_per_gemm": p001["ops_per_minion_per_gemm"],
           "values": p001["values"], "host_args": p001["host_args"], "name": p001["name"]}
    byid = {p["id"]: p for p in pts}
    rnd = random.Random(SEED)
    p1 = []
    for tier in (1, 2, 3):
        ids = sorted(p["id"] for p in pts if p["tier"] == tier)
        rnd.shuffle(ids)
        p1 += ids
    p2 = list(reversed(p1))
    seq = [("tie", "t01")] + [("pass1", i) for i in p1] + [("tie", "t01")] + [("pass2", i) for i in p2] + [("tie", "t01")]
    seq = [{"n": n, "block": b, "id": i, "name": (tie["name"] if i == "t01" else byid[i]["name"])} for n, (b, i) in enumerate(seq, 1)]
    fam, tiers = {}, {}
    for p in pts:
        fam[p["family"]] = fam.get(p["family"], 0) + 1
        tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
    kinds = {}
    for p in pts:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    return {"experiment": "E207", "request": "Q199", "what": "the registered point list and order of the blind matmul day (frozen before any E207 datum)",
            "card": "aifoundry3 card 0 at its pinned 600 MHz (reads only, nothing set)",
            "source": {"path": MM1_CSV, "sha256": MM1_CSV_SHA256, "what": "MM1-v1's frozen forecasts for the blind matmul day (its point list)"},
            "families": fam, "tiers": {str(k): v for k, v in sorted(tiers.items())}, "by_format": {t: sum(1 for p in pts if p["format"] == t) for t in FMTS},
            "by_kind": kinds, "n_points": len(pts), "n_cases": len(cases), "cases": cases,
            "scored_in_watts": [p["id"] for p in pts if p["scored_in_watts"]], "tie": tie, "smoke": list(SMOKE), "points": pts,
            "order": {"seed": SEED, "tie": "t01", "pass1": p1, "pass2": p2, "runs": len(seq), "points": len(p1), "sequence": seq}}


def csv_text(out):
    s = io.StringIO()
    w = csv.writer(s, lineterminator="\n")
    w.writerow(["id", "case", "name", "family", "tier", "arm", "format", "kind", "shire_mask", "shires", "minions", "M", "N", "K", "M_computed",
                "N_computed", "gemm_computed", "ops_per_minion_per_gemm", "macs_per_gemm", "bytes_MB_all", "scored_in_watts", "pass1_position", "values"])
    pos = {i: n for n, i in enumerate(out["order"]["pass1"], 1)}
    for p in out["points"]:
        w.writerow([p["id"], p["case"], p["name"], p["family"], p["tier"], p["arm"], p["format"], p["kind"], p["shire_mask"], p["shires"], p["minions"],
                    p["M"], p["N"], p["K"], p["M_computed"], p["N_computed"], p["gemm_computed"], p["ops_per_minion_per_gemm"], p["macs_per_gemm"],
                    f"{p['bytes_MB']['all']:.1f}", p["scored_in_watts"], pos.get(p["id"], ""), p["values"]])
    return s.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = build()
    jp, cp = os.path.join(HERE, "points-e207.json"), os.path.join(HERE, "points-e207.csv")
    if a.check:
        same_j = json.load(open(jp)) == json.loads(json.dumps(out))
        same_c = open(cp).read() == csv_text(out)
        print(f"points_e207 --check: points-e207.json rebuilt == committed: {same_j}; points-e207.csv rebuilt == committed: {same_c}; "
              f"{out['n_points']} points, {out['n_cases']} cases, {out['order']['runs']} runs; MM1-v1's list {out['source']['sha256'][:16]} as pinned")
        print("PASS" if (same_j and same_c) else "FAIL")
        sys.exit(0 if (same_j and same_c) else 1)
    json.dump(out, open(jp, "w"), indent=1)
    open(cp, "w").write(csv_text(out))
    print(f"E207 points: {out['n_points']} ({out['n_cases']} cases); families {out['families']}; tiers {out['tiers']}; formats {out['by_format']}; "
          f"kinds {out['by_kind']}; scored in watts {out['scored_in_watts']}")
    o = out["order"]
    print(f"order: seed {o['seed']!r}; {o['points']} points, {o['runs']} runs (tie, pass 1, tie, pass 2 = pass 1 reversed, tie); tie t01 = E206's p001")
    print(f"pass 1: {' '.join(o['pass1'])}")
    print(f"smoke: {' '.join(out['smoke'])}")


if __name__ == "__main__":
    main()
