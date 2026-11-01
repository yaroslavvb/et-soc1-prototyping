#!/usr/bin/env python3
"""E98 (Q132): builds predictions.json, the frozen numbers of the registration, from the constants below and nothing else. No
card and no randomness beyond the seeded power estimate. Standard library only.

    python3 make_predictions_e98.py > predictions.txt
"""
import calendar
import json
import math
import os
import random
import statistics as st
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- constants, each from the desk lane's committed post-hoc reading (docs/reports/data/2026-11-01-q132-governor-desk/)
K_LINE = 0.4573            # C per W: the line is die - K_LINE * board W (pooled within-session slope, aifoundry2, die-lines.txt)
W_PER_C_REST = 0.2315      # W per C: aifoundry2's idle W against its own idle die, 2,182 5-minute bins, r 0.978 (room-proxies.txt)
LINE_SLOPE_DESK = 0.25     # C of 76 s line per C of rest die: E64, E80, E83, E87 through E80, weighted (drift-paired.txt), n = 4, post hoc
L_800 = 0.442              # W per C at a fixed clock: E64's reference slope of board W on the die (surface_hpl.powers)
R_PATH = K_LINE            # C per W: the line's own slope, the heat path's resistance as these sessions see it
TRIP_MHZ_PER_C = -12.0     # MHz per C of rest die, fp16 ones at the trip: E64 737 MHz, E80 782 MHz over 3.7 C of rest (spec)
TRIP_W_PER_C = -1.0        # W per C of rest die at the trip: E64 49.3 W, E80 53.2 W (spec)

# Leakage feedback. A room shift d moves a state at fixed work by d / (1 - R * dP/dT): at rest dP/dT = 0.2315, on the hold 0.442.
GAIN_REST = 1.0 / (1.0 - R_PATH * W_PER_C_REST)
GAIN_HOLD = 1.0 / (1.0 - R_PATH * L_800)
HOLD_SLOPE_ROOM = GAIN_HOLD / GAIN_REST                  # C of hold die per C of rest die, if the room is the cause
HOLD_BAND = (1.0, round(GAIN_HOLD, 2))                   # 1:1 without the feedback's difference, up to the hold's whole gain
P_REST, P_HOLD = 22.1, 41.0                              # W: the idle board and int8 neg_ones (E80's 41.0 W, 60 C)
HOLD_SLOPE_PATH = HOLD_SLOPE_ROOM * P_HOLD / P_REST      # if the path's resistance moved instead: each state moves with its own watts
# On the fine reading: W at a fixed clock, as a thermometer, against W at rest (both in W, no die step in either).
HOLD_W_RATIO_ROOM = L_800 / W_PER_C_REST * HOLD_SLOPE_ROOM
HOLD_W_BAND = (round(L_800 / W_PER_C_REST * HOLD_BAND[0], 2), round(L_800 / W_PER_C_REST * HOLD_BAND[1], 2))
# The line in die - k W: a fixed-clock run's line moves (1 - k L) per C of its die, so slope s in the line is s / (1 - k L) in its die.
LINE_TO_DIE = 1.0 / (1.0 - K_LINE * L_800)
FINE_LINE_RATIO_DESK = LINE_SLOPE_DESK * LINE_TO_DIE * L_800 / W_PER_C_REST   # W at 800 MHz per W of rest W, on the desk's slope
FROM_REST_LINE_SLOPE = HOLD_SLOPE_ROOM / LINE_TO_DIE                          # the from-rest run, a linear system's 1:1, in the line's units

# ---- the rest level at the freeze: aifoundry2's own 5 s history, read 00:16:38 PDT Sun 1 Nov 2026 (five 5-minute means, -30 to -5 min)
W_NOW, DIE_NOW, NIC_NOW, NVME_NOW = 22.12, 46.6, 44.3, 37.5
T_NOW = "2026-11-01T07:05:00Z"          # 00:05 PDT, the middle of that span

