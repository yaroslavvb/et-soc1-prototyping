#!/usr/bin/env python3
"""data-e212s3 (Q223, Wed 18 Nov 2026): the lab's checks R of E212's re-run of aifoundry2 card 0's S3 (the session's first try was cut by
the box's reboot on Tue 17 Nov; the owner asked for it again, #11.13). These add to the checks Q208's lane ran on every E212 session
(C0-C9, W, P, B, the law test, the time re-derivation), for what is new in this session. Reads only; Python's own modules.

    /usr/bin/python3 -I -B rerun_e212s3.py <session dir> <registered src dir> --as-run-sums <EE's SRC-SHA256SUMS as run> \
        --as-run-build <EE's build_mms.sh as run> --record <EE's build record as read after the release> \
        --record-tue <Tuesday's committed build record> --binaries <EE build dir> --history <dir of the box's live history> \
        --meta <meta json> --cut <the first try's folder (stat only)> --out r.json --txt r.txt

  R1 the source as run: the kit's own list (SRC-SHA256SUMS as the session's harness read it) against the registered list: every entry
     equal but the builder's, src/build_mms.sh; the builder's change is only its job count (-j2 -> -j1 in its two cmake --build lines),
     its comments and the build record's added "jobs" field (both files compared with those three things normalised away); so no file
     the session runs (the runner, its constants, the identity and stop code, the host's source, the schedule, the tiles) differs
  R2 the host as built: the build record read after the release (day, BUILT, box, jobs) names the same host, kernel ELF and reader
     sha256 as Tuesday's committed record; the kernel ELF at E136's pin; the binaries in the kit hash to them and were last written
     before the session's T0; the runner's own box check passed (session.log line 3)
  R3 the freeze lines before the first card command: post #11 (E212's registration, 4d77f137...), #11.7.1 (8f2df483..., covering S3),
     #11.13.1.1.1 (6842eca5..., S3's re-run alone, registered fcbf60c4), #11.13.1.1.1.1.1 (0dca417d..., S3's re-run alone, registered
     d8dc4897) and MM1-v3's land (b1493082, its S3 forecasts frozen in it)
  R4 the host-load guard as claimed ("starting only at a host load under 6 and stopped at its next launch if the load reaches 6",
     #11.13): what the session's own records say (every line naming the load or an operator's stop in session.log, runner.out, the
     start output when given), and the box's own load history (the lab's 5 s watcher, a record outside the session): the 1-minute load
     at T0 and at every run's first process start (the last history entry at or before it), its maximum over the session
  R5 the first try: its folder is not this session's and was not opened (stat only); its directory entry is older than this T0
"""
import argparse
import datetime
import glob
import gzip
import hashlib
import json
import os
import re
import sys
import zoneinfo

TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
UTC = datetime.timezone.utc
FREEZE = [  # (name, post or commit, UTC time of the post or the commit, sha256 or commit)
    ("E212's registration post", "#11", "2026-11-17T13:22:43.963Z", "4d77f137293ef5bc8b34f1d3bde2b7104ec2493567f4fc854266cb3a769bd1e5"),
    ("the second seal (v3.2), covering S3", "#11.7.1", "2026-11-17T20:58:15.310Z", "8f2df48375701d3b6304e233d3d8c09e2ba9ee85ef431c9faabdc258094d010d"),
    ("the third seal (v3.3), S3's re-run alone; registered fcbf60c4", "#11.13.1.1.1", "2026-11-18T21:55:50.248Z",
     "6842eca51a6ee491d3e05deeb3f6477d395b887c9339a88463aa9fc096f038e0"),
    ("the fourth seal (v3.4), S3's re-run alone; registered d8dc4897", "#11.13.1.1.1.1.1", "2026-11-18T22:55:50.074Z",
     "0dca417d11b856c7aa4167107222fda459c2790614829235f3ee1182825de1a9"),
    ("MM1-v3's land (the lab's S3 forecasts frozen in it), commit time", "b1493082", "2026-11-18T04:52:46.000Z",
     "b149308280a73396516937304037af57a5563c16"),
]
LOAD_LINE = 6.0


def ms_utc(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC).timestamp() * 1000.0


def pst(ms, f="%H:%M:%S.%f"):
    s = datetime.datetime.fromtimestamp(ms / 1000.0, TZ).strftime(f)
    return s[:-3] if f.endswith("%f") else s


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sums(p):
    return dict((ln.split()[1], ln.split()[0]) for ln in open(p) if ln.strip())


