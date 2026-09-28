#!/usr/bin/env python3
"""Turn a scripts/mmbench-power.py run directory into the numbers and chart data for a report.

    scripts/mmbench-report-data.py build/mmbench-power
    scripts/mmbench-report-data.py docs/reports/data/2026-09-18-aifoundry2 \
        --manual docs/reports/data/2026-09-23-energy-manual/manual.json \
        --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html \
        --ladder docs/report/index.html

The run directory holds power.csv, runs.jsonl and results.json. The script prints each
workload's throughput, % of peak at the measured clock, board power, efficiency, and ratios
to the A100 spec sheet (dense peak / TDP). Those are the numbers in the report's tables and
prose, which are written by hand. --embed replaces the JSON inside the report's
<script type="application/json" id="trace-data"> tag and nothing else: the power trace, each
workload's windows (launches, the idle window before it, the settle second, its mean power and
throughput) for the idle-window chart, and, with --manual, an "eff" object for the efficiency
explorer: this run's GFLOP/s per W, the energy manual's random-normal variant (2000 / pj_loaded of
tensor.rows fp32_randn, fp16_randn, int8_randn), the operand-and-card band (the same variant on zeros, ones and
random data, aifoundry2's from tensor.rows and every card's from tensor.per_card_rows, all on board power) and the
A100 constants below.

--v3 MMB_JSON (default: the version-3 check's docs/reports/data/2026-09-25-claims-v3/results/mmb.json; "none" leaves
it out) adds a "v3" object for the three-card chart: for each card and workload the pass-mean throughput (MMB-b; the
DRAM workload's is the middle of MMB-a's launch range, which spans 0.6%), board power, the idle just before the
workload and the power above it with its 99% interval over the four passes (MMB-c), the die temperature, and
GFLOP/s per W of board power (MMB-d for the tiles-in-L2 workloads; throughput over board power for DRAM).

--ladder TESTDRIVE_HTML writes the test drive's performance ladder (<script id="ladder-data">):
the FOSDEM 2026 rungs parsed from docs/et-soc1-notes.md, this run's fp32 tensor-unit rate and the
fp32 peak at the reported clock. The test drive's own SGEMM rows are read from its table by the page.

Two per-W-above-idle figures are printed. "above first idle" subtracts results.json's idle_w,
the baseline before the first workload. "idle before" is each workload's own idle, the mean
board power from 3.5 to 1.8 s before its first timed launch (idle_before() in
scripts/mmbench-power.py, which newer runs also store as idle_before_w); "above it"
subtracts that. The die warms over a session and leaks more, so the report's "Per W above
idle" column uses the second: 30.61, 32.53, 33.83 and 35.16 W in the 2026-09-18 run.
"""
import argparse
import json
import os
import re
import statistics

A100_PEAK = {"fp32": 19.5, "fp16": 312.0, "int8": 624.0}  # TFLOP/s (TOP/s for int8), NVIDIA A100 datasheet, dense
A100_TF32 = 156.0                                           # TFLOP/s, tf32 tensor cores, same datasheet
A100_TDP = {"SXM4": 400.0, "PCIe 40GB": 250.0}             # W
# The one measured A100 matmul these reports use: Horace He, "Strangely, Matrix Multiplications on GPUs Run Faster
# When Given 'Predictable' Data!" (thonking.ai): 8192^3 bf16 on random data, 257 TFLOPS under a 330 W power limit.
A100_MEASURED = {"tflops": 257.0, "limit_w": 330.0}
PEAK_PER_MINION_CYCLE = {"fp32": 16, "fp16": 32, "int8": 128}  # measured op shapes: 512 / 512 / 256 cycles per op
FLOP_PER_OP = {"fp32": 2 * 16 * 16 * 16, "fp16": 2 * 16 * 16 * 32, "int8": 2 * 16 * 16 * 64}
IDLE_BEFORE_S = (3.5, 1.8)  # the same window as IDLE_BEFORE_S in scripts/mmbench-power.py
SETTLE_S = 1.0  # mmbench-power.py --settle (its default; the 2026-09-18 run used it): skipped at each workload's start
RANDN = {"fp32": "fp32_randn", "fp16": "fp16_randn", "int8": "int8_randn"}  # manual.json tensor.rows configs
# Short names for the FOSDEM rungs, in the order of docs/et-soc1-notes.md's table (checked against its step text).
LADDER_NAMES = [("1 hart", "1 hart"), ("512 harts", "512 harts"), ("2,048 harts", "2048 harts"),
                ("8-lane SIMD", "SIMD"), ("operands in the L2 scratchpad", "L2 scratchpad"),
                ("2\u00d716 register blocks", "2x16"), ("4\u00d732 register blocks", "4x32"),
                ("tensor unit", "Tensor unit"), ("software-pipelined tensor unit", "Software-pipeline")]


