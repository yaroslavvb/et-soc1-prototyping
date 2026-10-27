#!/usr/bin/env python3
"""Q129(a): build every table on README.md from the committed JSONs, and the ladder fits.

    python3 -I summarize.py [<this directory>] > summary.txt

Nothing here re-measures anything: it reads `caps_*.json` (the capacitance totals out of the
two SPEFs) and `reprice-*/reprice_*.json` (the activity-weighted energies at four Miller
factors) and prints the tables. The ladder slope is fitted exactly the way E60's own reducer
fits it -- an ordinary least-squares line over h >= 1 with a free intercept, against the
DESIGNED flip count -- so the fJ-per-flipped-bit rows are comparable with
docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt and with POWER.md's.
"""
import json
import os
import sys

HERE = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
VARIANTS = ["gr", "spef_k0", "spef_k1", "spef_k2"]
PATTERNS = ["randn", "ones", "zeros",
            "lq_h0", "lq_h1", "lq_h2", "lq_h4", "lq_h8",
            "lb_h0", "lb_h1", "lb_h2", "lb_h4", "lb_h8"]
# The published figures this run is set beside: POWER.md's own table, the 2022 conda OpenROAD.
PUBLISHED = {"keep": {"randn_pJ": 1.516, "clock_share": 0.327, "cap_fF": 47093.21,
                      "cap_fraction_priced": 0.5046, "nets": 20383,
                      "ladder_designed_fJ": {"lq": 32.9, "lb": 38.5}},
             "mixed": {"randn_pJ": 1.468, "clock_share": 0.320, "cap_fF": 40232.60,
                       "cap_fraction_priced": 0.5628, "nets": 16403,
                       "ladder_designed_fJ": {"lq": 34.8, "lb": 38.3}}}
# The Q128 ledger's split of a random multiply-add, on the KEPT netlist, 2022 flow.
LEDGER = {"transistor_gates_pJ": 0.306, "wire_in_cells_pJ": 0.620,
          "wire_between_cells_pJ": 0.590, "internal_pJ": 0.431, "switching_pJ": 1.516,
          "board_pJ": 5.783, "rail_ratio": 0.75}
# The detailed router's own totals, from route/route_<nl>.log.gz ("Total wire length = ...",
# "Total number of vias = ..."), and the two unit capacitances the global-route estimate uses,
# from the ORFS asap7 platform's setRC.tcl (`set_wire_rc -signal/-clock -capacitance`, fF/um).
# They are constants here because neither lives in a JSON; both are quoted in the README with
# their source, and this block is what makes the diagnosis below reproducible.
#
# Corrected Tue 27 Oct 2026, after review: both rows must be read from the FINAL, converged DRT
# pass -- the one whose `DRT-0199 Number of violations = 0` precedes it -- and not from an earlier
# iteration. The first version of this file took `keep` from the 0th iteration (3,861 violations
# still open: 88,248 um / 200,870 vias at route_keep.log.gz l.1063/1074), which read the wire
# 0.8% long and the vias 4.8% high. The converged pass is l.1275/1286. `mixed` was always read
# from its converged pass (l.1281/1292). The extraction ran on the converged route in both cases,
# so only the per-micron diagnosis below was affected; every capacitance and energy figure is
# taken from the SPEF and does not use these lengths at all.
ROUTED = {"mixed": {"wire_length_um": 82358, "vias": 166805},
          "keep": {"wire_length_um": 87570, "vias": 191590}}
SETRC = {"signal_fF_per_um": 1.65790E-01, "clock_fF_per_um": 1.45426E-01}


def load(nl, p):
    with open(os.path.join(HERE, "reprice-%s" % nl, "reprice_%s.json" % p)) as fh:
        return json.load(fh)


def caps(nl, which):
    with open(os.path.join(HERE, "caps_%s_%s.json" % (which, nl))) as fh:
        return json.load(fh)


