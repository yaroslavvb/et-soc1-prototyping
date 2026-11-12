#!/usr/bin/env python3
"""E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the harness check, v2, on the box and at
the desk. It reads files, never the card.

    python3 -B tools/claims-v3/e183/harness_e183_v2.py [--binaries]

1. harness-e183.json (v1's harness, cc597bf2) is at the sha256 harness-e183-v2.json pins for it, so v1's pins cannot be swapped;
2. v1's own check, check_e183.py's harness() imported and called unchanged: every one of v1's 80 box files and every image at its sha256,
   and with --binaries the train host's build (BUILD-E183.json, its two binaries, the patched main.cpp's pin and the 38-file build tree);
3. note 4's box files (harness-e183-v2.json "files": the train change's check, build v2, block v2, queue v2, session v2, preflight v2 and
   this file) each at its sha256.
Prints "HARNESS OK: <n> files (v1's check: <its own line>; note 4's <k> box files at their pins)" or "HARNESS FAULTS: ..."; exit 1 on any.
Run by session_e183_v2.sh (with --binaries, before any device opens), block_e183_v2.sh's preflight, rb/s08_a3_build_e183_v2.sh's wait
(with --binaries) and rb/s03_desk_e183_v5.sh (without). Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import contextlib
import hashlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import check_e183 as C1  # noqa: E402  (v1's checks, unchanged)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    args = sys.argv[1:]
    if args not in ([], ["--binaries"]):
        print(__doc__)
        return 2
    binaries = args == ["--binaries"]
    h2 = json.load(open(os.path.join(HERE, "harness-e183-v2.json")))
    bad = []
    v1 = os.path.join(ROOT, h2["harness_v1"]["path"])
    if not os.path.exists(v1) or sha(v1) != h2["harness_v1"]["sha256"]:
        bad.append(f"{h2['harness_v1']['path']} is not the v1 harness note 4 pinned")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc1 = C1.harness(binaries, ROOT)
    line1 = (buf.getvalue().strip().splitlines() or ["(v1's check printed nothing)"])[-1]
    if rc1 != 0 or not line1.startswith("HARNESS OK: "):
        bad.append(f"v1's check: {line1}")
    n1 = 0
    if line1.startswith("HARNESS OK: "):
        n1 = int(line1.split()[2])
    k = 0
    for rel, want in sorted(h2["files"].items()):
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
    print(f"HARNESS OK: {n1 + k} files (v1's check: {line1}; note 4's {k} box files at their pins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
