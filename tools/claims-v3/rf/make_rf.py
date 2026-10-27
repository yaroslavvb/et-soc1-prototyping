#!/usr/bin/env python3
"""V3-RF (E74, the register-file cell ladder): writes every operand file the experiment runs, and its designed counts.

    python3 tools/claims-v3/rf/make_rf.py <out-dir>           # srcs/, tiles/, manifest.json
    python3 tools/claims-v3/rf/make_rf.py <out-dir> --check   # also re-derive every count from the files on disk
    python3 tools/claims-v3/rf/make_rf.py --grid              # print the reachable (C, k, W) grid and stop

The question: **what does one bit stored in a vector register's own cell cost to change?** Every earlier ladder
held the sources still (gen_ops.py: "sources are never overwritten and sinks never read"), so the cell never
flipped and its price was never separated from the read port (E60: 20.83 fJ per read-port bit) or the result path
(31.17 fJ). E61 got at it once, through two kernels (`df.un1a.fnot` vs `df.un1b.fnot`), and put a cell bit at about
0.8 fJ with the two kernels' own difference inside the bar: under-resolved.

This is the same physics as a ladder **in the data alone**, on one kernel, one mode, one build: the instruction
stream of `df.un1b.fnot` is byte-identical across every rung, and only the 256 B operand image changes.

`df.un1b.fnot` (gen_df.py, build with -DENERCAT_DF=ON) is 16 ops per iteration:

    phase 1:  fnot.pi f(8+i), f(i)            i = 0..7
    phase 2:  fnot.pi f(8+((i+3)%8)), f(i)    i = 0..7

With the eight 256-bit source registers S0..S7 loaded once, before the loop, and never written:

  * read ports     see S0,S1,...,S7,S0,S1,...,S7 per iteration -> 2 * sum_j popcount(S_j ^ S_j+1)   = 16 C
  * the result bus sees ~S0,...,~S7,~S0,...,~S7                -> the same count                     = 16 C
  * sink f(8+m)    holds ~S_m after phase 1 and ~S_(m-3 mod 8) after phase 2, and ~S_m again in the
    next iteration, so its **cell** flips 2 * popcount(S_m ^ S_(m-3 mod 8)) per iteration             = 16 k
  * read indices, sink indices and the op count are fixed by the kernel, not by the data.

So an operand set with popcount(S_j ^ S_j+1) = C for every j (held at one value for the whole ladder) and
popcount(S_m ^ S_(m-3 mod 8)) = k for every m (the rung) moves the register file's cells, and nothing else, by
16(k - k') bits per iteration between rungs k and k'. The slope over the rungs is the cell bit's price.

popcount(S_j) = W is held equal for every j and every rung too, so no rung carries more ones than another (a
static or bitline-precharge term cannot masquerade as the slope).

Construction. Bit position p of the 256-bit register is described by the 8-bit indicator v(p): which of the eight
registers have that bit set. Then

    popcount(S_j ^ S_j+d) = sum over p of [ v(p)_j != v(p)_(j+d mod 8) ]

so a multiset of indicators fixes every count exactly. Taking **whole cyclic orbits** of indicators (every
distinct rotation of one 8-bit word, one bit position each) makes all three counts independent of j, and the code
below enumerates the 36 orbits of Z8 on {0,1}^8, tabulates each orbit's (C, k, W) contribution, then searches
integer combinations that fit 256 bit positions. Every number in manifest.json is re-derived from the bytes on
disk by `--check`, never trusted from the construction.

The items (each a 256 B image of f0..f7, in srcs/<name>.bin):

    rf_k<k>      op df.un1b.fnot: the ladder. k bits of stored register content flip per op, C bits on the ports.
    rfz_c<C>     op df.un1a.fnot: the same operands through the kernel whose sinks never change value (16 ops,
                 sink 8+i <- ~S_i twice): ports and result path identical, cells still. A secondary anchor only
                 (a different .text, so E61's loop-address trap applies: compare it to a rung with care).
    anchor_pi    the fma drift anchor every V3 block starts and ends with (run_hl.py's own repeated item).

The ladder's own zero is the FIT, not an item: k = 0 with C > 0 is unreachable (k = 0 forces S_m = S_(m-3) for
every m, and 3 generates Z8, so every S_j would be equal and C would be 0 too).
"""
import argparse
import json
import os
import struct

PI = 0x40490FDB
BITS = 256          # one .pi register: 8 lanes x 32 bits
NREG = 8            # f0..f7
DIST = 3            # un1b's sink rotation: the reuse distance of a cell
SEED = 20261027


