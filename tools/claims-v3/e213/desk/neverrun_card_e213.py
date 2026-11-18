#!/usr/bin/env python3
"""E213's never-run search REPEATED right before an arm's first card command, and its judgement (Q216, lane kit-e213, Tue 17 Nov 2026, before
any E213 datum). E213.md section 4: "The card lanes repeat this scan right before their first card command (desk/neverrun_e213.py scan, then
report with desk/candidates-e213.json, on the lab at GitHub main then and the folders then, E213's own folders subtracted): a point whose case ran
on its card in a record dated before its freeze line (arm A: MM1-v3's land, pushed 20:52:46 PST Tue 17 Nov 2026; arm B: this registration's push,
which the land lane records) is labelled 'ran before' in a dated note before the data commit and leaves every rule and head-to-head (the scorer's
--labels); one dated after its freeze line is REPORTED and stays in every rule (the model never saw it). The kit checks that every label names a
point or case of points-e213.json (the scorer refuses one that does not: exit 10)." Runbook step 6n (rb/s06n_neverrun_e213.sh) calls it at the
desk. Standard library only; it runs the registration's scanner UNCHANGED (desk/neverrun_e213.py, by its pinned sha256) as a subprocess and
judges its outputs.

    /usr/bin/python3 -I -B tools/claims-v3/e213/desk/neverrun_card_e213.py run DIR --arm A|B --lab LAB --lanes OUT
        1. desk/neverrun_e213.py scan --lab LAB --lanes OUT --out DIR          (the registration's scan: DIR/scan-e213.json)
        2. desk/neverrun_e213.py report --scan DIR/scan-e213.json --points desk/candidates-e213.json --out DIR
                                                                               (its verdicts: DIR/neverrun-e213.json, DIR/neverrun-e213.txt)
        3. THE JUDGEMENT for the arm: DIR/judge-e213-<arm>.json and .txt, DIR/labels-e213-<arm>.json (the scorer's --labels form,
           {"<arm>": {"ran_before_points": [...], "ran_before_cases": [...]}}, always written, its lists empty when nothing ran before);
           its last line "NEVER-RUN-E213 arm <arm>: ..."
    /usr/bin/python3 -I -B tools/claims-v3/e213/desk/neverrun_card_e213.py check-labels FILE    every label names a point or case of the arm
                                                                                                (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

THE JUDGEMENT (E213.md 4; the kit's reading of "a record dated"): for every SCORED point of the arm whose verdict the report now reads not never
run (arm A: its token has a hit on any card or among MM1-v3's measured points; arm B: a hit counted for aifoundry1 card 1), the kit rescans the
same roots by the scanner's own rules (its functions, imported from the pinned file) for that token alone and lists EVERY file holding it, each
with its date: a lab file by the commit that added it (git log --diff-filter=A, its committer time), a lane file under OUT by its modification
time. A point with any counted hit file dated before the arm's FREEZE LINE (arm A: the commit b1493082's committer time, its push; arm B: the
registration commit's - the commit that added tools/claims-v3/e213/E213.md - committer time, its push by commit_lab.sh), or with a file that cannot
be dated, is labelled 'ran before' (the conservative side: it leaves every rule); a point whose every hit is dated after the freeze line is
REPORTED and kept. Since the scan is shape-level, a token's label covers every scored point of the arm with that token; ran_before_cases names
their cases. The labels are checked against points-e213.json before they are written (exit 10 on a label naming nothing). REPORTED, never a gate:
the card lane writes a dated note before the data commit when any point is labelled, and passes the labels file to the scorer at step 13.
NOT SEARCHED, as registered: the boxes' own disks and the model session's uncommitted folders. RB_DESKTEST=1 lets E213_NR_SCANNER name a stand-in
scanner (the runbook's desk test only). SPDX-License-Identifier: Apache-2.0
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
SCANNER = os.path.join(HERE, "neverrun_e213.py")
SCANNER_PIN = "d603ff8b4fac97a8adbafe0bf4ea0e99e555576c7601c93484362c0cd3500546"       # SHA256SUMS-e213-registration's line for it
CANDIDATES = os.path.join(HERE, "candidates-e213.json")
POINTS = os.path.join(E, "points-e213.json")
ARM_A_FREEZE = "b149308280a73396516937304037af57a5563c16"       # MM1-v3's land, pushed 20:52:46 PST Tue 17 Nov 2026 (E213.md section 0)
CARD = {"A": "aifoundry3 card 0", "B": "aifoundry1 card 1"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def git(lab, *a):
    r = subprocess.run(["git", "-C", lab] + list(a), capture_output=True, text=True, env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    return r.returncode, r.stdout.strip()


def freeze_epoch(lab, arm):
    """(epoch or None, what): the arm's freeze line from the lab's own history."""
    if arm == "A":
        rc, out = git(lab, "log", "-1", "--format=%ct", ARM_A_FREEZE)
        return (int(out), f"MM1-v3's land {ARM_A_FREEZE[:8]}") if rc == 0 and out.isdigit() else (None, "MM1-v3's land not in the lab")
    rc, out = git(lab, "log", "--diff-filter=A", "--format=%H %ct", "--", "tools/claims-v3/e213/E213.md")
    lines = [ln.split() for ln in out.splitlines() if ln.strip()]
    if rc != 0 or not lines:
        return None, "the registration commit not in the lab"
    h, ct = lines[-1]
    return int(ct), f"the registration commit {h[:8]}"


def load_scanner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("neverrun_e213", SCANNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def counted(NR, arm, c):
    if c == "SUBTRACTED":
        return False
    return True if arm == "A" else NR.counted_for(NR.C1, c)


def rescan(NR, lab, lanes, tokens):
    """{token: [(rel path, class)]} for the given tokens, over the scanner's own roots by its own rules (its scan(), restricted)."""
    expmap = NR.exp_cards(lab)
    roots = [os.path.join(lab, "docs", "reports", "data"), os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
             os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(("card-", "data-", "a1", "a2", "a3")))
    want = set(tokens)
    hits = {t: [] for t in tokens}
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if ".git" in dn or ".git" in fns:
                dn[:] = []
                continue
            dn.sort()
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(NR.SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > NR.MAX_BYTES:
                        continue
                    txt = NR.read_text(p)
                except (OSError, EOFError):
                    continue
                found = set(NR.RX.findall(txt)) & want
                if not found:
                    continue
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else "W/out/" + os.path.relpath(p, lanes)
                c = "SUBTRACTED" if NR.subtracted(rel) else (NR.lane_card(rel) or NR.folder_card(rel, expmap) or NR.NONE)
                for t in found:
                    hits[t].append((rel, c, p))
    return hits


def date_of(lab, lanes, rel, p):
    """(epoch or None, how): a lab file by the commit that added it; a lane file by its modification time."""
    if not rel.startswith("W/out/"):
        rc, out = git(lab, "log", "--diff-filter=A", "--format=%ct", "--", rel)
        ts = [int(x) for x in out.split() if x.isdigit()]
        if rc == 0 and ts:
            return min(ts), "the commit that added it"
        return None, "no commit adds it (not datable)"
    try:
        return int(os.stat(p).st_mtime), "its modification time"
    except OSError:
        return None, "unreadable (not datable)"


def check_labels(lab_obj):
    P = json.load(open(POINTS))
    bad = []
    for arm, L in lab_obj.items():
        if arm not in ("A", "B") or not isinstance(L, dict):
            bad.append(f"arm {arm!r}")
            continue
        ids = {p["id"] for p in P["arms"][arm]["points"] if p["role"] == "point"}
        cases = {p["case"] for p in P["arms"][arm]["points"] if p["role"] == "point"}
        bad += [f"{arm}:{x}" for x in L.get("ran_before_points", []) if x not in ids]
        bad += [f"{arm}:{x}" for x in L.get("ran_before_cases", []) if x not in cases]
        bad += [f"{arm}:{k}" for k in L if k not in ("ran_before_points", "ran_before_cases")]
    return bad


def run(d, arm, lab, lanes):
    if arm not in ("A", "B"):
        print("usage: run DIR --arm A|B --lab LAB --lanes OUT")
        return 2
    scanner = SCANNER
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E213_NR_SCANNER"):
        scanner = os.environ["E213_NR_SCANNER"]
    elif sha(SCANNER) != SCANNER_PIN:
        print(f"REFUSED: the registration's scanner {SCANNER} is {sha(SCANNER)}, pinned {SCANNER_PIN}")
        return 4
    os.makedirs(d, exist_ok=True)
    t0 = now()
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "scan-e213.json")):
        print(f"SCAN FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "report", "--scan", os.path.join(d, "scan-e213.json"), "--points", CANDIDATES,
                        "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "neverrun-e213.json")):
        print(f"REPORT FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    rep = json.load(open(os.path.join(d, "neverrun-e213.json")))
    P = json.load(open(POINTS))
    pts = {p["id"]: p for p in P["arms"][arm]["points"]}
    rows = rep["arms"][arm]["points"]
    hit_ids = [x["id"] for x in rows if x["role"] != "reference" and not x["never_run"] and x["id"] in pts]
    fe, fwhat = freeze_epoch(lab, arm)
    NR = load_scanner()
    toks = sorted({x["token"] for x in rows if x["id"] in hit_ids})
    found = rescan(NR, lab, lanes, toks) if toks else {}
    judged, before, after = [], [], []
    for x in rows:
        if x["id"] not in hit_ids:
            continue
        files = []
        for rel, c, p in found.get(x["token"], []):
            if not counted(NR, arm, c):
                continue
            ep, how = date_of(lab, lanes, rel, p)
            files.append({"path": rel, "class": c, "epoch": ep, "dated_by": how,
                          "before_freeze": (ep is None or fe is None or ep < fe)})
        meas = x.get("mm1_v3_measured") or []
        rb = any(f["before_freeze"] for f in files) or bool(meas) or not files or fe is None
        judged.append({"id": x["id"], "token": x["token"], "case": pts[x["id"]]["case"], "files": files, "mm1_v3_measured": meas,
                       "ran_before": rb, "why": ("MM1-v3's measured points hold it (before the freeze by construction)" if meas else
                                                  "no counted file found again (read conservatively)" if not files else
                                                  "the freeze line could not be read" if fe is None else
                                                  "a counted record dated before the freeze line, or not datable" if rb else
                                                  "every counted record dated after the freeze line (REPORTED; kept in every rule)")})
        (before if rb else after).append(x["id"])
    tok_before = {pts[i]["arm"] for i in before}
    lab_pts = sorted({p["id"] for p in pts.values() if p["role"] == "point" and p["arm"] in tok_before})
    lab_cases = sorted({pts[i]["case"] for i in lab_pts})
    labels = {arm: {"ran_before_points": lab_pts, "ran_before_cases": lab_cases}}
    bad = check_labels(labels)
    if bad:
        print(f"LABELS-REFUSED (a label names nothing in points-e213.json): {bad}")
        return 10
    n_pts = sum(1 for x in rows if x["role"] != "reference")
    n_never = sum(1 for x in rows if x["role"] != "reference" and x["never_run"])
    res = {"what": "E213's never-run search repeated and judged (desk/neverrun_card_e213.py)", "arm": arm, "card": CARD[arm], "dir": os.path.basename(d),
           "started": t0, "ended": now(), "scanner_sha256": sha(scanner), "scan_sha256": rep["scan_sha256"], "files_read": rep["files_read"],
           "rule": rep["arms"][arm]["rule"], "freeze_line": {"epoch": fe, "what": fwhat}, "n_points": n_pts, "n_never_run": n_never,
           "judged": judged, "ran_before": before, "ran_after_REPORTED": after, "labels": labels,
           "not_searched": "the boxes' own disks and the model session's uncommitted folders (as registered)"}
    json.dump(res, open(os.path.join(d, f"judge-e213-{arm}.json"), "w"), indent=1, sort_keys=True)
    json.dump(labels, open(os.path.join(d, f"labels-e213-{arm}.json"), "w"), indent=1, sort_keys=True)
    where = "on any card" if arm == "A" else "on aifoundry1 card 1"
    line = (f"NEVER-RUN-E213 arm {arm}: {n_never} of {n_pts} scored points never ran {where} (scan {rep['scan_sha256'][:12]}, {rep['files_read']} files); "
            f"ran before the freeze line ({fwhat}), labelled: {' '.join(lab_pts) or 'none'}; ran after it (REPORTED, kept): {' '.join(after) or 'none'}")
    txt = [line] + [f"  {j['id']} {j['token']}: {'RAN BEFORE' if j['ran_before'] else 'REPORTED'} - {j['why']}; "
                    + "; ".join(f"{f['path']} ({f['class']}, {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(f['epoch'])) if f['epoch'] else 'not datable'})"
                                for f in j["files"][:6]) for j in judged] + [line]
    open(os.path.join(d, f"judge-e213-{arm}.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt[1:]))
    return 0


def main(argv):
    if argv[:1] == ["run"] and len(argv) == 8 and argv[2] == "--arm" and argv[4] == "--lab" and argv[6] == "--lanes":
        return run(os.path.abspath(argv[1]), argv[3], os.path.abspath(argv[5]), os.path.abspath(argv[7]))
    if argv[:1] == ["check-labels"] and len(argv) == 2:
        bad = check_labels(json.load(open(argv[1])))
        print("LABELS-OK" if not bad else f"LABELS-REFUSED: {bad}")
        return 0 if not bad else 10
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
