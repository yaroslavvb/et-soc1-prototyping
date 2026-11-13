#!/usr/bin/env python3
"""E190's harness (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the sha256 of every file a box runs or reads for E190, and its
check. Python's own modules only.

    python3 -B tools/claims-v3/e190/check_e190.py --make            writes harness-e190.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e190/check_e190.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e190/check_e190.py --box [--only-src]
                    on a box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the ten rgm136 sources
                    only (build_e190.sh's first check)
    python3 -B tools/claims-v3/e190/check_e190.py --list            the paths, one a line (step 5's sync list)
The files: E190's box files (the runner, its common module, the wrapper, the build, this check, the preflight, the guard, the doubles the
box's dry pass runs); the registration's plan and forecast (the runner reads them); the device-command checker and its table; E136's
rgm136 sources, unchanged (the build's input; the registration's subtree 30da3ec3...); the three tiles the --values name.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e190.json")
E = "tools/claims-v3/e190/"
R = "tools/claims-v3/e136/rgm136/"
SRC = [R + f for f in ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
                       "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")]
FILES = [E + f for f in ("run_e190.py", "e190_common.py", "session_e190.sh", "build_e190.sh", "check_e190.py", "preflight_e190.sh",
                         "ettelem_guard_e190.sh", "fake_card_e190.py", "plan-e190.json", "forecast-e190.json")] + [
    "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
    "tools/claims-v3/kinds/tiles/fp32/randn.bin", "tools/claims-v3/kinds/tiles/fp16/randn.bin", "tools/claims-v3/kinds/tiles/int8/full.bin"] + SRC


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make():
    return {"what": "E190's harness: every file a box runs or reads, at its sha256 (check_e190.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if "--make" in argv:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1)
        print(f"wrote harness-e190.json ({len(FILES)} files)")
        return 0
    if "--list" in argv:
        print("\n".join(FILES))
        return 0
    if "--check" in argv:
        old = json.load(open(HARNESS))
        same = old == make()
        print(f"harness-e190.json re-made: {'equal' if same else 'DIFFERS'} ({len(FILES)} files)")
        print("CHECK PASS" if same else "CHECK FAIL")
        return 0 if same else 1
    if "--box" in argv:
        h = json.load(open(HARNESS))["files"]
        want = {p: v for p, v in h.items() if ("--only-src" not in argv or p.startswith(R))}
        bad = []
        for p, v in sorted(want.items()):
            got = sha(p) if os.path.isfile(os.path.join(REPO, p)) else "missing"
            if got != v:
                bad.append(f"{p}: {got[:16]} (want {v[:16]})")
        if bad:
            print("HARNESS DIFFERS: " + "; ".join(bad))
            return 9
        print(f"HARNESS OK: {len(want)} files at harness-e190.json's sha256" + (" (rgm136's sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
