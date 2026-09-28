#!/usr/bin/env python3
"""The heat-placement (HP) placements, derived from the repository's own MARTY map and checked; writes placements.json.

    python3 tools/claims-v3/hp/placements.py            # from the tree root: asserts every identity, rewrites placements.json
    python3 tools/claims-v3/hp/placements.py --check    # asserts, and checks that placements.json equals what it would write

A copy of the design's design2_sets.py (DESIGN2 §4.2) with its asserts, extended with the run definitions the blocks
use (mask, minions per shire). Source of the map: workloads/nocbench/analyze.py MARTY and EMPTY, read from the file,
not copied. Die frame (an inference, observability.md:262-284): die row r = map x (r0 = the edge with I/O and PCIe),
die column c = map y + 1 (c1 beside the west memory strip MS0-3, c6 beside the east strip MS4-7).
Minion semantics: sparsity_host --shires M --per-shire N runs hart 0 of minions 0..N-1 of each shire in M
(workloads/sparsity/host/main.cpp participants(); kernel/sparsity.c returns for (minion & 31) >= N).
"""
import ast
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def derive(root=ROOT):
    src = open(os.path.join(root, "workloads", "nocbench", "analyze.py")).read()
    MARTY = ast.literal_eval(re.search(r"MARTY = (\{.*?\})\n", src, re.S).group(1))
    EMPTY = ast.literal_eval(re.search(r"EMPTY = (\[.*?\])", src).group(1))
    assert sorted(MARTY) == list(range(32)) and len(set(MARTY.values())) == 32
    assert set(MARTY.values()) | set(EMPTY) == {(x, y) for x in range(6) for y in range(6)}
    die = {s: (x, y + 1) for s, (x, y) in MARTY.items()}           # shire -> (row, col)
    NONCOMP = {(0, 4): "M/S", (5, 4): "M/S", (0, 5): "IO/PCIe", (0, 6): "IO/PCIe"}
    assert set(NONCOMP) == {(x, y + 1) for x, y in EMPTY}
    IO = [(0, 5), (0, 6)]
    MS = [(0, 4), (5, 4)]
    S = list(range(32))

    def mask(ss):
        return f"0x{sum(1 << s for s in ss):08x}"

    def sel(f):
        return sorted(s for s in S if f(*die[s]))

    def adj(rc, cells):
        return any(abs(rc[0] - a) + abs(rc[1] - b) == 1 for a, b in cells)

    def feat(ss):
        rc = [die[s] for s in ss]
        return dict(n=len(ss), mask=mask(ss), shires=sorted(ss),
                    rows=sorted({r for r, c in rc}), cols=sorted({c for r, c in rc}),
                    ns_edge=sum(r in (0, 5) for r, c in rc),
                    mem_side=sum(c in (1, 6) and 1 <= r <= 4 for r, c in rc),
                    by_io=sum(adj(x, IO) for x in rc), by_ms=sum(adj(x, MS) for x in rc),
                    mean_row=round(sum(r for r, c in rc) / len(rc), 3), mean_col=round(sum(c for r, c in rc) / len(rc), 3),
                    hops_ctr=round(sum(abs(r - 2.5) + abs(c - 3.5) for r, c in rc) / len(rc), 3))
    G = {
        "INT16": sel(lambda r, c: 1 <= r <= 4 and 2 <= c <= 5),
        "PER16": sel(lambda r, c: not (1 <= r <= 4 and 2 <= c <= 5)),
        "MEM8": sel(lambda r, c: c in (1, 6) and 1 <= r <= 4),
        "EDGE8": sel(lambda r, c: r in (0, 5)),
        "CEN8": sel(lambda r, c: 1 <= r <= 4 and c in (3, 4)),
        "W12": sel(lambda r, c: 1 <= r <= 4 and c <= 3),
        "E12": sel(lambda r, c: 1 <= r <= 4 and c >= 4),
        "N12": sel(lambda r, c: r in (1, 2)),
        "S12": sel(lambda r, c: r in (3, 4)),
        "W8b": sel(lambda r, c: (r in (2, 3) and c <= 3) or (r == 4 and c <= 2)),
        "E8b": sel(lambda r, c: (r in (2, 3) and c >= 4) or (r == 4 and c >= 5)),
        "N8b": sel(lambda r, c: r in (1, 2) and c <= 4),
        "S8b": sel(lambda r, c: r in (3, 4) and c <= 4),
        "B4NE": [5, 20, 28, 29], "B4SW": [2, 10, 11, 19], "B4C": sel(lambda r, c: r in (2, 3) and c in (3, 4)),
        "UNI32": S,
    }
    I, P = set(G["INT16"]), set(G["PER16"])
    assert len(I) == len(P) == 16 and not I & P and I | P == set(S)
    assert set(G["MEM8"]) | set(G["EDGE8"]) == P and not set(G["MEM8"]) & set(G["EDGE8"])
    assert set(G["CEN8"]) <= I and len(G["CEN8"]) == 8
    for a, b in (("W12", "E12"), ("N12", "S12")):
        A, B = set(G[a]), set(G[b])
        assert len(A) == len(B) == 12 and not A & B and A | B == set(G["INT16"]) | set(G["MEM8"])
    at = {v: k for k, v in die.items()}
    assert sorted(at[(r, 7 - c)] for r, c in (die[s] for s in G["W12"])) == G["E12"]
    assert sorted(at[(5 - r, c)] for r, c in (die[s] for s in G["N12"])) == G["S12"]
    assert G["B4C"] == [13, 14, 21, 22]
    assert sorted(at[(r, 7 - c)] for r, c in (die[s] for s in G["W8b"])) == G["E8b"]
    assert sorted(at[(5 - r, c)] for r, c in (die[s] for s in G["N8b"])) == G["S8b"]
    for a, b in (("W8b", "E8b"), ("N8b", "S8b")):
        fa, fb = feat(G[a]), feat(G[b])
        assert fa["n"] == fb["n"] == 8 and fa["by_io"] == fb["by_io"] == 0 and fa["by_ms"] == fb["by_ms"]
        assert fa["mem_side"] == fb["mem_side"] and fa["ns_edge"] == fb["ns_edge"] == 0
    # the masks DESIGN.md registered, DESIGN2's new ones, and CRITIQUE.md's (reproduced, not used: DESIGN2 §11 R3)
    for k, m in dict(INT16="0x6477f412", PER16="0x9b880bed", MEM8="0x130002e4", EDGE8="0x88880909", CEN8="0x04647010",
                     B4NE="0x30100020", B4SW="0x00080c04", B4C="0x00606000", W8b="0x02026606", E8b="0x606080e0",
                     N8b="0x01213212", S8b="0x06464404", W12="0x03076616", E12="0x747090e0", N12="0x31313232",
                     S12="0x4646c4c4", UNI32="0xffffffff").items():
        assert mask(G[k]) == m, (k, mask(G[k]), m)
    # minion level: INT16@16 + PER16@16 = UNI32@16 exactly (disjoint); INT16@32 + PER16@32 = ALL@32
    def minions(shires, per):
        return {(s, m) for s in shires for m in range(per)}
    assert minions(I, 16) | minions(P, 16) == minions(S, 16) and not minions(I, 16) & minions(P, 16)
    assert minions(I, 32) | minions(P, 32) == minions(S, 32)
    assert minions(I, 32) != minions(S, 16)      # DESIGN.md's H6 identity is false (DESIGN2 §1)
    groups = {k: feat(v) for k, v in G.items()}
    grid = []
    for r in range(6):
        grid.append([("S%d" % at[(r, c)]) if (r, c) in at else NONCOMP[(r, c)] for c in range(1, 7)])
    return groups, grid


