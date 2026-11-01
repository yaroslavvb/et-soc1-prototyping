#!/usr/bin/env python3
"""E111: the card minutes the first queue used (its queue_end record's card_min_total), for chain_go2_e111.sh."""
import json
import sys

ends = [json.loads(ln) for ln in open(sys.argv[1]) if '"queue_end"' in ln]
print(ends[0].get("card_min_total", 0) if ends else 0)
