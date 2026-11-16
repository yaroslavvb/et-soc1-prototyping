# E191: the blind day on aifoundry1 card 1, Mon 16 Nov 2026 - the third session (E191.md's dated amendment A2), a REPEAT: its scorer output REPORTED beside the registered verdicts, which are the second session's; all 24 registered passes ran in one session of 15.84 card-minutes, reads only, no stop line tripped, none SHORT and none a failed run; the frozen scorer runs after this commit

*Mon 16 Nov 2026 (week 47), PST, Q191's card lane `card-e191c`, orchestrated from aifoundry2. Registered in `300d76e4`
([`E191.md`](../../../../tools/claims-v3/e191/E191.md)), its dated note 1 `8c8f825f`
([`E191.md.dated-note-1.md`](../../../../tools/claims-v3/e191/E191.md.dated-note-1.md)), kitted in `eb1ac923`
([`KIT.md`](../../../../tools/claims-v3/e191/KIT.md)), the kit's dated note 2 with E191.md's dated amendment A1 landed in `2d0fe517`
([`KIT.md.dated-note-2.md`](../../../../tools/claims-v3/e191/KIT.md.dated-note-2.md),
[`E191.md.dated-amendment-A1.md`](../../../../tools/claims-v3/e191/E191.md.dated-amendment-A1.md)), and E191.md's dated amendment A2 with
the kit's dated note 3 and the brief's dated note 2 landed in `318a0985`
([`E191.md.dated-amendment-A2.md`](../../../../tools/claims-v3/e191/E191.md.dated-amendment-A2.md),
[`KIT.md.dated-note-3.md`](../../../../tools/claims-v3/e191/KIT.md.dated-note-3.md),
[`CARD-LANE-BRIEF.md.dated-note-2.md`](../../../../tools/claims-v3/e191/CARD-LANE-BRIEF.md.dated-note-2.md)), all before any datum of this
session. The session, T0 1794816854 = 00:14:14 PST, ran to its `session end` at 00:30:05 PST: **15.84 card-minutes** from its first card
command, against the registered estimate of about 95 and the cap of 110. All 24 passes ran in `plan-e191.json`'s order, each with its K
launches, host status PASS and reading PASS, and all 24 reduced with the reducer's hard checks passed. Reads only. **A REPEAT (A2-1):**
E191's registered verdicts are the second session's (`7156ac15`, its scorer output committed in `f74c81e3`) and they stand; this session's
scorer words are REPORTED beside them, never verdicts and never pooled with the second session's passes. **Departures, dated and set before
the session (Departures 1-10):** the go is the owner's standing words of Sun 15 Nov 2026 with his "Try again", the registered items as their
defaults; the card day is Mon 16 Nov 2026, moved from Sunday by the round's stop, with G3 = this lane's booking of aifoundry1, 00:00:41 PST;
the post was waived by the owner, his words of Sun 15 Nov 2026 10:22:36 PST; the host's package counter was not read; there is no
network-access approval to name from aifoundry2; the desk was aifoundry2 under `/usr/bin/python3` 3.12.3; the orchestrator was the round's
session on its yvb3 account. **Not blind to the second session's data** (A2's own label: A2 was written after `7156ac15` and `f74c81e3`); the
frozen forecasts (`300d76e4`) are blind to every E191 datum.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold, band and
rule is **registered** (E191.md, its note 1, A1, A2, `plan-e191.json`, `forecast-e191.json`). The per-configuration means in the second table
are **desk arithmetic of the measured passes** (each configuration's four `energy.json` records): **they are not verdicts**, and no forecast
is set beside them here. Three readings are marked **post hoc** (desk readings of the collected files after the collection): where the
runtime's line sits in each raw `stdout.txt`, the die notes under the pass table, and the power-state note in Departures 12. The four rules'
words are the frozen scorer's (`score_e191.py`, unchanged), which runs only on this directory once it is committed
(`rb/s24_score_e191_v3.sh`), with A2's repeat reading beside the registered verdicts; its outputs are committed beside this directory by a
later lane, REPORTED. Nothing here changes a frozen number. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## What ran (measured)

- **Card:** aifoundry1 card 1, **600 MHz in all 9,492 samples** of the session's 10 Hz telemetry (00:14:15.199-00:30:05.632 PST; none
  without a clock reading, none off 600 MHz: `queue.json` > `off_clock` is empty). `ettelem config` through the kit's guard at the session's
  start (00:14:15) and end (00:30:05): TDP 65 W, threshold 65 C, power state 1 (`managed_power`), 600 MHz, `minion_mv` 499, the same at both
  ends. **Nothing was set.** `since_reset_ms` -1 in every sample: no statistics reset.
