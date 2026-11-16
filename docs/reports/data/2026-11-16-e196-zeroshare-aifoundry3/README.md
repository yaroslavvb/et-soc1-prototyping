# E196, 2026-11-16, aifoundry3 card 0 at 600 MHz as found: RAN WHOLE - the smoke, T1, T2 and 7 passes (0-6) in 48.07 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST, Q191's card lane `card-e196`, orchestrated from aifoundry2. The model session's proposal X14 (request
1113-x14-zeroshare version 3, posted Sun 15 Nov 2026 10:11:13 PST: the resident fp32 TensorFMA loop's clocked and data parts against graded
issue, with fields flipped and zeros shared). Registered as E196 in `2cf02aae` ([`E196.md`](../../../../tools/claims-v3/e196/E196.md)) with
its forecast sealed by sha256, kitted in `99bc9a38` ([`KIT.md`](../../../../tools/claims-v3/e196/KIT.md),
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e196/CARD-LANE-BRIEF.md)), verified (verify-e196: DOES NOT HOLD; fix-e196: FIXED, its
redaction R1 and dated notes 1-4 made before the land), landed and readiness-checked (ready-e196: READY WITH GAPS), all before any E196
datum; no E196 file changed since the kit (step 0: 56 of 56 anchor lines as stated at HEAD `250f825b`; step 2 and step 11: HISTORY OK).
Run on the owner's go of his standing words of Sun 15 Nov 2026 (10:05:42, 10:22:36, 17:21:16 PST), his "Try again" and his words of
21:51:09 PST, with G = this lane's booking of aifoundry3 at 03:48:42 PST Mon 16 Nov 2026 (departures 1 and 3). The passes and the train
anchors ran on the lab's unchanged sparsity host, the trains on the request's x14_host (E196.md section 3). Nothing was set on the card.*

**The freeze line:** the model session's sealed forecast is known to the lab only by its sha256,
`5c5acc1622e526aa20917a646a077763a630468ca2435ba3c05511408b148aba` (E196.md section 0). **No forecast number and no score are in this
directory:** the model session scores its sealed forecast privately, after this commit, against the prices the reduction's dated note
publishes. The session, T0 1794830144 = 03:55:44 PST, ran to its `session end` at 04:43:48 PST: **48.07 card-minutes** from its first card
command (03:55:44), against the registered estimate of about 49 (46-53) and the cap of 60.

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every arm, value, order, window,
threshold, stop, host assignment and the cap is **registered** (E196.md; the kit). The order check, the record counts by host, the cycle
range and the per-block peaks below are **desk arithmetic of the measured records** (`run/runs.jsonl`, `run/train.jsonl`,
`run/checks.jsonl`, `run/marks.jsonl` and `run/telemetry.jsonl.gz`, read at the desk), not prices and not rules. The reduced prices are
**not here**: step 13 (`rb/s24_reduce_e196.sh`, the registered `reduce_e196.py`) runs on this directory only after it is committed, and its
outputs are committed by a later lane in a dated note. The desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures and notes (dated Mon 16 Nov 2026, PST; 1-9 set by his go, the kit and the round's plan before the session; 10-13 after the collection, said so; all written here after the collection)

1. **The go, his words, verbatim, Sun 15 Nov 2026 (PST).** Standing: **10:05:42** "continue, all machines are up"; **10:22:36** "don't
   worry about discord post, just use the machines, nobody is using them" (E196.md 12 reads them as the go for each run once registered,
   kitted, verified and readiness-checked, with its registered items as its defaults); **17:21:16** "Feel free to use more cards in
   parallel, I don't need to reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is
   being used, feel free to use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); and
   "don't worry about hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before
   21:51:09). Beside them, a report of his words (not his own text), the round's Discussion at 19:34:12: "The aifoundry cards are all free
   right now (I can see it on the lab dashboard's live view, though a collector is running on them); feel free to use them." **His words
   name no experiment: the registered items are taken as their defaults** (E196.md 12): aifoundry3 card 0, 600 MHz as found, reads only,
   nothing set; about 49 card-minutes, cap 60; the 40-minute rests; one session; the window of E196.md 12.
2. **The card day: Mon 16 Nov 2026**, moved from Sunday by the round's weekly-usage-limit stop at about 18:05 PST Sun 15 Nov (E196 had not
   been booked and had sent nothing to any card then).
