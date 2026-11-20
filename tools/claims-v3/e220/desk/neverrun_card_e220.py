#!/usr/bin/env python3
"""E220's never-run search REPEATED right before each arm's first card command, and its judgement (Q233, lane kit-e220, Fri 20 Nov 2026, before
any E220 datum), for BOTH ARMS (arm A's step 6n, rb/s06n_neverrun_e220a.sh; arm B's, rb/s06n_neverrun_e220b.sh). E220.md section 4: "The card
lanes repeat the scan right before their first card command (step 6n): a point found run then is labelled 'ran before' and leaves every rule,
said." It runs the registration's scanner and report UNCHANGED, each at its pinned sha256 (SHA256SUMS-e220-registration), as subprocesses with
every output in DIR (never the registration's own desk/ folder: the report's defaults write there), and judges their outputs:

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/neverrun_card_e220.py run DIR --arm A|B --lab LAB --lanes OUT
        1. desk/neverrun_e220.py scan --lab LAB --lanes OUT --out DIR            (the registration's literal scan, E218's form: DIR/scan-e220-reg.json;
                                                                                 E220's own folders SUBTRACTED: a path holding '-e220-', W/out/card-e220*)
        2. desk/neverrun_report_e220.py --scan DIR/scan-e220-reg.json --points LAB/tools/claims-v3/e220/points-e220.csv --out DIR
                                                                                (each registered point's verdict on its own arm's card by its
                                                                                family's reading: DIR/neverrun-e220.json and .txt)
        3. THE JUDGEMENT for the arm: DIR/judge-e220-<arm>.json and .txt, DIR/labels-e220-<arm>.json (the frozen scorer's --labels form,
           {"ran_before_points": {"<arm>": [...]}}, always written, its list empty when nothing ran); its last line
           "NEVER-RUN-E220 arm <arm>: <n> of <N> registered points never ran on <card> ...; ran before, labelled: <none / ids>"
    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/neverrun_card_e220.py check-labels FILE --arm A|B
        every label names a registered point of that arm (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

THE JUDGEMENT (E220.md 4, READ BY DATED NOTE 1 since fix-e220: tools/claims-v3/e220-notes/E220.md.dated-note-1.md, before any E220 datum, on
verify-e220's F1 and the orchestrator's RULING 1 of Fri 20 Nov 2026): every registered point of the arm (points-e220.json > points > <arm>) whose
verdict the report now reads not never run, under its family's registered reading (the token reading for XG, XGt, XF, L3, Y2, G2 and G2t; the
configuration reading for XY), AND whose hits hold A SESSION RECORD ON THE ARM'S CARD (note1() below: MM1-v3.2's measured points on the card, a
committed data folder naming the card, a session's own file in a lane folder naming the card; a capped listing that cannot be cleared counts,
the conservative side; a folder naming no card never counts), is labelled 'ran before' and leaves every rule (the scorer's --labels), whatever
the date of the record; the registered literal reading's labels (any hit counted for the card) are REPORTED beside them, never a label, with
the report's evidence. A label is one point. REPORTED, never a gate: the card lane writes a dated note before the data commit when any point
is labelled, and passes the labels file to the scorer at step 13. NOT SEARCHED, as registered: the boxes' own disks and the model session's
uncommitted folders (E220.md 4 and 8). Exit 0 with its line; 14 a scan or report failed (run it again); 10 a usage error. RB_DESKTEST=1 lets
E220_NR_SCANNER and E220_NR_REPORT name stand-in tools (the runbooks' desk tests only). Standard library only here (the scanner reads
MM1-v3.2's measured points through its data loader, numpy through it: the card lane runs this inside the round's slot, single-threaded).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = (os.path.join(HERE, "neverrun_e220.py"), "31028e3deb281f15856352f4bbdffd14737e8a51f0c22fd3137985be9e049ec2")
REPORT = (os.path.join(HERE, "neverrun_report_e220.py"), None)          # its pin read from SHA256SUMS-e220-registration
POINTS_JSON = os.path.join(E, "points-e220.json")
POINTS_CSV = "tools/claims-v3/e220/points-e220.csv"
CARD = {"A": "aifoundry1 card 1", "B": "aifoundry2 card 0"}
# a hit's file is a SESSION RECORD when it sits in a session's folder or is one of a session's own files (REPORTED reading, never a label rule)
SESSION_FILE = re.compile(r"/(session|sessions|runs|smoke)/|(^|/)(proc[-0-9]*\.(out|err)|run\.json|smoke\.json|queue\.json|session\.log)$")


def counted_for(card, c):
    """the registration's folder classes (neverrun_e220.counted_for): a folder naming the card, or naming none; for aifoundry1's cards also a
    folder naming aifoundry1 but no card"""
    return c == card or c == "no card named" or (card in ("aifoundry1 card 1", "aifoundry1 card 0") and c == "aifoundry1 (card not named)")


def hit_kinds(S, token, card):
    """('session' | 'desk only' | 'unlisted', [the counted files]) for a token's hits counted for the card in the registration's scan"""
    files, unlisted = [], False
    for c, v in (S.get("tokens", {}).get(token) or {}).items():
        if c == "SUBTRACTED" or not counted_for(card, c):
            continue
        fl = v.get("files") or []
        files += fl
        unlisted |= int(v.get("n") or 0) > len(fl)
    if any(SESSION_FILE.search(f) and "/dry/" not in f for f in files):      # a dry pass (the doubles, no card) is never a session on a card
        return "session", files
    return ("unlisted" if unlisted or not files else "desk only"), files


NOTE1 = "tools/claims-v3/e220-notes/E220.md.dated-note-1.md"


def note1(S, row, card):
    """DATED NOTE 1's READING (fix-e220, Fri 20 Nov 2026, before any E220 datum: verify-e220's F1 and the orchestrator's RULING 1 in
    W/out/orch/e220-answers.txt) for a point the registered literal reading labelled: it counts as RUN on its arm's card only by a SESSION
    RECORD ON THAT CARD. -> ('ran' | 'never', why, [the files that count]).
      1. MM1-v3.2's measured points hold it on the card (committed session data): the token on the card (token families) or the configuration
         (token, mask) on the card (XY): ran;
      2. a hit in a folder NAMING THE CARD (for aifoundry1 card 1 also a folder naming aifoundry1 but no card: the conservative side), under the
         family's reading (XY: only a folder class whose files name the point's mask): a file of a committed data folder (docs/reports/data/...)
         or a session's own file in a lane folder (SESSION_FILE, never under a /dry/ folder: a dry pass is no session): ran; a class whose
         listing is capped (more hits than the scan lists) with no such file among those listed cannot be cleared from the scan: ran (the
         conservative side, REPORTED as unresolved);
      3. a hit in a folder naming NO card (desk copies in card-less lane folders: W/out/data-*, decl-*, verify-* ...; plans and registrations)
         and every other hit (plans, schedules, desk logs, dry passes) never counts: never."""
    tok, mask, reading = row.get("token"), row.get("mask"), row.get("reading")
    if reading == "config":
        m = "0x%x" % int(mask, 16)
        mm = S.get("mm1_v32_measured_masks", {}).get(tok, {})
        if m in (mm.get(card) or []):
            return "ran", f"MM1-v3.2's measured points hold ({tok}, {m}) on {card}", []
    else:
        mt = [x for x in S.get("mm1_v32_measured_tokens", {}).get(tok, []) if x.endswith(card)]
        if mt:
            return "ran", f"MM1-v3.2's measured points hold {tok} on {card}: {mt[:3]}", []
    ok_cls = {card} | ({"aifoundry1 (card not named)"} if card in ("aifoundry1 card 1", "aifoundry1 card 0") else set())
    counted, unresolved, desk = [], [], []
    for c, v in sorted((S.get("tokens", {}).get(tok) or {}).items()):
        if c == "SUBTRACTED" or not counted_for(card, c):
            continue
        if reading == "config":
            ms = (S.get("masks_by_card", {}).get(tok) or {}).get(c) or []
            if not (m in ms or "any" in ms):
                continue
        fl = v.get("files") or []
        if c not in ok_cls:
            desk.append(f"{c}: {len(fl)} of {int(v.get('n') or 0)} listed, a folder naming no card (never a session record on {card})")
            continue
        rec = [f for f in fl if f.startswith("docs/reports/data/") or (SESSION_FILE.search(f) and "/dry/" not in f)]
        if rec:
            counted += rec
        elif int(v.get("n") or 0) > len(fl):
            unresolved.append(f"{c}: {len(fl)} of {int(v.get('n'))} files listed, none a session record (the rest unlisted)")
        else:
            desk.append(f"{c}: {len(fl)} file(s), none a session record (desk files: plans, logs, dry passes)")
    if counted:
        return "ran", f"a session record on {card}", counted[:8]
    if unresolved:
        return "ran", "UNRESOLVED from the scan (labelled: the conservative side): " + "; ".join(unresolved), []
    return "never", "desk files only: " + ("; ".join(desk) if desk else "no hit counted"), []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def reg_pin(rel):
    for ln in open(os.path.join(E, "SHA256SUMS-e220-registration")):
        if ln.strip() and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            if f.strip() == rel:
                return h
    return None


def arm_points(arm):
    return json.load(open(POINTS_JSON))["points"][arm]


def tool(env_name, pinned):
    path, pin = pinned
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get(env_name):
        return os.environ[env_name], "a desk-test stand-in"
    rel = os.path.relpath(path, REPO)
    want = pin or reg_pin(rel)
    if want is None or reg_pin(rel) != want or sha(path) != want:
        raise ValueError(f"{rel} is not at its registered sha256")
    return path, f"{rel} at its registered sha256 {want[:12]}"


def run(d, arm, lab, lanes):
    os.makedirs(d, exist_ok=True)
    try:
        scan, swhy = tool("E220_NR_SCANNER", SCANNER)
        rep, rwhy = tool("E220_NR_REPORT", REPORT)
    except ValueError as e:
        print(f"NEVER-RUN-E220 arm {arm}: REFUSED ({e})")
        return 14
    t0 = now()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    r1 = subprocess.run([sys.executable, "-I", "-B", scan, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True,
                        env=env)
    open(os.path.join(d, "scan.out"), "w").write(r1.stdout + r1.stderr)
    sp = os.path.join(d, "scan-e220-reg.json")
    if r1.returncode != 0 or not os.path.exists(sp):
        print(f"NEVER-RUN-E220 arm {arm}: the scan failed (rc {r1.returncode}; {d}/scan.out)")
        return 14
    r2 = subprocess.run([sys.executable, "-I", "-B", rep, "--scan", sp, "--points", os.path.join(lab, POINTS_CSV), "--out", d],
                        capture_output=True, text=True, env=env)
    open(os.path.join(d, "report.out"), "w").write(r2.stdout + r2.stderr)
    rp = os.path.join(d, "neverrun-e220.json")
    if r2.returncode not in (0, 1) or not os.path.exists(rp):
        print(f"NEVER-RUN-E220 arm {arm}: the report failed (rc {r2.returncode}; {d}/report.out)")
        return 14
    R = json.load(open(rp))
    S = json.load(open(sp))
    mine = {q["id"] for q in arm_points(arm)}
    v = [x for x in R["points"] if x["arm"] == arm and x["id"] in mine]
    if {x["id"] for x in v} != mine:
        print(f"NEVER-RUN-E220 arm {arm}: the report does not read every registered point of the arm ({len(v)} of {len(mine)})")
        return 14
    ran = sorted(x["id"] for x in v if not x["never_run"])          # the registered literal reading (REPORTED beside since dated note 1)
    tok = {q["id"]: q.get("token") for q in arm_points(arm)}
    kinds = {pid: hit_kinds(S, tok.get(pid), CARD[arm]) for pid in ran}
    desk_only = sorted(pid for pid, (k, _) in kinds.items() if k == "desk only")
    # fix-e220: THE LABELS BY DATED NOTE 1'S READING (a session record on the arm's card); the literal reading's labels REPORTED beside
    note1_dec = {x["id"]: note1(S, x, CARD[arm]) for x in v if not x["never_run"]}
    lab1 = sorted(pid for pid, (k, _, _) in note1_dec.items() if k == "ran")
    unres = sorted(pid for pid, (k, w, _) in note1_dec.items() if k == "ran" and w.startswith("UNRESOLVED"))
    labels = {"ran_before_points": {arm: lab1}}
    json.dump(labels, open(os.path.join(d, f"labels-e220-{arm}.json"), "w"), indent=1, sort_keys=True)
    rec = {"what": f"E220 arm {arm}'s step 6n: the registration's scan and report repeated, and the judgement (desk/neverrun_card_e220.py)",
           "arm": arm, "card": CARD[arm], "started": t0, "ended": now(), "scanner": swhy, "report": rwhy, "lab_head": S.get("lab_head"),
           "files_read": S.get("files_read"), "scan_sha256": sha(sp), "report_sha256": sha(rp), "n_points": len(v),
           "reading": f"dated note 1 ({NOTE1}; fix-e220, before any E220 datum; the orchestrator's RULING 1 of Fri 20 Nov 2026): a point counts "
                      f"as run on its arm's card only by a session record on that card; desk copies in folders naming no card never count",
           "n_never_run": len(v) - len(lab1), "ran_before_labelled": lab1, "ran_before_unresolved_labelled": unres,
           "note1_REPORTED": {pid: {"decision": k, "why": w, "files": fl} for pid, (k, w, fl) in note1_dec.items()},
           "literal_reading_REPORTED": {"what": "the registered literal reading (E220.md 4, N1): a token or configuration named in any file "
                                                "counted for the card, a folder naming no card counting for every card; REPORTED, never a label",
                                        "n_never_run": len(v) - len(ran), "ran_before": ran},
           "evidence": {x["id"]: x.get("evidence") for x in v if not x["never_run"]},
           "ran_before_hit_kinds_REPORTED": {pid: {"kind": k, "files": fl[:8]} for pid, (k, fl) in kinds.items()},
           "ran_before_desk_only_REPORTED": desk_only,
           "rule": "E220.md 4 read by dated note 1: a registered point the repeated scan finds run on its arm's card - by a session record on "
                   "that card - is labelled 'ran before' and leaves every rule, whatever the date (REPORTED, never a gate)"}
    json.dump(rec, open(os.path.join(d, f"judge-e220-{arm}.json"), "w"), indent=1, sort_keys=True)
    line = (f"NEVER-RUN-E220 arm {arm}: {len(v) - len(lab1)} of {len(v)} registered points never ran on {CARD[arm]} by dated note 1's reading "
            f"(a session record on the card) (scan {rec['scan_sha256'][:12]}, {S.get('files_read')} files, lab {str(S.get('lab_head'))[:12]}); "
            f"ran before, labelled: {', '.join(lab1) if lab1 else 'none'}{' (unresolved from the scan: ' + ', '.join(unres) + ')' if unres else ''}; "
            f"the literal reading (REPORTED, not a label): {len(v) - len(ran)} of {len(v)} never ran, {len(ran)} read ran before, "
            f"{len(desk_only)} of them with desk files only")
    open(os.path.join(d, f"judge-e220-{arm}.txt"), "w").write(json.dumps(rec, indent=1, sort_keys=True)[:4000] + "\n" + line + "\n")
    print(line)
    return 0


def check_labels(f, arm):
    try:
        L = json.load(open(f))
        ids = L["ran_before_points"][arm]
        ok = isinstance(ids, list) and all(isinstance(x, str) for x in ids) and set(L["ran_before_points"]) == {arm}
    except (OSError, ValueError, KeyError, TypeError):
        ok, ids = False, None
    mine = {q["id"] for q in arm_points(arm)}
    if not ok or any(x not in mine for x in ids):
        print(f"LABELS-REFUSED: {f} is not arm {arm}'s labels of its registered points")
        return 10
    print(f"LABELS-OK: {len(ids)} label(s) of arm {arm}'s registered points ({', '.join(ids) if ids else 'none'})")
    return 0


def main(a):
    if len(a) >= 2 and a[0] == "check-labels" and len(a) == 4 and a[2] == "--arm" and a[3] in CARD:
        return check_labels(a[1], a[3])
    if len(a) == 8 and a[0] == "run" and a[2] == "--arm" and a[3] in CARD and a[4] == "--lab" and a[6] == "--lanes":
        return run(a[1], a[3], a[5], a[7])
    print(__doc__.split("THE JUDGEMENT")[0])
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
