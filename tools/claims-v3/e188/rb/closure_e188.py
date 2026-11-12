#!/usr/bin/env python3
"""E188 (Q165, the kit): a DESK-TEST helper of rb/selftest_rb_e188.sh only: the lab files E188's step 2 reads, found by running its Python
checks in this process under an audit hook (sys.addaudithook, the 'open' event) and listing every file they open inside the repository,
with every file the pinned lists and harness-e188.json name (check_history_e188.py paths). The runbook desk test copies exactly these
into its scratch repository, so step 2 runs there as committed (E185's day-2 closure was made the same way, by a run-time trace). It reads
files only and writes nothing; it runs no box command and opens no device.

    /usr/bin/python3 -B tools/claims-v3/e188/rb/closure_e188.py <repo>      (prints repo-relative paths, one a line, sorted)
SPDX-License-Identifier: Apache-2.0
"""
import io
import os
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
REPO = os.path.realpath(sys.argv[1])
SEEN = set()


def hook(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        p = os.fsdecode(args[0])
        rp = os.path.realpath(p if os.path.isabs(p) else os.path.join(os.getcwd(), p))
        if (rp + os.sep).startswith(REPO + os.sep) and os.path.isfile(rp):
            SEEN.add(os.path.relpath(rp, REPO))


RUNS = [("tools/claims-v3/e188/make_harness_e188.py", ["--check"]), ("tools/claims-v3/e188/e188_common.py", ["--verify"]),
        ("tools/claims-v3/e188/check_e188.py", ["--desk"]), ("tools/claims-v3/e182/check_inputs_e182.py", []),
        ("tools/claims-v3/e188/plan_e188.py", ["--root", ".", "--check"]), ("tools/claims-v3/e188/forecast_e188.py", ["--root", ".", "check"]),
        ("tools/claims-v3/e188/e188_stats.py", [])]


def main():
    os.chdir(REPO)
    sys.addaudithook(hook)
    out, err = sys.stdout, sys.stderr
    for rel, args in RUNS:
        sys.argv = [rel] + args
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            runpy.run_path(rel, run_name="__main__")
        except SystemExit:
            pass
        finally:
            sys.stdout, sys.stderr = out, err
        SEEN.add(rel)
    p = subprocess.run(["/usr/bin/python3", "-I", "-B", "tools/claims-v3/e188/rb/check_history_e188.py", "paths"], capture_output=True, text=True)
    for line in p.stdout.splitlines():
        q = line.strip()
        if q and os.path.isfile(os.path.join(REPO, q)):
            SEEN.add(q)
    for q in sorted(SEEN):
        print(q)


if __name__ == "__main__":
    main()
