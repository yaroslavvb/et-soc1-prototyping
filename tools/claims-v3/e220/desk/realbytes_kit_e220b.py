#!/usr/bin/env python3
"""E220 ARM B (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum): THE PARSERS ON REAL COMMITTED BYTES (E216's desk/realbytes_kit_e216.py
form, E209's desk/realbytes_e209.py;
E215's and E209's lessons: every host-output parser on the path fed the lab's committed bytes of that tool, from THIS card where the card has
them; the collection's scrub tested on records that carry the box's home). Reads committed files only (no device, no host process, no
network); writes only in its scratch folder. Standard library only. Named realbytes_kit_e220b.py: the registration's desk/realbytes_e220.py is
the frozen scorer's reader check and stays as committed.

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/realbytes_kit_e220b.py <empty scratch dir>

THE CASES (every input a committed file of the lab, named by path):
  RB1  E208's parse_sparsity (src/mms_common.py, unchanged) on every host stdout of E209's session on this card (data ea3fa3ce): each process's
       fma-record count equal to the runner's own n_launch in its run.json (every run, the smoke too); RB1b the same on E216's session on this
       card (Thu 19 Nov 2026: E208's runner with family G, rgm211's host on ten gemmLnc runs)
  RB2  the same on E212's S3 re-run on this card (data 321f992c, the model session's E208-form session)
  RB3  E208's parse_ident (src/mms_ident.py, unchanged) on every host stderr and both config reads of those three sessions: the host's node
       /dev/et0_ops, the reader's /dev/et0_mgmt, physical device ID 0 on each, nothing else
  RB4  E220's walk check (src/run_e220b.walk_read) on EVERY REAL STDOUT OF RGM211'S HOST RUNNING A gemmLnc ARM the lab has committed (E216 on
       THIS card, E213 arm A on aifoundry3, E213 arm B on aifoundry1 card 1, E211's family C on aifoundry3: runs and smokes): each read ok, walk 'mn' on every launch,
       no tag, walk_launches_bad 0; and E208's ok_launch reads their launch records (rgm211's extra walk fields change nothing it reads)
  RB5  the walk check REFUSES what is not family G's: rgm211's gemmLn stdouts (walk 'nm', the tag on every hart: E211's) and rgm136's own host's
       stdouts (no walk field at all: E209's and E216's on this card), so a gemmLnc process run by the wrong host or kernel cannot pass it
  RB6  E191's runtime line spliced at EVERY BYTE OFFSET of a real gemmLnc launch record and of its check record (E213 arm A's a082): the walk
       check never reads a wrong value: the split record is dropped (one launch fewer, the rest byte-equal) or the check record lost (then the
       check reads 'no check record' and the kernel stop follows); never ok with a changed field
  RB7  THE MASK on E209's REAL fwgate read record (session/first/fwgate-aifoundry2-c0-20261117-103044.json, committed with its ledger line
       masked by E209's kit note 1): the box's raw bytes rebuilt with this box's home written back into that line read E209's MANIFEST line
       a91fcc83... exactly; collect_e220b's mask_record() turns them into the committed bytes 2d56a732... exactly; THE SCRUB's patterns (the
       login, the home, '/home/') find the home in the raw bytes and nothing in the masked ones; two ledger lines: stopped (16)
  RB8  collect_e220b.py --manifest-check on E209's committed session folder as committed (1 line by THE MASK) and with the raw record (0 by THE
       MASK, every line plain OK); another line changed: refused (10)
  RB9  THE WHOLE COLLECTION on a stand-in box root whose session is E209's real session with the raw record (the box's home in its ledger line)
       restored: collect_e220b.py exit 0, the data directory's record masked and nothing else changed; with a home path planted in runner.out:
       THE SCRUB stops it (16) and nothing is written in the stand-in lab
  RB7b THE MASK on E216's REAL fwgate read record (session/first/fwgate-aifoundry2-c0-20261119-165555.json, THE MASK of E216's kit, note 12):
       the raw bytes rebuilt with this box's home read E216's MANIFEST line 5204a9ad... exactly; mask_record() gives the committed 9b49fec5...
  RB8b collect_e220b.py --manifest-check on E216's committed session folder: OK with 1 line by THE MASK
Prints one line a case and REALBYTES-E220B <n> of <m> PASS last.
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import importlib.util
import json
import os
import pwd
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
SRC8 = os.path.join(REPO, "tools", "claims-v3", "e208", "proposal", "src")
E209S = os.path.join(DATA, "2026-11-17-e209-blind-matmul-aifoundry2", "session")
E216S = os.path.join(DATA, "2026-11-19-e216-blind-matmul-aifoundry2", "session")
REC16 = "first/fwgate-aifoundry2-c0-20261119-165555.json"
RAW16_SHA = "5204a9adc5eb149465718b3d4d264a6de033e8ad7384cde10816bbe66bce358d"
MASKED16_SHA = "9b49fec575adabe59ca7aa8eb5a9258f5b7fa694b945feb85ef95854a5b5492d"
E212S3 = os.path.join(DATA, "2026-11-18-e212-mmsweep2-a2c0-S3")
G_DIRS = [os.path.join(DATA, "2026-11-18-e213-blind-matmul-aifoundry3", "session"), os.path.join(DATA, "2026-11-18-e213-blind-matmul-aifoundry1-c1", "session"),
          os.path.join(DATA, "2026-11-17-e211-second-kernel-aifoundry3", "session")]
G_DIRS.append(E216S)          # E216 on THIS card (kept last: RB5 reads G_DIRS[2], E211, and RB6 G_DIRS[0], E213 arm A)
REC = "first/fwgate-aifoundry2-c0-20261117-103044.json"
RAW_SHA = "a91fcc837457ffb2c447ceeb61800bfec3bde1eeab2a5f85884eb1ced95fe47d"
MASKED_SHA = "2d56a73219f7ba99b08986ef723a46477444feda7b3db7f255eb6e027e09a377"
RT = "[runtime] ET [DEVICE_LAYER]: Opening device 0\n"
ROWS = []
sys.path.insert(0, SRC8)
import mms_common as C  # noqa: E402  (E208's, unchanged)
import mms_ident as N  # noqa: E402


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    spec.loader.exec_module(m)
    return m


def row(words, ok, detail=""):
    ROWS.append(bool(ok))
    print(f"{'PASS' if ok else 'FAIL'} {words}" + (f" [{detail}]" if detail != "" else ""), flush=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sessions_of(top):
    """the E208-form session folders under a committed data folder (those holding queue.json and runs/)"""
    return sorted({os.path.dirname(q) for q in glob.glob(os.path.join(top, "**", "queue.json"), recursive=True)
                   if os.path.isdir(os.path.join(os.path.dirname(q), "runs"))})


def launch_counts(sd):
    """(processes checked, mismatches) over every run's run.json and the smoke's smoke.json"""
    n, bad = 0, []
    for rj in sorted(glob.glob(os.path.join(sd, "runs", "*", "run.json"))):
        r = json.load(open(rj))
        for p in r.get("procs") or []:
            out = os.path.join(os.path.dirname(rj), p["name"] + ".out")
            k = len([x for x in C.parse_sparsity(open(out, errors="replace").read()) if x.get("test") == "fma"])
            n += 1
            if k != p.get("n_launch"):
                bad.append(f"{os.path.relpath(out, sd)}: {k} vs {p.get('n_launch')}")
    for sj in sorted(glob.glob(os.path.join(sd, "smoke", "*", "smoke.json"))):
        p = json.load(open(sj))
        out = os.path.join(os.path.dirname(sj), "proc.out")
        k = len([x for x in C.parse_sparsity(open(out, errors="replace").read()) if x.get("test") == "fma"])
        n += 1
        if k != p.get("n_launch"):
            bad.append(f"{os.path.relpath(out, sd)}: {k} vs {p.get('n_launch')}")
    return n, bad


def idents(sd):
    tg, ids, n = set(), set(), 0
    for f in glob.glob(os.path.join(sd, "runs", "*", "proc-*.err")) + glob.glob(os.path.join(sd, "smoke", "*", "proc.err")):
        t, i = N.parse_ident(open(f, errors="replace").read())
        tg |= {f"/dev/et{c}_{k}" for c, k in t}
        ids |= set(i)
        n += 1
    ct, ci = set(), set()
    for f in glob.glob(os.path.join(sd, "config-*.err")):
        t, i = N.parse_ident(open(f, errors="replace").read())
        ct |= {f"/dev/et{c}_{k}" for c, k in t}
        ci |= set(i)
    return n, tg, ids, ct, ci


def g_stdouts():
    out = []
    for top in G_DIRS:
        for f in sorted(glob.glob(os.path.join(top, "**", "*.out"), recursive=True)):
            t = open(f, errors="replace").read()
            sp = C.parse_sparsity(t)
            if any(str(x.get("arm", "")).startswith("gemmLnc") for x in sp):
                out.append((f, t))
    return out


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    S = os.path.abspath(argv[0])
    os.makedirs(S, exist_ok=True)
    if os.listdir(S):
        print("give an empty scratch dir")
        return 2
    print(f"E220 ARM B REALBYTES {time.strftime('%Y-%m-%d %H:%M:%S %Z')}: committed bytes only (the lab clone's HEAD)")
    # E220's runner module from a box root synced here (its identity gate reads its inputs beside it in src/); importing it runs nothing
    box = os.path.join(S, "box-root")
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "make_box_e220b.py"), "sync", box], capture_output=True, text=True)
    if r.returncode != 0:
        print("the sync failed: " + r.stdout + r.stderr)
        return 1
    sys.path.insert(0, os.path.join(box, "src"))
    import run_e220b as RE  # noqa: E402
    CO = load("collect_e220b", os.path.join(E, "collect_e220b.py"))
    # RB1, RB2
    for tag, top in (("RB1 E209's session on this card", E209S), ("RB1b E216's session on this card", E216S), ("RB2 E212's S3 re-run on this card", E212S3)):
        sds = sessions_of(top) if top == E212S3 else [top]
        tot, bad = 0, []
        for sd in sds:
            n, b = launch_counts(sd)
            tot += n
            bad += b
        row(f"{tag}: E208's parse_sparsity on every host stdout, each process's fma records = the runner's own n_launch", tot > 0 and not bad,
            f"{len(sds)} session(s), {tot} processes, mismatches {bad[:3]}")
    # RB3
    for tag, top in (("E209's", E209S), ("E216's", E216S), ("E212 S3's", E212S3)):
        sds = sessions_of(top) if top == E212S3 else [top]
        ok, det = True, []
        for sd in sds:
            n, tg, ids, ct, ci = idents(sd)
            ok &= n > 0 and tg == {"/dev/et0_ops"} and ids == {0} and ct == {"/dev/et0_mgmt"} and ci == {0}
            det.append(f"{n} host stderrs: {sorted(tg)} IDs {sorted(ids)}; config reads {sorted(ct)} IDs {sorted(ci)}")
        row(f"RB3 E208's parse_ident on {tag} host stderrs and config reads: the ops node, the mgmt node, physical device ID 0, nothing else", ok,
            "; ".join(det))
    # RB4
    gs = g_stdouts()
    bad, launches, okl = [], 0, 0
    for f, t in gs:
        wok, words, rec = RE.walk_read(t)
        sp = [x for x in C.parse_sparsity(t) if x.get("test") == "fma"]
        launches += len(sp)
        okl += sum(1 for x in sp if C.ok_launch(x))
        if not wok or rec["walk"] != ["mn"]:
            bad.append(f"{os.path.relpath(f, DATA)}: {words}")
    want_ok = sum(1 for f, t in gs for x in C.parse_sparsity(t) if x.get("test") == "fma" and (x.get("launch") if x.get("launch") is not None else -9) >= 0
                  and x.get("ok") and (x.get("wall_s") or 0) >= 0.1 and x.get("passes"))
    n16 = sum(1 for f, _ in gs if f.startswith(E216S + os.sep))
    row("RB4 E220's walk check on EVERY committed stdout of rgm211's host running a gemmLnc arm (E216 on this card, E213 arm A, E213 arm B, E211 "
        "family C): each ok, walk 'mn', no tag, walk_launches_bad 0; E208's ok_launch reads their launches",
        len(gs) >= 18 and n16 == 10 and not bad and okl == want_ok and okl > 0,
        f"{len(gs)} stdouts ({n16} E216 on this card, {sum(1 for f, _ in gs if 'aifoundry3' in f)} aifoundry3, "
        f"{sum(1 for f, _ in gs if 'aifoundry1' in f)} card 1), "
        f"{launches} launch records, {okl} counted by ok_launch; refused {bad[:2]}")
    # RB5
    nm = []
    for f in sorted(glob.glob(os.path.join(G_DIRS[2], "**", "*.out"), recursive=True)):
        t = open(f, errors="replace").read()
        if any(str(x.get("arm", "")).startswith("gemmLn") and not str(x.get("arm", "")).startswith("gemmLnc") for x in C.parse_sparsity(t)):
            nm.append((f, RE.walk_read(t)))
    own = [(f, RE.walk_read(open(f, errors="replace").read())) for f in sorted(glob.glob(os.path.join(E209S, "runs", "*", "proc-00.out")))[:20]]
    own += [(f, RE.walk_read(open(f, errors="replace").read())) for f in sorted(glob.glob(os.path.join(E216S, "runs", "*", "proc-00.out")))[:20]
            if not any(str(x.get("arm", "")).startswith("gemmLnc") for x in C.parse_sparsity(open(f, errors="replace").read()))]
    row("RB5 the walk check refuses what is not family G's: rgm211's gemmLn stdouts (walk 'nm', tagged) and rgm136's own host's (no walk field)",
        nm and own and all(not w[0] and "nm" in w[1] for _, w in nm) and all(not w[0] for _, w in own),
        f"{len(nm)} gemmLn stdouts refused ({nm[0][1][1][:60] if nm else ''}); {len(own)} rgm136-host stdouts refused ({own[0][1][1][:60] if own else ''})")
    # RB6
    a082 = os.path.join(G_DIRS[0], "runs", "079-pass1-a082", "proc-00.out")
    t = open(a082).read()
    lines = t.splitlines(keepends=True)
    li = [i for i, ln in enumerate(lines) if ln.startswith("SPARSITY ") and '"test":"fma"' in ln and '"launch":0,' in ln][0]
    ci = [i for i, ln in enumerate(lines) if ln.startswith("SPARSITY ") and '"test":"check"' in ln][0]
    base_ok, base_w, base_rec = RE.walk_read(t)
    orig = {json.dumps(x, sort_keys=True) for x in C.parse_sparsity(t)}
    wrong, n_off, dropped, lost = [], 0, 0, 0
    for idx in (li, ci):
        L = lines[idx]
        for k in range(1, len(L) - 1):
            spl = L[:k] + "\n" + RT + L[k:]
            t2 = "".join(lines[:idx]) + spl + "".join(lines[idx + 1:])
            n_off += 1
            wok, words, rec = RE.walk_read(t2)
            recs = C.parse_sparsity(t2)
            if any(json.dumps(x, sort_keys=True) not in orig for x in recs):
                wrong.append(f"line {idx + 1} offset {k}: a changed record read")
            if idx == li:
                dropped += rec["launches"] == base_rec["launches"] - 1
                if wok and rec["launches"] != base_rec["launches"] - 1:
                    wrong.append(f"launch line offset {k}: ok with {rec['launches']} launches")
            else:
                lost += (not wok) and "no check record" in words
                if wok:
                    wrong.append(f"check line offset {k}: still ok")
    row("RB6 a runtime line spliced at every byte offset of a82's launch record and of its check record: never a changed value read; a split "
        "launch record is dropped (the rest byte-equal), a split check record leaves no check (the kernel stop)",
        base_ok and not wrong and dropped == len(lines[li]) - 2 and lost == len(lines[ci]) - 2,
        f"{n_off} splices; launch line dropped {dropped}/{len(lines[li]) - 2}; check lost {lost}/{len(lines[ci]) - 2}; wrong {wrong[:2]}")
    # RB7
    home = pwd.getpwuid(os.getuid()).pw_dir
    login = pwd.getpwuid(os.getuid()).pw_name
    committed = open(os.path.join(E209S, REC), "rb").read()
    raw = committed.replace(b'"ledger": "~/.local/state/fwgate/', b'"ledger": "' + home.encode() + b'/.local/state/fwgate/', 1)
    man = dict((ln.split("  ", 1)[1].strip(), ln.split("  ", 1)[0]) for ln in open(os.path.join(E209S, "MANIFEST.sha256")) if "  " in ln)
    mb, li7 = CO.mask_record(raw, home.encode())
    pats = [login.encode(), home.encode(), b"/home/"]
    two = raw + b"\n" + [ln for ln in raw.split(b"\n") if b'"ledger"' in ln][0]
    stopped = subprocess.run([sys.executable, "-I", "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); import collect_e220b as C; "
                              "C.mask_record(open(sys.argv[2], 'rb').read(), sys.argv[3].encode())", E,
                              os.path.join(S, "two.json"), home], capture_output=True, text=True) if open(os.path.join(S, "two.json"), "wb").write(two) else None
    row("RB7 THE MASK on E209's REAL fwgate read record: the raw bytes (this box's home written back) = E209's MANIFEST line a91fcc83...; the mask "
        "gives the committed bytes 2d56a732... exactly, its line 34; THE SCRUB's patterns hit the raw and miss the masked; two ledger lines stop (16)",
        sha(raw) == RAW_SHA == man.get(REC) and sha(mb) == MASKED_SHA and li7 == 34 and any(p in raw for p in pats)
        and not any(p in mb for p in pats) and stopped is not None and stopped.returncode == 16,
        f"raw {sha(raw)[:16]}, masked {sha(mb)[:16]}, line {li7}; two lines rc {stopped.returncode if stopped else None}")
    # RB7b: THE MASK on E216's real record (this card, Thu 19 Nov 2026)
    c16 = open(os.path.join(E216S, REC16), "rb").read()
    raw16 = c16.replace(b'"ledger": "~/.local/state/fwgate/', b'"ledger": "' + home.encode() + b'/.local/state/fwgate/', 1)
    man16 = dict((ln.split("  ", 1)[1].strip(), ln.split("  ", 1)[0]) for ln in open(os.path.join(E216S, "MANIFEST.sha256")) if "  " in ln)
    mb16, li16 = CO.mask_record(raw16, home.encode())
    row("RB7b THE MASK on E216's REAL fwgate read record (this card): the raw bytes (this box's home written back) = E216's MANIFEST line "
        "5204a9ad...; the mask gives the committed bytes 9b49fec5... exactly, its line 34; THE SCRUB's patterns hit the raw and miss the masked",
        sha(raw16) == RAW16_SHA == man16.get(REC16) and sha(mb16) == MASKED16_SHA == sha(c16) and li16 == 34 and any(p in raw16 for p in pats)
        and not any(p in mb16 for p in pats), f"raw {sha(raw16)[:16]}, masked {sha(mb16)[:16]}, line {li16}")
    r16 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--manifest-check", E216S], capture_output=True, text=True)
    row("RB8b step 13's manifest read on E216's committed session as committed: OK with 1 line by THE MASK",
        r16.returncode == 0 and "(1 by THE MASK" in r16.stdout, r16.stdout.strip()[:120])
    # RB8
    s8 = os.path.join(S, "rb8-session")
    shutil.copytree(E209S, s8)
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--manifest-check", s8], capture_output=True, text=True)
    open(os.path.join(s8, REC), "wb").write(raw)
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--manifest-check", s8], capture_output=True, text=True)
    open(os.path.join(s8, "session.log"), "a").write("a changed line\n")
    r3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--manifest-check", s8], capture_output=True, text=True)
    row("RB8 step 13's manifest read on E209's committed session: OK with 1 line by THE MASK; on the raw record OK with 0; another line changed: 10",
        r1.returncode == 0 and "(1 by THE MASK" in r1.stdout and r2.returncode == 0 and "(0 by THE MASK" in r2.stdout and r3.returncode == 10,
        f"{r1.stdout.strip()[:80]} | {r2.stdout.strip()[:60]} | rc {r3.returncode}")
    # RB9
    root = os.path.join(S, "rb9-root")
    sid = f"{int(time.time()) - 3600}-a2c0-E220"
    sd = os.path.join(root, "sessions", sid)
    shutil.copytree(E209S, sd)
    open(os.path.join(sd, REC), "wb").write(raw)
    os.makedirs(os.path.join(root, "build"))
    for n in ("BUILD-mms.json", "BUILD-e220b.json"):
        json.dump({"day": "2026-11-19", "verdict": "BUILT", "box": "aifoundry2", "what": "a desk test's record"}, open(os.path.join(root, "build", n), "w"))
    shutil.copytree(SRC8, os.path.join(root, "src"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(os.path.join(REPO, "tools", "claims-v3", "e209", "box", "a2c0-E209.json"), os.path.join(root, "src", "sched", "a2c0-E209.json"))
    #   (the session is E209's: E208's checker reads its schedule from the box root's src/sched/, as E209's box root held it)
    lab = os.path.join(S, "rb9-lab")
    chk = "docs/reports/data/2026-11-16-e208-mmsweep-a2c0-S1"
    os.makedirs(os.path.join(lab, chk))
    for n in ("check_session_e208.py", "SHA256SUMS"):
        shutil.copyfile(os.path.join(REPO, chk, n), os.path.join(lab, chk, n))
    rbo = os.path.join(S, "rb9-rbout")
    os.makedirs(rbo)
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--root", root, "--sid", sid, "--rb-out", rbo, "--lab", lab],
                       capture_output=True, text=True)
    dd = glob.glob(os.path.join(lab, "docs", "reports", "data", "*-e220-blind-matmul-aifoundry2"))
    got = open(os.path.join(dd[0], "session", REC), "rb").read() if dd else b""
    same_else = bool(dd) and all(open(os.path.join(dd[0], "session", rel), "rb").read() == open(os.path.join(sd, rel), "rb").read()
                                 for rel in man if rel != REC and os.path.isfile(os.path.join(sd, rel)))
    ok9a = r.returncode == 0 and sha(got) == MASKED_SHA and same_else and "THE SCRUB: " in r.stdout
    shutil.rmtree(os.path.join(lab, "docs", "reports", "data", os.path.basename(dd[0]))) if dd else None
    open(os.path.join(sd, "runner.out"), "a").write(f"a planted home path: {home}/x\n")
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e220b.py"), "--root", root, "--sid", sid, "--rb-out", rbo, "--lab", lab,
                         "--copy-name", "copy2"], capture_output=True, text=True)
    nothing = not glob.glob(os.path.join(lab, "docs", "reports", "data", "*-e220-blind-matmul-aifoundry2"))
    row("RB9 THE WHOLE COLLECTION on E209's real session with its raw record (the box's home in the ledger line): exit 0, the record masked to "
        "the committed bytes, every other file the box's; a home path planted in runner.out: THE SCRUB stops it (16), nothing in the lab",
        ok9a and r2.returncode == 16 and "THE SCRUB found" in r2.stdout and nothing,
        f"{r.stdout.strip().splitlines()[-1][:90] if r.stdout.strip() else r.stderr[-200:]} | rc {r2.returncode}")
    print(f"REALBYTES-E220B {sum(ROWS)} of {len(ROWS)} {'PASS' if all(ROWS) else 'FAIL'}")
    return 0 if all(ROWS) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
