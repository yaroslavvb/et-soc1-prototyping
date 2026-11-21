#!/usr/bin/env python3
"""E222's REAL-BYTES desk test (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; CONTEXT section 116's lesson: "every kit reads a
host's result from a source no runtime print can split ... and its real-path desk test feeds the parser the REAL stdout bytes committed from a
card"; E209's lesson: a collection's scrub must meet records that carry the box's home BEFORE the session). Every parser, reducer path, identity
reader and the collection's scrub of E222's kit, fed bytes committed from aifoundry3 card 0 - E222's card - read-only (nothing here writes in the
repo; the scrub cases write only under the scratch folder given). E218's desk/realbytes_e218.py (kit 5582edfc; E215 arm A's, 8bde0182) for
E222's one card, WITH THE BYTES OF THE LAB'S LATEST DAYS ON THIS CARD (the round's lesson: every host-output parser fed real committed bytes from
aifoundry3 card 0 - E218, E215 arm A and E213 arm A):

  RB-E218A  E218's committed outputs on aifoundry3 card 0 (docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/, b445b0f5, run at 03:11-03:56
            PST Fri 20 Nov 2026 by E218's kit, of which E222's is the port: E222's two families exactly - 'rgm136 gemmL' on rgm136's host, 'rgm136
            gemmLnc' on rgm211's host with rgm136's ELF - the opening smoke s01 and the gemmLnc smoke s03 in its place, subset masks, f04's two
            processes cut by the plain timeout 10 among them) through e222_common.host_records with each process's own committed command line:
            every record read, none unparsed or naming another command; every rgm211-host process's walk read by its family from the run's own
            point (points-e218.json's loop) and good;
  RB-E218AR E218's committed runs and smoke processes through reduce_e222.reduce_run (E218's reducer, line for line) against its committed
            data-e218.json: every run field and walk field equal, the gemmLnc smoke s03 at its place (n 84) among them;

  RB-E215A  E215 arm A's committed outputs on aifoundry3 card 0 (docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/, 8355db15, run on Thu 19 Nov 2026:
            both of E222's families among its four - 'rgm136 gemmL' on rgm136's host, 'rgm136 gemmLnc' on rgm211's host with rgm136's ELF - the
            opening smoke s01, s02, s04 and the gemmLnc smoke s03 in its place, subset masks) through e222_common.host_records with each process's own
            committed command line: every record read, none unparsed or naming another command; every rgm211-host process's walk read by its family
            from the run's own point (points-e215.json's loop) and good;
  RB-E215AR E215 arm A's committed runs and smoke processes through reduce_e222.reduce_run (E215 arm A's reducer, line for line) against its
            committed data-e215.json: every run field and walk field equal, the gemmLnc smoke s03 at its place (n 112) among them;
  RB-E213A  E213 arm A's committed outputs on aifoundry3 card 0 (docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/, c69a12aa) the same way;
  RB-E213AR E213 arm A's committed runs through reduce_run against its committed data-e213.json: equal;
  and, as E215's and E213's kits read them (the same card, the same hosts' forms):
  RB-E211   E211's committed outputs on aifoundry3 card 0, BOTH HOSTS: every record read, every gemmLnc process's walk (E222's family 'rgm136
            gemmLnc', mn) good;
  RB-E211R  E211's committed runs through reduce_run against data-e211.json: equal;
  RB-E207   E207's committed rgm136 outputs on aifoundry3 card 0 (its shire masks among them): every record read;
  RB-E207R  E207's committed runs through reduce_run against data-e207.json: equal;
  RB-SPLICE runtime lines (cards 0 and 1, and a nested pair) spliced into REAL records at every byte offset: a gemmLnc launch record and check
            record of rgm211's host from E215 arm A (the walk fields inside) and an rgm136-host record of E215 arm A's: each reads the same records
            and the same walk;
  RB-CFG    config_json on the card's committed config lines (E215 arm A's and E213 arm A's config-start.out) with runtime lines before, after and
            inside: the committed config-start.json each time; config_ok passes them and refuses E206 arm B's card-1 line (TDP 65 W);
  RB-ID     THE CARD'S IDENTITY GATE on committed forms: E222's arm passes aifoundry3's committed reads (E215 arm A's, E213 arm A's, E211's and E207's,
            start and end) and refuses card 1's (E206 arm B's) and a read with its block removed; the committed smoke host blocks (E215 arm A's s01
            and s03, rgm136's and rgm211's hosts) read by host_identity as card 0's;
  RB-SIM    rgm211's host's REAL simulator bytes (E211's committed logs/simcheck, its kit's sys_emu runs on aifoundry3): every stdout's records read
            whole against its own command line; the gemmLnc case C (rgm136's ELF on rgm211's host) read OK as 'rgm136 gemmLnc' by E222's walk check;
  RB-SMOKE  the smoke's reading on real bytes: each committed smoke process of E218 (s01, s03), E215 arm A (s01-s04), E213 arm A, E211 and E207 read the way the
            runner's smoke gate reads it (the median cycles_per_op over its counted launches) and the way the reducer hands it to the frozen
            scorer's R0 (reduce_e222.reduce_run's cycles_per_op): equal, and inside R0's band of 200-4,000;
  RB-SCRUB  THE COLLECTION'S SCRUB ON REAL RECORDS THAT CARRY THE BOX'S HOME (E209's lesson): E218's, E215 arm A's, E213 arm A's, E211's and E207's committed
            aifoundry3 sessions turned back into the box's own bytes (each committed file whose sha256 is not its MANIFEST line has "~" and
            "<login>" put back as the box's home and login, and must then read its MANIFEST sha256 exactly: the box's raw record, the home in it at
            every place the box wrote one), then collect_e222.copy_back_exact (COPY-BACK EXACT) and collect_e222's scrub over a copy: every file
            byte-identical to the committed session, none left with a home or the login; the same with the home given in three forms (a stand-in
            physical path through a symlink, the user database's) and a record holding a home NOT given: the scrub refuses it (SCRUB-CHECK LEFT) -
            never silently. The box login and home used to rebuild the raw bytes are this desk's (the same login on the boxes); they are written only
            in the scratch folder, never in a log line;
  RB-HOLDERS ANOTHER LOGIN'S et-who HOLDER LINES AT THE COLLECTION: E215 arm A's committed et-who record (session/reads/etwho-001-tie-t01.out) turned
            back into a box's bytes with a MADE-UP login of ours ("e222us", its home /home/e222us) and two lines of a MADE-UP other login
            ("e222other") holding card 0 appended - one whose command names no home, one whose command names its own /home/... - in a stand-in
            session copy: collect_e222.py scrub-check reads CLEAN (the checked folder unchanged), and the data collection (desk mode) COLLECTED, with
            no collected file naming either made-up login or holding a /home/ path, the other login's two lines "<another-login>" with their pid and
            time and no command, and our own lines byte-identical to the committed record; then the same holder line in a file the scrub does not
            rewrite (a .bin): SCRUB-CHECK LEFT (exit 3) and SCRUB FAILED (exit 3) - refused, never silent.
    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/realbytes_e222.py <scratch dir> > logs/realbytes-e222.txt   (last line: REALBYTES-E222 <n> of <m> PASS)
A desk read of committed records and a desk check of code: nothing here is measured. SPDX-License-Identifier: Apache-2.0
"""
import glob
import gzip
import hashlib
import json
import os
import pwd
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
sys.path.insert(0, E)
import e222_common as C  # noqa: E402
import e222_ident as N1  # noqa: E402
import reduce_e222 as RD  # noqa: E402
import collect_e222 as CO  # noqa: E402

