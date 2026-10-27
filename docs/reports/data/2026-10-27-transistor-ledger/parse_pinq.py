#!/usr/bin/env python3
"""Q128(d): reduce the per-cell pin-charge run to charge per driven gate pin
and per fin, weighted by the mix of cells this design actually drives.

  parse_pinq.py <pinq.log> <meta.json> <fanout2.json> <out.json>
"""
import json
import re
import sys
from collections import defaultdict

E = 1.602176634e-19


def read_log(path):
    out, cur = {}, None
    mre = re.compile(r'^(\w+)\s*=\s*([-+0-9.eE]+)\s*$')
    for line in open(path, errors="replace"):
        if line.startswith("### "):
            cur = line[4:].strip()
            out[cur] = {}
            continue
        if cur is None:
            continue
        m = mre.match(line.strip())
        if m:
            try:
                out[cur][m.group(1)] = float(m.group(2))
            except ValueError:
                pass
    return out


def main():
    logp, metap, fanp, outp = sys.argv[1:5]
    log = read_log(logp)
    meta = json.load(open(metap))
    fan = json.load(open(fanp))
    mix = fan["driven_cell_mix_by_toggle_weighted_pins"]

    per, dropped = {}, {}
    for deck, m in log.items():
        md = meta.get(deck)
        if md is None:
            continue
        if "qi_hi" not in m:
            dropped[deck] = {"why": "ngspice aborted this deck (timestep too small): no "
                                    "measurement was written"}
            continue
        q = m["qi_hi"] - m["qi_lo"]
        vdd = md["vdd"]
        # A gate fin cannot take 100 aC at these rails; a value that large is a
        # convergence failure, not a measurement.  Drop it and say so.
        if abs(q) * 1e18 / md["fins_gated_by_this_pin"] > 100:
            dropped[deck] = {"Q_per_fin_aC": q * 1e18 / md["fins_gated_by_this_pin"],
                             "why": "non-physical: ngspice did not converge on this deck"}
            continue
        per[deck] = dict(md)
        per[deck].update({
            "Q_into_pin_C": q, "Q_into_pin_aC": q * 1e18,
            "electrons": q / E,
            "E_from_VDD_on_this_edge_aJ": q * vdd * 1e18,
            "C_pin_effective_fF": q / vdd * 1e15,
            "Q_per_fin_aC": q * 1e18 / md["fins_gated_by_this_pin"],
            "C_schematic_over_liberty":
                (q / vdd * 1e15) / md["liberty_pin_fF"] if md["liberty_pin_fF"] else None,
        })

    # per (cell, pin, vdd): average the two hold states, keep the spread
    bycellpin = defaultdict(list)
    for d, r in per.items():
        bycellpin[(r["cell"], r["pin"], r["vdd"])].append(r)
    cp = {}
    for (cell, pin, vdd), rs in bycellpin.items():
        qs = [r["Q_into_pin_aC"] for r in rs]
        cp[f"{cell}|{pin}|{vdd}"] = {
            "cell": cell, "pin": pin, "VDD_V": vdd,
            "fins_gated_by_this_pin": rs[0]["fins_gated_by_this_pin"],
            "liberty_pin_fF": rs[0]["liberty_pin_fF"],
            "Q_into_pin_aC_mean": sum(qs) / len(qs),
            "Q_into_pin_aC_by_hold_state": {r["hold"]: r["Q_into_pin_aC"] for r in rs},
            "spread_hi_over_lo": (max(qs) / min(qs)) if min(qs) else None,
            "Q_per_fin_aC_mean": (sum(qs) / len(qs)) / rs[0]["fins_gated_by_this_pin"],
            "C_pin_effective_fF_mean": (sum(qs) / len(qs)) * 1e-18 / vdd * 1e15,
            "C_schematic_over_liberty":
                ((sum(qs) / len(qs)) * 1e-18 / vdd * 1e15) / rs[0]["liberty_pin_fF"]
                if rs[0]["liberty_pin_fF"] else None,
        }

    # mix-weighted, over the 15 cell types that take 88% of the driven pins.
    # Within a cell every input pin is weighted equally -- the DEF join does not
    # say which pin of a cell a toggling net lands on.
    out = {"what": "charge one driven gate pin takes, measured on the cells this "
                   "multiply-add actually drives",
           "convention": "Q is the charge into the pin on its rising edge; the "
                         "driver pays Q x VDD from its own rail for it; "
                         "electrons = Q / e",
           "decks": len(per), "decks_dropped": dropped,
           "cell_pin_voltage_points": len(cp),
           "by_cell_pin": cp,
           "driven_cell_mix_toggle_weighted": mix}

    for vdd in sorted({r["VDD_V"] for r in cp.values()}):
        num_q = num_f = num_c = num_l = den = 0.0
        covered = 0.0
        for cell, share in mix.items():
            rows = [r for r in cp.values() if r["cell"] == cell and r["VDD_V"] == vdd]
            if not rows:
                continue
            covered += share
            qbar = sum(r["Q_into_pin_aC_mean"] for r in rows) / len(rows)
            fbar = sum(r["fins_gated_by_this_pin"] for r in rows) / len(rows)
            cbar = sum(r["C_pin_effective_fF_mean"] for r in rows) / len(rows)
            lbar = sum(r["liberty_pin_fF"] for r in rows) / len(rows)
            num_q += share * qbar
            num_f += share * fbar
            num_c += share * cbar
            num_l += share * lbar
            den += share
        k = ("%.3f" % vdd).replace(".", "p")
        out[f"mix_weighted_{k}"] = {
            "VDD_V": vdd,
            "share_of_driven_pins_covered": covered,
            "Q_per_driven_pin_aC": num_q / den,
            "electrons_per_driven_pin": num_q / den * 1e-18 / E,
            "E_from_VDD_per_driven_pin_rising_edge_aJ": num_q / den * 1e-18 * vdd * 1e18,
            "fins_per_driven_pin": num_f / den,
            "Q_per_fin_aC": (num_q / den) / (num_f / den),
            "C_schematic_pin_fF": num_c / den,
            "C_liberty_pin_fF": num_l / den,
            "schematic_over_liberty": (num_c / den) / (num_l / den),
        }

    json.dump(out, open(outp, "w"), indent=1, sort_keys=True)
    for k in sorted(out):
        if k.startswith("mix_weighted"):
            print(k, json.dumps(out[k], indent=1))


if __name__ == "__main__":
    main()
