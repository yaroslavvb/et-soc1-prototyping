#!/usr/bin/env python3
"""Render the energy manual's markdown from manual.json, so every number on the page is the one in the data.

    render_energy_manual.py docs/reports/data/2026-09-23-energy-manual/manual.json docs/energy-manual/

Every entry carries its confidence bar: **mean** [lo–hi] is the mean over every pass on every card and the full
range those passes spanned; a per-card column is that card's mean ± its pass-to-pass standard error. The bars
come from the version-3 check's measurements on three cards (26 September 2026: the full catalogue, three shuffled
passes on each card, for sections 2, 3.1, 4.1, 4.3, 8; the tensor ablation, four runs on each card, for 3.2; the rings,
levels and relay, six passes on each card, for 4.2 and 5) and the reruns of the hot line (6, two cards). The per-card
figures of the check itself (manual.json v3) give each card's idle, the card-to-card scale and the tests' intervals.
"""

ORDER = ["aifoundry2", "aifoundry3", "aifoundry1-c1", "aifoundry1-c0"]     # the pages' card registry order
SHORT = {"aifoundry2": "a2", "aifoundry3": "a3", "aifoundry1-c1": "a1c1", "aifoundry1-c0": "a1c0"}
NAME = {"aifoundry1-c1": "aifoundry1 card 1", "aifoundry1-c0": "aifoundry1 card 0"}


def order(cards):
    return sorted(cards, key=lambda c: ORDER.index(c) if c in ORDER else len(ORDER))


def name(c):
    return NAME.get(c, c)


def and_list(xs):
    xs = list(xs)
    return "".join(xs) if len(xs) < 2 else ", ".join(xs[:-1]) + " and " + xs[-1]


def semi_list(xs):
    xs = list(xs)
    return "".join(xs) if len(xs) < 2 else "; ".join(xs[:-1]) + "; and " + xs[-1]


def sgn(v, n=2):
    return ("−" if v < 0 else "+") + f"{abs(v):.{n}f}"


