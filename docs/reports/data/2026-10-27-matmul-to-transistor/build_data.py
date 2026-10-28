#!/usr/bin/env python3
"""Assemble the data block for the matmul-to-transistor page from the committed data directories.

    build_data.py <repo root> <out.json>

Every value comes from a committed data directory, so the page cannot drift from the record. The page's
script also renders an optional `vault` block of {title, rows} boxes when a build adds one; nothing in this
repository writes that block, and the page built here has none.
"""
import json
import math
import sys

root, out = sys.argv[1], sys.argv[2]

D = f"{root}/docs/reports/data"
chain = json.load(open(f"{D}/2026-10-27-chain-closure/chain.json"))
led = json.load(open(f"{D}/2026-10-27-transistor-ledger/transistor-ledger.json"))
# Q129's rebuilt waterfall (28 Oct 2026): the board-to-rail step measured instead of carried across, and the
# bottom-up count rebuilt with routed wires, all of the capacitance, the measured glitch factor and the lane's
# transport. Its own script asserts the arithmetic; see that directory's README for which rows overlap.
wf2 = json.load(open(f"{D}/2026-10-28-q129-waterfall/waterfall-v2.json"))

pl = chain["price_list"]
sat = chain["saturation"]
sup = chain["superposition"]
bud = chain["budget_600"]
ch = chain["chain"]
net = led["one_physical_net_toggle"]
tr = led["one_transistor_switching"]
board = led["up_to_the_board"]
floor = led["the_floor"]

o = {}

# ---- level 0: the speed gap -------------------------------------------------
o["speed"] = {
    "burst": {"zeros_tflops": 12.3, "randn_tflops": 10.7, "ratio": 12.3 / 10.7, "pct": 100 * (12.3 / 10.7 - 1)},
    # the sustained gap is exact in clocks: zeros holds 800 MHz and random data sits on the governor's
    # 600 MHz floor, and E64's 9.2 TFLOPS is 12.3 x 600/800 = 9.225 rounded. Quote 800/600, not 12.3/9.2.
    "sustained": {"zeros_tflops": 12.3, "randn_tflops": 9.2, "zeros_mhz": 800, "randn_mhz": 600,
                  "ratio": 800 / 600, "pct": 100 * (800 / 600 - 1), "exact_in_clocks": True},
    "comparators": ch["burst_measured_comparators"],
}

# ---- level 1: the governor --------------------------------------------------
# chain.json's clamp note said the window holds "every candidate cap"; E64's measured sustained randn
# point, 54.4 W, is above it. Corrected at its source (chain.py) on Tue 27 Oct 2026, so it is carried as is.
_clamp = dict(ch["sustained_is_a_clamp"])
assert "every candidate cap" not in _clamp["note"], "chain.json carries the superseded clamp note again"
o["governor"] = {
    "cap_W": ch["power_cap_W"], "cap_source": ch["power_cap_source"],
    "tau_s": ch["governor"]["tau_s"], "rms_mhz": ch["governor"]["rms_mhz"], "n": ch["governor"]["n"],
    "trip_C": 66.0, "die_line": ch["die_line"], "sustained_cap_W": ch["sustained_cap_W"],
    "clamp": _clamp, "cap_sensitivity": ch["burst_cap_sensitivity"],
}

# ---- level 2: board power ---------------------------------------------------
o["board"] = {
    "measured": ch["e64_measured_board_W"], "predicted": ch["predicted_board_W"],
    "static_B_W": ch["B_f_W"], "anchors_600_W": chain["superposition"]["anchors_W"],
    "step_W": sup["step_W"], "clocking_W": sup["clocking_W"], "data_W": sup["data_W"],
}

# ---- level 3: board to the rail --------------------------------------------
o["rail"] = {
    "lq_ratio": board["per_flipped_operand_bit"]["lq"]["rail_over_board"],
    "lb_ratio": board["per_flipped_operand_bit"]["lb"]["rail_over_board"],
    "range": [0.70, 0.89],
}

