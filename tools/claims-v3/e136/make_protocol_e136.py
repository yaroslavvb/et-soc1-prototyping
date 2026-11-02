#!/usr/bin/env python3
"""E136 (Q137): writes protocol.json and protocol-dry.json from predictions-e136.json; prints protocol.txt. No card.

    python3 tools/claims-v3/e136/make_protocol_e136.py > tools/claims-v3/e136/protocol.txt

E119's and E126's design and parameters, unchanged (E80's with E105's): a burst is one 6 s process from a die reading <= 55 C; sustained is nine 8 s
processes (about 76 s) from <= 57 C with the last 40 s read. Every start is cool. Nothing is set on the card. rgm136 (build/e136), E119's sampler and
runner (through run_e136.py).

THE MARGIN (Q137 keeps Q136's rule: every run inside the registered stops with margin): E119's admission limit (88 W at the estimate) and lock (93 W)
are unchanged, and the session's stops are E126's: one die reading (mean or hottest sensor) at or above 80 C, or the board above 93 W on three samples
in a row, ends the session; E101's registered stop is 97 W. The highest planned estimate is g2k fp32 random's 75.6 W (E126's highest planned was 84.1 W,
its highest reading 85.62 W).

THE KINDS: zeros (the file's tile through the whole pool), random (fp32 and fp16 randn, int8 full: rgm105's generator draws the pool), one sparse
(sparse50: half of the elements zero, the rest random, the same generator), one real model kind (E101's registered real set, kinds/e101_common.py REAL_SET:
four tiles per format cut from GPT-2 small, BERT and ViT-B/16 by Q132(r) in tools/claims-v3/kinds/real2/tiles/<format>/, cycled through the pools: A tile t
and B tile t are file t mod 4's).

THE ORDER is one fixed list, most important first, and the cap (45 card-minutes for the session, the smoke apart) cuts the tail: E119's run_e119.py
starts a run only if its planned time fits what is left.
  SMOKE  the idle card (30 s, the session's rest reading), then a 2 s launch of four cells' zeros (g4k in every format, g2k int8), each with its check of C.
  A      fp32 bursts: g4k zeros, randn, sparse50, real; g2k zeros, randn.
  B      fp32 sustained on g4k: randn, zeros.
  C      int8 bursts: g4k zeros, full, sparse50, real; g2k zeros, full.
  D      fp16 bursts: g4k zeros, randn, sparse50, real; g2k zeros, randn.
  E      sustained on g4k: int8 full, int8 zeros, fp16 randn, fp16 zeros.
  F      sustained: g2k fp32 randn, zeros; g4k fp32 real, sparse50.
  G      the tail: sustained g4k int8 real, fp16 real; bursts g2k fp32 sparse50, real.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e136.json")))
TILES = "tools/claims-v3/kinds/tiles"
import sys
sys.path.insert(0, os.path.join(HERE, "..", "kinds"))
import e101_common as EC  # noqa: E402
REAL = "tools/claims-v3/kinds/real2/tiles"
VA = P["gemms"]
TOP = P["top"]


def values(g, t, k):
    a = VA[g]
    if k == "zeros":
        return f"{a}:tiles:{TILES}/{t}/zeros.bin"
    if k == "randn":
        return f"{a}:randn:{TILES}/{t}/randn.bin"
    if k == "full":
        return f"{a}:randn:{TILES}/{t}/full.bin"
    if k == "sparse50":
        return f"{a}:sparse50:{TILES}/{t}/sparse50.bin"
    if k == "real":
        return f"{a}:tiles:" + ",".join(f"{REAL}/{t}/{f}.bin" for f in EC.REAL_SET[t])
    raise KeyError(k)


def plan():
    """(block, [(gemm, format, kind, mode)]) in session order."""
    def bursts(t):
        top = TOP[t]
        return [("g4k", t, "zeros", "burst"), ("g4k", t, top, "burst"), ("g4k", t, "sparse50", "burst"), ("g4k", t, "real", "burst"),
                ("g2k", t, "zeros", "burst"), ("g2k", t, top, "burst")]
    A = bursts("fp32")
    B = [("g4k", "fp32", "randn", "sus"), ("g4k", "fp32", "zeros", "sus")]
    C = bursts("int8")
    D = bursts("fp16")
    E = [("g4k", "int8", "full", "sus"), ("g4k", "int8", "zeros", "sus"), ("g4k", "fp16", "randn", "sus"), ("g4k", "fp16", "zeros", "sus")]
    F = [("g2k", "fp32", "randn", "sus"), ("g2k", "fp32", "zeros", "sus"), ("g4k", "fp32", "real", "sus"), ("g4k", "fp32", "sparse50", "sus")]
    G = [("g4k", "int8", "real", "sus"), ("g4k", "fp16", "real", "sus"), ("g2k", "fp32", "sparse50", "burst"), ("g2k", "fp32", "real", "burst")]
    return [("A", A), ("B", B), ("C", C), ("D", D), ("E", E), ("F", F), ("G", G)]


def build(dry):
    burst = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    sus = {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5} if dry else {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}
    gate_b = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
    gate_s = {"start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}}
    smoke = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": 3 if dry else 30}]
    smoke_cells = (("g4k", "fp32"), ("g4k", "int8"), ("g4k", "fp16"), ("g2k", "int8"))
    for g, t in smoke_cells:
        smoke.append({"type": t, "values": values(g, t, "zeros"), "label": f"{g}-{t}-zeros"})
    blocks = [{"name": "SMOKE", "title": "the idle card with no launch (its last 30 s are the session's rest reading), then a 2 s launch of four cells' zeros", "default": False,
               "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke}]
    for name, rows in plan():
        rs = []
        for g, t, k, mode in rows:
            r = {"type": t, "values": values(g, t, k), "label": f"{g}-{t}-{k}"}
            r.update(burst if mode == "burst" else sus)
            r.update(gate_b if mode == "burst" else gate_s)
            rs.append(r)
        blocks.append({"name": name, "title": f"block {name}", "passes": 1, "shuffle": False, "runs": rs})
    dry_c = {}
    for bl in blocks:
        for r in bl["runs"]:
            dry_c[r["values"]] = P["cells"].get(r["label"], {}).get("c600_w", 3.0)
    cyc = {f"{g}-{t}-zeros": round(P["laws"][f"{g}.{t}"]["P1"]["T800_us"] * 800, 1) for g, t in smoke_cells}
    rel = P["relation"]
    return {"experiment": "E136", "request": "Q137", "card": "aifoundry2", "order_seed": 136,
            "note": "a large GEMM in the vendor's pattern (rgm136 SP_GEMM_LARGE: g4k 192 MB with C, g2k 20 MB), four kinds in fp32, fp16 and int8, under aifoundry2's own governor; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/e136/predictions-e136.json",
            "sampler": {"every_ms": 100}, "safety": dict(P["rules"]["safety"]), "caps": {"max_card_min": 45}, "smoke_cycles": cyc, "dry_c_w": dry_c,
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
                est += 100 if sus else 25
            a = p["admission"].get(r["label"], {})
            top = max(top, a.get("fixed_p800_w") or 0)
            print(f"  {r['label']:22s} {'sus' if sus else 'burst':5s} {r['values'][:70]:70s} est {a.get('fixed_p800_w')} W  cum {est / 60:5.1f} min")
    print(n, f"about {est / 60:.0f} card-minutes at 25 s a burst and 100 s a sustained run, gates included, plus the smoke; the 45-minute cap cuts the tail")
    print(f"highest planned estimate {top} W; admission limit {p['limit_p800_w']} W, lock {p['peak_lock_w']} W; session stops {p['safety']}; smoke cycles {p['smoke_cycles']}")


if __name__ == "__main__":
    main()
