#!/usr/bin/env python3
"""Fourth round: all three links at once again (1 -> 2, 2 -> 3, 3 -> 1), watching each port's address during the
run. phase2's ring ran into aifoundry2's NetworkManager retry; here every run records whether any of the three
link-local addresses was removed or re-added while it ran ("disturbed"), and we stop after two clean runs."""
import json, threading, time
from drive import NB, has_ll, record, run_on, target

PAIRS = [(1, 2), (2, 3), (3, 1)]
SECS = 8

clean = 0
for attempt in range(1, 9):
    if clean == 2:
        break
    while not all(has_ll(h) for h in (1, 2, 3)):
        time.sleep(2)
    mon, out = {}, {}

    def watch(h):
        # every address event on the wired port during the test; an empty log means no NetworkManager retry hit it
        rc, o, e = run_on(h, f"timeout {SECS + 3} ip -6 monitor address dev enp7s0", SECS + 20)
        mon[h] = o.strip()

    def flow(c, s):
        rc, o, e = run_on(c, f"{NB} up {target(s, 'eth')} --secs {SECS}")
        try:
            out[(c, s)] = json.loads(o.strip().splitlines()[-1])
        except Exception:
            out[(c, s)] = None

    ws = [threading.Thread(target=watch, args=(h,)) for h in (1, 2, 3)]
    [w.start() for w in ws]
    time.sleep(0.5)
    fs = [threading.Thread(target=flow, args=p) for p in PAIRS]
    [f.start() for f in fs]
    [t.join() for t in fs + ws]
    disturbed = [h for h in (1, 2, 3) if mon.get(h)]
    if all(out.values()):
        record({"test": "ring-watched", "path": "eth", "tries": attempt, "disturbed": disturbed,
                "links": [{"client": c, "server": s, "Mbps": r["Mbps"], "MBps": r["MBps"]} for (c, s), r in out.items()],
                "Mbps_total": round(sum(r["Mbps"] for r in out.values()), 1)})
        clean += 0 if disturbed else 1
    else:
        print(f"retry ring: a flow failed; disturbed={disturbed}", flush=True)
    time.sleep(2)
