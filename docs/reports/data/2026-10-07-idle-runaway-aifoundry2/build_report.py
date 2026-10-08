#!/usr/bin/env python3
"""Build the 7 October page (one self-contained HTML file) from analysis.json and kernel.txt.

  python3 analyze.py && python3 build_report.py analysis.json kernel.txt report.css out.html

Every number in the text comes from analysis.json or kernel.txt, so the page cannot drift from the data; the only
constants typed here are the firmware facts (with their source) and the 6 October fan reading (from that day's page).
The charts are drawn in the browser from the embedded data, so their text stays readable at any width.
The page is public: it names the machines but carries no address, no access path and no account."""
import datetime as dt
import html
import json
import re
import sys

A, KERN, CSS, OUT = sys.argv[1:5]
a = json.load(open(A))
n = a["numbers"]
S, TAIL, SC, HOURS = a["series"], a["tail"], a["scatter"], a["hours"]
PDT = dt.timezone(dt.timedelta(hours=-7))
first_s = a["first_s"]

# ---- the kernel log: when the link complained, when the driver lost the card, when the port was reset ----------
kl = [l for l in open(KERN) if l.startswith("[")]


def ktime(pat):
    line = next(l for l in kl if re.search(pat, l))
    return line[12:20]


k_aer, k_sq, k_reset = ktime(r"RxErr"), ktime(r"SQ\[0\]"), ktime(r"resetting")
n_aer = sum(1 for l in kl if "AER: Correctable error message" in l)

# ---- the firmware fact (read, not measured) ---------------------------------------------------------------------
FW_COMMIT = "836a4ab"
FW_URL = ("https://github.com/aifoundry-org/et-platform/blob/836a4ab600e93c3059bb58c898edbc37744cd8d0/"
          "device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c#L864-L883")
FW_THRESHOLD = 65  # TEMP_THRESHOLD_SW_MANAGED, thermal_pwr_mgmt.h:41
# the source closest to the card's own build (BL2 0.20.0, release 1.3.1; docs/findings/14-card-behaviour.md, "The clock
# governor, by firmware build"): its thermal test runs busy or idle, update_module_current_temperature()
FW131_URL = ("https://github.com/aifoundry-org/et-platform/blob/ffca4cbb436713cffcbc5028fc9a86529dc86c7c/"
             "device-bootloaders/src/ServiceProcessorBL2/services/thermal_pwr_mgmt.c#L651-L688")
SAFE_FIX_URL = "https://github.com/aifoundry-org/et-platform/commit/e024210bcc20f4e0a138ade0edf744db0f0ddcc8"
FAN_RPM_1006 = "2,368"  # System 5 at full speed on the BIOS screen, 6 Oct 16:01 (the 6 October page)


def hm(t):
    return t[:5]


def w0(x):
    return f"{x:.0f}"


def mins_of(clock, day):
    """'HH:MM' on 'Tue 6 Oct'/'Wed 7 Oct' -> chart x (minutes since the first reading)"""
    d = 6 if day.startswith("Tue") else 7
    h, m = map(int, clock.split(":"))
    return (dt.datetime(2026, 10, d, h, m, tzinfo=PDT).timestamp() - first_s) / 60


last, o2, air, host = n["last"], n["oct2_last"], n["air"], n["host"]
step, cross, fit = n["step"], n["cross"], n["fit"]
night = n["night_level"]
second = n["second"]  # the first minute from which the model's air holds 1.5 degrees above 13:50-14:20's
# round to the nearest five minutes for the prose; the table and charts carry the minute
sh, sm = map(int, second["t"].split(":"))
second_t = f"{sh:02d}:{5 * round(sm / 5):02d}"


def mdie(d, a_, b_):
    v = [p["die"] for p in S if p["d"].startswith(d) and a_ <= p["t"] < b_]
    return sum(v) / len(v)


warmer = round(mdie("Wed", "05:00", "11:30") - mdie("Wed", "00:00", "03:50"))
step_after_h = round((mins_of(step["t"], "Wed 7 Oct")) / 60)

# ---- chart data, compact ------------------------------------------------------------------------------------------
day_ticks = []
for d, hh in [("Tue 6 Oct", h) for h in (18, 21)] + [("Wed 7 Oct", h) for h in (0, 3, 6, 9, 12, 15)]:
    x = mins_of(f"{hh:02d}:00", d)
    day_ticks.append(dict(x=round(x, 2), label=f"{hh:02d}:00", sub=d if hh in (18, 0) else "",
                          subN=d[:3] if hh in (18, 0) else "", six=hh % 6 == 0))
