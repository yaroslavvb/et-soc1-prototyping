#!/usr/bin/env python3
"""E126 (Q136), POST HOC, labelled: written after the session had started; no rule reads it. From results.json (reduce_e126.py) and the session's
raw records: (1) the ten arms' X on this card, E119's seven and E126's three, per format; (2) each new arm's fit T = C/f + M against the frozen models'
splits; (3) the replicate against E119, cell by cell; (4) the device commands this session actually sent, counted from its own records (every sampler
line is one GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE and GET_ASIC_FREQUENCIES; every
`ettelem config` five GETs; the residency queries' return codes; the drains). Standard library only.
(5b) is a DATED NOTE added on Mon 2 Nov 2026 after verification: the replicate's heat history, which (5) left out (heat_history() below).
Everything else prints as it did in 70c87605.

    python3 tools/claims-v3/e126/posthoc_e126.py <results.json> <RUNS dir (the queue's runs: snapshot-*.json, smoke/, s1/ ...)> [--out posthoc.json] > posthoc.txt
"""
import glob
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
R119 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed/results.json")))
P = json.load(open(os.path.join(HERE, "predictions-e126.json")))
TYPES = ("fp32", "fp16", "int8")
ORDER = ("c1", "c16r32", "c16r8", "c16r4", "c16r2", "c4s", "c8s", "c16s", "c8", "c16")
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
from reduce_hpl import SUS_LAST_S  # noqa: E402  (the registered reducers' sustained window: the last 40 s of work)
TRIP_C = 65  # the software temperature threshold, which ettelem config read at all 53 reads of both sessions


def heat_history(e119_s1, e126_s1, res126):
    """DATED NOTE, Mon 2 Nov 2026, after verification (post hoc, labelled): each session's heat history before its replicate random runs, from the
    sessions' own records. Where block B (the four replicate pairs) began; for each fp32 random sustained run, its start (the gate's reading and the
    reducer's die_start), the seconds from its first work process to the first sampler line whose die mean read >= 65 C (t65), where the reducer's
    sustained window (the last SUS_LAST_S s of work) began against t65, and the run's sustained numbers (results.json cells)."""
    out = {}
    for nm, d, res in (("E119", e119_s1, R119), ("E126", e126_s1, res126)):
        runs = [json.loads(x) for x in open(os.path.join(d, "runs.jsonl")) if x.strip()]
        b0 = next(i for i, r in enumerate(runs) if r["block"] == "B")
        procs = {}
        with opn(os.path.join(d, "launches.jsonl.gz")) as f:
            for x in f:
                if x.strip():
                    L = json.loads(x)
                    if L.get("role") == "work":
                        procs.setdefault(L["run"], []).append(L)
        rec = {"block_B_first_run": runs[b0]["run"], "runs_before_block_B": b0,
               "block_B_start_min": round((runs[b0]["t_first_ms"] - runs[0]["t_first_ms"]) / 60000.0, 1), "random_sustained": {}}
        for r in runs:
            arm = r["label"].split("-")[0]
            if r["block"] != "B" or arm not in P["replicate"] or r["label"] != f"{arm}-fp32-randn":
                continue
            ps = procs.get(r["run"]) or []
            t0, t1 = min(p["t_start_ms"] for p in ps), max(p["t_end_ms"] for p in ps)
            tp = sorted(glob.glob(os.path.join(d, "tel", r["run"] + ".jsonl*")))[0]
            with opn(tp) as f:
                dies = [(j["t_ms"], j["temp_c"]["minshire"][0]) for j in (json.loads(x) for x in f if x.startswith("{"))
                        if j.get("temp_c") and t0 <= j["t_ms"] <= t1]
            hot = next((t for t, c in dies if c >= TRIP_C), None)
            t65 = None if hot is None else round((hot - t0) / 1000.0, 1)
            win = round((t1 - t0) / 1000.0 - SUS_LAST_S, 1)
            c = res["cells"].get(f"{arm}-fp32-randn") or {}
            g = (r.get("gate") or {}).get("reading") or [None] * 4
            rec["random_sustained"][arm] = {"run": r["run"], "runs_before": runs.index(r), "gate_die_c": g[0], "gate_board_w": g[2],
                                            "die_start_c": (c.get("sus_die_start") or [None])[0], "work_s": round((t1 - t0) / 1000.0, 1),
                                            "t65_s": t65, "window_start_s": win, "window_start_minus_t65_s": None if t65 is None else round(win - t65, 1),
                                            "sus_die_c": c.get("sus_die"), "sus_w": c.get("sus_w"), "sus_mhz": c.get("sus_mhz"),
                                            "limit": (c.get("sus_limit_runs") or [None])[0]}
        out[nm] = rec
    out["E126_minus_E119"] = {a: {k: round(out["E126"]["random_sustained"][a][k] - out["E119"]["random_sustained"][a][k], 2)
                                  for k in ("die_start_c", "gate_die_c", "t65_s", "sus_w", "sus_mhz")}
                              for a in P["replicate"] if a in out["E126"]["random_sustained"] and a in out["E119"]["random_sustained"]}
    return out


