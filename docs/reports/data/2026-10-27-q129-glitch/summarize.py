#!/usr/bin/env python3
"""Build summary.txt from this directory's glitch_*.json: the measured glitch factor, its
sensitivities, the comparison with the tape-out flow, and what it does to Q128's waterfall.

    python3 summarize.py > summary.txt
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# --- the published numbers this is measured against (all per random fp32 multiply-add, 0.517 V)
BOARD = 5.783          # E38 registered means, 3 cards, over idle
RAIL = 4.337           # minion rail, 0.75 x board
LEDGER = {             # Q128 docs/reports/data/2026-10-27-transistor-ledger
    "gates": 0.306, "wire_in_cells": 0.620, "wire_between": 0.590, "internal": 0.431}
LEDGER_SWITCHING = 1.516       # = gates + wire_in_cells + wire_between (POWER.md, keep, randn)
LEDGER_CLOCK_SHARE = 0.327     # POWER.md
ROUTE = {              # Q129(a) 2026-10-27-q129-routed-netlist, the extraction at Miller k = 1
    "wire_between": 0.453, "switching": 1.379, "internal": 0.429, "clock_share": 0.267}
INTERNAL_FJ = 0.1188   # Q126(d) census-weighted internal energy per transition at 0.517 V
TAPEOUT = {"tree_zero": 1244.0, "tree_timed": 1871.0,
           "toggle_ratio": 1871.0 / 1244.0, "energy_ratio": 1.4}


def load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else None


def row(label, s, w=26):
    t = s["glitch_toggle_ratio"]
    e = s["k1"]["glitch_energy_ratio"]
    return (f"{label:<{w}} {s['zero_toggles_per_muladd']:9.1f} -> "
            f"{s['timed_toggles_per_muladd']:9.1f}  x{t:5.3f}   "
            f"{s['k1']['zero_pJ_per_muladd']:7.4f} -> {s['k1']['timed_pJ_per_muladd']:7.4f} pJ"
            f"  x{e:5.3f}")


def main():
    mx = load("glitch_mixed_full.json")
    kp = load("glitch_keep_full.json")
    ni = load("glitch_mixed_nointer.json")
    nc = load("glitch_mixed_nocond.json")
    ic = load("glitch_mixed_icarus.json")
    zd = load("glitch_mixed_zerodelta.json")
    chk = load("check_mixed.json")
    chkk = load("check_keep.json")
    out = sys.stdout

    def p(*a):
        print(*a, file=out)

    p("THE GLITCH FACTOR OF THE OPEN TensorFMA32, MEASURED        Q129(b), 27 Oct 2026")
    p("=" * 100)
    p("One random fp32 multiply-add (randn, 512 micro-ops), ASAP7 RVT TT, energy at 0.517 V.")
    p("Numerator: every physical edge in a timed gate-level run with the detailed-route SDF.")
    p("Denominator: the settled value per 1 ns vector step, which is what a zero-delay")
    p("simulator reports and what the published ledger priced.")
    p("")
    p("VALIDATION OF THE ENGINE (the zero-delay pass against Icarus's own zero-delay VCD)")
    for tag, c in (("mixed", chk), ("keep", chkk)):
        if not c:
            p(f"  {tag:6s} not run")
            continue
        p(f"  {tag:6s} gsim {c['gsim_total']:,} toggles over {c['gsim_nets']:,} nets; "
          f"Icarus {c['vcd_total']:,} over {c['vcd_nets']:,}; "
          f"nets differing {c['nets_differing']}; EXACT = {c['exact']}")
    p("")
    p("HEADLINE, the `mixed` netlist (the comparator), full SDF: cells + interconnect + COND")
    p(f"{'scope':<26} {'toggles/MAC':>9}    {'timed':>9}   ratio     "
      f"{'pJ/MAC at Miller k=1':>26}   ratio")
    for s in ("unit", "signal", "clock", "multiplier", "wallace_tree",
              "ppg", "wallace1", "wallace2", "prod_adder_64b"):
        p(row(s, mx["scopes"][s]))
    p("")
    u = mx["scopes"]["unit"]
    p(f"  nets that glitch: {u['nets_with_glitches']:,} of {u['nets']:,} that toggle at all; "
      f"nets that toggle LESS with delays: {u['nets_quieter']}")
    p(f"  the energy ratio over the Miller band: k=0 {u['k0']['glitch_energy_ratio']:.3f}, "
      f"k=1 {u['k1']['glitch_energy_ratio']:.3f}, k=2 {u['k2']['glitch_energy_ratio']:.3f}"
      "  (it barely moves: glitches are a count, not a capacitance)")
    cov = mx["coverage"]["k1"]
    p(f"  CAPACITANCE COVERAGE: {cov['cap_fraction_priced'] * 100:.1f}% of the extracted "
      f"{cov['cap_all_fF']:,.1f} fF is named by this simulation "
      f"({mx['netcap_nets']:,} extracted nets, {mx['netlist_nets']:,} netlist nets), against "
      "50.5%/56.3% published and 43.6%/51.8% in Q129(a).")
    p(f"  of those farads, {u['k1']['cap_priced_fF']:,.1f} fF "
      f"({u['k1']['cap_priced_fF'] / cov['cap_all_fF'] * 100:.1f}%) belongs to a net that "
      "toggles at all in a random multiply-add.")
    p("")
    p("SENSITIVITIES AND A SECOND INSTRUMENT (unit / Wallace tree, toggles then k=1 energy)")
    tbl = [("full SDF, mixed  (the number)", mx),
           ("  - no interconnect delay", ni),
           ("  - no (COND ...) paths", nc),
           ("full SDF, keep netlist", kp),
           ("Icarus, cell delays only*", ic),
           ("zero-delay delta events**", zd)]
    for lab, d in tbl:
        if not d:
            p(f"  {lab:<30} not run")
            continue
        a, b = d["scopes"]["unit"], d["scopes"]["wallace_tree"]
        p(f"  {lab:<30} unit x{a['glitch_toggle_ratio']:.3f} / "
          f"x{a['k1']['glitch_energy_ratio']:.3f}    tree x{b['glitch_toggle_ratio']:.3f} / "
          f"x{b['k1']['glitch_energy_ratio']:.3f}")
    p("   * Icarus cannot annotate any SDF containing an (INTERCONNECT ...) entry on this")
    p("     design, drops every (COND ...) path and has no CLK->Q delay on the behavioural")
    p("     flip-flop, and rounds every delay to the 10 ps precision of the bench's timescale.")
    p("     An upper bound, and an independent one.")
    p("  ** every zero-delay delta event counted instead of the settled value: a counting")
    p("     convention, not a measurement. It is LARGER than the timed count, so the glitch")
    p("     factor below is not an artefact of counting every edge.")
    p("")
    p("AGAINST THE RECORD")
    t = mx["scopes"]["wallace_tree"]
    p(f"  tape-out flow (tfma.glitch): tree {TAPEOUT['tree_zero']:.0f} -> "
      f"{TAPEOUT['tree_timed']:.0f} toggles/MAC, x{TAPEOUT['toggle_ratio']:.3f}, "
      f"x{TAPEOUT['energy_ratio']:.1f} in energy")
    p(f"  open flow, this run:         tree {t['zero_toggles_per_muladd']:.1f} -> "
      f"{t['timed_toggles_per_muladd']:.1f} toggles/MAC, x{t['glitch_toggle_ratio']:.3f}, "
      f"x{t['k1']['glitch_energy_ratio']:.3f} in energy")
    p(f"  so the open tree glitches {t['glitch_toggle_ratio'] / TAPEOUT['toggle_ratio']:.2f}x "
      f"as hard, and its energy factor is "
      f"{t['k1']['glitch_energy_ratio'] / TAPEOUT['energy_ratio']:.2f}x the record's.")
    p(f"  BUT the two flows' TIMED tree counts are "
      f"{TAPEOUT['tree_timed'] / t['timed_toggles_per_muladd']:.2f}x apart, against "
      f"{TAPEOUT['tree_zero'] / t['zero_toggles_per_muladd']:.2f}x at zero delay: counting "
      "glitches brings them together.")
    p(f"  Q124's \"glitches add about 40% to the tree's energy\" is the x1.4 above. In the tree "
      f"it is x{t['k1']['glitch_energy_ratio']:.2f}; at the WHOLE UNIT it is "
      f"x{u['k1']['glitch_energy_ratio']:.2f}, so a page that applied 1.4 to a unit-level")
    p("  figure was about right and one that applied it to the tree understated by 1.7x.")
    p("")
    p("WHAT IT DOES TO THE WATERFALL")
    sig = mx["scopes"]["signal"]
    re_ = sig["k1"]["glitch_energy_ratio"]
    rt = sig["glitch_toggle_ratio"]
    p(f"  the multipliers used: signal capacitance x{re_:.4f}, signal transitions x{rt:.4f};")
    p("  the clock tree does not glitch (x1.000 measured), so it is carried through unchanged.")
    p("")
    for name, sw, clks, intl, wb in (
            ("(A) the PUBLISHED ledger", LEDGER_SWITCHING, LEDGER_CLOCK_SHARE,
             LEDGER["internal"], LEDGER["wire_between"]),
            ("(B) Q129(a)'s revision", ROUTE["switching"], ROUTE["clock_share"],
             ROUTE["internal"], ROUTE["wire_between"])):
        clk = sw * clks
        sg = sw - clk
        sw2 = clk + sg * re_
        in2 = intl * rt
        p(f"  {name}: wire between the cells {wb:.3f} pJ")
        p(f"      switching {sw:.3f} -> {sw2:.3f} pJ   (clock {clk:.3f} held, "
          f"signal {sg:.3f} -> {sg * re_:.3f})")
        p(f"      cells' internal {intl:.3f} -> {in2:.3f} pJ")
        p(f"      BOTTOM-UP TOTAL {sw + intl:.3f} -> {sw2 + in2:.3f} pJ")
        p(f"      unaccounted against the board's {BOARD:.3f}: {BOARD - sw - intl:.3f} -> "
          f"{BOARD - sw2 - in2:.3f} pJ   (closure "
          f"{(sw + intl) / BOARD * 100:.1f}% -> {(sw2 + in2) / BOARD * 100:.1f}%)")
        p(f"      unaccounted against the rail's {RAIL:.3f}: {RAIL - sw - intl:.3f} -> "
          f"{RAIL - sw2 - in2:.3f} pJ")
        p("")
    p("  (C) MEASURED END TO END on this run - no published term reused, 100% of the")
    p("      extracted capacitance priced, the routed netlist simulated as built:")
    for k in (0, 1, 2):
        kk = f"k{k}"
        sz = u[kk]["zero_pJ_per_muladd"]
        st = u[kk]["timed_pJ_per_muladd"]
        iz = sig["zero_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
        it = sig["timed_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
        p(f"      Miller k={k}: switching {sz:.4f} -> {st:.4f} pJ, internal "
          f"{iz:.4f} -> {it:.4f} pJ, bottom-up {sz + iz:.4f} -> {st + it:.4f} pJ;")
        p(f"                 unaccounted {BOARD - sz - iz:.4f} -> {BOARD - st - it:.4f} pJ, "
          f"closure {(sz + iz) / BOARD * 100:.1f}% -> {(st + it) / BOARD * 100:.1f}%")
    p("")
    p("  Note (C)'s zero-delay bottom-up lands within 1% of the published 1.947 pJ by a")
    p("  coincidence of two errors cancelling: the published figure priced half the farads at")
    p("  a Steiner estimate that is 20% high, this one prices all of them at the extraction.")
    p("")
    p("WHAT THIS DOES NOT SETTLE")
    p("  - one stimulus (randn) and one netlist pair; the Hamming-ladder rungs were not run,")
    p("    so whether the fJ-per-flipped-bit slope carries the same factor is NOT measured.")
    p("  - the design misses its 1250 ps SDC by about 2x, so these delays belong to a netlist")
    p("    that would not run at 800 MHz; and the SDF is ASAP7 TT at 0.700 V while the energy")
    p("    is priced at the 0.517 V rail, where every delay would be longer.")
    p("  - inertial delay with full pulse rejection is the conservative model; a transport")
    p("    model would report more glitches.")


if __name__ == "__main__":
    main()
