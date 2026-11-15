# E189: the blind day on aifoundry3 card 0 - all 24 registered passes ran in one session of 15.8 card-minutes, reads only, no stop line tripped; every copy burst was cut to 7 of its 8 launches by the host's own budget (SHORT, scored on the launches it ran); the frozen scorer runs after this commit

*Sat 14 Nov 2026 (week 46), PST, Q174's card lane `card-e189` (its re-run), orchestrated from aifoundry2. Registered in `c86940c1`
([`E189.md`](../../../../tools/claims-v3/e189/E189.md): the question, the six configurations, the frozen forecasts, the rules E189-S1,
S1T, S2 and S2T, the order, the card time, the stops) and kitted in `b42dc95c` ([`KIT.md`](../../../../tools/claims-v3/e189/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e189/CARD-LANE-BRIEF.md)), both on Fri 13 Nov 2026, before any E189 datum. It answers
the step of the plan behind the owner's question of Wed 11 Nov 2026, "Can I answer how many joules a particular computation takes?", as
E189.md lays it out: four programs (a copy, SHA-256, a sort and sparse parity) in six configurations, their joules forecast before the card.
**Blind:** every forecast, band and rule was committed before the session's first card command (20:11:45 PST), and these are the first
E189 passes on any card. The day's post was waived by the owner (Departures, 4).*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold, band and
rule is **registered** (E189.md, `plan-e189.json`, `forecast-e189.json`). The per-configuration means in the second table are **desk arithmetic
of the measured passes** (each configuration's four `energy.json` records): **they are not verdicts**, and no forecast is set beside them
here. The four rules' words are the frozen scorer's (`score_e189.py`, unchanged), which runs only on this directory once it is committed
(`rb/s24_score_e189.sh`); its output, `scores-e189.json`, is committed beside this directory by a later lane. Nothing here changes a frozen
number. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## What ran (measured)

- **Card:** aifoundry3 card 0, **600 MHz in all 9,436 samples** of the session's 10 Hz telemetry (none without a clock reading; no sample
  off 600 MHz: `queue.json` > `off_clock` is empty). `ettelem config` through E128's guard at the session's start (20:11:45 PST) and end
  (20:27:30): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV, the same at both ends. **Nothing was set.** `since_reset_ms` −1 in every
  sample: no statistics reset.
- **Card session:** T0 1794715904 = 20:11:44 PST to its `session end` at 20:27:30 PST: **946 s, 15.77 card-minutes** (from the first card
  command, 20:11:45.08, to the close, 20:27:30.25: 945.2 s), against the registered estimate of about 95 and the cap of 110. `runner.rc` 0.