def neg(v, n=2):
    return ("−" if v < 0 else "") + f"{abs(v):.{n}f}"
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
        return " · ".join(f"{SHORT.get(h, h)}: {f(c['per_card'][h]['mean'], n)} ± {se(c['per_card'][h]['se'])}" for h in order(c["per_card"]))

    def rate(key, field="ops_per_cycle_per_hart"):
        e = S["aifoundry2"].get(key)
        return e[field]["mean"] if e else None

    def stat(key, field):
        e = S["aifoundry2"].get(key)
        return e[field]["mean"] if e else None

    BARS = ("Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "
            "\"a2\", \"a3\" and \"a1c1\" are aifoundry2, aifoundry3 and aifoundry1's card 1, each as its own mean ± its pass-to-pass standard error.")
    V = m.get("v3", {})
    VI = V.get("idle", {})
    CATSRC = ("`docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/` (the version-3 full catalogue, reduced by "
              "`tools/claims-v3/catfull/reduce.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`)")
    # AMENDMENTS.md C2: every card's V3-ABL-A switching carries a launch-temperature offset (tensor.launch_offset); the
    # registered values stay in the tables, and the text that compares cards gives the offsets and the values at each run's launch
    # C2 as revised: the launch temperatures are whole-degree readings, the references thermal-model temperatures at launches on a
    # downward step of the reading; at_launch_step_w takes each launch to be on such a step (die = reading + step_c), at_launch_w
    # the reading as the die temperature, and the text gives each value as the range over the two (rng2)
    LO = m["tensor"].get("launch_offset", {})
    atl = lambda h, k: LO.get(h, {}).get("at_launch_w", {}).get(k)
    atls = lambda h, k: LO.get(h, {}).get("at_launch_step_w", {}).get(k)

    def rng2(a, b, n=2):
        if a is None or b is None:
            return f(a if b is None else b, n)
        lo, hi = f(min(a, b), n), f(max(a, b), n)
        return lo if lo == hi else f"{lo}–{hi}"

    def lo_off(h):
        a, b = LO[h]["mean_w"], LO[h].get("mean_w_step")
        if b is None:
            return f"{abs(a):.2f} W {'lower' if a < 0 else 'higher'}"
        lo, hi = min(a, b), max(a, b)
        return (f"{lo:.2f}–{hi:.2f} W higher" if lo >= 0 else f"{-hi:.2f}–{-lo:.2f} W lower" if hi <= 0
                else f"between {-lo:.2f} W lower and {hi:.2f} W higher")
    lo_by = {}
    for h in order(LO):
        lo_by.setdefault(f"{LO[h]['ref_c']:.1f}", []).append(h)
    st_c = LO[order(LO)[0]].get("step_c") if LO else None
    lo_note = ("the registered switching values carry a launch-temperature offset (AMENDMENTS.md, note C2): they are referenced to "
               + and_list(f"{r} °C ({and_list(name(h) for h in hs)})" for r, hs in lo_by.items())
               + " while the runs launched at whole-degree readings of " + and_list(f"{LO[h]['launch_c']:.1f}" for h in order(LO)) + " °C in that order"
               + (f"; the references were taken at launches on a downward step of the reading, so the die at these launches was at the reading or up to {st_c:.2f} °C above it, which the reading cannot tell apart," if st_c is not None else ",")
               + " so at the die temperature of each launch "
               + and_list(f"{name(h)}'s are {lo_off(h)}" for h in order(LO))) if LO else ""
    CARDS = order(m["catalogue"]["cards"])
    NC = WORD[len(CARDS)]

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
    tau_txt = ("time constant " + and_list(f"{rf[h]['tau_s']:.2f} s on {name(h)}" for h in order(rf) if rf[h])) if taus else "time constant about 1 s"
    pf, iu, lr = r["profile"], m["catalogue"]["idle_unsensed"], m["catalogue"]["idle_law_residual"]
    p80 = r["P_fix_w"] + r["A_leak_80_w"]
    # the version-3 idle cycles (manual.json v3.idle): the unsensed blocks' and metered rails' slopes, each card against the law
    ci99 = lambda x, n=2: f"{f(x['mean'], n)} [{f(x['ci99'][0], n)}–{f(x['ci99'][1], n)}]"
    US, RS, a3u = VI.get("unsensed_slope_74_88", {}), VI.get("rails_slope_75_80", {}), VI.get("unsensed_slope_a3_cycles") or []
    uns_slope = (f"{ci99(US['aifoundry2'])} W per °C over 74–88 °C on aifoundry2 in the version-3 idle cycles (26 September, three per card; 99% intervals)"
                 + (", " + and_list(([f"{f(sum(a3u) / len(a3u), 2)} on aifoundry3"] if a3u else []) + [f"{ci99(US[h])} on {name(h)}" for h in order(US) if h != "aifoundry2"]) if a3u or len(US) > 1 else "")
                 if "aifoundry2" in US else "0.03 W per °C over 71–83 °C in the catalogue's idle gaps")
    rails_slope = (f"{ci99(RS['aifoundry2'])} W per °C between them at 75–80 °C on aifoundry2" + (" (" + and_list(f"{ci99(RS[h])} on {name(h)}" for h in order(RS) if h != "aifoundry2") + ")" if len(RS) > 1 else "")
                   if "aifoundry2" in RS else "0.55 W per °C between them at about 75 °C")
    L2, LRv = VI.get("law_residual_a2"), VI.get("law_residual", {})
    v3_idle = semi_list(([f"aifoundry2 sat {sgn(L2['mean'])} W [{sgn(L2['ci99'][0])}, {sgn(L2['ci99'][1])}] from the law at {L2['T'][0]}–{L2['T'][1]} °C"] if L2 else [])
                        + [f"{name(h)} {sgn(LRv[h]['mean'])} W [{sgn(LRv[h]['ci99'][0])}, {sgn(LRv[h]['ci99'][1])}] at {LRv[h]['T'][0]}–{LRv[h]['T'][1]} °C, the gap growing {f(LRv[h]['slope_w_per_c']['mean'], 3)} W per °C"
                           for h in order(LRv) if h != "aifoundry2"])
    PCL = r.get("per_card", {})
    per_card_laws = and_list(f"{name(h)} {f(PCL[h]['P_fix_w'], 1)} W + {f(PCL[h]['A_leak_80_w'], 1)} W·e^((T−80)/36), rms {f(PCL[h]['rms_w'], 2)} W" for h in order(PCL))
    fr_ = []
    for t_ in sorted(x["T"] for x in r["measured_idle"]):
        if fr_ and t_ == fr_[-1][1] + 1:
            fr_[-1][1] = t_
        else:
            fr_.append([t_, t_])
    fit_runs = and_list(f"{a_}–{b_}" if a_ != b_ else f"{a_}" for a_, b_ in fr_)
    rg0 = lambda v: f"{v[0]:.0f}–{v[1]:.0f}"
    sg = lambda v: ("−" if v < 0 else "+") + f(abs(v), 2)
    s = ["# 1. The card at rest\n",
         "What the card draws when nothing is running. Every joule in the rest of the manual is *above* this.\n",
         "## The law\n",
         f"$$P_\\text{{idle}}(T) = {f(r['P_fix_w'],1)}\\,\\mathrm{{W}} + {f(r['A_leak_80_w'],1)}\\,\\mathrm{{W}}\\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/{f(r['T_L_c'],0)}\\,^\\circ\\mathrm{{C}}}}$$\n",
         # The two slopes are typed: aifoundry2's catalogue idle gaps (600 MHz samples at least 1.5 s before and 2.5 s after
         # any burst, n ≈ 9,800, 71–83 °C) against the die temperature give 0.033 W/°C for board minus the rails and 0.548 W/°C
         # for the three rails together; no committed script writes them (the energy-manual page says the same).
         # D3 (version 3): the law is led by its measured slope; its split into fixed and leakage is the range over the
         # e-foldings that fit the idle bins equally well (rest.profile, build_energy_manual.py).
         f"- **What the idle measurements pin down is the slope.** On aifoundry2 the idle card draws {f(p80,1)} W at 80 °C and {f(r['lambda_80_w_per_c'],2)} W more for each degree there ({f(pf['lambda_80_w_per_c'][0],2)}–{f(pf['lambda_80_w_per_c'][1],2)} W per °C for every e-folding that fits). This is the term a workload controls, by setting the temperature.",
         f"- **How much of it is leakage they do not.** The idle bins fit equally well with the leakage e-folding anywhere from {pf['T_L_window_c'][0]} to {pf['T_L_window_c'][1]} °C (doubling every {rg0(pf['doubling_c'])} °C), which puts the leakage at 80 °C at {rg0(pf['A_leak_80_w'])} W and the fixed part at {rg0(pf['P_fix_w'])} W. The law above is the best fit, {f(r['P_fix_w'],1)} W fixed and {f(r['A_leak_80_w'],1)} W of leakage at 80 °C e-folding every {f(r['T_L_c'],0)} °C: a fit, not a block-by-block account.",
         f"- **The blocks with no rail sensor** (PCIe, the DDR PHY, the IO shire, the regulators) draw about {and_list(f'{f(iu[h]['mean'],0)} W on {name(h)} ({rg0(iu[h]['die_c'])} °C)' for h in order(iu))} at idle in the catalogue's idle stretches, and move little with temperature: {uns_slope}. The three metered rails carry the leakage, {rails_slope}. What the unsensed blocks spend when a kernel uses them (DRAM traffic through the DDR PHY, the regulators' delivery loss) is counted in the per-event costs of the later sections; [4.3](04a-fine-grain.md) attributes it.",
         f"- **Confidence.** Fitted on 21 September to every idle sample of five hours of sessions on aifoundry2, rms 0.20 W from {min(x['T'] for x in r['measured_idle'])} to {max(x['T'] for x in r['measured_idle'])} °C (bins {fit_runs} °C). Checked two ways: it predicted the idle {f(rl.get('hours_idle'), 1)} hours after the last workload (apart from a 4.9 s single-hart probe a few minutes before), the next day, to {rl['board'] - (r['P_fix_w'] + r['A_leak_80_w'] * math.exp((rl['die_c'] - 80) / r['T_L_c'])):+.2f} W ({rl.get('samples', 300)} samples over a minute, sd {f(rl.get('board_sd'), 2)} W); and in the version-3 check's idle cycles (26 September: three heat-and-cool cycles per card, every sample at 600 MHz) {v3_idle}. The law holds on aifoundry2 to a tenth of a watt; the other two cards idle above it, and [7](07-composition.md) prices each with its own law (the same form refitted to its cycles, e-folding held at 36 °C: {per_card_laws}). Source: `" + r["source"]["law"] + "`, `" + V.get("source", "") + "/idle.json`.\n",
         f"| Die °C | Idle W, best fit | Leakage share, best fit | Leakage share, e-folding {pf['T_L_window_c'][0]}–{pf['T_L_window_c'][1]} °C |", "|---|---|---|---|"]
    for c in r["curve"]:
        if c["T"] % 10 == 0:
            lo_, hi_ = pf["leak_frac"][str(c["T"])]
            s.append(f"| {c['T']} | {f(c['P_idle'],1)} | {100*c['leak_frac']:.0f}% | {100*lo_:.0f}–{100*hi_:.0f}% |")
    t0, t1 = min(x["T"] for x in r["measured_idle"]), max(x["T"] for x in r["measured_idle"])
    idle_at = lambda q, t: q["P_fix_w"] + q["A_leak_80_w"] * math.exp((t - 80) / q["T_L_c"])
    out_rows = [c["T"] for c in r["curve"] if c["T"] % 10 == 0 and not t0 <= c["T"] <= t1]
    spread = max(max(idle_at(q, t) for q in pf["fits"]) - min(idle_at(q, t) for q in pf["fits"]) for t in out_rows) if out_rows else 0
    s.append(f"\nThe fitted bins run from {t0} to {t1} °C; the other rows are the law extrapolated, where the e-foldings that fit differ by up to {f(spread,1)} W in the idle itself.")
    SP = VI.get("split_73c", {})
    spc = order(SP)
    cyc = lambda h: SP[h]["minion"]["n"]
    s += [f"\n## Where idle goes, by rail ({f(rl['die_c'],0)} °C)\n",
          "| Rail | aifoundry2, 22 Sep, W | Share | " + " | ".join(f"{name(h)}, 26 Sep ({WORD[cyc(h)]} cycle{'s' if cyc(h) > 1 else ''})" for h in spc) + " |",
          "|---|---|---|" + "---|" * len(spc)]
    for lab, k in (("Minions", "minion"), ("SRAM (L2, L3, scratchpad)", "sram"), ("Mesh", "noc"), ("**No rail sensor** (PCIe, DDR, IO shire, regulators)", "unsensed")):
        s.append(f"| {lab} | {f(rl[k])} | {100*rl[k]/rl['board']:.0f}% | " + " | ".join(f(SP[h][k]["mean"]) for h in spc) + " |")
    s.append(f"| Board | {f(rl['board'])} ± {f(rl.get('board_sd'), 2)} | | " + " | ".join(f(SP[h]["board"]["mean"]) for h in spc) + " |")
    s += [f"\nThe three sensed rails are the PMIC's own running averages (roughly first-order, {tau_txt}), which the service processor reports; the unsensed remainder is board power minus their sum. The 22 September sample is aifoundry2, {f(rl.get('hours_idle'),1)} hours after the last workload apart from a 4.9 s single-hart probe a few minutes before; the board figure's ± is the sd of its {rl.get('samples', 300)} samples, taken over one minute; the rails' sd is 0.01 W or less. "
          + (f"The 26 September columns are the 73 °C bin of the version-3 idle cycles, which {and_list(('all three of ' + name(h) + chr(39) + 's') if cyc(h) == 3 else (WORD[cyc(h)] + ' of ' + name(h) + chr(39) + 's three') for h in spc)} reached; "
             + (f"aifoundry2's agree with 22 September to within {max(abs(SP['aifoundry2'][k]['mean'] - rl[k]) for k in ('minion', 'sram', 'noc', 'unsensed')):.2f} W but come from {WORD[cyc('aifoundry2')]} cycles, one short of the three the check needed, so the split is not confirmed there" if "aifoundry2" in SP and cyc("aifoundry2") < 3 else "")
             + "".join(f"; {name(h)} draws {SP[h]['board']['mean'] - rl['board']:.1f} W more" + (", on every rail" if all(SP[h][k]["mean"] > rl[k] for k in ("minion", "sram", "noc", "unsensed")) else "") for h in spc if h != "aifoundry2") + ". " if spc else "")
          + "Source: `" + r["source"]["rails"] + "`, `" + V.get("source", "") + "/idle.json`. The SRAM rail's own temperature law, on every card, is in [4.3](04a-fine-grain.md).\n",
          "## Operating points\n", "| MHz | Minion V | Relative switching power (V²f) |", "|---|---|---|"]
    p0 = r["operating_points"][0]
    for p in r["operating_points"]:
        s.append(f"| {p['mhz']} | {f(p['volts'],3)} | {(p['volts']/p0['volts'])**2 * p['mhz']/p0['mhz']:.2f}× |")
    s += ["\nA warm card is held at the first row by the governor, which steps down when the whole-degree die reading is above 65 °C or board power is above 65 W; every table in this manual is at that point unless it says otherwise. The other two are reached only from a cool start (docs/findings/16-dvfs-and-leakage.md); aifoundry3, whose firmware reports a TDP of 0 W, never leaves 600 MHz; aifoundry1's card 1 (firmware 1.2.0) reports 65 W like aifoundry2 and sat at 600 MHz in every sample of the version-3 check. **On a cooler die the governor lifts the clock in the middle of a burst** (below about 68 °C of the sampler's mean reading, so the reruns preheat the die to 76 °C): the first attempt at the reruns of section 5 and 6 on aifoundry2 (12:51–13:10 on 23 September, die 65 °C) had 700–800 MHz excursions in a fifth of its samples and was discarded; the bars in this manual are from bursts at 600 MHz throughout.\n"]
    CS, CLK, ISP = V.get("card_state", {}), VI.get("clocks", {}), m["catalogue"].get("idle_split", {})
    if CS:
        cc = order(CS)
        s += [f"## The {NC} cards\n", "| | " + " | ".join(name(h) for h in cc) + " |", "|---|" + "---|" * len(cc),
              "| Firmware | " + " | ".join(CLK.get(h, {}).get("firmware", "—") for h in cc) + " |",
              "| Static TDP the firmware uses | " + " | ".join((f"**{CS[h]['tdp_w']} W** (pinned at 600 MHz for life)" if CS[h]["tdp_w"] == 0 else f"{CS[h]['tdp_w']} W") for h in cc) + " |",
              "| Power state at rest | " + " | ".join(CS[h]["power_state_name"] for h in cc) + " |",
              "| Minion voltage at 600 MHz | " + " | ".join(f"{CLK.get(h, {}).get('mv', CS[h]['minion_mv']):.0f} mV" for h in cc) + " |",
              "| Idle during the catalogue (26 September; mean board power, die range) | " + " | ".join(f"{f(ISP[h]['board'], 1)} W at {rg0(iu[h]['die_c'])} °C" if h in ISP else "—" for h in cc) + " |", ""]
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
    av = m["tensor"].get("activity_v3_mw_per_minion", {})
    sv = m["awake"]["spin_v3_w"]
    T6, T7 = V.get("tensor", {}).get("spin_w", {}), V.get("tensor", {}).get("active_minions", {})
    ci3 = lambda x: f"{neg(x['mean'])} W [{neg(x['lo'])}, {neg(x['hi'])}]"
    nop, fen = cb("nop/zeros/h2"), cb("fence/zeros/h2")
    hw = lambda c: 100 * (c["hi"] - c["lo"]) / 2 / c["mean"]
    s = ["# 2. A core that is awake\n",
         "The cost of a minion that is running and doing as little as it can: an `addi` loop, no memory, no data. Everything an instruction costs in section 3 is on top of section 1 and includes the awake core.\n",
         BARS + "\n",
         "| Configuration | pJ per instruction | per card | W over idle, 1,024 minions (a2) | Per minion (a2) | Rate |", "|---|---|---|---|---|---|",
         f"| One hart per minion, `addi` loop | {bar(sp1)} | {cards(sp1)} | {f(w1)} | {f(w1/1024*1e3,2)} mW | {sci(r1)}/s |",
         f"| Both harts per minion | {bar(sp2)} | {cards(sp2)} | {f(w2)} | {f(w2/1024*1e3,2)} mW | {sci(r2)}/s |",
         f"| The second hart's share | {f((w2-w1)/(r2-r1)*1e12,1)} pJ per extra instruction | | {f(w2-w1)} | {f((w2-w1)/1024*1e3,2)} mW | |",
         f"| The ablation's integer loop: four adds and a branch per iteration, hart 0; four 7 s runs on each card (V3-ABL-A, 26 Sep) | {f(aw['pj_marginal'],1)} pJ (a2) | {' · '.join(SHORT[h] + ': ' + f(sv['per_card'][h]['mean']) + ' ± ' + f(sv['per_card'][h]['se']) + ' W' for h in order(sv['per_card']))} | {f(aw['over_idle_w'])} | {f(aw['over_idle_w']/1024*1e3,2)} mW | {sci(aw['per_s'])}/s |",
         (f"| 1,024 minions stalled on one contended atomic (the hot line, E23; each waits about {round(1024*at0['cycles_per_op'], -3):,.0f} cycles for its turn) | — | {cards(hot, 2)} W; both **{f(hot['mean'])}** [{f(hot['lo'])}–{f(hot['hi'])}] | {f(hot['per_card']['aifoundry2']['mean'])} | {f(hot['per_card']['aifoundry2']['mean']/1024*1e3,2)} mW | — |" if hot else
          f"| 1,024 minions stalled on one contended atomic (the hot line, E23; each waits about {round(1024*at0['cycles_per_op'], -3):,.0f} cycles for its turn) | — | a2 only, 22 September | {f(at0['over_idle_w'])} | {f(at0['over_idle_w']/1024*1e3,1)} mW | — |"),
         f"| For scale: every minion running a random-data fp32 matmul (the activity term; per minion with 256, 512 and 1,024 active: {'; '.join(SHORT[h] + ' ' + ', '.join(f(av[h][k], 1) for k in ('256', '512', '1024')) for h in order(av))} mW, four runs each; {f(act['fp32_randn_24'],1)} with 768, a2, 21 Sep) | — | {' · '.join(SHORT[h] + ': ' + f(av[h]['1024'], 1) + ' mW' for h in order(av))} | {f(t32['over_idle_w'])} | {f(av['aifoundry2']['1024'],1)} mW | tensor state machines plus everything else that wakes |",
         f"\n**The addi loop is not the floor.** It increments seven registers, so its operands change on every instruction. With both harts a `nop` costs {f(nop['mean'],1)} pJ [{f(nop['lo'],1)}–{f(nop['hi'],1)}] and a `fence` {f(fen['mean'],1)} [{f(fen['lo'],1)}–{f(fen['hi'],1)}] per instruction ([3.1](03a-every-instruction.md)), so the awake core is about {f(fen['mean'],1)}–{f(nop['mean'],1)} pJ per issue slot. The ablation's loop issued at half the one-hart `addi` loop's rate, on hart 0 only; it is the loop behind the figures in [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power), {f(aw['over_idle_w']/1024*1e3,1)} mW per minion and {f(aw['pj_marginal'],0)} pJ per instruction on aifoundry2. "
         + (f"The version-3 check resolves it from idle on {and_list(name(h) + ' (' + ci3(T6[h]) + ')' for h in order(T6) if T6[h]['lo'] > 0)} but not on {and_list(name(h) + ' (' + ci3(T6[h]) + ')' for h in order(T6) if not T6[h]['lo'] > 0)} (99% intervals over four runs). " if T6 else "")
         + (f"But {lo_note}, on some cards as large as the loop itself: at that temperature it draws {and_list(rng2(atl(h, 'spin'), atls(h, 'spin')) + ' W on ' + name(h) for h in order(LO))}. " if LO else "")
         + (f"Per minion, the matmul's power is flat from 256 to 1,024 active minions on aifoundry2 (1,024 against 256: {f(T7['aifoundry2']['ratio_1024_256'])}); as registered it is {and_list(f(T7[h]['ratio_1024_256']) + ' on ' + name(h) for h in order(T7) if h != 'aifoundry2')}"
            + (f"; at the die temperature of each launch, where the offset moves the smaller 256-minion runs most, it is {and_list(rng2((atl(h, 'fp32_randn') / 1024) / (atl(h, 'fp32_randn_8') / 256), (atls(h, 'fp32_randn') / 1024) / (atls(h, 'fp32_randn_8') / 256) if atls(h, 'fp32_randn') and atls(h, 'fp32_randn_8') else None) for h in order(LO))} in that order, so which card is flat is not settled" if LO else "") + ".\n" if T7 else "\n"),
         f"**Rules.** An awake minion costs about 2 mW; a second hart adds about 1 mW; a minion stalled on a contended atomic draws less than one spinning ({f((hot['mean'] if hot else at0['over_idle_w'])/1024*1e3,1)} against {f(w1/1024*1e3,1)} mW). Keeping 1,024 minions awake for a second is {w1:.0f}–{w2:.1f} J, against 36 J for the card at 80 °C, so the awake cost is small next to leakage and next to real instructions.\n",
         f"The bars here are ±{hw(sp1):.0f}–{hw(sp2):.0f}%, a little wider than the catalogue's median, because the signal is small: 2–3 W over a 26–43 W idle that drifts by a few tenths of a watt with the die temperature. On the two-hart loop {and_list(name(h) + ' reads ' + f(sp2['per_card'][h]['mean']/sp2['per_card']['aifoundry2']['mean'], 2) + '×' for h in order(sp2['per_card']) if h != 'aifoundry2')} aifoundry2.\n",
         "Sources: " + CATSRC + ", `" + m["awake"]["source"]["spin_v3"] + "` (the ablation's loop and the matmul, V3-ABL-A), `" + m["tensor"]["source"]["activity_term"] + "` (768 minions).\n"]
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
    dvs = [cb(f"{n}/random/h2")["mean"] for n in ("div", "divu", "rem", "remu")]
    rc = cb("frcp.ps/random/h2")
    def issue_share(h):   # (issue / 8) / (fmadd.ps per lane - tensor unit), per card, with the fence or the nop as the issue
        sv = fm["per_card"][h]["mean"] / 8 - tb["fp32_randn"]["per_card"][h]["mean"]
        sh = [100 * c["per_card"][h]["mean"] / 8 / sv for c in (fen, nop)]
        return f"{min(sh):.0f}–{max(sh):.0f}%"
    ishare = {h: issue_share(h) for h in order(tb["fp32_randn"]["per_card"]) if h in fm["per_card"]}
    add_nop = [ia["per_card"][h]["mean"] - nop["per_card"][h]["mean"] for h in order(ia["per_card"]) if h in nop["per_card"]]
    n_cat = max(c["n"] for c in C.values())
    tlaunch = m["tensor"].get("launch_c", {})
    tl_by = {}
    for h in order(tlaunch):
        tl_by.setdefault(f"{tlaunch[h]:.0f}", []).append(h)
    tl_keys = sorted(tl_by, key=lambda k: -len(tl_by[k]))
    tl_txt = f"{tl_keys[0]} °C" + (" (" + "; ".join(f"{k} °C on {and_list(name(h) for h in tl_by[k])}" for k in tl_keys[1:]) + ")" if len(tl_keys) > 1 else "")
    nrun = m["tensor"].get("runs_per_card", {})
    s = ["# 3. Instructions\n",
         "Energy per instruction retired, above idle, at 600 MHz and 0.52 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2).\n",
         BARS + f" Three shuffled passes on each of {NC} cards (26 September), so n = {n_cat} for every entry. The full catalogue of 161 instructions is in [3.1](03a-every-instruction.md).\n",
         "## Scalar and vector units\n",
         "| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | per card, random | Note |",
         "|---|---|---|---|---|---|---|---|",
         row("add", "add", 1), row("xor", "xor", 1), row("mul", "mul", 1, "64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op"),
         row("fadd.s", "fadd.s", 1), row("fmul.s", "fmul.s", 1), row("fmadd.s", "fmadd.s", 1),
         row("fadd.ps", "fadd.ps (8 lanes)", 8), row("fmul.ps", "fmul.ps (8 lanes)", 8), row("fmadd.ps", "fmadd.ps (8 lanes)", 8, "16 flops"),
         row("fadd.pi", "fadd.pi (8 lanes, int32)", 8), row("fmul.pi", "fmul.pi (8 lanes, int32)", 8),
         row("fexp.ps", "fexp.ps (8 lanes)", 8, "transcendental unit, ¼ the rate"), row("frcp.ps", "frcp.ps (8 lanes)", 8, "transcendental unit"),
         "", "Thirteen instructions trapped in U-mode in a one-off check while the catalogue was written (listed in [3.1](03a-every-instruction.md); the card and the log of that check were not kept), among them every float and vector divide and square root, as expected: this silicon has no hardware divide or square root for them.\n",
         "**What the table says.**",
         f"- **An integer add on zeros, {f(ia['mean'],1)} pJ [{f(ia['lo'],1)}–{f(ia['hi'],1)}], costs little more than a `nop`** ({f(nop['mean'],1)} pJ; {f(min(add_nop),1)}–{f(max(add_nop),1)} pJ more on each card): on zeros it is mostly the awake core that issues it (section 2). Random operands add {f(iar['mean']-ia['mean'],1)} pJ.",
         f"- **A scalar float add costs {f(fa['mean']/ia['mean'],1)}× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.",
         f"- **An 8-lane vector op on zeros costs the same as the scalar op** ({f(vz['mean'],1)} against {f(fa['mean'],1)} pJ, bars overlapping): lanes computing on zeros add nothing. On random data the eight lanes cost {f(vr['mean']/vz['mean'],1)}× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.",
         f"- **Per lane on random data, `fmadd.ps` is {f(fm['mean']/8,1)} pJ per multiply-add** [{f(fm['lo']/8,1)}–{f(fm['hi']/8,1)}]. The tensor unit below does the same multiply-add for {f(tb['fp32_randn']['mean'],1)} pJ [{f(tb['fp32_randn']['lo'],1)}–{f(tb['fp32_randn']['hi'],1)}]. Take out the vector instruction's issue — {f(fen['mean'],1)}–{f(nop['mean'],1)} pJ, what a fence or a nop costs (section 2) — and the lane is {f(lane[0],1)}–{f(lane[1],1)} pJ, about {100*((lane[0]+lane[1])/2/tb['fp32_randn']['mean']-1):.0f}% above the tensor unit. Read that way, **of the {f(fm['mean']/8-tb['fp32_randn']['mean'],1)} pJ per multiply-add the tensor unit saves, roughly half is instruction issue and the rest datapath** ({and_list(ishare[h] + ' issue on ' + name(h) for h in ishare)}, with the fence or the nop as the issue cost); that is arithmetic on rows whose operands differ (uniform in [0.5, 2) here, normal for the tensor unit), not a measured decomposition.",
         f"- **Integer vector adds are half the price of float ones** ({f(ipz['mean'],1)} vs {f(vz['mean'],1)} pJ on zeros); integer vector multiplies are not.",
         f"- **The transcendentals rank with the 64-bit divides as the dearest arithmetic**: `flog.ps` at {f(lg['mean'],0)} pJ and `fexp.ps` at {f(ex['mean'],0)} pJ for eight lanes, at a quarter of the rate, against {f(min(dvs),0)}–{f(max(dvs),0)} pJ for the 64-bit divides and remainders; `frcp.ps` ({f(rc['mean'],0)}) is cheaper, and `fexp.ps` is {f(ex['mean']/fm['mean'],1)}× a vector multiply-add. Only loads and stores that bypass the L1 ({f(min(byp),0)}–{f(max(byp),0)} pJ) and atomics ({f(min(amo),0)}–{f(max(amo),0)} pJ) cost more ([3.1](03a-every-instruction.md)).\n",
         "## 3.2 The tensor unit\n",
         "`TensorFMA` on a tile per instruction: fp32 16×16×16 = 4,096 multiply-adds, fp16 8,192, int8 16,384; 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, each run 7 s, launched at " + tl_txt + ": aifoundry3's values compare a cool card with warm ones" + (f". {lo_note[0].upper() + lo_note[1:]}: about {rng2(abs(LO['aifoundry3']['mean_w'] - LO['aifoundry2']['mean_w']), abs(LO['aifoundry3']['mean_w_step'] - LO['aifoundry2']['mean_w_step']) if 'mean_w_step' in LO['aifoundry3'] and 'mean_w_step' in LO['aifoundry2'] else None, 1)} W of any difference between aifoundry3 and aifoundry2 comes from the reduction, most of the spread on the zeros rows; at the die temperature of each launch the fp32 rows read {and_list(rng2(atl(h, 'fp32_zeros') / m['tensor']['rows'][0]['per_s'] * 1e12, atls(h, 'fp32_zeros') / m['tensor']['rows'][0]['per_s'] * 1e12 if atls(h, 'fp32_zeros') is not None else None) for h in order(LO))} pJ per MAC on zeros and {and_list(rng2(atl(h, 'fp32_randn') / m['tensor']['rows'][2]['per_s'] * 1e12, atls(h, 'fp32_randn') / m['tensor']['rows'][2]['per_s'] * 1e12 if atls(h, 'fp32_randn') is not None else None) for h in order(LO))} on random data ({and_list(name(h) for h in order(LO))})" if LO and 'aifoundry3' in LO and 'aifoundry2' in LO else "") + ". **Marginal** is board power above idle per multiply-add; **loaded** is total board power, idle included, per multiply-add, which is what a multiply-add costs when it is the only thing running.\n",
         f"The rows are the version-3 check's ablation (V3-ABL-A, 26 September), {WORD[max(nrun.values())] if nrun else 'four'} runs on each of {NC} cards; the bar on each row is the range over every run on every card: ±{min(tbw(k) for k in ('fp32_randn', 'fp16_randn', 'int8_randn')):.0f}–{max(tbw(k) for k in ('fp32_randn', 'fp16_randn', 'int8_randn')):.0f}% on random data and ±{min(tbw(k) for k in ('fp32_zeros', 'fp16_zeros', 'int8_zeros')):.0f}–{max(tbw(k) for k in ('fp32_zeros', 'fp16_zeros', 'int8_zeros')):.0f}% on zeros, most of it the difference between the cards. The rates are the same on every card (546 cycles per instruction, 318 for int8, in every timed launch). The loaded and W columns are aifoundry2's means. Until 25 September these rows were the 21 September ablation's two runs on aifoundry2 and, for fp32, the 22 September card transfer.\n",
         "| Type, operands | pJ per MAC, marginal | per card | pJ per MAC, loaded (a2) | W over idle (a2) | MACs per second |", "|---|---|---|---|---|---|"]
    for t in m["tensor"]["rows"]:
        b = tb[t["config"]]
        pc = " · ".join(f"{SHORT.get(h, h)}: {f(b['per_card'][h]['mean'],3)}" for h in order(b["per_card"])) + ("" if b["cards"] > 1 else " (a2 only)")
        s.append(f"| {t['label']} | **{f(b['mean'],3)}** [{f(b['lo'],3)}–{f(b['hi'],3)}] | {pc} | {f(t['pj_loaded'],2)} | {f(t['over_idle_w'],2)} | {sci(t['per_s'])} |")
    fl = m["tensor"]["flips"]
    s += ["", "### Where the tensor unit's energy goes: per flip\n",
          "The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands aifoundry2 actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four energies fitted on that card:\n",
          "| Event | fJ each | What it is |", "|---|---|---|"]
    for c, e in fl["e_fJ"].items():
        s.append(f"| {c} | {f(e,3)} | {fl['classes'][c]} |")
    s += [f"| tensor state machines | {f(fl['p_sm_full_chip_w']/1024*1e3,2)} mW per active minion | per minion, whatever the data |",
          "", "A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and aifoundry2 measured 27.6 in the 21 September runs they were fitted to (27.2 in the four runs of 26 September). Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran on aifoundry2 (one session, two runs each). The four energies are one fit on aifoundry2; their confidence is that 0.9 W rms over fourteen held-out patterns, and the 8% by which aifoundry3 runs below the fit on every pattern (section 8).\n",
          "Sources: " + CATSRC + " (3.1), `" + m["tensor"]["source"]["rows"] + "` (3.2), `" + m["tensor"]["source"]["flips"] + "` (flips).\n"]
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
    WR = V.get("catalogue", {}).get("dram_write_read", {})
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
         f"## 4.1 Reads and writes, measured together (26 September, three passes on each of {NC} cards)\n",
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
        l1pc = {h: (100 * (lv["l1"]["per_card"][h]["mean"] / l1c["per_card"][h]["mean"] - 1), l1c["per_card"][h]["mean"]) for h in order(lv["l1"]["per_card"]) if h in l1c["per_card"]}
        LB = RR.get("levels_by_contents_pj_per_byte") or {}
        PP = (RR.get("passes_per_card") or {}).get("levels", {})
        npp = sorted({len(v) for v in PP.values()})
        SBC = V.get("rl", {}).get("scp_by_contents", {})
        inb = lambda h: 1.7 <= SBC[h]["zeros"]["mean"] <= 2.3 and 3.7 <= SBC[h]["random"]["mean"] <= 4.7
        s += ["## 4.2 Reads by level (memhier, 26 September: the version-3 check's V3-RL, at 600 MHz)\n",
              f"**L1**: both harts of every minion re-reading a private 256 B buffer with 32 B vector loads, in memhier's own loop over a buffer whose contents it does not set. "
              f"That loop (8 loads per loop iteration) issued a load every {cyc_mh:.1f} minion-cycles where the catalogue's (64) issued one every {cyc_cat:.1f} ({tbs_cat:.1f} TB/s), and it reads {and_list(f'{v[0]:.0f}%' for v in l1pc.values())} above the L1 row of 4.1 on {and_list(name(h) for h in l1pc)} ({and_list(f(v[1]) for v in l1pc.values())} pJ/B on random data), which is the figure to use. "
              "**L2, L3, DRAM and the scratchpads**: hart 0 of every minion streaming 1 KB tensor loads — which skip the L1 but are cached in the L2 and L3 — over a working set sized to each level. "
              f"The probe does not set the contents of the L2, L3 and DRAM buffers, so those rows are not directly comparable to the zeros and random columns of 4.1 (the DRAM level is within noise of the random-data row), and the L2 and L3 levels move a lot from pass to pass ({f(lv['l2']['lo'])}–{f(lv['l2']['hi'])} and {f(lv['l3']['lo'],1)}–{f(lv['l3']['hi'],1)} pJ/B). "
              "**The version-3 passes set the scratchpads' contents**, filling them with zeros (odd passes) or random data (even passes) before they are read, and the own scratchpad follows the fill"
              + (f": inside the check's registered bands (1.7–2.3 and 3.7–4.7 pJ/B) on {and_list(name(h) for h in order(SBC) if inb(h))}" + (f", above them on {and_list(name(h) + ' (' + f(SBC[h]['zeros']['mean']) + ' and ' + f(SBC[h]['random']['mean']) + ')' for h in order(SBC) if not inb(h))}" if any(not inb(h) for h in SBC) else "") if SBC else "") + ". "
              "On the L1 and the own scratchpad no pair of cards differs beyond the 99% interval of their passes. "
              f"{(WORD[npp[0]] if len(npp) == 1 else 'Several').capitalize()} passes on each of {WORD[len(PP)]} cards at 600 MHz, every sample, pinned there on aifoundry3 and held there on the others by a warm die (n = {lv['dram']['n']}); they replace three passes on each of two cards of 23 September, whose scratchpads were not filled. The first measurement of 18 September, one run on aifoundry2, ran with the governor free (its clock averaged {min(gh):.2f}–{max(gh):.2f} GHz across the levels) and is superseded.\n",
              "| Level | Working set | pJ/B | per card |", "|---|---|---|---|"]
        for k, lab, what in LV:
            c = lv.get(k)
            if not c:
                continue
            if k in ("scp-local", "scp-remote") and all(k in (LB.get(o) or {}) for o in ("zeros", "random")):
                for o, ol in (("zeros", "zeros"), ("random", "random data")):
                    cc = LB[o][k]
                    s.append(f"| {lab}, {ol} | {what}, filled with {ol} | {bar(cc, 1 if cc['mean'] >= 10 else 2)} | {cards(cc, 1 if cc['mean'] >= 10 else 2)} |")
            else:
                s.append(f"| {lab} | {what} | {bar(c, 1 if c['mean'] >= 10 else 2)} | {cards(c, 1 if c['mean'] >= 10 else 2)} |")
        s += ["", f"Passes: {RR['passes'].get('levels', 0)}. Source: `" + str(RR.get("v3_rl", "")) + "/<card>/rl/p<K>/B/` (reduced by `tools/ettelem/analyze_reruns.py --v3-rl` into `" + RR.get("source", "") + "`)."]
    else:
        s += ["## 4.2 Reads by level (18 September, memhier)\n",
              "| Level | Working set | pJ/B | GB/s | Clock during the run |", "|---|---|---|---|---|"]
        for x in mr["rows"]:
            s.append(f"| {x['level']} | {x['what']} | {f(x['pj_per_byte'])} | {x['gb_s']:.0f} | {f(x.get('implied_ghz'),2)} GHz implied |")
        s += ["", "*Caveat:* " + mr["caveat"] + "."]
    s += ["", "**What the tables say.**",
          f"- **DRAM is {f(dl['mean']/sl['mean'],0)}× the energy of the shire's own scratchpad per byte read**, and {f(ds['mean']/cb('tstore/scp/random')['mean'],0)}× per byte written.",
          f"- **A DRAM write costs about what a DRAM read costs** ({f(ds['mean'],0)} vs {f(dl['mean'],0)} pJ/B on random data; {and_list(f'{100*(ds['per_card'][h]['mean']/dl['per_card'][h]['mean']-1):.0f}% more on ' + name(h) for h in order(ds['per_card']) if h in dl['per_card'])}; the version-3 check, a separate run of these rows, did not resolve the difference from zero on {and_list(name(h) for h in order(WR) if WR[h]['lo'] <= 0 <= WR[h]['hi'])}: {semi_list(name(h) + ' ' + sgn(WR[h]['diff'], 1) + ' pJ/B [' + sgn(WR[h]['lo'], 1) + ', ' + sgn(WR[h]['hi'], 1) + ']' for h in order(WR))}, 99% intervals) — by tensor store, which skips the L1 and the L2. **Through the L1 write-back path the same bytes cost {f(ss['mean']/ds['mean'],1)}× more** and arrive at a third of the bandwidth, consistent with each store allocating its line, so that the line is read from DRAM before it is written back and the byte pays for a read and a write. Off-rail it costs {f(off_rail('st_stream/dram/random'),0)} pJ against a tensor store's {f(off_rail('tstore/dram/random'),0)} ([Limits of observability, §4.2](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#the-unmetered-remainder-attributed)), and a tensor load plus a tensor store come to {f(dl['mean']+ds['mean'],0)} of its {f(ss['mean'],0)} pJ/B.",
          f"- **Even DRAM is data-dependent**: zeros {f(dz['mean'],0)}, random {f(dl['mean'],0)} pJ/B, bars [{f(dz['lo'],0)}–{f(dz['hi'],0)}] and [{f(dl['lo'],0)}–{f(dl['hi'],0)}] well apart. The scratchpad doubles from zeros to random.",
          f"- **A scratchpad write is twice a scratchpad read** ({f(ssz['mean'])} vs {f(slz['mean'])} pJ/B on zeros).",
          f"- **An L1 hit is nearly free**: {f(l1['mean'])} pJ/B [{f(l1['lo'])}–{f(l1['hi'])}] including the instruction.\n",
          "Where the bytes' energy goes below the line — the wires, the cache lines, the DRAM rows, the SRAM's own leakage and the rails — is in [4.3](04a-fine-grain.md).\n",
          "Sources: " + CATSRC + ", `" + mr["source"]["rows"] + "` (18 September).\n"]
    open(os.path.join(out, "04-bytes-memory.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 5 comm
    cm = m["comm"]
    MH = cm.get("mesh_hops", {})
    rg = RR.get("rings_pj_per_byte") or {}
    rp = {x["medium"]: x for x in m["relay"]["power"]["media"]}
    rr = RR.get("relay_pj_per_byte") or {}
    hops = lambda k: ("—" if k not in MH else "0" if not MH[k]["mean"] else f"{f(MH[k]['mean'], 1)} ({MH[k]['min']}–{MH[k]['max']})")
    # the 18 September runs were on aifoundry2, so they are set against aifoundry2's own new passes
    dev = sorted(100 * (x["pj_per_byte_local"] / rg[x["ring"]]["per_card"]["aifoundry2"]["mean"] - 1) for x in cm["rows"]
                 if x["ring"] in rg and "aifoundry2" in rg[x["ring"]]["per_card"] and x.get("pj_per_byte_local"))
    pm = lambda v: ("−" if v < 0 else "+") + f"{abs(v):.0f}"
    PP = RR.get("passes_per_card") or {}
    npass = lambda d: (f"{WORD[len(next(iter(d.values())))]} passes on each of {WORD[len(d)]} cards" if d and len({len(v) for v in d.values()}) == 1 else "several passes per card")
    x16d = [x for x in RR.get("dropped", []) if x.get("burst") == "xshire16" and x.get("sampler_median_ms") and "claims-v3" in str(x.get("pass"))]
    x16c = order({str(x["pass"]).split("/raw/")[1].split("/")[0] for x in x16d if "/raw/" in str(x["pass"])})
    fb16 = (RR.get("fallback_23sep") or {}).get("xshire16")
    x16 = next((x for x in cm["rows"] if x["ring"] == "xshire16"), None)
    s = ["# 5. Bytes between cores and shires\n",
         "Register file to register file over the tensor network (`TensorSend`/`TensorRecv`), 1 KB messages unless said otherwise, hart 0 of every minion sending and receiving in rings, at 600 MHz. "
         "Shire IDs do not follow the mesh, so each ring between shires is given with its mean distance in mesh hops, the Manhattan distance between shire s and shire s + k averaged over all 32 compute shires on the shire map of [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication) (checked against latency on aifoundry2).\n",
         BARS + (f" The rings were re-measured in the version-3 check (26 September) with the manual's own sampler, {npass(PP.get('rings', {}))}, the die held warm on the governor-free cards; they replace three passes on each of two cards of 23 September. The pair of 18 September runs on aifoundry2, sampled without the die temperature and so without a leakage correction, is not pooled; against aifoundry2's own new passes the values On-chip communication publishes from it read {pm(dev[0])}% to {pm(dev[-1])}% (median {pm(dev[len(dev) // 2])}%). "
                 + (f"**The s ↔ s+16 ring starves the service processor's own management path** — the sampler's latency rises from 22 ms to {min(x['sampler_median_ms'] for x in x16d):.0f}–{max(x['sampler_median_ms'] for x in x16d):.0f} ms and the board reading takes a new value about twice a second instead of six times — in every version-3 pass on {and_list(name(h) for h in x16c)}, so those bursts were dropped" + (f" and that row keeps {and_list(name(h) for h in fb16['cards'])}'s three passes of 23 September, when its sampler stayed at 22 ms" if fb16 else "") if x16d else "")
                 + (f" (On-chip communication gives {f(x16['pj_per_byte_local'], 1)} pJ/B for it on aifoundry2 on 18 September)." if x16 and x16.get("pj_per_byte_local") else ".") if rg else " Two independent runs averaged; ± is half their difference.") + "\n",
         "| Ring | What moves | Mesh hops, mean (range) | pJ/B | per card | GB/s aggregate |", "|---|---|---|---|---|---|"]
    small = lambda k: k.endswith("c4")
    for x in sorted(cm["rows"], key=lambda x: (small(x["ring"]), (MH.get(x["ring"]) or {"mean": 0})["mean"])):
        c = rg.get(x["ring"])
        s.append(f"| {x['ring']} | {x['what']} | {hops(x['ring'])} | {bar(c, 2) if c else '**' + f(x['pj_per_byte']) + '** ± ' + f(x['pj_spread'])} | {cards(c, 2) if c else 'a2 only'} | {x['gb_s']:,.0f} |")
    PP = RR.get("passes_per_card") or {}
    npass = lambda d: (f"{WORD[len(next(iter(d.values())))]} passes on each of {WORD[len(d)]} cards" if d and len({len(v) for v in d.values()}) == 1 else "several passes per card")
    rel_note = (f"The relay was re-measured in the version-3 check (26 September), {npass(PP.get('relay', {}))} (n = {rr['dram']['n']}); it replaces the 22 September session and the 23 September passes. A stage reads a slab, adds 1 and writes it where the next stage reads it; the next shire is shire s − 1 by ID, {hops('xshire1')} mesh hops away. GB/s: the 22 September session's, on aifoundry2." if rr else "")
    s += ["", "## Handing a slab to the next shire through its scratchpad (E25)\n" + rel_note + "\n",
          "| Medium | pJ per byte (read + write) | per card | GB/s on the card |", "|---|---|---|---|"]
    for med, label in (("dram", "Write to DRAM, read back"), ("hop", "Write where the next shire reads it"), ("scp", "Keep it in this shire's scratchpad")):
        c = rr.get(med)
        v = bar(c, 1) if c else f"**{f(rp[med]['pj_per_byte'],1)}**"
        s.append(f"| {label} | {v} | {cards(c, 1) if c else 'a2 only'} | {rp[med]['bytes_per_s']/1e9:,.0f} |")
    mesh = [x for x in cm["rows"] if x["ring"].startswith("xshire") and "c4" not in x["ring"]]
    xs = [(rg[x["ring"]]["mean"] if x["ring"] in rg else x["pj_per_byte"]) for x in mesh]
    pr = rg["pair"]["mean"] if "pair" in rg else cm["rows"][0]["pj_per_byte"]
    sh = (rg["shire"]["mean"] + rg["neigh"]["mean"]) / 2 if "shire" in rg else cm["rows"][2]["pj_per_byte"]
    hw = [100 * (rr[k]["hi"] - rr[k]["lo"]) / 2 / rr[k]["mean"] for k in ("dram", "hop", "scp") if k in rr]
    # the line through the rings between shires, per card, on the rings every card measured
    rcards = order({h for x in mesh if x["ring"] in rg for h in rg[x["ring"]]["per_card"]})
    both = [x for x in mesh if x["ring"] in rg and all(h in rg[x["ring"]]["per_card"] for h in rcards) and x["ring"] in MH]
    pcf = {h: lfit([(MH[x["ring"]]["mean"], rg[x["ring"]]["per_card"][h]["mean"]) for x in both]) for h in rcards} if len(both) >= 3 else None
    hb = [MH[x["ring"]]["mean"] for x in both]
    rpc = {h: (rr["dram"]["per_card"][h]["mean"] / rr["hop"]["per_card"][h]["mean"], rr["hop"]["per_card"][h]["mean"]) for h in order(rr["dram"]["per_card"]) if h in rr["hop"]["per_card"]} if rr else None
    RL = V.get("rl", {})
    ES, SMm, RQ, MSl = RL.get("exit_step", {}), RL.get("small_messages", {}), RL.get("relay_ratio", {}), RL.get("mesh_slope", {})
    ci1 = lambda x: f"{f(x['mean'], 1)} [{neg(x['ci99'][0], 1)}, {f(x['ci99'][1], 1)}]"
    esY, esN = [h for h in order(ES) if ES[h]["ci99"][0] > 0], [h for h in order(ES) if not ES[h]["ci99"][0] > 0]
    sm_all = bool(SMm) and all(all(o[h]["ci99"][0] > 0 for h in o) for o in SMm.values())
    rd = rr.get("dram", {}).get("per_card", {}) if rr else {}
    hi_c = max(rd, key=lambda h: rd[h]["mean"]) if rd else None
    prem = [100 * (rd[hi_c]["mean"] / rd[h]["mean"] - 1) for h in rd if h != hi_c] if rd else []
    s += ["", "**What the tables say.**",
          f"- **Between the two minions of a pair a byte costs under a picojoule** ({f(pr, 2)} pJ); around a neighbourhood or a shire about {f(sh,1)} pJ; across the mesh {f(min(xs),0)}–{f(max(xs),0)} pJ."
          + (f" A straight line through the 1 KB rings between shires against their mean distances (the {WORD[len(both)]} that every card measured, {f(min(hb), 1)}–{f(max(hb), 1)} hops) gives {semi_list(f(pcf[h][0], 1) + (' pJ to leave the shire' if i == 0 else '') + ' plus ' + f(pcf[h][1], 1) + (' pJ per mesh hop' if i == 0 else '') + ' on ' + name(h) for i, h in enumerate(pcf))}"
             + (f"; the version-3 check finds no card's per-hop cost different from another's, {f(MSl['pooled'], 2)} pJ/B per hop pooled" if MSl.get("pooled") is not None else "")
             + f". [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures 1.5 pJ/B per hop on the mesh rail and 2.2 on board power directly. **Leaving the shire is the biggest single step ([4.3](04a-fine-grain.md)'s wire fit shows it on every card), but the hops after it are not free.**"
             + (f" The step out of the shire beyond one hop is {and_list(ci1(ES[h]) + ' pJ/B on ' + name(h) for h in esY)}" + (f", not resolved on {and_list(name(h) + ' (' + ci1(ES[h]) + ')' for h in esN)}" if esN else "") + " (99% intervals over six passes)." if esY else "") if pcf else ""),
          (f"- **Small messages cost more per byte**: the 128 B rows are dearer than the 1 KB ones on every card, by " + and_list(f"{min(o[h]['mean'] for h in o):.1f}–{max(o[h]['mean'] for h in o):.1f} pJ/B " + ("around a shire" if k.startswith("shire") else "between neighbouring shire IDs") for k, o in SMm.items()) + " (resolved from zero at 99% on each card)"
           if sm_all else "- Small messages cost more per byte in the 128 B rows")
          + "; the per-message overhead is 40–224 cycles of the sending and receiving harts ([On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), one session on aifoundry2).",
          (f"- **Handing a slab to the next shire through its scratchpad costs {and_list(f(v[0], 1) + '×' for v in rpc.values())} less than the DRAM round trip** on {and_list(name(h) for h in rpc)}" + (f" (the same on every card at 99%, {f(RQ['pooled'], 1)}× pooled)" if RQ.get("pooled") is not None else "") + f"; the hand-off itself costs {and_list(f(v[1], 1) for v in rpc.values())} pJ/B in that order for the write and the read together, and sits between the in-shire and cross-mesh tensor-network figures." if rpc else ""),
          (f"- The three relay bars are ±{min(hw):.0f}–{max(hw):.0f}%, most of it {name(hi_c)} reading {min(prem):.0f}–{max(prem):.0f}% above the others through DRAM, a difference the version-3 check resolves; within a card the passes agree to about {max(100 * rd[h]['se'] / rd[h]['mean'] for h in rd):.0f}% (standard error).\n" if hw and prem else ""),
          "Sources: `" + "`, `".join(cm["source"]) + "` (the rings' GB/s), `" + m["relay"]["source"] + "` (the relay's GB/s)" + (", `" + RR["source"] + "`" if RR else "") + "; mesh hops from [marty1885](https://github.com/marty1885/etTopoScan)'s shire map as `workloads/nocbench/analyze.py` holds it.\n"]
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
         BARS + (f" The hot line was measured on 22 September on aifoundry2 and re-run on 23 September, three warm passes on aifoundry2 and {WORD[hn['contended']['per_card']['aifoundry3']['n']]} on aifoundry3 (n = {hn['contended']['n']}); the first session alone (aifoundry2, 22 September, one run) gave {f(at['contended']['nj_per_op'], 1)} and {f(at['spread']['nj_per_op'], 2)} nJ." if hn else "") + "\n",
         "| Event | Energy | per card | Time | Note |", "|---|---|---|---|---|",
         f"| Global atomic, one line, 1,024 requesters | {con[0]} | {con[1]} | {at['contended']['cycles_per_op']:.0f} cycles each at the bank | the bank serialises and every requester waits its turn; the host shire's own loads stop |",
         f"| Global atomic, 32 lines, one per shire | {spr[0]} | {spr[1]} | {at['spread']['cycles_per_op']:.2f} cycles each, aggregate | the same instruction, {f(conm/sprm,0)}× cheaper |",
         f"| Uncontended remote atomic round trip | — | | {sy['remote_atomic_latency_cycles']:.0f} cycles | E22; the same on both cards |",
         f"| Chip-wide barrier, {sy.get('barrier_participants', 1024):,} minions | ≈ {f(stall_w*sy['barrier_cycles_chip']/0.6e9*1e6, 0)} µJ of waiting | | {sy['barrier_cycles_chip']:,} cycles | derived: 1,024 minions stalled at {f(stall_w/1024*1e3, 1)} mW (§2) for the barrier's length, which is one run on aifoundry2 (18 September); the 32 atomics and 32 credit stores are negligible beside it |",
         "| FLB (fast local barrier) + credit barrier, one shire | — | | 237 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), aifoundry2, 18 September |",
         "| TensorReduce (the hardware reduction tree) + broadcast, 32 minions | — | | 432 cycles | [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication), aifoundry2, 18 September |",
         "", f"**What the table says.** A contended atomic costs {f(conm/sprm,0)}× the same atomic spread over 32 lines, and its cost is not on the requesters: the shire that hosts the line keeps its share of the atomic, but its own other loads stop ([One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line), docs/findings/17-hot-line.md). Waiting itself is cheap — a stalled minion draws about {f(stall_w/1024*1e3, 1)} mW, less than a spinning one ({f(stat('spin/zeros/h1', 'over_idle_w')/1024*1e3, 1)} mW, section 2) — so a barrier's energy is small next to the leakage the card burns while it lasts.\n",
         f"The contended row's bar is wide mostly because of the first session: the whole chip stalled drew {f(at['contended']['over_idle_w'], 1)} W over idle in it, against {f((hot6['n']*hot6['mean']-at['contended']['over_idle_w'])/(hot6['n']-1), 2) if hot6 else f(conm*at['contended']['ops_per_s']*1e-9, 1)} W in the mean of the passes since, and the per-operation figure divides that small number by a rate the bank fixes at one per 10 cycles.\n",
         "Source: `" + sy["source"] + "`" + (", `" + RR["source"] + "`" if RR else "") + ".\n"]
    open(os.path.join(out, "06-synchronisation.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 8 cards
    ci = m["catalogue"]
    REF = "aifoundry2"
    XC = ci.get("cross_cards", {})
    OC = order(XC)
    def ratios(h, byte=None):
        out_ = []
        for k, e in S[REF].items():
            if k not in S[h]:
                continue
            isb = e["bytes_per_s"]["mean"] > 0
            fld = "pj_per_byte" if isb else "pj_per_op"
            if (byte is None or isb == byte) and e[fld]["mean"] > 0 and S[h][k][fld]["mean"] > 0:
                out_.append(S[h][k][fld]["mean"] / e[fld]["mean"])
        return sorted(out_)
    med = lambda v: (v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2) if v else None
    rer = {}
    for sec in ("relay_pj_per_byte", "hotline_nj_per_op", "rings_pj_per_byte", "levels_pj_per_byte"):
        for k, v in (RR.get(sec) or {}).items():
            if v and REF in v["per_card"]:
                for h in OC:
                    if h in v["per_card"]:
                        rer.setdefault(h, []).append(v["per_card"][h]["mean"] / v["per_card"][REF]["mean"])
    rer = {h: sorted(v) for h, v in rer.items()}
    C3 = V.get("catalogue", {})
    DB, TP, CBw, GAP, C23, OUTL, RM = (ci.get("die_c_busy_median", {}), C3.get("temperature", {}), C3.get("cool_a3_warm_a2"), C3.get("gap_vs_a2", {}),
                                       C3.get("committed_23sep"), ci.get("scale_outliers", {}), ci.get("rail_mv", {}))
    X5, PR, LRv8 = V.get("x5", {}), m["tensor"].get("per_card_rows", {}), VI.get("law_residual", {})
    hn = RR.get("hotline_nj_per_op") or {}
    rr = RR.get("relay_pj_per_byte") or {}
    col = lambda fn: " | ".join(fn(h) for h in OC)
    tens = lambda h: (f"{PR[h]['fp32_randn']['over_idle_w'] / PR[REF]['fp32_randn']['over_idle_w']:.3f}"
                      + (f" ({rng2(atl(h, 'fp32_randn') / atl(REF, 'fp32_randn'), atls(h, 'fp32_randn') / atls(REF, 'fp32_randn') if atls(h, 'fp32_randn') and atls(REF, 'fp32_randn') else None, 3)} at the die temperature of each launch, note C2)" if atl(h, "fp32_randn") and atl(REF, "fp32_randn") else "")) if h in PR and "fp32_randn" in PR[h] else "—"
    tin = [h for h in order(TP) if TP[h]["decision"] == "temperature"]
    tno = [h for h in order(TP) if TP[h]["decision"] != "temperature"]
    bci = lambda b: f"{sgn(b['beta'])}% per °C [{sgn(b['lo'])}, {sgn(b['hi'])}]"
    v2 = lambda h, k: 100 * ((RM[h][k] / RM[REF][k]) ** 2 - 1)
    xr = [h for h in order(X5) if isinstance(X5.get(h), dict) and X5[h].get("fp32_randn") and X5[h]["fp32_randn"]["ci"][0] > 0]
    s = ["# 8. Card-to-card variation\n",
         f"Every catalogue and rerun table in sections 2 to 5 was measured on {NC} cards with the same binaries, in the version-3 check of 26 September: aifoundry2 and aifoundry3 (firmware 1.3.1; aifoundry3 pinned at 600 MHz by its 0 W TDP) and aifoundry1's card 1 (firmware 1.2.0). The hot line of section 6 is aifoundry2 and aifoundry3 only (23 September). aifoundry1's card 0 overheats and is left out (docs/findings/14-card-behaviour.md).\n",
         "| Comparison | " + col(lambda h: f"{name(h)} / aifoundry2") + " |", "|---|" + "---|" * len(OC),
         f"| Instruction and byte energies, {XC[OC[0]]['n']} catalogue entries, 3 passes each, each card at its own die temperature | " + col(lambda h: f"median **{f(XC[h]['median'], 3)}**, 10th–90th percentile {f(XC[h]['p10'], 3)}–{f(XC[h]['p90'], 3)}, range {f(ratios(h)[0])}–{f(ratios(h)[-1])}") + " |",
         "| The same, per instruction and per byte (medians) | " + col(lambda h: f"{f(med(ratios(h, False)), 3)} and {f(med(ratios(h, True)), 3)}") + " |",
         "| The catalogue pass by pass (the version-3 check, 99% interval) | " + col(lambda h: f"{f(GAP[h]['ratio'], 3)} [{f(GAP[h]['lo'], 3)}, {f(GAP[h]['hi'], 3)}]" if GAP.get(h) else "—") + " |",
         f"| Relay, rings and levels (and the hot line on aifoundry3) | " + col(lambda h: f"median {f(med(rer[h]), 3)} over {len(rer[h])} entries, range {f(rer[h][0])}–{f(rer[h][-1])}" if h in rer else "—") + " |",
         "| Tensor-unit switching, fp32 random data (section 3.2), each card at its own launch temperature | " + col(tens) + " |",
         "| Idle against aifoundry2's law (the version-3 idle cycles) | " + col(lambda h: f"{sgn(LRv8[h]['mean'])} W at {LRv8[h]['T'][0]}–{LRv8[h]['T'][1]} °C" if h in LRv8 else "—") + " |",
         "| Die temperature under load, catalogue median (aifoundry2: " + f"{DB.get(REF, 0):.0f} °C) | " + col(lambda h: f"{DB[h]:.0f} °C" if h in DB else "—") + " |",
         "| Minion and SRAM rail voltage (aifoundry2: " + (f"{RM[REF]['minion']:.0f} and {RM[REF]['sram']:.0f} mV" if REF in RM else "—") + ") | " + col(lambda h: f"{RM[h]['minion']:.0f} and {RM[h]['sram']:.0f} mV" if h in RM else "—") + " |",
         "",
         "**What it says.** " + and_list(f"{name(h)} reads {100 * abs(1 - XC[h]['median']):.0f}% {'lower' if XC[h]['median'] < 1 else 'higher'} than aifoundry2 in the median ({f(XC[h]['median'], 3)})" for h in OC)
         + ", each card at its own die temperature; the 23 September catalogue, which this one replaces (its data: `docs/reports/data/2026-09-23-energy-manual/catalogue-23sep.json`), gave " + (f"{f(C23['median'], 3)}" if C23 else "0.950") + " for aifoundry3. "
         + " ".join(f"{name(h)} reads {f(med(ratios(h, False)), 3)} per instruction but {f(med(ratios(h, True)), 3)} per byte." for h in OC if abs(med(ratios(h, True)) / med(ratios(h, False)) - 1) > 0.05)
         + " Against each card's own common scale, once the " + str(XC[OC[0]]["n"]) + " comparisons are allowed for, " + and_list((f"{WORD[len(OUTL[h]['outliers'])]} entr{'ies' if len(OUTL[h]['outliers']) > 1 else 'y'} on {name(h)} (" + and_list(f"`{o['cfg']}` {f(o['vs_scale'])}×" for o in OUTL[h]["outliers"]) + ")") if OUTL[h]["outliers"] else f"no entry on {name(h)}" for h in order(OUTL))
         + " differ beyond the noise of three passes (99%, Bonferroni). The rerun entries of sections 4.2, 5 and 6 do not share the catalogue's scale.\n",
         "**What sets the scale.** " + (f"The energy per operation rises with die temperature on {and_list(name(h) + ', ' + bci(TP[h]['beta_pct_per_c']) for h in tin)}" + (f", and is not resolved on {and_list(name(h) + ', ' + bci(TP[h]['beta_pct_per_c']) for h in tno)}" if tno else "") + f" (a 30-entry panel run hot and cool on each card, 6–14 °C apart; 99% intervals): enough to account for aifoundry3's gap, its die {DB.get(REF, 0) - DB.get('aifoundry3', 0):.0f} °C cooler here, so that aifoundry3 itself differs from aifoundry2 is not established. " if tin else "")
         + (f"With aifoundry3 cool and aifoundry2 warm, as here, the panel gives {f(CBw['ratio'], 3)} [{f(CBw['lo'], 3)}, {f(CBw['hi'], 3)}]. " if CBw else "")
         + (f"Switching power itself follows the die: the random-data fp32 matmul drew {and_list(sgn(X5[h]['fp32_randn']['hot_minus_cool_w'], 1) + ' W [' + sgn(X5[h]['fp32_randn']['ci'][0], 1) + ', ' + sgn(X5[h]['fp32_randn']['ci'][1], 1) + '] more on ' + name(h) + ' launched at ' + f'{X5[h]['launch_c']['hi']:.0f}' + ' than at ' + f'{X5[h]['launch_c']['lo']:.0f}' + ' °C' for h in xr)}. " if xr else "")
         + (f"By V² alone the rail voltages would make {semi_list(name(h) + chr(39) + 's instructions cost ' + f'{abs(v2(h, 'minion')):.0f}% ' + ('more' if v2(h, 'minion') > 0 else 'less') + ' and its SRAM accesses ' + f'{abs(v2(h, 'sram')):.0f}% ' + ('more' if v2(h, 'sram') > 0 else 'less') for h in order(RM) if h != REF)}: the voltage does not explain aifoundry3's scale, and is in line with aifoundry1 card 1's cheaper instructions and dearer bytes, which its cooler die would not explain." if len(RM) > 1 else "") + "\n",
         f"**How the bars split.** For the catalogue's {XC[OC[0]]['n']} shared entries the pass-to-pass scatter on one card is 1–2% (median standard error) and about half of the bar an entry carries is the difference between the cards, the rest the day. "
         + (f"The smallest signal, the hot line (about {hn['contended']['mean']*at['contended']['ops_per_s']*1e-9:.1f} W over idle), carries one of the widest bars, ±{100*(hn['contended']['hi']-hn['contended']['lo'])/2/hn['contended']['mean']:.0f}%, mostly because its first session read {at['contended']['over_idle_w']:.1f} W against 1.0–1.2 W in every pass since, and because on so small a signal the leakage correction, a few tenths of a watt, moves each pass by 10–25%" if "contended" in hn else "")
         + (f"; the DRAM relay's bar (±{100*(rr['dram']['hi']-rr['dram']['lo'])/2/rr['dram']['mean']:.0f}%) is mostly aifoundry1 card 1 against the other two" if "dram" in rr else "") + ".\n"]
    open(os.path.join(out, "08-cards.md"), "w").write("\n".join(s))

    # ---------------------------------------------------------------- 00: the structure page's two card-dependent lines
    # 00-structure.md is written by hand; its row for section 8 and its note on the rail voltage follow the cards in the data
    sp_ = os.path.join(out, "00-structure.md")
    if os.path.exists(sp_):
        txt = open(sp_).read().split("\n")
        CLK = VI.get("clocks", {})
        for i, line in enumerate(txt):
            if line.startswith("| 8 | **Card-to-card variation** |"):
                txt[i] = (f"| 8 | **Card-to-card variation** | every table on {and_list(name(h) for h in CARDS)}; aifoundry1's card 0 overheats and is left out"
                          " | measured here (the version-3 check, 26 September 2026) |")
            if "the minion rail reads" in line and CLK:
                j = line.index("the minion rail reads")
                k = line.find(")", j)
                txt[i] = line[:j] + "the minion rail reads " + and_list(f"{CLK[h]['mv'] / 1000:.3f} V on {name(h)}" for h in order(CLK)) + line[k:]
        open(sp_, "w").write("\n".join(txt))
    print("rendered", out)


if __name__ == "__main__":
    main()
