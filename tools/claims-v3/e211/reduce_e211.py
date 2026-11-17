#!/usr/bin/env python3
"""E211's reducer (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the session directory into THE DATA the frozen scorer reads
(score_e211.py's docstring: {"experiment": "E211", "arms": {"A": {"smoke": {"runs": [RUN, ...]}, "runs": [RUN, ...]}}}; E211.md section 7),
and a table. Every reading of a run is E206's reducer's (tools/claims-v3/e206/reduce_e206.py, landed in 906699ea, which reduced E206 arm A's
session on this card into its committed data-e206.json), line for line; desk/realbytes_e211.py reduces E206 arm A's committed session's runs
with reduce_run and gets E206's committed data-e206.json run fields back. E211 adds two fields to a run, as the scorer's form names them: "walk"
(rgm211's host's walk check) and "gate" (the identity gate's words for the process), and keys each run by its point and pair. Python's own
modules only; run at the desk at the collection, on the copied-back session; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e211/reduce_e211.py --arm A=<session dir> --out data-e211.json [--txt reduce-e211.txt]

PER RUN (a run whose one process started, or whose process the identity gate refused; the registration's words, each choice the kit makes
marked "kit"):
  the records      the process's stdout through e211_common.host_records with the run's own command line (run.json): runtime lines
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
  checks           every check of C the process printed (exact / approx / wrong); a process with none: checks_missing 1 (kit); a process
                   the identity gate refused: no check ([]), so the scorer's R0 reads it
  record           {arm, type, minions, shire_mask} of the counted launches (all must agree, else the run is flagged and its record is the
                   first's); block, n from run.json; the point from run.json, the pair from points-e211.json's order at the run's
                   place n (family C's twin runs belong to c01 and c02, the C block's pairs)
  walk             rgm211's host (gemmLn, gemmLnc): {"names": the walk of every counted launch, "ok": walk_ok of every counted launch,
                   "launches_bad": the last check record's walk_launches_bad}; rgm136's host (gemmL): null (it prints no walk)
  gate             the identity gate's words the runner recorded for the process ("GATE OK: ..." or "GATE FAILED: ...")
A run with no counted launch keeps t_gemm_s null with its reason (the scorer skips it). THE SMOKE: one RUN per smoke point (s01, s02, s03,
block "smoke", n 1-3) by the same readings over its 2 s process (the 5 s before it its rest: the end of the 30 s rest reading for s01, the
previous process's tail for the others; kit), plus "check_cycles_per_op", the check record's cycles an op (the runner's smoke gate's reading,
E206's), REPORTED beside: R0 reads cycles_per_op (the median over its counted launches), as the scorer's form says.
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
import e211_common as C  # noqa: E402


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
    """E206's per-run readings (reduce_e206.reduce_run, line for line) over the run's processes, plus the counted launches' walk fields and the
    last check record's walk_launches_bad (read by reduce_arm for rgm211's host)."""
    procs = rec.get("procs") or []
    launches, checks, missing, info_all = [], [], 0, {"runtime_lines": 0, "unparsed": 0, "mismatched": 0}
    last_chk = {}
    for p in procs:
        fma, chk, info = C.host_records(proc_text(d, p["name"] + ".out"), p.get("argv"))
        launches += fma
        checks += [x.get("result") for x in chk]
        missing += 0 if chk else 1
        if chk:
            last_chk = chk[-1]
        info_all["runtime_lines"] += len(info["runtime_lines"])
        info_all["unparsed"] += info["unparsed"]
        info_all["mismatched"] += len(info["mismatched"])
    cnt = [L for L in launches if C.counted(L)]
    out = {"run": rec["run"], "n": rec["n"], "block": rec["block"], "id": rec["id"], "n_procs": len(procs), "rcs": [p["rc"] for p in procs],
           "n_launch": len(launches), "n_launch_counted": len(cnt), "flags": rec.get("flags", []), "checks": checks,
           "checks_missing": missing, "records": info_all,
           "walk_names": [L.get("walk") for L in cnt], "walk_ok": [L.get("walk_ok") for L in cnt],
           "walk_launches_bad": last_chk.get("walk_launches_bad"), "check_cycles_per_op": last_chk.get("cycles_per_op")}
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
        # E206.md 7 (E211.md 7 the same): "a run whose host record differs from its point ... is set aside and flagged": the records the host
        # printed for another command are never read as data, but their own fields are passed on, so the scorer sets the run aside and flags it
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


SCORER_KEYS = ("point", "block", "pair", "n", "t_gemm_s", "cycles_per_op", "cycles_gemm", "p_work_w", "p_rest_w", "die_start_c", "mhz_min",
               "mhz_max", "checks", "record", "walk", "gate")


def order_pair(n, pid):
    """The run's pair as the registered order gives it at its place n (a twin run in family C's block belongs to that block's pair, c01 or
    c02, not to its point's W pair); a point's own pair if n is not in the order (never on the card day)."""
    for x in C.points()["order"]:
        if x["n"] == n and x["point"] == pid:
            return x["pair"]
    return C.point(pid)["pair"]


def scorer_run(pid, r, gate_words):
    """One run in the frozen scorer's form (its docstring's RUN), with the reducer's other readings under "detail"."""
    p = C.point(pid)
    walk = None
    if p["host"] == "rgm211":
        walk = {"names": r.get("walk_names") or [], "ok": r.get("walk_ok") or [], "launches_bad": r.get("walk_launches_bad")}
    run = {"point": pid, "block": r.get("block"), "pair": order_pair(r.get("n"), pid), "n": r.get("n"), "walk": walk, "gate": gate_words}
    for k in ("t_gemm_s", "cycles_per_op", "cycles_gemm", "p_work_w", "p_rest_w", "die_start_c", "mhz_min", "mhz_max", "checks", "record"):
        run[k] = r.get(k)
    run["checks"] = run["checks"] or []
    run["detail"] = {k: r.get(k) for k in ("run", "rcs", "n_launch", "n_launch_counted", "n_gemm", "flags", "checks_missing", "records",
                                           "n_rest_samples", "n_work_samples", "kclock_mhz", "mhz", "die_c", "check_cycles_per_op", "why")}
    return run