- **The sequence, as registered:** the stop-path test passed (the board, die and clock lines each tripped on live samples within 0.2 s, and
  each refused a start); the ramped smoke, all 8 runs ok (the ledger's self-test; the copy at 64 MiB random and zeros, then 1 GiB random;
  SHA-256 at `--block 2048 --repeat 1` with `--expect`; the sort of 512 keys shuffled and sorted; sparse parity's instance once), `smoke gate passed`
  at 20:11:50; idle anchor 1 (20:11:50-20:13:50), rounds 1-2 (passes 1-12, 20:13:50-20:18:40), idle anchor 2 (20:18:40-20:20:40), rounds
  3-4 (passes 13-24, 20:20:40-20:25:30), idle anchor 3 (20:25:30-20:27:30), each anchor whole; `the counters arm: DROPPED by the kit
  (KIT.md section 5): not run`; the closing config read; `session end`.
- **All 24 passes ran in the registered order** (`plan-e189.json`, never re-drawn), and **all 24 reduced with the reducer's hard checks
  passed** (`energy.json` > `ok` true, `hard` empty; the reducer is energy.sh's `energy_reduce.py`, unchanged). The runner set none aside.
- **No stop line tripped.** The highest live readings were **41.77 W board** (20:24:30) and **53 °C `minshire[0]`** (20:16:53), against
  the stops 65 W and 70 °C.
- **The die gate never waited.** Every pass started at 49-51 °C (the runner's live sample and the reducer's `die_c.before` alike), below the
  forecast band of 52-60 °C: each pass carries the runner's flag "T0 below the forecast band" and is scored given its own T0, as E189.md
  section 11 says (a die below 52 °C does not block).
- **Every copy burst was SHORT.** In all 8 copy passes (copy, zeros, and copy, random) the ledger host's own budget ended the burst after **7
  of the 8 registered launches**: the host exited 1 with status FAIL, the adapter's `host.json` reads `problems` ["reps: 7 of 8 done"] and
  `stop_reason` "budget", and every other check of the host's line was good (records, mismatches, units). E189.md sections 8.2 and 12 score
  such a pass on the launches it ran, flagged SHORT, never as the program failing; the reducer flags each "host ran 7 of 8 launches
  (budget)". Each of the 16 other passes ran its K launches with status PASS. **No pass is a failed run.**
- **The host's package counter was not read** (step 9 ran without `--rapl-allowed`); the host's share stays assumed and labelled so.

## The passes (measured; the means are desk arithmetic of the measured passes, not verdicts)

| configuration | passes reduced ok | launches a pass (K registered) | J over idle a launch, mean of 4 (passes) | J with the card at rest a launch, mean of 4 (passes) | flags |
|---|---:|---|---|---|---|
| copy, zeros (`--bytes 1G --passes 14 --data zeros --width 32`) | 4 of 4 | 7 (8): SHORT | 5.431 (5.326-5.528) | 26.747 (26.547-26.891) | budget: 7 of 8 launches |
| copy, random (`--bytes 1G --passes 14 --data random --width 32`) | 4 of 4 | 7 (8): SHORT | 7.468 (7.300-7.651) | 28.893 (28.771-29.043) | budget: 7 of 8 launches |
| SHA-256 (`--block 2048 --repeat 800`, with `--expect`) | 4 of 4 | 9 (9) | 2.603 (2.570-2.692) | 12.811 (12.766-12.883) | |
| sort, sorted (`--keys 512 --reps 1800 --order sorted`) | 4 of 4 | 8 (8) | 3.382 (3.334-3.499) | 16.643 (16.562-16.750) | |
| sort, shuffled (`--keys 512 --reps 1800 --order shuffled`) | 4 of 4 | 7 (7) | 4.125 (4.103-4.142) | 20.495 (20.375-20.546) | |
| sparse parity (the registered instance: `--n 544 --k 4 --eta 0.39 --m 1792 --seed 3`) | 4 of 4 | 9 (9) | 7.599 (7.480-7.798) | 19.900 (19.709-20.073) | |

J over idle a launch is `energy.json` > `board.j_per_solve`; J with the card at rest a launch is `board.j_per_solve_total` (E189.md 8.1).
Every pass also carries the die flag above, and every ledger pass the reducer's note that the host's share uses the whole process's CPU
time (an upper bound). Five passes (two of copy, random, two of sort, sorted and one of sparse parity; each pass's `energy.json` > `flags`
names it) carry the reducer's note of one busy board reading at idle, which it reports as moving its catalogue cross-check (about 3-4% low), not the
headline.

## Registered against happened

| item | registered (E189.md, the kit) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry3 card 0, 600 MHz as found, reads only | card 0; 600 MHz in 9,436 of 9,436 samples; TDP 0 W / 65 °C / 600 MHz at both ends; nothing set |
| card time | about 95 card-minutes, cap 110 (no pass after 108) | 15.77 card-minutes; the cap never bound |
| passes | 24 (four rounds of the six configurations) | 24 ran, 24 reduced ok, 0 set aside |
| order | `plan-e189.json`, never re-drawn | as written, all four rounds |
| launches K | `plan-e189.json` | as planned in 16 passes; 7 of 8 in all 8 copy passes (the host's budget: SHORT) |
| die gate and band | gate at 60 °C, at most 10 minutes; forecast band 52-60 °C | the gate never waited; every pass started at 49-51 °C, below the band (flagged, scored given its own T0) |
| stops | board 65 W, `minshire[0]` 70 °C, the clock off 600 MHz | none tripped (41.77 W, 53 °C; no sample off the clock) |
| stop-path test and smoke | before any pass; a failed smoke ends the session | passed; all 8 smoke runs ok |
| idle anchors | three of 2 minutes | three, each whole |
| the counters arm | dropped by the kit's dated note before any datum | not run |
| builds | at most two starts a Pacific day; kernels by their hashes, hosts by their behaviour | one start (20:10:06-20:10:16 PST on the box); both kernels at their pinned hashes (ledger `78708041...` / `.text` `5e00e45a...`; sparse parity `65dd07da...` / `3e14be32...`); both hosts HOST-BEHAVIOUR OK |
| the rest | at least 40 minutes after our last real session on the card | 1,655 minutes since E183's session end (Fri 13 Nov 2026, 16:36:43 PST) |
| the window | alone: last start G+1:30, last end G+3:30 | last start 21:35, last end 23:35 PST (Departures, 6); launched 20:11:44, ended 20:27:30 |
| the host's package counter | not read unless his go allows it | not read |
| the post | the day's ONE post, 'for 2 h' | none: waived by the owner (Departures, 4) |

## Departures and notes (dated Sat 14 Nov 2026, PST; each set by his go and the round's brief before the session, written here after the collection and before the scorer ran)

1. **The go.** Asked today at about 14:44 PST, "May E189 run on aifoundry3 card 0 today (about 95 card-minutes, 600 MHz as found, reads
   only), followed by E191/E192/E193 as each becomes ready — and how should today's Discord claim post be handled?", the owner answered
   "Yes, but I'll post on Discord" (about 14:50). The registered defaults held unchanged: E189 FULL on aifoundry3 card 0, 600 MHz as found,
   reads only, about 95 card-minutes, cap 110.
2. **The host's package counter: not read** (the default; his go did not allow it): step 9 ran without `--rapl-allowed`, and the host's
   share stays assumed and labelled so.
3. **The fresh network-access approval for aifoundry3 that E189.md section 13 names: nothing to name.** The session was orchestrated from
   aifoundry2, a lab box that reaches aifoundry3 without that check. The kit's login-link stop stayed live (an exit 11 with its lock line
   ends the day's box steps); no step met a login link.
4. **The post: waived.** Asked next to post the day's claim, the owner answered "it's fine not to announce, the cards are unused". No post
   was made, so no release line either. Every other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder
   rule: FREE at 20:09:50), step 7's reads (et-who clean at 20:10:49), the card's lock held by the session to its end, the runner's holder
   read before every pass, `timeout 10` a host process.
5. **The day moved.** E189 was registered and kitted for Fri 13 Nov 2026's plan; its card lane had written only helper scripts when
   aifoundry2, the box that orchestrates it, went down abruptly at about 16:53 PST that day, before any step of the day ran (no booking, no
   box call, no card). It ran on Sat 14 Nov 2026 instead, orchestrated by a new session of the round, on the owner's go above.
6. **G and the window.** E189.md section 13 counts the window from his go at G. His go came at about 14:50 PST without a window time; the
   round read G as the moment the card lane held the round's booking of aifoundry3, **20:04:17 PST**, as the plan for Friday had. The window
   took the form "alone": last start G+1:30 = 21:34:17 and last end G+3:30 = 23:34:17, each rounded up to the next whole minute because
   step 1 takes whole minutes: **21:35 and 23:35 PST**, inside the Pacific day 2026-11-14 (written by step 1 at 20:09:04). E183's second
   session had ended at 16:36:43 PST on Fri 13 Nov 2026, so E189's 40-minute rest was long met: step 9's rest rule read 1,655 minutes.
7. **The desk.** aifoundry2 (Linux) ran every desk step under `/usr/bin/python3` 3.12.3, where E189.md and KIT.md name 3.9 and 3.13; the
   self-tests' verdicts are the same (the readiness check before the day).
8. **Notes, not departures.** Step 10's wait looks for the session by the name `session_e189.sh`, which is the script step 9 launched; it
   was read before step 9 (two calls: running at 20:20:44, ended with 178 files in its manifest at 20:27:32). No pass read `host rc 124`. The
   card time came in far under the estimate: the die gate never waited, and the counters arm's 6 minutes and the 20-minute margin went
   unused.

## Device commands sent

Reads only. The session sent `ettelem config` at its start and end and `ettelem sample --every-ms 100` (no `--reset-ms`) through E128's guard,
which passes `config` and `sample` only; the two hosts opened the card's ops node only. The device-command audit (`dmcmd_audit.py` through
`preflight_e189.sh`) read **GO, 11 send sites, 0 disallowed, every one a READ** at step 2 on the desk and again on the box after the build.
Step 7's config read before the session (20:10:49 PST) was the same read. No set of any kind (TDP, threshold, clock, voltage), no reset, no
statistics reset, no firmware-revisions query, no power cycle.

