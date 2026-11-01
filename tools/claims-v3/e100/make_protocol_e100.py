#!/usr/bin/env python3
"""E100: writes protocol.json. Two rounds in opposite order; R (the statistics-reset arm) sits at the turn, so a short slot loses it last on neither side but the
session's own end check (run_e100.py) stops cleanly wherever the slot ends.

    python3 make_protocol_e100.py        (writes protocol.json beside this script)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TILE = "file:tools/claims-v3/kinds/tiles/int8/zeros.bin"
FIXED = 850000
N_ITERS = 10000000


def arm(label, gap=0, procs=3, reset=False):
    la = {"seconds": 7.5, "budget": 9.0, "processes": procs, "fixed_iters": FIXED}
    if gap:
        la["gap_ms"] = gap
    r = {"label": label, "launch": la}
    if reset:
        r["sampler_reset_ms"] = 1000
    return r


def long_kernel():
    return {"label": "n", "launch": {"seconds": 4.5, "budget": 7.5, "processes": 5, "one_kernel_iters": N_ITERS}}


ARMS = {"A0": (arm("a0"), 4), "A5": (arm("a5", 5), 4), "A20": (arm("a20", 20), 4), "A100": (arm("a100", 100, 2), 6), "N": (long_kernel(), 5), "R": (arm("r", 20, reset=True), 4)}
ROUND1 = ["A0", "A5", "A20", "A100", "N", "R"]
ROUND2 = ["R", "N", "A100", "A20", "A5", "A0"]


def main():
    common = {"type": "int8", "values": TILE, "mask": "0xffffffff", "per_shire": 32, "seed": 1, "start": {"mode": "cool", "max_c": 62, "max_wait_s": 120}, "tail_s": 2}
    blocks = [{"name": "SMOKE", "title": "one short process of each flag and one full-length long kernel (not analysed)", "default": False, **common,
               "tail_s": 1, "runs": [
                   {"label": "smoke-a0", "launch": {"seconds": 2, "budget": 3.5, "processes": 1, "fixed_iters": FIXED}},
                   {"label": "smoke-a100", "launch": {"seconds": 2, "budget": 3.5, "processes": 1, "fixed_iters": FIXED, "gap_ms": 100}},
                   {"label": "smoke-n", "launch": {"seconds": 4.5, "budget": 7.5, "processes": 1, "one_kernel_iters": N_ITERS}},
                   {"label": "smoke-r", "sampler_reset_ms": 1000, "launch": {"seconds": 2, "budget": 3.5, "processes": 1, "fixed_iters": FIXED, "gap_ms": 20}},
               ]}]
    for rnd, order in ((1, ROUND1), (2, ROUND2)):
        for a in order:
            cfg, passes = ARMS[a]
            blocks.append({"name": f"R{rnd}{a}", "title": f"round {rnd}, arm {a}", **common, "passes": passes, "runs": [cfg]})
    proto = {"experiment": "E100", "request": "Q132", "card": "aifoundry2", "order_seed": 100,
             "title": "The idle reset against launch gaps of different lengths, and one long launch with no gap",
             "tools": {"heater": "build/e100/host/sparsity_host", "kernel": "build/e100/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
             "kinds": "tools/claims-v3/kinds/kinds.json", "sampler": {"every_ms": 100},
             "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3}, "caps": {"max_card_min": 32},
             "pause_s": [0.0, 1.0], "pause_seed": 100, "blocks": blocks}
    json.dump(proto, open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    print("protocol.json:", len(blocks), "blocks")


if __name__ == "__main__":
    main()
