#!/usr/bin/env python3
"""Q130(a): build the kinds-of-numbers inventory from what is already committed.

Reads committed JSON in docs/reports/data/ and writes inventory.json plus the
markdown tables the README quotes. No third-party modules; no card access.

Every emitted cell carries `source` (path + key) and `status` (measured /
modelled / predicted / missing). A number is typed into this file ONLY where the
experiment left no machine-readable form; each such number is in TYPED below with
its citation, and the emitted cell says `typed: true`.

Usage (from the repository's top directory):
    python3 docs/reports/data/2026-10-31-q130-kinds-inventory/build_inventory.py \
        --out docs/reports/data/2026-10-31-q130-kinds-inventory
"""

import argparse
import json
import math
import re
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, ".."))          # docs/reports/data

# ---------------------------------------------------------------- source paths
P_ABLA = "2026-09-25-claims-v3/results/abla.runs.json"
P_ABLA_S = "2026-09-25-claims-v3/results/abla.json"      # the scored registered items
P_ABLB = "2026-09-25-claims-v3/results/ablb.runs.json"
P_H_A2 = "2026-09-21-horace-aifoundry2/horace3.json"
P_H_A3 = "2026-09-22-horace-aifoundry3/horace3.json"
P_ABL15 = "2026-09-21-horace-aifoundry2/ablation.json"
P_PRED14 = "2026-09-21-horace-aifoundry2/structured_predictions_before.json"
P_RECOUNT = "2026-10-26-toggle-recount/recount.json"
P_E64_F = "2026-10-23-e64-horace-power-limit/figures.json"
P_E64_R = "2026-10-23-e64-horace-power-limit/results.json"
P_E60 = "2026-10-20-bitflip-ladder/hl.json"
P_E65 = "2026-10-26-e65-bit-prices-hart-ladder/hl.json"
P_E67 = "2026-10-27-e67-a-side-bit-prices/hl.json"
P_E68 = "2026-10-27-e68-stage-map/verdicts.json"
P_E70 = "2026-10-27-e70-saturation-ladder/hl.json"
P_E70S = "2026-10-27-e70-saturation-ladder/scored.json"
P_E71 = "2026-10-27-e71-idle-slope-aifoundry3/slopes.json"
P_E72 = "2026-10-27-e72-600mhz/verdicts.json"
P_E74 = "2026-10-28-e74-register-file-cells/rf.json"
P_E75 = "2026-10-28-e75-memory-flip-ladder/mf.json"
P_E61 = "2026-10-21-dtf/dtf.json"

# MACs per 16x16x16 TensorFMA are FORMAT-DEPENDENT. tools/claims-v3/hpl/surface_hpl.py:32
# gives flops per op (fp32 8192, fp16 16384, int8 32768) and one multiply-add is two
# flops, so MACs per op are 4,096 / 8,192 / 16,384. MACS_PER_OP keeps the fp32 figure
# because every use of it below is fp32 (E67's anchors and the RTL recount); anything
# that crosses formats must take its divisor from MACS_PER_OP_BY_FMT, and anything that
# starts from a rate must use MAC/s = TFLOPS or TOPS x 1e12 / 2, which holds in every format.
MACS_PER_OP_BY_FMT = {"fp32": 4096, "fp16": 8192, "int8": 16384}
MACS_PER_OP = MACS_PER_OP_BY_FMT["fp32"]
FLOPS_PER_MAC = 2           # one multiply-add = two flops

# Numbers with no machine-readable form in the repo, typed here with a citation.
TYPED = {
    "e64_idle_board_W_LAD": {
        "value": 24.25, "unit": "W",
        "note": "mean of the 20 LAD runs' gate readings (die 50-55 C, 600 MHz)",
        "source": "docs/reports/data/2026-10-23-e64-horace-power-limit/s1/runs.jsonl: gate.reading[2], block LAD",
    },
    "e64_idle_board_W_SUS": {
        "value": 25.02, "unit": "W",
        "note": "mean of the 9 SUS runs' gate readings (die 57 C, 600 MHz)",
        "source": "docs/reports/data/2026-10-23-e64-horace-power-limit/s1/runs.jsonl: gate.reading[2], block SUS",
    },
    "e65_flowM_fJ": {
        "value": 745.0, "interval": "+-56", "unit": "fJ per flipped bit",
        "note": "b bit 11 alternating against a = pi, board, all-in; E71 re-prices it 722 +- 61 fJ",
        "source": "docs/reports/data/2026-10-26-e65-bit-prices-hart-ladder/README.md (the flow-M case); "
                  "re-price docs/reports/data/2026-10-27-q129-leak-sensitivity/README.md",
    },
    "e68_lo12_fJ_band": {
        "value": "117.5-135.9", "unit": "fJ per flipped bit",
        "note": "sm_lo12 at the registered 1.508 W/C and at E66's measured 0.296 W/C; the band is the "
                "leakage slope, which E68 never measured on its own data",
        "source": "docs/reports/data/2026-10-27-e68-stage-map/README.md; "
                  "verdicts.json items.sm_lo12.fJ_per_flipped_bit is the 1.508 end only",
    },
    "e68_s_mul": {
        "value": 0.50, "interval": "+-0.15", "unit": "fraction",
        "note": "post-hoc column assignment; the registered two-column fit wants a negative multiplier term",
        "source": "docs/reports/data/2026-10-27-e68-stage-map/README.md (post-hoc fit); posthoc.txt",
    },
}
# The zeros->random split (lane un-gating against operand flips) was typed from E70's
# README in the first cut of this file. It is arithmetic on three published levels, so it
# is COMPUTED here instead, with an interval and a stated footing: ungating_split() below.


def jload(rel):
    with open(os.path.join(DATA, rel)) as fh:
        return json.load(fh)


def src(rel, key):
    return "docs/reports/data/" + rel + ": " + key


def r(x, n=4):
    if x is None:
        return None
    if isinstance(x, (int,)) and not isinstance(x, bool):
        return x
    try:
        return round(float(x), n)
    except (TypeError, ValueError):
        return x


# ---------------------------------------- configuration variants, which are not kinds
# Each of these rows is the SAME operand stream at a different minion count, or with TenB
# streaming on. They are rows of the cell list; they are not kinds of number. Every cell's
# `conditions` already carries the minion count or the nnz_a/row_mask that makes it a
# variant; the kind counts in row_taxonomy() fold them into their base kind so that a
# coverage claim counts kinds of number and nothing else.
VARIANT_OF = {
    ("fp32", "randn@256min"): ("randn", "256 minions (claims-v3 abla)"),
    ("fp32", "randn@512min"): ("randn", "512 minions (claims-v3 abla)"),
    ("fp32", "randn@640min"): ("randn", "640 minions (E64's MIN sweep)"),
    ("fp32", "randn@768min"): ("randn", "768 minions (E64's MIN sweep)"),
    ("fp32", "randn_8"): ("randn", "256 minions (September E15; the same point as randn@256min)"),
    ("fp32", "randn_16"): ("randn", "512 minions (September E15; the same point as randn@512min)"),
    ("fp32", "randn_24"): ("randn", "768 minions (September E15; the same point as randn@768min)"),
    ("fp16", "randn+TenB"): ("randn", "TenB streaming on (claims-v3 ablb)"),
    ("int8", "randn+TenB"): ("randn", "TenB streaming on (claims-v3 ablb)"),
    ("int8", "ones+TenB"): ("ones", "TenB streaming on (claims-v3 ablb)"),
}


def ungating_split():
    """The zeros->random board step, split into lane un-gating and operand flips.

    Arithmetic on three published levels, all aifoundry3 at a pinned 600 MHz with a
    58 C launch, as E70's README does it - but with the interval propagated and the
    footing stated, which the README's bare "8.6 W / 16.1 W / 24.66 W" does not carry.

    Every level is a `p80`: board power with that run's own leakage rise since launch
    removed (p80 = p_raw - k (t_win - t_launch)). Both campaigns refer their levels to
    the same 58 C launch, so no leakage term survives the difference; the two reducers
    used k = 0.1755 (E67) and 0.1975 W/C (E70), and `slope_sensitivity_W` below says
    how little that disagreement is worth.
    """
    e67 = jload(P_E67)["cards"]["aifoundry3"]["anchors"]
    e70 = jload(P_E70)["cards"]["aifoundry3"]["items"]
    z, rn = e67["anchor_zeros"], e67["anchor_randn"]
    const = {k: (e70[k]["p80"], e70[k].get("p80_se", 0.0)) for k in ("lq_h0", "aq_h0", "anchor_pi")}
    cvals = [v[0] for v in const.values()]
    cm = st.mean(cvals)
    cse = st.stdev(cvals) / math.sqrt(len(cvals))        # the spread BETWEEN the items dominates

    def sens(k):
        """both levels re-reduced from the raw runs at one common slope k."""
        out = {}
        for rel, items in ((P_E67, ("anchor_zeros",)), (P_E70, ("lq_h0", "aq_h0", "anchor_pi"))):
            d = jload(rel)
            for item in items:
                byp = {}
                for x in d["runs"]:
                    if x["card"] != "aifoundry3" or x["item"] != item or x.get("fail"):
                        continue
                    byp.setdefault(x["pass"], []).append(x["p_raw"] - k * (x["t_win"] - x["start_c"]))
                out[item] = st.mean([st.mean(v) for v in byp.values()])
        return st.mean([out[i] for i in ("lq_h0", "aq_h0", "anchor_pi")]) - out["anchor_zeros"]

    ung, flips = cm - z["p80"], rn["p80"] - cm
    return {
        "zeros_level_W": {"value": r(z["p80"], 3), "se": r(z["se"], 4), "n_passes": z["n"],
                          "source": src(P_E67, "cards.aifoundry3.anchors.anchor_zeros.p80")},
        "constant_operand_level_W": {
            "value": r(cm, 3), "se": r(cse, 4),
            "items": {k: r(v[0], 3) for k, v in const.items()},
            "spread_W": r(max(cvals) - min(cvals), 3),
            "source": src(P_E70, "cards.aifoundry3.items[lq_h0, aq_h0, anchor_pi].p80 (mean of 3)")},
        "random_level_W": {"value": r(rn["p80"], 3), "se": r(rn["se"], 4), "n_passes": rn["n"],
                           "source": src(P_E67, "cards.aifoundry3.anchors.anchor_randn.p80")},
        "lane_ungating_W": {"value": r(ung, 3), "se": r(math.hypot(cse, z["se"]), 4),
                            "range_over_constant_items_W": [r(min(cvals) - z["p80"], 3),
                                                            r(max(cvals) - z["p80"], 3)]},
        "operand_flips_W": {"value": r(flips, 3), "se": r(math.hypot(rn["se"], cse), 4)},
        "step_W": {"value": r(rn["p80"] - z["p80"], 3), "se": r(math.hypot(rn["se"], z["se"]), 4)},
        "slope_sensitivity_W": {
            "ungating_at_k_0.1975": r(sens(0.1975), 3),
            "ungating_at_k_0.3803": r(sens(0.3803), 3),
            "note": "both levels re-reduced from the raw runs at ONE common slope: E70's registered "
                    "0.1975 W/C and E71's steepest measured idle slope on this card, 0.3803 W/C "
                    "(58-62 C). The un-gating term moves %.3f W between those two, against its own "
                    "%.3f W standard error, so the leakage footing is not what the split rests on - "
                    "which is what 'no leakage term survives the difference' means here. At E70's "
                    "own slope the re-reduction agrees with the published-anchor arithmetic above "
                    "to %.3f W. The reducers themselves used k = 0.1755 (E67) and 0.1975 (E70), "
                    "solved from their own runs' p_raw, p80, t_win and start_c."
                    % (abs(sens(0.1975) - sens(0.3803)), math.hypot(cse, z["se"]),
                       abs(sens(0.1975) - (cm - z["p80"]))),
        },
        "published_as": "E70's README quotes this split as 8.6 W / 16.1 W / 24.66 W, from the same "
                        "three levels with the constant-operand level rounded to 36.40 W",
        "source": "docs/reports/data/2026-10-27-e70-saturation-ladder/README.md (the zeros->random "
                  "step) recomputed from " + P_E67 + " and " + P_E70,
    }


SPLIT = ungating_split()
UNG = SPLIT["lane_ungating_W"]["value"]
UNG_SE = SPLIT["lane_ungating_W"]["se"]
FLIPS = SPLIT["operand_flips_W"]["value"]
STEP = SPLIT["step_W"]["value"]

# Which zero a cell is measured against. Rendered as a superscript in tables.md.
BASIS = {
    "idle_lc": "over the pre-launch idle, leakage-normalised to a fixed launch temperature",
    "idle_raw": "over the pre-launch idle, NOT leakage-corrected (reads high on the busiest kinds "
                "by roughly leak x the die rise). The offset DIFFERS BY QUANTITY on fp32 randn at "
                "600 MHz on aifoundry2: switching_W +2.34 W (+8.6%, 29.52 against the "
                "leakage-normalised 27.18) and pJ per MAC +0.71 pJ (+12.0%, 6.630 against 5.920). "
                "The extra 3.1% is the denominator: the September pJ column implies 8.905 TFLOPS "
                "where the same record's `tflops` field reads 9.183",
    "idle_elec": "the September model's fitted electrical term, leakage and thermal terms removed",
    "zeros": "over a RUNNING kernel on zero data, so the %.2f +- %.2f W of lane un-gating is NOT "
             "in it" % (UNG, UNG_SE),
    "const": "over a constant NON-zero operand, so the lane is un-gated and only the flips are missing",
    "model": "E64's governor model's data-dependent term c x s(f), referred to a 58 C die",
    "abs": "absolute, no baseline subtracted",
    "none": "not a power difference",
}


def cell(fmt, kind, quantity, value, unit, conditions, source,
         status="measured", interval=None, typed=False, extra=None, basis="none"):
    c = {
        "format": fmt, "kind": kind, "quantity": quantity,
        "value": value, "interval": interval, "unit": unit,
        "conditions": conditions, "source": source, "status": status,
        "basis": basis,
    }
    if (fmt, kind) in VARIANT_OF:
        base, what = VARIANT_OF[(fmt, kind)]
        c["variant_of"] = base
        c["variant_is"] = what
    if typed:
        c["typed"] = True
    if extra:
        c.update(extra)
    return c


# =============================================================== table 1 rows
def pm(vals):
    """mean and a +-SE string for a small sample."""
    if not vals:
        return None, None
    m = st.mean(vals)
    if len(vals) < 2:
        return m, None
    se = st.stdev(vals) / math.sqrt(len(vals))
    return m, "+-%.4g" % se


