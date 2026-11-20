#!/usr/bin/env python3
"""E218's never-run search REPEATED right before the first card command, and its judgement (Q230, lane kit-e218, Thu 19 Nov 2026, before any
E218 datum). E218.md section 4: "The card lane repeats this scan right before its first card command (E215's step 6n form; a point it finds run
then is labelled 'ran before' and leaves every rule, said); the scan's result depends on when it runs, because data lanes keep adding files."
Runbook step 6n (rb/s06n_neverrun_e218.sh) calls it at the desk. Standard library only here; it runs the registration's scanner UNCHANGED
(desk/neverrun_e218.py, by its pinned sha256 in SHA256SUMS-e218-registration: its scan reads MM1-v3.2's measured points through MM1-v3.2's data
loader and its report e218_v32.py's Never class, numpy through them) as a subprocess and judges its outputs. E215's step-6n tool's form
(tools/claims-v3/e215/desk/neverrun_card_e215.py, landed in 8bde0182, which E215 arm A ran today: 60 of 60 never ran), with E218's readings.

    /usr/bin/python3 -I -B tools/claims-v3/e218/desk/neverrun_card_e218.py run DIR --arm A --lab LAB --lanes OUT
        1. desk/neverrun_e218.py scan --lab LAB --lanes OUT --out DIR       (the registration's scan: DIR/scan-e218-reg.json)
        2. desk/neverrun_e218.py report --scan DIR/scan-e218-reg.json --points LAB/tools/matmul/mm1/v3.2/out/e218/points-e218.csv --out DIR
                                                                            (its verdicts on the 54 landed points, as the registration ran it:
                                                                            DIR/neverrun-e218.json, DIR/neverrun-e218.txt)
        3. THE JUDGEMENT: DIR/judge-e218-A.json and .txt, DIR/labels-e218-A.json (the scorer's --labels form, {"A": {"ran_before_points":
           [...]}}, always written, its list empty when nothing ran); its last line "NEVER-RUN-E218 arm A: ..."
    /usr/bin/python3 -I -B tools/claims-v3/e218/desk/neverrun_card_e218.py check-labels FILE    every label names a registered point
                                                                                                (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

THE JUDGEMENT (E218.md 4; the kit's reading): every one of E218's 52 REGISTERED points (points-e218.json) whose verdict the report now reads not
never run, under its family's registered reading (F the shape token on ANY card; G and Gt the token on aifoundry3 card 0 by E213's classes - a
folder naming aifoundry3 or a3, or naming no card - or an MM1-v3.2 point of it there; Y the configuration (shape, mask) on aifoundry3 card 0), is
labelled 'ran before' and leaves every rule and head-to-head (the scorer's --labels): E218.md's rule, whatever the date of the record (the
conservative side; E215's date reading does not keep a point here). REPORTED beside each, never deciding: the report's own evidence, the
literal scan plus the fit lane's stand-in (the registration's union), and the files the scan names for the point's token in the classes counted
for its reading (the scan record keeps up to six a class), each dated - a lab file by the commit that added it (its committer time), a lane file
under OUT by its modification time - against MM1-v3.2's land 4e386f75 (the points' and forecasts' freeze line, committed 19:50:04 PST Thu 19 Nov
2026). The two points the registration dropped (D1: g07t, y03a) are not registered points: their verdicts are REPORTED. A label is one point
(every E218 point is its own case); the labels are checked against points-e218.json before they are written (exit 10 on a label naming
nothing). REPORTED, never a gate: the card lane writes a dated note before the data commit when any point is labelled, and passes the labels file
to the scorer at step 13. NOT SEARCHED, as registered: the box's own disk and the model session's uncommitted folders. RB_DESKTEST=1 lets
E218_NR_SCANNER name a stand-in scanner (the runbook's desk test only).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = os.path.join(HERE, "neverrun_e218.py")
SCANNER_PIN = "f9744c7814197e0971c0530cca6842a942f5c426a135cdeedda8661b55079260"       # SHA256SUMS-e218-registration's line for it
LANDED_POINTS = "tools/matmul/mm1/v3.2/out/e218/points-e218.csv"                          # the 54 landed points, as the registration's report read them
LANDED_POINTS_PIN = "1771826ee5a05327a2516b51345f9f0ef198c029b072e3d587e3d490cac54936"
POINTS = os.path.join(E, "points-e218.json")
FREEZE = "4e386f7519a236fb0bf8c43d26f8303be57e09a2"       # MM1-v3.2's land, committed 19:50:04 PST Thu 19 Nov 2026 (E218.md section 0)
CARD = "aifoundry3 card 0"
DROPPED = ("g07t", "y03a")                                # E218.md D1


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def git(lab, *a):
    r = subprocess.run(["git", "-C", lab] + list(a), capture_output=True, text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    return r.returncode, r.stdout.strip()


def freeze_epoch(lab):
    """(epoch or None, what): the freeze line from the lab's own history."""
    rc, out = git(lab, "log", "-1", "--format=%ct", FREEZE)
    return (int(out), f"MM1-v3.2's land {FREEZE[:8]}") if rc == 0 and out.isdigit() else (None, "MM1-v3.2's land not in the lab")


