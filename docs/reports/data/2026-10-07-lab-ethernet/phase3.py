#!/usr/bin/env python3
"""Third round: rerun the two Ethernet directions that came in below line rate in drive.py (aifoundry3 -> 2 and
aifoundry1 -> 3, 753-760 Mb/s), twice each. Both first runs overlapped a NetworkManager DHCP retry on one end,
which drops the link-local address for a moment."""
import json, time
from drive import NB, has_ll, record, run_on, target

for c, s in [(2, 3), (3, 1)]:
    done = 0
    for attempt in range(1, 13):
        if done == 2:
            break
        while not (has_ll(c) and has_ll(s)):
            time.sleep(3)
        rc, o, e = run_on(c, f"{NB} down {target(s, 'eth')} --secs 8")
        try:
            r = json.loads(o.strip().splitlines()[-1])
            r.update(client=c, server=s, path="eth", test="down-rerun", tries=attempt)
            record(r)
            done += 1
        except Exception:
            print(f"retry {c}<-{s}: rc={rc} {e.strip()[-200:]}", flush=True)
            time.sleep(2)
