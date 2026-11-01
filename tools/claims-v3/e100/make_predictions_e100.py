#!/usr/bin/env python3
"""E100: the frozen predictions. A small event simulation of the chain the public firmware describes, run before any launch.

    python3 make_predictions_e100.py > predictions.txt      (writes predictions.json beside this script)

The model, nothing more than the chain in README.md:
  * a heartbeat every Q ms reads the kernel slot: busy if a kernel is in use at that instant, else idle;
  * the SP's state follows it; on a busy-to-idle edge the clock goes to 600 MHz at once;
  * while the SP's state is busy and the clock is under 800 MHz, each SP pass (every 200 ms, phase random) climbs one point;
  * a process: a device-open delay, a 20,000-iteration calibration kernel, then kernels of a fixed cycle count, with an idle window of w + g
    ms between kernels (w the firmware and host's own gap, g the added sleep, uniform in 0 to 2 x its mean), until the kernels' wall plus the sleeps reach --seconds;
  * the arm N: one kernel of 3.18 G cycles and nothing else.
A fall is any transition to 600 MHz from a higher clock, counted more than 1.5 s after the process starts and more than 0.3 s before it ends, the
window the sampler rule of E80 and of the scorer uses. The heartbeats exposed are that window's length over Q.

w is not known exactly: 2.0 ms is the width of the zone in which the committed boundaries fell (docs/reports/data/2026-11-01-q132-governor-desk),
1.29 ms the host's mean gap (a floor), 2.5 ms a generous top. Each arm is simulated at all three, and the scorer's band runs from the lower Poisson
limit at 1.3 ms to the upper Poisson limit at 2.5 ms, at the heartbeats the session really exposed.
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
Q_MS = 1000.01
PASS_MS = 200.0
FIXED_ITERS = 850000
CYCLES_PER_ITER = 318.017
CAL_ITERS = 20000
N_ITERS = 10000000
OPEN_MS = 140.0
OVERHEAD_MS = 0.47
SECONDS = 7.5
ARMS = {"A0": 0.0, "A5": 5.0, "A20": 20.0, "A100": 100.0}
N_SIM = 600
UP = {600: 700, 700: 800}
DUR = {}


def sim_process(rng, t0, phi, arm_gap, w, seconds=SECONDS, one_kernel=False, clock0=600, sp_busy0=False, q=Q_MS):
    """One process from t0 (ms): returns dict with t1, kernels [(start, end, cycles)], transitions [(t, mhz)], falls [(t, from)]."""
    clock = clock0
    sp_busy = sp_busy0
    trans = [(t0, clock)]
    falls = []
    kernels = []
    t = t0 + OPEN_MS
    next_hb = phi + q * math.ceil((t0 - phi) / q)
    next_pass = t0 + rng.uniform(0, PASS_MS)
    spent = 0.0
    queue = [CAL_ITERS * CYCLES_PER_ITER] if not one_kernel else [N_ITERS * CYCLES_PER_ITER]
    first = True
    in_kernel = False
    remaining = 0.0
    k_start = None
    k_cycles = 0.0
    idle_until = t
    done = False
    t_now = t0

    def events_until(limit):
        nonlocal next_hb, next_pass, sp_busy, clock, t_now, remaining
        while True:
            nxt = min(next_hb, next_pass)
            if nxt > limit:
                if in_kernel:
                    remaining -= (limit - t_now) * clock * 1e3
                t_now = limit
                return
            if in_kernel:
                remaining -= (nxt - t_now) * clock * 1e3
            t_now = nxt
            if nxt == next_hb:
                busy = in_kernel
                if sp_busy and not busy and clock > 600:
                    falls.append((nxt, clock))
                    clock = 600
                    trans.append((nxt + 0.005, clock))
                sp_busy = busy
                next_hb += q
            else:
                if sp_busy and clock < 800:
                    clock = UP[clock]
                    trans.append((nxt, clock))
                next_pass += PASS_MS

    # the idle time before the first kernel
    events_until(idle_until)
    while not done:
        cycles = queue.pop(0)
        in_kernel = True
        remaining = cycles
        k_start = t_now
        k_cycles = cycles
        while True:
            # the kernel's end at this clock, if nothing changes
            eta = t_now + remaining / (clock * 1e3)
            nxt = min(next_hb, next_pass)
            if eta <= nxt:
                t_now = eta
                remaining = 0.0
                break
            events_until(nxt)
        in_kernel = False
        wall = t_now - k_start + OVERHEAD_MS
        t_now += OVERHEAD_MS
        kernels.append((k_start, t_now, k_cycles))
        if one_kernel:
            break
        if first:
            first = False
        else:
            spent += wall + arm_gap  # the mean sleep, for this count only
        if spent >= seconds * 1000.0:
            break
        events_until(t_now + w + rng.uniform(0.0, 2.0 * arm_gap))
        queue.append(FIXED_ITERS * CYCLES_PER_ITER)
    t1 = t_now + 50.0
    events_until(t1)
    return {"t0": t0, "t1": t1, "kernels": kernels, "trans": trans, "falls": falls, "clock": clock, "sp_busy": sp_busy}


def rate(gap, w, one_kernel=False, n=N_SIM, seed=100):
    rng = random.Random(seed + int(gap * 10) + int(w * 100) + (7 if one_kernel else 0))
    nf = 0
    hb = 0.0
    durations = []
    for _ in range(n):
        phi = rng.uniform(0, Q_MS)
        p = sim_process(rng, 0.0, phi, gap, w, one_kernel=one_kernel, clock0=600, sp_busy0=False)
        a, b = p["t0"] + 1500.0, p["t1"] - 300.0
        hb += max(0.0, b - a) / Q_MS
        nf += sum(1 for t, _ in p["falls"] if a < t < b)
        for t, _ in p["falls"]:
            if a < t < b:
                up = next((x for x, m in p["trans"] if x > t + 1 and m > 600), None)
                if up is not None:
                    durations.append((up - t) / 1000.0)
    DUR[(gap, w)] = durations
    return nf / hb, hb / n


def poisson_lo(mu, tail=0.025):
    """The largest L with P(X < L) <= tail."""
    L = 0
    c = 0.0
    while True:
        c += math.exp(-mu) * mu ** L / math.factorial(L)
        if c > tail:
            return L
        L += 1


def poisson_hi(mu, tail=0.025):
    """The smallest H with P(X > H) <= tail."""
    H = 0
    c = math.exp(-mu)
    while 1 - c > tail:
        H += 1
        c += math.exp(-mu) * mu ** H / math.factorial(H)
    return H


def main():
    out = {"experiment": "E100", "note": "frozen before any launch; the model is in this script's docstring",
           "q_ms": Q_MS, "fixed_iters": FIXED_ITERS, "cycles_per_iter": CYCLES_PER_ITER, "n_iters": N_ITERS, "w_ms": [1.3, 2.0, 2.5], "planned_heartbeats_per_arm": 144,
           "arms": {}}
    print("arm    gap ms   analytic f(1-f), w 2.0   falls per heartbeat (simulated): w 1.3, 2.0, 2.5   heartbeats per process   falls in 144   band in 144")
    L = FIXED_ITERS * CYCLES_PER_ITER / 800e3 + OVERHEAD_MS
    for arm, g in ARMS.items():
        f = (2.0 + g) / (L + 2.0 + g)
        rr = {}
        hbp = None
        for w in (1.3, 2.0, 2.5):
            r, hbp = rate(g, w)
            rr[str(w)] = round(r, 5)
        mu_lo, mu_mid, mu_hi = rr["1.3"] * 144, rr["2.0"] * 144, rr["2.5"] * 144
        band = [poisson_lo(mu_lo), poisson_hi(mu_hi)]
        out["arms"][arm] = {"gap_ms": g, "analytic_f": round(f, 5), "analytic_rate": round(f * (1 - f), 5), "falls_per_heartbeat": rr, "heartbeats_per_process": round(hbp, 3),
                            "falls_in_144": round(mu_mid, 2), "band_in_144": band,
                            "at600_s_median": round(sorted(DUR[(g, 2.0)])[len(DUR[(g, 2.0)]) // 2], 3) if DUR[(g, 2.0)] else None,
                            "at600_share_ge_1p9_s": round(sum(1 for d in DUR[(g, 2.0)] if d >= 1.9) / len(DUR[(g, 2.0)]), 3) if DUR[(g, 2.0)] else None}
        print(f"{arm:6s} {g:6.0f}   {f * (1 - f) * 100:6.2f}%                  {rr['1.3'] * 100:5.2f}% {rr['2.0'] * 100:5.2f}% {rr['2.5'] * 100:5.2f}%               {hbp:5.2f}                 {mu_mid:6.1f}        {band[0]}-{band[1]}    at 600 MHz: median {out['arms'][arm]['at600_s_median']} s, share 1.9 s or more {out['arms'][arm]['at600_share_ge_1p9_s']}")
    out["arms"]["N"] = {"gap_ms": None, "falls_per_heartbeat": {"1.3": 0.0, "2.0": 0.0, "2.5": 0.0}, "falls_in_144": 0.0, "note": "no gap inside the kernel: zero by construction of the chain"}
    out["arms"]["R"] = dict(out["arms"]["A20"], note="A20 plus the sampler's statistics reset: the chain has no path from the reset to the kernel slot, so A20's numbers")
    print("N      none: zero falls inside the kernel, by construction of the chain")
    print("R      as A20")
    json.dump(out, open(os.path.join(HERE, "predictions.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
