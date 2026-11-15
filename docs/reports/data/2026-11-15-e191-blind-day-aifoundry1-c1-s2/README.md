# E191: the blind day on aifoundry1 card 1, Sun 15 Nov 2026 - the second session (E191.md's dated amendment A1): all 24 registered passes ran in one session of 15.85 card-minutes, reads only, no stop line tripped, none SHORT and none a failed run; the frozen scorer runs after this commit

*Sun 15 Nov 2026 (week 46), PST, Q184's card lane `card-e191b`, orchestrated from aifoundry2. Registered in `300d76e4`
([`E191.md`](../../../../tools/claims-v3/e191/E191.md)), its dated note 1 `8c8f825f`
([`E191.md.dated-note-1.md`](../../../../tools/claims-v3/e191/E191.md.dated-note-1.md)), kitted in `eb1ac923`
([`KIT.md`](../../../../tools/claims-v3/e191/KIT.md)), and the kit's dated note 2 with E191.md's dated amendment A1 landed in `2d0fe517`
([`KIT.md.dated-note-2.md`](../../../../tools/claims-v3/e191/KIT.md.dated-note-2.md),
[`E191.md.dated-amendment-A1.md`](../../../../tools/claims-v3/e191/E191.md.dated-amendment-A1.md),
[`CARD-LANE-BRIEF.md.dated-note-1.md`](../../../../tools/claims-v3/e191/CARD-LANE-BRIEF.md.dated-note-1.md)), all before any E191 pass
datum. The session, T0 1794780355 = 14:05:55 PST, ran to its `session end` at 14:21:46 PST: **15.85 card-minutes** from its first card
command, against the registered estimate of about 95 and the cap of 110. All 24 passes ran in `plan-e191.json`'s order, each with its K
launches, host status PASS and reading PASS, and all 24 reduced with the reducer's hard checks passed. Reads only. **The day's post: waived
by the owner**, his words of Sun 15 Nov 2026 10:22:36 PST (Departures 2). **Blind:** every forecast, band and rule was committed in
`300d76e4` before E189's data (step 2 v2's never-ran check (b)), and these are the first E191 passes on any card: the first session
(`1a4bc1e3`) stopped at its smoke gate before any pass, and its record is used by no rule here (A1-2).*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold, band and
rule is **registered** (E191.md, its note 1, A1, `plan-e191.json`, `forecast-e191.json`). The per-configuration means in the second table
are **desk arithmetic of the measured passes** (each configuration's four `energy.json` records): **they are not verdicts**, and no forecast
is set beside them here. Two readings are marked **post hoc** (desk readings of the collected files after the collection): where the runtime's
line sits in each raw `stdout.txt`, and the die notes under the pass table. The four rules' words are the frozen scorer's (`score_e191.py`,
unchanged), which runs only on this directory once it is committed (`rb/s24_score_e191_v2.sh`); its output, `scores-e191.json`, is committed
beside this directory by a later lane. Nothing here changes a frozen number. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## What ran (measured)

- **Card:** aifoundry1 card 1, **600 MHz in all 9,493 samples** of the session's 10 Hz telemetry (14:05:55.907-14:21:46.447 PST; none
  without a clock reading, none off 600 MHz: `queue.json` > `off_clock` is empty). `ettelem config` through the kit's guard at the session's
  start (14:05:55) and end (14:21:46): TDP 65 W, threshold 65 C, power state 3 (`low_power`), 600 MHz, `minion_mv` 499, the same at both
  ends. **Nothing was set.** `since_reset_ms` -1 in every sample: no statistics reset.
- **The identity lines, as the session log reads them:**
  - `config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499 (read, nothing set); identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510`;
  - `identity (b): et-who with the sampler running: ours on card 1 2 (on /dev/et1_mgmt 1), ours on card 0 0, another login's 0; the sampler holds /dev/et1_mgmt only`;
  - the smoke hosts: `ledger-selftest` "no device (the self-test)"; the seven others "card 1";
  - every pass's host: its `host.err` block names PCIe target `/dev/et1_ops` and physical device ID 1, and the node it held was
    `/dev/et1_ops` (`run.json` > `identity` > `right` true in 24 of 24);
  - `config end: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499; its identity card 1`.
  THE IDENTITY GATE (note 1, item 3) passed: `queue.json` > `identity_ok` true.
