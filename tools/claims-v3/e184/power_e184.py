#!/usr/bin/env python3
"""E184's frozen forecasts and the power of every registered rule (registration, desk only).

    /usr/bin/python3 -B tools/claims-v3/e184/power_e184.py <repository top> > tools/claims-v3/e184/forecast-e184.json
    /usr/bin/python3 -B tools/claims-v3/e184/power_e184.py <repository top> --text > tools/claims-v3/e184/forecast-e184.txt

It reads inputs-e184.json and plan-e184.json (both beside it, both in the registration's hash list) and the September TEL block's
committed reset windows for card 1 (docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/tel/), and writes every forecast the
registration freezes with the power of each rule under two noise models:
  base:  the board's per-refresh sd inside E180's fadd.ps bursts (inputs-e184.json > e180_noise), lag-1 correlation as measured,
         7 kept refreshes a 1.6 s block, and 0.008 W of drift left in each quad;
  pess:  twice that refresh sd, and 0.030 W of drift a quad.
The rules' own intervals come from the measured quads (score_e184.py); the models only set the power. Every simulation is seeded.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ".")
TEXT = "--text" in sys.argv
REPS = int(os.environ.get("E184_POWER_REPS", "2000"))
INP = json.load(open(os.path.join(HERE, "inputs-e184.json")))
PLAN = json.load(open(os.path.join(HERE, "plan-e184.json")))
DS = PLAN["design"]

# ---- the registered thresholds ------------------------------------------------------------------------------------------------------
DELTA_N = 0.020         # E184-N: the null within +-0.020 W
DELTA_L = 0.10          # E184-L: the ladder's small-to-large slope ratio within 1 +- 0.10
DELTA_P = 0.12          # E184-P: the operating point's ratio within 1 +- 0.12
EXCLUDE_P = 0.5         # E184-P: METER EXCLUDED when the ratio's lower end is above 0.5 (E178's pair read 0.29 of M10's forecast)
Z_JUMP = 2.807          # E184-J: Bonferroni over the ladder's 10 levels, two-sided 5%
E178_RATIO = 0.0532 / 0.1857   # E178-H-int8's measured pair over M10's frozen forecast (E178's data README; critic of Q149)


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


# ---- the noise model -------------------------------------------------------------------------------------------------------------------
SIG_R = INP["e180_noise"]["refresh_sd_w_median"]["zeros"]
RHO = INP["e180_noise"]["lag1_median"]
SP_PASS_S = 0.160
M_REF = int(math.floor((DS["block_launches"] * DS["launch_s"] - DS["discard_s"]) / SP_PASS_S + 1e-9))


def block_sd(sig_r, rho, m):
    v = m + 2 * math.fsum((m - k) * rho ** k for k in range(1, m))
    return sig_r * math.sqrt(v) / m


MODELS = {}
for name, k_r, drift in (("base", 1.0, 0.008), ("pess", 2.0, 0.030)):
    sb = block_sd(SIG_R * k_r, RHO, M_REF)
    MODELS[name] = {"refresh_sd_w": SIG_R * k_r, "rho": RHO, "refreshes_per_block": M_REF, "block_sd_w": sb,
                    "drift_sd_w": drift, "quad_sd_w": math.sqrt(sb * sb + drift * drift)}

S_MW = INP["e180_anchor"]["board_mw_per_minion"]          # E180: fadd.ps random less zeros on aifoundry3, per minion
S_W = S_MW / 1000.0
S_SE_W = INP["e180_anchor"]["board_mw_per_minion_se"] / 1000.0
S_CAT_W = INP["catalogue"]["fadd_ps_step"]["aifoundry3"]["board_mw_per_minion"] / 1000.0
RAIL_W = INP["e180_anchor"]["rail_mw_per_minion"] / 1000.0
LSB_W = INP["pmic_meter"]["mw_per_code_at_12v"] / 1000.0
CARRY_W = INP["pmic_meter"]["carry_1024_board_w_at_11p7_12p0_12p3_v"]


def quads_of(part):
    """[(pass, n, ref, count)] per level for one part, from the plan."""
    out = {}
    for p in PLAN["arm_S"]["passes"]:
        for it in p["items"]:
            if it["part"] == part:
                out[it["n"]] = out.get(it["n"], 0) + 1
    return out


def delta_ratio(levels, small, large):
    """E184-L's and E184-P's registered statistic: R = b(small) / b(large), slopes through the origin over the quads, with the
    delta-method 95% interval from the pooled within-level variance of the part's quads (every level, the null's too)."""
    ss = [(n, y) for n in small for y in levels[n]]
    ll = [(n, y) for n in large for y in levels[n]]
    bs = math.fsum(n * y for n, y in ss) / math.fsum(n * n for n, _ in ss)
    bl = math.fsum(n * y for n, y in ll) / math.fsum(n * n for n, _ in ll)
    dev, dof = [], 0
    for n, ys in levels.items():
        m = c.fmean(ys)
        dev.extend((y - m) ** 2 for y in ys)
        dof += len(ys) - 1
    s2 = math.fsum(dev) / dof
    vs, vl = s2 / math.fsum(n * n for n, _ in ss), s2 / math.fsum(n * n for n, _ in ll)
    R = bs / bl
    rel = math.sqrt(vs / bs ** 2 + vl / bl ** 2)
    return R, R * (1 - 1.96 * rel), R * (1 + 1.96 * rel), bs, bl, math.sqrt(s2)


def sim_ratio(counts, small, large, model, delta, gain_small=1.0, jump=None, do_jump=False, reps=REPS, seed=0):
    r = random.Random(18406 + seed)
    sq = MODELS[model]["quad_sd_w"]
    out = {"LINEAR": 0, "LOW": 0, "HIGH": 0, "NOT RESOLVED": 0}
    halfw, jumps, excl = [], 0, 0
    for _ in range(reps):
        lv = {}
        for n, k in counts.items():
            mu = S_W * n * (gain_small if n in small else 1.0) + (jump[1] if jump and n >= jump[0] else 0.0)
            lv[n] = [mu + r.gauss(0.0, sq) for _ in range(k)]
        R, lo, hi, _, _, _ = delta_ratio(lv, small, large)
        out[c.three_way(lo, hi, delta)] += 1
        halfw.append((hi - lo) / 2)
        excl += 1 if lo > EXCLUDE_P else 0
        if do_jump:
            v, _ = c.jump_reading(lv, Z_JUMP)
            jumps += 1 if v == "SEEN" else 0
    return {k: round(v / reps, 3) for k, v in out.items()}, r6(c.median(halfw)), round(jumps / reps, 3), round(excl / reps, 3)


def sim_null(k, model, reps=REPS):
    r = random.Random(18407)
    sq = MODELS[model]["quad_sd_w"]
    res = {"NULL": 0, "OFFSET": 0, "NOT RESOLVED": 0}
    hw = []
    for _ in range(reps):
        ys = [r.gauss(0.0, sq) for _ in range(k)]
        v, m, lo, hi = c.null_reading(ys, DELTA_N)
        res[v] += 1
        hw.append((hi - lo) / 2)
    return {kk: round(v / reps, 3) for kk, v in res.items()}, r6(c.median(hw))


def scan_quads(model, r, step_at_n=None, d=0.0):
    sq = MODELS[model]["quad_sd_w"]
    cq = PLAN["design"]["C"]
    ref, per = cq["ref"], cq["quads_per_level_per_sweep"] * len(cq["sweeps"])
    qs = []
    for n in cq["levels"]:
        mu = S_W * (n - ref)
        if step_at_n is not None:
            mu += d * ((1.0 if n > step_at_n else 0.0) - (1.0 if ref > step_at_n else 0.0))
        qs.extend({"n": n, "y": mu + r.gauss(0.0, sq)} for _ in range(per))
    return qs


def sim_scan():
    cq = PLAN["design"]["C"]
    out = {}
    for model in ("base", "pess"):
        r = random.Random(18408)
        null_t = sorted(c.scan_fit(scan_quads(model, r), cq["ref"])["max_abs_t"] for _ in range(REPS // 3))
        tcrit = null_t[int(math.ceil(0.95 * (len(null_t) - 1)))]
        powers = {}
        base_w = PLAN_SCAN_BASE_W
        for lbl, pw in (("carry at 11.7 V", CARRY_W[0]), ("carry at 12.0 V", CARRY_W[1]), ("carry at 12.3 V", CARRY_W[2])):
            n_at = (pw - base_w) / S_W
            for dname, dd in (("1 LSB", LSB_W), ("half an LSB", LSB_W / 2)):
                hits, near = 0, 0
                for _ in range(REPS // 6):
                    fit = c.scan_fit(scan_quads(model, r, n_at, dd), cq["ref"])
                    if fit["max_abs_t"] > tcrit:
                        hits += 1
                        near += 1 if abs(fit["best"]["break_n"] - n_at) <= 18 else 0
                powers["%s, a step of %s" % (lbl, dname)] = {"n_at": r6(n_at), "seen": round(hits / (REPS // 6), 3),
                                                             "seen_and_located_within_18_minions": round(near / (REPS // 6), 3)}
        out[model] = {"t_crit_family_5pct": r6(tcrit), "power": powers}
    return out


# ---- the dither model's bound for one code's DNL ----------------------------------------------------------------------------------------
def dither_bound(delta_lsb, sigma_lsb):
    """The largest change of the mean reading one displaced transition (by delta_lsb) makes under Gaussian dither of sigma_lsb (in
    LSB): delta * phi(0) / sigma for small delta, computed exactly as the difference of two normal CDFs."""
    best = 0.0
    for i in range(-400, 401):
        x = i / 100.0
        v = 0.5 * (math.erf((delta_lsb - x) / (sigma_lsb * math.sqrt(2))) - math.erf((0.0 - x) / (sigma_lsb * math.sqrt(2))))
        best = max(best, abs(v))
    return best


# ---- the rail's filter on a quad -------------------------------------------------------------------------------------------------------------
def rail_gain(tau, delay):
    """The minion rail's quad contrast over its step: a first-order filter (tau) published one SP pass late (delay), the rail's
    block means read in the board's windows. Mean over the two orientations, the settle block at A."""
    dt = 0.01
    gains = []
    for orient in ("ABBA", "BAAB"):
        segs = [("S", DS["settle_launches"])] + [(x, DS["block_launches"]) for x in c.ORIENT[orient]]
        t, edges = 0.0, []
        for lab, k in segs:
            edges.append((lab, t, t + k * DS["launch_s"]))
            t += k * DS["launch_s"]
        T = t
        y, ys = 0.0, []
        steps = int(T / dt) + 1
        for i in range(steps):
            tt = i * dt - delay
            u = 0.0
            for lab, a, b in edges:
                if lab == "B" and a <= tt < b:
                    u = 1.0
            y += (u - y) * dt / tau
            ys.append(y)
        vals = {"A": [], "B": []}
        for lab, a, b in edges[1:]:
            w = [ys[i] for i in range(steps) if a + DS["discard_s"] <= i * dt <= b]
            vals[lab].append(c.fmean(w))
        gains.append((math.fsum(vals["B"]) - math.fsum(vals["A"])) / 2.0)
    return c.fmean(gains)