def counted_for_a3(c):
    """E213's classes (e218_v32.counted_for, neverrun_e215.counted_for): a folder naming aifoundry3 card 0, or naming no card"""
    return c in (CARD, "no card named")


def date_of(lab, lanes, rel):
    """(epoch or None, how): a lab file by the commit that added it; a lane file by its modification time."""
    if rel.startswith("W/out/"):
        try:
            return int(os.stat(os.path.join(lanes, rel[len("W/out/"):])).st_mtime), "its modification time"
        except OSError:
            return None, "unreadable now (not datable)"
    rc, out = git(lab, "log", "--diff-filter=A", "--format=%ct", "--", rel)
    ts = [int(x) for x in out.split() if x.isdigit()]
    if rc == 0 and ts:
        return min(ts), "the commit that added it"
    return None, "no commit adds it (not datable)"


def registered():
    P = json.load(open(POINTS))
    return {p["id"]: p for p in P["points"] if p.get("role") == "point"}


def check_labels(lab_obj):
    pts = registered()
    bad = []
    if not isinstance(lab_obj, dict):
        return ["not an object"]
    for arm, L in lab_obj.items():
        if arm != "A" or not isinstance(L, dict):
            bad.append(f"arm {arm!r}")
            continue
        bad += [f"{arm}:{x}" for x in L.get("ran_before_points", []) if x not in pts]
        bad += [f"{arm}:{k}" for k in L if k != "ran_before_points"]
    return bad


def files_of(S, token, reading, lab, lanes, fe):
    """the files the scan record names for the token in the classes counted for the reading (up to six a class, as the record keeps them), dated"""
    out = []
    for c, v in sorted((S.get("tokens", {}).get(token) or {}).items()):
        if c == "SUBTRACTED" or (reading != "F" and not counted_for_a3(c)):
            continue
        for rel in v.get("files", []):
            ep, how = date_of(lab, lanes, rel)
            out.append({"path": rel, "class": c, "epoch": ep, "dated_by": how,
                        "vs_freeze": "not datable" if ep is None or fe is None else ("before" if ep < fe else "after")})
    return out


