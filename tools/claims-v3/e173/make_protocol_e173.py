#!/usr/bin/env python3
"""E173 (Q142(kg)): writes protocol.json, protocol-subset.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json,
protocol-stoptest-die.json and their dry twins) from predictions-e173.json; prints protocol.txt. No card. It is E165's make_protocol_e165.py with
pool 8, the registered order, the subset protocol and each protocol's order entries (the scorer maps every run to the order through them).

    python3 -B tools/claims-v3/e173/make_protocol_e173.py > tools/claims-v3/e173/protocol.txt

THE BURST is E165's: one 6 s process (budget 7.5 s) of `sparsity_host --test fma` on the tile from a die reading <= 55 C (max wait 300 s), a 4 s
tail, the sampler every 100 ms without --reset-ms. The heater is Q139(k)'s wrapper running the C-logging host E160 built on aifoundry2 with E80's
kernel; the sampler is E80's ettelem build. Nothing is set on the card.

THE BLOCK: BURST, the 165 runs of the registered order ("passes": 1, "shuffle": false, so run_hpl.py keeps it and every run's idx is its index
in the protocol): 3 passes of 55, each opening with the three zeros anchors. protocol-subset.json: passes 1-2 (110 runs) under --cap 28.
protocol-dry.json: the dry twin's short order (22 runs, the zeros anchors, 3 governed and 3 pinned scored tiles, E80's two replicates, passes 1-2)
at 1.5 s, the toy card only. Every protocol carries order_entries: [{idx, registered_idx, pass, label}] and its order_source.

THE STOPS (E165's): one die reading >= 76 C, or the board above 85 W on three samples in a row, ends the session. The admission (run_e105.py): a
run starts only if its frozen estimate is <= 82 W; after a run whose highest board sample reached 82 W, nothing at or above that run's estimate runs.

THE STOP-PATH TESTS (after the smoke, before the session; the queue halts unless both pass): STOPTEST-BOARD (30 W on three samples, one 6 s burst
of fp32.anchor7_zeros) and STOPTEST-DIE (30 C: the die reads about 45 C at rest, so the watcher trips on the first live sample, before any launch).

THE SMOKE: the idle card (30 s, the rest reading), then a 2 s launch of each type's zeros anchor, cycles per op 546 / 546 / 318, C logged.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e173_common as C  # noqa: E402

with open(os.path.join(HERE, "predictions-e173.json")) as _f:
    P = json.load(_f)
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
SMOKE_TILES = C.ZEROS_ANCHORS
STOPTEST_TILE = "fp32.anchor7_zeros"


def run_of(label):
    n = C.name_of(label)
    if n is not None:
        t = P["tiles"][n]
        assert not t["left_out"], label
        return {"type": t["type"], "values": t["values"], "label": t["label"]}
    r = P["replicate"][label]
    return {"type": r["type"], "values": r["values"], "label": label}


def build(kind):
    """kind: full | subset | dry"""
    dry = kind == "dry"
    burst = {"launch": {"seconds": 1.5, "budget": 3, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    for n in SMOKE_TILES:
        t = P["tiles"][n]
        smoke.append({"type": t["type"], "values": t["values"], "label": t["label"]})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of each type's zeros anchor, C logged",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    if kind == "dry":
        src, order = "dry_order", list(P["dry_order"])
    elif kind == "subset":
        src, order = "order", [o for o in P["order"] if o["pass"] in C.SUBSET_PASSES]
    else:
        src, order = "order", list(P["order"])
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E165's BURST block), C logged; the registered order, "
                                   "each pass opening with the zeros anchors",
         "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": [run_of(o["label"]) for o in order]}
    b.update(burst)
    blocks.append(b)
    r = P["rules"]
    caps = {"full": C.CAP_CARD_MIN, "subset": C.SUBSET_CAP_MIN, "dry": 30}[kind]
    return {"experiment": "E173", "request": "Q142(kg)", "card": "aifoundry2", "kind": kind, "order_seed": P["order_seed"],
            "note": "blind pool 8 under aifoundry2's own governor in 6 s bursts (E165's harness and shape, E80's kernel), every launch's C logged by Q139(k)'s "
                    "host; the registered order (3 passes of 55, each opening with the zeros anchors); the 11 tiles over 82 W left out by name; every start "
                    "is cool; nothing is set on the card",
            "order_source": src, "order_entries": [{"idx": i, "registered_idx": o["idx"], "pass": o["pass"], "label": o["label"]} for i, o in enumerate(order)],
            "order": {"source": f"tools/claims-v3/e173/predictions-e173.json {src}", "runs": len(order), "passes": sorted({o["pass"] for o in order})},
            "tools": {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.ETTELEM_REL},
            "ccheck": {"host": C.CC_HOST_REL, "host_sha256": C.CC_HOST_SHA256, "wrapper": C.WRAPPER_REL, "wrapper_sha256": C.CCHECK_FROZEN[C.WRAPPER_REL],
                       "kernel": C.KERNEL_REL, "kernel_sha256": C.E80_SHA256[C.KERNEL_REL], "log": "<session dir>/c-log.jsonl"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e173/predictions-e173.json",
            "left_out_by_name": P["left_out"], "sampler": {"every_ms": 100}, "safety": dict(r["safety"]), "caps": {"max_card_min": caps},
            "smoke_cycles": {P["tiles"][n]["label"]: CYCLES[P["tiles"][n]["type"]] for n in SMOKE_TILES}, "dry_c_w": P["dry_c_w"],
            "dma": {"e143_smoke_gap_ms_median": P["dma"]["e143"]["smoke"]["launch_gap_ms_median"], "e143_s1_held_s_max": P["dma"]["e143"]["s1"]["device_held_s_max"],
                    "launches": r["dma"]["launches"], "projected_held_max_s": r["dma"]["projected_held_max_s"], "budget_s": r["dma"]["budget_s"]},
            "limit_p800_w": r["limit_w"], "peak_lock_w": r["peak_lock_w"], "relation": {"B800": P["relation"]["B800"], "s800": P["relation"]["s800"]},
            "admission": P["admission"], "blocks": blocks}


def stoptest(kind, dry):
    p = build("dry" if dry else "full")
    t = P["tiles"][STOPTEST_TILE]
    run = {"type": t["type"], "values": t["values"], "label": t["label"], "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5},
           "launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    p["order_entries"], p["order_source"], p["kind"] = [], "none", f"stoptest-{kind}"
    if kind == "board":
        p["safety"] = {"abs_stop_c": P["rules"]["safety"]["abs_stop_c"], "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": P["rules"]["safety"]["board_cap_w"], "cap_consecutive": 3}
    p["note"] = f"E173's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    outs = {"protocol.json": build("full"), "protocol-subset.json": build("subset"), "protocol-dry.json": build("dry")}
    for kind in ("board", "die"):
        outs[f"protocol-stoptest-{kind}.json"] = stoptest(kind, False)
        outs[f"protocol-stoptest-{kind}-dry.json"] = stoptest(kind, True)
    for name, p in outs.items():
        with open(os.path.join(HERE, name), "w") as f:
            json.dump(p, f, indent=1)
    p = outs["protocol.json"]
    bl = p["blocks"][1]
    ct = P["card_time"]
    print(f"block BURST: {len(bl['runs'])} bursts in the registered order ({P['passes']} passes of {P['runs_per_pass']}, each opening with the zeros "
          f"anchors; order_seed {P['order_seed']}); about {ct['e173_session_min']} card-minutes at E165's {ct['s_per_burst']} s a burst, plus the smoke and "
          f"the two stop tests (E165: {ct['e165_before_s1_min']} min); cap {p['caps']['max_card_min']} min; slot {C.SLOT_MIN} min")
    print(f"subset: {len(outs['protocol-subset.json']['blocks'][1]['runs'])} bursts (passes {list(C.SUBSET_PASSES)}), cap {C.SUBSET_CAP_MIN}, slot {C.SUBSET_SLOT_MIN} min")
    print(f"left out by name (in no run): {p['left_out_by_name']}")
    for i, r in enumerate(bl["runs"]):
        o = P["order"][i]
        print(f"  {i:3d} pass {o['pass']} {'Z ' if o['first_of_pass'] else '  '}{r['label']:44s} {r['type']} est {p['admission'][r['label']]['fixed_p800_w']} W")
    top = max(p["admission"][r["label"]]["fixed_p800_w"] for r in bl["runs"])
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    print(f"heater {p['tools']['heater']} -> {p['ccheck']['host']} ({p['ccheck']['host_sha256'][:16]}...), kernel {p['tools']['kernel']} "
          f"({p['ccheck']['kernel_sha256'][:16]}...); dma rule {p['dma']}")
    for kind in ("board", "die"):
        q = outs[f"protocol-stoptest-{kind}.json"]
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")
    d = outs["protocol-dry.json"]
    print(f"dry twin: {len(d['blocks'][1]['runs'])} runs (passes {d['order']['passes']}) at {d['blocks'][1]['launch']['seconds']} s")
    for name in outs:
        print(f"{name}: sha256 {C.sha256_file(os.path.join(HERE, name))}")


if __name__ == "__main__":
    main()