# ---- card 1's SRAM arm: the September reset windows as the scatter model ----------------------------------------------------------------
def tel_card1():
    rows = []
    for f in sorted(glob.glob(os.path.join(TOP, "docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/tel/p*/reset.jsonl.gz"))):
        ds = []
        for line in gzip.open(f, "rt"):
            try:
                ds.append(json.loads(line))
            except ValueError:
                continue
        rows.extend(c.reset_window_ratios(ds))
    return rows


def sim_hmix(rows, per_level=30, levels=10, reps=REPS):
    """Power of E184-M: each level's samples drawn from September's card-1 steady samples (H-MIX true, ratios constant), or with
    each level's min/avg moved by its share of a 0.12 spread (load-dependent ratios)."""
    r = random.Random(18409)
    ma = [x[0] for x in rows]
    out = {}
    for name, spread in (("H-MIX true (constant ratios)", 0.0), ("ratios move 0.12 across levels", 0.12)):
        sup, ref = 0, 0
        for _ in range(reps):
            meds = []
            for li in range(levels):
                shift = spread * (li / (levels - 1) - 0.5)
                meds.append(c.median([ma[r.randrange(len(ma))] + shift for _ in range(per_level)]))
            sp = max(meds) - min(meds)
            sup += 1 if sp <= 0.06 and all(0.55 <= m <= 0.71 for m in meds) else 0
            ref += 1 if sp > 0.10 else 0
        out[name] = {"supported_parts": round(sup / reps, 3), "spread_over_0p10": round(ref / reps, 3)}
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------------
PLAN_SCAN_BASE_W = DS["C"]["scan_start_w"]          # the scan's zeros base by its mask rule
counts_L, counts_P = quads_of("L"), quads_of("P")
L_SMALL, L_LARGE = DS["L"]["small"], DS["L"]["large"]
P_SMALL, P_LARGE = DS["P"]["small"], DS["P"]["large"]

