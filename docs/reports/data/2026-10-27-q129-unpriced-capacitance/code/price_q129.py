#!/usr/bin/env python3
"""Q129: price the half of the open design's capacitance Q126(e)'s ledger left unpriced.

Q126(e) (docs/reports/data/2026-10-26-open-netlist/POWER.md) joins a per-net capacitance table
from the global route onto a SAIF taken on the PRE-route netlist, and reports that 49.5% of the
design's farads go unpriced -- attributing the gap to "the 9,923 nets CTS and repair_design
created after the netlist was simulated". This script resolves every one of those nets to a
labelled activity and prices it with the same arithmetic (1/2 C V^2 per toggle at 0.517 V), so the
gap is decomposed instead of asserted.

Methods, in the order they are tried, each labelled in the output:
  direct     the extracted name is in the differenced SAIF             (what power.py prices)
  cts_name   power.py's own clknet_<n>_<source> name-strip rule        (what power.py prices)
  bitshift   the same wire under the simulator's own bit numbering: Verilator renumbers a vector
             whose declared LSB is not 0 (this unit has many, e.g. [63:32]) from 0 in its SAIF, so
             the extractor's bus[32] and the SAIF's bus[0] are one wire
  alias      the SAME physical net under another hierarchical name: a wire that crosses a module
             boundary has one name per level, the extractor keeps one and the simulation writes
             the others, so the two tables are joined through the instance tree
  buffer     the net is driven by a one-input cell (BUF/INV/CKINVDC) in the post-CTS netlist, so
             at zero delay it toggles exactly as that cell's input net -- this is what prices
             repair_design's buffers and the clock tree CTS built
  tie        driven by TIEHIx1/TIELOx1: a constant, zero toggles
  sim_zero   the simulation names the net and its differenced activity is zero: priced at zero
             switching energy, which is an ANSWER, not a gap
  unresolved nothing above applies
"""
import argparse, gzip, json, os, re, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hierparse import alias_classes, flat_nets, bit_offsets   # noqa: E402
from nlparse import parse as parse_flat                 # noqa: E402

OUT_PINS = {"Y", "Q", "H", "L"}          # ASAP7 RVT: every cell in this netlist drives one of these
ONE_IN = re.compile(r'^(BUF|INV|CKINV)')  # one-input, one-output: output toggles with the input


