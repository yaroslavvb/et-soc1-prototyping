# E191: the blind day on aifoundry1 card 1, Sun 15 Nov 2026 - STOPPED at the smoke gate by a kit defect: no pass ran, no data; the identity gate passed (card 1 only), reads only, nothing set, card 0 never opened

*Sun 15 Nov 2026 (week 46), PST, Q182's card lane `card-e191`, orchestrated from aifoundry2. Registered in `300d76e4`
([`E191.md`](../../../../tools/claims-v3/e191/E191.md)), its dated note 1 `8c8f825f`, and kitted in `eb1ac923`
([`KIT.md`](../../../../tools/claims-v3/e191/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e191/CARD-LANE-BRIEF.md)), all
before any E191 datum. The session, T0 1794766494 = 10:14:54 PST, ended at 10:14:56 PST after **about 2 s (0.02 card-minutes from its
first card command)**, at its smoke gate, before any pass: the second smoke run's own line was split on its standard output, so the
runner could not read its status (What ran, and Departures 8). Reads only. **The day's post: none.** The owner's go did not name the post
route; the round read it with his Saturday words as no post (Departures 2).*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every plan figure, threshold and rule
is **registered** (E191.md, `plan-e191.json`, `forecast-e191.json`). The reading of why the smoke failed is a **desk reading after the
collection (post hoc)** of the collected `stdout.txt` and of the kit's code; nothing in it changes a registered item or a frozen number.
No pass ran, so no forecast is set beside anything here, and the four rules' words come only from the frozen scorer after this commit. The
desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## What ran (measured)

- **Card:** aifoundry1 card 1, **600 MHz in all 12 samples** of the session's 10 Hz telemetry (10:14:54.917-10:14:56.018 PST; none off
  600 MHz: `queue.json` > `off_clock` is empty). `ettelem config` through the kit's guard at the session's start (10:14:54) and end
  (10:14:56): TDP 65 W, threshold 65 C, 600 MHz, `minion_mv` 499, the same at both ends. **Nothing was set.** `since_reset_ms` -1 in every
  sample: no statistics reset.
- **The identity lines, as the session log reads them:**
  - `config start: TDP 65 W, threshold 65 C, minion 600 MHz, minion_mv 499 (read, nothing set); identity (a): /dev/et1_mgmt, device ID 1, minion_mv below 510`;
  - `identity (b): et-who with the sampler running: ours on card 1 2 (on /dev/et1_mgmt 1), ours on card 0 0, another login's 0; the sampler holds /dev/et1_mgmt only`;
  - the smoke hosts: `ledger-selftest` "no device (the self-test)"; `copy-64m-random` "card 1" (its `host.err` block: PCIe target
    `/dev/et1_ops`, physical device ID 1; the node it held, `/dev/et1_ops`);
  - `config end: ... minion_mv 499; its identity card 1`.
  THE IDENTITY GATE (note 1, item 3) passed: `queue.json` > `identity_ok` true.
- **Card session:** T0 1794766494 = 10:14:54 PST to its `session end` at 10:14:56 PST; from the first card command (10:14:54.897) to the
  close (10:14:56.143): **1.246 s, 0.02 card-minutes**, against the registered estimate of about 95 and the cap of 110. `runner.rc` 16.