def abla_cells():
    """E38 / claims-v3 abla: 23 configurations on three cards, 600 MHz, 4 passes.

    `switching` is board power over the pre-launch idle, with each card's
    September leakage slope times the rise since launch removed.
    """
    d = jload(P_ABLA)
    params = d["params_by_card"]
    idle = d["idle_by_card"]
    out, rows = [], {}
    # config -> (format, kind) for the operand-kind configs
    cfgmap = {
        "fp32_zeros": ("fp32", "zeros"), "fp32_ones": ("fp32", "ones"),
        "fp32_randn": ("fp32", "randn"), "fp32_signs": ("fp32", "signs"),
        "fp32_pow2": ("fp32", "pow2"), "fp32_mant": ("fp32", "mant"),
        "fp32_a1br": ("fp32", "a_ones_b_randn"), "fp32_arb1": ("fp32", "a_randn_b_ones"),
        "fp16_zeros": ("fp16", "zeros"), "fp16_ones": ("fp16", "ones"),
        "fp16_randn": ("fp16", "randn"),
        "int8_zeros": ("int8", "zeros"), "int8_ones": ("int8", "ones"),
        "int8_randn": ("int8", "randn"),
        "m_butterfly": ("fp32", "m_butterfly"), "m_fft_cos": ("fp32", "m_fft_cos"),
        "m_hadamard": ("fp32", "m_hadamard"), "m_kaleidoscope": ("fp32", "m_kaleidoscope"),
        "m_negzero": ("fp32", "m_negzero"), "m_relu": ("fp32", "m_relu"),
        "fp32_randn_8": ("fp32", "randn@256min"), "fp32_randn_16": ("fp32", "randn@512min"),
    }
    for card, runs in d["runs"].items():
        kept = [x for x in runs if x.get("kept_busy")]
        bycfg = {}
        for x in kept:
            bycfg.setdefault(x["config"], []).append(x)
        for cfg, rs in sorted(bycfg.items()):
            if cfg not in cfgmap:
                continue
            fmt, kind = cfgmap[cfg]
            sw, se = pm([x["switching"] for x in rs])
            per_s = st.mean([x["per_s"] for x in rs])
            unit = rs[0]["unit"]
            cond = ("%s, 600 MHz, %d minions, launch %.1f C, leak %.2f W/C, "
                    "over pre-launch idle %.2f W, n=%d passes"
                    % (card, rs[0]["minions"], params[card]["launch"],
                       params[card]["leak"], idle[card]["idle_w"], len(rs)))
            out.append(cell(fmt, kind, "switching_W", r(sw, 3), "W", cond,
                            src(P_ABLA, "runs.%s[config=%s].switching (mean of %d)" % (card, cfg, len(rs))),
                            interval=se, basis="idle_lc"))
            if unit == "MAC":
                out.append(cell(fmt, kind, "pJ_per_MAC", r(sw / per_s * 1e12, 4),
                                "pJ per MAC (board, over idle)", cond, basis="idle_lc",
                                source=src(P_ABLA, "runs.%s[config=%s].switching / .per_s" % (card, cfg)),
                                interval=("+-%.4g" % (float(se[2:]) / per_s * 1e12) if se else None)))
                out.append(cell(fmt, kind, "pJ_per_flop", r(sw / per_s / FLOPS_PER_MAC * 1e12, 4),
                                "pJ per flop (board, over idle)",
                                cond + "; 1 MAC = 2 flops",
                                src(P_ABLA, "runs.%s[config=%s].switching / (.per_s * 2)" % (card, cfg))))
                out.append(cell(fmt, kind, "TFLOPS", r(per_s * FLOPS_PER_MAC / 1e12, 3),
                                "TFLOPS" if fmt != "int8" else "TOPS",
                                cond + "; fixed 600 MHz, no governor action",
                                src(P_ABLA, "runs.%s[config=%s].per_s * 2" % (card, cfg))))
            rows.setdefault((fmt, kind), set()).add("abla:" + card)
    return out, rows


def ablb_cells():
    """E39 / claims-v3 ablb: the sparsity ladder and the TenB arms, three cards, 600 MHz."""
    d = jload(P_ABLB)
    params, idle = d["params_by_card"], d["idle_by_card"]
    # nnz_a out of 256 A elements -> the A-side sparsity level
    cfgmap = {
        "fma-dense": ("fp32", "small_dense_0pc"), "fma-col50": ("fp32", "small_sparse_69pc"),
        "fma-50": ("fp32", "small_sparse_50pc"), "fma-875": ("fp32", "small_sparse_90pc"),
        "fma-zero": ("fp32", "small_sparse_100pc"), "fma-rowmask": ("fp32", "small_rowmask_half"),
        "int8_randn_l1": ("int8", "randn"), "int8_ones_l1": ("int8", "ones"),
        "fp16_randn_l1": ("fp16", "randn"),
        "int8_randn_tenb": ("int8", "randn+TenB"), "int8_ones_tenb": ("int8", "ones+TenB"),
        "fp16_randn_tenb": ("fp16", "randn+TenB"),
    }
    out, rows = [], {}
    for card, runs in d["runs"].items():
        kept = [x for x in runs if x.get("kept_busy")]
        bycfg = {}
        for x in kept:
            bycfg.setdefault(x["config"], []).append(x)
        for cfg, rs in sorted(bycfg.items()):
            if cfg not in cfgmap:
                continue
            fmt, kind = cfgmap[cfg]
            sw, se = pm([x["switching"] for x in rs])
            per_s = st.mean([x["per_s"] for x in rs])
            cond = ("%s, 600 MHz, %s nnz_a=%s of 256, row_mask=%s, over pre-launch idle %.2f W, "
                    "leak %.2f W/C, n=%d blocks"
                    % (card, rs[0]["type"], rs[0]["nnz_a"], rs[0]["row_mask"],
                       idle[card]["idle_w"], params[card]["leak"], len(rs)))
            out.append(cell(fmt, kind, "switching_W", r(sw, 3), "W", cond,
                            src(P_ABLB, "runs.%s[config=%s].switching" % (card, cfg)),
                            interval=se, basis="idle_lc"))
            out.append(cell(fmt, kind, "pJ_per_MAC", r(sw / per_s * 1e12, 4),
                            "pJ per MAC (board, over idle)", cond,
                            src(P_ABLB, "runs.%s[config=%s].switching / .per_s" % (card, cfg)),
                            basis="idle_lc"))
            rows.setdefault((fmt, kind), set()).add("ablb:" + card)
    return out, rows


def sept_cells():
    """E9 (aifoundry2, 14 patterns) and E20 (aifoundry3, 8), 600 MHz, strict start."""
    out, rows = [], {}
    for rel, card, launch in ((P_H_A2, "aifoundry2", 80.9), (P_H_A3, "aifoundry3", 55.3)):
        d = jload(rel)
        leak = d["leak_w_per_c"]
        for kind, p in d["patterns"].items():
            cond = ("%s, 600 MHz, 1024 minions, strict start at ~%.1f C, 7 s runs, "
                    "leak %.3f W/C, n=%d runs" % (card, p["start_temp"], leak, p["n"]))
            over_idle = p["p_early"] - p["p_before"]
            out.append(cell("fp32", kind, "switching_W", r(over_idle, 3), "W",
                            cond + "; p_early - p_before, NOT leakage-corrected",
                            src(rel, "patterns.%s.p_early - .p_before" % kind), basis="idle_raw"))
            out.append(cell("fp32", kind, "switching_W_leakcorr", r(p["a_electrical"], 3), "W",
                            cond + "; the model's fitted electrical term",
                            src(rel, "patterns.%s.a_electrical" % kind), basis="idle_elec"))
            out.append(cell("fp32", kind, "pJ_per_flop", r(p["pj_per_flop_over_idle"], 4),
                            "pJ per flop (board, over idle)", cond,
                            src(rel, "patterns.%s.pj_per_flop_over_idle" % kind)))
            out.append(cell("fp32", kind, "pJ_per_MAC", r(p["pj_per_flop_over_idle"] * FLOPS_PER_MAC, 4),
                            "pJ per MAC (board, over idle)", cond + "; 1 MAC = 2 flops",
                            src(rel, "patterns.%s.pj_per_flop_over_idle * 2" % kind), basis="idle_raw"))
            out.append(cell("fp32", kind, "TFLOPS", r(p["tflops"], 3), "TFLOPS",
                            cond + "; fixed 600 MHz", src(rel, "patterns.%s.tflops" % kind)))
            out.append(cell("fp32", kind, "die_rise_C", r(p["rise_end"], 3), "C over the launch reading",
                            cond + "; end of a 7 s run", src(rel, "patterns.%s.rise_end" % kind)))
            out.append(cell("fp32", kind, "die_slope_C_per_s", r(p["slope"], 4), "C/s",
                            cond, src(rel, "patterns.%s.slope" % kind)))
            if "rails_late" in p:
                out.append(cell("fp32", kind, "minion_rail_W_abs", r(p["rails_late"]["minion"], 3),
                                "W (absolute, late in the run)", cond,
                                src(rel, "patterns.%s.rails_late.minion" % kind), basis="abs"))
            out.append(cell("fp32", kind, "clock_MHz_pinned", p["mhz"][0], "MHz",
                            cond + "; a fixed 600 MHz pin, so this is NOT a burst clock: the "
                            "governor never acts, and the data's watts never become speed here",
                            src(rel, "patterns.%s.mhz[0]" % kind)))
            rows.setdefault(("fp32", kind), set()).add("sept:" + card)
    return out, rows


def e15_cells():
    """E15 ablation (aifoundry2, 600 MHz, 80 C launch): the 14 structured matrices, measured."""
    d = jload(P_ABL15)
    zero_rail = d["configs"]["fp32_zeros"]["rails_late"]["minion"]
    out, rows = [], {}
    for cfg, c in d["configs"].items():
        if c.get("unit") != "MAC":
            continue
        fmt = "fp16" if cfg.startswith("fp16") else ("int8" if cfg.startswith("int8") else "fp32")
        kind = cfg if cfg.startswith("m_") else cfg.split("_", 1)[1]
        cond = ("aifoundry2, 600 MHz, %d minions, launch ~80 C, 7 s, over idle %.2f W, n=%d"
                % (c["minions"], c["idle"], c["n"]))
        out.append(cell(fmt, kind, "switching_W", r(c["dyn"], 3), "W",
                        cond + "; p80 (normalised to an 80 C die) minus the idle mean",
                        src(P_ABL15, "configs.%s.dyn" % cfg), basis="idle_lc",
                        interval=("sd %.3g over %d" % (c["p80_sd"], c["n"]))))
        out.append(cell(fmt, kind, "pJ_per_MAC", r(c["pj_per_unit_dyn"], 4),
                        "pJ per MAC (board, over idle)", cond,
                        src(P_ABL15, "configs.%s.pj_per_unit_dyn" % cfg), basis="idle_lc"))
        out.append(cell(fmt, kind, "minion_rail_W_over_zeros",
                        r(c["rails_late"]["minion"] - zero_rail, 3), "W",
                        cond + "; minion rail minus the fp32_zeros config's rail (%.3f W), NOT over idle"
                        % zero_rail,
                        src(P_ABL15, "configs.%s.rails_late.minion - configs.fp32_zeros.rails_late.minion" % cfg),
                        basis="zeros"))
        out.append(cell(fmt, kind, "die_rise_C", r(c["rise"], 3), "C over the launch reading", cond,
                        src(P_ABL15, "configs.%s.rise" % cfg)))
        rows.setdefault((fmt, kind), set()).add("e15:aifoundry2")
    return out, rows


def e14_cells():
    """E14: power predicted from RTL flip counts BEFORE the structured matrices ran."""
    d = jload(P_PRED14)
    out = []
    for kind, p in d["patterns"].items():
        out.append(cell("fp32", "m_" + kind, "switching_W", r(p["p_switching"], 3), "W",
                        "aifoundry2, 600 MHz, predicted from E13 RTL flip counts through E17's model, "
                        "written to disk at %s (the file's own made_at) - before any of these matrices "
                        "had run on the card, per the file's `note`. The measured figures this is "
                        "scored against are the claims-v3 abla runs of 26 Sep (earliest aifoundry2 "
                        "run t0 1790391404.347 = 2026-09-26T02:56:44 UTC), five days later. NO lead "
                        "time shorter than that is checkable from this repository: the same-afternoon "
                        "session's t0 values (validation_afternoon.json) are relative offsets into "
                        "session long2 with no absolute anchor committed" % d["made_at"],
                        src(P_PRED14, "patterns.%s.p_switching" % kind), status="predicted",
                        basis="idle_lc"))
        out.append(cell("fp32", "m_" + kind, "board_W", r(p["p_board_at_launch"], 3), "W",
                        "aifoundry2, 600 MHz, predicted board power at an 80 C launch",
                        src(P_PRED14, "patterns.%s.p_board_at_launch" % kind), status="predicted"))
    return out


def toggle_cells():
    """Q126(b) recount: nets_hier is the figure to quote (not `nets`)."""
    d = jload(P_RECOUNT)
    out = []
    for kind, v in d.items():
        m = v["mean"]
        out.append(cell("fp32", kind, "toggles_per_MAC", r(m["nets_hier"] / MACS_PER_OP, 5),
                        "physical-net toggles per multiply-add",
                        "RTL, rtl-sim/fma_toggle under Verilator 5.052 on the Intel, on E9's "
                        "card-dumped tiles; nets_hier = one count per net, a name merged with its "
                        "ancestor scope's; zero-delay, so no glitches; multiply-add units only",
                        src(P_RECOUNT, "%s.mean.nets_hier / %d" % (kind, MACS_PER_OP)),
                        status="modelled"))
        out.append(cell("fp32", kind, "toggles_per_MAC_published21sep",
                        r(m["nets"] / MACS_PER_OP, 5),
                        "net toggles per multiply-add (SUPERSEDED)",
                        "the 21 Sep `nets` count under Verilator 5.042; 8-16x too large "
                        "(simulator defect + hierarchy naming)",
                        src(P_RECOUNT, "%s.mean.nets / %d" % (kind, MACS_PER_OP)),
                        status="modelled"))
        out.append(cell("fp32", kind, "clocked_bits_per_MAC", r(m["ff_clocked"] / MACS_PER_OP, 5),
                        "register bits clocked with enable high, per multiply-add",
                        "RTL, as above", src(P_RECOUNT, "%s.mean.ff_clocked / %d" % (kind, MACS_PER_OP)),
                        status="modelled"))
    return out


