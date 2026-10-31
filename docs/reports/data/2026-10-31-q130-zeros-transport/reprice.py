#!/usr/bin/env python3
"""Q130(i): re-price Q129's transport netlist on the gating the RTL actually has.

Inputs, all committed:
  - Q129's per-block gate-level switching energies,
      docs/reports/data/2026-10-27-q129-ledger-scope/power-mixed/power_gr_<pattern>.json
      and .../power-mixed-clkwide/ (the widened clock regex, which isolates the latch array's
      own gated-clock nets `clk_rf_wr[i]`, `clk_wr_data_a_n`, `enclk`);
  - its census,  .../census_mixed.json  (clock-pin capacitance per block);
  - the structural audit's toggle counts, sim/counts.txt, from sim/run.sh.

Outputs reprice.json and a table on stdout. Nothing here is measured on a card; the card
numbers quoted are E38's, through Q128's data.json.

    python3 reprice.py --q129 <dir> --counts <counts.txt> --out reprice.json

CORRECTIONS of 31 Oct 2026, same day, after review (README § Corrections has the full list):
  - the ledger now carries BOTH internal-energy conventions, because Q129's published
    1.261 / 1.484 pJ add the whole internal estimate to the switching while this script's
    `internal_ratio_used` scales it with the switching. Setting the two side by side without
    saying so was not like-for-like;
  - the clock-load breakdown gained the `vrf` wrapper's own clock pins, which were inside the
    bound but missing from the printed detail (373.9 of 421.0 fF was shown);
  - the card check carries the three registered cards' own figures, not only their mean, and the
    strict "same netlist" upper (no read-enable pin, addresses fixed) as its own reading;
  - `f_data_read`'s fallback when the bench's read tree is static is 1.0 (keep Q129's figure),
    not 0.0. On `zeros` the term it multiplies is exactly 0, so no published number moves.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os

MACS = 512          # micro-ops per op per lane; Q129's own denominator
PJ = 1e-12

# Q129's per-part table maps netlist blocks to parts of the lane's transport.
PARTS = {
    "rf_array":  ["vrf/arr"],
    "top_clock": ["(top)"],                       # plus every clknet_*, added below
    "bypass":    ["bypass"],
    "rf_bypass": ["vrf"],
    "tena":      ["tena_rf", "tena_rf/rf_buffer_array"],
    "tenb":      ["LANE_TIMA[0].tenb_rf", "LANE_TIMA[1].tenb_rf",
                  "LANE_TIMA[0].tenb_rf/rf_buffer_array", "LANE_TIMA[1].tenb_rf/rf_buffer_array"],
    "tenc":      ["tenc_rf", "tenc_rf/arr"],
    "tentmp":    ["tentmp_rf", "tentmp_rf/rf_buffer_array"],
    "ctl":       ["ctl"],
}


def load(q129, sub, pattern):
    with open(os.path.join(q129, sub, "power_gr_%s.json" % pattern)) as f:
        return json.load(f)


def part_energies(d):
    """pJ per multiply-add, by part, from a Q129 power JSON."""
    b = d["blocks"]
    out = {}
    for part, names in PARTS.items():
        out[part] = sum(b[n]["energy_J"] for n in names if n in b) / MACS / PJ
    out["top_clock"] += sum(v["energy_J"] for k, v in b.items()
                            if k.startswith("clknet_")) / MACS / PJ
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--q129", required=True)
    ap.add_argument("--counts", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    counts = {}
    for line in open(a.counts):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        pat = os.path.basename(d["tiles"]).replace(".hex", "")
        counts[(pat, d["allmadd"])] = d

    census = {v.get("path"): v for v in json.load(open(os.path.join(a.q129, "census_mixed.json")))["blocks"]}
    census_total = json.load(open(os.path.join(a.q129, "census_mixed.json")))["total"]

    res = {"source": {
        "q129_dir": "docs/reports/data/2026-10-27-q129-ledger-scope",
        "macs_per_op": MACS,
        "note": "switching energy per fp32 multiply-add, one VPU lane, ASAP7 RVT TT, 0.517 V",
        "counts_from": "sim/counts.txt, the corrected structural simulation of 31 Oct 2026",
        "sim_read_path_self_check": "every row of sim/counts.txt carries rd_chk_fail = 0: the "
                                    "read tree delivers rf[rd_addr] on all three ports every "
                                    "cycle. The first version of the simulation had an off-by-one "
                                    "in offs() and a testbench multiply-add that Verilator "
                                    "silently turned into `return c`; both are fixed and both are "
                                    "described in README § Corrections",
    }}
    chk = sum(d.get("rd_chk_fail", -1) for d in counts.values())
    if chk != 0:
        raise SystemExit("counts.txt has rd_chk_fail != 0 (sum %s): the read tree is broken" % chk)

    # ---------------------------------------------------------------- the read-port factor
    cz = counts[("zeros", 0)]
    sel_b = cz["bench"]["sel_pin_tr"]
    sel_r = cz["rtl"]["sel_pin_tr"]
    sel_p2 = cz["rtl"]["sel_pin_tr_p"][2]
    f_read_silicon = sel_p2 / sel_b          # macro honours rd_enable0/1/2 -> port 2 alone
    f_read_model = sel_r / sel_b             # latch array, no read enable, RTL addresses
    res["read_factor"] = {
        "sel_pin_transitions_bench": sel_b,
        "sel_pin_transitions_rtl_wired_latch_array": sel_r,
        "sel_pin_transitions_port2_only": sel_p2,
        "per_port_rtl_wired": cz["rtl"]["sel_pin_tr_p"],
        "f_read_silicon": f_read_silicon,
        "f_read_model_rewired": f_read_model,
        "mux_output_transitions_on_zeros": cz["bench"]["mux_out_tr"],
        "addr_bit_flips_bench": cz["bench"]["addr_tr"],
        "q129_idx_toggles_per_op": 992,
        "check": "addr_bit_flips_bench / 3 must equal Q129 sim_acct idx_toggles = 992",
    }

    # ---------------------------------------------------------------- the write-side factor
    wz = {k: cz["rtl"][k] / cz["bench"][k] if cz["bench"][k] else 0.0
          for k in ("dec_tr", "wr_clk_edges", "entry_clk_edges", "wrdata_clk_edges")}
    f_write_firstpass = wz["entry_clk_edges"]
    f_write_allmadd = (counts[("zeros", 1)]["rtl"]["entry_clk_edges"]
                       / counts[("zeros", 1)]["bench"]["entry_clk_edges"])
    res["write_factor"] = {
        "gated_uops_of_512_firstpass_is_mul": cz["gated"],
        "gated_uops_of_512_all_madd": counts[("zeros", 1)]["gated"],
        "f_write_firstpass_ungated": f_write_firstpass,
        "f_write_all_madd": f_write_allmadd,
        "per_counter": wz,
    }

    # ---------------------------------------------------------------- the clock-load bound
    arr_clk = census["vrf/arr"]["clk_cap_ff"]          # model for vpu_64x32_3r2w_vpurf
    tenc_clk = census["tenc_rf/arr"]["clk_cap_ff"]     # model for vpu_tensorc_rf_buffer_array
    byp_clk = census["bypass"]["clk_cap_ff"]           # gated off for the whole TensorFMA
    tot_clk = census_total["clk_cap_ff"]
    # the clock-NET capacitance the power run actually prices, for the bias note below
    pwr_clk_cap = load(a.q129, "power-mixed", "zeros")["total"]["clock_cap_fF"]
    rem_clk = tot_clk - arr_clk - tenc_clk - byp_clk
    f_clock_lower = rem_clk / tot_clk
    rem_detail = {k: census[k]["clk_cap_ff"] for k in
                  ("tentmp_rf", "LANE_TIMA[0].tenb_rf", "LANE_TIMA[1].tenb_rf",
                   "tena_rf", "ctl")}
    # the vrf WRAPPER's own clock pins: inside the bound, but it was missing from this breakdown
    rem_detail["vrf_wrapper_excl_arr"] = census["vrf"]["clk_cap_ff"] - arr_clk
    res["clock_bound"] = {
        "clk_cap_fF_total": tot_clk,
        "clk_cap_fF_latch_array_model_vpu_rf": arr_clk,
        "clk_cap_fF_latch_array_model_tenc": tenc_clk,
        "clk_cap_fF_bypass_gated_off_on_a_txfma": byp_clk,
        "clk_cap_fF_remaining": rem_clk,
        "clk_cap_fF_remaining_detail": rem_detail,
        "clk_cap_fF_remaining_detail_sum": sum(rem_detail.values()),
        "f_clock_lower": f_clock_lower,
        "f_clock_upper": 1.0,
        "clk_cap_fF_power_run_nets": pwr_clk_cap,
        "clk_cap_fF_tree_wiring": pwr_clk_cap - tot_clk,
        "bias": ("the LOWER end is optimistic, in two named ways. (1) The denominator is the "
                 "census's clock-PIN capacitance, %.1f fF, but the energy scaled is the power "
                 "run's clock-NET energy, whose capacitance is %.1f fF -- about %.1f fF of it is "
                 "tree wiring, not leaf pins. Re-running CTS on a smaller leaf load drops leaf "
                 "wires and keeps the trunk, so the real reduction is LESS than proportional to "
                 "leaf pin load. (2) The two compiled macros' own clock pins are removed with "
                 "their models and never added back. Both push the true figure above the lower "
                 "end, which is why the UPPER end is the one to quote against a card measurement"
                 % (tot_clk, pwr_clk_cap, pwr_clk_cap - tot_clk)),
        "why": ("the chip's two biggest clock loads here are models: vpu_64x32_3r2w_vpurf and "
                "vpu_tensorc_rf_buffer_array are compiled macros with one clock pin each, not "
                "2,243 + 562 latches behind per-entry gates, and vpu_bypass's clock is held off "
                "for the whole TensorFMA (vpu_ctrl.v ll.1244, 1334, 1403, 1463, 1538 -> "
                "vpu_lane.v l.218, l.245). The three real latch files (TENA, TENB x2, TMP) are "
                "rf_latch_1r_1w in the chip too and stay. Clock-tree energy tracks the pin load "
                "the tree drives, so the share of the pin load that survives bounds it below; "
                "the two macros' own clock pins are a few fF and are not added back"),
    }

    # ---------------------------------------------------------------- per-pattern re-price
    res["patterns"] = {}
    for pat in ("zeros", "ones", "randn"):
        d = load(a.q129, "power-mixed", pat)
        dw = load(a.q129, "power-mixed-clkwide", pat)
        p = part_energies(d)
        tot = d["per_muladd"]["energy_pJ"]
        clock_total = d["total"]["clock_energy_J"] / MACS / PJ
        # the latch array's own gated-clock nets, isolated by the widened regex
        arr_wrclk = dw["blocks"]["vrf/arr"].get("clock_energy_J", 0.0) / MACS / PJ
        # the bypass block's clock floor: its zeros energy is all clock (no data moves there on
        # zeros: Q129 sim_acct bus_toggles = res_toggles = 0, and its 216.5 toggles/MAC equal the
        # clock root's 216.4, the signature of nets that toggle every cycle)
        byp_clock_floor = part_energies(load(a.q129, "power-mixed", "zeros"))["bypass"]

        cz_p = counts[(pat, 0)]
        # data-dependent read activity scales with the mux-output transitions of the ports kept.
        # With a static read tree (every entry holding the same word) there is no measured ratio;
        # the fallback keeps Q129's figure in full, which is the ceiling-preserving choice. On
        # `zeros` the term this multiplies is exactly 0, so the fallback never moves a number.
        mo_b = cz_p["bench"]["mux_out_tr"]
        mo_p2 = cz_p["rtl"]["mux_out_tr_p"][2]
        f_data_read = (mo_p2 / mo_b) if mo_b else 1.0
        f_write = (cz_p["rtl"]["entry_clk_edges"] / cz_p["bench"]["entry_clk_edges"]
                   if cz_p["bench"]["entry_clk_edges"] else 0.0)

        # the array: address/select side + its own write clocks + the data-dependent remainder
        arr = p["rf_array"]
        arr_zeros = part_energies(load(a.q129, "power-mixed", "zeros"))["rf_array"]
        arr_addr = arr_zeros - arr_wrclk            # address/select tree (+ the tiny write decode)
        arr_data = arr - arr_zeros                  # what the operand words add in this pattern
        arr_new = arr_addr * f_read_silicon + arr_wrclk * f_write + arr_data * f_data_read
        arr_new_model = arr_addr * f_read_model + arr_wrclk * f_write + arr_data * (
            cz_p["rtl"]["mux_out_tr"] / mo_b if mo_b else 1.0)

        # the bypass: its clock floor goes, its combinational data path stays
        byp_new = max(p["bypass"] - byp_clock_floor, 0.0)

        # the top-level row: clock term bounded, signal term stands
        top_signal = p["top_clock"] - clock_total
        top_lo = top_signal + clock_total * f_clock_lower
        top_hi = p["top_clock"]

        rest = sum(p[k] for k in ("rf_bypass", "tena", "tenb", "tenc", "tentmp", "ctl"))

        lo = arr_new + byp_new + top_lo + rest
        hi = arr_new + byp_new + top_hi + rest
        hi_model = arr_new_model + byp_new + top_hi + rest

        # the cells' internal energy: Q129 adds 0.118842 fJ per combinational transition. Scale it
        # by the same factor the switching of each part moved (stated approximation).
        int_ratio = d["internal_estimate"]["ratio_to_switching_only"]
        res["patterns"][pat] = {
            "q129_parts_pJ_per_mac": p,
            "q129_total_switching_pJ_per_mac": tot,
            "q129_clock_net_pJ_per_mac": clock_total,
            "array_address_side_pJ_per_mac": arr_addr,
            "array_own_write_clock_pJ_per_mac": arr_wrclk,
            "array_data_dependent_pJ_per_mac": arr_data,
            "f_data_read_port2_only": f_data_read,
            "f_write": f_write,
            "bypass_clock_floor_removed_pJ_per_mac": byp_clock_floor if p["bypass"] else 0.0,
            "corrected": {
                "rf_array": arr_new,
                "rf_array_model_rewired_only": arr_new_model,
                "bypass": byp_new,
                "top_clock_lower": top_lo,
                "top_clock_upper": top_hi,
                "other_parts": rest,
                "total_switching_lower_pJ_per_mac": lo,
                "total_switching_upper_pJ_per_mac": hi,
                "total_switching_upper_model_rewired_only_pJ_per_mac": hi_model,
                "total_plus_internal_lower_pJ_per_mac": lo * int_ratio,
                "total_plus_internal_upper_pJ_per_mac": hi * int_ratio,
                "internal_ratio_used": int_ratio,
            },
            "cut_vs_q129": {
                "switching_lower": tot - lo,
                "switching_upper": tot - hi,
                "fraction_remaining_lower": lo / tot,
                "fraction_remaining_upper": hi / tot,
            },
        }

    # ---------------------------------------------------------------- the zero gate by pattern
    res["gating_by_pattern"] = {}
    for (pat, am), d in sorted(counts.items()):
        res["gating_by_pattern"]["%s_allmadd%d" % (pat, am)] = {
            "uops": d["uops"], "gated": d["gated"],
            "fraction_gated": d["gated"] / d["uops"] if d["uops"] else 0.0,
            "first_pass_uops": d["first_pass_uops"],
        }
    res["gating_rule"] = {
        "rtl": "vpu_ctrl.v ll.805-818: ex_tensor_zero_mask = A-zero | (B-zero-tima0 & "
               "B-zero-tima1), where tima0 indexes ex_tima_tenb_raddr and tima1 that address "
               "OR 1 -- but only when ex_tima_valid_unqual is set",
        "why_one_word_is_exact_on_fp32":
            "vpu_tensorfma.v l.861 is `s1_tima_valid <= s0_fma_en_conv && req_int8`, so TIMA is "
            "live on an int8 TensorFMA and nowhere else. On an fp32 TensorFMA32 "
            "ex_tima_valid_unqual = 0, both paired terms index the SAME entry ex_ra2_ten "
            "(ll.808, 811), the AND is idempotent, and the mask is exactly A-zero | B-zero. The "
            "testbench's single-word B test is therefore exact for every number here, not a "
            "simplification. On an int8 TIMA op the two addresses differ, the AND bites, and "
            "this bench does not model it -- nothing here is int8",
        "a_side": "f3_zero_data_a is {8{tena_word == 0}} (vpu_ctrl.v l.1230): one scalar A word "
                  "broadcast to all eight lane bits. f3_zero_data_b[i] is per-lane (l.1233)",
    }
    res["corrections"] = {
        "dated": "2026-10-31, same day, after review; README section Corrections has the detail",
        "sim_offs_off_by_one": "rf3r2w_struct.sv offs() was NODES - (ENTRIES >> L) = -1 at L = 0 "
                               "instead of 0, so the read tree was built one index low and its "
                               "root was never assigned. Fixed to ENTRIES - (ENTRIES >> L); a "
                               "new rd_chk_fail counter asserts rd_data[p] == rf[rd_addr[p]] on "
                               "every port every cycle and reads 0 in every row",
        "sim_shortreal_fma": "tb_gate_audit.sv computed the multiply-add with $bitstoshortreal / "
                             "$shortrealtobits. Verilator does not support shortreal (it warns "
                             "`Unsupported: shortreal being promoted to real`, which -Wno-lint "
                             "hid), so the casts read a double's bit pattern, every product "
                             "underflowed, and the multiply-add returned c unchanged: "
                             "A=3f800000 B=3f800000 C=467a0000 fma=467a0000. The arithmetic now "
                             "comes from sim/accum.py and the testbench holds no floating point",
        "what_moved": "NOTHING in the headline or in any pattern total. The address side "
                      "(sel_pin_tr, addr_tr) and the write side (dec_tr, the clock-edge "
                      "counters, the zero-gate counts) never read the tree or the result. "
                      "f_data_read is 1/3 exactly before and after, because the bench's three "
                      "read ports and the RTL's port 2 carry the same address stream over the "
                      "same file. What moved: the mux_out_tr and rd_data_tr columns, and the "
                      "*_model_rewired_only figures built on their ratio (randn 0.829 -> "
                      "0.849377, ones 0.349 -> 1.0)",
        "cross_check": "the corrected counts agree digit for digit, on all eight rows and every "
                       "counter, with two independent Python replicas of the two SystemVerilog "
                       "files, one of them written by the reviewer before this fix",
    }

    # ---------------------------------------------------------------- the card comparison
    zp = res["patterns"]["zeros"]
    z = zp["corrected"]
    board_zeros = 0.27          # E38 three-card registered mean, Q128 data.json /permac/mean_zeros_pJ
    per_card = [0.1633, 0.4034, 0.2512]      # the same data.json, e38_registered
    clk_z = zp["q129_clock_net_pJ_per_mac"]
    sig_lo = z["total_switching_lower_pJ_per_mac"] - clk_z * res["clock_bound"]["f_clock_lower"]
    sig_hi = z["total_switching_upper_pJ_per_mac"] - clk_z
    strict_hi = z["total_switching_upper_model_rewired_only_pJ_per_mac"]
    res["card_check"] = {
        "board_zeros_pJ_per_mac": board_zeros,
        "board_zeros_per_card_pJ": per_card,
        "board_zeros_per_card_spread_pJ": [min(per_card), max(per_card)],
        "q129_transport_zeros_pJ_per_mac": zp["q129_total_switching_pJ_per_mac"],
        "q129_ratio_over_board": zp["q129_total_switching_pJ_per_mac"] / board_zeros,
        "q129_signal_only_pJ_per_mac": 0.4309799743594726,
        "q129_ratio_signal_only_over_board": 0.4309799743594726 / board_zeros,
        "corrected_lower_pJ_per_mac": z["total_switching_lower_pJ_per_mac"],
        "corrected_upper_pJ_per_mac": z["total_switching_upper_pJ_per_mac"],
        "corrected_ratio_over_board_lower": z["total_switching_lower_pJ_per_mac"] / board_zeros,
        "corrected_ratio_over_board_upper": z["total_switching_upper_pJ_per_mac"] / board_zeros,
        "corrected_signal_only_lower_pJ_per_mac": sig_lo,
        "corrected_signal_only_upper_pJ_per_mac": sig_hi,
        "corrected_ratio_signal_only_over_board": [sig_lo / board_zeros, sig_hi / board_zeros],
        # the three readings, each named, each with its verdict
        "readings": {
            "signal_only_vs_board_mean": {
                "pJ_per_mac": sig_lo, "ratio": sig_lo / board_zeros, "verdict": "PASSES",
                "what": "the clock term is inside the idle subtract, so only signal switching "
                        "has to fit inside the board's 0.27 pJ/MAC",
            },
            "with_clock_vs_board_mean": {
                "pJ_per_mac": [z["total_switching_lower_pJ_per_mac"],
                               z["total_switching_upper_pJ_per_mac"]],
                "ratio": [z["total_switching_lower_pJ_per_mac"] / board_zeros,
                          z["total_switching_upper_pJ_per_mac"] / board_zeros],
                "verdict": "STRADDLES",
                "what": "the lane's clocks are gated at idle, so the whole figure has to fit. "
                        "The lower end fits at 0.73x; the UPPER end still exceeds the whole "
                        "board by 37%, so this reading is narrowed, not settled",
            },
            "same_netlist_strict_vs_board_mean": {
                "pJ_per_mac": strict_hi, "ratio": strict_hi / board_zeros, "verdict": "FAILS",
                "what": "the strictest re-price of the SAME netlist: the latch array has no "
                        "read-enable pin at all, so only the bench's three swept addresses are "
                        "fixable and the whole clock term stands. 1.79x the board",
            },
            "with_clock_vs_lowest_registered_card": {
                "pJ_per_mac": [z["total_switching_lower_pJ_per_mac"],
                               z["total_switching_upper_pJ_per_mac"]],
                "ratio": [z["total_switching_lower_pJ_per_mac"] / min(per_card),
                          z["total_switching_upper_pJ_per_mac"] / min(per_card)],
                "verdict": "FAILS",
                "what": "against the lowest of the three registered cards (%.4f pJ/MAC, not the "
                        "three-card mean) both ends exceed it" % min(per_card),
            },
        },
        "reading": ("E38's 0.27 pJ/MAC is a three-card mean and the cards themselves run "
                    "%.4f-%.4f pJ/MAC. It is measured over idle: if the lane's clocks run at idle "
                    "the clock term is inside the subtract and only the signal-only figure has to "
                    "fit inside 0.27; if they are gated at idle the whole corrected figure has to. "
                    "Q129's numbers failed both tests (2.42x and 1.60x). The corrected ones pass "
                    "the signal-only reading cleanly at 0.54x and STRADDLE the board on the other "
                    "at 0.73x-1.37x -- so the contradiction is NARROWED, not resolved: one lane's "
                    "transport at the top of its own bound still exceeds the whole board by 37%%, "
                    "and against the lowest registered card, or on the strict same-netlist "
                    "reading (%.4f, 1.79x), it still fails. See `readings` for all four."
                    % (min(per_card), max(per_card), strict_hi)),
    }

    # ---------------------------------------------------------------- the ledger
    arith_sw, arith_int = 1.516, 1.946          # Q126(e), one lane, random fp32
    r = res["patterns"]["randn"]["corrected"]
    # Q129's own internal estimate for randn, per MAC: it ADDS this to the switching, whatever
    # the switching is. This script's `internal_ratio_used` instead scales it with the switching.
    # Both rows are published, because Q129's 1.261 / 1.484 are on the additive convention and
    # setting them beside a multiplicative row without saying so is not like-for-like.
    dr = load(a.q129, "power-mixed", "randn")
    int_add = dr["internal_estimate"]["internal_J_signal_transitions"] / MACS / PJ
    res["ledger_randn"] = {
        "arithmetic_switching_pJ": arith_sw,
        "arithmetic_plus_internal_pJ": arith_int,
        "q129_transport_switching_pJ": res["patterns"]["randn"]["q129_total_switching_pJ_per_mac"],
        "q129_transport_plus_internal_upper_pJ": 1.4841,
        "q129_transport_plus_internal_excl_clock_pJ": 1.2610,
        "q129_total_range_pJ": [3.207, 3.430],
        "corrected_transport_switching_range_pJ": [r["total_switching_lower_pJ_per_mac"],
                                                   r["total_switching_upper_pJ_per_mac"]],
        "internal_convention": {
            "multiplicative": {
                "what": "the cells' internal energy is scaled by the same factor the switching "
                        "moved (internal_ratio_used = %.6f). Defensible, because the transitions "
                        "that carry the internal energy are the ones the gating removes -- but "
                        "NOT the convention Q129 published on" % r["internal_ratio_used"],
                "ratio_used": r["internal_ratio_used"],
            },
            "additive_q129": {
                "what": "Q129's own convention: the whole internal estimate is ADDED to the "
                        "switching, unchanged. Its published 1.261 = 0.80979 signal switching + "
                        "%.5f internal, and 1.484 = 1.0329 + %.5f. Conservative here, because it "
                        "keeps internal energy for transitions the gating removed"
                        % (int_add, int_add),
                "internal_pJ_per_mac_added": int_add,
            },
        },
        "corrected_transport_plus_internal_range_pJ": [r["total_plus_internal_lower_pJ_per_mac"],
                                                       r["total_plus_internal_upper_pJ_per_mac"]],
        "corrected_transport_plus_internal_range_additive_q129_pJ": [
            r["total_switching_lower_pJ_per_mac"] + int_add,
            r["total_switching_upper_pJ_per_mac"] + int_add],
        "corrected_total_range_pJ": [arith_int + r["total_plus_internal_lower_pJ_per_mac"],
                                     arith_int + r["total_plus_internal_upper_pJ_per_mac"]],
        "corrected_total_range_additive_q129_pJ": [
            arith_int + r["total_switching_lower_pJ_per_mac"] + int_add,
            arith_int + r["total_switching_upper_pJ_per_mac"] + int_add],
        "board_E38_pJ": 5.783,
        "rail_Q128_pJ": 4.337,
        "rail_Q129_corrected_footing_pJ": 4.77,
    }
    lr = res["ledger_randn"]
    lr["corrected_closure_vs_board"] = [lr["corrected_total_range_pJ"][0] / 5.783,
                                        lr["corrected_total_range_pJ"][1] / 5.783]
    lr["corrected_closure_vs_rail_Q128"] = [lr["corrected_total_range_pJ"][0] / 4.337,
                                            lr["corrected_total_range_pJ"][1] / 4.337]
    lr["corrected_closure_vs_board_additive_q129"] = [
        lr["corrected_total_range_additive_q129_pJ"][0] / 5.783,
        lr["corrected_total_range_additive_q129_pJ"][1] / 5.783]
    lr["corrected_closure_vs_rail_Q128_additive_q129"] = [
        lr["corrected_total_range_additive_q129_pJ"][0] / 4.337,
        lr["corrected_total_range_additive_q129_pJ"][1] / 4.337]
    lr["note"] = ("Q129's published 55-59%% closure is on the additive convention. Like-for-like "
                  "against it, the corrected closure is %.0f-%.0f%% of the board; on the "
                  "multiplicative convention %.0f-%.0f%%. Both are a FALL from 55-59%%, which is "
                  "the direction that matters: what came off was energy the chip does not spend."
                  % (100 * lr["corrected_closure_vs_board_additive_q129"][0],
                     100 * lr["corrected_closure_vs_board_additive_q129"][1],
                     100 * lr["corrected_closure_vs_board"][0],
                     100 * lr["corrected_closure_vs_board"][1]))

    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=False)

    # ---------------------------------------------------------------- stdout table
    print("read-port factor: silicon %.5f (port 2 alone), latch array re-wired %.5f"
          % (f_read_silicon, f_read_model))
    print("write factor on zeros: %.5f (k=0 pass ungated), %.5f (every pass MADD)"
          % (f_write_firstpass, f_write_allmadd))
    print("clock-load bound: %.1f of %.1f fF of clock-pin load survives -> f_clock in [%.4f, 1]; "
          "the lower end is optimistic (clock_bound.bias)" % (rem_clk, tot_clk, f_clock_lower))
    print()
    for pat in ("zeros", "ones", "randn"):
        q = res["patterns"][pat]
        c = q["corrected"]
        print("%-6s Q129 %.4f -> corrected %.4f .. %.4f pJ/MAC  (%.0f%%..%.0f%% of Q129)"
              % (pat, q["q129_total_switching_pJ_per_mac"],
                 c["total_switching_lower_pJ_per_mac"], c["total_switching_upper_pJ_per_mac"],
                 100 * q["cut_vs_q129"]["fraction_remaining_lower"],
                 100 * q["cut_vs_q129"]["fraction_remaining_upper"]))
        print("       array %.4f -> %.4f | bypass %.4f -> %.4f | top+clk %.4f -> %.4f..%.4f | rest %.4f"
              % (q["q129_parts_pJ_per_mac"]["rf_array"], c["rf_array"],
                 q["q129_parts_pJ_per_mac"]["bypass"], c["bypass"],
                 q["q129_parts_pJ_per_mac"]["top_clock"], c["top_clock_lower"], c["top_clock_upper"],
                 c["other_parts"]))
    print()
    cc = res["card_check"]
    print("zeros vs the card: board %.2f pJ/MAC (three cards %.4f..%.4f); Q129 lane transport "
          "%.4f (%.2fx the board) -> corrected %.4f..%.4f (%.2fx..%.2fx)"
          % (cc["board_zeros_pJ_per_mac"], cc["board_zeros_per_card_spread_pJ"][0],
             cc["board_zeros_per_card_spread_pJ"][1], cc["q129_transport_zeros_pJ_per_mac"],
             cc["q129_ratio_over_board"], cc["corrected_lower_pJ_per_mac"],
             cc["corrected_upper_pJ_per_mac"], cc["corrected_ratio_over_board_lower"],
             cc["corrected_ratio_over_board_upper"]))
    for name, rd in cc["readings"].items():
        print("   %-38s %-10s %s" % (name, rd["verdict"],
              rd["ratio"] if isinstance(rd["ratio"], float) else
              "%.2fx..%.2fx" % (rd["ratio"][0], rd["ratio"][1])))
    print("   signal only (clock inside the idle subtract): Q129 %.4f (%.2fx) -> corrected "
          "%.4f..%.4f (%.2fx..%.2fx)"
          % (cc["q129_signal_only_pJ_per_mac"], cc["q129_ratio_signal_only_over_board"],
             cc["corrected_signal_only_lower_pJ_per_mac"], cc["corrected_signal_only_upper_pJ_per_mac"],
             cc["corrected_ratio_signal_only_over_board"][0],
             cc["corrected_ratio_signal_only_over_board"][1]))
    print("   zero gate fires on: " + ", ".join(
        "%s %.1f%%" % (k, 100 * v["fraction_gated"]) for k, v in res["gating_by_pattern"].items()))
    print("randn ledger, internal scaled with the switching: arithmetic %.3f + transport "
          "%.3f..%.3f = %.3f..%.3f pJ, %.0f%%..%.0f%% of the board's 5.783"
          % (arith_int, lr["corrected_transport_plus_internal_range_pJ"][0],
             lr["corrected_transport_plus_internal_range_pJ"][1],
             lr["corrected_total_range_pJ"][0], lr["corrected_total_range_pJ"][1],
             100 * lr["corrected_closure_vs_board"][0], 100 * lr["corrected_closure_vs_board"][1]))
    print("randn ledger, Q129's additive convention (like-for-like with its 55-59%%): transport "
          "%.3f..%.3f = %.3f..%.3f pJ, %.0f%%..%.0f%% of the board"
          % (lr["corrected_transport_plus_internal_range_additive_q129_pJ"][0],
             lr["corrected_transport_plus_internal_range_additive_q129_pJ"][1],
             lr["corrected_total_range_additive_q129_pJ"][0],
             lr["corrected_total_range_additive_q129_pJ"][1],
             100 * lr["corrected_closure_vs_board_additive_q129"][0],
             100 * lr["corrected_closure_vs_board_additive_q129"][1]))
    zc = res["patterns"]["zeros"]["corrected"]
    rc = res["patterns"]["randn"]["corrected"]
    print("zeros / randn, corrected transport switching: %.4f / %.4f = %.1f%%"
          % (zc["total_switching_lower_pJ_per_mac"], rc["total_switching_lower_pJ_per_mac"],
             100 * zc["total_switching_lower_pJ_per_mac"] / rc["total_switching_lower_pJ_per_mac"]))


if __name__ == "__main__":
    main()
