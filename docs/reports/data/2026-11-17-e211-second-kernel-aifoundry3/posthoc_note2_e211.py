#!/usr/bin/env python3
"""E211 data, dated note 2 (POST HOC; Q204's lane fix-e211d, Tue 17 Nov 2026, after the data verifier verify-e211d): the figures the note
states, each from this directory's committed records and the registration's frozen files, checked first against their sha256 (this
directory's SHA256SUMS; the registration's pins). It changes nothing it reads, writes only to stdout and the --json path, scores no rule and
reads no score: the frozen scorer's verdicts stand as it printed them.

  cd docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3
  /usr/bin/python3 -I -B posthoc_note2_e211.py --json posthoc-note2-e211.json > posthoc-note2-e211.txt

  1. THE HEAD TO HEAD PER W PAIR (H1 MM1 against F1, H2 against the chip-lines null NC, H3 against the no-walk null N0), as rules-e211.json
     registers it: each pair's measured wall ratio rgm211/rgm136 (the mean of its gemmLn runs' wall cycles an op over the mean of its gemmL
     runs', in its own W block; a run's wall = cycles_gemm / the point's ops a minion a GEMM), d = |ln(measured / second)| - |ln(measured /
     MM1)|, MM1 closer where d > tie, the second where d < -tie, a tie otherwise, with the registered tie (rules > H > tie_ln_cycles). On the
     raw ratios (Amendment A1 did not apply, so these carry the registered words "the controls did not pass: not a model test").
  2. THE SMOKE'S REST CELLS: each smoke process's 5 s before its start (the reducer's p_rest window, e211_common.REST_WINDOW_S), what falls in
     it (the smoke's 30 s rest reading, an earlier smoke process, neither), its median board W (= data-e211.json's p_rest_w), the README's
     cells (p_rest; mJ over idle = (p_work - p_rest) t_gemm; mJ at rest = p_work t_gemm), the smoke gate's own reading of the process's
     rise (smoke.json's board_rise) and, post hoc, mJ over idle on the session's own rest reading (session/smoke/rest.json's
     board_w_median).
  3. THE SHIRES' MEAN PEAK: the highest shires' mean (temp_c.minshire[0], e211_common.die_of) over every telemetry sample, how many samples
     read it, the first and the last, and where they fall (a run's process, its rest read, or between).
  4. THE NEVER-RUN SEARCH'S OWN GAP: each scan of neverrun-e211-card.json (roots, files read, unreadable, over 400 MB and skipped).
Python's own modules only; times in PST (UTC-8, the session's day). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

PST = timezone(timedelta(hours=-8), "PST")
REG = "tools/claims-v3/e211"
PINS = {  # the registration's frozen files (E211.md section 0; unchanged from 1393a649 to the data commit 38aaf004)
    f"{REG}/forecast-e211.json": "90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5",
    f"{REG}/rules-e211.json": "53c54fbe278fb9aa9e1a3875cdea0782339b25bd831a55f48f3fd912b26d37ca",
    f"{REG}/points-e211.json": "234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537",
}
REST_WINDOW_MS = 5000  # e211_common.REST_WINDOW_S = 5.0: the reducer's p_rest window, the last 5 s before a process starts


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def clock(t_ms):
    d = datetime.fromtimestamp(t_ms / 1000.0, tz=PST)
    return d.strftime("%H:%M:%S") + f".{int(round(t_ms)) % 1000:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=".", help="E211's data directory (default: the current directory)")
    ap.add_argument("--json", required=True)
    a = ap.parse_args()
    D = a.data
    R = os.path.normpath(os.path.join(D, "..", "..", "..", ".."))
    out = {"what": "E211 data, dated note 2: POST HOC figures (desk arithmetic of measured records and the frozen files); no score",
           "interpreter": f"{sys.executable} {sys.version.split()[0]}", "inputs_sha256": {}}
    lines = []
    P = lines.append

    # ---- the inputs, checked first
    sums = {}
    with open(os.path.join(D, "SHA256SUMS")) as f:
        for ln in f:
            h, _, p = ln.rstrip("\n").partition("  ")
            sums[p] = h
    run_dirs = sorted(x for x in os.listdir(os.path.join(D, "session", "runs")))
    data_files = ["data-e211.json", "neverrun-e211-card.json", "session/telemetry.jsonl.gz", "session/smoke/rest.json",
                  "session/smoke/s01/smoke.json", "session/smoke/s02/smoke.json", "session/smoke/s03/smoke.json"] + \
                 [f"session/runs/{r}/run.json" for r in run_dirs]
    bad = []
    for p in data_files:
        h = sha(os.path.join(D, p))
        if sums.get(p) != h:
            bad.append(p)
    for p, want in PINS.items():
        h = sha(os.path.join(R, p))
        out["inputs_sha256"][p] = h
        if h != want:
            bad.append(p)
    out["inputs_sha256"]["data-e211.json"] = sha(os.path.join(D, "data-e211.json"))
    P(f"INPUTS: {len(data_files)} files of this directory against its SHA256SUMS, 3 registration files against their pins: "
      f"{'ALL OK' if not bad else 'MISMATCH ' + ', '.join(bad)}")
    if bad:
        print("\n".join(lines))
        return 4

    data = json.load(open(os.path.join(D, "data-e211.json")))
    fc = json.load(open(os.path.join(R, REG, "forecast-e211.json")))
    rules = json.load(open(os.path.join(R, REG, "rules-e211.json")))
    pts = json.load(open(os.path.join(R, REG, "points-e211.json")))
    A = data["arms"]["A"]

    # ---- 1. the head to head per W pair (H1-H3), the registered tie
    ops = {p["id"]: p["ops_per_minion_per_gemm"] for p in pts["points"]}
    arm_of = {p["id"]: p["arm"] for p in pts["points"]}
    tie = rules["H"]["tie_ln_cycles"]
    others = [(r, rules["H"]["rules"][r]["second"]) for r in ("H1", "H2", "H3")]
    wpairs = sorted(k for k, v in fc["pairs"].items() if v["family"] == "W")
    per, counts = {}, {r: {"MM1": 0, o: 0, "tie": 0} for r, o in others}
    P("")
    P(f"1. THE HEAD TO HEAD PER W PAIR (raw wall ratios rgm211/rgm136; d = |ln(measured/second)| - |ln(measured/MM1)|; registered tie {tie} in ln)")
    P("   pair  measured   MM1      F1       NC       N0     | d H1 (F1)  d H2 (NC)  d H3 (N0) | closer H1 / H2 / H3")
    for pair in wpairs:
        walls = {"m": [], "n": []}
        for r in A["runs"]:
            pid = r.get("point") or ""
            if r.get("pair") != pair or r.get("block") != "W" or r.get("cycles_gemm") is None:
                continue
            rec = r.get("record") or {}
            if rec.get("arm") != arm_of.get(pid):
                continue
            walls[pid[-1]].append(r["cycles_gemm"] / ops[pid])
        rho = (sum(walls["n"]) / len(walls["n"])) / (sum(walls["m"]) / len(walls["m"]))
        fr = fc["pairs"][pair]["ratio_wall"]
        e_mm1 = abs(math.log(rho / fr["MM1"]))
        row = {"measured": rho, "runs_gemmL": len(walls["m"]), "runs_gemmLn": len(walls["n"]),
               "forecast": {k: fr[k] for k in ("MM1", "F1", "NC", "N0")}, "d": {}, "closer": {}}
        for rule, o in others:
            d = abs(math.log(rho / fr[o])) - e_mm1
            c = "MM1" if d > tie else (o if d < -tie else "tie")
            row["d"][rule] = d
            row["closer"][rule] = c
            counts[rule][c] += 1
        per[pair] = row
        P(f"   {pair}   {rho:.5f}  {fr['MM1']:.5f}  {fr['F1']:.5f}  {fr['NC']:.5f}  {fr['N0']:.3f}  | "
          f"{row['d']['H1']:+.4f}    {row['d']['H2']:+.4f}    {row['d']['H3']:+.4f}   | "
          f"{row['closer']['H1']} / {row['closer']['H2']} / {row['closer']['H3']}")
    for rule, o in others:
        P(f"   {rule} (MM1 against {o}): MM1 closer {counts[rule]['MM1']}, {o} closer {counts[rule][o]}, ties {counts[rule]['tie']}")
    near = [f"{p} {r} d {per[p]['d'][r]:+.4f}" for p in wpairs for r, _ in others if abs(per[p]["d"][r]) <= tie]
    P(f"   inside the tie (|d| <= {tie}): {'; '.join(near) if near else 'none'}")
    out["head_to_head_per_W_pair"] = {"tie_ln": tie, "basis": "raw ratios (Amendment A1 did not apply)",
                                      "words": rules["A1"]["label_not_a_model_test"], "pairs": per, "counts": counts}

    # ---- 2. the smoke's rest cells
    tel = []
    with gzip.open(os.path.join(D, "session", "telemetry.jsonl.gz"), "rt") as f:
        for ln in f:
            if not ln.startswith("{"):
                continue
            try:
                s = json.loads(ln)
            except ValueError:
                continue
            if isinstance(s, dict) and s.get("t_ms") is not None:
                tel.append((s["t_ms"], s.get("board_w"), ((s.get("temp_c") or {}).get("minshire") or [None])[0]))
    tel.sort()
    rest = json.load(open(os.path.join(D, "session", "smoke", "rest.json")))
    sm = {s: json.load(open(os.path.join(D, "session", "smoke", s, "smoke.json"))) for s in ("s01", "s02", "s03")}
    srun = {r["point"]: r for r in A["smoke"]["runs"]}
    p_rest_session = rest["board_w_median"]
    P("")
    P(f"2. THE SMOKE'S REST CELLS (the reducer's p_rest: the median board W of the {REST_WINDOW_MS // 1000} s before the process starts)")
    P(f"   the smoke's 30 s rest reading: {clock(rest['t0_ms'])} to {clock(rest['t1_ms'])} PST, {rest['samples']} samples, median "
      f"{p_rest_session} W (session/smoke/rest.json)")
    smoke = {}
    prev = []
    for s in ("s01", "s02", "s03"):
        t0, t1 = sm[s]["t0_ms"], sm[s]["t1_ms"]
        win = [x for x in tel if t0 - REST_WINDOW_MS <= x[0] < t0]
        in_rest = [x for x in win if rest["t0_ms"] <= x[0] <= rest["t1_ms"]]
        in_prev = {q: len([x for x in win if sm[q]["t0_ms"] <= x[0] <= sm[q]["t1_ms"]]) for q in prev}
        neither = len(win) - len(in_rest) - sum(in_prev.values())
        med = statistics.median([x[1] for x in win if x[1] is not None])
        r = srun[s]
        pw, pr, t = r["p_work_w"], r["p_rest_w"], r["t_gemm_s"]
        gap = (t0 - sm[prev[-1]]["t1_ms"]) if prev else None
        row = {"process_ms": [t0, t1], "process_pst": [clock(t0), clock(t1)], "gap_after_previous_ms": gap,
               "window_samples": len(win), "window_in_rest_reading": len(in_rest), "window_in_earlier_smoke": in_prev,
               "window_in_neither": neither, "window_median_board_w": med, "data_p_rest_w": pr, "p_work_w": pw, "t_gemm_s": t,
               "readme_mJ_over_idle": (pw - pr) * t * 1e3, "readme_mJ_at_rest": pw * t * 1e3,
               "posthoc_mJ_over_idle_on_session_rest": (pw - p_rest_session) * t * 1e3,
               "posthoc_W_over_session_rest": pw - p_rest_session, "rest_reading": len(in_rest) == len(win),
               "smoke_gate_board_rise": sm[s].get("board_rise")}
        smoke[s] = row
        P(f"   {s}: process {clock(t0)} to {clock(t1)} PST" + (f" ({gap} ms after {prev[-1]} ended)" if prev else "")
          + f"; its 5 s window: {len(win)} samples, {len(in_rest)} in the rest reading"
          + "".join(f", {n} in {q}'s process" for q, n in in_prev.items()) + f", {neither} in neither; median {med:.6g} W"
          + f" (data-e211.json p_rest_w {pr:.6g}): {'AT REST' if row['rest_reading'] else 'NOT A REST READING'}")
        P(f"       README cells: p_rest {pr:.6g} W, mJ over idle {row['readme_mJ_over_idle']:.4g}, mJ at rest {row['readme_mJ_at_rest']:.4g};"
          f" post hoc on the session's rest reading ({p_rest_session} W): {row['posthoc_W_over_session_rest']:.2f} W over it,"
          f" mJ over idle {row['posthoc_mJ_over_idle_on_session_rest']:.4g}")
        g = sm[s].get("board_rise") or {}
        P(f"       the smoke gate's own reading (smoke.json board_rise): {g.get('rise_w')} W over rest_w {g.get('rest_w')} W on "
          f"{g.get('samples')} samples")
        prev.append(s)
    runs_at_rest, runs_seen = [], 0
    for rd in run_dirs:
        rj = json.load(open(os.path.join(D, "session", "runs", rd, "run.json")))
        if not rj.get("procs") or not rj.get("rest"):
            continue
        runs_seen += 1
        t0 = rj["procs"][0]["t0_ms"]
        win = [x for x in tel if t0 - REST_WINDOW_MS <= x[0] < t0]
        if win and all(rj["rest"]["t0_ms"] <= x[0] <= rj["rest"]["t1_ms"] for x in win):
            runs_at_rest.append(rd)
    P(f"   the runs: the 5 s window before the process lies inside the run's own 10 s rest read in {len(runs_at_rest)} of {runs_seen}")
    out["smoke_rest_cells"] = {"window_ms": REST_WINDOW_MS, "session_rest_reading": {"t0_ms": rest["t0_ms"], "t1_ms": rest["t1_ms"],
                               "samples": rest["samples"], "board_w_median": p_rest_session}, "smoke": smoke,
                               "runs_window_inside_own_rest_read": len(runs_at_rest), "runs_seen": runs_seen}

    # ---- 3. the shires' mean peak
    dies = [x for x in tel if x[2] is not None]
    top = max(x[2] for x in dies)
    at = [x for x in dies if x[2] == top]
    span = [x for x in dies if at[0][0] <= x[0] <= at[-1][0]]
    wins = []
    for rd in run_dirs:
        rj = json.load(open(os.path.join(D, "session", "runs", rd, "run.json")))
        for pr_ in rj.get("procs") or []:
            wins.append((pr_["t0_ms"], pr_["t1_ms"], rd, "process"))
        if rj.get("rest"):
            wins.append((rj["rest"]["t0_ms"], rj["rest"]["t1_ms"], rd, "rest read"))
    where = {}
    for x in at:
        hit = [f"{w[2]} {w[3]}" for w in wins if w[0] <= x[0] <= w[1]]
        k = hit[0] if hit else "between (a run's gate wait or tail)"
        where[k] = where.get(k, 0) + 1
    P("")
    P(f"3. THE SHIRES' MEAN PEAK (temp_c.minshire[0] over {len(dies)} of {len(tel)} telemetry samples)")
    P(f"   highest {top} C on {len(at)} samples, the first at {clock(at[0][0])} PST and the last at {clock(at[-1][0])} PST "
      f"({len(span)} samples from the first to the last); where: " + "; ".join(f"{k} {v}" for k, v in sorted(where.items())))
    out["shires_mean_peak"] = {"samples": len(tel), "samples_with_reading": len(dies), "highest_c": top, "n_at_highest": len(at),
                               "first_pst": clock(at[0][0]), "last_pst": clock(at[-1][0]), "first_ms": at[0][0], "last_ms": at[-1][0],
                               "samples_first_to_last": len(span), "where": where}

    # ---- 4. the never-run search's own gap
    nr = json.load(open(os.path.join(D, "neverrun-e211-card.json")))
    P("")
    P(f"4. THE NEVER-RUN SEARCH'S OWN GAP (neverrun-e211-card.json, {nr.get('when')})")
    for s in nr["scans"]:
        P(f"   scan {s['label']} on {s['box']}: {s['roots']} roots, {s['files_read']} files read, unreadable {s['n_unreadable']}, "
          f"over 400 MB (skipped) {s['over_400MB']}")
    gap = [s for s in nr["scans"] if s["n_unreadable"] or s["over_400MB"]]
    P("   with a gap: " + ("; ".join(f"{s['label']}: {s['n_unreadable']} unreadable, {s['over_400MB']} over 400 MB" for s in gap) if gap else "none"))
    out["neverrun_scans"] = nr["scans"]

    print("\n".join(lines))
    with open(a.json, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
