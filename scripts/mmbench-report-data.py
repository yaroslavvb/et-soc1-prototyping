#!/usr/bin/env python3
"""Turn a scripts/mmbench-power.py run directory into the numbers and chart data for a report.

    scripts/mmbench-report-data.py build/mmbench-power
    scripts/mmbench-report-data.py docs/reports/data/2026-09-18-aifoundry2 \
        --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html

The run directory holds power.csv, runs.jsonl and results.json. The script prints each
workload's throughput, % of peak at the measured clock, board power, efficiency, and ratios
to the A100 spec sheet (dense peak / TDP). Those are the numbers in the report's tables and
prose, which are written by hand. --embed also replaces the power trace inside the report's
<script type="application/json" id="trace-data"> tag, so the power chart can be refreshed
without touching the rest of the page.
"""
import argparse
import json
import os
import re
import statistics

A100_PEAK = {"fp32": 19.5, "fp16": 312.0, "int8": 624.0}  # TFLOP/s (TOP/s for int8), NVIDIA A100 datasheet, dense
A100_TDP = {"SXM4": 400.0, "PCIe 40GB": 250.0}             # W
PEAK_PER_MINION_CYCLE = {"fp32": 16, "fp16": 32, "int8": 128}  # measured op shapes: 512 / 512 / 256 cycles per op


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir")
    p.add_argument("--embed", metavar="REPORT_HTML", help="replace the trace-data JSON in this report")
    args = p.parse_args()
    d = args.run_dir

    res = json.load(open(os.path.join(d, "results.json")))
    runs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl"))]
    samples = []
    for line in open(os.path.join(d, "power.csv")):
        t, _, w = line.strip().partition(",")
        if t.isdigit():
            samples.append((int(t), float(w)))

    measured_ghz = statistics.mean(r["implied_ghz"] for r in runs)
    # Peak uses the minion clock the card reports (as in the report), falling back to the measured one.
    reported = [re.search(r"Minion Shire: (\d+) Mhz", f) for f in res.get("info", {}).get("freqs", [])]
    reported = [int(m.group(1)) for m in reported if m]
    ghz = reported[0] / 1000 if reported else measured_ghz
    minions = runs[0]["minions"]
    print(f"idle {res['idle_w']:.2f} W (median of {res['idle_samples']} samples); minion clock {ghz:.3f} GHz "
          f"(device cycles vs wall time: {measured_ghz:.4f} GHz); {minions} minions")
    for x in res["results"]:
        mode = x["mode"]
        peak = PEAK_PER_MINION_CYCLE[mode] * minions * ghz * 1e9 / 1e12
        above = x["gflops_per_w_above_idle"]
        line = (f"{x['workload']:18s} {x['tflops']:8.3f} T/s  {100 * x['tflops'] / peak:5.1f}% of {peak:.2f}  "
                f"{x['mean_w']:6.2f} W ({x['min_w']:.1f}-{x['max_w']:.1f}, {x['power_samples']} samples)  "
                f"{x['gflops_per_w']:7.1f}/W  above idle {above if above is None else round(above, 1)}")
        for name, tdp in A100_TDP.items():
            line += f"  vs A100 {name} {x['gflops_per_w'] / (A100_PEAK[mode] * 1000 / tdp):.2f}x"
        print(line + f"  A100 speed {A100_PEAK[mode] / x['tflops']:.2f}x  check {','.join(x['check'])}")

    t0 = samples[0][0]
    windows = []
    for name in dict.fromkeys(r["workload"] for r in runs):
        rs = [r for r in runs if r["workload"] == name]
        windows.append({"workload": name, "start": round((rs[0]["t_start_ms"] - t0) / 1000, 2),
                        "end": round((rs[-1]["t_end_ms"] - t0) / 1000, 2), "launches": len(rs)})
    data = {"trace": [[round((t - t0) / 1000, 2), round(w, 2)] for t, w in samples],
            "windows": windows, "idle_w": round(res["idle_w"], 2)}
    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="trace-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one trace-data script tag")
        html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":")) + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded {len(data['trace'])} power samples and {len(windows)} windows into {args.embed}")


if __name__ == "__main__":
    main()
