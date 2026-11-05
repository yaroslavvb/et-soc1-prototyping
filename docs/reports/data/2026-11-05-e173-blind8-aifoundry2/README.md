# E173: blind pool 8 under aifoundry2's own governor - M10 carried by rule E reads the 21 pinned bursts' board to 1.09 W rms (mean −0.04 W), so A2-Bp FAILS on its 1.0 W rms line and A2-R2 FAILS through Bp; W2 and H1 PASS, F2 FAILS on the governor's mid-burst dips, and M1 (M10 against M9's part) is not resolved

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6, "a power model across kinds"**, with items 8 and 9 (heat) through the burst's die rise. It answers the Q142(r)/(p)/(d) critic's
`next` rank 2 for aifoundry2 and the readiness critic's (critic-q142v2rh) day-1 plan, "E173 on aifoundry2".*

*Thu 5 Nov 2026 (week 45), the pool-8 card day, aifoundry2 card 0 under its own governor (65 W / 65 C read at the queue's start and end,
nothing set). Registered before any E173 data: [`E173.md`](../../../../tools/claims-v3/e173/E173.md) `c8064454` (03:45:13 PST), the
scorer `99e5777e` (03:54:39), the kit `5a2a9ba0` (04:35:57), dated note 1 `5db9df6b` (05:45:17) with the v2 drivers `34436d68` (05:49:03),
and dated note 2 `c9a3e40a` (08:23:02) before the v3 code `e2b48f5a` (08:27:12) and `6f4b48e4` (08:31:18). Pool 8 and both models'
predictions were frozen in `4576fb90` (02:30:56), after the pool's design `153b720f` and the predictor's registration `3e97f583`. The
owner's go for the day's card time, all four cards, came at about 11:15 PST. The day's one `#community-lab` post (message 1567984130841641044, 11:29:08 PST) named aifoundry2 before the first launch, and its aifoundry2
clause was dropped by a rewrite saved at 12:16:52-12:16:58 PST, after the queue's end. The box's checkout ran at `ea12f108`, which descends from every frozen commit.
Every box step went through the v3 driver, `box/step_e173_v3.sh` (look, tree, dry start, dry wait, launch full, wait, collect), as dated
note 2 registers.*

## The answer

