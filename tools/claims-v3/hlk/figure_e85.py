#!/usr/bin/env python3
"""E85: the figure "heat follows the numbers" from the registered analysis's own outputs (no new numbers).

    python3 figure_e85.py ANA --out heat-follows-the-numbers.png

Left: every block's camera fundamental at 0.05 Hz (ROI, mK), corrected for the camera's gain drift to the session's
mid-time by the reference line, against the board's own 0.05 Hz fundamental (W); the line through the origin is the
reference line's transfer at the mid-time (+-1 SE band). Right: each kind's ratio R = |H_kind| / Href(t) with its
SE (thick) and its registered tolerance max(3 SE, 0.10) (thin), against the core prediction R = 1.
Colors: the reference palette's categorical slots 1-4 in fixed order (validated: CVD dE >= 9.1 adjacent, contrast
relief by direct labels and marker shapes); the reference rung is neutral gray.

Corrected after verification (Sat 31 Oct 2026, no new numbers): the title claimed "each kind", but int8 full was not
detected (E85-R1 FAIL). The title now names fp32 and fp16; a kind whose R1 failed is drawn with open markers and
labelled "not detected"; the footnote gives the reference line's slope with its SE (E85 alone does not resolve a drift).
"""
from __future__ import annotations

import argparse
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

KINDS = [("E85-F32", "fp32 randn", "#2a78d6", "o"), ("E85-I8", "int8 full", "#eb6834", "s"),
         ("E85-F16", "fp16 randn", "#1baf7a", "^"), ("E85-SP90", "fp32 sparse90", "#eda100", "D")]
