#!/usr/bin/env python3
"""E97 (Q132): what E97's runners, reducers, scorer and self-test share. Standard library only (the runners must work
without numpy). The registration is tools/claims-v3/e97/E97.md; the frozen numbers are predictions-e97.json beside it.

Part A runs E89's lock-in on the kinds E89 left out. run_e97.py and reduce_e97.py reuse E89's runner and reducer byte for
byte: they replace these module-level names on the imported module and call its main(), the way E86 and E95 reuse E78's:
    run_e89.BLOCKS, REF_BLOCK, LOW_BLOCKS, pass_order; e78_common.load_items (E86's install(), which adds the real tiles)
    reduce_e89.BLOCK_ITEMS, REF, LOW

    python3 tools/claims-v3/e97/e97_common.py --list
    python3 tools/claims-v3/e97/e97_common.py --order 9710 [--card aifoundry3]
    python3 tools/claims-v3/e97/e97_common.py --verify        # the reused files against the freeze, the tiles
"""
import argparse
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.join(TOOLS, "kinds"))
sys.path.insert(0, os.path.join(TOOLS, "e89"))

SEED_TAG = "E97"
FIRST_PASS = 9710       # Part A: 9710, 9711
SECOND_PASS = 9711
HOLDS_PASS = 9720       # Part B
SMOKE_A = 9701
SMOKE_B = 9702
REF_BLOCK = "f32randn"

# E89's frame: a kind switched against its type's zeros at 1/60 Hz. A kind with E78 D below 2 W against its own zeros
# would swing the die less than 0.25 degC, so it runs against idle (S 2.0-4.1 W, the frame E89 gave int8 zeros). Its
# over-idle cell is then measured, not a sum.
AGAINST_IDLE = {  # block: item
    "f32zero": "fp32.zeros", "f16zero": "fp16.zeros",
    "f32sp90": "fp32.sparse90", "f32arbz": "fp32.a_randn_b_zeros", "f32azbr": "fp32.a_zeros_b_randn",
    "f16sp90": "fp16.sparse90", "f16wsp90": "fp16.wsparse90", "f16arbz": "fp16.a_randn_b_zeros",
    "f16azbr": "fp16.a_zeros_b_randn",
    "i8azbf": "int8.a_zeros_b_full", "i8afbz": "int8.a_full_b_zeros", "i8wsp90": "int8.wsparse90",
    "i8sp90": "int8.sparse90", "i8ones": "int8.ones"}
AGAINST_ZEROS = {  # block: item (D >= 2 W)
    "i8wsp50": "int8.wsparse50", "i8high": "int8.highbit", "i8tern": "int8.ternary", "i8pos": "int8.pos",
    "i8sort": "int8.sorted", "f16wsp50": "fp16.wsparse50", "f32sp50": "fp32.sparse50", "f32neg1": "fp32.neg_ones",
    "f16neg1": "fp16.neg_ones", "f16ones": "fp16.ones", "f32pi": "fp32.pi",
    "i8r0up": "int8.real_l0_mlp_up", "i8r6dn": "int8.real_l6_mlp_down", "i8r6qk": "int8.real_l6_attn_qk"}
ZERO_OF = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}

BLOCKS = {}
for _b, _i in AGAINST_IDLE.items():
    BLOCKS[_b] = (_i, "idle")
for _b, _i in AGAINST_ZEROS.items():
    BLOCKS[_b] = (_i, ZERO_OF[_i.split(".")[0]])
BLOCKS[REF_BLOCK] = ("fp32.randn", "fp32.zeros")
LOW_BLOCKS = [b for b in BLOCKS if b != REF_BLOCK]
SMOKE_BLOCKS = "i8r6dn,f16zero"      # one real tile against int8 zeros, one zeros against idle

