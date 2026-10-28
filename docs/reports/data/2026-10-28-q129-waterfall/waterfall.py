#!/usr/bin/env python3
"""Q129's version of the matmul-to-transistor waterfall, built bottom up from the committed Q129 data.

    waterfall.py <repo root> <out.json>

Q128's waterfall (27 Oct 2026) had two bars and one step: a 5.783 pJ board figure, a 4.337 pJ rail figure
carried across from E60's per-flipped-bit ratio, and a 1.946 pJ bottom-up count of one lane's arithmetic on
the placed open netlist. This script rebuilds both halves from the seven Q129 directories that measured
them, and keeps every term's provenance in the output so the page cannot assert a number no directory wrote.

The one thing a reader must not do with these rows is add them all up. Three of them price the SAME
capacitance at three stages of knowledge, and only the last is used:

  * the routed wire (Q129(a), 2026-10-27-q129-routed-netlist) re-prices the between-cell wire from an
    extraction instead of a global-route Steiner estimate:            -0.137 pJ
  * the unpriced capacitance (Q129, 2026-10-27-q129-unpriced-capacitance) prices the nets the clock-tree
    build and the timing repair created after the simulation:         +0.101 pJ
  * the measured glitch factor (Q129(b), 2026-10-27-q129-glitch) simulates the ROUTED netlist against the
    extracted per-net table, so it prices 100% of the extracted farads AND the glitches:  its zero-delay
    figure already contains both of the rows above.

So the ledger's arithmetic row is Q129(b)'s waterfall (C) alone, and the two rows above are published as
the reconciliation that shows (C) is the same measurement reached by a different road: 1.9465 - 0.137 +
0.101 = 1.910 pJ against (C)'s own measured zero-delay 1.925 pJ, 0.015 pJ apart.

The transport row (Q129(scope), 2026-10-27-q129-ledger-scope) is NOT inside (C): it is a second netlist,
the lane's register files, operand bus, result path and control, which the arithmetic netlist does not
contain. It is a range, not a number, and the range is the 0.223 pJ its own clock nets cost: whether the
lane's register-file clock branches are gated when the card idles decides whether that third of its
zero-operand floor is inside the idle the board figure subtracts. The glitch factor is NOT applied to it:
that netlist has no detailed route, no SDF and 37.0% of its capacitance priced, so no glitch factor was
measured on it, and x1.33 there is an assumption, not a measurement.

Leakage is not a row at all. "Over idle" is already a leakage-corrected quantity: E38's registered metric
subtracts leak x (t_early - t_launch) from each window. What Q129 adds is the slope's own band, which the
rail ledger publishes as a sensitivity -- and E71's measurement that a leakage slope is not a card
constant but rises with die temperature, so a slope quoted without its band is ambiguous.
"""
import json
import sys

root, out = sys.argv[1], sys.argv[2]
D = f"{root}/docs/reports/data"


def j(p):
    return json.load(open(f"{D}/{p}"))


led = j("2026-10-27-transistor-ledger/transistor-ledger.json")
rail = j("2026-10-27-q129-rail-ledger/rail-ledger.json")
glit = j("2026-10-27-q129-glitch/glitch_mixed_full.json")
cap = j("2026-10-27-q129-unpriced-capacitance/q129-unpriced-capacitance.json")
scope = j("2026-10-27-q129-ledger-scope/ledger-scope.json")
route = j("2026-10-27-q129-routed-netlist/caps_spef_mixed.json")
e71 = j("2026-10-27-e71-idle-slope-aifoundry3/slopes.json")
a2_58 = j("2026-10-27-e71-idle-slope-aifoundry3/aifoundry2-58-62.json")

q128 = led["up_to_the_board"]["per_random_fp32_multiply_add"]
BOARD = q128["board_pJ"]
assert abs(BOARD - 5.783) < 1e-9, BOARD

