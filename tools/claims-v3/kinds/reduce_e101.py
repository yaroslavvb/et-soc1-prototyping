#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E101 reduction: reduce_e78.py, byte-identical to its freeze (sha256 checked against predictions-e101.json), with E101's items installed
(e101_common.install_for_reduce: an item of a new arm is typed "<arm>:<format>", so its D is over the format's RESIDENT zeros and it has no cycle gate). It writes
what reduce_e78.py writes. Every argument is reduce_e78.py's.

    python3 tools/claims-v3/kinds/reduce_e101.py <pass dir> [...] --out e101.json [--csv runs.csv] [--txt reduce.txt] [--leak auto|<W per C>] [--no-refit]
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e101_common as e101  # noqa: E402


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e101.json")))
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != want:
            sys.exit(f"refusing to reduce: {rel} sha256 {have} != registered {want}")
    e101.install_for_reduce()
    import reduce_e78  # noqa: E402  (after the check and the install)
    reduce_e78.main()
    a = sys.argv
    out = a[a.index("--out") + 1]
    d = json.load(open(out))
    d["experiment"] = "E101"
    json.dump(d, open(out, "w"), indent=1, default=lambda o: None)


if __name__ == "__main__":
    main()
