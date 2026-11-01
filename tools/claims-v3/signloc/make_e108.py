#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E108 (Q133, the kinds page's section 11 item 5): a random sign's ~5 W located further. The tiles and the expected accumulators. Desk compute only;
nothing here opens a card. The registration is tools/claims-v3/signloc/E108.md.

    python3 tools/claims-v3/signloc/make_e108.py            # writes e108/tiles/<type>/<kind>.bin and e108/e108.json
    python3 tools/claims-v3/signloc/make_e108.py --check    # rebuilds in memory, compares with disk
    python3 tools/claims-v3/signloc/make_e108.py --search   # reruns the seeded search that chose c_mx's draw, and prints its ranking

THE REST. On one card a random +-1 costs about 4.8 W more than all +1 in both formats (E106). A held tile, whose sum the read-back shows holding, keeps a
share of it that depends on the tile; the rest is by subtraction and not located. E88's s_walk and s_abs have the same signs at k >= 1 and differ only in
the k = 0 slice: s_walk's sums walk, s_abs's are absorbed (2^100). Their difference, E88's R32s (2.26 W on card 1), is the rest with the draws matched.
What s_walk has that s_abs lacks: (1) its 256 accumulators differ from each other, so a lane that alternates between C[i][l] and C[i][l+8] and moves
from row to row reads, adds and writes back a different word every micro-op (E88's R32bus: 3.80 W for random positive sums); (2) its sums change
(store bits, carries, the aligned product not zapped).

THE NEW fp32 TILES. Every one keeps s_abs's random signs at k >= 1 (E88's draw, seed 8802) on the side it names and changes the k = 0 slice or one side:
  axis b, A against B sign (the other side all +1)
    b_A_f    A = s_abs's A at k >= 1, B = +1; k = 0 (2^50, 2^50): absorbed, C = n 2^100 everywhere; eff_sub follows A's sign (it changes at a row boundary only)
    b_B_f    A = +1, B = s_abs's B at k >= 1; the same k = 0: absorbed, C = n 2^100; eff_sub follows B's sign (it can change every micro-op)
    b_A_w    b_A_f with k = 0 (1, 1): walks, C[i][j] = n (1 + sum_k A[i][k]), one value a row
    b_B_w    b_B_f with k = 0 (1, 1): walks, C[i][j] = n (1 + sum_k B[k][j]), one value a column
    b_B_z    E104's z_s (A = -0 at k >= 1, s_abs's B) with k = 0 (1, Q_j), Q_j = 1 + sum_k B[k][j] (-0 where Q_j = 0, so no word is raw zero): zero
             products, so C holds n Q_j, b_B_w's sums at every op's end, with b_B_w's B stream; the walk within an op and the nonzero products are all
             that b_B_w adds, and z_s's equal sums (n 2^100) are all it lacks
  axis c, the accumulators exponent-aligned against misaligned, frozen by E88's absorption (s_abs's signs on both sides at k >= 1)
    c_sg_f   k = 0 (2^50 s_i, 2^50 t_j): C = s_i t_j n 2^100, one exponent; the lane's C words differ in sign only
    c_ex_f   k = 0 (2^50 s_i 2^e_i, 2^50 t_j 2^f_j): C = s_i t_j 2^(e_i + f_j) n 2^100; sign and exponent differ, the mantissa is n's in every word
    c_mx_f   k = 0 (2^50 s_i a_i, 2^50 t_j b_j), a_i in {1, 3}, b_j in {1..10}: C = s_i t_j a_i b_j n 2^100; sign, exponent and mantissa differ, and the lane's
             C words toggle as many bits an op as s_walk's (34,088 against 34,033, averaged over eight op indices across a launch), chosen by a seeded
             search (--search)
    e_i = floor(log2 a_i), f_j = floor(log2 b_j): c_sg_f, c_ex_f and c_mx_f are nested, and s_walk is the walking end of the ladder. An exponent-aligned
    walking tile with random signs cannot be built exactly: 15 random +-1 on a seed keep every sum inside one binade only with a seed above 45, and then
    the sums pass 2^24 inside a launch (48 x 542,000 = 26 M), where +-1 rounds.
  Every product at k >= 1 is +-1, absorbed in the _f tiles (2^100 n against 1: below half an ulp) and exact in the _w tiles (|C| <= 16 n < 2^24).

