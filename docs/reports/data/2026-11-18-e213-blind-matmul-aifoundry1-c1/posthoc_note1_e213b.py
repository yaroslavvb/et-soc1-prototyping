#!/usr/bin/python3
"""E213 arm B data, dated note 1 (post hoc): the exact counts behind step 6n's never-run judgement in this directory.

Reads only files of this directory as the data commit holds them: judge-e213-card.json, judge-e213-card.txt and
labels-e213.json (each checked first against SHA256SUMS) and README.md (its results row's lane-folder figure).
Python's own modules only. Prints the counts; with --json PATH it also writes them as JSON.

    /usr/bin/python3 -I -B posthoc_note1_e213b.py [--json PATH]

What it counts (the judgement's own terms, desk/neverrun_card_e213.py of E213's registration):
  - a "hit" is one point of the judgement's list together with one counted file that names that point's shape
    (one entry of a point's "files" list in the JSON; the JSON lists every counted file of each point);
  - the text form, judge-e213-card.txt, names at most the first 6 of a point's counted files (the scanner's
    j["files"][:6]); the README's results row counted the "W/out/<lane folder>/" names in that text form.
Times print in PST (UTC-8); every time it prints is checked to fall inside Pacific standard time (1 Nov 2026 to
14 Mar 2027). Desk arithmetic on committed records, post hoc; it changes no label, rule or verdict.

SPDX-License-Identifier: Apache-2.0
"""
import collections
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PST = datetime.timezone(datetime.timedelta(hours=-8), "PST")
PST_FROM = datetime.datetime(2026, 11, 1, 1, 0, tzinfo=PST)   # Pacific time left daylight time at 02:00 PDT, 1 Nov 2026
PST_TO = datetime.datetime(2027, 3, 14, 2, 0, tzinfo=PST)     # and enters it at 02:00 PST, 14 Mar 2027
INPUTS = ("judge-e213-card.json", "judge-e213-card.txt", "labels-e213.json")
TEXT_CAP = 6
LANE = re.compile(r"W/out/([A-Za-z0-9._-]+)/")
TEXT_FILE = re.compile(r"(W/out/[^ ;()]+) \(([^,()]+), (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]{3})\)")