DATA = os.path.join(REPO, "docs/reports/data")
E218D = os.path.join(DATA, "2026-11-20-e218-blind-matmul-aifoundry3")
E215A = os.path.join(DATA, "2026-11-19-e215-blind-matmul-aifoundry3")
E213A = os.path.join(DATA, "2026-11-18-e213-blind-matmul-aifoundry3")
E211D = os.path.join(DATA, "2026-11-17-e211-second-kernel-aifoundry3")
E207D = os.path.join(DATA, "2026-11-17-e207-blind-matmul-aifoundry3")
E206B = os.path.join(DATA, "2026-11-17-e206-matmul-sweep-aifoundry1-c1")
P218 = os.path.join(REPO, "tools/claims-v3/e218/points-e218.json")
P215 = os.path.join(REPO, "tools/claims-v3/e215/points-e215.json")
P213 = os.path.join(REPO, "tools/claims-v3/e213/points-e213.json")
SIM = os.path.join(REPO, "tools/claims-v3/e211/logs/simcheck")
# the four families of E215 arm A and E213 arm A, read here only to know each committed process's host and ELF (E222 runs the first two)
LOOPS_READ = dict(C.LOOPS, **{"rgm211 gemmLn": {"host": "rgm211", "elf": "rgm211", "walk": "nm"},
                              "rgm211 gemmL": {"host": "rgm211", "elf": "rgm211", "walk": "mn"}})


class T:
    def __init__(self):
        self.n = self.ok = 0

    def case(self, name, good, detail):
        self.n += 1
        self.ok += 1 if good else 0
        print(f"{name}: {'PASS' if good else 'FAIL'} - {detail}", flush=True)


def plain_parse(text):
    out = []
    for ln in text.splitlines():
        if ln.startswith("SPARSITY "):
            try:
                out.append(json.loads(ln[9:]))
            except ValueError:
                pass
    return out


def proc_argv(pdir, name):
    for f in ("run.json", "smoke.json"):
        p = os.path.join(pdir, f)
        if os.path.exists(p):
            j = json.load(open(p))
            for pr in j.get("procs", []) or [j]:
                if pr.get("name", "proc") == name:
                    return pr.get("argv")
    return None


def by_time(recs):
    return sorted(recs, key=lambda r: (r.get("t_start_ms") or 0, r.get("launch") or 0, r.get("test") or ""))


def outs(sd):
    return sorted(glob.glob(os.path.join(sd, "smoke", "*", "proc.out")) + glob.glob(os.path.join(sd, "runs", "*", "proc-*.out")))


def parse_all(files, label_root):
    n_rec = n_rt = 0
    bad, cards = [], set()
    for p in files:
        text = open(p, errors="replace").read()
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4])
        fma, chk, info = C.host_records(text, argv)
        want = [r for r in plain_parse(text) if r.get("test") in ("fma", "check")]
        got = by_time(fma + chk)
        n_rec += len(got)
        n_rt += len(info["runtime_lines"])
        cards |= set(C.runtime_cards(info["runtime_lines"]))
        if argv is None or got != by_time(want) or info["unparsed"] or info["mismatched"] or text.count("Opening device") != len(info["runtime_lines"]):
            bad.append(f"{os.path.relpath(p, label_root)}: {len(got)} of {len(want)} records, unparsed {info['unparsed']}, mismatched "
                       f"{len(info['mismatched'])}, argv {argv is not None}")
    return n_rec, n_rt, bad, cards


KEYS = ("t_gemm_s", "cycles_per_op", "cycles_gemm", "n_gemm", "n_launch_counted", "p_work_w", "p_rest_w", "die_start_c", "die_c", "mhz", "mhz_min",
        "mhz_max", "checks", "record", "block", "n")


