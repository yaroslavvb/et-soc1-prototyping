#!/usr/bin/env python3
"""Roofline ridge points for the ET-SoC-1: how many FLOPs (or int8 OPs) a kernel must do per byte it fetches
from each level of the memory hierarchy before the level stops being the bottleneck.

    python3 scripts/ridge-points.py [--embed docs/reports/2026-09-18-et-soc1-ridge-points.html]

ridge = peak compute / bandwidth of the level. No new measurements: compute peaks come from the Minion VPU
Specification and the PRM, measured bandwidths from the raw data of the earlier reports (docs/reports/data/),
checked against the 23 September reruns of the same probe on both cards, spec bandwidths from the manuals and
micro-architecture docs, and energy per FLOP and per byte from the energy manual's data
(docs/reports/data/2026-09-23-energy-manual/manual.json: sections 3.2, 4 and 5). Every constant below names its
source. With --embed the script replaces the JSON inside the report's
<script type="application/json" id="ridge-data"> tag.
"""
import argparse
import json
import math
import os
import re
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "docs", "reports", "data")
REPORTS = os.path.join(ROOT, "docs", "reports")
MANUAL = os.path.join(DATA, "2026-09-23-energy-manual", "manual.json")  # the energy manual's data (23 Sep)
RERUN_DIRS = ("2026-09-23-reruns-aifoundry2-warm", "2026-09-23-reruns-aifoundry3")  # levels-pass*/runs.jsonl
MINIONS = 1024  # compute minions that run user kernels (32 shires x 32); the die has 1,088
CLOCK_MHZ = 600  # minion clock on both lab cards during every measured run (telemetry)
DESIGN_MHZ = 1000  # design clock of the minion shires (CORE-ET Minion Shire Description, Table 2)
NOC_MHZ = 400  # NoC clock the firmware programs (SP BL2 PLL mode 37); reported by the card

# ---- compute ceilings, per minion per minion-clock cycle -------------------------------------------------------
# Minion VPU Specification sec. 2: 8 lanes, one TXFMA per lane (one fp32 or two fp16 FMAs per cycle) and two TIMA
# units per lane (4 int8 MACs each). A multiply-add counts as 2 operations.
PEAK = {
    "fp32": {"name": "fp32 tensor (TensorFMA32)", "unit": "FLOP", "per_cycle": 16, "bytes": 4},
    "fp16": {"name": "fp16 in, fp32 accumulate (TensorFMA16A32)", "unit": "FLOP", "per_cycle": 32, "bytes": 2},
    "int8": {"name": "int8 in, int32 accumulate (TensorIMA8A32)", "unit": "OP", "per_cycle": 128, "bytes": 1},
    # The vector unit's fmadd.ps runs on the same TXFMA units as TensorFMA32, so its peak is not additive. It is
    # also single-issue with the loads that feed it (Minion Description sec. 2), so 16 is never reached in practice.
    "vec32": {"name": "fp32 vector (fmadd.ps)", "unit": "FLOP", "per_cycle": 16, "bytes": 4},
}
FLOP_PER_OP = {"fp32": 2 * 16 * 16 * 16, "fp16": 2 * 16 * 16 * 32, "int8": 2 * 16 * 16 * 64}
OP_BYTES = 2048  # one full op loads a 1 KiB A tile (16 lines) and a 1 KiB B tile (PRM ch. 9: tensors are <= 1 KiB)

