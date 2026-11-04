#!/usr/bin/env python3
"""Q140(m), M9-REGISTRATION.md section 8: the 16 fp32 single-bit tiles of the bench check (A every element 1.0; B every word w with
bit k flipped in columns 8-15, pool 6's b_onebit design) at four base words and four bits. Writes tiles/, cal-tiles.json and
points.txt beside it, and prints the bench's --extra-tiles argument.

    python3 make_cal_tiles.py            # then, in a build of rtl-sim/fma_toggle_v2 (Q133(b)'s README, section Rerun):
    python3 run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --maps maps --kinds <tree>/tools/claims-v3/kinds \\
        --only __none__ --jobs 4 --points "$(cat points.txt)" --out counts-cal.json --extra-tiles "<the printed argument>"
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "kinds"))
import make_kinds as mk  # noqa: E402

N = 16
WORDS = {"third": 0x3EAAAAAB, "w79": 0x3FBD207C, "w67": 0x3FBBC9E4, "pi": 0x40490FDB}
BITS = (12, 17, 20, 21)
os.makedirs(os.path.join(HERE, "tiles"), exist_ok=True)
spec, man = [], []
for wn, w in WORDS.items():
    for k in BITS:
        aw = np.full((N, N), 0x3F800000, dtype=np.uint64)
        bw = np.full((N, N), w, dtype=np.uint64)
        bw[:, 8:] ^= np.uint64(1 << k)
        raw = mk.from_words(aw, bw)
        name = f"cal_{wn}_b{k}"
        p = os.path.join(HERE, "tiles", f"fp32.{name}.bin")
        open(p, "wb").write(raw)
        spec.append(f"fp32:{name}:{p}")
        man.append({"name": f"fp32.{name}", "type": "fp32", "base_word": f"0x{w:08X}", "bit": k, "file": os.path.relpath(p, HERE),
                    "sha256": hashlib.sha256(raw).hexdigest()})
json.dump({"tiles": man}, open(os.path.join(HERE, "cal-tiles.json"), "w"), indent=1)
ops = 0.5 * 600e6 / 546
pts = [int(ops * (2 * j + 1) / 18) for j in range(9)]
assert all(int(ops * f) in pts for f in (1 / 6, 1 / 2, 5 / 6))
open(os.path.join(HERE, "points.txt"), "w").write(",".join(str(x) for x in pts))
print(",".join(spec))