def reduce_against(sd, refruns, keys=KEYS):
    """Each committed run (its detail's run key) through reduce_e222.reduce_run on the session's committed telemetry: (n, diffs)."""
    tel = RD.load_tel(sd)
    diffs, nr = [], 0
    for run in refruns:
        key = (run.get("detail") or {}).get("run")
        rj = os.path.join(sd, "runs", str(key), "run.json")
        if not key or not os.path.exists(rj):
            diffs.append(f"{key}: no run.json")
            continue
        mine = RD.reduce_run(os.path.join(sd, "runs", key), json.load(open(rj)), tel)
        nr += 1
        bad = [k for k in keys if k in run and mine.get(k) != run.get(k)]
        if bad:
            diffs.append(f"{key}: {bad[:4]}")
    return nr, diffs, len(tel)


def reduce_smoke_against(sd, refsmoke, keys=KEYS):
    """Each committed smoke RUN (its point's smoke.json) through reduce_run as the reducer reads a smoke: (n, diffs)."""
    tel = RD.load_tel(sd)
    diffs, nr = [], 0
    for run in refsmoke:
        pid = run.get("point")
        d = os.path.join(sd, "smoke", str(pid))
        sj = os.path.join(d, "smoke.json")
        if not os.path.exists(sj) or not os.path.exists(os.path.join(d, "proc.out")):
            diffs.append(f"{pid}: no smoke.json or proc.out")
            continue
        sm = json.load(open(sj))
        rec = {"run": f"smoke-{pid}", "n": run.get("n"), "block": "smoke", "id": pid, "flags": [],
               "procs": [{"name": "proc", "argv": sm.get("argv"), "rc": sm.get("rc"), "t0_ms": sm.get("t0_ms"), "t1_ms": sm.get("t1_ms")}]}
        mine = RD.reduce_run(d, rec, tel)
        nr += 1
        bad = [k for k in keys if k in run and mine.get(k) != run.get(k)]
        if bad:
            diffs.append(f"{pid}: {bad[:4]}")
    return nr, diffs


def splice_cases(text, argv, lines_to_splice, fam=None):
    base_f, base_c, base_i = C.host_records(text, argv)
    base_rt = C.runtime_cards(base_i["runtime_lines"])
    base_w = C.walk_check(fam, base_f, base_c)[0] if fam else None
    n1 = n2 = 0
    bad = []
    for which in lines_to_splice:
        for card in ("0", "1"):
            for k in range(len(which) + 1):
                sp = text.replace(which, which[:k] + f"Opening device {card}\n" + which[k:], 1)
                f_, c_, inf = C.host_records(sp, argv)
                n1 += 1
                if f_ != base_f or c_ != base_c or sorted(C.runtime_cards(inf["runtime_lines"])) != sorted(base_rt + [card]) or inf["unparsed"] or inf["mismatched"] or \
                        (fam and C.walk_check(fam, f_, c_)[0] != base_w):
                    bad.append(("single", card, k))
        outer = "Opening device 1\n"
        for j in (3, 9, 15, 16):
            pair = outer[:j] + "Opening device 0\n" + outer[j:]
            for k in range(0, len(which) + 1, 2):
                sp = text.replace(which, which[:k] + pair + which[k:], 1)
                f_, c_, inf = C.host_records(sp, argv)
                n2 += 1
                if f_ != base_f or c_ != base_c or sorted(C.runtime_cards(inf["runtime_lines"])) != sorted(base_rt + ["0", "1"]) or inf["unparsed"]:
                    bad.append(("nested", j, k))
    return n1, n2, bad, base_f


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rebuild_raw(sd, dst, home, login):
    """The box's own session bytes from a committed (scrubbed) session: every file copied; each whose sha256 is not its MANIFEST line gets the
    box's home and login put back ("~" -> home, "<login>" -> login) and must then read its MANIFEST sha256. (n files, n rebuilt, n masked-with-home,
    failures)."""
    man = {}
    for ln in open(os.path.join(sd, "MANIFEST.sha256")):
        if ln.strip():
            h, p = ln.rstrip("\n").split("  ", 1)
            man[p] = h
    shutil.copytree(sd, dst)
    nre, nhome, fails = 0, 0, []
    for p, h in man.items():
        fp = os.path.join(dst, p)
        if sha(fp) == h:
            continue
        raw = open(fp, "rb").read()
        gz = p.endswith(".gz")
        data = gzip.decompress(raw) if gz else raw
        cand = data.replace(b"<login>", login.encode()).replace(b"~", home.encode())
        if gz:
            fails.append(f"{p}: a .gz file scrubbed (not rebuilt here)")
            continue
        if hashlib.sha256(cand).hexdigest() != h:
            fails.append(f"{p}: rebuilt bytes not its MANIFEST line")
            continue
        open(fp, "wb").write(cand)
        nre += 1
        nhome += 1 if home.encode() in cand else 0
    return len(man), nre, nhome, fails


def scrub_compare(raw, committed, homes, login, work):
    """collect_e222's copy-back check on the rebuilt raw copy, then its scrub over a copy of it, compared with the committed session file for file."""
    cb = CO.copy_back_exact(raw)
    cp = os.path.join(work, "scrubbed")
    shutil.copytree(raw, cp)
    n, masked, left = CO.scrub_tree(cp, homes, login)
    diff = []
    for dp, dn, fn in os.walk(committed):
        for f in fn:
            a = os.path.join(dp, f)
            b = os.path.join(cp, os.path.relpath(a, committed))
            if not os.path.exists(b):
                diff.append(f"missing {os.path.relpath(a, committed)}")
                continue
            if f.endswith(".gz"):
                same = gzip.decompress(open(a, "rb").read()) == gzip.decompress(open(b, "rb").read())
            else:
                same = sha(a) == sha(b)
            if not same:
                diff.append(os.path.relpath(a, committed))
    return cb, n, masked, left, diff


