#!/usr/bin/env python3
"""E97, POST HOC and descriptive only (not registered; it changes nothing and scores nothing). Run from the data directory:

    python3 posthoc_e97.py > posthoc.txt

Reads e97.json, the raw pass aifoundry3/e97/p9720 and the three boxes' live-history excerpts in room/. Section tags in brackets are what the README cites.
"""
import gzip
import json
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
G, H_, C5 = 57400, 249400, 4096
os.environ["TZ"] = "America/Los_Angeles"
time.tzset()


def c2t(n):
    return (G + H_ * np.asarray(n, float) / C5 - H_ / 2) / 1000.0


def clock(t):
    return time.strftime("%H:%M:%S", time.localtime(t))


e = json.load(open(os.path.join(HERE, "e97.json")))
hs = e["holds"]["holds"]
D = os.path.join(HERE, "aifoundry3/e97/p9720")
tel = [json.loads(x) for x in gzip.open(os.path.join(D, "telemetry.jsonl.gz"), "rt") if x.startswith("{")]
marks = [json.loads(x) for x in open(os.path.join(D, "marks.jsonl"))]
runs = [json.loads(x) for x in open(os.path.join(D, "runs.jsonl"))]
t = np.array([r["t_ms"] / 1000 for r in tel])
S = np.array([c2t(r["pvt"]["c"]) for r in tel])
T = S.mean(axis=1)
P = np.array([r["board_w"] for r in tel], float)
M = np.array([r["sp"]["minion_w"][0] for r in tel], float)
Ti = np.array([r["temp_c"]["minshire"][0] for r in tel], float)
hold = {m["name"]: m for m in marks if m["kind"] == "hold"}
rest = {m["name"]: m for m in marks if m["kind"] == "rest"}
law = np.array(e["holds"]["idle_law_pooled"]["poly"])


def wm(y, a, b):
    q = (t >= a) & (t < b)
    return float(np.nanmean(y[q])), int(q.sum())


print("[timeline] Part B, PST")
for m in marks:
    if m["kind"] in ("rest", "hold"):
        print(f"  {m['kind']} {m['name']}: {clock(m['t_start_ms'] / 1000)}-{clock(m['t_end_ms'] / 1000)}, {(m['t_end_ms'] - m['t_start_ms']) / 1000:.0f} s, ended on {m['why_end']}")
    if m["kind"] == "stop":
        print(f"  stop in {m['hold']}: {clock(m['t_ms'] / 1000)}, firmware reading {m['die_c']} C, board {m['board_w']} W")
    if m["kind"] == "decision":
        print(f"  decision at {clock(m['t_ms'] / 1000)}: {m['choice']}; {m['left_s'] / 60:.1f} min left")
print()

print("[wander] each hold in 60 s bins: the 34-sensor mean minus the idle baseline (C), board power over it (W)")
for name, x in hs.items():
    h = hold[name]
    a, b = h["t_start_ms"] / 1000, h["t_end_ms"] / 1000
    Tb, Ta = x["idle"]["before"]["T"], x["idle"]["after_used"]["T"]
    Pb, Pa = x["idle"]["before"]["P"], x["idle"]["after_used"]["P"]
    tb = rest[x["idle"]["before"]["rest"]]["t_end_ms"] / 1000
    ta = rest[x["idle"]["after"]["rest"]]["t_end_ms"] / 1000 - 60
    row = []
    for s in np.arange(a, b, 60):
        q = (t >= s) & (t < s + 60)
        bt = Tb + (Ta - Tb) * (s + 30 - tb) / (ta - tb)
        bp = Pb + (Pa - Pb) * (s + 30 - tb) / (ta - tb)
        row.append(f"{T[q].mean() - bt:.2f}/{P[q].mean() - bp:.1f}")
    print(f"  {name} {x['item']}: " + " ".join(row))
print()

