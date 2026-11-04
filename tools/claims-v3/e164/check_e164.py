#!/usr/bin/env python3
"""E164 (Q141(b); E157's check_e157.py, ported): refuse unless every reused file and every E164 card file is byte-identical to
harness-e164.json (card_code_unchanged_sha256, e164_card_files_sha256, pool_sha256) and, on the box, every binary the run executes is
byte-identical to harness.box_binaries_sha256 (E78's sparsity_host, the heater, and the lab's ettelem, the ones E142, E155, E156 and
E157 ran on this card; the kernel the power passes load, build/sparsity/kernel/sparsity.elf; and Q139(k)'s patched C-logging host,
build/ccheck/b/host/sparsity_host, built on aifoundry1 by tools/claims-v3/ccheck/build_host_ccheck.sh on Tue 3 Nov 2026 and run by
E157). A binary that differs or is missing stops the session; a rebuild needs a dated amendment re-pinning it before the claim.

    python3 -B tools/claims-v3/e164/check_e164.py [--root <tree top>] [--desk]    # exit 0 and "HARNESS OK", or exit 9 with each difference

--desk skips the binaries (the Intel has none). session_e164.sh runs it on the box before any device opens; the dry pass on the Intel
runs it with --desk. Standard library only.
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
    h = json.load(open(os.path.join(HERE, "harness-e164.json")))
    want = dict(h["card_code_unchanged_sha256"])
    want.update(h["e164_card_files_sha256"])
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
    if "--root" in sys.argv:
        top = sys.argv[sys.argv.index("--root") + 1]
    bad, n = check(top, box="--desk" not in sys.argv)
    if bad:
        print("HARNESS DIFFERS - refusing:\n  " + "\n  ".join(bad))
        sys.exit(9)
    print(f"HARNESS OK: {n} files match harness-e164.json" + (" (desk: binaries not checked)" if "--desk" in sys.argv else ""))


if __name__ == "__main__":
    main()
