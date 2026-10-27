#!/usr/bin/env python3
"""Q129: the bottom-up ledger for the lane's TRANSPORT, and what it names of Q128's gap.

Reads the power.py outputs of tools/open-flow/scope/gatesim.sh runs on the scope netlist
(register files, operand bus, result path, per-lane control) and:

  1. prices every part per random multiply-add, splitting the clock from the data and the
     data-dependent part from the part that is there whether the data moves or not;
  2. fits the Hamming ladder the way E60's own reducer fits it, so the transport's per-flipped-
     operand-bit price can be added to the arithmetic's 32.9 / 38.5 fJ and set against E60's
     board measurement of 116.7 / 129.9 fJ -- against BOTH benches' bus counters, because the
     two count the same operand files differently (--acct-arith);
  3. takes the register-index term and the result-path term by difference against the two
     controls (+accfix, +resfix), against E61's 369-452 fJ per index bit and E60's 31.2 fJ
     per result bit;
  4. says how much of Q128's unaccounted 2.39 pJ (rail) and 3.84 pJ (board) the parts name,
     and checks the zero-operand floor against the card's own whole-board `zeros` measurement.

  python3 ledger_scope.py --power <dir of power_gr_*.json> --acct <dir of *_o1.log>
          --census <census_mixed.json> --out ledger-scope.json
          [--acct-arith <2026-10-26-open-netlist/power/sim_acct.txt>]
          [--cell-energies <asap7-cell-energies.json>]

Amended Tue 27 Oct 2026 after verification, in four places, each marked `AMENDED` below:
the gap arithmetic's lower reading (the zero-operand floor is 34% clock and 66% signal, not
"the clock gates"), the data-dependent internal term (differenced, not scaled), the index-alone
bound (priced at the bus-bit slope, not the designed-bit slope this file itself calls unfit),
and the card's `zeros` bound on the register-file model.
"""
import argparse
import json
import os
import re

MULADDS = 512.0            # one TensorFMA32 op, one lane (16 x 16 x 2 micro-ops)
LANES = 8                  # VPU_LANE_NUM: the shared blocks serve this many lanes

# --- the board-level measurements this is set against -----------------------------------
BOARD = {
    # E38/E39, three cards, registered means, per random fp32 multiply-add, over idle
    "mac_board_pJ": 5.783,
    "rail_ratio": 0.750,                  # E60's own measured board->minion-rail ratio
    "mac_rail_pJ": 5.783 * 0.750,         # 4.337
    # the bottom-up ledger of one lane's ARITHMETIC (Q128 / Q126(e), the open netlist)
    "arith_pJ": 1.946,
    "arith_switching_pJ": 1.516,
    "unaccounted_board_pJ": 3.837,
    "unaccounted_rail_pJ": 2.391,
    # E60, aifoundry3, 600 MHz, 521.8 mV, 4 passes (2026-10-20-bitflip-ladder/reduce.txt)
    "flip_lq_board_fJ": 116.746, "flip_lq_se": 0.613,
    "flip_lb_board_fJ": 129.918, "flip_lb_se": 0.480,
    "flip_lq_bus_board_fJ": 74.658, "flip_lb_bus_board_fJ": 85.578,
    "readport_bit_board_fJ": 20.83, "readport_bit_se": 0.10,
    "result_bit_board_fJ": 31.17, "result_bit_se": 0.17,
    # the open netlist's own ladder slopes for the ARITHMETIC (2026-10-26-open-netlist/POWER.md)
    "arith_flip_lq_fJ": 32.9, "arith_flip_lb_fJ": 38.5,
    "arith_flip_lq_internal_fJ": 46.3, "arith_flip_lb_internal_fJ": 54.9,
    # E61, aifoundry3 (2026-10-21-dtf), under-resolved: no linear law across three rungs
    "index_bit_board_fJ_lo": 369.0, "index_bit_board_fJ_hi": 452.0,
    # Q126(b): the RTL bench's register bits clocked per multiply-add
    "ff_clocked_per_mac": 602.5,
    # E38/E39, the `zeros` pattern: the WHOLE BOARD's cost per multiply-add over idle, three-card
    # registered mean (Q128 data.json /permac/mean_zeros_pJ; per card 0.1633 / 0.4034 / 0.2512).
    # Same instruction stream as this bench's `zeros` run, with zero operand data - so it is an
    # upper bound on what ONE LANE's transport can cost in that run.
    "mac_board_zeros_pJ": 0.27,
    "mac_board_zeros_per_card_pJ": [0.1633, 0.4034, 0.2512],
    # the arithmetic's own per-counted-bus-bit slopes (POWER.md ll. 131-134), for the common-
    # denominator addition in section 2
    "arith_flip_lq_bus_fJ": 20.0, "arith_flip_lb_bus_fJ": 27.5,
    "arith_flip_lq_bus_internal_fJ": 28.1, "arith_flip_lb_bus_internal_fJ": 39.2,
}

# --- which net prefix belongs to which part ---------------------------------------------
# The keys are matched against the block name power.py writes (a net path truncated at
# --block-depth), longest prefix first.
PARTS = [
    ("vrf/arr",            "VPU register file array, 64 x 32 (MODEL)"),
    ("vrf",                "VPU register file collision bypass"),
    ("bypass",             "operand bus + F4..F8 result pipeline"),
    ("tena_rf",            "tensor A register file, 32 b x 2"),
    ("LANE_TIMA",          "tensor B register files, 32 b x 4, x2"),
    ("tenb_rf",            "tensor B register files, 32 b x 4, x2"),
    ("tentmp_rf",          "tensor TMP register file, 32 b x 8"),
    ("tenc_rf",            "TIMA accumulator file, 32 b x 16 (MODEL)"),
    ("ctl",                "per-lane control pipeline (MODEL)"),
]
MODEL_PARTS = {"VPU register file array, 64 x 32 (MODEL)",
               "TIMA accumulator file, 32 b x 16 (MODEL)",
               "per-lane control pipeline (MODEL)"}


