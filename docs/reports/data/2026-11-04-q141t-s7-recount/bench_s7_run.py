#!/usr/bin/env python3
"""Q141(t): bench_s7.py's main(), unchanged (it is the registered driver, committed in 0830f65b), with one call made safe.

    python3 -B bench_s7_run.py <the same arguments as bench_s7.py>

bench_s7.py writes its run record with os.nice(0) (the driver's niceness). On the Intel on Wed 4 Nov 2026 that call raised
PermissionError (EPERM) after the 27-point run had finished: the session had reniced the driver from 0 to 20 while it ran, and
macOS's nice(0) then failed. run_kinds.py had already written its counts and exited 0, so only the run record was lost
(REGISTRATION.md.dated-note.md). Here os.nice(0) reads the process's priority with os.getpriority instead; every other step,
check and argument is bench_s7.py's own.
SPDX-License-Identifier: Apache-2.0
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_nice = os.nice


def _safe_nice(inc):
    if inc == 0:
        try:
            return os.getpriority(os.PRIO_PROCESS, 0)
        except OSError:
            return None
    return _nice(inc)


os.nice = _safe_nice
import bench_s7  # noqa: E402

if __name__ == "__main__":
    sys.argv[0] = bench_s7.__file__
    bench_s7.main()
