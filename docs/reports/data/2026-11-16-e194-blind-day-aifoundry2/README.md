# E194: the blind day on aifoundry2 card 0, Mon 16 Nov 2026 - all 24 registered passes ran in one session of 15.54 card-minutes under the card's own governor, reads only, no stop line tripped, the clock rule ok in all 24, four passes SHORT by the host's own budget (copy random, 7 of 8 launches each), none a failed run; the frozen scorer runs after this commit

*Mon 16 Nov 2026 (week 47), PST, Q191's card lane `card-e194`, run from aifoundry2 itself. Registered in `b6ef1ad3`
([`E194.md`](../../../../tools/claims-v3/e194/E194.md), with its dated note 1
[`E194.md.dated-note-1.md`](../../../../tools/claims-v3/e194/E194.md.dated-note-1.md)), kitted in `f01e1cb2`
([`KIT.md`](../../../../tools/claims-v3/e194/KIT.md)), the card's firmware read of record committed in `15cb0fcb`
(`docs/reports/data/2026-11-15-e194-fwread-aifoundry2/`, EQUAL to E69's), and E194.md's dated amendment A1 with the kit's and the brief's
dated notes 1 landed in `04b6f022` ([`E194.md.dated-amendment-A1.md`](../../../../tools/claims-v3/e194/E194.md.dated-amendment-A1.md),
[`KIT.md.dated-note-1.md`](../../../../tools/claims-v3/e194/KIT.md.dated-note-1.md),
[`CARD-LANE-BRIEF.md.dated-note-1.md`](../../../../tools/claims-v3/e194/CARD-LANE-BRIEF.md.dated-note-1.md)), all before any E194 datum.
The session, T0 1794818007 = 00:33:27 PST, ran to its `session end` at 00:49:00 PST: **15.54 card-minutes** from its first card command,
against the registered estimate of about 95 and the cap of 110. All 24 passes ran in `plan-e194.json`'s order with the clock rule's live
reading "the clock ok" in every one: 20 PASS, and the four copy random passes **SHORT (7 of 8 launches, the host's own budget: scored on its
launches)**. Reads only; nothing set. **The day's post: the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST** ("don't worry
about discord post, just use the machines, nobody is using them"; Departures 5).*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold, band and
rule is **registered** (E194.md, its note 1, A1, `plan-e194.json`, `forecast-e194.json`). The per-configuration means are **desk arithmetic of
the measured passes** (each configuration's four `energy.json` records): **they are not verdicts**, and no forecast is set beside them here.
The idle-anchor die readings and the session's clock counts below are **post hoc** desk readings of the collected telemetry. The four rules'
words are the frozen scorer's (`score_e194.py`, unchanged), which runs only on this directory once it is committed (`rb/s24_score_e194.sh`);
its output, `scores-e194.json`, is committed beside this directory by a later lane. Nothing here changes a frozen number. The desk steps ran
under `/usr/bin/python3` 3.12.3 on aifoundry2.

## What ran (measured)

- **Card:** aifoundry2 card 0 under its governor **as found**. `ettelem config` through the kit's guard at the session's start (00:33:27) and
  end (00:49:00): TDP 65 W, threshold 65 C, power state 3 (`low_power`), 600 MHz at rest, `minion_mv` 519, the same at both ends. **Nothing
  was set.** `since_reset_ms` -1 in every one of the session's 9,309 samples (00:33:27.9-00:49:00.0 PST): no statistics reset.
- **The clock (E194.md 8.2, 11):** of the 9,309 samples, 8,208 read 600 MHz, 47 read 700 MHz and 1,054 read 800 MHz (post hoc count).
  **THE CLOCK RULE's live reading, pass by pass:** "the clock ok" in **24 of 24** passes, on 16-58 live samples in each burst's window from
  its first launch's start + 1.5 s to its last launch's end (the counts are in the pass table); `queue.json` > `off_clock_passes` and
  `unread_clock_passes` are empty: **no pass set aside by the clock, no second off-clock pass, no window without a live sample.** The idle
  samples read 600 MHz (all 1,198 samples of each idle anchor; read, not checked). The reducer's hard line "minion clock in busy samples:
  [...] MHz (the governor moved it)" lists [800], [700, 800] or [600, 700, 800] MHz (its busy window opens at lo + 0.5 s, before the rule's
  1.5 s climb allowance) and is read by THE CLOCK RULE, not as a failure (E194.md 8.2): it is **the only hard line** in each of the 24
  `energy.json` records (`ok` false for that line alone). The rule's second half, the last launch's own cycles over its wall seconds at
  780-810 MHz, is the scorer's reading (`read_pass()`), after this commit.
- **The identity lines, as the session log reads them:**
  - `config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 519 (read, nothing set); identity (a): /dev/et0_mgmt, device ID 0, minion_mv between 450 and 600`;
  - `identity (b): et-who with the sampler running: ours on card 0 2 (on /dev/et0_mgmt 1), ours off card 0 0, another login's 0; the sampler holds /dev/et0_mgmt only`;
  - the smoke hosts: `ledger-selftest` "no device (the self-test)"; the seven others "card 0";
  - every pass's host: `run.json` > `identity` reads `stderr_targets` [`/dev/et0_ops`], `stderr_ids` [0], `nodes_held` [`/dev/et0_ops`],
    `right` true, in 24 of 24;
  - `config end: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 519; its identity card 0`.
  THE IDENTITY GATE passed: `queue.json` > `identity_ok` true. THE REBOOT GATE (A1): the host booted 2026-11-13 16:53:28 PST, before the
  firmware read of record of 2026-11-15 15:22:02 PST: ok (steps 4 and 9 v2).
- **Card session:** T0 1794818007 = 00:33:27 PST to its `session end` at 00:49:00 PST; from the first card command (00:33:27.952) to the close
  (00:49:00.202): **932.25 s, 15.54 card-minutes**. The cap's end (`queue.json` > `end_bound_ms`: 02:23:27.952 PST) and the window's last end
  (03:34 PST) were never reached. **The runner's exit status: `runner.rc` 0** (an ordinary end; `runner.out` ends with the closing config
  read and `session end`).