REUSED BYTE FOR BYTE (REUSED below): the like for like E106 named - fp32's and fp16's z_s (E104) beside signs, ones and c_abs, with E106's fp32.s_abs and
fp16.z_ss; E88's s_walk; axis a, product-sign alternation against operand sign changes at a fixed product sign - E92's fp32.h_add and h_sub (frozen) and
w_h_add, E104's m_h_sub (walking, w_h_add's magnitudes) in fp32, and E104's fp16 w_h_add and m_h_sub. fp16 has no frozen pair by absorption: its absorbed
subtractions walk (E104), so its alternation pair is walking only.

THE COUNTS. `real` from accum.c (the RTL's arithmetic: fp32 FMA in RNE, fp16 fp16_model), `manual` (the manual's sentence; equal to accum.c in fp32) and
`fl` (C = fl(n S)), written for every read-back length; they coincide on every tile here, so a read-back miss means the tile is not what it is called.
`dp_counts` (make_e104): eff_sub alternations, the lane's C read and result words, the store bits, from the real accumulators at two op indices.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KINDS)
import make_e104 as e  # noqa: E402

me, m90, mk = e.me, e.m90, e.mk
OUT = os.path.join(HERE, "e108")
ROOT = e.ROOT
SEED = 10800
H = 2.0 ** 50
READS = (2, 1000, 199874, 541999)
# E104's moving tiles reach 2^24 (fp32, 31 n) and 2^25 (fp16, 62 n) at op 541,200: E104 read them at 500,000, and so does E108.
READ_MOVING = (1000, 199874, 500000)
MOVING = ("fp32.w_h_add", "fp32.m_h_sub", "fp16.w_h_add", "fp16.m_h_sub")
# the search that chose c_mx's draw: default_rng(10800), 4000 draws of (s, t, a, b); the lane's C-read bits an op are averaged over eight op indices across a
# launch (SEARCH_NS: n x a b's low bits depend on n, so one round n would mislead); among the draws whose c_mx count lies within 0.2% of s_walk's (computed
# the same way, exactly, from s_walk's integer sums), the one whose c_sg count is nearest 2,048 (half the lane's micro-ops change C's sign), then the first
SEARCH_DRAWS = 4000
SEARCH_NS = tuple(50001 + 61000 * j for j in range(8))
SEARCH_TOL = 0.002
CHOSEN_DRAW = 290

