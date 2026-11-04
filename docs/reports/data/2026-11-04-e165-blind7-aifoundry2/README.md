# E165: blind pool 7 under aifoundry2's own governor - M9's aifoundry2 part, recomputed per tile, reads the 12 governed tiles' burst clock to 3.03 MHz rms (rank 2's clock line holds, resolved better than M7) and the board to 0.71 W governed and 0.99 W pinned, but rank 2's rule FAILS: neither board line is resolved better than M7 as frozen

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6, "a power model across kinds"**. It answers **rank 2 of Q139's final critic** (aifoundry2's level and session terms, scored blind)
and the E165 entry of Q140's and Q141's critics (`card_half[2]`).*

*Wed 4 Nov 2026 (week 45), the card half of Q141, aifoundry2 card 0 under its own governor (65 W / 65 C read at the queue's start and
end, nothing set). Registered before any E165 data: [`E165.md`](../../../../tools/claims-v3/e165/E165.md) `3ef06839` (09:36:11 PST),
the scorer `a5c56d17` (09:37:49), the kit and A1 `e3c4eafc` (09:43:55), the domain screen `fe6f4862` (10:43:24), amendment A2
`a509ff8b` (10:54:04, [`E165.md.dated-note-A2.md`](../../../../tools/claims-v3/e165/E165.md.dated-note-A2.md)). The owner's go was at
about 13:55 PST; the day's one `#community-lab` post (message 1567662592850399304, 14:11:27 PST) named aifoundry2 before the first
launch. The box's checkout ran at `5e1bb309`, which descends from every frozen commit (see Departures, D1).*

## The answer

| rule | set | measured (M9's aifoundry2 part, recomputed per tile) | line or reference | verdict |
|---|---|---|---|---|
| **E165-R2** (primary), G | governed clock, 12 tiles | **3.03 MHz rms, mean −1.04 MHz**; M9 − M7 rms [−4.61, −1.95] MHz | rms ≤ 4.0, \|mean\| ≤ 2.0, resolved better than M7 | **PASS** |
| E165-R2, Bg | governed board, 12 | **0.71 W rms, mean −0.43 W**; M9 − M7 rms [−0.96, +0.04] W | \|mean\| ≤ 0.5, resolved better than M7 | **FAIL** (not resolved) |
| E165-R2, Bp | pinned board, 40 | **0.99 W rms, mean −0.02 W**; M9 − M7 rms [−0.44, +0.08] W | \|mean\| ≤ 0.5, rms ≤ 1.0, resolved better than M7 | **FAIL** (not resolved) |
| **E165-R2** | G, Bg and Bp | | all three PASS | **FAIL** |
| E165-F1 | governed clock | 3.03 MHz rms | bootstrap of the end-to-end reference, 2.45-6.41 | PASS |
| E165-F2 | pinned clock | 5.11 MHz rms | 0.29-4.04 | **FAIL** |
| E165-W1 | governed board | 0.71 W rms | 0.42-1.14 | PASS |
| E165-W2 | pinned board | 0.99 W rms | 0.60-1.04 | PASS |
| E165-F3 | clock in the frozen band | 51 of 52 | at least 46 | PASS |
| E165-W3 | board in the frozen band | 45 of 52 | at least 46 | **FAIL** |
| E165-H1 | burst die rise | 0.455 °C rms | 0.556-0.811 | PASS (better than the reference says) |
| E165-H3 | die rise in the frozen band | 52 of 52 | at least 46 | PASS |
| E165-C | the check of C | **2,734 of 2,734 launches bit-exact** | all PASS | PASS |
| E165-R0 | E80's two replicates | fp16 randn 719.97 MHz / 66.03 W (−7.7 MHz, −0.56 W); int8 full 800 / 50.07 W (0, +0.27 W) | within 25 MHz and 3.37 W | PASS |

Source: [`results.json`](results.json) › `score.rules`, printed in [`score.txt`](score.txt), by the registered scorer
[`score_e165.py`](../../../../tools/claims-v3/e165/score_e165.py) on the session's counted runs, behind the code-path check
([`logs/path-check.txt`](logs/path-check.txt): PASS).

**Every numerical line of rank 2 holds** (the governed clock's rms and mean, both boards' means, the pinned board's rms), against the
registered forecast that the governed clock line would hold in only 35% of draws. **What fails is the resolution test**: the registered
form of "resolved better than M7 as frozen" is a paired 95% bootstrap over the set's tiles of rms(M9) − rms(M7), and on both boards the
interval reaches above zero. M9's board errors are smaller than M7's in this session (governed 0.71 against 1.20 W rms, pinned 0.99
against 1.15 W), but 12 and 40 tiles do not resolve that difference. On the clock, M9's part is resolved better than M7 (3.03 against
6.48 MHz rms).

## What this does to predicting power and heat

The term tested is **M9's aifoundry2 part** (Q140(l)'s cap plateau, the session's zeros level from its own anchors, the die at a
burst's start), blind, on a pool its fit never saw, in the session it predicts.

| | governed clock | governed board | pinned board | die rise |
|---|---|---|---|---|
| **before**: Q140(l)'s end-to-end held-out error (E160 / E143) | 3.68 / 5.12 MHz | 0.66 / 0.86 W | 0.80 / 0.87 W | 0.6845 °C (the heat law's reference) |
| **after**: E165, blind (M9's part, per tile) | **3.03 MHz** (mean −1.04) | **0.71 W** (mean −0.43) | **0.99 W** (mean −0.02) | **0.455 °C** |
| beside it, as frozen: M9 / M8 / M7 | 5.71 / 4.18 / 6.48 MHz | 0.69 / 1.53 / 1.20 W | 1.19 / 1.14 / 1.15 W | |

(`results.json` › `score.reported.by_set` and `lines_by_arm`.) So, on aifoundry2 under its governor, the blind error of the clock where the
governor acts is now about 3 MHz, inside the critic's 4 MHz line, and the governed board about 0.7 W. The pinned clock is the weak
point: **5.11 MHz rms against a 2.33 MHz reference**, because six pinned tiles each ran one of their three passes at 752-781 MHz while
their other passes ran at 800 (`fp32.exp_a_gray_walk` 756, `int8.a_full_b_pos` 754.2, `fp16.b_onebit_b9_one` 754.2,
`int8.bheld_55_asmall` 752, `fp32.dropout30_both` 758.8, `fp32.exp_b_alt_lsb` 780 MHz; `results.json` › `cells`). That is the mid-burst
dip E160 saw on three bursts (its M1), and no model of the bits predicts it: it is a session term of the governor, not of the data. The
zeros anchors ran every pass at 800 MHz, 1.00-1.08 W under the frozen fallback level (`score.reported.zeros_anchors`), and the session's
anchor delta is −1.47 / −1.25 / −1.58 W for fp32 / fp16 / int8 ([`anchor-delta-e165.json`](anchor-delta-e165.json)). The board's peak
samples ran over M9's frozen 95% upper peak on six single-bit tiles (by 0.66-5.25 W, 49 of 55 inside, at the line of 49;
`score.reported.peaks_vs_predictions`), all under the 82 W admission. The per-burst leakage slope k_T reads 0.348 W/°C [0.238, 0.411] against M9's 0.395 (reported).

