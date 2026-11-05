# E169: the stride shapes on aifoundry2 under its own governor - both power-of-two panel strides step, +30.0% at P1/N1 and +27.1% at P3/N3, each 0.81-0.88 of the L3 set map's frozen step: the registered verdict on the 8 MB index is A STRIDE STEP SM DOES NOT SIZE; B7 FAILS as expected; tied to E158

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 1** ("where a large GEMM falls"). It answers **rank 6 of Q139's final critic** and Q140's final critic's new fault 3 (the step
rule), through Q140's and Q141's critics' E169 entry (`card_half[6]`).*

*Wed 4 Nov 2026 (week 45), the card half of Q141, aifoundry2 card 0 under its own governor (65 W / 65 °C read before and after and after
every run, nothing set), E136's binary with every shape an argument. Registered before any E169 data: Q140(q)'s B6-B7 (`49575094`, the
predictions `e39d06da` and `1bfaa4e4`); amendment A2 with the step rule ([`REGISTRATION-A2.md`](../../../../tools/claims-v3/e169/REGISTRATION-A2.md))
`217c94a2` (09:22:23 PST); the scorer `18aaca80` (09:33:28); the kit `6a3929ec` (09:46:17); the notes `2bf8f092` (09:47:26) and
`5c9a62f1` (10:44:17). It ran last on aifoundry2 after E165, E167 and E168, from the checkout at `5e1bb309` (E165's README, D1). The day's
one `#community-lab` post (message 1567662592850399304) named aifoundry2 from 14:11:27 PST to the release at 17:18:22.*

## The answer

| pair (P over N), fp32 zeros | the step T800(P) / T800(N) − 1, 5 passes | its 95% interval | SM's frozen step | ISO / STRICT | reading |
|---|---|---|---|---|---|
| **P1/N1** `gemmL1x8x5` / `gemmL1x7x5` (decisive) | **+30.00%** (passes +30.58, +29.62, +29.39, +29.95, +30.47) | [+29.36, +30.65] | +37.06% | 0.00% / 0.00% | none of the three: between STRICT's zone and SM's; a step is **present**, its size **not SM's**; 0.81 [0.79, 0.83] of SM's step |
| **P3/N3** `gemmL1x4x8` / `gemmL1x5x8` (decisive) | **+27.11%** (+26.91, +26.49, +27.07, +27.31, +27.75) | [+26.53, +27.69] | +30.97% | 0.00% / 0.00% | none of the three; **present**, **not SM's** size; 0.88 [0.86, 0.89] of SM's step |
| P2/N2 `gemmL2x8x3` / `gemmL2x6x3` (reported) | +4.47% | [+3.81, +5.14] | +7.94% | +5.76% / −1.03% | supports ISO |

**The registered verdict on the L3's 8 MB index** (A2 S4, from P1/N1 and P3/N3): **A STRIDE STEP SM DOES NOT SIZE**: both pairs show a
step, and at least one lies outside SM's ±3-point zone (P1/N1's interval lies 6.4-7.7 points under SM's +37.06%, 3.4-4.7 under its zone;
P3/N3's 3.3-4.4 points under SM's +30.97%, 0.3-1.4 under its zone).

