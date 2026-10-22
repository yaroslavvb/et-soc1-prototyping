#!/usr/bin/env python3
"""render_hm.py - E62 heat movies: ANA + RED + protocol.json -> MOV (mp4s, posters, stills, SVGs, movies.json).

One movie per block that has a phase-averaged cycle, plus the bloom movie built straight from the reduced
frames.  Frame layout is phone-portrait first, 768x960:

    y    0..575   the camera panel: the 2x2-binned difference image (RdBu_r, +-L mK, alpha ~ |dT|/L)
                  composited over the session's own scene in grey, 128x96 -> x2 -> x3 = 768x576
    y      576    a hairline
    y  577..959   the read-out panel: the 6x6 die map on the left (active shires lit in the accent,
                  M/S and IO cells hatched and labelled), and on the right the block title, the real
                  time inside the cycle, the speed-up, the colour key in mK and a schedule strip of the
                  block's phases with a moving cursor.

Inputs are exactly the files build/INTERFACES.md defines; nothing here touches the card or the camera.

    uv run -q --with numpy --with matplotlib --with pillow python3 render_hm.py <ANA> \
        --red <RED> --protocol protocol.json --out <MOV> [--only BLOCK] [--fps 24] [--contact]

Every movie is 10-20 s at 24 fps: the speed-up is chosen per block from the cycle length, and L (the
half-range of the colour key) from the data - the 98th percentile of |difference| in the phases' steady
state, rounded up the 1-2-5 ladder.  Encoding is the lab's own line: libx264, yuv420p, crf 23, preset
slow, +faststart; a movie over the size budget is re-encoded at a higher crf rather than shipped fat.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- frame geometry and house style

FRAME_W, FRAME_H = 768, 960
CAM_H = 576                      # 192 * 3
PY = CAM_H + 1                   # first row of the read-out panel
BIN_W, BIN_H = 128, 96           # the reduced (2x2-binned) grid
FULL_W, FULL_H = 256, 192        # the sensor grid

INK = (24, 32, 43)
MUTED = (74, 84, 98)
FAINT = (100, 109, 123)          # 4.8:1 on the panel; the old #8b94a2 was 2.83:1 and failed WCAG
LINE = (203, 210, 222)
PANEL_BG = (244, 246, 249)
CARD = (255, 255, 255)
ACCENT = (166, 63, 28)           # the heat pages' warm rust
IDLE_FILL = (232, 236, 241)

DIE_CELL, DIE_GAP = 40, 4
DIE_X0, DIE_Y0 = 52, PY + 30
TXT_X0, TXT_X1 = 336, 744
DIE_NOTE = "this map is the die's own frame, not the camera's view"
# --die-view camera: draw the die turned the way E62 measured the camera sees it (rolled about -90 degrees, not
# mirrored: west->east runs UP the picture, north->south runs RIGHT), so a lit corner on the map sits where its heat
# appears in the camera panel. Die cell (row r, col index c 0..5) goes to screen row 5-c, screen column r.
DIE_VIEW = "die"
CAMERA_DIE_NOTE = "camera's view: west to east up, north to south right"   # fits the frame's two lines


def die_pos(r, c):
    """screen (row, col) of die cell (row r, 0-based column index c) in the current DIE_VIEW"""
    return (r, c) if DIE_VIEW == "die" else (5 - c, r)

IDLE_NAMES = {"", "-", "none", "idle", "off", "null", "None"}
NICE = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 80, 100, 125, 150, 200, 250, 300,
        400, 500, 600, 800, 1000, 1250, 1500, 2000, 2500, 3000, 4000, 5000]
SPEEDUPS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 50, 60, 90, 120]
FFMPEG = os.environ.get("FFMPEG", shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg")
FFPROBE = os.environ.get("FFPROBE", shutil.which("ffprobe") or
                         os.path.join(os.path.dirname(FFMPEG), "ffprobe"))


def nice_ceil(x: float) -> float:
    """Round up to the next 1-2-5-ish number, so a colour key reads '40 mK' and not '38.4 mK'."""
    if not np.isfinite(x) or x <= 0:
        return 1.0
    dec = 10.0 ** math.floor(math.log10(x))
    for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * dec >= x - 1e-12:
            return float(m * dec) if m * dec >= 1 else round(m * dec, 6)
    return float(10 * dec)


def nice_from_list(x: float) -> float:
    for n in NICE:
        if n >= x - 1e-9:
            return float(n)
    return float(NICE[-1])


# ---------------------------------------------------------------- fonts, colour maps, small drawing

from PIL import Image, ImageDraw, ImageFont                                     # noqa: E402

_FONT_CACHE: dict = {}
_FONT_FILES = [("/System/Library/Fonts/Helvetica.ttc", 0, 1),
               ("/System/Library/Fonts/HelveticaNeue.ttc", 0, 1),
               ("/System/Library/Fonts/Supplemental/Arial.ttf", None, None)]


def font(size: int, bold: bool = False):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    f = None
    for path, i_reg, i_bold in _FONT_FILES:
        if not os.path.exists(path):
            continue
        idx = (i_bold if bold else i_reg)
        try:
            f = ImageFont.truetype(path, size) if idx is None else ImageFont.truetype(path, size, index=idx)
            break
        except Exception:
            f = None
    if f is None:                                        # matplotlib always ships DejaVu
        try:
            import matplotlib
            base = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
            f = ImageFont.truetype(os.path.join(base, "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)
        except Exception:
            f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


_LUT_CACHE: dict = {}


def lut(name: str) -> np.ndarray:
    """256x3 uint8 colour table for a matplotlib colour map name."""
    if name in _LUT_CACHE:
        return _LUT_CACHE[name]
    import matplotlib
    try:
        cm = matplotlib.colormaps[name]
    except Exception:                                    # older matplotlib
        cm = matplotlib.cm.get_cmap(name)
    table = (np.asarray(cm(np.linspace(0, 1, 256)))[:, :3] * 255.0 + 0.5).astype(np.uint8)
    _LUT_CACHE[name] = table
    return table


def tint(colour, frac: float, over=CARD):
    return tuple(int(round(over[i] + (colour[i] - over[i]) * frac)) for i in range(3))


def text_w(draw, s, f) -> float:
    try:
        return draw.textlength(s, font=f)
    except Exception:
        return f.getsize(s)[0]


def wrap(draw, s: str, f, width: int):
    out, line = [], ""
    for word in str(s).split():
        trial = (line + " " + word).strip()
        if line and text_w(draw, trial, f) > width:
            out.append(line)
            line = word
        else:
            line = trial
    if line:
        out.append(line)
    return out or [""]


def fit_text(draw, s, width, sizes=(33, 30, 27, 24, 21), max_lines=2, bold=True):
    """The largest of `sizes` at which `s` still fits in `max_lines`; the last line is cut if nothing does."""
    f, lines = None, None
    for sz in sizes:
        f = font(sz, bold)
        lines = wrap(draw, s, f, width)
        if len(lines) <= max_lines:
            return f, lines
    lines = lines[:max_lines]
    if lines:
        last = lines[-1]
        while last and text_w(draw, last + u"…", f) > width:
            last = last[:-1]
        lines[-1] = last + u"…"
    return f, lines


def on_dark(rgb) -> bool:
    return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) < 140


def halo_text(draw, xy, s, f, fill, halo=(255, 255, 255), r=2):
    """Text with a light outline, so a label stays readable over the board."""
    for dx in (-r, 0, r):
        for dy in (-r, 0, r):
            if dx or dy:
                draw.text((xy[0] + dx, xy[1] + dy), s, font=f, fill=halo)
    draw.text(xy, s, font=f, fill=fill)


def rrect(draw, box, radius=4, fill=None, outline=None, width=1):
    try:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    except Exception:
        draw.rectangle(box, fill=fill, outline=outline, width=width)


def hatch(draw, box, colour, step=6, width=1):
    """Anti-diagonal hatching clipped to box - for the cells that are not compute shires."""
    x0, y0, x1, y1 = (float(v) for v in box)
    w, h = x1 - x0, y1 - y0
    for d in range(0, int(w + h) + 1, int(step)):
        ax, ay = (x0 + d, y0) if d <= w else (x1, y0 + d - w)
        bx, by = (x0, y0 + d) if d <= h else (x0 + d - h, y1)
        draw.line([ax, ay, bx, by], fill=colour, width=width)


def up(a: np.ndarray, k: int) -> np.ndarray:
    """Nearest-neighbour upscale by an integer factor - thermal pixels are never interpolated."""
    return np.repeat(np.repeat(a, k, axis=0), k, axis=1)


def bin2(a: np.ndarray) -> np.ndarray:
    h, w = a.shape[:2]
    return a[:h // 2 * 2, :w // 2 * 2].reshape(h // 2, 2, w // 2, 2).mean(axis=(1, 3))


# ---------------------------------------------------------------- the die map

def die_map():
    """(grid[6][6] of cell labels, {shire: (row, col1based)}, {group: feat}) from hp/placements.py."""
    grid = groups = None
    try:
        sys.path.insert(0, os.path.join(HERE, "..", "hp"))
        import placements                                                  # our own repo module
        groups, grid = placements.derive()
    except Exception as exc:                                               # fall back to the committed json
        sys.stderr.write("render_hm: placements.py did not import (%s); using placements.json\n" % exc)
        with open(os.path.join(HERE, "..", "hp", "placements.json")) as fh:
            pj = json.load(fh)
        grid, groups = pj["grid_rows_r0_r5_cols_c1_c6"], pj["groups"]
    pos = {}
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            s = str(cell).strip()
            if s.startswith("S") and s[1:].isdigit():
                pos[int(s[1:])] = (r, c + 1)
    assert len(pos) == 32, "die map should hold 32 compute shires, got %d" % len(pos)
    return grid, pos, groups


def cell_kind(label: str):
    s = str(label).strip()
    if s.startswith("S") and s[1:].isdigit():
        return "shire", int(s[1:]), s
    if s.upper().startswith("IO"):
        return "io", None, "IO"
    return "ms", None, "M/S"


def draw_die(img, draw, grid, lit, x0, y0, cell, gap, label_cells=True, fs=None, lit_colour=ACCENT,
             labels_rc=True):
    """The 6x6 die: lit shires in the accent, the four non-compute cells hatched and labelled."""
    fs = fs or max(9, int(cell * 0.40))
    f = font(fs, True)
    lit = set(lit or ())
    for r in range(6):
        for c in range(6):
            kind, shire, text = cell_kind(grid[r][c])
            sr, sc = die_pos(r, c)
            bx = x0 + sc * (cell + gap)
            by = y0 + sr * (cell + gap)
            box = (bx, by, bx + cell, by + cell)
            on = kind == "shire" and shire in lit
            if kind == "shire":
                rrect(draw, box, radius=max(2, cell // 9), fill=lit_colour if on else CARD,
                      outline=lit_colour if on else LINE, width=1)
            else:
                rrect(draw, box, radius=max(2, cell // 9), fill=(249, 250, 252), outline=LINE, width=1)
                hatch(draw, (bx + 1, by + 1, bx + cell - 1, by + cell - 1), LINE,
                      step=max(4, cell // 6))
            if label_cells:
                col = CARD if on else (MUTED if kind == "shire" else FAINT)
                tw = text_w(draw, text, f)
                if tw > cell - 2:                                          # "IO/PCIe" never fits
                    f2 = font(max(8, int(fs * (cell - 4) / max(tw, 1))), True)
                    tw = text_w(draw, text, f2)
                else:
                    f2 = f
                draw.text((bx + (cell - tw) / 2, by + (cell - f2.size * 1.25) / 2 + 1), text,
                          font=f2, fill=col)
    # row / column labels
    if not labels_rc:
        return
    fl = font(max(10, int(cell * 0.42)))
    for k in range(6):                       # labels down the left side, then along the bottom
        t = ("r%d" % k) if DIE_VIEW == "die" else ("c%d" % (6 - k))
        draw.text((x0 - 6 - text_w(draw, t, fl), y0 + k * (cell + gap) + (cell - fl.size * 1.3) / 2),
                  t, font=fl, fill=FAINT)
    for k in range(6):
        t = ("c%d" % (k + 1)) if DIE_VIEW == "die" else ("r%d" % k)
        draw.text((x0 + k * (cell + gap) + (cell - text_w(draw, t, fl)) / 2,
                   y0 + 6 * (cell + gap) - gap + 5), t, font=fl, fill=FAINT)


# ---------------------------------------------------------------- the camera panel

def scene_grey(scene: np.ndarray, lo_hi=(2, 98), out=(58, 214)) -> np.ndarray:
    """The session's own scene as a grey backdrop: robust percentiles -> a mid grey ramp."""
    s = np.asarray(scene, dtype=np.float32)
    lo, hi = np.percentile(s[np.isfinite(s)], lo_hi) if np.isfinite(s).any() else (0.0, 1.0)
    if hi - lo < 1e-6:
        hi = lo + 1.0
    g = np.clip((s - lo) / (hi - lo), 0, 1) * (out[1] - out[0]) + out[0]
    return np.repeat(g.astype(np.uint8)[:, :, None], 3, axis=2)