- **The sequence:** the box check passed (aifoundry1, `ET_DEVICES=1`, the reader at its pin, today's builds with their records); the start
  config read and identity (a); the sampler (attempt 1, every 100 ms); identity (b); **the stop-path test passed** (the board, die and
  clock lines each tripped on live samples within 0.2 s and each refused a start); then the ramped smoke:
  - `smoke ledger-selftest: rc 0, ok (0.0 s)`;
  - `smoke copy-64m-random: rc 0, FAILED (0.3 s); the host's card: card 1`;
  - `smoke gate failed: copy-64m-random: rc 0, status None`.
  The six later smoke runs (copy at 64 MiB zeros and 1 GiB random, SHA-256, the two sorts, sparse parity) did not start; sparse parity's
  host never opened the card. Then the closing config read and `session end`. **No idle anchor, no pass, no counters arm** (dropped by the
  kit in any case).
- **Why the smoke read FAILED (post hoc, desk reading of the collected files and the kit's code).** The host's own line, read whole, says
  the run was good: `status` "PASS", 2048 of 2048 records good, 0 bad, 0 mismatches, 67,108,864 of 67,108,864 units, one launch of
  0.0064 s. But the line reached the runner in two pieces: the ledger host prints its line in parts (`workloads/ledger/host/main.cpp`, the
  head at lines 478-492 before it opens the card, the rest from line 621 after its launches), and a line `Opening device 1`, which
  aifoundry1's device runtime prints on standard output when a host opens card 1 (it is not in the ledger host's source; earlier lab
  readers skip it, `workloads/memhier/analyze.py` line 125), fell between the two parts. The runner's parser (`e191_common.py`
  `last_json`, lines 134-141) takes the last line that begins with `{`, which was the broken head; it does not parse, so the status read
  None and the gate failed (`run_e191.py` line 691). The same host source passed E189's smoke on aifoundry3 card 0 on Sat 14 Nov, whose
  runtime prints no such line (E189's committed `stdout.txt` is one unbroken line). Every ledger pass reads its host's line through the
  same parser (`run_e191.py` line 791), so a session past the smoke would have met the same split (a desk check of code). The kit named
  the real hosts' first meeting with card 1 as not reachable on the desk (KIT.md section 8, items 2 and 3; the readiness check's GAPS 1);
  the ledger host's source is unchanged since `46a16bd0`. The gate failed safe, as E191.md section 12 registers ("the smoke fails ... no session (or no further pass): no data").
- **No stop line tripped.** The highest live readings were **29.25 W board** and **48 C `minshire[0]`**, against the stops 65 W and 70 C.
- **No BOUND line** (`queue.json` > `bound` is empty), **no early stop** (`early_stop` null; no stop file, no signal), **no "the sampler is
  not live" line** (`sampler_lines_not_live` 0; `passes_sampler_not_live` empty), no restart of the sampler.
- **The host's package counter was not read** (step 9 ran without `--rapl-allowed`).

## The passes (measured; none ran)

