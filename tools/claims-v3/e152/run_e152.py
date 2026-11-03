#!/usr/bin/env python3
"""E152 runner (Q139): one pass of E152's eleven gate-dose tiles on the local card. It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are checked against
predictions-e152.json first), with E152's items and order installed on the shared e78_common module (e152_common.install):
E78's 51 kinds and the tie, plus E152's 11 tiles; each pass is the tie, three segments of E78's six anchors and a third of
the tiles, the tie (31 runs). A port of tools/claims-v3/e127/run_e127.py, with E147's live-sample log and stop test.

    python3 tools/claims-v3/e152/run_e152.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP
file, the tile check against the registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's.
Nothing here opens the management node (run_e78.py reads the die temperature from the block's sampler file). Its log lines
and configs.json still say "E78": that is the unchanged code speaking.

THE STOPS READ LIVE SAMPLES (E147's design). run_e78.py's reading() takes the newest line of --tel-live, which block_e152.sh
points at the sampler's own output while it is being written ($OUT/telemetry.jsonl.raw; lib.sh copies it to telemetry.jsonl
only when the sampler stops), before every launch, and stops the pass when that line is older than 3 s. The die stop reads
that line's minion-shire reading; the board stop below wraps the same last_sample() call, so it reads the same live line's
board_w, and it logs the first line it reads (its age and board watts) in the block's runner.err.

E152's stop test (README, "Stops"): with E152_STOPTEST=board the board stop's line is E152_STOPTEST_W (it must be below
30 W), so it must fire at the first pre-launch reading, before any launch; block_e152.sh --stoptest board checks that it did
(exit 6, the STOP file's line, no run recorded, a first line at most 3 s old). The die test needs no change here:
block_e152.sh --stoptest die passes --max-c 20. Neither is ever set in a pass.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e152_common as e152  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e152.json")))
    bad = []
    for key in ("reused_unchanged_sha256", "e152_tiles_sha256"):
        for rel, want in reg["harness"][key].items():
            p = os.path.join(ROOT, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e152.check_frozen()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code, E152's tiles or E127's bridge tiles differ from E152's freeze:\n  "
              + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    stop_w = reg["plan"]["board_power_stop_w"]
    if os.environ.get("E152_STOPTEST") == "board":                      # E152: the stop test only
        stop_w = float(os.environ.get("E152_STOPTEST_W", "1.0"))
        if not 0 < stop_w < 30:
            print(f"refusing: a stop-test line must be below 30 W (got {stop_w})", file=sys.stderr)
            sys.exit(2)
        print(f"E152 STOP TEST: board-power line {stop_w} W (registered {reg['plan']['board_power_stop_w']} W)",
              file=sys.stderr, flush=True)
    e152.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e152_common's path)
    guard_board_power(run_e78, stop_w)
    run_e78.main()


def guard_board_power(run_e78, stop_w, out_dir=None):
    """E152's board-power stop (E127's and E147's, unchanged but for the label): run_e78.py reads the newest LIVE telemetry
    line (--tel-live, the sampler's .raw file) through its module-level last_sample() before every launch; this wraps that
    function so that a line with board_w >= stop_w writes the pass's STOP file (which the host program and the runner watch)
    and ends the pass with run_e78's own EXIT_HOT (6). It changes nothing else: the line is returned as before. It logs the
    first line it reads (age, board_w), so every block's log shows that the stop read a live sample."""
    orig = run_e78.last_sample
    out_dir = out_dir or (sys.argv[1] if len(sys.argv) > 1 else ".")
    seen = {"n": 0}

    def guarded(path):
        s = orig(path)
        w = (s or {}).get("board_w")
        seen["n"] += 1
        if seen["n"] == 1:
            age = None if not s or "t_ms" not in s else round(time.time() - s["t_ms"] / 1000.0, 2)
            print(f"E152 board stop reads {os.path.basename(str(path))}: first line board_w {w} W, age {age} s, "
                  f"line {stop_w} W", file=sys.stderr, flush=True)
        if isinstance(w, (int, float)) and w >= stop_w:
            msg = f"E152 board-power stop: board_w {w} W >= {stop_w} W"
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
