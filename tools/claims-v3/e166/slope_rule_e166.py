#!/usr/bin/env python3
"""E166 (Q141(h)): the 300-600 s slope decision's thresholds, derived mechanically from Q140(e)'s committed null (corrections.json > C10),
before any E166 data. Desk only. Registered in E166.md (rule SL), beside R6's G_A, which stays as registered.

The statistic (RA1.5's reported slope, made a decision here): arm A's error e(t) = T(t) - (the frozen chain open loop on the measured board +
its anchor over the last 120 s of R4), its least-squares slope over [t0 + 300 s, b10) of K_OL, in C per 10 min; t0 = K_OL's first process's
start, b10 = the end of its last process ending at or before t0 + 600 s (D2's b). It is exactly corrections_q140e.hold_stats's
"slope_from_300s_C_per_10min" on K_O's window, the number C10 read on every committed aifoundry3 hold and on the frozen scenarios.

The null, stated from C10 (corrections.json > C10 > sessions, out of sample for the chain): the seven slopes of E144's two holds and E154's
five. A normal null with zero mean and the pool's rms about zero, as C10 computed its rates:
  * sigma_wide   = the rms of all seven (E154's two fp32 large rises K_S and K_O included: the conservative null);
  * sigma_narrow = the rms of the five without them (C10's "without_E154_K_S_and_K_O");
  * sigma_E97    = E97's two 30-minute holds (in sample for the chain), their G_A at the registered geometry divided by 1.5 (the windows'
                   centres are 900 s apart), reported only.
The decision (one-sided, growth):
  SLOPE SEEN      s >= c_hi,  c_hi = z95 x sigma_wide                 (a 5.0% false-positive rate under the wide null);
  SLOPE NOT SEEN  s <= c_lo,  c_lo = s_stage_min - z95 x sigma_wide   (a slow stage of the frozen scenarios' size reads NOT SEEN at most
                                                                       5% of the time; s_stage_min = the smallest of the three extra-stage
                                                                       scenarios' slope on K_O's window, C10 > scenarios_same_statistic);
  INCONCLUSIVE    otherwise.
z95 = 1.6449 (C10's own constant). Every rate below is printed from these numbers, never tuned.

    /usr/bin/python3 tools/claims-v3/e166/slope_rule_e166.py      # writes slope_rule_e166.json beside itself
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CORR = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q140e-heat-replicates", "corrections.json")
CORR_SHA256 = "de5bba20657fecdcc6f8edf765cbcb0746da5ce545704dde7f21da966bafb2fa"     # as committed in a4fe976d (03:43:53 PST)
Z95 = 1.6449


def tail(x, sd, mu=0.0):
    """P(s >= x) for s ~ N(mu, sd), C10's tail_p"""
    return 0.5 * math.erfc((x - mu) / (sd * math.sqrt(2)))


def r4(x):
    return round(float(x), 4)


def main():
    raw = open(CORR, "rb").read()
    if hashlib.sha256(raw).hexdigest() != CORR_SHA256:
        sys.exit("E166 slope rule REFUSED: corrections.json is not the committed a4fe976d copy")
    c10 = json.loads(raw)["C10"]
    slopes = {}
    for lab in ("E144", "E154"):
        for nm, x in c10["sessions"][lab]["holds"].items():
            slopes[f"{lab}.{nm}"] = float(x["slope_from_300s_C_per_10min"])
    wide = list(slopes)
    narrow = [k for k in wide if k not in ("E154.K_S", "E154.K_O")]

    def rms(keys):
        return math.sqrt(sum(slopes[k] ** 2 for k in keys) / len(keys))

    s_wide, s_narrow = rms(wide), rms(narrow)
    g97 = [float(c10["null"]["E97_in_sample"]["holds"][h]["G_A_registered_geometry_C"]) for h in ("H1", "H3")]
    s_e97 = math.sqrt(sum((g / 1.5) ** 2 for g in g97) / len(g97))
    sc = c10["scenarios_same_statistic"]
    stage = {k: float(sc[k]["K_O_window_600s"]["slope_from_300s_C_per_10min"]) for k in ("tau_s_600", "tau_s_1200", "tau_s_2400")}
    gain = float(sc["gain_D6"]["K_O_window_600s"]["slope_from_300s_C_per_10min"])
    chain = float(sc["chain_as_frozen"]["K_O_window_600s"]["slope_from_300s_C_per_10min"])
    s_stage_min = min(stage.values())
    c_hi = Z95 * s_wide
    c_lo = s_stage_min - Z95 * s_wide
    nulls = {"wide (all seven out of sample)": s_wide, "narrow (five, without E154's K_S and K_O)": s_narrow,
             "E97 in sample (G_A / 1.5, reported only)": s_e97}
    out = {"_note": "E166 rule SL (registered in E166.md before any E166 data): thresholds derived from Q140(e) corrections.json C10 "
                    "(a4fe976d), nothing tuned",
           "input": {"file": os.path.relpath(CORR, ROOT), "sha256": CORR_SHA256, "commit": "a4fe976d"},
           "statistic": "arm A's least-squares error slope over [t0 + 300 s, b10) of K_OL, C per 10 min "
                        "(corrections_q140e.hold_stats slope_from_300s_C_per_10min on K_O's window)",
           "null_slopes_C_per_10min": {k: r4(v) for k, v in slopes.items()},
           "sigma_C_per_10min": {"wide": r4(s_wide), "narrow": r4(s_narrow), "E97_in_sample": r4(s_e97)},
           "z95": Z95, "scenario_slopes_C_per_10min": {**{k: r4(v) for k, v in stage.items()}, "gain_D6": r4(gain), "chain_as_frozen": r4(chain)},
           "s_stage_min_C_per_10min": r4(s_stage_min),
           "thresholds_C_per_10min": {"SEEN_at_or_above": round(c_hi, 3), "NOT_SEEN_at_or_below": round(c_lo, 3)},
           "rates": {}}
    for nm, sd in nulls.items():
        out["rates"][nm] = {"sigma": r4(sd),
                            "false_positive_SEEN": r4(tail(c_hi, sd)),
                            "no_slow_stage_read_other_than_NOT_SEEN": r4(tail(c_lo, sd))}
    out["power_under_sigma_wide"] = {}
    for nm, mu in {**stage, "gain_D6": gain, "chain_as_frozen": chain}.items():
        p_seen = tail(c_hi, s_wide, mu)
        p_not = 1.0 - tail(c_lo, s_wide, mu)
        out["power_under_sigma_wide"][nm] = {"mean_slope": r4(mu), "P_SEEN": r4(p_seen), "P_NOT_SEEN": r4(p_not),
                                             "P_INCONCLUSIVE": r4(1.0 - p_seen - p_not)}
    out["committed_holds_posthoc_readings"] = {k: {"slope": r4(slopes[k]),
                                        "would_read": ("SLOPE SEEN" if slopes[k] >= c_hi else
                                                       ("SLOPE NOT SEEN" if slopes[k] <= c_lo else "INCONCLUSIVE"))}
                                    for k in wide}
    json.dump(out, open(os.path.join(HERE, "slope_rule_e166.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