3. **G = the booking:** the card lane's `book.sh take aifoundry3 card-e196` printed BOOKED at **03:48:42 PST** Mon 16 Nov: last start
   G+1:30 and last end G+3:00 (E196.md 12 and its dated note 3), each rounded up to the whole minute: **05:19 and 06:49 PST**
   (`s02_window_e196.sh 2026-11-16 05:19 06:49`, written by step 1 at 03:53:55; the window file's `RB_GO_EPOCH`, 1794830035 = 03:53:55 PST,
   is the moment step 1 wrote it, not his go). The round's generic outer bound (G+3:30, 07:19) was not used: the registered, narrower last
   end binds. The session launched at 03:55:44 (before the last start) and ended at 04:43:48 (before the last end).
4. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every other
   etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE at 03:54:48), step 7's reads (et-who
   clean at 03:55:22), the session's holder check before its first card command (0 holder lines at the start) and its card lock held for
   each block, and `timeout 10` (no `-k`) on every device process.
5. **The host's package counter: not read** (his words do not name it): no E196 file has a step or option that reads it.
6. **A fresh network-access approval: nothing to name.** The session was orchestrated from aifoundry2, a lab box that reaches aifoundry3
   by the kit's ssh without a login link. The kit's login-link stop stayed live; no step met a login link (the round's file of checks held
   70 lines before and after every step).
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3; the box's interpreter was
   Python 3.12.3 (the build record's PYTHON line). The orchestrating session is the round's session on its yvb3 Claude account, which took
   the round over on Sat 14 Nov 2026 after aifoundry2 went down abruptly at about 16:53 PST on Fri 13 Nov.
8. **The rest and the order of the day's lanes.** The previous session of ours on aifoundry3 was E195's (session end 01:51:00 PST, data
   `97e144c3`): E196's committed rest rule, read on the box at step 7 (03:55:21) and again at step 9 (03:55:44), printed "rest: 124 minutes
   since E195's session end (2026-11-16 01:51:00 PST; dry sessions and blocks that opened no device skipped)" (40 required). Step 7's
   configuration read (03:55:22) was the day's first card command for the rests. The lane booked aifoundry3 with no other lane of ours in its
   collection span and no quiet-desk flag up, so its desk span (steps 0-2, 03:48:46-03:54:38) held no other lane's collection; aifoundry1
   card 1's lane (E199) ran beside it on its own box.
9. **THE HOST CHANGE as registered** (E196.md 3; `desk/host-change-e196.txt`): the passes and the train anchors on the lab's unchanged
   sparsity host, only the trains (and the smoke's premise runs and T1's first two processes) on the request's x14_host; both hosts built on
   the box by step 6 and pinned by sha256 in its build record and in `session/hashes.txt` (section 3). The records bear it out (section 2).
10. **Pass 6 fit** (a note after the collection; E196.md 6 registers "pass 6 only if it fits before the deadline"): pass 6 ran 04:39:12-
    04:43:29, inside DEADLINE 04:53:44; the session's line: "trains complete: 2 of 2; passes complete: 7 of 7 asked (pass 6 only if it
    fit)". Neither the deadline nor the end-stop (04:54:44) acted; no live stop fired; no stop file was written.
11. **The request's x14_host ran on a card for the first time** (ready-e196's gap 1; a note after the collection): its smoke premise runs (24
    launch records) and T1's first two processes passed the smoke gate, both trains completed (24 processes each), and every read-back of C
    read ok (108 of 108 records in `run/checks.jsonl`).