# ---- nine-day hour means of the idle card (PDT hours; room-proxies.txt). Tonight sits below them; the SHAPE is what is used.
HOUR_W = {0: 22.50, 1: 22.49, 2: 22.42, 3: 22.38, 4: 22.26, 5: 22.14, 6: 22.11, 7: 22.08, 8: 22.03, 9: 21.99}
HOUR_NIC = {0: 45.88, 1: 45.74, 2: 45.56, 3: 45.39, 4: 45.04, 5: 44.62, 6: 44.44, 7: 44.30, 8: 44.10, 9: 43.97}
# ---- the seven whole nights on record: rest W at 00:30 PDT minus at 08:00 PDT (live-5min.csv; 23, 24, 25, 28, 29, 30, 31 Oct)
NIGHT_FALLS_W = [0.556, 0.859, 0.880, 0.074, 0.420, -0.040, 0.525]


def ep(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%dT%H:%M:%SZ"))


def hours_pdt(t):
    return (t - ep("2026-11-01T07:00:00Z")) / 3600.0    # hours past 00:00 PDT, on the PDT clock whatever the box's zone says


def interp(table, h):
    a = int(math.floor(h))
    if a + 1 not in table:
        return table[a]
    return table[a] + (table[a + 1] - table[a]) * (h - a)


CUTOFF = ep("2026-11-01T15:15:00Z")     # 07:15 PST
# P1's rest reading is set when the queue starts: as soon as it may be, 15 min or more after the smoke. E100's 40 min slot starts 30 min after that
# rest reading, P2's rest reading is 90 min after it (so E100 ends 20 min before), and P2 must start by P2_LATEST so that its end leaves E96's gap
# over 90 min before P3. P3-P7 are fixed, 45 min apart. E96's slot is fixed too and ends 20 min before P3's rest reading.
P1_EXPECTED = ep("2026-11-01T08:05:00Z")
P2_EXPECTED = P1_EXPECTED + 90 * 60
P2_LATEST = "2026-11-01T09:41:00Z"
FIXED = {"P3": "2026-11-01T11:40:00Z", "P4": "2026-11-01T12:25:00Z", "P5": "2026-11-01T13:10:00Z", "P6": "2026-11-01T13:55:00Z",
         "P7": "2026-11-01T14:40:00Z"}
SLOT = {"E100": {"start": "30 min after P1's rest reading", "minutes": 40, "what": "the idle-reset test, int8 zeros, about 20 card-minutes"},
        "E96": {"start": "2026-11-01T10:05:00Z", "end": "2026-11-01T11:20:00Z", "what": "real tensors' speed, about 60 card-minutes"}}

probes = [("P1", P1_EXPECTED), ("P2", P2_EXPECTED)] + [(k, ep(v)) for k, v in sorted(FIXED.items())]
w_now_shape = interp(HOUR_W, hours_pdt(ep(T_NOW)))
exp_rows = {}
for k, t in probes:
    h = hours_pdt(t)
    dw = interp(HOUR_W, h) - w_now_shape
    exp_rows[k] = {"rest_read_utc": time.strftime("%H:%M", time.gmtime(t)), "hour_pdt": round(h, 2),
                   "rest_w": round(W_NOW + dw, 3), "rest_die_w_derived_change": round(dw / W_PER_C_REST, 2),
                   "rest_nic": round(NIC_NOW + interp(HOUR_NIC, h) - interp(HOUR_NIC, hours_pdt(ep(T_NOW))), 2),
                   "line_change_on_desk_slope": round(LINE_SLOPE_DESK * dw / W_PER_C_REST, 3),
                   "hold_die_change_if_room": round(HOLD_SLOPE_ROOM * dw / W_PER_C_REST, 2)}
x_exp = [exp_rows[k]["rest_w"] / W_PER_C_REST for k, _ in probes]
fall_w = exp_rows["P1"]["rest_w"] - exp_rows["P7"]["rest_w"]

# ---- planning noise, per probe, and what it makes of the rules (the probe is the unit; a t interval on n - 2 df)
SIGMA_LINE = 0.15          # C: rms 0.42 C of one run about E87's die line, over 8 runs. The die reads whole degrees.
SIGMA_HOLD_DIE = 0.40      # C: 0.29 C for the whole-degree reading, 0.28 C for the room's own 19.5 min cycle in a 2 min window
SIGMA_FINE_LINE = 0.05     # W: mean of three unclamped runs, reset samples left out
SIGMA_HOLD_W = 0.13        # W: the same cycle through L_800, plus the reading
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306}


