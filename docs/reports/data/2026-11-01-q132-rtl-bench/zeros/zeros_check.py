#!/usr/bin/env python3
"""Item 12's two remaining pieces, on the fixed bench. POST HOC: nothing here was registered, and E78's 0.61 W was known before any of it.

    python3 zeros_check.py > zeros-check.txt        # from this directory; standard library only

(1) int8 zeros sit 0.61 W above fp32 zeros. Does the bench's count of what stays on explain it? (2) Does the fixed bench change Q130(i)'s 0.20-0.37 pJ?
acct-*.txt and clocks-*.json come from a build of this bench with acct_files.cpp in place of acct.cpp, and vcd_clocks.py; q130i-rerun.txt from Q130(i)'s own sim/run.sh with and without -fno-dfg.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
B = os.path.abspath(os.path.join(HERE, ".."))
DD = os.path.abspath(os.path.join(B, ".."))
load = lambda p: json.load(open(p))
c = load(os.path.join(B, "counts-v2.json"))["rows"]
e78 = load(os.path.join(DD, "2026-10-31-e78-kinds-energy-matrix/e78.json"))["items"]
pr = load(os.path.abspath(os.path.join(DD, "..", "..", "..", "tools", "claims-v3", "kinds", "predictions-e103.json")))["models"]
F, I = pr["float"]["coef_fJ"], pr["int8"]["coef_fJ"]
rows = {}
print("# (1) per second, chip-wide, on E78's rates")
print(f"{'':42s} {'fp32 zeros':>12s} {'fp16 zeros':>12s} {'int8 zeros':>12s} {'int8/fp32':>10s}")
K = ("fp32.zeros", "fp16.zeros", "int8.zeros")
def line(name, f, fmt="{:12.3e}"):
    v = [f(k) for k in K]
    print(f"{name:42s} " + " ".join(fmt.format(x) for x in v) + f" {v[2] / v[0]:10.3f}")
    return v
rate = {k: e78[k]["rate"]["mean"] for k in K}
m = {k: c[k]["mean"] for k in K}
line("TensorFMA ops", lambda k: rate[k])
line("cycles an op (bench; card 546, 546, 318)", lambda k: m[k]["cycles"], "{:12.0f}")
line("register bits clocked, enable high", lambda k: m[k]["ff"]["all"]["clocked"] * rate[k])
line("register bits seeing a clock edge", lambda k: m[k]["ff"]["all"]["present"] * rate[k])
line("  of which the multiply-add unit's", lambda k: (m[k]["ff"]["txfma"]["present"] + m[k]["ff"]["tima"]["present"]) * rate[k])
line("register bits that change", lambda k: m[k]["ff"]["all"]["toggles"] * rate[k])
line("merged nets toggling (nets_map)", lambda k: m[k]["vpu"]["nets_map"] * rate[k])
line("clock-net toggles (coverage)", lambda k: m[k]["clock_nets_cov"] * rate[k])
line("scratchpad line reads", lambda k: m[k]["scp_reads"] * rate[k])
S = line("measured S, E78, W over idle", lambda k: e78[k]["S"]["mean"], "{:12.3f}")
print(f"S(int8 zeros) - S(fp32 zeros) = {S[2] - S[0]:.3f} W; 95% half-widths {e78['int8.zeros']['S'].get('ci95'):.3f}, {e78['fp32.zeros']['S'].get('ci95'):.3f}")
print("\n# priced at M4's float constants, an extrapolation: M4 was fitted over zeros, so its a has never been tested on the bits that stay clocked on zeros")
def price(k):
    s = m[k]["vpu"]["by_stage"]
    bus = s["lane_operand_bus"]
    core = s["multiplier"] + s["adder_norm"]
    rest = m[k]["vpu"]["nets_map"] - bus - core
    nets = (core * F["k_core"] + bus * F["k_bus"] + rest * F["k_rest"]) * 1e-15 * rate[k]
    clk = m[k]["ff"]["all"]["clocked"] * F["a_clocked"] * 1e-15 * rate[k]
    return clk, nets
pf, pi = price(K[0]), price(K[2])
print(f"fp32 zeros: clocked {pf[0]:.3f} W + nets {pf[1]:.3f} W = {sum(pf):.3f} W, of S {S[0]:.3f} W; left {S[0] - sum(pf):.3f} W")
print(f"int8 zeros: clocked {pi[0]:.3f} W + nets {pi[1]:.3f} W = {sum(pi):.3f} W, of S {S[2]:.3f} W; left {S[2] - sum(pi):.3f} W")
print(f"the count says int8 - fp32 = {sum(pi) - sum(pf):+.3f} W, against the measured {S[2] - S[0]:+.3f} W: {S[2] - S[0] - (sum(pi) - sum(pf)):.3f} W unexplained, and the sign is wrong")
print(f"to close that by the integer unit's clock alone at a = {F['a_clocked']:.3f} fJ, it would need {(S[2] - S[0] - (sum(pi) - sum(pf))) / (F['a_clocked'] * 1e-15 * rate[K[2]]) / 4096:.0f} more register bits on a slot's clock, where the RTL has {m[K[2]]['ff']['tima']['present'] / 4096:.0f}")
reads = [m[k]["scp_reads"] * rate[k] for k in K]
print(f"\n# what points the right way: scratchpad reads, {reads[2] / reads[0]:.3f}x, and ops, {rate[K[2]] / rate[K[0]]:.3f}x. Neither is priced by this bench: the dcache and the core are not in it")
print(f"if all of S(zeros) scaled with reads: {S[0] * reads[2] / reads[0]:.3f} W for int8, measured {S[2]:.3f} W. One number; a coincidence is not excluded")
c1, c2 = m[K[0]]["ff"]["all"]["clocked"] * rate[K[0]], m[K[2]]["ff"]["all"]["clocked"] * rate[K[2]]
det = c1 * reads[2] - c2 * reads[0]
print(f"S = c x clocked + r x reads, two equations, two unknowns: c = {(S[0] * reads[2] - S[2] * reads[0]) / det * 1e15:.3f} fJ a bit, r = {(c1 * S[2] - c2 * S[0]) / det * 1e12:.2f} pJ a line. That c is far below M4's a, so this reading needs the bits clocked on zeros to be nearly free")
d = (S[2] - S[0]) / (rate[K[2]] - rate[K[0]])
print(f"S = c + e x ops: e = {d * 1e12:.0f} pJ an op on one minion, c = {S[0] - d * rate[K[0]]:.3f} W")
print("\n# is the gap a property of the formats, not of one session? S, W over idle, each committed session with both zeros")
seen = []
for j in sorted(glob.glob(os.path.join(DD, "2026-1*-e*/e*.json"))):
    if not os.path.basename(j)[:-5].replace("e", "").isdigit():
        continue
    it = load(j).get("items", {})
    a, b = it.get("fp32.zeros"), it.get("int8.zeros")
    if a and b and isinstance(a.get("S"), dict) and isinstance(b.get("S"), dict) and a["S"].get("mean") is not None and b["S"].get("mean") is not None:
        print(f"  {os.path.basename(j):14s} fp32 {a['S']['mean']:.3f}  int8 {b['S']['mean']:.3f}  diff {b['S']['mean'] - a['S']['mean']:+.3f}  ratio {b['S']['mean'] / a['S']['mean']:.3f}")
print("\n# which clocks stay on with every slot gated: rising edges in one op, a lane or a unit (vcd_clocks.py). fp32's op is 559 cycles in this window, int8's 331")
a, b = load(os.path.join(HERE, "clocks-fp32.json")), load(os.path.join(HERE, "clocks-int8.json"))
for s in ("lane.clock_txfma", "lane.txfma_trans_top.txfma.txfmafrac0_top.opa_frf_clk", "lane.txfma_trans_top.txfma.txfmafrac0_top.opb_frf_clk", "lane.txfma_trans_top.txfma.txfmafrac0_top.opc_frf_clk", "lane.txfma_trans_top.txfma.txfmafrac0_top.ctrl_frf_clk",
          "lane.LANE_TIMA.lane_tima.tima_clock", "lane.LANE_TIMA.lane_tima.f2_tima_in3_en", "lane.clock_bypass", "lane.rf.vpu_64x32_3r2w_vpurf.rd_enable0", "lane.rf.vpu_64x32_3r2w_vpurf.rd_enable1", "lane.rf.vpu_64x32_3r2w_vpurf.rd_enable2", "lane.rf.vpu_64x32_3r2w_vpurf.wr_enable0", "lane.rf.vpu_64x32_3r2w_vpurf.wr_enable1"):
    print(f"  {s:70s} fp32 {a[s]['rises_mean']:6.1f}  int8 {b[s]['rises_mean']:6.1f}  ({a[s]['instances']} instances)")
print("\n# register bits by block, per op (acct-*.txt): clocked with enable high / seeing a clock edge")
for t in ("fp32", "int8"):
    print(" ", t)
    r = []
    for l in open(os.path.join(HERE, f"acct-{t}.txt")):
        x, y, z, n = l.split(None, 3)
        r.append((int(z) / 2, int(x) / 2, n.strip()))
    for z, x, n in sorted(r, reverse=True)[:9]:
        print(f"    {x:10.0f} / {z:10.0f}  {n}")
print("\n# (2) Q130(i)'s reading")
print("  its simulation, its own run.sh, with and without -fno-dfg: see q130i-rerun.txt: identical to each other and to its committed counts.txt")
r0 = load(os.path.join(DD, "2026-10-26-toggle-recount/recount.json"))["zeros"]["mean"]
r1 = load(os.path.join(B, "old-benches/recount-nodfg.json"))["zeros"]["mean"]
print("  the recount's bench on zeros, faulty against flag:", {k: (round(r0[k]), round(r1[k])) for k in ("nets", "clock_nets", "ff_clocked", "ff_toggles", "bus", "nets_hier")})
pm = lambda x: x / rate[K[0]] / 4096 * 1e12
print(f"  the whole VPU on fp32 zeros at M4's constants, an extrapolation: nets {pm(pf[1]):.3f} pJ a multiply-add, clocked bits {pm(pf[0]):.3f} pJ, together {pm(sum(pf)):.3f} pJ; S on E78's card {pm(S[0]):.3f} pJ")
print("  per multiply-add on fp32 zeros: merged nets %.1f, bus nets %.2f, register bits clocked %.1f, seeing an edge %.1f, changing %.2f" % (m[K[0]]["vpu"]["nets_map"] / 4096, m[K[0]]["vpu"]["by_stage"]["lane_operand_bus"] / 4096, m[K[0]]["ff"]["all"]["clocked"] / 4096, m[K[0]]["ff"]["all"]["present"] / 4096, m[K[0]]["ff"]["all"]["toggles"] / 4096))
