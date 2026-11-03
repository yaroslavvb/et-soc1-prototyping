#!/usr/bin/env python3
"""E151 runner (Q139): one block of E138's int8 single-bit trains (B) or E130's (A) on aifoundry3 card 0. It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are checked against
predictions-e151.json first), with E151's items and orders installed on the shared e78_common module (e151_common.install: E78's
51 kinds and the tie, plus Q136(a)'s 26 tiles). A port of tools/claims-v3/e145/run_e145.py (E145's design on card 1) with
tools/claims-v3/e141/run_e141.py's aifoundry3 stops (the field and the in-run watcher), each change marked E151:

  1. the stops read LIVE samples (E145's guard_stops, as E141 ported it): run_e78.py reads the newest line of the block's running
     sampler file (--tel-live <pass>/telemetry.jsonl.raw, which lib.sh's start_sampler writes one line a sample while it runs)
     through its module-level last_sample() before every launch and every 0.1 s while it waits; the wrapper ends the pass with
     run_e78's EXIT_HOT (6) and a STOP line when that line reads board_w >= the registered board stop (45 W) or the current
     minion-shire reading temp_c.minshire[0] >= the registered die stop (68 C). On aifoundry3 minshire[2] is a high-water latch
     (87 C in every sample of E138's and E140's blocks), so E145's field, the maximum of minshire, would stop every pass at once:
     E151 reads minshire[0], the field run_e78.py's own --max-c reads (E141 change 4). The STOP line records the sample's t_ms and
     its age when read;
  2. E141's in-run watcher, copied: a reading between runs cannot see a run's own peak (run_e78 blocks on the host program for the
     run's 4 s), so a daemon thread reads the same live file every 0.1 s for the whole pass, runs included, and on the same two
     stops writes the pass's STOP file (with the sample's t_ms and age). The host program checks that file before every launch of
     its --seconds loop (workloads/sparsity/host/main.cpp repeatFor), so a run ends within one launch; the main path then ends the
     pass with EXIT_HOT at its next reading. It opens nothing but the sampler's file;
  3. E151_STOPTEST=die|board|watch (the stop-path test, block_e151.sh --stoptest; README.md "Stops"): die and board run the guard
     with the die stop at 1.0 C or the board stop at 1.0 W, so it fires on the first live reading, before any launch; watch starts
     only the watcher with the board stop at 1.0 W and exits EXIT_HOT once it has written STOP (run_e78.main() is never called, so
     nothing launches).

    python3 tools/claims-v3/e151/run_e151.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Nothing here opens the management node: the readings come from the block's sampler file. Its log lines and configs.json still
say "E78": that is the unchanged code speaking.
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
import e151_common as e151  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)

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
    # E151 change 1 (E141's change 4): minshire[0], the current shire reading; minshire[2] is a constant latch on aifoundry3
    if msg is None and ms and ms[0] >= die_stop_c:
        msg = f"{tag} die stop: minion-shire reading minshire[0] {ms[0]} C >= {die_stop_c} C"
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


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir, tag="E151"):
    """E145's stops as E141 ported them (E151 change 1), plus the watcher's flag: a line with board_w >= board_stop_w or
    temp_c.minshire[0] >= die_stop_c writes <out>/STOP (with the line's t_ms and its age when read) and ends the pass with
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


def start_watcher(read_line, path, board_stop_w, die_stop_c, out_dir, every_s=0.1, tag="E151 watcher"):
    """E151 change 2 (E141's change 2): every `every_s` seconds read the newest line of the live sampler file at `path`
    (read_line is run_e78's original last_sample) and, on a registered stop, write <out>/STOP once and record it in TRIPPED.
    Returns the thread and an Event set after its first read."""
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

    t = threading.Thread(target=loop, name="e151-watcher", daemon=True)
    t.start()
    return t, first


def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    reg = json.load(open(os.path.join(HERE, "predictions-e151.json")))
    bad = []
    for key in ("card_code_unchanged_sha256", "e151_card_files_sha256", "e151_tiles_sha256"):
        for rel, want in reg["harness"][key].items():
            p = os.path.join(ROOT, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e151.check_frozen()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code, an E151 card file or Q136(a)'s tiles differ from E151's freeze:\n  "
              + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e151.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e151_common's path)
    st = reg["plan"]["stops"]
    board_w, die_c = st["board_w"], st["die_shire0_c"]
    wboard, wdie = board_w, die_c
    test = os.environ.get("E151_STOPTEST", "")                                                  # E151 change 3
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test == "watch":
        wboard = st["stoptest_board_w"]
    elif test:
        print(f"E151_STOPTEST={test!r}: only 'board', 'die' or 'watch'", file=sys.stderr)
        sys.exit(2)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir == "/dev/null" or "--list" in sys.argv:
        run_e78.main()
        return
    tel = _arg("--tel-live")
    dry = "--dry" in sys.argv or bool(os.environ.get("V3_DRY"))
    if tel and not dry:
        _, first = start_watcher(run_e78.last_sample, tel, wboard, wdie, out_dir)          # E151 change 2
        first.wait(5.0)
        if test == "watch":
            for _ in range(20):
                if TRIPPED:
                    break
                time.sleep(0.1)
            if TRIPPED:
                print(f"E151 stop-path test (watch): the watcher wrote STOP: {TRIPPED[0]}", file=sys.stderr, flush=True)
                sys.exit(run_e78.EXIT_HOT)
            print("E151 stop-path test (watch): the watcher did not fire within 2 s", file=sys.stderr, flush=True)
            sys.exit(1)
    elif test == "watch":
        print("E151 stop-path test (watch) needs --tel-live and no dry run", file=sys.stderr)
        sys.exit(1)
    guard_stops(run_e78, board_w, die_c, out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