- **Card session:** T0 1794780355 = 14:05:55 PST to its `session end` at 14:21:46 PST; from the first card command (14:05:55.888) to the
  close (14:21:46.610): **950.7 s, 15.85 card-minutes**. The cap's end (`queue.json` > `end_bound_ms`, 110 minutes from the first card
  command: 15:55:55.888 PST) and the window's last end (17:33 PST) were never reached. `runner.rc` 0.
- **The sequence, as registered:** the box check passed (aifoundry1, `ET_DEVICES=1`, the reader at its pin, today's builds by
  `build_e191.sh` with the `ET_DEVICES` reading passed, each host and kernel at its build record's sha256 with the kernel gate's OK); the
  start config read and identity (a); the sampler (attempt 1, every 100 ms); identity (b); **the stop-path test passed** (the board, die and
  clock lines each tripped on live samples within 0.2 s and each refused a start); the ramped smoke, **all 8 runs ok** (the ledger's
  self-test; the copy at 64 MiB random and zeros, then 1 GiB random; SHA-256 at `--block 2048 --repeat 1` with `--expect`; the sort of 512
  keys shuffled and sorted; sparse parity's instance once), `smoke gate passed` at 14:06:00; idle anchor 1 (14:06:00.9-14:08:00.9), passes
  1-12 (14:08:01-14:12:53), idle anchor 2 (14:12:53.7-14:14:53.7), passes 13-24 (14:14:53-14:19:46), idle anchor 3
  (14:19:46.5-14:21:46.5), each anchor whole (`anchors.json`); `the counters arm: DROPPED by E189's kit (its KIT.md section 5; E191.md 7):
  not run`; the closing config read; `session end`.
- **The host's line, read by kit note 2's reader for every host process.** Each of the 31 device-opening host runs (7 smoke runs and 24
  passes) printed exactly one runtime line, `Opening device 1`, on its standard output. Runner v2 dropped it and read the host's line with
  its own fields verified: `smoke.json` > `host_line` and `run.json` > `host_line` read `runtime_lines` ["Opening device 1"], `json_lines`
  1, `other_lines` 0 and an empty `why` in all 31, and each of the seven device smoke lines reads "the host's line: 1 runtime line(s)
  dropped (Opening device 1)".
  The ledger's self-test printed no runtime line. **No host's line went unread:** no pass carries the flag "the host's line was not read",
  and none is a FAILED RUN. Post hoc (a desk reading of the collected `stdout.txt` files): in each of the 26 ledger host runs the runtime's
  text sits at the end of the host line's first part, splitting the line in two, as it did in the first session; in each of the 5 sparse
  parity runs it is a line of its own before the host's line.
- **All 24 passes ran in the registered order** (`plan-e191.json`, never re-drawn), **each with its K launches** (copy 8, SHA-256 9, the
  sorts 8 and 7, sparse parity 9), host status PASS and reading PASS: **none SHORT, none a FAILED RUN, none set aside**
  (`queue.json` > `set_aside` empty). **All 24 reduced with the reducer's hard checks passed** (`energy.json` > `ok` true, `hard` empty;
  the reducer is energy.sh's `energy_reduce.py`, unchanged).
- **No stop line tripped.** The highest live readings were **50.57 W board** (14:11:52.6, during pass 10, sparse parity p2) and **55 C
  `minshire[0]`** (14:16:24.0, during pass 16, sparse parity p3), against the stops 65 W and 70 C.
- **The die gate never waited** (`pass.json` > `die_gate_wait_s` 0 in all 24). By the runner's live sample every pass started at 50-52 C:
  20 passes carry its flag "T0 below the forecast band" (below 52 C), and passes 6, 11, 17 and 18 started at 52 C, unflagged. As E191.md
  section 11 registers, a die below 52 C does not block: each pass is scored given its own T0.
- **No BOUND line** (`queue.json` > `bound` empty; `lock_released_with_bound_host_alive` false), **no early stop** (`early_stop` null; no
  stop file, no signal), **no "the sampler is not live" line** (`sampler_lines_not_live` 0; `passes_sampler_not_live` empty), no restart of
  the sampler. Every pass's `run.json` reads `sampler_live_during_pass` true, `live_gap_s_pass` and `live_gap_s_host` 0.10-0.11 s, and the
  three sample ages (at the host's start, at its end, at the pass's end) 0.00-0.10 s.
- **The host's package counter was not read** (step 9 v2 ran without `--rapl-allowed`; `run.json` > `rapl` "not read: his go did not allow
  it"); the host's share stays assumed and labelled so.

## The passes (measured; the means are desk arithmetic of the measured passes, not verdicts)

One row a pass, in the order run. J over idle a launch is `energy.json` > `board.j_per_solve`; J with the card at rest a launch is
`board.j_per_solve_total` (E191.md 8.1). t_w, T0 and t_k are the scorer's own measured inputs, by its definitions (`score_e191.py`'s
header), computed here as desk arithmetic of the same records: t_w = 1 / `solves_per_s`; T0 = `die_c.before`; t_k = the slowest minion's
cycles of the burst's last launch / 600 MHz (`host-raw.json` > `hart0_cycles.max` for the ledger programs, `host.json` > `kernel.cycles_max`
for sparse parity).

