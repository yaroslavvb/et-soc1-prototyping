#!/usr/bin/env python3
"""Summarize the sparsity runs into the numbers and chart data used by the report.

    python3 workloads/sparsity/analyze.py docs/reports/data/2026-09-18-sparsity-aifoundry3 \
        --later docs/reports/data/2026-09-22-horace-aifoundry3/horace3.json [--embed REPORT_HTML]

The data directory holds the SPARSITY lines of each run (*.jsonl from run_lab.sh; diverge/ for the divergence
sweep), clock.csv (minion clock and board power during those runs) and energy-*/ (run_energy.py). With --embed
the script replaces the JSON inside the report's <script type="application/json" id="sparsity-data"> tag.

--later HORACE3_JSON adds energy.later: the same TensorFMA loop on the same card, four days later and
temperature-controlled (the Horace experiment's aifoundry3 run): power above the idle just before each pattern
(p80 - p_before; the Horace analysis's p80 is the power at the run's launch temperature, about 55 C on this card,
not 80 C), the launch temperature and the throughput, for zeros, ones and random-normal operands.
"""
import argparse
import glob
import json
import math
import os
import re
import statistics


def load(path):
    out = []
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("SPARSITY "):
                out.append(json.loads(line.split(" ", 1)[1]))
    return out


def clock_mhz(d):
    vals = []
    for f in [os.path.join(d, "clock.csv"), os.path.join(d, "diverge", "clock.csv")]:
        if os.path.exists(f):
            for line in open(f):
                p = line.strip().split(",")
                if len(p) >= 2 and p[0].isdigit() and p[1]:
                    vals.append(float(p[1]))
    return statistics.median(vals) if vals else 600.0, sorted(set(vals))


