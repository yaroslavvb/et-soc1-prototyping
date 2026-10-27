#!/usr/bin/env python3.12
"""Q126(d) part 1 -- price one transistor flip, by cell, from ASAP7's open liberty.

Reads the ASAP7 7.5-track RVT typical-corner NLDM liberty files (BSD-3-Clause,
Clark et al. 2016) and tabulates, for the cells the ET-SoC-1's multiply-add is
built from: input pin capacitance, internal energy per output transition,
leakage, and the energy per transition at 0.7 V and at the minion's 0.517 V.

Usage:  python3.12 -I asap7_cell_energies.py <libdir> <outdir>

<libdir> holds the six *_RVT_TT_nldm_*.lib files unpacked from
asap7sc7p5t_28/LIB/NLDM/*.7z.  Nothing is written outside <outdir>.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import libparse as L                                            # noqa: E402

# ---------------------------------------------------------------- constants
VDD_LIB = 0.7          # V, the liberty's nom_voltage
VDD_MIN = 0.517        # V, the ET-SoC-1 minion rail at 600 MHz
VSCALE = (VDD_MIN / VDD_LIB) ** 2          # 0.5454
SLEW = 10.0            # ps  -- the stated input slew
CLOAD = 2.0            # fF  -- the stated output load
LOAD_SWEEP = [0.5, 1.0, 2.0, 4.0, 8.0]     # fF, for the "by load" column

# cell -> (liberty group file key, what it is)
CELLS = [
    ("INVx1",     "INVBUF", "inverter, minimum drive"),
    ("INVxp33",   "INVBUF", "inverter, 1/3 drive (the smallest)"),
    ("BUFx2",     "INVBUF", "buffer (two inverters)"),
    ("NAND2xp33", "SIMPLE", "2-input NAND, 1/3 drive"),
    ("NOR2xp33",  "SIMPLE", "2-input NOR, 1/3 drive"),
    ("AOI21xp33", "AO",     "AND-OR-invert 2+1, 1/3 drive"),
    ("OAI21xp33", "OA",     "OR-AND-invert 2+1, 1/3 drive"),
    ("NAND2x1",   "SIMPLE", "2-input NAND"),
    ("NOR2x1",    "SIMPLE", "2-input NOR"),
    ("XOR2x1",    "SIMPLE", "2-input XOR"),
    ("XNOR2x1",   "SIMPLE", "2-input XNOR"),
    ("XOR2xp5",   "SIMPLE", "2-input XOR, half drive"),
    ("XNOR2xp5",  "SIMPLE", "2-input XNOR, half drive"),
    ("AOI21x1",   "AO",     "AND-OR-invert, 2+1"),
    ("OAI21x1",   "OA",     "OR-AND-invert, 2+1"),
    ("MAJIxp5",   "SIMPLE", "majority gate, inverting (the 4:2 compressor's carry)"),
    ("MAJx2",     "SIMPLE", "majority gate, non-inverting"),
    ("HAxp5",     "SIMPLE", "half adder"),
    ("FAx1",      "SIMPLE", "full adder (28-transistor mirror type)"),
    ("DFFHQNx1",  "SEQ",    "D flip-flop, inverting output"),
    ("ICGx1",     "SEQ",    "integrated clock gate"),
]

FILES = {
    "INVBUF": "asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib",
    "SIMPLE": "asap7sc7p5t_SIMPLE_RVT_TT_nldm_211120.lib",
    "AO":     "asap7sc7p5t_AO_RVT_TT_nldm_211120.lib",
    "OA":     "asap7sc7p5t_OA_RVT_TT_nldm_211120.lib",
    "SEQ":    "asap7sc7p5t_SEQ_RVT_TT_nldm_220123.lib",
}
SUFFIX = "_ASAP7_75t_R"

# ASAP7 paper, Clark et al., Microelectronics Journal 53 (2016) 105-115,
# Tables 3 and 4 -- typical corner, per fin, 25 C, VDD = 0.7 V.
ASAP7_DEVICES = {
    "citation": ("L.T. Clark, V. Vashishtha, L. Shifren, A. Gujja, S. Sinha, "
                 "B. Cline, C. Ramamurthy, G. Yeric, \"ASAP7: A 7-nm finFET "
                 "predictive process design kit\", Microelectronics Journal 53 "
                 "(2016) 105-115, doi:10.1016/j.mejo.2016.04.006 (open access, "
                 "CC BY-NC-ND). Shipped with the kit as "
                 "asap7_pdk_r1p7/docs/mej_paper_asap7.pdf."),
    "corner": "typical (TT), per fin, 25 C, VDD = 0.7 V",
    "nmos": {  # Table 3
        "Idsat_uA":   {"SRAM": 28.57, "RVT": 37.85, "LVT": 45.19, "SLVT": 50.79},
        "Ieff_uA":    {"SRAM": 13.07, "RVT": 18.13, "LVT": 23.56, "SLVT": 28.67},
        "Ioff_nA":    {"SRAM": 0.001, "RVT": 0.019, "LVT": 0.242, "SLVT": 2.444},
        "Vtsat_V":    {"SRAM": 0.25,  "RVT": 0.17,  "LVT": 0.10,  "SLVT": 0.04},
        "Vtlin_V":    {"SRAM": 0.27,  "RVT": 0.19,  "LVT": 0.12,  "SLVT": 0.06},
        "SS_mV_dec":  {"SRAM": 62.44, "RVT": 63.03, "LVT": 62.90, "SLVT": 63.33},
        "DIBL_mV_V":  {"SRAM": 19.23, "RVT": 21.31, "LVT": 22.32, "SLVT": 22.55},
    },
    "pmos": {  # Table 4, magnitudes as printed
        "Idsat_uA":   {"SRAM": 26.90, "RVT": 32.88, "LVT": 39.88, "SLVT": 45.60},
        "Ieff_uA":    {"SRAM": 11.37, "RVT": 14.08, "LVT": 18.18, "SLVT": 22.64},
        "Ioff_nA":    {"SRAM": 0.004, "RVT": 0.023, "LVT": 0.230, "SLVT": 2.410},
        "Vtsat_V":    {"SRAM": -0.20, "RVT": -0.16, "LVT": -0.10, "SLVT": -0.04},
        "Vtlin_V":    {"SRAM": -0.22, "RVT": -0.19, "LVT": -0.13, "SLVT": -0.07},
        "SS_mV_dec":  {"SRAM": 64.34, "RVT": 64.48, "LVT": 64.44, "SLVT": 64.94},
        "DIBL_mV_V":  {"SRAM": 24.10, "RVT": 30.36, "LVT": 31.06, "SLVT": 31.76},
    },
    "geometry": {
        "CPP_nm": 54, "fin_pitch_nm": 27, "M1_M3_pitch_nm": 36,
        "fin_width_nm_actual": 6.5, "fin_width_nm_drawn": 7,
        "fin_height_nm": 32, "gate_length_nm_actual": 21,
        "gate_length_nm_drawn": 20, "cell_track_height": 7.5,
        "note": ("Section 3.1, 4.1 and Table 1 of the paper. The standard-cell "
                 "row is 7.5 M2 tracks of 36 nm = 270 nm."),
    },
    "gate_leakage": {
        "value": None,
        "note": ("The paper gives no gate-leakage number; it states only that "
                 "the BSIM-CMG cards enable it (igcmod = 1, in "
                 "models/hspice/7nm_TT_160803.pm). Table 3/4's Ioff is the "
                 "drain current at Vgs = 0, not gate leakage. Getting a gate-"
                 "leakage figure needs a SPICE sweep (part 2)."),
    },
    "fo4_note": ("The paper prints no FO4 delay. The FO4 in this file is "
                 "computed from the liberty itself, self-consistently: an "
                 "INVx1 driving four INVx1 input pins, input slew iterated "
                 "until it equals the output slew."),
}

# ---- the Q124 census this table is set beside -------------------------------
# docs/reports/data/2026-09-27-chip-diagram/research/tensorfma32.json
Q124 = {
    "source": "docs/reports/data/2026-09-27-chip-diagram/research/tensorfma32.json",
    "tfma.flip.gate": {
        "wires_total": 381, "f1": 129, "f1_flops": 19, "f2": 252, "f2_flops": 16,
        "case": "b bit 11 flipped, a = pi (the lab's E60 case)",
    },
    "tfma.flip.energy": {"pJ_low": 0.11, "pJ_high": 0.13,
                         "basis": "the real cells' energies, interpolated to 0.517 V"},
    "tfma.glitch": {"toggle_ratio": 1.5, "energy_ratio": 1.4},
    "tfma.clocked": {"flops_clocked_random": 1586, "flops_total": 1851,
                     "flops_clocked_zero": 15},
    "tfma.asbuilt.cells": {"cells": 4487, "transistors": 49755,
                           "full_adders": 248, "fa_mirror": 162, "fa_tg": 86},
}
E60 = {"board_fJ": [116.7, 129.9], "rail_fJ": [87.5, 96.9],
       "what": "E60's measured cost of one flipped mantissa bit per multiply-add"}


# ---------------------------------------------------------------- extraction
def pg_detail(groups, which, slew, load):
    """An internal_power event, split by related_pg_pin.

    ASAP7 characterises each event against both rails: INVx1's output rise is
    +0.120 fJ on VDD and -0.028 fJ on VSS.  Two readings are in use and they
    differ by about 2x, so both are carried:
      'vdd'  -- the VDD group alone, which is what a rail sensor would see;
      'sum'  -- VDD + VSS, the total internal energy a power tool reports.
    Part 2 settles which matches SPICE on the real cell netlist.
    """
    out = {"vdd": None, "vss": None, "sum": None}
    tot, seen = 0.0, False
    for g in groups:
        t = g.one(which)
        if t is None:
            continue
        i1, i2, rows = L.table(t)
        v = L.interp(i1, i2, rows, slew, load)
        if v is None:
            continue
        key = "vdd" if L.attr1(g, "related_pg_pin") == "VDD" else "vss"
        out[key] = (out[key] or 0.0) + v
        tot += v
        seen = True
    out["sum"] = tot if seen else None
    return out


def pg_sum(groups, which, slew, load):
    return pg_detail(groups, which, slew, load)["sum"]


def cell_record(lib, base, blurb, slew=SLEW, load=CLOAD):
    cell = lib.one("cell", base + SUFFIX)
    if cell is None:
        return None
    rec = {"cell": base + SUFFIX, "what": blurb,
           "area_um2": L.attr1(cell, "area", float),
           "inputs": {}, "arcs": {}, "clock_pin_energy": {}}

    # leakage: the unconditioned (state-averaged) VDD entry, in pW
    for lp in cell.find("leakage_power"):
        if L.attr1(lp, "when") is None and L.attr1(lp, "related_pg_pin") == "VDD":
            rec["leakage_pW"] = L.attr1(lp, "value", float)
    states = [(L.attr1(lp, "when"), L.attr1(lp, "value", float))
              for lp in cell.find("leakage_power")
              if L.attr1(lp, "when") and L.attr1(lp, "related_pg_pin") == "VDD"]
    if states:
        rec["leakage_by_state_pW"] = dict(states)

    for pin in cell.find("pin"):
        direction = L.attr1(pin, "direction")
        if direction == "input":
            rec["inputs"][pin.name] = {
                "cap_fF": L.attr1(pin, "capacitance", float),
                "rise_cap_fF": L.attr1(pin, "rise_capacitance", float),
                "fall_cap_fF": L.attr1(pin, "fall_capacitance", float),
                "is_clock": L.attr1(pin, "clock") == "true",
            }
            # a sequential cell carries the clock-pin energy on the clock pin
            ips = pin.find("internal_power")
            if ips:
                by_when = {}
                for ip in ips:
                    key = L.attr1(ip, "when") or "(any)"
                    by_when.setdefault(key, []).append(ip)
                ev = {}
                for key, grp in by_when.items():
                    dr = pg_detail(grp, "rise_power", slew, load)
                    df = pg_detail(grp, "fall_power", slew, load)
                    ev[key] = {
                        "rise_fJ": dr["sum"], "fall_fJ": df["sum"],
                        "per_clock_cycle_fJ": (dr["sum"] or 0.0) + (df["sum"] or 0.0),
                        "per_clock_cycle_VDDonly_fJ": (dr["vdd"] or 0.0) + (df["vdd"] or 0.0),
                    }
                vals = [v["per_clock_cycle_fJ"] for v in ev.values()]
                vv = [v["per_clock_cycle_VDDonly_fJ"] for v in ev.values()]
                rec["clock_pin_energy"][pin.name] = {
                    "by_state": ev,
                    "mean_per_cycle_fJ": sum(vals) / len(vals),
                    "mean_per_cycle_VDDonly_fJ": sum(vv) / len(vv),
                }
        elif direction == "output":
            for ip in pin.find("internal_power"):
                rel = L.attr1(ip, "related_pin")
                if rel is None:
                    continue
                for r in rel.split():
                    key = f"{r}->{pin.name}"
                    rec["arcs"].setdefault(key, {"groups": []})["groups"].append(ip)

    # collapse the arc groups into numbers
    arcs = {}
    for key, d in rec["arcs"].items():
        grp = d["groups"]
        dr = pg_detail(grp, "rise_power", slew, load)
        df = pg_detail(grp, "fall_power", slew, load)
        er, ef = dr["sum"], df["sum"]
        if er is None and ef is None:
            continue
        er, ef = er or 0.0, ef or 0.0
        mean = 0.5 * (er + ef)
        vr, vf = dr["vdd"] or 0.0, df["vdd"] or 0.0
        arcs[key] = {
            "E_int_rise_fJ": er, "E_int_fall_fJ": ef, "E_int_mean_fJ": mean,
            "E_int_per_cycle_fJ": er + ef,
            "E_int_rise_VDDonly_fJ": vr, "E_int_fall_VDDonly_fJ": vf,
            "E_int_mean_VDDonly_fJ": 0.5 * (vr + vf),
            "E_int_per_cycle_VDDonly_fJ": vr + vf,
            "by_load_fJ": {
                f"{c}": {
                    "E_int_mean_fJ": 0.5 * ((pg_sum(grp, "rise_power", slew, c) or 0.0)
                                            + (pg_sum(grp, "fall_power", slew, c) or 0.0)),
                    "E_transition_0p7_fJ": 0.5 * ((pg_sum(grp, "rise_power", slew, c) or 0.0)
                                                  + (pg_sum(grp, "fall_power", slew, c) or 0.0))
                    + 0.5 * c * VDD_LIB ** 2,
                } for c in LOAD_SWEEP},
            "E_transition_0p7_fJ": mean + 0.5 * load * VDD_LIB ** 2,
            "E_transition_0p517_fJ": (mean + 0.5 * load * VDD_LIB ** 2) * VSCALE,
        }
    rec["arcs"] = arcs
    rec["E_int_mean_over_arcs_fJ"] = (
        sum(a["E_int_mean_fJ"] for a in arcs.values()) / len(arcs)) if arcs else None
    rec["E_int_mean_over_arcs_VDDonly_fJ"] = (
        sum(a["E_int_mean_VDDonly_fJ"] for a in arcs.values()) / len(arcs)) if arcs else None
    return rec


def fo4(lib, suffix=SUFFIX):
    """INVx1 driving four INVx1 inputs, slew iterated to self-consistency."""
    cell = lib.one("cell", "INVx1" + suffix)
    cin = L.attr1(cell.one("pin", "A"), "capacitance", float)
    load = 4 * cin
    y = cell.one("pin", "Y")
    tim = y.one("timing")
    tabs = {k: L.table(tim.one(k))
            for k in ("cell_rise", "cell_fall", "rise_transition", "fall_transition")}
    slew = 10.0
    for _ in range(60):
        tr = L.interp(*tabs["rise_transition"], slew, load)
        tf = L.interp(*tabs["fall_transition"], slew, load)
        new = 0.5 * (tr + tf)
        if abs(new - slew) < 1e-9:
            break
        slew = new
    dr = L.interp(*tabs["cell_rise"], slew, load)
    df = L.interp(*tabs["cell_fall"], slew, load)
    return {"input_cap_fF": cin, "load_fF": load, "self_consistent_slew_ps": slew,
            "delay_rise_ps": dr, "delay_fall_ps": df, "FO4_ps": 0.5 * (dr + df),
            "note": ("Delay is 50%-to-50%; the liberty's slew is 10-90% with "
                     "slew_derate_from_library = 1. TT, 0.7 V, 25 C. The input "
                     "slew is iterated until it equals the stage's own output "
                     "slew, which is what a chain of these cells settles at.")}


# ------------------------------------------------- the flow-M flip estimate
def flip_estimate(recs, census=None):
    """Price Q124's 381-wire flow-M flip from ASAP7 alone.

    Q124 counted 381 physical wires toggling for 'b bit 11, a = pi' in a
    gate-level, zero-delay run of lane 0: 129 in f1 (19 of them flip-flop
    outputs) and 252 in f2 (16 of them the product register's).  Here each
    toggling wire is priced as one cell-output transition out of ASAP7's
    liberty, at the minion's 0.517 V.
    """
    flops = Q124["tfma.flip.gate"]["f1_flops"] + Q124["tfma.flip.gate"]["f2_flops"]
    comb = Q124["tfma.flip.gate"]["wires_total"] - flops

    # two cell mixes: the x1 drives, and the minimum drives a dense
    # synthesized tree actually fills up with
    MIXES = {
        "x1_drive": ["INVx1", "NAND2x1", "NOR2x1", "XOR2x1", "XNOR2x1",
                     "AOI21x1", "OAI21x1", "MAJIxp5"],
        "min_drive": ["INVxp33", "NAND2xp33", "NOR2xp33", "XOR2xp5",
                      "XNOR2xp5", "AOI21xp33", "OAI21xp33", "MAJIxp5"],
    }
    # the flip-flop's data-switching energy only: the clock runs on every
    # multiply-add either way (tfma.clocked), so the clock pin is not marginal
    ff_arc = next(iter(recs["DFFHQNx1"]["arcs"].values()))

    out = {"method": flip_estimate.__doc__.strip(),
           "wires": {"total": Q124["tfma.flip.gate"]["wires_total"],
                     "combinational": comb, "flip_flop_outputs": flops},
           "mixes": {}, "headline": {}}

    for conv, fld, ffld, cfld in (
            ("sum", "E_int_mean_over_arcs_fJ", "E_int_mean_fJ",
             "weighted_E_int_mean_fJ_0p7"),
            ("vdd_only", "E_int_mean_over_arcs_VDDonly_fJ",
             "E_int_mean_VDDonly_fJ", "weighted_E_int_mean_VDDonly_fJ_0p7")):
        e_ff_int = ff_arc[ffld]
        cases = [(m, {n: recs[n][fld] for n in names if n in recs}, None)
                 for m, names in MIXES.items()]
        if census and census.get(cfld):
            cases.append(("census", None, census[cfld]))
        for mix, pool, forced in cases:
            if forced is not None:
                e_mean = forced
                lo = hi = forced
                pool = {"(Q126(e) census-weighted)": forced}
            else:
                e_mean = sum(pool.values()) / len(pool)
                lo, hi = min(pool.values()), max(pool.values())
            rec = {"cell_pool_fJ_0p7": pool, "E_int_mean_fJ_0p7": e_mean,
                   "E_int_flop_fJ_0p7": e_ff_int, "loads_fF": {}}
            for cl in (1.0, 2.0, 4.0):
                e_load = 0.5 * cl * VDD_MIN ** 2                 # fJ at 0.517 V
                e_comb = (e_mean * VSCALE + e_load) * comb
                e_ff = (e_ff_int * VSCALE + e_load) * flops
                rec["loads_fF"][f"{cl}"] = {
                    "E_per_comb_net_fJ": e_mean * VSCALE + e_load,
                    "E_comb_total_fJ": e_comb, "E_flop_total_fJ": e_ff,
                    "E_flip_total_fJ": e_comb + e_ff,
                    "E_flip_total_pJ": (e_comb + e_ff) / 1000.0,
                }
            e_load2 = 0.5 * 2.0 * VDD_MIN ** 2
            rec["cell_spread_at_2fF_pJ"] = [
                ((x * VSCALE + e_load2) * comb
                 + (e_ff_int * VSCALE + e_load2) * flops) / 1000.0
                for x in (lo, hi)]
            rec["load_band_1_to_4fF_pJ"] = [
                rec["loads_fF"]["1.0"]["E_flip_total_pJ"],
                rec["loads_fF"]["4.0"]["E_flip_total_pJ"]]
            out["mixes"][f"{conv}/{mix}"] = rec

    allv = [r["loads_fF"][c]["E_flip_total_pJ"]
            for r in out["mixes"].values() for c in ("1.0", "2.0", "4.0")]
    best = ("vdd_only/census" if "vdd_only/census" in out["mixes"]
            else "vdd_only/min_drive")
    out["headline"] = {
        "full_range_pJ": [min(allv), max(allv)],
        "central_key": best,
        "central_pJ": out["mixes"][best]["loads_fF"]["2.0"]["E_flip_total_pJ"],
        "central_band_1_to_4fF_pJ": out["mixes"][best]["load_band_1_to_4fF_pJ"],
        "central_what": ("VDD-only internal energy (the convention SPICE "
                         "confirms in part 2), the cell mix Q126(e) measured "
                         "for this unit, 2 fF per net"),
        "q124_pJ": [Q124["tfma.flip.energy"]["pJ_low"],
                    Q124["tfma.flip.energy"]["pJ_high"]],
        "e60_rail_fJ": E60["rail_fJ"], "e60_board_fJ": E60["board_fJ"],
    }
    out["assumptions"] = [
        "One toggling physical wire = one cell-output transition.",
        ("The combinational cell mix is the unweighted mean of a pool of "
         "ASAP7 cells -- the gate kinds Q124's census names in the Booth "
         "rows, the Wallace tree and the product adder (tfma.asbuilt.cells, "
         "tfma.benc, tfma.cmp42). Two pools are carried: the x1 drives and "
         "the minimum drives (xp33/xp5) a dense synthesized tree fills up "
         "with. The real mix is not in the public data, so the min-to-max "
         "spread over each pool is carried too."),
        ("Internal energy is reported both ways -- VDD+VSS summed, and the "
         "VDD group alone. They differ by about 2x and part 2 settles which "
         "matches SPICE on the real netlist."),
        ("Load per net = pin capacitance of what it drives plus its wire. "
         "ASAP7's own input pins are 0.62 fF (INVx1) to about 2 fF (FAx1); "
         "wire inside a 30 um tree level at 0.2 fF/um is roughly 0.5-1.5 fF. "
         "1, 2 and 4 fF bracket it; 2 fF is the headline."),
        ("Flip-flops: the data-switching (QN) arc only. The clock reaches "
         "1,586 of 1,851 flops on every multiply-add either way "
         "(tfma.clocked), so the clock-pin energy is not marginal to a flip."),
        ("Zero-delay, like Q124's count: no glitches. tfma.glitch puts the "
         "timed tree at 1.5x the toggles and 1.4x the energy."),
        ("Internal energy is scaled from 0.7 V by (0.517/0.7)^2 = 0.5454. "
         "That is exact for the capacitive part and optimistic for the "
         "short-circuit part, which falls faster than V^2."),
        ("ASAP7 is a predictive 7 nm PDK, not TSMC N7, and the ET-SoC-1's "
         "cells are not these cells. This is an order-of-magnitude check."),
    ]
    return out


# ---------------------------------------------------------------------- main
def census_mix(libs, census_path, slew=SLEW, load=CLOAD):
    """Weight the cell prices by the cell mix Q126(e) measured.

    Q126(e) synthesized core-et's txfma_top (the same multiply-add) onto this
    very library with Yosys and counted every cell type.  That histogram is a
    far better basis for 'what a toggling net costs here' than an unweighted
    pool, so it is used for the headline estimate.
    """
    with open(census_path) as fh:
        cen = json.load(fh)
    counts = cen["by_cell_type"]
    index = {}
    for lib in libs.values():
        for c in lib.find("cell"):
            index[c.name] = lib
    seq_or_tie = ("DFF", "DLL", "DHL", "SDF", "ICG", "TIEHI", "TIELO")
    priced, missing, skipped = {}, [], {}
    tot_n = tot_e = tot_evdd = 0
    for name, n in counts.items():
        base = name.split("_ASAP7")[0]
        if base.startswith(seq_or_tie):
            skipped[name] = n
            continue
        lib = index.get(name)
        if lib is None:
            missing.append(name)
            continue
        r = cell_record(lib, base, "", slew, load)
        if not r or not r["arcs"]:
            missing.append(name)
            continue
        e = r["E_int_mean_over_arcs_fJ"]
        ev = r["E_int_mean_over_arcs_VDDonly_fJ"]
        priced[name] = {"count": n, "E_int_mean_fJ": e,
                        "E_int_mean_VDDonly_fJ": ev,
                        "leakage_pW": r.get("leakage_pW")}
        tot_n += n
        tot_e += n * e
        tot_evdd += n * ev
    return {
        "source": ("docs/reports/data/2026-10-26-open-netlist/census_flat.json "
                   "(Q126(e), same day): core-et's txfma_top synthesized onto "
                   "ASAP7 RVT with Yosys, 16,087 cells flattened."),
        "combinational_cells_priced": tot_n,
        "cell_types_priced": len(priced),
        "cell_types_missing": missing,
        "sequential_and_tie_cells_skipped": skipped,
        "weighted_E_int_mean_fJ_0p7": tot_e / tot_n if tot_n else None,
        "weighted_E_int_mean_VDDonly_fJ_0p7": tot_evdd / tot_n if tot_n else None,
        "by_cell": priced,
        "caveat": ("The open synthesis made 7,967 cells for the multiplier "
                   "against the tape-out flow's 4,487, so this is the mix of "
                   "a different netlist of the same RTL, not of the silicon. "
                   "It is used as the mix, not as the count."),
    }


def main():
    libdir, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    libs = {}
    for key, fn in FILES.items():
        libs[key] = L.parse(os.path.join(libdir, fn)).one("library")

    recs = {}
    for base, key, blurb in CELLS:
        r = cell_record(libs[key], base, blurb)
        if r is None:
            print("MISSING", base, file=sys.stderr)
            continue
        r["liberty_file"] = FILES[key]
        recs[base] = r

    out = {
        "what": ("ASAP7 cell energies: the price of one transistor flip, by kind "
                 "of gate, from open data. AI Foundry request Q126(d), "
                 "Mon 26 Oct 2026 (week 44)."),
        "kit": {
            "name": "ASAP7 7.5-track predictive 7 nm PDK and standard cell library",
            "licence": "BSD 3-Clause",
            "repos": ["github.com/The-OpenROAD-Project/asap7sc7p5t_28",
                      "github.com/The-OpenROAD-Project/asap7_pdk_r1p7"],
            "corner": "RVT, TT (typical), NLDM, 0.7 V, 25 C",
            "liberty_files": sorted(set(FILES.values())),
            "units": {"capacitance": "fF", "time": "ps", "leakage": "pW",
                      "energy": ("fJ -- the liberty's derived power unit is "
                                 "voltage_unit x current_unit x time_unit = "
                                 "1 V x 1 mA x 1 ps = 1 fJ")},
        },
        "operating_point": {
            "input_slew_ps": SLEW, "output_load_fF": CLOAD,
            "VDD_liberty_V": VDD_LIB, "VDD_minion_V": VDD_MIN,
            "V2_scale_0p517_over_0p7": VSCALE,
        },
        "conventions": {
            "internal_energy": ("An internal_power event is summed over its "
                                "related_pg_pin groups (VDD and VSS), which is "
                                "what a power tool does for total internal "
                                "energy. ASAP7 splits each event between the "
                                "two rails with a negative cross term: INVx1's "
                                "output rise is +0.120 fJ on VDD and -0.028 fJ "
                                "on VSS. rise/fall is the OUTPUT pin's "
                                "direction."),
            "E_transition": ("E_int_mean + 1/2 C_load V^2, the task's formula: "
                             "the energy DISSIPATED per output transition, "
                             "averaged over a rise and a fall. Over a full "
                             "cycle the load dissipates C_load V^2 in all."),
            "drawing_scale": ("ASAP7's layout is drawn at 4x: every length in "
                              "the GDS, the LEF and the QRC techfile is four "
                              "times the real dimension (the kit is drawn on a "
                              "relaxed 1 nm grid so commercial tools can hold "
                              "it). THE LIBERTY IS NOT SCALED: the "
                              "capacitances, energies, delays and leakages "
                              "here are real-world 7 nm values and need no 4x "
                              "correction. Only lengths and anything derived "
                              "from the LEF or QRC do."),
            "leakage": ("Leakage is the state-averaged VDD entry at 0.7 V and "
                        "25 C, in pW. It is NOT scaled to 0.517 V: leakage "
                        "falls with voltage through DIBL and the subthreshold "
                        "slope, not as V^2."),
        },
        "fo4_from_liberty": fo4(libs["INVBUF"]),
        "fo4_by_vt": {},
        "asap7_devices": ASAP7_DEVICES,
        "cells": recs,
        "q124_census": Q124,
        "e60_measured": E60,
    }
    # FO4 for every threshold flavour, so the number can be checked against
    # any quoted figure
    vtdir = sys.argv[3] if len(sys.argv) > 3 else None
    if vtdir and os.path.isdir(vtdir):
        for vt, fn, sfx in (
                ("RVT",  "asap7sc7p5t_INVBUF_RVT_TT_nldm_220122.lib",  "_ASAP7_75t_R"),
                ("LVT",  "asap7sc7p5t_INVBUF_LVT_TT_nldm_220122.lib",  "_ASAP7_75t_L"),
                ("SLVT", "asap7sc7p5t_INVBUF_SLVT_TT_nldm_220122.lib", "_ASAP7_75t_SL"),
                ("SRAM", "asap7sc7p5t_INVBUF_SRAM_TT_nldm_220122.lib", "_ASAP7_75t_SRAM")):
            p = os.path.join(vtdir, fn)
            if os.path.exists(p):
                out["fo4_by_vt"][vt] = fo4(L.parse(p).one("library"), sfx)
        out["fo4_by_vt"]["note"] = (
            "The brief for this request quoted 'about 8.1 ps RVT at 0.7 V' as "
            "the kit's FO4. The kit's own liberty does not give that: see the "
            "numbers above. The SPICE run in part 2 is checked against these.")

    census = sys.argv[4] if len(sys.argv) > 4 else None
    cm = census_mix(libs, census) if census and os.path.exists(census) else None
    if cm:
        out["census_weighted_mix"] = cm
    out["flow_m_flip_estimate"] = flip_estimate(recs, cm)

    # Vtn + |Vtp| against the minion rail
    vtn = ASAP7_DEVICES["nmos"]["Vtsat_V"]["RVT"]
    vtp = abs(ASAP7_DEVICES["pmos"]["Vtsat_V"]["RVT"])
    vtnl = ASAP7_DEVICES["nmos"]["Vtlin_V"]["RVT"]
    vtpl = abs(ASAP7_DEVICES["pmos"]["Vtlin_V"]["RVT"])
    out["short_circuit_window"] = {
        "Vtn_sat_V": vtn, "Vtp_sat_V": vtp, "sum_sat_V": vtn + vtp,
        "Vtn_lin_V": vtnl, "Vtp_lin_V": vtpl, "sum_lin_V": vtnl + vtpl,
        "VDD_minion_V": VDD_MIN,
        "verdict": ("0.517 V is ABOVE Vtn + |Vtp| for ASAP7 RVT, by "
                    f"{VDD_MIN - (vtn + vtp):.3f} V on the saturation "
                    f"thresholds and {VDD_MIN - (vtnl + vtpl):.3f} V on the "
                    "linear ones. So the short-circuit path does NOT close at "
                    "the minion's rail: both devices can conduct during an "
                    "input edge. The 20 Oct plan's hope that it might vanish "
                    "at 0.517 V is wrong for these devices. How much energy "
                    "that costs against edge time is part 2."),
    }

    with open(os.path.join(outdir, "asap7-cell-energies.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print("wrote", os.path.join(outdir, "asap7-cell-energies.json"))

    # ------------------------------------------------------------- markdown
    rows = []
    for base, _k, blurb in CELLS:
        r = recs.get(base)
        if not r:
            continue
        ins = {n: v["cap_fF"] for n, v in r["inputs"].items()}
        capstr = ", ".join(f"{n} {v:.3f}" for n, v in sorted(ins.items()) if v)
        arcs = r["arcs"]
        if arcs:
            mean = r["E_int_mean_over_arcs_fJ"]
            mvdd = r["E_int_mean_over_arcs_VDDonly_fJ"]
            etr = mean + 0.5 * CLOAD * VDD_LIB ** 2
            rows.append((base, blurb, capstr, r.get("leakage_pW"),
                         mean, mvdd, etr, etr * VSCALE))
    lines = ["| cell | what | input pin cap (fF) | leakage (pW) | internal E/transition, VDD+VSS (fJ) | internal E/transition, VDD only (fJ) | E/transition @0.7 V (fJ) | @0.517 V (fJ) |",
             "|---|---|---|---:|---:|---:|---:|---:|"]
    for base, blurb, capstr, lk, mean, mvdd, etr, e517 in rows:
        lines.append(f"| {base} | {blurb} | {capstr} | {lk:.1f} | {mean:.4f} | "
                     f"{mvdd:.4f} | {etr:.4f} | {e517:.4f} |")
    with open(os.path.join(outdir, "table.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))

    fe = out["flow_m_flip_estimate"]
    print()
    for vt, d in out["fo4_by_vt"].items():
        if isinstance(d, dict):
            print(f"FO4 {vt:5s}: {d['FO4_ps']:6.2f} ps "
                  f"(load {d['load_fF']:.2f} fF, slew {d['self_consistent_slew_ps']:.1f} ps)")
    print()
    print("flow-M flip (381 wires), pJ at 0.517 V:")
    for k, r in fe["mixes"].items():
        print(f"  {k:22s} 1 fF {r['loads_fF']['1.0']['E_flip_total_pJ']:.3f}  "
              f"2 fF {r['loads_fF']['2.0']['E_flip_total_pJ']:.3f}  "
              f"4 fF {r['loads_fF']['4.0']['E_flip_total_pJ']:.3f}")
    print("  full range", [round(x, 3) for x in fe["headline"]["full_range_pJ"]],
          "| Q124", fe["headline"]["q124_pJ"],
          "| E60 rail", [x / 1000 for x in E60["rail_fJ"]],
          "board", [x / 1000 for x in E60["board_fJ"]], "pJ")
    print("short circuit: Vtn+|Vtp| =",
          out["short_circuit_window"]["sum_sat_V"], "V vs VDD", VDD_MIN, "V")


if __name__ == "__main__":
    main()
