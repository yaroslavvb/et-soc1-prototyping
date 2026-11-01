#!/usr/bin/env python3
"""E105 (Q132): writes protocol.json and protocol-dry.json from predictions-e105.json. No card.

    python3 make_protocol_e105.py > protocol.txt

E80's design, E101 session 2's parameters: a burst is one 6 s process from a die reading <= 55 C, sustained is nine 8 s processes (~76 s) from <= 57 C with the last 40 s read. No hot start anywhere: every start is cool. No mm16 at all. Nothing is set on the card.

THE ORDER is one fixed list, most important first, and a time cut takes the tail; within a layout and format a probe comes before the cells it admits (run_e105.py).
  SMOKE  the idle card (a 45 s rest reading), then a 2 s launch of each layout's fp32 and int8 zeros, with the check of C read on each.
  A      fp32, the same kinds in the three layouts.
  B      int8.
  C      the one-pass cold variant, 16 blocks.
  D      half K and half the chip, the controls; the constant's sustained runs; replicates; gemm1 zeros sustained.
  E      fp16.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "predictions-e105.json")))
CELLS, CREF, LAW = P["cells"], P["c_ref_w"], P["laws"]
TILES = "tools/claims-v3/kinds/tiles"
HALF = "0x0000ffff"


def values(arm, t, k):
    if k in ("zeros", "ones"):
        return f"{arm}:tiles:{TILES}/{t}/{k}.bin"
    if k == "randn":
        return f"{arm}:randn:{TILES}/{t}/randn.bin"
    if k == "full":
        return f"{arm}:randn:{TILES}/{t}/full.bin"
    if k == "sparse50":
        return f"{arm}:sparse50:{TILES}/{t}/sparse50.bin"
    if k == "sparse25":
        return f"{arm}:sparse25:{TILES}/{t}/randn.bin"
    raise KeyError(k)


def cell(arm, t, k, suffix="", **kw):
    return dict({"type": t, "values": values(arm, t, k), "label": f"{arm}-{t}-{k}{suffix}"}, **kw)


# (arm, format, kind, burst?, sustained?), in session order. See the module docstring. The probes run first in their layout and format.
PLAN = {
    "A": [("gemm1", "fp32", "zeros", 1, 0), ("gemm1", "fp32", "sparse25", 1, 1), ("gemm1", "fp32", "randn", 1, 1),
          ("gemmc1", "fp32", "zeros", 1, 1), ("gemmc1", "fp32", "ones", 1, 0), ("gemmc1", "fp32", "sparse50", 1, 0), ("gemmc1", "fp32", "sparse25", 1, 1), ("gemmc1", "fp32", "randn", 1, 1),
          ("gemmv1", "fp32", "zeros", 1, 1), ("gemmv1", "fp32", "ones", 1, 0), ("gemmv1", "fp32", "sparse50", 1, 0), ("gemmv1", "fp32", "sparse25", 1, 1), ("gemmv1", "fp32", "randn", 1, 1)],
    "B": [("gemmc1", "int8", "zeros", 1, 1), ("gemmc1", "int8", "sparse50", 1, 1), ("gemmc1", "int8", "full", 1, 1),
          ("gemmv1", "int8", "zeros", 1, 0), ("gemmv1", "int8", "sparse50", 1, 0), ("gemmv1", "int8", "full", 1, 1)],
    "C": [("gemmc16", "fp32", "zeros", 1, 0), ("gemmc16", "fp32", "randn", 1, 1), ("gemmv16", "fp32", "zeros", 1, 0), ("gemmv16", "fp32", "randn", 1, 0)],
    "D": [("gemmh1", "fp32", "zeros", 1, 0)],
    "E": [("gemmc1", "fp16", "zeros", 1, 1), ("gemmc1", "fp16", "sparse50", 1, 1), ("gemmc1", "fp16", "randn", 1, 1),
          ("gemmv1", "fp16", "zeros", 1, 0), ("gemmv1", "fp16", "sparse50", 1, 0), ("gemmv1", "fp16", "randn", 1, 1)],
}
# Block D's other runs: half the chip on by-column random fp32, the one way the rule lets that kind reach silicon here; the constant's sustained runs; replicates of the primary sustained cells and of gemm1 zeros.
EXTRA_D = [("gemmc1", "fp32", "randn", "-half", "burst"), ("gemmc1", "fp32", "sparse25", "-rep2", "sus"), ("gemmc1", "fp32", "zeros", "-rep2", "sus"), ("gemmc1", "fp32", "ones", "", "sus"), ("gemmv1", "fp32", "ones", "", "sus"),
           ("gemmc1", "int8", "full", "-rep2", "sus"), ("gemmc1", "int8", "zeros", "-rep2", "sus"), ("gemm1", "fp32", "zeros", "", "sus"), ("gemmc1", "fp32", "randn", "-half", "sus"),
           ("gemmv1", "fp32", "sparse25", "-rep2", "sus"), ("gemmv1", "fp32", "zeros", "-rep2", "sus")]

BLOCK_BURST = {"start": {"mode": "cool", "max_c": 55, "max_wait_s": 300}}
BLOCK_SUS = {"start": {"mode": "cool", "max_c": 57, "max_wait_s": 300}}


def admission():
    t = {}
    # fixed: E101 measured the as-run layout at or below these on aifoundry2, and the zero, constant and sparse50 kinds cannot reach the limit in any layout at 1.16 x mm16's c
    for arm in ("gemm1", "gemmc1", "gemmv1"):
        for ty in ("fp32", "fp16", "int8"):
            for k in ("zeros", "ones", "sparse50"):
                if k in CREF[ty]:
                    t[f"{arm}-{ty}-{k}"] = {"c_ref_w": CREF[ty][k], "fixed_p800_w": round(P["relation"]["B"]["800"] + P["relation"]["s800"] * CREF[ty][k] * 1.16, 1)}
    t["gemm1-fp32-randn"] = {"c_ref_w": CREF["fp32"]["randn"], "fixed_p800_w": 74.0}     # E101: 73.19 and 73.97 W
    t["gemm1-fp32-sparse25"] = {"c_ref_w": CREF["fp32"]["sparse25"], "fixed_p800_w": 70.0}
    for arm in ("gemmc1", "gemmv1"):
        t[f"{arm}-fp32-sparse25"] = {"c_ref_w": CREF["fp32"]["sparse25"], "probe": f"{arm}-fp32-sparse50"}
        t[f"{arm}-fp32-randn"] = {"c_ref_w": CREF["fp32"]["randn"], "probe": f"{arm}-fp32-sparse50"}
        t[f"{arm}-int8-full"] = {"c_ref_w": CREF["int8"]["full"], "probe": f"{arm}-int8-sparse50"}
        t[f"{arm}-fp16-randn"] = {"c_ref_w": CREF["fp16"]["randn"], "probe": f"{arm}-fp16-sparse50"}
    # half the chip: half the c of the full chip's, by its fp32 probe
    t["gemmc1-fp32-randn-half"] = {"c_ref_w": round(CREF["fp32"]["randn"] / 2, 2), "probe": "gemmc1-fp32-sparse50"}
    # the cold variant: gemm16's S at aifoundry3 scaled by the miss share it loses; below the limit by a wide margin at any rate it can reach
    for arm in ("gemmc16", "gemmv16"):
        t[f"{arm}-fp32-zeros"] = {"c_ref_w": 5.0, "fixed_p800_w": 45.0}
        t[f"{arm}-fp32-randn"] = {"c_ref_w": 23.0, "fixed_p800_w": 77.0}
    t["gemmh1-fp32-zeros"] = {"c_ref_w": CREF["fp32"]["zeros"], "fixed_p800_w": 45.0}
    t["rest"] = {"fixed_p800_w": 30.0}                                                    # the idle card: no launch
    return t


def build(dry):
    burst_launch = {"launch": {"seconds": 2.5, "budget": 4, "processes": 1}, "tail_s": 0.5} if dry else {"launch": {"seconds": 6, "budget": 7.5, "processes": 1}, "tail_s": 4}
    sus_launch = {"launch": {"seconds": 2.5, "budget": 4, "processes": 2}, "tail_s": 0.5} if dry else {"launch": {"seconds": 8, "budget": 9.5, "processes": 9}, "tail_s": 6}
    smoke_tail = 3 if dry else 45
    blocks = []
    smoke_runs = [{"type": "fp32", "values": "zeros", "label": "rest", "launch": {"seconds": 2, "budget": 3.5, "processes": 0}, "tail_s": smoke_tail}]
    smoke_labels = [("gemm1", "fp32"), ("gemmc1", "fp32"), ("gemmv1", "fp32"), ("gemmc1", "int8"), ("gemmv1", "int8")]
    for arm, t in smoke_labels:
        smoke_runs.append(cell(arm, t, "zeros"))
    blocks.append({"name": "SMOKE", "title": "the idle card with no launch (its last 45 s are the session's rest reading), then a 2 s launch of each layout's zeros", "default": False,
                   "start": {"mode": "cool", "max_c": 99, "max_wait_s": 5}, "launch": {"seconds": 2, "budget": 3.5, "processes": 1}, "tail_s": 3, "runs": smoke_runs})

    def one(arm, t, k, suffix, mode):
        r = cell(arm, t, k, suffix)
        if suffix == "-half":
            r["mask"] = HALF
        return dict(r, **(burst_launch if mode == "burst" else sus_launch), **(BLOCK_BURST if mode == "burst" else BLOCK_SUS))
    # run_hpl names a run <block>-<idx>-<label>-r<rep> and reduces block BURST or SUS by name, so every block stays one of the two by a prefix the reducer maps
    for name in ("A", "B", "C", "D", "E"):
        rs = []
        for arm, t, k, b, s in PLAN[name]:
            if b:
                rs.append(one(arm, t, k, "", "burst"))
            if s:
                rs.append(one(arm, t, k, "", "sus"))
        if name == "D":
            for arm, t, k, suf, mode in EXTRA_D:
                rs.append(one(arm, t, k, suf, mode))
        blocks.append({"name": name, "title": f"block {name}", "passes": 1, "shuffle": False, "runs": rs})
    dry_c = {}
    for bl in blocks:
        for r in bl["runs"]:
            lab = r["label"]
            base = lab.replace("-rep2", "").replace("-half", "")
            c = CELLS.get(base, {}).get("c_w", 15.0)
            dry_c[r["values"]] = c
    cyc = {}
    for arm, t in smoke_labels:
        cyc[f"{arm}-{t}-zeros"] = round(LAW[f"{arm}.{t}"]["T_800_us"] * 800, 1)
    return {"experiment": "E105", "request": "Q132", "card": "aifoundry2", "order_seed": 105, "note": "E80's design on E105's layouts; every start is cool; nothing is set on the card",
            "tools": {"heater": "build/e105/host/sparsity_host", "kernel": "build/e105/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"},
            "kinds": "tools/claims-v3/kinds/kinds.json", "predictions": "tools/claims-v3/kspeed/e105/predictions-e105.json",
            "sampler": {"every_ms": 100}, "safety": {"abs_stop_c": 85, "board_cap_w": 97, "cap_consecutive": 3}, "caps": {"max_card_min": 52},
            "smoke_cycles": cyc, "dry_c_w": dry_c, "limit_p800_w": P["rules"]["limit_p800_w"], "peak_lock_w": P["rules"]["peak_lock_w"], "relation": {"B800": P["relation"]["B"]["800"], "s800": P["relation"]["s800"]},
            "admission": admission(), "blocks": blocks}


def main():
    json.dump(build(False), open(os.path.join(HERE, "protocol.json"), "w"), indent=1)
    json.dump(build(True), open(os.path.join(HERE, "protocol-dry.json"), "w"), indent=1)
    p = build(False)
    n = {"burst": 0, "sus": 0}
    est = 0.0
    for bl in p["blocks"]:
        print(f"block {bl['name']}:")
        for r in bl.get("runs", []):
            la = r.get("launch", {})
            sus = la.get("processes", 1) == 9
            if bl["name"] != "SMOKE":
                n["sus" if sus else "burst"] += 1
                est += 145 if sus else 40
            a = p["admission"].get(r["label"].replace("-rep2", ""), {})
            print(f"  {r['label']:30s} {'sus' if sus else 'burst':5s} {r.get('mask', ''):11s} {r['values'][:60]:60s} {('fixed ' + str(a.get('fixed_p800_w'))) if 'fixed_p800_w' in a else ('probe ' + str(a.get('probe')))}")
    print(n, f"about {est / 60:.0f} card-minutes at 40 s a burst and 145 s a sustained run; the cap and the slot cut the tail")


if __name__ == "__main__":
    main()
