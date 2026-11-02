#!/usr/bin/env python3
"""Desk-only checks for Q136(a)'s corrections after verification (Mon 2 Nov 2026): every number the README's dated
notes quote that is not already a predictions.json key, recomputed from committed files. Nothing frozen is changed or
re-derived: the frozen predictions are read, never rewritten.
Usage, from the repository's top directory:
    python3 -I docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/corrections-check.py .
Output committed beside it as corrections-check.txt (the README's dated notes cite its sections as [1]-[6])."""
import ast
import difflib
import hashlib
import itertools
import json
import math
import os
import statistics as st
import subprocess
import sys

TOP = sys.argv[1] if len(sys.argv) > 1 else "."
D = "docs/reports/data/2026-11-02-q136a-int8-netlist-predictions"
E79 = "docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices"
FREEZE = "d64ea98c"
ARMS = ("booth_tree", "booth", "booth_swap", "plain")
MERGES = ("map", "hier")


def P(*a):
    return os.path.join(TOP, *a)


def J(*a):
    with open(P(*a)) as f:
        return json.load(f)


pred = J(D, "predictions.json")
e79 = J(E79, "scored.json")["prices"]
hwA = [e79["int8_a"][str(b)]["fJ_ci95"] for b in range(8)]
hwB = [e79["int8_b_kg"][str(b)]["fJ_ci95"] for b in range(8)]
fA = [e79["int8_a"][str(b)]["fJ"] for b in range(8)]
fB = [e79["int8_b_kg"][str(b)]["fJ"] for b in range(8)]
npA = sorted({e79["int8_a"][str(b)]["n_passes"] for b in range(8)})
npB = sorted({e79["int8_b_kg"][str(b)]["n_passes"] for b in range(8)})
medA, medB = st.median(hwA), st.median(hwB)


def f1(v):
    return " ".join("%.1f" % x for x in v)


print("Q136(a) corrections check; frozen predictions read from %s/predictions.json (never rewritten)" % D)
print()
print("[1] E79's 95%% half-widths, board fJ, aifoundry3 (scored.json prices.<list>.<bit>.fJ_ci95; passes %s / %s)" % (npB, npA))
print("    B (int8_b_kg) bits 0-7: %s   median %.2f" % (f1(hwB), medB))
print("    A (int8_a)    bits 0-7: %s   median %.2f" % (f1(hwA), medA))
print("    B sign bit 7: %.2f +- %.2f fJ (interval %.1f to %.1f: it contains 0)" % (
    fB[7], hwB[7], e79["int8_b_kg"]["7"]["fJ_lo"], e79["int8_b_kg"]["7"]["fJ_hi"]))
print("    A sign bit 7: %.2f +- %.2f fJ" % (fA[7], hwA[7]))
print("    predictions.json card_precision_e79 medians: A %.2f, B %.2f (the footing of result 3's table)" % (
    pred["card_precision_e79"]["a_list_board_fJ_ci95_median_4pass"],
    pred["card_precision_e79"]["b_list_board_fJ_ci95_median_4pass"]))
print()


def odd_even(hw):
    return math.sqrt(sum(hw[b] ** 2 for b in (1, 3, 5)) / 9 + sum(hw[b] ** 2 for b in (0, 2, 4)) / 9)


def mean06(hw):
    return math.sqrt(sum(hw[b] ** 2 for b in range(7))) / 7


# each statistic: its predictions.json stats key, its separation key, its half-width from E79's items (independent
# items), and the groups result 3 says it separates (None: say the largest gap only)
BOOTH_B, BOOTH_A = ("booth_tree", "booth"), ("booth_swap",)
STATS = [
    ("B odd - even", "B_odd_minus_even_fJ", odd_even(hwB), BOOTH_B),
    ("A odd - even", "A_odd_minus_even_fJ", odd_even(hwA), BOOTH_A),
    ("A sign, B = 0x55 - B = 1", "A_sign_dense_minus_one_fJ", math.sqrt(2) * hwA[7], BOOTH_A),
    ("B list mean, bits 0-6", "B_mean_bits0to6_fJ", mean06(hwB), BOOTH_B),
    ("A list mean, bits 0-6", "A_mean_bits0to6_fJ", mean06(hwA), None),
    ("B sign, A = 0x55 - A = 1", "B_sign_dense_minus_one_fJ", math.sqrt(2) * hwB[7], None),
    ("B sign, word 2 - word 1", "B_sign_w2_minus_w1_fJ", math.sqrt(2) * hwB[7], None),
    ("A sign, word 2 - word 1", "A_sign_w2_minus_w1_fJ", math.sqrt(2) * hwA[7], None),
]

