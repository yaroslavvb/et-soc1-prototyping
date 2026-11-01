#!/usr/bin/env python3
"""E102 amendment A1 (E102.md, "Amendments"): the orders of the blocks A1 adds. Standard library only. The frozen e102_common.py, run_e102.py and block_e102.sh are not changed: 10213 runs through block_e102.sh as registered; 10214 and the R blocks
run through block_e102a1.sh, which hands run_e78.py an exact item list (`--items`, an option the runner already has).

    python3 tools/claims-v3/kinds/e102a1_common.py --order 10240 [--card aifoundry1-c1]     # the comma-separated item list of one block

  10214         short G: the launch gate; the tie, own zero, the six items R3 and R4's B-side legs read (all-in and balanced at bits 23, 27 and 31), shuffled, own zero, the tie.
  10240-10243   R: a train with dense own zeros, for R2's two cells. `fp32.aq`, a pair, `fp32.aq`, a pair, ... : every item has its own zero within three runs, and no neighbour differs from it by more than about 0.4 W. ABBA over the bit-0 and bit-6 pairs, so
                each of the four items is read twice a pass. The first block opens with five settling reads of the zero, which no price uses.
"""
import argparse
import random

Z = "fp32.aq"
SETTLE = 5
FIRST_R = 10240
SHORT_G_ITEMS = ("fp32.bj_23", "fp32.bp_23", "fp32.bj_27", "fp32.bp_27", "fp32.bj_31", "fp32.bp_31")
PAIRS = (("fp32.aj_0", "fp32.ap_0"), ("fp32.aj_6", "fp32.ap_6"))
SMOKE = ("fp32.aq", "fp32.aj_6", "fp32.ap_6", "fp32.hq")


def order(pass_no, card="aifoundry1-c1"):
    rng = random.Random(f"E102A1|{card}|{pass_no}")
    if pass_no == 10214:
        items = list(SHORT_G_ITEMS)
        rng.shuffle(items)
        return ["anchor_pi", "fp32.hq"] + items + ["fp32.hq", "anchor_pi"]
    if 10240 <= pass_no <= 10249:
        first, second = [list(p) for p in PAIRS]
        rng.shuffle(first)
        rng.shuffle(second)
        pairs = [first, second]
        rng.shuffle(pairs)
        seq = [Z]
        for pair in (pairs[0], pairs[1], pairs[1][::-1], pairs[0][::-1]):
            seq += pair + [Z]
        return ([Z] * SETTLE if pass_no == FIRST_R else []) + seq
    raise SystemExit(f"pass {pass_no} is no A1 block")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", type=int, required=True)
    ap.add_argument("--card", default="aifoundry1-c1")
    a = ap.parse_args()
    print(",".join(order(a.order, a.card)))


if __name__ == "__main__":
    main()
