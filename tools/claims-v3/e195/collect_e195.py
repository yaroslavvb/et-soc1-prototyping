#!/usr/bin/env python3
"""E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the collection's desk half, run by step 11
(rb/s22_collect_e195.sh) after the one read-only copy back of the session's files. E192's collect_e192.py's form. Standard library only;
nothing on the box is touched.

    collect_e195.py copycheck <box-manifest.txt> <raw tree> <T0>
        THE EXACT COPY-BACK: every file the box listed ("SUM <sha256> <path>", paths from the box's tree) is in <raw tree> at the same path
        and sha256, and nothing else is there; and the session's own MANIFEST.sha256 (written last by session_e195.sh: every file of its
        session directory and of its data folder, paths from the box's tree) holds for every file it lists. Prints COPY EXACT: ... or COPY
        NOT EXACT: ... (exit 0 or 16).
    collect_e195.py assemble <raw tree> <T0> <day> <out parent> [--owner LOGIN]
        THE DATA DIRECTORY <out parent>/<day>-e195-x09-dramtoggle-aifoundry3/ when the session ran a pass or its smoke past its gates; or,
        for a session that ended at a gate (a refusal or a GATE-STOP before any pass: E195.md 12's "no session" or "no pass that day: no
        data"), ITS GATE STOP'S RECORD <out parent>/gate-stops/<day>-e195-x09-dramtoggle-T<T0>-aifoundry3/ (the card lane commits it under
        docs/reports/gate-stops/, never under docs/reports/data/, so step 2's no-datum check never meets it: E193's fix). Either holds:
        session/ (the session's log and records, MANIFEST.sha256 and session.rc), passes/p<pass>/ (each block's files as the box wrote them:
        runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, configs.json, block.json, code.sha256, text.sha256, gen.sha256, manifest.txt,
        any STOP or SAMPLER-STUCK), build/ (the day's build record, its check_elf, loops, arm table and generator check, the build
        attempts and logs), launch.out, box-manifest.txt, facts-e195.json and SHA256SUMS (every file but itself). OUR OWN BOX LOGIN masked
        as <box-login> in every text file but the records the reducer reads (runs.jsonl, marks.jsonl, telemetry.jsonl.gz: kept byte for
        byte; step 13 checks them against the box's manifest). Exit 0, or 16 on a missing input.
    collect_e195.py scrubcheck <dir> [--owner LOGIN]
        THE HOLDER-LINE CHECK: the session's chain writes other accounts only in holder lines (lib_x09.sh's "others present: procs=[<uid>:
        <pid>:<comm>] holders=[<user>:<pid>]", runitems' "another user on this card: <user>:<pid>", et-who's "<node> <user> <pid> ..."
        lines in etwho-*.txt), forms E178's scrub does not know. Any such line naming an account other than --owner (or <box-login>) is
        listed and the step stops (16) until it is rewritten by hand (and named in the data README); /home/<name> paths of another name
        likewise. Prints SCRUB-CHECK OK or SCRUB-CHECK LEFT.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import sys

KEEP_BYTES = ("runs.jsonl", "marks.jsonl")
NAME = "e195-x09-dramtoggle-aifoundry3"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def copycheck(manifest, raw, t0):
    listed = {}
    for ln in open(manifest):
        if ln.startswith("SUM "):
            _, h, p = ln.rstrip("\n").split(" ", 2)
            listed[os.path.normpath(p)] = h
    have = set()
    for root, _, fs in os.walk(raw):
        for fn in fs:
            have.add(os.path.normpath(os.path.relpath(os.path.join(root, fn), raw)))
    missing = [p for p in listed if p not in have]
    diff = [p for p in listed if p in have and sha(os.path.join(raw, p)) != listed[p]]
    extra = sorted(have - set(listed))
    mf = os.path.join(raw, "build/e195/T%s" % t0, "MANIFEST.sha256")
    mbad, mn = [], 0
    if os.path.exists(mf):
        for ln in open(mf):
            h, p = ln.rstrip("\n").split("  ", 1)
            mn += 1
            q = os.path.join(raw, p)
            if not os.path.exists(q) or sha(q) != h:
                mbad.append(p)
    else:
        mbad.append("no MANIFEST.sha256")
    if missing or diff or extra or mbad or not listed:
        print("COPY NOT EXACT: %d listed, missing %s, different %s, not listed %s; the session's manifest: %s" % (
            len(listed), missing[:3], diff[:3], extra[:3], mbad[:3]))
        return 16
    print("COPY EXACT: %d files at the box's sha256, nothing else; the session's own MANIFEST.sha256 holds for its %d files" % (len(listed), mn))
    return 0


def mask_login(out, login):
    """Our own box login masked in every text file but the reducer's records: '/home/<login>' and the login as a whole word become
    '<box-login>'. Returns {file: lines changed}."""
    changed = {}
    if not login:
        return changed
    rx = re.compile(r"(?<![A-Za-z0-9_.-])%s(?![A-Za-z0-9_-])" % re.escape(login))
    for root, _, fs in os.walk(out):
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, out)
            if fn.endswith((".gz", ".bin", ".elf")) or fn in KEEP_BYTES:
                continue
            try:
                text = open(p, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            n = 0
            lines = text.split("\n")
            for i, ln in enumerate(lines):
                new = rx.sub("<box-login>", ln)
                if new != ln:
                    lines[i] = new
                    n += 1
            if n:
                with open(p, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                changed[rel] = n
    return changed


def copytree_into(src, dst):
    n = 0
    for root, _, fs in os.walk(src):
        for fn in fs:
            s = os.path.join(root, fn)
            d = os.path.join(dst, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            n += 1
    return n


def peak(d):
    p = os.path.join(d, "telemetry.jsonl.gz")
    bw, dc = [], []
    if os.path.exists(p):
        with gzip.open(p, "rt", errors="replace") as f:
            for ln in f:
                if not ln.startswith("{"):
                    continue
                try:
                    s = json.loads(ln)
                    bw.append(float(s["board_w"]))
                    dc.append(float(s["temp_c"]["minshire"][0]))
                except (ValueError, KeyError, IndexError, TypeError):
                    pass
    return (max(bw) if bw else None), (max(dc) if dc else None), len(bw)


def assemble(raw, t0, day, parent, owner=None):
    sd = os.path.join(raw, "build/e195/T%s" % t0)
    if not os.path.isdir(sd):
        print("ASSEMBLE FAILED: no session directory build/e195/T%s in the copy" % t0)
        return 16
    log = open(os.path.join(sd, "session.log"), errors="replace").read()
    rc = open(os.path.join(sd, "session.rc")).read().strip() if os.path.exists(os.path.join(sd, "session.rc")) else None
    root = os.path.join(raw, "build/claims-v3/aifoundry3/e195")
    data = os.path.join(root, "build/claims-v3/aifoundry3", "x09-T%s" % t0)
    passes = sorted(p for p in (os.listdir(data) if os.path.isdir(data) else []) if re.fullmatch(r"p\d+(\.attempt-\d+)?", p))
    gated = (rc in ("3", "8")) and not any(re.fullmatch(r"p91\d", p) for p in passes)
    out = os.path.join(parent, "gate-stops", "%s-e195-x09-dramtoggle-T%s-aifoundry3" % (day, t0)) if gated else os.path.join(parent, "%s-%s" % (day, NAME))
    if os.path.exists(out):
        print("ASSEMBLE FAILED: %s exists (a data directory is written once)" % out)
        return 16
    os.makedirs(out)
    copytree_into(sd, os.path.join(out, "session"))
    for p in passes:
        copytree_into(os.path.join(data, p), os.path.join(out, "passes", p))
    for rel in ("build/x09mem-built.txt", "build/x09mem/check_elf.txt", "build/x09mem/loops.txt", "build/x09mem/arm-table.json",
                "build/x09mem/arm-table.txt", "build/x09mem/make-check.txt", "build-attempts.txt"):
        s = os.path.join(root, rel)
        if os.path.exists(s):
            d = os.path.join(out, "build", rel.replace("build/", "", 1) if rel.startswith("build/") else rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    bl = os.path.join(root, "build-logs")
    if os.path.isdir(bl):
        copytree_into(bl, os.path.join(out, "build", "build-logs"))
    lo = os.path.join(raw, "build/e195/launch-T%s.out" % t0)
    if os.path.exists(lo):
        shutil.copy2(lo, os.path.join(out, "launch.out"))
    bm = os.path.join(os.path.dirname(os.path.normpath(raw)), "box-manifest.txt")
    shutil.copy2(bm if os.path.exists(bm) else os.path.join(raw, "box-manifest.txt"), os.path.join(out, "box-manifest.txt"))
    ok_passes = [p for p in passes if os.path.exists(os.path.join(data, p, "block.json")) and
                 '"status":"ok"' in open(os.path.join(data, p, "block.json"), errors="replace").read()]
    pk = {p: dict(zip(("board_w", "die_c", "samples"), peak(os.path.join(data, p)))) for p in passes}
    first = open(os.path.join(sd, "first-card-command.txt")).read().strip() if os.path.exists(os.path.join(sd, "first-card-command.txt")) else None
    end = re.search(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \S+) session end \(T0 %s\)" % t0, log, re.M)
    dropped = 0
    for p in passes:
        dropped += len(re.findall(r"runtime line\(s\) dropped", open(os.path.join(data, p, "run.log"), errors="replace").read())) \
            if os.path.exists(os.path.join(data, p, "run.log")) else 0
    import subprocess
    end_epoch = None
    if end:
        r = subprocess.run(["date", "-d", end.group(1), "+%s"], capture_output=True, text=True)
        end_epoch = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else None
    facts = {"T0": int(t0), "day": day, "card": "aifoundry3 card 0", "session_rc": rc, "kind": "gate stop's record" if gated else "data",
             "passes": passes, "passes_block_ok": ok_passes,
             "main_passes_for_the_reducer": [p for p in ok_passes if re.fullmatch(r"p91[0-7]", p)],
             "first_card_command_epoch": int(first) if first and first.isdigit() else None, "session_end": end.group(1) if end else None,
             "card_minutes_first_command_to_session_end": round((end_epoch - int(first)) / 60.0, 2) if end_epoch and first and first.isdigit() else None,
             "queue_end": (re.findall(r"queue end: (.*)", log) or [None])[-1],
             "gate_stop": (re.findall(r"GATE-STOP: (.*)", log) or re.findall(r"refused, no device opened: (.*)", log) or [None])[0],
             "smoke_gate": (re.findall(r"(smoke gate (?:PASS|FAIL).*)", log) or [None])[0],
             "smoke_peak_gate": (re.findall(r"(SMOKE-PEAK (?:PASS|FAIL).*)", log) or [None])[0],
             "start_config": (re.findall(r"start config read: (.*)", log) or [None])[0],
             "closing_config": (re.findall(r"closing config read: (.*)", log) or [None])[0],
             "peaks": pk, "runtime_lines_dropped_runs": dropped,
             "sampler_stuck": sorted(p for p in passes if os.path.exists(os.path.join(data, p, "SAMPLER-STUCK"))),
             "stop_files": sorted(f for f in os.listdir(sd) if f.startswith("stopfile-")),
             "interpreter_on_the_box": (re.findall(r"(Python \d+\.\d+\.\d+)", log) or [None])[0],
             "telemetry": "passes/<p>/telemetry.jsonl.gz as the block wrote it (its gzip header carries the block's own name and time); "
                          "the session's MANIFEST.sha256 names its sha256"}
    masked = mask_login(out, owner)
    facts["login_masked"] = {"lines": sum(masked.values()), "files": sorted(masked)}
    with open(os.path.join(out, "facts-e195.json"), "w") as f:
        json.dump(facts, f, indent=1)
    rows = []
    for r_, _, fs in os.walk(out):
        for fn in fs:
            p = os.path.relpath(os.path.join(r_, fn), out)
            if p != "SHA256SUMS":
                rows.append("%s  %s" % (sha(os.path.join(out, p)), p))
    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x.split("  ", 1)[1])) + "\n")
    print("ASSEMBLED %s%s: %d files; session.rc %s; passes %s (block ok: %s); card-minutes %s; %s" % (
        "gate-stops/" if gated else "", os.path.basename(out), len(rows) + 1, rc, ",".join(passes) or "none", ",".join(ok_passes) or "none",
        facts["card_minutes_first_command_to_session_end"], facts["queue_end"] or facts["gate_stop"]))
    return 0


def scrubcheck(d, owner):
    left = []
    ok_names = {owner, "<box-login>", None, ""}
    for root, _, fs in os.walk(d):
        for fn in fs:
            p = os.path.join(root, fn)
            if fn.endswith((".gz", ".bin")):
                continue
            try:
                text = open(p, errors="replace").read()
            except OSError:
                continue
            for i, ln in enumerate(text.splitlines(), 1):
                rel = "%s:%d" % (os.path.relpath(p, d), i)
                m = re.search(r"holders=\[([^\]]*)\]", ln)
                if m:
                    for ent in m.group(1).split():
                        if ent.split(":")[0] not in ok_names and not ent.startswith("<another-"):
                            left.append("%s: a holder entry naming another account" % rel)
                            break
                m = re.search(r"procs=\[([^\]]*)\]", ln)
                if m and re.search(r"\d+:\d+:\S+", m.group(1)):
                    left.append("%s: another user's process entry (uid:pid:comm)" % rel)
                m = re.search(r"another user on this card: (\S+)", ln)
                if m and m.group(1).split(":")[0].rstrip(",") not in ok_names and not m.group(1).startswith("<another-"):
                    left.append("%s: runitems' holder line naming another account" % rel)
                w = ln.split()
                if len(w) >= 2 and (w[0].startswith("/dev/et") or w[0].startswith("lock:etsoc")) and w[1] not in ok_names and not w[1].startswith("<another-"):
                    left.append("%s: an et-who holder line naming another account" % rel)
                for hm in re.finditer(r"/home/([A-Za-z0-9_.-]+)", ln):
                    if hm.group(1) not in ok_names:
                        left.append("%s: a /home path of another name" % rel)
    if left:
        print("SCRUB-CHECK LEFT: %d line(s) name another account:" % len(left))
        for x in left[:10]:
            print("  " + x)
        return 16
    print("SCRUB-CHECK OK: no holder line, process entry or /home path names another account")
    return 0


def main(argv):
    if len(argv) >= 4 and argv[0] == "copycheck":
        return copycheck(argv[1], argv[2], argv[3])
    if len(argv) >= 5 and argv[0] == "assemble":
        return assemble(argv[1], argv[2], argv[3], argv[4], argv[argv.index("--owner") + 1] if "--owner" in argv else None)
    if len(argv) >= 2 and argv[0] == "scrubcheck":
        own = argv[argv.index("--owner") + 1] if "--owner" in argv else None
        return scrubcheck(argv[1], own)
    print(__doc__)
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
