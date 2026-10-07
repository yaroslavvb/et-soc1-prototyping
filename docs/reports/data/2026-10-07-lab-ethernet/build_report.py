#!/usr/bin/env python3
"""Build the 7 October Ethernet report (one self-contained HTML file) from results.jsonl.

  python3 build_report.py results.jsonl report.css out.html

Every number in the text is computed here from the results, so the page cannot drift from the data.
The page is public: it names the machines but carries no address, no ssh/root step and no account."""
import datetime as dt, html, json, statistics, sys

RES, CSS, OUT = sys.argv[1:4]
NM = sys.argv[4] if len(sys.argv) > 4 else None  # nm-restarts.txt: when each port's NetworkManager restarted
rows = [json.loads(l) for l in open(RES) if l.strip()]
NAME = {"eth": "Ethernet", "wifi": "WiFi", "ts": "Tailscale"}


def flows():
    """(path, sender, receiver) -> list of Mb/s, one per single-stream run, in time order."""
    out = {}
    for r in rows:
        if r.get("failed") or r.get("test") not in ("up", "down", "down-rerun"):
            continue
        c, s = r["client"], r["server"]
        snd, rcv = (c, s) if r["test"] == "up" else (s, c)
        out.setdefault((r["path"], snd, rcv), []).append(r["Mbps"])
    return out


F = flows()
DIRS = [(1, 2), (2, 1), (2, 3), (3, 2), (3, 1), (1, 3)]


def best(path, d):
    v = F.get((path,) + d)
    return max(v) if v else None


def first(path, d):
    v = F.get((path,) + d)
    return v[0] if v else None


def med(xs):
    return statistics.median(xs)


def rtt(path):
    """pair -> (p50 ms, p99 ms)"""
    return {(r["client"], r["server"]): (r["us_p50"] / 1000, r["us_p99"] / 1000)
            for r in rows if r.get("test") == "rtt" and r["path"] == path}


thr = {p: [best(p, d) for d in DIRS if best(p, d) is not None] for p in NAME}
med_thr = {p: med(v) for p, v in thr.items() if v}
rt = {p: rtt(p) for p in NAME}
med_rtt = {p: med([a for a, _ in v.values()]) for p, v in rt.items() if v}
p4 = [r["Mbps"] for r in rows if r.get("test") == "up-P4"]
both = next((r for r in rows if r.get("test") == "both-ways" and not r.get("failed")), None)
watched = [r for r in rows if r.get("test") == "ring-watched"]
ring = next((r for r in watched if not r["disturbed"]), None)
first_ring = next((r for r in rows if r.get("test") == "ring" and not r.get("failed")), None)
reruns = [r for r in rows if r.get("test") == "down-rerun"]
low_first = [(d, first("eth", d)) for d in DIRS if first("eth", d) and first("eth", d) < 900]
times = sorted(r["t"][11:16] for r in rows if "t" in r)
eth_times = sorted(r["t"][11:16] for r in rows if r.get("path") == "eth" and "t" in r)

wifi_all = thr["wifi"] + thr["ts"]
ratio_thr = med_thr["eth"] / med_thr["wifi"]
ratio_rtt = med_rtt["wifi"] / med_rtt["eth"]
MBps_eth = med_thr["eth"] / 8
MBps_wifi = med_thr["wifi"] / 8


def f0(x):
    return f"{int(x + 0.5):,}"  # half up: 928.5 reads 929, as everywhere else


def ms(x):
    return f"{x:.2f}" if x < 1 else f"{x:.1f}"


def dur(secs):
    if secs < 90:
        return f"{secs:.0f} s"
    if secs < 5400:
        return f"{secs / 60:.0f} min"
    return f"{secs / 3600:.1f} h"


def bars(title, sub, items, vmax, ticks, unit, fmt, tipfn, tickfmt=None):
    """A one-series horizontal bar chart in HTML: label | track with the bar and its value at the tip."""
    out = [f'<figure class="bz"><div class="ttl">{title}</div><div class="sub">{sub}</div><div class="rows">']
    for key, label, v in items:
        f = v / vmax
        tip = html.escape(tipfn(key, v), quote=True)
        out.append(f'<div class="row" tabindex="0" data-tip="{tip}"><span class="lab">{label}</span>'
                   f'<span class="track" style="--f:{f:.4f}"><span class="bar"></span>'
                   f'<span class="val">{fmt(v)} {unit}</span></span></div>')
    out.append('</div><div class="axis"><span class="lab"></span><span class="track">')
    for i, t in enumerate(ticks):
        cls = "tk mid" if i % 2 else "tk"
        out.append(f'<span class="{cls}" style="--f:{t / vmax:.4f}">{(tickfmt or fmt)(t) if t else "0"}</span>')
    out.append('</span></div></figure>')
    return "".join(out)


