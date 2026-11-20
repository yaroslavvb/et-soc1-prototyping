# E220 session 1795215462-a2c0-E220, 2026-11-20: arm B of MM1-v3.2's card-transfer blind day on aifoundry2 card 0 under its governor at 799 MHz (route c) (rgm136; family G on rgm211's host), the session's records

*Written by the card lane's collection (`tools/claims-v3/e220/collect_e220b.py`, runbook step 11) from the session's own records; the card lane adds
its dated departures and notes below before the data commit. **E220** is registered in `tools/claims-v3/e220/E220.md` (its freeze line: the
registration's commit, which froze every forecast E220 scores) and kitted in `tools/claims-v3/e220/KIT.md`. This directory holds the measured
records and the lab's desk checks of them; **no score is here**: E208's registered reducer and the frozen scorer `score_e220.py` run after this
data commit (runbook step 13) and a later lane commits their outputs beside it.*

**Labels.** Everything under `session/` is **measured** (the card's own records, written by `src/run_e220b.py` - E208's registered runner,
unchanged and imported, with E220's registered stop lines and family G - on its real path), but for one line of fwgate's read record in
`session/first/` whose box home is written as `~` (THE MASK, registered in E220's kit before any datum; the collection printed both sha256);
the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (E220.md, E208's kit at its sha256s);
`checks-e220b.*` is **the lab's desk check of the records** (E208's data lane's checker, unchanged); `facts-e220b.json` is the collection's
reading of the records; `neverrun-e220b-card.txt` and `ranbefore-e220b.json` are the never-run search repeated right before the first card command
(**desk**, REPORTED). The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## The session (from its records)

| | |
|---|---|
| card | aifoundry2 card 0 under its own governor, as found (read, never set) |
| session | `1795215462-a2c0-E220`, T0 2026-11-20 14:57:42 PST; runner rc 0 |
| the window | G 2026-11-20 14:50:53 PST; last start 2026-11-20 16:21:00 PST; last end 2026-11-20 18:21:00 PST (G + 1:30 and G + 3:30, rounded up) |
| the reboot gate (step 7) | stamp 2026-11-20 14:57:42 PST, `read` (the record in `session/first/`) |
| the end | 2026-11-20 15:37:07 PST; **39.36 card-minutes** from the session's config read (the runner's count) |
| runs | 103 of 103 ran (s01 E208's three smoke arms; t01 at 1 and 86; s03 at 87; the G block 88-103, last); not run: none |
| stop | None |
| the lab's checks | FAIL: C0_src, C2_runs: C0_src FAIL, C1_clean_end PASS, C2_runs FAIL, C3_identity PASS, C4_clock PASS, C5_stops PASS, C6_timeouts PASS, C7_no_leftover PASS, C8_sampler PASS |
| never-run (step 6n) | NOT RUN |

## Departures and notes, dated (the card lane writes these before the data commit)

1. **The go**: the owner's standing words of Sun 15 Nov 2026, Mon 16 Nov 2026 and Tue 17 Nov 2026 and his words relayed since (E220.md
   section 6), with E220's registered items as their defaults; G = the booking on its day; **the post waived** (his words of 10:22:36 PST Sun 15
   Nov 2026); **the host's package counter not read**; the desk aifoundry2 with Python 3.12.3 (`/usr/bin/python3`).
2. **The session, G and the account** (Fri 20 Nov 2026, PST). The go of item 1, run by the card lane `card-e220b` (round Q233) in the
   round's orchestrating session, which runs under the yvb2 Claude account since 08:56 PST Thu 19 Nov 2026 (before that the yvb3 account;
   the session moved that morning on the owner's ask, in his words "Use Cloud Session Mover to restore it on this Claude account and
   continue." and "Do this in ultracode for maximum parallelism"). **G = its booking of aifoundry2 at 14:50:53 PST** (`book.sh take
   aifoundry2 card-e220b` printed BOOKED): last start 16:21:00 and last end 18:21:00 PST (step 1 at 14:54:16). The booking waited at row B
   behind the orchestrator's hold for the model session's sealed forecast (`orch-hold-e220-seal`, booked 14:38:21 PST and released after
   the seal's registration, note 3) and booked at the first read after it (QUEUE OVER at 14:50:49). Step 3, the post, SKIPPED by the
   owner's waiver (item 1). Every desk step ran on aifoundry2 under `/usr/bin/python3` 3.12.3, each numerical one single-threaded inside
   the round's CPU slots; the box's own load history read the host's 1-minute load at most 2.32 (14:53:09 PST) from G to the collection,
   under the round's limit of 6, and the host CPU at most 26.0%. The go lines' pins read W 19 of 19 and LAB 18 of 18 OK and the lists 29 of
   29, 5 of 5 and 120 of 120 OK before row R (14:42:15).
3. **The sealed forecast, a freeze line before the booking** (the seal hold, a dated departure of the booking's time only). The model
   session's sealed forecast of all 158 of E220's points on both arms (sha256
   `f2cf18f0ea1d3e590a7cecdd663ba3f2314a0bcb11e5e23e7aeb3b8e91dd5b82`, posted on the round's coordination thread at 13:26:12 PST Fri 20 Nov
   2026) is registered in `tools/claims-v3/sealed-e220/e220-freeze-lines.md` (`d5df9568`, committed 14:44:58 PST), before this lane's
   booking and before any E220 card command; the orchestrator held both arms' boxes for it from 14:38:21 PST and wrote the round's record of
   it at 14:50:44 PST. Step 0's S1 and step 2's check 10 read "SEALED-E220: sealed 1 of 1 registered". No number of it is here, and the lab
   does not score it.
4. **The release records, read through the kit's copy** (row R, `rb/releases_e220b.py`, with fix-e220's reading of E221's release lines).
   At 14:42:32 PST: "RELEASES-E220B: MADE 6 records (15 lines naming aifoundry2 card 0: 6 read as they are, 3 session ends added in the
   rule's form (2 of them at the post's own time), 6 comments: no session end)"; its guard read "REL-GUARD-E220B: AS READ (6 records; the
   round's records hold what the copies were made from)" at steps 7 and 9 (14:57:41-14:57:42). The rest rule read at row B (14:50:53) and
   at steps 7 and 9: "REST OPEN since 2026-11-20 12:20:40 PST (the last end 2026-11-20 11:40:40 PST, the release record: e221-15.10.1
   #15.10.1)": the last session on this card was the model session's E221 a2c0-S2 (its own records end 11:39:08 PST; its release post at
   11:40:40 counts as its end, the later of the two).
5. **THE ORDER: arm A first.** Both card lanes booked at 14:50:53 PST, when the orchestrator released both seal holds. This lane then
   waited (a wait, never a gate; a dated departure: the go lines say arm A's rows 0-2 go first when both lanes are ready at once, and this
   lane's bounded wait made it so) until card-e220a had entered its own desk span (14:51:23) and left it (`wait_other_desk_e220.sh` read it
   gone at 14:53:46); this lane's desk span followed (note 6). Row O's first wait read "card-e220a holds aifoundry1 (booked 2026-11-20
   14:50:53 PST)" at 14:54:37; the kit's row O read arm A's launch marker, written 14:55:20 PST (arm A's T0 14:55:15), after its booking:
   "THE ORDER: every other card lane of ours that holds a booking has passed its launch step" (14:55:29). **THE QUIET DESK FLAG** was
   raised as `card-e220b 2026-11-20 14:55:42 PST`, 22 s after arm A's launch marker, and lowered at 15:37:34 PST, right after the
   copy-back (step 11); THE P2 COUNT read 0 at 14:55:42 and again at steps 7 and 9. No other card lane of ours held a booking meanwhile.
6. **Steps 0, H, 1 and 2, inside THE ONE-LAB RULE's desk span (14:53:53-14:54:32 PST).** Step 0 at 14:53:53: the 1-minute load 1.84; the
   step-0 anchor read "GO-ANCHORS-E220 arm B: 79 of 79 as stated (HEAD d5df95683320de9fefde7dc2ca149fa6dd992630 = GitHub main; status 0
   lines)" (14:54:02); S1 "sealed 1 of 1" (14:54:06). THE QUIET HOLD as `card-e220b` at 14:54:12, beside card-e220a's line (the lab
   clone's status 0 lines). Step 2 at 14:54:27 (its own sha256 `f4aaf31e...` equal to the land's anchor): "STEP2 PASS (HEAD
   d5df95683320de9fefde7dc2ca149fa6dd992630)", checks 1o-12 as stated (the desk span held; HEAD = GitHub's main; the registration and the
   kit in HEAD, the history additions only; the lists 29 of 29, 120 of 120, 58 of 58, 64 of 64, 170 of 170, 114 of 114, 57 of 57 and 48 of
   48 at their pins; the frozen scorer's two self-tests byte for byte; the timeout table CHECK PASS; `make_box_e220b.py check` CHECK PASS
   (77 files); dmcmd_audit GO, 12 send sites, 0 disallowed; the freeze line, E220's registration `6901854c4da4`, committed 12:31:40 PST,
   with the seal of note 3 registered; no E220 arm B datum in any ref; HEAD unchanged).
7. **Steps 5, 4, 6 and 8** (sending nothing to the card): the sync at 14:55:47, "SYNCED: 77 files at the harness's sha256 (77 copied, 0
   already there, 0 pruned []) from HEAD d5df95683320de9fefde7dc2ca149fa6dd992630"; the look at 14:55:51, "FREE; the reboot gate:
   NEEDS-READ"; the builds 14:55:55-14:56:11, "MMS-BUILT and E220-BUILT: the kernel at E136's pin, rgm211's host gated for family G" (the
   build records in this directory); the dry pass 14:56:14-14:57:15, "DRY PASS a2c0 E220 (runner rc 0; 0 runs not clean)": 103 of 103 runs
   in the registered order, 106 of 106 processes GATE OK (17 'rgm136 gemmLnc', 89 'rgm136 gemmL'), family G's 17 runs the last 17 host
   calls, on rgm211's host, every host call under its sized plain timeout (13 s for xf04's, 10 s for every other).
8. **The never-run search, repeated** (step 6n, 14:57:23-14:57:36 PST; desk, REPORTED, never a gate), read by E220's dated note 1 (a
   registered note: `tools/claims-v3/e220-notes/E220.md.dated-note-1.md`, the orchestrator's ruling before any E220 datum: a point counts
   as run on this card only by a session record on it; the literal folder reading is REPORTED beside, never a label): "NEVER-RUN-E220 arm B:
   74 of 74 registered points never ran on aifoundry2 card 0 by dated note 1's reading (a session record on the card) (scan 4f4f7fea860c,
   107913 files, lab d5df95683320); ran before, labelled: none; the literal reading (REPORTED, not a label): 32 of 74 never ran, 42 read
   ran before, 41 of them with desk files only". `ranbefore-e220b.json` names no point: every point keeps its registered label. **The
   table's row 'never-run (step 6n)' reads NOT RUN, and `neverrun-e220b-card.txt` (named in the Files table) is not in this directory**
   (REPORTED, a kit finding): the collection copies a file of that name from step 6n's folder, and the kit's step 6n writes its report
   under other names; step 6n ran, and printed the line quoted here, 6 s before step 7, which read it.
9. **Step 7, the reboot gate: the day's first card command, stamped 14:57:42 PST, mode `read`.** Before it, step 7 read the window, the
   flag (ours), both builds and the dry pass of today, the release-records guard (note 4), the P2 count 0, step 6n's line, the rest
   (note 4), the card free by et-who (read 1: `et-who --check` rc 0, no holder line) and THE CPU RULE's gate (the host's 1-minute load
   0.44, under 6). fwgate's look read NEEDS-READ (aifoundry2 booted 2026-11-17 16:46:04 PST; the newest firmware read of record E72's of
   2026-10-27 14:59:39 PDT); then fwgate's ONE firmware-revisions READ, **the boot's second firmware read on this card** (a dated departure
   the go lines accepted: E216's read of 16:55:55 PST Thu 19 Nov 2026 was the first, and it ended EQUAL; fwgate refuses a later read only
   after one that did not; the owner's rulings of Sun 15 Nov 2026, 15:07:01 PST "Firmware revisions query was a false positive. It should
   have never been forbidden. Reading operations and firmware are always allowed." and 15:09:49 PST "I don't want to modify firmware, but
   commands which read firmware should be fine."): "EQUAL: aifoundry2 card 0 at 2026-11-20 14:57:42 PST matches E72's read of 2026-10-27
   14:59:39 PDT in all seven fields"; its guard "identity: aifoundry2 card 0 booted 2026-11-17 16:46:04 PST, before the firmware read of
   2026-11-20 14:57:42 PST (fwgate-aifoundry2-c0-20261120-145742.json): ok". The record is
   `session/first/fwgate-aifoundry2-c0-20261120-145742.json` (THE MASK, note 12). Step 9 launched at once (14:57:42; the guard and the
   rest read again, the P2 count 0, the load 0.44), and the session's own config read followed at 14:57:46 PST, so the card time from the
   day's first card command is the runner's 39.36 card-minutes plus about 4 s.
10. **The session: no stop, no dropped run, no cut point.** 103 of 103 runs ran (100 arm runs, s03 among them, and the three anchor runs
   t01, at 1, 67 and 86), the smoke's three processes first, every one of the 106 processes rc 0 (`checks-e220b.txt` C3, C6); the run
   processes' checks of C 98 approx and 5 exact, every one ok; the G block last (s03 at 087; runs 088-096 every gemmLnc point once by
   its planning peak, ascending: family X's two gemmLnc points, xg08 and xg04, and the seven G2 points; runs 097-103 the G2 points again in reverse; each
   rc 0, its check of C approx); stop none; runner rc 0; the session ended at 15:37:07 PST after 39.36
   card-minutes (planned 40.73; the rule 60, the cap 70). The config read at 14:57:46: TDP 65 W, threshold 65 C, power state 3
   (low_power), minion 600 MHz, 519 mV, read and never set, and the same at the end (C3). The stop-path test passed at E220's lines (the
   board tripped in 0.25 s, the die in 0.1 s), and the smoke's three processes (gemmL1x1x4 fp16 ones, fp32 zeros, int8 random) ended rc 0
   with their checks exact.
11. **The clock and the peaks** (measured: `checks-e220b.txt` C4 and C5, and a desk read of `session/telemetry.jsonl.gz` by each run's own
   work window, post hoc). The clock is in every sample (23,581 of 23,581: 600 MHz 17,085, 700 MHz 209, 800 MHz 6,287; inside the device
   processes' windows 1,069 / 203 / 5,944; the counted launches' clock 598.9-799.8 MHz), governed, read and never set. The board peaked at
   63.3 W at 15:19:19 PST in run 055-l03 (family L3; its planning peak 66.31 W, the arm's highest); no sample was over the 70 W line (C5: no
   trip, 0 samples over the line). The board's peak inside each family's work windows: L3 63.3 W (055-l03), the G block's smoke s03
   61.05 W (087-s03), G2 60.74 W (run 095), X 60.04 W (096-xg04), the anchor 57.71 W (067-t01), G2t 49.66 W (run 027), Y2 30.13 W
   (050-p02a). The shires' mean die peaked at 51 C (15:36:17); the hottest-sensor latch read 56 C at its first sample and never rose. The
   opening rest: board 20.84 W, die 41 C.
12. **THE MASK: one line of one file is not the box's bytes** (registered in E220's kit before any E220 datum, E209's kit note 1's form).
   In `session/first/fwgate-aifoundry2-c0-20261120-145742.json`, line 34 (fwgate's attempt-ledger path) is written with the box's home as
   "~". Every other line of that file and every other file under `session/` is the box's bytes. The record's sha256:
   - **the box's bytes `ba1f241b952d5d0c2d5e81a2bb9b6c60cab15fe83d0b65317e58604e6a0bbc62`**: its line in `session/MANIFEST.sha256`, which
     is as the box wrote it;
   - **the committed bytes `b5e813bdfdb07337d9c1a901b43ca91883bd801ad88f1d986be062ff1deda6e0`**.

   So `sha256sum -c MANIFEST.sha256` in `session/` fails on that one line by design, and step 13's manifest read takes it back. The
   collection read "COPY-BACK EXACT: 342 manifest lines OK, 345 files (1795215462-a2c0-E220)" and "THE SCRUB: 347 files (the copy and the
   checks), no login name, home path ...", nothing else masked or changed.
13. **The lab's checks C0 and C2 read FAIL; neither is a fault of the session** (REPORTED; desk readings, post hoc). E208's data checker,
   unchanged:
   - **C0_src**, as in E216 (its data note 13): the checker takes the schedule's name and sha256 from the first line of
     `session/session.log`, where E220's runner writes its own lines ("E220's lines: board above 70 W on 3 samples, die or a risen latch at
     or above 70 C; line 67 W; family G on rgm211's host ..."), and E208's 'session start' line second, so it found no match (`log_prefix`
     None). Every other field of C0 reads as registered: the schedule `a2c0-E220.json`; its sha256
     `b364d836501028f170c873cfc54a9d6b1ab194f92ee462f4a5a19295f912d6b6`, equal to the box's src list's line; the harness "HARNESS OK: 69
     files at src/SRC-SHA256SUMS's sha256"; the log's second line names "schedule a2c0-E220.json sha256 b364d836501028f1".
   - **C2_runs**: its one problem is run 060-xf04 (gemmL15x16x32 fp32, the arm's longest GEMM, under its sized plain `timeout 13`). Its host
     printed "stopping: device-time budget of 7.5 s used", the end of its own registered `--budget 7.5`, and E208's runner records any
     'stopping:' line as `stopped_by_file`; the session's STOP file was never written (no stop, C5). The process ran its 6 launches, all
     ok, and its check of C ok (approx), rc 0 after 9.58 s. Every other field of C2 reads as registered: 103 run records of 103 scheduled,
     forms burst, 103 processes, every one rc 0, 1,626 launches recorded.
   The checks are REPORTED, never a gate; C1 and C3-C8 PASS.
14. **SHA256SUMS** (every file here but itself): the collection wrote it before these notes; once they were added it was made again in the
   same form, so only its `README.md` line differs from the collection's list.
15. **Steps 12 and 13.** This commit is step 12, under THE QUIET HOLD (`card-e220b`, beside card-e220a's line) inside THE ONE-LAB RULE's
   collect span (from 15:37:29 PST). After its push the hold line is removed and the booking released; step 13 (E208's registered reducer
   and the frozen scorer `score_e220.py --b`) runs on the committed session, and a later lane commits its outputs beside this directory.

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's folder as the runner wrote it, byte for byte but for THE MASK's one line (its `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`); `first/` holds step 7's reboot-gate record; `gates.jsonl` every process's identity gate | measured |
| `checks-e220b.json`, `checks-e220b.txt` | E208's data lane's checks C0-C8 (unchanged checker) | desk check of the records |
| `build-record-aifoundry2.json`, `build-record-e220b-aifoundry2.json` | the box root's two build records of the day (E208's build and E220's rgm211 host), byte for byte | record |
| `facts-e220b.json` | the collection's facts | desk reading |
| `neverrun-e220b-card.txt`, `ranbefore-e220b.json` | step 6n's search and its labels (the scorer's `--labels` form) | desk, REPORTED |
| `SHA256SUMS` | every file here but itself | - |
