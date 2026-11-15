#!/usr/bin/env python3
"""E193's collection at the desk (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): step 11's desk half for one sitting,
after the copy-back. E189's collector's form (collect_e189.py), with no reducer: E193 is reduced after the data commit (step 13).

    /usr/bin/python3 -I -B tools/claims-v3/e193/collect_e193.py COPY DATA --box-home PATH --sitting A|B [--login NAME]
        COPY  the session's directory as rsync copied it from the box (RB_OUT/e193-raw/T<T0>/)
        DATA  docs/reports/data/<day>-e193-x04-clock-sitting-<a|b>-aifoundry3 (new; refused if it exists)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but
     MANIFEST.sha256 itself and session.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. DATA in the kit's form: session/ (session.log, the two config reads, the holder check's output, the first card command's time, the
     binaries' hashes, the harness and preflight outputs, the smoke's runner output and gate, the main runner's output, MANIFEST.sha256,
     session.rc), smoke/ and x04/ (each runner call's run.log, events.jsonl, runs.jsonl, device-stdout.txt, device-stderr.txt, any
     stderr-*.txt and STOPPED, and its telemetry as telemetry.jsonl.gz, gzip with no name and mtime 0, so the same bytes every time;
     step 13 unpacks it and checks it against the box's manifest before the reducer reads it);
  3. THE SCRUB: the box's home path (as the box reported it) becomes "~" in every text file; in every holder line (a /dev/et... or
     lock:... word, a user, a process id: et-who's form, which the runner logs when the card is busy) the user becomes <login>; our own
     login (from the look, --login) becomes <login> wherever it stands as a word; then no file may hold the box's home, any /home/ path or
     that login, else exit 3 (the desk-path gate, E183 note 5's, runs after this, from step 11);
  4. facts-e193-<sitting>.json: the session's facts for the data README (registered against happened): the session log's gate and stop
     lines, the card-minutes from the first card command to "session end", each runner call's calls, launches, passes, stops, telemetry
     samples, samples off 600 MHz and the board's and the die's peaks (check_e193.py summary's reading); never a reduced price;
  5. DATA/SHA256SUMS (paths beside it, as the lab's data lists).
Exit 0 COLLECTED, 3 a gate, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".sha256", ".jsonl")
HOLDER = re.compile(r"((?:/dev/et[\w]+|lock:[\w.-]+)\s+)([A-Za-z_][\w.-]*)(\s+\d+)")
TS = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) ")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def copy_back_exact(copy):
    man = os.path.join(copy, "MANIFEST.sha256")
    if not os.path.exists(man):
        return ["no MANIFEST.sha256"], {}
    want = {}
    for ln in open(man):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            want[p] = h
    have = set()
    for dp, _dn, fn in os.walk(copy):
        for n in fn:
            have.add(os.path.relpath(os.path.join(dp, n), copy))
    bad = [f"missing {p}" for p in want if p not in have]
    bad += [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += [f"not in the manifest: {p}" for p in sorted(have - set(want) - {"MANIFEST.sha256", "session.rc"})]
    return bad, want


def scrub(data, box_home, login):
    t = data.replace(box_home.encode(), b"~")
    s = t.decode("utf-8", errors="surrogateescape")
    s = HOLDER.sub(lambda m: m.group(1) + "<login>" + m.group(3), s)
    if login:
        s = re.sub(r"(?<![\w.-])" + re.escape(login) + r"(?![\w-])", "<login>", s)
    return s.encode("utf-8", errors="surrogateescape")


def gz(data):
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as f:
        f.write(data)
    return buf.getvalue()


def card_minutes(session_log, first):
    end = None
    for ln in open(session_log, errors="replace"):
        m = TS.match(ln)
        if m and "session end" in ln:
            end = m.group(1)
    if not end or not first:
        return None
    t = subprocess.run(["date", "-d", end, "+%s"], capture_output=True, text=True).stdout.strip()
    return round((int(t) - int(first)) / 60.0, 2) if t.isdigit() else None


def main(argv):
    if len(argv) < 6 or argv[2] != "--box-home" or "--sitting" not in argv:
        print(__doc__)
        return 2
    copy, data, box_home = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/")
    sit = argv[argv.index("--sitting") + 1]
    login = argv[argv.index("--login") + 1] if "--login" in argv else ""
    if sit not in ("A", "B"):
        print("COLLECT-REFUSED: --sitting is A or B")
        return 2
    if not box_home.startswith("/") or len(box_home) < 6:
        print(f"COLLECT-REFUSED: the box's home path {box_home!r} is not an absolute path")
        return 2
    if os.path.exists(data):
        print(f"COLLECT-REFUSED: {data} exists: never merge into an earlier copy")
        return 2
    bad, want = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print(f"COPY-BACK EXACT: every file of the box's MANIFEST.sha256 ({len(want)}) at its sha256, nothing else but session.rc")
    out = {}
    for p in sorted(want) + [x for x in ("MANIFEST.sha256", "session.rc") if os.path.exists(os.path.join(copy, x))]:
        top = p.split("/", 1)
        if len(top) == 2 and top[0] in ("smoke", "x04"):
            dst = p
        else:
            dst = "session/" + p
        raw = open(os.path.join(copy, p), "rb").read()
        if p.endswith("telemetry.jsonl"):
            out[dst + ".gz"] = ("gz", raw)
        else:
            out[dst] = ("plain", raw)
    left = []
    os.makedirs(data)
    for dst, (kind, raw) in sorted(out.items()):
        q = os.path.join(data, dst)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        body = scrub(raw, box_home, login) if (dst.endswith(TEXT) or kind == "gz" or "." not in os.path.basename(dst)) else raw
        if box_home.encode() in body or b"/home/" in body or (login and re.search(
                rb"(?<![\w.-])" + re.escape(login.encode()) + rb"(?![\w-])", body)):
            left.append(dst)
        with open(q, "wb") as f:
            f.write(gz(body) if kind == "gz" else body)
    if left:
        print("SCRUB FAILED: the box's home, a /home/ path or the login is left in " + ", ".join(left[:10]))
        return 3
    sess = os.path.join(data, "session")
    first = open(os.path.join(sess, "first-card-command.txt")).read().strip() if os.path.exists(
        os.path.join(sess, "first-card-command.txt")) else ""
    facts = {"schema": "e193-facts/1", "sitting": sit, "card_minutes_first_command_to_session_end":
             card_minutes(os.path.join(sess, "session.log"), first),
             "session_lines": [ln.rstrip("\n") for ln in open(os.path.join(sess, "session.log"), errors="replace")
                               if re.search(r"GATE-STOP|stopped|SMOKE|config read|session (start|end)|main run|smoke (start|end)", ln)],
             "session_rc": open(os.path.join(sess, "session.rc")).read().strip() if os.path.exists(os.path.join(sess, "session.rc")) else None,
             "runner_calls": {}}
    for d in ("smoke", "x04"):
        if os.path.isdir(os.path.join(copy, d)):
            r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "check_e193.py"), "summary", os.path.join(copy, d)],
                               capture_output=True, text=True)
            facts["runner_calls"][d] = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip().startswith("{") else {
                "error": r.stderr[-300:]}
    with open(os.path.join(data, f"facts-e193-{sit.lower()}.json"), "w") as f:
        f.write(json.dumps(facts, indent=1, sort_keys=True) + "\n")
    body = open(os.path.join(data, f"facts-e193-{sit.lower()}.json"), "rb").read()
    if box_home.encode() in body or b"/home/" in body or (login and login.encode() in body):
        print("SCRUB FAILED: facts-e193 holds the box's home, a /home/ path or the login")
        return 3
    rows = []
    for dp, _dn, fn in os.walk(data):
        for n in fn:
            p = os.path.relpath(os.path.join(dp, n), data)
            if p != "SHA256SUMS":
                rows.append((p, sha(os.path.join(data, p))))
    rows.sort()
    with open(os.path.join(data, "SHA256SUMS"), "w") as f:
        for p, h in rows:
            f.write(f"{h}  {p}\n")
    rel = data if not os.path.isabs(data) else os.path.basename(data)
    print(f"COLLECTED {rel}: sitting {sit}; {len(rows)} files in SHA256SUMS; the scrub clean (no /home/ path, no login); "
          f"card-minutes {facts['card_minutes_first_command_to_session_end']}; session rc {facts['session_rc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