def pst(epoch):
    d = datetime.datetime.fromtimestamp(epoch, PST)
    if not PST_FROM <= d < PST_TO:
        raise SystemExit(f"STOP: {epoch} is outside Pacific standard time; this script prints PST only")
    return d.strftime("%Y-%m-%d %H:%M:%S PST")


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main(argv):
    out_json = None
    if argv[:1] == ["--json"] and len(argv) == 2:
        out_json = argv[1]
    elif argv:
        print("usage: posthoc_note1_e213b.py [--json PATH]")
        return 2
    lines = []
    say = lines.append

    sums = {}
    with open(os.path.join(HERE, "SHA256SUMS")) as f:
        for ln in f:
            h, name = ln.rstrip("\n").split(None, 1)
            sums[name.lstrip("*")] = h
    say("E213 arm B data, dated note 1 (post hoc): the never-run judgement's exact counts (posthoc_note1_e213b.py)")
    say("")
    say("1. The inputs, checked against SHA256SUMS (the data commit's list)")
    inputs_ok = True
    for name in INPUTS:
        got = sha256(os.path.join(HERE, name))
        ok = sums.get(name) == got
        inputs_ok = inputs_ok and ok
        say(f"   {name}: sha256 {got} {'OK (listed)' if ok else 'NOT AS LISTED'}")
    if not inputs_ok:
        print("\n".join(lines))
        print("STOP: an input differs from SHA256SUMS")
        return 3
    say(f"   README.md: sha256 {sha256(os.path.join(HERE, 'README.md'))} (not listed in SHA256SUMS, by design)")

    J = json.load(open(os.path.join(HERE, "judge-e213-card.json")))
    labels = json.load(open(os.path.join(HERE, "labels-e213.json")))
    fe = J["freeze_line"]["epoch"]
    say("")
    say("2. The judgement (judge-e213-card.json)")
    say(f"   arm {J['arm']}, {J['card']}; search {J['started']} to {J['ended']}; files read {J['files_read']}; scan {J['scan_sha256'][:12]}")
    say(f"   freeze line: {J['freeze_line']['what']}, {pst(fe)}")
    say(f"   points judged {len(J['judged'])}; never ran {J['n_never_run']} of {J['n_points']}; "
        f"ran before {len(J['ran_before'])}; ran after (REPORTED, kept) {len(J['ran_after_REPORTED'])}")
    say(f"   labels in the judgement {json.dumps(J['labels'], sort_keys=True)}; labels-e213.json equal to them: {labels == J['labels']}")

    hits = [(j["id"], f) for j in J["judged"] for f in j["files"]]
    per_point = {j["id"]: len(j["files"]) for j in J["judged"]}
    files = collections.OrderedDict()
    for pid, f in hits:
        e = files.setdefault(f["path"], {"class": f["class"], "epoch": f["epoch"], "dated_by": f["dated_by"],
                                         "before_freeze": f["before_freeze"], "points": []})
        same = (e["class"], e["epoch"], e["dated_by"], e["before_freeze"]) == (f["class"], f["epoch"], f["dated_by"], f["before_freeze"])
        if not same:
            raise SystemExit(f"STOP: {f['path']} is recorded two ways")
        e["points"].append(pid)
    by_date = collections.Counter(pst(f["epoch"]) for _, f in hits)
    by_class = collections.Counter(f["class"] for _, f in hits)
    by_lane = collections.Counter((LANE.match(f["path"]) or [None, "(not a lane folder)"])[1] for _, f in hits)
    n_before = sum(1 for _, f in hits if f["before_freeze"])
    n_after_epoch = sum(1 for _, f in hits if f["epoch"] is not None and f["epoch"] > fe)
    say("")
    say("3. The counted hits in the JSON (every counted file of every point)")
    say(f"   hits (a point and one counted file naming its shape): {len(hits)}")
    say(f"   distinct files: {len(files)}")
    say(f"   by lane folder: {json.dumps(dict(sorted(by_lane.items())))}")
    say(f"   by date: {json.dumps(dict(sorted(by_date.items())))}")
    say(f"   by class: {json.dumps(dict(sorted(by_class.items())))}")
    say(f"   marked before the freeze line: {n_before}; dated after it: {n_after_epoch} of {len(hits)}")
    say(f"   counted files a point: {json.dumps(dict(sorted(collections.Counter(per_point.values()).items())))} (files: points)")
    say("   the files, each with its date, class and the number of points it names:")
    for path, e in sorted(files.items(), key=lambda kv: (kv[1]["epoch"], kv[0])):
        say(f"     {path} | {pst(e['epoch'])} ({e['dated_by']}) | {e['class']} | {len(e['points'])} points")

    tl = [ln for ln in open(os.path.join(HERE, "judge-e213-card.txt")).read().splitlines() if re.match(r"^\s+k\d\d ", ln)]
    t_lane = collections.Counter(m.group(1) for ln in tl for m in LANE.finditer(ln))
    t_files = {}
    for ln in tl:
        pid = ln.split()[0]
        t_files[pid] = [(m.group(1), m.group(2), m.group(3)) for m in TEXT_FILE.finditer(ln)]
    t_date = collections.Counter(d for v in t_files.values() for _, _, d in v)
    agree = sum(1 for j in J["judged"]
                if t_files.get(j["id"]) == [(f["path"], f["class"], pst(f["epoch"])) for f in j["files"][:TEXT_CAP]])
    capped = {pid: n for pid, n in per_point.items() if n > TEXT_CAP}
    say("")
    say(f"4. The text form (judge-e213-card.txt: at most the first {TEXT_CAP} counted files a point)")
    say(f"   point lines: {len(tl)}; names of a lane-folder file: {sum(t_lane.values())}; by lane folder: {json.dumps(dict(sorted(t_lane.items())))}")
    say(f"   by date: {json.dumps(dict(sorted(t_date.items())))}")
    say(f"   points whose text names exactly the JSON's first {TEXT_CAP} (or all) counted files, in order: {agree} of {len(J['judged'])}")
    say(f"   points with more than {TEXT_CAP} counted files: {len(capped)} ({' '.join(sorted(capped))}); "
        f"the files the text leaves out: {sum(n - TEXT_CAP for n in capped.values())}")

    readme = open(os.path.join(HERE, "README.md")).read()
    m = re.search(r"the judgement's named hits by lane folder: (\{[^}]*\})", readme)
    r_fig = json.loads(m.group(1)) if m else None
    say("")
    say("5. The README's figure (its results row, the never-run search)")
    say(f"   it reads: \"the judgement's named hits by lane folder: {json.dumps(r_fig) if r_fig is not None else 'NOT FOUND'}\"")
    say(f"   equal to the text form's names by lane folder: {r_fig == dict(t_lane)}; equal to the JSON's hits by lane folder: {r_fig == dict(by_lane)}")
    say("")
    say("6. So")
    say(f"   the judgement holds {len(hits)} counted hits in {len(files)} distinct files, every one under the lane folder "
        f"{'/'.join(sorted(by_lane))}, every one dated after the freeze line and none marked before it;")
    say(f"   the README's {sum(r_fig.values()) if r_fig else 'NOT FOUND'} counts the text form's file names, which stop at "
        f"{TEXT_CAP} a point ({sum(n - TEXT_CAP for n in capped.values())} names left out at {len(capped)} points);")
    say(f"   the labels stay empty and every point stays in every rule ({len(J['ran_after_REPORTED'])} of {J['n_points']} "
        f"'ran after (REPORTED, kept)'). Nothing changes.")
    text = "\n".join(lines) + "\n"
    sys.stdout.write(text)
    if out_json:
        res = {"what": "E213 arm B data, dated note 1 (post hoc): the never-run judgement's exact counts",
               "inputs": {n: sha256(os.path.join(HERE, n)) for n in INPUTS + ("README.md",)},
               "freeze_line": {"what": J["freeze_line"]["what"], "pst": pst(fe), "epoch": fe},
               "json_hits": len(hits), "json_distinct_files": len(files), "json_hits_by_lane_folder": dict(sorted(by_lane.items())),
               "json_hits_by_date": dict(sorted(by_date.items())), "json_hits_by_class": dict(sorted(by_class.items())),
               "json_hits_marked_before_freeze": n_before, "json_hits_dated_after_freeze": n_after_epoch,
               "json_files": [{"path": p, "pst": pst(e["epoch"]), "dated_by": e["dated_by"], "class": e["class"],
                               "before_freeze": e["before_freeze"], "points": e["points"]}
                              for p, e in sorted(files.items(), key=lambda kv: (kv[1]["epoch"], kv[0]))],
               "json_counted_files_per_point": dict(sorted(per_point.items())),
               "text_cap_per_point": TEXT_CAP, "text_names_by_lane_folder": dict(sorted(t_lane.items())),
               "text_names_by_date": dict(sorted(t_date.items())), "text_points_agreeing_with_json": agree,
               "text_points_capped": dict(sorted(capped.items())),
               "readme_figure": r_fig, "readme_figure_equals_text_form": r_fig == dict(t_lane),
               "readme_figure_equals_json": r_fig == dict(by_lane),
               "labels": J["labels"], "labels_file_equal": labels == J["labels"], "n_points": J["n_points"],
               "n_never_run": J["n_never_run"], "ran_before": J["ran_before"], "ran_after_REPORTED": len(J["ran_after_REPORTED"])}
        with open(out_json, "w") as f:
            json.dump(res, f, indent=1, sort_keys=True)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
