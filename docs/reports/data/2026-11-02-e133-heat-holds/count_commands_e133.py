#!/usr/bin/env python3
"""E133: every device command the session sent, counted from the collected records (desk only, read-only). Each sample row is one round of
the sampler's six GETs; each config read is five GETs; sptrace is a driver ioctl and MMIO read; a residency line in e133-not-sent.jsonl was never sent.
usage: count_commands.py <data dir>   (prints a JSON summary and a table)"""
import glob, gzip, json, os, sys

d = sys.argv[1]
steps = [s for s in ("SMOKE", "W2", "END", "W1B", "END2", "W3") if os.path.isdir(os.path.join(d, s))]
tot = {"sample_rows": 0, "sampler_processes": 0, "config_in_runs": 0, "sptrace": 0, "residency_not_sent": 0, "residency_sent": 0,
       "config_snapshots": 0, "config_snapshot_attempts": 0, "drains": 0, "launch_processes": 0, "reset": 0}
rows = []
for s in steps:
    p = os.path.join(d, s)
    n_tel = 0
    for f in glob.glob(os.path.join(p, "tel", "*.jsonl*")):
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            n_tel += sum(1 for ln in fh if ln.strip())
    q = [json.loads(l) for l in open(os.path.join(p, "queries.jsonl")) if l.strip()] if os.path.exists(os.path.join(p, "queries.jsonl")) else []
    rj = os.path.join(p, "runs.jsonl")
    for ln in (open(rj) if os.path.exists(rj) else []):
        if ln.strip():
            rq = json.loads(ln).get("queries")
            if isinstance(rq, dict):
                q.append(rq)
    cfg = sum(1 for x in q if x.get("config_rc") is not None)
    spt = sum(1 for x in q if x.get("sptrace_rc") is not None)
    res_sent = sum(1 for x in q if x.get("residency_rc") is not None)
    ns = sum(1 for l in open(os.path.join(p, "e133-not-sent.jsonl")) if l.strip()) if os.path.exists(os.path.join(p, "e133-not-sent.jsonl")) else 0
    marks = [json.loads(l) for l in open(os.path.join(p, "marks.jsonl")) if l.strip()] if os.path.exists(os.path.join(p, "marks.jsonl")) else []
    samp = sum(1 for m in marks if m.get("kind") == "sampler_start")
    drains = sum(1 for m in marks if "drain" in str(m.get("kind", "")) or "drain" in str(m.get("detail", "")))
    snaps, att = 0, 0
    for tag in ("start", "end"):
        f = os.path.join(p, f"snapshot-{tag}.json")
        if os.path.exists(f):
            sj = json.load(open(f))
            snaps += 1
            att += int(sj.get("config_attempts") or 0)
    lf = [f for f in (os.path.join(p, "launches.jsonl"), os.path.join(p, "launches.jsonl.gz")) if os.path.exists(f)]
    nl = 0
    for f in lf:
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            nl += sum(1 for ln in fh if ln.strip())
    argv_reset = 0
    for f in glob.glob(os.path.join(p, "run.log")) + glob.glob(os.path.join(p, "run.out")):
        txt = open(f, errors="replace").read()
        argv_reset += txt.count("--reset-ms") + txt.count("SET_STATS")
    r = dict(step=s, sample_rows=n_tel, sampler_processes=samp, config_in_runs=cfg, sptrace=spt, residency_not_sent=ns, residency_sent=res_sent,
             config_snapshots=snaps, config_snapshot_attempts=att, drains=drains, launch_processes=nl, reset=argv_reset)
    rows.append(r)
    for k in tot:
        tot[k] += r[k]
extra = sorted(os.path.basename(f) for f in glob.glob(os.path.join(d, "config-session-*.txt")))
print(json.dumps({"steps": rows, "total": tot, "session_config_files": extra}, indent=1))
