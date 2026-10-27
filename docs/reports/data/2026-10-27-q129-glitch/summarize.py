#!/usr/bin/env python3
"""Build summary.txt from this directory's glitch_*.json: the measured glitch factor, its
sensitivities, the comparison with the tape-out flow, and what it does to Q128's waterfall.

    python3 summarize.py > summary.txt
"""
import gzip
import json
import math
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


def _fit(xs, ys):
    """Least squares with a free intercept. Returns slope, intercept, the slope's standard
    error (2 degrees of freedom on a four-point fit) and the residuals. The SE is printed
    beside every slope: a four-point fit yields it directly, the ladder is markedly
    non-linear, and quoting four significant figures without it overstates the precision
    (corrected 27 Oct after verification)."""
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    m = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b = (sy - m * sx) / n
    res = [y - (m * x + b) for x, y in zip(xs, ys)]
    mx = sx / n
    se = math.sqrt((sum(r * r for r in res) / (n - 2)) / sum((x - mx) ** 2 for x in xs))
    return m, b, se, res


def ladder():
    """The ladder rungs, fitted over h >= 1 with a free intercept, zero delay against timed."""
    out = {}
    for part in ("lq", "lb"):
        z, t, zi, ti, rt, cs = {}, {}, {}, {}, {}, {}
        for h in (0, 1, 2, 4, 8):
            d = load(f"glitch_mixed_{part}_h{h}.json")
            if not d:
                return None
            u, s, c = d["scopes"]["unit"], d["scopes"]["signal"], d["scopes"]["clock"]
            z[h] = u["k1"]["zero_pJ_per_muladd"]
            t[h] = u["k1"]["timed_pJ_per_muladd"]
            zi[h] = z[h] + s["zero_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
            ti[h] = t[h] + s["timed_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
            rt[h] = u["glitch_toggle_ratio"]
            cs[h] = c["k1"]["zero_pJ_per_muladd"] / z[h]
        hs = [1, 2, 4, 8]
        mz, bz, sez, rz = _fit(hs, [z[h] for h in hs])
        mt, bt, set_, rtl = _fit(hs, [t[h] for h in hs])
        mzi, _, sezi, _ = _fit(hs, [zi[h] for h in hs])
        mti, _, seti, _ = _fit(hs, [ti[h] for h in hs])
        out[part] = {"z": z, "t": t, "rt": rt, "cs": cs,
                     "mz": mz * 1000, "mt": mt * 1000, "mzi": mzi * 1000, "mti": mti * 1000,
                     "sez": sez * 1000, "set": set_ * 1000,
                     "sezi": sezi * 1000, "seti": seti * 1000,
                     "bz": bz * 1000, "bt": bt * 1000,
                     "rz_fJ": [r * 1000 for r in rz], "rt_fJ": [r * 1000 for r in rtl]}
    return out


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
    nmiss = mx["netlist_nets"] - mx["netcap_nets"]
    p(f"  CAPACITANCE COVERAGE: {cov['cap_fraction_priced'] * 100:.1f}% of the EXTRACTED "
      f"{cov['cap_all_fF']:,.1f} fF is named by this simulation "
      f"({mx['netcap_nets']:,} extracted nets, {mx['netlist_nets']:,} netlist nets).")
    p(f"    EXACT BUT NARROWER THAN IT READS: {nmiss} netlist net names "
      f"({nmiss / mx['netlist_nets'] * 100:.1f}%) have NO extraction entry at all and")
    p("    are priced at zero. Exactly one of them moves - wallace_fC41_f2a_h[63], 16")
    p("    transitions against a settled count of 0, so a pure glitch - and its omission")
    p("    can therefore only understate the timed energy, by a nil amount.")
    p("    AND THE FRACTIONS IT IS COMPARED AGAINST COME FROM A DIFFERENT EXTRACTION:")
    p("    the published 50.5% is 23,762 of 47,093 fF of Steiner estimate on the keep")
    p("    netlist (56.3% the same on mixed), 43.6%/51.8% are Q129(a)'s, and this 100% is")
    p(f"    of the SPEF extraction's {cov['cap_all_fF']:,.0f} fF at k=1. One question, three")
    p("    denominators. What is strictly true here: no net this netlist contains is left")
    p("    unpriced for want of an extraction of it.")
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
    p("  THE SPREAD TO QUOTE. One instrument over two netlists and two SDF options reads")
    p("  x1.50-1.58 in toggles and x1.29-1.33 in energy at the unit. That is a hierarchy-and-")
    p("  options band, NOT an uncertainty: the second instrument in this very directory reads")
    p("  x1.762 / x1.444. ACROSS INSTRUMENTS the spread is x1.55-1.76 in toggles and")
    p("  x1.32-1.44 in energy, and that is the band to quote beside x1.572.")
    p("  The nearest matched pair is gsim cells-only (COND kept) x1.553 against Icarus")
    p("  cells-only (COND dropped) x1.762 - 13.5% apart. Of the three mechanisms the probe")
    p("  names, ONE CANNOT EXPLAIN IT: gsim has no CLK->Q delay either (sdf_bind")
    p("  iopath_missing = 1,974 of 42,486 input pins, the flip-flops and the clock")
    p("  gates), so simultaneous launch is COMMON to both instruments and makes both")
    p("  conservative. What is left is Icarus running 1,390 XOR2x2/XNOR2x2 at ZERO delay in")
    p("  the middle of the tree (gsim back-fills those pins from the conditional entries,")
    p("  iopath_from_cond = 2,780) and its 10 ps delay grid against gsim's femtoseconds.")
    p("  No run here separates the two, and --no-cond would NOT reproduce Icarus's zeroed")
    p("  XOR paths, so a like-for-like pass needs a change to gsim and not just a flag.")
    p("  Open, and recorded as such.")
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
    clk_sc = mx["scopes"]["clock"]
    re_ = sig["k1"]["glitch_energy_ratio"]
    rt = sig["glitch_toggle_ratio"]
    meas_clk = clk_sc["k1"]["zero_pJ_per_muladd"] / u["k1"]["zero_pJ_per_muladd"]
    p(f"  the multipliers used: signal capacitance x{re_:.4f}, signal transitions x{rt:.4f};")
    p("  the clock tree does not glitch (x1.000 measured), so it is carried through unchanged.")
    p("")
    p("  (C) MEASURED END TO END on this run, and THE ONE TO USE - no published term")
    p("      reused, 100% of the extracted capacitance priced, the routed netlist")
    p("      simulated as built. It is self-contained: do not compose it with Q129(a)'s")
    p("      or eda-cap's deltas, and do not quote (A) or (B) as this result's headline.")
    iz = sig["zero_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
    it = sig["timed_toggles_per_muladd"] * INTERNAL_FJ / 1000.0
    for k in (0, 1, 2):
        kk = f"k{k}"
        sz = u[kk]["zero_pJ_per_muladd"]
        st = u[kk]["timed_pJ_per_muladd"]
        p(f"      Miller k={k}: switching {sz:.4f} -> {st:.4f} pJ, internal "
          f"{iz:.4f} -> {it:.4f} pJ, bottom-up {sz + iz:.4f} -> {st + it:.4f} pJ;")
        p(f"                 unaccounted {BOARD - sz - iz:.4f} -> {BOARD - st - it:.4f} pJ, "
          f"closure {(sz + iz) / BOARD * 100:.1f}% -> {(st + it) / BOARD * 100:.1f}%")
    sz1, st1 = u["k1"]["zero_pJ_per_muladd"], u["k1"]["timed_pJ_per_muladd"]
    p(f"      SO: +{(st1 + it) - (sz1 + iz):.3f} pJ at k=1 moves from unaccounted to accounted,")
    p(f"      and the closure against the board goes "
      f"{(sz1 + iz) / BOARD * 100:.1f}% -> {(st1 + it) / BOARD * 100:.1f}% "
      "(band 41.3% at k=0 to 52.3% at k=2).")
    p("")
    p("  Note (C)'s zero-delay bottom-up lands within 1% of the published 1.947 pJ by a")
    p("  coincidence of two errors cancelling: the published figure priced half the farads at")
    p("  a Steiner estimate that is 20% high, this one prices all of them at the extraction.")
    p("")
    p("  (A) and (B) are BRIDGES ONLY - what this run's multipliers do to someone else's")
    p("      ledger, kept so the published and Q129(a) numbers can be followed. Each one")
    p("      composes this run's ratio onto a switching total from a different simulation,")
    p("      and each splits that total with a clock share that is NOT this run's.")
    p(f"      THE MISMATCH, as a number: this run measures the clock at "
      f"{meas_clk * 100:.2f}% of the")
    p(f"      unit's switching energy (k=1, zero delay, post-CTS routed netlist), against the")
    p(f"      {LEDGER_CLOCK_SHARE * 100:.1f}% (A) uses and the {ROUTE['clock_share'] * 100:.1f}% "
      f"(B) uses - {abs(meas_clk / ROUTE['clock_share'] - 1) * 100:.0f}% relative on (B),")
    p("      because Q129(a) repriced PRE-CTS toggle counts (477 clock toggles/MAC) against")
    p("      post-route capacitance while this run simulates the post-CTS netlist (658.6).")
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
        if name.startswith("(B)"):
            b_total = sw2 + in2
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
    clk = ROUTE["switching"] * meas_clk
    sg = ROUTE["switching"] - clk
    sw2 = clk + sg * re_ + ROUTE["internal"] * rt
    p(f"  (B) re-run with this run's own {meas_clk * 100:.2f}% clock share instead of "
      f"{ROUTE['clock_share'] * 100:.1f}%:")
    p(f"      BOTTOM-UP TOTAL {ROUTE['switching'] + ROUTE['internal']:.3f} -> {sw2:.3f} pJ, "
      f"closure {sw2 / BOARD * 100:.1f}% (not {b_total:.3f} pJ and "
      f"{b_total / BOARD * 100:.1f}%). The three")
    p("      waterfalls agree to within 0.11 pJ at k=1, which is the size of this")
    p("      inconsistency; (C) carries none of it.")
    p("")
    p("THE HAMMING LADDER: DOES THE fJ-PER-FLIPPED-BIT SLOPE CARRY THE SAME FACTOR?")
    p("  Both partners, h = 0, 1, 2, 4, 8, on the same routed netlist. Fitted the way E60's own")
    p("  reducer fits it: a line over h >= 1 with a free intercept, against the DESIGNED flips.")
    lad = ladder()
    if not lad:
        p("  not run")
    else:
        p("  Every slope carries the fit's own standard error (2 dof). The ladder is markedly")
        p("  non-linear (POWER.md's own trap 3), so the residuals are large and structured and")
        p("  these intervals are wide: every share below is good to about +-2 percentage")
        p("  points and no better, before and after.")
        p(f"  {'':<6} {'slope, switching only':<40} {'slope, + cells internal':<40} "
          f"{'E60 at the board':>18}")
        for part, lab, e60 in (("lq", "quiet partner A = 1.0", 116.7),
                               ("lb", "busy  partner A = pi ", 129.9)):
            r = lad[part]
            p(f"  {part:<6} {r['mz']:6.2f}+-{r['sez']:4.2f} -> {r['mt']:6.2f}+-{r['set']:4.2f} fJ"
              f"  x{r['mt'] / r['mz']:.3f}   "
              f"{r['mzi']:6.2f}+-{r['sezi']:4.2f} -> {r['mti']:6.2f}+-{r['seti']:4.2f} fJ"
              f"  x{r['mti'] / r['mzi']:.3f}   {e60:7.1f} fJ   ({lab})")
            p(f"         share of the board: switching "
              f"{r['mz'] / e60 * 100:.1f}+-{r['sez'] / e60 * 100:.1f}% -> "
              f"{r['mt'] / e60 * 100:.1f}+-{r['set'] / e60 * 100:.1f}%, with internal "
              f"{r['mzi'] / e60 * 100:.1f}+-{r['sezi'] / e60 * 100:.1f}% -> "
              f"{r['mti'] / e60 * 100:.1f}+-{r['seti'] / e60 * 100:.1f}%  (1 sigma)")
            p("         residuals of the timed fit, fJ: " + ", ".join(
                f"h{h}={v:+.1f}" for h, v in zip((1, 2, 4, 8), r['rt_fJ'])))
        p("  rung by rung, pJ per multiply-add at k=1 (zero delay -> timed):")
        for part in ("lq", "lb"):
            p(f"    {part}  " + "  ".join(
                f"h{h}={lad[part]['z'][h]:.4f}->{lad[part]['t'][h]:.4f}" for h in (0, 1, 2, 4, 8)))
        p("  the unit's own glitch factor by rung (toggles): " + ", ".join(
            f"lq_h{h} x{lad['lq']['rt'][h]:.3f}" for h in (0, 1, 2, 4, 8)))
        p(f"  so it is strongly ACTIVITY-DEPENDENT: x1.00 with the operands held still - at h0")
        p(f"  the clock is {lad['lq']['cs'][0] * 100:.1f}% (lq) and "
          f"{lad['lb']['cs'][0] * 100:.1f}% (lb) of the rung's energy MEASURED HERE, on this")
        p("  routed netlist, and the clock does not glitch - then x1.23 at h = 8, x1.57 at randn.")
        p("  (POWER.md's 97.6%/97.7% for the same rungs is its own keep-netlist figure, not this")
        p("  run's; the first version of this file quoted it as if it were measured here.)")
        p("  The SLOPE - the marginal cost of one more flipped bit, which is what the project's")
        p("  30%-of-the-board claim rests on - carries x1.28 (quiet) to x1.34 (busy) on switching,")
        p("  and x1.32 to x1.38 with the cells' internal energy. So the published")
        p('  "about 30% of what the board pays, about 40% with internal energy" becomes')
        p("  ABOUT 38% (1 sigma +-2 pp) and ABOUT 55% (+-3 pp). Those two words carry the")
        p("  precision: 38.4% and 54.6% do not.")
        p("  FIT WINDOWS. On POWER.md's own window (h >= 1, four rungs) the ratio is x1.278")
        p("  (lq) and x1.336 (lb). Leave one rung out and it runs x1.237-1.285 (lq) and")
        p("  x1.309-1.554 (lb); the widest excursion in both is the window that drops h = 8,")
        p("  the longest lever. Include h = 0 and the ratio holds (x1.271 / x1.281) but the")
        p("  absolute share jumps (lb 37.4% -> 48.0%), which is why the h >= 1 window is kept:")
        p("  it is the convention POWER.md's own figure was fitted on, so the before/after is")
        p("  like-for-like. ABOUT 1.3 is what these fits support, not 1.278 and 1.336.")
    p("")
    p("A FUNCTIONAL CHECK ON THE TIMED RUN (positive evidence, and a caveat)")
    zz = json.load(gzip.open(os.path.join(HERE, "toggles_mixed_zero.json.gz")))
    tz = json.load(gzip.open(os.path.join(HERE, "toggles_mixed_timed.json.gz")))
    nz, nt = zz["all_nets"], tz["all_nets"]
    sz_, st_ = zz["settled"], tz["settled"]
    if isinstance(sz_, dict):
        sz_ = [sz_.get(n, 0) for n in nz]
        st_ = [st_.get(n, 0) for n in nt]
    nd = sum(1 for a, b in zip(sz_, st_) if a != b)
    p(f"  the timed run's own SETTLED count is {tz['total_settled']:,} against the zero run's")
    p(f"  {zz['total_settled']:,}: +{(tz['total_settled'] / zz['total_settled'] - 1) * 100:.3f}% "
      f"over {nd} nets of {len(nz):,}. So the two passes compute the same")
    p("  function to 1 part in 900, which they must for the ratio to mean anything - worth")
    p("  stating because the netlist misses its SDC by about 2x. Using the timed run's own")
    p(f"  settled as the denominator instead gives x"
      f"{tz['total_transitions'] / tz['total_settled']:.4f} at the whole design against")
    p(f"  x{tz['total_transitions'] / zz['total_settled']:.4f}: a 0.1% effect on the headline, "
      "and the published convention (the")
    p("  zero-delay pass is the denominator) is the one used.")
    p("")
    p("WHAT THIS DOES NOT SETTLE")
    p("  - one tile per pattern and one netlist pair; no repeat, so no repeat-variance")
    p("    interval. The LADDER fits do carry a regression interval and it is printed above")
    p("    (4-9% on the slopes); the headline ratios carry no interval at all.")
    p("  - the design misses its 1250 ps SDC by about 2x, so these delays belong to a netlist")
    p("    that would not run at 800 MHz; and the SDF is ASAP7 TT at 0.700 V while the energy")
    p("    is priced at the 0.517 V rail, where every delay would be longer.")
    p("  - inertial delay with full pulse rejection is the conservative model; a transport")
    p("    model would report more glitches.")
    p("  - 4.6% of the 'timed' netlist ran at ZERO delay in gsim too: sdf_bind")
    p("    iopath_missing = 1,974 of 42,486 input-pin paths, essentially every flip-flop's and")
    p("    clock gate's CLK->Q, because the behavioural stand-in asap7_seq_behav.v carries no")
    p("    specify block. gsim therefore launches every flip-flop simultaneously, removing the")
    p("    launch skew that would deepen these glitches: x1.572 is conservative on that axis")
    p("    too. The probe faults Icarus for exactly this; it is only fair to fault gsim for it.")
    p("  - WHICH FLOOR-REASON EACH RUN RETIRED, of Q126(e)'s three: Q129(a) retired the")
    p("    coupling/SPEF one (detailed route closed, coupling extracted, and the wire turned")
    p("    out not to be a floor at all); THIS run retires the coverage one (the routed")
    p("    netlist is what is simulated, so no extracted net goes unpriced). The third - the")
    p("    ledger covers one lane's arithmetic while the board also pays for the register-file")
    p("    read ports, the operand bus, the result path, pipeline registers and leakage -")
    p("    stands untouched by either.")
    p("")
    p("WHAT THE FIRST VERSION OF THIS FILE GOT WRONG   (corrected 27 Oct, after verification)")
    p("  1. It led with waterfall (B) - 1.810 -> 2.598 pJ, closure 31.3% -> 44.9%, '+0.790 pJ'")
    p("     - the composition its own open issues told the integrator not to make, and (B)")
    p("     splits Q129(a)'s switching total with Q129(a)'s 26.7% clock share while this run")
    p("     measures 32.88% on the same netlist. (C) now leads: 1.925 -> 2.706 pJ, +0.781 pJ,")
    p("     closure 33.3% -> 46.8%.")
    p("  2. It quoted x1.50-1.57 / x1.29-1.33 as 'the honest band' while its own second")
    p("     instrument read x1.762 / x1.444. The cross-instrument spread is now quoted.")
    p("  3. It quoted the ladder slopes to four figures with no interval. The regression SEs")
    p("     are now printed: 4-9% on the slopes, +-2 pp on the headline share.")
    p("  4. It said 'the clock is 97.6% of that rung' as if measured here; 97.6%/97.7% is")
    p("     POWER.md's keep-netlist figure. This run measures 97.9% (lq) and 97.8% (lb).")
    p("  5. 'the committed randn.vec' was false - no .vec was committed. All eleven are now,")
    p("     gzipped, in stimulus/ (the netlists and the SDF still are not: 3-21 MB each,")
    p("     identified by sha256 in versions.txt and regenerable from Q129(a)'s flow).")
    p("  6. '100% of the extracted capacitance' needed the clause now beside it, and the")
    p("     settled-divergence and CLK->Q checks above were not stated at all.")


if __name__ == "__main__":
    main()
