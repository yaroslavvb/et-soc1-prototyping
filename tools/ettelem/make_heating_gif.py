#!/usr/bin/env python3
"""Animated GIF of die temperature during matmul runs on different operand values.

    make_heating_gif.py horace3.json out.gif [--patterns zeros,ones,randn] [--poster out.png]

Reads the per-run curves written by analyze_horace_strict.py. Dots are the sensor readings (whole degrees).
Thin lines are single runs: the de-quantised temperature (the thermal-network fit to that run's readings,
`curve_fit`), or a 1 s moving average of the readings when the analysis has no fit. Bold lines are the mean
of a pattern's runs. Drawn with PIL at 2x and downsampled; one global palette.
"""
import argparse
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, SS = 960, 540, 2
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG, INK, MUTED, GRID = (252, 252, 251), (11, 11, 11), (98, 97, 93), (226, 225, 221)
STYLE = {  # label, colour
    "zeros": ("all zeros", (42, 120, 214)),
    "ones": ("all ones", (237, 161, 0)),
    "pi": ("all π", (27, 175, 122)),
    "sparse50": ("half zeros, half random", (74, 58, 167)),
    "uniform": ("random uniform [0, 1)", (232, 123, 164)),
    "randn": ("random normal", (227, 73, 72)),
}


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size * SS)


