#!/usr/bin/env python3
"""Synthetic dtf-cam passes for testing cam_reduce.py: real file formats, a planted moving lobe, known truth.

    python3 synth_cam.py --out <dir> [--passes 4] [--amp-mk 120] [--shift-px 9] [--drift-mk-s 2.92]
        [--noise-mk 3.6] [--fixed-pattern-c 0.6] [--rate 0.45] [--seed 1] [--null]

Writes, per pass, exactly what the campaign writes:
  <dir>/frames/p<N>/f<epoch_ms>.csv   192 lines x 256 comma-separated degC, as /frame.csv
  <dir>/frames/p<N>/frames.jsonl      camera_poll.py's index ({t0,t1,bytes,ok,n,file,...})
  <dir>/marks/p<N>/marks.jsonl        run_dtf.py's marks (heater + burnin + 20 "run" lines of the four d7 items)
and <dir>/truth.json.

The scene copies what the camera actually sees (measured 21 Oct 2026 00:3x PDT: a ~41.6 degC field): an ambient
plateau, a warmer rectangular card, a fixed pattern of 0.6 degC p-p (~17x the frame noise), a whole-field linear
drift of 2.92 mK/s, and per-pixel white noise of 3.6 mK. On top of that, a Gaussian lobe on the card whose CENTRE
MOVES by --shift-px between the W-side and E-side blocks of the hi arm, with amplitude --amp-mk; the lo arm gets
the same lobe at a quarter of the amplitude and NO movement, as the quiet control. Side order alternates
W-first / E-first between passes, exactly as plan §10(a) prescribes.

`--null` plants no side effect at all (same lobe, same place, both sides): the p-values must then be uniform-ish,
which is the test that the reduction's null is calibrated rather than merely tight.
"""
import argparse
import json
import math
import os

import numpy as np

