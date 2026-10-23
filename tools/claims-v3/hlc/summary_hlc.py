#!/usr/bin/env python3
"""E63: derived numbers for the write-up, from the registered lock-in's output (lockin.json) and the RED.

    python3 summary_hlc.py RED ANA --out summary.json

Adds what the README lists as reported with no verdict: the price per designed flipped bit from each block's board
step (256 minions x 800 MHz / 546 cycles per op x designed B flips per op), the camera's amplitude per 10^13 flips a
second, the transfers, the shutter rate, and a plain lock-in on reduce_hm.py's bridged frames (one stretch per block,
no guard bins) beside the registered one, so the reader can see what the stretches change. numpy only.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockin_hlc as L  # noqa: E402

FLIPS_PER_OP = {"E63-TOP": 94208, "E63-TOP2": 94208, "E63-MID": 32768, "E63-NULL": 0}
CYCLES_PER_OP = 546.0
MINIONS = 256


def plain(R, block, roi, rng):
    """The same lap model with no stretches and no guard bins, on the bridged frames: what a reader would get
    by trusting reduce_hm.py's bridging."""
    laps = L.block_laps(R, block)
    okl = [x for x in laps if x[3]]
    idx, lapj, phi, _ = L.select_bins(R, laps, use_ffc=False)
    if len(idx) < 50:
        return None
    t = R["t"][idx]
    X, _ = L.design(t, lapj, phi, len(okl))
    X = X - X.mean(axis=0)
    y = R["mk"][idx][:, roi].mean(axis=1).astype(np.float64)
    z, v, _, _ = L.fit(X, (y - y.mean())[:, None], len(okl))
    w = np.where(np.isfinite(v) & (v > 0), 1.0 / v, 0.0)
    return L.lap_stats(z[:, 0], w, rng)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("red")
    ap.add_argument("ana")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    res = json.load(open(os.path.join(a.ana, "lockin.json")))
    R = L.load_red(a.red)
    rng = np.random.default_rng(63)
    roi = None
    out = dict(blocks={}, decisions=res["decisions"], registration=res.get("registration"))
    for b, r in res["blocks"].items():
        if "roi" not in r:
            continue
        if roi is None and os.path.exists(os.path.join(a.ana, f"{b}-maps.npz")):
            roi = np.load(os.path.join(a.ana, f"{b}-maps.npz"))["roi"]
        laps = L.block_laps(R, b)
        clocks = []
        for Lr in R["launches"]:
            if Lr.get("block") == b and Lr.get("mhz_minion"):
                clocks.append(Lr["mhz_minion"])
        mhz = 800.0
        flips_s = MINIONS * mhz * 1e6 / CYCLES_PER_OP * FLIPS_PER_OP.get(b, 0)
        step = r["board_step_w"]["mean"]
        rec = dict(
            laps=r["laps_analysed"], bins_kept=r["bins_kept"], bins_in_laps=r["bins_in_laps"], stretches=r["stretches"],
            board_step_w=step, board_step_se=r["board_step_w"]["se"],
            power_fundamental_w=r["power"]["amp"], power_phase_deg=r["power"]["phase_deg"],
            roi_amp_mk=r["roi"]["amp"], roi_se_mk=r["roi"]["se_along"], roi_phase_deg=r["roi"]["phase_deg"],
            roi_p=r["roi"]["p_signflip"], frame_amp_mk=r["frame"]["amp"], frame_se_mk=r["frame"]["se_along"],
            transfer_mk_per_w=(r["transfer_roi"] or {}).get("mag"), transfer_se=(r["transfer_roi"] or {}).get("se_mag"),
            lag_deg=(r["transfer_roi"] or {}).get("phase_deg"), lag_se_deg=(r["transfer_roi"] or {}).get("se_phase_deg"),
            camera_mk_per_w_step=r["roi"]["amp"] / step if step and abs(step) > 0.2 else None,
            flips_per_s=flips_s, fj_per_flip=(step / flips_s * 1e15) if flips_s else None,
            camera_mk_per_1e13_flips_s=(r["roi"]["amp"] / (flips_s / 1e13)) if flips_s else None,
            spatial=r["spatial"], ffc=r["ffc"], hold=r["hold"], fpa=r.get("fpa"),
            ffc_per_min=r["ffc"]["n_events"] / (r["laps_analysed"] * 20.0 / 60.0) if r.get("ffc") else None,
            plain_bridged=plain(R, b, roi, rng) if roi is not None else None)
        out["blocks"][b] = rec
    tops = [out["blocks"][b] for b in ("E63-TOP", "E63-TOP2") if b in out["blocks"]]
    if tops:
        out["top_pooled"] = dict(
            roi_amp_mk=float(np.mean([t["roi_amp_mk"] for t in tops])),
            board_step_w=float(np.mean([t["board_step_w"] for t in tops])),
            transfer_mk_per_w=float(np.mean([t["transfer_mk_per_w"] for t in tops])))
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    for b, x in out["blocks"].items():
        pb = x["plain_bridged"] or {}
        print(f"{b}: step {x['board_step_w']:+.3f} W, power {x['power_fundamental_w']:.3f} W; ROI {x['roi_amp_mk']:.1f} "
              f"± {x['roi_se_mk']:.1f} mK (p {x['roi_p']:.2g}), lag {x['lag_deg']}, H {x['transfer_mk_per_w']}; "
              f"fJ/flip {x['fj_per_flip']}; plain bridged {pb.get('amp', float('nan')):.1f} ± "
              f"{pb.get('se_along', float('nan')):.1f} mK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
