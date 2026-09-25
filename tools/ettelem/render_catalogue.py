#!/usr/bin/env python3
"""Render the comprehensive instruction catalogue and the fine-grained memory pages from catalogue.json.

    render_catalogue.py docs/reports/data/2026-09-23-energy-manual/catalogue.json docs/energy-manual/
"""
import json
import os
import sys

CLASSES = [
    ("Scalar integer, one cycle", ["add", "sub", "and", "or", "xor", "sll", "srl", "sra", "slt", "sltu", "addw", "subw", "sllw", "srlw", "sraw",
                                   "addi", "andi", "ori", "xori", "slli", "srli", "srai", "slti", "sltiu", "addiw", "lui", "auipc", "nop"]),
    ("Scalar integer multiply and divide", ["mul", "mulh", "mulhu", "mulhsu", "mulw", "div", "divu", "rem", "remu", "divw", "divuw", "remw", "remuw"]),
    ("Scalar float", ["fadd.s", "fsub.s", "fmul.s", "fmin.s", "fmax.s", "fsgnj.s", "fsgnjn.s", "fsgnjx.s", "fmadd.s", "fmsub.s", "fnmadd.s", "fnmsub.s"]),
    ("Between the float and integer register files", ["feq.s", "flt.s", "fle.s", "fclass.s", "fcvt.w.s", "fcvt.wu.s", "fmv.x.w", "fcvt.s.w", "fcvt.s.wu", "fmv.w.x"]),
    ("Vector float, 8 lanes", ["fadd.ps", "fsub.ps", "fmul.ps", "fmin.ps", "fmax.ps", "fsgnj.ps", "fsgnjn.ps", "fsgnjx.ps", "fmadd.ps", "fmsub.ps", "fnmadd.ps", "fnmsub.ps",
                               "feq.ps", "flt.ps", "fle.ps", "fcmov.ps", "fcmovm.ps", "fround.ps", "ffrc.ps", "fclass.ps", "fcvt.ps.pw", "fcvt.pw.ps", "fswizz.ps"]),
    ("Vector integer, 8 lanes", ["fadd.pi", "fsub.pi", "fmul.pi", "fmulh.pi", "fmulhu.pi", "fand.pi", "for.pi", "fxor.pi", "fnot.pi", "fsll.pi", "fsrl.pi", "fsra.pi",
                                 "fmin.pi", "fmax.pi", "fminu.pi", "fmaxu.pi", "feq.pi", "flt.pi", "fltu.pi", "fle.pi", "faddi.pi", "fandi.pi", "fslli.pi", "fsrli.pi", "fsrai.pi",
                                 "fpackrepb.pi", "fpackreph.pi"]),
    ("Transcendental unit, 8 lanes", ["fexp.ps", "flog.ps", "frcp.ps"]),
    ("Masks and broadcasts", ["feqm.ps", "fltm.ps", "flem.ps", "fbcx.ps", "fbci.ps", "fbci.pi"]),
    ("Loads and stores that hit the L1", ["lb", "lh", "lw", "ld", "lbu", "lhu", "lwu", "sb", "sh", "sw", "sd", "flw", "fsw", "flw.ps", "fsw.ps"]),
    ("Loads and stores that bypass the L1", ["flwl.ps", "fswl.ps"]),
    ("Branches and jumps", ["beq_taken", "bne_nottaken", "blt_data", "bge_data", "bltu_data", "bgeu_data", "jal"]),
    ("Atomics on a private line", ["amoaddl.w", "amoswapl.w", "amoorl.w", "amomaxl.w", "amoaddl.d", "amoaddg.w", "amoaddg.d"]),
    ("System", ["csrr_fccnb", "fence"]),
    ("Compressed against full-width, in-place forms", ["c.add", "add_norvc", "c.addi", "addi_norvc", "c.mv", "c.li"]),
]
LANES = {n: 8 for c in CLASSES[4:8] for n in c[1]}
HUB = "https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability"
TRAPPED = ["fdiv.s", "fsqrt.s", "fdiv.ps", "fsqrt.ps", "frsq.ps", "fsin.ps", "fdiv.pi", "fdivu.pi", "frem.pi", "fremu.pi", "fcvt.l.s", "fcvt.s.l", "csrr cycle"]


def f(v, n=1):
    return "—" if v is None else f"{v:.{n}f}"


def bar(c, n=1):
    """mean [lo–hi] over every rerun on every card."""
    return "—" if not c else f"**{f(c['mean'], n)}** [{f(c['lo'], n)}–{f(c['hi'], n)}]"


def cards_of(c, n=1):
    return " · ".join(f"{h.replace('aifoundry', 'card ')} {f(v['mean'], n)} ± {f(v['se'], n)}" for h, v in c["per_card"].items()) if c else "—"


