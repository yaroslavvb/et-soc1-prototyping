# E198 sitting B, 2026-11-16, aifoundry1 card 1 at 600 MHz as found: RAN WHOLE - all 9 registered passes (pass 0 the warm-up) of block C in one session of 27.42 card-minutes, reads only, no stop, the smoke gate GO, every device process exit 0 under a plain `timeout 10` (amendment A1: nothing killed); the registered reducer runs after this commit

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
Sitting B: block C, after sitting A (`docs/reports/data/2026-11-16-e198-x04-clock-sitting-a-aifoundry1-c1/`,
committed `e8b4c0d7`) under the same booking. Nothing was set on the card. **E198 is not blind to E193's data:** E193's reduced prices are its forecast 1.
It is blind to every card-1 X04 reading: these are the first. **The forecasts stay sealed:** no number of forecast 2 is here, and nothing
here scores E198 against either forecast.*

*Departures, dated Mon 16 Nov 2026 and set before the session (in full under Departures below): E198's registered items run as their
defaults on the owner's standing words of Sun 15 Nov 2026; amendment A1 (the runner's kill path removed, by the orchestrator's HOLD of
02:56:14 PST); the card day Mon 16 Nov 2026, the day of the booking; one booking for both sittings, taken 07:22:33 PST; sitting B's G = sitting A's
session end + 40 minutes, 08:48:04 PST (last start 10:19, last end 12:19); the
post waived by his words of 10:22:36 PST; the host's package counter not read; the desk aifoundry2 under `/usr/bin/python3` 3.12.3; the
orchestrating session the round's session on its yvb3 Claude account.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E198.md, A1, the kit). The pass spans, peak times, clock counts and the order check below are **desk arithmetic of the
measured records** (`x04/runs.jsonl`, `x04/run.log`, the two `telemetry.jsonl.gz`), not prices and not checks: the prices are the registered
reducer's (`tools/claims-v3/e193/proposal/src/reduce_x04.py`, sha256 98bbc174..., unchanged) and E193.md section 8's nine checks are the
kit's checker's (`check_e193.py`), both run only on this directory once it is committed (`rb/s24_reduce_e198.sh B`); their outputs
(`x04-e198-B.json`, `checks-e198-B.json`) and the transport scorer's are committed by a later lane. The desk steps ran under
`/usr/bin/python3` 3.12.3 on aifoundry2.

## Results (measured: the session's own records; the reduced prices follow after the data commit)

| what | value | label |
|---|---|---|
| the sitting's card-minutes, first card command to "session end" | **27.42** (08:48:55 to 09:16:20 PST, 1,645 s; cap 50) | measured (the session's clock) |
| device processes of the main run, by exit status | **135, every one exit 0** | measured |
| passes run (pass 0 the registered warm-up, set aside by the reduction) | **9 of 9** (passes 0-8, 15 runs each): **8 measured passes** | measured |
| launches, and how many were ok | **1,350 / 1,350** | measured (the host's X04 lines) |
| how the main run ended | **no stop: done**; the session's line "main run end: runner rc 0, every pass (no stop: done)" at 09:16:20 PST; session.rc 0 | measured |
| the smoke (10 device processes, --blocks S,D,W,T,C) and its gate | "SMOKE GO: 10 of 10 device processes exit 0 as registered, 57 launches all ok, the train 12 of 12 (3 a segment); telemetry 1040 samples, every one at 600 MHz, board max 39.21 W, die max 53 C (below every stop)" (08:50:50 PST) | measured |
| telemetry samples of the main run, and those not at 600 MHz | **15,273 / 0** (08:50:51-09:16:20 PST; every sample with the board, the die and the clock) | measured |
| board power, peak; die, peak (minshire[0]) | **40.34 W** (09:14:33 PST; lowest 29.87 W); **55 C** (08:52:42; lowest 52 C) | measured |
| idle-down waits; card waits; short trains; incomplete launches | **4** (1.0, 1.0, 1.0 and 1.5 s, each logged at a die of 54 C, the idle reference + 2 C); **0; 0; 0** | measured |
| A1: device processes ended by their timeout's TERM (exit 124); device processes NOT ENDED (the runner's `device_not_ended` events; reported, never killed) | **0; 0** | measured |
| the start and closing config reads | TDP 65 W, threshold 65 C, power state managed_power, minion 600 MHz, 499 mV at the start (08:48:56 PST); **the same at the close** (09:16:20) | measured (READ) |