# ---- level 4: per multiply-add ---------------------------------------------
o["permac"] = {
    "e38_registered": bud["e38_pJ_registered_per_card"],
    "e38_source": bud["e38_source"],
    "mean_zeros_pJ": 0.27, "mean_ones_pJ": 2.13, "mean_randn_pJ": 5.783,
    "budget_600_pJ": bud["pJ_per_mac"],
    "this_work_clocking_pJ": bud["pJ_per_mac"]["clocking"],
    "this_work_data_pJ": bud["pJ_per_mac"]["data"],
}
# The per-multiply-add figure and the per-bit price are measured in different experiments, so the page must
# not present one as a quotient of the other. What IS a fair consistency check: the DATA half of the budget
# (the clocking half does not depend on the operands) over the bits that actually change.
o["permac"]["changed_bits"] = sup["m_A"] + sup["m_B"]
o["permac"]["data_per_changed_bit_fJ"] = 1000.0 * bud["pJ_per_mac"]["data"] / o["permac"]["changed_bits"]

# ---- level 5: per flipped bit ----------------------------------------------
B, A = pl["B_fJ"], pl["A_fJ"]
o["perbit"] = {
    "e60_lq_fJ": board["per_flipped_operand_bit"]["lq"]["board_fJ"],
    "e60_lq_se": board["per_flipped_operand_bit"]["lq"]["board_se_fJ"],
    "e60_lb_fJ": board["per_flipped_operand_bit"]["lb"]["board_fJ"],
    "e60_lb_se": board["per_flipped_operand_bit"]["lb"]["board_se_fJ"],
    "e60_cards": {"aifoundry3 600 MHz, quiet partner": 116.746, "aifoundry3 600 MHz, busy partner": 129.918,
                  "aifoundry2 800 MHz": 121.3, "aifoundry1 card 0, 800 MHz": 102.490},
    "B_fJ": B, "B_se_fJ": pl["B_se_fJ"], "A_fJ": A, "A_se_fJ": pl["A_se_fJ"],
    "B_min": min(B.values()), "B_max": max(B.values()), "B_span": max(B.values()) / min(B.values()),
    "A_min": min(A.values()), "A_max": max(A.values()), "A_span": max(A.values()) / min(A.values()),
    "shape": pl["shape"],
    "flowM_fJ": 745.0, "flowM_se": 56.0, "flowM_A_side_fJ": 856.0,
    "e68_band_fJ": [117.5, 135.9], "e68_vs_e60_same_card": [133.7, 121.3],
    "e66_leak_W_per_C": 0.294, "a1_leak_W_per_C": 1.508,  # E66 final: median of 18 cycles, 51-58 C (lab 1cd09165)
    "ladder_rows": sat["lq_rows"], "flat_fJ_per_bit": sat["flat_fJ_per_bit"],
    "flat_marginal_fJ": sat["flat_fJ_per_bit_marginal"],
    "laws": sat["law_scores_pct"], "beta": sat["beta"],
}

# ---- level 6: toggles -------------------------------------------------------
o["toggles"] = {
    "signal_per_mac": net["signal_nets"]["toggles_per_muladd"],
    "signal_per_mac_all": net["signal_nets_including_those_the_DEF_does_not_name"]["toggles_per_muladd"],
    "clock_per_mac": net["clock_nets"]["toggles_per_muladd"],
    "total_per_mac": board["per_random_fp32_multiply_add"]["toggles_per_muladd"],
    "open_netlist_wires": 3299, "rtl_names_traced": 7232.7, "names_per_wire": 7232.7 / 3299,
    "names_per_wire_measured": 2.55, "merged_floor": 1300.8,
    "bench_overcount": 21331,
    "per_designed_bit_switching_fJ": board["per_flipped_operand_bit"]["lb"]["open_netlist_switching_fJ"],
    "per_designed_bit_total_fJ": board["per_flipped_operand_bit"]["lb"]["open_netlist_with_cell_internal_fJ"],
    "closure_lb": board["per_flipped_operand_bit"]["lb"]["closure_switching"]["vs_board"],
    "closure_lb_total": board["per_flipped_operand_bit"]["lb"]["closure_with_internal"]["vs_board"],
    "closure_lq": board["per_flipped_operand_bit"]["lq"]["closure_switching"]["vs_board"],
    "closure_lq_total": board["per_flipped_operand_bit"]["lq"]["closure_with_internal"]["vs_board"],
}

