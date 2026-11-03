#!/usr/bin/env python3
"""E156 runner (Q139): one pass of E156's items on aifoundry1 card 1. It is E139's runner, tools/claims-v3/runitems.py, run UNCHANGED (E139 ran
it through E75's mf/block.sh), with the live-sample stops E155 ran on this card (tools/claims-v3/e155/run_e155.py, E142's and E148's before it)
installed around it. Before anything is installed it runs check_e156.py's check (every reused file, and on the box every binary, byte-identical
to predictions-e156.json > harness), exit 9 on a difference. The changes, marked E156:

  1. the stops read LIVE samples: runitems.py reads the newest line of the block's running sampler file (--tel-live <pass>/telemetry.jsonl.raw,
     which lib.sh's start_sampler writes one line a sample while it runs) through its module-level last_sample() before every launch and every
     0.1 s while it waits for the launch reading; the wrapper ends the pass with runitems' EXIT_HOT (6) and a STOP line when that line reads
     board_w >= the registered board stop or any minion-shire field >= the registered die stop, or is >= stale_line_s old when read
     (predictions-e156.json > plan.stops). E139's board watcher read the closed telemetry.jsonl and so never saw a sample (E139's C1): this
     reads the .raw file the sampler is writing;
  2. E142's in-run watcher: a daemon thread reads the same live file every 0.1 s for the whole pass, runs included, and on the same stops writes
     the pass's STOP file. The heater and the drift anchor (sparsity_host) check it before every launch of their --seconds loop, so they end
     within one 0.4 s launch; enercat_host has no stop file, so a memory run ends within its 4 s (timeout 10) and runitems.py, which checks
     the STOP file before every item, ends the pass (exit 8) or the guard does (exit 6);
  3. E156_STOPTEST=die|board|watch|stale (block_e156.sh --stoptest): die and board run the guard with the die stop at 1.0 C or the board stop at
     1.0 W, and stale with the stale limit at 0.0 s, so each fires on the first live reading, before any launch; watch starts only the watcher
     with the board stop at 1.0 W and exits EXIT_HOT once it has written STOP (runitems.main() is never called, so nothing launches).

Everything else - the approach protocol, the shuffled order, the drift anchor, timeout 10 on every device process, the other-user test, the
STOP file, the records - is runitems.py's. Nothing here opens the management node: the readings come from the block's sampler file.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import check_e156  # noqa: E402

TRIPPED = []          # set by the watcher; the guard reads it


def _check_line(s, board_stop_w, die_stop_c, tag, path, stale_s=None):
    """The registered test on one telemetry line (E155's, unchanged): the stop message, or None."""
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
    if msg is None and stale_s is not None and (age is None or age >= stale_s):
        msg = f"{tag} stale-line stop: the newest sampler line is {age} s old >= {stale_s} s"
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


def guard_stops(mod, board_stop_w, die_stop_c, out_dir, tag="E156", stale_s=None):
    orig = mod.last_sample

    def guarded(path):
        if TRIPPED:
            print(f"{tag}: the in-run watcher wrote STOP ({TRIPPED[0][:160]}): ending the pass", file=sys.stderr, flush=True)
            sys.exit(mod.EXIT_HOT)
        s = orig(path)
        msg = _check_line(s, board_stop_w, die_stop_c, tag, path, stale_s)
        if msg:
            _write_stop(out_dir, msg)
            sys.exit(mod.EXIT_HOT)
        return s

    mod.last_sample = guarded
    return guarded


def start_watcher(read_line, path, board_stop_w, die_stop_c, out_dir, every_s=0.1, tag="E156 watcher", stale_s=None):
    first = threading.Event()

    def loop():
        while True:
            try:
                msg = _check_line(read_line(path), board_stop_w, die_stop_c, tag, path, stale_s)
            except Exception as ex:          # a bad line never kills the watcher
                msg = None
                print(f"{tag}: read error {ex!r}", file=sys.stderr, flush=True)
            if msg and not TRIPPED:
                TRIPPED.append(msg)
                _write_stop(out_dir, msg)
            first.set()
            time.sleep(every_s)

    t = threading.Thread(target=loop, name="e156-watcher", daemon=True)
    t.start()
    return t, first


def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    bad, _ = check_e156.check(ROOT, box=not os.environ.get("E156_DESK"))      # E156_DESK=1 only for a dry run on the Intel, which has no binaries
    if bad:
        print("refusing to run - E156's harness differs from its freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    reg = json.load(open(os.path.join(HERE, "predictions-e156.json")))
    import runitems  # noqa: E402  (after the check)
    st = reg["plan"]["stops"]
    board_w, die_c, stale_s = st["board_w"], st["die_hottest_shire_c"], st["stale_line_s"]
    wboard, wdie = board_w, die_c
    test = os.environ.get("E156_STOPTEST", "")                                                  # E156 change 3
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test == "stale":
        stale_s = st["stoptest_stale_s"]
    elif test == "watch":
        wboard = st["stoptest_board_w"]
    elif test:
        print(f"E156_STOPTEST={test!r}: only 'board', 'die', 'stale' or 'watch'", file=sys.stderr)
        sys.exit(2)
    sys.argv = [os.path.join(HERE, "..", "runitems.py")] + sys.argv[1:]
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir == "/dev/null" or "--list" in sys.argv:
        runitems.main()
        return
    tel = _arg("--tel-live")
    dry = "--dry" in sys.argv or bool(os.environ.get("V3_DRY"))
    os.makedirs(out_dir, exist_ok=True)
    if tel and not dry:
        _, first = start_watcher(runitems.last_sample, tel, wboard, wdie, out_dir, stale_s=st["stale_line_s"])          # E156 change 2
        first.wait(5.0)
        if test == "watch":
            for _ in range(20):
                if TRIPPED:
                    break
                time.sleep(0.1)
            if TRIPPED:
                print(f"E156 stop-path test (watch): the watcher wrote STOP: {TRIPPED[0]}", file=sys.stderr, flush=True)
                sys.exit(runitems.EXIT_HOT)
            print("E156 stop-path test (watch): the watcher did not fire within 2 s", file=sys.stderr, flush=True)
            sys.exit(1)
    elif test == "watch":
        print("E156 stop-path test (watch) needs --tel-live and no dry run", file=sys.stderr)
        sys.exit(1)
    guard_stops(runitems, board_w, die_c, out_dir, stale_s=None if dry else stale_s)            # E156 change 1
    runitems.main()


if __name__ == "__main__":
    main()