def e64_cells():
    """E64 (aifoundry2, its own governor, 800 MHz nominal): clocks, speed, heat, the limit."""
    f = jload(P_E64_F)
    fit = f["fit"]
    s800 = fit["s"]["800"]
    out, rows = [], {}

    # --- the cool-die ladder and the minion sweep: burst clock, speed, power, the limit
    byl = {}
    for run in f["runs"]:
        byl.setdefault((run["type"], run["values"], run["minions"], run["block"]), []).append(run)

    for (typ, vals, minions, block), rs in sorted(byl.items()):
        kind = vals if minions == 1024 else "%s@%dmin" % (vals, minions)
        if block in ("LAD", "MIN"):
            cond = ("aifoundry2, own governor (TDP 65 W, threshold 65 C), cool die 50-56 C, "
                    "6 s launches, %d minions, n=%d runs" % (minions, len(rs)))
            p800, i800 = pm([x["p800_w"] for x in rs if x["p800_w"] is not None])
            mhz, imhz = pm([x["mhz_mean"] for x in rs])
            rate, irate = pm([x["rate_t"] for x in rs])
            cs = [fit["c"][x["run"]] for x in rs if x["run"] in fit["c"]]
            cmean, ci = pm(cs)
            out.append(cell(typ, kind, "board_W_at_800", r(p800, 3), "W (board, absolute)",
                            cond, src(P_E64_F, "runs[block=%s,%s-%s-%d].p800_w" % (block, typ, vals, minions)),
                            interval=i800, basis="abs"))
            out.append(cell(typ, kind, "switching_W", r(cmean * s800, 3), "W",
                            cond + ("; the data-dependent term c x s(800) from the governor model "
                                    "(c is W at 600 MHz and 0.517 V, s(800)=%.4f); the model's busy "
                                    "offset B(600)=%.2f W is within 1.2 W of the card's measured idle "
                                    "at 57 C (%.2f W), so c is also switching over idle at 600 MHz"
                                    % (s800, fit["B"]["600"], TYPED["e64_idle_board_W_SUS"]["value"])),
                            src(P_E64_F, "fit.c[<run>] x fit.s['800'] (mean of %d runs)" % len(cs)),
                            interval=("+-%.4g" % (float(ci[2:]) * s800) if ci else None),
                            status="modelled", basis="model"))
            out.append(cell(typ, kind, "switching_W_600", r(cmean, 3), "W",
                            cond + "; same model, at 600 MHz / 0.517 V",
                            src(P_E64_F, "fit.c[<run>] (mean of %d runs)" % len(cs)),
                            interval=ci, status="modelled", basis="model"))
            out.append(cell(typ, kind, "burst_MHz", r(mhz, 1), "MHz",
                            cond + "; mean over the whole 6 s run after the start ramp",
                            src(P_E64_F, "runs[...].mhz_mean"), interval=imhz))
            unit = "TOPS" if typ == "int8" else "TFLOPS"
            out.append(cell(typ, kind, "TOPS" if typ == "int8" else "TFLOPS", r(rate, 3), unit,
                            cond + "; whole run, kernel clock",
                            src(P_E64_F, "runs[...].rate_t"), interval=irate))
            macs = rate * 1e12 / FLOPS_PER_MAC
            out.append(cell(typ, kind, "pJ_per_MAC", r(cmean * s800 / macs * 1e12, 4),
                            "pJ per MAC (board, over idle)",
                            cond + "; switching_W / (rate x 1e12 / 2)",
                            src(P_E64_F, "fit.c x fit.s['800'] / (runs[...].rate_t x 1e12 / 2)"),
                            status="modelled", basis="model"))
            steps = sum(x["events"].get("power_down", 0) for x in rs)
            tsteps = sum(x["events"].get("thermal_down", 0) for x in rs)
            limit = "power" if steps else ("thermal" if tsteps else "none")
            out.append(cell(typ, kind, "limit", limit, "which governor test acts",
                            cond + ("; %d power_down and %d thermal_down steps over %d runs"
                                    % (steps, tsteps, len(rs))),
                            src(P_E64_F, "runs[...].events / .first_down_kind")))
            rows.setdefault((typ, kind), set()).add("e64:LAD")
        if block == "SUS":
            x = rs[0]
            cond = ("aifoundry2, own governor, ~80 s run, last 40 s, 1024 minions, "
                    "launch 57-58 C, n=1 run")
            if x["run"] in fit["c"]:
                c0 = fit["c"][x["run"]]
                out.append(cell(typ, kind, "switching_W", r(c0 * s800, 3), "W",
                                "aifoundry2, own governor, the SUS run's own fitted "
                                "data-dependent term c x s(800) (c = %.3f W at 600 MHz / 0.517 V, "
                                "s(800) = %.4f), referred to a 58 C die; n=1 run" % (c0, s800),
                                src(P_E64_F, "fit.c[%s] x fit.s['800']" % x["run"]),
                                status="modelled", basis="model"))
                out.append(cell(typ, kind, "switching_W_600", r(c0, 3), "W",
                                "as above, at 600 MHz / 0.517 V",
                                src(P_E64_F, "fit.c[%s]" % x["run"]),
                                status="modelled", basis="model"))
                macs0 = x["rate_t"] * 1e12 / FLOPS_PER_MAC
                out.append(cell(typ, kind, "pJ_per_MAC", r(c0 * s800 / macs0 * 1e12, 4),
                                "pJ per MAC (board, over idle)",
                                "aifoundry2, own governor, the SUS run's burst rate %.3f %s"
                                % (x["rate_t"], "TOPS" if typ == "int8" else "TFLOPS"),
                                src(P_E64_F, "fit.c[%s] x fit.s['800'] / (runs[%s].rate_t x 1e12 / 2)"
                                    % (x["run"], x["run"])),
                                status="modelled", basis="model"))
            out.append(cell(typ, kind, "sustained_MHz", r(x["sus_mhz_mean"], 1), "MHz", cond,
                            src(P_E64_F, "runs[%s].sus_mhz_mean" % x["run"])))
            unit = "TOPS" if typ == "int8" else "TFLOPS"
            out.append(cell(typ, kind, "TOPS_sustained" if typ == "int8" else "TFLOPS_sustained",
                            r(x["sus_rate_t"], 3), unit, cond + "; kernel clock",
                            src(P_E64_F, "runs[%s].sus_rate_t" % x["run"])))
            out.append(cell(typ, kind, "TOPS_sustained_wall" if typ == "int8" else "TFLOPS_sustained_wall",
                            r(x["sus_rate_wall_t"], 3), unit, cond + "; wall clock",
                            src(P_E64_F, "runs[%s].sus_rate_wall_t" % x["run"])))
            out.append(cell(typ, kind, "die_C_sustained", r(x["sus_die_mean"], 2), "C", cond,
                            src(P_E64_F, "runs[%s].sus_die_mean" % x["run"])))
            out.append(cell(typ, kind, "board_W_sustained", r(x["sus_w_mean"], 2), "W (absolute)", cond,
                            src(P_E64_F, "runs[%s].sus_w_mean" % x["run"])))
            out.append(cell(typ, kind, "burst_MHz_first8s", r(x["first8_mhz"], 1), "MHz",
                            "aifoundry2, the same run's first 8 s from a 57-58 C launch",
                            src(P_E64_F, "runs[%s].first8_mhz" % x["run"])))
            # the limit that acts in the sustained window
            bins = x["sus_bins"] or []
            tail = [b for b in bins if b["t_s"] >= (bins[-1]["t_s"] - 40)] if bins else []
            at800 = sum(1 for b in tail if b["mhz"] >= 795) / len(tail) if tail else None
            hot = sum(1 for b in tail if b["die"] >= 65.0) / len(tail) if tail else None
            if at800 is not None and at800 >= 0.9:
                limit = "none"
            elif hot and hot >= 0.6 and x["first_down_kind"] == "thermal_down":
                limit = "thermal"
            elif x["first_down_kind"] == "power_down":
                limit = "power"
            else:
                limit = "thermal" if (hot or 0) >= 0.5 else "unclassified"
            out.append(cell(typ, kind, "limit_sustained", limit, "which governor test acts",
                            cond + ("; %.0f%% of the last-40 s bins at >=795 MHz, %.0f%% at a die "
                                    ">=65 C, first step %s"
                                    % (100 * at800, 100 * (hot or 0), x["first_down_kind"])),
                            src(P_E64_F, "runs[%s].sus_bins / .first_down_kind" % x["run"])))
            rows.setdefault((typ, kind), set()).add("e64:SUS")

    # --- the hot-start block: the thermal test alone
    for run in f["runs"]:
        if run["block"] not in ("HOT", "HOT2"):
            continue
        out.append(cell(run["type"], run["values"], "burst_MHz_hotstart", r(run["mhz_mean"], 1), "MHz",
                        "aifoundry2, own governor, launched at a %d C die reading, 6 s, 1024 minions"
                        % run["die_start"],
                        src(P_E64_F, "runs[%s].mhz_mean" % run["run"])))

    # --- the modelled cap table: the clock each kind would hold at each power cap
    ct = jload(P_E64_F)["cap_table"]
    for row in ct["rows"]:
        for cap, mhz in row["mhz"].items():
            out.append(cell(row["type"], row["values"], "burst_MHz_at_cap_%sW" % cap, r(mhz, 1), "MHz",
                            "aifoundry2, cool die, E64's governor model on this kind's own measured "
                            "powers (c = %.2f W at 600 MHz); 65 W is the card's own cap, so that "
                            "column is the measured regime and the others are extrapolations "
                            "(E69 tested 12 of them: 12/12 in band, 11.50 MHz rms)" % row["c_w"],
                            src(P_E64_F, "cap_table.rows[%s-%s].mhz['%s']" % (row["type"], row["values"], cap)),
                            status="modelled"))
            out.append(cell(row["type"], row["values"], "TFLOPS_at_cap_%sW" % cap,
                            r(row["rate"][cap], 3), "TOPS" if row["type"] == "int8" else "TFLOPS",
                            "as above",
                            src(P_E64_F, "cap_table.rows[%s-%s].rate['%s']" % (row["type"], row["values"], cap)),
                            status="modelled"))
        for mhz_k, w in row["p_w"].items():
            out.append(cell(row["type"], row["values"], "board_W_at_%sMHz" % mhz_k, r(w, 2),
                            "W (board, absolute)",
                            "aifoundry2, cool die, %s" % row["p_src"][mhz_k],
                            src(P_E64_F, "cap_table.rows[%s-%s].p_w['%s']" % (row["type"], row["values"], mhz_k)),
                            status="measured" if row["p_src"][mhz_k] == "measured" else "modelled"))
    return out, rows


def e67_anchor_cells():
    """E67's card anchors on aifoundry3 at 600 MHz: board AND minion rail, full card."""
    d = jload(P_E67)
    a = d["cards"]["aifoundry3"]["anchors"]
    z = a["anchor_zeros"]
    out, rows = [], {}
    for item, kind in (("anchor_zeros", "zeros"), ("anchor_ones", "ones"),
                       ("anchor_pi", "pi"), ("anchor_randn", "randn")):
        v = a[item]
        macs = v["rate"] * MACS_PER_OP
        cond = ("aifoundry3, pinned 600 MHz by a boot-time TDP of 0, 521.9 mV, 1024 minions, "
                "launch 58 C, leakage-corrected p80, n=%d passes" % v["n"])
        out.append(cell("fp32", kind, "board_W_abs", r(v["p80"], 3), "W (board, absolute)", cond,
                        src(P_E67, "cards.aifoundry3.anchors.%s.p80" % item),
                        interval="+-%.4g" % v["se"], basis="abs"))
        out.append(cell("fp32", kind, "minion_rail_W_abs", r(v["rail"], 3), "W (rail, absolute)", cond,
                        src(P_E67, "cards.aifoundry3.anchors.%s.rail" % item), basis="abs"))
        if item != "anchor_zeros":
            out.append(cell("fp32", kind, "switching_W_over_zeros", r(v["p80"] - z["p80"], 3), "W",
                            cond + "; over the zeros anchor's board power (%.2f W), NOT over idle"
                            % z["p80"],
                            src(P_E67, "cards.aifoundry3.anchors.%s.p80 - .anchor_zeros.p80" % item),
                            basis="zeros"))
            out.append(cell("fp32", kind, "pJ_per_MAC_rail",
                            r((v["rail"] - z["rail"]) / macs * 1e12, 4),
                            "pJ per MAC (minion rail, over zeros)",
                            cond + "; rail minus the zeros anchor's rail (%.3f W)" % z["rail"],
                            src(P_E67, "(anchors.%s.rail - anchors.anchor_zeros.rail) / (.rate x %d)"
                                % (item, MACS_PER_OP)), basis="zeros"))
            out.append(cell("fp32", kind, "pJ_per_MAC_over_zeros",
                            r((v["p80"] - z["p80"]) / macs * 1e12, 4),
                            "pJ per MAC (board, over zeros)", cond,
                            src(P_E67, "(anchors.%s.p80 - anchors.anchor_zeros.p80) / (.rate x %d)"
                                % (item, MACS_PER_OP)), basis="zeros"))
        rows.setdefault(("fp32", kind), set()).add("e67:aifoundry3")
    # the one-sided random operands
    for item, kind in (("nrd_a", "a_randn_b_const"), ("nrd_b", "a_const_b_randn")):
        v = a[item]
        macs = v["rate"] * MACS_PER_OP
        out.append(cell("fp32", kind, "switching_W_over_constant", r(v["dW_vs_zero"], 3), "W",
                        "aifoundry3, 600 MHz, over its own constant-operand zero (%s); "
                        "%s A bits and %s B bits designed to flip per multiply-add"
                        % (v["zero"], v["A_bits_per_op"], v["B_bits_per_op"]),
                        src(P_E67, "cards.aifoundry3.anchors.%s.dW_vs_zero" % item),
                        interval="+-%.4g" % v["dW_se"], basis="const"))
        rows.setdefault(("fp32", kind), set()).add("e67:aifoundry3")
    return out, rows


