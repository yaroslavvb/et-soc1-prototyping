#!/usr/bin/env python3.12
"""Q126(d) part 2: turn the ngspice run's text into numbers.

Usage: python3.12 -I parse_spice.py <spice_raw.txt> <outdir>
                                    [<fixup.log> [<part1.json>]]

<fixup.log> is the second run added after review: FAx1 with its carry-out load
removed, FAx1 in all four hold states, and NAND2x1 / XOR2x1 in the states whose
liberty arcs they should be compared against.  <part1.json> is part 1's
`asap7-cell-energies.json`; when given, the SPICE numbers are set against the
matching liberty arc AND STATE, which is the only fair comparison.
"""
import json
import re
import sys

VDDS = {"0p517": 0.517, "0p700": 0.700}
Q = 1.602176634e-19


def split_decks(text):
    out, name, buf = {}, None, []
    for line in text.split("\n"):
        if line.startswith("===DECK "):
            if name:
                out[name] = "\n".join(buf)
            name, buf = line[8:].strip(), []
        elif line.startswith("===ALLDONE"):
            break
        else:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf)
    return out


def meas(block):
    """`meas` prints `name = value`; also catch `print`ed branch currents."""
    d = {}
    for m in re.finditer(r'^\s*(\w+)\s*=\s*(-?[\d.]+e?[-+]?\d*)', block, re.M):
        d[m.group(1)] = float(m.group(2))
    for m in re.finditer(r'^(\w+#branch)\s*=?\s*(-?[\d.]+e?[-+]?\d*)',
                         block, re.M):
        d[m.group(1)] = float(m.group(2))
    # `print i(vda)` prints `i(vda) = 3.7e-10`
    for m in re.finditer(r'i\((\w+)\)\s*=\s*(-?[\d.]+e?[-+]?\d*)', block, re.I):
        d[m.group(1).lower() + "#branch"] = float(m.group(2))
    return d


def cycle_energy(m, vdd, cl_fF):
    """Rail charge over one full cycle -> rail, load and internal energy."""
    q = m["qd2"] - m["qd0"]
    e_rail = q * vdd * 1e15
    e_load = cl_fF * 1e-15 * vdd ** 2 * 1e15
    return {"E_rail_per_cycle_fJ": e_rail, "E_load_per_cycle_fJ": e_load,
            "E_internal_per_cycle_fJ": e_rail - e_load}