- **The sequence, as registered:** the box check passed (aifoundry2, `ET_DEVICES` and `V3_DEVICE` unset, the reader at its pin, today's builds
  by `build_e194.sh`, each host and kernel at its build record's sha256 with the kernel gate's OK); the start config read and identity (a);
  the sampler (attempt 1, every 100 ms); identity (b); **the stop-path test passed** (the board, die, board-85x3 and die-80-or-latch lines
  each tripped on live samples within 0.3 s and each refused a start; the clock rule read the live samples); the ramped smoke, **all 8 runs
  ok** (the ledger's self-test; the copy at 64 MiB random and zeros, then 1 GiB random; SHA-256; the sort shuffled and sorted; sparse
  parity's instance once), `smoke gate passed` at 00:33:33; idle anchor 1 (00:33:33-00:35:33), passes 1-12 (00:35:33-00:40:16), idle anchor
  2 (00:40:16-00:42:16), passes 13-24 (00:42:16-00:47:00), idle anchor 3 (00:47:00-00:49:00), each anchor whole (`anchors.json`); `the
  counters arm: DROPPED by E189's kit (its KIT.md section 5; E194.md 7): not run`; the closing config read; `session end`.
- **The host's line, read by reassembly for every host process:** `run.json` > `host_line` and `smoke.json` > `host_line` read method
  "whole line", 0 dropped spans and 0 runtime lines in all 24 passes and all 7 device smoke runs (the ledger's self-test: "the self-test's
  lines (no JSON)"). **No runtime line was printed inside or beside a host's line on aifoundry2's runtime**, as expected; no line went unread,
  and no pass is a FAILED RUN.
- **All 24 passes ran in the registered order** (`plan-e194.json`, never re-drawn). 20 ran their K launches with host status PASS and reading
  PASS. **The four copy random passes (4, 8, 16, 23) each ran 7 of 8 launches: host rc 1, status FAIL, reading "SHORT (7 of 8 launches, the
  host's own budget: scored on its launches)"**, the reducer's flags "host status FAIL (reps: 7 of 8 done)", "host ran 7 of 8 launches
  (budget)", "host exit code 1". E194.md 8.2: a burst the host's budget cut short is scored on the launches it ran and flagged SHORT. None
  set aside (`queue.json` > `set_aside` empty).
- **No stop line tripped** (`queue.json` > `stop` null, `stop_events` empty). The highest live readings: **64.59 W board** (00:39:00.2, during
  pass 9, sparse parity p2: 0.41 W under E189's 65 W line; no sample at or above 65 W, none above 85 W), **55 C `minshire[0]`** (first at
  00:38:59.8, the same pass) and **58 C on the latch `minshire[2]`** (00:39:00.3), against the stops 65 W and 70 C (E189's) and 85 W on 3
  samples and 80 C (aifoundry2's). The registered predicted peaks were 47.9 W at the points and 68.5 W at the bands' top.
- **The die gate never waited** (`pass.json` > `die_gate_wait_s` 0 in all 24). Every pass started at 47-50 C by the runner's live sample
  (inside the forecast band 46-57 C; no pass flagged); T0 (`die_c.before`) 47.0-50.0 C.
- **No climb while idle** (post hoc, the session telemetry): `minshire[0]` read 48 C at the start and the end of idle anchor 1, 50 then 47 C
  across anchor 2, 49 then 48 C across anchor 3; the board averaged 22.39-22.48 W in the anchors. (This card ran away thermally while idle in
  October, before its fan bracket of 9 Oct; nothing like it here.)
- **The holder rule's re-reads at the start:** `queue.json` > `holder_reads_at_start` one read (00:33:27.952), no transient holder. **No BOUND
  line** (`bound` empty; `lock_released_with_bound_host_alive` false), **no early stop** (`early_stop` null; no stop file, no signal), **no
  "the sampler is not live" line** (`sampler_lines_not_live` 0, `sampler_lines_unreadable` 0, `passes_sampler_not_live` empty), no restart
  of the sampler. Every pass's `run.json` reads `sampler_live_during_pass` true, `live_gap_s_pass` and `live_gap_s_host` 0.11-0.19 s, and the
  three sample ages 0.00-0.19 s.
- **The host's package counter was not read** (step 9 v2 ran without `--rapl-allowed`; `energy.json` > `rapl` "not read: his go did not
  allow it"); the host's share stays assumed and labelled so.

## The passes (measured; the means are desk arithmetic of the measured passes, not verdicts)

One row a pass, in the order run. J over idle a launch is `energy.json` > `board.j_per_solve`; J with the card at rest a launch is
`board.j_per_solve_total` (E194.md 8.1). t_w, T0 and t_k are the scorer's own measured inputs, by its definitions (`score_e194.py`'s header),
computed here as desk arithmetic of the same records: t_w = 1 / `solves_per_s`; T0 = `die_c.before`; t_k = the slowest minion's cycles of the
burst's last launch / 800 MHz (`host-raw.json` > `hart0_cycles.max` for the ledger programs, `host.json` > `kernel.cycles_max` for sparse
parity). The clock column is the runner's live reading with its sample count.

| # | pass | started (PST) | launches (K) | die at start (runner) / T0, C | J over idle a launch | J with the card at rest a launch | t_w, s | t_k, s | the clock (live samples) | reading |
|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | sparse parity p1 | 00:35:33 | 9 (9) | 48 / 48.0 | 12.738 | 22.392 | 0.4146 | 0.3845 | ok (23) | PASS |
| 2 | SHA-256 p1 | 00:35:55 | 9 (9) | 49 / 49.0 | 5.400 | 13.309 | 0.3454 | 0.3237 | ok (16) | PASS |
| 3 | sort, sorted p1 | 00:36:17 | 8 (8) | 49 / 49.0 | 6.859 | 17.098 | 0.4488 | 0.4195 | ok (21) | PASS |
| 4 | copy, random p1 | 00:36:39 | 7 (8) | 49 / 49.0 | 13.778 | 34.568 | 0.9076 | 0.9065 | ok (48) | SHORT 7 of 8 (host rc 1) |
| 5 | copy, zeros p1 | 00:37:05 | 8 (8) | 49 / 49.0 | 11.579 | 32.504 | 0.9081 | 0.9073 | ok (58) | PASS |
| 6 | sort, shuffled p1 | 00:37:33 | 7 (7) | 49 / 49.0 | 8.749 | 21.258 | 0.5384 | 0.5206 | ok (23) | PASS |
| 7 | copy, zeros p2 | 00:37:55 | 8 (8) | 50 / 49.0 | 12.368 | 33.369 | 0.9075 | 0.9067 | ok (58) | PASS |
| 8 | copy, random p2 | 00:38:22 | 7 (8) | 50 / 49.0 | 13.426 | 34.501 | 0.9079 | 0.9049 | ok (48) | SHORT 7 of 8 (host rc 1) |
| 9 | sparse parity p2 | 00:38:48 | 9 (9) | 50 / 49.0 | 13.204 | 22.782 | 0.4013 | 0.3848 | ok (21) | PASS |
| 10 | sort, shuffled p2 | 00:39:10 | 7 (7) | 50 / 50.0 | 8.894 | 21.545 | 0.5427 | 0.5206 | ok (23) | PASS |
| 11 | sort, sorted p2 | 00:39:33 | 8 (8) | 50 / 50.0 | 7.845 | 17.857 | 0.4321 | 0.4195 | ok (19) | PASS |
| 12 | SHA-256 p2 | 00:39:54 | 9 (9) | 50 / 50.0 | 5.483 | 13.413 | 0.3441 | 0.3237 | ok (16) | PASS |
| 13 | sparse parity p3 | 00:42:16 | 9 (9) | 47 / 47.0 | 12.994 | 22.457 | 0.4070 | 0.3852 | ok (22) | PASS |
| 14 | copy, zeros p3 | 00:42:38 | 8 (8) | 48 / 48.0 | 11.312 | 32.143 | 0.9075 | 0.9066 | ok (58) | PASS |
| 15 | sort, shuffled p3 | 00:43:06 | 7 (7) | 49 / 48.0 | 8.843 | 21.124 | 0.5341 | 0.5206 | ok (23) | PASS |
| 16 | copy, random p3 | 00:43:28 | 7 (8) | 49 / 48.0 | 14.534 | 35.415 | 0.9073 | 0.9053 | ok (49) | SHORT 7 of 8 (host rc 1) |
| 17 | SHA-256 p3 | 00:43:54 | 9 (9) | 49 / 49.0 | 5.493 | 13.462 | 0.3499 | 0.3237 | ok (16) | PASS |
| 18 | sort, sorted p3 | 00:44:16 | 8 (8) | 49 / 48.1 | 6.517 | 17.013 | 0.4574 | 0.4195 | ok (22) | PASS |
| 19 | sort, shuffled p4 | 00:44:38 | 7 (7) | 49 / 48.0 | 8.447 | 21.317 | 0.5600 | 0.5206 | ok (24) | PASS |
| 20 | SHA-256 p4 | 00:45:00 | 9 (9) | 49 / 48.0 | 5.290 | 13.178 | 0.3431 | 0.3237 | ok (16) | PASS |
| 21 | copy, zeros p4 | 00:45:22 | 8 (8) | 49 / 48.0 | 11.275 | 32.134 | 0.9081 | 0.9076 | ok (58) | PASS |
| 22 | sort, sorted p4 | 00:45:49 | 8 (8) | 49 / 48.8 | 7.643 | 17.799 | 0.4444 | 0.4195 | ok (21) | PASS |
| 23 | copy, random p4 | 00:46:11 | 7 (8) | 49 / 48.0 | 13.474 | 34.394 | 0.9079 | 0.9075 | ok (49) | SHORT 7 of 8 (host rc 1) |
| 24 | sparse parity p4 | 00:46:37 | 9 (9) | 49 / 48.8 | 13.347 | 22.711 | 0.3992 | 0.3848 | ok (21) | PASS |

Means a configuration (desk arithmetic of its four passes; not verdicts):

| configuration | passes | J over idle a launch | J with the card at rest a launch | t_w, s | t_k, s |
|---|---:|---:|---:|---:|---:|
| copy, random | 4 (all SHORT, 7 launches each) | 13.803 | 34.719 | 0.9076 | 0.9060 |
| copy, zeros | 4 | 11.634 | 32.537 | 0.9078 | 0.9071 |
| SHA-256 | 4 | 5.417 | 13.341 | 0.3456 | 0.3237 |
| sort, sorted | 4 | 7.216 | 17.442 | 0.4457 | 0.4195 |
| sort, shuffled | 4 | 8.733 | 21.311 | 0.5438 | 0.5206 |
| sparse parity | 4 | 13.071 | 22.586 | 0.4055 | 0.3848 |

## Registered against happened

| item | registered (E194.md, note 1, the kit, A1) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry2 card 0 under its governor as found (600 MHz at rest, 800 MHz under load; TDP 65 W, threshold 65 C), reads only | card 0; 600 / 700 / 800 MHz in 8,208 / 47 / 1,054 of 9,309 samples; TDP 65 W / 65 C / 600 MHz, 519 mV at both ends; nothing set |
| THE CLOCK RULE (8.2, 11) | every busy sample from first launch + 1.5 s to last launch end at 800 MHz; first pass off it set aside, a second stops the session; the last launch's own count 780-810 MHz | "the clock ok" in 24 of 24 by the live samples; none set aside, none unread; the last launch's count is the scorer's |
| the identity gate | the start config names `/dev/et0_mgmt` and device ID 0, `minion_mv` between 450 and 600; et-who with the sampler: ours on card 0 only, one on `/dev/et0_mgmt`; each device-opening host's block card 0 | passed: `/dev/et0_mgmt`, ID 0, 519 mV; ours on card 0 2 (1 on `/dev/et0_mgmt`), off card 0 0, another login's 0; every host card 0 |
| the reboot gate (A1) | the box not booted at or after the firmware read of record (2026-11-15 15:22:02 PST, `15cb0fcb`, EQUAL to E69's) | booted 2026-11-13 16:53:28 PST: ok (steps 2, 4 and 9 v2) |
| card time | about 95 card-minutes, cap 110 from the first card command (no pass after 108) | 15.54 card-minutes (932.25 s); the cap never bound |
| passes | 24, in `plan-e194.json`'s order | 24 ran in that order; 20 PASS, 4 SHORT (copy random, 7 of 8, the host's budget); 0 set aside, 0 FAILED RUN |
| launches K | `plan-e194.json` (copy 8, SHA-256 9, sort sorted 8, sort shuffled 7, sparse parity 9) | as planned in 20; 7 of 8 in each copy random pass |
| the host's line | read by reassembly (fix-e194); a runtime line dropped and named | "whole line" in all 31 device-opening host runs; 0 runtime lines |
| stop-path test and smoke | before any pass; a failed smoke is a gate: no data | the stop-path test passed; all 8 smoke runs ok |
| stops | board 65 W or `minshire[0]` 70 C (E189's); board above 85 W on 3 samples or 80 C on `minshire[0]` or the latch `minshire[2]` (aifoundry2's) | none tripped (64.59 W, 55 C, latch 58 C) |
| predicted peaks | 47.9 W at the points, 68.5 W at the bands' top (under the card's 82 W line) | 64.59 W measured peak |
| die gate and band | gate at 57 C, at most 10 minutes; forecast band 46-57 C | the gate never waited; starts at 47-50 C; T0 47.0-50.0 C |
| idle anchors | three of 2 minutes | three, each whole |
| the counters arm | dropped by E189's kit | not run |
| builds | at most two starts a Pacific day | one start, 00:31:43 PST on the box: ledger and sparse parity built, each KERNEL OK (ledger `.text` `5e00e45a...`, ELF `2b2eb281...`; sparse parity `.text` `3e14be32...`, ELF `6ee70c92...`) |
| the dry pass | on the kit's doubles, no device, rc 0 that day | `E194-DRY rc=0 passes=6 of 6 (each PASS with the clock ok) dry-check=1 identity-lines=2` (00:32:23-00:32:46 PST) |
| the rest | at least 40 minutes after our last real session on this card | 3,368 minutes since E190 arm A's end (Fri 13 Nov 16:24:57 PST) |
| the window (A1-4) | from G = the card lane's booking: last start G+1:30, last end G+3:30, each rounded up; G at 20:29:00 PST or earlier | G 00:03:59 PST: last start 01:34, last end 03:34 (Departures 3); launched 00:33:27, ended 00:49:00 |
| sessions | one of ours on the card; no relaunch | one launch, one session |
| the host's package counter | not read unless his go allows it | not read |
| the post | the day's etiquette (E194.md 13) | waived by the owner (Departures 5) |

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-9 set by his go, A1 and the round's plan before the session; 10-11 after the collection, said so; all written here after the collection and before the scorer ran)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** The go naming E194, at **15:05:27**: "yes, feel free to run it, feel free to read
   firmware as well" (answering whether E194 may run on aifoundry2's own card after Friday's reboot; the round's reading, his to correct).
   At **15:07:01**: "Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware are
   always allowed." At **15:09:49**: "Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which read firmware
   should be fine." Standing: **10:05:42** "continue, all machines are up"; **10:22:36** "don't worry about discord post, just use the
   machines, nobody is using them". For a day after Sun 15 Nov: **17:21:16** "Feel free to use more cards in parallel, I don't need to
   reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used, feel free to
   use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); and "don't worry about hitting the
   limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09). Beside them, a report of
   his words (not his own text), the round's Discussion at 19:34:12: "The aifoundry cards are all free right now (I can see it on the lab
   dashboard's live view, though a collector is running on them); feel free to use them." **The registered items are taken as their
   defaults**: aifoundry2 card 0 under its governor as found, reads only, nothing set; about 95 card-minutes, cap 110; THE IDENTITY GATE;
   his words name no other item.
