#!/usr/bin/env python3
"""E160 (Q139): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from predictions-e160.json; prints protocol.txt. No card. It is E143's make_protocol_e143.py with pool 6, Q139(k)'s C-logging host and
section 22's power rule.

    python3 tools/claims-v3/e160/make_protocol_e160.py > tools/claims-v3/e160/protocol.txt

THE BURST is E143's (E80's BURST block, the shape M8's aifoundry2 term was fitted on: E80's, E83's and E143's kinds bursts): one 6 s process (budget
7.5 s) of the kinds harness (sparsity_host --test fma on the tile) from a die reading <= 55 C (max wait 300 s), a 4 s tail, the sampler every 100 ms
without --reset-ms. The heater is Q139(k)'s wrapper, tools/claims-v3/ccheck/sparsity_ccheck.sh, which runs the C-logging host
build/ccheck/b/host/sparsity_host with E80's kernel build/sparsity_t2/kernel/sparsity.elf (the runner's own --kernel, kept by the wrapper) and appends
--c-log <session>/c-log.jsonl --c-poison. Nothing is set on the card.

THE BLOCK: BURST, 3 passes, each pass pool 6's 48 tiles that run (the two whose M8 95% upper peak exceeds 82 W are DROPPED: fp32.anchor6_randn,
fp32.real_qwen_softmax_v) and E80's two replicate tiles fp16 randn and int8 full (its fp32 randn is dropped: E143 read 84.3-85.0 W on it), in a seeded
shuffled order (order_seed 160; run_hpl.py's load_protocol shuffles each pass on its own, so a pass is whole before the next starts). 150 bursts.
The session's cap (40 card-minutes; run_e119.py starts a run only if its planned time fits) cuts pass 3's tail if the gates run long.

THE STOPS (section 22: every registered board stop at most 85 W on live samples; E159's die stop), under the keys run_hpl.py's watcher reads: one die
reading (the minion shires' mean or hottest sensor) at or above 76 C, or the board above 85 W on three samples in a row, ends the session. The
admission rule (run_e105.py): a cell runs only if its frozen estimate, M8's 95% upper peak board sample, is <= 82 W; after a run whose highest board
sample reached 82 W, nothing at or above that run's estimate runs (E159's lock).

THE STOP-PATH TESTS (after the smoke, before the session; the queue halts unless both pass; E143's, through the same wrapper):
  STOPTEST-BOARD  board_cap_w 30 W (three samples): one 6 s burst of the pool's fp32.anchor6_zeros (M8: 36.35 W, peak 38.29 W). The watcher must trip
                  on three live samples over 30 W while the launch runs; the launch loop ends at its next launch boundary; exit 4.
  STOPTEST-DIE    abs_stop_c 30 C: the die reads about 45 C on this card at rest, so the watcher must trip on the first live sample, before any
                  launch; exit 4.

THE SMOKE: the idle card (30 s, the session's rest reading), then a 2 s launch of each type's zeros anchor (fp32, fp16, int8 anchor6_zeros), each with
the kernel's cycles per op (546 / 546 / 318) and its C log: the queue checks on the box, before the stop tests, that every smoke launch has a C record
with the poison written, every minion's C is +0 (zeros' C, closed form) and the log names E80's kernel and the pinned C-logging host; and it times the
C log's extra DMA (the DMA rule, predictions-e160.json rules.dma).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e160_common as C  # noqa: E402

P = json.load(open(os.path.join(HERE, "predictions-e160.json")))
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
SMOKE_TILES = ("fp32.anchor6_zeros", "fp16.anchor6_zeros", "int8.anchor6_zeros")
STOPTEST_TILE = "fp32.anchor6_zeros"
SESSION_CAP_MIN = 40


def runs_of_pass():
    rs = []
    for name in sorted(P["tiles"]):
        t = P["tiles"][name]
        if t["dropped"]:
            continue
        rs.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    for lab, r in P["replicate"].items():
        rs.append({"type": r["type"], "values": r["values"], "label": lab})
    return rs


def build(dry):
    burst = {"launch": {"seconds": 1.5, "budget": 3, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    for n in SMOKE_TILES:
        t = P["tiles"][n]
        smoke.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of each type's zeros anchor, C logged",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E143's BURST block: E80's, E64's LAD shape), C logged",
         "passes": 2 if dry else 3, "shuffle": True, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": runs_of_pass()}
    b.update(burst)
    blocks.append(b)
    r = P["rules"]
    return {"experiment": "E160", "request": "Q139", "card": "aifoundry2", "order_seed": 160,
            "note": "blind pool 6 under aifoundry2's own governor in 6 s bursts (E143's harness and shape, E80's kernel), every launch's C logged by Q139(k)'s host; "
                    "two flagged tiles dropped; every start is cool; nothing is set on the card",
            "tools": {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.ETTELEM_REL},
            "ccheck": {"host": C.CC_HOST_REL, "host_sha256": C.CC_HOST_SHA256, "wrapper": C.WRAPPER_REL, "wrapper_sha256": C.CCHECK_FROZEN[C.WRAPPER_REL],
                       "kernel": C.KERNEL_REL, "kernel_sha256": C.E80_SHA256[C.KERNEL_REL], "log": "<session dir>/c-log.jsonl"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e160/predictions-e160.json",
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
    p["note"] = f"E160's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
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
    print(f"block BURST: {bl['passes']} passes x {len(bl['runs'])} runs = {n} bursts (shuffled at run time, order_seed 160); about {est_s / 60:.0f} card-minutes at 14 s a burst "
          f"(E143: 117 bursts in 27.1 min); plus the smoke and the two stop tests (about 3 min); the session's cap {p['caps']['max_card_min']} min cuts pass 3's tail")
    print(f"dropped (not in the protocol): {P['dropped']} and {list(P['replicate_dropped'])}")
    for r in bl["runs"]:
        a = p["admission"][r["label"]]
        print(f"  {r['label']:36s} {r['type']} {r['values'][:72]:72s} est {a['fixed_p800_w']} W")
    top = max(p["admission"][r["label"]]["fixed_p800_w"] for r in bl["runs"])
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    print(f"heater {p['tools']['heater']} -> {p['ccheck']['host']} ({p['ccheck']['host_sha256'][:16]}...), kernel {p['tools']['kernel']} ({p['ccheck']['kernel_sha256'][:16]}...); dma rule {p['dma']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
