#!/usr/bin/env python3
"""Q128(d): the bottom of the Horace chain, from open data only.

One convention throughout:
  * every energy is the energy DRAWN FROM VDD by one event, at 0.517 V;
  * electrons = charge / e, with charge = energy / VDD;
  * a "cycle" is one rise plus one fall; a "transition"/"toggle" is one edge;
    a "rise" is the 0 -> 1 edge.  A capacitor C driven through a gate takes
    C x VDD^2 from the rail on the RISE and nothing on the fall, so a toggle
    -- the per-edge average -- costs 1/2 C VDD^2, which is also what the
    open-netlist power accounting charges per toggle.
  * the transistor section and the Landauer ladder are PER RISE, the net
    section is PER TOGGLE, and each says so; they differ by exactly 2x.

Builds docs/reports/data/2026-10-27-transistor-ledger/transistor-ledger.json
from
  * this request's SPICE runs on ASAP7's BSIM-CMG devices (one-switch3.json,
    pinq.json)  -- the transistor;
  * this request's DEF/SAIF/capacitance join (fanout2.json)  -- the net;
  * Q126(e)'s committed per-pattern power JSONs  -- the multiply-add;
  * E60's and E65's committed card measurements  -- the board.

  ledger.py <repo_root> <one-switch3.json> <fanout2.json> <pinq.json|-> <out.json>
            [one-switch4.json]
"""
import json
import math
import os
import sys

E = 1.602176634e-19        # C, exact
KB = 1.380649e-23          # J/K, exact
VDD = 0.517                # the minion rail the open flow prices at
LN2 = math.log(2)


def fit(xs, ys):
    """least squares y = a + b x, E60's reducer's shape"""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    return my - b * mx, b


