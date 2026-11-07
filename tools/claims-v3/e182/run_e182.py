#!/usr/bin/env python3
"""E182 runner (Q153, the kit): one kinds pass of E182's 24 one-number kinds on aifoundry3 card 0, the smoke's kinds items, a train's
opening and closing anchors (--items), or the stop-path test. It is E178's runner, tools/claims-v3/e178/run_e178.py, with the items module,
the registration files, the harness and the tags changed (E182; E182.md section 7, "Stops (E171's, unchanged; E178's)"), so it is E78's
runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are checked against
harness-e182.json first), with E182's items and its registered order (plan-e182.json) installed on the shared e78_common module
(e182_common.install). E178's three changes are kept as they were:

  1. the stops read LIVE samples: run_e78.py reads the newest line of the block's running sampler file (--tel-live
     <block>/telemetry.jsonl.raw) through its module-level last_sample() before every launch and every 0.1 s while it waits; the wrapper
     ends the pass with run_e78's EXIT_HOT (6) and a STOP line when that line reads board_w >= 65 W or temp_c.minshire[0] >= 70 C
     (e182_common.stops(); minshire[2] is a high-water latch on aifoundry3);
  2. the in-run watcher: a daemon thread reads the same live file every 0.1 s for the whole pass and on the same two stops writes the
     block's STOP file; the host program checks that file before every launch of its --seconds loop;
  3. E182_STOPTEST=die|board|watch (the stop-path test, block_e182.sh --stoptest), as E178's.

Its stop functions, the watcher and the harness check are also the train runner's (run_e182t.py imports them: check_line, write_stop,
start_watcher, last_sample, others_on_card, harness_problems, TRIPPED).

    /usr/bin/python3 tools/claims-v3/e182/run_e182.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Nothing here opens the management node: the readings come from the block's sampler file. Its log lines and configs.json still say
"E78": that is the unchanged code speaking.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys
import threading
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e182_common as e182  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)

TRIPPED = []          # set by the watcher; the guard reads it


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _check_line(s, board_stop_w, die_stop_c, tag, path):
    """The registered test on one telemetry line: the stop message, or None (E163's, E171's, copied)."""
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
    # aifoundry3's minshire[2] is a constant high-water latch: read minshire[0], the current shire reading, which run_e78.py's own
    # --max-c stop reads
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


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir, tag="E182"):
    """E153's guard, copied: a line with board_w >= board_stop_w or temp_c.minshire[0] >= die_stop_c writes <out>/STOP (with the line's
    t_ms and its age when read) and ends the pass with EXIT_HOT (6); so does a stop the watcher has already written."""
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


def start_watcher(read_line, path, board_stop_w, die_stop_c, out_dir, every_s=0.1, tag="E182 watcher"):
    """E153's in-run watcher, copied: every `every_s` seconds read the newest line of the live sampler file and, on a registered stop,
    write <out>/STOP once and record it in TRIPPED. Returns the thread and an Event set after its first read."""
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

    t = threading.Thread(target=loop, name="e182-watcher", daemon=True)
    t.start()
    return t, first


def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def harness_problems():
    """every reused file, every E182 card file, the registration's files and the watcher files against harness-e182.json, and the
    registration's own hash list (e182_common.check_frozen): [] when all match"""
    har = json.load(open(os.path.join(HERE, "harness-e182.json")))
    bad = []
    for key in ("card_code_unchanged_sha256", "e182_card_files_sha256", "registration_sha256", "watcher_sha256"):
        for rel, want in har[key].items():
            p = os.path.join(TOP, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e182.check_frozen()
    if e:
        bad.append(e)
    return bad


# the train runner's names for the shared pieces (E182)
check_line = _check_line
write_stop = _write_stop


def last_sample(path):
    sys.path.insert(0, e182.KINDS)
    import run_e78  # noqa: E402
    return run_e78.last_sample(path)


def others_on_card():
    import run_e78  # noqa: E402
    dev_n = os.environ.get("ET_DEVICES")
    return run_e78.others_on_card(int(dev_n) if dev_n not in (None, "") else None)


def main():
    bad = harness_problems()
    if bad:
        print("refusing to run - the reused E78 code, an E182 card file, the registration, the watcher files or the registration's "
              "frozen files differ from E182's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e182.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e182_common's path)
    st = e182.stops()
    first = _arg("--first-block")
    kind = e182.block_kind(first) if first and first.isdigit() else "S"
    board_w, die_c = st["board_w"], st["die_shire0_c"]
    wboard, wdie = board_w, die_c
    test = os.environ.get("E182_STOPTEST", "")
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test == "watch":
        wboard = st["stoptest_board_w"]
    elif test:
        print(f"E182_STOPTEST={test!r}: only 'board', 'die' or 'watch'", file=sys.stderr)
        sys.exit(2)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir == "/dev/null" or "--list" in sys.argv:
        run_e78.main()
        return
    print(f"E182 runner: block {first} ({kind}), stops board {board_w} W / die {die_c} C (watcher {wboard} W / {wdie} C)",
          file=sys.stderr, flush=True)
    tel = _arg("--tel-live")
    dry = "--dry" in sys.argv or bool(os.environ.get("V3_DRY"))
    if tel and not dry:
        _, ev = start_watcher(run_e78.last_sample, tel, wboard, wdie, out_dir)
        ev.wait(5.0)
        if test == "watch":
            for _ in range(20):
                if TRIPPED:
                    break
                time.sleep(0.1)
            if TRIPPED:
                print(f"E182 stop-path test (watch): the watcher wrote STOP: {TRIPPED[0]}", file=sys.stderr, flush=True)
                sys.exit(run_e78.EXIT_HOT)
            print("E182 stop-path test (watch): the watcher did not fire within 2 s", file=sys.stderr, flush=True)
            sys.exit(1)
    elif test == "watch":
        print("E182 stop-path test (watch) needs --tel-live and no dry run", file=sys.stderr)
        sys.exit(1)
    guard_stops(run_e78, board_w, die_c, out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
