"""ET-SoC-1 shire tile pitch from the published die plot (IEEE Micro 2022 Fig. 7; same plot in MPR Dec 2020
Fig. 1 and Hot Chips 33 slide 20), scaled by the published 570 mm^2 die area. Writes pitch.json and an annotated PNG."""
import json
import numpy as np
from PIL import Image, ImageDraw

AREA = 570.0  # mm^2, HC33 slide 20 "Die-area: 570 mm2"; IEEE Micro 2022 "die area of 570 mm2"

def runs(prof, thr, gap=3, minlen=0):
    out = []
    for i in (i for i in range(len(prof)) if prof[i] > thr):
        if out and i - out[-1][1] <= gap: out[-1][1] = i
        else: out.append([i, i])
    return [r for r in out if r[1] - r[0] >= minlen]

def pitch(edges):
    return (edges[-1] - edges[0]) / (len(edges) - 1)

plots = {
    # name: (file, crop height, die box (left, top, right, bottom_inner, bottom_outer)) -- die box measured by
    # the inner edge of the cyan frame; the bottom has two readings (see notes): the black layout ends at
    # bottom_inner, the cyan frame's outer edge is bottom_outer.
    "micro22_fig7": ("micro22_p7-000.jpg", 1560, (20, 24, 1772, 1523, 1543)),
    "mpr2020_fig1": ("mpr_p1-002.jpg", None, (34, 33, 1486, 1276, 1291)),
    "hc33_slide20": ("hc33_p20-001.jpg", None, (6, 7, 518, 445, 451)),
}
res = {}
for name, (f, ylim, box) in plots.items():
    a = np.asarray(Image.open(f).convert("RGB")).astype(int)
    if ylim: a = a[:ylim]
    H, W, _ = a.shape
    blue = (a[:, :, 0] < 100) & (a[:, :, 1] > 120) & (a[:, :, 1] < 210) & (a[:, :, 2] > 200)
    warm = (a[:, :, 0] > 150) & (a[:, :, 2] < 120)
    # blue outline grid lines: alternate right edge of tile i / left edge of tile i+1
    v = [(r[0] + r[1]) / 2 for r in runs(blue.sum(0), 0.5 * H * 0.55, gap=2)]
    h = [(r[0] + r[1]) / 2 for r in runs(blue.sum(1), 0.5 * W * 0.55, gap=2)]
    out = {"image_px": [W, H]}
    if len(v) == 12 and len(h) == 12:
        out["outline_pitch_x_px"] = (pitch(v[0::2]) + pitch(v[1::2])) / 2
        out["outline_pitch_y_px"] = (pitch(h[0::2]) + pitch(h[1::2])) / 2
    # layout content (warm-coloured cells) of the tiles
    cx = runs(warm[int(0.22 * H):int(0.30 * H), :].mean(0), 0.3, gap=max(2, W // 600), minlen=W // 20)
    cy = runs(warm[:, int(0.24 * W):int(0.33 * W)].mean(1), 0.3, gap=max(2, W // 600), minlen=W // 20)
    if len(cx) == 6: out["content_pitch_x_px"] = (pitch([r[0] for r in cx]) + pitch([r[1] for r in cx])) / 2
    if len(cy) == 6: out["content_pitch_y_px"] = (pitch([r[0] for r in cy]) + pitch([r[1] for r in cy])) / 2
    px = np.mean([out[k] for k in ("outline_pitch_x_px", "content_pitch_x_px") if k in out])
    py = np.mean([out[k] for k in ("outline_pitch_y_px", "content_pitch_y_px") if k in out])
    l, t, r, bi, bo = box
    Wd, Hi, Ho = r - l + 1, bi - t + 1, bo - t + 1
    out.update(pitch_x_px=px, pitch_y_px=py, pitch_ratio_x_over_y=px / py, die_w_px=Wd,
               die_h_px_inner=Hi, die_h_px_outer=Ho, die_w_over_pitch_x=Wd / px,
               die_h_over_pitch_y_inner=Hi / py, die_h_over_pitch_y_outer=Ho / py, aspect_inner=Wd / Hi,
               aspect_outer=Wd / Ho, content_x_runs=cx, content_y_runs=cy)
    res[name] = out

# Scale with the Micro22 image (highest resolution), three readings of what 570 mm^2 covers
m = res["micro22_fig7"]
cases = {
    "A_black_layout_region": (m["die_w_px"], m["die_h_px_inner"]),
    "B_symmetric_bottom": (m["die_w_px"], m["die_h_px_outer"]),
    "C_including_cyan_frame": (1796, 1544),  # outer extents of the cyan frame (x 0..1795, y ~4..1547 minus 1 row)
}
scale = {}
for k, (w, hh) in cases.items():
    s = (AREA / (w * hh)) ** 0.5
    scale[k] = dict(mm_per_px=s, die_w_mm=w * s, die_h_mm=hh * s, pitch_x_mm=m["pitch_x_px"] * s,
                    pitch_y_mm=m["pitch_y_px"] * s, pitch_geomean_mm=(m["pitch_x_px"] * m["pitch_y_px"]) ** 0.5 * s,
                    grid_w_mm=6 * m["pitch_x_px"] * s, memshire_col_w_mm=(140 - 20) * s)
res["scale_from_570mm2"] = scale
json.dump(res, open("pitch.json", "w"), indent=1, default=float)
for k, v in res.items():
    print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if "runs" not in kk})

# Annotated image: die box, measured tile left/top edges (content), one-hop arrows
im = Image.open("micro22_p7-000.jpg").convert("RGB").crop((0, 0, 1800, 1560))
d = ImageDraw.Draw(im)
l, t, r, bi, bo = plots["micro22_fig7"][2]
d.rectangle((l, t, r, bi), outline=(255, 0, 255), width=3)
d.line((l, bo, r, bo), fill=(255, 0, 255), width=2)
for x0, x1 in m["content_x_runs"]:
    d.line((x0, 0, x0, 1559), fill=(255, 255, 255), width=1)
for y0, y1 in m["content_y_runs"]:
    d.line((0, y0, 1799, y0), fill=(255, 255, 255), width=1)
s = scale["A_black_layout_region"]["mm_per_px"]
cx = [(x0 + x1) / 2 for x0, x1 in m["content_x_runs"]]
cy = [(y0 + y1) / 2 for y0, y1 in m["content_y_runs"]]
d.line((cx[1], cy[2], cx[2], cy[2]), fill=(0, 255, 0), width=6)
d.line((cx[1], cy[2], cx[1], cy[3]), fill=(0, 255, 0), width=6)
d.text((cx[1] + 10, cy[2] - 30), "1 hop x ~ %.2f mm" % (m["pitch_x_px"] * s), fill=(255, 255, 255))
d.text((cx[1] + 10, cy[2] + 60), "1 hop y ~ %.2f mm" % (m["pitch_y_px"] * s), fill=(255, 255, 255))
im.save("die_plot_annotated.png")
im.resize((900, 780)).save("die_plot_annotated_small.png")
