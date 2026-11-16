#!/usr/bin/env python3
"""E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum; E192's collector, a6fe5c20, unchanged beside it, ported to aifoundry1 card 1): the collection's desk half, run by step 11
(rb/s22_collect_e199.sh) after the one read-only copy back of the session's files. Standard library only; nothing on the box is touched.

    collect_e199.py copycheck <box-manifest.txt> <raw dir> <T0>
        THE EXACT COPY-BACK: every file the box listed ("SUM <sha256> <path>", paths from the box's tree) is in <raw dir> at the same path
        and sha256, and nothing else is there; and the session's own MANIFEST.sha256 (written last by session_e199.sh) holds for every
        file it lists. Prints COPY EXACT: ... or COPY NOT EXACT: ... (exit 0 or 16).
    collect_e199.py assemble <raw dir> <T0> <day> <out parent> [--owner LOGIN]
        THE DATA DIRECTORY <out parent>/<day>-e199-intbits-aifoundry1-c1/: run/ (the reference session's own files, telemetry.jsonl gzipped
        with no name or time in its header, so the same bytes give the same file), session/ (the wrapper's log and records, the box's
        MANIFEST.sha256 and wrapper.rc), build/ (the day's build record, logs and attempts), box-manifest.txt, facts-e199.json (T0, the
        sampler, passes complete, the STOP, the card time, the exit), SHA256SUMS (every file but itself). Exit 0, or 16 on a missing input.
    collect_e199.py scrubcheck <dir> [--owner LOGIN]
        THE HOLDER-LINE CHECK: the reference session writes other accounts into its log only in its holder lines ("held: <node> <login>
        <pid> ..." from et-who, "another user's device process: <uid>:<pid>:<comm>" from ps), forms E178's scrub does not know. Any such
        line naming an account other than --owner is listed and the step stops (16) until it is rewritten by hand (and named in the data
        README); /home/<name> paths of another name likewise. Prints SCRUB-CHECK OK or SCRUB-CHECK LEFT.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import re
import shutil
import sys


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
    sd = os.path.join(raw, "build/e199/T%s" % t0)
    mf = os.path.join(sd, "MANIFEST.sha256")
    mbad, mn = [], 0
    if os.path.exists(mf):
        for ln in open(mf):
            h, p = ln.rstrip("\n").split("  ", 1)
            mn += 1
            q = os.path.join(sd, p)
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


def gz(src, dst):
    with open(src, "rb") as f, open(dst, "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as g:
            shutil.copyfileobj(f, g)


def mask_login(out, login):
    """Our own box login, masked in every text file of the data directory (the round's rule: our own login is masked in every copy we
    keep): '/home/<login>' and the login as a whole word become '<box-login>'. The reference session's records (run/runs.jsonl,
    run/marks.jsonl, run/telemetry.jsonl.gz) are left byte for byte (they carry no login; step 13 checks them against the box's
    manifest). Returns {file: lines changed}."""
    changed = {}
    if not login:
        return changed
    rx = re.compile(r"(?<![A-Za-z0-9_.-])%s(?![A-Za-z0-9_-])" % re.escape(login))
    for root, _, fs in os.walk(out):
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, out)
            if fn.endswith((".gz", ".bin", ".elf")) or rel in ("run/runs.jsonl", "run/marks.jsonl"):
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


def first_match(pats, text):
    """The first group of the first pattern that matches the text, or None (E199's identity lines in the wrapper's log)."""
    for pat in pats:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    return None


def assemble(raw, t0, day, parent, owner=None):
    sd = os.path.join(raw, "build/e199/T%s" % t0)
    if not os.path.isdir(sd):
        print("ASSEMBLE FAILED: no session directory build/e199/T%s in the copy" % t0)
        return 16
    out = os.path.join(parent, "%s-e199-intbits-aifoundry1-c1" % day)
    if os.path.exists(out):
        print("ASSEMBLE FAILED: %s exists (a data directory is written once)" % out)
        return 16
    os.makedirs(os.path.join(out, "run"))
    os.makedirs(os.path.join(out, "session"))
    os.makedirs(os.path.join(out, "build"))
    for root, _, fs in os.walk(sd):
        for fn in fs:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, sd)
            if rel.startswith("run" + os.sep):
                dst = os.path.join(out, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if fn == "telemetry.jsonl":
                    gz(src, dst + ".gz")
                else:
                    shutil.copy2(src, dst)
            else:
                dst = os.path.join(out, "session", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
    br = os.path.join(raw, "build/claims-v3/aifoundry1-c1/e199")
    for root, _, fs in os.walk(br):
        for fn in fs:
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, br)
            dst = os.path.join(out, "build", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    shutil.copy2(os.path.join(raw, "..", "box-manifest.txt") if os.path.exists(os.path.join(raw, "..", "box-manifest.txt"))
                 else os.path.join(raw, "box-manifest.txt"), os.path.join(out, "box-manifest.txt"))
    log = open(os.path.join(sd, "session.log"), errors="replace").read()
    marks = []
    for ln in open(os.path.join(sd, "run", "marks.jsonl"), errors="replace") if os.path.exists(os.path.join(sd, "run", "marks.jsonl")) else []:
        try:
            marks.append(json.loads(ln))
        except ValueError:
            pass
    stop = None
    if os.path.exists(os.path.join(sd, "run", "STOP")):
        try:
            stop = json.loads(open(os.path.join(sd, "run", "STOP")).read().strip())
        except ValueError:
            stop = open(os.path.join(sd, "run", "STOP")).read().strip()[:300]
    m = re.search(r"sampler: (\w+) \(([^\n]*)\)", log)
    c = re.search(r"card time (\d+) s from the first card command", log)
    facts = {"T0": int(t0), "day": day, "card": "aifoundry1 card 1", "sampler": m.group(1) if m else None, "sampler_why": m.group(2) if m else None,
             "passes_complete": sum(1 for x in marks if x.get("kind") == "idle" and x.get("label") == "after" and x.get("pass", -1) >= 0),
             "launches_recorded": sum(1 for _ in open(os.path.join(sd, "run", "runs.jsonl"))) if os.path.exists(os.path.join(sd, "run", "runs.jsonl")) else 0,
             "stop": stop, "card_time_s": int(c.group(1)) if c else None,
             "wrapper_rc": open(os.path.join(sd, "wrapper.rc")).read().strip() if os.path.exists(os.path.join(sd, "wrapper.rc")) else None,
             "session_end_line": bool(re.search(r"session end \(T0 %s\)" % t0, log)),
             "telemetry_gzip": "run/telemetry.jsonl.gz (gzip, no name, mtime 0); its uncompressed bytes are session/MANIFEST.sha256's run/telemetry.jsonl",
             "identity_a": first_match((r"identity \(a\): ([^\n]*)", r"THE IDENTITY GATE \(a\) FAILED: ([^\n]*)"), log),
             "identity_b": [json.loads(x) for x in open(os.path.join(sd, "run", "gate.jsonl"), errors="replace") if '"identity_b"' in x]
                           if os.path.exists(os.path.join(sd, "run", "gate.jsonl")) else [],
             "end_config_read": first_match((r"the end config read: ([^\n]*)",), log)}
    masked = mask_login(out, owner)
    facts["login_masked"] = {"lines": sum(masked.values()), "files": sorted(masked)}
    with open(os.path.join(out, "facts-e199.json"), "w") as f:
        json.dump(facts, f, indent=1)
    rows = []
    for root, _, fs in os.walk(out):
        for fn in fs:
            p = os.path.relpath(os.path.join(root, fn), out)
            if p != "SHA256SUMS":
                rows.append("%s  %s" % (sha(os.path.join(out, p)), p))
    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(rows, key=lambda x: x.split("  ", 1)[1])) + "\n")
    print("ASSEMBLED %s: %d files; sampler %s; passes complete %s; card time %s s; stop %s" % (
        os.path.basename(out), len(rows) + 1, facts["sampler"], facts["passes_complete"], facts["card_time_s"],
        (stop or {}).get("by") if isinstance(stop, dict) else stop))
    return 0


def scrubcheck(d, owner):
    left = []
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
                m = re.search(r"held: (.*)$", ln)
                if m:   # run_session.sh: et-who's holder lines joined by ';' (node, login, pid, command)
                    for ent in m.group(1).split(";"):
                        w = ent.split()
                        if len(w) >= 2 and w[1] != owner and not w[1].startswith("<another-"):
                            left.append("%s: a holder line naming another account" % rel)
                            break
                m = re.search(r"another user's device process: (.*)$", ln)
                if m and re.search(r"\d+:\d+:\S+", m.group(1)):   # run_session.sh: ps entries uid:pid:comm of another user
                    left.append("%s: another user's process entry (uid:pid:comm)" % rel)
                for hm in re.finditer(r"/home/([A-Za-z0-9_.-]+)", ln):
                    if hm.group(1) != owner:
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
