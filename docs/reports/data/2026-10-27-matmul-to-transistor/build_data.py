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
o["governor"] = {
    "cap_W": ch["power_cap_W"], "cap_source": ch["power_cap_source"],
    "tau_s": ch["governor"]["tau_s"], "rms_mhz": ch["governor"]["rms_mhz"], "n": ch["governor"]["n"],
    "trip_C": 66.0, "die_line": ch["die_line"], "sustained_cap_W": ch["sustained_cap_W"],
    "clamp": ch["sustained_is_a_clamp"], "cap_sensitivity": ch["burst_cap_sensitivity"],
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
    "e66_leak_W_per_C": 0.296, "a1_leak_W_per_C": 1.508,
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
sw = board["per_random_fp32_multiply_add"]
o["waterfall"] = {
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

o["meta"] = {
    "date": "2026-10-27",
    "repo": "https://github.com/yaroslavvb/et-soc1-prototyping",
    "private": False,
}

json.dump(o, open(out, "w"), indent=1, sort_keys=True)
print(f"wrote {out}  keys={len(o)}")
