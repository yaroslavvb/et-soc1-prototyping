# E185's kit, dated note 3 (Sun 8 Nov 2026, before any E185 datum): step 2 v4 runs the day-2 check before step 2 v3 (no change but an addition since 6860643c on the day's paths, every list the day reads at its own bytes, no added file that shadows a module, nothing uncommitted), and october-forecast-model's M1 reader runs only behind the check's gate, after the data commit; no box file, rule, forecast, threshold, plan, cap, stop or order of box steps changes

*Beside [KIT.md](KIT.md) (`460c352f`), [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`ad2ed873`) and
[KIT.md.dated-note-2.md](KIT.md.dated-note-2.md) (`408a9a9e`, git 06:48:51 PST Sun 8 Nov 2026); it edits nothing there. Written on the
Intel, desk only (no card, no device command, no ssh to a lab box, no post in the lab's channel, no Modal), by the lane `fix-d2b` of Q158b,
begun at 07:46 PST Sun 8 Nov 2026 by the clock; its commit's own time is git's. It answers the adversarial verifier of kit note 2 and of
E183's note M1 dated note 1 and the day-2 brief (`verify-d2b`, Sun 8 Nov 2026 07:01-07:45 PST: **holds with fixes**, 0 critical, 0 major,
4 minor faults and 5 nits, none blocking): its faults 2 and 3 (E185's side) and fault 1 (E185's reader) here, E183's side of faults 1 and 3
in E183's kit ([`../e183/KIT.md.dated-note-2.md`](../e183/KIT.md.dated-note-2.md)), and fault 4 with the nits in the brief's dated note
([`CARD-LANE-BRIEF.md.dated-note-1.md`](CARD-LANE-BRIEF.md.dated-note-1.md), the same in both kits). **No E185 datum exists**
(`git log --all` on `docs/reports/data/*e185*` and `*-e185-*`: nothing). **No box file changes:** `frozen-e185.sha256`'s 30 entries, the
runner, the session, the block, the smoke gate, the stops and the device commands are the kit's as committed, and so is every step that
reaches the box.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the day-2 desk test**, on a scratch clone of a local bare upstream (itself a clone of the lab) and a helper clone of it; stand-in ssh, rsync and scp refuse any call | **SELFTEST-DAY2-V1 PASS, 25 of 25**; 0 calls to any box, 0 lines in the lock file | [`rb/logs/selftest-day2-v1.txt`](rb/logs/selftest-day2-v1.txt) |
| **the dry listing v4** | every step exits 0, no ssh or rsync call; the look before the day's post; step 2 v4 listed twice (step 2, and again just before step 14); the M1 gate after step 14 and the data commit | [`rb/logs/dry-listing-v4.txt`](rb/logs/dry-listing-v4.txt) |
| **device commands**, the runbook with step 2 v4 and the day-2 check in v3's place (v3 still scanned: it runs inside v4) | **GO, 11 send sites**, every one a READ; bare, NO-GO at exactly step 9's guard call; **both bodies byte for byte kit note 2's** | [`rb/logs/dmcmd-audit-v4.txt`](rb/logs/dmcmd-audit-v4.txt), [`rb/logs/dmcmd-audit-bare-v4.txt`](rb/logs/dmcmd-audit-bare-v4.txt) |
| **every step 2 for real** at this note's commit, on a scratch clone, each with its own window written that day | step 2 v4 rc 0 twice, v3 and v2 rc 0; E183's v3 and v2 rc 0 | the lane's own run (the records give its time) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sun 8 Nov 2026 at about 08:21 PST: public rows H24, H25
   and H28 (opaque pointers), as KIT.md and its notes 1 and 2 read them.
