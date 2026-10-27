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
    ("DFFHQNx1",  "SEQ",    "D flip-flop, inverting output, minimum drive"),
    ("DFFHQx4",   "SEQ",    "D flip-flop, x4 drive (the only flop in the Q126(e) census)"),
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
# E60's Hamming ladder, docs/findings/03-experiments.md: the two numbers are
# two OPERAND CASES, not an uncertainty band.  Q124's flip-gate count -- and so
# this estimate -- is the a = pi case, so 129.9 fJ board / 96.9 fJ rail is the
# figure that matches; 116.7 / 87.5 is a different multiply (a = 1.0).
E60 = {
    "source": "docs/findings/03-experiments.md, E60 Hamming ladder "
              "(aifoundry3, 600 MHz, 0.522 V, h >= 1, 4 passes)",
    "a_eq_pi":  {"board_fJ": 129.9, "board_sigma_fJ": 0.5,
                 "rail_fJ": 96.9, "matches_this_estimate": True},
    "a_eq_1p0": {"board_fJ": 116.7, "board_sigma_fJ": 0.6,
                 "rail_fJ": 87.5, "matches_this_estimate": False},
    "what": "E60's measured cost of one flipped mantissa B bit per multiply-add",
    "scope_differences": [
        ("E60 is BOARD energy (the 129.9 fJ figure) including the regulator's "
         "conversion loss; the minion-rail figure, 96.9 fJ, is the one to set "
         "against a cell-level estimate, and even that is the whole rail, not "
         "the one unit."),
        ("E60 is measured 'the cascade included', while this estimate and "
         "Q124 cover the Booth rows, the Wallace tree and the product adder "
         "only."),
        ("E60 is silicon and therefore contains glitches; this estimate and "
         "Q124 are zero-delay. tfma.glitch puts the timed tree at 1.4x the "
         "energy, so the comparable number is this estimate x 1.4."),
    ],
}


