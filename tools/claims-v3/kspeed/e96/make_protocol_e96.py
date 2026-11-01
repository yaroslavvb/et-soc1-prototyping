#!/usr/bin/env python3
"""E96 (Q132): writes protocol.json (the session's blocks) and protocol-dry.json (the same order with short runs, for the
dry run of the queue and the reducer only). No card. The burst order comes from run_hpl.load_protocol's seeded shuffle
(order_seed 96); the sustained order is fixed here, from its own seeded generator, and written out explicitly, because
the int8 arm's rounds must stay whole and the runs a time cut would lose must be the ones that matter least.

    python3 make_protocol_e96.py

THE SUSTAINED BLOCK, in order (each group shuffled inside itself, except G3):
  R1  a round of the int8 arm: int8 full and E87's three real int8 tiles
  Ga  two of the six gated float tiles of claims.E96.S2b (one fp32, one fp16, different models), fp32 randn, fp16 randn
  R2  a round
  Gb  two more gated tiles, fp32 resnet18_l2c1 (the first of sustained_first, the mid-power gated tile), fp16 zeros, int8 zeros
  R3  a round
  Gc  the last two gated tiles, fp32 randn again, fp16 randn again
  R4  a round
  -- the plan ends here: 29 runs, about 65 card-minutes with the bursts and the smoke --
  G3  the rest of sustained_first's first 11, in that list's order, then fp32 zeros: they run if the clock allows, so a cut
      takes the list's tail first (queue_e96.py ends the session 3 min before the slot's end, whatever is left)
sustained_first's own tail (its last four, all int8) gets no sustained run: they burst like every tier-1 tile.
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
REAL2 = "tools/claims-v3/kinds/real2"
REAL1 = "tools/claims-v3/kinds/real"
ANCHORS = [("fp32", "randn"), ("fp32", "zeros"), ("fp16", "randn"), ("fp16", "zeros"), ("int8", "full"), ("int8", "zeros")]
ARM_TILES = ["l0_mlp_up", "l6_mlp_down", "l6_attn_qk"]
KEEP_SUS = 11          # how many of sustained_first run sustained; the plan's budget decides it (README, "The budget")
ROUNDS = 4             # the arm's rounds


def r2(k):
    t, n = k.split("/")
    return {"type": t, "values": f"file:{REAL2}/tiles/{t}/{n}.bin", "label": f"{t}-r2-{n}"}


def anchor(t, n, suffix=""):
    return {"type": t, "values": f"file:tools/claims-v3/kinds/tiles/{t}/{n}.bin", "label": f"{t}-{n}{suffix}"}


def arm_real(n, suffix=""):
    return {"type": "int8", "values": f"file:{REAL1}/tiles/int8/{n}.bin", "label": f"int8-real-{n}{suffix}"}


def sustained_order(P):
    first = P["e96_suggested"]["sustained_first"]
    keep, cut = first[:KEEP_SUS], first[KEEP_SUS:]
    gated = P["claims"]["E96"]["S2b_gate_buys_sustained_clock"]["tiles"]
    assert set(gated) <= set(keep), "every S2b tile must run sustained"
    rng = random.Random(9600)
    # a Latin square: each group gets one fp32 tile and one fp16 tile, of different models
    models = sorted({k.split("/")[1] for k in gated})
    rng.shuffle(models)
    pairs = [[f"fp32/{models[i]}", f"fp16/{models[(i + 1) % 3]}"] for i in range(3)]
    Ga = [r2(k) for k in pairs[0]] + [anchor("fp32", "randn"), anchor("fp16", "randn")]
    Gb = [r2(k) for k in pairs[1]] + [r2(first[0]), anchor("fp16", "zeros"), anchor("int8", "zeros")]
    Gc = [r2(k) for k in pairs[2]] + [anchor("fp32", "randn", "-rep2"), anchor("fp16", "randn", "-rep2")]
    for g in (Ga, Gb, Gc):
        rng.shuffle(g)
    G3 = [r2(k) for k in keep if k not in gated and k != first[0]] + [anchor("fp32", "zeros")]
    rounds = []
    for i in range(1, ROUNDS + 1):
        s = f"-round{i}"
        r = [anchor("int8", "full", s)] + [arm_real(n, s) for n in ARM_TILES]
        rng.shuffle(r)
        for x in r:
            x["round"] = i
        rounds.append(r)
    order = []
    for name, grp in (("R1", rounds[0]), ("Ga", Ga), ("R2", rounds[1]), ("Gb", Gb), ("R3", rounds[2]), ("Gc", Gc),
                      ("R4", rounds[3]), ("G3", G3)):
        for x in grp:
            x["group"] = name
            order.append(x)
    return order, keep, cut


def proto(P, order, burst, sus, smoke_tail, cap, note):
    tier1 = [k for k, v in P["tiles"].items() if v["tier"] == 1]
    runs_b = [r2(k) for k in tier1] + [anchor(t, n) for t, n in ANCHORS]
    return {
        "experiment": "E96",
        "request": "Q132",
        "card": "aifoundry2",
        "order_seed": 96,
        "note": note,
        "tools": {"heater": "build/sparsity_t2/host/sparsity_host", "kernel": "build/sparsity_t2/kernel/sparsity.elf",
                  "ettelem": "build/ettelem-hpl/ettelem"},
        "kinds": "tools/claims-v3/kinds/kinds.json",
        "real_tiles": [f"{REAL2}/predictions-real2.json", f"{REAL1}/predictions-real.json"],
        "predictions": "tools/claims-v3/kspeed/e96/predictions.json",
        "sampler": {"every_ms": 100},
        "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3},
        "caps": {"max_card_min": cap},
        "blocks": [
            {"name": "SMOKE", "title": "the idle card with no launch (its last 60 s are the session's rest reading), then one 2 s launch of a real2 tile at each gating level (not analysed)",
             "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5},
             "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
             "runs": [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0},
                       "tail_s": smoke_tail},
                      r2("fp32/vgg16_fc2"), r2("fp16/t5small_l0_down"), r2("int8/gpt2_l11_down_maxabs")]},
            {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E80's, E83's and E87's BURST)",
             "passes": 2, "shuffle": True, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300},
             "launch": burst["launch"], "tail_s": burst["tail_s"], "runs": runs_b},
            {"name": "SUS", "title": "sustained: nine back-to-back 8 s processes (~76 s) from a die reading <= 57 C (E80's, E83's and E87's SUS), in the order make_protocol_e96.py fixed",
             "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 57, "max_wait_s": 300},
             "launch": sus["launch"], "tail_s": sus["tail_s"], "runs": order},
        ],
    }


def main():
    P = json.load(open(os.path.join(ROOT, REAL2, "predictions-real2.json")))
    order, keep, cut = sustained_order(P)
    note = ("E80's, E83's and E87's design on Q132(r)'s real2 tiles, E87's six anchors, and four rounds of E87's three real "
            "int8 tiles against int8 full; nothing is set on the card")
    full = proto(P, order, {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4},
                 {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}, 75, 72, note)
    full["sustained_first_kept"], full["sustained_first_cut"] = keep, cut
    json.dump(full, open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    dry = proto(P, order, {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5},
                {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5}, 3, 72,
                "THE DRY SHAPE, toy card only: the same order with short runs, for the queue and the reducer")
    json.dump(dry, open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    b = sum(1 for k, v in P["tiles"].items() if v["tier"] == 1) + len(ANCHORS)
    print(f"bursts {b} x 2 = {2 * b}; sustained {len(order)} runs, {sum(1 for x in order if x['group'] != 'G3')} of them the plan")
    for x in order:
        print(f"  {x['group']} {x['label']}")
    print("sustained_first kept:", keep)
    print("sustained_first cut:", cut)


if __name__ == "__main__":
    main()
