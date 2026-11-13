# E183's kit, dated note 5 (Fri 13 Nov 2026, before any E183 datum): the card lane orchestrated from aifoundry2; step 11's desk-path gate for a desk whose home has the box account's shape (step 11 v3); step 2 v6; no rule, forecast, threshold, plan, cap, stop or reading changes

*Beside [KIT.md](KIT.md) and its dated notes 1-4 (`45e514e3`, `1e74546a`, `e8e9f4e1`, `24b9b99e`); it edits nothing there, nor in
[E183.md](E183.md) or its notes. Written on aifoundry2, desk only, by the lane `port-e183` of Q168, begun at 11:15 PST Fri 13 Nov 2026 by the
clock; its commit's own time is git's. No card was claimed, no device command was sent, no lab box was reached, nothing was posted. Every run
of a built binary, runner or stand-in box went through the round's CPU slot and a no-device sandbox (aifoundry2 has a card of its own).
The orchestrating session moved from the Intel to aifoundry2 on Fri 13 Nov 2026, and the Intel cannot be reached from there; this note asks
whether E183's next day (note 4's runbook, READY WITH GAPS for Fri 13 Nov 2026 or later) runs with aifoundry2 as the desk. **No E183 datum
exists** (`git log --all` on `docs/reports/data/*e183*`: nothing). Before the land it was read by a verifier (`verify-note5`, Q170: holds
with fixes, one minor fault and seven nits, none blocking) and changed by the lane `fix-note5` of Q170, on GitHub main `50430114`: section 11
lists each finding and its answer.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| the orchestrator side's 38 files, for macOS-only forms | none; three GNU-only `date -d` lines, all inside scripts sent to the box; the Python files compile under 3.12.3 with no warning | [`logs/port-aifoundry2-e183.txt`](logs/port-aifoundry2-e183.txt) |
| note 4's desk tests on aifoundry2 | rest 13 of 13, runbook v3 31 of 31, dry pass v2 29 of 29, the train check 42 of 42 on real g++-13 13.3.0 and clang 18.1.3 builds, the dry listing v5 14 steps: the Intel's counts | the same |
| step 0, the anchor lines 1-6, step 1 (a stand-in window) and step 2 v5, in a scratch clone at GitHub main | all as stated; step 2 v5 rc 0 with HARNESS OK 87 on its second run (its first stopped on a GitHub pull that timed out) | the same |
| **step 11's desk-path gate on aifoundry3's committed data, here** | **stops**: E180's data 2 files, E185's 8, E186's 71, "this user's home" | the same; section 1 |
| **step 11 v3's gate, note 5** | the same data pass; every desk path still stops it, however it is spelled: **SELFTEST-NOPATH-E183 PASS, 37 of 37** | [`logs/selftest-nopath-e183.txt`](logs/selftest-nopath-e183.txt) |
| **step 11 v3 end to end** with a stand-in box | step 11 v2 stops at the gate (16) on a session log naming the box's own tree; step 11 v3 refuses an empty HOME before any copy (10), stops on a desk path written `<home>/./...` (16), and collects and scores the same session: **SELFTEST-COLLECT-E183-V3 11 of 11 PASS** | [`logs/selftest-collect-e183-v3.txt`](logs/selftest-collect-e183-v3.txt) |
| the dry listing v6 | 14 steps, 0 exiting non-zero; step 2 v6 and step 11 v3 named, with step 11 v3's early check | [`logs/dry-listing-e183-v6.txt`](logs/dry-listing-e183-v6.txt) |

## 1. What fails on aifoundry2: step 11's desk-path gate

