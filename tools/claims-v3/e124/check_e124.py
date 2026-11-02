#!/usr/bin/env python3
"""E124 (Q134): refuse unless every reused file is byte-identical to predictions-e124.json › harness.reused_unchanged_sha256.

    python3 tools/claims-v3/e124/check_e124.py [--root <tree root>]       # exit 0 and "HARNESS OK", or exit 9 with each difference

session_e124.sh runs it on the box before any device opens; selftest_e124.py runs it on the Intel. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def check(root):
    reg = json.load(open(os.path.join(HERE, "predictions-e124.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(root, rel)
        have = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    return bad, len(reg["harness"]["reused_unchanged_sha256"])


def main():
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]
    bad, n = check(root)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} reused files match predictions-e124.json")


if __name__ == "__main__":
    main()