def half_width(xs, sigma):
    m = st.mean(xs)
    return T975[len(xs) - 2] * sigma / math.sqrt(sum((x - m) ** 2 for x in xs))


def verdict_line(lo, hi, target=LINE_SLOPE_DESK):
    if hi < 0:
        return "OPPOSITE"
    if lo > target:
        return "ABOVE_TARGET"
    if hi < target:
        return "POSITIVE_BELOW_TARGET" if lo > 0 else "BELOW_TARGET"
    return "SUPPORTS" if lo > 0 else "INCONCLUSIVE"


def verdict_hold(lo, hi, band=HOLD_BAND, floor=LINE_SLOPE_DESK):
    if lo > band[1]:
        return "ABOVE_BAND"
    if hi < band[0]:
        return "BELOW_BAND"
    return "SUPPORTS" if lo > floor else "INCONCLUSIVE"


def simulate(beta, xs, sigma, kind, n=20000, seed=98):
    rng = random.Random(seed)
    m = st.mean(xs)
    sxx = sum((x - m) ** 2 for x in xs)
    tq = T975[len(xs) - 2]
    out = {}
    for _ in range(n):
        ys = [beta * (x - m) + rng.gauss(0, sigma) for x in xs]
        my = st.mean(ys)
        b = sum((x - m) * (y - my) for x, y in zip(xs, ys)) / sxx
        res = [y - my - b * (x - m) for x, y in zip(xs, ys)]
        se = math.sqrt(sum(r * r for r in res) / (len(xs) - 2) / sxx)
        lo, hi = b - tq * se, b + tq * se
        v = verdict_line(lo, hi) if kind == "line" else verdict_hold(lo, hi)
        out[v] = out.get(v, 0) + 1
    return {k: round(v / n, 3) for k, v in sorted(out.items())}


def scaled(xs, fall):
    """The expected shape of the night, scaled to a given fall in C from the first probe to the last."""
    a, b = xs[0], xs[-1]
    return [(x - b) / (a - b) * fall for x in xs]


power = {}
for fall in (2.0, 1.5, 1.0):
    xs = scaled(x_exp, fall)
    power[f"fall_{fall:g}_C"] = {
        "line_half_width": round(half_width(xs, SIGMA_LINE), 2),
        "line_verdicts_if_slope_0.25": simulate(LINE_SLOPE_DESK, xs, SIGMA_LINE, "line"),
        "line_verdicts_if_slope_0": simulate(0.0, xs, SIGMA_LINE, "line"),
        "hold_half_width": round(half_width(xs, SIGMA_HOLD_DIE), 2),
        "hold_verdicts_if_slope_room": simulate(HOLD_SLOPE_ROOM, xs, SIGMA_HOLD_DIE, "hold"),
        "hold_verdicts_if_slope_0.25": simulate(LINE_SLOPE_DESK, xs, SIGMA_HOLD_DIE, "hold"),
        "fine_line_half_width_w_per_w": round(half_width([x * W_PER_C_REST for x in xs], SIGMA_FINE_LINE), 2),
        "hold_w_half_width_w_per_w": round(half_width([x * W_PER_C_REST for x in xs], SIGMA_HOLD_W), 2),
    }

