#!/usr/bin/env python3
"""Q129(a): price one gate-level activity file against SEVERAL capacitance tables at once,
keeping the wire and the pin halves apart.

    reprice.py --saif <with-op.saif> --saif-base <without-op.saif> --strip tb/lane[0]/txfma
               --muladds 512 --vdd 0.517 [--cell-energies asap7-cell-energies.json]
               --caps gr=net_cap_globalroute.txt
               --caps spef_k0=spef_caps.txt:0 --caps spef_k1=spef_caps.txt:1
               --out reprice_randn.json

Why not just `power.py --spef`. Three reasons, all of which the Q128 ledger needs:

  1. **The wire half has to stay separate from the pin half.** `power.py` sums wire + pin into
     one C per net, and the ledger's waterfall splits a toggle's energy into transistor gates,
     wire inside the cells (both of which live in the liberty's PIN capacitance) and wire
     between the cells (the extractor's WIRE capacitance). Only the third one is re-priced by a
     detailed route, so the wire column has to be carried through on its own.
  2. **Coupling capacitance needs a stated Miller factor.** A `<table>:<k>` cap source is read
     as ground + k*coupling + pinload, so the same extraction gives k = 0, 1 and 2 in one pass.
  3. **One SAIF, many tables.** The SAIF parse is the expensive step; this walks it once.

The activity handling is `power.py`'s own, imported, not re-implemented: the same SAIF reader,
the same base-run differencing, and the same rule that walks the EXTRACTOR's net list and asks
the simulation for each net's toggles (so a hierarchical name is not double counted), with the
same `clknet_<n>_<source>` fallback for the nets CTS created after the netlist was simulated.
"""
import argparse
import importlib.util
import json
import os
import re
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_power():
    spec = importlib.util.spec_from_file_location("txfma_power", os.path.join(_HERE, "power.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


POWER = _load_power()


def read_caps(path, miller):
    """-> {net: (wire_F, pin_F)}. Two header shapes, told apart by the header comment:

    '# net wire_cap pin_cap'                 -> wire, pin                 (OpenSTA / pnr.tcl)
    '# net ground_F coupling_F pinload_F'    -> ground + k*coupling, pin  (spef_caps.py)
    """
    out = {}
    kind = "wirepin"
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                if "coupling" in line:
                    kind = "ground_coupling_pin"
                continue
            p = line.split()
            try:
                if kind == "ground_coupling_pin" and len(p) >= 4:
                    out[p[0]] = (float(p[1]) + miller * float(p[2]), float(p[3]))
                elif len(p) >= 3:
                    out[p[0]] = (float(p[1]), float(p[2]))
            except ValueError:
                continue
    return out, kind


def price(caps, sim, clk, vdd, block_depth):
    """power.py's accounting, with wire and pin kept apart. caps in farads."""
    V2 = vdd * vdd

    def activity(net):
        if net in sim:
            return sim[net], "direct"
        if net.startswith("clknet_"):
            rest = net[len("clknet_"):]
            while rest:
                if rest in sim:
                    return sim[rest], "cts"
                if "_" not in rest:
                    break
                rest = rest.split("_", 1)[1]
        return None, "none"

    tot = defaultdict(float)
    by_block = defaultdict(lambda: defaultdict(float))
    matched = unmatched = cts_nets = 0
    cap_all = cap_found = 0.0
    for net, (wc, pc) in caps.items():
        c = wc + pc
        cap_all += c
        n, how = activity(net)
        if n is None:
            unmatched += 1
            continue
        if how == "cts":
            cts_nets += 1
        matched += 1
        cap_found += c
        if n == 0:
            continue
        key = "clock" if clk.search(net) else "signal"
        tot[key + "_toggles"] += n
        tot[key + "_cap_F"] += c
        tot[key + "_wire_cap_F"] += wc
        tot[key + "_pin_cap_F"] += pc
        tot[key + "_energy_J"] += 0.5 * c * V2 * n
        tot[key + "_wire_energy_J"] += 0.5 * wc * V2 * n
        tot[key + "_pin_energy_J"] += 0.5 * pc * V2 * n
        b = POWER.block_of(net, block_depth)
        by_block[b]["toggles"] += n
        by_block[b]["energy_J"] += 0.5 * c * V2 * n
        by_block[b]["wire_energy_J"] += 0.5 * wc * V2 * n
    e_tot = tot["signal_energy_J"] + tot["clock_energy_J"]
    cap_priced = tot["signal_cap_F"] + tot["clock_cap_F"]
    return {
        "coverage": {"extracted_nets": len(caps),
                     "extracted_nets_found_in_sim": matched,
                     "extracted_nets_not_in_sim": unmatched,
                     "cts_nets_priced_from_their_source": cts_nets,
                     "cap_fF_extracted": cap_all * 1e15,
                     "cap_fF_found_in_sim": cap_found * 1e15,
                     "cap_fF_priced": cap_priced * 1e15,
                     "cap_fraction_priced": (cap_priced / cap_all) if cap_all else 0.0},
        "total": {k: v for k, v in sorted(tot.items())},
        "energy_J": e_tot,
        "wire_energy_J": tot["signal_wire_energy_J"] + tot["clock_wire_energy_J"],
        "pin_energy_J": tot["signal_pin_energy_J"] + tot["clock_pin_energy_J"],
        "clock_share": (tot["clock_energy_J"] / e_tot) if e_tot else 0.0,
        "blocks": {b: dict(v) for b, v in sorted(by_block.items(),
                                                 key=lambda kv: -kv[1]["energy_J"])},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saif", required=True)
    ap.add_argument("--saif-base")
    ap.add_argument("--caps", action="append", required=True,
                    help="<name>=<table>[:<miller>], repeatable")
    ap.add_argument("--strip", default="tb/lane[0]/txfma")
    ap.add_argument("--vdd", type=float, default=0.517)
    ap.add_argument("--muladds", type=float, default=0.0)
    ap.add_argument("--clock-re", default=r"(^|/)(clock|clk|CLK)(\[|$|/)|clknet|clkbuf")
    ap.add_argument("--block-depth", type=int, default=3)
    ap.add_argument("--cell-energies")
    ap.add_argument("--label", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tc = POWER.read_saif(a.saif, a.strip)
    if a.saif_base:
        base = POWER.read_saif(a.saif_base, a.strip)
        tc = {k: v - base.get(k, 0) for k, v in tc.items()}
        neg = sum(1 for v in tc.values() if v < 0)
        tc = {k: v for k, v in tc.items() if v > 0}
        print(f"# differenced: {len(tc)} nets with activity, {neg} negative")
    sim = {k.replace("\\", ""): v for k, v in tc.items()}
    clk = re.compile(a.clock_re)

    e_mix = None
    if a.cell_energies:
        with open(a.cell_energies) as fh:
            ce = json.load(fh)
        mix = ce["census_weighted_mix"]
        v_lib = float(ce["operating_point"]["VDD_liberty_V"])
        e_mix = float(mix["weighted_E_int_per_transition_VDDonly_fJ_0p7"]) * (a.vdd / v_lib) ** 2

    out = {"label": a.label, "saif": a.saif, "saif_base": a.saif_base, "vdd": a.vdd,
           "muladds": a.muladds, "simulated_names": len(sim), "variants": {}}
    for spec in a.caps:
        name, _, rest = spec.partition("=")
        table, _, mk = rest.partition(":")
        miller = float(mk) if mk else 1.0
        caps, kind = read_caps(table, miller)
        r = price(caps, sim, clk, a.vdd, a.block_depth)
        r["source"] = {"table": table, "kind": kind,
                       "miller": miller if kind == "ground_coupling_pin" else None}
        if a.muladds:
            r["per_muladd"] = {
                "toggles": (r["total"].get("signal_toggles", 0)
                            + r["total"].get("clock_toggles", 0)) / a.muladds,
                "signal_toggles": r["total"].get("signal_toggles", 0) / a.muladds,
                "energy_pJ": r["energy_J"] / a.muladds * 1e12,
                "wire_energy_pJ": r["wire_energy_J"] / a.muladds * 1e12,
                "pin_energy_pJ": r["pin_energy_J"] / a.muladds * 1e12,
                "clock_energy_pJ": r["total"].get("clock_energy_J", 0) / a.muladds * 1e12,
                "signal_energy_pJ": r["total"].get("signal_energy_J", 0) / a.muladds * 1e12,
            }
            if e_mix is not None:
                e_int = r["total"].get("signal_toggles", 0) * e_mix * 1e-15
                r["internal_estimate"] = {
                    "E_int_per_transition_fJ_at_vdd": e_mix,
                    "internal_J_signal_transitions": e_int,
                    "switching_plus_internal_J": r["energy_J"] + e_int,
                }
                r["per_muladd"]["switching_plus_internal_pJ"] = \
                    (r["energy_J"] + e_int) / a.muladds * 1e12
        out["variants"][name] = r
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)
    for name, r in out["variants"].items():
        pm = r.get("per_muladd", {})
        print("%-12s priced %.4f of farads  %8.4f pJ/MAC  wire %8.4f  pin %8.4f  clk %.1f%%"
              % (name, r["coverage"]["cap_fraction_priced"], pm.get("energy_pJ", 0),
                 pm.get("wire_energy_pJ", 0), pm.get("pin_energy_pJ", 0),
                 100 * r["clock_share"]))


if __name__ == "__main__":
    main()
