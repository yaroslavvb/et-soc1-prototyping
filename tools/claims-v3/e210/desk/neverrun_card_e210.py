#!/usr/bin/env python3
"""E210's never-run search REPEATED by its card lane (Q202, lane kit-e210, Tue 17 Nov 2026, before any E210 datum; E210.md section 4: "A pattern
the model session runs before E210's card day stays in E210 but is no longer 'never run'; E210's card lane repeats this search before its data
commit and says which"). Runbook step 6n (rb/s06n_neverrun_e210.sh A: right before step 7's config read, the day's first card command) and
step 12n (rb/s06n_neverrun_e210.sh A --late: after the copy-back, right before step 12 builds the data directory) call it at the desk. Standard
library only. It runs E210's own registered scanner and report UNCHANGED (desk/neverrun_e210.py, at the sha256 SHA256SUMS-e210-registration
records for it, checked first), and adds only the roots, the exclusions and the words.

    /usr/bin/python3 -I -B tools/claims-v3/e210/desk/neverrun_card_e210.py desk DIR [--late]      the desk's scans -> DIR/scan-*.json
    /usr/bin/python3 -I -B tools/claims-v3/e210/desk/neverrun_card_e210.py report DIR [--a3 SCAN.json --a3-gens GENS.json [--a3-home H] | --a3-not-searched WHY] [--late]
                                                                                                 the registered report, scrubbed, and the words

THE ROOTS (the registered search's four, E210.md section 4): at the desk (aifoundry2) the lab clone at its HEAD, the round's lane folders OUT
(named by E210_ROUND_OUT, so no private path is written here; scratch clones are skipped by the scanner's own .git rule) and the lab account's
work folder HOME/claude/work; on aifoundry3 (rb/s06n's remote read: the same scanner sent on stdin, at nice 19 and idle IO, nothing written
there) the registered tops there that exist (HOME/claude/work, HOME/claude/et-soc1-prototyping, HOME/aifoundry, HOME/e71, HOME/q1NN-*,
HOME/tmp). The --late form scans the desk's three roots only (the box's E210 folders are E210's own, and the box was searched at 6n).
WHAT IS LEFT OUT, BY THE SCANNER'S OWN --exclude (the kit's reading, stated before any datum; verify-e207's findings 1 and 3, taken in):
  - E210'S OWN FOLDERS: in the lab, tools/claims-v3/e210 (the registration's tiles and desk files, the kit's desk tests' logs: the registered
    search excluded it too) and any docs/reports/data/*e210* folder (none before the data commit); in OUT, every top-level folder named
    <role>-e210[<suffix>] (reg-, kit-, verify-, fix-, land-, ready-, card-e210 and any second lane of theirs: their desk tests' doubles name
    E210's tile files by the thousand, and no E210 lane has card time before the card lane's session); on aifoundry3, build/e210, build/e210rgm
    and the synced tools/claims-v3/e210 (E210's dry passes and its own session are E210's, never runs "before" it);
  - THE MODEL SESSION'S FOLDERS (HOME/claude/work/ee-*/, on both boxes): the orchestrator's rule of Mon 16 Nov 2026 23:18:35 PST bars every lab
    lane from reading their uncommitted session folders until E210's forecasts are frozen, and the registered search did not read them; their
    released sessions are committed in the lab, which is searched. NOT SEARCHED (as registered): aifoundry1's own folders.
The registered report counts a law-passing tile file in sw-design-a's folder as a desk file (its own markers) and gives each law NEVER IN A
GEMM unless (i) a GEMM record or command names a generator the host does not draw itself, or (ii) names a tile file that passes the law outside
the desk folders. Condition (i) flips all nine laws at once, whatever the generator's string is in: a desk test's refusal case counts as
much as a run (Tue 17 Nov 2026 01:48 PST, this kit's real run of step 6n: E211's kit and registration name "gemmLn2x2x2:noise:..." and
"gemmLnc2x2x2:noise:..." in their host-refusal checks, which the host refuses before any device, and every law read SEE HITS). So, beside the
registered report (unchanged, its verdict quoted first), this wrapper REPORTS the two conditions apart, by a second read of the same roots with
the scanner's own rules: for each generator not the host's, the text files whose GEMM --values strings use it (with their strings), and for
each law, whether a law-passing tile file outside the desk folders is named by a GEMM, and by which text files. The card lane reads both and
says which patterns ran before (E210.md 4); nothing here is a gate, and E210's frozen scorer never changes (the pattern stays in E210).
AMENDED BEFORE ANY DATUM (E210.md amendment A1 item 1; Q202, lane fix-e210, Tue 17 Nov 2026; verify-e210's finding 1): both conditions count
only a GEMM string inside a HOST LAUNCH RECORD (a "SPARSITY" record's "values" field, or a record split from its prefix that keeps its "launch"
field: a GEMM that ran). A string anywhere else (a command, a script, a document, a plan, a schedule) is listed apart and is never a run: a GEMM
host refuses a generator it does not draw before any kernel launch (rgm136 throws "unknown gen" while filling its pools), and a GEMM that ran
leaves its launch records. (Condition (i)'s case: E211's host-refusal checks name "noise"; condition (ii)'s, found by fix-e210 at 07:07 PST Tue
17 Nov 2026: E212's planned arms and schedules, copied into the round's folders, name two of E212's own tiles that pass the signs and highmant8
laws, before any of those sessions ran.) The classes come from desk/neverrun_gens_e210.py (registered by A1, checked at its registration-list
sha256), run over the same roots with the same exclusions: at the desk by `desk`, on aifoundry3 by rb/s06n in the same bounded read as the
registered scan (its output named by --a3-gens; --a3 without --a3-gens is refused). THE VERDICT (A1): a law is RAN BEFORE when a generator not
the host's sits in a launch record (all nine at once, as registered: the conservative side) or a law-passing tile file outside the desk folders
is named by a GEMM string inside a launch record; else NEVER IN A GEMM. The registered report runs unchanged and its verdict, and condition
(ii) read anywhere, are quoted beside it.
The output: DIR/neverrun-e210-card.json and .txt (the registered report, scrubbed: no login, no home path), DIR/named-by.json (both conditions'
sources and A1's classes and verdict, scrubbed), and the last line "NEVER-RUN <n> of 9 patterns (A1)[; RAN BEFORE: <laws> (see named-by.json)];
by named tile files in launch records: <k> of 9 named[ (<laws>)]; anywhere (the registered condition ii): <k2> of 9 named[ (<laws>)];
generators not the host's in launch records: none | <gens> in <f> file(s); elsewhere (never a run): none | <gens> in <f> file(s); the
registered rule as first written: <m> of 9 (<form>; aifoundry3 ...)". RB_DESKTEST=1 lets E210_NR_LAB, E210_NR_OUT and E210_NR_HOMEW name
stand-in roots (the runbook's desk test only). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = os.path.join(HERE, "neverrun_e210.py")
SCANNER_REL = "tools/claims-v3/e210/desk/neverrun_e210.py"
GENS = os.path.join(HERE, "neverrun_gens_e210.py")          # E210.md A1 item 1's instrument
GENS_REL = "tools/claims-v3/e210/desk/neverrun_gens_e210.py"
REG_LIST = os.path.join(E, "SHA256SUMS-e210-registration")
OWN_LANE = re.compile(r"^[a-z0-9]+-e210(?![0-9])[a-z0-9-]*$")    # E210's own lanes' folders by the round's naming: <role>-e210[<suffix>]
LAWS = ("negzero", "signs", "lowmant8", "highmant8", "bhalfeq", "badjeq", "hd4", "maxalte", "arow50")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def scanner_ok(path=SCANNER, rel=SCANNER_REL):
    want = None
    with open(REG_LIST) as f:
        for ln in f:
            parts = ln.rstrip("\n").split("  ", 1)
            if len(parts) == 2 and parts[1] == rel:
                want = parts[0]
    got = sha(path)
    return got == want, got, want


def roots():
    if os.environ.get("RB_DESKTEST") == "1":
        lab = os.environ.get("E210_NR_LAB", REPO)
        out = os.environ.get("E210_NR_OUT") or os.environ.get("E210_ROUND_OUT")
        homew = os.environ.get("E210_NR_HOMEW", os.path.expanduser("~/claude/work"))
    else:
        lab, out, homew = REPO, os.environ.get("E210_ROUND_OUT"), os.path.expanduser("~/claude/work")
    return os.path.realpath(lab), (os.path.realpath(out) if out else None), os.path.realpath(homew)


def excludes(lab, out, homew):
    ex = {"lab": [os.path.join(lab, "tools/claims-v3/e210")], "out": [], "homew": []}
    dd = os.path.join(lab, "docs/reports/data")
    if os.path.isdir(dd):
        ex["lab"] += [os.path.join(dd, x) for x in sorted(os.listdir(dd)) if "e210" in x]
    if out and os.path.isdir(out):
        ex["out"] = [os.path.join(out, x) for x in sorted(os.listdir(out)) if OWN_LANE.match(x) and os.path.isdir(os.path.join(out, x))]
    if os.path.isdir(homew):
        ex["homew"] = [os.path.join(homew, x) for x in sorted(os.listdir(homew)) if x.startswith("ee-") and os.path.isdir(os.path.join(homew, x))]
    return ex


def run_scan(label, top, ex, path, scanner=SCANNER):
    cmd = [sys.executable, "-I", "-B", scanner, "scan", label, top] + [f"--exclude={x}" for x in ex]
    with open(path, "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
    return r.returncode, r.stderr[-300:]


def desk(d, late):
    ok, got, want = scanner_ok()
    if not ok:
        print(f"REFUSED: the registered scanner's sha256 {got[:12]} is not the registration list's {str(want)[:12]}")
        return 4
    ok2, got2, want2 = scanner_ok(GENS, GENS_REL)
    if not ok2:
        print(f"REFUSED: A1's scanner's sha256 {got2[:12]} is not the registration list's {str(want2)[:12]}")
        return 4
    lab, out, homew = roots()
    if not out or not os.path.isdir(out):
        print("REFUSED: E210_ROUND_OUT does not name the round's lane folders")
        return 2
    os.makedirs(d, exist_ok=True)
    ex = excludes(lab, out, homew)
    meta = {"form": "late" if late else "6n", "roots": {"lab": lab, "out": out, "homew": homew}, "excludes": ex,
            "scanner_sha256": got, "python": sys.version.split()[0]}
    meta["gens_scanner_sha256"] = got2
    for label, top, key in (("lab-at-head", lab, "lab"), ("round-lane-folders", out, "out"), ("lab-account-work", homew, "homew")):
        rc, err = run_scan(label, top, ex[key], os.path.join(d, f"scan-{label}.json"))
        if rc != 0:
            print(f"SCAN FAILED: {label} rc {rc} ({err.strip()[:160]})")
            return 14
        rc, err = run_scan(label, top, ex[key], os.path.join(d, f"gens-{label}.json"), GENS)      # A1 item 1: the same roots, the classes
        if rc != 0:
            print(f"SCAN FAILED: {label} (A1's scanner) rc {rc} ({err.strip()[:160]})")
            return 14
    json.dump(meta, open(os.path.join(d, "desk-meta.json"), "w"), indent=1, sort_keys=True)
    print(f"SCANNED-DESK {meta['form']}: the lab at HEAD, the round's lane folders ({len(ex['out'])} of E210's own lane folders left out), "
          f"the work folder ({len(ex['homew'])} of the model session's folders left out)")
    return 0


def named_by(tops_ex, names, gens=()):
    """The text files under the tops (with the scanner's own rules) whose GEMM --values strings name a tile file of `names` (basenames), and
    those whose strings use a generator of `gens`: ({basename: [paths]}, {gen: {path: [up to 2 value strings]}}, {basename: [paths]} - the
    last, A1 item 1: the files where a string naming the tile sits inside a host launch record, by A1's scanner's own rule)."""
    sys.path.insert(0, HERE)
    import neverrun_e210 as S  # noqa: E402 -- the registered scanner's own rules, imported read-only
    import neverrun_gens_e210 as G  # noqa: E402 -- A1's classes (its launch-record rule), imported read-only
    out, gout, out_lr = {}, {}, {}
    for top, ex in tops_ex:
        if not os.path.isdir(top):
            continue
        for dirpath, dirs, files in os.walk(top):
            if dirpath != top and (".git" in dirs or ".git" in files):
                dirs[:] = []
                continue
            if any(dirpath == x or dirpath.startswith(x.rstrip("/") + "/") for x in ex):
                dirs[:] = []
                continue
            dirs[:] = [x for x in dirs if x != ".git"]
            for fn in files:
                p = os.path.join(dirpath, fn)
                if os.path.splitext(fn)[1].lower() not in S.TEXT_EXT:
                    continue
                try:
                    if os.path.getsize(p) == 2048:
                        continue
                except OSError:
                    continue
                lines = S.read_lines(p)
                for line in lines or []:
                    if "gemm" not in line:
                        continue
                    launch_line = G.RE_LAUNCH.search(line) is not None
                    for rx in (S.RE_REC_VAL, S.RE_CMD_VAL):
                        for m in rx.finditer(line):
                            v = m.group(1).rstrip("',]")
                            arm, gen, fl = S.parse_values(v)
                            if gen in gens:
                                lst = gout.setdefault(gen, {}).setdefault(p, [])
                                if len(lst) < 2 and v not in lst:
                                    lst.append(v)
                            for f in fl:
                                b = os.path.basename(f)
                                if b in names:
                                    out.setdefault(b, set()).add(p)
                                    if rx is S.RE_REC_VAL and launch_line:
                                        out_lr.setdefault(b, set()).add(p)
    return {k: sorted(v) for k, v in out.items()}, gout, {k: sorted(v) for k, v in out_lr.items()}


def report(d, a3, a3_home, a3_not, late, a3_gens=None):
    lab, out, homew = roots()
    meta = json.load(open(os.path.join(d, "desk-meta.json")))
    if a3 and not a3_gens:
        print("REPORT FAILED: --a3 without --a3-gens (A1 item 1 reads aifoundry3's classes from the same read)")
        return 14
    founds = [os.path.join(d, f"scan-{x}.json") for x in ("lab-at-head", "round-lane-folders", "lab-account-work")]
    gfounds = [os.path.join(d, f"gens-{x}.json") for x in ("lab-at-head", "round-lane-folders", "lab-account-work")]
    if a3:
        founds.append(a3)
        gfounds.append(a3_gens)
    try:
        gscans = [json.load(open(f)) for f in gfounds]
    except (OSError, ValueError) as e:
        print(f"REPORT FAILED: A1's scans not readable ({type(e).__name__}: {str(e)[:120]})")
        return 14
    home = os.path.expanduser("~")
    scrubs = [(lab + "/", "<lab at HEAD>/"), (lab, "<lab at HEAD>"), (out + "/", "<the round's lane folders>/"), (out, "<the round's lane folders>"),
              (homew, "<the lab account's work folder>")]
    for h in [x for x in (a3_home, home) if x]:
        scrubs += [(h.rstrip("/") + "/", "<home>/"), (h.rstrip("/"), "<home>")]
    args = [sys.executable, "-I", "-B", SCANNER, "report", os.path.join(d, "neverrun-e210-card.json"), os.path.join(d, "neverrun-e210-card.txt")] + \
        founds + [f"--scrub={p}=>{q}" for p, q in scrubs]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"REPORT FAILED: rc {r.returncode} ({r.stderr.strip()[-200:]})")
        return 14
    rep = json.load(open(os.path.join(d, "neverrun-e210-card.json")))
    verdict = rep.get("verdict", {})
    seen = [x for x in LAWS if verdict.get(x) != "NEVER IN A GEMM"]
    hits = rep.get("law_hits_outside_desk_folders", [])
    names = set(rep.get("law_hit_files_named_by_a_gemm", []))
    gens = list(rep.get("generators_not_the_hosts", []))
    named_laws = sorted({law for h in hits if os.path.basename(h["path"]) in names for law in h["laws"]}, key=LAWS.index)
    # A1 item 1: the classes of every string naming a generator not the host's, from A1's scanner over the same roots
    lr, el = {}, {}
    for g in gscans:
        for gen, v in (g.get("non_host") or {}).items():
            for cls, acc in (("launch_records", lr), ("elsewhere", el)):
                if v.get(cls):
                    a = acc.setdefault(gen, {"strings": 0, "files": {}})
                    a["strings"] += v[cls]
                    for p_, vs in (v.get("files_" + cls) or {}).items():
                        a["files"].setdefault(f"{g.get('label')}: {p_}", vs)
    # A1 item 1, condition (ii): a law-passing tile file outside the desk folders counts only when a string inside a launch record names it
    names_lr = set()
    for g in gscans:
        names_lr |= {b for b, n in (g.get("tile_names_launch_records") or {}).items() if n}
    named_laws_lr = sorted({law for h in hits if os.path.basename(h["path"]) in names_lr for law in h["laws"]}, key=LAWS.index)
    a1_seen = list(LAWS) if lr else list(named_laws_lr)
    a1_verdict = {x: ("RAN BEFORE" if x in a1_seen else "NEVER IN A GEMM") for x in LAWS}
    nb, gnb, nb_lr = {}, {}, {}
    if names or gens:
        ex = meta["excludes"]
        nb, gnb, nb_lr = named_by([(lab, ex["lab"]), (out, ex["out"]), (homew, ex["homew"])], names, set(gens))
    txt = json.dumps({"laws_not_never": seen, "generators_not_the_hosts": gens,
                      "condition_i_generators_named_by_text_files": gnb,
                      "condition_ii_laws_with_a_named_tile_file": named_laws,
                      "tile_files_named": {b: [h["path"] for h in hits if os.path.basename(h["path"]) == b] for b in sorted(names)},
                      "named_by_text_files": nb, "a3": ("NOT SEARCHED: " + a3_not) if a3_not else ("searched" if a3 else "not in this form"),
                      "A1_item_1": {"rule": "both conditions count a GEMM string only inside a host launch record (a SPARSITY record's values field, or "
                                            "a record split from its prefix that keeps its launch field); a string anywhere else (a command, a script, "
                                            "a document, a plan, a schedule) is never a run",
                                    "verdict": a1_verdict, "laws_ran_before": a1_seen,
                                    "condition_ii_laws_with_a_tile_file_named_in_a_launch_record": named_laws_lr,
                                    "tile_files_named_in_launch_records": sorted(names & names_lr),
                                    "named_in_launch_records_by_text_files": nb_lr,
                                    "generators_in_launch_records": lr, "generators_elsewhere_never_a_run": el,
                                    "scans": [{k: g.get(k) for k in ("label", "host", "files_seen", "text_files_read", "gemm_strings", "seconds",
                                                                     "python", "excluded_dirs")} for g in gscans]},
                      "registered_rule_as_first_written": {"verdict": verdict, "laws_not_never": seen},
                      "note": "the desk roots' files only are listed under condition_i, named_by and named_in_launch_records_by_text_files; A1's "
                              "generator classes list the files of every folder scanned, and its tile-name classes (the verdict's input) count the "
                              "strings of every folder scanned, aifoundry3's among them when it was searched"},
                     indent=1, sort_keys=True)
    for p, q in scrubs:
        txt = txt.replace(p, q)
    open(os.path.join(d, "named-by.json"), "w").write(txt + "\n")
    n_reg = len(LAWS) - len(seen)
    n_a1 = len(LAWS) - len(a1_seen)
    nf = lambda acc: sum(len(v["files"]) for v in acc.values())  # noqa: E731
    words = f"NEVER-RUN {n_a1} of {len(LAWS)} patterns (A1)" + (f"; RAN BEFORE: {' '.join(a1_seen)} (see named-by.json)" if a1_seen else "")
    words += f"; by named tile files in launch records: {len(named_laws_lr)} of {len(LAWS)} named" + (f" ({' '.join(named_laws_lr)})" if named_laws_lr else "")
    words += f"; anywhere (the registered condition ii): {len(named_laws)} of {len(LAWS)} named" + (f" ({' '.join(named_laws)})" if named_laws else "")
    words += "; generators not the host's in launch records: " + (f"{' '.join(sorted(lr))} in {nf(lr)} file(s)" if lr else "none")
    words += "; elsewhere (never a run): " + (f"{' '.join(sorted(el))} in {nf(el)} file(s)" if el else "none")
    words += f"; the registered rule as first written: {n_reg} of {len(LAWS)}"
    words += f" ({meta['form']}; aifoundry3 {'NOT SEARCHED: ' + a3_not if a3_not else ('searched' if a3 else 'not searched in this form')})"
    with open(os.path.join(d, "neverrun-e210-card.txt"), "a") as f:
        f.write("\n" + words + "\n")
        for g_, files in sorted(gnb.items()):
            for p_, vs in sorted(files.items()):
                pp = p_
                for a_, b_ in scrubs:
                    pp = pp.replace(a_, b_)
                f.write(f"  generator {g_}: {pp}: {' | '.join(v[:80] for v in vs)}\n")
        for tag, acc in (("in a launch record", lr), ("elsewhere (never a run)", el)):
            for g_, a in sorted(acc.items()):
                for p_, vs in sorted(a["files"].items()):
                    pp = p_
                    for a_, b_ in scrubs:
                        pp = pp.replace(a_, b_)
                    f.write(f"  A1: generator {g_} {tag}: {pp}: {' | '.join(v[:80] for v in vs)}\n")
    print(words)
    return 0


def main(argv):
    if len(argv) >= 2 and argv[0] == "desk":
        return desk(argv[1], "--late" in argv)
    if len(argv) >= 2 and argv[0] == "report":
        a3 = argv[argv.index("--a3") + 1] if "--a3" in argv else None
        a3h = argv[argv.index("--a3-home") + 1] if "--a3-home" in argv else None
        a3n = argv[argv.index("--a3-not-searched") + 1] if "--a3-not-searched" in argv else None
        a3g = argv[argv.index("--a3-gens") + 1] if "--a3-gens" in argv else None
        return report(argv[1], a3, a3h, a3n, "--late" in argv, a3g)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
