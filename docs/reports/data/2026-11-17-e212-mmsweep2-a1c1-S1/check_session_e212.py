#!/usr/bin/env python3
"""data-e212 (Q208, Tue 17 Nov 2026): the lab's own check of one released E212 (1117-mmsweep2) session directory. It is Q200
data-e208's check_session.py (committed as check_session_e208.py with E208's sessions, sha256 77118c69...), unchanged in C0-C8 but for
these names and one added check, C9 (the claim's power line for the card: every scheduled run's and smoke process's planning peak
est_peak_w at or under the line the claims name, and the measured board peak reported against it). E212's kit is E208's kit unchanged
in behaviour (its runner, reducer and stop lines differ from E208's registered copies only in the kit's name), so C0-C8 read the same
records the same way. Reads only (the session copy in work/, the src copy in work/); imports nothing from the kit. Python's own
modules only.

    /usr/bin/python3 -I -B check_session_e212.py <session dir> <card a2c0|a1c1|a1c0> <src dir> --out checks.json --txt checks.txt

Checks (each PASS / FAIL / NOTE, with its numbers):
  C0 the src: the schedule's sha256 (session.log's first line, queue.json) against src/SRC-SHA256SUMS; harness.txt's line
  C1 a clean end: runner.rc 0; the log's last line 'session end'; status closing 'ended', runs_done = runs_total = runs_ran;
     stop null; queue.json n_ran, stop, leftover
  C2 the runs: against the schedule (order, arm, form, role); every process's rc (0); processes per form (burst 1, sus3 3, null 0);
     launches_ok, check_ok, not stopped by file; flags
  C3 the identity: config reads and the sampler on the card's own management node only; et-who with the sampler: nobody else;
     every host process (smoke and runs): its stderr's device blocks (exactly one, the card's own ops node and physical ID), the
     runner's own watch record (right, nothing wrong, no trip); the config start = end, at the card's registered start config
  C4 the clock: mhz.minion in every telemetry sample (histogram; inside the processes' windows too); every counted launch's kernel
     clock (cycles_max / wall_s) by band
  C5 the stops: status/queue stop null; the stop-path test (its own test lines); the real lines replayed on every sample (board
     strictly above the cap on N samples in a row; the shires' mean at or above the absolute line; the latch's rise); maxima
  C6 the timeouts: every process rc not 124/137/143/-9/-15; no kill word in any log or record of the session
  C7 no leftover: status/queue leftover null; no leftover line; et-who at the close
  C8 the sampler's run: one start (attempt 1), no restart; its banner's node; coverage of the session and of every process window;
     gaps; slow reads
  C9 the claim's power line (E212): every scheduled run's and smoke arm's est_peak_w at or under plan_w (aifoundry1 card 0: 52 W,
     "every arm at or under 52 W", #11 and #11.2; aifoundry1 card 1: 66.6 W, "card 1's runs are planned at or under 66.6 W", #11);
     the measured board peak reported against plan_w (a NOTE when above it: the claims name a planning line, and the live stop
     line, checked in C5, is the bound a measured sample must keep)
"""
import argparse
import bisect
import collections
import gzip
import hashlib
import json
import os
import re
import statistics
import sys

CARDS = {
    "a2c0": {"box": "aifoundry2", "n": "0", "governed": True, "config": {"tdp_w": [65], "temp_threshold_c": [65], "minion_mhz": [600],
                                                                       "power_state": [3]},
             "cap_w": 85.0, "need": 3, "abs_c": 80.0, "clocks": (600, 700, 800), "plan_w": None},
    "a1c1": {"box": "aifoundry1", "n": "1", "governed": False, "config": {"tdp_w": [65], "temp_threshold_c": [65], "minion_mhz": [600],
                                                                        "power_state": [1, 3]},
             "cap_w": 75.0, "need": 3, "abs_c": 80.0, "clocks": (600,), "plan_w": 66.6},
    "a1c0": {"box": "aifoundry1", "n": "0", "governed": True, "config": {"tdp_w": [65], "temp_threshold_c": [65], "minion_mhz": [600],
                                                                       "power_state": [3]},
             "cap_w": 65.0, "need": 3, "abs_c": 80.0, "clocks": (600, 700, 800), "under_w": 65.0, "plan_w": 52.0},
}
NPROC = {"burst": 1, "sus3": 3, "null": 0}
KILL_RE = re.compile(r"sigkill|\bkill(ed|s)?\b|timeout -k|\s-k\s+\d|signal 9|outlived|leftover", re.I)
BANDS = {"800": (790.0, 810.0), "700": (690.0, 710.0), "600": (590.0, 610.0)}


