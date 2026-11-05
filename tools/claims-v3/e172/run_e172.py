#!/usr/bin/env python3
"""E172 runner (Q142(k6)): one pass of blind pool 8 on aifoundry1 card 1, or the smoke or the stop-path test, every launch's C logged. It
is E164's runner, tools/claims-v3/e164/run_e164.py, with E172's registration files, items module and tags (E172; E172.md, "The session
plan"), so it is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 and those of the rest of E78's card code are
checked against harness-e172.json first), with E172's items and order installed on the shared e78_common module (e172_common.install:
E78's 51 kinds and the tie, plus pool 8's 64 tiles; a pass is the tie, three segments of E78's six anchors and a third of the 64, the tie:
84 runs). E164's (E142's and E157's) changes are kept unchanged:
  1. E172_STOPTEST=die|board|watch (the stop-path test, block_e172.sh --stoptest); the stops are read from plan-e172.json > plan.stops
     (E164's: board 66 W, a minion-shire field 72 C; the stop-path test's 1.0 W and 1.0 C);
  2. the hashes it checks are harness-e172.json's (card_code_unchanged_sha256, e172_card_files_sha256, registration_sha256,
     watcher_sha256), with pool 8's frozen files through e172_common's own check.

    python3 tools/claims-v3/e172/run_e172.py <out-dir> --root <tree top> ...     (every run_e78.py option)

E142's notes hold: the stops read LIVE samples (the newest line of the block's running sampler file, before every launch and every
0.1 s while waiting, E145's guard), and the in-run watcher reads the same file every 0.1 s for the whole pass and writes the pass's
STOP file, which the host program checks before every launch of its --seconds loop (main.cpp repeatFor). The watcher keeps no file
position (each read opens the one live file and takes its newest complete line), so the run_hpl follow() race that watcher_q142s.py
fixes has no path here (E172.md, "The watcher"). Nothing here opens the management node: the readings come from the block's sampler
file. Its log lines and configs.json still say "E78": that is the unchanged code speaking.
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
import e172_common as e172  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)

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


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir, tag="E172"):
    """E145's stops, copied (E142 change 1), plus the watcher's flag: a line with board_w >= board_stop_w or
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


def start_watcher(read_line, path, board_stop_w, die_stop_c, out_dir, every_s=0.1, tag="E172 watcher"):
    """E142 change 2: every `every_s` seconds read the newest line of the live sampler file at `path` (read_line is run_e78's
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

    t = threading.Thread(target=loop, name="e172-watcher", daemon=True)
    t.start()
    return t, first


def _arg(name):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def main():
    reg = json.load(open(os.path.join(HERE, "plan-e172.json")))
    har = json.load(open(os.path.join(HERE, "harness-e172.json")))                              # E172 (E164 change 2)
    bad = []
    for key in ("card_code_unchanged_sha256", "e172_card_files_sha256", "registration_sha256", "watcher_sha256"):
        for rel, want in har[key].items():
            p = os.path.join(TOP, rel)
            have = sha(p) if os.path.exists(p) else "missing"
            if have != want:
                bad.append(f"{rel}: {have} != registered {want}")
    e = e172.check_frozen()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused E78 code, an E172 card file, the registration, the watcher files or pool 8's frozen "
              "files differ from E172's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e172.install()
    import run_e78  # noqa: E402  (after the check and the install; found in tools/claims-v3/kinds via e172_common's path)
    st = reg["plan"]["stops"]
    board_w, die_c = st["board_w"], st["die_hottest_shire_c"]
    wboard, wdie = board_w, die_c
    test = os.environ.get("E172_STOPTEST", "")                                                  # E172 (E164 change 1)
    if test == "board":
        board_w = st["stoptest_board_w"]
    elif test == "die":
        die_c = st["stoptest_die_c"]
    elif test == "watch":
        wboard = st["stoptest_board_w"]
    elif test:
        print(f"E172_STOPTEST={test!r}: only 'board', 'die' or 'watch'", file=sys.stderr)
        sys.exit(2)
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir == "/dev/null" or "--list" in sys.argv:
        run_e78.main()
        return
    tel = _arg("--tel-live")
    dry = "--dry" in sys.argv or bool(os.environ.get("V3_DRY"))
    spars = _arg("--sparsity") or ""
    if not dry and not test:                                                                    # E157 change 2, kept
        host = os.path.join(TOP, "build", "ccheck", "b", "host", "sparsity_host")
        why = []
        if not spars.endswith("tools/claims-v3/ccheck/sparsity_ccheck.sh"):
            why.append(f"--sparsity {spars!r} is not the C-logging wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh")
        if not os.environ.get("CCHECK_LOG"):
            why.append("CCHECK_LOG is not set")
        if not os.access(host, os.X_OK):
            why.append(f"no patched host {host}")
        if why:
            print("E172: refusing to run a pass without its C log: " + "; ".join(why), file=sys.stderr, flush=True)
            sys.exit(9)
    if tel and not dry:
        _, first = start_watcher(run_e78.last_sample, tel, wboard, wdie, out_dir)          # E142 change 2
        first.wait(5.0)
        if test == "watch":
            for _ in range(20):
                if TRIPPED:
                    break
                time.sleep(0.1)
            if TRIPPED:
                print(f"E172 stop-path test (watch): the watcher wrote STOP: {TRIPPED[0]}", file=sys.stderr, flush=True)
                sys.exit(run_e78.EXIT_HOT)
            print("E172 stop-path test (watch): the watcher did not fire within 2 s", file=sys.stderr, flush=True)
            sys.exit(1)
    elif test == "watch":
        print("E172 stop-path test (watch) needs --tel-live and no dry run", file=sys.stderr)
        sys.exit(1)
    guard_stops(run_e78, board_w, die_c, out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
