# E209 session 1794940244-a2c0-E209, 2026-11-17: the blind matmul day on aifoundry2 card 0 under its governor (rgm136, MM1-v2's frozen forecasts), the session's records

*Written by the card lane's collection (`tools/claims-v3/e209/collect_e209.py`, runbook step 11) from the session's own records; the card lane adds
its dated departures and notes below before the data commit. **E209** is registered in `tools/claims-v3/e209/E209.md` (its freeze line: MM1-v2's
forecasts pushed in `3ca4b717` at 01:44:48 PST Tue 17 Nov 2026) and kitted in `tools/claims-v3/e209/KIT.md`. This directory holds the measured
records and the lab's desk checks of them; **no score is here**: the registered reducer and the frozen scorer run after this data commit (runbook
step 13) and a later lane commits their outputs beside it.*

**Labels.** Everything under `session/` is **measured** (the card's own records, written by E208's registered runner, unchanged, on its real path);
the schedule, the run forms, the windows, the stop lines and the reduction's rules are **registered** (E209.md, E208's kit at its sha256s);
`checks-e209.*` is **the lab's desk check of the records** (E208's data lane's checker, unchanged); `facts-e209.json` is the collection's
reading of the records; `neverrun-e209-card.txt` and `ranbefore-e209.json` are the never-run search repeated right before the first card command
(**desk**, REPORTED). The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## The session (from its records)

| | |
|---|---|
| card | aifoundry2 card 0 under its own governor, as found (read, never set) |
| session | `1794940244-a2c0-E209`, T0 2026-11-17 10:30:44 PST; runner rc 0 |
| the window | G 2026-11-17 10:23:36 PST; last start 2026-11-17 11:54:00 PST; last end 2026-11-17 13:54:00 PST (G + 1:30 and G + 3:30, rounded up) |
| the reboot gate (step 7) | stamp 2026-11-17 10:30:44 PST, `read` (the record in `session/first/`) |
| the end | 2026-11-17 10:56:57 PST; **26.16 card-minutes** from the session's config read (the runner's count) |
| runs | 62 of 62 ran; not run: none |
| stop | None |
| the lab's checks | ALL PASS: C0_src PASS, C1_clean_end PASS, C2_runs PASS, C3_identity PASS, C4_clock PASS, C5_stops PASS, C6_timeouts PASS, C7_no_leftover PASS, C8_sampler PASS |
| never-run (step 6n) | NEVER-RUN 45 of 45 points, 29 of 29 shapes |

## Departures and notes, dated (the card lane writes these before the data commit)

1. **The go**: the owner's standing words of Sun 15 Nov 2026 and of Mon 16 Nov 2026 (E209.md section 6), with E209's
   registered items as their defaults; G = the booking on its day; **the post waived** (his words of 10:22:36 PST Sun 15 Nov 2026); **the host's
   package counter not read**; the desk aifoundry2 with Python 3.12.3 (`/usr/bin/python3`).
