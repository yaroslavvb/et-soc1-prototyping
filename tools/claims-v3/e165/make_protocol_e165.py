#!/usr/bin/env python3
"""E165 (Q141(g)): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from predictions-e165.json; prints protocol.txt. No card. It is E160's make_protocol_e160.py with pool 7 and the registered order.

    python3 -B tools/claims-v3/e165/make_protocol_e165.py > tools/claims-v3/e165/protocol.txt

THE BURST is E160's (E143's, E80's BURST block): one 6 s process (budget 7.5 s) of the kinds harness (sparsity_host --test fma on the tile) from a die
reading <= 55 C (max wait 300 s), a 4 s tail, the sampler every 100 ms without --reset-ms. The heater is Q139(k)'s wrapper,
tools/claims-v3/ccheck/sparsity_ccheck.sh, which runs the C-logging host build/ccheck/b/host/sparsity_host with E80's kernel
build/sparsity_t2/kernel/sparsity.elf and appends --c-log <session>/c-log.jsonl --c-poison. Nothing is set on the card.

THE BLOCK: BURST, the 171 runs of predictions-e165.json's registered order, listed in that order ("passes": 1, "shuffle": false, so run_hpl.py's
load_protocol keeps it and every run's idx is its index in the order): 3 passes of 57, each opening with pool 7's three zeros anchors, then the other
52 admitted tiles and E80's two replicate tiles fp16 randn and int8 full, shuffled (order_seed 165). The 6 tiles left out by name and E80's fp32 randn
are in no run. The dry twin lists the first two passes (114 runs) at 1.5 s, as E160's dry twin ran two passes. The session's cap (40 card-minutes;
run_e119.py starts a run only if its planned time fits) cuts pass 3's tail if the gates run long; the registered subset (the first two passes) is the
same protocol under --cap 25.

THE STOPS (E160's), under the keys run_hpl.py's watcher reads: one die reading at or above 76 C, or the board above 85 W on three samples in a row,
ends the session. The admission rule (run_e105.py): a run starts only if its frozen estimate is <= 82 W; after a run whose highest board sample
reached 82 W, nothing at or above that run's estimate runs (E159's lock).

THE STOP-PATH TESTS (after the smoke, before the session; the queue halts unless both pass; E160's, through the same wrapper):
  STOPTEST-BOARD  board_cap_w 30 W (three samples): one 6 s burst of fp32.anchor7_zeros (M9 35.36 W). The watcher must trip on three live samples
                  over 30 W while the launch runs; exit 4.
  STOPTEST-DIE    abs_stop_c 30 C: the die reads about 45 C on this card at rest, so the watcher must trip on the first live sample, before any launch.

THE SMOKE: the idle card (30 s, the session's rest reading), then a 2 s launch of each type's zeros anchor (fp32, fp16, int8 anchor7_zeros), each with
the kernel's cycles per op (546 / 546 / 318) and its C log checked on the box (queue_e165.py step 5), and the DMA rule (E160's).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e165.json")))
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
SMOKE_TILES = C.ZEROS_ANCHORS
STOPTEST_TILE = "fp32.anchor7_zeros"
SESSION_CAP_MIN = 40
DRY_PASSES = 2


def run_of(label):
    n = C.name_of(label)
    if n is not None:
        t = P["tiles"][n]
        assert not t["left_out"], label
        return {"type": t["type"], "values": t["values"], "label": t["label"]}
    r = P["replicate"][label]
    return {"type": r["type"], "values": r["values"], "label": label}


def build(dry):
    burst = {"launch": {"seconds": 1.5, "budget": 3, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    for n in SMOKE_TILES:
        t = P["tiles"][n]
        smoke.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of each type's zeros anchor, C logged",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    order = [o for o in P["order"] if not dry or o["pass"] <= DRY_PASSES]
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E160's and E143's BURST block), C logged; the registered "
                                   "order, each pass opening with the zeros anchors",
         "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": [run_of(o["label"]) for o in order]}
    b.update(burst)
    blocks.append(b)
    r = P["rules"]
    return {"experiment": "E165", "request": "Q141(g)", "card": "aifoundry2", "order_seed": P["order_seed"],
            "note": "blind pool 7 under aifoundry2's own governor in 6 s bursts (E160's harness and shape, E80's kernel), every launch's C logged by Q139(k)'s "
                    "host; the registered order (3 passes of 57, each opening with the zeros anchors); 6 tiles left out by name; every start is cool; nothing is "
                    "set on the card",
            "order": {"source": "tools/claims-v3/e165/predictions-e165.json order", "runs": len(order), "runs_per_pass": P["runs_per_pass"],
                      "passes": sorted({o["pass"] for o in order})},
            "tools": {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.ETTELEM_REL},
            "ccheck": {"host": C.CC_HOST_REL, "host_sha256": C.CC_HOST_SHA256, "wrapper": C.WRAPPER_REL, "wrapper_sha256": C.CCHECK_FROZEN[C.WRAPPER_REL],
                       "kernel": C.KERNEL_REL, "kernel_sha256": C.E80_SHA256[C.KERNEL_REL], "log": "<session dir>/c-log.jsonl"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e165/predictions-e165.json",
            "left_out_by_name": P["left_out"],
            "sampler": {"every_ms": 100}, "safety": dict(r["safety"]), "caps": {"max_card_min": SESSION_CAP_MIN},
            "smoke_cycles": {P["tiles"][n]["label"]: CYCLES[P["tiles"][n]["type"]] for n in SMOKE_TILES}, "dry_c_w": P["dry_c_w"],
            "dma": {"e143_smoke_gap_ms_median": P["dma"]["e143"]["smoke"]["launch_gap_ms_median"], "e143_s1_held_s_max": P["dma"]["e143"]["s1"]["device_held_s_max"],
                    "launches": r["dma"]["launches"], "projected_held_max_s": r["dma"]["projected_held_max_s"], "budget_s": r["dma"]["budget_s"]},
            "limit_p800_w": r["limit_w"], "peak_lock_w": r["peak_lock_w"],
            "relation": {"B800": P["relation"]["B800"], "s800": P["relation"]["s800"]}, "admission": P["admission"], "blocks": blocks}


def stoptest(kind, dry):
    """the same runner, wrapper and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    t = P["tiles"][STOPTEST_TILE]
    run = {"type": t["type"], "values": t["values"], "label": t["label"], "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5},
           "launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": P["rules"]["safety"]["abs_stop_c"], "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": P["rules"]["safety"]["board_cap_w"], "cap_consecutive": 3}
    p["note"] = f"E165's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
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
    n = len(bl["runs"])
    ct = P["card_time"]
    print(f"block BURST: {n} bursts in the registered order ({P['passes']} passes of {P['runs_per_pass']}, each opening with the zeros anchors; order_seed "
          f"{P['order_seed']}); about {n * ct['s_per_burst'] / 60:.1f} card-minutes at E160's {ct['s_per_burst']} s a burst, plus the smoke and the two stop "
          f"tests (E160: {ct['e160_before_s1_min']} min); the session's cap {p['caps']['max_card_min']} min cuts pass 3's tail; the subset (passes 1-2, "
          f"{ct['e165_two_pass_subset_bursts']} bursts, about {ct['e165_two_pass_subset_min']} min) under --cap {ct['subset_cap_min']:g}")
    print(f"left out by name (in no run): {p['left_out_by_name']}; E80's fp32 randn dropped")
    for i, r in enumerate(bl["runs"]):
        a = p["admission"][r["label"]]
        o = P["order"][i]
        print(f"  {i:3d} pass {o['pass']} {'Z ' if o['first_of_pass'] else '  '}{r['label']:42s} {r['type']} est {a['fixed_p800_w']} W")
    top = max(p["admission"][r["label"]]["fixed_p800_w"] for r in bl["runs"])
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    print(f"heater {p['tools']['heater']} -> {p['ccheck']['host']} ({p['ccheck']['host_sha256'][:16]}...), kernel {p['tools']['kernel']} ({p['ccheck']['kernel_sha256'][:16]}...); dma rule {p['dma']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")
    d = build(True)
    print(f"dry twin: {len(d['blocks'][1]['runs'])} runs (passes 1-{DRY_PASSES}) at {d['blocks'][1]['launch']['seconds']} s")


if __name__ == "__main__":
    main()
