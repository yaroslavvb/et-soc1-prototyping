# E192: scalar integer bit-flip and carry ladders on aifoundry3 card 0 - all 9 registered passes (pass 0 the warm-up) ran in one session of 59.5 card-minutes, reads only, no stop, the smoke gate GO, every run in the registered order; the registered reducer runs after this commit

*Sat 14 Nov 2026 (week 46), PST, Q179's card lane `card-e192`, orchestrated from aifoundry2. Registered in `a282aad6`
([`E192.md`](../../../../tools/claims-v3/e192/E192.md): the model session's proposal X01, its 32 arms, the order, the passes, the smoke, the
reduction by sha256, the checks, the stops, the card time, and both freeze lines of its sealed forecasts) and kitted in `a6fe5c20`
([`KIT.md`](../../../../tools/claims-v3/e192/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e192/CARD-LANE-BRIEF.md)), both on
Sat 14 Nov 2026, before any E192 datum. **Blind:** both freeze lines were in the registration before the session's first card command
(21:07:37 PST), and these are the first E192 runs on any card. **The forecasts stay sealed:** no forecast number is in this directory, and
nothing here scores E192 against them; the model session scores them privately against the reduced prices the lab publishes.*

*Departures, dated Sat 14 Nov 2026 and set before the session (in full under Departures below): the go, by the owner's answer of about
14:50 PST naming the runs to follow E189 on aifoundry3 card 0 "as each becomes ready", with E192's registered defaults unchanged; the day's
post waived by his words; the audit table for command 74 (E144's) and one relaunch after a "no device opened" refusal (not needed), both the
kit's defaults, set by the orchestrator; the window in the form "after another session of ours that day" (E189's, 20:11:44-20:27:30 PST);
the host's package counter not read; no fresh network-access approval to name from aifoundry2; the desk aifoundry2 under
`/usr/bin/python3` 3.12.3; the orchestrating session the round's session on its yvb3 Claude account.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E192.md, the kit). The counts below of runs, launches, approach flags and peaks are **desk arithmetic of the measured
records** (`run/runs.jsonl`, `run/marks.jsonl`, `run/telemetry.jsonl.gz`), not prices and not checks: the prices are the registered reducer's
(`proposal/src/reduce_intbits.py`, sha256 `715fddaa...`, unchanged) and the section 7 checks are the kit's checker's (`check_e192.py`), both
run only on this directory once it is committed (`rb/s24_reduce_e192.sh`); their outputs, `intbits-e192.json` and `checks-e192.json`, are
committed by a later lane. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Results (measured)

- **Passes complete: 9 of 9** (pass 0 the registered warm-up, recorded and set aside by the reducer): **8 measured passes**. Each pass ran its
  36 runs (two burn-ins of the anchor, the anchor first, the 32 arms, the anchor last), **327 runs and 3,255 launches** with the smoke's 3.