def idle_before_window(t_first_ms, t_prev_end_ms=None):
    """[lo, hi] ms: from 3.5 to 1.8 s before a workload's first timed launch, leaving out samples less than 1 s
    after the previous workload ended. Matches idle_before_window() in scripts/mmbench-power.py."""
    lo = t_first_ms - IDLE_BEFORE_S[0] * 1000
    if t_prev_end_ms is not None:
        lo = max(lo, t_prev_end_ms + 1000)
    return lo, t_first_ms - IDLE_BEFORE_S[1] * 1000


def idle_before(samples, t_first_ms, t_prev_end_ms=None):
    """Mean board power over idle_before_window(). Matches idle_before() in scripts/mmbench-power.py."""
    lo, hi = idle_before_window(t_first_ms, t_prev_end_ms)
    w = [x for t, x in samples if lo <= t <= hi]
    return statistics.mean(w) if w else float("nan")


def sig(v, n=4):
    """Round to n significant digits (keeps the embedded JSON short and stable)."""
    return float(f"{v:.{n}g}")


def eff_object(res, manual_path, run_dir):
    """The efficiency explorer's data: this run, the energy manual's random-normal variant, the A100 constants."""
    run = {}
    for x in res["results"]:
        if x["workload"].endswith("-L2"):
            run[x["mode"]] = {"tflops": sig(x["tflops"], 5), "board_w": sig(x["mean_w"], 6), "per_w": sig(x["gflops_per_w"], 5),
                              "cycles_per_op": sig(FLOP_PER_OP[x["mode"]] / x["flop_per_minion_cycle"])}
    man = json.load(open(manual_path))
    rows = {r["config"]: r for r in man["tensor"]["rows"]}
    randn = {}
    for mode, cfg in RANDN.items():
        r = rows[cfg]
        randn[mode] = {"tflops": sig(2 * r["per_s"] / 1e12, 5), "board_w": sig(r["idle_w"] + r["over_idle_w"]),
                       "per_w": sig(2000 / r["pj_loaded"], 5), "idle_w": sig(r["idle_w"]), "cycles_per_op": round(r["cycles_per_op"])}
    # The operand-and-card band: GFLOP/s per W of total board power (tensor.rows, aifoundry2, the same basis as
    # "randn" above) at each of the three operand patterns, all three precisions; and each card's figure on the same
    # board-power basis, from tensor.per_card_rows (each card's idle and power above idle, four runs per card in the
    # version-3 manual of 26 September) over tensor.rows' throughput, which repeats on every card (the three-card
    # check: cycle counts within 0.05%). Only where the manual has more than one card.
    pcr = man["tensor"].get("per_card_rows", {})
    OPERANDS = (("zeros", "zeros"), ("ones", "ones"), ("random", "randn"))
    operand_band = {}
    for mode in RANDN:
        operand_band[mode] = {}
        for op, suffix in OPERANDS:
            cfg = f"{mode}_{suffix}"
            r = rows[cfg]
            entry = {"per_w": sig(2000 / r["pj_loaded"], 5), "tflops": sig(2 * r["per_s"] / 1e12, 5)}
            byc = {c: {"per_w": sig(2 * r["per_s"] / 1e9 / (v[cfg]["idle_w"] + v[cfg]["over_idle_w"]), 5),
                       "board_w": sig(v[cfg]["idle_w"] + v[cfg]["over_idle_w"]), "idle_w": sig(v[cfg]["idle_w"]),
                       "launch_c": v[cfg].get("launch_c")}
                   for c, v in pcr.items() if cfg in v}
            if len(byc) > 1:
                entry["by_card"] = byc
            operand_band[mode][op] = entry
    a100_per_w = {k: sig(A100_PEAK[k] * 1000 / A100_TDP["SXM4"], 5) for k in A100_PEAK}
    return {"run": {"source": os.path.join(run_dir, "results.json"), "rows": run},
            "randn": {"source": manual_path + " tensor.rows (" + ", ".join(RANDN.values()) + "); power at 80 C",
                      "rows": randn},
            "operands": {"source": manual_path + " tensor.rows (board power, aifoundry2) and tensor.per_card_rows "
                         "(each card's board power over the same throughput)",
                         "rows": operand_band, "a100_per_w": a100_per_w},
            "a100": {"peak": {**A100_PEAK, "tf32": A100_TF32}, "tdp": {"SXM4": A100_TDP["SXM4"], "PCIe": A100_TDP["PCIe 40GB"]},
                     "measured": A100_MEASURED}}


