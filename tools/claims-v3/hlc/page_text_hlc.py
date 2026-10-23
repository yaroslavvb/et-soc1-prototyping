#!/usr/bin/env python3
"""E63 report page: the prose, every number from summary_hlc.py's and dips_hlc.py's output (none typed by hand).

    python3 tools/claims-v3/hlc/page_text_hlc.py --summary <session 1 summary.json> [--summary2 <session 2>]
        --figures <session 1 figures.json> --dips <dips.json> --fpa-scene <fpa_scene.json> --out <text.json>

The fragments go to build_page_hlc.py: title, description, byline, body (with {{fig:...}} slots) and captions.
"""
import argparse
import json

PREREG = "5740cdb7"
A1 = "d6704c60"
REPO = "https://github.com/yaroslavvb/et-soc1-prototyping"
RULES = (("1_top_seen", "1. The camera sees the top rung (p &lt; 0.001, warming that lags the power)"),
         ("2_top_holds_800", "2. The top rung holds 800 MHz (95% of its launches clean)"),
         ("3_null_flat", "3. The null is flat"),
         ("4_mid_scales_with_watts", "4. The middle rung scales with its watts"),
         ("5_top_repeats", "5. The top rung repeats"))


def n(x, d=0):
    return "–" if x is None else f"{x:,.{d}f}"


def verdict(d):
    v = (d or {}).get("verdict", "–")
    return f'<span class="verdict {"pass" if v == "PASS" else "fail"}">{v}</span>'