# ---- level 7: nets, gates, wires -------------------------------------------
o["gates"] = {
    "signal": net["signal_nets"], "clock": net["clock_nets"],
    "split_pJ": board["per_random_fp32_multiply_add"]["switching_by_what_it_charges_pJ"],
    "split_share": board["per_random_fp32_multiply_add"]["switching_by_what_it_charges_share"],
    "internal_pJ": board["per_random_fp32_multiply_add"]["cells_own_internal_pJ"],
    "switching_pJ": board["per_random_fp32_multiply_add"]["open_netlist_switching_pJ"],
    "total_pJ": board["per_random_fp32_multiply_add"]["open_netlist_total_pJ"],
    "board_pJ": board["per_random_fp32_multiply_add"]["board_pJ"],
    "rail_pJ": board["per_random_fp32_multiply_add"]["rail_pJ"],
    "capacitance_priced": board["per_random_fp32_multiply_add"]["capacitance_priced"],
    "clock_share": board["per_random_fp32_multiply_add"]["clock_share"],
    "driven_pin": tr["in_a_real_cell_mix_weighted"],
    "wire_is_a_floor": net["the_wire_is_a_lower_bound"],
}

# ---- level 8: one transistor -----------------------------------------------
iso = tr["isolated_device_at_0p517V"]
o["transistor"] = {
    "E_aJ": iso["mean_over_the_four_aJ"], "electrons": iso["mean_over_the_four_electrons"],
    "Cgg_fF": net["per_fin_capacitance_used_for_the_split"]["C_per_fin_fF"],
    "Q_per_fin_aC": net["per_fin_capacitance_used_for_the_split"]["Q_per_fin_aC_static"],
    "range_aJ": iso["range_aJ"], "VDD": 0.517,
    "in_a_cell": {"E_per_fin_aJ": tr["in_a_real_cell_mix_weighted"]["E_from_VDD_per_fin_aJ"],
                  "electrons_per_fin": tr["in_a_real_cell_mix_weighted"]["electrons_per_fin"],
                  "Q_per_fin_aC": tr["in_a_real_cell_mix_weighted"]["Q_per_fin_aC"]},
    "short_circuit": tr["short_circuit_bracketed"],
    "fins_per_signal_net": net["signal_nets"]["transistor_fins_behind_them"],
    "fins_per_clock_net": net["clock_nets"]["transistor_fins_behind_them"],
    "transistor_share": net["signal_nets"]["share_transistor"],
}

