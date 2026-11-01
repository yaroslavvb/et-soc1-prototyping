#!/usr/bin/env python3
"""E93 corrections after verification: the desk check behind README.md § Corrections after verification. Every number
that section cites and the frozen outputs do not already print, read or recomputed from the committed files. Post hoc
throughout: no registered number changes and no verdict moves. No card is touched. Standard library only.

    python3 docs/reports/data/2026-11-01-e93-zero-gate-silicon/corrections-check.py > corrections-check.txt
"""
import datetime
import glob
import hashlib
import json
import math
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
T4 = 2.776


def load(*p):
    return json.load(open(os.path.join(*p)))


s = load(HERE, "scored.json")
e = load(HERE, "e93.json")
reg = load(K, "predictions-e93.json")
t93 = load(K, "e93", "e93.json")
e82 = load(ROOT, reg["inputs_frozen"]["e82_reduction"]["path"])
e88 = load(ROOT, reg["inputs_frozen"]["e88_reduction"]["path"])
kinds = load(K, "kinds.json")
P = s["primary"]
R = P["rules"]
pr = reg["prices"]
RATE = pr["op_rate_per_s"]
PASSES = [str(p) for p in e["passes"]]


def per(a, b=None):
    out = []
    for p in PASSES:
        c = e["per_pass"][p]
        if a in c and c[a].get("D") is not None and (b is None or (b in c and c[b].get("D") is not None)):
            out.append(c[a]["D"] - (c[b]["D"] if b else 0.0))
    return out


