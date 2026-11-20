#!/usr/bin/env python3
"""E220 (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE COLLECTION (runbook step 11), E209's FIXED collection
(tools/claims-v3/e209/collect_e209_n1.py, landed in f92136dd with E209's kit note 1: THE MASK registered there) for E220's session, with
E220's names and its second build record. Python's own modules only; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e220/collect_e220b.py --root E220B_ROOT --sid SID --rb-out RB_OUT --lab LAB [--copy-name NAME] \
        [--desktest]
    /usr/bin/python3 -I -B tools/claims-v3/e220/collect_e220b.py --manifest-check SESSION_DIR        (step 13's manifest read)

THE MASK (E209's kit note 1, E200's registered form), registered here BEFORE ANY E220 DATUM (E209's step-11 lesson: every real fwgate READ
record carries the box's home in its ledger line): in fwgate's read record in the session's first/ folder
(first/fwgate-aifoundry2-c0-<YYYYMMDD>-<HHMMSS>.json), the ONE line
    "ledger": "<the box's home>/.local/state/fwgate/aifoundry2-c0.jsonl",
is written with the home as "~", in the data directory's copy only; nothing else changes in any file. The home is the user database's
(pwd), as fwgate.py and the scrub read it. A record with no such line is left as it is; a record with two such lines is refused (16). The
copy-back in RB_OUT keeps the box's bytes (the raw record stays on this box, outside the lab). THE SCRUB then runs on the masked bytes of
that record and on the copy's bytes of every other file: a login name, a home path, the box root's path or '/home/' left anywhere stops the
collection (16) before anything is written in LAB.

THE STEPS (E209's, with E220's names):
  1. THE BOX-TREE GATE: the session is E220B_ROOT/sessions/<SID> (SID = <T0>-a2c0-E220), a real folder under the box root's sessions/ (no link
     anywhere in it), ended (MANIFEST.sha256 and runner.rc present); a desk test's session (its DESKTEST file, or a DESKTEST start line) is
     refused unless --desktest;
  2. COPY-BACK EXACT: one byte copy into RB_OUT/<NAME>/<SID>/ (--copy-name, default copy; refused (10) if RB_OUT/<NAME> exists: one copy-back a
     name), then every MANIFEST.sha256 line read OK in the copy and every file of the copy in the manifest but runner.rc and runner.out;
  3. THE CHECKS: E208's data lane's own checker, unchanged (LAB/docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1/check_session_e208.py, at its
     data directory's SHA256SUMS): C0-C8, REPORTED, never a gate (a cut or stopped session FAILs C1 or C2 honestly);
  4. THE MASK, then THE SCRUB (above);
  5. THE DATA DIRECTORY LAB/docs/reports/data/<day>-e220-blind-matmul-aifoundry2/ (refused if it exists): session/ (the copy, byte for byte,
     but for the masked line), checks-e220b.json and checks-e220b.txt (step 3), build-record-aifoundry2.json and build-record-e220b-aifoundry2.json
     (the box root's build/BUILD-mms.json and build/BUILD-e220b.json, byte for byte), neverrun-e220b-card.txt and ranbefore-e220b.json (step
     6n's), facts-e220b.json, README.md (DATA-README-FORM-e220b.md's form, its facts filled from the records), SHA256SUMS (every file but itself).
Prints the masked line with both sha256, the data directory's path relative to LAB last: "DATA DIR docs/reports/data/<...> (<n> files)".
Exits: 0 written; 10 refused (the gate, or the copy-back's name taken); 14 the copy-back not exact; 16 the scrub found a private string, or
THE MASK met two ledger lines in one record (nothing written in LAB). --manifest-check: 0 every line OK (masked lines named), 10 not.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import hashlib
import json
import os
import pwd
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1/check_session_e208.py"
CHECKER_SHA = None      # read from that data directory's SHA256SUMS (the committed list), below
MASK_REC = re.compile(r"first/fwgate-aifoundry2-c0-\d{8}-\d{6}\.json")     # fwgate's read record, as step 7 copies it into first/
LEDGER_TAIL = b"/.local/state/fwgate/aifoundry2-c0.jsonl"                  # fwgate's attempt ledger for this card (fwgate.py ledger_path())
LEDGER_LINE = re.compile(rb'(\s*"ledger": ")(.*)(' + re.escape(LEDGER_TAIL) + rb'",?)')
try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001
    TZ = None


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pst(ms_or_s, ms=True):
    if ms_or_s is None:
        return None
    t = ms_or_s / 1000.0 if ms else ms_or_s
    return datetime.datetime.fromtimestamp(t, TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def die(code, words):
    print(f"COLLECT REFUSED: {words}" if code == 10 else f"COLLECT STOPPED: {words}")
    sys.exit(code)


def ledger_lines(b, what):
    """The record's lines whose ledger path is <what>/.local/state/fwgate/aifoundry2-c0.jsonl exactly (index, match)."""
    out = []
    for i, ln in enumerate(b.split(b"\n")):
        m = LEDGER_LINE.fullmatch(ln)
        if m and m.group(2) == what:
            out.append((i, m))
    return out


