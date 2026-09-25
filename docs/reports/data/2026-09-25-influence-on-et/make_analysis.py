#!/usr/bin/env python3
"""Write analysis.json for the report "Influence functions on the ET-SoC-1" (docs/reports/sources/influence-on-et.*).

    python3 docs/reports/data/2026-09-25-influence-on-et/make_analysis.py

Desk analysis: no card was run for it. Every ET-SoC-1 number is read here from the repository's measured data
(the energy manual's manual.json, the 18 September matmul, sparsity and nocbench runs). Everything else is a constant
below with its kind and source:

    M  measured on an ET-SoC-1 lab card (read from a data file)
    D  derived: arithmetic on measured numbers
    S  vendor spec (datasheet, programmer's manual)
    X  published by others (papers, measured on their hardware)
    O  the influence-function report's owner: his measurements or cost model
    E  estimate: an assumption of this page, never measured

The page's explorer recomputes the same model in the browser from the `model` block; the reference cases in `s1`,
`duty` and `s2` are the explorer's model evaluated here, so the page's text and its chart agree.
"""
import json
import math
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")


def load(rel):
    return json.load(open(os.path.join(DATA, rel)))


def jsonl(rel, prefix):
    out = []
    for line in open(os.path.join(DATA, rel)):
        line = line.strip()
        if line.startswith(prefix):
            out.append(json.loads(line[len(prefix):].strip()))
    return out


def r(x, sig=4):
    """Round to sig significant figures for a readable JSON."""
    if x is None or x == 0 or not math.isfinite(x):
        return x
    return round(x, sig - 1 - int(math.floor(math.log10(abs(x)))))


# ---------------------------------------------------------------- measured on the ET-SoC-1 (M, read from files)
MAN = "2026-09-23-energy-manual/manual.json"
man = load(MAN)
comb = man["catalogue"]["combined"]
cards = man["catalogue"]["cards"]


def per_card_mean(key, field):
    return sum(cards[c]["summary"][key][field]["mean"] for c in ("aifoundry2", "aifoundry3")) / 2


sram_pj = comb["tload/scp/random"]            # pJ/B above idle, tensor load from the shire's own scratchpad
dram_pj = comb["tload/dram/random"]           # pJ/B above idle, tensor load from DRAM
sram_bw = per_card_mean("tload/scp/random", "bytes_per_s")
dram_bw = per_card_mean("tload/dram/random", "bytes_per_s")
idle = man["cards"]["idle"]                   # board W at rest: aifoundry2 (hot) and aifoundry3 (cool)
idle_T = man["cards"]["launch"]
idle_lo, idle_hi = min(idle.values()), max(idle.values())

# SWAR estimate for 1-bit codes: packed-integer vector instructions (the chip has no popcount instruction)
PI = ["fxor.pi/random/h2", "fand.pi/random/h2", "fsrl.pi/random/h2", "fadd.pi/random/h2"]
pi_pj = sum(comb[k]["mean"] for k in PI) / len(PI)
pi_rate = per_card_mean("fxor.pi/random/h2", "ops_per_s")
SWAR_INSTR_PER_256 = 14  # E: xor, a 12-instruction SWAR popcount per 32-bit lane, an add; 8 lanes = 256 bits

# atomics spread over 32 lines (the hot-line report), as a reference for scatter-accumulate
hot_nj = man["reruns"]["hotline_nj_per_op"]["spread"]
spread_rate = [x for x in man["sync"]["atomics"]["runs"] if x["label"] == "spread"][0]["ops_per_s"]

# the 18 September matmul benchmark: peak rate and board power per precision (aifoundry2, 600 MHz)
MM = "2026-09-18-aifoundry2/results.json"
mm = load(MM)
mm_idle = mm["idle_w"]
peak = {}
for row in mm["results"]:
    if row["workload"] in ("fp32-tensor-L2", "fp16-tensor-L2", "int8-tensor-L2"):
        p = row["mode"]
        peak[p] = {"ops_per_s": row["tflops"] * 1e12, "board_w": row["mean_w"],
                   "pj_per_op_above_idle": (row["mean_w"] - mm_idle) / (row["tflops"] * 1e12) * 1e12}

# the batch-1 1024x4096 fp32 layer in the scratchpads (sparsity report, aifoundry3): the S1 anchor
SP = "2026-09-18-sparsity-aifoundry3/energy-b/results.json"
sp = load(SP)["results"]["gemv-skip-0"]
tree = [x for x in jsonl("2026-09-18-sparsity-aifoundry3/gemv-tree-dense.jsonl", "SPARSITY")
        if abs(x["sparsity"]) < 1e-9][0]
