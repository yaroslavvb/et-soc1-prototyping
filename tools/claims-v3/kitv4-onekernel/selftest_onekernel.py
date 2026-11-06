#!/usr/bin/env python3
"""The desk test of kit v4's one-kernel option. No card, no device, no ssh.

    python3 selftest_onekernel.py                              the unit checks (T1-T5)
    python3 selftest_onekernel.py --dry <v3 rundir> <v4 rundir>   T6-T8 on drypass_onekernel.sh's two dry sessions

T1 the iterations finish under the host's 6 s launch timeout at 600 MHz, for every format; the wall at the cap after a climb
T2 command() turns a v3 burst command (E173's committed launch record's flags) into one kernel, and refuses what it must
T3 install() refuses a run_hpl that is not the committed file, and leaves heater and gate launches to the original method
T4 the v3 drivers are untouched: every file of E173's, E174's and E175's harness lists (harness-e17x.json, the files their
   box steps check before a launch) hashes as listed, and run_hpl.py is the committed file
T5 the dip term (tools/claims-v3/dipterm) on a synthetic one-kernel session: no eligible gap, DT-N's band [0, 0]
T6 the dry pass: every v4 work process has one SPARSITY line (launch -1, iters N) and no gap inside its burst window; the v3
   form on the same protocol has 12 or more launches and gaps
T7 the reduction on the dry v4 session: reduce_hpl.run_metrics and burst_extra_v4: burst_mhz and burst_w as before, burst_rate
   and burst_ghz_kernel None (no launch starts 1.5 s in), the window's rate from the sampled clock beside
T8 the dip term's exposure on both dry sessions: 0 eligible gaps for v4
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import onekernel as OK  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    yield json.loads(ln)
                except ValueError:
                    pass


def unit():
    res = {}
    # T1
    t1 = {}
    ok = True
    for t in ("fp32", "fp16", "int8"):
        n = OK.iters_for(t)
        w600 = n * OK.CPO[t] / 600e6
        w_late = OK.wall_at(t, n, first_beat_s=1.0)
        w_mid = OK.wall_at(t, n, first_beat_s=0.5)
        t1[t] = {"iters": n, "cycles": int(n * OK.CPO[t]), "wall_at_600_s": round(w600, 3), "wall_cap_first_beat_0.5_s": round(w_mid, 3),
                 "wall_cap_first_beat_1.0_s": round(w_late, 3), "window_s_at_cap": round(w_mid - 1.5 + 0.15, 3)}
        ok &= w600 <= OK.T600_S + 1e-9 and w600 < OK.HOST_TIMEOUT_S - 0.4
    try:
        OK.iters_for("fp32", 6.0)
        ok = False
    except ValueError:
        pass
    t1["ok"] = ok
    res["T1_sizing"] = t1
    # T2: E173's first committed work launch, its flags kept and its paths masked
    p = os.path.join(ROOT, "docs/reports/data/2026-11-05-e173-blind8-aifoundry2/aifoundry2/s1/launches.jsonl.gz")
    v3 = next(r for r in jl(p) if r.get("role") == "work")["cmd"]
    v3m = [("<path>" + os.path.basename(x)) if x.startswith("/") else x for x in v3]
    v4 = OK.command(v3m, "fp32")
    refused = []
    for bad in (v3m + ["--iters", "5"], [x for x in v3m if x != "--stop-file"], v3m):
        try:
            OK.command(bad, "fp16" if bad is v3m else "fp32")
            refused.append(False)
        except ValueError:
            refused.append(True)
    i = v4.index("--seconds")
    res["T2_command"] = {"v3_flags": " ".join(v3m[2:]), "v4_flags": " ".join(v4[2:]),
                         "ok": v4[i + 1] == "0" and v4[i + 2] == "--iters" and int(v4[i + 3]) == OK.iters_for("fp32")
                         and len(v4) == len(v3m) + 2 and all(refused), "refused_three_bad_commands": refused}
    # T3: install() on a stand-in module refuses; the original is kept for heater calls (checked on the real module in T6)
    fake = types.SimpleNamespace(__file__=os.path.join(HERE, "onekernel.py"), Session=type("S", (), {"spawn_kernel": lambda *a, **k: None}))
    try:
        OK.install(fake)
        r3 = False
    except RuntimeError:
        r3 = True
    res["T3_install_refuses_other_runner"] = {"ok": r3}
    # T4: the v3 drivers untouched
    t4, ok4 = {}, True
    for kit in ("e173", "e174", "e175"):
        fj = os.path.join(ROOT, "tools/claims-v3", kit, f"harness-{kit}.json")
        d = json.load(open(fj))
        files = d.get("files_sha256") or {}
        n = bad = 0
        for rel, h in (files.items() if isinstance(files, dict) else []):
            if not isinstance(h, str) or len(h) != 64:
                continue
            ap = os.path.join(ROOT, rel)
            if not os.path.isfile(ap):
                continue
            n += 1
            bad += sha(ap) != h
        t4[kit] = {"files_checked": n, "mismatched": bad}
        ok4 &= n > 0 and bad == 0
    t4["run_hpl.py"] = sha(os.path.join(ROOT, "tools/claims-v3/hpl/run_hpl.py")) == OK.RUN_HPL_SHA256
    t4["ok"] = ok4 and t4["run_hpl.py"]
    res["T4_v3_untouched"] = t4
    # T5: the dip term on a synthetic one-kernel session
    sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/dipterm"))
    import dipterm as DT  # noqa: E402
    procs, _, _ = DT._synth("a2", 30, 77, "chain", one_kernel=True)
    c = DT.count_rule(procs, "a2")
    res["T5_dipterm_one_kernel"] = {"eligible_gaps": c["eligible_gaps"], "band": c["band_95"], "ok": c["eligible_gaps"] == 0 and c["band_95"] == [0, 0]}
    return res


def dry(v3dir, v4dir):
    res = {}
    rows = {}
    for tag, d in (("v3", v3dir), ("v4", v4dir)):
        procs = [r for r in jl(os.path.join(d, "launches.jsonl")) if r.get("role") == "work"]
        per = []
        for p in procs:
            L = sorted(p.get("sparsity", []), key=lambda k: k["t_start_ms"])
            w0 = p["t_start_ms"] + 1500
            gaps = [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(L, L[1:])]
            gw = [g for (a, b), g in zip(zip(L, L[1:]), gaps) if b["t_start_ms"] > w0]
            per.append({"run": p["run"], "launches": len(L), "launch_numbers": sorted({k.get("launch") for k in L}),
                        "iters": sorted({k.get("iters") for k in L}), "gaps": len(gaps), "gaps_in_window": len(gw),
                        "wall_s": round(sum(k.get("wall_s", 0) for k in L), 3), "process_s": round((p["t_end_ms"] - p["t_start_ms"]) / 1000.0, 3),
                        "ok": all(k.get("ok") for k in L), "rc": p.get("rc")})
        rows[tag] = per
    v4ok = all(x["launches"] == 1 and x["launch_numbers"] == [-1] and x["gaps"] == 0 and x["ok"] and x["rc"] == 0 for x in rows["v4"])
    v3ok = all(x["launches"] >= 12 and x["gaps_in_window"] >= 6 for x in rows["v3"])
    res["T6_launch_records"] = {"v3": rows["v3"], "v4": rows["v4"], "ok": v4ok and v3ok and len(rows["v4"]) == len(rows["v3"]) > 0}
    # T7: the reduction
    sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/hpl"))
    sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kspeed"))
    import reduce_hpl as R  # noqa: E402
    import reduce_kspeed as RK  # noqa: E402
    B = {600: 25.419081832471313, 700: 28.272082443537354, 800: 33.613874697546834}   # m9_a2.json's busy levels (c_w only)
    t7 = {}
    ok7 = True
    for tag, d in (("v3", v3dir), ("v4", v4dir)):
        sess, runs, launches, q0 = R.load_session(d)
        runs = list(runs)
        launches = list(launches)
        out = []
        for r in runs:
            procs = [p for p in launches if p.get("run") == r["run"]]
            m = R.run_metrics(d, r, procs, None, None)
            x = OK.burst_extra_v4(m, procs, B, RK)
            out.append({"run": r["run"], **{k: x.get(k) for k in ("burst_mhz", "burst_w", "burst_n", "burst_rate", "burst_ghz_kernel",
                                                                  "v4_one_kernel", "v4_launches_in_window", "v4_gaps_in_window",
                                                                  "v4_burst_rate_from_clock", "v4_whole_kernel_ghz", "v4_work_s")}})
        t7[tag] = out
        if tag == "v4":
            ok7 &= all(o["burst_mhz"] is not None and o["burst_rate"] is None and o["burst_ghz_kernel"] is None
                       and o["v4_one_kernel"] and o["v4_gaps_in_window"] == 0 and o["v4_burst_rate_from_clock"] for o in out)
        else:
            ok7 &= all(o["burst_rate"] is not None and not o["v4_one_kernel"] for o in out)
    t7["ok"] = ok7
    res["T7_reduction"] = t7
    # T8: the dip term's exposure
    sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/dipterm"))
    import dipterm as DT  # noqa: E402
    t8 = {}
    for tag, d in (("v3", v3dir), ("v4", v4dir)):
        procs = []
        for r in jl(os.path.join(d, "launches.jsonl")):
            if r.get("role") != "work":
                continue
            L = sorted(((int(k.get("launch", 0)), int(k["t_start_ms"]), int(k["t_end_ms"]), float(k.get("ghz") or 0))
                        for k in r.get("sparsity", [])), key=lambda x: x[1])
            procs.append({"run": r["run"], "t0": r["t_start_ms"], "t1": r["t_end_ms"], "launches": L})
        c = DT.count_rule(procs, "a2")
        t8[tag] = {"eligible_gaps": c["eligible_gaps"], "expected": c["expected"], "band": c["band_95"]}
    t8["ok"] = t8["v4"]["eligible_gaps"] == 0 and t8["v3"]["eligible_gaps"] > 0
    res["T8_dipterm_exposure"] = t8
    return res


def main():
    if "--dry" in sys.argv:
        i = sys.argv.index("--dry")
        r = dry(sys.argv[i + 1], sys.argv[i + 2])
    else:
        r = unit()
    r["ok"] = all(v.get("ok", True) for v in r.values() if isinstance(v, dict))
    print(json.dumps(r, indent=1, sort_keys=True))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