print("[windows] the steady rise on other windows of the same hold (the registered one is the hold's last 300 s)")
for name, wins in (("H1", ((600, 900), (660, 930), (900, 960), (1080, 1200), (1500, 1800))), ("H2", ((240, 480), (600, 900))), ("H3", ((900, 1200), (1200, 1500), (1500, 1800)))):
    x = hs[name]
    h = hold[name]
    a = h["t_start_ms"] / 1000
    Tb, Ta = x["idle"]["before"]["T"], x["idle"]["after_used"]["T"]
    Pb, Pa = x["idle"]["before"]["P"], x["idle"]["after_used"]["P"]
    Mb = x["idle"]["before"]["Pm"]
    tb = rest[x["idle"]["before"]["rest"]]["t_end_ms"] / 1000
    ta = rest[x["idle"]["after"]["rest"]]["t_end_ms"] / 1000 - 60
    for w0, w1 in wins:
        mid = a + (w0 + w1) / 2
        bt = Tb + (Ta - Tb) * (mid - tb) / (ta - tb)
        bp = Pb + (Pa - Pb) * (mid - tb) / (ta - tb)
        dt, _ = wm(T, a + w0, a + w1)
        dp, _ = wm(P, a + w0, a + w1)
        dm, _ = wm(M, a + w0, a + w1)
        print(f"  {name} {w0:5.0f}-{w1:5.0f} s: dT {dt - bt:6.2f} C, dP {dp - bp:6.2f} W, rise per board W {(dt - bt) / (dp - bp):.3f}, per minion-rail W {(dt - bt) / (dm - Mb):.3f}")
print()

print("[bump] H1's bump: the 34 sensors between 660-930 s and 1080-1200 s of the hold; every launch the same tile")
a = hold["H1"]["t_start_ms"] / 1000
qb = (t >= a + 660) & (t < a + 930)
qp = (t >= a + 1080) & (t < a + 1200)
qi = (t >= a - 120) & (t < a)
dS = S[qp].mean(axis=0) - S[qb].mean(axis=0)
rise = S[qb].mean(axis=0) - S[qi].mean(axis=0)
print(f"  the bump per sensor: mean {dS.mean():.3f} C, sd {dS.std(ddof=1):.3f}, min {dS.min():.3f}, max {dS.max():.3f}; the rise per sensor at the plateau: mean {rise.mean():.2f}, sd {rise.std(ddof=1):.2f}, min {rise.min():.2f}, max {rise.max():.2f}")
print(f"  board {wm(P, a + 660, a + 930)[0]:.3f} -> {wm(P, a + 1080, a + 1200)[0]:.3f} W, minion rail {wm(M, a + 660, a + 930)[0]:.3f} -> {wm(M, a + 1080, a + 1200)[0]:.3f} W; "
      f"the idle law's slope there is {np.polyval(np.polyder(law), 62.8):.3f} W/C, so leakage alone would add {np.polyval(np.polyder(law), 62.8) * dS.mean():.3f} W")
print()

print("[room] the boxes' live history (room/, 5 s records), in 1 min means across H1's last 17 minutes and H2; time is minutes after H1 started. cpu% is the host's whole-machine CPU use; its temperature sensors are the host's")
rooms = {}
for h in ("aifoundry1", "aifoundry2", "aifoundry3"):
    rooms[h] = [json.loads(x) for x in gzip.open(os.path.join(HERE, "room", h + ".jsonl.gz"), "rt")]
for h, rows in rooms.items():
    tt = np.array([r["t"] / 1000 for r in rows])
    print(f"  {h}")
    for m_ in range(13, 46):
        q = (tt >= a + m_ * 60) & (tt < a + (m_ + 1) * 60)
        rr = [r for r, k in zip(rows, q) if k]
        if not rr:
            continue
        dies = [c.get("die") for c in rr[-1]["cards"]]
        print(f"    min {m_:2d} {clock(a + m_ * 60)[:5]}: cpu {np.mean([r.get('cpu', np.nan) for r in rr]):5.1f}%, CPU sensor {np.mean([r['temps'].get('cpu', np.nan) for r in rr]):5.1f} C, NVMe {np.mean([r['temps'].get('nvme', np.nan) for r in rr]):5.1f} C, NIC {np.mean([r['temps'].get('nic', np.nan) for r in rr]):6.2f} C, idle card readings {dies}")