def popcount(x):
    return bin(x).count("1")


def rot(v, t):
    """rotate an 8-bit indicator right by t (register j takes bit j of v)"""
    return ((v >> t) | (v << (8 - t))) & 0xFF


def orbit(v):
    return sorted({rot(v, t) for t in range(8)})


def counts(v):
    """(C, k, W) contributed per j by ONE bit position in each member of v's orbit."""
    o = orbit(v)
    c = sum((m >> 0 & 1) != (m >> 1 & 1) for m in o)
    kk = sum((m >> 0 & 1) != (m >> DIST & 1) for m in o)
    w = sum(m & 1 for m in o)
    # j-independence check: every j must give the same three numbers
    for j in range(8):
        assert c == sum((m >> j & 1) != (m >> ((j + 1) % 8) & 1) for m in o), v
        assert kk == sum((m >> j & 1) != (m >> ((j + DIST) % 8) & 1) for m in o), v
        assert w == sum(m >> j & 1 for m in o), v
    return c, kk, w, len(o), o


def orbits():
    seen, out = set(), []
    for v in range(256):
        o = tuple(orbit(v))
        if o in seen:
            continue
        seen.add(o)
        c, kk, w, n, mem = counts(v)
        out.append({"rep": v, "members": mem, "size": n, "c": c, "k": kk, "w": w})
    return out


def build(target_k, target_c, target_w, obs):
    """Pick multiples of whole orbits: sum(size) <= BITS, and the three counts hit their targets exactly.

    Greedy over a tiny search space: at most four orbit families with multiplicities, which is enough because the
    orbits of the all-zero and all-one indicators are free filler that moves only W.
    """
    zero = next(o for o in obs if o["rep"] == 0)        # c=0 k=0 w=0, size 1
    ones = next(o for o in obs if o["rep"] == 0xFF)     # c=0 k=0 w=1, size 1
    movers = [o for o in obs if o["size"] == 8 and (o["c"] or o["k"])]
    movers.sort(key=lambda o: (o["k"], o["c"]))
    best = None
    for a in movers:
        for b in movers:
            for na in range(0, 33):
                for nb in range(0, 33):
                    bits = (na + nb) * 8
                    if bits > BITS:
                        continue
                    c = na * a["c"] + nb * b["c"]
                    k = na * a["k"] + nb * b["k"]
                    if c != target_c or k != target_k:
                        continue
                    w = na * a["w"] + nb * b["w"]
                    rest = BITS - bits
                    # filler: `nf` all-ones positions (w += 1 each) and the remainder all-zero
                    nf = target_w - w
                    if nf < 0 or nf > rest:
                        continue
                    cand = ([(a, na), (b, nb)] if a is not b else [(a, na + nb)]) + [(ones, nf), (zero, rest - nf)]
                    score = (len(movers) - movers.index(a), na + nb)
                    if best is None or score < best[0]:
                        best = (score, cand)
    return None if best is None else best[1]


def words(plan):
    """Turn a plan (orbit, multiplicity) into the eight 256-bit register values, as 8x8 uint32 lanes."""
    pos = 0
    regs = [0] * NREG
    for o, n in plan:
        for _ in range(n):
            for m in o["members"] if o["size"] > 1 else [o["rep"]]:
                if pos >= BITS:
                    raise SystemExit("plan overflows 256 bit positions")
                for j in range(NREG):
                    if (m >> j) & 1:
                        regs[j] |= 1 << pos
                pos += 1
    if pos != BITS:
        raise SystemExit(f"plan fills {pos} of {BITS} bit positions")
    return regs


def img(regs):
    """256 B image of f0..f7: register j is 32 B, little-endian lanes."""
    out = bytearray()
    for j in range(NREG):
        v = regs[j]
        for lane in range(8):
            out += struct.pack("<I", (v >> (32 * lane)) & 0xFFFFFFFF)
    return bytes(out)


def regs_of(blob):
    regs = []
    for j in range(NREG):
        v = 0
        for lane in range(8):
            (w,) = struct.unpack_from("<I", blob, 32 * j + 4 * lane)
            v |= w << (32 * lane)
        regs.append(v)
    return regs


def measure(regs):
    c = [popcount(regs[j] ^ regs[(j + 1) % NREG]) for j in range(NREG)]
    k = [popcount(regs[m] ^ regs[(m - DIST) % NREG]) for m in range(NREG)]
    w = [popcount(regs[j]) for j in range(NREG)]
    return c, k, w