2. **The card day: Mon 16 Nov 2026**, moved from Sunday by the round's weekly-usage-limit stop at about 18:05 PST Sun 15 Nov (no card was in
   use then; no E194 step had run on the box).
3. **G = the booking (A1-4):** the card lane's `book.sh take aifoundry2 card-e194` printed BOOKED at **00:03:59 PST** Mon 16 Nov: last start
   G+1:30 = 01:33:59 and last end G+3:30 = 03:33:59, each rounded up to the whole minute: **01:34 and 03:34 PST** (`s02_window_e194.sh
   2026-11-16 01:34 03:34`, written by step 1 at 00:12:54; the window file's `RB_GO_EPOCH`, 1794816774 = 00:12:54 PST, is the moment step 1
   wrote it, not his go).
4. **The reboot gate answered by A1's firmware read of record:** the read of Sun 15 Nov 15:22:02 PST (`15cb0fcb`, EQUAL to E69's in all seven
   fields), read by E194's own gate (`rb/fwgate_e194.sh`) in steps 2, 4 and 9 v2: the box's boot (2026-11-13 16:53:28 PST) is before it. The
   session sent no firmware query (A1-6).
5. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim and no release, a departure from E194.md
   13's etiquette sentence. Every other etiquette check stood: the look before the session (et-who, who, uptime, ps, the holder rule: FREE at
   00:31:23), step 7's read (the card free at 00:32:14), card 0's lock held by the session to its end, the runner's holder read, `timeout 10`
   a host process.
