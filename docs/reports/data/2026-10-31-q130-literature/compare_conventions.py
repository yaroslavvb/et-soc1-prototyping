#!/usr/bin/env python3
"""Q130(e) -- the data-effect ratio, with every entry on a NAMED convention.

The first pass of this lane printed one band ("every GPU lands x1.6-x1.9 of
switching power") against the ET-SoC-1's x13.6 and let three different
quantities into it: ratios OVER IDLE, ratios of ABSOLUTE board power, and a
bare watt difference.  Two of the five members were not the quantity the
sentence named.  This script recomputes each entry in both conventions where
an idle figure exists, and refuses to convert the ones where it does not.

It also prints the per-MAC figures in both conventions, because the lab's
5.783 pJ is switching energy OVER IDLE, not a whole-board total, and the
whole-board pair is a different number (11.58 / 6.14 pJ) that lives in the
same JSON object.

Every input is annotated with the committed file it comes from.  No card was
touched and nothing here is measured by this lane; the A100 watts are this
lane's reduction of a third party's published traces (see
reduce_idp.py / a100-watts.txt).
"""

# ---------------------------------------------------------------- lab figures
# docs/findings/10-data-dependent-power.md lines 27, 40, 42 (aifoundry2,
# 21 Sep session, fp32, 1,024 harts; "the idle card just before each launch
# drew 36.29 W +/- 0.06")
ET_IDLE = 36.29
ET_ZEROS_W = 38.29
ET_RANDN_W = 63.40

# docs/reports/data/2026-10-27-chain-closure/README.md, the term table
# (same clock, the E67 session's anchors; a different idle because it is a
# different session and basis)
ET_CC_IDLE = 24.60
ET_CC_ZEROS_W = 27.83
ET_CC_RANDN_W = 52.49

# docs/reports/data/2026-10-27-matmul-to-transistor/data.json
PERMAC = {
    # /permac/mean_randn_pJ, /permac/mean_zeros_pJ -- E38 registered means,
    # 3 cards, AT THE BOARD OVER IDLE (docs/findings/05-claims.md line 1094)
    "over_idle_mean": (5.783, 0.27),
    # /permac/budget_600_pJ/randn_board, /zeros_board -- WHOLE board, idle
    # included, at 1,024 harts and 600 MHz
    "whole_board": (11.579211514381424, 6.139126797383452),
    # /permac/e38_registered/<card>/{random,zeros} -- over idle, per card
    "per_card": {
        "aifoundry2": (5.920030441985411, 0.4034032614174854),
        "aifoundry3": (5.36889998752414, 0.16334422815135063),
        "aifoundry1-c1": (6.057890339687507, 0.2512321671350261),
    },
}

HOROWITZ_FP32_MAC = 4.6      # 3.7 pJ fp32 multiply + 0.9 pJ fp32 add, 45 nm 0.9 V,
                             # arithmetic only (Dally Scaled ML 2018 reproducing
                             # Horowitz ISSCC 2014 Fig. 1.1.9)

# ------------------------------------------------------- A100, derived by this
# lane from github.com/theo-gregersen/input-dependent-power-sc24.
# Values are the means printed in a100-watts.txt (10 seeds pooled, first 500 ms
# trimmed as the authors trim).  Idle 48.56 W is their own other_expt/idle.tsv.
A100_IDLE = 48.56
A100 = {
    # datatype: (randn, zeros, quietest cell, busiest cell, note)
    "fp32":   (289.10, 196.13, 196.13, 298.78, "CUDA cores"),
    "fp16":   (248.27, 197.64, 195.34, 289.26, "CUDA cores"),
    "fp16-T": (297.33, 183.77, 182.33, 299.04, "tensor cores; busiest cell has 6 samples/file"),
    "int8":   (266.27, 178.59, 171.90, 269.89, "CUDA cores"),
}

# ------------------------------------------------- literature, as published
# Bhalachandra 2022 (arXiv:2212.08805): A100 on Perlmutter, 400 W limit.
# NO idle published -> an over-idle ratio needs an assumption, and is labelled.
BHALA = (398.0, 239.0)
# Lucas & Juurlink 2016 (MASCOTS): "the power consumption of one kernel varies
# between 155 and 257 Watt depending on the processed values".  GPU unnamed,
# kernel unnamed, no idle anywhere on the record -> NOT convertible.
LUCAS = (257.0, 155.0)
ASSUMED_A100_IDLE = 50.0     # only for the labelled Bhalachandra conversion


def pct_span(quiet, busy):
    return (quiet - busy) / busy * 100.0