2. **Used.**
   - **Kit note 2** (`408a9a9e`): `rb/s03_desk_e185_v3.sh`, run unchanged inside step 2 v4; `rb/list_steps_e185_v3.sh`, the form of the
     dry listing v4; `rb/selftest_rb_e185_v3.sh`'s cases K, P2-P5 and W, the form of this test's K, H-cases and P0.
   - **verify-d2b's cases**, re-made on this test's clone: H2b, H2c, H2d, H2f, H3b, H3c, H4e, H7, H5c (as S1), H6b (as L1), H6c (as U), H6d
     (as D) and H6e (as X); and its git-diff line, taken in a stricter form (below).
   - **E185's note M1** (`2f6a4440`): its list `SHA256SUMS-e185-m1` (21, `52a6c162...`) and its reader's run line, which the gate runs.
   - *The same operation, earlier:* on the intact tree step 2 v4 and v3 read alike (P0: both 0, v3's line inside v4's); v4 differs only where
     the day-2 check refuses, and kit note 2's desk test stands for every check v3 makes.
3. **Not used.** Any change to a box file or a box step; aifoundry1 or aifoundry2; any E185 datum (none exists); anything of the private
   tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## The runbook as it now runs (kit note 2's table, with this note's changes)

| step | file | from this note |
|---|---|---|
| **0, before step 1** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py tree --pull`** | **new:** the day-2 check by hand, in place of the brief's plain pull (the brief's dated note 1, section 1) |
| 1, the window | `rb/s02_window_e185.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e185_v4.sh`** | **new:** the day-2 check with its own pull, then step 2 v3 unchanged on the same tree, then HEAD unchanged |
| 3-13 | as kit note 2's table | unchanged |
| **before 14** | **`rb/s03_desk_e185_v4.sh` again**, with the same `RB_OUT` | step 14 only on its 0 (the brief's dated note 1, item 3) |
| 14, the collection | `rb/s22_collect_e185_v2.sh` | unchanged |
| **after the data commit** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py m1 e185 --data <E185's data dir> --rb-out <E185's RB_OUT>`** | **new:** october-forecast-model's reader runs only behind the gate (fault 1, below) |

**Step 2 v3 is never run alone on E185's card day** (it runs inside v4), nor v2 or v1. Step 2 v4 sources nothing before the check; v3 sources
the kit's `rb_common_e185.sh` unchanged, with the same exit codes (KIT.md).

## Fault by fault

### verify-d2b's minor fault 2: E185's registered scorer sat behind count pins only

- **What it was.** M11's scorer v5 (`score_m11_v5.py`, which scores E185's registered rules) rewritten together with its line in
  `SHA256SUMS-score-m11-v5` (H2d), or under a copied line (H3c), or that list reordered (H4e), passed both runs of step 2 v3: v3 holds M11's
  seventeen lists at their counts only, and the scorer's one byte pin, in note M1's list, is report-only.