# ---------------------------------------------------------------- the rail ---
# The three footings differ in how E38's registered leakage correction is distributed over the rows; the
# choice between them is the single largest uncertainty in the board-to-rail step.
F = rail["footings"]["two_card_mean"]["launch"]
foot = {name: F[name]["on_q128_board_pJ"] for name in F}
central, lower, upper = "drift_split", "uncorrected", [k for k in foot if k not in
                                                       ("drift_split", "uncorrected")][0]
RAIL = foot[central]["minion"]
rail_band = sorted(foot[k]["minion"] for k in foot)

step = {}
for name in foot:
    r = foot[name]
    step[name] = {
        "regulators_and_instep_logic_pJ": r["delivery_and_instep"],
        "sram_rail_pJ": r["sram"], "noc_rail_pJ": r["noc"],
        "fit_residual_pJ": r["unattributed"],
        "board_to_rail_pJ": BOARD - r["minion"],
        "minion_pJ": r["minion"], "minion_over_board": r["minion"] / BOARD,
    }
    # the four rows sum to the step exactly, by construction of the fit
    s = sum(r[k] for k in ("delivery_and_instep", "sram", "noc", "unattributed"))
    assert abs(s - (BOARD - r["minion"])) < 2e-9, (name, s, BOARD - r["minion"])

# -------------------------------------------------- the lane's arithmetic ----
# Q129(b)'s waterfall (C): the ROUTED netlist simulated with and without the extracted SDF, priced on the
# extracted per-net capacitance, so 100% of the extracted farads and every glitch are in one measurement.
U = glit["scopes"]["unit"]
INT = {"zero": 0.4127, "timed": 0.6933}   # summary.txt (C): the cells' internal energy, scaled x1.68
arith = {}
for k in ("k0", "k1", "k2"):
    arith[k] = {
        "switching_zero_pJ": U[k]["zero_pJ_per_muladd"],
        "switching_timed_pJ": U[k]["timed_pJ_per_muladd"],
        "internal_zero_pJ": INT["zero"], "internal_timed_pJ": INT["timed"],
        "zero_delay_total_pJ": U[k]["zero_pJ_per_muladd"] + INT["zero"],
        "total_pJ": U[k]["timed_pJ_per_muladd"] + INT["timed"],
        "glitch_energy_ratio": U[k]["glitch_energy_ratio"],
    }
ARITH = arith["k1"]["total_pJ"]
arith_band = [arith["k0"]["total_pJ"], arith["k2"]["total_pJ"]]

# the reconciliation: Q128's own ledger walked forward by the two deltas that (C) subsumes
WIRE_DELTA = -0.1371          # Q129(a) summary.txt, mixed netlist at Miller k=1 (0.590 -> 0.453 pJ)
recon = {
    "q128_bottom_up_pJ": q128["open_netlist_total_pJ"],
    "routed_wire_delta_pJ": WIRE_DELTA,
    "unpriced_capacitance_delta_pJ": cap["waterfall"]["moved_from_unaccounted_to_accounted_pJ"],
    "walked_forward_pJ": (q128["open_netlist_total_pJ"] + WIRE_DELTA
                          + cap["waterfall"]["moved_from_unaccounted_to_accounted_pJ"]),
    "measured_zero_delay_pJ": arith["k1"]["zero_delay_total_pJ"],
}
recon["they_agree_to_pJ"] = recon["measured_zero_delay_pJ"] - recon["walked_forward_pJ"]
assert abs(recon["they_agree_to_pJ"]) < 0.02, recon