| also scored | result | verdict |
|---|---|---|
| B7 as registered (SM's frozen T800 within 3% on every shape) | SM's level 13.3-22.0% above the measured T800 on all six shapes; resolved 0 of 3 | **FAIL** (registered as expected to fail) |
| the ties to E158 | T800 of `K4n7`, `K4n8`, `K6n5`, `K6n4` within −0.19% to +0.28% of E158's; steps `K4n8/K4n7` +29.20% (E158 +28.89%), `K6n4/K6n5` +14.32% (E158 +14.86%) | **TIED** |
| R0, the check of C | 50 runs, every one exact | **PASS** |
| each model's level (rms over the six shapes, fp32) | ISO 10.2%, STRICT 15.4%, SM 18.7% | reported |
| fp16 and int8 (one pass each, printed, no reading) | P1/N1 +29.36% / +28.69%; P3/N3 +27.56% / +26.79%; P2/N2 +4.81% / +4.02% | printed |
| a zeros burst's power on the six new shapes (D12) | fp32 p800 against P0 + β δ + 0.47 (T_start − T_ref): 0.72 W rms (mean −0.68); against P0 alone 2.51 W | reported |

Source: [`results.json`](results.json) › `scores`, printed in [`score.txt`](score.txt), by the registered scorer
[`score_e169.py`](../../../../tools/claims-v3/e169/score_e169.py) on `aifoundry2/s1` (the only session).

## What this does to predicting power and heat

Time per op sets a large GEMM's energy per op (E = P·T) and, under the governor, its clock and power. Before E169, a new shape's time per
op stood at ISO's 6-11% rms (E158's retention curve, no set index), with single misses of 8-13% at power-of-two panel strides, and SM as a
level failed at 13-14%. **E169 shows the power-of-two stride step is real on this card and repeatable** (5 passes, each within about
±0.6 points of the pooled step; the two tied steps within 0.3 and 0.5 points of E158's), **but smaller than the public set map with its 8 MB index predicts**: 81% and 88% of SM's step. So,
as the registered reading says, a stride term stays in the next time model with its size unknown here; fitting it to these two pairs
afterwards would not be blind, so any size must be registered and tested on further shapes. ISO's level (10.2% rms) remains the best of
the three on these six shapes. Heat: nothing directly (zeros bursts at 36-37 W board). The power reading puts E136's P0 with Q140(l)'s zeros
level and the start term within 0.72 W on six shapes that had never run.

## The session

| | PST | card-minutes | |
|---|---|---|---|
| queue | 17:06:32-17:17:49 | | `queue_e169.py --slots ~/claude/work/q141-a2-e169-slot.txt --runs build/e169/runs`, detached, into an empty `build/e169/runs`; slot 17:06:32-17:51:32 |
| smoke | to 17:07:33 | 1.0 | rc 0 (30 s rest, four 2 s checked launches) |
| stop test, board | to 17:07:37 | 0.1 | `board_cap_w` 30 W: `board 35.0 W > 30 W on 3 samples` |
| stop test, die | to 17:07:39 | 0.0 | 30 °C: `die 70 C >= 30 C` on the first live line (the hottest-sensor latch) |
| `s1` | 17:07:39-17:17:49 | 10.2 | A-F, 50 bursts, none refused by the admission, every cool gate reached; exit 0 "done" |
| in all | | **11.3** | the cap 20, at most 25 |

Peaks: board 36.95 W, the shires' mean 55 °C, the hottest-sensor field 70 °C (its latch). The registered stops (board above 60 W on three
live samples, a die reading at or above 76 °C, the 82 W admission, the 60 W peak lock) never came near; both fired on live samples in
their tests. The hottest-sensor field read 70 °C, under the 76 °C die line, so the smoke's die check passed after E168 (README box step 6).

## Departures and notes (dated, Wed 4 Nov 2026)

- **None from the registration.** The dry pass (README.md.dated-note.md box step 4) ran into `build/e169/dry` with its own slot file and
  ended rc 0 at 14:31:23 PST, before E165's session; `build/e169/runs` did not exist when the queue started; the tree, the 54-file and
  3-tile hash lists, `score_e169.py check` and `selftest_kit_e169.py` read clean on the box at 14:22 PST.
- **The tree**: fast-forwarded to `5e1bb309` before the day's first session (E165's README, D1).
- **Collection**: the runbook's v2 step (`tools/claims-v3/q141k-runbook/v2/s22_collect.sh e169`): a bounded copy of `build/e169/runs`
  only (never `build/e169/dry`), E111's login scrub, the gzip of E158's committed layout, then `score_e169.py <dir>/aifoundry2/s[1-6]`.

## Device commands sent

Exactly the registered set ([`README.md` § Device commands sent](../../../../tools/claims-v3/e169/README.md#device-commands-sent);
[`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e169/logs/dmcmd-audit.txt): GO, 19 send sites, every one READ). No statistics reset, no
firmware-revisions query, no governor, TDP, threshold or clock set.

## Files

| file | what |
|---|---|
| [`results.json`](results.json), [`score.txt`](score.txt) | the registered score (the step rule, B7, the ties, R0, the levels, the power reading) |
| `aifoundry2/` | the queue's records and the smoke, the two stop tests and `s1` (launches and the sampler lines gzipped, `sp/` traces) |
| `logs/` | `queue.out` and the slot file |

SPDX-License-Identifier: Apache-2.0
