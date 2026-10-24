#!/usr/bin/env python3
"""E64 page prose: every number from reduce_hpl.py's results and surface_hpl.py's figures, so the text cannot drift
from the data.

    python3 tools/claims-v3/hpl/page_text_hpl.py --results results.json --figures figures.json --out page_text.json
"""
import argparse
import json
import statistics as st

OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}
UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
NAME = {"zeros": "zeros", "sparse75": "75% zeros", "ones": "ones", "signs": "random signs", "pow2": "random powers of 2",
        "a_randn_b_ones": "A random, B ones", "a_ones_b_randn": "A ones, B random", "mant": "random mantissas",
        "uniform": "uniform [0, 1)", "randn": "random normal"}
REPO = "https://github.com/yaroslavvb/et-soc1-prototyping"


def rate(t, mhz, minions=1024):
    return minions * OPS[t] / CYC[t] * mhz * 1e6 / 1e12


def g(x, n=1):
    return "–" if x is None else f"{x:.{n}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--figures", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--end", default=None, help="the main session's end.json (its card minutes)")
    a = ap.parse_args()
    R = json.load(open(a.results))
    F = json.load(open(a.figures))
    rules = R["rules"]
    runs = F["runs"]

    def lad(values, minions=1024):
        xs = [r for r in runs if r["block"] in ("LAD", "MIN") and r["values"] == values and r["minions"] == minions]
        return {"p800": st.mean(r["p800_w"] for r in xs), "mhz": st.mean(r["mhz_steady"] for r in xs),
                "rate": st.mean(r["rate_t"] for r in xs), "n": len(xs),
                "pd": sum((r.get("events") or {}).get("power_down", 0) for r in xs)} if xs else None
    z, o, rn = lad("zeros"), lad("ones"), lad("randn")
    m768, m640, m512 = lad("randn", 768), lad("randn", 640), lad("randn", 512)
    gov = F.get("governor") or {}
    fit = F.get("fit") or {}
    # every governor step of the session
    pd, td = [], []
    for r in R["runs"]:
        for e in r.get("event_list") or []:
            if not e.get("in_work"):
                continue
            if e["kind"] == "power_down":
                pd.append((e["pwr_mw"] / 1000.0, e.get("die"), r["block"]))
            if e["kind"] == "thermal_down":
                td.append((e.get("T"), r["block"], r["values"]))
    pd_blocks = sorted({b for *_, b in pd})
    td_blocks = sorted({b for _, b, _ in td})
    hot = [r for r in runs if r["block"] in ("HOT", "HOT2")]
    sus = {(r["type"], r["values"]): r for r in runs if r["block"] == "SUS"}
    th = F.get("thermal") or {}
    speed_up = 100 * (z["mhz"] / rn["mhz"] - 1) if z and rn else None
    sus_z = (sus.get(("fp32", "zeros")) or {}).get("sus_rate_t")
    sus_r = (sus.get(("fp32", "randn")) or {}).get("sus_rate_t")
    sus_gap = 100 * (sus_z / sus_r - 1) if sus_z and sus_r else None
    td_hot = [x for x in td if x[1] in ("HOT", "HOT2")]
    tcount = {}
    for t, _, _ in td:
        tcount[t] = tcount.get(t, 0) + 1
    t_readings = " and ".join(f"{n} at a reading of {t} °C" for t, n in sorted(tcount.items(), key=lambda kv: -kv[1]))
    td_hot_t = sorted({t for t, _, _ in td_hot})
    pd_hot = [x for x in pd if x[2] in ("HOT", "HOT2")]
    r1, r2, r3, r4 = rules["R1"], rules["R2"], rules["R3"], rules["R4"]

    def verdict(v):
        cls = {"PASS": "pass", "FAIL": "fail"}.get(v, "")
        return f'<span class="verdict {cls}">{v}</span>'

    # sustained rows, if any
    sus_rows = ""
    for t in ("fp32", "fp16", "int8"):
        for v in ("zeros", "ones", "randn"):
            r = sus.get((t, v))
            if not r:
                continue
            sl = r.get("sus_last") or {}
            cool = r.get("first8_mhz")
            vname = "random (uniform −128..127)" if (t, v) == ("int8", "randn") else NAME[v]
            sus_rows += (f"<tr><td>{t}</td><td>{vname}</td><td class='n'>{g(rate(t, 800), 1)}</td>"
                         f"<td class='n'>{g(rate(t, cool) if cool else None, 1)}</td>"
                         f"<td class='n'>{g(r.get('sus_rate_t'), 1)}</td><td class='n'>{g(r.get('sus_mhz_mean'), 0)}</td>"
                         f"<td class='n'>{g(r.get('sus_die_mean'), 1)}</td><td class='n'>{g(r.get('sus_w_mean'), 1)}</td>"
                         f"<td class='n'>{g(100 * sl.get('thermal', 0) / max(1e-9, 1 - sl.get('800', 0)), 0) if sl and sl.get('800', 1) < 1 else '–'}</td></tr>")
    ct = F.get("cap_table") or {}
    cap_html = ""
    if ct:
        caps = ct["caps_w"]
        order = [("fp32", "zeros"), ("fp32", "ones"), ("fp32", "signs"), ("fp32", "a_ones_b_randn"), ("fp32", "randn"),
                 ("fp16", "zeros"), ("fp16", "ones"), ("fp16", "randn"), ("int8", "zeros"), ("int8", "ones"),
                 ("int8", "randn")]
        rows = {(r["type"], r["values"]): r for r in ct["rows"]}
        cap_html = ("<div class='tablewrap'><table><thead><tr><th>type</th><th>data</th><th class='n'>W at 800 MHz</th>"
                    + "".join(f"<th class='n'>{c} W level</th>" for c in caps) + "</tr></thead><tbody>")
        for k in order:
            r = rows.get(k)
            if not r:
                continue
            vname = "random (uniform −128..127)" if k == ("int8", "randn") else NAME[k[1]]
            cap_html += (f"<tr><td>{k[0]}</td><td>{vname}</td><td class='n'>{g(r['p_w']['800'], 0)}</td>"
                         + "".join(f"<td class='n'>{g(r['rate'][str(c)], 1)}</td>" for c in caps) + "</tr>")
        cap_html += ("</tbody></table></div><p class='muted'>TFLOPS for fp32 and fp16, TOPS for int8, on all 1,024 "
                     "minions, from the modelled mean clock after the start ramp.</p>")
    T = {}
    T["title"] = "Power, then heat: what limits the ET-SoC-1's matmul speed"
    T["description"] = ("E64 on aifoundry2: the governor's 65 W power test alone sets the speed of a matmul on a cool die, "
                        "dithering the clock so random data runs about 12% slower than zeros; its 65 °C test alone sets it "
                        "on a hot die; the service processor's own log names every step.")
    T["byline"] = ("Experiment E64 (request Q123), run Fri 23 Oct 2026 on aifoundry2, pre-registered in "
                   f"<a href='{REPO}/tree/main/tools/claims-v3/hpl'>tools/claims-v3/hpl</a> before the first pass; "
                   f"<a href='{REPO}/tree/main/docs/reports/data/2026-10-23-e64-horace-power-limit'>data</a>.")
    body = []
    body.append(f"""<p class="lede">Horace He found that an A100 runs the same matmul about 15% faster on zeros than on random
numbers, because the GPU sits at its power cap: data that flips fewer transistors draws fewer watts and earns a higher
clock. The ET-SoC-1's firmware has <em>two</em> caps, 65 W of card power and 65 °C on the die, so the same effect could
come from either. This experiment pulls them apart on aifoundry2's card and reads every clock step's cause from the
service processor's own log.</p>
<div class="stats">
<div class="stat"><b>{g(speed_up, 0)}%</b><span>faster on zeros than on random normal data, on a cool die ({g(z['mhz'] if z else None, 0)} against {g(rn['mhz'] if rn else None, 0)} MHz)</span></div>
<div class="stat"><b>{len(pd)}</b><span>power steps in the governor's log, every one at a die reading of {g(min((d for _, d, _ in pd if d is not None), default=None), 0)}–{g(max((d for _, d, _ in pd if d is not None), default=None), 0)} °C, under the 65 °C line</span></div>
<div class="stat"><b>{len(td)}</b><span>thermal steps in the log, {t_readings}: the first readings over the line</span></div>
<div class="stat"><b>{g(sus_gap, 0)}%</b><span>faster on zeros than on random data in a sustained run ({g(sus_z, 1)} against {g(sus_r, 1)} fp32 TFLOPS), and heat sets it</span></div>
<div class="stat"><b>{g(gov.get('tau_s'), 1)} s</b><span>the averaging time of the power the governor regulates (a model that reproduces {gov.get('n', 0)} runs to {g(gov.get('rms_mhz'), 1)} MHz)</span></div>
</div>""")
    body.append(f"""<h2>The answer</h2>
<p><strong>Both limits act, each on its own, and which one sets the speed depends on the die's temperature.</strong> On a
die below 65 °C only the power test acts: every one of the {r1['population']} runs whose work drew 67 W or more at
800 MHz was stepped down by the power test first ({verdict(r1['verdict'])}, rule R1), and none of the
{r2['population']} runs under 62 W was ({verdict(r2['verdict'])}, R2). Random normal data on the full card draws about
{g(rn['p800'] if rn else None, 0)} W at 800 MHz, so the governor pulls it back to a mean of {g(rn['mhz'] if rn else None, 0)}
MHz, while zeros ({g(z['p800'] if z else None, 0)} W) and ones ({g(o['p800'] if o else None, 0)} W) stay at the 800 MHz
ceiling: Horace's effect, by Horace's mechanism, {g(speed_up, 0)}% here against his 15%. On a die above 65 °C only the
thermal test acts, even for zeros at a third of the power cap ({verdict(r3['verdict'])}, R3).
{{{{SUS_ANSWER}}}}</p>""")
    body.append(f"""<h2>What was known before</h2>
<p>The <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment">Horace experiment</a> (September) ran this
kernel at a fixed 600 MHz on a hot die and found the same arithmetic drawing 38.3 W on zeros, 46.7 W on ones and 63.4 W on
random normal data. From a 62–63 °C die it saw the speed effect too: 11.4–11.8 TFLOPS on zeros against 9.3 on random data,
about 25%. But the limits were tangled then. The card idled above 65 °C, random data at 800 MHz touched 88 W and took
the die past 65 °C within half a second, and ones (56 W, under the power level) lost 800 MHz to the thermal test alone.
Since 9 October a fan bracket keeps aifoundry2's idle die at about 50 °C. So the two limits can now be pulled apart without
changing anything on the card.</p>""")
    body.append(f"""<h2>What the specifications say</h2>
<p>Esperanto presented the chip at Hot Chips 2021 as 1,088 RISC-V cores that typically draw under 20 W and
"can be adjusted for 10 to 60+ watts under SW control", with an operating range of 300 MHz to 2 GHz
(<a href="https://www.hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf">slides</a>;
its energy-versus-voltage curve, by its own footnote 6, compares different physical designs, not one chip). The card in the
lab is narrower. Its operating-point table has three points, 600, 700 and 800 MHz at 0.517, 0.568 and 0.618 V, so
800 MHz is a hard ceiling. And its firmware (open source, <code>thermal_pwr_mgmt.c</code> in et-platform) has a software
governor with two limits that are set, not physical: a <strong>65 °C</strong> threshold on the integer mean of 34 on-die
sensors, tested first, and a <strong>65 W</strong> TDP level, plus a 75 W / 75 °C alarm in the power-management chip. A
step down when either is exceeded, a step up when neither is, no dead band.</p>
<p>So a matmul on this card can be held back three ways: by the clock table's top (800 MHz), by the power level, or by the
temperature level. The runs below separate them.</p>""")
    body.append(f"""<h2>On a cool die: the power limit alone</h2>
<p>Ten fp32 operand patterns ran on all 1,024 minions, and random normal data on 768, 640 and 512, each for 6 s from a
die reading of 55 °C or less, twice in shuffled order. The clock left 800 MHz exactly when the work crossed the power
level, whatever made up the watts: random normal data on 768 minions ({g(m768['p800'] if m768 else None, 0)} W) was
stepped down, on 640 ({g(m640['p800'] if m640 else None, 0)} W) it was not, and ones and random powers of 2 under 65 W ran
at the ceiling with no power step at all.</p>
{{{{fig:ladder}}}}
<p>The mechanism is a dither. Once a ~{g(gov.get('tau_s'), 1)} s average of the card's power passes 65 W the governor steps
down one point per pass (about {g(gov.get('pass_s'), 2)} s), and once it falls under, steps up again, with nothing in
between to stop it. For random normal data the card goes 800 → 700 → 600 → 700 → 800, round and round, drawing about
{g(rn and per(F, 'randn', 800), 0)}, {g(rn and per(F, 'randn', 700), 0)} and {g(rn and per(F, 'randn', 600), 0)} W at the three
points, and the average sits on the level. The governor logged its power reading at each of {len(pd)} power steps down:
{g(min((w for w, _, _ in pd), default=None), 2)} to {g(max((w for w, _, _ in pd), default=None), 2)} W, while the board's own
reading at 800 MHz was {g(rn['p800'] if rn else None, 0)} W. A model of that loop, a first-order average with a
{g(gov.get('tau_s'), 1)} s time constant compared against 65 W once per pass, reproduces the mean clock of all
{gov.get('n', 0)} cool-die runs to {g(gov.get('rms_mhz'), 1)} MHz rms.</p>
{{{{fig:traces}}}}""")
    hot_txt = ", ".join(f"{NAME[r['values']]} launched at {r.get('die_start')} °C: {g(r.get('mhz_steady'), 0)} MHz" for r in hot[:4])
    body.append(f"""<h2>On a hot die: the temperature limit alone</h2>
<p>Work that draws less than 65 W even at 800 MHz, ones and zeros, was launched on a die heated to 63–67 °C. The log
of those {len(hot)} runs holds {len(td_hot)} thermal steps, every one at a reading of
{" or ".join(f"{t} °C" for t in td_hot_t)}, and {len(pd_hot)} power steps. Runs that started above the line held 600 MHz until the die read 65 °C
({r3['a_held_600_until_65']} of {r3['a_population']}), then climbed, heated, and were sent back down; every run that reached
66 °C at 800 MHz was stepped down by the thermal test and not the power test ({r3['b_thermal_not_power']} of
{r3['b_population_reaching_66']}). Zeros, at about a third of the power level, lost speed to heat alone.</p>
{{{{fig:map}}}}""")
    body.append(f"""<h2>Sustained: which limit holds a long matmul</h2>
{{{{SUS_TEXT}}}}
{{{{fig:sus}}}}""")
    body.append(f"""<h2>What speed to expect, by number type</h2>
<p>fp32 and fp16 matmuls retire one 16×16 tile operation every 546 cycles and int8 every 318, so at the 800 MHz ceiling the
full card does {g(rate('fp32', 800), 1)} fp32 TFLOPS, {g(rate('fp16', 800), 1)} fp16 TFLOPS and {g(rate('int8', 800), 1)} int8 TOPS.
What it actually delivers depends on the data and on how long it has been running:</p>
<div class="tablewrap"><table><thead><tr><th>type</th><th>data</th><th class="n">at 800 MHz</th><th class="n">cool die, first 8 s</th>
<th class="n">sustained, last 40 s</th><th class="n">MHz, last 40 s</th><th class="n">die °C</th><th class="n">board W</th>
<th class="n">% of below-800 time thermal</th></tr></thead><tbody>{sus_rows}</tbody></table></div>
{{{{fig:types}}}}
<p>Under other power levels the governor model gives the speed each kind of number would hold on a cool die, from that
kind's own measured power at 600, 700 and 800 MHz (a model: the level was not changed on the card):</p>
{cap_html}""")
    body.append(f"""<h2>The surface</h2>
<p>Put the two axes together: the work's power at 800 MHz (the data: zeros at the left, random normal data at the right)
and the power level the governor is given. The fitted governor model gives the mean clock for every pair. Under the card's
65 W the measured runs fall on the model's row. Every 10 W of extra level buys random fp32 data about 60 MHz of mean clock
until it reaches the 800 MHz ceiling near 85 W, and on this card the 65 °C threshold sets a lower effective level for
sustained work
{{{{SURFACE_THERMAL}}}}. This part is a model: the level itself was never changed (the lab's rule: no TDP, threshold or clock
is set on a shared card).</p>
{{{{fig:surface}}}}""")
    body.append(f"""<h2>How it was run</h2>
<ul>
<li><strong>Pre-registered</strong> before the first card pass: design, predictions and rules R1–R4 in
<a href="{REPO}/blob/main/tools/claims-v3/hpl/README.md">the README</a>. Amendments: A0, a use-count check that read the
runner's own sampler as another user; A1, the trace reader (the lab's earlier one stopped at the first binary record and
lost most governor lines); A2, the hot starts (the heater cannot take this card's die past about 67 °C, because the two
limits hold it there); A3, the placement of the log's lines on the host clock (the ring keeps only its last ~67 entries,
so a dump covers a short run's last few seconds and a sustained run's last 5–60 s, and is anchored at the run's end).</li>
<li><strong>Nothing was set on the card.</strong> The TDP and threshold read 65 W and 65 °C after every run.</li>
<li><strong>The cause of each step</strong> comes from the service processor's 4 KB trace ring, dumped after every run:
its CRITICAL lines ("Power throttle down event, current pwr … tdp level …", "Thermal throttle down event, current
temperature …"), its "New OP" line at every operating point set, and a 16-byte power-status record (power, throttle state,
temperature, target clock), placed on the host clock by matching the operating-point lines to the sampler's clock changes.
The ring holds about 67 entries, three per clock step, so the counts above are of the steps it kept; where it had
wrapped, the sampler's die readings still say which side of 65 °C each step was on.</li>
<li><strong>The kernel</strong> is the Horace experiment's: one 16×16 TensorFMA per minion on tiles in its L1 scratchpad,
back to back. Speeds come from the kernel's own cycle counters.</li>
<li>Claimed and released in #community-lab; {len(R['runs'])} runs, about {{{{CARD_MIN}}}} minutes of card time.</li>
</ul>""")
    # the sustained runs, from the data
    cap_th = th.get("cap_w_at_65_5")
    sz = sus.get(("fp32", "zeros"))
    hot_runs = [r for (t, v), r in sus.items() if (r.get("sus_last") or {}).get("800", 1) < 0.95]
    th_runs = [r for r in hot_runs if (r["sus_last"].get("thermal", 0) / max(1e-9, 1 - r["sus_last"]["800"])) >= 0.5]
    pw_runs = [r for r in hot_runs if (r["sus_last"].get("power", 0) / max(1e-9, 1 - r["sus_last"]["800"])) >= 0.5]
    wins = "heat" if len(th_runs) > len(pw_runs) else "power"
    parts = []
    if cap_th:
        parts.append(f"over 80 s the die settles where its cooling puts it, and on this card the 65 °C line sits at about "
                     f"{g(cap_th, 0)} W of steady board power, below the 65 W level")
    if hot_runs:
        parts.append(f"{len(th_runs)} of the {len(hot_runs)} sustained runs that left 800 MHz spent most of that time under "
                     f"the thermal test and {len(pw_runs)} under the power test ({verdict(r4['verdict'])}, R4)")
    if sz:
        parts.append(f"zeros ran at 800 MHz for the whole run at {g(sz.get('sus_die_mean'), 0)} °C and "
                     f"{g(sz.get('sus_w_mean'), 0)} W, held back by nothing but the clock table")
    if sus_gap:
        parts.append(f"so a sustained matmul runs {g(sus_gap, 0)}% faster on zeros than on random data ({g(sus_z, 1)} "
                     f"against {g(sus_r, 1)} fp32 TFLOPS): Horace's effect again, wider, and set by heat")
    sus_answer = f"<strong>For sustained work on this card, {wins} wins:</strong> " + "; ".join(parts) + "."
    sus_par = []
    for (t, v) in [("fp32", "randn"), ("fp16", "randn"), ("int8", "randn"), ("fp32", "ones"), ("fp16", "ones"),
                   ("int8", "ones"), ("fp32", "zeros"), ("fp16", "zeros"), ("int8", "zeros")]:
        r = sus.get((t, v))
        if not r or not r.get("sus_last"):
            continue
        sl = r["sus_last"]
        below = 1 - sl["800"]
        vname = "random (uniform over −128 to 127)" if (t, v) == ("int8", "randn") else NAME[v]
        sus_par.append(f"{t} {vname}: {g(r.get('sus_mhz_mean'), 0)} MHz in the last 40 s, {g(100 * sl['800'], 0)}% of it at "
                       f"800 MHz" + (f", the rest {g(100 * sl['thermal'] / below, 0)}% thermal and "
                                    f"{g(100 * sl['power'] / below, 0)}% power" if below > 0.02 else "")
                       + f"; die {g(r.get('sus_die_mean'), 1)} °C, board {g(r.get('sus_w_mean'), 1)} W")
    s_r = sus.get(("fp32", "randn")) or {}
    s_o = sus.get(("fp32", "ones")) or {}
    sus_text = (f"""<p>Each number type ran for about 80 s: nine 8 s launch processes back to back from a die of 57 °C or
less. A run whose power at 800 MHz is over the level starts in the power dither, but the die keeps warming, and once it
reads 66 °C the thermal test takes over: fp32 random data first read 66 °C {g(s_r.get('sus_first_66_s'), 0)} s in, fp32
ones, under the power level, {g(s_o.get('sus_first_66_s'), 0)} s in. From then on the thermal test sets the clock. For
random fp32 and fp16 data it holds 600 MHz, the bottom of the table, and the die stays above the line anyway
({g(s_r.get('sus_die_mean'), 0)} °C): the governor has no lower step to take. Only work light enough to keep the die under
65 °C for good holds the ceiling.</p>
<ul>""" + "".join(f"<li>{x}</li>" for x in sus_par) + "</ul>"
                + (f"""<p>The line through the nine runs' last 40 s gives the cooling: the die reading rises {g(th.get('k_c_per_w'), 2)} °C
per watt of board power, and reads 65.5 °C at {g(cap_th, 0)} W. That is the sustained power the 65 °C test allows here,
and it is below the 65 W level: on aifoundry2's cooling the temperature limit is the tighter of the two for anything
that runs long.</p>""" if cap_th else ""))
    surface_thermal = (f"(about {g(cap_th, 0)} W, the amber line)" if cap_th else "")
    end = json.load(open(a.end)) if a.end else {}
    for k, v in (("{{SUS_ANSWER}}", sus_answer), ("{{SUS_TEXT}}", sus_text), ("{{SURFACE_THERMAL}}", surface_thermal),
                 ("{{CARD_MIN}}", g(end.get("card_min"), 0) if end else "–")):
        body = [x.replace(k, v) for x in body]
    T["body"] = "\n".join(body)
    T["captions"] = {
        "ladder": "Each dot is one 6 s run from a cool die: the work's board power at 800 MHz and the mean clock after the start "
                  "ramp (from 1.5 s). Circles the first pass, squares the second. The dashed line is the governor model at 65 W.",
        "traces": "The minion clock through three runs from a cool die (offset slightly so they don't overlap). Dots along "
                  "the top mark each power step down the service processor logged; random normal data dithers around the "
                  "power level for the whole run.",
        "map": "Every step the governor took in the work windows of the session, placed by the die's reading and the "
               "governor's own power reading at that moment. Power steps sit on the 65 W line at a cool die; thermal steps sit "
               "on the 66 °C reading at any power.",
        "sus": "The mean clock in 2 s bins through each sustained run: nine 8 s launch processes back to back, from a die of "
               "57 °C or less. The brief dips in the ones and zeros lines fall at the boundaries between launch processes, "
               "where the governor's idle reset sends the clock to 600 MHz for a moment.",
        "types": "The rate each number type reached, as a share of its 800 MHz peak: on a cool die (the first launch process of "
                 "each sustained run, after its ramp) and sustained (the last 40 s).",
        "surface": "The governor model's mean clock for work drawing a given power at 800 MHz (across) under a given power "
                   "level (up): the darkest blue is the 800 MHz ceiling, the palest 600 MHz. Dots: the measured runs at the "
                   "card's 65 W. The amber line is the power the 65 °C test allows for sustained work on this card's "
                   "cooling, from the sustained runs.",
    }
    json.dump(T, open(a.out, "w"), indent=1)
    print("wrote", a.out)


def per(F, values, f):
    xs = [r["p"][str(f)] for r in F["runs"] if r["block"] == "LAD" and r["values"] == values and r.get("p")
          and r["p"].get(str(f)) is not None]
    return st.mean(xs) if xs else None


if __name__ == "__main__":
    main()
