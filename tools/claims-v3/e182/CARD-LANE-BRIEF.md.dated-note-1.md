# The card lane's brief, dated note 1: E184 now runs by its kit note 2 (six pinned lists), E182's steps 2 v4, 6 v4 and 11 v3, what to do after 11-14 on a step-6 start, the step-6 record in the data, and the map from box steps to file numbers (Q154; E182's kit, dated note 3)

*Sat 7 Nov 2026 (week 45), first written 19:03 PST on the Intel, desk only (Q154, lane `fix-e182n`): no card was claimed, no device command
was sent, no lab box was reached, nothing was posted. It sits beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) (`22da6a7b`), which stays as
committed, and E182's kit note 3 ([KIT.md.dated-note-3.md](KIT.md.dated-note-3.md)) lists it. It answers the adversarial verifier of E182's
kit notes 1 and 2 (`verify-e182n`, 17:55-18:36 PST today): its minor 4 (the brief's E184 facts were stale) and nit 7 (the step numbers).
It also carries note 3's runbook changes (the verifier's minors 1 and 2 and nit 5) into the brief. **Where this note and the brief differ,
this note governs.** The brief's order on the boxes (its section 2), look before the post (section 3), the day's one post (section 4), and
the stops, commands and caps (section 6) stand as written. It adds no rule. The re-run rule's departure from the letter of E182.md section 7
is stated in [E182.md.dated-note-2.md](E182.md.dated-note-2.md).*

## 1. E184 runs by its kit note 2 (the brief's opening paragraph and section 1)

After the brief was written, E184 gained dated amendment A3 (`3b48cf7b`, 18:10:08 PST, committed alone) and its kit's dated note 2
(`571511d0`, 18:30:34 PST). **Kit note 2's section 3 table governs E184's steps**, by the brief's own clause ("If a later E184 note changes
E184's steps, its table governs those steps"). What changes for the card lane:

| E184 box step | as the brief read it (kit note 1) | now (kit note 2) |
|---|---|---|
| 2, the desk check | `rb/s03_desk_e184.sh`, four lists pinned (11, 44, 6 and 45) | **`rb/s03_desk_e184_v2.sh`, six lists pinned: 11, 44, 6, 45, 3 and 20** (the registration, the kit, A2, kit note 1, A3, kit note 2) |
| 4 then 3 | the look, then the post (the brief's order) | the same: kit note 2's table lists the look first |
| 7, the reads | `rb/s09_reads_e184.sh S\|B` | **`rb/s09_reads_e184_v2.sh S\|B`** (the config read kept on the box, A3-3) |
| 10b, new | (none) | **`rb/s09_reads_e184_v2.sh S\|B after`**, right after step 10 exits 0 and before the release, every time (READ only) |
| 11, collect | `rb/s22_collect_e184.sh S\|B` | **`rb/s22_collect_e184_v2.sh S\|B`**; `scored-e184-v3.md` and `.json` govern; E184-L and E184-P are quoted with `governing_R` and `governing_ci95` |

- **Unchanged:** A3 leaves E184's forecasts, bands, plan, stops and caps unchanged ("What does not change"). The brief's section 6 stands:
  arm S about 125 card-minutes (cap 135), arm B about 18 (cap 25); 65 W / 70 C on aifoundry3, 66 W / 72 C on card 1; the one WRITE, the
  statistics reset in arm B's pass 18441.
- **The order on aifoundry3 is unchanged:** E184 arm S's look comes only after E182's step 11 copy-back. Arm S's step 10b read runs after
  arm S's own session, so it never runs beside E182, which has ended. On aifoundry1 card 1, arm B's step 10b runs after arm B's session.
- **Checked here:** each of E184's six lists reads exactly its pinned count, all entries OK, at lab `eb15a69b` (a records commit after
  `571511d0` that touches no E184 file; `logs/reruns-note3.txt`).

## 2. E182's steps 2, 6 and 11 are now v4, v4 and v3 (the brief's sections 1 and 5)

