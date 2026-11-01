#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E109, POST HOC (written Sun 1 Nov 2026 13:2x PST, after the registered reduction had set pass 10912 aside): the same reduction with ONE of E78's
pass gates lifted, so that all three passes are read. Nothing here is registered; every number it writes is labelled post hoc in the data README.

    uv run tools/claims-v3/e109/posthoc_e109.py <pass dir> [...] --out e109-3pass.json [--csv ...] [--txt ...]

reduce_e78.py, byte-identical to its freeze (sha256 checked as reduce_e109.py checks it), with E109's items installed, and GATES["random_range_w"]
raised from E78's 1.0 W to 99 W before main() runs. That gate set pass 10912 aside because its random fp32 anchor's three runs spanned 1.067 W (one run
read 51.75 W of board power against 52.82 and 52.75 W). The random fp32 anchor enters no E109 statistic except R10's tie; every E109 D is over the
format's zeros anchors, which in pass 10912 span 0.053 W (fp32) and 0.054 W (int8). Every other gate is E78's, unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e109_common as e109  # noqa: E402


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e109.json")))
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != want:
            sys.exit(f"refusing to reduce: {rel} sha256 {have} != registered {want}")
    e109.install_for_reduce()
    import reduce_e78  # noqa: E402
    reduce_e78.GATES["random_range_w"] = 99.0          # POST HOC: the one change
    reduce_e78.main()
    a = sys.argv
    out = a[a.index("--out") + 1]
    d = json.load(open(out))
    d["experiment"] = "E109"
    d["post_hoc"] = "reduce_e78.py with GATES['random_range_w'] = 99 W (E78's 1.0 W), all else unchanged; tools/claims-v3/e109/posthoc_e109.py"
    json.dump(d, open(out, "w"), indent=1, default=lambda o: None)


if __name__ == "__main__":
    main()
