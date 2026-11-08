#!/usr/bin/env python3
"""E183 (Q155, the kit): the train host's build inputs and its build tree at their pins (E182's check_inputs_e182.py, ported).

    python3 -B tools/claims-v3/e183/check_inputs_e183.py [--tree <top>]   # the build inputs in the tree at their pins: exit 0
                                                                          # "BUILD INPUTS OK: 40 files", or exit 9 "BUILD INPUTS DIFFER"
    python3 -B tools/claims-v3/e183/check_inputs_e183.py --src <dir>      # a generated, patched build tree holds exactly the pinned
                                                                          # files: exit 0 "BUILD TREE OK: <n> files", or exit 9
    python3 -B tools/claims-v3/e183/check_inputs_e183.py --list           # the 37 workloads/enercat inputs, relative to workloads/enercat/

The pins are harness-e183.json's (make_harness_e183.py): build_inputs, the 37 committed files of workloads/enercat, E180's generator
gen_acc_e180.py and its appended text acc-modes-e180.inc, and this kit's patch_host_e183.py; and build_tree, every file of the tree that
build_host_e183.sh makes from a clean stage of those 37 files (E180's generator, then the patch), relative to the tree. rb/s08's read
before the build runs the first form, and build_host_e183.sh runs the first and, after the patch, the second. It opens no device and
writes nothing. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WL = "workloads/enercat/"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(argv):
    h = json.load(open(os.path.join(HERE, "harness-e183.json")))
    inputs, tree = h["build_inputs"], h["build_tree"]
    if "--list" in argv:
        for rel in sorted(inputs):
            if rel.startswith(WL):
                print(rel[len(WL):])
        return 0
    if "--src" in argv:
        src = argv[argv.index("--src") + 1]
        have = set()
        for dp, _, fs in os.walk(src):
            for f in fs:
                have.add(os.path.relpath(os.path.join(dp, f), src))
        bad = [f"{r}: in the tree, not pinned" for r in sorted(have - set(tree))]
        for r, w in sorted(tree.items()):
            p = os.path.join(src, r)
            got = sha(p) if os.path.isfile(p) else "missing"
            if got != w:
                bad.append(f"{r}: {got[:16]} != pinned {w[:16]}")
        if bad:
            print("BUILD TREE DIFFERS - refusing:\n  " + "\n  ".join(bad[:20]))
            return 9
        print(f"BUILD TREE OK: {len(tree)} files at their pins, and nothing else")
        return 0
    top = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--tree" in argv:
        top = argv[argv.index("--tree") + 1]
    bad = []
    for rel, w in sorted(inputs.items()):
        p = os.path.join(top, rel)
        got = sha(p) if os.path.isfile(p) else "missing"
        if got != w:
            bad.append(f"{rel}: {got[:16]} != pinned {w[:16]}")
    if bad:
        print("BUILD INPUTS DIFFER - refusing:\n  " + "\n  ".join(bad[:20]))
        return 9
    print(f"BUILD INPUTS OK: {len(inputs)} files match harness-e183.json (37 of workloads/enercat, E180's generator and its text, the patch)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