- **The identity lines, as the session log reads them:**
  - `config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499 (read, nothing set); identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510`;
  - `identity (b): et-who with the sampler running: ours on card 1 2 (on /dev/et1_mgmt 1), ours on card 0 0, another login's 0; the sampler holds /dev/et1_mgmt only`;
  - the smoke hosts: `ledger-selftest` "no device (the self-test)"; the seven others "card 1";
  - every pass's host: its `run.json` > `identity` reads the node held `/dev/et1_ops`, its stderr's target `/dev/et1_ops` and its physical
    device ID 1, `right` true in 24 of 24;
  - `config end: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499; its identity card 1`.
  THE IDENTITY GATE (note 1, item 3) passed: `queue.json` > `identity_ok` true.
- **Card session:** T0 1794816854 = 00:14:14 PST to its `session end` at 00:30:05 PST; from the first card command (00:14:15.180) to the
  close (00:30:05.828): **950.6 s, 15.84 card-minutes**. The cap's end (`queue.json` > `end_bound_ms`, 110 minutes from the first card
  command: 02:04:15.180 PST) and the window's last end (03:31 PST) were never reached. `runner.rc` 0.
- **The sequence, as registered:** the box check passed (aifoundry1, `ET_DEVICES=1`, the reader at its pin, the day's builds by
  `build_e191.sh` with the `ET_DEVICES` reading passed, each host and kernel at its build record's sha256 with the kernel gate's OK); the
  start config read and identity (a); the sampler (attempt 1, every 100 ms); identity (b); **the stop-path test passed** (the board, die and
  clock lines each tripped on live samples within 0.2 s and each refused a start); the ramped smoke, **all 8 runs ok** (the kit's smoke, as
  in the second session: `ledger-selftest`, `copy-64m-random`, `copy-64m-zeros`, `copy-1g-random`, `sha256-b2048-r1`, `sort-shuffled-r1`,
  `sort-sorted-r1`, `sparse-parity-r1`), `smoke gate passed` at 00:14:20; idle anchor 1 (00:14:20.2-00:16:20.2), passes 1-12
  (00:16:20-00:21:12), idle anchor 2 (00:21:12.9-00:23:12.9), passes 13-24 (00:23:13-00:28:05), idle anchor 3 (00:28:05.7-00:30:05.7), each
  anchor whole (`anchors.json`); `the counters arm: DROPPED by E189's kit (its KIT.md section 5; E191.md 7): not run`; the closing config
  read; `session end`.
- **The host's line, read by kit note 2's reader for every host process.** Each of the 31 device-opening host runs (7 smoke runs and 24
  passes) printed exactly one runtime line, `Opening device 1`, on its standard output. Runner v2 dropped it and read the host's line with
  its own fields verified: `smoke.json` > `host_line` and `run.json` > `host_line` read `runtime_lines` ["Opening device 1"], `json_lines`
  1, `other_lines` 0 and an empty `why` in all 31, and each of the seven device smoke lines reads "the host's line: 1 runtime line(s)
  dropped (Opening device 1)". The ledger's self-test printed no runtime line. **No host's line went unread:** no pass carries the flag "the
  host's line was not read", and none is a FAILED RUN. Post hoc (a desk reading of the collected `stdout.txt` files): in each of the 26 ledger
  host runs the runtime's text sits at the end of the host line's first part, splitting the line in two, as it did in the first and second
  sessions; in each of the 5 sparse parity runs it is a line of its own before the host's line.