| # | pass | started (PST) | launches (K) | die at start (runner) / T0 (`die_c.before`), C | J over idle a launch | J with the card at rest a launch | t_w, s | t_k, s | reading | flags |
|---:|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | copy, zeros p1 | 14:08:01 | 8 (8) | 50 / 50 | 5.934 | 33.017 | 0.9091 | 0.9067 | PASS | die below the band |
| 2 | SHA-256 p1 | 14:08:28 | 9 (9) | 50 / 50 | 2.467 | 15.396 | 0.4332 | 0.4316 | PASS | die below the band |
| 3 | sort, sorted p1 | 14:08:50 | 8 (8) | 50 / 50 | 3.452 | 20.211 | 0.5609 | 0.5593 | PASS | die below the band |
| 4 | copy, random p1 | 14:09:13 | 8 (8) | 51 / 50 | 8.105 | 35.399 | 0.9094 | 0.9076 | PASS | die below the band |
| 5 | sparse parity p1 | 14:09:40 | 9 (9) | 51 / 51 | 8.709 | 24.362 | 0.5144 | 0.5128 | PASS | die below the band |
| 6 | sort, shuffled p1 | 14:10:04 | 7 (7) | 52 / 51 | 3.755 | 24.946 | 0.6959 | 0.6942 | PASS | reducer: catalogue cross-check off the headline by more than 6% |
| 7 | SHA-256 p2 | 14:10:27 | 9 (9) | 51 / 51 | 2.587 | 15.641 | 0.4332 | 0.4316 | PASS | die below the band |
| 8 | copy, random p2 | 14:10:50 | 8 (8) | 51 / 51 | 8.333 | 35.636 | 0.9089 | 0.9070 | PASS | die below the band |
| 9 | sort, sorted p2 | 14:11:17 | 8 (8) | 51 / 51 | 3.612 | 20.472 | 0.5610 | 0.5593 | PASS | die below the band |
| 10 | sparse parity p2 | 14:11:40 | 9 (9) | 51 / 51 | 8.788 | 24.441 | 0.5143 | 0.5129 | PASS | die below the band |
| 11 | sort, shuffled p2 | 14:12:03 | 7 (7) | 52 / 51 | 3.800 | 24.953 | 0.6956 | 0.6941 | PASS |  |
| 12 | copy, zeros p2 | 14:12:26 | 8 (8) | 51 / 51 | 6.107 | 33.459 | 0.9094 | 0.9077 | PASS | die below the band |
| 13 | sort, shuffled p3 | 14:14:53 | 7 (7) | 50 / 50 | 4.089 | 24.825 | 0.6957 | 0.6942 | PASS | die below the band; reducer: 1 of 24 busy board_w readings at idle (catalogue cross-check only) |
| 14 | copy, zeros p3 | 14:15:17 | 8 (8) | 51 / 50.375 | 6.126 | 33.281 | 0.9092 | 0.9081 | PASS | die below the band |
| 15 | copy, random p3 | 14:15:44 | 8 (8) | 51 / 51 | 8.416 | 35.651 | 0.9094 | 0.9072 | PASS | die below the band |
| 16 | sparse parity p3 | 14:16:11 | 9 (9) | 51 / 51 | 8.671 | 24.426 | 0.5150 | 0.5130 | PASS | die below the band; reducer: 2 of 27 busy board_w readings at idle (catalogue cross-check only) |
| 17 | SHA-256 p3 | 14:16:34 | 9 (9) | 52 / 52 | 2.522 | 15.684 | 0.4332 | 0.4316 | PASS |  |
| 18 | sort, sorted p3 | 14:16:57 | 8 (8) | 52 / 51 | 3.417 | 20.406 | 0.5607 | 0.5593 | PASS |  |
| 19 | SHA-256 p4 | 14:17:20 | 9 (9) | 51 / 51 | 2.467 | 15.563 | 0.4331 | 0.4316 | PASS | die below the band |
| 20 | sort, shuffled p4 | 14:17:42 | 7 (7) | 51 / 51 | 4.078 | 25.087 | 0.6957 | 0.6942 | PASS | die below the band |
| 21 | sort, sorted p4 | 14:18:06 | 8 (8) | 51 / 51 | 3.547 | 20.466 | 0.5609 | 0.5593 | PASS | die below the band |
| 22 | copy, random p4 | 14:18:29 | 8 (8) | 51 / 51 | 8.174 | 35.648 | 0.9094 | 0.9070 | PASS | die below the band |
| 23 | copy, zeros p4 | 14:18:56 | 8 (8) | 51 / 51 | 5.880 | 33.401 | 0.9092 | 0.9071 | PASS | die below the band; reducer: 1 of 41 busy board_w readings at idle (catalogue cross-check only) |
| 24 | sparse parity p4 | 14:19:23 | 9 (9) | 51 / 51 | 8.598 | 24.403 | 0.5144 | 0.5130 | PASS | die below the band; reducer: 1 of 27 busy board_w readings at idle (catalogue cross-check only) |

