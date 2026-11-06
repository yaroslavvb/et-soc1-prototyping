#!/usr/bin/env python3
"""E178 (Q146, the kit): did every session that must carry a C log carry one, checked to its end? (E178.md section 7, "The sessions that
must carry a C log (E171's rule)".) It is tools/claims-v3/p8-600/ccsessions_p8.py, imported UNCHANGED, with E178's layout added to its RUNS
table in memory; its listing rule, its three checks per session and its stop-path rule are ccsessions_p8.py's own:

  THE LIST: e178-smoke/p17801, then every pass directory e178/p1781N (aifoundry3) or e178/p1782N (aifoundry1 card 1), never an .attempt-*
  copy, whose runs.jsonl holds a launch record, whatever its block status. The stop-path test e178-stoptest/p17802 must hold no launch
  record and no C record.

    python3 -B tools/claims-v3/e178/ccsessions_e178.py --run E178|E178c1 --raw <raw copy> --ccheck <ccheck --out json> [--since <epoch s>]
        [--json <out>]

Exit 0 when every listed session is CCSESSION-OK and the stop-path test is clean, 4 when not, 2 on a usage error (ccsessions_p8's codes).
check(run, raw, ccheck, since) is what score_e178.py calls. Standard library only. SPDX-License-Identifier: Apache-2.0
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
import ccsessions_p8 as C  # noqa: E402  (unchanged; its sha256 is pinned in SHA256SUMS-e178-kit)

LAYOUT = {"E178": {"dir": "e178", "smoke": "p17801", "stoptest": "p17802", "passes": re.compile(r"^p1781[0-9]$")},
          "E178c1": {"dir": "e178", "smoke": "p17801", "stoptest": "p17802", "passes": re.compile(r"^p1782[0-9]$")}}
for _k, _v in LAYOUT.items():
    C.RUNS.setdefault(_k, _v)
RUN_OF_CARD = {"aifoundry3": "E178", "aifoundry1c1": "E178c1"}


def check(run, raw, ccheck_out, since=None):
    return C.check(run, raw, ccheck_out, since)


def listed_sessions(run, raw):
    return C.listed_sessions(run, raw)


if __name__ == "__main__":
    sys.exit(C.main(sys.argv[1:]))
