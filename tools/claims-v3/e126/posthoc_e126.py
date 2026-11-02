#!/usr/bin/env python3
"""E126 (Q136), POST HOC, labelled: written after the session had started; no rule reads it. From results.json (reduce_e126.py) and the session's
raw records: (1) the ten arms' X on this card, E119's seven and E126's three, per format; (2) each new arm's fit T = C/f + M against the frozen models'
splits; (3) the replicate against E119, cell by cell; (4) the device commands this session actually sent, counted from its own records (every sampler
line is one GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE and GET_ASIC_FREQUENCIES; every
`ettelem config` five GETs; the residency queries' return codes; the drains). Standard library only.

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
    c8 = res["cells"].get("c8s-fp32-randn") or {}
    out["c4s_vs_c8s_this_session"] = {a: {"randn_sus_mhz": (res["cells"].get(f"{a}-fp32-randn") or {}).get("sus_mhz"),
                                         "randn_sus_w": (res["cells"].get(f"{a}-fp32-randn") or {}).get("sus_w"),
                                         "gap": (res["gaps"].get(f"{a}-fp32-randn") or {}).get("sus_rate")} for a in ("c4s", "c8s")}
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
    print("\n(6) c4s against c8s in this session (fp32 random sustained; R6 compared c4s with E119's c8s):")
    for a, v in out["c4s_vs_c8s_this_session"].items():
        print(f"  {a:4s} {v}")


if __name__ == "__main__":
    main()
