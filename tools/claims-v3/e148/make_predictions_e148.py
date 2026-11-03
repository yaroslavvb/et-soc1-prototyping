#!/usr/bin/env python3
"""E148 (Q138): write predictions-e148.json and predictions-e148.txt - the frozen readings of the two-row arm, from the TIMA bench's counts
(tools/claims-v3/e148/desk/bench-e148.json, Q136(c)'s binary run by desk/bench_e148.py) and E129's committed reduction on this card
(docs/reports/data/2026-11-02-e129-int8-noissue/e129.json, scored.json), plus the rules, the plan, the stops and the harness's sha256.

    python3 tools/claims-v3/e148/make_predictions_e148.py        # from the repo root; standard library only

The readings of D21 = N2 - N1, where N_a = S(a.int8.zeros) - S(a.fp32.zeros) (S over the idle bracket, paired inside a pass):
  W (the walk)      all of E129's N - N1 is TenC's read-address walk: D21 = (N - N1) x dW(r2) / dW(r16), dW the new-address TenC reads a second
                    (int8; fp32 reads TenC at one frozen address in the card's order, Q136(c) result 3, so it adds none)
  T (the A path)    all of N - N1 is int8's TenTMP staging, its 64-bit A reads: D21 = (N - N1) x (dT(r2) - dT(r1)) / (dT(r16) - dT(r1))
  C (per cycle)     none of it is per-row: N1 is work int8 does every working cycle, scaled by the TIMA controls' clocked bits a second:
                    D21 = N1 x (dC(r2) / dC(r1) - 1)
each a 95% range from E129's own 95% intervals of N - N1 and N1; and the bench at its own constants (Q136(c)'s M2, M4, I3; card 1's scale), in the
card's order (fp32 after int8, the fp32 streams run with +pre=2) and from reset.
SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "rtl-sim", "tima_bench"))
import price as pr  # noqa: E402

E129 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e129-int8-noissue")
MINIONS, CLOCK = 1024, 600e6
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ci(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T95[n - 1] * sd / math.sqrt(n)
    return {"mean": m, "half": h, "lo": m - h, "hi": m + h, "n": n, "sd": sd}


def main():
    B = json.load(open(os.path.join(HERE, "desk", "bench-e148.json")))
    E = json.load(open(os.path.join(E129, "e129.json")))
    pp = E["per_pass"]
    # E129's measured duty (rate over the clock's ops a second at the card's cycles), per arm, mean over its passes and both formats
    duty = {}
    for arm, cyc in (("m0", {"fp32": 544.001, "int8": 318.001}), ("m0r1", {"fp32": 62.0, "int8": 62.0})):
        v = [pp[p][f"{arm}.{f}.zeros"]["rate"] / (MINIONS * CLOCK / c) for p in pp for f, c in cyc.items()]
        duty[arm] = sum(v) / len(v)
    duty["m0r2"] = duty["m0r1"]          # the same short-op launch: E129's one-row duty
    N = [pp[p]["m0.int8.zeros"]["S"] - pp[p]["m0.fp32.zeros"]["S"] for p in sorted(pp)]
    N1 = [pp[p]["m0r1.int8.zeros"]["S"] - pp[p]["m0r1.fp32.zeros"]["S"] for p in sorted(pp)]
    dN = [a - b for a, b in zip(N, N1)]
    cN, cN1, cdN = ci(N), ci(N1), ci(dN)
    st = B["streams"]
    cyc = B["card_cycles_predicted"]
    rate = {f"{arm}.{f}": MINIONS * CLOCK * duty[arm] / cyc[f"{arm}.{f}"] for arm in ("m0", "m0r1", "m0r2") for f in ("fp32", "int8")}

    def per_s(name, arm, fmt):
        return pr.scale(st[name]["candidates"], rate[f"{arm}.{fmt}"])

    # int8 - fp32 a second, in the card's order (pre.) and from reset
    d_card, d_reset, raw = {}, {}, {}
    for arm in ("m0", "m0r1", "m0r2"):
        i8 = per_s(f"{arm}.int8.zeros", arm, "int8")
        fpc = per_s(f"pre.{arm}.fp32.zeros", arm, "fp32")
        fpr = per_s(f"{arm}.fp32.zeros", arm, "fp32")
        raw[arm] = {"int8": i8, "fp32_card_order": fpc, "fp32_from_reset": fpr}
        d_card[arm], d_reset[arm] = pr.sub(i8, fpc), pr.sub(i8, fpr)

    def q(d, arm):
        return {"tenc_newaddr": d[arm]["tenc"]["reads_newaddr"], "tentmp_64bit": d[arm]["scp"]["rd64"],
                "tima_ctrl_bits": d[arm]["tima_ctrl"]["int8_enabled_clocked"], "tenc_reads": d[arm]["tenc"]["reads"],
                "tena_writes": d[arm]["scp"]["tena_writes"], "scp_reads": d[arm]["scp"]["reads"], "scp_bits": d[arm]["scp"]["bits_requested"],
                "tenb_writes": d[arm]["tenb"]["writes"], "working_cycles": d[arm]["tima_clk_en_cycles"]}
    Q = {arm: q(d_card, arm) for arm in ("m0", "m0r1", "m0r2")}
    Qr = {arm: q(d_reset, arm) for arm in ("m0", "m0r1", "m0r2")}
    fW = (Q["m0r2"]["tenc_newaddr"] - Q["m0r1"]["tenc_newaddr"]) / (Q["m0"]["tenc_newaddr"] - Q["m0r1"]["tenc_newaddr"])
    fT = (Q["m0r2"]["tentmp_64bit"] - Q["m0r1"]["tentmp_64bit"]) / (Q["m0"]["tentmp_64bit"] - Q["m0r1"]["tentmp_64bit"])
    gC = raw["m0r2"]["int8"]["tima_ctrl"]["int8_enabled_clocked"] / raw["m0r1"]["int8"]["tima_ctrl"]["int8_enabled_clocked"] - 1.0
    fA = (Q["m0r2"]["tena_writes"] - Q["m0r1"]["tena_writes"]) / (Q["m0"]["tena_writes"] - Q["m0r1"]["tena_writes"])

    def rng(f, c):
        a, b = f * c["lo"], f * c["hi"]
        return {"point": f * c["mean"], "lo": min(a, b), "hi": max(a, b)}
    readings = {
        "W": {"what": "all of E129's N - N1 is TenC's read-address walk (a price per TenC read at a new address)", "factor": fW,
              "of": "E129's N - N1", **rng(fW, cdN)},
        "T": {"what": "all of E129's N - N1 is int8's TenTMP staging, its 64-bit A reads (a price per 64-bit A read into TenTMP)", "factor": fT,
              "of": "E129's N - N1", **rng(fT, cdN)},
        "C": {"what": "none of N is per-row: N1 is work int8 does every working cycle, scaled by the TIMA controls' clocked bits a second", "factor": gC,
              "of": "E129's N1", **rng(gC, cN1)},
    }
    readings_reported = {
        "A": {"what": "all of E129's N - N1 is TenA's writes (int8 - fp32); excluded beforehand by Q136(c)'s fp32-level bound (at most 0.14 W on card 1)",
              "factor": fA, "of": "E129's N - N1", **rng(fA, cdN)},
    }
    # the bench at its own constants, D21 = (r2 - r1) contrast of the (int8 - fp32) terms a second
    K = pr.constants()
    bench = {}
    for order, dd in (("card_order", d_card), ("from_reset", d_reset)):
        tt = {}
        for arm in ("m0", "m0r1", "m0r2"):
            i8t = pr.scale(pr.terms(st[f"{arm}.int8.zeros"]["candidates"]), rate[f"{arm}.int8"])
            nm = f"pre.{arm}.fp32.zeros" if order == "card_order" else f"{arm}.fp32.zeros"
            fpt = pr.scale(pr.terms(st[nm]["candidates"]), rate[f"{arm}.fp32"])
            tt[arm] = pr.sub(i8t, fpt)
        bench[order] = {}
        for kn, kv in K.items():
            w2 = pr.price(tt["m0r2"], kv, kv["card1"])
            w1 = pr.price(tt["m0r1"], kv, kv["card1"])
            w16 = pr.price(tt["m0"], kv, kv["card1"])
            bench[order][kn] = {"N2": sum(w2.values()), "N1": sum(w1.values()), "N": sum(w16.values()), "D21": sum(w2.values()) - sum(w1.values())}
        vals = [v["D21"] for v in bench[order].values()]
        bench[order]["range_D21"] = {"lo": min(vals), "hi": max(vals)}
    # the two-term model (reported, no verdict): per pass, N - N1 = pw dW16 + pt (dT16 - dT1), D21 = pw dW2 + pt (dT2 - dT1)
    design = {"a11": Q["m0"]["tenc_newaddr"], "a12": Q["m0"]["tentmp_64bit"] - Q["m0r1"]["tentmp_64bit"],
              "a21": Q["m0r2"]["tenc_newaddr"], "a22": Q["m0r2"]["tentmp_64bit"] - Q["m0r1"]["tentmp_64bit"]}
    reg = {
        "experiment": "E148",
        "question": "Where int8's no-issue excess goes on aifoundry1 card 1 (kinds page section 11 item 11): with two A rows, TenC's read-address walk turns on while int8's TenTMP staging falls a second against one row. D21 = N2 - N1 says which of E129's readings carries the 0.70 W one A row removed.",
        "card": {"name": "aifoundry1-c1", "host": "aifoundry1", "device": 1, "lock": "/run/lock/etsoc-shire1.lock", "clock_mhz": 600,
                 "config_gate": {"expected": {"tdp_w": 65, "temp_threshold_c": 65}},
                 "what": "aifoundry1 card 1, release 1.4.0 (BL1 and BL2 0.22.0, PMIC 1.3.0, minions 0.25.1, E82 A1), 600 MHz; TDP 65 W / threshold 65 C (read, never set)"},
        "sources": {"bench": "tools/claims-v3/e148/desk/bench-e148.json (Q136(c)'s bench, binary sha256 " + B["binary_sha256"] + ")",
                    "e129": "docs/reports/data/2026-11-02-e129-int8-noissue/e129.json > per_pass (the primary, 3 passes)",
                    "q136c": "docs/reports/data/2026-11-02-q136c-tima-bench/README.md"},
        "arms": {"m0": [16, 16, 0], "m0r1": [1, 16, 0], "m0r2": [2, 16, 0]},
        "items": ["m0.fp32.zeros", "m0.int8.zeros", "m0r1.fp32.zeros", "m0r1.int8.zeros", "m0r2.fp32.zeros", "m0r2.int8.zeros"],
        "anchors": ["fp32.zeros", "int8.zeros"], "runs_per_pass": 14, "burnin_runs_per_pass": 2,
        "passes": list(range(14810, 14820)), "smoke_pass": 14801, "stoptest_pass": 14802, "min_kept_passes": 3,
        "budget": {"card_minutes": 40, "from": "the session's first config read", "to": "its last", "queue_limit_s": 2400 - 150,
                   "no_session_after": "2026-11-02 23:00 PST", "passes_end_by": "2026-11-02 23:45 PST", "every_run_ends_by": "2026-11-02 23:50 PST"},
        "plan": {"stops": {"board_w": 66.0, "die_hottest_shire_c": 72.0, "stoptest_board_w": 1.0, "stoptest_die_c": 1.0, "run_e78_max_c": 72,
                           "how": "E142's: the newest line of the running sampler's file, read before every launch and every 0.1 s while waiting, and by an in-run watcher every 0.1 s that writes the STOP file the host program checks before every launch; tested before the smoke by block_e148.sh --stoptest (each of die, board, watch must exit 6 with a STOP line read from a live sample)"}},
        "primary_reduction": "reduce_e148.py --leak 0.2414 (E82's slope on this card, E124's and E129's primary), card 1's launch-gap dips removed (E82 A2)",
        "set_aside_rule": {"rule": "The primary reduction (E78's pass gates as they apply to E148's pass, E129's) carries every verdict if it keeps at least 3 passes. If it keeps fewer, the relaxed reduction (reduce_e148.py --relax-tie: GATES['tie_drift_w'] 0.60 -> 99 W) carries them if it keeps more: a pass set aside ONLY by pi's drift is restored, any other stays out, and the verdicts are labelled 'scored under the set-aside rule'. Fewer than 3 kept passes in the carrying reduction: every rule reads NOT-SCORED. The relaxed reduction is always reported. No pass is added after any reduction is read, and none is chosen after the fact.",
                           "relaxed_gate": {"tie_drift_w": 99.0}},
        "bench_per_s_card_order": Q, "bench_per_s_from_reset": Qr, "duty": duty, "rates_pred_ops_per_s": rate,
        "cycles_pred": {k: float(v) for k, v in cyc.items()},
        "e129_reference": {"N": cN, "N1": cN1, "N_minus_N1": cdN, "per_pass_N": N, "per_pass_N1": N1},
        "readings": readings, "readings_reported": readings_reported, "bench_constants": bench, "two_term_design": design,
        "rules": {
            "W1": {"statistic": "D21 = N2 - N1, N_a = S(a.int8.zeros) - S(a.fp32.zeros), per kept pass, mean and 95% t interval over passes",
                   "line": "each reading X in {W, T, C}: CONSISTENT if D21's 95% interval overlaps X's frozen 95% range, else EXCLUDED",
                   "verdicts": "WALK if W is consistent and T and C are excluded; A-PATH if T is consistent and W and C are excluded; PER-CYCLE if C is consistent and W and T are excluded; NONE if all three are excluded; else INCONCLUSIVE (naming the consistent set)"},
            "W2": {"statistic": "D21", "line": "D21's 95% lower bound > 0", "verdicts": "RISES (two rows cost int8 more than one: the A path is excluded as the sole per-row carrier) / NOT-RISES"},
            "R6": {"statistic": "median cycles per op of each of the six arms", "line": "|measured - predicted| <= 2.0", "predicted": {k: float(v) for k, v in cyc.items()},
                   "verdicts": "PASS / FAIL per arm (m0r2's 96.0 and 94.0 are new: the silicon's schedule at two rows)"},
            "Y1": {"statistic": "N", "line": "PASS if lower >= 0.84 W; FAIL if upper < 0.84 W (E124's line)", "verdicts": "PASS / FAIL / INCONCLUSIVE"},
            "V1": {"statistic": "N1 against N/2 (E129's V1, this session alone)", "line": "PER-ROW if N1's upper < N/2; PER-CYCLE if N1's lower >= N/2",
                   "verdicts": "PER-ROW / PER-CYCLE / INCONCLUSIVE"},
            "V1p": {"statistic": "N1 - N/2 per pass, pooled over E129's 3 passes (known when this was written) and E148's kept passes, mean and 95% t interval",
                    "line": "PER-ROW if upper < 0; PER-CYCLE if lower >= 0; at least 6 passes in all", "verdicts": "PER-ROW / PER-CYCLE / INCONCLUSIVE / NOT-SCORED"},
            "T1": {"statistic": "N, N1 against E129's (1.566, 0.865 W)", "line": "|difference| <= 0.5 W each", "verdicts": "PASS / FAIL per cell; a failed cell labels every verdict and removes none"},
        },
        "reported_no_verdict": ["N - N1 and D21 per pass", "S(m0r2.f) - S(m0r1.f) per format", "the two-term solve per pass: pw (fJ a TenC read at a new address) and pt (pJ a 64-bit A read into TenTMP)",
                                "N2's out-of-sample prediction by each reading (N1 of this session + the reading's D21) against N2 measured", "every arm's D, S, rate and cycles"],
        "harness": {},
    }
    e = json.load(open(os.path.join(ROOT, "tools/claims-v3/e129/predictions-e129.json")))["harness"]
    reg["harness"]["reused_unchanged_sha256"] = {rel: sha(os.path.join(ROOT, rel)) for rel in e["reused_unchanged_sha256"]}
    changed = [rel for rel, w in e["reused_unchanged_sha256"].items() if reg["harness"]["reused_unchanged_sha256"][rel] != w]
    reg["harness"]["reused_changed_since_e129"] = changed
    reg["harness"]["box_binaries_sha256"] = dict(e["box_binaries_sha256"])
    reg["harness"]["box_binaries_sources"] = e.get("box_binaries_sources")
    reg["harness"]["e148_card_files_sha256"] = {f"tools/claims-v3/e148/{f}": sha(os.path.join(HERE, f)) for f in sorted(os.listdir(HERE))
                                                if f.endswith((".py", ".sh")) and f != "make_predictions_e148.py"}
    json.dump(reg, open(os.path.join(HERE, "predictions-e148.json"), "w"), indent=1, sort_keys=False)
    L = [f"E148 frozen readings of D21 = N2 - N1 (W), aifoundry1 card 1, from the bench's counts and E129's reduction",
         f"E129: N {cN['mean']:+.3f} [{cN['lo']:+.3f}, {cN['hi']:+.3f}]; N1 {cN1['mean']:+.3f} [{cN1['lo']:+.3f}, {cN1['hi']:+.3f}]; N - N1 {cdN['mean']:+.3f} [{cdN['lo']:+.3f}, {cdN['hi']:+.3f}]",
         f"predicted card cycles: {json.dumps(cyc)}", f"predicted rates (1e9/s): " + ", ".join(f"{k} {v / 1e9:.4f}" for k, v in rate.items())]
    for k, r in list(readings.items()) + list(readings_reported.items()):
        L.append(f"reading {k}: factor {r['factor']:+.4f} of {r['of']}: D21 {r['point']:+.3f} W [{r['lo']:+.3f}, {r['hi']:+.3f}]  ({r['what']})")
    for order in ("card_order", "from_reset"):
        L.append(f"bench constants, {order}: D21 {bench[order]['range_D21']['lo']:+.4f} to {bench[order]['range_D21']['hi']:+.4f} W; "
                 + "; ".join(f"{kn}: N2 {v['N2']:+.3f} N1 {v['N1']:+.3f}" for kn, v in bench[order].items() if kn != "range_D21"))
    L.append("per second, int8 - fp32 in the card's order (1e10): " + "; ".join(
        f"{arm}: walk {Q[arm]['tenc_newaddr'] / 1e10:.2f}, TenTMP {Q[arm]['tentmp_64bit'] / 1e10:.3f}, TIMA ctrl bits {Q[arm]['tima_ctrl_bits'] / 1e10:.1f}, TenC reads {Q[arm]['tenc_reads'] / 1e10:.2f}, TenA {Q[arm]['tena_writes'] / 1e10:.3f}"
        for arm in ("m0", "m0r1", "m0r2")))
    open(os.path.join(HERE, "predictions-e148.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    if changed:
        print("WARNING: reused files changed since E129's freeze:", changed)


if __name__ == "__main__":
    main()
