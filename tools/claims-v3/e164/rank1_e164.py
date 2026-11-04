#!/usr/bin/env python3
"""E164-RANK1, registered by amendment E164-A1 (E164.md.dated-note.md, A1-3; Wed 4 Nov 2026, before any E164 data): card 1's half of rank
1, read from E164's own registered verdicts in its scored.json (score_e164.py, unchanged). It is E163-RANK1's conjunction
(tools/claims-v3/e163/predictions-e163.json > spec.rank1, scored by score_e163.py lines 384-389), with E164's rules in E163's places:

    PASS        if E164-M1 reads BETTER and E164-U1, E164-B1, E164-B2 and E164-C1 each read PASS;
    NOT SCORED  else, if any of the five reads NOT SCORED;
    FAIL        else.

No statistic is new: each part is scored as E164.md registers it, with E164's own minimum tiles (U1 at least 10, B1 at least 8, B2 at least
6, C1 NOT SCORED under 10). Rank 1 holds on both 600 MHz cards only if E163-RANK1 and E164-RANK1 both read PASS. Standard library only.

    python3 -B tools/claims-v3/e164/rank1_e164.py <E164's scored.json> [--out rank1-e164.json]
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json

NEEDS = {"E164-M1": "BETTER", "E164-U1": "PASS", "E164-B1": "PASS", "E164-B2": "PASS", "E164-C1": "PASS"}


def rank1(verdicts):
    parts = {r: verdicts.get(r, "NOT SCORED") for r in NEEDS}
    ok = all(parts[r] == NEEDS[r] for r in parts)
    ns = any(v == "NOT SCORED" for v in parts.values())
    return {"id": "E164-RANK1", "verdict": "PASS" if ok else ("NOT SCORED" if ns else "FAIL"), "parts": parts, "needs": NEEDS,
            "registered": "amendment E164-A1 (E164.md.dated-note.md, A1-3), before any E164 data"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scored")
    ap.add_argument("--out")
    a = ap.parse_args()
    r = rank1(json.load(open(a.scored))["verdicts"])
    print(f"E164-RANK1: {r['verdict']} ({', '.join(f'{k} {v}' for k, v in r['parts'].items())})")
    if a.out:
        with open(a.out, "w") as f:
            json.dump(r, f, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