6. **The host's package counter: not read** (his words do not name it: E194.md 13's default no): step 9 v2 ran without `--rapl-allowed`.
7. **A fresh network-access approval: nothing to name.** The session ran on aifoundry2 itself, reached by the kit's ssh to the same box. The
   kit's login-link stop stayed live; no step met a login link (`RB_LOCK` unchanged at 70 lines).
8. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names. The
   orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14 Nov 2026 after aifoundry2
   went down abruptly at about 16:53 PST on Fri 13 Nov.
9. **THE QUIET DESK FLAG** (E194.md 13): raised by `card-e194` at **00:13:37**, lowered at **00:49:40** after step 11's COPY-BACK EXACT. THE
   P2 COUNT read **0** before the look (00:31:17, `count --wait`; the look's own read 0 at 00:31:23) and **0** before the launch (00:33:26;
   step 9 v2's own read 0). The round's in-flight wait (a by-hand step of the go lines) found one desk test of another lane of ours begun
   before the raise (a desk test in a no-device sandbox, started 00:09:11), paused by its own quiet-flag wait between cases; that lane
   stopped its own test at 00:30:04, and the wait read 0 at 00:31:12, 17 min 35 s after the raise, inside its 30-minute bound. No device-named
   process or session script of ours ran on the box during the session (the runner read no foreign holder).
10. **Notes, not departures (after the collection).** The four SHORT bursts are the host's own budget, read by the kit as registered (E194.md
    8.2), each scored on its 7 launches by the scorer. The peak board 64.59 W came during sparse parity p2, 0.41 W under E189's 65 W stop
    line. The card time came in far under the estimate: the die gate never waited, and the cap's margin went unused.