| rule | set | measured (M10 carried, recomputed per tile from the session's own reads) | line | verdict |
|---|---|---|---|---|
| **P8-A2-Bp** | pinned board, 21 tiles | **1.094 W rms, mean −0.035 W** | \|mean\| ≤ 0.5 W AND rms ≤ 1.0 W | **FAIL** (the rms; the mean holds) |
| **P8-A2-R2** | G, Bg and Bp | G and Bg NOT SCORED; Bp FAIL | PASS if all three PASS; FAIL if any FAILs | **FAIL** (through Bp, the registered route on pool 8) |
| P8-A2-F2 | pinned clock, 21 | **7.01 MHz rms, mean −2.66 MHz** | 0.174-4.540 MHz | **FAIL** |
| P8-A2-W2 | pinned board, 21 | 1.094 W rms | 0.528-1.113 W | PASS |
| P8-A2-M1 | board, all 24 | M10 carried 1.036 W against M9's part on M9's D 1.086 W rms: −0.050 W [−0.161, +0.037] | BETTER if the upper end < 0 | NOT RESOLVED |
| P8-A2-H1 | burst die rise, all 24 | **0.522 °C rms, mean −0.329 °C** | 0.491-0.870 °C | PASS |
| P8-A2-G | governed clock, 3 | 3.27 MHz rms, mean +1.90 MHz | rms ≤ 4.0 MHz AND \|mean\| ≤ 2.0 MHz, at least 8 tiles | NOT SCORED (n 3 < 8), as registered |
| P8-A2-Bg | governed board, 3 | mean −0.361 W | \|mean\| ≤ 0.5 W, at least 8 | NOT SCORED (n 3 < 8), as registered |
| P8-A2-F1 | governed clock, 3 | 3.27 MHz rms | the bootstrap line, at least 8 | NOT SCORED (n 3 < 8), as registered |
| P8-A2-W1 | governed board, 3 | 0.463 W rms | the bootstrap line, at least 8 | NOT SCORED (n 3 < 8), as registered |
| P8-HM | heat over minutes | | | NOT SCORED (E173 runs no hold) |
| E173-C | the check of C | **2,836 of 2,836 launches bit-exact** (the smoke's 21 and stoptest-board's 5 beside) | all PASS | PASS |
| E173-R0 | E80's two replicates | fp16 randn 722.83 MHz / 66.44 W (−4.87 MHz, −0.15 W); int8 full 800 MHz / 49.63 W (0, −0.17 W) | within 25 MHz and 3.37 W | PASS |

Source: [`results.json`](results.json) › `score.rules`, `c_check` and `replicate_R0`, printed in [`score.txt`](score.txt), by the
registered scorer [`score_e173.py`](../../../../tools/claims-v3/e173/score_e173.py) on the session's counted runs (165 of 165), behind the
code-path check ([`logs/path-check.txt`](logs/path-check.txt): HARNESS OK 135) and the C-log gate (smoke, stoptest-board and s1 each carry
a C log and a finished check of it).

**Against what was frozen** (E173.md, "What I expect"): E173-C PASS, W2 PASS, M1 NOT RESOLVED, H1 PASS and R0 PASS read as expected; F2 was
"PASS or FAIL" and FAILED; **Bp was expected to PASS** ("so Bp's rms may FAIL") with the registered forecast that both its lines hold in
88.6% of draws (the rms line in 89.3%), and it FAILED on the rms line, so A2-R2 reads FAIL, the registered outcome when Bp fails.

**Why Bp's rms fails while its mean holds.** The pinned board's errors split by kind (`results.json` › `score.reported.by_set` and
`score.reported.tiles`): the eight single-high-bit tiles (class S) read **+0.11 to +1.67 W above M10 carried, +1.06 W on average** (M9's
part: +1.13 W); three tiles whose passes dipped below 800 MHz read **−1.84 to −2.30 W below it** (`fp16.r8_granite_l3_pv_e993b7`,
`int8.l8_flip_d2p2c16_231d`, `int8.u8_ar_k_0a9fe5`, at 784.3, 777.5 and 783.3 MHz against 800 predicted); and the twelve int8 tiles read
0.62 W low on average. The signs cancel in the mean and add in the rms.

**Why F2 fails.** Four scored pinned tiles each ran one or two passes at 750-796 MHz while their other passes ran at 800
(`fp16.r8_granite_l3_pv_e993b7` pass 3 at 752.9 MHz; `int8.l8_flip_d2p2c16_231d` passes 2 and 3 at 779.6 and 752.9;
`int8.u8_ar_k_0a9fe5` pass 2 at 750; `int8.r8_granite_l4_actdown_b076f2` pass 1 at 796; `results.json` › `run_rows`). That is the
governor's mid-burst dip that E165's F2 FAIL showed on six pinned tiles (5.11 MHz rms) and E160's M1 on three bursts. No model of the bits
predicts it: it is a session term of the governor, not of the data. M9's part reads the same 7.01 MHz.

## What this does to predicting power and heat

The term tested is **M10 carried by rule E** (POOL8-REGISTRATION.md § 5): M10's D at 600 MHz, carried to aifoundry2's governed 800 MHz
bursts through M9's aifoundry2 part with the session's own zeros level and each burst's die start, blind, on 24 new kinds the fits never saw.

| | pinned board | pinned clock | governed board | governed clock | die rise |
|---|---|---|---|---|---|
| **before**: the end-to-end held-out references (Q140(l); `../../../../tools/claims-v3/e165/predictions-e165.json` › `reference`) | 0.82 W (42 cells) | 2.33 MHz (42) | 0.78 W (36) | 4.50 MHz (36) | 0.6845 °C (the heat law's 112 residuals) |
| **before**: E165, blind on pool 7, M9's part | 0.99 W | 5.11 MHz | 0.71 W | 3.03 MHz | 0.455 °C |
| **after**: E173, blind on pool 8, **M10 carried** | **1.094 W** (mean −0.035) | **7.01 MHz** (mean −2.66) | 0.46 W (3 tiles, not scored) | 3.27 MHz (3 tiles, not scored) | **0.522 °C** (mean −0.329) |
| beside it: M9's part on M9's D, the same bursts | 1.147 W (mean −0.004) | 7.01 MHz | 0.48 W | 3.84 MHz | 0.529 °C |

(`results.json` › `score.rules` and `score.reported.by_set`.) So, on aifoundry2 under its governor:
- **The board of a new kind at 800 MHz is predicted blind to about 1.1 W rms** with no bias (mean −0.04 W). That is worse than the
  held-out 0.82 W and E165's blind 0.99 W, inside W2's bootstrap line, and outside rank 2's 1.0 W rms line.
- **M10's refit carries in sign, not resolved**: over the 24 tiles M10 carried is 0.05 W rms better than M9's part on M9's D
  ([−0.161, +0.037] W); the clock's paired interval beside it is −0.038 MHz [−0.190, +0.004] (`score.reported.P8-A2-M1_clock_beside`).
  The part's own error (about 1 W) hides the D difference, as registered.
- **Two named error sources**: single high B bits at 800 MHz read about 1.1 W above both models here, as E165's class-S tiles read high on
  pool 7; and the governor's mid-burst dips, a session term.
- **Heat**: the burst heat law (0.1400 °C/W, unchanged) holds blind on a third pool, 0.522 °C rms over 24 kinds, the measured rises
  running 0.33 °C below the law's on average.
- **The governed clock line is still untested as a verdict** (3 governed tiles under the 82 W admission). Reported only, never a verdict
  (`score.reported.GX7_reported`, `GX10_reported`): over the 7 governed tiles that ran, M10 carried reads the clock to **5.62 MHz rms**
  (mean −0.66 MHz; 10 tiles with the three fp16 random anchors: 5.30 MHz), above rank 2's 4.0 MHz line. M9's part reads the 3 scored
  governed tiles at 3.84 MHz.

For the kinds page's item 6 and the Horace Hub's Levels: the governed card's pinned-burst board is now a blind ~1.1 W (pool 8) where it was
a blind ~1.0 W (pool 7), the single-high-bit price at 800 MHz is the largest data term the models miss on this card, and the governor's
dips remain a session term that no bit model predicts.

## What ran

| | |
|---|---|
| look first | 11:36:02 and again 11:39:24 PST, right before the session (`step_e173_v3.sh look`): et-who "No process holds" (holder lines 0), no device process of ours or of another user, 0 logins, the host booted 2026-10-26 15:13:03 PST, before E69's firmware read of 2026-10-27 13:56:26 PDT (BL2 0.22.0 by continuity): FREE |
| the tree | 11:36:10-11:36:15: `git pull --ff-only` fast-forwarded the checkout from `5e1bb309` to `ea12f108`; `5a2a9ba0` an ancestor; `tools/claims-v3` clean; HARNESS OK 135 + 3 binaries; 64 tiles OK; blind8 89 OK; the preflight's `dmcmd_audit` GO (19 send sites, 0 disallowed); 165 BURST runs listed |
| the box's dry pass | 11:36:30-11:39:09, rc 0 (the toy card: the smoke clean, both stop tests exit 4, s1 rc 0, the queue's end) |
| queue | `queue_e173.py --slots ~/claude/work/q142-a2-e173-slot.txt --runs build/e173/runs --cap 42 --protocol tools/claims-v3/e173/protocol.json` (`launch full`), detached, 11:39:25-12:16:17 PST; its slot 11:39:25-12:27:25 |
| smoke | 11:39:25-11:40:17, rc 0: C 21 of 21 records, 3 host records; the DMA rule's δ 2.0 ms, its projected held time 6.604 s under the 7.2 s limit |
| stop-path tests, on live samples | board: `safety:board 32.0 W > 30 W on 3 samples` (rc 4), 64 ms after the third live line over 30 W, the launch ending 295 ms after the trip; die: `safety:die 70 C >= 30 C` (rc 4), 110 ms after the first live line, before any launch |
| the session `s1` | 11:40:24-12:16:17 PST, **all 165 registered bursts** (3 passes of 55, each opening with the zeros anchors), every one complete and counted; it ended `done` (rc 0) |
| card-minutes | **36.9** (smoke 0.9, stop tests 0.1, `s1` 35.9) of the 42 cap; 36.9 minutes of wall time |
| peaks | board 80.68 W (`BURST-20`, `fp16.u8_rowscale_ecc921`, pass 1); the shires' mean 63 °C; the hottest-sensor field 70 °C (its latch, as in E165); 21,347 samples |
| the card at the start and end | `ettelem config`: TDP 65 W, threshold 65 °C, power state 3 (low power), 600 MHz at 519 mV, both times |
| other users | the queue's 685 idle-login reads: 0 other users, 0 blocking, throughout |

The zeros anchors ran all nine bursts at 800 MHz, 33.99 / 33.90 / 35.30 W for fp32 / fp16 / int8, 1.36-1.39 W under the frozen fallback
level (`score.reported.zeros_anchors`); the session's anchor delta is −1.43 / −1.30 / −1.42 W (`score.anchor_delta`). The board's peak
samples ran over M10's frozen 95% upper peak on 4 of the 53 tiles that ran, all single bits, by 1.83-3.59 W (`fp16.b_onebit_b8_pi` 65.99 W,
`fp16.s8_onebit_b7_b945b945` 64.57, `fp32.s8_onebit_b18_be2584eb` 63.70, `fp32.s8_onebit_b19_c11b3dd2` 65.88;
`score.reported.peaks_vs_hi95`; M9's part the same 4), all far under the 82 W admission.

## Registered against what happened

- **The tiles scored are the registered 24** (3 governed, 21 pinned); the 11 tiles left out by name stayed out (in no run). Every scored
  tile has three counted passes. Every rule is scored on the counted runs, as registered.
- **The tree needed no remedy.** The pull fast-forwarded with nothing local in its way, so Wed's D1 remedy (inventory, tar, stash,
  fast-forward) was not used. The collector's re-hash of the box's kit files, tiles and binaries against this tree reads "all as the desk's
  tree and the pins" ([`logs/box-files-check.txt`](logs/box-files-check.txt)).