2. **(a) The session and G** (card-e209's note to the orchestrator, item 4 (a); Tue 17 Nov 2026, PST). The go of item 1, run by the card
   lane `card-e209` (round Q202c) in the round's session on its yvb3 Claude account. **G = its booking of aifoundry2 at 10:23:36 PST Tue 17
   Nov 2026** (`book.sh take aifoundry2 card-e209` printed BOOKED): last start 11:54:00 and last end 13:54:00 PST (step 1 at 10:24:56).
   Step 3, the post, SKIPPED by the owner's waiver (item 1).
3. **(b) Steps 4 and 5 in the other order, 10:25:44-10:28:07 PST** (item 4 (b); a departure from the go lines' order; both steps send
   nothing to the card). At 10:25:44 step 4 (`rb/s05_look_e209.sh`) refused with exit 16, "the reboot gate's look ended rc 2": the look
   runs fwgate.py from the box root, and on the new, empty box root the go lines require only step 5 (the sync) puts it there. fwgate never
   ran (its ledger unchanged since Mon 16 Nov 09:37:17 PST) and nothing was sent. Step 5 then ran at 10:28:03 ("SYNCED: 72 files at the
   harness's sha256", from HEAD `a90105da`) and step 4 again at 10:28:07: "FREE; the reboot gate: NEEDS-READ". No step was otherwise
   changed and no gate was skipped. `tools/claims-v3/e209/KIT.md.dated-note-1.md` section 4 registers this order for a new box root.
4. **(c) The first step 11 stopped at THE SCRUB at 10:57:21 PST; its stop path ran at 10:58:42 PST** (item 4 (c)).
   `rb/s22_collect_e209.sh` (`collect_e209.py`) read "COPY-BACK EXACT: 221 manifest lines OK, 224 files (1794940244-a2c0-E209)" and E208's
   checker ALL PASS (C0-C8), then stopped with exit 16, in its words: "COLLECT STOPPED: THE SCRUB found 1 file(s) with a private string
   (['first/fwgate-aifoundry2-c0-20261117-103044.json: the login name']): nothing written in LAB; tell the orchestrator". Nothing was
   written in the lab. The stop path at 10:58:42: the quiet desk flag lowered, the collect span left, the hold line removed, the booking
   released, row E (`rb/end_e209.sh`) rc 0. The cause, a kit defect: fwgate's read record names its attempt ledger by a path that holds the
   box's home (KIT.md.dated-note-1.md section 1). The fix and the second step 11: notes 10 and 11.
5. **(d) Step 7, the reboot gate: the day's first card command, stamped 10:30:44 PST, mode `read`** (item 4 (d)). fwgate's one
   firmware-revisions READ (a read, by the owner's rulings of Sun 15 Nov 2026 15:07:01 and 15:09:49 PST): "EQUAL: aifoundry2 card 0 at
   2026-11-17 10:30:44 PST matches E72's read of 2026-10-27 14:59:39 PDT in all seven fields"; the guard ok. Its record is
   `session/first/fwgate-aifoundry2-c0-20261117-103044.json` (note 11). The session's own config read followed at 10:30:48 PST (`queue.json`
   `t_first_ms`), so the card time from the day's first card command is the runner's 26.16 card-minutes plus about 4 s.
6. **(e) The never-run search, repeated** (item 4 (e); step 6n, 10:29:38-10:30:11 PST; REPORTED, never a gate): "NEVER-RUN 45 of 45
   points, 29 of 29 shapes" on this card (`neverrun-e209-card.txt`). The runs of E209's shapes on other cards, by experiment: E207
   (aifoundry3 card 0) and E212's aifoundry1 sessions a1c0-S1, a1c0-S2, a1c1-S1 and a1c1-S4, all after MM1-v2's freeze; E206 arms A and B
   (e30's shape; aifoundry3 card 0 and aifoundry1 card 1). The scanner also counts the lane folders card-e207, card-e211, card-e206a and
   card-e206b2 as other-card hits; card-e211 is a desk folder (no E211 session has run on any card). `ranbefore-e209.json` names no point and
   no case.
7. **(f) No stop, no dropped run, no cut point** (item 4 (f)). 62 of 62 runs ran (64 device processes, every one rc 0: `checks-e209.txt`
   C2); stop none; runner rc 0; the session ended at 10:56:57 PST after 26.16 card-minutes (the rule 45, the cap 55).
8. **(g) The clock: governed, 600/700/800 MHz, read and never set** (item 4 (g)). The clock is in every sample (15,675 of 15,675: 600 MHz
   11,545, 700 MHz 131, 800 MHz 3,999; C4). It stepped inside all 64 device processes' windows (card-e209's desk reading of the telemetry):
   - 62 started from the 600 MHz boot point and stepped up 0.26-1.46 s in;
   - the two third processes of the sus3 runs (007-e43 and 031-e39, proc-02) started at 800 MHz and dipped;
   - 8 processes ended at 600 MHz after stepping up: runs 011, 015, 024, 028, 030, 052, 053 and 056.
9. **The other gates, as the records read them** (measured; `checks-e209.txt`). The rest: "REST OPEN since 2026-11-17 00:50:41 PST (the
   last end 2026-11-17 00:10:41 PST, ...)", E208's session a2c0-S1r on this card, read at step B and again at step 7 before anything reached
   the card. The config read at 10:30:48: TDP 65 W, threshold 65 C, power state 3 (low_power), minion 600 MHz, 519 mV, read and never set,
   the same at the end (C3). The stop-path test passed and the smoke's three processes ended rc 0 (C3, C5). Peaks: the board 69.55 W (run
   036-e44), no sample over the 85 W line; the shires' mean die 55 C; the hottest-sensor latch 62 C at its first sample and never higher
   (C5).
