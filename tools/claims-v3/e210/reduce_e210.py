#!/usr/bin/env python3
"""E210's reducer (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum): the session directory into THE DATA the frozen scorer reads
(score_e210.py's docstring: {"experiment": "E210", "runs": {"<run id of points-e210.json>": RUN, ...}} plus the smoke's and the probe's checks,
which its R0 reads), and a table. Every per-run reading is E206's reducer's (tools/claims-v3/e206/reduce_e206.py, landed in 906699ea, which
reduced E206 arm A's session on this card into its committed data-e206.json) line for line; desk/realbytes_e210.py reduces E206 arm A's
committed runs with this code's reduce_run and gets E206's committed per-run fields back. Python's own modules only; run at the desk at the
collection, on the copied-back session; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e210/reduce_e210.py --arm A=<session dir> --out data-e210.json [--txt reduce-e210.txt]

PER RUN (a run whose one process started; the registration's words, each choice the kit makes marked "kit"):
  ran              true when the run's one host process started (kit: a run the gate, the cap, the probe or a stop kept from starting is
                   "ran": false with its reason, and the scorer reads it as not run)
  case, role, pass, n   from run.json (the registered run of points-e210.json)
  the records      the process's stdout through e210_common.host_records with the run's own command line (run.json): runtime lines
                   dropped wherever they fell, a record that does not parse whole or names another command never read (counted)
  counted launches the fma launches with launch >= 0, ok, wall_s >= 0.1 s, passes >= 1 and a kernel clock (cycles_max / wall_s) in 590-610 MHz
                   (the calibration launch -1 and the check launch -3 never count)
  t_gemm_s, n_gemm sum of wall_s / sum of passes over the counted launches; the sum of passes
  cycles_per_op    the median over the counted launches of the host's cycles_per_op (the kernel's counter: its mean over minions / ops)
  cycles_gemm      the median over the counted launches of cycles_max / passes (the slowest minion's counter, a GEMM; reported)
  p_work_w         the median board W of the 10 Hz samples whose t_ms falls inside a counted launch [t_start_ms, t_end_ms]
  p_rest_w         the median board W of the samples in the last 5 s before the process started (its 10 s rest read's second half)
  die_start_c      the mean of the shires' mean over those same samples (kit: E190's and E206's reading)
  die_c            the highest shires' mean in the work window (the process's start to its end)
  mhz, mhz_min,    the mean, the lowest and the highest minion clock of the samples inside the counted launches (the scorer's clock band
  mhz_max          reads the lowest and the highest)
  checks           every check of C the process printed (exact / approx / wrong); a process that printed none has checks [] (kit; the
                   frozen scorer's R0 reads a run with no check as not good) and checks_missing 1
  record           {arm, type, minions, shire_mask} of the counted launches (all must agree, else the run is flagged and its record is the
                   first's); a host whose records name another command: the first such record passed on, so the scorer sets the run aside
A run with no counted launch keeps t_gemm_s null with its reason (the scorer reads it as incomplete). A QUIET SAMPLER (fix-e210, before any
datum; verify-e210's finding 2; E210.md amendment A1 item 6): a run with counted launches but no telemetry sample inside them carries no mhz,
mhz_min or mhz_max key at all (the clock was not read) and p_work_w null, with the flag "no telemetry sample inside the counted launches"; the
frozen scorer sets it aside (its clock not read), and the table prints it without crashing. A sample's board W, die or clock that is not a
finite number is read as no reading (never NaN into a median). THE SMOKE: per case that started,
every check of C of its process and its cycles an op from its check record (the counter's mean, read against E206's at the shape); THE PROBE:
its process's checks, verdict, board and die maxima, if its process started (R0 reads its checks), and "probe_reading" always (the verdict
and its reason, also when no probe process started). A case the probe took out keeps its runs as "ran": false, the probe's reason named.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e210_common as C  # noqa: E402


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def load_tel(sd):
    p = os.path.join(sd, "telemetry.jsonl.gz")
    out = []
    if not os.path.exists(p):
        return out
    with gzip.open(p, "rt") as f:
        for ln in f:
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(s, dict):
                continue
            mz = s.get("mhz")
            out.append((s.get("t_ms"), fin(s.get("board_w")), fin(C.die_of(s)), fin(mz.get("minion") if isinstance(mz, dict) else None)))
    return sorted([x for x in out if x[0] is not None])


def fin(x):
    """fix-e210 (A1 item 6): a reading is a finite number, else None (a NaN or a string never reaches a median)."""
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) else None


def proc_text(d, name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return ""
    with open(p, errors="replace") as f:
        return f.read()


def reduce_run(d, rec, tel):
    """One run's readings (E206's reduce_run, line for line; the run's identifying fields read from rec)."""
    procs = rec.get("procs") or []
    launches, checks, missing, info_all = [], [], 0, {"runtime_lines": 0, "unparsed": 0, "mismatched": 0}
    for p in procs:
        fma, chk, info = C.host_records(proc_text(d, p["name"] + ".out"), p.get("argv"))
        launches += fma
        checks += [x.get("result") for x in chk]
        missing += 0 if chk else 1
        info_all["runtime_lines"] += len(info["runtime_lines"])
        info_all["unparsed"] += info["unparsed"]
        info_all["mismatched"] += len(info["mismatched"])
    cnt = [L for L in launches if C.counted(L)]
    out = {"run": rec.get("run"), "n": rec.get("n"), "n_procs": len(procs), "rcs": [p["rc"] for p in procs],
           "n_launch": len(launches), "n_launch_counted": len(cnt), "flags": rec.get("flags", []), "checks": checks,
           "checks_missing": missing, "records": info_all}
    if procs:
        t_first = procs[0]["t0_ms"]
        w0, w1 = procs[0]["t0_ms"], procs[-1]["t1_ms"]
        rest = [x for x in tel if t_first - C.REST_WINDOW_S * 1000 <= x[0] < t_first]
        rb = [x[1] for x in rest if x[1] is not None]
        out["p_rest_w"] = statistics.median(rb) if rb else None
        out["die_start_c"] = mean([x[2] for x in rest])
        out["n_rest_samples"] = len(rest)
        work = [x for x in tel if w0 <= x[0] <= w1]
        out["die_c"] = max([x[2] for x in work if x[2] is not None], default=None)
    recs = sorted({json.dumps({"arm": L.get("arm"), "type": L.get("type"), "minions": L.get("minions"), "shire_mask": L.get("shire_mask")},
                              sort_keys=True) for L in cnt})
    if recs:
        out["record"] = json.loads(recs[0])
        if len(recs) > 1:
            out["flags"] = out["flags"] + [f"the counted launches name {len(recs)} different records (the first kept)"]
    elif info_all["mismatched"]:
        # the records the host printed for another command are never read as data, but their own fields are passed on, so the scorer
        # sets the run aside (its record is not the case's) and the block is incomplete
        other = []
        for p in procs:
            f_all, _, _ = C.host_records(proc_text(d, p["name"] + ".out"), None)
            other += [L for L in f_all if C.counted(L)]
        if other:
            L0 = other[0]
            out["record"] = {"arm": L0.get("arm"), "type": L0.get("type"), "minions": L0.get("minions"), "shire_mask": L0.get("shire_mask")}
            out["flags"] = out["flags"] + ["the host's records name another command than the run's (not read as data; the record passed on "
                                           "for the scorer to set the run aside)"]
    if not cnt:
        out.update({"t_gemm_s": None, "n_gemm": 0, "p_work_w": None, "mhz": None, "mhz_min": None, "mhz_max": None, "cycles_per_op": None,
                    "cycles_gemm": None,
                    "why": "no counted launch (none in the clock band, or none ok)" if launches else "no launch read"})
        return out
    out["t_gemm_s"] = sum(L["wall_s"] for L in cnt) / sum(L["passes"] for L in cnt)
    out["n_gemm"] = sum(L["passes"] for L in cnt)
    out["cycles_per_op"] = statistics.median([L["cycles_per_op"] for L in cnt if L.get("cycles_per_op") is not None]) \
        if any(L.get("cycles_per_op") is not None for L in cnt) else None
    out["cycles_gemm"] = statistics.median([L["cycles_max"] / L["passes"] for L in cnt])
    inside = [x for x in tel if any(L["t_start_ms"] <= x[0] <= L["t_end_ms"] for L in cnt)]
    bw = [x[1] for x in inside if x[1] is not None]
    mz = [x[3] for x in inside if x[3] is not None]
    out["p_work_w"] = statistics.median(bw) if bw else None
    out["n_work_samples"] = len(bw)
    out["mhz"] = mean(mz)
    out["mhz_min"] = min(mz) if mz else None
    out["mhz_max"] = max(mz) if mz else None
    out["kclock_mhz"] = mean([C.kclock(L) for L in cnt])
    return out