# Part B
HOLD_ITEMS = {"H1": "int8.full", "H2": "fp32.ones", "H3": "fp32.randn"}
HOLD_S = 1800.0          # about 30 minutes
CHAIN_S = 900.0          # H2 chained straight after H1 when the full plan does not fit
LAUNCH_S = 6.8           # as E89: back-to-back launches, each under timeout 10
REDUCED_LAUNCH_S = 3.5   # after a stop at the lab's 78 C reading: 3.5 s launches (eight fp32 kernels, 3.9 s of compute) ...
REDUCED_PERIOD_S = 7.0   # ... one every 7 s (a compute share near 0.56)
MAX_C = 78.0             # the lab's stop, E89's
RESUME_C = 75.0          # after a stop no launch until the reading is back here
HARD_C = 82.0            # the pass ends at once: no launch, the sampler stopped
MAX_BOARD_W = 70.0       # a stop like MAX_C (the PMIC's over-power alarm is at 75 W, E84)
RISE_LEVEL_C = 0.10      # a rest ends within this of the starting idle
SLOPE_C_PER_5MIN = 0.05  # R0, the starting idle: fallen by at most this over 5 minutes
REST_MIN_S = 600.0
R0_MAX_S = 1800.0
R_MAX_S = 2100.0
IDLE_WINDOW_S = 120.0    # the idle read at the end of a rest
DEADLINE = "2026-11-01 07:13 PST"   # every session ends by 07:15 PST; two minutes for the closing reads

# the frozen plan's thresholds, seconds left to the deadline, decided after H1 (E97.md, "The plan")
LEFT_FULL_S = 135 * 60   # R1, H2 for 30 min, R2, H3, R3
LEFT_CHAIN_S = 65 * 60   # H2 for 15 min chained on H1, R1, H3, R3
LEFT_H3_S = 45 * 60      # no H2: R1, H3, R3
H3_MIN_S = 900.0
R3_MIN_S = 600.0


def pass_order(card, pass_no):
    """The registered order: the 28 low-power blocks shuffled with Random("E97|<card>|<pass>"), then the reference (E89's rule)."""
    low = sorted(LOW_BLOCKS)
    random.Random(f"{SEED_TAG}|{card}|{pass_no}").shuffle(low)
    return low + [REF_BLOCK]


def sha256_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def reused_files():
    return {"tools/claims-v3/lib.sh": os.path.join(TOOLS, "lib.sh"),
            "tools/claims-v3/e89/run_e89.py": os.path.join(TOOLS, "e89", "run_e89.py"),
            "tools/claims-v3/e89/reduce_e89.py": os.path.join(TOOLS, "e89", "reduce_e89.py"),
            "tools/claims-v3/e89/pvt_sample.py": os.path.join(TOOLS, "e89", "pvt_sample.py"),
            "tools/claims-v3/kinds/e78_common.py": os.path.join(TOOLS, "kinds", "e78_common.py"),
            "tools/claims-v3/kinds/e86_common.py": os.path.join(TOOLS, "kinds", "e86_common.py"),
            "tools/claims-v3/kinds/kinds.json": os.path.join(TOOLS, "kinds", "kinds.json"),
            "tools/claims-v3/kinds/real/real.json": os.path.join(TOOLS, "kinds", "real", "real.json")}


def check_reused(pred_path=None):
    """The reused files' sha256 against predictions-e97.json's harness block; a list of problems."""
    pred_path = pred_path or os.path.join(HERE, "predictions-e97.json")
    want = json.load(open(pred_path))["harness"]["reused_unchanged_sha256"]
    bad = []
    for rel, p in reused_files().items():
        have = sha256_file(p)
        if have != want.get(rel):
            bad.append(f"{rel}: {have} != frozen {want.get(rel)}")
    return bad


def install_runner():
    """E89's runner, byte for byte, with E97's blocks and order."""
    import e86_common
    import run_e89
    e86_common.install()
    run_e89.BLOCKS = dict(BLOCKS)
    run_e89.REF_BLOCK = REF_BLOCK
    run_e89.LOW_BLOCKS = list(LOW_BLOCKS)
    run_e89.FIRST_PASS = FIRST_PASS
    run_e89.pass_order = pass_order
    return run_e89


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--order", type=int)
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.list:
        print(json.dumps({"blocks": BLOCKS, "n": len(BLOCKS), "against_idle": len(AGAINST_IDLE),
                          "against_zeros": len(AGAINST_ZEROS), "holds": HOLD_ITEMS}, indent=1))
    if a.order is not None:
        print(json.dumps(pass_order(a.card, a.order)))
    if a.verify:
        import e86_common
        import e78_common as ec
        items = {it["name"]: it for it in e86_common.load_items()}
        used = sorted({x for b in BLOCKS.values() for x in b if x != "idle"} | set(HOLD_ITEMS.values()))
        probs = check_reused() + ec.verify_tiles(ROOT, [items[n] for n in used])
        print(json.dumps({"items": len(used), "problems": probs}))
        sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
