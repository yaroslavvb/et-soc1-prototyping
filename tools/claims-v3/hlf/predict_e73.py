#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""E73: the frozen predictions - the drive's own spectrum, and the two rival heat paths.

    python3 predict_e73.py --protocol protocol-e73.json --out predictions.json

Run and committed BEFORE the first launch.  Nothing here reads E73 data; everything is computed from
the planned timing in the protocol and from two numbers already in the repo:

  * E63's registered fundamental, pooled over its four top-rung blocks (Q126):
        H(0.05 Hz) = 52.71 +- 1.98 mK/W at a lag of 95.4 deg (mean per-block lag 99.1 deg)
  * Q126's third harmonic, pooled the same way:
        H(0.15 Hz) = 18.41 +- 5.45 mK/W at a lag of 150.6 deg, ratio |H(3f)|/|H(f)| = 0.343 +- 0.104
    (docs/reports/data/2026-10-23-e63-camera-hamming-ladder/posthoc/h3-rails-pooled.json)

## The drive

A block's arms differ only inside their launch windows, and the idle tail is the same in both, so the
difference drive is u(t) - u(t - T/2) with u the N-pulse burst of one arm.  That is odd in the half
period, so it carries ONLY odd harmonics of f0 = 1/T; the common on-pattern carries the even ones and
cannot leak into f0.  `drive_amp` integrates the planned pulse train exactly, so the predicted board
amplitude at each odd harmonic follows from the measured step alone.  It is reported for the record:
every transfer point of E73 is camera-over-board at the SAME harmonic of the SAME fit, so the drive
divides out of the answer and only its size, which sets the signal-to-noise, matters.

## The two rival heat paths, each with two free parameters fitted to the two existing points

**M1, one pole and a transport delay.** H(f) = G / (1 + i 2 pi f tau) * exp(-i 2 pi f Td).  tau comes
from the measured magnitude ratio |H(3f)|/|H(f)| = 0.343 and Td from the measured lag at f = 99.1 deg.
Two parameters, three measured numbers: the ratio's own PHASE is then a prediction, and M1 gets it
right (155.8 deg predicted against 150.6 measured).

**M2, two poles, no delay.** H(f) = G / ((1 + i 2 pi f tau1)(1 + i 2 pi f tau2)).  Fitted to the two
measured LAGS (99.1 deg at f, 150.6 deg at 3f), which is where a two-pole model is least embarrassed;
the best it can do is tau1 = tau2, and the magnitude ratio is then a prediction: 0.178, which is 1.6 SE
below the measured 0.343.

**The existing two points do not settle this, and that is why E73 exists.**  A two-pole model forced
instead through the measured lag at f AND the measured magnitude ratio is not impossible - it is
degenerate: the ratio it can reach at a 99.1 deg lag is at most 0.304 (one pole running away to
infinity, contributing a clean 90 deg and a factor 1/3, the other carrying the remaining 9.1 deg), and
the measured 0.343 +- 0.104 sits 0.37 SE ABOVE that ceiling.  So two points, one of which is at the
noise floor in every single block, leave both pictures alive and one of them pinned against its own
boundary.  Only a third frequency, far enough below 0.05 Hz for the phase to be read cleanly, separates
them.

