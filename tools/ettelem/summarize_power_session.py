#!/usr/bin/env python3
"""Reduce the 20 September load-step session (E5, E6) to the summary.json the power-and-temperature page reads.

    python3 tools/ettelem/summarize_power_session.py docs/reports/data/2026-09-20-power-aifoundry2 \\
        --out docs/reports/data/2026-09-20-power-aifoundry2/summary.json

Reads, in the data directory: thermal-telemetry.jsonl (ettelem at 10 Hz), thermal-phases.jsonl (run_thermal.sh's
phase marks), per-shire-voltage-idle.json (tools/ettelem/parse_sptrace_voltage.py on raw/sp1.bin) and, if present,
thermal-loads.log or raw/thermal-loads.log (run_thermal.sh's one line per load process). Writes, merged into an
existing --out file whose other sections (horace, horace2) are kept as they are:

  thermal.phases  [{phase, t}]: each mark's time in s after the idle0 mark, to 1 ms.
  thermal.series  1 s bins k = floor((t_ms - t_idle0) / 1000) for k = 0..175 (the recording runs to 184.9 s; the
                  page's time axis ends at 176 s). Per bin, the mean of board_w, sp.minion_w[0], sp.sram_w[0] and
                  sp.noc_w[0] (3 decimals) and of temp_c.minshire[0], temp_c.pmic, die_mv.ddr and die_mv.minion
                  (1 decimal), as keys board, minion, sram, noc, temp, pmic, die_ddr, die_mnn. Means are
                  statistics.mean (exact, so a mean of whole-number readings stays an integer and ties round
                  the same way every time); this reproduces the committed series exactly.
  thermal.gaps    the dips between successive load processes, from the 10 Hz stream: within the matmul and DRAM
                  phases, from 1 s after the mark to the next mark, runs of samples with board power below the
                  midpoint of the phase's median and the median of the 3 s before the mark; each run's time is that
                  of its lowest sample (the first, on a tie), to 0.1 s.
  thermal.fast    the 10 Hz samples at the matmul's start (15-35 s) and stop (73-95 s): t, board_w, the PMIC's own
                  board average (sp.board_avg_w) and the three rails' sum, for the page's remainder panels.
  thermal.loads   what each load process ran, parsed from raw/thermal-loads.log. run_thermal.sh cut the lines at
                  200 and 160 characters, so the per-launch times are not in the file.
  shires          per-shire-voltage-idle.json, copied.
  voltage_repeat  for each later SP trace dump in raw/ (sp2.bin, sp3.bin: the next passes, 0.3 s apart), how many of
                  the map's 102 cells [now, low, high] differ from it and by how much (parse_sptrace_voltage.py).
  mesh            marty1885's shire layout and the four cells without a compute shire, imported from
                  workloads/nocbench/analyze.py (MARTY, EMPTY), so the page never retypes coordinates.
  context         the later measurements the page compares with, copied with their sources: the idle law
                  (dvfs.json leak_model), the rail filter (catalogue.json rail_filter), the minion rail's IR drop
                  (unmetered_fit.json ddr_droop) and the busy drift of the Horace strict runs (report.json), and
                  that drift on each card with its run count, spread and temperatures (busy_drift_cards, recomputed
                  run by run from each card's horace3.json and checked against its leak_w_per_c).

The output is json.dumps with default separators and no final newline, as committed, with the top-level keys in a
fixed order.
"""
import argparse
import json
import os
import re
import statistics
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LAST_BIN = 175
FAST_WINDOWS = [(15.0, 35.0), (73.0, 95.0)]
CONTEXT = {  # later measurements the page sets beside this session's, and where they come from
    "idle_law": ("docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json", lambda d: {
        k: d["leak_model"][k] for k in ("P_fix", "A_at_80", "T_L")}),
    "rail_filter": ("docs/reports/data/2026-09-23-energy-manual/catalogue.json", lambda d: {
        card: {k: v[k] for k in ("frac_1s", "frac_2s", "tau_s", "n")} for card, v in d["rail_filter"].items()}),
    "minion_ir_drop_mv_per_w": ("docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json",
                                lambda d: d["ddr_droop"]["minion_ir_drop_mv_per_w"]),
    "busy_drift_w_per_c": ("docs/reports/data/2026-09-21-horace-aifoundry2/report.json", lambda d: d["leak_w_per_c"]),
}
# The same busy drift on each card, from the strict Horace sessions (tools/ettelem/analyze_horace_strict.py): with its
# run count and spread, so the page can say how well each card pins it down.
DRIFT_SESSIONS = {"aifoundry2": "docs/reports/data/2026-09-21-horace-aifoundry2/horace3.json",
                  "aifoundry3": "docs/reports/data/2026-09-22-horace-aifoundry3/horace3.json"}
