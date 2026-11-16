# E200 sitting 1, 2026-11-16, aifoundry2 card 0 under its governor (800 MHz under load) as found: RAN WHOLE (4 of 4 blocks) - the smoke and 13 trains in 400 processes, 43.63 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST, Q192's card lane `card-e200`, run from aifoundry2 itself. The model session's proposal X02 on a second
card: E197's registered protocol (registration `ea4b4ad7`, kit `2c68a633`) run on aifoundry2 card 0 as E200 (registration `7361cc24`,
[`E200.md`](../../../../tools/claims-v3/e200/E200.md), its departures W1 and C1-C3; forecast sealed by sha256, contents sealed), kitted
(`b4a5f6f2`, [`KIT.md`](../../../../tools/claims-v3/e200/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e200/CARD-LANE-BRIEF.md)),
verified (verify-e200: HOLDS WITH FIXES; fix-e200: FIXED before the land), landed (land-e200: LANDED) and readiness-checked (ready-e200:
READY WITH GAPS), all before any E200 datum; no E200 file changed since the kit (step 0: 72 of 72 anchor lines as stated at HEAD `8aa6185e`
= GitHub main; steps 2 and 11: HISTORY OK). Run on the owner's standing go (E200.md 12: his words of Sun 15 Nov 2026 at 10:05:42, 10:22:36
and 17:21:16 PST, "Try again", and 21:51:09 PST), with G = this lane's booking of aifoundry2 at 08:02:34 PST Mon 16 Nov 2026. Sitting 1:
blocks A-D, the full plan. Nothing was set on the card.*

