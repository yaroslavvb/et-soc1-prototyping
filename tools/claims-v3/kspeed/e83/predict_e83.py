#!/usr/bin/env python3
"""E83 (Q130): the FROZEN predictions for the 33 kinds of numbers E80 did not run, on aifoundry2 card 0 under the
card's own governor (65 W static TDP, 65 C threshold: read, never changed). No E83 data exists when this runs.

    python3 predict_e83.py [--out predictions.json] > predictions.txt

THE INPUTS, each refused unless its sha256 is the one frozen here:
  * Q130(c) predictions.json (commit 2bbe03dd): per kind the switching W on aifoundry3 at 600 MHz, its 95% interval,
    `c_w_a2_600mhz` (the model's own conversion to aifoundry2, c = c_E64(type, zeros) + W / 1.01865), and its own
    frozen clocks `burst_mhz_65w` (4-12 s) and `sustained_mhz` (40-80 s from 58 C) with `sustained_limit`.
  * kinds.json (Q130(s) revision 2, commit 7d9c0d9e): the tiles, their sha256 and rules.
  * E80's results.json and posthoc-idle.json (commit c244f148): each of E80's 18 kinds' MEASURED switching term c
    (E64's method), burst clock and sustained clock. The burst cells used for the fit are amendment A1's view with
    the governor's idle-reset samples set aside (`burst_mhz_without`): the relation describes how the governor
    answers power, and the reset is not a function of power (E80 README section 3d).
  * E64's figures.json (commit of 23 Oct): the registered B_f and s_f of P_f = B_f + c * s_f, and the governor.
  * E80's kspeed predictions.json (commit 10f58581): E64-T1's build (gamma 3), used only for the labelled T1 arm.

PREDICTION (a), PRIMARY -- E80's measured relation between a kind's power and its clock, fitted on E80's 18 kinds
ONLY, applied to Q130(c)'s predicted c of each of the 33 (out of sample). The form, chosen before any E83 data by
its leave-one-kind-out rms on E80 (it beat a two-parameter hinge in both regimes; both are printed):
  the clock at which the kind's power curve P_f(c) = B_f + c * s_f (E64's registered B_f and s_f, 58 C-referred)
  time-averages an effective cap W, the governor dithering between neighbouring DVFS points
      f(c, W) = 800                                             if W >= P_800
              = 700 + 100 (W - P_700) / (P_800 - P_700)         if P_700 <= W < P_800
              = 600 + 100 (W - P_600) / (P_700 - P_600)         if P_600 <= W < P_700
              = 600                                             otherwise,
  averaged over W ~ Normal(W*, sigma) (41 points over +-3 sigma). Two parameters per regime, least squares on
  E80's 18 cells: the BURST (E80's 1.5-6.5 s mean of a 6 s run from <= 55 C) and the SUSTAINED (the last 40 s of
  nine 8 s processes from <= 57 C). The same average gives the expected time share at 800 MHz; the predicted
  sustained limit is `none` when that share is >= 0.9 (the measured rule's own threshold), otherwise `thermal`
  (E80: no sustained sample of any kind carried a power label). The predicted burst limit is `power` when the burst
  share at 800 is < 0.9, otherwise `none`. Interval: the clock at the ends of Q130(c)'s converted 95% c interval.
PREDICTION (b) -- Q130(c)'s own frozen clocks, verbatim (burst 4-12 s, sustained 40-80 s from 58 C, its limit).
LABELLED ARMS (tabulated, never a verdict): E64's registered governor on Q130(c)'s c (E80's own burst prediction);
E64-T1 at gamma 3 with E80's post-hoc die line (42.233 + 0.4349 C/W), the sustained arm E80 found at 9.2 MHz rms
in sample. The in-session anchor adjustment (a-adj) is defined in README.md and computed by reduce_e83.py.
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "hpl"))
import surface_hpl as SH  # noqa: E402
import surface_hpl_t as ST  # noqa: E402

Q130C = "docs/reports/data/2026-10-31-q130-kinds-model/predictions.json"
KINDS = "tools/claims-v3/kinds/kinds.json"
E80R = "docs/reports/data/2026-10-31-e80-kinds-speed/results.json"
E80A = "docs/reports/data/2026-10-31-e80-kinds-speed/posthoc-idle.json"
E64F = "docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json"
E80P = "tools/claims-v3/kspeed/predictions.json"
FROZEN_SHA = {
    Q130C: "c5a66cb6d5f07a35d783d7db4be0f94a69482cf123defd2eccfda04fb6320a2c",
    KINDS: "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
    E80R: "f8ab6fc08ef73a5f0e91fe518c2d33162fe14687235ab763ac50639dd49ae6fd",
    E80A: "f1f37c5e113559aa7a7a5f11227c7242eae964f16f90d9eb6b76903d196fbad4",
    E64F: "d430bfabd8f142d8fbb29b6f3f4ede71ff909d491b4de06526826d415828f9cb",
    E80P: "69a62b31607a02a481a8ea23ba716d42fae5822343cb372f7fa706e6ba00762c",
}
XFER = (0.5218 / 0.517) ** 2
PTS = (600, 700, 800)
NONE_SHARE = 0.9
E80_DIE_LINE = {"a_c": 42.233, "k_c_per_w": 0.4349}       # E80 results.json posthoc.die_line_e80
SUS_WIN = (36.2, 76.2)
BURST_WIN = (1.5, 6.5)
E80_KINDS = {"fp16": ["zeros", "ones", "randn", "sparse50", "smallint", "fp8grid", "nn_like"],
             "int8": ["zeros", "neg_ones", "full", "smallint", "gauss_q", "sparse50"],
             "fp32": ["randn", "bf16trunc", "sparse90", "smallint", "nn_like"]}
# E80's anchors, repeated inside E83's session (the brief): ties the two sessions together; fp32 zeros is one of
# the 33 (E80 never ran it), so its tie is to E64 (23 Oct) only
ANCHORS = ["fp32/randn", "fp16/randn", "int8/full", "fp16/zeros", "int8/zeros"]
# E64's own measurements of kinds among the 33 (23 Oct; host-generated values with the same bit rules), tabulated only
E64_CELLS = {"fp32/zeros": {"burst": 800, "sus": 800.0}, "fp32/ones": {"burst": 800, "sus": 738.0},
             "fp32/pow2": {"burst": 800, "sus": None}, "int8/ones": {"burst": None, "sus": 800.0},
             "source": "docs/reports/data/2026-10-23-e64-horace-power-limit/README.md, LAD and SUS tables"}
NQ = 41


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


class Rel:
    """The dither-at-an-effective-cap relation on E64's registered power curve."""

    def __init__(self, B):
        self.B = B
        self.S = {f: SH.S[f] for f in PTS}
        self.z = [-3.0 + 6.0 * i / (NQ - 1) for i in range(NQ)]
        self.w = [math.exp(-z * z / 2.0) for z in self.z]
        self.wt = sum(self.w)

    def p(self, c):
        return {f: self.B[f] + c * self.S[f] for f in PTS}

    @staticmethod
    def _d(p6, p7, p8, W):
        if W >= p8:
            return 800.0, 1.0
        if W >= p7:
            s = (W - p7) / (p8 - p7)
            return 700.0 + 100.0 * s, s
        if W >= p6:
            return 600.0 + 100.0 * (W - p6) / (p7 - p6), 0.0
        return 600.0, 0.0

    def dither(self, c, W):
        P = self.p(c)
        return self._d(P[600], P[700], P[800], W)

    def f(self, c, W, sig):
        """(mean clock, expected time share at 800)"""
        P = self.p(c)
        p6, p7, p8 = P[600], P[700], P[800]
        if sig <= 1e-9:
            return self._d(p6, p7, p8, W)
        m = s8 = 0.0
        d = self._d
        for z, w in zip(self.z, self.w):
            a, b = d(p6, p7, p8, W + sig * z)
            m += w * a
            s8 += w * b
        return m / self.wt, s8 / self.wt