V3_MMB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "data", "2026-09-25-claims-v3",
                      "results", "mmb.json")
WORKLOADS = ("fp32-tensor-L2", "fp16-tensor-L2", "int8-tensor-L2", "fp32-tensor-DRAM")


def v3_object(path):
    """The version-3 check's matmul values per card (items MMB-a to MMB-d of mmb.json), for the three-card chart."""
    m = json.load(open(path))
    it = {x["item"]: x for x in m["items"]}
    c_items, b_items, a_items, d_items = (it[k]["per_card"] for k in ("MMB-c", "MMB-b", "MMB-a", "MMB-d"))
    cards = [c for c in m["cards"]["all"] if c in c_items]
    out = {"source": "docs/reports/data/2026-09-25-claims-v3/results/mmb.json (items MMB-a to MMB-d; four passes per card)",
           "passes": {c: len(m["passes"].get(c, [])) for c in cards}, "cards": {}}
    for c in cards:
        rows = {}
        for w in WORKLOADS:
            cc = c_items[c].get(w)
            if not cc:
                continue
            b = b_items.get(c, {}).get(w)
            if b and b.get("tflops_pass_values"):
                tf, tf_basis = statistics.mean(b["tflops_pass_values"]), "pass mean"
            else:
                tf, tf_basis = statistics.mean(a_items[c][w]["info_tflops_range"]), "middle of the launch range"
            d = d_items.get(c, {}).get(w)
            per_w = ({"mean": sig(d["mean"], 5), "lo": sig(d["ci99"][0], 5), "hi": sig(d["ci99"][1], 5)} if d
                     else {"mean": sig(tf * 1000 / cc["board_w"], 5)})
            rows[w] = {"tflops": sig(tf, 5), "tflops_basis": tf_basis, "board_w": sig(cc["board_w"], 5),
                       "idle_w": sig(cc["idle_before_w"], 5),
                       "above_w": {"mean": sig(cc["mean"], 5), "lo": sig(cc["ci99"][0], 5), "hi": sig(cc["ci99"][1], 5),
                                   "n": cc["n"]},
                       "die_c": sig(cc["die_c_mean"], 3), "die_c_start": cc.get("die_c_start"), "per_w": per_w}
        out["cards"][c] = rows
    return out


def ladder_object(res, ghz, minions):
    """The test drive's ladder: FOSDEM rungs from docs/et-soc1-notes.md, this run's fp32 tensor rate, the fp32 peak."""
    notes = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "et-soc1-notes.md")).read()
    sec = notes.split('## Performance ladder (FOSDEM "Zero to matmul", 512x512 fp32)', 1)[1].split("\n## ", 1)[0]
    unit = {"MFLOP/s": 1e-3, "GFLOP/s": 1.0, "TFLOP/s": 1e3}
    rungs = []
    for line in sec.splitlines():
        m = re.match(r"\|\s*(.+?)\s*\|\s*\**([\d.]+) (MFLOP/s|GFLOP/s|TFLOP/s)\**\s*\|$", line)
        if m:
            rungs.append({"step": re.sub(r"[*`]", "", m.group(1)), "gflops": sig(float(m.group(2)) * unit[m.group(3)])})
    if len(rungs) != len(LADDER_NAMES):
        raise SystemExit(f"docs/et-soc1-notes.md ladder: expected {len(LADDER_NAMES)} rungs, found {len(rungs)}")
    for r, (name, key) in zip(rungs, LADDER_NAMES):
        if key.lower() not in r["step"].lower():
            raise SystemExit(f"docs/et-soc1-notes.md ladder changed: {r['step']!r} does not mention {key!r}")
        r["name"] = name
    clock = re.search(r"FOSDEM talk measured about [\d.]+ TFLOP/s fp32 on \d+ minions at (\d+) MHz", notes)
    tensor = next(x for x in res["results"] if x["workload"] == "fp32-tensor-L2")
    return {"fosdem": {"clock_mhz": int(clock.group(1)), "n": 512, "rungs": rungs,
                       "transcription": "docs/et-soc1-notes.md"},
            "tensor": {"gflops": sig(tensor["tflops"] * 1000, 5), "clock_mhz": round(ghz * 1000),
                       "source": "docs/reports/data/2026-09-18-aifoundry2/results.json (fp32-tensor-L2)"},
            "peak": {"gflops": sig(PEAK_PER_MINION_CYCLE["fp32"] * minions * ghz, 5), "clock_mhz": round(ghz * 1000),
                     "minions": minions, "flop_per_minion_cycle": PEAK_PER_MINION_CYCLE["fp32"]}}


