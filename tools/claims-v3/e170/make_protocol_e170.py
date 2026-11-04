#!/usr/bin/env python3
"""E170 (Q141(w)): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and
their dry twins) from predictions-e170.json; prints protocol.txt. No card. It is E165's make_protocol_e165.py with card 0's tools, stops, smoke and
order.

    python3 -B tools/claims-v3/e170/make_protocol_e170.py > tools/claims-v3/e170/protocol.txt

THE BURST is E165's: one 6 s process (budget 7.5 s) of `sparsity_host --test fma` on the tile from a die reading <= 55 C (max wait 300 s), a 4 s tail,
the sampler every 100 ms without --reset-ms. The heater is Q139(k)'s wrapper running the C-logging host E157 built on aifoundry1 with E78's kernel
there; the sampler and every query go through E170's guard in front of E84's ettelem build. Nothing is set on the card.

THE BLOCK: BURST, the 135 runs of predictions-e170.json's registered order, listed in that order ("passes": 1, "shuffle": false, so run_hpl.py's
load_protocol keeps it and every run's idx is its index in the order): half A (passes 1-3: the three zeros anchors, then tier A shuffled), then half
B (passes 4-6: the three zeros anchors, then tier B in ascending card-0 estimate, the hottest last). The 19 tiles left out by name are in no run.
The dry twin lists passes 1 and 4 at 1.5 s. The session's cap (40 card-minutes) cuts the tail if the gates run long; the registered subset (passes
1, 2, 4 and 5) is protocol-subset.json under --cap 25.

THE STOPS (E170.md "Safety", at least as strict as E164's 66 W / 72 C): one die reading at or above 72 C, or one board sample above 65.9 W, ends the
session. The admission rule (run_e105.py): a run starts only if its card-0 estimate is <= 60 W; after a run whose highest board sample reached 62 W,
nothing at or above that run's estimate runs.

THE STOP-PATH TESTS (before the smoke; the queue halts unless both pass):
  STOPTEST-DIE    abs_stop_c 30 C: card 0's die reads 47-57 C at rest, so the watcher must trip on the first live sample, before any launch.
  STOPTEST-BOARD  board_cap_w 25 W on one sample: one 6 s burst of int8.anchor7_zeros (about 30 W at 800 MHz on card 0; its idle 19-21 W). The
                  watcher must trip on a live sample over 25 W while the launch runs; exit 4. (The dry twin's toy card idles near 23 W, so its
                  twin's line is 30 W: the toy's, never the box's.)

THE SMOKE, ramped (after the stop tests; under the session's stops): the idle card (30 s, the rest reading), then a 2 s launch of int8.anchor7_zeros
(the low-power tile), then a 2 s launch of fp32.randn_a24k (fp32 random data with A 2:4 sparse: the session's fp32 random kind, card-0 estimate 58.0 W),
each with its cycles per op (318 / 546) and its C log checked on the box (queue_e170.py).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e170_common as C  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e170.json")))
P165 = json.load(open(os.path.join(C.ROOT, "tools/claims-v3/e165/protocol-dry.json")))
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
SMOKE_TILES = ("int8.anchor7_zeros", "fp32.randn_a24k")
STOPTEST_TILE = "int8.anchor7_zeros"
REST_W = 21.2              # card 0's highest idle reading between E84's runs (results.json runs[].idle_w): the rest run's admission estimate
DRY_PASSES = (1, 4)
SUBSET_PASSES = (1, 2, 4, 5)
E84_DRY_RELATION = {"B800": 33.60956684526229, "s800": 1.90517380064275}   # E165's (aifoundry2's): E105 needs it; c is reported, never a rule


def run_of(name):
    t = P["tiles"][name]
    return {"type": t["type"], "values": C.tile_value(C.manifest()[name]), "label": t["label"]}


def admission():
    a = {"rest": {"c_ref_w": 0.0, "fixed_p800_w": REST_W, "what": "the idle card (no launch): card 0's highest idle reading in E84"}}
    for n, t in P["tiles"].items():
        a[t["label"]] = {"fixed_p800_w": t["est_card0_peak_w"], "what": "the card-0 estimate of the tile's 95% upper peak (predictions-e170.json)"}
    return a


def dry_c():
    vals = {C.tile_value(C.manifest()[n]) for n in P["tiles"]}
    return {v: c for v, c in P165["dry_c_w"].items() if v in vals}


def build(dry, passes=None):
    burst = {"launch": {"seconds": 1.5, "budget": 3, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke += [run_of(n) for n in SMOKE_TILES]
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of int8.anchor7_zeros "
                                         "(low power) and a 2 s launch of fp32.randn_a24k (the session's fp32 random kind), C logged, under the session's stops",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    keep = passes or (DRY_PASSES if dry else None)
    order = [o for o in P["order"] if keep is None or o["pass"] in keep]
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E165's BURST block), C logged; the registered order, "
                                   "each pass opening with the zeros anchors, half B (the hottest kinds) last",
         "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": [run_of(o["name"]) for o in order]}
    b.update(burst)
    blocks.append(b)
    p = {"experiment": "E170", "request": "Q141(w)", "card": "aifoundry1-c0", "order_seed": P["order_seed"],
         "note": "blind pool 7 on aifoundry1 card 0 under its own governor in 6 s bursts at the 800 MHz cap (E165's harness and shape over E84's card-0 runner), "
                 "every launch's C logged by Q139(k)'s host; the registered order (half A passes 1-3, half B passes 4-6, each pass opening with the zeros anchors); "
                 "19 tiles left out by name; every start is cool; nothing is set on the card",
         "order": {"source": "tools/claims-v3/e170/predictions-e170.json order", "runs": len(order), "passes": sorted({o["pass"] for o in order})},
         "tools": {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.GUARD_REL},
         "ccheck": {"host": C.CC_HOST_REL, "host_sha256": C.CC_HOST_SHA256, "wrapper": C.WRAPPER_REL, "wrapper_sha256": C.CCHECK_FROZEN[C.WRAPPER_REL],
                    "kernel": C.KERNEL_REL, "kernel_sha256": C.KERNEL_SHA256, "log": "<session dir>/c-log.jsonl"},
         "ettelem_real": {"path": C.ETTELEM_REL, "sha256": C.ETTELEM_SHA256},
         "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e170/predictions-e170.json",
         "left_out_by_name": sorted(P["left_out"]),
         "sampler": {"every_ms": 100}, "safety": dict(C.SAFETY), "caps": {"max_card_min": C.CAP_CARD_MIN},
         "smoke_cycles": {P["tiles"][n]["label"]: CYCLES[P["tiles"][n]["type"]] for n in SMOKE_TILES}, "dry_c_w": dry_c(),
         "dma": {"e143_smoke_gap_ms_median": 1.0, "e143_s1_held_s_max": 6.57, "launches": 17, "projected_held_max_s": 7.2, "budget_s": 7.5},
         "limit_p800_w": C.ADMIT_LINE_W, "peak_lock_w": C.PEAK_LOCK_W, "relation": dict(E84_DRY_RELATION), "admission": admission(), "blocks": blocks}
    return p


def stoptest(kind, dry):
    """the same runner, wrapper and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    run = dict(run_of(STOPTEST_TILE), start={"mode": "cool", "max_c": 99, "max_wait_s": 5},
               launch={"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, tail_s=0.5 if dry else 4)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": C.SAFETY["abs_stop_c"], "board_cap_w": 30 if dry else 25, "cap_consecutive": 1}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": C.SAFETY["board_cap_w"], "cap_consecutive": 1}
    p["note"] = f"E170's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(False, SUBSET_PASSES), open(os.path.join(HERE, "protocol-subset.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    bl = p["blocks"][1]
    n = len(bl["runs"])
    ct = P["card_time"]
    print(f"block BURST: {n} bursts in the registered order (half A passes 1-3, half B passes 4-6, each opening with the zeros anchors); about "
          f"{n * ct['s_per_burst_E160'] / 60:.1f} card-minutes at E160's {ct['s_per_burst_E160']} s a burst, plus the state reads, the stop tests and the smoke "
          f"(about {ct['smoke_and_stop_tests_min']} min); cap {p['caps']['max_card_min']} min; the subset (passes {SUBSET_PASSES}) "
          f"{len(build(False, SUBSET_PASSES)['blocks'][1]['runs'])} bursts")
    print(f"left out by name (in no run): {len(p['left_out_by_name'])}")
    for i, r in enumerate(bl["runs"]):
        a = p["admission"][r["label"]]
        o = P["order"][i]
        print(f"  {i:3d} pass {o['pass']} half {o['half']} {r['label']:42s} {r['type']} est {a['fixed_p800_w']} W")
    top = max(p["admission"][r["label"]]["fixed_p800_w"] for r in bl["runs"])
    print(f"highest planned estimate {top} W; admission line {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke "
          f"{[r['label'] for r in p['blocks'][0]['runs']]} cycles {p['smoke_cycles']}")
    print(f"heater {p['tools']['heater']} -> {p['ccheck']['host']} ({p['ccheck']['host_sha256'][:16]}...), kernel {p['tools']['kernel']} "
          f"({p['ccheck']['kernel_sha256'][:16]}...), ettelem {p['tools']['ettelem']} -> {C.ETTELEM_REL} ({C.ETTELEM_SHA256[:16]}...)")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']}")
    d = build(True)
    print(f"dry twin: {len(d['blocks'][1]['runs'])} runs (passes {DRY_PASSES}) at {d['blocks'][1]['launch']['seconds']} s; dry_c_w {len(d['dry_c_w'])} values")


if __name__ == "__main__":
    main()