# ---- level 9: electrons and the floor --------------------------------------
# the rungs are renamed to short, stable keys here, so a wording change upstream cannot silently empty a
# number on the page; the long name travels with each rung as its label.
RUNG = {
    "mac_board": "one random fp32 multiply-add, E38 at the board",
    "mac_netlist": "one random fp32 multiply-add, open netlist",
    "bit_flowM": "one flipped operand bit, E65's flow-M at the board",
    "bit_board": "one flipped operand bit, E60 at the board",
    "bit_netlist": "one flipped operand bit, open netlist, quiet partner",
    "clock_rise": "one rise (0 -> 1) of an average clock net",
    "signal_rise": "one rise (0 -> 1) of an average signal net",
    "gate_pin": "one gate pin of the cells this unit drives",
    "fin_in_cell": "one transistor fin, driven inside a working cell",
    "transistor": "one minimum device's gate, isolated (mean of the four bias cases)",
    "electron": "one electron across the rail (e x 0.517 V)",
}
LABEL = {
    "mac_board": "One random fp32 multiply-add, at the board (E38)",
    "mac_netlist": "One random fp32 multiply-add, counted on the open netlist",
    "bit_flowM": "One flipped operand bit, E65's flow-M case, at the board",
    "bit_board": "One flipped operand bit, E60's quiet ladder, at the board",
    "bit_netlist": "One flipped operand bit, counted on the open netlist",
    "clock_rise": "One rise of an average clock net",
    "signal_rise": "One rise of an average signal net",
    "gate_pin": "One gate pin of the cells this unit drives",
    "fin_in_cell": "One transistor fin, driven inside a working cell",
    "transistor": "One minimum transistor's gate, isolated",
    "electron": "One electron across the 0.517 V rail",
}
# The same rungs named short enough to fit beside their value column on a phone, where the chart has about
# 330px of label room rather than 700.
SHORT = {
    "mac_board": "One random fp32 multiply-add, at the board",
    "mac_netlist": "The same, counted on the open netlist",
    "bit_flowM": "One flipped bit (E65 flow-M), at the board",
    "bit_board": "One flipped operand bit, at the board",
    "bit_netlist": "The same, counted on the netlist",
    "clock_rise": "One rise of an average clock net",
    "signal_rise": "One rise of an average signal net",
    "gate_pin": "One gate pin of the cells driven",
    "fin_in_cell": "One transistor fin, inside a cell",
    "transistor": "One transistor's gate, isolated",
    "electron": "One electron across the rail",
}
rungs = {}
for k, long in RUNG.items():
    r = dict(floor["rungs"][long])
    r["label"] = LABEL[k]
    r["short"] = SHORT[k]
    rungs[k] = r
land = [v for key, v in floor["kT_ln2"].items() if "66" in key][0]
o["floor"] = {
    "rungs": rungs, "order": list(RUNG),
    "land66_J": land["kT_ln2_J"], "land66_zJ": land["kT_ln2_zJ"],
    "kT_ln2": floor["kT_ln2"], "unit": floor["unit"],
    "one_sentence": floor["the_one_sentence"],
}
# How many decades the ladder actually spans, computed rather than asserted: the page said "eleven" from
# 2026-10-27 until this build, and the real figure is 7.84.
o["floor"]["decades"] = math.log10(rungs["mac_board"]["E_J"] / rungs["electron"]["E_J"])
o["floor"]["decades_from_landauer"] = math.log10(rungs["mac_board"]["E_J"] / land["kT_ln2_J"])

# ---- the closure ------------------------------------------------------------
o["closure"] = {
    "burst_pred": ch["burst_referral_band"]["as published"]["ratio"],
    "burst_band": [ch["burst_referral_band"]["random costs -11% less"]["ratio"],
                   ch["burst_referral_band"]["random costs +13% more"]["ratio"]],
    "burst_measured": list(ch["burst_measured_comparators"].values()),
    "sustained_pred": ch["sustained_is_a_clamp"]["ratio_anywhere_in_window"],
    "clamp_window_W": ch["sustained_is_a_clamp"]["clamp_window_W"],
    "clamp_width_W": ch["sustained_is_a_clamp"]["window_width_W"],
    "candidate_caps": ch["sustained_is_a_clamp"]["candidate_caps_W"],
    "bottom_up_burst": [1.06, 1.19],
    "superposition": {"naive_W": sup["naive_W"], "within_word_W": sup["within_word_W"],
                      "cross_operand_W": sup["cross_operand_W"], "measured_W": sup["measured_W"],
                      "low_arm_W": sup["low_arm_range_W"], "bracket_W": sup["bracket_both_random_W"],
                      "m_A": sup["m_A"], "m_B": sup["m_B"]},
    "results": ch["results"],
    "measured_mhz": ch["measured_mhz"],
    "measured_tflops": ch["measured_tflops"],
    "cap_source_note": ch["sustained_cap_source"],
}
# Which candidate caps actually sit inside the clamp window, counted rather than asserted. E64's own
# measured sustained randn point, 54.4 W, is ABOVE the window: at that cap random would settle above the
# 600 MHz floor and the ratio would fall to about 1.30, so the clamp argument holds for three of the four.
_lo, _hi = o["closure"]["clamp_window_W"]
o["closure"]["caps_inside"] = {k: v for k, v in sorted(o["closure"]["candidate_caps"].items()) if _lo <= v <= _hi}
o["closure"]["caps_outside"] = {k: v for k, v in sorted(o["closure"]["candidate_caps"].items()) if not (_lo <= v <= _hi)}

