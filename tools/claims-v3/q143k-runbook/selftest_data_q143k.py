#!/usr/bin/env python3
"""Q143(k)'s fix pass, Thu 5 Nov 2026: the desk test's data maker for step 22 v2 (selftest_runbook_q143k_v2.sh). It writes, in a scratch
directory outside the lab clone, either a data directory in E176's collected layout or a stand-in box's pass directories:

  committed <committed data dir> <smoke pass rel> <measured pass rel> <out data dir> [fault ...]
      the committed session's launch marks, C logs and check, renamed to E176's passes (smoke -> p17601, measured -> p17620; the check's
      log names with them). E166's (4 Nov 2026) and E154's (3 Nov) committed sessions carry launch marks with records and their C logs.
  synth <out data dir> [fault ...]
      a small synthetic session: the smoke 2 processes (4 and 2 records), the measured pass 5 processes (3 records each).
  box <committed data dir> <smoke pass rel> <measured pass rel> <out box tree> [fault ...]
      the stand-in box's build/claims-v3/aifoundry3/{e176-smoke/p17601, e176/p17620} from the committed passes (each file copied, the C
      log un-gzipped into the pass as the box leaves it), the measured pass's holds renamed to M11's as score_m11_v2.py's self-test names
      them (H_M->H_E, K_S->Z, K_Q->L1, K_L->S, K_O->L2) with a passed start_gate mark added, and build/e176/session.log.

faults: no-measured-clog, empty-measured-clog, no-smoke-clog, short-measured (the check misses one launch of the measured pass's last
process), orphan (a checked launch outside every window), smoke-nolaunch, measured-nolaunch, no-records (the first measured launch mark
loses its records).

Standard library only. It refuses an output inside the lab clone. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
TREE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
REN = {"H_M": "H_E", "K_S": "Z", "K_Q": "L1", "K_L": "S", "K_O": "L2"}
FAULTS = {"no-measured-clog", "empty-measured-clog", "no-smoke-clog", "short-measured", "orphan", "smoke-nolaunch", "measured-nolaunch",
          "no-records"}


def outside(p):
    a = os.path.realpath(p)
    if a == TREE or a.startswith(TREE + os.sep):
        raise SystemExit(f"refused: {p} is inside the lab clone")
    return p


def jl(p):
    with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as f:
        return [json.loads(x) for x in f if x.strip()]


def wjl(p, rows, gz=False):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with (gzip.open(p, "wt") if gz else open(p, "w")) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def summary(rows):
    s = {k: sum(1 for r in rows if r.get("verdict") == k) for k in ("PASS", "ROUNDING", "UNMODELLED", "FAIL")}
    return dict(launches=len(rows), **s, all_pass=s["FAIL"] == 0 and len(rows) > 0)


def apply_marks(marks, nolaunch=False, norecords=False):
    out = [m for m in marks if not (nolaunch and m.get("kind") == "launch")]
    if norecords:
        for m in out:
            if m.get("kind") == "launch":
                m.pop("records", None)
                break
    return out


def write_check(out, rows_s, rows_m, faults):
    if "short-measured" in faults and rows_m:
        rows_m = rows_m[:-1]
    if "orphan" in faults and rows_m:
        x = dict(rows_m[-1])
        x["t_start_ms"] = int(x["t_start_ms"]) + 3_600_000
        x["t_end_ms"] = int(x["t_end_ms"]) + 3_600_000
        rows_m = rows_m + [x]
    rows = rows_s + rows_m
    os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
    with open(os.path.join(out, "ccheck", "ccheck-all.json"), "w") as f:
        json.dump({"engine": "selftest_data_q143k", "summary": summary(rows), "launches": rows}, f)
    return len(rows)


def committed(src, smoke_rel, meas_rel, out, faults):
    outside(out)
    s_name, m_name = os.path.basename(smoke_rel), os.path.basename(meas_rel)
    ms = apply_marks(jl(os.path.join(src, smoke_rel, "marks.jsonl")), nolaunch="smoke-nolaunch" in faults)
    mm = apply_marks(jl(os.path.join(src, meas_rel, "marks.jsonl")), nolaunch="measured-nolaunch" in faults,
                     norecords="no-records" in faults)
    wjl(os.path.join(out, "aifoundry3", "e176-smoke", "p17601", "marks.jsonl"), ms)
    wjl(os.path.join(out, "aifoundry3", "e176", "p17620", "marks.jsonl"), mm)
    chk = json.load(open(os.path.join(src, "ccheck", "ccheck-all.json")))["launches"]
    rows_s, rows_m = [], []
    if not ({"no-smoke-clog", "smoke-nolaunch"} & faults):
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        shutil.copy2(os.path.join(src, "ccheck", f"c-log-{s_name}.jsonl.gz"), os.path.join(out, "ccheck", "c-log-p17601.jsonl.gz"))
        rows_s = [dict(r, log="c-log-p17601.jsonl") for r in chk if r.get("log") == f"c-log-{s_name}.jsonl"]
    if "empty-measured-clog" in faults:
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        with gzip.open(os.path.join(out, "ccheck", "c-log-p17620.jsonl.gz"), "wt"):
            pass
    elif not ({"no-measured-clog", "measured-nolaunch"} & faults):
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        shutil.copy2(os.path.join(src, "ccheck", f"c-log-{m_name}.jsonl.gz"), os.path.join(out, "ccheck", "c-log-p17620.jsonl.gz"))
        rows_m = [dict(r, log="c-log-p17620.jsonl") for r in chk if r.get("log") == f"c-log-{m_name}.jsonl"]
    n = write_check(out, rows_s, rows_m, faults)
    print(f"committed session {os.path.basename(os.path.normpath(src))} ({s_name}, {m_name}) -> {out}: check rows {n}; faults {sorted(faults) or 'none'}")


def synth(out, faults):
    outside(out)
    base = 1793900000000

    def sess(n_proc, recs, t0):
        marks, rows = [], []
        for i in range(n_proc):
            a = t0 + 10_000 * i
            marks.append({"kind": "launch", "block": "X", "t_start_ms": a, "t_end_ms": a + 5_000, "rc": 0, "records": recs[i]})
            for j in range(recs[i]):
                rows.append({"t_start_ms": a + 100 * (j + 1), "t_end_ms": a + 100 * (j + 1) + 20, "verdict": "PASS", "type": "fp32"})
        return marks, rows

    ms, rs = sess(2, [4, 2], base)
    mm, rm = sess(5, [3] * 5, base + 600_000)
    ms = apply_marks([{"kind": "room", "t_ms": base - 1000}] + ms, nolaunch="smoke-nolaunch" in faults)
    mm = apply_marks([{"kind": "start_gate", "t_ms": base + 590_000, "passed": True}] + mm, nolaunch="measured-nolaunch" in faults,
                     norecords="no-records" in faults)
    wjl(os.path.join(out, "aifoundry3", "e176-smoke", "p17601", "marks.jsonl"), ms)
    wjl(os.path.join(out, "aifoundry3", "e176", "p17620", "marks.jsonl"), mm)
    rows_s, rows_m = [], []
    if not ({"no-smoke-clog", "smoke-nolaunch"} & faults):
        rows_s = [dict(r, log="c-log-p17601.jsonl") for r in rs]
        wjl(os.path.join(out, "ccheck", "c-log-p17601.jsonl.gz"), [{"kind": "c"} for _ in rows_s], gz=True)
    if "empty-measured-clog" in faults:
        wjl(os.path.join(out, "ccheck", "c-log-p17620.jsonl.gz"), [], gz=True)
    elif not ({"no-measured-clog", "measured-nolaunch"} & faults):
        rows_m = [dict(r, log="c-log-p17620.jsonl") for r in rm]
        wjl(os.path.join(out, "ccheck", "c-log-p17620.jsonl.gz"), [{"kind": "c"} for _ in rows_m], gz=True)
    n = write_check(out, rows_s, rows_m, faults)
    print(f"synthetic session -> {out}: check rows {n}; faults {sorted(faults) or 'none'}")


def box(src, smoke_rel, meas_rel, out, faults):
    outside(out)
    s_name, m_name = os.path.basename(smoke_rel), os.path.basename(meas_rel)
    bld = os.path.join(out, "aifoundry3", "aifoundry", "build")
    ds = os.path.join(bld, "claims-v3", "aifoundry3", "e176-smoke", "p17601")
    dm = os.path.join(bld, "claims-v3", "aifoundry3", "e176", "p17620")
    for d in (ds, dm):
        if os.path.exists(d):
            shutil.rmtree(d)
    shutil.copytree(os.path.join(src, smoke_rel), ds)
    os.makedirs(dm)
    for fn in os.listdir(os.path.join(src, meas_rel)):
        if fn in ("marks.jsonl", "runs.jsonl"):
            continue
        shutil.copy2(os.path.join(src, meas_rel, fn), dm)
    marks = []
    for m in jl(os.path.join(src, meas_rel, "marks.jsonl")):
        for key in ("name", "hold", "block"):
            if m.get(key) in REN:
                m[key] = REN[m[key]]
        marks.append(m)
        if m.get("kind") == "room" and not any(x.get("kind") == "start_gate" for x in marks):
            marks.append({"kind": "start_gate", "t_ms": m["t_ms"], "room_c": m.get("mean34_c"), "max_c": 53.0, "passed": True,
                          "why": "desk test: added to a committed pass that predates or names no M11 gate"})
    wjl(os.path.join(dm, "marks.jsonl"), apply_marks(marks, nolaunch="measured-nolaunch" in faults, norecords="no-records" in faults))
    runs = []
    for r in jl(os.path.join(src, meas_rel, "runs.jsonl")):
        if r.get("block") in REN:
            r["block"] = REN[r["block"]]
        runs.append(r)
    wjl(os.path.join(dm, "runs.jsonl"), runs)
    if not ({"no-smoke-clog", "smoke-nolaunch"} & faults):
        wjl(os.path.join(ds, "c-log.jsonl"), jl(os.path.join(src, "ccheck", f"c-log-{s_name}.jsonl.gz")))
    if not ({"no-measured-clog", "measured-nolaunch"} & faults):
        wjl(os.path.join(dm, "c-log.jsonl"), jl(os.path.join(src, "ccheck", f"c-log-{m_name}.jsonl.gz")))
    os.makedirs(os.path.join(bld, "e176"), exist_ok=True)
    with open(os.path.join(bld, "e176", "session.log"), "w") as f:
        f.write("2026-11-05 13:00:00 PST session start (desk test)\n2026-11-05 14:15:00 PST pass 17620 rc=0\n"
                "2026-11-05 14:15:30 PST session end\n")
    print(f"stand-in box passes from {os.path.basename(os.path.normpath(src))} ({s_name} -> p17601, {m_name} -> p17620, M11's names) -> "
          f"{os.path.relpath(bld, out)}; faults {sorted(faults) or 'none'}")


def main(a):
    if not a:
        raise SystemExit(__doc__)
    mode = a[0]
    if mode == "committed" and len(a) >= 5:
        f = set(a[5:])
        args = (a[1], a[2], a[3], a[4], f)
        fn = committed
    elif mode == "box" and len(a) >= 5:
        f = set(a[5:])
        args = (a[1], a[2], a[3], a[4], f)
        fn = box
    elif mode == "synth" and len(a) >= 2:
        f = set(a[2:])
        args = (a[1], f)
        fn = synth
    else:
        raise SystemExit(__doc__)
    if f - FAULTS:
        raise SystemExit(f"unknown fault(s): {sorted(f - FAULTS)}")
    fn(*args)


if __name__ == "__main__":
    main(sys.argv[1:])
