#!/usr/bin/env python3
"""Turn the RTL toggle counts of each number format into a frozen prediction of E78's switching watts.

    predict.py <counts.json from rtl-sim/fma_toggle_formats/run_kinds.py> --out predictor.json

THE MODEL, and why it has three terms. The one-term model (watts proportional to toggled nets) cannot
hold: E64 measured fp32 `ones` at 10.41 W of switching while this bench counts 4,682 toggled nets an op
for it, against `randn`'s 29.6 million. What `ones` buys over `zeros` is not switching, it is that its
lanes are NOT ZERO-GATED - every lane is enabled, clocked and presenting operands. So:

    W_switching(600 MHz, 1024 minions) = W0 + g * live_slot_cycles_per_s + k * nets_hier_per_s

    W0   the floor: the unit's clock runs for the whole op even when every lane is gated
    g    W per enabled column-slot-cycle per second: the price of a lane being ON with static operands
    k    W per merged-net toggle per second, i.e. the fJ per toggled net

CALIBRATION. The three parameters are fitted on fp32 {zeros, ones, randn} ONLY - three measured anchors,
three unknowns, so the fit is exact and makes no claim beyond those points. Every other cell in the table,
and every fp16 and int8 cell, is then a PREDICTION with no fitted freedom. The six fp16/int8 anchors E64
also measured are held out and used only to score the predictor.

TOGGLE CONVENTION. `nets_hier` is the per-merged-net count the toggle recount
(docs/reports/data/2026-10-26-toggle-recount/README.md) established as the figure to quote. This script
reaches it from the raw Verilator coverage total by the whole-unit factor measured there
(rtl-sim/fma_toggle/../../docs/.../hier-factors.json `_total` = 5.3271), NOT by a VCD of these runs. That
factor was measured on fp32 randn; applying it to fp16 and to the TIMA is the predictor's largest
modelling assumption and is declared as such.
"""
import argparse
import hashlib
import json
import os

HIER = 5.3271115221865095          # hier-factors.json `_total`, measured on fp32 randn
CYCLES = {"fp32": 546, "fp16": 546, "int8": 318}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
SLOTS = {"fp32": 8, "fp16": 8, "int8": 16}
F_HZ = 600e6                        # E78 pins 600 MHz; E64's fit.c is the 600 MHz switching term (s=1.0)
MINIONS = 1024

# E64 (docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json `fit.c`), the switching term of
# P = B(f) + c * s(f) with s(600 MHz) = 1.0, so c is watts of switching at 600 MHz on 1024 minions.
ANCHORS = {
    ("fp32", "zeros"): [1.406, 1.473, 1.442],      # LAD-00 r1, r2 and SUS-00
    ("fp32", "ones"):  [11.164, 9.648, 9.704],     # LAD-02 r1, r2 and SUS-01
    ("fp32", "randn"): [25.459, 25.593, 25.862],   # LAD-09 r1, r2 and SUS-02
}
HELD_OUT = {
    ("fp16", "zeros"): [1.394], ("fp16", "ones"): [9.702], ("fp16", "randn"): [23.284],
    ("int8", "zeros"): [2.123], ("int8", "ones"): [2.684], ("int8", "full"): [9.101],
}


def unit_nets(row):
    """Toggled nets per op inside the unit that format actually uses.

    The bench instantiates both units and switches one off by tying its clock and valid low, but a
    disabled txfma_top's COMBINATIONAL input nets still follow the operand bus, so an int8 run carries
    about 194k of txfma names an op that no clock ever samples. They are dropped here by name.
    """
    bb = row["new_bench"]["by_block"]
    if row["type"] == "int8":
        return sum(v for k, v in bb.items() if k.startswith("tima") or k == "et_clk_gate")
    return sum(v for k, v in bb.items() if not k.startswith("tima"))


