#!/usr/bin/env python3
"""Q129(a): split an OpenRCX SPEF into per-net GROUND and COUPLING capacitance.

    spef_caps.py txfma_coupled.spef --table net_caps.txt --summary summary.json
                 [--pin-from net_cap_spef.txt] [--netcap-out caps_k1.txt --miller 1]

Why this exists. `power.py --spef` reads the `*D_NET <net> <total>` header and prices
1/2 C V^2 against it. That is one number per net and it hides the thing Q129 was asked for:
how much of a routed net's capacitance is coupling to its neighbours rather than to ground.
SPEF carries that explicitly --

    *CAP
    8 *1:68 2.70775e-05            <- one node:  capacitance to GROUND
    24 *1:6 *6308:46 1.32941e-05   <- two nodes: COUPLING between two nets

-- so a Miller factor becomes an explicit, stated choice instead of something buried in an
extractor flag:

    C_switched(net) = C_ground + k_miller * C_coupling   (+ the liberty's pin capacitance)

k = 0 is a net whose neighbours always move with it: no coupling cost at all, and the genuine
lower bound. k = 1 is the quiet-neighbour convention and the one to quote. k = 2 is a neighbour
switching the other way, the worst case.

k = 0 is NOT the analogue of the global-route Steiner estimate (corrected 27 Oct 2026; this header
first said it was). That estimate is not coupling-free either: the ORFS asap7 setRC.tcl hands it
0.1658 fF/um for a signal wire, a layer's TOTAL capacitance at nominal spacing with the neighbour
coupling bundled in and grounded -- which is why it comes out 20-23% ABOVE the k = 1 extraction,
not below the k = 0 one. See docs/reports/data/2026-10-27-q129-routed-netlist/README.md.

**Every coupling cap is charged to BOTH nets of its pair.** Under the quiet-neighbour
convention that is not a double count but the physics: net A's driver delivers C_c*V when A
switches past a still B, and B's driver does the same when B switches past a still A, so the
design's energy per period carries 1/2*C_c*V^2*(n_A + n_B). The summary therefore reports the
PHYSICAL coupling total (each cap once) and the per-net attribution (twice it) separately.

Three SPEF facts this depends on, all read out of the file and asserted in the summary:

  * OpenRCX writes `*DESIGN_FLOW ... "PIN_CAP NONE"`, so there are **no pin capacitances in the
    SPEF at all** -- the `*CONN` lines carry no `*L` field. The cell-internal half of each net
    has to come from the liberty, i.e. from OpenSTA's own `net ... pin_cap` table, which is what
    `--pin-from` reads. A `power.py --spef` run would silently price the wire half only.
  * **OpenRCX already writes each coupling cap under both of its nets** -- this design's SPEF has
    502,324 two-node `*CAP` entries for the 251,162 coupling caps OpenRCX reports extracting.
    Entries are therefore de-duplicated on their node pair before anything is summed; without
    that step the coupling total comes out exactly 2x too large. The de-duplication is measured
    (`coupling_entries_distinct` against `cap_entries_coupling`), not assumed, so a SPEF from a
    tool that writes each cap once is handled by the same code.
  * the second node of a coupling entry can be an instance PIN (`*21669:B`), whose name-map id
    is the INSTANCE, not the net. Resolving it needs the `*CONN` sections of every net, so this
    is a two-pass parse: collect, then resolve.
"""
import argparse
import gzip
import json
import re
from collections import defaultdict


def op(path):
    return gzip.open(path, "rt", errors="replace") if path.endswith(".gz") \
        else open(path, errors="replace")


def _unesc(name):
    """SPEF escapes a dot in a hierarchical name (`E1A_FF\\.Q[0]`); OpenSTA's own net table and
    the SAIF do not. Strip the escapes so the three sources key alike."""
    return name.replace("\\", "")