- **The sampler: the per-sensor sampler** (`SAMPLER=pvt`, E89's `pvt_sample.py`) for the whole session, because all three of the kit's
  conditions held: the per-sensor chain GO with E144's table (the go's audit table for command 74, Departures 3), the box copy at its reviewed
  sha256 `c4e4aed5...`, and the probe (the session's first card command, three ticks) answered with all 34 sensors on every tick. Its 10 Hz
  telemetry holds **35,703 samples** (21:07:38-22:07:08 PST), every one with the board, the die and the clock, and every one with the 34
  per-sensor codes.
- **Card time: 3,571 s = 59.52 card-minutes** from the first card command (the probe, 21:07:37 PST) to the session's end (22:07:08 PST),
  against the registered about 52 (about 55.5 with the eight 30 s gaps) and **the cap of 65** (22:12:37): the cap never bound (the gate's
  check before pass 8 read 723 s left against 491 s needed), and no end-stop came.
- **No STOP**: no live stop (board, die, a quiet sampler), no gate stop, no end-stop, no stop by hand; `run/STOP` was never written. The
  reference session's own `run/SESSION_DONE` (an empty file) ended the gate; `run_session.sh` and the wrapper each exited 0.
- **The smoke gate: GO** at 21:08:14 PST: `nop`, `add.a.f2` and `add.cr.l31`, each exit 0, 5 launches of 0.4 s, every line ok, `check_bad`
  0 and 1,024 participants; the smoke's heater check exited 0 with its **highest board reading 49.79 W over 33 samples**, under the 70 W
  ceiling.
- **Peaks:** board **53.32 W** (21:20:17 PST; no sample above 80 W) and `temp_c.minshire[0]` **61 °C** (22:06:43; lowest 49 °C; no sample at
  or above 70 °C), against the stops 80 W on three distinct readings and 70 °C.
- **Clock: 600 MHz in 35,703 of 35,703 samples.** The minion rail read 521-523 mV.
- **The order:** every pass's 36 runs in exactly the order `desk/order-e192-aifoundry3.txt` writes out for a host named `aifoundry3`, 9 of 9
  passes, run for run; the smoke as registered (`nop`, `add.a.f2`, `add.cr.l31`).
- **The runs' own records:** all 3,255 launches `ok` with `check_bad` 0 and 1,024 participants; every device process exited 0. The approach
  was on protocol for **325 of 327 runs**; the two off it, each flagged in its record and kept (the checker counts them, E192.md section 7
  item 4): pass 0's first burn-in of the anchor (15 heats, the cap on heats, its start at 57 °C, 1.4 s quiet) and pass 5's `add.a.f0` (its
  start at 59 °C, 1.9 s quiet). No approach wait timed out. 378 heater launches preheated in all.

| block | span (PST) | runs | the gate's measured length |
|---|---|---|---|
| the smoke (pass -1) | 21:07:48-21:08:23 | 3 (2 s each) and the heater check | |
| pass 0 (the warm-up) | 21:08:23-21:15:04 | 36 | 400.9 s |
| pass 1 | 21:15:34-21:21:38 | 36 | 364.1 s |
| pass 2 | 21:22:08-21:28:05 | 36 | 356.4 s |
| pass 3 | 21:28:35-21:34:30 | 36 | 355.2 s |
| pass 4 | 21:35:00-21:41:03 | 36 | 363.1 s |
| pass 5 | 21:41:33-21:47:30 | 36 | 356.8 s |
| pass 6 | 21:48:00-21:54:03 | 36 | 362.8 s |
| pass 7 | 21:54:33-22:00:33 | 36 | 359.9 s |
| pass 8 | 22:01:03-22:07:00 | 36 | 356.4 s (from the marks) |

The spans are the first and last marks of each block (`run/marks.jsonl`); the lengths are the gate's own (`run/gate.jsonl`, `cap_ok`).
Between passes the card lock was released for the registered 30 s and the holder check made again: it passed every time.

## Registered against happened

| item | registered (E192.md, the kit) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry3 card 0, 600 MHz as found, reads only, nothing set | card 0; 600 MHz in 35,703 of 35,703 samples; k6's config read before the session (20:58:58 PST): TDP 0 W / 65 °C / max_power / 600 MHz / 523 mV; nothing set |
| harts | all 32 shires x 32 minions, hart 0 of each | 1,024 participants on every launch |
| arms and order | the 32 arms of `arms.txt`, the order `random.Random("<hostname>\|<pass>")` gives, written out for aifoundry3 | the dry pass's `E192-DRY OK: 328 device calls (327 host, 1 heater)` in the registered order (20:59:04); the session ran the same order, 9 of 9 passes, run for run |
| the run | `timeout 10 intbits_host --arm <arm> --seconds 4 --window 240000000 --stop-file`, launches of 0.4 s | 10 launches a run in passes 0-8, 5 in the smoke's 2 s runs; every device process exit 0 |
| the approach | E78's: heat to 59 °C or more, idle to 58 °C or less, at least 2 s quiet, at most 120 s | 325 of 327 runs on protocol; 2 off it, flagged and kept (Results) |
| passes | 9, pass 0 the warm-up, 36 runs each, 30 s with the lock released between | 9 complete, 36 runs each; the gaps and holder checks as registered |
| the smoke | first, under the lock; the heater check under 70 W (the code: stop above 70 W); the kit's smoke gate | heater check 49.79 W, exit 0; the smoke gate GO |
| stops | board above 80 W on three distinct readings, the die at or above 70 °C, the sampler quiet 10 s; the block's own die and staleness checks | none tripped (53.32 W, 61 °C; the sampler never quiet) |
| card time | about 52 card-minutes (about 55.5 with the gaps), cap 65 from the first card command | 59.52 card-minutes; the cap never bound |
| the rest | E192's first card command at least 40 minutes after our previous session on the card | 40 minutes after E189's session end (20:27:30 PST): step 9's rest line, Departures 4 |
| the window | his go's, inside one Pacific day | last start 22:24, last end 23:30 PST; launched 21:07:42 (T0 21:07:37), ended 22:07:08 |
| the sampler | the per-sensor sampler where it answers and the audit reads command 74 as a READ (E144's table), else the plain one | the per-sensor sampler, its probe 34 sensors on every tick |
| the build | on aifoundry3, `check_elf.py` "loops 16, bad 0", the host's `--list` byte for byte the registration's table; at most two starts a day | one start (20:58:06-20:58:08 PST on the box): loops 16, bad 0; the arm table byte-equal; kernel ELF `2635bcd3...`, `.text` `aafdba4b...` (the registration's desk build's `.text`; its ELF differs: reported, never judged), host `6e170019...` |
| the host's package counter | not read | not read |
| the post | the day's post, or his waiver for that day | none: waived by the owner (Departures 2) |

## Departures and notes (dated Sat 14 Nov 2026, PST; each set by his go, the round's brief and the orchestrator before the session, written here after the collection and before the reducer ran)

1. **The go.** Asked today at about 14:44 PST, "May E189 run on aifoundry3 card 0 today (about 95 card-minutes, 600 MHz as found, reads
   only), followed by E191/E192/E193 as each becomes ready — and how should today's Discord claim post be handled?", the owner answered
   "Yes, but I'll post on Discord" (about 14:50). E192.md section 12's items are named by his "followed by E191/E192/E193 as each becomes
   ready", in answer to a question that named aifoundry3 card 0, 600 MHz as found and reads only. E192's own items (about 52 card-minutes,
   cap 65; the 40-minute rest before its first card command and after its end) are its registered defaults, unchanged.