| block | span (PST, first launch to last) | runs | launches |
|---|---|---|---|
| the smoke (its telemetry 08:49:06-08:50:50) | 08:49:31-08:50:42 | 10 | 57 |
| pass 0 (the warm-up) | 08:51:16-08:53:30 | 15 | 150 |
| pass 1 | 08:54:05-08:56:21 | 15 | 150 |
| pass 2 | 08:56:56-08:59:12 | 15 | 150 |
| pass 3 | 08:59:47-09:02:02 | 15 | 150 |
| pass 4 | 09:02:37-09:04:52 | 15 | 150 |
| pass 5 | 09:05:27-09:07:41 | 15 | 150 |
| pass 6 | 09:08:17-09:10:30 | 15 | 150 |
| pass 7 | 09:11:06-09:13:20 | 15 | 150 |
| pass 8 | 09:13:55-09:16:12 | 15 | 150 |

- **The idle references** (the median die reading of the 20 s of telemetry before each runner call's first run, the idle-down rule's base):
  52 C for the smoke and 52 C for the main run, 200 samples each (`events.jsonl`). The main run logged four idle-down waits (`x04/events.jsonl`,
  kind `idle_down`: 1.0, 1.0, 1.0 and 1.5 s), the registered rule at work (a run waits, at most 30 s, until the die reads at most the idle
  reference + 2 C); none reached its bound.
- **The clock: 600 MHz in 15,273 of 15,273 main-run samples and 1,040 of 1,040 smoke samples.** The minion rail read 499 mV in every
  sample of both runner calls.
- **The smoke's peaks:** board 39.21 W (08:50:34 PST; lowest 29.77 W), die 53 C (lowest 52 C).
- **Against the registered predicted peaks** (E198.md 9: die 53 C, board 41.65 W; the stops 70 C and 65 W): the board peak 40.34 W is
  1.31 W under its prediction; the die peak 55 C is 2 C over it, as in sitting A (desk arithmetic). The die rose 3 C over the main run's idle
  reference (52 to 55 C). Margins to the stops: 24.66 W and 15 C. No stop fired.

## Registered against happened