def parse(path):
    namemap = {}
    nets = {}
    pin2net = {}          # "instid:pin" (ids as written) -> net name
    coupling_raw = []     # (netA, partner_node_string, value_fF)
    c_unit = 1.0
    design_flow = ""
    section = None
    cur = cur_name = None
    n_g = n_c = n_L = 0
    with op(path) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("//"):
                continue
            if s.startswith("*C_UNIT"):
                p = s.split()
                try:
                    c_unit = float(p[1])
                except (ValueError, IndexError):
                    c_unit = 1.0
                if len(p) > 2:
                    u = p[2].upper()
                    if u.startswith("PF"):
                        c_unit *= 1000.0
                    elif u.startswith("NF"):
                        c_unit *= 1e6
                continue
            if s.startswith("*DESIGN_FLOW"):
                design_flow = s
                continue
            if s.startswith("*NAME_MAP"):
                section = "namemap"
                continue
            if s.startswith("*PORTS"):
                section = "ports"
                continue
            if s.startswith("*D_NET"):
                p = s.split()
                cur_name = _unesc(namemap.get(p[1], p[1].lstrip("*")))
                tot = 0.0
                if len(p) >= 3:
                    try:
                        tot = float(p[2]) * c_unit
                    except ValueError:
                        tot = 0.0
                cur = nets.setdefault(cur_name, {"ground": 0.0, "coupling": 0.0,
                                                 "pinload": 0.0, "dnet_total": 0.0,
                                                 "nconn": 0})
                cur["dnet_total"] += tot
                section = "dnet"
                continue
            if s.startswith("*END"):
                cur, cur_name, section = None, None, None
                continue
            if s.startswith("*CONN"):
                section = "conn"
                continue
            if s.startswith("*CAP"):
                section = "cap"
                continue
            if s.startswith("*RES") or s.startswith("*INDUC"):
                section = "res"
                continue
            if section == "namemap":
                p = s.split()
                if len(p) == 2 and p[0].startswith("*"):
                    namemap[p[0]] = p[1]
                continue
            if section == "conn" and cur is not None:
                p = s.split()
                if p and p[0] in ("*I", "*P") and len(p) >= 2:
                    cur["nconn"] += 1
                    if p[0] == "*I":
                        pin2net[p[1].lstrip("*")] = cur_name
                if "*L" in p:
                    try:
                        cur["pinload"] += float(p[p.index("*L") + 1]) * c_unit
                        n_L += 1
                    except (ValueError, IndexError):
                        pass
                continue
            if section == "cap" and cur is not None:
                p = s.split()
                if len(p) == 3:
                    try:
                        cur["ground"] += float(p[2]) * c_unit
                        n_g += 1
                    except ValueError:
                        pass
                elif len(p) == 4:
                    try:
                        v = float(p[3]) * c_unit
                    except ValueError:
                        continue
                    n_c += 1
                    # NOT added to cur["coupling"] here: OpenRCX writes the same cap under both
                    # nets, so the entries are de-duplicated first and then charged to both.
                    cur["dnet_coupling"] = cur.get("dnet_coupling", 0.0) + v
                    coupling_raw.append((cur_name, p[1], p[2], v))
                continue

    def resolve(node):
        base, _, suffix = node.lstrip("*").rpartition(":")
        if not base:
            return None
        if suffix.isdigit():                       # an internal node: the id IS the net
            return _unesc(namemap.get("*" + base, base))
        return pin2net.get(base + ":" + suffix)    # an instance pin: look it up in *CONN

    # De-duplicate on the unordered node pair, then charge each distinct cap to both its nets.
    seen = {}
    for netA, n1, n2, v in coupling_raw:
        key = (n1, n2) if n1 <= n2 else (n2, n1)
        if key not in seen:
            seen[key] = v
    unresolved = 0
    phys_total = 0.0
    for (n1, n2), v in seen.items():
        phys_total += v
        a, b = resolve(n1), resolve(n2)
        if a is None or b is None:
            unresolved += 1
        for side in (a, b):
            if side is None:
                continue
            nets.setdefault(side, {"ground": 0.0, "coupling": 0.0, "pinload": 0.0,
                                   "dnet_total": 0.0, "nconn": 0})
            nets[side]["coupling"] = nets[side].get("coupling", 0.0) + v
    return nets, {"c_unit_to_fF": c_unit, "design_flow": design_flow}, {
        "cap_entries_ground": n_g, "cap_entries_coupling": n_c,
        "coupling_entries_distinct": len(seen),
        "entries_per_distinct_cap": (n_c / len(seen)) if seen else 0.0,
        "conn_L_fields": n_L, "name_map_entries": len(namemap),
        "coupling_pairs_with_an_unresolved_side": unresolved,
        "coupling_total_physical_fF": phys_total}