anchor = {
    "bytes": 1024 * 4096 * 4,
    "t_s": tree["cycles_per_layer_mean"] / (tree["ghz"] * 1e9),
    "board_j": sp["j_per_unit"],
    "above_idle_j": sp["j_per_unit_above_idle"],
    "board_w": sp["mean_w"],
    "source": f"docs/reports/data/{SP} (gemv-skip-0: board J per layer) and "
              "docs/reports/data/2026-09-18-sparsity-aifoundry3/gemv-tree-dense.jsonl (cycles per layer)",
}
anchor["model_above_idle_j"] = anchor["bytes"] * sram_pj["mean"] * 1e-12

# chip-wide allreduce, 32 B, 1,024 minions (on-chip communication report, aifoundry2)
xar = [x for x in jsonl("2026-09-18-nocbench-aifoundry2/xallreduce-c1.jsonl", "NOCBENCH") if x["minions"] == 1024][0]
allreduce_us = xar["cycles_per_iter"] / 600e6 * 1e6

SRAM_USABLE = 32 * 2.25e6  # D: 2.5 MB scratchpad per shire, less the first 256 KB (offset 0 faulted); on-chip relay

et = {
    "sram_usable_B": {"v": SRAM_USABLE, "k": "D", "src": "32 shires × 2.25 MB: each 2.5 MB scratchpad less the first 256 KB (on-chip relay report)"},
    "sram_bw": {"v": r(sram_bw), "k": "M", "src": f"docs/reports/data/{MAN}: catalogue tensor loads from the shire's own scratchpad, random data, both cards"},
    "sram_pj_B": {"v": r(sram_pj["mean"]), "lo": r(sram_pj["lo"]), "hi": r(sram_pj["hi"]), "k": "M", "src": "energy manual §4.1, above idle, random data, 3 passes on each card"},
    "dram_B": {"v": 32e9, "k": "S", "src": "LPDDR4X, 32 GB per card"},
    "dram_bw": {"v": r(dram_bw), "k": "M", "src": "energy manual §4.1, tensor loads from DRAM, both cards"},
    "dram_pj_B": {"v": r(dram_pj["mean"]), "lo": r(dram_pj["lo"]), "hi": r(dram_pj["hi"]), "k": "M", "src": "energy manual §4.1, above idle, random data"},
    "idle_W": {"lo": r(idle_lo), "hi": r(idle_hi), "k": "M",
               "src": f"board power at rest: aifoundry3 {idle['aifoundry3']:.1f} W at {idle_T['aifoundry3']['T']:.0f} °C, aifoundry2 {idle['aifoundry2']:.1f} W at {idle_T['aifoundry2']['T']:.0f} °C (energy manual, cards block)"},
    "peak": {p: {"ops_per_s": r(v["ops_per_s"]), "board_w": r(v["board_w"]), "pj_op": r(v["pj_per_op_above_idle"]), "k": "M/D"} for p, v in peak.items()},
    "peak_src": f"docs/reports/data/{MM}: matmul benchmark, tiles in L2, aifoundry2, 600 MHz; pJ per op above the run's {mm_idle:.1f} W idle (D)",
    "bit": {"ops_per_s": r(pi_rate * 256 / SWAR_INSTR_PER_256), "pj_op": r(pi_pj * SWAR_INSTR_PER_256 / 256), "k": "E",
            "src": f"no popcount instruction: SWAR on the vector unit, about {SWAR_INSTR_PER_256} packed-integer instructions per 256 bits (E) at the catalogue's measured {pi_rate/1e9:.0f} G instructions/s and {pi_pj:.1f} pJ each (M)"},
    "rows16": {"k": "E", "src": "a tensor op multiplies 16 rows of A; ops with fewer rows (one query per row) were measured only in fp32, at batch 1, where the pass stayed load-bound"},
    "l1_scp_B": {"v": 3072, "k": "S/M", "src": "the L1 in scratchpad mode: sets 0–11, 3 KB per minion (memory-hierarchy report); a 4,096-coordinate int8 query (4 KB) does not fit, so every minion re-reads the query tiles for each tile of 16 codes it holds (E)"},
    "launch_ms": {"lo": 0.2, "hi": 0.4, "k": "M", "src": "host kernel launch on aifoundry3 (sparse-compute report); a persistent kernel avoids it"},
    "allreduce_us": {"v": r(allreduce_us, 2), "k": "M", "src": "32 B TensorReduce + TensorBroadcast over 1,024 minions, aifoundry2 (on-chip communication report)"},
    "atomics_spread": {"ops_per_s": r(spread_rate, 3), "nj": r(hot_nj["mean"], 3), "k": "M", "src": "global atomics spread over 32 lines (hot-line report; energy from the energy manual's reruns)"},
    "pcie_Bps": {"v": 15.75e9, "k": "S", "src": "PCIe Gen4 x8, never timed on these cards"},
    "anchor": {k: (r(v) if isinstance(v, float) else v) for k, v in anchor.items()},
}

