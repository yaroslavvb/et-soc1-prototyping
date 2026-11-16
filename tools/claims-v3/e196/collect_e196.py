#!/usr/bin/env python3
"""E196's collection at the desk (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): step 11's desk half, after the
copy-back. E193's collector's form (tools/claims-v3/e193/collect_e193.py), with no reducer: E196 is reduced after the data commit (step 13).

    /usr/bin/python3 -I -B tools/claims-v3/e196/collect_e196.py COPY DATA --box-home PATH [--login NAME]
        COPY  the session's directory as rsync copied it from the box (RB_OUT/e196-raw/T<T0>/)
        DATA  docs/reports/data/<day>-e196-zeroshare-aifoundry3, or for a gate stop docs/reports/gate-stops/<day>-e196-zeroshare-T<T0>-
              aifoundry3 (new; refused if it exists)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but MANIFEST.sha256
     itself and session.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. DATA in the kit's form: session/ (the wrapper's files: session.log, the first card command's time, the hashes, the pins and the
     preflight, the port's output, MANIFEST.sha256, session.rc) and run/ (the port's OUT as the box wrote it: its session.log, the two
     configuration reads, runs.jsonl, train.jsonl, checks.jsonl, marks.jsonl, the hosts' stderr.txt, the sampler's and the stops' error
     files, gen/ with arms.json and the tiles, STOP when one was written, SESSION_DONE), the telemetry as run/telemetry.jsonl.gz (gzip with
     no name and mtime 0: the same bytes every time; step 13 unpacks it and checks it against the box's manifest);
  3. THE SCRUB: the box's home path (as the box reported it) becomes "~" in every text file; in every holder line (a /dev/et... or lock:...
     word, a user, a process id: et-who's form) the user becomes <login>; our own login (from the look, --login) becomes <login> wherever it
     stands as a word; then no file may hold the box's home, any /home/ path or that login, else exit 3 (the desk-path gate, E183 note 5's,
     runs after this, from step 11). Binary files (the tiles) are copied as they are;
  4. facts-e196.json: the session's facts for the data README (registered against happened): the wrapper's lines (the checks, the first
     card command, the cut order, the stops, how it ended, the blocks complete), the card-minutes from the first card command to "session
     end", the smoke gate's verdict, the launch, process and read-back counts, the runtime lines dropped and the unreadable outputs, the
     telemetry's samples, samples off 600 MHz, the board's and the die's peaks with their times; never a reduced price;
  5. DATA/SHA256SUMS (paths beside it, as the lab's data lists).
Exit 0 COLLECTED, 3 a gate, 2 usage. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys

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
            want[os.path.normpath(p)] = h
    have = set()
    for dp, _dn, fn in os.walk(copy):
        for n in fn:
            have.add(os.path.normpath(os.path.relpath(os.path.join(dp, n), copy)))
    bad = ["missing %s" % p for p in want if p not in have]
    bad += ["differs %s" % p for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += ["not in the manifest: %s" % p for p in sorted(have - set(want) - {"MANIFEST.sha256", "session.rc"})]
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


def epoch(ts):
    t = subprocess.run(["date", "-d", ts, "+%s"], capture_output=True, text=True).stdout.strip()
    return int(t) if t.isdigit() else None


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, errors="ignore"):
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def facts_of(copy):
    sl = os.path.join(copy, "session.log")
    lines = open(sl, errors="replace").read().splitlines() if os.path.exists(sl) else []
    first = open(os.path.join(copy, "first-card-command.txt")).read().strip() if os.path.exists(
        os.path.join(copy, "first-card-command.txt")) else ""
    end = None
    for ln in lines:
        m = TS.match(ln)
        if m and "session end" in ln:
            end = epoch(m.group(1))
    run = os.path.join(copy, "run")
    runs, trecs, checks, marks = (jl(os.path.join(run, f)) for f in ("runs.jsonl", "train.jsonl", "checks.jsonl", "marks.jsonl"))
    tel = jl(os.path.join(run, "telemetry.jsonl"))
    sg = [m for m in marks if m.get("kind") == "smoke_gate"]
    bw = [(s["board_w"], s["t_ms"]) for s in tel if isinstance(s.get("board_w"), (int, float))]
    dc = [(s["temp_c"]["minshire"][0], s["t_ms"]) for s in tel if isinstance(s.get("temp_c", {}).get("minshire"), list)]
    pk = lambda v: {"value": max(v)[0], "first_t_ms": min(t for x, t in v if x == max(v)[0]),
                    "samples_at_peak": sum(1 for x, t in v if x == max(v)[0])} if v else None
    return {"schema": "e196-facts/1",
            "card_minutes_first_command_to_session_end": round((end - int(first)) / 60.0, 2) if (end and first) else None,
            "first_card_command_epoch": int(first) if first else None,
            "session_lines": [ln for ln in lines if re.search(r"checked|first card command|the cut order|GATE-STOP|STOP:|session stopped|"
                                                               r"without a registered stop|unreadable|complete:|refused|not free|"
                                                               r"session (start|end)", ln)],
            "session_rc": open(os.path.join(copy, "session.rc")).read().strip() if os.path.exists(os.path.join(copy, "session.rc")) else None,
            "smoke_gate": (sg[0].get("ok"), sg[0].get("problems")) if sg else None,
            "pass_launch_records": len(runs), "train_launch_records": len(trecs), "x14check_records": len(checks),
            "x14check_not_ok": sum(1 for c in checks if not c.get("ok")),
            "blocks_after": sorted({m.get("pass") for m in marks if m.get("kind") == "idle" and m.get("label") == "after"}),
            "device_processes": sum(1 for m in marks if m.get("kind") in ("run", "train", "heater", "heater_check")),
            "runtime_lines_dropped": sum(len(m.get("runtime_lines") or []) for m in marks if m.get("kind") == "host_lines"),
            "unreadable_host_outputs": [m.get("what") for m in marks if m.get("kind") == "host_lines" and m.get("written") is False],
            "telemetry_samples": len(tel),
            "samples_off_600_MHz": sum(1 for s in tel if int(s.get("mhz", {}).get("minion", 0)) != 600),
            "board_w_peak": pk(bw), "die_c_peak": pk(dc),
            "stop": open(os.path.join(run, "STOP")).read().strip() if os.path.exists(os.path.join(run, "STOP")) else None}


def main(argv):
    if len(argv) < 4 or argv[2] != "--box-home":
        print(__doc__)
        return 2
    copy, data, box_home = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/")
    login = argv[argv.index("--login") + 1] if "--login" in argv else ""
    if not box_home.startswith("/") or len(box_home) < 6:
        print("COLLECT-REFUSED: the box's home path %r is not an absolute path" % box_home)
        return 2
    if os.path.exists(data):
        print("COLLECT-REFUSED: %s exists: never merge into an earlier copy" % data)
        return 2
    bad, want = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print("COPY-BACK EXACT: every file of the box's MANIFEST.sha256 (%d) at its sha256, nothing else but session.rc" % len(want))
    out = {}
    for p in sorted(want) + [x for x in ("MANIFEST.sha256", "session.rc") if os.path.exists(os.path.join(copy, x))]:
        dst = p if p.split("/", 1)[0] == "run" else "session/" + p
        raw = open(os.path.join(copy, p), "rb").read()
        out[dst + ".gz" if p == "run/telemetry.jsonl" else dst] = ("gz" if p == "run/telemetry.jsonl" else "plain", raw)
    left = []
    os.makedirs(data)
    for dst, (kind, raw) in sorted(out.items()):
        q = os.path.join(data, dst)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        textual = dst.endswith(TEXT) or kind == "gz" or "." not in os.path.basename(dst)
        body = scrub(raw, box_home, login) if textual else raw
        if textual and (box_home.encode() in body or b"/home/" in body or (login and re.search(
                rb"(?<![\w.-])" + re.escape(login.encode()) + rb"(?![\w-])", body))):
            left.append(dst)
        with open(q, "wb") as f:
            f.write(gz(body) if kind == "gz" else body)
    if left:
        print("SCRUB FAILED: the box's home, a /home/ path or the login is left in " + ", ".join(left[:10]))
        return 3
    facts = facts_of(copy)
    fb = scrub(json.dumps(facts, indent=1, sort_keys=True).encode() + b"\n", box_home, login)
    if box_home.encode() in fb or b"/home/" in fb or (login and login.encode() in fb):
        print("SCRUB FAILED: facts-e196.json holds the box's home, a /home/ path or the login")
        return 3
    open(os.path.join(data, "facts-e196.json"), "wb").write(fb)
    rows = []
    for dp, _dn, fn in os.walk(data):
        for n in fn:
            p = os.path.relpath(os.path.join(dp, n), data)
            if p != "SHA256SUMS":
                rows.append((p, sha(os.path.join(data, p))))
    rows.sort()
    with open(os.path.join(data, "SHA256SUMS"), "w") as f:
        for p, h in rows:
            f.write("%s  %s\n" % (h, p))
    rel = data if not os.path.isabs(data) else os.path.basename(data)
    print("COLLECTED %s: %d files in SHA256SUMS; the scrub clean (no /home/ path, no login); card-minutes %s; session rc %s" % (
        rel, len(rows), facts["card_minutes_first_command_to_session_end"], facts["session_rc"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
