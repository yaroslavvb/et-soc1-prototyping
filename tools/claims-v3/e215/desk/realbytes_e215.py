#!/usr/bin/env python3
"""E215's REAL-BYTES desk test (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum; CONTEXT section 116's lesson: "every kit reads a
host's result from a source no runtime print can split ... and its real-path desk test feeds the parser the REAL stdout bytes committed from a
card"; E209's lesson: a collection's scrub must meet records that carry the box's home BEFORE the session). Every parser, reducer path, identity
reader and the collection's scrub of E215's kit, fed bytes committed from the two cards E215 uses, read-only (nothing here writes in the repo; the
scrub cases write only under the scratch folder given). E213's desk/realbytes_e213.py (landed in 6efdb002) for E215's two arms, WITH THE BYTES OF
THE LAB'S LATEST DAYS ON BOTH CARDS (the round's lesson for this kit: every host-output parser fed real committed bytes - E213 arm A on aifoundry3,
E213 arm B and E214 on card 1):

  RB-E213A  E213 arm A's committed outputs on aifoundry3 card 0 (docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/, c69a12aa: ALL FOUR
            FAMILIES on their two hosts, the smoke s01-s04, subset masks) through e215_common.host_records with each process's own committed
            command line: every record read, none unparsed or naming another command; every rgm211-host process's walk read by its family from
            the run's own point (points-e213.json's loop: 'rgm211 gemmLn' nm; 'rgm136 gemmLnc' and 'rgm211 gemmL' mn) and good;
  RB-E213AR E213 arm A's committed runs through reduce_e215.reduce_run (E213's reducer, line for line, with the gemmLnc smoke's place added) against
            its committed data-e213.json: every run field and walk field equal;
  RB-E213B  E213 arm B's committed card-1 outputs (docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/, b0c727c5: rgm136's host and
            rgm211's host with rgm136's ELF, aifoundry1's runtime lines on the hosts' stdout) through host_records: every record read, every
            runtime line dropped and counted, card 1's; the gemmLnc processes' walk mn and good;
  RB-E213BR E213 arm B's committed runs through reduce_run against its committed data-e213.json (arm B): equal;
  RB-E214   E214's committed card-1 sessions (the model session's runner and host build on aifoundry1, 18 Nov 2026: docs/reports/data/2026-11-18-e214-
            mmsweep3-a1c1-S1 ... S4) through host_records with each process's own committed command line: every record read, none unparsed or
            naming another command, card 1's runtime lines dropped and counted;
  and, as E213's kit read them (kept: the same two cards, the same hosts' forms):

  RB-E207   E207's committed rgm136 outputs on aifoundry3 card 0 (docs/reports/data/2026-11-17-e207-blind-matmul-aifoundry3/: the smoke's and the
            runs' stdouts, its shire masks among them) through e215_common.host_records with each process's own committed command line: every
            record a plain reader reads is read, none unparsed, none naming another command, every runtime line counted;
  RB-E207R  E207's committed session's runs through reduce_e215.reduce_run: every run's t_gemm_s, cycles_per_op, cycles_gemm, n_gemm,
            n_launch_counted, p_work_w, p_rest_w, die_start_c, die_c, mhz, mhz_min, mhz_max, checks, record, block and n EQUAL to E207's committed
            data-e207.json;
  RB-E211   E211's committed outputs on aifoundry3 card 0, BOTH HOSTS (rgm136's and rgm211's real card bytes, rgm211's with its walk fields):
            every record read, and every rgm211-host process's walk read by its family (gemmLn: 'rgm211 gemmLn', nm; gemmLnc: 'rgm136 gemmLnc', mn)
            as E211's runner and scorer read it (walk_ok true on every launch, walk_launches_bad 0);
  RB-E211R  E211's committed runs through reduce_run (its walk fields among them) against E211's committed data-e211.json: equal;
  RB-E206B  E206 arm B's committed card-1 outputs (docs/reports/data/2026-11-17-e206-matmul-sweep-aifoundry1-c1/: aifoundry1's runtime prints
            "Opening device 1" on the host's stdout) through host_records: every record read, every runtime line dropped and counted, card 1's;
  RB-E206BR E206 arm B's committed runs through reduce_run against E206's committed data-e206.json (arm B): equal;
  RB-E212   E212's committed card-1 sessions (the model session's runner, its own host build on aifoundry1: docs/reports/data/2026-11-17-e212-
            mmsweep2-a1c1-S1 ... S4) through host_records with each process's own committed command line: every record read, none unparsed or
            naming another command, card 1's runtime lines dropped and counted;
  RB-SPLICE runtime lines (cards 0 and 1, and a nested pair) spliced into REAL records at every byte offset: an rgm211-host launch record and
            check record of E211's (the walk fields inside them) and a card-1 record of E206 arm B's: each reads the same records and the same walk;
  RB-CFG    config_json on each arm's committed config line (E207's aifoundry3 config-start.out, E206 arm B's card-1 one) with runtime lines before,
            after and inside it: the committed config-start.json each time; config_ok passes each on its own arm and refuses it on the other;
  RB-ID     THE CARD'S IDENTITY GATE on committed forms, per arm: arm A passes aifoundry3's committed reads (E207's, E211's) and refuses card 1's;
            arm B passes card 1's committed reads (E206 arm B's, 499-500 mV) and refuses aifoundry3's, card 0's 519 mV and a read with its block
            removed; the committed host blocks (E211's smoke on card 0, E206 arm B's smoke on card 1) read by host_identity per arm;
  RB-SIM    rgm211's host's REAL simulator bytes (E211's committed logs/simcheck: its kit's sys_emu runs on aifoundry3, the home written "~"), each
            through host_records against its own command line and walk_check BY E215'S FAMILY: gemmLn cases read OK as 'rgm211 gemmLn'; gemmLnc on
            rgm136's ELF OK as 'rgm136 gemmLnc'; THE NEW FAMILY's own bytes, case N (gemmL on rgm211's host and rgm211's ELF), read OK as 'rgm211
            gemmL' (walk mn, the tag on none, walk_ok true, walk_launches_bad 0); the wrong-ELF case BAD (gemmLn on rgm136's ELF) NOT OK;
  RB-SMOKE  the smoke's reading on real bytes: each committed smoke process of E207, E211 and E206 arm B read the way the runner's smoke gate reads it
            (the median cycles_per_op over its counted launches, run_e215's counted_cycles_per_op) and the way the reducer hands it to the frozen
            scorer's R0 (reduce_e215.scorer_run's cycles_per_op): equal, and inside R0's band of 200-4,000;
  RB-SCRUB  THE COLLECTION'S SCRUB ON REAL RECORDS THAT CARRY THE BOX'S HOME (E209's lesson): E211's (aifoundry3), E207's (aifoundry3) and E206 arm
            B's (aifoundry1) committed sessions turned back into the box's own bytes (each committed file whose sha256 is not its MANIFEST line
            has "~" and "<login>" put back as the box's home and login, and must then read its MANIFEST sha256 exactly: the box's raw record, the
            home in it at every place the box wrote one), then collect_e215.copy_back_exact (COPY-BACK EXACT) and collect_e215's scrub over a copy:
            every file byte-identical to the committed session, none left with a home or the login; the same with the home given in three forms
            (a stand-in physical path through a symlink, the user database's) and a record holding a home NOT given: the scrub refuses it
            (SCRUB-CHECK LEFT) - never silently. The box login and home used to rebuild the raw bytes are this desk's (the same login on the
            three boxes); they are written only in the scratch folder, never in a log line.
  RB-HOLDERS (fix-e213, verify-e213's finding 2) ANOTHER LOGIN'S et-who HOLDER LINES AT THE COLLECTION: E206 arm B's committed card-1 et-who record
            (session/reads/etwho-001-tie-p001.out) turned back into a box's bytes with a MADE-UP login of ours ("e215us", its home /home/e215us)
            and two lines of a MADE-UP other login ("e215other") holding card 0 appended - one whose command names no home, one whose command
            names its own /home/... - in a stand-in session copy: collect_e215.py scrub-check reads CLEAN (the checked folder unchanged), and the
            data collection (desk mode) COLLECTED, with no collected file naming the other login or holding a /home/ path, both of its lines
            "<another-login>" with their pid and time and no command, and our own two lines byte-identical to the committed record; then the same
            holder line in a file the scrub does not rewrite (a .bin): SCRUB-CHECK LEFT (exit 3) and SCRUB FAILED (exit 3) - refused, never silent.
    /usr/bin/python3 -I -B tools/claims-v3/e215/desk/realbytes_e215.py <scratch dir> > logs/realbytes-e215.txt   (last line: REALBYTES-E215 <n> of <m> PASS)
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
import e215_common as C  # noqa: E402
import e215_ident as N1  # noqa: E402
import reduce_e215 as RD  # noqa: E402
import collect_e215 as CO  # noqa: E402

DATA = os.path.join(REPO, "docs/reports/data")
E213A = os.path.join(DATA, "2026-11-18-e213-blind-matmul-aifoundry3")
E213B = os.path.join(DATA, "2026-11-18-e213-blind-matmul-aifoundry1-c1")
E214 = sorted(glob.glob(os.path.join(DATA, "2026-11-18-e214-mmsweep3-a1c1-S*")))
P213 = os.path.join(REPO, "tools/claims-v3/e213/points-e213.json")
E207D = os.path.join(DATA, "2026-11-17-e207-blind-matmul-aifoundry3")
E211D = os.path.join(DATA, "2026-11-17-e211-second-kernel-aifoundry3")
E206B = os.path.join(DATA, "2026-11-17-e206-matmul-sweep-aifoundry1-c1")
E212 = sorted(glob.glob(os.path.join(DATA, "2026-11-17-e212-mmsweep2-a1c1-S*")))
SIM = os.path.join(REPO, "tools/claims-v3/e211/logs/simcheck")


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
    """Each committed run (its detail's run key) through reduce_e215.reduce_run on the session's committed telemetry: (n, diffs)."""
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


def splice_cases(text, argv, lines_to_splice, fam=None):
    base_f, base_c, base_i = C.host_records(text, argv)
    base_rt = C.runtime_cards(base_i["runtime_lines"])          # a card-1 stdout carries aifoundry1's own runtime line already
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
    """collect_e215's copy-back check on the rebuilt raw copy, then its scrub over a copy of it, compared with the committed session file for file."""
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
    print(f"realbytes_e215 ({sys.executable} {sys.version.split()[0]}), {time.strftime('%Y-%m-%d %H:%M:%S %Z')}; reading the committed data of "
          f"<lab clone>/docs/reports/data (read only); the scrub cases in a scratch folder", flush=True)
    sd7, sd11, sd6 = os.path.join(E207D, "session"), os.path.join(E211D, "session"), os.path.join(E206B, "session")
    sd13a, sd13b = os.path.join(E213A, "session"), os.path.join(E213B, "session")
    loop213 = {}
    for arm_, A_ in json.load(open(P213))["arms"].items():
        for q in A_["points"] + A_["smoke"] + [A_["tie"]]:
            loop213[q["id"]] = q["loop"]

    def walk_by_point(files, root):
        """every rgm211-host process's walk read by its family, the family from the run's own point (E213's points file: its loop)"""
        walks, wbad = {}, []
        for p in files:
            pdir = os.path.dirname(p)
            argv = proc_argv(pdir, os.path.basename(p)[:-4]) or []
            j = json.load(open(os.path.join(pdir, "run.json" if os.path.exists(os.path.join(pdir, "run.json")) else "smoke.json")))
            pid = j.get("id") or os.path.basename(pdir)
            fam = loop213.get(pid)
            if fam is None:
                wbad.append(f"{os.path.relpath(p, root)}: no point {pid}")
                continue
            host = "rgm211" if "/rgm211/host/" in (argv[0] if argv else "") else "rgm136"
            kern = "rgm211" if "/rgm211/kernel/" in str(C.arg_of(argv, "--kernel")) else "rgm136"
            if (host, kern) != (C.LOOPS[fam]["host"], C.LOOPS[fam]["elf"]):
                wbad.append(f"{os.path.relpath(p, root)}: host {host}, ELF {kern}, family {fam}")
                continue
            if C.LOOPS[fam]["host"] != "rgm211":
                continue
            fma, chk, _ = C.host_records(open(p).read(), argv)
            ok, words, _ = C.walk_check(fam, fma, chk)
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
    # ---- RB-E213A and RB-E213AR (aifoundry3, all four families)
    f13a = outs(sd13a)
    n_rec, n_rt, bad, cards = parse_all(f13a, E213A)
    walks, wbad = walk_by_point(f13a, E213A)
    masks = {C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [], "--shires") for p in f13a}
    t.case("RB-E213A", len(f13a) >= 100 and not bad and not wbad and all(walks.get(f, 0) > 0 for f in ("rgm211 gemmLn", "rgm136 gemmLnc", "rgm211 gemmL"))
           and len(masks) >= 2,
           f"{len(f13a)} committed aifoundry3 card-0 stdouts of E213 arm A (both hosts, masks {len(masks)}), {n_rec} records read against each process's "
           f"own command line; {n_rt} runtime lines; the walk by the run's own family on every rgm211-host process: {walks}"
           f"{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref13a = json.load(open(os.path.join(E213A, "data-e213.json")))["arms"]["A"]
    runs13a = runs_of_data(ref13a)
    nr, diffs, nt = reduce_against(sd13a, runs13a, KEYS + ("walk_names", "walk_ok", "walk_launches_bad"))
    t.case("RB-E213AR", nr == len(runs13a) and nr >= 100 and not diffs, f"{nr} of E213 arm A's committed runs: reduce_e215.reduce_run gives data-e213.json's "
           f"run and walk fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E213B and RB-E213BR (card 1)
    f13b = outs(sd13b)
    n_rec, n_rt, bad, cards = parse_all(f13b, E213B)
    walks, wbad = walk_by_point(f13b, E213B)
    t.case("RB-E213B", len(f13b) >= 70 and not bad and not wbad and n_rt > 0 and cards == {"1"} and walks.get("rgm136 gemmLnc", 0) > 0,
           f"{len(f13b)} committed aifoundry1 card-1 stdouts of E213 arm B, {n_rec} records read, {n_rt} runtime lines dropped and counted (cards named "
           f"{sorted(cards)}); the walk by family: {walks}{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
    ref13b = json.load(open(os.path.join(E213B, "data-e213.json")))["arms"]["B"]
    runs13b = runs_of_data(ref13b)
    nr, diffs, nt = reduce_against(sd13b, runs13b, KEYS + ("walk_names", "walk_ok", "walk_launches_bad"))
    t.case("RB-E213BR", nr == len(runs13b) and nr >= 70 and not diffs, f"{nr} of E213 arm B's committed runs: reduce_run gives data-e213.json's arm B "
           f"run fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E214 (the model session's card-1 sessions of 18 Nov 2026)
    tot = [0, 0, 0]
    allbad, allcards = [], set()
    for d in E214:
        fl = outs(os.path.join(d, "session"))
        a, b2, bad, cards = parse_all(fl, d)
        tot[0] += len(fl)
        tot[1] += a
        tot[2] += b2
        allbad += bad
        allcards |= cards
    t.case("RB-E214", len(E214) == 4 and tot[0] >= 300 and not allbad and allcards <= {"1"},
           f"{len(E214)} committed E214 card-1 sessions ({', '.join(os.path.basename(d)[-6:] for d in E214)}), {tot[0]} stdouts, {tot[1]} records read "
           f"against each process's own command line, {tot[2]} runtime lines (cards {sorted(allcards)}){'; ' + '; '.join(allbad[:3]) if allbad else ''}")
    # ---- RB-E207 and RB-E207R
    f7 = outs(sd7)
    n_rec, n_rt, bad, cards = parse_all(f7, E207D)
    masks = {C.arg_of(proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [], "--shires") for p in f7}
    t.case("RB-E207", len(f7) >= 100 and not bad and n_rec > 0 and len(masks) >= 2,
           f"{len(f7)} committed aifoundry3 card-0 stdouts of E207 (masks {sorted(masks)}), {n_rec} records read as a plain reader reads them, each "
           f"against its own command line; {n_rt} runtime lines{'; ' + '; '.join(bad[:3]) if bad else ''}")
    ref7 = json.load(open(os.path.join(E207D, "data-e207.json")))["arms"]["A"]
    runs7 = [r for P in ref7["points"].values() for r in P["runs"]] + list(ref7["ties"]["runs"])
    nr, diffs, nt = reduce_against(sd7, runs7)
    t.case("RB-E207R", nr == len(runs7) and nr >= 100 and not diffs, f"{nr} of E207's committed runs: reduce_e215.reduce_run gives data-e207.json's run "
           f"fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E211 and RB-E211R (both hosts, the walk)
    f11 = outs(sd11)
    n_rec, n_rt, bad, cards = parse_all(f11, E211D)
    walks, wbad = {}, []
    for p in f11:
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or []
        tok = C.arg_of(argv, "--values").split(":")[0]
        host = "rgm211" if "/rgm211/host/" in argv[0] else "rgm136"
        fam = "rgm211 gemmLn" if tok.startswith("gemmLn") and not tok.startswith("gemmLnc") else ("rgm136 gemmLnc" if tok.startswith("gemmLnc") else "rgm136 gemmL")
        if host != C.LOOPS[fam]["host"]:
            wbad.append(f"{os.path.relpath(p, E211D)}: host {host}, family {fam}")
            continue
        fma, chk, _ = C.host_records(open(p).read(), argv)
        ok, words, _ = C.walk_check(fam, fma, chk)
        walks[fam] = walks.get(fam, 0) + (1 if ok else 0)
        if not ok:
            wbad.append(f"{os.path.relpath(p, E211D)}: {words[:80]}")
    t.case("RB-E211", len(f11) >= 40 and not bad and not wbad and walks.get("rgm211 gemmLn", 0) > 0 and walks.get("rgm136 gemmLnc", 0) > 0,
           f"{len(f11)} committed aifoundry3 stdouts of E211, both hosts, {n_rec} records read; the walk read by E215's family on every rgm211-host "
           f"process: {walks}{'; ' + '; '.join((bad + wbad)[:3]) if bad or wbad else ''}")
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
    # ---- RB-E206B and RB-E206BR (card 1)
    f6 = outs(sd6)
    n_rec, n_rt, bad, cards = parse_all(f6, E206B)
    t.case("RB-E206B", len(f6) >= 200 and not bad and n_rt > 0 and cards == {"1"},
           f"{len(f6)} committed aifoundry1 card-1 stdouts of E206 arm B, {n_rec} records read, {n_rt} runtime lines dropped and counted (cards named "
           f"{sorted(cards)}){'; ' + '; '.join(bad[:3]) if bad else ''}")
    ref6 = json.load(open(os.path.join(E206B, "data-e206.json")))["arms"]["B"]
    runs6 = [r for P in ref6["points"].values() for r in P["runs"]] + list(ref6["ties"]["runs"])
    nr, diffs, nt = reduce_against(sd6, runs6)
    t.case("RB-E206BR", nr == len(runs6) and nr >= 200 and not diffs, f"{nr} of E206 arm B's committed runs: reduce_run gives data-e206.json's arm B "
           f"run fields equal ({'equal' if not diffs else 'DIFFER: ' + '; '.join(diffs[:4])}); {nt} committed samples read")
    # ---- RB-E212 (the model session's card-1 sessions)
    tot = [0, 0, 0]
    allbad, allcards = [], set()
    for d in E212:
        fl = outs(os.path.join(d, "session"))
        a, b2, bad, cards = parse_all(fl, d)
        tot[0] += len(fl)
        tot[1] += a
        tot[2] += b2
        allbad += bad
        allcards |= cards
    t.case("RB-E212", len(E212) >= 3 and tot[0] >= 200 and not allbad and allcards <= {"1"},
           f"{len(E212)} committed E212 card-1 sessions ({', '.join(os.path.basename(d)[-6:] for d in E212)}), {tot[0]} stdouts, {tot[1]} records read "
           f"against each process's own command line, {tot[2]} runtime lines (cards {sorted(allcards)}){'; ' + '; '.join(allbad[:3]) if allbad else ''}")
    # ---- RB-SPLICE: E211's rgm211-host records (the walk inside) and E206 arm B's card-1 records
    n1 = n2 = 0
    sbad = []
    p11 = [p for p in f11 if "/rgm211/host/" in (proc_argv(os.path.dirname(p), os.path.basename(p)[:-4]) or [""])[0]]
    for p, fam in ((p11[0] if p11 else None, "rgm211 gemmLn"), (f6[len(f6) // 2], None)):
        if not p:
            sbad.append("no rgm211-host stdout")
            continue
        text = open(p).read()
        argv = proc_argv(os.path.dirname(p), os.path.basename(p)[:-4])
        if fam:
            tok = C.arg_of(argv, "--values").split(":")[0]
            fam = "rgm211 gemmLn" if tok.startswith("gemmLn") and not tok.startswith("gemmLnc") else "rgm136 gemmLnc"
        lines = [ln for ln in text.split("\n") if ln.startswith("SPARSITY ")]
        a, b2, bad, _ = splice_cases(text, argv, (lines[1], lines[-1]), fam)
        n1 += a
        n2 += b2
        sbad += bad
    t.case("RB-SPLICE", not sbad and n1 > 1500 and n2 > 1500,
           f"{n1} single and {n2} nested runtime-line splices into a real rgm211-host launch and check record of E211's (the walk fields inside) and a "
           f"real card-1 record of E206 arm B's: every one read the same records{' and the same walk' if p11 else ''}{'; bad ' + str(sbad[:4]) if sbad else ''}")
    # ---- RB-CFG
    ok_all, words = True, []
    for arm, sd in (("A", sd7), ("B", sd6)):
        cj = json.load(open(os.path.join(sd, "config-start.json")))
        line = [ln for ln in open(os.path.join(sd, "config-start.out")).read().splitlines() if ln.startswith("{")][-1]
        ok = all(C.config_json(line[:k] + f"Opening device {c}\n" + line[k:] + "\n") == cj for k in range(len(line) + 1) for c in ("0", "1"))
        ok = ok and C.config_json("Opening device 1\n" + line + "\n") == cj and C.config_json(line[:40] + "\n") == {}
        other = "B" if arm == "A" else "A"
        ok = ok and C.config_ok(arm, cj) and not C.config_ok(other, cj)
        ok_all &= ok
        words.append(f"arm {arm}'s committed config line ({len(line) + 1} offsets x 2 cards): {ok}")
    t.case("RB-CFG", ok_all, "; ".join(words) + " (each passes its own arm's start config gate and fails the other's)")
    # ---- RB-ID
    def cfg(d, name="config-start"):
        return json.load(open(os.path.join(d, name + ".json"))), open(os.path.join(d, name + ".err"), errors="replace").read()
    rows = []
    for nm in ("config-start", "config-end"):
        j, err = cfg(sd7, nm)
        rows += [("A", f"E207 {nm}", j, err, True), ("B", f"E207 {nm} (aifoundry3) on arm B", j, err, False)]
        j, err = cfg(sd11, nm)
        rows += [("A", f"E211 {nm}", j, err, True)]
        j, err = cfg(sd6, nm)
        rows += [("B", f"E206 arm B {nm} (card 1)", j, err, True), ("A", f"E206 arm B {nm} (card 1) on arm A", j, err, False),
                 ("B", f"E206 arm B {nm} at 519 mV (card 0's)", dict(j, minion_mv=519), err, False),
                 ("B", f"E206 arm B {nm} with its block removed", j, "\n".join(x for x in err.splitlines() if not x.startswith(("PCIe target", "Physical device ID"))), False)]
    bad = [r[1] for r in rows if (N1.config_identity(r[0], r[2], r[3]) == "") != r[4]]
    hosts = []
    for arm, sd, pids in (("A", sd11, ("s01", "s02")), ("B", sd6, ("p001", "p046", "p021"))):
        for pid in pids:
            ep = os.path.join(sd, "smoke", pid, "proc.err")
            if os.path.exists(ep):
                tg, ids = N1.parse_ident(open(ep, errors="replace").read())
                w, r = N1.host_identity(arm, tg, ids, set())
                w2, r2 = N1.host_identity("B" if arm == "A" else "A", tg, ids, set())
                hosts.append(not w and r and w2 and not r2)
    t.case("RB-ID", not bad and len(rows) == 14 and hosts and all(hosts),
           f"{len(rows)} committed config forms, each passed or refused per arm as stated ({'none wrong' if not bad else 'WRONG: ' + '; '.join(bad[:4])}); "
           f"{len(hosts)} committed smoke host blocks pass on their own arm and are refused on the other: {hosts}")
    # ---- RB-SIM: rgm211's host's real simulator bytes, by E215's families (the new one: case N)
    want = {"W": ("rgm211 gemmLn", True), "Wi": ("rgm211 gemmLn", True), "X": ("rgm211 gemmLn", True), "Xb": ("rgm211 gemmLn", True),
            "C": ("rgm136 gemmLnc", True), "BAD": ("rgm211 gemmLn", False), "N": ("rgm211 gemmL", True)}
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
        if c in want:
            fam, ok_want = want[c]
            ok, words, det = C.walk_check(fam, fma, chk)
            seen[c] = ok
            if ok != ok_want or (c == "BAD" and det.get("launches_bad") != 1) or (c == "N" and (det.get("names") != ["mn"] * len(fma) or any(det.get("tagged")))):
                bad.append(f"{c}: walk read {ok} ({words[:80]}), want {ok_want}")
    nN = json.load(open(os.path.join(SIM, "N.json"))) if os.path.exists(os.path.join(SIM, "N.json")) else {}
    t.case("RB-SIM", not bad and len(seen) == len(want) and seen.get("N") is True,
           f"{len(os.listdir(SIM)) // 2 if os.path.isdir(SIM) else 0} simulator stdouts of the two hosts built on aifoundry3 (E211's kit), {nrec} records "
           f"read against their command lines; the walk read by E215's families {seen}; THE NEW FAMILY's own bytes (case N, {C.arg_of(nN.get('argv', []), '--values')}, "
           f"rgm211's host on rgm211's ELF): walk mn, the tag on none, walk_ok true{'; ' + '; '.join(bad[:3]) if bad else ''}")
    # ---- RB-SMOKE: the runner's smoke reading = the reducer's R0 reading, inside R0's band, on real smoke bytes
    rows, sbad = [], []
    for label, sd in (("E213A", sd13a), ("E213B", sd13b), ("E207", sd7), ("E211", sd11), ("E206B", sd6)):
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
    t.case("RB-SMOKE", rows and not sbad and len(rows) >= 16,
           f"{len(rows)} committed smoke processes: the runner's smoke reading (the median over its counted launches) equals the reducer's (R0's), "
           f"each in R0's 200-4,000: {[(a, b, round(c, 1) if c else c) for a, b, c in rows]}{'; ' + '; '.join(sbad[:3]) if sbad else ''}")
    # ---- RB-SCRUB: the collection's scrub on the boxes' own records (the home in them)
    login = pwd.getpwuid(os.getuid()).pw_name
    home = pwd.getpwuid(os.getuid()).pw_dir.rstrip("/")
    sc_ok, words = True, []
    for label, sd in (("E213 arm A aifoundry3", sd13a), ("E213 arm B aifoundry1 card 1", sd13b), ("E211 aifoundry3", sd11), ("E207 aifoundry3", sd7),
                      ("E206 arm B aifoundry1 card 1", sd6)):
        w = os.path.join(S, "scrub-" + label.split()[0] + ("B" if "arm B" in label else ("A" if "arm A" in label else "")))
        if os.path.exists(w):
            shutil.rmtree(w)
        os.makedirs(w)
        raw = os.path.join(w, "raw")
        n, nre, nh, fails = rebuild_raw(sd, raw, home, login)
        hs = os.path.join(w, "homes.txt")
        open(hs, "w").write(home + "\n")
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
    open(os.path.join(sess, "session.log"), "w").write(f"a {lh}/nekko/build/e215 b {ph}/nekko/x c {dbh}/.local/state d {login}\n")
    open(os.path.join(sess, "x.json"), "w").write(json.dumps({"argv": [f"{ph}/nekko/build/e215rgm/rgm211/host/sparsity_host"]}) + "\n")
    hf = os.path.join(w, "homes-3.txt")
    open(hf, "w").write(f"{lh}\n{dbh}\n{ph}\n")
    lf = os.path.join(w, "login.txt")
    open(lf, "w").write(login + "\n")
    r3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "scrub-check", sess, hf, lf], capture_output=True, text=True)
    hf1 = os.path.join(w, "homes-1.txt")
    open(hf1, "w").write(f"{lh}\n")
    r1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "scrub-check", sess, hf1, lf], capture_output=True, text=True)
    unchanged = open(os.path.join(sess, "session.log")).read().count(dbh) == 1
    forms_ok = r3.returncode == 0 and "SCRUB-CHECK CLEAN: 2 files, 2 held a home path" in r3.stdout and r1.returncode == 3 and \
        "SCRUB-CHECK LEFT" in r1.stdout and unchanged
    t.case("RB-SCRUB", sc_ok and forms_ok,
           "; ".join(words) + f"; the home in three forms (a symlinked home, its physical path, the user database's): scrub-check rc {r3.returncode} "
           f"'{r3.stdout.strip()[:60]}'; with the first form alone: rc {r1.returncode} '{r1.stdout.strip()[:40]}...' (refused, never silent); the "
           f"checked folder unchanged {unchanged}")
    # ---- RB-HOLDERS (fix-e213, verify-e213's finding 2): another login's holder lines at the collection (made-up logins only)
    w = os.path.join(S, "scrub-holders")
    if os.path.exists(w):
        shutil.rmtree(w)
    cp = os.path.join(w, "copy")
    os.makedirs(os.path.join(cp, "reads"))
    real = os.path.join(E206B, "session", "reads", "etwho-001-tie-p001.out")
    committed = open(real, "rb").read()
    ours = committed.replace(b"<login>", b"e215us").replace(b"~/", b"/home/e215us/")
    other = (b"/dev/et0_ops   e215other    204411        3:07 ./build/bench/somebench --card 0 --iters 100\n"
             b"lock:etsoc-shire0.lock e215other    204400        3:08 /home/e215other/work/somebench --card 0\n")
    open(os.path.join(cp, "reads", "etwho-002-pass1-k03.out"), "wb").write(ours + other)
    open(os.path.join(cp, "queue.json"), "w").write('{"queue": [{"ran": false}]}\n')
    open(os.path.join(cp, "session.log"), "w").write("a stand-in session\n")

    def manifest(d):
        rows = []
        for dp, dn, fn in os.walk(d):
            for n in fn:
                rel = os.path.relpath(os.path.join(dp, n), d)
                if rel != "MANIFEST.sha256":
                    rows.append(f"{hashlib.sha256(open(os.path.join(dp, n), 'rb').read()).hexdigest()}  {rel}")
        open(os.path.join(d, "MANIFEST.sha256"), "w").write("\n".join(sorted(rows, key=lambda x: x[66:])) + "\n")
    manifest(cp)
    hf, lf = os.path.join(w, "homes.txt"), os.path.join(w, "login.txt")
    open(hf, "w").write("/home/e215us\n")
    open(lf, "w").write("e215us\n")
    before = {f: hashlib.sha256(open(os.path.join(cp, f), "rb").read()).hexdigest() for f in os.listdir(cp) if os.path.isfile(os.path.join(cp, f))}
    rc1 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "scrub-check", cp, hf, lf], capture_output=True, text=True)
    after = {f: hashlib.sha256(open(os.path.join(cp, f), "rb").read()).hexdigest() for f in os.listdir(cp) if os.path.isfile(os.path.join(cp, f))}
    outd = os.path.join(w, "out")
    os.makedirs(outd)
    rc2 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "data", "2026-11-18", "B", cp, hf, lf, "--outside", outd],
                         capture_output=True, text=True, env=dict(os.environ, RB_DESKTEST="1"))
    named, homes_left, got = [], [], b""
    for dp, dn, fn in os.walk(outd):
        for n in fn:
            b = open(os.path.join(dp, n), "rb").read()
            if b"e215other" in b or b"e215us" in b:
                named.append(n)
            if b"/home/" in b:
                homes_left.append(n)
            if n == "etwho-002-pass1-k03.out":
                got = b
    gl = got.split(b"\n")
    our_lines = [x for x in committed.split(b"\n") if x]
    masked_ok = (gl[:len(our_lines)] == our_lines and gl[len(our_lines)] == b"/dev/et0_ops   <another-login>  204411  3:07"
                 and gl[len(our_lines) + 1] == b"lock:etsoc-shire0.lock <another-login>  204400  3:08")
    open(os.path.join(cp, "reads", "holders.bin"), "wb").write(other)
    manifest(cp)
    rc3 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "scrub-check", cp, hf, lf], capture_output=True, text=True)
    outd2 = os.path.join(w, "out2")
    os.makedirs(outd2)
    rc4 = subprocess.run([sys.executable, "-I", "-B", os.path.join(E, "collect_e215.py"), "data", "2026-11-18", "B", cp, hf, lf, "--outside", outd2],
                         capture_output=True, text=True, env=dict(os.environ, RB_DESKTEST="1"))
    t.case("RB-HOLDERS", rc1.returncode == 0 and rc1.stdout.startswith("SCRUB-CHECK CLEAN: ") and before == after and rc2.returncode == 0
           and "COLLECTED-GATE-STOP " in rc2.stdout and not named and not homes_left and masked_ok
           and rc3.returncode == 3 and "SCRUB-CHECK LEFT" in rc3.stdout and "holders.bin" in rc3.stdout
           and rc4.returncode == 3 and "SCRUB FAILED" in rc4.stdout and "holders.bin" in rc4.stdout,
           f"E206 arm B's committed et-who record with a made-up login of ours and two lines of a made-up other login on card 0: scrub-check rc "
           f"{rc1.returncode} '{rc1.stdout.strip()[:60]}' (the checked copy unchanged {before == after}); collected rc {rc2.returncode}; files naming "
           f"either made-up login after it {len(named)}, holding a home path {len(homes_left)}; the other login's lines masked, its commands dropped and ours "
           f"byte-identical to the committed record {masked_ok}; a holder line in a .bin: scrub-check rc {rc3.returncode} "
           f"('{rc3.stdout.strip()[:40]}...'), the collection rc {rc4.returncode} ('{rc4.stdout.strip().splitlines()[-1][:12] if rc4.stdout.strip() else ''}...')")
    print(f"REALBYTES-E215 {t.ok} of {t.n} {'PASS' if t.ok == t.n else 'FAIL'}")
    return 0 if t.ok == t.n else 1


if __name__ == "__main__":
    sys.exit(main())