# ---------------------------------------------------------------- H100 (S spec, X published, E estimate)
H100_IDLE = (60.0, 90.0)
H100_TDP = 700.0
h_peak = {"int8": 1978.9e12, "fp16": 989.4e12, "fp32": 494.7e12}  # S: dense tensor-core rates (fp32 runs as TF32)
H_EFF = 0.6  # E: fraction of peak a scoring GEMM sustains
h_bit = 132 * 16 * 1.98e9 * 32 / 2  # E: popc 16/clk/SM (CUDA guide) x 132 SMs x 1.98 GHz x 32 bits, halved for xor+add
h_lane = 132 * 128 * 1.98e9  # S: fp32 lane-operations per second (132 SMs x 128 lanes x 1.98 GHz)
# E: an xor, a popc and an add per 32 bits, each priced as one fp32 lane-operation at the TDP: (700 - 75) W / h_lane
h_bit_pj = 3 * (H100_TDP - sum(H100_IDLE) / 2) / h_lane / 32 * 1e12
h100 = {
    "hbm_B": {"v": 80e9, "k": "S", "src": "H100 SXM datasheet"},
    "hbm_bw": {"v": 3.0e12, "spec": 3.35e12, "k": "E", "src": "90% of the 3.35 TB/s spec"},
    "l2_pin_B": {"v": 37.5e6, "k": "E", "src": "at most three quarters of the 50 MB L2 kept pinned with an access-policy window (the true set-aside limit not checked)"},
    "l2_bw": {"v": 4.3e12, "k": "X", "src": "an A100 SXM4's measured L2 read bandwidth, as a floor (memory-hierarchy report's A100 notes)"},
    "hbm_pj_B": {"v": 105.0, "path": 155.3, "k": "X/E", "src": "A100 study (Antepara et al., SC'25): 13.11 pJ/bit for the HBM level alone, standing in for Hopper's newer process and HBM3 (E); the A100's whole path through L2 and L1 is 19.41 pJ/bit (155 pJ/B), not used"},
    "l2_pj_B": {"v": 37.7, "path": 50.4, "k": "X/E", "src": "same study: 4.71 pJ/bit for the L2 level alone; 6.30 with L1 (50 pJ/B), not used"},
    "idle_W": {"lo": H100_IDLE[0], "hi": H100_IDLE[1], "k": "E", "src": "not measured here"},
    "launch_s": {"v": 1.3e-6, "k": "X", "src": "per kernel with CUDA graphs, measured on an H100 (cited in the sparse-compute report)"},
    "peak": {p: {"ops_per_s": v, "eff": H_EFF, "pj_op": r((H100_TDP - sum(H100_IDLE) / 2) / v * 1e12)} for p, v in h_peak.items()},
    "bit": {"ops_per_s": r(h_bit), "eff": H_EFF, "pj_op": r(h_bit_pj), "k": "E",
            "src": "popc 16 per clock per SM (CUDA C++ Programming Guide) × 132 SMs × 1.98 GHz × 32 bits, halved for the xor and the add; Hopper has no binary tensor cores. Energy: an xor, a popc and an add per 32 bits, each priced as one fp32 lane-operation at the TDP, (700 − 75) W ÷ (132 × 128 lanes × 1.98 GHz)"},
    "peak_src": "H100 SXM datasheet (dense int8, fp16/bf16, TF32); 60% sustained (E); energy per op above idle = (700 W TDP − 75 W) ÷ peak (E)",
}

# ---------------------------------------------------------------- host CPU (E): the scorer that is already powered
cpu = {
    "bw": {"v": 200e9, "k": "E", "src": "one server socket's DDR5, or its L3 for a small shard"},
    "rate": {"int8": 4e12, "fp16": 2e12, "fp32": 2e12, "bit": 5e13, "k": "E", "src": "AVX-512 VNNI / FMA / VPOPCNTDQ on one socket"},
    "inc_W": {"lo": 40.0, "hi": 200.0, "k": "E", "src": "incremental socket power while it scores; the host is powered anyway"},
}

