#!/usr/bin/env python3
"""E143 (Q138): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from predictions-e143.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e143/make_protocol_e143.py > tools/claims-v3/e143/protocol.txt

THE BURST is E80's BURST block, the shape M7's aifoundry2 term was fitted on (E80's and E83's kinds bursts): one 6 s process (budget 7.5 s) of the
kinds harness (sparsity_host --test fma on the tile, build/sparsity_t2, E80's binaries) from a die reading <= 55 C (max wait 300 s), a 4 s tail,
the sampler every 100 ms without --reset-ms. Nothing is set on the card.

THE BLOCK: BURST, 3 passes, each pass the 36 pool tiles and E80's three replicate tiles (fp32 randn, fp16 randn, int8 full) in a seeded shuffled
order (order_seed 143; run_hpl.py's load_protocol shuffles each pass on its own, so a pass is whole before the next starts). 117 bursts.
The session's cap (38 card-minutes; run_e119.py starts a run only if its planned time fits) cuts pass 3's tail if the gates run long.

THE STOPS (E136's registered stops, under the keys run_hpl.py's watcher reads, as E146): one die reading (the minion shires' mean or hottest sensor)
at or above 80 C, or the board above 93 W on three samples in a row, ends the session. The admission rule (run_e105.py): a cell runs only if its
frozen estimate of the first second at 800 MHz is <= 86 W (E101's rule had 88 W); after a run that read 93 W, nothing at or above its estimate.

THE STOP-PATH TESTS (after the smoke, before the session; the queue halts unless both pass; E146's):
  STOPTEST-BOARD  board_cap_w 30 W (three samples): one 6 s burst of the pool's fp32 anchor_randn (M7: about 82 W in its first second). The
                  watcher must trip on three live samples over 30 W while the launch runs; the launch loop ends at its next launch boundary;
                  exit 4.
  STOPTEST-DIE    abs_stop_c 30 C: the die reads above 40 C on this card at rest, so the watcher must trip on the first live sample, before any
                  launch; exit 4.

THE SMOKE: the idle card (30 s, the session's rest reading), then a 2 s launch of each type's zeros anchor, each with its check of C and the
kernel's cycles per op (546 / 546 / 318 for fp32 / fp16 / int8: E87's and E96's smoke).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e143_common as C  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e143.json")))
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
SMOKE_TILES = ("fp32.anchor_zeros", "fp16.anchor_zeros", "int8.anchor_zeros")
STOPTEST_TILE = "fp32.anchor_randn"


def runs_of_pass():
    rs = []
    for name in sorted(P["tiles"]):
        t = P["tiles"][name]
        rs.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    for lab, r in P["replicate"].items():
        rs.append({"type": r["type"], "values": r["values"], "label": lab})
    return rs


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    for n in SMOKE_TILES:
        t = P["tiles"][n]
        smoke.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of each type's zeros anchor",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E80's BURST block, E64's LAD shape)",
         "passes": 2 if dry else 3, "shuffle": True, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": runs_of_pass()}
    b.update(burst)
    blocks.append(b)
    return {"experiment": "E143", "request": "Q138", "card": "aifoundry2", "order_seed": 143,
            "note": "blind pool 5 under aifoundry2's own governor in 6 s bursts (E80's harness and shape), with E80's three replicate tiles; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/sparsity_t2/host/sparsity_host", "kernel": "build/sparsity_t2/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e143/predictions-e143.json",
            "sampler": {"every_ms": 100}, "safety": dict(P["rules"]["safety"]), "caps": {"max_card_min": 38},
            "smoke_cycles": {P["tiles"][n]["label"]: CYCLES[P["tiles"][n]["type"]] for n in SMOKE_TILES}, "dry_c_w": P["dry_c_w"],
            "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"],
            "relation": {"B800": P["relation"]["B800"], "s800": P["relation"]["s800"]}, "admission": P["admission"], "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    t = P["tiles"][STOPTEST_TILE]
    run = {"type": t["type"], "values": t["values"], "label": t["label"], "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5},
           "launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": 80, "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": 93, "cap_consecutive": 3}
    p["note"] = f"E143's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    bl = p["blocks"][1]
    n = len(bl["runs"]) * bl["passes"]
    est_s = n * 14
    print(f"block BURST: {bl['passes']} passes x {len(bl['runs'])} runs = {n} bursts (shuffled at run time, order_seed 143); about {est_s / 60:.0f} card-minutes at 14 s a burst "
          f"(E146: 104 runs in 25.1 min, smoke and stop tests included); plus the smoke and the two stop tests (about 3 min); the session's cap {p['caps']['max_card_min']} min cuts pass 3's tail")
    for r in bl["runs"]:
        a = p["admission"][r["label"]]
        print(f"  {r['label']:36s} {r['type']} {r['values'][:72]:72s} est800 {a['fixed_p800_w']} W")
    top = max(a["fixed_p800_w"] for a in p["admission"].values())
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
