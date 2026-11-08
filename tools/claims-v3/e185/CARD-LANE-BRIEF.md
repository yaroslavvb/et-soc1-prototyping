# The card lane's brief for day 2, E185 then E183 on aifoundry3 card 0: E185 first in the cool morning hour, E183 only after E185's step 14, each run's step 2 at its latest version, one RB_OUT each, the "no reading" line, and october-forecast-model's notes as reported arms only (dated Sun 8 Nov 2026, before any E183 or E185 datum; Q157)

*Sun 8 Nov 2026 (week 45), first written between 06:33 and 06:50 PST by the clock on the Intel, desk only (Q157, lane `fix-d2`); its
commit's own time is git's. No card was claimed, no device command was sent, no lab box was reached, nothing was posted. It sits in
E185's kit beside [KIT.md.dated-note-2.md](KIT.md.dated-note-2.md), which lists it, and an identical copy of sections 1-6 sits in E183's
kit as [`../e183/CARD-LANE-BRIEF.md`](../e183/CARD-LANE-BRIEF.md). It is for the card lane of day 2 (Mon 9 Nov 2026 at the earliest, on
the owner's go), read before either runbook. It restates what the two kits and their notes register, as the readiness critic of Q155
planned day 2 and the adversarial verifier of E183's and E185's last fixes (`verify-d2`, Sun 8 Nov 2026 05:22-06:08 PST) asked. **It adds
no rule, forecast, threshold, plan, cap, stop or order.** The one change in the runbook's order, step 2 v3 run again just before E185's step
14, is E185's kit note 2's fix of `verify-d2`'s fault 2, restated here. Where a kit's own text says less about the other run on the box,
this brief's order binds; everything else is each kit's. No E183 or E185 datum exists (`git log --all` on `docs/reports/data/*e183*` and
`*e185*`: nothing).*

The runbooks: **E185** by its kit's [dated note 1](KIT.md.dated-note-1.md) table, with step 2 as v3 by its [dated note 2](KIT.md.dated-note-2.md);
**E183** by its kit's [dated note 1, section 8](../e183/KIT.md.dated-note-1.md) (`45e514e3`). Step numbers below are each kit's own.

## 1. Before anything

- **His go** names the day and one window in PST (the last start and the last end), with E185 launching before 12:00 PST, and gives a fresh
  network approval for aifoundry3. Nothing below runs without both. No other box is needed.
- `git pull --ff-only` in the lab clone.
- **One `RB_OUT` per runbook**, each outside the repo: one for E185, another for E183. **One `RB_LOCK`** for the whole day (the Intel's
  lock file of checks). Each runbook's step 1 (its `s02_window`) comes first, for its own `RB_OUT`; each step 2 refuses (10) without a
  window written that day.
- **Each run's step 2 at its latest version:**
  - E185: **`rb/s03_desk_e185_v3.sh`** (E185's kit note 2): E185's five lists at their pinned counts and their own committed bytes (8, 13,
    21, 5 and 28) and the kit note 2's list at its count (16), beside M11's seventeen lists and the footing law's two at theirs.
    october-forecast-model's note M1's list (21) is read and reported, never a gate. It runs twice: as step 2, and again just before step
    14 (section 2, item 3).
  - E183: **`rb/s03_desk_e183_v2.sh`** (E183's kit note 1): three lists at 20, 46 and 46, with no override.
  - Never a v1 step 2, and never E185's step 2 v2.
- A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`. There is no retry loop: after
  the approval, the same step is run again.

## 2. The order on aifoundry3 (card 0 only, 600 MHz pinned, nothing set)

Each step file is named from its own run's kit directory, `tools/claims-v3/e185/` or `tools/claims-v3/e183/`; k6's from
`tools/claims-v3/q141k-runbook/k6/`.

| | the run | its steps |
|---|---|---|
| first | **E185**, M11's session 3, in the cool morning hour | 1 `rb/s02_window_e185.sh`; 2 **`rb/s03_desk_e185_v3.sh`**; 3 the look, `rb/s05_look_e185.sh aifoundry3`, FIRST; 4 the post; 5-7 `rb/s07_a3_sync_e185.sh`, `rb/s08_a3_preflight_e185.sh`, `rb/s09_a3_reads_e185.sh`; 8 `rb/s10_a3_dry_e185.sh start`, then `wait`; 9 `rb/s12_a3_host_e185.sh start`; 10 `rb/s11_a3_launch_e185_v2.sh [--later-try] [--under-an-hour] [--after-noon]`; 11 `rb/s20_wait_e185.sh`, again while it says 17; 12 `rb/s12_a3_host_e185.sh end`; 13 the release; **then step 2 v3 again**, and only on its 0, 14 **`rb/s22_collect_e185_v2.sh`** |
| then | **E183**, the one-number vector add's round 2 | from its look on, only after E185's **step 14** has copied E185's files back: 1 `rb/s02_window_e183.sh`; 2 **`rb/s03_desk_e183_v2.sh`**; 4 the look, k6's `s05_look_k6.sh aifoundry3`, BEFORE 3 the post; 5 `rb/s07_a3_sync_e183.sh`; 6 `rb/s08_a3_build_e183.sh start`, then `wait` **while it says 17 or 14**; 7 k6's `s09_a3_reads_k6.sh`; 8 `rb/s10_a3_dry_e183.sh start`, then `wait`; 9 `rb/s11_a3_session_e183.sh FULL` (or `SHORT`); 10 `rb/s20_wait_e183.sh`, again while it says 17; 11 the release, then **`rb/s22_collect_e183_v2.sh`** |

Never E185's v1 steps 2, 10 or 14 (`s03_desk_e185.sh`, `s11_a3_launch_e185.sh`, `s22_collect_e185.sh`), and never E183's v1 steps 2 or 11.

1. **E185 first, in the cool morning hour.** It is launched before 12:00 PST: step 10 v2 refuses at or after noon unless `--after-noon`, a
   logged departure from A7-4's plan. It is launched at least 40 minutes after our last real session end on aifoundry3, the rest gate step 10
   v2 reads from every log of ours on the card (E183's and E184's log forms among them), and an hour after it by A7-4's plan: under an hour
   step 10 v2 refuses unless `--under-an-hour`, a logged departure. Our last real session there so far is E184 arm S's, which ended Sun 8 Nov
   2026 02:22:24 PST by its own log (`docs/reports/data/2026-11-08-e184-sensor-validation/raw/aifoundry3/logs/session-S-t1794133299.log`,
   `13a4b34d`); the gate still reads the box's logs on the day. (E185.md section 8; M11's A7-4; E185's kit note 1.)
2. **E183 only after E185's step 14.** E183's look, sync, build and dry pass start only after E185's **step 14**, its collection
   (`rb/s22_collect_e185_v2.sh`), has copied E185's files back to the Intel. Where E183's notes say "after E185's step-11 copy-back"
   (E183.md's dated note 1, section 5; E183's kit note 1, section 6), read **E185's step 14**: in E185's own numbering step 11 is the wait
   and step 14 the collection, and E185.md section 8 says "after E185's collection has copied its files back". E183 never starts before E185
   on that day. E183's own launch step has no rest rule of its own (k6's guard only), so this order is what keeps E185 first on a rested card.
3. **Before E185's step 14, step 2 v3 again**, the same command with E185's `RB_OUT`. Step 14 v2 reads its eight lists by shasum's exit
   status alone, an hour or two after step 2 (`verify-d2`'s fault 2); step 2 v3 reads all eight at their pins on the tree step 14 runs on
   (E185's five at their counts and bytes, M11's three at their counts). On its 0, run step 14. On a 16 whose "the desk check failed:"
   line names a list (with its count, its pin or its bytes), step 14 does not run: E185's files stay on the box, read-only, and a dated note
   decides first. On a 16 that names `pull` alone, run step 2 v3 again once the network answers. E185 is launched before noon, so its step 14
   falls on the day its window was written.
4. **One session of ours at a time.** A dry pass, a build or a launch is refused beside a session of ours (k6's guard; E183's step 6 also
   beside a running runbook job).
5. **The window gates each launch.** No session starts after the last start. E185 needs 6,300 s before the last end (step 10 v2), E183
   FULL 3,900 s and SHORT 1,920 s (its cap from T0). SHORT is chosen only when the window cannot fit FULL; it runs T3, T1, T4 and T2, so it
   reads neither his pair (T5) nor the exponent control (T6).
6. **E183's build.** A failed, overrun or lost build (16) gets one re-run, `start` then `wait`; after a second, the registered fallback
   SKIP: no E183 that day, and no card time.

## 3. The "no reading" line, on every k6 job wait

k6's `rb_job_wait` returns 14 for a job that ended non-zero, for JOB-LOST, and for a cut call: a dropped link, where the call fails before
the box prints JOB-DONE, JOB-LOST or JOB-RUNNING. **A 14 whose lines show "no reading (rc 14)" and no JOB-DONE or JOB-LOST line is a cut
call: run the same wait again**, and no other call of that step until it reads. Only JOB-DONE with a non-zero rc, or JOB-LOST, is a failed
job. The job waits of day 2:
- E185's step 8, `rb/s10_a3_dry_e185.sh wait`;
- E183's step 6, `rb/s08_a3_build_e183.sh wait`, which says so itself: 14, "no reading of the build job ...: run this step's wait again
  before any start". So it waits while it says 17 or 14;
- E183's step 8, `rb/s10_a3_dry_e183.sh wait`.

The session waits read the same way: a 14 "the wait on e185 exited ..." (or e183) with no RUN-ENDED, RUN-GONE or gate line is a cut call.
Run the same wait again: the session runs detached on the box, and a wait never touches the card. (critic-q155's line; no code changes.)

## 4. The day's one post

The lab's rule: find the day's post first; every reservation and release rewrites that one post, never a second post and never an earlier
day's. One line, opening with `<ai> **Claude says:** `, then one clause:

| run | the clause |
|---|---|
| E185 | `using aifoundry3 for 2.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)` |
| E183 FULL | the same with `for 1.5 h` |
| E183 SHORT | the same with `for 1 h` |

After E185's look reads FREE, the post carries E185's clause. It stays until E183's look reads FREE, then becomes E183's clause (or is
released, if E183 does not start that day). The last release appends ` — released` to whatever the post then says, every word kept. Every
change is made under the post's lock and rewritten with EXPECT_TEXT.

## 5. Card-minutes, stops and commands (registered; unchanged)

| run | expected card-minutes | cap | stops on a live sample |
|---|---|---|---|
| E185 | about 103 | 105 (the measured pass's deadline T0 + 104 min) | `minshire[0]` at or above 70 °C, the board at or above 65 W, or the 34-sensor mean at or above 72 °C ends the hold and the pass; no launch at a firmware reading at or above 70 °C |
| E183 FULL | about 52 | 65 (3,900 s from T0) | the board at or above 65 W or `minshire[0]` at or above 70 °C, read before every burst and process and every 0.1 s; a stop ends the session |
| E183 SHORT | about 26 | 32 (1,920 s) | the same |

In all about 155 card-minutes (caps 170), or about 129 (caps 137) with SHORT: about 4.5 h on aifoundry3 with the box steps, then about
30 minutes of collection at the desk. **Every device command is a READ.** E185 sends no statistics reset; E183's one conditional statistics
reset (lib.sh line 154) is never reached, as in E180. No governor, TDP, threshold or clock set; no firmware, PMIC write, reset or power
cycle; no firmware-revisions query. A stop ends that run's queue, and nothing is retried.

## 6. october-forecast-model's notes M1: reported arms only

- `tools/claims-v3/e183/E183.md.dated-note-M1.md` (`06286213`) and `tools/claims-v3/e185/E185.md.dated-note-M1.md` (`2f6a4440`) carry
  the model's v3 and v4 as **reported arms**, committed before any datum. They are never a rule, never one of E185-BEST's arms and never
  one of E183-MECH's lines, and their readings use words of their own (inside, above or below), never a scorer's verdict words.
- **E183's reader** runs after E183's step 11 collection (`rb/s22_collect_e183_v2.sh`) and before the data commit. **E185's reader** runs
  after E185's **step 14** (`rb/s22_collect_e185_v2.sh`; its note's "step 22" is this step) and before the data commit.
- Before each reader, its own list, from the lab's top: `shasum -a 256 -c tools/claims-v3/e183/SHA256SUMS-e183-m1` must read 25 of 25 OK,
  and `shasum -a 256 -c tools/claims-v3/e185/SHA256SUMS-e185-m1` 21 of 21 OK (E185's step 2 v3 has read it twice by then). Otherwise the
  reader is not run, and the data README records the refusal.
- The run lines, from the lab's top:
  - `/usr/bin/python3 -B tools/claims-v3/e183/arm_m1_read_e183.py --reduced <data dir>/reduced-e183.json --scored <data dir>/scored-e183.json --out <data dir>/arm-m1-e183`
  - `/usr/bin/python3 -B tools/claims-v3/e185/arm_m1_read_e185.py --data <data dir> --out <data dir>/arm-m1-e185`
- A reader's refusal, or any non-zero exit (E185's reader stops with rc 1 on a score whose start gate carries no room, a latent case:
  `verify-d2`'s nit 9), never blocks the data commit. The data README records it, with the reader's output.

## 7. E185's collection and its data README

- Step 14 v2's "left on the box" line, if any, names an earlier try's directories; they stay on the box (E185's kit note 1).
- **The README quotes E185-C's consequence from its F line only** (A1-2): the scorer v5's `E185` > `rules` > `E185-C` prints F, B and Rl,
  and only the F line governs; B's and Rl's are reported, with A1-2's offsets beside them.
- **The pooled HM-CAL and HM-CAL-I8 verdicts printed with E185 are E181's, never E185's** (A1-3): scored-m11.md's A10 line prints them
  bare, whatever their word (in `verify-d2`'s stand-in case, "HM-CAL BETTER; HM-CAL-I8 BETTER", carried by E181's two-pass points alone).
  A record never quotes either as an E185 result.
- E185's verdicts are quoted on A10's reading (registered), with the stated reading's arm (`E185` > `one_pass_reported`) beside them (A1-1).

## 8. After the day

Each run's data verifier, then a critic, then ONE records round, which quotes this brief's corrected words (E185's step 14, never "step-11
copy-back"; E183's step 6 "while it says 17 or 14"; the trains' half-widths by the t statistic) and E185's kit note 2's lines for the records.

*Labels: every pin, plan, cap, stop, clause, step and order named here is **registered** (E185.md with A1, E183.md with its note 1, M11's
A7-4, the kits and their notes); E184 arm S's end time is **post hoc** (its committed log); october-forecast-model's arms are **reported**,
their forecasts **blind** for E183 and E185 (frozen before any datum); the desk tests are checks of code. Nothing here is held out or
measured.*

SPDX-License-Identifier: Apache-2.0