def composite(diff: np.ndarray, L: float, grey: np.ndarray, cmap="RdBu_r", signed=True,
              gamma=1.0, max_alpha=0.95, k=1) -> np.ndarray:
    """diff [96,128] mK over the grey scene; alpha rises with |dT|/L so sub-threshold pixels stay grey."""
    d = np.nan_to_num(np.asarray(diff, dtype=np.float32))
    if signed:
        x = np.clip(d / L, -1.0, 1.0) * 0.5 + 0.5
        a = np.clip(np.abs(d) / L, 0.0, 1.0)
    else:
        x = np.clip(d / L, 0.0, 1.0)
        a = x.copy()
    rgb = lut(cmap)[(x * 255.0 + 0.5).astype(np.uint8)]
    a = (a ** gamma) * max_alpha
    sh = grey.shape[0] // d.shape[0]                     # 2 for the full scene, 1 for a binned one
    if sh > 1:
        rgb, a = up(rgb, sh), up(a, sh)
    out = grey.astype(np.float32) * (1.0 - a[:, :, None]) + rgb.astype(np.float32) * a[:, :, None]
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    return up(out, k) if k > 1 else out


# ---------------------------------------------------------------- the read-out panel

def draw_key(img, draw, box, cmap, lo, hi, caption, unit="mK", signed=True, ends=("cooler", "warmer"),
             fs=19):
    """The colour key: the ramp itself, the two ends named inside it, the numbers under it."""
    x0, y0, x1, y1 = box
    fc, fl, fe = font(fs), font(fs, True), font(max(13, fs - 3), True)
    if caption:
        draw.text((x0, y0 - fc.size - 7), caption, font=fc, fill=MUTED)
    n = max(8, int(x1 - x0))
    table = lut(cmap)
    ramp = table[(np.linspace(0, 1, n) * 255).astype(np.uint8)]
    bar = np.repeat(ramp[None, :, :], int(y1 - y0), axis=0)
    img.paste(Image.fromarray(bar), (int(x0), int(y0)))
    draw.rectangle(box, outline=LINE, width=1)
    if signed:
        draw.line([(x0 + x1) / 2, y0, (x0 + x1) / 2, y1], fill=(255, 255, 255), width=1)
    if ends:
        ty = y0 + ((y1 - y0) - fe.size * 1.3) / 2
        draw.text((x0 + 7, ty), ends[0], font=fe,
                  fill=CARD if on_dark(table[0]) else INK)
        draw.text((x1 - 7 - text_w(draw, ends[1], fe), ty), ends[1], font=fe,
                  fill=CARD if on_dark(table[255]) else INK)
    yl = y1 + 6
    draw.text((x0, yl), ("%+g" % lo) if signed else ("%g" % lo), font=fl, fill=INK)
    if signed:
        draw.text(((x0 + x1) / 2 - text_w(draw, "0", fl) / 2, yl), "0", font=fl, fill=INK)
    r = (("%+g" % hi) if signed else ("%g" % hi)) + " " + unit
    draw.text((x1 - text_w(draw, r, fl), yl), r, font=fl, fill=INK)


def draw_schedule(draw, box, edges, sets, t_now, cycle_s, n_cycles=None, caption_extra=None):
    """The block's phases as segments with a moving cursor; the segment in play wears the accent."""
    x0, y0, x1, y1 = box
    edges = [float(e) for e in np.asarray(edges, dtype=np.float64).ravel().tolist()]
    sets = list(sets)[:max(len(edges) - 1, 0)]       # a short phase_edges_s must not index past itself
    if len(edges) < 2 or not sets:
        return
    span = max(edges[-1] - edges[0], 1e-6)
    fs, fsb = font(18), font(18, True)
    cur = -1
    for i in range(len(sets)):
        if edges[i] <= t_now < edges[i + 1]:
            cur = i
    for i, name in enumerate(sets):
        a = x0 + (edges[i] - edges[0]) / span * (x1 - x0)
        b = x0 + (edges[i + 1] - edges[0]) / span * (x1 - x0)
        idle = str(name).strip() in IDLE_NAMES
        on = i == cur
        hot = on and not idle                                  # the accent only ever means "computing"
        fill = tint(ACCENT, 0.16) if hot else (IDLE_FILL if idle else CARD)
        out = ACCENT if hot else (MUTED if on else LINE)
        rrect(draw, (a, y0, max(b - 1, a + 2), y1), radius=3, fill=fill, outline=out, width=2 if on else 1)
        lab = "idle" if idle else str(name)
        f = fsb if on else fs
        col = ACCENT if hot else ((MUTED if idle else INK) if on else (FAINT if idle else MUTED))
        tw = text_w(draw, lab, f)
        if tw > (b - a) - 8:                           # too narrow to name: leave it blank, never stump it
            for smaller in (15, 13):
                f2 = font(smaller, on)
                if text_w(draw, lab, f2) <= (b - a) - 6:
                    f, tw = f2, text_w(draw, lab, f2)
                    break
            else:
                lab, tw = "", 0
        if lab:
            draw.text((a + ((b - a) - tw) / 2, y0 + ((y1 - y0) - f.size * 1.28) / 2), lab, font=f, fill=col)
    # the cursor
    cx = x0 + (min(max(t_now, edges[0]), edges[-1]) - edges[0]) / span * (x1 - x0)
    draw.line([cx, y0 - 7, cx, y1 + 7], fill=INK, width=3)
    draw.polygon([(cx - 6, y0 - 13), (cx + 6, y0 - 13), (cx, y0 - 6)], fill=INK)
    fc = font(17)
    draw.text((x0, y1 + 12), "0 s", font=fc, fill=FAINT)
    rt = "%g s" % round(cycle_s, 1)
    draw.text((x1 - text_w(draw, rt, fc), y1 + 12), rt, font=fc, fill=FAINT)
    mid = caption_extra or (("%d cycles averaged" % n_cycles) if n_cycles else "")
    if mid:
        draw.text(((x0 + x1) / 2 - text_w(draw, mid, fc) / 2, y1 + 12), mid, font=fc, fill=FAINT)


