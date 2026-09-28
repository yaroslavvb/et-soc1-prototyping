#!/usr/bin/env python3
"""DESIGN2 placement sets, re-derived from the repository's own MARTY map and checked against the die frame.

Source of the map: R/workloads/nocbench/analyze.py:50-60 (MARTY, EMPTY), read from the file, not copied.
Die frame (observability.md:262-284, an inference): die row r = map x (r0 = the edge with I/O and PCIe),
die column c = map y + 1 (c1 beside the west memory strip MS0-3, c6 beside the east strip MS4-7).
Minion semantics: sparsity_host --shires M --per-shire N runs hart 0 of minions 0..N-1 of each shire in M
(R/workloads/sparsity/host/main.cpp:275-287 participants(); kernel/sparsity.c:557 returns for (minion & 31) >= N).
"""
import ast, json, re, sys
R = sys.argv[1] if len(sys.argv) > 1 else "/home/yaroslavvb/claude/et-soc1-heat"
src = open(f"{R}/workloads/nocbench/analyze.py").read()
MARTY = ast.literal_eval(re.search(r"MARTY = (\{.*?\})\n", src, re.S).group(1))
EMPTY = ast.literal_eval(re.search(r"EMPTY = (\[.*?\])", src).group(1))
assert sorted(MARTY) == list(range(32)) and len(set(MARTY.values())) == 32
assert set(MARTY.values()) | set(EMPTY) == {(x, y) for x in range(6) for y in range(6)}
die = {s: (x, y + 1) for s, (x, y) in MARTY.items()}           # shire -> (row, col)
NONCOMP = {(0, 4): "M/S", (5, 4): "M/S", (0, 5): "IO/PCIe", (0, 6): "IO/PCIe"}   # die frame of EMPTY
assert set(NONCOMP) == {(x, y + 1) for x, y in EMPTY}
IO = [(0, 5), (0, 6)]; MS = [(0, 4), (5, 4)]
S = list(range(32))
def mask(ss): return f"0x{sum(1 << s for s in ss):08x}"
def sel(f): return sorted(s for s in S if f(*die[s]))
def adj(rc, cells): return any(abs(rc[0] - a) + abs(rc[1] - b) == 1 for a, b in cells)
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
    "MEM8":  sel(lambda r, c: c in (1, 6) and 1 <= r <= 4),
    "EDGE8": sel(lambda r, c: r in (0, 5)),
    "CEN8":  sel(lambda r, c: 1 <= r <= 4 and c in (3, 4)),
    "W12":   sel(lambda r, c: 1 <= r <= 4 and c <= 3),
    "E12":   sel(lambda r, c: 1 <= r <= 4 and c >= 4),
    "N12":   sel(lambda r, c: r in (1, 2)),
    "S12":   sel(lambda r, c: r in (3, 4)),
    # sensor-field-balanced antisymmetric pairs (DESIGN2 section 2.2): no tile beside the unsensed I/O-PCIe cells,
    # and the same number of tiles beside the (sensed, unloaded) master/spare cells on each side
    "W8b":   sel(lambda r, c: (r in (2, 3) and c <= 3) or (r == 4 and c <= 2)),
    "E8b":   sel(lambda r, c: (r in (2, 3) and c >= 4) or (r == 4 and c >= 5)),
    "N8b":   sel(lambda r, c: r in (1, 2) and c <= 4),
    "S8b":   sel(lambda r, c: r in (3, 4) and c <= 4),
    "B4NE":  [5, 20, 28, 29], "B4SW": [2, 10, 11, 19], "B4C": sel(lambda r, c: r in (2, 3) and c in (3, 4)),
    "UNI32": S,
}
# identities (shire level)
I, P = set(G["INT16"]), set(G["PER16"])
assert len(I) == len(P) == 16 and not I & P and I | P == set(S)
assert set(G["MEM8"]) | set(G["EDGE8"]) == P and not set(G["MEM8"]) & set(G["EDGE8"])
assert set(G["CEN8"]) <= I and len(G["CEN8"]) == 8
for a, b in (("W12", "E12"), ("N12", "S12")):
    A, B = set(G[a]), set(G[b])
    assert len(A) == len(B) == 12 and not A & B and A | B == set(G["INT16"]) | set(G["MEM8"])
# mirror images: W12 <-> E12 under c -> 7 - c, N12 <-> S12 under r -> 5 - r
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
# the masks DESIGN.md registered
for k, m in dict(INT16="0x6477f412", PER16="0x9b880bed", MEM8="0x130002e4", EDGE8="0x88880909",
                 CEN8="0x04647010", B4NE="0x30100020", B4SW="0x00080c04").items():
    assert mask(G[k]) == m, (k, mask(G[k]), m)
# the masks CRITIQUE.md proposed
for k, m in dict(W12="0x03076616", E12="0x747090e0", N12="0x31313232", S12="0x4646c4c4").items():
    assert mask(G[k]) == m, (k, mask(G[k]), m)
# minion level: INT16@16 + PER16@16 = UNI32@16 exactly; INT16@32 + PER16@32 = ALL@32
def minions(shires, per): return {(s, m) for s in shires for m in range(per)}
assert minions(I, 16) | minions(P, 16) == minions(S, 16) and not minions(I, 16) & minions(P, 16)
assert minions(I, 32) | minions(P, 32) == minions(S, 32)
# the old H6 identity is false: half of INT16@32 + half of PER16@32 is not UNI32@16's minion set
assert minions(I, 32) != minions(S, 16)
out = {k: feat(v) for k, v in G.items()}
json.dump(out, open("design2_sets.json", "w"), indent=1)
print("die frame (rows r0..r5, columns c1..c6):")
for r in range(6):
    print(f"  r{r}: " + " ".join(f"{('S' + str(at[(r, c)])) if (r, c) in at else NONCOMP[(r, c)]:>7}" for c in range(1, 7)))
for k, f in out.items():
    print(f"{k:6s} n={f['n']:2d} {f['mask']} rows={f['rows']} cols={f['cols']} ns_edge={f['ns_edge']} mem={f['mem_side']} "
          f"by_io={f['by_io']} by_ms={f['by_ms']} mean_rc=({f['mean_row']},{f['mean_col']}) hops_ctr={f['hops_ctr']} {f['shires']}")
print("all identities hold")
