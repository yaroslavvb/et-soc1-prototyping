# E198's card-lane brief after amendment A1: the steps that run E198 on aifoundry1 card 1 with the lab's runner copy, which kills nothing (Q196; kitted, not run)

*Mon 16 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q196, lane `a1-e198`), beside [E198.md.dated-amendment-A1.md](E198.md.dated-amendment-A1.md)
and [KIT.md.dated-note-A1.md](KIT.md.dated-note-A1.md). It replaces [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) (kit-e198, unchanged beside
it) for every E198 sitting after A1. No card was claimed or opened, no device command was sent, no lab box was reached, nothing was posted.
No E198 datum exists. This brief changes no arm, value, order, window, threshold, stop, cap, rest, rule, the reduction or a forecast.*

## 1. What the day carries (CARD-LANE-BRIEF.md 1, with A1)

- **Everything in CARD-LANE-BRIEF.md section 1 stands:** the go (the owner's standing words of Sun 15 Nov 2026 and "Try again"), the
  post waived, aifoundry1 card 1 at 600 MHz as found with `--device 1` and card 1's lock, nothing on card 0, the order on card 1, the
  sealed card-1 forecast (freeze line 2) and the dated note for a further one.
- **The runner is the lab's copy** `run_x04_e198a1.py` (A1): E193's runner with the kill path changed and nothing else. Every device
  process runs under a plain `timeout 10`: TERM at 10 s, **never a KILL**. A device process still running 25 s after it started is reported
  at once ("device process not ended: tell the lab admin") and left running. The runner's clean-up sends its `timeout` SIGTERM three
  times (at once, after a 15 s wait, after a 60 s wait) and never a KILL. GNU timeout ignores every TERM sent to it once it has passed
  one on or sent its own at 10 s, so such a host receives **one TERM in all**, its timeout's own at 10 s (two if the runner itself was
  signalled in the host's first 10 s); the clean-up's TERMs to the timeout are no-ops (the dated fix, verify-a1e198's finding 2;
  coreutils 9.4 as read on aifoundry2, aifoundry1's not read). The clean-up then **stops the runner's sampler with SIGTERM all the same**
  (hunk K9, the dated fix), so the sampler does not hold card 1's management node. The session then sends nothing else to the card.
- **The landed anchors:** the registration, the kit and A1 (A1's list `SHA256SUMS-e198-amendment-A1` and step 2 (A1),
  `rb/s03_desk_e198a1.sh`, outside that list, at the sha256s A1's LAND.md gives), all ancestors of GitHub main. **A1 needs its own
  readiness check and new go lines** before any sitting (ready-e198's GAP 6: the old go lines' anchor read refuses any addition under
  `tools/claims-v3/e198/`, and they call steps A1 replaces).

## 2. THE WINDOW FROM G

Unchanged (CARD-LANE-BRIEF.md 2): G is the card lane's booking of aifoundry1. Last start G + 1:30 and last end G + 3:30, rounded up, inside
G's Pacific day, with G at 20:29:00 or earlier. Sitting B's G is A's session end + 40 minutes.

## 3. The steps, in order, for EACH sitting (paths under `tools/claims-v3/e198/`), with THE ONE-LAB RULE and THE QUIET HOLD

Every row and every stop path of CARD-LANE-BRIEF.md section 3 stands. **Only the files change where A1 has its own** (marked A1). Steps 1,
4, 7 and 13 are v1's, unchanged: they never touch the runner. **Never run the v1 files of steps 2, 5, 6, 8, 9, 10 or 11 for E198 after A1.**
(v1's step 9 also refuses on A1's day by itself: A1's build and dry-pass jobs carry their own names, so v1's checks find no build or dry pass
of today.)

| # | the step | what to do with its exit |
|---|---|---|
| — | the booking (`bash W/book.sh take aifoundry1 <lane>`: G); the quiet hold (`bash W/hold.sh add <lane>`); **`bash W/onelab.sh desk <lane>`** | as v1 (from here to step 2, every stop path runs `undesk`) |
| 0 | by hand: `uptime` (THE LOAD RULE), GitHub main read, **the anchor lines of the registration's, the kit's and A1's LAND.md** (the new go lines') | any line not as stated: undesk, release the booking, remove the quiet hold; no box step that day |
| 1 | `rb/s02_window_e198.sh <A\|B> <day> <G>` (v1) | as v1 |
| 2 | **A1:** `rb/s03_desk_e198a1.sh` with `RB_GITLOCK`, never inside the lab-git lock | 0: the lists at their pins (A1's among them), A1's commit after the kit's and nothing under `tools/claims-v3/e198/` after it (the dated fix: else 16 "after-A1"), the runner copy re-made and equal, harness-e198-a1.json, the preflight GO, A1's desk-test logs, no E198 datum; anything else: undesk, release, remove the hold |
| — | **`bash W/onelab.sh undesk <lane>`** | always, whatever step 2 read |
| 4 | `rb/s05_look_e198.sh` (v1) | as v1 |
| 5 | **A1:** `rb/s07_a1_sync_e198a1.sh` | 0: harness-e198-a1.json's files in E198's root, HARNESS OK and TREE OK on the box; 10/16: no sitting until fixed |
| 6 | **A1:** `rb/s08_a1_build_e198a1.sh start`, then `wait` while 17 | 0: X04-BUILT by `build_e198a1.sh` (the kernel gate, the bodies, the host's refusals, **the listing on the lab's copy SAME x3**; the record names `build_e198a1.sh`), under a plain `timeout 900`; 16: once more if the day's first, then NO-THIRD-BUILD (the count reads v1's and A1's names) |
| 7 | `rb/s09_a1_reads_e198.sh` (v1) | as v1 (17 before the rest opens; 16 card 1 not as found) |
| 8 | **A1:** `rb/s10_a1_dry_e198a1.sh start`, then `wait` | 0: `session_e198a1.sh` with DRY=1 on the box, both listings SAME through `check_e198a1.py` |
| 9 | **A1:** `rb/s11_a1_session_e198a1.sh <A\|B>` | 0 launched (`session_e198a1.sh`); 10 refused, every v1 refusal (an earlier E198 sitting with a device process that did not finish among them: A1's own lines included); 16 IDENTITY-STOP |
| 10 | **A1:** `rb/s20_wait_e198a1.sh <A\|B>` again while 17 (it finds `session_e198a1.sh` by its real name) | 0 ended; 16 a gate stop, MAIN-CRASHED, or **DEVICE-NOT-ENDED** (section 4); **a 17 that prints "A DEVICE PROCESS DID NOT END ... REPORT IT ... NOW": report to the owner and the lab admin at once, then call again**; 14 RUN-GONE |
| — | **`bash W/onelab.sh collect <lane>`** right before step 11 | as v1 (to the data commit's push, every stop path runs `uncollect`) |
| 11 | **A1:** `rb/s22_collect_e198a1.sh <A\|B>` (refuses while `session_e198a1.sh` or `session_e198.sh` runs) | as v1 |
| 12 | the README in **[DATA-README-FORM-e198-a1.md](DATA-README-FORM-e198-a1.md)**'s form (E198's own freeze lines: GAP 4 corrected; no departure from the form needed), the public-text scan, the data commit, its push | then `bash W/onelab.sh uncollect <lane>` |
| 13 | `rb/s24_reduce_e198.sh <A\|B>`, then `score` (v1) | as v1 |
| — | sitting B: its own RB_OUT, G = A's session end + 40 minutes, steps 1-13 again (step 6: `wait` only) | as v1 |

**To stop a sitting by hand** (the operator's stop): touch the running runner call's stop file, `build/e198/T<T0>/smoke/STOP` or
`build/e198/T<T0>/x04/STOP`, and `build/e198/T<T0>/STOP`, as in v1. **Never kill a process.** The runner ends its own device process with
SIGTERM to its timeout and never with a KILL, and it stops its sampler with SIGTERM (also after a device process that did not end: K9).
Never a reset, a driver reload or a power cycle.

## 4. After a stop (CARD-LANE-BRIEF.md 4, with A1's device process not ended)

- A gate stop, a registered stop, a watch hit and a crash: as CARD-LANE-BRIEF.md section 4.
- **A device process that did not finish** (v1's paragraph stands) **and, under A1, A DEVICE PROCESS NOT ENDED.** The signs: the runner's
  "device process not ended" line, the session's "A DEVICE PROCESS DID NOT END", step 10's DEVICE-NOT-ENDED.
  - The process outlived its timeout's TERM. It was not killed and is not to be killed: no KILL, no `kill -9`, no `timeout -k`, no reset,
    no driver reload, no power cycle.
  - Report it to the owner and the lab admin at once, with the runner's line, the process (`ps` read-only on the box) and the card.
  - Stop the day and keep the booking.
  - The session sent nothing else to the card: its closing config read is skipped.
  - The runner stops its sampler with SIGTERM all the same (hunk K9, A1's dated fix; E193's clean-up had left it until its own
    `--seconds`, up to about 79 minutes on card 1's management node). The runner call's `run.log` says "E198 A1: the sampler is stopped
    all the same (SIGTERM), so it does not hold the management node". If it also says "sampler did not stop within 10 s of SIGTERM",
    report that sampler with the process (`ps` read-only); never signal it yourself.
  - **Card 1's lock is free once the runner has exited, while the host left running still holds card 1's ops node** (its `timeout` and
    the host wrapper `x04host_e198.sh` wait for it; they open no device node). `et-who` shows the host; report the lock and et-who's
    lines with the process.
  - **`x04host_e198.sh`'s header is stale:** the wrapper is v1's, unchanged, pinned and synced, and its header still says "`-k 1` still
    kills the group a second later". That described v1's runner. Under A1 nothing sends a KILL; the wrapper's code is unchanged (on a TERM
    it waits for the host and then ends with the host's own signal). Say so if the report quotes the wrapper.
  - Step 11 still collects the sitting. Its COPY-BACK EXACT may refuse while a process left running still writes the sitting's files (the
    host wrapper's output when the host ends; since K9 the sampler's telemetry is final before the manifest). Then the collection and any
    data commit wait for a dated note.
  - Step 9 (A1) refuses any further E198 sitting before a dated note.
  - A host that ends after its TERM **within 25 s of its start** reads as exit 124: the registered stop "killed by timeout (tell the lab
    admin)". It is reported the same way.
  - A host that ends later, **inside `end_device()`'s waits** (25 to 100 s after its start; the real-path test's HGE), still reads as A
    DEVICE PROCESS NOT ENDED: the runner's stop, the session's line, the skipped closing read, step 10's DEVICE-NOT-ENDED and step 9's
    refusal all stand. Report it by the runner's own `device_ended` event too (the runner call's `events.jsonl`, exit 124): "outlived its
    TERM, then ended by itself N s after its start" (verify-a1e198's finding 3).

## 5. What the lane reports

CARD-LANE-BRIEF.md section 5, plus: the runner copy's sha256 from the session's `hashes.txt`; any exit 124; any device process not
ended, with its times and what was reported to whom; for such a process, the runner's K9 line (the sampler stopped) or its "sampler did
not stop" line, any `device_ended` event and its second, card 1's lock (free once the runner exited), et-who's line for the host left
running and `ps`'s lines (read-only) for it, its `timeout` and its wrapper; and, if the wrapper is quoted, that `x04host_e198.sh`'s "-k 1"
header is v1's and stale.

## 6. The dated fix (Q196, `fix-a1e198`, Mon 16 Nov 2026, before the land)

Sections 1, 3, 4 and 5 carry verify-a1e198's findings 1, 2, 3 and 8 (E198.md.dated-amendment-A1.md 9 lists all eight): K9 (the sampler
stopped after a device process not ended), what the clean-up's TERMs reach, the 25 s bound for an exit 124, the report of a host that
ends inside the waits, the free lock beside the held nodes, and the stale wrapper header. Step 2 (A1) also refuses now any file under
`tools/claims-v3/e198/` added, changed or removed after A1's commit (16, "after-A1"): if it does, stop as for any step-2 refusal.

SPDX-License-Identifier: Apache-2.0
