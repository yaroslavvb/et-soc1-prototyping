#!/usr/bin/env python3
"""E151 (Q139; E145's check_e145.py and E141's check_e141.py, ported): refuse unless every reused file and every E151 card file is
byte-identical to predictions-e151.json > harness (card_code_unchanged_sha256, e151_card_files_sha256, e151_tiles_sha256) and, on the box,
every binary the run executes is byte-identical to harness.box_binaries_sha256 (E78's sparsity_host and the lab's ettelem, the two E138,
E140, E141 and E147 ran on aifoundry3).

    python3 tools/claims-v3/e151/check_e151.py [--root <tree root>] [--desk]    # exit 0 and "HARNESS OK", or exit 9 with each difference

--desk skips the binaries (the Intel has none). session_e151.sh runs it on the box before any device opens; selftest_e151.py on the Intel.
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
    reg = json.load(open(os.path.join(HERE, "predictions-e151.json")))
    h = reg["harness"]
    want = dict(h["card_code_unchanged_sha256"])
    want.update(h["e151_card_files_sha256"])
    want.update(h["e151_tiles_sha256"])
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
    print(f"HARNESS OK: {n} files match predictions-e151.json" + (" (desk: binaries not checked)" if "--desk" in sys.argv else ""))


if __name__ == "__main__":
    main()
