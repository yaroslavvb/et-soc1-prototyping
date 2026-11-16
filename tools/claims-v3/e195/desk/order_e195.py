#!/usr/bin/env python3
"""E195's run order on a host named aifoundry3 (a desk check of code; no device).

    python3 -I -B order_e195.py <gen dir> [<dir of runitems.py --dry stderr files p901.err, p910.err ... p917.err>]

The lab's runner (tools/claims-v3/runitems.py, unchanged) runs per pass: two burn-in runs of the anchor, then the anchor,
the selected x9_ items in the order random.Random(f"{card}|{seed}|{block}").shuffle gives (block_x09.sh passes the
hostname as the card and the pass as both the seed and the block), then the anchor again. This prints that order for the
smoke 901 (its five named items) and the passes 910-917, computed here from the manifest; with the dry listings it also
checks that the runner's own `--dry --card aifoundry3` calls come in exactly that order. Exit 0 when they agree.
"""
import json
import os
import random
import re
import sys

gen = sys.argv[1]
dry = sys.argv[2] if len(sys.argv) > 2 else None
items = json.load(open(os.path.join(gen, "manifest.json")))["items"]
SMOKE = ["anchor_pi", "x9_rd_rnd", "x9_wr_u4", "x9_wrh_rnd", "x9_wrh_nst"]
bad = 0
print("E195 run order on a host named aifoundry3 (runitems.py's rule: card|seed|block = aifoundry3|<pass>|<pass>)")
for p in [901] + list(range(910, 918)):
    sel = [it["name"] for it in items if (it["name"] in SMOKE if p == 901 else True)]
    rest = [n for n in sel if n != "anchor_pi"]
    random.Random(f"aifoundry3|{p}|{p}").shuffle(rest)
    order = ["anchor_pi"] + rest + ["anchor_pi"]
    print(f"pass {p} ({'smoke' if p == 901 else ('warm-up' if p == 910 else 'headline')}): burn-in anchor_pi x2, then")
    print("  " + " ".join(f"{i}:{n}" for i, n in enumerate(order)))
    if dry:
        calls = []
        for line in open(os.path.join(dry, f"p{p}.err")):
            if line.startswith("DRY hold10: "):
                m = re.search(r"--item (\S+)", line)
                calls.append("x9_" + m.group(1).replace(".", "_") if m else "anchor_pi")
        want = ["anchor_pi", "anchor_pi"] + order
        same = calls == want
        bad += 0 if same else 1
        print(f"  the runner's dry listing: {len(calls)} device calls, {'the same order' if same else 'A DIFFERENT ORDER'}")
print("ORDER CHECK " + ("PASS" if (dry and not bad) else ("NOT RUN (no dry listings)" if not dry else "FAIL")))
sys.exit(1 if bad else 0)
