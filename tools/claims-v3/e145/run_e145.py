#!/usr/bin/env python3
"""E145 runner (Q138): one block of E138's int8 single-bit trains (B) or E130's (A) on aifoundry1 card 1. It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are checked against
predictions-e145.json first), with E145's items and orders installed on the shared e78_common module (e145_common.install: E78's
51 kinds and the tie, plus Q136(a)'s 26 tiles). A port of tools/claims-v3/e138/run_e138.py with E137's registered stops
(tools/claims-v3/e137/run_e137.py guard_stops, copied, with the sample's age recorded), each change marked E145:

  1. the stops read LIVE samples: run_e78.py reads the newest line of the block's running sampler file (--tel-live
     <pass>/telemetry.jsonl.raw, which lib.sh's start_sampler writes one line a sample while it runs) through its module-level
     last_sample() before every launch and every 0.1 s while it waits; this wraps that function so that a line with
     board_w >= the registered board stop, or any minion-shire reading >= the registered die stop, writes the pass's STOP file
     (which the host program and the runner watch) and ends the pass with run_e78's own EXIT_HOT (6). The message records the
     line's t_ms and its age when read, so a stop shows it read a live sample (E139's stop watched a file written only at the
     pass's end: never again);
  2. E145_STOPTEST=board|die (the stop-path test, block_e145.sh --stoptest; README.md "Stops"): the same guard with the board
     stop at 1.0 W or the die stop at 1.0 C, so it must fire on the first live line, before any launch.

    python3 tools/claims-v3/e145/run_e145.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Nothing here opens the management node: the readings come from the block's sampler file. Its log lines and configs.json still
say "E78": that is the unchanged code speaking.
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
import e145_common as e145  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir, tag="E145"):
    """E137's stops, copied (README.md, "Stops"), E145 change 1: a line with board_w >= board_stop_w or
    max(temp_c.minshire) >= die_stop_c writes <out>/STOP (with the line's t_ms and its age when read) and ends the pass
    with EXIT_HOT (6). The line is otherwise returned unchanged."""
    orig = run_e78.last_sample

    def guarded(path):
        s = orig(path)
        if not s:
            return s
        w = s.get("board_w")
        try:
            age = round(time.time() - float(s.get("t_ms")) / 1000.0, 3)
        except (TypeError, ValueError):
            age = None
        msg = None
        if isinstance(w, (int, float)) and w >= board_stop_w:
            msg = f"{tag} board-power stop: board_w {w} W >= {board_stop_w} W"
        try:
            ms = [float(x) for x in (s.get("temp_c") or {}).get("minshire") or []]
        except (TypeError, ValueError):
            ms = []
        if msg is None and ms and max(ms) >= die_stop_c:
            msg = f"{tag} die stop: hottest minion-shire reading {max(ms)} C >= {die_stop_c} C"
        if msg:
            msg += f" (sample t_ms {s.get('t_ms')}, read {age} s after it was taken, from {os.path.basename(path)})"
            print(msg, file=sys.stderr, flush=True)
            try:
                with open(os.path.join(out_dir, "STOP"), "a") as f:
                    f.write(msg + "\n")
            except OSError:
                pass
            sys.exit(run_e78.EXIT_HOT)
        return s

    run_e78.last_sample = guarded
    return guarded


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e145.json")))
    bad = []
    for key in ("reused_unchanged_sha256", "e145_tiles_sha256"):
        for rel, want in reg["harness"][key].items():
            p = os.path.join(ROOT, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e145.check_frozen()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code or Q136(a)'s tiles differ from E145's freeze:\n  " + "\n  ".join(bad),
              file=sys.stderr)
        sys.exit(9)
    e145.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e145_common's path)
    st = reg["plan"]["stops"]
    board_w, die_c = st["board_w"], st["die_hottest_shire_c"]
    test = os.environ.get("E145_STOPTEST", "")                                                  # E145 change 2
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test:
        print(f"E145_STOPTEST={test!r}: only 'board' or 'die'", file=sys.stderr)
        sys.exit(2)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir != "/dev/null":
        guard_stops(run_e78, board_w, die_c, out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
