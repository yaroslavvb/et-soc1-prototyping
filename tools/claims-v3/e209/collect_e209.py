#!/usr/bin/env python3
"""E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): THE COLLECTION of E209's session (runbook step 11,
rb/s22_collect_e209.sh). Python's own modules only; it changes nothing it reads.

    /usr/bin/python3 -I -B tools/claims-v3/e209/collect_e209.py --root E209_ROOT --sid SID --rb-out RB_OUT --lab LAB [--desktest]

  1. THE BOX-TREE GATE: the session is E209_ROOT/sessions/<SID> (SID = <T0>-a2c0-E209), a real folder under the box root's sessions/ (no link
     anywhere in it), ended (MANIFEST.sha256 and runner.rc present); a desk test's session (its DESKTEST file, or a DESKTEST start line) is
     refused unless --desktest;
  2. COPY-BACK EXACT: one byte copy into RB_OUT/copy/<SID>/ (file by file, times kept), then every MANIFEST.sha256 line read OK in the copy
     and every file of the copy in the manifest but runner.rc and runner.out (the runner's two files outside it);
  3. THE CHECKS: E208's data lane's own checker, unchanged (LAB/docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1/check_session_e208.py,
     at its sha256 below): C0 the source (the schedule against the box root's src/SRC-SHA256SUMS; the harness line), C1 a clean end, C2 the
     runs against the schedule, C3 the identity, C4 the clock in every sample, C5 the stops replayed on every sample, C6 the timeouts and no
     kill word, C7 no leftover, C8 the sampler. Their verdicts are REPORTED, never a gate (a cut or stopped session FAILs C1 or C2 honestly);
  4. THE SCRUB: no byte of the copy holds the login name, a home folder's path or the box root's own path (the runner writes paths relative to
     the box root); a hit stops the collection (exit 16) before anything is written in LAB;
  5. THE DATA DIRECTORY LAB/docs/reports/data/<day>-e209-blind-matmul-aifoundry2/ (refused if it exists): session/ (the copy, byte for byte),
     checks-e209.json and checks-e209.txt (step 3), build-record-aifoundry2.json (the box root's build/BUILD-mms.json, byte for byte),
     neverrun-e209-card.txt and ranbefore-e209.json (step 6n's), facts-e209.json, README.md (DATA-README-FORM-e209.md's form, its facts
     filled from the records), SHA256SUMS (every file but itself, paths relative to the directory).
Prints the data directory's path relative to LAB last: "DATA DIR docs/reports/data/<...> (<n> files)". Exits: 0 written; 10 refused (the
gate); 14 the copy-back not exact; 16 the scrub found a private string (nothing written in LAB).
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


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--sid", required=True)
    ap.add_argument("--rb-out", required=True)
    ap.add_argument("--lab", required=True)
    ap.add_argument("--desktest", action="store_true")
    a = ap.parse_args(argv)
    root = os.path.realpath(a.root)
    if not re.fullmatch(r"\d{10}-a2c0-E209", a.sid):
        die(10, f"'{a.sid}' is not an E209 session id")
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
    # 2. the copy-back
    cp = os.path.join(a.rb_out, "copy", a.sid)
    if os.path.exists(cp):
        die(10, f"RB_OUT/copy/{a.sid} exists already (one copy-back)")
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
    ckdir = os.path.join(a.rb_out, "checks")
    os.makedirs(ckdir, exist_ok=True)
    r = subprocess.run(["/usr/bin/python3", "-I", "-B", ck, cp, "a2c0", os.path.join(root, "src"), "--out", os.path.join(ckdir, "checks-e209.json"),
                        "--txt", os.path.join(ckdir, "checks-e209.txt")], capture_output=True, text=True)
    if r.returncode not in (0, 1) or not os.path.exists(os.path.join(ckdir, "checks-e209.json")):
        die(14, f"the checker ended rc {r.returncode}: {r.stderr.strip()[-400:]}")
    cj = json.load(open(os.path.join(ckdir, "checks-e209.json")))
    # the checker's form (data-e208's): {"what", "session", "card", "checks": {"C0_src": {"verdict": ...}, ...}, "verdict": "ALL PASS" | ...}
    checks = cj.get("checks") if isinstance(cj, dict) and isinstance(cj.get("checks"), dict) else {}
    verdicts = {k: v.get("verdict") for k, v in checks.items() if isinstance(v, dict)}
    if not verdicts:
        die(14, "the checker's output names no check (checks-e209.json has no 'checks' table)")
    overall = cj.get("verdict")
    print(f"THE CHECKS (E208's data checker, unchanged): {overall}: " + ", ".join(f"{k} {v}" for k, v in verdicts.items()))
    # 4. the scrub
    me = pwd.getpwuid(os.getuid())
    pats = [me.pw_name.encode(), me.pw_dir.encode(), root.encode(), b"/home/"]
    hits = []
    scrub = [(rel, os.path.join(cp, rel)) for rel in files] + [(f"checks/{n}", os.path.join(ckdir, n)) for n in ("checks-e209.json", "checks-e209.txt")]
    for rel, path in scrub:
        b = open(path, "rb").read()
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
    rel_dd = f"docs/reports/data/{day}-e209-blind-matmul-aifoundry2"
    dd = os.path.join(lab, rel_dd)
    if os.path.exists(dd):
        die(10, f"{rel_dd} exists already")
    os.makedirs(dd)
    shutil.copytree(cp, os.path.join(dd, "session"))
    shutil.copyfile(os.path.join(ckdir, "checks-e209.json"), os.path.join(dd, "checks-e209.json"))
    shutil.copyfile(os.path.join(ckdir, "checks-e209.txt"), os.path.join(dd, "checks-e209.txt"))
    shutil.copyfile(os.path.join(root, "build", "BUILD-mms.json"), os.path.join(dd, "build-record-aifoundry2.json"))
    for n in ("ranbefore-e209.json",):
        if os.path.exists(os.path.join(a.rb_out, n)):
            shutil.copyfile(os.path.join(a.rb_out, n), os.path.join(dd, n))
    nr = sorted(x for x in os.listdir(a.rb_out) if x.startswith("neverrun-") and os.path.isdir(os.path.join(a.rb_out, x)))
    if nr and os.path.exists(os.path.join(a.rb_out, nr[-1], "neverrun-e209-card.txt")):
        shutil.copyfile(os.path.join(a.rb_out, nr[-1], "neverrun-e209-card.txt"), os.path.join(dd, "neverrun-e209-card.txt"))
    win = {}
    if os.path.exists(os.path.join(a.rb_out, "window.env")):
        for ln in open(os.path.join(a.rb_out, "window.env")):
            k, _, v = ln.strip().partition("=")
            win[k] = v
    first = {}
    if os.path.exists(os.path.join(a.rb_out, "e209-first.txt")):
        first = dict(x.split("=", 1) for x in open(os.path.join(a.rb_out, "e209-first.txt")).read().split())
    log = open(os.path.join(cp, "session.log"), errors="replace").read().splitlines()
    runs = q.get("queue") or []
    facts = {"experiment": "E209", "session": a.sid, "card": "aifoundry2 card 0", "t0_epoch": t0, "t0": pst(t0, ms=False),
             "first_card_command_session": pst(q.get("t_first_ms")), "close": pst(q.get("t_close_ms")), "card_min": q.get("card_min"),
             "runs_planned": 62, "runs_in_queue": len(runs), "runs_ran": q.get("n_ran"), "stop": q.get("stop"), "leftover": q.get("leftover"),
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
    json.dump(facts, open(os.path.join(dd, "facts-e209.json"), "w"), indent=1, sort_keys=True)
    form = open(os.path.join(HERE, "DATA-README-FORM-e209.md")).read()
    fill = {"SESSION": a.sid, "DAY": day, "T0": facts["t0"], "FIRST": str(facts["reboot_gate"]["stamp"]), "FWGATE": str(first.get("FWGATE")),
            "CLOSE": str(facts["close"]), "CARDMIN": str(facts["card_min"]), "RAN": str(facts["runs_ran"]), "STOP": str(facts["stop"]),
            "G": str(facts["window"].get("E209_G")), "LASTSTART": str(facts["window"].get("E209_LAST_START")),
            "LASTEND": str(facts["window"].get("E209_LAST_END")), "RUNNERRC": facts["runner_rc"],
            "CHECKS": f"{overall}: " + ", ".join(f"{k} {v}" for k, v in verdicts.items()),
            "NOTRUN": "; ".join(f"{x['i']} {x['arm']} ({x['why']})" for x in facts["not_run"]) or "none",
            "NEVERRUN": open(os.path.join(dd, "neverrun-e209-card.txt")).read().strip().splitlines()[-1] if os.path.exists(os.path.join(dd, "neverrun-e209-card.txt")) else "NOT RUN"}
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