def norm_builder(text):
    """the builder with its job count, its comments and the record's 'jobs' field normalised away"""
    out = []
    for ln in text.splitlines():
        if ln.lstrip().startswith("#"):
            continue
        ln = re.sub(r"-j[0-9]+\b", "-jN", ln)
        ln = ln.replace('"jobs": 1, ', "")
        out.append(ln.rstrip())
    joined = "\n".join(out)
    return re.sub(r",\s*\n\s*open\(", ", open(", joined)  # the record's dump call, split over two lines in the new file


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("src")
    ap.add_argument("--as-run-sums", required=True)
    ap.add_argument("--as-run-build", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--record-tue", required=True)
    ap.add_argument("--binaries", default=None)
    ap.add_argument("--history", default=None, help="the box's daily history folder, or an extract file")
    ap.add_argument("--write-extract", default=None, help="write the history entries of the span (t, load, cpu) here")
    ap.add_argument("--start-out", default=None)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--cut", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    S = a.session
    q = json.load(open(os.path.join(S, "queue.json")))
    log = open(os.path.join(S, "session.log"), errors="replace").read().splitlines()
    t0, first, close = q["t0"] * 1000.0, q["t_first_ms"], q["t_close_ms"]
    R, L = {}, []

    def rec(k, verdict, **kw):
        R[k] = dict(verdict=verdict, **kw)
        L.append(f"{k} {verdict}: " + "; ".join(f"{x} {y}" for x, y in kw.items()))

    # R1 the source as run
    reg, run = sums(os.path.join(a.src, "SRC-SHA256SUMS")), sums(a.as_run_sums)
    differ = sorted(k for k in set(reg) | set(run) if reg.get(k) != run.get(k))
    b_reg = open(os.path.join(a.src, "build_mms.sh")).read()
    b_run = open(a.as_run_build).read()
    b_sha_ok = sha(a.as_run_build) == run.get("src/build_mms.sh")
    same_norm = norm_builder(b_reg) == norm_builder(b_run)
    j_reg = re.findall(r"cmake --build \S+ -j([0-9]+)", b_reg)
    j_run = re.findall(r"cmake --build \S+ -j([0-9]+)", b_run)
    harness = open(os.path.join(S, "harness.txt")).read().strip()
    ok1 = (differ == ["src/build_mms.sh"] and len(reg) == len(run) and b_sha_ok and same_norm and j_reg == ["2", "2"]
           and j_run == ["1", "1"] and harness == f"HARNESS OK: {len(run)} files at src/SRC-SHA256SUMS's sha256")
    rec("R1_source_as_run", "PASS" if ok1 else "FAIL", entries=f"{len(run)} as run, {len(reg)} registered",
        equal=len([k for k in run if reg.get(k) == run[k]]), differ=differ,
        builder_sha256=f"registered {reg.get('src/build_mms.sh', '')[:16]}..., as run {run.get('src/build_mms.sh', '')[:16]}...",
        builder_as_run_hashes_to_its_list_entry=b_sha_ok, builder_jobs=f"registered -j{','.join(j_reg)}; as run -j{','.join(j_run)}",
        builder_equal_once_jobs_comments_and_record_field_normalised=same_norm,
        as_run_list_sha256=sha(a.as_run_sums), registered_list_sha256=sha(os.path.join(a.src, "SRC-SHA256SUMS")),
        session_harness=repr(harness))

    # R2 the host as built
    r_now, r_tue = json.load(open(a.record)), json.load(open(a.record_tue))
    keys = ("host_sha256", "kernel_sha256", "ettelem_sha256", "kernel_text_sha256")
    same3 = all(r_now.get(k) == r_tue.get(k) for k in keys)
    rec_day = r_now.get("day")
    day_t0 = datetime.datetime.fromtimestamp(q["t0"], TZ).strftime("%Y-%m-%d")
    bins = {}
    if a.binaries:
        for name, rel in (("host", "rgm/host/sparsity_host"), ("kernel", "rgm/kernel/sparsity.elf"), ("reader", "ettelem/ettelem")):
            p = os.path.join(a.binaries, rel)
            st = os.stat(p)
            bins[name] = {"sha256": sha(p), "mtime_pst": pst(st.st_mtime * 1000.0, "%a %d %b %H:%M:%S.%f"),
                          "before_t0": st.st_mtime * 1000.0 < t0}
    bin_ok = (not bins) or (bins["host"]["sha256"] == r_now.get("host_sha256") and bins["kernel"]["sha256"] == r_now.get("kernel_sha256")
                            and bins["reader"]["sha256"] == r_now.get("ettelem_sha256") and all(v["before_t0"] for v in bins.values()))
    box_line = next((ln for ln in log[:6] if "the box and the build:" in ln), None)
    ok2 = (same3 and r_now.get("verdict") == "BUILT" and r_now.get("box") == "aifoundry2" and rec_day == day_t0
           and r_now.get("kernel_sha256") == r_now.get("kernel_pin") and bin_ok and box_line is not None)
    rec("R2_host_as_built", "PASS" if ok2 else "FAIL",
        record=f"day {rec_day}, {r_now.get('verdict')}, box {r_now.get('box')}, jobs {r_now.get('jobs')}, epoch {r_now.get('epoch')} "
               f"({pst(r_now.get('epoch', 0) * 1000.0, '%a %d %b %H:%M:%S')} PST)",
        host_sha256=r_now.get("host_sha256"), kernel_sha256=r_now.get("kernel_sha256"), reader_sha256=r_now.get("ettelem_sha256"),
        equal_to_tuesdays_record=same3, tuesdays_record=f"day {r_tue.get('day')}, epoch {r_tue.get('epoch')}",
        kernel_at_e136_pin=(r_now.get("kernel_sha256") == r_now.get("kernel_pin")), record_day_is_the_sessions=(rec_day == day_t0),
        binaries=bins or "not read", runner_box_check=repr((box_line or "ABSENT")[24:200]))

    # R3 the freeze lines
    rows, ok3 = [], True
    for name, post, when, h in FREEZE:
        m = ms_utc(when)
        lead = (first - m) / 60000.0
        ok3 = ok3 and m < first
        rows.append(f"{post} {pst(m, '%a %H:%M:%S.%f')} PST ({name}; {h[:16]}...): {lead:.2f} min before the first card command")
    rec("R3_freeze_lines_first", "PASS" if ok3 else "FAIL", first_card_command=f"{pst(first, '%a %H:%M:%S.%f')} PST", lines=rows)

    # R4 the host-load guard
    texts = {"session.log": log, "runner.out": open(os.path.join(S, "runner.out"), errors="replace").read().splitlines()}
    if a.start_out and os.path.exists(a.start_out):
        texts["start.out (beside the folder)"] = open(a.start_out, errors="replace").read().splitlines()
    load_lines = {k: [ln[:220] for ln in v if re.search(r"\bload", ln, re.I)] for k, v in texts.items()}
    op_stop = [ln[:200] for ln in log if re.search(r"operator|STOP file", ln)]
    hist = []
    if a.history:
        if os.path.isfile(a.history):  # an extract (one JSON object a line: t, load, cpu), as committed beside the data
            files = [a.history]
        else:  # the box's daily files, named by their UTC day
            days = sorted({datetime.datetime.fromtimestamp(x / 1000.0, UTC).strftime("%Y-%m-%d") for x in (t0 - 300000, close + 120000)})
            files = [os.path.join(a.history, d + ".jsonl") for d in days if os.path.exists(os.path.join(a.history, d + ".jsonl"))]
        for p in files:
            for ln in open(p, errors="replace"):
                try:
                    x = json.loads(ln)
                except ValueError:
                    continue
                if isinstance(x, dict) and "t" in x and t0 - 300000 <= x["t"] <= close + 120000:
                    hist.append((x["t"], x.get("load"), x.get("cpu")))
    hist.sort()
    if a.write_extract:
        with open(a.write_extract, "w") as f:
            for t, ld, cpu in hist:
                f.write(json.dumps({"t": t, "load": ld, "cpu": cpu}) + "\n")

    def at(tms):
        best = None
        for t, ld, cpu in hist:
            if t <= tms:
                best = (t, ld, cpu)
            else:
                break
        return best

    starts = []
    for k in sorted(os.listdir(os.path.join(S, "runs"))):
        rj = json.load(open(os.path.join(S, "runs", k, "run.json")))
        ps = [p["t0_ms"] for p in rj.get("procs") or [] if p.get("t0_ms")]
        if ps:
            starts.append((k, min(ps)))
    for arm in sorted(os.listdir(os.path.join(S, "smoke"))):
        sj = json.load(open(os.path.join(S, "smoke", arm, "smoke.json")))
        if sj.get("t0_ms"):
            starts.append(("smoke/" + arm, sj["t0_ms"]))
    per = []
    for k, tms in starts:
        h = at(tms)
        per.append((k, tms, h[1] if h else None, (tms - h[0]) / 1000.0 if h else None))
    in_sess = [ld for t, ld, cpu in hist if t0 <= t <= close and ld is not None]
    top = max(((ld, t) for t, ld, cpu in hist if t0 <= t <= close and ld is not None), default=None)
    h0, hf = at(t0), at(first)
    per.sort(key=lambda x: x[1])
    over = [f"{k} {pst(tms)} load {ld}" for k, tms, ld, age in per if ld is not None and ld >= LOAD_LINE]
    known = [ld for _, _, ld, _ in per if ld is not None]
    first_over_ms = next((t for t, ld, cpu in hist if t0 <= t <= close and ld is not None and ld >= LOAD_LINE), None)
    starts_after_over = [k for k, tms, ld, age in per if first_over_ms is not None and tms > first_over_ms]
    st_ = json.load(open(os.path.join(S, "status.json")))
    if not hist:
        v4, how = "NOT ANSWERABLE", "no history entry in the session's span"
    elif not (h0 and h0[1] is not None and h0[1] < LOAD_LINE):
        v4, how = "FAIL", "the load at T0 was not under 6 (or unread)"
    elif first_over_ms is None:
        v4, how = "PASS", "the load stayed under 6 through the session: the guard had nothing to stop"
    elif not starts_after_over or (len(starts_after_over) == 1 and st_.get("stop")):
        v4, how = "PASS", "the load reached 6 and the session stopped at or before its next process start"
    else:
        v4, how = "FAIL", f"the load reached 6 at {pst(first_over_ms)} and {len(starts_after_over)} process starts followed"
    rec("R4_host_load_guard", v4, reading=how,
        first_history_entry_at_or_over_6=(pst(first_over_ms) if first_over_ms else "none"),
        claim=("#11.13: 'starting only at a host load under 6 and stopped at its next launch if the load reaches 6'"),
        session_records_naming_the_load={k: (v or "none") for k, v in load_lines.items()},
        operator_stop_lines=op_stop or "none",
        history="the box's own 5 s load history (the lab's watcher, outside the session): 1-minute load average",
        history_entries_in_span=len(hist),
        load_at_t0=(f"{h0[1]} at {pst(h0[0])} ({(t0 - h0[0]) / 1000.0:.1f} s before T0)" if h0 else None),
        load_at_first_card_command=(f"{hf[1]} at {pst(hf[0])}" if hf else None),
        load_max_in_session=(max(in_sess) if in_sess else None), load_max_at=(pst(top[1]) if top else None),
        load_min_in_session=(min(in_sess) if in_sess else None),
        process_starts_read=len(per), starts_with_a_history_entry=len(known),
        load_at_process_starts_max=(max(known) if known else None), starts_at_or_over_6=over or "none",
        oldest_entry_used_s=(max(age for *_, age in per if age is not None) if known else None))

    # R5 the first try
    if a.cut:
        st = os.stat(a.cut)
        cut_name = os.path.basename(os.path.normpath(a.cut))
        this = f"{q['t0']}-{q['sched'][:-5]}"
        ok5 = cut_name != this and st.st_mtime * 1000.0 < t0
        rec("R5_first_try_left", "PASS" if ok5 else "FAIL", first_try=cut_name, this_session=this,
            first_try_entry_mtime=pst(st.st_mtime * 1000.0, "%a %d %b %H:%M:%S.%f"), opened="no (stat of its directory entry only)")
    verdict = "ALL PASS" if all(v["verdict"] == "PASS" for v in R.values()) else \
        "NOT ALL PASS: " + ", ".join(f"{k} {v['verdict']}" for k, v in R.items() if v["verdict"] != "PASS")
    L.append(f"VERDICT {verdict}")
    out = {"what": "data-e212s3's checks R of E212's re-run of a2c0-S3 (reads only)", "session": f"{q['t0']}-{q['sched'][:-5]}",
           "checks": R, "verdict": verdict, "load_at_starts": [{"start": k, "t_ms": t, "load": ld, "entry_age_s": age}
                                                               for k, t, ld, age in per],
           "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    with open(a.txt, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
