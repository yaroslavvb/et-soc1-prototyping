#!/usr/bin/env python3
"""data-e217 (Q228; data-e212's box check, renamed for E217): the lab's check B of one released E217 session: one session at a time on
the box ("with nothing of ours on card N meanwhile", the claims). Reads this session's queue.json and those of every other E217 session of the same box this lane has copied
(their T0 to their close), and, when given, a read-only listing of the box's sessions folder (the folder names: '<T0 epoch>-<card>-<S>')
for sessions the lane has not copied. Python's own modules only; reads only.
    /usr/bin/python3 -I -B box_e217.py <this session dir> --others <session dir> ... [--listing <file>] --out b.json --txt b.txt
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
    ok = not bad
    stmt = (f"no other E217 session ran on {('aifoundry1' if card.startswith('a1') else 'aifoundry2')} while this one did "
            f"({pst(t0)}-{pst(t1)}): " + ("; ".join(rows + uncopied) if rows or uncopied else "no other session copied or listed")
            if ok else f"OTHER SESSIONS OVERLAP: {', '.join(bad)}")
    R = {"B1_one_session_at_a_time": {"verdict": "PASS" if ok else "FAIL", "statement": stmt, "others": rows,
                                      "listed_not_copied": uncopied}}
    labels = sorted({span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid})
    # E217: the other sessions' data directory names (the date of each session's start, Pacific)
    dirs = sorted({datetime.datetime.fromtimestamp(span(d)[0] / 1000.0, TZ).strftime("%Y-%m-%d") + "-e217-mmsweep4-"
                   + span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid})
    out = {"what": "data-e217's check B (one session at a time on the box) of one E217 session (reads only)", "session": sid,
           "checks": R, "others_labels": labels, "others_dirs": dirs, "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(out, open(a.out, "w"), indent=1)
    line = f"B1_one_session_at_a_time {R['B1_one_session_at_a_time']['verdict']}: {stmt}"
    open(a.txt, "w").write(line + "\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
