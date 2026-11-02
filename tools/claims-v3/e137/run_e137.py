#!/usr/bin/env python3
"""E137 runner (Q137): one pass on aifoundry1 card 1. It is E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED (its sha256 is checked
against predictions-e137.json first), with E137's items and order installed on the shared e78_common module (e137_common.install: E78's 51 kinds
and the tie, plus E128's seven fp16 sign tiles; a pass is the tie, three segments of E78's six anchors and a third of the eight E137 items, the
tie: 28 runs). A port of tools/claims-v3/e128/run_e128.py with one change, marked E137: E131's registered stops (tools/claims-v3/e131/run_e131.py,
guard_stops, copied): a telemetry line with board_w >= the registered board stop, or any minion-shire reading >= the registered die stop, writes
the pass's STOP file and ends the pass with run_e78's own EXIT_HOT (6). run_e78.py's own --max-c (block_e137.sh passes 72 C) still checks the
first shire reading and the PMIC's. Nothing here opens the management node: the readings come from the block's sampler file.

    python3 tools/claims-v3/e137/run_e137.py <out-dir> --root <tree root> ...     (every run_e78.py option)

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e137_common as e137  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir):
    """E131's stops, copied (E137.md, "Stops"): a line with board_w >= board_stop_w or max(temp_c.minshire) >= die_stop_c writes <out>/STOP and
    ends the pass with EXIT_HOT (6). The line is otherwise returned unchanged."""
    orig = run_e78.last_sample

    def guarded(path):
        s = orig(path)
        if not s:
            return s
        w = s.get("board_w")
        msg = None
        if isinstance(w, (int, float)) and w >= board_stop_w:
            msg = f"E137 board-power stop: board_w {w} W >= {board_stop_w} W"
        try:
            ms = [float(x) for x in (s.get("temp_c") or {}).get("minshire") or []]
        except (TypeError, ValueError):
            ms = []
        if msg is None and ms and max(ms) >= die_stop_c:
            msg = f"E137 die stop: hottest minion-shire reading {max(ms)} C >= {die_stop_c} C"
        if msg:
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
    reg = json.load(open(os.path.join(HERE, "predictions-e137.json")))
    bad = []
    for rel, want in reg["harness"]["reused_unchanged_sha256"].items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != registered {want}")
    e = e137.check_e128_json()
    if e:
        bad.append(e)
    if bad:
        print("refusing to run - the reused code or E128's e128.json differs from E137's freeze:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e137.install()
    import run_e78  # noqa: E402  (after the check and the install)
    st = reg["stops"]
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    if out_dir != "/dev/null":
        guard_stops(run_e78, st["board_w"], st["die_hottest_shire_c"], out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