- **All 24 passes ran in the registered order** (`plan-e191.json`, never re-drawn; the same order as the second session's), **each with its
  K launches** (copy 8, SHA-256 9, the sorts 8 and 7, sparse parity 9), host status PASS and reading PASS: **none SHORT, none a FAILED RUN,
  none set aside** (`queue.json` > `set_aside` empty). **All 24 reduced with the reducer's hard checks passed** (`energy.json` > `ok` true,
  `hard` empty; the reducer is energy.sh's `energy_reduce.py`, unchanged).
- **No stop line tripped.** The highest live readings were **52.27 W board** (00:18:12.7, during pass 5, sparse parity p1) and **57 C
  `minshire[0]`** (00:18:10.7, during pass 5), against the stops 65 W and 70 C. For scale, used by no rule: the registered prediction was
  about 47-50 W, and the second session's peaks were 50.57 W and 55 C.
- **The die gate never waited** (`pass.json` > `die_gate_wait_s` 0 in all 24). By the runner's live sample every pass started at 53-55 C,
  inside the forecast band (52-60 C): no pass carries the runner's flag "T0 below the forecast band". Each pass is scored given its own T0.
- **No BOUND line** (`queue.json` > `bound` empty; `lock_released_with_bound_host_alive` false), **no early stop** (`early_stop` null; no
  stop file, no signal), **no "the sampler is not live" line** (`sampler_lines_not_live` 0; `passes_sampler_not_live` empty), no restart of
  the sampler. Every pass's `run.json` reads `sampler_live_during_pass` true, `live_gap_s_pass` and `live_gap_s_host` 0.10-0.11 s, and the
  three sample ages (at the host's start, at its end, at the pass's end) 0.00-0.10 s.
- **The host's package counter was not read** (step 9 v3 ran without `--rapl-allowed`; `run.json` > `rapl` "not read: his go did not allow
  it" in 24 of 24); the host's share stays assumed and labelled so.

## The passes (measured; the means are desk arithmetic of the measured passes, not verdicts)

One row a pass, in the order run. J over idle a launch is `energy.json` > `board.j_per_solve`; J with the card at rest a launch is
`board.j_per_solve_total` (E191.md 8.1). t_w, T0 and t_k are the scorer's own measured inputs, by its definitions (`score_e191.py`'s
header), computed here as desk arithmetic of the same records: t_w = 1 / `solves_per_s`; T0 = `die_c.before`; t_k = the slowest minion's
cycles of the burst's last launch / 600 MHz (`host-raw.json` > `hart0_cycles.max` for the ledger programs, `host.json` > `kernel.cycles_max`
for sparse parity).

