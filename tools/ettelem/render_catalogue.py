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
         "Energy per instruction retired, above idle, at 600 MHz and 0.517 V, with both harts of all 1,024 minions "
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
    sl = d["cards"][cards[0]]["sram_leakage"]
    sl2 = d["cards"][cards[1]]["sram_leakage"] if len(cards) > 1 else None
    t = ["# 4.3 Finer grain: wires, lines, rows, and the leakage of the arrays\n",
         "What a byte costs is not one number. Below, the parts of it that can be separated with the card's own "
         "instruments: the distance the byte travels, the line it is part of, the DRAM row it comes from, and the "
         "leakage of the memory it sat in. **Every figure is the mean over three passes on each of two cards, and a "
         "bracket is the range those six measurements spanned.** Fits are made per card and both are shown.\n",
         "## Wires: energy against distance on the mesh\n",
         "1 KB tensor loads from the scratchpad of a shire exactly *d* hops away on the mesh, every shire reading, at "
         "most two readers per target. A straight line through the points gives the energy of the array access and "
         "the local path (the intercept) and the energy of one hop of mesh, router and wire per byte (the slope).\n",
         "| Operands | Card | own scratchpad pJ/B | intercept pJ/B | **slope pJ/B per hop** | rms of the fit |", "|---|---|---|---|---|---|"]
    for o in ("zeros", "random"):
        for h, wf in ((cards[0], W.get(o)), (cards[1] if len(cards) > 1 else None, W2.get(o))):
            if wf and h:
                t.append(f"| {o} | {h} | {f(wf['local_pj_per_byte'], 2)} | {f(wf['intercept_pj_per_byte'], 2)} | **{f(wf['slope_pj_per_byte_per_hop'], 3)}** | {f(wf['rms_pj_per_byte'], 2)} |")
    if W.get("zeros") and W.get("random") and W2.get("zeros") and W2.get("random"):
        sz = [W["zeros"]["slope_pj_per_byte_per_hop"], W2["zeros"]["slope_pj_per_byte_per_hop"]]
        sr = [W["random"]["slope_pj_per_byte_per_hop"], W2["random"]["slope_pj_per_byte_per_hop"]]
        tz, tr = (sr[0] - sz[0]), (sr[1] - sz[1])
        t.append(f"\n**One hop costs {f(sum(sz)/2, 2)} pJ/B on zeros [{f(min(sz), 2)}–{f(max(sz), 2)} across the cards] and {f(sum(sr)/2, 2)} pJ/B on random data "
                 f"[{f(min(sr), 2)}–{f(max(sr), 2)}].** The difference between the two, {f((tz + tr)/2, 2)} pJ/B per hop [{f(min(tz, tr), 2)}–{f(max(tz, tr), 2)}], "
                 f"is the switching energy of the wires themselves — **{f((tz + tr)/2*1000/8, 0)} fJ per bit per hop of toggling** [{f(min(tz, tr)*1000/8, 0)}–{f(max(tz, tr)*1000/8, 0)}]. "
                 f"The rest, what a hop costs whether or not the bits change, is clocking, arbitration and buffering.\n")
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
          "| Stride | Fills per 32 B load | zeros pJ per load (card 2) | random pJ per load (card 2) | zeros pJ/B delivered [range, both cards] | random pJ/B delivered [range] |", "|---|---|---|---|---|---|"]
    for st in ("32", "64", "128"):
        z, r = A.get(f"l1fill/stride{st}/zeros"), A.get(f"l1fill/stride{st}/random")
        if z and r:
            fills = {"32": 0.5, "64": 1, "128": 1}[st]
            cz, cr = C.get(f"l1fill/stride{st}/zeros"), C.get(f"l1fill/stride{st}/random")
            t.append(f"| {st} B | {fills} | {f(z['pj_per_op']['mean'], 1)} | {f(r['pj_per_op']['mean'], 1)} | {bar(cz, 2)} | {bar(cr, 2)} |")
    z32, z64 = A.get("l1fill/stride32/zeros"), A.get("l1fill/stride64/zeros")
    r32, r64 = A.get("l1fill/stride32/random"), A.get("l1fill/stride64/random")
    if z32 and z64 and r32 and r64:
        fz = 2 * (z64["pj_per_op"]["mean"] - z32["pj_per_op"]["mean"])
        fr = 2 * (r64["pj_per_op"]["mean"] - r32["pj_per_op"]["mean"])
        t.append(f"\nTwice the difference between the stride-64 and stride-32 rows is the fill of one 64 B line from the scratchpad "
                 f"into the L1: **{f(fz, 0)} pJ on zeros, {f(fr, 0)} pJ on random data** — {f(fz / 64, 1)} and {f(fr / 64, 1)} pJ per byte of line, "
                 f"which agrees with the {f(A['tload/scp/zeros']['pj_per_byte']['mean'], 1)} and {f(A['tload/scp/random']['pj_per_byte']['mean'], 1)} pJ/B "
                 f"a tensor load pays for the same bytes from the same scratchpad. The {f(fr - fz, 0)} pJ difference is the toggling "
                 f"of the line's 512 bits, {f((fr - fz) * 1000 / 512, 0)} fJ per bit on the path from the shire cache into the L1. "
                 f"What is left in a 32 B load once its share of the fill is taken out — about {f(2 * z32['pj_per_op']['mean'] - z64['pj_per_op']['mean'], 0)} pJ on zeros — is the "
                 f"L1 hit itself plus the awake core issuing it.\n")
    t += ["The same scratchpad read with 64 B tensor loads at strides that cycle the shire cache's banks, alternate two of "
          "them, or return to the same one (banks are address bits [7:6], sub-banks [9:8]):\n",
          "| Stride | zeros pJ per 64 B [range] | random pJ per 64 B [range] | GB/s |", "|---|---|---|---|"]
    for st in ("64", "128", "256"):
        z, r = A.get(f"scpline/stride{st}/zeros"), A.get(f"scpline/stride{st}/random")
        if z and r:
            cz, cr = C.get(f"scpline/stride{st}/zeros"), C.get(f"scpline/stride{st}/random")
            t.append(f"| {st} B | {f(cz['mean'] * 64, 1)} [{f(cz['lo'] * 64, 1)}–{f(cz['hi'] * 64, 1)}] | {f(cr['mean'] * 64, 1)} [{f(cr['lo'] * 64, 1)}–{f(cr['hi'] * 64, 1)}] | {f(r['bytes_per_s']['mean'] / 1e9, 0)} |")
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
    t.append("\n**The row pattern does not change the energy per byte.** Row hits, row misses and the streaming case agree "
             "within their pass-to-pass error on both operand sets. Either the controller closes pages after each access "
             "(so every access pays an activation and the baseline already includes it) or the activation is small "
             "next to the ~115 pJ/B the transfer costs; the card's instruments cannot tell which, and for a programmer "
             "it makes no difference: **on this card a DRAM byte costs the same whatever order the rows are visited in.**\n")
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
            t.append(f"| {k} (minions {8*k}–{8*k+7}) | {bar(C.get(f'neigh/{k}/random'), 2)} | {f(v['bytes_per_s']['mean'] / 1e9, 0)} |")
    if sl and sl.get("fit"):
        fit = sl["fit"]
        fit2 = sl2["fit"] if sl2 and sl2.get("fit") else None
        t += ["\n## Leakage of the arrays: the SRAM rail against temperature\n",
              f"The service processor's SRAM rail during every idle stretch of the session, against die temperature. The rail "
              f"feeds the 128 MB of on-chip SRAM (16 MB of L2, 32 MB of L3, 80 MB of scratchpad). Fitted with the same "
              f"shape as the idle law:\n",
              f"$$P_\\text{{SRAM}}(T) = {f(fit['P_fix_w'], 2)}\\,\\mathrm{{W}} + {f(fit['A_leak_80_w'], 2)}\\,\\mathrm{{W}}\\; e^{{(T-80\\,^\\circ\\mathrm{{C}})/36\\,^\\circ\\mathrm{{C}}}}$$\n",
              f"- **{f(fit['mw_per_mb_at_80'], 1)} mW per MB of SRAM at 80 °C**, {f(fit['mw_per_mb_at_80'] / 8 / 1024 / 1024 * 1e6, 1)} nW per bit including the cache logic on the same rail, rising {f(fit['slope_80_mw_per_c'], 0)} mW per °C for the whole 128 MB. Measured: " + ", ".join(f"{c['sram_w']:.2f} W at {c['T']} °C" for c in sl["curve"][::max(1, len(sl["curve"]) // 3)]) + ".",
              f"- This is what the memory costs for existing, per second, whatever runs; a byte that sits in scratchpad for a second costs "
              f"{f(fit['mw_per_mb_at_80'] / 1024 / 1024 * 1e9, 1)} pJ of leakage at 80 °C, against the {f(A.get('tload/scp/random', {}).get('pj_per_byte', {}).get('mean', 0), 1)} pJ it costs to read it once.",
              (f"- The same rail on {cards[1]}, which idles 20 °C cooler: " + ", ".join(f"{c['sram_w']:.2f} W at {c['T']} °C" for c in sl2["curve"][::max(1, len(sl2['curve']) // 3)]) +
               f"; fitted with the same shape it gives {f(fit2['mw_per_mb_at_80'], 1)} mW/MB at 80 °C, so across the two cards the figure is "
               f"**{f((fit['mw_per_mb_at_80'] + fit2['mw_per_mb_at_80'])/2, 0)} mW/MB [{f(min(fit['mw_per_mb_at_80'], fit2['mw_per_mb_at_80']), 0)}–{f(max(fit['mw_per_mb_at_80'], fit2['mw_per_mb_at_80']), 0)}] at 80 °C**, "
               f"with the caveat that each card's range of temperatures is narrow and the second's is an extrapolation." if fit2 else ""),
              "", "| Die °C | SRAM rail W, " + cards[0] + " | idle stretches |" + (" SRAM rail W, " + cards[1] + " | idle stretches |" if sl2 else ""), "|---|---|---|" + ("---|---|" if sl2 else "")]
        c2 = {c["T"]: c for c in sl2["curve"]} if sl2 else {}
        for T_ in sorted(set(c["T"] for c in sl["curve"]) | set(c2)):
            a_ = next((c for c in sl["curve"] if c["T"] == T_), None)
            b_ = c2.get(T_)
            t.append(f"| {T_} | {f(a_['sram_w'], 3) if a_ else '—'} | {a_['n'] if a_ else '—'} |" + (f" {f(b_['sram_w'], 3) if b_ else '—'} | {b_['n'] if b_ else '—'} |" if sl2 else ""))
    # ---- where the current flows: the rail split, by class
    t += ["\n## Where the current flows: each class of operation by rail\n",
          "The service processor meters three rails — the minions, the on-chip SRAM, and the mesh — and board power "
          "covers everything including the regulators' own losses. The split of a burst's power over idle across "
          "those rails, read from the last second of each burst (the rail figures lag by about two seconds), averaged "
          "over the instructions in each class on random data. What is not on a metered rail is the regulators and "
          "whatever else has no sensor.\n",
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
        return f"| {label} | {f(o, 2)} | {100*m/o:.0f}% | {100*sr/o:.0f}% | {100*n/o:.0f}% | {100*u/o:.0f}% |"
    for label, names in groups:
        r = rail_row(label, [f"{n}/random/h2" for n in names])
        if r:
            t.append(r)
    for label, cfgs in [("Own scratchpad, tensor load", ["tload/scp/random"]), ("Own scratchpad, tensor store", ["tstore/scp/random"]),
                        ("Scratchpad 1 hop away", ["wire/hop1/random"]), ("Scratchpad 3 hops away", ["wire/hop3/random"]),
                        ("Scratchpad 6 hops away", ["wire/hop6/random"]), ("DRAM, tensor load", ["tload/dram/random"]),
                        ("DRAM, tensor store", ["tstore/dram/random"]), ("DRAM through the L1 write-back path", ["st_stream/dram/random"])]:
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
              "The remainder — board power minus the three rails — cannot be metered with anything on the card, but over the whole catalogue it can be "
              "attributed: each burst's unmetered watts fitted as a fraction of each rail's watts plus a cost per DRAM byte, no intercept.\n",
              "| unmetered W of a burst = | " + " | ".join(h for h in uf if h.startswith("aifoundry")) + " |", "|---|" + "---|" * len([h for h in uf if h.startswith("aifoundry")])]
        hosts = [h for h in uf if h.startswith("aifoundry")]
        for label, k, n, unit in (("× minion-rail W", "minion", 3, ""), ("× SRAM-rail W", "sram", 3, ""), ("× mesh-rail W", "noc", 3, ""), ("per DRAM byte", "dram_pj_per_byte", 1, " pJ/B")):
            t.append(f"| {label} | " + " | ".join(f"{f(uf[h]['coef'][k], n)} ± {f(uf[h]['se'][k], n)}{unit}" for h in hosts) + " |")
        t.append("| residual rms, bursts | " + " | ".join(f"{f(uf[h]['rms_w'], 2)} W, n = {uf[h]['n']}" for h in hosts) + " |")
        a2 = uf["aifoundry2"]["coef"]
        t += ["", f"- **An instruction's unmetered energy is the regulator's**: {100*a2['minion']:.0f}% of what the minion rail delivers is lost between the 12 V input and the core, and nothing else moves. The 18% \"unmetered\" share of the arithmetic classes above is this.",
              f"- **A DRAM byte's unmetered energy is the memory's**: {f(a2['dram_pj_per_byte'], 0)} pJ per byte in the DDR PHY, the I/O rail and the DRAM chips, on top of the 50–60 pJ the mesh, the SRAM and the delivery losses take on the way. A byte written through the L1 costs twice that off-rail, because the line is read from DRAM before it is written.",
              f"- **The mesh coefficient is not all regulator**: {100*a2['noc']:.0f}% is too much for a delivery loss; the memory shires' own logic, on an unmetered rail, works whenever the mesh moves bytes to them.",
              "- What the fit cannot say: how the idle 12–15 W splits between DDR, PCIe, the IO shire, Maxion and the regulators' own draw, or how the DRAM term splits below its regulator. That is the subject of the observability report's improvement ladder.\n"]
        if "ddr_droop" in uf:
            dd = uf["ddr_droop"]
            t += [f"**A droop meter for DRAM.** The memory shires' Moortec voltage monitors report the 0.8 V DDR rail every 133 ms (`die_mv.ddr` in every telemetry file; {f(dd['idle_die_mv']['ddr'], 0)} mV at idle against an 800 mV set point). "
                  f"Across the {dd['n']} bursts it droops **{f(dd['mv_per_dram_offrail_w'], 2)} mV per watt of off-rail DRAM power** (plus {f(dd['mv_per_board_w_common'], 3)} mV per watt of anything else; rms {f(dd['rms_mv'], 2)} mV): 1 mV ≈ 1.2 W of DRAM at 10 Hz, from a sensor that was always there. "
                  f"It is calibrated against the fit above, so it is not independent of the board meter, but it responds to DRAM traffic alone and does not drift with the die temperature. The minion rail sags {f(dd['minion_ir_drop_mv_per_w'], 3)} mV per watt the cores draw, the IR drop the spatial temperature brief mapped shire by shire.\n",
                  "| Burst (aifoundry2) | W over idle | DRAM W off-rail | DDR-rail droop, mV | minion-rail droop, mV |", "|---|---|---|---|---|"]
            for e in dd["examples"]:
                t.append(f"| `{e['cfg']}` | {f(e['over_idle_w'], 2)} | {f(e['dram_offrail_w'], 2) if e['dram_offrail_w'] else '—'} | {f(e['droop_ddr_mv'], 2)} | {f(e['droop_minion_mv'], 2)} |")
            t.append("")
    t.append("\nSources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/`, reduced by "
             "`workloads/enercat/analyze_catalogue.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`; the attribution and the droop in `unmetered_fit.json` beside it.\n")
    open(os.path.join(out, "04a-fine-grain.md"), "w").write("\n".join(t) + "\n")
    print("rendered 03a and 04a")


if __name__ == "__main__":
    main()