## What ran

| | |
|---|---|
| queue | `queue_e165.py --slots ~/claude/work/q141-a2-e165-slot.txt --runs build/e165/runs --cap 40` (README box step 7), detached, 14:31:41-15:10:13 PST; its slot 14:31:41-15:16:41 |
| smoke | 14:31:41-14:32:34, rc 0: C 20 of 20 records; the DMA rule's projected held time 6.604 s under its 7.2 s limit |
| stop-path tests, on live samples | board: `safety:board 32.5 W > 30 W on 3 samples` (rc 4); die: `safety:die 70 C >= 30 C`, 59 ms after the first line (rc 4; the hottest-sensor field's 70 °C latch) |
| the session `s1` | 14:32:39-15:10:12 PST, **158 of the 171 registered bursts** (passes 1 and 2 whole, 44 of pass 3's 57), every one complete and counted; it ended with `error:telemetry_stale` at run 159 (D2) |
| card-minutes | **38.4** (smoke 0.9, stop tests 0.0, `s1` 37.5) of the 40 cap; 38.5 minutes of wall time |
| peaks | board 81.16 W (`fp16.randn_x8`, pass 1), the shires' mean 63 °C, the hottest-sensor field 70 °C (its latch) |
| the card at the start and end | `ettelem config`: TDP 65 W, threshold 65 °C, power state 3 (low power), 600 MHz at 519 mV, both times |

## Registered against what happened

- **The tiles scored are the registered 52** (12 governed, 40 pinned; the six left out by name stay out); every tile has at least two
  counted passes: 39 have three and 13 have two. Every rule is scored on the counted runs, as registered.
- **D1, the box's tree (14:19-14:22 PST, before any E165 launch).** README box step 3's `git pull --ff-only` refused on aifoundry2: the
  checkout sat at `0c187e12` (1 Nov) with 905 local entries, copies earlier lanes had synced in by hand. Before anything else, every
  entry was compared with `origin/main`'s blob: 903 byte-identical, one untracked older copy of `tools/claims-v3/e77/reduce_e77.py`, and
  one local tool directory outside `tools/` and `docs/`. The local copies were kept twice on the box (a tar file in `~/claude/work/` and a
  git stash), the checkout fast-forwarded to `5e1bb309`, and the 903 files re-hashed byte-identical after it; `git status --porcelain --
  tools/claims-v3` then read empty, `c31e7ae3` an ancestor, and every E165 preflight passed (61 tiles, blind7 91, the three binaries
  `eae32a15` / `990807f4` / `77a46171`). The collector's re-hash of the box's kit files, tiles and binaries against this tree reads "all as
  the desk's tree and the pins" ([`logs/box-files-check.txt`](logs/box-files-check.txt)).
- **D2, the session ended 13 bursts short, on the harness, not the card.** At 15:10:12 PST, 8.1 s into the sampler of run 159
  (`BURST-158-b7-fp16.randn_x8-r1`, a pass-3 burst still in its 55 °C cool gate, before any launch), run_hpl's guard found no telemetry
  reading newer than 5 s and ended the session (`error:telemetry_stale`, exit 1; [`aifoundry2/s1/end.json`](aifoundry2/s1/end.json)).
  The sampler itself never stalled: that run's telemetry file holds 83 lines at 100-101 ms spacing from 15:10:03.923 to 15:10:12.134, each
  with its die and board fields, and the card answered `ettelem config` at the queue's end. What the watcher saw is consistent with a
  race in `run_hpl.py`'s telemetry watcher (post hoc, not proven): `run()` reads `self.path` outside its lock, so a `follow()` of the next
  run's file landing between that read and the read of the old file leaves the read position at the old file's length (BURST-157's
  file is 90,896 bytes; BURST-158's was 58,432 bytes when the guard fired), and the watcher reads nothing new until the new file passes
  it. The guard's stale check is what made it safe: the stops cannot be blind for more than about 5 s. The 40-minute cap would itself
  have cut pass 3's tail about 2.5 card-minutes later (README: "`--cap 40` cuts pass 3's tail"). No burst was re-run.
- **The pinned clock's FAIL (F2) and the board band's 45 of 52 (W3)** are as measured; no tile or pass is set aside.
- **Nothing else departs.** The stops, the order, the slot, the cap, the check of C and the scorer are the registered ones.

## The stops, and their test on live samples

The registered stops: one die reading at or above 76 °C, or the board above 85 W on three live samples in a row (exit 4), plus the run-time
admission at 82 W (`e105`: every tile's estimate at most 82 W, the highest admitted 81.65 W) and E159's 82 W lock. Both stops were tested on
live samples by the queue before the session (above) and both fired as registered. Nothing came near a stop in the session: the highest
board sample was 81.16 W and the shires' mean 63 °C.

## Device commands sent

Exactly the registered set ([`E165.md` § Device commands sent](../../../../tools/claims-v3/e165/E165.md#device-commands-sent);
[`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e165/logs/dmcmd-audit.txt): GO, 19 send sites, every one READ): `ettelem sample`'s
and `ettelem config`'s reads (the PMIC voltage reads among them, the owner's allowed read-only reads), `ettelem sptrace`'s trace copy,
and the residency read that this build refuses before opening the device (rc 2, `aifoundry2/s1/queries.jsonl`). No statistics reset, no
firmware-revisions query, no governor, TDP, threshold or clock set. The day's look-first reads and the tree's fast-forward sent nothing to
the card.

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`score.txt`](score.txt) | the registered score (`score_e165.py`) |
| [`d-both.json`](d-both.json), [`d-both.txt`](d-both.txt) | the burst D in both forms (A2-4, reported; every anchor pass ran at 800 MHz, so the two forms agree) |
| [`anchors-for-e167-e168.json`](anchors-for-e167-e168.json), [`anchor-delta-e165.json`](anchor-delta-e165.json) | `score.anchors` and `score.anchor_delta`, for E167's E2 arm and E168's `--anchors` arm (both reported only) |
| `ccheck-*.json` | the check of C per session (`ccheck-s1.json` also gzipped) |
| `aifoundry2/` | the queue's records: `queue.jsonl`, `status.json`, the smoke, the two stop tests and `s1` (runs, launches and the C log gzipped, the sampler lines in `tel/` gzipped, `sp/` traces) |
| `logs/` | `queue.out`, the slot file, the box's file hashes and their check, the code-path check |

SPDX-License-Identifier: Apache-2.0
