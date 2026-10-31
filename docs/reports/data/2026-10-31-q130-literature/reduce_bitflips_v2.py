#!/usr/bin/env python3
"""A100 Hamming ladder from Gregersen/Patel/Choukse's published traces -- CORRECTED.

Corrects the Q130(e) desk lane's first reduction, which fitted ONE slope over
n = 0..8 and quoted the blend (0.8213 W per bit position, ~3.2 pJ per flipped bit)
while its own text said the ladder saturates at about n = 4.  Two things were
missing and are added here:

  1. A NOISE CONTROL.  `other_expt.cu` applies the mask through an `int8_t*`
     (`A[offset] = A[offset] ^ mask`), so for n >= 8 the mask truncates to 0xFF
     and every condition n = 8..32 is the SAME workload.  Their spread is
     therefore a direct read of run-to-run noise at one condition -- the only
     replication this dataset offers, since there is one trace per n.
  2. TWO SLOPES, not one.  The rising part (n = 0..4) and the flat part
     (n = 4..8) are reported separately, and the knee is located against the
     control's own sd.

The marginal price of a flipped bit is the RISING slope.  A fit that spans the
knee is not a price of anything.

Energy conversion carries the same +/-30% as the lane's other derived figures:
the runtime is inferred from trace length (99 samples at 100 ms plus the 5
trimmed), which includes `dcgmi dmon` pre- and post-roll.

Usage: python3 -I reduce_bitflips_v2.py <a100_expt_results/other_expt/bit_flips>
"""
import os
import sys
import statistics

ELEMS = 16384 * 16384           # bytes in the matrix (one flip per byte per set mask bit)
ITERS = 10000                   # kernel launches per trace
SAMPLE_S = 0.1                  # dcgmi dmon -d 100
TRIM = 5                        # samples dropped at the head, as the authors trim


def read_power(path, trim=TRIM):
    vals = []
    with open(path, errors="replace") as fh:
        lines = fh.read().splitlines()
    if not lines:
        return vals
    hdr = lines[0].split()
    try:
        col = hdr.index("POWER")
    except ValueError:
        return vals
    for ln in lines[2:]:
        f = ln.split()
        if not f or f[0] != "GPU":
            continue
        i = col - 1 + 2
        if i < len(f):
            try:
                vals.append(float(f[i]))
            except ValueError:
                pass
    return vals[trim:]


def ols(pts):
    """slope of a least-squares line through (x, y) pairs, and sum (x-xbar)^2."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx, sxx


def main():
    d = sys.argv[1]
    rows, nsamp, within = {}, {}, {}
    for fn in os.listdir(d):
        if not fn.endswith(".tsv"):
            continue
        stem = fn[:-4]
        if not stem.isdigit():
            continue
        v = read_power(os.path.join(d, fn))
        if not v:
            continue
        n = int(stem)
        rows[n] = statistics.mean(v)
        nsamp[n] = len(v)
        within[n] = statistics.stdev(v)

    base = rows[0]
    tbar = (statistics.mean(list(nsamp.values())) + TRIM) * SAMPLE_S
    flips_per_s = ELEMS * ITERS / tbar

    print("A100 PCIe -- Hamming ladder on a memory-resident int8 matrix")
    print("DERIVED from github.com/theo-gregersen/input-dependent-power-sc24")
    print("(the authors state no per-flipped-bit price anywhere in the paper)")
    print()
    print("  n  mean W   over n=0   within-trace sd   samples")
    for n in sorted(rows):
        print("  %2d  %7.2f   %+7.2f        %5.2f           %4d"
              % (n, rows[n], rows[n] - base, within[n], nsamp[n]))
    print()

    sat = [rows[n] for n in sorted(rows) if n >= 8]
    sat_mean, sat_sd = statistics.mean(sat), statistics.stdev(sat)
    print("IDENTICAL-WORKLOAD CONTROL  (n = 8..32: the int8_t store truncates the mask")
    print("to 0xFF, so these %d conditions are one workload run %d times)" % (len(sat), len(sat)))
    print("  mean %.2f W   min %.2f   max %.2f   spread %.2f   sd %.3f W"
          % (sat_mean, min(sat), max(sat), max(sat) - min(sat), sat_sd))
    print("  => a single condition's run-to-run noise is about %.2f W, and there is" % sat_sd)
    print("     ONE trace per n, so every rung below carries that much scatter.")
    print()

    s04, sxx04 = ols([(n, rows[n]) for n in range(0, 5)])
    s48, _ = ols([(n, rows[n]) for n in range(4, 9)])
    s08, _ = ols([(n, rows[n]) for n in range(0, 9)])
    se04 = sat_sd / (sxx04 ** 0.5)

    def fj(w):
        return w / flips_per_s * 1e15

    print("SLOPES  (%.1f s mean trace -> %.3g flips/s per mask bit position)" % (tbar, flips_per_s))
    print("  n=0..4, the RISING part : %+.4f W/bit  +/- %.4f (control sd)  -> %.0f fJ per flipped bit"
          % (s04, se04, fj(s04)))
    print("  n=4..8, past the knee   : %+.4f W/bit                        -> %+.0f fJ (zero within noise)"
          % (s48, fj(s48)))
    print("  n=0..8, SPANNING the knee: %+.4f W/bit  <- the blend the first reduction quoted;"
          % s08)
    print("                             it is not the price of anything.")
    print()
    print("  marginal price, rising part: %.2f pJ per flipped bit" % (fj(s04) / 1000.0))
    print("    fit uncertainty  +/- %.2f pJ (control sd / sqrt(Sxx))" % (fj(se04) / 1000.0))
    print("    timing uncertainty +/-30%% (trace-length runtime) dominates: %.1f to %.1f pJ"
          % (fj(s04) / 1000.0 * 0.7, fj(s04) / 1000.0 * 1.3))
    print()
    print("KNEE")
    print("  n=4 sits %+.2f W above the n>=8 plateau (%.2f W) = %.1f control sd"
          % (rows[4] - sat_mean, sat_mean, (rows[4] - sat_mean) / sat_sd))
    for n in range(1, 9):
        print("    step n=%d -> %d: %+.2f W" % (n - 1, n, rows[n] - rows[n - 1]))
    print("  the first four steps average %+.2f W; n=5..8 average %+.2f W"
          % (statistics.mean([rows[n] - rows[n - 1] for n in range(1, 5)]),
             statistics.mean([rows[n] - rows[n - 1] for n in range(5, 9)])))
    print()
    print("WHAT PATH THIS PRICES: a bandwidth-bound XOR over a 16,384^2 int8 matrix in")
    print("HBM2 -- load, flip, store.  It is NOT a flip inside an arithmetic unit, and")
    print("it is not comparable to the ET-SoC-1's 118-136 fJ multiply-add input bit.")


if __name__ == "__main__":
    main()