| registered (E198.md, A1, KIT.md) | happened |
|---|---|
| aifoundry1 card 1, 600 MHz as found, nothing set (E198.md 3) | card 1 alone (`--device 1`, ET_DEVICES=1, card 1's lock `/run/lock/etsoc-shire1.lock`); 600 MHz in every sample of both runner calls; the config reads at the start and the close of the session (and the runbook's step 7 read at 08:48:23 PST): TDP 65 W / 65 C / 600 MHz / 499 mV, as the card holds it; nothing set; nothing opened on card 0 |
| A1: the lab's runner copy (run_x04_e198a1.py, sha256 5b2307eb...), every device process under a plain `timeout 10`, no KILL sent by any process of the sitting (E198.md.dated-amendment-A1.md) | `session/hashes.txt`'s runner line: `5b2307ebab4c1b359f9163a0c2bdb8c8a0a0359f39a8d0c766b47dfa22805780`; every device process exit 0 (no 124, no not-ended); the session log has no "A DEVICE PROCESS DID NOT END" line; the dry pass's listings: every device call under a plain `timeout 10`, no `timeout -k` |
| at least 40 minutes between sitting A's end and sitting B's first card command (E198.md 11) | step 9's line: "rest: 40 minutes since E198's session end (2026-11-16 08:08:04 PST; dry sessions and blocks that opened no device skipped; every tree of ours on aifoundry1 read)"; the rest opened 08:48:04 PST, before step 7's config read (08:48:23) and the session's first card command (08:48:55); step 7 ran only after it had opened |
| for sitting B, a real sitting A on the box whose main run started and ended, and none that crashed (KIT.md, step 9) | step 9's line: "sitting A held first: build/e198/T1794842686" (sitting A's session, ended normally at 08:08:04, its data committed `e8b4c0d7`) |
| the smoke with --blocks S,D,W,T,C and the kit's gate (E198.md 2) | the gate's line: SMOKE GO (08:50:50 PST, Results) |
| 9 passes, the seeded order (E198.md 2) | 9 of 9 passes, 15 runs each; the 135 calls as run (block and arm, in `x04/run.log`) equal the 135 of the kit's dry listing `tools/claims-v3/e198/desk/dry-e198a1-B.txt`, call for call (a desk check of the measured log); the session's own dry pass on the box (step 8, 08:48:31) listed SAME |
| the cap: 50 card-minutes; the runner's deadline = first card command + cap - 120 s, never past the window's last end - 180 s | the deadline line: 09:36:55 PST (epoch 1794850615 = the first card command + 2,880 s; the window's last end - 180 s, 12:16:00, is later); it never fired: the main run ended at 09:16:20, 20 min 35 s before it; 27.42 card-minutes against the cap of 50 |
| the stops (E198.md 9, in A1's form) | none fired: board peak 40.34 W (the stop: above 65 W on three samples in a row); die peak 55 C (the stop: 70 C); every sample at 600 MHz; the telemetry file grew throughout; every device process exit 0 (no exit 1, 3 or 124, none still running at 25 s); no card wait; no stop file; the deadline not reached |
| the one sampler a runner call, through E191's guard (E198.md 3; the A1 form says "E128's guard", E193's wording); no statistics reset | two runner calls, the smoke and the main run, one sampler each: the box's `build/ettelem/ettelem` (sha256 8008f96f...) through E191's guard (6fd26f51...), `--every-ms 100`, no `--reset-ms`; the session's preflight `dmcmd_audit: GO (19 send site(s), 0 disallowed; allow-list: none)` |
| per-sensor codes not recorded (E198.md 2, by E193.md 4) | not recorded |
| the post-launch credit barrier on the card's build | UNCONFIRMED (E193.md 14; the kit found no worker firmware source to read) |
| the build: the day's (KIT.md; the card-lane brief, sitting B: step 6 `wait` only) | the day's one build (07:23:33-07:23:36 PST on the box, X04-BUILT rc=0 by `build_e198a1.sh`, the kernel gate on E193's `.text` `fd720727...`, LISTING SAME x3), read again by step 6's wait at 08:40:52; the session's binaries the same (host `a4bd858c...`, kernel `01a37767...`) |
| the dry pass: the session's own wrapper with DRY=1 (KIT.md, A1's step 8) | "E198-DRY sitting B rc=0 smoke=0 main=0 calls=10+135 manifest=written", both listings SAME (08:48:31 PST) |
| the harness | HARNESS OK on the box (51 files at their sha256 in E198's folder there, 3 of them executable), in the session's own log and at steps 5 and 6 |
| the window (E198.md 12) | sitting B's G = sitting A's session end + 40 minutes = 08:48:04 PST; last start 10:19, last end 12:19 PST (Departures 4); launched 08:49:00 PST (T0 08:48:55), ended 09:16:20 |
| one session of ours on aifoundry1 at a time; nothing on card 0 (E198.md 11) | the round's booking of aifoundry1 held by this lane from 07:22:33 PST for both sittings; the session's holder check found no process of ours or of another user on either card; the private /dev held card 1's two nodes only |
| the host's package counter | not read |
| the post | waived by the owner (Departures 5) |

## Departures, dated

*Mon 16 Nov 2026, PST. Items 1-10 were set by his go, the round's brief and E198's go lines (`ready-e198b`) before the session; item 11
was read at the collection. All were written here after the collection and before the reducer ran. Items 1-3 and 5-8 are sitting A's,
unchanged.*

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
4. **G = the booking's day, and sitting B's G from sitting A's end.** This lane took the round's booking of aifoundry1 at 07:22:33 PST
   (sitting A's G) and kept it for sitting B, as E198.md 12 allows ("A card lane that books once for both sittings uses that G for sitting A;
   sitting B's G is then sitting A's session end plus 40 minutes"). **Sitting B's G = 08:08:04 + 40 minutes = 08:48:04 PST.** The window:
   last start 10:19, last end 12:19 PST, rounded up, inside G's Pacific day (G at 20:29:00 or earlier: yes); step 1 wrote it at 08:40:18.
5. **The post: waived.** "the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST". No claim, no release.
6. **The host's package counter: not read.** No E198 or E193 file names it (git grep at HEAD `8aa6185e` for rapl, powercap or energy_uj, any
   case: 0 files; no E198 or E193 file changed since).
7. **No network-access approval to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry1 without that
   check. The kit's login-link stop stayed live, and no step met a login link: the round's lock file of such checks read 70 lines before and
   after every step.
8. **The desk and the session.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3. The orchestrating session is
   the round's session on its yvb3 Claude account.
9. **The order on aifoundry1.** E199 (sent first by the HOLD of item 2), then E198 sitting A (07:24:46-08:08:04 PST), then this sitting.
   Between the two sittings the round's quiet hold was off (sitting A's data commit at 08:13:31 to this sitting's step H at 08:39:45), and
   one other card lane's data commit landed while this sitting ran (`548d736e`, 09:02:36 PST, E200 on aifoundry2: another box and card;
   its own paths only). This sitting's step 0 (72 of 72 as stated) and step 2 read LAB at `e8b4c0d7`, and the collection's history check
   (HISTORY OK) read it at `548d736e`.
10. **The sealed card-1 forecast** is E198.md's freeze line 2: sha256 7de55c4f..., posted as #2.5.1.2.1 at 22:56:05 PST Sun 15 Nov 2026 and
    registered before the land. The round's list of sealed card-1 forecasts held no other E198 line (read 07:18:11 PST); no dated note was
    needed or made, and step 2 read "the sealed card-1 note: none". It stays sealed: no number of it is in this directory or any lab file.
11. **Notes, not departures.**
    - The die peak, 55 C, is 2 C above E198.md 9's predicted 53 C (Results), as in sitting A; a prediction, not a stop or a rule.
    - Step 10's wait found the session by A1's real script name (`session_e198a1\.sh`); four calls, running at each of the first three, the
      fourth at 09:16:22 with the box's manifest written (197 files).

## Device commands sent

READs only: the session's start and closing `ettelem config` and each runner call's `ettelem sample --every-ms 100`, all through E191's
guard (dmcmd_audit GO, KIT.md section 6), plus the identity read's sampler (THE IDENTITY GATE (b)) and the runbook's step 7 config read; the
host opened card 1's ops node only; `et-who --check` sends no device command. No set, no reset, no statistics reset, no firmware query,
nothing to card 0. With ET_DEVICES=1 and the private /dev, the device layer opened card 1 alone (the 145 runtime lines below), so its
runtime creation's stock abort of pending work on the submission queues (the lab-wide note of Mon 16 Nov 2026) reached card 1's queues only,
on a card held by this session alone.

## Files

| path | what |
|---|---|
| `session/` | session.log, the two config reads (`.json`, `.raw`, `.err`), the identity reads (`ident-a.txt`, `ident-b.txt`, `ident-end.txt`, `ident/`), the holder check's output, the private /dev's listing, the warden (`holderd/`, `warden.out`), the first card command's time, the binaries' hashes, the harness, tree and preflight outputs, the smoke's runner output and gate, the main runner's output, MANIFEST.sha256 (the box's), session.rc |
| `smoke/`, `x04/` | each runner call's run.log, events.jsonl, runs.jsonl, device-stdout.txt, device-stderr.txt, telemetry.jsonl.gz (gzip, no name, mtime 0; its unpacked bytes are the box's manifest's), hostraw.txt.gz and hostraw-index.jsonl (every device process's raw standard output, packed) |
| `facts-e198-b.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it |

## Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository
(the first line), then run the rest as they stand:

    D=docs/reports/data/2026-11-16-e198-x04-clock-sitting-b-aifoundry1-c1; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/x04" && cp "$D/x04/runs.jsonl" "$R/x04/" && gzip -dc "$D/x04/telemetry.jsonl.gz" > "$R/x04/telemetry.jsonl"
    for p in runs.jsonl telemetry.jsonl; do [ "$(awk -v p="x04/$p" '$2 == p {print $1}' "$D/session/MANIFEST.sha256")" = "$(shasum -a 256 "$R/x04/$p" | cut -d' ' -f1)" ] && echo "x04/$p: the box's bytes" || echo "x04/$p: not the box's bytes"; done
    /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$R/x04" --out "$R/x04.json"
    /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$R/x04.json" "$R/x04" --out "$R/checks.json"

They check every entry of `SHA256SUMS`; unpack the main run's telemetry and set it and `x04/runs.jsonl` against the box's own manifest
(`session/MANIFEST.sha256`: both lines must say "the box's bytes"); run the registered reducer (`proposal/src/reduce_x04.py`, sha256
98bbc174..., unchanged, no `--pvt`, no `--keep-warmup`); and read E193.md 8's nine checks with the kit's checker. Step 13
(`rb/s24_reduce_e198.sh B`) does the same from a runbook directory whose window names the day of the sitting.

## What E198's README adds to E193's form

- **The card and its gates:** aifoundry1 card 1 (`--device 1`, ET_DEVICES=1 for every device process, card 1's lock). **THE PRIVATE /dev:**
  "the private /dev (privdev_e198.sh, a listing inside it, nothing opened): card nodes inside [et1_mgmt et1_ops], 16 entries; the box's real
  /run/lock, /proc and /sys" (08:48:56). **THE IDENTITY GATE (a):** "IDENT-A OK: TDP 65 W, 65 C, minion 600 MHz as found; PCIe target
  /dev/et1_mgmt and physical device ID 1 on its stderr; minion_mv within (450, 510)"; the closing read the same (`session/ident-end.txt`).
  **THE IDENTITY GATE (b)** (08:49:06, with the sampler running): OK; ours on card 1's management node 1, ours on card 1 1, ours on card 0
  0, ours elsewhere 0, another login's on card 1 0, on card 0 0; the holder check from inside the private /dev saw the same line as the
  box's own et-who outside it. **The warden** (`session/holderd/summary.json`): 15 holder checks served from inside; 148 processes of the
  sitting held a card node, every one card 1's (`/dev/et1_mgmt` 3, `/dev/et1_ops` 145; the programs `ettelem` and `x04clock_host`);
  **watch hits: none**; ended by its stop file.
- **The runtime line:** each runner call's `hostraw-index.jsonl` summed (`facts-e198-b.json`, "host_runtime_lines"): the smoke 10 device
  processes, 10 runtime lines dropped by the guard, 57 X04 lines; the main run 135 device processes, 135 runtime lines dropped, 1,350 X04
  lines; "x04_not_at_start" 0 and "opening_text_left" 0 in both; every runtime line names card 1 ("Opening device 1", 135 of 135 in the main
  run's `hostraw.txt.gz`, 10 of 10 in the smoke's). Re-make: unpack `hostraw.txt.gz`, split it at its "### <seq>.stdout <bytes>" headers,
  and `dropruntime_e198.py`'s drop_runtime gives each process's stream as the runner read it.
- **The rests and the window:** the booking 07:22:33 PST (sitting A's G); sitting B's G from sitting A's end plus 40 minutes, 08:48:04; last
  start 10:19, last end 12:19; the rest before the sitting, step 9's line above (40 minutes since sitting A's session end).
- **The scores** are not in this commit: step 13 (`rb/s24_reduce_e198.sh B`, then `score <A> <B>`) runs the registered reducer, E193's
  checker and E198's transport scorer after it; a records lane commits their outputs beside the data with a dated note.
- **The sealed card-1 forecasts:** E198.md's freeze line 2 (the model session's, sha256 `7de55c4f...`, posted 22:56:05 PST Sun 15 Nov
  2026, registered before the land); no later one (Departures 10). Named by its sha256 only; never scored in a lab file.

## The day's records

- **The steps' exits** (the card lane's runbook log; PST): the round's quiet hold added again for this sitting (step H, 08:39:45); the
  one-lab desk span 08:39:45-08:40:36; step 0, A1's anchor read for sitting B, 72 of 72 as stated at LAB's HEAD `e8b4c0d7` = GitHub main,
  status 0 lines (sitting A's data directory the only E198 data path), the 1-minute load 1.85 (08:39:55-08:40:06); step 1 rc 0 (08:40:18);
  step 2 (A1) rc 0, HEAD `e8b4c0d724d3`, the registration, the kit and A1 found by their content, nothing under `tools/claims-v3/e198` after
  A1's commit, HISTORY OK, the lists at their pinned counts and bytes, the runner copy re-made and equal, "E198 data paths in any ref: 59
  (sitting A's: 59)" (08:40:24-08:40:26); step 4 FREE on both cards (08:40:36); step 5, 52 paths, 0 files' contents sent, HARNESS OK and TREE
  OK (08:40:37); step 6 wait only, rc 0, the day's build (08:40:52); step 7 rc 0 after the rest opened (08:48:23); step 8 start and one wait,
  rc 0 (08:48:28-08:48:37); step 9 rc 0, launched (08:48:55-08:49:00); step 10, four waits, the last rc 0 (09:16:22); the one-lab collect span
  from 09:16:36; step 11 rc 0, COLLECTED (09:16:36-09:16:38).
- **The copy:** one read-only copy back of the session's directory, **COPY-BACK EXACT** against the box's manifest
  (`session/MANIFEST.sha256`: 197 files at the box's sha256, nothing else but `session.rc`), packed into the 57 files `SHA256SUMS` lists.
- **Privacy:** the collector's scrub (the box's home as `~`, every holder line's user and our own box login as `<login>`: no home-folder path
  and no login left), the desk-path gate (CLEAN: 58 files read, 0 hits) and the history check (HISTORY OK) all passed; `facts-e198-b.json` is
  the collector's summary. `SHA256SUMS` (the collector's) pins every file but this README and itself.
- **The device-command audit** (`dmcmd_audit.py`, no allow-list, no exception): GO, 19 send sites, every one a READ, at step 2 on the desk,
  on the box after the build, and by the session's own preflight (`session/preflight.txt`).
- **The public-text scan** before this commit read every text file here, the text inside every `.gz` and this README, with the lab's
  sanitizer (its fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's
  classes over this README and the commit message. This README and the commit message: no sanitizer hit; the classes match only the owner's
  quoted word "discord" (Departures 1). Its three hits in the collected files are three uses of one word, the kit's own name for E198's
  folder on the box (in the harness line, twice, and in the session log's line naming the box and its tree), matched by the sanitizer's
  privilege-word pattern (it names a folder, not an account's rights): kept as collected. The round's classes, read over the collected text
  files too, match only the device layer's own lines about the chip's on-die memory addressing (in the config reads' and the identity
  sampler's `.err` files and each runner call's `device-stderr.txt`: the hardware's word for that memory, which the class lists because a
  desk path of ours holds the same word; here it names no path) and the warden's request ids in `session/holderd/served.jsonl` (a process
  id and a nanosecond time, matched by the class for chat ids): kept as collected.

SPDX-License-Identifier: Apache-2.0
