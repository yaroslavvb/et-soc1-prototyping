#!/usr/bin/env python3
"""E207's reducer (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum): the session directory into THE DATA the frozen scorer reads
(score_e207.py's docstring: E206's reducer form, one arm: {"experiment": "E207", "arms": {"A": ARM}}; E207.md section 7), and a table. E206's
reducer (tools/claims-v3/e206/reduce_e206.py, landed in 906699ea, which reduced E206 arm A's session on this card into its committed
data-e206.json) line for line in every reading, for E207's smoke points (b01, b02, b03) and its experiment's name; desk/realbytes_e207.py
reduces E206 arm A's committed session with this code and gets E206's committed data-e206.json back field for field. Python's own modules
only; run at the desk at the collection, on the copied-back session; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e207/reduce_e207.py --arm A=<session dir> --out data-e207.json [--txt reduce-e207.txt]

PER RUN (a run whose one process started; the registration's words, each choice the kit makes marked "kit"):
  the records      the process's stdout through e207_common.host_records with the run's own command line (run.json): runtime lines
                   dropped wherever they fell, a record that does not parse whole or names another command never read (counted)
  counted launches the fma launches with launch >= 0, ok, wall_s >= 0.1 s, passes >= 1 and a kernel clock (cycles_max / wall_s) in 590-610 MHz
                   (the calibration launch -1 and the check launch -3 never count)
  t_gemm_s, n_gemm sum of wall_s / sum of passes over the counted launches; the sum of passes
  cycles_per_op    the median over the counted launches of the host's cycles_per_op (the kernel's counter: its mean over minions / ops; the
                   scorer's "counter's mean")
  cycles_gemm      the median over the counted launches of cycles_max / passes (the slowest minion's counter, a GEMM; the scorer's "wall"
                   is cycles_gemm / ops a minion a GEMM)
  p_work_w         the median board W of the 10 Hz samples whose t_ms falls inside a counted launch [t_start_ms, t_end_ms]
  p_rest_w         the median board W of the samples in the last 5 s before the process started (its 10 s rest read's second half)
  die_start_c      the mean of the shires' mean over those same samples (kit: "the shires' mean then", read as their mean, E190's)
  die_c            the highest shires' mean in the work window (the process's start to its end)
  mhz, mhz_min,    the mean, the lowest and the highest minion clock of the samples inside the counted launches (S6 reads the lowest and
  mhz_max          the highest)
  checks           every check of C the process printed (exact / approx / wrong); a process with none: checks_missing 1 (kit)
  record           {arm, type, minions, shire_mask} of the counted launches (all must agree, else the run is flagged and its record is the
                   first's); block and n from run.json
A run with no counted launch keeps t_gemm_s null with its reason (the scorer skips it). THE SMOKE: every check of C of its three processes,
and each point's cycles an op from its check record (the host's last launch's mean cycles over its ops, the counter's mean, as E190's and
E206's smoke read it), keyed by the point (b01, b02, b03: R0 reads them against MM1-v1's counter-mean forecast). THE TIES: block "tie" runs
(t01) go to "ties" (the scorer's tie reading), never into a point's runs (a point's two runs are its pass 1 and pass 2 runs).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e207_common as C  # noqa: E402


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
            out.append((s.get("t_ms"), s.get("board_w"), C.die_of(s), (s.get("mhz") or {}).get("minion")))
    return sorted([x for x in out if x[0] is not None])


def proc_text(d, name):
    p = os.path.join(d, name)
    if not os.path.exists(p):
        return ""
    with open(p, errors="replace") as f:
        return f.read()


def reduce_run(d, rec, tel):
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
    out = {"run": rec["run"], "n": rec["n"], "block": rec["block"], "id": rec["id"], "n_procs": len(procs), "rcs": [p["rc"] for p in procs],
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
        # E206.md 7: "a run whose host record differs from its point ... is set aside and flagged": the records the host printed for
        # another command are never read as data, but their own fields are passed on, so the scorer sets the run aside and flags it
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
    out["mhz_max"] = max(mz) if mz else None      # fix-e206 (E206.md A1 item 4): S6 reads the highest counted sample
    out["kclock_mhz"] = mean([C.kclock(L) for L in cnt])
    return out


def reduce_arm(sd, arm, smoke_pids=None):
    """The arm's session directory in the scorer's form. smoke_pids: the smoke's points (E207's b01, b02, b03 by default; the real-bytes desk
    test passes E206's p001, p046, p021 to read E206 arm A's committed session through this same code)."""
    tel = load_tel(sd)
    A = {"session": os.path.basename(os.path.normpath(sd)), "n_samples": len(tel), "smoke": {"checks": [], "cycles_per_op": {}},
         "points": {}, "ties": {"runs": []}, "runs_not_started": [], "runs_without_counted_launch": []}
    sm_argv = {}
    for pid in (smoke_pids or C.SMOKE_PIDS):
        d = os.path.join(sd, "smoke", pid)
        sj = os.path.join(d, "smoke.json")
        argv = C.load(sj).get("argv") if os.path.exists(sj) else None
        sm_argv[pid] = argv
        fma, chk, info = C.host_records(proc_text(d, "proc.out"), argv)
        A["smoke"]["checks"] += [x.get("result") for x in chk]
        if chk and chk[-1].get("cycles_per_op"):
            A["smoke"]["cycles_per_op"][pid] = chk[-1]["cycles_per_op"]
    rd = os.path.join(sd, "runs")
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, key, "run.json")
        if not os.path.exists(p):
            continue
        rec = C.load(p)
        if not rec.get("procs"):
            A["runs_not_started"].append({"run": key, "why": rec.get("why")})
            continue
        r = reduce_run(os.path.join(rd, key), rec, tel)
        run = {k: r.get(k) for k in ("t_gemm_s", "cycles_per_op", "cycles_gemm", "n_gemm", "n_launch_counted", "p_work_w", "p_rest_w",
                                     "die_start_c", "die_c", "mhz", "mhz_min", "mhz_max", "checks", "record", "block", "n")}
        run["detail"] = {k: r.get(k) for k in ("run", "rcs", "n_launch", "flags", "checks_missing", "records", "n_rest_samples",
                                               "n_work_samples", "kclock_mhz", "why")}
        if r.get("t_gemm_s") is None:
            A["runs_without_counted_launch"].append({"run": key, "why": r.get("why")})
        if rec["block"] == "tie":
            A["ties"]["runs"].append(run)
        else:
            A["points"].setdefault(rec["id"], {"runs": []})["runs"].append(run)
    q = os.path.join(sd, "queue.json")
    if os.path.exists(q):
        qq = C.load(q)
        A["queue"] = {"stop": qq.get("stop"), "card_min": qq.get("card_min"), "rest_die_c": qq.get("rest_die_c"),
                      "rest_board_w": qq.get("rest_board_w"), "hung": qq.get("hung"), "rc": qq.get("rc"),
                      "not_started": [x for x in qq.get("queue", []) if not x.get("ran")]}
    return A


def table(data):
    L = ["E207 reduced (each run; J over idle = (p_work - p_rest) t_gemm, J with the card at rest = p_work t_gemm, the scorer's form)"]
    for arm, A in data["arms"].items():
        L.append(f"arm {arm} ({A.get('session')}): {A.get('n_samples')} samples; smoke checks {A['smoke']['checks']}, cycles an op "
                 f"{ {k: round(v, 1) for k, v in A['smoke']['cycles_per_op'].items()} }; queue stop {A.get('queue', {}).get('stop')}")
        rows = [(r["n"], pid, r) for pid, P in A["points"].items() for r in P["runs"]] + [(r["n"], "tie", r) for r in A["ties"]["runs"]]
        for n, pid, r in sorted(rows, key=lambda x: x[0] or 0):
            if r.get("t_gemm_s"):
                jo = (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] if r.get("p_rest_w") is not None and r.get("p_work_w") is not None else None
                jr = r["p_work_w"] * r["t_gemm_s"] if r.get("p_work_w") is not None else None
                L.append(f"  {n:3d} {r.get('block'):5s} {pid:4s} t {r['t_gemm_s']:.6g} s over {r['n_gemm']} GEMMs; cycles an op "
                         f"{r.get('cycles_per_op')}; work {r['p_work_w']} W, rest {r['p_rest_w']} W; J over idle "
                         f"{jo if jo is None else round(jo, 6)}, at rest {jr if jr is None else round(jr, 6)}; die {r.get('die_start_c')} -> "
                         f"{r.get('die_c')} C; {r['mhz']:.0f} MHz (min {r['mhz_min']}, max {r.get('mhz_max')}); checks {sorted(set(map(str, r['checks'])))}")
            else:
                L.append(f"  {n:3d} {r.get('block'):5s} {pid:4s} NO COUNTED LAUNCH ({r['detail'].get('why')})")
        for x in A.get("runs_not_started", []):
            L.append(f"  not started: {x['run']} ({x['why']})")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[], help="A=<session dir> (E207's one arm)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    data = {"experiment": "E207", "reducer": "tools/claims-v3/e207/reduce_e207.py", "arms": {}}
    for spec in a.arm:
        arm, sd = spec.split("=", 1)
        if arm != "A" or not os.path.isdir(sd):
            print(f"refused: --arm {spec}")
            return 2
        data["arms"][arm] = reduce_arm(sd, arm)
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
