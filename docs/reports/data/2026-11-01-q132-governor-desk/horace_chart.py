#!/usr/bin/env python3
"""Q132(g), item 1: read the bar heights of the unlabelled chart "Benchmark Performance by Input Type" in Horace He's post, from its pixels.
Pure Python (zlib only). The image itself is not committed; its URL is:
https://substack-post-media.s3.amazonaws.com/public/images/112e6999-afc8-47c6-8cc9-c81aa145ab98_1392x844.png

    horace_chart.py <that png> > horace-chart.txt
"""
import json
import struct
import sys
import zlib


def read_png(path):
    b = open(path, "rb").read()
    assert b[:8] == b"\x89PNG\r\n\x1a\n"
    i = 8
    idat = b""
    while i < len(b):
        n, t = struct.unpack(">I4s", b[i:i + 8])
        d = b[i + 8:i + 8 + n]
        if t == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", d[:10])
        elif t == b"IDAT":
            idat += d
        i += 12 + n
    assert depth == 8 and ctype in (2, 6)
    ch = 4 if ctype == 6 else 3
    raw = zlib.decompress(idat)
    rows = []
    p = 0
    prev = bytearray(w * ch)
    stride = w * ch
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if f == 1:
            for x in range(ch, stride):
                line[x] = (line[x] + line[x - ch]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                line[x] = (line[x] + (a + prev[x]) // 2) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                b0 = prev[x]
                c = prev[x - ch] if x >= ch else 0
                pa, pb, pc = abs(b0 - c), abs(a - c), abs(a + b0 - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b0 if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        rows.append(line)
        prev = line
    return w, h, ch, rows


def main():
    w, h, ch, rows = read_png(sys.argv[1])
    px = lambda x, y: tuple(rows[y][x * ch:x * ch + 3])
    print(f"image {w} x {h}")
    # the axis baseline: the darkest long horizontal row in the lower part of the plot
    dark = []
    for y in range(h):
        n = sum(1 for x in range(130, w - 20) if sum(px(x, y)) < 200)
        dark.append((n, y))
    base = max(dark)[1]
    # the y ticks: dark pixels just left of the axis column
    # find the axis column: the darkest long vertical column in the left part
    col = max(((sum(1 for y in range(30, base) if sum(px(x, y)) < 200), x) for x in range(60, 200)))[1]
    # the dashed grid lines: rows with many light grey pixels right of the last bar and between bars
    grid = []
    for y in range(20, base - 2):
        n = sum(1 for x in range(col + 5, w - 15) if 190 <= px(x, y)[0] <= 240 and abs(px(x, y)[0] - px(x, y)[1]) < 6 and abs(px(x, y)[1] - px(x, y)[2]) < 6)
        grid.append((n, y))
    cut = 0.35 * max(n for n, _ in grid)
    ticks = [y for n, y in grid if n >= cut]
    groups = []
    for y in ticks:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    centers = [sum(g) / len(g) for g in groups] + [float(base)]
    print("axis column", col, "baseline row", base, "tick rows", centers)
    # ticks are 290, 280, ..., 230 from the top
    vals = [290, 280, 270, 260, 250, 240, 230]
    assert len(centers) == len(vals), (centers, vals)
    n = len(vals)
    mx, my = sum(centers) / n, sum(vals) / n
    b = sum((c - mx) * (v - my) for c, v in zip(centers, vals)) / sum((c - mx) ** 2 for c in centers)
    a = my - b * mx
    print(f"scale: {abs(1 / b):.3f} px per TFLOPS")
    # the bars: scan a row a little above the baseline for runs of one non-background colour
    y0 = base - 12
    runs = []
    x = col + 3
    while x < w - 5:
        c = px(x, y0)
        if sum(c) < 720:  # not near-white
            s = x
            while x < w - 5 and sum(abs(px(x, y0)[i] - c[i]) for i in range(3)) < 24:
                x += 1
            if x - s > 40:
                runs.append((s, x - 1, c))
        x += 1
    # the plot's vertical grid lines split each bar in two at this row: join runs that nearly touch
    joined = []
    for r in runs:
        if joined and r[0] - joined[-1][1] <= 12:
            joined[-1] = (joined[-1][0], r[1], joined[-1][2])
        else:
            joined.append(r)
    runs = joined
    names = ["Randn", "Checkerboard", "Sparse", "Rand", "Ternary", "One Bit", "All Pi", "Twos", "Zeros"]
    print("bars found", len(runs))
    out = {}
    for name, (s, e, c) in zip(names, runs):
        mid = s + (e - s) // 4
        # walk up the bar; a dashed grid line drawn across it interrupts the colour for a few rows, so stop only after 6 rows of something else
        y = y0
        last = y0
        while y > 5 and y > last - 6:
            if sum(abs(px(mid, y)[i] - c[i]) for i in range(3)) < 36:
                last = y
            y -= 1
        top = last  # first row of the bar
        val = a + b * (top - 0.5)
        out[name] = round(val, 2)
        print(f"  {name:13s} top row {top}  {val:.2f} TFLOPS (colour {c})")
    print("zeros / randn from the chart:", round(out["Zeros"] / out["Randn"], 4))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
