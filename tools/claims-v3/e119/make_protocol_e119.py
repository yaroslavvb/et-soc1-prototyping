#!/usr/bin/env python3
"""E119 (Q134): writes protocol.json and protocol-dry.json from predictions-e119.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e119/make_protocol_e119.py > tools/claims-v3/e119/protocol.txt

E80's design with E105's parameters, unchanged: a burst is one 6 s process from a die reading <= 55 C; sustained is nine 8 s processes (about 76 s) from
<= 57 C with the last 40 s read. Every start is cool (no hot start: E101's 97 W stop came from one). Nothing is set on the card.

THE ORDER is one fixed list, most important first, and the cap (45 card-minutes in all, smoke included) cuts the tail: run_e119.py starts a run only if
its planned time fits what is left.
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four arms, with the check of C read on each.
  A      fp32 bursts: zeros on all seven arms, random on the five the rule admits (c1 and c16r32 random are over 88 W at the estimate; not planned).
  B      fp32 sustained: random and zeros on c8s, c16r4, c16r8, c16r2.
  C      int8 bursts: zeros on all seven arms, full on six (c1's full is E105's cell; not planned).
  D      fp16 bursts: zeros on all seven arms, random on five (c1 over the limit; c16r32's 86.5 W estimate is the closest to it, so not planned).
  E      int8 sustained: full on c16r8, c16r32, c16r4, c8s; zeros on c8s.
  F      fp16 sustained: random on c8s, c16r4, c16r8; zeros on c8s.
  G      the tail: c16 random sustained (fp32, E105's gemmc16 tie), c16r2 random sustained in fp16 and int8, and two fp32 zeros bursts again.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e119.json")))
TILES = "tools/claims-v3/kinds/tiles"
VA = P["values_arm"]
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
ALL7 = ("c8s", "c16r4", "c16r2", "c16r8", "c16r32", "c16", "c1")


def values(arm, t, k):
    a = VA[arm]
    if k == "zeros":
        return f"{a}:tiles:{TILES}/{t}/zeros.bin"
    if k == "randn":
        return f"{a}:randn:{TILES}/{t}/randn.bin"
    if k == "full":
        return f"{a}:randn:{TILES}/{t}/full.bin"
    raise KeyError(k)


def plan():
    """(block, [(arm, format, kind, mode, suffix)]) in session order."""
    A = [(a, "fp32", "zeros", "burst", "") for a in ALL7] + [(a, "fp32", "randn", "burst", "") for a in ("c8s", "c16r4", "c16r2", "c16r8", "c16")]
    B = []
    for a in ("c8s", "c16r4", "c16r8", "c16r2"):
        B += [(a, "fp32", "randn", "sus", ""), (a, "fp32", "zeros", "sus", "")]
    C = [(a, "int8", "zeros", "burst", "") for a in ALL7] + [(a, "int8", "full", "burst", "") for a in ("c8s", "c16r4", "c16r2", "c16r8", "c16r32", "c16")]
    D = [(a, "fp16", "zeros", "burst", "") for a in ALL7] + [(a, "fp16", "randn", "burst", "") for a in ("c8s", "c16r4", "c16r2", "c16r8", "c16")]
    E = [(a, "int8", "full", "sus", "") for a in ("c16r8", "c16r32", "c16r4", "c8s")] + [("c8s", "int8", "zeros", "sus", "")]
    F = [(a, "fp16", "randn", "sus", "") for a in ("c8s", "c16r4", "c16r8")] + [("c8s", "fp16", "zeros", "sus", "")]
    G = [("c16", "fp32", "randn", "sus", ""), ("c16r2", "fp16", "randn", "sus", ""), ("c16r2", "int8", "full", "sus", ""),
         ("c8s", "fp32", "zeros", "burst", "-rep2"), ("c16r4", "fp32", "zeros", "burst", "-rep2")]
    return [("A", A), ("B", B), ("C", C), ("D", D), ("E", E), ("F", F), ("G", G)]


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    sus = {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5} if dry else {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}
    gate_b = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
    gate_s = {"start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke_cells = (("c8s", "fp32"), ("c16r4", "int8"), ("c16r2", "fp16"), ("c16r32", "fp32"))
    for a, t in smoke_cells:
        smoke.append({"type": t, "values": values(a, t, "zeros"), "label": f"{a}-{t}-zeros"})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four arms' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke}]
    for name, rows in plan():
        rs = []
        for a, t, k, mode, suf in rows:
            r = {"type": t, "values": values(a, t, k), "label": f"{a}-{t}-{k}{suf}"}
            r.update(burst if mode == "burst" else sus)
            r.update(gate_b if mode == "burst" else gate_s)
            rs.append(r)
        blocks.append({"name": name, "title": f"block {name}", "passes": 1, "shuffle": False, "runs": rs})
    dry_c = {}
    for bl in blocks:
        for r in bl["runs"]:
            base = r["label"].replace("-rep2", "")
            dry_c[r["values"]] = P["cells"].get(base, {}).get("c600_w", 3.0)
    cyc = {f"{a}-{t}-zeros": round(P["laws"][f"{a}.{t}"]["T800_us"] * 800, 1) for a, t in smoke_cells}
    adm = dict(P["admission"])
    return {"experiment": "E119", "request": "Q134", "card": "aifoundry2", "order_seed": 119,
            "note": "E80's design on E107's arms under aifoundry2's own governor; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e119/host/sparsity_host", "kernel": "build/e119/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/e119/predictions-e119.json",
            "sampler": {"every_ms": 100}, "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3}, "caps": {"max_card_min": 45},
            "smoke_cycles": cyc, "dry_c_w": dry_c, "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"],
            "relation": {"B800": P["relation"]["B"]["800"], "s800": P["relation"]["s800"]}, "admission": adm, "blocks": blocks}


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    p = build(False)
    n = {"burst": 0, "sus": 0}
    est = 0.0
    for bl in p["blocks"]:
        print(f"block {bl['name']}:")
        for r in bl["runs"]:
            la = r.get("launch", bl.get("launch", {}))
            sus = la.get("processes", 1) == 9
            if bl["name"] != "SMOKE":
                n["sus" if sus else "burst"] += 1
                est += 95 if sus else 22
            a = p["admission"].get(r["label"].replace("-rep2", ""), {})
            print(f"  {r['label']:26s} {'sus' if sus else 'burst':5s} {r['values'][:62]:62s} est {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    print(n, f"about {est / 60:.0f} card-minutes at 22 s a burst and 95 s a sustained run, gates included, plus the smoke; the 45-minute cap cuts the tail")


if __name__ == "__main__":
    main()