def swap(b, i, m, new):
    lines = b.split(b"\n")
    lines[i] = m.group(1) + new + m.group(3)
    return b"\n".join(lines)


def mask_record(b, home):
    """THE MASK (E209's kit note 1's form, registered in E220's kit): (the masked bytes, the masked line's number); (b, 0) when no line holds the home's exact ledger
    path; two such lines stop the collection (16)."""
    hits = ledger_lines(b, home)
    if not hits:
        return b, 0
    if len(hits) > 1:
        die(16, f"THE MASK: {len(hits)} ledger lines in one record (lines {[i + 1 for i, _ in hits]}), not the one line "
                "E209's kit note 1 masks: nothing written in LAB; tell the orchestrator")
    i, m = hits[0]
    return swap(b, i, m, b"~"), i + 1


def manifest_check(sd):
    """Step 13's manifest read (rb/s24_score_e220.sh): `sha256sum -c MANIFEST.sha256` in SESSION_DIR, but for THE MASK."""
    home = pwd.getpwuid(os.getuid()).pw_dir.encode()
    man = os.path.join(sd, "MANIFEST.sha256")
    if not os.path.isfile(man):
        print("MANIFEST CHECK FAILED: no MANIFEST.sha256 in the session folder")
        return 10
    rows, bad, masked = [], [], []
    for ln in open(man):
        if ln.strip():
            h, r = ln.rstrip("\n").split("  ", 1)
            rows.append((h, r))
    for h, r in rows:
        p = os.path.join(sd, r)
        if not os.path.isfile(p):
            bad.append(f"{r}: missing")
            continue
        s = sha(p)
        if s == h:
            continue
        if MASK_REC.fullmatch(os.path.normpath(r)):
            b = open(p, "rb").read()
            back = ledger_lines(b, b"~")
            if len(back) == 1:
                raw = swap(b, back[0][0], back[0][1], home)
                if hashlib.sha256(raw).hexdigest() == h and len(ledger_lines(raw, home)) == 1 and mask_record(raw, home)[0] == b:
                    masked.append(f"{r} line {back[0][0] + 1} (the box's bytes {h[:16]}... = its manifest line; committed {s[:16]}...)")
                    continue
            bad.append(f"{r}: differs, and not by THE MASK of E209's kit note 1 (E220's kit) alone")
            continue
        bad.append(f"{r}: differs")
    if not rows or bad:
        print(f"MANIFEST CHECK FAILED: {len(bad)} of {len(rows)} manifest lines not OK: {bad[:6]}")
        return 10
    print(f"MANIFEST CHECK: {len(rows)} of {len(rows)} manifest lines OK ({len(masked)} by THE MASK of E209's kit note 1 (E220's kit)"
          f"{': ' + '; '.join(masked) if masked else ''})")
    return 0


