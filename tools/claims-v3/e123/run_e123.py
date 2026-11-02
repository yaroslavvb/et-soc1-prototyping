#!/usr/bin/env python3
"""E123 runner (Q134): one pass of the dagger rows' spread on the local card (aifoundry3). It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 is checked against predictions-e123.json first), with E123's
items and order installed on the shared e78_common module (e123_common.install): E78's 51 kinds and the tie, plus E123's
forty-two draws (e123.json); each pass is the tie, three segments of E78's six anchors and 18 of the 54 E123 items, the tie
(74 runs). A port of tools/claims-v3/kinds/run_e94.py.

    python3 tools/claims-v3/e123/run_e123.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test,
the STOP file, the tile check against the registered sha256 before anything opens the card (exit 9), the records -
is run_e78.py's. Its log lines and configs.json still say "E78": that is the unchanged code speaking.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e123_common as e123  # noqa: E402  (it puts tools/claims-v3/kinds on sys.path for e78_common and run_e78)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e123.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    e = e123.check_e123_json()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code or e123.json differs from E123's freeze:\n  " + "\n  ".join(bad),
              file=sys.stderr)
        sys.exit(9)
    e123.install()
    import run_e78  # noqa: E402  (after the check and the install)
    run_e78.main()


if __name__ == "__main__":
    main()
