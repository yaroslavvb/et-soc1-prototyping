#!/usr/bin/env python3
"""E181 (M11's session 2): the desk test's data maker for E181's runbook (selftest_rb_e181.sh): ../../q143k-runbook/selftest_data_q143k.py
(6b013ad9, which stays as committed) with E181's passes (smoke p18101, measured p18120) and three more faults (dup-start, g0-refused,
f0-stopped); the synthetic and stand-in sessions carry A6-1's floor mark and an A6-2-with-A8-4 start_gate mark. It writes, in a scratch
directory outside the lab clone, either a data directory in E181's collected layout or a stand-in box's pass directories:

  committed <committed data dir> <smoke pass rel> <measured pass rel> <out data dir> [fault ...]
      the committed session's launch marks, C logs and check, renamed to E181's passes (smoke -> p18101, measured -> p18120; the check's
      log names with them). E166's (4 Nov 2026) and E154's (3 Nov) committed sessions carry launch marks with records and their C logs.
  synth <out data dir> [fault ...]
      a small synthetic session: the smoke 2 processes (4 and 2 records), the measured pass 5 processes (3 records each).
  box <committed data dir> <smoke pass rel> <measured pass rel> <out box tree> [fault ...]
      the stand-in box's build/claims-v3/aifoundry3/{e181-smoke/p18101, e181/p18120} from the committed passes (each file copied, the C
      log un-gzipped into the pass as the box leaves it), the measured pass's holds renamed to M11's as score_m11_v2.py's self-test names
      them (H_M->H_E, K_S->Z, K_Q->L1, K_L->S, K_O->L2), the smoke's floor mark (F0: its first 3 s, as run_e181.py reads it) and the
      measured pass's start_gate mark in A6-2-with-A8-4's form added, and build/e181/session.log.

faults: no-measured-clog, empty-measured-clog, no-smoke-clog, short-measured (the check misses one launch of the measured pass's last
process), orphan (a checked launch outside every window), smoke-nolaunch, measured-nolaunch, no-records (the first measured launch mark
loses its records); E181's: dup-start (the measured pass's second launch mark takes the first's t_start_ms), g0-refused (the measured
pass's start gate refused: passed false, no launch, no C log), f0-stopped (A6-1: the smoke's floor mark refused, no launch anywhere, no
measured pass).

Standard library only. It refuses an output inside the lab clone. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
TREE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
G_TS, H_TS, CAL5 = 57400, 249400, 4096
REN = {"H_M": "H_E", "K_S": "Z", "K_Q": "L1", "K_L": "S", "K_O": "L2"}
FAULTS = {"no-measured-clog", "empty-measured-clog", "no-smoke-clog", "short-measured", "orphan", "smoke-nolaunch", "measured-nolaunch",
          "no-records", "dup-start", "g0-refused", "f0-stopped"}


def norm(faults):
    """E181: g0-refused implies the measured pass ran no launch; f0-stopped implies no launch anywhere and no measured pass"""
    f = set(faults)
    if "g0-refused" in f:
        f |= {"measured-nolaunch"}
    if "f0-stopped" in f:
        f |= {"smoke-nolaunch", "measured-nolaunch"}
    return f


def gate_marks(t_ms, room, f0, refused=False):
    resid = room - f0
    exc = resid - 0.414
    ok = (room <= 53.9 and exc <= 0.50) and not refused
    return {"kind": "start_gate", "t_ms": t_ms, "room_c": room if not refused else 54.2, "max_c": 53.9, "floor_c": f0, "floor_from": "desk test",
            "residue_c": resid, "residue_pred_c": 0.414, "residue_excess_c": exc, "residue_line_c": 0.5, "room_ok": not refused,
            "residue_ok": exc <= 0.5, "passed": ok, "why": "desk test: the start gate (G0-A6 with A8-4)" + (": room 54.200 C > 53.9 C" if refused else ""),
            "rule": "A6-2 with A8-4"}


def floor_mark(t_ms, f0, stopped=False):
    return {"kind": "floor", "t_ms": t_ms, "first_sample_ms": t_ms - 3000, "window_s": 3.0, "samples": 30, "samples_34": 30,
            "mean34_c": 54.2 if stopped else f0, "firmware_c": None, "board_w": 23.4, "line_c": 53.9, "passed": not stopped,
            "why": "F0 54.200 C > 53.9 C" if stopped else "F0 at or under 53.9 C: the smoke runs"}


def dup(marks):
    """dup-start: the second launch mark takes the first's t_start_ms"""
    ls = [m for m in marks if m.get("kind") == "launch"]
    if len(ls) >= 2:
        ls[1]["t_start_ms"] = ls[0]["t_start_ms"]
    return marks


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
    faults = norm(faults)
    s_name, m_name = os.path.basename(smoke_rel), os.path.basename(meas_rel)
    ms = apply_marks(jl(os.path.join(src, smoke_rel, "marks.jsonl")), nolaunch="smoke-nolaunch" in faults)
    mm = apply_marks(jl(os.path.join(src, meas_rel, "marks.jsonl")), nolaunch="measured-nolaunch" in faults,
                     norecords="no-records" in faults)
    if "dup-start" in faults:
        mm = dup(mm)
    wjl(os.path.join(out, "aifoundry3", "e181-smoke", "p18101", "marks.jsonl"), ms)
    if "f0-stopped" not in faults:
        wjl(os.path.join(out, "aifoundry3", "e181", "p18120", "marks.jsonl"), mm)
    chk = json.load(open(os.path.join(src, "ccheck", "ccheck-all.json")))["launches"]
    rows_s, rows_m = [], []
    if not ({"no-smoke-clog", "smoke-nolaunch"} & faults):
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        shutil.copy2(os.path.join(src, "ccheck", f"c-log-{s_name}.jsonl.gz"), os.path.join(out, "ccheck", "c-log-p18101.jsonl.gz"))
        rows_s = [dict(r, log="c-log-p18101.jsonl") for r in chk if r.get("log") == f"c-log-{s_name}.jsonl"]
    if "empty-measured-clog" in faults:
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        with gzip.open(os.path.join(out, "ccheck", "c-log-p18120.jsonl.gz"), "wt"):
            pass
    elif not ({"no-measured-clog", "measured-nolaunch"} & faults):
        os.makedirs(os.path.join(out, "ccheck"), exist_ok=True)
        shutil.copy2(os.path.join(src, "ccheck", f"c-log-{m_name}.jsonl.gz"), os.path.join(out, "ccheck", "c-log-p18120.jsonl.gz"))
        rows_m = [dict(r, log="c-log-p18120.jsonl") for r in chk if r.get("log") == f"c-log-{m_name}.jsonl"]
    n = write_check(out, rows_s, rows_m, faults)
    print(f"committed session {os.path.basename(os.path.normpath(src))} ({s_name}, {m_name}) -> {out}: check rows {n}; faults {sorted(faults) or 'none'}")


