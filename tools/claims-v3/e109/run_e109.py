#!/usr/bin/env python3
"""E109 runner (Q133): one pass of E109's arms on the local card. It is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256, and those of
e78_common.py and kinds.json, are checked against predictions-e109.json first), with E109's items and order installed on the shared e78_common module
(e109_common.install), as run_e107.py did for E107.

    python3 tools/claims-v3/e109/run_e109.py <out-dir> --root <tree root> ...     (every run_e78.py option; --sparsity is build/e109's binary, --heater E78's)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP file, the tile check against the
registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's. Its log lines and configs.json still say "E78": that is the unchanged
code speaking.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e109_common as e109  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e109.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    if bad:
        print("refusing to run - the reused E78 code differs from E109's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e109.install()
    import run_e78  # noqa: E402  (after the check and the install)
    run_e78.main()


if __name__ == "__main__":
    main()