# =========================================================== table 2: bit level
def bit_cells():
    out = []

    def bc(fmt, side, item, quantity, value, unit, conditions, source,
           status="measured", interval=None, typed=False):
        c = {"format": fmt, "side": side, "item": item, "quantity": quantity,
             "value": value, "interval": interval, "unit": unit,
             "conditions": conditions, "source": source, "status": status}
        if typed:
            c["typed"] = True
        out.append(c)

    # ---- E65: the B side, all 32 positions, quiet partner (A = 1.0)
    e65 = jload(P_E65)["cards"]["aifoundry3"]
    cond65 = ("aifoundry3, 600 MHz, 521.9 mV, A = 1.0, each position measured against the "
              "constant-operand zero lq_h0 (so it carries the turn-on, not a marginal slope); "
              "5 passes, 205 runs; E71 re-prices at the measured 0.3803 W/C idle slope")
    for pos in sorted(e65["bits"], key=int):
        v = e65["bits"][pos]
        bc("fp32", "B", "bit_%s" % pos, "fJ_per_flipped_bit",
           r(v["J_per_alternating_bit"] * 1e15, 2), "fJ per flipped bit", cond65,
           src(P_E65, "cards.aifoundry3.bits['%s'].J_per_alternating_bit" % pos),
           interval="+-%.3g W on dW" % v["se"])
        bc("fp32", "B", "bit_%s" % pos, "dW", r(v["dW"], 4), "W", cond65,
           src(P_E65, "cards.aifoundry3.bits['%s'].dW" % pos), interval="+-%.4g" % v["se"])
    for pos in sorted(e65["bits_pi"], key=int):
        v = e65["bits_pi"][pos]
        bc("fp32", "B", "bpi_%s" % pos, "fJ_per_flipped_bit",
           r(v["J_per_alternating_bit"] * 1e15, 2), "fJ per flipped bit",
           cond65.replace("A = 1.0", "A = pi (the busy partner)").replace("lq_h0", "lb_h0"),
           src(P_E65, "cards.aifoundry3.bits_pi['%s'].J_per_alternating_bit" % pos),
           interval="+-%.3g W on dW" % v["se"])
    t = TYPED["e65_flowM_fJ"]
    bc("fp32", "B", "bpi_11 (the flow-M case)", "fJ_per_flipped_bit", t["value"], t["unit"],
       "aifoundry3, 600 MHz, b bit 11 alternating against a = pi, board, all-in; the gate-level "
       "price of the same stimulus is 0.11-0.13 pJ in the multiplier, so the Booth rows, the tree "
       "and the product adder are about 23%% of what a flipped operand bit costs. %s" % t["note"],
       t["source"], interval=t["interval"], typed=True)

    # ---- E67: the A side, all 32 positions
    e67 = jload(P_E67)["cards"]["aifoundry3"]
    cond67 = ("aifoundry3, 600 MHz, 521.9 mV, B = 1.0, one shared A base word, against the "
              "shared-base constant-A zero; A[i][k] is held across both micro-ops of a pair, so "
              "2,048 designed A-bit flips per multiply-add against B's 4,096; 10 of 14 passes kept")
    for pos in sorted(e67["a_bits"], key=int):
        v = e67["a_bits"][pos]
        bc("fp32", "A", "abit_%s" % pos, "fJ_per_flipped_bit",
           r(v["e_fJ"], 2), "fJ per flipped bit", cond67,
           src(P_E67, "cards.aifoundry3.a_bits['%s'].e_fJ" % pos),
           interval="+-%.3g W on dW" % v["se"])
        bc("fp32", "A", "abit_%s" % pos, "dW", r(v["dW"], 4), "W", cond67,
           src(P_E67, "cards.aifoundry3.a_bits['%s'].dW" % pos), interval="+-%.4g" % v["se"])
    for pos in sorted(e67["a_bits_pi"], key=int):
        v = e67["a_bits_pi"][pos]
        bc("fp32", "A", "abp_%s" % pos, "fJ_per_flipped_bit", r(v["e_fJ"], 2),
           "fJ per flipped bit", cond67.replace("B = 1.0", "B = pi (the busy partner)"),
           src(P_E67, "cards.aifoundry3.a_bits_pi['%s'].e_fJ" % pos),
           interval="+-%.3g W on dW" % v["se"])

    # ---- E60: the ladder slopes on three cards, and the orders
    e60 = jload(P_E60)["cards"]
    for card, c in sorted(e60.items()):
        for arm, label in (("lq", "quiet partner A = 1.0"), ("lb", "busy partner A = pi")):
            dz = c[arm]["designed"]
            if dz.get("J") is None:
                continue
            bc("fp32", "B", "%s ladder slope" % arm, "fJ_per_flipped_bit",
               r(dz["J"] * 1e15, 2), "fJ per flipped bit",
               "%s, %d MHz, %.4f V, %s, h >= 1, %d passes; per designed flipped B mantissa bit, "
               "cascade included" % (card, c["clock_mhz"], c["v_mean"], label, dz["n_passes"]),
               src(P_E60, "cards.%s.%s.designed.J" % (card, arm)),
               interval="+-%.3g fJ" % (dz["se_J"] * 1e15))
            if dz.get("rail_J"):
                bc("fp32", "B", "%s ladder slope" % arm, "fJ_per_flipped_bit_rail",
                   r(dz["rail_J"] * 1e15, 2), "fJ per flipped bit (minion rail)",
                   "as above, on the minion rail",
                   src(P_E60, "cards.%s.%s.designed.rail_J" % (card, arm)),
                   interval="+-%.3g fJ" % (dz["rail_se_J"] * 1e15))
        for arm, label in (("lq", "A = 1.0"), ("lb", "A = pi")):
            ff = c[arm].get("first_flip_W") or {}
            item0 = (c.get("items") or {}).get(arm + "_h1") or {}
            if not ff.get("W"):
                continue
            # the ladder's own per-h slope in watts: J per designed bit x 4,096 designed bits
            # per h-step per op x the op rate
            rate = item0.get("rate")
            ratio = None
            if rate and c[arm]["designed"].get("J"):
                ratio = ff["W"] / (c[arm]["designed"]["J"] * 4096 * rate)
            bc("fp32", "B", "the first flip (%s)" % label, "dW", r(ff["W"], 4), "W",
               "%s, %d MHz: the step from NO flipping bit to one, against the ladder's own "
               "per-h slope%s. Turning the data on at all costs more than the next bit does: "
               "the price list is a local slope, not a per-bit tariff."
               % (card, c["clock_mhz"],
                  (" = %.2fx" % ratio) if ratio else ""),
               src(P_E60, "cards.%s.%s.first_flip_W.W" % (card, arm)),
               interval="+-%.4g" % ff["se"])
        for grp, orders in sorted((c.get("ord") or {}).items()):
            for name, v in sorted(orders.items()):
                bc("fp32", "both", "order %s (bits %s..), over Gray" % (name, grp), "dW",
                   r(v["W"], 4), "W",
                   "%s, %d MHz: the SAME 4,096 multiply-adds presented in %s order instead of Gray; "
                   "%d extra A-side bit flips per op; %d passes"
                   % (card, c["clock_mhz"], name, v["extra_A_bits_per_op"], v["n"]),
                   src(P_E60, "cards.%s.ord['%s'].%s.W" % (card, grp, name)),
                   interval="+-%.4g" % v["se"])
                bc("fp32", "both", "order %s (bits %s..), over Gray" % (name, grp),
                   "fJ_per_extra_flipped_bit", r(v["J_per_extra_A_bit"] * 1e15, 2),
                   "fJ per extra flipped bit", "as above",
                   src(P_E60, "cards.%s.ord['%s'].%s.J_per_extra_A_bit" % (card, grp, name)))
        for g, v in sorted((c.get("ec") or {}).items()):
            if v.get("J_per_bit") is None:
                continue
            bc("int (vector)", "read port / result", g, "fJ_per_flipped_bit",
               r(v["J_per_bit"] * 1e15, 2), "fJ per flipped bit",
               "%s, %d MHz: one-gate-deep vector integer op (%s), %d passes"
               % (card, c["clock_mhz"], g, v["n_passes"]),
               src(P_E60, "cards.%s.ec.%s.J_per_bit" % (card, g)),
               interval="+-%.3g fJ" % (v["se_J"] * 1e15))

    # ---- E72: the same card at both clocks
    e72 = jload(P_E72)
    m = e72["measured"]
    bc("fp32", "B", "lq h2->h8 secant", "fJ_per_flipped_bit",
       r(m["lq_h2_h8_secant_fJ_items"], 2), "fJ per flipped bit",
       "aifoundry2, 600 MHz (pinned by TDP 0), %.4f V, %d passes; the same card reads "
       "121.27 +- 0.61 fJ at 800 MHz, so the board price is 10-15%% BELOW a pure V^2 "
       "extrapolation at matched leakage slopes; the exponent n in (V600/V800)^n is bracketed "
       "1.60-2.92, and the clock-scaling rival n = 3.637 is excluded everywhere at >= 3.4 SE"
       % (e72["v_mean"], len(e72["passes"])),
       src(P_E72, "measured.lq_h2_h8_secant_fJ_items"),
       interval="+-%.3g" % m["lq_h2_h8_secant_fJ_se"])
    bc("fp32", "B", "lq h2->h8 secant", "fJ_per_flipped_bit_rail",
       r(m["lq_h2_h8_secant_rail_fJ_items"], 2), "fJ per flipped bit (minion rail)",
       "as above; 'the rail is slope-free' is WITHDRAWN - the rail is merely uncorrected",
       src(P_E72, "measured.lq_h2_h8_secant_rail_fJ_items"),
       interval="+-%.3g" % m["lq_h2_h8_secant_rail_fJ_se"])

    # ---- E68: the stage map (which pipeline stage spends it)
    e68 = jload(P_E68)
    for item, v in e68["items"].items():
        bc("fp32", "B", item, "fJ_per_flipped_bit", r(v["fJ_per_flipped_bit"], 1),
           "fJ per flipped bit",
           "aifoundry2, 800 MHz, 512 minions (so the ~65 W cap never acts), %d passes, "
           "%d mask bits; priced at the REGISTERED 1.508 W/C leakage slope, which is 4-5x every "
           "measured idle slope - the README publishes each price at 1.508 and at E66's measured "
           "0.296 W/C and the second is the better footing"
           % (v["passes"], v["mask_bits"]),
           src(P_E68, "items.%s.fJ_per_flipped_bit" % item),
           interval="+-%.3g" % v["se_fJ"])
    t = TYPED["e68_lo12_fJ_band"]
    bc("fp32", "B", "sm_lo12 (12 low mantissa bits)", "fJ_per_flipped_bit_band", t["value"], t["unit"],
       t["note"], t["source"], typed=True)
    t = TYPED["e68_s_mul"]
    bc("fp32", "B", "s_mul (the multiplier's share)", "fraction_of_in_unit_cost", t["value"], t["unit"],
       "aifoundry2, 800 MHz: between about a third and two thirds of a 12-bit mantissa flip's "
       "IN-UNIT cost is the multiplier, against the gate level's 15-17%% of a BOARD flip. %s"
       % t["note"], t["source"], interval=t["interval"], typed=True)
    bc("fp32", "B", "sm_sgn (a sign flip, zero tree toggles)", "dW",
       r(e68["items"]["sm_sgn"]["dP_W"], 4), "W",
       "aifoundry2, 800 MHz: a flipped bit that never enters the multiplier - the RTL shows "
       "EXACTLY 0 toggles in every tree-only module - still costs 0.127 of a 12-bit mantissa "
       "flip for one twelfth the bits (P3 PASS, 4.9 SE above zero)",
       src(P_E68, "items.sm_sgn.dP_W"), interval="+-%.3g" % e68["items"]["sm_sgn"]["se_W"])

    # ---- E70: the saturation law, the layouts, the carry-over
    s70 = jload(P_E70S)
    d2 = s70["D2"]
    bc("fp32", "B", "the saturating law dW = Winf(1 - e^(-S/Winf))", "residual_rms_W",
       r(d2["R_S_refit_W"], 4), "W over 15 rungs",
       "aifoundry3, 600 MHz, 6 of 7 passes: one saturating curve in the ADDITIVE SUM of the "
       "constituent single-bit prices leaves %.3f W rms over 8 lq + 7 ls rungs (dW 0.61-9.75 W), "
       "against %.3f W for the best possible law in Hamming weight alone and %.3f W for pure "
       "additivity. Frozen at E60's own Winf (12.58 W) it leaves %.3f W and predicts the "
       "out-of-sample top rung to +0.072 W (0.5 SE) where the refit misses by +1.851 W (11.7 SE)."
       % (d2["R_S_refit_W"], d2["R_h_W"], d2["R_additive_W"], d2["R_S_frozen_W"]),
       src(P_E70S, "D2.R_S_refit_W / .R_h_W / .R_additive_W / .R_S_frozen_W"))
    for rung in s70["D1"]:
        if rung["h"] == 8:
            bc("fp32", "B", "spread minus low layout at h = 8", "dW",
               r(rung["dW_ls_minus_lq"], 4), "W",
               "aifoundry3, 600 MHz, %d passes: the SAME Hamming weight, 8 bits spread over the "
               "23 mantissa positions instead of the low 8 - %.1f SE from the zero a law in 'how "
               "many bits flip' requires. It is the wires, not the count."
               % (rung["n_passes"], rung["sigma_from_zero"]),
               src(P_E70S, "D1[h=8].dW_ls_minus_lq"), interval="+-%.4g" % rung["se"])
    co = s70["carry_over_measured"]
    bc("fp32", "A over B", "carry-over rho at matched h", "ratio",
       r(co["rho_h12"], 4), "A price per flipped bit over B's",
       "aifoundry3, 600 MHz, h = 12 (near a random fp32 word's 13.9 average Hamming distance); "
       "the window mean over h = 12 and 16 is %.3f with a BETWEEN-h spread of %.3f (not an SE). "
       "E71's measured slope re-prices rho(12) to 1.246 +- 0.014. This replaces the 1.57 / 1.01 "
       "choice Q128 had to make." % (co["rho_mean_12_16"], co["between_h_SD_12_16"]),
       src(P_E70S, "carry_over_measured.rho_h12"), interval="+-%.4g" % co["rho_h12_se"])
    for arm, label in (("lq", "B, low layout"), ("ls", "B, spread layout"), ("alq", "A, low layout")):
        for rung in s70[arm]:
            bc("fp32", "A" if arm == "alq" else "B", "%s (h = %d)" % (rung["item"], rung["h"]),
               "fJ_per_flipped_bit", r(rung["fJ_per_bit"], 1), "fJ per flipped bit",
               "aifoundry3, 600 MHz, %d passes, %s: %d designed bit flips per multiply-add; "
               "measured/additive %.3f. These fJ divide BOARD watts by a per-operand-tile bit "
               "count and a per-minion rate - a within-experiment currency, not the gate-level ledger."
               % (rung["n_passes"], label, rung["designed_bits_per_op"],
                  rung["ratio_measured_over_additive"]),
               src(P_E70S, "%s[item=%s].fJ_per_bit" % (arm, rung["item"])),
               interval="+-%.4g W on dW" % rung["se"])
    ac = s70["A_ceiling"]
    bc("fp32", "A", "the A side's saturating form", "fit_rms_W", r(ac["fit_rms_W"], 4), "W",
       "aifoundry3, 600 MHz: REJECTED. 4.6x the B side's rms, systematic residuals to 84 SE, and "
       "increments that ACCELERATE (+0.38, +1.53, +2.23 W at k = 8, 12, 16) where saturation "
       "requires decay. What the A side's real shape is, E70 does not answer.",
       src(P_E70S, "A_ceiling.fit_rms_W"), status="measured")

    # ---- E67: the interaction grid, sub-additivity
    ix = jload(P_E67)["cards"]["aifoundry3"]["ix"]
    bc("fp32", "A x B", "the 4x4 interaction grid", "excess_over_sum_of_margins_W",
       r(ix["excess_mean_W"], 4), "W",
       "aifoundry3, 600 MHz: all %d cells are SUB-additive, mean excess %.3f W (%.1f SE), largest "
       "%.2f W; a cell costs 62-96%% of its two margins' sum, median 83%%. Summing the per-position "
       "prices over a random operand's own flip histogram over-predicts by 2.3x (A) and 2.0x (B), "
       "so the per-bit price list is an UPPER BOUND on a random workload, high by about 2x. The two "
       "operand PATHS do add (0.88 of the sum); what fails is decomposing one operand into bits."
       % (ix["n_cells"], ix["excess_mean_W"], ix["excess_mean_W"] / ix["excess_mean_se"],
          -ix["excess_abs_max_W"]),
       src(P_E67, "cards.aifoundry3.ix.excess_mean_W"), interval="+-%.4g" % ix["excess_mean_se"])

    # ---- E61: one gate, carry, register-file cell, the zero gate
    e61 = jload(P_E61)["cards"]["aifoundry3"]["derived"]
    for key, label, note in (
        ("e_in_fxor", "a read-port bit into fxor.pi",
         "the cross-campaign tie to E60's 20.83 +- 0.10 fJ"),
        ("e_in_fand_d2A", "a read-port bit into fand.pi", "an AND costs more per port bit than an XOR"),
        ("e_out_fand_BA", "a result bit out of fand.pi", "e_out > e_in, as predicted"),
        ("e_carry", "one carry position", "REGISTERED form; 3.48 +- 0.74 fJ with the changed-word "
                                         "term removed, against the proposing page's 14.2 fJ"),
        ("e_cell", "one register-file cell bit", "under-resolved here; E74 bounds it < 2.73 fJ at 95%"),
        ("e_addr", "one register-INDEX bit (gated regime)",
         "12-14x the proposing page's 32 fJ, with no linear law across the matched rungs"),
    ):
        v = e61.get(key)
        if not v or v.get("value") is None:
            continue
        bc("int (vector)", "one gate deep", label, "fJ_per_flipped_bit",
           r(v["value"] * 1e15, 3), "fJ per flipped bit",
           "aifoundry3, 600 MHz, E61 registered reduction (%s). %s"
           % (v.get("identified_by", "")[:140], note),
           src(P_E61, "cards.aifoundry3.derived.%s.value" % key),
           interval="+-%.3g fJ" % (v["se"] * 1e15))
    zg = e61["zero_gate_step"]
    bc("fp32", "the zero gate", "fmadd.ps zero-gate step", "dW", r(zg["value"], 4), "W",
       "aifoundry3, 600 MHz: the vector fmadd.ps has NO zero gate - %.3f +- %.3f W, i.e. "
       "0.23 +- 0.16 pJ/op, against the 8.94 pJ a zero gate would save. Zero gating in the "
       "TENSOR unit is real and worth %.2f +- %.2f W of lane un-gating (the zeros->random "
       "split); the vector unit's is not there."
       % (zg["value"], zg["se"], UNG, UNG_SE),
       src(P_E61, "cards.aifoundry3.derived.zero_gate_step.value"), interval="+-%.4g" % zg["se"])

    # ---- E74: the register file's own cells
    rf = jload(P_E74)
    bc("fp32", "register file", "one flipped cell bit", "fJ_per_flipped_bit",
       r(rf["e_cell_fJ"]["mean"], 4), "fJ per flipped bit (board)",
       "aifoundry3, 600 MHz, 5 kept passes: NOT RESOLVED on the board - the 95%% t interval "
       "[%.2f, %.2f] contains zero, so the result is a BOUND, e_cell < %.2f fJ at 95%%. Per "
       "multiply-add that is 0.055 pJ at the point and at most 0.175 pJ (64 bits of register "
       "content, the registered basis): 1.4%% of Q128's 3.837 pJ remainder, at most 4.6%%. The "
       "cells CANNOT be the explanation."
       % (rf["e_cell_fJ"]["lo"], rf["e_cell_fJ"]["hi"], rf["rule5_resolution"]["bound_95pct_fJ"]),
       src(P_E74, "rf.json: e_cell_fJ.mean / .lo / .hi"),
       interval="95%% [%.2f, %.2f]" % (rf["e_cell_fJ"]["lo"], rf["e_cell_fJ"]["hi"]))
    bc("fp32", "register file", "one flipped cell bit", "fJ_per_flipped_bit_rail",
       r(rf["e_cell_rail_fJ"]["mean"], 4), "fJ per flipped bit (minion rail)",
       "aifoundry3, 600 MHz: the ONLY arm that excludes zero, 95%% [%.3f, %.3f], four times "
       "tighter on the same runs"
       % (rf["e_cell_rail_fJ"]["lo"], rf["e_cell_rail_fJ"]["hi"]),
       src(P_E74, "rf.json: e_cell_rail_fJ.mean"),
       interval="95%% [%.3f, %.3f]" % (rf["e_cell_rail_fJ"]["lo"], rf["e_cell_rail_fJ"]["hi"]))

    # ---- E75: the memory path, changed bits against carried ones
    mf = jload(P_E75)
    for lv in ("l1", "l2", "l3", "dram"):
        L = mf["levels"][lv]
        ef = L.get("e_flip_pJ_per_bit")
        if isinstance(ef, dict):
            val, lo, hi = ef.get("mean"), ef.get("lo"), ef.get("hi")
        else:
            val, lo, hi = ef, None, None
        bc("memory", lv.upper(), "one CHANGED bit", "pJ_per_changed_bit", r(val, 5),
           "pJ per changed bit",
           "aifoundry3, 600 MHz, 4 kept passes, %s. k-arm monotone in every pass: %s. "
           "L1 and L2 are coefficients; L3 and DRAM are NOT RESOLVED (non-monotone k-arms) and "
           "must be quoted as bounds, < 0.37 pJ and < 0.42 pJ at 95%%."
           % (L["unit"], L["k_arm_monotone"]),
           src(P_E75, "levels.%s.e_flip_pJ_per_bit" % lv),
           interval=("95%% [%s, %s]" % (r(lo, 5), r(hi, 5)) if lo is not None else None),
           status="measured" if L["k_arm_monotone"] else "missing")
        eo = L.get("e_one_pJ_per_bit")
        if isinstance(eo, dict):
            oval, olo, ohi = eo.get("mean"), eo.get("lo"), eo.get("hi")
        else:
            oval, olo, ohi = eo, None, None
        if oval is not None:
            bc("memory", lv.upper(), "one CARRIED one", "pJ_per_carried_one", r(oval, 5),
               "pJ per carried one",
               "aifoundry3, 600 MHz, %s. Of the 1,008 pJ per 64 B DRAM line the two designed "
               "counts explain, 94%% is the ONES term (946 pJ) and 62 pJ the unresolved "
               "changed-bit term - so off-chip, packing zeros is the big lever and reducing "
               "transitions the small one. Bit-counting explains 98.3%% of L1's zeros-to-random "
               "chord and only 36.6%% of DRAM's." % L["unit"],
               src(P_E75, "levels.%s.e_one_pJ_per_bit" % lv),
               interval=("95%% [%s, %s]" % (r(olo, 5), r(ohi, 5)) if olo is not None else None))
    return out