res = {"what": "E184's frozen forecasts and the power of its rules (power_e184.py)", "reps": REPS, "models": MODELS,
       "thresholds": {"delta_N_w": DELTA_N, "delta_L": DELTA_L, "delta_P": DELTA_P, "exclude_P_lower_end": EXCLUDE_P,
                      "z_jump": Z_JUMP, "e178_pair_ratio_to_m10": r6(E178_RATIO)}}
fc = {}
LEAK_G = INP["thermal"]["leak_gain_allowance"]
fc["step_w_per_minion"] = {"primary_e180": r6(S_W), "e180_se": r6(S_SE_W), "catalogue_26sep": r6(S_CAT_W), "leak_allowance": LEAK_G,
                           "band_95": [r6(S_W - 1.96 * S_SE_W - 0.01 * S_W), r6(max(S_CAT_W, S_W * (1 + LEAK_G)) + 1.96 * S_SE_W)],
                           "why_band": "E180's mean +- 1.96 se, widened below by 1% and above to the larger of the catalogue's 26 Sep row "
                                       "and E180 with the most of its own leakage a step can carry (inputs-e184.json > thermal)"}
fc["levels_w"] = {"L": {str(n): r6(S_W * n) for n in DS["L"]["levels"]}, "P": {str(n): r6(S_W * n) for n in DS["P"]["levels"]},
                  "C_against_ref": {str(n): r6(S_W * (n - DS["C"]["ref"])) for n in DS["C"]["levels"]}}
