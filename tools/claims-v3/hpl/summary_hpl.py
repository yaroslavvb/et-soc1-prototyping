#!/usr/bin/env python3
"""E64: the results section of the data README, as Markdown, from reduce_hpl.py's results and surface_hpl.py's figures.

    python3 tools/claims-v3/hpl/summary_hpl.py --results results.json --figures figures.json > results.md
"""
import argparse
import json
import statistics as st

OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}


def g(x, n=1):
    return "–" if x is None else f"{x:.{n}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--figures", required=True)
    a = ap.parse_args()
    R = json.load(open(a.results))
    F = json.load(open(a.figures))
    out = []
    rules = R["rules"]
    out.append("### The registered rules\n")
    out.append("| Rule | Verdict | Counts |\n|---|---|---|")
    for k in ("R1", "R2", "R3", "R4"):
        v = rules[k]
        counts = {x: y for x, y in v.items() if x not in ("runs", "rows", "verdict")}
        out.append(f"| {k} | **{v['verdict']}** | {json.dumps(counts)} |")
    out.append("")
    out.append("### The cool-die ladder (LAD, MIN): each run's power at 800 MHz and its clock after the start ramp\n")
    out.append("| operands | minions | runs | W at 800 MHz | mean MHz after 1.5 s | TFLOPS, whole run | power steps down | "
               "first step |\n|---|---|---|---|---|---|---|---|")
    groups = {}
    for r in F["runs"]:
        if r["block"] in ("LAD", "MIN") and r.get("p800_w"):
            groups.setdefault((r["values"], r["minions"]), []).append(r)
    for (v, n), xs in sorted(groups.items(), key=lambda kv: st.mean(r["p800_w"] for r in kv[1])):
        out.append(f"| {v} | {n} | {len(xs)} | {g(st.mean(r['p800_w'] for r in xs))} | "
                   f"{g(st.mean(r['mhz_steady'] for r in xs), 0)} | {g(st.mean(r['rate_t'] for r in xs), 2)} | "
                   f"{sum((r.get('events') or {}).get('power_down', 0) for r in xs)} | "
                   f"{', '.join(sorted({str(r.get('first_down_kind')) for r in xs}))} |")
    out.append("")
    out.append("### Hot starts (HOT, HOT2)\n")
    out.append("| run | die at launch | mean MHz | thermal steps | power steps | first step |\n|---|---|---|---|---|---|")
    for r in F["runs"]:
        if r["block"] in ("HOT", "HOT2"):
            ev = r.get("events") or {}
            out.append(f"| {r['run']} | {r.get('die_start')} | {g(r.get('mhz_steady'), 0)} | {ev.get('thermal_down', 0)} | "
                       f"{ev.get('power_down', 0)} | {r.get('first_down_kind')} |")
    out.append("")
    out.append("### Sustained (SUS): the last 40 s of about 80 s\n")
    out.append("| type | operands | rate at 800 MHz | cool die, first 8 s | sustained (kernel) | sustained (wall) | MHz | "
               "die °C | board W | at 800 | thermal | power | ramp |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted((r for r in F["runs"] if r["block"] == "SUS"), key=lambda r: (r["type"], r["values"])):
        sl = r.get("sus_last") or {}
        peak = 1024 * OPS[r["type"]] / CYC[r["type"]] * 800e6 / 1e12
        cool = 1024 * OPS[r["type"]] / CYC[r["type"]] * r["first8_mhz"] * 1e6 / 1e12 if r.get("first8_mhz") else None
        out.append(f"| {r['type']} | {r['values']} | {g(peak)} | {g(cool)} | {g(r.get('sus_rate_t'))} | "
                   f"{g(r.get('sus_rate_wall_t'))} | {g(r.get('sus_mhz_mean'), 0)} | {g(r.get('sus_die_mean'))} | "
                   f"{g(r.get('sus_w_mean'))} | {g(sl.get('800'), 2)} | {g(sl.get('thermal'), 2)} | {g(sl.get('power'), 2)} | "
                   f"{g(sl.get('ramp'), 2)} |")
    out.append("")
    gov, fit, th = F.get("governor") or {}, F.get("fit") or {}, F.get("thermal") or {}
    out.append("### The model (descriptive)\n")
    out.append(f"- Power per clock, referred to a 58 °C die: busy offsets {json.dumps({k: round(v, 1) for k, v in fit.get('B', {}).items()})} W "
               f"plus each run's switching term × (V/0.517)²·f/600; rms {g(fit.get('rms_w'), 2)} W over {fit.get('n')} points.")
    out.append(f"- The governor: a first-order average of the board's power, time constant {gov.get('tau_s')} s, compared with "
               f"the level once per {gov.get('pass_s')} s pass, one point up or down; mean clock after the ramp reproduced to "
               f"{gov.get('rms_mhz')} MHz rms over {gov.get('n')} cool-die runs.")
    if th:
        out.append(f"- The thermal line over the SUS runs' last 40 s: die = {th.get('a_c')} + {th.get('k_c_per_w')} °C per W of board "
                   f"power; it reads 65.5 °C at {th.get('cap_w_at_65_5')} W.")
    ct = F.get("cap_table")
    if ct:
        out.append("\n**The cap table** (the model on each measured kind's own powers, cool die, mean MHz):\n")
        out.append("| type | operands | " + " | ".join(f"{c} W" for c in ct["caps_w"]) + " |\n|---|---|"
                   + "---|" * len(ct["caps_w"]))
        for r in sorted(ct["rows"], key=lambda r: (r["type"], r["p_w"]["800"])):
            out.append(f"| {r['type']} | {r['values']} | " + " | ".join(f"{r['mhz'][str(c)]:.0f}" for c in ct["caps_w"]) + " |")
    print("\n".join(out))


if __name__ == "__main__":
    main()