# The runs the blocks launch: name -> (group, minions per shire). Power at 25.6 mW per minion at 600 MHz
# (16-dvfs-and-leakage.md:160-162): 512 -> 13.1 W, 256 -> 6.6 W, 128 -> 3.3 W, 768 -> 19.7 W.
RUNS = {
    "INT16@32": ("INT16", 32), "PER16@32": ("PER16", 32), "UNI32@16": ("UNI32", 16),
    "INT16@16": ("INT16", 16), "PER16@16": ("PER16", 16),
    "MEM8": ("MEM8", 32), "EDGE8": ("EDGE8", 32), "CEN8": ("CEN8", 32),
    "W8b": ("W8b", 32), "E8b": ("E8b", 32), "N8b": ("N8b", 32), "S8b": ("S8b", 32),
    "B4NE": ("B4NE", 32), "B4SW": ("B4SW", 32), "B4C@32": ("B4C", 32),
    "INT16@8": ("INT16", 8), "PER16@8": ("PER16", 8), "UNI32@4": ("UNI32", 4),
    "ALL24": ("UNI32", 24),                     # CAL and preheat: not a registered placement
}


def build(root=ROOT):
    groups, grid = derive(root)
    runs = {}
    for name, (g, per) in RUNS.items():
        f = groups[g]
        runs[name] = {"group": g, "mask": f["mask"], "per_shire": per, "minions": f["n"] * per,
                      "shires": f["shires"], "centroid_rc": [f["mean_row"], f["mean_col"]],
                      "by_io": f["by_io"], "by_ms": f["by_ms"], "mem_side": f["mem_side"], "ns_edge": f["ns_edge"]}
    return {"source": "workloads/nocbench/analyze.py MARTY/EMPTY; die frame observability.md:262-284 (inferred transpose)",
            "grid_rows_r0_r5_cols_c1_c6": grid, "groups": groups, "runs": runs,
            "identities": ["INT16 + PER16 = all 32 shires, disjoint", "MEM8 + EDGE8 = PER16", "CEN8 in INT16",
                           "INT16@16 + PER16@16 = UNI32@16 (minions, disjoint)", "INT16@32 + PER16@32 = ALL@32",
                           "INT16@32 != UNI32@16 (D:154 false)", "W8b<->E8b mirror c->7-c", "N8b<->S8b mirror r->5-r"]}


def main():
    out = build()
    path = os.path.join(HERE, "placements.json")
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if "--check" in sys.argv:
        ok = os.path.exists(path) and open(path).read() == text
        print("placements.json %s; all identities hold" % ("matches" if ok else "DIFFERS"))
        sys.exit(0 if ok else 1)
    open(path, "w").write(text)
    for r, row in enumerate(out["grid_rows_r0_r5_cols_c1_c6"]):
        print("  r%d: " % r + " ".join("%7s" % c for c in row))
    for k, v in out["runs"].items():
        print("%-9s %s x%-2d = %4d minions, centroid %s" % (k, v["mask"], v["per_shire"], v["minions"], v["centroid_rc"]))
    print("all identities hold; wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
