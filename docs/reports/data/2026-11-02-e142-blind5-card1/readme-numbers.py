#!/usr/bin/env python3
"""E142 (desk, reported): print the numbers the README quotes, from this directory's scored.json, e142.json, the arms,
telemetry-max.json and posthoc/runlength-posthoc.json, so every figure in the README can be traced to a file and a key. Standard
library only.

    python3 docs/reports/data/2026-11-02-e142-blind5-card1/readme-numbers.py > docs/reports/data/2026-11-02-e142-blind5-card1/readme-numbers.txt
SPDX-License-Identifier: Apache-2.0"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
S = json.load(open(os.path.join(HERE, "scored.json")))
P = S["primary"]
F = ("fp32", "fp16", "int8")


def f(x, n=3, sign=False):
    return "-" if x is None else (f"{x:+.{n}f}" if sign else f"{x:.{n}f}")


print("== passes:", P["passes"], "set aside:", P["set_aside"], "leak:", P["leak"])
print("== verdicts (primary) and arm sensitivity")
for rid, r in P["rules"].items():
    if "rms" in r:
        extra = (f"rms {r['rms']:.3f} {r['unit']} n {len(r['tiles'])} interval [{r['interval']['lo95']:.3f}, {r['interval']['hi95']:.3f}] "
                 f"below {r['below_interval']}")
    elif "bias_meas_minus_pred_w" in r:
        extra = (f"bias {r['bias_meas_minus_pred_w']:+.3f} W n {len(r['tiles'])} interval [{r['interval']['lo95']:+.3f}, "
                 f"{r['interval']['hi95']:+.3f}]")
    elif "share" in r:
        extra = f"{r['inside']} of {r['n']} (low end {r['binomial_low_2p5']}); outside {r['outside']}"
    elif "d_rms_w" in r:
        extra = f"d {r['d_rms_w']:+.3f} W [{r['lo95']:+.3f}, {r['hi95']:+.3f}] n {r['n']}"
    elif "median_ratio" in r:
        extra = f"median {r['median_ratio']:.4f} [{r['lo95']:.4f}, {r['hi95']:.4f}] n {r['n']}"
    else:
        extra = r.get("why", "")
    arms = {n: (a.get("rules") or {}).get(rid, {}).get("verdict") for n, a in S["arms"].items()}
    print(f"  {rid}: {r['verdict']} | {extra} | arms {arms}")
print("== reported per model (priority-1 rms / bias per format; 30 non-anchor rms / bias; coverage)")
for m, x in P["reported"].items():
    pw = x["power"]
    print(f"  {m}: " + "; ".join(f"{t} rms {f(pw[t]['rms'])} bias {f(pw[t]['bias'], sign=True)}" for t in F)
          + f"; all30 rms {f(x['power_all_nonanchor']['rms'])} bias {f(x['power_all_nonanchor']['bias'], sign=True)}"
          + f"; inside {x['coverage_power'].get('inside')}/{x['coverage_power'].get('n')} outside {x['coverage_power'].get('outside')}")
    if "heat" in x:
        print("     heat: " + "; ".join(f"{t} rms {f(x['heat'][t]['rms'])} bias {f(x['heat'][t]['bias'], sign=True)}" for t in F)
              + f"; inside {x['coverage_heat'].get('inside')}/{x['coverage_heat'].get('n')} outside {x['coverage_heat'].get('outside')}")
for name, a in S["arms"].items():
    rep = a.get("reported", {}).get("M7")
    if rep:
        print(f"  arm {name} (leak {(a.get('leak') or {}).get('k_w_per_c')}): M7 "
              + "; ".join(f"{t} rms {f(rep['power'][t]['rms'])} bias {f(rep['power'][t]['bias'], sign=True)}" for t in F)
              + f"; inside {rep['coverage_power'].get('inside')}/{rep['coverage_power'].get('n')}; passes {a.get('passes')} "
                f"set aside {a.get('set_aside')}")
print("== both-card reference arm:", P.get("reported_both_card_reference"))
print("== heat at the measured run length (registered reported arm):",
      json.dumps(P.get("reported_heat_at_measured_run_length"), default=str)[:900])
ph = os.path.join(HERE, "posthoc", "runlength-posthoc.json")
if os.path.exists(ph):
    for n, v in json.load(open(ph))["views"].items():
        print(f"   post hoc {n}: T_run {v['T_run_median_s']} rms {v['rms_c']} bias {v['bias_c']} inside {v['coverage'].get('inside')}/"
              f"{v['coverage'].get('n')} left out {v['tiles_left_out']}")
print("== rise per board W:", P.get("reported_rise_per_board_w"))
print("== pool anchors:")
for t, a in sorted(P["pool_anchors"].items()):
    print(f"  {t}: measured D {f(a['measured_D'])} M7 {f(a['M7_D'])} error {f(a['error'], sign=True)} inside {a['inside']} "
          f"dT {f(a['measured_dT'])}")
print("== E78 anchors D (this session):", {k: (f(v['mean']), [round(x, 3) for x in v['per_pass']]) for k, v in P["e78_anchors_D"].items()})
e131 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e131-real-tiles-card1/e131.json")
if os.path.exists(e131):
    r1 = json.load(open(e131))
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        v = [r1["per_pass"][str(p)][a]["D"] for p in r1["passes"] if a in r1["per_pass"][str(p)]]
        print(f"   E131 {a}: {statistics.mean(v):.3f} over {len(v)} passes")
print("== per tile (M7 power; error = measured - M7):")
rows = P["power_rows"]["M7"]
hr = P["heat_rows"]["M7"]
for t, r in sorted(rows.items(), key=lambda kv: (kv[1]["type"], kv[0])):
    e6 = P["power_rows"]["M6"][t]["error"]
    e5 = P["power_rows"]["M5"][t]["error"]
    h = hr.get(t, {})
    print(f"  {t:34s} p{r['priority']}{'a' if r['pool_anchor'] else ' '} meas {f(r['measured'])} sd {f(r['sd'])} M7 {r['pred']:.3f} "
          f"err {f(r['error'], sign=True)} in {r['inside']} | M6 err {f(e6, sign=True)} M5 err {f(e5, sign=True)} | dT {f(h.get('measured'))} "
          f"pred {f(h.get('pred'))} err {f(h.get('error'), sign=True)} in {h.get('inside')}")
print("== errors by case (M7, non-anchor):")
by = {}
for t, r in rows.items():
    if r["pool_anchor"] or r["error"] is None:
        continue
    by.setdefault(r["case"], []).append(r["error"])
for c, v in sorted(by.items()):
    print(f"  {c}: n {len(v)} mean {statistics.mean(v):+.3f} rms {math.sqrt(sum(x * x for x in v) / len(v)):.3f}")
tm = os.path.join(HERE, "telemetry-max.json")
if os.path.exists(tm):
    t = json.load(open(tm))
    print("== telemetry max: board", t["board_w_max"], "hottest shire", t["hottest_shire_c_max"])
    for k, v in t["blocks"].items():
        print(f"  {k}: samples {v['samples']} board {v['board_w_min']}-{v['board_w_max']} (p999 {v['board_w_p999']}) shire mean "
              f"{v['shire_mean_c_min']}-{v['shire_mean_c_max']} hottest {v['hottest_shire_c_max']} pmic {v['pmic_c_max']} mhz {v['minion_mhz']} "
              f"since_reset {v['since_reset_ms']} rail@34.5 {v['rail_samples_at_34p5']}")
