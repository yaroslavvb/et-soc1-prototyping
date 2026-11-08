# The card lane's brief, dated note 2: after step 6's "no reading", wait again and nothing else; E184's step 2 and the window; E182's steps 2 and 6 are v5; E184 runs by its kit note 3 (Q155; E182's kit, dated note 4)

*Sat 7 Nov 2026 (week 45), first written 21:11 PST on the Intel, desk only (Q155, lane `fix-q154k`): no card was claimed, no device command
was sent, no lab box was reached, nothing was posted. It sits beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) (`22da6a7b`) and
[CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md) (`e0d31903`), which stay as committed, and E182's kit note 4
([KIT.md.dated-note-4.md](KIT.md.dated-note-4.md)) lists it. It answers critic-q154's nits 2 and 3 (Q154's readiness critic, 19:14-19:49 PST
today) and the adversarial verifier of e0d31903, 3b48cf7b and 571511d0 (`verify-q154k`, 19:55-20:29 PST: holds with fixes), its fault 1 (a).
**Where this note and the brief or its note 1 differ, this note governs.** The brief's order on the boxes (its section 2), look before the
post (section 3), the day's one post (section 4), and the stops, commands and caps (section 6) stand as written. It adds no rule.*

## 1. After step 6's "no reading", wait again, and no other step-6 call (critic-q154's nit 2; verify-q154k's fault 1)

k6's `rb_job_wait` prints "no reading (rc 14)" when a wait call fails or is cut before the box prints JOB-DONE, JOB-LOST or JOB-RUNNING (a
dropped link: ssh's 255). That is a network fault, never a build's failure.

- **On the card day step 6 is v5** (`rb/s08_a3_preflight_e182_v5.sh`, the kit's note 4). Its wait says it itself: on "no reading" it stops
  with **14**, "no reading of the build job ...: nothing is counted; run this step's wait again, and no other step-6 call (start or
  --no-trains) until it reads". **Run wait again**, while it says 14 or 17, before any other step-6 call. The same holds for a 14 "no reading
  of <check>" after the build (run wait again) and in the fallback (run `--no-trains` again).
- **If step 6 v4 runs by mistake:** after a **16** from its wait whose lines show "no reading (rc 14)" and no JOB-DONE or JOB-LOST line, run
  **wait again before ANY other step-6 call, `start` or `--no-trains`, and never take the fallback on that reading**, whatever the 16's own
  words say (at the day's second build they name the fallback). A 16 from v4's checks after the build, "a binary or file differs: a dated
  amendment first", that follows a 14 call in the runbook log (`rc=14 child_rc=255`) is also a cut read: run wait again. Then go on with v5.
  Step 6 v3 is never run on the card day.
- **`--no-trains` is refused (10) after a good build that day** under v5 ("the registered fallback is for a failed build"): run wait, which
  reads the build's checks. The fallback runs only after two builds that did not read TRAIN-HOST-BUILT (or after a second
  TRAIN-HOST-INPUTS-DIFFER, note 1's rule), as the step names it.
- The brief's note 1 still holds for start: after 11-14 on start, run wait first.

## 2. Run each runbook's s02 first (critic-q154's nit 3)

The brief's section 1 says of the three runbooks: "Each one's box step 1 (its `s02_window`) comes first; each step 2 refuses without it."
That held for E182's step 2 only. **E184's step 2 v2 (`rb/s03_desk_e184_v2.sh`) does not itself refuse without the window**; its dry pass,
launch and collection do. E184's step 2 v3 (its kit note 3) now refuses too. Either way: **run each runbook's `s02` first, for each RB_OUT**
(E182; E184 arm S; E184 arm B), then its step 2.

## 3. E182's steps 2 and 6 are v5 (the kit's note 4)

| KIT.md box step | the file on the card day | changed here |
|---|---|---|
| 2, the desk check | **`rb/s03_desk_e182_v5.sh`**: six lists at pinned counts, **32, 79, 50, 49, 89 and 19** | v5 |
| 6, the build and the box's checks | **`rb/s08_a3_preflight_e182_v5.sh start`, then `wait` while it says 17 or 14** (or `--no-trains` for the fallback) | v5 |
| every other step | as the brief's note 1, section 3 | no |

The brief's section 5 and note 1's section 2 read with v5's words: a failed, overrun or lost build (TRAIN-HOST-BUILD-FAILED, -OVERRAN, or
JOB-LOST) is 16, "build 1 of at most 2 today": the one re-run; the second names the fallback, which starts with step 6 **v5** `--no-trains`.
Everything else there stands (TRAIN-HOST-INPUTS-DIFFER, the good-build refusal on start, the data README's step-6 outcome).

## 4. E184 runs by its kit note 3

E184 gained dated amendment A4 ([`../e184/E184.md.dated-note-A4.md`](../e184/E184.md.dated-note-A4.md), committed alone) and its kit's dated note
3 ([`../e184/KIT.md.dated-note-3.md`](../e184/KIT.md.dated-note-3.md)). **Kit note 3's section 3 table governs E184's steps**, by the brief's own
clause:

| E184 box step | as the brief's note 1 read it (kit note 2) | now (kit note 3) |
|---|---|---|
| 1, the window | first | first; step 2 v3 refuses without it |
| 2, the desk check | `rb/s03_desk_e184_v2.sh`, six lists | **`rb/s03_desk_e184_v3.sh`, eight lists pinned: 11, 44, 6, 45, 3, 20, 1 and 18** |
| 11, collect | `rb/s22_collect_e184_v2.sh S\|B` | **`rb/s22_collect_e184_v3.sh S\|B`**: `collect_e184_v3.sh`, which reduces with `reduce_e184_v4.py` (A4) and scores with `score_e184_v3.py`; `scored-e184-v3.*` govern |

A4: a session config read lacking `tdp_w`, `temp_threshold_c` or `minion_mhz`, or holding a null among them (a failed GET), is MISSING and
replaced by step 7's read, as A3-3 says; a complete read not as registered still voids the arm. A replacement is named in the data README with
the step-7 read used and the replaced read's status. A4 leaves E184's plan, caps and stops unchanged. Steps 7 and 10b (`rb/s09_reads_e184_v2.sh`)
are unchanged; `$RB_OUT/config-B-reads.json` holds the latest of arm B's reads, and the box keeps both (kit note 3 section 6).

*Labels: every pin, plan, cap, stop and step named here is **registered** (E182's and E184's kits, notes and amendments). The desk tests that
show step 6 v5 and reduce v4 are checks of code. Nothing here is blind, held out or measured.*

SPDX-License-Identifier: Apache-2.0