12. **The box build's kernel ELF differs as a file from the registration's desk build (`990807f4...`) and from the request's
    (`abbdbe40...`); its `.text` is the registered `8798e43c...` for both hosts** (the build record: "kernel_elf_same_as_desk_build ... lab
    no x14 no; as request.md's ... no (reported, never judged)"); step 6's gate checked the `.text` (ready-e196's gap 2).
13. **"Reads only" is true of the management node** (ready-e196's gap 5): as every runtime creation of the lab's runtime does, each host's
    creation also sends the ops node's abort on the card's submission queues; harmless on a card held alone (0 holder lines at the start,
    the card lock held for each block, aifoundry3 has one card).

## 1. Results first (measured; the card's own records)

| what | value | label |
|---|---|---|
| card-minutes, first card command to "session end" | **48.07** (03:55:44-04:43:48; cap 60; the session's "card time 2884 s from the first card command (cap 3600 s)"); step 7's read at 03:55:22 reported apart: 48.43 to the session end | measured (the session's clock); the 48.43 desk arithmetic |
| the cut order at the start | "the cut order: M = 60 minutes: M >= 53: every arm, passes 0-5 and pass 6 if it fits; DEADLINE 04:53:44 PST; the end-stop 04:54:44 PST"; the pass plan "PLAN runs=32 arms=28 dropped=- orphaned=-" | measured (the clock at the first card command) |
| blocks complete | facts' `blocks_after` [-1, 0, 1, 2, 3, 4, 5, 6, 101, 102]: the smoke, passes 0-6, T1 (101), T2 (102); "trains complete: 2 of 2; passes complete: 7 of 7 asked (pass 6 only if it fit)" | measured |
| device processes; pass launch records; train launch records; read-backs of C (X14CHECK) and those not ok | 437 (236 run processes, 50 train processes, 150 heater launches between runs, 1 heater check); 2,328; 700; 108 / 0 | measured (the process split desk arithmetic of `run/marks.jsonl`) |
| how the session ended | ended: "run_session_e196.sh rc 0"; the port's "session done (rc 0): 2328 pass launches, 700 train launches recorded"; session.rc 0; STOP none (facts' `stop` null) | measured |
| the smoke (the heater check; four arms on each host; two T1 processes) and its gate | "smoke gate passed" at 03:57:05; facts' `smoke_gate` [true, []]; the heater check rc 0 (die 50 C); the heater level 6 launches, board max 50.0 W against the 70 W ceiling (33 samples) | measured |
| runtime lines dropped from the hosts' stdout; host outputs that could not be read (no record written) | 0; none | measured (run_block_e196.py's marks) |
| telemetry samples, and those not at 600 MHz | 28,783 (03:55:46-04:43:47) / 0 | measured |
| board power, peak; die, peak (minshire[0]), with how many samples read it and the first | 53.79 W (1 sample, 04:40:06, pass 6); 62 C (44 samples, the first 04:09:12, pass 0) | measured |
| the opening and closing configuration reads | TDP 0 W / 65 C / 600 MHz / 523 mV at the start (03:55:46) and at the close (04:43:47) | measured (READ) |

Per block (desk arithmetic: each block's window from its own records' `t_start_ms`/`t_end_ms`; the telemetry samples inside it):

| block | window (PST) | samples | board peak | die peak | samples off 600 MHz |
|---|---|---|---|---|---|
| smoke (-1) | 03:56:06-03:56:55 | 488 | 51.01 W | 55 C | 0 |
| T1 (101) | 03:58:27-04:01:49 | 2,021 | 52.84 W | 60 C | 0 |
| T2 (102) | 04:02:59-04:06:17 | 1,980 | 52.88 W | 60 C | 0 |
| pass 0 | 04:07:26-04:11:44 | 2,579 | 53.58 W | 62 C | 0 |
| pass 1 | 04:12:45-04:17:01 | 2,555 | 53.65 W | 62 C | 0 |
| pass 2 | 04:18:04-04:22:20 | 2,554 | 53.60 W | 62 C | 0 |
| pass 3 | 04:23:21-04:27:39 | 2,578 | 53.63 W | 62 C | 0 |
| pass 4 | 04:28:40-04:32:50 | 2,497 | 53.61 W | 62 C | 0 |
| pass 5 | 04:33:52-04:38:10 | 2,586 | 53.74 W | 62 C | 0 |
| pass 6 | 04:39:12-04:43:29 | 2,572 | 53.79 W | 62 C | 0 |

## 2. Registered against happened

| registered (E196.md, KIT.md) | happened |
|---|---|
| aifoundry3 card 0, 600 MHz as found, nothing set; the opening read TDP 0 W and 600 MHz (E196.md 4 and 6) | `run/config-start.json` and `run/config-end.json`: TDP 0 W, 65 C, 600 MHz, 523 mV; 28,783 of 28,783 telemetry samples at 600 MHz (the minion clock); the die's minion rail 521-523 mV; nothing set |
| the 40-minute rest before the session (E196.md 10), after E195's | step 9's "rest: 124 minutes since E195's session end (2026-11-16 01:51:00 PST; ...)"; step 7 (03:55:21-03:55:22) read the same |
| the host assignment (E196.md 3) | `run/runs.jsonl`: `sparsity_host` for every pass run (2,240 records: 1,960 arm, 140 K.pi anchor, 140 burn-in), every train anchor (40) and the smoke's lab-host runs (24); `x14_host` for the smoke's premise runs (24); `run/train.jsonl`: `x14_host` for all 700 train records (T1's two smoke processes 28, T1 336, T2 336) |
| the smoke with both hosts, its gate and the kit's stop K1 (E196.md 6; KIT.md 4) | "smoke gate passed" (03:57:05); the gate's problems: none; the heater check and level as in section 1 |
| T1 and T2: 24 processes each, 13 launches after the calibration launch, SFFS and FSSF alternating (E196.md 2 and 6) | T1 (block 101) and T2 (block 102): 24 processes each, 14 records each (the calibration and 13); SFFS 168 and FSSF 168 records in each; their K.pi anchors (first and last, 10 records each) on the lab's host |
| passes 0-5 and 6 if it fits, the written order for aifoundry3 (E196.md 6) | passes 0-6 ran, each 32 runs of 10 launch records (320); **the run order SAME as `desk/order-e196-aifoundry3.txt` in 7 of 7 passes** (desk arithmetic: each pass's run sequence by `seq`, K.pi's burn-in, first and last by their roles) |
| the cut order (E196.md 6) | M = 60; DROP_ARMS none ("dropped=-") |
| the cap: 60 card-minutes; DEADLINE = first card command + 58 minutes or the last end - 2 minutes; the end-stop at the cap - 60 s | DEADLINE 04:53:44, the end-stop 04:54:44 (the window's last end 06:49 later); the session ended at 04:43:48: neither acted |
| the stops (E196.md 9: the lab's 65 W and 70 C, stopwatch.py's, the block's, the hosts' budgets) | none fired: facts' `stop` null; `run/stops.err` and `run/stopwatch.err` empty; no `run/STOP`. The registered predicted peak (E196.md 9): board about 54 W, die about 62 C; measured 53.79 W and 62 C |
| one sampler, `ettelem sample --every-ms 100` through E128's guard; no statistics reset | "sampler up (start 1)"; dmcmd_audit GO at step 2 and at the session's preflight (`session/dmcmd-preflight.txt`); no `--reset-ms` |
| every unchanged-host launch record "readback": "none"; ops = iters x minions (E196.md 7) | 2,304 of 2,304 `sparsity_host` records "readback": "none"; ops = iters x minions in 2,328 of 2,328; every record ok, 0 tensor errors, 0 non-zero rc |
| the pass cycle gate: within 0.5 % of 546 or 544 (E196.md 6) | cycles per op of every timed launch 544.000-546.001 on both hosts (2,072 on the lab's host, 20 on the request's; desk arithmetic); the records' `ghz` field (cycles over wall time) 0.5826-0.5998 |

## 3. The day's records

- **The steps** (Mon 16 Nov, PST): B 03:48:42 (booked); 0 03:48:46-03:53:47 (load 0.67; "GO-ANCHORS-E196: 56 of 56 as stated (HEAD
  250f825b... = GitHub main; status 0 lines)"); H 03:53:51 (LAB status 0 lines); 1 03:53:55 ("fits now: E196 (its 60 card-minutes)"); 2
  03:54:01-03:54:32 (the quiet-desk flag absent; the desk check inside the round's CPU slot and its no-device sandbox, rc 0; HISTORY OK;
  the preflight GO); 4 03:54:47 (FREE); 3 the post waived; 5 03:54:54 (synced, 45 paths, the box's copies at their pins); 6
  03:54:59-03:55:05 (built, the first of the day's two allowed starts); 7 03:55:21-03:55:22; 8 03:55:27-03:55:31 ("E196-DRY OK: 255 device
  calls (237 with the cut order), line for line the registered commands"); 9 03:55:44-03:55:49 (launched); 10 six bounded waits to 04:43:51
  (RUN-ENDED, MANIFEST-WRITTEN 37 files); 11 04:44:19-04:49:39 (collected).
- **The box build** (step 6; `session/hashes.txt`): the lab's unchanged sparsity host `3da15c4007925580...`, the request's x14_host
  `1fcd9cd6d2b6873c...`, both hosts' kernel ELF `d521e43248d00b4d...`, its `.text` `8798e43c4869a124...` (the registered one); "42 of 42
  refusals before anything (every registered command parses; --label refused by the lab's host)"; the box's sampler `16037641ab75bdbe...`;
  "BOXCHECK-E196 OK".
- **The copy-back:** the box's `MANIFEST.sha256` (37 files) and step 11's "COPY-BACK EXACT: every file of the box's MANIFEST.sha256 (37) at
  its sha256, nothing else but session.rc"; the collection's own `SHA256SUMS` (40 entries: every file but itself; this README is not in it).
- **The scrub** (step 11): the collector's scrub read clean (no home-directory path and no login left); the desk-path gates "nopath ... 0 hit(s): CLEAN" and "nopath_spell
  ... 0 hit(s): CLEAN"; the history check again after the collection: "HISTORY OK".
- **The interpreters:** on the box Python 3.12.3; at the desk `/usr/bin/python3` 3.12.3.
- **The commits:** the registration `2cf02aae` and the kit `99bc9a38`, both ancestors of this data commit (steps 0 and 2 read them at HEAD
  `250f825b`). The data commit's own sha is in the repository's history.

## Device commands sent

READs only: step 7's configuration read through the lab's guard (`ettelem config`) and `et-who` (03:55:22); the dry pass on the kit's
doubles (no device); the session's holder checks (`et-who --check`, which sends no device command), its opening and closing `ettelem
config` and the one `ettelem sample --every-ms 100`, all through E128's guard (dmcmd_audit GO, 11 send sites, every one a READ: KIT.md
section 6); the E78 heater between runs; both hosts opened the ops node only (`createPcieDeviceLayer(true, false)`; the runtime's launches,
copies and allocations, and its creation's abort of the card's submission queues, note 13). No set, no reset, no statistics reset, no
firmware query, no PMIC command.

## Privacy and the public-text scan

Our box login is masked in every collected file; no other account's name, holder line or process entry is in this directory (step 11's
scrub; the tree scrub's check again before the commit: "scrub-tree: OK (28 files in 4 directories read, 0 left)"). Before the commit the
round's public-text scans read this directory, this README and the commit message. The path scan read 29 text files and 1 .gz file of the
collection: 0 hits in them. The tier scan's matches: this README's line quoting his words about the post; the runtime's device-configuration
prints in `run/stderr.txt` (5,244 lines) and `run/sampler.err` (12 lines), which name the card's own on-chip memory by the word the scan's path class lists, not a path;
and one tile of binary data (`run/gen/tiles/lab_a_zeros_b_randn.bin`) whose bytes happen to match a text pattern. No number from any
private source; no forecast number (the forecast is sealed: only its sha256 is here).

## 4. Files

| path | what |
|---|---|
| `session/` | the wrapper's files: `session.log`, `first-card-command.txt`, `etwho-start-holders.txt` (0), `hashes.txt` (both hosts, both kernels, the sampler), the pins (`pins-registration.txt`, `pins-kit.txt`, `pins-shared.txt`) and `dmcmd-preflight.txt`, the port's output `run_session.out`, `MANIFEST.sha256` (the box's manifest), `session.rc` |
| `run/` | the port's OUT as the box wrote it: `session.log`, `config-start.json`, `config-end.json`, `runs.jsonl`, `train.jsonl`, `checks.jsonl`, `marks.jsonl`, `stderr.txt` (the hosts'), `sampler.err`, `stopwatch.err`, `stops.err`, `gen_check.json`, `gen/` (`arms.json` and the tiles the session generated), `SESSION_DONE`, and `telemetry.jsonl.gz` (gzip, no name, mtime 0; its unpacked bytes are the box's: `MANIFEST.sha256`) |
| `facts-e196.json` | the collector's facts (no reduced price) |
| `SHA256SUMS` | every collected file, paths beside it (not this README) |

## 5. Re-make it

From the top of the repository, nothing here opens a device; set D to this directory and R to an empty folder outside the repository,
then run the rest as they stand:

    D=docs/reports/data/2026-11-16-e196-zeroshare-aifoundry3; R=<an empty folder outside the repository>
    (cd "$D" && shasum -a 256 -c SHA256SUMS)
    mkdir -p "$R/run/gen" && cp "$D"/run/runs.jsonl "$D"/run/train.jsonl "$D"/run/checks.jsonl "$D"/run/marks.jsonl "$R/run/" && cp "$D/run/gen/arms.json" "$R/run/gen/"
    [ -f "$D/run/STOP" ] && cp "$D/run/STOP" "$R/run/"
    gzip -dc "$D/run/telemetry.jsonl.gz" > "$R/run/telemetry.jsonl"
    for p in runs.jsonl train.jsonl checks.jsonl marks.jsonl telemetry.jsonl; do grep -q "$(shasum -a 256 "$R/run/$p" | cut -d' ' -f1)  ./run/$p" "$D/session/MANIFEST.sha256" && echo "run/$p: the box's bytes" || echo "run/$p: NOT the box's bytes"; done
    cmp "$D/run/gen/arms.json" tools/claims-v3/e196/proposal/src/arms.json && echo "arms.json: the registered table"
    /usr/bin/python3 -I -B tools/claims-v3/e196/reduce_e196.py "$R/run" --readback-none-ok --json "$R/x14-e196.json"
    /usr/bin/python3 -I -B tools/claims-v3/e196/check_e196.py "$R/run" "$R/x14-e196.json" --out "$R/checks-e196.json"

The reduction is `reduce_e196.py` at its registered sha256 (`c58c6690...`), run as E196.md section 7 writes it; step 13
(`rb/s24_reduce_e196.sh`) runs exactly these lines on the committed directory, and a later lane commits their outputs with a dated note
(no score).

## Next

The reduction (step 13) on this directory once it is committed; its outputs in a dated note by a later lane. The model session scores its
sealed forecast privately. On aifoundry3, the next session of ours (E197) no earlier than 05:23:48 PST Mon 16 Nov (40 minutes after this
session's end).

SPDX-License-Identifier: Apache-2.0