print()
print("[bursts] host-CPU bursts on any box during E97's whole session: minutes with whole-machine CPU use of at least 10%")
for h, rows in rooms.items():
    tt = np.array([r["t"] / 1000 for r in rows])
    cpu = np.array([r.get("cpu", 0.0) for r in rows], float)
    bins = np.floor(tt / 60.0).astype(int)
    hot = [int(i) for i in np.unique(bins) if cpu[bins == i].mean() >= 10.0]
    spans = []
    for i in hot:
        if spans and i == spans[-1][1] + 1:
            spans[-1][1] = i
        else:
            spans.append([i, i])
    print(f"  {h}: " + (", ".join(f"{clock(s * 60)[:5]}-{clock((f + 1) * 60)[:5]}" for s, f in spans) or "none"))
print()

print("[stop] H3's natural phase")
a3 = hold["H3"]["t_start_ms"] / 1000
stop3 = [m for m in marks if m["kind"] == "stop" and m["hold"] == "H3"][0]["t_ms"] / 1000
red3 = [m for m in marks if m["kind"] == "phase" and m["hold"] == "H3" and m["phase"] == "reduced"][0]["t_ms"] / 1000
q = (t >= a3) & (t < stop3 + 20)
first78 = t[q][np.argmax(Ti[q] >= 78)]
nat = [m for m in marks if m["kind"] == "launch" and m["block"] == "H3" and m["half"] == "natural"]
red = [m for m in marks if m["kind"] == "launch" and m["block"] == "H3" and m["half"] == "reduced"]
qn = (t >= first78 - 1) & (t < first78 + 1)
print(f"  the firmware's reading first read 78 C {first78 - a3:.1f} s after the hold started; the runner saw it between launches at {stop3 - a3:.1f} s; the next launch started at {red3 - a3:.1f} s, in the reduced phase (the reading was back at 75 C by then: the fast stages fall within a launch's gap)")
print(f"  {len(nat)} natural launches, {len(red)} reduced; at the first 78 C reading the 34-sensor mean read {T[qn].mean():.2f} C and the board {P[qn].mean():.1f} W; rate over the last 30 s before it {np.polyfit(t[(t >= first78 - 30) & (t < first78)] - first78, T[(t >= first78 - 30) & (t < first78)], 1)[0] * 60:.2f} C/min")
print()

print("[gaps] H3's reduced phase has idle gaps of about 3 s between launches: board power in the gaps' last 1.5 s against the idle law at the same moment's die (the law is carried up from the rests, whose top bin is 64.8 C)")
ph = [m for m in marks if m["kind"] == "phase" and m["hold"] == "H3" and m["phase"] == "reduced"][0]["t_ms"] / 1000
ls = sorted([m for m in marks if m["kind"] == "launch" and m["block"] == "H3" and m["t_start_ms"] / 1000 >= ph + 300], key=lambda m: m["t_start_ms"])
pg, tg, lawg = [], [], []
for u, v in zip(ls, ls[1:]):
    g0, g1 = v["t_start_ms"] / 1000 - 1.5, v["t_start_ms"] / 1000
    if g0 < u["t_end_ms"] / 1000 + 0.5:
        continue
    q = (t >= g0) & (t < g1)
    if q.sum() >= 5:
        pg.append(P[q].mean())
        tg.append(T[q].mean())
print(f"  {len(pg)} gaps from 5 minutes into the reduced phase: board {np.mean(pg):.2f} W at a die of {np.mean(tg):.2f} C; the idle law gives {np.polyval(law, np.mean(tg)):.2f} W there, so the law is {np.polyval(law, np.mean(tg)) - np.mean(pg):+.2f} W against the gaps. "
      f"The rails' own running average (1 s) still carries part of the last launch, and the fast stages are falling, so this is a rough check")
