#!/usr/bin/env python3
"""E182 (Q153, the kit's dated note 1; the verifier's MAJOR 2, the E174 class): the train host's build inputs at their pinned sha256.

    python3 -B tools/claims-v3/e182/check_inputs_e182.py [--tree <top>]   # every file of harness-e182-note1.json in the tree: exit 0
                                                                          # "NOTE1 FILES OK: 10 files", or exit 9 "NOTE1 FILES DIFFER"
    python3 -B tools/claims-v3/e182/check_inputs_e182.py --src <dir>      # a build's copy: <dir> holds exactly the 9 build inputs
                                                                          # (main.cpp unpatched) at their pins: exit 0 "BUILD INPUTS OK:
                                                                          # 9 files", or exit 9
    python3 -B tools/claims-v3/e182/check_inputs_e182.py --list           # the 9, relative to workloads/sparsity/, one a line

The pins: harness-e182-note1.json (the 8 build inputs beside main.cpp, and note 1's two box files) and harness-e182.json (main.cpp,
card_code_unchanged_sha256), both read beside this file. rb/s08_a3_preflight_e182_v2.sh runs it on the box before the build, and
build_host_e182_v2.sh runs it twice (the tree, then its copy). It opens no device and writes nothing. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WL = "workloads/sparsity/"
MAIN = "workloads/sparsity/host/main.cpp"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pins():
    n1 = json.load(open(os.path.join(HERE, "harness-e182-note1.json")))
    h = json.load(open(os.path.join(HERE, "harness-e182.json")))
    build = dict(n1["train_host_build_inputs_sha256"])
    build[MAIN] = h["card_code_unchanged_sha256"][MAIN]
    return n1, build


def main(argv):
    n1, build = pins()
    if "--list" in argv:
        for rel in sorted(build):
            print(rel[len(WL):])
        return 0
    if "--src" in argv:
        src = argv[argv.index("--src") + 1]
        want = {rel[len(WL):]: h for rel, h in build.items()}
        have = set()
        for dp, _, fs in os.walk(src):
            for f in fs:
                have.add(os.path.relpath(os.path.join(dp, f), src))
        bad = [f"{r}: in the copy, not a build input" for r in sorted(have - set(want))]
        for r, w in sorted(want.items()):
            p = os.path.join(src, r)
            got = sha(p) if os.path.isfile(p) else "missing"
            if got != w:
                bad.append(f"{r}: {got} != pinned {w}")
        if bad:
            print("BUILD INPUTS DIFFER - refusing:\n  " + "\n  ".join(bad))
            return 9
        print(f"BUILD INPUTS OK: {len(want)} files in the build's copy at their pins, and nothing else")
        return 0
    top = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--tree" in argv:
        top = argv[argv.index("--tree") + 1]
    want = dict(n1["train_host_build_inputs_sha256"])
    want.update(n1["kit_note1_box_files_sha256"])
    bad = []
    for rel, w in want.items():
        p = os.path.join(top, rel)
        got = sha(p) if os.path.isfile(p) else "missing"
        if got != w:
            bad.append(f"{rel}: {got} != pinned {w}")
    if bad:
        print("NOTE1 FILES DIFFER - refusing:\n  " + "\n  ".join(bad))
        return 9
    print(f"NOTE1 FILES OK: {len(want)} files match harness-e182-note1.json (8 build inputs, 2 box files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