# ----------------------------------------------------- the lane's transport --
G = scope["gap"]
_rf = [p for p in scope["per_part"] if p["part"].startswith("VPU register file array")][0]
_bus = [p for p in scope["per_part"] if p["part"].startswith("operand bus")][0]
transport = {
    "low_pJ": G["transport_excl_clock_nets_with_internal_pJ_per_mac"],
    "high_pJ": G["transport_switching_plus_internal_pJ_per_mac"],
    "clock_net_pJ": G["transport_clock_net_pJ_per_mac"],
    "switching_pJ": G["transport_switching_pJ_per_mac"],
    "zero_operand_floor_pJ": G["zeros_switching_pJ_per_mac"],
    "zero_operand_share_of_transport": G["zeros_switching_pJ_per_mac"] / G["transport_switching_pJ_per_mac"],
    "zero_operand_clock_pJ": G["zeros_clock_net_pJ_per_mac"],
    "zero_operand_signal_pJ": G["zeros_signal_switching_pJ_per_mac"],
    "moves_with_the_operand_words_pJ": G["transport_data_dependent_with_internal_pJ_per_mac"],
    "register_file_model_pJ": _rf["pJ_per_mac_switching"],
    "register_file_model_zeros_pJ": _rf["pJ_per_mac_zeros"],
    "operand_bus_and_result_path_pJ": _bus["pJ_per_mac_switching"],
    "card_zeros_bound_pJ": 0.27,
    "why_a_range": "the 0.223 pJ its own clock nets cost: whether the lane's register-file clock branches "
                   "are gated when the card idles decides whether that third of the zero-operand floor is "
                   "inside the idle E38 subtracts. Unmeasured on silicon.",
    "why_no_glitch_factor": "that netlist has no detailed route, no SDF and 37.0% of its capacitance "
                            "priced, so no glitch factor was measured on it. x1.33 there would be an "
                            "assumption: it would put the ledger at 4.38-4.68 pJ, 92-98% of the rail, on "
                            "top of a register-file row the card's own zeros measurement already "
                            "contradicts.",
    "the_ceiling_is_violated": "one lane's transport model costs 0.654 pJ in the zeros stimulus where the "
                               "WHOLE BOARD costs 0.27 pJ per multiply-add over idle (E38, per card "
                               "0.163 / 0.403 / 0.251), so the 0.4815 pJ register-file row over-prices and "
                               "a true accounting sits BELOW the bottom of every range here.",
}

# ------------------------------------------------------------- the closure ---
def closure(ar, tr, rl, dl):
    acc = ar + tr
    return {
        "arithmetic_pJ": ar, "transport_pJ": tr, "accounted_on_the_rail_pJ": acc,
        "rail_pJ": rl, "unaccounted_vs_rail_pJ": rl - acc, "closure_vs_rail": acc / rl,
        "regulators_and_instep_logic_pJ": dl,
        "accounted_vs_board_pJ": acc + dl, "closure_vs_board": (acc + dl) / BOARD,
        "unaccounted_vs_board_pJ": BOARD - acc - dl,
        "bottom_up_only_closure_vs_board": acc / BOARD,
    }


DL = step[central]["regulators_and_instep_logic_pJ"]
cl = {
    "central_low_transport": closure(ARITH, transport["low_pJ"], RAIL, DL),
    "central_high_transport": closure(ARITH, transport["high_pJ"], RAIL, DL),
    "band_low": closure(arith_band[0], transport["low_pJ"], max(rail_band),
                        min(step[k]["regulators_and_instep_logic_pJ"] for k in step)),
    "band_high": closure(arith_band[1], transport["high_pJ"], min(rail_band),
                         max(step[k]["regulators_and_instep_logic_pJ"] for k in step)),
}

# ------------------------------------------------------------------ leakage --
S = rail["footings"]["leak_slope_sensitivity"]
leak = {
    "note": "not a row. 'Over idle' is already leakage-corrected: E38's registered metric subtracts "
            "leak x (t_early - t_launch) from each window, so the window's own die heating is out of the "
            "board figure before anything here divides it. What Q129 adds is the slope's band.",
    "rail_at_each_slope_pJ": {k: v["minion_pJ_on_q128_board"] for k, v in S.items()
                              if isinstance(v, dict)},
    "slopes_used_W_per_C": {k: v["leak_w_per_c"] for k, v in S.items() if isinstance(v, dict)},
    "sensitivity_note": S["note"],
    "measured_idle_slopes_W_per_C": {
        "aifoundry2, 51-58 C (E66)": 0.2936, "aifoundry2, 58-62 C (E71 re-fit)": 0.3452,
        "aifoundry3, 52-58 C (E71)": 0.3200, "aifoundry3, 58-62 C (E71)": 0.3803,
    },
    "aifoundry2_58_62_spread": {"sd": 0.0112, "n_passes": 18,
                                "per_pass_range": [0.3183, 0.3613]},
    "aifoundry3_58_62_se": 0.0036,
    "registered_estimator_W_per_C": 1.508,
    "it_is_not_a_card_constant": "a slope rises about 0.009 W/C per C of die temperature on aifoundry2 and "
                                 "about 0.011 on aifoundry3 over 51-65 C, so a correction quoted without "
                                 "its band is ambiguous at the 20-30% level -- larger than the 10% "
                                 "card-to-card difference it is usually invoked for. About three fifths of "
                                 "the gap between E66's 0.2936 and E71's 0.3803 is the temperature band, "
                                 "not the card (69.5% measured the other way round).",
}
_rails = list(leak["rail_at_each_slope_pJ"].values())
leak["spread_pJ"] = max(_rails) - min(_rails)

