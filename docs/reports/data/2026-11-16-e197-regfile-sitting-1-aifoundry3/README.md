# E197 sitting 1, 2026-11-16, aifoundry3 card 0 at 600 MHz as found: RAN WHOLE (4 of 4 blocks) - the smoke and 13 trains in 400 processes, 43.28 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST, Q191's card lane `card-e197`, orchestrated from aifoundry2. The model session's proposal X02 (request
1113-x02-regfile revision 3: 13 A B B A trains of register-only scalar kinds at equal issue, pricing the scalar register file's parts: a
stored bit, a result bit, a write, a destination switch, and the read-port and read-field bits), registered as E197 (`ea4b4ad7`,
[`E197.md`](../../../../tools/claims-v3/e197/E197.md)) with its forecast sealed by sha256 (`e8e1746e...`; contents sealed), kitted
(`2c68a633`, [`KIT.md`](../../../../tools/claims-v3/e197/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e197/CARD-LANE-BRIEF.md)),
verified (verify-e197: DOES NOT HOLD; fix-e197: FIXED, with the redaction R1; verify2-e197: HOLDS WITH FIXES; fix2-e197: FIXED), landed
(land-e197) and readiness-checked (ready-e197: READY WITH GAPS), all before any E197 datum; no E197 file changed since the kit (step 0:
63 of 63 anchor lines as stated at HEAD `4bc7a07a` = GitHub main; steps 2 and 11: HISTORY OK). Run on the owner's go of his standing words
of Sun 15 Nov 2026 (10:05:42, 10:22:36, 17:21:16 PST), his "Try again" and his words of 21:51:09 PST, with G = this lane's booking of
aifoundry3 at 05:25:46 PST Mon 16 Nov 2026 (departures 1-3). Sitting 1: blocks A, B, C and D, the full plan. Nothing was set on the card.*

**The freeze line:** the model session's sealed forecast is known to the lab only by its sha256,
`e8e1746ea412dc0a7692408d54429500fd95db6b5015b2aef583e255242dba14` (E197.md section 0). **No forecast number and no score are in this
directory:** the model session scores its sealed forecast privately, after this commit. The reduced prices are not here (section
"Reduced" below).

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-9 set by his go, the kit and the round's plan before the session; 10-12 read after the collection, said so)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** Standing: **10:05:42** "continue, all machines are up"; **10:22:36** "don't
   worry about discord post, just use the machines, nobody is using them" (E197.md 12 reads his standing words as the go for E197 once
   registered, kitted, verified and readiness-checked, with its registered items as its defaults); **17:21:16** "Feel free to use more
   cards in parallel, I don't need to reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only
   1 card is being used, feel free to use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known);
   and "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before
   21:51:09). Beside them, a report of his words (not his own text), the round's Discussion at 19:34:12: "The aifoundry cards are all free
   right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free to use them." **His words
   name no experiment: the registered items are taken as their defaults** (E197.md 12): aifoundry3 card 0, 600 MHz as found, reads only,
   nothing set; sitting 1 about 45 card-minutes, cap 50; the 40-minute rests; one session of ours on aifoundry3; the window of E197.md 12.
2. **The card day: Mon 16 Nov 2026**, moved from Sunday by the round's weekly-usage-limit stop at about 18:05 PST Sun 15 Nov (E197 had not
   been booked and had sent nothing to any card then).
3. **G = the booking:** the card lane's `book.sh take aifoundry3 card-e197` printed BOOKED at **05:25:46 PST** Mon 16 Nov: last start
   G+1:30 and last end G+3:00 (E197.md 12, as the readiness lane's go lines define G), each rounded up to the whole minute: **06:56 and
   08:26 PST** (`s02_window_e197.sh 1 2026-11-16 06:56 08:26`, written by step 1 at 05:26:14; the window file's `RB_GO_EPOCH`, 1794835574 =
   05:26:14 PST, is the moment step 1 wrote it, not his go). The round's generic outer bound (G+3:30, 08:56) was not used: the registered,
   narrower last end binds. The sitting's first card command came at 05:27:28 (before the last start) and its end at 06:10:45 (before the
   last end).
4. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other
   etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE at 05:26:39), step 7's reads (et-who
   clean at 05:27:28), the session's own holder check and card lock, and `timeout 10` (no `-k`) on every device process.