def fit(xs, ys):
    """least squares y = a + b x, returned (b, a)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    return b, my - b * mx


def main():
    out = []
    w = out.append
    for nl in ("mixed", "keep"):
        g, s = caps(nl, "gr"), caps(nl, "spef")
        w("")
        w("=== %s netlist: the design's capacitance, fF ===" % nl)
        w("  nets                            %8d   (clock %d)" % (s["nets"], s["clock_nets"]))
        w("  pin, from the liberty           %10.1f  (unchanged by routing)" % s["all_fF"]["pinload"])
        w("  wire, global-route Steiner      %10.1f" % g["all_fF"]["ground"])
        w("  wire, extracted to ground       %10.1f" % s["all_fF"]["ground"])
        w("  wire, extracted coupling        %10.1f   (each cap once: %d caps)"
          % (s["entries"]["coupling_total_physical_fF"],
             s["entries"]["coupling_entries_distinct"]))
        w("  wire, ground + coupling k=1     %10.1f   (each cap charged to both its nets)"
          % (s["all_fF"]["ground"] + s["all_fF"]["coupling"]))
        w("  wire, extractor's own per-net   %10.1f   (= sum of *D_NET)" % s["all_fF"]["dnet_total"])
        w("  ratio extracted(k=1)/Steiner    %10.3f"
          % ((s["all_fF"]["ground"] + s["all_fF"]["coupling"]) / g["all_fF"]["ground"]))
        w("  coupling / extracted wire       %10.1f%%"
          % (100 * s["entries"]["coupling_total_physical_fF"]
             / (s["all_fF"]["ground"] + s["entries"]["coupling_total_physical_fF"])))
        w("  CLOCK nets only: pin %.1f  Steiner %.1f  ground %.1f  coupling(both) %.1f"
          % (s["totals_fF"]["clock_pinload_fF"], g["totals_fF"]["clock_ground_fF"],
             s["totals_fF"]["clock_ground_fF"], s["totals_fF"]["clock_coupling_fF"]))
        w("  CLOCK total cap: Steiner %.1f -> extracted k=1 %.1f"
          % (g["totals_fF"]["clock_ground_fF"] + s["totals_fF"]["clock_pinload_fF"],
             s["totals_fF"]["clock_ground_fF"] + s["totals_fF"]["clock_coupling_fF"]
             + s["totals_fF"]["clock_pinload_fF"]))
        rr = load(nl, "randn")["variants"]
        w("  CLOCK cap that TOGGLES at randn (POWER.md's 1,846 fF row, kept netlist):")
        for v in VARIANTS:
            t = rr[v]["total"]
            w("    %-9s %8.1f fF  (wire %7.1f  pin %7.1f)"
              % (v, t["clock_cap_F"] * 1e15, t["clock_wire_cap_F"] * 1e15,
                 t["clock_pin_cap_F"] * 1e15))

        # Where the Steiner estimate's over-prediction comes from: length, or fF per micron.
        L = ROUTED[nl]["wire_length_um"]
        c_phys = s["all_fF"]["ground"] + s["entries"]["coupling_total_physical_fF"]
        c_k1 = s["all_fF"]["ground"] + s["all_fF"]["coupling"]
        implied = (g["totals_fF"]["signal_ground_fF"] / SETRC["signal_fF_per_um"]
                   + g["totals_fF"]["clock_ground_fF"] / SETRC["clock_fF_per_um"])
        w("  detailed route: %d um of wire, %d vias" % (L, ROUTED[nl]["vias"]))
        w("  extracted fF per um: %.4f physical (each cap once), %.4f as each driver sees it"
          % (c_phys / L, c_k1 / L))
        w("  setRC's own unit capacitance: %.4f signal, %.4f clock fF/um"
          % (SETRC["signal_fF_per_um"], SETRC["clock_fF_per_um"]))
        w("  so the Steiner estimate assumes %d um (%.3fx the routed length) at %.3fx the"
          % (round(implied), implied / L, SETRC["signal_fF_per_um"] / (c_k1 / L)))
        w("  extracted fF/um -> %.3fx, against the measured Steiner/extracted(k=1) of %.3fx"
          % (implied / L * SETRC["signal_fF_per_um"] / (c_k1 / L), g["all_fF"]["ground"] / c_k1))

        w("")
        w("=== %s netlist: pJ per random multiply-add (randn), switching ===" % nl)
        w("  %-9s %9s %9s %9s %9s %8s %8s" % ("variant", "total", "wire", "pin", "clock",
                                              "clk%", "priced"))
        r = {}
        for v in VARIANTS:
            d = load(nl, "randn")["variants"][v]
            pm = d["per_muladd"]
            r[v] = pm
            w("  %-9s %9.4f %9.4f %9.4f %9.4f %7.1f%% %7.1f%%"
              % (v, pm["energy_pJ"], pm["wire_energy_pJ"], pm["pin_energy_pJ"],
                 pm["clock_energy_pJ"], 100 * d["clock_share"],
                 100 * d["coverage"]["cap_fraction_priced"]))
        pub = PUBLISHED[nl]
        w("  published (2022 OpenROAD, POWER.md): %.4f pJ, clock %.1f%%, priced %.1f%%"
          % (pub["randn_pJ"], 100 * pub["clock_share"], 100 * pub["cap_fraction_priced"]))
        w("  wire ratio within this run, extracted(k=1)/Steiner: %.4f"
          % (r["spef_k1"]["wire_energy_pJ"] / r["gr"]["wire_energy_pJ"]))
        w("  wire ratio k=0/Steiner %.4f   k=2/Steiner %.4f"
          % (r["spef_k0"]["wire_energy_pJ"] / r["gr"]["wire_energy_pJ"],
             r["spef_k2"]["wire_energy_pJ"] / r["gr"]["wire_energy_pJ"]))
        if nl == "keep":
            w("  this run's Steiner wire energy %.4f pJ against the ledger's own %.4f pJ "
              "(same netlist, 2022 tool): %.3fx"
              % (r["gr"]["wire_energy_pJ"], LEDGER["wire_between_cells_pJ"],
                 r["gr"]["wire_energy_pJ"] / LEDGER["wire_between_cells_pJ"]))

        w("")
        w("=== %s netlist: every pattern, pJ per multiply-add ===" % nl)
        w("  %-7s %8s %8s %8s %8s | %8s %8s %8s %8s"
          % ("pattern", "gr", "k=0", "k=1", "k=2", "gr wire", "k0 wire", "k1 wire", "k2 wire"))
        for p in PATTERNS:
            d = load(nl, p)["variants"]
            w("  %-7s %8.4f %8.4f %8.4f %8.4f | %8.4f %8.4f %8.4f %8.4f"
              % (p, d["gr"]["per_muladd"]["energy_pJ"], d["spef_k0"]["per_muladd"]["energy_pJ"],
                 d["spef_k1"]["per_muladd"]["energy_pJ"], d["spef_k2"]["per_muladd"]["energy_pJ"],
                 d["gr"]["per_muladd"]["wire_energy_pJ"],
                 d["spef_k0"]["per_muladd"]["wire_energy_pJ"],
                 d["spef_k1"]["per_muladd"]["wire_energy_pJ"],
                 d["spef_k2"]["per_muladd"]["wire_energy_pJ"]))

        w("")
        w("=== %s netlist: the Hamming ladder, fJ per DESIGNED flipped bit ===" % nl)
        w("  (OLS over h = 1,2,4,8 with a free intercept, E60's reducer's convention)")
        w("  %-6s %-9s %10s %12s" % ("ladder", "variant", "slope fJ", "intercept fJ"))
        for lad in ("lq", "lb"):
            for v in VARIANTS:
                hs, es = [], []
                for h in (1, 2, 4, 8):
                    d = load(nl, "%s_h%d" % (lad, h))["variants"][v]
                    hs.append(float(h))
                    es.append(d["per_muladd"]["energy_pJ"] * 1000.0)   # fJ
                b, a = fit(hs, es)
                w("  %-6s %-9s %10.2f %10.2f" % (lad, v, b, a))
            w("  %-6s %-9s %10.2f   (published, 2022 OpenROAD)"
              % (lad, "gr(pub)", pub["ladder_designed_fJ"][lad]))

    # The Q128 waterfall, revised two ways.
    w("")
    w("=== the Q128 waterfall for one random fp32 multiply-add, pJ ===")
    k = load("keep", "randn")["variants"]
    gr_w = k["gr"]["per_muladd"]["wire_energy_pJ"]
    ratios = {v: k[v]["per_muladd"]["wire_energy_pJ"] / gr_w for v in VARIANTS}
    w("  (A) the published ledger, with ONLY the between-cell wire re-priced by the")
    w("      within-run extracted/Steiner ratio on the same (kept) netlist")
    w("  %-26s %8s %8s %8s %8s" % ("", "published", "k=0", "k=1", "k=2"))
    rows = []
    for name, key in (("transistor gates", "transistor_gates_pJ"),
                      ("wire inside the cells", "wire_in_cells_pJ")):
        rows.append((name, [LEDGER[key]] * 4))
    wbc = LEDGER["wire_between_cells_pJ"]
    rows.append(("wire between the cells",
                 [wbc, wbc * ratios["spef_k0"], wbc * ratios["spef_k1"],
                  wbc * ratios["spef_k2"]]))
    sw = [LEDGER["switching_pJ"] - wbc + x for x in rows[-1][1]]
    rows.append(("switching total", sw))
    rows.append(("the cells' internal", [LEDGER["internal_pJ"]] * 4))
    tot = [x + LEDGER["internal_pJ"] for x in sw]
    rows.append(("bottom-up total", tot))
    rows.append(("unaccounted vs the board", [LEDGER["board_pJ"] - x for x in tot]))
    rows.append(("unaccounted vs the rail",
                 [LEDGER["board_pJ"] * LEDGER["rail_ratio"] - x for x in tot]))
    for name, vals in rows:
        w("  %-26s %8.3f %8.3f %8.3f %8.3f" % (name, *vals))
    w("  ratios applied: k=0 %.4f  k=1 %.4f  k=2 %.4f"
      % (ratios["spef_k0"], ratios["spef_k1"], ratios["spef_k2"]))
    w("")
    w("  (B) the whole thing re-measured on the current tool, kept netlist, routed.")
    w("      The pin half's own split (gates vs wire-inside-cells) is NOT re-measured: it is")
    w("      carried at the ledger's measured share, %.1f%% of the pin energy on gates."
      % (100 * LEDGER["transistor_gates_pJ"]
         / (LEDGER["transistor_gates_pJ"] + LEDGER["wire_in_cells_pJ"])))
    share = LEDGER["transistor_gates_pJ"] / (LEDGER["transistor_gates_pJ"]
                                             + LEDGER["wire_in_cells_pJ"])
    w("  %-26s %8s %8s %8s %8s" % ("", "gr", "k=0", "k=1", "k=2"))
    pin = [k[v]["per_muladd"]["pin_energy_pJ"] for v in VARIANTS]
    wir = [k[v]["per_muladd"]["wire_energy_pJ"] for v in VARIANTS]
    swi = [k[v]["per_muladd"]["energy_pJ"] for v in VARIANTS]
    inte = [k[v]["per_muladd"]["switching_plus_internal_pJ"] - k[v]["per_muladd"]["energy_pJ"]
            for v in VARIANTS]
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("transistor gates", *[p * share for p in pin]))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("wire inside the cells",
                                           *[p * (1 - share) for p in pin]))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("wire between the cells", *wir))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("switching total", *swi))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("the cells' internal", *inte))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f" % ("bottom-up total",
                                           *[s + i for s, i in zip(swi, inte)]))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f"
      % ("unaccounted vs the board", *[LEDGER["board_pJ"] - s - i
                                       for s, i in zip(swi, inte)]))
    w("  %-26s %8.3f %8.3f %8.3f %8.3f"
      % ("closure vs the board, %", *[100 * (s + i) / LEDGER["board_pJ"]
                                      for s, i in zip(swi, inte)]))
    print("\n".join(out))


if __name__ == "__main__":
    main()