def synth(out, faults):
    outside(out)
    faults = norm(faults)
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
    ms = apply_marks([floor_mark(base - 5000, 50.5, stopped="f0-stopped" in faults), {"kind": "room", "t_ms": base - 1000}] + ms,
                     nolaunch="smoke-nolaunch" in faults)
    mm = apply_marks([gate_marks(base + 590_000, 50.9, 50.5, refused="g0-refused" in faults)] + mm, nolaunch="measured-nolaunch" in faults,
                     norecords="no-records" in faults)
    if "dup-start" in faults:
        mm = dup(mm)
    wjl(os.path.join(out, "aifoundry3", "e181-smoke", "p18101", "marks.jsonl"), ms)
    if "f0-stopped" not in faults:
        wjl(os.path.join(out, "aifoundry3", "e181", "p18120", "marks.jsonl"), mm)
    rows_s, rows_m = [], []
    if not ({"no-smoke-clog", "smoke-nolaunch"} & faults):
        rows_s = [dict(r, log="c-log-p18101.jsonl") for r in rs]
        wjl(os.path.join(out, "ccheck", "c-log-p18101.jsonl.gz"), [{"kind": "c"} for _ in rows_s], gz=True)
    if "empty-measured-clog" in faults:
        wjl(os.path.join(out, "ccheck", "c-log-p18120.jsonl.gz"), [], gz=True)
    elif not ({"no-measured-clog", "measured-nolaunch"} & faults):
        rows_m = [dict(r, log="c-log-p18120.jsonl") for r in rm]
        wjl(os.path.join(out, "ccheck", "c-log-p18120.jsonl.gz"), [{"kind": "c"} for _ in rows_m], gz=True)
    n = write_check(out, rows_s, rows_m, faults)
    print(f"synthetic session -> {out}: check rows {n}; faults {sorted(faults) or 'none'}")


