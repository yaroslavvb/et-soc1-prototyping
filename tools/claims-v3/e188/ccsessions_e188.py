#!/usr/bin/env python3
"""E188 (Q165, the kit): did every session that must carry a C log carry one, checked to its end? (E188.md section 6, "The sessions that
must carry a C log".) A port of tools/claims-v3/e186/ccsessions_e186.py (itself E182's ccsessions_e182.py): tools/claims-v3/p8-600/ccsessions_p8.py, imported UNCHANGED, with
E188's layout added to its RUNS table and its listing rule widened in memory for E188's train blocks (E188); its three checks per session
and its stop-path rule are ccsessions_p8's:

  THE LIST: e188-smoke/p18801, then every block directory e188/p1881N (a train), e188/p1882N (a FULL kinds pass) or e188/p1883N (a fallback kinds pass), never an
  .attempt-* copy, that holds a launch record: a kinds pass in its runs.jsonl; a train in its train.jsonl (a "process" and a "launch"
  field) or in its anchors' a0/runs.jsonl and a1/runs.jsonl; whatever its block status. The stop-path test e188-stoptest/p18802 must hold
  no launch record and no C record. Each listed session's C log is its block's c-log.jsonl (one per block: the anchors, the train and the
  smoke's train share it).

    python3 -B tools/claims-v3/e188/ccsessions_e188.py --run E188 --raw <raw copy> --ccheck <ccheck --out json> [--since <epoch s>]
        [--json <out>]

Exit 0 when every listed session is CCSESSION-OK and the stop-path test is clean, 4 when not, 2 on a usage error (ccsessions_p8's codes).
check(run, raw, ccheck, since) is what score_e188.py calls. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P8 = os.path.join(TOP, "tools", "claims-v3", "p8-600")
if P8 not in sys.path:
    sys.path.insert(0, P8)
import ccsessions_p8 as C  # noqa: E402  (unchanged; its sha256 is pinned in SHA256SUMS-e188-kit)

C.RUNS.setdefault("E188", {"dir": "e188", "smoke": "p18801", "stoptest": "p18802", "passes": re.compile(r"^p188(1[0-6]|2[0-9]|3[0-9])$")})
RUN_OF_CARD = {"aifoundry3": "E188"}
_orig_listed = C.listed_sessions


def _has_train_launch(d):
    p = os.path.join(d, "train.jsonl")
    if os.path.exists(p) and any(isinstance(r, dict) and "process" in r and "launch" in r for r in C._lines(p)):
        return True
    return any(C.has_launch(os.path.join(d, sub, "runs.jsonl")) for sub in ("a0", "a1"))


def listed_sessions(run, raw):
    """E188: ccsessions_p8's list, plus the train blocks whose launches sit in train.jsonl or the anchors' runs.jsonl"""
    if run != "E188":
        return _orig_listed(run, raw)
    R = C.RUNS[run]
    out = [os.path.join(raw, f"{R['dir']}-smoke", R["smoke"])]
    pd = os.path.join(raw, R["dir"])
    if os.path.isdir(pd):
        for nm in sorted(os.listdir(pd)):
            if ".attempt-" in nm or not R["passes"].match(nm):
                continue
            d = os.path.join(pd, nm)
            if os.path.isdir(d) and (C.has_launch(os.path.join(d, "runs.jsonl")) or _has_train_launch(d)):
                out.append(d)
    return out


C.listed_sessions = listed_sessions


def check(run, raw, ccheck_out, since=None):
    return C.check(run, raw, ccheck_out, since)


if __name__ == "__main__":
    sys.exit(C.main(sys.argv[1:]))
