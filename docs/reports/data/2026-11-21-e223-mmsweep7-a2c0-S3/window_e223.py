#!/usr/bin/env python3
"""data-e223 (Q239, Sat 21 Nov 2026): the lab's check W of one released E223 (1121-mmsweep7) session: was its claim's window kept?
data-e221's window check (Q235; data-e217's, Q228; data-e214's, Q220; data-e212's, Q208, itself Q205 data-e208r's made general), for
E223, the freeze line moved to post #16: the claim's and release's post ids and times (the round's Discussion watcher's UTC
stamps), the window and the plan's numbers come from the session's meta file (work/meta/<label>.json, written by this lane from the
round's records); the session's own records give the rest (queue.json, status.json, session.log, the telemetry stamps). The registered
schedule's sha256 is read from the src list given. Python's own modules only; reads only; prints its lines and writes a JSON.

    /usr/bin/python3 -I -B window_e223.py <session dir> <meta json> <src dir> --out window.json --txt window.txt

W checks (each PASS / FAIL / NOTE with its numbers):
  W1 the claim came before the session: the claim post's time before the session's T0 and before its first card command
  W2 the window's start: T0 and the first card command at or after the window's start (PST)
  W3 the window's end: the closing (t_close) and the last telemetry sample at or before the window's end (PST)
  W4 the bound: card-minutes (close - first card command) at most the claim's bound when it names one, and at most the schedule's
     own cap_min, with the runner's end bound = first card command + the schedule's cap_min
  W5 the plan: the runs ran = the claim's runs = the queue's length; the schedule's sha256 = the leading hex the claim names (when it
     names one); the schedule's arms counted as the claim counts them, when it names them (#13's to #15's claims named runs only) (every
     distinct arm name, the anchor and the null runs included, as E212's #11.1, #11.2 and #11.4 did; or the arms alone, with the anchor
     runs and the null runs given apart, as E212's #11.5 did) = the claim's; the schedule's name and sha256 = the registered list's entry
  W6 the release: posted after the closing (and at or before the claim's "released by" when it names one)
  W7 the freeze line (post #16, 01:25:49.677 PST Sat 21 Nov 2026) before the first card command; the registration commit's time
     reported against the session (the post, not the commit, is the registration: a commit after the data is not a failure)
"""
import argparse
import datetime
import gzip
import json
import os
import sys
import zoneinfo

TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
UTC = datetime.timezone.utc
FREEZE_UTC = "2026-11-21T09:25:49.677Z"  # post #16, the watcher's stamp (01:25:49.677 PST Sat 21 Nov 2026)


def ms_utc(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC).timestamp() * 1000.0