H, W = 192, 256
ITEMS_HI = ("d7w_hi", "d7e_hi")
ITEMS_LO = ("d7w_lo", "d7e_lo")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--passes", type=int, default=4)
    p.add_argument("--runs-per-block", type=int, default=5)
    p.add_argument("--run-s", type=float, default=4.3, help="the launch window of one run")
    p.add_argument("--gap-s", type=float, default=6.3, help="the wait between runs (E60 measured 10.6 s per run)")
    p.add_argument("--rate", type=float, default=0.45, help="frames per second (measured 393,216 B in 1.03-1.30 s)")
    p.add_argument("--amp-mk", type=float, default=120.0, help="lobe amplitude on the back of the board")
    p.add_argument("--shift-px", type=float, default=9.0, help="how far the lobe moves between W and E")
    p.add_argument("--sigma-px", type=float, default=18.0, help="lobe width (a shire arrives as a 3-5 cm blob)")
    p.add_argument("--drift-mk-s", type=float, default=2.92, help="whole-field drift (measured 20 Oct)")
    p.add_argument("--noise-mk", type=float, default=3.6, help="per-pixel frame-to-frame noise")
    p.add_argument("--fixed-pattern-c", type=float, default=0.6, help="fixed pattern across the frame, p-p")
    p.add_argument("--ambient-c", type=float, default=41.6)
    p.add_argument("--card-c", type=float, default=3.2, help="how much warmer the card is than ambient")
    p.add_argument("--card", default="70,50,190,140", help="card rectangle x0,y0,x1,y1")
    p.add_argument("--tau-s", type=float, default=25.0, help="thermal time constant of the board's back")
    p.add_argument("--mode", choices=("lobe", "halves"), default="lobe",
                   help="lobe = a Gaussian blob that MOVES --shift-px between the sides (tests the displacement); "
                        "halves = the loud half of the card is hot and the quiet half is not, which is what "
                        "driving 512 harts on one side of the die actually looks like (tests the double difference)")
    p.add_argument("--lo-scale", type=float, default=0.25, help="the lo arm's amplitude, at its OWN side's place")
    p.add_argument("--null", action="store_true", help="plant NO side effect (calibration test)")
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()

    rng = np.random.default_rng(a.seed)
    os.makedirs(a.out, exist_ok=True)
    x0, y0, x1, y1 = [int(v) for v in a.card.split(",")]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    card = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)

    base = np.full((H, W), a.ambient_c)
    base[card] += a.card_c
    fixed = a.fixed_pattern_c * (rng.random((H, W)) - 0.5)        # a fixed pattern, identical in every frame
    base = base + fixed

    cxw = x0 + 0.30 * (x1 - x0)                                    # the W lobe centre
    cxe = cxw + (0.0 if a.null else a.shift_px)                    # the E lobe centre
    cy = y0 + 0.5 * (y1 - y0)

    def lobe(cx):
        g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2.0 * a.sigma_px ** 2)))
        return np.where(card, g, 0.0)

    if a.mode == "lobe":
        lob = {"W": lobe(cxw), "E": lobe(cxe)}
    else:
        xmid = 0.5 * (x0 + x1)                                     # the half-vs-half pattern, blurred by the board
        halfw = np.where(card & (xx <= xmid), 1.0, 0.0)
        halfe = np.where(card & (xx > xmid), 1.0, 0.0)
        k = np.exp(-((xx - xx.mean()) ** 2 + (yy - yy.mean()) ** 2) / (2.0 * a.sigma_px ** 2))
        k = k / k.sum()
        fk = np.fft.rfft2(np.fft.ifftshift(k))
        lob = {"W": np.fft.irfft2(np.fft.rfft2(halfw) * fk, s=halfw.shape),
               "E": np.fft.irfft2(np.fft.rfft2(halfe) * fk, s=halfe.shape)}
        if a.null:
            lob["E"] = lob["W"]

    t = 1792640000.0                                               # an arbitrary but realistic epoch
    truth = {"args": vars(a), "card_xyxy": [x0, y0, x1, y1], "lobe_w_cx": cxw, "lobe_e_cx": cxe,
             "lobe_cy": cy, "planted_shift_px": 0.0 if a.null else a.shift_px, "passes": []}
    for pi in range(1, a.passes + 1):
        order = (["W", "E"] if pi % 2 else ["E", "W"])             # plan §10(a): alternate the side order
        fdir = os.path.join(a.out, "frames", "p%d" % pi)
        mdir = os.path.join(a.out, "marks", "p%d" % pi)
        os.makedirs(fdir, exist_ok=True)
        os.makedirs(mdir, exist_ok=True)
        marks = open(os.path.join(mdir, "marks.jsonl"), "w")
        index = open(os.path.join(fdir, "frames.jsonl"), "w")
        t_pass0 = t
        marks.write(json.dumps({"kind": "heater", "item": "burnin", "block": -1,
                                "t_start_ms": int(t * 1000), "t_end_ms": int((t + 2.2) * 1000),
                                "die_c": 58.0, "rc": 0}) + "\n")
        t += 3.0
        runs = []
        for arm, items in (("hi", ITEMS_HI), ("lo", ITEMS_LO)):
            for side in order:
                item = items[0] if side == "W" else items[1]
                for k in range(a.runs_per_block):
                    runs.append({"item": item, "arm": arm, "side": side, "t0": t, "t1": t + a.run_s,
                                 "pos": len(runs)})
                    marks.write(json.dumps({"kind": "run", "item": item, "block": 1,
                                            "t_start_ms": int(t * 1000), "t_end_ms": int((t + a.run_s) * 1000),
                                            "pos": len(runs) - 1, "attempt": 1, "rc": 0, "launches": 12,
                                            "start_c": 58.0, "start_hot_c": 60.0, "heats": 0,
                                            "wait_s": 0.5, "on_protocol": True}) + "\n")
                    t += a.run_s + a.gap_s
        marks.close()
        t_end = t + 2.0

        # The board's back answers the load with a first-order lag (dT/dt = (P - T)/tau): the response at tq is
        # the run envelope convolved with exp(-s/tau)/tau, which for a run [t0, t1] integrates in closed form.
        # Dividing by the duty cycle makes 1.0 mean "a long block of that side at full load".
        duty = a.run_s / (a.run_s + a.gap_s)

        def heat(tq, side, arm):
            s = 0.0
            for r in runs:
                if r["side"] != side or r["arm"] != arm or r["t0"] >= tq:
                    continue
                hi = min(tq, r["t1"])
                s += math.exp(-(tq - hi) / a.tau_s) - math.exp(-(tq - r["t0"]) / a.tau_s)
            return s / duty

        rowfmt = ",".join(["%.4f"] * W) + "\n"
        n = 0
        tq = t_pass0 + rng.random() / max(1e-6, a.rate)
        while tq < t_end:
            img = base + (a.drift_mk_s / 1000.0) * (tq - t_pass0)
            for arm, scale in (("hi", 1.0), ("lo", a.lo_scale)):
                for side in ("W", "E"):
                    h = heat(tq, side, arm)
                    if h:                       # the lo arm heats its OWN side's place, as the same shire mask does
                        img = img + (a.amp_mk / 1000.0) * scale * h * lob[side]
            img = img + (a.noise_mk / 1000.0) * rng.standard_normal((H, W))
            t1 = tq + 1.03 + 0.27 * rng.random()
            name = "f%d.csv" % int(tq * 1000)
            with open(os.path.join(fdir, name), "w") as fh:
                fh.write("".join(rowfmt % tuple(row) for row in img))
            nbytes = os.path.getsize(os.path.join(fdir, name))
            n += 1
            index.write(json.dumps({"t0": tq, "t1": t1, "bytes": nbytes, "ok": True, "n": n, "file": name,
                                    "http": 200, "err": None, "slow": False}) + "\n")
            tq = t1 + max(0.0, 1.0 / max(1e-6, a.rate) - (t1 - tq))
        index.close()
        truth["passes"].append({"pass": "p%d" % pi, "order": order, "frames": n,
                                "t0": t_pass0, "t1": t_end, "runs": len(runs)})
        t = t_end + 20.0
    with open(os.path.join(a.out, "truth.json"), "w") as fh:
        json.dump(truth, fh, indent=1)
    print("wrote %d passes under %s (%d frames total)"
          % (a.passes, a.out, sum(p_["frames"] for p_ in truth["passes"])))
    print("planted: mode %s, amp %.0f mK, shift %.1f px, lo x%.2f, drift %.2f mK/s, noise %.1f mK, null=%s"
          % (a.mode, a.amp_mk, truth["planted_shift_px"], a.lo_scale, a.drift_mk_s, a.noise_mk, a.null))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