- **What the day-2 check does** ([`rb/check_day2_v1.py`](rb/check_day2_v1.py), Python's own modules only, run with `-I`), before step 2 v3:
  - **No change but an addition since `6860643c` on the day's paths**, read twice: per commit (`git log -m --full-history
    --diff-filter=a 6860643c..HEAD`) and on the tree (`git diff --diff-filter=a 6860643c HEAD`). The filter `a` is everything but an
    addition: modified, deleted, renamed, type-changed. It is stricter than verify-d2b's `MDR`, and the per-commit read also catches a file
    added after `6860643c` and changed later (this note's own files among them).
  - **The day's paths** are E183's, E185's, M11's, the footing law's, the k6/v3.1 runbook's and the enercat workload's directories, plus
    each of the 133 files outside them that the day's 32 lists, E183's harness (its 80 files and 40 build inputs) or E185's runbook pins
    name. Desk case C counts 446 named files, every one under them.
  - **Every list the day's two step 2s read, at its pinned count, its own sha256 and with every entry OK**, 30 in all: M11's seventeen
    (among them `SHA256SUMS-score-m11-v5` `f6dd93bd...`, `-score-m11-v4` `efcc3cfb...` and `-a10` `50f24610...`, the three step 14 v2
    reads), the footing law's two, E185's seven (its five, kit note 2's `f4211256...`, and the box list's 27 repo entries) and E183's four
    (its three, and the brief's, whose M1 entries are reported). Note M1's two lists are read and reported, never a gate.
  - The other two checks are below (additions, "Found here"; nothing uncommitted on the day's paths).
- **Desk cases:** H2d, H3c and H4e read v4 16 each, naming the list's bytes and the history; H2d's v3 alone still reads 0 (the fault,
  re-made).

### verify-d2b's minor fault 3, E185's side: a committed change to either brief passed

- **E185's brief** rewritten with its line in kit note 2's list (H2b), or under a copied line (H3b): v4 16 (kit note 2's list off its own
  bytes; the history names the brief); H2b's v3 alone 0.
- **E183's brief**, which E185's day also reads: committed (H7) or uncommitted (S1), v4 16. v3 alone passed S1: its status check reads
  E185's, M11's and the footing law's paths only.

### verify-d2b's minor fault 1, E185's side: the M1 reader's gate was weaker than step 2 v3's byte pin

- **What it was.** The brief's gate before the reader was `shasum -a 256 -c` of the M1 list (21 of 21), which a reader rewritten together
  with its list line passes (H2c), and nothing tied it to step 2 v3's byte pin. The reader is Python, run with the lane's rights in the lab
  clone, with `--out` in the data directory, before the data commit.
- **What the gate does** (`check_day2_v1.py m1 e185 --data <dir> --rb-out <E185's RB_OUT>`), **after E185's data commit**: the day-2 check
  (no pull); E185's six M1 files unchanged since `6860643c`; `SHA256SUMS-e185-m1` at 21 and at its own sha256 `52a6c1622fcf5f31...`, 21 of 21
  OK; the last M1 line of step 2 v3 in E185's `RB_OUT` log reading "present, its list 21 of 21 at its pinned bytes"; the data directory
  committed and clean, and the reader's two outputs not yet there. Only then does it run the M1 note's own run line
  (`/usr/bin/python3 -B tools/claims-v3/e185/arm_m1_read_e185.py --data <dir> --out <dir>/arm-m1-e185`, from the lab's top, bounded at
  600 s, with no `PYTHON*` variable), print its exit status, and check that the reader wrote only its two outputs (else 16). A reader's
  refusal or non-zero exit is recorded, never a block. The outputs go in with a dated note beside the data README.
- **Its place moves**, from "after step 22's score and before the data commit" (note M1's M1-4; the brief's section 6) to after the data
  commit, so a reader can no longer change the files the data commit holds. The reading is unchanged: the same reader, on the same committed
  files, by the same line.
- **Desk cases:** H2c, v4 0 with the M1 change reported, and the gate 16, the reader not run; R1, the gate 0, the reader run on a stand-in
  data directory (rc 0, "not read"), its two outputs the only new files; R2 (an uncommitted file in the data directory) and R3 (no step 2
  M1 line in the log) 16, not run; R5 (a directory that is not E185's) 10.

### Found here: an added file can shadow a module a reader or scorer imports

The M1 readers and M11's scorer run with `-B`, so Python looks in their own directories first, and a `json.py` added beside them (an addition, which the history
check allows by design) would be imported before the standard module; and M11's scorer v5 puts E185's directory first on `sys.path`, so a
module of M11's name added under e185 could take its place. The day-2 check refuses (16), in the day's directories, an added `.py` or
package whose name the system python finds outside the lab clone (its own modules and site packages, the user site with the scorers'
numpy among them), one whose module name another of the day's modules has, a byte-code file and a `.pth` file. Desk cases: AD2
(`e185/json.py`), v4 and E183's v3 16; AD3 (a forced-in `m11/__pycache__/*.pyc`), AD4 (`e185/score_m11_v4.py`) and AD5
(`e185/numpy.py`), v4 16 each. Any other addition passes and is counted (AD1: a dated note M2, v4 0).

### Found here: the lab moving during step 2, and the pull's failure named

- Step 2 v4 pulls first and checks that tree, so v3's own pull then reads "Already up to date". If HEAD moves between the two (a push
  landing in the seconds between), v4 refuses: "the lab clone moved during step 2 v3: run step 2 v4 again" (LM, made with a hook in the
  test's clone).
- A failed pull names its cause: "the upstream did not answer (the network's: run this step again once it answers)" (U), "the clone has
  diverged from its upstream (not the network's: a dated note first)" (D), "HEAD is detached (not the network's ...)" (X). The brief's
  item 3 reads these words.

### What it does not close

- The check is code in the lab clone too. The day-2 go names the commit that added this note, and before step 0 the card lane checks this
  note's lists against it (the brief's dated note 1, section 1): a commit that rewrote the check would show there.