- **D1, the desk-path gate (Thu 5 Nov 2026, 12:30-12:41 PST, after the scoring, before any commit).** The collection step ended with exit
  16 at 12:30:54. v3.1's desk-path gate found the day's scratch directory, an absolute desk path outside the repo, three times in
  [`logs/cclist.txt`](logs/cclist.txt). These are the C-log list's three REQUIRED lines: `collect_e173_bounded.sh` tees them with the raw
  copy's paths (line 86) and copies `logs/` into the data dir (line 96). The gate's remedy reads "fix the route, remove the outputs, collect
  again". Collecting again through the committed driver would write the same three lines, because the raw copy always lives in the day's
  directory outside the repo. So only that prefix was replaced, by `<RB_OUT>` (the runbook's own display form), in that one file:
  - sha256 `48807990…` as collected, `5273aabd…` after; nothing else in it changed;
  - the as-collected copy is kept outside the repo;
  - the step's two gates were then re-run through the runbook's own functions (`rb_common_v3.sh`). The C-log gate read v3's list (3
    required, equal to v2's and v1's), with 3 of 3 checks finished and all PASS. The desk-path gate read 425 files, 0 hits: CLEAN;
  - no scored file, rule, number or check changed. E174's collector (`collect_e174.sh` lines 34 and 38) has the same route.
