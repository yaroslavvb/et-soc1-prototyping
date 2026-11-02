#!/usr/bin/env python3
"""E131 runner (Q136): one pass of E95's real-tiles matrix on aifoundry1 card 1. It is E78's runner,
tools/claims-v3/kinds/run_e78.py, run UNCHANGED, with E95's items and order installed on the shared e78_common module
(tools/claims-v3/kinds/e95_common.install, unchanged): E78's 51 kinds and the tie, Q132(r)'s thirty real2 tiles and three of
E86's real tiles; a pass is the tie, three segments of E78's six anchors and eleven of the 33 E95 items, the tie (53 runs).
A port of tools/claims-v3/kinds/run_e95.py with one change, marked E131: the registered stops of E131.md (the owner's rule
of Mon 2 Nov 2026, "don't do any power cycles": every run stays inside the registered stops with margin).

    python3 tools/claims-v3/e131/run_e131.py <out-dir> --root <tree root> ...     (every run_e78.py option)

Before anything runs, the reused files (E95's freeze, predictions-e95.json > harness > reused_unchanged_sha256, and
E131's own list, predictions-e131.json > harness > card_code_unchanged_sha256) are checked by sha256, and the run refuses
(exit 9) on any difference. E131 change: run_e78.py reads the newest telemetry line through its module-level last_sample()
before every launch and in every wait; this wraps that function (E127's and E130's board-power stop, extended) so that a
line with board_w >= the registered board stop, or any minion-shire reading >= the registered die stop, writes the pass's
STOP file and ends the pass with run_e78's own EXIT_HOT (6). run_e78.py's own --max-c (block_e131.sh passes the registered
72 C) still checks the first shire reading and the PMIC's. Nothing here opens the management node: the readings come from
the block's sampler file. Its log lines and configs.json still say "E78": that is the unchanged code speaking.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
sys.path.insert(0, K)
import e95_common as e95  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check():
    reg = json.load(open(os.path.join(HERE, "predictions-e131.json")))
    reg95 = json.load(open(os.path.join(K, "predictions-e95.json")))
    bad = []
    want = dict(reg95["harness"]["reused_unchanged_sha256"])
    want.update(reg["harness"]["card_code_unchanged_sha256"])
    for rel, w in want.items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != w:
            bad.append(f"{rel}: {have} != registered {w}")
    e = e95.check_real_jsons()
    if e:
        bad.append(e)
    return reg, bad


def guard_stops(run_e78, board_stop_w, die_stop_c, out_dir):
    """E131's stops (E131.md, "Stops"): a telemetry line with board_w >= board_stop_w or max(temp_c.minshire) >= die_stop_c
    writes <out>/STOP (which the host program and the runner watch) and ends the pass with run_e78's EXIT_HOT (6). The line
    is otherwise returned unchanged."""
    orig = run_e78.last_sample

    def guarded(path):
        s = orig(path)
        if not s:
            return s
        w = s.get("board_w")
        msg = None
        if isinstance(w, (int, float)) and w >= board_stop_w:
            msg = f"E131 board-power stop: board_w {w} W >= {board_stop_w} W"
        try:
            ms = [float(x) for x in (s.get("temp_c") or {}).get("minshire") or []]
        except (TypeError, ValueError):
            ms = []
        if msg is None and ms and max(ms) >= die_stop_c:
            msg = f"E131 die stop: hottest minion-shire reading {max(ms)} C >= {die_stop_c} C"
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
    reg, bad = check()
    if bad:
        print("refusing to run - the reused code, a frozen JSON or an E131 card file differs from E131's freeze:\n  "
              + "\n  ".join(bad), file=sys.stderr)
        sys.exit(9)
    e95.install()
    import run_e78  # noqa: E402  (after the check and the install)
    st = reg["stops"]
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    guard_stops(run_e78, st["board_w"], st["die_hottest_shire_c"], out_dir)
    run_e78.main()


if __name__ == "__main__":
    main()
