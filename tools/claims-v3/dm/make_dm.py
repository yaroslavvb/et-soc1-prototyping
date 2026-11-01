#!/usr/bin/env python3
"""V3-DM (E99, Q132): which mechanism carries the DRAM pattern effect. The operand images, the commands, every count.

    python3 tools/claims-v3/dm/make_dm.py <out-dir>                    # srcs/, manifest.json
    python3 tools/claims-v3/dm/make_dm.py <out-dir> --check            # + re-derive every count from the bytes on disk
    python3 tools/claims-v3/dm/make_dm.py <out-dir> --check --e81-gen <E81 gen dir>   # + byte identity of dp_c1, dp_c2

Same command as E75 and E81: flw_pat, --stride 64, 128 KB per hart, --harts 1, one 64 B line fetched per load. The
question and the frozen rules are in README.md. The images hold the counts apart that E75's and E81's images move
together (their high-pin count, encoded toggle count and raw toggle count correlate at 0.99-1.00, posthoc-desk.txt):

  Family   item              lines  what is held equal, what moves
  tent     dm_u1,2,4,5,7,8   1      every byte of a line one value of p ones: no toggle anywhere, no change between
                                    lines; w = 64p, pins driven high 64 min(p, 9-p)
  lane     dm_l08            1      lanes constant, one 0x00, one 0xFF: w 256, 32 high, no toggle (against dm_u4)
  beat     dm_a08,26,35,44   1      each beat one value, alternating X, Y: w 256, 496 raw toggles, half 0; high 32, 160,
                                    224, 256; encoded toggles 62, 62, 62, 496 (the DMI pin alone in the first three)
  bytes    dm_r08,26,44      2      random bytes with p in {0,8}, {2,6}, {4}: w 256, k 256, half 128, 248 raw toggles;
                                    high 32, 160, 256
  floor    dm_w1             1      one bit in every line
  ladder   dm_L<p>           p      p = 1,2,3,4,8,16,17,32,256,8192 distinct lines drawn from one byte distribution:
                                    every line w 256, 211 high, 258 encoded and 248 raw toggles, half 128 (exact to
                                    p = 17, within 2 beyond); consecutive lines differ in exactly 256 bits (p >= 2)
  anchors  dp_zeros, dp_bern, dp_c1, dp_c2: E81's bytes and commands, for the session tie

The file: operand takes exactly 256 B (four lines). Periods that do not divide 4 need the host's new lines: operand
(make_host_src.py); the images of 1, 2 and 4 lines keep file:. Each image starts at the region's line 0 whenever its
length divides 1 KB; every region of an image of p lines starts at a phase set by its slice and bank offset.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
sys.path.insert(0, os.path.join(HERE, "..", "dp"))
from dm_enc import ENC, HIGH, POP, POP9, bit_distance, counts, lines_of, within_toggles  # noqa: E402
from make_dp import build_images, lines_image  # noqa: E402  (E81's dp_c1 and dp_c2, unchanged)
from make_mf import args_for  # noqa: E402  (E75's DRAM command, unchanged)

SEED = 0xE99
LADDER = [1, 2, 3, 4, 8, 16, 17, 32, 256, 8192]
# one fixed byte distribution: the multiset nearest Binomial(8, 1/2) with exactly 256 ones in 64 bytes
MULTISET = {1: 2, 2: 7, 3: 14, 4: 18, 5: 14, 6: 7, 7: 2}
T_ENC, T_RAW, HALF, W_FIRST = 258, 248, 128, 128     # every ladder line with p <= 17 exactly; longer within TOL
TOL = {"t_enc": 2, "t_raw": 2, "half": 2, "w_first": 2}
BY_POP = {p: np.array([b for b in range(256) if POP[b] == p], dtype=np.uint8) for p in range(9)}
IDN = np.arange(256, dtype=np.int64)


def rand_lines(rng, n, pops):
    """n lines whose 64 bytes have the popcounts `pops` in random positions, each byte random among its class."""
    P = np.tile(np.array(pops, dtype=np.int64), (n, 1))
    P = rng.permuted(P, axis=1)
    out = np.zeros((n, 64), dtype=np.uint8)
    for p in set(pops):
        m = P == p
        out[m] = BY_POP[p][rng.integers(0, len(BY_POP[p]), m.sum())]
    return out


def line_stats(L):
    return {"t_enc": within_toggles(L, ENC), "t_raw": within_toggles(L, IDN),
            "half": bit_distance(L[:, :32], L[:, 32:]), "w_first": POP[L[:, :32]].sum(axis=1)}


def pool(rng, want, pops, exact, tol=None, batch=200000):
    """Rejection-sample `want` lines with the exact (or within tol) counts."""
    got, have = [], 0
    while have < want:
        L = rand_lines(rng, batch, pops)
        S = line_stats(L)
        ok = np.ones(batch, dtype=bool)
        for k, v in exact.items():
            ok &= np.abs(S[k] - v) <= (tol[k] if tol else 0)
        got.append(L[ok])
        have += int(ok.sum())
    return np.concatenate(got)[:want]


def chain(cands, p, rng, used, extra=None, tries=200):
    """A cycle of p distinct unused lines from cands, every consecutive pair exactly 256 bits apart; `extra(i)` lists
    earlier indices that line i must also be 256 bits from. The last line closes the cycle. Marks what it used."""
    for _ in range(tries):
        free = ~used.copy()
        start = np.flatnonzero(free)
        idx = [int(start[rng.integers(0, len(start))])]
        free[idx[0]] = False
        for i in range(1, p):
            need = [idx[-1]] + ([idx[j] for j in extra(i)] if extra else [])
            if i == p - 1 and p > 2:
                need.append(idx[0])
            ok = free.copy()
            for j in need:
                ok &= bit_distance(cands, np.broadcast_to(cands[j], cands.shape)) == 256
            c = np.flatnonzero(ok)
            if not len(c):
                idx = None
                break
            idx.append(int(c[rng.integers(0, len(c))]))
            free[idx[-1]] = False
        if idx is not None:
            used[idx] = True
            return cands[idx]
    raise RuntimeError("no cycle of %d lines in this pool" % p)


def uniform(v):
    return np.full((1, 64), v, dtype=np.uint8)


def beats(x, y):
    L = np.zeros((1, 64), dtype=np.uint8)
    for b in range(32):
        L[0, 2 * b] = L[0, 2 * b + 1] = x if b % 2 == 0 else y
    return L


def r_images(rng):
    """Period 2, 256 bits apart, half 128, 248 raw toggles and 128 ones in the first half on both lines."""
    out = {}
    for name, pops in (("dm_r08", [0] * 32 + [8] * 32), ("dm_r26", [2] * 32 + [6] * 32), ("dm_r44", [4] * 64)):
        L = pool(rng, 200, pops, {"t_raw": T_RAW, "half": HALF, "w_first": W_FIRST})
        out[name] = chain(L, 2, rng, np.zeros(len(L), dtype=bool))
    return out


def ladder(rng):
    """Lines of periods up to 17 have the counts exactly; periods 32, 256 and 8192 within TOL (two toggles at the
    fitted price is 0.006 W). No line is used twice across the ladder."""
    out = {}
    pops = sum(([p] * n for p, n in MULTISET.items()), [])
    exact = {"t_enc": T_ENC, "t_raw": T_RAW, "half": HALF, "w_first": W_FIRST}
    E = pool(rng, 600, pops, exact)
    used = np.zeros(len(E), dtype=bool)
    for p in LADDER:
        if p == 1:
            used[0] = True
            out["dm_L1"] = E[:1]
        elif p <= 17:
            out["dm_L%d" % p] = chain(E, p, rng, used)
    C = pool(rng, 40000, pops, exact, tol=TOL)
    used = np.zeros(len(C), dtype=bool)
    # the two lines each channel sees in a 32-line image (i, i + 16) are 256 bits apart too
    out["dm_L32"] = chain(C, 32, rng, used, extra=lambda i: [i - 16] if i >= 16 else [])
    out["dm_L256"] = chain(C, 256, rng, used)
    out["dm_L8192"] = chain(C, 8192, rng, used)
    return out


def build(a_out):
    rng = np.random.default_rng(SEED)
    imgs = {"dm_w1": None}
    w1 = np.zeros((1, 64), dtype=np.uint8)
    w1[0, 0] = 0x01
    imgs["dm_w1"] = w1
    for p, v in ((1, 0x01), (2, 0x03), (4, 0x0F), (5, 0x1F), (7, 0x7F), (8, 0xFF)):
        imgs["dm_u%d" % p] = uniform(v)
    l08 = np.zeros((1, 64), dtype=np.uint8)
    l08[0, 1::2] = 0xFF
    imgs["dm_l08"] = l08
    for nm, x, y in (("dm_a08", 0x00, 0xFF), ("dm_a26", 0x03, 0xFC), ("dm_a35", 0x07, 0xF8), ("dm_a44", 0x0F, 0xF0)):
        imgs[nm] = beats(x, y)
    imgs.update(r_images(rng))
    imgs.update(ladder(rng))
    e81, _ = build_images()
    for nm in ("dp_c1", "dp_c2"):
        imgs[nm] = lines_of(lines_image(e81[nm]))
    return imgs


def image_bytes(L):
    """The bytes the host gets: a file: image is exactly 256 B, so a 1-, 2- or 4-line period is repeated up to four
    lines; anything else goes as itself through lines:."""
    n = len(L)
    if n in (1, 2, 4):
        return np.tile(L, (4 // n, 1)).tobytes(), "file"
    return L.tobytes(), "lines"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--e81-gen")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "srcs"), exist_ok=True)
    imgs = build(a.out)
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    for nm in ("dp_zeros", "dp_bern"):
        base = args_for("dram", None)
        if nm == "dp_bern":
            base = [x if x != "zeros" else "bern:0.5" for x in base]
        items.append({"name": nm, "kind": "cmd", "tool": "main", "family": "anchor", "level": "dram",
                      "k": 0 if nm == "dp_zeros" else 256, "w": 0 if nm == "dp_zeros" else 256,
                      "elem_bits": 512, "n_elem": 4, "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {", "args": base,
                      "designed": "E81's " + nm})
    for nm, L in imgs.items():
        blob, op = image_bytes(L)
        open(os.path.join(a.out, "srcs", nm + ".bin"), "wb").write(blob)
        args = args_for("dram", nm)
        if op == "lines":
            args = [x.replace("file:", "lines:") if x.startswith("file:") else x for x in args]
        c = counts(lines_of(blob))
        items.append({"name": nm, "kind": "cmd", "tool": "main",
                      "family": "anchor" if nm.startswith("dp_") else nm[:4], "level": "dram",
                      "src": "%GEN%/srcs/" + nm + ".bin", "src_bytes": len(blob), "k": c["k"], "w": c["w"],
                      "elem_bits": 512, "n_elem": len(L), "unit": "DRAM, 128 MB in all", "tag": "ENERCAT {",
                      "args": args, "designed": "period %d; hi %.1f, t_enc %.1f, t_raw %.1f, k %.1f, w %.1f"
                      % (len(L), c["hi"], c["t_enc"], c["t_raw"], c["k"], c["w"])})
    man = {"exp": "E99", "seed": SEED, "ladder": LADDER, "multiset": MULTISET, "items": items}
    json.dump(man, open(os.path.join(a.out, "manifest.json"), "w"), indent=1)
    print("%d items -> %s" % (len(items), a.out))
    if not a.check:
        return
    # ---- re-derive from the bytes on disk -------------------------------------------------------------------------
    bad = 0
    C = {}
    want = {  # item: (period, w, hi, t_enc, t_raw, k, half) exact
        "dm_w1": (1, 1, 1, 1, 1, 0, 1),
        "dm_u1": (1, 64, 64, 0, 0, 0, 0), "dm_u2": (1, 128, 128, 0, 0, 0, 0), "dm_u4": (1, 256, 256, 0, 0, 0, 0),
        "dm_u5": (1, 320, 256, 0, 0, 0, 0), "dm_u7": (1, 448, 128, 0, 0, 0, 0), "dm_u8": (1, 512, 64, 0, 0, 0, 0),
        "dm_l08": (1, 256, 32, 0, 0, 0, 0),
        "dm_a08": (1, 256, 32, 62, 496, 0, 0), "dm_a26": (1, 256, 160, 62, 496, 0, 0),
        "dm_a35": (1, 256, 224, 62, 496, 0, 0), "dm_a44": (1, 256, 256, 496, 496, 0, 0)}
    for it in items:
        if not it.get("src"):
            continue
        blob = open(it["src"].replace("%GEN%", a.out), "rb").read()
        L = lines_of(blob)
        c = counts(L)
        c["sha256"] = hashlib.sha256(blob).hexdigest()
        c["distinct"] = int(len(np.unique(L, axis=0)))
        C[it["name"]] = c
        ok = len(blob) == it["src_bytes"]
        if it["name"] in want:
            per, w, hi, te, tr, k, half = want[it["name"]]
            ok &= (c["distinct"], c["w"], c["hi"], c["t_enc"], c["t_raw"], c["k"], c["half"]) == (per, w, hi, te, tr, k, half)
        if it["name"].startswith("dm_r"):
            hi = {"dm_r08": 32, "dm_r26": 160, "dm_r44": 256}[it["name"]]
            ok &= (c["distinct"], c["w"], c["hi"], c["t_raw"], c["k"], c["half"]) == (2, 256, hi, T_RAW, 256, HALF)
        if it["name"].startswith("dm_L"):
            p = int(it["name"][4:])
            ok &= c["distinct"] == p and c["w"] == 256 and c["hi"] == 211
            if p <= 17:
                ok &= (c["t_enc"], c["t_raw"], c["half"]) == (T_ENC, T_RAW, HALF)
            else:
                ok &= abs(c["t_enc"] - T_ENC) <= 2 and abs(c["t_raw"] - T_RAW) <= 2 and abs(c["half"] - HALF) <= 2
            ok &= c["k"] == (0 if p == 1 else 256)
            ok &= all(POP[L].sum(axis=1) == 256)
        print("%s %-9s bytes=%-6d lines=%-5d distinct=%-5d w=%-6.1f hi=%-6.1f t_enc=%-6.1f t_raw=%-6.1f k=%-6.1f half=%-6.1f"
              " k_chan=%-6.1f k_shire=%-6.1f k_bank=%-6.1f"
              % ("ok " if ok else "BAD", it["name"], len(blob), len(L), c["distinct"], c["w"], c["hi"], c["t_enc"],
                 c["t_raw"], c["k"], c["half"], c["k_chan"], c["k_shire"], c["k_bank"]))
        bad += 0 if ok else 1
    if a.e81_gen:
        for nm in ("dp_c1", "dp_c2"):
            x = open(os.path.join(a.out, "srcs", nm + ".bin"), "rb").read()
            y = open(os.path.join(a.e81_gen, "srcs", nm + ".bin"), "rb").read()
            same = x == y
            print("%s %s == E81's (sha256 %s)" % ("ok " if same else "BAD", nm, hashlib.sha256(x).hexdigest()[:16]))
            bad += 0 if same else 1
    json.dump(C, open(os.path.join(a.out, "counts.json"), "w"), indent=1, sort_keys=True)
    print("check: %d bad" % bad)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