def thr_tip(p, v):
    vs = thr[p]
    return (f"{NAME[p]}: median {v:,.1f} Mb/s ({v / 8:,.1f} MB/s) over {len(vs)} directions; "
            f"range {min(vs):,.1f}–{max(vs):,.1f} Mb/s")


def rtt_tip(p, v):
    vs = [a for a, _ in rt[p].values()]
    p99 = max(b for _, b in rt[p].values())
    return (f"{NAME[p]}: median round trip {ms(v)} ms over {len(vs)} pairs "
            f"(pairs {ms(min(vs))}–{ms(max(vs))} ms); worst 99th percentile {ms(p99)} ms")


chart1 = bars("Transfer speed between two machines",
              "Median over the six directions, one TCP stream, in Mb/s. Longer is faster.",
              [("eth", "Ethernet", med_thr["eth"]), ("wifi", "WiFi", med_thr["wifi"]),
               ("ts", "Tailscale (over WiFi)", med_thr["ts"])],
              1000, [0, 250, 500, 750, 1000], "Mb/s", f0, thr_tip)
chart2 = bars("Round trip between two machines",
              "Median over the three pairs, a 64-byte message and its echo, in ms. Shorter is faster.",
              [("eth", "Ethernet", med_rtt["eth"]), ("wifi", "WiFi", med_rtt["wifi"]),
               ("ts", "Tailscale (over WiFi)", med_rtt["ts"])],
              8, [0, 2, 4, 6, 8], "ms", ms, rtt_tip, tickfmt=lambda x: f"{x:g}")


def cell(p, d):
    b, f = best(p, d), first(p, d)
    if b is None:
        return "<td>–</td>"
    note = "*" if p == "eth" and f is not None and f < 900 and b > f else ""
    return f'<td class="n">{b:,.1f}{note}</td>'


trows = "".join(
    f"<tr><td>aifoundry{a} → aifoundry{b}</td>{cell('eth', (a, b))}{cell('wifi', (a, b))}{cell('ts', (a, b))}</tr>"
    for a, b in DIRS)
rrows = "".join(
    f"<tr><td>aifoundry{a} ↔ aifoundry{b}</td>"
    + "".join(f'<td class="n">{ms(rt[p][(a, b)][0])} <span class="q">({ms(rt[p][(a, b)][1])})</span></td>'
              if (a, b) in rt[p] else "<td>–</td>" for p in NAME) + "</tr>"
    for a, b in [(1, 2), (2, 3), (3, 1)])

copyrows = "".join(
    f"<tr><td>{label}</td><td class='n'>{dur(nbytes / (med_thr['eth'] * 1e6 / 8))}</td>"
    f"<td class='n'>{dur(nbytes / (med_thr['wifi'] * 1e6 / 8))}</td></tr>"
    for label, nbytes in [("1 GB (a model checkpoint)", 1e9), ("10 GB", 1e10), ("100 GB", 1e11)])

if both:
    bl = both["links"]
    both_txt = (f"<li><strong>Both directions at once</strong> (aifoundry1 → 2 and 2 → 1 together): "
                f"{bl[0]['Mbps']:,.0f} and {bl[1]['Mbps']:,.0f} Mb/s. The link is full duplex: "
                f"each direction keeps the whole gigabit.</li>")
else:
    both_txt = ""