**Where they part, and why E73 can tell.**  Both models bend over above 0.05 Hz, where E63 and Q126
already measured and where the camera signal is small.  Below it they separate in the one quantity a
drifting camera gain cannot touch, the PHASE: the low-frequency group delay is tau + Td = 13.7 s for M1
and tau1 + tau2 = 7.5 s for M2.  At 0.01 Hz that is a lag of 42.6 deg against 26.4 deg, and a magnitude
rise over 0.05 Hz of 3.17x against 2.25x.
"""
from __future__ import annotations

import argparse
import cmath
import json
import math

# the two measured anchors (Q126's pooled numbers; see the module docstring)
H_F_MK_W, SE_H_F = 52.7058820253343, 1.9800290175146842
LAG_F_DEG = 99.11206421624695           # the mean per-block lag at 0.05 Hz
RATIO_3F, SE_RATIO_3F = 0.3432192359564515, 0.10435780010272477
LAG_3F_DEG = 150.55585702413788
F_REF = 0.05

TAU_PULSE = 8.9                          # the planned device hold, seconds (--seconds 8.5, budget 9.5)
DWELL = 10.0


# --------------------------------------------------------------------------------------- the drive

def drive_amp(n_per_arm, k, tau=TAU_PULSE, dwell=DWELL):
    """|one-sided Fourier amplitude| of the difference drive at the k-th harmonic of f0, per unit step.

    One arm's on-pattern is n pulses of width tau at 0, dwell, ..., (n-1)*dwell inside a period
    T = 2*n*dwell; the other arm's is the same shifted by T/2.  Their difference has coefficient
    2 * (1/T) * |sum_m int_{m*dwell}^{m*dwell+tau} e^{-i 2 pi k t / T} dt| for odd k, and 0 for even k.
    A 50% square wave gives 2/pi = 0.6366; E63 (n = 1, k = 1) gives 0.627."""
    if k % 2 == 0:
        return 0.0
    T = 2.0 * n_per_arm * dwell
    w = 2.0 * math.pi * k / T
    s = 0j
    for m in range(n_per_arm):
        t0 = m * dwell
        s += (cmath.exp(-1j * w * t0) - cmath.exp(-1j * w * (t0 + tau))) / (1j * w)
    return 2.0 * abs(s) / T


# --------------------------------------------------------------------------------------- the models

def m1(f, tau, td, gain=1.0):
    return gain / (1 + 1j * 2 * math.pi * f * tau) * cmath.exp(-1j * 2 * math.pi * f * td)


def m2(f, tau1, tau2, gain=1.0):
    return gain / ((1 + 1j * 2 * math.pi * f * tau1) * (1 + 1j * 2 * math.pi * f * tau2))


def fit_m1():
    """tau from the magnitude ratio, Td from the lag at f."""
    # |H(3f)|/|H(f)| = sqrt((1+a^2)/(1+9a^2)) with a = 2 pi f tau
    r2 = RATIO_3F ** 2
    a2 = (1 - r2) / (9 * r2 - 1)
    a = math.sqrt(a2)
    tau = a / (2 * math.pi * F_REF)
    lag_pole = math.degrees(math.atan(a))
    td = (LAG_F_DEG - lag_pole) / (360.0 * F_REF)
    return tau, td


def fit_m2():
    """Two poles through the two measured lags; the best a two-pole can do is tau1 = tau2."""
    th = math.radians(LAG_F_DEG / 2.0)
    a = math.tan(th)
    tau = a / (2 * math.pi * F_REF)
    return tau, tau


def two_pole_ratio_ceiling():
    """The largest |H(3f)|/|H(f)| a two-pole model can give at a lag of LAG_F_DEG at f.

    One pole runs away (contributing 90 deg and a clean factor 1/3), the other carries the rest."""
    b = math.tan(math.radians(LAG_F_DEG - 90.0))
    return math.sqrt((1 + b * b) / (1 + 9 * b * b)) / 3.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", default="protocol-e73.json")
    ap.add_argument("--out", default="predictions.json")
    a = ap.parse_args()
    with open(a.protocol) as f:
        proto = json.load(f)

    tau1, td1 = fit_m1()
    t2a, t2b = fit_m2()
    harms = (1, 3, 5, 7, 9)

    # the step between arms, measured: E63 A1 (192 minions, 800 MHz) read 4.02 W on the board
    step_w = 4.02
    blocks = []
    freqs = {}
    for b in proto["blocks"]:
        n = int(b["n_per_arm"])
        f0 = 1.0 / (2 * n * DWELL)
        rows = []
        for k in harms:
            amp = drive_amp(n, k)
            f = k * f0
            r1 = abs(m1(f, tau1, td1)) / abs(m1(F_REF, tau1, td1))
            r2 = abs(m2(f, t2a, t2b)) / abs(m2(F_REF, t2a, t2b))
            l1 = -math.degrees(cmath.phase(m1(f, tau1, td1)))
            l2 = -math.degrees(cmath.phase(m2(f, t2a, t2b)))
            board = amp * step_w
            rows.append(dict(k=k, f_hz=f, drive_rel=amp, board_w=board,
                             M1_H_over_ref=r1, M1_lag_deg=l1,
                             M2_H_over_ref=r2, M2_lag_deg=l2,
                             M1_camera_mk=board * r1 * H_F_MK_W,
                             M2_camera_mk=board * r2 * H_F_MK_W))
            freqs.setdefault(round(f, 6), []).append(f"{b['id']}:k{k}")
        blocks.append(dict(id=b["id"], n_per_arm=n, lap_s=2 * n * DWELL, f0_hz=f0,
                           laps_total=b["cycles"], laps_analysed=b["cycles"] - b["warmup_cycles"],
                           analysed_s=(b["cycles"] - b["warmup_cycles"]) * 2 * n * DWELL,
                           harmonics=rows))

    out = dict(
        experiment="E73", request="Q129",
        frozen="Tue 27 Oct 2026 (week 44), before the first launch",
        anchors=dict(H_f_mk_per_w=H_F_MK_W, se_H_f=SE_H_F, lag_f_deg=LAG_F_DEG, f_ref_hz=F_REF,
                     ratio_3f_over_f=RATIO_3F, se_ratio=SE_RATIO_3F, lag_3f_deg=LAG_3F_DEG,
                     board_step_w=step_w,
                     source=("docs/reports/data/2026-10-23-e63-camera-hamming-ladder/posthoc/"
                             "h3-rails-pooled.json (Q126) and E63 A1's measured 4.02 W step")),
        models=dict(
            M1=dict(name="one pole and a transport delay", tau_s=tau1, delay_s=td1,
                    group_delay_s=tau1 + td1,
                    fitted_to="the magnitude ratio 0.343 (tau) and the lag 99.1 deg at f (Td)",
                    predicted_lag_3f_deg=-math.degrees(cmath.phase(m1(3 * F_REF, tau1, td1))),
                    measured_lag_3f_deg=LAG_3F_DEG),
            M2=dict(name="two poles, no delay", tau1_s=t2a, tau2_s=t2b, group_delay_s=t2a + t2b,
                    fitted_to="the two measured lags, 99.1 deg at f and 150.6 deg at 3f",
                    predicted_ratio_3f=abs(m2(3 * F_REF, t2a, t2b)) / abs(m2(F_REF, t2a, t2b)),
                    measured_ratio_3f=RATIO_3F, se_measured_ratio=SE_RATIO_3F,
                    sigma_low=((RATIO_3F - abs(m2(3 * F_REF, t2a, t2b)) /
                                abs(m2(F_REF, t2a, t2b))) / SE_RATIO_3F),
                    ratio_ceiling_if_forced_through_lag=two_pole_ratio_ceiling(),
                    ceiling_note=("a two-pole model made to give 99.1 deg at f cannot give a magnitude "
                                  "ratio above this; the measured 0.343 +- 0.104 sits 0.37 SE above it, "
                                  "so the existing two points leave a two-pole picture alive but pinned "
                                  "against its own boundary (one pole running away to infinity)"),
                    sigma_above_ceiling=(RATIO_3F - two_pole_ratio_ceiling()) / SE_RATIO_3F),
            discriminator=dict(
                quantity="the low-frequency group delay, read off the phase, which the camera's "
                         "drifting gain cannot touch",
                M1_group_delay_s=tau1 + td1, M2_group_delay_s=t2a + t2b,
                lag_at_0p01_M1_deg=-math.degrees(cmath.phase(m1(0.01, tau1, td1))),
                lag_at_0p01_M2_deg=-math.degrees(cmath.phase(m2(0.01, t2a, t2b))),
                H_over_ref_at_0p01_M1=abs(m1(0.01, tau1, td1)) / abs(m1(F_REF, tau1, td1)),
                H_over_ref_at_0p01_M2=abs(m2(0.01, t2a, t2b)) / abs(m2(F_REF, t2a, t2b)))),
        blocks=blocks,
        frequency_grid={str(k): v for k, v in sorted(freqs.items())},
        rules=dict(
            R1=("E73-F10's ROI fundamental (0.01 Hz) is at least 3 SE from zero with sign-flip "
                "p <= 0.01, and its board fundamental at least 5 SE. Otherwise the 0.01 Hz point is "
                "reported as a non-detection and R3/R4 are not scored."),
            R2=("the three 0.05 Hz reference blocks' |H| agree with a straight line in time within "
                "3 SE each; that line is what every ratio to 0.05 Hz is taken against, and its "
                "slope is the session's gain drift."),
            R3=("the heat path is low-pass: |H(0.025)|/|H_ref(0.05)| > 1 and "
                "|H(0.01)|/|H_ref(0.05)| > |H(0.025)|/|H_ref(0.05)|, each by at least 1 SE. "
                "A flat or falling ratio refutes the picture E63 built."),
            R4=("the discriminator, which has no PASS: the measured lag at 0.01 Hz is compared with "
                "M1's 42.6 deg and M2's 26.4 deg, and the surviving model is named. Both may fail."),
            R5=("0.05 Hz, measured twice over: E73-F10's fifth harmonic agrees with the reference "
                "line's H(0.05) within 3 SE of the complex difference."),
            R6=("hold: at least 95% of the in-launch telemetry samples of every block's analysed laps "
                "read 790 MHz or more, and the block's die mean stays under 65 C. The per-launch "
                "one-second dips are counted and reported WITHOUT a verdict, which is E63's lesson: "
                "a per-launch gate fails on the governor's idle-reset dip at any load."),
            inclusion=("a transfer point enters the across-frequency fit only when its board amplitude "
                       "is at least 5 SE; otherwise the ratio's denominator is unstable. Points that "
                       "fail it are published with their errors and left out of the fit.")),
    )
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    print(f"M1: tau {tau1:.3f} s, delay {td1:.3f} s, group delay {tau1+td1:.2f} s; "
          f"predicted lag(3f) {out['models']['M1']['predicted_lag_3f_deg']:.1f} deg "
          f"(measured {LAG_3F_DEG:.1f})")
    print(f"M2: tau1 = tau2 = {t2a:.3f} s, group delay {t2a+t2b:.2f} s; "
          f"predicted ratio(3f) {out['models']['M2']['predicted_ratio_3f']:.3f} "
          f"(measured {RATIO_3F:.3f} +- {SE_RATIO_3F:.3f}, "
          f"{out['models']['M2']['sigma_low']:.1f} SE); two-pole ceiling at that lag "
          f"{two_pole_ratio_ceiling():.3f} ("
          f"{out['models']['M2']['sigma_above_ceiling']:+.2f} SE)")
    print(f"at 0.01 Hz: M1 lag {out['models']['discriminator']['lag_at_0p01_M1_deg']:.1f} deg, "
          f"|H|/ref {out['models']['discriminator']['H_over_ref_at_0p01_M1']:.2f}; "
          f"M2 lag {out['models']['discriminator']['lag_at_0p01_M2_deg']:.1f} deg, "
          f"|H|/ref {out['models']['discriminator']['H_over_ref_at_0p01_M2']:.2f}")
    print()
    for b in out["blocks"]:
        print(f"{b['id']:10s} f0 {b['f0_hz']:.4f} Hz  analysed {b['analysed_s']/60:.1f} min")
        for r in b["harmonics"]:
            if r["drive_rel"] <= 0:
                continue
            print(f"    k{r['k']} f {r['f_hz']:.4f} Hz  drive {r['drive_rel']:.3f}  "
                  f"board {r['board_w']:.3f} W  M1 {r['M1_camera_mk']:6.1f} mK @ "
                  f"{r['M1_lag_deg']:5.1f} deg | M2 {r['M2_camera_mk']:6.1f} mK @ "
                  f"{r['M2_lag_deg']:5.1f} deg")
    print("\nwrote", a.out)


if __name__ == "__main__":
    main()
