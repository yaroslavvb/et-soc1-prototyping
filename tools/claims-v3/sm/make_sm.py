#!/usr/bin/env python3
"""V3-SM (E68, the stage map): operand files that move one stage group of the multiply-add at a time.

    python3 tools/claims-v3/sm/make_sm.py <out-dir>            # tiles/, manifest.json
    python3 tools/claims-v3/sm/make_sm.py <out-dir> --check    # also re-derive every count from the files

The ladder experiments (E60, E65) priced *a flipped operand bit* at the board. They cannot say **where** in the
7-stage pipeline (tfma.stages: f0 capture, f1-f2 Booth+Wallace+product adder, f3 align, f4 add+leading-one,
f5 normalise, f6 round) that energy is spent. This set does, by a contrast that is exact in the arithmetic:

  * **An fp32 multiplier never sees the sign or the exponent of its operands.** The Booth recoder reads a's
    significand and the rows are 0, +-b, +-2b in b's significand (tfma.booth.rows); the sign is one XOR and the
    exponent one small adder. So an item whose two alternating B words **share their significand** and differ
    only in sign or exponent drives *the identical switching pattern through the Booth rows, the Wallace tree,
    its register and the product adder* -- f1 and f2 are frozen by construction -- while f3, f4, f5 and f6 see
    two different results every cycle.
  * Conversely, an item whose two B words share their sign and exponent and differ only in low significand bits
    moves f1 and f2 and leaves the product's exponent, and therefore f3's shift distance, where it was.

Every item alternates its two B words every cycle (the issue order of make_hl.py: lane l gets B[k][l] then
B[k][8+l]), against its family's own zero, which is the same base with no alternation. Prices are differences
from that zero, so the static power, the clocking and the kernel's fixed cost all cancel.

Families (item names in manifest.json; all fma, A constant, 512 minions -- see README "Power"):

  zero       smz_q           A = 1.0, B constant                     the quiet family's zero
             smz_b           A = pi,  B constant                     the busy family's zero
  multiplier sm_lo12         mask 0x00000FFF   mantissa bits 0-11    f1/f2 only, product stays in its binade
             sm_hi12         mask 0x007FF800   mantissa bits 11-22   f1/f2 only, a larger product change
             sm_sp12         mask spread_12    12 bits over 0-22     f1/f2 only, the bits spread
  back end   sm_sgn          mask 0x80000000   the sign bit          f1/f2 FROZEN; the add becomes a subtract
             sm_e1           mask 1<<23        exponent -1           f1/f2 FROZEN; f3 shift distance 1
             sm_e16          mask 1<<27        exponent -16          f1/f2 FROZEN; f3 shift distance 16
             sm_e64          mask 1<<29        exponent -64          f1/f2 FROZEN; f3 saturates, f4 trivial
  both       sm_sgnlo        mask 0x80000FFF   sign + mantissa 0-11  additivity: sm_sgn + sm_lo12 ?
             sm_pi_sgn       mask 0x80000000, A = pi                 the sign flip with a busy partner

The three "f1/f2 FROZEN" claims are asserted from the files in `--check` (`frozen_significand`): the two B words
of every lane are bit-identical in bits 0-22, so no Booth row and no tree input differs between the two cycles.

One base serves every masked item, so any two items differ in their mask alone. The base keeps both words normal
and finite under every mask above (exponent 127: 127^1 = 126, 127^16 = 111, 127^64 = 63; bit 30 is never used,
because 127^128 would be inf/NaN).
"""
import argparse
import json
import os
import sys

import numpy as np

HL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hl")
sys.path.insert(0, os.path.abspath(HL))
from make_hl import ONE, PI, N, base_b, ladder_tiles, write_tiles, fma_flips, is_normal, spread_mask  # noqa: E402

SEED = 20261026
MANT = 0x007FFFFF

# name -> (mask, partner)
MASKS = [
    ("smz_q",     0x00000000, ONE),
    ("smz_b",     0x00000000, PI),
    ("sm_lo12",   0x00000FFF, ONE),
    ("sm_hi12",   0x007FF800, ONE),
    ("sm_sp12",   spread_mask(12), ONE),
    ("sm_sgn",    0x80000000, ONE),
    ("sm_e1",     1 << 23,    ONE),
    ("sm_e16",    1 << 27,    ONE),
    ("sm_e64",    1 << 29,    ONE),
    ("sm_sgnlo",  0x80000FFF, ONE),
    ("sm_pi_sgn", 0x80000000, PI),
]

