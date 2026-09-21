#!/usr/bin/env python3
"""Animated GIF of the long runs: die temperature against log time until the 90 C cap or 10 minutes.

    make_long_gif.py long.json out.gif [--poster out.png] [--groups zeros:32,ones:32,randn:32,randn:12]
"""
import argparse
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, SS = 960, 540, 2
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BG, INK, MUTED, GRID = (252, 252, 251), (11, 11, 11), (98, 97, 93), (226, 225, 221)
STYLE = {
    ("zeros", 32): ("all zeros", (42, 120, 214)),
    ("ones", 32): ("all ones", (237, 161, 0)),
    ("randn", 32): ("random normal", (227, 73, 72)),
    ("randn", 12): ("random, 3/8 of the cores", (74, 58, 167)),
    ("randn", 8): ("random, 1/4 of the cores", (27, 175, 122)),
    ("ones", 16): ("ones, half of the cores", (160, 120, 40)),
    ("checker", 32): ("checkerboard", (27, 175, 122)),
    ("uniform", 32): ("random uniform", (232, 123, 164)),
}


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size * SS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("analysis")
    ap.add_argument("out")
    ap.add_argument("--poster")
    ap.add_argument("--groups", default="zeros:32,ones:32,randn:32")
    ap.add_argument("--title", default="How long until 90 °C? Same matmul, same FLOPs")
    ap.add_argument("--cap", type=float, default=90.0)
    a = ap.parse_args()
    d = json.load(open(a.analysis))
    groups = [(g.split(":")[0], int(g.split(":")[1])) for g in a.groups.split(",")]
    runs = {g: [r for r in d["runs"] if (r["values"], r["per_shire"]) == g] for g in groups}
    curves = {}
    for g, rs in runs.items():
        curves[g] = []
        for r in rs:
            sec = np.array(r["sec"], float)
            T = np.array([np.nan if v is None else v for v in r["curve_T"]], float)
            keep = (sec >= 1) & (sec <= r["dur"]) & ~np.isnan(T)
            sec, T = sec[keep], T[keep]
            Ts = np.convolve(np.concatenate([[T[0]], T, [T[-1]]]), np.ones(3) / 3, mode="valid")
            curves[g].append((sec, Ts, r))
    t_lo, t_hi = 1.0, 600.0
    y_lo, y_hi = 75.5, a.cap + 1.5
    L, R, T_, B = 78 * SS, 280 * SS, 150 * SS, 72 * SS
    px = lambda s: L + (math.log10(max(s, t_lo)) - math.log10(t_lo)) / (math.log10(t_hi) - math.log10(t_lo)) * (W * SS - L - R)
    py = lambda c: H * SS - B - (c - y_lo) / (y_hi - y_lo) * (H * SS - T_ - B)
    tflops = np.mean([r["tflops"] for rs in runs.values() for r in rs if r["per_shire"] == 32])

    def frame(now):
        im = Image.new("RGB", (W * SS, H * SS), BG)
        dr = ImageDraw.Draw(im, "RGBA")
        dr.text((L - 50 * SS, 22 * SS), a.title, font=font(27, True), fill=INK)
        dr.text((L - 50 * SS, 62 * SS), f"ET-SoC-1: 1,024 RISC-V cores multiply 16×16 fp32 tiles at {tflops:.1f} TFLOPS. Only the operand values differ.",
                font=font(14), fill=MUTED)
        dr.text((L - 50 * SS, 84 * SS), f"Each run starts as the die cools through 81 → 80 °C and ends at {a.cap:.0f} °C or after 10 minutes. One line per run.",
                font=font(14), fill=MUTED)
        for c in range(int(math.ceil(y_lo)), int(y_hi) + 1, 2):
            dr.line([(L, py(c)), (W * SS - R, py(c))], fill=GRID, width=SS)
            dr.text((L - 12 * SS, py(c)), f"{c}", font=font(14), fill=MUTED, anchor="rm")
        dr.line([(L, py(a.cap)), (W * SS - R, py(a.cap))], fill=(227, 73, 72, 160), width=2 * SS)
        dr.text((W * SS - R - 4 * SS, py(a.cap) - 6 * SS), f"{a.cap:.0f} °C: run stops", font=font(12), fill=(180, 60, 60), anchor="rs")
        dr.text((L - 50 * SS, T_ - 30 * SS), "die temperature, °C", font=font(13), fill=MUTED)
        for s, lab in [(1, "1 s"), (3, "3"), (10, "10 s"), (30, "30"), (60, "1 min"), (180, "3"), (600, "10 min")]:
            dr.line([(px(s), H * SS - B), (px(s), H * SS - B + 6 * SS)], fill=MUTED, width=SS)
            dr.text((px(s), H * SS - B + 10 * SS), lab, font=font(14), fill=MUTED, anchor="ma")
        dr.text(((L + W * SS - R) / 2, H * SS - B + 34 * SS), "time since the kernel launched (log scale)", font=font(13), fill=MUTED, anchor="ma")
        dr.line([(L, H * SS - B), (W * SS - R, H * SS - B)], fill=MUTED, width=SS)
        labels = []
        for g in groups:
            name, col = STYLE.get(g, (f"{g[0]} @{g[1]}", (80, 80, 80)))
            tip = None
            ends = []
            for sec, Ts, r in curves[g]:
                sel = sec <= now
                pts = [(px(s), py(v)) for s, v in zip(sec[sel], Ts[sel])]
                if len(pts) > 1:
                    dr.line(pts, fill=col + (230,), width=3 * SS, joint="curve")
                    if tip is None or pts[-1][0] > tip[0]:
                        tip = pts[-1]
                    if now >= r["dur"]:
                        x, y = pts[-1]
                        dr.ellipse([x - 5 * SS, y - 5 * SS, x + 5 * SS, y + 5 * SS], fill=col + (255,), outline=BG + (255,), width=2 * SS)
                        ends.append(r)
            if tip:
                done = [r for r in ends]
                if done and len(done) == len(curves[g]):
                    capped = [r["dur"] for r in done if r["reason"] == "cap"]
                    if capped:
                        note = f"{a.cap:.0f} \u00b0C after " + (f"{capped[0]:.0f}" if len(capped) == 1 else f"{min(capped):.0f}\u2013{max(capped):.0f}") + f" s ({len(done)} runs)" * (len(done) > 1)
                    else:
                        ends_T = [r["T_at"].get("600", r["t_max"]) for r in done]
                        note = "never: " + (f"{ends_T[0]:.0f}" if len(ends_T) == 1 else f"{min(ends_T):.0f}\u2013{max(ends_T):.0f}") + " \u00b0C after 10 min"
                else:
                    note = f"{len(curves[g])} runs"
                labels.append([tip[1], tip[0], name, col, note])
        labels.sort()
        tips_y = [l[0] for l in labels]
        gap = 44 * SS
        for i in range(1, len(labels)):
            if labels[i][0] - labels[i - 1][0] < gap:
                labels[i][0] = labels[i - 1][0] + gap
        for (y, x, name, col, note), y0 in zip(labels, tips_y):
            lx = W * SS - R + 18 * SS
            if x < W * SS - R - 4 * SS:
                dr.line([(x + 8 * SS, y0), (lx - 6 * SS, y)], fill=col + (120,), width=SS)
            dr.text((lx, y - 9 * SS), name, font=font(15, True), fill=col)
            dr.text((lx, y + 10 * SS), note, font=font(13), fill=MUTED)
        dr.text((W * SS - 16 * SS, H * SS - 14 * SS), "github.com/yaroslavvb/et-soc1-prototyping", font=font(11), fill=MUTED, anchor="rs")
        return im.resize((W, H), Image.LANCZOS)

    times = list(np.logspace(0, math.log10(t_hi), 80))
    frames = [frame(s) for s in times]
    last = frame(1e9)
    pal = last.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames + [last]]
    q[0].save(a.out, save_all=True, append_images=q[1:], duration=[70] * len(frames) + [3500], loop=0, optimize=False, disposal=1)
    if a.poster:
        last.save(a.poster)
    print(f"{len(q)} frames -> {a.out}")


if __name__ == "__main__":
    main()
