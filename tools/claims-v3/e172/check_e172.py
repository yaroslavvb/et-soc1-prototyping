#!/usr/bin/env python3
"""E172 (Q142(k6), tools/claims-v3/e172/E172.md): pool 8 in E164's form on aifoundry1 card 1 (E164's check_e164.py, ported): refuse unless every reused file, every E172 card file, the registration and
plan, the pinned watcher files and pool 8's files and tiles are byte-identical to harness-e172.json (card_code_unchanged_sha256,
e172_card_files_sha256, registration_sha256, watcher_sha256, pool_sha256) and, on the box, every binary the run executes is byte-identical
to harness.box_binaries_sha256 (E164's four pins on this card: E78's sparsity_host, the heater; the lab's ettelem; the kernel; Q139(k)'s
patched C-logging host). A binary that differs or is missing stops the session; a rebuild needs a dated amendment re-pinning it.

    python3 -B tools/claims-v3/e172/check_e172.py [--tree <top>] [--desk]     # exit 0 "HARNESS OK", or exit 9 with each difference

--desk skips the binaries (the Intel has none). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(top, box=True):
    h = json.load(open(os.path.join(HERE, "harness-e172.json")))
    want = dict(h["card_code_unchanged_sha256"])
    want.update(h["e172_card_files_sha256"])
    want.update(h["registration_sha256"])
    want.update(h["watcher_sha256"])
    want.update(h["pool_sha256"])
    if box:
        want.update(h["box_binaries_sha256"])
    bad = []
    for rel, w in want.items():
        p = os.path.join(top, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != w:
            bad.append(f"{rel}: {have} != registered {w}")
    return bad, len(want)


def main():
    top = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--tree" in sys.argv:
        top = sys.argv[sys.argv.index("--tree") + 1]
    bad, n = check(top, box="--desk" not in sys.argv)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} files match harness-e172.json" + (" (desk: binaries not checked)" if "--desk" in sys.argv else ""))


if __name__ == "__main__":
    main()