# =============================================================== the mechanisms
# two-sided 95% t, df 1..30, for re-reading a published interval at 95%
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
        9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042}


def t95(df):
    ks = sorted(_T95)
    if df <= ks[0]:
        return _T95[ks[0]]
    if df >= ks[-1]:
        return _T95[ks[-1]]
    lo = max(k for k in ks if k <= df)
    hi = min(k for k in ks if k >= df)
    if lo == hi:
        return _T95[lo]
    return _T95[lo] + (df - lo) * (_T95[hi] - _T95[lo]) / (hi - lo)


def abl_t1():
    """ABL-T1 (-0.0 against +0.0 and against all-ones) as its own file scores it.

    The published intervals are Bonferroni family-wise (alpha = 0.01/19 = 0.000526), NOT
    95%, and the item's outcome is CARD-DIFFERENT, not a pass. Both are reported here,
    with each published interval re-read at 95% from its own point, se and df.
    """
    d = jload(P_ABLA_S)
    item = [x for x in d if x.get("item") == "ABL-T1"][0]
    out = []
    for card, c in item["per_card"].items():
        s = [x for x in c["subtests"] if "ones" in x["test"]][0]
        ci = s["ci"]
        h = t95(ci["df"]) * ci["se"]
        out.append({
            "card": card, "card_outcome": c["outcome"], "subtest": s["test"],
            "point_W": r(ci["point"], 4), "se_W": r(ci["se"], 4), "df": r(ci["df"], 3),
            "published_interval_W": [r(ci["lo"], 3), r(ci["hi"], 3)],
            "published_alpha": ci["alpha"],
            "interval_95_W": [r(ci["point"] - h, 3), r(ci["point"] + h, 3)],
            "subtest_ok": s.get("ok"),
        })
    by = {x["card"]: x for x in out}
    a2, a3, a1 = by["aifoundry2"], by["aifoundry3"], by["aifoundry1-c1"]
    reading = (
        "the registered outcome is %s (a2 PASS, a3 FAIL, a1c1 FAIL). The equivalence subtest "
        "'%s' holds on aifoundry2 only: %+.2f W, published interval [%+.2f, %+.2f] at the "
        "family-wise alpha %s - NOT 95%%; re-read at 95%% it is [%+.2f, %+.2f]. It FAILS on "
        "aifoundry3 (%+.2f W, [%+.2f, %+.2f]) and aifoundry1-c1 (%+.2f W, [%+.2f, %+.2f]) on "
        "interval WIDTH, not on sign: every point estimate is within 0.15 W of zero and all three "
        "95%% intervals lie inside the +-1 W band."
        % (item["outcome"], a2["subtest"], a2["point_W"], a2["published_interval_W"][0],
           a2["published_interval_W"][1], a2["published_alpha"], a2["interval_95_W"][0],
           a2["interval_95_W"][1], a3["point_W"], a3["published_interval_W"][0],
           a3["published_interval_W"][1], a1["point_W"], a1["published_interval_W"][0],
           a1["published_interval_W"][1]))
    return {
        "item": "ABL-T1", "registered_outcome": item["outcome"],
        "test_as_registered": item["test"], "per_card": out, "reading": reading,
        "source": src(P_ABLA_S, "[item=ABL-T1].per_card.*.subtests"
                                "[negzero - ones within +-1 W].ci"),
    }


