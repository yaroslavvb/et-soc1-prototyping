#!/usr/bin/env python3
"""E137 (Q136): refuse unless every reused file and every E137 card file is byte-identical to predictions-e137.json > harness
(card_code_unchanged_sha256, e137_card_files_sha256) and, on the box, every binary the run executes is byte-identical to
harness.box_binaries_sha256 (E78's sparsity_host, the one E128 ran on this box; the lab's ettelem).

    python3 tools/claims-v3/e137/check_e137.py [--root <tree root>] [--desk]    # exit 0 and "HARNESS OK", or exit 9 with each difference

--desk skips the binaries (the Intel has none). session_e137.sh runs it on the box before any device opens; selftest_e137.py on the Intel.
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(root, box=True):
    reg = json.load(open(os.path.join(HERE, "predictions-e137.json")))
    h = reg["harness"]
    want = dict(h["card_code_unchanged_sha256"])
    want.update(h["e137_card_files_sha256"])
    if box:
        want.update(h["box_binaries_sha256"])
    bad = []
    for rel, w in want.items():
        p = os.path.join(root, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != w:
            bad.append(f"{rel}: {have} != registered {w}")
    return bad, len(want)


def main():
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]
    bad, n = check(root, box="--desk" not in sys.argv)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} files match predictions-e137.json" + (" (desk: binaries not checked)" if "--desk" in sys.argv else ""))


if __name__ == "__main__":
    main()