def read_netcap(path):
    cap = {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.split()
            if len(p) >= 3:
                try:
                    cap[p[0]] = (float(p[1]) + float(p[2])) * 1e15      # F -> fF
                except ValueError:
                    pass
    return cap


def build_struct(pnr_netlist):
    """driver[net] = (celltype, inst, {pin: net}); the post-CTS netlist is flat, so its net names
    are the extractor's own names."""
    ports, wires, insts = parse_flat(pnr_netlist)
    driver = {}
    for ct, inst, cs in insts:
        for pin, net in cs.items():
            if pin in OUT_PINS:
                driver[net] = (ct, inst, cs)
    return ports, set(wires), insts, driver


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--netcap", required=True)
    ap.add_argument("--pnr-netlist", required=True)
    ap.add_argument("--syn-netlist", required=True)
    ap.add_argument("--top", default="txfma_top")
    ap.add_argument("--toggles", required=True, help="gz json from saif_reduce.py")
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--vdd", type=float, default=0.517)
    ap.add_argument("--muladds", type=float, default=512.0)
    ap.add_argument("--clock-re", default=r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")
    ap.add_argument("--cell-energies")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    cap = read_netcap(a.netcap)
    cap_all = sum(cap.values())
    d = json.load(gzip.open(a.toggles))
    sim = {k.replace("\\", ""): v for k, v in d["toggles"].items()}
    simnames = set(n.replace("\\", "") for n in d["names_measured"])

    uf, _ = alias_classes(a.syn_netlist, a.top)
    pre = flat_nets(a.syn_netlist, a.top)
    boff = bit_offsets(a.syn_netlist, a.top)
    bitsel = re.compile(r'^(.*)\[(\d+)\]$')
    _, pnr_wires, _, driver = build_struct(a.pnr_netlist)

    # class -> activity, from any member the simulation knows
    cls_act, cls_disagree = {}, 0
    for n, v in sim.items():
        if n in uf.p:
            r = uf.find(n)
            if r in cls_act and cls_act[r] != v:
                cls_disagree += 1
                cls_act[r] = max(cls_act[r], v)
            else:
                cls_act[r] = v
    cls_known = set()
    for n in simnames:
        if n in uf.p:
            cls_known.add(uf.find(n))

    memo = {}

    def activity(net, depth=0):
        """(toggles, method). Memoised; `depth` guards a buffer loop."""
        if net in memo:
            return memo[net]
        if depth > 40:
            return None, "unresolved"
        memo[net] = (None, "pending")
        r = _activity(net, depth)
        memo[net] = r
        return r

    def _activity(net, depth):
        if net in sim:
            return sim[net], "direct"
        if net.startswith("clknet_"):                    # power.py's own rule, kept verbatim
            rest = net[len("clknet_"):]
            while rest:
                if rest in sim:
                    return sim[rest], "cts_name"
                if "_" not in rest:
                    break
                rest = rest.split("_", 1)[1]
        m = bitsel.match(net)
        if m and m.group(1) in boff:
            shifted = f"{m.group(1)}[{int(m.group(2)) - boff[m.group(1)]}]"
            if shifted in sim:
                return sim[shifted], "bitshift"
            if shifted in simnames:
                return 0, "bitshift"
        if net in uf.p:
            r = uf.find(net)
            if r in cls_act:
                return cls_act[r], "alias"
        drv = driver.get(net)
        if drv is not None:
            ct, inst, cs = drv
            base = ct.split("_ASAP7")[0]
            if base.startswith(("TIEHI", "TIELO")):
                return 0, "tie"
            if ONE_IN.match(base):
                src = cs.get("A")
                if src is not None:
                    n, how = activity(src, depth + 1)
                    if n is not None:
                        return n, "buffer"
        if net in simnames or (net in uf.p and uf.find(net) in cls_known):
            return 0, "sim_zero"
        if net in pre:
            # the pre-route netlist has it, the simulation never names it: Verilator folded it
            return None, "folded"
        return None, "unresolved"

    clk = re.compile(a.clock_re)
    V2 = a.vdd * a.vdd
    by = defaultdict(lambda: defaultdict(float))
    rows = []
    for net, c in sorted(cap.items()):
        n, how = activity(net)
        isclk = bool(clk.search(net))
        kind = "clock" if isclk else "signal"
        isnew = net not in pre
        e = 0.0 if not n else 0.5 * c * 1e-15 * V2 * n
        for k in (how, f"{how}|{kind}", f"ALL|{kind}", "ALL"):
            by[k]["nets"] += 1
            by[k]["cap_fF"] += c
            by[k]["toggles"] += (n or 0)
            by[k]["energy_J"] += e
        if isnew:
            for k in ("NEW", f"NEW|{kind}", f"NEW|{how}"):
                by[k]["nets"] += 1
                by[k]["cap_fF"] += c
                by[k]["toggles"] += (n or 0)
                by[k]["energy_J"] += e
        rows.append((net, c, n, how, kind, isnew))

    # power.py's own join, reproduced exactly, for the before/after
    base_e = base_cap = 0.0
    base_tog = defaultdict(float)
    base_nets = 0
    for net, c, n, how, kind, isnew in rows:
        if how in ("direct", "cts_name") and n:
            base_nets += 1
            base_cap += c
            base_e += 0.5 * c * 1e-15 * V2 * n
            base_tog[kind] += n
        elif how in ("direct", "cts_name"):
            base_nets += 1
    full_e = by["ALL"]["energy_J"]
    priced_cap_full = sum(c for _, c, n, how, _, _ in rows
                          if n is not None)
    out = {
        "pattern": a.pattern,
        "inputs": {"netcap": os.path.basename(a.netcap),
                   "pnr_netlist": os.path.basename(a.pnr_netlist),
                   "syn_netlist": os.path.basename(a.syn_netlist),
                   "toggles": os.path.basename(a.toggles),
                   "vdd": a.vdd, "muladds": a.muladds},
        "design": {"extracted_nets": len(cap), "cap_fF_extracted": cap_all,
                   "pre_route_flat_nets": len(pre),
                   "nets_cts_and_repair_added": sum(1 for r in rows if r[5]),
                   "cap_fF_cts_and_repair_added": by["NEW"]["cap_fF"],
                   "cap_fraction_cts_and_repair_added": by["NEW"]["cap_fF"] / cap_all,
                   "alias_classes_with_disagreeing_members": cls_disagree},
        "baseline_power_py": {
            "nets_matched": base_nets,
            "cap_fF_priced": base_cap,
            "cap_fraction_priced": base_cap / cap_all,
            "signal_toggles_per_muladd": base_tog["signal"] / a.muladds,
            "clock_toggles_per_muladd": base_tog["clock"] / a.muladds,
            "energy_J": base_e,
            "pJ_per_muladd": base_e / a.muladds * 1e12,
        },
        "resolved": {k: dict(v) for k, v in sorted(by.items())},
        "after": {
            "cap_fF_resolved": priced_cap_full,
            "cap_fraction_resolved": priced_cap_full / cap_all,
            "signal_toggles_per_muladd": by["ALL|signal"]["toggles"] / a.muladds,
            "clock_toggles_per_muladd": by["ALL|clock"]["toggles"] / a.muladds,
            "energy_J": full_e,
            "pJ_per_muladd": full_e / a.muladds * 1e12,
            "signal_pJ_per_muladd": by["ALL|signal"]["energy_J"] / a.muladds * 1e12,
            "clock_pJ_per_muladd": by["ALL|clock"]["energy_J"] / a.muladds * 1e12,
            "added_pJ_per_muladd": (full_e - base_e) / a.muladds * 1e12,
            "ratio_to_baseline": (full_e / base_e) if base_e else 0.0,
        },
        "residue": {
            "nets": by["unresolved"]["nets"] + by["folded"]["nets"],
            "cap_fF": by["unresolved"]["cap_fF"] + by["folded"]["cap_fF"],
            "cap_fraction": (by["unresolved"]["cap_fF"] + by["folded"]["cap_fF"]) / cap_all,
        },
    }
    if a.cell_energies:
        with open(a.cell_energies) as fh:
            ce = json.load(fh)
        mix = ce["census_weighted_mix"]
        v_lib = float(ce["operating_point"]["VDD_liberty_V"])
        e_mix = float(mix["weighted_E_int_per_transition_VDDonly_fJ_0p7"]) * (a.vdd / v_lib) ** 2
        s_base = base_tog["signal"]
        s_full = by["ALL|signal"]["toggles"]
        c_full = by["ALL|clock"]["toggles"]
        out["internal_estimate"] = {
            "E_int_per_transition_fJ_at_vdd": e_mix,
            "baseline_signal_internal_pJ_per_muladd": s_base * e_mix * 1e-15 / a.muladds * 1e12,
            "after_signal_internal_pJ_per_muladd": s_full * e_mix * 1e-15 / a.muladds * 1e12,
            "clock_tree_buffer_internal_pJ_per_muladd":
                by["ALL|clock"]["toggles"] * e_mix * 1e-15 / a.muladds * 1e12,
            "note": "the per-transition figure is Q126(d)'s combinational-cell mix; the clock row "
                    "prices the CTS buffers' own internal energy on the same figure, which the "
                    "published estimate left out entirely (it counted signal transitions only)",
            "clock_toggles_per_muladd": c_full / a.muladds,
        }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    # a per-net dump of everything CTS/repair added, and of everything unresolved
    with gzip.open(a.out.replace(".json", "-nets.json.gz"), "wt") as fh:
        json.dump([{"net": n, "cap_fF": c, "toggles": t, "method": h, "kind": k, "new": bool(w)}
                   for n, c, t, h, k, w in rows if w or h != "direct"],
                  fh)
    print(json.dumps({k: out[k] for k in
                      ("pattern", "design", "baseline_power_py", "after", "residue")}, indent=1))
    print("--- by method ---")
    for k in sorted(by):
        if "|" in k or k in ("ALL", "NEW"):
            continue
        v = by[k]
        print(f"{k:11s} nets {v['nets']:6.0f}  cap {v['cap_fF']:9.1f} fF  "
              f"toggles/muladd {v['toggles']/a.muladds:9.2f}  pJ/muladd {v['energy_J']/a.muladds*1e12:8.4f}")


if __name__ == "__main__":
    main()