REF_COLOR, INK, MUTED, GRID = "#5f5e5a", "#1f1e1c", "#6b6a64", "#e4e3de"
YLO, YHI = 0.0, 1.8   # the ratio panel's range; a tolerance beyond it is drawn clipped and labelled


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ana")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(os.path.join(a.ana, "score.json")) as f:
        sc = json.load(f)
    with open(os.path.join(a.ana, "lockin.json")) as f:
        lk = json.load(f)
    rl = sc["reference_line"]
    undetected = {k for k, v in sc["rules"].get("E85-R1_seen", {}).items() if v.get("verdict") == "FAIL"}

    def label(bid, name):
        return name + " (not detected)" if bid in undetected else name

    def line_at(t):
        return rl["mag_at_mid"] + rl["slope_mk_per_w_per_s"] * (t - rl["t_mid_s"])

    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "font.family": "DejaVu Sans"})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 4.6), gridspec_kw={"width_ratios": [1.45, 1]})
    fig.patch.set_facecolor("#fcfcfb")
    for x in (ax, bx):
        x.set_facecolor("#fcfcfb")
        x.grid(True, color=GRID, lw=0.8)
        x.set_axisbelow(True)
        for s in ("top", "right"):
            x.spines[s].set_visible(False)

    # ---- left: camera vs meter
    xmax = 0.0
    refs = [b for b in ("E85-REF1", "E85-REF2", "E85-REF3") if b in lk["blocks"] and "roi" in lk["blocks"][b]]
    for i, b in enumerate(refs):
        r = lk["blocks"][b]
        fac = rl["mag_at_mid"] / line_at(r["t_mid_s"])
        y, ye, xw = r["roi"]["amp"] * fac, r["roi"]["se_along"] * fac, r["power"]["amp"]
        ax.errorbar(xw, y, yerr=ye, fmt="o", ms=8, color=REF_COLOR, mec="#fcfcfb", mew=1.5, elinewidth=1.6,
                    capsize=0, zorder=3, label="reference rung (lq_h23 vs lq_h0)" if i == 0 else None)
        xmax = max(xmax, xw)
    if refs:
        r0 = lk["blocks"][refs[0]]
        ax.annotate("reference ×%d" % len(refs), (r0["power"]["amp"], r0["roi"]["amp"] *
                                                rl["mag_at_mid"] / line_at(r0["t_mid_s"])),
                    xytext=(10, -16), textcoords="offset points", color=INK, fontsize=9)
    for bid, name, col, mk in KINDS:
        x = sc["kinds"].get(bid)
        if not x:
            continue
        fac = rl["mag_at_mid"] / x["href_at_t"]
        y, ye, xw = x["camera_roi_mk"] * fac, x["se_camera_roi_mk"] * fac, x["board_fundamental_w"]
        face, edge = ("#fcfcfb", col) if bid in undetected else (col, "#fcfcfb")
        ax.errorbar(xw, y, yerr=ye, fmt=mk, ms=8.5, color=col, mfc=face, mec=edge, mew=1.5, elinewidth=1.6,
                    capsize=0, zorder=4, label=label(bid, name))
        off = {"E85-F16": (-78, 8), "E85-SP90": (10, 10)}.get(bid, (10, 4))
        ax.annotate(label(bid, name), (xw, y), xytext=off, textcoords="offset points", color=INK, fontsize=9, bbox=dict(boxstyle="round,pad=0.2", fc="#fcfcfb", ec="none", alpha=0.85))
        xmax = max(xmax, xw)
    xs = [0.0, xmax * 1.12]
    g, ge = rl["mag_at_mid"], rl["se_mag_at_mid"]
    ax.fill_between(xs, [0, (g - ge) * xs[1]], [0, (g + ge) * xs[1]], color=REF_COLOR, alpha=0.12, lw=0, zorder=1)
    ax.plot(xs, [0, g * xs[1]], color=REF_COLOR, lw=2, zorder=2,
            label="reference transfer %.1f ± %.1f mK/W" % (g, ge))
    ax.set_xlim(0, xs[1])
    ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    ax.set_xlabel("board power at 0.05 Hz, fundamental (W)")
    ax.set_ylabel("camera at 0.05 Hz, die footprint (mK), drift-corrected")
    ax.set_title("fp32 and fp16 random data heat the die as the meter says", color=INK, fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8.5, loc="upper left", labelcolor=INK)

    # ---- right: the ratios
    names, i = [], 0
    for bid, name, col, mk in KINDS:
        x = sc["kinds"].get(bid)
        if not x or bid == "E85-SP90":
            continue
        tol = max(3 * x["se_R"], 0.10)
        lo, hi = max(x["ratio_R"] - tol, YLO), min(x["ratio_R"] + tol, YHI)
        bx.plot([i, i], [lo, hi], color=col, lw=1.2, zorder=2)
        if hi < x["ratio_R"] + tol or lo > x["ratio_R"] - tol:
            bx.annotate("tolerance ±%.2f (clipped)" % tol, (i, YLO), xytext=(4, 4), textcoords="offset points",
                        color=MUTED, fontsize=7.5, rotation=90, va="bottom")
        bx.plot([i, i], [x["ratio_R"] - x["se_R"], x["ratio_R"] + x["se_R"]], color=col, lw=4, solid_capstyle="round",
                zorder=3)
        face, edge = ("#fcfcfb", col) if bid in undetected else (col, "#fcfcfb")
        bx.plot([i], [x["ratio_R"]], marker=mk, ms=9, color=col, mfc=face, mec=edge, mew=1.5, zorder=4)
        bx.annotate("%.2f ± %.2f" % (x["ratio_R"], x["se_R"]), (i, x["ratio_R"]), xytext=(12, -4),
                    textcoords="offset points", color=INK, fontsize=9, bbox=dict(boxstyle="round,pad=0.2", fc="#fcfcfb", ec="none", alpha=0.85))
        names.append(name + ("\n(not detected)" if bid in undetected else ""))
        i += 1
    if "E85-R3_pooled" in sc["rules"]:
        p = sc["rules"]["E85-R3_pooled"]
        bx.plot([i, i], [p["R_pooled"] - p["tolerance"], p["R_pooled"] + p["tolerance"]], color=REF_COLOR, lw=1.2)
        bx.plot([i, i], [p["R_pooled"] - p["se"], p["R_pooled"] + p["se"]], color=REF_COLOR, lw=4,
                solid_capstyle="round")
        bx.plot([i], [p["R_pooled"]], marker="o", ms=9, color=REF_COLOR, mec="#fcfcfb", mew=1.5)
        bx.annotate("%.2f ± %.2f" % (p["R_pooled"], p["se"]), (i, p["R_pooled"]), xytext=(12, -4),
                    textcoords="offset points", color=INK, fontsize=9, bbox=dict(boxstyle="round,pad=0.2", fc="#fcfcfb", ec="none", alpha=0.85))
        names.append("pooled")
        i += 1
    bx.set_ylim(YLO, YHI)
    bx.axhspan(0.9, 1.1, color=GRID, alpha=0.7, lw=0, zorder=0)
    bx.axhline(1.0, color=MUTED, lw=1.2, ls="--", zorder=1)
    bx.set_xticks(range(len(names)))
    bx.set_xticklabels(names)
    bx.set_xlim(-0.5, len(names) - 0.05)
    bx.set_ylabel("R = kind's mK/W ÷ reference's mK/W")
    bx.set_title("Ratio to the reference (prediction: 1)", color=INK, fontsize=11, loc="left")
    m = rl["mag_at_mid"]
    drift = "Drift correction: the registered reference line, %+.0f ± %.0f %%/h (E85 alone resolves no drift)" % (
        100 * rl["slope_mk_per_w_per_s"] * 3600 / m, 100 * rl["se_slope"] * 3600 / m)
    fig.text(0.01, 0.034, "E85, aifoundry2, 192 minions at 800 MHz, each kind against its own type's zeros at 0.05 Hz. "
             "Thick bar: ±1 SE; thin: the registered tolerance max(3 SE, 0.10); band: ±10%.",
             color=MUTED, fontsize=8)
    fig.text(0.01, 0.005, "Open markers: not detected (E85-R1 FAIL), so their ratio and lag carry no claim. " + drift + ".",
             color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(a.out, dpi=160)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
