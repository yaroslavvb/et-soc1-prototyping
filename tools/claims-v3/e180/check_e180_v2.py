#!/usr/bin/env python3
"""E180's checks, v2 (the kit's dated note 1, KIT.md.dated-note-1.md sections 1 and 4), off-card (they read files, never the card).

    python3 tools/claims-v3/e180/check_e180_v2.py harness [--binaries]
        every file the v2 box session runs, sources, builds from or reads equals harness-e180-v2.json's sha256 (the box's E180 build
        too with --binaries, against build/enercat-e180/BUILD-E180.json, which build_e180.sh writes); every image equals
        kinds-e180.json's sha256. Prints "HARNESS OK: <n> files" or the faults; exit 1 on any.
    python3 tools/claims-v3/e180/check_e180_v2.py block <pass dir> --card <id> --root <tree>
    python3 tools/claims-v3/e180/check_e180_v2.py smoke <smoke pass dir> --root <tree>
        v1's post-block check and smoke gate (check_e180.py's block() and smoke(), imported unchanged).

check_e180.py (v1, which stays as committed) with one change: the harness is harness-e180-v2.json (make_harness_e180_v2.py), which names
the v2 files the session runs (block_e180_v2.sh, others_d1_e180.sh, run_e180_v2.py, queue_e180_v2.sh, session_e180_v2.sh, this file,
preflight_e180_v2.sh, check_elf_e180.py) in place of v1's block, runner, queue, session, check and preflight. The image check and the
binaries' check are v1's code, unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_e180 as c1  # noqa: E402  (v1's sha, block and smoke, unchanged)

ROOT = c1.ROOT


def harness(binaries):
    h = json.load(open(os.path.join(HERE, "harness-e180-v2.json")))
    bad = []
    for rel, want in sorted(h["files"].items()):
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            bad.append(f"missing {rel}")
        elif c1.sha(p) != want:
            bad.append(f"changed {rel}")
    kinds = json.load(open(os.path.join(HERE, "kinds-e180.json")))
    for rel, want in kinds["images"].items():
        p = os.path.join(HERE, rel)
        if not os.path.exists(p) or c1.sha(p) != want:
            bad.append(f"image {rel} differs from kinds-e180.json")
    n = len(h["files"]) + len(kinds["images"])
    if binaries:
        bj = os.path.join(ROOT, "build", "enercat-e180", "BUILD-E180.json")
        if not os.path.exists(bj):
            bad.append("build/enercat-e180/BUILD-E180.json missing (run build_e180.sh)")
        else:
            b = json.load(open(bj))
            for rel, want in b["binaries"].items():
                p = os.path.join(ROOT, rel)
                if not os.path.exists(p) or c1.sha(p) != want:
                    bad.append(f"binary {rel} differs from BUILD-E180.json")
                n += 1
            if b.get("acc_modes_inc_sha256") != h["acc_modes_inc_sha256"]:
                bad.append("the build's appended modes differ from acc-modes-e180.inc")
    if bad:
        print("HARNESS FAULTS: " + "; ".join(bad[:12]) + (f" (+{len(bad) - 12})" if len(bad) > 12 else ""))
        return 1
    print(f"HARNESS OK: {n} files (v2)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["harness", "block", "smoke"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--card")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--binaries", action="store_true")
    a = ap.parse_args()
    if a.cmd == "harness":
        sys.exit(harness(a.binaries))
    if a.cmd == "block":
        sys.exit(c1.block(a.dir, a.card, a.root))
    sys.exit(c1.smoke(a.dir, a.root))


if __name__ == "__main__":
    main()