def main(argv):
    if argv and argv[0] == "--manifest-check":
        if len(argv) != 2:
            print("usage: collect_e220b.py --manifest-check SESSION_DIR")
            return 2
        return manifest_check(argv[1])
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--sid", required=True)
    ap.add_argument("--rb-out", required=True)
    ap.add_argument("--lab", required=True)
    ap.add_argument("--copy-name", default="copy")
    ap.add_argument("--desktest", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.realpath(a.root)
    if not re.fullmatch(r"\d{10}-a2c0-E220", a.sid):
        die(10, f"'{a.sid}' is not an E220 session id")
    if not re.fullmatch(r"copy[A-Za-z0-9._-]*", a.copy_name) or ".." in a.copy_name:
        die(10, f"--copy-name '{a.copy_name}': a name 'copy...' of letters, digits, '.', '_' and '-' only")
    sd = os.path.join(root, "sessions", a.sid)
    if os.path.islink(sd) or not os.path.isdir(sd) or os.path.realpath(sd) != os.path.join(root, "sessions", a.sid):
        die(10, f"THE BOX-TREE GATE: {a.sid} is not a real folder under the box root's sessions/")
    for dp, dn, fn in os.walk(sd):
        for n in dn + fn:
            if os.path.islink(os.path.join(dp, n)):
                die(10, f"THE BOX-TREE GATE: a link inside the session ({os.path.relpath(os.path.join(dp, n), sd)})")
    if not (os.path.exists(os.path.join(sd, "MANIFEST.sha256")) and os.path.exists(os.path.join(sd, "runner.rc"))):
        die(10, "the session has not ended (no MANIFEST.sha256 or runner.rc): step 10 first")
    so = os.path.join(root, "sessions", a.sid + ".start.out")
    desk = os.path.exists(os.path.join(sd, "DESKTEST")) or (os.path.exists(so) and "STARTED DESKTEST" in open(so, errors="replace").read())
    if desk and not a.desktest:
        die(10, "a desk test's session (DESKTEST): never collected as data")
    # 2. the copy-back, under its own name (one copy-back a name)
    cbase = os.path.join(a.rb_out, a.copy_name)
    cp = os.path.join(cbase, a.sid)
    if os.path.exists(cbase):
        die(10, f"RB_OUT/{a.copy_name} exists already (one copy-back a name: read why, then give a new --copy-name)")
    print(f"THE COPY-BACK'S NAME (E209's kit note 1's form, registered in E220's kit): RB_OUT/{a.copy_name}/{a.sid}/ (checks in RB_OUT/{a.copy_name}/checks/)")
    shutil.copytree(sd, cp, symlinks=True)
    man = {}
    for ln in open(os.path.join(cp, "MANIFEST.sha256")):
        h, r = ln.rstrip("\n").split("  ", 1)
        man[r] = h
    bad = [r for r, h in man.items() if not os.path.isfile(os.path.join(cp, r)) or sha(os.path.join(cp, r)) != h]
    files = sorted(os.path.relpath(os.path.join(dp, n), cp) for dp, _, fn in os.walk(cp) for n in fn)
    extra = [r for r in files if r not in man and r not in ("MANIFEST.sha256", "runner.rc", "runner.out")]
    if bad or extra:
        die(14, f"COPY-BACK NOT EXACT: {len(bad)} manifest lines not OK {bad[:4]}, {len(extra)} files outside it {extra[:4]}")
    print(f"COPY-BACK EXACT: {len(man)} manifest lines OK, {len(files)} files ({a.sid})")
    # 3. the checks, E208's data lane's checker unchanged
    lab = os.path.realpath(a.lab)
    sums = {}
    for ln in open(os.path.join(lab, os.path.dirname(CHECKER), "SHA256SUMS")):
        h, r = ln.rstrip("\n").split("  ", 1)
        sums[r] = h
    ck = os.path.join(lab, CHECKER)
    if sums.get(os.path.basename(CHECKER)) != sha(ck):
        die(10, f"{CHECKER} is not at its data directory's SHA256SUMS")
    ckdir = os.path.join(cbase, "checks")
    os.makedirs(ckdir, exist_ok=True)
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", ck, cp, "a2c0", os.path.join(root, "src"), "--out", os.path.join(ckdir, "checks-e220b.json"),
                        "--txt", os.path.join(ckdir, "checks-e220b.txt")], capture_output=True, text=True)
    if r.returncode not in (0, 1) or not os.path.exists(os.path.join(ckdir, "checks-e220b.json")):
        die(14, f"the checker ended rc {r.returncode}: {r.stderr.strip()[-400:]}")
    cj = json.load(open(os.path.join(ckdir, "checks-e220b.json")))
    # the checker's form (data-e208's): {"what", "session", "card", "checks": {"C0_src": {"verdict": ...}, ...}, "verdict": "ALL PASS" | ...}
    checks = cj.get("checks") if isinstance(cj, dict) and isinstance(cj.get("checks"), dict) else {}
    verdicts = {k: v.get("verdict") for k, v in checks.items() if isinstance(v, dict)}
    if not verdicts:
        die(14, "the checker's output names no check (checks-e220b.json has no 'checks' table)")
    overall = cj.get("verdict")
    print(f"THE CHECKS (E208's data checker, unchanged): {overall}: " + ", ".join(f"{k} {v}" for k, v in verdicts.items()))
    # 4. the scrub, after THE MASK (E209's kit note 1's form, registered in E220's kit): that one line of fwgate's read record, the box's home written as "~"
    me = pwd.getpwuid(os.getuid())
    masked = {}
    for rel in files:
        if MASK_REC.fullmatch(rel):
            raw = open(os.path.join(cp, rel), "rb").read()
            mb, li = mask_record(raw, me.pw_dir.encode())
            if li:
                masked[rel] = (mb, li, hashlib.sha256(raw).hexdigest(), hashlib.sha256(mb).hexdigest())
    for rel, (mb, li, rs, ms) in masked.items():
        print(f"THE MASK (E209's kit note 1's form, registered in E220's kit): {rel} line {li}, fwgate's ledger path with the box's home written as \"~\"; the box's "
              f"bytes sha256 {rs} (its MANIFEST.sha256 line {'lists it' if man.get(rel) == rs else 'DIFFERS'}), the committed bytes sha256 {ms}")
    if not masked:
        print("THE MASK (E209's kit note 1's form, registered in E220's kit): no line to mask (no fwgate read record in first/ holds the box's home in its ledger path)")
    json.dump({"note": "the collection's MASK (E220's kit, E209's note 1 form)", "session": a.sid,
               "masked": [{"file": f"session/{rel}", "line": li, "box_sha256": rs, "manifest_sha256": man.get(rel), "committed_sha256": ms,
                           "committed_line": mb.split(b"\n")[li - 1].decode("utf-8", "replace")} for rel, (mb, li, rs, ms) in masked.items()]},
              open(os.path.join(cbase, "mask.json"), "w"), indent=1, sort_keys=True)
    pats = [me.pw_name.encode(), me.pw_dir.encode(), root.encode(), b"/home/"]
    hits = []
    scrub = [(rel, os.path.join(cp, rel)) for rel in files] + [(f"checks/{n}", os.path.join(ckdir, n)) for n in ("checks-e220b.json", "checks-e220b.txt")]
    for rel, path in scrub:
        b = masked[rel][0] if rel in masked else open(path, "rb").read()
        if rel.endswith(".gz"):
            import gzip
            try:
                b = gzip.decompress(b)
            except OSError:
                pass
        for p in pats:
            if p and p in b:
                hits.append(f"{rel}: {'the login name' if p == pats[0] else 'a home path' if p in (pats[1], pats[3]) else 'the box root path'}")
                break
    if hits:
        die(16, f"THE SCRUB found {len(hits)} file(s) with a private string ({hits[:5]}): nothing written in LAB; tell the orchestrator")
    print(f"THE SCRUB: {len(scrub)} files (the copy and the checks), no login name, home path or box-root path")
    # 5. the data directory
    q = json.load(open(os.path.join(cp, "queue.json")))
    st = json.load(open(os.path.join(cp, "status.json"))) if os.path.exists(os.path.join(cp, "status.json")) else {}
    t0 = int(a.sid.split("-")[0])
    day = datetime.datetime.fromtimestamp(t0, TZ).strftime("%Y-%m-%d")
    rel_dd = f"docs/reports/data/{day}-e220-blind-matmul-aifoundry2"
    dd = os.path.join(lab, rel_dd)
    if os.path.exists(dd):
        die(10, f"{rel_dd} exists already")
    os.makedirs(dd)
    shutil.copytree(cp, os.path.join(dd, "session"))
    for rel, (mb, li, rs, ms) in masked.items():
        dst = os.path.join(dd, "session", rel)
        with open(dst, "wb") as f:
            f.write(mb)
        shutil.copystat(os.path.join(cp, rel), dst)
    shutil.copyfile(os.path.join(ckdir, "checks-e220b.json"), os.path.join(dd, "checks-e220b.json"))
    shutil.copyfile(os.path.join(ckdir, "checks-e220b.txt"), os.path.join(dd, "checks-e220b.txt"))
    shutil.copyfile(os.path.join(root, "build", "BUILD-mms.json"), os.path.join(dd, "build-record-aifoundry2.json"))
    shutil.copyfile(os.path.join(root, "build", "BUILD-e220b.json"), os.path.join(dd, "build-record-e220b-aifoundry2.json"))
    for n in ("ranbefore-e220b.json",):
        if os.path.exists(os.path.join(a.rb_out, n)):
            shutil.copyfile(os.path.join(a.rb_out, n), os.path.join(dd, n))
    nr = sorted(x for x in os.listdir(a.rb_out) if x.startswith("neverrun-") and os.path.isdir(os.path.join(a.rb_out, x)))
    if nr and os.path.exists(os.path.join(a.rb_out, nr[-1], "neverrun-e220b-card.txt")):
        shutil.copyfile(os.path.join(a.rb_out, nr[-1], "neverrun-e220b-card.txt"), os.path.join(dd, "neverrun-e220b-card.txt"))
    win = {}
    if os.path.exists(os.path.join(a.rb_out, "window.env")):
        for ln in open(os.path.join(a.rb_out, "window.env")):
            k, _, v = ln.strip().partition("=")
            win[k] = v
    first = {}
    if os.path.exists(os.path.join(a.rb_out, "e220b-first.txt")):
        first = dict(x.split("=", 1) for x in open(os.path.join(a.rb_out, "e220b-first.txt")).read().split())
    log = open(os.path.join(cp, "session.log"), errors="replace").read().splitlines()
    runs = q.get("queue") or []
    facts = {"experiment": "E220", "session": a.sid, "card": "aifoundry2 card 0", "t0_epoch": t0, "t0": pst(t0, ms=False),
             "first_card_command_session": pst(q.get("t_first_ms")), "close": pst(q.get("t_close_ms")), "card_min": q.get("card_min"),
             "runs_planned": 103, "runs_in_queue": len(runs), "runs_ran": q.get("n_ran"), "stop": q.get("stop"), "leftover": q.get("leftover"),
             "rest_die_c": q.get("rest_die_c"), "rest_board_w": q.get("rest_board_w"), "runner_rc": open(os.path.join(cp, "runner.rc")).read().strip(),
             "window": {k: (pst(int(v), ms=False) if v.isdigit() else v) for k, v in win.items()},
             "reboot_gate": {"stamp": pst(int(first["FIRST"]), ms=False) if first.get("FIRST", "").isdigit() else None,
                             "mode": first.get("FWGATE"), "folder": "session/first/"},
             "checks": verdicts, "log_first": log[0][:300] if log else None, "log_last": log[-1][:300] if log else None,
             "not_run": [{"i": x.get("i"), "arm": x.get("arm"), "why": x.get("why")} for x in runs if not x.get("ran")],
             "desktest": desk}
    facts["checks_overall"] = overall
    for k in ("C4_clock", "C5_stops"):
        if isinstance(checks.get(k), dict):
            facts[k] = {kk: vv for kk, vv in checks[k].items() if kk != "verdict"}
    json.dump(facts, open(os.path.join(dd, "facts-e220b.json"), "w"), indent=1, sort_keys=True)
    form = open(os.path.join(HERE, "DATA-README-FORM-e220b.md")).read()
    fill = {"SESSION": a.sid, "DAY": day, "T0": facts["t0"], "FIRST": str(facts["reboot_gate"]["stamp"]), "FWGATE": str(first.get("FWGATE")),
            "CLOSE": str(facts["close"]), "CARDMIN": str(facts["card_min"]), "RAN": str(facts["runs_ran"]), "STOP": str(facts["stop"]),
            "G": str(facts["window"].get("E220B_G")), "LASTSTART": str(facts["window"].get("E220B_LAST_START")),
            "LASTEND": str(facts["window"].get("E220B_LAST_END")), "RUNNERRC": facts["runner_rc"],
            "CHECKS": f"{overall}: " + ", ".join(f"{k} {v}" for k, v in verdicts.items()),
            "NOTRUN": "; ".join(f"{x['i']} {x['arm']} ({x['why']})" for x in facts["not_run"]) or "none",
            "NEVERRUN": open(os.path.join(dd, "neverrun-e220b-card.txt")).read().strip().splitlines()[-1] if os.path.exists(os.path.join(dd, "neverrun-e220b-card.txt")) else "NOT RUN"}
    for k, v in fill.items():
        form = form.replace("{{" + k + "}}", v)
    open(os.path.join(dd, "README.md"), "w").write(form)
    rows = []
    for dp, dn, fn in os.walk(dd):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            r_ = os.path.relpath(p, dd)
            if r_ != "SHA256SUMS":
                rows.append(f"{sha(p)}  {r_}")
    open(os.path.join(dd, "SHA256SUMS"), "w").write("\n".join(sorted(rows, key=lambda x: x.split("  ", 1)[1])) + "\n")
    print(f"DATA DIR {rel_dd} ({len(rows) + 1} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
