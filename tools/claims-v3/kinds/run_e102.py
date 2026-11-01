#!/usr/bin/env python3
"""E102 runner (Q132): one pass (block G, T or I, e102_common.py) on the local card. It is E78's runner, run_e78.py, run UNCHANGED (its sha256 is
checked against predictions-e102.json first), with E102's items and orders installed on the shared e78_common module (e102_common.install).

    python3 tools/claims-v3/kinds/run_e102.py <out-dir> --root <tree root> ...     (every run_e78.py option)

A train (blocks T and I) is E78's runner with options it already has: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (block_e102.sh passes them).
Everything else - `timeout 10` on every device process, the other-user test, the STOP file, the tile check against the registered sha256 before anything
opens the card (exit 9), the records - is run_e78.py's. Its log lines and configs.json still say "E78": that is the unchanged code speaking.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e102_common as e102  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e102.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    e = e102.check_e102_json()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code or e102.json differs from E102's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e102.install()
    import run_e78  # noqa: E402  (after the check and the install)
    run_e78.main()


if __name__ == "__main__":
    main()
