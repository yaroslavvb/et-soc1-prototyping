#!/usr/bin/env python3
"""E155 (Q139): refuse unless every reused file is byte-identical to predictions-e155.json › harness.reused_unchanged_sha256 and, on the box, every binary
the run executes is byte-identical to harness.box_binaries_sha256 (E109's sp109 as E124 built it on aifoundry1 and E129 and E148 ran it, E78's heater, the lab's ettelem). A copy of tools/claims-v3/e148/check_e148.py with the names changed.

    python3 tools/claims-v3/e155/check_e155.py [--root <tree root>] [--desk]    # exit 0 and "HARNESS OK", or exit 9 with each difference

--desk skips the binaries (the Intel has none). session_e155.sh and run_e155.py run it on the box before any device opens; selftest_e155.py on the Intel.
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
    reg = json.load(open(os.path.join(HERE, "predictions-e155.json")))
    h = reg["harness"]
    want = dict(h["reused_unchanged_sha256"])
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
    print(f"HARNESS OK: {n} files match predictions-e155.json" + (" (desk: binaries not checked)" if "--desk" in sys.argv else ""))


if __name__ == "__main__":
    main()