def embed(path, tag, data):
    html = open(path).read()
    pat = re.compile(r'(<script type="application/json" id="' + tag + r'">)(.*?)(</script>)', re.S)
    if len(pat.findall(html)) != 1:
        raise SystemExit(f"{path}: expected exactly one {tag} script tag")
    html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + m.group(3), html)
    open(path, "w").write(html)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("run_dir")
    p.add_argument("--embed", metavar="REPORT_HTML", help="replace the trace-data JSON in this report")
    p.add_argument("--manual", metavar="MANUAL_JSON", help="energy manual data: adds the efficiency explorer's 'eff' object")
    p.add_argument("--ladder", metavar="TESTDRIVE_HTML", help="replace the ladder-data JSON in the test drive")
    p.add_argument("--v3", metavar="MMB_JSON", default=V3_MMB,
                   help="the version-3 check's mmb.json (default: the committed one); 'none' leaves the three-card data out")
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
    prev_end = None
    for x in res["results"]:
        mode = x["mode"]
        peak = PEAK_PER_MINION_CYCLE[mode] * minions * ghz * 1e9 / 1e12
        above = x["gflops_per_w_above_idle"]
        rs = [r for r in runs if r["workload"] == x["workload"]]
        idle_b = x.get("idle_before_w", idle_before(samples, rs[0]["t_start_ms"], prev_end))
        prev_end = rs[-1]["t_end_ms"]
        above_b = x["tflops"] * 1000 / (x["mean_w"] - idle_b) if x["mean_w"] > idle_b else None
        line = (f"{x['workload']:18s} {x['tflops']:8.3f} T/s  {100 * x['tflops'] / peak:5.1f}% of {peak:.2f}  "
                f"{x['mean_w']:6.2f} W ({x['min_w']:.1f}-{x['max_w']:.1f}, {x['power_samples']} samples)  "
                f"{x['gflops_per_w']:7.1f}/W  above first idle {above if above is None else round(above, 1)}  "
                f"idle before {idle_b:.2f} W, above it {above_b if above_b is None else round(above_b, 1)}/W")
        for name, tdp in A100_TDP.items():
            line += f"  vs A100 {name} {x['gflops_per_w'] / (A100_PEAK[mode] * 1000 / tdp):.2f}x"
        print(line + f"  A100 speed {A100_PEAK[mode] / x['tflops']:.2f}x  check {','.join(x['check'])}")

    t0 = samples[0][0]
    sec = lambda t: round((t - t0) / 1000, 2)
    windows, prev_end = [], None
    by_name = {x["workload"]: x for x in res["results"]}
    for name in dict.fromkeys(r["workload"] for r in runs):
        rs = [r for r in runs if r["workload"] == name]
        x = by_name[name]
        lo, hi = idle_before_window(rs[0]["t_start_ms"], prev_end)
        idle_b = x.get("idle_before_w", idle_before(samples, rs[0]["t_start_ms"], prev_end))
        prev_end = rs[-1]["t_end_ms"]
        windows.append({"workload": name, "mode": x["mode"], "start": sec(rs[0]["t_start_ms"]), "end": sec(rs[-1]["t_end_ms"]),
                        "launches": len(rs), "idle_before_w": round(idle_b, 2), "idle_t0": sec(lo), "idle_t1": sec(hi),
                        "settle_end": sec(rs[0]["t_start_ms"] + SETTLE_S * 1000), "mean_w": round(x["mean_w"], 4),
                        "tflops": round(x["tflops"], 3), "power_samples": x["power_samples"]})
    data = {"trace": [[sec(t), round(w, 2)] for t, w in samples], "windows": windows, "idle_w": round(res["idle_w"], 2)}
    if args.manual:
        data["eff"] = eff_object(res, args.manual, d)
    if args.v3 and args.v3 != "none" and os.path.exists(args.v3):
        data["v3"] = v3_object(args.v3)
    if args.embed:
        embed(args.embed, "trace-data", data)
        print(f"embedded {len(data['trace'])} power samples and {len(windows)} windows"
              f"{' and the efficiency data' if args.manual else ''}{' and the three-card data' if 'v3' in data else ''} into {args.embed}")
    if args.ladder:
        embed(args.ladder, "ladder-data", ladder_object(res, ghz, minions))
        print(f"embedded the performance ladder into {args.ladder}")


if __name__ == "__main__":
    main()
