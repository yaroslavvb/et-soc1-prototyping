#!/usr/bin/env python3
"""data-e208r (Q205, Tue 17 Nov 2026): the lab's check W of E208's added seventh session (the model session's repeat of a2c0-S1 on
aifoundry2 card 0): was its claim's window kept? Reads the session's own records (queue.json, status.json, session.log, the first and
last telemetry stamps) and takes the posts' times (the round's Discussion watcher's UTC stamps) and the claim's words as arguments.
Python's own modules only; reads only; prints its lines and writes a JSON beside them.

    /usr/bin/python3 -I -B window_e208r.py <session dir> --out window.json --txt window.txt

W checks (each PASS / FAIL with its numbers), all registered by the claim post #10.13.1.1.1 (23:28:27 PST Mon 16 Nov 2026):
  W1 the claim came before the session: the post's time before the session's T0 and before its first card command
  W2 the window's start: T0 and the first card command at or after 23:31:00 PST Mon 16 Nov
  W3 the window's end: the closing (t_close) and the last telemetry sample at or before 00:58:00 PST Tue 17 Nov
  W4 the bound: card-minutes (close - first card command) at most 72, and the runner's end bound = first card command + 72 min
  W5 the plan: 85 runs ran over 71 arms (runs of role arm and time, by arm name), the schedule a2c0-S1.json at its registered sha256
  W6 the release: posted after the closing and at or before 01:15:00 PST Tue 17 Nov ("released by 01:15")
  W7 the freeze line (post #10, 18:25:03.097 PST) and the registration commit (d005dc53, 20:26:46 PST) both before the first card command
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
POSTS = {  # the round's Discussion watcher's UTC stamps (its seen-list keys), Tue 17 Nov 2026 UTC
    "#10": "2026-11-17T02:25:03.097Z",
    "#10.13.1.1.1": "2026-11-17T07:28:27.327Z",
    "#10.13.1.1.1.2": "2026-11-17T08:11:25.138Z",
}
REG_COMMIT = ("d005dc5309287ef504e8d47e7d481db672d7f491", "2026-11-16T20:26:46-08:00")
SCHED_SHA256 = "c073cf501e19c28f1958db2476a6fb15b6673b1b67117925c881f0864f9197a4"  # src/sched/a2c0-S1.json, in SRC-SHA256SUMS 543e9298
WIN = ("2026-11-16T23:31:00", "2026-11-17T00:58:00", "2026-11-17T01:15:00")  # PST: the claim's "from 23:31 to 00:58 PST (released by 01:15)"
CLAIM = {"runs": 85, "arms": 71, "planned_min": 58, "cap_min": 72}


def ms_utc(s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC).timestamp() * 1000.0


def ms_pst(s):
    return datetime.datetime.fromisoformat(s).replace(tzinfo=TZ).timestamp() * 1000.0


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, TZ).strftime("%a %H:%M:%S.%f")[:-3]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    S = a.session
    q = json.load(open(os.path.join(S, "queue.json")))
    st = json.load(open(os.path.join(S, "status.json")))
    log = open(os.path.join(S, "session.log"), errors="replace").read().splitlines()
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
    claim, rel, frz = ms_utc(POSTS["#10.13.1.1.1"]), ms_utc(POSTS["#10.13.1.1.1.2"]), ms_utc(POSTS["#10"])
    w0, w1, wr = (ms_pst(x) for x in WIN)
    reg_ms = datetime.datetime.fromisoformat(REG_COMMIT[1]).timestamp() * 1000.0
    R, L = {}, []

    def rec(k, ok, **kw):
        R[k] = dict(verdict="PASS" if ok else "FAIL", **kw)
        L.append(f"{k} {R[k]['verdict']}: " + "; ".join(f"{x} {y}" for x, y in kw.items()))

    rec("W1_claim_first", claim < t0 and claim < first, claim_post=f"#10.13.1.1.1 {pst(claim)} PST",
        session_t0=f"{pst(t0)} PST", first_card_command=f"{pst(first)} PST", claim_lead_s=round((first - claim) / 1000.0, 3))
    rec("W2_window_start", t0 >= w0 and first >= w0, window_start=f"{pst(w0)} PST", t0_after_s=round((t0 - w0) / 1000.0, 3),
        first_after_s=round((first - w0) / 1000.0, 3), first_log_line=log[0][:60] if log else None)
    rec("W3_window_end", close <= w1 and (ts[-1] if ts else close) <= w1, window_end=f"{pst(w1)} PST",
        close=f"{pst(close)} PST", last_sample=(f"{pst(ts[-1])} PST" if ts else None),
        close_before_end_s=round((w1 - close) / 1000.0, 3), last_line=log[-1][:90] if log else None)
    card_min = (close - first) / 60000.0
    rec("W4_bound", card_min <= CLAIM["cap_min"] and bound == first + CLAIM["cap_min"] * 60000,
        card_minutes=round(card_min, 2), status_card_min=st.get("card_min"), cap_min=CLAIM["cap_min"],
        planned_min_about=CLAIM["planned_min"], runner_end_bound=(f"{pst(bound)} PST" if bound else None))
    runs = q["queue"]
    arms = sorted({r["arm"] for r in runs if r.get("role") in ("arm", "time")})
    names = sorted({r["arm"] for r in runs if r.get("role") != "null"})
    rec("W5_plan", q.get("n_ran") == CLAIM["runs"] == len(runs) and len(arms) == CLAIM["arms"] and q.get("sched") == "a2c0-S1.json"
        and q.get("sched_sha256") == SCHED_SHA256, runs_ran=q.get("n_ran"), runs_listed=len(runs),
        arms_arm_and_time=len(arms), arm_names_with_anchor=len(names), schedule=q.get("sched"),
        schedule_sha256=q.get("sched_sha256"))
    rec("W6_release", close < rel <= wr, release_post=f"#10.13.1.1.1.2 {pst(rel)} PST", released_by=f"{pst(wr)} PST",
        release_after_close_s=round((rel - close) / 1000.0, 3))
    rec("W7_freeze_and_registration_first", frz < first and reg_ms < first, freeze_post=f"#10 {pst(frz)} PST (Mon 16 Nov)",
        freeze_lead=f"{(first - frz) / 60000.0:.2f} min", registration_commit=f"{REG_COMMIT[0][:8]} {REG_COMMIT[1]}",
        registration_lead=f"{(first - reg_ms) / 60000.0:.2f} min")
    verdict = "ALL PASS" if all(v["verdict"] == "PASS" for v in R.values()) else \
        "FAIL: " + ", ".join(k for k, v in R.items() if v["verdict"] != "PASS")
    L.append(f"VERDICT {verdict}")
    out = {"what": "data-e208r's check W of the claim's window for E208's added seventh session (reads only)",
           "session": os.path.basename(os.path.normpath(S)), "posts_utc": POSTS, "window_pst": WIN, "claim": CLAIM,
           "checks": R, "verdict": verdict, "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    with open(a.txt, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