# ---------------------------------------------------------------- the owner's numbers (O) and published ones (X)
owner = {
    "q_grad_s": 0.25, "ihvp_s": 1.06,
    "query_energy_J": [r(1.31 * 350), r(1.31 * 700)],
    "amortized_query_h100h": 8.4,
    "src": "influence-functions report §3.1 (the 8B price table: P = 8×10⁹, T = 2,048, H100 at 40% of 989 TFLOP/s); power 350–700 W is E",
    "atlas": {"P": 34122, "N": 60000, "Q": 100, "C": 10, "activation": "tanh", "curvature_dtype": "float64",
              "scan_s": 0.231, "grad_pass_s": 0.558, "lissa_500_s": 7.07, "cg_20_s": 5.36, "ekfac_query_s": 0.0061,
              "gpu": "A100-SXM4-80GB",
              "src": "MNIST influence atlas manifest (costs.rows[kfac].phases.scan.seconds; costs.measured; config.activation)"},
    "haiku_k": {"v": 3e6, "src": "secondhand: a summary of Grosse's 13 April 2026 talk (the owner's Bergson page, §9.4)"},
}

# ---------------------------------------------------------------- the scoring model (the explorer runs the same)
BYTES_PER = {"bit": 1 / 8, "int8": 1, "fp16": 2, "fp32": 4}


MINIONS, TILE = 1024, 16


def query_bytes(n, k, prec, Q, chips):
    """Query tiles re-read from the shire's SRAM: a minion's 3 KB L1 scratchpad cannot hold a query, so each minion
    loads the Q query rows once for every tile of 16 codes it holds (E; the layout the first experiment would use)."""
    per_minion = math.ceil(n / (chips * MINIONS))
    return chips * MINIONS * math.ceil(per_minion / TILE) * Q * k * BYTES_PER[prec]


def et_pass(n, k, prec, Q, where="sram", rows16=False):
    """One pass of Q queries over n codes of k coordinates on the ET-SoC-1. Returns chips, time, J above idle."""
    B = n * k * BYTES_PER[prec]
    chips = max(1, math.ceil(B / (SRAM_USABLE if where == "sram" else 32e9)))
    Bq = query_bytes(n, k, prec, Q, chips)
    Qc = math.ceil(Q / 16) * 16 if (rows16 and prec != "bit") else Q
    if prec == "bit":
        rate, pjop, ops = pi_rate * 256 / SWAR_INSTR_PER_256, pi_pj * SWAR_INSTR_PER_256 / 256, Qc * n * k
    else:
        rate, pjop, ops = peak[prec]["ops_per_s"], peak[prec]["pj_per_op_above_idle"], 2 * Qc * n * k
    if where == "sram":
        t_load, e_bytes = (B + Bq) / chips / sram_bw, (B + Bq) * sram_pj["mean"]
    else:  # codes stream from DRAM, the query tiles from the shire's SRAM
        t_load, e_bytes = max(B / dram_bw, Bq / sram_bw) / chips, B * dram_pj["mean"] + Bq * sram_pj["mean"]
    t_comp = ops / chips / rate
    t = max(t_load, t_comp)
    e_above = max(e_bytes, ops * pjop) * 1e-12
    return {"B": B, "Bq": Bq, "chips": chips, "t": t, "e_above": e_above, "bound": "memory" if t_load >= t_comp else "compute"}


def h100_pass(n, k, prec, Q, idle_w):
    B = n * k * BYTES_PER[prec]
    gpus = max(1, math.ceil(B / 80e9))
    l2 = B <= 37.5e6
    bw = 4.3e12 if l2 else 3.0e12
    pjB = h100["l2_pj_B" if l2 else "hbm_pj_B"]["v"]
    pk = h100["bit"] if prec == "bit" else h100["peak"][prec]
    ops = (1 if prec == "bit" else 2) * Q * n * k
    t = max(B / gpus / bw, ops / gpus / (pk["ops_per_s"] * H_EFF)) + 1.3e-6
    e = gpus * idle_w * t + (B * pjB + ops * pk["pj_op"]) * 1e-12
    return {"B": B, "gpus": gpus, "l2": l2, "t": t, "e": e}