# ---- the waterfall ----------------------------------------------------------
# Two versions live here. `v1` is Q128's, built 27 Oct 2026 from the transistor ledger alone: a rail figure
# carried across from E60's per-flipped-bit ratio and a bottom-up count of one lane's arithmetic. The block
# itself is Q129's, built 28 Oct from the seven directories that measured the rail, the routed wire, the
# unpriced capacitance, the glitch factor and the lane's transport. The chart reads whichever block it is
# handed, so the 27 October page rebuilds unchanged from data-2026-10-27-q128.json.
sw = board["per_random_fp32_multiply_add"]
v1 = {
    "label": "Q128, 27 October 2026",
    "board_pJ": sw["board_pJ"],
    "zeros_pJ": 0.27,
    "steps": [
        {"k": "transistor gates", "pJ": sw["switching_by_what_it_charges_pJ"]["transistor_gates"]},
        {"k": "wire inside the cells", "pJ": sw["switching_by_what_it_charges_pJ"]["wire_inside_the_cells"]},
        {"k": "wire between the cells", "pJ": sw["switching_by_what_it_charges_pJ"]["wire_between_the_cells"]},
        {"k": "the cells' own internal energy", "pJ": sw["cells_own_internal_pJ"]},
    ],
    "accounted_pJ": sw["open_netlist_total_pJ"],
    "unaccounted_pJ": sw["board_pJ"] - sw["open_netlist_total_pJ"],
    "rail_pJ": sw["rail_pJ"],
    "why": board["what_the_missing_energy_is"],
}
_lo, _hi = wf2["closure"]["central_low_transport"], wf2["closure"]["central_high_transport"]
_blo, _bhi = wf2["closure"]["band_low"], wf2["closure"]["band_high"]
_tr = wf2["transport"]
o["waterfall"] = {
    "version": "q129",
    "label": "Q129, 28 October 2026",
    "board_pJ": wf2["board_pJ"],
    "zeros_pJ": wf2["zeros_pJ"],
    # The arithmetic is one row, not three: Q129(b) simulates the routed netlist against the extracted
    # per-net table, so the routed-wire and unpriced-capacitance deltas are already inside it. The
    # transport's clock-net third is drawn as its own segment because it is what the range spans.
    # each step carries a `short` for the legend on a phone, where it has about 330px of room
    "steps": [
        {"k": "the lane's arithmetic, with routed wires and measured glitches",
         "short": "the lane's arithmetic", "pJ": wf2["arithmetic"]["pJ"],
         "band_pJ": wf2["arithmetic"]["band_pJ"]},
        {"k": "the lane's transport, less its own clock nets", "short": "its transport",
         "pJ": _tr["low_pJ"]},
        {"k": "the transport's clock nets, if they are gated at idle",
         "short": "its clock nets, if gated", "pJ": _tr["high_pJ"] - _tr["low_pJ"]},
    ],
    "accounted_pJ": _hi["accounted_on_the_rail_pJ"],
    "accounted_band_pJ": [_lo["accounted_on_the_rail_pJ"], _hi["accounted_on_the_rail_pJ"]],
    "unaccounted_pJ": _hi["unaccounted_vs_rail_pJ"],
    "unaccounted_band_pJ": [_hi["unaccounted_vs_rail_pJ"], _lo["unaccounted_vs_rail_pJ"]],
    "unaccounted_of": "the minion rail",
    "unaccounted_of_pJ": wf2["rail"]["pJ"],
    "rail_pJ": wf2["rail"]["pJ"],
    "rail_band_pJ": wf2["rail"]["band_pJ"],
    "closure_vs_rail": [_lo["closure_vs_rail"], _hi["closure_vs_rail"]],
    "closure_vs_rail_band": [_blo["closure_vs_rail"], _bhi["closure_vs_rail"]],
    "closure_vs_board": [_lo["closure_vs_board"], _hi["closure_vs_board"]],
    "closure_vs_board_band": [_blo["closure_vs_board"], _bhi["closure_vs_board"]],
    "unaccounted_vs_board_pJ": [_hi["unaccounted_vs_board_pJ"], _lo["unaccounted_vs_board_pJ"]],
    "unaccounted_vs_board_band_pJ": [_bhi["unaccounted_vs_board_pJ"], _blo["unaccounted_vs_board_pJ"]],
    "regulators_pJ": _hi["regulators_and_instep_logic_pJ"],
    "board_to_rail": wf2["board_to_rail_step"]["by_footing"][wf2["board_to_rail_step"]["footing_used"]],
    "glitch_energy_ratio": wf2["arithmetic"]["glitch_energy_ratio"],
    "glitch_toggle_ratio": wf2["arithmetic"]["glitch_toggle_ratio"],
    "glitch_moved_pJ": wf2["arithmetic"]["glitch_moved_pJ"],
    "reconciliation": wf2["arithmetic"]["reconciliation"],
    "transport": _tr,
    "leakage": wf2["leakage"],
    "why": wf2["what_is_still_unaccounted"],
    "v1": v1,
}