- **`ccheck-s1.json` is committed gzipped only**, as E165's was: `ccheck-s1.json.gz` (gzip -n). Its gunzip is the bytes whose sha256
  `results.json` › `ccheck_files` records (`5440f57d…`).
- **The F2 FAIL and the Bp FAIL are as measured.** No tile or pass is set aside.
- **Nothing else departs.** The stops, the order, the slot, the cap, the check of C and the scorer are the registered ones.

## The stops, and their test on live samples

The registered stops: one die reading at or above 76 °C, or the board above 85 W on three live samples in a row (exit 4). Beside them, the
run-time admission at 82 W (`e105`: every tile's frozen estimate at most 82 W, the highest admitted 81.88 W) and E159's 82 W lock. Both stops
were tested on live samples by the queue before the session (above), and both fired as registered. Nothing came near a stop in the
session: the highest board sample was 80.68 W and the shires' mean 63 °C.

## Device commands sent

Exactly the registered set ([`E173.md` § Device commands sent](../../../../tools/claims-v3/e173/E173.md#device-commands-sent); the tree
step's preflight on the box read `dmcmd_audit: GO (19 send site(s), 0 disallowed)`): `ettelem sample`'s and `ettelem config`'s reads (the
PMIC voltage reads among them, the owner's allowed read-only reads), `ettelem sptrace`'s trace copy, and the residency read that this
build refuses before opening the device. No statistics reset (no `--reset-ms`), no firmware-revisions query, no governor, TDP, threshold
or clock set. The look-first reads, the tree's fast-forward and the box's dry pass (the toy card) sent nothing to the card.

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`score.txt`](score.txt) | the registered score (`score_e173.py`) |
| `ccheck-smoke.json`, `ccheck-stoptest-board.json`, `ccheck-s1.json.gz` | the check of C per listed session (`s1`'s gzipped only, as above) |
| `aifoundry2/` | the queue's records: `queue.jsonl`, `status.json`, `admission.json`, `idle_logins.jsonl` (counts only), the snapshots, configs and sensor reads, the smoke, the two stop tests and `s1` (runs, launches and the C log gzipped, the sampler lines in `tel/` gzipped, `sp/` traces) |
| `logs/` | `queue.out`, the slot file, the box's file hashes and their check, the code-path check, the login scrub's count (0 marks), the C-log list (D1) |

SPDX-License-Identifier: Apache-2.0
