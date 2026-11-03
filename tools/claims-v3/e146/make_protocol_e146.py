#!/usr/bin/env python3
"""E146 (Q138): writes protocol.json, protocol-dry.json and the two stop-path tests (protocol-stoptest-board.json, protocol-stoptest-die.json and their
dry twins) from predictions-e146.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e146/make_protocol_e146.py > tools/claims-v3/e146/protocol.txt

E136's design and parameters, unchanged (E119's, E105's, E80's): a burst is one 6 s process from a die reading <= 55 C; sustained is nine 8 s processes
(about 76 s) from <= 57 C with the last 40 s read. Every start is cool. Nothing is set on the card. rgm136 (build/e136, E136's binary: the shapes are
arguments, `gemmL<MB>x<NB>x<KB>`), E119's sampler and runner (through run_e146.py).

THE STOPS (E136's registered stops, now under the keys run_hpl.py's watcher reads): one die reading (the minion shires' mean or hottest sensor) at or
above 80 C, or the board above 93 W on three samples in a row, ends the session. E136's protocol.json named them "die_c", "board_w" and "board_samples";
the watcher reads "abs_stop_c", "board_cap_w" and "cap_consecutive", so E136 ran on the watcher's defaults (85 C; 97 W on three samples). E146 writes the
watcher's keys, and the queue proves the path before the session: two stop-path tests on live samples (below).

THE STOP-PATH TESTS (after the smoke, before the session; the queue halts unless both pass):
  STOPTEST-BOARD  the same runner and watcher with board_cap_w 30 W (three samples): one 6 s burst of D8 fp32 random (E136: 52.5 W at 800 MHz). The
                  watcher must trip on three live samples over 30 W while the launch runs, touch the stop file, and the launch loop must end at its next
                  launch boundary; the session ends with exit 4 (a safety stop).
  STOPTEST-DIE    abs_stop_c 30 C: the die reads above 40 C on this card at rest, so the watcher must trip on the first live sample, before any launch;
                  exit 4.

THE ORDER, most important first; the session's cap (40 card-minutes, the smoke and the tests apart) cuts the tail: run_e119.py starts a run only if its
planned time fits what is left.
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four cells' zeros (L1 fp32, L8 fp16, D1 int8, F6 fp32), each with its check.
  A      fp32 bursts, pass 1: L1, D1, L2, D2, L4, D4, L8, D8, each zeros then random.
  B      int8 bursts, pass 1, the same order.
  C      fp16 bursts, pass 1, the same order.
  D      the fresh shape F6: bursts in fp32, int8 and fp16 (zeros, random), then sustained fp32 random and int8 full.
  E      pass 2: the 48 bursts of A, B and C again, in one shuffled order (seed 146).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e146.json")))
TILES = "tools/claims-v3/kinds/tiles"
ARM = P["shapes"]
TOP = P["top"]
ORDER = ("L1", "D1", "L2", "D2", "L4", "D4", "L8", "D8")


def values(s, t, k):
    a = ARM[s]
    if k == "zeros":
        return f"{a}:tiles:{TILES}/{t}/zeros.bin"
    if k == "randn":
        return f"{a}:randn:{TILES}/{t}/randn.bin"
    if k == "full":
        return f"{a}:randn:{TILES}/{t}/full.bin"
    raise KeyError(k)


def plan():
    def bursts(t):
        return [(s, t, k, "burst") for s in ORDER for k in ("zeros", TOP[t])]
    A, Bk, C = bursts("fp32"), bursts("int8"), bursts("fp16")
    D = [("F6", t, k, "burst") for t in ("fp32", "int8", "fp16") for k in ("zeros", TOP[t])] + [("F6", "fp32", "randn", "sus"), ("F6", "int8", "full", "sus")]
    E = A + Bk + C
    return [("A", A, False), ("B", Bk, False), ("C", C, False), ("D", D, False), ("E", E, True)]


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    sus = {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5} if dry else {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}
    gate_b = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
    gate_s = {"start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke_cells = (("L1", "fp32"), ("L8", "fp16"), ("D1", "int8"), ("F6", "fp32"))
    for s, t in smoke_cells:
        smoke.append({"type": t, "values": values(s, t, "zeros"), "label": f"{s}-{t}-zeros"})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four cells' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke}]
    for name, rows, shuffle in plan():
        rs = []
        for s, t, k, mode in rows:
            r = {"type": t, "values": values(s, t, k), "label": f"{s}-{t}-{k}"}
            r.update(burst if mode == "burst" else sus)
            r.update(gate_b if mode == "burst" else gate_s)
            rs.append(r)
        blocks.append({"name": name, "title": f"block {name}", "passes": 1, "shuffle": shuffle, "runs": rs})
    dry_c = {}
    for bl in blocks:
        for r in bl["runs"]:
            dry_c[r["values"]] = P["cells"].get(r["label"], {}).get("c600_w", 3.0)
    cyc = {f"{s}-{t}-zeros": P["laws"][f"{s}.{t}"]["MS"]["cyc800"] for s, t in smoke_cells}
    rel = P["relation"]
    return {"experiment": "E146", "request": "Q138", "card": "aifoundry2", "order_seed": 146,
            "note": "a ladder of C-store cadences (a store every 32, 64, 128, 256 ops) in GEMMs the L3 holds and GEMMs that stream to DRAM, and one fresh shape, in fp32, fp16 and int8, under aifoundry2's own governor; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/e146/predictions-e146.json",
            "sampler": {"every_ms": 100}, "safety": dict(P["rules"]["safety"]), "caps": {"max_card_min": 40}, "smoke_cycles": cyc, "dry_c_w": dry_c,
            "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"], "relation": {"B800": rel["B"]["800"], "s800": rel["s800"]},
            "admission": dict(P["admission"]), "blocks": blocks}


def stoptest(kind, dry):
    """the same runner and watcher, one block, one stop lowered so that it must fire on live samples"""
    p = build(dry)
    burst = {"launch": {"seconds": 2.5 if dry else 6, "budget": 4 if dry else 7.5, "processes": 1}, "tail_s": 0.5 if dry else 4}
    run = {"type": "fp32", "values": values("D8", "fp32", "randn"), "label": "D8-fp32-randn", "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}}
    run.update(burst)
    p["blocks"] = [{"name": "STOPTEST", "title": f"the {kind} stop's path on live samples", "default": False, "passes": 1, "shuffle": False, "runs": [run]}]
    if kind == "board":
        p["safety"] = {"abs_stop_c": 80, "board_cap_w": 30, "cap_consecutive": 3}
    else:
        p["safety"] = {"abs_stop_c": 30, "board_cap_w": 93, "cap_consecutive": 3}
    p["note"] = f"E146's stop-path test ({kind}): the registered watcher with one stop lowered, so that it must trip on live samples; the session must end with exit 4"
    p["caps"] = {"max_card_min": 2}
    return p


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    for kind in ("board", "die"):
        json.dump(stoptest(kind, False), open(os.path.join(HERE, f"protocol-stoptest-{kind}.json"), "w"), indent=1)
        json.dump(stoptest(kind, True), open(os.path.join(HERE, f"protocol-stoptest-{kind}-dry.json"), "w"), indent=1)
    p = build(False)
    n = {"burst": 0, "sus": 0}
    est, top = 0.0, 0.0
    for bl in p["blocks"]:
        print(f"block {bl['name']}{' (shuffled at run time, seed 146)' if bl.get('shuffle') else ''}:")
        for r in bl["runs"]:
            la = r.get("launch", bl.get("launch", {}))
            sus = la.get("processes", 1) == 9
            if bl["name"] != "SMOKE":
                n["sus" if sus else "burst"] += 1
                est += 100 if sus else 14
            a = p["admission"].get(r["label"], {})
            top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:18s} {'sus' if sus else 'burst':5s} {r['values'][:64]:64s} est {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    print(n, f"about {est / 60:.0f} card-minutes at 14 s a burst (E136: 12 s from a cool die) and 100 s a sustained run, gates included, plus the smoke and the two stop tests (about 2.5 min); the 40-minute cap cuts the tail")
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")
    for kind in ("board", "die"):
        q = stoptest(kind, False)
        print(f"stop-path test {kind}: safety {q['safety']}; run {q['blocks'][0]['runs'][0]['label']} {q['blocks'][0]['runs'][0]['values']}")


if __name__ == "__main__":
    main()
