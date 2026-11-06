#!/usr/bin/env python3
"""run_hpl.py with kit v4's one-kernel option: the committed runner imported unchanged, the q142s watcher fix installed (as every
v3 kit installs it), then onekernel.install(), then run_hpl's own main() with the same arguments.

    python3 run_hpl_onekernel.py --protocol <protocol.json> --out <RUNDIR> [--dry] [--only BLOCK ...] [--root <tree>]

It writes <RUNDIR>/onekernel.json (both install records) before the session starts. Only --dry is exercised by this option's
files (drypass_onekernel.sh); a card session with it needs its own kit, registration, dmcmd_audit GO and readiness critic
(README.md, "Before a card uses it"). SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
sys.path.insert(0, HERE)
import run_hpl as H  # noqa: E402
import watcher_q142s as W  # noqa: E402
import onekernel as OK  # noqa: E402


def main():
    rec = {"watcher": W.install(H), "onekernel": OK.install(H)}
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if out:
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "onekernel.json"), "w") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
    return H.main()


if __name__ == "__main__":
    sys.exit(main())