def loops_of(path, arms=None):
    out = {}
    P = json.load(open(path))
    for arm_, A_ in P["arms"].items():
        if arms and arm_ not in arms:
            continue
        for q in A_["points"] + A_.get("references", []) + A_["smoke"] + [A_["tie"]]:
            out[q["id"]] = q["loop"]
    return out


def loops_of_flat(path):
    """E218's registration's form (points, smoke and tie at the top): {id: loop}"""
    P = json.load(open(path))
    return {q["id"]: q["loop"] for q in P["points"] + P["smoke"] + [P["tie"]]}


def walk_by_point(files, root, loops):
    """every rgm211-host process's walk read by its family, the family from the run's own point (the experiment's points file: its loop)"""
    walks, wbad = {}, []
    for p in files:
        pdir = os.path.dirname(p)
        argv = proc_argv(pdir, os.path.basename(p)[:-4]) or []
        j = json.load(open(os.path.join(pdir, "run.json" if os.path.exists(os.path.join(pdir, "run.json")) else "smoke.json")))
        pid = j.get("id") or os.path.basename(pdir)
        fam = loops.get(pid)
        if fam is None:
            wbad.append(f"{os.path.relpath(p, root)}: no point {pid}")
            continue
        host = "rgm211" if "/rgm211/host/" in (argv[0] if argv else "") else "rgm136"
        kern = "rgm211" if "/rgm211/kernel/" in str(C.arg_of(argv, "--kernel")) else "rgm136"
        if (host, kern) != (LOOPS_READ[fam]["host"], LOOPS_READ[fam]["elf"]):
            wbad.append(f"{os.path.relpath(p, root)}: host {host}, ELF {kern}, family {fam}")
            continue
        if LOOPS_READ[fam]["host"] != "rgm211":
            continue
        fma, chk, _ = C.host_records(open(p).read(), argv)
        if fam in C.LOOPS:           # E222's two families: by E222's own walk check
            ok, words, _ = C.walk_check(fam, fma, chk)
        else:                        # the other two (E215's and E213's only): their walk read against the family's own want
            want = LOOPS_READ[fam]["walk"]
            ok = bool(fma) and all(x.get("walk") == want and x.get("walk_ok") is True for x in fma) and bool(chk) and chk[-1].get("walk_launches_bad") == 0
            words = f"walk {want}" if ok else "walk not as its family's"
        walks[fam] = walks.get(fam, 0) + (1 if ok else 0)
        if not ok:
            wbad.append(f"{os.path.relpath(p, root)}: {words[:80]}")
    return walks, wbad


