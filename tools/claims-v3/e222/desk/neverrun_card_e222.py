#!/usr/bin/env python3
"""E222's never-run search REPEATED right before the first card command, and its judgement (Q236, lane kit-e222, Fri 20 Nov 2026, before any
E222 datum). E222.md section 4: "The card lane repeats the scan right before its first card command (step 6n, the same reading): a point found
run then is labelled 'ran before' and leaves every rule, said." Runbook step 6n (rb/s06n_neverrun_e222.sh) calls it at the desk. E220's step-6n
tool's form (tools/claims-v3/e220/desk/neverrun_card_e220.py, landed in 2f0ab9cd with fix-e220's dated note 1 reading) for E222's one card: it
runs the registration's scanner UNCHANGED (desk/neverrun_e222.py, at its pinned sha256 in SHA256SUMS-e222-registration, both its `scan` and its
`report`, every output in DIR, never the registration's own desk/ folder) as subprocesses and judges their outputs:

    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/neverrun_card_e222.py run DIR --arm A --lab LAB --lanes OUT
        1. desk/neverrun_e222.py scan --lab LAB --lanes OUT --out DIR       (the registration's scan: DIR/scan-e222-reg.json; E222's own folders -
                                                                            any lane or data folder whose name holds 'e222', W/out/card-e222
                                                                            among them - and E220's are never opened, as registered)
        2. desk/neverrun_e222.py report --scan DIR/scan-e222-reg.json --points LAB/tools/claims-v3/e222/points-e222.csv --out DIR
                                                                            (each registered point's verdict on aifoundry3 card 0 by session
                                                                            records, dated note 1's reading: DIR/neverrun-e222.json and .txt)
        3. THE JUDGEMENT: DIR/judge-e222-A.json and .txt, DIR/labels-e222-A.json (the frozen scorer's --labels form, score_e220.read_a's:
           {"ran_before_points": {"A": [...]}}, always written, its list empty when nothing ran); its last line "NEVER-RUN-E222 arm A: ..."
    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/neverrun_card_e222.py check-labels FILE [--arm A]
        every label names a registered point of E222 outside family R (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

THE JUDGEMENT (E222.md 4, the registration's reading: E220's dated note 1, tools/claims-v3/e220-notes/E220.md.dated-note-1.md - a point counts as
RUN on aifoundry3 card 0 only by a SESSION RECORD on that card; desk copies in folders naming no card never count):
  - every registered point outside family R that the report now reads not never run (a session record on aifoundry3 card 0 names it, or an
    MM1-v3.2 measured point holds it there) is labelled 'ran before' and leaves every rule (the scorer's --labels), whatever the date;
  - FAMILY R (ry01a, ry01b, rg01, rg01t: E218's own points, run on this card at 03:11-03:56 PST Fri 20 Nov 2026) is exempt by its FAMILY NAME
    only (E222.md 3 and 4: the report's 'exempt' reading) and is in no rule; the judgement prints each as "RAN (exempt by family name: same-card
    repeats, REPORTED only)" and never as never run (the orchestrator's answer 1 of 14:21 PST Fri 20 Nov 2026, W/out/orch/e222-answers.txt);
  - THE POSITIVE CONTROL (the same answer): R's exemption LIFTED, each R point read by the registered scanner's own Never class on the same scan
    (the R-Y pair by its configuration, token and mask; rg01 and rg01t by their token): all four must read RAN, from E218's committed data folder
    on this card. If any reads never run, the scan cannot see this card's sessions and no non-R verdict can be trusted: the judgement writes its
    files, prints "POSITIVE CONTROL FAILED" and exits 15 (step 6n stops the day before step 7: no card command; the orchestrator decides);
  - the registered literal reading (any file counted for the card, a folder naming no card counting for every card) is REPORTED beside, never a
    label, with the report's evidence.
A label is one point. REPORTED, never a gate (but the positive control): the card lane writes a dated note before the data commit when any point
is labelled, and passes the labels file to the scorer at step 13. NOT SEARCHED, as registered: the box's own disk and the model session's
uncommitted folders (E222.md 4). Exits: 0 with its line; 15 the positive control failed; 14 a scan or report failed (run it again); 10 a usage
error or a refused label; 4 the scanner or the points not at their pins. RB_DESKTEST=1 lets E222_NR_SCANNER name a stand-in scanner (the
runbook's desk test only; the positive control always reads the registered scanner's Never class, at its pin). Standard library only here (the
scanner reads MM1-v3.2's measured points through its data loader, numpy through it: the card lane runs this inside the round's slot,
single-threaded).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = os.path.join(HERE, "neverrun_e222.py")
SCANNER_PIN = "e3c0b391ef675a4b73f600537a0101f88c10a1cd0aeb4c49a90d30b7dc0f3ac2"       # SHA256SUMS-e222-registration's line for it
POINTS_CSV = "tools/claims-v3/e222/points-e222.csv"
POINTS_CSV_PIN = "8b709d4bf80ba98bd90728b492f7f6aca4edcc516615c194de1da65b38f69809"
POINTS = os.path.join(E, "points-e222.json")
CARD = "aifoundry3 card 0"
R_EXEMPT = ("ry01a", "ry01b", "rg01", "rg01t")            # family R (E222.md 3): E218's y01a, y01b, g01, g01t, re-run; exempt by name
R_WORDS = "RAN (exempt by family name: same-card repeats, REPORTED only)"
NOTE1 = "tools/claims-v3/e220-notes/E220.md.dated-note-1.md"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def reg_pin(rel):
    for ln in open(os.path.join(E, "SHA256SUMS-e222-registration")):
        if ln.strip() and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            if f.strip() == rel:
                return h
    return None


def registered():
    """the 70 registered points, by id (points-e222.json > points)"""
    P = json.load(open(POINTS))
    return {p["id"]: p for p in P["points"] if p.get("role") == "point"}


def check_labels(obj, arm="A"):
    """[] when obj is the scorer's labels form for the arm and every label is a registered point outside family R; else what is wrong"""
    pts = registered()
    try:
        L = obj["ran_before_points"]
        ids = L[arm]
        ok = isinstance(ids, list) and all(isinstance(x, str) for x in ids) and set(L) == {arm} and set(obj) == {"ran_before_points"}
    except (TypeError, KeyError):
        return ["not the scorer's labels form {\"ran_before_points\": {\"A\": [...]}}"]
    if not ok:
        return ["not the scorer's labels form {\"ran_before_points\": {\"A\": [...]}}"]
    bad = [x for x in ids if x not in pts]
    bad += [f"{x} (family R: exempt by name, in no rule)" for x in ids if x in pts and pts[x]["family"] == "R"]
    return bad