# The registered ladder. C and W are held at these values on every rung; --grid prints what k is reachable there
# (at C = 96, W = 128: every multiple of 8 from 32 to 176, and 192). The rungs span 6x in cell flips.
C_FIX = 96
W_FIX = 128
LADDER = [32, 64, 96, 128, 160, 192]
# The null test: the same operands through df.un1a.fnot, whose cells never change value. Its power must NOT
# depend on k. Three of the six rungs carry it, which keeps the block at 11 runs.
NULLS = [32, 96, 192]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--grid", action="store_true", help="print the reachable (k) values at C_FIX and stop")
    a = ap.parse_args()
    obs = orbits()

    if a.grid:
        rows = []
        for k in range(0, 257, 8):
            rows.append((k, build(k, C_FIX, W_FIX, obs) is not None))
        print(f"C={C_FIX} W={W_FIX}: reachable k = " + ",".join(str(k) for k, ok in rows if ok))
        print(f"orbits: {len(obs)}; of size 8 that move something: {sum(1 for o in obs if o['size'] == 8 and (o['c'] or o['k']))}")
        return

    if not a.out:
        raise SystemExit("need an out-dir (or --grid)")
    out = a.out
    os.makedirs(f"{out}/srcs", exist_ok=True)
    os.makedirs(f"{out}/tiles", exist_ok=True)

    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    made = []
    for k in LADDER:
        plan = build(k, C_FIX, W_FIX, obs)
        if plan is None:
            raise SystemExit(f"rung k={k} is not reachable at C={C_FIX}, W={W_FIX}: run --grid")
        regs = words(plan)
        c, kk, w = measure(regs)
        if set(c) != {C_FIX} or set(kk) != {k} or set(w) != {W_FIX}:
            raise SystemExit(f"rung k={k}: construction does not verify: C={sorted(set(c))} k={sorted(set(kk))} W={sorted(set(w))}")
        name = f"rf_k{k}"
        open(f"{out}/srcs/{name}.bin", "wb").write(img(regs))
        items.append({"name": name, "kind": "ec", "family": "rf", "op": "df.un1b.fnot", "k": k, "c": C_FIX, "w": W_FIX,
                      "cell_bits_per_op": k, "port_bits_per_op": C_FIX, "ops_per_iter": 16,
                      "note": "register-file cell ladder: k stored bits flip per op, C on each port"})
        made.append((name, regs))
        # the same operands through the kernel whose cells never change value
        if k in NULLS:
            zname = f"rfz_k{k}"
            open(f"{out}/srcs/{zname}.bin", "wb").write(img(regs))
            items.append({"name": zname, "kind": "ec", "family": "rfz", "op": "df.un1a.fnot", "k": k, "c": C_FIX,
                          "w": W_FIX, "cell_bits_per_op": 0, "port_bits_per_op": C_FIX, "ops_per_iter": 16,
                          "note": "null test: identical operands, the kernel whose sinks never change value"})
    json.dump({"seed": SEED, "exp": "E74", "dist": DIST, "c_fix": C_FIX, "w_fix": W_FIX, "ladder": LADDER,
               "items": items}, open(f"{out}/manifest.json", "w"), indent=1)
    print(f"{len(items)} items -> {out} (ladder k = {','.join(str(k) for k in LADDER)}, C = {C_FIX}, W = {W_FIX})")

    if a.check:
        man = json.load(open(f"{out}/manifest.json"))
        bad = 0
        for it in man["items"]:
            if it["kind"] != "ec":
                continue
            blob = open(f"{out}/srcs/{it['name']}.bin", "rb").read()
            if len(blob) != 256:
                print(f"BAD {it['name']}: {len(blob)} bytes"); bad += 1; continue
            regs = regs_of(blob)
            c, k, w = measure(regs)
            ok = set(c) == {it["c"]} and set(w) == {it["w"]} and set(k) == {it["k"] or [x for x in set(k)][0]}
            kd = sorted(set(k))
            want_k = it["k"] if it["family"] == "rf" else kd[0]
            ok = set(c) == {it["c"]} and set(w) == {it["w"]} and set(k) == {want_k}
            print(f"{'ok ' if ok else 'BAD'} {it['name']:10s} op={it['op']:14s} C={sorted(set(c))} k={kd} W={sorted(set(w))} "
                  f"cells/op={it['cell_bits_per_op']}")
            bad += 0 if ok else 1
        # and the ladder's own identity: the rungs must differ from one another only in k
        print(f"check: {bad} bad of {sum(1 for i in man['items'] if i['kind'] == 'ec')} ec items")
        if bad:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