Step 11 v2 (`rb/s22_collect_e183_v2.sh`) ends with k6's `rb_nopath` over the collected output, which runs v3.1's `nopath_q142s.py` with the
lab clone and RB_OUT forbidden. That script also forbids **this user's home** (`os.path.expanduser("~")`). On the Intel the home was a Mac
home, which no box writes. On aifoundry2 it is `/home/<login>`, and the box account on aifoundry3 has the same login, so every path aifoundry3
writes into a session's logs and runs (`/home/<login>/aifoundry/build/...`, `/home/<login>/aifoundry/tools/...`) carries the desk's home as
its prefix. nopath's own header says a box's own path is not a desk path; on this desk it cannot tell them apart. Read here on the lab's
committed aifoundry3 data: E180's vector add (E183's parent) 2 files hit, E185's session 3 8 files, E186's run 3 71 files, all "this user's
home"; with `HOME` set elsewhere, none. So on E183's day, collected from aifoundry2, step 11 v2 would stop (16, "a desk path reached what this
step wrote") after the copy-back and the scoring, before the data commit.

## 2. The fix: step 11 v3 ([`rb/s22_collect_e183_v3.sh`](rb/s22_collect_e183_v3.sh)) and its gate ([`rb/nopath_desk_e183.sh`](rb/nopath_desk_e183.sh), [`rb/nopath_spell_e183.py`](rb/nopath_spell_e183.py))

