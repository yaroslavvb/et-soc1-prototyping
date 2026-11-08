# The card lane's brief for day 2, dated note 2 (Sun 8 Nov 2026, before any E183 or E185 datum; Q158): the day-2 check v2 before each run's step 1 and inside each step 2 (E185's v5, E183's v4), the M1 readers behind the check v2's gate, the go's anchor lines, and "writes or commits"

*Beside the day-2 brief, `CARD-LANE-BRIEF.md` (`408a9a9e` in E185's kit, `6860643c` in E183's), and its dated note 1 (`1e74546a`, git
08:37:53 PST Sun 8 Nov 2026), which it edits nothing of; an identical copy sits in each kit. Written on the Intel, desk only, by the lane
`fix-fx` of Q158, begun at 11:31 PST Sun 8 Nov 2026 by the clock; its commit's own time is git's. No card was claimed, no device command was
sent, no lab box was reached, nothing was posted. It answers the adversarial verifier of the day-2 check (`verify-fx`, Sun 8 Nov 2026
10:42-11:3x PST: holds with fixes, 2 minor faults and 6 nits, none blocking). The code is E185's kit note 4
([`../e185/KIT.md.dated-note-4.md`](../e185/KIT.md.dated-note-4.md)) and E183's kit note 3
([`../e183/KIT.md.dated-note-3.md`](../e183/KIT.md.dated-note-3.md)). **It adds no rule, forecast, threshold, plan, cap or stop.** It changes
note 1's sections 1, 2 (item 3) and 4 as below; everything else in the brief and in note 1 stands.*

## 1. Before anything (note 1's section 1, changed)

- **The day-2 go names the commit that added this note, and the own sha256 of its two lists.** Before anything else, in the lab clone:
  `git merge-base --is-ancestor <that commit> HEAD` exits 0; `git diff --quiet <that commit> -- tools/claims-v3/e185/SHA256SUMS-e185-kit-note4
  tools/claims-v3/e183/SHA256SUMS-e183-kit-note3` exits 0; `shasum -a 256` of each of those two lists reads the go's sha256; and `shasum -a
  256 -c` of each, from the lab's top, reads every line OK (20 and 19). Otherwise nothing below runs, and a dated note comes first. Note 1's
  lines need not be run as well: `1e74546a` is an ancestor of this note's commit, and this note's two lists pin note 1's two lists at their
  bytes.
- **The day-2 check v2 by hand, in place of v1's**, before E185's step 1 and again before E183's step 1, under the Intel's lab-commit lock
  as note 1 says: `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull`. It is v1's check, with v1 at its committed
  bytes, on a wider perimeter (47 lists; 6 directories and 592 named files outside them), and no untracked module in any of the day's 156
  directories. On its 0, go on; on a 16, its STOP line names why, and a dated note comes first (a "pull" that says "the network's" is run
  again once the network answers).
- **Each run's step 2 at its latest version:** E185 **`rb/s03_desk_e185_v5.sh`** (the check v2 with its own pull, then step 2 v4 unchanged on
  the same tree), as step 2 and again just before step 14; E183 **`rb/s03_desk_e183_v4.sh`** (the same, then step 2 v3). Never E185's step 2
  v4, v3, v2 or v1 alone, nor E183's v3, v2 or v1, nor the check v1 by hand.
- **The lab clone stays still while the day runs** (note 1's line, corrected: verify-fx's nit 8). From E185's step 2 to E183's data commit,
  no lane but the card lane **writes or commits** in the lab clone. An uncommitted file another lane leaves under the day's paths, a
  working note under `e183/` or `e185/` among them, stops each step 2 with 16 (fail closed, but it delays the day).

## 2. The order (note 1's section 2, changed)

In the table, E185's step 2 and its "again" are **`rb/s03_desk_e185_v5.sh`**, and E183's step 2 is **`rb/s03_desk_e183_v4.sh`**. Note 1's
item 3 reads v5 for v4: before E185's step 14, step 2 v5 again, with E185's `RB_OUT`; step 14 runs only on its 0, right after it. The cases
run again once are a 16 whose STOP line says "pull: the upstream did not answer (the network's ...)", and one that says "the lab clone moved
during step 2 v4" (v5's own HEAD check) or "the lab clone moved during step 2 v3" (v4's, inside v5): run step 2 v5 again. Every other exit
waits on a dated note, as note 1 says, E185's files staying on the box, read-only; the window is never rewritten. For E183's step 2 v4 the
same holds, with "moved during step 2 v3" (its own) or "moved during step 2 v2" (v3's, inside it): run step 2 v4 again.

## 3. october-forecast-model's readers (note 1's section 4, changed)

- **Each reader runs after its run's data commit, through the check v2's gate**, never by hand and never through v1's gate:
  - E185: `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e185 --data <E185's data dir> --rb-out <E185's RB_OUT>`;
  - E183: `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data <E183's data dir>`.
- The gate is v1's word for word with the check v2's tree check (no pull): the run's M1 files unchanged since `6860643c`, its M1 list at its
  count and own bytes, for E185 step 2 v3's last M1 line in its `RB_OUT` log, the data directory committed and clean; then the note's own
  run line, `READER-RC`, and only its two outputs written. On its 0 the outputs and the `READER-RC` line go into a dated note beside the data
  README (a refusal or a non-zero exit is recorded there, never a block); on a 16 the reader is not run, and that note records the STOP line.

## 4. Lines for the records

- **The day-2 perimeter, for any lane that writes in the lab:** the check v2's day paths, `check_day2_v2.py paths` (one a line). They are
  v1's (6 directories and 133 named files) plus each of the 15 added lists and every file it names, among them: E176's and E181's committed
  passes that `score_e185.sh` pools; E78's to E164's committed runs and their summaries that M11's scorer opens; the bench's `accum.c` and
  `run_kinds.py`; pool 8's predictor's and freeze's lists and every file they name (blind8's READMEs, predictions and dated notes among them);
  M10's list (174) and its files; M11's card-1 reader and refit lists and their files; the pool-8 scorers; aifoundry3's idle-floor lists; k6's
  driver list. **None is edited in place.** A dated note beside one is an addition and passes; an untracked module in any of the day's
  directories stops the day, and an untracked note outside the core directories does not.
- **Outside every day-2 path:** `docs/findings/02-requests.md`, `03-experiments.md`, `04-artifacts.md`, `05-claims.md`,
  `docs/findings/README.md`, `AGENT.md` and its changelog file. The check v2 passed at a HEAD where all of them had changed since `6860643c`.
- The E186 records lines (verify-fx's nits 3-7) are in E186's kit note 2.

*Labels: every step, gate, plan, cap, stop and order named here is **registered** (the kits, their notes and E183.md and E185.md with their
notes); october-forecast-model's arms are **reported**, their forecasts **blind** for E183 and E185 (frozen before any datum); the desk tests
are checks of code. Nothing here is held out, measured or post hoc.*

SPDX-License-Identifier: Apache-2.0