def build_frame(cam_rgb, *, title, now_line, t_label, speedup, lit, grid, key, sched, foot=None,
                die_note=None):
    """One 768x960 frame: the camera panel on top, the die map and the read-out below."""
    img = Image.new("RGB", (FRAME_W, FRAME_H), PANEL_BG)
    img.paste(Image.fromarray(cam_rgb), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([0, CAM_H, FRAME_W, CAM_H], fill=LINE, width=1)

    # ---- left: the die
    fh = font(19, True)
    d.text((28, PY + 4), "active shires", font=fh, fill=MUTED)
    draw_die(img, d, grid, lit, DIE_X0, DIE_Y0, DIE_CELL, DIE_GAP)
    ly = DIE_Y0 + 6 * (DIE_CELL + DIE_GAP) - DIE_GAP + 28
    fl = font(17)
    rrect(d, (DIE_X0, ly + 2, DIE_X0 + 15, ly + 17), radius=3, fill=ACCENT, outline=ACCENT)
    d.text((DIE_X0 + 22, ly), "running", font=fl, fill=MUTED)
    bx = DIE_X0 + 22 + text_w(d, "running", fl) + 22
    rrect(d, (bx, ly + 2, bx + 15, ly + 17), radius=3, fill=(249, 250, 252), outline=LINE)
    hatch(d, (bx + 1, ly + 3, bx + 14, ly + 16), LINE, step=4)
    d.text((bx + 22, ly), "no compute", font=fl, fill=MUTED)
    # The die map is in the die's frame and the picture is rolled and possibly mirrored against it,
    # so a reader who takes the map as picture-aligned reads the movie backwards.  Say so, here,
    # in MUTED - this caveat is the one piece of fine print that changes what the picture means.
    ny = ly + 24
    for line in wrap(d, die_note or DIE_NOTE, font(17), TXT_X0 - 56)[:2]:
        d.text((28, ny), line, font=font(17), fill=MUTED)
        ny += 19

    # ---- right: title, time, key, schedule - every element on a fixed line, so nothing jumps
    w = TXT_X1 - TXT_X0
    ft, lines = fit_text(d, title, w)
    y = PY + 14
    for line in lines:
        d.text((TXT_X0, y), line, font=ft, fill=INK)
        y += ft.size + 5
    if now_line:
        fn = font(21)
        d.text((TXT_X0, PY + 96), wrap(d, now_line, fn, w)[0], font=fn, fill=MUTED)
    fT, fs = font(32, True), font(20)
    d.text((TXT_X0, PY + 125), t_label, font=fT, fill=INK)
    sp = "%g x real time" % speedup
    sx = TXT_X0 + text_w(d, t_label, fT) + 16
    d.text((sx, PY + 137) if sx + text_w(d, sp, fs) <= TXT_X1 else (TXT_X0, PY + 162),
           sp, font=fs, fill=ACCENT)
    draw_key(img, d, (TXT_X0, PY + 195, TXT_X1 - 40, PY + 217), key["cmap"], key["lo"], key["hi"],
             key["caption"], signed=key.get("signed", True), ends=key.get("ends"))
    draw_schedule(d, (TXT_X0, PY + 269, TXT_X1 - 40, PY + 311), sched["edges"], sched["sets"],
                  sched["t"], sched["cycle_s"], sched.get("n_cycles"), sched.get("caption"))
    if foot:
        ff, fll = fit_text(d, foot, w, (17, 16, 15, 14), 1, bold=False)
        d.text((TXT_X0, FRAME_H - 27), fll[0], font=ff, fill=FAINT)
    return img


# ---------------------------------------------------------------- encoding

def encode(frames, path, fps, crf=23, w=FRAME_W, h=FRAME_H, poster_idx=None, contact_idx=()):
    """Pipe rgb24 frames into libx264.  Returns (n_frames, poster PIL image, {idx: PIL image})."""
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (w, h), "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(crf), "-preset", "slow",
           "-movflags", "+faststart", path]
    log = tempfile.TemporaryFile()                   # a file, not a pipe: ffmpeg can never block on it
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    poster, keep, n = None, {}, 0
    try:
        for i, im in enumerate(frames):
            arr = np.asarray(im, dtype=np.uint8)
            p.stdin.write(arr.tobytes())
            if i == poster_idx:
                poster = im.copy()
            if i in contact_idx:
                keep[i] = im.copy()
            n += 1
        p.stdin.close()
    except BrokenPipeError:
        pass
    rc = p.wait()
    log.seek(0)
    err = log.read().decode("utf8", "replace")
    log.close()
    if rc != 0:
        raise RuntimeError("ffmpeg rc=%d: %s" % (rc, err.strip()[-800:]))
    return n, poster, keep


def probe(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                          "stream=width,height,pix_fmt,avg_frame_rate,nb_frames,codec_name,profile:"
                          "format=duration,size", "-of", "json", path],
                         capture_output=True, text=True)
    try:
        j = json.loads(out.stdout)
        s = j["streams"][0]
        num, den = (s.get("avg_frame_rate") or "0/1").split("/")
        return {"codec": s.get("codec_name"), "profile": s.get("profile"),
                "w": s.get("width"), "h": s.get("height"), "pix_fmt": s.get("pix_fmt"),
                "fps": round(float(num) / float(den or 1), 3) if float(den or 0) else None,
                "frames": int(s.get("nb_frames") or 0),
                "duration_s": round(float(j["format"]["duration"]), 3),
                "bytes": int(j["format"]["size"])}
    except Exception as exc:
        return {"error": "%s: %s" % (exc, out.stderr.strip()[:200])}


def contact_sheet(keep, path, cols=3, scale=0.5, labels=None):
    """Six frames of a movie in one PNG, so a human can see at a glance if a frame is ugly."""
    ims = [keep[k] for k in sorted(keep)]
    if not ims:
        return None
    w, h = int(ims[0].width * scale), int(ims[0].height * scale)
    rows = int(math.ceil(len(ims) / cols))
    pad, lab = 8, 26
    sheet = Image.new("RGB", (cols * w + (cols + 1) * pad, rows * (h + lab) + (rows + 1) * pad), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = pad + c * (w + pad), pad + r * (h + lab + pad)
        sheet.paste(im.resize((w, h), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + w, y + h), outline=LINE)
        t = (labels or {}).get(sorted(keep)[i], "frame %d" % sorted(keep)[i])
        d.text((x + 2, y + h + 5), t, font=font(16), fill=INK)
    sheet.save(path)
    return path


# ---------------------------------------------------------------- inputs

def jread(path, default=None):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return default


def jlread(path):
    out = []
    try:
        with open(path) as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    try:
                        out.append(json.loads(ln))
                    except Exception:
                        pass
    except Exception:
        pass
    return out


def load_protocol(path, groups):
    """protocol.json -> ({block: spec}, {set: shires}).  Tolerant: anything missing falls back."""
    prot = jread(path, {}) or {}
    blocks = prot.get("blocks") or prot.get("block") or []
    if isinstance(blocks, dict):
        blocks = [dict(v, **{"block": k}) for k, v in blocks.items()]
    bl = {}
    for b in blocks:
        if not isinstance(b, dict):
            continue
        name = str(b.get("block") or b.get("name") or b.get("id") or "").strip()
        if name:
            bl[name] = b
    sets = {}
    raw_sets = prot.get("sets") or {}
    if isinstance(raw_sets, list):
        raw_sets = {str(s.get("name") or s.get("set")): s for s in raw_sets if isinstance(s, dict)}
    for k, v in raw_sets.items():
        shires = None
        if isinstance(v, dict):
            shires = v.get("shires")
            if shires is None and v.get("mask"):
                shires = [i for i in range(32) if int(str(v["mask"]), 16) >> i & 1]
        elif isinstance(v, list):
            shires = v
        if shires is not None:
            sets[str(k)] = {"shires": sorted(int(s) for s in shires),
                            "mask": (v.get("mask") if isinstance(v, dict) else None),
                            "per_shire": (v.get("per_shire") if isinstance(v, dict) else None),
                            "harts": (v.get("harts") if isinstance(v, dict) else None)}
    for k, f in (groups or {}).items():                                   # registered placements
        if k not in sets and isinstance(f, dict) and f.get("shires"):
            sets[k] = {"shires": sorted(int(s) for s in f["shires"]), "mask": f.get("mask"),
                       "per_shire": None, "harts": None}
    return bl, sets, prot


_WARNED = set()


def set_shires(name, sets):
    n = str(name).strip()
    if n in IDLE_NAMES:
        return []
    if n in sets:
        return sets[n]["shires"]
    base = n.split("@")[0]                                                # "INT16@32" -> "INT16"
    if base in sets:
        return sets[base]["shires"]
    if n.lower().startswith("0x"):
        try:
            m = int(n, 16)
            return [i for i in range(32) if m >> i & 1]
        except Exception:
            pass
    if n not in _WARNED:
        _WARNED.add(n)
        sys.stderr.write("render_hm: set %r is unknown - the die map will show nothing for it\n" % n)
    return []


def set_meta(name, sets):
    n = str(name).strip()
    m = sets.get(n) or sets.get(n.split("@")[0]) or {}
    sh = set_shires(name, sets)
    per = m.get("per_shire")
    if per is None and "@" in n and n.split("@")[1].isdigit():
        per = int(n.split("@")[1])
    return sh, m.get("mask"), per, m.get("harts")


def pretty_title(block, spec):
    for k in ("title", "label", "headline", "name"):
        if isinstance(spec, dict) and spec.get(k) and k != "name":
            return str(spec[k])
    return str(block).replace("_", " ").replace("-", " ")


# ---------------------------------------------------------------- per-block rendering

def steady_mask(t, edges, frac=0.4, min_s=2.0):
    """True for the bins in the last `frac` of each phase - the steady state the key is scaled on."""
    m = np.zeros(len(t), dtype=bool)
    for i in range(len(edges) - 1):
        a, b = float(edges[i]), float(edges[i + 1])
        cut = max(a, b - max((b - a) * frac, min_s))
        m |= (t >= cut) & (t < b)
    return m if m.any() else np.ones(len(t), dtype=bool)


def pick_speedup(cycle_s, fps, target=14.0, lo=10.0, hi=20.0):
    ok = [s for s in SPEEDUPS if lo <= cycle_s / s <= hi]
    if ok:
        return min(ok, key=lambda s: abs(cycle_s / s - target))
    return min(SPEEDUPS, key=lambda s: abs(cycle_s / s - target))          # clamp: nothing fits


def interp_cycle(diff, t, t_want):
    """Linear in time, wrapping at the end of the cycle (the movie is a loop)."""
    T = diff.shape[0]
    dt = float(t[1] - t[0]) if T > 1 else 0.5
    x = (np.asarray(t_want, dtype=np.float64) - float(t[0])) / dt
    i0 = np.floor(x).astype(int)
    f = (x - i0)[:, None, None]
    a, b = diff[np.mod(i0, T)], diff[np.mod(i0 + 1, T)]
    return a * (1.0 - f) + b * f


def first(d, *keys):
    """The first of `keys` present and numeric in dict `d` - the producers' names come first."""
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v):
            return float(v)
    return None