# ---- spec bandwidths ----------------------------------------------------------------------------------------------
SPEC = {
    "vrf": (96, "B/cycle/minion", "Minion VPU Specification sec. 2.2.2: 3 read ports x 32 B per lane group"),
    "l1d": (32, "B/cycle/minion", "Minion DCache Description sec. 3.2: 4 LRAM blocks x 64 bits, one 256-bit row per access"),
    "shire": (256 / 32, "B/cycle/minion",
              "CORE-ET Shire Cache Specification sec. 1: 4 banks x one 64 B line per cycle = 256 B/cycle per shire; "
              "CORE-ET Neighborhood MAS sec. 4.4: one 64 B response per cycle per neighbourhood of 8 minions"),
    # Four 512-bit AXI ports per shire to the L3 mesh (Shire Cache Spec sec. 2.3, 2.4). One 64 B beat per NoC cycle
    # per port is an assumption: no document gives the mesh link throughput.
    "mesh": (4 * 64 * NOC_MHZ * 1e6 * 32 / 1e9, "GB/s chip",
             "Shire Cache Spec sec. 2.3-2.4: 4 x 512-bit ports per shire to the L3 mesh, at the 400 MHz NoC clock, "
             "assuming one 64 B beat per NoC cycle per port"),
    # 16 x 16-bit LPDDR4X channels. The datasheet maximum is 4266 MT/s; the firmware selects a 933 MHz DDR clock
    # (choices 800 / 933 / 1066), which at the 1066 : 4266 ratio is 3733 MT/s.
    "dram_max": (16 * 2 * 4.266, "GB/s", "ET Preliminary Datasheet sec. 7.1: 16 x 16-bit LPDDR4X at up to 4266 MT/s "
                 "(HC33: 137 GB/s)"),
    "dram_cfg": (16 * 2 * 3.733, "GB/s", "DDR clock 933 MHz (card telemetry; SP BL2 mem_controller.c), read as "
                 "3733 MT/s (assumes the 1066 MHz : 4266 MT/s ratio)"),
    "pcie": (15.75, "GB/s per direction", "ET Preliminary Datasheet sec. 1: PCIe Gen4 x8 = 16 GT/s x 8 lanes, "
             "128b/130b encoding, before protocol overhead"),
    "fln": (16, "B/cycle/sender", "CORE-ET Neighborhood MAS sec. 4.7: 256-bit messages, at most one every other "
            "cycle per sender"),
    "xbar_msg": (32 / 8, "B/cycle/minion", "CORE-ET Neighborhood MAS sec. 4.3: 256-bit request path, 32 B/cycle "
                 "per neighbourhood of 8 minions"),
}

# ---- A100 (published; docs/reports/sources/2026-09-18-a100-memory-hierarchy.md and the matmul report) ---------
A100 = {
    "peaks_tflops": {"fp32": 19.5, "fp16": 312, "int8": 624},  # CUDA-core fp32; dense tensor fp16 / int8
    "levels": [  # (name, sustained TB/s, peak TB/s)
        ("Shared memory / L1", 14.8, 19.5),
        ("L2", 4.4, 7.2),
        ("HBM2 (40 GB)", 1.40, 1.555),
    ],
}


def jsonl(path, prefix=None):
    out = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        if prefix:
            if not line.startswith(prefix):
                continue
            line = line.split(" ", 1)[1]
        out.append(json.loads(line))
    return out


def embedded(report, tag):
    html = open(os.path.join(REPORTS, report)).read()
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % tag, html, re.S)
    return json.loads(m.group(1))


def memhier_levels():
    """Per-cycle bandwidth of each streaming probe of the memory-hierarchy report (aifoundry2), from the launches
    that ran at 600 MHz. B/cycle uses the slowest minion's cycle count (cycles_max), as a kernel would see."""
    runs = []
    for d in ("energy", "energy2"):
        runs += [r for r in jsonl(os.path.join(DATA, "2026-09-18-memhier-aifoundry2", d, "runs.jsonl"))
                 if r.get("launch", -1) >= 0 and r["bytes"] > 0]
    out = {}
    for cfg in sorted({r["config"] for r in runs}):
        rs = [r for r in runs if r["config"] == cfg]
        at600 = [r for r in rs if 0.59 <= r["implied_ghz"] <= 0.61]
        # L1, L2 and the local scratchpad run on the minion clock, so every launch gives the same bytes per cycle;
        # the levels past the shire run on the NoC and DRAM clocks, so only the 600 MHz launches count.
        bpc = [r["bytes"] / r["minions"] / r["cycles_max"] for r in (rs if cfg in ("l1", "l2", "scp-local") else at600)]
        # Elasticity of GB/s with the minion clock over all launches (0.6 GHz up to 0.74-0.80 GHz, depending on the
        # level): ~1 in the minion's clock domain, ~0 in a fixed one (NoC, DRAM).
        xs = [math.log(r["implied_ghz"]) for r in rs]
        ys = [math.log(r["bytes"] / r["wall_s"]) for r in rs]
        mx, my = statistics.mean(xs), statistics.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else float("nan")
        out[cfg] = {"launches_600": len(at600), "launches": len(rs),
                    "bpc_minion": statistics.median(bpc) if bpc else None,
                    "gbps_600": statistics.median([r["bytes"] / r["wall_s"] / 1e9 for r in at600]) if at600 else None,
                    "harts": rs[0]["harts"], "clock_elasticity": slope}
    return out


