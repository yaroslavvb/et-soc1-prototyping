#!/usr/bin/env python3
"""E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE NEVER-RUN SEARCH REPEATED right before the card day's first card
command (runbook step 6n, rb/s06n_neverrun_e209.sh; E209.md sections 4 and 7: "The card lane repeats this search right before its first card
command ... a point whose case ran on this card in a record dated before MM1-v2's freeze line is labelled 'ran before' in a dated note before
the data commit ... one dated after the freeze is REPORTED"). Standard library only; reads only, but for its own folder DIR.

    /usr/bin/python3 -I -B tools/claims-v3/e209/desk/neverrun_card_e209.py DIR --lab LAB --out-root OUT --work HOMEWORK

WHAT IT RUNS, UNCHANGED: the registration's scanner and report (desk/neverrun_e209.py, with points-e209.json), from COPIES in DIR/reg/ (each
checked against SHA256SUMS-e209-registration first: that script writes its report beside itself, and the committed report must never be
overwritten): `scan --lab LAB --out-root OUT --work HOMEWORK --json DIR/found.json`, then `report DIR/found.json [--e207-points ...]`. The
registration's classes stand (COUNTED, OTHER CARD, DESK ONLY, SUBTRACTED; NOT READ: the model session's ee-* folders and scratch clones).
THE DATING (E207's rule with MM1-v2's freeze, 01:44:45 PST Tue 17 Nov 2026, in place of MM1-v1's): every COUNTED record of an E209 shape is
dated from (1) a session's start epoch in its path (sessions/<T0>-..., T<T0>-...), else (2) in the lab, the commit time of the commit that
added its data directory, else (3) the file's last write. A shape with a COUNTED record dated BEFORE the freeze makes every E209 point of that
shape RAN BEFORE (conservative: any format, data kind or mask; the card lane may narrow it to the point's case in its dated note by reading the
record, never widen it); a shape whose COUNTED records are all AFTER the freeze is REPORTED and its points stay in every rule (MM1-v2 never saw
them). OTHER CARD and DESK ONLY are REPORTED by the registration's report only.
THE OUTPUT: DIR/found.json, DIR/reg/desk/neverrun-e209.json and .txt (the registration's form), DIR/ranbefore-e209.json (the scorer's --labels
form: ran_before_points, ran_before_cases, with the dating beside), DIR/neverrun-e209-card.txt, and the last line
  "NEVER-RUN <n> of 45 points, <m> of 29 shapes[; RAN BEFORE: <ids>][; AFTER THE FREEZE (REPORTED, kept): <ids>]".
Every path it prints is in the public form (LAB, OUT, HOMEWORK). Exit 0 the search done (whatever it found: REPORTED, never a gate); 14 a
scan or the report failed; 10 a copied file not at its registered sha256.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001
    TZ = None
FREEZE = datetime.datetime(2026, 11, 17, 1, 44, 45, tzinfo=TZ).timestamp()      # MM1-v2's commit 3ca4b717, committer time
T0_RE = re.compile(r"(?:^|/)(?:sessions/|T)(\d{10})(?:-|/|$)")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pub(s, roots):
    for name, p in roots:
        if p:
            s = s.replace(p.rstrip("/") + "/", f"{name}/").replace(p.rstrip("/"), name)
    return s


def main(argv):
    if len(argv) < 1:
        print(__doc__)
        return 2
    d = os.path.abspath(argv[0])
    kv = dict(zip(argv[1::2], argv[2::2]))
    lab, out, work = kv.get("--lab"), kv.get("--out-root"), kv.get("--work")
    if not (lab and out and work):
        print(__doc__)
        return 2
    roots = [("LAB", os.path.abspath(lab)), ("OUT", os.path.abspath(out)), ("HOMEWORK", os.path.abspath(work))]
    sums = {}
    for ln in open(os.path.join(E, "SHA256SUMS-e209-registration")):
        h, p = ln.rstrip("\n").split("  ", 1)
        sums[p] = h
    os.makedirs(os.path.join(d, "reg", "desk"), exist_ok=True)
    for rel in ("desk/neverrun_e209.py", "points-e209.json"):
        src = os.path.join(E, rel)
        want = sums.get(f"tools/claims-v3/e209/{rel}")
        if not want or sha(src) != want:
            print(f"REFUSED: tools/claims-v3/e209/{rel} is not at its registered sha256")
            return 10
        shutil.copyfile(src, os.path.join(d, "reg", rel))
    nr = os.path.join(d, "reg", "desk", "neverrun_e209.py")
    found = os.path.join(d, "found.json")
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", nr, "scan", "--lab", lab, "--out-root", out, "--work", work, "--json", found],
                       capture_output=True, text=True)
    print(pub(r.stdout.strip(), roots))
    if r.returncode != 0 or not os.path.exists(found):
        print(pub(r.stderr.strip()[-2000:], roots))
        print("NEVER-RUN FAILED: the scan did not end (run the step again)")
        return 14
    args = ["/usr/bin/python3", "-I", "-B", nr, "report", found]
    e207 = os.path.join(lab, "tools", "claims-v3", "e207", "points-e207.json")
    if os.path.exists(e207):
        args += ["--e207-points", e207]
    r = subprocess.run(args, capture_output=True, text=True)
    open(os.path.join(d, "report.txt"), "w").write(pub(r.stdout, roots))
    if r.returncode != 0:
        print(pub(r.stderr.strip()[-2000:], roots))
        print("NEVER-RUN FAILED: the report did not end (run the step again)")
        return 14
    rep = json.load(open(os.path.join(d, "reg", "desk", "neverrun-e209.json")))
    F = json.load(open(found))
    sys.path.insert(0, os.path.dirname(nr))
    import neverrun_e209 as NR  # noqa: E402  (the copy at its registered sha256: its classify())
    pts = json.load(open(os.path.join(d, "reg", "points-e209.json")))["points"]
    by_shape = {}
    for h in F["hits"]:
        cls, card = NR.classify(h["root"], h["path"])
        if cls != "COUNTED":
            continue
        base = {"lab": lab, "out": out, "work": work}[h["root"]]
        full = os.path.join(base, h["path"])
        m = T0_RE.search(h["path"])
        if m:
            t, how = float(m.group(1)), "a session's start epoch in its path"
        else:
            t, how = None, None
            if h["root"] == "lab" and h["path"].startswith("docs/reports/data/"):
                dd = "/".join(h["path"].split("/")[:4])
                c = subprocess.run(["git", "-C", lab, "log", "--diff-filter=A", "--format=%ct", "--", dd], capture_output=True, text=True)
                ts = [int(x) for x in c.stdout.split()]
                if ts:
                    t, how = float(min(ts)), "the commit that added its data directory"
            if t is None:
                try:
                    t, how = os.path.getmtime(full), "the file's last write"
                except OSError:
                    t, how = 0.0, "unreadable: counted as before"
        for s in h["shapes"]:
            by_shape.setdefault(s, []).append({"path": f"<{h['root']}>/{h['path']}", "epoch": t, "dated_by": how,
                                               "before_freeze": t <= FREEZE})
    ran_before, after = [], []
    for p in pts:
        recs = by_shape.get(p["arm"], [])
        if any(x["before_freeze"] for x in recs):
            ran_before.append(p["id"])
        elif recs:
            after.append(p["id"])
    never = rep.get("never_ran_on_this_card")
    words = (f"NEVER-RUN {never} of {rep.get('of')} points, {rep.get('shapes_never_on_this_card')} of {rep.get('n_shapes')} shapes"
             + (f"; RAN BEFORE: {', '.join(ran_before)}" if ran_before else "")
             + (f"; AFTER THE FREEZE (REPORTED, kept): {', '.join(after)}" if after else ""))
    lab_out = {"experiment": "E209", "what": "the card lane's never-run search, repeated (neverrun_card_e209.py): the scorer's --labels form",
               "freeze": {"what": "MM1-v2's commit 3ca4b717, committer time", "epoch": FREEZE, "pst": "2026-11-17 01:44:45 PST"},
               "ran_before_points": ran_before, "ran_before_cases": [], "after_freeze_REPORTED": after,
               "counted_records_by_shape": by_shape, "words": words, "scan": {k: F[k] for k in F if k != "hits"}}
    json.dump(json.loads(pub(json.dumps(lab_out), roots)), open(os.path.join(d, "ranbefore-e209.json"), "w"), indent=1, sort_keys=True)
    txt = pub(r.stdout, roots) + words + "\n"
    open(os.path.join(d, "neverrun-e209-card.txt"), "w").write(txt)
    sys.stdout.write(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