def phase_stat(stats, idx, name):
    """Find phase `idx` / set `name` in stats.json whatever shape analyze_hm chose."""
    if not stats:
        return {}
    cand = stats.get("phases") if isinstance(stats, dict) else None
    if cand is None and isinstance(stats, dict):
        for k in ("arms", "positions", "per_phase", "phase"):
            if isinstance(stats.get(k), (list, dict)):
                cand = stats[k]
                break
    if cand is None and isinstance(stats, list):
        cand = stats
    if isinstance(cand, dict):
        for key in (str(name), str(idx), name):
            if key in cand and isinstance(cand[key], dict):
                return cand[key]
        return {}
    if isinstance(cand, list):
        for e in cand:
            if isinstance(e, dict) and str(e.get("set") or e.get("name") or e.get("arm")) == str(name):
                return e
        if idx < len(cand) and isinstance(cand[idx], dict):
            return cand[idx]
    return {}


def fmt_stat(st):
    """One line of numbers for a map panel, printing only what analyze_hm actually wrote.

    analyze_hm's per-arm entry is `lobe_stats` output (`contrast_mk`, `frame_mean_mk`, `peak_mk`);
    a hand-written stats.json may instead use `amplitude_mk` / `monopole_mk`.  Both are read.
    """
    if not st:
        return ""
    bits = []
    amp = first(st, "amplitude_mk", "amp_mk", "amplitude", "contrast_mk")
    se = first(st, "se_mk", "amp_se_mk", "amplitude_se_mk", "se")
    p = first(st, "p", "p_perm", "permutation_p")
    if amp is not None:
        bits.append(("lobe contrast %.0f %s %.0f mK" % (amp, u"±", se)) if se is not None
                    else ("lobe contrast %.0f mK" % amp))
    if p is not None:
        bits.append("p = %.4g" % p)
    mono = first(st, "monopole_mk", "monopole", "frame_mean_mk")
    if mono is not None:
        bits.append("monopole 0 mK" if abs(mono) < 0.5 else "monopole %+.0f mK" % mono)
    return ("   %s   " % u"\u00b7").join(bits)


def block_line(st):
    """The block's own headline numbers (its primary contrast), drawn once on the maps still.

    The permutation p and the error bar belong to the block's chosen pair, not to any one arm, so
    they go here and never on a per-arm panel.
    """
    if not isinstance(st, dict):
        return ""
    bits = []
    amp = first(st, "amp_mk", "amplitude_mk", "amp_proj_mk", "amplitude")
    se = first(st, "amp_se_mk", "se_mk", "amplitude_se_mk")
    p = first(st, "p", "p_perm", "permutation_p")
    pair = st.get("contrast") if isinstance(st.get("contrast"), (list, tuple)) else None
    if amp is not None:
        lead = ("%s against %s  " % (pair[0], pair[1])) if pair and len(pair) == 2 else ""
        bits.append(lead + (("%.0f %s %.0f mK" % (amp, u"±", se)) if se is not None
                            else ("%.0f mK" % amp)))
    if p is not None:
        floor = first(st, "p_floor")
        at_floor = floor is not None and abs(p - floor) < 1e-9
        bits.append("permutation p %s %.4g" % (u"≤" if at_floor else "=", p))
    n = first(st, "n_cycles")
    if n:
        bits.append("%d cycles" % int(n))
    v = st.get("verdict")
    if isinstance(v, str) and v.strip():
        bits.append(v.strip().upper())
    return ("   %s   " % u"·").join(bits)


def render_block(block, ana_dir, sets, spec, out_dir, args, grid, stats):
    cyc = np.load(os.path.join(ana_dir, "cycle.npz"), allow_pickle=False)
    t = np.asarray(cyc["t_s"], dtype=np.float64)
    diff = np.asarray(cyc["diff_mk"], dtype=np.float32)
    edges = np.asarray(cyc["phase_edges_s"], dtype=np.float64)
    psets = [str(s) for s in np.asarray(cyc["phase_sets"]).ravel().tolist()]
    n_cycles = int(np.asarray(cyc["n_cycles"]).ravel()[0]) if "n_cycles" in cyc else None
    cycle_s = float(edges[-1] - edges[0]) if edges.size >= 2 else float(t[-1] - t[0] + 0.5)
    assert diff.shape[0] == t.size, "cycle.npz: diff_mk has %d frames, t_s %d" % (diff.shape[0], t.size)

    sm = steady_mask(t, edges, args.steady_frac)
    p98 = float(np.nanpercentile(np.abs(diff[sm]), args.pct)) if sm.any() else float(np.nanmax(np.abs(diff)))
    L = max(nice_from_list(p98), args.min_mk)
    speed = args.speedup or pick_speedup(cycle_s, args.fps)
    n_out = max(2, int(round(args.fps * cycle_s / speed)))
    # One clock for everything: the cycle's own, starting at phase_edges_s[0].  analyze_hm writes
    # t_s as bin *centres* ((i + 0.5) * bin_s), so anchoring the movie on t_s[0] would put the
    # time label half a bin behind the cursor and the schedule strip, and the strip would change
    # colour before the clock reached the phase boundary.  interp_cycle wraps, so sampling at
    # cycle time 0 is well defined.
    t0c = float(edges[0]) if edges.size else float(t[0])
    t_out = t0c + np.arange(n_out) * (cycle_s / n_out)
    seq = interp_cycle(diff, t, t_out)

    grey = scene_grey(args._scene)
    title = pretty_title(block, spec)
    if args.poster_at is not None:                  # a chosen frame beats the loudest one
        poster_idx = int(np.clip(round((float(args.poster_at) % cycle_s) / (cycle_s / n_out)),
                                 0, n_out - 1))
    else:
        score = np.sqrt(np.nanmean(seq.reshape(n_out, -1) ** 2, axis=1))
        poster_idx = int(np.argmax(score))
    contact = sorted(set(np.linspace(0, n_out - 1, 6).round().astype(int).tolist())) if args.contact else []

    def phase_of(tt):
        for i in range(min(len(psets), edges.size - 1)):
            if edges[i] <= tt < edges[i + 1]:
                return i
        return len(psets) - 1

    def frames():
        for i in range(n_out):
            tt = float(t_out[i])
            pi = phase_of(tt)
            name = psets[pi]
            sh, mask, per, harts = set_meta(name, sets)
            idle = str(name).strip() in IDLE_NAMES
            now = "idle" if idle else ("now: %s %s %d shires" % (name, u"·", len(sh)))
            if not idle and per:
                now += " %s %d harts each" % (u"×", per)
            cam = composite(seq[i], L, grey, "RdBu_r", True, args.alpha_gamma, args.max_alpha, k=3)
            yield build_frame(
                cam, title=title, now_line=now,
                t_label="t = %.1f s" % (tt - t0c), speedup=speed, lit=sh, grid=grid,
                die_note=args._die_note,
                key={"cmap": "RdBu_r", "lo": -L, "hi": L, "signed": True,
                     "caption": args.key_caption or "difference from the cycle mean",
                     "ends": ("cooler", "warmer")},
                sched={"edges": edges, "sets": psets, "t": tt, "cycle_s": cycle_s,
                       "n_cycles": n_cycles},
                foot=args.foot or "phase-averaged, 0.5 s bins, 2x2-binned pixels")

    if args.skip_movies:                                                   # stills and SVGs only
        maps_still(block, title, t, diff, edges, psets, L, sets, grid, out_dir, args, stats)
        return None
    mp4 = os.path.join(out_dir, "%s.mp4" % block)
    crf, info = args.crf, None
    for attempt in range(3):
        n, poster, keep = encode(frames(), mp4, args.fps, crf, poster_idx=poster_idx, contact_idx=contact)
        info = probe(mp4)
        if info.get("bytes", 0) <= args.max_bytes or attempt == 2:
            break
        crf += 3
        sys.stderr.write("render_hm: %s is %.2f MB, re-encoding at crf %d\n"
                         % (block, info["bytes"] / 1e6, crf))
    pj = os.path.join(out_dir, "%s-poster.jpg" % block)
    (poster or Image.new("RGB", (FRAME_W, FRAME_H), PANEL_BG)).convert("RGB").save(
        pj, quality=82, optimize=True)
    if args.contact and keep:
        contact_sheet(keep, os.path.join(out_dir, "contact", "%s.png" % block),
                      labels={k: "frame %d  t = %.1f s" % (k, t_out[k] - t0c) for k in keep})

    # ---- the steady-state map still, one panel per phase
    maps_png = maps_still(block, title, t, diff, edges, psets, L, sets, grid, out_dir, args, stats)

    return {"file": os.path.basename(mp4), "poster": os.path.basename(pj), "block": block,
            "kind": str((spec or {}).get("kind") or "swap"), "title": title,
            "duration_s": info.get("duration_s"), "speedup": speed, "fps": args.fps,
            "frames": info.get("frames") or n, "vmax_mk": L, "range_mk": [-L, L], "cmap": "RdBu_r",
            "bytes": info.get("bytes"), "crf": crf, "cycle_s": round(cycle_s, 2),
            "n_cycles": n_cycles, "sets": [s for s in dict.fromkeys(psets) if s not in IDLE_NAMES],
            "steady_p%g_mk" % args.pct: round(p98, 1), "maps": os.path.basename(maps_png) if maps_png else None,
            "poster_t_s": round(float(t_out[poster_idx] - t0c), 2),
            "probe": info, "over_budget": bool(info.get("bytes", 0) > args.max_bytes)}