def rerun_levels():
    """The same streaming probes re-run on 23 September at a pinned 600 MHz, 3 passes on aifoundry2 and 2 on
    aifoundry3 (the energy manual's section 4.2 runs). Per level: the range over passes of the median GB/s of the
    600 MHz launches, the median bytes per minion-cycle, and the passes per card."""
    out = {}
    for d in RERUN_DIRS:
        card = "aifoundry3" if d.endswith("aifoundry3") else "aifoundry2"
        for p in sorted(os.listdir(os.path.join(DATA, d))):
            path = os.path.join(DATA, d, p, "runs.jsonl")
            if not (p.startswith("levels-pass") and os.path.exists(path)):
                continue
            runs = [r for r in jsonl(path) if r.get("launch", -1) >= 0 and r["bytes"] > 0
                    and 0.59 <= r["implied_ghz"] <= 0.61]
            for cfg in sorted({r["config"] for r in runs}):
                rs = [r for r in runs if r["config"] == cfg]
                o = out.setdefault(cfg, {"gbps": [], "bpc": [], "passes": {}})
                o["gbps"].append(statistics.median([r["bytes"] / r["wall_s"] / 1e9 for r in rs]))
                o["bpc"] += [r["bytes"] / r["minions"] / r["cycles_max"] for r in rs]
                o["passes"][card] = o["passes"].get(card, 0) + 1
    return {cfg: {"gbps": [min(o["gbps"]), max(o["gbps"])], "bpc_minion": statistics.median(o["bpc"]),
                  "passes": o["passes"]} for cfg, o in out.items()}


def sparsity_tload(where):
    """16-line TensorLoads from all 1,024 minions on aifoundry3 (a steady 600 MHz)."""
    rows = jsonl(os.path.join(DATA, "2026-09-18-sparsity-aifoundry3", f"tload-{where}-all.jsonl"), "SPARSITY ")
    r = [r for r in rows if r["lines"] == 16][0]
    return r["lines"] * 64 * r["iters"] / r["cycles_max"]


def all_minion_tload(where):
    """Cycles per load and bytes per minion-cycle (slowest minion) by lines requested, all 1,024 minions."""
    rows = jsonl(os.path.join(DATA, "2026-09-18-sparsity-aifoundry3", f"tload-{where}-all.jsonl"), "SPARSITY ")
    return {int(r["lines"]): (r["cycles_per_load"], r["lines"] * 64 * r["iters"] / r["cycles_max"]) for r in rows}


def one_minion_tload(where):
    rows = jsonl(os.path.join(DATA, "2026-09-18-sparsity-aifoundry3", f"tload-{where}-one.jsonl"), "SPARSITY ")
    return {int(r["lines"]): r["cycles_per_load"] for r in rows}