def runs_of_data(ref):
    out = []
    for r in [r for P in ref["points"].values() for r in P["runs"]] + list(ref["ties"]["runs"]):
        rr = dict(r)
        w = r.get("walk")
        if w is not None:
            rr["walk_names"], rr["walk_ok"], rr["walk_launches_bad"] = w.get("names"), w.get("ok"), w.get("launches_bad")
        out.append(rr)
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    S = os.path.abspath(sys.argv[1])
    if S == REPO or S.startswith(REPO + os.sep):
        print("the scratch directory must be outside the repository")
        return 2
    os.makedirs(S, exist_ok=True)
    t = T()
    print(f"realbytes_e222 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; reading the committed data of "
          f"<lab clone>/docs/reports/data (read only); the scrub cases in a scratch folder", flush=True)
    sd18, sd15, sd13, sd11, sd7, sd6 = (os.path.join(x, "session") for x in (E218D, E215A, E213A, E211D, E207D, E206B))
    WK = KEYS + ("walk_names", "walk_ok", "walk_launches_bad")
    # ---- RB-E218A and RB-E218AR (E218's day on this card, 03:11-03:56 PST Fri 20 Nov 2026: E222's two families, its kit's own form)
    f18 = outs(sd18)
    n_rec, n_rt, bad, cards = parse_all(f18, E218D)
    walks, wbad = walk_by_point(f18, E218D, loops_of_flat(P218))
    masks = {C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [], "--shires") for p in f18}
    t.case("RB-E218A", len(f18) >= 100 and not bad and not wbad and walks.get("rgm136 gemmLnc", 0) >= 20 and len(masks) >= 2,
           f"{len(f18)} committed aifoundry3 card-0 stdouts of E218 (both hosts, masks {len(masks)}), {n_rec} records read against each process's "
           f"own command line; {n_rt} runtime lines; the walk by the run's own family on every rgm211-host process: {walks}"
           f"{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref18 = json.load(open(os.path.join(E218D, "data-e218.json")))["arms"]["A"]
    runs18 = runs_of_data(ref18)
    nr, diffs, nt = reduce_against(sd18, runs18, WK)
    ns, sdiffs = reduce_smoke_against(sd18, ref18["smoke"]["runs"], WK)
    s03 = [r for r in ref18["smoke"]["runs"] if r.get("point") == "s03"]
    t.case("RB-E218AR", nr == len(runs18) and nr >= 100 and not diffs and ns == len(ref18["smoke"]["runs"]) == 2 and not sdiffs
           and s03 and s03[0].get("n") == 84,
           f"{nr} of E218's committed runs and {ns} smoke processes: reduce_e222.reduce_run gives data-e218.json's run and walk fields equal "
           f"({'equal' if not diffs and not sdiffs else 'DIFFER: ' + '; '.join((diffs + sdiffs)[:4])}); the gemmLnc smoke s03 at place "
           f"{s03[0].get('n') if s03 else None}; {nt} committed samples read")
    # ---- RB-E215A and RB-E215AR (on Thu 19 Nov 2026's day on this card: E222's two families among four, the gemmLnc smoke in its place)
    f15 = outs(sd15)
    n_rec, n_rt, bad, cards = parse_all(f15, E215A)
    walks, wbad = walk_by_point(f15, E215A, loops_of(P215, ("A",)))
    masks = {C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [], "--shires") for p in f15}
    t.case("RB-E215A", len(f15) >= 100 and not bad and not wbad and walks.get("rgm136 gemmLnc", 0) >= 5 and len(masks) >= 2,
           f"{len(f15)} committed aifoundry3 card-0 stdouts of E215 arm A (both hosts, masks {len(masks)}), {n_rec} records read against each process's "
           f"own command line; {n_rt} runtime lines; the walk by the run's own family on every rgm211-host process: {walks}"
           f"{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref15 = json.load(open(os.path.join(E215A, "data-e215.json")))["arms"]["A"]
    runs15 = runs_of_data(ref15)
    nr, diffs, nt = reduce_against(sd15, runs15, WK)
    ns, sdiffs = reduce_smoke_against(sd15, ref15["smoke"]["runs"], WK)
    s03 = [r for r in ref15["smoke"]["runs"] if r.get("point") == "s03"]
    t.case("RB-E215AR", nr == len(runs15) and nr >= 100 and not diffs and ns == len(ref15["smoke"]["runs"]) == 4 and not sdiffs
           and s03 and s03[0].get("n") == 112,
           f"{nr} of E215 arm A's committed runs and {ns} smoke processes: reduce_e222.reduce_run gives data-e215.json's run and walk fields equal "
           f"({'equal' if not diffs and not sdiffs else 'DIFFER: ' + '; '.join((diffs + sdiffs)[:4])}); the gemmLnc smoke s03 at place "
           f"{s03[0].get('n') if s03 else None}; {nt} committed samples read")
    # ---- RB-E213A and RB-E213AR
    f13 = outs(sd13)
    n_rec, n_rt, bad, cards = parse_all(f13, E213A)
    walks, wbad = walk_by_point(f13, E213A, loops_of(P213, ("A",)))
    t.case("RB-E213A", len(f13) >= 100 and not bad and not wbad and walks.get("rgm136 gemmLnc", 0) > 0,
           f"{len(f13)} committed aifoundry3 card-0 stdouts of E213 arm A, {n_rec} records read; {n_rt} runtime lines; the walk by the run's own family: "
           f"{walks}{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref13 = json.load(open(os.path.join(E213A, "data-e213.json")))["arms"]["A"]
    runs13 = runs_of_data(ref13)
    nr, diffs, nt = reduce_against(sd13, runs13, WK)
    t.case("RB-E213AR", nr == len(runs13) and nr >= 100 and not diffs, f"{nr} of E213 arm A's committed runs: reduce_run gives data-e213.json's run "
           f"and walk fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E211 and RB-E211R (both hosts, the walk)
    f11 = outs(sd11)
    n_rec, n_rt, bad, cards = parse_all(f11, E211D)
    walks, wbad = {}, []
    for p in f11:
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or []
        tok = C.arg_of(argv, "--values").split(":")[0]
        host = "rgm211" if "/rgm211/host/" in argv[0] else "rgm136"
        if host != "rgm211" or not tok.startswith("gemmLnc"):
            continue
        fma, chk, _ = C.host_records(open(p).read(), argv)
        ok, words, _ = C.walk_check("rgm136 gemmLnc", fma, chk)
        walks["rgm136 gemmLnc"] = walks.get("rgm136 gemmLnc", 0) + (1 if ok else 0)
        if not ok:
            wbad.append(f"{os.path.relpath(p, E211D)}: {words[:80]}")
    t.case("RB-E211", len(f11) >= 40 and not bad and not wbad and walks.get("rgm136 gemmLnc", 0) > 0,
           f"{len(f11)} committed aifoundry3 stdouts of E211, both hosts, {n_rec} records read; E222's walk check on every gemmLnc process of rgm211's "
           f"host: {walks}{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref11 = json.load(open(os.path.join(E211D, "data-e211.json")))["arms"]["A"]
    runs11 = []
    for r in ref11["runs"]:
        rr = dict(r)
        w = r.get("walk")
        if w is not None:
            rr["walk_names"], rr["walk_ok"], rr["walk_launches_bad"] = w.get("names"), w.get("ok"), w.get("launches_bad")
        runs11.append(rr)
    nr, diffs, nt = reduce_against(sd11, runs11, KEYS[:3] + ("p_work_w", "p_rest_w", "die_start_c", "mhz_min", "mhz_max", "checks", "record", "block",
                                                          "n", "walk_names", "walk_ok", "walk_launches_bad"))
    t.case("RB-E211R", nr == len(runs11) and nr >= 30 and not diffs, f"{nr} of E211's committed runs (both hosts): reduce_run gives data-e211.json's "
           f"fields and walk fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E207 and RB-E207R
    f7 = outs(sd7)
    n_rec, n_rt, bad, cards = parse_all(f7, E207D)
    masks = {C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [], "--shires") for p in f7}
    t.case("RB-E207", len(f7) >= 100 and not bad and n_rec > 0 and len(masks) >= 2,
           f"{len(f7)} committed aifoundry3 card-0 stdouts of E207 (masks {sorted(masks)}), {n_rec} records read, each against its own command line; "
           f"{n_rt} runtime lines{'; ' + '; '.join(bad[:3]) if bad else ''}")
    ref7 = json.load(open(os.path.join(E207D, "data-e207.json")))["arms"]["A"]
    runs7 = [r for P in ref7["points"].values() for r in P["runs"]] + list(ref7["ties"]["runs"])
    nr, diffs, nt = reduce_against(sd7, runs7)
    t.case("RB-E207R", nr == len(runs7) and nr >= 100 and not diffs, f"{nr} of E207's committed runs: reduce_e222.reduce_run gives data-e207.json's run "
           f"fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-SPLICE: E215 arm A's gemmLnc records of rgm211's host (the walk inside) and an rgm136-host record
    n1 = n2 = 0
    sbad = []
    lnc = [p for p in f15 if "/rgm211/host/" in (proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [""])[0]
           and str(C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]), "--values")).startswith("gemmLnc")]
    g136 = [p for p in f15 if "/rgm136/host/" in (proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [""])[0]]
    for p, fam in ((lnc[0] if lnc else None, "rgm136 gemmLnc"), (g136[len(g136) // 2] if g136 else None, None)):
        if not p:
            sbad.append("no stdout of that form")
            continue
        text = open(p).read()
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4])
        lines = [ln for ln in text.split("\n") if ln.startswith("SPARSITY ")]
        a, b2, bad, _ = splice_cases(text, argv, (lines[1], lines[-1]), fam)
        n1 += a
        n2 += b2
        sbad += bad
    t.case("RB-SPLICE", not sbad and n1 > 1500 and n2 > 1500,
           f"{n1} single and {n2} nested runtime-line splices into a real gemmLnc launch and check record of rgm211's host (E215 arm A, the walk inside) "
           f"and a real rgm136-host record of E215 arm A's: every one read the same records and the same walk{'; bad ' + str(sbad[:4]) if sbad else ''}")
    # ---- RB-CFG
    ok_all, words = True, []
    for label, sd in (("E215 arm A", sd15), ("E213 arm A", sd13)):
        cj = json.load(open(os.path.join(sd, "config-start.json")))
        line = [ln for ln in open(os.path.join(sd, "config-start.out")).read().splitlines() if ln.startswith("{")][-1]
        ok = all(C.config_json(line[:k] + f"Opening device {c}\n" + line[k:] + "\n") == cj for k in range(len(line) + 1) for c in ("0", "1"))
        ok = ok and C.config_json("Opening device 0\n" + line + "\n") == cj and C.config_json(line[:40] + "\n") == {} and C.config_ok("A", cj)
        ok_all &= ok
        words.append(f"{label}'s committed config line ({len(line) + 1} offsets x 2 cards): {ok}")
    cj6 = json.load(open(os.path.join(sd6, "config-start.json")))
    refuse6 = not C.config_ok("A", cj6)
    t.case("RB-CFG", ok_all and refuse6, "; ".join(words) + f" (each passes the start config gate); E206 arm B's card-1 config (TDP {cj6.get('tdp_w')} W) refused: {refuse6}")
    # ---- RB-ID
    def cfg(d, name="config-start"):
        return json.load(open(os.path.join(d, name + ".json"))), open(os.path.join(d, name + ".err"), errors="replace").read()
    rows = []
    for nm in ("config-start", "config-end"):
        for label, sd in (("E215 arm A", sd15), ("E213 arm A", sd13), ("E211", sd11), ("E207", sd7)):
            j, err = cfg(sd, nm)
            rows.append((f"{label} {nm}", j, err, True))
            rows.append((f"{label} {nm} with its block removed", j,
                         "\n".join(x for x in err.splitlines() if not x.startswith(("PCIe target", "Physical device ID"))), False))
        j, err = cfg(sd6, nm)
        rows.append((f"E206 arm B {nm} (card 1)", j, err, False))
    bad = [r[0] for r in rows if (N1.config_identity("A", r[1], r[2]) == "") != r[3]]
    hosts = []
    for pid in ("s01", "s03"):
        ep = os.path.join(sd15, "smoke", pid, "proc.err")
        if os.path.exists(ep):
            tg, ids = N1.parse_ident(open(ep, errors="replace").read())
            w, r = N1.host_identity("A", tg, ids, set())
            hosts.append(not w and r)
    t.case("RB-ID", not bad and len(rows) == 18 and len(hosts) == 2 and all(hosts),
           f"{len(rows)} committed config forms, each passed or refused as stated ({'none wrong' if not bad else 'WRONG: ' + '; '.join(bad[:4])}); "
           f"E215 arm A's smoke host blocks s01 (rgm136's host) and s03 (rgm211's) read as card 0's: {hosts}")
    # ---- RB-SIM: rgm211's host's real simulator bytes
    bad, nrec, seen = [], 0, {}
    for case in sorted(os.listdir(SIM)) if os.path.isdir(SIM) else []:
        if not case.endswith(".out"):
            continue
        c = case[:-4]
        meta = json.load(open(os.path.join(SIM, c + ".json")))
        text = open(os.path.join(SIM, case)).read()
        argv = meta["argv"]
        fma, chk, info = C.host_records(text, argv)
        plain = [r for r in plain_parse(text) if r.get("test") in ("fma", "check")]
        nrec += len(fma) + len(chk)
        if by_time(fma + chk) != by_time(plain) or info["unparsed"] or info["mismatched"] or not fma or not chk:
            bad.append(f"{c}: {len(fma) + len(chk)} of {len(plain)} records")
            continue
        seen[c] = True
        if c == "C":
            ok, words, det = C.walk_check("rgm136 gemmLnc", fma, chk)
            if not ok or det.get("names") != ["mn"] * len(fma) or any(det.get("tagged")):
                bad.append(f"C: walk read {ok} ({words[:80]})")
            seen["C-walk"] = ok
    t.case("RB-SIM", not bad and seen.get("C-walk") is True and len(seen) >= 8,
           f"{len([k for k in seen if not k.endswith('-walk')])} simulator stdouts of the two hosts built on aifoundry3 (E211's kit), {nrec} records read "
           f"whole against their command lines; the gemmLnc case C (rgm136's ELF on rgm211's host) by E222's walk check: {seen.get('C-walk')}"
           f"{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-SMOKE: the runner's smoke reading = the reducer's R0 reading, inside R0's band, on real smoke bytes
    rows, sbad = [], []
    for label, sd in (("E218", sd18), ("E215A", sd15), ("E213A", sd13), ("E211", sd11), ("E207", sd7)):
        for pdir in sorted(glob.glob(os.path.join(sd, "smoke", "*"))):
            p = os.path.join(pdir, "proc.out")
            if not os.path.exists(p):
                continue
            argv = proc_argv(pdir, "proc")
            fma, chk, _ = C.host_records(open(p).read(), argv)
            runner = statistics.median([x["cycles_per_op"] for x in fma if C.counted(x) and x.get("cycles_per_op") is not None]) \
                if any(C.counted(x) and x.get("cycles_per_op") is not None for x in fma) else None
            sm = json.load(open(os.path.join(pdir, "smoke.json")))
            rec = {"run": "smoke", "n": -1, "block": "smoke", "id": "s01", "flags": [],
                   "procs": [{"name": "proc", "argv": argv, "rc": sm.get("rc"), "t0_ms": sm.get("t0_ms"), "t1_ms": sm.get("t1_ms")}]}
            red = RD.reduce_run(pdir, rec, [])["cycles_per_op"]
            rows.append((label, os.path.basename(pdir), runner))
            if runner is None or red != runner or not (C.SMOKE_CYC[0] <= runner <= C.SMOKE_CYC[1]):
                sbad.append(f"{label} {os.path.basename(pdir)}: runner {runner}, reducer {red}")
            if label in ("E218", "E215A") and sm.get("counted_cycles_per_op") is not None and sm.get("counted_cycles_per_op") != runner:
                sbad.append(f"{label} {os.path.basename(pdir)}: the committed runner reading {sm.get('counted_cycles_per_op')} is not {runner}")
    t.case("RB-SMOKE", rows and not sbad and len(rows) >= 16,
           f"{len(rows)} committed smoke processes: the runner's smoke reading (the median over its counted launches) equals the reducer's (R0's), "
           f"each in R0's 200-4,000 (E218's and E215 arm A's equal to their runner's committed reading): {[(a, b, round(c, 1) if c else c) for a, b, c in rows]}"
           f"{'; ' + '; '.join(sbad[:3]) if sbad else ''}")
    # ---- RB-SCRUB: the collection's scrub on the box's own records (the home in them)
    login = pwd.getpwuid(os.getuid()).pw_name
    home = pwd.getpwuid(os.getuid()).pw_dir.rstrip("/")
    sc_ok, words = True, []
    for label, sd in (("E218 aifoundry3", sd18), ("E215-armA aifoundry3", sd15), ("E213-armA aifoundry3", sd13), ("E211 aifoundry3", sd11),
                      ("E207 aifoundry3", sd7)):
        w = os.path.join(S, "scrub-" + label.split()[0])
        if os.path.exists(w):
            shutil.rmtree(w)
        os.makedirs(w)
        raw = os.path.join(w, "raw")
        n, nre, nh, fails = rebuild_raw(sd, raw, home, login)
        cb, nn, masked, left, diff = scrub_compare(raw, sd, [home], login, w)
        ok = not fails and nre > 10 and nh > 10 and not cb and not left and not diff and masked == nre
        sc_ok &= ok
        words.append(f"{label}: {n} files, {nre} rebuilt to the box's own bytes (each at its MANIFEST sha256; {nh} hold the home), COPY-BACK "
                     f"{'EXACT' if not cb else 'NOT EXACT'}, the scrub masked {masked}, left {len(left)}, differs from the committed session in {len(diff)}"
                     + (f" ({fails[:2]} {diff[:2]})" if fails or diff else ""))
    # the homes in three forms, and a home not given
    w = os.path.join(S, "scrub-forms")
    if os.path.exists(w):
        shutil.rmtree(w)
    os.makedirs(os.path.join(w, "phys", "realhome"))
    os.symlink(os.path.join(w, "phys", "realhome"), os.path.join(w, "linkhome"))
    lh, ph = os.path.join(w, "linkhome"), os.path.join(w, "phys", "realhome")
    dbh = "/srv/standin-userdb-home"
    sess = os.path.join(w, "sess")
    os.makedirs(sess)
    open(os.path.join(sess, "session.log"), "w").write(f"a {lh}/aifoundry/build/e222 b {ph}/aifoundry/x c {dbh}/.local/state d {login}\n")
    open(os.path.join(sess, "x.json"), "w").write(json.dumps({"argv": [f"{ph}/aifoundry/build/e222rgm/rgm211/host/sparsity_host"]}) + "\n")
    hf = os.path.join(w, "homes-3.txt")
    open(hf, "w").write(f"{lh}\n{dbh}\n{ph}\n")
    lf = os.path.join(w, "login.txt")
    open(lf, "w").write(login + "\n")
    r3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "scrub-check", sess, hf, lf], capture_output=True, text=True)
    hf1 = os.path.join(w, "homes-1.txt")
    open(hf1, "w").write(f"{lh}\n")
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "scrub-check", sess, hf1, lf], capture_output=True, text=True)
    unchanged = open(os.path.join(sess, "session.log")).read().count(dbh) == 1
    forms_ok = r3.returncode == 0 and "SCRUB-CHECK CLEAN: 2 files, 2 held a home path" in r3.stdout and r1.returncode == 3 and \
        "SCRUB-CHECK LEFT" in r1.stdout and unchanged
    t.case("RB-SCRUB", sc_ok and forms_ok,
           "; ".join(words) + f"; the home in three forms (a symlinked home, its physical path, the user database's): scrub-check rc {r3.returncode} "
           f"'{r3.stdout.strip()[:60]}'; with the first form alone: rc {r1.returncode} '{r1.stdout.strip()[:40]}...' (refused, never silent); the "
           f"checked folder unchanged {unchanged}")
    # ---- RB-HOLDERS: another login's holder lines at the collection (made-up logins only)
    w = os.path.join(S, "scrub-holders")
    if os.path.exists(w):
        shutil.rmtree(w)
    cp = os.path.join(w, "copy")
    os.makedirs(os.path.join(cp, "reads"))
    real = os.path.join(sd15, "reads", "etwho-001-tie-t01.out")
    committed = open(real, "rb").read()
    ours = committed.replace(b"<login>", b"e222us").replace(b"~/", b"/home/e222us/")
    other = (b"/dev/et0_ops   e222other    204411        3:07 ./build/bench/somebench --card 0 --iters 100\n"
             b"lock:etsoc-shire0.lock e222other    204400        3:08 /home/e222other/work/somebench --card 0\n")
    open(os.path.join(cp, "reads", "etwho-002-pass1-y06b.out"), "wb").write(ours + other)
    open(os.path.join(cp, "queue.json"), "w").write('{"queue": [{"ran": false}]}\n')
    open(os.path.join(cp, "session.log"), "w").write("a stand-in session\n")

    def manifest(d):
        rows_ = []
        for dp, dn, fn in os.walk(d):
            for n_ in fn:
                rel = os.path.relpath(os.path.join(dp, n_), d)
                if rel != "MANIFEST.sha256":
                    rows_.append(f"{hashlib.sha256(open(os.path.join(dp, n_), 'rb').read()).hexdigest()}  {rel}")
        open(os.path.join(d, "MANIFEST.sha256"), "w").write("\n".join(sorted(rows_, key=lambda x: x[66:])) + "\n")
    manifest(cp)
    hf, lf = os.path.join(w, "homes.txt"), os.path.join(w, "login.txt")
    open(hf, "w").write("/home/e222us\n")
    open(lf, "w").write("e222us\n")
    before = {f: hashlib.sha256(open(os.path.join(cp, f), "rb").read()).hexdigest() for f in os.listdir(cp) if os.path.isfile(os.path.join(cp, f))}
    rc1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "scrub-check", cp, hf, lf], capture_output=True, text=True)
    after = {f: hashlib.sha256(open(os.path.join(cp, f), "rb").read()).hexdigest() for f in os.listdir(cp) if os.path.isfile(os.path.join(cp, f))}
    outd = os.path.join(w, "out")
    os.makedirs(outd)
    rc2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "data", "2026-11-20", "A", cp, hf, lf, "--outside", outd],
                         capture_output=True, text=True, env=dict(os.environ, RB_DESKTEST="1"))
    named, homes_left, got = [], [], b""
    for dp, dn, fn in os.walk(outd):
        for n_ in fn:
            b = open(os.path.join(dp, n_), "rb").read()
            if b"e222other" in b or b"e222us" in b:
                named.append(n_)
            if b"/home/" in b:
                homes_left.append(n_)
            if n_ == "etwho-002-pass1-y06b.out":
                got = b
    gl = got.split(b"\n")
    our_lines = [x for x in committed.split(b"\n") if x]
    masked_ok = (gl[:len(our_lines)] == our_lines and gl[len(our_lines)] == b"/dev/et0_ops   <another-login>  204411  3:07"
                 and gl[len(our_lines) + 1] == b"lock:etsoc-shire0.lock <another-login>  204400  3:08")
    open(os.path.join(cp, "reads", "holders.bin"), "wb").write(other)
    manifest(cp)
    rc3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "scrub-check", cp, hf, lf], capture_output=True, text=True)
    outd2 = os.path.join(w, "out2")
    os.makedirs(outd2)
    rc4 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e222.py"), "data", "2026-11-20", "A", cp, hf, lf, "--outside", outd2],
                         capture_output=True, text=True, env=dict(os.environ, RB_DESKTEST="1"))
    t.case("RB-HOLDERS", rc1.returncode == 0 and rc1.stdout.startswith("SCRUB-CHECK CLEAN: ") and before == after and rc2.returncode == 0
           and "COLLECTED-GATE-STOP " in rc2.stdout and not named and not homes_left and masked_ok
           and rc3.returncode == 3 and "SCRUB-CHECK LEFT" in rc3.stdout and "holders.bin" in rc3.stdout
           and rc4.returncode == 3 and "SCRUB FAILED" in rc4.stdout and "holders.bin" in rc4.stdout,
           f"E215 arm A's committed et-who record with a made-up login of ours and two lines of a made-up other login on card 0: scrub-check rc "
           f"{rc1.returncode} '{rc1.stdout.strip()[:60]}' (the checked copy unchanged {before == after}); collected rc {rc2.returncode}; files naming "
           f"either made-up login after it {len(named)}, holding a home path {len(homes_left)}; the other login's lines masked, its commands dropped and ours "
           f"byte-identical to the committed record {masked_ok}; a holder line in a .bin: scrub-check rc {rc3.returncode} "
           f"('{rc3.stdout.strip()[:40]}...'), the collection rc {rc4.returncode} ('{rc4.stdout.strip().splitlines()[-1][:12] if rc4.stdout.strip() else ''}...')")
    print(f"REALBYTES-E222 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main())
