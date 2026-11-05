#!/usr/bin/env python3
"""E163, post hoc and desk only (Wed 4 Nov 2026, the fix pass after E163's verifier): is the session's excess over M9 a level or a gain?

Reads only the committed scored.json beside it (primary > primary > power_rows > M9: each tile's M9 prediction and its measured D over
the session's own zeros, on the registered primary). For each family (the floats, fp32 and fp16; int8) it fits the error
(measured - M9) = a + b * (M9's predicted D) by ordinary least squares over every scored tile except class S (the single high B bits,
the largest per-kind miss) and the zero anchors, and prints a and b with their standard errors, beside a level alone (the mean error)
and a gain alone (a line through zero). No rule was registered for this: it changes no verdict, band, prediction or frozen file.
Standard library only:

    python3 -I -B posthoc_level_gain.py scored.json > posthoc-level-gain.txt
"""
import json
import math
import sys


def ols(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    s2 = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / (n - 2)
    return a, math.sqrt(s2 * (1 / n + mx * mx / sxx)), b, math.sqrt(s2 / sxx), mx, min(xs), max(xs)


def main():
    rows = json.load(open(sys.argv[1]))["primary"]["primary"]["power_rows"]["M9"]
    print("E163, post hoc: error (measured - M9, W) = a + b * D (M9's predicted D, W), by ordinary least squares;")
    print("every scored tile of the family except class S (single high B bits) and the zero anchors; the registered primary.")
    for fam, types in (("floats", ("fp32", "fp16")), ("int8", ("int8",))):
        sel = {k: v for k, v in rows.items()
               if v["type"] in types and not v["case"].startswith("S ") and not k.endswith("_zeros")}
        xs = [v["pred"] for v in sel.values()]
        ys = [v["error"] for v in sel.values()]
        n = len(ys)
        a, sa, b, sb, mx, lo, hi = ols(xs, ys)
        m = sum(ys) / n
        sm = math.sqrt(sum((y - m) ** 2 for y in ys) / (n - 1)) / math.sqrt(n)
        g = sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)
        print(f"\n{fam}: n = {n}, D from {lo:.2f} to {hi:.2f} W (mean {mx:.2f})")
        print(f"  both terms: a = {a:+.3f} W (s.e. {sa:.3f}), b = {100 * b:+.2f}% of D (s.e. {100 * sb:.2f}%)")
        print(f"  a level alone: {m:+.3f} W (s.e. {sm:.3f})")
        print(f"  a gain alone: {100 * g:+.2f}% of D")
        print("  tiles: " + ", ".join(sorted(sel)))


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