RUN_KEYS = ("t_gemm_s", "cycles_per_op", "cycles_gemm", "n_gemm", "n_launch_counted", "p_work_w", "p_rest_w", "die_start_c", "die_c", "mhz",
            "mhz_min", "mhz_max", "checks", "record")


def reduce_session(sd):
    """The session directory in the scorer's form."""
    tel = load_tel(sd)
    pts = C.points()
    reg = {r["run"]: r for r in pts["runs"]}
    data = {"experiment": "E210", "reducer": "tools/claims-v3/e210/reduce_e210.py", "session": os.path.basename(os.path.normpath(sd)),
            "n_samples": len(tel), "runs": {}, "smoke": {}, "probe": {}, "probe_reading": None, "dropped": {},
            "runs_not_started": [], "runs_without_counted_launch": [], "runs_without_a_sample_inside": []}
    for case in C.SMOKE_CASES:
        d = os.path.join(sd, "smoke", case.replace("@", "-"))
        sj = os.path.join(d, "smoke.json")
        if not os.path.exists(sj):
            continue
        sm = C.load(sj)
        fma, chk, info = C.host_records(proc_text(d, "proc.out"), sm.get("argv"))
        data["smoke"][case] = {"checks": [x.get("result") for x in chk], "cycles_per_op": chk[-1].get("cycles_per_op") if chk else None,
                               "rc": sm.get("rc"), "n_launch": len(fma), "good": sm.get("good"), "cycles_ref": sm.get("cycles_ref"),
                               "cycles_ratio": sm.get("cycles_ratio")}
    pj = os.path.join(sd, "probe", C.PROBE_CASE.replace("@", "-"), "probe.json")
    if os.path.exists(pj):
        pr = C.load(pj)
        data["probe_reading"] = {k: pr.get(k) for k in ("case", "verdict", "why", "board_max_w", "die_max_c", "samples", "gate", "rule",
                                                        "window_ms", "latch_low_c")}
        if pr.get("proc"):
            d = os.path.dirname(pj)
            fma, chk, info = C.host_records(proc_text(d, "proc.out"), pr["proc"].get("argv"))
            data["probe"][C.PROBE_CASE] = {"checks": [x.get("result") for x in chk], "verdict": pr.get("verdict"), "rc": pr["proc"].get("rc"),
                                           "n_launch": len(fma), "board_max_w": pr.get("board_max_w"), "die_max_c": pr.get("die_max_c")}
    rd = os.path.join(sd, "runs")
    seen = set()
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, key, "run.json")
        if not os.path.exists(p) or key not in reg:
            continue
        rec = C.load(p)
        seen.add(key)
        if not rec.get("procs"):
            data["runs"][key] = {"ran": False, "case": reg[key]["case"], "why": rec.get("why")}
            data["runs_not_started"].append({"run": key, "why": rec.get("why")})
            continue
        r = reduce_run(os.path.join(rd, key), rec, tel)
        run = {"ran": True, "case": reg[key]["case"], "role": reg[key]["role"], "pass": reg[key]["pass"], "n": reg[key]["n"]}
        run.update({k: r.get(k) for k in RUN_KEYS})
        quiet = bool(r.get("n_launch_counted")) and r.get("mhz_min") is None
        if quiet:      # fix-e210 (A1 item 6): no telemetry sample inside the counted launches: the clock keys are omitted, so the scorer sets the run aside
            for k in ("mhz", "mhz_min", "mhz_max"):
                run.pop(k, None)
        run["detail"] = {k: r.get(k) for k in ("run", "rcs", "n_launch", "flags", "checks_missing", "records", "n_rest_samples",
                                               "n_work_samples", "kclock_mhz", "why")}
        if quiet:
            run["detail"]["flags"] = list(run["detail"].get("flags") or []) + [
                "no telemetry sample inside the counted launches: the clock and the work power not read (the scorer sets the run aside)"]
            data["runs_without_a_sample_inside"].append(key)
        if r.get("t_gemm_s") is None:
            data["runs_without_counted_launch"].append({"run": key, "why": r.get("why")})
        data["runs"][key] = run
    q = os.path.join(sd, "queue.json")
    if os.path.exists(q):
        qq = C.load(q)
        data["dropped"] = qq.get("dropped") or {}
        for x in qq.get("queue", []):
            k = x.get("run")
            if k in reg and k not in seen and not x.get("ran"):
                data["runs"][k] = {"ran": False, "case": reg[k]["case"], "why": x.get("why")}
                data["runs_not_started"].append({"run": k, "why": x.get("why")})
        data["queue"] = {"stop": qq.get("stop"), "card_min": qq.get("card_min"), "rest_die_c": qq.get("rest_die_c"),
                         "rest_board_w": qq.get("rest_board_w"), "hung": qq.get("hung"), "rc": qq.get("rc"),
                         "n_queue": len(qq.get("queue", [])), "sequence": qq.get("sequence")}
        if data["probe_reading"] is None and qq.get("probe"):
            data["probe_reading"] = {k: qq["probe"].get(k) for k in ("case", "verdict", "why", "board_max_w", "die_max_c", "samples", "gate")}
    data["runs_not_started"].sort(key=lambda x: x["run"])
    return data