10. **Step 11 again, by KIT.md.dated-note-1.md (`f92136dd`), 12:55:26-12:55:27 PST Tue 17 Nov 2026; no card command** (the lane
   `collect-e209`, round Q212). THE ONE-LAB RULE's collect span as `collect-e209` at 12:55:26; THE QUIET HOLD as `collect-e209` at
   12:55:26 (for this data commit); THE QUIET DESK FLAG raised as `card-e209`'s at 12:55:26 (`rb/quiet_e209.sh`); then
   `rb/s22_collect_e209_n1.sh` (`collect_e209_n1.py`) on card-e209's records, in its words: "COPY-BACK EXACT: 221 manifest lines OK, 224
   files (1794940244-a2c0-E209)" (a second copy-back on the box, under a new name; the first stays as it was); "THE CHECKS (E208's
   data checker, unchanged): ALL PASS"; THE MASK (note 11); "THE SCRUB: 226 files (the copy and the checks), no login name, home path or
   box-root path"; "DATA DIR docs/reports/data/2026-11-17-e209-blind-matmul-aifoundry2 (232 files)"; the flag lowered after the copy-back
   at 12:55:27. So this directory was written by `collect_e209_n1.py` (`collect_e209.py` with THE MASK, nothing else changed in what it
   collects, gates, checks or refuses), not by `collect_e209.py` as the line under the title says.
11. **THE MASK: one line of one file is not the box's bytes** (KIT.md.dated-note-1.md section 2; E200's registered form). In
   `session/first/fwgate-aifoundry2-c0-20261117-103044.json`, line 34 (fwgate's attempt-ledger path) reads
   `"ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl",` with the box's home written as "~". Every other line of that file and every
   other file under `session/` is the box's bytes, so the Files table's "byte for byte" holds but for that line; the raw record stays on
   aifoundry2, outside the lab. The record's sha256 (111 lines either way; 2,311 bytes on the box, 2,296 here):
   - **the box's bytes `a91fcc837457ffb2c447ceeb61800bfec3bde1eeab2a5f85884eb1ced95fe47d`**: line 20 of `session/MANIFEST.sha256`, which
     is as the box wrote it (221 lines; its own sha256 `e7ec7162a87b219e5dcf6704def364c8b6aabc58007bf7c7a43e6c9f1b5d5154`);
   - **the committed bytes `2d56a73219f7ba99b08986ef723a46477444feda7b3db7f255eb6e027e09a377`**.

   So `sha256sum -c MANIFEST.sha256` in `session/` fails on that one line by design, and step 13's manifest read
   (`collect_e209_n1.py --manifest-check`, in `rb/s24_score_e209_n1.sh`) reads "221 of 221 manifest lines OK (1 by THE MASK of
   KIT.md.dated-note-1.md ...)".
12. **SHA256SUMS** (every file here but itself): the collection wrote it before these notes; once they were added, it was made again in the
   same form, so only its `README.md` line differs from the collection's list.
13. **The model session's sealed forecast for E209** was posted after this session and before this data commit; it is registered as a
   REPORTED freeze line in `tools/claims-v3/sealed-e209/` (`d6d62660`). No number of it is here.
14. **Steps 12 and 13.** This commit is step 12, by `collect-e209` under THE QUIET HOLD; right after its push the lane leaves its collect
   span and removes its hold line (no booking was taken: the session had run). Step 13 (`rb/s24_score_e209_n1.sh`: E208's registered
   reducer on the committed session, the frozen scorer and the readings beside it) runs after this commit, its outputs outside the lab; a
   later lane commits them beside this directory.

## Files

| file | what | label |
|---|---|---|
| `session/` | the session's folder as E208's runner wrote it, byte for byte (its `MANIFEST.sha256` lists every file but itself, `runner.out` and `runner.rc`); `first/` holds step 7's reboot-gate record | measured |
| `checks-e209.json`, `checks-e209.txt` | E208's data lane's checks C0-C8 (unchanged checker) | desk check of the records |
| `build-record-aifoundry2.json` | the box root's build record of the day, byte for byte | record |
| `facts-e209.json` | the collection's facts | desk reading |
| `neverrun-e209-card.txt`, `ranbefore-e209.json` | step 6n's search and its labels (the scorer's `--labels` form) | desk, REPORTED |
| `SHA256SUMS` | every file here but itself | - |