| configuration | passes reduced ok | launches a pass (K registered) | J over idle a launch, mean of 4 (min-max) | J with the card at rest a launch, mean of 4 (min-max) |
|---|---:|---|---|---|
| copy, zeros (`--bytes 1G --passes 14 --data zeros --width 32`) | 4 of 4 | 8 (8) | 6.012 (5.880-6.126) | 33.289 (33.017-33.459) |
| copy, random (`--bytes 1G --passes 14 --data random --width 32`) | 4 of 4 | 8 (8) | 8.257 (8.105-8.416) | 35.583 (35.399-35.651) |
| SHA-256 (`--block 2048 --repeat 800`, with `--expect`) | 4 of 4 | 9 (9) | 2.511 (2.467-2.587) | 15.571 (15.396-15.684) |
| sort, sorted (`--keys 512 --reps 1800 --order sorted`) | 4 of 4 | 8 (8) | 3.507 (3.417-3.612) | 20.389 (20.211-20.472) |
| sort, shuffled (`--keys 512 --reps 1800 --order shuffled`) | 4 of 4 | 7 (7) | 3.931 (3.755-4.089) | 24.953 (24.825-25.087) |
| sparse parity (the registered instance: `--n 544 --k 4 --eta 0.39 --m 1792 --seed 3`) | 4 of 4 | 9 (9) | 8.691 (8.598-8.788) | 24.408 (24.362-24.441) |

Notes on the table. "die below the band" is the runner's flag "T0 below the forecast band" (its live sample at the pass's start, below 52 C).
Post hoc: the reducer's `die_c.before` (the scorer's T0) reads below the runner's start sample in passes 4, 6, 11, 14 and 18 (by 0.6-1 C),
so passes 6, 11 and 18 carry a T0 of 51 C without the runner's flag; every T0 is 50.0-52.0 C. Every ledger pass (20) also carries the reducer's note
that the host's share uses the whole process's CPU time (an upper bound). The reducer's other notes touch its catalogue cross-check only,
not the headline: in pass 6, the cross-check (4.207 J) is off the headline (3.755 J) by more than 6% and one SP pass of its step; in passes
13, 16, 23 and 24, one or two busy board readings at idle move the cross-check about 4%, 7%, 2% and 3% low (each pass's `energy.json` >
`flags` names it).

