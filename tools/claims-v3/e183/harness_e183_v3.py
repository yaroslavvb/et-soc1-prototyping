#!/usr/bin/env python3
"""E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the harness check, v3, on the box
and at the desk. It reads files, never the card.

    python3 -B tools/claims-v3/e183/harness_e183_v3.py [--binaries]

1. harness-e183-v2.json (note 4's harness file) and harness_e183_v2.py (note 4's check) are at the sha256 harness-e183-v3.json pins for
   them, so v2's pins and v2's code cannot be swapped;
2. v2's own check, harness_e183_v2.py run by its path with this interpreter and the same argument, unchanged: v1's harness file at its pin,
   v1's check (check_e183.py harness) on v1's 80 box files and the images, with --binaries the train host's build (BUILD-E183.json, its two
   binaries, the patched main.cpp's pin and the 38-file build tree), and note 4's 7 box files at their pins;
3. note 6's box files (harness-e183-v3.json "files": block v3, queue v3, session v3, preflight v3 and this file), each at its sha256.
Prints "HARNESS OK: <n> files (v2's check: <its own line>; note 6's <k> box files at their pins)" or "HARNESS FAULTS: ..."; exit 1 on any.
Run by session_e183_v3.sh (with --binaries, before any device opens), block_e183_v3.sh's preflight and rb/s03_desk_e183_v7.sh (without).
Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    args = sys.argv[1:]
    if args not in ([], ["--binaries"]):
        print(__doc__)
        return 2
    h3 = json.load(open(os.path.join(HERE, "harness-e183-v3.json")))
    bad = []
    for key in ("harness_v2", "harness_v2_code"):
        p = os.path.join(ROOT, h3[key]["path"])
        if not os.path.exists(p) or sha(p) != h3[key]["sha256"]:
            bad.append(f"{h3[key]['path']} is not the one note 6 pinned")
    line2 = "(v2's check not run: its files are off their pins)"
    if not bad:
        r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, h3["harness_v2_code"]["path"])] + args,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True)
        line2 = (r.stdout.strip().splitlines() or ["(v2's check printed nothing)"])[-1]
        if r.returncode != 0 or not line2.startswith("HARNESS OK: "):
            bad.append(f"v2's check: {line2}")
    n2 = int(line2.split()[2]) if line2.startswith("HARNESS OK: ") else 0
    k = 0
    for rel, want in sorted(h3["files"].items()):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad.append(f"missing {rel}")
        elif sha(p) != want:
            bad.append(f"changed {rel}")
        else:
            k += 1
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (f" (+{len(bad) - 12})" if len(bad) > 12 else ""))
        return 1
    print(f"HARNESS OK: {n2 + k} files (v2's check: {line2}; note 6's {k} box files at their pins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