def maps_still(block, title, t, diff, edges, psets, L, sets, grid, out_dir, args, stats):
    """<block>-maps.png: the steady-state difference map for each arm or position, side by side."""
    idx = list(range(min(len(psets), len(edges) - 1)))   # a short phase_edges_s must not index past itself
    panels = []
    for i in idx:
        m = (t >= max(edges[i], edges[i + 1] - max((edges[i + 1] - edges[i]) * args.steady_frac, 2.0))) \
            & (t < edges[i + 1])
        if not m.any():
            continue
        panels.append((i, psets[i], np.nanmean(diff[m], axis=0)))
    if not panels:
        return None
    pw, ph = BIN_W * 3, BIN_H * 3                                          # 384 x 288
    cols = min(len(panels), 3 if len(panels) != 4 else 2)
    rows = int(math.ceil(len(panels) / cols))
    dcell, dgap, dpad = 17, 2, 8
    dside = 6 * dcell + 5 * dgap + 2 * dpad
    pad, cap = 22, 118
    W = cols * pw + (cols + 1) * pad
    bl = block_line(stats if isinstance(stats, dict) else {})
    # The key owns the right edge, but on a one-panel still a fixed 210 px of it is half the sheet:
    # scale it with the width so the title keeps a usable column.  Measure the header on a scratch
    # canvas first, because a narrow sheet needs two lines for the caption and the caveat - and an
    # ellipsis there would eat the words that carry the meaning ("not the camera's").
    kw = 210 if W >= 760 else max(148, int(W * 0.34))
    kx0 = W - pad - kw
    hw = max(120, kx0 - pad - 18)
    nmax = 1 if W >= 760 else 2
    d0 = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    ft, tl = fit_text(d0, title, hw, (33, 30, 27, 24, 21, 19, 17), max_lines=1)
    f2, l2 = fit_text(d0, "steady-state difference from the cycle mean  %s  last %d%% of each phase"
                      % (u"·", round(args.steady_frac * 100)), hw, (19, 18, 17, 16, 15),
                      1 if W >= 760 else 3, bold=False)
    fb, lb = fit_text(d0, bl, W - 2 * pad, (20, 19, 18, 17, 16), nmax, bold=True) if bl else (None, [])
    f3, l3 = fit_text(d0, "the die sketch is drawn in the die's own frame, not the camera's "
                          "(see orientation.png)", W - 2 * pad, (18, 17, 16, 15), nmax, bold=False)
    y2, y3 = 62, 62 + len(l2) * 24
    yb, y3 = y3, y3 + (len(lb) * 24 if bl else 0)
    head = max(122, y3 + len(l3) * 22 + 14)
    H = head + rows * (ph + cap) + pad
    img = Image.new("RGB", (W, H), CARD)
    d = ImageDraw.Draw(img)
    d.text((pad, 20), tl[0], font=ft, fill=INK)
    for n, line in enumerate(l2):
        d.text((pad, y2 + n * 24), line, font=f2, fill=MUTED)
    for n, line in enumerate(lb):
        d.text((pad, yb + n * 24), line, font=fb, fill=ACCENT)
    for n, line in enumerate(l3):
        d.text((pad, y3 + n * 22), line, font=f3, fill=MUTED)
    draw_key(img, d, (kx0, 28, kx0 + kw, 50), "RdBu_r", -L, L, None,
             ends=("cooler", "warmer"), fs=17)
    grey = scene_grey(bin2(args._scene))
    for k, (i, name, dm) in enumerate(panels):
        r, c = divmod(k, cols)
        x, y = pad + c * (pw + pad), head + r * (ph + cap)
        img.paste(Image.fromarray(composite(dm, L, grey, "RdBu_r", True, args.alpha_gamma,
                                            args.max_alpha, k=3)), (x, y))
        d.rectangle((x, y, x + pw - 1, y + ph - 1), outline=LINE)
        sh, mask, per, _ = set_meta(name, sets)
        idle = str(name).strip() in IDLE_NAMES
        cx0, cy0 = x + pw - 8 - dside, y + 8                             # the die, as an inset card
        flab = font(12, True)
        rrect(d, (cx0, cy0, cx0 + dside, cy0 + dside + 17), radius=5, fill=CARD, outline=LINE)
        draw_die(img, d, grid, sh, cx0 + dpad, cy0 + dpad, dcell, dgap, label_cells=False,
                 labels_rc=False)
        d.text((cx0 + (dside - text_w(d, "die map", flab)) / 2, cy0 + dside - 1), "die map",
               font=flab, fill=FAINT)
        d.text((x, y + ph + 10), "idle" if idle else str(name), font=font(26, True), fill=INK)
        sub = "" if idle else "%d shires%s" % (len(sh), (" %s %d harts each" % (u"×", per)) if per else "")
        if mask and not idle:
            sub += "  %s  mask %s" % (u"·", mask)
        fsub, lsub = fit_text(d, sub, pw, (18, 17, 16, 15), 1, bold=False)
        d.text((x, y + ph + 42), lsub[0], font=fsub, fill=MUTED)
        st = fmt_stat(phase_stat(stats, i, name))
        if st:                                   # two lines: an ellipsis here would eat a number
            fst, lst = fit_text(d, st, pw, (19, 18, 17, 16, 15), 2, bold=False)
            for n, line in enumerate(lst):
                d.text((x, y + ph + 68 + n * 21), line, font=fst, fill=ACCENT)
    path = os.path.join(out_dir, "%s-maps.png" % block)
    img.save(path)
    return path


# ---------------------------------------------------------------- the bloom