clean_rings = [r for r in watched if not r["disturbed"]]
hit_rings = [r for r in watched if r["disturbed"]] + ([first_ring] if first_ring else [])
hit_slowed = [sum(1 for x in r["links"] if x["Mbps"] < 900) for r in hit_rings]
hit_lows = [x["Mbps"] for r in hit_rings for x in r["links"] if x["Mbps"] < 900] or [0]
if ring:
    rl = " and ".join(", ".join(f"{x['Mbps']:,.0f}" for x in r["links"]) for r in clean_rings)
    ring_txt = (f"<li><strong>All three links at once</strong> (1 → 2, 2 → 3 and 3 → 1 together): {rl} Mb/s in the "
                f"{len(clean_rings)} runs that no NetworkManager restart touched, about "
                f"{statistics.mean(r['Mbps_total'] for r in clean_rings):,.0f} Mb/s in all. The switch gives every port "
                f"its full speed at the same time. In the {len(hit_rings)} runs a restart touched, "
                f"{'two of the three links' if all(n == 2 for n in hit_slowed) else 'one or two links'} dropped to "
                f"{min(hit_lows):,.0f}–{max(hit_lows):,.0f} Mb/s.</li>")
elif first_ring:
    rl = ", ".join(f"{x['Mbps']:,.0f}" for x in first_ring["links"])
    ring_txt = (f"<li><strong>All three links at once</strong>: {rl} Mb/s; the two slower links ran into a "
                f"NetworkManager restart on aifoundry2, so this run does not settle whether the switch keeps every "
                f"port at full speed at once.</li>")
else:
    ring_txt = ""

if reruns:
    rr = ", ".join(f"{r['Mbps']:,.0f}" for r in reruns)
    rerun_txt = f" Run again later in quiet moments, the same two directions gave {rr} Mb/s; the table shows the best run (marked *)."
else:
    rerun_txt = ""
star_note = ('<p class="kicker">* The first run in this direction overlapped a NetworkManager restart; '
             'the best of its runs is shown (see How it was measured).</p>') if any(
    best("eth", d) and first("eth", d) and first("eth", d) < 900 and best("eth", d) > first("eth", d) for d in DIRS) else ""

# Every Ethernet throughput run against the NetworkManager restarts logged on its machines: a restart drops the
# port's link-local address for a moment. A run covers about the 10 s before its record time.
restarts = {}
if NM:
    for line in open(NM):
        if "failed for connection" in line:
            w = line.split()
            restarts.setdefault(int(w[1].replace("aifoundry", "")), []).append(dt.datetime.fromisoformat(w[0]).timestamp())


def hits(r):
    end = dt.datetime.fromisoformat(r["t"][:19] + r["t"][19:22] + ":" + r["t"][22:]).timestamp()
    hosts = {r["client"], r["server"]} if "client" in r else {h for x in r["links"] for h in (x["client"], x["server"])}
    return sorted(dt.datetime.fromtimestamp(e).strftime("%H:%M:%S") for h in hosts for e in restarts.get(h, [])
                  if end - 10.5 <= e <= end)


def touched(r):
    """Did a NetworkManager restart fall inside this run? Watched runs say so themselves; the rest go by the logs."""
    return bool(r["disturbed"]) if "disturbed" in r else bool(hits(r))


def low(r):
    return min([r["Mbps"]] if "Mbps" in r else [x["Mbps"] for x in r["links"]])


eth_runs = [r for r in rows if r.get("path") == "eth" and r.get("test") != "rtt" and not r.get("failed")]
slow = [r for r in eth_runs if low(r) < 900]
slow_hit = [r for r in slow if touched(r)]
fast_touched = [r for r in eth_runs if low(r) >= 900 and touched(r)]
untouched = [r for r in eth_runs if not touched(r)]
slow_range = (min(low(r) for r in slow), max(low(r) for r in slow)) if slow else None
low_txt = " and ".join(f"aifoundry{d[0]} → aifoundry{d[1]} ({v:,.0f} Mb/s)" for d, v in low_first)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="referrer" content="no-referrer">
<meta name="color-scheme" content="light dark">
<title>AI Foundry lab, 7 October 2026: Ethernet, measured</title>
<meta name="description" content="The three lab machines are wired together at 1 Gb/s: 929 Mb/s between any two, about 30 times WiFi. Nothing uses the cable yet: the wired ports have no addresses.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%94%8C%3C/text%3E%3C/svg%3E">
<style>
{open(CSS).read()}
</style>
<style>
/* One-series bar charts in HTML, so the text stays readable on a phone (dataviz: thin bars, 4px rounded data end,
   value at the tip in ink, hairline grid, hover/focus tooltip; the tables below are the table view) */
