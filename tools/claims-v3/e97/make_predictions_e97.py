#!/usr/bin/env python3
"""E97 (Q132): write predictions-e97.json, the frozen numbers of the registration (E97.md). Run once, before the claim, from anywhere:

    /usr/bin/python3 tools/claims-v3/e97/make_predictions_e97.py > tools/claims-v3/e97/predictions-e97.json

Inputs, every one a committed file, read here and never retyped: E78's and E86's switching powers (e78.json, e86.json items.<name>.D
and .S, aifoundry3 card 0, 600 MHz), E89's measured coefficients (e89.json) and raw passes (the launch coverage), the heat chain fitted to E89's
raw passes (desk/chain_e89.json), the lab's thermal model's chain (docs/findings/11-thermal-model.md, copied below with its source), E71's
idle slope on this card, and E73's heat path. The three heat predictions are simulated by closed_loop() below; none uses a number from E97.
"""
import gzip
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e97_common as c  # noqa: E402

ROOT = c.ROOT
DATA = os.path.join(ROOT, "docs/reports/data")
# docs/findings/11-thermal-model.md, "Thermal stage" table (aifoundry2, September, before the October cooling changes)
LAB_TAU = [1.5, 4.0, 60.0, 150.0, 400.0, 2500.0]
LAB_R = [0.106, 0.050, 0.234, 0.136, 0.860, 0.081]
# docs/reports/data/2026-10-27-e71-idle-slope-aifoundry3/README.md: aifoundry3's idle slope, 6 cycles, W per degC
E71 = {"51-58": 0.3200, "54-58": 0.3276, "58-62": 0.3803, "58-65": 0.3957, "56-66": 0.3858}
E71_L = 36.0    # the published law's scale, degC: P = c + A exp((T - 80)/36) (2026-09-21-horace-aifoundry2/model.json)
# docs/reports/data/2026-10-27-e73-camera-frequencies/README.md, results 3 and 6: aifoundry2, the camera on the back of the board
E73 = {"G0_mK_per_W": [250.5, 300.0], "G0_ci_mK_per_W": [217.0, 292.0], "tau_s": 16.0, "lag_s": 1.0,
       "shares": "63% of a step in 17 s, 95% in 49 s"}
T_IDLE = 51.4   # the 34-sensor mean of a rested card at night: the firmware's 50-51 C plus E89's ~1 C (live history, 31 Oct; E89 result 3)


def e71_leak_a():
    """A of the law P = c + A exp((T - 80)/36), from E71's mean slope over 58-62 C on this card"""
    return E71["58-62"] * 4.0 / (math.exp((62 - 80) / E71_L) - math.exp((58 - 80) / E71_L))   # P(62) - P(58) = 4 x the mean slope


def closed_loop(S_eff, tau, R, A, Ti=T_IDLE, dur=3600.0, stop_C=None, reduced_S=None, dt=0.5):
    """The die above idle under board power P = S_eff + leak(T) - leak(Ti), through the chain R, tau, which is open loop (board power in, die
    out). stop_C: the mean at which a natural hold moves to reduced_S. Returns {t: (rise, dP)} on a 0.5 s grid plus the stop's time."""
    xs = [0.0] * len(tau)
    a = [math.exp(-dt / t) for t in tau]
    leak = lambda T: A * math.exp((T - 80.0) / E71_L)  # noqa: E731
    out, ts, s, n = [], None, S_eff, int(dur / dt)
    for i in range(n):
        T = Ti + sum(xs)
        if stop_C is not None and ts is None and T >= stop_C:
            ts = i * dt
            s = reduced_S if reduced_S is not None else 0.0
        elif stop_C is not None and ts is not None and T >= stop_C and i * dt > ts + 60.0:
            s = 0.0             # the stop again in the reduced phase: the hold ends
        P = s + min(leak(T) - leak(Ti), 500.0)
        xs = [ak * x + (1 - ak) * Rk * P for x, ak, Rk in zip(xs, a, R)]
        out.append((T - Ti, P))
    return out, ts


def at(series, s, dt=0.5):
    return series[min(len(series) - 1, int(s / dt))]


