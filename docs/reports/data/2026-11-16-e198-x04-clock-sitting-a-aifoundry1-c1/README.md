# E198 sitting A, 2026-11-16, aifoundry1 card 1 at 600 MHz as found: RAN WHOLE - all 9 registered passes (pass 0 the warm-up) of blocks S, D, W and T in one session of 43.30 card-minutes, reads only, no stop, the smoke gate GO, every device process exit 0 under a plain `timeout 10` (amendment A1: nothing killed); the registered reducer runs after this commit

*Mon 16 Nov 2026 (week 46), PST. Card lane `card-e198b` (round Q196), orchestrated from aifoundry2. The model session's proposal X04
(request 1113-x04-clock revision 2) on aifoundry1 card 1, registered as E198 in `62b102fe` ([`E198.md`](../../../../tools/claims-v3/e198/E198.md))
with its two freeze lines: forecast 1, the lab's, `forecast-e198.json` sha256 524f49ad661a419f... (E193's committed aifoundry3 prices,
frozen before any card-1 datum); forecast 2, the model session's sealed aifoundry1 card-1 forecast, sha256 7de55c4fcc199ced... (posted
22:56:05 PST Sun 15 Nov 2026; its contents sealed, scored by the model session, never in a lab file). Amended by A1 in `9e59ca0d`
([`E198.md.dated-amendment-A1.md`](../../../../tools/claims-v3/e198/E198.md.dated-amendment-A1.md): the lab's runner copy
`run_x04_e198a1.py`, every device process under a plain `timeout 10`, never a KILL). Kitted in `82532e71`
([`KIT.md`](../../../../tools/claims-v3/e198/KIT.md); A1's kit note in `9e59ca0d`). Verified: `verify-e198` HOLDS WITH FIXES, fixed by
`fix-e198` before the land; A1 `verify-a1e198` HOLDS WITH FIXES, fixed by `fix-a1e198` before the land. Readiness-checked by `ready-e198b`:
READY WITH GAPS (its go lines replace `ready-e198`'s, void since A1). Run on the owner's standing go of Sun 15 Nov 2026 (Departures 1).
Sitting A: blocks S, D, W, T. Nothing was set on the card. **E198 is not blind to E193's data:** E193's reduced prices are its forecast 1.
It is blind to every card-1 X04 reading: these are the first. **The forecasts stay sealed:** no number of forecast 2 is here, and nothing
here scores E198 against either forecast.*

*Departures, dated Mon 16 Nov 2026 and set before the session (in full under Departures below): E198's registered items run as their
defaults on the owner's standing words of Sun 15 Nov 2026; amendment A1 (the runner's kill path removed, by the orchestrator's HOLD of
02:56:14 PST); the card day Mon 16 Nov 2026, the day of the booking; G = the booking, 07:22:33 PST (last start 08:53, last end 10:53); the
post waived by his words of 10:22:36 PST; the host's package counter not read; the desk aifoundry2 under `/usr/bin/python3` 3.12.3; the
orchestrating session the round's session on its yvb3 Claude account.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E198.md, A1, the kit). The pass spans, peak times, clock counts and the order check below are **desk arithmetic of the
measured records** (`x04/runs.jsonl`, `x04/run.log`, the two `telemetry.jsonl.gz`), not prices and not checks: the prices are the registered
reducer's (`tools/claims-v3/e193/proposal/src/reduce_x04.py`, sha256 98bbc174..., unchanged) and E193.md section 8's nine checks are the
kit's checker's (`check_e193.py`), both run only on this directory once it is committed (`rb/s24_reduce_e198.sh A`); their outputs
(`x04-e198-A.json`, `checks-e198-A.json`) and the transport scorer's are committed by a later lane. The desk steps ran under
`/usr/bin/python3` 3.12.3 on aifoundry2.

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command to "session end" | **43.30** (07:24:46 to 08:08:04 PST, 2,598 s; cap 60) | measured (the session's clock) |
| device processes of the main run, by exit status | **234, every one exit 0** | measured |
| passes run (pass 0 the registered warm-up, set aside by the reduction) | **9 of 9** (passes 0-8, 26 runs each): **8 measured passes** | measured |
| launches, and how many were ok | **2,808 / 2,808** | measured (the host's X04 lines) |
| how the main run ended | **no stop: done**; the session's line "main run end: runner rc 0, every pass (no stop: done)" at 08:08:04 PST; session.rc 0 | measured |
| the smoke (10 device processes, --blocks S,D,W,T,C) and its gate | "SMOKE GO: 10 of 10 device processes exit 0 as registered, 57 launches all ok, the train 12 of 12 (3 a segment); telemetry 1040 samples, every one at 600 MHz, board max 39.37 W, die max 54 C (below every stop)" (07:26:41 PST) | measured |
| telemetry samples of the main run, and those not at 600 MHz | **24,792 / 0** (07:26:41-08:08:03 PST; every sample with the board, the die and the clock) | measured |
| board power, peak; die, peak (minshire[0]) | **39.86 W** (07:35:13 PST; lowest 29.63 W); **55 C** (07:35:13; lowest 52 C) | measured |
| idle-down waits; card waits; short trains; incomplete launches | **0; 0; 0; 0** | measured |
| A1: device processes ended by their timeout's TERM (exit 124); device processes NOT ENDED (the runner's `device_not_ended` events; reported, never killed) | **0; 0** | measured |
| the start and closing config reads | TDP 65 W, threshold 65 C, power state managed_power, minion 600 MHz, 499 mV at the start (07:24:46 PST); **the same at the close** (08:08:04) | measured (READ) |

| block | span (PST, first launch to last) | runs | launches |
|---|---|---|---|
| the smoke (its telemetry 07:24:57-07:26:41) | 07:25:22-07:26:33 | 10 | 57 |
| pass 0 (the warm-up) | 07:27:06-07:31:07 | 26 | 312 |
| pass 1 | 07:31:42-07:35:43 | 26 | 312 |
| pass 2 | 07:36:19-07:40:19 | 26 | 312 |
| pass 3 | 07:40:55-07:44:55 | 26 | 312 |
| pass 4 | 07:45:31-07:49:31 | 26 | 312 |
| pass 5 | 07:50:07-07:54:07 | 26 | 312 |
| pass 6 | 07:54:43-07:58:43 | 26 | 312 |
| pass 7 | 07:59:19-08:03:19 | 26 | 312 |
| pass 8 | 08:03:55-08:07:55 | 26 | 312 |

- **The idle references** (the median die reading of the 20 s of telemetry before each runner call's first run, the idle-down rule's base):
  52 C for the smoke and 52 C for the main run, 200 samples each (`events.jsonl`). No idle-down wait was logged.
- **The clock: 600 MHz in 24,792 of 24,792 main-run samples and 1,040 of 1,040 smoke samples.** The minion rail read 499 mV in every
  sample of both runner calls.
- **The smoke's peaks:** board 39.37 W (07:26:25 PST; lowest 29.35 W), die 54 C (lowest 52 C).
- **Against the registered predicted peaks** (E198.md 9: die 53 C, board 41.65 W; the stops 70 C and 65 W): the board peak 39.86 W is
  1.79 W under its prediction; the die peak 55 C is 2 C over it (desk arithmetic). The die rose 3 C over the main run's idle reference
  (52 to 55 C), the rise E198.md 9 took from E193; the idle reference read 2 C above the 50 C that prediction assumed. Margins to the stops:
  25.14 W and 15 C. No stop fired.

## Registered against happened

| registered (E198.md, A1, KIT.md) | happened |
|---|---|
| aifoundry1 card 1, 600 MHz as found, nothing set (E198.md 3) | card 1 alone (`--device 1`, ET_DEVICES=1, card 1's lock `/run/lock/etsoc-shire1.lock`); 600 MHz in every sample of both runner calls; the config reads at the start and the close of the session (and the runbook's step 7 read at 07:24:12 PST): TDP 65 W / 65 C / 600 MHz / 499 mV, as the card holds it; nothing set; nothing opened on card 0 |
| A1: the lab's runner copy (run_x04_e198a1.py, sha256 5b2307eb...), every device process under a plain `timeout 10`, no KILL sent by any process of the sitting (E198.md.dated-amendment-A1.md) | `session/hashes.txt`'s runner line: `5b2307ebab4c1b359f9163a0c2bdb8c8a0a0359f39a8d0c766b47dfa22805780`; every device process exit 0 (no 124, no not-ended); the session log has no "A DEVICE PROCESS DID NOT END" line; the dry pass and the build's listings: every device call under a plain `timeout 10`, no `timeout -k` |
| the 40-minute rest before the sitting (E198.md 11) | step 9's line: "rest: 162 minutes since E199's session end (2026-11-16 04:42:32 PST; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry1 read)"; the rest opened 05:22:32 PST, before step 7's config read (07:24:12) and the session's first card command (07:24:46) |
| the smoke with --blocks S,D,W,T,C and the kit's gate (E198.md 2) | the gate's line: SMOKE GO (07:26:41 PST, Results) |
| 9 passes, the seeded order (E198.md 2) | 9 of 9 passes, 26 runs each; the 234 calls as run (block and arm, in `x04/run.log`) equal the 234 of the kit's dry listing `tools/claims-v3/e198/desk/dry-e198a1-A.txt`, call for call (a desk check of the measured log); the session's own dry pass on the box (step 8, 07:24:18) listed SAME |
| the cap: 60 card-minutes; the runner's deadline = first card command + cap - 120 s, never past the window's last end - 180 s | the deadline line: 08:22:46 PST (epoch 1794846166 = the first card command + 3,480 s; the window's last end - 180 s, 10:50:00, is later); it never fired: the main run ended at 08:08:04, 14 min 42 s before it; 43.30 card-minutes against the cap of 60 |
| the stops (E198.md 9, in A1's form) | none fired: board peak 39.86 W (the stop: above 65 W on three samples in a row); die peak 55 C (the stop: 70 C); every sample at 600 MHz; the telemetry file grew throughout; every device process exit 0 (no exit 1, 3 or 124, none still running at 25 s); no card wait; no stop file; the deadline not reached |
| the one sampler a runner call, through E191's guard (E198.md 3; the A1 form says "E128's guard", E193's wording); no statistics reset | two runner calls, the smoke and the main run, one sampler each: the box's `build/ettelem/ettelem` (sha256 8008f96f...) through E191's guard (6fd26f51...), `--every-ms 100`, no `--reset-ms`; the session's preflight `dmcmd_audit: GO (19 send site(s), 0 disallowed; allow-list: none)` |
| per-sensor codes not recorded (E198.md 2, by E193.md 4) | not recorded |
| the post-launch credit barrier on the card's build | UNCONFIRMED (E193.md 14; the kit found no worker firmware source to read) |
| the build on aifoundry1, at most two starts a Pacific day; THE KERNEL GATE (E198.md 13) | one start, 07:23:33-07:23:36 PST on the box: X04-BUILT rc=0 by `build_e198a1.sh` under a plain `timeout 900`; the kernel's `.text` `fd720727...` (68,358 B) is E193's registered one (the gate); the kernel ELF `01a37767...` is E193's desk build's and differs from request.md's (reported, never a gate); BODIES CHECK PASS; HOST-BEHAVIOUR OK (three refusals before the device layer); LISTING SAME x3 (10, 234 and 135 device calls); the host `a4bd858c...`; cmake 3.28.3, riscv64-unknown-elf-gcc () 15.1.0, c++ 13.3.0, the box's Python 3.12.3, 0 build warnings |
| the dry pass: the session's own wrapper with DRY=1 (KIT.md, A1's step 8) | "E198-DRY sitting A rc=0 smoke=0 main=0 calls=10+234 manifest=written", both listings SAME (07:24:18 PST) |
| the harness | HARNESS OK on the box (51 files at their sha256 in E198's folder there, 3 of them executable), in the session's own log and at steps 5 and 6 |
| the window (E198.md 12) | G = the booking 07:22:33 PST; last start 08:53, last end 10:53 PST (Departures 4); launched 07:24:51 PST (T0 07:24:46), ended 08:08:04 |
| one session of ours on aifoundry1 at a time; nothing on card 0 (E198.md 11) | the round's booking of aifoundry1 held by this lane from 07:22:33 PST; the session's holder check found no process of ours or of another user on either card; the private /dev held card 1's two nodes only |
| the host's package counter | not read |
| the post | waived by the owner (Departures 5) |

## Departures, dated

*Mon 16 Nov 2026, PST. Items 1-10 were set by his go, the round's brief and E198's go lines (`ready-e198b`) before the session; item 11
was read at the collection. All were written here after the collection and before the reducer ran.*

1. **The go.** His standing words of Sun 15 Nov 2026, verbatim:
   - "continue, all machines are up" (10:05:42 PST);
   - "don't worry about discord post, just use the machines, nobody is using them" (10:22:36);
   - "Feel free to use more cards in parallel, I don't need to reserve them ..., feel free to use more in parallel" (17:21:16);
   - "Try again" (received at or before 21:28:59, after the account's usage-limit stop);
   - "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before
     21:51:09);
   - "Make sure to incorporate suggestions from Fable when planning experiments" (received between 21:55 and 22:07:09; it binds the
     planning of experiments and changes nothing E198 registers).

   Beside them stands the round's coordination thread, #2.5.1 (19:34:12 PST): the model session's report of his words, "The aifoundry cards
   are all free right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free to use them."
   His words name no experiment, so **E198's registered items stand as its defaults**, with A1.
2. **Amendment A1** (`9e59ca0d`, pushed 06:26:25 PST, before any E198 datum): the runner's kill path removed. The orchestrator's HOLD of
   02:56:14 PST stopped E198 until "a dated amendment (A1) gives the lab's runner copy 'timeout 10' without -k and an end_device() that never
   sends SIGKILL ..., verified, landed and re-readied": E193's registered runner wrapped every device process in `timeout -k 1 10`, and the
   lab never kills a device process (`AGENT.md`: "Stop tools with Ctrl-C or a plain `kill`, never `kill -9`"). A1 was verified, fixed
   before the land, landed and readiness-checked; this sitting ran the lab's copy, which differs from E193's runner only in that kill path.
3. **The card day: Mon 16 Nov 2026**, the day of the booking. It moved from Sunday because the account's weekly usage limit stopped the
   round at about 18:05 PST Sun 15 Nov.
4. **G = the booking: 07:22:33 PST**, when this lane took the round's booking of aifoundry1 (`book.sh take aifoundry1 card-e198b`, after
   E199's queue read QUEUE OVER and its rest had opened). The window, by E198.md 12: last start 08:53, last end 10:53 PST, rounded up, inside
   G's Pacific day (G at 20:29:00 or earlier: yes); step 1 wrote it at 07:23:02. One booking serves both sittings: sitting B's G is this
   sitting's end plus 40 minutes, 08:48:04 PST.
5. **The post: waived.** "the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST". No claim, no release.
6. **The host's package counter: not read.** No E198 or E193 file names it (git grep at HEAD `8aa6185e` for rapl, powercap or energy_uj, any
   case: 0 files).
7. **No network-access approval to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry1 without that
   check. The kit's login-link stop stayed live, and no step met a login link: the round's lock file of such checks read 70 lines before and
   after every step.
8. **The desk and the session.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3. The orchestrating session is
   the round's session on its yvb3 Claude account.
9. **The order on aifoundry1.** The round's plan put E198 before E199. The HOLD (item 2) sent E199 first; E199's session ended 04:42:32 PST,
   so E198's rest opened at 05:22:32 (step 9's line above).
10. **The sealed card-1 forecast** is E198.md's freeze line 2: sha256 7de55c4f..., posted as #2.5.1.2.1 at 22:56:05 PST Sun 15 Nov 2026 and
    registered before the land. The round's list of sealed card-1 forecasts held no other E198 line (read 07:18:11 PST); no dated note was
    needed or made, and step 2 read "the sealed card-1 note: none". It stays sealed: no number of it is in this directory or any lab file.
11. **Notes, not departures.**
    - The die peak, 55 C, is 2 C above E198.md 9's predicted 53 C (Results); a prediction, not a stop or a rule.
    - Step 10's wait found the session by A1's real script name (`session_e198a1\.sh`); five calls, running at each of the first four, the
      fifth at 08:08:20 with the box's manifest written (296 files).

## Device commands sent

READs only: the session's start and closing `ettelem config` and each runner call's `ettelem sample --every-ms 100`, all through E191's
guard (dmcmd_audit GO, KIT.md section 6), plus the identity read's sampler (THE IDENTITY GATE (b)) and the runbook's step 7 config read; the
host opened card 1's ops node only; `et-who --check` sends no device command. No set, no reset, no statistics reset, no firmware query,
nothing to card 0. With ET_DEVICES=1 and the private /dev, the device layer opened card 1 alone (the 244 runtime lines below), so its
runtime creation's stock abort of pending work on the submission queues (the lab-wide note of Mon 16 Nov 2026) reached card 1's queues only,
on a card held by this session alone.

## Files

| path | what |
|---|---|
| `session/` | session.log, the two config reads (`.json`, `.raw`, `.err`), the identity reads (`ident-a.txt`, `ident-b.txt`, `ident-end.txt`, `ident/`), the holder check's output, the private /dev's listing, the warden (`holderd/`, `warden.out`), the first card command's time, the binaries' hashes, the harness, tree and preflight outputs, the smoke's runner output and gate, the main runner's output, MANIFEST.sha256 (the box's), session.rc |
| `smoke/`, `x04/` | each runner call's run.log, events.jsonl, runs.jsonl, device-stdout.txt, device-stderr.txt, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's), hostraw.txt.gz and hostraw-index.jsonl (every device process's raw standard output, packed) |
| `facts-e198-a.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-16-e198-x04-clock-sitting-a-aifoundry1-c1; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    for p in runs.jsonl telemetry.jsonl; do [ "$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/x04/$p" | cut -d' ' -f1)" ] && echo "x04/$p: the box's bytes" || echo "x04/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04.json"
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04.json" "$R/x04" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the main run's telemetry and set it and `x04/runs.jsonl` against the box's own manifest
(`session/MANIFEST.sha256`: both lines must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_x04.py`, sha256
98bbc174..., unchanged, no `--pvt`, no `--keep-warmup`); and read E193.md 8's nine checks with the kit's checker. Step 13
(`rb/s24_reduce_e198.sh A`) does the same from a runbook directory whose window names the day of the sitting.

## What E198's README adds to E193's form

- **The card and its gates:** aifoundry1 card 1 (`--device 1`, ET_DEVICES=1 for every device process, card 1's lock). **THE PRIVATE /dev:**
  "the private /dev (privdev_e198.sh, a listing inside it, nothing opened): card nodes inside [et1_mgmt et1_ops], 16 entries; the box's real
  /run/lock, /proc and /sys" (07:24:46). **THE IDENTITY GATE (a):** "IDENT-A OK: TDP 65 W, 65 C, minion 600 MHz as found; PCIe target
  /dev/et1_mgmt and physical device ID 1 on its stderr; minion_mv within (450, 510)"; the closing read the same (`session/ident-end.txt`).
  **THE IDENTITY GATE (b)** (07:24:56, with the sampler running): OK; ours on card 1's management node 1, ours on card 1 1, ours on card 0
  0, ours elsewhere 0, another login's on card 1 0, on card 0 0; the holder check from inside the private /dev saw the same line as the
  box's own et-who outside it. **The warden** (`session/holderd/summary.json`): 42 holder checks served from inside; 247 processes of the
  sitting held a card node, every one card 1's (`/dev/et1_mgmt` 3, `/dev/et1_ops` 244; the programs `ettelem` and `x04clock_host`);
  **watch hits: none**; ended by its stop file.
- **The runtime line:** each runner call's `hostraw-index.jsonl` summed (`facts-e198-a.json`, "host_runtime_lines"): the smoke 10 device
  processes, 10 runtime lines dropped by the guard, 57 X04 lines; the main run 234 device processes, 234 runtime lines dropped, 2,808 X04
  lines; "x04_not_at_start" 0 and "opening_text_left" 0 in both; every runtime line names card 1 ("Opening device 1", 234 of 234 in the main
  run's `hostraw.txt.gz`). Re-make: unpack `hostraw.txt.gz`, split it at its "### <seq>.stdout <bytes>" headers, and `dropruntime_e198.py`'s
  drop_runtime gives each process's stream as the runner read it.
- **The rests and the window:** G (the booking) 07:22:33 PST, last start 08:53, last end 10:53; the rest before the sitting, step 9's line
  above (162 minutes since E199's session end); sitting B's G from this sitting's end plus 40 minutes, 08:48:04, under the same booking.
- **The scores** are not in this commit: step 13 (`rb/s24_reduce_e198.sh A`, then `score <A> [<B>]`) runs the registered reducer, E193's
  checker and E198's transport scorer after it; a records lane commits their outputs beside the data with a dated note.
- **The sealed card-1 forecasts:** E198.md's freeze line 2 (the model session's, sha256 `7de55c4f...`, posted 22:56:05 PST Sun 15 Nov
  2026, registered before the land); no later one (Departures 10). Named by its sha256 only; never scored in a lab file.

## The day's records

- **The steps' exits** (the card lane's runbook log; PST): the sealed card-1 step rc 0 (07:18:11); the booking and the round's quiet hold
  (07:22:33); the one-lab desk span 07:22:37-07:23:20; step 0, A1's anchor read, 72 of 72 as stated at LAB's HEAD `8aa6185e` = GitHub main,
  status 0 lines, the 1-minute load 0.76 (07:22:41-07:22:52); step 1 rc 0 (07:23:02); step 2 (A1) rc 0, "Already up to date", HEAD
  `8aa6185e701d`, the registration, the kit and A1 found by their content, nothing under `tools/claims-v3/e198` after A1's commit, HISTORY OK,
  the lists at their pinned counts and bytes, the runner copy re-made and equal, "E198 data paths in any ref: 0" (07:23:07-07:23:11); step 4
  FREE on both cards (07:23:20); step 5, 52 paths synced, HARNESS OK and TREE OK (07:23:28); step 6 start and one wait, rc 0 (07:23:33-07:23:45);
  step 7 rc 0 (07:24:12); step 8 start and one wait, rc 0 (07:24:17-07:24:25); step 9 rc 0, launched (07:24:45-07:24:51); step 10, five waits,
  the last rc 0 (08:08:20); the one-lab collect span from 08:08:43; step 11 rc 0, COLLECTED (08:08:43-08:08:46).
- **The copy:** one read-only copy back of the session's directory, **COPY-BACK EXACT** against the box's manifest
  (`session/MANIFEST.sha256`: 296 files at the box's sha256, nothing else but `session.rc`), packed into the 57 files `SHA256SUMS` lists.
- **Privacy:** the collector's scrub (the box's home as `~`, every holder line's user and our own box login as `<login>`: no home-folder path
  and no login left), the desk-path gate (CLEAN: 58 files read, 0 hits) and the history check (HISTORY OK) all passed; `facts-e198-a.json` is
  the collector's summary. `SHA256SUMS` (the collector's) pins every file but this README and itself.
- **The device-command audit** (`dmcmd_audit.py`, no allow-list, no exception): GO, 19 send sites, every one a READ, at step 2 on the desk,
  on the box after the build, and by the session's own preflight (`session/preflight.txt`).
- **The public-text scan** before this commit read every text file here, the text inside every `.gz` and this README, with the lab's
  sanitizer (its fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's
  classes over this README and the commit message. This README and the commit message: no sanitizer hit; the classes match only the
  owner's quoted word "discord" (Departures 1). Its four hits in the collected files are kept as collected: one counter value in
  `x04/hostraw.txt.gz`, an instruction-cache miss count of 8792 written after its key's colon, matched by a port pattern (a measured
  count, not a port); and three uses of one word, the
  kit's own name for E198's folder on the box (in the harness line, twice, and in the session log's line naming the box and its tree), matched
  by the sanitizer's privilege-word pattern (it names a folder, not an account's rights). The round's classes, read over the collected text
  files too, match only the device layer's own lines about the chip's on-die memory addressing (in the config reads' and the identity
  sampler's `.err` files and each runner call's `device-stderr.txt`: the hardware's word for that memory, which the class lists because a
  desk path of ours holds the same word; here it names no path) and the warden's request ids in `session/holderd/served.jsonl` (a process
  id and a nanosecond time, matched by the class for chat ids): kept as collected.

SPDX-License-Identifier: Apache-2.0
