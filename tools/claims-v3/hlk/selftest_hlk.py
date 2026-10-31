#!/usr/bin/env python3
"""E85: a synthetic session through the registered lock-in and rules (numpy only), run before the freeze.

    python3 selftest_hlk.py [--seed 85] [--laps-scale 0.5]

E63's synthetic camera (test_lockin_hlc.py: a square-wave board power of the measured shape, a first-order
lag of 15 s, a broad blob, a shutter every 2-12 s with per-pixel offset steps, a focal-plane drift that
restarts at each shutter, 34 mK frame noise), laid out as E85's seven blocks with each block's predicted
step, and two things planted that E85 must see:

  * the camera's gain DRIFTS: 60 mK/W at the start falling linearly to 45 at the end (E63's direction), so
    a kind block read against a fixed reference would be wrong by up to 25%;
  * the kinds: F32 and F16 heat the camera exactly as their watts say (true R = 1.00), but I8 is planted at
    R = 2.00 (its watts heat the camera twice as much), so E85-R2 must PASS F32 and F16 and FAIL I8.
    (A first run planted I8 at R = 1.30 and E85-R2 passed it: at E85's signal-to-noise int8's ratio has
    an SE of about 0.13 and a 3-SE tolerance of about 0.40, so the design can only flag a gross int8
    departure. That is a property of the design, said in the README, not of the code.)

Over --seeds seeds it prints the recovered R per kind against the truth (z-scores) and the verdicts, and
exits 1 if an expected verdict is wrong in any seed or the z-scores do not cover (|mean| > 1, sd > 1.6).
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
import lockin_hlk as K  # noqa: E402

L = K.L
H_, W_ = 96, 128
BIN = 0.5
STEPS = {"E85-REF1": 4.02, "E85-F32": 9.12, "E85-I8": 2.64, "E85-REF2": 4.02, "E85-F16": 7.94,
         "E85-SP90": 0.27, "E85-REF3": 4.02}
PLANT_R = {"E85-F32": 1.0, "E85-I8": 2.0, "E85-F16": 1.0, "E85-SP90": 1.0}


def blob(shape, cy, cx, sy, sx):
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    return np.exp(-0.5 * (((y - cy) / sy) ** 2 + ((x - cx) / sx) ** 2))


def make(d, proto, seed, laps_scale):
    rng = np.random.default_rng(seed)
    t0_ms = 1_800_000_000_000
    pre = 60.0
    phases, launches, sched = [], [], []
    t = pre
    blocks = []
    for b in proto["blocks"]:
        cyc = max(6, int(round(b["cycles"] * laps_scale)))
        wu = max(1, int(round(b["warmup_cycles"] * laps_scale)))
        blocks.append(dict(b, cycles=cyc, warmup_cycles=wu))
        dp = STEPS[b["id"]]
        for c in range(cyc):
            for ph in (0, 1):
                ps, ls = t, t + 0.02
                le = ls + 8.9 + rng.uniform(-0.15, 0.15)
                pe = ps + 10.0
                sname = b["phases"][ph]["set"]
                phases.append(dict(block=b["id"], cycle=c, phase=ph, slot=ph, set=sname, idle=False,
                                   planned_start_ms=t0_ms + int(ps * 1000), planned_end_ms=t0_ms + int(pe * 1000),
                                   t_first_start_ms=t0_ms + int(ls * 1000), t_last_end_ms=t0_ms + int(le * 1000),
                                   n_launches=1, warmup=c < wu, n_launch_fail=0, n_launch_short=0,
                                   stopped=None, truncated=None))
                launches.append(dict(block=b["id"], cycle=c, phase=ph, set=sname,
                                     t_start_ms=t0_ms + int(ls * 1000), t_end_ms=t0_ms + int(le * 1000), rc=0))
                sched.append((ls, le, dp if ph == 0 else 0.0, PLANT_R.get(b["id"], 1.0)))
                t = pe
    T = t + 60.0
    tb = np.arange(0.0, T, BIN) + BIN / 2
    tt = np.arange(0.0, T, 0.1)
    P = np.full(len(tt), 24.0)
    Pc = np.full(len(tt), 24.0)                       # what the camera sees: the step scaled by the planted R
    for (a, b, dp, r) in sched:
        m = (tt >= a) & (tt < b)
        ramp = np.clip((tt[m] - a) / 0.7, 0.75, 1.0)
        P[m] += (6.7 + dp) * ramp
        Pc[m] += (6.7 + dp * r) * ramp
    P_noisy = P + rng.normal(0, 0.05, len(P))
    alpha = 0.1 / 15.0
    lp = np.zeros(len(Pc))
    mean_pc = Pc.mean()
    for i in range(1, len(Pc)):
        lp[i] = lp[i - 1] + alpha * ((Pc[i] - mean_pc) - lp[i - 1])
    lp_b = np.interp(tb, tt, lp)
    gain = 60.0 + (45.0 - 60.0) * tb / T                # the drifting gain, mK per W (ROI-weighted ~1)
    G = 0.4 + 0.6 * blob((H_, W_), 30, 75, 30, 40)
    tmpl = 8000.0 * G
    sig = (gain * lp_b)[:, None, None] * G[None]
    ev, x = [], 5.0
    while x < T - 5:
        x += rng.uniform(2.0, 12.0)
        ev.append(x)
        if rng.random() < 0.25:
            x += rng.uniform(0.8, 1.6)
            ev.append(x)
    ev = np.array(ev)
    seg = np.searchsorted(ev, tb, side="right")
    nseg = len(ev) + 1
    gp = 0.7 + 0.6 * blob((H_, W_), 48, 64, 60, 80)
    F = np.cumsum(rng.normal(0, 0.8, len(tb)))
    Fseg = F - F[np.searchsorted(tb, np.concatenate([[0.0], ev]), side="left").clip(0, len(tb) - 1)][seg]
    drift = gp[None] * (Fseg + 3.0 * (tb - np.concatenate([[0.0], ev])[seg]))[:, None, None]
    offs = np.zeros((nseg, H_, W_), np.float32)
    for k in range(1, nseg):
        step = rng.normal(0, 30.0) + rng.normal(0, 25.0, (H_, W_))
        if rng.random() < 0.1:
            step += rng.uniform(1000, 3000) * blob((H_, W_), rng.uniform(0, H_), rng.uniform(0, W_), 20, 25)
        offs[k] = offs[k - 1] + step
    mk = np.empty((len(tb), H_, W_), np.float32)
    for i0 in range(0, len(tb), 500):                 # in chunks, to keep memory small
        i1 = min(len(tb), i0 + 500)
        noise = rng.normal(0, 34.0 / math.sqrt(12.5), (i1 - i0, H_, W_))
        mk[i0:i1] = 20000.0 + sig[i0:i1] + drift[i0:i1] + noise + offs[seg[i0:i1]]
    n = np.full(len(tb), 12, np.int16)
    for e in ev:
        k = int(e // BIN)
        n[max(0, k - 1):k + 1] = 3
    os.makedirs(d, exist_ok=True)
    np.savez(os.path.join(d, "frames.npz"), t_s=tb, mk=mk, n=n, ffc=np.zeros(len(tb), bool))
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
                                    temp_c=dict(minshire=[56, 56, 57]), mhz=dict(minion=800))) + "\n")
    np.save(os.path.join(d, "template.npy"), tmpl.astype(np.float32))
    p2 = dict(proto, blocks=blocks)
    with open(os.path.join(d, "protocol.json"), "w") as f:
        json.dump(p2, f)
    return os.path.join(d, "protocol.json")


def one(proto, seed, laps_scale, keep=None):
    d = keep or tempfile.mkdtemp(prefix="selftest_hlk_")
    try:
        pp = make(os.path.join(d, "red"), proto, seed, laps_scale)
        K.main([os.path.join(d, "red"), "--protocol", pp, "--predictions", os.path.join(HERE, "predictions.json"),
                "--template", os.path.join(d, "red", "template.npy"), "--out", os.path.join(d, "ana")])
        with open(os.path.join(d, "ana", "score.json")) as f:
            return json.load(f)
    finally:
        if not keep:
            shutil.rmtree(d, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=85)
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--laps-scale", type=float, default=1.0)
    ap.add_argument("--keep", default=None)
    a = ap.parse_args()
    with open(os.path.join(HERE, "protocol-e85.json")) as f:
        proto = json.load(f)
    want = {"E85-F32": "PASS", "E85-I8": "FAIL", "E85-F16": "PASS"}
    bad, zs, rows = 0, [], []
    for s in range(a.seed, a.seed + a.seeds):
        sc = one(proto, s, a.laps_scale, a.keep if s == a.seed else None)
        for k, v in want.items():
            x = sc["kinds"][k]
            z = (x["ratio_R"] - PLANT_R[k]) / x["se_R"]
            zs.append(z)
            got = sc["rules"]["E85-R2_heat_follows_watts"][k]["verdict"]
            bad += 0 if got == v else 1
            rows.append(f"  seed {s} {k}: planted R {PLANT_R[k]:.2f}, recovered {x['ratio_R']:.3f} +- {x['se_R']:.3f} "
                        f"(z {z:+.2f}); R2 {got} (expected {v}) {'ok' if got == v else 'WRONG'}")
        rl = sc["reference_line"]
        rows.append(f"  seed {s}: reference line drift {rl['drift_per_hour_frac'] * 100:.1f}%/h "
                    f"(planted 60 -> 45 mK/W of DC gain, -25% over the session); R7 "
                    f"{sc['rules']['E85-R7_reference_line']['verdict']}")
    print("\nplanted vs recovered (laps x%.2f):" % a.laps_scale)
    print("\n".join(rows))
    zs = np.array(zs)
    cover = abs(zs.mean()) <= 1.0 and zs.std() <= 1.6
    print(f"  z over {len(zs)} kind-seeds: mean {zs.mean():+.2f}, sd {zs.std():.2f}, max |z| {abs(zs).max():.2f}"
          f" -> {'covers' if cover else 'DOES NOT COVER'}")
    bad += 0 if cover else 1
    print("SELFTEST " + ("PASS" if bad == 0 else f"FAIL ({bad})"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
