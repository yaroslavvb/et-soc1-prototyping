#!/usr/bin/env python3
"""E200's collection at the desk (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): step 11's desk half for one sitting, after
the copy-back. E197's collector (tools/claims-v3/e197/collect_e197.py, unchanged beside it) on a desk that is the box, with E194's
box-tree gate (tools/claims-v3/e194/collect_e194.py's, the lesson of E183's note 5 for a desk that is the box) and no reducer: E200 is
reduced after the data commit (step 13, reduce_e200.py). Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e200/collect_e200.py COPY DATA --box-home PATH --sitting 1|2 [--login NAME] [--allow-desktest]
        COPY  the sitting's directory as rsync copied it from the box tree (RB_OUT/e200-raw/T<T0>/)
        DATA  docs/reports/data/<day>-e200-regfile-sitting-<n>-aifoundry2, or for a gate stop
              docs/reports/gate-stops/<day>-e200-regfile-sitting-<n>-T<T0>-aifoundry2 (new; refused if it exists)

  1. COPY-BACK EXACT: every file of the box's MANIFEST.sha256 is in COPY at its sha256, and COPY holds nothing else but
     MANIFEST.sha256 itself and wrapper.rc (the one file the wrapper writes after it); else exit 3, nothing written;
  2. THE BOX-TREE GATE (E194's, before anything is written): in every text and .gz file of COPY, each place the box's home is written
     must begin a path inside the box tree (<home>/claude/et-soc1-prototyping/, read lexically: a path through ".", ".." or "//" that
     leaves the tree stops it), or be the home itself, or be fwgate's own attempt ledger for this card (<home>/.local/state/fwgate/
     aifoundry2-c0.jsonl, which fwgate's read record names: tools/claims-v3/fwgate/README.md); and no file may hold a session scratch root
     (/tmp/claude-); else exit 3, nothing written ("a desk path in the session's files": on this box a desk path carries the same home, so
     this gate runs before the scrub can hide it);
  3. DATA in the kit's form: session/ (the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, ref-patch.txt,
     diegate-<k>.jsonl and .err, run_session.out, watch.jsonl, watch.out, summary.txt, config-end.out and .err, first/ (step 7's folder: the
     config read's stdout and stderr, et-who after it, and fwgate's read record with its raw answer when the look read NEEDS-READ),
     MANIFEST.sha256, wrapper.rc), ref/ (the four files the session ran: E197's run_session.sh, stopwatch.py and trains.tsv byte for byte
     at E197's registration's sha256, and E200's runner run_trains.py at E200's runner sha256), run/ (the reference session's OUT: runs.jsonl,
     marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, STOP and SESSION_DONE when there, and its telemetry as
     telemetry.jsonl.gz, gzip with no name and mtime 0, so the same bytes every time; step 13 unpacks it and checks it against the box's
     manifest before the reduction reads it);
  4. THE SCRUB: the box's home path (as the box reported it) becomes "~" in every text file; in every holder line the user becomes <login>;
     our own login (from the look, --login) becomes <login> wherever it stands as a word; then no file may hold the box's home, any /home/
     path or that login, else exit 3 (k6's desk-path gate runs after this, from step 11). The four ref/ files must keep their pinned bytes;
  5. facts-e200-<n>.json: the sitting's facts for the data README (registered against happened): the plan; the wrapper's key lines (the
     firmware identity, the first card command and the cap, the die gate, the smoke gate, the kit's smoke check, the clock (C3), the blocks,
     the deadline, the stop, SITTING-RESULT, GATE-STOP, HUNG, a crash, the configuration at the end, the card time); the card-minutes from the
     first card command to "session end"; the launches and train processes recorded; the telemetry's samples, samples at 800 MHz, at 600 MHz
     and at other clocks, and the board's, the die's and the latch's peaks; never a reduced price;
  6. DATA/SHA256SUMS (paths beside it, as the lab's data lists).
A session whose start line names DESKTEST (the wrapper's desk-test variables were set) is refused before anything (exit 3): the card day
never sets them; only the runbook's desk test collects such a session, with RB_DESKTEST=1 in its environment and --allow-desktest.
Exit 0 COLLECTED, 3 a gate, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEXT = (".json", ".txt", ".log", ".err", ".out", ".rc", ".sha256", ".jsonl", ".tsv", ".py", ".sh", ".stdout", ".stderr")
TREE = "claude/et-soc1-prototyping"          # k6's rb_tree for aifoundry2 (E194's e194_common.TREE)
FWLEDGER = ".local/state/fwgate/aifoundry2-c0.jsonl"   # fwgate's attempt ledger for this card, named in its read record
SCRATCH = b"/tmp/claude-"                    # a session scratch root: never in the data
PATH_END = b" \t\r\n\"'`<>()[]{},;:=|$"      # what ends a path written in text (E194's)
HOLDER = re.compile(r"((?:/dev/et[\w]+|lock:[\w.-]+)\s+)([A-Za-z_][\w.-]*)(\s+\d+)")
TS = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\S+) ")
REF = {"ref/run_session.sh": "proposal/src/run_session.sh", "ref/stopwatch.py": "proposal/src/stopwatch.py",
       "ref/trains.tsv": "proposal/src/trains.tsv"}
RUNNER_SHA = "8774027b4bba78c6b532988c46446987f75eec6d32985bd7b400cbb963eb5a41"   # E200.md 4: E197's lab runner with W1
KEY = re.compile(r"GATE-STOP|HUNG|first card command|the firmware identity|the die gate|smoke|the clock|C3:|train blocks|the deadline|"
                 r"stop: |SITTING-RESULT|without a registered stop|configuration at the sitting|card time|session (start|end)|"
                 r"run_session.sh rc|refused|not free|the free check")


def box_tree_gate(copy, box_home):
    """THE BOX-TREE GATE (the module docstring, item 2): ([hits], files read). A hit names the file and the path written there."""
    home = box_home.encode()
    tree = os.path.normpath(box_home + "/" + TREE)
    ledger = os.path.normpath(box_home + "/" + FWLEDGER)
    hits, nread = [], 0
    for dp, _dn, fn in os.walk(copy):
        for n in sorted(fn):
            p = os.path.join(dp, n)
            if not (n.endswith(TEXT) or n.endswith(".gz") or "." not in n):
                continue
            try:
                body = open(p, "rb").read()
                if n.endswith(".gz"):
                    body = gzip.decompress(body)
            except (OSError, EOFError, gzip.BadGzipFile):
                hits.append(f"{os.path.relpath(p, copy)}: unreadable")
                continue
            nread += 1
            rel = os.path.relpath(p, copy)
            if SCRATCH in body:
                hits.append(f"{rel}: a session scratch root ({SCRATCH.decode()}...)")
            k = body.find(home)
            while k >= 0:
                j = k
                while j < len(body) and body[j:j + 1] not in PATH_END:
                    j += 1
                tok = body[k:j].decode("utf-8", "replace")
                after = body[k + len(home):k + len(home) + 1]
                if after in (b"",) or after in PATH_END:
                    pass                                             # the home itself, not a path under it
                else:
                    norm = os.path.normpath(tok)
                    inside = norm == tree or norm.startswith(tree + "/") or norm == ledger
                    if not inside or "/./" in tok or "//" in tok[1:] or "/../" in tok:
                        hits.append(f"{rel}: {tok[:120]}")
                k = body.find(home, j if j > k else k + 1)
    return hits, nread


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
            have.add(os.path.relpath(os.path.join(dp, n), copy))
    bad = [f"missing {p}" for p in want if p not in have]
    bad += [f"differs {p}" for p in want if p in have and sha(os.path.join(copy, p)) != want[p]]
    bad += [f"not in the manifest: {p}" for p in sorted(have - set(want) - {"MANIFEST.sha256", "wrapper.rc"})]
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


def tel_facts(raw):
    n = at800 = at600 = other = nomhz = 0
    bmax = dmax = lmax = None
    for ln in raw.decode(errors="ignore").splitlines():
        ln = ln.strip()
        if not (ln.startswith("{") and ln.endswith("}")):
            continue
        try:
            s = json.loads(ln)
        except ValueError:
            continue
        n += 1
        m = (s.get("mhz") or {}).get("minion") if isinstance(s.get("mhz"), dict) else None
        if isinstance(m, bool) or not isinstance(m, (int, float)):
            nomhz += 1
        elif abs(m - 800) <= 1:
            at800 += 1
        elif abs(m - 600) <= 1:
            at600 += 1
        else:
            other += 1
        w = s.get("board_w")
        if isinstance(w, (int, float)):
            bmax = w if bmax is None else max(bmax, w)
        try:
            d = float(s["temp_c"]["minshire"][0])
            dmax = d if dmax is None else max(dmax, d)
        except (KeyError, IndexError, TypeError, ValueError):
            pass
        try:
            d = float(s["temp_c"]["minshire"][2])
            lmax = d if lmax is None else max(lmax, d)
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    return {"samples": n, "samples_at_800_mhz": at800, "samples_at_600_mhz": at600, "samples_at_other_clocks": other,
            "samples_without_a_clock": nomhz, "board_w_peak": bmax, "die_c_peak": dmax, "latch_minshire2_c_peak": lmax}


def main(argv):
    if len(argv) < 6 or argv[2] != "--box-home" or "--sitting" not in argv:
        print(__doc__)
        return 2
    copy, data, box_home = os.path.abspath(argv[0]), argv[1], argv[3].rstrip("/")
    sit = argv[argv.index("--sitting") + 1]
    login = argv[argv.index("--login") + 1] if "--login" in argv else ""
    if sit not in ("1", "2"):
        print("COLLECT-REFUSED: --sitting is 1 or 2")
        return 2
    if not box_home.startswith("/") or len(box_home) < 6:
        print(f"COLLECT-REFUSED: the box's home path {box_home!r} is not an absolute path")
        return 2
    if os.path.exists(data):
        print(f"COLLECT-REFUSED: {data} exists: never merge into an earlier copy")
        return 2
    try:
        start = [ln for ln in open(os.path.join(copy, "session.log"), errors="replace") if "session start" in ln]
    except OSError:
        start = []
    if any("DESKTEST" in ln for ln in start) and not ("--allow-desktest" in argv and os.environ.get("RB_DESKTEST") == "1"):
        print("COLLECT-REFUSED: the session ran with the wrapper's desk-test variables (its start line names DESKTEST): never a card "
              "day's data; nothing written")
        return 3
    bad, want = copy_back_exact(copy)
    if bad:
        print("COPY-BACK NOT EXACT: " + "; ".join(bad[:10]))
        return 3
    print(f"COPY-BACK EXACT: every file of the box's MANIFEST.sha256 ({len(want)}) at its sha256, nothing else but wrapper.rc")
    hits, nread = box_tree_gate(copy, box_home)
    if hits:
        print(f"BOX-TREE GATE: a desk path in the session's files ({len(hits)}): " + "; ".join(hits[:10]) + ": nothing written")
        return 3
    print(f"BOX-TREE GATE: every path under the box's home in the {nread} text files read lies in its tree ~/{TREE}/ (or is fwgate's "
          f"ledger ~/{FWLEDGER}); no scratch root")
    reg = {}
    rl = os.path.join(HERE, os.pardir, "e197", "SHA256SUMS-e197-registration")
    for ln in open(rl):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            reg[p.replace("tools/claims-v3/e197/", "", 1)] = h
    out = {}
    for p in sorted(want) + [x for x in ("MANIFEST.sha256", "wrapper.rc") if os.path.exists(os.path.join(copy, x))]:
        top = p.split("/", 1)
        dst = p if (len(top) == 2 and top[0] in ("run", "ref")) else "session/" + p
        raw = open(os.path.join(copy, p), "rb").read()
        if dst == "run/telemetry.jsonl":
            out[dst + ".gz"] = ("gz", raw)
        else:
            out[dst] = ("plain", raw)
    for d, r in REF.items():
        if d in out and hashlib.sha256(out[d][1]).hexdigest() != reg.get(r):
            print(f"COLLECT-REFUSED: {d} is not E197's registered {r}")
            return 3
    if "ref/run_trains.py" in out and hashlib.sha256(out["ref/run_trains.py"][1]).hexdigest() != RUNNER_SHA:
        print("COLLECT-REFUSED: ref/run_trains.py is not E200's runner (E197's lab runner with W1, 8774027b...)")
        return 3
    left = []
    os.makedirs(data)
    for dst, (kind, raw) in sorted(out.items()):
        q = os.path.join(data, dst)
        os.makedirs(os.path.dirname(q), exist_ok=True)
        if dst in REF or dst == "ref/run_trains.py":
            body = raw
        else:
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
    lines = [ln.rstrip("\n") for ln in open(os.path.join(sess, "session.log"), errors="replace")]
    first = open(os.path.join(sess, "first-card-command.txt")).read().strip() if os.path.exists(
        os.path.join(sess, "first-card-command.txt")) else ""
    end = None
    for ln in lines:
        m = TS.match(ln)
        if m and "session end" in ln:
            end = epoch(m.group(1) + " " + m.group(2))
    plan = None
    for ln in lines:
        m = re.search(r"E200 sitting (\d), plan (full|short|ext)", ln)
        if m:
            plan = m.group(2)
            break
    runs = os.path.join(copy, "run", "runs.jsonl")
    marks = os.path.join(copy, "run", "marks.jsonl")
    nl = sum(1 for _ in open(runs)) if os.path.exists(runs) else 0
    tp = 0
    if os.path.exists(marks):
        for ln in open(marks):
            try:
                m = json.loads(ln)
            except ValueError:
                continue
            if m.get("kind") == "train" and m.get("block") in ("A", "B", "C", "D", "E"):
                tp += 1
    tel = os.path.join(copy, "run", "telemetry.jsonl")
    facts = {"schema": "e200-facts/1", "sitting": int(sit), "plan": plan,
             "first_card_command_epoch": int(first) if first.isdigit() else None,
             "card_minutes_first_command_to_session_end": round((end - int(first)) / 60.0, 2) if end and first.isdigit() else None,
             "session_lines": [ln for ln in lines if KEY.search(ln)],
             "wrapper_rc": open(os.path.join(sess, "wrapper.rc")).read().strip() if os.path.exists(os.path.join(sess, "wrapper.rc")) else None,
             "launch_records": nl, "train_processes_recorded": tp,
             "telemetry": tel_facts(open(tel, "rb").read()) if os.path.exists(tel) else None,
             "stop": open(os.path.join(copy, "run", "STOP"), errors="replace").read().strip()[:400] if os.path.exists(
                 os.path.join(copy, "run", "STOP")) else None}
    fj = os.path.join(data, f"facts-e200-{sit}.json")
    with open(fj, "w") as f:
        f.write(json.dumps(facts, indent=1, sort_keys=True) + "\n")
    body = scrub(open(fj, "rb").read(), box_home, login)
    with open(fj, "wb") as f:
        f.write(body)
    if box_home.encode() in body or b"/home/" in body or (login and re.search(
            rb"(?<![\w.-])" + re.escape(login.encode()) + rb"(?![\w-])", body)):
        print("SCRUB FAILED: facts-e200 holds the box's home, a /home/ path or the login")
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
    print(f"COLLECTED {rel}: sitting {sit} (plan {plan}); {len(rows)} files in SHA256SUMS; the scrub clean (no /home/ path, no login); "
          f"card-minutes {facts['card_minutes_first_command_to_session_end']}; wrapper rc {facts['wrapper_rc']}; "
          f"{nl} launch records, {tp} train processes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