def ms_pst(s):
    return datetime.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp() * 1000.0


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, TZ).strftime("%a %H:%M:%S.%f")[:-3]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("meta")
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    S = a.session
    m = json.load(open(a.meta))
    q = json.load(open(os.path.join(S, "queue.json")))
    st = json.load(open(os.path.join(S, "status.json")))
    log = open(os.path.join(S, "session.log"), errors="replace").read().splitlines()
    sums = dict((ln.split()[1], ln.split()[0]) for ln in open(os.path.join(a.src, "SRC-SHA256SUMS")) if ln.strip())
    sched = json.load(open(os.path.join(a.src, "sched", q["sched"])))
    t0 = q["t0"] * 1000.0
    first, close, bound = q["t_first_ms"], q["t_close_ms"], q.get("end_bound_ms")
    ts = []
    with gzip.open(os.path.join(S, "telemetry.jsonl.gz"), "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    ts.append(json.loads(ln)["t_ms"])
                except (ValueError, KeyError):
                    pass
    claim = ms_utc(m["claim"]["posted_utc"])
    rel = ms_utc(m["release"]["posted_utc"])
    frz = ms_utc(FREEZE_UTC)
    w0, w1 = ms_pst(m["window"][0]), ms_pst(m["window"][1])
    wr = ms_pst(m["window"][2]) if len(m["window"]) > 2 and m["window"][2] else None
    reg = m.get("registration") or {}
    reg_ms = datetime.datetime.fromisoformat(reg["time"]).timestamp() * 1000.0 if reg.get("time") else None
    plan = m.get("plan") or {}
    cap_sched = (sched.get("timing") or {}).get("cap_min")
    R, L = {}, []

    def rec(k, verdict, **kw):
        R[k] = dict(verdict=verdict, **kw)
        L.append(f"{k} {verdict}: " + "; ".join(f"{x} {y}" for x, y in kw.items()))

    P = lambda ok: "PASS" if ok else "FAIL"  # noqa: E731
    rec("W1_claim_first", P(claim < t0 and claim < first), claim_post=f"{m['claim']['post']} {pst(claim)} PST",
        session_t0=f"{pst(t0)} PST", first_card_command=f"{pst(first)} PST", claim_lead_s=round((first - claim) / 1000.0, 3))
    wc = m.get("window_correction")
    extra = {}
    if wc:
        cw0 = ms_pst(wc["window"][0])
        cpost = ms_utc(wc["posted_utc"])
        extra = {"correction": f"{wc['post']} posted {pst(cpost)} PST ({'after' if cpost > t0 else 'before'} T0) names the window from "
                               f"{pst(cw0)} PST: T0 {round((t0 - cw0) / 1000.0, 3)} s after it (REPORTED; W2 reads the claim as posted)"}
    rec("W2_window_start", P(t0 >= w0 and first >= w0), window_start=f"{pst(w0)} PST", t0_after_s=round((t0 - w0) / 1000.0, 3),
        first_after_s=round((first - w0) / 1000.0, 3), first_log_line=log[0][:60] if log else None, **extra)
    rec("W3_window_end", P(close <= w1 and (ts[-1] if ts else close) <= w1), window_end=f"{pst(w1)} PST",
        close=f"{pst(close)} PST", last_sample=(f"{pst(ts[-1])} PST" if ts else None),
        close_before_end_s=round((w1 - close) / 1000.0, 3), last_line=log[-1][:90] if log else None)
    card_min = (close - first) / 60000.0
    ok4 = (cap_sched is not None and card_min <= cap_sched and bound == first + cap_sched * 60000
           and (plan.get("cap_min") is None or card_min <= plan["cap_min"]))
    rec("W4_bound", P(ok4), card_minutes=round(card_min, 2), status_card_min=st.get("card_min"),
        claim_cap_min=(plan["cap_min"] if plan.get("cap_min") is not None else "not named in the record of the claim"),
        schedule_cap_min=cap_sched,
        planned_min_claim=(plan["planned_min"] if plan.get("planned_min") is not None else "not named in the record of the claim"),
        planned_min_schedule=sched.get("planned_min"),
        runner_end_bound=(f"{pst(bound)} PST" if bound else None))
    runs = q["queue"]
    names = sorted({r["arm"] for r in sched["runs"]})
    nonnull = sorted({r["arm"] for r in sched["runs"] if r.get("role") != "null"})
    arms_only = sorted({r["arm"] for r in sched["runs"] if r.get("role") not in ("null", "anchor")})
    n_anchor = sum(1 for r in sched["runs"] if r.get("role") == "anchor")
    n_null = sum(1 for r in sched["runs"] if r.get("role") == "null")
    sname = q.get("sched")
    kind = plan.get("arms_kind", "names_all")  # how the claim counts its arms: every distinct name, or the arms alone
    n_arms = len(names) if kind == "names_all" else len(arms_only)
    pref = plan.get("sched_sha_prefix")
    ok5 = (q.get("n_ran") == plan.get("runs") == len(runs) == len(sched["runs"])
           and (plan.get("arms") is None or n_arms == plan.get("arms"))
           and plan.get("anchor_runs", n_anchor) == n_anchor and plan.get("nulls", n_null) == n_null
           and sname == m.get("schedule") and q.get("sched_sha256") == sums.get(f"src/sched/{sname}")
           and (pref is None or (q.get("sched_sha256") or "").startswith(pref)))
    rec("W5_plan", P(ok5), runs_ran=q.get("n_ran"), runs_claim=plan.get("runs"), runs_listed=len(runs),
        arm_names_incl_anchor_and_nulls=len(names), arm_names_without_nulls=len(nonnull), arms_alone=len(arms_only),
        anchor_runs=n_anchor, null_runs=n_null,
        arms_claim=(f"{plan.get('arms')} ({kind})" if plan.get("arms") is not None else "not named by the claim (it names its runs)"),
        schedule=sname, schedule_sha256=q.get("sched_sha256"), registered_entry=(sums.get(f"src/sched/{sname}") or "ABSENT"),
        claim_schedule_sha256=(f"{pref}... = the schedule's: {(q.get('sched_sha256') or '').startswith(pref)}" if pref
                               else "not named by the claim"))
    ok6 = close < rel and (wr is None or rel <= wr)
    rec("W6_release", P(ok6), release_post=f"{m['release']['post']} {pst(rel)} PST",
        released_by=(f"{pst(wr)} PST" if wr else "not named in the record of the claim"),
        release_after_close_s=round((rel - close) / 1000.0, 3))
    rec("W7_freeze_first", P(frz < first), freeze_post=f"#16 {pst(frz)} PST", freeze_lead=f"{(first - frz) / 60000.0:.2f} min",
        registration_commit=(f"{reg.get('sha', '')[:8]} {reg.get('time')}" if reg_ms else "not landed when this check ran"),
        registration_vs_session=(("before the first card command, by " + f"{(first - reg_ms) / 60000.0:.2f} min") if reg_ms and reg_ms < first
                                 else ("after the session's close (the post is the registration)" if reg_ms and reg_ms > close
                                       else ("during the session" if reg_ms else "-"))))
    verdict = "ALL PASS" if all(v["verdict"] == "PASS" for v in R.values()) else \
        "FAIL: " + ", ".join(k for k, v in R.items() if v["verdict"] != "PASS")
    L.append(f"VERDICT {verdict}")
    out = {"what": "data-e223's check W of the claim's window for one E223 session (reads only)",
           "session": os.path.basename(os.path.normpath(S)), "freeze_utc": FREEZE_UTC, "meta": m, "checks": R, "verdict": verdict,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    with open(a.txt, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