def pareto_eff(alpha, n):
    """Lane efficiency E[k] / E[max of n] for continuous Pareto(alpha, xmin = 1) (research note, verified by MC)."""
    if alpha <= 1:
        return 0.0
    return (alpha / (alpha - 1)) / (math.gamma(n + 1) * math.gamma(1 - 1 / alpha) / math.gamma(n + 1 - 1 / alpha))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("data_dir")
    p.add_argument("--embed", metavar="REPORT_HTML")
    p.add_argument("--later", metavar="HORACE3_JSON", help="later runs of the same loop on this card (energy.later)")
    args = p.parse_args()
    d = args.data_dir
    mhz, mhz_values = clock_mhz(d)
    ns_per_cycle = 1000.0 / mhz
    data = {"clock_mhz": mhz, "clock_values": mhz_values}
    bad = []
    for f in glob.glob(os.path.join(d, "*.jsonl")) + glob.glob(os.path.join(d, "diverge", "*.jsonl")):
        bad += [os.path.basename(f) for r in load(f) if r.get("ok") is False]
    if bad:
        print("WARNING: failed lines in", sorted(set(bad)))
    print(f"minion clock: median {mhz:.0f} MHz, values seen {mhz_values}")

    # ---- TensorFMA: cycles per op against the fraction of zeros
    fma = {}
    for name in ["fp32-elem", "fp32-col", "fp32-row", "fp32-elem-tenb", "fp16-elem", "fp16-pair", "int8-elem",
                 "fp32-elem-all"]:
        rows = load(os.path.join(d, f"fma-{name}.jsonl"))
        fma[name] = [[r["sparsity"], round(r["cycles_per_op"], 2), r["result"], r["nnz_a"], r["a_elems"]] for r in rows]
    fma["b-sparse"] = [[r["b_sparsity"], round(r["cycles_per_op"], 2), r["result"]]
                       for n in ["fp32-bsparse", "fp32-bsparse90"] for r in load(os.path.join(d, f"fma-{n}.jsonl"))]
    fma["rowmask"] = []
    for m in ["0xFFFF", "0x00FF", "0x000F", "0x0001", "0x0000"]:
        for r in load(os.path.join(d, f"fma-fp32-rowmask-{m}.jsonl")):
            fma["rowmask"].append([bin(int(m, 16)).count("1"), round(r["cycles_per_op"], 2), r["result"]])
    data["fma"] = fma
    print("\nTensorFMA cycles per op (A tile 16x16, B 16x16):")
    for name, rows in fma.items():
        if rows:
            cyc = [r[1] for r in rows]
            print(f"  {name:15s} {min(cyc):7.1f}-{max(cyc):7.1f}  over {len(rows)} points  results {sorted(set(r[2] for r in rows))}")

    # ---- TensorLoad under a mask
    tload = {}
    for w in ["dram", "l2", "scp"]:
        for scope in ["one", "all"]:
            rows = load(os.path.join(d, f"tload-{w}-{scope}.jsonl"))
            # Bytes the mask let through over the slowest minion's loop time at the logged clock. (The host's
            # gbps_wall divides by the launch's wall time, which adds 0.2-0.4 ms to runs of about 1 ms.)
            tload[f"{w}-{scope}"] = [[int(r["lines"]), round(r["cycles_per_load"], 1),
                                      round(r["bytes_requested"] / (r["cycles_max"] * ns_per_cycle), 2)]
                                     for r in rows]
    data["tload"] = tload
    print("\nTensorLoad (16 lines max) cycles per load and GB/s on chip by lines requested:")
    for k, rows in tload.items():
        print(f"  {k:9s} " + "  ".join(f"{l}:{c:.1f}c/{g:.1f}GB/s" for l, c, g in rows))

    # ---- The batch-1 layer (time of each 16-row block's slowest minion, mean over the 64 blocks)
    gemv = {}
    for name in ["dense", "masked", "skip", "skip-oneshire", "tree-dense", "tree-masked", "tree-skip",
                 "tree-oneshire"]:
        rows = load(os.path.join(d, f"gemv-{name}.jsonl"))
        gemv[name] = [[r["sparsity"], round(r["cycles_per_layer_mean"], 1), round(r["cycles_per_layer_mean"] * ns_per_cycle / 1000, 3),
                       round(r["slices_per_minion"], 2), round(r["lines_per_minion"], 1), r["ok"]] for r in rows]
    data["gemv"] = gemv
    print(f"\nlayer y = W x, 1024 x 4096 fp32 (cycles, us at {mhz:.0f} MHz):")
    for k, rows in gemv.items():
        if rows:
            print(f"  {k:14s} " + "  ".join(f"{s:.2f}:{c:.0f}c/{u:.2f}us" for s, c, u, *_ in rows))

    # ---- Divergence
    div = {"alpha": [], "static": [], "refill": [], "scalar": [], "simt8": [], "simt32": [], "model8": [], "model32": []}
    for a in ["0", "3", "2", "1.5", "1.2"]:
        rs = {v: load(os.path.join(d, "diverge", f"diverge-{v}-a{a}.jsonl")) for v in ["static", "refill", "scalar"]}
        if not all(rs.values()):
            continue
        alpha = float(a)
        div["alpha"].append(alpha)
        for v, rows in rs.items():
            r = rows[0]
            fma_mean = 8 * r["useful_lane_iters"] / r["minions"] / r["cycles_mean"]
            fma_max = 8 * r["useful_lane_iters"] / r["minions"] / r["cycles_max"]
            div[v].append({"lane_eff": round(r["lane_efficiency"], 4), "fma_per_cycle_mean": round(fma_mean, 3),
                           "fma_per_cycle_makespan": round(fma_max, 3), "mean_k": r["mean_k"], "max_k": r["max_k"],
                           "tfma_chip_mean": round(fma_mean * r["minions"] * mhz / 1e6, 3),
                           "cycles_mean": r["cycles_mean"], "cycles_max": r["cycles_max"], "items": r["items"],
                           "harts": r["harts"], "chunk": r["chunk"]})
        div["simt8"].append(rs["static"][0]["simt8_efficiency"])
        div["simt32"].append(rs["static"][0]["simt32_efficiency"])
        div["model8"].append(round(pareto_eff(alpha, 8), 4) if alpha > 0 else 1.0)
        div["model32"].append(round(pareto_eff(alpha, 32), 4) if alpha > 0 else 1.0)
    data["diverge"] = div
    if div["alpha"]:
        print("\ndivergence (mean k 64, capped at 16384; lane efficiency, FMA/cycle/minion in steady state):")
        for i, a in enumerate(div["alpha"]):
            print(f"  alpha {a:>4}: static {div['static'][i]['lane_eff']:.3f} ({div['static'][i]['fma_per_cycle_mean']:.2f})"
                  f"  refill {div['refill'][i]['lane_eff']:.3f} ({div['refill'][i]['fma_per_cycle_mean']:.2f})"
                  f"  scalar ({div['scalar'][i]['fma_per_cycle_mean']:.2f})  simt8 {div['simt8'][i]:.3f}"
                  f"  simt32 {div['simt32'][i]:.3f}  [continuous model 8/32: {div['model8'][i]:.3f}/{div['model32'][i]:.3f}]")

    # ---- Energy
    energy = []
    for ef in sorted(glob.glob(os.path.join(d, "energy-*", "results.json"))):
        energy.append({"run": os.path.basename(os.path.dirname(ef)), **json.load(open(ef))})
    summary = {}
    for e in energy:
        for name, r in e["results"].items():
            summary.setdefault(name, []).append(r)
    en = {"runs": [e["run"] for e in energy], "idle_w": [e["idle_w"] for e in energy], "configs": {}}
    # The TensorFMA configurations' A tile as drawn (nonzero elements, size) and tensor_mask, from the host's records.
    tile = {}
    for rf in sorted(glob.glob(os.path.join(d, "energy-*", "runs.jsonl"))):
        for line in open(rf):
            r = json.loads(line)
            if r.get("nnz_a") is not None:
                t = (r["nnz_a"], r["a_elems"], r.get("row_mask", "0xffff"))
                if tile.setdefault(r["config"], t) != t:
                    raise SystemExit(f"{rf}: {r['config']} has A tiles of different sparsity: {tile[r['config']]} and {t}")
    for name, rs in summary.items():
        def col(key):
            vals = [r[key] for r in rs if r.get(key) is not None]
            return {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)} if vals else None
        en["configs"][name] = {"what": rs[0]["what"], "unit": rs[0]["unit"], "mean_w": col("mean_w"),
                               "above_idle_w": col("above_idle_w"), "above_spin_w": col("above_spin_w"),
                               "per_s": col("per_s"), "mean_mhz": col("mean_mhz"),
                               "j_per_unit_above_idle": col("j_per_unit_above_idle"), "j_per_unit": col("j_per_unit"),
                               "pj_slot": col("pj_per_fma_slot_above_idle"),
                               "pj_useful": col("pj_per_useful_fma_above_idle"),
                               "cycles_per_op": col("cycles_per_op"), "cycles_per_layer": col("cycles_per_layer")}
        if name in tile:
            c = en["configs"][name]
            c["nnz_a"], c["a_elems"], c["row_mask"] = tile[name]
            c["rows_on"] = bin(int(c["row_mask"], 16)).count("1")  # of 16 rows of C
    if args.later:
        h = json.load(open(args.later))
        en["later"] = {"source": args.later, "patterns": {}}
        for k in ["zeros", "ones", "randn"]:
            q = h["patterns"][k]
            w = q["p80"] - q["p_before"]
            en["later"]["patterns"][k] = {"above_idle_w": round(w, 3), "tflops": round(q["tflops"], 4),
                                          "pj_mac": round(w / (q["tflops"] * 1e12 / 2) * 1e12, 3),
                                          "launch_c": round(q["start_temp"], 1)}
    data["energy"] = en
    if energy:
        print(f"\nenergy: runs {en['runs']}, idle {[round(w, 2) for w in en['idle_w']]} W")
        for name, c in en["configs"].items():
            extra = ""
            if c["pj_slot"]:
                extra = f"  {c['pj_slot']['mean']:.3f} pJ/FMA slot"
                if c["pj_useful"]:
                    extra += f", {c['pj_useful']['mean']:.3f} pJ/useful FMA"
            elif c["j_per_unit_above_idle"]:
                extra = f"  {c['j_per_unit_above_idle']['mean'] * 1e6:.3f} uJ/{c['unit']} above idle"
            print(f"  {name:14s} {c['mean_w']['mean']:6.2f} W (+{c['above_idle_w']['mean']:5.2f}, "
                  f"{c['above_idle_w']['min']:.2f}-{c['above_idle_w']['max']:.2f}){extra}")
    if "later" in en:
        L = en["later"]["patterns"]
        print("later runs of the loop on this card (" + en["later"]["source"] + "): "
              + ", ".join(f"{k} +{v['above_idle_w']:.2f} W ({v['pj_mac']:.2f} pJ per multiply-add)" for k, v in L.items())
              + "; zero-skip saves " + ", ".join(f"{1 - L['zeros']['above_idle_w'] / L[k]['above_idle_w']:.0%} against {k}"
                                                  for k in ["ones", "randn"]))

    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="sparsity-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one sparsity-data script tag")
        html = pat.sub(lambda m: m.group(1) + json.dumps(data, separators=(",", ":")) + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded report data into {args.embed}")


if __name__ == "__main__":
    main()
