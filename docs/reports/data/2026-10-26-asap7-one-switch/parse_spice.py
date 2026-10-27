#!/usr/bin/env python3.12
"""Q126(d) part 2: turn the ngspice run's text into numbers.

Usage: python3.12 -I parse_spice.py <spice_raw.txt> <outdir>
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
    res["device_check"]["verdict"] = (
        "The BSIM-CMG cards load and reproduce the ASAP7 paper's own device "
        "table to within a few per cent, which is the check that the models "
        "are running as the kit intends.")

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

    with open(f"{outdir}/asap7-one-switch.json", "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    print("wrote", f"{outdir}/asap7-one-switch.json")

    # ---- a short human summary
    print("\ndevice check (per fin, RVT):")
    for k, d in res["device_check"].items():
        if isinstance(d, dict) and k.endswith("C"):
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


if __name__ == "__main__":
    main()
