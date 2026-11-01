#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E107 reduction: tools/claims-v3/kinds/reduce_e78.py, byte-identical to its freeze (sha256 checked against predictions-e107.json), with E107's items installed
(e107_common.install_for_reduce: an item of a new arm is typed "<arm>:<format>", so its D is over the format's RESIDENT zeros and it has no cycle gate),
as reduce_e101.py did for E101. It writes what reduce_e78.py writes. Every argument is reduce_e78.py's.

    python3 tools/claims-v3/e107/reduce_e107.py <pass dir> [...] --out e107.json [--csv runs.csv] [--txt reduce.txt]
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e107_common as e107  # noqa: E402


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e107.json")))
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != want:
            sys.exit(f"refusing to reduce: {rel} sha256 {have} != registered {want}")
    e107.install_for_reduce()
    import reduce_e78  # noqa: E402  (after the check and the install)
    reduce_e78.main()
    a = sys.argv
    out = a[a.index("--out") + 1]
    d = json.load(open(out))
    d["experiment"] = "E107"
    json.dump(d, open(out, "w"), indent=1, default=lambda o: None)


if __name__ == "__main__":
    main()