| # | pass | started (PST) | launches (K) | die at start (runner) / T0 (`die_c.before`), C | J over idle a launch | J with the card at rest a launch | t_w, s | t_k, s | reading | flags |
|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | copy, zeros p1 | 00:16:20 | 8 (8) | 54 / 54 | 6.214 | 34.535 | 0.9094 | 0.9078 | PASS | reducer: 2 of 44 busy board_w readings at idle (catalogue cross-check only) |
| 2 | SHA-256 p1 | 00:16:47 | 9 (9) | 54 / 54 | 2.714 | 16.225 | 0.4332 | 0.4316 | PASS |  |
| 3 | sort, sorted p1 | 00:17:10 | 8 (8) | 54 / 54 | 3.733 | 21.236 | 0.5607 | 0.5593 | PASS |  |
| 4 | copy, random p1 | 00:17:32 | 8 (8) | 54 / 54 | 8.487 | 36.908 | 0.9092 | 0.9078 | PASS |  |
| 5 | sparse parity p1 | 00:18:00 | 9 (9) | 54 / 54 | 8.793 | 25.193 | 0.5147 | 0.5134 | PASS | reducer: 1 of 27 busy board_w readings at idle (catalogue cross-check only) |
| 6 | sort, shuffled p1 | 00:18:23 | 7 (7) | 55 / 54.9375 | 4.075 | 26.103 | 0.6956 | 0.6942 | PASS |  |
| 7 | SHA-256 p2 | 00:18:46 | 9 (9) | 54 / 54 | 2.581 | 16.197 | 0.4332 | 0.4316 | PASS |  |
| 8 | copy, random p2 | 00:19:09 | 8 (8) | 54 / 54 | 8.374 | 36.871 | 0.9091 | 0.9072 | PASS |  |
| 9 | sort, sorted p2 | 00:19:36 | 8 (8) | 54 / 54 | 3.605 | 21.207 | 0.5609 | 0.5593 | PASS |  |
| 10 | sparse parity p2 | 00:19:59 | 9 (9) | 54 / 54 | 8.894 | 25.238 | 0.5142 | 0.5131 | PASS | reducer: 1 of 27 busy board_w readings at idle (catalogue cross-check only) |
| 11 | sort, shuffled p2 | 00:20:22 | 7 (7) | 55 / 54 | 3.746 | 25.831 | 0.6954 | 0.6942 | PASS | reducer: catalogue cross-check off the headline by more than 6% |
| 12 | copy, zeros p2 | 00:20:45 | 8 (8) | 54 / 54 | 6.176 | 34.614 | 0.9090 | 0.9058 | PASS | reducer: 1 of 42 busy board_w readings at idle (catalogue cross-check only) |
| 13 | sort, shuffled p3 | 00:23:13 | 7 (7) | 53 / 53 | 4.352 | 25.773 | 0.6957 | 0.6942 | PASS |  |
| 14 | copy, zeros p3 | 00:23:36 | 8 (8) | 53 / 53 | 6.125 | 34.202 | 0.9086 | 0.9075 | PASS | reducer: 1 of 41 busy board_w readings at idle (catalogue cross-check only) |
| 15 | copy, random p3 | 00:24:03 | 8 (8) | 53 / 53 | 8.160 | 36.528 | 0.9091 | 0.9064 | PASS |  |
| 16 | sparse parity p3 | 00:24:30 | 9 (9) | 54 / 53.9062 | 8.880 | 25.135 | 0.5147 | 0.5123 | PASS | reducer: 1 of 27 busy board_w readings at idle (catalogue cross-check only) |
| 17 | SHA-256 p3 | 00:24:53 | 9 (9) | 54 / 54 | 2.382 | 16.096 | 0.4333 | 0.4316 | PASS |  |
| 18 | sort, sorted p3 | 00:25:16 | 8 (8) | 54 / 54 | 3.678 | 21.208 | 0.5610 | 0.5593 | PASS |  |
| 19 | SHA-256 p4 | 00:25:39 | 9 (9) | 54 / 54 | 2.707 | 16.174 | 0.4332 | 0.4316 | PASS |  |
| 20 | sort, shuffled p4 | 00:26:02 | 7 (7) | 54 / 53.6562 | 4.311 | 25.931 | 0.6956 | 0.6942 | PASS |  |
| 21 | sort, sorted p4 | 00:26:25 | 8 (8) | 54 / 53.0625 | 3.459 | 20.973 | 0.5607 | 0.5593 | PASS |  |
| 22 | copy, random p4 | 00:26:48 | 8 (8) | 54 / 53 | 8.103 | 36.577 | 0.9094 | 0.9078 | PASS | reducer: 1 of 44 busy board_w readings at idle (catalogue cross-check only) |
| 23 | copy, zeros p4 | 00:27:15 | 8 (8) | 54 / 54 | 6.332 | 34.569 | 0.9091 | 0.9078 | PASS |  |
| 24 | sparse parity p4 | 00:27:42 | 9 (9) | 54 / 54 | 8.916 | 25.147 | 0.5144 | 0.5122 | PASS |  |