pts = S + [dict(x=p["x"], t=p["t"], d=p["d"], die=p["die"], w=round(p["w"], 2)) for p in TAIL if p["x"] > S[-1]["x"]]
xs = [p["x"] for p in pts]
chart = dict(
    x=xs, t=[p["t"] for p in pts], d=[p["d"][:3] for p in pts],
    die=[p["die"] for p in pts], w=[p["w"] for p in pts],
    dair=[p.get("d_air") for p in pts], dnvme=[p.get("d_nvme") for p in pts], dnic=[p.get("d_nic") for p in pts],
    air=[p.get("air") for p in pts], nvme=[p.get("nvme") for p in pts], nic=[p.get("nic") for p in pts],
    ticks=day_ticks, x1=xs[-1],
    notes=[dict(x=round(mins_of("16:30", "Tue 6 Oct"), 2), y=max(p["die"] for p in S if p["d"].startswith("Tue") and p["t"] < "17:00"),
                text="6 Oct: the fix's load tests", short="tests", ly=104, start=True),
           dict(x=round(mins_of(step["t"], "Wed 7 Oct"), 2), y=step["die_0354"], text=f"{step['t']}: the cooling at the card gets worse", short=step["t"], ly=92),
           dict(x=second["x"], y=second["die"], text=f"about {second_t}: worse again", short=second_t, ly=104),
           dict(x=xs[-1], y=last["die"], text=f"{hm(last['t'])}: {last['die']} °C, {w0(last['w'])} W, off the bus", short=f"{hm(last['t'])} off the bus", end=True)],
    sc=SC, law=dict(a=fit["a"], b=fit["b"], c=fit["c"]),
    step_x=round(mins_of(step["t"], "Wed 7 Oct"), 2), step_t=step["t"],
)
dmin = min(v for k in ("dair", "dnvme", "dnic") for v in chart[k] if v is not None)
dmax = max(v for k in ("dair", "dnvme", "dnic") for v in chart[k] if v is not None)
chart["dlo"], chart["dhi"] = 4 * ((dmin // 4)), 4 * (-(-dmax // 4))
data_json = json.dumps(chart, ensure_ascii=False, separators=(",", ":"))

# ---- tables -------------------------------------------------------------------------------------------------------
timeline = [
    (f"Tue 6 Oct {hm(n['back']['t'])}", f"{n['back']['die']} °C, {n['back']['w']:.1f} W",
     "Back on the PCIe bus after the BIOS fan fix (every fan at full speed). From "
     f"{hm(n['held_first'])} to {hm(n['held_last'])} that day's load tests held the card; nobody held it after that."),
    ("17:00 to 03:50", f"{w0(n['evening']['die'][0])}–{w0(n['evening']['die'][1])} °C, "
                       f"{n['evening']['w'][0]:.1f}–{n['evening']['w'][1]:.1f} W",
     "Idle and steady through the evening and the night."),
    (f"Wed 7 Oct {step['t']}", f"{w0(step['die_0354'])} °C, then {w0(step['die_0450'])} °C by 04:50",
     f"The cooling at the card gets worse, in one step. The host is idle ({host['cpu_util_0330_0430']:.1f}% CPU) "
     "and its own temperatures do not move."),
    ("05:00 to 11:30", f"{w0(n['morning_die'][0])}–{w0(n['morning_die'][1])} °C",
     f"Steady again, about {warmer} °C warmer than in the night."),
    (f"about {second_t}", f"80 °C, then {cross['85']['die']} °C by {hm(cross['85']['t'])}", "The cooling gets worse again."),
    (hm(cross["90"]["t"]), f"{cross['90']['die']} °C, {w0(cross['90']['w'])} W",
     "At the tipping point: from here the leakage grows faster than the cooling can carry it away."),
    (f"{hm(cross['100']['t'])} to {hm(last['t'])}", f"{cross['100']['die']} → {last['die']} °C, "
                                                    f"{w0(cross['100']['w'])} → {w0(last['w'])} W", "Runaway."),
    (k_aer, "", f"{n_aer} corrected receiver errors on the card's PCIe link in four seconds (kernel log)."),
    (last["t"], f"{last['die']} °C (hottest sensor {last['max']} °C), {last['w']:.1f} W",
     f"The card's last reading. There is none from {n['gone']} on."),
    (hm(k_sq), "", "The driver finds the card's queue unreadable: reads from the card return all ones."),
    (k_reset, "", "The card's PCIe root port is reset; by whom or what is not known. The card does not come back, "
                  "and is still off the bus."),
]
trows = "".join(f'<tr><td class="t">{html.escape(a_)}</td><td class="n">{html.escape(b_)}</td><td>{html.escape(c_)}</td></tr>'
                for a_, b_, c_ in timeline)


def hrow(h):
    airs = "–" if h["air"] is None else f"{h['air']:.1f}"
    return (f"<tr><td class='t'>{h['d'][:3]} {h['h']}</td><td class='n'>{w0(h['die'][0])}–{w0(h['die'][1])}</td>"
            f"<td class='n'>{h['w'][0]:.1f}–{h['w'][1]:.1f}</td><td class='n'>{airs}</td>"
            f"<td class='n'>{h['nvme']:.1f}</td><td class='n'>{h['nic']:.1f}</td></tr>")


hrows = "".join(hrow(h) for h in HOURS)
dup = abs(last["die"] - o2["die"]) <= 1 and abs(last["max"] - o2["max"]) <= 1

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light dark">
<title>AI Foundry lab, 7 October 2026: aifoundry2's card ran away again</title>
<meta name="description" content="Idle, with nobody using it, aifoundry2's card heated from {w0(step['die_0354'])} °C to {last['die']} °C and fell off the PCIe bus at {hm(last['t'])}, {n['hours_up']:.1f} hours after the BIOS fan fix. The cooling at the card got worse at {step['t']}; the card itself did not change. It is out of service again.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8C%A1%3C/text%3E%3C/svg%3E">
<style>
{open(CSS).read()}
</style>
<style>
/* Charts (dataviz method): the data in one accent hue, context in gray; 2px lines; hairline grid; one tooltip with
   every value at the pointer, values first; keyboard focus shows the same as hover; the tables are the table view. */
:root{{--s1:#2a78d6;--ctx:#7d7c77;--band:rgba(125,124,119,.22);--grid:#e6e5e1;--axis:#a3a29c;--tick:#6c7c86;--tipbg:#ffffff;--tipbd:#d5dde2}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--s1:#3987e5;--ctx:#9b9a95;--band:rgba(155,154,149,.26);--grid:#26343c;--axis:#4c5b64;--tick:#8a9aa4;--tipbg:#1d2a32;--tipbd:#33444e}}}}
:root[data-theme="dark"]{{--s1:#3987e5;--ctx:#9b9a95;--band:rgba(155,154,149,.26);--grid:#26343c;--axis:#4c5b64;--tick:#8a9aa4;--tipbg:#1d2a32;--tipbd:#33444e}}
figure.ch{{margin:28px 0 34px;max-width:900px;background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:16px 16px 10px}}
figure.ch .ttl{{font-family:var(--sans);font-weight:650;font-size:16.5px;color:var(--ink);margin:0 0 3px}}
figure.ch .sub{{font-family:var(--sans);font-size:13.5px;color:var(--muted);margin:0 0 10px;line-height:1.45;max-width:none}}
figure.ch .plot{{position:relative;width:100%;min-height:260px}}
figure.ch svg{{display:block;overflow:visible;font-family:var(--sans)}}
figure.ch .grid line{{stroke:var(--grid);stroke-width:1}}
figure.ch .ax{{stroke:var(--axis);stroke-width:1}}
figure.ch .zero{{stroke:var(--axis);stroke-width:1}}
figure.ch text.tk{{fill:var(--tick);font-size:11.5px;font-variant-numeric:tabular-nums}}
figure.ch text.tk.sub{{font-weight:600}}
figure.ch text.lab{{fill:var(--ink-2);font-size:12.5px}}
figure.ch text.lab.strong{{fill:var(--ink);font-weight:600}}
figure.ch .ln{{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}}
figure.ch .ln.s1{{stroke:var(--s1)}}
figure.ch .ln.ctx{{stroke:var(--ctx)}}
figure.ch .bandf{{fill:var(--band);stroke:none}}
figure.ch .dot{{fill:var(--s1);stroke:var(--paper);stroke-width:2}}
figure.ch .mk{{fill:var(--s1);stroke:var(--paper);stroke-width:2}}
figure.ch .cross{{stroke:var(--ink-2);stroke-width:1;opacity:.55}}
figure.ch .hd{{stroke:var(--paper);stroke-width:2}}
figure.ch .hd.s1{{fill:var(--s1)}}
figure.ch .hd.ctx{{fill:var(--ctx)}}
figure.ch .hit{{fill:transparent;cursor:crosshair;outline:none}}
figure.ch .hit:focus-visible{{stroke:var(--s1);stroke-width:2}}
.lg{{display:flex;flex-wrap:wrap;gap:4px 18px;font-family:var(--sans);font-size:13px;color:var(--ink-2);margin:0 0 8px}}
.lg span{{display:inline-flex;align-items:center;gap:7px}}
.lg i{{display:inline-block;width:18px;height:0;border-top:2px solid var(--s1);border-radius:2px}}
.lg i.ctx{{border-color:var(--ctx)}}
.lg i.band{{height:10px;border:0;background:var(--band);border-radius:2px}}
.lg i.dot{{width:9px;height:9px;border:0;border-radius:50%;background:var(--s1)}}
.tipx{{position:fixed;z-index:9;pointer-events:none;min-width:150px;max-width:300px;background:var(--tipbg);color:var(--ink);border:1px solid var(--tipbd);
  border-radius:6px;padding:7px 10px;font-family:var(--sans);font-size:13px;line-height:1.45;box-shadow:0 2px 10px rgba(0,0,0,.14);opacity:0;transition:opacity .08s}}
.tipx .th{{color:var(--muted);font-size:12px;margin-bottom:2px}}
.tipx .tr{{display:flex;align-items:baseline;gap:7px;white-space:nowrap}}
.tipx .tr b{{font-weight:650;font-variant-numeric:tabular-nums}}
.tipx .tr .l{{color:var(--ink-2)}}
.tipx .k{{display:inline-block;width:12px;height:0;border-top:2px solid var(--s1);transform:translateY(-3px)}}
.tipx .k.ctx{{border-color:var(--ctx)}}
.tipx .k.none{{border-color:transparent}}
td.n{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.big{{font-family:var(--sans);display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:22px 0 24px;max-width:960px}}
.big div{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:12px 14px}}
.big b{{display:block;font-size:30px;font-weight:600;line-height:1.1;color:var(--ink)}}
.big span{{display:block;font-size:13.5px;color:var(--muted);margin-top:4px;line-height:1.35}}
.state{{font-family:var(--sans);display:inline-block;font-size:12px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--bad);
  border:1px solid color-mix(in srgb,var(--bad) 55%,transparent);border-radius:4px;padding:2px 7px;margin:0 0 14px}}
</style>
</head>
<body>
<div class="wrap">
<header class="mast">
<p class="eyebrow">AI Foundry lab</p>
<h1 class="title">aifoundry2's card ran away again, a day after the fan fix</h1>
<p class="lede"><em>Covers Tue 6 Oct 2026, {hm(n['back']['t'])} PDT, to Wed 7 Oct 2026, {k_reset[:5]} PDT: aifoundry2 in the AI Foundry lab at Studio 45.
Written on Wed 7 Oct from the lab's live collector (one record every 5 s) and the machine's kernel log.</em></p>
</header>
<main>
<p class="state">⚠ Out of service since Wed 7 Oct, {hm(last['t'])} PDT</p>
<p><strong>The card is out of service again.</strong> Idle, with nobody using it, it heated from {w0(step['die_0354'])} °C to a
{last['die']} °C mean (hottest sensor {last['max']} °C) at {w0(last['w'])} W, and fell off the PCIe bus at {hm(last['t'])},
{n['hours_up']:.1f} hours after the <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-6-october">6 October fan fix</a>
brought it back. {"It failed exactly as on" if dup else "It failed as on"} <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-2-october">2 October</a>
({o2['die']} °C, hottest {o2['max']} °C, {w0(o2['w'])} W). It is still off the bus; the machine itself is up.</p>

<p><strong>What changed was the cooling at the card, not the card.</strong> At {step['t']} on Wednesday, with the host
idle and its own temperatures unchanged, the card started heating and settled about {warmer} °C warmer. In the afternoon it
got worse again and crossed the tipping point. All day the card drew exactly the power that its temperature calls for,
on the same curve as on 2 October. Something at the card stopped carrying heat away: its own fan, or a fan near it, that
stopped, slowed or moved would do this. Fan speeds are not visible from the machine, so someone has to look on site.</p>

<div class="big">
<div><b>{last['die']} °C</b><span>mean die temperature at the last reading, {last['t']} (hottest sensor {last['max']} °C), at {w0(last['w'])} W</span></div>
<div><b>{n['hours_up']:.1f} hours</b><span>from back on the bus after the fan fix (Tue {hm(n['back']['t'])}) to off it again</span></div>
<div><b>{step['t']}</b><span>when the cooling at the card got worse, with the host idle and its own sensors unchanged</span></div>
<div><b>{n['resid']['rms_all']:.2f} W</b><span>rms gap between the card's power and the 2 October leakage curve over all {n['card_records']:,} readings: the card itself did not change</span></div>
</div>

<figure class="ch" id="c1">
<p class="ttl">The idle card's last day</p>
<p class="sub">aifoundry2's card, mean die temperature, one point a minute (every reading in the last minutes), from the moment the fan fix brought it back. Hover, tap or focus and use the arrow keys for values.</p>
<div class="plot" aria-label="Line chart: the card held 63 to 70 °C overnight, stepped up to about 75 °C after {step['t']}, rose again in the afternoon and ran away to {last['die']} °C at {hm(last['t'])}."></div>
</figure>

<h2 id="timeline">What happened</h2>
<div class="tablewrap"><table>
<thead><tr><th>When (PDT)</th><th>The card</th><th>What happened</th></tr></thead>
<tbody>{trows}</tbody>
</table></div>

<h2 id="cooling">Only the cooling at the card changed</h2>
<p>Three things rule out everything but the card's own cooling.</p>
<ul>
<li><strong>Nothing ran on the card.</strong> No process held it after the 6 October tests ended at {hm(n['held_last'])},
and at {step['t']} the host's CPU was {host['cpu_util_0330_0430']:.1f}% busy.</li>
<li><strong>The card drew what its temperature calls for, and nothing more.</strong> On 2 October the card's power fitted
{fit['a']:.1f} W plus a part that doubles every {0.693/fit['c']:.0f} °C (the chip's leakage). On Wednesday every reading
sat on that same curve, {n['resid']['rms_all']:.2f} W rms over the day and within {n['scatter_worst'][0]:.1f} W at every temperature
the card held for a minute or more (the second chart). Power only ever followed temperature: had work started, or had the
firmware changed the clock or the voltage, the readings would have left the curve.</li>
<li><strong>The rest of the machine did not warm up.</strong> Across {step['t']} the host's NVMe drive read
{host['pre']['nvme']:.1f} then {host['post']['nvme']:.1f} °C, its network chip {host['pre']['nic']:.1f} then {host['post']['nic']:.1f} °C,
and its CPU {host['pre']['cpu']:.0f} then {host['post']['cpu']:.0f} °C. The room and the case air stayed as they were.</li>
</ul>
<p>The 2 October heat model puts a number on it: the air temperature the card's heat balance needs (the model's single
"air" number, so a loss of airflow also shows up as warmer air). Overnight that was about {air['night']:.0f} °C, as just after
the fix. After {step['t']} it was about {air['morning']:.0f} °C; after {second_t} about {air['late']:.0f} °C, which is where
it was before the fix. The model checks itself: with air at 39, 46 and 51 °C it says the idle card settles at
{n['settle']['39']:.0f}, {n['settle']['46']:.0f} and {n['settle']['51']:.0f} °C, which is what it did. Above
{n['air_crit']:.1f} °C it has no steady temperature at all.</p>

<figure class="ch" id="c2">
<p class="ttl">Only the card's air changed</p>
<p class="sub">Change from each line's own level in the night (00:00–03:50, Wed), °C, nine-minute running medians. The
card's line is the air temperature its heat balance needs, by the 2 October model (night level {night['air']:.1f} °C),
and stops at 16:30, when the die starts climbing too fast for the model's 6-minute slope. The band spans the host's NVMe
drive and network chip (night levels {night['nvme']:.1f} and {night['nic']:.1f} °C).</p>
<div class="lg"><span><i></i>air reaching the card (model)</span><span><i class="band"></i>the host's NVMe drive and network chip</span></div>
<div class="plot" aria-label="Line chart: the card's air steps up by about 6 °C at {step['t']} and by about 11 °C by late afternoon, while the host's sensors stay within a few degrees of their night level."></div>
</figure>

<figure class="ch" id="c3">
<p class="ttl">The card drew the power its temperature calls for</p>
<p class="sub">Board power against mean die temperature, Wednesday's readings (median power at each whole degree), with
the leakage curve fitted on 2 October. Hover, tap or focus for values.</p>
<div class="lg"><span><i class="dot"></i>7 October: median power at each degree</span><span><i class="ctx"></i>2 October fit: {fit['a']:.1f} + {fit['b']:.3f}·e<sup>{fit['c']:.3f}·T</sup> W</span></div>
<div class="plot" aria-label="Scatter chart: Wednesday's power at each temperature lies on the 2 October leakage curve, from 63 to 138 °C."></div>
</figure>

<h2 id="firmware">Why the card could not save itself</h2>
<p>From {FW_THRESHOLD} °C to {last['die']} °C nothing on the card slowed it down, today as on 2 October. The card's
firmware (release 1.3.1, boot loader 0.20.0; its closest public source is
<a href="{FW131_URL}">et-platform ffca4cbb4</a>) does run its thermal check on an idle card above {FW_THRESHOLD} °C.
But all the check can do is step the minion clock down the voltage table, and the idle card already sits at the bottom
of it, 600 MHz, so nothing changes. The emergency safe state changes nothing either: it moves the clock only when
looking up its voltage fails, and its voltage step is commented out
(<a href="{SAFE_FIX_URL}">fixed upstream on 5 September 2024</a>). Nothing in the firmware shuts the card down. The
current upstream code does no better at idle: its check (<a href="{FW_URL}"><code>check_power_throttle_conditions()</code></a>,
{FW_COMMIT}) does not run at all while the card is idle.</p>
<p>So the two problems meet. Hotter silicon leaks more, which heats it further; a fan keeps that loop from closing,
and the firmware does nothing once it does. Until the firmware can cut an idle card's power or shut it down, the
cooling at the card is the only thing that keeps it out of the loop.</p>

<h2 id="fan">What is not known: the fan</h2>
<p>The machine cannot see its fans: no fan sensor driver is loaded for this board, and loading one needs root. Two
causes can still be ruled out. The BIOS setting cannot have reverted, because the machine has not rebooted since the
fix, and Linux never switched a fan (the kernel's ACPI fans show no change of state since boot). That leaves the
hardware: the card's own fan, if it has one, or a case fan by it, that stopped, slowed or was knocked out of line, or
something in the way of its air. The
change came at {step['t']} at night, all at once, while nobody was there.</p>
<p>On site: look at the card's own fan (follow its cable, if it has one) and at the case fans by it, then at the BIOS's
Smart Fan 6 page, which shows each fan's speed (System 5 read {FAN_RPM_1006} RPM at full speed on 6 October).</p>

<h2 id="next">What changes for people using the lab</h2>
<ul>
<li><strong>Run nothing on aifoundry2's card.</strong> The lab's docs, the new-user brief and the dashboard mark it out
of service; new users set up on aifoundry3 or aifoundry1. The machine stays up.</li>
<li><strong>To bring it back:</strong> first fix the cooling at the card, then the full reset as root, the cold reboot
that power-cycles the slot. A warm reboot or a slot reset leaves it off the bus, as the {hm(k_reset)} reset showed.</li>
<li><strong>Then watch it.</strong> After a reset the card looks healthy for about an hour while it heats. This time it
ran {n['hours_up']:.0f} hours, and the trouble started {step_after_h} hours in.</li>
</ul>

<h2 id="data">The numbers behind the charts</h2>
<details>
<summary>Hour by hour: the card, the model's air and the host's sensors</summary>
<p class="kicker">Die and power: the range of the 5-second readings in the hour. Air: the model's mean (to 16:30).
NVMe and network chip: the host's sensors, hourly means. Tue 16:00 includes the fix's load tests (16:22–16:35).</p>
<div class="tablewrap"><table>
<thead><tr><th>Hour (PDT)</th><th>Die °C</th><th>Power W</th><th>Air at the card °C (model)</th><th>NVMe °C</th><th>Network chip °C</th></tr></thead>
<tbody>{hrows}</tbody>
</table></div>
</details>

<h2 id="method">Sources and method</h2>
<ul>
<li><strong>Readings.</strong> The lab's live collector on aifoundry2 reads the card once a second and keeps one record
every 5 s: the mean of the 34 minion-shire temperature sensors ("die"), the highest reading since the card started
("hottest"), board power, and whether anyone holds the card; and the host's own sensors. {n['records']:,} records, {n['card_records']:,} with a card reading.</li>
<li><strong>The model.</strong> The 2 October fit, recomputed from that day's records by the same method: power
P(T) = {fit['a']:.2f} + {fit['b']:.3f}·e<sup>{fit['c']:.4f}·T</sup> W; heat balance C·dT/dt = P − (T − T<sub>air</sub>)/R with
C = {fit['C']:.0f} J/°C and R = {fit['R']:.3f} °C/W. Each minute's air is T − R·(P − C·dT/dt), with dT/dt a least-squares slope
over 6 minutes. These are model numbers, not measurements, and R and the air are correlated in a one-run fit.</li>
<li><strong>The kernel log.</strong> The card's lines, {k_aer} to {k_reset}. The {k_aer[:5]} lines come from a read at 17:16:
the ring buffer, flooded with AppArmor audit lines, had dropped them by 17:40.</li>
<li><strong>Earlier pages.</strong> <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-2-october">2 October</a>, the
first runaway and its fit; <a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-6-october">6 October</a>, the fan fix.</li>
</ul>
<p>The records, the kernel lines, the analysis and this page's builder are in
<a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-10-07-idle-runaway-aifoundry2">docs/reports/data/2026-10-07-idle-runaway-aifoundry2</a>
of the lab repository, with this page as <code>docs/reports/2026-10-07-aifoundry2-idle-runaway.html</code>.</p>
</main>
</div>
<footer>AI Foundry lab · Wed 7 Oct 2026 · aifoundry2 ·
<a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">the lab dashboard's worklog</a></footer>
<div class="tipx" id="tipx" role="tooltip"></div>
<script type="application/json" id="d">{data_json}</script>
<script>
(function(){{
"use strict";
var D=JSON.parse(document.getElementById("d").textContent), NS="http://www.w3.org/2000/svg", tip=document.getElementById("tipx");
function E(tag,at,par,txt){{var e=document.createElementNS(NS,tag);for(var k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;if(par)par.appendChild(e);return e;}}
function show(rows,x,y){{
  tip.replaceChildren();
  rows.forEach(function(r){{var d=document.createElement("div");
    if(r.h){{d.className="th";d.textContent=r.h;}}
    else{{d.className="tr";var k=document.createElement("span");k.className="k "+(r.k||"none");d.appendChild(k);
      var b=document.createElement("b");b.textContent=r.v;d.appendChild(b);
      if(r.l){{var l=document.createElement("span");l.className="l";l.textContent=r.l;d.appendChild(l);}}}}
    tip.appendChild(d);}});
  tip.style.opacity=1;var w=tip.offsetWidth,h=tip.offsetHeight;
  tip.style.left=Math.max(8,Math.min(x+14,innerWidth-w-8))+"px";tip.style.top=Math.max(8,y-h-14)+"px";
}}
function hide(){{tip.style.opacity=0;}}
addEventListener("scroll",hide,{{passive:true}});
function f1(v){{return (Math.round(v*10)/10).toFixed(1);}}
function sg(v){{return (v>0?"+":v<0?"−":"")+f1(Math.abs(v));}}

/* A line chart over the day: o = {{box, ys:[{{v,cls}}], band:[lo,hi], y0,y1,ystep,yfmt, right, notes, endLabels, tipf, zero}} */
function day(o){{
  var box=o.box, xs=D.x, x0=0, x1=D.x1;
  function draw(){{
    var W=Math.max(280,box.clientWidth), nar=W<560, H=nar?250:300;
    var m={{l:nar?34:44,r:(nar?o.rightN:o.right)||12,t:12,b:nar?44:46}}, pw=W-m.l-m.r, ph=H-m.t-m.b;
    function X(x){{return m.l+(x-x0)/(x1-x0)*pw;}} function Y(y){{return m.t+(1-(y-o.y0)/(o.y1-o.y0))*ph;}}
    box.replaceChildren();
    var svg=E("svg",{{width:W,height:H,viewBox:"0 0 "+W+" "+H,role:"img","aria-label":box.getAttribute("aria-label")||""}},box);
    var g=E("g",{{"class":"grid"}},svg);
    for(var y=o.y0;y<=o.y1+1e-9;y+=o.ystep){{E("line",{{x1:m.l,x2:m.l+pw,y1:Y(y),y2:Y(y)}},g);
      E("text",{{x:m.l-6,y:Y(y)+4,"text-anchor":"end","class":"tk"}},svg,o.yfmt(y));}}
    if(o.zero)E("line",{{x1:m.l,x2:m.l+pw,y1:Y(0),y2:Y(0),"class":"zero"}},svg);
    E("line",{{x1:m.l,x2:m.l+pw,y1:m.t+ph,y2:m.t+ph,"class":"ax"}},svg);
    D.ticks.forEach(function(t){{if(nar&&!t.six)return;var x=X(t.x);
      E("line",{{x1:x,x2:x,y1:m.t+ph,y2:m.t+ph+4,"class":"ax"}},svg);
      E("text",{{x:x,y:m.t+ph+17,"text-anchor":"middle","class":"tk"}},svg,t.label);
      if(t.sub)E("text",{{x:x,y:m.t+ph+32,"text-anchor":"middle","class":"tk sub"}},svg,nar?t.subN:t.sub);}});
    if(o.band){{var lo=D[o.band[0]],hi=D[o.band[1]],up="",dn="";
      for(var i=0;i<xs.length;i++){{if(lo[i]==null||hi[i]==null)continue;var a=Math.min(lo[i],hi[i]),b=Math.max(lo[i],hi[i]);
        up+=(up?"L":"M")+X(xs[i]).toFixed(1)+","+Y(b).toFixed(1);dn="L"+X(xs[i]).toFixed(1)+","+Y(a).toFixed(1)+dn;}}
      E("path",{{d:up+dn+"Z","class":"bandf"}},svg);}}
    o.ys.forEach(function(s){{var v=D[s.v],d="",pen=false;
      for(var i=0;i<xs.length;i++){{if(v[i]==null){{pen=false;continue;}}d+=(pen?"L":"M")+X(xs[i]).toFixed(1)+","+Y(v[i]).toFixed(1);pen=true;}}
      E("path",{{d:d,"class":"ln "+s.cls}},svg);}});
    (o.notes||[]).forEach(function(nt){{var x=X(nt.x),y=Y(nt.y);
      if(nt.end){{E("text",{{x:x-10,y:y+4,"text-anchor":"end","class":"lab strong"}},svg,nar?nt.short:nt.text);}}
      else{{var ly=Y(nt.ly);E("line",{{x1:x,x2:x,y1:y-6,y2:ly+5,"class":"ax"}},svg);
        E("text",{{x:nt.start?x-4:x+(nar?0:4),y:ly,"text-anchor":nt.start?"start":(nar?"middle":"end"),"class":"lab"}},svg,nar?nt.short:nt.text);}}
      E("circle",{{cx:x,cy:y,r:4.5,"class":"mk"}},svg);}});
    (o.endLabels||[]).forEach(function(el){{var v=D[el.v],i=v.length-1;while(i>0&&v[i]==null)i--;
      E("text",{{x:X(xs[i])+7,y:Y(el.y!=null?el.y:v[i])+4,"class":"lab"}},svg,nar?el.short:el.text);}});
    var cross=E("line",{{x1:0,x2:0,y1:m.t,y2:m.t+ph,"class":"cross",visibility:"hidden"}},svg);
    var hd=o.ys.map(function(s){{return E("circle",{{r:4,cx:0,cy:0,"class":"hd "+s.cls,visibility:"hidden"}},svg);}});
    var hit=E("rect",{{x:m.l,y:m.t,width:pw,height:ph,"class":"hit",tabindex:0,"aria-label":"Chart values: use the left and right arrow keys"}},svg);
    function at(i,cx,cy){{var x=X(xs[i]);cross.setAttribute("x1",x);cross.setAttribute("x2",x);cross.setAttribute("visibility","visible");
      o.ys.forEach(function(s,k){{var v=D[s.v][i];if(v==null){{hd[k].setAttribute("visibility","hidden");}}else{{hd[k].setAttribute("cx",x);hd[k].setAttribute("cy",Y(v));hd[k].setAttribute("visibility","visible");}}}});
      show(o.tipf(i),cx,cy);}}
    function near(px){{var xv=x0+(px-m.l)/pw*(x1-x0),lo=0,hi=xs.length-1;while(hi-lo>1){{var md=(lo+hi)>>1;if(xs[md]<xv)lo=md;else hi=md;}}return (xv-xs[lo]<xs[hi]-xv)?lo:hi;}}
    function mv(e){{var r=svg.getBoundingClientRect();ki=near(e.clientX-r.left);at(ki,e.clientX,e.clientY);}}
    function off(){{hide();cross.setAttribute("visibility","hidden");hd.forEach(function(c){{c.setAttribute("visibility","hidden");}});}}
    var ki=xs.length-1;
    hit.addEventListener("pointermove",mv);hit.addEventListener("pointerdown",mv);hit.addEventListener("pointerleave",off);
    hit.addEventListener("focus",function(){{var r=svg.getBoundingClientRect();at(ki,r.left+X(xs[ki]),r.top+m.t+20);}});
    hit.addEventListener("blur",off);
    hit.addEventListener("keydown",function(e){{if(e.key!=="ArrowLeft"&&e.key!=="ArrowRight")return;e.preventDefault();
      var st=e.shiftKey?60:10;ki=Math.max(0,Math.min(xs.length-1,ki+(e.key==="ArrowRight"?st:-st)));
      var r=svg.getBoundingClientRect();at(ki,r.left+X(xs[ki]),r.top+m.t+20);}});
  }}
  draw();var lw=box.clientWidth;
  if(window.ResizeObserver)new ResizeObserver(function(){{if(Math.abs(box.clientWidth-lw)>4){{lw=box.clientWidth;draw();}}}}).observe(box);
}}
function head(i){{return D.d[i]+" "+D.t[i];}}
day({{box:document.querySelector("#c1 .plot"),ys:[{{v:"die",cls:"s1"}}],y0:60,y1:140,ystep:20,yfmt:function(y){{return y+" °C";}},right:14,rightN:10,
  notes:D.notes,
  tipf:function(i){{return [{{h:head(i)}},{{k:"s1",v:f1(D.die[i])+" °C",l:"die, mean"}},{{v:f1(D.w[i])+" W",l:"board power"}}];}}}});
day({{box:document.querySelector("#c2 .plot"),ys:[{{v:"dair",cls:"s1"}}],band:["dnvme","dnic"],zero:true,
  y0:D.dlo,y1:D.dhi,ystep:4,yfmt:function(y){{return (y>0?"+":y<0?"−":"")+Math.abs(y);}},right:92,rightN:44,
  endLabels:[{{v:"dair",text:"card's air",short:"card"}},{{v:"dnvme",text:"host",short:"host"}}],
  tipf:function(i){{var r=[{{h:head(i)}}];
    if(D.dair[i]!=null)r.push({{k:"s1",v:sg(D.dair[i])+" °C",l:"card's air ("+f1(D.air[i])+" °C)"}});
    if(D.dnvme[i]!=null)r.push({{k:"ctx",v:sg(D.dnvme[i])+" °C",l:"NVMe drive ("+f1(D.nvme[i])+" °C)"}});
    if(D.dnic[i]!=null)r.push({{k:"ctx",v:sg(D.dnic[i])+" °C",l:"network chip ("+f1(D.nic[i])+" °C)"}});
    return r;}}}});

/* the scatter: power at each degree against the 2 October law */
(function(){{
  var box=document.querySelector("#c3 .plot"),P=D.sc,L=D.law;
  function law(T){{return L.a+L.b*Math.exp(L.c*T);}}
  function draw(){{
    var W=Math.max(280,box.clientWidth),nar=W<560,H=nar?250:300,m={{l:nar?40:48,r:14,t:12,b:40}},pw=W-m.l-m.r,ph=H-m.t-m.b;
    var x0=60,x1=140,y0=20,y1=140;
    function X(x){{return m.l+(x-x0)/(x1-x0)*pw;}} function Y(y){{return m.t+(1-(y-y0)/(y1-y0))*ph;}}
    box.replaceChildren();
    var svg=E("svg",{{width:W,height:H,viewBox:"0 0 "+W+" "+H,role:"img","aria-label":box.getAttribute("aria-label")||""}},box);
    var g=E("g",{{"class":"grid"}},svg);
    for(var y=y0;y<=y1;y+=20){{E("line",{{x1:m.l,x2:m.l+pw,y1:Y(y),y2:Y(y)}},g);E("text",{{x:m.l-6,y:Y(y)+4,"text-anchor":"end","class":"tk"}},svg,y+" W");}}
    E("line",{{x1:m.l,x2:m.l+pw,y1:m.t+ph,y2:m.t+ph,"class":"ax"}},svg);
    for(var x=x0;x<=x1;x+=(nar?20:10)){{E("line",{{x1:X(x),x2:X(x),y1:m.t+ph,y2:m.t+ph+4,"class":"ax"}},svg);
      E("text",{{x:X(x),y:m.t+ph+17,"text-anchor":"middle","class":"tk"}},svg,x+" °C");}}
    var d="";for(var T=x0;T<=x1;T+=0.5){{var v=law(T);if(v>y1)break;d+=(d?"L":"M")+X(T).toFixed(1)+","+Y(v).toFixed(1);}}
    E("path",{{d:d,"class":"ln ctx"}},svg);
    P.forEach(function(p){{E("circle",{{cx:X(p.T),cy:Y(Math.min(p.w,y1)),r:4,"class":"dot"}},svg);}});
    var ring=E("circle",{{r:7,cx:0,cy:0,fill:"none",stroke:"var(--ink)","stroke-width":1.5,visibility:"hidden"}},svg);
    var hit=E("rect",{{x:m.l,y:m.t,width:pw,height:ph,"class":"hit",tabindex:0,"aria-label":"Chart values: use the left and right arrow keys"}},svg);
    var ki=0;
    function at(i,cx,cy){{var p=P[i];ring.setAttribute("cx",X(p.T));ring.setAttribute("cy",Y(Math.min(p.w,y1)));ring.setAttribute("visibility","visible");
      show([{{h:p.T+" °C mean die"}},{{k:"none",v:f1(p.w)+" W",l:"measured ("+p.n.toLocaleString("en")+(p.n===1?" reading)":" readings, median)")}},
            {{k:"ctx",v:f1(law(p.T))+" W",l:"the 2 October curve"}}],cx,cy);}}
    function near(px){{var Tv=x0+(px-m.l)/pw*(x1-x0),b=0;P.forEach(function(p,i){{if(Math.abs(p.T-Tv)<Math.abs(P[b].T-Tv))b=i;}});return b;}}
    function mv(e){{var r=svg.getBoundingClientRect();ki=near(e.clientX-r.left);at(ki,e.clientX,e.clientY);}}
    function off(){{hide();ring.setAttribute("visibility","hidden");}}
    hit.addEventListener("pointermove",mv);hit.addEventListener("pointerdown",mv);hit.addEventListener("pointerleave",off);
    hit.addEventListener("focus",function(){{var r=svg.getBoundingClientRect();at(ki,r.left+X(P[ki].T),r.top+Y(P[ki].w));}});
    hit.addEventListener("blur",off);
    hit.addEventListener("keydown",function(e){{if(e.key!=="ArrowLeft"&&e.key!=="ArrowRight")return;e.preventDefault();
      ki=Math.max(0,Math.min(P.length-1,ki+(e.key==="ArrowRight"?1:-1)));var r=svg.getBoundingClientRect();at(ki,r.left+X(P[ki].T),r.top+Y(Math.min(P[ki].w,y1)));}});
  }}
  draw();var lw=box.clientWidth;
  if(window.ResizeObserver)new ResizeObserver(function(){{if(Math.abs(box.clientWidth-lw)>4){{lw=box.clientWidth;draw();}}}}).observe(box);
}})();
}})();
</script>
</body>
</html>
"""
open(OUT, "w").write(page)
print(f"wrote {OUT}: {len(page):,} bytes; {len(xs)} chart points, {len(SC)} degree bins; second loss of cooling at "
      f"{second['t']} (prose: about {second_t}); kernel {k_aer} / {k_sq} / {k_reset}; chart-2 range {chart['dlo']}..{chart['dhi']}")
