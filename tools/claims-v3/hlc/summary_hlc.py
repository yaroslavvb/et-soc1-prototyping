#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E63: derived numbers for the write-up, from the registered lock-in's output (lockin.json) and the RED.

    python3 summary_hlc.py RED ANA --out summary.json

Adds what the README lists as reported with no verdict: the price per designed flipped bit from each block's board
step (its own minions x its own clock / 546 cycles per op x designed B flips per op), the camera's amplitude per
10^13 flips a second, the transfers, the shutter rate, and a plain lock-in on reduce_hm.py's bridged frames (one
stretch per block, no guard bins) beside the registered one, so the reader can see what the stretches change.
numpy only.

The minions and the clock come from the session's own records, never from a constant here (Q126, Mon 26 Oct 2026).
Until then both were hard-coded, 256 minions and 800 MHz, and session 2 ran amendment A1's 6 minions per shire,
192 in all: its three prices were 3/4 of the truth. The clock is the MEDIAN minion MHz over the same steady windows
the board step's medians are taken in, from the 10 Hz telemetry; `launches.jsonl`'s own `mhz_minion` is read before
the launch opens and says 600 in all 360 records of both sessions, while 99.6% of the in-launch samples are at 800.
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


def minions_and_clock(R, tel, block, laps_ok):
    """How many minions this block ran on and at what clock, from the session's own records.

    minions: `harts` in the block's own launch records (`launches.jsonl`), which is what run_hlc.py passed
    to the heater; the protocol's set is the fallback. clock: the minion MHz in the same steady windows the
    board step is measured in (2.0 s after a launch starts to 0.3 s before it ends), from the 10 Hz
    telemetry. The median is the one used, because the step is itself a median over those windows; the mean
    and the share at 800 MHz go beside it, so the one-second clock dips are visible in the number."""
    cycles = {c for (c, *_r) in laps_ok}
    harts, mhz = set(), []
    for Lr in R["launches"]:
        if Lr.get("block") != block or int(Lr["cycle"]) not in cycles:
            continue
        if Lr.get("harts"):
            harts.add(int(Lr["harts"]))
        a = Lr["t_start_ms"] / 1000.0 + L.STEADY_FROM_S
        b = Lr["t_end_ms"] / 1000.0 - L.STEADY_TO_END_S
        m = (tel[:, 0] >= a) & (tel[:, 0] <= b)
        v = tel[m, 3]
        mhz += list(v[np.isfinite(v)])
    if not harts:
        for s in (R["session"].get("protocol", {}).get("sets") or {}).values():
            if s.get("harts"):
                harts.add(int(s["harts"]))
    mhz = np.array(mhz, dtype=np.float64)
    return dict(minions=(max(harts) if harts else None), minions_seen=sorted(harts),
                mhz=(float(np.median(mhz)) if len(mhz) else None),
                mhz_mean=(float(mhz.mean()) if len(mhz) else None),
                mhz_share_800=(float((mhz == 800).mean()) if len(mhz) else None),
                mhz_samples=int(len(mhz)),
                mhz_in_launch_records=sorted({float(Lr["mhz_minion"]) for Lr in R["launches"]
                                              if Lr.get("block") == block and Lr.get("mhz_minion")}))


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
    tel = L.tel_samples(a.red)
    rng = np.random.default_rng(63)
    roi = None
    out = dict(blocks={}, decisions=res["decisions"], registration=res.get("registration"))
    for b, r in res["blocks"].items():
        if "roi" not in r:
            continue
        if roi is None and os.path.exists(os.path.join(a.ana, f"{b}-maps.npz")):
            roi = np.load(os.path.join(a.ana, f"{b}-maps.npz"))["roi"]
        laps = L.block_laps(R, b)
        mc = minions_and_clock(R, tel, b, [x for x in laps if x[3]])
        mhz = mc["mhz"] or 0.0
        flips_s = (mc["minions"] or 0) * mhz * 1e6 / CYCLES_PER_OP * FLIPS_PER_OP.get(b, 0)
        step = r["board_step_w"]["mean"]
        rec = dict(
            minions=mc["minions"], mhz=mc["mhz"], clock=mc,
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
        print(f"{b}: {x['minions']} minions at {x['mhz']:.0f} MHz (mean {x['clock']['mhz_mean']:.1f}, "
              f"{100 * x['clock']['mhz_share_800']:.2f}% at 800; the launch records say "
              f"{x['clock']['mhz_in_launch_records']})")
        print(f"{b}: step {x['board_step_w']:+.3f} W, power {x['power_fundamental_w']:.3f} W; ROI {x['roi_amp_mk']:.1f} "
              f"± {x['roi_se_mk']:.1f} mK (p {x['roi_p']:.2g}), lag {x['lag_deg']}, H {x['transfer_mk_per_w']}; "
              f"fJ/flip {x['fj_per_flip']}; plain bridged {pb.get('amp', float('nan')):.1f} ± "
              f"{pb.get('se_along', float('nan')):.1f} mK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