| configuration | passes reduced ok | launches a pass (K registered) | J over idle a launch, mean of 4 (min-max) | J with the card at rest a launch, mean of 4 (min-max) |
|---|---:|---|---|---|
| copy, zeros (`--bytes 1G --passes 14 --data zeros --width 32`) | 4 of 4 | 8 (8) | 6.211 (6.125-6.332) | 34.480 (34.202-34.614) |
| copy, random (`--bytes 1G --passes 14 --data random --width 32`) | 4 of 4 | 8 (8) | 8.281 (8.103-8.487) | 36.721 (36.528-36.908) |
| SHA-256 (`--block 2048 --repeat 800`, with `--expect`) | 4 of 4 | 9 (9) | 2.596 (2.382-2.714) | 16.173 (16.096-16.225) |
| sort, sorted (`--keys 512 --reps 1800 --order sorted`) | 4 of 4 | 8 (8) | 3.619 (3.459-3.733) | 21.156 (20.973-21.236) |
| sort, shuffled (`--keys 512 --reps 1800 --order shuffled`) | 4 of 4 | 7 (7) | 4.121 (3.746-4.352) | 25.910 (25.773-26.103) |
| sparse parity (the registered instance: `--n 544 --k 4 --eta 0.39 --m 1792 --seed 3`) | 4 of 4 | 9 (9) | 8.871 (8.793-8.916) | 25.178 (25.135-25.238) |

Notes on the table. Post hoc: the reducer's `die_c.before` (the scorer's T0) reads below the runner's start sample in passes 6, 11, 16, 20,
21 and 22 (by 0.06-1 C); every T0 is 53.0-54.9 C, inside the band. Every ledger pass (20) also carries the reducer's note that the host's
share uses the whole process's CPU time (an upper bound). The reducer's other notes touch its catalogue cross-check only, not the headline:
in pass 11, the cross-check (4.166 J) is off the headline (3.746 J) by more than 6% and one SP pass of its step; in passes 1, 5, 10, 12, 14,
16 and 22, one or two busy board readings at idle move the cross-check about 4%, 3%, 3%, 2%, 2%, 3% and 2% low (each pass's `energy.json` >
`flags` names it).

## Registered against happened