def opn(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p)


def counts(runs_dir):
    """the device commands sent, from the session's own records"""
    out = {"sampler_lines": 0, "config_reads_session": 0, "config_reads_queue": 0, "sptrace": 0, "residency_queries": 0, "residency_rc": {}, "drains": 0,
           "sessions": []}
    for sd in sorted(glob.glob(os.path.join(runs_dir, "*"))):
        if not os.path.isdir(sd) or not os.path.exists(os.path.join(sd, "session.json")):
            continue
        out["sessions"].append(os.path.basename(sd))
        for p in glob.glob(os.path.join(sd, "tel", "*.jsonl")) + glob.glob(os.path.join(sd, "tel", "*.jsonl.gz")):
            with opn(p) as f:
                out["sampler_lines"] += sum(1 for ln in f if ln.startswith("{"))
        qs = []
        for name in ("queries.jsonl",):
            p = os.path.join(sd, name)
            if os.path.exists(p):
                qs += [json.loads(x) for x in open(p) if x.strip()]
        p = os.path.join(sd, "runs.jsonl")
        if os.path.exists(p):
            qs += [json.loads(x).get("queries") or {} for x in open(p) if x.strip()]
        for q in qs:
            if "config_rc" in q:
                out["config_reads_session"] += 1
            if "sptrace_rc" in q:
                out["sptrace"] += 1
            if "residency_rc" in q:
                out["residency_queries"] += 1
                k = str(q.get("residency_rc"))
                out["residency_rc"][k] = out["residency_rc"].get(k, 0) + 1
        for name in ("run.log",):
            p = os.path.join(sd, name)
            if os.path.exists(p):
                out["drains"] += sum(1 for ln in open(p) if "draining the management queue" in ln)
    for p in glob.glob(os.path.join(runs_dir, "snapshot-*.json")):
        s = json.load(open(p))
        if s.get("config_rc") is not None:
            out["config_reads_queue"] += s.get("config_attempts", 1)
    n, c = out["sampler_lines"], out["config_reads_session"] + out["config_reads_queue"]
    out["dm_commands"] = {"GET_MODULE_POWER": n, "GET_SP_STATS": n, "GET_MODULE_CURRENT_TEMPERATURE": n, "GET_MODULE_VOLTAGE": n,
                          "GET_ASIC_VOLTAGE": n + c, "GET_ASIC_FREQUENCIES": n + c, "GET_MODULE_STATIC_TDP_LEVEL": c, "GET_MODULE_TEMPERATURE_THRESHOLDS": c,
                          "GET_MODULE_POWER_STATE": c, "GET_MODULE_POWER (drain)": out["drains"],
                          "PMIC voltage-register reads (9 per GET_MODULE_VOLTAGE, 2 per GET_ASIC_VOLTAGE)": 9 * n + 2 * (n + c),
                          "WRITE commands": 0}
    return out


