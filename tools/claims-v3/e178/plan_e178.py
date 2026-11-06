#!/usr/bin/env python3
"""E178 (Q146): the run order of every planned pass, fixed by rule before any session (E178.md section 7).

    python3 -B plan_e178.py --dir tools/claims-v3/e178            # writes plan-e178.json (both cards, FULL and TWO)
    python3 -B plan_e178.py --dir tools/claims-v3/e178 --check    # rebuilds it and compares byte for byte

A pass (E78's protocol, E171's form): the tie `anchor_pi`; three segments; the tie. Each segment: E78's six anchors in E78's
order (fp32.zeros, fp32.randn, fp16.zeros, fp16.randn, int8.zeros, int8.full); then the four core couples, each as two adjacent
runs, (A, B) when (pass + segment) is even and (B, A) when odd (ABBA across segments and passes); then the segment's share of the
other 32 kinds: sorted by key, shuffled with random.Random("E178|<card>|<pass>"), dealt round-robin into the three segments (11,
11, 10), each segment then shuffled with the same generator (E163's and E171's order rule). 76 runs a pass; E171's two burn-ins
of the tie are the kit's. The kinds and couples are kinds-e178.json's; nothing here reads a card datum.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import random
import sys

ANCHORS = ["fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"]
COUPLES = [("fp32.e178_v4", "fp32.e178_v5"), ("fp16.e178_v4", "fp16.e178_v5"), ("int8.e178_v4", "int8.e178_v5"),
           ("fp32.ones", "fp32.e178_uf")]
CARDS = {"aifoundry3": {"FULL": [17810, 17811, 17812, 17813], "TWO": [17810, 17811]},
         "aifoundry1c1": {"FULL": [17820, 17821, 17822, 17823], "TWO": [17820, 17821]}}


def one_pass(kinds, card, p):
    core = {k for c in COUPLES for k in c}
    others = sorted(k for k in kinds if k not in core)
    assert len(others) == 32, len(others)
    rng = random.Random(f"E178|{card}|{p}")
    rng.shuffle(others)
    segs = [others[i::3] for i in range(3)]
    for s in segs:
        rng.shuffle(s)
    runs = ["anchor_pi"]
    for si, s in enumerate(segs):
        runs += ANCHORS
        for a, b in COUPLES:
            runs += [a, b] if (p + si) % 2 == 0 else [b, a]
        runs += s
    runs.append("anchor_pi")
    return runs


def build(d):
    kinds = [k["key"] for k in json.load(open(os.path.join(d, "kinds-e178.json")))["kinds"]]
    out = {"_what": "E178's run order (plan_e178.py)", "anchors": ANCHORS, "couples": COUPLES, "cards": {}}
    for card, plans in CARDS.items():
        out["cards"][card] = {"plans": plans, "passes": {}}
        for p in sorted(set(plans["FULL"] + plans["TWO"])):
            r = one_pass(kinds, card, p)
            assert len(r) == 76 and sum(1 for x in r if x in kinds) == 40 + 3 * 4 * 2 - 8
            out["cards"][card]["passes"][str(p)] = r
    return json.dumps(out, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="tools/claims-v3/e178")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    s = build(a.dir)
    f = os.path.join(a.dir, "plan-e178.json")
    if a.check:
        ok = open(f).read() == s
        print("CHECK", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    open(f, "w").write(s)
    print(f"wrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