def rates(row):
    typ = row["type"]
    ops_s = F_HZ / CYCLES[typ]
    nets_hier_op = unit_nets(row) / HIER
    return {
        "nets_per_op": unit_nets(row),
        "nets_hier_per_op": nets_hier_op,
        "nets_hier_per_mac": nets_hier_op / MACS[typ],
        "live_slot_cycles_per_op": row["new_bench"]["slot_valid"],
        # 512 micro-ops x 8 slots in txfma, 256 x 16 in TIMA: 4,096 column-slot-cycles an op either way
        "gated_slot_frac": 1.0 - row["new_bench"]["slot_valid"] / 4096.0,
        "bus_ab_per_op": row["new_bench"]["bus_ab"],
        "ops_per_s_per_minion": ops_s,
        "nets_hier_per_s": nets_hier_op * ops_s * MINIONS,
        "live_slot_cycles_per_s": row["new_bench"]["slot_valid"] * ops_s * MINIONS,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("counts")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    rows = {(r["type"], r["kind"]): r for r in json.load(open(a.counts))["rows"]}
    rate = {k: rates(r) for k, r in rows.items()}

    # --- the exact 3-point fit on fp32 zeros / ones / randn -------------------------------------
    z, o, n = rate[("fp32", "zeros")], rate[("fp32", "ones")], rate[("fp32", "randn")]
    wz = sum(ANCHORS[("fp32", "zeros")]) / len(ANCHORS[("fp32", "zeros")])
    wo = sum(ANCHORS[("fp32", "ones")]) / len(ANCHORS[("fp32", "ones")])
    wn = sum(ANCHORS[("fp32", "randn")]) / len(ANCHORS[("fp32", "randn")])
    # zeros: no live slot, ~no nets -> W0 (its 86 nets an op are folded in, 4e-5 W)
    # ones:  all slots live, ~no nets -> g
    # randn: all slots live, 29.6M nets -> k
    # solve the 3x3 by hand in this order; the two "~no nets" terms are kept, not dropped.
    A = [[1.0, z["live_slot_cycles_per_s"], z["nets_hier_per_s"]],
         [1.0, o["live_slot_cycles_per_s"], o["nets_hier_per_s"]],
         [1.0, n["live_slot_cycles_per_s"], n["nets_hier_per_s"]]]
    b = [wz, wo, wn]
    # Gaussian elimination, 3x3
    M = [row[:] + [bb] for row, bb in zip(A, b)]
    for i in range(3):
        pv = max(range(i, 3), key=lambda r: abs(M[r][i]))
        M[i], M[pv] = M[pv], M[i]
        for r in range(3):
            if r != i and M[r][i] != 0.0:
                f = M[r][i] / M[i][i]
                for c in range(i, 4):
                    M[r][c] -= f * M[i][c]
    W0, g, k = (M[i][3] / M[i][i] for i in range(3))

    def predict(key):
        r = rate[key]
        return W0 + g * r["live_slot_cycles_per_s"] + k * r["nets_hier_per_s"]

    out = {
        "_what": "frozen prediction of E78's fp32/fp16/int8 switching watts per kind, from the RTL",
        "_model": "W_switching(600 MHz, 1024 minions) = W0 + g*live_slot_cycles_per_s + k*nets_hier_per_s",
        "_calibration": {
            "fitted_on": "fp32 zeros, ones, randn only (E64 figures.json fit.c; aifoundry2, 600 MHz term)",
            "fit_is_exact": "3 anchors, 3 parameters: the fp32 anchors are reproduced by construction",
            "W0_w": W0, "g_w_per_live_slot_cycle_per_s": g, "k_w_per_net_toggle_per_s": k,
            "k_fJ_per_toggled_net": k * 1e15,
            "hier_factor": HIER,
            "hier_factor_source": "docs/reports/data/2026-10-26-toggle-recount/hier-factors.json `_total`",
            "departures": [
                "E64 ran on aifoundry2, not aifoundry3: these are the only committed fp32 "
                "zeros/ones/randn switching-watt anchors. E78 must REFIT W0, g and k on its own "
                "aifoundry3 anchors before quoting absolute watts; the per-kind ratios do not move.",
                "the 5.3271 hierarchy factor was measured on fp32 randn and is reused for fp16 and TIMA",
                "1024 minions and 600 MHz assumed, as E78 registers",
            ],
        },
        "_inputs": {"cycles_per_op": CYCLES, "macs_per_op": MACS, "column_slots": SLOTS,
                    "f_hz": F_HZ, "minions": MINIONS},
        "predictions": {},
        "held_out_scoring": {},
    }
    for key in sorted(rate, key=lambda t: (t[0], t[1])):
        r = rate[key]
        w = predict(key)
        out["predictions"][f"{key[0]}.{key[1]}"] = {
            "switching_W_600MHz_1024minions": round(w, 3),
            "pJ_per_MAC": round(w / (F_HZ / CYCLES[key[0]] * MINIONS * MACS[key[0]]) * 1e12, 4),
            "nets_hier_per_op": round(r["nets_hier_per_op"], 1),
            "toggles_per_MAC": round(r["nets_hier_per_mac"], 2),
            "live_slot_cycles_per_op": r["live_slot_cycles_per_op"],
            "gated_slot_frac": round(r["gated_slot_frac"], 4),
            "bus_ab_per_op": r["bus_ab_per_op"],
            "is_anchor": (key in ANCHORS),
            "is_held_out": (key in HELD_OUT),
        }
    for key, ws in HELD_OUT.items():
        if key not in rate:
            continue
        m = sum(ws) / len(ws)
        pr = predict(key)
        out["held_out_scoring"][f"{key[0]}.{key[1]}"] = {
            "measured_W": m, "predicted_W": round(pr, 3),
            "err_W": round(pr - m, 3), "ratio": round(pr / m, 3) if m else None,
        }
    # What each format's OWN zeros/ones pair says the "a lane is enabled" price is. This USES HELD-OUT
    # DATA and is therefore NOT part of the frozen prediction: it is the one extra parameter E78 should
    # measure per format, reported so the refit is mechanical.
    out["per_format_g_from_held_out"] = {
        "_what": "g_fmt = (W(ones) - W(zeros)) / live_slot_cycles_per_s(ones); NOT FROZEN, uses held-out cells",
        "_why": "a TIMA column slot is four 9x9 int8 multipliers; a txfma lane is one 24x24 fp32 "
                "multiply-add. The frozen fp32-only fit charges them the same and so overpredicts int8.",
    }
    for f in ("fp32", "fp16", "int8"):
        kz, ko = (f, "zeros"), (f, "ones")
        src = {**ANCHORS, **HELD_OUT}
        if kz in rate and ko in rate and kz in src and ko in src:
            wzz = sum(src[kz]) / len(src[kz])
            woo = sum(src[ko]) / len(src[ko])
            lv = rate[ko]["live_slot_cycles_per_s"]
            out["per_format_g_from_held_out"][f] = {
                "W_zeros": wzz, "W_ones": woo,
                "g_w_per_live_slot_cycle_per_s": (woo - wzz) / lv,
                "ratio_to_fp32_g": ((woo - wzz) / lv) / g,
            }
    errs = [v["err_W"] for v in out["held_out_scoring"].values()]
    if errs:
        out["held_out_scoring"]["_rms_W"] = round((sum(e * e for e in errs) / len(errs)) ** 0.5, 3)
        out["held_out_scoring"]["_worst_ratio"] = max(
            (v["ratio"] for v in out["held_out_scoring"].values() if isinstance(v, dict)), key=abs)
    json.dump(out, open(a.out, "w"), indent=1, sort_keys=False)
    raw = open(a.out, "rb").read()
    print("sha256", hashlib.sha256(raw).hexdigest(), os.path.basename(a.out))
    print(f"W0={W0:.4f} W   g={g:.6e} W/(slot-cycle/s)   k={k * 1e15:.4f} fJ per toggled net")
    for key, v in out["held_out_scoring"].items():
        if isinstance(v, dict):
            print(f"  held out {key:12s} measured {v['measured_W']:6.2f} W  predicted {v['predicted_W']:6.2f} W"
                  f"  ratio {v['ratio']}")


if __name__ == "__main__":
    main()