print()

print("[common times] the rise per W of E78's S at the same seconds after a hold starts, H1 (compute share %.3f) against H3's natural phase (share 0.97)" % hs["H1"]["steady"]["compute_share"])
s1 = hs["H1"]["steady"]["S_E78_W"] * hs["H1"]["steady"]["compute_share"]
s3 = hs["H3"]["steady"]["S_E78_W"] * 0.9653
for k in ("2", "10", "30", "60", "120", "180"):
    c1, c3 = hs["H1"]["curve"][k], hs["H3"]["curve"][k]
    print(f"  {k:>4s} s: H1 {c1['dT']:6.2f} C, {c1['dT'] / s1:.3f} C/W, {c1['dT'] / c1['dP']:.3f} per board W | H3 {c3['dT']:6.2f} C, {c3['dT'] / s3:.3f} C/W, {c3['dT'] / c3['dP']:.3f} per board W | ratio per S {c3['dT'] / s3 / (c1['dT'] / s1):.3f}")
print()

print("[peaks] the hottest sensor and the highest readings")
for name in hs:
    h = hold[name]
    q = (t >= h["t_start_ms"] / 1000) & (t < h["t_end_ms"] / 1000)
    print(f"  {name}: mean up to {T[q].max():.2f} C, hottest sensor {S[q].max():.2f} C, firmware reading up to {Ti[q].max():.0f} C, board up to {P[q].max():.2f} W, minion rail up to {M[q].max():.1f} W")
print(f"  the sensors' high latch: {e['holds']['hi_max_code']} codes, {e['holds']['hi_max_C']:.1f} C, as in E89; a latch never moved backwards ({e['holds']['hi_drops']} drops); fault samples {e['holds']['fault_samples']}")
print()

print("[pattern] per-sensor rise per board W at each hold's end, against each other and E89's reference pattern")
E89 = json.load(open(os.path.join(HERE, "../2026-10-31-e89-heat-low-power/e89.json")))["blocks"]["f32randn"]["H_sensor_proj"]
v = {n: np.array(hs[n]["per_sensor_R_ol"]["values"]) for n in hs}
for a_, b_ in (("H1", "H2"), ("H1", "H3"), ("H2", "H3")):
    print(f"  {a_} vs {b_}: correlation {np.corrcoef(v[a_], v[b_])[0, 1]:.4f}")
for n in hs:
    print(f"  {n} vs E89's fp32 random at 1/60 Hz: correlation {np.corrcoef(v[n], np.array(E89, float))[0, 1]:.4f}; coolest sensor {int(np.argmin(v[n]))}, warmest {int(np.argmax(v[n]))}, {v[n].min():.3f}-{v[n].max():.3f} C/W")
print()

print("[rests] how long a rest takes: seconds from the last launch to within 2, 1, 0.5, 0.2, 0.1 C of its final idle, and the board to within 0.5, 0.2, 0.1, 0.05 W of its final idle")
for r in e["holds"]["rests"]:
    print(f"  {r['name']}: first 30 s mean {r['T_first_30s']:.2f} C; {r['within_final_s']}; board {r['P_within_final_s']}; idle {r['idle_c']:.3f} C ({r['final_minus_starting_idle_C']:+.3f} from the starting idle), {r['P_final_W']:.3f} W")
print()

