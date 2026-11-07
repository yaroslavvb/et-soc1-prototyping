#!/usr/bin/env python3
"""E182 (Q153, the kit; E178's check_e178.py, ported): refuse unless every reused file, every E182 card file, the registration's files, the
pinned watcher files and every tile E182 runs are byte-identical to harness-e182.json (card_code_unchanged_sha256, e182_card_files_sha256,
registration_sha256, watcher_sha256, tiles_sha256) and, on the box, every binary the run executes is byte-identical to
harness.box_binaries_sha256 (E178's four: E78's sparsity_host, the kernel, the C-logging host, ettelem). With the trains (the default),
also the train host: its patched source build/e182host/src/host/main.cpp equals harness.train_host_source_sha256, its build record
build/e182host/SHA256 names that source and the binary build/e182host/b/host/sparsity_host, and the binary hashes as that record says.

    python3 tools/claims-v3/e182/check_e182.py [--tree <top of the tree>] [--desk] [--no-trains]   # exit 0 "HARNESS OK", or exit 9

--desk (or V3_DRY set, a dry run that never opens a device) skips the binaries and the train host (the Intel has none). session_e182.sh
runs it on the box before any device opens. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = ("card_code_unchanged_sha256", "e182_card_files_sha256", "registration_sha256", "watcher_sha256", "tiles_sha256")
TRHOST = "build/e182host/b/host/sparsity_host"
TRSRC = "build/e182host/src/host/main.cpp"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(top, box=True, trains=True):
    h = json.load(open(os.path.join(HERE, "harness-e182.json")))
    want = {}
    for k in KEYS:
        want.update(h[k])
    if box:
        want.update(h["box_binaries_sha256"])
        if trains:
            want.update(h["train_host_source_sha256"])
    bad = []
    for rel, w in want.items():
        p = os.path.join(top, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != w:
            bad.append(f"{rel}: {have} != registered {w}")
    if box and trains:
        rec = os.path.join(top, "build/e182host/SHA256")
        got = {}
        if os.path.exists(rec):
            for line in open(rec):
                if line.strip():
                    hh, pth = line.split(None, 1)
                    got[os.path.relpath(pth.strip(), top) if os.path.isabs(pth.strip()) else pth.strip()] = hh
        if got.get(TRSRC) != h["train_host_source_sha256"][TRSRC]:
            bad.append(f"build/e182host/SHA256 does not record the registered patched source ({got.get(TRSRC)})")
        p = os.path.join(top, TRHOST)
        if not os.path.exists(p):
            bad.append(f"{TRHOST}: missing (build_host_e182.sh, the runbook's step 6)")
        elif got.get(TRHOST) != sha(p):
            bad.append(f"{TRHOST}: sha256 {sha(p)} is not its build record's {got.get(TRHOST)}")
        n_extra = 2
    else:
        n_extra = 0
    return bad, len(want) + n_extra


def main():
    top = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if "--tree" in sys.argv:
        top = sys.argv[sys.argv.index("--tree") + 1]
    desk = "--desk" in sys.argv or bool(os.environ.get("V3_DRY"))
    trains = "--no-trains" not in sys.argv
    bad, n = check(top, box=not desk, trains=trains)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} files match harness-e182.json" + (" (desk or dry run: binaries and the train host not checked)" if desk else "")
          + (" (the trains off: the train host not checked)" if not trains and not desk else ""))


if __name__ == "__main__":
    main()
