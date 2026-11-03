#!/usr/bin/env python3
"""E143 (Q138): the README's tables, printed from results.json and the frozen predictions (presentation only: no number is computed here that the
registered reducer did not write, except differences and the band each tile's value is read against).

    python3 docs/reports/data/2026-11-02-e143-blind5-aifoundry2/tables_e143.py > docs/reports/data/2026-11-02-e143-blind5-aifoundry2/tables.md
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e143", "predictions-e143.json")))
sc = R["score"]
ru = sc["rules"]


def f(x, n=1):
    return "-" if x is None else f"{x:.{n}f}"


# Corrected Mon 2 Nov 2026, after verification: results.json stores each rule's ref_rms rounded to three places (W1 1.945, H1 0.685), and
# printing those to two places rounded twice (1.95, 0.69). The verdicts table now prints the frozen reference's own values
# (predictions-e143.json reference: W1 1.9447 -> 1.94, H1 0.6845 -> 0.68); F1, F2 and W2 print as before. No number or verdict changes.
REF_RMS = {"E143-F1": P["reference"]["governed"]["rms_mhz"], "E143-F2": P["reference"]["pinned"]["rms_mhz"],
           "E143-W1": P["reference"]["governed"]["rms_w"], "E143-W2": P["reference"]["pinned"]["rms_w"], "E143-H1": P["reference"]["heat"]["rms_c"]}


print("## Verdicts\n")
print("| rule | set | n | measured | reference line (2.5% – 97.5%) or coverage line | verdict |")
print("|---|---|---:|---|---|---|")
lab = {"E143-F1": ("burst clock, governed", "MHz"), "E143-F2": ("burst clock, pinned", "MHz"), "E143-F3": ("burst clock, all: inside ±21.3 MHz", ""),
       "E143-W1": ("board W, governed", "W"), "E143-W2": ("board W, pinned", "W"), "E143-W3": ("board W, all: inside ±3.37 W", ""),
       "E143-H1": ("die rise, all", "°C"), "E143-H3": ("die rise, all: inside ±1.41 °C", "")}
for k, (s, u) in lab.items():
    v = ru[k]
    if "rms" in v:
        print(f"| **{k}** | {s} | {v['n']} | rms {f(v['rms'], 2)} {u} (mean error {f(v['mean_err'], 2)}) | {f(v['range_2.5_97.5'][0], 2)} – {f(v['range_2.5_97.5'][1], 2)} {u} (reference rms {f(REF_RMS.get(k, v['ref_rms']), 2)}) | **{v['verdict']}** |")
    else:
        print(f"| **{k}** | {s} | {v['n']} | {v['inside']} of {v['n']} inside | at least {v['line']} | **{v['verdict']}** |")
rp = R["replicate"]
print(f"| **E143-R0** | E80's replicate tiles | 3 | " + "; ".join(f"{k[2:]} {f(t.get('burst_mhz'), 1)} MHz ({t.get('d_mhz'):+.1f}), {f(t.get('burst_w'), 2)} W ({t.get('d_w'):+.2f})"
                                                       for k, t in rp["tiles"].items() if t.get("n")) + f" | within 25 MHz and 3.37 W of E80's and E83's cells | **{rp['verdict']}** |")

print("\n## Before and after (rms, measured − predicted)\n")
print("| set | n | clock: reference (before) → E143 blind (after) | board W: before → after | die rise: before → after |")
print("|---|---:|---|---|---|")
ref = P["reference"]
bs = sc["reported"]["by_set"]
rows = [("governed (M7 < 795 MHz)", "governed", ref["governed"]["rms_mhz"], ref["governed"]["rms_w"]),
        ("pinned (M7 795–800 MHz)", "pinned", ref["pinned"]["rms_mhz"], ref["pinned"]["rms_w"]),
        ("all 36", "all", 8.50, 1.86)]
for name, key, bm, bw in rows:
    r = bs[key]
    print(f"| {name} | {r['n']} | {bm:.2f} → **{f(r['M7_mhz_rms'], 2)}** MHz | {bw:.2f} → **{f(r['M7_w_rms'], 2)}** W | {ref['heat']['rms_c']:.2f} → **{f(r['M7_rise_rms'], 2)}** °C |")

print("\n## M7, M6 and M5 on the same tiles (rms; the paired difference's 95% interval over tiles)\n")
print("| set | n | clock M7 / M6 / M5 (MHz) | M7 − M6 | M7 − M5 | board M7 / M6 / M5 (W) | M7 − M6 | M7 − M5 | burst D M7 / M6 / M5 (W) |")
print("|---|---:|---|---|---|---|---|---|---|")
for key in ("governed", "pinned", "all", "priority1", "fp32", "fp16", "int8", "measured_governed", "measured_pinned"):
    r = bs[key]
    print(f"| {key} | {r['n']} | {f(r['M7_mhz_rms'], 2)} / {f(r['M6_mhz_rms'], 2)} / {f(r['M5_mhz_rms'], 2)} | {r['M7_minus_M6_mhz_rms_95']} | {r['M7_minus_M5_mhz_rms_95']} | "
          f"{f(r['M7_w_rms'], 2)} / {f(r['M6_w_rms'], 2)} / {f(r['M5_w_rms'], 2)} | {r['M7_minus_M6_w_rms_95']} | {r['M7_minus_M5_w_rms_95']} | "
          f"{f(r['M7_D_rms'], 2)} / {f(r['M6_D_rms'], 2)} / {f(r['M5_D_rms'], 2)} |")
hl = sc["reported"]["heat_law_on_measured_w"]
print(f"\nThe heat law on the measured board W (the rise less {hl['k']:.3f} °C/W × (measured W − {hl['P_idle_w']} W)): rms {hl['rms_c']} °C, mean {hl['mean_c']:+.3f} °C over {hl['n']} tiles.")

print("\n## Every tile (mean over its passes; M7's frozen prediction and band in brackets)\n")
print("| tile | group | prio | passes | clock MHz (runs) | M7 MHz [95%] | board W | M7 W [95%] | rise °C | M7 rise [95%] | burst D W | M7 D |")
print("|---|---|---:|---:|---|---|---:|---|---:|---|---:|---:|")
T = sc["reported"]["tiles"]
for n, t in sorted(T.items(), key=lambda kv: (kv[1]["group"], P["tiles"][kv[0]]["type"], -kv[1]["M7_mhz"], kv[0])):
    m = P["tiles"][n]["models"]["M7"]
    runs = ", ".join(f"{x:.0f}" for x in t["burst_mhz_runs"])
    ins = lambda v, b: "" if b[0] - 1e-9 <= v <= b[1] + 1e-9 else " ✗"
    print(f"| `{n}` | {t['group']} | {t['priority']} | {len(t['passes'])} | **{t['burst_mhz']:.1f}**{ins(t['burst_mhz'], m['burst_mhz_95'])} ({runs}) | {m['burst_mhz']:.1f} [{m['burst_mhz_95'][0]:.0f}, {m['burst_mhz_95'][1]:.0f}] | "
          f"**{t['burst_w']:.2f}**{ins(t['burst_w'], m['burst_board_95'])} | {m['burst_board_w']:.2f} [{m['burst_board_95'][0]:.1f}, {m['burst_board_95'][1]:.1f}] | "
          f"**{t['rise_c']:.2f}**{ins(t['rise_c'], m['burst_die_rise_95'])} | {m['burst_die_rise_c']:.2f} [{m['burst_die_rise_95'][0]:.2f}, {m['burst_die_rise_95'][1]:.2f}] | "
          f"{f(t['D_w'], 2)} | {m['burst_D_w']:.2f} |")
print("\n✗ = outside M7's frozen 95% band.")
print("\n## Each pass scored alone\n")
print("| pass | " + " | ".join(lab) + " |")
print("|---|" + "---|" * len(lab))
for p, rr in R.get("per_pass", {}).items():
    print(f"| {p} | " + " | ".join(f"{f(rr[k].get('rms'), 2) if rr[k].get('rms') is not None else rr[k].get('inside')} {rr[k].get('verdict', '').split(' (')[0]}" for k in lab) + " |")
