#!/usr/bin/env python3
"""E215's never-run search REPEATED right before an arm's first card command, and its judgement (Q224, lane kit-e215, Thu 19 Nov 2026, before
any E215 datum). E215.md section 4: "The card lanes repeat this scan right before their first card command (desk/neverrun_e215.py scan, then
report with desk/candidates-e215.json, on the lab at GitHub main then and the folders then, E215's own subtracted): a point whose configuration
ran on its card in a record dated before its freeze line (arm A: MM1-v3.1's land; arm B: this registration's push) is labelled 'ran before' in a
dated note before the data commit and leaves every rule and head-to-head (the scorer's --labels); one dated after its freeze line is REPORTED and
stays in every rule. The scorer refuses a label naming no point or case (exit 10)." Runbook step 6n (rb/s06n_neverrun_e215.sh) calls it at the
desk. Standard library only here; it runs the registration's scanner UNCHANGED (desk/neverrun_e215.py, by its pinned sha256: its scan reads
MM1-v3.1's measured points through MM1-v3.1's data loader, numpy through it) as a subprocess and judges its outputs. E213's step-6n tool's form
(tools/claims-v3/e213/desk/neverrun_card_e213.py, landed 6efdb002), with E215's three readings.

    /usr/bin/python3 -I -B tools/claims-v3/e215/desk/neverrun_card_e215.py run DIR --arm A|B --lab LAB --lanes OUT
        1. desk/neverrun_e215.py scan --lab LAB --lanes OUT --out DIR          (the registration's scan: DIR/scan-e215.json)
        2. desk/neverrun_e215.py report --scan DIR/scan-e215.json --points desk/candidates-e215.json --out DIR
                                                                               (its verdicts: DIR/neverrun-e215.json, DIR/neverrun-e215.txt)
        3. THE JUDGEMENT for the arm: DIR/judge-e215-<arm>.json and .txt, DIR/labels-e215-<arm>.json (the scorer's --labels form,
           {"<arm>": {"ran_before_points": [...], "ran_before_cases": [...]}}, always written, its lists empty when nothing ran before);
           its last line "NEVER-RUN-E215 arm <arm>: ..."
    /usr/bin/python3 -I -B tools/claims-v3/e215/desk/neverrun_card_e215.py check-labels FILE    every label names a point or case of the arm
                                                                                                (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

THE JUDGEMENT (E215.md 4; the kit's reading of "a record dated"): for every SCORED point of the arm whose verdict the report now reads not never
run, the kit rescans the same roots by the scanner's own rules (its functions and patterns, imported from the pinned file) and lists EVERY file
that makes the verdict false under the point's own reading, each with its date - a lab file by the commit that added it (git log
--diff-filter=A, its committer time), a lane file under OUT by its modification time:
  literal (P, C, R): a file holding the point's shape token, counted for the arm (arm A: any card; arm B: E213's classes for card 1);
  post hoc L: a file holding the shape token that names the point's shire mask (the masks as numbers), counted for the arm;
  post hoc S: a file holding a GEMM run record (the host's values string) naming one of the kind's tile files (or the e37 generator), in a
      folder counted for the arm whose experiment lies outside MM1-v3.1's data.
MM1-v3.1's own measured points of the token, configuration or kind (on the arm's card; arm A any card, and for S its points of the kind at
gemmL3x1x3) are 'ran before' by construction (its data were committed before its land). A point with any counted file dated before the arm's
FREEZE LINE (arm A: MM1-v3.1's land 2c971828's committer time, 23:09:13 PST Wed 18 Nov 2026; arm B: the registration commit's - the commit that
added tools/claims-v3/e215/E215.md - committer time, its push by commit_lab.sh), or with no file found again, or with a file that cannot be
dated, is labelled 'ran before' (the conservative side: it leaves every rule); a point whose every such file is dated after the freeze line is
REPORTED and kept. THE LABELS: a literal point's label covers every scored point of the arm with its shape token (the reading is shape-level) and
their cases; an L point's covers itself and its case (its case is its configuration); an S point's covers itself only, never its case (family S is
scored in energy only, and its case is its random reference's, shared by the other S points of its format). The labels are checked against
points-e215.json before they are written (exit 10 on a label naming nothing). REPORTED, never a gate: the card lane writes a dated note before
the data commit when any point is labelled, and passes the labels file to the scorer at step 13. NOT SEARCHED, as registered: the boxes' own
disks and the model session's uncommitted folders. RB_DESKTEST=1 lets E215_NR_SCANNER name a stand-in scanner (the runbook's desk test only).
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
SCANNER = os.path.join(HERE, "neverrun_e215.py")
SCANNER_PIN = "9e68b0012dd782cd1fcb91806a8213f550294822337de204344bd22b73a89789"       # SHA256SUMS-e215-registration's line for it
CANDIDATES = os.path.join(HERE, "candidates-e215.json")
POINTS = os.path.join(E, "points-e215.json")
ARM_A_FREEZE = "2c971828c29ebb62b4ecc156024c7a5debd7404e"       # MM1-v3.1's land, committed 23:09:13 PST Wed 18 Nov 2026 (E215.md section 0)
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
        return (int(out), f"MM1-v3.1's land {ARM_A_FREEZE[:8]}") if rc == 0 and out.isdigit() else (None, "MM1-v3.1's land not in the lab")
    rc, out = git(lab, "log", "--diff-filter=A", "--format=%H %ct", "--", "tools/claims-v3/e215/E215.md")
    lines = [ln.split() for ln in out.splitlines() if ln.strip()]
    if rc != 0 or not lines:
        return None, "the registration commit not in the lab"
    h, ct = lines[-1]
    return int(ct), f"the registration commit {h[:8]}"


def load_scanner(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("neverrun_e215", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def counted(NR, arm, c):
    if c == "SUBTRACTED":
        return False
    return True if arm == "A" else NR.counted_for(NR.C1, c)


def rescan(NR, lab, lanes, tokens, kinds):
    """[(rel, class, path, tokens found, masks named, S kinds named in run records, experiments)] for every file holding a wanted token or a
    GEMM run record naming a wanted S kind, over the scanner's own roots by its own rules (its scan(), restricted)."""
    N = NR.e213_module()
    expmap = N.exp_cards(lab)
    names, _aliases = NR.tile_names(lab) if kinds else ({}, {})
    base_kind = {}
    for k, v in names.items():
        if k in kinds:
            for n in v:
                base_kind.setdefault(n, set()).add(k)
    roots = [os.path.join(lab, "docs", "reports", "data"), os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
             os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes) if d.startswith(("card-", "data-", "a1", "a2", "a3")))
    want = set(tokens)
    out = []
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if ".git" in dn or ".git" in fns:
                dn[:] = []
                continue
            dn.sort()
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(N.SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > N.MAX_BYTES:
                        continue
                    txt = N.read_text(p)
                except (OSError, EOFError):
                    continue
                found = set(N.RX.findall(txt)) & want if want else set()
                ks = set()
                if kinds and ":" in txt:
                    for tok, gen, files in NR.VRX.findall(txt):
                        for f in files.split(","):
                            ks |= base_kind.get(os.path.basename(f.strip()), set())
                        if gen == "e37" and "fp32.e37" in kinds:
                            ks.add("fp32.e37")
                if not found and not ks:
                    continue
                masks = {"0x%x" % int(m, 16) for m in NR.MRX.findall(txt)} if found else set()
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else "W/out/" + os.path.relpath(p, lanes)
                c = "SUBTRACTED" if NR.subtracted(rel) else (N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE)
                out.append((rel, c, p, found, masks, ks, NR.folder_exps(rel)))
    return out


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


def evidence(x, arm, card):
    """(the reading, MM1-v3.1's own measured evidence) for one report row"""
    if x["family"] == "L":
        return "L", list(x.get("mask_in_mm1_v31_points") or [])
    if x["family"] == "S":
        kc = list(x.get("kind_mm1_v31_points_by_card") or [])
        meas = [c for c in kc if c == card] if arm == "B" else kc
        if arm == "A":
            meas += [f"gemmL3x1x3 on {c}" for c in (x.get("configuration_gemmL3x1x3_mm1_v31_points") or [])]
        return "S", meas
    meas = list(x.get("mm1_v31_measured_token") or [])
    return "literal", ([m for m in meas if m.endswith(card)] if arm == "B" else meas)


def run(d, arm, lab, lanes):
    if arm not in ("A", "B"):
        print("usage: run DIR --arm A|B --lab LAB --lanes OUT")
        return 2
    scanner = SCANNER
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E215_NR_SCANNER"):
        scanner = os.environ["E215_NR_SCANNER"]
    elif sha(SCANNER) != SCANNER_PIN:
        print(f"REFUSED: the registration's scanner {SCANNER} is {sha(SCANNER)}, pinned {SCANNER_PIN}")
        return 4
    os.makedirs(d, exist_ok=True)
    t0 = now()
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "scan-e215.json")):
        print(f"SCAN FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    r = subprocess.run([sys.executable, "-I", "-B", scanner, "report", "--scan", os.path.join(d, "scan-e215.json"), "--points", CANDIDATES,
                        "--out", d], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0 or not os.path.exists(os.path.join(d, "neverrun-e215.json")):
        print(f"REPORT FAILED: rc {r.returncode} {r.stderr[-300:]}")
        return 14
    rep = json.load(open(os.path.join(d, "neverrun-e215.json")))
    P = json.load(open(POINTS))
    pts = {p["id"]: p for p in P["arms"][arm]["points"]}
    rows = rep["arms"][arm]["points"]
    hit = [x for x in rows if x["role"] == "point" and not x["never_run"] and x["id"] in pts]
    fe, fwhat = freeze_epoch(lab, arm)
    NR = load_scanner(scanner)
    toks = sorted({x["token"] for x in hit if x["family"] != "S"})
    kinds = sorted({x.get("kind_key") for x in hit if x["family"] == "S" and x.get("kind_key")})
    found = rescan(NR, lab, lanes, toks, set(kinds)) if hit else []
    v31x = set(json.load(open(os.path.join(d, "scan-e215.json"))).get("mm1_v31_experiments") or [])
    judged, before, after = [], [], []
    for x in hit:
        reading, meas = evidence(x, arm, CARD[arm])
        files = []
        for rel, c, p, ftoks, fmasks, fkinds, exps in found:
            if not counted(NR, arm, c):
                continue
            if reading == "literal" and x["token"] not in ftoks:
                continue
            if reading == "L" and (x["token"] not in ftoks or x.get("mask") not in fmasks):
                continue
            if reading == "S" and (x.get("kind_key") not in fkinds or (exps and set(exps) <= v31x)):
                continue
            ep, how = date_of(lab, lanes, rel, p)
            files.append({"path": rel, "class": c, "epoch": ep, "dated_by": how, "before_freeze": (ep is None or fe is None or ep < fe)})
        rb = any(f["before_freeze"] for f in files) or bool(meas) or not files or fe is None
        judged.append({"id": x["id"], "family": x["family"], "reading": reading, "token": x["token"], "mask": x.get("mask"),
                       "kind_key": x.get("kind_key"), "case": pts[x["id"]]["case"], "files": files, "mm1_v31_measured": meas,
                       "ran_before": rb, "why": ("MM1-v3.1's measured points hold it (before the freeze by construction)" if meas else
                                                  "no counted file found again (read conservatively)" if not files else
                                                  "the freeze line could not be read" if fe is None else
                                                  "a counted record dated before the freeze line, or not datable" if rb else
                                                  "every counted record dated after the freeze line (REPORTED; kept in every rule)")})
        (before if rb else after).append(x["id"])
    lab_pts, lab_cases = set(), set()
    for j in judged:
        if not j["ran_before"]:
            continue
        if j["reading"] == "literal":           # shape-level: every scored point of the arm with that token, and their cases
            same = [p for p in pts.values() if p["role"] == "point" and p["arm"] == j["token"] and p["family"] in ("P", "C", "R")]
            lab_pts.update(p["id"] for p in same)
            lab_cases.update(p["case"] for p in same if p.get("time_scored"))
        elif j["reading"] == "L":
            lab_pts.add(j["id"])
            lab_cases.add(j["case"])
        else:                                    # S: the point only (scored in energy only; its case is its random reference's)
            lab_pts.add(j["id"])
    labels = {arm: {"ran_before_points": sorted(lab_pts), "ran_before_cases": sorted(lab_cases)}}
    bad = check_labels(labels)
    if bad:
        print(f"LABELS-REFUSED (a label names nothing in points-e215.json): {bad}")
        return 10
    n_pts = sum(1 for x in rows if x["role"] == "point")
    n_never = sum(1 for x in rows if x["role"] == "point" and x["never_run"])
    res = {"what": "E215's never-run search repeated and judged (desk/neverrun_card_e215.py)", "arm": arm, "card": CARD[arm], "dir": os.path.basename(d),
           "started": t0, "ended": now(), "scanner_sha256": sha(scanner), "scan_sha256": rep["scan_sha256"], "files_read": rep["files_read"],
           "freeze_line": {"epoch": fe, "what": fwhat}, "n_points": n_pts, "n_never_run": n_never,
           "judged": judged, "ran_before": before, "ran_after_REPORTED": after, "labels": labels,
           "not_searched": "the boxes' own disks and the model session's uncommitted folders (as registered)"}
    json.dump(res, open(os.path.join(d, f"judge-e215-{arm}.json"), "w"), indent=1, sort_keys=True)
    json.dump(labels, open(os.path.join(d, f"labels-e215-{arm}.json"), "w"), indent=1, sort_keys=True)
    where = "on any card" if arm == "A" else "on aifoundry1 card 1"
    line = (f"NEVER-RUN-E215 arm {arm}: {n_never} of {n_pts} scored points never ran {where} (scan {rep['scan_sha256'][:12]}, {rep['files_read']} files); "
            f"ran before the freeze line ({fwhat}), labelled: {' '.join(sorted(lab_pts)) or 'none'}; ran after it (REPORTED, kept): {' '.join(after) or 'none'}")
    txt = [line] + [f"  {j['id']} {j['family']} {j['token']}{(' ' + j['mask']) if j.get('mask') else ''}{(' ' + j['kind_key']) if j.get('kind_key') else ''}: "
                    f"{'RAN BEFORE' if j['ran_before'] else 'REPORTED'} - {j['why']}; "
                    + "; ".join(f"{f['path']} ({f['class']}, {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(f['epoch'])) if f['epoch'] else 'not datable'})"
                                for f in j["files"][:6]) for j in judged] + [line]
    open(os.path.join(d, f"judge-e215-{arm}.txt"), "w").write("\n".join(txt) + "\n")
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