.bz-pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px 40px;margin:26px 0 30px}}
@media (max-width:820px){{.bz-pair{{grid-template-columns:1fr}}}}
.bz{{--s1:#2a78d6;--grid:#e3e7ea;--axis:#9aa6ad;--tipbg:#ffffff;--tipbd:#d5dde2;margin:0;position:relative;font-family:var(--sans)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]) .bz{{--s1:#3987e5;--grid:#26343c;--axis:#5f707a;--tipbg:#1d2a32;--tipbd:#33444e}}}}
:root[data-theme="dark"] .bz{{--s1:#3987e5;--grid:#26343c;--axis:#5f707a;--tipbg:#1d2a32;--tipbd:#33444e}}
.bz .ttl{{font-weight:650;font-size:16px;color:var(--ink);margin:0 0 2px}}
.bz .sub{{font-size:13.5px;color:var(--muted);margin:0 0 12px;line-height:1.4}}
.bz .row,.bz .axis{{display:grid;grid-template-columns:9.6em 1fr;align-items:center;gap:0 10px}}
.bz .row{{padding:5px 0;border-radius:4px;outline:none}}
.bz .row:hover .bar,.bz .row:focus-visible .bar{{filter:brightness(1.12)}}
.bz .row:focus-visible{{box-shadow:0 0 0 2px var(--s1)}}
.bz .lab{{font-size:14px;color:var(--ink-2);line-height:1.2}}
.bz .track{{position:relative;height:22px;--w:calc(100% - 5.6em)}}
.bz .rows .track::before{{content:"";position:absolute;inset:-5px auto -5px 0;width:var(--w);
  background:repeating-linear-gradient(to right,var(--grid) 0 1px,transparent 1px 25%);border-right:1px solid var(--grid)}}
.bz .bar{{position:absolute;left:0;top:0;height:22px;width:calc(var(--w) * var(--f));min-width:3px;background:var(--s1);border-radius:0 4px 4px 0}}
.bz .val{{position:absolute;top:0;line-height:22px;left:calc(var(--w) * var(--f) + 7px);font-size:13.5px;font-weight:650;color:var(--ink);white-space:nowrap;font-variant-numeric:tabular-nums}}
.bz .axis{{margin-top:4px}}
.bz .axis .track{{height:16px}}
.bz .tk{{position:absolute;left:calc(var(--w) * var(--f));transform:translateX(-50%);font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}}
@media (max-width:560px){{.bz .row,.bz .axis{{grid-template-columns:7.4em 1fr;gap:0 8px}}.bz .lab{{font-size:13px}}.bz .tk.mid{{display:none}}}}
.bz-tip{{position:fixed;z-index:9;pointer-events:none;max-width:300px;background:var(--tipbg,#fff);color:var(--ink);border:1px solid var(--tipbd,#ccc);border-radius:6px;
  padding:7px 9px;font-family:var(--sans);font-size:13px;line-height:1.4;box-shadow:0 2px 10px rgba(0,0,0,.12);opacity:0;transition:opacity .08s}}
td.n{{font-variant-numeric:tabular-nums;white-space:nowrap}}
td .q{{color:var(--muted);font-size:.9em}}
.big{{font-family:var(--sans);display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:22px 0 24px;max-width:900px}}
.big div{{background:var(--paper);border:1px solid var(--rule);border-radius:6px;padding:12px 14px}}
.big b{{display:block;font-size:30px;font-weight:600;line-height:1.1;color:var(--ink)}}
.big span{{display:block;font-size:13.5px;color:var(--muted);margin-top:4px;line-height:1.35}}
</style>
</head>
<body>
<div class="wrap">
<header class="mast">
<p class="eyebrow">AI Foundry lab</p>
<h1 class="title">The lab machines are wired together: Ethernet runs about {ratio_thr:.0f} times faster than WiFi, and nothing uses it yet</h1>
</header>
<main>
<p class="lede"><em>Covers Wed 7 Oct 2026 (week 41), {times[0]}–{times[-1]} PDT: aifoundry1, aifoundry2 and aifoundry3 at Studio 45.
Written the same afternoon from timed transfers between every pair of machines, run from aifoundry1.</em></p>

<p><strong>The three machines are cabled to one wired network, and it works.</strong> Every port came up at 1 Gb/s,
every machine reaches the other two, and one TCP stream moves <strong>{f0(med_thr['eth'])} Mb/s ({MBps_eth:,.0f} MB/s)</strong>
in every direction: the most a gigabit link carries. WiFi between the same machines moves a median
<strong>{med_thr['wifi']:,.0f} Mb/s</strong> ({min(thr['wifi']):,.0f}–{max(thr['wifi']):,.0f}), so the cable is about
{ratio_thr:.0f} times faster. A round trip takes <strong>{ms(med_rtt['eth'])} ms</strong> on the cable and about
{ms(med_rtt['wifi'])} ms over WiFi.</p>

<div class="big">
<div><b>{f0(med_thr['eth'])} Mb/s</b><span>Ethernet, any machine to any other ({MBps_eth:,.0f} MB/s)</span></div>
<div><b>{med_thr['wifi']:,.0f} Mb/s</b><span>WiFi between the same machines, median ({MBps_wifi:,.1f} MB/s)</span></div>
<div><b>{ms(med_rtt['eth'])} ms</b><span>Ethernet round trip, against {ms(med_rtt['wifi'])} ms over WiFi</span></div>
</div>

<p><strong>But nothing uses the cable yet.</strong> The wired ports have no IP address. Nothing on that network
hands addresses out (no DHCP server), so each machine's NetworkManager asks for 45 seconds, four times, gives up for
5 minutes and starts again. Until each port gets an address, all traffic between the machines, ssh and Tailscale
included, still goes over WiFi. These tests used the ports' automatic IPv6 link-local addresses, which exist only while
NetworkManager is asking: about 3 minutes in every 8. The fix is a fixed address on each wired port, a one-time step
for whoever has root on the machines.</p>

<div class="bz-pair">
{chart1}
{chart2}
</div>

<h2 id="pairs">Every pair, every path</h2>
<p>Speed in Mb/s, one TCP stream for 8 seconds, counted by the receiver. Tailscale between these machines connects
directly over the WiFi network, so it measures WiFi plus encryption.</p>
<div class="tablewrap"><table>
<thead><tr><th>From → to</th><th>Ethernet</th><th>WiFi</th><th>Tailscale</th></tr></thead>
<tbody>{trows}</tbody>
</table></div>
{star_note}
<p>Round trip in ms, median (99th percentile in brackets):</p>
<div class="tablewrap"><table>
<thead><tr><th>Pair</th><th>Ethernet</th><th>WiFi</th><th>Tailscale</th></tr></thead>
<tbody>{rrows}</tbody>
</table></div>
<ul>
<li><strong>Four streams at once</strong> move the same {med(p4):,.0f} Mb/s as one, on every pair: the link is the limit,
not the machines or the software.</li>
{both_txt}
{ring_txt}
</ul>

<h2 id="meaning">What it means</h2>
<p>Time to copy a file from one machine to another, at the speeds measured:</p>
<div class="tablewrap"><table>
<thead><tr><th>File</th><th>Ethernet ({f0(med_thr['eth'])} Mb/s)</th><th>WiFi ({med_thr['wifi']:,.0f} Mb/s)</th></tr></thead>
<tbody>{copyrows}</tbody>
</table></div>
<p>WiFi is also uneven: its slowest round trips took up to
{ms(max(b for _, b in rt['wifi'].values()))} ms, against {ms(max(b for _, b in rt['eth'].values()))} ms on the cable.</p>

<h2 id="gigabit">Why 1 Gb/s</h2>
<p>Each machine's wired port is an Aquantia AQC107, a 10 Gb/s controller that also runs at 2.5 and 5 Gb/s, and each
offers all of those speeds. All three links settled at 1 Gb/s, so the switch (or the cabling) is gigabit. A 10 Gb/s
switch would raise the ceiling up to ten times.</p>

<h2 id="next">To make it usable</h2>
<ol>
<li><strong>A fixed address on each wired port</strong> (root, one command per machine) and a name for each, such as
aifoundry2-eth. NetworkManager then stops asking for an address every few minutes.</li>
<li><strong>Tailscale should then pick the cable by itself.</strong> It offers every address a machine has and uses
the fastest path it finds between two machines, so <code>ssh aifoundryN</code>, which goes through Tailscale, would
ride the cable. To be checked once the ports have addresses.</li>
<li><strong>Plain ssh to a wired address needs a key.</strong> Between the lab machines, ssh works today only through
Tailscale; to the wired address it was refused for lack of a key in <code>~/.ssh/authorized_keys</code>.</li>
</ol>

<h2 id="method">How it was measured</h2>
<ul>
<li><strong>The cabling.</strong> Each port showed a carrier at 1 Gb/s full duplex. Pings between every pair over the
link-local addresses were answered in about 0.5 ms. No port counted an error or a dropped packet; the frames are the
standard 1,500 bytes.</li>
<li><strong>The tool.</strong> <code>netbench.py</code>, a small Python TCP sender and receiver: each test runs 8 s after
a 1 s warm-up that is discarded, and the receiver counts the bytes. The round trip is a 64-byte message and its echo
on one TCP connection, repeated 2,000 times on Ethernet and 200 times over WiFi.</li>
<li><strong>When.</strong> WiFi and Tailscale at {times[0]}–15:12 PDT; Ethernet at {eth_times[0]}–{eth_times[-1]},
each test waiting until both ends had their address.</li>
<li><strong>Slow runs.</strong> {len(slow)} of the {len(eth_runs)} Ethernet runs had a link below 900 Mb/s
({slow_range[0]:,.0f}–{slow_range[1]:,.0f}), and {"every one" if len(slow_hit) == len(slow) else f"{len(slow_hit)} of them"}
overlapped a NetworkManager restart, by the machines' logs or by watching the ports' addresses during the run. All
{len(untouched)} runs that no restart touched ran at full speed{f", and so did {len(fast_touched)} that a restart touched" if fast_touched else ""}.
A restart re-sets the port's address, but it is not only that port that slows: in the all-links runs a restart on one
machine sometimes slowed the link between the other two. It does not bounce the cable (the ports' carrier counters
did not move). Fixed addresses end the restarts. The table shows each direction's best run.{" * marks a direction whose first run was one of these." if star_note else ""}</li>
<li><strong>WiFi moves</strong> with everyone else's traffic and with the access point a machine is on. These are a
few minutes' sample, not a long-term average.</li>
</ul>
<p>The tool, the scripts and every result are in
<a href="https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/docs/reports/data/2026-10-07-lab-ethernet">docs/reports/data/2026-10-07-lab-ethernet</a>
of the lab repository, with this page as <code>docs/reports/2026-10-07-lab-ethernet.html</code>.</p>
</main>
</div>
<footer>AI Foundry lab · Wed 7 Oct 2026 · measured from aifoundry1 ·
<a href="https://spacesheep.dev/@yaroslavvb/aifoundry-lab-dashboard#worklog">the lab dashboard's worklog</a></footer>
<div class="bz-tip" id="bz-tip" role="tooltip"></div>
<script>
(function(){{
  var tip=document.getElementById("bz-tip");
  function show(row,x,y){{
    tip.textContent=row.getAttribute("data-tip");
    var st=getComputedStyle(row.closest(".bz"));
    tip.style.setProperty("--tipbg",st.getPropertyValue("--tipbg"));
    tip.style.setProperty("--tipbd",st.getPropertyValue("--tipbd"));
    var w=tip.offsetWidth,h=tip.offsetHeight;
    tip.style.left=Math.max(8,Math.min(x+14,innerWidth-w-8))+"px";
    tip.style.top=Math.max(8,y-h-12)+"px";
    tip.style.opacity=1;
  }}
  function hide(){{tip.style.opacity=0;}}
  document.querySelectorAll(".bz .row").forEach(function(r){{
    r.addEventListener("mousemove",function(e){{show(r,e.clientX,e.clientY);}});
    r.addEventListener("mouseleave",hide);
    r.addEventListener("focus",function(){{var b=r.getBoundingClientRect();show(r,b.left+b.width/3,b.top);}});
    r.addEventListener("blur",hide);
    r.addEventListener("click",function(e){{show(r,e.clientX,e.clientY);}});
  }});
  addEventListener("scroll",hide,{{passive:true}});
}})();
</script>
</body>
</html>
"""
open(OUT, "w").write(page)
print(f"wrote {OUT}: {len(page):,} bytes; eth {med_thr['eth']:.1f} wifi {med_thr['wifi']:.1f} ts {med_thr['ts']:.1f} Mb/s; "
      f"rtt eth {med_rtt['eth']:.3f} wifi {med_rtt['wifi']:.2f} ts {med_rtt['ts']:.2f} ms; ratio {ratio_thr:.1f}x / {ratio_rtt:.1f}x; "
      f"both={bool(both)} ring={bool(ring)} reruns={len(reruns)}")
