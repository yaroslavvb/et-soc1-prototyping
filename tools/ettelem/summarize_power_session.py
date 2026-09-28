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
                  (dvfs.json leak_model, with fit_T, the whole-degree readings of its idle fit), the rail filter
                  (catalogue.json rail_filter), the minion rail's IR drop (unmetered_fit.json ddr_droop) and the busy
                  drift of the Horace strict runs (report.json), and that drift on each card with its run count,
                  spread and temperatures (busy_drift_cards, recomputed run by run from each card's horace3.json and
                  checked against its leak_w_per_c; each: the per-run slopes), and the same load step's busy slope on
                  every card of the version-3 claims check (busy_drift_loadstep_v3: V3-MMB item MMB-T/P1, four repeats
                  of this session's load step per card on 26 September 2026, fitted from 5 s after launch by
                  tools/claims-v3/mmb/x1_reduce.py; read from LOADSTEP_V3 when that file exists).
  tel_v3          the version-3 claims check's V3-TEL, when TEL_V3 exists (27 September 2026): sp_pass, the service
                  processor's pass in ms under each way of polling the card, per card and pass (sp_pass_v3); vmaps,
                  the DEBUG block's per-shire voltage maps at idle and under load for the passes of item TEL-Q's Q4
                  test, with that test's figures recomputed from the maps and checked against tel.json (vmaps_v3).

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
    # the law's constants, and the whole-degree die readings its idle fit used (idle_curve T), so the page can say
    # over which temperatures the data pin it
    "idle_law": ("docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json", lambda d: dict(
        {k: d["leak_model"][k] for k in ("P_fix", "A_at_80", "T_L")},
        fit_T=[b["T"] for b in d["leak_model"]["idle_curve"]])),
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
# The version-3 claims check (docs/reports/data/2026-09-25-claims-v3) repeated this session's load step four times on
# each of three cards; its reduced results give each repeat's busy slope (MMB-T/P1). Added 26 September 2026.
LOADSTEP_V3 = "docs/reports/data/2026-09-25-claims-v3/results/mmb.json"
# Its meter and voltage-map tests (V3-TEL, tools/claims-v3/tel/reduce.py): the service processor's pass under each way
# of polling the card (tel.json passes.<card>[].sp), and the per-shire voltage maps of the DEBUG block
# (raw/<card>/tel/p<N>/dbg/x2-idle.bin and x2-load.bin, read with parse_sptrace_voltage.py as the reducer reads them).
# Added 27 September 2026.
TEL_V3 = "docs/reports/data/2026-09-25-claims-v3/results/tel.json"
TEL_V3_RAW = "docs/reports/data/2026-09-25-claims-v3/raw"
SP_ARMS = ["Q", "PWR", "L10", "VOLT", "E10", "E20", "E40"]  # the order of the check's arms, lightest first
# what each arm ran (PLAN3.md, V3-TEL "Order"), and the interval it asked at, ms (None: no fixed interval)
SP_ARM_WHAT = {"Q": ("nothing polling", None), "PWR": ("one power command every ~16 ms", 16),
               "L10": ("one power command every 100 ms", 100), "VOLT": ("the voltage command, in a loop", None),
               "E10": ("ettelem every 100 ms (10 Hz)", 100), "E20": ("ettelem every 50 ms (20 Hz)", 50),
               "E40": ("ettelem every 25 ms (40 Hz)", 25)}
KEY_ORDER = ["thermal", "horace", "shires", "horace2", "context", "voltage_repeat", "mesh", "tel_v3"]


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
            "temp_c": [min(lo), max(hi)], "each": [round(x, 4) for x in lam], "source": rel}


def loadstep_v3(rel):
    """The load step's busy slope per card in the version-3 claims check: MMB-T/P1's per-repeat board slopes (W/C,
    least squares from 5 s after the matmul's launch, x1_reduce.py) and each repeat's die range, with the same summary
    fields as busy_drift (mean, sd, standard error of the mean, run count, temperatures) and the item's 99% interval.
    tested: whether the card's slope was tested against a registered band (aifoundry2, aifoundry3) or only reported."""
    d = json.load(open(os.path.join(ROOT, rel)))
    it = next(i for i in d["items"] if i["item"] == "MMB-T/P1")
    out = {}
    for card, v in it["per_card"].items():
        xs, T = v["values"], v["busy_T_range"]
        mean, sd = statistics.mean(xs), statistics.stdev(xs)
        assert abs(mean - v["mean"]) < 1e-3 and abs(sd - v["sd"]) < 1e-3, (card, mean, v["mean"], sd, v["sd"])
        out[card] = {"w_per_c": round(mean, 4), "runs": len(xs), "sd": round(sd, 4), "se": round(sd / len(xs) ** 0.5, 4),
                     "temp_c": [min(t[0] for t in T), max(t[1] for t in T)], "each": xs, "each_temp_c": T,
                     "ci99": v["ci99"], "tested": v.get("holds") is not None, "source": rel + " MMB-T/P1"}
    return out