def cpu_pass(n, k, prec, Q, w):
    B = n * k * BYTES_PER[prec]
    ops = (1 if prec == "bit" else 2) * Q * n * k
    t = max(B / cpu["bw"]["v"], ops / cpu["rate"][prec])
    return {"t": t, "e": t * w}


def case(n, k, prec, Q, rows16=False):
    """Board energy per pass on each device (lo, hi) and the ET's lead."""
    e = et_pass(n, k, prec, Q, rows16=rows16)
    et_lo = e["e_above"] + e["chips"] * idle_lo * e["t"]
    et_hi = e["e_above"] + e["chips"] * idle_hi * e["t"]
    h_lo = h100_pass(n, k, prec, Q, H100_IDLE[0])
    h_hi = h100_pass(n, k, prec, Q, H100_IDLE[1])
    return {"n": n, "k": k, "prec": prec, "Q": Q, "MB": r(e["B"] / 1e6), "chips": e["chips"],
            "et_us": r(e["t"] * 1e6, 3), "et_mJ": [r(et_lo * 1e3, 3), r(et_hi * 1e3, 3)], "et_above_mJ": r(e["e_above"] * 1e3, 3),
            "et_bound": e["bound"], "h100_where": "L2" if h_lo["l2"] else "HBM",
            "h100_us": r(h_lo["t"] * 1e6, 3), "h100_mJ": [r(h_lo["e"] * 1e3, 3), r(h_hi["e"] * 1e3, 3)],
            "lead": [r(h_lo["e"] / et_hi, 2), r(h_hi["e"] / et_lo, 2)]}