| item | registered (E191.md, note 1, the kit, kit notes 2 and 3, A1, A2) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry1 card 1, 600 MHz as found, reads only | card 1; 600 MHz in 9,492 of 9,492 samples; TDP 65 W / 65 C / 600 MHz, 499 mV at both ends; nothing set |
| the identity gate (note 1, item 3) | the start config names `/dev/et1_mgmt` and device ID 1, `minion_mv` below 510; et-who with the sampler: ours on card 1 only, one on `/dev/et1_mgmt`; each device-opening host's block card 1 | passed: `/dev/et1_mgmt`, ID 1, 499 mV; ours on card 1 2 (1 on `/dev/et1_mgmt`), on card 0 0, another login's 0; every host's block card 1 (31 of 31) |
| the reboot gate | aifoundry1 up since before E82's firmware read (2026-10-31 13:45:24 PDT) | booted 2026-10-26 15:02:04 PDT: ok (steps 4 and 9 v3) |
| card time | about 95 card-minutes, cap 110 from the third session's own first card command (no pass after 108) | 15.84 card-minutes (950.6 s); the cap never bound |
| passes | 24, in `plan-e191.json`'s order | 24 ran in that order, 24 reduced ok, 0 set aside, 0 SHORT, 0 FAILED RUN |
| launches K | `plan-e191.json` | as planned in all 24 |
| the host's line (kit note 2) | read from the host's standard output with the runtime's exact line dropped and the line's own fields verified; a line not verified is not read | read in all 31 device-opening host runs, one runtime line dropped from each; no line unread |
| stop-path test and smoke | before any pass; a failed smoke is a gate: no data | the stop-path test passed; all 8 smoke runs ok |
| stops | board 65 W, `minshire[0]` 70 C, the clock off 600 MHz | none tripped (52.27 W, 57 C; no sample off the clock) |
| die gate and band | gate at 60 C, at most 10 minutes; forecast band 52-60 C | the gate never waited; starts at 53-55 C by the runner's sample (none below the band); T0 53.0-54.9 C |
| idle anchors | three of 2 minutes | three, each whole |
| the counters arm | dropped by the kit (KIT.md 5) | not run |
| builds (A2-5) | the third session's day builds its own: that day's first start, then the wait; never a third start that day | one start (step 6, 00:13:18-00:13:20 PST: `E191-BUILDS-TODAY 0`; the job ended rc 0 at 00:13:29 PST on the box): LEDGER-BUILT and SPP-BUILT, both kernels KERNEL OK (ledger ELF `2b2eb281...`, `.text` `5e00e45a...`; sparse parity ELF `6ee70c92...`, `.text` `3e14be32...`, each `.text` the registered one), both hosts HOST-BEHAVIOUR OK (10 and 3 checks), `ET_DEVICES` read yes, both build records BUILT 2026-11-16 |
| the dry pass | runner v2's dry pass ended rc 0 that day | `E191-DRY-V2 rc=0 passes=6 dry-check=1 identity-lines=2 note2=1 runtime-dropped=7` (00:13:43-00:14:04 PST on the box) |
| the rest (A2-4) | at least 40 minutes after our last real session on aifoundry1; step 7 only after the rest has opened | 592 minutes since the second session's end (14:21:46 PST Sun 15 Nov; open since 15:01:46 PST that day); step 7 ran at 00:13:40 PST |
| the window (A2-4) | from G3: last start G3+1:30, last end G3+3:30, each rounded up, inside that Pacific day; G3 at 20:29:00 PST or earlier | G3 00:00:41 PST Mon 16 Nov: last start 01:31, last end 03:31 PST (Departures 3); launched at 00:14:14, ended 00:30:05 |
| sessions (A2-2) | one of ours on aifoundry1 at a time; this the third and last E191 session (no fourth) | one launch, one session; no relaunch; card 0 never opened |
| the box's last launch (kit note 2, A2) | step 9 v3 launches only when the box's last E191 launch is the one this RB_OUT knows (with none, the second session's 1794780355) | read 1794780355, the second session's T0; this RB_OUT had launched nothing |
| the host's package counter | not read unless his go allows it | not read |
| the post | the day's etiquette (E191.md 13) | waived by the owner (Departures 2) |

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-10 set by his go, A2 and the round's brief before the session; 11 read before this commit; 12 after the collection, said so; all written here after the collection and before the scorer ran)

1. **The go.** The owner's standing words of Sun 15 Nov 2026, verbatim: at **10:05:42 PST**, "continue, all machines are up"; at **10:22:36
   PST**, "don't worry about discord post, just use the machines, nobody is using them"; at **17:21:16 PST**, "Feel free to use more cards
   in parallel, I don't need to reserve them (things are automatically updated on [a link, left out here]), currently I see only 1 card is
   being used, feel free to use more in parallel"; and, after the round's agents stopped at about
   18:05 PST, "Try again" (received at or before 21:28:59 PST). Beside them, the report of his words posted for him at 19:34:12 PST: "The
   aifoundry cards are all free right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free
   to use them." His words name no experiment: **the registered items stand as their defaults** (A2-3, A2-4; E191.md 13): aifoundry1 card 1,
   600 MHz as found, reads only, nothing set, nothing on card 0; about 95 card-minutes, cap 110; THE IDENTITY GATE.
2. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim and no release, a departure from
   E191.md 13's etiquette sentence. Every other etiquette check stood: the look before the session (et-who, who, uptime, the holder rule:
   FREE on both cards at 00:13:17), step 7's reads (both cards free at 00:13:41), card 1's lock held by the session to its end, the runner's
   holder read, `timeout 10` a host process.
3. **A2: the third session as a REPEAT, its window from G3, and the build rule.** E191.md's dated amendment A2 (landed `318a0985`, 23:05:32
   PST Sun 15 Nov 2026, after the second session's data and scores and before any datum of this session) allows this one third session,
   E191's last. Its window runs from **G3, this lane's booking of aifoundry1: 00:00:41 PST Mon 16 Nov 2026** (the booking's own record): last
   start G3+1:30 = 01:30:41 and last end G3+3:30 = 03:30:41, each rounded up to the whole minute: **01:31 and 03:31 PST**
   (`s02_window_e191.sh 2026-11-16 01:31 03:31`, written by step 1 at 00:12:33; the window file's `RB_GO_EPOCH`, 1794816753 = 00:12:33 PST,
   is the moment step 1 wrote it, not his go). The build rule (A2-5): the day's own build, one start (Builds, in the table above).
4. **The card day: Mon 16 Nov 2026, moved from Sunday.** The round's agents stopped at its session's weekly usage limit at about 18:05 PST
   Sun 15 Nov; Sunday's last possible G3 (20:29:00 PST) had passed before A2 landed at 23:05:32 PST. This lane booked at the first moment of
   Monday it went on (00:00:41 PST), as A2-4 allows (Mon 16 Nov 2026 or a later Pacific day). G3 = the booking, never his words' times.
5. **The host's package counter: not read** (his go does not name it: E191.md 13's default no): step 9 v3 ran without `--rapl-allowed`.
6. **Both earlier records, used by no gate of this session** (A2-1, A2-3): the first session's (`1a4bc1e3`,
   `2026-11-15-e191-blind-day-aifoundry1-c1/`, no pass in it) and the second session's (`7156ac15`, `2026-11-15-e191-blind-day-aifoundry1-c1-s2/`,
   with its data note 1 `aaf70691` and the scores commit `f74c81e3`). No gate, forecast or rule of this session reads their readings; this
   directory is a new one (`-c1-s3`), never merged into either, and neither record is edited. Step 9 v3's check of the box's last launch read
   the second session's T0 (1794780355) as the box's last E191 launch, as A2 expects.