## Registered against happened

| item | registered (E191.md, note 1, the kit, kit note 2, A1) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry1 card 1, 600 MHz as found, reads only | card 1; 600 MHz in 9,493 of 9,493 samples; TDP 65 W / 65 C / 600 MHz, 499 mV at both ends; nothing set |
| the identity gate (note 1, item 3) | the start config names `/dev/et1_mgmt` and device ID 1, `minion_mv` below 510; et-who with the sampler: ours on card 1 only, one on `/dev/et1_mgmt`; each device-opening host's block card 1 | passed: `/dev/et1_mgmt`, ID 1, 499 mV; ours on card 1 2 (1 on `/dev/et1_mgmt`), on card 0 0, another login's 0; every host's block card 1 (31 of 31) |
| the reboot gate | aifoundry1 up since before E82's firmware read (2026-10-31 13:45:24 PDT) | booted 2026-10-26 15:02:04 PDT: ok (steps 4 and 9 v2) |
| card time | about 95 card-minutes, cap 110 from the second session's own first card command (no pass after 108) | 15.85 card-minutes (950.7 s); the cap never bound |
| passes | 24, in `plan-e191.json`'s order | 24 ran in that order, 24 reduced ok, 0 set aside, 0 SHORT, 0 FAILED RUN |
| launches K | `plan-e191.json` | as planned in all 24 |
| the host's line (kit note 2) | read from the host's standard output with the runtime's exact line dropped and the line's own fields verified; a line not verified is not read | read in all 31 device-opening host runs, one runtime line dropped from each; no line unread |
| stop-path test and smoke | before any pass; a failed smoke is a gate: no data | the stop-path test passed; all 8 smoke runs ok |
| stops | board 65 W, `minshire[0]` 70 C, the clock off 600 MHz | none tripped (50.57 W, 55 C; no sample off the clock) |
| die gate and band | gate at 60 C, at most 10 minutes; forecast band 52-60 C | the gate never waited; starts at 50-52 C by the runner's sample (20 flagged below the band); T0 50.0-52.0 C |
| idle anchors | three of 2 minutes | three, each whole |
| the counters arm | dropped by the kit (KIT.md 5) | not run |
| builds | A1-4: no build start on the day of the second session; the day's build re-read | no start; step 6's wait alone re-read the day's one start (10:13:38-10:13:49 PST on the box): both kernels KERNEL OK (ledger ELF `2b2eb281...`, `.text` `5e00e45a...`; sparse parity ELF `6ee70c92...`, `.text` `3e14be32...`, each `.text` the registered one), both hosts HOST-BEHAVIOUR OK (10 and 3 checks), `ET_DEVICES` read yes, both build records BUILT today |
| the dry pass | runner v2's dry pass ended rc 0 today | `E191-DRY-V2 rc=0 passes=6 dry-check=1 identity-lines=2 note2=1 runtime-dropped=7` (14:05:06-14:05:29 PST on the box) |
| the rest | at least 40 minutes after our last real session on aifoundry1 | 230 minutes since the first session's end (10:14:56 PST) |
| the window (A1-3) | from G2: last start G2+1:30, last end G2+3:30, each rounded up; G2 at 20:29:00 PST or earlier | G2 14:02:10 PST: last start 15:33, last end 17:33 PST (Departures 3); launched at 14:05:55, ended 14:21:46 |
| sessions | one of ours on aifoundry1 at a time; this the day's last E191 session | one launch, one session; no relaunch; card 0 never opened |
| the host's package counter | not read unless his go allows it | not read |
| the post | the day's etiquette (E191.md 13) | waived by the owner (Departures 2) |

## Departures and notes (dated Sun 15 Nov 2026, PST; 1-9 set by his go, A1 and the round's brief before the session; 10 after the collection, said so; all written here after the collection and before the scorer ran)

