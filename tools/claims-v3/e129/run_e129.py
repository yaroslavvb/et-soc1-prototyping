#!/usr/bin/env python3
"""E129 runner (Q136): one pass of E129's arms on the local card. It is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED, with E129's items
and order installed on the shared e78_common module (e129_common.install), as run_e109.py did for E109. Before anything is installed it runs
check_e129.py's check (every reused file, and on the box every binary, byte-identical to predictions-e129.json), exit 9 on a difference.

    python3 tools/claims-v3/e129/run_e129.py <out-dir> --root <tree root> ...     (every run_e78.py option; --sparsity is build/e109's binary, --heater E78's)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP file, the tile check against the
registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's. Its log lines and configs.json still say "E78": that is the
unchanged code speaking. run_e78.py opens no management node: its die reading comes from the block's sampler file (--tel-live).
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import check_e129  # noqa: E402
import e129_common as e129  # noqa: E402


def main():
    bad, _ = check_e129.check(ROOT, box=not os.environ.get("E129_DESK"))      # E129_DESK=1 only for a dry run on the Intel, which has no binaries
    if bad:
        print("refusing to run - E129's harness differs from its freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e129.install()
    import run_e78  # noqa: E402  (after the check and the install)
    run_e78.main()


if __name__ == "__main__":
    main()