def hinge(c, c0, b):
    return max(600.0, min(800.0, 800.0 - b * max(0.0, c - c0)))


def grid_fit(fun, data, g1, g2):
    """least squares over a coarse grid, then a fine grid around the best point; returns (params, rms)."""
    def sse(p):
        return sum((fun(x, *p) - y) ** 2 for x, y in data)
    best = min(((sse((a, b)), (a, b)) for a in g1 for b in g2))
    (a0, b0) = best[1]
    st1 = (g1[1] - g1[0]) if len(g1) > 1 else 1.0
    st2 = (g2[1] - g2[0]) if len(g2) > 1 else 1.0
    fine1 = [a0 - st1 + i * st1 / 10.0 for i in range(21)]
    fine2 = [max(0.0, b0 - st2 + i * st2 / 10.0) for i in range(21)]
    best = min(((sse((a, b)), (a, b)) for a in fine1 for b in fine2))
    return best[1], math.sqrt(best[0] / len(data))


def frange(a, b, st):
    n = int(round((b - a) / st))
    return [round(a + i * st, 6) for i in range(n + 1)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "predictions.json"))
    a = ap.parse_args()
    shas = {}
    for p, want in FROZEN_SHA.items():
        got = sha(os.path.join(ROOT, p))
        if got != want:
            sys.exit(f"refused: {p} sha256 {got} is not the frozen {want}")
        shas[p] = got
    Q = json.load(open(os.path.join(ROOT, Q130C)))["predictions"]
    K = json.load(open(os.path.join(ROOT, KINDS)))["kinds"]
    R80 = json.load(open(os.path.join(ROOT, E80R)))
    A80 = json.load(open(os.path.join(ROOT, E80A)))
    F64 = json.load(open(os.path.join(ROOT, E64F)))
    P80 = json.load(open(os.path.join(ROOT, E80P)))
    B = {int(k): v for k, v in F64["fit"]["B"].items()}
    gov = F64["governor"]
    rel = Rel(B)

    # ---- the fit, on E80's 18 kinds only
    e80 = []
    for t, ks in E80_KINDS.items():
        for k in ks:
            key = f"{t}/{k}"
            c = R80["cells"][key]
            e80.append({"kind": key, "c_w": c["c_w"], "burst_mhz_without": A80["kinds"][key]["burst_mhz_without"],
                        "burst_mhz_registered": c["burst_mhz"], "sus_mhz": c["sus_mhz"],
                        "sus_limit": c["sus_limit"], "sus_w": c["sus_w"], "sus_die": c["sus_die"]})
    gW = frange(40.0, 76.0, 0.25)
    gS = frange(0.0, 6.0, 0.25)
    gC = frange(4.0, 20.0, 0.25)
    gB = frange(2.0, 30.0, 0.25)
    fits = {}
    for regime, ykey in (("burst", "burst_mhz_without"), ("sustained", "sus_mhz")):
        data = [(r["c_w"], r[ykey]) for r in e80]
        res = {}
        for form, fun, g1, g2 in (("dither", lambda x, W, s: rel.f(x, W, s)[0], gW, gS),
                                  ("hinge", hinge, gC, gB)):
            par, r_in = grid_fit(fun, data, g1, g2)
            loo = []
            for i in range(len(data)):
                pp, _ = grid_fit(fun, data[:i] + data[i + 1:], g1, g2)
                loo.append(round(fun(data[i][0], *pp) - data[i][1], 2))
            res[form] = {"params": [round(par[0], 4), round(par[1], 4)], "rms_in_sample_mhz": round(r_in, 2),
                         "rms_loo_mhz": round(math.sqrt(sum(x * x for x in loo) / len(loo)), 2),
                         "loo_residuals_mhz": dict(zip([r["kind"] for r in e80], loo))}
        fits[regime] = res
    for regime in fits:
        if fits[regime]["dither"]["rms_loo_mhz"] > fits[regime]["hinge"]["rms_loo_mhz"]:
            sys.exit(f"refused: the registered form must be the one with the lower LOO rms ({regime})")
    Wb, sb = fits["burst"]["dither"]["params"]
    Ws, ss = fits["sustained"]["dither"]["params"]
    for r in e80:
        r["fit_burst_mhz"] = round(rel.f(r["c_w"], Wb, sb)[0], 1)
        r["fit_sus_mhz"] = round(rel.f(r["c_w"], Ws, ss)[0], 1)

    t1 = P80["t1_build"]["3.0"]
    T1B = {int(k): v for k, v in t1["B"].items()}

    def t1_sus(c, T0=57.0):
        sim = ST.simulate(ST.p_maker(T1B, c, 3.0), 65.0, t1["governor"]["tau_s"], t1["governor"]["pass_s"],
                          t_end=SUS_WIN[1], t_from=SUS_WIN[0], T0=float(T0), therm=E80_DIE_LINE,
                          tau_th=t1["tau_th"]["tau_th_s"], trip=66.0)
        return round(sim["mhz"], 1)

    out = {"experiment": "E83", "request": "Q130", "card": "aifoundry2 card 0", "date": "2026-10-31",
           "what": ("FROZEN predictions for E83, made before the #community-lab claim and before any E83 launch: the "
                    "burst and sustained clock under the card's own governor of the 33 kinds of kinds.json that E80 "
                    "did not run, plus E80's five anchors repeated inside the session"),
           "inputs_sha256": shas,
           "inputs_commits": {"q130c_freeze": "2bbe03dd", "kinds_spec_revision_2": "7d9c0d9e",
                              "e80_data": "c244f148", "e80_preregistration": "10f58581"},
           "constants": {"B_registered_w": B, "s_f": {f: SH.S[f] for f in PTS}, "xfer_a3_over_a2": XFER,
                         "governor_registered": gov, "none_share_800": NONE_SHARE, "quadrature_points": NQ,
                         "e80_die_line": E80_DIE_LINE, "sus_window_s": SUS_WIN, "burst_window_s": BURST_WIN},
           "relation": {"form": "dither at an effective cap W, W ~ Normal(W*, sigma), on P_f = B_f + c s_f",
                        "fitted_on": "E80's 18 kinds only: measured c (results.json cells.*.c_w), burst = A1's "
                                     "burst_mhz_without (posthoc-idle.json kinds.*), sustained = cells.*.sus_mhz",
                        "burst": {"W_star_w": Wb, "sigma_w": sb}, "sustained": {"W_star_w": Ws, "sigma_w": ss},
                        "fits": fits, "e80_points": e80},
           "anchors": {k: {"e80_burst_mhz": R80["cells"][k]["burst_mhz"],
                           "e80_burst_mhz_runs": R80["cells"][k]["burst_mhz_runs"],
                           "e80_sus_mhz": R80["cells"][k]["sus_mhz"],
                           "e80_sus_mhz_runs": R80["cells"][k]["sus_mhz_runs"],
                           "e80_c_w": R80["cells"][k]["c_w"], "e80_sus_w": R80["cells"][k]["sus_w"],
                           "e80_sus_die": R80["cells"][k]["sus_die"]} for k in ANCHORS},
           "e64_cells": E64_CELLS, "kinds": {}}
    for t in ("fp32", "fp16", "int8"):
        c0 = Q[f"{t}/zeros"]["c_w_a2_600mhz"]
        for k, rec in K[t].items():
            key = f"{t}/{k}"
            in_e80 = k in E80_KINDS[t]
            if in_e80 and key not in ANCHORS:
                continue
            q = Q[key]
            tile = os.path.join("tools/claims-v3/kinds", rec["file"])
            tsha = sha(os.path.join(ROOT, tile))
            if tsha != rec["sha256"] or tsha != q["tile_sha256"]:
                sys.exit(f"refused: tile {tile} sha256 {tsha} disagrees with kinds.json / Q130(c)")
            c = q["c_w_a2_600mhz"]
            lo, hi = q["switching_w_ci95"]
            c_lo, c_hi = c0 + lo / XFER, c0 + hi / XFER
            b, b8 = rel.f(c, Wb, sb)
            s, s8 = rel.f(c, Ws, ss)
            pw = rel.p(c)
            gb = SH.simulate(pw, 65.0, gov["tau_s"], gov["pass_s"], t_end=BURST_WIN[1], t_from=BURST_WIN[0])
            ent = {"type": t, "kind": k, "role": "anchor" if in_e80 else "e83", "tier": rec["tier"],
                   "rule": rec["rule"], "tile": tile, "tile_sha256": tsha,
                   "gated_lane_frac": rec["stats"]["gated_lane_frac"], "bus_bits_per_op": rec["stats"]["bus_bits_per_op"],
                   "provisional_power": t == "int8",
                   "c_pred_w": round(c, 3), "c_ci95_w": [round(c_lo, 3), round(c_hi, 3)],
                   "p_pred_w_at_58c": {str(f): round(pw[f], 2) for f in PTS},
                   "a": {"burst_mhz": round(b, 1), "burst_share800": round(b8, 3),
                         "burst_limit": "none" if b8 >= NONE_SHARE else "power",
                         "burst_mhz_from_c_ci95": [round(rel.f(c_hi, Wb, sb)[0], 1), round(rel.f(c_lo, Wb, sb)[0], 1)],
                         "burst_rate": round(SH.rate_t(t, b), 3),
                         "sus_mhz": round(s, 1), "sus_share800": round(s8, 3),
                         "sus_limit": "none" if s8 >= NONE_SHARE else "thermal",
                         "sus_mhz_from_c_ci95": [round(rel.f(c_hi, Ws, ss)[0], 1), round(rel.f(c_lo, Ws, ss)[0], 1)],
                         "sus_rate": round(SH.rate_t(t, s), 3)},
                   "b": {"burst_mhz_4_12s": q["burst_mhz_65w"], "sus_mhz_40_80s": q["sustained_mhz"],
                         "sus_limit": q["sustained_limit"], "sus_die_c": q["sustained_die_c"],
                         "sus_board_w": q["sustained_board_w"], "calibration_status": q["calibration_status"]},
                   "arm_gov_burst_mhz": round(gb, 1),
                   "arm_t1_e80line_sus_mhz_from57": t1_sus(c)}
            if key in E64_CELLS:
                ent["e64_cell"] = E64_CELLS[key]
            out["kinds"][key] = ent
    n33 = sum(1 for e in out["kinds"].values() if e["role"] == "e83")
    if n33 != 33 or len(out["kinds"]) != 38:
        sys.exit(f"refused: {n33} new kinds and {len(out['kinds'])} in all (want 33 and 38)")
    json.dump(out, open(a.out, "w"), indent=1)

    print("E83 frozen predictions (aifoundry2 card 0, 65 W / 65 C as found). c: switching W at 600 MHz / 517 mV "
          "(Q130(c), c_E64 zeros + W/1.01865)")
    for regime in ("burst", "sustained"):
        f = fits[regime]
        print(f"relation {regime}: dither W* {f['dither']['params'][0]} W sigma {f['dither']['params'][1]} W "
              f"(in-sample rms {f['dither']['rms_in_sample_mhz']}, LOO {f['dither']['rms_loo_mhz']} MHz); "
              f"hinge c0 {f['hinge']['params'][0]} W slope {f['hinge']['params'][1]} MHz/W "
              f"(in-sample {f['hinge']['rms_in_sample_mhz']}, LOO {f['hinge']['rms_loo_mhz']} MHz)")
    print("E80 points: kind, measured c, burst (A1 view) vs fit, sustained vs fit")
    for r in e80:
        print("  %-15s c %6.2f  burst %6.1f fit %6.1f   sus %6.1f fit %6.1f" % (
            r["kind"], r["c_w"], r["burst_mhz_without"], r["fit_burst_mhz"], r["sus_mhz"], r["fit_sus_mhz"]))
    print()
    print("%-21s %-6s %6s %-13s | %7s %-9s %-5s %6s | %7s %-9s %5s %-7s | %6s %6s %-7s | %6s %6s" % (
        "kind", "role", "c W", "c ci95", "(a) bur", "ci95", "lim", "rate", "(a) sus", "ci95", "sh800", "limit",
        "(b) b", "(b) s", "(b) lim", "gov b", "T1 s"))
    for key, e in out["kinds"].items():
        A_, B_ = e["a"], e["b"]
        print("%-21s %-6s %6.2f %-13s | %7.1f %-9s %-5s %6.2f | %7.1f %-9s %5.2f %-7s | %6.0f %6.0f %-7s | %6.1f %6.1f" % (
            key, e["role"], e["c_pred_w"], "%.2f-%.2f" % tuple(e["c_ci95_w"]), A_["burst_mhz"],
            "%.0f-%.0f" % tuple(A_["burst_mhz_from_c_ci95"]), A_["burst_limit"], A_["burst_rate"], A_["sus_mhz"],
            "%.0f-%.0f" % tuple(A_["sus_mhz_from_c_ci95"]), A_["sus_share800"], A_["sus_limit"],
            B_["burst_mhz_4_12s"], B_["sus_mhz_40_80s"], B_["sus_limit"], e["arm_gov_burst_mhz"],
            e["arm_t1_e80line_sus_mhz_from57"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