def fixups(text, res, part1_path=None):
    """The second run, added after review.

    Three things the first version could not say:
      1. how much of FAx1's measured internal energy was the 0.5 fF load the
         deck hung on its carry-out pin, which `internal = rail - C_load V^2`
         never subtracted;
      2. how far a full adder's arc energy moves with its hold state;
      3. whether the schematic netlist really runs UNDER the liberty for
         every cell, which the first version generalised from one.
    """
    decks = split_decks(text)
    out = {"what": fixups.__doc__.strip()}

    # 1. FAx1 with and without the carry-out load
    con = {}
    for v, vdd in VDDS.items():
        rows = {}
        for name, b in decks.items():
            mm = re.match(rf"fa_noc_{v}_([\dp]+)\.sp$", name)
            if not mm:
                continue
            cl = float(mm.group(1).replace("p", "."))
            m = meas(b)
            if "qd2" not in m:
                continue
            d = cycle_energy(m, vdd, cl)
            d["Cload_fF"] = cl
            d["CON_swing_V"] = [m.get("con_min"), m.get("con_max")]
            rows[mm.group(1)] = d
        b = decks.get(f"fa_cc_{v}_2p0.sp")
        if b and rows.get("2p0"):
            m = meas(b)
            with_cc = cycle_energy(m, vdd, 2.0)
            no_cc = rows["2p0"]
            con[v] = {
                "with_Ccout_0p5fF_E_internal_fJ":
                    with_cc["E_internal_per_cycle_fJ"],
                "without_Ccout_E_internal_fJ":
                    no_cc["E_internal_per_cycle_fJ"],
                "contamination_fJ": (with_cc["E_internal_per_cycle_fJ"]
                                     - no_cc["E_internal_per_cycle_fJ"]),
                "CON_swing_with_Ccout_V": [m.get("con_min"), m.get("con_max")],
                "CON_swing_without_Ccout_V": no_cc["CON_swing_V"],
            }
        out.setdefault("FAx1_no_CON_load", {})[v] = rows
    out["FAx1_CON_load_contamination"] = con
    out["FAx1_CON_note"] = (
        "CON is the INVERTED carry-out, so with B = CI = 0 it sits HIGH and "
        "never switches -- it only glitches as A toggles. The committed "
        "energy decks hang Ccout = 0.5 fF on it, and that glitch charge was "
        "booked as FAx1's internal energy. The corrected FAx1 energies, with "
        "no CON load, are in FAx1_no_CON_load.")

    # 2. FAx1 by hold state
    for v, vdd in VDDS.items():
        st = {}
        for name, b in decks.items():
            mm = re.match(rf"fa_st_{v}_B(\d)CI(\d)\.sp$", name)
            if not mm:
                continue
            m = meas(b)
            if "qd2" not in m:
                continue
            st[f"B={mm.group(1)} CI={mm.group(2)}"] = cycle_energy(m, vdd, 2.0)
        if st:
            vals = [d["E_internal_per_cycle_fJ"] for d in st.values()]
            out.setdefault("FAx1_by_hold_state", {})[v] = {
                "by_state": st, "min_fJ": min(vals), "max_fJ": max(vals),
                "mean_fJ": sum(vals) / len(vals),
                "spread_x": max(vals) / min(vals) if min(vals) else None,
            }

    # 3. SPICE against the liberty, arc AND state matched
    cmp_rows, spice = {}, {}
    lib = None
    if part1_path:
        try:
            lib = json.load(open(part1_path))["cells"]
        except Exception:                                 # noqa: BLE001
            lib = None

    def lib_cycle(cell, ipin, state):
        """What the liberty charges for toggling `ipin` in `state`: the SUM
        over every output this input drives in that state.

        This matters for the full adder. With exactly one of B, CI high, the
        carry-out CON follows A as well as SN does, so the cell delivers two
        output transitions and the liberty carries two arcs for that state.
        Comparing SPICE against A->SN alone there would be half the answer.
        """
        if not lib:
            return None, []
        tot, used = 0.0, []
        for arc, a in lib.get(cell, {}).get("arcs", {}).items():
            if not arc.startswith(ipin + "->"):
                continue
            s = a["by_state"].get(state)
            if s is None:
                continue
            tot += s["E_int_per_cycle_VDDonly_fJ"]
            used.append(arc)
        return (tot if used else None), used

    # (deck, cell, input pin, liberty `when` state, load)
    WANT = [("nand_B1_{v}.sp", "NAND2x1", "A", "(any)", 2.0),
            ("xor_B1_{v}.sp", "XOR2x1", "A", "B", 2.0),
            ("xor_B0_{v}.sp", "XOR2x1", "A", "!B", 2.0),
            ("fa_st_{v}_B0CI0.sp", "FAx1", "A", "(!B * !CI)", 2.0),
            ("fa_st_{v}_B1CI1.sp", "FAx1", "A", "(B * CI)", 2.0),
            ("fa_st_{v}_B0CI1.sp", "FAx1", "A", "(!B * CI)", 2.0),
            ("fa_st_{v}_B1CI0.sp", "FAx1", "A", "(B * !CI)", 2.0)]
    for tmpl, cell, ipin, state, cl in WANT:
        for v, vdd in VDDS.items():
            b = decks.get(tmpl.format(v=v))
            if b is None:
                continue
            m = meas(b)
            if "qd2" not in m:
                continue
            d = cycle_energy(m, vdd, cl)
            spice[(cell, ipin, state, v)] = d["E_internal_per_cycle_fJ"]
            if v != "0p700":
                continue          # the liberty is characterised at 0.7 V only
            lv, used = lib_cycle(cell, ipin, state)
            cmp_rows[f"{cell} {ipin} [{state}]"] = {
                "SPICE_E_internal_per_cycle_fJ": d["E_internal_per_cycle_fJ"],
                "liberty_E_int_per_cycle_VDDonly_fJ": lv,
                "liberty_arcs_summed": used,
                "spice_over_liberty": (d["E_internal_per_cycle_fJ"] / lv
                                       if lv else None),
            }
    # the inverter's rows come from the first run's own decks
    for v, vdd in VDDS.items():
        e = res["energy"].get("INVx1", {}).get(v, {}).get("2p0")
        if not e:
            continue
        spice[("INVx1", "A", "(any)", v)] = e["E_internal_per_cycle_fJ"]
        if v != "0p700":
            continue
        lv, used = lib_cycle("INVx1", "A", "(any)")
        if lv:
            cmp_rows["INVx1 A [(any)]"] = {
                "SPICE_E_internal_per_cycle_fJ": e["E_internal_per_cycle_fJ"],
                "liberty_E_int_per_cycle_VDDonly_fJ": lv,
                "liberty_arcs_summed": used,
                "spice_over_liberty": e["E_internal_per_cycle_fJ"] / lv,
            }
    out["spice_vs_liberty_0p7V"] = cmp_rows
    r07 = {k: v["spice_over_liberty"] for k, v in cmp_rows.items()
           if v["spice_over_liberty"]}
    if r07:
        lo_k = min(r07, key=r07.get)
        hi_k = max(r07, key=r07.get)
        out["spice_vs_liberty_verdict"] = (
            "At 0.7 V and 2 fF, with the arc, the state and the set of "
            "outputs driven all matched, the schematic netlist runs "
            f"{r07[lo_k]:.2f}x ({lo_k}) to {r07[hi_k]:.2f}x ({hi_k}) of the "
            "liberty's VDD-only figure, over "
            f"{len(r07)} cases. IT GOES BOTH WAYS. So a schematic SPICE "
            "energy is NOT a general lower bound on the extracted one: the "
            "first version of this file said it was, generalising from the "
            "inverter alone, and carried the 2.04x schematic-vs-extracted "
            "DELAY ratio across to energy with no measurement behind it. "
            "Corrected in review the same day. The only honest statement is "
            "that the two agree to within about +-35% per case, with no "
            "systematic sign.")
        out["spice_vs_liberty_caveat"] = (
            "The decks drive a 5 ps (0-100%) input edge while the liberty "
            "figures are interpolated at a 10 ps (10-90%) slew; from the "
            "short-circuit sweep that is worth under 0.01 fJ per cycle for "
            "INVx1, so it does not change the sign of any row. The liberty "
            "is characterised at 0.7 V, so only the 0.7 V decks are "
            "compared with it.")

    # 4. does internal energy really scale as V^2 between the two rails?
    vs = {}
    for (cell, ipin, state, v), e in spice.items():
        if v != "0p700":
            continue
        lo = spice.get((cell, ipin, state, "0p517"))
        if not lo:
            continue
        vs[f"{cell} {ipin} [{state}]"] = {
            "E_0p700_fJ": e, "E_0p517_fJ": lo, "measured_ratio": lo / e}
    if vs:
        rs = [d["measured_ratio"] for d in vs.values()]
        out["voltage_scaling_check"] = {
            "by_case": vs,
            "V2_ratio_assumed": (0.517 / 0.700) ** 2,
            "measured_range": [min(rs), max(rs)],
            "verdict": ("Part 1 scales internal energy from 0.7 V to 0.517 V "
                        f"by (0.517/0.7)^2 = {(0.517/0.7)**2:.4f}. SPICE "
                        f"measures {min(rs):.3f} to {max(rs):.3f} for the "
                        "same cells, so the V^2 rule is CONSERVATIVE by "
                        f"{100*(1 - min(rs)/((0.517/0.7)**2)):.0f}-"
                        f"{100*(1 - max(rs)/((0.517/0.7)**2)):.0f}% -- the "
                        "short-circuit and internal-node terms fall faster "
                        "than V^2, as the short-circuit sweep also shows. "
                        "Part 1's 0.517 V column is therefore a slight "
                        "overestimate, in the direction it already claims."),
        }
    return out


