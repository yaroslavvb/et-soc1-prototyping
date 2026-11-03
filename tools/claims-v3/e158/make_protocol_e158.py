#!/usr/bin/env python3
"""E158 (Q139): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from predictions-e158.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e158/make_protocol_e158.py > tools/claims-v3/e158/protocol.txt

E146's design and parameters, unchanged (E136's, E119's, E105's, E80's): a burst is one 6 s process from a die reading <= 55 C, its tail 4 s. Every start
is cool. Nothing is set on the card. rgm136 (build/e136, E136's binary: the shapes are arguments), E119's sampler and runner (through run_e158.py).
EVERY CELL IS ZEROS (the file's zero tile through the pool, as E146's zeros cells): the kind does not move a large GEMM's time per op (E146 R7, worst
0.66%; E136 R7; E126 R7), and zeros keep every cell near 35-40 W, far under aifoundry2's 82 W design limit for this round.

THE STOPS (Q139's rule for aifoundry2: every registered board stop at most 85 W on live samples, tested in the smoke): one die reading (the minion
shires' mean or hottest sensor) at or above 80 C, or the board above 60 W on three samples in a row, ends the session; the admission limit is 82 W at
the estimate (the predicted peak), and after any run whose board reading reached 60 W no cell with an estimate at or above that run's goes on.

THE STOP-PATH TESTS (E146's, after the smoke, before the session; the queue halts unless both pass):
  STOPTEST-BOARD  board_cap_w 30 W on three samples, one 6 s burst of K4n8 fp32 zeros (the rest reads 22 W; E146's zeros bursts 34-38 W at 800 MHz):
                  the watcher must trip on three live samples over 30 W while the launch runs, and the launch must end at its next launch boundary.
  STOPTEST-DIE    abs_stop_c 30 C: the die reads above 40 C at rest, so the watcher must trip on the first live sample, before any launch.

THE ORDER (most important first; run_e119.py starts a run only if its planned time fits what is left of the session's cap):
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four cells' zeros (K4n2 fp32, K2n13 fp16, K6n6 int8, F6 fp32), each checked.
  A      pass 1, fp32: the 23 ladder rungs in order (K2 NB 4-13, K4 NB 2-8, K6 NB 1-6).
  B      pass 1, the shapes E146 ran: F6 in fp32, fp16 and int8; D2 and D4 in fp32.
  C      pass 2: A and B again, shuffled (run_hpl.py's one generator over the blocks, order_seed 158).
  E      the formats: the K4 rungs in fp16 and in int8 (pass 1 of each).
  F      pass 3: A and B again, shuffled (the same generator, so in another order).
  The registered subset, if the cap cuts: A, B and C (two passes of the ladder and of F6).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e158.json")))
TILES = "tools/claims-v3/kinds/tiles"
LADDER = P["ladder"]


def arm(s):
    return P["laws"][f"{s}.fp32"]["arm"]


def values(s, t):
    return f"{arm(s)}:tiles:{TILES}/{t}/zeros.bin"


def plan():
    A = [(s, "fp32") for s in LADDER]
    Bk = [("F6", t) for t in ("fp32", "fp16", "int8")] + [("D2", "fp32"), ("D4", "fp32")]
    E = [(s, t) for t in ("fp16", "int8") for s in LADDER if s.startswith("K4")]
    return [("A", A, False), ("B", Bk, False), ("C", A + Bk, True), ("E", E, False), ("F", A + Bk, True)]


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    gate_b = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke_cells = (("K4n2", "fp32"), ("K2n13", "fp16"), ("K6n6", "int8"), ("F6", "fp32"))
    for s, t in smoke_cells:
        smoke.append({"type": t, "values": values(s, t), "label": f"{s}-{t}-zeros"})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four cells' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke}]
    for name, rows, shuffle in plan():
        rs = []
        for s, t in rows:
            r = {"type": t, "values": values(s, t), "label": f"{s}-{t}-zeros"}
            r.update(burst)
            r.update(gate_b)
            rs.append(r)
        blocks.append({"name": name, "title": f"block {name}", "passes": 1, "shuffle": shuffle, "runs": rs})
    dry_c = {}
    for bl in blocks:
        for r in bl["runs"]:
            dry_c[r["values"]] = P["cells"].get(r["label"], {}).get("c600_w", 3.0)
    cyc = {f"{s}-{t}-zeros": P["laws"][f"{s}.{t}"]["STRICT-C"]["cyc800"] for s, t in smoke_cells}
    rel = P["relation"]
    return {"experiment": "E158", "request": "Q139", "card": "aifoundry2", "order_seed": 158,
            "note": "a ladder of B-panel reuse distances (19-59 MB) in three families of large GEMMs with different shares of C in the distance, and the shapes E146 ran (F6, D2, D4), zeros in every cell, under aifoundry2's own governor; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/e158/predictions-e158.json",
            "sampler": {"every_ms": 100}, "safety": dict(P["rules"]["safety"]), "caps": {"max_card_min": 30}, "smoke_cycles": cyc, "dry_c_w": dry_c,
            "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"], "relation": {"B800": rel["B"]["800"] if "800" in rel["B"] else rel["B"][800], "s800": rel["s800"]},
            "admission": dict(P["admission"]), "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    burst = {"launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    run = {"type": "fp32", "values": values("K4n8", "fp32"), "label": "K4n8-fp32-zeros", "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}
    run.update(burst)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": 80, "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": 60, "cap_consecutive": 3}
    p["note"] = f"E158's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
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
    for bl in p["blocks"]:
        print(f"block {bl['name']}{' (shuffled at run time: run_hpl.py\'s one generator, order_seed 158, over the blocks in order)' if bl.get('shuffle') else ''}:")
        for r in bl["runs"]:
            if bl["name"] != "SMOKE":
                n += 1
                est += 12.5
            a = p["admission"].get(r["label"], {})
            top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:18s} {r['values'][:72]:72s} est {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    print(f"{n} bursts, about {est / 60:.0f} card-minutes at 12.5 s a zeros burst (E146: 12.1 s a zeros burst from a cool die), plus the smoke and the two stop tests (about 2.5 min); the session's 30-minute cap cuts the tail")
    print(f"highest planned estimate (the predicted peak) {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