fc["operating_point"] = {"target_board_w": INP["e178_op"]["target_board_w"],
                         "m_op_forecast": round((INP["e178_op"]["target_board_w"] - INP["e180_noise"]["idle_before_burst_w_median"]) /
                                                ((INP["e180_noise"]["zeros32_board_w_median"] - INP["e180_noise"]["idle_before_burst_w_median"]) / 32)),
                         "m_s_forecast": round((DS["C"]["scan_start_w"] - INP["e180_noise"]["idle_before_burst_w_median"]) /
                                               ((INP["e180_noise"]["zeros32_board_w_median"] - INP["e180_noise"]["idle_before_burst_w_median"]) / 32)),
                         "base32_board_w": INP["e180_noise"]["zeros32_board_w_median"],
                         "why": "a straight line from E180's idle card (24.4 W) to its zeros base on 32 shires (35.5 W); the "
                                "calibration pass decides on the day"}
fc["carry"] = {"code_1024_board_w_at_11p7_12p0_12p3_v": CARRY_W, "lsb_w_at_12v": r6(LSB_W),
               "regions_w": {"P (30.1-31.1 W)": "below the band", "C (32.4-34.8 W)": "across the band",
                             "L (35.5-36.6 W)": "above the band"},
               "dither_bound_lsb": {"1 LSB displaced, sd 2.1 LSB": r6(dither_bound(1.0, SIG_R / LSB_W)),
                                    "1 LSB displaced, sd 1.0 LSB": r6(dither_bound(1.0, 1.0)),
                                    "0.5 LSB displaced, sd 2.1 LSB": r6(dither_bound(0.5, SIG_R / LSB_W))},
               "dither_sd_lsb": r6(SIG_R / LSB_W)}
