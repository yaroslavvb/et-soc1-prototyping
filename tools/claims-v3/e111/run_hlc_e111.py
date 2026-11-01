#!/usr/bin/env python3
"""E111 amendment A1: E63's camera runner, run_hlc.py, imported and run unchanged, except that its one `who` call (the other-user
check's logins, _logged_in_others) is answered by idle_logins_e111.py: a user whose every session has been idle for at least 120
minutes does not block. Every other check (other users' device processes, our stale ones, the et_soc1 use count, the card lock),
the sampler (with its once-a-second statistics reset, allowed by the owner's ruling of 31 October 2026), the camera recorder, the
safety stops and the schedule are run_hlc.py's own code.

    python3 run_hlc_e111.py --protocol protocol-cam.json --out <RUNDIR> [--dry] [--list] ...      (from build/e111/cam)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.join(HERE, "..", "hlc")):
    if os.path.exists(os.path.join(p, "run_hlc.py")):
        sys.path.insert(0, os.path.abspath(p))
        break
sys.path.insert(0, HERE)
import run_hlc as R  # noqa: E402
import idle_logins_e111 as IL  # noqa: E402

if __name__ == "__main__":
    if "--dry" not in sys.argv:
        IL.patch(R, as_bytes=False)
    sys.exit(R.main())
