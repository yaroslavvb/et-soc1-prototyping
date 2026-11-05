#!/usr/bin/env python3
"""E165, post hoc and desk only (Wed 4 Nov 2026, the fix pass after the verifier of aifoundry2's card day): where the board's blind
error under M9's aifoundry2 part sits, by tile.

Reads only the committed results.json beside it: score > reported > tiles, each scored tile's measured burst board (burst_w, the mean
of its counted passes) and M9's aifoundry2 part recomputed for that tile (primary > burst_board_w), the registered primary of
E165-R2; and cells > burst_mhz_runs for each pass's burst clock. It first checks that it reproduces the registered E165-R2 Bp and Bg
lines (results.json > score > rules), then splits the pinned board's squared error between

  * the single-high-bit tiles (class S) whose board ran more than 1 W over M9's part, and
  * the tiles with a single-pass clock dip (a counted pass below 790 MHz while the tile's other passes ran at 800 MHz),

and reads the governed board's error as a level (the mean) and a spread (the standard deviation about it). The error is measured
minus predicted, as in the registered scorer. No rule was registered for any of this: it changes no verdict, band, prediction or
frozen file. Standard library only:

    python3 -I -B posthoc_board_split.py results.json > posthoc-board-split.txt
"""
import json
import math
import sys


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


def main():
    d = json.load(open(sys.argv[1]))
    tiles = d["score"]["reported"]["tiles"]
    rules = d["score"]["rules"]["E165-R2"]
    cells = {c["name"]: c for c in d["cells"].values() if "name" in c}   # E80's two replicate cells (R0) carry no tile name
    err = {k: v["burst_w"] - v["primary"]["burst_board_w"] for k, v in tiles.items()}
    grp = {k: v["group"] for k, v in tiles.items()}
    print("E165, post hoc: the board's blind error (measured - M9's aifoundry2 part, recomputed per tile; W), by tile.")
    print("Source: results.json > score > reported > tiles (burst_w, primary.burst_board_w) and cells (burst_mhz_runs).")

    ok = True
    for g, key in (("pinned", "Bp"), ("governed", "Bg")):
        e = [err[k] for k in err if grp[k] == g]
        r, m = round(rms(e), 3), round(sum(e) / len(e), 3)
        same = r == rules[key]["rms"] and m == rules[key]["mean"] and len(e) == rules[key]["n"]
        ok = ok and same
        print(f"\nself-check, {g} board: n {len(e)}, rms {r:.3f} W, mean {m:+.3f} W; the registered E165-R2 {key}: n "
              f"{rules[key]['n']}, rms {rules[key]['rms']:.3f}, mean {rules[key]['mean']:+.3f}: {'EQUAL' if same else 'DIFFERS'}")
    if not ok:
        print("STOPPED: this script does not reproduce the registered lines")
        sys.exit(1)

    pin = sorted(k for k in err if grp[k] == "pinned")
    sse = sum(err[k] ** 2 for k in pin)
    print(f"\nTHE PINNED BOARD, {len(pin)} tiles: rms {rms([err[k] for k in pin]):.3f} W, squared error {sse:.3f} W^2")

    cls_s = [k for k in pin if tiles[k]["class"] == "S"]
    over = [k for k in cls_s if err[k] > 1.0]
    print(f"\n(a) class S (single high B bits): {len(cls_s)} pinned tiles, {100 * sum(err[k] ** 2 for k in cls_s) / sse:.0f}% of the "
          "squared error; each one:")
    for k in sorted(cls_s, key=lambda k: -err[k]):
        print(f"    {k:34s} {err[k]:+.3f} W   (measured {tiles[k]['burst_w']:.3f}, M9's part {tiles[k]['primary']['burst_board_w']:.3f})")
    print(f"    over by more than 1 W: {len(over)} tiles, {min(err[k] for k in over):+.2f} to {max(err[k] for k in over):+.2f} W, "
          f"{100 * sum(err[k] ** 2 for k in over) / sse:.0f}% of the squared error")
    rest = [err[k] for k in pin if k not in over]
    print(f"    the pinned board without those {len(over)}: rms {rms(rest):.3f} W over {len(rest)} tiles (mean {sum(rest) / len(rest):+.3f})")

    dips = []
    for k in pin:
        runs = cells[k]["burst_mhz_runs"]
        low = [x for x in runs if x < 790]
        if len(low) == 1 and all(x >= 799.5 for x in runs if x >= 790):
            dips.append((k, low[0], runs))
    print(f"\n(b) a single-pass clock dip (one counted pass under 790 MHz, the others at 800): {len(dips)} pinned tiles, "
          f"{100 * sum(err[k] ** 2 for k, _, _ in dips) / sse:.0f}% of the board's squared error; each one:")
    for k, lo, runs in sorted(dips, key=lambda x: x[1]):
        print(f"    {k:34s} dip {lo:.1f} MHz (passes {', '.join(f'{x:.1f}' for x in runs)}); board error {err[k]:+.3f} W")
    if dips:
        print(f"    the dips span {min(x[1] for x in dips):.1f}-{max(x[1] for x in dips):.1f} MHz")
    dk = {k for k, _, _ in dips}
    rest2 = [err[k] for k in pin if k not in dk]
    print(f"    the pinned board without those {len(dips)}: rms {rms(rest2):.3f} W over {len(rest2)} tiles")
    both = [err[k] for k in pin if k not in dk and k not in over]
    print(f"    without both sets: rms {rms(both):.3f} W over {len(both)} tiles")

    gov = sorted(k for k in err if grp[k] == "governed")
    e = [err[k] for k in gov]
    m = sum(e) / len(e)
    sd = math.sqrt(sum((x - m) ** 2 for x in e) / len(e))
    print(f"\n(c) THE GOVERNED BOARD, {len(gov)} tiles (the burst clock under the cap): rms {rms(e):.3f} W = a level (the mean) "
          f"{m:+.3f} W and a spread about it {sd:.3f} W (population SD; rms^2 = mean^2 + SD^2);")
    print(f"    the level is {100 * m * m / rms(e) ** 2:.0f}% of the mean squared error; {sum(1 for x in e if x < 0)} of "
          f"{len(e)} tiles read under M9's part; the errors run {min(e):+.3f} to {max(e):+.3f} W")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
