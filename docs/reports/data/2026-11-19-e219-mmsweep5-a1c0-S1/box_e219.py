#!/usr/bin/env python3
"""data-e219 (Q232; data-e212's box check, renamed for E214, E217 and E219): the lab's check B of one released E219 session: one session at a time on
the box ("with nothing of ours on card N meanwhile", the claims). Reads this session's queue.json and those of every other E219 session of the same box this lane has copied
(their T0 to their close), and, when given, a read-only listing of the box's sessions folder (the folder names: '<T0 epoch>-<card>-<S>')
for sessions the lane has not copied. E219 shares aifoundry1 with E217's last sessions (the model session's fourth sweep, another kit
folder), so check B also reads (new for E219): --e217-dirs, E217's committed session folders in the lab (exact: their T0 to their
close), and --e217-record, the orchestrator's E217 record (each E217 session's claim post to its release post, a bound on when it ran,
for the E217 sessions not committed when this runs). Python's own modules only; reads only.
    /usr/bin/python3 -I -B box_e219.py <this session dir> --others <session dir> ... [--listing <file>]
        [--e217-dirs <committed E217 session dir> ...] [--e217-record <e217-releases.txt>] --out b.json --txt b.txt
"""
import argparse
import datetime
import json
import os
import re
import sys
import zoneinfo

TZ = zoneinfo.ZoneInfo("America/Los_Angeles")


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, TZ).strftime("%H:%M:%S")


def span(d):
    q = json.load(open(os.path.join(d, "queue.json")))
    return q["t0"] * 1000.0, q["t_close_ms"], q["card"], f"{q['t0']}-{q['sched'][:-5]}"  # the model session's folder name


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--others", nargs="*", default=[])
    ap.add_argument("--listing", default=None)
    ap.add_argument("--e217-dirs", nargs="*", default=[])
    ap.add_argument("--e217-record", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    t0, t1, card, sid = span(a.session)
    rows, bad = [], []
    for d in a.others:
        o0, o1, oc, osid = span(d)
        if osid == sid:
            continue
        ov = o0 < t1 and t0 < o1
        rows.append(f"{osid} ({oc}) {pst(o0)}-{pst(o1)}: {'OVERLAPS' if ov else 'apart'}")
        if ov:
            bad.append(osid)
    uncopied = []
    if a.listing and os.path.exists(a.listing):
        for ln in open(a.listing):
            m = re.search(r"\b(\d{10})-(a\dc\d)-(S\d)\b", ln)
            if m and m.group(0) != sid and not any(m.group(0) in r for r in rows + uncopied):
                st = int(m.group(1)) * 1000.0
                uncopied.append(f"{m.group(0)} (T0 {pst(st)}; not copied: only its start is known)")
                if t0 <= st <= t1:
                    bad.append(m.group(0))
    # E217's sessions on the same box (new for E219): exact spans from its committed folders, else the record's claim-release bounds
    e217 = []
    e217_exact = set()
    e217_dirs_read = []
    for d in a.e217_dirs:
        if not os.path.exists(os.path.join(d, "queue.json")):
            continue
        e217_dirs_read.append(os.path.basename(os.path.dirname(os.path.normpath(d))))
        o0, o1, oc, osid = span(d)
        lab17 = osid.split("-", 1)[1]
        e217_exact.add(lab17)
        if osid == sid:
            continue
        ov = o0 < t1 and t0 < o1
        e217.append(f"E217 {osid} ({oc}, committed) {pst(o0)}-{pst(o1)}: {'OVERLAPS' if ov else 'apart'}")
        if ov:
            bad.append("E217 " + osid)
    if a.e217_record and os.path.exists(a.e217_record):
        claims, rels = {}, {}
        for ln in open(a.e217_record, errors="replace"):
            m = re.search(r"\b(20\d\d-\d\d-\d\d) (\d\d:\d\d:\d\d) PST: (CLAIM|RELEASE) aifoundry1 card (\d)\b(.*)", ln)
            if not m:
                continue
            s = re.search(r"\bE217 (?:card-0 )?(S\d+)\b", m.group(5)) or re.search(r"\ba\dc\d-(S\d+)\b", m.group(5))
            if not s:
                continue
            lab17 = f"a1c{m.group(4)}-{s.group(1)}"
            when = datetime.datetime.fromisoformat(f"{m.group(1)}T{m.group(2)}").replace(tzinfo=TZ).timestamp() * 1000.0
            (claims if m.group(3) == "CLAIM" else rels).setdefault(lab17, []).append(when)
        for lab17 in sorted(set(claims) | set(rels)):
            if lab17 in e217_exact:
                continue
            c0 = min(claims.get(lab17, [None]) or [None]) if claims.get(lab17) else None
            r1 = max(rels.get(lab17, [None]) or [None]) if rels.get(lab17) else None
            lo = c0 if c0 is not None else float("-inf")
            hi = r1 if r1 is not None else float("inf")
            ov = lo < t1 and t0 < hi
            e217.append(f"E217 {lab17} (not committed here: its claim {pst(c0) if c0 else '?'} to its release "
                        f"{pst(r1) if r1 else 'NOT SEEN'}, the record's bound): {'OVERLAPS' if ov else 'apart'}")
            if ov:
                bad.append("E217 " + lab17)
    ok = not bad
    stmt = (f"no other E219 session ran on {('aifoundry1' if card.startswith('a1') else 'aifoundry2')} while this one did "
            f"({pst(t0)}-{pst(t1)}): " + ("; ".join(rows + uncopied) if rows or uncopied else "no other E219 session copied or listed")
            + "; and no E217 session: " + ("; ".join(e217) if e217 else "none read")
            if ok else f"OTHER SESSIONS OVERLAP: {', '.join(bad)}")
    R = {"B1_one_session_at_a_time": {"verdict": "PASS" if ok else "FAIL", "statement": stmt, "others": rows,
                                      "listed_not_copied": uncopied, "e217": e217}}
    labels = sorted({span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid})
    # E219: the other sessions' data directory names (the date of each session's start, Pacific)
    dirs = sorted({datetime.datetime.fromtimestamp(span(d)[0] / 1000.0, TZ).strftime("%Y-%m-%d") + "-e219-mmsweep5-"
                   + span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid})
    out = {"what": "data-e219's check B (one session at a time on the box) of one E219 session (reads only)", "session": sid,
           "checks": R, "others_labels": labels, "others_dirs": dirs, "e217_dirs_read": sorted(e217_dirs_read),
           "e217_record_read": bool(a.e217_record and os.path.exists(a.e217_record)),
           "e217_from_record_only": sorted(x.split()[1] for x in e217 if "not committed here" in x),
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(out, open(a.out, "w"), indent=1)
    line = f"B1_one_session_at_a_time {R['B1_one_session_at_a_time']['verdict']}: {stmt}"
    open(a.txt, "w").write(line + "\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
