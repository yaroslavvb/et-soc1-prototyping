#!/usr/bin/env python3
"""Cell, transistor and flip-flop census of a hierarchical Yosys netlist mapped onto ASAP7.

    census.py --json <yosys .json> --cdl <asap7sc7p5t_28_R.cdl> --lib <dir of .lib> --out <census.json>

Counts, for the whole unit and for every block of the hierarchy:
  cells          standard-cell instances
  transistors    MOSFETs, from ASAP7's own CDL netlist of each cell (BSD-3-Clause)
  fins           fins over those MOSFETs (ASAP7 draws 3 fins on an x1 device, not 2)
  flops          sequential cells (a liberty ff() group)
  latches        liberty latch() groups, which is what an et_clk_gate becomes
  area           liberty cell areas, in the library's own (4x-drawn) square microns;
                 divide by 16 for drawn 7 nm microns
Blocks are the instance paths of the hierarchy, aggregated at each depth.
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict


def read_cdl(path):
    """{cell: (n_mos, n_fins)} from a CDL/LVS netlist."""
    out = {}
    cur, nmos, fins = None, 0, 0
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.upper().startswith(".SUBCKT"):
                cur, nmos, fins = s.split()[1], 0, 0
            elif s.upper().startswith(".ENDS"):
                if cur:
                    out[cur] = (nmos, fins)
                cur = None
            elif cur and s[:1].upper() == "M":
                nmos += 1
                m = re.search(r"nfin=(\d+)", s)
                fins += int(m.group(1)) if m else 0
    return out


def read_libs(libdir):
    """{cell: {'area':float,'kind':'ff'|'latch'|'comb','clock_pins':[..],'cap':{pin:ff}}}"""
    cells = {}
    for fn in sorted(os.listdir(libdir)):
        if not fn.endswith(".lib"):
            continue
        name, depth, cur = None, 0, None
        with open(os.path.join(libdir, fn), errors="replace") as fh:
            for line in fh:
                s = line.strip()
                m = re.match(r"cell\s*\(\s*([A-Za-z0-9_]+)\s*\)", s)
                if m and depth <= 1:
                    name = m.group(1)
                    cur = {"area": 0.0, "kind": "comb", "clock_pins": [], "cap": {}}
                    cells[name] = cur
                    pin = None
                if cur is not None:
                    m = re.match(r"pin\s*\(\s*([A-Za-z0-9_]+)\s*\)", s)
                    if m:
                        pin = m.group(1)
                    if s.startswith("area"):
                        try:
                            cur["area"] = float(s.split(":")[1].strip().rstrip(";"))
                        except Exception:
                            pass
                    if re.match(r"ff\s*\(", s):
                        cur["kind"] = "ff"
                    if re.match(r"latch\s*\(", s):
                        cur["kind"] = "latch"
                    if s.startswith("clock") and "true" in s:
                        if pin:
                            cur["clock_pins"].append(pin)
                    if s.startswith("capacitance") and pin:
                        try:
                            cur["cap"][pin] = float(s.split(":")[1].strip().rstrip(";"))
                        except Exception:
                            pass
                depth += line.count("{") - line.count("}")
    return cells


def walk(mods, top):
    """yield (path, leaf_type) for every leaf cell, path = 'a/b/c'."""
    stack = [(top, "")]
    while stack:
        mod, path = stack.pop()
        for inst, c in mods[mod].get("cells", {}).items():
            t = c["type"]
            p = (path + "/" + inst) if path else inst
            if t in mods:
                stack.append((t, p))
            else:
                yield p, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--cdl", required=True)
    ap.add_argument("--lib", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--top", default="txfma_top")
    a = ap.parse_args()

    cdl = read_cdl(a.cdl)
    lib = read_libs(a.lib)
    with open(a.json) as fh:
        mods = json.load(fh)["modules"]
    top = a.top if a.top in mods else next(k for k in mods if k.endswith(a.top))

    # module type of every instance path, so blocks can be named by what they are
    types = {}
    stack = [(top, "")]
    while stack:
        mod, path = stack.pop()
        for inst, c in mods[mod].get("cells", {}).items():
            t = c["type"]
            p = (path + "/" + inst) if path else inst
            if t in mods:
                types[p] = re.sub(r"^\$paramod[^\\]*\\\\?", "", t).lstrip("\\")
                stack.append((t, p))

    tot = defaultdict(float)
    by_cell = defaultdict(int)
    by_path = defaultdict(lambda: defaultdict(float))
    unknown = set()

    for path, t in walk(mods, top):
        t = t.lstrip("\\")
        by_cell[t] += 1
        nmos, fins = cdl.get(t, (0, 0))
        if t not in cdl:
            unknown.add(t)
        li = lib.get(t, {})
        kind = li.get("kind", "comb")
        clkcap = sum(li.get("cap", {}).get(p, 0.0) for p in li.get("clock_pins", []))
        rec = {"cells": 1, "transistors": nmos, "fins": fins,
               "area": li.get("area", 0.0),
               "flops": 1 if kind == "ff" else 0,
               "latches": 1 if kind == "latch" else 0,
               "clk_cap_ff": clkcap}
        for k, v in rec.items():
            tot[k] += v
        parts = path.split("/")[:-1]          # drop the leaf instance name
        for d in range(1, min(len(parts), 4) + 1):
            key = "/".join(parts[:d])
            for k, v in rec.items():
                by_path[key][k] += v

    blocks = []
    for key, rec in sorted(by_path.items(), key=lambda kv: -kv[1]["cells"]):
        blocks.append({"path": key, "module": types.get(key, ""), "depth": key.count("/") + 1,
                       **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in rec.items()}})

    out = {
        "top": top,
        "total": {k: (round(v, 4) if k in ("area", "clk_cap_ff") else int(v)) for k, v in tot.items()},
        "by_cell_type": dict(sorted(by_cell.items(), key=lambda kv: -kv[1])),
        "blocks": blocks,
        "cells_without_cdl": sorted(unknown),
        "note": ("area and lengths are in ASAP7's 4x drawing scale: divide area by 16 and length by 4 "
                 "for drawn 7 nm units. Capacitances in the liberty are already in real fF."),
    }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(out["total"], indent=1))
    print("blocks:", len(blocks), "cell types:", len(by_cell), "no CDL:", len(unknown))


if __name__ == "__main__":
    main()
