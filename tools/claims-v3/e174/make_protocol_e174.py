#!/usr/bin/env python3
"""E174 (Q142(kg)): writes protocol.json, protocol-subset.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json,
protocol-stoptest-die.json and their dry twins) from predictions-e174.json; prints protocol.txt. No card. It is E170's make_protocol_e170.py with
pool 8, the ramp's second tile, each protocol's order entries and the dry twin's short order.

    python3 -B tools/claims-v3/e174/make_protocol_e174.py > tools/claims-v3/e174/protocol.txt

THE BURST is E170's (E165's): one 6 s process (budget 7.5 s) from a die reading <= 55 C (max wait 300 s), a 4 s tail, the sampler every 100 ms
without --reset-ms; the heater Q139(k)'s wrapper running the C-logging host E157 built on aifoundry1 with E78's kernel there; the sampler and every
query through E170's guard in front of E84's ettelem build. Nothing is set on the card.

THE BLOCK: BURST, the 126 runs of the registered order ("passes": 1, "shuffle": false): half A (passes 1-3: the three zeros anchors, then tier A's
26 tiles shuffled), then half B (passes 4-6: the three zeros anchors, then tier B's 10 tiles in ascending card-0 estimate, the hottest last).
protocol-subset.json: passes 1, 2, 4 and 5 (84 runs) under --cap 25. protocol-dry.json: the dry twin's short order (24 runs: passes 1-2 of the zeros
and 6 scored tier-A tiles, pass 4 of the zeros and 3 scored tier-B tiles) at 1.5 s, the toy card only. Every protocol carries order_entries.

THE STOPS (E170's): one die reading >= 72 C, or one board sample above 65.9 W, ends the session; the alarm check (any sampler line under 590 MHz)
after every run; the admission at 60 W on the card-0 estimate; E105's lock at 62 W.

THE STOP-PATH TESTS (before the smoke): STOPTEST-DIE (30 C: the die reads 47-57 C at rest, so the watcher trips on the first live sample, before any
launch); STOPTEST-BOARD (25 W on one sample, one 6 s burst of int8.anchor7_zeros, about 30 W on card 0; the dry twin's toy card idles near 23 W, so
its line is 30 W).

THE SMOKE, ramped (after the stop tests, under the session's stops): the idle card (30 s, the rest reading), a 2 s launch of int8.anchor7_zeros, then a
2 s launch of fp32.b_onebit_b20_one (estimate 57.69 W, the second-hottest admitted; E170 measured it on this card at 53.0 W, peak 56.4 W).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e174_common as C  # noqa: E402

with open(os.path.join(HERE, "predictions-e174.json")) as _f:
    P = json.load(_f)
with open(os.path.join(HERE, "..", "e173", "predictions-e173.json")) as _f:
    P173 = json.load(_f)      # the toy card's c per pool-8 tile value (dry passes only) and aifoundry2's relation, which E105 needs to report c
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}


def run_of(name):
    t = P["tiles"][name]
    return {"type": t["type"], "values": t["values"], "label": t["label"]}


def admission():
    a = {"rest": {"c_ref_w": 0.0, "fixed_p800_w": C.REST_W, "what": "the idle card (no launch): card 0's highest idle reading in E84"}}
    for n, t in P["tiles"].items():
        a[t["label"]] = {"fixed_p800_w": t["est_card0_peak_w"], "what": "the card-0 estimate of the tile's 95% upper peak (predictions-e174.json)"}
    return a


def dry_c():
    vals = {P["tiles"][n]["values"] for n in P["tiles"]}
    return {v: c for v, c in P173["dry_c_w"].items() if v in vals}


def build(kind):
    dry = kind == "dry"
    burst = {"launch": {"seconds": 1.5, "budget": 3, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke += [run_of(n) for n in C.SMOKE_TILES]
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of int8.anchor7_zeros "
                                         "(low power) and a 2 s launch of fp32.b_onebit_b20_one (the second-hottest admitted kind), C logged, under the session's stops",
               "default": False, "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3,
               "runs": smoke}]
    if dry:
        src, order = "dry_order", list(P["dry_order"])
    elif kind == "subset":
        src, order = "order", [o for o in P["order"] if o["pass"] in C.SUBSET_PASSES]
    else:
        src, order = "order", list(P["order"])
    b = {"name": "BURST", "title": "a burst on a cool die: one 6 s process from a die reading <= 55 C (E165's BURST block), C logged; the registered order, "
                                   "each pass opening with the zeros anchors, half B (the hottest kinds) last",
         "passes": 1, "shuffle": False, "start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}, "runs": [run_of(o["name"]) for o in order]}
    b.update(burst)
    blocks.append(b)
    caps = {"full": C.CAP_CARD_MIN, "subset": C.SUBSET_CAP_MIN, "dry": 30}[kind]
    return {"experiment": "E174", "request": "Q142(kg)", "card": "aifoundry1-c0", "kind": kind, "order_seed": P["order_seed"],
            "note": "blind pool 8 on aifoundry1 card 0 under its own governor in 6 s bursts at the 800 MHz cap (E170's harness and form), every launch's C "
                    "logged; the registered order (half A passes 1-3, half B passes 4-6, each pass opening with the zeros anchors); 25 tiles left out by name; "
                    "every start is cool; nothing is set on the card",
            "order_source": src, "order_entries": [{"idx": i, "registered_idx": o["idx"], "pass": o["pass"], "label": o["label"]} for i, o in enumerate(order)],
            "order": {"source": f"tools/claims-v3/e174/predictions-e174.json {src}", "runs": len(order), "passes": sorted({o["pass"] for o in order})},
            "tools": {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.GUARD_REL},
            "ccheck": {"host": C.CC_HOST_REL, "host_sha256": C.CC_HOST_SHA256, "wrapper": C.WRAPPER_REL, "wrapper_sha256": C.CCHECK_FROZEN[C.WRAPPER_REL],
                       "kernel": C.KERNEL_REL, "kernel_sha256": C.KERNEL_SHA256, "log": "<session dir>/c-log.jsonl"},
            "ettelem_real": {"path": C.ETTELEM_REL, "sha256": C.ETTELEM_SHA256},
            "kinds": "tools/claims-v3/kinds/kinds.json", "pool": C.MAN_REL, "predictions": "tools/claims-v3/e174/predictions-e174.json",
            "left_out_by_name": sorted(P["left_out"]), "sampler": {"every_ms": 100}, "safety": dict(C.SAFETY), "caps": {"max_card_min": caps},
            "smoke_cycles": {P["tiles"][n]["label"]: CYCLES[P["tiles"][n]["type"]] for n in C.SMOKE_TILES}, "dry_c_w": dry_c(),
            "dma": {"e143_smoke_gap_ms_median": 1.0, "e143_s1_held_s_max": 6.57, "launches": 17, "projected_held_max_s": 7.2, "budget_s": 7.5},
            "limit_p800_w": C.ADMIT_LINE_W, "peak_lock_w": C.PEAK_LOCK_W, "relation": {"B800": P173["relation"]["B800"], "s800": P173["relation"]["s800"]},
            "admission": admission(), "blocks": blocks}


def stoptest(kind, dry):
    p = build("dry" if dry else "full")
    run = dict(run_of(C.STOPTEST_TILE), start={"mode": "cool", "max_c": 99, "max_wait_s": 5},
               launch={"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, tail_s=0.5 if dry else 4)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    p["order_entries"], p["order_source"], p["kind"] = [], "none", f"stoptest-{kind}"
    if kind == "board":
        p["safety"] = {"abs_stop_c": C.SAFETY["abs_stop_c"], "board_cap_w": 30 if dry else 25, "cap_consecutive": 1}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": C.SAFETY["board_cap_w"], "cap_consecutive": 1}
    p["note"] = f"E174's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
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
    print(f"block BURST: {len(bl['runs'])} bursts in the registered order (half A passes 1-3, half B passes 4-6, each opening with the zeros anchors); "
          f"about {ct['e174_session_min']} card-minutes at E170's {ct['s_per_burst']} s a burst, plus the state reads, the stop tests and the smoke "
          f"(E170: {ct['e170_before_s1_min']} min); cap {p['caps']['max_card_min']} min; slot {C.SLOT_MIN} min")
    print(f"subset: {len(outs['protocol-subset.json']['blocks'][1]['runs'])} bursts (passes {list(C.SUBSET_PASSES)}), cap {C.SUBSET_CAP_MIN}, slot {C.SUBSET_SLOT_MIN} min")
    print(f"left out by name (in no run): {len(p['left_out_by_name'])}")
    for i, r in enumerate(bl["runs"]):
        o = P["order"][i]
        print(f"  {i:3d} pass {o['pass']} half {o['half']} {r['label']:44s} {r['type']} est {p['admission'][r['label']]['fixed_p800_w']} W")
    top = max(p["admission"][r["label"]]["fixed_p800_w"] for r in bl["runs"])
    print(f"highest planned estimate {top} W; admission line {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke "
          f"{[r['label'] for r in p['blocks'][0]['runs']]} cycles {p['smoke_cycles']}")
    print(f"heater {p['tools']['heater']} -> {p['ccheck']['host']} ({p['ccheck']['host_sha256'][:16]}...), kernel {p['tools']['kernel']} "
          f"({p['ccheck']['kernel_sha256'][:16]}...), ettelem {p['tools']['ettelem']} -> {C.ETTELEM_REL} ({C.ETTELEM_SHA256[:16]}...)")
    for kind in ("board", "die"):
        q = outs[f"protocol-stoptest-{kind}.json"]
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']}")
    d = outs["protocol-dry.json"]
    print(f"dry twin: {len(d['blocks'][1]['runs'])} runs (passes {d['order']['passes']}) at {d['blocks'][1]['launch']['seconds']} s; dry_c_w {len(d['dry_c_w'])} values")
    for name in outs:
        print(f"{name}: sha256 {C.sha256_file(os.path.join(HERE, name))}")


if __name__ == "__main__":
    main()
