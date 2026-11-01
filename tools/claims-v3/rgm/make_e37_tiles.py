#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E101: the tile files of E37's fill, tiles/<type>/e37.bin: every element -2, -1, +1 or +2, as launchers/mmbench/mmbench.cpp fills its tiles (2,048 bytes,
raw A then raw B, the kinds' format). The element slots are drawn independently, so no layout question arises. Deterministic: the seed is fixed.

    python3 tools/claims-v3/rgm/make_e37_tiles.py
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
HALF = {-2: 0xC000, -1: 0xBC00, 1: 0x3C00, 2: 0x4000}    # launchers/mmbench/mmbench.cpp halfBits


def main():
    rng = np.random.default_rng(101)
    for ty, n in (("fp32", 512), ("fp16", 1024), ("int8", 2048)):
        v = rng.choice([-2, -1, 1, 2], size=n)
        if ty == "fp32":
            b = v.astype("<f4").tobytes()
        elif ty == "fp16":
            b = np.array([HALF[int(x)] for x in v], dtype="<u2").tobytes()
        else:
            b = v.astype("i1").tobytes()
        assert len(b) == 2048
        p = os.path.join(HERE, "tiles", ty)
        os.makedirs(p, exist_ok=True)
        open(os.path.join(p, "e37.bin"), "wb").write(b)


if __name__ == "__main__":
    main()
