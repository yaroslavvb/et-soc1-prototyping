#!/usr/bin/env python3
"""E148 runner (Q138): one pass of E148's arms on aifoundry1 card 1. It is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED, with E148's
items and order installed on the shared e78_common module (e148_common.install), as run_e129.py did for E129 this morning. Before anything is installed
it runs check_e148.py's check (every reused file, and on the box every binary, byte-identical to predictions-e148.json), exit 9 on a difference.
To E129's runner it adds E142's live stops, copied from tools/claims-v3/e142/run_e142.py (which ran on this card at 20:50-21:36 PST today), each
change marked E148:

  1. the stops read LIVE samples (E145's guard_stops as E142 copied it): run_e78.py reads the newest line of the block's running sampler file
     (--tel-live <pass>/telemetry.jsonl.raw, which lib.sh's start_sampler writes one line a sample while it runs) through its module-level
     last_sample() before every launch and every 0.1 s while it waits; the wrapper ends the pass with run_e78's EXIT_HOT (6) and a STOP line when
     that line reads board_w >= the registered board stop or any minion-shire field >= the registered die stop (predictions-e148.json > plan.stops);
  2. E142's in-run watcher: a daemon thread reads the same live file every 0.1 s for the whole pass, runs included, and on the same two stops writes
     the pass's STOP file, which the host program checks before every launch of its --seconds loop, so a run ends within one launch;
  3. E148_STOPTEST=die|board|watch (block_e148.sh --stoptest): die and board run the guard with the die stop at 1.0 C or the board stop at 1.0 W, so it
     fires on the first live reading, before any launch; watch starts only the watcher with the board stop at 1.0 W and exits EXIT_HOT once it has
     written STOP (run_e78.main() is never called, so nothing launches).

    python3 tools/claims-v3/e148/run_e148.py <out-dir> --root <tree root> ...     (every run_e78.py option; --sparsity is build/e109's binary)

Everything else - the launch reading, the quiet rule, `timeout 10` on every device process, the other-user test, the STOP file, the tile check against
the registered sha256 before anything opens the card (exit 9), the records - is run_e78.py's. Its log lines and configs.json still say "E78": that is
the unchanged code speaking. Nothing here opens the management node: the readings come from the block's sampler file.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import check_e148  # noqa: E402
import e148_common as e148  # noqa: E402

TRIPPED = []          # set by the watcher; the guard reads it


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _check_line(s, board_stop_w, die_stop_c, tag, path):
    """The registered test on one telemetry line: the stop message, or None."""
    if not s:
        return None
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
    return msg


def _write_stop(out_dir, msg):
    print(msg, file=sys.stderr, flush=True)
    try:
        with open(os.path.join(out_dir, "STOP"), "a") as f:
            f.write(msg + "\n")
    except OSError:
        pass


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir, tag="E148"):
    """E145's stops as E142 copied them (E148 change 1), plus the watcher's flag: a line with board_w >= board_stop_w or
    max(temp_c.minshire) >= die_stop_c writes <out>/STOP (with the line's t_ms and its age when read) and ends the pass with
    EXIT_HOT (6); so does a stop the watcher has already written. The line is otherwise returned unchanged."""
    orig = run_e78.last_sample

    def guarded(path):
        if TRIPPED:
            print(f"{tag}: the in-run watcher wrote STOP ({TRIPPED[0][:160]}): ending the pass", file=sys.stderr, flush=True)
            sys.exit(run_e78.EXIT_HOT)
        s = orig(path)
        msg = _check_line(s, board_stop_w, die_stop_c, tag, path)
        if msg:
            _write_stop(out_dir, msg)
            sys.exit(run_e78.EXIT_HOT)
        return s

    run_e78.last_sample = guarded
    return guarded


def start_watcher(read_line, path, board_stop_w, die_stop_c, out_dir, every_s=0.1, tag="E148 watcher"):
    """E148 change 2 (E142's change 2): every `every_s` seconds read the newest line of the live sampler file at `path` (read_line is run_e78's
    original last_sample) and, on a registered stop, write <out>/STOP once and record it in TRIPPED. Returns the thread and
    an Event set after its first read."""
    first = threading.Event()

    def loop():
        while True:
            try:
                msg = _check_line(read_line(path), board_stop_w, die_stop_c, tag, path)
            except Exception as ex:          # a bad line never kills the watcher
                msg = None
                print(f"{tag}: read error {ex!r}", file=sys.stderr, flush=True)
            if msg and not TRIPPED:
                TRIPPED.append(msg)
                _write_stop(out_dir, msg)
            first.set()
            time.sleep(every_s)

    t = threading.Thread(target=loop, name="e148-watcher", daemon=True)
    t.start()
    return t, first


def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    bad, _ = check_e148.check(ROOT, box=not os.environ.get("E148_DESK"))      # E148_DESK=1 only for a dry run on the Intel, which has no binaries
    if bad:
        print("refusing to run - E148's harness differs from its freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    reg = json.load(open(os.path.join(HERE, "predictions-e148.json")))
    e148.install()
    import run_e78  # noqa: E402  (after the check and the install)
    st = reg["plan"]["stops"]
    board_w, die_c = st["board_w"], st["die_hottest_shire_c"]
    wboard, wdie = board_w, die_c
    test = os.environ.get("E148_STOPTEST", "")                                                  # E148 change 3
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test == "watch":
        wboard = st["stoptest_board_w"]
    elif test:
        print(f"E148_STOPTEST={test!r}: only 'board', 'die' or 'watch'", file=sys.stderr)
        sys.exit(2)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir == "/dev/null" or "--list" in sys.argv:
        run_e78.main()
        return
    tel = _arg("--tel-live")
    dry = "--dry" in sys.argv or bool(os.environ.get("V3_DRY"))
    if tel and not dry:
        _, first = start_watcher(run_e78.last_sample, tel, wboard, wdie, out_dir)          # E148 change 2
        first.wait(5.0)
        if test == "watch":
            for _ in range(20):
                if TRIPPED:
                    break
                time.sleep(0.1)
            if TRIPPED:
                print(f"E148 stop-path test (watch): the watcher wrote STOP: {TRIPPED[0]}", file=sys.stderr, flush=True)
                sys.exit(run_e78.EXIT_HOT)
            print("E148 stop-path test (watch): the watcher did not fire within 2 s", file=sys.stderr, flush=True)
            sys.exit(1)
    elif test == "watch":
        print("E148 stop-path test (watch) needs --tel-live and no dry run", file=sys.stderr)
        sys.exit(1)
    guard_stops(run_e78, board_w, die_c, out_dir)                                              # E148 change 1
    run_e78.main()


if __name__ == "__main__":
    main()