print("[part A] the 28 blocks, by frame")
B = e["blocks"]
for frame, names in (("against idle", [b for b in B if B[b]["ref"] == "idle"]), ("against own zeros", [b for b in B if B[b]["ref"] != "idle" and b != "f32randn"])):
    rb = [B[b]["r_board_lap"]["r"] for b in names]
    rm = [B[b]["r_minion_lap"]["r"] for b in names]
    sh = [B[b]["minion_share"] for b in names]
    pw = [B[b]["step2_per_W"] for b in names]
    print(f"  {frame} ({len(names)}): r per board W {min(rb):.3f}-{max(rb):.3f}, mean {np.mean(rb):.3f}; r per minion-rail W {min(rm):.3f}-{max(rm):.3f}, mean {np.mean(rm):.3f}; minion share of the board swing {min(sh):.3f}-{max(sh):.3f}; 2 s rise per W {min(pw):.4f}-{max(pw):.4f}")
print(f"  the reference: H by pass {B['f32randn']['H_by_pass']}, minion share {B['f32randn']['minion_share']:.3f}; 2 s rise {B['f32randn']['step2']['mean']:.3f} C, {B['f32randn']['step2_per_W']:.4f} C/W of D")
vs = {}
ts = {}
for x in e["verdicts"]:
    if x["unit"] == "pass" and x["rule"] in ("E97-R2", "E97-R4", "E97-R5"):
        vs.setdefault(x["rule"], {}).setdefault(x["verdict"], []).append(x["cell"])
        if x.get("trend_sensitive"):
            ts.setdefault(x["rule"], []).append((x["cell"], x["verdict"], x["trend_sensitive"]))
for k, d in vs.items():
    print(f"  {k}, the pass as the unit: " + "; ".join(f"{a_} {len(b_)}" for a_, b_ in d.items()))
print(f"  verdicts that move under a linear or cubic trend: " + "; ".join(f"{k}: {len(v_)}" for k, v_ in ts.items()))
for x in e["verdicts"]:
    if x["unit"] == "pass" and x["rule"] == "E97-R2" and x["verdict"] == "PASS":
        print(f"    R2 PASS at the pass unit: {x['cell']} {x['measured']['r']:.3f} [{x['measured']['lo']:.3f}, {x['measured']['hi']:.3f}]")
print("  with H_ref taken as a fixed number (its pass-to-pass spread out), r per board W at the pass unit:")
hr = np.mean(B["f32randn"]["H_by_pass"])
widest = 0
for b in [b for b in B if b != "f32randn"]:
    hb = np.array(B[b]["H_by_pass"]) / hr
    hw = 12.706 * hb.std(ddof=1) / math.sqrt(2)
    widest = max(widest, hw)
print(f"    the widest half-width {widest:.3f}")
print()

print("[cycle] the 2 s step: cycle 1 over cycle 0, by baseline (E89 C6), against zeros")
fl = [b for b in B if B[b]["ref"] != "idle" and B[b]["item"].split(".")[0] != "int8"]
i8 = [b for b in B if B[b]["ref"] != "idle" and B[b]["item"].split(".")[0] == "int8"]
idl = [b for b in B if B[b]["ref"] == "idle"]
for nm, group in (("float against zeros", fl), ("int8 against zeros", i8), ("against idle", idl)):
    for key, lab in (("step2", "E89's line"), ("step2_gapfree_baseline", "[-8, -2) s line"), ("step2_quadratic_baseline", "quadratic")):
        q = [B[b][key]["cycle1"] / B[b][key]["cycle0"] for b in group]
        print(f"  {nm}, {lab}: c1/c0 {min(q):.3f}-{max(q):.3f}, mean {np.mean(q):.3f}")
    q = [B[b]["step2_quadratic_baseline"]["mean"] / B[b]["step2"]["mean"] for b in group]
    print(f"  {nm}: the quadratic's mean rise over E89's line's: {min(q):.3f}-{max(q):.3f}, mean {np.mean(q):.3f}")
print()
print("[tie] fp32 random over idle, derived: its rise over fp32 zeros %.3f + fp32 zeros over idle %.3f = %.3f C; E78 measured 3.16 +- 0.08 C" % (B["f32randn"]["step2"]["mean"], B["f32zero"]["step2"]["mean"], B["f32randn"]["step2"]["mean"] + B["f32zero"]["step2"]["mean"]))