def bloom_movie(block, spec, red, ana, sets, grid, out_dir, args, stats):
    """The one pattern-against-idle movie: all 32 shires on, dT from the pre-step baseline, inferno."""
    fr = red["frames"]
    t, mk = fr["t_s"], fr["mk"]
    ph = [p for p in red["phases"] if str(p.get("block")) == str(block)]
    on = [p for p in ph if not p.get("idle")]
    if not on:
        sys.stderr.write("render_hm: no loaded phase for the bloom block %r - skipping\n" % block)
        return None
    t0ms = red["t_start_ms"]

    def sec(p, *keys):
        for k in keys:
            if p.get(k) is not None:
                return (float(p[k]) - t0ms) / 1000.0
        return None
    t_on = min(sec(p, "t_first_start_ms", "planned_start_ms") for p in on)
    t_off = max(sec(p, "t_last_end_ms", "planned_end_ms") for p in on)
    base = (t >= t_on - args.bloom_base - 1.0) & (t <= t_on - 1.0)
    if base.sum() < 2:
        base = t <= t_on
    b = np.nanmean(mk[base], axis=0)
    w = (t >= t_on - args.bloom_pre) & (t <= t_off + args.bloom_post)
    if w.sum() < 4:
        sys.stderr.write("render_hm: the bloom window holds %d bins - skipping\n" % int(w.sum()))
        return None
    dt = mk[w] - b[None]
    tw = t[w]
    if args.bloom_gain and ana.get("gain") is not None:
        dt = dt / np.clip(ana["gain"], 0.25, 1.5)[None]
    hot = (tw >= t_off - 4.0) & (tw <= t_off)                              # the map at the end of the step
    end = dt[hot if hot.sum() >= 2 else slice(max(0, len(dt) - 8), None)].mean(axis=0)
    if args.bloom_cm:                                                      # drift out, via the coolest quarter
        ref = end <= np.nanpercentile(end, 25)
        dt = dt - np.nanmean(dt[:, ref], axis=1)[:, None, None]
        end = end - np.nanmean(end[ref])
    L = max(nice_from_list(float(np.nanpercentile(end, args.pct))), args.min_mk)

    span = float(tw[-1] - tw[0])
    speed = args.speedup or pick_speedup(span, args.fps)
    n_out = max(2, int(round(args.fps * span / speed)))
    t_out = np.linspace(tw[0], tw[-1], n_out)
    k = np.clip(np.searchsorted(tw, t_out) - 1, 0, len(tw) - 2)
    f = ((t_out - tw[k]) / np.maximum(np.diff(tw)[k], 1e-9))[:, None, None]
    seq = dt[k] * (1 - f) + dt[k + 1] * f

    name = str((on[0].get("set") or "UNI32"))
    sh, mask, per, _ = set_meta(name, sets)
    if not sh:
        sh = list(range(32))
    title = pretty_title(block, spec)
    grey = scene_grey(args._scene)
    edges = np.array([tw[0], t_on, min(t_off, tw[-1]), tw[-1]], dtype=np.float64)
    edges = np.maximum.accumulate(edges)
    psets = ["idle", name, "idle"]
    poster_idx = int(np.argmax([np.nanpercentile(s, 99) for s in seq]))
    contact = sorted(set(np.linspace(0, n_out - 1, 6).round().astype(int).tolist())) if args.contact else []

    def frames():
        for i in range(n_out):
            tt = float(t_out[i])
            running = t_on <= tt < t_off
            cam = composite(seq[i], L, grey, args.bloom_cmap, False, args.bloom_gamma, 1.0, k=3)
            yield build_frame(
                cam, title=title,
                now_line=("now: %s %s all %d shires" % (name, u"·", len(sh))) if running
                         else "idle %s nothing scheduled" % u"·",
                t_label="t = %+.1f s" % (tt - t_on), speedup=speed, lit=sh if running else [], grid=grid,
                die_note=args._die_note,
                key={"cmap": args.bloom_cmap, "lo": 0, "hi": L, "signed": False,
                     "caption": "warmer than before the step", "ends": ("no change", "hottest")},
                sched={"edges": edges, "sets": psets, "t": tt, "cycle_s": span,
                       "caption": "t = 0 is load on"},
                foot="single pass %s baseline: the %g s before load on" % (u"·", args.bloom_base))

    mp4 = os.path.join(out_dir, "%s.mp4" % block)
    crf, info = args.crf, None
    for attempt in range(3):
        n, poster, keep = encode(frames(), mp4, args.fps, crf, poster_idx=poster_idx, contact_idx=contact)
        info = probe(mp4)
        if info.get("bytes", 0) <= args.max_bytes or attempt == 2:
            break
        crf += 3
    pj = os.path.join(out_dir, "%s-poster.jpg" % block)
    (poster or Image.new("RGB", (FRAME_W, FRAME_H), PANEL_BG)).convert("RGB").save(
        pj, quality=82, optimize=True)
    if args.contact and keep:
        contact_sheet(keep, os.path.join(out_dir, "contact", "%s.png" % block),
                      labels={i: "frame %d  t = %+.1f s" % (i, t_out[i] - t_on) for i in keep})
    return {"file": os.path.basename(mp4), "poster": os.path.basename(pj), "block": block,
            "kind": "bloom", "title": title, "duration_s": info.get("duration_s"), "speedup": speed,
            "fps": args.fps, "frames": info.get("frames") or n, "vmax_mk": L, "range_mk": [0, L],
            "cmap": args.bloom_cmap, "bytes": info.get("bytes"), "crf": crf,
            "window_s": [round(float(tw[0]), 2), round(float(tw[-1]), 2)], "t_on_s": round(t_on, 2),
            "t_off_s": round(t_off, 2), "sets": [name], "n_cycles": 1,
            "notes": "dT from the pre-step baseline" + ("; common mode from the coolest quarter removed"
                                                        if args.bloom_cm else ""),
            "probe": info, "over_budget": bool(info.get("bytes", 0) > args.max_bytes)}


# ---------------------------------------------------------------- orientation and the set SVGs