KEY_ORDER = ["thermal", "horace", "shires", "horace2", "context", "voltage_repeat", "mesh"]


def load_jsonl(path):
    return [json.loads(l) for l in open(path) if l.startswith("{")]


def series(tel, t0):
    bins = {}
    for r in tel:
        k = int((r["t_ms"] - t0) // 1000)
        if 0 <= k <= LAST_BIN:
            bins.setdefault(k, []).append(r)
    fields = [("board", 3, lambda r: r["board_w"]), ("minion", 3, lambda r: r["sp"]["minion_w"][0]),
              ("sram", 3, lambda r: r["sp"]["sram_w"][0]), ("noc", 3, lambda r: r["sp"]["noc_w"][0]),
              ("temp", 1, lambda r: r["temp_c"]["minshire"][0]), ("pmic", 1, lambda r: r["temp_c"]["pmic"]),
              ("die_ddr", 1, lambda r: r["die_mv"]["ddr"]), ("die_mnn", 1, lambda r: r["die_mv"]["minion"])]
    out = []
    for k in sorted(bins):
        rs = bins[k]
        row = {"t": k}
        for name, dp, f in fields:
            row[name] = round(statistics.mean(f(r) for r in rs), dp)
        out.append(row)
    return out


def gaps(tel, t0, marks):
    t = [(r["t_ms"] - t0) / 1000 for r in tel]
    b = [r["board_w"] for r in tel]
    out = []
    for i, (name, a) in enumerate(marks):
        if name not in ("matmul", "dram"):
            continue
        z = marks[i + 1][1]
        busy = [b[j] for j in range(len(t)) if a <= t[j] < z]
        before = [b[j] for j in range(len(t)) if a - 3 <= t[j] < a]
        thr = (statistics.median(busy) + statistics.median(before)) / 2
        run = []
        for j in range(len(t)):
            inside = a + 1 <= t[j] < z and b[j] < thr
            if inside:
                run.append(j)
            elif run:
                low = min(run, key=lambda q: (b[q], q))
                out.append(round(t[low], 1)); run = []
        if run:
            out.append(round(t[min(run, key=lambda q: (b[q], q))], 1))
    return out


def fast(tel, t0):
    f = {"windows": [list(w) for w in FAST_WINDOWS], "t": [], "board": [], "board_avg": [], "rails": []}
    for r in tel:
        s = (r["t_ms"] - t0) / 1000
        if any(a <= s < z for a, z in FAST_WINDOWS):
            sp = r["sp"]
            f["t"].append(round(s, 3)); f["board"].append(r["board_w"]); f["board_avg"].append(sp["board_avg_w"])
            f["rails"].append(round(sp["minion_w"][0] + sp["sram_w"][0] + sp["noc_w"][0], 3))
    return f


FIELD = re.compile(r'"(\w+)":("[^"]*"|-?[\d.]+(?:e[-+]?\d+)?)(?=[,}])')


def loads(path):
    """Each line is 'MMBENCH {json…' or 'MEMPROBE {json…', cut short; keep the fields that closed before the cut."""
    rows = {"MMBENCH": [], "MEMPROBE": []}
    for line in open(path):
        kind, _, rest = line.strip().partition(" ")
        if kind in rows:
            rows[kind].append({k: json.loads(v) for k, v in FIELD.findall(rest)})
    mm, mp = rows["MMBENCH"], rows["MEMPROBE"]
    same = lambda rs, drop: len({json.dumps({k: v for k, v in r.items() if k not in drop}, sort_keys=True) for r in rs}) == 1
    out = {"source": "raw/thermal-loads.log; run_thermal.sh cut each line at 200 (matmul) or 160 (DRAM) characters, "
                     "so the per-launch times and rates are missing"}
    if mm:
        r = mm[0]
        out["matmul"] = {"processes": len(mm), "launches_per_process": r["launch"] + 1, "mode": r["mode"],
                         "minions": r["minions"], "iters_per_launch": r["iters"], "flop_per_op": r["flop_per_op"],
                         "ops_per_minion": r["ops_per_minion"], "identical": same(mm, ())}
    if mp:
        r = mp[0]
        # memprobe_host --loop times one launch of 2,000 iterations, sets iters to 0.6 s of work at that rate, and
        # launches until --seconds is spent; the line kept is the last launch (numbered from 0).
        out["dram"] = {"processes": len(mp), "launches_per_process": r["launch"] + 1, "name": r["name"],
                       "minions": r["minions"], "iters_per_launch": [x["iters"] for x in mp],
                       "identical_but_iters": same(mp, ("iters",))}
    return out


def voltage_repeat(d, shires):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parse_sptrace_voltage import parse
    out = []
    for name in ("sp2.bin", "sp3.bin"):
        p = os.path.join(d, "raw", name)
        if not os.path.exists(p):
            continue
        v = parse(open(p, "rb").read())
        diff = [abs(a - b) for k in shires for rail in ("mnn", "sram", "noc")
                for j, (a, b) in enumerate(zip(shires[k][rail], v[k][rail])) if a != b]
        out.append({"trace": "raw/" + name, "cells": 3 * len(shires), "differing": len(diff),
                    "max_abs_mv": max(diff, default=0),
                    "low_high_identical": all(shires[k][r][1:] == v[k][r][1:] for k in shires for r in ("mnn", "sram", "noc"))})
    return out


def mesh():
    sys.path.insert(0, os.path.join(ROOT, "workloads", "nocbench"))
    import analyze
    return {"layout": {str(s): list(xy) for s, xy in analyze.MARTY.items()}, "empty_cells": [list(c) for c in analyze.EMPTY],
            "source": "workloads/nocbench/analyze.py (MARTY, EMPTY)"}


def busy_drift(rel):
    """analyze_horace_strict.py's leakage rule, run by run: the least-squares slope of power against the whole-degree
    temperature from 1 s after launch to 0.2 s before the end, in runs that heat the die by 3 C or more; the mean
    over those runs is the file's leak_w_per_c."""
    d = json.load(open(os.path.join(ROOT, rel)))
    lam, lo, hi = [], [], []
    for r in d["runs"]:
        idx = [i for i, g in enumerate(d["grid"]) if 1.0 <= g <= r["dur"] - 0.2]
        T, P = [r["curve_T"][i] for i in idx], [r["curve_P"][i] for i in idx]
        if max(T) - min(T) >= 3:
            mt, mp = statistics.mean(T), statistics.mean(P)
            lam.append(sum((x - mt) * (y - mp) for x, y in zip(T, P)) / sum((x - mt) ** 2 for x in T))
            lo.append(min(T)); hi.append(max(T))
    mean, sd = statistics.mean(lam), statistics.stdev(lam)
    assert abs(mean - d["leak_w_per_c"]) < 1e-6, (rel, mean, d["leak_w_per_c"])
    return {"w_per_c": round(mean, 4), "runs": len(lam), "sd": round(sd, 4), "se": round(sd / len(lam) ** 0.5, 4),
            "temp_c": [min(lo), max(hi)], "source": rel}


def context():
    out = {}
    for key, (rel, get) in CONTEXT.items():
        out[key] = {"value": get(json.load(open(os.path.join(ROOT, rel)))), "source": rel}
    out["busy_drift_cards"] = {card: busy_drift(rel) for card, rel in DRIFT_SESSIONS.items()}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("dir", help="the session's data directory")
    ap.add_argument("--out", required=True, help="summary.json to write (merged if it exists)")
    a = ap.parse_args()
    tel = load_jsonl(os.path.join(a.dir, "thermal-telemetry.jsonl"))
    marks_raw = load_jsonl(os.path.join(a.dir, "thermal-phases.jsonl"))
    t0 = marks_raw[0]["t_ms"]
    phases = [{"phase": p["phase"], "t": round((p["t_ms"] - t0) / 1000, 3)} for p in marks_raw]
    marks = [(p["phase"], (p["t_ms"] - t0) / 1000) for p in marks_raw]
    out = json.load(open(a.out)) if os.path.exists(a.out) else {}
    thermal = {"series": series(tel, t0), "phases": phases, "gaps": gaps(tel, t0, marks), "fast": fast(tel, t0)}
    # run_thermal.sh writes thermal-loads.log next to the telemetry; the 20 September one was recovered into raw/
    lp = next((p for p in (os.path.join(a.dir, "thermal-loads.log"), os.path.join(a.dir, "raw", "thermal-loads.log"))
               if os.path.exists(p)), None)
    if lp:
        thermal["loads"] = loads(lp)
    out["thermal"] = thermal
    out["shires"] = json.load(open(os.path.join(a.dir, "per-shire-voltage-idle.json")))
    out["context"] = context()
    out["voltage_repeat"] = voltage_repeat(a.dir, out["shires"])
    out["mesh"] = mesh()
    # a fixed key order, so the file comes out the same whichever earlier version it is merged into
    out = {k: out[k] for k in KEY_ORDER + [k for k in out if k not in KEY_ORDER] if k in out}
    with open(a.out, "w") as f:
        f.write(json.dumps(out))
    print("wrote %s: %d bins, gaps at %s s" % (a.out, len(thermal["series"]), ", ".join("%.1f" % g for g in thermal["gaps"])))


if __name__ == "__main__":
    main()
