#!/usr/bin/env python3
"""Q128(d) part 2, from the DEF: what one physical-net toggle actually charges.

The first pass read the flat Verilog (`txfma_pnr.v`) and matched only 15,001 of
the 20,383 extracted nets, because OpenROAD's per-net capacitance table names
nets hierarchically (`txfmafrac0_top/txfma0_f1/fb_f1a_h[18]`) while the written
Verilog is flat and mangled.  The placed DEF uses the SAME names as the
capacitance table, so it is the right source for fanout; this reads it.

For every net: the gate pins it drives, the cells behind them, its wire and pin
capacitance from the global-route Steiner estimate, and its toggle count in one
random fp32 multiply-add — weights taken with tools/open-flow/txfma/power.py's
own SAIF reader, so they are exactly the ones behind the published 1.516 pJ.

  fanout2.py <tools_dir> <pnr_dir> <def> <saif_op> <saif_base> <libdir> <cdl> <out.json> [muladds]

Open data only.  No card, no vault.
"""
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, sys.argv[1])
import power as P   # noqa: E402

STRIP = "tb/lane[0]/txfma"
CLK_RE = re.compile(r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")

CELL_RE = re.compile(r'^\s*cell\s*\(\s*"?([^")]+)"?\s*\)')
PIN_RE = re.compile(r'^\s*pin\s*\(\s*"?([^")]+)"?\s*\)')
DIR_RE = re.compile(r'^\s*direction\s*:\s*([a-z]+)\s*;')
CAP_RE = re.compile(r'^\s*capacitance\s*:\s*([-0-9.eE+]+)\s*;')


def read_liberty_pins(libdir):
    """{cell: {pin: [direction, capacitance_fF]}}; ASAP7's load unit is 1 fF.
    Only the per-group liberties: work/lib also holds concatenations of them."""
    out = {}
    for fn in sorted(os.listdir(libdir)):
        if not (fn.startswith("asap7sc7p5t_") and fn.endswith(".lib")):
            continue
        cell = pin = None
        dc = dp = None
        depth = 0
        for line in open(os.path.join(libdir, fn), errors="replace"):
            m = CELL_RE.match(line)
            if m and "{" in line:
                cell, dc = m.group(1), depth
                out.setdefault(cell, {})
            elif cell is not None:
                m = PIN_RE.match(line)
                if m and "{" in line:
                    pin, dp = m.group(1), depth
                    out[cell].setdefault(pin, ["", None])
                elif pin is not None:
                    m = DIR_RE.match(line)
                    if m:
                        out[cell][pin][0] = m.group(1)
                    else:
                        m = CAP_RE.match(line)
                        if m and out[cell][pin][1] is None:
                            out[cell][pin][1] = float(m.group(1))
            depth += line.count("{") - line.count("}")
            if dp is not None and depth <= dp:
                pin, dp = None, None
            if dc is not None and depth <= dc:
                cell, dc = None, None
    return out


def read_def(path):
    """COMPONENTS -> {instance: cell}; NETS -> {net: [(instance, pin), ...]}."""
    comp, nets = {}, {}
    sect = None
    buf = []
    cur = None
    conn = re.compile(r'\(\s*(\S+)\s+(\S+)\s*\)')
    for line in open(path, errors="replace"):
        s = line.strip()
        if s.startswith("COMPONENTS "):
            sect = "C"
            continue
        if s.startswith("END COMPONENTS"):
            sect = None
            continue
        if s.startswith("NETS "):
            sect = "N"
            continue
        if s.startswith("END NETS"):
            if cur is not None:
                nets[cur] = parse_conns(" ".join(buf), conn)
            sect = None
            continue
        if sect == "C":
            if s.startswith("- "):
                p = s.split()
                if len(p) >= 3:
                    comp[p[1]] = p[2]
        elif sect == "N":
            if s.startswith("- "):
                if cur is not None:
                    nets[cur] = parse_conns(" ".join(buf), conn)
                p = s.split()
                cur = p[1]
                buf = [s[2 + len(cur):]]
            elif cur is not None:
                buf.append(s)
            if s.endswith(";"):
                if cur is not None:
                    nets[cur] = parse_conns(" ".join(buf), conn)
                cur, buf = None, []
    return comp, nets


def parse_conns(text, conn):
    # stop at the routing part of the record: + ROUTED / + USE / + NONDEFAULTRULE
    cut = len(text)
    for kw in (" + ROUTED", " + FIXED", " + COVER", " + USE ", " + NONDEFAULTRULE",
               " + SOURCE", " + WEIGHT", " + PROPERTY"):
        i = text.find(kw)
        if i >= 0:
            cut = min(cut, i)
    return conn.findall(text[:cut])


def main():
    _, pnr_dir, defp, saif_op, saif_base, libdir, cdl, outp = sys.argv[1:9]
    muladds = float(sys.argv[9]) if len(sys.argv) > 9 else 512.0
    vdd = 0.517

    libpins = read_liberty_pins(libdir)
    comp, defnets = read_def(defp)

    # Fins behind each INPUT PIN, from the CDL the SPICE decks use: a device
    # counts against a pin only if that pin IS its gate node.  (Dividing a
    # cell's total fins by its input-pin count over-counts every compound cell,
    # whose output-stage devices are gated by an internal node.)
    fins_by_pin, fins_total = {}, {}
    cur, ports = None, []
    for line in open(cdl, errors="replace"):
        s = line.strip()
        if s.upper().startswith(".SUBCKT "):
            p = s.split()
            cur, ports = p[1], p[2:]
            fins_by_pin[cur] = {}
            fins_total[cur] = 0
        elif s.upper().startswith(".ENDS"):
            cur, ports = None, []
        elif cur and (s.startswith("N") or s.startswith("M")):
            p = s.split()
            if len(p) < 6:
                continue
            gate = p[2]
            m = re.search(r'nfin\s*=\s*(\d+)', s)
            k = int(m.group(1)) if m else 1
            fins_total[cur] += k
            if gate in ports:
                fins_by_pin[cur][gate] = fins_by_pin[cur].get(gate, 0) + k

    wire, pin = {}, {}
    for line in open(os.path.join(pnr_dir, "net_cap_globalroute.txt")):
        if line.startswith("#"):
            continue
        p = line.split()
        if len(p) == 3:
            wire[p[0]] = float(p[1]) * 1e15
            pin[p[0]] = float(p[2]) * 1e15

    tc = P.read_saif(saif_op, STRIP)
    base = P.read_saif(saif_base, STRIP)
    sim = {k.replace("\\", ""): v - base.get(k, 0)
           for k, v in tc.items() if v - base.get(k, 0) > 0}

    def activity(net):
        if net in sim:
            return sim[net]
        if net.startswith("clknet_"):
            rest = net[len("clknet_"):]
            while rest:
                if rest in sim:
                    return sim[rest]
                if "_" not in rest:
                    break
                rest = rest.split("_", 1)[1]
        return 0

    rows = []
    miss_cell = defaultdict(int)
    for net in wire:
        conns = defnets.get(net, [])
        fo = 0
        fincount = 0.0
        libcap = 0.0
        cellmix = []
        for inst, pn in conns:
            cell = comp.get(inst)
            if cell is None:
                if inst != "PIN":
                    miss_cell[inst] += 1
                continue
            d, cap = libpins.get(cell, {}).get(pn, ["", None])
            if d == "input":
                fo += 1
                libcap += cap or 0.0
                fincount += fins_by_pin.get(cell, {}).get(pn, 0)
                cellmix.append(cell)
        rows.append({
            "net": net, "fanout": fo, "fins_behind_the_pins": fincount,
            "liberty_pin_fF": libcap,
            "wire_fF": wire[net], "pin_fF": pin[net],
            "toggles": activity(net),
            "is_clock": bool(CLK_RE.search(net)),
            "in_def": net in defnets,
        })

    def summarise(rs, label):
        if not rs:
            return None
        n = len(rs)
        tog = sum(x["toggles"] for x in rs)

        def wm(key):
            return (sum(x[key] * x["toggles"] for x in rs) / tog) if tog else None
        return {
            "label": label, "nets": n,
            "toggles_total": tog, "toggles_per_muladd": tog / muladds,
            "fanout_mean_unweighted": sum(x["fanout"] for x in rs) / n,
            "fanout_mean_toggle_weighted": wm("fanout"),
            "fins_behind_the_pins_toggle_weighted": wm("fins_behind_the_pins"),
            "wire_fF_mean_toggle_weighted": wm("wire_fF"),
            "pin_fF_mean_toggle_weighted": wm("pin_fF"),
            "liberty_pin_fF_from_the_DEF_toggle_weighted": wm("liberty_pin_fF"),
            "cap_fF_mean_toggle_weighted": (wm("wire_fF") + wm("pin_fF")) if tog else None,
            "wire_share_of_cap_toggle_weighted":
                (wm("wire_fF") / (wm("wire_fF") + wm("pin_fF"))) if tog else None,
            "E_per_toggle_fJ_half_CV2":
                (0.5 * (wm("wire_fF") + wm("pin_fF")) * 1e-15 * vdd * vdd * 1e15) if tog else None,
            "cap_fF_total": sum(x["wire_fF"] + x["pin_fF"] for x in rs),
            "nets_found_in_the_DEF": sum(1 for x in rs if x["in_def"]),
        }

    sig = [x for x in rows if not x["is_clock"]]
    clk = [x for x in rows if x["is_clock"]]
    act = [x for x in sig if x["toggles"] > 0]
    actdef = [x for x in act if x["in_def"]]

    out = {
        "what": "per-physical-net fanout, gate pins driven, fins behind them and "
                "capacitance in the placed TensorFMA32 netlist, weighted by the "
                "activity of one random fp32 multiply-add",
        "inputs": {"def": defp, "netcap": os.path.join(pnr_dir, "net_cap_globalroute.txt"),
                   "saif_op": saif_op, "saif_base": saif_base, "libdir": libdir,
                   "cdl": cdl, "muladds": muladds, "vdd_V": vdd, "strip": STRIP},
        "def_components": len(comp), "def_nets": len(defnets),
        "nets_in_netcap": len(rows),
        "nets_in_netcap_found_in_the_DEF": sum(1 for x in rows if x["in_def"]),
        "def_instances_with_no_cell": len(miss_cell),
        "summary": {
            "all_nets": summarise(rows, "every extracted net"),
            "signal_nets": summarise(sig, "signal nets (clock tree excluded)"),
            "signal_nets_active": summarise(act, "signal nets that toggle in this multiply-add"),
            "signal_nets_active_named_by_the_DEF": summarise(
                actdef, "the same, restricted to nets the DEF names -- the unbiased "
                        "fanout, since a net the DEF does not name reads as fanout 0"),
            "clock_nets": summarise(clk, "clock-tree nets"),
        },
    }

    h, ht = defaultdict(int), defaultdict(int)
    for x in sig:
        k = min(x["fanout"], 10)
        h[k] += 1
        ht[k] += x["toggles"]
    out["fanout_histogram_signal_nets"] = {
        ("10+" if k == 10 else str(k)): {"nets": h[k], "toggles": ht[k]} for k in sorted(h)}

    drive = defaultdict(float)
    for x in rows:
        pass
    for net in wire:
        n = activity(net)
        if not n or CLK_RE.search(net):
            continue
        for inst, pn in defnets.get(net, []):
            cell = comp.get(inst)
            if cell and libpins.get(cell, {}).get(pn, ["", None])[0] == "input":
                drive[cell] += n
    tot = sum(drive.values()) or 1.0
    out["driven_cell_mix_by_toggle_weighted_pins"] = {
        k: round(v / tot, 6) for k, v in sorted(drive.items(), key=lambda kv: -kv[1])[:15]}

    # how well the DEF's own pin capacitance reproduces the extractor's pin column
    num = den = 0.0
    for x in rows:
        if x["toggles"] and x["pin_fF"] > 0:
            num += x["liberty_pin_fF"] * x["toggles"]
            den += x["pin_fF"] * x["toggles"]
    out["check_liberty_pin_sum_over_extractor_pin_column"] = (num / den) if den else None

    json.dump(out, open(outp, "w"), indent=1, sort_keys=True)
    print("wrote", outp)
    print(json.dumps(out["summary"], indent=1))
    print("DEF coverage:", out["nets_in_netcap_found_in_the_DEF"], "of", out["nets_in_netcap"])
    print("pin-cap check:", out["check_liberty_pin_sum_over_extractor_pin_column"])


if __name__ == "__main__":
    main()