def mmbench():
    res = json.load(open(os.path.join(DATA, "2026-09-18-aifoundry2", "results.json")))
    return {r["workload"]: r for r in res["results"]}, res["idle_w"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--embed", metavar="REPORT_HTML")
    args = p.parse_args()
    ghz = CLOCK_MHZ / 1000
    chip = lambda per_cycle: per_cycle * MINIONS * ghz  # per minion-cycle -> G/s for the chip at 600 MHz

    mh = memhier_levels()
    mm, mm_idle = mmbench()
    demo = {k: mm[f"{k}-tensor-L2"]["flop_per_minion_cycle"] for k in ("fp32", "fp16", "int8")}
    peaks = {}
    for k, v in PEAK.items():
        peaks[k] = dict(v, chip_600=chip(v["per_cycle"]) / 1000, chip_design=v["per_cycle"] * MINIONS * DESIGN_MHZ / 1e6,
                        demo_per_cycle=demo.get(k))
    peaks["vec32"]["demo_per_cycle"] = 2.94e12 / (MINIONS * 0.65e9)  # FOSDEM 2026 best vector matmul, 650 MHz
    op_cycles = {k: FLOP_PER_OP[k] / demo[k] for k in demo}

    # ---- bandwidth of each level, per minion per minion-cycle at 600 MHz -----------------------------------------
    gb = lambda bpc: chip(bpc)  # GB/s at 600 MHz
    to_bpc = lambda gbps: gbps / (MINIONS * ghz)
    L = []

    def level(key, name, group, size, clock, meas, spec, note):
        L.append({"key": key, "name": name, "group": group, "size": size, "clock": clock, "measured": meas,
                  "spec": spec, "note": note})

    level("vrf", "Vector registers", "minion", "1 KB per hart (32 x 32 B)", "minion", None,
          {"bpc": SPEC["vrf"][0], "src": SPEC["vrf"][2]},
          "Provisioned for one three-operand fmadd.ps per cycle. Tensor ops read only their C accumulators here.")
    level("l1d", "L1 data cache (flw.ps)", "minion", "512 B per hart", "minion",
          {"bpc": mh["l1"]["bpc_minion"], "gbps": gb(mh["l1"]["bpc_minion"]),
           "src": "memory-hierarchy probe: 32 B vector loads by both harts, about 0.3 loads per minion-cycle", "gbps_600": mh["l1"]["gbps_600"]},
          {"bpc": SPEC["l1d"][0], "src": SPEC["l1d"][2]},
          "Feeds the vector unit only. Loads and FMAs share one issue slot, so there is no sharp ridge.")
    level("l2", "L2 cache, own shire", "shire", "512 KB per shire; 16 MB chip", "minion",
          {"bpc": mh["l2"]["bpc_minion"], "gbps": mh["l2"]["gbps_600"],
           "src": "memory-hierarchy probe: 1 KB TensorLoads, 2 in flight, private 8 KB per minion"},
          {"bpc": SPEC["shire"][0], "src": SPEC["shire"][2]},
          "")
    op_bpc = {k: OP_BYTES / op_cycles[k] for k in op_cycles}
    L[-1]["demonstrated"] = {"bpc": op_bpc["int8"], "gbps": gb(op_bpc["int8"]),
                             "src": "int8 matmul loop: A and B tiles (2 KB) per 280-cycle op, tiles shared by all minions"}
    level("scp", "L2 scratchpad, own shire", "shire", "2.5 MB per shire; 80 MB chip", "minion",
          {"bpc": mh["scp-local"]["bpc_minion"], "gbps": mh["scp-local"]["gbps_600"],
           "bpc_card2": sparsity_tload("scp"),
           "src": "memory-hierarchy probe and sparsity probe (second card): 1 KB TensorLoads, 2 in flight"},
          {"bpc": SPEC["shire"][0], "src": SPEC["shire"][2]}, "")
    mesh_bpc = to_bpc(SPEC["mesh"][0])
    for cfg in ("l3", "scp-remote", "dram"):  # past the shire: bytes per minion-cycle from GB/s at 600 MHz
        mh[cfg]["bpc_minion"] = to_bpc(mh[cfg]["gbps_600"])
    level("l3", "L3", "mesh", "1 MB per shire, 32 MB chip; lines spread over all shires", "noc",
          {"bpc": mh["l3"]["bpc_minion"], "gbps": mh["l3"]["gbps_600"],
           "src": "memory-hierarchy probe: 1 KB TensorLoads, 24 MB working set"},
          {"bpc": mesh_bpc, "gbps": SPEC["mesh"][0], "src": SPEC["mesh"][2], "assumed": True}, "")
    level("scp_remote", "L2 scratchpad, other shire", "mesh", "2.5 MB in each of 31 other shires", "noc",
          {"bpc": mh["scp-remote"]["bpc_minion"], "gbps": mh["scp-remote"]["gbps_600"],
           "src": "memory-hierarchy probe: every minion reads the scratchpad 16 shire IDs away (2.1 hops mean)"},
          {"bpc": mesh_bpc, "gbps": SPEC["mesh"][0], "src": SPEC["mesh"][2], "assumed": True}, "")
    level("dram", "DRAM (LPDDR4X)", "chip", "32 GB", "dram",
          {"bpc": mh["dram"]["bpc_minion"], "gbps": mh["dram"]["gbps_600"],
           "gbps_card2": sparsity_tload("dram") * MINIONS * ghz,
           "src": "memory-hierarchy probe: 1 KB TensorLoads, 256 MB working set; the 23 Sep reruns give 76 GB/s on "
                  "both cards (gbps_card2 is the sparsity report's shorter probe on aifoundry3)"},
          {"bpc": to_bpc(SPEC["dram_cfg"][0]), "gbps": SPEC["dram_cfg"][0], "src": SPEC["dram_cfg"][2],
           "max_gbps": SPEC["dram_max"][0], "max_src": SPEC["dram_max"][2]}, "")
    level("pcie", "Host memory over PCIe", "chip", "host RAM", "pcie", None,
          {"bpc": to_bpc(SPEC["pcie"][0]), "gbps": SPEC["pcie"][0], "src": SPEC["pcie"][2]},
          "Not measured; only the per-launch overhead is known (see limits).")
    noc = embedded("2026-09-18-et-soc1-on-chip-communication.html", "nocbench-data")["energy"]["configs"]
    xs = [noc[k]["gb_per_s"] for k in noc if k.startswith("xshire") and not k.endswith("-c4")]
    level("fln", "TensorSend, fast local network", "network", "neighbourhood tree edges", "minion",
          {"bpc": to_bpc(noc["pair"]["gb_per_s"]), "gbps": noc["pair"]["gb_per_s"],
           "src": "on-chip communication report: all 512 pairs exchanging 1 KB messages"},
          {"bpc": SPEC["fln"][0], "src": SPEC["fln"][2]}, "")
    level("xbar", "TensorSend inside a shire", "network", "rings of 8 or 32 minions", "minion",
          {"bpc": to_bpc(noc["shire"]["gb_per_s"]), "gbps": noc["shire"]["gb_per_s"],
           "src": "on-chip communication report: rings of 32, 1 KB messages"},
          {"bpc": SPEC["xbar_msg"][0], "src": SPEC["xbar_msg"][2]}, "")
    level("xmesh", "TensorSend between shires", "network", "1–10 mesh hops (1.6–4.7 mean per pattern)", "noc",
          {"bpc": to_bpc(max(xs)), "bpc_low": to_bpc(min(xs)), "gbps": max(xs), "gbps_low": min(xs),
           "src": "on-chip communication report: every minion sends to a shire 1-16 IDs away, 1 KB messages"},
          None, "Limited per message (packets in flight), not by the mesh links.")

    # ---- the 23 September reruns of the memory probes (pinned 600 MHz, both cards) against the values above -----
    rr = rerun_levels()
    rerun_dev = 0.0
    for lv in L:
        cfg = {"l1d": "l1", "l2": "l2", "scp": "scp-local", "l3": "l3", "scp_remote": "scp-remote", "dram": "dram"}.get(lv["key"])
        if cfg and cfg in rr and lv.get("measured"):
            lv["measured"]["rerun"] = rr[cfg]
            g = lv["measured"]["gbps"]
            rerun_dev = max(rerun_dev, max(abs(x / g - 1) for x in rr[cfg]["gbps"]))

    # ---- ridge points -------------------------------------------------------------------------------------------
    for lv in L:
        lv["ridge"] = {}
        for basis in ("measured", "demonstrated", "spec"):
            b = lv.get(basis)
            if not b:
                continue
            r = {k: PEAK[k]["per_cycle"] / b["bpc"] for k in PEAK}
            if "bpc_low" in b:
                r = {k: [PEAK[k]["per_cycle"] / b["bpc"], PEAK[k]["per_cycle"] / b["bpc_low"]] for k in PEAK}
            lv["ridge"][basis] = r
        if lv["key"] == "dram":
            lv["ridge"]["spec_max"] = {k: PEAK[k]["per_cycle"] / to_bpc(SPEC["dram_max"][0]) for k in PEAK}
        # Ridges against levels outside the minion clock domain grow with the minion clock. For DRAM and PCIe the
        # bandwidth is fixed in GB/s; the measured L3 and remote-scratchpad bandwidth rose partly with the clock.
        lv["ridge_design"] = None
        if lv["clock"] in ("dram", "pcie") and lv.get("measured"):
            lv["ridge_design"] = {k: v * DESIGN_MHZ / CLOCK_MHZ for k, v in lv["ridge"]["measured"].items()}
        elif lv["clock"] in ("dram", "pcie"):
            lv["ridge_design"] = {k: v * DESIGN_MHZ / CLOCK_MHZ for k, v in lv["ridge"]["spec"].items()}
        cfg = {"l3": "l3", "scp_remote": "scp-remote", "dram": "dram", "l2": "l2", "scp": "scp-local", "l1d": "l1"}.get(lv["key"])
        if cfg:
            lv["clock_elasticity"] = mh[cfg]["clock_elasticity"]
        if lv["key"] in ("l3", "scp_remote"):
            e = mh[{"l3": "l3", "scp_remote": "scp-remote"}[lv["key"]]]["clock_elasticity"]
            f = DESIGN_MHZ / CLOCK_MHZ
            lv["ridge_design"] = {k: [v * f ** (1 - min(1, max(0, e))), v * f] for k, v in lv["ridge"]["measured"].items()}

    # ---- limits that act like ridges ------------------------------------------------------------------------------
    one_l2, one_dram = one_minion_tload("l2"), one_minion_tload("dram")
    launch = [r["wall_s"] - r["cycles_max"] / (CLOCK_MHZ * 1e6) for r in jsonl(os.path.join(DATA, "2026-09-18-aifoundry2", "runs.jsonl"))
              if r.get("launch", -1) >= 0 and "cycles_max" in r and r.get("wall_s")] if os.path.exists(
        os.path.join(DATA, "2026-09-18-aifoundry2", "runs.jsonl")) else []
    scp_all = all_minion_tload("scp")
    limits = {
        "one_minion_l2_bpc": 1024 / one_l2[16], "one_minion_dram_bpc": 1024 / one_dram[16],
        "one_minion_4line_bpc": 256 / one_l2[4],
        "tload_floor_cycles": one_l2[0], "tload_all_small_cycles": scp_all[4][0],
        "tload_all_4line_bpc": scp_all[4][1], "tload_all_1line_bpc": scp_all[1][1],
        # Little's law with a lone minion's rate, so a lower bound. The chip's 76 GB/s holds on both cards (23 Sep
        # reruns); the sparsity report's shorter probe read 72 GB/s on aifoundry3.
        "minions_to_saturate_dram": mh["dram"]["gbps_600"] / (1024 / one_dram[16] * ghz),
        "rerun_max_deviation": rerun_dev,
        "launch_overhead_ms_median": statistics.median(launch) * 1e3 if launch else None,
        "launch_overhead_ms_range": [min(launch) * 1e3, max(launch) * 1e3] if launch else None,
    }

    for lv in L:
        if lv["key"] == "pcie" and limits["launch_overhead_ms_range"]:
            lo, hi = limits["launch_overhead_ms_range"]
            lv["note"] = f"Not measured; only the per-launch overhead ({lo:.2f}-{hi:.2f} ms) is known."

    # ---- measured kernels, for the roofline chart ---------------------------------------------------------------
    gemv = jsonl(os.path.join(DATA, "2026-09-18-sparsity-aifoundry3", "gemv-dense.jsonl"), "SPARSITY ")[0]
    gemv_tf = 2 * 1024 * 4096 / (gemv["cycles_per_layer_mean"] / (CLOCK_MHZ * 1e6)) / 1e12  # partial sums added by the host
    tree = jsonl(os.path.join(DATA, "2026-09-18-sparsity-aifoundry3", "gemv-tree-dense.jsonl"), "SPARSITY ")[0]
    limits["gemv_tree_tflops"] = 2 * 1024 * 4096 / (tree["cycles_per_layer_mean"] / (CLOCK_MHZ * 1e6)) / 1e12
    limits["gemv_tree_us"] = tree["cycles_per_layer_mean"] / CLOCK_MHZ
    limits["gemv_host_us"] = gemv["cycles_per_layer_mean"] / CLOCK_MHZ
    kernels = [
        {"name": "fp32 matmul, tiles in L2", "ai": 4, "t": mm["fp32-tensor-L2"]["tflops"], "prec": "fp32", "vs": "L2"},
        {"name": "fp16 matmul, tiles in L2", "ai": 8, "t": mm["fp16-tensor-L2"]["tflops"], "prec": "fp16", "vs": "L2"},
        {"name": "int8 matmul, tiles in L2", "ai": 16, "t": mm["int8-tensor-L2"]["tflops"], "prec": "int8", "vs": "L2"},
        {"name": "fp32 matmul, every tile from DRAM", "ai": 4, "t": mm["fp32-tensor-DRAM"]["tflops"], "prec": "fp32", "vs": "DRAM"},
        {"name": "batch-1 fp32 layer, weights in scratchpad (partial sums added by the host)", "ai": 0.5, "t": gemv_tf, "prec": "fp32", "vs": "scratchpad"},
    ]

    # ---- energy balance points (both sides are card power above idle), from the energy manual's data -------------
    # Energy per operation: manual section 3.2, TensorFMA with A and B in the L1 scratchpad at 600 MHz, pooled over
    # the Horace ablation and the 22 Sep card transfer (tensor.bars: fp32 on both cards, int8 on aifoundry2 only).
    # Not tensor.rows, which hold aifoundry2's values alone. A multiply-add counts as 2 operations.
    man = json.load(open(MANUAL))
    bars = man["tensor"]["bars"]

    def per_op(cfg):
        b = bars[cfg]
        return {"pj": b["mean"] / 2, "lo": b["lo"] / 2, "hi": b["hi"] / 2, "cards": b["cards"], "n": b["n"]}

    e_flop = {"fp32": per_op("fp32_randn"), "fp32_ones": per_op("fp32_ones"), "fp32_zeros": per_op("fp32_zeros"),
              "int8": per_op("int8_randn")}
    ef, ei = e_flop["fp32"]["pj"], e_flop["int8"]["pj"]
    # Energy per byte: section 4.2 (the memory probes above, re-run at a pinned 600 MHz on both cards over buffers
    # that were never written) and section 5 (TensorSend, 1 KB messages, both cards).
    lev, rings = man["reruns"]["levels_pj_per_byte"], man["reruns"]["rings_pj_per_byte"]
    e_byte = [("L1 data cache", lev["l1"]), ("L2 scratchpad, own shire", lev["scp-local"]), ("L2 cache", lev["l2"]),
              ("L2 scratchpad, other shire", lev["scp-remote"]), ("L3", lev["l3"]), ("DRAM", lev["dram"]),
              ("TensorSend, fast local network", rings["pair"]), ("TensorSend inside a shire", rings["shire"])]
    xs_keys = sorted(k for k in rings if k.startswith("xshire") and not k.endswith("-c4"))
    xs_pj = [min(rings[k]["mean"] for k in xs_keys), max(rings[k]["mean"] for k in xs_keys)]
    hops = [noc[k]["mean_hops"] for k in noc if k.startswith("xshire") and not k.endswith("-c4")]
    # The same TensorLoads on random data (section 4.1, both cards): the shire's own scratchpad and DRAM; and for L1
    # the catalogue's 32 B vector load (flw.ps) hitting L1 on random data, per byte.
    cat = man["catalogue"]["combined"]
    rnd = {w: cat[f"tload/{w}/random"]["mean"] for w in ("scp", "dram")}
    rnd["l1"] = cat["flw.ps/random/h2"]["mean"] / 32
    energy = {"e_flop": e_flop,
              "e_byte": [{"name": n, "pj": v["mean"], "lo": v["lo"], "hi": v["hi"], "balance_fp32": v["mean"] / ef,
                          "balance_int8": v["mean"] / ei} for n, v in e_byte],
              "xshire": {"pj": xs_pj, "patterns": xs_keys, "hops": [min(hops), max(hops)],
                         "balance_fp32": [x / ef for x in xs_pj], "balance_int8": [x / ei for x in xs_pj]},
              "random_tload": {w: {"pj": v, "balance_fp32": v / ef} for w, v in rnd.items()},
              "source": "docs/reports/data/2026-09-23-energy-manual/manual.json: tensor.bars, reruns, catalogue.combined"}

    a100 = {"peaks": A100["peaks_tflops"],
            "levels": [{"name": n, "tbs": s, "tbs_peak": pk, "ridge": {k: v / s for k, v in A100["peaks_tflops"].items()}}
                       for n, s, pk in A100["levels"]]}

    data = {"clock_mhz": CLOCK_MHZ, "design_mhz": DESIGN_MHZ, "noc_mhz": NOC_MHZ, "minions": MINIONS, "peaks": peaks,
            "op_cycles": op_cycles, "levels": L, "limits": limits, "kernels": kernels, "energy": energy, "a100": a100}

    # ---- printout ---------------------------------------------------------------------------------------------------
    print(f"Peaks per minion-cycle, and for {MINIONS} minions at {CLOCK_MHZ} MHz / {DESIGN_MHZ} MHz:")
    for k, v in peaks.items():
        d = f", measured {v['demo_per_cycle']:.2f}" if v.get("demo_per_cycle") else ""
        print(f"  {v['name']:44s} {v['per_cycle']:4d} {v['unit']}/cycle{d}  -> {v['chip_600']:6.2f} / {v['chip_design']:6.2f} T{v['unit']}/s")
    print(f"  op cycles (tiles in L2): " + ", ".join(f"{k} {c:.1f}" for k, c in op_cycles.items()))
    print(f"\nRidge points at {CLOCK_MHZ} MHz, FLOP (int8: OP) per byte fetched; fp32 / fp16 / int8 / fp32 vector:")
    fmt = lambda x: ("%.0f" % x) if x >= 100 else ("%.1f" % x) if x >= 10 else ("%.2f" % x)
    for lv in L:
        print(f"  {lv['name']}")
        for basis in ("measured", "demonstrated", "spec", "spec_max"):
            r = lv["ridge"].get(basis)
            if not r:
                continue
            b = lv.get(basis) or {}
            bw = f"{b['bpc']:.3f} B/minion-cycle" if b.get("bpc") else ""
            if basis == "spec_max":
                bw = f"{SPEC['dram_max'][0]:.1f} GB/s"
            vals = " / ".join(fmt(v) if not isinstance(v, list) else f"{fmt(v[0])}-{fmt(v[1])}" for v in (r["fp32"], r["fp16"], r["int8"], r["vec32"]))
            gbps = f", {b['gbps']:.0f} GB/s" if b.get("gbps") else ""
            print(f"    {basis:13s} {vals:32s} ({bw}{gbps})")
        if lv.get("clock_elasticity") is not None:
            print(f"    GB/s vs minion clock elasticity {lv['clock_elasticity']:.2f}")
        if lv.get("ridge_design"):
            r = lv["ridge_design"]
            vals = " / ".join(fmt(v) if not isinstance(v, list) else f"{fmt(v[0])}-{fmt(v[1])}" for v in (r["fp32"], r["fp16"], r["int8"]))
            print(f"    at {DESIGN_MHZ} MHz  {vals}")
    print("\nLimits:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in limits.items()})
    print("Kernels:", [(k["name"], k["ai"], round(k["t"], 3)) for k in kernels])
    print("Memory probes re-run 23 Sep (GB/s range over passes; B/minion-cycle):",
          {cfg: ([round(x, 1) for x in v["gbps"]], round(v["bpc_minion"], 3), v["passes"]) for cfg, v in rr.items()})
    print(f"  largest difference from the bandwidths used above: {100 * rerun_dev:.2f}%")
    print("Energy per operation above idle (pJ; fp32 per FLOP, int8 per OP):",
          {k: f"{v['pj']:.3f} [{v['lo']:.3f}-{v['hi']:.3f}], {v['cards']} card(s)" for k, v in e_flop.items()})
    print(f"  fp32 on random data costs {ef / e_flop['fp32_zeros']['pj']:.1f}x its zeros figure and "
          f"{ef / e_flop['fp32_ones']['pj']:.1f}x its all-ones figure")
    for e in energy["e_byte"]:
        print(f"  {e['name']:34s} {e['pj']:7.2f} pJ/B -> balance fp32 {e['balance_fp32']:6.2f} FLOP/B, int8 {e['balance_int8']:6.1f} OP/B")
    xs = energy["xshire"]
    print(f"  {'TensorSend between shires':34s} {xs['pj'][0]:.2f}-{xs['pj'][1]:.2f} pJ/B -> balance fp32 "
          f"{xs['balance_fp32'][0]:.2f}-{xs['balance_fp32'][1]:.2f}, int8 {xs['balance_int8'][0]:.1f}-{xs['balance_int8'][1]:.1f} "
          f"({len(xs['patterns'])} patterns, {xs['hops'][0]:.2f}-{xs['hops'][1]:.2f} hops mean)")
    for w, v in energy["random_tload"].items():
        what = "flw.ps L1 hit" if w == "l1" else "TensorLoad from " + w
        print(f"  {what} on random data: {v['pj']:.2f} pJ/B -> balance fp32 {v['balance_fp32']:.2f} FLOP/B")
    print("A100 ridges (sustained):", [(l["name"], {k: round(v, 1) for k, v in l["ridge"].items()}) for l in a100["levels"]])

    if args.embed:
        html = open(args.embed).read()
        pat = re.compile(r'(<script type="application/json" id="ridge-data">)(.*?)(</script>)', re.S)
        if len(pat.findall(html)) != 1:
            raise SystemExit(f"{args.embed}: expected exactly one ridge-data script tag")
        blob = json.dumps(data, separators=(",", ":"), default=lambda o: None)
        html = pat.sub(lambda m: m.group(1) + blob + m.group(3), html)
        open(args.embed, "w").write(html)
        print(f"embedded ridge data into {args.embed}")


if __name__ == "__main__":
    main()