2. **The post: waived for the day.** Asked next to post the day's claim, the owner answered "it's fine not to announce, the cards are
   unused". No post was made, so no release line either (step 3, and step 11's release: SKIPPED). Every other etiquette check stood: k6's
   look before the session (et-who, who, uptime, the holder rule: FREE at 20:57:49 PST), step 7's reads (et-who clean at 20:58:58), the
   card's lock taken by every block, the holder check before every pass, `timeout 10` a device process.
3. **The two kit items his go did not name**, set by the orchestrator to the kit's defaults before the session (the round's log, section
   112): **the audit table for command 74 = E144's** (`tools/claims-v3/e144/dmcmd_table_e144.json`: command 74 group 0 READ), so the
   session's first card command was the per-sensor probe and the per-sensor sampler ran (step 9 without `--plain-sampler`); **one relaunch
   after a launch refused with "no device opened"**, only after the look reads FREE again. **Not needed:** the first launch passed every
   check of its own and ran the session; there was no refused launch.
4. **The window, the form "after another session of ours that day"** of the readiness check's go lines. E189 ran on aifoundry3 card 0
   today (session 20:11:44-20:27:30 PST, its data `fa9098c4`), so E192's first card command could come no earlier than 21:07:30 PST, and
   the kit's rest rule read it on the box at step 9: "rest: 40 minutes since E189's session end (2026-11-14 20:27:30 PST; dry sessions and
   blocks that opened no device skipped)". G is the moment the card lane held the round's booking of aifoundry3, **20:54:40 PST**. The last
   start is G+1:30 but no later than 22:25: G+1:30 = 22:24:40, written to the whole minute below so that it is never later than G+1:30:
   **22:24 PST**; the last end **23:30 PST** (step 10 reads only a session start written today, so the session's end had to be seen before
   midnight): `s02_window_e192.sh 2026-11-14 22:24 23:30`, written by step 1 at 20:57:28.
5. **The host's package counter: not read** (E192's kit has no step or option that reads it; his go said nothing of it).
6. **A fresh network-access approval for aifoundry3: nothing to name.** The session was orchestrated from aifoundry2, a lab box that
   reaches aifoundry3 without that check. The kit's login-link stop stayed live (an exit 11 with its lock line ends the day's box steps); no
   step met a login link.
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names. The
   orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14 Nov 2026 after aifoundry2
   went down abruptly at about 16:53 PST on Fri 13 Nov.