def part_of(block):
    # A generate block's instance path carries its index, so vpu_lane.v's two TIMA files come
    # through as LANE_TIMA[0].tenb_rf - which matches none of "/", "." or the bare name.
    for pre, name in PARTS:
        if block == pre or any(block.startswith(pre + c) for c in ("/", ".", "[")):
            return name
    return "top-level nets, the clock root and the lane control's own ports"


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(xs, ys)]
    # standard error of the slope, n-2 degrees of freedom
    s2 = sum(r * r for r in res) / (n - 2) if n > 2 else 0.0
    return b, a, (s2 / sxx) ** 0.5 if sxx else 0.0


def load_power(d, tag):
    p = os.path.join(d, f"power_gr_{tag}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def load_acct(d, tag):
    p = os.path.join(d, f"{tag}_o1.log")
    if not os.path.exists(p):
        return {}
    for line in open(p):
        if line.startswith("ACCT "):
            return json.loads(line[5:].strip())
    return {}


def load_acct_table(path):
    """A whole sim_acct.txt: `<tag> ACCT {json}` per line. Used for --acct-arith, so the
    transport's bus-bit slope can be refitted against the ARITHMETIC bench's own counts."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    for line in open(path):
        if "ACCT" not in line:
            continue
        tag, body = line.split()[0], line.split("ACCT", 1)[1].strip()
        try:
            out[tag] = json.loads(body)
        except ValueError:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--power", required=True)
    ap.add_argument("--acct", required=True)
    ap.add_argument("--acct-arith", dest="acct_arith",
                    help="the ARITHMETIC bench's sim_acct.txt "
                         "(docs/reports/data/2026-10-26-open-netlist/power/sim_acct.txt): its "
                         "bus_toggles for the same operand files, so the two ladders' bus-bit "
                         "slopes can be fitted on one denominator before they are added")
    ap.add_argument("--cell-energies", dest="cell_energies",
                    help="Q126(d)'s asap7-cell-energies.json: re-weights the internal-energy "
                         "estimate on THIS netlist's cell mix as a stated sensitivity (power.py "
                         "applies the txfma mix, which is what lets the two ledgers add)")
    ap.add_argument("--census")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    arith_acct = load_acct_table(a.acct_arith)

    out = {"method": __doc__.strip().splitlines()[0], "board": BOARD, "muladds": MULADDS}

    # ---------- 1. the per-part table, random data ---------------------------------------
    rn = load_power(a.power, "randn")
    if rn is None:
        raise SystemExit("no power_gr_randn.json")
    zr = load_power(a.power, "zeros")
    acct = load_acct(a.acct, "randn")
    out["acct"] = {t: load_acct(a.acct, t) for t in
                   ("randn", "zeros", "ones", "randn_accfix", "randn_resfix")}

    def parts_of(d):
        agg = {}
        for b, v in d["blocks"].items():
            k = part_of(b)
            e = agg.setdefault(k, {"energy_J": 0.0, "clock_energy_J": 0.0,
                                   "toggles": 0.0, "clock_toggles": 0.0, "cap_fF": 0.0,
                                   "blocks": []})
            e["energy_J"] += v["energy_J"]
            e["clock_energy_J"] += v.get("clock_energy_J", 0.0)
            e["toggles"] += v["toggles"]
            e["clock_toggles"] += v.get("clock_toggles", 0.0)
            e["cap_fF"] += v.get("cap_fF", 0.0)
            e["blocks"].append(b)
        return agg

    pr = parts_of(rn)
    pz = parts_of(zr) if zr else {}
    # the internal-energy estimate is a whole-design number; split it by each part's share of
    # the SIGNAL toggles, which is what it prices.
    sig_tot = sum(v["toggles"] - v["clock_toggles"] for v in pr.values())
    e_int = rn.get("internal_estimate", {}).get("internal_J_signal_transitions", 0.0)

    table = []
    for k, v in sorted(pr.items(), key=lambda kv: -kv[1]["energy_J"]):
        sig = v["toggles"] - v["clock_toggles"]
        zz = pz.get(k, {})
        table.append({
            "part": k,
            "blocks": sorted(v["blocks"])[:6],
            "is_model": k in MODEL_PARTS,
            "pJ_per_mac_switching": v["energy_J"] / MULADDS * 1e12,
            "pJ_per_mac_clock": v["clock_energy_J"] / MULADDS * 1e12,
            "pJ_per_mac_signal": (v["energy_J"] - v["clock_energy_J"]) / MULADDS * 1e12,
            # zeros is the same netlist and the same micro-op stream with every operand word
            # zero, so (randn - zeros) is the DATA-DEPENDENT part. AMENDED: `zeros` is NOT "what
            # the part costs for being clocked at all" - the accumulator index sweeps in that run
            # too, so most of the zeros column is signal switching the instruction stream causes.
            # Its own clock/signal split is given beside it.
            "pJ_per_mac_data_dependent": (v["energy_J"] - zz.get("energy_J", 0.0)) / MULADDS * 1e12,
            "pJ_per_mac_zeros": zz.get("energy_J", 0.0) / MULADDS * 1e12,
            "pJ_per_mac_zeros_clock": zz.get("clock_energy_J", 0.0) / MULADDS * 1e12,
            "pJ_per_mac_zeros_signal": (zz.get("energy_J", 0.0)
                                        - zz.get("clock_energy_J", 0.0)) / MULADDS * 1e12,
            "pJ_per_mac_internal_est": (e_int * sig / sig_tot / MULADDS * 1e12) if sig_tot else 0.0,
            "signal_toggles_per_mac": sig / MULADDS,
            "clock_toggles_per_mac": v["clock_toggles"] / MULADDS,
            "cap_fF": v["cap_fF"],
        })
    out["per_part"] = table
    out["totals"] = {
        "switching_pJ_per_mac": rn["energy_J"] / MULADDS * 1e12,
        "internal_est_pJ_per_mac": e_int / MULADDS * 1e12,
        "switching_plus_internal_pJ_per_mac":
            rn["internal_estimate"]["switching_plus_internal_J"] / MULADDS * 1e12
            if "internal_estimate" in rn else None,
        "clock_share": rn["clock_share"],
        "zeros_switching_pJ_per_mac": (zr["energy_J"] / MULADDS * 1e12) if zr else None,
        "data_dependent_pJ_per_mac":
            ((rn["energy_J"] - zr["energy_J"]) / MULADDS * 1e12) if zr else None,
        "cap_fraction_priced": rn["coverage"]["cap_fraction_priced"],
        "cap_fF_extracted": rn["coverage"]["cap_fF_extracted"],
    }

    # ---------- 2. the Hamming ladder, fitted E60's way ---------------------------------
    lad = {}
    for fam in ("lq", "lb"):
        z = load_power(a.power, f"{fam}_h0")
        if z is None:
            continue
        pts = []
        for h in (1, 2, 4, 8):
            d = load_power(a.power, f"{fam}_h{h}")
            if d is None:
                continue
            ai = load_acct(a.acct, f"{fam}_h{h}")
            pts.append((h, d["energy_J"] / MULADDS,
                        d["internal_estimate"]["switching_plus_internal_J"] / MULADDS
                        if "internal_estimate" in d else None,
                        ai.get("bus_toggles", 0) / MULADDS,
                        arith_acct.get(f"{fam}_h{h}", {}).get("bus_toggles", 0) / MULADDS))
        if len(pts) < 3:
            continue
        ez = z["energy_J"] / MULADDS
        ezi = (z["internal_estimate"]["switching_plus_internal_J"] / MULADDS
               if "internal_estimate" in z else None)
        bz = load_acct(a.acct, f"{fam}_h0").get("bus_toggles", 0) / MULADDS
        bza = arith_acct.get(f"{fam}_h0", {}).get("bus_toggles", 0) / MULADDS
        row = {}
        # AMENDED: three regressors, not two. The two benches count the SAME operand files'
        # bus bits differently (lb_h1 -26%, lb_h8 +40%), so the scope's own counter is not the
        # denominator the arithmetic's 20.0 / 27.5 fJ was fitted on. `bus_arith` refits the
        # transport's energies against the arithmetic bench's counts, which is the only pair
        # that may be added.
        regs = [("designed", [h for h, *_ in pts]),
                ("bus", [b - bz for *_, b, _ in pts])]
        if arith_acct:
            regs.append(("bus_arith", [b - bza for *_, b in pts]))
        for reg, xs in regs:
            ys = [(e - ez) * 1e15 for _, e, _, _, _ in pts]
            s, c, se = fit(xs, ys)
            row[reg] = {"slope_fJ": s, "intercept_fJ": c, "slope_se_fJ": se}
            if ezi is not None:
                yi = [(e - ezi) * 1e15 for _, _, e, _, _ in pts]
                si, ci, sei = fit(xs, yi)
                row[reg]["slope_with_internal_fJ"] = si
                row[reg]["intercept_with_internal_fJ"] = ci
                row[reg]["slope_with_internal_se_fJ"] = sei
        row["rungs"] = [{"h": h, "pJ": e * 1e12, "bus_bits_per_mac": b,
                         "arith_bench_bus_bits_per_mac": ba,
                         "bus_bits_ratio_scope_over_arith": (b / ba) if ba else None}
                        for h, e, _, b, ba in pts]
        row["h0_pJ"] = ez * 1e12
        row["h0_bus_bits_per_mac"] = bz
        row["h0_arith_bench_bus_bits_per_mac"] = bza
        row["monotone"] = all(pts[i][1] <= pts[i + 1][1] for i in range(len(pts) - 1))
        lad[fam] = row
    out["ladder"] = lad

    # the headline closure: arithmetic + transport against E60's board price
    clos = {}
    for fam, board_key, arith_key, arith_int_key in (
            ("lq", "flip_lq_board_fJ", "arith_flip_lq_fJ", "arith_flip_lq_internal_fJ"),
            ("lb", "flip_lb_board_fJ", "arith_flip_lb_fJ", "arith_flip_lb_internal_fJ")):
        if fam not in lad:
            continue
        t = lad[fam]["designed"]["slope_fJ"]
        ti = lad[fam]["designed"].get("slope_with_internal_fJ", t)
        board = BOARD[board_key]
        clos[fam] = {
            "transport_fJ_per_designed_bit": t,
            "transport_se_fJ": lad[fam]["designed"]["slope_se_fJ"],
            "transport_with_internal_fJ": ti,
            "arithmetic_fJ": BOARD[arith_key],
            "arithmetic_with_internal_fJ": BOARD[arith_int_key],
            "sum_fJ": BOARD[arith_key] + t,
            "sum_with_internal_fJ": BOARD[arith_int_key] + ti,
            "board_fJ": board,
            "rail_fJ": board * BOARD["rail_ratio"],
            "closure_vs_board": (BOARD[arith_key] + t) / board,
            "closure_vs_board_with_internal": (BOARD[arith_int_key] + ti) / board,
            "closure_vs_rail": (BOARD[arith_key] + t) / (board * BOARD["rail_ratio"]),
            "closure_vs_rail_with_internal":
                (BOARD[arith_int_key] + ti) / (board * BOARD["rail_ratio"]),
            "arith_alone_closure_vs_board": BOARD[arith_key] / board,
        }
        # AMENDED: the per-counted-bus-bit addition, on each of the two denominators. E60's own
        # amendment-A2 regressor is the counted bus bit, and for `lq` the designed-bit fit here is
        # unresolved (SE 57% of the slope) - but the arithmetic's 20.0 / 27.5 fJ were fitted on the
        # ARITHMETIC bench's counter, so only the `bus_arith` row is a like-for-like sum.
        bb = BOARD[f"flip_{fam}_bus_board_fJ"]
        for reg, lab in (("bus", "scope_bench_counts"), ("bus_arith", "arith_bench_counts")):
            if reg not in lad[fam]:
                continue
            s = lad[fam][reg]["slope_fJ"]
            si = lad[fam][reg].get("slope_with_internal_fJ", s)
            ab = BOARD[f"arith_flip_{fam}_bus_fJ"]
            abi = BOARD[f"arith_flip_{fam}_bus_internal_fJ"]
            clos[fam][f"per_bus_bit_{lab}"] = {
                "transport_fJ": s, "transport_se_fJ": lad[fam][reg]["slope_se_fJ"],
                "transport_with_internal_fJ": si,
                "arithmetic_fJ": ab, "sum_fJ": ab + s, "sum_with_internal_fJ": abi + si,
                "board_fJ": bb, "rail_fJ": bb * BOARD["rail_ratio"],
                "closure_vs_board": (ab + s) / bb,
                "closure_vs_board_with_internal": (abi + si) / bb,
                "closure_vs_rail_with_internal": (abi + si) / (bb * BOARD["rail_ratio"]),
                "like_for_like": reg == "bus_arith",
            }
    out["flip_closure"] = clos

    # ---------- 3. the two controls: the index term and the result term ------------------
    ctrl = {}
    for name, tag, bitkey in (("register_index", "randn_accfix", "idx_toggles"),
                              ("result_word", "randn_resfix", "res_toggles")):
        d = load_power(a.power, tag)
        if d is None or rn is None:
            continue
        ac_full = load_acct(a.acct, "randn")
        ac_fix = load_acct(a.acct, tag)
        dE = (rn["energy_J"] - d["energy_J"]) / MULADDS            # J per mac
        dbits = (ac_full.get(bitkey, 0) - ac_fix.get(bitkey, 0)) / MULADDS
        ei_full = rn.get("internal_estimate", {}).get("switching_plus_internal_J", 0.0) / MULADDS
        ei_fix = d.get("internal_estimate", {}).get("switching_plus_internal_J", 0.0) / MULADDS
        ctrl[name] = {
            "control": tag,
            "delta_pJ_per_mac": dE * 1e12,
            "delta_pJ_per_mac_with_internal": (ei_full - ei_fix) * 1e12,
            "bits_changed_per_mac": dbits,
            "fJ_per_bit": (dE / dbits * 1e15) if dbits else None,
            "fJ_per_bit_with_internal": ((ei_full - ei_fix) / dbits * 1e15) if dbits else None,
            # The control does not move one bit field in isolation, and saying so is the point.
            # Holding the index still also stops the accumulator word the index selects from
            # changing; holding the result still also stops the accumulator READ-BACK from
            # changing. Both numbers are therefore composites, and they are compared against
            # board numbers that are composites of exactly the same kind.
            "also_changed_per_mac": {
                "operand_bus_bits": (ac_full.get("bus_toggles", 0)
                                     - ac_fix.get("bus_toggles", 0)) / MULADDS,
                "accumulator_read_bits": (ac_full.get("acc_rd_toggles", 0)
                                          - ac_fix.get("acc_rd_toggles", 0)) / MULADDS,
                "result_bits": (ac_full.get("res_toggles", 0)
                                - ac_fix.get("res_toggles", 0)) / MULADDS,
                "index_bits": (ac_full.get("idx_toggles", 0)
                               - ac_fix.get("idx_toggles", 0)) / MULADDS,
            },
            "is_composite": True,
        }
    if "register_index" in ctrl:
        c = ctrl["register_index"]
        c["board_fJ_per_index_bit_range"] = [BOARD["index_bit_board_fJ_lo"],
                                             BOARD["index_bit_board_fJ_hi"]]
        c["board_rail_fJ_per_index_bit_range"] = [BOARD["index_bit_board_fJ_lo"] * BOARD["rail_ratio"],
                                                  BOARD["index_bit_board_fJ_hi"] * BOARD["rail_ratio"]]
        if c["fJ_per_bit"]:
            c["closure_vs_board_lo"] = c["fJ_per_bit"] / BOARD["index_bit_board_fJ_hi"]
            c["closure_vs_board_hi"] = c["fJ_per_bit"] / BOARD["index_bit_board_fJ_lo"]
            c["closure_vs_rail_lo"] = c["fJ_per_bit"] / (BOARD["index_bit_board_fJ_hi"]
                                                         * BOARD["rail_ratio"])
            c["closure_vs_rail_hi"] = c["fJ_per_bit"] / (BOARD["index_bit_board_fJ_lo"]
                                                         * BOARD["rail_ratio"])
            # how much of the composite is the INDEX alone, bounded by subtracting the
            # accumulator-read bits at the transport's own fitted per-operand-bit slope
            # (the two ladder families bracket it). A negative lower bound means this design
            # cannot resolve the index from the data it drags, which is E61's own verdict.
            #
            # AMENDED: the bits subtracted are COUNTED bits (acc_rd_toggles), so they must be
            # priced at a per-counted-bit slope. The first version priced them at the DESIGNED-
            # bit slope - fJ per designed h-flip, a different unit, and the regressor this same
            # file reports as unfit - which put the bound at 72-136 fJ and supported the opposite
            # conclusion. At the counted-bus-bit slope the bound is 166-175 fJ, i.e. most of the
            # composite IS the index term.
            nb = c["also_changed_per_mac"]["accumulator_read_bits"]
            ib = c["bits_changed_per_mac"]
            bounds = {}
            for reg in ("bus", "bus_arith", "designed"):
                bnds = [(c["delta_pJ_per_mac"] * 1e3 - nb * lad[fam][reg]["slope_fJ"]) / ib
                        for fam in ("lq", "lb") if fam in lad and reg in lad[fam] and ib]
                if bnds:
                    bounds[reg] = sorted(bnds)
            if "bus" in bounds:
                c["index_alone_fJ_per_bit_bounds"] = bounds["bus"]
                c["index_alone_regressor"] = "bus (counted operand-bus bits, scope bench)"
                c["index_alone_share_of_composite"] = [b / c["fJ_per_bit"] for b in bounds["bus"]]
                c["index_alone_fJ_per_bit_bounds_by_regressor"] = bounds
                c["index_alone_note"] = (
                    "the composite minus the 13.75 COUNTED accumulator-read bits, priced at the "
                    "transport's own fitted per-counted-bus-bit slope (lq and lb bracket it). "
                    "The designed-bit entry is a sensitivity only: it prices counted bits at a "
                    "per-designed-flip slope, which is the wrong unit and the regressor this "
                    "ladder reports as unfit. Either way this is a bound, not a measurement - "
                    "an accumulator bit read through the 64 x 32 array does not take the path a "
                    "B-mantissa bit takes.")
    if "result_word" in ctrl:
        c = ctrl["result_word"]
        c["board_fJ_per_result_bit"] = BOARD["result_bit_board_fJ"]
        if c["fJ_per_bit"]:
            c["closure_vs_board"] = c["fJ_per_bit"] / BOARD["result_bit_board_fJ"]
            c["closure_vs_rail"] = c["fJ_per_bit"] / (BOARD["result_bit_board_fJ"]
                                                     * BOARD["rail_ratio"])
    out["controls"] = ctrl

    # ---------- 4. what it names of Q128's gap ------------------------------------------
    sw = rn["energy_J"] / MULADDS * 1e12
    swi = (rn["internal_estimate"]["switching_plus_internal_J"] / MULADDS * 1e12
           if "internal_estimate" in rn else sw)
    # the clock/signal split of the TOTAL, which is what decides the lower reading
    clk = rn["total"].get("clock_energy_J", 0.0) / MULADDS * 1e12
    sig = rn["total"].get("signal_energy_J", 0.0) / MULADDS * 1e12
    zsw = (zr["energy_J"] / MULADDS * 1e12) if zr else None
    zswi = ((zr["internal_estimate"]["switching_plus_internal_J"] / MULADDS * 1e12)
            if zr and "internal_estimate" in zr else zsw)
    zclk = (zr["total"].get("clock_energy_J", 0.0) / MULADDS * 1e12) if zr else None
    zsig = (zr["total"].get("signal_energy_J", 0.0) / MULADDS * 1e12) if zr else None
    # AMENDED: the LOWER reading. The first version charged the card only for the data-dependent
    # part (randn - zeros), on the ground that the zero-operand floor "may already be inside the
    # idle E38 subtracts". But only 34% of that floor is clock-net energy; the other 66% is
    # ordinary signal switching that the instruction stream causes - the accumulator index sweeps
    # 2i+h in EVERY pattern (idx_toggles = 992 per op with zero data), so the 64-entry read mux
    # tree keeps switching. An idle subtract cannot contain switching no idle performs. So the
    # defensible lower reading removes the clock NETS only.
    excl_clk = sig + (swi - sw)
    # the shared blocks (A file, TMP file, and the per-lane control's own clock root) are
    # instantiated once for VPU_LANE_NUM lanes, so a per-lane-MAC charge divides by 8.
    shared = {"tensor A register file, 32 b x 2", "tensor TMP register file, 32 b x 8"}
    per_lane = sum(r["pJ_per_mac_switching"] for r in table if r["part"] not in shared)
    shared_pj = sum(r["pJ_per_mac_switching"] for r in table if r["part"] in shared)
    fair = per_lane + shared_pj / LANES
    # TENC is the int8 accumulator; an fp32 multiply-add does not touch it. Priced separately.
    tenc = sum(r["pJ_per_mac_switching"] for r in table
               if r["part"].startswith("TIMA accumulator"))
    dd = out["totals"].get("data_dependent_pJ_per_mac")
    # AMENDED: the data-dependent figure WITH internal energy is a DIFFERENCE, not a scaling.
    # power.py's internal estimate is signal_toggles x a constant fJ per transition, so the
    # data-dependent internal is (randn - zeros) toggles x that constant. The first version
    # scaled the switching difference by the whole-design +internal ratio, which reads 0.5443
    # against the differenced 0.5176 - 5.2% high, and the same document differences both
    # controls and both ladder fits correctly.
    dd_i = (swi - zswi) if (zswi is not None) else None
    dd_i_scaled_superseded = (dd * swi / sw) if (dd and sw) else None
    out["gap"] = {
        "transport_switching_pJ_per_mac": sw,
        "transport_clock_net_pJ_per_mac": clk,
        "transport_signal_switching_pJ_per_mac": sig,
        "zeros_switching_pJ_per_mac": zsw,
        "zeros_clock_net_pJ_per_mac": zclk,
        "zeros_signal_switching_pJ_per_mac": zsig,
        "zeros_clock_share": (zclk / zsw) if zsw else None,
        # Two readings, and the honest answer is a range between them. The UPPER one charges the
        # card for the whole transport netlist. The LOWER one removes the clock-NET energy only
        # (0.223 pJ/MAC), because that is the only part of the zero-operand floor an idle subtract
        # could already contain - the rest of the floor is the accumulator index sweep, which the
        # card's instruction stream performs too. The data-dependent figure below is reported as
        # its own quantity (how much of the transport moves with the operands), NOT as the lower
        # end of the gap-closure range.
        "transport_excl_clock_nets_with_internal_pJ_per_mac": excl_clk,
        "share_of_board_gap_excl_clock_nets": excl_clk / BOARD["unaccounted_board_pJ"],
        "share_of_rail_gap_excl_clock_nets": excl_clk / BOARD["unaccounted_rail_pJ"],
        "new_ledger_total_excl_clock_nets_pJ": BOARD["arith_pJ"] + excl_clk,
        "new_closure_vs_board_excl_clock_nets":
            (BOARD["arith_pJ"] + excl_clk) / BOARD["mac_board_pJ"],
        "new_closure_vs_rail_excl_clock_nets":
            (BOARD["arith_pJ"] + excl_clk) / BOARD["mac_rail_pJ"],
        "transport_data_dependent_pJ_per_mac": dd,
        "transport_data_dependent_with_internal_pJ_per_mac": dd_i,
        "transport_data_dependent_with_internal_scaled_superseded_pJ": dd_i_scaled_superseded,
        "share_of_board_gap_data_dependent": (dd_i / BOARD["unaccounted_board_pJ"]) if dd_i else None,
        "share_of_rail_gap_data_dependent": (dd_i / BOARD["unaccounted_rail_pJ"]) if dd_i else None,
        "new_ledger_total_data_dependent_pJ": (BOARD["arith_pJ"] + dd_i) if dd_i else None,
        "new_closure_vs_board_data_dependent":
            ((BOARD["arith_pJ"] + dd_i) / BOARD["mac_board_pJ"]) if dd_i else None,
        "new_closure_vs_rail_data_dependent":
            ((BOARD["arith_pJ"] + dd_i) / BOARD["mac_rail_pJ"]) if dd_i else None,
        "transport_switching_plus_internal_pJ_per_mac": swi,
        "transport_charged_per_lane_mac_pJ": fair,
        "shared_blocks_pJ_as_built": shared_pj,
        "shared_blocks_divided_by_lanes_pJ": shared_pj / LANES,
        "tenc_not_on_fp32_path_pJ": tenc,
        "unaccounted_board_pJ": BOARD["unaccounted_board_pJ"],
        "unaccounted_rail_pJ": BOARD["unaccounted_rail_pJ"],
        "share_of_board_gap_switching": sw / BOARD["unaccounted_board_pJ"],
        "share_of_board_gap_with_internal": swi / BOARD["unaccounted_board_pJ"],
        "share_of_rail_gap_switching": sw / BOARD["unaccounted_rail_pJ"],
        "share_of_rail_gap_with_internal": swi / BOARD["unaccounted_rail_pJ"],
        "share_of_board_gap_charged_per_lane": fair / BOARD["unaccounted_board_pJ"],
        "share_of_rail_gap_charged_per_lane": fair / BOARD["unaccounted_rail_pJ"],
        "new_ledger_total_pJ": BOARD["arith_pJ"] + swi,
        "new_closure_vs_board": (BOARD["arith_pJ"] + swi) / BOARD["mac_board_pJ"],
        "new_closure_vs_rail": (BOARD["arith_pJ"] + swi) / BOARD["mac_rail_pJ"],
        "old_closure_vs_board": BOARD["arith_pJ"] / BOARD["mac_board_pJ"],
        "old_closure_vs_rail": BOARD["arith_pJ"] / BOARD["mac_rail_pJ"],
        "charging_convention": ("the per-part table and every total charge the shared files "
                                "(TENA, TMP) and the one-lane netlist's whole clock root to this "
                                "one lane; transport_charged_per_lane_mac_pJ divides the two "
                                "shared files by VPU_LANE_NUM = 8 instead (a 0.0062 pJ/MAC "
                                "difference). The clock root is not divided in either: an 8-lane "
                                "netlist's root is not 8x this one's."),
    }

    # AMENDED: the card's own `zeros` measurement bounds the register-file model FROM ABOVE.
    # E38 ran the same instruction stream with zero operand data and the WHOLE BOARD cost
    # 0.27 pJ per multiply-add over idle. One lane's transport cannot cost more than the whole
    # board in the same run - and this model does, by 2.4x, or 1.6x counting its signal part
    # alone. Even the register-file array row by itself exceeds it.
    if zsw is not None:
        zb = BOARD["mac_board_zeros_pJ"]
        arr = next((r for r in table if r["is_model"]
                    and r["part"].startswith("VPU register file array")), None)
        out["gap"]["card_zeros_bound"] = {
            "board_zeros_pJ_per_mac": zb,
            "board_zeros_per_card_pJ": BOARD["mac_board_zeros_per_card_pJ"],
            "transport_zeros_pJ_per_mac": zsw,
            "ratio_transport_over_board": zsw / zb,
            "transport_zeros_signal_only_pJ_per_mac": zsig,
            "ratio_signal_only_over_board": (zsig / zb) if zsig is not None else None,
            "rf_array_zeros_pJ_per_mac": arr["pJ_per_mac_zeros"] if arr else None,
            "rf_array_zeros_clock_pJ_per_mac": arr["pJ_per_mac_zeros_clock"] if arr else None,
            "ratio_rf_array_over_board": (arr["pJ_per_mac_zeros"] / zb) if arr else None,
            "verdict": ("the latch-array model is not merely an unbounded ceiling: a card "
                        "measurement puts it above what the board permits. Whichever way the "
                        "idle subtract falls - if the lane's clocks run at idle the card figure "
                        "excludes clock and the comparison is against the 0.431 pJ signal part; "
                        "if they are gated at idle the comparison is against the whole 0.654 - "
                        "the model over-prices. Over-pricing of the array's write port is "
                        "therefore the leading explanation for the result-bit term reading 101% "
                        "of its card number."),
        }

    # m2: the internal-energy estimate is weighted by the ARITHMETIC netlist's cell mix (which is
    # what lets the two ledgers add). Re-weighting on this netlist's own mix as a sensitivity.
    if a.cell_energies and a.census:
        try:
            ce = json.load(open(a.cell_energies))["census_weighted_mix"]
            by = ce["by_cell"]
            cen = json.load(open(a.census)).get("by_cell_type", {})
            num = den = 0.0
            missing = {}
            for cell, n in cen.items():
                e = by.get(cell)
                if e is None:
                    missing[cell] = n
                    continue
                num += n * float(e["E_int_per_transition_VDDonly_fJ"])
                den += n
            if den:
                e_this = (num / den) * (0.517 / 0.7) ** 2
                e_used = rn["internal_estimate"]["E_int_per_transition_fJ_at_vdd"]
                st = rn["total"]["signal_toggles"] / MULADDS
                out["internal_mix_sensitivity"] = {
                    "mix_used_by_power_py": "the arithmetic netlist's (txfma_top flattened)",
                    "mix_source": ce.get("source"),
                    "E_int_per_transition_fJ_used": e_used,
                    "E_int_per_transition_fJ_this_netlist_mix": e_this,
                    "relative_difference": e_this / e_used - 1.0,
                    "internal_pJ_per_mac_used": st * e_used / 1e3,
                    "internal_pJ_per_mac_this_netlist_mix": st * e_this / 1e3,
                    "combinational_cells_this_netlist": den,
                    "cells_with_no_liberty_entry": missing,
                    "note": ("power.py's own census fields in every power JSON "
                             "(combinational_cells_priced, sequential_and_tie_cells_skipped) are "
                             "the MIX's provenance census, not this netlist's. Kept as the tool "
                             "produced them, because applying the txfma mix unchanged is the "
                             "precondition for adding the two ledgers; this row says what it "
                             "costs."),
                }
        except (KeyError, ValueError, OSError) as exc:
            out["internal_mix_sensitivity"] = {"error": repr(exc)}

    if a.census:
        c = json.load(open(a.census))
        out["census_total"] = c.get("total")
        # join the census onto the parts, by the same prefix rule, depth-1 blocks only so
        # nothing is double-counted (vrf/arr is inside vrf)
        FIELDS = (("cells", "cells"), ("transistors", "transistors"), ("area", "area_um2"),
                  ("flops", "flops"), ("latches", "latches"), ("clk_cap_ff", "clk_cap_fF"))
        rows = {b["path"]: b for b in c.get("blocks", [])}

        def blank():
            return {d: 0.0 for _, d in FIELDS}

        def add(e, b, sign=1):
            for src, dst in FIELDS:
                e[dst] += sign * (b.get(src, 0.0) or 0.0)

        # A census row counts its own children, so a part whose prefix is a nested path (here
        # vrf/arr, the register-file array inside vpu_rf's wrapper) must be TAKEN OUT of its
        # parent's part, or the array's 15,685 cells land twice - once as the array and once as
        # the collision bypass that wraps it.
        nested = [pre for pre, _ in PARTS if "/" in pre and pre in rows]
        cj = {}
        for path, b in rows.items():
            if b.get("depth") != 1:
                continue
            k = part_of(path)
            e = cj.setdefault(k, blank())
            add(e, b)
            for ch in nested:
                if ch.startswith(path + "/") and part_of(ch) != k:
                    add(e, rows[ch], -1)
        for ch in nested:
            e = cj.setdefault(part_of(ch), blank())
            add(e, rows[ch])
        out["census_per_part"] = cj
        for r in out["per_part"]:
            if r["part"] in cj:
                r["census"] = cj[r["part"]]
        # the sequential bits this netlist holds, against the arithmetic's
        tot = c.get("total", {})
        out["sequential"] = {
            "transport_flops": tot.get("flops"),
            "transport_latches": tot.get("latches"),
            "transport_sequential_bits": (tot.get("flops") or 0) + (tot.get("latches") or 0),
            "transport_clk_pin_cap_fF": tot.get("clk_cap_ff"),
            # 2026-10-26-open-netlist/README.md, census_mixed.json, the same flow
            "arithmetic_flops": 1974, "arithmetic_latches": 13,
            "arithmetic_clk_pin_cap_fF": 945.0,
            "arithmetic_cells": 15805, "arithmetic_transistors": 159896,
            "arithmetic_area_um2": 2126.1,
            "note": "Q126(b)'s 602.5 register bits clocked per multiply-add is counted inside "
                    "txfma_7s only (the 83 libs/registers instances ff_acct.sv stands in for, "
                    "838 bits). None of the sequential bits in this netlist are in that scope, "
                    "so the transport's clocked bits are additional to the 602.5, not part of it.",
        }

    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1)

    # --- a readable print ---------------------------------------------------------------
    print(f"transport, random multiply-add, one lane: {sw:.4f} pJ switching, "
          f"{swi:.4f} pJ with the cells' internal, clock {rn['clock_share']*100:.1f}%")
    print(f"{'part':46} {'pJ/MAC':>8} {'clock':>8} {'data-dep':>9} {'toggles':>8}  model")
    for r in table:
        print(f"{r['part'][:45]:46} {r['pJ_per_mac_switching']:8.4f} "
              f"{r['pJ_per_mac_clock']:8.4f} {r['pJ_per_mac_data_dependent']:9.4f} "
              f"{r['signal_toggles_per_mac']:8.1f}  {'Y' if r['is_model'] else '-'}")
    for fam, r in clos.items():
        print(f"\nflip, {fam}: arithmetic {r['arithmetic_fJ']:.1f} + transport "
              f"{r['transport_fJ_per_designed_bit']:.1f} +- {r['transport_se_fJ']:.1f} = "
              f"{r['sum_fJ']:.1f} fJ  vs board {r['board_fJ']:.1f} fJ "
              f"({r['closure_vs_board']*100:.0f}%, was {r['arith_alone_closure_vs_board']*100:.0f}%)"
              f"; with internal {r['sum_with_internal_fJ']:.1f} fJ "
              f"({r['closure_vs_board_with_internal']*100:.0f}%)   [designed-bit regressor]")
        for lab in ("arith_bench_counts", "scope_bench_counts"):
            b = r.get(f"per_bus_bit_{lab}")
            if b:
                print(f"  per bus bit, {lab:18}: {b['arithmetic_fJ']:.1f} + "
                      f"{b['transport_fJ']:.1f} +- {b['transport_se_fJ']:.1f} = {b['sum_fJ']:.1f} fJ "
                      f"vs {b['board_fJ']:.1f} ({b['closure_vs_board']*100:.0f}%)"
                      f"{'  <- like for like' if b['like_for_like'] else ''}")
    for k, r in ctrl.items():
        print(f"\n{k}: {r['delta_pJ_per_mac']*1000:.1f} fJ/MAC over {r['bits_changed_per_mac']:.2f} "
              f"bits = {r['fJ_per_bit'] if r['fJ_per_bit'] is None else round(r['fJ_per_bit'],2)} fJ/bit")
    g = out["gap"]
    print(f"\ncap priced: {out['totals']['cap_fraction_priced']*100:.1f}% of "
          f"{out['totals']['cap_fF_extracted']:.0f} fF")
    print(f"zero-operand floor {g['zeros_switching_pJ_per_mac']:.4f} pJ = clock nets "
          f"{g['zeros_clock_net_pJ_per_mac']:.4f} ({g['zeros_clock_share']*100:.0f}%) + signal "
          f"{g['zeros_signal_switching_pJ_per_mac']:.4f} (the index sweeps in every pattern)")
    z = g.get("card_zeros_bound")
    if z:
        print(f"CARD BOUND: the whole board's `zeros` MAC is {z['board_zeros_pJ_per_mac']:.2f} pJ, "
              f"so one lane's {z['transport_zeros_pJ_per_mac']:.4f} is "
              f"{z['ratio_transport_over_board']:.2f}x it "
              f"({z['ratio_signal_only_over_board']:.2f}x on signal alone; the RF-array row alone "
              f"is {z['ratio_rf_array_over_board']:.2f}x) -- the model over-prices")
    print(f"\nRANGE, + the cells' internal energy:")
    print(f"  upper (whole netlist)            {g['transport_switching_plus_internal_pJ_per_mac']:.4f} pJ -> "
          f"{g['share_of_board_gap_with_internal']*100:.1f}% of the 3.837 pJ board gap, "
          f"{g['share_of_rail_gap_with_internal']*100:.1f}% of the rail gap; ledger "
          f"{g['new_ledger_total_pJ']:.3f}, closure {g['new_closure_vs_board']*100:.0f}% board / "
          f"{g['new_closure_vs_rail']*100:.0f}% rail")
    print(f"  lower (less the clock nets)      {g['transport_excl_clock_nets_with_internal_pJ_per_mac']:.4f} pJ -> "
          f"{g['share_of_board_gap_excl_clock_nets']*100:.1f}% of the board gap, "
          f"{g['share_of_rail_gap_excl_clock_nets']*100:.1f}% of the rail gap; ledger "
          f"{g['new_ledger_total_excl_clock_nets_pJ']:.3f}, closure "
          f"{g['new_closure_vs_board_excl_clock_nets']*100:.0f}% board / "
          f"{g['new_closure_vs_rail_excl_clock_nets']*100:.0f}% rail")
    print(f"  of which moves with the operands {g['transport_data_dependent_with_internal_pJ_per_mac']:.4f} pJ "
          f"(a separate quantity, NOT the bottom of the range)")
    print(f"  closure was {g['old_closure_vs_board']*100:.0f}% of the board, "
          f"{g['old_closure_vs_rail']*100:.0f}% of the rail (arithmetic alone)")


if __name__ == "__main__":
    main()