- **Step 2 is v4,** `rb/s03_desk_e182_v4.sh`: five lists at pinned counts, **32, 79, 50, 49 and 89**. The brief's "four hash lists ... 32,
  79, 50 and 49" reads this way.
- **Step 6 is v4,** `rb/s08_a3_preflight_e182_v4.sh start`, then `wait` again while it says 17, or `--no-trains` for the fallback. The
  brief's section 5 reads with v4's words:
  - **TRAIN-HOST-INPUTS-DIFFER (16)** can come from `start`: the read before the build now checks all nine build inputs, main.cpp with
    them. It can also come from `wait`: the build job's own check, if an input changed after that read. Either way nothing was built and
    **no build is counted**. Note 1's rule applies: step 5 v2 once more, then step 6 v4 `start`; if the inputs differ again, the fallback.
  - **`start` after a good build that day is refused** (10, "the train host was built on aifoundry3 today"). Run `wait`, which reads the
    build's checks again.
  - **After 11, 12, 13 or 14 on `start`, run `wait` first.** The start may have launched the job before its call was cut. Run `start`
    again only if `wait` reads JOB-UNKNOWN (no build job today), or if the step itself asks for it: a failed build (the one re-run), or
    TRAIN-HOST-INPUTS-DIFFER (after step 5 v2). After 11, 12 or 13 on `wait`, run `wait` again.
  - **The fallback** starts with step 6 v4 `--no-trains`, then follows the brief: k6's reads, `rb/s10_a3_dry_e182_v2.sh start --no-trains`
    and `wait --no-trains`, `rb/s11_a3_session_e182_v2.sh PASSES no`, the wait, the release and step 11.
  - Never run step 6 v3 on a day step 6 v4 runs. v3 counts every line of the day in the box's count file, v4's "ended" lines with them.
- **Step 11 is v3,** `rb/s22_collect_e182_v3.sh`. It also copies the box's count file (`build/e182-build-attempts.txt`) and each build's own
  log (`build/e182-build-logs/<day>/e182-build-host-start<k>.txt`) into the data's `logs/`. **The data README states step 6's outcome from
  them** (the brief's last bullet of section 5): each start and each "ended" line with its result, the day's builds less any that read
  TRAIN-HOST-INPUTS-DIFFER, and TRAIN-HOST-BUILT, or the fallback and why. The data commit's public-text scan covers these logs with the
  other files. Step 6's calls are also kept in `RB_OUT`, outside the repo; none of them needs committing.

## 3. KIT.md's box steps and the file numbers (nit 7)

KIT.md and the notes' bodies name E182's steps by KIT.md's box steps. Note 1's v2 files name them by their file numbers in their messages:
s11 v2's "after step 8 v2's build failed" means box step 6's build, and s08 v2's fallback "step 8 v2 ... step 10 v2 ... step 11 v2" means
box steps 6, 8 and 9. Notes 2 and 3 name the files themselves in their messages.

| KIT.md box step | the file on the card day | a v2 message calls it |
|---|---|---|
| 1, the window | `rb/s02_window_e182.sh` | step 2 |
| 2, the desk check | `rb/s03_desk_e182_v4.sh` | step 3 |
| 4, the look (before 3) | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | step 5 |
| 3, the post | (the card lane's) | |
| 5, the sync | `rb/s07_a3_sync_e182_v2.sh` | step 7 |
| 6, the build and the box's checks | `rb/s08_a3_preflight_e182_v4.sh` | step 8 |
| 7, the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | step 9 |
| 8, the dry pass | `rb/s10_a3_dry_e182_v2.sh` | step 10 |
| 9, the session | `rb/s11_a3_session_e182_v2.sh` | step 11 |
| 10, the wait | `rb/s20_wait_e182.sh` | step 20 |
| 11, the release, then the collection | `rb/s22_collect_e182_v3.sh` | step 22 |

*Labels: every pin, plan, cap, stop and step named here is **registered** (E182's and E184's kits and notes). The E184 lists' counts were
checked at the desk (`logs/reruns-note3.txt`). Nothing here is blind, held out or measured.*

SPDX-License-Identifier: Apache-2.0