def main():
    d = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    cards = list(d["cards"])
    A = d["cards"][cards[0]]["summary"]
    B = d["cards"][cards[1]]["summary"] if len(cards) > 1 else {}
    C = d.get("combined", {})

    def g(name, o, h=2):
        return A.get(f"{name}/{o}/h{h}")

    def gb(name, o, h=2):
        return B.get(f"{name}/{o}/h{h}")

    hw = [(c["hi"] - c["lo"]) / 2 / c["mean"] for c in C.values() if c["mean"] > 0 and c["cards"] > 1]
    import numpy as np
    s = ["# 3.1 Every instruction\n",
         "Energy per instruction retired, above idle, at 600 MHz and 0.52 V, with both harts of all 1,024 minions "
         "issuing it back to back. **Every figure is the mean over six measurements — three passes in shuffled order "
         "on each of two cards — and the bracket after it is the confidence bar: the range those six spanned.** The "
         "per-card columns give each card's own mean with its pass-to-pass standard error. Operands: zeros, and random "
         "values in [0.5, 2) (random 32-bit words for integer ops).\n",
         f"Over the whole catalogue the bar is ±{100*np.median(hw):.1f}% of the value in the median and ±{100*np.percentile(hw, 90):.1f}% at "
         f"the 90th percentile; most of it is the difference between the two cards, which runs {d['cross_card']['median']:.3f}× in the median.\n",
         f"Instructions that **trap** in U-mode on this silicon and so have no energy: `" + "`, `".join(TRAPPED) + "`.\n"]
    for title, names in CLASSES:
        rows = []
        for n in names:
            z, r = C.get(f"{n}/zeros/h2"), C.get(f"{n}/random/h2")
            if not (z and r):
                continue
            lanes = LANES.get(n, 1)
            rate = A.get(f"{n}/random/h2", {}).get("ops_per_cycle_per_hart", {}).get("mean")
            per = f" ({f(r['mean'] / lanes)}/lane)" if lanes > 1 else ""
            rows.append(f"| `{n}` | {bar(z)} | {bar(r)}{per} | {f(r['mean'] / z['mean'], 2)}× | {f(rate, 3)} | {cards_of(r)} |")
        if rows:
            s += [f"\n## {title}\n", "| Instruction | zeros pJ [range] | random pJ [range] | random / zeros | issue per hart per cycle | random, by card ± se |",
                  "|---|---|---|---|---|---|"] + rows
    open(os.path.join(out, "03a-every-instruction.md"), "w").write("\n".join(s) + "\n")

    # ---------------- fine grain
    W = d["cards"][cards[0]]["wire"]
    W2 = d["cards"][cards[1]]["wire"] if len(cards) > 1 else {}

    def shr(dd):
        return next((p_["shires"] for p_ in W["random"]["points"] if p_["hops"] == dd), "—")

    def slope6(wf):
        """the same points fitted over 1–6 hops, leaving out d = 8"""
        pts = [(p_["hops"], p_["pj_per_byte"]) for p_ in wf["points"] if 1 <= p_["hops"] <= 6]
        return float(np.polyfit([q[0] for q in pts], [q[1] for q in pts], 1)[0])
    sl = d["cards"][cards[0]]["sram_leakage"]
    sl2 = d["cards"][cards[1]]["sram_leakage"] if len(cards) > 1 else None
    t = ["# 4.3 Finer grain: wires, lines, rows, and the leakage of the arrays\n",
         "What a byte costs is not one number. Below, the parts of it that can be separated with the card's own "
         "instruments: the distance the byte travels, the line it is part of, the DRAM row it comes from, and the "
         "leakage of the memory it sat in. **Every figure is the mean over three passes on each of two cards, and a "
         "bracket is the range those six measurements spanned.** Fits are made per card and both are shown.\n",
         "## Wires: energy against distance on the mesh\n",
         "1 KB tensor loads from the scratchpad of a shire exactly *d* hops away on the mesh, all 32 shires reading up to "
         f"{max(p_['hops'] for p_ in W['random']['points'] if p_['shires'] == 32)} hops ({shr(6)} at 6 hops and {shr(8)} at 8, so the 8-hop point has half the traffic), at "
         "most two readers per target. A straight line through the points gives the energy of the array access and "
         "the local path (the intercept) and the energy of one hop of mesh, router and wire per byte (the slope), fitted over 1–8 hops.\n",
         "| Operands | Card | own scratchpad pJ/B | intercept pJ/B | **slope pJ/B per hop** | rms of the fit |", "|---|---|---|---|---|---|"]
    for o in ("zeros", "random"):
        for h, wf in ((cards[0], W.get(o)), (cards[1] if len(cards) > 1 else None, W2.get(o))):
            if wf and h:
                t.append(f"| {o} | {h} | {f(wf['local_pj_per_byte'], 2)} | {f(wf['intercept_pj_per_byte'], 2)} | **{f(wf['slope_pj_per_byte_per_hop'], 3)}** | {f(wf['rms_pj_per_byte'], 2)} |")
    if W.get("zeros") and W.get("random") and W2.get("zeros") and W2.get("random"):
        sz = [W["zeros"]["slope_pj_per_byte_per_hop"], W2["zeros"]["slope_pj_per_byte_per_hop"]]
        sr = [W["random"]["slope_pj_per_byte_per_hop"], W2["random"]["slope_pj_per_byte_per_hop"]]
        tz, tr = (sr[0] - sz[0]), (sr[1] - sz[1])
        t.append(f"\n**Fitted over 1–8 hops, one hop costs {f(sum(sz)/2, 2)} pJ/B on zeros [{f(min(sz), 2)}–{f(max(sz), 2)} across the cards] and {f(sum(sr)/2, 2)} pJ/B on random data "
                 f"[{f(min(sr), 2)}–{f(max(sr), 2)}].** The difference between the two, {f((tz + tr)/2, 2)} pJ/B per hop [{f(min(tz, tr), 2)}–{f(max(tz, tr), 2)}], "
                 f"is what random data adds over zeros, the data-dependent energy of the links and routers — **{f((tz + tr)/2*1000/8, 0)} fJ per random bit per hop** [{f(min(tz, tr)*1000/8, 0)}–{f(max(tz, tr)*1000/8, 0)}]: "
                 f"part of it is bits that differ from one flit (the unit the mesh moves as a whole) to the next and part is the ones carried, which cost even when they do not change; "
                 f"[Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) separates the two with chosen bit patterns and converts them to fJ per bit·mm. "
                 f"The rest, what a hop costs on all-zero data, is clocking, arbitration and buffering.\n")
        r6 = [slope6(W["random"]), slope6(W2["random"])]
        z6 = [slope6(W["zeros"]), slope6(W2["zeros"])]
        t.append(f"**Over 1–6 hops**, leaving out d = 8, where only {shr(8)} shires have a partner and the point sits nearly level with d = 6, the same data give "
                 f"{f(r6[0], 2)} and {f(r6[1], 2)} pJ/B per hop on random data ({cards[0]}, {cards[1]}) and {f((r6[0] - z6[0]) * 1000 / 8, 0)} and {f((r6[1] - z6[1]) * 1000 / 8, 0)} fJ per random bit per hop, "
                 f"which is what [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) measures (2.17 pJ/B per hop on board power, loaded mesh): use its figures for wires.\n")
        t += ["| hops | zeros pJ/B [range over both cards, 6 runs] | random pJ/B [range] | shires reading |", "|---|---|---|---|"]
        for p_ in W["random"]["points"]:
            dd = p_["hops"]
            cz, cr = C.get(f"wire/hop{dd}/zeros"), C.get(f"wire/hop{dd}/random")
            t.append(f"| {dd} | {bar(cz, 2)} | {bar(cr, 2)} | {p_['shires']} |")

    def grp(prefix):
        return {k: v for k, v in A.items() if k.startswith(prefix)}

    t += ["\n## Lines: what opening a 64 B line costs, and the shire cache's banks\n",
          "32 B vector loads through the L1 from the shire's own scratchpad, striding so that every line is filled once "
          "and all, half or a quarter of it is used. Energy per *load* rises as the fill is shared by fewer loads; the "
          "difference is the cost of the fill itself.\n",
          "| Stride | Fills per 32 B load | zeros pJ per load [range, both cards] | random pJ per load [range] | zeros pJ/B delivered | random pJ/B delivered |", "|---|---|---|---|---|---|"]
    def c32(k):   # the catalogue stores these per byte delivered; a 32 B load is 32 of them
        c = C.get(k)
        return c and {"mean": 32 * c["mean"], "lo": 32 * c["lo"], "hi": 32 * c["hi"], "per_card": {h: {"mean": 32 * v["mean"]} for h, v in c["per_card"].items()}}
    for st in ("32", "64", "128"):
        cz, cr = C.get(f"l1fill/stride{st}/zeros"), C.get(f"l1fill/stride{st}/random")
        if cz and cr:
            fills = {"32": 0.5, "64": 1, "128": 1}[st]
            t.append(f"| {st} B | {fills} | {bar(c32(f'l1fill/stride{st}/zeros'), 1)} | {bar(c32(f'l1fill/stride{st}/random'), 1)} | {f(cz['mean'], 2)} | {f(cr['mean'], 2)} |")
    z32, z64 = c32("l1fill/stride32/zeros"), c32("l1fill/stride64/zeros")
    r32, r64 = c32("l1fill/stride32/random"), c32("l1fill/stride64/random")
    if z32 and z64 and r32 and r64:
        fz = 2 * (z64["mean"] - z32["mean"])
        fr = 2 * (r64["mean"] - r32["mean"])
        per = ", ".join(f"{h} {f(2 * (r64['per_card'][h]['mean'] - r32['per_card'][h]['mean']), 0)}" for h in sorted(r64["per_card"]))
        tlz, tlr = C["tload/scp/zeros"]["mean"], C["tload/scp/random"]["mean"]
        t.append(f"\nTwice the difference between the stride-64 and stride-32 rows is the fill of one 64 B line from the scratchpad "
                 f"into the L1: **{f(fz, 0)} pJ on zeros, {f(fr, 0)} pJ on random data** ({per} on random data) — {f(fz / 64, 1)} and {f(fr / 64, 1)} pJ per byte of line, "
                 f"about {5 * round(100 * (fz + fr) / 64 / (tlz + tlr) / 5):.0f}% of the {f(tlz, 1)} and {f(tlr, 1)} pJ/B "
                 f"a tensor load pays for the same bytes from the same scratchpad. What random data adds over zeros is about {f(fr - fz, 0)} pJ for the line's 512 bits, "
                 f"{f((fr - fz) * 1000 / 512, 0)} fJ per bit on the path from the shire cache into the L1. "
                 f"What is left in a 32 B load once its share of the fill is taken out — about {f(2 * z32['mean'] - z64['mean'], 0)} pJ on zeros — is the "
                 f"L1 hit itself plus the awake core issuing it.\n")
    t += ["The same scratchpad read with 64 B tensor loads at strides that cycle the shire cache's banks, alternate two of "
          "them, or return to the same one (banks are address bits [7:6], sub-banks [9:8]):\n",
          "| Stride | zeros pJ per 64 B [range] | random pJ per 64 B [range] | GB/s |", "|---|---|---|---|"]
    for st in ("64", "128", "256"):
        z, r = A.get(f"scpline/stride{st}/zeros"), A.get(f"scpline/stride{st}/random")
        if z and r:
            cz, cr = C.get(f"scpline/stride{st}/zeros"), C.get(f"scpline/stride{st}/random")
            t.append(f"| {st} B | {f(cz['mean'] * 64, 1)} [{f(cz['lo'] * 64, 1)}–{f(cz['hi'] * 64, 1)}] | {f(cr['mean'] * 64, 1)} [{f(cr['lo'] * 64, 1)}–{f(cr['hi'] * 64, 1)}] | {r['bytes_per_s']['mean'] / 1e9:,.0f} |")
    t += ["\n## Rows: does the DRAM row pattern matter?\n",
          "1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB, so the "
          "touched set beats the 32 MB L3 whatever the pattern. Sequential: consecutive kilobytes go to consecutive "
          "banks and each bank sees 32 columns of a row before moving on. Row hit: stride 8 KB, so every access is the "
          "next column of the same bank and row. Row miss: after every 8 KB a jump to the next row, so every bank "
          "sees a new row on every visit. Thirty-two awake minions are 0.06 W, not worth correcting for.\n",
          "| Pattern | zeros pJ/B [range over 3 passes, one card] | random pJ/B [range] | GB/s |", "|---|---|---|---|"]
    for name, what in (("seq", "sequential: next bank, 32 columns per row visit"), ("rowhit", "same bank and row, next column, every access"),
                       ("rowmiss", "new row on every visit to a bank")):
        z, r = A.get(f"dramrow2/{name}/zeros"), A.get(f"dramrow2/{name}/random")
        if z and r:
            cz, cr = C.get(f"dramrow2/{name}/zeros"), C.get(f"dramrow2/{name}/random")
            t.append(f"| {what} | {bar(cz, 1)} | {bar(cr, 1)} | {f(r['bytes_per_s']['mean'] / 1e9, 1)} |")
    l3 = A.get("dramrow/stride8K/random"), A.get("dramrow/stride8K/zeros")
    pats = [p_ for p_ in ("seq", "rowhit", "rowmiss") if C.get(f"dramrow2/{p_}/random")]
    if pats and C.get("tload/dram/random"):
        # each of the 32 harts moves one 1 KB access per visit to its row, at the aggregate rate / 32, at 600 MHz
        gbs = [A[f"dramrow2/{p_}/{o}"]["bytes_per_s"]["mean"] for p_ in pats for o in ("zeros", "random")]
        cyc = [1024 * 32 / g * 600e6 for g in gbs]
        prem = {o: [100 * (C[f"dramrow2/{p_}/{o}"]["mean"] / C[f"tload/dram/{o}"]["mean"] - 1) for p_ in pats] for o in ("zeros", "random")}
        r100 = lambda v: f"{round(v / 100) * 100:,.0f}"
        # 3.87 µs and 2,325 cycles: the refresh interval the memory-anatomy report reads from the controller (PLAN2 D21)
        t.append("\n**The row pattern does not change the energy per byte.** Row hits, row misses and the streaming case agree "
                 "within their pass-to-pass error on both operand sets. The controller runs an open-page policy: a row stays open "
                 "until a refresh (every 3.87 µs) or an access to another row of its bank closes it ([Anatomy of a memory access]"
                 "(https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#how-long-a-row-stays-open)). "
                 f"Each hart here comes back to its row only every {r100(min(cyc))}–{r100(max(cyc))} cycles or so (32 harts at "
                 f"{min(gbs) / 1e9:.0f}–{max(gbs) / 1e9:.0f} GB/s), with 31 other streams in between, and a refresh falls every 2,325 cycles. "
                 "So either every pattern paid an activation, or an activation is small next to the transfer (one of 20 pJ/B would "
                 "have shown); for a programmer it makes no difference. "
                 f"These 32-hart loads cost {min(prem['random']):.0f}–{max(prem['random']):.0f}% more per byte than [4.1](04-bytes-memory.md)'s tensor loads at "
                 f"{A['tload/dram/random']['bytes_per_s']['mean'] / 1e9:.0f} GB/s ({min(prem['zeros']):.0f}–{max(prem['zeros']):.0f}% more on zeros): "
                 "use them to compare patterns, and 4.1 to price DRAM.\n")
    if l3[0] and l3[1]:
        t.append(f"An earlier version of this experiment with all 1,024 minions and 32 KB touched per hart fitted in the L3 and "
                 f"measured that instead: **{f(l3[1]['pj_per_byte']['mean'], 1)} pJ/B on zeros, {f(l3[0]['pj_per_byte']['mean'], 1)} on random "
                 f"data at {f(l3[0]['bytes_per_s']['mean'] / 1e9, 0)} GB/s** — the L3, read by tensor loads through the mesh, which the "
                 f"18 September table put at 10.8 pJ/B at a higher clock.\n")
    t += ["## Placement inside a shire: which neighbourhood reads\n",
          "The shire's own scratchpad read by only one of its four neighbourhoods at a time (8 minions each), random data.\n",
          "| Neighbourhood | pJ/B [range, both cards] | GB/s |", "|---|---|---|"]
    for k in range(4):
        v = A.get(f"neigh/{k}/random")
        if v:
            t.append(f"| {k} (minions {8*k}–{8*k+7}) | {bar(C.get(f'neigh/{k}/random'), 2)} | {v['bytes_per_s']['mean'] / 1e9:,.0f} |")
    if sl and sl.get("fit"):
        fit = sl["fit"]
        fit2 = sl2["fit"] if sl2 and sl2.get("fit") else None
        c80 = next((c for c in sl["curve"] if c["T"] == 80), None)
        mb = 1000 * c80["sram_w"] / 128 if c80 else fit["mw_per_mb_at_80"]
        nj = mb / 1048576 * 1e6
        rd = C.get("tload/scp/random", {}).get("mean")
        t += ["\n## Leakage of the arrays: the SRAM rail against temperature\n",
              f"The SRAM rail during every idle stretch of the session on {cards[0]}, against die temperature. The rail "
              f"feeds the 128 MB of on-chip SRAM (16 MB of L2, 32 MB of L3, 80 MB of scratchpad). Fitted with the idle law's "
              f"36 °C e-folding imposed, not fitted:\n",
              f"$$P_\\text{{SRAM}}(T) = {f(fit['P_fix_w'], 2)}\\,\\mathrm{{W}} + {f(fit['A_leak_80_w'], 2)}\\,\\mathrm{{W}}\\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/36\\,^\\circ\\mathrm{{C}}}}$$\n",
              ("- **The negative constant says the rail rises faster than that shape**, so the fitted leakage term is not the arrays' leakage. " if fit["P_fix_w"] < 0 else "- ")
              + (f"The whole rail at 80 °C is {f(c80['sram_w'], 2)} W, **{f(mb, 1)} mW per MB**, an upper bound on the arrays' leakage including the cache logic on the same rail; " if c80 else "")
              + f"it rises {f(fit['slope_80_mw_per_c'], 0)} mW per °C at 80 °C for the whole 128 MB. Measured: " + ", ".join(f"{c['sram_w']:.2f} W at {c['T']} °C" for c in sl["curve"][::max(1, len(sl["curve"]) // 3)]) + ".",
              f"- This is what the memory costs for existing, per second, whatever runs: at about {f(mb, 0)} mW per MB a byte held in scratchpad for one second leaks at most about {f(nj, 0)} nJ at 80 °C, "
              f"as much as reading it {round(nj * 1000 / rd, -2):,.0f} times ({f(rd, 1)} pJ per read)." if rd else "",
              (f"- The same rail on {cards[1]}, which idles 20 °C cooler: " + ", ".join(f"{c['sram_w']:.2f} W at {c['T']} °C" for c in sl2["curve"][::max(1, len(sl2['curve']) // 3)]) + "." if sl2 and sl2.get("curve") else ""),
              "", "| Die °C | SRAM rail W, " + cards[0] + " | idle stretches |" + (" SRAM rail W, " + cards[1] + " | idle stretches |" if sl2 else ""), "|---|---|---|" + ("---|---|" if sl2 else "")]
        c2 = {c["T"]: c for c in sl2["curve"]} if sl2 else {}
        for T_ in sorted(set(c["T"] for c in sl["curve"]) | set(c2)):
            a_ = next((c for c in sl["curve"] if c["T"] == T_), None)
            b_ = c2.get(T_)
            t.append(f"| {T_} | {f(a_['sram_w'], 3) if a_ else '—'} | {a_['n'] if a_ else '—'} |" + (f" {f(b_['sram_w'], 3) if b_ else '—'} | {b_['n'] if b_ else '—'} |" if sl2 else ""))
    # ---- where the current flows: the rail split, by class
    taus = [v["tau_s"] for v in (d.get("rail_filter") or {}).values()]   # the PMIC's running average, measured (catalogue.json rail_filter)
    tau_txt = f"time constant {min(taus):.1f}–{max(taus):.1f} s on the two cards" if taus else "time constant about 1 s"
    t += ["\n## Where the current flows: each class of operation by rail\n",
          "The PMIC meters three rails — the minions, the on-chip SRAM, and the mesh — and the service processor reports "
          "them; board power covers everything including the regulators' own losses. The split of a burst's power over idle across "
          "those rails, read from the last 0.6 s of each burst and divided by the 0.94 of the step that the PMIC's running average "
          f"({tau_txt}) has reached there, averaged over the instructions in each class on random data, on "
          f"{cards[0]} (three passes). What is not on a metered rail is the regulators and whatever else has no sensor.\n",
          "| Class | W over idle | minions | SRAM | mesh | unmetered |", "|---|---|---|---|---|---|"]
    groups = [("Scalar integer", ["add", "sub", "and", "or", "xor", "sll", "srl", "sra", "slt", "sltu", "addi", "andi", "ori", "xori", "slli", "srli"]),
              ("Scalar multiply", ["mul", "mulh", "mulhu", "mulhsu"]), ("Scalar float", ["fadd.s", "fsub.s", "fmul.s", "fmadd.s", "fmsub.s"]),
              ("Vector float", ["fadd.ps", "fsub.ps", "fmul.ps", "fmadd.ps", "fmsub.ps"]), ("Vector integer", ["fadd.pi", "fsub.pi", "fmul.pi", "fand.pi", "fxor.pi"]),
              ("Transcendental", ["fexp.ps", "flog.ps", "frcp.ps"]), ("L1 hits", ["lw", "ld", "sw", "sd", "flw.ps", "fsw.ps"]),
              ("L1-bypass to the L2", ["flwl.ps", "fswl.ps"]), ("Atomics, local L2", ["amoaddl.w", "amoaddl.d"]), ("Atomics, home L3", ["amoaddg.w", "amoaddg.d"])]
    def rail_row(label, cfgs):
        rows = [A[c] for c in cfgs if c in A]
        if not rows:
            return None
        o = sum(r["over_idle_w"]["mean"] for r in rows) / len(rows)
        m = sum(r["rails_over_w"]["minion_w"]["mean"] for r in rows) / len(rows)
        sr = sum(r["rails_over_w"]["sram_w"]["mean"] for r in rows) / len(rows)
        n = sum(r["rails_over_w"]["noc_w"]["mean"] for r in rows) / len(rows)
        u = o - m - sr - n
        pc = lambda v: f"{100 * v / o:.0f}%".replace("-0%", "0%")
        return f"| {label} | {f(o, 2)} | {pc(m)} | {pc(sr)} | {pc(n)} | {pc(u)} |"
    for label, names in groups:
        r = rail_row(label, [f"{n}/random/h2" for n in names])
        if r:
            t.append(r)
    for label, cfgs in [("Own scratchpad, tensor load", ["tload/scp/random"]), ("Own scratchpad, tensor store", ["tstore/scp/random"]),
                        ("Scratchpad 1 hop away", ["wire/hop1/random"]), ("Scratchpad 3 hops away", ["wire/hop3/random"]),
                        ("Scratchpad 6 hops away", ["wire/hop6/random"]), ("DRAM, tensor load", ["tload/dram/random"]),
                        ("DRAM, tensor store", ["tstore/dram/random"]), ("DRAM, stores through the L1", ["st_stream/dram/random"])]:
        r = rail_row(label, cfgs)
        if r:
            t.append(r)
    # the mesh rail against hops: an independent measurement of the wire energy
    hp = [(A[f"wire/hop{d}/random"]["hop_distance"], A[f"wire/hop{d}/random"]["rails_over_w"]["noc_w"]["mean"] * A[f"wire/hop{d}/random"]["over_idle_w"]["mean"] and
           A[f"wire/hop{d}/random"]["rails_over_w"]["noc_w"]["mean"] / A[f"wire/hop{d}/random"]["bytes_per_s"]["mean"] * 1e12)
          for d in (1, 2, 3, 4, 5, 6, 8) if f"wire/hop{d}/random" in A]
    if len(hp) >= 3:
        import numpy as np
        x = np.array([p[0] for p in hp], float); y = np.array([p[1] for p in hp])
        c = np.polyfit(x, y, 1)
        t += ["", f"**The mesh rail alone**, against hop distance on random data: {f(c[0], 3)} pJ/B per hop with an intercept of {f(c[1], 2)} pJ/B "
              f"(the cost of leaving the shire). This is the wire and router energy measured on its own supply, independently of the "
              f"board-power fit above.\n", "| hops | mesh rail, pJ/B |", "|---|---|"] + [f"| {p[0]} | {f(p[1], 2)} |" for p in hp]
    # ---- the unmetered remainder, attributed; the DDR rail's droop as a DRAM-power proxy
    ufp = os.path.join(os.path.dirname(sys.argv[1]), "unmetered_fit.json")
    if os.path.exists(ufp):
        uf = json.load(open(ufp))
        t += ["\n## What is on no metered rail: attributed, and a droop meter for DRAM\n",
              "The remainder — board power minus the three rails — cannot be metered with anything on the card, but over the whole catalogue what a workload adds above idle can be "
              "attributed: each configuration's mean unmetered watts fitted as a fraction of each rail's watts plus a cost per DRAM byte, no intercept. "
              "`tools/ettelem/fit_unmetered.py` makes the fit from `catalogue.json` and writes it to `unmetered_fit.json`. "
              f"The canonical account of it is [Limits of observability, §4.2–4.3]({HUB}#the-unmetered-remainder-attributed); this section keeps the full tables.\n",
              "| unmetered W of a configuration = | " + " | ".join(h for h in uf if h.startswith("aifoundry")) + " |", "|---|" + "---|" * len([h for h in uf if h.startswith("aifoundry")])]
        hosts = [h for h in uf if h.startswith("aifoundry")]
        for label, k, n, unit in (("× minion-rail W", "minion", 3, ""), ("× SRAM-rail W", "sram", 3, ""), ("× mesh-rail W", "noc", 3, ""), ("per DRAM byte", "dram_pj_per_byte", 1, " pJ/B")):
            t.append(f"| {label} | " + " | ".join(f"{f(uf[h]['coef'][k], n)} ± {f(uf[h]['se'][k], n)}{unit}" for h in hosts) + " |")
        t.append("| residual rms, configuration means | " + " | ".join(f"{f(uf[h]['rms_w'], 2)} W, n = {uf[h]['n']}" for h in hosts) + " |")
        def dram_rms(h):   # the residual on the configurations that move DRAM
            Sx = d["cards"].get(h, {}).get("summary", {})
            r = []
            for k, e in Sx.items():
                if "dram" not in k or k.startswith("dramrow/stride8K"):
                    continue
                R_ = e["rails_over_w"]
                m_, sr_, n_ = R_["minion_w"]["mean"], R_["sram_w"]["mean"], R_["noc_w"]["mean"]
                cf = uf[h]["coef"]
                r.append(e["over_idle_w"]["mean"] - m_ - sr_ - n_ - (cf["minion"] * m_ + cf["sram"] * sr_ + cf["noc"] * n_ + cf["dram_pj_per_byte"] * e["bytes_per_s"]["mean"] * 1e-12))
            return (float(np.sqrt(np.mean(np.square(r)))), len(r)) if r else None
        t.append("| residual rms, the configurations that move DRAM | " + " | ".join((lambda x: f"{f(x[0], 2)} W, n = {x[1]}" if x else "—")(dram_rms(h)) for h in hosts) + " |")
        a2 = uf["aifoundry2"]["coef"]
        def split(h, k):   # (off-rail, rest) pJ per byte of one configuration: rest = the rails plus the fitted delivery losses
            e, cf = d["cards"][h]["summary"][k], uf[h]["coef"]
            R_ = e["rails_over_w"]; m_, sr_, n_ = R_["minion_w"]["mean"], R_["sram_w"]["mean"], R_["noc_w"]["mean"]
            tot = e["over_idle_w"]["mean"] / e["bytes_per_s"]["mean"] * 1e12
            off = (e["over_idle_w"]["mean"] - m_ - sr_ - n_ - (cf["minion"] * m_ + cf["sram"] * sr_ + cf["noc"] * n_)) / e["bytes_per_s"]["mean"] * 1e12
            return off, tot - off
        # the tensor loads and stores from DRAM and the 1,024-minion DRAM loads, on both cards
        dk = [(h, f"{p_}/{o}") for h in hosts for p_ in ("tload/dram", "tstore/dram", "dramrow/stride1K") for o in ("zeros", "const", "random")
              if f"{p_}/{o}" in d["cards"][h]["summary"]]
        lo_o = [split(h, k)[0] for h, k in dk if not k.endswith("random")]; hi_o = [split(h, k)[0] for h, k in dk if k.endswith("random")]
        rest = [split(h, k)[1] for h, k in dk]
        sto = [split(h, f"st_stream/dram/{o}")[0] for h in hosts for o in ("zeros", "const", "random") if f"st_stream/dram/{o}" in d["cards"][h]["summary"]]
        dco = [uf[h]["coef"]["dram_pj_per_byte"] for h in hosts]
        # hub-u-25: the idle remainder (board less the three rails) over every burst's idle, per card
        def unsensed(h):
            b = [x for x in d["bursts"][h] if x.get("minion_idle_w") is not None]
            u = [x["p_idle_w"] - x["minion_idle_w"] - x["sram_idle_w"] - x["noc_idle_w"] for x in b]
            T_ = [x["die_c_idle"] for x in b]
            return round(min(u)), round(max(u)), int(min(T_)), -int(-max(T_) // 1)
        us = {h: unsensed(h) for h in hosts if d.get("bursts", {}).get(h)}
        # the DRAM configurations' residual (measured unmetered W less the fit), per card: its size and its pattern
        def dram_res(h):
            cf, out_ = uf[h]["coef"], []
            for k, e in d["cards"][h]["summary"].items():
                if "dram" not in k or k.startswith("dramrow/stride8K"):
                    continue
                R_ = e["rails_over_w"]; m_, sr_, n_ = R_["minion_w"]["mean"], R_["sram_w"]["mean"], R_["noc_w"]["mean"]
                un = e["over_idle_w"]["mean"] - m_ - sr_ - n_
                out_.append((k, un - (cf["minion"] * m_ + cf["sram"] * sr_ + cf["noc"] * n_ + cf["dram_pj_per_byte"] * e["bytes_per_s"]["mean"] * 1e-12), un))
            return out_
        dres = {h: dram_res(h) for h in hosts}
        share = [float(np.sqrt(np.mean([r[1] ** 2 for r in v])) / np.mean([r[2] for r in v])) for v in dres.values() if v]
        st_r = [r[1] for v in dres.values() for r in v if r[0].startswith("st_stream/")]
        tp = [(r[0], r[1]) for v in dres.values() for r in v if r[0].split("/")[0] in ("tload", "tstore") or r[0].startswith("dramrow/stride1K")]
        tp_hi = [x for k, x in tp if k.endswith("/random")]; tp_lo = [x for k, x in tp if not k.endswith("/random")]
        res_txt = (f"- **The residual on the configurations that move DRAM is {100 * min(share):.0f}–{100 * max(share):.0f}% of their unmetered power (rms over mean), and it has a pattern**: "
                   f"stores through the L1 sit {f(min(st_r), 1)}–{f(max(st_r), 1)} W above the fit, because the line read from DRAM before each store is not in their byte count; "
                   f"the tensor loads and stores from DRAM and the 1,024-minion DRAM loads sit above it on random data (+{f(min(tp_hi), 1)} to +{f(max(tp_hi), 1)} W) "
                   f"and below it on zeros and constants ({f(max(tp_lo), 1).replace('-', '−')} to {f(min(tp_lo), 1).replace('-', '−')} W). The published fit is kept as it is; "
                   + ("counting those line reads (the stores' bytes twice) would bring the DRAM residual to " + " and ".join(
                       f"{f(uf[h]['l1_line_read_refit']['rms_dram_w'], 2)} W on {h} (DRAM term {f(uf[h]['l1_line_read_refit']['coef']['dram_pj_per_byte'], 1)} pJ/B)"
                       for h in hosts if uf[h].get('l1_line_read_refit')) + "; that refit is `l1_line_read_refit` in `unmetered_fit.json`."
                      if any(uf[h].get('l1_line_read_refit') for h in hosts) else "")
                   if share and st_r and tp_hi and tp_lo and max(tp_hi) > 0 > min(tp_lo) else "")
        t += ["", f"- **An instruction's unmetered energy is the regulator's**: {100*a2['minion']:.0f}% of what the minion rail delivers is lost between the 12 V input and the core, and nothing else moves; that is as far as the rails' meters can be trusted, since each 1% of error in their scale moves it by about {f(1 + a2['minion'], 1)} points. The 18% \"unmetered\" share of the arithmetic classes above is this.",
              f"- **A DRAM byte's unmetered energy is the memory's**: {f(min(dco), 0)}–{f(max(dco), 0)} pJ per byte on average (the fitted coefficient on the two cards) in the DDR PHY, the I/O rail and the DRAM chips "
              f"({f(min(lo_o), 0)}–{f(max(lo_o), 0)} on zeros and constants, {f(min(hi_o), 0)}–{f(max(hi_o), 0)} on random data), on top of the {f(min(rest), 0)}–{f(max(rest), 0)} pJ the mesh, the SRAM and the delivery losses take on the way: "
              f"together the {f(C['tload/dram/zeros']['mean'], 0)}–{f(C['tload/dram/random']['mean'], 0)} pJ per byte of [4.1](04-bytes-memory.md)'s tensor loads from DRAM. "
              f"A byte written through the L1 costs about twice that off-rail ({f(min(sto), 0)}–{f(max(sto), 0)} pJ), because the line is read from DRAM before it is written.",
              res_txt,
              f"- **The mesh coefficient is not all regulator**: {100*a2['noc']:.0f}% is too much for a delivery loss; the memory shires' own logic, on an unmetered rail, works whenever the mesh moves bytes to them.",
              "- What the fit cannot say: how the idle " + (f"{min(v[0] for v in us.values())}–{max(v[1] for v in us.values())} W (" + ", ".join(f"{v[0]}–{v[1]} W on {h} at {v[2]}–{v[3]} °C" for h, v in sorted(us.items(), key=lambda kv: kv[1][0])) + ")" if us else "12–16 W")
              + " splits between DDR, PCIe, the IO shire, Maxion and the regulators' own draw, or how the DRAM term splits below its regulator. That is the subject of the improvement ladder in [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability).\n"]
        if "ddr_droop" in uf:
            dd = uf["ddr_droop"]
            c0, cm = dd["mv_per_dram_offrail_w"], dd["mv_per_board_w_common"]
            fl = dd.get("per_config_fields") or []
            pc = [dict(zip(fl, row)) for row in dd.get("per_config", [])]
            nod = [q for q in pc if not q.get("dram_offrail_w")]   # configurations that move no DRAM
            l3d = [q["droop_ddr_mv"] for q in nod if q["cfg"].startswith("dramrow/stride8K")]
            oth = [q["droop_ddr_mv"] for q in nod if not q["cfg"].startswith("dramrow/stride8K")]
            ph = [(q["droop_ddr_mv"] - cm * q["over_idle_w"]) / c0 for q in nod]   # read as DRAM watts, after the common term
            t += [f"**A droop meter for DRAM.** The memory shires' Moortec voltage monitors report the 0.8 V DDR rail every 133 ms (`die_mv.ddr` in every telemetry file; {f(dd['idle_die_mv']['ddr'], 0)} mV at idle against an 800 mV set point). "
                  f"Across the {dd['n']} configuration means it droops **{f(dd['mv_per_dram_offrail_w'], 2)} mV per watt of off-rail DRAM power** (plus {f(dd['mv_per_board_w_common'], 3)} mV per watt of anything else; rms {f(dd['rms_mv'], 2)} mV): 1 mV ≈ {f(1 / dd['mv_per_dram_offrail_w'], 1)} W of DRAM, refreshed every 133 ms, from a sensor that was always there. "
                  f"It is a proxy calibrated against the fit above, not a meter, and not independent of the board meter. It responds mostly to DRAM traffic, but not only: heavy mesh and scratchpad traffic with no DRAM access droops it too"
                  + (f", by up to {f(max(oth), 1)} mV, and {f(max(l3d), 1)} mV for L3 reads through the mesh" if oth and l3d else "")
                  + " (" + " and ".join(f"`{e['cfg']}` {f(e['droop_ddr_mv'], 2)} mV" for e in dd["examples"] if not e["dram_offrail_w"] and e["droop_ddr_mv"] > 0.9) + " in the table below), "
                  + (f"which it would read as up to about {f(max(ph), 1)} W of DRAM" if ph else "which it would read as DRAM power")
                  + f"; and its idle reading moves by about 1 mV between 71 and 77 °C. The minion rail sags {f(dd['minion_ir_drop_mv_per_w'], 3)} mV per watt the cores draw; the "
                  "[Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) report (§3) maps each shire's rails at idle.\n",
                  "| Configuration (aifoundry2, mean of three passes) | W over idle | unmetered W less the fitted rail losses | DDR-rail droop, mV | minion-rail droop, mV |", "|---|---|---|---|---|"]
            for e in dd["examples"]:
                t.append(f"| `{e['cfg']}` | {f(e['over_idle_w'], 2)} | {f(e['dram_offrail_w'], 2) if e['dram_offrail_w'] else '—'} | {f(e['droop_ddr_mv'], 2)} | {f(e['droop_minion_mv'], 2)} |")
            t.append("")
    t.append("\nSources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/`, reduced by "
             "`workloads/enercat/analyze_catalogue.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`; the attribution and the droop in `unmetered_fit.json` beside it, "
             "written by `tools/ettelem/fit_unmetered.py`.\n")
    open(os.path.join(out, "04a-fine-grain.md"), "w").write("\n".join(t) + "\n")
    print("rendered 03a and 04a")


if __name__ == "__main__":
    main()
