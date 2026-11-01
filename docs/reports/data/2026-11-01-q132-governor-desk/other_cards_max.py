#!/usr/bin/env python3
"""Q132(g), item 1: the highest power-controller reading on aifoundry3 and aifoundry1 card 1 in the committed 31 Oct sessions, so that "untested" has a number.

    other_cards_max.py <repo> > other-cards-max.txt
"""
import gzip
import json
import os
import sys

SESS = [("E78", "aifoundry3", "2026-10-31-e78-kinds-energy-matrix"), ("E79", "aifoundry3", "2026-10-31-e79-fp16-int8-bit-prices"), ("E86", "aifoundry3", "2026-10-31-e86-real-tensors-energy"),
        ("E89", "aifoundry3", "2026-10-31-e89-heat-low-power"), ("E90", "aifoundry3", "2026-10-31-e90-signs-spread"),
        ("E82", "aifoundry1 card 1", "2026-10-31-e82-kinds-aifoundry1"), ("E88", "aifoundry1 card 1", "2026-10-31-e88-result-path"), ("E91", "aifoundry1 card 1", "2026-10-31-e91-real-tensors-aifoundry1")]


def main():
    data = os.path.join(sys.argv[1], "docs/reports/data")
    print("session card               telemetry files  readings   max board_w   readings >= 75 W")
    for exp, card, rel in SESS:
        d = os.path.join(data, rel)
        files = n = n75 = 0
        mx = 0.0
        for root, _, names in os.walk(d):
            for f in names:
                if not (f.endswith(".jsonl") or f.endswith(".jsonl.gz")):
                    continue
                p = os.path.join(root, f)
                op = gzip.open if f.endswith(".gz") else open
                try:
                    with op(p, "rt") as fh:
                        first = True
                        for ln in fh:
                            if '"board_w"' not in ln:
                                if first:
                                    break
                                continue
                            first = False
                            try:
                                w = json.loads(ln).get("board_w")
                            except ValueError:
                                continue
                            if isinstance(w, (int, float)):
                                n += 1
                                mx = max(mx, w)
                                n75 += 1 if w >= 75 else 0
                        files += 0 if first else 1
                except (OSError, EOFError):
                    pass
        print(f"{exp:7s} {card:18s} {files:15d} {n:9d} {mx:12.2f} {n75:12d}")


if __name__ == "__main__":
    main()
