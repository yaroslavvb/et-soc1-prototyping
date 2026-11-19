#!/usr/bin/env python3
"""data-e217 (Q228): the lab's check K of one released E217 session: the kit's records E217.md asks the data lane to read at each release
(section 13 items 3 and 11) and the claim's consistency with the registration (section 10). Reads only: the kit's build record and load
record as copied with the session (work/<label>/kit/build/BUILD-mms.json, work/<label>/kit/run/preflight-load.txt), the session's own
log and queue, this lane's meta records of every E217 claim so far (work/meta/*.json) and the registered schedules. Python's own modules.

    /usr/bin/python3 -I -B kit_e217.py <work dir> <label> <src dir> --out kit.json --txt kit.txt

  K1 the build record (copied at the release): verdict BUILT on aifoundry1, its day the session's start day (Pacific), the kernel at E136's
     pin, the host at the claim's sha256 (by the leading hex the claim writes, as #13's claims give 16), "jobs" 1 (the post's "-j1 builds"), its ET_DEVICES statement; built before the first card command
  K2 the runner's own box check in session.log (its line 'the box and the build: ...') before the first card command
  K3 the box's one-minute load: the last line of the kit's run/preflight-load.txt (written by the operator's full preflight) before this
     session's first card command, and whether it is under 6 (REPORTED: E217.md section 13 item 11 drops no session for it)
  K4 the claim against the registration: its schedule is this session's and the registered file's (by the leading hex of its sha256
     when the claim names it); its runs (and its arms, when it names them) are the schedule's;
     its host is the build record's and the host every earlier E217 claim named (a claim that changes a host, an arm, a schedule, a tile
     or the reduction needs a dated amendment before its data are committed: E217.md section 10)
"""
import argparse
import datetime
import glob
import json
import os
import sys
import zoneinfo

TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
PIN = "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0"


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("label")
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    D = os.path.join(a.work, a.label)
    S = os.path.join(D, "session")
    q = json.load(open(os.path.join(S, "queue.json")))
    meta = json.load(open(os.path.join(a.work, "meta", a.label + ".json")))
    log = open(os.path.join(S, "session.log"), errors="replace").read().splitlines()
    first_ms, t0 = q["t_first_ms"], q["t0"]
    day = datetime.datetime.fromtimestamp(t0, TZ).strftime("%Y-%m-%d")
    R, L = {}, []

    def rec(k, verdict, **kw):
        R[k] = dict(verdict=verdict, **kw)
        L.append(f"{k} {verdict}: " + "; ".join(f"{x} {y}" for x, y in kw.items()))

    bp = os.path.join(D, "kit", "build", "BUILD-mms.json")
    if os.path.exists(bp):
        b = json.load(open(bp))
        built_ms = (b.get("epoch") or 0) * 1000.0
        claim_host = meta.get("host_sha256_claim")
        ok = (b.get("verdict") == "BUILT" and b.get("box") == "aifoundry1" and b.get("day") == day and b.get("kernel_sha256") == PIN
              and (claim_host is None or (b.get("host_sha256") or "").startswith(claim_host)) and b.get("jobs") == 1
              and "ET_DEVICES" in (b.get("et_devices") or "") and built_ms < first_ms)
        rec("K1_build_record", "PASS" if ok else "FAIL", build_verdict=b.get("verdict"), box=b.get("box"), day=b.get("day"),
            session_day=day, built=datetime.datetime.fromtimestamp(b.get("epoch") or 0, TZ).strftime("%Y-%m-%d %H:%M:%S %Z"),
            built_before_first_card_command=built_ms < first_ms, kernel_at_pin=b.get("kernel_sha256") == PIN,
            host=(b.get("host_sha256") or "")[:16],
            host_is_the_claims=("the claim names no host hash" if claim_host is None
                                else (b.get("host_sha256") or "").startswith(claim_host)),
            claim_host_hex_named=(len(claim_host) if claim_host else 0),
            reader=(b.get("ettelem_sha256") or "")[:16], jobs=b.get("jobs"), et_devices=b.get("et_devices"))
    else:
        rec("K1_build_record", "NOT RUN", why="the build record was not listed at the release, so it was not copied")
    box_line = next((ln for ln in log[:8] if "the box and the build:" in ln), None)
    rec("K2_runner_box_check", "PASS" if box_line else "FAIL", line=(box_line[24:200] if box_line else None))
    loadp = os.path.join(D, "kit", "run", "preflight-load.txt")
    if os.path.exists(loadp):
        rows = []
        for ln in open(loadp, errors="replace"):
            p = ln.split()
            if len(p) >= 3 and p[0].isdigit():
                rows.append((int(p[0]), p[1], p[2]))
        before = [r for r in rows if r[0] * 1000.0 <= first_ms]
        last = before[-1] if before else None
        under = None
        if last:
            try:
                under = float(last[2]) < 6.0
            except ValueError:
                under = None
        rec("K3_load_reading", "REPORTED", lines=len(rows), readings_before_first_card_command=len(before),
            last_before=(f"{datetime.datetime.fromtimestamp(last[0], TZ).strftime('%Y-%m-%d %H:%M:%S %Z')} card {last[1]} load {last[2]}"
                         if last else "none"),
            last_before_lead_s=(round(first_ms / 1000.0 - last[0], 1) if last else None), under_6=under)
    else:
        rec("K3_load_reading", "NOT RUN", why="the kit's run/preflight-load.txt was not listed at the release")
    sched = json.load(open(os.path.join(a.src, "sched", q["sched"])))
    names = {r["arm"] for r in sched["runs"]}
    arms_alone = {r["arm"] for r in sched["runs"] if r.get("role") not in ("null", "anchor")}
    plan = meta.get("plan") or {}
    n_arms = len(names) if plan.get("arms_kind", "names_all") == "names_all" else len(arms_alone)
    hosts = {}
    for mp in sorted(glob.glob(os.path.join(a.work, "meta", "*.json"))):
        m = json.load(open(mp))
        hosts[m["label"]] = m.get("host_sha256_claim")
    first_host = None
    for mp in sorted(glob.glob(os.path.join(a.work, "meta", "*.json")), key=lambda p: json.load(open(p))["claim"]["posted_utc"]):
        first_host = first_host or json.load(open(mp)).get("host_sha256_claim")
    host_b = json.load(open(bp)).get("host_sha256") if os.path.exists(bp) else None
    # the build records copied at the earlier releases (each session's kit/build/BUILD-mms.json in work/)
    rec_hosts = {}
    for p in sorted(glob.glob(os.path.join(a.work, "a1c*-S*", "kit", "build", "BUILD-mms.json"))):
        rec_hosts[p.split(os.sep)[-4]] = json.load(open(p)).get("host_sha256")
    hosts_seen = sorted({h for h in rec_hosts.values() if h})
    claim_host = meta.get("host_sha256_claim")
    pref = plan.get("sched_sha_prefix")
    ok4 = (meta.get("schedule") == q["sched"] and plan.get("runs") == len(sched["runs"])
           and (plan.get("arms") is None or plan.get("arms") == n_arms)
           and (pref is None or (q.get("sched_sha256") or "").startswith(pref))
           and (plan.get("anchor_runs") is None or plan.get("anchor_runs") == sum(1 for r in sched["runs"] if r.get("role") == "anchor"))
           and (plan.get("nulls") is None or plan.get("nulls") == sum(1 for r in sched["runs"] if r.get("role") == "null"))
           and claim_host == first_host and (host_b is None or claim_host is None or host_b.startswith(claim_host)) and len(hosts_seen) <= 1)
    rec("K4_claim_vs_registration", "PASS" if ok4 else "FAIL", claim_schedule=meta.get("schedule"), session_schedule=q["sched"],
        claim_runs=plan.get("runs"), schedule_runs=len(sched["runs"]),
        claim_arms=(f"{plan.get('arms')} ({plan.get('arms_kind', 'names_all')})" if plan.get("arms") is not None
                    else "not named by the claim (it names its runs)"),
        claim_schedule_sha256=(f"{pref}... = the session's: {(q.get('sched_sha256') or '').startswith(pref)}" if pref
                               else "not named by the claim"),
        schedule_arms=n_arms, claim_host=(meta.get("host_sha256_claim") or "")[:16], first_claims_host=(first_host or "")[:16],
        build_record_host=(host_b or "not read")[:16], hosts_named_by_claims={k: (v or "none")[:12] for k, v in hosts.items()},
        hosts_in_the_build_records_copied={k: (v or "")[:12] for k, v in rec_hosts.items()})
    verdict = "ALL PASS" if all(v["verdict"] in ("PASS", "REPORTED") for v in R.values()) else \
        "SEE: " + ", ".join(f"{k} {v['verdict']}" for k, v in R.items() if v["verdict"] not in ("PASS", "REPORTED"))
    L.append(f"VERDICT {verdict}")
    out = {"what": "data-e217's check K of one E217 session: the kit's build and load records at its release, and its claim against the "
                   "registration (reads only)", "session": os.path.basename(os.path.normpath(S)), "checks": R, "verdict": verdict,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(out, open(a.out, "w"), indent=1)
    open(a.txt, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
