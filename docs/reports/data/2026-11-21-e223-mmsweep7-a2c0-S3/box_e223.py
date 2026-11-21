#!/usr/bin/env python3
"""data-e223 (Q239; data-e221's box_e221.py, Q235, itself data-e219's and data-e212's box check): the lab's check B of one released E223 session: one
session at a time on the box ("one session at a time" on aifoundry1, post #16; and on aifoundry2 the card's one session). Reads this
session's queue.json and those of every other E223 session of the same box this lane has copied (their T0 to their close), when given a
listing of the box's sessions folder (the folder names: '<T0 epoch>-<card>-<S>') for E223 sessions the lane has not copied, and (in
place of E219's E217 record) every session folder committed in the lab whose session/queue.json names a card on the same box and whose
T0 is within a day of this session's (the lab's own card days, E224's two arms and E220's among them, and any other experiment's sessions:
exact spans, their T0 to their close). Python's own modules only; reads only.
    /usr/bin/python3 -I -B box_e223.py <this session dir> --others <session dir> ... [--listing <file>] [--lab <lab top>]
        --out b.json --txt b.txt
"""
import argparse
import datetime
import glob
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
    ap.add_argument("--lab", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    t0, t1, card, sid = span(a.session)
    box = card[:2]
    boxname = {"a1": "aifoundry1", "a2": "aifoundry2"}.get(box, box)
    rows, bad = [], []
    for d in a.others:
        o0, o1, oc, osid = span(d)
        if osid == sid or oc[:2] != box:
            continue
        ov = o0 < t1 and t0 < o1
        rows.append(f"{osid} ({oc}) {pst(o0)}-{pst(o1)}: {'OVERLAPS' if ov else 'apart'}")
        if ov:
            bad.append(osid)
    uncopied = []
    if a.listing and os.path.exists(a.listing):
        for ln in open(a.listing):
            m = re.search(r"\b(\d{10})-(a\dc\d)-(S\d)\b", ln)
            if m and m.group(0) != sid and m.group(2)[:2] == box and not any(m.group(0) in r for r in rows + uncopied):
                st = int(m.group(1)) * 1000.0
                uncopied.append(f"{m.group(0)} (T0 {pst(st)}; not copied: only its start is known)")
                if t0 <= st <= t1:
                    bad.append(m.group(0))
    lab_rows, lab_read = [], []
    if a.lab:
        for qp in sorted(glob.glob(os.path.join(a.lab, "docs", "reports", "data", "*", "session", "queue.json"))):
            try:
                q = json.load(open(qp))
                o0, o1, oc = q["t0"] * 1000.0, q.get("t_close_ms"), q.get("card") or ""
            except (ValueError, KeyError, TypeError):
                continue
            if oc[:2] != box or o1 is None or abs(o0 - t0) > 86400e3:
                continue
            folder = qp.split(os.sep)[-3]
            if f"{q['t0']}-" in sid and folder.endswith(sid.split("-", 1)[1]):
                continue
            if "-e223-" in folder:
                continue  # E223's own committed sessions are read from the lane's copies (--others)
            lab_read.append(folder)
            ov = o0 < t1 and t0 < o1
            lab_rows.append(f"{folder} ({oc}, committed) {pst(o0)}-{pst(o1)}: {'OVERLAPS' if ov else 'apart'}")
            if ov:
                bad.append(folder)
    ok = not bad
    stmt = (f"no other E223 session ran on {boxname} while this one did ({pst(t0)}-{pst(t1)}): "
            + ("; ".join(rows + uncopied) if rows or uncopied else "no other E223 session copied or listed")
            + "; and no other session committed in the lab within a day on that box overlaps it: "
            + ("; ".join(lab_rows) if lab_rows else "none read")
            if ok else f"OTHER SESSIONS OVERLAP: {', '.join(bad)}")
    R = {"B1_one_session_at_a_time": {"verdict": "PASS" if ok else "FAIL", "statement": stmt, "others": rows,
                                      "listed_not_copied": uncopied, "lab_committed": lab_rows}}
    labels = sorted({span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid and span(d)[2][:2] == box})
    dirs = sorted({datetime.datetime.fromtimestamp(span(d)[0] / 1000.0, TZ).strftime("%Y-%m-%d") + "-e223-mmsweep7-"
                   + span(d)[3].split("-", 1)[1] for d in a.others if span(d)[3] != sid and span(d)[2][:2] == box})
    out = {"what": "data-e223's check B (one session at a time on the box) of one E223 session (reads only)", "session": sid,
           "box": boxname, "checks": R, "others_labels": labels, "others_dirs": dirs, "lab_dirs_read": lab_read,
           "python": sys.version.split()[0], "interpreter": sys.executable}
    json.dump(out, open(a.out, "w"), indent=1)
    line = f"B1_one_session_at_a_time {R['B1_one_session_at_a_time']['verdict']}: {stmt}"
    open(a.txt, "w").write(line + "\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