# the 58-62 C medians this block quotes, re-derived from E71's own per-pass fits
_a3 = sorted(p["fits"]["58-62"]["slope_w_per_c"] for p in e71["passes"].values()
             if p["fits"]["58-62"]["ok"])
leak["aifoundry3_58_62_remeasured_median"] = _a3[len(_a3) // 2] if len(_a3) % 2 else \
    0.5 * (_a3[len(_a3) // 2 - 1] + _a3[len(_a3) // 2])
assert abs(leak["aifoundry3_58_62_remeasured_median"] - 0.3803) < 5e-4, _a3
_a2 = sorted(p["fits"]["58-62"]["slope_w_per_c"] for p in a2_58["passes"].values()
             if p["fits"]["58-62"]["ok"])
leak["aifoundry2_58_62_remeasured_median"] = _a2[len(_a2) // 2] if len(_a2) % 2 else \
    0.5 * (_a2[len(_a2) // 2 - 1] + _a2[len(_a2) // 2])
leak["aifoundry2_58_62_spread"]["per_pass_range"] = [min(_a2), max(_a2)]
leak["aifoundry2_58_62_spread"]["n_passes"] = len(_a2)

o = {
    "what": "Q129's waterfall for one random fp32 multiply-add, over idle: the board-to-rail step measured "
            "instead of carried across, and the bottom-up count rebuilt with routed wires, all of the "
            "capacitance, the measured glitch factor and the lane's transport.",
    "version": "q129",
    "built": "2026-10-28",
    "supersedes": "the waterfall of 2026-10-27 (Q128): rail 4.337 pJ carried from E60's per-flipped-bit "
                  "ratio, bottom-up 1.9465 pJ, unaccounted 3.8365 pJ against the board",
    "board_pJ": BOARD,
    "zeros_pJ": 0.27,
    "rail": {"pJ": RAIL, "band_pJ": [min(rail_band), max(rail_band)],
             "ratio": RAIL / BOARD, "ratio_band": [min(rail_band) / BOARD, max(rail_band) / BOARD],
             "per_card_pJ": {k: v for k, v in
                             F[central]["per_card_minion_pJ_on_q128_board"].items()},
             "footing_used": central, "q128_carried_pJ": 4.33725,
             "q128_stated_ratio_range": [0.70, 0.89]},
    "board_to_rail_step": {"by_footing": step, "footing_used": central,
                           "sram_and_noc_withdrawn":
                               "the SRAM and NoC rails are withdrawn as per-MAC switching energies: their "
                               "whole window delta is their own leakage rise, 66%/61% and 100%/103% of it, "
                               "so at most 0.13 pJ together and about zero on the central footing",
                           "residual_is_consistent_with_zero":
                               "the fit's residual is 0.142 pJ central, -0.230 on the upper footing, and "
                               "negative in 12 of 16 configurations on aifoundry3"},
    "arithmetic": {"by_miller_k": arith, "pJ": ARITH, "band_pJ": arith_band,
                   "glitch_toggle_ratio": U["glitch_toggle_ratio"],
                   "glitch_energy_ratio": arith["k1"]["glitch_energy_ratio"],
                   "glitch_moved_pJ": ARITH - arith["k1"]["zero_delay_total_pJ"],
                   "clock_tree_glitch_ratio": glit["scopes"]["clock"]["glitch_toggle_ratio"],
                   "wallace_tree_energy_ratio": glit["scopes"]["wallace_tree"]["k1"]["glitch_energy_ratio"],
                   "capacitance_priced": glit["coverage"],
                   "coupling_caps_extracted": route["entries"]["coupling_entries_distinct"],
                   "reconciliation": recon,
                   "do_not_add":
                       "the routed-wire and unpriced-capacitance deltas are inside this row already: it "
                       "simulates the routed netlist against the extracted per-net table, so it prices "
                       "100% of the extracted farads. Adding them again double-counts."},
    "transport": transport,
    "closure": cl,
    "leakage": leak,
    "what_is_still_unaccounted":
        "0.58-0.81 pJ against the rail and 0.72-0.94 pJ against the board on the central footing at Miller "
        "k=1 (0.04-1.30 and 0.34-1.28 over the whole band), where Q128 had 2.39 and 3.84. Two warnings "
        "travel with it. First, the largest single row added here, the lane's transport, carries a "
        "register-file model the card's own zeros measurement already contradicts, so the remainder is "
        "larger than these numbers say by whatever that model over-prices -- E74 measured a bound on the "
        "cell bit (e_cell < 2.73 fJ, 95%) but not the array's own per-MAC energy. Second, the transport "
        "netlist is itself a floor on the three axes the arithmetic netlist has now cleared: no detailed "
        "route, no glitch measurement, 37.0% of its capacitance priced.",
    "sources": {
        "board 5.783 pJ, zeros 0.27 pJ": "E38 registered means, 3 cards (2026-10-27-transistor-ledger)",
        "rail and the board-to-rail step": "2026-10-27-q129-rail-ledger (b8b8691c)",
        "routed wire": "2026-10-27-q129-routed-netlist (273fe126, 01964253)",
        "the capacitance that was unpriced": "2026-10-27-q129-unpriced-capacitance (e7a2cbc2, 6e154623)",
        "the glitch factor and waterfall (C)": "2026-10-27-q129-glitch (4a6a840a, 2778b089)",
        "the lane's transport": "2026-10-27-q129-ledger-scope (39315c56, 936b0b88)",
        "the leakage slopes": "2026-10-27-e66-idle-long, 2026-10-27-e71-idle-slope-aifoundry3 (5db5f5d9)",
    },
}
json.dump(o, open(out, "w"), indent=1, sort_keys=True)
print(f"wrote {out}")
print(f"  rail        {RAIL:.3f} pJ  [{min(rail_band):.3f}, {max(rail_band):.3f}]  "
      f"ratio {RAIL / BOARD:.3f}")
print(f"  arithmetic  {ARITH:.3f} pJ  [{arith_band[0]:.3f}, {arith_band[1]:.3f}]  "
      f"(zero-delay {arith['k1']['zero_delay_total_pJ']:.3f}, glitch x{arith['k1']['glitch_energy_ratio']:.3f})")
print(f"  transport   {transport['low_pJ']:.3f} to {transport['high_pJ']:.3f} pJ")
for k, v in cl.items():
    print(f"  {k:24s} accounted {v['accounted_on_the_rail_pJ']:.3f} pJ = "
          f"{100 * v['closure_vs_rail']:.1f}% of the rail, "
          f"{100 * v['closure_vs_board']:.1f}% of the board with the regulators; "
          f"unaccounted {v['unaccounted_vs_board_pJ']:.3f} pJ vs the board")
print(f"  reconciliation: 1.9465 {WIRE_DELTA:+.4f} "
      f"{recon['unpriced_capacitance_delta_pJ']:+.4f} = {recon['walked_forward_pJ']:.4f} against the "
      f"measured {recon['measured_zero_delay_pJ']:.4f}, {recon['they_agree_to_pJ']:+.4f} apart")
print(f"  leakage: rail over the three slopes {leak['rail_at_each_slope_pJ']}, "
      f"spread {leak['spread_pJ']:.3f} pJ")
