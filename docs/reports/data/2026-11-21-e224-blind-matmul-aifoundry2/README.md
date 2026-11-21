# E224 session 1795248610-a2c0-E224, 2026-11-21: arm B of MM1-v3.3's blind day on aifoundry2 card 0 under its governor at 799 MHz (route c) (rgm136; family G on rgm211's host), the session's records

*Written by the card lane's collection (`tools/claims-v3/e224/collect_e224b.py`, runbook step 11) from the session's own records; the card lane adds
its dated departures and notes below before the data commit. **E224** is registered in `tools/claims-v3/e224/E224.md` (its freeze line: the
registration's commit, which froze every forecast E224 scores) and kitted in `tools/claims-v3/e224/KIT.md`. This directory holds the measured
records and the lab's desk checks of them; **no score is here**: E208's registered reducer and the frozen scorer `score_e224.py` run after this
data commit (runbook step 13) and a later lane commits their outputs beside it.*

**Labels.** Everything under `session/` is **measured** (the card's own records, written by `src/run_e224b.py` - E208's registered runner,
unchanged and imported, with E224's registered stop lines and family G - on its real path), but for one line of fwgate's read record in
`session/first/` whose box home is written as `~` (THE MASK, registered in E224's kit before any datum; the collection printed both sha256);
the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (E224.md, E208's kit at its sha256s);
`checks-e224b.*` is **the lab's desk check of the records** (E208's data lane's checker, unchanged); `facts-e224b.json` is the collection's
reading of the records; `neverrun-e224b-card.txt` and `ranbefore-e224b.json` are the never-run search repeated right before the first card command
(**desk**, REPORTED). The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## The session (from its records)

| | |
|---|---|
| card | aifoundry2 card 0 under its own governor, as found (read, never set) |
| session | `1795248610-a2c0-E224`, T0 2026-11-21 00:10:10 PST; runner rc 0 |
| the window | G 2026-11-21 00:00:34 PST; last start 2026-11-21 01:31:00 PST; last end 2026-11-21 03:31:00 PST (G + 1:30 and G + 3:30, rounded up) |
| the reboot gate (step 7) | stamp 2026-11-21 00:10:10 PST, `read` (the record in `session/first/`) |
| the end | 2026-11-21 00:50:01 PST; **39.78 card-minutes** from the session's config read (the runner's count) |
| runs | 105 of 103 ran (s01 E208's three smoke arms; t01 at 1 and 86; s03 at 87; the G block 88-103, last); not run: none |
| stop | None |
| the lab's checks | FAIL: C0_src, C2_runs: C0_src FAIL, C1_clean_end PASS, C2_runs FAIL, C3_identity PASS, C4_clock PASS, C5_stops PASS, C6_timeouts PASS, C7_no_leftover PASS, C8_sampler PASS |
| never-run (step 6n) | NOT RUN |

## Departures and notes, dated (the card lane writes these before the data commit)

1. **The go**: the owner's standing words of Sun 15 Nov 2026, Mon 16 Nov 2026 and Tue 17 Nov 2026 and his words relayed since (E224.md
   section 6), with E224's registered items as their defaults; G = the booking on its day; **the post waived** (his words of 10:22:36 PST Sun 15
   Nov 2026); **the host's package counter not read**; the desk aifoundry2 with Python 3.12.3 (`/usr/bin/python3`).
2. **Dated departures, recorded before the results** (Sat 21 Nov 2026, PST; the card lane `card-e224b`, round Q237). The go of item 1, run in
   the round's orchestrating session, which runs under the yvb2 Claude account since 08:56 PST Thu 19 Nov 2026 (before that the yvb3
   account; the session moved that morning on the owner's ask, in his words "Use Cloud Session Mover to restore it on this Claude account
   and continue." and "Do this in ultracode for maximum parallelism"). E224's registered items are the defaults; nothing registered was
   changed. **THE DAY:** the clock had passed 20:29:00 PST on Fri 20 Nov 2026 before E224 was ready, so the card day is Sat 21 Nov 2026 from
   00:00:30 PST (E224.md 6; the owner's relayed words "use all the cards without restriction, all night if needed"). **G = this lane's
   booking of aifoundry2 at 00:00:34 PST** (`book.sh take aifoundry2 card-e224b` printed BOOKED, at the first read after 00:00:30 that found
   the day open and the queue over): last start 01:31:00 and last end 03:31:00 PST (step 1 at 00:04:26). Step 3, the post, SKIPPED by the
   owner's waiver (item 1). The host's package counter was not read. Every desk step ran on aifoundry2 under `/usr/bin/python3` 3.12.3, each
   numerical one single-threaded inside the round's CPU slots; the box's own load history read the host's 1-minute load at most 2.28
   (00:04:59 PST) from G to the collection and at most 1.05 inside the session, under the round's limit of 6, and the host CPU at most
   25.3%. The go lines' pins read W 20 of 20 and LAB 20 of 20 OK and the lists 31 of 31, 9 of 9, 120 of 120 and 5 of 5 OK before row R
   (23:18:35 and again 23:47:17 PST Fri, at the seal's new HEAD).
3. **The sealed forecast, a freeze line before the booking** (the seal hold; it did not move G). The model session's sealed forecast of all
   127 of E224's points on both arms (sha256 `2919aa682fde5d2c4831f27d5069f3d036fd01eb05a4d968d5451035c4b0da31`, posted on the round's
   coordination thread at 23:00:49 PST Fri 20 Nov 2026) is registered in `tools/claims-v3/sealed-e224/e224-freeze-lines.md` (`71d217b8`,
   pushed by 23:27:41 PST Fri), before this lane's booking and before any E224 card command. The orchestrator held both arms' boxes for it
   from 23:11:49 PST and released them by 23:33:18 PST, after the registration and its record; THE DAY held the booking to 00:00:30 PST
   anyway. Step 0's S1 and step 2's check 10 read "SEALED-E224: sealed 1 of 1 registered". No number of it is here, and the lab does not
   score it.
4. **The release records, read through the kit's copy** (row R, `rb/releases_e224b.py`). At 00:00:34 PST: "RELEASES-E224B: MADE 6 records (17
   lines naming aifoundry2 card 0: 6 read as they are, 4 session ends added in the rule's form (3 of them at the post's own time), 7
   comments: no session end)"; its guard read "REL-GUARD-E224B: AS READ (6 records; the round's records hold what the copies were made from)"
   at steps 7 and 9 (00:10:10). The rest rule at steps 7 and 9: "REST OPEN since 2026-11-20 17:11:22 PST (the last end 2026-11-20 16:31:22
   PST, the release record: e221-15.11.1 #15.11.1)": the last session on this card was the model session's E221 a2c0-S3 (its own records end
   16:29:42 PST; its release post at 16:31:22 counts as its end, the later of the two); E220 arm B's session ended 15:37:07 PST before it.
5. **THE ORDER: arm A first, and card-e222 launched before the flag.** The three card lanes of the night booked within 3 s: this lane
   aifoundry2 at 00:00:34, card-e222 aifoundry3 at 00:00:36 and card-e224a aifoundry1 at 00:00:37 PST. This lane then waited (a wait,
   never a gate: the go lines say arm A's rows 0-2 go first when both lanes are ready at once) until card-e224a had entered its desk span
   (its stamp 00:00:47, seen 00:00:49) and left it (`wait_other_desk_e224.sh` read it gone at 00:03:53); this lane's desk span followed
   (note 6). Row O's first half, `order_wait_e224b.sh` (the go lines' addition), read at 00:06:43 "card-e224a holds aifoundry1 (booked
   2026-11-21 00:00:37 PST)" and "card-e222 launched (its marker written 00:06:35, after its booking 2026-11-21 00:00:36 PST)" and printed
   the launch-marker list rows O and Q used; the kit's row O read at 00:06:50 "THE ORDER: aifoundry1: card-e224a launched (its marker
   written 2026-11-21 00:05:33 PST, after its booking 2026-11-21 00:00:37); aifoundry2: ours; aifoundry3: card-e222 launched (its marker
   written 2026-11-21 00:06:35 PST, after its booking 2026-11-21 00:00:36)". **THE QUIET DESK FLAG** was raised as `card-e224b 2026-11-21
   00:06:58 PST`, 85 s after arm A's launch marker (00:05:33.42) and 23 s after card-e222's (00:06:35.42), and lowered at 00:50:30 PST, right
   after the copy-back (step 11); THE P2 COUNT read 0 at 00:06:58 and again at steps 4, 7, 9 and 4'.
6. **Steps 0, H, 1 and 2, inside THE ONE-LAB RULE's desk span (00:03:57-00:04:43 PST).** Step 0 at 00:03:57: the 1-minute load 1.60; the
   step-0 anchor read "GO-ANCHORS-E224 arm B: 87 of 87 as stated (HEAD 71d217b8fea4eb09230cb137e2750ee60d870d96 = GitHub main; status 0
   lines)" (00:04:18); S1 "SEALED-E224: sealed 1 of 1 registered (tools/claims-v3/sealed-e224/e224-freeze-lines.md at HEAD); comment lines:
   none" (00:04:22). THE QUIET HOLD as `card-e224b` at 00:04:26, beside card-e222's and card-e224a's lines (the lab clone's status 0
   lines). Step 2 at 00:04:37 (its own sha256 `da315ba6...` equal to the land's anchor): "STEP2 PASS (HEAD
   71d217b8fea4eb09230cb137e2750ee60d870d96)", checks 1o-12 as stated (the desk span held; HEAD = GitHub's main; the registration
   `7de833605903` and the kit `0fb6eb953888` in HEAD, the history additions only (123); the lists 31 of 31, 120 of 120, 58 of 58, 64 of 64,
   170 of 170, 114 of 114, 57 of 57 and 48 of 48 at their pins; the frozen scorer's two self-tests, the stand-ins byte for byte and the
   real bytes equal but the lab's HEAD and its pick (REPORTED `71d217b8fea4` NO PICK); the timeout table CHECK PASS; `make_box_e224b.py
   check` CHECK PASS (85 files); dmcmd_audit GO, 12 send sites, 0 disallowed; the freeze line, E224's registration `7de833605903`,
   committed 21:52:25 PST Fri, with the seal of note 3 registered; no E224 arm B datum in any ref; HEAD unchanged).
7. **Steps 5, 4, 6 and 8** (sending nothing to the card): the sync at 00:07:07, "SYNCED: 85 files at the harness's sha256 (85 copied, 0
   already there, 0 pruned []) from HEAD 71d217b8fea4eb09230cb137e2750ee60d870d96"; the look at 00:07:07, "FREE; the reboot gate:
   NEEDS-READ"; the builds 00:07:12-00:07:24, "MMS-BUILT and E224-BUILT: the kernel at E136's pin, rgm211's host gated for family G" (the
   build records in this directory); the dry pass 00:07:28-00:08:30, "DRY PASS a2c0 E224 (runner rc 0; 0 runs not clean)": 105 of 105
   runs in the registered order, 108 of 108 processes GATE OK (9 'rgm136 gemmLnc', 99 'rgm136 gemmL'), family G's 9 runs the last 9 host
   calls, on rgm211's host, every host call under its plain timeout 10.
8. **The never-run search, repeated** (step 6n, 00:08:34-00:09:13 PST; desk, REPORTED, never a gate), read by E224.md 4 (dated note 1's
   reading, registered: a point counts as run on this card only by a session record on it) with the kit's wider scan (KIT.md section 2,
   reading 1, accepted by the orchestrator): "NEVER-RUN-E224 arm B: 63 of 63 registered points never ran on aifoundry2 card 0 by session
   records (E224.md 4, dated note 1's reading), in the registered scan and the kit's wider scan (E220's and E222's folders read) both (scans
   8702939fb72c / 566af3238e50, 107973 / 111577 files, lab 71d217b8fea4); ran before, labelled: none; the literal reading (REPORTED, not a
   label): 48 / 0 of 63 never ran". `ranbefore-e224b.json` names no point: every point keeps its registered label. **The wider scan's
   literal reading moved from 48 of 63 (the readiness's desk run at 23:0x PST Fri) to 0 of 63** (REPORTED, post hoc): every one of its
   literal hits is one file, card-e222's own step-6n scan record, written at 00:05:35 PST in that lane's folder (a folder naming no card),
   which tabulates every shape name of the lab, E224's registered points among them; it is a desk record, not a session record, so by the
   registered reading it labels nothing. The registered scan's literal reading is unchanged (48 of 63).
9. **Step 7, the reboot gate: the day's first card command, stamped 00:10:10 PST, mode `read`.** Before it, step 7 read the window, the
   flag (ours), both builds and the dry pass of today, the release-records guard (note 4), the P2 count 0, step 6n's line, the rest
   (note 4), the card free by et-who (read 1: `et-who --check` rc 0, no holder line) and THE CPU RULE's gate (the host's 1-minute load
   0.81, under 6). fwgate's look read NEEDS-READ (aifoundry2 booted 2026-11-17 16:46:04 PST; the newest firmware read of record E72's of
   2026-10-27 14:59:39 PDT); then fwgate's ONE firmware-revisions READ, **the boot's third firmware read on this card** (a dated departure
   the go lines and the orchestrator accepted: E216's read of 16:55:55 PST Thu 19 Nov 2026 and E220 arm B's of 14:57:42 PST Fri 20 Nov 2026
   were the first two, and both ended EQUAL; fwgate refuses a later read only after one that did not; the owner's rulings of Sun 15 Nov
   2026, 15:07:01 PST "Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware
   are always allowed." and 15:09:49 PST "I don't want to modify firmware, but commands which read firmware should be fine."): "EQUAL:
   aifoundry2 card 0 at 2026-11-21 00:10:10 PST matches E72's read of 2026-10-27 14:59:39 PDT in all seven fields"; its guard "identity:
   aifoundry2 card 0 booted 2026-11-17 16:46:04 PST, before the firmware read of 2026-11-21 00:10:10 PST
   (fwgate-aifoundry2-c0-20261121-001010.json): ok". The record is `session/first/fwgate-aifoundry2-c0-20261121-001010.json` (THE MASK,
   note 13). Step 9 launched at once (00:10:10; the guard and the rest read again, the P2 count 0, the load 0.81), and the session's own
   config read followed at 00:10:14 PST, so the card time from the day's first card command is the runner's 39.78 card-minutes plus about
   4 s.
10. **The session: no stop, no dropped run, no cut point.** 105 of 105 runs ran (102 arm runs, s03 among them, and the three anchor runs
   t01, at 1, 60 and 96), the smoke's three processes first (gemmL1x1x4 fp16 ones, fp32 zeros, int8 random: rc 0, their checks exact); the
   stop-path test passed at E224's lines (the board tripped in 0.25 s, the die in 0.1 s). Of the 105 run processes 101 ended rc 0 and 4 rc 1
   (note 12); their checks of C read 30 exact, 71 approx and 4 wrong. The G block ran last: s03 at 097 (gemmLnc6x5x10 fp32 random, rc 0, its
   check approx, 16 launches), then runs 098-105 (d30, g03, g01, d29, g02, then g02, g01, g03 again in reverse), each rc 0 with its check
   exact (d30, int8) or approx; no KERNEL STOP and no IDENTITY GATE STOP. Stop none; runner rc 0; the session ended at 00:50:01 PST after
   39.78 card-minutes (planned 41.5; the rule 65, the cap 75). The config read at 00:10:14: TDP 65 W, threshold 65 C, power state 3
   (low_power), minion 600 MHz, 519 mV, the card's identity /dev/et0_mgmt with physical device ID 0, read and never set, and the same at
   the end (00:50:00).
11. **The clock and the peaks** (measured: `checks-e224b.txt` C4 and C5, and a desk read of `session/telemetry.jsonl.gz` by each run's own
   work window, post hoc). The clock is in every sample (23,832 of 23,832: 600 MHz 17,173, 700 MHz 217, 800 MHz 6,442; inside the device
   processes' windows 929 / 211 / 6,030; the counted launches' clock 586.5-799.4 MHz), governed, read and never set. The board peaked at
   65.64 W at 00:48:26 PST in run 101-d29 (a gemmLnc point of the G block, named among the governor's route-m risks); no sample was over the
   70 W line (C5: no trip, 0 samples over the line). The board's peak inside each family's work windows: D 65.64 W (101-d29), L 62.98 W
   (081-e04), the G block's smoke s03 61.29 W (097-s03), the anchor 58.11 W (060-t01), P 57.6 W (062-p2r). The shires' mean die peaked at
   52 C (00:48:27); the hottest-sensor latch read 56 C at its first sample and never rose. The opening rest: board 20.86 W, die 41 C.
12. **Four checks of C read 'wrong': family P's two fp16 pattern points at gemmL1x1x25** (measured; R0's input, REPORTED here, scored by the
   frozen scorer at step 13). p3a (`gemmL1x1x25` fp16, E212's `fld16_mant` tile) at runs 040 and 073: "words 16384, exact 0, within 0,
   result wrong"; p3b (`gemmL1x1x25` fp16, E217's `h_th_in` tile) at runs 014 and 085: "words 16384, exact 0, within 12160, result
   wrong". Each process ran all its launches (launches_ok true, 16 launches at 014), was not stopped, and exited rc 1, the host's exit
   for a wrong check; the session went on, as the registered runner does for a gemmL process (THE KERNEL STOP is family G's). The two
   points' random and zeros twins at the same shape read approx and exact (p3r at 035 and 075, p3z at 041 and 072). A desk read of
   committed records, post hoc: arm A's data on aifoundry1 card 1 (committed earlier tonight) reads the same two points wrong with the same
   counts (p3a within 0, p3b within 12,160 of 16,384, both passes), and these two tiles read approx at gemmL1x1x1 in E212's and E217's
   sessions; the same counts on two cards say the host's check of C at this depth (K 25,600 in fp16) with these two operand patterns, not a
   card fault, but this lane did not test that. Under E224.md 7, R0 (every check of C exact or approx) reads FAIL for arm B, and a FAIL
   labels every other verdict of the arm and the pooled ones; nothing here drops or re-chooses a point.
13. **THE MASK: one line of one file is not the box's bytes** (registered in E224's kit before any E224 datum, E209's kit note 1's form).
   In `session/first/fwgate-aifoundry2-c0-20261121-001010.json`, line 34 (fwgate's attempt-ledger path) is written with the box's home as
   "~". Every other line of that file and every other file under `session/` is the box's bytes. The record's sha256:
   - **the box's bytes `612a287887229deb7de95b4c77c21c6e207562dc2e50c9f046046ffd2a1f4381`**: its line in `session/MANIFEST.sha256`, which
     is as the box wrote it;
   - **the committed bytes `0bd00b72334a72f7cd25064d2debe205644abdd928dd38d8c198d7e405d91ef6`**.

   So `sha256sum -c MANIFEST.sha256` in `session/` fails on that one line by design, and step 13's manifest read takes it back. The
   collection read "COPY-BACK EXACT: 348 manifest lines OK, 351 files (1795248610-a2c0-E224)", and its scrub of 353 files (the copy and the
   checks) found no login name, no home path and no path of the box's own folders; nothing else was masked or changed.
14. **The lab's checks C0 and C2 read FAIL** (REPORTED; desk readings, post hoc). E208's data checker, unchanged:
   - **C0_src**, as in E216 and E220: the checker takes the schedule's name and sha256 from the first line of `session/session.log`, where
     E224's runner writes its own lines ("E224's lines: board above 70 W on 3 samples, die or a risen latch at or above 70 C; line 67 W;
     family G on rgm211's host ..."), and E208's 'session start' line second, so it found no match (`log_prefix` None). Every other field
     of C0 reads as registered: the schedule `a2c0-E224.json`; its sha256
     `796bd837924fbf55f10903192eb029bc953d4741696f2f0d94f02edd3ef5c99a`, equal to the box's src list's line; the harness "HARNESS OK: 77
     files at src/SRC-SHA256SUMS's sha256"; the log's second line names "schedule a2c0-E224.json sha256 796bd837924fbf55".
   - **C2_runs**: its problems are the four wrong checks of note 12 (014-p3b, 040-p3a, 073-p3a, 085-p3b: rc 1, launches_ok true,
     check_ok false, stopped_by_file false). Every other field of C2 reads as registered: 105 run records of 105 scheduled, forms burst, 105
     processes, 1,652 launches recorded.
   The checks are REPORTED, never a gate; C1 and C3-C8 PASS.
15. **Two words of the table above are the form's, ported** (REPORTED, a kit finding; nothing measured changes). The row 'runs' reads "105 of
   103 ran (s01 E208's three smoke arms; t01 at 1 and 86; s03 at 87; the G block 88-103, last)": the counts in brackets are E220's; E224 arm
   B's registered schedule is 105 runs, s01's three smoke processes first, t01 at 1, 60 and 96, s03 at 097 and the G block 098-105, last,
   and all 105 ran. The row 'never-run (step 6n)' reads NOT RUN, and `neverrun-e224b-card.txt` (named in the Files table) is not in this
   directory, as in E220: the collection copies a file of that name from step 6n's folder, and the kit's step 6n writes its report under
   other names; step 6n ran and printed the line of note 8, 57 s before step 7, which read it.
16. **SHA256SUMS** (every file here but itself): the collection wrote it before these notes; once they were added it was made again in the
   same form, so only its `README.md` line differs from the collection's list.
17. **Steps 12 and 13.** This commit is step 12, under THE QUIET HOLD (`card-e224b`) inside THE ONE-LAB RULE's collect span (from 00:50:29
   PST). After its push the hold line is removed and the booking released; step 13 (E208's registered reducer and the frozen scorer
   `score_e224.py --b`) runs on the committed session, and a later lane commits its outputs beside this directory.

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's folder as the runner wrote it, byte for byte but for THE MASK's one line (its `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`); `first/` holds step 7's reboot-gate record; `gates.jsonl` every process's identity gate | measured |
| `checks-e224b.json`, `checks-e224b.txt` | E208's data lane's checks C0-C8 (unchanged checker) | desk check of the records |
| `build-record-aifoundry2.json`, `build-record-e224b-aifoundry2.json` | the box root's two build records of the day (E208's build and E224's rgm211 host), byte for byte | record |
| `facts-e224b.json` | the collection's facts | desk reading |
| `neverrun-e224b-card.txt`, `ranbefore-e224b.json` | step 6n's search and its labels (the scorer's `--labels` form) | desk, REPORTED |
| `SHA256SUMS` | every file here but itself | - |
