#!/usr/bin/env python3
"""E88 runner (Q130): E78's runner, tools/claims-v3/kinds/run_e78.py, run UNCHANGED with e88_common in the place of
e78_common - E88's 22 tiles and the pi tie, E88's per-pass order (seeded "E88|<card>|<pass>"), everything else
(the quiet rule, the launch band, the heater, `timeout 10` on every device process, the STOP file, the other-user
test) E78's. Its arguments are run_e78.py's; block_e88.sh passes them. It refuses to run if run_e78.py's sha256 is
not the one predictions-e88.json registers.
"""
import hashlib
import json
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
RUN78 = os.path.join(HERE, "..", "kinds", "run_e78.py")
want = json.load(open(os.path.join(HERE, "predictions-e88.json")))["harness"]["reused_unchanged_sha256"]
have = hashlib.sha256(open(RUN78, "rb").read()).hexdigest()
if have != want["tools/claims-v3/kinds/run_e78.py"]:
    raise SystemExit(f"refusing to run: run_e78.py sha256 {have} is not the registered one")
import e88_common  # noqa: E402

sys.modules["e78_common"] = e88_common
sys.argv[0] = RUN78
runpy.run_path(RUN78, run_name="__main__")
