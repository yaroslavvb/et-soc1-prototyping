#!/usr/bin/env python3
"""What place-and-route actually did to the netlist, and how the clock tree is gated.

  structure.py <syn_netlist.v> <pnr_netlist.v> <net_cap.txt> <pnr_toggles.json.gz>... > structure.json

Reports the cell-count delta (which is how you see that `repair_design` downsized far more than it
buffered), the nets CTS and repair_design created, and the clock tree split into the ungated root
and the branches behind the RTL's own clock gates, with the capacitance that toggles in each
pattern.
"""
import gzip, json, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hierparse import flat_nets                       # noqa: E402
from nlparse import parse as parse_flat               # noqa: E402

CLK = re.compile(r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")
ROOT = re.compile(r"^(clock|clknet_(leaf_)?\d+_clock|clknet_\d+_\d+_\d+_clock|"
                  r"clknet_\d+_\d+__leaf_clock|clknet_opt_\d+_\d+_clock)$")


def cells(path):
    txt = open(path, errors="replace").read()
    return Counter(re.findall(r"(?:^|\n)\s*([A-Za-z][A-Za-z0-9_]*_ASAP7_75t_[A-Z]+)\s", txt))


def main():
    syn, pnr, netcap = sys.argv[1], sys.argv[2], sys.argv[3]
    toggles = sys.argv[4:]
    a, b = cells(syn), cells(pnr)
    delta = {k: b.get(k, 0) - a.get(k, 0) for k in set(a) | set(b)}
    delta = {k.split("_ASAP7")[0]: v for k, v in delta.items() if v}
    added = {k: v for k, v in sorted(delta.items(), key=lambda kv: -kv[1]) if v > 0}
    removed = {k: v for k, v in sorted(delta.items(), key=lambda kv: kv[1]) if v < 0}

    cap = {}
    for line in open(netcap):
        if line.startswith("#"):
            continue
        p = line.split()
        if len(p) >= 3:
            cap[p[0]] = (float(p[1]) + float(p[2])) * 1e15
    pre = flat_nets(syn, "txfma_top")
    new = {n: c for n, c in cap.items() if n not in pre}
    _, _, insts = parse_flat(pnr)
    dll = [i for ct, i, _ in insts if "DLLx1" in ct]
    clkpin = Counter(cs["CLK"] for ct, _, cs in insts if "CLK" in cs)
    gated_roots = sorted(n for n in cap if n.endswith("_clk") and not n.startswith("clknet"))

    out = {
        "cells": {"pre_route": sum(a.values()), "post_cts": sum(b.values()),
                  "delta": sum(b.values()) - sum(a.values()),
                  "distinct_types": {"pre_route": len(a), "post_cts": len(b)},
                  "added": added, "removed": removed,
                  "cells_added_total": sum(added.values()),
                  "cells_removed_total": -sum(removed.values()),
                  "comment": "repair_design is overwhelmingly a DOWNSIZE pass on this netlist: "
                             "the traffic runs to weaker drives, and the only cells it and CTS "
                             "actually insert are buffers"},
        "nets_place_and_route_created": {
            "total": len(new), "cap_fF": sum(new.values()),
            "clknet": sum(1 for n in new if n.startswith("clknet_")),
            "clknet_cap_fF": sum(c for n, c in new.items() if n.startswith("clknet_")),
            "repair_netN": sum(1 for n in new if re.match(r"^net\d+$", n)),
            "repair_netN_cap_fF": sum(c for n, c in new.items() if re.match(r"^net\d+$", n)),
        },
        "clock_gating": {
            "et_clk_gate_instances_DLLx1": len(dll),
            "gate_instance_names": sorted(dll),
            "gated_clock_nets": gated_roots,
            "clock_pins_on_flops_and_latches": sum(clkpin.values()),
            "distinct_nets_on_a_clock_pin": len(clkpin),
            "what_the_rtl_has": "13 et_clk_gate instances, each a DLLx1 latch and its AND, all in "
                                "the fraction block; the exponent and control blocks' flops hang "
                                "off the ungated root",
        },
    }
    tree = {}
    for t in toggles:
        pat = re.sub(r".*?_(.*)\.json\.gz$", r"\1", os.path.basename(t))
        d = json.load(gzip.open(t))
        sim = {k.replace("\\", ""): v for k, v in d["toggles"].items()}
        acc = {"root": [0, 0.0, 0.0], "gated": [0, 0.0, 0.0]}
        for n, c in cap.items():
            if not CLK.search(n):
                continue
            k = "root" if ROOT.match(n) else "gated"
            acc[k][0] += 1
            acc[k][1] += c
            if sim.get(n, 0):
                acc[k][2] += c
        tot = acc["root"][1] + acc["gated"][1]
        tog = acc["root"][2] + acc["gated"][2]
        tree[pat] = {
            "root_nets": acc["root"][0], "root_cap_fF": acc["root"][1],
            "root_cap_toggling_fF": acc["root"][2],
            "gated_nets": acc["gated"][0], "gated_cap_fF": acc["gated"][1],
            "gated_cap_toggling_fF": acc["gated"][2],
            "clock_cap_fF": tot, "clock_cap_toggling_fF": tog,
            "fraction_of_the_tree_toggling": tog / tot,
        }
    out["clock_gating"]["tree_per_pattern"] = tree
    if "randn" in tree and "zeros" in tree:
        out["clock_gating"]["zero_gating_shuts"] = (
            1 - tree["zeros"]["clock_cap_toggling_fF"] / tree["randn"]["clock_cap_toggling_fF"])
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
