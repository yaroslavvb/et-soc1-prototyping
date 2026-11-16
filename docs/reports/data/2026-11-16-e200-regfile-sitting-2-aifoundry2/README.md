# E200 sitting 2, 2026-11-16, aifoundry2 card 0 under its governor (800 MHz under load) as found: RAN WHOLE (block E) - the smoke and 3 trains in 266 processes, 26.45 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST, Q192's card lane `card-e200`, run from aifoundry2 itself. The model session's proposal X02 on a second
card: E197's registered protocol (registration `ea4b4ad7`, kit `2c68a633`) run on aifoundry2 card 0 as E200 (registration `7361cc24`,
[`E200.md`](../../../../tools/claims-v3/e200/E200.md), its departures W1 and C1-C3; forecast sealed by sha256, contents sealed), kitted
(`b4a5f6f2`, [`KIT.md`](../../../../tools/claims-v3/e200/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e200/CARD-LANE-BRIEF.md)),
verified (verify-e200: HOLDS WITH FIXES; fix-e200: FIXED before the land), landed (land-e200: LANDED) and readiness-checked (ready-e200:
READY WITH GAPS), all before any E200 datum; no E200 file changed since the kit (step 0, in its sitting-2 form: 77 of 77 anchor lines as
stated at HEAD `548d736e` = GitHub main; steps 2 and 11: HISTORY OK). Run on the owner's standing go (E200.md 12: his words of Sun 15 Nov
2026 at 10:05:42, 10:22:36 and 17:21:16 PST, "Try again", and 21:51:09 PST), on the booking held since 08:02:34 PST for both sittings,
sitting 2's G = sitting 1's end + 40 minutes = 09:37:03 PST. Sitting 2: block E, the ext plan, after sitting 1
([`../2026-11-16-e200-regfile-sitting-1-aifoundry2/`](../2026-11-16-e200-regfile-sitting-1-aifoundry2/), data `548d736e`). Nothing was
set on the card.*