7. **No refused launch.** One launch (T0 1794816854), which sent card commands and ran to its end: THE RELAUNCH RULE was not used, and no
   `e191-relaunch.txt` exists.
8. **A fresh network-access approval for aifoundry1: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches
   aifoundry1 without that check. The kit's login-link stop stayed live; no step met a login link.
9. **The desk.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names.
10. **The orchestrator.** The orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14
    Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov, and which resumed after the round's stop on Sun 15 Nov.
11. **THE EXCLUSION RULE (A2-6), read before this commit.** E194's card lane passed its step 2 (its desk check v2, rc 0) at 00:13:19 PST Mon
    16 Nov, before this data commit; and E194's dated amendment A1, whose step 2 v2 leaves out every
    `<day>-e191-blind-day-aifoundry1-c1-s3` folder of any day, had landed in `04b6f022` (23:11:06 PST Sun 15 Nov). So this directory does not
    stop E194's step 2. The third session's data commit itself follows the kit as written.
12. **Notes, not departures (after the collection).** The die notes under the pass table (post hoc). Power state (post hoc, a reading no
    gate names): the config reads at both ends of this session read power state 1 (`managed_power`), where the second session's read 3
    (`low_power`); TDP, threshold, clock and `minion_mv` read the same as then. Step 6's wait printed "the dry pass a1-build-e191 ended rc 0"
    for the build job: the kit's wording, not a dry pass. Step 10 v2 found the session by the pattern `session_e191*.sh`, which names the
    script step 9 v3 launched, `session_e191_v2.sh` (read before step 9 v3; two calls: running at 00:23:15, after 526 s; ended with 207 files
    in its manifest at 00:30:13). The card time came in close to the second session's (15.85 card-minutes) and far under the estimate.

## Device commands sent