NEW = ("fp32.b_A_f", "fp32.b_B_f", "fp32.b_A_w", "fp32.b_B_w", "fp32.b_B_z", "fp32.c_sg_f", "fp32.c_ex_f", "fp32.c_mx_f")
REUSED = {
    "fp32.ones": "tools/claims-v3/kinds/tiles/", "fp16.ones": "tools/claims-v3/kinds/tiles/",
    "fp32.signs": "tools/claims-v3/kinds/e92/tiles/", "fp16.signs": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.c_abs": "tools/claims-v3/kinds/e92/tiles/", "fp16.c_abs": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.s_abs": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.z_s": "tools/claims-v3/kinds/e104/tiles/", "fp16.z_s": "tools/claims-v3/kinds/e104/tiles/",
    "fp16.z_ss": "tools/claims-v3/kinds/e106/tiles/",
    "fp32.s_walk": "tools/claims-v3/rpath/tiles/",
    "fp32.h_add": "tools/claims-v3/kinds/e92/tiles/", "fp32.h_sub": "tools/claims-v3/kinds/e92/tiles/",
    "fp32.w_h_add": "tools/claims-v3/kinds/e92/tiles/", "fp32.m_h_sub": "tools/claims-v3/kinds/e104/tiles/",
    "fp16.w_h_add": "tools/claims-v3/kinds/e104/tiles/", "fp16.m_h_sub": "tools/claims-v3/kinds/e104/tiles/",
}
# beside the tiles, once a pass, as E106 ran them: E78's fp32.ones and fp16.ones (e108_common.COMPARE); every other tile is in POWER
COMPARE = ("fp32.ones", "fp16.ones")
POWER = tuple(sorted([n for n in NEW] + [n for n in REUSED if n not in COMPARE]))
SMOKE = ("anchor_pi", "fp32.c_mx_f", "fp32.b_B_w", "fp32.s_walk", "fp32.zeros", "fp32.randn", "fp16.z_s", "fp16.zeros")
GROUPS = {
    "fp32.ones": "the +1 side of the step", "fp16.ones": "the +1 side of the step", "fp32.signs": "the +-1 side of the step", "fp16.signs": "the +-1 side of the step",
    "fp32.c_abs": "held baseline", "fp16.c_abs": "held baseline", "fp32.z_s": "held, zero products, B's signs", "fp16.z_s": "held, zero products, B's signs",
    "fp32.s_abs": "held, absorbed, both signs", "fp16.z_ss": "held, zero products, both signs",
    "fp32.s_walk": "s_abs walking", "fp32.b_A_f": "A's signs, held", "fp32.b_B_f": "B's signs, held", "fp32.b_A_w": "A's signs, walking", "fp32.b_B_w": "B's signs, walking",
    "fp32.b_B_z": "B's signs, zero products, held at b_B_w's sums",
    "fp32.c_sg_f": "held, C differs in sign", "fp32.c_ex_f": "held, C differs in sign and exponent", "fp32.c_mx_f": "held, C differs as s_walk's does",
    "fp32.h_add": "fixed product sign, held", "fp32.h_sub": "product sign alternating, held", "fp32.w_h_add": "fixed product sign, walking",
    "fp32.m_h_sub": "product sign alternating, walking", "fp16.w_h_add": "fixed product sign, walking", "fp16.m_h_sub": "product sign alternating, walking",
}


def read_lengths(name):
    return READ_MOVING if name in MOVING else READS


def s_abs_signs():
    """E88's random +-1 at k >= 1 (seed 8802), read from s_abs's bytes: A[i][k], B[k][j] as float32 grids (k = 0 is s_abs's 2^50, replaced by every user)."""
    aw, bw = me.words_from_tile(open(os.path.join(ROOT, "tools/claims-v3/rpath/tiles/fp32/s_abs.bin"), "rb").read())
    A = aw.view(np.float32).astype(np.float64)
    B = bw.view(np.float32).astype(np.float64)
    assert np.all(A[:, 0] == H) and np.all(B[0, :] == H)
    assert np.all(np.abs(A[:, 1:]) == 1.0) and np.all(np.abs(B[1:, :]) == 1.0)
    return A, B


