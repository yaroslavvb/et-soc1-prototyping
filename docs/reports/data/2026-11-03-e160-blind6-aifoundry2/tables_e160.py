#!/usr/bin/env python3
"""E160 (Q139): the README's tables, printed from results.json and the frozen predictions (presentation only: no number is computed here that the
registered reducer did not write, except differences, the all-92 reference rms from the frozen reference errors, and the band each tile's value is
read against). E143's tables_e143.py with E160's names, M8 as the primary model and M7 and M6 beside it.

    python3 docs/reports/data/2026-11-03-e160-blind6-aifoundry2/tables_e160.py > docs/reports/data/2026-11-03-e160-blind6-aifoundry2/tables.md

SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
R = json.load(open(os.path.join(HERE, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "e160", "predictions-e160.json")))
sc = R["score"]
ru = sc["rules"]
ref = P["reference"]


def f(x, n=1):
    return "-" if x is None else f"{x:.{n}f}"


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


REF_RMS = {"E160-F1": rms(ref["governed"]["mhz_err"]), "E160-F2": rms(ref["pinned"]["mhz_err"]),
           "E160-W1": rms(ref["governed"]["w_err"]), "E160-W2": rms(ref["pinned"]["w_err"]), "E160-H1": rms(ref["heat"]["rise_err_c"])}
# the all-92 "before" is m8.json's own figure (E160.md: 7.16 MHz and 1.86 W); the rows copied into predictions-e160.json are rounded to 0.1 MHz
M8E2E = json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-q139m-model", "m8.json")))["aifoundry2"]["end_to_end_from_M8_nested_D"]
ALL_MHZ = M8E2E["rms_mhz"]
ALL_W = M8E2E["rms_board_w"]

print("## Verdicts\n")
print("| rule | set | n | measured | reference line (2.5% – 97.5%) or coverage line | verdict |")
print("|---|---|---:|---|---|---|")
lab = {"E160-F1": ("burst clock, governed", "MHz"), "E160-F2": ("burst clock, pinned", "MHz"), "E160-F3": ("burst clock, all: inside ±16.9 MHz", ""),
       "E160-W1": ("board W, governed", "W"), "E160-W2": ("board W, pinned", "W"), "E160-W3": ("board W, all: inside ±3.50 W", ""),
       "E160-H1": ("die rise, all", "°C"), "E160-H3": ("die rise, all: inside ±1.41 °C", ""),
       "E160-PK": ("highest board sample, every tile: at or under M8's 95% peak", "")}
for k, (s, u) in lab.items():
    v = ru[k]
    if "rms" in v:
        print(f"| **{k}** | {s} | {v['n']} | rms {f(v['rms'], 2)} {u} (mean error {v['mean_err']:+.2f}) | {f(v['range_2.5_97.5'][0], 2)} – {f(v['range_2.5_97.5'][1], 2)} {u} "
              f"(reference rms {f(REF_RMS.get(k, v['ref_rms']), 2)}) | **{v['verdict']}** |")
    else:
        extra = ""
        if k == "E160-PK" and v.get("over"):
            extra = " (over: " + "; ".join(f"`{o['tile']}` {o['peak_w']:.2f} W against {o['hi95_w']:.2f}" for o in v["over"]) + ")"
        print(f"| **{k}** | {s} | {v['n']} | {v['inside']} of {v['n']} inside{extra} | at least {v['line']} | **{v['verdict']}** |")
cc = R["c_check"]
print(f"| **E160-C** | the check of C, every launch of every BURST run | {cc['launches']} | " + ", ".join(f"{k} {v}" for k, v in cc["by_verdict"].items())
      + " (bit-exact) | all PASS | **" + cc["verdict"] + "** |")
rp = R["replicate"]
print("| **E160-R0** | E80's replicate tiles | 2 | " + "; ".join(f"{k[2:]} {f(t.get('burst_mhz'), 1)} MHz ({t.get('d_mhz'):+.1f}), {f(t.get('burst_w'), 2)} W ({t.get('d_w'):+.2f})"
                                                       for k, t in rp["tiles"].items() if t.get("n")) + f" | within 25 MHz and 3.37 W of E80's and E83's cells | **{rp['verdict']}** (a diagnostic) |")
sv = R["scale"]["verdict_E160-S"]
print(f"| **E160-S** | rank 5: aifoundry2's scale | - | floats {R['scale']['floats|M8_predicted_D600']['median']} and int8 {R['scale']['int8|M8_predicted_D600']['median']} against M8's "
      f"predicted D600 (reported) | V600² physical within 1% of the scale on aifoundry3's measured D | **{sv['floats'].split(' (')[0]}** (no E153 D) |")

print("\n## Before and after (rms, measured − predicted, M8)\n")
print("| set | n | clock: reference (before) → E160 blind (after) | board W: before → after | die rise: before → after |")
print("|---|---:|---|---|---|")
bs = sc["reported"]["by_set"]
hr = REF_RMS["E160-H1"]
rows = [("governed (M8 < 795 MHz)", "governed", REF_RMS["E160-F1"], REF_RMS["E160-W1"]),
        ("pinned (M8 795–800 MHz)", "pinned", REF_RMS["E160-F2"], REF_RMS["E160-W2"]),
        ("all 48", "all", ALL_MHZ, ALL_W)]
for name, key, bm, bw in rows:
    r = bs[key]
    print(f"| {name} | {r['n']} | {bm:.2f} → **{f(r['M8_mhz_rms'], 2)}** MHz | {bw:.2f} → **{f(r['M8_w_rms'], 2)}** W | {hr:.2f} → **{f(r['M8_rise_rms'], 2)}** °C |")
pk = ru["E160-PK"]["per_burst"]
print(f"\nThe peak (M8's new rule): {pk['inside']} of {pk['n']} counted bursts at or under their tile's 95% peak; the highest sample against M8's expected peak: "
      f"rms {pk['rms_vs_expected_w']:.2f} W, mean {pk['mean_vs_expected_w']:+.2f} W (M8's own in-sample figure, on E143's peaks: 1.60 W rms).")

print("\n## M8, M7 and M6 on the same tiles (rms; the paired difference's 95% interval over tiles; reported, never a verdict)\n")
print("| set | n | clock M8 / M7 / M6 (MHz) | M8 − M7 | M8 − M6 | board M8 / M7 / M6 (W) | M8 − M7 | M8 − M6 | burst D M8 / M7 / M6 (W) | M8 − M7 | M8 − M6 |")
print("|---|---:|---|---|---|---|---|---|---|---|---|")
for key in ("governed", "pinned", "all", "priority1", "new_kinds", "real", "fp32", "fp16", "int8", "measured_governed", "measured_pinned"):
    r = bs[key]
    print(f"| {key} | {r['n']} | {f(r['M8_mhz_rms'], 2)} / {f(r['M7_mhz_rms'], 2)} / {f(r['M6_mhz_rms'], 2)} | {r['M8_minus_M7_mhz_rms_95']} | {r['M8_minus_M6_mhz_rms_95']} | "
          f"{f(r['M8_w_rms'], 2)} / {f(r['M7_w_rms'], 2)} / {f(r['M6_w_rms'], 2)} | {r['M8_minus_M7_w_rms_95']} | {r['M8_minus_M6_w_rms_95']} | "
          f"{f(r['M8_D_rms'], 2)} / {f(r['M7_D_rms'], 2)} / {f(r['M6_D_rms'], 2)} | {r['M8_minus_M7_D_rms_95']} | {r['M8_minus_M6_D_rms_95']} |")
hl = sc["reported"]["heat_law_on_measured_w"]
print(f"\nThe heat law on the measured board W (the rise less {hl['k']:.3f} °C/W × (measured W − {hl['P_idle_w']} W)): rms {hl['rms_c']} °C, mean {hl['mean_c']:+.3f} °C over {hl['n']} tiles.")
kc = sc["reported"]["kernel_clock_minus_sampled_mhz"]
print(f"The kernel's own clock less the sampled clock: mean {kc['mean']:+.2f} MHz over {kc['n']} tiles, {kc['governed_mean']:+.2f} MHz on the governed ones.")

print("\n## Every tile (mean over its passes; M8's frozen prediction and 95% band in brackets)\n")
print("| tile | group | prio | class | passes | clock MHz (runs) | M8 MHz [95%] | board W | M8 W [95%] | rise °C | M8 rise [95%] | burst D W | M8 D | highest sample W | M8 peak / 95% |")
print("|---|---|---:|---|---:|---|---|---:|---|---:|---|---:|---:|---:|---|")
T = sc["reported"]["tiles"]
for n, t in sorted(T.items(), key=lambda kv: (kv[1]["group"], P["tiles"][kv[0]]["type"], kv[1]["M8_mhz"], kv[0])):
    m = P["tiles"][n]["models"]["M8"]
    runs = ", ".join(f"{x:.0f}" for x in t["burst_mhz_runs"])
    ins = lambda v, b: "" if b[0] - 1e-9 <= v <= b[1] + 1e-9 else " ✗"
    pkv = max(x for x in t["peak_w_runs"] if x is not None)
    pko = "" if pkv <= m["peak_board_hi95_w"] + 1e-9 else " ✗"
    print(f"| `{n}` | {t['group']} | {t['priority']} | {t['class']} | {len(t['passes'])} | **{t['burst_mhz']:.1f}**{ins(t['burst_mhz'], m['burst_mhz_95'])} ({runs}) | "
          f"{m['burst_mhz']:.1f} [{m['burst_mhz_95'][0]:.0f}, {m['burst_mhz_95'][1]:.0f}] | "
          f"**{t['burst_w']:.2f}**{ins(t['burst_w'], m['burst_board_95'])} | {m['burst_board_w']:.2f} [{m['burst_board_95'][0]:.1f}, {m['burst_board_95'][1]:.1f}] | "
          f"**{t['rise_c']:.2f}**{ins(t['rise_c'], m['burst_die_rise_95'])} | {m['burst_die_rise_c']:.2f} [{m['burst_die_rise_95'][0]:.2f}, {m['burst_die_rise_95'][1]:.2f}] | "
          f"{f(t['D_w'], 2)} | {m['burst_D_w']:.2f} | {pkv:.2f}{pko} | {m['peak_board_w']:.2f} / {m['peak_board_hi95_w']:.2f} |")
print("\n✗ = outside M8's frozen 95% band (for the highest sample: over M8's 95% peak). Classes (the pool's `case`): 0 anchor; B int8 B position (held or "
      "flipped at one bit); C the C-register candidate; E exponent-heavy; L int8 whole-line or whole-word flip-flops; R real model tiles; S single bits on "
      "other base words; W power-law int8 weights; Z zeros' transport.")
print("\n## Each pass scored alone (reported)\n")
print("| pass | " + " | ".join(lab) + " |")
print("|---|" + "---|" * len(lab))
for p, rr in (R.get("per_pass") or {}).items():
    print(f"| {p} | " + " | ".join(f"{f(rr[k].get('rms'), 2) if rr[k].get('rms') is not None else rr[k].get('inside')} {(rr[k].get('verdict') or '').split(' (')[0]}" for k in lab) + " |")