print("[2] Each statistic's half-width from the items it uses (E79's per-item half-widths, items independent: a")
print("    difference of two three-bit means sqrt(sum of the six hw^2 / 9), of two items sqrt(2) x hw, a seven-bit mean")
print("    sqrt(sum hw^2) / 7), against the median footing predictions.json used; gaps |stat_i - stat_j| / half-width")
tree_vs_booth = {}
for name, key, hw_items, group in STATS:
    for mk in MERGES:
        sep = pred["separation"][mk][key]
        hw_lane = sep["card_ci95_halfwidth_fJ_expected"]
        v = sep["by_arm"]
        for a in ARMS:
            assert abs(v[a] - pred["arms"][a]["stats"][mk][key]) < 1e-9, (a, mk, key)
        gaps = {(a, b): abs(v[a] - v[b]) / hw_items for a, b in itertools.combinations(ARMS, 2)}
        gl = {(a, b): abs(v[a] - v[b]) / hw_lane for a, b in itertools.combinations(ARMS, 2)}
        tree_vs_booth[(name, mk)] = (gaps[("booth_tree", "booth")], gl[("booth_tree", "booth")])
        vals = " / ".join("%+.1f" % v[a] for a in ARMS)
        line = "    %-26s %-4s %s fJ; hw items %.2f (median footing %.2f)" % (name, mk, vals, hw_items, hw_lane)
        if group:
            cross = [k for k in gaps if (k[0] in group) != (k[1] in group)]
            gi = [gaps[k] for k in cross]
            gm = [gl[k] for k in cross]
            line += "; %s from the rest: %.2f-%.2f (median footing %.2f-%.2f)" % (
                "+".join(group), min(gi), max(gi), min(gm), max(gm))
        else:
            line += "; largest gap any pair: %.2f (median footing %.2f)" % (max(gaps.values()), max(gl.values()))
        print(line)
print("    booth_tree vs booth, largest over these statistics and both merges: %.2f per item (%s, %s); median footing %.2f" % (
    max(x[0] for x in tree_vs_booth.values()),
    *max(tree_vs_booth, key=lambda k: tree_vs_booth[k][0]),
    max(x[1] for x in tree_vs_booth.values())))
print("    A sign word-2 ratio, E79's 4-pass precision of a ratio of two A sign items: +- %.1f%% (sqrt(2) x %.2f / %.1f)" % (
    100 * math.sqrt(2) * hwA[7] / fA[7], hwA[7], fA[7]))
print()

print("[3] Sign bit, word 2 / word 1 (predictions.json arms.<netlist>.stats.<merge>.<side>_sign_w2_over_w1)")
allr = []
for side in ("B", "A"):
    for mk in MERGES:
        r = [pred["arms"][a]["stats"][mk]["%s_sign_w2_over_w1" % side] for a in ARMS]
        allr += r
        print("    %s %-4s %s" % (side, mk, " / ".join("%.3f" % x for x in r)))
print("    range over the four netlists, both sides and both merges: %.3f-%.3f; largest |ratio - 1| %.3f" % (
    min(allr), max(allr), max(abs(x - 1) for x in allr)))
print()

print("[4] Odd / even ratios (predictions.json arms.<netlist>.stats.<merge>.<side>_odd_over_even)")
for side in ("B", "A"):
    for mk in MERGES:
        r = [pred["arms"][a]["stats"][mk]["%s_odd_over_even" % side] for a in ARMS]
        print("    %s %-4s %s" % (side, mk, " / ".join("%.3f" % x for x in r)))
print()

# E79's base words: make_e130.py's constants (read with ast, not run), checked against committed tiles' bytes
src = open(P("tools/claims-v3/kinds/make_e130.py")).read()
const = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        if node.targets[0].id in ("E79_A", "E79_B"):
            const[node.targets[0].id] = ast.literal_eval(node.value)