def room(runs_dir):
    """the room, by proxies only (no inlet thermometer): the host's ACPI zones and CPU package at the queue's two snapshots; the card's idle die and board
    power in the box's own 5 s history over the 10 minutes before the first launch (medians); the smoke's 30 s rest reading (medians)."""
    out = {}
    for tag in ("start", "end"):
        p = os.path.join(runs_dir, f"sensors-{tag}.json")
        if os.path.exists(p):
            s = json.load(open(p))
            out[f"host_{tag}"] = {"acpitz_0": s.get("acpitz_0-acpi-0", {}).get("temp1", {}).get("temp1_input"),
                                  "acpitz_1": s.get("acpitz_1-acpi-0", {}).get("temp1", {}).get("temp1_input"),
                                  "cpu_package": s.get("coretemp-isa-0000", {}).get("Package id 0", {}).get("temp1_input")}
    p = os.path.join(runs_dir, "history-before.jsonl")
    if os.path.exists(p):
        rows = [json.loads(x) for x in open(p) if x.strip()]
        if rows:
            t1 = rows[-1]["t"]
            idle = [c for r in rows if r["t"] >= t1 - 600000 for c in r.get("cards", []) if c.get("n") == 0 and c.get("die") is not None and not c.get("held")]
            dies, ws = sorted(c["die"] for c in idle), sorted(c["w"] for c in idle if c.get("w") is not None)
            out["card_idle_10min_before"] = {"n": len(idle), "die_median_c": dies[len(dies) // 2] if dies else None, "board_median_w": ws[len(ws) // 2] if ws else None}
    rest = glob.glob(os.path.join(runs_dir, "smoke", "tel", "SMOKE-00-rest-r1.jsonl*"))
    if rest:
        with opn(rest[0]) as f:
            ln = [json.loads(x) for x in f if x.startswith("{")]
        d = sorted(x["temp_c"]["minshire"][0] for x in ln if x.get("temp_c"))
        w = sorted(x["board_w"] for x in ln if x.get("board_w") is not None)
        out["rest_reading"] = {"n": len(ln), "die_median_c": d[len(d) // 2] if d else None, "board_median_w": w[len(w) // 2] if w else None}
    return out


def main():
    res = json.load(open(sys.argv[1]))
    runs_dir = sys.argv[2]
    out = {"label": "post hoc: written after the session had started; no rule reads it"}
    per = res["per_arm"]
    ten = {}
    for t in TYPES:
        row = {}
        for a in ORDER:
            src = per if a in P["new_arms"] else R119["per_arm"]
            v = src.get(f"{a}.{t}") or {}
            row[a] = {"X": None if v.get("X") is None else round(v["X"], 4), "how": v.get("how"), "from": "E126" if a in P["new_arms"] else "E119"}
        ten[t] = row
    out["ten_arms_X"] = ten
    fits = {}
    for a in P["new_arms"]:
        for t in TYPES:
            f = (per.get(f"{a}.{t}") or {}).get("fit") or {}
            rec = {"C_cycles": f.get("C"), "M_us": f.get("M"), "n": f.get("n"), "span_mhz": f.get("span_mhz"), "C_ci": f.get("C_ci"), "M_ci": f.get("M_ci")}
            if a in P["dram_arms"]:
                L = P["laws"][f"{a}.{t}"]
                f1 = R119["per_arm"][f"c1.{t}"]["fit"]
                f16 = R119["per_arm"][f"c16.{t}"]["fit"]
                phi = L["phi"]
                rec["model_S"] = {"C_cycles": round(f1["C"] + phi * (f16["C"] - f1["C"]), 1), "M_us": round(f1["M"] + phi * (f16["M"] - f1["M"]), 4)}
                rec["model_W"] = {"C_cycles": L["C_W_cycles"], "M_us": L["M_W_us"]}
            if a == "c4s":
                f8 = R119["per_arm"][f"c8s.{t}"]["fit"]
                rec["c8s_e119"] = {"C_cycles": f8["C"], "M_us": f8["M"]}
            fits[f"{a}.{t}"] = rec
    out["fits"] = fits
    rep = {}
    for a, ref in P["replicate"].items():
        z, r = res["cells"].get(f"{a}-fp32-zeros") or {}, res["cells"].get(f"{a}-fp32-randn") or {}
        rep[a] = {"randn_mhz": [ref["randn_sus_mhz"], r.get("sus_mhz")], "zeros_mhz": [ref["zeros_sus_mhz"], z.get("sus_mhz")],
                  "randn_w": [R119["cells"][f"{a}-fp32-randn"]["sus_w"], r.get("sus_w")], "randn_die": [R119["cells"][f"{a}-fp32-randn"]["sus_die"], r.get("sus_die")],
                  "zeros_w": [R119["cells"][f"{a}-fp32-zeros"]["sus_w"], z.get("sus_w")], "limit": r.get("sus_limit_runs"),
                  "gap": [ref["gap"], (res["gaps"].get(f"{a}-fp32-randn") or {}).get("sus_rate")]}
    out["replicate_e119_then_e126"] = rep
    out["commands_sent"] = counts(runs_dir)
    out["room"] = {"E119": room(os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed/aifoundry2")), "E126": room(runs_dir)}
    hh = heat_history(os.path.join(ROOT, "docs/reports/data/2026-11-01-e119-gemm-speed/aifoundry2/s1"), os.path.join(runs_dir, "s1"), res)
    c8 = res["cells"].get("c8s-fp32-randn") or {}
    out["c4s_vs_c8s_this_session"] = {a: {"randn_sus_mhz": (res["cells"].get(f"{a}-fp32-randn") or {}).get("sus_mhz"),
                                         "randn_sus_w": (res["cells"].get(f"{a}-fp32-randn") or {}).get("sus_w"),
                                         "gap": (res["gaps"].get(f"{a}-fp32-randn") or {}).get("sus_rate")} for a in ("c4s", "c8s")}
    out["heat_history_dated_note_2026_11_02"] = hh  # added last, so every earlier key keeps its place
    if "--out" in sys.argv:
        json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1)
    print("E126 post hoc, labelled: written after the session had started; no rule reads it.")
    print("\n(1) X = T600 / T800 on aifoundry2, E119's seven arms and E126's three (fp32 / fp16 / int8):")
    for a in ORDER:
        xs = [ten[t][a]["X"] for t in TYPES]
        print(f"  {a:7s} {' / '.join('-' if x is None else f'{x:.3f}' for x in xs)}   ({ten['fp32'][a]['from']})")
    print("\n(2) each new arm's fit T = C/f + M (cycles, us) against the frozen models' splits:")
    for k, v in fits.items():
        extra = ""
        if "model_S" in v:
            extra = f"  S: C {v['model_S']['C_cycles']} M {v['model_S']['M_us']}   W: C {v['model_W']['C_cycles']} M {v['model_W']['M_us']}"
        if "c8s_e119" in v:
            extra = f"  c8s (E119): C {v['c8s_e119']['C_cycles']} M {v['c8s_e119']['M_us']}"
        print(f"  {k:10s} C {v['C_cycles']} M {v['M_us']} (n {v['n']}, span {v['span_mhz']}){extra}")
    print("\n(3) the replicate, E119 then E126 (fp32 sustained):")
    for a, v in rep.items():
        print(f"  {a:6s} random {v['randn_mhz']} MHz, {v['randn_w']} W, die {v['randn_die']} C; zeros {v['zeros_mhz']} MHz, {v['zeros_w']} W; gap {v['gap']}; limit {v['limit']}")
    c = out["commands_sent"]
    print("\n(4) device commands sent, from the session's own records:")
    print(f"  sessions {c['sessions']}; sampler lines {c['sampler_lines']}; config reads {c['config_reads_session']} in sessions + {c['config_reads_queue']} by the queue; "
          f"sptrace {c['sptrace']}; residency queries {c['residency_queries']} (return codes {c['residency_rc']}: 2 = refused before the device opened); drains {c['drains']}")
    for k, v in c["dm_commands"].items():
        print(f"    {k}: {v}")
    print("\n(5) the room, by proxies (no inlet thermometer): E119 (Sun 1 Nov, 19:30 PST) against E126 (Mon 2 Nov, 07:33 PST)")
    for k in ("E119", "E126"):
        print(f"  {k}: {json.dumps(out['room'][k])}")
    print("\n(5b) DATED NOTE, Mon 2 Nov 2026, after verification (post hoc, labelled): the heat history, which (5) left out. The idle proxies in (5)")
    print("  compare the two rooms; how long and how hard the card had worked before each replicate random run compares the runs.")
    for k in ("E119", "E126"):
        print(f"  {k}: block B (the replicate pairs) began with {hh[k]['block_B_first_run']}, after {hh[k]['runs_before_block_B']} runs, "
              f"{hh[k]['block_B_start_min']} min into the session")
    print(f"  fp32 random sustained runs: start = the gate's die reading / the reducer's die_start (C); t65 = s from the first work process to the first die")
    print(f"  mean >= {TRIP_C} C; window = where the reducer's sustained window (the last {SUS_LAST_S:.0f} s of work) began, in s after t65 (negative: before it)")
    for a in P["replicate"]:
        cells = []
        for k in ("E119", "E126"):
            v = hh[k]["random_sustained"].get(a)
            if v:
                cells.append(f"{k}: run {v['runs_before']:2d}, start {v['gate_die_c']:.0f}/{v['die_start_c']} C, t65 {v['t65_s']} s of {v['work_s']}, "
                             f"window {v['window_start_minus_t65_s']:+.1f} s, {v['sus_w']} W {v['sus_mhz']} MHz die {v['sus_die_c']} C {v['limit']}")
        print(f"  {a:6s} " + "\n         ".join(cells))
    for a, v in hh["E126_minus_E119"].items():
        print(f"  {a:6s} E126 - E119: start {v['gate_die_c']:+.0f} C (gate) / {v['die_start_c']:+.0f} C (die_start); t65 {v['t65_s']:+.1f} s; "
              f"sustained {v['sus_w']:+.2f} W, {v['sus_mhz']:+.1f} MHz")
    print("\n(6) c4s against c8s in this session (fp32 random sustained; R6 compared c4s with E119's c8s):")
    for a, v in out["c4s_vs_c8s_this_session"].items():
        print(f"  {a:4s} {v}")


if __name__ == "__main__":
    main()
