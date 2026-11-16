#!/usr/bin/env python3
"""E198 desk check (desk arithmetic of committed records; nothing measured): a second path to rule T2's scale band, and the
readings set beside it.

  1. The band, by a second path: aifoundry3's means from E189's frozen scorer output (scores-e189.json > configs >
     measured_j_over_mean, committed in 830a3901), card 1's from E191's second session's energy.json files (7156ac15), set
     against forecast-e198.json's scale_source (forecast_e198.py's own reading of both data directories' energy.json).
  2. REPORTED beside it: the same ratios for the core-issue programs alone (SHA-256 and the sorts); the energy catalogue's
     card-1 / aifoundry3 ratios (docs/reports/data/2026-09-23-energy-manual/catalogue.json, the three-card check of 25-26
     Sep 2026) for the three rows E193's checks 1 and 2 name, and over every row both cards hold above 0.5 W; the minion
     rail's volts from the two cards' committed config reads, squared.
  3. The registered reducer's leakage law on card 1: E17's law (23.257/36 e^((T-80)/36) W per C) against card 1's own
     idle law in the frozen ledger v2 (docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json > idle_laws >
     aifoundry1-c1), and E193's mean busy-minus-idle die difference per arm (x04-e193-*.json > runs): what the reducer
     would leave in card 1's board prices if card 1's die moved as aifoundry3's did.
usage (from the repository's top): python3 -I -B tools/claims-v3/e198/desk/scale_e198.py"""
import json
import math
import statistics as st

D = "docs/reports/data/"
E189 = D + "2026-11-14-e189-blind-day-aifoundry3/"
E191 = D + "2026-11-15-e191-blind-day-aifoundry1-c1-s2/"
CFG = ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity")
F = json.load(open("tools/claims-v3/e198/forecast-e198.json"))

print("1. THE BAND, A SECOND PATH (and a third for card 1: E191's frozen scorer output, scores-e191.json, f74c81e3)")
sc = json.load(open(E189 + "scores-e189.json"))["configs"]
s1 = json.load(open(E191 + "scores-e191.json"))["configs"]
r = {}
for c in CFG:
    a3 = sc[c]["measured_j_over_mean"]
    c1v = [json.load(open(E191 + "passes/%s/p%d/energy.json" % (c, k)))["board"]["j_per_solve"] for k in (1, 2, 3, 4)]
    c1 = sum(c1v) / 4.0
    r[c] = c1 / a3
    f = F["scale_source"]["configs"][c]
    print("  %-14s aifoundry3 %.6f (E189 scorer) / %.6f (forecast)  card 1 %.6f (energy.json) / %.6f (E191 scorer) / "
          "%.6f (forecast)  ratio %.6f / %.6f  t_k %.4f / %.4f s" % (
              c, a3, f["aifoundry3_j_over_mean"], c1, s1[c]["measured_j_over_mean"], f["card1_j_over_mean"], r[c],
              f["ratio_card1_over_aifoundry3"], sc[c]["t_k_mean"], s1[c]["t_k_mean"]))
    assert abs(r[c] - f["ratio_card1_over_aifoundry3"]) < 1e-9, c
    assert abs(s1[c]["measured_j_over_mean"] - c1) < 1e-9 and abs(sc[c]["measured_j_over_mean"] - f["aifoundry3_j_over_mean"]) < 1e-9, c
lo, hi = min(r.values()), max(r.values())
print("  least %.5f (%s), greatest %.5f (%s); frozen band %s" % (lo, min(r, key=r.get), hi, max(r, key=r.get),
                                                              F["rules"]["scale_band"]))
assert F["rules"]["scale_band"] == [math.floor(lo * 1000) / 1000, math.ceil(hi * 1000) / 1000]
core = [r[c] for c in ("sha256", "sort-sorted", "sort-shuffled")]
print("  REPORTED: the core-issue programs alone (SHA-256, the sorts): %.4f to %.4f, median %.4f" % (
    min(core), max(core), st.median(core)))
print("  REPORTED: all six, median %.4f, mean %.4f" % (st.median(list(r.values())), st.mean(r.values())))
print("BAND SECOND PATH AGREES")