s1 = {
    "hbm_case": case(16000, 4096, "int8", 1),      # 65.5 MB: a static shard that spills an H100's pinned L2
    "l2_case": case(9155, 4096, "int8", 1),        # 37.5 MB: small enough to stay pinned in the H100's L2
    "fp16_case": case(8000, 4096, "fp16", 1),
    "hbm_case_rows16": case(16000, 4096, "int8", 1, rows16=True),
    "capacity_codes_k4096": {p: int(SRAM_USABLE // (4096 * b)) for p, b in BYTES_PER.items()},
}
# parity in Q (queries per pass) for the 65.5 MB shard, charging the ET its idle during the pass only
QS = [1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128, 192, 256, 384, 512, 1024]
for prec, n in (("int8", 16000), ("fp16", 8000)):
    parity = []
    for Q in QS:
        c = case(n, 4096, prec, Q)
        parity.append({"Q": Q, "et_mJ_per_q": [r(x / Q, 3) for x in c["et_mJ"]], "h100_mJ_per_q": [r(x / Q, 3) for x in c["h100_mJ"]]})
    # the smallest Q where the ET's best case meets the H100's worst, and where the ET's worst meets the H100's best
    lo = next((p["Q"] for p in parity if p["et_mJ_per_q"][1] >= p["h100_mJ_per_q"][0]), None)
    hi = next((p["Q"] for p in parity if p["et_mJ_per_q"][0] >= p["h100_mJ_per_q"][1]), None)
    s1["parity_" + prec] = {"table": parity, "Q": [lo, hi]}
s1["q16_case"] = case(16000, 4096, "int8", 16)  # the largest Q the critique allows S1

# duty cycle: the ET card is dedicated, so its idle is paid between queries; the H100 and the host are there anyway.
# Break-even arrival rate: chips x P_idle / lambda + e_above = the other device's energy per pass (one query per pass).
def breakeven(n, prec="int8", k=4096):
    e = et_pass(n, k, prec, 1)
    h = (h100_pass(n, k, prec, 1, H100_IDLE[0])["e"], h100_pass(n, k, prec, 1, H100_IDLE[1])["e"])
    c = (cpu_pass(n, k, prec, 1, cpu["inc_W"]["lo"])["e"], cpu_pass(n, k, prec, 1, cpu["inc_W"]["hi"])["e"])
    lo, hi = e["chips"] * idle_lo, e["chips"] * idle_hi
    return {"chips": e["chips"], "h100_mJ": [r(h[0] * 1e3, 3), r(h[1] * 1e3, 3)], "cpu_mJ": [r(c[0] * 1e3, 3), r(c[1] * 1e3, 3)],
            "vs_h100_qps": [r(lo / (h[1] - e["e_above"]), 2), r(hi / (h[0] - e["e_above"]), 2)],
            "vs_cpu_qps": [r(lo / (c[1] - e["e_above"]), 2), r(hi / (c[0] - e["e_above"]), 2)]}


hc = s1["hbm_case"]
be_hbm, be_l2 = breakeven(16000), breakeven(9155)
duty = {
    "et_idle_per_query_J_at_1qps": [r(idle_lo), r(idle_hi)],
    "et_active_mJ": [r(v, 3) for v in hc["et_mJ"]],
    "ratio_idle_to_active": [r(idle_lo / (hc["et_mJ"][1] * 1e-3), 2), r(idle_hi / (hc["et_mJ"][0] * 1e-3), 2)],
    "hbm_case": be_hbm, "l2_case": be_l2,
    "breakeven_vs_h100_qps": [min(be_hbm["vs_h100_qps"][0], be_l2["vs_h100_qps"][0]), max(be_hbm["vs_h100_qps"][1], be_l2["vs_h100_qps"][1])],
    "breakeven_vs_cpu_qps": [min(be_hbm["vs_cpu_qps"][0], be_l2["vs_cpu_qps"][0]), max(be_hbm["vs_cpu_qps"][1], be_l2["vs_cpu_qps"][1])],
    "query_side_J": owner["query_energy_J"],
    "step_share_of_query": [r(hc["h100_mJ"][0] * 1e-3 / owner["query_energy_J"][1], 2), r(hc["h100_mJ"][1] * 1e-3 / owner["query_energy_J"][0], 2)],
}

# ---------------------------------------------------------------- the killed candidates' numbers (K1, K4, K5)
def dram_fetch(B):
    """Read B bytes from the ET card's DRAM: time and board energy (above idle plus the card's idle meanwhile)."""
    t = B / dram_bw
    e = B * dram_pj["mean"] * 1e-12
    return {"MB": r(B / 1e6), "ms": r(t * 1e3, 2), "mJ": [r((e + idle_lo * t) * 1e3, 2), r((e + idle_hi * t) * 1e3, 2)]}


k1 = dram_fetch(64e6)  # a per-query stage-2 shortlist of 64 MB (map-0 cand. 1)
k1["pcie_ms"] = r(64e6 / 15.75e9 * 1e3, 2)
k1["h100_us"] = r(64e6 / 3.0e12 * 1e6, 2)
k1["x_pass"] = [r(64e6 / dram_bw / (hc["et_us"] * 1e-6), 2), r(64e6 / 15.75e9 / (hc["et_us"] * 1e-6), 2)]
k4 = dram_fetch(25e6)  # a 20-term query over 10^7 documents: 20 bitmaps of 1.25 MB (map-0, E)
k5_bits_n = 16000 * 8  # the same 65.5 MB as 1-bit codes, too big to pin in the H100's L2
k5 = {"et_int8_pJ": [r(v * 1e-3 / (16000 * 4096) * 1e12, 2) for v in hc["et_mJ"]],
      "h100_bit_pJ": [r(h100_pass(k5_bits_n, 4096, "bit", 1, w)["e"] / (k5_bits_n * 4096) * 1e12, 2) for w in H100_IDLE]}
k7 = {"chips_1e7": et_pass(1e7, 4096, "int8", 1)["chips"], "kW_1e7": [r(et_pass(1e7, 4096, "int8", 1)["chips"] * w / 1e3, 2) for w in (idle_lo, idle_hi)],
      "hot_tier": breakeven(1e5)}  # the top 1% of 10^7 as a hot tier: 10^5 codes
kills = {"k1": k1, "k4": k4, "k5": k5, "k7": k7}

# ---------------------------------------------------------------- S2: the atlas scan on one chip
A = owner["atlas"]
scanF = 2 * A["Q"] * A["C"] * A["N"] * A["P"] + 6 * A["P"] * A["N"]
a100_J = (250 * A["scan_s"], 400 * A["scan_s"])  # E: A100 board power while scanning
s2 = {"scan_flop": r(scanF, 3), "a100_s": A["scan_s"], "a100_tflops_nominal": r(scanF / A["scan_s"] / 1e12, 3),
      "a100_J": [r(a100_J[0], 2), r(a100_J[1], 2)], "a100_W": [250, 400],
      "et": []}
for prec, eff in [("fp16", 1.0), ("fp32", 1.0), ("fp32", 0.3), ("fp32", 0.1)]:
    t = scanF / (eff * peak[prec]["ops_per_s"])
    s2["et"].append({"prec": prec, "eff": eff, "s": r(t, 3), "J": r(t * peak[prec]["board_w"], 3)})
s2["breakeven_eff_fp32"] = [r(scanF / peak["fp32"]["ops_per_s"] * peak["fp32"]["board_w"] / a100_J[1], 2),
                            r(scanF / peak["fp32"]["ops_per_s"] * peak["fp32"]["board_w"] / a100_J[0], 2)]
s2["breakeven_eff_fp16"] = [r(scanF / peak["fp16"]["ops_per_s"] * peak["fp16"]["board_w"] / a100_J[1], 2),
                            r(scanF / peak["fp16"]["ops_per_s"] * peak["fp16"]["board_w"] / a100_J[0], 2)]
s2["time_eff_needed"] = {p: r(scanF / peak[p]["ops_per_s"] / A["scan_s"], 2) for p in ("fp16", "fp32")}
s2["atlas_bytes"] = {"weights_KB": r(A["P"] * 4 / 1e3, 3), "images_MB": r(A["N"] * 196 / 1e6, 3),
                     "queries_MB": r(A["Q"] * A["P"] * 4 / 1e6, 3)}
s2["lissa_ms_per_step"] = r(A["lissa_500_s"] / 500 * 1e3, 2)
s2["cg_ms_per_iter"] = r(A["cg_20_s"] / 20 * 1e3, 3)

# ---------------------------------------------------------------- dense work: one ET card against one H100
et_fp16 = peak["fp16"]
h_grad = 989.4e12 * 0.4
dense = {"slower": [r(h_grad / et_fp16["ops_per_s"], 2), r(h_grad / (0.6 * et_fp16["ops_per_s"]), 2)],
         "energy": [r(et_fp16["board_w"] / et_fp16["ops_per_s"] / (700 / h_grad), 2),
                    r(et_fp16["board_w"] / (0.6 * et_fp16["ops_per_s"]) / (700 / h_grad), 2)],
         "src": "ET fp16 at 60–100% of its measured 19.0 TFLOP/s and 59.3 W board (M/E) against an H100 at 40% of 989 TFLOP/s and 700 W (the owner's model, O/S)"}

# ---------------------------------------------------------------- the pipeline at big-lab scale
H = 3600.0
pipeline = [
    {"key": "scan", "label": "Scan 10⁷ candidates by recomputing gradients", "h": 702, "per": "per batch of 100 queries", "fit": "no", "k": "O",
     "why": "dense backprop, the bill itself; one ET card is 21–35× slower and spends 1.8–2.9× the energy"},
    {"key": "build", "label": "Build a sketch index of 10⁷ gradients", "h": 1150, "per": "once per checkpoint", "fit": "no", "k": "O",
     "why": "dense backprop plus a projection; the sparse sketches would need 16 GB per sequence over a 15.75 GB/s link"},
    {"key": "valid", "label": "Validation retrains (LDS)", "h": 506, "per": "per method", "fit": "no", "k": "O", "why": "training runs"},
    {"key": "rerank", "label": "Exact rerank of the top 10⁴ at 70B", "h": 6.0, "per": "per query", "fit": "no", "k": "E",
     "why": "10⁴ fresh gradients; with an EK-FAC iHVP it is over 99.9% of a query's energy"},
    {"key": "stats", "label": "EK-FAC curvature statistics", "h": 2.07, "per": "once per checkpoint", "fit": "no", "k": "O", "why": "dense gradient passes"},
    {"key": "astra", "label": "Iterative iHVP (ASTRA, 300 steps)", "h": 1.41, "per": "per query", "fit": "no", "k": "O", "why": "minibatch Hessian-vector products are gradients"},
    {"key": "qgrad", "label": "Query gradients, 100 queries", "h": 0.007, "per": "per batch", "fit": "no", "k": "O", "why": "dense backprop; an 8B model in fp16 does not fit one card's 32 GB comfortably, and there is no bf16"},
    {"key": "eigh", "label": "Eigendecompose the Kronecker factors", "h": 0.002, "per": "once per checkpoint", "fit": "no", "k": "O",
     "why": "needs fp64 (the chip has none, and no hardware divide or square root); factors up to 14,336² (0.8 GB in fp32, 1.6 GB in fp64) exceed the 72 MB of SRAM"},
    {"key": "ihvp", "label": "EK-FAC iHVP (1.06 s)", "h": 1.06 / H, "per": "per query", "fit": "no", "k": "O",
     "why": "compute-bound matmuls against 108 GB of resident bases: 1,500 chips of SRAM to keep them on chip"},
    {"key": "lookup", "label": "Stream the whole 82 GB sketch index, 1 query", "h": 82e9 / 3.35e12 / H, "per": "per query", "fit": "no", "k": "S",
     "why": "bandwidth-bound: the ET's DRAM gives 76 GB/s at 129 pJ/B above idle, 44× slower than HBM, and holds 32 GB"},
    {"key": "prefilter", "label": "Lexical prefilter (BM25/TF-IDF)", "h": 1.27e-3 / H, "per": "per query", "fit": "killed", "k": "X",
     "why": "ET-shaped (per-core document ownership, no atomics) but about 10⁻⁶ of the bill; the host CPU's inverted index does it"},
    {"key": "scatter", "label": "Scatter the gradients' sparse parts into sketches", "h": 0.01 * 702, "per": "per batch of 100 queries (at most 1% of the scan)", "fit": "killed", "k": "E",
     "why": "the one ET-shaped step with real size, but the data is born in the GPU's backward pass (16 GB per sequence would have to cross a 15.75 GB/s link); GPUs keep the buckets in L2 or avoid the scatter; the chip's gather/scatter rate is unmeasured (S3)"},
    {"key": "shard", "label": "Score a static 65 MB shard, 1 query (S1)", "h": s1["hbm_case"]["h100_us"] * 1e-6 / H, "per": "per query", "fit": "research", "k": "E",
     "why": "the one physical edge: 4.2 pJ/B from the chip's own SRAM; no time win, and it needs a busy card"},
    {"key": "topk", "label": "Select the top k (fused into scoring)", "h": 1e-6 / H, "per": "per query", "fit": "feature", "k": "E",
     "why": "10⁴–1.5×10⁵ heap inserts per query even at N = 10¹⁰: free in a GPU kernel's epilogue; kept only as part of S1"},
]
for p in pipeline:
    p["h"] = r(p["h"], 3)
    p["J"] = r(p["h"] * H * 700, 3)

presets = [
    {"key": "shard", "label": "S1: a static shard", "n": 16000, "k": 4096, "prec": "int8", "Q": 1, "lam": 1, "where": "sram"},
    {"key": "busy", "label": "The same, kept busy", "n": 16000, "k": 4096, "prec": "int8", "Q": 1, "lam": 1e4, "where": "sram"},
    {"key": "less", "label": "Fine-tuning attribution", "n": 270000, "k": 8192, "prec": "int8", "Q": 100, "lam": 1, "where": "sram"},
    {"key": "owner", "label": "The author's 10⁷ index", "n": 1e7, "k": 4096, "prec": "int8", "Q": 1, "lam": 1, "where": "sram"},
    {"key": "haiku", "label": "3 million dimensions", "n": 1e6, "k": 3e6, "prec": "fp16", "Q": 1, "lam": 1, "where": "dram"},
]

out = {
    "generated": str(date(2026, 9, 25)),
    "producer": "docs/reports/data/2026-09-25-influence-on-et/make_analysis.py",
    "kinds": {"M": "measured on an ET-SoC-1 lab card", "D": "derived: arithmetic on measured numbers", "S": "vendor spec",
              "X": "published by others", "O": "the influence-function report's owner (his measurements or cost model)",
              "E": "estimate: an assumption of this page, never measured"},
    "model": {"et": et, "h100": h100, "cpu": cpu, "bytes_per": BYTES_PER, "h_eff": H_EFF},
    "owner": owner,
    "s1": s1, "duty": duty, "kills": kills, "s2": s2, "dense": dense, "pipeline": pipeline, "presets": presets,
    "topk_inserts": {"N": [1e9, 1e10], "k": 1e4, "inserts": [r(1e4 * (1 + math.log(1e9 / 1e4)), 2), r(1e4 * (1 + math.log(1e10 / 1e4)), 2)]},
}
path = os.path.join(HERE, "analysis.json")
json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
print("wrote", os.path.relpath(path, ROOT))
print("anchor: measured %.1f µs, %.0f µJ board, %.0f µJ above idle; model above idle %.0f µJ"
      % (anchor["t_s"] * 1e6, anchor["board_j"] * 1e6, anchor["above_idle_j"] * 1e6, anchor["model_above_idle_j"] * 1e6))
for k in ("hbm_case", "l2_case", "fp16_case"):
    print(k, s1[k])
print("parity Q int8:", s1["parity_int8"]["Q"], "fp16:", s1["parity_fp16"]["Q"])
print("rows16:", s1["hbm_case_rows16"])
print("duty:", duty)
print("q16:", s1["q16_case"])
print("kills:", kills)
print("s2:", s2)
print("dense:", dense)