P = {
    "experiment": "E98", "request": "Q132", "card": "aifoundry2 card 0", "frozen_before_the_claim": True,
    "constants": {"k_line_c_per_w": K_LINE, "rest_w_per_c": W_PER_C_REST, "line_slope_desk": LINE_SLOPE_DESK, "l_800_w_per_c": L_800,
                  "gain_rest": round(GAIN_REST, 3), "gain_hold": round(GAIN_HOLD, 3), "p_rest_w": P_REST, "p_hold_w": P_HOLD},
    "targets": {
        "line_slope": LINE_SLOPE_DESK,
        "hold_slope_room": round(HOLD_SLOPE_ROOM, 2), "hold_band": HOLD_BAND, "hold_floor": LINE_SLOPE_DESK,
        "hold_slope_path": round(HOLD_SLOPE_PATH, 2),
        "fine_line_w_per_w_desk": round(FINE_LINE_RATIO_DESK, 2),
        "hold_w_per_w_room": round(HOLD_W_RATIO_ROOM, 2), "hold_w_band": HOLD_W_BAND,
        "hold_w_per_w_if_line_slope": round(FINE_LINE_RATIO_DESK, 2),
        "hold_w_per_w_path": round(HOLD_W_RATIO_ROOM * P_HOLD / P_REST, 2),
        "from_rest_line_slope": round(FROM_REST_LINE_SLOPE, 2),
        "from_rest_w_per_w_room": round(HOLD_W_RATIO_ROOM, 2),
        "trip_mhz_per_c": TRIP_MHZ_PER_C, "trip_w_per_c": TRIP_W_PER_C},
    "gates": {"min_probes": 4, "min_rest_range_c": 0.75, "min_gated_runs_per_probe": 6, "rest_min": 15,
              "rest_history_window_min": 20, "rest_skip_after_busy_min": 10, "rest_min_rows": 60},
    "rest_at_freeze": {"w": W_NOW, "die": DIE_NOW, "nic": NIC_NOW, "nvme": NVME_NOW, "at": T_NOW},
    "expected_rest": exp_rows,
    "expected_fall": {"w": round(fall_w, 3), "c_w_derived": round(fall_w / W_PER_C_REST, 2),
                      "night_falls_w_on_record": NIGHT_FALLS_W, "night_falls_mean_w": round(st.mean(NIGHT_FALLS_W), 3),
                      "night_falls_sd_w": round(st.stdev(NIGHT_FALLS_W), 3), "band_w": [0.1, 0.9]},
    "noise_planning": {"line_c": SIGMA_LINE, "hold_die_c": SIGMA_HOLD_DIE, "fine_line_w": SIGMA_FINE_LINE, "hold_w": SIGMA_HOLD_W},
    "power": power,
    "schedule": {"cutoff_utc": "2026-11-01T15:15:00Z", "p1": "as soon as it may be, 15 min or more after the smoke; expected ~08:05 UTC",
                 "p2": "90 min after P1, latest start " + P2_LATEST, "p2_latest_utc": P2_LATEST,
                 "fixed_rest_read_utc": FIXED, "slots": SLOT},
    "hold": {"kind": "int8/neg_ones", "die_expected_c": [60, 64.5], "w_expected": [40, 43.5], "window_s": 120},
    "kinds_line": ["fp16/zeros", "int8/zeros", "int8/neg_ones", "int8/sparse50", "fp16/ones", "int8/full", "fp32/randn"],
    "kinds_fine": ["fp16/zeros", "int8/zeros", "int8/neg_ones"],
    "t975": T975,
}

json.dump(P, open(os.path.join(HERE, "predictions.json"), "w"), indent=1, sort_keys=True)
print("E98 frozen numbers")
print(f"line slope target {LINE_SLOPE_DESK}; hold slope if room {HOLD_SLOPE_ROOM:.2f} (band {HOLD_BAND}), if the path {HOLD_SLOPE_PATH:.2f}")
print(f"fine: 800 MHz W per rest W {FINE_LINE_RATIO_DESK:.2f} on the desk's slope; hold W per rest W {HOLD_W_RATIO_ROOM:.2f} if room (band {HOLD_W_BAND}), "
      f"{HOLD_W_RATIO_ROOM * P_HOLD / P_REST:.2f} if the path; from-rest line slope {FROM_REST_LINE_SLOPE:.2f}")
print(f"expected fall P1 to P7: {fall_w:.3f} W = {fall_w / W_PER_C_REST:.2f} C; seven nights on record: mean {st.mean(NIGHT_FALLS_W):.3f} W, sd {st.stdev(NIGHT_FALLS_W):.3f}")
for k, _ in probes:
    print(k, exp_rows[k])
for k, v in power.items():
    print(k, json.dumps(v))