def mechanisms():
    e70s = jload(P_E70S)
    t1 = abl_t1()
    return [
        {
            "mechanism": "zero gating (the tensor unit)",
            "what_it_does": "an all-zero operand word turns the lane's work off, so the die never "
                            "sees the switching at all",
            "size": "%.2f +- %.2f W of the zeros->random step at 600 MHz on aifoundry3, with "
                    "%.2f +- %.2f W of operand flips on top (%.2f +- %.2f W in all); all three "
                    "levels are p80, referred to the same 58 C launch, so no leakage term survives "
                    "the difference"
                    % (UNG, UNG_SE, FLIPS, SPLIT["operand_flips_W"]["se"],
                       STEP, SPLIT["step_W"]["se"]),
            "status": "measured", "source": SPLIT["source"],
            "notes": "the chip gates the all-zero BIT PATTERN only, so -0.0 is not gated: it costs "
                     "+8.36 W over +0.0 (ABL-T1 subtest 1, PASS on all three cards) and is "
                     "indistinguishable from all-ones. The equivalence to all-ones is ONE CARD's "
                     "registered pass: " + t1["reading"] + " The VECTOR fmadd.ps has no zero gate "
                     "at all (E61, 0.087 +- 0.060 W).",
        },
        {
            "mechanism": "order (which number follows which)",
            "what_it_does": "the SAME arithmetic costs more when consecutive operands differ in "
                            "more bits, because the flips, not the values, are what is paid for",
            "size": "max-flip minus Gray on the same 4,096 multiply-adds: +0.682 +- 0.010 W at "
                    "600 MHz / 0.5218 V (aifoundry3, bits 0-3) and +1.291 +- 0.009 W at "
                    "800 MHz / 0.6174 V (aifoundry2); the four orders rank by their flipped bits, "
                    "and binary is indistinguishable from Gray at bits 0-3",
            "status": "measured",
            "source": src(P_E60, "cards.aifoundry3.ord['0'].maxflip.W, cards.aifoundry2.ord['0'].maxflip.W"),
            "notes": "this is the cleanest single demonstration for a blog reader: identical "
                     "results, identical count of operations, different energy. THE 1.9x BETWEEN "
                     "THE TWO IS THE OPERATING POINT, NOT THE CARD: 0.6825 x s(800) = 1.90517 "
                     "gives 1.300 W against aifoundry2's measured 1.291 W, so referred to one "
                     "clock the two cards agree. Quote the clock and voltage with each figure.",
        },
        {
            "mechanism": "shared wires (saturation)",
            "what_it_does": "two flips that travel the same wires do not cost twice one flip, so a "
                            "word's price is a saturating function of the additive sum of its bits' prices",
            "size": "one curve dW = Winf(1 - e^(-S/Winf)) fits 15 B-side rungs to %.3f W rms "
                    "against %.3f W for any law in Hamming weight alone and %.3f W for pure "
                    "additivity; summing per-bit prices over a random word over-predicts by about 2x"
                    % (e70s["D2"]["R_S_refit_W"], e70s["D2"]["R_h_W"], e70s["D2"]["R_additive_W"]),
            "status": "measured", "source": src(P_E70S, "D2"),
            "notes": "WHICH bits flip beats HOW MANY: 8 spread mantissa bits cost +3.860 +- 0.052 W "
                     "more than the low 8 at the same Hamming weight (73.9 SE). Winf is the "
                     "curve's CURVATURE, not a ceiling - correction C1 withdrew the ceiling reading.",
        },
        {
            "mechanism": "position inside the word",
            "what_it_does": "a high mantissa bit drives a wider slice of the multiplier tree than a "
                            "low one, so the same single flip costs 12x more at bit 22 than at bit 6",
            "size": "B side 83 fJ (bit 6) to 1,008 fJ (bit 22), span 12.2x; A side 153 fJ (bit 4) "
                    "to 1,440 fJ (bit 22), span 9.4x; exponent bits average 174 (B) / 265 (A) fJ "
                    "and the sign bit 123 / 247 fJ",
            "status": "measured",
            "source": src(P_E65, "cards.aifoundry3.bits") + "; " + src(P_E67, "cards.aifoundry3.a_bits"),
            "notes": "the mantissa is TWO regimes: bits 0-9 flat at ~109 fJ, then a monotone climb "
                     "from bit 10. 'The exponent is dearer than the low mantissa' holds only below "
                     "bit 10 (E65 A3 and E67 P3 both FAIL on that clause).",
        },
        {
            "mechanism": "the busy partner",
            "what_it_does": "a flipped bit costs more when the OTHER operand is a busy number, "
                            "because the partial products it selects are themselves wide",
            "size": "A = pi over A = 1.0 is 1.59-4.73x at the five shared B positions (5 of 5 at "
                    ">= 2 SE); B = pi over B = 1.0 reaches 1,566 fJ at A bit 22. On the ladder "
                    "SLOPE the effect is only +11% (116.7 -> 129.9 fJ)",
            "status": "measured",
            "source": src(P_E65, "cards.aifoundry3.bits_pi") + "; " + src(P_E67, "cards.aifoundry3.a_bits_pi"),
            "notes": "the two operands' flow-M prices agree within 30% (B 745, A 856 fJ), and the "
                     "two operand PATHS add (0.88 of the sum) even though bits within one operand "
                     "do not.",
        },
        {
            "mechanism": "voltage, not clock",
            "what_it_does": "a flip's price follows the rail voltage the governor picks, not the "
                            "clock it picks with it",
            "size": "the same card reads 79.18 +- 3.09 fJ at 600 MHz / 0.5179 V and 121.27 +- 0.61 "
                    "fJ at 800 MHz / 0.6174 V; the board price is 10-15% below a pure V^2 "
                    "extrapolation, the exponent is bracketed 1.60-2.92, and the clock-scaling "
                    "rival n = 3.637 is excluded at >= 3.4 SE in every reduction",
            "status": "measured", "source": src(P_E72, "measured / rules.V1"),
            "notes": "quote E72 as 'the price follows the voltage, not the clock', never as 'the "
                     "exponent is 2'.",
        },
        {
            "mechanism": "carried ones, off chip",
            "what_it_does": "on the DRAM path what costs is the NUMBER OF ONES in flight, not the "
                            "number of bits that changed",
            "size": "3.255 pJ per carried one at DRAM [2.97, 3.55] against nothing measurable at "
                    "L1 (-0.0001 pJ); 94% of the 1,008 pJ per 64 B line the two counts explain is "
                    "the ones term",
            "status": "measured", "source": src(P_E75, "levels.dram.e_one_pJ_per_bit"),
            "notes": "so off chip, PACKING ZEROS is the big lever and reducing transitions the "
                     "small one - the opposite of the arithmetic path. DRAM's changed-bit arm is "
                     "unresolved (non-monotone in every pass): quote a bound.",
        },
        {
            "mechanism": "the governor (power test, then thermal test)",
            "what_it_does": "the watts the data causes are turned into SPEED by the firmware, which "
                            "regulates a ~1.3 s average of board power to the TDP and the die "
                            "reading to the threshold",
            "size": "on a cool die the power test alone acts, so zeros run 12.1 against random "
                    "fp32's 10.6 TFLOPS over a 6 s burst (zeros +14%, random -12%); in 80 s runs "
                    "the thermal test wins, because this card's cooling puts the die at 65 C at "
                    "about 50 W, and zeros run 12.278 against 9.209 TFLOPS - zeros +33.3%, random "
                    "-25.0%. STATE THE DIRECTION: the two percentages are the same gap read from "
                    "the two ends, and 'random is 33% slower' is wrong",
            "status": "measured", "source": src(P_E64_F, "runs / governor / thermal"),
            "notes": "the model is a first-order average, tau 1.3 s, compared once per 0.24 s pass, "
                     "one step up or down, 3.3 MHz rms over 26 cool-die runs; the thermal line is "
                     "die = 41.88 + 0.4696 C per board W. E69 moved the cap for the first time and "
                     "12 of 12 extrapolated cap-table cells held. WHICH CLOCK a switching figure "
                     "belongs to decides whether it explains a governor run: random int8's "
                     "switching term at the governor's own 800 MHz footing is 17.34 W "
                     "(fit.c[SUS-08] 9.101 x s(800) 1.90517) against random fp32's 49.27 W "
                     "(fit.c[SUS-02] 25.862 x s(800)), which is why int8 settles at a 65.3 C die "
                     "holding 763 MHz while fp32 randn is pinned to the 600 MHz floor at 67.1 C. "
                     "The 9.885 W figure for int8 randn is a PINNED 600 MHz measurement "
                     "(claims-v3 abla) and must not be used to explain an 800 MHz governor run.",
        },
    ]


# ==================================================================== the holes
def holes():
    return [
        {"id": "H1", "lane": "E78 (aifoundry3, 600 MHz pinned)", "priority": 1,
         "hole": "fp16 and int8 have only zeros, ones and randn. Every other kind - sparse, signs, "
                 "pow2, mant, constants, negative zero, the structured matrices - is fp32 only.",
         "cells_missing": "2 formats x 11+ kinds x {switching_W, pJ_per_MAC} = 44+ cells of table 1",
         "why_it_matters": "the blog's claim is about the KIND of number, and two of the three "
                           "formats a reader would actually use are a three-point line.",
         "how": "`sparsity_host --test fma --type fp16|int8 --values file:<tiles>` takes raw A then B "
                "tiles, 1,024 bytes each, in the chosen type's layout (host `fillValues`), so any "
                "kind in any format needs only a tile file.",
         "evidence": "claims-v3 abla has fp16/int8 for zeros, ones, randn only; E64's LAD ladder is "
                     "fp32 only; hub Status 'what's missing now' item 9."},
        {"id": "H2", "lane": "E79 (aifoundry3, 600 MHz pinned)", "priority": 2,
         "hole": "there is NO per-bit price list for fp16 or int8. Table 2 is entirely fp32 "
                 "(plus the vector integer one-gate ops).",
         "cells_missing": "2 formats x 2 sides x 16 or 8 bit positions, and both ladders",
         "why_it_matters": "fp16's PRM pseudo-code has a 2-term update only when all four of a1, a2, "
                           "b1, b2 are nonzero, so fp16 may have a zero-gating rule fp32 does not - "
                           "untested. int8's 318 cycles per op against fp32's 546 changes the "
                           "per-op denominator as well.",
         "how": "E60/E65's Hamming ladders by bit position, with the operand files written in the "
                "fp16 and int8 layouts.",
         "evidence": "E65 and E67 are fp32 B and A sides; hub Levels stop 5 'fp16 and int8 price lists'."},
        {"id": "H3", "lane": "E80 (aifoundry2, its own governor)", "priority": 3,
         "hole": "burst and sustained clock, TFLOPS/TOPS and sustained die temperature exist for "
                 "only 9 of E64's 16 (format, kind) pairs: the SUS block ran 3 kinds x 3 formats. "
                 "The seven fp32 ladder kinds (sparse75, signs, pow2, mant, uniform, "
                 "a_randn_b_ones, a_ones_b_randn) have a cool-die burst clock and NO sustained cell.",
         "cells_missing": "7 fp32 kinds x {sustained_MHz, TFLOPS_sustained, die_C_sustained, "
                          "limit_sustained}, plus every new fp16/int8 kind",
         "why_it_matters": "the blog's headline distinction is burst (power test) against sustained "
                           "(thermal test), and the second is where the big gap lives: sustained "
                           "fp32 zeros are 33.3% faster than randn (randn 25.0% slower), against "
                           "+14.2% / -12.4% on a 6 s cool-die burst.",
         "how": "E64's SUS block (~80 s runs, last 40 s) on the ladder kinds; no governor move.",
         "evidence": src(P_E64_F, "runs[block=SUS] has 9 rows against LAD's 10 kinds")},
        {"id": "H4", "lane": "E80", "priority": 4,
         "hole": "the fp16 all-ones sustained cell is the one sustained cell that NO (gamma, trip) "
                 "pairing closes: measured 737.1 MHz against 744.9-758.4 MHz over Q129's six "
                 "pairings, a +7.8 to +21.3 MHz miss (E64's own cap predicts 780.6, +43.5). n = 1 run.",
         "cells_missing": "1 cell, with a replicate",
         "why_it_matters": "it is an all-ONES cell - exactly the 'predictable data' case the blog is "
                           "about - and the only sustained cell where every candidate governor "
                           "surface is wrong in the same direction.",
         "how": "repeat the fp16 ones SUS run; E64 ran it once (n = 1). E80's REGISTERED PREDICTION "
                "for this cell is 744.9-758.4 MHz, which is the fp16 row of Q129's trip surface. "
                "The 775 MHz figure (chain.py) belongs to the fp32 all-ones cell (measured 737.9), "
                "whose miss Q129 narrows from +37 to +18.5...-7.8 MHz; it closes only at the warm "
                "end of gamma, and gamma and the thermal trip are jointly unidentified. Do not "
                "carry 775 into an fp16 registration: the two cells both measure ~738 MHz, which "
                "is how they were welded together.",
         "evidence": "docs/reports/data/2026-10-27-q129-governor-temperature/README.md lines 80-81 "
                     "(the trip surface's fp32 and fp16 rows) and 97, 103 (the two misses); hub "
                     "Status item 9 and Levels stop 1."},
        {"id": "H5", "lane": "E78 (rail arm) / E77 (reserved, NOT this workflow)", "priority": 5,
         "hole": "energy per op AT THE MINION RAIL exists for four fp32 kinds on aifoundry3 "
                 "(E67's anchors, over zeros) and as absolute rail power for the September "
                 "patterns and the E15 structured matrices on aifoundry2. There is no rail figure "
                 "over IDLE for any kind, and none at all for fp16 or int8.",
         "cells_missing": "the whole pJ_per_MAC_rail column for fp16, int8 and 20+ fp32 kinds",
         "why_it_matters": "the board carries the regulators' delivery loss (0.875 pJ of a 5.783 pJ "
                           "multiply-add), so a reader asking 'what does the CHIP pay' needs the rail.",
         "how": "every ladder run already samples the rail (runs.csv column `rail`); the gap is that "
                "no experiment has recorded an IDLE rail beside it at the same temperature. E77, "
                "which needs a governor move, is the registered fix and is out of scope today.",
         "evidence": src(P_E67, "cards.aifoundry3.anchors.*.rail (absolute, no idle rail recorded)")},
        {"id": "H6", "lane": "desk (Q130 later lanes)", "priority": 6,
         "hole": "toggles per multiply-add exist for the 14 September fp32 patterns and the 17 "
                 "structured matrices, under `nets_hier`. There is no toggle count for ANY fp16 or "
                 "int8 operand kind, and none for the E64 ladder's kinds as such.",
         "cells_missing": "the toggles_per_MAC column for fp16 and int8",
         "why_it_matters": "the RTL count is the bridge from the card to the gate-level ledger, and "
                           "the blog's bottom third rests on it.",
         "how": "rtl-sim/fma_toggle under Verilator 5.052 on the Intel; the fp16 and int8 micro-op "
                "streams need the PRM 9.4 order written for those types.",
         "evidence": src(P_RECOUNT, "14 fp32 patterns only")},
        {"id": "H7", "lane": "E70 follow-up (no number yet)", "priority": 7,
         "hole": "the A side's saturating form is REJECTED and nothing replaces it: the fitted "
                 "asymptote lies 28 SE below the A side's own top rung and the increments accelerate "
                 "where saturation requires decay.",
         "cells_missing": "the law itself; every summed A-side prediction inherits the gap",
         "why_it_matters": "the B-side law is what lets the per-bit list be used at all; without "
                           "the A-side one, a two-sided prediction has no footing.",
         "how": "more A-side rungs between k = 16 and 23, and a layout contrast (alq against als) "
                "that the B side has and the A side does not.",
         "evidence": src(P_E70S, "A_ceiling.fit_rms_W = 1.063 W against the B side's 0.232")},
        {"id": "H8", "lane": "E81 (reserved, aifoundry3, if time allows)", "priority": 8,
         "hole": "the DRAM pattern question: a third image at the same changed-bit and carried-one "
                 "counts but a longer period, to test whether a two-value alternating image is "
                 "compressible on the link or in DRAM in a way random data is not.",
         "cells_missing": "DRAM's changed-bit coefficient (now a bound, < 0.42 pJ, non-monotone in "
                          "every pass) and the 63.4% of its chord that bit-counting does not explain",
         "why_it_matters": "a DRAM tensor load costs 94-134 pJ per byte against a multiply-add's "
                           "5.8 pJ, so the memory path dominates a real workload's energy.",
         "how": "E75's ladder with a third image; the scratchpad rung stays out of scope (no host "
                "fill reaches the scratchpad address).",
         "evidence": src(P_E75, "levels.dram.k_arm_monotone = false")},
        {"id": "H9", "lane": "E74 follow-up / E77", "priority": 9,
         "hole": "the register file's READ PORTS, its read mux tree and its clocking. E74 bounds the "
                 "cell BIT (< 2.73 fJ at 95%), not the array, and in the zeros stimulus those cells "
                 "never flip while the transport model still charges 0.654 pJ a multiply-add - where "
                 "the WHOLE BOARD costs 0.27.",
         "cells_missing": "the one row the card's own measurement contradicts",
         "why_it_matters": "it is the hub's number-one missing item, and it means the published "
                           "bottom-up closure (68.6-72.4% of the board) sits below the bottom of "
                           "every range quoted.",
         "how": "about 40 passes (~80 card-minutes) on the board arm, or a re-registration with the "
                "RAIL as the estimator and the board as the check.",
         "evidence": src(P_E74, "rule5_resolution") + "; hub Status item 1"},
        {"id": "H10", "lane": "desk", "priority": 10,
         "hole": "no kind has been measured on more than one card at one clock AND one temperature. "
                 "a3 launches 23 C cooler than a2 in the September campaign, E64 is a2 only at "
                 "800 MHz, and the bit ladders are a3 at 600 MHz. Card and temperature move together "
                 "almost everywhere (E40 could not separate them).",
         "cells_missing": "a card column for every table-1 row at matched temperature",
         "why_it_matters": "the blog will quote one number per cell; without this, each carries an "
                           "unquantified 3-5% card term on top of its own interval.",
         "how": "desk work: re-reduce the existing campaigns onto one launch temperature with each "
                "card's own measured idle slope (E66 for a2, E71 for a3), which E71's "
                "leak_sensitivity.py already does for the a3 ladders.",
         "evidence": "E38 caveat (post-data note C2); E40; E71 'a leakage slope is not a card constant'"},
    ]


