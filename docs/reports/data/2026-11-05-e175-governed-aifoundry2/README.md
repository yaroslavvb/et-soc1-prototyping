# E175: aifoundry2's governed line - M10 carried reads 16 new governed kinds' clock to 4.49 MHz rms (mean +0.12 MHz), so E175-A2-G FAILS its 4.0 MHz rms line while matching the held-out 4.50 MHz (F1 PASS); the governed board's level holds (Bg PASS); the pinned board reads 0.53 W high, so Bp FAILS on its mean and A2-R2 FAILS through G and Bp; F2, W1, W2, H1, C and R0 PASS, and M1 reads WORSE, which dated note A2 reads as a group's board level, not evidence on D

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6, "a power model across kinds"**, with items 8 and 9 (heat) through the burst's die rise. It answers the earlier critics' rank
"aifoundry2's governed line" (the pool-8 card day's critic, `next` rank 1; the Q142(h2)/(a2)/(r3) critic's `next` rank 7: "Pool 8 gives the
governed clock line no blind test (3 governed tiles)"), as [`E175.md`](../../../../tools/claims-v3/e175/E175.md) registers.*

*Thu 5 Nov 2026 (week 45), the evening card round (Q143(c)), aifoundry2 card 0 under its own governor (65 W / 65 C read at the queue's start
and end, nothing set). Registered before any E175 data: [`E175.md`](../../../../tools/claims-v3/e175/E175.md) `c50ff493` (12:16:51 PST),
dated note A1 `0e56a875` (12:54:59), the tiles, their selection and their frozen predictions `b3f5e83c` (13:04:23), the kit and scorer
`16b3d6e3` (13:11:41), dated note A2 with its M1 reader `73125272` (14:57:16); the collection's D1 rule, the q142kg runbook's
[dated note 3](../../../../tools/claims-v3/q142kg-runbook/README.md.dated-note-3.md), `d85d1e0f` (14:41:14). The stream's seed follows from lab
commit `4576fb90` (02:30:56, pool 8's predictions frozen). The owner's go for the day's card time came at about 11:15 PST ("feel free to use
all 4 cards for experiments"), covering each registered experiment once it is kitted and passed by a readiness critic; the readiness critic
(15:34-15:56 PST) read E175 READY and set this round's window: no session starts after 18:30 PST and every run ends by 20:30 PST
(`s02_window_q142kg.sh 2026-11-05 18:30 20:30`, 16:27:04). The day's one `#community-lab` post (message 1567984130841641044) named aifoundry2
from 16:31:09 PST ("using aifoundry2 for 1.5 h, until ~18:00 PST"), read back unchanged at 16:42:33-44 before the launch, and dropped that clause
at 17:26:27 PST, after the queue's end. The box's checkout ran at `04159d14`, which descends from every registered commit. Every box step went
through the v3 driver, `box/step_e175_v3.sh` (look, tree, dry start, dry wait, launch full, wait, collect).*

## The answer

| rule | set | measured (M10 carried, recomputed per tile from the session's own reads) | line | verdict |
|---|---|---|---|---|
| **E175-A2-G** | governed clock, 16 tiles | **4.492 MHz rms, mean +0.121 MHz** | rms ≤ 4.0 MHz AND \|mean\| ≤ 2.0 MHz | **FAIL** (the rms; the mean holds) |
| **E175-A2-Bg** | governed board, 16 | mean −0.346 W (rms 0.675 W) | \|mean\| ≤ 0.5 W | PASS |
| **E175-A2-Bp** | pinned board, 8 | **mean +0.532 W**, rms 0.668 W | \|mean\| ≤ 0.5 W AND rms ≤ 1.0 W | **FAIL** (the mean: measured above predicted; the rms holds) |
| **E175-A2-R2** | G, Bg and Bp | G FAIL, Bg PASS, Bp FAIL | PASS if all three PASS; FAIL if any FAILs | **FAIL** (through G and Bp) |
| E175-A2-F1 | governed clock, 16 | 4.492 MHz rms | 2.675-6.148 MHz | PASS |
| E175-A2-W1 | governed board, 16 | 0.675 W rms | 0.461-1.093 W | PASS |
| E175-A2-F2 | pinned clock, 8 | 1.239 MHz rms (mean +0.651 MHz) | 0.000-5.288 MHz | PASS |
| E175-A2-W2 | pinned board, 8 | 0.668 W rms | 0.370-1.287 W | PASS |
| E175-A2-M1 | board, all 24 | M10 carried 0.6725 W against M9's part on M9's D 0.6549 W rms: **+0.0177 W [+0.0003, +0.0405]** | BETTER if the upper end < 0, WORSE if the lower end > 0 | **WORSE**, read by dated note A2 as a group's board level, not evidence on D (below) |
| E175-A2-H1 | burst die rise, all 24 | **0.582 °C rms, mean +0.528 °C** | 0.493-0.869 °C | PASS |
| E175-C | the check of C | **2,125 of 2,125 launches bit-exact** (the smoke's 21 and stoptest-board's 5 beside, all PASS) | all PASS | PASS |
| E175-R0 | E80's two replicates | fp16 randn 725.62 MHz / 66.98 W (−2.08 MHz, +0.40 W); int8 full 800 MHz / 50.63 W (0, +0.83 W) | within 25 MHz and 3.37 W | PASS |
| E175-GS (reported) | governed clock error on the predicted clock, 16 | slope +0.040 MHz per MHz, 2.5-97.5% [−0.060, +0.150] over 725.6-791.4 MHz | never a verdict | resolved neither way |

Source: [`results.json`](results.json) › `score.rules`, `score.reported`, `c_check` and `replicate_R0`, printed in [`score.txt`](score.txt), by the
registered scorer [`score_e175.py`](../../../../tools/claims-v3/e175/score_e175.py) on the session's counted runs (126 of 126 complete and
counted), behind the code-path check ([`logs/path-check.txt`](logs/path-check.txt): HARNESS OK 103) and the C-log gate (smoke, stoptest-board and
s1 each carry a C log and a finished check of it, by v3's list). The lines are read at the scored n, which equals the planned n for every rule
(16 governed, 8 pinned, 24 in all). M9's part beside, the same bursts (`score.reported.M9_on_every_rule`): G FAIL 4.749 MHz (mean +0.844), Bg
PASS −0.356 W, **Bp PASS +0.458 W** (rms 0.604), F1 PASS, W1 PASS, F2 PASS 1.248 MHz, W2 PASS 0.604 W, R2 FAIL through G.

**Against what was frozen** (E175.md, "What I expect"): E175-C PASS, Bg PASS, F1 PASS, W1 PASS, F2 PASS, W2 PASS, H1 PASS, R0 PASS and GS
"resolved neither way" read as expected. **G was expected to PASS and FAILED; Bp was expected to PASS and FAILED; R2 was "PASS or FAIL on Bg"
and FAILED, on G and Bp, with Bg passing; M1 was expected NOT RESOLVED and read WORSE.** The registered power said so much was possible: G
passes in 31.5% of draws if M10 carried errs as Q140(l)'s held-out cells (4.50 MHz) and in 91.0% at E165's blind errors (3.03 MHz), and the
session's 4.49 MHz is the held-out figure; Bp passes in 74.7% and 50.2% at those two truths, and 57.1% with a 0.5 W board level; R2 in 23.1%
and 31.9%.

**Why G fails while its mean holds** (`results.json` › `score.reported.tiles` and `run_rows`). The error is tile-to-tile, not a level and not a
gain: the mean is +0.12 MHz and GS reads no slope. By stratum (`score.reported.by_set`): S1 (predicted below 745 MHz) 6.47 MHz rms (mean −4.20),
S2 (745-762) 5.66 (+3.54), S3 (762-779) 2.54 (+1.59), S4 (779-795, near the cap) 0.60 (−0.45). Four tiles miss by more than 4 MHz:
`fp32.e5c10_ar_i_t10_adc630` −12.27 MHz, `fp16.e5c24_grid_t1_cdcbf7` +9.79, `fp16.e5c03_ar_k_t4_5b8e8e` +5.36 and `fp32.e5c09_uniform_t6_dad136`
−4.08. *Post hoc, this lane's reading, never a verdict:* without `fp32.e5c10` the other 15 read 3.39 MHz rms, and one of that tile's four passes
dipped (pass 3: 708 MHz at 62.81 W, against 730.0-734.0 MHz at 66.30-67.47 W in passes 1, 2 and 4), the governor's mid-burst dip that E165 and
E173 named a session term no model of the bits predicts; `fp16.e5c24` reads high in every pass (755.8-766.7 MHz against 752.19 predicted), a
miss of the data term on that kind. M9's part reads the governed clock at 4.75 MHz, mean +0.84 MHz.

**Why Bp fails while its rms holds.** The eight pinned tiles' board reads above M10 carried on six of them, by +0.33 to +1.18 W, and within
0.05 W on the other two (`fp32.e5c50_ar_k_t22_16d78b` −0.046, `fp32.e5c65_sparse_t5_254f07` −0.048): a level of about half a watt (*post hoc:*
+0.44 W without the largest, `fp32.e5c14_ar_k_t22_a444f5` +1.18 W), 0.032 W over Bp's 0.5 W line. M9's part on M9's D predicts those boards
0.07 W higher on average and reads +0.458 W, inside the line. The pinned rms, 0.67 W, is below E165's and E173's blind figures (0.99 and 1.09 W)
and the held-out 0.82 W (below).

**E175-A2-M1, read by [dated note A2](../../../../tools/claims-v3/e175/E175.md.dated-note-A2.md)** ([`m1-reading.txt`](m1-reading.txt),
[`m1-reading.json`](m1-reading.json), by `m1_reading_e175.py`, exit 0: the verdict and the clock beside re-derived from the scorer's own tiles,
equal). The verdict is WORSE, as registered. Beside it: Bg's mean −0.346 W and Bp's +0.532 W, so the session's board lies below both models'
predictions on the governed tiles and above both on the pinned ones (M9's part's means −0.356 and +0.458 W); delta = M9's part − M10 carried
averages +0.0317 W (governed +0.0104, pinned +0.0744; the pinned tiles carry 78% of Σ delta); ā_δ +0.418 W against θ 0.0485 W, and the identity
holds (mean(a²) − mean(b²) = 2 · mean(delta) · (ā_δ − θ) = +0.02345). E175-A2-M1c (each group's level removed) reads NOT RESOLVED
[−0.0088, +0.0154]. By A2-3 (5), a resolved M1 with the board on different sides of the predictions in the two groups is evidence on D only
when M1c resolves the same way; it does not, so **this WORSE is the pinned group's board level, not evidence on D**, and the registration's
sentence for WORSE is not written. The clock beside it reads NOT RESOLVED [−0.539, +0.098] (centred: BETTER [−0.248, −0.048]), reported.

## What this does to predicting power and heat

The term tested is **M10 carried by rule E** (POOL8-REGISTRATION.md § 5): M10's D at 600 MHz, carried to aifoundry2's governed bursts through
M9's aifoundry2 part with the session's own zeros level and each burst's die start, blind, on 24 new kinds drawn by a committed rule from a seed
nobody chose, 16 of them predicted to run governed at 727.9-793.8 MHz. Before E175 the governed clock line had no blind score on M10 carried
(pool 8 left it NOT SCORED with 3 governed tiles).

| | governed clock | governed board | pinned board | pinned clock | die rise |
|---|---|---|---|---|---|
| **before**: the end-to-end held-out references (Q140(l); `../../../../tools/claims-v3/e165/predictions-e165.json` › `reference`) | 4.50 MHz (36 cells) | 0.78 W (36) | 0.82 W (42) | 2.33 MHz (42) | 0.6845 °C (the heat law's 112 residuals) |
| **before**: E165, blind on pool 7, M9's part | 3.03 MHz (12 tiles) | 0.71 W | 0.99 W | 5.11 MHz | 0.455 °C |
| **before**: E173, blind on pool 8, M10 carried | 3.27 MHz (3 tiles, not scored) | 0.46 W (3, not scored) | 1.094 W (21) | 7.01 MHz (21) | 0.522 °C (24) |
| **after**: E175, blind, **M10 carried** | **4.49 MHz** (16; mean +0.12) | **0.675 W** (mean −0.35) | **0.668 W** (8; mean +0.53) | **1.24 MHz** (mean +0.65) | **0.582 °C** (24; mean +0.53) |
| beside it: M9's part on M9's D, the same bursts | 4.75 MHz (mean +0.84) | 0.679 W (mean −0.36) | 0.604 W (mean +0.46) | 1.25 MHz | 0.578 °C |

(`results.json` › `score.rules` and `score.reported.by_set`; the earlier rows from E173's data README and E175.md.) So, on aifoundry2 under its
governor:
- **The governed clock of a new kind is now predicted blind to about 4.5 MHz rms with no bias**, the same as the held-out end-to-end figure
  (4.50 MHz) and above rank 2's 4.0 MHz line, which is stricter than held out. The miss is tile-to-tile: no slope on the predicted clock (GS),
  no level (mean +0.12 MHz); near the cap (S4) the clock is predicted to 0.6 MHz, lower down to 5-6 MHz. M10 carried reads the clock a little
  closer than M9's part (4.49 against 4.75 MHz rms), not resolved (the clock beside M1: NOT RESOLVED).
- **The governed board's level holds on new kinds** (Bg PASS, mean −0.35 W, rms 0.68 W, inside the held-out 0.78 W): the governor's plateau is
  predicted, so on governed bursts D enters through the clock, as E175.md says.
- **The pinned board at 800 MHz is predicted with less spread than on pools 7 and 8 (0.67 W rms) but with a level of +0.53 W** on these
  truncated kinds, just outside Bp's 0.5 W line; M9's part's higher D sits nearer (+0.46 W). E173's pinned board on pool 8 read the opposite
  way (mean −0.04 W, rms 1.09 W, its single-high-bit and dipped tiles cancelling in the mean).
- **M10 against M9's part on the board stays untested on D**: M1's WORSE is the pinned group's board level (A2-3), as A2-2 forecast that E175
  cannot test M10's D against M9's at this design.
- **Heat**: the burst heat law (0.1400 °C/W, unchanged) holds blind on a fourth pool, 0.58 °C rms over 24 kinds, inside its held-out
  0.6845 °C, with the measured rises running 0.53 °C above the law on average (E173's ran 0.33 °C below).
- **The governor's dips** recur as a session term on the governed tiles too (one pass of `fp32.e5c10` above, post hoc); the pinned clock read
  1.24 MHz rms (E173: 7.01 MHz, all of it from dips), six of the eight pinned tiles holding 800 MHz on every counted pass.

For the kinds page's item 6 and the Horace Hub's Levels: aifoundry2's governed clock line has its first blind score on M10 carried, 4.5 MHz
rms on 16 new kinds (rank 2's 4.0 MHz not met; the held-out 4.5 MHz met), the governed board's level and the burst heat law hold blind, and the
pinned board's spread is below pool 7's and pool 8's while its level is half a watt high; rank 2's three lines (A2-R2) have still not read PASS
on blind kinds.

## What ran

| | |
|---|---|
| look first | 16:38:54 and again 16:42:53 PST, right before the session (`step_e175_v3.sh look`): et-who "No process holds" (holder lines 0), no device process of ours or of another user, 0 logins, the host booted 2026-10-26 15:13:03 PST, before E69's firmware read of 2026-10-27 13:56:26 PDT (BL2 0.22.0 by continuity): FREE |
| the tree | 16:39:00-16:39:06: `git pull --ff-only` fast-forwarded the checkout from `ea12f108` to `04159d14`; `c50ff493` an ancestor; `tools/claims-v3` clean; HARNESS OK 103 + 3 binaries; 27 tiles OK; the pool's SHA256SUMS 28 OK; the preflight's `dmcmd_audit` GO (19 send sites, 0 disallowed); 145 BURST runs listed |
| the box's dry pass | 16:39:23-16:42:03, rc 0 (the toy card: the smoke clean, both stop tests exit 4, s1 rc 0, the queue's end) |
| queue | `queue_e175.py --slots ~/claude/work/q143-a2-e175-slot.txt --runs build/e175/runs --cap 42 --protocol tools/claims-v3/e175/protocol.json` (`launch full`), detached, 16:42:59-17:25:45 PST; its slot 16:42:59-17:30:59; E173's queue had ended 16,002 s before (the launch gate's 600 s met) |
| smoke | 16:42:59-16:43:52, rc 0: C 21 of 21 records, 3 host records; the DMA rule's δ 2.0 ms, its projected held time 6.604 s under the 7.2 s limit |
| stop-path tests, on live samples | board: `safety:board 33.1 W > 30 W on 3 samples` (rc 4), 65 ms after the third live line over 30 W; die: `safety:die 70 C >= 30 C` (rc 4), 61 ms after the first live line, before any launch |
| the session `s1` | 16:43:58-17:25:45 PST, rc 0, ended `done:cap_cuts_tail`: **126 of the 145 registered bursts** (passes 1-4 whole, the first 10 of pass 5), every one complete and counted |
| card-minutes | **42.8** (smoke 0.9, stop tests 0.1, `s1` 41.8 of its 42 cap); 42.8 minutes of wall time |
| peaks | board 81.05 W (`BURST-54`, E80's `k-fp16-randn`); the shires' mean 63 °C; the hottest-sensor field 70 °C (its latch, as in E165 and E173); 24,922 samples |
| the card at the start and end | `ettelem config`: TDP 65 W, threshold 65 °C, power state 3 (low power), 600 MHz at 519 mV, both times |
| other users | the queue's 587 idle-login reads: 0 other users, 0 blocking, throughout |
| the release | the day's post dropped aifoundry2's clause at 17:26:27 PST (dry 17:26:18, saved 17:26:21-27, under the post's lock), read back from the edit box at once and from a fresh plan at 17:28:02-09 |
| collect, at the desk | 17:26:40-17:38:35 PST at nice 10 (the check of C with 2 workers): the box's file hashes "all as the desk's tree and the pins", the check of C on the three listed sessions, the C-log list, E111's login scrub (0 marks), the registered scorer; then D1 (below) |

The zeros anchors ran at 800 MHz for fp32 and fp16 (34.91 and 34.86 W) and at 791.42 MHz for int8 (35.68 W), 0.43-0.98 W under the frozen
fallback level (`score.reported.zeros_anchors`); the session's anchor delta is −1.45 / −1.42 / −1.42 W (`score.anchor_delta`). No tile's board
peak exceeded either model's frozen 95% upper peak (0 of 27 for M10 and for M9; `score.reported.peaks_vs_hi95`), and every peak was under the
82 W admission.

## Registered against what happened

- **The tiles scored are the registered 24** (16 governed, 8 pinned); every one has at least four counted passes, and every rule is scored on
  the counted runs, at its planned n.
- **The cap cut pass 5's tail, as registered.** `s1` ran 126 of the 145 bursts: passes 1-4 whole (29 each) and the first 10 of pass 5.
  `run_e119.py` did not start `BURST-126` at 2,506.9 s because its planned time no longer fit the 42-minute cap (`aifoundry2/s1/run.log`,
  "the cap cuts the tail here"), and the session ended `done:cap_cuts_tail`, rc 0. E175.md registers exactly this ("it cuts pass 5's tail if the
  die gates run long"), and the readiness critic named it as a risk. The die gates did run long: the wait for a die reading at or below 55 °C
  before each burst came to 1,010 s in all (median 9.6 s, at most 14.2 s, always reached), so the bursts came every 20.0 s on average against
  E165's measured 13.5 s (pinned) and 16.2 s (governed), from which the 38-minute estimate was made.
- **The tree needed no remedy.** The pull fast-forwarded with nothing local in its way, so E165's D1 tree remedy was not used. The collector's
  re-hash of the box's kit files, tiles and binaries against this tree reads "all as the desk's tree and the pins"
  ([`logs/box-files-check.txt`](logs/box-files-check.txt)).
- **D1, the desk-path gate, by the registered rule (Thu 5 Nov 2026, 17:38:35-17:38:48 PST, after the scoring, before any commit): a departure
  of the collection route under the q142kg runbook's [dated note 3](../../../../tools/claims-v3/q142kg-runbook/README.md.dated-note-3.md)
  (`d85d1e0f`, committed before any E175 data).** The collect step ended with exit 16 at 17:38:35. v3.1's desk-path gate found the round's
  scratch directory, an absolute desk path outside the repo, three times in [`logs/cclist.txt`](logs/cclist.txt) (4 HIT lines), and nowhere
  else: the C-log list's three REQUIRED lines, which `collect_e175_bounded.sh` tees with the raw copy's paths (line 86) and copies into the data
  dir (line 96), as note 3 foresaw. At 17:38:46-48 the rule ran, `bash tools/claims-v3/q142kg-runbook/d1mask_q142kg.sh E175
  docs/reports/data/2026-11-05-e175-governed-aifoundry2 aifoundry2`, with the collect step's own `RB_OUT` and `RB_LOCK`, and exited 0:
  - its `--since` is the collect step's probe line, 17:26:41 PST (1793928401); every hit lay inside the rule;
  - the three occurrences were replaced by `<RB_OUT>` (the runbook's display form) in `logs/cclist.txt` only: **sha256 `6e21b0ebedee1adab2cb52946060a2219ded931ef8f899883ddae7e5809a0012` as collected, `6d45619ee2a6238117a71d26c1f8ee5648365c2b6480045b523d903d367b77f7` after**; the bytes as collected are kept outside the repo;
  - of the data dir's 347 files only `logs/cclist.txt` changed (its manifests before and after);
  - the step's two gates then re-ran through the runbook's own functions: the C-log gate read v3's list (3 required, equal to v2's and v1's),
    with 3 of 3 checks finished and all PASS; the desk-path gate read 347 files, 0 hits: CLEAN;
  - no scored file, rule, number or check changed.
- **`ccheck-s1.json` is committed gzipped only**, as E165's and E173's were: `ccheck-s1.json.gz` (gzip -n). Before the plain copy was left
  out (about 17:41 PST), its gunzip was checked equal to it and to the sha256 `results.json` › `ccheck_files` records (`a62e2a023a92d9a4…`).
- **E175-A2-M1 is stated as dated note A2 registers** (A2-3, committed before the session): the verdict as registered, and the reading beside
  it, by A2-4's desk step after the collector (exit 0).
- **The G and Bp FAILs are as measured.** No tile or pass is set aside.
- **Nothing else departs.** The stops, the order, the slot, the cap, the check of C and the scorer are the registered ones.

## The stops, and their test on live samples

The registered stops: one die reading at or above 76 °C, or the board above 85 W on three live samples in a row (exit 4). Beside them, the
run-time admission at 82 W (every tile's frozen estimate at most 82 W, the highest 81.53 W) and E159's 82 W lock. Both stops were tested on
live samples by the queue before the session (above), and both fired as registered. Nothing came near a stop in the session: the highest board
sample was 81.05 W, under the 82 W lock, which therefore never engaged, and the shires' mean reached 63 °C.

## Device commands sent

Exactly the registered set ([`E175.md` § Device commands sent](../../../../tools/claims-v3/e175/E175.md#device-commands-sent), E173's
table with E175's names; the tree step's preflight on the box read `dmcmd_audit: GO (19 send site(s), 0 disallowed)`): `ettelem sample`'s and
`ettelem config`'s reads (the PMIC voltage reads among them, the owner's allowed read-only reads), `ettelem sptrace`'s trace copy, and the
residency read that this build refuses before opening the device. No statistics reset (no `--reset-ms`), no firmware-revisions query, no
governor, TDP, threshold or clock set, no power cycle. The look-first reads, the tree's fast-forward and the box's dry pass (the toy card) sent
nothing to the card.

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`score.txt`](score.txt) | the registered score (`score_e175.py`, E173's `p8gov.py` imported unchanged) |
| [`m1-reading.json`](m1-reading.json), [`m1-reading.txt`](m1-reading.txt) | dated note A2-4's reading of E175-A2-M1 (`m1_reading_e175.py`): the registered verdict re-derived and equal, M1c, the groups' means, ā_δ and θ |
| `ccheck-smoke.json`, `ccheck-stoptest-board.json`, `ccheck-s1.json.gz` | the check of C per listed session (`s1`'s gzipped only, as above) |
| `aifoundry2/` | the queue's records: `queue.jsonl`, `status.json`, `admission.json`, `idle_logins.jsonl` (counts only), the snapshots, configs and sensor reads, the smoke, the two stop tests and `s1` (runs, launches and the C log gzipped, the sampler lines in `tel/` gzipped, `sp/` traces) |
| `logs/` | `queue.out`, the slot file, the box's file hashes and their check, the code-path check, the login scrub's count (0 marks), the C-log list (D1, masked by the rule) |

SPDX-License-Identifier: Apache-2.0