g = rail_gain(INP["e58_tau_s"]["aifoundry3"]["minion_w"], SP_PASS_S)
fc["rail"] = {"tau_s": INP["e58_tau_s"]["aifoundry3"]["minion_w"], "delay_s": SP_PASS_S, "quad_gain": r6(g),
              "rail_w_per_minion": r6(RAIL_W), "rail_contrast_w_per_minion": r6(RAIL_W * g),
              "rail_over_board": INP["e180_anchor"]["rail_over_board"]}
pw = {}
for model in ("base", "pess"):
    pw.setdefault("N", {})[model] = dict(zip(("verdicts", "halfwidth_w"), sim_null(counts_L[0], model)))
    v, hw, j, _ = sim_ratio(counts_L, L_SMALL, L_LARGE, model, DELTA_L, do_jump=True, seed=1)
    v8, hw8, _, _ = sim_ratio(counts_L, L_SMALL, L_LARGE, model, DELTA_L, gain_small=0.8, seed=2)
    v9, _, _, _ = sim_ratio(counts_L, L_SMALL, L_LARGE, model, DELTA_L, gain_small=0.9, seed=3)
    _, _, jj, _ = sim_ratio(counts_L, L_SMALL, L_LARGE, model, DELTA_L, jump=(48, 0.05), do_jump=True, seed=4)
    pw.setdefault("L", {})[model] = {"if linear": v, "halfwidth": hw, "if small steps read 0.8": v8, "if small steps read 0.9": v9,
                                     "J seen if linear (false alarm)": j, "J seen if a 0.05 W jump from n = 48": jj}
    v, hw, _, ex = sim_ratio(counts_P, P_SMALL, P_LARGE, model, DELTA_P, seed=5)
    v8, _, _, ex8 = sim_ratio(counts_P, P_SMALL, P_LARGE, model, DELTA_P, gain_small=0.8, seed=6)
    _, _, _, ex29 = sim_ratio(counts_P, P_SMALL, P_LARGE, model, DELTA_P, gain_small=E178_RATIO, seed=7)
    pw.setdefault("P", {})[model] = {"if linear": v, "halfwidth": hw, "EXCLUDED if linear": ex, "if small steps read 0.8": v8,
                                     "EXCLUDED if small steps read 0.8": ex8,
                                     "EXCLUDED if small steps read E178's 0.29": ex29}
pw["C"] = sim_scan()
rows = tel_card1()
ma, Ma = [x[0] for x in rows], [x[1] for x in rows]
fc["card1_sram"] = {
    "H-MIX": {"min_over_avg": r6(c.median(ma)), "max_over_avg": r6(c.median(Ma)),
              "f": r6((c.median(ma) / c.median(Ma) + 1) / 2), "band_min_over_avg": [0.55, 0.71], "band_max_over_avg": [1.40, 1.78],
              "band_f": [0.65, 0.75], "level_spread_max": 0.06,
              "q150_committed": {"idle": INP["q150_sram"]["card1_sram"]["idle"], "busy": INP["q150_sram"]["card1_sram"]["busy"]},
              "september_samples": len(rows), "sample_sd_min_over_avg": r6(c.fsd(ma))},
    "control": {"minion": {"min_over_avg": INP["q150_sram"]["card1_minion_noc"]["minion_w"]["min_over_avg"],
                           "max_over_avg": INP["q150_sram"]["card1_minion_noc"]["minion_w"]["max_over_avg"]},
                "noc": {"min_over_avg": INP["q150_sram"]["card1_minion_noc"]["noc_w"]["min_over_avg"],
                        "max_over_avg": INP["q150_sram"]["card1_minion_noc"]["noc_w"]["max_over_avg"]}},
    "tau_s": {"sram": [INP["e58_tau_s"]["aifoundry1-c1"]["sram_w"], [0.44, 0.64]],
              "minion": [INP["e58_tau_s"]["aifoundry1-c1"]["minion_w"], [0.90, 1.35]],
              "noc": [INP["e58_tau_s"]["aifoundry1-c1"]["noc_w"], [0.90, 1.25]]},
    "restart_first_nonzero": {"sram": INP["q150_sram"]["card1_sram_restart_by_100ms"]["300"], "band": [0.72, 0.82]},
    "share_ratio_c1_over_a3": None, "glitch_rate": INP["e172_glitch"]["rate"], "glitch_band": [0.0003, 0.0015]}
