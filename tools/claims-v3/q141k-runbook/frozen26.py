#!/usr/bin/env python3
"""Q141(k), go checklist step 3: predict_q140e's 26 frozen input hashes, checked by parsing its FROZEN table (never importing it,
so nothing of it runs), as Q141(f) re-hashed them. Desk only: reads files, sends nothing.

    /usr/bin/python3 -B tools/claims-v3/q141k-runbook/frozen26.py [<lab repo top>]

Prints "FROZEN 26 OK" and exits 0, or names each file that differs and exits 1. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import hashlib
import os
import sys

SRC = "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py"
WANT = 26


def main():
    top = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
    tree = ast.parse(open(os.path.join(top, SRC)).read())
    frozen = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FROZEN" for t in node.targets):
            frozen = ast.literal_eval(node.value)
    if not isinstance(frozen, dict):
        print(f"FROZEN not found in {SRC}")
        return 1
    bad = []
    for rel, want in frozen.items():
        p = os.path.join(top, rel)
        got = hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else None
        if got != want:
            bad.append(rel)
            print(f"DIFFERS {rel}")
    if len(frozen) != WANT:
        print(f"FROZEN holds {len(frozen)} entries, not {WANT}")
        return 1
    print(f"FROZEN {len(frozen) - len(bad)} OK" + (f", {len(bad)} differ" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