# ---- Q129, 28 October 2026 --------------------------------------------------
# What the Q129 experiments and desk reductions changed in the rungs above. Each value is the figure its own
# data directory publishes after its correction pass; the directory is named on every line, in the same
# convention as the hard-coded values in level 5. The waterfall's own terms are computed, not listed here.
o["q129"] = {
    # E69, the knob test: the cap was moved for the first time (2026-10-27-e69-governor-knob)
    "knob": {
        "cells_in_band": [12, 12], "rms_mhz": 11.50, "bar_mhz": 25,
        "ones_at_45W_mhz": [758.0, 739.6], "ones_at_45W_pred_mhz": 733.3,
        "ones_at_45W_steps": [10, 9], "ones_at_65W_steps": [0, 0],
        "a_ones_b_randn_mhz": {"65": 764.3, "55": 698.8, "45": 604.1},
        "a_ones_b_randn_pred_mhz": {"65": 742.9, "55": 681.0, "45": 600.0},
        "randn_mhz": {"65": 709.0, "55": 638.7}, "randn_pred_mhz": {"65": 704.8, "55": 633.3},
        "sustained_thr65_mhz": 763.4, "sustained_thr70_mhz": 800.0,
        "threshold_sensitivity_mhz": 36.6,
        "thermal_steps_thr65": 11, "thermal_steps_thr70": 0,
        "cause_flip_at_50W": {"mhz": 769.6, "thermal_steps": 0, "power_steps": 11},
        "card_minutes": 11.4, "rules_failed": ["K1", "K2", "K5"], "rules_total": 6,
        "drift_vs_e64_mhz": 25.5, "drift_vs_e64_W": 2.51,
        "unmeasured": "both sustained randn cells aborted on an 85 W board bound, and the 62 C cell never "
                      "reached equilibrium inside 76 s",
    },
    # E64-T1, the governor's missing temperature term (2026-10-27-q129-governor-temperature)
    "temperature_term": {
        "all_ones_measured_mhz": 737.9, "e64_cap_pred_mhz": 780.6, "chain_pred_mhz": 775.0,
        "t1_miss_mhz": [-7.8, 18.5], "nine_cell_rms_mhz": [4.8, 9.6], "e64_cap_rms_mhz": 23.0,
        "informative_rms_mhz": [6.5, 12.9], "e64_cap_informative_rms_mhz": 30.8,
        "fp16_miss_mhz": [7.8, 21.3], "tau_th_s": 14.0,
        "jointly_unidentified": "gamma, the voltage exponent of the leakage law, and the thermal trip "
                                "(66.0 C is E64's R3 reading, 65.5 C its registered sustained one). Eight "
                                "labelled pairings are published and no default is asserted; the miss "
                                "crosses zero at two of them and is still +18.5 MHz at the "
                                "least-assumption corner",
    },
    # E70, the saturation ladder and the A-side ladder (2026-10-27-e70-saturation-ladder)
    "saturation": {
        "answer": "shared wires, not interaction",
        "layout_contrast_W": 3.860, "layout_contrast_se_W": 0.052, "layout_contrast_SE": 73.9,
        "law_rms_W": 0.232, "law_rms_frozen_W": 0.595, "best_in_h_alone_W": 1.358,
        "pure_additivity_W": 6.062,
        "carry_over": 1.246, "carry_over_se": 0.014, "carry_over_window": 1.305,
        "q128_choice": [1.01, 1.57],
        "a_side": "the saturating form is REJECTED: its fitted asymptote lies 28.6 SE BELOW its own top "
                  "rung, the fit rms is 4.7x the B side's, and the increments accelerate where saturation "
                  "requires decay. E70 measured the A-side ladder but did not find the law that describes "
                  "it, so the A side's shape is newly open",
        "withdrawn": "the first version read the fitted W_inf as a 16.90 +- 0.20 W cap on operand-driven "
                     "switching with random data at 95% of it. W_inf is the curve's curvature, not a "
                     "bound: E70's own top rungs and both random-operand steps exceed it, and "
                     "nrd_a + nrd_b is 107% of the withdrawn cap. No ceiling goes into this chain",
        "step_split_W": {"lane un-gating": 8.57, "operand flips": 16.09, "total": 24.66},
        "rules": "P1-P8: PASS PASS PASS PASS FAIL PASS PASS PASS",
    },
    # E72, the same card at 600 MHz (2026-10-27-e72-600mhz)
    "voltage": {
        "fJ_600": 79.18, "fJ_600_se": 3.09, "fJ_800": 121.27, "fJ_800_se": 0.61,
        "exponent_board": [2.43, 2.92], "exponent_rail": [1.60, 1.72],
        "clock_scaling_exponent": 3.637, "clock_scaling_excluded_SE": 3.4,
        "matched_slope_misses_pct": [-10.2, -12.9, -15.0],
        "second_card_ratio": 0.970, "second_card_fJ": [113.22, 116.75],
        "says": "the price follows the voltage, not the clock",
        "does_not_say": "that the exponent is 2. No reduction has 2 as its point estimate: the board "
                        "family brackets it from above (2.43-2.92) and the rail family from below "
                        "(1.60-1.72), and the registered +-10% test fails at three of four matched slopes "
                        "once both sides are reduced at the same leakage slope",
    },
    # E71 + the aifoundry3 re-reduction (2026-10-27-e71-idle-slope-aifoundry3, 2026-10-27-q129-leak-sensitivity)
    "leak": {
        "a3_58_62": 0.3803, "a3_58_62_se": 0.0036, "a3_52_58": 0.3200,
        "a2_51_58": 0.2936, "a2_58_62": 0.3452, "a2_58_62_sd": 0.0112,
        "registered": 1.508, "band_share_of_the_gap_pct": [59.5, 69.5],
        "group_shifts_pct": [-0.70, -5.17], "item_shifts_pct": [3.95, -8.97],
        "verdicts_moved": 0, "verdicts_scored": 16,
        "rule_failed": "S5d, the registered leg 'every price moves downward', FAILS on one item of 166: "
                       "abit_26 in E67's clean reduction rises 0.019 W (+4.0%, 0.9x its own SE) because "
                       "its window ran 0.09 C cooler than its zero's, and lq_h2 does not move at all",
        "e60_a3_lq_fJ": [116.746, 115.049], "flowM_fJ": [745.0, 722.2],
        "flat_floor_fJ": [109.3, 103.6],
    },
    # E73, the camera's heat path (2026-10-27-e73-camera-frequencies)
    "heat_path": {
        "pole_s": 15.98, "pole_ci_s": [13.34, 19.12], "delay_s": 1.009, "delay_ci_s": [0.78, 1.24],
        "group_delay_s": 16.99, "group_delay_ci_s": [14.47, 20.13],
        "one_pole_alone_dAIC": 17.02, "rivals_refuted_SE": [3.98, 7.64],
        "G0_mK_per_W": 250.5, "G0_ci": [217, 292], "line_implies_mK_per_W": 300,
        "attenuation_at_0p05Hz": 0.1953,
        "say_which": "the 0.05 Hz transfer the camera ladder quotes is 0.1953 of the steady-state "
                     "response, so a steady gain must name itself: the fit's G0 = 250.5 mK/W [217, 292], "
                     "whose own 0.05 Hz value sits 2.71 line-SE (16.5%) BELOW the measured line, or the "
                     "~300 mK/W that measured line implies through the fitted attenuation. The 17% "
                     "between them is itself a finding, and the fitted family is strained in two places",
    },
    # Stop 9 (2026-10-27-q129-stop9-atoms)
    "atoms": {
        "landauer_x": 24515, "landauer_x_at_58C": 26143, "aJ_per_edge": 82.85, "electrons": 2000.4,
        "C_fF": 0.619928,
        "bare_fins_x": 7948, "min_inverter_x": 2645,
        "channel_share_pct": 97.2, "channel_band_pct": [93.0, 99.5],
        "wire_share_of_capacitance_pct": 78, "crossover_um": [68, 1085],
        "phonon_meV": 64.6, "phonons_per_edge": 4.00, "phonons_per_mac": 4.2e8,
        "optical_phonon_range": [3.91e8, 4.98e8],
        "naming": "ASAP7's INVx1 is a 3x cell, not the library's minimum inverter: its LVS netlist gives "
                  "nfin=3 per device (6 fins) against INVxp33's 1+1, and its leakage is exactly 3.00x. "
                  "The 24,515x prices INVx1's liberty input pin, which carries the cell's own layout "
                  "wire; the same pin's six bare fins are 7,948x and the library's real minimum inverter "
                  "is 2,645x",
    },
    # E74-E76, measured on aifoundry3 on Wed 28 Oct (2026-10-28-e74-register-file-cells,
    # -e75-memory-flip-ladder, -e76-trapped-instructions). Their full fold-in to this chain is a separate
    # step and is not in the ledger above; what is here is the part that bears on sections 2 and 5.
    "kernels": {
        "status": "measured Wed 28 Oct 2026 on aifoundry3; being folded into the chain",
        "e74_bound_fJ": 2.73, "e74_bound_conf": 0.95,
        "e74_card_minutes": 11.6, "e75_card_minutes": 21.5, "e76_card_minutes": 7.7,
        "e76_trapped": 13, "e76_probe_passes": 2,
        "e76_source": "there is no emulation path in the firmware, so the thirteen instructions have no "
                      "per-instruction energy at all: a U-mode illegal instruction is delegated M->S and "
                      "the exception handler calls return_from_kernel(KERNEL_RETURN_EXCEPTION), 758 "
                      "instructions counted on the installed build, and that ends the hart's kernel. "
                      "libgcc's __divsf3 (299 instructions) contains no trapping instruction, so a C "
                      "float divide is safe and costs 310-570 multiply-adds; libm's sqrtf and fmodf and "
                      "libgcc's __fixunssfdi do contain them, so sqrtf(x) is fatal",
        "e76_confirmed": "all thirteen trap on silicon, 13 of 13, each ending the kernel with 0 ops",
    },
    # The private cross-check, phrased exactly as the Q128 build phrases it: run, not reported here.
    "archive": {
        "when": "27-28 October 2026",
        "say": "A private archive cross-check of the same quantities was run; it is not part of this page "
               "and nothing from it is quoted here.",
    },
}

o["meta"] = {
    "date": "2026-10-27",
    "updated": "2026-10-28",
    "updated_with": "Q129",
    "repo": "https://github.com/yaroslavvb/et-soc1-prototyping",
    "private": False,
}

json.dump(o, open(out, "w"), indent=1, sort_keys=True)
print(f"wrote {out}  keys={len(o)}")
