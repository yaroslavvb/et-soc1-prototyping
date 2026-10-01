#!/usr/bin/env python3
"""make_usage.py ETU_SCRATCH [--et-usage CLI] [--work DIR]: the @@usage sections of testdata/ from real et-usage output.

ETU_SCRATCH is the scratch directory of `python3 tools/lab/et-usage/test/test_et_usage.py --dir ETU_SCRATCH --keep`.
Its logs are records the logger wrote or its tests made: the daemon's own end-to-end runs (`log/`: the flock pattern,
unseen opens with and without a lock hint, a holder present at start, SIGTERM while holding; `fixes/log/`: a program
named with terminal escapes, SIGKILL and restart, which writes a hold with "lost_end"), the CLI tests' lock-hint log
(`clifix/lockuser/log/`) and a busy CI day (`clifix/size1/log/`). This script lays them out over an invented day,
renaming logins to the testdata's invented ones (owner, user-a, user-b), hosts and cards to the lab's, and shifting
times; adds the heartbeats a running daemon writes, a `now.json` per host, and two invented holds (a login and a
program name that fail the collector's rules); then runs the et-usage CLI (`--json --since 26h --log-dir --run-dir
--now`, TZ=America/Los_Angeles) on them and puts its output, unchanged, in each raw file's @@usage section, followed
by "rc 0" as remote.sh prints it.

The three runs (collector --now 12:45, 12:55, 13:05 on 30 September 2026; the hosts' clocks say 12:40 in run 1):
  aifoundry1  run 1: a short run at 06:50 (a crash and a restart), then running since 08:00, restarted at 09:30;
              user-a holds card 1 since 10:08. Run 2: down (no section). Run 3: back after a power loss: the new daemon
              wrote user-a's hold with "lost_end" and started at 13:00:30.
  aifoundry2  a CI login (user-b) every minute or so for a day: et-usage merges its runs (merged_gap_s). Logging
              paused at 12:05 for low free space ("paused"). Runs 1 and 2 read it with --max-read-mb 0.25, so that
              the read budget cuts the log ("truncated_before"; remote.sh uses the default 64 MB). Run 2: rebooted
              at 12:48, still paused. Run 3: the daemon died at 12:58 (now.json 7 minutes old: "stale"), and the
              whole log is read: over 200 KB, so et-usage merges the login's runs ("merged_gap_s").
  aifoundry3  never answers in these runs (no section).
The work files (logs, now.json, outputs) go in WORK (default ETU_SCRATCH/dash-testdata); nothing outside testdata/ and
WORK is written.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["TZ"] = "America/Los_Angeles"
time.tzset()
DAY = "2026-09-30"
BOOT = {"aifoundry1": "1a1a1a1a-0000-4000-8000-000000000001", "aifoundry1b": "1b1b1b1b-0000-4000-8000-000000000001",
        "aifoundry2": "2b2b2b2b-0000-4000-8000-000000000002", "aifoundry2b": "2c2c2c2c-0000-4000-8000-000000000002"}


def T(hms, day=DAY):
    """a local time of the invented day -> epoch seconds"""
    return time.mktime(time.strptime(day + " " + hms, "%Y-%m-%d %H:%M:%S"))


def load(d):
    out = []
    for n in sorted(os.listdir(d)):
        if re.fullmatch(r"\d{4}-\d\d-\d\d\.jsonl", n):
            with open(os.path.join(d, n)) as f:
                out += [json.loads(ln) for ln in f if ln.strip()]
    return out


def rtime(r):
    return r.get("at", r.get("end"))


def lay(recs, to, users, cards, host, boot, types=None):
    """recs moved so that the earliest record starts at `to`; logins, cards, host and boot renamed; the watched paths
    become the host's own (the test's are scratch files)"""
    t0 = min(min(r[k] for k in ("at", "start") if isinstance(r.get(k), (int, float))) for r in recs)
    out = []
    for r in recs:
        if types and r["t"] not in types:
            continue
        r = dict(r)
        for k in ("at", "start", "end"):
            if isinstance(r.get(k), (int, float)):
                r[k] = round(r[k] - t0 + to, 3)
        for k in ("user", "lock_user"):
            if k in r and r[k] in users:
                r[k] = users[r[k]]
        if "uid" in r and r.get("user") in UIDS:
            r["uid"] = UIDS[r["user"]]
        if "card" in r:
            if r["card"] not in cards:
                continue
            r["card"] = cards[r["card"]]
        if isinstance(r.get("cards"), list):
            r["cards"] = sorted({cards[c] for c in r["cards"] if c in cards})
            r["watch"] = ["/dev/et%d_%s" % (c, n) for c in r["cards"] for n in ("mgmt", "ops")] + \
                         ["/run/lock/etsoc-shire%d.lock" % c for c in r["cards"]]
            r.pop("added", None), r.pop("gone", None)
        if "host" in r:
            r["host"] = host
        if "boot" in r:
            r["boot"] = boot
        if "sees_all" in r:
            r["sees_all"] = True   # the test ran as a plain user; the service sees every process
        out.append(r)
    return out


UIDS = {"owner": 1001, "user-a": 1002, "user-b": 1003}


def beats(a, b, every=600):
    t, out = a, []
    while t <= b:
        out.append({"t": "beat", "v": 1, "at": round(t, 3), "holding": 0})
        t += every
    return out


def hold(card, pid, user, comm, parent, nodes, lock, s, e, **kw):
    return dict({"t": "hold", "v": 1, "card": card, "pid": pid, "user": user, "uid": UIDS.get(user), "comm": comm,
                 "parent": parent, "nodes": nodes, "lock": lock, "start": round(s, 3), "end": round(e, 3)}, **kw)


def write_log(d, recs):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    by = {}
    for r in sorted(recs, key=rtime):
        by.setdefault(time.strftime("%Y-%m-%d", time.localtime(rtime(r))), []).append(r)
    for day, rs in by.items():
        with open(os.path.join(d, day + ".jsonl"), "w") as f:
            for r in rs:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")


def write_now(d, host, at, started, boot, cards, holds, paused=None):
    os.makedirs(d, exist_ok=True)
    doc = {"v": 1, "host": host, "at": at, "started_at": started, "pid": 4321, "boot": boot, "cards": cards,
           "holds": holds, "sees_all": True,
           "stats": {"scans": 812, "events": 3307, "overflows": 0, "unseen": 4, "last_scan_ms": 6.1, "max_scan_ms": 31.0,
                     "last_scan_cpu_ms": 5.2, "fd_truncated": 0, "maps_truncated": 0, "holds_dropped": 0,
                     "dropped": 37 if paused else 0}}
    if paused:
        doc["paused"] = paused
    with open(os.path.join(d, "now.json"), "w") as f:
        json.dump(doc, f)


def now_hold(h):
    return {k: h[k] for k in ("card", "pid", "user", "uid", "comm", "parent", "nodes", "lock", "start")}


def run_cli(cli, work, name, now, extra=()):
    out = subprocess.run([sys.executable, cli, "--json", "--since", "26h", "--log-dir", work + "/" + name + "/log",
                          "--run-dir", work + "/" + name + "/run", "--now", str(now)] + list(extra),
                         capture_output=True, text=True, check=True).stdout
    with open(work + "/" + name + ".json", "w") as f:
        f.write(out)
    return out.strip()


def put_section(path, body):
    with open(path) as f:
        text = f.read()
    new, n = re.subn(r"(?ms)^@@usage\n.*?(?=^@@)", lambda m: "@@usage\n" + body + "\nrc 0\n", text)
    if n != 1:
        sys.exit("make_usage.py: no single @@usage section in " + path)
    with open(path, "w") as f:
        f.write(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scratch")
    ap.add_argument("--et-usage", default=os.path.join(HERE, "..", "..", "et-usage", "et-usage"))
    ap.add_argument("--work")
    a = ap.parse_args()
    S, W = a.scratch, a.work or os.path.join(a.scratch, "dash-testdata")
    os.makedirs(W, exist_ok=True)
    e2e, fixes = load(S + "/log"), load(S + "/fixes/log")
    lockuser, ci = load(S + "/clifix/lockuser/log"), load(S + "/clifix/size1/log")
    me = next(r["user"] for r in e2e if r["t"] == "hold" and r["user"] != "?")   # the login the tests ran as
    now1, now2, now3 = T("12:40:00"), T("12:55:00"), T("13:05:00")

    # ---- aifoundry1: card 0 is the excluded card, card 1 the one in use (the tests' cards 0 and 1 swap places)
    sw, b1 = {0: 1, 1: 0}, BOOT["aifoundry1"]
    log1 = lay(fixes, T("06:50:00"), {me: "user-b"}, sw, "aifoundry1", b1)                 # a crash and a restart
    log1 += lay(lockuser, T("08:00:00"), {"alice": "owner"}, {0: 1}, "aifoundry1", b1)     # a lock hint (owner)
    log1 += beats(T("08:10:00"), T("09:20:00"))                                            # every 10 min
    log1 += lay(e2e, T("09:30:00"), {me: "user-a"}, sw, "aifoundry1", b1)                  # a restart (09:30), the flock
    log1 += beats(T("09:40:00"), now1 - 120)                                               # pattern, unseen opens
    log1 += [r for r in lay(e2e, T("09:50:00"), {me: "user-a"}, sw, "aifoundry1", b1, types=("hold", "act"))
             if r["card"] == 1]                                                            # the same runs again
    log1.append(hold(1, 7101, "bad user!", "10.0.0.7", "timeout", ["ops"], True, T("09:55:00"), T("09:55:04")))
    # user-a's run since 10:08 (as the testdata's et-who section says): flock, timeout and the program
    run = [hold(1, 7201, "user-a", "flock", "bash", [], True, T("10:08:50"), 0),
           hold(1, 7202, "user-a", "timeout", "flock", [], True, T("10:08:50") + 0.01, 0),
           hold(1, 7203, "user-a", "sgemm_host", "timeout", ["mgmt", "ops"], True, T("10:08:52"), 0)]
    write_log(W + "/a1-run1/log", log1)
    write_now(W + "/a1-run1/run", "aifoundry1", now1 - 10, T("09:30:00"), b1, [0, 1], [now_hold(h) for h in run])
    # run 3: the power went at 12:49:50; at boot the new daemon writes the open holds with lost_end, then starts
    b1b = BOOT["aifoundry1b"]
    log3 = log1 + beats(T("12:40:00"), T("12:49:00"))
    log3 += [dict(h, end=T("12:49:50"), lost_end=True) for h in run]
    log3.append({"t": "start", "v": 1, "at": T("13:00:30"), "host": "aifoundry1", "boot": b1b, "pid": 911,
                 "cards": [0, 1], "watch": ["/dev/et0_mgmt", "/dev/et0_ops", "/dev/et1_mgmt", "/dev/et1_ops",
                                            "/run/lock/etsoc-shire0.lock", "/run/lock/etsoc-shire1.lock"],
                 "sees_all": True})
    write_log(W + "/a1-run3/log", log3)
    write_now(W + "/a1-run3/run", "aifoundry1", now3 - 10, T("13:00:30"), b1b, [0, 1], [])

    # ---- aifoundry2: a CI login all day, paused at 12:05 (low free space); one card
    ci2 = lay(ci, 0, {r["user"]: "user-b" for r in ci if r.get("user")}, {0: 0}, "aifoundry2", BOOT["aifoundry2"])
    last = max(rtime(r) for r in ci2)
    ci2 = [dict(r, **{k: round(r[k] - last + T("12:05:00"), 3) for k in ("at", "start", "end") if k in r}) for r in ci2]
    paused = "the filesystem of /var/log/et-usage has 310 MB free (--min-free-mb 512)"
    started = min(rtime(r) for r in ci2)
    for name, at, st, boot in (("a2-run1", now1 - 5, started, BOOT["aifoundry2"]),
                               ("a2-run2", now2 - 10, T("12:48:30"), BOOT["aifoundry2b"]),
                               ("a2-run3", T("12:58:00"), T("12:48:30"), BOOT["aifoundry2b"])):
        write_log(W + "/" + name + "/log", ci2)
        write_now(W + "/" + name + "/run", "aifoundry2", at, st, boot, [0], [], paused=paused)

    cut = ["--max-read-mb", "0.25"]
    put_section(HERE + "/raw-aifoundry1.txt", run_cli(a.et_usage, W, "a1-run1", now1))
    put_section(HERE + "/run3/raw-aifoundry1.txt", run_cli(a.et_usage, W, "a1-run3", now3))
    put_section(HERE + "/raw-aifoundry2.txt", run_cli(a.et_usage, W, "a2-run1", now1, cut))
    put_section(HERE + "/run2/raw-aifoundry2.txt", run_cli(a.et_usage, W, "a2-run2", now2, cut))
    put_section(HERE + "/run3/raw-aifoundry2.txt", run_cli(a.et_usage, W, "a2-run3", now3))  # all read: merged
    print("make_usage.py: wrote the @@usage sections of 5 raw files (work files in %s)" % W)


if __name__ == "__main__":
    main()
