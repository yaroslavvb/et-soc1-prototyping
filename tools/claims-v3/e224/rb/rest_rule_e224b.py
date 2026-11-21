#!/usr/bin/env python3
"""E224 (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum; E209's kit's rb/rest_rule_e209.py form): THE REST RULE (E224.md 6): the first card command at least 40 minutes
after the last session on aifoundry2 card 0 ended, whoever ran it. Standard library only; reads only; opens no device.

    /usr/bin/python3 -I -B tools/claims-v3/e224/rb/rest_rule_e224b.py --lab LAB --root E224B_ROOT [--releases RECORD ...] [--tree DIR ...]
        [--now EPOCH] [--rest-s 2400]
    prints every session end found (source, what, when), the latest, and the last line
        REST OPEN since <time> (the last end <time>, <source>)                       exit 0
        REST NOT OPEN until <time> (the last end <time>, <source>): call again        exit 17
        REST UNREADABLE: <why>                                                        exit 16 (a source that cannot be read stops)

WHERE A SESSION END IS READ (each a session of this card; the latest counts):
  1. the lab's committed data (LAB/docs/reports/data/<dir>, each folder dated yesterday or today whose name names aifoundry2 or a2c0):
     every queue.json's t_close_ms (E208's runner form: E208's, E209's, E212's and E224's), and every line holding 'session end' in a .log or .txt file whose line
     starts with its time 'YYYY-MM-DD HH:MM:SS' (E190's, E194's, E200's forms; a time zone word PST or PDT after it);
  2. the round's records of the model session's releases (--releases, repeated: W/out/orch/e208-releases.txt, e212-releases.txt and any later one):
     every line naming 'aifoundry2 card 0', its post's day and its 'ended [cleanly] HH:MM:SS' (a session the lab has not committed yet);
  3. E224's own box root (--root): every sessions/<T0>-a2c0-E224 folder, its queue.json's t_close_ms, or, for a session with none (cut,
     or still running), the latest write of any file in it (a running session's end is now: the rule then waits);
  4. any other tree of ours on this box given by --tree (read-only: queue.json t_close_ms and 'session end' log lines written in the last
     48 hours; E200's and E194's box-tree folders, if the card lane names them).
A dry pass (dry/ folders, a queue.json saying dry) is never a session on the card. The model session's own folders (ee-*) are never read:
its released sessions come through 1 and 2.
A session whose queue.json says it never reached the card (E208's runner writes t_first_ms null when it ended at a gate before its first
card command: the box lock, the box check, the card's lock, a holder) is not a session on the card, wherever it is read: it is listed and
not counted (no card command, no load; the runbook's 'one session a day' counts only sessions that reached the card, so a second session
the same day follows one that never did). Its own 'session end' log line is not counted either. The box root is never read again by 1 or 4.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import json
import os
import re
import sys
import time

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001
    TZ = None
LINE_T = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)(?:\.\d+)? (PST|PDT)\b")
REL_DAY = re.compile(r"\b(\d{4}-\d\d-\d\d) (\d\d:\d\d:\d\d) PST\b")
REL_END = re.compile(r"\bended (?:cleanly )?(\d\d:\d\d:\d\d)\b")


def pst(epoch):
    return datetime.datetime.fromtimestamp(epoch, TZ).strftime("%Y-%m-%d %H:%M:%S %Z") if epoch else "never"


def epoch_of(day_time):
    return datetime.datetime.strptime(day_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ).timestamp()


NEVER = []      # (path, why) of sessions found that never reached the card or are dry passes: listed, never counted


def queue_state(p):
    """-> ("dry" | "never" | "end" | "none", t_close in seconds or None)"""
    try:
        q = json.load(open(p))
    except (OSError, ValueError) as e:
        raise RuntimeError(f"{p}: unreadable ({type(e).__name__})")
    if q.get("dry"):
        return "dry", None
    if "t_first_ms" in q and q.get("t_first_ms") is None:
        return "never", None
    t = q.get("t_close_ms")
    return ("end", t / 1000.0) if isinstance(t, (int, float)) else ("none", None)


def from_queue(p):
    st, t = queue_state(p)
    return t if st == "end" else None


def from_logs(top, since=None, skip=None):
    out = []
    for dp, dn, fn in os.walk(top):
        if skip and (os.path.realpath(dp) + os.sep).startswith(skip + os.sep):
            dn[:] = []
            continue
        dn[:] = [d for d in dn if d not in ("dry", "__pycache__") and not d.startswith("ee-")]
        if "queue.json" in fn:
            st, _ = queue_state(os.path.join(dp, "queue.json"))
            if st in ("dry", "never"):
                NEVER.append((dp, "a dry pass" if st == "dry" else "never reached the card (t_first_ms null)"))
                dn[:] = []
                continue
        for n in fn:
            p = os.path.join(dp, n)
            if n == "queue.json":
                t = from_queue(p)
                if t:
                    out.append((t, p, "queue.json t_close_ms"))
            elif n.endswith((".log", ".txt")) and os.path.getsize(p) < 50 * 2 ** 20:
                if since and os.path.getmtime(p) < since:
                    continue
                try:
                    for ln in open(p, errors="replace"):
                        if "session end" in ln:
                            m = LINE_T.match(ln)
                            if m:
                                out.append((epoch_of(m.group(1)), p, "a 'session end' line"))
                except OSError as e:
                    raise RuntimeError(f"{p}: unreadable ({type(e).__name__})")
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--releases", action="append", default=[], help="a release record; several by repeating it")
    ap.add_argument("--tree", action="append", default=[])
    ap.add_argument("--now", type=float)
    ap.add_argument("--rest-s", type=float, default=2400.0)
    a = ap.parse_args(argv)
    now = a.now or time.time()
    found = []
    try:
        d0 = datetime.datetime.fromtimestamp(now, TZ).date()
        days = {str(d0), str(d0 - datetime.timedelta(days=1))}
        data = os.path.join(a.lab, "docs", "reports", "data")
        for d in sorted(os.listdir(data)):
            if d[:10] in days and ("aifoundry2" in d or "a2c0" in d) and os.path.isdir(os.path.join(data, d)):
                found += [(t, f"LAB/docs/reports/data/{os.path.relpath(p, data)}", w)
                          for t, p, w in from_logs(os.path.join(data, d), skip=os.path.realpath(a.root))]
        skip = os.path.realpath(a.root)
        for rel in a.releases:
            if not os.path.exists(rel):
                raise RuntimeError(f"the release record {rel} is missing")
            for ln in open(rel):
                if ln.startswith("#") or "aifoundry2 card 0" not in ln:
                    continue
                m, e = REL_DAY.search(ln), REL_END.search(ln)
                if not (m and e):
                    raise RuntimeError(f"a release line without its day or end: {ln.strip()[:100]}")
                t_post = epoch_of(f"{m.group(1)} {m.group(2)}")
                t_end = epoch_of(f"{m.group(1)} {e.group(1)}")
                if t_end > t_post:
                    t_end -= 86400
                found.append((t_end, f"the release record: {ln.split()[0]} {ln.split()[4] if len(ln.split()) > 4 else ''}".strip(),
                              "'ended HH:MM:SS' of a release post"))
        sd = os.path.join(a.root, "sessions")
        for n in sorted(os.listdir(sd)) if os.path.isdir(sd) else []:
            p = os.path.join(sd, n)
            if not (os.path.isdir(p) and n.endswith("-a2c0-E224")):
                continue
            q = os.path.join(p, "queue.json")
            st, t = queue_state(q) if os.path.exists(q) else ("none", None)
            if st in ("dry", "never"):
                NEVER.append((f"E224B_ROOT/sessions/{n}", "a dry pass" if st == "dry" else "never reached the card (t_first_ms null)"))
            elif t:
                found.append((t, f"E224B_ROOT/sessions/{n}", "queue.json t_close_ms"))
            else:
                latest = max([os.path.getmtime(os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs] + [os.path.getmtime(p)])
                running = not os.path.exists(os.path.join(p, "MANIFEST.sha256")) and not os.path.exists(os.path.join(p, "runner.rc"))
                found.append((max(latest, now) if running else latest, f"E224B_ROOT/sessions/{n}",
                              "no queue.json: " + ("still running (its end is now)" if running else "a cut session, at its latest write")))
        for tr in a.tree:
            if os.path.isdir(tr):
                found += [(t, f"tree {os.path.basename(os.path.normpath(tr))}/{os.path.relpath(p, tr)}", w)
                          for t, p, w in from_logs(tr, since=now - 172800, skip=skip)]
    except (OSError, RuntimeError) as e:
        print(f"REST UNREADABLE: {e}")
        return 16
    for src, why in NEVER[-6:]:
        print(f"  not counted: {src} ({why})")
    for t, src, w in sorted(found)[-8:]:
        print(f"  {pst(t)}  {src}  ({w})")
    if not found:
        print("REST OPEN since always (no session of aifoundry2 card 0 found in the sources above)")
        return 0
    t, src, w = max(found)
    opens = t + a.rest_s
    if now >= opens:
        print(f"REST OPEN since {pst(opens)} (the last end {pst(t)}, {src})")
        return 0
    print(f"REST NOT OPEN until {pst(opens)} (the last end {pst(t)}, {src}): call again")
    return 17


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
