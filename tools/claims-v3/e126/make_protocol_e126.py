#!/usr/bin/env python3
"""E126 (Q136): writes protocol.json and protocol-dry.json from predictions-e126.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e126/make_protocol_e126.py > tools/claims-v3/e126/protocol.txt

E119's design and parameters, unchanged (E80's with E105's): a burst is one 6 s process from a die reading <= 55 C; sustained is nine 8 s processes (about
76 s) from <= 57 C with the last 40 s read. Every start is cool. Nothing is set on the card. E119's binary (build/e119), sampler and runner.

THE MARGIN (Q136's rule: every run inside the registered stops with margin): E119's admission limit (88 W at the estimate) and lock (93 W) are unchanged,
and the session's own stops are tightened: one die reading (mean or hottest sensor) at or above 80 C (E119: 85 C), or the board above 93 W on three
samples in a row (E119: 97 W), ends the session. The highest planned estimate is E119's own c16r8 fp32 random, 84.1 W; E119's highest single reading,
85.71 W in that cell's sustained run, and its die's 69 C (the SP's running maximum) sit 7 W and 11 C inside these stops.

THE ORDER is one fixed list, most important first, and the cap (44 card-minutes for the session, the smoke apart, as E119's queue) cuts the tail: E119's
run_e119.py starts a run only if its planned time fits what is left.
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four arms' zeros, with the check of C read on each.
  A      fp32 bursts on the three new arms: zeros on c4s, c8, c16s; random on c4s, c8, c16s.
  B      the replicate: E119's block B exactly, fp32 sustained random and zeros on c8s, c16r4, c16r8, c16r2.
  C      int8 bursts on the new arms: zeros, then full.
  D      fp16 bursts on the new arms: zeros, then random.
  E      fp32 sustained on the new arms: random and zeros on c4s, c16s, c8.
  F      int8 full and fp16 random, sustained, on c4s, c16s, c8.
  G      the tail: c4s's int8 and fp16 zeros sustained, then fp32 zeros bursts again on c4s and c16s.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e126.json")))
P119 = json.load(open(os.path.join(HERE, "..", "e119", "predictions-e119.json")))
TILES = "tools/claims-v3/kinds/tiles"
VA = P["values_arm"]
TOP = {"fp32": "randn", "fp16": "randn", "int8": "full"}
NEW = ("c4s", "c8", "c16s")


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
    A = [(a, "fp32", "zeros", "burst", "") for a in NEW] + [(a, "fp32", "randn", "burst", "") for a in NEW]
    B = []
    for a in P["replicate_arms"]:                    # c8s, c16r4, c16r8, c16r2: E119's block B order
        B += [(a, "fp32", "randn", "sus", ""), (a, "fp32", "zeros", "sus", "")]
    C = [(a, "int8", "zeros", "burst", "") for a in NEW] + [(a, "int8", "full", "burst", "") for a in NEW]
    D = [(a, "fp16", "zeros", "burst", "") for a in NEW] + [(a, "fp16", "randn", "burst", "") for a in NEW]
    E = []
    for a in ("c4s", "c16s", "c8"):
        E += [(a, "fp32", "randn", "sus", ""), (a, "fp32", "zeros", "sus", "")]
    F = []
    for a in ("c4s", "c16s", "c8"):
        F += [(a, "int8", "full", "sus", ""), (a, "fp16", "randn", "sus", "")]
    G = [("c4s", "int8", "zeros", "sus", ""), ("c4s", "fp16", "zeros", "sus", ""),
         ("c4s", "fp32", "zeros", "burst", "-rep2"), ("c16s", "fp32", "zeros", "burst", "-rep2")]
    return [("A", A), ("B", B), ("C", C), ("D", D), ("E", E), ("F", F), ("G", G)]


def t800_frozen(arm, t):
    """the frozen T at 800 MHz, for the smoke's cycles check only (50%-250%)"""
    if arm == "c4s":
        L = P["laws"][f"c4s.{t}"]
        return P["laws"][f"c4s.{t}"]["T600_e107_us"] / L["X_like_c8s"]
    if arm in P["dram_arms"]:
        return P["laws"][f"{arm}.{t}"]["T800_S_us"]
    return P["replicate"][arm]["T800_zeros_us"]


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    sus = {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5} if dry else {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}
    gate_b = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
    gate_s = {"start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke_cells = (("c4s", "fp32"), ("c8", "int8"), ("c16s", "fp16"), ("c8s", "fp32"))
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
    cyc = {f"{a}-{t}-zeros": round(t800_frozen(a, t) * 800, 1) for a, t in smoke_cells}
    rel = P119["relation"]
    return {"experiment": "E126", "request": "Q136", "card": "aifoundry2", "order_seed": 126,
            "note": "E119's harness and design on E107's arms c4s, c8 and c16s, and E119's four sustained fp32 pairs again, under aifoundry2's own governor; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e119/host/sparsity_host", "kernel": "build/e119/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/e126/predictions-e126.json",
            "sampler": {"every_ms": 100}, "safety": dict(P["rules"]["safety"]), "caps": {"max_card_min": 44}, "smoke_cycles": cyc, "dry_c_w": dry_c,
            "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"], "relation": {"B800": rel["B"]["800"], "s800": rel["s800"]},
            "admission": dict(P["admission"]), "blocks": blocks}


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    p = build(False)
    n = {"burst": 0, "sus": 0}
    est, top = 0.0, 0.0
    for bl in p["blocks"]:
        print(f"block {bl['name']}:")
        for r in bl["runs"]:
            la = r.get("launch", bl.get("launch", {}))
            sus = la.get("processes", 1) == 9
            if bl["name"] != "SMOKE":
                n["sus" if sus else "burst"] += 1
                est += 95 if sus else 22
            a = p["admission"].get(r["label"].replace("-rep2", ""), {})
            top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:26s} {'sus' if sus else 'burst':5s} {r['values'][:62]:62s} est {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    print(n, f"about {est / 60:.0f} card-minutes at 22 s a burst and 95 s a sustained run, gates included, plus the smoke; the 44-minute cap cuts the tail")
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}")


if __name__ == "__main__":
    main()