- An uncommitted change on the day's paths still stops step 2 (v3's status check, and the day-2 check's): the M1 arm is "never a gate"
  only for committed changes (verify-d2b's nit 6).

## What the card day reads from this note

- Step 0 is the day-2 check by hand; step 2 is v4, run as step 2 and again just before step 14 (step 14 only on its 0); the M1 reader
  runs only through the gate, after the data commit.
- The rest of the day's order, the "no reading" line, the post and the README's words: [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) with its
  [dated note 1](CARD-LANE-BRIEF.md.dated-note-1.md).

## What does not change

KIT.md, kit notes 1 and 2 and their files and lists; the box list (`frozen-e185.sha256`); the session, runner, block, smoke gate, stops,
device commands, budget and cap; every step that reaches the box; E185.md and A1; note M1, its reader and its reading; M11's scorer v5;
E181's data. The rest gate's 40 minutes, A7-4's noon and hour, and the 6,300 s window gate are step 10 v2's, as committed. The new files are
new; v1's, v2's and v3's stay as committed.

## Files ([`SHA256SUMS-e185-kit-note3`](SHA256SUMS-e185-kit-note3), 16 entries)

This note; [CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md); [`rb/check_day2_v1.py`](rb/check_day2_v1.py),
[`rb/s03_desk_e185_v4.sh`](rb/s03_desk_e185_v4.sh), [`rb/list_steps_e185_v4.sh`](rb/list_steps_e185_v4.sh) and
[`rb/selftest_day2_v1.sh`](rb/selftest_day2_v1.sh); the logs `rb/logs/selftest-day2-v1.txt`, `dry-listing-v4.txt`, `dmcmd-audit-v4.txt`
and `dmcmd-audit-bare-v4.txt`. The list also pins the unchanged files step 2 v4 runs or names: `rb/s03_desk_e185_v3.sh`,
`rb/rb_common_e185.sh`, `rb/s02_window_e185.sh`, `rb/s22_collect_e185_v2.sh`, `SHA256SUMS-e185-kit-note2` and the brief this note's
brief note corrects, `CARD-LANE-BRIEF.md`. It holds no file of note M1.

    bash tools/claims-v3/e185/rb/selftest_day2_v1.sh <a scratch directory outside the repo> > selftest-day2-v1.txt
    bash tools/claims-v3/e185/rb/list_steps_e185_v4.sh <an empty scratch directory> > dry-listing-v4.txt

## Labels

- **Registered:** every list, pin, step, gate, plan, cap and stop named here (E185.md with A1, M11's A7-4, KIT.md and its notes); this
  note's step 0, step 2 v4 and its re-run before step 14, and the M1 gate, before any datum.
- **Desk checks of code, not measurements:** every test result here.
- **Reported:** october-forecast-model's arm (note M1); its forecasts are blind for E185 (frozen before any datum).
- Nothing here is held out or post hoc.

## Compute

The Intel, through the round's local slot, one job at a time at nice 10: the dry listings, two development runs and the committed run of
the desk test (about 150 s each), the audits, the public-text scans and every step 2 at the commit. The scratch clones are shared and
sparse (about 250 MB each) and are removed after use. No lab box, no remote host, no card.

SPDX-License-Identifier: Apache-2.0