# =========================================== how many rows, and how many KINDS
def row_taxonomy(cells, rows):
    """One set of denominators, computed, so no two sentences can disagree.

    Four different counts were being quoted as one in the first cut of this file:
      - rows in the cell list                55 (fp32 46, fp16 4, int8 5)
      - rows with at least one RUN-sourced   52 (fp32 43, fp16 4, int8 5)  = len(rows)
        cell (what `row_coverage` holds)
      - rows with at least one MEASURED cell 52 - the 3 prediction-only matrices
      - distinct KINDS OF NUMBER measured    42 (fp32 36, fp16 3, int8 3), after folding
        the configuration variants in VARIANT_OF into their base kind
    The coverage claim a blog may quote is the LAST one.
    """
    def byfmt(keys):
        c = {"total": len(keys)}
        for f in ("fp32", "fp16", "int8"):
            c[f] = sum(1 for k in keys if k[0] == f)
        return c

    all_rows, measured, status_of = {}, set(), {}
    for c in cells:
        k = (c["format"], c["kind"])
        all_rows.setdefault(k, set()).add(c["status"])
        if c["status"] == "measured":
            measured.add(k)
    for k, v in all_rows.items():
        status_of[k] = sorted(v)

    def q_rows(quantity, only_measured=False):
        out = set()
        for c in cells:
            if c["quantity"] != quantity:
                continue
            if only_measured and c["status"] != "measured":
                continue
            out.add((c["format"], c["kind"]))
        return out

    pred_only = sorted(k for k, v in all_rows.items() if v == {"predicted"})
    kinds = {(f, VARIANT_OF.get((f, k), (k, None))[0]) for f, k in measured}
    variants = sorted(k for k in all_rows if k in VARIANT_OF)
    sw_any, sw_meas = q_rows("switching_W"), q_rows("switching_W", True)
    pj_any, pj_meas = q_rows("pJ_per_MAC"), q_rows("pJ_per_MAC", True)
    return {
        "one_sentence": (
            "%d (format, kind) rows have at least one run-sourced cell (fp32 %d, fp16 %d, int8 %d); "
            "%d more fp32 matrices are prediction-only, so the cell list holds %d rows. Folding the "
            "%d configuration variants (minion count, TenB streaming) into their base kind leaves "
            "%d distinct KINDS OF NUMBER with a measured cell: fp32 %d, fp16 %d, int8 %d."
            % (byfmt(rows)["total"], byfmt(rows)["fp32"], byfmt(rows)["fp16"], byfmt(rows)["int8"],
               len(pred_only), byfmt(all_rows)["total"], len(variants),
               byfmt(kinds)["total"], byfmt(kinds)["fp32"], byfmt(kinds)["fp16"], byfmt(kinds)["int8"])),
        "rows_in_cell_list": byfmt(all_rows),
        "rows_run_sourced": byfmt(rows),
        "rows_with_a_measured_cell": byfmt(measured),
        "rows_prediction_only": ["%s/%s" % k for k in pred_only],
        "distinct_kinds_of_number_measured": byfmt(kinds),
        "kinds_of_number_measured": sorted("%s/%s" % k for k in kinds),
        "configuration_variant_rows": {
            "%s/%s" % k: {"base_kind": VARIANT_OF[k][0], "variant_is": VARIANT_OF[k][1]}
            for k in variants},
        "rows_with_switching_W": {"any_status": byfmt(sw_any), "measured": byfmt(sw_meas),
                                  "never_measured": sorted("%s/%s" % k for k in (sw_any - sw_meas))},
        "rows_with_pJ_per_MAC": {"any_status": byfmt(pj_any), "measured": byfmt(pj_meas)},
        "row_status": {"%s/%s" % k: v for k, v in sorted(status_of.items())},
    }


# ================================================== the markdown the README uses
# The blog's table is quoted at ONE clock per column group, because a clock change
# is a voltage change and a price may not be scaled across it (see `normalisation`).
BLOG_ROWS = [
    ("fp32", "zeros"), ("fp32", "sparse75"), ("fp32", "sparse50"), ("fp32", "checker"),
    ("fp32", "ternary"), ("fp32", "ones"), ("fp32", "pi"), ("fp32", "m_negzero"),
    ("fp32", "signs"), ("fp32", "pow2"), ("fp32", "a_randn_b_ones"), ("fp32", "a_ones_b_randn"),
    ("fp32", "mant"), ("fp32", "uniform"), ("fp32", "randn"),
    ("fp16", "zeros"), ("fp16", "ones"), ("fp16", "randn"),
    ("int8", "zeros"), ("int8", "ones"), ("int8", "randn"),
    ("fp32", "m_identity"), ("fp32", "m_permutation"), ("fp32", "m_diagonal"),
    ("fp32", "m_tridiagonal"), ("fp32", "m_block_diag"), ("fp32", "m_upper"),
    ("fp32", "m_butterfly"), ("fp32", "m_hadamard"), ("fp32", "m_fft_cos"),
    ("fp32", "m_dct"), ("fp32", "m_kaleidoscope"), ("fp32", "m_circulant"),
    ("fp32", "m_lowrank"), ("fp32", "m_quant4"), ("fp32", "m_relu"),
]


def pick(cells, fmt, kind, quantity, must=(), mustnot=()):
    """the one cell for this row/column, preferring `measured` and the named conditions."""
    cands = [c for c in cells if c["format"] == fmt and c["kind"] == kind
             and c["quantity"] == quantity
             and all(m in (c["conditions"] + c["source"]) for m in must)
             and not any(m in (c["conditions"] + c["source"]) for m in mustnot)]
    if not cands:
        return None
    order = {"measured": 0, "modelled": 1, "predicted": 2, "missing": 3}
    border = {"idle_lc": 0, "model": 1, "idle_elec": 2, "idle_raw": 3, "const": 4,
              "zeros": 5, "abs": 6, "none": 0}
    cands.sort(key=lambda c: (order.get(c["status"], 9), border.get(c.get("basis", "none"), 9)))
    return cands[0]


def fmtcell(c, nd=3):
    if c is None:
        return "—"
    v = c["value"]
    s = ("%.*g" % (nd + 2, v)) if isinstance(v, float) else str(v)
    if c["interval"] and c["interval"].startswith("+-"):
        s += " " + c["interval"].replace("+-", "±")
    if c["status"] == "modelled":
        s += " ᵐ"
    elif c["status"] == "predicted":
        s += " ᵖ"
    mark = {"idle_raw": " ˢ", "zeros": " ᶻ", "const": " ᶜ", "abs": " ᵃ"}
    s += mark.get(c.get("basis"), "")
    return s


