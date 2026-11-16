#!/usr/bin/env python3
"""E198 desk check (desk arithmetic of committed records; nothing measured): the predicted peak on aifoundry1 card 1.

  E193's measured board peak and die peak in each sitting on aifoundry3 card 0, set over that sitting's idle median (every
  sample outside the launches' spans, from 0.5 s before a launch to 2.5 s after it); aifoundry1 card 1's idle in E191's
  second session (the median of its three idle anchors, from 5 s after each start); then
    predicted board peak = card 1's idle + (E193's peak over its idle) x T2's upper scale (1.144)
                           + card 1's idle law's rise from its anchor die to the die peak predicted below,
    predicted die peak   = card 1's anchor die + E193's largest rise of the die over its pre-session median.
usage (from the repository's top): python3 -I -B tools/claims-v3/e198/desk/peaks_e198.py"""
import gzip
import json
import math
import statistics as st

D = "docs/reports/data/"


def tel(path):
    out = []
    with gzip.open(path, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def die(s):
    try:
        return float(s["temp_c"]["minshire"][0])
    except (KeyError, TypeError, IndexError, ValueError):
        return None


S_HI = json.load(open("tools/claims-v3/e198/forecast-e198.json"))["rules"]["scale_band"][1]
over, rise = [], []
for sit in ("a", "b"):
    d = D + "2026-11-15-e193-x04-clock-sitting-%s-aifoundry3/" % sit
    t = tel(d + "x04/telemetry.jsonl.gz")
    runs = [json.loads(l) for l in open(d + "x04/runs.jsonl") if l.strip()]
    spans = sorted((r["t_start_ms"] / 1000.0, r["t_end_ms"] / 1000.0) for r in runs)

    def busy(ts):
        return any(a - 0.5 <= ts <= b + 2.5 for a, b in spans)
    w = [s["board_w"] for s in t if s.get("board_w") is not None]
    T = [die(s) for s in t if die(s) is not None]
    idle = [s["board_w"] for s in t if s.get("board_w") is not None and not busy(s["t_ms"] / 1000.0)]
    pre = [die(s) for s in t if die(s) is not None and s["t_ms"] / 1000.0 < spans[0][0] - 0.5]
    over.append(max(w) - st.median(idle)); rise.append(max(T) - st.median(pre))
    print("E193 sitting %s (aifoundry3 card 0): %d samples; board peak %.2f W, idle median %.3f W, peak over idle %.3f W; "
          "die peak %.0f C, pre-session median %.1f C, rise %.1f C" % (sit.upper(), len(t), max(w), st.median(idle),
                                                                      over[-1], max(T), st.median(pre), rise[-1]))
d = D + "2026-11-15-e191-blind-day-aifoundry1-c1-s2/session/"
t = tel(d + "telemetry.jsonl.gz")
an = json.load(open(d + "anchors.json"))
aw, aT = [], []
for a in an:
    lo, hi = a["t0_ms"] / 1000.0 + 5.0, a["t1_ms"] / 1000.0
    aw += [s["board_w"] for s in t if s.get("board_w") is not None and lo <= s["t_ms"] / 1000.0 <= hi]
    aT += [die(s) for s in t if die(s) is not None and lo <= s["t_ms"] / 1000.0 <= hi]
idle1, T1 = st.median(aw), st.median(aT)
print("E191's second session (aifoundry1 card 1): its three idle anchors, %d samples: board median %.3f W, die median %.1f C"
      % (len(aw), idle1, T1))
law = json.load(open(D + "2026-11-12-q166-ledger-v2/frozen-v2.json"))["idle_laws"]["aifoundry1-c1"]


def p_idle(T):
    q, band, e = law["quad"], law["quad_band_c"], law["exp"]
    if band[0] <= T <= band[1]:
        return q["a"] * T * T + q["b"] * T + q["c"]
    return e["B"] + e["A80"] * math.exp((T - 80.0) / e["T_L"])


Tpk = T1 + max(rise)
law_rise = max(0.0, p_idle(Tpk) - p_idle(T1))
pk = idle1 + max(over) * S_HI + law_rise
print("predicted die peak: %.1f + %.1f = %.1f C" % (T1, max(rise), Tpk))
print("card 1's idle law from %.1f to %.1f C: %.3f -> %.3f W, a rise of %.3f W (the law's exponential form below 56 C)" % (
    T1, Tpk, p_idle(T1), p_idle(Tpk), law_rise))
print("predicted board peak: %.3f + %.3f x %.3f + %.3f = %.2f W" % (idle1, max(over), S_HI, law_rise, pk))
print("the runner's registered stops: board above 65 W on three samples in a row; a die reading at or above 70 C: "
      "margins %.1f W and %.1f C" % (65.0 - pk, 70.0 - Tpk))
print("PEAKS DESK DONE")