def load(p):
    with open(p) as f:
        return json.load(f)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sparsity(path):
    out = []
    if not os.path.exists(path):
        return out
    for ln in open(path, errors="replace"):
        if ln.startswith("SPARSITY "):
            try:
                out.append(json.loads(ln[9:]))
            except ValueError:
                out.append({"_bad": ln[:80]})
    return out


def dev_blocks(path):
    """(targets, ids) of every device block in a device layer's banner (stderr)."""
    t, i = [], []
    if not os.path.exists(path):
        return t, i
    for ln in open(path, errors="replace"):
        m = re.match(r"PCIe target:\s+(\S+)", ln)
        if m:
            t.append(m.group(1))
        m = re.match(r"Physical device ID:\s+(\d+)", ln)
        if m:
            i.append(m.group(1))
    return t, i


def band(L):
    w = L.get("wall_s") or 0
    if w <= 0:
        return None, None
    f = (L.get("cycles_max") or 0) / w / 1e6
    for b, (lo, hi) in BANDS.items():
        if lo <= f <= hi:
            return b, f
    return "other", f


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("card", choices=sorted(CARDS))
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    S, K, n = a.session, CARDS[a.card], CARDS[a.card]["n"]
    mgmt, ops = f"/dev/et{n}_mgmt", f"/dev/et{n}_ops"
    R = collections.OrderedDict()
    L = []

    def rec(key, verdict, **kw):
        R[key] = dict(verdict=verdict, **kw)
        L.append(f"{key} {verdict}: " + "; ".join(f"{k} {v}" for k, v in kw.items()))

    st = load(os.path.join(S, "status.json"))
    q = load(os.path.join(S, "queue.json"))
    log = open(os.path.join(S, "session.log"), errors="replace").read().splitlines()
    runner_rc = open(os.path.join(S, "runner.rc")).read().strip()
    same_log = open(os.path.join(S, "runner.out"), "rb").read() == open(os.path.join(S, "session.log"), "rb").read()

    # C0 the src
    sums = {}
    for ln in open(os.path.join(a.src, "SRC-SHA256SUMS")):
        h, p = ln.split()
        sums[p] = h
    m = re.search(r"schedule (\S+) sha256 ([0-9a-f]+);", log[0]) if log else None
    sched_name = q.get("sched")
    sched_full = sums.get(f"src/sched/{sched_name}")
    ok0 = bool(m) and m.group(1) == sched_name and sched_full is not None and sched_full.startswith(m.group(2)) \
        and q.get("sched_sha256") == sched_full and sha(os.path.join(a.src, "sched", sched_name)) == sched_full
    harness = open(os.path.join(S, "harness.txt")).read().strip()
    ok0 = ok0 and harness == f"HARNESS OK: {len(sums)} files at src/SRC-SHA256SUMS's sha256"
    rec("C0_src", "PASS" if ok0 else "FAIL", schedule=sched_name, schedule_sha256=q.get("sched_sha256"),
        log_prefix=(m.group(2) if m else None), src_listed=sched_full, harness=repr(harness),
        src_sums_sha256=sha(os.path.join(a.src, "SRC-SHA256SUMS")))

    # C1 the clean end
    last = log[-1] if log else ""
    ok1 = runner_rc == "0" and " session end (" in last and st.get("closing") == "ended" \
        and st.get("runs_done") == st.get("runs_total") == st.get("runs_ran") and st.get("stop") is None \
        and q.get("n_ran") == st.get("runs_ran") and q.get("stop") is None and q.get("leftover") is None and same_log
    rec("C1_clean_end", "PASS" if ok1 else "FAIL", runner_rc=runner_rc, last_line=repr(last[:120]),
        closing=st.get("closing"), runs=f"{st.get('runs_ran')}/{st.get('runs_done')}/{st.get('runs_total')} ran/done/total",
        card_min=st.get("card_min"), stop=st.get("stop"), queue_n_ran=q.get("n_ran"), runner_out_eq_session_log=same_log)

    # C2 the runs, against the schedule
    sched = load(os.path.join(a.src, "sched", sched_name))
    runs_dir = os.path.join(S, "runs")
    keys = sorted(os.listdir(runs_dir))
    runs = [load(os.path.join(runs_dir, k, "run.json")) for k in keys]
    bad = []
    nproc = rcs = 0
    rc_hist = collections.Counter()
    flags = collections.Counter()
    n_launch = 0
    proc_windows = []
    host_err_files = []
    launches = []
    for i, (k, r) in enumerate(zip(keys, runs)):
        s = sched["runs"][i] if i < len(sched["runs"]) else None
        if s is None or (s["arm"], s["form"], s["role"], s["i"]) != (r["arm"], r["form"], r["role"], r["i"]):
            bad.append(f"{k}: not the schedule's run {i + 1}")
        if r.get("sched") != s:
            bad.append(f"{k}: its sched record differs from the schedule's entry")
        if not r.get("ran"):
            bad.append(f"{k}: ran false")
        for fl in r.get("flags") or []:
            flags[str(fl)] += 1
        ps = r.get("procs") or []
        if len(ps) != NPROC[r["form"]]:
            bad.append(f"{k}: {len(ps)} processes for form {r['form']}")
        for p in ps:
            nproc += 1
            rc_hist[str(p.get("rc"))] += 1
            if p.get("rc") != 0:
                bad.append(f"{k}/{p.get('name')}: rc {p.get('rc')}")
            if not p.get("launches_ok") or not p.get("check_ok") or p.get("stopped_by_file"):
                bad.append(f"{k}/{p.get('name')}: launches_ok {p.get('launches_ok')} check_ok {p.get('check_ok')} "
                           f"stopped_by_file {p.get('stopped_by_file')}")
            n_launch += p.get("n_launch") or 0
            proc_windows.append((k, p.get("name"), p["t0_ms"], p["t1_ms"]))
            host_err_files.append((f"{k}/{p.get('name')}", os.path.join(runs_dir, k, p.get("name") + ".err"), p.get("ident") or {}))
            for Lx in sparsity(os.path.join(runs_dir, k, p.get("name") + ".out")):
                if Lx.get("test") == "fma" and (Lx.get("launch") if Lx.get("launch") is not None else -9) >= 0 and Lx.get("ok") \
                        and (Lx.get("wall_s") or 0) >= 0.1 and Lx.get("passes"):
                    launches.append((k, Lx))
    if len(runs) != len(sched["runs"]):
        bad.append(f"{len(runs)} run records against {len(sched['runs'])} scheduled")
    rec("C2_runs", "PASS" if not bad else "FAIL", run_records=len(runs), scheduled=len(sched["runs"]),
        forms=dict(collections.Counter(r["form"] for r in runs)), roles=dict(collections.Counter(r["role"] for r in runs)),
        processes=nproc, rc_hist=dict(rc_hist), launches_recorded=n_launch, counted_launches=len(launches),
        flags=dict(flags) or "none", problems=bad[:12] or "none")

    # C3 the identity
    idn = load(os.path.join(S, "identity.json"))
    bad = []
    for kk in ("config_start", "config_end"):
        c = idn.get(kk) or {}
        if c.get("ids") != [int(n)] or c.get("targets") != [mgmt] or c.get("why"):
            bad.append(f"{kk}: {c}")
    sn = idn.get("sampler_nodes") or {}
    if sn.get("nodes") != [mgmt] or sn.get("why"):
        bad.append(f"sampler_nodes: {sn}")
    ew = idn.get("etwho_with_sampler") or {}
    cnt = ew.get("counts") or {}
    if cnt.get("other_on_card") != 0 or cnt.get("other_off_card") != 0 or cnt.get("ours_off_card") != 0 or ew.get("why"):
        bad.append(f"etwho_with_sampler: {ew}")
    for f in ("config-start.err", "config-end.err", "sampler.err"):
        t, i = dev_blocks(os.path.join(S, f))
        if t != [mgmt] or i != [n]:
            bad.append(f"{f}: device blocks {t} {i}")
    sm_dir = os.path.join(S, "smoke")
    smoke_n = 0
    smoke_rc = collections.Counter()
    for arm in sorted(os.listdir(sm_dir)):
        smoke_n += 1
        sj = load(os.path.join(sm_dir, arm, "smoke.json"))
        host_err_files.append((f"smoke/{arm}", os.path.join(sm_dir, arm, "proc.err"), sj.get("host") or (sj.get("ident") or {})))
        smoke_rc[str(sj.get("rc"))] += 1
        if sj.get("rc") != 0 or not sj.get("launches_ok") or not sj.get("check_ok") or sj.get("stopped_by_file") \
                or sj.get("identity_ok") is not True or sj.get("good") is not True:
            bad.append(f"smoke/{arm}: rc {sj.get('rc')} launches_ok {sj.get('launches_ok')} check_ok {sj.get('check_ok')} "
                       f"identity_ok {sj.get('identity_ok')} good {sj.get('good')}")
    nb = 0
    for name, ef, ident in host_err_files:
        t, i = dev_blocks(ef)
        nb += 1
        if t != [ops] or i != [n]:
            bad.append(f"{name}: device blocks {t} {i}")
        if ident:
            if ident.get("stderr_targets") != [ops] or ident.get("stderr_ids") != [int(n)] or \
                    any(x != ops for x in ident.get("nodes_held") or []) or ident.get("wrong") or ident.get("right") is not True \
                    or ident.get("tripped"):
                bad.append(f"{name}: watch record {ident}")
        else:
            bad.append(f"{name}: no watch record")
    cs, ce = load(os.path.join(S, "config-start.json")), load(os.path.join(S, "config-end.json"))
    for kk, allowed in K["config"].items():
        if cs.get(kk) not in allowed:
            bad.append(f"config start {kk} {cs.get(kk)} not in {allowed}")
    if cs != ce:
        bad.append(f"config start {cs} != end {ce}")
    rec("C3_identity", "PASS" if not bad else "FAIL", card=f"{K['box']} card {n}", mgmt=mgmt, ops=ops,
        host_processes_checked=f"{nb} (smoke {smoke_n} + runs {nb - smoke_n})", smoke_rc=dict(smoke_rc), etwho_counts=cnt,
        config_start=cs, config_end_equal=(cs == ce), problems=bad[:12] or "none")

    # telemetry
    rows = []
    with gzip.open(os.path.join(S, "telemetry.jsonl.gz"), "rt") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except ValueError:
                rows.append({"_bad": ln[:60]})
    good = [x for x in rows if "t_ms" in x]
    ts_ = [x["t_ms"] for x in good]

    # C4 the clock
    clk = collections.Counter()
    clk_in = collections.Counter()
    no_clk = 0
    pw = sorted((w[2], w[3]) for w in proc_windows)
    starts_ = [w[0] for w in pw]
    for x in good:
        c = (x.get("mhz") or {}).get("minion")
        if c is None:
            no_clk += 1
            continue
        clk[c] += 1
        t = x["t_ms"]
        ii = bisect.bisect_right(starts_, t) - 1
        if ii >= 0 and pw[ii][0] <= t <= pw[ii][1]:
            clk_in[c] += 1
    lb = collections.Counter()
    lf = []
    for k, Lx in launches:
        b, f = band(Lx)
        lb[b] += 1
        if f is not None:
            lf.append(f)
    allowed = set(K["clocks"])
    off = {c: v for c, v in clk.items() if c not in allowed}
    ok4 = no_clk == 0 and not off and (K["governed"] or (set(clk) == {600} and set(lb) <= {"600"}))
    rec("C4_clock", "PASS" if ok4 else "FAIL", samples=len(good), samples_without_clock=no_clk,
        sample_mhz=dict(sorted(clk.items())), in_process_windows=dict(sorted(clk_in.items())),
        counted_launch_bands=dict(lb), launch_clock_mhz_min_max=(f"{min(lf):.1f}-{max(lf):.1f}" if lf else None),
        rule=("governed: 600/700/800 only" if K["governed"] else "600 MHz in every sample and every counted launch"))

    # C5 the stops
    sp = load(os.path.join(S, "stop-path.json"))
    over = trips = 0
    first_trip = None
    latch0 = None
    bmax = dmax = lmax = None
    over_cap = 0
    under_w_bad = 0
    for x in good:
        bw = x.get("board_w")
        ms = (x.get("temp_c") or {}).get("minshire") or []
        die = ms[0] if ms else None
        lat = ms[2] if len(ms) > 2 else None
        if lat is not None and latch0 is None:
            latch0 = lat
        if bw is not None:
            bmax = bw if bmax is None else max(bmax, bw)
            if bw > K["cap_w"]:
                over_cap += 1
            if K.get("under_w") is not None and bw >= K["under_w"]:
                under_w_bad += 1
        if die is not None:
            dmax = die if dmax is None else max(dmax, die)
        if lat is not None:
            lmax = lat if lmax is None else max(lmax, lat)
        trip = None
        if die is not None and die >= K["abs_c"]:
            trip = "die"
        elif lat is not None and latch0 is not None and lat > latch0 and lat >= K["abs_c"]:
            trip = "latch"
        elif bw is not None and bw > K["cap_w"]:
            over += 1
            if over >= K["need"]:
                trip = "board"
        else:
            over = 0
        if trip:
            trips += 1
            first_trip = first_trip or (trip, x["t_ms"])
    stop_lines = [ln for ln in log if re.search(r"\bstop", ln, re.I) and "stop-path test passed" not in ln]
    ok5 = st.get("stop") is None and q.get("stop") is None and sp.get("ok") is True and trips == 0 and not stop_lines \
        and (K.get("under_w") is None or under_w_bad == 0)
    rec("C5_stops", "PASS" if ok5 else "FAIL", status_stop=st.get("stop"), stop_path_test=sp.get("ok"),
        test_lines={k: (v.get("tripped"), v.get("s")) for k, v in (sp.get("lines") or {}).items()},
        real_lines=sp.get("real_lines"), replayed_trips=trips, first_trip=first_trip,
        board_max_w=bmax, samples_over_cap=over_cap, die_max_c=dmax, latch_first_max_c=(latch0, lmax),
        log_stop_lines=[x[24:140] for x in stop_lines][:6] or "none",
        **({"under_w": K["under_w"], "samples_at_or_over": under_w_bad} if K.get("under_w") else {}))

    # C6 the timeouts and kills
    bad_rc = {k: v for k, v in (rc_hist + smoke_rc).items() if k in ("124", "137", "143", "-9", "-15")}
    hits = []
    nfiles = 0
    for dirpath, dirs, files in os.walk(S):
        for fn in files:
            p = os.path.join(dirpath, fn)
            if fn.endswith(".gz"):
                continue
            nfiles += 1
            for ln_no, ln in enumerate(open(p, errors="replace"), 1):
                if KILL_RE.search(ln):
                    s_ = ln.strip()
                    if re.fullmatch(r'"leftover": null,?', s_):
                        continue
                    hits.append(f"{os.path.relpath(p, S)}:{ln_no}: {s_[:100]}")
    ok6 = not bad_rc and not hits
    rec("C6_timeouts", "PASS" if ok6 else "FAIL", process_rc_hist=dict(rc_hist), smoke_rc_hist=dict(smoke_rc),
        timeout_or_kill_rcs=bad_rc or "none",
        files_read=nfiles, kill_or_leftover_words=hits[:10] or "none")

    # C7 no leftover
    ec = open(os.path.join(S, "etwho-close.txt")).read().strip()
    lo_lines = [ln for ln in log if re.search(r"leftover", ln, re.I)]
    ok7 = st.get("leftover") is None and q.get("leftover") is None and not lo_lines and \
        ec == "no holder that blocks; no device process that blocks"
    rec("C7_no_leftover", "PASS" if ok7 else "FAIL", status_leftover=st.get("leftover"), queue_leftover=q.get("leftover"),
        log_leftover_lines=len(lo_lines), etwho_close=repr(ec))

    # C8 the sampler's run
    starts = [ln for ln in log if "sampler started" in ln]
    restarts = [ln for ln in log if re.search(r"sampler (re)?start|attempt [2-9]|sampler .*(died|ended|stopped|exit)", ln)
                and "attempt 1" not in ln]
    gaps = [(b - a_) for a_, b in zip(ts_, ts_[1:])]
    big = [g for g in gaps if g > 1000]
    slow = sum(1 for x in good if (x.get("took_ms") or 0) > 100)
    t_first, t_close = q.get("t_first_ms"), q.get("t_close_ms")
    unc = []
    for k, nm, a0, a1 in proc_windows:
        i0 = next((ii for ii, t in enumerate(ts_) if t >= a0), None)
        inside = [t for t in ts_ if a0 <= t <= a1]
        if len(inside) < max(1, int((a1 - a0) / 1000.0 * 5)):
            unc.append(f"{k}/{nm}: {len(inside)} samples in {(a1 - a0) / 1000:.1f} s")
        _ = i0
    ok8 = len(starts) == 1 and "attempt 1" in starts[0] and not restarts and not big and len(rows) == len(good) and not unc \
        and ts_ and ts_[0] <= (t_first or ts_[0]) + 1000 and (t_close is None or ts_[-1] >= t_close - 5000)
    rec("C8_sampler", "PASS" if ok8 else "FAIL", start_lines=len(starts), start=repr(starts[0][20:110]) if starts else None,
        restarts=len(restarts), samples=len(good), bad_lines=len(rows) - len(good),
        first_sample_vs_first_card_command_s=(round((ts_[0] - t_first) / 1000.0, 3) if ts_ and t_first else None),
        last_sample_vs_close_s=(round((ts_[-1] - t_close) / 1000.0, 3) if ts_ and t_close else None),
        span_min=(round((ts_[-1] - ts_[0]) / 60000.0, 2) if ts_ else None),
        median_interval_ms=(statistics.median(gaps) if gaps else None), gaps_over_1s=len(big),
        max_gap_ms=(max(gaps) if gaps else None), slow_reads_over_100ms=slow,
        process_windows_thin=unc[:6] or "none", sampler_err_device=dev_blocks(os.path.join(S, "sampler.err")))

    # C9 the claim's power line (planning) and the measured peak against it
    line = K.get("plan_w")
    line_src = "the claims' planning line" if line is not None else "the schedule's own line_w (no claim line set here)"
    if line is None:
        line = sched.get("line_w")
    peaks = [(r.get("arm"), r.get("est_peak_w")) for r in sched["runs"] if r.get("role") != "null"]
    peaks += [("smoke " + (s.get("arm") or "?"), s.get("est_peak_w")) for s in (sched.get("smoke") or [])]
    missing = [a_ for a_, p in peaks if p is None]
    over_plan = [f"{a_} {p}" for a_, p in peaks if p is not None and line is not None and p > line + 1e-9]
    pmax = max((p for _, p in peaks if p is not None), default=None)
    meas_over = None if (bmax is None or line is None) else bmax > line
    ok9 = line is not None and not missing and not over_plan
    rec("C9_power_plan", "PASS" if ok9 else "FAIL", line_w=line, line_from=line_src, schedule_line_w=sched.get("line_w"),
        planned_peaks_read=len(peaks), planned_peak_max_w=pmax, planned_over_line=over_plan[:8] or "none",
        planned_missing=missing[:8] or "none", measured_board_max_w=bmax,
        measured_vs_line=("NOTE: the measured board peak is above the planning line (the live stop line, C5, is the bound "
                          "a measured sample keeps)" if meas_over else "at or under the planning line"),
        live_stop_line_w=K["cap_w"])

    verdict = "ALL PASS" if all(v["verdict"] == "PASS" for v in R.values()) else \
        "FAIL: " + ", ".join(k for k, v in R.items() if v["verdict"] != "PASS")
    out = {"what": "data-e212's own check of one released E212 session (Q200's check_session.py with C9 added; reads only)",
           "session": os.path.basename(os.path.normpath(S)), "card": a.card, "checks": R, "verdict": verdict,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, default=str)
    L.append(f"VERDICT {verdict}")
    with open(a.txt, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