def table(data):
    L = ["E210 reduced (each run; J over idle = (p_work - p_rest) t_gemm, the scorer's form)",
         f"session {data.get('session')}: {data.get('n_samples')} samples; smoke "
         f"{ {k: (v['checks'], v['cycles_per_op']) for k, v in data['smoke'].items()} }; probe {data.get('probe_reading')}; "
         f"queue stop {data.get('queue', {}).get('stop')}"]
    for key in sorted(data["runs"], key=lambda k: int(k.split("-")[0])):
        r = data["runs"][key]
        if not r.get("ran"):
            L.append(f"  {key:24s} NOT STARTED ({r.get('why')})")
        elif r.get("t_gemm_s"):
            jo = (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] if r.get("p_rest_w") is not None and r.get("p_work_w") is not None else None
            mzs = (f"{r['mhz']:.0f} MHz (min {r.get('mhz_min')}, max {r.get('mhz_max')})" if isinstance(r.get("mhz"), (int, float))
                   else "the clock not read (no telemetry sample inside the counted launches)")      # fix-e210: None-safe (verify-e210 V6)
            L.append(f"  {key:24s} t {r['t_gemm_s']:.6g} s over {r.get('n_gemm')} GEMMs; cycles an op {r.get('cycles_per_op')}; work {r.get('p_work_w')} W, "
                     f"rest {r.get('p_rest_w')} W; J over idle {jo if jo is None else round(jo, 9)}; die {r.get('die_start_c')} -> {r.get('die_c')} C; "
                     f"{mzs}; checks {sorted(set(map(str, r.get('checks') or [])))}")
        else:
            L.append(f"  {key:24s} NO COUNTED LAUNCH ({r['detail'].get('why')})")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[], help="A=<session dir> (E210's one arm)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    if len(a.arm) != 1:
        print("refused: one --arm A=<session dir>")
        return 2
    arm, sd = a.arm[0].split("=", 1)
    if arm != "A" or not os.path.isdir(sd):
        print(f"refused: --arm {a.arm[0]}")
        return 2
    data = reduce_session(sd)
    with open(a.out, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    t = table(data)
    if a.txt:
        with open(a.txt, "w") as f:
            f.write(t)
    sys.stdout.write(t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