def main():
    print("=" * 78)
    print("1. THE DATA EFFECT, IN TWO CONVENTIONS (one row cannot serve both)")
    print("=" * 78)
    print("%-34s %10s %10s %9s" % ("system / what varied", "over idle", "absolute", "idle W"))
    print("-" * 78)

    r_oi = (ET_RANDN_W - ET_IDLE) / (ET_ZEROS_W - ET_IDLE)
    print("%-34s %9.2fx %9.2fx %9.2f" % (
        "ET-SoC-1 fp32 zeros->randn (21 Sep)", r_oi, ET_RANDN_W / ET_ZEROS_W, ET_IDLE))
    print("%-34s %9.2fx %9.2fx %9.2f" % (
        "  same, the E67-session anchors",
        (ET_CC_RANDN_W - ET_CC_IDLE) / (ET_CC_ZEROS_W - ET_CC_IDLE),
        ET_CC_RANDN_W / ET_CC_ZEROS_W, ET_CC_IDLE))
    for dt, (rn, zr, q, b, _note) in A100.items():
        print("%-34s %9.2fx %9.2fx %9.2f" % (
            "A100 %s zeros->randn" % dt,
            (rn - A100_IDLE) / (zr - A100_IDLE), rn / zr, A100_IDLE))
    for dt, (rn, zr, q, b, _note) in A100.items():
        print("%-34s %9.2fx %9.2fx %9.2f" % (
            "A100 %s quietest->busiest" % dt,
            (b - A100_IDLE) / (q - A100_IDLE), b / q, A100_IDLE))
    print("%-34s %9s  %9.3fx %9s" % (
        "Bhalachandra A100 fixed->random", "--", BHALA[0] / BHALA[1], "none"))
    print("%-34s %9.2fx %9s %9.1f" % (
        "  the same at an ASSUMED idle",
        (BHALA[0] - ASSUMED_A100_IDLE) / (BHALA[1] - ASSUMED_A100_IDLE),
        "(assumed)", ASSUMED_A100_IDLE))
    print("%-34s %9s  %9.3fx %9s" % (
        "Lucas & Juurlink, one kernel", "n/a", LUCAS[0] / LUCAS[1], "none"))
    print("%-34s %9s %10s %9s" % (
        "Ujeniya H100/H200 const->random", "n/a", "+100 W", "none"))
    print()
    print("  OVER IDLE, the four A100 datatypes quietest->busiest span")
    oi = [(b - A100_IDLE) / (q - A100_IDLE) for (_r, _z, q, b, _n) in A100.values()]
    print("    x%.2f to x%.2f   <- the band the blog may quote, over idle"
          % (min(oi), max(oi)))
    ab = [b / q for (_r, _z, q, b, _n) in A100.values()] + [BHALA[0] / BHALA[1],
                                                            LUCAS[0] / LUCAS[1]]
    print("  ABSOLUTE board, the same four plus Bhalachandra and Lucas")
    print("    x%.2f to x%.2f   <- and the ET-SoC-1 sits INSIDE this one (x%.2f / x%.2f)"
          % (min(ab), max(ab), ET_RANDN_W / ET_ZEROS_W, ET_CC_RANDN_W / ET_CC_ZEROS_W))
    print()
    print("  So the x13.6-against-x1.6 contrast is a statement about the QUIET-DATA")
    print("  FLOOR, and only over idle.  The floor as a SHARE of each machine's own")
    print("  busiest switching is the convention-robust way to say it:")
    floors = []
    for dt, (rn, zr, _q, _b, _n) in A100.items():
        share = (zr - A100_IDLE) / (rn - A100_IDLE) * 100
        floors.append(share)
        print("    A100 %-7s zeros %6.1f W of a %6.1f W switching budget = %4.1f%%"
              % (dt, zr - A100_IDLE, rn - A100_IDLE, share))
    et_floors = [(ET_ZEROS_W - ET_IDLE) / (ET_RANDN_W - ET_IDLE) * 100,
                 (ET_CC_ZEROS_W - ET_CC_IDLE) / (ET_CC_RANDN_W - ET_CC_IDLE) * 100]
    print("    ET-SoC-1 fp32  zeros %6.2f W of a %6.2f W budget = %4.1f%%  (21 Sep)"
          % (ET_ZEROS_W - ET_IDLE, ET_RANDN_W - ET_IDLE, et_floors[0]))
    print("    ET-SoC-1 fp32  zeros %6.2f W of a %6.2f W budget = %4.1f%%  (E67 session)"
          % (ET_CC_ZEROS_W - ET_CC_IDLE, ET_CC_RANDN_W - ET_CC_IDLE, et_floors[1]))
    pc = [z / r * 100 for r, z in PERMAC["per_card"].values()]
    print("    ET-SoC-1 fp32  per MAC, E38's three cards: %.1f%%, %.1f%%, %.1f%%"
          % tuple(sorted(pc)))
    print("  => the quietest data still costs the A100 %.0f-%.0f%% of its busiest"
          % (min(floors), max(floors)))
    print("     switching; on the ET-SoC-1 it costs %.0f-%.0f%%.  THAT is the finding,"
          % (min(pc + et_floors), max(pc + et_floors)))
    print("     and the ratio is just its reciprocal (x%.1f-x%.1f against x%.1f-x%.1f)."
          % (100 / max(pc + et_floors), 100 / min(pc + et_floors),
             100 / max(floors), 100 / min(floors)))
    print("  Note the A100 floor is a measured FLOOR -- the quietest data run -- not a")
    print("  demonstrated data-independent component, so write 'as little as', not")
    print("  'no matter what the numbers are'.")
    print()

    print("=" * 78)
    print("2. SPAN AS A PERCENTAGE, A100 (what the paper's 38-40 pct headline is about)")
    print("=" * 78)
    for dt, (rn, zr, q, b, note) in A100.items():
        print("  %-7s quietest %.2f -> busiest %.2f W = %+.1f%%   (%s)"
              % (dt, q, b, pct_span(q, b), note))
    rb = A100["fp16-T"]
    print("  fp16-T against its own 180-sample baseline (297.33 W): %+.1f%%"
          % pct_span(rb[2], rb[0]))
    print("  -> the paper states 'almost 40%' (abstract) / 'up to 38%' (intro) and")
    print("     names NO datatype; this lands between the two, it does not reproduce")
    print("     a statistic the paper claims.")
    print()

    print("=" * 78)
    print("3. ENERGY PER MULTIPLY-ADD -- WHICH CONVENTION")
    print("=" * 78)
    r, z = PERMAC["over_idle_mean"]
    wr, wz = PERMAC["whole_board"]
    print("  ET-SoC-1 fp32, AT THE BOARD OVER IDLE (05-claims.md line 1094):")
    print("    random %.3f pJ   zeros %.2f pJ   ratio x%.1f" % (r, z, r / z))
    print("    against Horowitz's 45 nm arithmetic-only %.1f pJ: random x%.2f, zeros x%.3f (%.0fx BELOW)"
          % (HOROWITZ_FP32_MAC, r / HOROWITZ_FP32_MAC, z / HOROWITZ_FP32_MAC,
             HOROWITZ_FP32_MAC / z))
    print("  ET-SoC-1 fp32, WHOLE BOARD (data.json /permac/budget_600_pJ/*_board):")
    print("    random %.3f pJ   zeros %.3f pJ   ratio x%.2f" % (wr, wz, wr / wz))
    print("    against the same %.1f pJ: random x%.2f, zeros x%.2f -- BOTH ABOVE it"
          % (HOROWITZ_FP32_MAC, wr / HOROWITZ_FP32_MAC, wz / HOROWITZ_FP32_MAC))
    print("    -> the '17x below the bare 45 nm arithmetic' line is TRUE over idle")
    print("       and FALSE whole-board.  Horowitz's figure is a dynamic (switching)")
    print("       energy with no idle or leakage term, so over-idle is the like-for-like")
    print("       side -- but the convention has to be printed either way.")
    print()
    print("  Per card, over idle (data.json /permac/e38_registered):")
    ratios = []
    for card, (cr, cz) in PERMAC["per_card"].items():
        ratios.append(cr / cz)
        print("    %-14s random %.3f  zeros %.4f  ratio x%.1f" % (card, cr, cz, cr / cz))
    print("    across-card spread x%.1f to x%.1f (mean of ratios x%.1f);"
          % (min(ratios), max(ratios), sum(ratios) / len(ratios)))
    print("    the 3-card MEANS give x%.1f, which is NOT the mean of the ratios." % (r / z))
    print("    The spread is set by the zeros denominator: %.4f to %.4f pJ."
          % (min(z for _r, z in PERMAC["per_card"].values()),
             max(z for _r, z in PERMAC["per_card"].values())))
    print()
    print("  10-data-dependent-power.md line 58 states the same effect as")
    print("  'a factor of 14-15 in energy per FLOP (0.22 against 2.95 pJ at 80 C,")
    print("  3.31 on the run average)' -> x%.1f to x%.1f, i.e. the 21 Sep session's"
          % (2.95 / 0.22, 3.31 / 0.22))
    print("  x%.2f over idle.  Reconciled: one session x%.1f, three cards x%.1f-x%.1f."
          % (r_oi, r_oi, min(ratios), max(ratios)))


if __name__ == "__main__":
    main()