def smooth(y, half=5):
    """Centred moving average over 2*half+1 samples (1.1 s at 10 Hz), edges held."""
    pad = np.concatenate([np.full(half, y[0]), y, np.full(half, y[-1])])
    return np.convolve(pad, np.ones(2 * half + 1) / (2 * half + 1), mode="valid")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("out")
    ap.add_argument("--patterns", default="zeros,ones,randn")
    ap.add_argument("--poster")
    ap.add_argument("--title", default="Same matmul, same FLOPs, different heat")
    ap.add_argument("--steps", action="store_true", help="draw each run's raw reading as a thin staircase instead of dots")
    a = ap.parse_args()
    d = json.load(open(a.analysis))
    grid = np.array(d["grid"])
    pats = a.patterns.split(",")
    runs = {p: [r for r in d["runs"] if r["values"] == p] for p in pats}
    t_max = min(min(r["dur"] for r in rs) for rs in runs.values())
    t_max = float(np.floor(t_max * 10) / 10)
    start = d.get("thermal", {}).get("model_T_at_launch", {}).get("mean") or float(np.mean([r["start_temp"] for rs in runs.values() for r in rs]))
    tflops = float(np.mean([r["tflops"] for rs in runs.values() for r in rs]))
    keep = (grid >= 0.0) & (grid <= t_max + 1e-9)  # inside the run only, so the cool-down after it does not bend the end
    grid = grid[keep]
    n = len(grid)
    offset = d.get("thermal", {}).get("start_offset", 0.0)
    raw = {p: [np.array(r["curve_T"])[keep] for r in rs] for p, rs in runs.items()}
    have_fit = all("curve_fit" in r for rs in runs.values() for r in rs)
    if have_fit:  # curve_fit starts 0.1 s after launch; prepend the common launch temperature
        curves = {p: [np.concatenate([[start], r["curve_fit"]])[:n] for r in rs] for p, rs in runs.items()}
    else:
        curves = {p: [smooth(x) for x in raw[p]] for p in runs}
    means = {p: np.mean(curves[p], axis=0) for p in pats}
    y_lo = np.floor(start) - 0.6
    y_hi = max(float(m[grid <= t_max].max()) for m in means.values()) + 1.0
    L, R, T, B = 78 * SS, 250 * SS, 150 * SS, 72 * SS
    px = lambda s: L + (s - 0.0) / (t_max - 0.0) * (W * SS - L - R)
    py = lambda c: H * SS - B - (c - y_lo) / (y_hi - y_lo) * (H * SS - T - B)

    def frame(now, final=False):
        im = Image.new("RGB", (W * SS, H * SS), BG)
        dr = ImageDraw.Draw(im, "RGBA")
        dr.text((L - 50 * SS, 22 * SS), a.title, font=font(27, True), fill=INK)
        dr.text((L - 50 * SS, 62 * SS), f"ET-SoC-1: 1,024 RISC-V cores multiply 16×16 fp32 tiles at {tflops:.1f} TFLOPS. Only the operand values differ.",
                font=font(14), fill=MUTED)
        note = ("Steps: the 1 \u00b0C sensor, one staircase per run. Smooth: the mean." if a.steps
                else "Dots: sensor readings (whole degrees). Lines: single runs; bold, their mean.")
        dr.text((L - 50 * SS, 84 * SS), "Each run starts as the die cools through 81 \u2192 80 \u00b0C. " + note, font=font(14), fill=MUTED)
        for c in range(int(np.ceil(y_lo)), int(y_hi) + 1):
            dr.line([(L, py(c)), (W * SS - R, py(c))], fill=GRID, width=SS)
            dr.text((L - 12 * SS, py(c)), f"{c}", font=font(14), fill=MUTED, anchor="rm")
        dr.text((L - 50 * SS, T - 22 * SS), "die temperature, °C", font=font(13), fill=MUTED)
        for s in range(0, int(t_max) + 1):
            dr.line([(px(s), H * SS - B), (px(s), H * SS - B + 6 * SS)], fill=MUTED, width=SS)
            dr.text((px(s), H * SS - B + 10 * SS), f"{s}", font=font(14), fill=MUTED, anchor="ma")
        dr.text(((L + W * SS - R) / 2, H * SS - B + 34 * SS), "seconds since the kernel launched", font=font(13), fill=MUTED, anchor="ma")
        dr.line([(L, H * SS - B), (W * SS - R, H * SS - B)], fill=MUTED, width=SS)
        sel = (grid >= 0.0) & (grid <= min(now, t_max) + 1e-9)
        labels = []
        for p in pats:
            name, col = STYLE.get(p, (p, (80, 80, 80)))
            if have_fit and a.steps:
                for k, c in enumerate(raw[p]):
                    pts = []
                    for s_, v in zip(grid[sel], c[sel]):
                        if pts and pts[-1][1] != py(v):
                            pts.append((px(s_), pts[-1][1]))
                        pts.append((px(s_), py(v)))
                    if len(pts) > 1:
                        dr.line(pts, fill=col + (95,), width=int(1.5 * SS))
            elif have_fit:
                for k, c in enumerate(raw[p]):
                    for s_, v in list(zip(grid[sel], c[sel]))[k % 2::2]:
                        x0, y0 = px(s_), py(v)
                        dr.ellipse([x0 - 2.2 * SS, y0 - 2.2 * SS, x0 + 2.2 * SS, y0 + 2.2 * SS], fill=col + (70,))
            for c in ([] if a.steps else curves[p]):
                pts = [(px(s), py(v)) for s, v in zip(grid[sel], c[sel])]
                if len(pts) > 1:
                    dr.line(pts, fill=col + (90,), width=2 * SS, joint="curve")
            m = means[p]
            pts = [(px(s), py(v)) for s, v in zip(grid[sel], m[sel])]
            if len(pts) > 1:
                dr.line(pts, fill=col + (255,), width=5 * SS, joint="curve")
                x, y = pts[-1]
                dr.ellipse([x - 6 * SS, y - 6 * SS, x + 6 * SS, y + 6 * SS], fill=col + (255,), outline=BG + (255,), width=2 * SS)
                labels.append([y, x, p, float(m[sel][-1] - start)])
        # direct labels, pushed apart so they never overlap
        labels.sort()
        gap = 44 * SS
        for i in range(1, len(labels)):
            if labels[i][0] - labels[i - 1][0] < gap:
                labels[i][0] = labels[i - 1][0] + gap
        shift = max(0, labels[-1][0] - (H * SS - B - 8 * SS)) if labels else 0
        for y, x, p, rise in labels:
            y -= shift
            name, col = STYLE.get(p, (p, (80, 80, 80)))
            watts = d["patterns"][p].get("p80", d["patterns"][p]["p_early"])
            dr.text((x + 14 * SS, y - 9 * SS), name, font=font(15, True), fill=col)
            dr.text((x + 14 * SS, y + 10 * SS), f"{rise:+.1f} °C · {watts:.0f} W · {len(runs[p])} runs", font=font(13), fill=MUTED)
        dr.text((W * SS - 16 * SS, H * SS - 14 * SS), "github.com/yaroslavvb/et-soc1-prototyping", font=font(11), fill=MUTED, anchor="rs")
        return im.resize((W, H), Image.LANCZOS)

    times = list(np.arange(0.0, t_max + 1e-9, 0.1))
    frames = [frame(s) for s in times]
    last = frame(t_max, final=True)
    pal = last.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames + [last]]
    q[0].save(a.out, save_all=True, append_images=q[1:], duration=[70] * len(frames) + [3000], loop=0, optimize=False, disposal=1)
    if a.poster:
        last.save(a.poster)
    print(f"{len(q)} frames, {t_max} s, start {start:.1f} C -> {a.out}")


if __name__ == "__main__":
    main()
