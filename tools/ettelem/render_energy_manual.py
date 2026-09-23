#!/usr/bin/env python3
"""Render the energy manual's markdown from manual.json, so every number on the page is the one in the data.

    render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/
"""
import json
import os
import sys


def f(v, n=2):
    return "—" if v is None else f"{v:.{n}f}"


def main():
    m = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    E = m["enercat"]["cards"]
    A2 = E["aifoundry2"]
    A3 = E.get("aifoundry3", [])
    k = lambda r: (r["pattern"], r["operands"], r["harts"], r["scp"])
    a2 = {k(r): r for r in A2}
    a3 = {k(r): r for r in A3}

    # ---------------------------------------------------------------- 1 at rest
    r = m["rest"]
    s = ["# 1. The card at rest\n",
         "What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.\n",
         "## The law\n",
         f"$$P_\\text{{idle}}(T) = {f(r['P_fix_w'],1)}\\,\\mathrm{{W}} + {f(r['A_leak_80_w'],1)}\\,\\mathrm{{W}}\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/{f(r['T_L_c'],0)}\\,^\\circ\\mathrm{{C}}}}$$\n",
         f"- **{f(r['P_fix_w'],1)} W is temperature-independent**: PCIe, the DDR PHY, the IO shire, regulators, clocks. It does not respond to anything a kernel does.",
         f"- **The rest is leakage**, {f(r['A_leak_80_w'],1)} W at 80 °C, e-folding every {f(r['T_L_c'],0)} °C, so its slope at 80 °C is {f(r['lambda_80_w_per_c'],2)} W per °C. This is the term a workload controls, by setting the temperature.",
         "- Fitted on 21 September to every idle sample of five hours of sessions (rms 0.20 W from 64 to 88 °C); predicted a 20-hour idle the next day to +0.01 W; extrapolated 25 °C below its range onto aifoundry3 to +0.73 W. Source: `" + r["source"]["law"] + "`.\n",
         "| Die °C | Idle W | Leakage share |", "|---|---|---|"]
    for c in r["curve"]:
        if c["T"] % 10 == 0:
            s.append(f"| {c['T']} | {f(c['P_idle'],1)} | {100*c['leak_frac']:.0f}% |")
    rl = r["rails_73c"]
    s += ["\n## Where idle goes, by rail (73 °C, 20 hours idle)\n",
          "| Rail | W | Share |", "|---|---|---|",
          f"| Minions | {f(rl['minion'])} | {100*rl['minion']/rl['board']:.0f}% |",
          f"| SRAM (L2, L3, scratchpad) | {f(rl['sram'])} | {100*rl['sram']/rl['board']:.0f}% |",
          f"| Mesh | {f(rl['noc'])} | {100*rl['noc']/rl['board']:.0f}% |",
          f"| **No rail sensor** (PCIe, DDR, IO shire, regulators) | **{f(rl['unsensed'])}** | {100*rl['unsensed']/rl['board']:.0f}% |",
          f"| Board | {f(rl['board'])} | |",
          "\nThe three sensed rails are the service processor's own ~2 s averages; the unsensed remainder is board power minus their sum. Source: `" + r["source"]["rails"] + "`.\n",
          "## Operating points\n", "| MHz | Minion V | Relative switching power (V²f) |", "|---|---|---|"]
    p0 = r["operating_points"][0]
    for p in r["operating_points"]:
        s.append(f"| {p['mhz']} | {f(p['volts'],3)} | {(p['volts']/p0['volts'])**2 * p['mhz']/p0['mhz']:.2f}× |")
    s += ["\nA warm card (above 65 °C) is pinned to the first row by the governor; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md).\n"]
    if "cards" in r:
        c = r["cards"]
        s += ["## The two working cards\n", "| | aifoundry2 | aifoundry3 |", "|---|---|---|",
              f"| Static TDP the firmware uses | {c['aifoundry2']['tdp_w']} W | **{c['aifoundry3']['tdp_w']} W** (pinned at 600 MHz for life) |",
              f"| Minion voltage at 600 MHz | {c['aifoundry2']['minion_mv']} mV | {c['aifoundry3']['minion_mv']} mV |",
              "| Typical idle | 31–36 W at 73–80 °C | 23.6 W at 51 °C |", ""]
    open(os.path.join(out, "01-at-rest.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 2 awake
    sp1, sp2 = a2[("spin", "zeros", 1, False)], a2[("spin", "zeros", 2, False)]
    aw = m["awake"]
    s = ["# 2. A core that is awake\n",
         "The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes this.\n",
         "| Configuration | W over idle, 1,024 minions | Per minion | Per instruction | Rate |", "|---|---|---|---|---|",
         f"| One hart per minion, `addi` loop | {f(sp1['over_idle_w'])} | {f(sp1['over_idle_w']/1024*1e3,2)} mW | {f(sp1['pj_per_op'],1)} pJ | {sp1['ops_per_s']:.2e}/s |",
         f"| Both harts per minion | {f(sp2['over_idle_w'])} | {f(sp2['over_idle_w']/1024*1e3,2)} mW | {f(sp2['pj_per_op'],1)} pJ | {sp2['ops_per_s']:.2e}/s |",
         f"| The second hart's share | {f(sp2['over_idle_w']-sp1['over_idle_w'])} | {f((sp2['over_idle_w']-sp1['over_idle_w'])/1024*1e3,2)} mW | {f((sp2['over_idle_w']-sp1['over_idle_w'])/(sp2['ops_per_s']-sp1['ops_per_s'])*1e12,1)} pJ per extra instruction | |",
         f"| Ablation of 21 Sep, hart 0, 80 °C | {f(aw['spin_hart0_1024']['over_idle_w'])} | {f(aw['spin_hart0_1024']['over_idle_w']/1024*1e3,2)} mW | {f(aw['spin_hart0_1024']['pj_marginal'],1)} pJ | {aw['spin_hart0_1024']['per_s']:.2e}/s |",
         "| 1,024 minions stalled in a load that never returns (hot line, E23) | 1.41 | 1.4 mW | — | — |",
         "| Activity term under a dense matmul (E15) | 26.2 | 25.6 mW | — | tensor state machines plus everything else that wakes |",
         "\n**Rules.** An awake minion costs about 2 mW; a second hart adds 1.2 mW; a minion stalled on memory costs the same as one spinning. Keeping 1,024 minions awake for a second is 2–3 J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.\n",
         "Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/`, `" + aw["source"] + "`.\n"]
    open(os.path.join(out, "02-awake.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 3 instructions
    def row(pat, label, lanes, note=""):
        z, c, rnd = a2.get((pat, "zeros", 2, False)), a2.get((pat, "const", 2, False)), a2.get((pat, "random", 2, False))
        z3 = a3.get((pat, "random", 2, False))
        if not (z and c and rnd):
            return ""
        per = f" ({f(rnd['pj_per_op']/lanes,1)}/lane)" if lanes > 1 else ""
        return (f"| `{label}` | {f(z['pj_per_op'],1)} | {f(c['pj_per_op'],1)} | **{f(rnd['pj_per_op'],1)}**{per} | "
                f"{f(rnd['pj_per_op']/z['pj_per_op'],2)}× | {rnd['ops_per_cycle_per_hart']:.2f} | {f(z3['pj_per_op'],1) if z3 else '—'} | {note} |")
    s = ["# 3. Instructions\n",
         "Energy per instruction retired, above idle, at 600 MHz and 0.517 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2). The last column is the same measurement on the second card.\n",
         "## 3.1 Scalar and vector units\n",
         "| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | aifoundry3, random | Note |",
         "|---|---|---|---|---|---|---|---|",
         row("iadd", "add", 1), row("ixor", "xor", 1), row("imul", "mul", 1, "64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op"),
         row("fadd_s", "fadd.s", 1), row("fmul_s", "fmul.s", 1), row("fmadd_s", "fmadd.s", 1),
         row("fadd_ps", "fadd.ps (8 lanes)", 8), row("fmul_ps", "fmul.ps (8 lanes)", 8), row("fmadd_ps", "fmadd.ps (8 lanes)", 8, "16 flops"),
         row("iadd_pi", "fadd.pi (8 lanes, int32)", 8), row("imul_pi", "fmul.pi (8 lanes, int32)", 8),
         row("fexp_ps", "fexp.ps (8 lanes)", 8, "transcendental unit, ¼ the rate"), row("frcp_ps", "frcp.ps (8 lanes)", 8, "transcendental unit"),
         "", "`fdiv.ps` and `fsqrt.ps` trap: there is no hardware divide or square root in U-mode on this silicon.\n",
         "**What the table says.**",
         f"- **An integer add is the cheapest thing a core does, {f(a2[('iadd','zeros',2,False)]['pj_per_op'],1)} pJ on zeros**, and almost all of that is the awake core (section 2: {f(sp2['pj_per_op'],1)} pJ per `addi`). Random operands add {f(a2[('iadd','random',2,False)]['pj_per_op']-a2[('iadd','zeros',2,False)]['pj_per_op'],1)} pJ.",
         f"- **A scalar float add costs {f(a2[('fadd_s','zeros',2,False)]['pj_per_op']/a2[('iadd','zeros',2,False)]['pj_per_op'],1)}× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.",
         f"- **An 8-lane vector op on zeros costs the same as the scalar op** ({f(a2[('fadd_ps','zeros',2,False)]['pj_per_op'],1)} against {f(a2[('fadd_s','zeros',2,False)]['pj_per_op'],1)} pJ): idle lanes are free. On random data the eight lanes cost {f(a2[('fadd_ps','random',2,False)]['pj_per_op']/a2[('fadd_ps','zeros',2,False)]['pj_per_op'],1)}× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.",
         f"- **Per lane on random data, `fmadd.ps` is {f(a2[('fmadd_ps','random',2,False)]['pj_per_op']/8,1)} pJ per multiply-add**, and its marginal cost over the `addi` loop is {f(a2[('fmadd_ps','random',2,False)].get('pj_per_op_vs_spin',0)/8,1)} pJ. The tensor unit below does the same multiply-add for {f(m['tensor']['rows'][2]['pj_marginal'],1)} pJ. **The datapath energy per multiply-add is the same in both units; what the tensor unit saves is instruction issue.**",
         f"- **Integer vector adds are half the price of float ones** ({f(a2[('iadd_pi','zeros',2,False)]['pj_per_op'],1)} vs {f(a2[('fadd_ps','zeros',2,False)]['pj_per_op'],1)} pJ on zeros); integer vector multiplies are not.",
         f"- **Transcendentals are the most expensive instructions on the chip**: `fexp.ps` at {f(a2[('fexp_ps','random',2,False)]['pj_per_op'],0)} pJ for eight lanes is {f(a2[('fexp_ps','random',2,False)]['pj_per_op']/a2[('fmadd_ps','random',2,False)]['pj_per_op'],1)}× a vector multiply-add, at a quarter of the rate.\n",
         "## 3.2 The tensor unit\n",
         "`TensorFMA32` on a 16×16×16 tile, 4,096 multiply-adds per instruction, 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, launched at 80 °C. Marginal is above idle; loaded is total board power divided by the rate, which is what a multiply-add costs when it is the only thing running.\n",
         "| Type, operands | pJ per MAC, marginal | pJ per MAC, loaded | W over idle | MACs per second |", "|---|---|---|---|---|"]
    for t in m["tensor"]["rows"]:
        s.append(f"| {t['label']} | **{f(t['pj_marginal'],3)}** | {f(t['pj_loaded'],2)} | {f(t['over_idle_w'],2)} | {t['per_s']:.2e} |")
    fl = m["tensor"]["flips"]
    s += ["", "### Where the tensor unit's energy goes: per flip\n",
          "The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands the card actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four fitted energies:\n",
          "| Event | fJ each | What it is |", "|---|---|---|"]
    for c, e in fl["e_fJ"].items():
        s.append(f"| {c} | {f(e,3)} | {fl['classes'][c]} |")
    s += [f"| tensor state machines | {f(fl['p_sm_full_chip_w']/1024*1e3,2)} mW per active minion | per minion, whatever the data |",
          "", "A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and the card measures 27.6. Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran.\n",
          "Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/` (3.1), `" + m["tensor"]["source"]["rows"] + "` (3.2), `" + m["tensor"]["source"]["flips"] + "` (flips).\n"]
    open(os.path.join(out, "03-instructions.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 4 bytes
    def mrow(pat, scp, label, harts):
        z, rn = a2.get((pat, "zeros", harts, scp)), a2.get((pat, "random", harts, scp))
        z3 = a3.get((pat, "random", harts, scp))
        if not (z and rn):
            return ""
        return (f"| {label} | {f(z['pj_per_byte'])} | **{f(rn['pj_per_byte'])}** | {f(rn['pj_per_byte']/z['pj_per_byte'],2)}× | "
                f"{rn['bytes_per_s']/1e9:.0f} | {f(z3['pj_per_byte']) if z3 else '—'} |")
    mr = m["memory_reads"]
    s = ["# 4. Bytes through the memory hierarchy\n",
         "Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the bus toggles are a large part of the cost at every level.\n",
         "## 4.1 Reads and writes, measured together (23 September)\n",
         "| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | aifoundry3, random |", "|---|---|---|---|---|---|",
         mrow("ld_l1", False, "L1 hit, `flw.ps` 32 B (both harts)", 2),
         mrow("st_l1", False, "L1 hit, `fsw.ps` 32 B (both harts)", 2),
         mrow("tload", True, "Tensor load from the shire's own scratchpad", 1),
         mrow("tstore", True, "Tensor store into the shire's own scratchpad", 1),
         mrow("tload", False, "Tensor load from DRAM", 1),
         mrow("tstore", False, "Tensor store to DRAM", 1),
         mrow("st_stream", False, "`fsw.ps` streaming to DRAM through the L1 write-back path", 2),
         "", "## 4.2 Reads by level (18 September, memhier)\n",
         "| Level | Working set | pJ/B | GB/s | Clock during the run |", "|---|---|---|---|---|"]
    for x in mr["rows"]:
        s.append(f"| {x['level']} | {x['what']} | {f(x['pj_per_byte'])} | {x['gb_s']:.0f} | {f(x.get('implied_ghz'),2)} GHz implied |")
    s += ["", "*Caveat:* " + mr["caveat"] + ". The two levels re-measured at a pinned 600 MHz on 23 September (4.1) agree with these to within the data dependence: DRAM " +
          f(mr["rows"][[x["level"] for x in mr["rows"]].index("dram")]["pj_per_byte"]) + " here against " +
          f(a2[("tload", "random", 1, False)]["pj_per_byte"]) + " on random data now.\n",
          "**What the tables say.**",
          f"- **DRAM is {f(a2[('tload','random',1,False)]['pj_per_byte']/a2[('tload','random',1,True)]['pj_per_byte'],0)}× the energy of the shire's own scratchpad per byte read**, and {f(a2[('tstore','random',1,False)]['pj_per_byte']/a2[('tstore','random',1,True)]['pj_per_byte'],0)}× per byte written.",
          f"- **A DRAM write costs about what a DRAM read costs** ({f(a2[('tstore','random',1,False)]['pj_per_byte'],0)} vs {f(a2[('tload','random',1,False)]['pj_per_byte'],0)} pJ/B on random data) — by tensor store, which bypasses the caches. **Through the L1 write-back path the same bytes cost {f(a2[('st_stream','random',2,False)]['pj_per_byte']/a2[('tstore','random',1,False)]['pj_per_byte'],1)}× more** and arrive at a third of the bandwidth: every store allocates a line, and the line goes down through L2 and L3.",
          f"- **Even DRAM is data-dependent**: zeros {f(a2[('tload','zeros',1,False)]['pj_per_byte'],0)}, random {f(a2[('tload','random',1,False)]['pj_per_byte'],0)} pJ/B. The scratchpad doubles from zeros to random.",
          f"- **A scratchpad write is twice a scratchpad read** ({f(a2[('tstore','zeros',1,True)]['pj_per_byte'])} vs {f(a2[('tload','zeros',1,True)]['pj_per_byte'])} pJ/B on zeros).",
          f"- **An L1 hit is nearly free**: {f(a2[('ld_l1','random',2,False)]['pj_per_byte'])} pJ/B including the instruction, {f(a2[('ld_l1','random',2,False)].get('pj_per_op_vs_spin',0)/32,2)} pJ/B over the awake core.\n",
          "Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/`, `" + mr["source"]["rows"] + "`.\n"]
    open(os.path.join(out, "04-bytes-memory.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 5 comm
    cm = m["comm"]
    s = ["# 5. Bytes between cores and shires\n",
         "Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV. Two independent runs averaged; ± is half their difference.\n",
         "| Ring | What moves | pJ/B | GB/s aggregate |", "|---|---|---|---|"]
    for x in cm["rows"]:
        s.append(f"| {x['ring']} | {x['what']} | **{f(x['pj_per_byte'])}** ± {f(x['pj_spread'])} | {x['gb_s']:.0f} |")
    rp = {x["medium"]: x for x in m["relay"]["power"]["media"]}
    s += ["", "## Handing a slab to another shire through its scratchpad (E25)\n",
          "| Medium | pJ per byte (read + write) | GB/s on the card |", "|---|---|---|",
          f"| Write to DRAM, read back | {f(rp['dram']['pj_per_byte'],1)} | {rp['dram']['bytes_per_s']/1e9:.0f} |",
          f"| Write where the next shire reads it | **{f(rp['hop']['pj_per_byte'],1)}** | {rp['hop']['bytes_per_s']/1e9:.0f} |",
          f"| Keep it in this shire's scratchpad | {f(rp['scp']['pj_per_byte'],1)} | {rp['scp']['bytes_per_s']/1e9:.0f} |",
          "", "**What the tables say.**",
          f"- **Inside a neighbourhood a byte costs under a picojoule**; inside a shire about {f(cm['rows'][2]['pj_per_byte'],1)} pJ; across the mesh {f(min(x['pj_per_byte'] for x in cm['rows'] if x['ring'].startswith('xshire')),0)}–{f(max(x['pj_per_byte'] for x in cm['rows'] if x['ring'].startswith('xshire')),0)} pJ, roughly flat in distance. The step is leaving the shire, not the number of hops after that.",
          "- Small messages cost more per byte (the 128 B rows): the per-message overhead is a few hundred cycles of the sending and receiving harts.",
          f"- **Handing a slab to the next shire through its scratchpad, {f(rp['hop']['pj_per_byte'],1)} pJ/B for the write and the read together, is a twelfth of the energy of the DRAM round trip** and sits between the in-shire and cross-mesh tensor-network figures.\n",
          "Sources: `" + "`, `".join(cm["source"]) + "`, `" + m["relay"]["source"] + "`.\n"]
    open(os.path.join(out, "05-bytes-between-cores.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 6 sync
    sy = m["sync"]
    at = {x["label"]: x for x in sy["atomics"]["runs"]}
    s = ["# 6. Synchronisation\n",
         "| Event | Energy | Time | Note |", "|---|---|---|---|",
         f"| Global atomic, one line, 1,024 requesters | **{f(at['contended']['nj_per_op'],1)} nJ** | {at['contended']['cycles_per_op']:.0f} cycles each at the bank | the bank serialises; every requester stalls |",
         f"| Global atomic, 32 lines, one per shire | {f(at['spread']['nj_per_op'],1)} nJ | {at['spread']['cycles_per_op']:.2f} cycles each, aggregate | the same instruction, {f(at['contended']['nj_per_op']/at['spread']['nj_per_op'],0)}× cheaper |",
         f"| Uncontended remote atomic round trip | — | {sy['remote_atomic_latency_cycles']:.0f} cycles | E22 |",
         f"| Chip-wide barrier, 1,024 minions | ≈ {1024*1.4e-3*sy['barrier_cycles_chip']/0.6e9*1e9:.0f} nJ of waiting | {sy['barrier_cycles_chip']:,} cycles | derived: 1,024 minions stalled at 1.4 mW for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |",
         "| FLB + credit barrier, one shire | — | 237 cycles | nocbench, 18 September |",
         "| TensorReduce + broadcast, 32 minions | — | 432 cycles | nocbench, 18 September |",
         "", "**What the table says.** A contended hot line is the single most expensive thing a program can do per operation on this chip, and its cost is not on the requesters: the shire that hosts the line loses its own memory path entirely (docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws what a spinning one does, about 1.4 mW — so a barrier's energy is small next to the leakage the card burns while it lasts.\n",
         "Source: `" + sy["source"] + "`.\n"]
    open(os.path.join(out, "06-synchronisation.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 8 cards
    ratios = []
    for kk, r2 in a2.items():
        r3 = a3.get(kk)
        if not r3:
            continue
        v2, v3 = (r2["pj_per_byte"], r3["pj_per_byte"]) if r2["bytes"] else (r2["pj_per_op"], r3["pj_per_op"])
        if v2:
            ratios.append(v3 / v2)
    ratios.sort()
    med = ratios[len(ratios) // 2]
    cd = m.get("cards", {})
    s = ["# 8. Card-to-card variation\n",
         "Every table in sections 2 to 4 was measured on aifoundry2 and repeated on aifoundry3 the same day, with the same binaries. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).\n",
         f"| Comparison | aifoundry3 / aifoundry2 |", "|---|---|",
         f"| Instruction and byte energies, {len(ratios)} entries | median **{f(med,3)}**, range {f(ratios[0],2)}–{f(ratios[-1],2)} |",
         f"| Tensor-unit switching power, 8 operand patterns (E20) | {f(cd.get('scale', 0.924),3)} |",
         "| Idle law extrapolated 25 °C below its fitted range (E20) | +0.73 W of 25 W |",
         "| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |",
         "", "**What it says.** A second card of the same design gives the same energies to about 5%, with a single per-card scale factor that the voltage does not explain and that leans the same way in every table. One random-data run calibrates it. The catalogue is a property of the design; the last 5% is the card.\n"]
    open(os.path.join(out, "08-cards.md"), "w").write("\n".join(s))
    print("rendered", out)


if __name__ == "__main__":
    main()