def along_null(S):
    d = S["decisions"].get("3_null_flat", {})
    return d.get("along_top_mk"), d.get("se_mk"), d.get("p")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--summary2", default=None)
    ap.add_argument("--figures", required=True)
    ap.add_argument("--dips", required=True)
    ap.add_argument("--fpa-scene", required=True, help="session 1's fpa_scene.json")
    ap.add_argument("--fpa-scene2", default=None, help="session 2's, with bridge_jump_c added")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S1 = json.load(open(a.summary))
    S2 = json.load(open(a.summary2)) if a.summary2 else None
    F = json.load(open(a.figures))
    DP = json.load(open(a.dips))
    FS = json.load(open(a.fpa_scene))
    FS2 = json.load(open(a.fpa_scene2)) if a.fpa_scene2 else {}
    h2 = S2["blocks"]["E63-TOP"]["hold"] if S2 else None
    h2txt = (f"{h2['launches_held']} of {h2['launches']} launches clean" if h2 else "")
    B = S1["blocks"]
    top, nul, mid, top2 = B["E63-TOP"], B["E63-NULL"], B["E63-MID"], B["E63-TOP2"]
    na, nse, np_ = along_null(S1)
    D1 = S1["decisions"]
    D2 = S2["decisions"] if S2 else {}
    t2 = S2["blocks"]["E63-TOP"] if S2 else None
    hold = top["hold"]
    dips = [d for s in DP.values() for d in s["dips"]]
    nd = sum(s["launches_with_dip"] for s in DP.values())
    nl = sum(s["launches"] for s in DP.values())
    onsets = [d["onset_s"] for d in dips]
    T = {}
    T["title"] = "Weighing flipped bits with heat: the camera half of the Hamming ladder"
    T["description"] = (f"E63, pre-registered: E60's top rung against its zero at 0.05 Hz on aifoundry2, filmed from the back "
                        f"of the board. {n(top['board_step_w'], 2)} W of flips moved it {n(top['roi_amp_mk'])} mK; a null "
                        f"of equal watts stayed flat.")
    T["byline"] = (f"AI Foundry lab · E63 (request Q122) · aifoundry2, Fri 23 Oct 2026, 12:55–14:00 PDT · pre-registered in "
                   f'<a href="{REPO}/commit/{PREREG}">{PREREG}</a> before the first launch')
    T["captions"] = {
        "watts": ("Every block's camera amplitude at 0.05 Hz over the die (the warm quarter of the frame), along its "
                  "session's top-rung phase, against the watts its two arms differ by (each lap's median board power in "
                  "the first arm's launch minus the second's). Bars: ±1 SE over laps. Dashed: the least-squares line through "
                  "zero."),
        "power": ("The board's power over the 20 s cycle, every analysed lap of session 1 averaged, its own mean taken off. "
                  "The rung runs in the shaded first half, the zero in the second; the sharp dips are the ~1 s idle tails "
                  "between launches, the same in both halves, so they sit at 0.1 Hz, not 0.05."),
        "roi": ("The back of the board over the same cycle, over the die (reduce_hm.py's bridged frames with a 20 s running "
                "mean taken off: a picture of the shape, while every number comes from the registered fit). The rung's "
                "half climbs, the zero's half falls; the idle tails add the same quick dip to both."),
        "laps": ("Each analysed lap of session 1 as a point: its amplitude at 0.05 Hz over the die, in phase with the "
                 "switching (right) and a quarter cycle later (up). The rungs' laps cluster away from zero, along one "
                 "direction (the heat lags the switch by about a quarter cycle); the null's sit around zero."),
    }
    st = F.get("map_stats", {})
    body = []
    body.append(f"""<p class="lede">E60 weighed a flipped bit with the board's power meter. This experiment weighs it with heat. The
thermal camera behind aifoundry2's card watched the back of the board while 256 of the chip's cores switched every
10 seconds between E60's top rung, with all 23 mantissa bits of one operand flipping on every cycle, and its zero, the
same arithmetic with nothing flipping. The flips put {n(top['board_step_w'], 2)} W on the board, and the back of the board
followed: {n(top['roi_amp_mk'])} ± {n(top['roi_se_mk'])} mK at 0.05 Hz over the die, {n(top['transfer_mk_per_w'])} mK per
watt of power at that frequency, the heat {n(top['lag_deg'])}° (about {n(top['lag_deg'] / 18.0)} s) behind the power. A middle rung moved it in proportion to
its watts, a null of equal watts in the same place stayed flat, and the whole run repeated on 192 cores.</p>""")
    body.append(f"""<div class="stats">
<div class="stat"><b>{n(top['roi_amp_mk'])} mK</b><span>the back of the board over the die at 0.05 Hz, top rung against its zero (SE {n(top['roi_se_mk'])})</span></div>
<div class="stat"><b>{n(top['board_step_w'], 2)} W</b><span>what the flips add on the board: {n(top['fj_per_flip'])} fJ per flipped bit at 800 MHz</span></div>
<div class="stat"><b>{n(top['camera_mk_per_w_step'])} mK/W</b><span>per watt switched; {n(top['transfer_mk_per_w'])} ± {n(top['transfer_se'])} per watt of power at 0.05 Hz</span></div>
<div class="stat"><b>{n(na)} ± {n(nse)} mK</b><span>the null, ones against pi: equal watts in the same place ({n(abs(nul['board_step_w']), 2)} W apart)</span></div>
</div>""")
    s2txt = ""
    if t2:
        t22 = S2["blocks"]["E63-TOP2"]
        s2txt = (f" Session 2, the same run on 192 cores, put {n(t2['board_step_w'], 2)} W on the board and read "
                 f"{n(t2['roi_amp_mk'])} ± {n(t2['roi_se_mk'])} mK, {n(t2['camera_mk_per_w_step'])} mK per watt switched against "
                 f"session 1's {n(top['camera_mk_per_w_step'])}. The camera's gain fell through the hour as the board and the "
                 f"camera warmed: {n(top['transfer_mk_per_w'])}, {n(top2['transfer_mk_per_w'])}, {n(t2['transfer_mk_per_w'])} "
                 f"and {n(t22['transfer_mk_per_w'])} mK per watt for the four top-rung blocks in order, the lag growing from "
                 f"{n(top['lag_deg'])}° to {n(t22['lag_deg'])}°. Each session's middle rung is read against its own top "
                 f"rungs, before and after it.")
    d4 = D1.get("4_mid_scales_with_watts", {})
    body.append("<h2>The camera reads the watts the flips draw</h2>")
    body.append("{{fig:watts}}")
    body.append(f"""<p>The middle rung, eight flipping bits instead of 23, added {n(mid['board_step_w'], 2)} W and moved the camera
{n(mid['roi_amp_mk'])} ± {n(mid['roi_se_mk'])} mK: {n(d4.get('camera_ratio'), 2)} of the top rung's amplitude where its power was
{n(d4.get('power_ratio'), 2)} of the top rung's. The top rung run again at the end of the session read
{n(top2['roi_amp_mk'])} ± {n(top2['roi_se_mk'])} mK.{s2txt}</p>""")
    body.append("<h2>One cycle, averaged</h2>")
    body.append("{{fig:power}}")
    body.append("{{fig:roi}}")
    body.append(f"""<h2>Where it shows</h2>
<p>Each block's amplitude at 0.05 Hz, pixel by pixel, along the top rung's phase, all on one scale. The outline is the warm
quarter of the frame under all 32 shires in E62, the region the numbers are read from. The top rung's map reads
{n(st.get('E63-TOP', {}).get('roi_mean_mk'))} mK there and {n(st.get('E63-TOP', {}).get('frame_mean_mk'))} mK over the whole
frame: the board spreads the heat wider than the camera's view.</p>
<div class="maps">
<figure data-ss-id="map-top"><img src="img/map-top.png" alt="Top rung: the board warms over the die"><figcaption>Top rung, lq_h23 against lq_h0</figcaption></figure>
<figure data-ss-id="map-mid"><img src="img/map-mid.png" alt="Middle rung: the same place, a quarter as warm"><figcaption>Middle rung, lq_h8 against lq_h0</figcaption></figure>
<figure data-ss-id="map-null"><img src="img/map-null.png" alt="Null: nothing"><figcaption>Null, ones against pi</figcaption></figure>
</div>
<img class="key" src="img/map-key.png" alt="Colour key: blue below zero, red above, in millikelvin">""")
    body.append("<h2>Lap by lap</h2>")
    body.append("{{fig:laps}}")
    pb = top.get("plain_bridged") or {}
    sp = top["spatial"]
    bridge_txt = ""
    if S2:
        m2 = S2["blocks"]["E63-MID"]
        pm2 = m2.get("plain_bridged") or {}
        bridge_txt = (f" And bridging can fail outright: in session 2 one step was bridged about {n(FS2['bridge_jump_c'])} K "
                      f"wrong in the middle of the middle rung's block, and the plain lock-in reads {n(pm2.get('amp'))} ± "
                      f"{n(pm2.get('se_along'))} mK there, where the registered fit, which never bridges, reads "
                      f"{n(m2['roi_amp_mk'])} ± {n(m2['roi_se_mk'])}.")
    body.append(f"""<h2>Board, not camera</h2>
<p>Three checks say the signal is heat on the board and not the camera. The map carries the capacitor field's pattern: the
shiny terminations under-report, as they did when E62 warmed the whole die (the fine detail of the two maps correlates
{n(sp['r_bloom_highpass'], 2)}), and a camera artefact would not know where the capacitors are. The focal plane's own
thermistor shows nothing at 0.05 Hz (p {n((top.get('fpa') or {}).get('vtemp', {}).get('p_signflip'), 2)}) and does not follow
the board (correlation {n(FS['r_vtemp_frame_detrended'], 2)}). The header field the decoder calls the focal-plane temperature
turned out to be the scene's mean: it ran about {n(FS['offset_c'])} °C above the board's frame mean all session and followed it
(correlation {n(FS['r_fpa_frame_detrended'], 2)}), so it saw the signal too,
{n((top.get('fpa') or {}).get('fpa_c', {}).get('amp'), 2)} K for the top rung. And the null, the same cores switching between
operands of equal watts, reads {n(na)} ± {n(nse)} mK.</p>""")
    body.append(f"""<h2>The shutter, planned around</h2>
<p>The camera's automatic shutter fired {n(top['ffc_per_min'], 1)} times a minute during the top rung, and every time it reset
the offset of every pixel (it fired about seven times a minute with the card idle, too). So the registered fit never
bridges a step: it gives each stretch between two shutter events its own free offset and reads the 0.05 Hz signal only from
the variation inside the stretches, with a slow spline for the camera's drift. The events fell at no preferred phase of the
cycle (Rayleigh p {n(top['ffc']['p_rayleigh'], 3)}). Read plainly off the bridged frames, the top rung gives the same
{n(pb.get('amp'))} mK with twice the error, ± {n(pb.get('se_along'))}.{bridge_txt}</p>""")
    rows = []
    for key, label in RULES:
        rows.append(f"<tr><td>{label}</td><td>{verdict(D1.get(key))}</td><td>{verdict(D2.get(key)) if S2 else '–'}</td></tr>")
    body.append(f"""<h2>The registered tests</h2>
<div class="tablewrap"><table><thead><tr><th>Decision rule, frozen before the run</th><th>Session 1, 256 cores</th><th>Session 2, 192 cores</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>""")
    body.append(f"""<h2>800 MHz, and a one-second dip</h2>
<p>The top rung on 256 cores held the die at {n(hold['die_mean_c'], 1)} °C, at most {n(hold['die_max_c'], 1)}, well under the
governor's 65 °C step, and {n(100 * hold['samples_800_share'], 1)}% of its samples after each launch's ramp read 800 MHz. But in
{nd} of {nl} launches over both sessions the clock fell to 600 MHz for about a second, anywhere from
{n(min(onsets), 1)} to {n(max(onsets), 1)} s into a launch, at every load, the null's included. That broke rule 2's 95% bar in
session 1 ({hold['launches_held']} of {hold['launches']} launches clean), and amendment
<a href="{REPO}/commit/{A1}">A1</a> repeated the run on 192 cores as the rule said to; there the top rung held
({h2txt}). Every dip has the same shape, the clock straight to its boot point and back up through 700 MHz, like the
governor's reset for an idle card and its climb at the start of a launch; it is not heat and not the power limit, and the
heater's own launches ran on through it. The camera numbers include it, and so does the measured power they are divided
by.</p>""")
    body.append(f"""<h2>How it ran</h2>
<p>aifoundry2 as it is, the camera's settings untouched, so the public live view kept its look. E60's own operand files,
checked byte for byte on the card first; the Horace kernel on 8 cores in each of the 32 shires, since the full card would
heat past the governor's step within minutes of switching. One 8.5 s launch per 10 s phase, so every on-window was under
9.5 s and the arms switched on a fixed 20 s grid. Four blocks per session: the top rung (7 min analysed after 3 min of warm-up),
the null (6 min), the middle rung (6 min) and the top rung again (5 min). Code, pre-registration and amendments:
<a href="{REPO}/tree/main/tools/claims-v3/hlc">tools/claims-v3/hlc</a>; data:
<a href="{REPO}/tree/main/docs/reports/data/2026-10-23-e63-camera-hamming-ladder">docs/reports/data/2026-10-23-e63-camera-hamming-ladder</a>.
Before it: <a href="https://spacesheep.dev/@yaroslavvb/et-soc1-bitflip-ladder">what one flipped bit costs</a> (E60) and
<a href="https://spacesheep.dev/@yaroslavvb/et-soc1-heat-movies">heat follows the work</a> (E62).</p>""")
    T["body"] = "\n".join(body)
    with open(a.out, "w") as f:
        json.dump(T, f, indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
