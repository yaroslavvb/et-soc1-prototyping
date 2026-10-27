#!/usr/bin/env python3
"""Price a gate-level activity file at the extracted capacitances, per block and per stage.

    power.py --saif <activity.saif> --spef <txfma.spef> [--vcd <dump.vcd>]
             --strip tb/lane[0]/txfma --cycles <n> --period-ns <f> [--vdd 0.517]
             --out power.json

Energy per net = 1/2 * C * V^2 per toggle, C the net's total capacitance from the SPEF (wire,
coupling to ground and the pin capacitances of everything it drives). Clock nets are reported
separately: they toggle twice a cycle, so their C*V^2 per cycle is the clock tree's share.

This is the switching energy only. The cells' own internal (short-circuit and internal-node)
energy is not in it; ASAP7's liberty carries it and the as-built work puts it at a few per cent
of a delivered bit, so the number here is a floor, and the ratio between two runs - which is what
the glitch question asks - is unaffected.

Blocks are the leading components of each net's hierarchical name, so the table reads
per stage (txfma0_f1 ...) and per block (ppg, wallace1, wallace2, prod_adder_64b).
"""
import argparse
import json
import re
from collections import defaultdict


def read_saif(path, strip):
    """{net_full_name: toggle_count} from a SAIF, walking its INSTANCE nesting."""
    tc = {}
    stack = []
    innet = False
    tok = re.compile(r'\(|\)|"[^"]*"|[^\s()]+')
    cur = None
    with open(path, errors="replace") as fh:
        text = fh.read()
    toks = tok.findall(text)
    i, depth_of = 0, []
    while i < len(toks):
        t = toks[i]
        if t == "(":
            kw = toks[i + 1] if i + 1 < len(toks) else ""
            if kw == "INSTANCE":
                name = toks[i + 2].strip('"') if i + 2 < len(toks) else ""
                stack.append(name)
                depth_of.append(("I", len(stack)))
                i += 3
                continue
            if kw == "NET":
                innet = True
                depth_of.append(("N", None))
                i += 2
                continue
            # A net entry is "( <name> ( T0 ...": its first child is another group. An attribute
            # is "( T0 <number> )". Do not test the keyword against a list of attribute names:
            # Verilator writes TB as well as T0/T1/TX/TZ/TC, and one missing name silently turns
            # every following count in that net into an attribute of nothing.
            if innet and i + 2 < len(toks) and toks[i + 2] == "(":
                cur = kw.strip('"')
                depth_of.append(("S", cur))
                i += 2
                continue
            depth_of.append(("O", None))
            i += 1
            continue
        if t == ")":
            if depth_of:
                k, v = depth_of.pop()
                if k == "I":
                    stack.pop()
                elif k == "N":
                    innet = False
                elif k == "S":
                    cur = None
            i += 1
            continue
        if t == "TC" and cur is not None:
            try:
                n = int(toks[i + 1])
            except (ValueError, IndexError):
                n = 0
            full = "/".join(stack + [cur])
            if strip and full.startswith(strip + "/"):
                full = full[len(strip) + 1:]
            tc[full] = tc.get(full, 0) + n
            i += 2
            continue
        i += 1
    return tc


def read_spef(path):
    """{net: total_cap_in_spef_units} from *D_NET lines."""
    cap, unit = {}, 1.0
    with open(path, errors="replace") as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("*C_UNIT"):
                p = s.split()
                try:
                    unit = float(p[1])
                except (ValueError, IndexError):
                    pass
                if len(p) > 2 and p[2].upper().startswith("PF"):
                    unit *= 1000.0        # to fF
            elif s.startswith("*D_NET"):
                p = s.split()
                if len(p) >= 3:
                    try:
                        cap[p[1].lstrip("*")] = float(p[2]) * unit
                    except ValueError:
                        pass
    return cap


def read_name_map(path):
    """SPEF *NAME_MAP: {*123: real_name}."""
    m = {}
    with open(path, errors="replace") as fh:
        inmap = False
        for line in fh:
            s = line.strip()
            if s.startswith("*NAME_MAP"):
                inmap = True
                continue
            if inmap:
                if s.startswith("*PORTS") or s.startswith("*D_NET"):
                    break
                if s.startswith("*"):
                    p = s.split()
                    if len(p) == 2:
                        m[p[0]] = p[1]
    return m