def draw(rng):
    s = np.where(rng.random(16) < 0.5, -1.0, 1.0)
    t = np.where(rng.random(16) < 0.5, -1.0, 1.0)
    a = rng.choice([1.0, 3.0], 16)
    b = rng.choice([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 16)
    return s, t, a, b


def popc(x):
    x = np.asarray(x, dtype=np.uint64)
    c = np.zeros_like(x)
    for _ in range(32):
        c += x & np.uint64(1)
        x = x >> np.uint64(1)
    return c


def cbus_frozen(val, ns=e.DP_NS):
    """The lane's C-read bits an op for a frozen tile whose C[i][j] = val[i][j] n 2^100 exactly: for k, for i, for h, lane l reads C[i][8h+l]."""
    tot = 0.0
    for n in ns:
        W = np.asarray(val * float(n) * 2.0 ** 100, dtype=np.float32).view(np.uint32)
        seq = np.array([W[i, 8 * h: 8 * h + 8] for i in range(16) for h in range(2)])
        tot += float(popc(seq ^ np.roll(seq, 1, axis=0)).sum()) * 16
    return tot / len(ns)


def ladder(s, t, a, b):
    mx = np.outer(s * a, t * b)
    ex = np.outer(s * 2.0 ** np.floor(np.log2(a)), t * 2.0 ** np.floor(np.log2(b)))
    sg = np.outer(s, t)
    return sg, ex, mx


def seq_reads(Cfun):
    """The lane's C reads of one fp32 op in issue order (for k, for i, for h): an array [512, 8]; Cfun(k) is C before slot k's product."""
    return np.array([Cfun(k)[i, 8 * h: 8 * h + 8] for k in range(16) for i in range(16) for h in range(2)])


def cbus_walk(A, B, ns=SEARCH_NS):
    """The lane's C-read bits an op for a walking fp32 tile with exact integer sums (s_walk's), from the sums themselves."""
    P = np.einsum("ik,kj->kij", A, B)
    S = P.sum(axis=0)
    cum = np.cumsum(P, axis=0)
    tot = 0.0
    for n in ns:
        W = seq_reads(lambda k: ((n - 1) * S + (cum[k - 1] if k > 0 else 0)).astype(np.float32)).view(np.uint32)
        tot += float(popc(W ^ np.roll(W, 1, axis=0)).sum())
    return tot / len(ns)


def target_cbus():
    aw, bw = me.words_from_tile(open(os.path.join(ROOT, "tools/claims-v3/rpath/tiles/fp32/s_walk.bin"), "rb").read())
    return cbus_walk(aw.view(np.float32).astype(np.float64), bw.view(np.float32).astype(np.float64))


def chosen_draw():
    rng = np.random.default_rng(SEED)
    for _ in range(CHOSEN_DRAW):
        draw(rng)
    return draw(rng)


def search():
    tgt = target_cbus()
    rng = np.random.default_rng(SEED)
    rows = []
    for trial in range(SEARCH_DRAWS):
        sg, ex, mx = ladder(*draw(rng))
        cm, ce, cs = cbus_frozen(mx, SEARCH_NS), cbus_frozen(ex, SEARCH_NS), cbus_frozen(sg, SEARCH_NS)
        rows.append((abs(cm - tgt) > SEARCH_TOL * tgt, abs(cs - 2048), trial, cm, ce, cs))
    rows.sort()
    print(f"s_walk's lane C-read bits an op over {len(SEARCH_NS)} op indices: {tgt:.1f}")
    for r in rows[:8]:
        print(f"draw {r[2]:5d}  c_mx {r[3]:8.0f}  c_ex {r[4]:7.0f}  c_sg {r[5]:6.0f}  {'outside' if r[0] else 'inside'} 0.2%")
    return rows[0][2]


def new_designs():
    A, B = s_abs_signs()
    out = {}

    def tile(a_k0, b_k0, AA, BB, rule):
        AA = np.array(AA, dtype=np.float64)
        BB = np.array(BB, dtype=np.float64)
        AA[:, 0] = a_k0
        BB[0, :] = b_k0
        wa, wb = me.f32w(AA.astype(np.float32)), me.f32w(BB.astype(np.float32))
        assert np.all(wa != 0) and np.all(wb != 0)       # no raw-zero word: the zero gate compares raw words (E93), so -0 keeps a lane on
        return wa, wb, rule

    one = np.ones((16, 16))
    out["fp32.b_A_f"] = tile(H, H, A, one, "A = s_abs's A at k>=1 (E88's random +-1, seed 8802), B = +1 at k>=1; k=0 (2^50, 2^50): every product absorbed, C = n 2^100; eff_sub follows A's sign")
    out["fp32.b_B_f"] = tile(H, H, one, B, "A = +1 at k>=1, B = s_abs's B at k>=1; k=0 (2^50, 2^50): every product absorbed, C = n 2^100; eff_sub follows B's sign")
    out["fp32.b_A_w"] = tile(1.0, 1.0, A, one, "b_A_f with k=0 (1, 1): C[i][j] = n (1 + sum_k>=1 A[i][k]), exact, one value a row")
    out["fp32.b_B_w"] = tile(1.0, 1.0, one, B, "b_B_f with k=0 (1, 1): C[i][j] = n (1 + sum_k>=1 B[k][j]), exact, one value a column")
    Q = 1.0 + B[1:, :].sum(axis=0)
    q0 = np.where(Q == 0, -0.0, Q)
    az = np.full((16, 16), -0.0)
    out["fp32.b_B_z"] = tile(1.0, q0, az, B, "E104's z_s (A = -0 at k>=1, s_abs's B at k>=1) with k=0 (1, Q_j), Q_j = 1 + sum_k>=1 B[k][j] (-0 where Q_j = 0): zero products hold C = n Q_j, b_B_w's sums at every op's end")
    s, t, a, b = chosen_draw()
    e_ = 2.0 ** np.floor(np.log2(a))
    f_ = 2.0 ** np.floor(np.log2(b))
    tag = f"default_rng({SEED}) draw {CHOSEN_DRAW} (make_e108.py --search)"
    out["fp32.c_sg_f"] = tile(H * s, H * t, A, B, f"s_abs's signs at k>=1; k=0 (2^50 s_i, 2^50 t_j), s, t random signs ({tag}): C = s_i t_j n 2^100, one exponent")
    out["fp32.c_ex_f"] = tile(H * s * e_, H * t * f_, A, B, f"s_abs's signs at k>=1; k=0 (2^50 s_i 2^e_i, 2^50 t_j 2^f_j), e_i = floor(log2 a_i), f_j = floor(log2 b_j) ({tag}): C = s t 2^(e+f) n 2^100")
    out["fp32.c_mx_f"] = tile(H * s * a, H * t * b, A, B, f"s_abs's signs at k>=1; k=0 (2^50 s_i a_i, 2^50 t_j b_j), a in {{1, 3}}, b in {{1..10}} ({tag}): C = s t a b n 2^100, the lane's C words toggle as s_walk's do")
    meta = {"s": s.tolist(), "t": t.tolist(), "a": a.tolist(), "b": b.tolist(), "draw": CHOSEN_DRAW, "seed": SEED, "search_draws": SEARCH_DRAWS, "search_ns": list(SEARCH_NS),
            "search_tol": SEARCH_TOL, "cbus_at_search_ns": {"c_sg_f": cbus_frozen(np.outer(s, t), SEARCH_NS), "c_ex_f": cbus_frozen(np.outer(s * e_, t * f_), SEARCH_NS),
                                                         "c_mx_f": cbus_frozen(np.outer(s * a, t * b), SEARCH_NS), "s_walk": target_cbus()}}
    return out, meta


def expected_c(name, ty, raw, n):
    """What the design says C holds after n ops, for the new tiles (the rule, independent of accum.c)."""
    aw, bw = me.words_from_tile(raw)
    A = aw.view(np.float32).astype(np.float64)
    B = bw.view(np.float32).astype(np.float64)
    if name.endswith(("_f", "_z")):
        return np.asarray(np.outer(A[:, 0], B[0, :]) * n, dtype=np.float32).view(np.uint32).reshape(256)
    return np.asarray((A @ B) * n, dtype=np.float32).view(np.uint32).reshape(256)


def build():
    accum = e.accum_binary()
    spec = {"experiment": "E108", "date": "2026-11-01", "generator": "tools/claims-v3/signloc/make_e108.py", "power": list(POWER), "compare": list(COMPARE), "smoke": list(SMOKE),
            "readback": {}, "tiles": {}, "reused_from": {}, "groups": GROUPS}
    new, meta = new_designs()
    spec["c_draw"] = meta
    names = [(n, "new") for n in NEW] + [(n, "reused") for n in REUSED]
    raws, rules = {}, {}
    for name, how in names:
        ty, kind = name.split(".")
        if how == "new":
            aw, bw, rule = new[name]
            raws[name] = me.tile_from_words(aw, bw)
        else:
            raws[name] = open(os.path.join(ROOT, REUSED[name], ty, kind + ".bin"), "rb").read()
            rule = f"{REUSED[name]}{ty}/{kind}.bin, byte for byte"
            spec["reused_from"][name] = REUSED[name] + f"{ty}/{kind}.bin"
        rules[name] = rule
    lens = {n: read_lengths(n) for n, _ in names}
    with ThreadPoolExecutor(int(os.environ.get("E104_JOBS", "6"))) as ex:
        list(ex.map(lambda nh: e.real_c(nh[0].split(".")[0], raws[nh[0]], tuple(lens[nh[0]]) + tuple(n - 1 for n in e.DP_NS), accum), names))
        list(ex.map(lambda nh: e.manual_c(nh[0].split(".")[0], raws[nh[0]], lens[nh[0]], accum), names))
    problems = []
    for name, how in names:
        ty, kind = name.split(".")
        raw = raws[name]
        st = mk.tile_stats(raw, ty)
        fa, fb = m90.sign_flips_per_op(raw, ty)
        real = e.real_c(ty, raw, lens[name], accum)
        man = e.manual_c(ty, raw, lens[name], accum)
        cnt = e.dp_counts(ty, raw, accum, list(e.DP_NS))
        spec["readback"][name] = list(lens[name])
        ent = {"type": ty, "kind": kind, "how": how, "rule": rules[name], "group": GROUPS[name], "file": f"tiles/{ty}/{kind}.bin", "bytes": len(raw), "sha256": e.sha(raw),
               "sha256_a": e.sha(raw[:1024]), "sha256_b": e.sha(raw[1024:]),
               "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"], "sign_flips_per_op_a": fa, "sign_flips_per_op_b": fb},
               "counts_real": cnt, "read": {}}
        for n, v in real.items():
            f = e.fl_c(ty, raw, n)
            mv = man[n]
            ent["read"][str(n)] = {"rtl_hex": v.tobytes().hex(), "fl_hex": f.tobytes().hex(), "manual_hex": mv.tobytes().hex(), "words_rtl_vs_fl": int((v != f).sum()),
                                   "words_rtl_vs_manual": int((v != mv).sum()), "words_fl_vs_manual": int((f != mv).sum()),
                                   "distinct": {"rtl": len(set(v.tolist())), "fl": len(set(f.tolist())), "manual": len(set(mv.tolist()))},
                                   "c00": {"rtl": f"{int(v[0]):08x}", "fl": f"{int(f[0]):08x}", "manual": f"{int(mv[0]):08x}"}, "c08": {"rtl": f"{int(v[8]):08x}", "fl": f"{int(f[8]):08x}", "manual": f"{int(mv[8]):08x}"}}
            if int((v != f).sum()) or int((v != mv).sum()):
                problems.append(f"{name} n={n}: rtl!=fl {int((v != f).sum())}, rtl!=manual {int((v != mv).sum())}")
            if how == "new":
                want = expected_c(name, ty, raw, n)
                if not np.array_equal(v.view(np.float32), want.view(np.float32)):        # by value: a held +-0 may carry either sign
                    problems.append(f"{name} n={n}: accum.c differs from the design's sum on {int((v.view(np.float32) != want.view(np.float32)).sum())} words")
        spec["tiles"][name] = ent
        r = ent["read"][str(lens[name][-1])]
        print(f"{name:14s} {how:6s} bus {st['bus_bits_per_op']:6d} signflips A {fa:5d} B {fb:5d} alt {cnt['alt1']:6.0f} {cnt['alt2']:6.0f} cbus {cnt['cbus']:7.0f} rbus {cnt['rbus']:7.0f} "
              f"store {cnt['store']:7.0f} chg {cnt['chg']:.3f} words {r['distinct']['rtl']} C00 {r['c00']['rtl']} C08 {r['c08']['rtl']}", flush=True)
    return spec, raws, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--search", action="store_true")
    a = ap.parse_args()
    if a.search:
        best = search()
        print("chosen:", best, "registered:", CHOSEN_DRAW)
        sys.exit(0 if best == CHOSEN_DRAW else 1)
    spec, raws, problems = build()
    if a.check:
        bad = [n for n, r in raws.items() if open(os.path.join(OUT, spec["tiles"][n]["file"]), "rb").read() != r]
        old = json.load(open(os.path.join(OUT, "e108.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            bad.append("e108.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(raws), "problems": bad, "readings_differ": problems}))
        sys.exit(1 if bad or problems else 0)
    for name, raw in raws.items():
        p = os.path.join(OUT, spec["tiles"][name]["file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "wb").write(raw)
    json.dump(spec, open(os.path.join(OUT, "e108.json"), "w"), indent=1)
    print(json.dumps({"tiles": len(raws), "readings_differ": problems}))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