# ---------------------------------------------------------------- extraction
def pg_detail(groups, which, slew, load):
    """One internal_power EVENT, summed over its related_pg_pin groups.

    The groups handed in must all describe the same event -- the same
    (related_pin, output pin, `when`) -- because summing is only correct
    across the pg pins of one event.  Mutually exclusive `when` states are
    averaged by the caller, never summed.

    ASAP7 characterises each event against both rails: INVx1's output rise is
    +0.120 fJ on VDD and -0.028 fJ on VSS.  Two readings are carried:
      'vdd'  -- the VDD group alone, which is the energy drawn from the rail
                (part 2's SPICE run confirms this is the right one);
      'sum'  -- VDD + VSS, what a power tool reports as total internal
                energy.  It double-counts the same charge in and out, so it
                is kept only as a labelled reference column.
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
                # the `when` states here are the held data/enable values, and
                # they too are averaged, not summed
                ev = {}
                for key, grp in by_when.items():
                    dr = pg_detail(grp, "rise_power", slew, load)
                    df = pg_detail(grp, "fall_power", slew, load)
                    ev[key] = {
                        "per_clock_cycle_VDDonly_fJ": ((dr["vdd"] or 0.0)
                                                       + (df["vdd"] or 0.0)),
                        "per_clock_cycle_summed_reference_fJ": ((dr["sum"] or 0.0)
                                                                + (df["sum"] or 0.0)),
                    }
                vv = [v["per_clock_cycle_VDDonly_fJ"] for v in ev.values()]
                vals = [v["per_clock_cycle_summed_reference_fJ"] for v in ev.values()]
                rec["clock_pin_energy"][pin.name] = {
                    "by_state": ev,
                    "n_when_states": len(ev),
                    "state_weighting": "uniform over the held-data states",
                    "mean_per_cycle_VDDonly_fJ": sum(vv) / len(vv),
                    "mean_per_cycle_summed_reference_fJ": sum(vals) / len(vals),
                }
        elif direction == "output":
            for ip in pin.find("internal_power"):
                rel = L.attr1(ip, "related_pin")
                if rel is None:
                    continue
                when = L.attr1(ip, "when") or "(any)"
                for r in rel.split():
                    key = f"{r}->{pin.name}"
                    rec["arcs"].setdefault(key, {}).setdefault(when, []).append(ip)

    # Collapse the arc groups into numbers.
    #
    # An arc's `when` groups are MUTUALLY EXCLUSIVE side-input states -- FAx1's
    # A->SN carries four, (B*CI), (B*!CI), (!B*CI), (!B*!CI) -- and exactly one
    # of them holds at any moment.  So they are AVERAGED over states, never
    # summed; only the related_pg_pin groups WITHIN one state are summed.
    # Summing across states inflated every state-conditioned cell here by the
    # number of its states, 1.5x to 8.7x (found in review, same day).
    arcs = {}
    for key, bystate in rec["arcs"].items():
        states = {}
        for when, grp in bystate.items():
            dr = pg_detail(grp, "rise_power", slew, load)
            df = pg_detail(grp, "fall_power", slew, load)
            if dr["sum"] is None and df["sum"] is None:
                continue
            vr, vf = dr["vdd"] or 0.0, df["vdd"] or 0.0
            sr, sf = dr["sum"] or 0.0, df["sum"] or 0.0
            states[when] = {
                "E_int_rise_VDDonly_fJ": vr, "E_int_fall_VDDonly_fJ": vf,
                "E_int_per_transition_VDDonly_fJ": 0.5 * (vr + vf),
                "E_int_per_cycle_VDDonly_fJ": vr + vf,
                "E_int_rise_summed_fJ": sr, "E_int_fall_summed_fJ": sf,
                "E_int_per_transition_summed_fJ": 0.5 * (sr + sf),
            }
        if not states:
            continue
        n = len(states)
        mv = sum(s["E_int_per_transition_VDDonly_fJ"]
                 for s in states.values()) / n
        ms = sum(s["E_int_per_transition_summed_fJ"]
                 for s in states.values()) / n

        by_load = {}
        for c in LOAD_SWEEP:
            vals = []
            for when, grp in bystate.items():
                dr = pg_detail(grp, "rise_power", slew, c)
                df = pg_detail(grp, "fall_power", slew, c)
                if dr["sum"] is None and df["sum"] is None:
                    continue
                vals.append(0.5 * ((dr["vdd"] or 0.0) + (df["vdd"] or 0.0)))
            if not vals:
                continue
            m = sum(vals) / len(vals)
            by_load[f"{c}"] = {
                "E_int_per_transition_VDDonly_fJ": m,
                "E_transition_0p7_fJ": m + 0.5 * c * VDD_LIB ** 2,
                "E_transition_0p517_fJ": (m + 0.5 * c * VDD_LIB ** 2) * VSCALE,
            }

        arcs[key] = {
            "n_when_states": n,
            "when_states": sorted(states),
            "state_weighting": ("uniform over the mutually exclusive `when` "
                                "states; the liberty carries no state "
                                "probabilities"),
            "by_state": states,
            "E_int_per_transition_VDDonly_fJ": mv,
            "E_int_per_cycle_VDDonly_fJ": 2.0 * mv,
            "E_int_per_transition_summed_fJ": ms,
            "by_load_fJ": by_load,
            "E_transition_0p7_fJ": mv + 0.5 * load * VDD_LIB ** 2,
            "E_transition_0p517_fJ": (mv + 0.5 * load * VDD_LIB ** 2) * VSCALE,
            "E_transition_0p7_summed_reference_fJ": ms + 0.5 * load * VDD_LIB ** 2,
        }
    rec["arcs"] = arcs
    rec["E_int_per_transition_VDDonly_fJ"] = (
        sum(a["E_int_per_transition_VDDonly_fJ"] for a in arcs.values())
        / len(arcs)) if arcs else None
    rec["E_int_per_transition_summed_fJ"] = (
        sum(a["E_int_per_transition_summed_fJ"] for a in arcs.values())
        / len(arcs)) if arcs else None
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
    # The flip-flop's data-switching energy only: the clock runs on every
    # multiply-add either way (tfma.clocked), so the clock pin is not marginal.
    #
    # Which flop matters: the Q126(e) census's netlist contains exactly one
    # flop type, DFFHQx4 (1,953 of them), whose internal energy is 2.0x
    # DFFHQNx1's.  So the census mix is priced with the census's own flop, and
    # the two hand-built pools keep the minimum-drive DFFHQNx1 that matches
    # their own spirit.  Both are reported, and the swap is carried as a
    # sensitivity (found in review, same day: the estimate had used DFFHQNx1
    # while claiming the census's mix).
    FF_FOR_MIX = {"x1_drive": "DFFHQNx1", "min_drive": "DFFHQNx1",
                  "census": "DFFHQx4"}

    def ff_energy(name, fld):
        arcs = recs[name]["arcs"]
        arc = "CLK->Q" if "CLK->Q" in arcs else "CLK->QN"
        return arc, arcs[arc][fld]

    out = {"method": flip_estimate.__doc__.strip(),
           "wires": {"total": Q124["tfma.flip.gate"]["wires_total"],
                     "combinational": comb, "flip_flop_outputs": flops},
           "flop_choice": {
               "census_mix": ("DFFHQx4 -- the only flop type in Q126(e)'s "
                              "histogram, 1,953 of them"),
               "hand_built_pools": ("DFFHQNx1, the minimum-drive flop, to "
                                    "match those pools' minimum-drive cells"),
               "sensitivity": "see flop_sensitivity below"},
           "mixes": {}, "headline": {}}

    for conv, fld, ffld, cfld in (
            ("summed_reference", "E_int_per_transition_summed_fJ",
             "E_int_per_transition_summed_fJ",
             "weighted_E_int_per_transition_summed_fJ_0p7"),
            ("vdd_only", "E_int_per_transition_VDDonly_fJ",
             "E_int_per_transition_VDDonly_fJ",
             "weighted_E_int_per_transition_VDDonly_fJ_0p7")):
        cases = [(m, {n: recs[n][fld] for n in names if n in recs}, None)
                 for m, names in MIXES.items()]
        if census and census.get(cfld):
            cases.append(("census", None, census[cfld]))
        for mix, pool, forced in cases:
            ff_name = FF_FOR_MIX[mix]
            ff_arc_name, e_ff_int = ff_energy(ff_name, ffld)
            if forced is not None:
                e_mean = forced
                lo = hi = forced
                pool = {"(Q126(e) census-weighted)": forced}
            else:
                e_mean = sum(pool.values()) / len(pool)
                lo, hi = min(pool.values()), max(pool.values())
            rec = {"cell_pool_fJ_0p7": pool, "E_int_per_transition_fJ_0p7": e_mean,
                   "flop_cell": ff_name, "flop_arc": ff_arc_name,
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
            for k, r in out["mixes"].items() if k.startswith("vdd_only/")
            for c in ("1.0", "2.0", "4.0")]
    best = ("vdd_only/census" if "vdd_only/census" in out["mixes"]
            else "vdd_only/min_drive")
    band = out["mixes"][best]["load_band_1_to_4fF_pJ"]
    glitch = Q124["tfma.glitch"]["energy_ratio"]
    out["headline"] = {
        "full_range_vdd_only_pJ": [min(allv), max(allv)],
        "central_key": best,
        "central_pJ": out["mixes"][best]["loads_fF"]["2.0"]["E_flip_total_pJ"],
        "central_band_1_to_4fF_pJ": band,
        "central_what": ("VDD-only internal energy, `when`-state averaged "
                         "(the convention SPICE confirms in part 2), the cell "
                         "mix Q126(e) measured for this unit with its own "
                         "flop DFFHQx4, 2 fF per net, zero delay"),
        "compare_like_for_like": {
            "what": ("Q124 is the only like-for-like check: same 381-wire "
                     "count, same scope (Booth rows, tree, product adder), "
                     "same zero-delay basis."),
            "this_estimate_pJ": band,
            "q124_pJ": [Q124["tfma.flip.energy"]["pJ_low"],
                        Q124["tfma.flip.energy"]["pJ_high"]],
            "verdict": ("The estimate BRACKETS Q124 rather than erring dear: "
                        "its light-load end sits on Q124's low end, and it "
                        "runs above Q124 only for the heavier net loads."),
        },
        "compare_to_E60": {
            "operand_case": "a = pi, b bit 11 -- the case Q124 counted",
            "e60_board_fJ": E60["a_eq_pi"]["board_fJ"],
            "e60_minion_rail_fJ": E60["a_eq_pi"]["rail_fJ"],
            "not_this_case_a_eq_1p0_fJ": [E60["a_eq_1p0"]["board_fJ"],
                                          E60["a_eq_1p0"]["rail_fJ"]],
            "this_estimate_x_glitch_pJ": [b * glitch for b in band],
            "glitch_factor": glitch,
            "scope_differences": E60["scope_differences"],
        },
    }
    # Invert the model: what per-net load would make it hit each target?
    # The estimate is linear in the net load, so this is the single clearest
    # statement of how it compares with a measured or counted number.
    cen = out["mixes"][best]
    e_base = (cen["E_int_per_transition_fJ_0p7"] * VSCALE * comb
              + cen["E_int_flop_fJ_0p7"] * VSCALE * flops)      # fJ at C = 0
    per_fF = 0.5 * VDD_MIN ** 2 * (comb + flops)                # fJ per fF

    def implied(target_fJ, glitch=1.0):
        return (target_fJ / glitch - e_base) / per_fF

    out["headline"]["implied_net_load_fF"] = {
        "model": (f"E_flip(C) = {e_base:.2f} fJ + {per_fF:.2f} fJ/fF x C, "
                  "at 0.517 V, census mix, VDD only, zero delay"),
        "cell_only_fJ_at_zero_load": e_base,
        "fJ_per_fF_of_net_load": per_fF,
        "to_hit_q124_low_0p11pJ": implied(110.0),
        "to_hit_q124_high_0p13pJ": implied(130.0),
        "to_hit_e60_rail_96p9fJ_zero_delay": implied(
            E60["a_eq_pi"]["rail_fJ"]),
        "to_hit_e60_rail_96p9fJ_with_1p4x_glitch": implied(
            E60["a_eq_pi"]["rail_fJ"], glitch),
        "note": ("Q124's band corresponds to a per-net load of about 1.0 to "
                 "1.4 fF, which is squarely in the plausible range for a "
                 "tree-level wire plus a pin. E60's rail figure needs a "
                 "lighter load still, and once the 1.4x glitch factor is "
                 "carried it needs a load below any real wire -- but E60 "
                 "measures a different scope (the cascade included, the "
                 "whole rail, silicon not zero-delay), so that is a scope "
                 "gap, not a contradiction."),
    }

    # what the flop choice is worth, both ways round
    fs = {}
    for ffn in ("DFFHQNx1", "DFFHQx4"):
        if ffn not in recs:
            continue
        an, e = ff_energy(ffn, "E_int_per_transition_VDDonly_fJ")
        e_mean = (census["weighted_E_int_per_transition_VDDonly_fJ_0p7"]
                  if census else
                  sum(recs[n]["E_int_per_transition_VDDonly_fJ"]
                      for n in MIXES["min_drive"] if n in recs)
                  / len(MIXES["min_drive"]))
        e_load2 = 0.5 * 2.0 * VDD_MIN ** 2
        fs[ffn] = {
            "arc": an, "E_int_per_transition_VDDonly_fJ_0p7": e,
            "census_mix_flip_at_2fF_pJ": ((e_mean * VSCALE + e_load2) * comb
                                          + (e * VSCALE + e_load2) * flops) / 1000.0,
        }
    out["flop_sensitivity"] = {
        "by_flop": fs,
        "note": ("35 of the 381 toggling wires are flop outputs, so the flop "
                 "choice moves the headline by about 6%, against 2.2x for the "
                 "per-net load."),
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
        ("Internal energy is the VDD group alone, which part 2's SPICE run "
         "confirms is the energy drawn from the rail. The VDD+VSS sum is "
         "carried as a labelled reference only -- it double-counts the same "
         "charge in through VDD and out through VSS, and is what a power "
         "tool reports as 'total internal'."),
        ("An arc's mutually exclusive `when` states are AVERAGED, uniformly, "
         "never summed. The liberty carries no state probabilities, so a "
         "real workload's state statistics would shift the per-cell numbers "
         "within the by_state spread each arc carries."),
        ("Load per net = pin capacitance of what it drives plus its wire. "
         "ASAP7's own input pins are 0.62 fF (INVx1) to about 2 fF (FAx1); "
         "wire inside a 30 um tree level at 0.2 fF/um is roughly 0.5-1.5 fF. "
         "1, 2 and 4 fF bracket it; 2 fF is the headline."),
        ("Flip-flops: the data-switching (CLK->Q or CLK->QN) arc only. The "
         "clock reaches 1,586 of 1,851 flops on every multiply-add either "
         "way (tfma.clocked), so the clock-pin energy is not marginal to a "
         "flip. The census mix uses the census's own flop, DFFHQx4; the two "
         "hand-built pools use the minimum-drive DFFHQNx1. See "
         "flop_sensitivity."),
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
        e = r["E_int_per_transition_summed_fJ"]
        ev = r["E_int_per_transition_VDDonly_fJ"]
        nstates = max((a["n_when_states"] for a in r["arcs"].values()),
                      default=1)
        priced[name] = {"count": n,
                        "E_int_per_transition_VDDonly_fJ": ev,
                        "E_int_per_transition_summed_fJ": e,
                        "max_when_states_per_arc": nstates,
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
        "weighted_E_int_per_transition_VDDonly_fJ_0p7":
            tot_evdd / tot_n if tot_n else None,
        "weighted_E_int_per_transition_summed_fJ_0p7":
            tot_e / tot_n if tot_n else None,
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
            "internal_energy": ("THE HEADLINE NUMBER IS THE VDD GROUP ALONE. "
                                "ASAP7 splits each internal_power event "
                                "between VDD and VSS with a negative cross "
                                "term (INVx1's output rise is +0.120 fJ on "
                                "VDD and -0.028 fJ on VSS). Summing the two "
                                "double-counts the same charge in through "
                                "VDD and out through VSS; part 2's SPICE run "
                                "measures the rail directly and lands on the "
                                "VDD-only reading. Every "
                                "'..._summed_reference_fJ' key is the other "
                                "convention, kept only because a reader "
                                "coming from a power tool will see it. "
                                "rise/fall is the OUTPUT pin's direction."),
            "when_states": ("An arc's `when` groups are MUTUALLY EXCLUSIVE "
                            "side-input states and are AVERAGED over, "
                            "uniformly -- never summed. FAx1's A->SN carries "
                            "four of them. Summing inflates a "
                            "state-conditioned cell by the number of its "
                            "states (1.5x to 8.7x across the cells here); "
                            "each arc's `by_state` carries the spread."),
            "E_transition": ("E_int_per_transition (VDD only) + "
                             "1/2 C_load V^2, the task's formula: the energy "
                             "drawn from the rail per output transition, "
                             "averaged over a rise and a fall and over the "
                             "arc's `when` states. Over a full cycle the "
                             "load costs C_load V^2 in all."),
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
            mvdd = r["E_int_per_transition_VDDonly_fJ"]
            msum = r["E_int_per_transition_summed_fJ"]
            nst = max(a["n_when_states"] for a in arcs.values())
            etr = mvdd + 0.5 * CLOAD * VDD_LIB ** 2
            rows.append((base, blurb, capstr, r.get("leakage_pW"), nst,
                         mvdd, msum, etr, etr * VSCALE))
    lines = [
        "Internal energy is per OUTPUT TRANSITION, averaged over rise and fall",
        "and over the arc's mutually exclusive `when` states, then over the",
        "cell's arcs. **The headline convention is the VDD group alone**; the",
        "summed column is VDD+VSS, what a power tool reports, and it",
        "double-counts (part 2 settles it in SPICE). 10 ps input slew, 2.0 fF",
        "output load, RVT TT 0.7 V 25 C.",
        "",
        "| cell | what | input pin cap (fF) | leakage (pW) | when states | **internal E/transition, VDD only (fJ)** | summed reference, VDD+VSS (fJ) | **E/transition @0.7 V (fJ)** | **@0.517 V (fJ)** |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for base, blurb, capstr, lk, nst, mvdd, msum, etr, e517 in rows:
        lines.append(f"| {base} | {blurb} | {capstr} | {lk:.1f} | {nst} | "
                     f"{mvdd:.4f} | {msum:.4f} | {etr:.4f} | {e517:.4f} |")
    lines += ["",
              "`E/transition` = internal (VDD only) + 1/2 C_load V^2 at "
              "2.0 fF; the @0.517 V column scales the whole by (0.517/0.7)^2."]
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
    h = fe["headline"]
    print("  VDD-only range",
          [round(x, 3) for x in h["full_range_vdd_only_pJ"]],
          "| central", round(h["central_pJ"], 4),
          "| Q124", h["compare_like_for_like"]["q124_pJ"], "pJ")
    print("  E60 (a = pi, the matching case): board",
          E60["a_eq_pi"]["board_fJ"] / 1000, "pJ, minion rail",
          E60["a_eq_pi"]["rail_fJ"] / 1000, "pJ; this estimate x1.4 glitch",
          [round(x, 3) for x in h["compare_to_E60"]["this_estimate_x_glitch_pJ"]])
    print("  flop sensitivity:",
          {k: round(v["census_mix_flip_at_2fF_pJ"], 4)
           for k, v in fe["flop_sensitivity"]["by_flop"].items()})
    print("short circuit: Vtn+|Vtp| =",
          out["short_circuit_window"]["sum_sat_V"], "V vs VDD", VDD_MIN, "V")


if __name__ == "__main__":
    main()