No pass ran: the session ended at its smoke gate, before idle anchor 1. There is no `passes/` directory, no reducer output and no mean. All
24 registered passes (four of each of the six configurations, `plan-e191.json`'s order) are **NO DATA** by E191.md section 12; none is a
failed run and none is a failed prediction.

| configuration | passes registered | passes run | reading |
|---|---:|---:|---|
| copy, zeros | 4 | 0 | NO DATA (the smoke gate) |
| copy, random | 4 | 0 | NO DATA (the smoke gate) |
| SHA-256 | 4 | 0 | NO DATA (the smoke gate) |
| sort, sorted | 4 | 0 | NO DATA (the smoke gate) |
| sort, shuffled | 4 | 0 | NO DATA (the smoke gate) |
| sparse parity | 4 | 0 | NO DATA (the smoke gate) |

## Registered against happened

| item | registered (E191.md, note 1, the kit) | happened (measured) |
|---|---|---|
| card, clock, config | aifoundry1 card 1, 600 MHz as found, reads only | card 1; 600 MHz in 12 of 12 samples; TDP 65 W / 65 C / 600 MHz, 499 mV at both ends; nothing set |
| the identity gate (note 1, item 3) | the start config names `/dev/et1_mgmt` and device ID 1, `minion_mv` above 450 and below 510; et-who with the sampler: ours on card 1 only, one on `/dev/et1_mgmt` | passed: `/dev/et1_mgmt`, ID 1, 499 mV; ours on card 1 2 (1 on `/dev/et1_mgmt`), on card 0 0, another login's 0 |
| the reboot gate | aifoundry1 up since before E82's firmware read (2026-10-31 13:45:24 PDT) | booted 2026-10-26 15:02:04 PDT: ok (steps 4 and 9) |
| card time | about 95 card-minutes, cap 110 (no pass after 108) | 0.02 card-minutes (1.246 s) |
| passes | 24, in `plan-e191.json`'s order | 0: the session ended at the smoke gate |
| stop-path test and smoke | before any pass; a failed smoke is a gate: no session, no data (section 12) | the stop-path test passed; the smoke's self-test ok, `copy-64m-random` FAILED (its status unreadable, Departures 8), six runs not started; the gate ended the session |
| stops | board 65 W, `minshire[0]` 70 C, the clock off 600 MHz | none tripped (29.25 W, 48 C; no sample off the clock) |
| die gate and band | gate at 60 C, at most 10 minutes; forecast band 52-60 C | not reached (no pass); the die read 48 C at the smoke |
| idle anchors | three of 2 minutes | none (the session ended before anchor 1) |
| the counters arm | dropped by the kit (KIT.md 5) | not run |
| builds | at most two starts a Pacific day; each kernel through THE KERNEL GATE; hosts by their behaviour; the `ET_DEVICES` reading | one start (10:13:38-10:13:49 PST on the box); both KERNEL OK (ledger ELF `2b2eb281...`, `.text` `5e00e45a...`; sparse parity ELF `6ee70c92...`, `.text` `3e14be32...`, each `.text` the registered one and each ELF the pin of the toolchain that reads "() 15.1.0"); HOST-BEHAVIOUR OK (10 and 3 checks); `ET_DEVICES` read yes for both |
| the dry pass | rc 0, on stand-ins | `E191-DRY rc=0 passes=6 dry-check=1 identity-lines=2` (10:14:06-10:14:29 PST on the box) |
| the rest | at least 40 minutes after our last real session on aifoundry1 | 2506 minutes since E190's session end (Fri 13 Nov 2026, 16:27:55 PST) |
| the window | from his go at G: last start G+1:30, last end G+3:30 | last start 11:36, last end 13:36 PST (Departures 7); launched at 10:14:54, ended 10:14:56 |
| the host's package counter | not read unless his go allows it | not read |
| the post | the day's etiquette (E191.md 13) | none: the route not named; read as no post (Departures 2) |

## Departures and notes (dated Sun 15 Nov 2026, PST; 1-7 set by his go and the round's brief before the session; 8-10 after the collection, said so; all written here after the collection and before the scorer ran)

1. **The go.** The owner's words, verbatim, at **10:05:42 PST**: "continue, all machines are up". They answer the orchestrator's message
   that asked for Sunday's go for E191 (aifoundry1 card 1: about 95 card-minutes, cap 110, 600 MHz as found, reads only, nothing on card 0)
   and E193 (aifoundry3: sittings of 42 and 24 card-minutes) and for the day's post route. **G = 10:05:42 PST.** The registered items stand
   unchanged: his words do not name them one by one; they answer a message that named them.
2. **The post route was not named.** The readiness check's go lines asked that a go for Sun 15 Nov name it. The orchestrator read his "all
   machines are up" with his Saturday words "it's fine not to announce, the cards are unused" (20:01:31 PST, Sat 14 Nov) as **no post
   today**: no claim and no release, a departure from E191.md 13's etiquette sentence. He can still ask for a post. Every other etiquette
   check stood: the look before the session (et-who, who, uptime, the holder rule: FREE on both cards at 10:13:16), step 7's reads (both
   cards free at 10:14:01), card 1's lock held by the session to its end, the runner's holder read, `timeout 10` a host process.
3. **The host's package counter: not read** (the default; his go did not allow it): step 9 ran without `--rapl-allowed`.
4. **A fresh network-access approval for aifoundry1: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches
   aifoundry1 without that check. The kit's login-link stop stayed live (an exit 11 with its lock line ends the day's box steps); no step
   met a login link.
5. **The desk.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3, as KIT.md names.
6. **The orchestrator.** The orchestrating session is the round's session on its yvb3 Claude account, which took the round over on Sat 14
   Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov.
7. **G and the window.** From his go at G = 10:05:42 PST: last start G+1:30 = 11:35:42 and last end G+3:30 = 13:35:42, each rounded up to
   the whole minute, inside the Pacific day 2026-11-15: **11:36 and 13:36 PST** (`s02_window_e191.sh 2026-11-15 11:36 13:36`, written by
   step 1 at 10:12:39). The window file's `RB_GO_EPOCH` (1794766359 = 10:12:39 PST) is the moment step 1 wrote it, not his go (a note).
   Step 9's rest rule read 2506 minutes since E190's session end.
8. **The smoke gate (after the collection).** Not a departure: a gate, as E191.md section 12 registers. Its cause, read after the
   collection (post hoc), is in What ran: a kit defect, the runner reading a host line that aifoundry1's runtime split. Nothing collected
   was edited.
