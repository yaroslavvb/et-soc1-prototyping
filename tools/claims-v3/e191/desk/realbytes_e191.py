#!/usr/bin/env python3
"""E191's REAL-BYTES desk test (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026,
20:34:12 PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum; CONTEXT section 116's
lesson: "its real-path desk test feeds the parser the REAL stdout bytes committed from a card, not only stand-in JSON"). The reader of
kit note 2 (e191_common_v2.host_result, config_json, drop_runtime) and v1's (e191_common.last_json), fed the bytes the lab committed:

  RB1  THE DAY'S BYTES: 1a4bc1e3's session/smoke/copy-64m-random/stdout.txt (its sha256 the data's SHA256SUMS line) with that run's own
       command line (its smoke.json argv): v2 reads the host's PASS line, 2,048 of 2,048 records, 0 bad, 0 mismatches, 1 launch, one
       runtime line dropped ("Opening device 1"), and the smoke's own test (rc 0 and status PASS) reads good; v1 reads {} there (status
       None): the defect reproduced, the negative control;
  RB2  the reassembled line through the unchanged adapter (status PASS, reps_consistent ok, the reading PASS), the frozen scorer's reader
       and the unchanged reducer's reader on host-raw.json as runner v2 writes it (the same dict);
  RB3  the runtime line at EVERY byte offset of the day's line (and of each of E189's six committed ledger smoke lines): each reads the
       same dict; v1's misreads counted for the record;
  RB4  two runtime lines at once (offset pairs), and "Opening device 0": reassembled, every dropped line recorded;
  RB5  the runtime line on its own line before the line (ettelem's form, aifoundry1 card 0's committed config read) and after it: read;
  RB6  A TRULY FAILED HOST still reads FAILED: the day's bytes with a mismatch and status FAIL (status FAIL; the adapter's FAILED RUN; the
       smoke's test not good); the head and the runtime line with no tail (the host died after it opened the card); nothing; the head alone
       (it died before); v1's cut line; an unknown text inside the line where the runtime line was; the line of another command (width
       64); a line with a field missing; a span end missing; the host's REFUSED line: none reads PASS, none is a wrong datum;
  RB7  E189's committed real bytes (aifoundry3 card 0, the clean form): its eight smoke stdout.txt files, its twenty ledger passes'
       host-raw.json and its four sparse parity passes' host.json, each with its own command line (smoke.json argv; run.json host_args):
       v2 reads each exactly as v1 read it (the same dict, the same status): no reading E189's data had changes;
  RB8  sparse parity in aifoundry1's form: E189's committed sparse parity lines with the runtime line before them (its host prints its
       line at the end) and at every 50th byte inside: the same dict;
  RB9  the self-test's committed lines (E191's and E189's ledger-selftest stdout.txt): "SELFTEST PASS" read once the runtime lines drop;
  RB10 every committed occurrence of "Opening device" in a raw text file under docs/reports/data AS COMMITTED AT fe08ed67 (GitHub main
       when this note was written: the lab's whole record of the runtime's line then, read from git's blobs, so a later record, such as
       the second session's raw stdout.txt files or a later kit's, cannot change this reading; added before the land, after the note's
       verifier, finding 5): each is the exact text RUNTIME_LINE drops ("Opening device <n>" and its newline), or a record quoting it
       inside a JSON string (an escaped newline, never on a host's stdout); none of another form; exactly one inside a host's line (the
       day's, in 1a4bc1e3's record).
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/realbytes_e191.py        (from the top of the tree; REALBYTES-E191 <n> of <m> PASS)
A desk check of code on committed records: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e191_common as V1  # noqa: E402
import e191_common_v2 as C  # noqa: E402

D191 = os.path.join(REPO, "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1")
D189 = os.path.join(REPO, "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3")
RB10_AT = "fe08ed6705b36d2a4efbbdfd6b1d4e5ada18443b"     # RB10 reads the lab's records as committed here (GitHub main when note 2 was written)
RT = "Opening device 1\n"
res = []


def case(name, good, detail):
    res.append(bool(good))
    print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)


def load(path, modname):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def raw(p):
    with open(p, "rb") as f:
        return f.read()


def main():
    print(f"realbytes_e191 ({sys.executable} {sys.version.split()[0]}): the readers fed the lab's committed bytes")
    # ---- RB1: the day's bytes
    so = os.path.join(D191, "session/smoke/copy-64m-random/stdout.txt")
    sm = json.load(open(os.path.join(D191, "session/smoke/copy-64m-random/smoke.json")))
    b = raw(so)
    sums = {ln.split("  ", 1)[1].strip(): ln.split()[0] for ln in open(os.path.join(D191, "SHA256SUMS")) if ln.strip()}
    h = hashlib.sha256(b).hexdigest()
    text = b.decode()
    argv = sm["argv"]
    j, rec = C.host_result(text, "ledger", argv)
    v1 = V1.last_json(text)
    good = sm["rc"] == 0 and j.get("status") == "PASS"
    case("RB1", h == sums.get("session/smoke/copy-64m-random/stdout.txt") and text.count("\n") == 2 and "32Opening device 1\n,\"launches\"" in text
         and j.get("status") == "PASS" and j.get("records_ok") == 2048 and j.get("participants") == 2048 and j.get("records_bad") == 0
         and j.get("mismatches") == 0 and j.get("launches") == 1 and rec["runtime_lines"] == ["Opening device 1"] and not rec["why"]
         and good and v1 == {} and v1.get("status") is None and sm["status"] is None and sm["good"] is False,
         f"the committed bytes (sha256 {h[:16]}..., {len(b)} bytes, its SHA256SUMS line {'matches' if h == sums.get('session/smoke/copy-64m-random/stdout.txt') else 'DIFFERS'}): "
         f"v2 reads status {j.get('status')}, records {j.get('records_ok')} of {j.get('participants')} ok, {j.get('records_bad')} bad, "
         f"{j.get('mismatches')} mismatches, {j.get('launches')} launch, dropped {rec['runtime_lines']}, the smoke's test good {good}; "
         f"v1 reads {v1} (status {v1.get('status')}), as the day's smoke.json recorded (status {sm['status']}, good {sm['good']})")
    whole = json.dumps(j, separators=(",", ":"))
    # ---- RB2: the adapter, the scorer's reader and the reducer's reader
    ad = V1.adapt_ledger(j, 1)
    scorer = load(os.path.join(E, "score_e191.py"), "score_e191_rb")
    reducer = load(os.path.join(REPO, "workloads/sparseparity/tools/energy_reduce.py"), "energy_reduce_rb")
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"realbytes-e191-{os.getpid()}")
    os.makedirs(tmp, exist_ok=True)
    hr = os.path.join(tmp, "host-raw.json")
    with open(hr, "w") as f:
        f.write(json.dumps(j) + "\n")                     # as runner v2 writes host-raw.json (v1's form: json.dumps of the line)
    sj = scorer.last_json(hr)
    rj = reducer.last_json(hr) if hasattr(reducer, "last_json") else None
    case("RB2", ad["status"] == "PASS" and ad["reps_consistent"] == "ok" and ad["reps_done"] == 1 and ad["problems"] == []
         and V1.reading("copy-random", ad) == "PASS" and sj == j and rj == j,
         f"the adapter: status {ad['status']}, reps_consistent {ad['reps_consistent']}, reps_done {ad['reps_done']}, the reading "
         f"{V1.reading('copy-random', ad)!r}; the frozen scorer's reader and the reducer's reader on host-raw.json: the same dict "
         f"{sj == j} / {rj == j}")
    os.remove(hr)
    os.rmdir(tmp)
    # ---- RB3: every offset, the day's line and E189's six ledger smoke lines
    lines = [("E191 copy-64m-random (reassembled)", whole, argv)]
    for n in ("copy-64m-random", "copy-64m-zeros", "copy-1g-random", "sha256-b2048-r1", "sort-shuffled-r1", "sort-sorted-r1"):
        t = open(os.path.join(D189, "session/smoke", n, "stdout.txt")).read().rstrip("\n")
        lines.append((f"E189 {n}", t, json.load(open(os.path.join(D189, "session/smoke", n, "smoke.json")))["argv"]))
    tot = bad = v1bad = 0
    for name, ln, av in lines:
        want = json.loads(ln)
        for k in range(len(ln) + 1):
            s = ln[:k] + RT + ln[k:] + "\n"
            jj, rr = C.host_result(s, "ledger", av)
            tot += 1
            if jj != want or rr["runtime_lines"] != ["Opening device 1"]:
                bad += 1
            if V1.last_json(s) != want:
                v1bad += 1
    case("RB3", bad == 0 and tot > 3000, f"{tot} split forms over {len(lines)} committed lines (the runtime line at every byte offset): v2 read "
         f"{tot - bad} of {tot} as the whole line; v1 misread {v1bad} of {tot} (every offset but 0)")
    # ---- RB4: two runtime lines; device 0
    want = json.loads(whole)
    pairs = [(a, c) for a in range(0, len(whole) + 1, 37) for c in range(a, len(whole) + 1, 53)]
    okp = 0
    for a, c in pairs:
        s = whole[:a] + RT + whole[a:c] + "Opening device 0\n" + whole[c:] + "\n"
        jj, rr = C.host_result(s, "ledger", argv)
        okp += jj == want and rr["runtime_lines"] == ["Opening device 1", "Opening device 0"]
    case("RB4", okp == len(pairs) and len(pairs) > 50, f"{okp} of {len(pairs)} forms with two runtime lines (device 1 and device 0) read as the "
         "whole line, both dropped lines recorded in order")
    # ---- RB5: the runtime line on its own line before and after; the committed config read with it (aifoundry1 card 0)
    jb, rb_ = C.host_result(RT + whole + "\n", "ledger", argv)
    ja, ra = C.host_result(whole + "\n" + RT, "ledger", argv)
    cfgp = os.path.join(REPO, "docs/reports/data/2026-11-04-e170-blind7-card0/aifoundry1-c0/config-start.txt")
    ct = raw(cfgp).decode()
    cj = C.config_json(ct)
    case("RB5", jb == want and ja == want and ct.startswith("Opening device 0\n") and cj == V1.last_json(ct) and cj.get("tdp_w") == 65,
         f"before: read {jb == want}, after: read {ja == want}; E170's committed config read on aifoundry1 card 0 ('Opening device 0' then its "
         f"line): config_json {cj} equals v1's reading {cj == V1.last_json(ct)}")
    # ---- RB6: truly failed hosts
    head, tail = text.split("Opening device 1\n")
    tail = tail.rstrip("\n")
    failed = head + RT + tail.replace('"mismatches":0,', '"mismatches":1,').replace('"first_mismatch":""', '"first_mismatch":"participant 7"').replace('"status":"PASS"', '"status":"FAIL"') + "\n"
    jf, rf = C.host_result(failed, "ledger", argv)
    adf = V1.adapt_ledger(jf, 1)
    goodf = 0 == 0 and jf.get("status") == "PASS"
    forms = {"the head and the runtime line, no tail (died after it opened the card)": head + RT,
             "nothing on stdout": "",
             "the head alone (died before it opened the card)": head,
             "v1's cut line (a timeout mid-line)": head + RT + '{"ledger":1,"prog":"cut\n',
             "an unknown text inside the line": head + "Warning: card busy\n" + tail + "\n",
             "the line of another command (width 64)": head.replace('"width":32', '"width":64') + RT + tail + "\n",
             "a field missing (records_ok)": head + RT + tail.replace('"records_ok":2048,', "") + "\n",
             "a span end missing": head + RT + re.sub(r'"launch_epoch_ms":\[(\d+),\d+\]', r'"launch_epoch_ms":[\1]', tail) + "\n"}
    reads = {k: C.host_result(v, "ledger", argv) for k, v in forms.items()}
    refused = head + ',"status":"REFUSED","why":"model 9.000 s over --max-kernel-s 8.000"}\n'
    jr, rr2 = C.host_result(refused, "ledger", argv)
    adr = V1.adapt_ledger(jr, 1)
    case("RB6", jf.get("status") == "FAIL" and jf.get("mismatches") == 1 and adf["reps_consistent"] == "bad" and V1.reading("x", adf).startswith("FAILED RUN")
         and not goodf and all(jj == {} and rr["why"] for jj, rr in reads.values())
         and jr.get("status") == "REFUSED" and V1.reading("x", adr).startswith("FAILED RUN"),
         f"a failed host: status {jf.get('status')}, the adapter's reading {V1.reading('x', adf)!r}, the smoke's test good {goodf}; not read: "
         + "; ".join(f"{k} ({rr['why'][:70]})" for k, (jj, rr) in reads.items()) + f"; the REFUSED line: status {jr.get('status')}, "
         f"the reading {V1.reading('x', adr)!r}")
    # ---- RB7: E189's committed real bytes, the clean form: v2 reads each as v1 did
    count_rb7 = same_rb7 = 0
    diffs = []
    for p in sorted(glob.glob(os.path.join(D189, "session/smoke/*/stdout.txt"))):
        name = os.path.basename(os.path.dirname(p))
        if name == "ledger-selftest":
            continue
        smj = json.load(open(os.path.join(os.path.dirname(p), "smoke.json")))
        t = open(p).read()
        kind = "spp" if name.startswith("sparse") else "ledger"
        jj, rr = C.host_result(t, kind, smj["argv"])
        count_rb7 += 1
        if jj == V1.last_json(t) and jj and jj.get("status") == smj.get("status") and not rr["runtime_lines"]:
            same_rb7 += 1
        else:
            diffs.append(f"{name}: {rr['why'][:80]}")
    for p in sorted(glob.glob(os.path.join(D189, "passes/*/p*/run.json"))):
        d = os.path.dirname(p)
        cfg = os.path.basename(os.path.dirname(d))
        run = json.load(open(p))
        av = [run["build"] + ("/host/sparseparity_host" if cfg == "sparse-parity" else "/host/ledger_host")] + run["host_args"].split()
        f = os.path.join(d, "host.json" if cfg == "sparse-parity" else "host-raw.json")
        t = open(f).read()
        jj, rr = C.host_result(t, "spp" if cfg == "sparse-parity" else "ledger", av)
        count_rb7 += 1
        if jj == V1.last_json(t) and jj:
            same_rb7 += 1
        else:
            diffs.append(f"{cfg}/{os.path.basename(d)}: {rr['why'][:80]}")
    st = {}
    for p in sorted(glob.glob(os.path.join(D189, "passes/*/p*/host-raw.json"))):
        s_ = (V1.last_json(open(p).read()) or {}).get("status")
        st[s_] = st.get(s_, 0) + 1
    case("RB7", count_rb7 == 31 and same_rb7 == count_rb7, f"{same_rb7} of {count_rb7} committed lines of E189's day (7 smoke runs, 20 ledger passes, 4 sparse parity passes) "
         f"read by v2 exactly as v1 read them (the ledger passes' statuses {st}){'; differ: ' + '; '.join(diffs[:4]) if diffs else ''}")
    # ---- RB8: sparse parity in aifoundry1's form
    sp = open(os.path.join(D189, "session/smoke/sparse-parity-r1/stdout.txt")).read().rstrip("\n")
    sav = json.load(open(os.path.join(D189, "session/smoke/sparse-parity-r1/smoke.json")))["argv"]
    swant = json.loads(sp)
    count_rb8 = good_rb8 = 0
    for s in [RT + sp + "\n"] + [sp[:k] + RT + sp[k:] + "\n" for k in range(0, len(sp) + 1, 50)]:
        jj, rr = C.host_result(s, "spp", sav)
        count_rb8 += 1
        good_rb8 += jj == swant and rr["runtime_lines"] == ["Opening device 1"]
    case("RB8", good_rb8 == count_rb8 and count_rb8 > 40, f"{good_rb8} of {count_rb8} sparse parity forms (the runtime line before E189's committed smoke line, as its host prints "
         f"it on aifoundry1, and at every 50th byte inside) read as the whole line (status {swant.get('status')}, solved "
         f"{(swant.get('result') or {}).get('solved')})")
    # ---- RB9: the self-test's lines
    s191 = open(os.path.join(D191, "session/smoke/ledger-selftest/stdout.txt")).read()
    s189 = open(os.path.join(D189, "session/smoke/ledger-selftest/stdout.txt")).read()
    case("RB9", "SELFTEST PASS" in C.drop_runtime(s191)[0] and "SELFTEST PASS" in C.drop_runtime(s189)[0]
         and C.drop_runtime(s191) == (s191, []) and C.drop_runtime(s189) == (s189, []),
         "both committed self-test outputs read 'SELFTEST PASS'; no runtime line in either (the self-test opens no device)")
    # ---- RB10: every occurrence of "Opening device" in the lab's raw text files, as committed at RB10_AT (git's blobs, not the worktree)
    kinds = {"exact runtime line": 0, "quoted inside a JSON string": 0, "inside a host line (the day's split)": 0, "other": 0}
    other = []
    nfiles = 0
    inside = []
    git = ["git", "-C", REPO]
    have = subprocess.run(git + ["cat-file", "-e", RB10_AT + "^{commit}"], capture_output=True).returncode == 0
    gr = subprocess.run(git + ["grep", "-l", "-z", "-F", "Opening device", RB10_AT, "--", "docs/reports/data"], capture_output=True) if have else None
    names = []
    if gr is not None and gr.returncode == 0:
        for x in gr.stdout.split(b"\0"):
            p = x.decode("utf-8", "replace").split(":", 1)[-1]
            n = os.path.basename(p)
            if x and n.endswith((".out", ".txt", ".raw", ".jsonl", ".log", ".err", ".json")) and not n.startswith("README"):
                names.append(p)
    out = subprocess.run(git + ["cat-file", "--batch"], input="".join(f"{RB10_AT}:{p}\n" for p in names).encode(),
                         capture_output=True).stdout if names else b""
    pos = 0
    for p in names:
        nl = out.index(b"\n", pos)
        head = out[pos:nl].split()
        if len(head) != 3 or head[1] != b"blob":
            other.append(f"{p}: not read from git ({head!r})")
            break
        size = int(head[2])
        bb = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
        if b"Opening device" not in bb:
            continue
        nfiles += 1
        t = bb.decode("utf-8", "replace")
        for m in re.finditer(r"Opening device", t):
            i = m.start()
            after = t[i:i + 40]
            lstart = t.rfind("\n", 0, i) + 1
            if re.match(r"Opening device [0-9]+\n", after):
                if lstart == i:
                    kinds["exact runtime line"] += 1
                else:
                    kinds["inside a host line (the day's split)"] += 1
                    inside.append(p)
            elif re.match(r"Opening device [0-9]+\\n", after):
                kinds["quoted inside a JSON string"] += 1
            else:
                kinds["other"] += 1
                other.append(f"{p}: {after!r}")
    day = os.path.relpath(D191, REPO) + "/"
    case("RB10", have and not other and len(inside) == 1 and inside[0].startswith(day) and kinds["exact runtime line"] > 700,
         f"at {RB10_AT[:8]} (git's blobs: {'present' if have else 'NOT IN THIS CLONE'}): {sum(kinds.values())} occurrences in {nfiles} "
         f"committed files: {kinds}; each a form RUNTIME_LINE drops, or a quotation; the one inside a host's line: "
         f"{[os.path.relpath(q, day.rstrip('/')) for q in inside]} in 1a4bc1e3's record" + (f"; OTHER: {other[:3]}" if other else ""))
    n = sum(res)
    print(f"REALBYTES-E191 {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'}")
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
