#!/usr/bin/env python3
"""Q128(d): turn the 50-deck SPICE run into the measured half of the ledger.

  parse3.py <spice3.log> <out.json>

Convention, held throughout: every energy is the energy DRAWN FROM VDD by one
event, at 0.517 V unless the key says otherwise, and electrons = charge / e.
A "cycle" is one rise plus one fall; a "transition" is one edge, half a cycle.
"""
import json
import re
import sys

E_CHARGE = 1.602176634e-19      # C, exact (SI 2019)
K_B = 1.380649e-23              # J/K, exact


def read_log(path):
    """{deck: {measure: value}}"""
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
    logp, outp = sys.argv[1], sys.argv[2]
    d = read_log(logp)
    V = {"0p517": 0.517, "0p700": 0.700}
    R = {"convention": "energy drawn from VDD per event; electrons = charge / e; "
                       "e = 1.602176634e-19 C; a cycle is one rise + one fall",
         "decks_parsed": len(d)}

    # ---- 1. the gate charge of one minimum device ---------------------------
    gq = {}
    for k, m in d.items():
        g = re.match(r'gq_(n3|n|p)_(gnd|vdd)_(0p\d+)\.sp', k)
        if not g:
            continue
        dev, drain, v = g.groups()
        vdd = V[v]
        q = m.get("qg_hi", 0) - m.get("qg_lo", 0)
        gq[f"{dev}mos_RVT_drain_{drain}_{v}"] = {
            "device": {"n": "nmos_rvt, 1 fin, l=20n", "p": "pmos_rvt, 1 fin, l=20n",
                       "n3": "nmos_rvt, 3 fins, l=20n"}[dev],
            "drain_held_at": drain,
            "VDD_V": vdd,
            "Qg_C": q,
            "Qg_aC": q * 1e18,
            "electrons": q / E_CHARGE,
            "E_from_VDD_J": q * vdd,
            "E_from_VDD_aJ": q * vdd * 1e18,
            "Cgg_effective_fF": q / vdd * 1e15,
            "charge_returned_at_the_fall_C": m.get("qg_end", 0) - m.get("qg_lo", 0),
        }
    R["one_device_gate_charge"] = gq

    # ---- 2. the charge one driven gate PIN takes ----------------------------
    pq = {}
    for k, m in d.items():
        g = re.match(r'pinq_(\w+)_(0p\d+)\.sp', k)
        if not g:
            continue
        cell, v = g.groups()
        vdd = V[v]
        q = m.get("qi_hi", 0) - m.get("qi_lo", 0)
        qd = m.get("qd_hi", 0) - m.get("qd_lo", 0)
        pq[f"{cell}_{v}"] = {
            "cell": cell, "VDD_V": vdd,
            "Q_into_pin_on_a_rising_edge_C": q,
            "Q_into_pin_aC": q * 1e18,
            "electrons_into_the_pin": q / E_CHARGE,
            "E_the_driver_pays_for_this_pin_aJ": q * vdd * 1e18,
            "Cpin_effective_fF": q / vdd * 1e15,
            "the_cell_s_own_rail_charge_over_the_same_edge_C": qd,
        }
    R["one_gate_pin"] = pq

    # ---- 3. the inverter per edge, by load ----------------------------------
    en = {}
    for k, m in d.items():
        g = re.match(r'en_INVx1_(0p\d+)_(\d+p\d+)\.sp', k)
        if not g:
            continue
        v, cl = g.groups()
        vdd = V[v]
        c = float(cl.replace("p", "."))
        qcyc = m.get("qd2", 0) - m.get("qd0", 0)
        e_cyc = qcyc * vdd
        e_load = c * 1e-15 * vdd * vdd            # the load's own CV^2 per cycle
        en[f"{v}_{cl}fF"] = {
            "VDD_V": vdd, "C_load_fF": c,
            "E_rail_per_cycle_fJ": e_cyc * 1e15,
            "E_rail_per_transition_fJ": e_cyc * 1e15 / 2,
            "E_load_CV2_per_cycle_fJ": e_load * 1e15,
            "E_internal_per_cycle_fJ": (e_cyc - e_load) * 1e15,
            "internal_share": (e_cyc - e_load) / e_cyc if e_cyc else None,
            "electrons_per_cycle": qcyc / E_CHARGE,
        }
    R["inverter_by_load"] = en

    # ---- 4. short circuit, at a real net's load -----------------------------
    sc = {}
    for k, m in d.items():
        g = re.match(r'sc_INVx1_(0p\d+)_(\d+)ps\.sp', k)
        if not g:
            continue
        v, tr = g.groups()
        vdd = V[v]
        q = m.get("qd2", 0) - m.get("qd0", 0)
        sc.setdefault(v, {})[int(tr)] = q * vdd * 1e15
    scx = {}
    for v, byt in sc.items():
        lo = min(byt.values())
        scx[v] = {
            "VDD_V": V[v],
            "C_load_fF": 2.105,
            "E_rail_per_cycle_fJ_by_input_edge_ps": {str(t): byt[t] for t in sorted(byt)},
            "cheapest_edge_ps": min(byt, key=byt.get),
            "excess_over_cheapest_fJ": {str(t): byt[t] - lo for t in sorted(byt)},
            "excess_share_over_cheapest": {str(t): (byt[t] - lo) / byt[t] for t in sorted(byt)},
        }
    R["short_circuit_at_a_real_net_load"] = scx

    # ---- 5. one net as built: driver + N gate pins + wire -------------------
    nets = {}
    for k, m in d.items():
        g = re.match(r'net_(0p\d+)_fo(\d+)\.sp', k)
        if not g:
            continue
        v, fo = g.groups()
        vdd = V[v]
        q = m.get("qd2", 0) - m.get("qd0", 0)
        nets.setdefault(v, {})["fo%d" % int(fo)] = {
            "fanout": int(fo),
            "Q_rail_per_cycle_C": q,
            "E_rail_per_cycle_fJ": q * vdd * 1e15,
            "E_rail_per_transition_fJ": q * vdd * 1e15 / 2,
            "electrons_per_cycle": q / E_CHARGE,
            "v_out_low_V": m.get("vo_lo"), "v_out_high_V": m.get("vo_hi"),
        }
    # marginal cost of one more gate pin, by regression over fo = 0..4
    for v, byfo in nets.items():
        xs = sorted(int(k[2:]) for k in byfo)
        ys = [byfo["fo%d" % x]["E_rail_per_cycle_fJ"] for x in xs]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        den = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
        inter = my - slope * mx
        byfo["fit"] = {
            "what": "E_rail per cycle = intercept + slope x fanout, 0.785 fF of wire on the net",
            "intercept_fJ": inter, "slope_fJ_per_gate_pin": slope,
            "slope_electrons_per_gate_pin_per_cycle": slope * 1e-15 / V[v] / E_CHARGE,
        }
    R["one_net_as_built"] = nets

    json.dump(R, open(outp, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: (len(v) if isinstance(v, dict) else v) for k, v in R.items()}, indent=1))
    return R


if __name__ == "__main__":
    main()
