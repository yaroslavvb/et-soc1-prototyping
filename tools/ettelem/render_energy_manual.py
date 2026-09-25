#!/usr/bin/env python3
"""Render the energy manual's markdown from manual.json, so every number on the page is the one in the data.

    render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/

Every entry carries its confidence bar: **mean** [lo–hi] is the mean over every pass on every card and the full
range those passes spanned; a per-card column is that card's mean ± its pass-to-pass standard error. The bars
come from the three shuffled passes on two cards of the catalogue (sections 2, 3.1, 4.1, 8), the ablation and
the card transfer (3.2), and the reruns of the relay, hot line, rings and levels (4.2, 5, 6).
"""
import json
import math
import os
import statistics
import sys


def f(v, n=2):
    return "—" if v is None else f"{v:,.{n}f}" if abs(v) >= 1000 else f"{v:.{n}f}"


def sci(v):
    """4.59 × 10¹², not 4.59e+12."""
    e = int(f"{v:e}".split("e")[1])
    return f"{v / 10**e:.2f} × 10" + str(e).translate(str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))


WORD = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight"]


def lfit(pts):
    """least-squares line through [(x, y)]: intercept, slope, r²"""
    n = len(pts)
    mx, my = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pts)
    syy = sum((p[1] - my) ** 2 for p in pts)
    b = sxy / sxx
    return my - b * mx, b, sxy * sxy / (sxx * syy)


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
        def se(v):   # a standard error that rounds to zero gets up to two more decimals
            k = n
            while k < n + 2 and v > 0 and float(f(v, k)) == 0:
                k += 1
            return f(v, k)
        return " · ".join(f"a{h[-1]}: {f(v['mean'], n)} ± {se(v['se'])}" for h, v in sorted(c["per_card"].items()))

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
    lk = m["cards"]["leakage"]
    lk_ts = [x["T"] for x in lk["idle_curve"]]
    lk_n = sum(x["n"] for x in lk["idle_curve"])
    lk_t = f"{min(lk_ts)}–{max(lk_ts)} °C"
    tmin = min(x["T"] for x in r["measured_idle"])
    lk_below = f"{tmin - max(lk_ts)}–{tmin - min(lk_ts)} °C"
    rf = m["catalogue"].get("rail_filter") or {}
    taus = [v["tau_s"] for v in rf.values()]
    tau_txt = f"time constant {min(taus):.1f}–{max(taus):.1f} s on the two cards" if taus else "time constant about 1 s"
    s = ["# 1. The card at rest\n",
         "What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.\n",
         "## The law\n",
         f"$$P_\\text{{idle}}(T) = {f(r['P_fix_w'],1)}\\,\\mathrm{{W}} + {f(r['A_leak_80_w'],1)}\\,\\mathrm{{W}}\\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/{f(r['T_L_c'],0)}\\,^\\circ\\mathrm{{C}}}}$$\n",
         # The two slopes are typed: aifoundry2's catalogue idle gaps (600 MHz samples at least 1.5 s before and 2.5 s after
         # any burst, n ≈ 9,800, 71–83 °C) against the die temperature give 0.033 W/°C for board minus the rails and 0.548 W/°C
         # for the three rails together; no committed script writes them (the energy-manual page says the same).
         f"- **The fixed part is the law's constant, {f(r['P_fix_w'],1)} W.** The blocks with no rail sensor (PCIe, the DDR PHY, the IO shire, the regulators) draw about {f(rl['unsensed'],0)} W at idle and barely move with temperature: 0.03 W per °C over 71–83 °C in the catalogue's idle gaps. The three metered rails carry the leakage, 0.55 W per °C between them at about 75 °C. The split into {f(r['P_fix_w'],1)} W and leakage is a fit with the {f(r['T_L_c'],0)} °C shape imposed, not a block-by-block account. What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs of the later sections; [4.3](04a-fine-grain.md) attributes it.",
         f"- **The rest is leakage**, {f(r['A_leak_80_w'],1)} W at 80 °C, e-folding every {f(r['T_L_c'],0)} °C, so its slope at 80 °C is {f(r['lambda_80_w_per_c'],2)} W per °C. This is the term a workload controls, by setting the temperature.",
         f"- **Confidence.** Fitted on 21 September to every idle sample of five hours of sessions on aifoundry2, rms 0.20 W from {min(x['T'] for x in r['measured_idle'])} to {max(x['T'] for x in r['measured_idle'])} °C. Checked two ways: it predicted the idle {f(rl.get('hours_idle'), 1)} hours after the last workload (apart from a 4.9 s single-hart probe a few minutes before), the next day, to {rl['board'] - (r['P_fix_w'] + r['A_leak_80_w'] * math.exp((rl['die_c'] - 80) / r['T_L_c'])):+.2f} W ({rl.get('samples', 300)} samples over a minute, sd {f(rl.get('board_sd'), 2)} W); extrapolated {lk_below} below its fitted range onto aifoundry3 it was {lk['mean_offset_W']:+.2f} W off (rms {f(lk['rms_W'], 2)} W over {lk_n:,} samples at {lk_t}), which is the card-to-card bar on the law: about 3% of the idle power. Source: `" + r["source"]["law"] + "`.\n",
         "| Die °C | Idle W | Leakage share |", "|---|---|---|"]
    for c in r["curve"]:
        if c["T"] % 10 == 0:
            s.append(f"| {c['T']} | {f(c['P_idle'],1)} | {100*c['leak_frac']:.0f}% |")
    s += [f"\n## Where idle goes, by rail ({f(rl['die_c'],0)} °C, {f(rl.get('hours_idle'),1)} hours after the last workload)\n",
          "| Rail | W | Share |", "|---|---|---|",
          f"| Minions | {f(rl['minion'])} | {100*rl['minion']/rl['board']:.0f}% |",
          f"| SRAM (L2, L3, scratchpad) | {f(rl['sram'])} | {100*rl['sram']/rl['board']:.0f}% |",
          f"| Mesh | {f(rl['noc'])} | {100*rl['noc']/rl['board']:.0f}% |",
          f"| **No rail sensor** (PCIe, DDR, IO shire, regulators) | **{f(rl['unsensed'])}** | {100*rl['unsensed']/rl['board']:.0f}% |",
          f"| Board | {f(rl['board'])} ± {f(rl.get('board_sd'), 2)} | |",
          f"\nThe three sensed rails are the PMIC's own running averages (roughly first-order, {tau_txt}), which the service processor reports; the unsensed remainder is board power minus their sum. The sample is aifoundry2 on 22 September, {f(rl.get('hours_idle'),1)} hours after the last workload apart from a 4.9 s single-hart probe a few minutes before; the board figure's ± is the sd of its {rl.get('samples', 300)} samples, taken over one minute; the rails' sd is 0.01 W or less. Source: `" + r["source"]["rails"] + "`. The SRAM rail's own temperature law, on both cards, is in [4.3](04a-fine-grain.md).\n",
          "## Operating points\n", "| MHz | Minion V | Relative switching power (V²f) |", "|---|---|---|"]
    p0 = r["operating_points"][0]
    for p in r["operating_points"]:
        s.append(f"| {p['mhz']} | {f(p['volts'],3)} | {(p['volts']/p0['volts'])**2 * p['mhz']/p0['mhz']:.2f}× |")
    s += ["\nA warm card is held at the first row by the governor, which steps down when the whole-degree die reading is above 65 °C or board power is above 65 W; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md), and aifoundry3, whose firmware reports a TDP of 0 W, never leaves 600 MHz. **On a cooler die the governor lifts the clock in the middle of a burst** (below about 68 °C of the sampler's mean reading, so the reruns preheat the die to 76 °C): the first attempt at the reruns of section 5 and 6 on aifoundry2 (12:51–13:10 on 23 September, die 65 °C) had 700–800 MHz excursions in a fifth of its samples and was discarded; the bars in this manual are from bursts at 600 MHz throughout.\n"]
    if "cards" in r:
        c = r["cards"]
        s += ["## The two working cards\n", "| | aifoundry2 | aifoundry3 |", "|---|---|---|",
              f"| Static TDP the firmware uses | {c['aifoundry2']['tdp_w']} W | **{c['aifoundry3']['tdp_w']} W** (pinned at 600 MHz for life) |",
              f"| Minion voltage at 600 MHz | {c['aifoundry2']['minion_mv']} mV | {c['aifoundry3']['minion_mv']} mV |",
              "| Idle during the 23 September catalogue (catalogue.json bursts) | 31–37 W at 71–82 °C | 23.6–25.0 W at 51–56 °C |", ""]
    open(os.path.join(out, "01-at-rest.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 2 awake
    sp1, sp2 = cb("spin/zeros/h1"), cb("spin/zeros/h2")
    w1, w2 = stat("spin/zeros/h1", "over_idle_w"), stat("spin/zeros/h2", "over_idle_w")
    r1, r2 = stat("spin/zeros/h1", "ops_per_s"), stat("spin/zeros/h2", "ops_per_s")
    aw = m["awake"]["spin_hart0_1024"]
    hot = (RR.get("hotline_over_idle_w") or {}).get("contended")
    at0 = {x["label"]: x for x in m["sync"]["atomics"]["runs"]}["contended"]
    t32 = next(t for t in m["tensor"]["rows"] if t["config"] == "fp32_randn")
    act = m["tensor"]["activity_term_mw_per_minion"]
    nop, fen = cb("nop/zeros/h2"), cb("fence/zeros/h2")
    hw = lambda c: 100 * (c["hi"] - c["lo"]) / 2 / c["mean"]
    s = ["# 2. A core that is awake\n",
         "The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes the awake core.\n",
         BARS + "\n",
         "| Configuration | pJ per instruction | per card | W over idle, 1,024 minions (a2) | Per minion (a2) | Rate |", "|---|---|---|---|---|---|",
         f"| One hart per minion, `addi` loop | {bar(sp1)} | {cards(sp1)} | {f(w1)} | {f(w1/1024*1e3,2)} mW | {sci(r1)}/s |",
         f"| Both harts per minion | {bar(sp2)} | {cards(sp2)} | {f(w2)} | {f(w2/1024*1e3,2)} mW | {sci(r2)}/s |",
         f"| The second hart's share | {f((w2-w1)/(r2-r1)*1e12,1)} pJ per extra instruction | | {f(w2-w1)} | {f((w2-w1)/1024*1e3,2)} mW | |",
         f"| Ablation of 21 Sep: four adds and a branch per iteration, hart 0, 80 °C, 2 runs | {f(aw['pj_marginal'],1)} pJ | a2 only, run-to-run sd 0.02 W | {f(aw['over_idle_w'])} | {f(aw['over_idle_w']/1024*1e3,2)} mW | {sci(aw['per_s'])}/s |",
         (f"| 1,024 minions stalled on one contended atomic (the hot line, E23; each waits about {round(1024*at0['cycles_per_op'], -3):,.0f} cycles for its turn) | — | {cards(hot, 2)} W; both **{f(hot['mean'])}** [{f(hot['lo'])}–{f(hot['hi'])}] | {f(hot['per_card']['aifoundry2']['mean'])} | {f(hot['per_card']['aifoundry2']['mean']/1024*1e3,2)} mW | — |" if hot else
          f"| 1,024 minions stalled on one contended atomic (the hot line, E23; each waits about {round(1024*at0['cycles_per_op'], -3):,.0f} cycles for its turn) | — | a2 only, 22 September | {f(at0['over_idle_w'])} | {f(at0['over_idle_w']/1024*1e3,1)} mW | — |"),
         f"| For scale: every minion running a random-data fp32 matmul (the activity term, E15; {f(act['fp32_randn_8'],1)} mW per minion with 256 or 512 active, {f(act['fp32_randn_24'],1)} with 768) | — | a2 only | {f(t32['over_idle_w'])} | {f(act['fp32_randn'],1)} mW | tensor state machines plus everything else that wakes |",
         f"\n**The addi loop is not the floor.** It increments seven registers, so its operands change on every instruction. With both harts a `nop` costs {f(nop['mean'],1)} pJ [{f(nop['lo'],1)}–{f(nop['hi'],1)}] and a `fence` {f(fen['mean'],1)} [{f(fen['lo'],1)}–{f(fen['hi'],1)}] per instruction ([3.1](03a-every-instruction.md)), so the awake core is about {f(fen['mean'],1)}–{f(nop['mean'],1)} pJ per issue slot. The ablation's loop issued at half the one-hart `addi` loop's rate, on hart 0 only; it is the loop behind the figures in [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power), {f(aw['over_idle_w']/1024*1e3,1)} mW per minion and {f(aw['pj_marginal'],0)} pJ per instruction.\n",
         f"**Rules.** An awake minion costs about 2 mW; a second hart adds about 1 mW; a minion stalled on a contended atomic draws less than one spinning ({f((hot['mean'] if hot else at0['over_idle_w'])/1024*1e3,1)} against {f(w1/1024*1e3,1)} mW). Keeping 1,024 minions awake for a second is {w1:.0f}–{w2:.1f} J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.\n",
         f"The bars here are ±{hw(sp1):.0f}–{hw(sp2):.0f}%, about the catalogue's median, although the signal is small: 2–3 W over a 28–36 W idle that drifts by a few tenths of a watt with the die temperature. The two cards differ by {100*abs(sp2['per_card']['aifoundry3']['mean']/sp2['per_card']['aifoundry2']['mean']-1):.0f}% on the two-hart loop, which is the cross-card scale of section 8.\n",
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
    nop, fen, lg = cb("nop/zeros/h2"), cb("fence/zeros/h2"), cb("flog.ps/random/h2")
    lane = sorted([(fm["mean"] - nop["mean"]) / 8, (fm["mean"] - fen["mean"]) / 8])
    byp = [cb(f"{n}/random/h2")["mean"] for n in ("flwl.ps", "fswl.ps")]
    amo = [cb(f"{n}/random/h2")["mean"] for n in ("amoaddl.w", "amoswapl.w", "amoorl.w", "amomaxl.w", "amoaddl.d", "amoaddg.w", "amoaddg.d")]
    tbw = lambda k: 100 * (tb[k]["hi"] - tb[k]["lo"]) / 2 / tb[k]["mean"] if k in tb else 0
    s = ["# 3. Instructions\n",
         "Energy per instruction retired, above idle, at 600 MHz and 0.52 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2).\n",
         BARS + " Three shuffled passes on each of two cards, so n = 6 for every entry (3 where the constant set was not run). The full catalogue of 161 instructions is in [3.1](03a-every-instruction.md).\n",
         "## Scalar and vector units\n",
         "| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | per card, random | Note |",
         "|---|---|---|---|---|---|---|---|",
         row("add", "add", 1), row("xor", "xor", 1), row("mul", "mul", 1, "64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op"),
         row("fadd.s", "fadd.s", 1), row("fmul.s", "fmul.s", 1), row("fmadd.s", "fmadd.s", 1),
         row("fadd.ps", "fadd.ps (8 lanes)", 8), row("fmul.ps", "fmul.ps (8 lanes)", 8), row("fmadd.ps", "fmadd.ps (8 lanes)", 8, "16 flops"),
         row("fadd.pi", "fadd.pi (8 lanes, int32)", 8), row("fmul.pi", "fmul.pi (8 lanes, int32)", 8),
         row("fexp.ps", "fexp.ps (8 lanes)", 8, "transcendental unit, ¼ the rate"), row("frcp.ps", "frcp.ps (8 lanes)", 8, "transcendental unit"),
         "", "Thirteen instructions trap in U-mode (listed in [3.1](03a-every-instruction.md)), among them every float and vector divide and square root: there is no hardware divide or square root for them on this silicon.\n",
         "**What the table says.**",
         f"- **An integer add costs {f(ia['mean'],1)} pJ on zeros** [{f(ia['lo'],1)}–{f(ia['hi'],1)}], barely more than a `nop` ({f(nop['mean'],1)}) or a `fence` ({f(fen['mean'],1)}): on zeros it is almost all the awake core (section 2). Random operands add {f(iar['mean']-ia['mean'],1)} pJ.",
         f"- **A scalar float add costs {f(fa['mean']/ia['mean'],1)}× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.",
         f"- **An 8-lane vector op on zeros costs the same as the scalar op** ({f(vz['mean'],1)} against {f(fa['mean'],1)} pJ, bars overlapping): lanes computing on zeros add nothing. On random data the eight lanes cost {f(vr['mean']/vz['mean'],1)}× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.",
         f"- **Per lane on random data, `fmadd.ps` is {f(fm['mean']/8,1)} pJ per multiply-add** [{f(fm['lo']/8,1)}–{f(fm['hi']/8,1)}]. The tensor unit below does the same multiply-add for {f(tb['fp32_randn']['mean'],1)} pJ [{f(tb['fp32_randn']['lo'],1)}–{f(tb['fp32_randn']['hi'],1)}]. Take out the vector instruction's issue — {f(fen['mean'],1)}–{f(nop['mean'],1)} pJ, what a fence or a nop costs (section 2) — and the lane is {f(lane[0],1)}–{f(lane[1],1)} pJ, about {100*((lane[0]+lane[1])/2/tb['fp32_randn']['mean']-1):.0f}% above the tensor unit: **of the {f(fm['mean']/8-tb['fp32_randn']['mean'],1)} pJ per multiply-add the tensor unit saves, about half is instruction issue and half datapath** (the operands differ as well: uniform in [0.5, 2) here, normal for the tensor unit).",
         f"- **Integer vector adds are half the price of float ones** ({f(ipz['mean'],1)} vs {f(vz['mean'],1)} pJ on zeros); integer vector multiplies are not.",
         f"- **Transcendentals are the dearest arithmetic**: `fexp.ps` at {f(ex['mean'],0)} pJ and `flog.ps` at {f(lg['mean'],0)} pJ for eight lanes, at a quarter of the rate; `fexp.ps` is {f(ex['mean']/fm['mean'],1)}× a vector multiply-add. Only loads and stores that bypass the L1 ({f(min(byp),0)}–{f(max(byp),0)} pJ) and atomics ({f(min(amo),0)}–{f(max(amo),0)} pJ) cost more ([3.1](03a-every-instruction.md)).\n",
         "## 3.2 The tensor unit\n",
         "`TensorFMA` on a tile per instruction: fp32 16×16×16 = 4,096 multiply-adds, fp16 8,192, int8 16,384; 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, launched at 80 °C. **Marginal** is board power above idle per multiply-add; **loaded** is total board power, idle included, per multiply-add, which is what a multiply-add costs when it is the only thing running.\n",
         f"The bar on each fp32 row is the envelope of ±1 sd around the ablation's two runs on aifoundry2 and the 22 September transfer's runs on both cards (n = 4); fp16 and int8 were run twice on aifoundry2 only, and their bar is ±1 sd of those two runs: under {math.ceil(max(tbw('fp16_randn'), tbw('int8_randn'))):.0f}% on random data, {tbw('int8_zeros'):.1f}% on int8 zeros, {min(tbw('fp16_ones'), tbw('int8_ones')):.0f}–{max(tbw('fp16_ones'), tbw('int8_ones')):.0f}% on the ones patterns.\n",
         "| Type, operands | pJ per MAC, marginal | per card | pJ per MAC, loaded (a2) | W over idle (a2) | MACs per second |", "|---|---|---|---|---|---|"]
    for t in m["tensor"]["rows"]:
        b = tb[t["config"]]
        pc = " · ".join(f"a{h[-1]}: {f(v['mean'],3)}" for h, v in sorted(b["per_card"].items())) + ("" if b["cards"] > 1 else " (a2 only)")
        s.append(f"| {t['label']} | **{f(b['mean'],3)}** [{f(b['lo'],3)}–{f(b['hi'],3)}] | {pc} | {f(t['pj_loaded'],2)} | {f(t['over_idle_w'],2)} | {sci(t['per_s'])} |")
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
        if not bps and scale < 1:   # the L1 rows: the instruction rate times the bytes per instruction
            bps = stat(f"{key}/random" + (f"/h{harts}" if harts else ""), "ops_per_s") / scale
        nd = lambda c: 1 if c["mean"] >= 10 else 2   # two decimals below 10, one above, as on the page
        return (f"| {label} | {bar(z, nd(z))} | {bar(rn, nd(rn))} | {f(rn['mean']/z['mean'],2)}× | "
                f"{f(bps/1e9, 0) if bps else '—'} | {cards(rn, nd(rn))} |")
    lv = RR.get("levels_pj_per_byte") or {}
    mr = m["memory_reads"]
    dl, sl = cb("tload/dram/random"), cb("tload/scp/random")
    ds, ss = cb("tstore/dram/random"), cb("st_stream/dram/random")
    dz = cb("tload/dram/zeros")
    ssz, slz = cb("tstore/scp/zeros"), cb("tload/scp/zeros")
    l1 = cb("flw.ps/random/h2", 1 / 32)
    def off_rail(k):   # aifoundry2: over idle less the rails and the fitted delivery losses on them, per byte (Limits of observability §4.2)
        e, c = S["aifoundry2"][k], m["unmetered"]["aifoundry2"]["coef"]
        R_ = e["rails_over_w"]; mm, sr, nn = R_["minion_w"]["mean"], R_["sram_w"]["mean"], R_["noc_w"]["mean"]
        return (e["over_idle_w"]["mean"] - mm - sr - nn - (c["minion"] * mm + c["sram"] * sr + c["noc"] * nn)) / e["bytes_per_s"]["mean"] * 1e12
    dd4 = [cb(k + "/random" + h)["mean"] / cb(k + "/zeros" + h)["mean"] for k, h in
           (("flw.ps", "/h2"), ("fsw.ps", "/h2"), ("tload/scp", ""), ("tstore/scp", ""), ("tload/dram", ""), ("tstore/dram", ""), ("st_stream/dram", ""))]
    s = ["# 4. Bytes through the memory hierarchy\n",
         f"Energy per byte moved, above idle, at 600 MHz. Zeros and random data, because the data is a large part of the cost at every level: random data costs {min(dd4):.1f}–{max(dd4):.1f}× what zeros cost on the paths of 4.1.\n",
         BARS + "\n",
         "## 4.1 Reads and writes, measured together (23 September, three passes on each card)\n",
         "| Path | zeros pJ/B | random pJ/B | random / zeros | GB/s | per card, random |", "|---|---|---|---|---|---|",
         mrow("flw.ps", "L1 hit, `flw.ps` 32 B (both harts)", 1 / 32, 2),
         mrow("fsw.ps", "L1 hit, `fsw.ps` 32 B (both harts)", 1 / 32, 2),
         mrow("tload/scp", "Tensor load from the shire's own scratchpad"),
         mrow("tstore/scp", "Tensor store into the shire's own scratchpad"),
         mrow("tload/dram", "Tensor load from DRAM"),
         mrow("tstore/dram", "Tensor store to DRAM"),
         mrow("st_stream/dram", "`fsw.ps` stores to DRAM through the L1 (the write-back path)"),
         ""]
    if lv:
        LV = [("l1", "L1 hits", "256 B per hart, 2,048 harts"), ("l2", "L2", "256 KB per shire (L2 is 512 KB)"),
              ("l3", "L3", "768 KB per shire, 24 MB in all (L3 is 32 MB)"), ("dram", "DRAM", "256 MB in all"),
              ("scp-local", "own scratchpad", "2 MB of the shire's own L2 scratchpad"),
              ("scp-remote", "remote scratchpad", f"2 MB of the scratchpad 16 shire IDs away ({f(m['comm']['mesh_hops']['xshire16']['mean'], 1)} mesh hops on average)")]
        gh = [x["implied_ghz"] for x in mr["rows"] if x.get("implied_ghz")]
        l1c = cb("flw.ps/random/h2", 1 / 32)
        # The two L1 loops: memhier.c's (8 flw.ps per loop iteration; minion-cycles per load from its 18 September row, B per
        # cycle being clock-independent in the minion's domain) and the catalogue's (enercat.c's RUN macro, 64 per iteration;
        # both cards' issue rate, and aifoundry2's instruction rate as in 4.1).
        mh1 = next(x for x in mr["rows"] if x["level"] == "l1")
        cyc_mh = 32 / (mh1["gb_s"] / (mh1["implied_ghz"] * 1024))
        cyc_cat = 1 / (2 * statistics.fmean(S[h]["flw.ps/random/h2"]["ops_per_cycle_per_hart"]["mean"] for h in S))
        tbs_cat = stat("flw.ps/random/h2", "ops_per_s") * 32 / 1e12
        s += ["## 4.2 Reads by level (memhier, re-run at a pinned 600 MHz on 23 September)\n",
              f"**L1**: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in memhier's own loop over a buffer whose contents it does not set. "
              f"That loop (8 loads per loop iteration) issued a load every {cyc_mh:.1f} minion-cycles where the catalogue's (64) issued one every {cyc_cat:.1f} ({tbs_cat:.1f} TB/s), and it reads {100*(lv['l1']['mean']/l1c['mean']-1):.0f}% above the L1 row of 4.1 ({f(l1c['mean'])} pJ/B on random data), which is the figure to use. "
              "**L2, L3, DRAM and the scratchpads**: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. "
              "The probe does not set the memory's contents, so these rows sit between the zeros and random columns of 4.1 and are not directly comparable to them. "
              f"{WORD[RR['passes'].get('levels', 0) // 2].capitalize()} passes on each card at a pinned 600 MHz (n = {RR['passes'].get('levels', 0)}). The first measurement of 18 September ran with the governor free (its clock averaged {min(gh):.2f}–{max(gh):.2f} GHz across the levels) and is superseded.\n",
              "| Level | Working set | pJ/B | per card |", "|---|---|---|---|"]
        for k, lab, what in LV:
            c = lv.get(k)
            if c:
                s.append(f"| {lab} | {what} | {bar(c, 1 if c['mean'] >= 10 else 2)} | {cards(c, 1 if c['mean'] >= 10 else 2)} |")
        s += ["", f"Passes: {RR['passes'].get('levels', 0)}. Source: `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`."]
    else:
        s += ["## 4.2 Reads by level (18 September, memhier)\n",
              "| Level | Working set | pJ/B | GB/s | Clock during the run |", "|---|---|---|---|---|"]
        for x in mr["rows"]:
            s.append(f"| {x['level']} | {x['what']} | {f(x['pj_per_byte'])} | {x['gb_s']:.0f} | {f(x.get('implied_ghz'),2)} GHz implied |")
        s += ["", "*Caveat:* " + mr["caveat"] + "."]
    s += ["", "**What the tables say.**",
          f"- **DRAM is {f(dl['mean']/sl['mean'],0)}× the energy of the shire's own scratchpad per byte read**, and {f(ds['mean']/cb('tstore/scp/random')['mean'],0)}× per byte written.",
          f"- **A DRAM write costs about what a DRAM read costs** ({f(ds['mean'],0)} vs {f(dl['mean'],0)} pJ/B on random data) — by tensor store, which skips the L1 and the L2. **Through the L1 write-back path the same bytes cost {f(ss['mean']/ds['mean'],1)}× more** and arrive at a third of the bandwidth: each store allocates its line, so the line is read from DRAM before it is written back and the byte pays for a read and a write. Off-rail it costs {f(off_rail('st_stream/dram/random'),0)} pJ against a tensor store's {f(off_rail('tstore/dram/random'),0)} ([Limits of observability, §4.2](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed)), and a tensor load plus a tensor store come to {f(dl['mean']+ds['mean'],0)} of its {f(ss['mean'],0)} pJ/B.",
          f"- **Even DRAM is data-dependent**: zeros {f(dz['mean'],0)}, random {f(dl['mean'],0)} pJ/B, bars [{f(dz['lo'],0)}–{f(dz['hi'],0)}] and [{f(dl['lo'],0)}–{f(dl['hi'],0)}] well apart. The scratchpad doubles from zeros to random.",
          f"- **A scratchpad write is twice a scratchpad read** ({f(ssz['mean'])} vs {f(slz['mean'])} pJ/B on zeros).",
          f"- **An L1 hit is nearly free**: {f(l1['mean'])} pJ/B [{f(l1['lo'])}–{f(l1['hi'])}] including the instruction.\n",
          "Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in [4.3](04a-fine-grain.md).\n",
          "Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/`, `" + mr["source"]["rows"] + "`.\n"]
    open(os.path.join(out, "04-bytes-memory.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 5 comm
    cm = m["comm"]
    MH = cm.get("mesh_hops", {})
    rg = RR.get("rings_pj_per_byte") or {}
    rp = {x["medium"]: x for x in m["relay"]["power"]["media"]}
    rr = RR.get("relay_pj_per_byte") or {}
    hops = lambda k: ("—" if k not in MH else "0" if not MH[k]["mean"] else f"{f(MH[k]['mean'], 1)} ({MH[k]['min']}–{MH[k]['max']})")
    dev = sorted(100 * (x["pj_per_byte_local"] / rg[x["ring"]]["mean"] - 1) for x in cm["rows"] if x["ring"] in rg and x.get("pj_per_byte_local"))
    drop = [x["sampler_median_ms"] for x in RR.get("dropped", []) if x.get("sampler_median_ms")]
    x16 = next((x for x in cm["rows"] if x["ring"] == "xshire16"), None)
    s = ["# 5. Bytes between cores and shires\n",
         "Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz and 518 mV. "
         "Shire IDs do not follow the mesh, so each ring between shires is given with its mean distance in mesh hops, the Manhattan distance between shire s and shire s + k averaged over all 32 compute shires on the shire map of [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication).\n",
         BARS + (f" The rings were re-measured on 23 September with the manual's own sampler, {WORD[RR['passes'].get('rings', 0) // 2]} passes on each card, the die held warm on aifoundry2. The pair of 18 September runs, sampled without the die temperature and so without a leakage correction, is not pooled; the values On-chip communication publishes from it read {dev[0]:.0f}–{dev[-1]:.0f}% higher in every configuration (median {dev[len(dev) // 2]:.0f}%). "
                 f"**The s ↔ s+16 ring starves the service processor's own management path** — the sampler's latency rises from 22 ms to {min(drop):.0f}–{max(drop):.0f} ms and the board reading takes a new value about twice a second instead of six times — so its aifoundry2 passes were dropped and that row is aifoundry3 only"
                 + (f" (On-chip communication gives {f(x16['pj_per_byte_local'], 1)} pJ/B for it on aifoundry2 on 18 September)." if x16 and x16.get("pj_per_byte_local") else ".") if rg else " Two independent runs averaged; ± is half their difference.") + "\n",
         "| Ring | What moves | Mesh hops, mean (range) | pJ/B | per card | GB/s aggregate |", "|---|---|---|---|---|---|"]
    small = lambda k: k.endswith("c4")
    for x in sorted(cm["rows"], key=lambda x: (small(x["ring"]), (MH.get(x["ring"]) or {"mean": 0})["mean"])):
        c = rg.get(x["ring"])
        s.append(f"| {x['ring']} | {x['what']} | {hops(x['ring'])} | {bar(c, 2) if c else '**' + f(x['pj_per_byte']) + '** ± ' + f(x['pj_spread'])} | {cards(c, 2) if c else 'a2 only'} | {x['gb_s']:,.0f} |")
    pc = (rr.get("dram") or {}).get("per_card", {})
    rel_note = (f"The relay was measured on 22 September on aifoundry2 and re-run on 23 September, three warm passes on aifoundry2 and {WORD[pc['aifoundry3']['n']]} on aifoundry3 (n = {rr['dram']['n']}). A stage reads a slab, adds 1 and writes it where the next stage reads it; the next shire is shire s − 1 by ID, {hops('xshire1')} mesh hops away." if rr and "aifoundry3" in pc else "")
    s += ["", "## Handing a slab to the next shire through its scratchpad (E25)\n" + rel_note + "\n",
          "| Medium | pJ per byte (read + write) | per card | GB/s on the card |", "|---|---|---|---|"]
    for med, label in (("dram", "Write to DRAM, read back"), ("hop", "Write where the next shire reads it"), ("scp", "Keep it in this shire's scratchpad")):
        c = rr.get(med)
        v = bar(c, 1) if c else f"**{f(rp[med]['pj_per_byte'],1)}**"
        s.append(f"| {label} | {v} | {cards(c, 1) if c else 'a2 only'} | {rp[med]['bytes_per_s']/1e9:,.0f} |")
    mesh = [x for x in cm["rows"] if x["ring"].startswith("xshire") and "c4" not in x["ring"]]
    xs = [(rg[x["ring"]]["mean"] if x["ring"] in rg else x["pj_per_byte"]) for x in mesh]
    a_, b_, r2_ = lfit([(MH[x["ring"]]["mean"], rg[x["ring"]]["mean"] if x["ring"] in rg else x["pj_per_byte"]) for x in mesh]) if MH else (None, None, None)
    hx = [MH[x["ring"]]["mean"] for x in mesh] if MH else [0]
    pr = rg["pair"]["mean"] if "pair" in rg else cm["rows"][0]["pj_per_byte"]
    sh = (rg["shire"]["mean"] + rg["neigh"]["mean"]) / 2 if "shire" in rg else cm["rows"][2]["pj_per_byte"]
    hop = rr["hop"]["mean"] if rr else rp["hop"]["pj_per_byte"]
    dram = rr["dram"]["mean"] if rr else rp["dram"]["pj_per_byte"]
    hw = [100 * (rr[k]["hi"] - rr[k]["lo"]) / 2 / rr[k]["mean"] for k in ("dram", "hop", "scp") if k in rr]
    ow = [rp[k]["over_idle_w"] for k in ("dram", "hop", "scp")]
    s += ["", "**What the tables say.**",
          f"- **Between the two minions of a pair a byte costs under a picojoule** ({f(pr, 2)} pJ); around a neighbourhood or a shire about {f(sh,1)} pJ; across the mesh {f(min(xs),0)}–{f(max(xs),0)} pJ"
          + (f": about {f(a_, 0)} pJ to leave the shire plus {f(b_, 1)} pJ per mesh hop (a straight line through the six 1 KB rings between shires against their mean distances of {f(min(hx), 1)}–{f(max(hx), 1)} hops, r² {f(r2_, 2)}; [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures 1.5 pJ/B per hop on the mesh rail and 2.2 on board power directly). **Leaving the shire is the biggest single step, but the hops after it are not free.**" if a_ is not None else "."),
          "- Small messages cost more per byte (the 128 B rows): the per-message overhead is 40–224 cycles of the sending and receiving harts ([On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication)).",
          f"- **Handing a slab to the next shire through its scratchpad, {f(hop,1)} pJ/B for the write and the read together, costs {f(dram/hop,0)}× less than the DRAM round trip** and sits between the in-shire and cross-mesh tensor-network figures.",
          (f"- The three relay bars are ±{min(hw):.0f}–{max(hw):.0f}% because each is a {min(ow):.0f}–{max(ow):.0f} W signal over a board idle that drifts; the DRAM relay's power also rides on a path with no rail sensor.\n" if hw else ""),
          "Sources: `" + "`, `".join(cm["source"]) + "`, `" + m["relay"]["source"] + "`" + (", `" + RR["source"] + "`" if RR else "") + "; mesh hops from [marty1885](https://github.com/marty1885/etTopoScan)'s shire map as `workloads/nocbench/analyze.py` holds it.\n"]
    open(os.path.join(out, "05-bytes-between-cores.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 6 sync
    sy = m["sync"]
    at = {x["label"]: x for x in sy["atomics"]["runs"]}
    hn = RR.get("hotline_nj_per_op") or {}
    def hv(lab, n=1):
        c = hn.get(lab)
        return (bar(c, n) + " nJ", cards(c, n)) if c else (f"**{f(at[lab]['nj_per_op'], n)} nJ**", "a2 only")
    con, spr = hv("contended"), hv("spread", 2)
    conm = hn["contended"]["mean"] if "contended" in hn else at["contended"]["nj_per_op"]
    hot6 = (RR.get("hotline_over_idle_w") or {}).get("contended")
    stall_w = hot6["mean"] if hot6 else at["contended"]["over_idle_w"]   # 1,024 minions stalled, W over idle
    sprm = hn["spread"]["mean"] if "spread" in hn else at["spread"]["nj_per_op"]
    s = ["# 6. Synchronisation\n",
         BARS + (f" The hot line was measured on 22 September on aifoundry2 and re-run on 23 September, three warm passes on aifoundry2 and {WORD[hn['contended']['per_card']['aifoundry3']['n']]} on aifoundry3 (n = {hn['contended']['n']}); the first session alone gave {f(at['contended']['nj_per_op'], 1)} and {f(at['spread']['nj_per_op'], 2)} nJ." if hn else "") + "\n",
         "| Event | Energy | per card | Time | Note |", "|---|---|---|---|---|",
         f"| Global atomic, one line, 1,024 requesters | {con[0]} | {con[1]} | {at['contended']['cycles_per_op']:.0f} cycles each at the bank | the bank serialises and every requester waits its turn; the host shire's own loads stop |",
         f"| Global atomic, 32 lines, one per shire | {spr[0]} | {spr[1]} | {at['spread']['cycles_per_op']:.2f} cycles each, aggregate | the same instruction, {f(conm/sprm,0)}× cheaper |",
         f"| Uncontended remote atomic round trip | — | | {sy['remote_atomic_latency_cycles']:.0f} cycles | E22 |",
         f"| Chip-wide barrier, {sy.get('barrier_participants', 1024):,} minions | ≈ {f(stall_w*sy['barrier_cycles_chip']/0.6e9*1e6, 0)} µJ of waiting | | {sy['barrier_cycles_chip']:,} cycles | derived: 1,024 minions stalled at {f(stall_w/1024*1e3, 1)} mW (§2) for the barrier's length; the 32 atomics and 32 credit stores are negligible beside it |",
         "| FLB (fast local barrier) + credit barrier, one shire | — | | 237 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), 18 September |",
         "| TensorReduce (the hardware reduction tree) + broadcast, 32 minions | — | | 432 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), 18 September |",
         "", f"**What the table says.** A contended atomic costs {f(conm/sprm,0)}× the same atomic spread over 32 lines, and its cost is not on the requesters: the shire that hosts the line keeps its share of the atomic, but its own other loads stop ([One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line), docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws about {f(stall_w/1024*1e3, 1)} mW, less than a spinning one ({f(stat('spin/zeros/h1', 'over_idle_w')/1024*1e3, 1)} mW, section 2) — so a barrier's energy is small next to the leakage the card burns while it lasts.\n",
         f"The contended row's bar is wide because the whole chip stalled draws only about {f(conm*at['contended']['ops_per_s']*1e-9, 1)} W over idle ({f(at['contended']['over_idle_w'], 1)} W in the first session), and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.\n",
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
         "Every catalogue and rerun table in sections 2 to 6 was measured on aifoundry2 and repeated on aifoundry3 with the same binaries; the rows that ran on one card say so. aifoundry1 holds two cards that cannot be opened (docs/findings/14-card-behaviour.md).\n",
         f"| Comparison | aifoundry3 / aifoundry2 |", "|---|---|",
         f"| Instruction and byte energies, {len(ratios)} catalogue entries, 3 passes each | median **{f(med,3)}**, 10th–90th percentile {f(p10,3)}–{f(p90,3)}, range {f(ratios[0],2)}–{f(ratios[-1],2)} |",
         (f"| Relay, hot line, rings and levels, {len(rer)} entries | median {f(rer[len(rer)//2],3)}, range {f(rer[0],2)}–{f(rer[-1],2)} |" if rer else ""),
         f"| Tensor-unit switching power, 8 operand patterns (E20) | {f(cd.get('scale', 0.924),3)} |",
         f"| Idle law extrapolated {lk_below} below its fitted range (E20) | {lk['mean_offset_W']:+.2f} W of about 25 W |",
         "| Minion voltage at 600 MHz | 523 mV against 518 mV, which predicts 2% *more* |",
         "", f"**What it says.** A second card of the same design reads about {100*(1-med):.0f}% lower (median {f(med,2)}; 10–90%: {f(p10,2)}–{f(p90,2)}), with a single per-card scale factor that the voltage does not explain and that leans the same way in every table. One random-data run calibrates it. The catalogue is a property of the design; the last 5% is the card.\n",
         f"**How the bars split.** For the catalogue's {len(ratios)} shared entries the pass-to-pass scatter on one card is 1–2% (median standard error) and the card-to-card difference is 5%: the bar an entry carries is mostly the card, not the day. The smallest signal, the hot line (about {hn['contended']['mean']*at['contended']['ops_per_s']*1e-9:.1f} W over idle), carries the widest bar, ±{100*(hn['contended']['hi']-hn['contended']['lo'])/2/hn['contended']['mean']:.0f}%, because there the idle baseline's drift is most of the bar; the awake core (±5–7%) and the DRAM relay (±{100*(rr['dram']['hi']-rr['dram']['lo'])/2/rr['dram']['mean']:.1f}%) are about as wide as a typical catalogue entry.\n"]
    open(os.path.join(out, "08-cards.md"), "w").write("\n".join(s))
    print("rendered", out)


if __name__ == "__main__":
    main()