5. **The host's package counter: not read** (his words do not name it): no E197 step, option or code reads it.
6. **A fresh network-access approval: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry3
   by the kit's ssh without a login link. The kit's login-link stop stayed live; no step met a login link (the round's file of checks held
   70 lines before and after every step).
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3; the box's interpreter was
   Python 3.12.3 (the build record's line). The orchestrating session is the round's session on its yvb3 Claude account, which took the
   round over on Sat 14 Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov.
8. **The rest and the order of the day's lanes.** The previous session of ours on aifoundry3 was E196's (session end 04:43:48 PST, data
   `4bc7a07a`). E197's rest rule, read on the box at step 7 (05:27:28) and again at step 9 (05:27:33), printed "rest: 43 minutes since
   E196's session end (2026-11-16 04:43:48 PST; dry sessions and blocks that opened no device skipped)" (40 required). The lane waited for
   the rest to open (05:23:48) before it booked; step 7's configuration read at 05:27:28 was the sitting's first card command.
9. **Departure D1 (E197.md 15, registered before any datum):** the lab's runner (`tools/claims-v3/e197/lab/run_trains.py`, its diff in
   `lab/run_trains-D1.diff`) runs every device process under `timeout 10`, never `-k 1`: no device process is ever killed. None outlived its
   TERM (the kit's hang watch recorded no HUNG line).
10. **The kernel file (reported, never a gate; E197.md 17.5):** the box's build of the kernel ELF has a file sha256 different from the desk
    build's (`a950ea13...` on the box); its `.text` (12,696 B, sha256 `ce8c93c6...`) is the desk build's. The host's kind table was the
    registration's byte for byte (34 kinds), and the dry pass listed the full plan SAME (474 lines, 429 device calls).
11. **"Reads only" is the management node's** (a lab-wide correction of Mon 16 Nov 2026, 01:4x PST, for the next records round): every
    runtime creation sends the ops node's abort on every submission queue of the card it opens, and the firmware aborts what is pending
    there; harmless with the card held alone (et-who empty, the card lock held), as here. Nothing changes in the kit.
12. **The sealed forecast's text (E197's R1):** the registration's copy of the proposal's `request.md` withholds lines 207-237 in a marked
    redaction and registers the received file by its sha256; the model session had not answered whether those lines are the sealed
    forecast by this sitting. No line of this directory quotes them.

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command (step 7's config read, 05:27:28) to "session end" (06:10:45) | 43.28 (cap 50; the registered estimate about 45) | measured (the session's clock) |
| train blocks begun and complete | started 4 of 4 (A B C D); complete 4 (A B C D) | measured |
| train processes recorded (of the plan's 400) and launch records | 400; 5,427 (35 in the smoke; A 2,024, B 1,426, C 1,088, D 854) | measured |
| how the sitting ended | "stop: none"; "SITTING-RESULT: smoke passed; train blocks complete 4 (A B C D); card stop none"; run_session.sh rc 0; wrapper rc 0 | measured |
| the runner's smoke gate and the kit's smoke check | "the runner's smoke gate: passed (26 launches, rates 523890000000.0-524230000000.0)"; "the kit's smoke check: passed (every smoke launch ok, check_bad 0, 1024 participants; every smoke device process exit 0)" (05:28:13) | measured |
| the deadline (a train skipped or cut) | none: the session ended at 06:10:45, before the runner's deadline (about 06:15:28) and the end-stop (06:16:58) | measured |
| a device process that outlived its timeout's TERM (the kit's hang watch) | none (the watch's closing record lists no hung process) | measured |
| device processes and their exits | 429 (27 anchors, 402 train processes: 2 in the smoke, 400 in blocks A-D), every one exit 0; 5,427 of 5,427 launch records ok, check_bad 0, 1,024 participants | measured |
| the run order | the 429 device processes in the dry listing's order (each train's F kind, S kind and orientation; each anchor's kind): 0 mismatches against the kit's committed full-plan listing | desk check of the measured records |
| telemetry samples, and those not at 600 MHz | 25,930 (05:27:29-06:10:44) / 0 | measured |
| board power, peak; die, peak (minshire[0]) | 29.74 W (05:38:16); 55 C (first at 05:34:40; 4,750 samples at 55 C) | measured |
| the sampler | the plain sampler, `ettelem sample --seconds <SAMPLER_S> --every-ms 100` (SAMPLER_S = CAP_S + 600; CAP_S 2,939 s this sitting), through E128's guard | registered (E197.md 4) |

## Registered against happened

| registered (E197.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set (E197.md 3) | step 7's config read: TDP 0 W, threshold 65 C, power state max_power, 600 MHz, 523 mV (05:27:28); 25,930 of 25,930 samples at 600 MHz; nothing set |
| the 40-minute rest before the sitting's first card command (E197.md 6) | "rest: 43 minutes since E196's session end (2026-11-16 04:43:48 PST; ...)" (step 7, 05:27:28; step 9 read it again at 05:27:33) |
| the first card command: step 7's config read (KIT.md 4) | 1794835648 = 05:27:28 PST (the runbook's `e197-1-first.txt`; `session/first-card-command.txt`) |
| the plan (sitting 1: full unless the window cannot hold it) | full (logged by step 7 before the first card command) |
| the smoke and its gate (the runner's), the kit's smoke check | both passed (Results) |
| the blocks, trains, processes and orientations in trains.tsv's order (E197.md 5) | the dry pass on the box: "LISTING SAME full: 474 lines, 429 device calls"; the run: 429 device processes in that order (desk check), 400 train processes over 13 trains (T1-T6, T8-T13, T15) |
| the cap: 50 card-minutes from the first card command; the runner's deadline at the first card command + the cap - 120 s; the end-stop at the cap - 30 s | "the cap 3000 s, at 06:17:28 PST; CAP_S 2939 s, the runner's deadline at about 06:15:28 PST; the end-stop at 06:16:58 PST"; no train skipped or cut; the end-stop did not fire; 43.28 card-minutes used |
| the stops (E197.md 9: the proposal's, the runner's, the kit's) | none fired ("stop: none"); peaks 29.74 W and 55 C, under the 65 W and 70 C stops and inside E197.md 9's desk estimate (about 30 W, under 35 W; the die under 56 C) |
| departure D1: `timeout 10`, never a KILL | every device process under `timeout 10` (`ref/run_trains.py`); no HUNG line |
| one session of ours on aifoundry3; the card exclusive | k6's look FREE before (05:26:39) and after (06:11:04) the session; et-who clean at step 7 |
| the window (E197.md 12) | G 05:25:46; first card command 05:27:28 (last start 06:56); session end 06:10:45 (last end 08:26) |

## Device commands sent

READs only: step 7's `ettelem config` (five READs) and the session's one `ettelem sample --every-ms 100` (six READs a sample), both
through E128's guard (dmcmd_audit GO, KIT.md 6); the host opened the ops node only (and each runtime creation sent the ops node's abort on
the card's queues: note 11); `et-who --check` sends no device command. No set, no reset, no statistics reset, no firmware query, no KILL
to any process.

## Files

| path | what |
|---|---|
| `session/` | the wrapper's files: session.log, first-card-command.txt, harness.txt, preflight.txt, run_session.out, watch.jsonl, watch.out, summary.txt, MANIFEST.sha256 (the box's), wrapper.rc |
| `ref/` | the four registered files the session ran, byte for byte (run_session.sh, stopwatch.py, trains.tsv; the lab's run_trains.py, D1) |
| `run/` | the reference session's own files: runs.jsonl, marks.jsonl, stderr.txt, session.log, sampler.err, stopwatch.err, SESSION_DONE, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's) |
| `facts-e197-1.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it (this README is not in it) |

The public-text scan before this commit read two hits in the collected files, both the harness line's word for the kit's folder on
the box ("HARNESS OK: 45 files at their sha256 under the ..."), in `session/harness.txt` and `session/session.log`, as in E193's and
E195's committed data; they are kept as collected. The round's path classes also match the device layer's address-format lines in
`run/stderr.txt` and `run/sampler.err`: the card's own printout, not a desk path.

## Reduced (not here)

Step 13 (`rb/s24_reduce_e197.sh 1`: the registered reducer `proposal/src/reduce_regfile.py`, sha256 f325bd0e..., unchanged, never
`--prediction`, then the kit's checker) runs on this directory only after it is committed; its outputs (`regfile-e197-s1.json`,
`checks-e197-1.json`) are committed beside it by a later lane in a dated note, which fills this section. If a second sitting runs, its
step 13 pools both sittings (E197.md 6).

## Re-make it

From the top of the repository, nothing here opens a device (R is an empty folder outside the repository):

    D=docs/reports/data/2026-11-16-e197-regfile-sitting-1-aifoundry3; R=$(mktemp -d)
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/sitting-1" && cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$R/sitting-1/" && gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/sitting-1/telemetry.jsonl"
    if [ -f "$D/run/STOP" ]; then cp "$D/run/STOP" "$R/sitting-1/"; fi
    for p in runs.jsonl marks.jsonl telemetry.jsonl; do [ "$(awk -v p="./run/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/sitting-1/$p" | cut -d' ' -f1)" ] && echo "run/$p: the box's bytes" || echo "run/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e197/proposal/src/reduce_regfile.py "$R/sitting-1" --out "$R/regfile-e197-s1.json"
    /usr/bin/python3 -I -B tools/claims-v3/e197/check_e197.py checks "$R/regfile-e197-s1.json" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the telemetry and set it, `run/runs.jsonl` and `run/marks.jsonl` against the box's own
manifest (`session/MANIFEST.sha256`: every line must say "the box's bytes"); run the registered reducer (unchanged, never `--prediction`);
and read E197.md 8's rows with the kit's checker. This sitting has no `run/STOP` (no stop fired).

## Labels

Measured: every number in Results and in the "happened" column, from this sitting's own files and the runbook's log. Registered: the
kinds, the trains, the protocol, the caps, the stops, the reduction (E197.md). Desk checks of code: the kit's tests (KIT.md). Desk check
of the measured records: the run order line (this lane's reading of `run/marks.jsonl` against `desk/dry-e197-full.txt`). Not blind to:
E197.md 13's list. Interpreter: the desk's `/usr/bin/python3` 3.12.3 on aifoundry2.
