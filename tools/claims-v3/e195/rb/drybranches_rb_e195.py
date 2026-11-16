#!/usr/bin/env python3
"""E195's kit (Q191, lane fix-e195, Sun 15 Nov 2026, before any E195 datum; verify-e195's nit 7): THE AUDIT TABLE of every line of the
runbook that reads the dry flag RB_DRY (rb/dry-branches-rb-e195.tsv), the runbook's twin of desk/dry-branches-e195.tsv: each such line of
rb/rb_e195.sh, rb/s*_e195.sh and k6's rb_common.sh (sourced unchanged by every step, and by k6's own steps 4 and 7), its number, the
function it sits in, its text, what the dry listing does there, what the real path does, and the runbook desk test's cases that ran its
real branch. rb/list_steps_e195.sh is not read: it is the dry listing itself (it sets RB_DRY=1 for every step; the desk test's case A runs
it). A case is named by the first word of its ok line in rb/selftest_rb_e195.sh, and one ok line can hold several cases: K holds K, W1-W3
and G; P2 holds P2, P3, H1-H3 and D1; X holds X and T; L1 holds L1-L3; RS holds RS, SF and LA. A row whose cases begin "NOT ON E195'S
DAY" names a branch no E195 step reaches (the reason in the row).

    python3 -I -B drybranches_rb_e195.py [--write]         the rows (made from the files' own lines); --write writes the table;
                                                           DRYBRANCHES-RB-E195 OK, or exit 3 when a line has no reading below
    python3 -I -B drybranches_rb_e195.py --check <results> the committed table against the files (a line without a row, or a row whose
                                                           text differs, fails) and every named case PASS in <results> (lines "PASS <case>"
                                                           or "FAIL <case>", written by the desk test's ok()): AUDIT-RB-E195 OK or FAIL
SPDX-License-Identifier: Apache-2.0
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
TSV = os.path.join(HERE, "dry-branches-rb-e195.tsv")
STEPS = ["s02_window_e195.sh", "s03_desk_e195.sh", "s07_a3_sync_e195.sh", "s08_a3_build_e195.sh", "s09_a3_reads_e195.sh",
         "s10_a3_dry_e195.sh", "s11_a3_session_e195.sh", "s20_wait_e195.sh", "s22_collect_e195.sh", "s24_reduce_e195.sh"]
FILES = ["tools/claims-v3/e195/rb/rb_e195.sh"] + ["tools/claims-v3/e195/rb/" + s for s in STEPS] + \
        ["tools/claims-v3/q141k-runbook/k6/rb_common.sh"]
ANY = "P1,S,B,RT"   # the real steps every helper serves: step 2, the sync, the build, step 7's reads
# (file, function or "-" at the top level, the stripped line's start) -> (under the dry listing, on the real path, the cases that ran it)
READ = [
    ("rb_e195.sh", "rb_init", '[ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing', "the step's dry-listing banner", "no banner", ANY),
    ("rb_e195.sh", "e195_window", 'if [ -n "${RB_DRY:-}" ]; then echo "--- gate: RB_OUT', "the window gate named, the window read", "window.env written today (Pacific), naming today and E195, else 10", "K,P1"),
    ("rb_e195.sh", "e195_pull", 'if [ -n "${RB_DRY:-}" ]; then', "the pull printed, RB_RC 0", "RB_GITLOCK required and outside the repo; git pull --ff-only under the lab-git lock (a nested lock exits 75)", "K,N,P1"),
    ("rb_e195.sh", "e195_harness_sha", '[ -n "${RB_DRY:-}" ] && { echo "<harness', "a placeholder", "the lab clone's harness-e195.json sha256 (steps 8 and 9 pass it)", "DR,RS"),
    ("s02_window_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ "$day" = ', "any day (a sample)", "the window's day must be today (Pacific), else 10", "K,P1"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ "${RB_RC:-0}" -ne 0 ] && bad="$bad pull', "no pull status read", "a failed or nested pull is a stop (16)", "N,P1"),
    ("s03_desk_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && continue', "the commits by content not checked", "the registration's and the kit's commits found by content, ancestors of HEAD, the registration's subtree pinned", "P1,P2"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad paths-not-clean"', "not read", "E195's paths and the day's tools clean, else 16", "P1"),
    ("s03_desk_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then#lists', "the lists' own sha256 and counts not compared", "each list at its pinned sha256 and count, else 16", "P1,P2"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && { [ "$RB_RC" -eq 0 ] && [ "$(grep -c', "the entries not counted", "every entry OK, at the pinned count, else 16", "P1,P2"),
    ("s03_desk_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then#unknown', "lists not pinned not read", "every other SHA256SUMS file under e195 read and reported (never a gate)", "P1"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && { [ "$(rb_val \'^([0-9]+)$\')" = 1 ] || bad="$bad freeze-line"; }', "not read", "the freeze line on exactly one line of E195.md, else 16", "P1"),
    ("s03_desk_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || { rm -rf "${RB_OUT:?}/drylisting"', "no scratch made", "RB_OUT/drylisting made afresh for the listing check", "P1"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && bad="$bad E195-datum-in-a-ref"', "not read", "no docs/reports/data/*e195* path in any commit of any ref, else 16", "P1,P2"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && { rb_has \'^NO-DATUM OK\'', "not read", "check_history_e195.py nodatum reads NO-DATUM OK, else 16", "P1,P2"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && { [ "$(rb_val \'^([0-9]+)$\')" = 1 ] || bad="$bad log-$f"; }', "not read", "each desk test's committed log holds its PASS line once, else 16", "P1"),
    ("s03_desk_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ "$h0" != "$h1" ] && bad="$bad HEAD-moved"', "not compared", "HEAD unchanged across the checks, else 16", "P1"),
    ("s07_a3_sync_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || rb_has \'^NOT-BESIDE-OURS: \'', "not read", "the read before the sync answered (no session or job of ours on the box), else 14", "S"),
    ("s07_a3_sync_e195.sh", "-", 'if [ -n "${RB_DRY:-}" ]; then', "a placeholder for the sync list", "the sync list from harness_e195.py --list (at least 50 paths, else 10)", "S"),
    ("s07_a3_sync_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "the synced paths have uncommitted', "not read", "the synced paths have no uncommitted change, else 16", "S"),
    ("s07_a3_sync_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || rb_has \'^CHECK PASS\'', "not read", "harness-e195.json re-made from the lab clone's files, else 16", "S"),
    ("s07_a3_sync_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || rb_has \'^HARNESS OK: \' || rb_die $RB_E_GATE "a harness file', "not read", "every harness file at its sha256 in the lab clone, else 16", "S"),
    ("s07_a3_sync_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || rb_has \'^HARNESS OK: \' || rb_die $RB_E_GATE "the box', "not read", "the box's copies all at their pins (HARNESS OK on the box), else 16", "S"),
    ("s08_a3_build_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then', "the day's build count not read", "the count of today's builds read; built today: 10 (run the wait); a third start: NO-THIRD-BUILD", "B,X"),
    ("s08_a3_build_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && { rb_say "then: the verdict line', "the wait's verdict named, exit 0", "the verdict line, the box's pins and tools read, RB_OUT/e195-built.txt", "B"),
    ("s09_a3_reads_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || {', "the rest's answer not read", "the rest read first: REFUSED stops with 10 and no config read; no answer stops with 14", "RT"),
    ("s09_a3_reads_e195.sh", "-", 'if [ -n "${RB_DRY:-}" ]; then', "k6's step 7 named before its own listing", "no line; k6's step 7 runs (exec)", "RT"),
    ("s10_a3_dry_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ -n "$(e195_built)" ]', "the build record not needed", "today's build record (RB_OUT/e195-built.txt), else 10", "DR"),
    ("s10_a3_dry_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && exit 0', "exit 0 after the listing", "the dry pass's job started and its verdict read", "DR"),
    ("s11_a3_session_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ -n "$(e195_built)" ]', "the build record not needed", "today's build record, else 10", "RS"),
    ("s11_a3_session_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ -n "$HS" ]', "the harness sha256 not needed", "the lab clone's harness-e195.json present, else 10", "RS"),
    ("s11_a3_session_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ] && [ -f "$RB_OUT/e195-T0.txt" ]; then', "no relaunch read", "an earlier launch from this RB_OUT: its one relaunch, or no third launch (10)", "SD"),
    ("s11_a3_session_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && exit 0', "exit 0 after the listing", "the launch read: LAUNCHED (the T0 recorded), or the box's refusal (10)", "RS,SD"),
    ("s20_wait_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ -n "$want" ]', "no T0 needed", "RB_OUT's e195-T0.txt names the run, else 10", "W1r,W2r"),
    ("s20_wait_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && exit 0', "exit 0 after the listing", "the wait's verdict: RUN-RUNNING 17, RUN-ENDED 0, GATE-STOPPED or MAIN-CRASHED 16, RUN-GONE 14", "W1r,W2r,WN,GS"),
    ("s22_collect_e195.sh", "-", '[ -n "$T0" ] || [ -n "${RB_DRY:-}" ]', "no T0 needed", "the T0 step 9 recorded, else 10", "C,C2,GS"),
    ("s22_collect_e195.sh", "-", '[ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}', "a placeholder login", "the box login the look recorded, else 10", "C,C2,GS"),
    ("s22_collect_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then#raw', "no folders checked", "RB_OUT's copy-back and output folders new, else 10", "C,C2,GS"),
    ("s22_collect_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then#have', "the box's answer not read", "the session's directory on the box (HAVE), its SUM and ABSENT lines kept", "C,C2,GS"),
    ("s22_collect_e195.sh", "-", 'rb_has \'^ASSEMBLED \' || [ -n "${RB_DRY:-}" ]', "not read", "the data directory or the gate stop's record assembled, else 14", "C,GS"),
    ("s24_reduce_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || [ "$(grep -c . "$RB_CAP")" = 3 ]', "not read", "the data directory committed, else 10", "R"),
    ("s24_reduce_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die', "not read", "no uncommitted change in it, else 10", "R"),
    ("s24_reduce_e195.sh", "-", '[ -z "${RB_DRY:-}" ] && [ "$RB_RC" -ne 0 ] && rb_die', "not read", "its SHA256SUMS holds, else 10", "R"),
    ("s24_reduce_e195.sh", "-", '[ -n "${RB_DRY:-}" ] || rb_has \'^999232f2', "not read", "the reducer at its registered sha256, else 10", "R"),
    ("s24_reduce_e195.sh", "-", 'if [ -z "${RB_DRY:-}" ]; then', "no input folder made", "the reducer's input folder made new; the main passes (block.json ok) linked in", "R"),
    ("s24_reduce_e195.sh", "-", 'rb_has \'^LEFTOVER-E195: \' || [ -n "${RB_DRY:-}" ]', "not read", "the leftover checker ran, else 14", "R"),
    ("rb_common.sh", "rb_say", 'rb_say() { if [ -n "${RB_DRY:-}" ]; then', "'(dry listing; a real run would say:)'", "the plain line", ANY),
    ("rb_common.sh", "rb_init", '[ -n "${RB_DRY:-}" ] && echo "=== [$RB_STEP] dry listing', "k6's banner (k6's own steps 4 and 7)", "no banner", "L1,RT"),
    ("rb_common.sh", "rb_probe", 'if [ -n "${RB_DRY:-}" ]; then echo "--- probe', "the probe printed", "the 15 s hard-killed probe (ssh true)", "S,B,RT,DR,RS,L1"),
    ("rb_common.sh", "rb_remote", 'if [ -n "${RB_DRY:-}" ]; then', "the remote script printed in full", "the script over ssh bash -s at its class's bound; a login link 11, a hang 13, a cut 14", "S,B,RT,DR,RS,W1r,C,L1"),
    ("rb_common.sh", "rb_local", 'if [ -n "${RB_DRY:-}" ]; then', "the command printed", "the command run at its class's bound, its output captured", "P1,P2,C,R"),
    ("rb_common.sh", "rb_has", '[ -n "${RB_DRY:-}" ] && return 0', "always true", "grep in the last call's output", ANY),
    ("rb_common.sh", "rb_val", '[ -n "${RB_DRY:-}" ] && { echo DRY; return 0; }', "DRY", "the first match in the last call's output", "P1,B"),
    ("rb_common.sh", "rb_refused", '[ -n "${RB_DRY:-}" ] && return 0', "never stops", "a box's REFUSED stops the step with 10", "S,B,RT,C"),
    ("rb_common.sh", "rb_identity_stop", '[ -n "${RB_DRY:-}" ] && return 0', "never stops", "a box's IDENTITY-STOP stops with 16 (read by rb_launched before a refusal)", "RS,SD"),
    ("rb_common.sh", "rb_launched", '[ -n "${RB_DRY:-}" ] && return 0', "always launched", "LAUNCHED <run>, or the identity stop (16), the box's refusal (10), else 14", "RS,SD"),
    ("rb_common.sh", "rb_need_start", 'if [ -n "${RB_DRY:-}" ]; then echo "--- gate: now <=', "the gate named", "now <= the window's last start, else 13", "S,B,DR,RS"),
    ("rb_common.sh", "rb_need_end", 'if [ -n "${RB_DRY:-}" ]; then echo "--- gate: now +', "the gate named", "now + the cap <= the window's last end, else 13", "RS"),
    ("rb_common.sh", "rb_job_wait", '[ -n "${RB_DRY:-}" ] && return 0', "no verdict read", "the job's verdict: done rc 0, done non-zero or lost 14, still running 17", "B,DR,L1"),
    ("rb_common.sh", "rb_nopath", 'if [ -n "${RB_DRY:-}" ]; then rb_disp', "the gate named", "nopath_q142s.py over what the step wrote",
     "NOT ON E195'S DAY: no E195 step calls rb_nopath (step 11 uses E183's desk-path gate)"),
]
# lines whose start repeats in one top-level file: told apart by a line just above them
CONTEXT = {("s03_desk_e195.sh", 'if [ -z "${RB_DRY:-}" ]; then'): [("for spec in $REGPIN $KITPIN; do", "#lists"), ('unknown=""', "#unknown")],
           ("s22_collect_e195.sh", 'if [ -z "${RB_DRY:-}" ]; then'): [('[ -n "$own" ] || rb_die', "#raw"), ("G=()", "#have")]}


def lines_of(fn):
    """(line number, stripped text, function) for each line of fn that reads RB_DRY and is not a comment."""
    out = []
    func = "-"
    for i, ln in enumerate(open(os.path.join(REPO, fn), encoding="utf-8"), 1):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\(\) *\{", ln)
        if m:
            func = m.group(1)
        s = ln.strip()
        if "RB_DRY" in ln and not s.startswith("#"):
            out.append((i, s, func))
        if m and ln.rstrip().endswith("}"):
            func = "-"                        # a one-line function
        elif ln.rstrip() == "}":
            func = "-"
    return out


def tag_of(fn, i, s):
    b = os.path.basename(fn)
    for (cf, start), tags in CONTEXT.items():
        if b == cf and s.startswith(start) and s == start:
            text = open(os.path.join(REPO, fn), encoding="utf-8").read().splitlines()
            best = None
            for above, tag in tags:
                for j in range(i - 2, max(-1, i - 8), -1):
                    if text[j].strip().startswith(above):
                        if best is None or j > best[0]:
                            best = (j, tag)
                        break
            return best[1] if best else ""
    return ""


def rows():
    out, bad = [], []
    for fn in FILES:
        b = os.path.basename(fn)
        for i, s, func in lines_of(fn):
            t = tag_of(fn, i, s)
            cands = [r for r in READ if r[0] == b and r[1] == func and
                     ((t and r[2] == s + t) or (not t and "#" not in r[2][-10:] and s.startswith(r[2])))]
            if not cands:
                bad.append(f"{fn}:{i} ({func}) has no reading: {s[:80]}")
                continue
            r = max(cands, key=lambda r: len(r[2]))
            out.append([fn, str(i), func, s[:70], r[3], r[4], r[5]])
    return out, bad


def write_tsv(rs):
    with open(TSV, "w", encoding="utf-8") as f:
        f.write("# E195's kit: THE AUDIT of every line of the runbook that reads RB_DRY (made by rb/drybranches_rb_e195.py from the files' own\n"
                "# lines; rb/selftest_rb_e195.sh checks the files against it at its end: a line without a row, a row whose text differs or a named\n"
                "# case that did not pass fails its case AUDIT-RB). Q191, lane fix-e195, verify-e195's nit 7.\n"
                "# file\tline\tfunction\ttext (prefix)\tunder the dry listing\ton the real path\tcases that ran the real branch\n")
        for r in rs:
            f.write("\t".join(r) + "\n")


def check(results):
    res = {}
    for ln in open(results, encoding="utf-8"):
        p = ln.split()
        if len(p) == 2 and p[0] in ("PASS", "FAIL"):
            res[p[1]] = res.get(p[1], True) and p[0] == "PASS"
    have = {}
    for ln in open(TSV, encoding="utf-8"):
        if ln.strip() and not ln.startswith("#"):
            r = ln.rstrip("\n").split("\t")
            have[(r[0], r[1])] = r
    bad, n = [], 0
    for fn in FILES:
        for i, s, func in lines_of(fn):
            n += 1
            r = have.get((fn, str(i)))
            if not r:
                bad.append(f"{fn}:{i} has no row")
                continue
            if r[3] != s[:len(r[3])] or r[2] != func:
                bad.append(f"{fn}:{i} the row's text or function differs")
            if r[6].startswith("NOT ON E195'S DAY"):
                continue
            for c in [x.strip() for x in r[6].split(",") if x.strip()]:
                if not res.get(c):
                    bad.append(f"{fn}:{i} case {c} did not pass in this run")
    extra = len(have) - n
    if extra:
        bad.append(f"{extra} row(s) name no line that reads RB_DRY")
    if bad:
        print(f"AUDIT-RB-E195 FAIL: {len(bad)} problem(s): " + "; ".join(bad[:8]))
        return 1
    print(f"AUDIT-RB-E195 OK: {n} lines of the runbook read RB_DRY (rb_e195.sh, the ten steps, k6's rb_common.sh), each with a row whose "
          f"cases passed in this run ({sum(1 for v in res.values() if v)} ok lines read), but the one no E195 step reaches")
    return 0


def main(argv):
    if argv[:1] == ["--check"] and len(argv) == 2:
        return check(argv[1])
    rs, bad = rows()
    for r in rs:
        print("\t".join(r))
    if bad:
        print("DRYBRANCHES-RB-E195 NOT COVERED: " + "; ".join(bad))
        return 3
    if argv[:1] == ["--write"]:
        write_tsv(rs)
    print(f"DRYBRANCHES-RB-E195 OK: {len(rs)} lines that read RB_DRY, each read and mapped")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
