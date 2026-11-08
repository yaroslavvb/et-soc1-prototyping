# The card lane's brief for E186's day: what his go must say, look before the post, the order of the box steps, what stops the session, and the words the records use (Q158; E186's kit)

*Sun 8 Nov 2026 (week 45), on the Intel, desk only (Q158, lane `kit-e186`): no card was claimed, no device command was sent, no lab box
was reached, nothing was posted. It sits in E186's kit beside [KIT.md](KIT.md), which lists it, and is read before the runbook on the day
the owner's go names. It is E182's brief ([`../e182/CARD-LANE-BRIEF.md`](../e182/CARD-LANE-BRIEF.md) with its dated notes 1 and 2) for
E186's one run, and it restates what E186.md and the kit register: **no rule, forecast, threshold, statistic, power figure, plan, cap or
stop changes here.** Box step numbers are KIT.md's.*

## 1. What his go must say, and what needs no word

- **The day,** after day 2: E185, then E183 after E185's step 14. E186 runs after E183's step 11 copy-back has ended, on the same day
  only if the window fits; otherwise another day.
- **One window in PST:** the last start and the last end. It must fit about 100 card-minutes (FULL's cap, 6,000 s from E186_T0) plus the
  box steps around them (the sync, the build, its checks, the reads, the dry pass before the session; the copy-back after it): about
  2.5 h in all. Step 9 refuses a launch less than 6,000 s before the last end; step 11's copies start at least 600 s before it.
- **A fresh Tailscale approval for aifoundry3.** One approval lasts about 12 h: the window's last end must come before it lapses.
- **Nothing else needs his word:** aifoundry3 card 0 at 600 MHz pinned; one session of ours on the box; the stops (65 W, 70 C); every
  device command a READ; the day's one post.

## 2. Before anything

- `git pull --ff-only` in the lab clone, **under the lab-git lock** (other lanes commit in the same clone): step 2 does it itself with
  `RB_GITLOCK` set; never a bare pull beside another lane's commit.
- **One `RB_OUT` for E186** (outside the repo, new and empty), **one `RB_LOCK`** (the file a login check is appended to), and
  **`RB_GITLOCK`** (the lab-git lock's path, outside the repo). None of the three is written in any committed file.
- **Step 1 first, on the day itself:** `rb/s02_window_e186.sh <today> <last start> <last end>`. Step 2 and every E186 step that starts
  something on the box or copies from it refuse a window not written today (Pacific), not naming today, or written for another runbook
  (RB_PLAN e186); the wait reads the T0 the runbook launched today. A window written yesterday serves nothing.
- **Step 2, the desk check,** must read 0: the paths clean, **the history check's HISTORY OK** (no change but an addition since E186's
  registration `a41408d9` on E186's paths, no added file that shadows a module, nothing uncommitted: `rb/check_history_e186.py`), the
  eleven lists at their counts and bytes, the kit's at 74, HARNESS OK 71, NOTE1 FILES OK 10, the plan and forecast re-made, no E186 datum
  in any ref. Note M1's list is read and reported, never a gate; a later dated M-note's list likewise.
- **Anything but 0 from step 2 is no box step that day,** whatever it names (status, ancestry, history, a list, the harness, a log): the
  records say what it named. One exception: a 16 naming the pull whose output shows the upstream did not answer (the network's): run step
  2 again once it answers. A diverged or detached clone is no exception. A 13 (a call past its bound) or an 11 (a login link) is k6's:
  run the step again, after the approval for an 11.
- **The Tailscale-lapse rule:** a printed login link stops the step at once (exit 11) and appends `<HH:MM:SS> aifoundry3 needs a check`
  to `RB_LOCK`; nothing waits on it and nothing retries in a loop. After he approves, run the same step again. A session already detached
  on the box keeps running while the link is open; collect it when the box answers, inside the window.

## 3. Look before the post, then the box steps in order

1. **The look** (box step 4, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3`, then `--wait` while the card is held, at most 30 minutes
   in all, then skip the day): it must read FREE. An idle login does not block (the owner's ruling of 1 Nov 2026); a holder of a device
   node, the card's lock or another user's device process does. **Never beside another session of ours on aifoundry3:** steps 6, 8 and 9
   refuse it by code (k6's `ours_live`), and E183's and E185's sessions must have ended and been collected first.
2. **Only then the day's one post** (box step 3): the lab's one-post-a-day rule, under the post's lock, with `EXPECT_TEXT`. If a post for
   the day exists, rewrite it; never a second post, never an earlier day's. One line:
   `<ai> **Claude says:** using aifoundry3 for 2 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`
   (PASSES: `for 1 h`). At the release, append ` — released` to whatever the post then says, every word kept.
3. Step 5, the sync; step 6, the build (`start`, then `wait` while it says 17, or 14 with "no reading"; the rules in section 5); step 7,
   k6's reads; step 8,
   the dry pass (`start`, then `wait` while it says 17); step 9, `FULL yes`; step 10, the wait, while it says 17; the release; step 11,
   the collection.
4. **Never step 6, 8 or 9 while a session of ours runs on the box**, and never a second build after a good one the same day (step 6
   refuses it: a rebuild would remove the good host first).

## 4. What stops the session (each registered; nothing is retried)

| where | what stops it | what follows |
|---|---|---|
| the session's start | no window gates, past the last start, an unknown plan or switch, an E186 block directory already on the box | exit 8, no device opened |
| | the harness check (any reused, E186 or E182 file, tile, binary or the train host off its pin) | exit 9, no device opened |
| | the device-command preflight not GO | exit 3, no device opened |
| the stop-path test 18602 | any of die, board and watch not reading rc 6 (the block); or its STOP not naming the stop and the sample's age (read by the smoke's kinds gate) | no smoke, no block; or no block runs |
| the smoke 18601 | its kinds gate fails (records, ok, cycles, clocks, configs 0 W / 65 C / 600 MHz, dumps, telemetry, C log pairing, launch gaps) | no block runs |
| | its train gate fails (H16's two processes: schedule, tiles, rates, the train host's C records) | the queue runs PASSES, every train rule NOT SCORED |
| any block | board at or above 65 W, or `minshire[0]` at or above 70 C, on a live sample (before every launch and process, every 0.1 s in the watcher) | that block stops, the queue stops after it |
| | another user on the card or a device process (rc 3); any block failure (rc 1) | the queue stops after it |
| the queue | the next item's projection past T0 + the cap - 60 s, or past the last end | stops before it; nothing skipped ahead |
| any time | `build/e186/STOP` on the box | the queue stops before its next item |

**The commands:** every device command is a READ (`ettelem config`, `ettelem sample` through E128's guard: the config reads, the clock,
the PMIC voltage reads the owner's rule of 2 November 2026 allows, power, stats and temperature); the train host opens the card through
the runtime only. **No statistics reset, no firmware-revisions query, no residency read, no SET of any kind, no governor, TDP, threshold
or clock set, no reset, no power cycle and nothing that risks one;** nothing near card 0's 75 W alarm (one-number kinds draw less than
random tiles; E182's highest reading was 54.17 W). Never another user's process or session; no lab user's login in any file.

**The caps:** FULL about 93 card-minutes (cap 100), PASSES about 28 (cap 40).

## 5. Step 6, the train host's build: E182 v5's rules

- TRAIN-HOST-BUILT, then NOTE1 FILES OK 10, HARNESS OK 78, GO and the verify: go on to step 7.
- A build that failed, overran its 500 s bound or was lost (16, "build 1 of at most 2 today"): run `start` and `wait` **once more**.
  If that fails too, or `start` says "no third": the registered fallback, as the step names it: step 6 `--no-trains`, step 7, step 8
  `start --no-trains` and `wait --no-trains`, step 9 `PASSES no`, steps 10 and 11.
- TRAIN-HOST-INPUTS-DIFFER (16): step 5 once more, then step 6 `start`; if they differ again, the fallback.
- **11, 12 or 13 on `start`: run `wait` first;** start again only if wait reads JOB-UNKNOWN or the step asks. **14 on `wait`: "no
  reading" is a network fault, never a failed build: run `wait` again, and no other step-6 call until it reads.** Any other 14 (as "the
  build job ended rc 0 without its TRAIN-HOST-BUILT line") names what to read on the box: read it, read-only; no other step-6 call
  until the records say what it was.
- The data README states step 6's outcome from the box's count file and each build's log (step 11 copies them into `logs/step6/`).

## 6. After the session

- **Step 10** until RUN-ENDED, with MANIFEST-WRITTEN. A gate stop (16) is still collected.
- **The release** of the day's post.
- **Step 11** (`rb/s22_collect_e186.sh`, inside the window): it copies the session's own directory and exactly the block directories it
  ran, reads them **COPY-BACK EXACT** against the session's manifest (anything else stops it: move `build/e186-raw` aside, read the box
  read-only, then collect again), then **the history check again before any scoring** (a change since step 2 stops it, 16: the raw
  copy stays, nothing is scored, a dated note first), then the check of C, the reductions (the trains; the float trains' anchors for the
  scale), the scorer, the C-session gate, the desk-path gate, the login scrub, and **note M1's reader after the score, only through its
  gate** (`check_history_e186.py m1`: note M1's list at 5 and its own bytes with every entry OK and its files unchanged, then the reader
  by note M1's own run line; `arm-m1-e186.json` and `.txt`). M1-NOT-RUN or the reader's refusal is recorded in the data README and never
  blocks the data commit; M1-WROTE-OTHER (the reader changed another file) stops the step before the data commit. It refuses a used
  output.
- **The data commit:** the public-text scan over the files and the commit message, its exit status read with no pipe masking it, then
  `commit_lab.sh` with the data directory's own paths only, new files only.
- Then the data verifier, a fix if needed, a critic, and ONE records round.

## 7. The words the records use

- E186's verdicts are its rules' own words (E186.md section 5): each train's SIGN, SIZE against M12's band, SIZE against M10 and WHICH;
  E186-H16's arm word (F16-SAME, SCALED, M10, a "+" of them, or NONE); the splits' words; E186-M's M12 / M10 / BOTH / NEITHER.
- **s not read** (fail closed) is a reading, not a failure: the four ladder trains' SIZE words, E186-GB and E186-GA read NOT SCORED, and
  KIT.md section 4 says why they also leave E186-M.
- For the six trains whose two kinds give the same C, E186-C's PASS is the arithmetic, not the pairing (KIT.md, "Results first").
- october-forecast-model is named only so, and its arm is reported, never a verdict: M1-READ, M1-NOT-RUN and M1-READER-REFUSED are
  records lines.
- A train's forecast half-width is about 0.0051 W at E182's registered noise (0.0060 for the float trains at its measured noise).

*Labels: every plan, cap, stop, clause and verdict word above is **registered** (E186.md, its note M1, E182's kit and brief as E186's kit
takes them); nothing here is blind, held out or measured.*

SPDX-License-Identifier: Apache-2.0