Reads only. The session's `commands.jsonl` lists 61 commands, each with `ET_DEVICES=1` and card 1's lock: et-who 26 times (no device);
`ettelem config` at the start and the end and `ettelem sample --every-ms 100` (no `--reset-ms`), each through the kit's guard, which passes
`config` and `sample` only; the ledger host's self-test (no device); and 31 host runs on the card (the 7 smoke runs and the 24 passes: 26
ledger runs, 5 sparse parity runs), each of which opened card 1's ops node only. Step 7's config read before the session (00:13:40 PST) was
the same read, with the box's manifest kept on the box (sysfs and files only); the dry pass ran on stand-ins. The device-command audit
(`dmcmd_audit.py` through the preflight and preflight v2) read **GO, 16 send sites, 0 disallowed** at step 2 on the desk and again on the
box after the build (step 6's wait); the dry pass's device-command check passed (`dry-check=1`). No set of any kind (TDP, threshold, clock,
voltage), no reset, no statistics reset, no firmware-revisions query, no power cycle. Card 0 was never opened: every command carried
`ET_DEVICES=1`, identity (b) read nothing of ours on card 0, and every host that opened a device named card 1.

## Privacy and the public-text scan

The collector's scrub ran (the box's home path became `~`, the box login `<login>`), and the desk-path gate read CLEAN over the 259 files it
read. The public-text scan before the commit read every text file of this directory, the text inside its 25 `.gz` files and this README,
with the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its fixed list and the local privacy table) plus the private-network,
Mac-home, scratch and e-mail patterns: 231 text files and 25 `.gz` files, **25 hits, every one the sanitizer's pattern for administrator
words on the reducer's fixed note below** (24 in the `energy.json` files, 1 in this README's quotation of it). The round's classes over this
README and the commit message (names under NDA, logins and home paths, private links, access words) matched **1 line**: the post platform's
name inside the owner's verbatim words of 10:22:36 PST (Departures 1), kept verbatim as other committed records quote them; the commit
message read 0 lines and 0 sanitizer hits. The round's classes, run also over the collected text files, matched only words of the card's
and the workload's own output and one hash, kept as collected: the device layer's identity block's name for the card's on-chip scratch
memory (12 lines in each of 34 files: the 31 hosts' `host.err`, `config-start.err`, `config-end.err` and `sampler.err`), the same block
the second session's committed record carries; sparse parity's own field naming its instance's hidden indices (one line in each of 13
files: each pass's `host.json`, `stdout.txt` and `energy.json`, and the smoke run's `stdout.txt`), as in the second session's record; byte
runs in the 4 binary `host.rec` files; and the first hex digits of one sha256 in `SHA256SUMS` (the digest of `session/MANIFEST.sha256`). **The unchanged reducer's fixed note** "assumed package power (RAPL is root-only)" (`energy_reduce.py`) is in every
`energy.json` here, **24 of 24**, kept as collected (a collected file is never edited).

## Files

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E191.md 8.1), 24 directories: `stdout.txt` (the host's standard output, raw as collected: the runtime's `Opening device 1` inside the ledger host's line, or on a line of its own before sparse parity's), `host-raw.json` (the ledger programs: the host's own line as runner v2 reassembled it, which the frozen scorer reads), `host.json` (the reducer's input: the adapter's fields of the ledger host's line, or sparse parity's own verified line), `host.rec` (sparse parity's records), `host.err` (the host's stderr: its device-layer block names card 1), `telemetry.jsonl.gz` (the session's samples over the pass), `run.json` (energy.sh's marks, with the reader's record `host_line`), `pass.json` (the runner's marks), `energy.json` and `energy.txt` (the reducer's output, its `dir` set to this path) |
| `session/` | the session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`: its 207 files, plus `runner.rc`), scrubbed: `session.log` and `runner.out` (the session's lines), `runner.rc` (0), `queue.json` (the queue, `identity_ok` true, no stop, bound or early stop), `identity.json` (the identity gate's readings), `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err` (the config reads and their device-layer blocks: `/dev/et1_mgmt`, ID 1), `etwho-before.txt`, `etwho-identity.txt`, `commands.jsonl` (every command sent), `stop-path.json`, `anchors.json`, `sampler.err`, `telemetry.jsonl.gz` (the whole session: 9,492 samples), `MANIFEST.sha256`; no `STOP` (no early stop) |
| `session/smoke/<run>/` | the 8 smoke runs: `stdout.txt` (the host's standard output, raw), `host.err` (the host's stderr), `smoke.json` (the runner's reading, with the reader's record `host_line`) |
| `SHA256SUMS` | the collector's (`collect_e191.py`, 257 files): every file but this README, itself and `FILES.txt` |
| `FILES.txt` | the collector's list of every collected file, by path (257) |

## Next

The frozen scorer, after this commit only: `rb/s24_score_e191_v3.sh` runs `score_e191.py` (registered in `300d76e4`, unchanged) on this
committed directory and writes three outputs: `scores-e191-s3.json` (this session's four rules' words, E191-S1, S1T, S2 and S2T, with each
configuration's errors: **REPORTED**, never verdicts); `scores-e191-s2.json`, the second session's output re-derived, which must read the
registered bytes `23484c4f...`; and `repeat-e191-s3.json` with `repeat-e191-s3.txt` (the repeat reading, the two sessions side by side). A
later lane commits them beside this directory. **E191's verdicts are the second session's and stand.**

SPDX-License-Identifier: Apache-2.0
