# The card lane's brief for day 2, dated note 1 (Sun 8 Nov 2026, before any E183 or E185 datum; Q158b): the day-2 check before each run's step 1 and inside each step 2 (E185's v4, E183's v3), only the network's pull retried before E185's step 14, the M1 readers only behind the check's gate after each data commit, and lines for the records

*Beside the day-2 brief, `CARD-LANE-BRIEF.md` (`408a9a9e` in E185's kit, `6860643c` in E183's, git 06:48:51 and 06:49:00 PST Sun 8 Nov
2026), which it edits nothing of; an identical copy sits in each kit. Written on the Intel, desk only, by the lane `fix-d2b` of Q158b, begun
at 07:46 PST Sun 8 Nov 2026 by the clock; its commit's own time is git's. No card was claimed, no device command was sent, no lab box was
reached, nothing was posted. It answers the adversarial verifier of the brief and of E185's kit note 2 (`verify-d2b`, Sun 8 Nov 2026
07:01-07:45 PST: holds with fixes, 4 minor faults and 5 nits, none blocking). The code is E185's kit note 3
([`../e185/KIT.md.dated-note-3.md`](../e185/KIT.md.dated-note-3.md)) and E183's kit note 2
([`../e183/KIT.md.dated-note-2.md`](../e183/KIT.md.dated-note-2.md)). **It adds no rule, forecast, threshold, plan, cap or stop.** It changes
the brief's sections 1, 2 (item 3 and E183's step 6), 5 and 6 as below; everything else in the brief stands.*

## 1. Before anything (the brief's section 1, changed)

- **The day-2 go names the commit that added this note.** Before anything else, in the lab clone: `git merge-base --is-ancestor <that
  commit> HEAD` exits 0; `git diff --quiet <that commit> -- tools/claims-v3/e185/SHA256SUMS-e185-kit-note3
  tools/claims-v3/e183/SHA256SUMS-e183-kit-note2` exits 0; and `shasum -a 256 -c` of each of those two lists, from the lab's top, reads
  every line OK (16 and 15). Otherwise nothing below runs, and a dated note comes first.
- **The day-2 check by hand, in place of the plain `git pull --ff-only`**, before E185's step 1 and again before E183's step 1:
  `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py tree --pull`. It pulls, then reads HEAD's descent from `6860643c`, every
  list the day reads at its count, its own bytes and every entry, no change but an addition since `6860643c` on the day's paths, no added
  file that shadows a module, and nothing uncommitted. On its 0, go on; on a 16, its STOP line names why, and a dated note comes first
  (a "pull" that says "the network's" is run again once the network answers).
- **Each run's step 2 at its latest version:** E185 **`rb/s03_desk_e185_v4.sh`** (the day-2 check with its own pull, then step 2 v3
  unchanged on the same tree), as step 2 and again just before step 14; E183 **`rb/s03_desk_e183_v3.sh`** (the same, then step 2 v2).
  Never E185's step 2 v3, v2 or v1 alone, nor E183's v2 or v1.
- **The lab clone stays still while the day runs.** Each hand check and each step 2 runs under the Intel's lab-commit lock (the lock its
  commit helper takes), and from E185's step 2 to E183's data commit no lane but the card lane commits in the lab clone.

## 2. The order (the brief's section 2, changed)

In the table, E185's step 2 and its "step 2 v3 again" are **`rb/s03_desk_e185_v4.sh`**, and E183's step 2 is **`rb/s03_desk_e183_v3.sh`**.
Item 3 becomes:

3. **Before E185's step 14, step 2 v4 again**, with E185's `RB_OUT`; step 14 runs only on its 0, right after it, with no pull or commit in
   the lab clone between them. **Any other exit means step 14 does not run until a dated note says how**, E185's files staying on the box,
   read-only, with two exceptions, each run again once:
   - a 16 whose STOP line says "pull: the upstream did not answer (the network's ...)": run step 2 v4 again once the network answers;
   - a 16 that says "the lab clone moved during step 2 v3": run step 2 v4 again.

   A 16 naming a list, the history, an addition, status, ancestry or the box list; a "pull" that is not the network's (the clone diverged
   from its upstream, or HEAD detached); or a 10 (a window not written today, as when step 14 would fall after midnight), each waits on
   that dated note. **The window is never rewritten:** a new window changes `RB_DAY`, and with it the name of E185's data directory.