def read_pin_caps(path):
    """pin_cap column of an OpenSTA `net wire_cap pin_cap` table, in farads -> fF."""
    out = {}
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.split()
            if len(p) >= 3:
                try:
                    out[p[0]] = float(p[2]) * 1e15
                except ValueError:
                    pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spef")
    ap.add_argument("--table", required=True,
                    help="per-net table: net ground_F coupling_F pinload_F (farads)")
    ap.add_argument("--pin-from",
                    help="OpenSTA 'net wire_cap pin_cap' table to take the pin column from, "
                         "because an OpenRCX SPEF carries PIN_CAP NONE")
    ap.add_argument("--summary")
    ap.add_argument("--netcap-out", help="power.py --netcap form: wire = ground + k*coupling")
    ap.add_argument("--miller", type=float, default=1.0)
    ap.add_argument("--clock-re", default=r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")
    a = ap.parse_args()

    nets, units, stats = parse(a.spef)
    pin = read_pin_caps(a.pin_from) if a.pin_from else {}
    if pin:
        for name, d in nets.items():
            if d["pinload"] == 0.0:
                d["pinload"] = pin.get(name, 0.0)
    clk = re.compile(a.clock_re)
    agg = defaultdict(float)
    n_clk = n_sig = 0
    with open(a.table, "w") as fh:
        fh.write("# net ground_F coupling_F pinload_F  (SPEF %s; coupling charged to BOTH "
                 "nets of each pair; pin column from %s)\n"
                 % (a.spef, a.pin_from or "the SPEF (PIN_CAP NONE -> zero)"))
        for name, d in sorted(nets.items()):
            fh.write("%s %.6e %.6e %.6e\n" % (name, d["ground"] * 1e-15,
                                              d["coupling"] * 1e-15, d["pinload"] * 1e-15))
            k = "clock" if clk.search(name) else "signal"
            if k == "clock":
                n_clk += 1
            else:
                n_sig += 1
            for col in ("ground", "coupling", "pinload", "dnet_total", "dnet_coupling"):
                agg[k + "_" + col + "_fF"] += d.get(col, 0.0)
    if a.netcap_out:
        with open(a.netcap_out, "w") as fh:
            fh.write("# net wire_cap pin_cap  (wire = ground + %g*coupling, farads)\n" % a.miller)
            for name, d in sorted(nets.items()):
                fh.write("%s %.6e %.6e\n"
                         % (name, (d["ground"] + a.miller * d["coupling"]) * 1e-15,
                            d["pinload"] * 1e-15))
    allf = {c: agg["signal_%s_fF" % c] + agg["clock_%s_fF" % c]
            for c in ("ground", "coupling", "pinload", "dnet_total", "dnet_coupling")}
    out = {"spef": a.spef, "units": units, "entries": stats,
           "nets": len(nets), "clock_nets": n_clk, "signal_nets": n_sig,
           "totals_fF": {k: v for k, v in sorted(agg.items())},
           "all_fF": allf, "miller_for_netcap_out": a.miller,
           "checks": {
               # Does each net's *D_NET header equal its own *CAP section (its ground caps plus
               # the coupling entries written under it)? Answered by the file, not assumed. The
               # SPEF's own per-net view already charges each coupling cap to both its nets, so
               # sum(dnet_total) = sum(ground) + 2 * physical coupling, and the k = 1 per-net
               # attribution below reproduces it.
               "sum_dnet_total_fF": allf["dnet_total"],
               "sum_ground_fF": allf["ground"],
               "sum_dnet_coupling_fF": allf["dnet_coupling"],
               "ground_plus_dnet_coupling_fF": allf["ground"] + allf["dnet_coupling"],
               "coupling_physical_once_fF": stats["coupling_total_physical_fF"],
               "coupling_charged_to_both_sides_fF": allf["coupling"],
           }}
    if a.summary:
        with open(a.summary, "w") as fh:
            json.dump(out, fh, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