1. **The go.** The owner's standing words, verbatim: at **10:05:42 PST**, "continue, all machines are up" (the go for E191 on aifoundry1
   card 1 that day, the registered items unchanged); and at **10:22:36 PST**, "don't worry about discord post, just use the machines,
   nobody is using them". A1-3 carries them to the second session. The registered items stand unchanged: aifoundry1 card 1, 600 MHz as
   found, reads only, nothing set, nothing on card 0; about 95 card-minutes, cap 110; THE IDENTITY GATE.
2. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim and no release, a departure from
   E191.md 13's etiquette sentence. Every other etiquette check stood: the look before the session (et-who, who, uptime, the holder rule:
   FREE on both cards at 14:05:04), step 7's reads (both cards free at 14:05:05), card 1's lock held by the session to its end, the runner's
   holder read, `timeout 10` a host process.
3. **A1: the second session, its window from G2, and the build rule.** E191.md's dated amendment A1 (landed `2d0fe517`, 13:16:10 PST, before
   any E191 pass datum) allows this one second session. Its window runs from **G2, the card lane's booking of aifoundry1: 14:02:10 PST**
   (the booking's own record): last start G2+1:30 = 15:32:10 and last end G2+3:30 = 17:32:10, each rounded up to the whole minute: **15:33
   and 17:33 PST** (`s02_window_e191.sh 2026-11-15 15:33 17:33`, written by step 1 at 14:03:57; the window file's `RB_GO_EPOCH`,
   1794780237 = 14:03:57 PST, is the moment step 1 wrote it, not his go). The build rule (A1-4): no build start that day; step 6 ran its
   wait alone, which re-read the day's one build (the first session's, 10:13:38-10:13:49 PST on the box) into this session's run folder
   ("ledger,spp").
4. **The host's package counter: not read** (his go does not name it: E191.md 13's default no): step 9 v2 ran without `--rapl-allowed`.
5. **The first session's record (`1a4bc1e3`, `2026-11-15-e191-blind-day-aifoundry1-c1/`): used by no rule** (A1-2). No gate, forecast
   or rule of this session reads its readings; this directory is a new one (`-c1-s2`), never merged into that one, and that record is not
   edited. The step 9 v2 check of the box's last launch read that session's T0 (1794766494) as the box's last E191 launch, as A1 expects.
6. **No refused launch.** One launch (T0 1794780355), which sent card commands and ran to its end: THE RELAUNCH RULE was not used, and no
   `e191-relaunch.txt` exists.
7. **A fresh network-access approval for aifoundry1: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches
   aifoundry1 without that check. The kit's login-link stop stayed live; no step met a login link.
8. **The desk.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names.
9. **The orchestrator.** The orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14
   Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov.
10. **Notes, not departures (after the collection).** The die notes under the pass table (post hoc). Step 6's wait printed "the dry pass
    a1-build-e191 ended rc 0" for the build job: the kit's wording, not a second dry pass. Step 10 v2 found the session by the pattern
    `session_e191*.sh`, which names the script step 9 v2 launched, `session_e191_v2.sh` (read before step 9 v2; two calls: running at
    14:15:00, ended with 207 files in its manifest at 14:21:56). The card time came in far under the estimate: the die gate never waited,
    and the cap's margin went unused.

## Device commands sent

