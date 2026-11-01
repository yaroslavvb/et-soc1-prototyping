#!/usr/bin/env python3
"""E89: the README's tables, printed from e89.json (it changes nothing). Run from the data directory:
    python3 tables_e89.py e89.json > tables.txt
"""
import json
import math
import sys

e = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "e89.json"))
B = e["blocks"]
ORDER = ["i8full", "i8gauss", "i8small", "i8sp50", "i8neg1", "i8zero", "f32ones", "f32randn"]
NAME = {"i8full": "int8 full (random)", "i8gauss": "int8 gauss_q", "i8small": "int8 smallint", "i8sp50": "int8 sparse50",
        "i8neg1": "int8 neg_ones (−1)", "i8zero": "int8 zeros", "f32ones": "fp32 ones (1.0)", "f32randn": "fp32 randn (reference)"}


def pm(x, n=3, k="mean"):
    if not x or x.get(k) is None:
        return "—"
    s = f"{x[k]:.{n}f}"
    if x.get("ci95") is not None:
        s += f" ± {x['ci95']:.{n}f}"
    return s


def rr(r, n=3):
    return "—" if not r else f"{r['r']:.{n}f} [{r['lo']:.{n}f}, {r['hi']:.{n}f}]"


print("## T1 the lock-in at 1/60 Hz (34-sensor mean), each kind against its reference")
print()
print("| block | against | E78 W (D or S) | board fundamental (W) | over (2/π)·E78 W | temperature fundamental (°C) | H (°C per board W) | °C per W of E78's switching power | r = H / H_ref [95%] | phase (deg) | laps |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for b in ORDER:
    v = B[b]
    if not v.get("laps"):
        print(f"| {NAME[b]} | {v['ref']} | | | | | | | | | 0 |")
        continue
    d = v["denominator"]
    print(f"| {NAME[b]} | {v['ref']} | {d['what'].split()[0]} {d['w']:.3f} | {pm(v['P_fund_W'])} | {v['P_fund_over_E78']:.3f} | "
          f"{pm(v['T_fund_C'])} | {pm(v['H_proj_ref_phase'], 4)} | {pm(v['C_per_W_E78'], 4)} | {rr(v.get('r_H')) if b != 'f32randn' else '1 (by definition)'} | "
          f"{v['H_phase_deg']:.1f} | {v['laps']} |")
print()
print("## T2 the same blocks: E78's 2 s window and the 30 s swing on the fine reading, and the whole-degree reading")
print()
print("| block | step2: 2 s rise (°C) | step2 per E78 W (°C/W) | r_step2 [95%] | swing30 (°C) | swing30 per E78 W (°C/W) | r_swing30 [95%] | whole-degree mean: temperature fundamental (°C) | r on the whole-degree mean [95%] |")
print("|---|---|---|---|---|---|---|---|---|")
for b in ORDER:
    v = B[b]
    if not v.get("laps"):
        continue
    print(f"| {NAME[b]} | {pm(v['step2_C'])} | {pm(v['step2_C_per_W_E78'], 4)} | {rr(v.get('r_step2')) if b != 'f32randn' else '—'} | "
          f"{pm(v['swing30_C'])} | {pm(v['swing30_C_per_W_E78'], 4)} | {rr(v.get('r_swing30')) if b != 'f32randn' else '—'} | "
          f"{pm(v['T_int_fund_C'])} | {rr(v.get('r_H_int')) if b != 'f32randn' else '—'} |")
print()
print("## T3 per pass (E78's convention: the pass is the unit, n = 2, t(0.975, 1) = 12.706)")
print()
print("| block | H pass 8910 | H pass 8911 | mean ± 95% over passes |")
print("|---|---|---|---|")
for b in ORDER:
    v = B[b]
    if not v.get("laps"):
        continue
    bp = v["H_proj_by_pass"]
    print(f"| {NAME[b]} | {bp.get('8910', float('nan')):.4f} | {bp.get('8911', float('nan')):.4f} | {pm(v['H_proj_over_passes'], 4)} |")
print()
print("## T4 per sensor: H of each of the 34 sensors (°C per W, on the reference phase)")
print()
ref = B["f32randn"].get("H_sensor_proj") or []
for b in ORDER:
    v = B[b]
    h = v.get("H_sensor_proj")
    if not h:
        continue
    x = [q for q in h if q is not None]
    srt = sorted(x)
    print(f"- {NAME[b]}: min {srt[0]:.3f}, median {srt[len(srt)//2]:.3f}, max {srt[-1]:.3f} °C/W over {len(x)} sensors; "
          f"correlation with the reference's pattern {v.get('sensor_corr_with_ref') if v.get('sensor_corr_with_ref') is None else round(v['sensor_corr_with_ref'], 3)}")
print()
print("Reference's 34 values (sensor 0..33): " + ", ".join(f"{q:.3f}" for q in ref))
print()
print("## T5 verdicts")
print()
print("| rule | cell | measured | band | verdict |")
print("|---|---|---|---|---|")
for v in e["verdicts"]:
    m = v["measured"]
    if isinstance(m, dict) and "r" in m:
        ms = f"{m['r']:.3f} [{m['lo']:.3f}, {m['hi']:.3f}]"
    elif isinstance(m, dict):
        ms = ", ".join(f"{k} {val:.4f}" if isinstance(val, float) else f"{k} {val}" for k, val in m.items())
    else:
        ms = "—"
    print(f"| {v['rule']} | {v['cell']} | {ms} | {v['band']} | **{v['verdict']}** |")
print()
print("tally:", e["tally"])
print()
i = e["instrument"]
print("## T6 the instrument")
print()
print(f"- samples {i['samples']}, with all 34 sensors {i['with_34']} ({i['share_with_34']:.4f}); firmware integer mean rebuilt from the codes equals minshire_avg in {i['floor_mean_eq_firmware']} ({i['share_eq']:.4f})")
for d in i["idle_dither"]:
    off = d["off_mode_share_per_sensor"]
    print(f"- idle bracket, pass {d['pass']}: {d['n']} samples; share of samples off each sensor's modal code: median {sorted(off)[len(off)//2]:.3f}, range {min(off):.3f}-{max(off):.3f}; SD of the 34-sensor mean {d['mean34_sd']:.4f} °C")
bd = i["block_dither"]
if bd:
    print(f"- inside blocks: share of samples off each sensor's 1 s rolling median, mean over sensors {min(x['off_median_share_mean'] for x in bd):.3f}-{max(x['off_median_share_mean'] for x in bd):.3f} across blocks")
print()
print("## T7 gates")
print()
for g in e["gates"]:
    if "block" in g:
        print(f"- pass {g['pass']} {g['block']}: ok {g['ok']}, clock600 {g['clock_600']}, mV {g['mv_min']}-{g['mv_max']}, samples {g['samples']} ({g['with_34']} with 34), launches {g['launches']} (failures {g['launch_failures']}), cycles/op records {g['cycles_per_op_records']} (off {g['cycles_per_op_off']})")
    else:
        print(f"- pass {g['pass']} gate: die {g['die_c']} C, reached {g['reached']}, waited {g['wait_s']:.1f} s")
print()
print(f"reference phase {e['phi_ref_deg']:.1f} deg")