def run(d, arm, lab, lanes):
    if arm != "A":
        print("usage: run DIR --arm A --lab LAB --lanes OUT")
        return 2
    scanner = SCANNER
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E218_NR_SCANNER"):
        scanner = os.environ["E218_NR_SCANNER"]
    elif sha(SCANNER) != SCANNER_PIN:
        print(f"REFUSED: the registration's scanner {SCANNER} is {sha(SCANNER)}, pinned {SCANNER_PIN}")
        return 4
    lp = os.path.join(lab, LANDED_POINTS)
    if not os.path.isfile(lp) or sha(lp) != LANDED_POINTS_PIN:
        print(f"REFUSED: the landed points {LANDED_POINTS} are not at their pin {LANDED_POINTS_PIN[:12]}")
        return 4
    os.makedirs(d, exist_ok=True)
    t0 = now()
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "scan-e218-reg.json")):
        print(f"SCAN FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "report", "--scan", os.path.join(d, "scan-e218-reg.json"), "--points", lp,
                        "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "neverrun-e218.json")):
        print(f"REPORT FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    rep = json.load(open(os.path.join(d, "neverrun-e218.json")))
    S = json.load(open(os.path.join(d, "scan-e218-reg.json")))
    pts = registered()
    lit = {x["id"]: x for x in rep["literal"]["points"]}
    uni = {x["id"]: x for x in rep["standin_union_REPORTED"]["points"]}
    miss = sorted(pid for pid in pts if pid not in lit)
    if miss:
        print(f"REPORT FAILED: the report holds no verdict for {miss}")
        return 14
    fe, fwhat = freeze_epoch(lab)
    judged, labelled = [], []
    for pid in sorted(pts, key=lambda k: list(pts).index(k)):
        x = lit[pid]
        if x["never_run"]:
            continue
        files = files_of(S, x["token"], x["family"] if x["family"] == "F" else "a3", lab, lanes, fe)
        judged.append({"id": pid, "family": x["family"], "token": x["token"], "mask": x["mask"], "rule": x["rule"], "evidence": x["evidence"],
                       "with_standin_REPORTED": {"never_run": uni.get(pid, {}).get("never_run")}, "files_REPORTED": files,
                       "ran_before": True, "why": "the registered reading finds it run (E218.md 4: labelled 'ran before', leaves every rule)"})
        labelled.append(pid)
    dropped = [{"id": q, "never_run": lit.get(q, {}).get("never_run"), "evidence": lit.get(q, {}).get("evidence"),
                "note": "dropped at the registration (E218.md D1): not a registered point; REPORTED"} for q in DROPPED]
    labels = {arm: {"ran_before_points": sorted(labelled)}}
    bad = check_labels(labels)
    if bad:
        print(f"LABELS-REFUSED (a label names nothing in points-e218.json): {bad}")
        return 10
    n_never = sum(1 for pid in pts if lit[pid]["never_run"])
    res = {"what": "E218's never-run search repeated and judged (desk/neverrun_card_e218.py)", "arm": arm, "card": CARD, "dir": os.path.basename(d),
           "started": t0, "ended": now(), "scanner_sha256": sha(scanner), "scan_sha256": rep["scan_sha256"], "files_read": rep["files_read"],
           "lab_head": rep.get("lab_head"), "scan_window": rep.get("scan_window"), "points_report_on": LANDED_POINTS,
           "freeze_line_REPORTED": {"epoch": fe, "what": fwhat}, "n_points": len(pts), "n_never_run": n_never,
           "judged": judged, "ran_before": labelled, "dropped_REPORTED": dropped, "labels": labels,
           "standin_union_REPORTED": {"ran": [q for q in rep["standin_union_REPORTED"]["ran"] if q in pts]},
           "rule": "E218.md 4: a registered point the repeated scan finds run is labelled 'ran before' and leaves every rule (whatever the date)",
           "not_searched": "the box's own disk and the model session's uncommitted folders (as registered)"}
    json.dump(res, open(os.path.join(d, f"judge-e218-{arm}.json"), "w"), indent=1, sort_keys=True)
    json.dump(labels, open(os.path.join(d, f"labels-e218-{arm}.json"), "w"), indent=1, sort_keys=True)
    dr = "; ".join(f"{q['id']} {'never ran' if q['never_run'] else 'reads as run'}" for q in dropped)
    line = (f"NEVER-RUN-E218 arm {arm}: {n_never} of {len(pts)} registered points never ran on {CARD} by their family's reading (scan "
            f"{rep['scan_sha256'][:12]}, {rep['files_read']} files); ran, labelled 'ran before' (E218.md 4): {' '.join(sorted(labelled)) or 'none'}; "
            f"the dropped (D1, REPORTED): {dr}")
    txt = [line] + [f"  {j['id']} {j['family']} {j['token']} {j['mask']}: RAN BEFORE - {j['why']}; evidence {json.dumps(j['evidence'], sort_keys=True)[:200]}; "
                    + "; ".join(f"{f['path']} ({f['class']}, {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(f['epoch'])) if f['epoch'] else 'not datable'}"
                                f", {f['vs_freeze']} the freeze line)" for f in j["files_REPORTED"][:6]) for j in judged] + [line]
    open(os.path.join(d, f"judge-e218-{arm}.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt[1:]))
    return 0


def main(argv):
    if argv[:1] == ["run"] and len(argv) == 8 and argv[2] == "--arm" and argv[4] == "--lab" and argv[6] == "--lanes":
        return run(os.path.abspath(argv[1]), argv[3], os.path.abspath(argv[5]), os.path.abspath(argv[7]))
    if argv[:1] == ["check-labels"] and len(argv) == 2:
        try:
            obj = json.load(open(argv[1]))
        except (OSError, ValueError) as e:
            print(f"LABELS-REFUSED: unreadable ({type(e).__name__})")
            return 10
        bad = check_labels(obj)
        print("LABELS-OK" if not bad else f"LABELS-REFUSED: {bad}")
        return 0 if not bad else 10
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
