#!/usr/bin/env python3
"""E163 (Q141; E153's check_e153.py, ported): refuse unless every reused file, every E163 card file, the registration files and the
pools' and re-runs' tiles are byte-identical to harness-e163.json (card_code_unchanged_sha256, e163_card_files_sha256,
registration_sha256, reused_e151_sha256, pool_sha256) and, on the box, every binary the run executes is byte-identical to
harness.box_binaries_sha256: E78's sparsity_host (the heater) and its kernel, the C-logging host build/ccheck/b/host/sparsity_host
(E153's, built on aifoundry3 from workloads/sparsity with tools/claims-v3/ccheck/patch_host_ccheck.py; it runs every measured launch),
the lab's ettelem.

    python3 tools/claims-v3/e163/check_e163.py [--tree <top of the tree>] [--desk]    # exit 0 and "HARNESS OK", or exit 9 with each difference

--desk (or V3_DRY set, a dry run that never opens a device) skips the binaries (the Intel has none). session_e163.sh runs it on the box
before any device opens. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ("card_code_unchanged_sha256", "e163_card_files_sha256", "registration_sha256", "reused_e151_sha256", "pool_sha256")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(top, box=True):
    h = json.load(open(os.path.join(HERE, "harness-e163.json")))
    want = {}
    for k in KEYS:
        want.update(h[k])
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
    desk = "--desk" in sys.argv or bool(os.environ.get("V3_DRY"))
    bad, n = check(top, box=not desk)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} files match harness-e163.json" + (" (desk or dry run: binaries not checked)" if desk else ""))


if __name__ == "__main__":
    main()