def block_of(net, depth):
    p = net.split("/")
    return "/".join(p[:depth]) if len(p) > depth else "/".join(p[:-1]) or "(top)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saif", required=True)
    ap.add_argument("--saif-base", help="a run of the same bench with the measured ops left out; "
                                        "its toggle counts are subtracted, because a SAIF counts "
                                        "the whole simulation and $dumpoff does not stop it")
    ap.add_argument("--spef")
    ap.add_argument("--netcap", help="fallback: 'net wire_cap pin_cap' table")
    ap.add_argument("--strip", default="tb/lane[0]/txfma")
    ap.add_argument("--vdd", type=float, default=0.517)
    ap.add_argument("--cycles", type=int, default=0)
    ap.add_argument("--muladds", type=float, default=0.0,
                    help="multiply-adds in the measured window, for the per-multiply-add numbers")
    ap.add_argument("--clock-re", default=r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf",
                    help="nets counted as clock")
    ap.add_argument("--block-depth", type=int, default=3,
                    help="hierarchy levels to group blocks by: 3 separates ppg, wallace1, "
                         "wallace2 and the product adder inside a stage")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tc = read_saif(a.saif, a.strip)
    if a.saif_base:
        base = read_saif(a.saif_base, a.strip)
        tc = {k: v - base.get(k, 0) for k, v in tc.items()}
        neg = sum(1 for v in tc.values() if v < 0)
        tc = {k: v for k, v in tc.items() if v > 0}
        print(f"# differenced against {a.saif_base}: {len(tc)} nets with activity, {neg} negative")
    cap = {}
    src = "none"
    if a.spef:
        nm = read_name_map(a.spef)
        raw = read_spef(a.spef)
        cap = {nm.get(k, k): v for k, v in raw.items()}
        src = "spef"
    elif a.netcap:
        with open(a.netcap) as fh:
            for line in fh:
                if line.startswith("#"):
                    continue
                p = line.split()
                if len(p) >= 3:
                    try:
                        cap[p[0]] = (float(p[1]) + float(p[2])) * 1e15   # F -> fF
                    except ValueError:
                        pass
        src = "netcap"

    clk = re.compile(a.clock_re)
    V2 = a.vdd * a.vdd
    tot = defaultdict(float)
    by_block = defaultdict(lambda: defaultdict(float))

    # The extractor's net list is the canonical one: walk IT, and ask the simulation for each
    # net's activity. A hierarchical simulation names the same physical wire once per level it
    # crosses, so walking the simulation instead double-counts every net that leaves a module.
    sim = {k.replace("\\", ""): v for k, v in tc.items()}

    def activity(net):
        """toggles of this extracted net, from the simulated netlist."""
        if net in sim:
            return sim[net], "direct"
        # Clock-tree-synthesis nets did not exist when the netlist was simulated: CTS made them.
        # They are named clknet_<numbers>_<source net>, so strip leading tokens until what is
        # left is a net the simulation knows - that is the gated clock this branch hangs off.
        if net.startswith("clknet_"):
            rest = net[len("clknet_"):]
            while rest:
                if rest in sim:
                    return sim[rest], "cts"
                if "_" not in rest:
                    break
                rest = rest.split("_", 1)[1]
        return None, "none"

    matched = unmatched = 0
    unmatched_tc = 0
    cts_nets = 0
    for net, c in cap.items():
        n, how = activity(net)
        if n is None:
            unmatched += 1
            continue
        if how == "cts":
            cts_nets += 1
        matched += 1
        if n == 0:
            continue
        e = 0.5 * c * 1e-15 * V2 * n      # J
        isclk = bool(clk.search(net))
        key = "clock" if isclk else "signal"
        tot[key + "_toggles"] += n
        tot[key + "_energy_J"] += e
        tot[key + "_cap_fF"] += c
        b = block_of(net, a.block_depth)
        by_block[b]["toggles"] += n
        by_block[b]["energy_J"] += e
        by_block[b]["cap_fF"] += c
        if isclk:
            by_block[b]["clock_toggles"] += n
            by_block[b]["clock_energy_J"] += e

    e_tot = tot["signal_energy_J"] + tot["clock_energy_J"]
    out = {
        "source": {"saif": a.saif, "cap": src, "vdd": a.vdd},
        "coverage": {"extracted_nets_found_in_sim": matched,
                     "extracted_nets_not_in_sim": unmatched,
                     "cts_nets_priced_from_their_source": cts_nets,
                     "extracted_nets": len(cap), "simulated_names": len(sim)},
        "total": {k: v for k, v in sorted(tot.items())},
        "energy_J": e_tot,
        "clock_share": (tot["clock_energy_J"] / e_tot) if e_tot else 0.0,
        "blocks": {b: dict(v) for b, v in sorted(by_block.items(),
                                                 key=lambda kv: -kv[1]["energy_J"])},
    }
    if a.muladds:
        out["per_muladd"] = {
            "toggles": (tot["signal_toggles"] + tot["clock_toggles"]) / a.muladds,
            "signal_toggles": tot["signal_toggles"] / a.muladds,
            "energy_J": e_tot / a.muladds,
            "energy_pJ": e_tot / a.muladds * 1e12,
        }
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ("coverage", "total", "energy_J", "clock_share")
                      if k in out}, indent=1))
    if "per_muladd" in out:
        print("per multiply-add:", json.dumps(out["per_muladd"], indent=1))


if __name__ == "__main__":
    main()
