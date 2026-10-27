#!/usr/bin/env python3
"""Build the Q129 summary: the decomposition of the unpriced half, the before/after per pattern,
the two routes' agreement, the ladder refit, and what it moves in Q128's waterfall."""
import glob, gzip, json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__)) + "/"
MA = 512.0
PATS = ["randn", "zeros", "ones",
        "lb_h0", "lb_h1", "lb_h2", "lb_h4", "lb_h8",
        "lq_h0", "lq_h1", "lq_h2", "lq_h4", "lq_h8"]
BOARD = {"randn": 5.783, "ones": 2.13, "zeros": 0.27}      # E38/E39, three-card means, over idle
RAIL_RATIO = 0.75                                           # minion rail / board, Q128's chain
E60 = {("lq", "designed"): 116.746, ("lq", "bus"): 74.658,
       ("lb", "designed"): 129.918, ("lb", "bus"): 85.578}
BUS = {"lq_h0": 99, "lq_h1": 1123, "lq_h2": 2147, "lq_h4": 4617, "lq_h8": 6959,
       "lb_h0": 119, "lb_h1": 1565, "lb_h2": 2532, "lb_h4": 3891, "lb_h8": 6666,
       "randn": 17349, "ones": 31, "zeros": 0}


def fit(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return b, my - b * mx


out = {"date": "2026-10-27", "question": "Q129", "unit": "one lane, one TensorFMA32 op "
       "(512 multiply-adds, 547 cycles), ASAP7 RVT TT, 0.517 V",
       "patterns": {}, "methods": {}, "waterfall": {}, "ladder": {}, "clock_gating": {}}

st_randn = json.load(open(D + "res/q129_syn_randn.json"))
out["design"] = st_randn["design"]

for p in PATS:
    st = json.load(open(D + f"res/q129_syn_{p}.json"))
    pub = json.load(open(D + f"a1out/power_syn_{p}.json"))
    new = json.load(open(D + f"a1out/power_pnr_{p}.json"))
    cmp_ = json.load(open(D + f"res/cmp_{p}.json"))
    row = {
        "published": {
            "cap_fraction_priced": pub["coverage"]["cap_fraction_priced"],
            "signal_toggles_per_muladd": pub["total"].get("signal_toggles", 0) / MA,
            "clock_toggles_per_muladd": pub["total"].get("clock_toggles", 0) / MA,
            "switching_pJ_per_muladd": pub["per_muladd"]["energy_pJ"],
            "switching_plus_internal_pJ_per_muladd":
                pub["per_muladd"].get("switching_plus_internal_pJ"),
            "clock_share": pub["clock_share"],
        },
        "resimulated_post_cts": {
            "nets_priced": new["coverage"]["extracted_nets_found_in_sim"],
            "extracted_nets_not_named_by_the_sim": cmp_["nets_not_named_by_post_cts_sim"],
            "cap_fF_not_named_by_the_sim": cmp_["cap_fF_not_named_by_post_cts_sim"],
            "signal_toggles_per_muladd": cmp_["post_cts_direct"]["signal_toggles_per_muladd"],
            "clock_toggles_per_muladd": cmp_["post_cts_direct"]["clock_toggles_per_muladd"],
            "signal_pJ_per_muladd": cmp_["post_cts_direct"]["signal_pJ_per_muladd"],
            "clock_pJ_per_muladd": cmp_["post_cts_direct"]["clock_pJ_per_muladd"],
            "switching_pJ_per_muladd": cmp_["post_cts_direct"]["pJ_per_muladd"],
            "switching_plus_internal_pJ_per_muladd":
                new["per_muladd"].get("switching_plus_internal_pJ"),
        },
        "structural_from_the_pre_route_saif": {
            "cap_fraction_resolved": st["after"]["cap_fraction_resolved"],
            "signal_toggles_per_muladd": st["after"]["signal_toggles_per_muladd"],
            "clock_toggles_per_muladd": st["after"]["clock_toggles_per_muladd"],
            "switching_pJ_per_muladd": st["after"]["pJ_per_muladd"],
            "residue_cap_fraction": st["residue"]["cap_fraction"],
        },
        "agreement": {
            "unpriced_nets_checked": cmp_["inferred_vs_direct"]["nets_checked"],
            "exact": cmp_["inferred_vs_direct"]["exact"],
            "differ": cmp_["inferred_vs_direct"]["differ"],
            "energy_error_pJ_per_muladd": cmp_["inferred_vs_direct"]["energy_error_pJ_per_muladd"],
            "two_sims_on_nets_both_name_pJ_per_muladd":
                cmp_["two_sims_on_shared_nets"]["energy_delta_pJ_per_muladd"],
            "two_sims_on_nets_both_name_toggles_per_muladd":
                cmp_["two_sims_on_shared_nets"]["toggle_delta_per_muladd"],
        },
    }
    d_sw = (row["resimulated_post_cts"]["switching_pJ_per_muladd"]
            - row["published"]["switching_pJ_per_muladd"])
    row["delta"] = {
        "switching_pJ_per_muladd": d_sw,
        "switching_relative": d_sw / row["published"]["switching_pJ_per_muladd"],
        "switching_plus_internal_pJ_per_muladd":
            row["resimulated_post_cts"]["switching_plus_internal_pJ_per_muladd"]
            - row["published"]["switching_plus_internal_pJ_per_muladd"],
        "of_which_clock": (row["resimulated_post_cts"]["clock_pJ_per_muladd"]
                           - row["published"]["clock_share"]
                           * row["published"]["switching_pJ_per_muladd"]),
    }
    out["patterns"][p] = row

# the decomposition of the unpriced half, on randn
res = st_randn["resolved"]
cap_all = st_randn["design"]["cap_fF_extracted"]
dec = {}
for m in ("direct", "cts_name", "bitshift", "buffer", "tie", "sim_zero", "folded", "unresolved"):
    if m not in res:
        continue
    v = res[m]
    dec[m] = {"nets": v["nets"], "cap_fF": v["cap_fF"], "cap_fraction": v["cap_fF"] / cap_all,
              "toggles_per_muladd": v["toggles"] / MA,
              "switching_pJ_per_muladd": v["energy_J"] / MA * 1e12,
              "in_the_published_number": m in ("direct", "cts_name")}
out["methods"] = dec
out["unpriced_half"] = {
    "cap_fF": sum(v["cap_fF"] for m, v in dec.items() if not v["in_the_published_number"]),
    "cap_fraction": sum(v["cap_fraction"] for m, v in dec.items()
                        if not v["in_the_published_number"]),
    "nets": sum(v["nets"] for m, v in dec.items() if not v["in_the_published_number"]),
    "switching_pJ_per_muladd_it_was_worth":
        sum(v["switching_pJ_per_muladd"] for m, v in dec.items()
            if not v["in_the_published_number"]),
    "carries_no_switching_energy_cap_fraction":
        sum(v["cap_fraction"] for m, v in dec.items()
            if not v["in_the_published_number"] and v["toggles_per_muladd"] == 0),
}

# the waterfall
r = out["patterns"]["randn"]
pub_tot = r["published"]["switching_plus_internal_pJ_per_muladd"]
new_tot = r["resimulated_post_cts"]["switching_plus_internal_pJ_per_muladd"]
CELL_ENERGIES = os.environ.get(
    "CELL_ENERGIES",
    "../2026-10-26-asap7-cell-energies/asap7-cell-energies.json")
ce = json.load(open(os.path.join(D, CELL_ENERGIES)))
e_mix = (float(ce["census_weighted_mix"]["weighted_E_int_per_transition_VDDonly_fJ_0p7"])
         * (0.517 / float(ce["operating_point"]["VDD_liberty_V"])) ** 2)
clk_int = r["resimulated_post_cts"]["clock_toggles_per_muladd"] * e_mix * 1e-3   # fJ -> pJ
board = BOARD["randn"]
rail = board * RAIL_RATIO
out["waterfall"] = {
    "board_pJ_per_muladd_over_idle": board,
    "minion_rail_pJ_per_muladd": rail,
    "published_accounted_pJ": pub_tot,
    "new_accounted_pJ": new_tot,
    "moved_from_unaccounted_to_accounted_pJ": new_tot - pub_tot,
    "published_unaccounted_vs_board_pJ": board - pub_tot,
    "new_unaccounted_vs_board_pJ": board - new_tot,
    "published_unaccounted_vs_rail_pJ": rail - pub_tot,
    "new_unaccounted_vs_rail_pJ": rail - new_tot,
    "closure_vs_board": {"published": pub_tot / board, "new": new_tot / board},
    "closure_vs_rail": {"published": pub_tot / rail, "new": new_tot / rail},
    "data_dependent_vs_clocking": {
        "note": "the correction is entirely signal: the clock tree was already fully priced, "
                "because power.py's clknet_ name rule reached all 236 of CTS's clock nets",
        "signal_pJ_added": (r["resimulated_post_cts"]["signal_pJ_per_muladd"]
                            - r["published"]["switching_pJ_per_muladd"]
                            * (1 - r["published"]["clock_share"])),
        "clock_pJ_added": r["delta"]["of_which_clock"],
        "randn_signal_pJ": r["resimulated_post_cts"]["signal_pJ_per_muladd"],
        "randn_clock_pJ": r["resimulated_post_cts"]["clock_pJ_per_muladd"],
        "randn_over_zeros_switching_pJ":
            r["resimulated_post_cts"]["switching_pJ_per_muladd"]
            - out["patterns"]["zeros"]["resimulated_post_cts"]["switching_pJ_per_muladd"],
        "randn_over_zeros_signal_pJ":
            r["resimulated_post_cts"]["signal_pJ_per_muladd"]
            - out["patterns"]["zeros"]["resimulated_post_cts"]["signal_pJ_per_muladd"],
        "randn_over_zeros_clock_pJ":
            r["resimulated_post_cts"]["clock_pJ_per_muladd"]
            - out["patterns"]["zeros"]["resimulated_post_cts"]["clock_pJ_per_muladd"],
        "zeros_rung_is_the_ungated_clock_root_pJ":
            out["patterns"]["zeros"]["resimulated_post_cts"]["switching_pJ_per_muladd"],
    },
    "labelled_sensitivity_clock_buffer_internal": {
        "pJ_per_muladd": clk_int,
        "accounted_with_it_pJ": new_tot + clk_int,
        "closure_vs_board_with_it": (new_tot + clk_int) / board,
        "what": "the CTS buffers' and the flops' clock-pin internal energy, which Q126(d)'s "
                "internal estimate leaves out entirely (it prices signal transitions only). "
                "Priced here at the same combinational mix figure, so it is indicative, not "
                "measured: the real clock buffers are BUFx2-x5, bigger than the mix.",
    },
}

# the ladder, refit on the complete capacitance
for fam in ("lq", "lb"):
    z = out["patterns"][f"{fam}_h0"]
    rows = {}
    for which, key in (("published", "published"), ("complete", "resimulated_post_cts")):
        ez = z[key]["switching_pJ_per_muladd"]
        ezi = z[key]["switching_plus_internal_pJ_per_muladd"]
        hs = [1, 2, 4, 8]
        ys = [(out["patterns"][f"{fam}_h{h}"][key]["switching_pJ_per_muladd"] - ez) * 1000
              for h in hs]
        yi = [(out["patterns"][f"{fam}_h{h}"][key]["switching_plus_internal_pJ_per_muladd"] - ezi)
              * 1000 for h in hs]
        s, c = fit(hs, ys)
        si, ci = fit(hs, yi)
        xb = [BUS[f"{fam}_h{h}"] / MA - BUS[f"{fam}_h0"] / MA for h in hs]
        sb, cb = fit(xb, ys)
        sbi, _ = fit(xb, yi)
        rows[which] = {
            "fJ_per_designed_bit_switching": s, "intercept_fJ": c,
            "fJ_per_designed_bit_with_internal": si, "intercept_with_internal_fJ": ci,
            "fJ_per_counted_bus_bit_switching": sb,
            "fJ_per_counted_bus_bit_with_internal": sbi,
            "vs_E60_board_designed_switching": s / E60[(fam, "designed")],
            "vs_E60_board_designed_with_internal": si / E60[(fam, "designed")],
        }
    out["ladder"][fam] = {"E60_board_fJ_per_designed_bit": E60[(fam, "designed")], **rows}

json.dump(out, open(D + "res/q129-unpriced-capacitance.json", "w"), indent=1)
print(json.dumps({"design": out["design"], "methods": out["methods"],
                  "unpriced_half": out["unpriced_half"], "waterfall": out["waterfall"]}, indent=1))