def gate_refused_run(pid, n, block, words, why):
    """A run (or smoke process) whose process the identity gate refused: no record, no check; its gate words, so R0 reads the failure."""
    p = C.point(pid)
    return {"point": pid, "block": block, "pair": order_pair(n, pid), "n": n, "t_gemm_s": None, "cycles_per_op": None, "cycles_gemm": None,
            "p_work_w": None, "p_rest_w": None, "die_start_c": None, "mhz_min": None, "mhz_max": None, "checks": [], "record": None,
            "walk": None if p["host"] != "rgm211" else {"names": [], "ok": [], "launches_bad": None}, "gate": words,
            "detail": {"why": why, "process_started": False}}


def reduce_arm(sd, arm):
    """The arm's session directory in the scorer's form."""
    tel = load_tel(sd)
    order = {x["point"]: x["n"] for x in C.points()["order"] if x["block"] == "smoke"}
    A = {"session": os.path.basename(os.path.normpath(sd)), "n_samples": len(tel), "smoke": {"runs": []}, "runs": [],
         "runs_not_started": [], "runs_without_counted_launch": []}
    for pid in C.SMOKE_PIDS:
        d = os.path.join(sd, "smoke", pid)
        sj = os.path.join(d, "smoke.json")
        if not os.path.exists(sj):
            continue
        sm = C.load(sj)
        if sm.get("ran") is False or not os.path.exists(os.path.join(d, "proc.out")):
            A["smoke"]["runs"].append(gate_refused_run(pid, order[pid], "smoke", sm.get("gate"), "the identity gate refused the smoke's process"))
            continue
        rec = {"run": f"smoke-{pid}", "n": order[pid], "block": "smoke", "id": pid, "flags": [],
               "procs": [{"name": "proc", "argv": sm.get("argv"), "rc": sm.get("rc"), "t0_ms": sm.get("t0_ms"), "t1_ms": sm.get("t1_ms")}]}
        r = reduce_run(d, rec, tel)
        run = scorer_run(pid, r, sm.get("gate"))
        run["check_cycles_per_op"] = r.get("check_cycles_per_op")
        A["smoke"]["runs"].append(run)
    rd = os.path.join(sd, "runs")
    for key in sorted(os.listdir(rd)) if os.path.isdir(rd) else []:
        p = os.path.join(rd, key, "run.json")
        if not os.path.exists(p):
            continue
        rec = C.load(p)
        if not rec.get("procs"):
            if str(rec.get("gate_words", "")).startswith("GATE FAILED"):
                A["runs"].append(gate_refused_run(rec["id"], rec["n"], rec["block"], rec["gate_words"], rec.get("why")))
            A["runs_not_started"].append({"run": key, "why": rec.get("why")})
            continue
        r = reduce_run(os.path.join(rd, key), rec, tel)
        run = scorer_run(rec["id"], r, rec["procs"][0].get("gate"))
        if r.get("t_gemm_s") is None:
            A["runs_without_counted_launch"].append({"run": key, "why": r.get("why")})
        A["runs"].append(run)
    A["runs"].sort(key=lambda x: x["n"] or 0)
    q = os.path.join(sd, "queue.json")
    if os.path.exists(q):
        qq = C.load(q)
        A["queue"] = {"stop": qq.get("stop"), "card_min": qq.get("card_min"), "rest_die_c": qq.get("rest_die_c"),
                      "rest_board_w": qq.get("rest_board_w"), "hung": qq.get("hung"), "rc": qq.get("rc"),
                      "not_started": [x for x in qq.get("queue", []) if not x.get("ran")]}
    return A