def box(src, smoke_rel, meas_rel, out, faults):
    outside(out)
    faults = norm(faults)
    s_name, m_name = os.path.basename(smoke_rel), os.path.basename(meas_rel)
    bld = os.path.join(out, "aifoundry3", "aifoundry", "build")
    ds = os.path.join(bld, "claims-v3", "aifoundry3", "e181-smoke", "p18101")
    dm = os.path.join(bld, "claims-v3", "aifoundry3", "e181", "p18120")
    for d in (ds, dm):
        if os.path.exists(d):
            shutil.rmtree(d)
    shutil.copytree(os.path.join(src, smoke_rel), ds)
    # E181: A6-1's floor mark, F0 read from the smoke's first 3 s as run_e181.py reads it, first in the smoke's marks
    tel = [r for r in jl(os.path.join(ds, "telemetry.jsonl.gz"))]
    t_first = tel[0]["t_ms"]
    vals = []
    for r in tel:
        pv = r.get("pvt") or {}
        cs = pv.get("c") or []
        if r["t_ms"] < t_first + 3000 and pv.get("st") == 0 and len(cs) == 34 and not pv.get("f"):
            vals.append(sum((G_TS + H_TS * c / CAL5 - H_TS / 2) / 1000.0 for c in cs) / 34.0)
    f0 = sum(vals) / len(vals)
    sm = jl(os.path.join(ds, "marks.jsonl"))
    wjl(os.path.join(ds, "marks.jsonl"), [floor_mark(t_first + 3200, f0, stopped="f0-stopped" in faults)] + sm)
    os.makedirs(dm)
    for fn in os.listdir(os.path.join(src, meas_rel)):
        if fn in ("marks.jsonl", "runs.jsonl"):
            continue
        shutil.copy2(os.path.join(src, meas_rel, fn), dm)
    marks = []
    for m in jl(os.path.join(src, meas_rel, "marks.jsonl")):
        if m.get("kind") == "start_gate":
            continue
        for key in ("name", "hold", "block"):
            if m.get(key) in REN:
                m[key] = REN[m[key]]
        marks.append(m)
        if m.get("kind") == "room" and not any(x.get("kind") == "start_gate" for x in marks):
            marks.append(gate_marks(m["t_ms"], m.get("mean34_c"), f0, refused="g0-refused" in faults))
    mm = apply_marks(marks, nolaunch="measured-nolaunch" in faults, norecords="no-records" in faults)
    if "dup-start" in faults:
        mm = dup(mm)
    wjl(os.path.join(dm, "marks.jsonl"), mm)
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
    if "f0-stopped" in faults:
        shutil.rmtree(dm)
    os.makedirs(os.path.join(bld, "e181"), exist_ok=True)
    with open(os.path.join(bld, "e181", "session.log"), "w") as f:
        f.write("2026-11-06 09:00:00 PST session start (desk test)\n2026-11-06 10:15:00 PST pass 18120 rc=0\n"
                "2026-11-06 10:15:30 PST session end\n")
    print(f"stand-in box passes from {os.path.basename(os.path.normpath(src))} ({s_name} -> p18101, {m_name} -> p18120, M11's names; "
          f"F0 {f0:.3f} C) -> {os.path.relpath(bld, out)}; faults {sorted(faults) or 'none'}")


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