E183's step 6 (item 6, and section 3's job waits): **wait again while it says 17, or 14 with "no reading"** ("no reading of the build job
...: run this step's wait again before any start"). Its other 14, "the build job ended rc 0 without its TRAIN-HOST-BUILT line", is not a
cut call: waiting again only re-reads a finished job, so the step's own words govern (read the job's output and the build's log on
aifoundry3 that it names). The brief's shorthand "while it says 17 or 14" is quoted this way from here on.

## 3. The card-minutes (the brief's section 5, for the records)

E183 SHORT is **25.3** card-minutes by its registration (`plan-e183.json`; E183.md "about 25"; KIT.md's "about 26" adds the kit's gaps), so
the day with SHORT is **about 128** card-minutes (caps 137, unchanged); with FULL (51.9) it stays about 155 (caps 170). No plan or cap
changes.

## 4. october-forecast-model's readers (the brief's section 6, changed)

- **Each reader runs after its run's data commit, through the day-2 check's gate**, never by hand:
  - E185: `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py m1 e185 --data <E185's data dir> --rb-out <E185's RB_OUT>`;
  - E183: `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py m1 e183 --data <E183's data dir>`.
- The gate reads the day-2 check (no pull), the run's M1 files unchanged since `6860643c`, its M1 list at its count and its own bytes
  (E185's 21 at `52a6c1622fcf5f31...`, E183's 25 at `c8bad97187caf6f3...`) with every entry OK, for E185 the last M1 line of step 2 v3 in its
  `RB_OUT` log ("present, its list 21 of 21 at its pinned bytes"), and the data directory committed and clean. On all of them it runs the
  note's own run line (`--out` in the data directory, as the M1 notes give it), prints `READER-RC`, and checks the reader wrote only its two
  outputs.
- **On its 0**, the reader has run: its two outputs, the only new files, go into a dated note beside the data README, with the `READER-RC`
  line (a refusal or a non-zero exit is recorded there, never a block). **On a 16**, the reader is not run, and that note records the STOP
  line. The section's two `shasum -c` lines are replaced by the gate, which reads the same lists at their own bytes too.
- The data commit no longer waits on, or records, the readers: the M1 notes' "before the data commit" becomes "after it". The readings are
  unchanged (the same reader, on the same committed files, by the same line).

## 5. Lines for the records

- **"Never a gate"** (step 2 v3's line for note M1's list) holds for committed changes only: an uncommitted M1 file stops step 2 v3 by its
  status check, and so would a login link (11) or a bound (13) on the M1 list's read (`verify-d2b`'s nit 6).
- **The datelines** "first written between ... and 06:50 PST" in E185's kit note 2, both briefs and E183's M1 note's dated note 1 ran ahead
  of the clock (their files were last written at 06:44 PST, by the files' own times); quote git's times: `408a9a9e` 06:48:51 PST and `6860643c` 06:49:00 PST
  (nit 8).
- **The public-text scans** of fix-d2, of verify-d2b and of this lane ran without the lab scanner's private table, which is absent on the
  Intel, so its people and login patterns were not applied; each lane's own categories found nothing. A later public scan runs where the
  table exists (nit 9).
- The E183 SHORT figure and E183's step 6 wording: sections 2 and 3 above (nits 5 and 7).

*Labels: every step, gate, plan, cap, stop and order named here is **registered** (the kits, their notes and E183.md and E185.md with their
notes); october-forecast-model's arms are **reported**, their forecasts **blind** for E183 and E185 (frozen before any datum); the desk tests
are checks of code. Nothing here is held out, measured or post hoc.*

SPDX-License-Identifier: Apache-2.0