**The freeze line:** the model session's sealed aifoundry2 forecast is known to the lab only by its sha256,
`2eba6ef4b60241674628dde125273db4547b0ba17dd6d5a3e30935c7c6e89733` (E200.md section 0; step 2 printed it, later notes: none). **No forecast
number and no score are in this directory:** the model session scores its sealed forecast privately, after this commit. The reduced prices
are not here (section "Reduced" below).

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command (step 7's: fwgate's read, stamped 09:37:16) to "session end" (10:03:43) | 26.45 (cap 35; the registered estimate about 28.2 at the mean climb) | measured (the session's clock) |
| train blocks begun and complete | "train blocks started: 1 of 1 (E); complete: 1 (E); train processes recorded: 266" | measured |
| train processes recorded (of the plan's 266) and launch records | 266 (T1 230, T7 18, T14 18); 3,541 launch records, every one ok | measured |
| device processes and their exits | 277 (9 anchors, 268 train processes: 2 in the smoke, 266 in block E), every one exit 0 | measured |
| the run order | the 277 device processes in the dry listing's order (each train's F kind, S kind and orientation; each anchor's kind): 0 mismatches against the kit's committed ext-plan listing (E197's `desk/dry-e197-ext.txt`, which E200's listing equals but for W1's window word) | desk check of the measured records |
| how the sitting ended | "stop: none"; "SITTING-RESULT: smoke passed; train blocks complete 1 (E); card stop none"; run_session.sh rc 0 ("session done (rc 0): 3541 launches recorded"); wrapper rc 0 | measured |
| the runner's smoke gate and the kit's smoke check (with the smoke's clock, C3) | "the runner's smoke gate: passed (26 launches, rates 523860000000.0-524100000000.0)"; "the kit's smoke check: passed (every smoke launch ok, check_bad 0, 1024 participants; every smoke device process exit 0; both smoke train processes at 800 MHz from their first launch + 1.5 s and their last launch at 780-810 MHz by its own count)" (09:38:04) | measured |
| the clock live (C3, the kit's watch) | "train processes judged 266; at 800 MHz 263; OFF 3; not judged 0; the longest OFF run 1": OFF were block E T1 processes 53, 126 and 224, each with 6-13 of its 40-41 samples at 600 or 700 MHz after its first launch + 1.5 s; never two in a row, so C3 did not stop the sitting | measured |
| THE DIE GATE (57 C, E200.md 9) | "the die gate, read 1 (rc 0): 5 sample(s), the highest minshire[0] 46 C: OK"; it passed after 1 s (09:37:19) | measured |
| the die while idle | in each of the session's 12 idle spans the shires' mean (`minshire[0]`) ended at or below where it began (0 rises) | desk read of the measured telemetry |
| the deadline (a train skipped or cut) | none: the session ended at 10:03:43, before the runner's deadline (about 10:10:16) and the end-stop (10:11:46) | measured |
| a device process that outlived its timeout's TERM (the kit's hang watch) | none (the watch's closing record: hung []) | measured |
| telemetry samples: at 800 MHz, at 600 MHz, at other clocks, without a clock | 13,972 / 1,672 / 172 (all at 700 MHz) / 0 of 15,816 (09:37:19.8-10:03:42.7) | measured |
| board power, peak; die, peak (minshire[0]); the latch, peak (minshire[2]) | 41.23 W (09:55:56.2); 59 C (09:52:53.7); 61 C, read from the session's first sample on (a latched value, at rest with minshire[0] at 46 C; sitting 1 first reached 61 C at 08:20:48); the pmic's sensor 59 C | measured |
| the configuration at the start (step 7) and at the end (the wrapper) | TDP 65 W / threshold 65 C / 600 MHz at rest, power state low_power, minion_mv 519, /dev/et0_mgmt and device ID 0 (09:37:17, `session/first/config.out`); the same at the end: "the configuration at the sitting's end (reported, never a gate): rc 0; ... tdp_w 65, temp_threshold_c 65, low_power, minion_mhz 600, minion_mv 519" (10:03:43) | measured (READs) |
| the firmware identity (THE REBOOT GATE, E200.md 8) | fwgate's look NEEDS-READ again (sitting 1's EQUAL record lives in sitting 1's step-7 folder, not in fwgate's committed records); its read at 09:37:17: "EQUAL: aifoundry2 card 0 at 2026-11-16 09:37:17 PST matches E72's read of 2026-10-27 14:59:39 PDT in all seven fields" (`session/first/fwgate-aifoundry2-c0-20261116-093717.json`); step 9's guard: "identity: ... ok" | measured (READ) |
| the sampler | the plain sampler, `ettelem sample --seconds <CAP_S + 600> --every-ms 100` (CAP_S 2,037 s this sitting), through E200's guard (build/ettelem-hpl/ettelem at 77a46171...) | registered (E197.md 4; the kit) |

**Reading the checker's rail row (when the reduction's dated note fills it).** E197's REPORTED row "rail voltage samples beyond +-3 mV of
the session median in the train's spans" reads high by design on this card: every train process's span includes its climb, run at the
600 MHz point's lower voltage, so the count is no rail fault and never a gate (KIT.md 7; fix-e200, verify-e200's F8).

## Registered against happened

| registered (E200.md, E197.md by reference, KIT.md) | happened |
|---|---|
| aifoundry2 card 0 under its governor as found, nothing set (E200.md 3): TDP 65 W, threshold 65 C, 600 MHz at rest at the start | step 7's config read at 09:37:17: 65 W / 65 C / 600 MHz, 519 mV; the end read at 10:03:43: the same; nothing set |
| THE REBOOT GATE: the lab's fwgate (E200.md 8) | look NEEDS-READ (step 4, 09:18:32); the read EQUAL in all seven fields (step 7, 09:37:17); step 9's guard "identity: aifoundry2 card 0 booted 2026-11-13 16:53:28 PST, before the firmware read of 2026-11-16 09:37:17 PST (...): ok" |
| the second sitting's condition: sitting 1 ran its smoke and a train block with no stop naming the card, 40 minutes before (E200.md 5, 11) | sitting 1's "SITTING-RESULT: smoke passed; train blocks complete 4 (A B C D); card stop none" (its session end 08:57:03); step 9: "sitting 1 held first: build/e200/T1794845607"; step 7's rest line: "rest: 40 minutes since E200's session end (2026-11-16 08:57:03 PST; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry2 read)" (read on the box before anything reached the card; step 9 read it again) |
| the window: one booking for both sittings, sitting 2's G = sitting 1's end + 40 minutes; last start G+1:30, last end G+3:30 (E200.md 12) | G2 09:37:03; `s02_window_e200.sh 2 2026-11-16 11:08 13:08` (step 1, 09:03:31); first card command 09:37:16 (before 11:08); the sampler's stop 10:03:43 (before 13:08) |
| the plan (sitting 2: ext) | ext (logged by step 7 before the first card command) |
| THE DIE GATE: minshire[0] at or below 57 C, up to 10 minutes, in the cap | passed on its first read (46 C), 1 s |
| W1: every launch at --window 320000000; E200's runner at 8774027b... | the dry pass on the box: "LISTING SAME ext: 292 lines, 277 device calls, each with W1's window"; `ref/run_trains.py` sha256 8774027b4bba78c6... |
| C1, THE CLOCK RULE (the reduction's), C2 (nothing read before 2.0 s): applied after the data commit | step 13's "e200" lines (the pooled reduction), filled by the dated note |
| C3: the smoke's clock; three train processes in a row off 800 MHz end the sitting | the smoke's clock passed; 263 of 266 train processes at 800 MHz, 3 OFF, the longest OFF run 1: no C3 stop |
| the smoke and its gate (the runner's), the kit's smoke check | both passed (Results) |
| the block, trains, processes and orientations in trains.tsv's order (E197.md 5) | 277 device processes in the ext plan's listed order (desk check); 266 train processes over 3 trains (T1, T7, T14) |
| the cap: 35 card-minutes from the first card command; the runner's deadline at the first card command + the cap - 120 s; the end-stop at the cap - 30 s | "the cap 2100 s, at 10:12:16 PST; CAP_S 2037 s, the runner's deadline at about 10:10:16 PST ...; the end-stop at 10:11:46 PST"; no train skipped or cut; the end-stop did not fire; 1,586 s used ("card time 1586 s from the first card command") |
| the stops (E197.md 9 with C3 in the kit's clock stop's place; aifoundry2's 85 W and 80 C lines, E200.md 9) | none fired ("stop: none"); peaks 41.23 W and 59 C (minshire[0]), 61 C (minshire[2], latched): under E189's 65 W and 70 C lines, under the 82 W predicted-peak line and aifoundry2's 85 W and 80 C lines |
| departure D1: `timeout 10`, never a KILL | every device process under `timeout 10` (`ref/run_trains.py`); no HUNG line |
| THE QUIET DESK FLAG from the look to the copy-back (E200.md 12) | raised 09:16:24 (before the look, 09:18:32), lowered 10:04:07 (after step 11's COPY-BACK EXACT); THE P2 COUNT 0 at 09:18:19, at the look, at 09:37:15 before step 7 and in step 9's launch call |
| one session of ours on this card; the card exclusive | the look FREE before (09:18:32) and after (10:04:05) the session; et-who clean at step 7 |

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-11 set by his go, the kit and the round's plan before the session; 12-14 read after the collection, said so)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about
   discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I don't need to
   reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used, feel free to
   use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); and "don't worry about hitting the
   limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09). Beside them, a report of
   his words (not his own text): the round's Discussion #2.5.1 at 19:34:12, "The aifoundry cards are all free right now (I can see it on
   the lab dashboard's live view, though a collector is running on them); feel free to use them.", and #2.5.1.2 at 21:51:33, which named
   aifoundry2 for X02 as E200. **His words name no experiment and do not withhold sitting 2: the registered items are taken as their
   defaults** (E200.md 12): aifoundry2 card 0 under its governor as found, reads only, nothing set; sitting 2 about 28 card-minutes, cap
   35, after a sitting 1 that qualifies; the 40-minute rests.
2. **The card day: Mon 16 Nov 2026,** the day of the booking (E200.md 12: Mon 16 Nov 2026 or a later day; the round's usage-limit stop of
   about 18:05 PST Sun 15 Nov had moved every card day to Monday). Both sittings ran that day.
3. **One booking for both sittings:** `book.sh take aifoundry2 card-e200` printed BOOKED at **08:02:34 PST** (sitting 1's G) and the booking
   was kept through sitting 2 (the go lines; E200.md 12: "A card lane that books once for both sittings uses that G for sitting 1;
   sitting 2's G is then sitting 1's end plus 40 minutes"). Sitting 1's session ended at 08:57:03, so **G2 = 09:37:03**: last start 11:08,
   last end 13:08 PST (step 1 at 09:03:31; the window file's `RB_GO_EPOCH`, 1794848611 = 09:03:31 PST, is the moment step 1 wrote it, not
   his go).
4. **Step 0's sitting-2 form.** The go's anchor read for this sitting was ready-e200's `go_anchors_e200.sh 2 <sitting 1's data commit>
   <its directory>` (77 of 77 as stated at 09:03:27): sitting 1's form can only read NOT AS STATED once sitting 1's data are committed (the
   way E197's sitting 2 was lost, E197 data note 1), so this form replaces those three lines with eight that pin sitting 1's directory to
   its data commit `548d736e`. The script is the readiness lane's, outside the repository (ready-e200's gap 3); step 2 then read "E200 data
   paths in any ref: 38 (sitting 1's: 38)" and passed.
5. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other
   etiquette check stood: the look before the session (et-who, who, uptime, ps as counts, the holder rule: FREE at 09:18:32), step 7's reads
   (et-who clean at 09:37:17), the session's own free check and card lock, and `timeout 10` (no `-k`) on every device process.
6. **The host's package counter: not read** (his words do not name it): no E200 step, option or code reads it.
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 itself under `/usr/bin/python3` 3.12.3. The orchestrating session is
   the round's session on its yvb3 Claude account. No network approval was needed or named; the kit's login-link stop stayed live and no
   step met a login link (the round's file of checks held 70 lines before and after).
8. **THE QUIET DESK FLAG's form and span.** Raised and lowered only with `rb/quiet_e200.sh` (its line `e200 card-e200 <time>`), never
   written by hand in the round's shorter form, which the kit's steps 4-11 refuse (fix-e200's F7; the go lines). Lowered after sitting 1's
   copy-back at 08:57:27; raised again for this sitting at 09:16:24, later than its step 2 (09:03:39) so that it was up for as short a
   span as the rest allowed; the round's in-flight wait then read 0 desk-test sandboxes of ours from before the raise at 09:18:19; THE P2
   COUNT read 0 every time; lowered 10:04:07.
9. **The rest.** The previous session of ours on this card was sitting 1's (08:13:25-08:57:03). E200's rest rule, read on the box at step 7
   (09:37:16) and again at step 9, printed 40 minutes (40 required).
10. **Departure D1 (E197.md 15, E200's by reference):** E200's runner (E197's lab runner with W1) runs every device process under
    `timeout 10`, never `-k 1`: no device process is ever killed. None outlived its TERM.
11. **A second firmware read on this boot** (ready-e200's gap 2). Step 7's look passes no earlier sitting's folder, and sitting 1's EQUAL
    record lives in its own step-7 folder, not in fwgate's committed records, so this sitting's look read NEEDS-READ again and step 7 sent
    fwgate's `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` query a second time this boot (09:37:17), as E200.md 8 registers it per sitting ("only
    on NEEDS-READ ... --out <the sitting's data folder>/fwgate"); KIT.md 6 and CARD-LANE-BRIEF.md 5 say "once a boot". It is a READ by the
    owner's rulings (below), and it read EQUAL, as sitting 1's did (08:13:26).
12. **The latch's reading.** `minshire[2]` read 61 C from this session's first sample (at rest, `minshire[0]` 46 C) to its last: a latched
    value, which sitting 1's trains first raised to 61 C at 08:20:48; it is reported as read, under aifoundry2's 80 C line.
13. **"Reads only" is the management node's** (a lab-wide correction of Mon 16 Nov 2026, 01:4x PST, for the next records round): every
    runtime creation sends the ops node's abort on every submission queue of the card it opens, and the firmware aborts what is pending
    there; harmless with the card held alone (et-who empty, the card lock held), as here. Nothing changes in the kit.
14. **Not blind to E197's data, nor to this experiment's sitting 1** (E200.md's preamble, REPORTED): E197's sitting 1 (`ae3c1ee0`) and its
    note 1 (`8aa6185e`) landed before E200 ran, and sitting 1's reduction ran after its data commit, before this sitting (step 13, its
    outputs not committed); nothing of E200 changed.

## Device commands sent

READs only (dmcmd_audit_v2 GO, KIT.md 6): fwgate's `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` query at 09:37:17, its look having read
NEEDS-READ (the second such query on this boot, note 11; a READ by the owner's rulings, Sun 15 Nov 2026: "Firmware revisions query was a
false positive. It should have never been forbidden. Reading operations and firmware are always allowed." at 15:07:01 PST, and "Yeah, fix
the corresponding guards. I don't want to modify firmware, but commands which read firmware should be fine." at 15:09:49 PST; the audit
table v2's id 14 line, `tools/claims-v3/dmcmd_table_v2.json`: READ); step 7's and the end's `ettelem config` (five READs each); the die
gate's one `ettelem sample --seconds 1 --every-ms 200` read and the session's one `ettelem sample --every-ms 100` (six READs a sample), all
through E200's guard; the host opened the ops node only (and each runtime creation sent the ops node's abort on the card's queues: note
13); `et-who --check` sends no device command. No set, no reset, no statistics reset, no firmware change, no KILL to any process.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, ref-patch.txt (empty: the patch printed nothing), diegate-1.jsonl and .err, run_session.out, watch.jsonl, watch.out, summary.txt, config-end.out and .err, MANIFEST.sha256 (the box's), wrapper.rc |
| `session/first/` | step 7's folder: the config read's config.out and config.err (and the call's own config-093717.*), et-who after it, and fwgate's read record with its raw answer (fwgate-aifoundry2-c0-20261116-093717.json, .stdout, .stderr) |
| `ref/` | the four files the session ran: E197's run_session.sh, stopwatch.py and trains.tsv byte for byte; E200's runner run_trains.py (E197's lab runner with W1, 8774027b...) |
| `run/` | the reference session's own files: runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, SESSION_DONE, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e200-2.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it (this README is not in it) |

The public-text scan before this commit read two hits in the collected files, both the harness line's word for the kit's folder on
the box ("HARNESS OK: 54 files at their sha256 under the ..."), in `session/harness.txt` and `session/session.log`, as in sitting 1's and
E197's committed data; they are kept as collected. The round's path classes also match the device layer's address-format lines (the base
addresses of the card's on-chip memory in each format) in `run/stderr.txt`, `run/sampler.err` and the config and die-gate reads' stderr:
the card's own printout, as in sitting 1's, E194's and E197's committed data, not a desk path.

## Reduced (not here)

Step 13 (`rb/s24_reduce_e200.sh 2`: E200's registered reduction `reduce_e200.py`, sha256 10a44034..., unchanged, never `--prediction`,
then the kit's checker) runs on both sittings' committed directories only after this one is committed: the pooled reduction
`regfile-e200.json`, E200's registered result (sitting 1's own `regfile-e200-s1.json` stays beside it), and `checks-e200-2.json`; a later
lane commits them beside the data in a dated note, which fills this section.

## Re-make it

From the top of the repository, nothing here opens a device; set D1 and D2 to the two sittings' directories and R to an empty folder
outside the repository (the first line), then run the rest as they stand (the pooled reduction of both sittings):

    D1=docs/reports/data/2026-11-16-e200-regfile-sitting-1-aifoundry2; D2=docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2; R=$(mktemp -d)
    (cd "$D1" && shasum -a 256 -c SHA256SUMS) && (cd "$D2" && shasum -a 256 -c SHA256SUMS)
    for k in 1 2; do D=$(eval echo \$D$k); mkdir -p "$R/sitting-$k" && cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$R/sitting-$k/" && gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/sitting-$k/telemetry.jsonl"; if [ -f "$D/run/STOP" ]; then cp "$D/run/STOP" "$R/sitting-$k/"; fi; for p in runs.jsonl marks.jsonl telemetry.jsonl; do [ "$(awk -v p="./run/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/sitting-$k/$p" | cut -d' ' -f1)" ] && echo "sitting $k run/$p: the box's bytes" || echo "sitting $k run/$p: not the box's bytes"; done; done
    /usr/bin/python3 -I -B tools/claims-v3/e200/reduce_e200.py "$R/sitting-1" "$R/sitting-2" --out "$R/regfile-e200.json"
    /usr/bin/python3 -I -B tools/claims-v3/e200/check_e200.py checks "$R/regfile-e200.json" --out "$R/checks.json"

They check every entry of both `SHA256SUMS`; unpack each sitting's telemetry and set it, `run/runs.jsonl` and `run/marks.jsonl` against
that sitting's own manifest (`session/MANIFEST.sha256`: every line must say "the box's bytes"); run E200's registered reduction
(`reduce_e200.py`, unchanged, never `--prediction`: it loads E197's reducer by path and sha256 and applies C1 and C2) on both sittings;
and read E197.md 8's rows with the kit's checker, the clock row by C1 with its tallies. Neither sitting has a `run/STOP` (no stop fired).

## Labels

Measured: every number in Results and in the "happened" column, from this sitting's own files and the runbook's log. Registered: the
protocol (E197.md by reference), W1 and C1-C3, the caps, the stops, the die gate, the reduction (E200.md). Desk checks of code: the kit's
tests (KIT.md). Desk reads of the measured records: the run order (this lane's reading of `run/marks.jsonl` against E197's
`desk/dry-e197-ext.txt`) and the die in the idle spans (`run/marks.jsonl`'s idle spans against `run/telemetry.jsonl.gz`). Not blind to:
E200.md 16's list, E197's data and E200's sitting 1 (note 14). Interpreter: the desk's `/usr/bin/python3` 3.12.3 on aifoundry2.