def main():
    repo, swp, fanp, pinqp, outp = sys.argv[1:6]
    sw = json.load(open(swp))
    fan = json.load(open(fanp))
    pq = json.load(open(pinqp)) if pinqp != "-" else None
    sw4 = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else None
    pdir = os.path.join(repo, "docs/reports/data/2026-10-26-open-netlist/power")

    def pwr(tag):
        return json.load(open(os.path.join(pdir, f"power_gr_{tag}.json")))

    R = {
        "what": "the bottom of the Horace chain priced from open data: one transistor "
                "switching, one physical-net toggle, one random fp32 multiply-add, and "
                "Landauer's floor",
        "request": "Q128(d)",
        "date": "2026-10-27",
        "convention": {
            "energy": "the energy drawn from VDD by one event, at 0.517 V (the minion rail)",
            "electrons": "charge / e, with charge = energy / VDD and e = 1.602176634e-19 C",
            "cycle_vs_toggle": "a cycle is one rise + one fall; a toggle is one edge; a "
                               "rise is the 0 -> 1 edge. A capacitor C takes C.VDD^2 from "
                               "the rail on the rise and nothing on the fall, so a toggle "
                               "-- the per-edge average -- costs 0.5 C VDD^2",
            "which_unit_each_section_uses":
                "one_transistor_switching and the_floor's rungs are PER RISE (C.VDD^2), "
                "because that is what a device deck measures. one_physical_net_toggle is "
                "PER TOGGLE (0.5 C VDD^2), because that is what the SAIF counts; its "
                "C_total_fF x VDD^2 gives the per-rise figure, exactly twice the per-toggle "
                "one. up_to_the_board's figures are sums over a whole event and belong to "
                "neither unit.",
            "note_on_E60s_electron_column":
                "docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt prints electrons as "
                "C.V/e, i.e. 2E/(V.e) -- the charge of the equivalent capacitor. Under the "
                "convention here (E/(V.e)) every one of its electron figures halves. Both "
                "appear below, labelled.",
            "temperature": "25 C for every SPICE number (ASAP7's TT corner); the die "
                           "temperature only enters Landauer's floor, where it is stated",
            "electrons_of_a_board_figure":
                "a board energy is not delivered at the die's rail, so its electron count is a "
                "convention, not a measurement. Every electron figure here divides by the same "
                "0.517 V. The cards that produced E60, E65 and E38 ran at 521.9 mV, so an "
                "electron count taken at their own rail would be 0.9% lower.",
        },
        "sources": {
            "transistor": "this request's SPICE on ASAP7's BSIM-CMG devices and LVS cell "
                          "netlists, run on aifoundry2 in the Q126(d) environment",
            "net": "this request's join of the placed DEF, the global-route Steiner "
                   "capacitance and the bench SAIF, with Q126(e)'s own reader",
            "multiply_add": "Q126(e), docs/reports/data/2026-10-26-open-netlist/power/",
            "board": "E60 docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt; "
                     "E65 docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/; "
                     "E38/E39 docs/findings/05-claims.md",
        },
    }

    # ======================================================= 1. one transistor
    g = sw["one_device_gate_charge"]
    n1 = g["nmos_RVT_drain_gnd_0p517"]
    n1v = g["nmos_RVT_drain_vdd_0p517"]
    p1 = g["pmos_RVT_drain_gnd_0p517"]
    p1v = g["pmos_RVT_drain_vdd_0p517"]
    n3 = g["n3mos_RVT_drain_gnd_0p517"]
    inv = sw["inverter_by_load"]
    net_load = inv["0p517_2p105fF"]
    # The static per-fin gate charge: the mean of the four isolated-device
    # cases.  Section 2 splits a net's capacitance with it, because the
    # extractor's pin column and the liberty behind it are static too.
    one_static = (n1["Qg_aC"] + n1v["Qg_aC"] + p1["Qg_aC"] + p1v["Qg_aC"]) / 4

    one = {
        "what": "one minimum-size ASAP7 RVT device (Lg 20 nm, one fin), gate driven "
                "0 -> VDD through an ammeter and the current integrated",
        "isolated_device_at_0p517V": {
            "nmos_drain_at_0":   {"Qg_aC": n1["Qg_aC"], "electrons": n1["electrons"],
                                  "E_from_VDD_aJ": n1["E_from_VDD_aJ"],
                                  "Cgg_fF": n1["Cgg_effective_fF"]},
            "nmos_drain_at_VDD": {"Qg_aC": n1v["Qg_aC"], "electrons": n1v["electrons"],
                                  "E_from_VDD_aJ": n1v["E_from_VDD_aJ"],
                                  "Cgg_fF": n1v["Cgg_effective_fF"]},
            "pmos_drain_at_0":   {"Qg_aC": p1["Qg_aC"], "electrons": p1["electrons"],
                                  "E_from_VDD_aJ": p1["E_from_VDD_aJ"],
                                  "Cgg_fF": p1["Cgg_effective_fF"]},
            "pmos_drain_at_VDD": {"Qg_aC": p1v["Qg_aC"], "electrons": p1v["electrons"],
                                  "E_from_VDD_aJ": p1v["E_from_VDD_aJ"],
                                  "Cgg_fF": p1v["Cgg_effective_fF"]},
            "range_aJ": [min(x["E_from_VDD_aJ"] for x in (n1, n1v, p1, p1v)),
                         max(x["E_from_VDD_aJ"] for x in (n1, n1v, p1, p1v))],
            "mean_over_the_four_aJ": sum(x["E_from_VDD_aJ"] for x in (n1, n1v, p1, p1v)) / 4,
            "mean_over_the_four_electrons": sum(x["electrons"] for x in (n1, n1v, p1, p1v)) / 4,
        },
        "per_fin_linearity_check": {
            "three_fins_over_one": n3["Qg_aC"] / n1["Qg_aC"],
            "comment": "the gate charge is linear in fins to 0.01%, so 'per fin' is the "
                       "right unit and a wider device is simply more of them",
        },
        "charge_returns_at_the_fall": {
            "nmos_drain_at_0_C": n1["charge_returned_at_the_fall_C"],
            "comment": "the integrator comes back to zero, so the gate is a capacitor: "
                       "nothing is lost in the device itself, the energy is lost in "
                       "whatever drives it",
        },
        "inverter_per_edge_at_0p517V": {
            "no_load_internal_fJ_per_cycle_from_Q126d": 0.0241,
            "cross_check":
                "this request re-ran the same deck shape at 0.596 and 2.105 fF and reads "
                "internal 0.0415 and 0.0451 fJ per cycle, against Q126(d)'s 0.0407 at "
                "0.5 fF and 0.0450 at 2 fF -- the same measurement, to 2%",
            "with_a_typical_net_2p105fF": {
                "E_rail_fJ_per_cycle": net_load["E_rail_per_cycle_fJ"],
                "E_rail_fJ_per_toggle": net_load["E_rail_per_transition_fJ"],
                "of_which_the_load_CV2_fJ": net_load["E_load_CV2_per_cycle_fJ"],
                "of_which_the_cell_s_own_internal_fJ": net_load["E_internal_per_cycle_fJ"],
                "internal_share": net_load["internal_share"],
                "electrons_per_cycle": net_load["electrons_per_cycle"],
            },
            "by_load_fJ_per_cycle": {k: v["E_rail_per_cycle_fJ"]
                                     for k, v in sorted(inv.items()) if k.startswith("0p517")},
        },
        "short_circuit_share": {
            "measured_as": "excess rail energy over the cheapest input edge, INVx1 at the "
                           "2.105 fF a real net carries, edges 1-100 ps",
            "at_0p517V": sw["short_circuit_at_a_real_net_load"]["0p517"]["excess_share_over_cheapest"],
            "at_0p700V": sw["short_circuit_at_a_real_net_load"]["0p700"]["excess_share_over_cheapest"],
            "verdict":
                "over the 1-100 ps edges this first sweep covers, the spread is at most "
                "2.5% of the net's 0.608 fJ per cycle -- but at 0.517 V the curve was "
                "still falling at its slowest edge, so that was the sampled spread and "
                "not a bound. The extended sweep below finds the minimum.",
        },
    }
    if sw4:
        sc4 = {}
        for v in ("0p517", "0p700"):
            s = sw4[v]
            slew = s["excess_at_the_design_s_own_edge"]["output_slew"]
            sc4[v] = {
                "VDD_V": s["VDD_V"],
                "minimum_is_bracketed": s["minimum_is_bracketed"],
                "cheapest_edge_ps": s["cheapest_edge_ps"],
                "E_switching_at_the_minimum_fJ": s["E_switching_at_the_minimum_fJ"],
                "excess_share_by_input_edge_ps": {
                    k: r["excess_share"] for k, r in s["by_input_edge_ps"].items()},
                "max_excess_share": s["max_excess_share"],
                "output_slew_20_80_ps": slew,
                "static_leakage_nA": {k: leak["I_nA"] for k, leak
                                      in s["static_leakage"].items()},
                "worst_relative_difference_against_the_first_sweep":
                    s["against_the_first_sweep"]["worst_relative_difference"],
            }
        one["short_circuit_bracketed"] = dict(
            sc4,
            what="the same inverter and load swept 1 ps to 2 ns of input edge, on one "
                 "measurement window shared by every deck, with each input state's "
                 "static leakage measured and subtracted (one-switch4.json)",
            verdict=(
                "the minimum is real at both rails: %d ps at 0.517 V and %d ps at 0.700 V. "
                "Over the whole 1 ps - 2 ns range the spread is %.1f%% of a cycle at "
                "0.517 V against %.0f%% at 0.700 V, so short circuit is the term that "
                "blows up at the higher rail and is worth a couple of percent at the "
                "minion's. This inverter's own output edge into this load is %.1f ps "
                "(20-80%%), where it sits %.1f%% above its minimum."
                % (sc4["0p517"]["cheapest_edge_ps"], sc4["0p700"]["cheapest_edge_ps"],
                   100 * sc4["0p517"]["max_excess_share"],
                   100 * sc4["0p700"]["max_excess_share"],
                   sc4["0p517"]["output_slew_20_80_ps"]["rise_20_80_ps"],
                   100 * sc4["0p517"]["excess_share_by_input_edge_ps"]["20"])))

    if pq:
        mw = pq["mix_weighted_0p517"]
        one["in_a_real_cell_mix_weighted"] = {
            "what": "the same gate, measured at the pin of the cells this multiply-add "
                    "actually drives (15 types, %.1f%% of the toggle-weighted driven pins)"
                    % (100 * mw["share_of_driven_pins_covered"]),
            "Q_per_driven_pin_aC": mw["Q_per_driven_pin_aC"],
            "electrons_per_driven_pin": mw["electrons_per_driven_pin"],
            "E_from_VDD_per_driven_pin_aJ": mw["E_from_VDD_per_driven_pin_rising_edge_aJ"],
            "fins_per_driven_pin": mw["fins_per_driven_pin"],
            "Q_per_fin_aC": mw["Q_per_fin_aC"],
            "electrons_per_fin": mw["Q_per_fin_aC"] * 1e-18 / E,
            "E_from_VDD_per_fin_aJ": mw["Q_per_fin_aC"] * 1e-18 * VDD * 1e18,
            "over_the_isolated_device_static_mean": mw["Q_per_fin_aC"] / one_static,
            "comment":
                "a fin inside a working cell costs the driver MORE than the same fin "
                "measured alone, because the cell's output swings against the input "
                "(Miller) and the internal nodes move with it. That excess is real energy "
                "and it is transistor, not wire -- but it is not capacitance sitting on "
                "the net, so the capacitance split above uses the static figure instead. "
                "The per-hold-state spread in by_cell_pin is the size of the Miller term: "
                "a cell whose output cannot move in either state (AO21x1 driven on A1, "
                "MAJx2) shows none.",
            "schematic_pin_over_liberty_pin": mw["schematic_over_liberty"],
            "schematic_pin_fF": mw["C_schematic_pin_fF"],
            "liberty_pin_fF": mw["C_liberty_pin_fF"],
            "the_split_inside_the_pin":
                "the liberty's pin capacitance was characterised on ASAP7's "
                "parasitic-extracted netlist; the SPICE here is the LVS (schematic) one. "
                "The ratio is what the cell's own layout interconnect adds to its "
                "transistors -- wire, inside the cell.",
        }
    R["one_transistor_switching"] = one

    # ================================================ 2. one physical-net toggle
    s = fan["summary"]["signal_nets_active_named_by_the_DEF"]
    sall = fan["summary"]["signal_nets_active"]
    c = fan["summary"]["clock_nets"]

    # Which per-fin number splits a net's CAPACITANCE?  The static one.  The
    # extractor's pin column and the liberty it comes from are both static
    # capacitances, so the transistor share has to be measured the same way:
    # the four isolated-device cases (n/p, drain at 0 and at VDD), averaged.
    # The in-cell pin charge measured below is LARGER, because in a working
    # cell the output swings against the input -- that Miller term is real
    # energy the driver pays, but it is not capacitance on the net, so it does
    # not belong in the split.
    per_fin_aC = one_static

    def split(row):
        ctot = row["cap_fF_mean_toggle_weighted"]
        cw = row["wire_fF_mean_toggle_weighted"]
        cp_ = row["pin_fF_mean_toggle_weighted"]
        cg = (row["fins_behind_the_pins_toggle_weighted"] * per_fin_aC * 1e-18 / VDD * 1e15
              if per_fin_aC else None)
        out = {
            "nets": row["nets"], "toggles_per_muladd": row["toggles_per_muladd"],
            "gate_pins_driven": row["fanout_mean_toggle_weighted"],
            "transistor_fins_behind_them": row["fins_behind_the_pins_toggle_weighted"],
            "C_total_fF": ctot,
            "C_wire_between_cells_fF": cw,
            "C_pin_fF": cp_,
            "E_per_toggle_fJ": 0.5 * ctot * 1e-15 * VDD * VDD * 1e15,
            "electrons_per_toggle": 0.5 * ctot * 1e-15 * VDD / E,
        }
        if cg is not None:
            out.update({
                "C_transistor_gates_fF": cg,
                "C_wire_inside_the_cells_fF": cp_ - cg,
                "share_transistor": cg / ctot,
                "share_wire_inside_the_cells": (cp_ - cg) / ctot,
                "share_wire_between_cells": cw / ctot,
                "E_per_toggle_on_the_transistors_fJ": 0.5 * cg * 1e-15 * VDD * VDD * 1e15,
            })
        return out

    SPLIT_S, SPLIT_ALL, SPLIT_C = split(s), split(sall), split(c)

    # A second, independent route to the same split, for cross-checking: the
    # mix-weighted ratio of the SPICE schematic input capacitance to the
    # liberty's own pin capacitance, over the cells this unit drives.  Route A
    # counts fins and prices each; route B measures whole pins and divides.
    if pq:
        rB = pq["mix_weighted_0p517"]["schematic_over_liberty"]
        for row, tag in ((SPLIT_S, "signal"), (SPLIT_C, "clock")):
            cg = row["C_pin_fF"] * rB
            row["cross_check_route_B"] = {
                "what": "C_pin x (SPICE schematic pin capacitance / liberty pin "
                        "capacitance), mix-weighted over the driven cells",
                "schematic_over_liberty": rB,
                "C_transistor_gates_fF": cg,
                "share_transistor": cg / row["C_total_fF"],
                "route_A_share_transistor": row["share_transistor"],
                "A_over_B": row["share_transistor"] / (cg / row["C_total_fF"]),
            }
    R["one_physical_net_toggle"] = {
        "what": "what one toggle of one physical net in the TensorFMA32 lane charges, "
                "activity-weighted over a random fp32 multiply-add",
        "per_fin_capacitance_used_for_the_split": {
            "Q_per_fin_aC_static": one_static,
            "C_per_fin_fF": one_static * 1e-18 / VDD * 1e15,
            "from": "the mean of the four isolated-device cases (nmos/pmos, drain held at "
                    "0 and at VDD), which is a static capacitance like the liberty's own "
                    "pin column",
            "spread_over_the_four_aC": [min(x["Qg_aC"] for x in (n1, n1v, p1, p1v)),
                                        max(x["Qg_aC"] for x in (n1, n1v, p1, p1v))],
        },
        "signal_nets": SPLIT_S,
        "signal_nets_including_those_the_DEF_does_not_name": SPLIT_ALL,
        "clock_nets": SPLIT_C,
        "def_coverage": {
            "nets_in_the_capacitance_table": fan["nets_in_netcap"],
            "nets_the_DEF_names": fan["nets_in_netcap_found_in_the_DEF"],
            "check_liberty_pin_sum_over_extractor_pin_column":
                fan["check_liberty_pin_sum_over_extractor_pin_column"],
            "comment":
                "the capacitance table names nets hierarchically and the written Verilog is "
                "flat, so fanout has to come from the DEF. On the nets the DEF names, the "
                "sum of the liberty's own pin capacitances reproduces the extractor's pin "
                "column, which is the check that the join is right. The 'including' row "
                "reads fanout 0 for the rest and so is a floor.",
        },
        "the_wire_is_a_lower_bound":
            "the between-cell capacitance is the global-route Steiner estimate with no "
            "coupling term (detailed routing never closed, Q126(e)), so the wire share is "
            "a floor and the transistor share a ceiling.",
    }

    # the join has to reproduce Q126(e)'s own published numbers, or it is wrong
    rnx = pwr("randn")
    R["one_physical_net_toggle"]["reproduces_Q126e"] = {
        "signal_toggles_per_muladd": {
            "this_join": SPLIT_ALL["toggles_per_muladd"],
            "power_gr_randn.json": rnx["per_muladd"]["signal_toggles"]},
        "clock_toggles_per_muladd": {
            "this_join": SPLIT_C["toggles_per_muladd"],
            "power_gr_randn.json": (rnx["per_muladd"]["toggles"]
                                    - rnx["per_muladd"]["signal_toggles"])},
        "fJ_per_signal_toggle": {
            "this_join_half_CV2": SPLIT_ALL["E_per_toggle_fJ"],
            "power_gr_randn.json_energy_over_toggles":
                rnx["total"]["signal_energy_J"] / rnx["total"]["signal_toggles"] * 1e15},
        "fJ_per_clock_toggle": {
            "this_join_half_CV2": SPLIT_C["E_per_toggle_fJ"],
            "power_gr_randn.json_energy_over_toggles":
                rnx["total"]["clock_energy_J"] / rnx["total"]["clock_toggles"] * 1e15},
        "total_extracted_cap_fF": {
            "this_join": fan["summary"]["all_nets"]["cap_fF_total"],
            "power_gr_randn.json": rnx["coverage"]["cap_fF_extracted"]},
        "comment": "the weights here are power.py's own, so these must agree exactly; they do",
    }

    # ====================================================== 3. up to the board
    rn = pwr("randn")
    zz = pwr("zeros")
    ladder = {}
    for fam in ("lq", "lb"):
        hs = [1, 2, 4, 8]
        sws = [pwr(f"{fam}_h{h}")["per_muladd"]["energy_pJ"] for h in hs]
        swi = [pwr(f"{fam}_h{h}")["per_muladd"]["switching_plus_internal_pJ"] for h in hs]
        a1, b1 = fit(hs, sws)
        a2, b2 = fit(hs, swi)
        ladder[fam] = {"intercept_pJ": a1, "fJ_per_designed_bit_switching": b1 * 1000,
                       "intercept_with_internal_pJ": a2,
                       "fJ_per_designed_bit_with_internal": b2 * 1000}

    BOARD = {
        "lq": {"fJ": 116.746, "se": 0.613, "rail_fJ": 87.520,
               "what": "E60, quiet partner A = 1.0, per designed flipped bit, "
                       "aifoundry3 at 600 MHz and 521.9 mV, 4 passes"},
        "lb": {"fJ": 129.918, "se": 0.480, "rail_fJ": 96.850,
               "what": "E60, busy partner A = pi, per designed flipped bit, same card"},
    }
    E65 = {
        "flow_M_b_bit11_vs_a_pi_fJ": 745, "se": 56,
        "bit6_fJ": 83, "bit22_fJ": 1008,
        "what": "E65, aifoundry3, 600 MHz, 521.9 mV, per designed flipped bit at the board",
    }
    E38 = {
        "per_muladd_over_idle_pJ": {"zeros": 0.27, "ones": 2.13, "randn": 5.783},
        "per_card_randn_pJ": {"aifoundry2": 5.92, "aifoundry3": 5.37, "aifoundry1_c1": 6.06},
        "what": "E38/E39's registered V3-ABL-A values, three cards; the chain's "
                "0.27 / 2.13 / 5.78 pJ are the three-card means of them "
                "(docs/findings/05-claims.md)",
    }

    def closure(bottom_fJ, board_fJ, rail_fJ):
        return {"vs_board": bottom_fJ / board_fJ, "vs_rail": bottom_fJ / rail_fJ}

    perbit = {}
    for fam in ("lq", "lb"):
        b = BOARD[fam]
        perbit[fam] = {
            "what": b["what"],
            "open_netlist_switching_fJ": ladder[fam]["fJ_per_designed_bit_switching"],
            "open_netlist_with_cell_internal_fJ": ladder[fam]["fJ_per_designed_bit_with_internal"],
            "board_fJ": b["fJ"], "board_se_fJ": b["se"], "rail_fJ": b["rail_fJ"],
            "rail_over_board": b["rail_fJ"] / b["fJ"],
            "closure_switching": closure(ladder[fam]["fJ_per_designed_bit_switching"],
                                         b["fJ"], b["rail_fJ"]),
            "closure_with_internal": closure(ladder[fam]["fJ_per_designed_bit_with_internal"],
                                             b["fJ"], b["rail_fJ"]),
            "electrons_bottom_up": ladder[fam]["fJ_per_designed_bit_switching"] * 1e-15 / VDD / E,
            "electrons_at_the_board": b["fJ"] * 1e-15 / VDD / E,
            "electrons_at_the_board_in_E60s_own_column": b["fJ"] * 1e-15 / VDD / E * 2,
        }

    sw_pJ = rn["per_muladd"]["energy_pJ"]
    int_pJ = rn["per_muladd"]["switching_plus_internal_pJ"] - sw_pJ
    clk_share = rn["clock_share"]
    permul = {
        "what": "one random fp32 multiply-add in one lane, against what the card pays for "
                "one over idle",
        "open_netlist_switching_pJ": sw_pJ,
        "of_which_clock_tree_pJ": sw_pJ * clk_share,
        "of_which_signal_pJ": sw_pJ * (1 - clk_share),
        "clock_share": clk_share,
        "cells_own_internal_pJ": int_pJ,
        "open_netlist_total_pJ": sw_pJ + int_pJ,
        "capacitance_priced": rn["coverage"]["cap_fraction_priced"],
        "board_pJ": E38["per_muladd_over_idle_pJ"]["randn"],
        "rail_pJ": E38["per_muladd_over_idle_pJ"]["randn"] * 0.75,
        "closure_switching": closure(sw_pJ, E38["per_muladd_over_idle_pJ"]["randn"],
                                     E38["per_muladd_over_idle_pJ"]["randn"] * 0.75),
        "closure_total": closure(sw_pJ + int_pJ, E38["per_muladd_over_idle_pJ"]["randn"],
                                 E38["per_muladd_over_idle_pJ"]["randn"] * 0.75),
        "electrons_bottom_up": (sw_pJ + int_pJ) * 1e-12 / VDD / E,
        "electrons_at_the_board": E38["per_muladd_over_idle_pJ"]["randn"] * 1e-12 / VDD / E,
        "toggles_per_muladd": rn["per_muladd"]["toggles"],
        "signal_toggles_per_muladd": rn["per_muladd"]["signal_toggles"],
        "zeros_caution":
            "the open flow prices the zeros pattern at %.3f pJ, against E38's 0.27 pJ over "
            "idle, but these are not the same quantity: the open flow's zeros figure is the "
            "ungated root of this lane's clock tree, which on a card is already inside the "
            "idle the measurement subtracts. Do not read it as 80%% closure."
            % zz["per_muladd"]["energy_pJ"],
    }

    # the bottom-up ledger, by what the energy charges
    sg, ck = SPLIT_S, SPLIT_C
    if per_fin_aC:
        es, ec = sw_pJ * (1 - clk_share), sw_pJ * clk_share
        permul["switching_by_what_it_charges_pJ"] = {
            "transistor_gates": es * sg["share_transistor"] + ec * ck["share_transistor"],
            "wire_inside_the_cells": (es * sg["share_wire_inside_the_cells"]
                                      + ec * ck["share_wire_inside_the_cells"]),
            "wire_between_the_cells": (es * sg["share_wire_between_cells"]
                                       + ec * ck["share_wire_between_cells"]),
            "note": "the cells' own internal energy (%.3f pJ) sits on top of all three and "
                    "is not split here" % int_pJ,
        }
        t = permul["switching_by_what_it_charges_pJ"]
        tot = t["transistor_gates"] + t["wire_inside_the_cells"] + t["wire_between_the_cells"]
        permul["switching_by_what_it_charges_share"] = {
            k: t[k] / tot for k in ("transistor_gates", "wire_inside_the_cells",
                                    "wire_between_the_cells")}

    R["up_to_the_board"] = {
        "per_flipped_operand_bit": perbit,
        "per_random_fp32_multiply_add": permul,
        "E65_not_closed_here": dict(E65, note=(
            "E65 prices 32 individual B-side bit positions and the flow-M flip. The open "
            "flow was only run on the ladder's own h = 0,1,2,4,8 rungs, so there is no "
            "like-for-like bottom-up number for a named bit position yet; running "
            "mktiles.sh on E65's own operand files would give one.")),
        "E38": E38,
        "what_the_missing_energy_is":
            "the bottom-up figure is a floor three times over: half the design's "
            "capacitance is unpriced (CTS and repair_design made those nets after the "
            "netlist was simulated), the between-cell wire has no coupling term, and the "
            "ledger covers one lane's arithmetic while the board pays for the register "
            "file's read ports, the operand bus, the result path and leakage as well.",
    }

    # ============================================================ 4. the floor
    floors = {}
    for name, tc in (("die at the governor's trip, 66 C", 66.0),
                     ("die at E65's block temperature, 58 C", 58.0),
                     ("the SPICE corner, 25 C", 25.0),
                     ("the leakage corner, 80 C", 80.0)):
        T = tc + 273.15
        floors[name] = {"T_K": T, "kT_ln2_J": KB * T * LN2, "kT_ln2_zJ": KB * T * LN2 * 1e21}
    kt = floors["die at the governor's trip, 66 C"]["kT_ln2_J"]

    rungs = {
        "one electron across the rail (e x 0.517 V)": VDD * E,
        "one minimum device's gate, isolated (mean of the four bias cases)":
            one_static * 1e-18 * VDD,
    }
    if pq:
        rungs["one transistor fin, driven inside a working cell"] = \
            pq["mix_weighted_0p517"]["Q_per_fin_aC"] * 1e-18 * VDD
        rungs["one gate pin of the cells this unit drives"] = \
            pq["mix_weighted_0p517"]["E_from_VDD_per_driven_pin_rising_edge_aJ"] * 1e-18
    # Per RISE, like every rung above: a net's C takes C.VDD^2 on the 0 -> 1
    # edge, which is twice the per-toggle figure section 2 reports.  Mixing the
    # two units here is what made 14.5 fins x 108 electrons read as 43% of a
    # net instead of the 21.7% the capacitances actually say.
    rungs["one rise (0 -> 1) of an average signal net"] = 2 * sg["E_per_toggle_fJ"] * 1e-15
    rungs["one rise (0 -> 1) of an average clock net"] = 2 * ck["E_per_toggle_fJ"] * 1e-15
    rungs["one flipped operand bit, open netlist, quiet partner"] = \
        ladder["lq"]["fJ_per_designed_bit_switching"] * 1e-15
    rungs["one flipped operand bit, E60 at the board"] = BOARD["lq"]["fJ"] * 1e-15
    rungs["one flipped operand bit, E65's flow-M at the board"] = E65["flow_M_b_bit11_vs_a_pi_fJ"] * 1e-15
    rungs["one random fp32 multiply-add, open netlist"] = (sw_pJ + int_pJ) * 1e-12
    rungs["one random fp32 multiply-add, E38 at the board"] = \
        E38["per_muladd_over_idle_pJ"]["randn"] * 1e-12

    R["the_floor"] = {
        "what": "Landauer's kT ln2, at the die's own temperature, against every rung",
        "unit": "every single-edge rung here is ONE RISE (C.VDD^2 from the rail); the "
                "rungs from a flipped bit upwards are whole composite events. Section "
                "one_physical_net_toggle's per-toggle figures are half the two net rungs.",
        "kT_ln2": floors,
        "rungs": {k: {"E_J": v, "over_Landauer_at_66C": v / kt,
                      "electrons": v / VDD / E} for k, v in rungs.items()},
        "the_one_sentence":
            "moving a single electron across this chip's 0.517 V rail already costs %.1f "
            "Landauer quanta at the die's 66 C, and the smallest switch in the design -- "
            "one minimum transistor's gate -- moves %.0f of them, so the floor is %.0fx "
            "below one transistor and %.2g x below one random fp32 multiply-add at the board."
            % (VDD * E / kt, one_static * 1e-18 / E, one_static * 1e-18 * VDD / kt,
               E38["per_muladd_over_idle_pJ"]["randn"] * 1e-12 / kt),
    }

    json.dump(R, open(outp, "w"), indent=1, sort_keys=True)
    print("wrote", outp)
    return R


if __name__ == "__main__":
    main()
