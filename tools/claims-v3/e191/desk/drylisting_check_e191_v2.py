#!/usr/bin/env python3
"""E191's check of the runbook's command lines, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST; after E189's data commit fa9098c4
of Sat 14 Nov 2026, 20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum):
desk/drylisting_check_e191.py (eb1ac923, unchanged beside it) with its device-opening pattern naming session v2 too
(bash tools/claims-v3/e191/session_e191_v2.sh), so step 9 v2's launch line must carry ET_DEVICES=1 as v1's does; every other rule is v1's.
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/drylisting_check_e191_v2.py <the dry listing v2>    (DRYLISTING-CHECK-E191 PASS or FAIL)
A desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drylisting_check_e191 as V1  # noqa: E402

V1.OPEN = re.compile(V1.OPEN.pattern.replace(r"bash tools/claims-v3/e191/session_e191\.sh", r"bash tools/claims-v3/e191/session_e191(_v2)?\.sh"))
if "session_e191(_v2)?" not in V1.OPEN.pattern:
    sys.exit("drylisting_check_e191_v2: v1's pattern was not widened")

if __name__ == "__main__":
    sys.exit(V1.main(sys.argv[1:]))
