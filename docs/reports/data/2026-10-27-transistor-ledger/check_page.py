#!/usr/bin/env python3
"""Q128(d): assert the numbers printed in README.md against the two JSONs.

  check_page.py <this directory>

Exits 0 when every figure on the page matches the data it came from, 1
otherwise.  It exists because the page's first version mixed two energy
conventions -- a rung priced per rise sitting in a column of rungs priced per
toggle -- which no single file was wrong about.
"""
import json
import sys

D = sys.argv[1]
L = json.load(open(D + "/transistor-ledger.json"))
S4 = json.load(open(D + "/one-switch4.json"))
r = L["the_floor"]["rungs"]
sg = L["one_physical_net_toggle"]["signal_nets"]
ck = L["one_physical_net_toggle"]["clock_nets"]
up = L["up_to_the_board"]["per_random_fp32_multiply_add"]
ok = True


def chk(label, got, want, tol=5e-3):
    global ok
    good = abs(got - want) <= tol * max(abs(want), 1e-30)
    ok &= good
    print(("  ok  " if good else "  FAIL") + f" {label}: page {want}  json {got:.6g}")


def chk_le(label, got, bound):
    global ok
    ok &= got <= bound
    print(("  ok  " if got <= bound else "  FAIL")
          + f" {label}: page says <= {bound}  json {got:.6g}")


print("README section 4 ladder, per rise:")
chk("signal rise fJ", r["one rise (0 -> 1) of an average signal net"]["E_J"] * 1e15, 0.5969)
chk("signal rise electrons", r["one rise (0 -> 1) of an average signal net"]["electrons"], 7206)
chk("signal rise xLandauer", r["one rise (0 -> 1) of an average signal net"]["over_Landauer_at_66C"],
    1.8e5, 0.03)
chk("clock rise fJ", r["one rise (0 -> 1) of an average clock net"]["E_J"] * 1e15, 2.083)
chk("clock rise electrons", r["one rise (0 -> 1) of an average clock net"]["electrons"], 25149)
chk("clock rise xLandauer", r["one rise (0 -> 1) of an average clock net"]["over_Landauer_at_66C"],
    6.4e5, 0.01)
print("unchanged rungs:")
chk("gate isolated aJ", r["one minimum device's gate, isolated (mean of the four bias cases)"]["E_J"] * 1e18, 8.94)
chk("gate pin aJ", r["one gate pin of the cells this unit drives"]["E_J"] * 1e18, 57.3)

print("\nREADME section 2:")
chk("signal C fF", sg["C_total_fF"], 2.233)
chk("clock C fF", ck["C_total_fF"], 7.794)
chk("fins x 108 / rise electrons = transistor share",
    sg["transistor_fins_behind_them"] * 107.95469817717992 / (2 * sg["electrons_per_toggle"]),
    sg["share_transistor"], 1e-6)
chk("per toggle x toggles == per rise x rises (all nets, pJ)",
    2 * 0.2813570 * (up["signal_toggles_per_muladd"] / 2) * 1e-3, 1.019, 2e-3)

print("\nREADME section 3:")
chk("capacitance priced share", up["capacitance_priced"], 0.505, 2e-3)
chk("unpriced fF", 47093.20546652248 * (1 - up["capacitance_priced"]), 23331, 1e-4)
chk("priced fF", 47093.20546652248 * up["capacitance_priced"], 23762, 1e-4)

print("\nREADME section 1, the bracketed sweep:")
for v, want_min, want_max in (("0p517", 300, 0.0749), ("0p700", 50, 0.5882)):
    s = S4[v]
    chk(f"{v} cheapest edge ps", s["cheapest_edge_ps"], want_min, 0)
    chk(f"{v} max excess share", s["max_excess_share"], want_max, 2e-3)
    chk(f"{v} bracketed", 1.0 if s["minimum_is_bracketed"] else 0.0, 1.0, 0)
    chk_le(f"{v} worst vs first sweep",
           s["against_the_first_sweep"]["worst_relative_difference"], 5e-6)
chk("0.517 excess at 1 ps", S4["0p517"]["by_input_edge_ps"]["1"]["excess_share"], 0.0304, 5e-3)
chk("0.517 excess at 50 ps", S4["0p517"]["by_input_edge_ps"]["50"]["excess_share"], 0.0128, 5e-3)
chk("0.517 minimum fJ", S4["0p517"]["E_switching_at_the_minimum_fJ"], 0.5905, 1e-3)
chk("0.700 at 200 ps, excess fJ",
    S4["0p700"]["by_input_edge_ps"]["200"]["E_switching_per_cycle_fJ"]
    - S4["0p700"]["E_switching_at_the_minimum_fJ"], 0.0620, 5e-3)
sl = S4["0p517"]["excess_at_the_design_s_own_edge"]["output_slew"]
chk("slew rise ps", sl["rise_20_80_ps"], 23.4, 1e-3)
chk("slew fall ps", sl["fall_80_20_ps"], 17.0, 3e-3)
chk("linear-ramp equivalent of the rise", sl["rise_20_80_ps"] / 0.6, 39, 5e-3)
chk("linear-ramp equivalent of the fall", sl["fall_80_20_ps"] / 0.6, 28, 2e-2)
chk("leak lo nA", S4["0p517"]["static_leakage"]["lo"]["I_nA"], 0.035, 2e-2)
chk("leak hi nA", S4["0p517"]["static_leakage"]["hi"]["I_nA"], 0.043, 2e-2)
chk("leak fJ over the window",
    S4["0p517"]["by_input_edge_ps"]["1"]["leakage_in_the_window_fJ"], 0.00028, 2e-2)

print("\nALL OK" if ok else "\nSOMETHING FAILED")
sys.exit(0 if ok else 1)