print("2. REPORTED: THE ENERGY CATALOGUE (three-card check, 25-26 Sep 2026), card 1 / aifoundry3, W over idle at 600 MHz")
cat = json.load(open(D + "2026-09-23-energy-manual/catalogue.json"))["cards"]
a3s, c1s = cat["aifoundry3"]["summary"], cat["aifoundry1-c1"]["summary"]
for row, arm in (("nop/zeros/h2", "spin2 (check 1)"), ("fadd.ps/zeros/h2", "faddps_p1 (check 2)"),
                 ("fsgnj.s/zeros/h2", "fsgnjs_p1 (check 2)"), ("fadd.s/zeros/h2", "fadds_p16's class")):
    w3, w1 = a3s[row]["over_idle_w"]["mean"], c1s[row]["over_idle_w"]["mean"]
    print("  %-18s %-22s aifoundry3 %.4f W  card 1 %.4f W  ratio %.4f" % (row, arm, w3, w1, w1 / w3))
rows = sorted(w for w in (c1s[k]["over_idle_w"]["mean"] / a3s[k]["over_idle_w"]["mean"]
                          for k in set(a3s) & set(c1s) if a3s[k]["over_idle_w"]["mean"] > 0.5))
n = len(rows)
print("  every row both cards hold above 0.5 W on aifoundry3: %d rows, median %.4f, 10th-90th percentile %.4f-%.4f, "
      "least %.4f, greatest %.4f" % (n, st.median(rows), rows[int(0.1 * n)], rows[int(0.9 * n)], rows[0], rows[-1]))
v3 = json.load(open(D + "2026-11-15-e193-x04-clock-sitting-a-aifoundry3/session/config-start.json"))["minion_mv"]
v1 = json.load(open(E191 + "session/config-start.json"))["minion_mv"]
print("  the minion rail's volts: aifoundry3 %d mV (E193 sitting A's start read), card 1 %d mV (E191's second session's); "
      "(card 1 / aifoundry3)^2 = %.4f" % (v3, v1, (v1 / v3) ** 2))

print("3. THE REDUCER'S LEAKAGE LAW ON CARD 1 (desk arithmetic; card 1's die assumed to move as aifoundry3's did)")
law = json.load(open(D + "2026-11-12-q166-ledger-v2/frozen-v2.json"))["idle_laws"]["aifoundry1-c1"]
print("  card 1's idle law as frozen: %s" % json.dumps({k: law[k] for k in law if k in ("quad", "quad_band_c", "exp")}))


def k_card1(T):
    q, band, e = law["quad"], law["quad_band_c"], law["exp"]
    if band[0] <= T <= band[1]:
        return 2 * q["a"] * T + q["b"]
    return e["A80"] / e["T_L"] * math.exp((T - 80.0) / e["T_L"])


def k_e17(T):
    return 23.257 / 36.0 * math.exp((T - 80.0) / 36.0)


for T in (50.0, 52.0, 55.0, 58.0):
    print("  at %.0f C: card 1's slope %.4f W/C, the reducer's (E17) %.4f W/C, left in the price %.4f W per C of rise" % (
        T, k_card1(T), k_e17(T), k_card1(T) - k_e17(T)))
for sit in ("a", "b"):
    x = json.load(open(D + "2026-11-15-e193-x04-clock-sitting-%s-aifoundry3/x04-e193-%s.json" % (sit, sit.upper())))
    dts = {}
    for run in x["runs"]:
        if run["pass"] > 0 and run["ok"]:
            dts.setdefault(run["arm"], []).append(run["die_c_busy"] - run["die_c_idle"])
    for arm in sorted(dts, key=lambda a: -x["arms"][a]["board_w"]):
        dT = st.mean(dts[arm])
        w = x["arms"][arm]["board_w"]
        left = (k_card1(50.0) - k_e17(50.0)) * dT
        print("  sitting %s %-12s board %.3f W, mean busy-minus-idle die %+.3f C -> %+.4f W left at 50 C (%+.2f%% of the price)" % (
            sit.upper(), arm, w, dT, left, 100 * left / w if abs(w) > 0.05 else float("nan")))
print("SCALE DESK DONE")
