#!/usr/bin/env python3
"""E128 runner (Q136): one pass on the local card. It is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 is checked against
predictions-e128.json first), with E128's items and order installed on the shared e78_common module (e128_common.install): E78's 51 kinds and the tie,
plus E128's tiles (e128/e128.json); each pass is the tie, three segments of E78's six anchors and a third of E128's tiles and E78's two ones, the tie.
A port of tools/claims-v3/signloc/run_e108.py.

    python3 tools/claims-v3/e128/run_e128.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP file, the tile check against
the registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's. Its log lines and configs.json still say "E78": that is the
unchanged code speaking.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e128_common as e128  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e128.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    e = e128.check_e128_json()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code or e128.json differs from E128's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e128.install()
    import run_e78  # noqa: E402  (after the check and the install)
    run_e78.main()


if __name__ == "__main__":
    main()