def sp_pass_v3(tel):
    """V3-TEL's service-processor pass, ms, per card and pass: the median interval of the SP's own stats records in each
    arm of the pass (tel.json passes.<card>[].sp; reduce.py sp_pass_values), with the record count behind it. Q: quiet
    segments, nothing polling; PWR: et-power-log's single power command, one per ~16 ms; L10: one power command per
    0.1 s; VOLT: a loop of the module-voltage command; E10, E20, E40: ettelem sampling every 100, 50 and 25 ms."""
    out = {}
    for card in tel["cards"]["all"]:
        rows = []
        for p in tel["passes"].get(card, []):
            sp = p["sp"]
            rows.append({"pass": p["pass"], "ms": {a: sp.get(a) for a in SP_ARMS},
                         "n": {a: sp.get("Q_n") if a == "Q" else sp["seg"].get(a, {}).get("n") for a in SP_ARMS}})
        if rows:
            out[card] = rows
    return {"arms": [{"key": a, "what": SP_ARM_WHAT[a][0], "ask_ms": SP_ARM_WHAT[a][1]} for a in SP_ARMS], "cards": out}


def vmaps_v3(tel):
    """V3-TEL's per-shire voltage maps at idle and under a 7 s random-data burst, for each card's passes that entered
    item TEL-Q's Q4 test (both dumps hold all 34 shires, the launch at 600 MHz): each map as parse_sptrace_voltage.py
    reads the dump ({shire: {mnn, sram, noc: [now, low, high]}} mV), whether the dump held one whole pass, and the
    item's Q4 figures for the pass, recomputed here from the maps' minion 'now' readings (each shire's deviation from
    the 34-shire mean under load less the same at idle: its sd and largest magnitude; the load mean less the idle mean)
    and checked against tel.json. Also each card's 99% upper bound on that sd and the registered tolerance, 0.5 mV."""
    import io
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parse_sptrace_voltage import parse
    item = next(i for i in tel["items"] if i["item"] == "TEL-Q")
    shires = [str(s) for s in range(34)]
    out = {}
    for card in tel["cards"]["all"]:
        pc = item["per_card"].get(card) or {}
        rows = []
        for pr in pc.get("passes", []):
            q4 = pr.get("Q4") or {}
            if "sd_dev_change_mv" not in q4:
                continue
            d = os.path.join(ROOT, TEL_V3_RAW, card, "tel", "p%d" % pr["pass"], "dbg")
            caps = {}
            for key, name in (("idle", "x2-idle"), ("load", "x2-load")):
                err = io.StringIO()
                m = parse(open(os.path.join(d, name + ".bin"), "rb").read(), warn=err)
                caps[key] = {"whole_pass": "no pass has all" not in err.getvalue() and len(m) == 34,
                             "map": {s: m[s] for s in shires}}
            iv = [caps["idle"]["map"][s]["mnn"][0] for s in shires]
            lv = [caps["load"]["map"][s]["mnn"][0] for s in shires]
            mi, ml = statistics.mean(iv), statistics.mean(lv)
            dd = [(b - ml) - (a - mi) for a, b in zip(iv, lv)]
            got = {"common_shift_mv": ml - mi, "sd_dev_change_mv": statistics.stdev(dd),
                   "max_abs_dev_change_mv": max(abs(x) for x in dd)}
            for k, v in got.items():
                assert abs(v - q4[k]) < 0.006, (card, pr["pass"], k, v, q4[k])
            rows.append(dict(caps, **{"pass": pr["pass"], "q4": {k: q4[k] for k in got}}))
        if rows:
            out[card] = {"passes": rows, "q4_sd_99_upper_mv": pc.get("Q4_sd_99_upper_mv"),
                         "status": pc.get("status")}
    return {"cards": out, "tolerance_mv": 0.5,
            "test": "TEL-Q Q4: the 99% upper bound of the pass-level sd of each shire's deviation change, idle to load, "
                    "at most 0.5 mV if each monitor carries a fixed offset"}


def tel_v3():
    tel = json.load(open(os.path.join(ROOT, TEL_V3)))
    return {"sp_pass": sp_pass_v3(tel), "vmaps": vmaps_v3(tel),
            "source": TEL_V3 + " (passes.<card>[].sp; items TEL-Q) and " + TEL_V3_RAW + "/<card>/tel/p<N>/dbg/x2-idle.bin, x2-load.bin"}


def context():
    out = {}
    for key, (rel, get) in CONTEXT.items():
        out[key] = {"value": get(json.load(open(os.path.join(ROOT, rel)))), "source": rel}
    out["busy_drift_cards"] = {card: busy_drift(rel) for card, rel in DRIFT_SESSIONS.items()}
    if os.path.exists(os.path.join(ROOT, LOADSTEP_V3)):
        out["busy_drift_loadstep_v3"] = loadstep_v3(LOADSTEP_V3)
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
    if os.path.exists(os.path.join(ROOT, TEL_V3)):
        out["tel_v3"] = tel_v3()
    # a fixed key order, so the file comes out the same whichever earlier version it is merged into
    out = {k: out[k] for k in KEY_ORDER + [k for k in out if k not in KEY_ORDER] if k in out}
    with open(a.out, "w") as f:
        f.write(json.dumps(out))
    print("wrote %s: %d bins, gaps at %s s" % (a.out, len(thermal["series"]), ", ".join("%.1f" % g for g in thermal["gaps"])))


if __name__ == "__main__":
    main()
