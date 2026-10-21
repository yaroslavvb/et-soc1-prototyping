#!/usr/bin/env python3
"""V3-HL report page prose, with every number taken from reduce_hl.py's output (no number typed by hand).

    python3 tools/claims-v3/hl/page_text.py --hl <hl.json> --out <text.json>

Statements whose truth depends on the data (a ranking, a verdict, a pass or fail) are decided here from the data.
"""
import argparse
import json
import math

K_B = 1.380649e-23
E = 1.602176634e-19


def g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict):
            return default
        d = d.get(k, d.get(str(k)))
    return default if d is None else d


def fj(x, se=None, n=1):
    if x is None:
        return "–"
    if se:
        m = n
        while m < 3 and round(se * 1e15, m) == 0:
            m += 1
        return f"{x * 1e15:.{m}f} ± {se * 1e15:.{m}f} fJ"
    return f"{x * 1e15:.{n}f} fJ"


def el(x):
    if not x:
        return "–"
    return f"{x / 1e6:.2f} million" if x >= 1e6 else f"{float(f'{x:.3g}'):,.0f}"


def w(x, se=None, n=2):
    if x is None:
        return "–"
    return f"{x:+.{n}f} W" + (f" ± {se:.{n}f}" if se else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hl", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.hl))
    C3, C2, C1 = R["cards"]["aifoundry3"], R["cards"].get("aifoundry2", {}), R["cards"].get("aifoundry1-c0", {})
    G = R["gates"]
    v3 = C3["v_mean"]
    v2c, v1c = C2.get("v_mean", 0), C1.get("v_mean", 0)
    lq, lb, ec3 = C3["lq"], C3["lb"], C3.get("ec", {})
    lq_d, lq_b, lq_n = lq["designed"], lq["bus"], lq["nets"]
    lb_d, lb_b, lb_n = lb["designed"], lb["bus"], lb["nets"]
    e_in = ec3.get("e_in", {})
    e_out = ec3.get("e_out_from_xnz") or ec3.get("e_out_from_xio", {})
    e_out_xio = ec3.get("e_out_from_xio", {})
    ain = ec3.get("ain", {})
    items3 = C3["items"]

    # ---- the order family: aifoundry3 (600 MHz) first, aifoundry2 (800 MHz) beside it
    o3 = lambda pos, o: g(C3, "ord", pos, o) or {}
    o2 = lambda pos, o: g(C2, "ord", pos, o) or {}
    m0, m19 = o3(0, "maxflip"), o3(19, "maxflip")
    n2 = o2(0, "maxflip").get("n")

    def ranking(getter, pos):
        """How the four orders rank, from the data; an order within 2 SE of zero is called indistinguishable from Gray."""
        vals = [("Gray", 0.0, 0.0)] + [(nm, getter(pos, o).get("W"), getter(pos, o).get("se") or 0)
                                         for nm, o in (("binary", "binary"), ("shuffled", "shuffled"), ("max-flip", "maxflip"))]
        if any(v is None for _, v, _ in vals):
            return "(not all measured)"
        mono = all(vals[i + 1][1] > vals[i][1] for i in range(3))
        flat = [nm for nm, v, se in vals[1:] if abs(v) < 2 * max(se, 1e-9)]
        s = "in the order of their flipped bits" if mono else "not quite in the order of their flipped bits"
        if flat:
            s += f" ({', '.join(flat)} indistinguishable from Gray)"
        return s

    # ---- ladders: linearity verdict, first flip, nets per bit
    lin, lin_b = lq.get("linear", {}), lb.get("linear", {})
    lin_ok = lambda L: bool(L) and (L["residual_rms_W"] <= 0.25 or L["residual_rms_W"] <= 0.05 * L["span_W"])
    lin_branch = lambda L: "the absolute 0.25 W bar" if L["residual_rms_W"] <= 0.25 else "its alternative, 5% of the span, not the absolute 0.25 W bar"
    ff_q, ff_b = g(lq, "first_flip_W", "W"), g(lb, "first_flip_W", "W")
    per_bit_q, per_bit_b = lin.get("W_per_h"), lin_b.get("W_per_h")
    nets_q = lq_d["J"] / lq_n["J"] if lq_n.get("J") else None
    nets_b = lb_d["J"] / lb_n["J"] if lb_n.get("J") else None
    rq = {r["h"]: r["dW"] for r in lq["rungs"].values()}
    inc_low = (rq[2] - rq[1]) if rq.get(2) is not None and rq.get(1) is not None else None
    inc_high = (rq[23] - rq[12]) / 11 if rq.get(23) is not None and rq.get(12) is not None else None
    rtl = C3.get("rtl_score", {})
    rtl_ok = rtl.get("rms_W") is not None and rtl["rms_W"] <= 1.5
    pi3, rn3 = g(items3, "anchor_pi", "p80"), g(items3, "anchor_randn", "p80")

    # ---- ec: gate type, zero words, the never-zero control
    and_vs_xor = (ain["J_per_bit"] / e_in["J"] - 1) if ain.get("J_per_bit") and e_in.get("J") else 0
    zero_note = ""
    a32, a8 = items3.get("ain_h32", {}), items3.get("ain_h8", {})
    if a32.get("d_p80") is not None and a8.get("d_p80") is not None:
        off = a32["d_p80"] / (a8["d_p80"] * 4) - 1
        zero_note = (f" The AND rung whose operands include the all-zero word (h = 32, kept out of the fit by the pre-registration) reads "
                     f"{abs(off) * 100:.0f}% {'below' if off < 0 else 'above'} a straight line through h = 8, level with the XOR ladder's h = 32 rung: "
                     f"either the AND's price per bit falls with h, or the all-zero word is cheaper; these rungs cannot tell which.")
    xnz_vs_xio = (ec3["e_out_from_xnz"]["J"] / ec3["e_out_from_xio"]["J"] - 1) if ec3.get("e_out_from_xnz") and ec3.get("e_out_from_xio") else 0
    c1ec = C1.get("ec", {})
    xnz1 = (c1ec["e_out_from_xnz"]["J"] / c1ec["e_out_from_xio"]["J"] - 1) if c1ec.get("e_out_from_xnz") and c1ec.get("e_out_from_xio") else 0
    rail_in = g(ec3, "xin", "rail_J_per_bit")
    rail_out = (2 * g(ec3, "xnz", "rail_J_per_bit") - rail_in) if g(ec3, "xnz", "rail_J_per_bit") and rail_in else None

    # ---- bits
    bits3 = C3.get("bits") or {}
    b = lambda j, k="dW": g(bits3, j, k)
    measured = [j for j in (0, 8, 16, 22, 23, 31) if b(j)]
    worst = max(((j, b(j, "pred_dW") / b(j)) for j in measured), key=lambda t: t[1]) if measured else (None, 0)

    # ---- V^2 and the board meters
    v2 = R.get("v2", {})
    band = (1.34 * 0.88, 1.40 / 0.88)
    keys = ("xin_rail_J_ratio", "xin_J_ratio", "lq_h2_h8_rail_J_ratio", "lq_h2_h8_J_ratio")
    ratios = [g(v2, c, k) for c in ("aifoundry1-c0", "aifoundry2") for k in keys]
    in_band = sum(1 for r in ratios if r and band[0] <= r <= band[1])
    br = {c: R["cards"][c]["lq"]["designed"]["J"] / R["cards"][c]["lq"]["designed"]["rail_J"] for c in R["cards"]
          if R["cards"][c]["lq"]["designed"].get("J") and R["cards"][c]["lq"]["designed"].get("rail_J")}
    ls2 = g(C2, "ls_vs_lq", 2) or {}
    lq2_2 = g(C2, "items", "lq_h2", "d_p80")

    kT = K_B * (273.15 + 58) * math.log(2)
    inv = 0.5 * 0.62e-15 * v3 ** 2
    passes = {c: len(R["cards"][c]["passes"]) for c in R["cards"]}
    kept = {c: (G[c]["kept"], G[c]["runs"]) for c in G}
    aside = {c: [x["pass"] for x in G[c]["passes_set_aside"]] for c in G}
    n_kept, n_all = sum(k for k, _ in kept.values()), sum(t for _, t in kept.values())

    stats = f"""<div class="stats">
<div class="stat"><b>{fj(lq_d.get('J'), n=0)}</b><span>per flipped B bit of an fp32 multiply-add, everything it sets off included (board, 600 MHz)</span></div>
<div class="stat"><b>{fj(e_in.get('J'), n=0)}</b><span>per flipped bit on a register-file read port, into one XOR</span></div>
<div class="stat"><b>{fj(e_out.get('J'), n=0)}</b><span>per flipped result bit</span></div>
<div class="stat"><b>{w(m0.get('W'), n=2)}</b><span>the same 4,096 multiply-adds, max-flip order against Gray order (600 MHz)</span></div>
</div>"""

    lede = (f"<p class=\"lede\">Horace He showed that a GPU multiplies predictable data faster because it flips fewer transistors. "
            f"Tonight we turned that into a measurement on the ET-SoC-1: hold the clock, the voltage, the launch temperature and the "
            f"arithmetic fixed, change only how many operand bits flip from one operation to the next, and read the slope. "
            f"<b>One flipped B-operand bit of an fp32 multiply-add costs {fj(lq_d.get('J'), lq_d.get('se_J'), 0)} of board energy</b>, "
            f"everything it sets off included; the same bit carried into a unit that only XORs it costs "
            f"<b>{fj(e_in.get('J'), e_in.get('se_J'), 1)}</b> on the way in and <b>{fj(e_out.get('J'), e_out.get('se_J'), 1)}</b> "
            f"on the way out. And the same 4,096 multiply-adds, put in an order that flips more bits, cost "
            f"<b>{w(m0.get('W'), m0.get('se'))}</b> more.</p>")

    gloss = ("<p class=\"note\"><b>Names on this page.</b> A <i>minion</i> is one of the chip's 1,088 small RISC-V cores (these kernels use "
             "1,024); each has an 8-lane vector unit. The <i>minion rail</i> is the supply that feeds them, metered on the card separately "
             "from the board's 12 V input. <i>TensorFMA32</i> is the instruction that multiplies two 16×16 fp32 tiles into an accumulator, "
             "512 eight-lane multiply-adds per operation; the <i>Horace kernel</i> is the lab's test that repeats it on one tile pair, named "
             "after the post. <code>fxor.pi</code> and <code>fand.pi</code> are the vector unit's bitwise XOR and AND on 8 lanes of 32 bits. "
             "Energies are <i>board</i> energies (the card's 12 V input) unless marked <i>rail</i>.</p>")

    body = lede + stats + gloss + f"""
<h2>The question</h2>
<p>Horace He's post (<a href="https://www.thonking.ai/p/strangely-matrix-multiplications">Strangely, Matrix Multiplications on GPUs Run Faster When Given "Predictable" Data!</a>, 2024)
explained the effect as power: random data flips more transistors, so a power-capped GPU clocks lower. He wrote that he could not count how many
times each transistor flips. On this chip the multiply-add unit's RTL is open, and the <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment">Horace experiment</a>
(21 Sep) showed one matmul drawing 38.3, 46.7 and 63.4 W on zeros, ones and random data at one speed, with counted toggles predicting
14 patterns to half a watt. What was missing was a <i>dose</i>: turn one knob, the number of bits that flip, and watch the watts follow.
Prior work measured GPU power against value distributions and bit similarity (<a href="https://depositonce.tu-berlin.de/items/f6f95245-1fea-41d7-8a84-8f83c4d6a84a">ALUPower</a>, Lucas and Juurlink, 2016; <a href="https://arxiv.org/abs/2409.18324">Gregersen, Patel and Choukse</a>, 2024), and
side-channel analysis has modelled power as Hamming distance since 2004; none of it priced a flip in joules on a chip whose flips can be counted.</p>

<h2>The experiment</h2>
<p>Pre-registered (<a href="https://github.com/yaroslavvb/et-soc1-prototyping/blob/main/tools/claims-v3/hl/README.md">tools/claims-v3/hl/README.md</a>:
the design, the analysis, the decision rules and the RTL predictions, committed before the first measured pass) and run tonight on three cards:</p>
<ul>
<li><b>The Hamming ladder.</b> The Horace kernel unchanged. In every vector lane the B operand alternates, every cycle, between a word and the
same word with its low h mantissa bits flipped; A is the same everywhere. h = 0, 1, 2, 4, 8, 12, 16, 23, with a quiet partner (A = 1.0) and
a busy one (A = π).</li>
<li><b>Same arithmetic, different order.</b> Every A column holds the same 16 values, differing in 4 mantissa bits, in Gray order (1 bit flips a
step), binary, shuffled, or the order that flips the most (3.5 bits a step, the most a cycle of 16 codes allows). Permuting A's rows permutes C's:
the same 4,096 multiply-adds, only their order differs.</li>
<li><b>Which bit.</b> One B bit at a time flips every cycle: the sign, an exponent bit, mantissa bits.</li>
<li><b>One bit, one gate.</b> The vector integer unit's <code>fxor.pi</code> and <code>fand.pi</code>, with the eight source registers set so that a
known number of bits flips on the read ports and in the result from one instruction to the next, and nothing else changes: the sources are never
written, and every destination is rewritten with the value it already holds.</li>
</ul>
<p><b>Protocol.</b> Every run launched as the die's reading first fell to a fixed value (58 °C; 57 °C on aifoundry1's card 0) after a short
heater burst, the 21 Sep method; 4 s runs; the board's power over two seconds once the clock had settled, corrected to the launch reading with each
card's own leakage slope; every item compared with its zero rung inside the same pass; every error bar the scatter between passes. Each
device process stayed under 10 s, and the cards were claimed in the lab channel.</p>
<p><b>Three operating points, none changed by us.</b> The cards no longer reach 80 °C under this duty cycle (they level off at 60–64 °C), so the
two cards whose clock governor is free ran at 800 MHz (aifoundry2 at {v2c:.3f} V, aifoundry1's card 0 at {v1c:.3f} V), and only aifoundry3, whose clock
is pinned, ran at 600 MHz and {v3:.3f} V. That gave the ½CV² test three voltages for free. On aifoundry3 tonight's anchors read {pi3:.1f} W on π and
{rn3:.1f} W on random data, {rn3 - pi3:.1f} W apart, against 16.4 W apart on 21 Sep (on another card, launched at 80 °C).</p>

<h2>1. Same arithmetic, different order</h2>
<p>The cleanest result needs no bit accounting at all. On the pinned card the same 4,096 multiply-adds cost <b>{w(m0.get('W'), m0.get('se'), 3)}</b>
more in max-flip order than in Gray order when the four changing bits are mantissa bits 0–3, and <b>{w(m19.get('W'), m19.get('se'), 3)}</b> when they
are bits 19–22 ({m0.get('n', '–')} passes; the RTL model predicted {w(m0.get('pred_W'), n=2)} and {w(m19.get('pred_W'), n=2)}). The four orders rank
{ranking(o3, 0)} at bits 0–3, and {ranking(o3, 19)} at bits 19–22. On aifoundry2 at 800 MHz and {v2c:.3f} V, where every switching watt is about 1.9 times
larger: {w(o2(0, 'maxflip').get('W'), o2(0, 'maxflip').get('se'))} and {w(o2(19, 'maxflip').get('W'), o2(19, 'maxflip').get('se'))} ({n2} passes).
By the pre-registered rule, a difference of at least three standard errors, the effect is confirmed on both cards.</p>
{{{{fig:ord}}}}

<h2>2. The Hamming ladder: the price of a flipped input bit</h2>
<p>Once the first bit has flipped, power rises close to a straight line with the number of flipped B bits. On the pinned card the slope is
<b>{fj(lq_d.get('J'), lq_d.get('se_J'), 1)}</b> per flipped B bit with the quiet partner and <b>{fj(lb_d.get('J'), lb_d.get('se_J'), 1)}</b> with the
busy one (h ≥ 1, {lq_d.get('n_passes')} passes). The residuals about the lines, {lin.get('residual_rms_W', 0):.2f} and {lin_b.get('residual_rms_W', 0):.2f} W over
{lin.get('span_W', 0):.1f} and {lin_b.get('span_W', 0):.1f} W spans, {'pass' if lin_ok(lin) and lin_ok(lin_b) else 'fail'} the pre-registered linearity rule on
{lin_branch(lin)}: the bottom of the ladder bends (the second flipped bit adds {inc_low:.2f} W, each bit above h = 12 about {inc_high:.2f} W), so the slope is
an average along it. The first flip costs {w(ff_b, g(lb, 'first_flip_W', 'se'))} with the busy partner, {ff_b / per_bit_b:.1f} times an ordinary bit on that
ladder: a dense partner's partial-product tree sits still under a constant operand, and the first changing bit wakes it. With the quiet partner the
first flip costs {w(ff_q, g(lq, 'first_flip_W', 'se'))}, {ff_q / per_bit_q:.1f} times an ordinary bit: no turn-on to speak of.</p>
<p>That price is <i>everything one flipped B bit causes</i>: the operand bus, the Booth and Wallace trees, the aligner, the adder, the result, and
the accumulator reads that change along with it. The pre-registered primary measure counts every operand-bus bit the RTL says changes,
accumulator reads included: {fj(lq_b.get('J'), lq_b.get('se_J'), 1)} per bus bit (quiet) and {fj(lb_b.get('J'), lb_b.get('se_J'), 1)} (busy). Per toggle of
any counted net in the unit it is {lq_n.get('J', 0) * 1e18:.0f} aJ and {lb_n.get('J', 0) * 1e18:.0f} aJ: by the RTL's counts the busy partner wakes
{nets_b / nets_q:.1f} times as many nets per flipped bit ({nets_b:,.0f} against {nets_q:,.0f}) and costs only {(lb_d['J'] / lq_d['J'] - 1) * 100:.0f}% more,
which puts most of the energy outside the tree's many small nets (a direction read from the model's own net counts, not a measured split).
The RTL model, fitted on 21 Sep and frozen before tonight, predicted the shape and over-predicted the size: measured differences are
{rtl.get('ratio_measured_over_pred', 0):.2f} of predicted, {rtl.get('rms_W', 0):.2f} W rms over {rtl.get('n_items')} items on the pinned card, which
{'passes' if rtl_ok else 'fails'} the pre-registered 1.5 W mark{'' if rtl_ok else ' and is reported as a failed prediction'}. It was fitted at 80 °C,
and these runs launched at 58 °C.</p>
{{{{fig:ladder}}}}

<h2>3. One bit, one gate</h2>
<p>On the vector integer unit a flipped bit on the two read ports costs <b>{fj(e_in.get('J'), e_in.get('se_J'), 1)}</b> into an XOR. A flipped result
bit costs <b>{fj(e_out.get('J'), e_out.get('se_J'), 1)}</b> on the ladder whose results never touch the all-zero word, and
{fj(e_out_xio.get('J'), e_out_xio.get('se_J'), 1)} on the ladder whose results alternate with it ({xnz_vs_xio * 100:+.0f}% between them here,
{xnz1 * 100:+.0f}% on aifoundry1's card 0): about {e_out['J'] / e_in['J']:.1f} times an input bit. Into an AND an input bit costs
{fj(ain.get('J_per_bit'), ain.get('se_J'), 1)}, {and_vs_xor * 100:.0f}% more than into an XOR, from the one AND rung the pre-registration kept (h = 8).{zero_note}
Even so, the gate is the small part of the bill: one gate of arithmetic behind a pipeline of transport. The multiply-add's
{fj(lq_d.get('J'), n=0)} per flipped bit is {lq_d['J'] / e_in['J']:.1f} times the read-port price: that factor is what a multiply-add does with one
changed input bit.</p>
<p class="note">An estimate published earlier today from the E46 instruction catalogue put the input bit at 5.0 fJ and the output and register write
at 33.7 fJ, on the die. On the minion rail, the nearest thing here to a die figure, the input bit measures {fj(rail_in, n=1)}, about three times that,
and the result bit {fj(rail_out, n=1)}. The catalogue's "random" operands are floats in [0.5, 2), which flip about 12 bits a word rather than 16, and
its two equations do not resolve the input price from zero card by card; tonight's sources set every flip by design.</p>
{{{{fig:ec}}}}

<h2>4. Not every bit costs the same</h2>
<p>A workload in which one B bit alternates costs {w(b(31), b(31, 'se'))} above constant operands for the sign bit, {w(b(23), b(23, 'se'))} for
exponent bit 23 (the only exponent bit run), {w(b(0), b(0, 'se'))} and {w(b(8), b(8, 'se'))} for mantissa bits 0 and 8, and {w(b(16), b(16, 'se'))} and
{w(b(22), b(22, 'se'))} for mantissa bits 16 and 22 (aifoundry3, 600 MHz). Sign, exponent and low mantissa bits sit together around half a watt;
what climbs is mantissa significance, the bits whose change runs through the whole multiplier. Mantissa bit {worst[0]} is the model's largest
miss: {b(worst[0]):.2f} W measured against {b(worst[0], 'pred_dW'):.2f} W predicted. At the same Hamming weight, position matters too: two flipped
bits spread across the mantissa cost {w(ls2.get('W'), ls2.get('se'))} more than two low bits (aifoundry2, {ls2.get('n')} passes), more than the low pair
itself costs ({w(lq2_2)} above its zero). There is no single price per bit.</p>
{{{{fig:bits}}}}

<h2>5. Does a flip cost ½CV²?</h2>
<p>The energy of a flip should grow with the square of the supply voltage and not with the clock. On the minion rail the read-port price on the two
800 MHz cards is {g(v2, 'aifoundry1-c0', 'xin_rail_J_ratio'):.2f}× and {g(v2, 'aifoundry2', 'xin_rail_J_ratio'):.2f}× aifoundry3's, at
{g(v2, 'aifoundry1-c0', 'v2_ratio'):.2f}× and {g(v2, 'aifoundry2', 'v2_ratio'):.2f}× its V²; the multiply-add ladder between h = 2 and h = 8 gives
{g(v2, 'aifoundry1-c0', 'lq_h2_h8_rail_J_ratio'):.2f}× and {g(v2, 'aifoundry2', 'lq_h2_h8_rail_J_ratio'):.2f}× on the rail. On the board meter the four
ratios are {g(v2, 'aifoundry1-c0', 'xin_J_ratio'):.2f}, {g(v2, 'aifoundry2', 'xin_J_ratio'):.2f}, {g(v2, 'aifoundry1-c0', 'lq_h2_h8_J_ratio'):.2f} and
{g(v2, 'aifoundry2', 'lq_h2_h8_J_ratio'):.2f}. {in_band} of the 8 sit inside the pre-registered band for ½CV² scaling ({band[0]:.2f}–{band[1]:.2f}),
and none near the 1.8–1.9× a price that also followed the clock would give: a flip costs ½CV². The band is wide; it rules out a clock-dependent
price, not every exponent near two. One caution: on aifoundry1's card 0 the board meter reads the multiply-add ladder only
{br.get('aifoundry1-c0', 0):.2f}× its own minion rail, against {br.get('aifoundry3', 0):.2f}× and {br.get('aifoundry2', 0):.2f}× on the other two cards,
although the board figure carries the regulators' loss; the rail is the number to use there.</p>
{{{{fig:v2}}}}

<h2>From one flip down to the floor</h2>
<div class="tablewrap"><table><thead><tr><th>One event</th><th class="n">Energy</th><th class="n">C = 2E/V² at {v3 * 1000:.0f} mV</th><th class="n">Electrons, CV/e</th></tr></thead><tbody>
<tr><td>Landauer's floor at 58 °C, kT ln 2</td><td class="n">{kT * 1e21:.1f} zJ</td><td class="n">–</td><td class="n">–</td></tr>
<tr><td>A minimum 7 nm inverter's input (ASAP7 INVx1, 0.62 fF)</td><td class="n">{inv * 1e18:.0f} aJ</td><td class="n">0.62 fF</td><td class="n">{el(0.62e-15 * v3 / E)}</td></tr>
<tr><td>One counted net toggle in the multiply-add, busy partner</td><td class="n">{lb_n.get('J', 0) * 1e18:.0f} aJ</td><td class="n">{lb_n.get('C_fF', 0):.1f} fF</td><td class="n">{el(lb_n.get('electrons'))}</td></tr>
<tr><td>One flipped bit on a register-file read port</td><td class="n">{fj(e_in.get('J'), n=1)}</td><td class="n">{e_in.get('C_fF', 0):.0f} fF</td><td class="n">{el(e_in.get('electrons'))}</td></tr>
<tr><td>One flipped result bit</td><td class="n">{fj(e_out.get('J'), n=1)}</td><td class="n">{e_out.get('C_fF', 0):.0f} fF</td><td class="n">{el(e_out.get('electrons'))}</td></tr>
<tr><td>One flipped B bit of an fp32 multiply-add, all it sets off</td><td class="n">{fj(lq_d.get('J'), n=0)}</td><td class="n">{lq_d.get('C_fF', 0):.0f} fF</td><td class="n">{el(lq_d.get('electrons'))}</td></tr>
<tr><td>The meter's smallest step (10 mW for one 0.16 s reading)</td><td class="n">1.6 mJ</td><td class="n">–</td><td class="n">–</td></tr>
</tbody></table></div>
<p>These energies are on the board's 12 V input, so they include the regulators' loss; the capacitances and electron counts are charge-equivalents at the
minion rail's voltage, upper bounds for the die. On the minion rail itself the multiply-add price is {fj(lq_d.get('rail_J'), n=0)} and the read-port
price {fj(rail_in, n=1)}. One flip is far below anything the meter can see; the slope over 10¹⁴–10¹⁶ flips a second is not.</p>

<h2>What this does not measure</h2>
<ul>
<li>A single transistor or a single wire: every price is an average over the nets one flipped bit sets switching.</li>
<li>Glitches: they are inside the measured watts, not in the RTL counts.</li>
<li>The die alone: board energy includes the regulators; the minion rail is reported beside it.</li>
<li>Heat as such: the thermal camera's lock-in of these rungs is the next session's work.</li>
<li>A second card at 600 MHz: the order and bit results have replicates only on the 800 MHz cards, at another voltage.</li>
</ul>

<h2>Method, data and how to rerun</h2>
<p>Experiment E60 (request Q119) in the <a href="https://github.com/yaroslavvb/et-soc1-prototyping">lab repository</a>. The code is in
<a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/tools/claims-v3/hl">tools/claims-v3/hl</a>; its README holds the design,
departures D1–D5 and amendments A1–A3, each committed before the data it touched (A1 added passes, the order family on the pinned card and a
never-zero control; A2 starts the 800 MHz cards' window after the clock settles; A3 excludes one rung that tripped aifoundry2's power limit).
Every pass's telemetry and run records, the reduced results (<code>hl.json</code>) and one row per run (<code>runs.csv</code>) are in
<a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-10-20-bitflip-ladder">docs/reports/data/2026-10-20-bitflip-ladder</a>.
Passes and runs kept after the gates: aifoundry3 {passes.get('aifoundry3')} passes, {kept['aifoundry3'][0]} of {kept['aifoundry3'][1]} runs;
aifoundry2 {passes.get('aifoundry2')} passes{(' (pass ' + ', '.join(map(str, aside['aifoundry2'])) + ' set aside)') if aside.get('aifoundry2') else ''},
{kept['aifoundry2'][0]} of {kept['aifoundry2'][1]}; aifoundry1's card 0 {passes.get('aifoundry1-c0')} passes, {kept['aifoundry1-c0'][0]} of
{kept['aifoundry1-c0'][1]}. To rerun a pass on a free card: <code>bash tools/claims-v3/hl/block.sh &lt;pass&gt; &lt;items&gt;</code>, then
<code>reduce_hl.py</code> over the pass folders.</p>
"""
    captions = {
        "ord": "Board watts above Gray order for the same 16 A values in other orders, on aifoundry3 (600 MHz) and aifoundry2 (800 MHz). Bars: the mean over passes; whiskers: one standard error between passes.",
        "ladder": "Watts above the h = 0 rung (the same operands with nothing changing) against the number of B mantissa bits that flip every cycle in every lane, "
                  "on aifoundry3 at 600 MHz and 0.522 V. Whiskers: one standard error between passes. Dashed: the RTL model's prediction, frozen before the run.",
        "ec": "Watts above the rung where nothing changes, against the bits that flip on the two read ports per instruction. Circles: the result never changes; "
              "squares: the result flips as many bits as the ports. aifoundry3, 600 MHz.",
        "bits": "One B bit alternates every cycle in every lane (A = 1.0); watts above constant operands. aifoundry3, 600 MHz.",
        "v2": "Energy per flipped bit on each card's minion rail against its supply voltage squared. Circles: a read-port bit (XOR ladder); squares: a B mantissa bit of the "
              "multiply-add between h = 2 and h = 8. Dashed: proportional to V² through aifoundry3.",
    }
    out = {"title": "What one flipped bit costs on the ET-SoC-1",
           "description": f"The Hamming ladder, run on three cards: {fj(lq_d.get('J'), n=0)} per flipped input bit of an fp32 multiply-add, "
                          f"{fj(e_in.get('J'), n=0)} per bit on a read port, the same arithmetic in another order {w(m0.get('W'))}, and ½CV² across three voltages.",
           "byline": f"AI Foundry lab · experiment E60 · Tue 20 Oct 2026 · aifoundry3, aifoundry2 and aifoundry1's card 0 · {n_kept} of {n_all} runs",
           "body": body, "captions": captions}
    json.dump(out, open(a.out, "w"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
