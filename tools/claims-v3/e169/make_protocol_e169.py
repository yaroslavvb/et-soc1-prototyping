#!/usr/bin/env python3
"""E169 (Q141(s)): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json,
protocol-stoptest-die.json and their dry twins) from REGISTRATION-A2.md's design (D2, D3, D7) and kit-e169.json; prints protocol.txt.
E158's make_protocol_e158.py ported: its burst, its smoke form, its stop-path tests, its keys. No card.

    nice -n 10 python3 -B tools/claims-v3/e169/make_protocol_e169.py > tools/claims-v3/e169/protocol.txt

THE DESIGN (REGISTRATION-A2.md D2-D3; the brief's "every shape an argument of E136's binary"): a burst is one 6 s process from a die
reading <= 55 C (waiting at most 300 s), its tail 4 s, as E158. Every cell is zeros (the format's zero tile through the pool).
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four cells' zeros (P1 fp32, N2 fp16, P3 int8, N3 fp32),
         each with its check of C, its cycles per op within 50-250% of STRICT's frozen T800 x 800 (kit-e169.json smoke_cycles).
  A      pass 1, fp32: N1 P1 N2 P2 N3 P3, then the ties K4n7 K4n8 K6n5 K6n4 (in that order: each N before its P).
  B      pass 2: A's ten, shuffled.
  C D E  passes 3, 4 and 5: the six E169 shapes, each block shuffled.
  F      the formats, printed if run: the six shapes in fp16, then in int8 (pass 1 of each), in order.
  The shuffles use run_hpl.py's one generator over the blocks (order_seed 169). 50 bursts. The registered subset: A, B and C.
THE STOPS (D7): the board above 60 W on three samples in a row, a die reading (the minion shires' mean or hottest sensor) at or above 76 C,
the admission limit 82 W at the estimate, the peak lock 60 W. THE STOP-PATH TESTS (E158's): stoptest-board (board_cap_w 30 W; one 6 s
burst of K4n8 fp32 zeros, E158's own test burst) and stoptest-die (abs_stop_c 30 C), each must fire on live samples or the queue halts.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = json.load(open(os.path.join(HERE, "kit-e169.json")))
CELLS = KIT["cells"]
E169 = ("N1", "P1", "N2", "P2", "N3", "P3")
TIES = ("K4n7", "K4n8", "K6n5", "K6n4")
CAP_MIN = 20
SEED = 169


def run(label, dry, start=None):
    c = CELLS[label]
    r = {"type": c["type"], "values": c["values"], "label": label}
    r.update({"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4})
    r["start"] = dict(start or {"mode": "cool", "max_c": 55, "max_wait_s": 300})
    return r


def plan():
    pair = [f"{s}-fp32-zeros" for s in E169]
    ties = [f"{s}-fp32-zeros" for s in TIES]
    fmts = [f"{s}-{t}-zeros" for t in ("fp16", "int8") for s in E169]
    return [("A", "pass 1: the six E169 shapes, each N before its P, then E158's four tie rungs (fp32 zeros)", pair + ties, False),
            ("B", "pass 2: A's ten, shuffled", pair + ties, True),
            ("C", "pass 3: the six E169 shapes, shuffled", pair, True),
            ("D", "pass 4: the six E169 shapes, shuffled", pair, True),
            ("E", "pass 5: the six E169 shapes, shuffled", pair, True),
            ("F", "the formats, printed if run: the six shapes in fp16, then in int8 (pass 1 of each)", fmts, False)]


def build(dry):
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    for lab in KIT["smoke_cells"]:
        c = CELLS[lab]
        smoke.append({"type": c["type"], "values": c["values"], "label": lab})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four cells' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke}]
    for name, title, labels, shuffle in plan():
        blocks.append({"name": name, "title": title, "passes": 1, "shuffle": shuffle, "runs": [run(lab, dry) for lab in labels]})
    dry_c = {"zeros": 3.0}
    for c in CELLS.values():
        dry_c[c["values"]] = c["c600_w"]
    rel = KIT["relation"]
    return {"experiment": "E169", "request": "Q141(s)", "card": "aifoundry2", "order_seed": SEED,
            "note": "E169: the stride shapes, P1-P3 at power-of-two panel strides against N1-N3, five passes of fp32 zeros bursts with E158's four tie rungs in two, then fp16 and int8 printed if run; E158's harness (every shape an argument of E136's binary) under aifoundry2's own governor; every start cool; nothing is set on the card",
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/predictions-e169.json",
            "registration": "docs/reports/data/2026-11-04-q140q-gemm-g4-stride/REGISTRATION.md (49575094) and tools/claims-v3/e169/REGISTRATION-A2.md (217c94a2)",
            "sampler": {"every_ms": 100}, "safety": dict(KIT["safety"]), "caps": {"max_card_min": CAP_MIN}, "smoke_cycles": dict(KIT["smoke_cycles"]), "dry_c_w": dry_c,
            "limit_p800_w": KIT["limit_p800_w"], "peak_lock_w": KIT["peak_lock_w"], "relation": {"B800": rel["B"]["800"], "s800": rel["s800"]},
            "admission": dict(KIT["admission"]), "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples (E158's, unchanged in form)"""
    p = build(dry)
    r = run("K4n8-fp32-zeros", dry, {"mode": "cool", "max_c": 99, "max_wait_s": 5})
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [r]}]
    sf = KIT["safety"]
    p["safety"] = ({"abs_stop_c": sf["abs_stop_c"], "board_cap_w": 30, "cap_consecutive": 3} if kind == "board"
                   else {"abs_stop_c": 30, "board_cap_w": sf["board_cap_w"], "cap_consecutive": 3})
    p["note"] = f"E169's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    n, est, top = 0, 0.0, 0.0
    print(f"E169 protocol (REGISTRATION-A2.md D2-D3, D7; kit-e169.json): session stops {p['safety']}; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; "
          f"session cap {p['caps']['max_card_min']} card-minutes; order_seed {p['order_seed']}")
    for bl in p["blocks"]:
        print(f"block {bl['name']}: {bl['title']}{' (shuffled at run time by run_hpl.py' + chr(39) + 's one generator over the blocks)' if bl.get('shuffle') else ''}")
        for r in bl["runs"]:
            if bl["name"] != "SMOKE":
                n += 1
                est += 12.1
            a = p["admission"].get(r["label"], {})
            top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:16s} {r['values'][:62]:62s} estimate {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    sub = sum(len(b["runs"]) for b in p["blocks"] if b["name"] in ("A", "B", "C"))
    print(f"{n} bursts, about {est / 60:.1f} card-minutes at 12.1 s a zeros burst (E158: 98 in 19.7 min), plus the smoke and the two stop tests (about 1.1 min in E158); "
          f"the registered subset A-C is {sub} bursts, about {sub * 12.1 / 60:.1f} min")
    print(f"highest planned estimate (the predicted peak) {top} W; smoke cycles {p['smoke_cycles']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