def halves(path):
    b = open(P(path), "rb").read()
    assert len(b) == 2048, path
    return set(b[:1024]), set(b[1024:])


e102_a, e102_b = halves("tools/claims-v3/kinds/e102/tiles/int8/hq.bin")
e79_a, e79_b = halves(E79 + "/aifoundry3/hlp/p7910/tiles/a8q.b7910.bin")
e130 = J("tools/claims-v3/kinds/e130/e130.json")
bases = e130["bases"]
w79 = list(const["E79_B"])
print("[5] Base words (tools/claims-v3/kinds/e130/e130.json bases; E79's from make_e130.py E79_A, E79_B)")
print("    E79/E102 B word: %s; E102 hq.bin B half's byte values equal it: %s; its A half: %s" % (
    " ".join("%02x" % x for x in w79), e102_b == set(w79), sorted("%02x" % x for x in e102_a)))
print("    E79 A base: %02x; E79 a8q tile's A half: %s, B half: %s" % (
    const["E79_A"], sorted("%02x" % x for x in e79_a), sorted("%02x" % x for x in e79_b)))
hb1_a, hb1_b = halves("tools/claims-v3/kinds/e130/tiles/int8/hb1.bin")
print("    e130 hb1 tile: A half %s, B half's byte values = B1: %s" % (
    sorted("%02x" % x for x in hb1_a), hb1_b == {int(x, 16) for x in bases["B1"]}))
for name in ("B1", "B2"):
    w = [int(x, 16) for x in bases[name]]
    shared = [(w.index(x), x, w79.index(x)) for x in w if x in w79]
    print("    %s %s: bytes shared with E79's B word: %s; holds E79's A base %02x: %s" % (
        name, " ".join("%02x" % x for x in w),
        ", ".join("%02x (lane %d here, lane %d in E79's)" % (x, i, j) for i, x, j in shared) or "none",
        const["E79_A"], const["E79_A"] in w))
for name in ("A1", "A2"):
    x = int(bases[name], 16)
    print("    %s %02x: equals E79's A base: %s; is a byte of E79's B word: %s" % (
        name, x, x == const["E79_A"], ("lane %d" % w79.index(x)) if x in w79 else "no"))
pc4 = [x for x in range(256) if bin(x).count("1") == 4]
c1 = [x for x in pc4 if ((x >> 6) & 1) + ((x >> 5) & 1) == 1]
c2 = [x for x in pc4 if (x >> 6) & 1 and (x >> 5) & 1]
print("    popcount-4 bytes: %d; with b6 + b5 = 1 (B1's, A1's class): %d, of them in E79's B word: %s; with b6 = b5 = 1: %d" % (
    len(pc4), len(c1), " ".join("%02x" % x for x in w79 if x in c1), len(c2)))
print()

print("[6] sha256.txt, each line from its own directory; README.md against the README as frozen at %s" % FREEZE)
ok = {"data dir": 0, "top directory": 0}
bad = []
for ln in open(P(D, "sha256.txt")):
    ln = ln.rstrip("\n")
    if not ln or ln.startswith("#"):
        continue
    h, name = ln.split(None, 1)
    if name == "README.md":
        frozen = subprocess.run(["git", "-C", TOP, "show", "%s:%s/README.md" % (FREEZE, D)],
                                capture_output=True, check=True).stdout
        cur = open(P(D, "README.md"), "rb").read()
        sm = difflib.SequenceMatcher(None, frozen.decode().splitlines(), cur.decode().splitlines(), autojunk=False)
        removed = sum(i2 - i1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag in ("replace", "delete"))
        added = sum(j2 - j1 for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag in ("replace", "insert"))
        print("    README.md: the frozen README (git show %s) hashes to the line: %s; the current README removes %d"
              " frozen lines and inserts %d" % (FREEZE, hashlib.sha256(frozen).hexdigest() == h, removed, added))
        continue
    base = "top directory" if name.startswith("tools/") else "data dir"
    path = P(name) if base == "top directory" else P(D, name)
    if hashlib.sha256(open(path, "rb").read()).hexdigest() == h:
        ok[base] += 1
    else:
        bad.append(name)
print("    match from the data dir: %d; from the top directory: %d; mismatched: %s" % (
    ok["data dir"], ok["top directory"], bad or "none"))
