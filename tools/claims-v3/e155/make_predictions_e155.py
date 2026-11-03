#!/usr/bin/env python3
"""E155 (Q139): write predictions-e155.json and predictions-e155.txt - the frozen readings of the three-row arm and its K = 8 partner, from the TIMA
bench's counts (tools/claims-v3/e155/desk/bench-e155.json, Q136(c)'s binary run by desk/bench_e155.py) and E148's committed reduction on this card
(docs/reports/data/2026-11-02-e148-int8-excess/e148.json, ten passes; scored.json > reported.two_term), plus the rules, the plan, the stops and the
harness's sha256. Nothing is fitted to E155's data: none exists when this runs.

    python3 tools/claims-v3/e155/make_predictions_e155.py        # from the repo root; standard library only

The statistic. N_a = S(a.int8.zeros) - S(a.fp32.zeros) (S over the run's idle bracket, paired inside a pass); D31 = N3 - N1, the rise from one A row
to three (E148's D21 construction at three rows). Its frozen prediction under each reading is a COUNT TERM plus a SHARED PER-OP TERM:
  count terms (int8 - fp32 a second in the card's order, from the bench; scaled to E148's measured parts, 95% ranges from E148's ten-pass intervals)
    Wn  the walk counted in TenC reads at a new address (E148's registered count): (N - N1) x newaddr/s(m0r3) / newaddr/s(m0)
    Wt  the walk counted in TenC read-address bits that change (E148's post hoc count, registered here): (N - N1) x tog/s(m0r3) / tog/s(m0)
    C   per cycle: N1 scaled by the TIMA controls' clocked bits a second: N1 x (bits/s(m0r3) / bits/s(m0r1) - 1)
    T   the A path: (N - N1) x (A/s(m0r3) - A/s(m0r1)) / (A/s(m0) - A/s(m0r1)), A = 64-bit A reads into TenTMP
    reported: E148's registered two-term solve (pw a new-address read, pt a 64-bit A read) at three rows
  the shared per-op term: at three rows int8 runs 110 cycles an op and fp32 128, so int8 does 16 % more ops a second; with equal per-op energy in
    the two formats (the premise), N3 carries E_op x (r_int8 - r_fp32), E_op = fp32's per-op energy at K = 16 (its per-op work and its B traffic),
    frozen from E148's fp32: [S(m0r1) - S(m0r2)] / [rate(m0r1) - rate(m0r2)] per pass, mean and 95 % interval.
The per-op premise, F3: e(f) = [D(m0r3k8.f) - D(m0r3.f)] / [rate(m0r3k8.f) - rate(m0r3.f)] (E109's construction at three rows), de = e(int8) - e(fp32).
int8's counts a second change between the partner and the arm (the walk and TenTMP by -11 %, the TIMA controls by -6 %), which biases the raw de
low; its frozen allowance b is that change priced under each frozen reading (Wn, Wt, C, two-term), and F3 scores de - b_mid with the range's half
in quadrature.
SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E148 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e148-int8-excess")
MINIONS, CLOCK = 1024, 600e6
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "sd": sd}


def main():
    B = json.load(open(os.path.join(HERE, "desk", "bench-e155.json")))
    E = json.load(open(os.path.join(E148, "e148.json")))
    SC = json.load(open(os.path.join(E148, "scored.json")))
    pp = E["per_pass"]
    keys = sorted(pp, key=int)
    # E148's measured duty (rate over the clock's ops a second at the card's cycles): the 16-row arm, and the short ops (one and two rows)
    cyc148 = {"m0": {"fp32": 544.001, "int8": 318.001}, "m0r1": {"fp32": 62.0, "int8": 62.0}, "m0r2": {"fp32": 96.0, "int8": 94.0}}

    def duty_of(arms):
        v = [pp[p][f"{arm}.{f}.zeros"]["rate"] / (MINIONS * CLOCK / c) for p in keys for arm in arms for f, c in cyc148[arm].items()]
        return sum(v) / len(v)
    duty = {"m0": duty_of(["m0"]), "short": duty_of(["m0r1", "m0r2"])}
    duty_arm = {"m0": duty["m0"], "m0r1": duty["short"], "m0r3": duty["short"], "m0r3k8": duty["short"]}
    N = [pp[p]["m0.int8.zeros"]["S"] - pp[p]["m0.fp32.zeros"]["S"] for p in keys]
    N1 = [pp[p]["m0r1.int8.zeros"]["S"] - pp[p]["m0r1.fp32.zeros"]["S"] for p in keys]
    dN = [a - b for a, b in zip(N, N1)]
    Eop = [(pp[p]["m0r1.fp32.zeros"]["S"] - pp[p]["m0r2.fp32.zeros"]["S"]) / (pp[p]["m0r1.fp32.zeros"]["rate"] - pp[p]["m0r2.fp32.zeros"]["rate"])
           for p in keys]
    cN, cN1, cdN, cE = ci(N), ci(N1), ci(dN), ci(Eop)
    cyc = B["card_cycles_predicted"]
    st = B["streams"]
    rate = {f"{arm}.{f}": MINIONS * CLOCK * duty_arm[arm] / cyc[f"{arm}.{f}"] for arm in ("m0", "m0r1", "m0r3", "m0r3k8") for f in ("fp32", "int8")}

    def ps(arm, field):
        """int8 - fp32 a second in the card's order (fp32 streams run after two int8 ops, +pre=2), for one bench field."""
        ci8 = st[f"{arm}.int8.zeros"]["candidates"]
        cfp = st[f"pre.{arm}.fp32.zeros"]["candidates"]
        g = {"newaddr": lambda c: c["tenc"]["reads_newaddr"], "tog": lambda c: c["tenc"]["raddr_tog"], "A": lambda c: c["scp"]["rd64"],
             "bits": lambda c: c["tima_ctrl"]["int8_enabled_clocked"], "tenc_reads": lambda c: c["tenc"]["reads"],
             "tenb": lambda c: c["tenb"]["writes"], "tena": lambda c: c["scp"]["tena_writes"], "scp_reads": lambda c: c["scp"]["reads"],
             "regs": lambda c: c["registers"]["clocked"], "work": lambda c: c["working_cycles"]}[field]
        return g(ci8) * rate[f"{arm}.int8"] - g(cfp) * rate[f"{arm}.fp32"]

    def pi8(arm, field):
        """int8 alone, a second."""
        c = st[f"{arm}.int8.zeros"]["candidates"]
        g = {"newaddr": c["tenc"]["reads_newaddr"], "tog": c["tenc"]["raddr_tog"], "A": c["scp"]["rd64"],
             "bits": c["tima_ctrl"]["int8_enabled_clocked"], "tenb": c["tenb"]["writes"], "tena": c["scp"]["tena_writes"],
             "scp_reads": c["scp"]["reads"], "regs": c["registers"]["clocked"], "tenc_reads": c["tenc"]["reads"]}[field]
        return g * rate[f"{arm}.int8"]

    def pfp(arm, field):
        c = st[f"pre.{arm}.fp32.zeros"]["candidates"]
        g = {"tenb": c["tenb"]["writes"], "tena": c["scp"]["tena_writes"], "scp_reads": c["scp"]["reads"], "regs": c["registers"]["clocked"],
             "tenc_reads": c["tenc"]["reads"]}[field]
        return g * rate[f"{arm}.fp32"]

    fields = ("newaddr", "tog", "A", "bits", "tenc_reads", "tenb", "tena", "scp_reads", "regs")
    Q = {arm: {f: ps(arm, f) for f in fields} for arm in ("m0", "m0r1", "m0r3", "m0r3k8")}
    I8 = {arm: {f: pi8(arm, f) for f in fields} for arm in ("m0", "m0r1", "m0r3", "m0r3k8")}
    FP = {arm: {f: pfp(arm, f) for f in ("tenb", "tena", "scp_reads", "regs", "tenc_reads")} for arm in ("m0", "m0r1", "m0r3", "m0r3k8")}
    fWn = Q["m0r3"]["newaddr"] / Q["m0"]["newaddr"]
    fWt = Q["m0r3"]["tog"] / Q["m0"]["tog"]
    fC = Q["m0r3"]["bits"] / Q["m0r1"]["bits"] - 1.0
    fT = (Q["m0r3"]["A"] - Q["m0r1"]["A"]) / (Q["m0"]["A"] - Q["m0r1"]["A"])
    dr3 = rate["m0r3.int8"] - rate["m0r3.fp32"]
    shared = {"what": "E_op x (rate(m0r3.int8) - rate(m0r3.fp32)): equal per-op energy in the two formats at K = 16, E_op frozen from E148's fp32 [S(m0r1) - S(m0r2)] / [rate(m0r1) - rate(m0r2)]",
              "E_op_pJ": {k: (v * 1e12 if isinstance(v, float) else v) for k, v in cE.items()}, "delta_rate_per_s": dr3,
              "point": cE["mean"] * dr3, "lo": cE["lo"] * dr3, "hi": cE["hi"] * dr3}

    def reading(what, factor, of, c):
        a, b = factor * c["lo"], factor * c["hi"]
        cnt = {"point": factor * c["mean"], "lo": min(a, b), "hi": max(a, b)}
        return {"what": what, "factor": factor, "of": of, "count_term": cnt,
                "point": cnt["point"] + shared["point"], "lo": cnt["lo"] + shared["lo"], "hi": cnt["hi"] + shared["hi"]}
    readings = {
        "Wn": reading("the walk counted in TenC reads at a new address (E148's registered count): all of E148's N - N1 is the walk", fWn, "E148's N - N1", cdN),
        "Wt": reading("the walk counted in TenC read-address bits that change (E148's post hoc count, registered here): all of E148's N - N1 is the walk", fWt, "E148's N - N1", cdN),
        "C": reading("per cycle: none of the rise is per-row; N1 is work int8 does every working cycle, scaled by the TIMA controls' clocked bits a second", fC, "E148's N1", cN1),
        "T": reading("the A path: all of E148's N - N1 is int8's TenTMP staging, its 64-bit A reads (excluded as the sole per-row carrier by E148's W2)", fT, "E148's N - N1", cdN),
    }
    tt = SC["reported"]["two_term"]
    pw, pt = tt["pw_fJ_per_newaddr_read"], tt["pt_pJ_per_64bit_A_read"]
    two = pw["mean"] * 1e-15 * Q["m0r3"]["newaddr"] + pt["mean"] * 1e-12 * (Q["m0r3"]["A"] - Q["m0r1"]["A"])
    readings_reported = {
        "two_term": {"what": "E148's registered two-term solve (reported there): pw a TenC read at a new address, pt a 64-bit A read", "pw_fJ": pw["mean"],
                     "pt_pJ": pt["mean"], "count_term": {"point": two}, "point": two + shared["point"]},
        "null": {"what": "a third row changes nothing (D31 = 0)", "point": 0.0},
        "null_shared": {"what": "a third row changes nothing but the shared per-op term", "point": shared["point"], "lo": shared["lo"], "hi": shared["hi"]},
    }
    # F3's allowance: int8's counts a second, the K = 8 partner against the three-row arm, priced under each frozen reading, over int8's rate change
    dri = rate["m0r3k8.int8"] - rate["m0r3.int8"]
    drf = rate["m0r3k8.fp32"] - rate["m0r3.fp32"]
    p_wn = cdN["mean"] / I8["m0"]["newaddr"]
    p_wt = cdN["mean"] / I8["m0"]["tog"]
    p_c = cN1["mean"] / I8["m0r1"]["bits"]
    p_t1 = cdN["mean"] / (I8["m0"]["A"] - I8["m0r1"]["A"])
    dW = I8["m0r3k8"]["newaddr"] - I8["m0r3"]["newaddr"]
    dWt = I8["m0r3k8"]["tog"] - I8["m0r3"]["tog"]
    dA = I8["m0r3k8"]["A"] - I8["m0r3"]["A"]
    dC = I8["m0r3k8"]["bits"] - I8["m0r3"]["bits"]
    bias = {"Wn": p_wn * dW / dri * 1e12, "Wt": p_wt * dWt / dri * 1e12, "C": p_c * dC / dri * 1e12,
            "two_term": (pw["mean"] * 1e-15 * dW + pt["mean"] * 1e-12 * dA) / dri * 1e12}
    bias_reported = {"T (excluded as sole carrier by E148)": p_t1 * dA / dri * 1e12,
                     "B traffic, both formats (int8's TenB writes a second change by %.3g, fp32's by %.3g; at 0.10-0.16 pJ a write)" % (
                         I8["m0r3k8"]["tenb"] - I8["m0r3"]["tenb"], FP["m0r3k8"]["tenb"] - FP["m0r3"]["tenb"]):
                     [0.10 * ((I8["m0r3k8"]["tenb"] - I8["m0r3"]["tenb"]) / dri - (FP["m0r3k8"]["tenb"] - FP["m0r3"]["tenb"]) / drf),
                      0.16 * ((I8["m0r3k8"]["tenb"] - I8["m0r3"]["tenb"]) / dri - (FP["m0r3k8"]["tenb"] - FP["m0r3"]["tenb"]) / drf)]}
    blo, bhi = min(bias.values()), max(bias.values())
    allowance = {"by_reading_pJ": bias, "reported_pJ": bias_reported, "lo_pJ": blo, "hi_pJ": bhi, "mid_pJ": (blo + bhi) / 2, "half_pJ": (bhi - blo) / 2,
                 "rate_change_int8_per_s": dri, "rate_change_fp32_per_s": drf,
                 "int8_counts_partner_minus_arm_per_s": {"newaddr": dW, "tog": dWt, "A": dA, "bits": dC},
                 "fractions_of_arm": {"newaddr": dW / I8["m0r3"]["newaddr"], "tog": dWt / I8["m0r3"]["tog"], "A": dA / I8["m0r3"]["A"], "bits": dC / I8["m0r3"]["bits"]}}
    # the reported walk at one row's schedule: Q31k = S(m0r3k8.int8) - S(m0r1.int8), equal int8 schedule (62 cycles, the same TIMA bits, TenTMP and
    # TenC reads a second): its walk part under Wn and Wt (C and T predict 0 for it); B's TenB writes a second differ (K = 8 halves them)
    qk = {"what": "S(m0r3k8.int8) - S(m0r1.int8): int8 at one row's schedule with the walk on; its walk part under each count (C and T: 0); int8's TenB writes a second change by %.4g (B halved) and are not in the walk part" % (
              I8["m0r3k8"]["tenb"] - I8["m0r1"]["tenb"]),
          "walk_Wn": {"point": p_wn * I8["m0r3k8"]["newaddr"], "lo": cdN["lo"] / I8["m0"]["newaddr"] * I8["m0r3k8"]["newaddr"],
                      "hi": cdN["hi"] / I8["m0"]["newaddr"] * I8["m0r3k8"]["newaddr"]},
          "walk_Wt": {"point": p_wt * I8["m0r3k8"]["tog"], "lo": cdN["lo"] / I8["m0"]["tog"] * I8["m0r3k8"]["tog"],
                      "hi": cdN["hi"] / I8["m0"]["tog"] * I8["m0r3k8"]["tog"]},
          "same_schedule_check": {f: [st["m0r3k8.int8.zeros"]["candidates"]["tenc"]["reads"], st["m0r1.int8.zeros"]["candidates"]["tenc"]["reads"]] if f == "tenc_reads" else None
                                  for f in ("tenc_reads",)},
          "tenb_change_per_s": I8["m0r3k8"]["tenb"] - I8["m0r1"]["tenb"]}
    # precision expected from E148's per-pass spread of D21 (a four-arm contrast like D31)
    sd21 = SC["stats"]["D21"]["sd"]
    expect = {f"{n}_passes": T95[n - 1] * sd21 / math.sqrt(n) for n in (3, 4, 6, 8, 10)}
    cyc_pred = {k: float(v) for k, v in cyc.items() if not k.startswith("m0.")}
    reg = {
        "experiment": "E155",
        "question": "int8's no-issue floor by shape on aifoundry1 card 1 (kinds page section 11 item 11; Q138's final critic rank 10): which count the per-row part follows (TenC's read-address walk against the per-cycle reading; address-bit toggles against new-address reads), the per-op premise, and what stays at one row. D31 = N3 - N1 from one A row to three, with K = 8 partners at three rows in both formats.",
        "card": {"name": "aifoundry1-c1", "host": "aifoundry1", "device": 1, "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}},
                 "what": "aifoundry1 card 1, release 1.4.0 (BL1 and BL2 0.22.0), 600 MHz; TDP 65 W / threshold 65 C (read, never set)"},
        "sources": {"bench": "tools/claims-v3/e155/desk/bench-e155.json (Q136(c)'s bench, binary sha256 " + B["binary_sha256"] + ")",
                    "e148": "docs/reports/data/2026-11-02-e148-int8-excess/e148.json > per_pass (the primary, 10 passes); scored.json > reported.two_term, stats.D21.sd",
                    "q136c": "docs/reports/data/2026-11-02-q136c-tima-bench/README.md"},
        "arms": {"m0r1": [1, 16, 0], "m0r3": [3, 16, 0], "m0r3k8": [3, 8, 0]},
        "items": ["m0r1.fp32.zeros", "m0r1.int8.zeros", "m0r3.fp32.zeros", "m0r3.int8.zeros", "m0r3k8.fp32.zeros", "m0r3k8.int8.zeros"],
        "anchors": ["fp32.zeros", "int8.zeros"], "runs_per_pass": 14, "burnin_runs_per_pass": 2,
        "passes": list(range(15510, 15520)), "smoke_pass": 15501, "stoptest_pass": 15502, "min_kept_passes": 3,
        "budget": {"card_minutes": 40, "from": "the session's first config read", "to": "its last", "queue_limit_s": 2400 - 150,
                   "no_session_after": "2026-11-03 10:30 PST", "passes_end_by": "2026-11-03 11:20 PST", "every_run_ends_by": "2026-11-03 11:30 PST"},
        "plan": {"stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "stale_line_s": 1.5, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0,
                           "stoptest_stale_s": 0.0, "run_e78_max_c": 72,
                           "how": "E148's (E142's): the newest line of the running sampler's file, read before every launch and every 0.1 s while waiting, and by an in-run watcher every 0.1 s that writes the STOP file the host program checks before every launch; NEW in E155 (E148's verifier, C7): a line older than stale_line_s also stops, in the guard and the watcher; tested before the smoke by block_e155.sh --stoptest (each of die, board, watch and stale must exit 6 with a STOP line read from a live sample)"}},
        "primary_reduction": "reduce_e155.py --leak 0.2414 (E82's slope on this card, E124's, E129's and E148's primary), card 1's launch-gap dips removed (E82 A2)",
        "set_aside_rule": {"rule": "The primary reduction (E78's pass gates as they apply to E155's pass, E148's) carries every verdict if it keeps at least 3 passes. If it keeps fewer, the relaxed reduction (reduce_e155.py --relax-tie: GATES['tie_drift_w'] 0.60 -> 99 W) carries them if it keeps more: a pass set aside ONLY by pi's drift is restored, any other stays out, and the verdicts are labelled 'scored under the set-aside rule'. Fewer than 3 kept passes in the carrying reduction: every rule reads NOT-SCORED. The relaxed reduction is always reported. No pass is added after any reduction is read, and none is chosen after the fact.",
                           "relaxed_gate": {"tie_drift_w": 99.0}},
        "bench_per_s_card_order": Q, "bench_per_s_int8": I8, "bench_per_s_fp32_card_order": FP, "duty": duty, "rates_pred_ops_per_s": rate,
        "cycles_pred": cyc_pred,
        "e148_reference": {"N": cN, "N1": cN1, "N_minus_N1": cdN, "E_op_fp32_pJ": {k: (v * 1e12 if k in ("mean", "half", "lo", "hi", "sd") else v) for k, v in cE.items()},
                           "per_pass_N": N, "per_pass_N1": N1, "two_term": {"pw_fJ": pw, "pt_pJ": pt}, "D21_sd_per_pass": sd21},
        "shared_per_op_term": shared, "readings": readings, "readings_reported": readings_reported, "f3_allowance": allowance,
        "q31k_reported": qk, "expected_D31_half_width_w": expect,
        "rules": {
            "F1": {"statistic": "D31 = N3 - N1, N_a = S(a.int8.zeros) - S(a.fp32.zeros), per kept pass, mean and 95% t interval over passes",
                   "line": "each reading X in {Wn, Wt, C, T}: CONSISTENT if D31's 95% interval overlaps X's frozen band (its count term's range from E148's 95% intervals plus the shared per-op term's range from E148's E_op interval), else EXCLUDED",
                   "verdicts": {"F1a (the walk against the per-cycle reading)": "WALK if Wn or Wt is consistent and C is excluded; PER-CYCLE if C is consistent and Wn and Wt are excluded; NEITHER if Wn, Wt and C are all excluded; else INCONCLUSIVE",
                                "F1b (address-bit toggles against new-address reads)": "TOGGLES if Wt is consistent and Wn excluded; NEW-ADDRESS if Wn is consistent and Wt excluded; NEITHER if both are excluded; INCONCLUSIVE if both are consistent",
                                "consistent_set": "the readings whose bands D31's interval overlaps, T included, reported beside the two verdicts"}},
            "F3": {"statistic": "de3 = e(int8) - e(fp32), e(f) = [D(m0r3k8.f) - D(m0r3.f)] / [rate(m0r3k8.f) - rate(m0r3.f)] per kept pass (E109's construction at three rows, measured rates), corrected by the frozen allowance: de3c = de3 - b_mid",
                   "line": "H = sqrt(h^2 + b_half^2), h the 95% t half-width of de3 over passes; BOUNDED if [de3c - H, de3c + H] lies inside (-30, +30) pJ; EXCEEDS if de3c - H > 30 or de3c + H < -30; else INCONCLUSIVE",
                   "verdicts": "BOUNDED / EXCEEDS / INCONCLUSIVE; the raw de3 (no allowance) reported beside it"},
            "R6": {"statistic": "median cycles per op of each of the six arms", "line": "|measured - predicted| <= 2.0", "predicted": cyc_pred,
                   "verdicts": "PASS / FAIL per arm (m0r3's 128.0 / 110.0 and m0r3k8's 72.0 / 62.0 are new: the silicon's schedule at three rows and at K = 8 there)"},
            "T1": {"statistic": "N1 against E148's (0.884 W)", "line": "|difference| <= 0.5 W", "verdicts": "PASS / FAIL; a failed cell labels every verdict and removes none"},
        },
        "reported_no_verdict": ["D31 and N3 per pass; N3's out-of-sample prediction by each reading (E148's N1 + the reading's D31) against N3 measured",
                                "D31 less the shared term measured in this session (E_op from this session's fp32 m0r1 against m0r3), and each count's one-term price fitted on it",
                                "the raw de3 and each format's e at three rows", "Q31k = S(m0r3k8.int8) - S(m0r1.int8) against the walk parts of Wn and Wt",
                                "every arm's D, S, rate and cycles; the leakage-auto, dips-kept and relaxed arms"],
        "harness": {},
    }
    e = json.load(open(os.path.join(ROOT, "tools/claims-v3/e148/predictions-e148.json")))["harness"]
    reg["harness"]["reused_unchanged_sha256"] = {rel: sha(os.path.join(ROOT, rel)) for rel in e["reused_unchanged_sha256"]}
    changed = [rel for rel, w in e["reused_unchanged_sha256"].items() if reg["harness"]["reused_unchanged_sha256"][rel] != w]
    reg["harness"]["reused_changed_since_e148"] = changed
    reg["harness"]["box_binaries_sha256"] = dict(e["box_binaries_sha256"])
    reg["harness"]["box_binaries_sources"] = e.get("box_binaries_sources")
    reg["harness"]["e155_card_files_sha256"] = {f"tools/claims-v3/e155/{f}": sha(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE))
                                                if f.endswith((".py", ".sh")) and f != "make_predictions_e155.py"}
    json.dump(reg, open(os.path.join(HERE, "predictions-e155.json"), "w"), indent=1, sort_keys=False)
    L = ["E155 frozen readings of D31 = N3 - N1, aifoundry1 card 1, from the bench's counts and E148's reduction (10 passes)",
         f"E148: N {cN['mean']:+.3f} [{cN['lo']:+.3f}, {cN['hi']:+.3f}]; N1 {cN1['mean']:+.3f} [{cN1['lo']:+.3f}, {cN1['hi']:+.3f}]; N - N1 {cdN['mean']:+.3f} [{cdN['lo']:+.3f}, {cdN['hi']:+.3f}]; "
         f"fp32's E_op {cE['mean'] * 1e12:.1f} pJ [{cE['lo'] * 1e12:.1f}, {cE['hi'] * 1e12:.1f}]",
         f"duty {json.dumps({k: round(v, 5) for k, v in duty.items()})}; predicted card cycles: {json.dumps(cyc_pred)}",
         "predicted rates (1e9/s): " + ", ".join(f"{k} {v / 1e9:.4f}" for k, v in rate.items()),
         f"shared per-op term: E_op x {dr3 / 1e9:.4f}e9 = {shared['point']:+.4f} W [{shared['lo']:+.4f}, {shared['hi']:+.4f}]"]
    for k, r in readings.items():
        L.append(f"reading {k}: factor {r['factor']:+.4f} of {r['of']}: count term {r['count_term']['point']:+.3f} [{r['count_term']['lo']:+.3f}, {r['count_term']['hi']:+.3f}]; "
                 f"D31 {r['point']:+.3f} W, band [{r['lo']:+.3f}, {r['hi']:+.3f}]  ({r['what']})")
    for k, r in readings_reported.items():
        L.append(f"reported {k}: D31 {r['point']:+.3f} W  ({r['what']})")
    L.append(f"F3 allowance (pJ, int8's counts partner - arm over int8's rate change {dri / 1e9:.3f}e9): " + ", ".join(f"{k} {v:+.1f}" for k, v in bias.items())
             + f"; mid {allowance['mid_pJ']:+.1f}, half {allowance['half_pJ']:.1f}; reported " + json.dumps({k: (round(v, 1) if isinstance(v, float) else [round(x, 2) for x in v]) for k, v in bias_reported.items()}))
    L.append("int8's counts a second, partner against arm (fractions): " + json.dumps({k: round(v, 4) for k, v in allowance["fractions_of_arm"].items()}))
    L.append(f"reported Q31k walk parts: Wn {qk['walk_Wn']['point']:+.3f} [{qk['walk_Wn']['lo']:+.3f}, {qk['walk_Wn']['hi']:+.3f}], Wt {qk['walk_Wt']['point']:+.3f} [{qk['walk_Wt']['lo']:+.3f}, {qk['walk_Wt']['hi']:+.3f}]; int8 TenB writes a second change {qk['tenb_change_per_s']:.4g}")
    L.append("expected D31 95% half-width from E148's D21 spread (W): " + ", ".join(f"{k} {v:.3f}" for k, v in expect.items()))
    L.append("per second, int8 - fp32 in the card's order (1e10): " + "; ".join(
        f"{arm}: walk {Q[arm]['newaddr'] / 1e10:.3f}, toggles {Q[arm]['tog'] / 1e10:.3f}, TenTMP {Q[arm]['A'] / 1e10:.3f}, TIMA bits {Q[arm]['bits'] / 1e10:.2f}, TenB {Q[arm]['tenb'] / 1e10:.2f}"
        for arm in ("m0", "m0r1", "m0r3", "m0r3k8")))
    open(os.path.join(HERE, "predictions-e155.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    if changed:
        print("WARNING: reused files changed since E148's freeze:", changed)


if __name__ == "__main__":
    main()
