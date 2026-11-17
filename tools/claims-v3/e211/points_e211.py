#!/usr/bin/env python3
"""E211 (Q204): every point, run and the seeded order of THE SECOND KERNEL's card session. Desk; standard library.

    python3 -I -B tools/claims-v3/e211/points_e211.py            writes points-e211.json and points-e211.csv here
    python3 -I -B tools/claims-v3/e211/points_e211.py --check    re-makes both in memory and compares (exit 0 = PASS)

A POINT is one configuration (its arm family, shape, format, data kind; the full chip, 32 minions a shire, --seed 1; E206's host arguments,
--seconds 6 --budget 7.5 a scored process, the kit's shorter smoke) and is
its own case: no two points share a shape, format and walk. Three arm families (critic-kernel2 fix 2: each with its own kernel and host):
  gemmL<MB>x<NB>x<KB>    rgm136's walk (mb outer, nb inner), cooperative loads   rgm136's host and ELF (E206's and E207's build)    the twins
  gemmLn<MB>x<NB>x<KB>   rgm211's walk (nb outer, mb inner), cooperative loads   rgm211's host and ELF                              THE SECOND KERNEL
  gemmLnc<MB>x<NB>x<KB>  rgm136's walk, every minion loading for itself           rgm211's host, rgm136's ELF (no new device code)   family C
FAMILIES: W, the walk swap (10 shape pairs: twin and gemmLn); X, the exact controls (MB = 1 or NB = 1: one op stream, 2 pairs); C, the load
operations (gemmLnc at two shapes, each beside a twin run); the smoke (one short checked process of each family at 2x2x2).
THE ORDER (critic-kernel2 fix 4: family C after family W): the smoke; family X (each pair A B or B A, seeded); family W (the 10 pairs in a seeded
order; the pairs 2x8x4, 2x9x4, 3x5x7 and 4x3x6 A B B A or B A A B, the rest A B or B A, seeded); family C (gemmLnc, twin, gemmLnc at each shape).
random.Random(211) decides every coin and the shuffle, in the order the code draws them.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import io
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_JSON = os.path.join(HERE, "points-e211.json")
OUT_CSV = os.path.join(HERE, "points-e211.csv")
SEED = 211
MASK = "0xffffffff"
VALUES = {"fp32": "randn:tools/claims-v3/kinds/tiles/fp32/randn.bin", "int8": "randn:tools/claims-v3/kinds/tiles/int8/full.bin"}
KERNEL_OF = {"gemmL": "rgm136", "gemmLn": "rgm211", "gemmLnc": "rgm136"}
HOST_OF = {"gemmL": "rgm136", "gemmLn": "rgm211", "gemmLnc": "rgm211"}
# family W: (pair id, shape, format, A B B A?, why); twins of E206 arm A (in MM1-v1's fit) and of E207 (blind points of E207, run before E211)
W = [("w01", "2x3x2", "fp32", False, "inside the L3: both walks equal by MM1"),
     ("w02", "3x3x4", "fp32", False, "the knee: A's panel just past the retention"),
     ("w03", "3x6x3", "fp32", False, "B's panel small: the swap trades A's lines for B's"),
     ("w04", "2x8x4", "fp32", True, "B large, A small: the swap fetches fewer fresh lines; NB a power of two (MM1-v1's stride terms)"),
     ("w05", "2x9x4", "fp32", True, "2x8x4's neighbour with NB not a power of two: the stride carryover read beside it (critic-kernel2 fix 7)"),
     ("w06", "3x5x7", "fp32", True, "equal fresh lines a shire-op in both walks, A's stream in most of rgm211's ops; chip DRAM lines 1.45x"),
     ("w07", "3x6x6", "fp32", False, "the same, a second shape"),
     ("w08", "4x3x6", "fp32", True, "A large, B small: rgm211's fresh lines 1.5x a shire-op, 1.9x at the chip"),
     ("w09", "6x6x6", "fp32", False, "the largest footprint (180 MB)"),
     ("w10", "3x5x7", "int8", False, "3x5x7 in int8: the format (time ratio as fp32 in MM1, energy differs)")]
X = [("x01", "1x5x5", "fp32", "MB = 1: one op stream"), ("x02", "3x1x8", "fp32", "NB = 1: one op stream")]
C = [("c01", "2x3x2", "fp32", "w01m", "inside the L3"), ("c02", "3x5x7", "fp32", "w06m", "past the L3")]
SMOKE = [("s01", "gemmL", "2x2x2"), ("s02", "gemmLn", "2x2x2"), ("s03", "gemmLnc", "2x2x2")]
TWIN_HISTORY = {   # where a twin (gemmL, the full chip, random data) ran before, by the registration's own scan (desk/neverrun-e211.json)
    ("2x3x2", "fp32"): ("E207 blind point b04 (MM1-v1's frozen list): never on a card at this registration (only E207's kit stand-ins name it); it runs "
                        "in E207 on this card BEFORE E211 (E211 books no card before E207's data commit): a twin run after E207, labelled"),
    ("3x3x4", "fp32"): "E207 blind point b15: as w01m's",
    ("6x6x6", "fp32"): "E207 blind point b25: as w01m's",
    ("2x8x4", "fp32"): "E206 arm A point (aifoundry3 card 0, data d7e4f35e): IN SAMPLE for MM1-v1",
    ("3x5x7", "fp32"): "E206 arm A point (aifoundry3 card 0): IN SAMPLE for MM1-v1",
    ("3x6x6", "fp32"): "E206 arm A point (aifoundry3 card 0): IN SAMPLE for MM1-v1",
    ("3x5x7", "int8"): "E206 arm A point (aifoundry3 card 0): IN SAMPLE for MM1-v1",
    ("2x2x2", "fp32"): "the smoke's twin: E136 and E146 ran it on aifoundry2 card 0",
}
NEVER = "never run on any card (desk/neverrun-e211.json)"


def blocks(sh):
    return [int(x) for x in sh.split("x")]


def point(pid, family, fam, sh, fmt, role, why, pair=None, twin_of=None):
    MB, NB, KB = blocks(sh)
    ops = 64 * MB * NB * KB
    w = {"fp32": 1, "fp16": 2, "int8": 4}[fmt]
    arm = f"{fam}{sh}"
    return {"id": pid, "family": family, "arm_family": fam, "arm": arm, "shape": sh, "blocks": [MB, NB, KB], "format": fmt, "kind": "random",
            "walk": "nm" if fam == "gemmLn" else "mn", "coop": fam != "gemmLnc", "kernel": KERNEL_OF[fam], "host": HOST_OF[fam],
            "shire_mask": MASK, "shires": 32, "minions": 1024, "per_shire": 32,
            "M": 1024 * MB, "N": 512 * NB, "K": 512 * KB * w, "ops_per_minion_per_gemm": ops,
            "host_args": ["--test", "fma", "--type", fmt, "--pattern", "none", "--values", f"{arm}:{VALUES[fmt]}", "--shires", MASK, "--per-shire", "32",
                          "--seconds", "6", "--budget", "7.5", "--seed", "1"],
            "role": role, "pair": pair, "twin_of": twin_of, "why": why,
            "history": TWIN_HISTORY.get((sh, fmt), NEVER) if fam == "gemmL" else NEVER}


def build():
    rng = random.Random(SEED)
    pts = []
    for pid, sh, fmt, abba, why in W:
        pts.append(point(pid + "m", "W", "gemmL", sh, fmt, "twin", why, pair=pid))
        pts.append(point(pid + "n", "W", "gemmLn", sh, fmt, "second kernel", why, pair=pid))
    for pid, sh, fmt, why in X:
        pts.append(point(pid + "m", "X", "gemmL", sh, fmt, "control twin", why, pair=pid))
        pts.append(point(pid + "n", "X", "gemmLn", sh, fmt, "control", why, pair=pid))
    for pid, sh, fmt, twin, why in C:
        pts.append(point(pid + "c", "C", "gemmLnc", sh, fmt, "no cooperation", why, pair=pid, twin_of=twin))
    smoke = []
    for sid, fam, sh in SMOKE:
        p = point(sid, "smoke", fam, sh, "fp32", "smoke", "the smoke: one short checked process of the family")
        smoke.append(p)
    # ---- the order
    order = []

    def run(pid, block, pair, n_in_pair):
        order.append({"n": len(order) + 1, "point": pid, "block": block, "pair": pair, "place_in_pair": n_in_pair})
    for s in smoke:
        run(s["id"], "smoke", None, None)
    for pid, sh, fmt, why in X:
        first = "m" if rng.random() < 0.5 else "n"
        second = "n" if first == "m" else "m"
        run(pid + first, "X", pid, 1)
        run(pid + second, "X", pid, 2)
    wpairs = list(W)
    rng.shuffle(wpairs)
    for pid, sh, fmt, abba, why in wpairs:
        first = "m" if rng.random() < 0.5 else "n"
        second = "n" if first == "m" else "m"
        seq = [first, second, second, first] if abba else [first, second]
        for i, x in enumerate(seq):
            run(pid + x, "W", pid, i + 1)
    for pid, sh, fmt, twin, why in C:
        for i, x in enumerate((pid + "c", twin, pid + "c")):
            run(x, "C", pid, i + 1)
    allp = {p["id"]: p for p in pts + smoke}
    for o in order:
        o["arm"] = allp[o["point"]]["arm"]
        o["format"] = allp[o["point"]]["format"]
        o["kernel"] = allp[o["point"]]["kernel"]
        o["host"] = allp[o["point"]]["host"]
    counts = {"scored_runs": sum(1 for o in order if o["block"] != "smoke"), "smoke_runs": len(smoke), "points": len(pts),
              "second_kernel_points": sum(1 for p in pts if p["arm_family"] == "gemmLn"), "twin_points": sum(1 for p in pts if p["arm_family"] == "gemmL"),
              "family_C_points": sum(1 for p in pts if p["arm_family"] == "gemmLnc")}
    return {"experiment": "E211", "request": "Q204", "seed": SEED,
            "what": "every point and run of E211 and the seeded order; points are their own cases; the full chip, 32 minions a shire, --seed 1",
            "arm_families": {"gemmL": {"kernel": "rgm136", "host": "rgm136"}, "gemmLn": {"kernel": "rgm211", "host": "rgm211"},
                             "gemmLnc": {"kernel": "rgm136", "host": "rgm211"}},
            "points": pts, "smoke": smoke, "order": order, "counts": counts}


def csv_text(d):
    buf = io.StringIO()
    keys = ["id", "family", "arm", "arm_family", "shape", "format", "kind", "walk", "coop", "kernel", "host", "M", "N", "K", "ops_per_minion_per_gemm",
            "role", "pair", "twin_of", "history"]
    w = csv.DictWriter(buf, fieldnames=keys, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for p in d["points"] + d["smoke"]:
        w.writerow(p)
    return buf.getvalue()


def main():
    d = build()
    js = json.dumps(d, indent=1, sort_keys=True) + "\n"
    cs = csv_text(d)
    if sys.argv[1:] == ["--check"]:
        ok = js == open(OUT_JSON).read() and cs == open(OUT_CSV).read()
        print("points_e211 --check:", "PASS" if ok else "DIFFERS")
        return 0 if ok else 1
    open(OUT_JSON, "w").write(js)
    open(OUT_CSV, "w").write(cs)
    print(f"points-e211: {d['counts']}; order: " + " ".join(f"{o['point']}" for o in d["order"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