b3 = [x for x in INP["catalogue"]["sram_set"] if x["cfg"] in DS["B3"]["cfgs"]]
sr = sorted(x["share_ratio_c1_over_a3"] for x in b3)
fc["card1_sram"]["share_ratio_c1_over_a3"] = {"median_of_b3_set": r6(c.median(sr)), "n": len(sr), "min": sr[0], "max": sr[-1],
                                              "september_28_median": INP["catalogue"]["sram_share_ratio_median"]}
pw["M"] = sim_hmix(rows)
res["forecasts"] = fc
res["power"] = pw
res["card_minutes"] = {"aifoundry3": {"expected": round(PLAN["arm_S"]["est_s"] / 60.0 + 11 * 10 / 60.0 + 1.0, 1), "cap": 135},
                       "aifoundry1-c1": {"expected": round(PLAN["arm_B"]["est_s"] / 60.0 + 7 * 10 / 60.0 + 1.0, 1), "cap": 25}}

if TEXT:
    L = []
    L.append("E184 forecasts and power (power_e184.py), %d draws a case" % REPS)
    for k, m in MODELS.items():
        L.append("noise %-4s: refresh sd %.4f W, rho %.3f, %d refreshes a block, block sd %.4f W, drift %.3f W, quad sd %.4f W" %
                 (k, m["refresh_sd_w"], m["rho"], m["refreshes_per_block"], m["block_sd_w"], m["drift_sd_w"], m["quad_sd_w"]))
    L.append("step per minion (board): E180 %.3f mW (se %.3f), catalogue %.3f mW, band %s W" %
             (S_W * 1e3, S_SE_W * 1e3, S_CAT_W * 1e3, fc["step_w_per_minion"]["band_95"]))
    L.append("operating point: target %.3f W, M_op forecast %d shires, M_s forecast %d shires" %
             (fc["operating_point"]["target_board_w"], fc["operating_point"]["m_op_forecast"], fc["operating_point"]["m_s_forecast"]))
    L.append("carry: code 1024 at %s W (11.7 / 12.0 / 12.3 V), LSB %.4f W; dither bound %s" % (CARRY_W, LSB_W, fc["carry"]["dither_bound_lsb"]))
    L.append("rail: quad gain %.3f, %.3f mW a minion, contrast %.3f mW a minion" % (g, RAIL_W * 1e3, RAIL_W * g * 1e3))
    for rule in ("N", "L", "P"):
        for model in ("base", "pess"):
            L.append("E184-%s %s: %s" % (rule, model, json.dumps(pw[rule][model], sort_keys=True)))
    for model in ("base", "pess"):
        L.append("E184-C %s: t* %.3f; %s" % (model, pw["C"][model]["t_crit_family_5pct"], json.dumps(pw["C"][model]["power"], sort_keys=True)))
    L.append("card 1 SRAM (September, %d samples): min/avg %.4f, max/avg %.4f, f %.4f; E184-M power %s" %
             (len(rows), c.median(ma), c.median(Ma), fc["card1_sram"]["H-MIX"]["f"], json.dumps(pw["M"], sort_keys=True)))
    L.append("B3 share ratio, the %d no-prefill configurations: median %.4f [%s, %s]" % (len(sr), c.median(sr), sr[0], sr[-1]))
    L.append("card-minutes: %s" % json.dumps(res["card_minutes"], sort_keys=True))
    print("\n".join(L))
else:
    print(json.dumps(res, indent=1, sort_keys=True))
