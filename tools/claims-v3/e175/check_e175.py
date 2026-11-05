#!/usr/bin/env python3
"""E175 (Q143(g)): the harness check. Every file of harness-e175.json byte-identical to the Intel's committed tree and, on the box, the three
pinned binaries (the C-logging host, E80's kernel and sampler) with the registered sha256; else no device opens and nothing is scored. No device,
no lock. E173's check_e173.py (lab 5a2a9ba0; E170's form) with E175's list.

    python3 -B tools/claims-v3/e175/check_e175.py          # on the box: HARNESS OK <n> + 3 binaries, exit 0; else the differences, exit 9
    python3 -B tools/claims-v3/e175/check_e175.py --desk   # at the desk: the files only
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    desk = "--desk" in sys.argv
    with open(os.path.join(HERE, "harness-e175.json")) as f:
        H = json.load(f)
    bad = []
    items = list(H["files_sha256"].items()) + ([] if desk else list(H["box_binaries_sha256"].items()))
    for rel, want in items:
        p = os.path.join(TOP, rel)
        got = sha(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: {got}, registered {want}")
    if bad:
        print(f"HARNESS BAD: {len(bad)} of {len(items)}")
        for b in bad:
            print("  ", b)
        return 9
    print(f"HARNESS OK {len(H['files_sha256'])}" + ("" if desk else f" + {len(H['box_binaries_sha256'])} binaries"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
