#!/usr/bin/env python3
"""E127 runner (Q136): one pass of E127's thirteen B-lane-gate tiles on the local card. It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are checked against
predictions-e127.json first), with E127's items and order installed on the shared e78_common module (e127_common.install):
E78's 51 kinds and the tie, plus E127's 13 tiles; each pass is the tie, three segments of E78's six anchors and a third of
the tiles, the tie (33 runs). A port of tools/claims-v3/e115/run_e115.py.

    python3 tools/claims-v3/e127/run_e127.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP
file, the tile check against the registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's.
Nothing here opens the management node (run_e78.py reads the die temperature from the block's sampler file). Its log lines
and configs.json still say "E78": that is the unchanged code speaking.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e127_common as e127  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e127.json")))
    bad = []
    for key in ("reused_unchanged_sha256", "e127_tiles_sha256"):
        for rel, want in reg["harness"][key].items():
            p = os.path.join(ROOT, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e127.check_frozen()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code, E127's tiles or Q133(b)'s frozen files differ from E127's freeze:\n  "
              + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e127.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e127_common's path)
    guard_board_power(run_e78, reg["plan"]["board_power_stop_w"])
    run_e78.main()


def guard_board_power(run_e78, stop_w, out_dir=None):
    """E127's board-power stop (README.md, "Stops"): run_e78.py reads the newest telemetry line through its module-level
    last_sample() before every launch and while it waits for the launch reading; this wraps that function so that a line
    with board_w >= stop_w writes the pass's STOP file (which the host program and the runner watch) and ends the pass with
    run_e78's own EXIT_HOT (6). It changes nothing else: the line is returned as before."""
    orig = run_e78.last_sample
    out_dir = out_dir or (sys.argv[1] if len(sys.argv) > 1 else ".")

    def guarded(path):
        s = orig(path)
        w = (s or {}).get("board_w")
        if isinstance(w, (int, float)) and w >= stop_w:
            msg = f"E127 board-power stop: board_w {w} W >= {stop_w} W"
            print(msg, file=sys.stderr, flush=True)
            try:
                open(os.path.join(out_dir, "STOP"), "a").write(msg + "\n")
            except OSError:
                pass
            sys.exit(run_e78.EXIT_HOT)
        return s

    run_e78.last_sample = guarded
    return guarded


if __name__ == "__main__":
    main()