# Which stage groups the mask is designed to move, from the arithmetic alone (the RTL bench measures the rest).
DESIGN = {
    "smz_q":     "zero (quiet partner)",
    "smz_b":     "zero (busy partner)",
    "sm_lo12":   "f1/f2 only",
    "sm_hi12":   "f1/f2 only",
    "sm_sp12":   "f1/f2 only",
    "sm_sgn":    "f3-f6 only (f1/f2 frozen)",
    "sm_e1":     "f3-f6 only (f1/f2 frozen)",
    "sm_e16":    "f3-f6 only (f1/f2 frozen)",
    "sm_e64":    "f3-f6 only (f1/f2 frozen)",
    "sm_sgnlo":  "f1/f2 and f3-f6",
    "sm_pi_sgn": "f3-f6 only (f1/f2 frozen), busy partner",
}


def frozen_significand(A, B):
    """True when the two B words of every lane agree in bits 0-22: the tree's input never changes."""
    return all((B[k][l] & MANT) == (B[k][8 + l] & MANT) for k in range(N) for l in range(8))


def build(out):
    os.makedirs(f"{out}/tiles", exist_ok=True)
    os.makedirs(f"{out}/srcs", exist_ok=True)
    base = base_b(np.random.default_rng(SEED), 127)
    for w in base:
        assert is_normal(w), hex(w)
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"},
             {"name": "anchor_zeros", "kind": "fma", "family": "anchor", "values": "zeros"}]
    for name, mask, partner in MASKS:
        for w in base:
            assert is_normal(w) and is_normal(w ^ mask), (name, hex(w), hex(mask))
        A, B = ladder_tiles(partner, mask, base)
        write_tiles(f"{out}/tiles/{name}.bin", A, B)
        items.append({"name": name, "kind": "fma", "family": "sm", "mask": f"0x{mask:08x}",
                      "mask_bits": bin(mask).count("1"),
                      "partner": "1.0" if partner == ONE else "pi",
                      "zero": "smz_b" if partner == PI else "smz_q",
                      "design": DESIGN[name], "frozen_significand": frozen_significand(A, B),
                      "flips": fma_flips(A, B)})
    json.dump({"seed": SEED, "base": [f"0x{w:08x}" for w in base], "items": items},
              open(f"{out}/manifest.json", "w"), indent=1)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    items = build(a.out)
    for it in items:
        if "flips" not in it:
            print(f"{it['name']:12s} fma  built-in --values {it['values']}")
            continue
        f = it["flips"]
        print(f"{it['name']:12s} mask {it['mask']}  A={it['partner']:3s}  B bits/op {f['b_all']:6d} "
              f"(sign {f['b_sign']:5d} exp {f['b_exp']:5d} mant {f['b_mant']:6d})  A bits/op {f['a_all']:5d}  "
              f"tree frozen {str(it['frozen_significand']):5s}  {it['design']}")
    if a.check:
        for it in items:
            if "flips" not in it:
                continue
            raw = np.fromfile(f"{a.out}/tiles/{it['name']}.bin", dtype="<u4")
            A, B = raw[:256].reshape(16, 16).tolist(), raw[256:].reshape(16, 16).tolist()
            assert fma_flips(A, B) == it["flips"], it["name"]
            assert frozen_significand(A, B) == it["frozen_significand"], it["name"]
            # every masked item differs from the zero of its partner in the mask alone
            if it["name"] not in ("smz_q", "smz_b"):
                z = np.fromfile(f"{a.out}/tiles/{it['zero']}.bin", dtype="<u4")
                assert (z[:256] == raw[:256]).all(), f"{it['name']}: A differs from its zero"
                m = int(it["mask"], 16)
                d = (z[256:] ^ raw[256:])
                assert set(int(x) for x in np.unique(d)) <= {0, m}, f"{it['name']}: B differs by more than the mask"
        print("check: every count re-derived, every item differs from its zero in the mask alone")


if __name__ == "__main__":
    main()