def orientation_png(ori, out_dir, args, grid):
    """orientation.png: which way the die's rows and columns run in the picture."""
    path = os.path.join(out_dir, "orientation.png")
    img = Image.new("RGB", (FRAME_W, CAM_H + 230), PANEL_BG)
    img.paste(Image.fromarray(up(scene_grey(args._scene, out=(78, 206)), 3)), (0, 0))
    d = ImageDraw.Draw(img)
    d.line([0, CAM_H, FRAME_W, CAM_H], fill=LINE, width=1)

    def vec(key, *alts):
        for k in (key,) + alts:
            v = (ori or {}).get(k)
            if isinstance(v, dict):
                v = [v.get("x"), v.get("y")]
            if isinstance(v, (list, tuple)) and len(v) >= 2 and all(isinstance(q, (int, float)) for q in v[:2]):
                n = math.hypot(float(v[0]), float(v[1])) or 1.0
                return (float(v[0]) / n, float(v[1]) / n)
        return None
    # analyze_hm.fit_orientation writes row_unit_xy / col_unit_xy; the rest are older spellings.
    row = vec("row_unit_xy", "row", "r_hat", "row_hat", "plus_row", "row_vec", "e_row")
    col = vec("col_unit_xy", "col", "c_hat", "col_hat", "plus_col", "col_vec", "e_col")
    cx, cy, Ls = FRAME_W / 2, CAM_H / 2, 170

    def arrow(v, label, colour):
        if v is None:
            return
        ex, ey = cx + v[0] * Ls, cy + v[1] * Ls
        ang = math.atan2(ey - cy, ex - cx)
        for wid, col in ((9, CARD), (5, colour)):                          # a white halo under the shaft
            d.line([cx, cy, ex, ey], fill=col, width=wid)
            for s in (+1, -1):
                d.line([ex, ey, ex - 22 * math.cos(ang - s * 0.42), ey - 22 * math.sin(ang - s * 0.42)],
                       fill=col, width=wid)
        f = font(24, True)
        tw, th = text_w(d, label, f), f.size * 1.3
        px, py = -v[1], v[0]                               # step off the shaft, not along it
        # Keep the whole label on one side of the shaft: a label centred on the offset point still
        # straddles a near-vertical arrow, and a 2 px halo does not make text over its own
        # arrowhead readable.
        ox = cx + v[0] * (Ls + 18) + px * 30
        oy = cy + v[1] * (Ls + 18) + py * 30
        tx = ox - tw if px < 0 else ox
        ty = oy - th if py < -0.5 else (oy if py > 0.5 else oy - th / 2)
        tx = min(max(tx, 10), FRAME_W - tw - 10)
        ty = min(max(ty, 10), CAM_H - th - 8)
        halo_text(d, (tx, ty), label, f, colour)
    if row is not None and col is not None:                                # the die itself, as a sketch
        ov = Image.new("RGBA", (FRAME_W, CAM_H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        pit = 30.0

        def corner(r, c):
            return (cx + (r - 3) * pit * row[0] + (c - 3) * pit * col[0],
                    cy + (r - 3) * pit * row[1] + (c - 3) * pit * col[1])
        for a, b in ([((r, 0), (r, 6)) for r in range(7)] + [((0, c), (6, c)) for c in range(7)]):
            od.line([corner(*a), corner(*b)], fill=(255, 255, 255, 150), width=4)
        for a, b in ([((r, 0), (r, 6)) for r in range(7)] + [((0, c), (6, c)) for c in range(7)]):
            od.line([corner(*a), corner(*b)], fill=INK + (130,), width=1)
        od.line([corner(0, 0), corner(0, 6)], fill=ACCENT + (210,), width=3)
        img.paste(ov, (0, 0), ov)
        halo_text(d, corner(0, 0), "r0", font(17, True), ACCENT)
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=INK, outline=CARD, width=2)
    arrow(row, "+row  r0 to r5", ACCENT)
    arrow(col, "+col  c1 to c6", (31, 111, 139))
    if row is None and col is None:
        why = str((ori or {}).get("why") or "")
        halo_text(d, (24, 24), "the die's direction was not fitted" + ((": " + why) if why else ""),
                  font(24, True), ACCENT)

    y = CAM_H + 16
    d.text((24, y), "Which way the die lies in the picture", font=font(30, True), fill=INK)
    y += 40
    bits = []
    if (ori or {}).get("fitted") is False:
        bits.append("not fitted" + ((": %s" % ori["why"]) if ori.get("why") else ""))
    roll = first(ori, "roll_deg", "roll")
    droll = first(ori, "roll_deg_sd", "roll_deg_sigma", "roll_sigma", "roll_err", "circular_sd_deg")
    if roll is not None:
        bits.append("roll %.1f%s%s" % (roll, u"°", (" %s %.1f%s" % (u"±", droll, u"°"))
                                       if droll is not None else ""))
    mir = (ori or {}).get("mirrored", (ori or {}).get("is_mirrored"))
    ident = (ori or {}).get("mirror_identified")
    if mir is not None:
        bits.append("mirrored: %s%s" % ("yes" if mir else "no",
                                        "" if ident is not False else " (not identified)"))
    for k, lab in (("fit_from", "fitted from"), ("source", "fitted from"),
                   ("n_blocks", "blocks used"), ("n_pairs", "arm pairs used")):
        if (ori or {}).get(k) is not None:
            bits.append("%s %s" % (lab, ori[k] if not isinstance(ori[k], list) else ", ".join(map(str, ori[k]))))
            break
    d.text((24, y), ("   %s   " % u"·").join(bits) or "orientation.json was empty",
           font=font(22), fill=MUTED)
    y += 34
    for line in wrap(d, "The arrows and the 6 x 6 sketch start at the middle of the frame. "
                        "Millimetres per pixel is unmeasured, so the sketch's size is arbitrary and "
                        "no scale bar is drawn.", font(19), FRAME_W - 48):
        d.text((24, y), line, font=font(19), fill=FAINT)
        y += 26
    img = img.crop((0, 0, FRAME_W, min(img.height, int(y) + 14)))
    img.save(path)
    return path


SVG_CELL, SVG_GAP, SVG_PAD = 54, 6, 18


def set_svg(name, shires, grid, out_dir, mask=None, per=None):
    """sets/<SET>.svg: the die with this set lit, for the page.  viewBox only, so it scales."""
    os.makedirs(os.path.join(out_dir, "sets"), exist_ok=True)
    c, g, p = SVG_CELL, SVG_GAP, SVG_PAD
    gw = 6 * c + 5 * g
    x0, y0 = p + 30, p + 46
    W, H = x0 + gw + p, y0 + gw + 30 + p
    acc = "#%02x%02x%02x" % ACCENT
    ink = "#%02x%02x%02x" % INK
    mut = "#%02x%02x%02x" % MUTED
    fnt_faint = "#%02x%02x%02x" % FAINT
    ln = "#%02x%02x%02x" % LINE
    fnt = "-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,Roboto,sans-serif"
    sub = "%d shires" % len(shires) + (" %s %d harts each" % ("×", per) if per else "")
    if mask:
        sub += " · mask " + str(mask)
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="100%%" '
         'preserveAspectRatio="xMidYMid meet" role="img" aria-label="The 6 by 6 die with the %s shires lit">'
         % (W, H, name),
         '<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" '
         'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="%s" stroke-width="1.6"/>'
         '</pattern></defs>' % ln,
         '<rect width="%d" height="%d" fill="#fff"/>' % (W, H),
         '<text x="%d" y="%d" font-family="%s" font-size="26" font-weight="700" fill="%s">%s</text>'
         % (p, p + 22, fnt, ink, name),
         '<text x="%d" y="%d" font-family="%s" font-size="15" fill="%s">%s</text>'
         % (p, p + 42, fnt, mut, sub)]
    for r in range(6):
        o.append('<text x="%d" y="%.1f" font-family="%s" font-size="13" fill="%s" text-anchor="end">%s</text>'
                 % (x0 - 8, y0 + r * (c + g) + c / 2 + 5, fnt, mut,
                    ("r%d" % r) if DIE_VIEW == "die" else ("c%d" % (6 - r))))
        for cc in range(6):
            kind, shire, text = cell_kind(grid[r][cc])
            sr, sc = die_pos(r, cc)
            bx, by = x0 + sc * (c + g), y0 + sr * (c + g)
            on = kind == "shire" and shire in set(shires)
            if kind == "shire":
                o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s"/>'
                         % (bx, by, c, c, acc if on else "#fff", acc if on else ln))
            else:
                o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="#fafbfc" stroke="%s"/>'
                         '<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="url(#h)" stroke="none"/>'
                         % (bx, by, c, c, ln, bx, by, c, c))
            o.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" font-weight="600" '
                     'fill="%s" text-anchor="middle">%s</text>'
                     % (bx + c / 2, by + c / 2 + 6, fnt, 17 if kind == "shire" else 14,
                        "#fff" if on else (mut if kind == "shire" else fnt_faint), text))
    for cc in range(6):
        o.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="13" fill="%s" text-anchor="middle">'
                 '%s</text>' % (x0 + cc * (c + g) + c / 2, y0 + gw + 20, fnt, mut,
                                ("c%d" % (cc + 1)) if DIE_VIEW == "die" else ("r%d" % cc)))
    o.append('<text x="%d" y="%d" font-family="%s" font-size="13" fill="%s">%s</text>'
             % (p, H - 6, fnt, mut,
                "r0 is the die's I/O edge; hatched cells are not compute shires" if DIE_VIEW == "die"
                else "turned as the camera sees it: west to east runs up; hatched cells are not compute shires"))
    o.append('</svg>')
    path = os.path.join(out_dir, "sets", "%s.svg" % name)
    with open(path, "w") as fh:
        fh.write("\n".join(o) + "\n")
    return path


# ---------------------------------------------------------------- inputs, main

def load_red(red_dir):
    fr = np.load(os.path.join(red_dir, "frames.npz"), allow_pickle=False)
    frames = {"t_s": np.asarray(fr["t_s"], dtype=np.float64),
              "mk": np.asarray(fr["mk"], dtype=np.float32),
              "n": np.asarray(fr["n"]) if "n" in fr else None,
              "ffc": np.asarray(fr["ffc"]) if "ffc" in fr else None}
    scene = np.load(os.path.join(red_dir, "scene.npy")).astype(np.float32)
    sess = jread(os.path.join(red_dir, "session.json"), {}) or {}
    t0 = sess.get("t_start_ms")
    ph = jlread(os.path.join(red_dir, "phases.jsonl"))
    if t0 is None:                                         # fall back to the first planned start
        cands = [p.get("planned_start_ms") for p in ph if p.get("planned_start_ms")]
        t0 = min(cands) if cands else 0
    return {"frames": frames, "scene": scene, "session": sess, "t_start_ms": float(t0),
            "phases": ph, "blocks": jlread(os.path.join(red_dir, "blocks.jsonl")),
            "meta": jread(os.path.join(red_dir, "meta.json"), {}),
            "ffc": jread(os.path.join(red_dir, "ffc.json"), [])}