Reads only. The session's `commands.jsonl` lists 61 commands, each with `ET_DEVICES=1` and card 1's lock: et-who 26 times (no device);
`ettelem config` at the start and the end and `ettelem sample --every-ms 100` (no `--reset-ms`), each through the kit's guard, which passes
`config` and `sample` only; the ledger host's self-test (no device); and 31 host runs on the card (the 7 smoke runs and the 24 passes: 26
ledger runs, 5 sparse parity runs), each of which opened card 1's ops node only. Step 7's config read before the session (14:05:05 PST) was
the same read, with `et-lab-manifest` (sysfs and files only); the dry pass ran on stand-ins. The device-command audit (`dmcmd_audit.py`
through the preflight and preflight v2) read **GO, 16 send sites, 0 disallowed, every one a READ** at step 2 on the desk and again on the
box after the build (step 6's wait); the dry pass's device-command check read 16 device-opening command lines, each with `ET_DEVICES=1`,
none naming card 0 or calling the management service or et-powertop. No set of any kind (TDP, threshold, clock, voltage), no reset, no
statistics reset, no firmware-revisions query, no power cycle. Card 0 was never opened: every command carried `ET_DEVICES=1`, identity (b)
read nothing of ours on card 0, and every host that opened a device named card 1.

## Privacy and the public-text scan

The collector's scrub ran (the box's home path became `~`, the box login `<login>`), and the desk-path gate read CLEAN over the 259 files it
read. The public-text scan before the commit read every text file of this directory, the text inside its 25 `.gz` files and this README,
with the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its fixed list and the local privacy table) plus the private-network,
Mac-home, scratch and e-mail patterns: 231 text files and 25 `.gz` files, **25 hits, every one the sanitizer's pattern for administrator
words on the reducer's fixed note below** (24 in the `energy.json` files, 1 in this README's quotation of it). The round's classes over this
README and the commit message (names under NDA, logins and home paths, private links, access words) matched **1 line**: the post platform's
name inside the owner's verbatim words of 10:22:36 PST (Departures 1), kept verbatim as other committed records quote them; the commit
message read 0 lines and 0 sanitizer hits. The round's classes, run also over the collected text files, matched only words of the card's
and the workload's own output, kept as collected: the device layer's identity block's name for the card's on-chip scratch memory (12 lines
in each of 34 files: the 31 hosts' `host.err`, `config-start.err`, `config-end.err` and `sampler.err`), the same block that 1,558 committed
files under `docs/reports/data/` carry; sparse parity's own field naming its instance's hidden indices (one line in each of 13 files: each
pass's `host.json`, `stdout.txt` and `energy.json`, and the smoke run's `stdout.txt`), as in E189's committed record; and byte runs in the
4 binary `host.rec` files. **The unchanged reducer's fixed note** "assumed package power (RAPL is root-only)" (`energy_reduce.py`) is in
every `energy.json` here, **24 of 24**, kept as collected (a collected file is never edited).

## Files

| path | what |
|---|---|
| `passes/<configuration>/p<k>/` | one pass (E191.md 8.1), 24 directories: `stdout.txt` (the host's standard output, raw as collected: the runtime's `Opening device 1` inside the ledger host's line, or on a line of its own before sparse parity's), `host-raw.json` (the ledger programs: the host's own line as runner v2 reassembled it, which the frozen scorer reads), `host.json` (the reducer's input: the adapter's fields of the ledger host's line, or sparse parity's own verified line), `host.rec` (sparse parity's records), `host.err` (the host's stderr: its device-layer block names card 1), `telemetry.jsonl.gz` (the session's samples over the pass), `run.json` (energy.sh's marks, with the reader's record `host_line`), `pass.json` (the runner's marks), `energy.json` and `energy.txt` (the reducer's output, its `dir` set to this path) |
| `session/` | the session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`: its 207 files, plus `runner.rc`), scrubbed: `session.log` and `runner.out` (the session's lines), `runner.rc` (0), `queue.json` (the queue, `identity_ok` true, no stop, bound or early stop), `identity.json` (the identity gate's readings), `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err` (the config reads and their device-layer blocks: `/dev/et1_mgmt`, ID 1), `etwho-before.txt`, `etwho-identity.txt`, `commands.jsonl` (every command sent), `stop-path.json`, `anchors.json`, `sampler.err`, `telemetry.jsonl.gz` (the whole session: 9,493 samples), `MANIFEST.sha256`; no `STOP` (no early stop) |
| `session/smoke/<run>/` | the 8 smoke runs: `stdout.txt` (the host's standard output, raw), `host.err` (the host's stderr), `smoke.json` (the runner's reading, with the reader's record `host_line`) |
| `SHA256SUMS` | the collector's (`collect_e191.py`, 257 files): every file but this README, itself and `FILES.txt` |
| `FILES.txt` | the collector's list of every collected file, by path (257) |

## Next

The frozen scorer, after this commit only: `rb/s24_score_e191_v2.sh` runs `score_e191.py` (registered in `300d76e4`, unchanged) on this
committed directory alone and writes `scores-e191.json` (the four rules' words, E191-S1, S1T, S2 and S2T, with PASS, FAIL or NOT DECIDED,
and each configuration's errors); a later lane commits it beside this directory.

SPDX-License-Identifier: Apache-2.0
