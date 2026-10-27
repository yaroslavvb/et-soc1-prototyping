#!/usr/bin/env python3
"""Q128(d) amendment: parse the extended short-circuit sweep.

  parse_sc4.py <out.json> <one-switch3.json|-> <log> [log ...]

Every deck shares one measurement window, 0.95 ns -> 14.95 ns, so the only
thing that changes with the input edge is the edge.  The two leakage decks per
rail give the rail current in each input state, which is subtracted from every
sweep point: a slower edge spends less of the fixed window in the steady low
state, and without that subtraction the leakage difference is the same size as
the short-circuit term being measured.
"""
import json
import re
import sys

E_CHARGE = 1.602176634e-19
VDDS = {"0p517": 0.517, "0p700": 0.700}
T0, T1 = 0.95e-9, 14.95e-9          # the measurement window
WINDOW = T1 - T0                    # 14 ns
PW = 6e-9                           # time the input is held at VDD
CL_FF = 2.105


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


OLD_WINDOW = 4.0e-9                 # one-switch3's decks: 0.95 ns -> 4.95 ns
OLD_PW = 2.0e-9                     # with the input held at VDD for 2 ns


def cross_check(old, v, vdd, leak, rows):
    """The first sweep's own points, corrected for leakage with the same two
    currents and ITS window, against this one.  The two runs share nothing but
    the circuit: different pulse width, different window, different decks."""
    if not old:
        return None
    src = old["short_circuit_at_a_real_net_load"][v]["E_rail_per_cycle_fJ_by_input_edge_ps"]
    out, worst = {}, 0.0
    for tr_s, e_raw_fJ in src.items():
        tr = int(tr_s)
        if tr not in rows:
            continue
        t = tr * 1e-12
        q_leak = leak["lo"]["I_A"] * (OLD_WINDOW - OLD_PW - 2 * t) + leak["hi"]["I_A"] * OLD_PW
        e_old = e_raw_fJ - q_leak * vdd * 1e15
        e_new = rows[tr]["E_switching_per_cycle_fJ"]
        rel = abs(e_new - e_old) / e_old
        worst = max(worst, rel)
        out[tr_s] = {"first_sweep_deleaked_fJ": e_old, "this_sweep_fJ": e_new,
                     "relative_difference": rel}
    return {"what": "one-switch3.json's points, de-leaked with this run's measured "
                    "currents over its own 4 ns window, against this run",
            "by_input_edge_ps": out, "worst_relative_difference": worst}


def main():
    outp, oldp, logs = sys.argv[1], sys.argv[2], sys.argv[3:]
    old = json.load(open(oldp)) if oldp != "-" else None
    d = {}
    for p in logs:
        d.update(read_log(p))
    R = {
        "what": "INVx1 at 2.105 fF, rail energy per cycle against input edge time, "
                "1 ps to 2 ns, on one fixed measurement window with the static "
                "leakage of each input state measured and subtracted",
        "window": {"t0_ns": T0 * 1e9, "t1_ns": T1 * 1e9,
                   "input_held_high_ns": PW * 1e9,
                   "comment": "input low (output high) for 8 - 2*tr ns, input high "
                              "(output low) for 6 ns, in transition for 2*tr ns"},
        "C_load_fF": CL_FF,
        "decks_parsed": len(d),
    }

    for v, vdd in VDDS.items():
        leak = {}
        for st in ("lo", "hi"):
            m = d.get(f"leak_{v}_{st}.sp", {})
            q = m.get("qd2", 0) - m.get("qd0", 0)
            leak[st] = {"Q_C_over_the_window": q, "I_A": q / WINDOW,
                        "I_nA": q / WINDOW * 1e9}
        rows = {}
        for k, m in d.items():
            g = re.match(r'sc4_%s_(\d+)ps\.sp' % v, k)
            if not g:
                continue
            tr_ps = int(g.group(1))
            t = tr_ps * 1e-12
            q_raw = m["qd2"] - m["qd0"]
            t_lo = WINDOW - PW - 2 * t          # input low, output high
            q_leak = leak["lo"]["I_A"] * t_lo + leak["hi"]["I_A"] * PW
            q_dyn = q_raw - q_leak
            rows[tr_ps] = {
                "E_rail_per_cycle_raw_fJ": q_raw * vdd * 1e15,
                "leakage_in_the_window_fJ": q_leak * vdd * 1e15,
                "E_switching_per_cycle_fJ": q_dyn * vdd * 1e15,
                "electrons_per_cycle": q_dyn / E_CHARGE,
            }
        lo_key = min(rows, key=lambda t: rows[t]["E_switching_per_cycle_fJ"])
        lo = rows[lo_key]["E_switching_per_cycle_fJ"]
        for tr, r in rows.items():
            r["excess_over_the_cheapest_fJ"] = r["E_switching_per_cycle_fJ"] - lo
            r["excess_share"] = (r["E_switching_per_cycle_fJ"] - lo) / r["E_switching_per_cycle_fJ"]
        ts = sorted(rows)
        turns = (lo_key != max(ts) and lo_key != min(ts))
        # the edge this inverter itself produces into the same load: the input
        # edge the next gate in the design actually gets
        sl = d.get(f"slew_{v}.sp", {})
        slew = None
        if sl:
            slew = {"rise_20_80_ps": (sl["tr80"] - sl["tr20"]) * 1e12,
                    "fall_80_20_ps": (sl["tf20"] - sl["tf80"]) * 1e12,
                    "what": "INVx1 driving the same 2.105 fF, input edge 5 ps"}
        R[v] = {
            "VDD_V": vdd,
            "static_leakage": leak,
            "by_input_edge_ps": {str(t): rows[t] for t in ts},
            "cheapest_edge_ps": lo_key,
            "E_switching_at_the_minimum_fJ": lo,
            "minimum_is_bracketed": turns,
            "max_excess_share": max(r["excess_share"] for r in rows.values()),
            "against_the_first_sweep": cross_check(old, v, vdd, leak, rows),
            "excess_at_the_design_s_own_edge": {
                "comment": "the slowest edge this inverter produces into this load is "
                           "the output_slew below; the rows at or under it are the ones "
                           "that describe the design",
                "output_slew": slew,
            },
        }

    json.dump(R, open(outp, "w"), indent=1, sort_keys=True)
    for v in VDDS:
        s = R[v]
        print(f"=== {v}  leak lo {s['static_leakage']['lo']['I_nA']:.3f} nA, "
              f"hi {s['static_leakage']['hi']['I_nA']:.3f} nA")
        for t, r in s["by_input_edge_ps"].items():
            print(f"  {t:>5} ps  raw {r['E_rail_per_cycle_raw_fJ']:.6f}  "
                  f"leak {r['leakage_in_the_window_fJ']:.6f}  "
                  f"switching {r['E_switching_per_cycle_fJ']:.6f}  "
                  f"excess {100 * r['excess_share']:.3f}%")
        print(f"  cheapest {s['cheapest_edge_ps']} ps, bracketed: {s['minimum_is_bracketed']}, "
              f"max excess {100 * s['max_excess_share']:.2f}%, "
              f"slew {s['excess_at_the_design_s_own_edge']['output_slew']}")


if __name__ == "__main__":
    main()