def table(data):
    L = ["E211 reduced (each run; J over idle = (p_work - p_rest) t_gemm, J with the card at rest = p_work t_gemm, the scorer's form)"]
    for arm, A in data["arms"].items():
        L.append(f"arm {arm} ({A.get('session')}): {A.get('n_samples')} samples; queue stop {A.get('queue', {}).get('stop')}")
        for r in A["smoke"]["runs"] + A["runs"]:
            walk = r.get("walk")
            ws = "no walk (rgm136's host)" if walk is None else f"walk {sorted(set(map(str, walk['names'])))} ok {sorted(set(map(str, walk['ok'])))} bad {walk['launches_bad']}"
            g = str(r.get("gate") or "")[:9]
            if r.get("t_gemm_s"):
                jo = (r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] if r.get("p_rest_w") is not None and r.get("p_work_w") is not None else None
                jr = r["p_work_w"] * r["t_gemm_s"] if r.get("p_work_w") is not None else None
                L.append(f"  {r['n']:3d} {r.get('block'):5s} {r['point']:4s} t {r['t_gemm_s']:.6g} s; cycles an op {r.get('cycles_per_op')}, a GEMM "
                         f"{r.get('cycles_gemm')}; work {r['p_work_w']} W, rest {r['p_rest_w']} W; J over idle {jo if jo is None else round(jo, 6)}, "
                         f"at rest {jr if jr is None else round(jr, 6)}; die {r.get('die_start_c')} C; MHz min {r['mhz_min']}, max {r.get('mhz_max')}; "
                         f"checks {sorted(set(map(str, r['checks'])))}; {ws}; {g}")
            else:
                L.append(f"  {r['n']:3d} {r.get('block'):5s} {r['point']:4s} NO COUNTED LAUNCH ({r['detail'].get('why')}); checks "
                         f"{sorted(set(map(str, r['checks'])))}; {ws}; {g}")
        for x in A.get("runs_not_started", []):
            L.append(f"  not started: {x['run']} ({x['why']})")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", action="append", default=[], help="A=<session dir> (E211's one arm)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt")
    a = ap.parse_args(argv)
    data = {"experiment": "E211", "reducer": "tools/claims-v3/e211/reduce_e211.py", "arms": {}}
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