def launch_coverage():
    """E89's launches (--seconds 6.8, back to back) from its committed raw pass: the share of time a kernel runs, over the K halves"""
    p = os.path.join(DATA, "2026-10-31-e89-heat-low-power/aifoundry3/e89/p8910/runs.jsonl")
    by = {}
    for line in open(p):
        r = json.loads(line)
        if r["role"] == "K":
            by.setdefault((r["block"], r["half"]), []).append(r)
    vals = []
    for rr in by.values():
        rr.sort(key=lambda r: r["t_start_ms"])
        on = sum(r["t_end_ms"] - r["t_start_ms"] for r in rr)
        vals.append(on / (rr[-1]["t_end_ms"] - rr[0]["t_start_ms"]))
    return sum(vals) / len(vals)


def main():
    e78 = json.load(open(os.path.join(DATA, "2026-10-31-e78-kinds-energy-matrix/e78.json")))["items"]
    e86 = json.load(open(os.path.join(DATA, "2026-10-31-e86-real-tensors-energy/e86.json")))["items"]
    e89 = json.load(open(os.path.join(DATA, "2026-10-31-e89-heat-low-power/e89.json")))
    chain = json.load(open(os.path.join(HERE, "desk", "chain_e89.json")))
    fit = chain["fits"]["lab_grid"]
    b89 = e89["blocks"]
    # ---- Part A -----------------------------------------------------------------------------------------------------------------------
    zero_H = [b89[b]["H_proj_ref_phase"]["mean"] for b in ("i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "f32ones")]
    H_zero = sum(zero_H) / len(zero_H)
    H_idle = b89["i8zero"]["H_proj_ref_phase"]["mean"]
    H_ref = b89["f32randn"]["H_proj_ref_phase"]["mean"]
    k2 = [b89[b]["step2_C_per_W_E78"]["mean"] for b in ("i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "i8zero", "f32ones")]
    k2m = sum(k2) / len(k2)
    pf = [b89[b]["P_fund_over_E78"] for b in ("i8full", "i8gauss", "i8small", "i8sp50", "f32randn", "i8zero", "f32ones")]
    pfm = sum(pf) / len(pf)
    blocks = {}
    for b, (k, z) in c.BLOCKS.items():
        src = e78 if k in e78 else e86
        key = "S" if z == "idle" else "D"
        w = src[k][key]["mean"]
        H = H_idle if z == "idle" else (H_zero if b != c.REF_BLOCK else H_ref)
        p = (2 / math.pi) * w * pfm
        blocks[b] = {"kind": k, "ref": z, "w_source": "e78.json" if k in e78 else "e86.json", "w_quantity": key, "w": round(w, 4),
                     "w_ci95": round(src[k][key].get("ci95") or 0.0, 4), "S": round(src[k]["S"]["mean"], 4), "D": round(src[k]["D"]["mean"], 4),
                     "extrapolation_S_x_0118_C": round(0.118 * src[k]["S"]["mean"], 3),
                     "pred_board_fund_W": round(p, 3), "pred_T_fund_C": round(H * p, 3), "pred_H": round(H, 4),
                     "pred_r_board": round(H / H_ref, 3), "pred_r_minion": 1.0,
                     "pred_step2_C": round(w * (0.118 if b == c.REF_BLOCK else k2m), 3)}
    # ---- Part B: three heat paths, simulated closed loop --------------------------------------------------------------------------------
    A = e71_leak_a()
    cov = launch_coverage()
    # a launch runs whole kernels until its --seconds have passed (E89: 6.8 s, 14 fp32 kernels of 0.491 s), so 3.5 s is eight kernels in every 7 s
    red_share = math.ceil(c.REDUCED_LAUNCH_S / 0.491) * 0.491 / c.REDUCED_PERIOD_S
    S = {h: e78[it]["S"]["mean"] for h, it in c.HOLD_ITEMS.items()}
    paths = {"e89_fit": (fit["tau"], fit["R"]), "lab_model": (LAB_TAU, LAB_R),
             "e73_one_pole": ([c_ for c_ in [E73["tau_s"]]], [sum(E73["G0_mK_per_W"]) / 2000.0])}
    stop_mean = c.MAX_C + 1.0            # the firmware's reading runs about 1 degC below the 34-sensor mean (E89 result 3)
    holds = {}
    for name, (tau, R) in paths.items():
        one = {}
        for h, it in c.HOLD_ITEMS.items():
            s_nat = S[h] * cov
            ser, ts = closed_loop(s_nat, tau, R, A, dur=c.HOLD_S, stop_C=stop_mean, reduced_S=S[h] * red_share)
            r60, r300, r1800 = at(ser, 60.0)[0], at(ser, 300.0)[0], at(ser, c.HOLD_S - 1)[0]
            dP = at(ser, c.HOLD_S - 1)[1]
            leak_share = (dP - (S[h] * red_share if ts is not None else s_nat)) / dP if abs(dP) < 400 else None
            T_ss = T_IDLE + r1800
            k = A / E71_L * math.exp((T_ss - 80.0) / E71_L)
            one[h] = {"item": it, "S_E78_W": round(S[h], 3), "S_eff_natural_W": round(s_nat, 3), "stop_time_s": ts,
                      "rise_60s_C": round(r60, 3), "rise_300s_C": round(r300, 3), "rise_30min_C": round(r1800, 3),
                      "die_mean_30min_C": round(T_ss, 2), "dP_board_30min_W": round(dP, 3) if abs(dP) < 400 else None,
                      "rise_per_board_W_30min": round(r1800 / dP, 4) if abs(dP) < 400 else None,
                      "rise_per_S_eff_30min": round(r1800 / (S[h] * red_share if ts is not None else s_nat), 4),
                      "share_60s": round(r60 / r1800, 3), "share_300s": round(r300 / r1800, 3),
                      "leak_share_of_dP": None if leak_share is None else round(leak_share, 3),
                      "loop_gain": round(k * sum(R), 3), "k_W_per_C": round(k, 4)}
            ser0, _ = closed_loop(s_nat, tau, R, A, dur=4 * c.HOLD_S)
            r2h = at(ser0, 4 * c.HOLD_S - 1)[0]
            one[h]["rise_2h_no_stop_C"] = round(r2h, 2) if r2h < 60.0 else None   # None: on this chain and leakage law, no steady state short of a runaway
        holds[name] = one
    p1, p3 = holds["e89_fit"]["H1"], holds["e89_fit"]["H3"]
    lab_open = sum(LAB_R)
    lab_30 = sum(r * (1 - math.exp(-c.HOLD_S / t)) for r, t in zip(LAB_R, LAB_TAU))
    ratio_S = p3["rise_per_S_eff_30min"] / p1["rise_per_S_eff_30min"]
    lib = hashlib.sha256(open(os.path.join(c.TOOLS, "lib.sh"), "rb").read()).hexdigest()
    out = {
        "experiment": "E97", "card": "aifoundry3 card 0 (600 MHz, pinned by its boot-time TDP 0; never set)",
        "registration": "tools/claims-v3/e97/E97.md",
        "harness": {
            "reused_unchanged_sha256": {rel: c.sha256_file(p) for rel, p in c.reused_files().items()},
            "block_e89_sh_sha256": c.sha256_file(os.path.join(c.TOOLS, "e89", "block_e89.sh")),
            "lib_sh_sha256": lib, "data_dir": "docs/reports/data/2026-11-01-e97-heat-low-power-steady/",
            "passes_A": [c.FIRST_PASS, c.SECOND_PASS], "pass_B": c.HOLDS_PASS, "smoke": [c.SMOKE_A, c.SMOKE_B],
            "half_s": 30.0, "cycles": 2, "lead_s": 20.0, "launch_s": c.LAUNCH_S, "idle_s": 15.0, "gate_c": 62.0, "gate_max_s": 60.0,
            "max_c": c.MAX_C, "resume_c": c.RESUME_C, "hard_c": c.HARD_C, "max_board_w": c.MAX_BOARD_W,
            "deadline": c.DEADLINE, "sampler": "tools/claims-v3/e89/pvt_sample.py",
            "order": "the 28 low-power blocks shuffled with Random('E97|aifoundry3|<pass>'), then f32randn",
            "order_9710": c.pass_order("aifoundry3", 9710), "order_9711": c.pass_order("aifoundry3", 9711)},
        "plan_B": {"hold_s": c.HOLD_S, "chain_s": c.CHAIN_S, "reduced_launch_s": c.REDUCED_LAUNCH_S, "reduced_period_s": c.REDUCED_PERIOD_S,
                   "rise_level_C": c.RISE_LEVEL_C, "slope_C_per_5min": c.SLOPE_C_PER_5MIN, "rest_min_s": c.REST_MIN_S, "r0_max_s": c.R0_MAX_S,
                   "r_max_s": c.R_MAX_S, "idle_window_s": c.IDLE_WINDOW_S, "left_full_s": c.LEFT_FULL_S, "left_chain_s": c.LEFT_CHAIN_S,
                   "left_h3_s": c.LEFT_H3_S, "h3_min_s": c.H3_MIN_S, "r3_min_s": c.R3_MIN_S},
        "e89_coefficients": {"H_ref": round(H_ref, 4), "H_against_zeros": round(H_zero, 4), "H_against_idle": round(H_idle, 4),
                             "step2_C_per_W_mean": round(k2m, 4), "P_fund_over_E78_mean": round(pfm, 4),
                             "int8_zeros_step2_C": b89["i8zero"]["step2_C"]["mean"], "int8_zeros_step2_ci95": b89["i8zero"]["step2_C"]["ci95"]},
        "blocks": blocks,
        "heat_paths": {
            "e89_fit": {"source": "desk/chain_e89.json (lab_grid): the Foster chain fitted to E89's raw passes on this card", "tau": fit["tau"],
                        "R": [round(x, 4) for x in fit["R"]], "R_total_C_per_board_W": round(fit["total"], 4)},
            "lab_model": {"source": "docs/findings/11-thermal-model.md (aifoundry2, September)", "tau": LAB_TAU, "R": LAB_R,
                          "R_total_C_per_board_W": lab_open, "open_loop_30min": round(lab_30, 4)},
            "e73_one_pole": {"source": "docs/reports/data/2026-10-27-e73-camera-frequencies/README.md (aifoundry2, the camera on the back of the board)",
                             **E73}},
        "leak_law": {"source": "E71 on this card, in the published law's form", "A_W": round(A, 3), "L_C": E71_L, "e71_slopes": E71,
                     "slope_at_C": {str(T): round(A / E71_L * math.exp((T - 80.0) / E71_L), 4) for T in (52, 55, 60, 62, 65, 70, 72, 75, 78)}},
        "launch_coverage_natural": round(cov, 4), "compute_share_reduced": round(red_share, 4), "t_idle_C": T_IDLE, "stop_mean_C": stop_mean,
        "holds": holds,
        "rules": {
            "E97-R0": {"what": "the per-sensor reading works: 34 valid sensors, and the firmware's integer mean rebuilt from the codes equals minshire_avg (E89-R0)",
                       "min_share_with_34": 0.99, "min_share_eq": 0.95, "pred": "PASS"},
            "E97-R1": {"what": "each block's temperature fundamental is detected: the 95% lower bound > 0 (FAIL: upper bound < 0)", "pred": "PASS x29"},
            "E97-R2": {"what": "heat per board W: r = H_K / H_ref inside the band at 95% (FAIL: wholly outside)", "band": [0.80, 1.25],
                       "pred": "PASS x28 with the lap as the unit; with the pass as the unit (primary) PASS or INCONCLUSIVE, no FAIL"},
            "E97-R3": {"what": "the session's tie: H_ref against E89's, the same card and reading: the point inside the band, and the passes within 0.006 degC/W",
                       "band": [round(0.95 * H_ref, 4), round(1.05 * H_ref, 4)], "max_pass_spread": 0.006, "pred": "PASS"},
            "E97-R4": {"what": "the 2 s window: (step2/W)_K over (step2/W)_ref inside the band at 95% (FAIL: wholly outside)", "band": [0.70, 1.43],
                       "pred": "PASS x28 with the lap as the unit, INCONCLUSIVE allowed for the weakest with the pass as the unit; no FAIL"},
            "E97-R5": {"what": "heat per minion-rail W: r on the SP's minion rail, the reference's SE included, inside the band at 95% (FAIL: wholly outside)",
                       "band": [0.90, 1.11], "pred": "PASS, INCONCLUSIVE allowed with the pass as the unit; no FAIL"},
            "E97-R6": {"what": "one coefficient per minion-rail W: every block's point r_minion inside the band (FAIL: three or more outside; else INCONCLUSIVE)",
                       "band": [0.93, 1.07], "pred": "PASS"},
            "E97-R7": {"what": "the extrapolation's bias over the 25 kinds: the 2 s rise over idle / (S x 0.118): the median inside the band and at least 80% of the kinds inside the wide band (FAIL: the median outside)",
                       "band": [1.00, 1.20], "wide_band": [0.85, 1.30], "pred": "PASS, median about 1.09"},
            "E97-B1": {"what": "a hold is steady: |slope| over its last 10 minutes (5 for a chained hold) at most this, degC per minute", "max_abs_slope": 0.02, "pred": "PASS for each hold that ran"},
            "E97-B2a": {"what": "the rise per board W at the hold's end against the lab's thermal model, 1.42-1.47 degC/W open loop", "band": [1.25, 1.70], "pred": "FAIL for each hold: the model is aifoundry2's, in September"},
            "E97-B2b": {"what": "the rise per board W against E73's zero-frequency gain, 250-300 mK/W", "band": [0.217, 0.35], "pred": "FAIL for each hold: the camera's band and place are not the die's steady rise"},
            "E97-B2c": {"what": "the rise per board W against the chain fitted to E89 on this card, 0.86 degC/W", "band": [0.70, 1.05], "pred": "PASS for each hold"},
            "E97-B3": {"what": "linear in board power: rise per board W, H3 over H1 and H2 over H1 (a band each)", "band_H3_H1": [0.85, 1.15], "band_H2_H1": [0.90, 1.11],
                       "pred": "PASS; H3/H1 about 0.95-1.00 (E89's r carried over), H2/H1 about 1.00"},
            "E97-B4": {"what": "linear in minion-rail power: rise per minion-rail W, H3 over H1 and H2 over H1", "band": [0.90, 1.11], "pred": "PASS, about 1.00"},
            "E97-B5": {"what": "not linear in switching power: rise per W of E78's S at the hold's compute share, H3 over H1: leakage's feedback predicts more than 1", "band": [1.02, 1.25],
                       "pred_ratio": round(ratio_S, 3), "pred": "PASS"},
            "E97-B6": {"what": "how much of H1's rise arrives by 60 s and by 5 min, as shares of its steady rise",
                       "band_60s": [round(p1["share_60s"] - 0.12, 2), round(p1["share_60s"] + 0.12, 2)], "band_300s": [round(p1["share_300s"] - 0.10, 2), min(1.0, round(p1["share_300s"] + 0.10, 2))],
                       "alternatives": {"lab_model": {"share_60s": holds["lab_model"]["H1"]["share_60s"], "share_300s": holds["lab_model"]["H1"]["share_300s"]},
                                        "e73_one_pole": {"share_60s_at_least": 0.90}},
                       "pred": "PASS on the E89 chain's bands"},
            "E97-B7": {"what": "the idle law on the cooling curves against E71's slopes on this card: 51-58 and 58-62 C of the firmware's reading, each within 10%",
                       "band_51_58": [round(E71["51-58"] * 0.9, 4), round(E71["51-58"] * 1.1, 4)], "band_58_62": [round(E71["58-62"] * 0.9, 4), round(E71["58-62"] * 1.1, 4)], "pred": "PASS"},
            "E97-B8": {"what": "leakage's contribution at each hold's end: its share of the board's rise, and the loop gain k(T) x rise per board W",
                       "leak_share_band": {h: [round(holds["e89_fit"][h]["leak_share_of_dP"] - 0.08, 3), round(holds["e89_fit"][h]["leak_share_of_dP"] + 0.08, 3)] for h in c.HOLD_ITEMS},
                       "loop_gain_band": {h: [round(holds["e89_fit"][h]["loop_gain"] - 0.10, 3), round(holds["e89_fit"][h]["loop_gain"] + 0.10, 3)] for h in c.HOLD_ITEMS},
                       "page_section_4": "0.5-0.6 near the trip on the lab model's 1.47 degC/W", "pred": "PASS, so this card's loop near 62-72 C is well under the page's 0.5-0.6"},
            "E97-B9": {"what": "closure: (the board's rise minus leakage's) over E78's S at the hold's compute share", "band": [0.85, 1.15], "pred": "PASS"},
            "E97-B10": {"what": "fp32 random at its natural chain reaches the lab's 78 C reading: seconds from the hold's start (FAIL: no stop in the hold, which then is a steady state at full duty)",
                        "band_s": [150.0, 480.0], "pred_s": p3["stop_time_s"], "pred": "PASS"},
            "E97-B0": {"what": "a hold's gates: every sample at 600 MHz, minion 515-530 mV, at least 5 samples a second, at most 1% of launches failed, every record's cycles per op within 0.5% of 546 (fp32) / 318 (int8). A hold failing one scores no rule", "pred": "PASS"},
        },
    }
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