11. **One launch, no relaunch;** the dry pass ran on the kit's doubles before it (no device, no card time).

## Device commands sent

Reads only. The session's `commands.jsonl` lists 61 commands, each with `ET_DEVICES` and `V3_DEVICE` unset and card 0's lock
(`/run/lock/etsoc-shire0.lock`): et-who 26 times (no device); `ettelem config` at the start and the end and `ettelem sample --every-ms 100`
(no `--reset-ms`), each through the kit's guard (`ettelem_guard_e194.sh`); the ledger host's self-test (no device); and 31 host runs on the
card (the 7 device smoke runs and the 24 passes: 26 ledger runs, 5 sparse parity runs), each of which opened card 0's ops node only. Step
7's config read before the session (00:32:13-00:32:14 PST) was the same read, with `et-lab-manifest` (sysfs and files only). The
device-command audit (`dmcmd_audit`) read **GO, 16 send sites, 0 disallowed** at step 2 on the desk and again on the box after the build
(step 6's wait); the dry pass's device-command check read 16 device-opening command lines, each with `ET_DEVICES` and `V3_DEVICE` unset,
none naming another card or calling the management service or et-powertop. No set of any kind (TDP, threshold, clock, voltage), no
governor move, no reset, no statistics reset, no firmware-revisions query, no power cycle.

## Privacy and the public-text scan

THE BOX-TREE GATE passed (every path under the box's home in the 209 text files read lies in its tree `~/claude/et-soc1-prototyping/`; no
path in a scratch directory). The collector's scrub ran (the box's home path became `~`, the box login `<login>`), and k6's desk-path gate read
CLEAN over the 259 files it read. The public-text scan before the commit read every text file of this directory, the text inside its 25 `.gz`
files and this README, with the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its fixed list and the local privacy table) plus the
private-network, Mac-home, scratch and e-mail patterns: 231 text files and 25 `.gz` files, **25 hits, every one the sanitizer's pattern for
administrator words on the reducer's fixed note below** (24 in the `energy.json` files, 1 in this README's quotation of it). The round's
classes over this README and the commit message (names under NDA, logins and home paths, private links, access words) matched **2 lines**:
the post platform's name inside the owner's verbatim words of 10:22:36 PST (the title paragraph and Departures 1), kept verbatim as other
committed records quote them; the commit message read 0 lines and 0 sanitizer hits. The round's classes, run also over the collected text
files, matched only words of the card's and the workload's own output, kept as collected: the device layer's identity block's name for the
card's on-chip scratch memory (12 lines in each of 34 files: the 31 hosts' `host.err`, `config-start.err`, `config-end.err` and
`sampler.err`); sparse parity's own field naming its instance's hidden indices (one line in each of 13 files: each pass's `host.json`,
`host-stdout.txt` and `energy.json`, and the smoke run's `stdout.txt`); one hex run inside a sha256 value in `SHA256SUMS` and in
`MANIFEST.sha256`; and byte runs in the 4 binary `host.rec` files.
**The unchanged reducer's fixed note** "assumed package power (RAPL is root-only)" (`energy_reduce.py`) is in every `energy.json` here,
**24 of 24**, kept as collected (a collected file is never edited).

## Files

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E194.md 8.1), 24 directories: `telemetry.jsonl.gz` (the sampler's lines for the pass: THE CLOCK RULE reads their minion clock), `host.json` (the reducer's input: the ledger host's line through the adapter, or sparse parity's own line, as read), `host-raw.json` (the ledger programs: the host's own line as read by reassembly, which the frozen scorer reads), `host-stdout.txt` (the host's raw standard output, kept), `host.rec` (sparse parity's records, binary), `host.err` (the host's stderr: its identity block), `run.json` (the runner's record: identity, sampler liveness, `host_line`, the clock rule), `pass.json` (the pass's reading: K, die at start, die-gate wait, host rc and status, reading, clock rule), `energy.json` and `energy.txt` (the unchanged reducer's output) |
| `session/` | the session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`: its 207 files, plus `runner.rc`), scrubbed: `session.log` and `runner.out` (the session's lines), `runner.rc` (0), `queue.json` (the queue, `identity_ok` true, no stop, bound or early stop), `identity.json` (the identity gate's readings), `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err` (the closing and opening config reads), `etwho-before.txt`, `etwho-identity.txt` (et-who before the session and with the sampler running), `commands.jsonl` (every command the session sent), `stop-path.json` (the stop-path test), `anchors.json` (the three idle anchors), `sampler.err`, `telemetry.jsonl.gz` (the whole session's samples), `MANIFEST.sha256` |
| `session/smoke/<run>/` | the 8 smoke runs: `stdout.txt` (the host's standard output, raw), `host.err` (the host's stderr), `smoke.json` (the runner's reading, with the reader's record `host_line`) |
| `SHA256SUMS` | the collector's (`collect_e194.py`, 257 files): every file but this README, itself and `FILES.txt` |
| `FILES.txt` | the collector's list of every collected file, by path (257) |

## Next

The frozen scorer, after this commit only: `rb/s24_score_e194.sh` runs `score_e194.py` (registered in `b6ef1ad3`, unchanged) on this committed
directory alone and writes `scores-e194.json` (the four rules' words, E194-S1, S1T, S2 and S2T, with PASS, FAIL, NO DATA or NOT DECIDED, and
each configuration's errors); a later lane commits it beside this directory.

SPDX-License-Identifier: Apache-2.0