## Privacy and the public-text scan

The collector's scrub ran (the box's home path became `~`, and no home-directory path is left in any file, the text inside every `.gz`
included), and k6's desk-path gate read CLEAN over the 229 files it read. The public-text scan before the commit read every text file of
this directory, the text inside every `.gz` file and this README, with the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its
fixed list and the local privacy table) plus the private-network, Mac-home, scratch and e-mail patterns, and the round's classes over this
README (names under NDA, logins and home paths, private links, access words). Its only hits in the collected files are the unchanged reducer's own fixed note
on the host's package power, one in each pass's `energy.json` (24), which the sanitizer's pattern for administrator words matches: the
lab's public reducer text (`energy_reduce.py`, its line 427), kept as collected. This README's first draft hit twice, on its own words
about the network check and about home paths, reworded before the commit.

## Files

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E189.md 8.1): `telemetry.jsonl.gz` (the session's samples over the pass), `host.json` (the reducer's input: the ledger host's line through the adapter, or sparse parity's own line), `host-raw.json` (the ledger host's own line), `host.err`, `run.json` (energy.sh's marks), `pass.json` (the runner's marks), `energy.json` and `energy.txt` (the reducer's output, its `dir` set to this path) |
| `session/` | the session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`), scrubbed: `session.log`, `queue.json`, `config-start.json`, `config-end.json`, `etwho-before.txt`, `stop-path.json`, `anchors.json`, `smoke/<run>/` (`stdout.txt`, `host.err`, `smoke.json`), `sampler.err`, `telemetry.jsonl.gz` (the whole session), `runner.out`, `runner.rc`, `MANIFEST.sha256` |
| `SHA256SUMS` | the collector's (`collect_e189.py`, 228 files): it pins every file but this README and itself |

## Next

The frozen scorer, after this commit only: `rb/s24_score_e189.sh` runs `score_e189.py` (registered, unchanged) on this committed directory
and writes `scores-e189.json` (the four rules' words, PASS, FAIL or NOT DECIDED, and each configuration's errors); a later lane commits it
beside this directory. E188 waits for this day's verdict.

SPDX-License-Identifier: Apache-2.0