8. **Notes, not departures.** Step 10's wait looks for the session by the pattern `session_e192(_v[0-9]+)?\.sh`; step 9 launches
   `session_e192.sh`, which runs `run_session.sh` as a child and never replaces itself, so the pattern matches the script step 9 launched
   (read before step 9; seven calls, running at each of the first six, ended with its manifest at 22:07:18). The next session of ours on
   aifoundry3 rests until 22:47:08 PST (E192's end plus 40 minutes).

## The day's records

- **The build** (step 6, one start): `build/build/intbits/BUILD-E192.txt` (the hashes beside E192.md section 16's desk build),
  `check_elf.txt` ("loops 16, bad 0"), `arm-table.jsonl` (the host's own table, byte-equal to `desk/arm-table-e192.jsonl`), `preflight.txt`,
  and `build/build-attempts.txt`. The box's compilers: g++ 13.3.0, cmake 3.28.3, the RISC-V toolchain's gcc 15.1.0; the box's Python 3.12.3.
- **The copy:** one read-only copy back of the session's directory, its launch output and the build record, **COPY EXACT** against the box's
  manifest (`box-manifest.txt`, 26 files at the box's sha256, nothing else) and the session's own `session/MANIFEST.sha256` (18 files).
  `run/telemetry.jsonl.gz` is gzip with no name and mtime 0; its uncompressed bytes are the manifest's `run/telemetry.jsonl`.
- **Privacy:** our own box login was masked where it appeared (0 lines needed it); the holder-line check (SCRUB-CHECK OK), the desk-path gate
  (CLEAN, twice) and E178's login scrub (OK, 27 files) all passed; `facts-e192.json` is the collector's summary. `SHA256SUMS` (the collector's)
  pins every file but this README and itself.
- **The device-command audit** (`dmcmd_audit.py`, no allow-list, no exception): the plain chain GO with the stock table (17 send sites, every
  one a READ) and the per-sensor chain GO with E144's table (23 sites), at step 2 on the desk, again on the box after the build, and by the
  session's own preflight (`session/dmcmd-preflight.txt`).
- **The public-text scan** before this commit read every text file here, the text inside the `.gz` and this README, with the lab's sanitizer
  (its fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's classes over
  this README. Its one hit in the collected files is a false match: the scan's pattern for a private-network port matched one telemetry
  line where the per-sensor sampler's field `cmd_mismatch` (its running count of replies matched by tag whose command field differs, E89's
  rule A2: the match is on the tag alone) read 8,792, written after the field name's colon; kept as collected. The round's classes, read
  over the collected text files too, match only the device layer's own lines about the chip's scratchpad memory in `run/stderr.txt` (its
  "Scratchpad base address" lines, the hardware's word, not a path), kept as collected.

## Device commands sent

Reads only. The session's first card command was the per-sensor probe (three ticks, each of six READs: commands 33, 60, 27, 74 group 0, 32
and 53), then the per-sensor sampler sent the same six READs at 10 Hz for the whole session (no statistics reset: `since_reset_ms` −1); the
intbits host and E78's heater opened the card's ops node only (327 host runs and 379 heater launches, the smoke's heater check among them,
every one exit 0). Step 7's config read before the session (`ettelem config` through E128's guard) was the only other management command the
card lane sent. No set of any kind (TDP, threshold, clock, voltage), no reset, no statistics reset, no firmware-revisions query, no power
cycle. Nothing was killed.

## Files

| path | what |
|---|---|
| `run/` | the reference session's directory as the box wrote it: `runs.jsonl` (one `INTBITS` record a launch, with its run's approach), `marks.jsonl` (the blocks, idles, heater launches and checks), `telemetry.jsonl.gz` (the 10 Hz samples), `gate.jsonl` (the kit's gate: the smoke gate, the cap checks), `stderr.txt` (the host's device-layer log), `session.log`, `SESSION_DONE`, `sampler.err`, `stopwatch.err` |
| `session/` | the wrapper's files: `session.log` (the kits' session log), `wrapper.rc`, `first-card-command.txt`, `pvt-probe.jsonl` and `.err`, `gate.out`, `run_session.out`, `dmcmd-preflight.txt`, `pins-*.txt`, `MANIFEST.sha256` |
| `build/` | the day's build record (above) |
| `box-manifest.txt`, `facts-e192.json`, `SHA256SUMS` | the box's manifest of what was copied, the collector's summary, the collector's sums |

## Next

The registered reducer and the section 7 checker, after this commit only: `rb/s24_reduce_e192.sh` unpacks the telemetry, checks it and the
run records against the session's own manifest, runs `reduce_intbits.py` (unchanged) and `check_e192.py`, and writes `intbits-e192.json` and
`checks-e192.json`; a later lane commits them beside this directory. No score: the model session scores its sealed forecasts privately
against those published prices.

SPDX-License-Identifier: Apache-2.0
