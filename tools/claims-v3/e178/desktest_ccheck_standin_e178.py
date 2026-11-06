#!/usr/bin/env python3
"""E178 (Q146, the kit): the desk test's stand-in for `ccheck.py check` inside collect_e178.sh (selftest_collect_e178.py only; the card day
never runs it). It writes, as the check's --out, a prepared file of verdicts that tools/claims-v3/ccheck/ccheck.py itself wrote for the
same launches: E171's committed check of C (docs/reports/data/2026-11-05-e171-blind8-aifoundry3/ccheck/ccheck-all.json), with each verdict's
"log" field renamed to the relabelled session's name. Nothing is recomputed and no verdict is changed. It refuses unless E178_DESKTEST=1.

    E178_DESKTEST=1 E178_DESKTEST_VERDICTS=<prepared json> python3 desktest_ccheck_standin_e178.py check <log> ... --out <json> [--jobs N]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True


def main(argv):
    if os.environ.get("E178_DESKTEST") != "1":
        print("refusing: the check-of-C stand-in runs only in the desk test (E178_DESKTEST=1)")
        return 10
    if not argv or argv[0] != "check" or "--out" not in argv:
        print("usage: check <log> ... --out <json>")
        return 2
    out = argv[argv.index("--out") + 1]
    src = os.environ["E178_DESKTEST_VERDICTS"]
    shutil.copyfile(src, out)
    d = json.load(open(out))
    s = d["summary"]
    print(f"DESK-TEST STAND-IN: wrote {len(d['launches'])} verdicts ccheck.py wrote for E171's launches, relabelled; "
          f"PASS {s.get('PASS')} of {s.get('launches')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