**The freeze line:** the model session's sealed aifoundry2 forecast is known to the lab only by its sha256,
`2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733` (E200.md section 0; step 2 printed it, later notes: none). **No forecast
number and no score are in this directory:** the model session scores its sealed forecast privately, after this commit. The reduced prices
are not here (section "Reduced" below).

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command (step 7's: fwgate's read, stamped 08:13:25) to "session end" (08:57:03) | 43.63 (cap 50; the registered estimate about 46.3 at the mean climb) | measured (the session's clock) |
| train blocks begun and complete | "train blocks started: 4 of 4 (A B C D); complete: 4 (A B C D); train processes recorded: 400" | measured |
| train processes recorded (of the plan's 400) and launch records | 400 (A 152, B 106, C 80, D 62; 13 trains: T1-T6, T8-T13, T15); 5,420 launch records, every one ok | measured |
| device processes and their exits | 429 (27 anchors, 402 train processes: 2 in the smoke, 400 in blocks A-D), every one exit 0 | measured |
| the run order | the 429 device processes in the dry listing's order (each train's F kind, S kind and orientation; each anchor's kind): 0 mismatches against the kit's committed full-plan listing (E197's `desk/dry-e197-full.txt`, which E200's listing equals but for W1's window word) | desk check of the measured records |
| how the sitting ended | "stop: none"; "SITTING-RESULT: smoke passed; train blocks complete 4 (A B C D); card stop none"; run_session.sh rc 0 ("session done (rc 0): 5420 launches recorded"); wrapper rc 0 | measured |
| the runner's smoke gate and the kit's smoke check (with the smoke's clock, C3) | "the runner's smoke gate: passed (26 launches, rates 523870000000.0-524140000000.0)"; "the kit's smoke check: passed (every smoke launch ok, check_bad 0, 1024 participants; every smoke device process exit 0; both smoke train processes at 800 MHz from their first launch + 1.5 s and their last launch at 780-810 MHz by its own count)" (08:14:13) | measured |
| the clock live (C3, the kit's watch) | "train processes judged 400; at 800 MHz 394; OFF 6; not judged 0; the longest OFF run 1": OFF were block A T1 processes 43, 100 and 112, block B T3 process 8 and T5 process 14, block D T12 process 6, each with 6-13 of its 40-43 samples at 600 or 700 MHz after its first launch + 1.5 s; never two in a row, so C3 did not stop the sitting | measured |
| THE DIE GATE (57 C, E200.md 9) | "the die gate, read 1 (rc 0): 5 sample(s), the highest minshire[0] 46 C: OK"; it passed after 1 s (08:13:29) | measured |
| the die while idle | in each of the session's 36 idle spans the shires' mean (`minshire[0]`) ended at or below where it began (0 rises); the highest idle reading 58 C, falling, right after block A's trains | desk read of the measured telemetry |
| the deadline (a train skipped or cut) | none: the session ended at 08:57:03, before the runner's deadline (about 09:01:25) and the end-stop (09:02:55); T15 ran (18 processes) | measured |
| a device process that outlived its timeout's TERM (the kit's hang watch) | none (the watch's closing record: hung []) | measured |
| telemetry samples: at 800 MHz, at 600 MHz, at other clocks, without a clock | 21,359 / 4,468 / 286 (all at 700 MHz) / 0 of 26,113 (08:13:29.1-08:57:02.6) | measured |
| board power, peak; die, peak (minshire[0]); the latch, peak (minshire[2]) | 40.94 W (08:21:10.4); 59 C (08:20:43.7); 61 C (08:20:48.3); the pmic's sensor 59 C | measured |
| the configuration at the start (step 7) and at the end (the wrapper) | TDP 65 W / threshold 65 C / 600 MHz at rest, power state low_power, minion_mv 519, /dev/et0_mgmt and device ID 0 (08:13:26, `session/first/config.out`); the same at the end: "the configuration at the sitting's end (reported, never a gate): rc 0; ... tdp_w 65, temp_threshold_c 65, low_power, minion_mhz 600, minion_mv 519" (08:57:03) | measured (READs) |
| the firmware identity (THE REBOOT GATE, E200.md 8) | fwgate's look NEEDS-READ (this boot, 2026-11-13 16:53:28 PST, is after E72's read of record); its one read at 08:13:26: "EQUAL: aifoundry2 card 0 at 2026-11-16 08:13:26 PST matches E72's read of 2026-10-27 14:59:39 PDT in all seven fields" (`session/first/fwgate-aifoundry2-c0-20261116-081326.json`); step 9's guard: "identity: ... ok" | measured (READ) |
| the sampler | the plain sampler, `ettelem sample --seconds <CAP_S + 600> --every-ms 100` (CAP_S 2,936 s this sitting), through E200's guard (build/ettelem-hpl/ettelem at 77a46171...) | registered (E197.md 4; the kit) |

**Reading the checker's rail row (when the reduction's dated note fills it).** E197's REPORTED row "rail voltage samples beyond +-3 mV of
the session median in the train's spans" reads high by design on this card: every train process's span includes its climb, run at the
600 MHz point's lower voltage, so the count is no rail fault and never a gate (KIT.md 7; fix-e200, verify-e200's F8).

## Registered against happened

| registered (E200.md, E197.md by reference, KIT.md) | happened |
|---|---|
| aifoundry2 card 0 under its governor as found, nothing set (E200.md 3): TDP 65 W, threshold 65 C, 600 MHz at rest at the start | step 7's config read at 08:13:26: 65 W / 65 C / 600 MHz, 519 mV; the end read at 08:57:03: the same; nothing set |
| THE REBOOT GATE: the lab's fwgate (E200.md 8) | look NEEDS-READ (step 4, 08:12:16); the read EQUAL in all seven fields (step 7, 08:13:26); step 9's guard "identity: aifoundry2 card 0 booted 2026-11-13 16:53:28 PST, before the firmware read of 2026-11-16 08:13:26 PST (...): ok" |
| the 40-minute rest before the sitting's first card command (E200.md 11) | "rest: 444 minutes since E194's session end (2026-11-16 00:49:00 PST; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry2 read)" (step 7, read on the box before anything reached the card; step 9 read it again) |
| the window: G = the booking, last start G+1:30, last end G+3:30 (E200.md 12) | G 08:02:34 (the booking); `s02_window_e200.sh 1 2026-11-16 09:33 11:33` (step 1, 08:03:29); first card command 08:13:25 (before 09:33); the sampler's stop 08:57:03 (before 11:33) |
| the plan (sitting 1: full unless the window cannot hold it) | full (logged by step 7 before the first card command) |
| THE DIE GATE: minshire[0] at or below 57 C, up to 10 minutes, in the cap | passed on its first read (46 C), 1 s |
| W1: every launch at --window 320000000; E200's runner at 8774027b... | the dry pass on the box: "LISTING SAME full: 474 lines, 429 device calls, each with W1's window" and the short plan's 376 lines, 331 device calls; `ref/run_trains.py` sha256 8774027b4bba78c6... |
| C1, THE CLOCK RULE (the reduction's), C2 (nothing read before 2.0 s): applied after the data commit | step 13's "e200" line, filled by the dated note |
| C3: the smoke's clock; three train processes in a row off 800 MHz end the sitting | the smoke's clock passed; 394 of 400 train processes at 800 MHz, 6 OFF, the longest OFF run 1: no C3 stop |
| the smoke and its gate (the runner's), the kit's smoke check | both passed (Results) |
| the blocks, trains, processes and orientations in trains.tsv's order (E197.md 5) | 429 device processes in the full plan's listed order (desk check); 400 train processes over 13 trains |
| the cap: 50 card-minutes from the first card command; the runner's deadline at the first card command + the cap - 120 s; the end-stop at the cap - 30 s | "the cap 3000 s, at 09:03:25 PST; CAP_S 2936 s, the runner's deadline at about 09:01:25 PST ...; the end-stop at 09:02:55 PST"; no train skipped or cut; the end-stop did not fire; 2,618 s used ("card time 2618 s from the first card command") |
| the stops (E197.md 9 with C3 in the kit's clock stop's place; aifoundry2's 85 W and 80 C lines, E200.md 9) | none fired ("stop: none"); peaks 40.94 W and 59 C (minshire[0]), 61 C (minshire[2]): under E189's 65 W and 70 C lines, under the 82 W predicted-peak line and aifoundry2's 85 W and 80 C lines |
| departure D1: `timeout 10`, never a KILL | every device process under `timeout 10` (`ref/run_trains.py`); no HUNG line |
| THE QUIET DESK FLAG from the look to the copy-back (E200.md 12) | raised 08:04:00 (before the look, 08:12:16), lowered 08:57:27 (after step 11's COPY-BACK EXACT); THE P2 COUNT 0 at 08:12:02, at the look, at 08:13:25 before step 7 and in step 9's launch call |
| one session of ours on this card; the card exclusive | the look FREE before (08:12:16) and after (08:57:25) the session; et-who clean at step 7 |

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-9 set by his go, the kit and the round's plan before the session; 10-13 read after the collection, said so)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about
   discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I don't need to
   reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used, feel free to
   use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); and "don't worry about hitting the
   limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09). Beside them, a report of
   his words (not his own text): the round's Discussion #2.5.1 at 19:34:12, "The aifoundry cards are all free right now (I can see it on
   the lab dashboard's live view, though a collector is running on them); feel free to use them.", and #2.5.1.2 at 21:51:33, which named
   aifoundry2 for X02 as E200. **His words name no experiment: the registered items are taken as their defaults** (E200.md 12):
   aifoundry2 card 0 under its governor as found, reads only, nothing set; sitting 1 about 46 card-minutes, cap 50; sitting 2 about 28,
   cap 35; the 40-minute rests.
2. **The card day: Mon 16 Nov 2026,** the day of the booking (E200.md 12: Mon 16 Nov 2026 or a later day, after E194's session on this
   card, which ended at 00:49:00 PST; the round's usage-limit stop of about 18:05 PST Sun 15 Nov had moved every card day to Monday).
3. **G = the booking:** `book.sh take aifoundry2 card-e200` printed BOOKED at **08:02:34 PST** Mon 16 Nov: last start G+1:30 and last end
   G+3:30, each rounded up to the whole minute: **09:33 and 11:33 PST** (step 1 at 08:03:29; the window file's `RB_GO_EPOCH`, 1794845009 =
   08:03:29 PST, is the moment step 1 wrote it, not his go).
4. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other
   etiquette check stood: the look before the session (et-who, who, uptime, ps as counts, the holder rule: FREE at 08:12:16), step 7's reads
   (et-who clean at 08:13:26), the session's own free check and card lock, and `timeout 10` (no `-k`) on every device process.
5. **The host's package counter: not read** (his words do not name it): no E200 step, option or code reads it.
6. **The desk and the orchestrator.** Every desk step ran on aifoundry2 itself (the box is the desk; the kit's drivers reach it as k6
   does) under `/usr/bin/python3` 3.12.3. The orchestrating session is the round's session on its yvb3 Claude account, which took the round
   over on Sat 14 Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov. No network approval was needed or named;
   the kit's login-link stop stayed live and no step met a login link (the round's file of checks held 70 lines before and after).
7. **THE QUIET DESK FLAG's form and span.** Raised and lowered only with `rb/quiet_e200.sh` (its line `e200 card-e200 <time>`), never
   written by hand in the round's shorter `<lane> <time>` form, which the kit's steps 4-11 refuse (fix-e200's F7; the go lines). Raised
   08:04:00; the round's in-flight wait (a read-only step of the go lines) then waited until 08:12:02 for one desk-test sandbox of another
   lane that had started before the raise and ended by itself (nothing was signalled); THE P2 COUNT read 0 every time; lowered 08:57:27.
8. **The rest and the order on this card.** The previous session of ours on aifoundry2 card 0 was E194's (00:33:27-00:49:00 PST, data
   `72514ce5`). E200's rest rule, read on the box at step 7 (08:13:25) and again at step 9, printed 444 minutes (40 required).
9. **Departure D1 (E197.md 15, E200's by reference):** E200's runner (E197's lab runner with W1) runs every device process under
   `timeout 10`, never `-k 1`: no device process is ever killed. None outlived its TERM.
10. **The firmware read is the sitting's first card command** (KIT.md 4): fwgate's look read NEEDS-READ (E72's read of record precedes
    this boot), so step 7 sent fwgate's one `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` query (a READ by the owner's rulings, below) at 08:13:26,
    after the stamp of 08:13:25; EQUAL in all seven fields; its record and raw answer are in `session/first/`.
11. **"Reads only" is the management node's** (a lab-wide correction of Mon 16 Nov 2026, 01:4x PST, for the next records round): every
    runtime creation sends the ops node's abort on every submission queue of the card it opens, and the firmware aborts what is pending
    there; harmless with the card held alone (et-who empty, the card lock held), as here. Nothing changes in the kit.
12. **The build** (step 6, 08:12:28-08:12:31 on the box, its first start that day): REGFILE-BUILT rc 0; the kernel ELF's file sha256
    feafba8d..., its `.text` ce8c93c6... (the `.text` of E197's desk build); the host `regfile_host` 218dd5a8...; E200's runner 8774027b...;
    the reader 77a46171... at its pin; the harness (54 files) and the preflight (dmcmd_audit GO) read on the box after it.
13. **Not blind to E197's data** (E200.md's preamble, REPORTED): E197's sitting 1 (`ae3c1ee0`) and its note 1 (`8aa6185e`) landed before
    this sitting; step 2 reported 27 E197 data paths and never gated on them; nothing of E200 changed.

## Device commands sent

READs only (dmcmd_audit_v2 GO, KIT.md 6): fwgate's one `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` query at 08:13:26, its look having read
NEEDS-READ (a READ by the owner's rulings, Sun 15 Nov 2026: "Firmware revisions query was a false positive. It should have never been
forbidden. Reading operations and firmware are always allowed." at 15:07:01 PST, and "Yeah, fix the corresponding guards. I don't want to
modify firmware, but commands which read firmware should be fine." at 15:09:49 PST; the audit table v2's id 14 line,
`tools/claims-v3/dmcmd_table_v2.json`: READ); step 7's and the end's `ettelem config` (five READs each); the die gate's one `ettelem sample
--seconds 1 --every-ms 200` read and the session's one `ettelem sample --every-ms 100` (six READs a sample), all through E200's guard; the
host opened the ops node only (and each runtime creation sent the ops node's abort on the card's queues: note 11); `et-who --check` sends
no device command. No set, no reset, no statistics reset, no firmware change, no KILL to any process.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, ref-patch.txt (empty: the patch printed nothing), diegate-1.jsonl and .err, run_session.out, watch.jsonl, watch.out, summary.txt, config-end.out and .err, MANIFEST.sha256 (the box's), wrapper.rc |
| `session/first/` | step 7's folder: the config read's config.out and config.err (and the call's own config-081326.*), et-who after it, and fwgate's read record with its raw answer (fwgate-aifoundry2-c0-20261116-081326.json, .stdout, .stderr) |
| `ref/` | the four files the session ran: E197's run_session.sh, stopwatch.py and trains.tsv byte for byte; E200's runner run_trains.py (E197's lab runner with W1, 8774027b...) |
| `run/` | the reference session's own files: runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, SESSION_DONE, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e200-1.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it (this README is not in it) |

The public-text scan before this commit read two hits in the collected files, both the harness line's word for the kit's folder on
the box ("HARNESS OK: 54 files at their sha256 under the ..."), in `session/harness.txt` and `session/session.log`, as in E193's,
E195's and E197's committed data; they are kept as collected. The round's path classes also match the device layer's address-format
lines (the base addresses of the card's on-chip memory in each format) in `run/stderr.txt`, `run/sampler.err` and the config and
die-gate reads' stderr: the card's own printout, as in E194's and E197's committed data, not a desk path.

## Reduced (not here)

Step 13 (`rb/s24_reduce_e200.sh 1`: E200's registered reduction `reduce_e200.py`, sha256 10a44034..., unchanged, never `--prediction`,
then the kit's checker) runs on this directory only after it is committed; its outputs (`regfile-e200-s1.json`, `checks-e200-1.json`) are
committed beside it by a later lane in a dated note, which fills this section. If a second sitting runs (this sitting's SITTING-RESULT
qualifies it), its step 13 pools both sittings into `regfile-e200.json`, E200's registered result.

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2; R=$(mktemp -d)
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/sitting-1" && cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$R/sitting-1/" && gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/sitting-1/telemetry.jsonl"
    if [ -f "$D/run/STOP" ]; then cp "$D/run/STOP" "$R/sitting-1/"; fi
    for p in runs.jsonl marks.jsonl telemetry.jsonl; do [ "$(awk -v p="./run/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/sitting-1/$p" | cut -d' ' -f1)" ] && echo "run/$p: the box's bytes" || echo "run/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e200/reduce_e200.py "$R/sitting-1" --out "$R/regfile-e200-s1.json"
    /usr/bin/python3 -I -B tools/claims-v3/e200/check_e200.py checks "$R/regfile-e200-s1.json" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the telemetry and set it, `run/runs.jsonl` and `run/marks.jsonl` against the box's own
manifest (`session/MANIFEST.sha256`: every line must say "the box's bytes"); run E200's registered reduction (`reduce_e200.py`, unchanged,
never `--prediction`: it loads E197's reducer by path and sha256 and applies C1 and C2); and read E197.md 8's rows with the kit's checker,
the clock row by C1 with its tallies. This sitting has no `run/STOP` (no stop fired).

## Labels

Measured: every number in Results and in the "happened" column, from this sitting's own files and the runbook's log. Registered: the
protocol (E197.md by reference), W1 and C1-C3, the caps, the stops, the die gate, the reduction (E200.md). Desk checks of code: the kit's
tests (KIT.md). Desk reads of the measured records: the run order (this lane's reading of `run/marks.jsonl` against E197's
`desk/dry-e197-full.txt`) and the die in the idle spans (`run/marks.jsonl`'s idle spans against `run/telemetry.jsonl.gz`). Not blind to:
E200.md 16's list, and E197's data (note 13). Interpreter: the desk's `/usr/bin/python3` 3.12.3 on aifoundry2.