def main(argv=None):
    ap = argparse.ArgumentParser(description="E62: render the heat movies from ANA + RED + protocol.json")
    ap.add_argument("ana", help="the ANA directory analyze_hm.py wrote")
    ap.add_argument("--red", required=True, help="the RED directory reduce_hm.py wrote")
    ap.add_argument("--protocol", help="protocol.json (defaults to <ANA>/protocol.json or <RED>'s copy)")
    ap.add_argument("--out", required=True, help="the MOV directory to write")
    ap.add_argument("--only", action="append", default=[], help="render only this block (repeatable)")
    ap.add_argument("--bloom-block", default=None, help="which block is the bloom (default: autodetect)")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--speedup", type=float, default=None, help="force one speed-up for every movie")
    ap.add_argument("--crf", type=int, default=23)
    ap.add_argument("--max-mb", type=float, default=2.0, help="per-movie budget; over it, re-encode")
    ap.add_argument("--pct", type=float, default=98.0, help="percentile of |diff| that sets the key")
    ap.add_argument("--min-mk", type=float, default=5.0, help="floor for the colour half-range")
    ap.add_argument("--steady-frac", type=float, default=0.4, help="last fraction of a phase = steady state")
    ap.add_argument("--alpha-gamma", type=float, default=1.0)
    ap.add_argument("--max-alpha", type=float, default=0.95)
    ap.add_argument("--bloom-cmap", default="inferno")
    ap.add_argument("--bloom-gamma", type=float, default=0.85)
    ap.add_argument("--bloom-pre", type=float, default=4.0, help="seconds of movie before load on")
    ap.add_argument("--bloom-post", type=float, default=10.0, help="seconds of movie after load off")
    ap.add_argument("--bloom-base", type=float, default=12.0, help="seconds of baseline before load on")
    ap.add_argument("--bloom-gain", action="store_true", help="divide the bloom by ANA's gain map")
    ap.add_argument("--bloom-cm", dest="bloom_cm", action="store_true", default=True)
    ap.add_argument("--no-bloom-cm", dest="bloom_cm", action="store_false")
    ap.add_argument("--poster-at", type=float, default=None,
                    help="seconds into the cycle for the poster frame (default: the loudest frame)")
    ap.add_argument("--foot", default=None, help="override the footer line on the cycle movies")
    ap.add_argument("--die-view", choices=("die", "camera"), default="die",
                    help="draw the die map in its own frame (default) or turned as E62 measured the camera sees "
                         "it (west to east up, north to south right; only valid for aifoundry2's camera mount)")
    ap.add_argument("--key-caption", default=None,
                    help="override the colour key's caption on the cycle movies (default: difference from the "
                         "cycle mean); e.g. a bloom rendered as a cycle against its pre-step baseline")
    ap.add_argument("--contact", action="store_true", help="also write contact/<name>.png, 6 frames each")
    ap.add_argument("--skip-movies", action="store_true", help="stills and SVGs only")
    args = ap.parse_args(argv)
    args.max_bytes = int(args.max_mb * 1e6)

    t_run = time.time()
    ana_root, red_root, out = (os.path.abspath(args.ana), os.path.abspath(args.red),
                               os.path.abspath(args.out))
    os.makedirs(out, exist_ok=True)
    if args.contact:
        os.makedirs(os.path.join(out, "contact"), exist_ok=True)
    if not os.path.exists(FFMPEG):
        raise SystemExit("render_hm: no ffmpeg at %s (set FFMPEG=...)" % FFMPEG)

    grid, pos, groups = die_map()
    red = load_red(red_root)
    args._scene = red["scene"]
    assert args._scene.shape == (FULL_H, FULL_W), "scene.npy should be [192,256], got %s" % (args._scene.shape,)
    prot_path = args.protocol or next((p for p in (os.path.join(ana_root, "protocol.json"),
                                                   os.path.join(red_root, "protocol.json"))
                                       if os.path.exists(p)), None)
    spec_blocks, sets, prot = load_protocol(prot_path, groups)
    if not spec_blocks and isinstance(red["session"].get("protocol"), dict):
        spec_blocks, sets, prot = load_protocol(None, groups)              # keeps the placement sets
        pb = red["session"]["protocol"].get("blocks") or []
        spec_blocks = {str(b.get("block") or b.get("name")): b for b in pb if isinstance(b, dict)}
    ana = {"gain": None, "bloom_dt": None}
    for k, fn in (("gain", "gain.npy"), ("bloom_dt", "bloom_dt.npy")):
        p = os.path.join(ana_root, fn)
        if os.path.exists(p):
            ana[k] = np.load(p).astype(np.float32)
    ori = jread(os.path.join(ana_root, "orientation.json"), {})
    summary = jread(os.path.join(ana_root, "summary.json"), {})
    if not ori and isinstance((summary or {}).get("orientation"), dict):
        ori = summary["orientation"]                       # analyze_hm copies it into the summary
    # Every movie frame says how the die map relates to the picture, because it does not look like
    # it does: a set lit lower-left on the map can be the hot lobe at upper-right in the camera.
    _roll = first(ori, "roll_deg", "roll")
    _mir = (ori or {}).get("mirrored", (ori or {}).get("is_mirrored"))
    global DIE_VIEW
    DIE_VIEW = args.die_view
    if DIE_VIEW == "camera":
        args._die_note = CAMERA_DIE_NOTE
    elif _roll is not None and (ori or {}).get("fitted") is not False:
        args._die_note = ("the camera sees this map rolled %.0f%s%s, not as drawn"
                          % (_roll, u"°", ", mirrored" if _mir else ""))
    else:
        args._die_note = DIE_NOTE

    blocks = sorted(d for d in os.listdir(ana_root)
                    if os.path.exists(os.path.join(ana_root, d, "cycle.npz")))
    order = [str(b.get("block") or b.get("name")) for b in (prot.get("blocks") or [])
             if isinstance(b, dict)]
    blocks.sort(key=lambda b: (order.index(b) if b in order else len(order), b))
    bloom = args.bloom_block
    if bloom is None:
        cands = [n for n, s in spec_blocks.items() if str(s.get("kind", "")).lower() == "bloom"] \
            or [n for n in spec_blocks if "bloom" in n.lower()] \
            or [str(b.get("block")) for b in red["blocks"] if "bloom" in str(b.get("block", "")).lower()]
        bloom = cands[0] if cands else None
    if args.only:
        blocks = [b for b in blocks if b in args.only]
        if bloom not in args.only:
            bloom = None

    sumblocks = (summary or {}).get("blocks") or {}
    if isinstance(sumblocks, list):
        sumblocks = {str(e.get("block")): e for e in sumblocks if isinstance(e, dict)}

    def verdict_of(name):
        """What analyze_hm (or, failing that, the protocol) says about this block, for the page."""
        src = sumblocks.get(name) if isinstance(sumblocks.get(name), dict) else {}
        spec = spec_blocks.get(name) or {}
        out = {}
        for k in ("verdict", "predicted", "pass_rule", "p", "p_unrestricted", "dipole_deg",
                  "monopole_mk", "contrast"):
            v = src.get(k, spec.get(k))
            if v is not None:
                out[k] = v
        amp = first(src, "amp_mk", "amplitude_mk", "amp_proj_mk")
        if amp is None:
            amp = first(spec, "amp_mk", "amplitude_mk")
        if amp is not None:
            out["amplitude_mk"] = amp
        se = first(src, "amp_se_mk", "se_mk", "amplitude_se_mk")
        if se is not None:
            out["amplitude_se_mk"] = se
        return out

    movies, stills, used_sets, problems = [], [], {}, []
    for b in blocks:
        if b == bloom:
            continue                                                       # the bloom is not a cycle movie
        stats = jread(os.path.join(ana_root, b, "stats.json"), {})
        try:
            m = render_block(b, os.path.join(ana_root, b), sets, spec_blocks.get(b), out, args, grid, stats)
        except Exception as exc:
            if os.environ.get("HM_TRACE"):
                raise
            problems.append("%s: %s" % (b, exc))
            sys.stderr.write("render_hm: block %s failed: %s\n" % (b, exc))
            continue
        if m is None:                                                      # --skip-movies
            p = os.path.join(out, "%s-maps.png" % b)
            if os.path.exists(p):
                stills.append({"file": os.path.basename(p), "block": b, "kind": "steady-state maps"})
            for s in dict.fromkeys(str(x) for x in np.load(
                    os.path.join(ana_root, b, "cycle.npz"))["phase_sets"].ravel().tolist()):
                if s not in IDLE_NAMES:
                    used_sets[s] = set_meta(s, sets)
            continue
        if m.get("maps"):
            stills.append({"file": m.pop("maps"), "block": b, "kind": "steady-state maps"})
        else:
            m.pop("maps", None)
        m.update(verdict_of(b))
        movies.append(m)
        for s in m["sets"]:
            used_sets[s] = set_meta(s, sets)
        print("  %-14s %5.1f s  x%-4g %6.0f kB  %sL = %g mK  %d frames"
              % (m["file"], m["duration_s"] or 0, m["speedup"], (m["bytes"] or 0) / 1e3, u"±",
                 m["vmax_mk"], m["frames"] or 0))
    if bloom and not args.skip_movies:
        try:
            m = bloom_movie(bloom, spec_blocks.get(bloom), red, ana, sets, grid, out, args,
                            jread(os.path.join(ana_root, bloom, "stats.json"), {}))
        except Exception as exc:
            if os.environ.get("HM_TRACE"):
                raise
            problems.append("%s: %s" % (bloom, exc))
            sys.stderr.write("render_hm: the bloom failed: %s\n" % exc)
            m = None
        if m:
            m.update(verdict_of(bloom))
            movies.append(m)
            for s in m["sets"]:
                used_sets[s] = set_meta(s, sets)
            print("  %-14s %5.1f s  x%-4g %6.0f kB  0..%g mK  %d frames"
                  % (m["file"], m["duration_s"] or 0, m["speedup"], (m["bytes"] or 0) / 1e3,
                     m["vmax_mk"], m["frames"] or 0))

    op = orientation_png(ori, out, args, grid)
    stills.append({"file": os.path.basename(op), "kind": "orientation",
                   "bytes": os.path.getsize(op)})
    svgs = []
    for name, (sh, mask, per, _h) in sorted(used_sets.items()):
        p = set_svg(name, sh, grid, out, mask, per)
        svgs.append({"name": name, "file": os.path.join("sets", os.path.basename(p)),
                     "shires": sh, "n": len(sh), "mask": mask, "per_shire": per,
                     "bytes": os.path.getsize(p)})
    for s in stills:
        s.setdefault("bytes", os.path.getsize(os.path.join(out, s["file"])))

    mj = {"experiment": str(prot.get("experiment") or red["session"].get("experiment") or "E62"),
          "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "frame": [FRAME_W, FRAME_H], "fps": args.fps, "encoder":
              "libx264 yuv420p crf %d preset slow +faststart" % args.crf,
          "ana": ana_root, "red": red_root,
          "protocol": os.path.abspath(prot_path) if prot_path else None,
          "dry": bool(red["session"].get("dry")),
          "movies": movies, "stills": stills, "sets": svgs, "problems": problems,
          "render_s": round(time.time() - t_run, 1)}
    with open(os.path.join(out, "movies.json"), "w") as fh:
        json.dump(mj, fh, indent=1)
    big = [m["file"] for m in movies if m.get("over_budget")]
    print("render_hm: %d movies, %d stills, %d set SVGs -> %s  (%.0f s)"
          % (len(movies), len(stills), len(svgs), out, time.time() - t_run))
    if big:
        print("render_hm: over the %.1f MB budget: %s" % (args.max_mb, ", ".join(big)))
    if problems:
        print("render_hm: problems: " + "; ".join(problems))
    return 1 if (problems and not movies) else 0


if __name__ == "__main__":
    sys.exit(main())