def scanner_module():
    """the registered scanner module at its pin (its Never class reads the positive control), never a stand-in"""
    if sha(SCANNER) != SCANNER_PIN or reg_pin("tools/claims-v3/e222/desk/neverrun_e222.py") != SCANNER_PIN:
        raise ValueError(f"the registration's scanner is not at its pin {SCANNER_PIN[:12]}")
    spec = importlib.util.spec_from_file_location("neverrun_e222_pinned", SCANNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def positive_control(M, S, pts):
    """R's exemption lifted: each R point by the scanner's own reading on the same scan (the R-Y pair by configuration; rg01, rg01t by token).
    -> ({id: {"reading", "ran", "evidence"}}, all four ran)"""
    NV = M.Never(S)
    out = {}
    for pid in R_EXEMPT:
        q = pts[pid]
        if q["subfamily"] == "R-Y":
            ok, ev = NV.config(q["token"], q["shire_mask"])
            rd = "config (token, mask)"
        else:
            ok, ev = NV.token(q["token"])
            rd = "token"
        out[pid] = {"reading": rd, "ran": not ok, "evidence": ev, "token": q["token"], "mask": q["shire_mask"], "e218_id": q.get("e218_id")}
    return out, all(v["ran"] for v in out.values())


def run(d, arm, lab, lanes):
    if arm != "A":
        print("usage: run DIR --arm A --lab LAB --lanes OUT")
        return 10
    try:
        M = scanner_module()
    except (OSError, ValueError) as e:
        print(f"NEVER-RUN-E222 arm {arm}: REFUSED ({e})")
        return 4
    scanner, swhy = SCANNER, f"desk/neverrun_e222.py at its registered sha256 {SCANNER_PIN[:12]}"
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E222_NR_SCANNER"):
        scanner, swhy = os.environ["E222_NR_SCANNER"], "a desk-test stand-in"
    lp = os.path.join(lab, POINTS_CSV)
    if not os.path.isfile(lp) or sha(lp) != POINTS_CSV_PIN:
        print(f"NEVER-RUN-E222 arm {arm}: REFUSED (the registered points {POINTS_CSV} are not at their pin {POINTS_CSV_PIN[:12]})")
        return 4
    os.makedirs(d, exist_ok=True)
    t0 = now()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    r1 = subprocess.run([sys.executable, "-I", "-B", scanner, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True,
                        env=env)
    open(os.path.join(d, "scan.out"), "w").write(r1.stdout + r1.stderr)
    sp = os.path.join(d, "scan-e222-reg.json")
    if r1.returncode != 0 or not os.path.exists(sp):
        print(f"NEVER-RUN-E222 arm {arm}: the scan failed (rc {r1.returncode}; {d}/scan.out)")
        return 14
    r2 = subprocess.run([sys.executable, "-I", "-B", scanner, "report", "--scan", sp, "--points", lp, "--out", d], capture_output=True, text=True,
                        env=env)
    open(os.path.join(d, "report.out"), "w").write(r2.stdout + r2.stderr)
    rp = os.path.join(d, "neverrun-e222.json")
    if r2.returncode != 0 or not os.path.exists(rp):
        print(f"NEVER-RUN-E222 arm {arm}: the report failed (rc {r2.returncode}; {d}/report.out)")
        return 14
    R = json.load(open(rp))
    S = json.load(open(sp))
    pts = registered()
    v = {x["id"]: x for x in R.get("points", []) if x.get("id") in pts}
    if set(v) != set(pts):
        print(f"NEVER-RUN-E222 arm {arm}: the report does not read every registered point ({len(v)} of {len(pts)})")
        return 14
    nonr = [pid for pid in pts if pts[pid]["family"] != "R"]
    rfam = [pid for pid in pts if pts[pid]["family"] == "R"]
    if sorted(rfam) != sorted(R_EXEMPT) or any(v[pid].get("reading") != "exempt" for pid in rfam) or \
            any(v[pid].get("reading") == "exempt" for pid in nonr):
        print(f"NEVER-RUN-E222 arm {arm}: family R is not the registered four exempt by name ({sorted(rfam)})")
        return 14
    labelled = sorted(pid for pid in nonr if not v[pid]["never_run"])
    labels = {"ran_before_points": {arm: labelled}}
    bad = check_labels(labels, arm)
    if bad:
        print(f"LABELS-REFUSED: {bad}")
        return 10
    try:
        pc, pc_ok = positive_control(M, S, pts)
    except (KeyError, TypeError, ValueError) as e:
        pc, pc_ok = {"error": f"{type(e).__name__}: {str(e)[:200]}"}, False
    lit_never = [pid for pid in pts if v[pid].get("literal_never_run_REPORTED")]
    lit_ran = sorted(pid for pid in pts if not v[pid].get("literal_never_run_REPORTED"))
    rec = {"what": "E222's step 6n: the registration's scan and report repeated, and the judgement (desk/neverrun_card_e222.py)", "arm": arm,
           "card": CARD, "dir": os.path.basename(d), "started": t0, "ended": now(), "scanner": swhy, "lab_head": S.get("lab_head"),
           "files_read": S.get("files_read"), "session_record_files_read": S.get("session_record_files_read"), "scan_sha256": sha(sp),
           "report_sha256": sha(rp), "never_opened_REPORTED": S.get("never_opened"),
           "reading": (f"E222.md 4 (the registration's reading, E220's dated note 1, {NOTE1}): a point counts as run on {CARD} only by a session "
                       f"record on that card; desk copies in folders naming no card never count"),
           "n_points": len(pts), "n_non_R": len(nonr), "n_non_R_never_run": len(nonr) - len(labelled), "ran_before_labelled": labelled,
           "ran_before_evidence": {pid: v[pid].get("evidence") for pid in labelled},
           "family_R_REPORTED": {pid: {"words": R_WORDS, "e218_id": pts[pid].get("e218_id"), "token": pts[pid]["token"],
                                       "mask": pts[pid]["shire_mask"]} for pid in rfam},
           "positive_control": {"what": "family R's exemption lifted: each R point by the registered scanner's own Never class on the same scan "
                                        "(the orchestrator's answer 1, W/out/orch/e222-answers.txt); all four must read RAN",
                                "points": pc, "all_ran": pc_ok},
           "literal_reading_REPORTED": {"what": "the registered literal reading (any file counted for the card, a folder naming no card counting "
                                                "for every card); REPORTED, never a label", "n_never_run": len(lit_never), "ran": lit_ran},
           "rule": ("E222.md 4: a registered point the repeated scan finds run on aifoundry3 card 0 - by a session record on that card - is "
                    "labelled 'ran before' and leaves every rule, whatever the date (REPORTED, never a gate); family R exempt by name"),
           "not_searched": "the box's own disk and the model session's uncommitted folders (as registered)"}
    json.dump(rec, open(os.path.join(d, f"judge-e222-{arm}.json"), "w"), indent=1, sort_keys=True)
    json.dump(labels, open(os.path.join(d, f"labels-e222-{arm}.json"), "w"), indent=1, sort_keys=True)
    rwords = ", ".join(f"{pid} {R_WORDS.split(' (')[0]}" for pid in rfam)
    pcw = (f"{sum(1 for x in pc.values() if isinstance(x, dict) and x.get('ran'))} of {len(R_EXEMPT)} RAN"
           if "error" not in pc else f"NOT READ ({pc['error']})")
    line = (f"NEVER-RUN-E222 arm {arm}: {len(nonr) - len(labelled)} of {len(nonr)} registered non-R points never ran on {CARD} by session records "
            f"(dated note 1's reading; scan {rec['scan_sha256'][:12]}, {S.get('files_read')} files, lab {str(S.get('lab_head'))[:12]}); ran before, "
            f"labelled: {', '.join(labelled) if labelled else 'none'}; family R: {rwords} {R_WORDS[4:]}; the positive control (R's exemption "
            f"lifted, the same scan): {pcw}; the literal reading (REPORTED, not a label): {len(lit_never)} of {len(pts)} never ran")
    lines = [line]
    for pid in labelled:
        lines.append(f"  {pid} {pts[pid]['family']} {pts[pid]['token']} {pts[pid]['shire_mask']}: RAN BEFORE (labelled, leaves every rule); "
                     f"evidence {json.dumps(v[pid].get('evidence'), sort_keys=True)[:300]}")
    for pid in rfam:
        x = pc.get(pid) if isinstance(pc.get(pid), dict) else {}
        lines.append(f"  {pid} R {pts[pid]['token']} {pts[pid]['shire_mask']}: {R_WORDS}; the positive control ({x.get('reading')}): "
                     f"{'RAN' if x.get('ran') else 'NOT SEEN'} {json.dumps(x.get('evidence'), sort_keys=True)[:300]}")
    if not pc_ok:
        lines.append(f"POSITIVE CONTROL FAILED: the scan does not read every one of family R's four points as run on {CARD} (E218 ran them there at "
                     f"03:11-03:56 PST Fri 20 Nov 2026): it cannot see this card's sessions, so no non-R verdict can be trusted; no card command "
                     f"(the orchestrator's answer 1: a re-scan with a reader that does, a non-R point found run DROPPED by a rule stated with the drop)")
    lines.append(line)
    open(os.path.join(d, f"judge-e222-{arm}.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[1:]))
    return 0 if pc_ok else 15


def main(argv):
    if argv[:1] == ["run"] and len(argv) == 8 and argv[2] == "--arm" and argv[4] == "--lab" and argv[6] == "--lanes":
        return run(os.path.abspath(argv[1]), argv[3], os.path.abspath(argv[5]), os.path.abspath(argv[7]))
    if argv[:1] == ["check-labels"] and len(argv) in (2, 4) and (len(argv) == 2 or argv[2] == "--arm"):
        arm = argv[3] if len(argv) == 4 else "A"
        try:
            obj = json.load(open(argv[1]))
        except (OSError, ValueError) as e:
            print(f"LABELS-REFUSED: unreadable ({type(e).__name__})")
            return 10
        bad = check_labels(obj, arm)
        ids = obj.get("ran_before_points", {}).get(arm, []) if not bad else []
        print(f"LABELS-OK: {len(ids)} label(s) of E222's registered points ({', '.join(ids) if ids else 'none'})" if not bad else f"LABELS-REFUSED: {bad}")
        return 0 if not bad else 10
    print(__doc__.split("THE JUDGEMENT")[0])
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