def main():
    raw = open(sys.argv[1], errors="replace").read()
    outdir = sys.argv[2]
    decks = split_decks(raw)
    res = {"decks_run": len(decks), "device_check": {}, "fo4": {},
           "energy": {}, "short_circuit": {}, "leakage": {}}

    # ---- device check against the ASAP7 paper's Tables 3 and 4
    PAPER = {"Idsat_n_uA": 37.85, "Ioff_n_nA": 0.019, "SS_n_mV_dec": 63.03,
             "Idsat_p_uA": 32.88, "Ioff_p_nA": 0.023, "SS_p_mV_dec": 64.48}
    for t in (25, 80):
        b = decks.get(f"dev_{t}.sp")
        if not b:
            continue
        m = meas(b)
        ss = None
        if "vg_1n" in m and "vg_10n" in m:
            ss = (m["vg_10n"] - m["vg_1n"]) * 1000.0      # mV per decade
        res["device_check"][f"{t}C"] = {
            "Idsat_n_uA": abs(m.get("idsat_n", 0)) * 1e6,
            "Ioff_n_nA": abs(m.get("ioff_n", 0)) * 1e9,
            "Idlin_n_uA": abs(m.get("idlin_n", 0)) * 1e6,
            "SS_n_mV_dec": ss,
            "Idsat_p_uA": abs(m.get("idsat_p", 0)) * 1e6,
            "Ioff_p_nA": abs(m.get("ioff_p", 0)) * 1e9,
        }
    res["device_check"]["asap7_paper_TT_25C_per_fin"] = PAPER
    # state the tolerance per quantity rather than one blanket figure: the
    # drive currents and the slope land within 5%, the off-currents do not
    d25 = res["device_check"].get("25C", {})
    dev = {}
    for k, paper in PAPER.items():
        got = d25.get(k)
        if got:
            dev[k] = {"spice": got, "paper": paper,
                      "error_pct": 100.0 * (got - paper) / paper}
    res["device_check"]["deviation_vs_paper_25C"] = dev
    res["device_check"]["verdict"] = (
        "The BSIM-CMG cards load and run as the kit intends: the DRIVE "
        "CURRENTS and the SUBTHRESHOLD SLOPE land within 5% of the ASAP7 "
        "paper's own table, while the OFF-CURRENTS are 9% (NMOS) and 19% "
        "(PMOS) under it. The paper prints I_off to two significant figures "
        "and an off-current is exponentially sensitive to the threshold, so "
        "that is the expected size of disagreement -- but it is not 5%, and "
        "the leakage section below is built on those off-currents, so the "
        "wider tolerance travels with it. (The first version of this file "
        "said 'every figure within about 5%'; corrected in review the same "
        "day.)")

    # ---- FO4
    for v, vv in VDDS.items():
        b = decks.get(f"fo4_{v}.sp")
        if not b:
            continue
        m = meas(b)
        if "tout_r" not in m:
            continue
        dr = (m["tout_r"] - m["tin_f"]) * 1e12
        df = (m["tout_f"] - m["tin_r"]) * 1e12
        res["fo4"][v] = {
            "VDD_V": vv, "delay_rise_ps": dr, "delay_fall_ps": df,
            "FO4_ps": 0.5 * (dr + df),
            "out_slew_rise_ps": m.get("slew_r", 0) * 1e12,
            "out_slew_fall_ps": m.get("slew_f", 0) * 1e12,
        }

    # ---- energy per edge
    for name, b in decks.items():
        mm = re.match(r"en_(\w+?)_(0p\d+)_([\dp]+)\.sp", name)
        if not mm:
            continue
        cell, v, cls = mm.groups()
        cl = float(cls.replace("p", "."))
        vdd = VDDS[v]
        m = meas(b)
        if "qd2" not in m:
            continue
        # output FALLS on the first event, RISES on the second
        qd_fall = m["qd1"] - m["qd0"]
        qd_rise = m["qd2"] - m["qd1"]
        qs_fall = m["qs1"] - m["qs0"]
        qs_rise = m["qs2"] - m["qs1"]
        q_cycle = m["qd2"] - m["qd0"]
        e_rail_cycle = q_cycle * vdd                      # J
        e_load_cycle = cl * 1e-15 * vdd ** 2              # J
        res["energy"].setdefault(cell, {}).setdefault(v, {})[cls] = {
            "Cload_fF": cl, "VDD_V": vdd,
            "q_rail_per_cycle_C": q_cycle,
            "E_rail_per_cycle_fJ": e_rail_cycle * 1e15,
            "E_load_per_cycle_fJ": e_load_cycle * 1e15,
            "E_internal_per_cycle_fJ": (e_rail_cycle - e_load_cycle) * 1e15,
            "E_rail_rise_fJ": qd_rise * vdd * 1e15,
            "E_rail_fall_fJ": qd_fall * vdd * 1e15,
            "q_vss_rise_C": qs_rise, "q_vss_fall_C": qs_fall,
            "electrons_per_cycle": q_cycle / Q,
        }

    # ---- short circuit vs input edge time
    for name, b in decks.items():
        mm = re.match(r"sc_(0p\d+)_(\d+)\.sp", name)
        if not mm:
            continue
        v, tr = mm.groups()
        vdd = VDDS[v]
        m = meas(b)
        if "qs2" not in m:
            continue
        # on the OUTPUT RISE the pull-down should be off, so whatever charge
        # reaches VSS in that window crossed both devices at once
        q_sc = m["qs2"] - m["qs1"]
        res["short_circuit"].setdefault(v, {})[tr] = {
            "input_edge_ps": int(tr), "VDD_V": vdd,
            "q_vss_during_output_rise_C": q_sc,
            "E_rail_per_cycle_fJ": (m["qd2"] - m["qd0"]) * vdd * 1e15,
        }
    # short-circuit energy = the rail energy a slow edge costs ABOVE the
    # fastest edge. The charge that reaches VSS during the output rise is
    # dominated by the falling input's gate coupling, so it is kept as raw
    # data, not read as short circuit.
    for v, byt in res["short_circuit"].items():
        base = min(d["E_rail_per_cycle_fJ"] for d in byt.values())
        for d in byt.values():
            d["E_excess_over_cheapest_edge_fJ"] = d["E_rail_per_cycle_fJ"] - base
    res["short_circuit_method"] = (
        "INVx1, 2 fF load, driven by an ideal edge of the stated 0-100% "
        "length. The capacitive part of the rail energy does not depend on "
        "the input edge, so the rise above the fastest edge's value is the "
        "short-circuit (both-devices-on) energy. The curve is U-shaped at 0.7 V: fast edges cost extra through gate-drain (Miller) coupling, slow edges through short circuit, so the excess is quoted over the CHEAPEST edge, not the fastest.")

    # ---- leakage
    for name, b in decks.items():
        mm = re.match(r"leak_(\d+)_(0p\d+)\.sp", name)
        if not mm:
            continue
        t, v = mm.groups()
        vdd = VDDS[v]
        m = meas(b)
        ia = abs(m.get("vda#branch", 0.0))
        ib = abs(m.get("vdb#branch", 0.0))
        res["leakage"].setdefault(v, {})[f"{t}C"] = {
            "VDD_V": vdd, "temp_C": int(t),
            "INVx1_in_low_pW": ia * vdd * 1e12,
            "INVx1_in_high_pW": ib * vdd * 1e12,
            "INVx1_mean_pW": 0.5 * (ia + ib) * vdd * 1e12,
            "nmos_1fin_pW": abs(m.get("vdn#branch", 0.0)) * vdd * 1e12,
            "pmos_1fin_pW": abs(m.get("vsp#branch", 0.0)) * vdd * 1e12,
        }
    res["leakage"]["liberty_reference"] = {
        "INVx1_state_averaged_pW_0p7V_25C": 51.1588,
        "note": "asap7sc7p5t_INVBUF_RVT_TT, the unconditioned VDD entry.",
    }

    res["energy_note"] = (
        "These are the FIRST run's decks. Two caveats, both settled by the "
        "fix-up run in `fixups`: the FAx1 decks hang Ccout = 0.5 fF on the "
        "carry-out pin, which `internal = rail - C_load V^2` does not "
        "subtract (worth +0.0007 fJ per cycle at 0.7 V, 0.2%), and the FAx1 "
        "rows are the B = CI = 0 hold state only, which is the cheapest of "
        "four by 1.8x. Use `fixups.FAx1_no_CON_load` and "
        "`fixups.FAx1_by_hold_state` for the full adder. NAND2x1 is B = 1, "
        "the only state in which Y follows A.")

    # ---- the review fix-up run
    if len(sys.argv) > 3:
        res["fixups"] = fixups(open(sys.argv[3], errors="replace").read(),
                               res,
                               sys.argv[4] if len(sys.argv) > 4 else None)

    with open(f"{outdir}/asap7-one-switch.json", "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print("wrote", f"{outdir}/asap7-one-switch.json")

    # ---- a short human summary
    print("\ndevice check (per fin, RVT):")
    for k, d in res["device_check"].items():
        if isinstance(d, dict) and re.fullmatch(r"\d+C", k):
            print(f"  {k}: Idsat_n {d['Idsat_n_uA']:.2f} uA  Ioff_n "
                  f"{d['Ioff_n_nA']:.4f} nA  SS {d['SS_n_mV_dec'] or 0:.1f} mV/dec  "
                  f"Idsat_p {d['Idsat_p_uA']:.2f} uA  Ioff_p {d['Ioff_p_nA']:.4f} nA")
    print(f"  paper TT 25 C: {PAPER}")
    print("\nFO4:")
    for v, d in res["fo4"].items():
        print(f"  {d['VDD_V']} V: {d['FO4_ps']:.2f} ps "
              f"(rise {d['delay_rise_ps']:.2f}, fall {d['delay_fall_ps']:.2f}, "
              f"out slew {d['out_slew_rise_ps']:.1f}/{d['out_slew_fall_ps']:.1f} ps)")
    print("\nenergy per cycle (fJ), internal = rail - C*V^2:")
    for cell, byv in res["energy"].items():
        for v, byl in byv.items():
            s = "  ".join(f"{d['Cload_fF']}fF {d['E_internal_per_cycle_fJ']:.4f}"
                          for _k, d in sorted(byl.items(),
                                              key=lambda x: x[1]["Cload_fF"]))
            print(f"  {cell:9s} {VDDS[v]} V: {s}")
    print("\nshort circuit: rail energy/cycle above the cheapest edge, fJ:")
    for v, byt in res["short_circuit"].items():
        if v.endswith("method"):
            continue
        s = "  ".join(f"{d['input_edge_ps']}ps {d['E_excess_over_cheapest_edge_fJ']:+.4f}"
                      for _k, d in sorted(byt.items(),
                                          key=lambda x: x[1]["input_edge_ps"]))
        print(f"  {VDDS[v]} V: {s}")
    print("\nleakage (pW):")
    for v, byt in res["leakage"].items():
        if v == "liberty_reference":
            continue
        for t, d in sorted(byt.items()):
            print(f"  {d['VDD_V']} V {t}: INVx1 mean {d['INVx1_mean_pW']:.2f}  "
                  f"nmos/fin {d['nmos_1fin_pW']:.3f}  pmos/fin {d['pmos_1fin_pW']:.3f}")

    fx = res.get("fixups")
    if fx:
        print("\nFAx1, CON load removed (internal fJ per cycle):")
        for v, rows in sorted(fx.get("FAx1_no_CON_load", {}).items()):
            s = "  ".join(f"{d['Cload_fF']}fF {d['E_internal_per_cycle_fJ']:.4f}"
                          for _k, d in sorted(rows.items(),
                                              key=lambda x: x[1]["Cload_fF"]))
            print(f"  {VDDS[v]} V: {s}")
        for v, d in sorted(fx.get("FAx1_CON_load_contamination", {}).items()):
            print(f"  {VDDS[v]} V @2 fF: with Ccout "
                  f"{d['with_Ccout_0p5fF_E_internal_fJ']:.4f}, without "
                  f"{d['without_Ccout_E_internal_fJ']:.4f}, booked in error "
                  f"{d['contamination_fJ']:+.4f} fJ")
        print("\nFAx1 by hold state (internal fJ per cycle, 2 fF):")
        for v, d in sorted(fx.get("FAx1_by_hold_state", {}).items()):
            s = "  ".join(f"[{k}] {x['E_internal_per_cycle_fJ']:.4f}"
                          for k, x in sorted(d["by_state"].items()))
            print(f"  {VDDS[v]} V: {s}  (spread {d['spread_x']:.2f}x)")
        print("\nSPICE vs liberty at 0.7 V, arc + state + outputs matched "
              "(fJ per cycle, 2 fF):")
        for k, d in sorted(fx.get("spice_vs_liberty_0p7V", {}).items()):
            if d["liberty_E_int_per_cycle_VDDonly_fJ"] is None:
                continue
            print(f"  {k:30s} SPICE {d['SPICE_E_internal_per_cycle_fJ']:7.4f}  "
                  f"liberty {d['liberty_E_int_per_cycle_VDDonly_fJ']:7.4f}  "
                  f"ratio {d['spice_over_liberty']:.2f}x")
        vsc = fx.get("voltage_scaling_check")
        if vsc:
            print(f"\n0.517/0.7 internal-energy ratio (V^2 assumes "
                  f"{vsc['V2_ratio_assumed']:.4f}):")
            for k, d in sorted(vsc["by_case"].items()):
                print(f"  {k:30s} {d['measured_ratio']:.4f}")


if __name__ == "__main__":
    main()
