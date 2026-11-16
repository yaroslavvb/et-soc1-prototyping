# E202, 2026-11-16, aifoundry3 card 0 at 600 MHz as found: one pass over MNIST in int8: RAN WHOLE (the smoke, the scored scp pair T Z Z T T Z Z T, the dram pair REPORTED) in 8.37 card-minutes, reads only, no stop

*Mon 16 Nov 2026 (week 47), PST. E202, registered before any datum (`68abdd97`, [`E202.md`](../../../../tools/claims-v3/e202/E202.md);
forecasts frozen in `forecast-e202.json`, sha256 `d1dc7679...`), on the program commit (`4a7b48b1`, `workloads/mnistmlp`), kitted
(`ad0a1427`, [`KIT.md`](../../../../tools/claims-v3/e202/KIT.md), [`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e202/CARD-LANE-BRIEF.md)),
verified (verify-e202: HOLDS WITH FIXES; fix-e202: FIXED, before the land) and readiness-checked (ready-e202: READY WITH GAPS), all before
any E202 datum; no E202 file changed since the kit (step 0: "104 of 104 as stated" at HEAD `c45b2683`; steps 2 and 11: HISTORY OK). Q198's
card lane `card-e202`, orchestrated from aifoundry2. Run on the owner's go (his standing words of Sun 15 Nov 2026 and his matmul focus of
Mon 16 Nov 2026: departure 1). The lab's own network (784-1792-1792-1792-1792-10, int8: uint8 activations x int8 weights -> int32 on the
TensorIMA8A32 tiles), the trained and the random weight configurations (E202.md 2), every label and checksum checked bit for bit by the
host on the card. Nothing was set on the card.*

**Labels.** Every figure from the session is **measured** (the card's own records in this directory). Every arm, order, window, threshold,
stop and the cap is **registered** (E202.md; the kit). The per-configuration means, the per-image and per-multiply-add figures and the
card-minute sums below are **desk arithmetic of the measured records**, not prices and not verdicts. **No score is here:** the frozen
scorer (step 13, `score_e202.py`) runs on this directory only after it is committed, and a later lane commits its words beside it. The
desk steps ran under `/usr/bin/python3` 3.12.3 on aifoundry2.

## Departures, dated (Mon 16 Nov 2026, PST; placed before the results, as the round's go asks)

1. **The go, his words, verbatim (quoted without links).** Sun 15 Nov 2026: **10:05:42** "continue, all machines are up"; **10:22:36**
   "don't worry about discord post, just use the machines, nobody is using them"; **17:21:16** "Feel free to use more cards in parallel, I
   don't need to reserve them (things are automatically updated on [the lab dashboard's page]), currently I see only 1 card is being used,
   feel free to use more in parallel"; **"Try again"** (received at or before 21:28:59; its exact second not known); "don't worry about
   hitting the limit, I will use a reset, feel free to run things overnight and in parallel" (received at or before 21:51:09); "Make sure
   to incorporate suggestions from Fable when planning experiments" (received between 21:55 and 22:07:09). Mon 16 Nov 2026, received at or
   before 09:48:24: "I want you to focus on the matte mold most of all, ... just go as far as possible on the matte mold, on the FME, yeah,
   on the matmul operation." (a voice transcription: the matmul; the round kept E202 as an int8 matmul application). Beside them, reports
   of his words posted on the round's Discussion (not his own text): Sun 19:34:12 "The aifoundry cards are all free right now (I can see it
   on the lab dashboard's live view, though a collector is running on them); feel free to use them."; Mon 11:01:08 "There's no usage
   limit; feel free to use all the cards without restriction, since they look free every time I check the dashboard." **His words name no
   experiment: the registered items are taken as their defaults** (E202.md 8-10): aifoundry3 card 0, 600 MHz as found, reads only,
   nothing set; about 17-29 card-minutes, cap 35; the 40-minute rest; one session; the window of E202.md 10.
2. **G = the booking:** the card lane's `book.sh take aifoundry3 card-e202` printed BOOKED at **12:21:01 PST** Mon 16 Nov: last start
   G+1:30 and last end G+3:30 (E202.md 10), each rounded up to the whole minute: **13:52 and 15:52 PST** (`s02_window_e202.sh 2026-11-16
   13:52 15:52`, written by step 1 at 12:21:41; the window file's `RB_GO_EPOCH` 1794860501 = 12:21:41 PST is the moment step 1 wrote it, not
   his go). The session launched at 12:24:48 (before the last start) and ended at 12:33:10 (before the last end).
3. **The post: waived.** The owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST. No claim (step 3) and no release. Every
   other etiquette check stood: k6's look before the session (et-who, who, uptime, the holder rule: FREE at 12:22:07), step 7's reads
   (et-who clean at 12:24:24), the session's holder check before its first card command ("no holder of another login; no other user's
   device process"), card 0's lock held for the session, and a plain `timeout 10` (never `-k`) on every device process.
4. **The host's package counter: not read** (E202.md 10): every burst's record reads "rapl": "not read: the lab's default (E202.md 10)".
5. **E201 did not run first.** E202.md 3 and 10 say "after E201"; the owner's matmul focus of Mon 16 Nov 2026 (departure 1) paused E201 and
   E204 and kept E202 (KIT.md 4 item 25 and CARD-LANE-BRIEF.md 1 read this case before any datum). E202 ran after the box's last session of
   ours, E197's sitting 1 (session end 06:10:45 PST, data `ae3c1ee0`), and its 40-minute rest: the rest by the clock (from E197's committed
   session log) was 370 minutes at the booking; E202's committed rest rule, read on the box, printed "rest: 373 minutes since E197's session
   end (2026-11-16 06:10:45 PST; dry sessions and blocks that opened no device skipped)" at step 7 (12:24:24) and "rest: 374 minutes ..." at
   step 9 (12:24:53) (40 required).
6. **The R rule: no smaller R.** The registered rule (plan_e202.r_rule) chose R = 96 on all four arms from their own R = 1 smokes; the
   kit's host timeout cap (KIT.md 4 item 23) took no smaller R (`R_registered_rule` equals `R` on every arm in `session-facts-e202.json`;
   the four arms' smokes predicted an R = 96 launch of 2.911-2.919 s against the 7.5 s cap, with the host's time left at its launch
   9.01-9.02 s).
7. **The desk and the orchestrator.** Every desk step ran on aifoundry2 (Linux) under `/usr/bin/python3` 3.12.3 (the collection and the
   reducer with numpy 1.26.4); the box ran the session with its own `python3` (3.12.3 by the readiness lane's read-only look at 11:40:32 PST;
   not re-read by this lane). The orchestrating session is the round's session on its yvb3 Claude account.
8. **Ledger v3.** In HEAD at step 2 with E202's v3 note (step 2's line "ledger v3 in HEAD yes, E202's v3 note in HEAD yes (V3NOTE CHECK
   PASS)"); its REPORTED readings come after the data commit from `v3note_e202.py --score` (S2T-v3; S1, S1T and S2 equal v2's by
   construction), beside the scorer's words, never a verdict.
9. **"Reads only" is true of the management node** (ready-e202's gap 8): as every runtime creation of the lab's runtime does, each host's
   creation also sends the ops node's abort on the card's submission queues; harmless on a card held alone (et-who empty, card 0's lock held,
   aifoundry3 has one card).
10. **The card time ran shorter than the plan's estimate** (a note after the collection): 8.37 card-minutes against the registered estimate
    of about 17 at the point (29 at the slow end) and the cap of 35. The plan's fixed parts (12.0 minutes: checks, smoke, anchors, closing)
    counted its checks, the look and the dry listing, which the runbook ran before the session's first card command; no die-gate wait
    occurred (0.0 s before every process); every planned process ran.

## Results (measured: the session's own records; the scorer's words follow after the data commit)

| what | value | label |
|---|---|---|
| card-minutes, the session's first card command to its close | **8.37** (`config start` stamped at 12:24:48.516; the close at 12:33:10.674; cap 35; no burst after 33); step 7's config read at 12:24:24 PST (`e202-step7.txt`), reported apart: 8.78 to the close | measured (the session's clock); the 8.78 desk arithmetic |
| the smoke: T-scp, Z-scp, T-dram, Z-dram, ACC | every one rc 0, core PASS, status PASS; logits PASS on the four `--debug-logits` arms (ACC: not checked, as registered); the gate: "T-scp and Z-scp read core PASS: the scp pair is scored" | measured (the host's own --out files) |
| the on-card test accuracy (ACC, the trained network on the 10,000-image test split) | **9,849 of 10,000 = 98.49%**, equal to the model's 98.49% (every label is checked against the model's expected file) | measured |
| the R rule, each arm from its own R = 1 smoke | R = 96 on trained-scp, random-scp, trained-dram and random-dram; the registered rule's R the same on every arm (KIT.md 4, item 23: no smaller R) | measured (the cycle counter) and registered (the rule) |
| one pass alone (R = 1), each smoke process: kernel seconds (hart0_cycles.max / 600 MHz) | T-scp 0.03334 s, Z-scp 0.03329 s, T-dram 0.03329 s, Z-dram 0.03319 s; ACC (10,000 images) 0.00825 s (E202.md 5: about 34 ms forecast for the training split, REPORTED only, never scored) | measured (the cycle counter), REPORTED |
| bursts run, set aside, and each arm's end | 12 of 12 ran (8 scored, 4 REPORTED), every host rc 0, status PASS, core PASS, its checks good; none set aside; no arm ended early | measured |
| how the session ended | "session end (T0 1794860688)" at 12:33:10; queue.json stop: none; runner.rc 0 (the queue ran); no crash; the box's MANIFEST.sha256 118 files, COPY-BACK EXACT | measured |
| telemetry samples, and those at 600 MHz | 5,012 / 5,012; off the clock: none | measured |
| board power, peak; minshire[0], peak | **39.5 W**; **54 C** (stops 65 W, 70 C; the registered predicted peak 41.3-42.0 W at the points, band tops 54.9 W scp and 62.0 W dram) | measured |
| the opening and closing configuration reads | TDP 0 W, 65 C, power state max_power, minion 600 MHz, 523 mV at both ends (the closing read sent once et-who read the card free and our sampler had stopped) | measured (READ) |

**Per burst** (the reducer, `energy_reduce.py`, unchanged: J over idle a launch is `board.j_per_solve`, J with the card at rest a launch
`board.j_per_solve_total`; kernel seconds hart0_cycles.max / 600 MHz; wall seconds the host's own `wall_s`; a pass = a launch / R, an image
= a pass / 60,000; "busy W" the energy catalogue's busy average over the launch; every burst's reducer `ok` and no hard flag):

| order | burst | label | R | die at start | kernel s a launch | wall s a launch | J over idle a launch | J at rest a launch | J over idle a pass | J at rest a pass | kernel ms a pass | busy W | die C before / busy / after |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | trained-scp/b1 | scored | 96 | 49 C | 2.8266 | 2.8271 | 38.665 | 107.378 | 0.40276 | 1.11852 | 29.4433 | 37.71 | 50.0 / 51.04 / 50.0 |
| 2 | random-scp/b1 | scored | 96 | 50 C | 2.8262 | 2.8266 | 38.227 | 107.790 | 0.39820 | 1.12282 | 29.4395 | 38.45 | 50.0 / 51.58 / 51.0 |
| 3 | random-scp/b2 | scored | 96 | 50 C | 2.8261 | 2.8265 | 37.707 | 107.689 | 0.39279 | 1.12176 | 29.4387 | 38.52 | 50.0 / 51.78 / 51.0 |
| 4 | trained-scp/b2 | scored | 96 | 51 C | 2.8266 | 2.8272 | 38.671 | 108.139 | 0.40283 | 1.12645 | 29.4442 | 38.03 | 51.0 / 51.91 / 51.0 |
| 5 | trained-scp/b3 | scored | 96 | 51 C | 2.8265 | 2.8270 | 38.215 | 108.077 | 0.39807 | 1.12580 | 29.4429 | 38.17 | 51.0 / 52.22 / 51.0 |
| 6 | random-scp/b3 | scored | 96 | 51 C | 2.8264 | 2.8269 | 38.895 | 109.219 | 0.40516 | 1.13770 | 29.4416 | 38.57 | 51.0 / 52.50 / 51.5 |
| 7 | random-scp/b4 | scored | 96 | 51 C | 2.8265 | 2.8268 | 38.071 | 108.695 | 0.39658 | 1.13224 | 29.4425 | 38.77 | 51.0 / 52.70 / 52.0 |
| 8 | trained-scp/b4 | scored | 96 | 51 C | 2.8266 | 2.8270 | 36.220 | 106.984 | 0.37729 | 1.11441 | 29.4442 | 38.22 | 51.0 / 52.71 / 52.0 |
| 9 | trained-dram/b1 | REPORTED | 96 | 52 C | 2.8413 | 2.8419 | 36.838 | 108.134 | 0.38373 | 1.12640 | 29.5966 | 38.62 | 51.0 / 52.83 / 52.0 |
| 10 | random-dram/b1 | REPORTED | 96 | 52 C | 2.8412 | 2.8417 | 38.253 | 109.658 | 0.39847 | 1.14227 | 29.5955 | 39.22 | 51.0 / 52.91 / 52.0 |
| 11 | random-dram/b2 | REPORTED | 96 | 52 C | 2.8412 | 2.8418 | 40.537 | 111.373 | 0.42226 | 1.16014 | 29.5963 | 39.11 | 52.0 / 53.08 / 52.0 |
| 12 | trained-dram/b2 | REPORTED | 96 | 52 C | 2.8413 | 2.8418 | 38.836 | 109.814 | 0.40454 | 1.14390 | 29.5969 | 38.69 | 52.0 / 53.17 / 52.0 |

**Means a pass, per configuration** (desk arithmetic of the bursts above; issued multiply-adds an image 11,153,408 from the host's own
record, real 11,056,640 = 784 x 1,792 + 3 x 1,792 x 1,792 + 1,792 x 10; the scorer's own per-pass, per-image and per-multiply-add numbers
follow after the data commit):

| configuration | bursts | hart0 cycles a pass | kernel s a pass | J over idle a pass (sd) | J at rest a pass (sd) | uJ an image, over idle / at rest | pJ an issued multiply-add, over idle / at rest | pJ a real multiply-add, over idle / at rest |
|---|---|---|---|---|---|---|---|---|
| trained-scp (scored) | 4 | 17,666,191 | 0.029444 | 0.39524 (0.01217) | 1.12130 (0.00583) | 6.587 / 18.688 | 0.5906 / 1.6756 | 0.5958 / 1.6902 |
| random-scp (scored) | 4 | 17,664,346 | 0.029441 | 0.39818 (0.00517) | 1.12863 (0.00767) | 6.636 / 18.810 | 0.5950 / 1.6865 | 0.6002 / 1.7013 |
| trained-dram (REPORTED) | 2 | 17,758,058 | 0.029597 | 0.39414 (0.01472) | 1.13515 (0.01237) | 6.569 / 18.919 | 0.5890 / 1.6963 | 0.5941 / 1.7111 |
| random-dram (REPORTED) | 2 | 17,757,519 | 0.029596 | 0.41036 (0.01682) | 1.15121 (0.01263) | 6.839 / 19.187 | 0.6132 / 1.7203 | 0.6186 / 1.7353 |

The scp launch issued 2.273e13 multiply-adds a kernel second (about 37.0 a minion-cycle over 1,024 minions at 600 MHz; desk arithmetic).
The rails a pass (the reducer's ramp-baseline upper bounds, trained-scp means): minion 0.168 J, SRAM 0.190 J, NoC 0.012 J, unmetered
0.025 J.

## The meter's absolute scale (stated before the data, E202.md 11)

**Every number here is against the card's own meter, whose absolute scale is one fixed gain for every board, never set beside an outside
meter** (E184's arm S, the test of the meter itself, is pending). The joules over idle and with the card at rest carry that gain; a later
calibration would move every one by the same factor.

## Registered against happened

| registered (E202.md, plan-e202.json, KIT.md) | happened |
|---|---|
| aifoundry3 card 0 at 600 MHz as found, nothing set; the start config TDP 0 W / 65 C / 600 MHz (KIT.md 4) | `session/config-start.json` and `config-end.json`: TDP 0 W, 65 C, 600 MHz, 523 mV; step 7's read the same at 12:24:24; 5,012 of 5,012 samples at 600 MHz; nothing set |
| after E201 and the 40-minute rest; step 7 after the rest (E202.md 3, 10) | E201 did not run (paused by the owner's words of Mon 16 Nov 2026: departure 5); the box's last session of ours before E202 was E197's sitting 1, session end 06:10:45 PST; step 7's "rest: 373 minutes ..." and step 9's "rest: 374 minutes ..." (40 required) |
| the window from G = the booking: last start G + 1:30, last end G + 3:30 (E202.md 10) | G 12:21:01 PST; last start 13:52, last end 15:52; the session 12:24:48-12:33:10, inside it |
| the smoke's five processes and its gate on core_status (E202.md 7.2, 8.2) | all five core PASS and status PASS; logits PASS on the four debug arms; "smoke gate passed: T-scp and Z-scp read core PASS: the scp pair is scored" (12:26:52); UA = 1 (unsigned activations, a first use on silicon) passed every check |
| the R rule per arm, R 96 unless the 6 s ceiling binds (E202.md 8.3) | R 96 on every arm (the smokes' predicted R = 96 launch 2.911-2.919 s, under the 6 s ceiling); the host's timeout cap took no smaller R |
| K = 4 each, T Z Z T T Z Z T; the dram pair K = 2 REPORTED when scp is scored (E202.md 8.4-8.5) | queue.json: trained-scp b1, random-scp b1, b2, trained-scp b2, b3, random-scp b3, b4, trained-scp b4 (scored); then trained-dram b1, random-dram b1, b2, trained-dram b2 (REPORTED); 12 of 12 good |
| each burst: the die gate (60 C, 10 minutes), 8 s at rest, one host process under timeout 10, 10 s at rest (E202.md 8.4) | die at the starts 49-51 C (scored) and 52 C (dram); gate waits 0.0 s everywhere; **the eight scored bursts started below the forecast band's 52 C** (49-51 C), labelled "T0 below the forecast band" by the runner: E202.md 8: below 52 C does not block (scored given its own T0, labelled so) |
| the stops: 65 W, 70 C, the clock, a line older than 1 s; K1 (KIT.md 4) | none fired (queue.json stop null; no sample off the clock; no burst set aside); the stop-path test passed at the start (board, die, clock and stale each tripped in 0.1-0.2 s and refused a start) |
| one sampler, `ettelem sample --every-ms 100` through E128's guard; no statistics reset | "sampler started (attempt 1, ..., every 100 ms)" (`ettelem_guard.sh sample --seconds 3300 --every-ms 100`); dmcmd_audit_v2 GO at step 2 and on the box at step 6 ("22 send site(s), 0 disallowed"); no reset |
| the cap: no burst after 33 card-minutes from the first card command, the session ended by 35 | the last burst started at 12:30:49 (6.0 card-minutes); the close at 8.37 |
| two idle anchors of 2 minutes (E202.md 8.1, 8.6) | anchor 1 12:24:49-12:26:49 and anchor 2 12:31:10-12:33:10, each whole (120 s, nothing running but the sampler) |
| the post waived; the package counter not read (E202.md 10) | the owner's words of Sun 15 Nov 2026 10:22:36 PST; not read |
| the program built on the box, read by its `.text` and its host's behaviour; MNIST fetched there by sha256 (KIT.md 1) | step 6, 12:22:25-12:23:18: E202-BUILT rc=0; the kernel's `.text` `ace7bcb0...` at its pin (the ELF `0f74ff0d...`, equal to E202.md's aifoundry3 build, reported); the four MNIST files fetched from the program's mirrors and checked by sha256; 18 of 18 files at their pins; HOST-BEHAVIOUR OK 20 of 20; the box's harness 33 files, the preflight GO, the common self-check PASS; the dry pass "E202-DRY rc=0 bursts=4" (12:24:26-12:24:40) |

## Device commands sent

READs only: the session's opening and closing `ettelem config` and the one `ettelem sample --every-ms 100`, all through E128's guard
(dmcmd_audit_v2 GO, every send site a READ: KIT.md section 5), and k6's step 7 config read through the same guard; the mnistmlp host opened
the ops node only (`createPcieDeviceLayer(true, false)`; the runtime's creation aborts the submission queues of the card it enumerates, as
every lab host's does: harmless on a card held alone, et-who empty and card 0's lock held); `et-who` sends no device command. No set, no
reset, no statistics reset, no firmware write, no PMIC write.

## Files

| path | what |
|---|---|
| `smoke/<arm>/` | each smoke process: `host-raw.json` (the host's own --out file), `labels.bin` (the kernel's label lines, 64 B each), `smoke.json` (the runner's record and the R rule's inputs), `stdout.txt`, `host.err` |
| `bursts/<config>/b<k>/` | each burst (E202.md 7.1): `host-raw.json` (the host's own --out file), `host.json` (the adapter's), `burst.json` (the runner's marks: config, k, order index, R, set aside), `run.json`, `telemetry.jsonl.gz` (the session's samples over the burst), `stdout.txt`, `host.err`, `energy.json` and `energy.txt` (the reducer's output and its printed lines) |
| `session/` | `session.log`, `config-start.json`, `config-end.json`, `stop-path.json`, `etwho-before.txt`, `queue.json`, `telemetry.jsonl.gz` (the whole session), `runner.out`, `runner.rc`, `MANIFEST.sha256` (the box's), `sampler.err` |
| `session-facts-e202.json` | the collector's summary of the session's own files (measured) |
| `SHA256SUMS` | every file above but this README |

## Labels

Measured: the session's records. Registered: E202.md and its files. Desk check of code: the kit's tests. Desk arithmetic: the means, the
per-image and per-multiply-add figures and the card-minute sums above. Nothing here is blind to the forecasts' authors' earlier card results
(E202.md's label), and the scorer's words are the frozen scorer's, after the data commit.

For the reader of the scores (verify-e202's note 12): E202-S1T's 10% (registered) weighs the card at rest, about 60% of J with the card
at rest at the forecast point, so a miss in J over idle moves S1T by about 0.4 of its size (E202.md 7.4's self-test B: J over idle 25%
high gives S1T e -0.087); S1 is the joules-over-idle test.

SPDX-License-Identifier: Apache-2.0