def write_tables(inv, out):
    cells, bits = inv["operand_kind_cells"], inv["bit_level_cells"]
    L = []
    L.append("<!-- generated by build_inventory.py; do not hand-edit -->")
    L.append("")
    L.append("## Table 1 — every operand kind any experiment measured")
    L.append("")
    L.append("ᵐ modelled, ᵖ predicted, — missing. Baseline marks: no mark = over the "
             "pre-launch idle, leakage-normalised to a fixed launch temperature; ˢ = over the "
             "pre-launch idle but NOT leakage-corrected (the September strict runs: on fp32 randn "
             "+8.6%% on switching W and **+12.0%% on pJ per MAC** against the leakage-normalised "
             "claims-v3 figures in the same columns); ᶻ = over a RUNNING kernel on zero data "
             "(the %.2f ± %.2f W of lane un-gating is NOT in it); ᶜ = over a constant NON-zero "
             "operand; ᵃ = absolute. A clock is never crossed by scaling (see §Units)."
             % (UNG, UNG_SE))
    L.append("")
    L.append("Row counts, one set of denominators (`inventory.json` > `row_taxonomy`): "
             + inv["row_taxonomy"]["one_sentence"])
    L.append("")
    L.append("### 1A · aifoundry2 and aifoundry3 at 600 MHz (no governor action: a fixed pin)")
    L.append("")
    L.append("| format | kind | a2 switching W | a2 pJ/MAC board | a3 switching W | "
             "a3 pJ/MAC board | a3 pJ/MAC rail | TFLOPS·TOPS | toggles/MAC (nets_hier) | die rise °C |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for fmt, kind in BLOG_ROWS:
        a2w = pick(cells, fmt, kind, "switching_W", must=("aifoundry2", "600 MHz"))
        a2p = pick(cells, fmt, kind, "pJ_per_MAC", must=("aifoundry2", "600 MHz"))
        a3w = pick(cells, fmt, kind, "switching_W", must=("aifoundry3", "600 MHz"))
        a3p = pick(cells, fmt, kind, "pJ_per_MAC", must=("aifoundry3", "600 MHz"))
        a3r = pick(cells, fmt, kind, "pJ_per_MAC_rail")
        tf = pick(cells, fmt, kind, "TFLOPS", must=("600 MHz",))
        tg = pick(cells, fmt, kind, "toggles_per_MAC")
        dr = pick(cells, fmt, kind, "die_rise_C")
        if not any((a2w, a3w, a2p, tg)):
            continue
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                 % (fmt, kind, fmtcell(a2w), fmtcell(a2p), fmtcell(a3w), fmtcell(a3p),
                    fmtcell(a3r), fmtcell(tf), fmtcell(tg), fmtcell(dr)))
    L.append("")
    L.append("### 1B · aifoundry2 under its own governor, 800 MHz nominal (E64): speed, heat, the limit")
    L.append("")
    L.append("| format | kind | switching W (800 MHz) | pJ/MAC board | burst MHz | TFLOPS·TOPS burst | "
             "limit (burst) | sustained MHz | TFLOPS·TOPS sustained | die °C sustained | limit (sustained) | "
             "modelled MHz at a 65 W cap |")
    L.append("|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---:|")
    for fmt, kind in BLOG_ROWS:
        sw = pick(cells, fmt, kind, "switching_W", must=("own governor",))
        pj = pick(cells, fmt, kind, "pJ_per_MAC", must=("own governor",))
        bm = pick(cells, fmt, kind, "burst_MHz", must=("own governor",))
        tb = pick(cells, fmt, kind, "TOPS" if fmt == "int8" else "TFLOPS", must=("own governor",))
        lb = pick(cells, fmt, kind, "limit")
        sm = pick(cells, fmt, kind, "sustained_MHz")
        ts = pick(cells, fmt, kind, "TOPS_sustained" if fmt == "int8" else "TFLOPS_sustained")
        dc = pick(cells, fmt, kind, "die_C_sustained")
        ls = pick(cells, fmt, kind, "limit_sustained")
        cap = pick(cells, fmt, kind, "burst_MHz_at_cap_65W")
        if not any((sw, bm, cap)):
            continue
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |"
                 % (fmt, kind, fmtcell(sw), fmtcell(pj), fmtcell(bm), fmtcell(tb),
                    fmtcell(lb), fmtcell(sm), fmtcell(ts), fmtcell(dc), fmtcell(ls), fmtcell(cap)))
    L.append("")
    L.append("### 1C · coverage: which quantity exists for which row")
    L.append("")
    L.append("**Every row of the cell list is here** — the blog rows first, then the "
             "configuration variants (ᵛ, the same operand stream at another minion count or with "
             "TenB streaming: they are rows, not kinds) and the prediction-only matrices. The "
             "first cut of this table showed only the 36 blog rows with no note that it was "
             "partial.")
    L.append("")
    quants = ["switching_W", "pJ_per_MAC", "pJ_per_MAC_rail", "burst_MHz", "sustained_MHz",
              "TFLOPS", "die_C_sustained", "limit", "toggles_per_MAC"]
    L.append("| format | kind | " + " | ".join(q.replace("_", " ") for q in quants) + " |")
    L.append("|---|---|" + "---|" * len(quants))
    legend = {"measured": "M", "modelled": "m", "predicted": "p", "missing": "·"}
    ordered, seen = [], set()
    present = [(c["format"], c["kind"]) for c in cells]
    for k in BLOG_ROWS:
        if k in present and k not in seen:
            ordered.append(k)
            seen.add(k)
    for k in present:                       # first-appearance order for everything else
        if k not in seen:
            ordered.append(k)
            seen.add(k)
    other_only = []
    for fmt, kind in ordered:
        marks = []
        for q in quants:
            c = pick(cells, fmt, kind, q)
            marks.append(legend.get(c["status"], "?") if c else "·")
        name = kind
        if (fmt, kind) in VARIANT_OF:
            name += " ᵛ(= %s)" % VARIANT_OF[(fmt, kind)][0]
        if set(marks) == {"·"}:
            name += " ᵒ"
            other_only.append((fmt, kind))
        L.append("| %s | %s | %s |" % (fmt, name, " | ".join(marks)))
    L.append("")
    L.append("M = measured, m = modelled, p = predicted, · = missing. "
             "ᵛ = a configuration variant of the named kind, folded into it by the kind counts. "
             "%d rows, which is every row in `operand_kind_cells`." % len(ordered))
    if other_only:
        L.append("")
        bits_of = []
        for fmt, kind in other_only:
            qs = sorted({c["quantity"] for c in cells
                         if c["format"] == fmt and c["kind"] == kind})
            bits_of.append("`%s/%s` (%s)" % (fmt, kind, ", ".join(qs)))
        L.append("ᵒ carries no cell in any of the nine columns above, only: " + "; ".join(bits_of)
                 + ". Nothing is hidden: these rows are in the table so the denominators match.")
    L.append("")
    L.append("## Table 2 — the bit level")
    L.append("")
    L.append("### 2A · per-position prices, fp32, both operand sides (aifoundry3, 600 MHz, 521.9 mV)")
    L.append("")
    L.append("| bit | B side, quiet A = 1.0 (fJ) | B side, busy A = π (fJ) | A side, quiet B = 1.0 (fJ) | "
             "A side, busy B = π (fJ) |")
    L.append("|---|---:|---:|---:|---:|")
    byitem = {}
    for c in bits:
        byitem[(c["side"], c["item"], c["quantity"])] = c
    for pos in range(32):
        row = [
            byitem.get(("B", "bit_%d" % pos, "fJ_per_flipped_bit")),
            byitem.get(("B", "bpi_%d" % pos, "fJ_per_flipped_bit")),
            byitem.get(("A", "abit_%d" % pos, "fJ_per_flipped_bit")),
            byitem.get(("A", "abp_%d" % pos, "fJ_per_flipped_bit")),
        ]
        if not any(row):
            continue
        lab = ("mantissa %d" % pos) if pos <= 22 else ("exponent %d" % pos) if pos <= 30 else "sign 31"
        L.append("| %d (%s) | %s | %s | %s | %s |"
                 % (pos, lab,
                    ("%.0f" % row[0]["value"]) if row[0] else "—",
                    ("%.0f" % row[1]["value"]) if row[1] else "—",
                    ("%.0f" % row[2]["value"]) if row[2] else "—",
                    ("%.0f" % row[3]["value"]) if row[3] else "—"))
    L.append("")
    L.append("### 2B · ladder slopes, the orders, the one-gate and memory prices")
    L.append("")
    L.append("ᵗ = typed into build_inventory.py from a committed README (no machine-readable "
             "form), with its citation in `inventory.json` > `typed_numbers`.")
    L.append("")
    L.append("| format · side | item | quantity | value | interval | card · clock |")
    L.append("|---|---|---|---:|---|---|")
    skip = {"fJ_per_flipped_bit", "dW"}
    for c in bits:
        if c["item"].startswith(("bit_", "bpi_", "abit_", "abp_")):
            continue
        cond = c["conditions"]
        m = re.search(r"\b(aifoundry[0-9](?:-c[01])?|memory|L1|L2|L3|DRAM)\b", cond)
        where = m.group(1) if m else cond.split(",")[0][:24]
        m2 = re.search(r"\b([0-9]{3})\s*MHz", cond)
        if m2:
            where += " · " + m2.group(1) + " MHz"
        val = ("%.5g" % c["value"]) if isinstance(c["value"], float) else c["value"]
        if c["status"] == "missing":
            val = "%s — NOT RESOLVED, quote a bound" % val
        elif c["status"] == "modelled":
            val += " ᵐ"
        if c.get("typed"):
            val += " ᵗ"
        L.append("| %s · %s | %s | %s | %s | %s | %s |"
                 % (c["format"], c["side"], c["item"], c["quantity"], val,
                    (c["interval"] or "").replace("+-", "±") or "—", where))
    L.append("")
    L.append("## Table 3 — the mechanisms")
    L.append("")
    L.append("| mechanism | what it does | how big | status |")
    L.append("|---|---|---|---|")
    for m in inv["mechanisms"]:
        L.append("| **%s** | %s | %s | %s |"
                 % (m["mechanism"], m["what_it_does"], m["size"], m["status"]))
    L.append("")
    path = os.path.join(out, "tables.md")
    with open(path, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("wrote %s" % path)


# ========================================================================= main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()

    cells, rows = [], {}
    for fn in (abla_cells, ablb_cells, sept_cells, e15_cells, e64_cells, e67_anchor_cells):
        c, rw = fn()
        cells += c
        for k, v in rw.items():
            rows.setdefault(k, set()).update(v)
    cells += e14_cells()
    cells += toggle_cells()

    bits = bit_cells()

    inv = {
        "meta": {
            "lane": "Q130(a)",
            "title": "The kinds-of-numbers inventory: what is already measured",
            "date": "2026-10-31",
            "built_by": "docs/reports/data/2026-10-31-q130-kinds-inventory/build_inventory.py",
            "scope": "desk only; no card was touched; every number is read from a committed file "
                     "or typed from a committed README with its citation",
            "repo_head_note": "run `git log -1` for the head this was built at",
            "corrected": "2026-10-31, after adversarial verification of the first cut (commit "
                         "7d9b73c5): one set of row denominators in row_taxonomy (kinds of number, "
                         "not configurations), the format-dependent MACs per TensorFMA, ABL-T1 at "
                         "its own alpha with its two FAILs, the zeros->random split computed with "
                         "an interval instead of typed, the fp16 all-ones target separated from "
                         "fp32's, the September offset per quantity, E71's band label, and the "
                         "scope of the measured-slope rule. See README 'What the verification "
                         "changed'.",
        },
        "normalisation": {
            "mac_vs_flop": "1 multiply-add = 2 flops, so in EVERY format MAC/s = TFLOPS or TOPS "
                           "x 1e12 / 2. MACs per 16x16x16 TensorFMA are FORMAT-DEPENDENT: "
                           "fp32 %d, fp16 %d, int8 %d (tools/claims-v3/hpl/surface_hpl.py:32 gives "
                           "flops per op 8192 / 16384 / 32768). So MAC/s = ops/s x 4,096 holds for "
                           "fp32 ONLY: applied to fp16 it reports pJ per MAC 2x too high and to "
                           "int8 4x too high. The claims-v3 `per_s` field is already MAC/s (its "
                           "`unit` reads MAC) and needs no conversion: at one 600 MHz pin it reads "
                           "4.591e12 for fp32, 9.184e12 for fp16 (exactly 2x at the same 546 cycles "
                           "per op) and 3.153e13 for int8 (318 cycles)."
                           % (MACS_PER_OP_BY_FMT["fp32"], MACS_PER_OP_BY_FMT["fp16"],
                              MACS_PER_OP_BY_FMT["int8"]),
            "cycles_per_op": "fp32 546, fp16 546, int8 318 (tools/claims-v3/hpl/surface_hpl.py; "
                             "measured identical on three cards to 0.0002 cycle, claims-v3 ABLB-2a). "
                             "int8 is therefore 6.9x fp32's MAC rate at the same clock "
                             "(546/318 x 16384/4096 = 6.87), not 1.7x (the cycle ratio alone) and "
                             "not 4x (the MACs-per-op ratio alone).",
            "clock_600_vs_800": "NEVER scale a price by the clock ratio. E72 ran ONE card at both: "
                                "79.18 +- 3.09 fJ at 600 MHz / 0.5179 V against 121.27 +- 0.61 fJ at "
                                "800 MHz / 0.6174 V - the price follows the VOLTAGE, 10-15% below a "
                                "pure V^2 extrapolation, exponent bracketed 1.60-2.92, and the "
                                "clock-scaling rival n = 3.637 excluded at >= 3.4 SE. E64's own "
                                "governor model uses (V/0.517)^2 x f/600, i.e. s(700) = 1.408 and "
                                "s(800) = 1.905 over s(600) = 1.0; cells marked `modelled` that "
                                "cross clocks use exactly that factor and say so.",
            "card_to_card": "at the SAME die temperature aifoundry3 switches 0.958-0.969 of "
                            "aifoundry2 over the Horace patterns (E38's post-data note C2; E46's "
                            "independent catalogue 0.972), and a2's 600 MHz per-bit price is 0.970 "
                            "of a3's (E72). A cross-card quote carries about 3%. aifoundry1 card 1 "
                            "idled at 50.15 W against a2's 36.34 and a3's 25.78 in September and "
                            "borrows a2's leakage slope.",
            "baseline": "THREE different zeros are in play and they are not interchangeable. "
                        "(a) OVER IDLE: claims-v3 `switching` (board minus pre-launch idle minus "
                        "leakage x the rise since launch), the September p_early - p_before, and "
                        "E64's model term c. (b) OVER ZEROS: E67's anchors differenced against "
                        "anchor_zeros, and the E15 rail column - these subtract a RUNNING kernel on "
                        "zero data, so they omit the %.2f W of lane un-gating. (c) OVER A CONSTANT "
                        "OPERAND: every bit price in table 2 (lq_h0, aq_h0, lb_h0) - a constant "
                        "NON-zero operand, so the lane is un-gated and only the flips are missing. "
                        "(b) and (c) differ by that %.2f +- %.2f W; (a) and (c) differ by the whole "
                        "zeros level. Each cell's `conditions` names its own baseline."
                        % (UNG, UNG, UNG_SE),
            "leakage_slope": "a leakage slope is NOT a card constant (E71): it rises about 0.009 "
                             "W/C per C on aifoundry2 and 0.011 on aifoundry3 over 51-65 C. "
                             "Measured idle slopes: a2 0.2936 over 51-58 C (E66) and 0.3452 +- "
                             "0.0056 over 58-62; a3 0.3200 +- 0.0038 over 51-58 (E71's own band "
                             "label; its floor is 52-53 C, so that fit spans 5-6 degrees, not 7) "
                             "and 0.3803 +- 0.0036 over 58-62. THE SCOPE OF THIS RULE: it governs "
                             "the a3 bit ladders, which launch at 58 C inside the measured bands, "
                             "and E71's leak_sensitivity.py re-prices exactly those. It does NOT "
                             "reach the claims-v3 / September cells that carry table 1A's spine: "
                             "those launch at 80.9 C (a2) and 55.8 C (a3) on the campaign's own "
                             "FITTED BUSY-DIE slopes, 0.81 and 0.55 W/C, which are 2.1-2.8x every "
                             "measured idle slope and sit at a die temperature no measured band "
                             "covers (the bands stop at 66 C). No re-reduction of the 80.9 C "
                             "campaign onto a measured slope exists - that is this inventory's "
                             "own hole H10, and until it is done every 1A cell carries that "
                             "footing, not a measured-idle one. E68's registered estimator used 1.508 "
                             "W/C, which is 4-5x every measured idle slope and is a busy transient, "
                             "not leakage - its prices are published at both footings and the "
                             "measured one is the better. Re-pricing the a3 ladders at E71's slope "
                             "moves prices a few per cent and systematically (E65's flat mantissa "
                             "floor 109 -> ~103 fJ, bit 22 1008 -> 986, the flow-M flip "
                             "745 +- 56 -> 722 +- 61 fJ) and moves none of the 16 registered verdicts.",
            "launch_temperature": "September a2 and a1c1 launched at 80.9 C and a3 at 55.8 C; E64 "
                                  "launched at 50-57 C; the bit ladders at 58 C. Switching power "
                                  "itself drifts with die temperature at +22.0 +- 36.1 mW/C "
                                  "(E65 D1, re-read as +32.4 +- 39.6 at E71's slope) - consistent "
                                  "with zero and UNDECIDED, so it is not corrected for anywhere; it "
                                  "is a stated uncertainty of about +-1%/10 C.",
            "toggles": "quote `nets_hier`, not `nets` (Q126(b)). The 21 Sep figure of 21,331 net "
                       "toggles per random fp32 multiply-add reproduces only under the Verilator it "
                       "was measured with (5.042, a coverage-counter defect in two compressor "
                       "modules) and was never a count of wires; the figure to quote is about 1,301 "
                       "per multiply-add, 8-16x smaller.",
            "rail_vs_board": "the minion rail carries 4.774 pJ [4.549-4.951] of the board's 5.783 pJ "
                             "per random fp32 multiply-add, ratio 0.825 [0.787-0.856] (Q129). The "
                             "1.009 pJ between them is mostly the regulators' delivery loss "
                             "(0.875 pJ), which is a named account, not a bottom-up row.",
            "september_basis": "the September strict cells are marked `basis: idle_raw` and ˢ in "
                               "tables.md: p_early - p_before, NOT leakage-corrected. QUOTE THE "
                               "OFFSET PER QUANTITY, because it is not one number: on fp32 randn "
                               "(a2, 600 MHz) switching_W reads +8.6% high (29.52 against 27.18 W) "
                               "and pJ per MAC +12.0% (6.630 against 5.920), the extra 3.1% being "
                               "the denominator - the September pJ column implies 8.905 TFLOPS "
                               "where the same record's `tflops` field reads 9.183. Table 1A puts "
                               "September sparse75 (1.0966 pJ/MAC ˢ) in the same column as the "
                               "claims-v3 figures, so a reader comparing them across that mark is "
                               "comparing bases that differ by about a tenth, not by 8%.",
            "counting_kinds": "a configuration variant is not a kind of number. Seven fp32 rows are "
                              "the same randn operand at a different minion count and three are TenB "
                              "streaming arms; `row_taxonomy` folds them into their base kind with "
                              "VARIANT_OF, and each such cell carries `variant_of` and `variant_is`. "
                              "Quote `row_taxonomy.one_sentence` and nothing else for coverage.",
        },
        "zeros_random_split": SPLIT,
        "registered_items": {"ABL-T1": abl_t1()},
        "row_taxonomy": row_taxonomy(cells, rows),
        "typed_numbers": TYPED,
        "row_coverage": {"%s/%s" % k: sorted(v) for k, v in sorted(rows.items())},
        "operand_kind_cells": cells,
        "bit_level_cells": bits,
        "mechanisms": mechanisms(),
        "holes": holes(),
    }

    counts = {}
    for c in cells + bits:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    tax = inv["row_taxonomy"]
    inv["meta"]["cell_counts"] = {
        "operand_kind_cells": len(cells), "bit_level_cells": len(bits),
        "by_status": counts,
        # four DIFFERENT denominators, each named for what it counts. Nothing may quote
        # one of them against another: see row_taxonomy.one_sentence.
        "rows_in_cell_list": tax["rows_in_cell_list"]["total"],
        "rows_run_sourced": tax["rows_run_sourced"]["total"],
        "rows_with_a_measured_cell": tax["rows_with_a_measured_cell"]["total"],
        "distinct_kinds_of_number_measured": tax["distinct_kinds_of_number_measured"]["total"],
        "distinct_format_kind_rows": len(rows),
        "distinct_format_kind_rows_means": "rows with at least one run-sourced cell "
                                           "(= len(row_coverage)); NOT the number of kinds of "
                                           "number, and not the number of rows in the cell list",
        "rows_with_measured_switching_W": tax["rows_with_switching_W"]["measured"]["total"],
        "rows_with_switching_W_any_status": tax["rows_with_switching_W"]["any_status"]["total"],
        "typed_numbers": len(TYPED),
        "mechanisms": len(inv["mechanisms"]), "holes": len(inv["holes"]),
    }

    outp = os.path.join(args.out, "inventory.json")
    with open(outp, "w") as fh:
        json.dump(inv, fh, indent=1, sort_keys=False)
        fh.write("\n")
    print("wrote %s" % outp)
    write_tables(inv, args.out)
    print(json.dumps(inv["meta"]["cell_counts"], indent=1))
    return inv


if __name__ == "__main__":
    main()