9. **No second session today (after the collection).** The kit has no relaunch rule (the readiness check's GAPS 2), and its collector
   refuses an existing directory, so this directory is the day's whole record. A later E191 day needs the defect fixed in a dated kit note
   first; that is the round's decision, not this record's.
10. **Notes, not departures.** Step 10's wait looks for the session by the name `session_e191.sh`, the script step 9 launched (read before
    step 9; one call, which read the gate stop with 20 files in the manifest). The build step's wait printed "the dry pass a1-build-e191
    ended rc 0" for the build job: the kit's wording, not a second dry pass. The card time came in far under the estimate because the
    session ended at its gate.

## Device commands sent

Reads only. The session's `commands.jsonl` lists 7 commands, each with `ET_DEVICES=1` and card 1's lock: et-who twice (no device);
`ettelem config` at the start and the end and `ettelem sample --every-ms 100` (no `--reset-ms`), each through the kit's guard, which passes
`config` and `sample` only; the ledger host's self-test (no device); and the ledger host's one card run (`copy`, 64 MiB random, one launch),
which opened card 1's ops node only. Step 7's config read before the session (10:14:01 PST) was the same read; the dry pass ran on
stand-ins. The device-command audit (`dmcmd_audit.py` through `preflight_e191.sh`) read **GO, 16 send sites, 0 disallowed, every one a
READ** at step 2 on the desk and again on the box after the build. No set of any kind (TDP, threshold, clock, voltage), no reset, no
statistics reset, no firmware-revisions query, no power cycle. Card 0 was never opened: every command carried `ET_DEVICES=1`,
identity (b) read nothing of ours on card 0, and the one host that opened a device named card 1.

## Privacy and the public-text scan

The collector's scrub ran (the box's home path became `~`, the box login `<login>`), and the desk-path gate read CLEAN over the 24 files it
read. The public-text scan before the commit read every text file of this directory, the text inside its `.gz` file and this README, with
the lab's sanitizer (`tools/timeline/sanitize_extracts.py`: its fixed list and the local privacy table) plus the private-network, Mac-home,
scratch and e-mail patterns (24 text files and the one `.gz`: **0 hits**), and the round's classes over this README and the commit
message (names under NDA, logins and home paths, private links, access words: **0 lines**). The round's classes, run also over the
collected text files, matched only one word of the device layer's identity block, its name for the card's on-chip scratch memory (12
lines in each of `config-start.err`, `config-end.err`, `sampler.err` and the copy's `host.err`), the same block that 1,384 committed files
under `docs/reports/data/` carry; kept as collected. No pass reached the reducer, so no `energy.json` exists here and the unchanged reducer's
fixed note on assumed package power appears in no file (0 of 0).

## Files

| path | what |
|---|---|
| `session/` | the session directory as copied back (COPY-BACK EXACT against its `MANIFEST.sha256`: its 20 files, plus `runner.rc`), scrubbed: `session.log` and `runner.out` (the session's lines), `runner.rc` (16), `queue.json` (empty queue, `identity_ok` true, no stop, bound or early stop), `identity.json` (the identity gate's readings), `config-start.json`, `config-start.err`, `config-end.json`, `config-end.err` (the config reads and their device-layer blocks: `/dev/et1_mgmt`, ID 1), `etwho-before.txt`, `etwho-identity.txt`, `commands.jsonl` (every command sent), `stop-path.json`, `sampler.err`, `telemetry.jsonl.gz` (the whole session: 12 samples), `MANIFEST.sha256` |
| `session/smoke/<run>/` | the two smoke runs that started, `ledger-selftest` and `copy-64m-random`: `stdout.txt` (the host's standard output; the copy's is the split line), `host.err` (the host's stderr: the copy's device-layer block names card 1), `smoke.json` (the runner's reading) |
| `SHA256SUMS` | the collector's (`collect_e191.py`, 22 files): every file but this README, itself and `FILES.txt` |
| `FILES.txt` | the collector's list of every collected file, by path (22) |

## Next

The frozen scorer, after this commit only: `rb/s24_score_e191.sh` runs `score_e191.py` (registered, unchanged) on this committed directory
and writes `scores-e191.json` (the four rules' words and each configuration's errors; with no pass, every configuration is NO DATA); a
later lane commits it beside this directory. Any later E191 day waits for a dated kit note on the split host line (Departures 9).

SPDX-License-Identifier: Apache-2.0
