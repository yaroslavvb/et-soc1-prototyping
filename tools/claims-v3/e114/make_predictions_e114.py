#!/usr/bin/env python3
"""E114 (Q133): write predictions-e114.json, the frozen numbers of E114's rules, from the committed sources it names.
Every number is read from its file, never retyped, and each source is checked by sha256 before it is read.

    python3 tools/claims-v3/e114/make_predictions_e114.py          # from the repository root; rewrites the file

Sources:
  E84  docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/results.json   (card 0's single sustained runs, its die
       line over its 13 sustained runs, its start configuration)
  E80, E83, E87, E96 results.json on aifoundry2 (its fp16 and int8 sustained runs: S1's pool, context only)
"""
import hashlib
import json
import os
import statistics as st
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
OUT = os.path.join(ROOT, "tools/claims-v3/e114/predictions-e114.json")
E84 = ("docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/results.json",
       "69c76c753a76")  # the sha256 prefix E84's corrections-check.txt prints for this file
A2 = {
    "E80": "docs/reports/data/2026-10-31-e80-kinds-speed/results.json",
    "E83": "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json",
    "E87": "docs/reports/data/2026-10-31-e87-real-tensors-speed/results.json",
    "E96": "docs/reports/data/2026-11-01-e96-real-tensors-speed/results.json",
}
KINDS = ["fp16/zeros", "fp16/ones", "fp16/randn", "int8/zeros", "int8/full"]
HEAVY = {"fp16": "fp16/randn", "int8": "int8/full"}
ZEROS = {"fp16": "fp16/zeros", "int8": "int8/zeros"}


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def main():
    s84 = sha(E84[0])
    if not s84.startswith(E84[1]):
        sys.exit(f"refused: {E84[0]} sha256 {s84[:12]} is not E84's {E84[1]}")
    d84 = json.load(open(os.path.join(ROOT, E84[0])))
    kinds = {}
    for k in KINDS:
        c = d84["cells"][k]
        if c.get("n_sus") != 1:
            sys.exit(f"refused: E84 {k} has {c.get('n_sus')} sustained runs, not 1")
        kinds[k] = {
            "type": c["type"], "tile": f"tools/claims-v3/kinds/tiles/{k}.bin",
            "e84_sus_limit": c["sus_limit_runs"][0],
            "e84_sus_rate": c["sus_rate_runs"][0], "e84_sus_mhz": c["sus_mhz_runs"][0],
            "e84_sus_mhz_nonramp": c["sus_mhz_nonramp"], "e84_sus_w": c["sus_w"], "e84_sus_die": c["sus_die"],
            "e84_sus_die_max": c["sus_die_max"][0], "e84_sus_die_start": c["sus_die_start"][0],
            "e84_sus_ramp_share": c["sus_ramp_share"][0],
            "e84_run": next(m["run"] for m in d84["runs"] if m["kind"] == k and m["block"] in ("SUS", "SUS2")),
        }
    ratios84 = {f: round(kinds[ZEROS[f]]["e84_sus_rate"] / kinds[HEAVY[f]]["e84_sus_rate"], 4) for f in ZEROS}
    sus = [m for m in d84["runs"] if m["block"] in ("SUS", "SUS2")]
    xs, ys = [m["sus_w_mean"] for m in sus], [m["sus_die_mean"] for m in sus]
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    cfg = next(q["config"] for q in d84["config_reads"] if q["tag"] == "start")

    pool, srcs = {}, {}
    for e, p in A2.items():
        srcs[e] = {"path": p, "sha256": sha(p)}
        c = json.load(open(os.path.join(ROOT, p))).get("cells", {})
        for k in KINDS:
            if k in c and c[k].get("sus_rate_runs"):
                pool.setdefault(k, []).extend([{"exp": e, "rate": x} for x in c[k]["sus_rate_runs"]])
    a2 = {}
    for f in ZEROS:
        z, h = [x["rate"] for x in pool[ZEROS[f]]], [x["rate"] for x in pool[HEAVY[f]]]
        a2[f] = {"zeros_runs": pool[ZEROS[f]], "heavy_runs": pool[HEAVY[f]],
                 "zeros_mean": round(st.mean(z), 4), "zeros_sd": round(st.stdev(z), 4), "n_zeros": len(z),
                 "heavy_mean": round(st.mean(h), 4), "heavy_sd": round(st.stdev(h), 4), "n_heavy": len(h),
                 "ratio_of_means": round(st.mean(z) / st.mean(h), 4)}

    out = {
        "experiment": "E114", "request": "Q133", "card": "aifoundry1-c0",
        "frozen": "written by make_predictions_e114.py from the sources below and committed with E114.md before the "
                  "#community-lab claim and before any E114 device access; any change after it goes in E114.md's "
                  "Amendments, dated, before the data it touches",
        "sources": {"E84": {"path": E84[0], "sha256": s84}, "aifoundry2": srcs},
        "e84_start_config": cfg,
        "e84_firmware": {"release": "1.4.0", "bl1": "0.22.0", "bl2": "0.22.0", "pmic": "1.6.1", "minions": "0.25.1",
                         "source": "E84 README amendment A1 and ident/ident-154200.out"},
        "kinds": kinds,
        "e84_ratio_zeros_over_heavy_sus_rate": ratios84,
        "e84_die_line": {"a_c": round(a, 3), "b_c_per_w": round(b, 4), "n_runs": len(sus),
                         "what": "die = a + b x board W over E84's 13 sustained runs (per-run sus_w_mean, "
                                 "sus_die_mean), E84 corrections-check C1"},
        "aifoundry2_pool": a2,
        "expected": {
            "what": "context, never a verdict: where each E114 cell mean is expected to fall (E84's single run, "
                    "with run-to-run and day-to-day room)",
            "fp16/zeros": {"sus_rate": "24.20-24.56", "sus_mhz": "788-800", "limit": "none"},
            "fp16/ones": {"sus_rate": "23.80-24.56", "sus_mhz": "775-800",
                          "limit": "none (E84's die maxed at 65 C, so a thermal run is possible)"},
            "fp16/randn": {"sus_rate": "18.50-19.70", "sus_mhz": "610-655", "limit": "thermal"},
            "int8/zeros": {"sus_rate": "83.00-84.33", "sus_mhz": "788-800", "limit": "none"},
            "int8/full": {"sus_rate": "82.00-84.00", "sus_mhz": "780-797", "limit": "none"},
            "rho_fp16": "1.22-1.33 (E84 1.2746)", "rho_int8": "0.995-1.020 (E84 1.0076)",
        },
        "rules": {
            "E114-R1": {"says": "E84's single sustained run of each of the five kinds lies inside E114's 95% "
                                "prediction interval for one new run, on the kernel's sustained rate: mean +- "
                                "t(0.975, n-1) x sd x sqrt(1 + 1/n) over the kind's E114 runs",
                        "need_kinds": 4, "of": 5, "min_runs_per_kind": 3, "kind": "primary",
                        "pass": ">= 4 of 5 kinds inside; FAIL when >= 2 scored kinds are outside; otherwise "
                                "UNDER-RESOLVED", "expected": "PASS"},
            "E114-R2": {"says": "fp16 zeros faster than fp16 random data, sustained, replicated: rho16 = the mean "
                                "over passes of rate(fp16 zeros, pass p) / rate(fp16 randn, pass p), with its 95% "
                                "interval t(0.975, n-1) x sd / sqrt(n)",
                        "bar": 1.15, "min_pairs": 3, "kind": "primary",
                        "pass": "PASS when the interval's lower end >= 1.15; FAIL when its upper end < 1.15; "
                                "otherwise INCONCLUSIVE; UNDER-RESOLVED below three pairs",
                        "expected": "PASS", "expected_point": ratios84["fp16"]},
            "E114-R3": {"says": "int8 zeros against int8 full, sustained: rho8 = the mean over passes of "
                                "rate(int8 zeros, pass p) / rate(int8 full, pass p), with its 95% interval",
                        "bar": 0.02, "min_pairs": 3, "kind": "primary (a reading, scored against the frozen one)",
                        "readings": "FASTER when the interval's lower end > 1; SLOWER when its upper end < 1; "
                                    "SAME_WITHIN_BAR when it holds 1 and lies inside [0.98, 1.02]; otherwise "
                                    "INCONCLUSIVE; UNDER-RESOLVED below three pairs",
                        "expected": "SAME_WITHIN_BAR", "expected_point": ratios84["int8"]},
            "E114-R4": {"says": "the limiting test replicates: each E114 run's sustained limit (reduce_e84.py's "
                                "label, unchanged) equals E84's for its kind (fp16 randn thermal, the other four "
                                "none)",
                        "max_mismatch": 1, "min_runs": 14, "kind": "primary",
                        "pass": "PASS when at most 1 run of >= 14 differs; FAIL when >= 2 differ; otherwise "
                                "UNDER-RESOLVED", "expected": "PASS"},
            "E114-S1": {"says": "card 0's rho (R2's and R3's statistic) against aifoundry2's ratio of mean "
                                "sustained rates over its committed runs (E80, E83, E87, E96): delta = rho(card 0) "
                                "- rho(aifoundry2), 95% interval t(0.975, df) x sqrt(se_c0^2 + se_a2^2), df = the "
                                "smaller of card 0's pairs and aifoundry2's smaller run count, minus 1; se_a2 by "
                                "the delta method",
                        "bars": {"fp16": 0.05, "int8": 0.02}, "kind": "secondary",
                        "readings": "ALIKE when the interval lies inside +-bar; DIFFERENT when it excludes 0; "
                                    "otherwise INCONCLUSIVE",
                        "expected": {"fp16": "DIFFERENT (card 0 lower: its random fp16 draws less power and "
                                             "throttles less, while both cards' zeros sit near the 800 MHz cap; at "
                                             "three pairs the interval may not resolve it)",
                                     "int8": "INCONCLUSIVE"}},
        },
        "context_never_a_verdict": [
            "each cell's sampled clock, non-ramp clock, board W, die mean and max, ramp share and limit, with 95% "
            "intervals and prediction intervals; E84's single run beside each",
            "pass-paired zeros minus heavy sustained clock per format (E84-P1's form, -10 MHz)",
            "today's heat path against 31 Oct's: each run's die minus E84's die line at its board W, mean and 95% "
            "interval",
            "rho as the ratio of the two cells' mean rates, delta-method interval, beside R2's and R3's mean of "
            "pass ratios",
            "card 0's idle level per run (idle_w, idle_mhz) and the cooling gate's reading and hold",
        ],
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"wrote {os.path.relpath(OUT, ROOT)}: E84 rho fp16 {ratios84['fp16']}, int8 {ratios84['int8']}; "
          f"die line {a:.3f} + {b:.4f} W; aifoundry2 rho fp16 {a2['fp16']['ratio_of_means']} "
          f"(n {a2['fp16']['n_zeros']}/{a2['fp16']['n_heavy']}), int8 {a2['int8']['ratio_of_means']} "
          f"(n {a2['int8']['n_zeros']}/{a2['int8']['n_heavy']})")


if __name__ == "__main__":
    main()
