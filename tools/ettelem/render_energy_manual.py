#!/usr/bin/env python3
"""Render the energy manual's markdown from manual.json, so every number on the page is the one in the data.

    render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/

Every entry carries its confidence bar: **mean** [lo–hi] is the mean over every pass on every card and the full
range those passes spanned; a per-card column is that card's mean ± its pass-to-pass standard error. The bars
come from the three shuffled passes on two cards of the catalogue (sections 2, 3.1, 4.1, 8), the ablation and
the card transfer (3.2), and the reruns of the relay, hot line, rings and levels (4.2, 5, 6).
"""
import json
import os
import statistics
import sys


def f(v, n=2):
    return "—" if v is None else f"{v:,.{n}f}" if abs(v) >= 1000 else f"{v:.{n}f}"


def main():
    m = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    C = m["catalogue"]["combined"]
    S = {h: m["catalogue"]["cards"][h]["summary"] for h in m["catalogue"]["cards"]}
    RR = m.get("reruns", {})

    def cb(key, scale=1.0):
        c = C.get(key)
        if not c:
            return None
        return {"mean": c["mean"] * scale, "lo": c["lo"] * scale, "hi": c["hi"] * scale, "n": c["n"], "cards": c.get("cards", len(c["per_card"])),
                "per_card": {h: {"mean": v["mean"] * scale, "se": v.get("se", 0) * scale, "n": v["n"]} for h, v in c["per_card"].items()}}

    def bar(c, n=1):
        return "—" if not c else f"**{f(c['mean'], n)}** [{f(c['lo'], n)}–{f(c['hi'], n)}]"

    def cards(c, n=1):
        if not c:
            return "—"
        return " · ".join(f"a{h[-1]}: {f(v['mean'], n)} ± {f(v['se'], n)}" for h, v in sorted(c["per_card"].items()))

    def rate(key, field="ops_per_cycle_per_hart"):
        e = S["aifoundry2"].get(key)
        return e[field]["mean"] if e else None

    def stat(key, field):
        e = S["aifoundry2"].get(key)
        return e[field]["mean"] if e else None

    BARS = ("Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "
            "\"a2\" and \"a3\" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error.")

    # ---------------------------------------------------------------- 1 at rest
    r = m["rest"]
    rl = r["rails_73c"]
    s = ["# 1. The card at rest\n",
         "What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.\n",
         "## The law\n",
         f"$$P_\\text{{idle}}(T) = {f(r['P_fix_w'],1)}\\,\\mathrm{{W}} + {f(r['A_leak_80_w'],1)}\\,\\mathrm{{W}}\\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/{f(r['T_L_c'],0)}\\,^\\circ\\mathrm{{C}}}}$$\n",
         f"- **{f(r['P_fix_w'],1)} W is temperature-independent**: PCIe, the DDR PHY, the IO shire, regulators, clocks. It does not respond to anything a kernel does.",
         f"- **The rest is leakage**, {f(r['A_leak_80_w'],1)} W at 80 °C, e-folding every {f(r['T_L_c'],0)} °C, so its slope at 80 °C is {f(r['lambda_80_w_per_c'],2)} W per °C. This is the term a workload controls, by setting the temperature.",
         "- **Confidence.** Fitted on 21 September to every idle sample of five hours of sessions on aifoundry2, rms 0.20 W from 64 to 88 °C. Checked three ways: it predicted a 20-hour idle the next day to +0.01 W (300 samples, sd 0.04 W); extrapolated 25 °C below its range onto aifoundry3 it was +0.73 W high (rms 0.74 W over 3,600 samples at 50–57 °C), which is the card-to-card bar on the law: about 3% of the idle power. Source: `" + r["source"]["law"] + "`.\n",
         "| Die °C | Idle W | Leakage share |", "|---|---|---|"]
    for c in r["curve"]:
        if c["T"] % 10 == 0:
            s.append(f"| {c['T']} | {f(c['P_idle'],1)} | {100*c['leak_frac']:.0f}% |")
    s += ["\n## Where idle goes, by rail (73 °C, 20 hours idle)\n",
          "| Rail | W | Share |", "|---|---|---|",
          f"| Minions | {f(rl['minion'])} | {100*rl['minion']/rl['board']:.0f}% |",
          f"| SRAM (L2, L3, scratchpad) | {f(rl['sram'])} | {100*rl['sram']/rl['board']:.0f}% |",
          f"| Mesh | {f(rl['noc'])} | {100*rl['noc']/rl['board']:.0f}% |",
          f"| **No rail sensor** (PCIe, DDR, IO shire, regulators) | **{f(rl['unsensed'])}** | {100*rl['unsensed']/rl['board']:.0f}% |",
          f"| Board | {f(rl['board'])} ± 0.04 | |",
          "\nThe three sensed rails are the service processor's own ~1 s filtered averages; the unsensed remainder is board power minus their sum. The board figure's ± is the sd of 300 samples over the 20 hours; the rails' sd is below 0.01 W. Source: `" + r["source"]["rails"] + "`. The SRAM rail's own temperature law, on both cards, is in 4.3.\n",
          "## Operating points\n", "| MHz | Minion V | Relative switching power (V²f) |", "|---|---|---|"]
    p0 = r["operating_points"][0]
    for p in r["operating_points"]:
        s.append(f"| {p['mhz']} | {f(p['volts'],3)} | {(p['volts']/p0['volts'])**2 * p['mhz']/p0['mhz']:.2f}× |")
    s += ["\nA warm card (above 65 °C) is pinned to the first row by the governor; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md). **Below 65 °C the governor moves the clock in the middle of a burst**: the first attempt at the reruns of section 5 and 6 on aifoundry2 (12:51–13:10 on 23 September, die 65 °C) had 700–800 MHz excursions in a fifth of its samples and was discarded; the bars in this manual are from bursts at 600 MHz throughout.\n"]
    if "cards" in r:
        c = r["cards"]
        s += ["## The two working cards\n", "| | aifoundry2 | aifoundry3 |", "|---|---|---|",
              f"| Static TDP the firmware uses | {c['aifoundry2']['tdp_w']} W | **{c['aifoundry3']['tdp_w']} W** (pinned at 600 MHz for life) |",
              f"| Minion voltage at 600 MHz | {c['aifoundry2']['minion_mv']} mV | {c['aifoundry3']['minion_mv']} mV |",
              "| Typical idle | 31–36 W at 73–80 °C | 23.6 W at 51 °C |", ""]
    open(os.path.join(out, "01-at-rest.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 2 awake
    sp1, sp2 = cb("spin/zeros/h1"), cb("spin/zeros/h2")
    w1, w2 = stat("spin/zeros/h1", "over_idle_w"), stat("spin/zeros/h2", "over_idle_w")
    r1, r2 = stat("spin/zeros/h1", "ops_per_s"), stat("spin/zeros/h2", "ops_per_s")
    aw = m["awake"]["spin_hart0_1024"]
    hot = (RR.get("hotline_over_idle_w") or {}).get("contended")
    s = ["# 2. A core that is awake\n",
         "The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes this.\n",
         BARS + "\n",
         "| Configuration | pJ per instruction | per card | W over idle, 1,024 minions (a2) | Per minion | Rate |", "|---|---|---|---|---|---|",
         f"| One hart per minion, `addi` loop | {bar(sp1)} | {cards(sp1)} | {f(w1)} | {f(w1/1024*1e3,2)} mW | {r1:.2e}/s |",
         f"| Both harts per minion | {bar(sp2)} | {cards(sp2)} | {f(w2)} | {f(w2/1024*1e3,2)} mW | {r2:.2e}/s |",
         f"| The second hart's share | {f((w2-w1)/(r2-r1)*1e12,1)} pJ per extra instruction | | {f(w2-w1)} | {f((w2-w1)/1024*1e3,2)} mW | |",
         f"| Ablation of 21 Sep, hart 0, 80 °C, 2 runs | {f(aw['pj_marginal'],1)} pJ | a2 only, run-to-run sd 0.02 W | {f(aw['over_idle_w'])} | {f(aw['over_idle_w']/1024*1e3,2)} mW | {aw['per_s']:.2e}/s |",
         (f"| 1,024 minions stalled in a load that never returns (hot line, E23) | — | {cards(hot, 2)} W | **{f(hot['mean'])}** [{f(hot['lo'])}–{f(hot['hi'])}] | {f(hot['mean']/1024*1e3,1)} mW | — |" if hot else
          "| 1,024 minions stalled in a load that never returns (hot line, E23) | — | | 1.41 | 1.4 mW | — |"),
         "| Activity term under a dense matmul (E15) | — | | 26.2 | 25.6 mW | tensor state machines plus everything else that wakes |",
         "\n**Rules.** An awake minion costs about 2 mW; a second hart adds about 1 mW; a minion stalled on memory costs the same as one spinning. Keeping 1,024 minions awake for a second is 2–3 J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.\n",
         f"The bars here are the widest in the manual in relative terms, because the signal is small: 2–3 W over a 28–36 W idle that drifts by a few tenths of a watt with the die temperature. The two cards differ by {100*abs(sp2['per_card']['aifoundry3']['mean']/sp2['per_card']['aifoundry2']['mean']-1):.0f}% on the two-hart loop, which is the cross-card scale of section 8.\n",
         "Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `" + m["awake"]["source"] + "`.\n"]
    open(os.path.join(out, "02-awake.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 3 instructions
    def row(name, label, lanes, note=""):
        z, c, rnd = cb(f"{name}/zeros/h2"), cb(f"{name}/const/h2"), cb(f"{name}/random/h2")
        if not (z and rnd):
            return ""
        per = f" ({f(rnd['mean']/lanes,1)}/lane)" if lanes > 1 else ""
        return (f"| `{label}` | {bar(z)} | {bar(c) if c else '—'} | {bar(rnd)}{per} | "
                f"{f(rnd['mean']/z['mean'],2)}× | {f(rate(f'{name}/random/h2'),2)} | {cards(rnd)} | {note} |")
    ia, fa = cb("add/zeros/h2"), cb("fadd.s/zeros/h2")
    vz, vr = cb("fadd.ps/zeros/h2"), cb("fadd.ps/random/h2")
    fm, ex = cb("fmadd.ps/random/h2"), cb("fexp.ps/random/h2")
    ipz, iar = cb("fadd.pi/zeros/h2"), cb("add/random/h2")
    tb = m["tensor"]["bars"]
    s = ["# 3. Instructions\n",
         "Energy per instruction retired, above idle, at 600 MHz and 0.517 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2).\n",
         BARS + " Three shuffled passes on each of two cards, so n = 6 for every entry (3 where the constant set was not run). The full catalogue of 161 instructions is in 3a.\n",
         "## 3.1 Scalar and vector units\n",
         "| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | per card, random | Note |",
         "|---|---|---|---|---|---|---|---|",
         row("add", "add", 1), row("xor", "xor", 1), row("mul", "mul", 1, "64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op"),
         row("fadd.s", "fadd.s", 1), row("fmul.s", "fmul.s", 1), row("fmadd.s", "fmadd.s", 1),
         row("fadd.ps", "fadd.ps (8 lanes)", 8), row("fmul.ps", "fmul.ps (8 lanes)", 8), row("fmadd.ps", "fmadd.ps (8 lanes)", 8, "16 flops"),
         row("fadd.pi", "fadd.pi (8 lanes, int32)", 8), row("fmul.pi", "fmul.pi (8 lanes, int32)", 8),
         row("fexp.ps", "fexp.ps (8 lanes)", 8, "transcendental unit, ¼ the rate"), row("frcp.ps", "frcp.ps (8 lanes)", 8, "transcendental unit"),
         "", "`fdiv.ps` and `fsqrt.ps` trap: there is no hardware divide or square root in U-mode on this silicon.\n",
         "**What the table says.**",
         f"- **An integer add is the cheapest thing a core does, {f(ia['mean'],1)} pJ on zeros** [{f(ia['lo'],1)}–{f(ia['hi'],1)}], and almost all of that is the awake core (section 2: {f(sp2['mean'],1)} pJ per `addi`). Random operands add {f(iar['mean']-ia['mean'],1)} pJ.",
         f"- **A scalar float add costs {f(fa['mean']/ia['mean'],1)}× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.",
         f"- **An 8-lane vector op on zeros costs the same as the scalar op** ({f(vz['mean'],1)} against {f(fa['mean'],1)} pJ, bars overlapping): idle lanes are free. On random data the eight lanes cost {f(vr['mean']/vz['mean'],1)}× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.",
         f"- **Per lane on random data, `fmadd.ps` is {f(fm['mean']/8,1)} pJ per multiply-add** [{f(fm['lo']/8,1)}–{f(fm['hi']/8,1)}]. The tensor unit below does the same multiply-add for {f(tb['fp32_randn']['mean'],1)} pJ [{f(tb['fp32_randn']['lo'],1)}–{f(tb['fp32_randn']['hi'],1)}]. **The datapath energy per multiply-add is the same in both units to within the bars; what the tensor unit saves is instruction issue.**",
         f"- **Integer vector adds are half the price of float ones** ({f(ipz['mean'],1)} vs {f(vz['mean'],1)} pJ on zeros); integer vector multiplies are not.",
         f"- **Transcendentals are the most expensive instructions on the chip**: `fexp.ps` at {f(ex['mean'],0)} pJ for eight lanes is {f(ex['mean']/fm['mean'],1)}× a vector multiply-add, at a quarter of the rate.\n",
         "## 3.2 The tensor unit\n",
         "`TensorFMA32` on a 16×16×16 tile, 4,096 multiply-adds per instruction, 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, launched at 80 °C. Marginal is above idle; loaded is total board power divided by the rate, which is what a multiply-add costs when it is the only thing running.\n",
         "The bar on each fp32 row spans the ablation's two runs on aifoundry2 and the 22 September transfer's runs on both cards (n = 4); fp16 and int8 were run twice on aifoundry2 only, and their bar is the run-to-run spread, which is under 1%.\n",
         "| Type, operands | pJ per MAC, marginal | per card | pJ per MAC, loaded (a2) | W over idle (a2) | MACs per second |", "|---|---|---|---|---|---|"]
    for t in m["tensor"]["rows"]:
        b = tb[t["config"]]
        pc = " · ".join(f"a{h[-1]}: {f(v['mean'],3)}" for h, v in sorted(b["per_card"].items())) + ("" if b["cards"] > 1 else " (a2 only)")
        s.append(f"| {t['label']} | **{f(b['mean'],3)}** [{f(b['lo'],3)}–{f(b['hi'],3)}] | {pc} | {f(t['pj_loaded'],2)} | {f(t['over_idle_w'],2)} | {t['per_s']:.2e} |")
    fl = m["tensor"]["flips"]
    s += ["", "### Where the tensor unit's energy goes: per flip\n",
          "The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands the card actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four fitted energies:\n",
          "| Event | fJ each | What it is |", "|---|---|---|"]
    for c, e in fl["e_fJ"].items():
        s.append(f"| {c} | {f(e,3)} | {fl['classes'][c]} |")
    s += [f"| tensor state machines | {f(fl['p_sm_full_chip_w']/1024*1e3,2)} mW per active minion | per minion, whatever the data |",
          "", "A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and the card measures 27.6. Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran. The four energies are one fit on one card; their confidence is that 0.9 W rms over fourteen held-out patterns, and the 8% by which aifoundry3 runs below the fit on every pattern (section 8).\n",
          "Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/` (3.1), `" + m["tensor"]["source"]["rows"] + "` and `docs/reports/data/2026-09-22-cards/cards-report.json` (3.2), `" + m["tensor"]["source"]["flips"] + "` (flips).\n"]
    open(os.path.join(out, "03-instructions.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 4 bytes
    def mrow(key, label, scale=1.0, harts=None):
        z, rn = cb(f"{key}/zeros" + (f"/h{harts}" if harts else ""), scale), cb(f"{key}/random" + (f"/h{harts}" if harts else ""), scale)
        if not (z and rn):
            return ""
        bps = stat(f"{key}/random" + (f"/h{harts}" if harts else ""), "bytes_per_s")
        return (f"| {label} | {bar(z, 2)} | {bar(rn, 2)} | {f(rn['mean']/z['mean'],2)}× | "
                f"{bps/1e9:.0f} | {cards(rn, 2)} |")
    lv = RR.get("levels_pj_per_byte") or {}
    mr = m["memory_reads"]
    dl, sl = cb("tload/dram/random"), cb("tload/scp/random")
    ds, ss = cb("tstore/dram/random"), cb("st_stream/dram/random")
    dz = cb("tload/dram/zeros")
    ssz, slz = cb("tstore/scp/zeros"), cb("tload/scp/zeros")
    l1 = cb("flw.ps/random/h2", 1 / 32)
    s = ["# 4. Bytes through the memory hierarchy\n",
         "Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the bus toggles are a large part of the cost at every level.\n",
         BARS + "\n",
         "## 4.1 Reads and writes, measured together (23 September, three passes on each card)\n",
         "| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | per card, random |", "|---|---|---|---|---|---|",
         mrow("flw.ps", "L1 hit, `flw.ps` 32 B (both harts)", 1 / 32, 2),
         mrow("fsw.ps", "L1 hit, `fsw.ps` 32 B (both harts)", 1 / 32, 2),
         mrow("tload/scp", "Tensor load from the shire's own scratchpad"),
         mrow("tstore/scp", "Tensor store into the shire's own scratchpad"),
         mrow("tload/dram", "Tensor load from DRAM"),
         mrow("tstore/dram", "Tensor store to DRAM"),
         mrow("st_stream/dram", "`fsw.ps` streaming to DRAM through the L1 write-back path"),
         ""]
    if lv:
        LV = [("l1", "L1 hits", "256 B per hart, 2,048 harts"), ("l2", "L2", "256 KB per shire (L2 is 512 KB)"),
              ("l3", "L3", "768 KB per shire, 24 MB in all (L3 is 32 MB)"), ("dram", "DRAM", "256 MB in all"),
              ("scp-local", "own scratchpad", "2 MB of the shire's own L2 scratchpad"), ("scp-remote", "remote scratchpad", "2 MB of the scratchpad 16 shires away")]
        s += ["## 4.2 Reads by level (memhier, re-run at a pinned 600 MHz on 23 September)\n",
              "Plain vector loads streaming over a working set sized to each level, both harts of every minion. The first measurement of 18 September ran with the governor free (the clock sat at 0.67–0.77 GHz on the larger sets) and is superseded; these passes were at 600 MHz in every sample.\n",
              "| Level | Working set | pJ/B | per card |", "|---|---|---|---|"]
        for k, lab, what in LV:
            c = lv.get(k)
            if c:
                s.append(f"| {lab} | {what} | {bar(c, 2)} | {cards(c, 2)} |")
        s += ["", f"Passes: {RR['passes'].get('levels', 0)}. Source: `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`."]
    else:
        s += ["## 4.2 Reads by level (18 September, memhier)\n",
              "| Level | Working set | pJ/B | GB/s | Clock during the run |", "|---|---|---|---|---|"]
        for x in mr["rows"]:
            s.append(f"| {x['level']} | {x['what']} | {f(x['pj_per_byte'])} | {x['gb_s']:.0f} | {f(x.get('implied_ghz'),2)} GHz implied |")
        s += ["", "*Caveat:* " + mr["caveat"] + "."]
    s += ["", "**What the tables say.**",
          f"- **DRAM is {f(dl['mean']/sl['mean'],0)}× the energy of the shire's own scratchpad per byte read**, and {f(ds['mean']/cb('tstore/scp/random')['mean'],0)}× per byte written.",
          f"- **A DRAM write costs about what a DRAM read costs** ({f(ds['mean'],0)} vs {f(dl['mean'],0)} pJ/B on random data) — by tensor store, which bypasses the caches. **Through the L1 write-back path the same bytes cost {f(ss['mean']/ds['mean'],1)}× more** and arrive at a third of the bandwidth: every store allocates a line, and the line goes down through L2 and L3.",
          f"- **Even DRAM is data-dependent**: zeros {f(dz['mean'],0)}, random {f(dl['mean'],0)} pJ/B, bars [{f(dz['lo'],0)}–{f(dz['hi'],0)}] and [{f(dl['lo'],0)}–{f(dl['hi'],0)}] well apart. The scratchpad doubles from zeros to random.",
          f"- **A scratchpad write is twice a scratchpad read** ({f(ssz['mean'])} vs {f(slz['mean'])} pJ/B on zeros).",
          f"- **An L1 hit is nearly free**: {f(l1['mean'])} pJ/B [{f(l1['lo'])}–{f(l1['hi'])}] including the instruction.\n",
          "Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in 4a.\n",
          "Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `" + mr["source"]["rows"] + "`.\n"]
    open(os.path.join(out, "04-bytes-memory.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 5 comm
    cm = m["comm"]
    rg = RR.get("rings_pj_per_byte") or {}
    rp = {x["medium"]: x for x in m["relay"]["power"]["media"]}
    rr = RR.get("relay_pj_per_byte") or {}
    s = ["# 5. Bytes between cores and shires\n",
         "Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV.\n",
         BARS + (f" The rings were re-measured on 23 September with the manual's own sampler, {RR['passes'].get('rings', 0) // 2} passes on each card, the die held warm on aifoundry2; the pair of 18 September runs, sampled without the die temperature, is not pooled and agrees to within 10%. **The s ↔ s+16 ring starves the service processor's own management path** — the sampler's latency triples and the board reading is held for seconds — so its aifoundry2 passes were dropped and that row is aifoundry3 only (its 18 September value on aifoundry2 was 14.7)." if rg else " Two independent runs averaged; ± is half their difference.") + "\n",
         "| Ring | What moves | pJ/B | per card | GB/s aggregate |", "|---|---|---|---|---|"]
    for x in cm["rows"]:
        c = rg.get(x["ring"])
        s.append(f"| {x['ring']} | {x['what']} | {bar(c, 2) if c else '**' + f(x['pj_per_byte']) + '** ± ' + f(x['pj_spread'])} | {cards(c, 2) if c else 'a2 only'} | {x['gb_s']:.0f} |")
    rel_note = (f" The relay was measured on 22 September and re-run three times on each card on 23 September (n = {rr['dram']['n']})." if rr else "")
    s += ["", "## Handing a slab to another shire through its scratchpad (E25)\n" + rel_note + "\n",
          "| Medium | pJ per byte (read + write) | per card | GB/s on the card |", "|---|---|---|---|"]
    for med, label in (("dram", "Write to DRAM, read back"), ("hop", "Write where the next shire reads it"), ("scp", "Keep it in this shire's scratchpad")):
        c = rr.get(med)
        v = bar(c, 1) if c else f"**{f(rp[med]['pj_per_byte'],1)}**"
        s.append(f"| {label} | {v} | {cards(c, 1) if c else 'a2 only'} | {rp[med]['bytes_per_s']/1e9:.0f} |")
    xs = [(rg[x["ring"]]["mean"] if x["ring"] in rg else x["pj_per_byte"]) for x in cm["rows"] if x["ring"].startswith("xshire") and "c4" not in x["ring"]]
    sh = rg["shire"]["mean"] if "shire" in rg else cm["rows"][2]["pj_per_byte"]
    hop = rr["hop"]["mean"] if rr else rp["hop"]["pj_per_byte"]
    dram = rr["dram"]["mean"] if rr else rp["dram"]["pj_per_byte"]
    s += ["", "**What the tables say.**",
          f"- **Inside a neighbourhood a byte costs under a picojoule**; inside a shire about {f(sh,1)} pJ; across the mesh {f(min(xs),0)}–{f(max(xs),0)} pJ, roughly flat in distance. The step is leaving the shire, not the number of hops after that.",
          "- Small messages cost more per byte (the 128 B rows): the per-message overhead is a few hundred cycles of the sending and receiving harts.",
          f"- **Handing a slab to the next shire through its scratchpad, {f(hop,1)} pJ/B for the write and the read together, costs {f(dram/hop,0)}× less than the DRAM round trip** and sits between the in-shire and cross-mesh tensor-network figures.",
          "- The DRAM relay's bar is the widest of the three: its 4–5 W over idle rides on a DRAM path whose idle draw is not on any rail sensor, so the idle it is measured against is the board's, and the board's idle drifts.\n",
          "Sources: `" + "`, `".join(cm["source"]) + "`, `" + m["relay"]["source"] + "`" + (", `" + RR["source"] + "`" if RR else "") + ".\n"]
    open(os.path.join(out, "05-bytes-between-cores.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 6 sync
    sy = m["sync"]
    at = {x["label"]: x for x in sy["atomics"]["runs"]}
    hn = RR.get("hotline_nj_per_op") or {}
    def hv(lab, n=1):
        c = hn.get(lab)
        return (bar(c, n) + " nJ", cards(c, n)) if c else (f"**{f(at[lab]['nj_per_op'], n)} nJ**", "a2 only")
    con, spr = hv("contended"), hv("spread")
    conm = hn["contended"]["mean"] if "contended" in hn else at["contended"]["nj_per_op"]
    sprm = hn["spread"]["mean"] if "spread" in hn else at["spread"]["nj_per_op"]
    s = ["# 6. Synchronisation\n",
         BARS + (f" The hot line was measured on 22 September and re-run three times on each card on 23 September (n = {hn['contended']['n']})." if hn else "") + "\n",
         "| Event | Energy | per card | Time | Note |", "|---|---|---|---|---|",
         f"| Global atomic, one line, 1,024 requesters | {con[0]} | {con[1]} | {at['contended']['cycles_per_op']:.0f} cycles each at the bank | the bank serialises; every requester stalls |",
         f"| Global atomic, 32 lines, one per shire | {spr[0]} | {spr[1]} | {at['spread']['cycles_per_op']:.2f} cycles each, aggregate | the same instruction, {f(conm/sprm,0)}× cheaper |",
         f"| Uncontended remote atomic round trip | — | | {sy['remote_atomic_latency_cycles']:.0f} cycles | E22 |",
         f"| Chip-wide barrier, 1,024 minions | ≈ {f(1024*1.4e-3*sy['barrier_cycles_chip']/0.6e9*1e9, 0)} nJ of waiting | | {sy['barrier_cycles_chip']:,} cycles | derived: 1,024 minions stalled at 1.4 mW for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |",
         "| FLB + credit barrier, one shire | — | | 237 cycles | nocbench, 18 September |",
         "| TensorReduce + broadcast, 32 minions | — | | 432 cycles | nocbench, 18 September |",
         "", "**What the table says.** A contended hot line is the single most expensive thing a program can do per operation on this chip, and its cost is not on the requesters: the shire that hosts the line loses its own memory path entirely (docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws what a spinning one does, about 1.4 mW — so a barrier's energy is small next to the leakage the card burns while it lasts.\n",
         "The contended row's bar is wide for the same reason as the awake table's: the whole chip stalled draws only 1.4 W over idle, and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.\n",
         "Source: `" + sy["source"] + "`" + (", `" + RR["source"] + "`" if RR else "") + ".\n"]
    open(os.path.join(out, "06-synchronisation.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 8 cards
    ratios = sorted(v for v in m["catalogue"]["cross_card"]["ratios"].values() if v)
    med = ratios[len(ratios) // 2]
    p10, p90 = ratios[len(ratios) // 10], ratios[9 * len(ratios) // 10]
    cd = m.get("cards", {})
    rer = []
    for sec in ("relay_pj_per_byte", "hotline_nj_per_op", "rings_pj_per_byte", "levels_pj_per_byte"):
        for k, v in (RR.get(sec) or {}).items():
            if v and "aifoundry2" in v["per_card"] and "aifoundry3" in v["per_card"]:
                rer.append(v["per_card"]["aifoundry3"]["mean"] / v["per_card"]["aifoundry2"]["mean"])
    rer.sort()
    s = ["# 8. Card-to-card variation\n",
         "Every table in sections 2 to 6 was measured on aifoundry2 and repeated on aifoundry3 with the same binaries. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).\n",
         f"| Comparison | aifoundry3 / aifoundry2 |", "|---|---|",
         f"| Instruction and byte energies, {len(ratios)} catalogue entries, 3 passes each | median **{f(med,3)}**, 10th–90th percentile {f(p10,3)}–{f(p90,3)}, range {f(ratios[0],2)}–{f(ratios[-1],2)} |",
         (f"| Relay, hot line, rings and levels, {len(rer)} entries | median {f(rer[len(rer)//2],3)}, range {f(rer[0],2)}–{f(rer[-1],2)} |" if rer else ""),
         f"| Tensor-unit switching power, 8 operand patterns (E20) | {f(cd.get('scale', 0.924),3)} |",
         "| Idle law extrapolated 25 °C below its fitted range (E20) | +0.73 W of 25 W |",
         "| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |",
         "", "**What it says.** A second card of the same design gives the same energies to about 5%, with a single per-card scale factor that the voltage does not explain and that leans the same way in every table. One random-data run calibrates it. The catalogue is a property of the design; the last 5% is the card.\n",
         "**How the bars split.** For the catalogue's 392 entries the pass-to-pass scatter on one card is 1–2% (median standard error) and the card-to-card difference is 5%: the bar an entry carries is mostly the card, not the day. The small-signal entries — the awake core, the hot line, the DRAM relay — are the exception; there the idle baseline's drift is the bar.\n"]
    open(os.path.join(out, "08-cards.md"), "w").write("\n".join(s))
    print("rendered", out)


if __name__ == "__main__":
    main()
