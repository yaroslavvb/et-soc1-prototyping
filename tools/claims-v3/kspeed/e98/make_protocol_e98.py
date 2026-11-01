#!/usr/bin/env python3
"""E98: writes protocol.json (the probe's blocks) and protocol-dry.json (the same order with short runs, for the dry
run of the queue and the reducer only). No card, no randomness: the order is fixed by design, the same in every probe.

    python3 make_protocol_e98.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TILE = "file:tools/claims-v3/kinds/tiles/{}/{}.bin"
# The fixed order: low power to high, so that the trip runs sit on a warm card. Index 0 starts from the rest and is
# not in the line; indexes 1-8 are the gated line; the hold follows them.
SUS = [("fp32", "zeros", "fp32-zeros-fromrest"),
       ("fp16", "zeros", "fp16-zeros"),
       ("int8", "zeros", "int8-zeros"),
       ("int8", "neg_ones", "int8-neg_ones"),
       ("int8", "sparse50", "int8-sparse50"),
       ("fp16", "ones", "fp16-ones"),
       ("int8", "full", "int8-full"),
       ("fp32", "randn", "fp32-randn"),
       ("fp16", "ones", "fp16-ones-rep2")]
HOLD = ("int8", "neg_ones", "int8-neg_ones-hold")


def run(t, v, label):
    return {"type": t, "values": TILE.format(t, v), "label": label}


def proto(rest_tail, sus_procs, hold_procs, tail, cap):
    return {
        "experiment": "E98",
        "request": "Q132",
        "card": "aifoundry2",
        "order_seed": 98,
        "note": "E80's and E87's runner and SUS shape in a fixed order, one session per probe, under the card's own "
                "governor; REST holds no launch (processes 0: the sampler reads the idle card for tail_s); nothing is set on the card",
        "tools": {"heater": "build/sparsity_t2/host/sparsity_host", "kernel": "build/sparsity_t2/kernel/sparsity.elf",
                  "ettelem": "build/ettelem-hpl/ettelem"},
        "kinds": "tools/claims-v3/kinds/kinds.json",
        "sampler": {"every_ms": 100},
        "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3},
        "caps": {"max_card_min": cap},
        "blocks": [
            {"name": "SMOKE", "title": "20 s of the idle card, then one 2 s launch of three tiles (not analysed)", "default": False,
             "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1},
             "tail_s": 3,
             "runs": [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 20},
                      run("fp32", "zeros", "fp32-zeros"), run("int8", "neg_ones", "int8-neg_ones"), run("fp16", "ones", "fp16-ones")]},
            {"name": "REST", "title": "the rest reading: no launch, the 10 Hz sampler on the idle card; the last 60 s are the reading",
             "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 0},
             "tail_s": rest_tail, "runs": [{"type": "fp32", "values": "zeros", "label": "rest"}]},
            {"name": "SUS", "title": "sustained: nine back-to-back 8 s processes (~76 s) from a die reading <= 57 C (E80's, E83's and E87's SUS), in a fixed order",
             "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 57, "max_wait_s": 300},
             "launch": {"seconds": 8, "budget": 9.5, "processes": sus_procs}, "tail_s": tail,
             "runs": [run(*s) for s in SUS]},
            {"name": "HOLD", "title": "the hold: 39 back-to-back 8 s processes (~5.5 min) of one unclamped kind; the last 120 s are the reading",
             "start": {"mode": "cool", "max_c": 57, "max_wait_s": 300},
             "launch": {"seconds": 8, "budget": 9.5, "processes": hold_procs}, "tail_s": tail,
             "runs": [run(*HOLD)]},
        ],
    }


json.dump(proto(120, 9, 39, 6, 30), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
d = proto(10, 1, 2, 1, 10)
d["note"] = "the dry run's short shape: same order, 8 s per kind, never on a card"
json.dump(d, open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