def stat(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, T4 * sd / math.sqrt(n), n


def pm(v, d=3):
    m, h, n = stat(v)
    return f"{m:.{d}f} +- {h:.{d}f} (n {n})"


def bits(n):
    return t93["tiles"][n]["stats"]["bus_bits_per_op"]


def W(b, fj, ty):
    return b * fj * 1e-15 * RATE[ty]


def sha(*p):
    return hashlib.sha256(open(os.path.join(*p), "rb").read()).hexdigest()


print("E93 corrections after verification: the desk check (Sun 1 Nov 2026, PDT). Post hoc throughout; no registered")
print("number changes and no verdict moves. The frozen outputs' sha256 (compare with the data commit 9105d764):")
for f in ("scored.json", "results.md", "e93.json", "e93-dipskept.json", "e93-auto.json", "e93-leak0.1994.json",
          "e93-leak0.3803.json", "e93-leak0.545.json", "e93-leak0.json"):
    print(f"   {sha(HERE, f)}  {f}")
print(f"   {sha(K, 'predictions-e93.json')}  tools/claims-v3/kinds/predictions-e93.json")
print(f"   {sha(K, 'score_e93.py')}  tools/claims-v3/kinds/score_e93.py")
print(f"   {sha(K, 'kinds.json')}  tools/claims-v3/kinds/kinds.json")
print(f"Passes kept: {e['passes']}; t(0.975, 4) = {T4}; tally {P['tally']}")

# ------------------------------------------------------------------ C1
print("\nC1. THE FLUSH IS THE DOCUMENTS' STATEMENT; POWER AGREES")
res = {}
for d in sorted(glob.glob(os.path.join(HERE, "aifoundry1-c1", "kinds", "p93*", "runs.jsonl"))):
    for line in open(d):
        r = json.loads(line)
        res[r.get("result")] = res.get(r.get("result"), 0) + 1
print(f"   runs.jsonl `result` over the five passes' launch records: {res}  (no result and no flag is read)")
a32, a16 = pr["a_fj_per_bus_bit"]["fp32"], pr["a_fj_per_bus_bit"]["fp16"]
print(f"   E88's operand-bus price: fp32 {a32:.1f} fJ/bit, fp16 {a16:.1f} fJ/bit")
for label, x, y, ty, db in (
        ("fp32 both sides: dnr_both - dn1_both", "fp32.dnr_both", "fp32.dn1_both", "fp32", bits("fp32.dnr_both") - bits("fp32.dn1_both")),
        ("fp32 A side: a_dnr_b_randn - a_nz_b_randn", "fp32.a_dnr_b_randn", "fp32.a_nz_b_randn", "fp32", bits("fp32.a_dnr_b_randn") - bits("fp32.a_nz_b_randn")),
        ("fp32 B side: a_randn_b_dnr - a_randn_b_nz", "fp32.a_randn_b_dnr", "fp32.a_randn_b_nz", "fp32", bits("fp32.a_randn_b_dnr") - bits("fp32.a_randn_b_nz")),
        ("fp16 both sides: dnr_both - nz_both", "fp16.dnr_both", "fp16.nz_both", "fp16", bits("fp16.dnr_both") - bits("fp16.nz_both")),
        ("fp16 A side: a_dnr_b_randn - a_nz_b_randn", "fp16.a_dnr_b_randn", "fp16.a_nz_b_randn", "fp16", bits("fp16.a_dnr_b_randn") - bits("fp16.a_nz_b_randn"))):
    m, h, n = stat(per(x, y))
    k = db * 1e-15 * RATE[ty]
    print(f"   {label}: {m:.3f} +- {h:.3f} W over {db:,} raw bits an op = {m / k:.1f} +- {h / k:.1f} fJ/bit")
for nm, x in sorted(reg["flush_thresholds"].items()):
    print(f"   {nm}: flushed reading {x['flushed_w']} W, unflushed {x['unflushed_w']} W")
m, h, n = stat(per("fp32.dnr_both", "fp32.dn1_both"))
fl = reg["flush_thresholds"]["fp32.dnr_both"]
ppj = pr["pp_fj_per_booth_bit"]["fp32"]
pp_noflush = t93["tiles"]["fp32.dnr_both"]["booth_pp_bits_per_op_no_flush"]
term = W(pp_noflush, ppj, "fp32")
print(f"   fp32 flushed reading {fl['flushed_w']} W (the bus price alone); unflushed {fl['unflushed_w']} W, of which the partial-product term {term:.3f} W "
      f"= {pp_noflush:,} bits x {ppj:.2f} fJ")
print(f"   R4-fp32-both's high end {m + h:.3f} W: below the bus price alone by {fl['flushed_w'] - (m + h):.3f} W, and {100 * (m + h) / term:.0f}% of the partial-product term with no bus price at all")
ref = t93["reference_counts"]["fp32.r_abs"]
M, B88 = e88["items"]["fp32.r_abs"]["D"], ref["bus_bits_per_op"]
print(f"   the price's source: pp = (M - a x bus) / {ref['booth_pp_bits_per_op']:,}: M = {pr['operand_side_M_w']['fp32']:.3f} W, a x bus = {W(B88, a32, 'fp32'):.3f} W, "
      f"so all {pr['operand_side_M_w']['fp32'] - W(B88, a32, 'fp32'):.3f} W of r_abs's non-bus operand-side power, exponent path included, goes to Booth bits")
dn = e["items"]["fp32.dnr_both"]["D"]
print(f"   the yardstick: E88 fp32.r_abs (this card, frozen result, {B88:,} bus bits) {M['mean']:.3f} +- {M['ci95']:.3f} W; E93 fp32.dnr_both (frozen result, {bits('fp32.dnr_both'):,} bus bits) {dn['mean']:.3f} +- {dn['ci95']:.3f} W; "
      f"difference {M['mean'] - dn['mean']:.2f} W, across sessions; r_abs's exponents also move")

# ------------------------------------------------------------------ the stream, for C2
def words(path):
    w = struct.unpack("<512I", open(path, "rb").read())
    return [w[i * 16:(i + 1) * 16] for i in range(16)], [w[256 + i * 16:256 + (i + 1) * 16] for i in range(16)]


def rates(path, ph):
    """Product-sign flips per lane-cycle (fp16: per half, summed) and exponent bits per lane-cycle, A and B, on the
    fp32/fp16 issue stream (kinds/README.md 1.2), cyclic."""
    A, B = words(path)
    flips = ea = eb = n = 0
    for l in range(8):
        st = [(A[i][k], B[k][8 * h + l]) for k in range(16) for i in range(16) for h in (0, 1)]
        for j, (a, b) in enumerate(st):
            a2, b2 = st[(j + 1) % len(st)]
            n += 1
            if not ph:
                flips += ((a ^ b) >> 31) != ((a2 ^ b2) >> 31)
                ea += bin(((a >> 23) & 255) ^ ((a2 >> 23) & 255)).count("1")
                eb += bin(((b >> 23) & 255) ^ ((b2 >> 23) & 255)).count("1")
            else:
                for sh in (16, 0):
                    flips += (((a ^ b) >> (sh + 15)) & 1) != (((a2 ^ b2) >> (sh + 15)) & 1)
                    ea += bin(((a >> (sh + 10)) & 31) ^ ((a2 >> (sh + 10)) & 31)).count("1")
                    eb += bin(((b >> (sh + 10)) & 31) ^ ((b2 >> (sh + 10)) & 31)).count("1")
    return flips / n, ea / n, eb / n


def resid(n, ty):
    F = pr["F_w"][ty]
    bus = W(bits(n), pr["a_fj_per_bus_bit"][ty], ty)
    return e["items"][n]["D"]["mean"] - F - bus, F, bus


print("\nC2. ITEM 2 STAYS OPEN: THE RESIDUAL OVER THE CLOCKED LANE PLUS THE BUS PRICE DOES NOT SCALE")
E93T = os.path.join(K, "e93", "tiles")
print("   tile: D - F - a x bus; product-sign flips per lane-cycle; A, B exponent bits per lane-cycle")
for n, ty in (("fp32.a_nz_b_randn", "fp32"), ("fp16.a_nz_b_randn", "fp16"), ("fp16.a_randn_b_nz", "fp16"), ("fp32.a_randn_b_nz", "fp32"),
              ("fp32.a_dnr_b_randn", "fp32"), ("fp16.a_dnr_b_randn", "fp16")):
    r, F, b = resid(n, ty)
    f, ea, eb = rates(os.path.join(E93T, ty, n.split(".")[1] + ".bin"), ty == "fp16")
    print(f"   {n:22s} {e['items'][n]['D']['mean']:.3f} - {F:.3f} - {b:.3f} = {r:.3f} W; flips {f:.3f}; exponent bits A {ea:.3f}, B {eb:.3f}")
f, ea, eb = rates(os.path.join(K, "..", "rpath", "tiles", "fp32", "s_abs.bin"), False)
print(f"   E88 fp32.s_abs: sign cost {pr['sign_frozen_w']:.3f} W; flips {f:.3f}; exponent bits A {ea:.3f}, B {eb:.3f}")
t = reg["tiles"]["fp32.a_nz_b_randn"]
print(f"   fp32.a_nz_b_randn reads {e['items']['fp32.a_nz_b_randn']['D']['mean'] - t['arm_high_w']:+.3f} W from its high arm {t['arm_high_w']} W, which already holds the sign price")

# ------------------------------------------------------------------ C3
print("\nC3. R5's SHORTFALL")
pa, pb = reg["tiles"]["fp32.a_randn_b_nz"]["point_w"], reg["tiles"]["fp32.a_nz_b_randn"]["point_w"]
da, db = e["items"]["fp32.a_randn_b_nz"]["D"]["mean"], e["items"]["fp32.a_nz_b_randn"]["D"]["mean"]
print(f"   predicted contrast {pa:.3f} - {pb:.3f} = {pa - pb:.3f} W; measured {pm(per('fp32.a_randn_b_nz', 'fp32.a_nz_b_randn'))} W; shortfall {pa - pb - (da - db):.3f} W")
print(f"   of it: a_nz_b_randn above its point {db - pb:+.3f} W; a_randn_b_nz below its point {pa - da:+.3f} W")
print(f"   the registered failure readings: {[x for x in reg['rules'] if x['id'] == 'R5-fp32'][0]['failure_means']}")
r1, F1, b1 = resid("fp32.a_randn_b_nz", "fp32")
r2, _, _ = resid("fp32.a_nz_b_randn", "fp32")
print(f"   a_randn_b_nz over F + bus: {r1:.3f} W against {W(t93['tiles']['fp32.a_randn_b_nz']['booth_pp_bits_per_op'], ppj, 'fp32'):.3f} W priced for its partial products")
print(f"   fp32 what the bus price leaves: {r1:.3f} - {r2:.3f} = {r1 - r2:+.3f} W")
q1, _, q1b = resid("fp16.a_randn_b_nz", "fp16")
q2, _, q2b = resid("fp16.a_nz_b_randn", "fp16")
print(f"   fp16: measured {pm(per('fp16.a_randn_b_nz', 'fp16.a_nz_b_randn'))} W; E88's bus price alone gives {q1b - q2b:+.3f} W; residuals {q1:.3f} and {q2:.3f} W, leaving {q1 - q2:+.3f} W")

# ------------------------------------------------------------------ C4
print("\nC4. A ZERO THE GATE SEES IS ALMOST FREE, NOT FREE (D over the type's all-zero level)")
print(f"   E93 fp32.a_zeros_b_randn {pm(per('fp32.a_zeros_b_randn'), 2)} W; int8.a_zeros_b_full {pm(per('int8.a_zeros_b_full'), 2)} W")
for n in ("fp32.a_randn_b_zeros", "fp16.a_zeros_b_randn", "fp16.a_randn_b_zeros", "int8.a_full_b_zeros", "int8.a_zeros_b_full"):
    print(f"   E82 {n} {e82['items'][n]['D']['mean']:.2f} +- {e82['items'][n]['D']['ci95']:.2f} W")
print(f"   against random data: fp32.randn {pm(per('fp32.randn'), 2)}, int8.full {pm(per('int8.full'), 2)} W")
print(f"   gated units in the half-gated tile (reported, assuming half of int8.full is the data units'): {s['reported']['int8_unit_costs_w']['gated']['mean']:.2f} +- {s['reported']['int8_unit_costs_w']['gated']['ci95']:.2f} W")

# ------------------------------------------------------------------ C5
print("\nC5. EACH FORMAT'S OWN PREDICTION FOR THE ONE-SIDED CONTRAST (a_randn_b_nz - a_nz_b_randn)")
for ty in ("fp32", "fp16"):
    x, y = reg["tiles"][f"{ty}.a_randn_b_nz"], reg["tiles"][f"{ty}.a_nz_b_randn"]
    print(f"   {ty}: point {x['point_w'] - y['point_w']:+.2f} W; no sign cost {x['arm_low_w'] - y['arm_low_w']:+.2f} W, sign cost on both {x['arm_high_w'] - y['arm_high_w']:+.2f} W; "
          f"measured {pm(per(f'{ty}.a_randn_b_nz', f'{ty}.a_nz_b_randn'))} W; scored: {'yes (R5-fp32)' if ty == 'fp32' else 'no'}")

# ------------------------------------------------------------------ C6
print("\nC6. THE MASKED TILE")
ma, mb = words(os.path.join(E93T, "fp32", "sparse50_mask.bin"))
sa, sb = words(os.path.join(K, "tiles", "fp32", "sparse50.bin"))
nA = sum(1 for r in sa for w in r if w == 0)
nB = sum(1 for r in sb for w in r if w == 0)
mA = sum(1 for r in ma for w in r if w == 0x80000000)
mB = sum(1 for r in mb for w in r if w == 0x80000000)
print(f"   zero words given -0.0: A {mA} of {nA}, B {mB} of {nB}: {100 * (mA + mB) / (nA + nB):.0f}% over both operands")
print(f"   gate share {kinds['kinds']['fp32']['sparse50']['stats']['gated_lane_frac']:.3f} -> {t93['tiles']['fp32.sparse50_mask']['stats']['gated_lane_frac']:.3f}")
for key in ("D", "S"):
    x, y = e["items"]["fp32.sparse50"][key], e["items"]["fp32.sparse50_mask"][key]
    print(f"   {key}: {x['mean']:.2f} +- {x['ci95']:.2f} -> {y['mean']:.2f} +- {y['ci95']:.2f} W, {y['mean'] / x['mean']:.2f}x")

# ------------------------------------------------------------------ C7
print("\nC7. fp16's R4 BASELINE")
for rid in ("R4-fp32-both", "R4-fp16-both"):
    r = [x for x in reg["rules"] if x["id"] == rid][0]
    print(f"   {rid}: {r['a']} - {r['b']}: {R[rid]['contrast']['mean']:.3f} +- {R[rid]['contrast']['ci95']:.3f} W")
print(f"   fp16 tiles with a constant denormal in E93: {[n for n in t93['tiles'] if n.startswith('fp16.dn1')]}")

# ------------------------------------------------------------------ C8
print("\nC8. THE BANDS AND THE LAW'S RESIDUAL")
print(f"   int8.b_pairs_rtl's reference (predictions-e93.json): {reg['tiles']['int8.b_pairs_rtl']['reference']}")
print(f"   int8.b_pairs_rtl: read {e['items']['int8.b_pairs_rtl']['D']['mean']:.3f} W, point {reg['tiles']['int8.b_pairs_rtl']['point_w']:.3f} W, residual {e['items']['int8.b_pairs_rtl']['D']['mean'] - reg['tiles']['int8.b_pairs_rtl']['point_w']:+.3f} W")
g = kinds["kinds"]["int8"]["wsparse50"]["stats"]["gated_lane_frac"]
fu = e82["items"]["int8.full"]["D"]["mean"]
ga = (e82["items"]["int8.a_full_b_zeros"]["D"]["mean"] + e82["items"]["int8.a_zeros_b_full"]["D"]["mean"]) / 2
w = e82["items"]["int8.wsparse50"]["D"]
print(f"   E82 int8.wsparse50: gated {g:.4f}; law {1 - g:.4f} x {fu:.3f} + {g:.4f} x {ga:.3f} = {(1 - g) * fu + g * ga:.3f} W; read {w['mean']:.3f} +- {w['ci95']:.3f} W; residual {w['mean'] - ((1 - g) * fu + g * ga):+.3f} +- {w['ci95']:.3f} W (the kind's own interval)")

# ------------------------------------------------------------------ C9
print("\nC9. gated_lane_frac_alt_grouping: STOP QUOTING IT; kinds.json STAYS PINNED AND UNCHANGED")
pin = []
for f in sorted(glob.glob(os.path.join(K, "reduce_e*.py"))):
    txt = open(f).read()
    if "kinds.json" in txt and "refusing to reduce" in txt:
        pin.append(os.path.basename(f))
print(f"   reducers that refuse a changed kinds.json: {pin}")
print(f"   kinds.json occurrences of the field: {open(os.path.join(K, 'kinds.json')).read().count('gated_lane_frac_alt_grouping')}")
for rel in glob.glob(os.path.join(K, "real*", "real*.json")):
    c = open(rel).read().count("gated_lane_frac_alt_grouping")
    if c:
        print(f"   {os.path.relpath(rel, ROOT)}: {c}")
hlp = open(os.path.join(K, "..", "hlp", "README.md")).read().splitlines()
print(f"   hlp/README.md:274: {hlp[273][:88]}...")
print(f"   hlp/README.md:276: {hlp[275][:110]}")
rtl = open(os.path.join(ROOT, "docs", "reports", "data", "2026-10-31-q130-rtl-formats", "README.md")).read().splitlines()
print(f"   q130-rtl-formats/README.md:146: {rtl[145][:88]}")

# ------------------------------------------------------------------ C10
print("\nC10. WHAT THE THREE int8 TILES CAN AND CANNOT PICK")
Z = t93["int8_zero_columns"]
# the zero columns as the committed tiles hold them, line by line
sets = {}
for kind in ("b_pairs_rtl", "b_pairs_alt", "b_unpaired"):
    _, b = words(os.path.join(E93T, "int8", kind + ".bin"))
    sets[kind] = [frozenset(j for j in range(16) if b[p][j] == 0) for p in range(16)]
    assert sets[kind][0] == frozenset(Z[kind])


def share(pairs, kind):
    tot = 0
    for p in range(16):
        tot += sum(1 for x, y in pairs if x in sets[kind][p] and y in sets[kind][p])
    return tot / (16 * 8)


def matchings(cols, want):
    """Perfect matchings of `cols` keeping the pattern `want`: same side of the even-line zero set for b_pairs_rtl, opposite
    sides for the other two (a share of 0.5 needs every pair inside one side; a share of 0 needs every pair across)."""
    if not cols:
        yield []
        return
    a = cols[0]
    for i in range(1, len(cols)):
        b = cols[i]
        if ((a in want["b_pairs_rtl"]) == (b in want["b_pairs_rtl"])
                and (a in want["b_pairs_alt"]) != (b in want["b_pairs_alt"])
                and (a in want["b_unpaired"]) != (b in want["b_unpaired"])):
            for rest in matchings(cols[1:i] + cols[i + 1:], want):
                yield [(a, b)] + rest


want = {k: sets[k][0] for k in sets}
ok = list(matchings(list(range(16)), want))
total = 1
for x in range(15, 0, -2):
    total *= x
print(f"   perfect pairings of 16 columns: 15!! = {total:,}; those giving (b_pairs_rtl, b_pairs_alt, b_unpaired) = (0.5, 0, 0): {len(ok)}")
assert all(share(m, "b_pairs_rtl") == 0.5 and share(m, "b_pairs_alt") == 0 and share(m, "b_unpaired") == 0 for m in ok)
RTLP = [(l, l + 8) for l in range(8)]
print(f"   the RTL's (l, l+8) among them: {any(sorted(m) == RTLP for m in ok)}")
for name, m in (("(l, l+8)", RTLP), ("(2l, 2l+1)", [(2 * l, 2 * l + 1) for l in range(8)]),
                ("(l, l+2)", [(0, 2), (1, 3), (4, 6), (5, 7), (8, 10), (9, 11), (12, 14), (13, 15)]),
                ("(l, l+4)", [(0, 4), (1, 5), (2, 6), (3, 7), (8, 12), (9, 13), (10, 14), (11, 15)]),
                ("(l, 15-l)", [(l, 15 - l) for l in range(8)]),
                ("(l, 14-l), 7 with 15", [(l, 14 - l) for l in range(7)] + [(7, 15)])):
    print(f"   {name:22s} shares (rtl, alt, unpaired) = ({share(m, 'b_pairs_rtl'):.3f}, {share(m, 'b_pairs_alt'):.3f}, {share(m, 'b_unpaired'):.3f})")
print("   measured D, W: " + ", ".join(f"{k} {e['items']['int8.' + k]['D']['mean']:.3f} +- {e['items']['int8.' + k]['D']['ci95']:.3f}" for k in sets))

# ------------------------------------------------------------------ C11
print("\nC11. SMALL THINGS")
_, fb = words(os.path.join(K, "tiles", "int8", "full.bin"))
_, zb = words(os.path.join(K, "tiles", "int8", "a_zeros_b_full.bin"))
_, tb = words(os.path.join(E93T, "int8", "a_3of4_b_full.bin"))
print(f"   int8.full's B equals a_3of4_b_full's: {fb == tb}; a_zeros_b_full's B equals a_3of4_b_full's: {zb == tb}")
print(f"   R2-fp32: {R['R2-fp32']['contrast']['mean']:.3f} +- {R['R2-fp32']['contrast']['ci95']:.3f} W, inside the registered +-1.0 W, its interval just excluding 0")
TZ = datetime.timezone(datetime.timedelta(hours=-7))
b = load(HERE, "aifoundry1-c1", "kinds", "kinds-smoke-p9301", "block.json")
b2 = load(HERE, "aifoundry1-c1", "kinds", "p9314", "block.json")
print(f"   first block t0 {datetime.datetime.fromtimestamp(b['t0_ms'] / 1000, TZ).strftime('%H:%M:%S.%f')[:-3]} PDT; last block t1 {datetime.datetime.fromtimestamp(b2['t1_ms'] / 1000, TZ).strftime('%H:%M:%S.%f')[:-3]} PDT; {(b2['t1_ms'] - b['t0_ms']) / 60000:.1f} min")
SF = 1566349187598000201
print(f"   the claim's Discord id decodes to {datetime.datetime.fromtimestamp(((SF >> 22) + 1420070400000) / 1000, TZ).strftime('%H:%M:%S.%f')[:-3]} PDT")
print("   d470f6a9's push by origin/main's reflog on the Intel's clone: 00:11:18 PDT (not in the repository; `git reflog show origin/main`)")
