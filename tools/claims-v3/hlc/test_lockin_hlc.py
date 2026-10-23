#!/usr/bin/env python3
"""E63: tests for lockin_hlc.py on synthetic sessions (numpy only).

    python3 test_lockin_hlc.py [--seeds 6] [--keep DIR]

A synthetic RED with E63's TOP and NULL blocks: the board power is a square wave of the measured shape
(one ~8.9 s launch per 10 s phase, the idle tail in both arms), the camera sees it through a first-order lag
(tau 15 s) times a broad blob, and on top of that every nuisance E62 met: a shutter event every 2-12 s (some in
clusters 1 s apart), each replacing the offset map with a fresh per-pixel step (median ~30 mK, one in ten of
1-3 K), a focal-plane drift that restarts at every shutter, and 34 mK of frame noise. The test plants a known
amplitude, runs the registered lock-in, and checks that (1) the TOP block's ROI amplitude and phase come back
within 3 SE of the noiseless truth, (2) the NULL block (no power difference) is flat (p >= 0.01), (3) the
SEs cover: across seeds the TOP's z-scores have |z| < 3, and (4) a bridged copy and an unbridged copy of the
same data give the same answer (the fit is blind to per-stretch offsets).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockin_hlc as L  # noqa: E402

H_, W_ = 96, 128
BIN = 0.5


def blob(shape, cy, cx, sy, sx):
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    return np.exp(-0.5 * (((y - cy) / sy) ** 2 + ((x - cx) / sx) ** 2))


def make_session(d, seed, amp_mk_per_w=40.0, dP=6.0, tau=15.0, bridged=False, ffc_on=True):
    rng = np.random.default_rng(seed)
    t0_ms = 1_800_000_000_000
    blocks = [("E63-TOP", 9 + 21, 9, dP), ("E63-NULL", 3 + 18, 3, 0.0)]
    pre = 60.0
    phases, launches = [], []
    t = pre
    sched = []                                    # (t_start, t_end, watts above the zero arm)
    for (name, cycles, wu, dp) in blocks:
        for c in range(cycles):
            for ph in (0, 1):
                ps = t
                ls = ps + 0.02
                le = ls + 8.9 + rng.uniform(-0.15, 0.15)
                pe = ps + 10.0
                phases.append(dict(block=name, cycle=c, phase=ph, slot=ph, set=("A" if ph == 0 else "B"),
                                   idle=False, planned_start_ms=t0_ms + int(ps * 1000),
                                   planned_end_ms=t0_ms + int(pe * 1000), t_first_start_ms=t0_ms + int(ls * 1000),
                                   t_last_end_ms=t0_ms + int(le * 1000), n_launches=1, warmup=c < wu,
                                   n_launch_fail=0, n_launch_short=0, stopped=None, truncated=None))
                launches.append(dict(block=name, cycle=c, phase=ph, set=("A" if ph == 0 else "B"),
                                     t_start_ms=t0_ms + int(ls * 1000), t_end_ms=t0_ms + int(le * 1000), rc=0))
                sched.append((ls, le, dp if ph == 0 else 0.0))
                t = pe
    T = t + 60.0
    tb = np.arange(0.0, T, BIN) + BIN / 2
    # board power on a 10 Hz grid: idle 23 W, a launch adds 18 W (+dP in arm A), clock ramp 0.7 s at 75%
    tt = np.arange(0.0, T, 0.1)
    P = np.full(len(tt), 23.0)
    for (a, b, dp) in sched:
        m = (tt >= a) & (tt < b)
        ramp = np.clip((tt[m] - a) / 0.7, 0.75, 1.0)
        P[m] += (18.0 + dp) * ramp
    P_noisy = P + rng.normal(0, 0.05, len(P))
    # the camera's view: first-order lag of the power above its mean, through a blob
    alpha = 0.1 / tau
    lp = np.zeros(len(P))
    for i in range(1, len(P)):
        lp[i] = lp[i - 1] + alpha * ((P[i] - 41.0) - lp[i - 1])
    lp_b = np.interp(tb, tt, lp)
    G = 0.4 + 0.6 * blob((H_, W_), 30, 75, 30, 40)            # broad, peaked: the bloom's shape
    tmpl = 8000.0 * G
    sig = amp_mk_per_w * lp_b[:, None, None] * G[None]
    # the camera's nuisances
    if ffc_on:
        ev, x = [], 5.0
        while x < T - 5:
            x += rng.uniform(2.0, 12.0)
            ev.append(x)
            if rng.random() < 0.25:
                x += rng.uniform(0.8, 1.6)
                ev.append(x)
        ev = np.array(ev)
    else:
        ev = np.zeros(0)
    seg = np.searchsorted(ev, tb, side="right")
    nseg = len(ev) + 1
    gp = 0.7 + 0.6 * blob((H_, W_), 48, 64, 60, 80)          # the focal plane's per-pixel response
    F = np.cumsum(rng.normal(0, 0.8, len(tb)))               # mK, a wandering focal-plane drift
    Fseg = F - F[np.searchsorted(tb, np.concatenate([[0.0], ev]), side="left").clip(0, len(tb) - 1)][seg]
    drift = gp[None] * (Fseg + 3.0 * (tb - np.concatenate([[0.0], ev])[seg]))[:, None, None]
    offs = np.zeros((nseg, H_, W_), np.float32)
    for k in range(1, nseg):
        step = rng.normal(0, 30.0) + rng.normal(0, 25.0, (H_, W_))
        if rng.random() < 0.1:
            step += rng.uniform(1000, 3000) * blob((H_, W_), rng.uniform(0, H_), rng.uniform(0, W_), 20, 25)
        offs[k] = offs[k - 1] + step
    noise = rng.normal(0, 34.0 / math.sqrt(12.5), (len(tb), H_, W_))
    mk = 20000.0 + sig + drift + noise + (0 if bridged else offs[seg])
    n = np.full(len(tb), 12, np.int16)
    for e in ev:                                              # the shutter's dropped and frozen frames
        k = int(e // BIN)
        n[max(0, k - 1):k + 1] = 3
    os.makedirs(d, exist_ok=True)
    np.savez_compressed(os.path.join(d, "frames.npz"), t_s=tb, mk=mk.astype(np.float32), n=n,
                        ffc=np.zeros(len(tb), bool))
    with open(os.path.join(d, "ffc.json"), "w") as f:
        json.dump([dict(t_s=float(e)) for e in ev], f)
    with open(os.path.join(d, "meta.json"), "w") as f:
        json.dump(dict(bin_s=BIN, reconnect_gaps=[]), f)
    with open(os.path.join(d, "session.json"), "w") as f:
        json.dump(dict(t_start_ms=t0_ms), f)
    for nm, rows in (("phases.jsonl", phases), ("launches.jsonl", launches)):
        with open(os.path.join(d, nm), "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    with open(os.path.join(d, "tel.jsonl"), "w") as f:
        for ti, pw in zip(tt, P_noisy):
            f.write(json.dumps(dict(t_ms=t0_ms + int(ti * 1000), board_w=float(pw),
                                    temp_c=dict(minshire=[60, 60, 61]), mhz=dict(minion=800))) + "\n")
    # the truth: the noiseless ROI series through the same lap model, no stretches
    roi = L.roi_from_template(tmpl)
    truth = {}
    R = L.load_red(d)
    for b in ("E63-TOP", "E63-NULL"):
        laps = L.block_laps(R, b)
        okl = [x for x in laps if x[3]]
        sel = np.zeros(len(tb), bool)
        for (_, a, bb, _, _) in okl:
            sel |= (tb >= a) & (tb < bb)
        i = np.nonzero(sel)[0]
        lap = np.full(len(i), -1, int)
        phi = np.zeros(len(i))
        for j, (_, a, bb, _, _) in enumerate(okl):
            m = (tb[i] >= a) & (tb[i] < bb)
            lap[m] = j
            phi[m] = 2 * math.pi * (tb[i][m] - a) / (bb - a)
        X, _ = L.design(tb[i], lap, phi, len(okl))
        X = X - X.mean(axis=0)
        y = sig[i][:, roi].mean(axis=1)
        z, v, _, _ = L.fit(X, (y - y.mean())[:, None], len(okl))
        truth[b] = complex(np.mean(z[:, 0]))
    np.save(os.path.join(d, "template.npy"), tmpl.astype(np.float32))
    return truth


def proto_file(d):
    p = dict(experiment="E63", blocks=[dict(id="E63-TOP"), dict(id="E63-NULL")])
    path = os.path.join(d, "protocol.json")
    with open(path, "w") as f:
        json.dump(p, f)
    return path


def run(d, out):
    L.main([d, "--protocol", proto_file(d), "--template", os.path.join(d, "template.npy"), "--out", out])
    with open(os.path.join(out, "lockin.json")) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--keep", default=None)
    a = ap.parse_args()
    base = a.keep or tempfile.mkdtemp(prefix="hlc-test-")
    zs, nulls, fails = [], [], []
    for s in range(a.seeds):
        d = os.path.join(base, f"s{s}")
        truth = make_session(d, s)
        res = run(d, os.path.join(d, "ANA"))
        top, nul = res["blocks"]["E63-TOP"]["roi"], res["blocks"]["E63-NULL"]["roi"]
        Z = complex(top["Z_re"], top["Z_im"])
        Zt = truth["E63-TOP"]
        se = math.sqrt(0.5 * (top["se_re"] ** 2 + top["se_im"] ** 2))
        zre, zim = (Z.real - Zt.real) / top["se_re"], (Z.imag - Zt.imag) / top["se_im"]
        zs += [zre, zim]
        nulls.append(nul["p_signflip"])
        print(f"seed {s}: TOP {abs(Z):.1f} mK at {math.degrees(math.atan2(Z.imag, Z.real)):.0f} deg vs truth "
              f"{abs(Zt):.1f} at {math.degrees(math.atan2(Zt.imag, Zt.real)):.0f} (SE {se:.1f}; z {zre:+.2f} "
              f"{zim:+.2f}); NULL {nul['amp']:.1f} mK p {nul['p_signflip']:.3f}; "
              f"rule1 {res['decisions'].get('1_top_seen', {}).get('verdict')} "
              f"rule3 {res['decisions'].get('3_null_flat', {}).get('verdict')}")
        if abs(zre) > 3 or abs(zim) > 3:
            fails.append(f"seed {s}: TOP off truth by more than 3 SE")
        if res["decisions"].get("1_top_seen", {}).get("verdict") != "PASS":
            fails.append(f"seed {s}: rule 1 did not pass on a planted signal")
    # a bridged copy (the per-stretch offsets already removed) must give the same numbers
    d0, d1 = os.path.join(base, "u"), os.path.join(base, "b")
    make_session(d0, 101, bridged=False)
    make_session(d1, 101, bridged=True)
    r0, r1 = run(d0, os.path.join(d0, "ANA")), run(d1, os.path.join(d1, "ANA"))
    z0 = complex(r0["blocks"]["E63-TOP"]["roi"]["Z_re"], r0["blocks"]["E63-TOP"]["roi"]["Z_im"])
    z1 = complex(r1["blocks"]["E63-TOP"]["roi"]["Z_re"], r1["blocks"]["E63-TOP"]["roi"]["Z_im"])
    print(f"unbridged {z0:.3f} vs bridged {z1:.3f}")
    if abs(z0 - z1) > 1e-3 * max(1.0, abs(z0)):
        fails.append("the fit is not blind to per-stretch offsets")
    zs = np.array(zs)
    print(f"z-scores over {len(zs)} components: mean {zs.mean():+.2f}, sd {zs.std():.2f}; "
          f"NULL p: {[round(p, 3) for p in nulls]}")
    if (np.array(nulls) < 0.01).sum() > 1:
        fails.append("NULL flagged in more than one seed at p < 0.01")
    if not a.keep:
        shutil.rmtree(base, ignore_errors=True)
    print("FAIL: " + "; ".join(fails) if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