Step 11 v3 is step 11 v2 with two changes: its last gate but one, `rb_nopath "$OUT"`, becomes `nopath_desk "$OUT"`, and right after the window
it checks the gate's inputs, `nopath_desk_ready`, before any copy (and the step's name in the runbook's log, `s22_collect_v3`). **The desk's
home** is this account's home from the account database, never `HOME` alone, at its physical path. When it is not under `/home/` (the Intel),
`nopath_desk` is k6's `rb_nopath`, unchanged, and `nopath_desk_ready` checks nothing. When it is (aifoundry2):
- `nopath_desk_ready` stops the step **before any copy**: 10 when `HOME` is set but empty, is not absolute, or does not resolve to that home
  (unset is read as the account database's home, as bash and Python read it); 16 when the home holds an entry named as aifoundry3's tree
  (`rb_tree aifoundry3`: `aifoundry`), since such a desk cannot tell its own paths from the box's. `nopath_desk` makes both checks again;
- `nopath_desk` runs the same `nopath_q142s.py`, unchanged, with `HOME` set to RB_OUT for that one call (its home needle becomes RB_OUT,
  forbidden anyway), and forbids instead **each entry of the desk's home by name** (`--forbid <home>/<entry>`, hidden ones too) under each
  spelling of the home (its physical path, the account database's, `HOME` as set: a path written through a link that `HOME` names stops),
  and the session scratch root `/tmp/claude-<uid>` when it exists. An entry that is a symbolic link (nopath also forbids a link's target,
  which may be a short system path) or whose name begins the tree (nopath matches substrings: `<home>/a` would match `<home>/aifoundry/...`)
  is left out by name. The lab clone, RB_OUT, a Mac home or temp path and the Intel's session scratch root stay forbidden as before;
- then **`rb/nopath_spell_e183.py`** over the same output (standard library only; it reads and never writes; .gz read, links skipped, a
  missing output a hit, as nopath): every place a spelling of the home is written is cut into a path, up to the next blank, quote, bracket
  or separator, and two kinds are hits: (1) a path written with a `.`, `..` or empty component that resolves, lexically, under the home and
  outside the box's tree (`<home>/../<login>/x`, `<home>/./x`, `<home>//x`, `<home>/aifoundry/../x`, `<home>/aifoundry/build/../../x`,
  `/home//<login>/x`, `/home/./<login>/x`); (2) a path under an entry left out by name, read as a whole path component (`<home>/a/x` stops,
  `<home>/aifoundry/x` does not). A path that stays in the tree passes however it is written (`<home>/aifoundry/build/../include`), and so
  does the home itself (`HOME=<home>`).

So on aifoundry2 the gate stops every desk path it stopped in v2, **however it is spelled from the home**: under any entry, by name or as a
whole component, and through `.`, `..` or `//` anywhere after the home; and it lets aifoundry3's own tree through, since this desk has no
entry by that name (and refuses to run if one appears). A canonical box path under any other name of the home that the desk also has (a
hidden directory, say) would still stop it, fail closed; the committed aifoundry3 data of E163, E166, E171, E176, E178, E180, E181, E182,
E185 and E186 hold only `/home/<login>/aifoundry/...`, every one inside the tree, and read 0 hits on both halves of the gate. The login scrub
after it (E178's `scrub_tree_e178.py --check`, the owner from the look's `box-login-aifoundry3.txt`) is unchanged.

## 3. The desk tests

[`rb/selftest_nopath_e183.sh`](rb/selftest_nopath_e183.sh), 37 of 37: G1 step 11 v2's gate stops on E180's, E185's and E186's committed data here
(the failure); G2 v3's gate passes all three (nopath and the spelling check); G3 a stand-in output holding only the box's tree path passes v3
(v2 stops); G4 a path under a real entry of the desk's home stops v3 on that entry's own needle; G5-G9 the lab clone, RB_OUT, a Mac home, the
session scratch root and a missing output each stop v3 (16); G10 on a desk whose account home is not under `/home/`, `nopath_desk` is
`rb_nopath`; G11 step 11 v3 is v2 with exactly three lines replaced and two added, the early check before the first copy; G12 its dry listing
names the check and the gate; G13-G19 the home followed by `..`, `.` or `/`, the tree followed by `..`, a deeper climb out of the tree and the
home's own directory written with `//` or `/./` each stop (16), a climb that stays in the tree passes; G20-G21 a stand-in home (the account's
home redefined in the test's subshell) with a link and names that begin the tree: a path under each stops, the tree's form passes, and an
entry named as the tree is refused (16); G22 `HOME` empty, relative, missing or a subdirectory is refused (10), unset passes, and through a
link to the home a desk path stops while the tree's path passes. Run it with a scratch directory under the desk's home (G20-G21's stand-in
homes need the box account's shape; elsewhere they are reported, not asserted).
[`rb/selftest_collect_e183_v3.sh`](rb/selftest_collect_e183_v3.sh), 11 of 11: note 1's runbook test (`rb/selftest_rb_e183_v2.sh`, unchanged)
with its case P2 made portable (it shortens a list with BSD sed's `sed -i ''`, which GNU sed reads as an empty script: on aifoundry2 the
committed test fails P2, 7 of 8), a case C0 (a line naming the box's own tree appended to the stand-in session log, the box login recorded as
the look records it: step 11 v2 stops at the gate, 16), C1a (step 11 v3 with `HOME` set but empty: 10 before any copy, no raw tree, no call),
C1b (a desk path written `<home>/./<name>/x` in the session log: COPY EXACT, then 16 at the spelling check) and C1-C2 on step 11 v3 (COPY
EXACT, the collector v2, note 5's gate and the scrub: 0; again into the same raw tree: 10).

## 4. What else differs on aifoundry2, with no code change

1. **`/usr/bin/python3` is 3.12.3** (numpy 1.26.4), where KIT.md's "the readers' interpreter pinned" names 3.9 (the Intel's). The readers'
   self-tests read the same: score 14 of 14 and v2 23 of 23, loopcmp 4 of 4, note 1's checks, each identical to its committed log; the M1
   reader's self-test 19 of 19 with one printed number different in its last digits (a mean, 0.06648931623931596 under 3.9 and
   0.06648931623931628 under 3.12: 3.12's float `sum` rounds differently). A verdict could move only for a statistic within such a step of
   its threshold. Name the interpreter in the day's records.
2. **rsync 3.2.7** receives step 5a's copy (the Intel's was 3.5.1): the runbook test's real-rsync cases R5-R11 pass here with both ends 3.2.7.
3. **GitHub over ssh from aifoundry2 failed often** on Fri 13 Nov 2026, 11:21-11:43 PST: 7 of 12 `git ls-remote` calls answered on port 22,
   4 of 12 with `ConnectTimeout=10` and 3 attempts; over HTTPS 10 of 10. Steps 0 and 2 pull four times; a failed pull stops them fail closed
   (step 2 v2's own pull says only "the desk check failed: pull"). For steps 0 and 2 only (reads), the card lane may set, in the environment
   and never in a git config file, `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:`
   (step 2 v6 passed this way here). The data commit's push is the commit helper's, outside the kit.
4. The Intel's `lockf -k -t 600 <lock>` is `flock -w 600 -E 75 <lock>` here; the Intel's load reading (load_guard) is absent: read `uptime`.
5. `dry_intel_e183_v2.sh` says "Intel only"; it runs here, 29 of 29, with GNU date on PATH as `gdate`.

## 5. The runbook as it now runs

Note 4's table (its section 7), with two rows changed:

| step | file | from this note |
|---|---|---|
| 2, the desk check | **`rb/s03_desk_e183_v6.sh`** | **new**: step 2 v5, then this note's list and logs |
| 11, the release, then the collection | the post's release; **`rb/s22_collect_e183_v3.sh`** | **new**: step 11 v2 with this note's early check and desk-path gate |

Every other step is note 4's. **Never run on E183's day:** step 2 v5, v4, v3, v2 or v1 alone; step 11 v2 or v1; and everything note 4's
section 7 names. The dry listing: [`rb/list_steps_e183_v6.sh`](rb/list_steps_e183_v6.sh). Its lines "run on the Intel" (k6's `rb_local`
wording, unchanged) mean the desk: aifoundry2 when the card lane runs from there. The card lane's brief carries the same two rows in its dated
note 4 ([`CARD-LANE-BRIEF.md.dated-note-4.md`](CARD-LANE-BRIEF.md.dated-note-4.md)).

## 6. Step 2 v6 (`rb/s03_desk_e183_v6.sh`)

Step 2 v5 unchanged (it reports this note's list as one it does not know, never a gate), then on the same HEAD: `SHA256SUMS-e183-kit-note5`
at its 24 entries, its own pinned sha256 and every entry OK, a gate (16); this note's two desk tests' logs as committed; HEAD unchanged, else
16. Step 2 v6 is not in this note's list (a file cannot hold the sha256 of a list that holds its own); the go's anchor lines give its sha256
beside the list's.

## 7. What does not change

E183.md, its notes 1, M1 and M2, and every rule, forecast, threshold, power figure, plan, cap and stop. KIT.md and notes 1-4 and their files,
and the brief and its notes 1-3. The box files, the box steps, the build, the session, the rest rule and step 5a. The collector, the
reduction, the scorer, the copy check and the login scrub. Every new file is new; nothing committed is modified, renamed or removed. One new
Python file, `rb/nopath_spell_e183.py` (standard library only; a reader, run by path, never imported by another file).

## 8. Labels

- **Registered, before any datum:** step 11 v3's early check and gate, and step 2 v6's pins.
- **Desk checks of code, not measurements:** every test result here, and the GitHub reachability counts (a desk reading of the network).
- **Reported:** october-forecast-model's arms (notes M1 and M2), unchanged and unread.
- Nothing here is held out or post hoc, and nothing is measured.

## 9. Files ([`SHA256SUMS-e183-kit-note5`](SHA256SUMS-e183-kit-note5), 24 entries)

This note; `rb/nopath_desk_e183.sh`, `rb/nopath_spell_e183.py`, `rb/s22_collect_e183_v3.sh`, `rb/selftest_nopath_e183.sh`,
`rb/selftest_collect_e183_v3.sh`, `rb/list_steps_e183_v6.sh`, `CARD-LANE-BRIEF.md.dated-note-4.md`; the four logs. It also pins the unchanged
files the new steps run, source or name: `rb/rb_e183.sh`, `rb/s22_collect_e183_v2.sh`, `rb/s03_desk_e183_v5.sh`, `SHA256SUMS-e183-kit-note4`,
`rb/selftest_rb_e183_v2.sh`, `rb/list_steps_e183_v5.sh`, `collect_e183_v2.sh`, `copycheck_e183.py`, k6's `rb_common.sh`, v3.1's
`nopath_q142s.py` and `rb_run.py`, and E178's `scrub_tree_e178.py`. Step 2 v6 is outside it (section 6).

    bash tools/claims-v3/e183/rb/selftest_nopath_e183.sh <scratch dir under the desk's home>
    bash tools/claims-v3/e183/rb/selftest_collect_e183_v3.sh <scratch dir>
    bash tools/claims-v3/e183/rb/list_steps_e183_v6.sh <an empty scratch dir>

## 10. Open items

1. E183 FULL only on his go. A second verifier did not read section 11's changes before the land; the fix lane's own checks are in
   `logs/port-aifoundry2-e183.txt`.
2. Note 4's gaps stand: the train host's first compile is on the box, the box's compiler read at step 5a, box steps rehearsed against
   stand-ins only.
3. A canonical box path under a desk-home name other than `aifoundry` (one this desk also has) would stop step 11 v3, fail closed; none is in
   the committed aifoundry3 data.
4. The readers run under 3.12.3 here (section 4, item 1); a records round names the interpreter beside the day's verdicts.
5. What neither gate reads (v3.1's nopath, unchanged): a symbolic link in the output (skipped), an empty output (nothing to read), a desk path
   in upper case (not this desk's path on its case-sensitive file system), and a relative path that climbs into the home without writing it.
   The spelling check cuts a path at the next blank, quote, bracket or separator, so a `..` written after such a character in a path's own
   name is not read with the home before it.

## 11. Read before the land: verify-note5's findings, and what changed (fix-note5)

| # | verify-note5 found | the answer |
|---|---|---|
| 1 (minor) | the gate missed a desk path written after the home with `..`, `.` or `/` (`<home>/../<login>/.ssh`, `<home>/aifoundry/../.ssh`, `<home>/./.ssh`, `<home>//.ssh`), which v2 stopped, while section 2 said "the gate keeps every desk path it kept" | **fixed**: `rb/nopath_spell_e183.py`, run by the gate after nopath, stops every path written from the home with a `.`, `..` or empty component that resolves under the home outside the tree, the deeper climbs and the home's own directory written with `//` or `/./` among them (v3.1's gap too); G13-G19 and C1b; section 2 reworded |
| 2 (nit) | a home entry that is a symbolic link, or whose name begins `aifoundry`, was left unforbidden, and a desk path under it passed | **fixed**: each such entry is read as a whole path component by the spelling check (a path under it stops; the tree does not); an entry named `aifoundry` itself is refused (16), by the early check and by the gate; G20-G21 |
| 3 (nit) | the gate leaned on `HOME`: empty, missing, a subdirectory or a link let a desk path through | **fixed**: the home is the account database's; `HOME` set but empty, relative, or not resolving to it is refused (10) before any copy; `HOME`'s own spelling (a link) is forbidden too; G22 and C1a |
| 4 (nit) | G4's "path under a desk home entry" was the test's own scratch path, so G4 failed with a scratch directory elsewhere | **fixed**: G4 writes under a real entry of the home and asserts that entry's needle |
| 5 (nit) | `rb/nopath_desk_e183.sh` wrote the Intel's scratch directory name literally | **fixed**: the header names it in words |
| 6 (nit) | no card-lane brief note: the brief's table still named step 2 v5 and step 11 v2 | **fixed**: [`CARD-LANE-BRIEF.md.dated-note-4.md`](CARD-LANE-BRIEF.md.dated-note-4.md), in this note's list |
| 7 (nit) | the dry listing v6 says "run on the Intel" for desk calls | **answered**: section 5's sentence |
| 8 (nit) | nothing read the files' modes after the land | **answered** outside the kit: the land's record reads `git ls-tree` on the commit (11 files 100644, 3 files 100755) |

The re-make: the lane made note 5 again on GitHub main `50430114` (five commits after `f9632ee3`, other lanes' registrations and records,
none under `tools/claims-v3/e183/`), with 14 files where port-e183's commit had 12; the list has 24 entries where it had 22, and step 2 v6's
two pins changed with it. The verifier's 62 stand-in cases and 16 new ones, run on the revised gate beside v2's and port-e183's: 78 of 78
as the cases want, and the 14 where port-e183's gate did not do what the verifier's case wanted now stop. Two of the verifier's cases that
wanted a pass are now refusals by design: an empty `HOME` (10, any output) and a stand-in home with an entry named `aifoundry` (16, any
output) (`logs/port-aifoundry2-e183.txt`).

SPDX-License-Identifier: Apache-2.0
