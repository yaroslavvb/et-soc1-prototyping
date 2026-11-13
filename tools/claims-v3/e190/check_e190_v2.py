#!/usr/bin/env python3
"""E190's harness v2 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): check_e190.py (the kit,
unchanged beside it, with harness-e190.json) for the files a box runs or reads under note 1: the v2 runner, its note-1 module, the v2
wrapper, the v2 build, this check, the v2 preflight, the v2 doubles (the box's dry pass v2 runs them), and every v1 file they still use
(the common module, the guard, the registration's plan and forecast, the device-command checker and its table, E136's rgm136 sources, the
three tiles). Python's own modules only.

    python3 -B tools/claims-v3/e190/check_e190_v2.py --make            writes harness-e190-v2.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e190/check_e190_v2.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e190/check_e190_v2.py --box [--only-src]
                    on a box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the ten rgm136 sources
                    only (build_e190_v2.sh's first check)
    python3 -B tools/claims-v3/e190/check_e190_v2.py --list            the paths, one a line (step 5 v2's sync list)
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e190-v2.json")
E = "tools/claims-v3/e190/"
R = "tools/claims-v3/e136/rgm136/"
SRC = [R + f for f in ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
                       "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")]
FILES = [E + f for f in ("run_e190_v2.py", "e190_note1.py", "e190_common.py", "session_e190_v2.sh", "build_e190_v2.sh", "check_e190_v2.py",
                         "preflight_e190_v2.sh", "ettelem_guard_e190.sh", "fake_card_e190_v2.py", "plan-e190.json", "forecast-e190.json")] + [
    "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
    "tools/claims-v3/kinds/tiles/fp32/randn.bin", "tools/claims-v3/kinds/tiles/fp16/randn.bin", "tools/claims-v3/kinds/tiles/int8/full.bin"] + SRC


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make():
    return {"what": "E190's harness v2 (note 1): every file a box runs or reads, at its sha256 (check_e190_v2.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if "--make" in argv:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1)
        print(f"wrote harness-e190-v2.json ({len(FILES)} files)")
        return 0
    if "--list" in argv:
        print("\n".join(FILES))
        return 0
    if "--check" in argv:
        old = json.load(open(HARNESS))
        same = old == make()
        print(f"harness-e190-v2.json re-made: {'equal' if same else 'DIFFERS'} ({len(FILES)} files)")
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
        print(f"HARNESS OK: {len(want)} files at harness-e190-v2.json's sha256" + (" (rgm136's sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
