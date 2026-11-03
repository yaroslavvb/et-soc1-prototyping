#!/usr/bin/env python3
"""E147 runner (Q138): one block of E147's fp32 single-bit trains (block A or B, e147_common.py) on the local card. It is
E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are
checked against predictions-e147.json first), with E147's items and orders installed on the shared e78_common module
(e147_common.install): E78's 51 kinds and the tie, plus E147's 73 tiles. A port of tools/claims-v3/e134/run_e134.py.

    python3 tools/claims-v3/e147/run_e147.py <out-dir> --root <tree root> ...     (every run_e78.py option)

A train is E78's runner with options it already has: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0 (block_e147.sh
passes them), as E102's and E134's trains. Everything else - `timeout 10` on every device process, the other-user test,
the STOP file, the die stop (--max-c), the tile check against the registered sha256 before anything opens the card
(exit 9), the records - is run_e78.py's. Nothing here opens the management node (run_e78.py reads the die temperature from
the block's sampler file).

THE STOPS READ LIVE SAMPLES. run_e78.py's reading() takes the newest line of --tel-live, which block_e147.sh points at
the sampler's own output file while it is being written ($OUT/telemetry.jsonl.raw: lib.sh's start_sampler writes there and
copies it to telemetry.jsonl only when the sampler stops), and stops the pass when that line is older than --stale-s (3 s).
The die stop reads that line's minion-shire reading; the board stop below wraps the same last_sample() call, so it reads the
same live line's board_w before every launch. (E139's 65 W stop watched telemetry.jsonl, written only at a pass's end, and
so never read a sample: E147's stops never read that file.)

E147 change, the stop test (README, "Stops"): with E147_STOPTEST=board the board stop's line is E147_STOPTEST_W (it must be
below 30 W), so it must fire at the first pre-launch reading, before any launch; block_e147.sh --stoptest board checks that
it did (exit 6, the STOP file's line, no run recorded). The die test needs no change here: block_e147.sh --stoptest die
passes --max-c 20. Neither is ever set in a block.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e147_common as e147  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e147.json")))
    bad = []
    for key in ("reused_unchanged_sha256", "e147_tiles_sha256"):
        for rel, want in reg["harness"][key].items():
            p = os.path.join(ROOT, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    if bad:
        print("refusing to run - the reused E78 code or E147's tiles differ from E147's freeze:\n  " + "\n  ".join(bad),
              file=sys.stderr)
        sys.exit(9)
    stop_w = reg["plan"]["board_power_stop_w"]
    if os.environ.get("E147_STOPTEST") == "board":                      # E147: the stop test only
        stop_w = float(os.environ.get("E147_STOPTEST_W", "1.0"))
        if not 0 < stop_w < 30:
            print(f"refusing: a stop-test line must be below 30 W (got {stop_w})", file=sys.stderr)
            sys.exit(2)
        print(f"E147 STOP TEST: board-power line {stop_w} W (registered {reg['plan']['board_power_stop_w']} W)",
              file=sys.stderr, flush=True)
    e147.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e147_common's path)
    guard_board_power(run_e78, stop_w)
    run_e78.main()


def guard_board_power(run_e78, stop_w, out_dir=None):
    """E147's board-power stop (README.md, "Stops"; E127's, E130's and E134's, unchanged): run_e78.py reads the newest LIVE
    telemetry line (--tel-live, the sampler's .raw file) through its module-level last_sample() before every launch; this
    wraps that function so that a line with board_w >= stop_w writes the pass's STOP file (which the host program and the
    runner watch) and ends the pass with run_e78's own EXIT_HOT (6). It changes nothing else: the line is returned as before.
    It logs the first line it reads (time, age, board_w), so every block's log shows that the stop read a live sample."""
    orig = run_e78.last_sample
    out_dir = out_dir or (sys.argv[1] if len(sys.argv) > 1 else ".")
    seen = {"n": 0}

    def guarded(path):
        s = orig(path)
        w = (s or {}).get("board_w")
        seen["n"] += 1
        if seen["n"] == 1:
            import time
            age = None if not s or "t_ms" not in s else round(time.time() - s["t_ms"] / 1000.0, 2)
            print(f"E147 board stop reads {os.path.basename(str(path))}: first line board_w {w} W, age {age} s, "
                  f"line {stop_w} W", file=sys.stderr, flush=True)
        if isinstance(w, (int, float)) and w >= stop_w:
            msg = f"E147 board-power stop: board_w {w} W >= {stop_w} W"
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
