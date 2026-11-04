# E154: heat over minutes predicted from the bits on aifoundry3 card 0 - four 10-minute holds of new kinds, every plateau inside its registered band, 0.37 °C rms from the bits against 0.34 °C given the measured watts

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 9** (heat over minutes: a steady state for heat), **item 8** (the heat path between sessions) and **item 6** (the power model). It
answers **rank 4 of Q138's final critic**, "Heat over minutes predicted end to end from the computation's description ... The
bits-to-M7-power-to-chain path for a new kind has never been scored", its aifoundry3 half (E161 is aifoundry2's). Tue 3 Nov 2026 (week 45),
Q139. The owner's mandate: his words of 2 November 2026 ("settle any unanswered questions regarding horace's power model"), with his goal "to be
able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible".*
- **Frozen first:** Q139(e)'s predictions, `predictions-q139e.json` (`455c46c1`, 06:00:48 PST) and amendment A1 (`e224a3f8`, 06:51:54 PST),
  [`../2026-11-03-q139e-heat-end-to-end/`](../2026-11-03-q139e-heat-end-to-end/README.md): M8's watts from the bits for pool 6's four hold
  candidates through Q138(t)'s frozen chain, with the bands and rules. Nothing was fitted here.
- **Pre-registered** in `8c23853c` (pushed 17:51:30 PST), before the claim (17:52:43) and before any device access (17:52:59):
  [`tools/claims-v3/e154/README.md`](../../../../tools/claims-v3/e154/README.md). The post hoc script `posthoc_e154.py` was committed in
  `64aa95ee` (17:56) during R0, before any hold's data.
- **Card:** aifoundry3 card 0, 600 MHz in all 44,259 samples. `ettelem config` read at the session's start (17:52:59), at both ends of both
  blocks and at the session's end (19:06:50): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV every time. Nothing was set.
- **Card session** 17:52:59-19:06:50 PST, **73.9 card-minutes**, inside the 76: the smoke with its five stop tests (block 15401), then **the
  full design** in one measured pass, 15420 (17:54:12-19:06:50).
- **Every device-management command sent was a read** (ten kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November
  2026 allows); no statistics reset (`since_reset_ms` −1 in every sample).
- **Every launch's C is bit-exact:** 6,346 of 6,346 dispatches (the smoke's 58 and the pass's 6,288) read PASS against the RTL's arithmetic
  (Q139(k)'s `ccheck.py`), so every hold ran the computation it was meant to.

**In plain words.** Before today, every check of this chip's heat over minutes was given the board's measured watts. Here the watts came from
the numbers alone: a model (M8) read each tile's bits and said how many watts it would draw, and a frozen heat model (Q138(t)'s chain) turned
those watts into a die temperature over ten minutes. Four kinds the models had never seen ran for ten minutes each: a real attention block in
fp32 (a causal softmax times V), a real int8 W8A8 projection, an int8 kind whose B lines flip between all-zero and all-one bytes, and an fp32
kind with one walking bit. **Each plateau landed within 0.02-0.49 °C of the prediction from the bits, 0.37 °C rms, all four inside their
registered 95% bands.** Given the measured watts instead, the same heat model reads the same holds to 0.34 °C rms. So composing the power model
in front of the heat model costs almost nothing in the total here: on the two fp32 holds its errors partly cancel the heat model's, and on the
two int8 holds the heat model given watts is nearly exact (+0.005 and +0.073 °C), so the error there is the power model's (±0.4 W).

## Results

**The registered verdicts** (`scored.json` › `verdicts`, the registered scorer `score_e154.py` on pass 15420):

| hold | kind | arm E, end to end from the bits (the primary) | arm A, given the measured watts (the comparison arm) |
|---|---|---|---|
| **K_S** | `fp32.real_smol_softmax_v_causal`, 3.20 s every 4.37 s | **PASS** | **PASS** |
| **K_Q** | `int8.real_qwen_w8a8_v`, back to back | **PASS** | **PASS** |
| **K_L** | `int8.b_line_zero_ff`, back to back | **PASS** | **PASS** |
| **K_O** | `fp32.a_onebit_b5_third`, back to back | **PASS** | **PASS** |
| **H_M** | `int8.full` (E97's H1 again; not end to end) | (b) from E78's watts **PASS**; (c) the replicate **PASS** | **PASS** |

**The numbers** (`scored.json` › `holds`; rises are over each hold's anchor, the last 120 s of the rest before it, read the same way in the
measurement and the prediction; the plateau is the last 300 s):

| hold | rest die before (34-sensor mean, last 120 s) | share / period | measured plateau rise | arm E predicted (M8), over the carried-in tail | **arm E error** | checkpoints' rms (60 s to the end) | band / FAIL beyond | arm A rms / plateau error | **E − A** |
|---|---|---|---|---|---|---|---|---|---|
| **K_S** | 54.653 °C | 0.7891 / 4.37 s | 11.792 °C | 11.768 (tail 3.21) | **+0.024** | 0.372 | 0.599 / 1.30 | 0.330 / +0.418 | −0.394 |
| **K_Q** | 56.066 | 0.9615 | 5.673 | 6.091 (tail 4.43) | **−0.418** | 0.401 | 0.941 / 1.882 | 0.058 / +0.005 | −0.423 |
| **K_L** | 54.583 | 0.9616 | 4.024 | 3.532 (tail 3.07) | **+0.492** | 0.450 | 1.446 / 2.892 | 0.107 / +0.073 | +0.419 |
| **K_O** | 53.383 | 0.9610 | 11.546 | 11.186 (tail 1.89) | **+0.360** | 0.344 | 0.688 / 1.376 | 0.406 / +0.536 | −0.176 |
| **session** (4 holds) | R0: 51.410 °C (the room; K_S at the plan period) | | | | **0.370 rms**, mean +0.115 | | | **0.342 rms**, mean +0.258 | 0.37 rms |

**H_M, E97's H1 again (item 8, a third session):** from a rested die (51.410 °C), its rise per board W at 570-630 s is **0.884 °C/W, 0.984 of
E97's H1** (PASS inside [0.94, 1.06]); from E78's measured watts the plateau error is **+0.194 °C** with the checkpoints at 0.180 rms (PASS
±1.30, and inside the tight 0.361 °C); arm A rms 0.345, plateau +0.352 (PASS).

**The arms beside** (registered as reported; `scored.json` › `holds` › `M7_through_the_chain`, `M6_through_the_chain`,
`E153_through_the_chain`; the plateau errors in °C):

| hold | M8 S (W) → error | M7 S → error | M6 S → error | **E153's measured S** (4.5 s runs this afternoon) → error | E − E153 |
|---|---|---|---|---|---|
| K_S | 15.674 → +0.024 | 15.605 → +0.095 | 15.528 → +0.177 | 15.298 → +0.417 | −0.393 |
| K_Q | 9.241 → −0.418 | 9.239 → −0.437 | 9.250 → −0.475 | 9.043 → −0.299 | −0.119 |
| K_L | 5.935 → +0.492 | 6.250 → +0.130 | 6.649 → −0.324 | 6.378 → −0.087 | +0.579 |
| K_O | 11.427 → +0.360 | 11.373 → +0.529 | 11.317 → +0.730 | 11.463 → +0.459 | −0.099 |
| **rms** | **0.370** | **0.352** | **0.473** | **0.347** | |

- **Against the critic's decisive scale** (Q139(e)'s `critic_scale_C`, reported by the rule: √(0.18² + (0.87 σ_S)²) per hold): K_S 0.024
  within 0.278 °C, K_L 0.492 within 0.574, **K_Q 0.418 over 0.369 and K_O 0.360 over 0.277**. The session's 0.370 °C rms sits at the critic's
  "about 0.35 °C". Two of four holds pass that tighter test; the registered bands (D4 of Q139(e)) are 1.7-4.1 times wider.
- **M6's frozen step response on the measured trace** (`a_M6`, no leakage loop) reads the four plateaus 0.95-1.39 °C low and H_M 0.28 °C low,
  rms 0.70-1.42 °C: as in E144, the leakage loop is what makes the chain right.
- **The plan readings:** the measured rises against amendment A1's table (the registered machinery on the plan's records at a 51.2 °C room) are
  +0.07 (K_S), −0.42 (K_Q), +0.48 (K_L) and +0.34 °C (K_O); against the frozen session table +0.43, −0.53, +0.48, +0.34 (A1's C1: the table ran
  K_S at a rounded duty).

**Post hoc** ([`posthoc.json`](posthoc.json), [`tools/claims-v3/e154/posthoc_e154.py`](../../../../tools/claims-v3/e154/posthoc_e154.py),
committed before any hold's data; never a verdict):

| hold | board over R0's P_ref, last 300 s: measured / M8's loop / E153's loop (W) | S at work over the last 300 s, after the leakage law (W) | M8's S | E153's S |
|---|---|---|---|---|
| H_M | 12.85 / 12.98 / — | 9.43 | 9.648 (E78's) | — |
| K_S | 17.38 / 17.72 / 17.25 | 15.21 | 15.674 | 15.298 |
| K_Q | 11.90 / 12.39 / 12.11 | 8.81 | 9.241 | 9.043 |
| K_L | 8.15 / 7.74 / 8.35 | 6.14 | 5.935 | 6.378 |
| K_O | 15.60 / 15.54 / 15.59 | 11.29 | 11.427 | 11.463 |

- **The power path over minutes:** M8's loop reads the board 0.34 W high on K_S, 0.49 W high on K_Q, 0.41 W low on K_L and 0.06 W low on K_O.
  On the first three that is the E − A column (−0.39, −0.42, +0.42 °C at the chain's ~1 °C per W). K_O's −0.18 °C comes with a +0.06 W board
  error in the hold, so most of it is carried in, consistent with K_L's under-read board leaving arm E a smaller tail at K_O's start (E − A
  counts the power errors of the holds before, through the tail, as well as the hold's own).
- **The S at work after ten minutes** is 0.09-0.24 W below E153's 4.5 s measurement on all four tiles (mean −0.18 W). This reading divides by the
  leakage law, E97's pooled quadratic, which is not E153's footing, so the offset is as much the two leakage corrections as the tiles.
- **The carried tail is not optional:** restarting the loop at each hold's own rest die, as if that warm die were the room, reads K_S, K_Q, K_L and
  K_O 3.8, 5.4, 2.8 and 1.8 °C too high (errors −3.79, −5.39, −2.75, −1.83 °C; H_M, from rest, unchanged at +0.19).
- **The room:** R0's rest die moved ±0.25 °C moves every arm E plateau error by at most 0.04 °C.

**Trajectories.** On the two fp32 holds the measured die rose slower than predicted in the first three minutes (K_S −0.40 to −0.51 °C at
60-180 s, K_O −0.20 to −0.28) and was still rising at the end (+0.24 and +0.49 °C at the hold's end). On the int8 holds the error is flat from
two minutes on (K_Q −0.37 to −0.48, K_L +0.41 to +0.51): a level, which is the power model's (A is 0.06-0.11 °C rms there). The fp32 holds'
shape is the heat path's: given the watts, A's plateau errors are +0.42 and +0.54 °C on K_S and K_O, against E144's +0.015 and −0.032 °C on
this card on 2 Nov.

## What this does to predicting power and heat

**The term tested** is the whole path from a computation's description to its die over minutes on a pinned card: the tile's bits, then M8's
switching watts, then Q138(t)'s closed chain from watts to the die, carried through the tails of the holds before.

**Out-of-sample error of heat over 10 minutes for a new kind on aifoundry3, before:**
- from the bits: **never scored**. Q139(e)'s expected 95% sizes were 0.60-0.69 °C (floats) and 0.94-1.45 °C (int8); the critic's scale about
  0.35 °C;
- given the measured board watts: 0.04-0.18 °C rms on E144's two holds (2 Nov), plateaus +0.015 / −0.032 °C;
- from the bits over a 4.5 s run: 0.10-0.13 °C (E153, M8, today).

**After (this session, four new kinds, registered):**
- **from the bits: 0.370 °C rms on the plateaus** (largest 0.49 °C, K_L), **trajectories 0.34-0.45 °C rms**, every hold inside its band;
- given the measured watts (arm A), the same holds: 0.342 °C rms, mean +0.258 °C, so the heat path alone is now **0.3-0.5 °C on hot fp32
  holds** on a second session of this card, not 0.04-0.18;
- the power path's share (E − A): 0.37 °C rms, with M8's in-hold board errors −0.49 to +0.41 W (post hoc);
- from E153's measured watts for the same tiles: 0.347 °C rms. So the bits are within 0.02 °C rms of having measured the tiles first, at n = 4.

**What it changes:** heat over minutes from a computation's description can now be quoted on aifoundry3 at about **±0.4 °C on a 10-minute
plateau (rms 0.37 °C over n = 4 new kinds; 95% interval for the 1σ 0.22-1.06 °C, χ² with 4 degrees of freedom)**, with the power model and the heat model contributing about equally. The model ranking is not resolved at
n = 4 (M8 0.370, M7 0.352, M6 0.473 °C rms). K_L again shows M8's int8 near-whole-byte discount over-correcting (M8 +0.49 °C, M7 +0.13, M6 −0.32;
the S at work, 6.14 W, lies between M8's 5.94 and M7's 6.25), as E153 found over 4.5 s. The heat path's +0.4-0.5 °C on the fp32 holds is the
next term to correct (item 9: a slow stage or a between-session move; E97's moves were 0.3-0.8 °C).

## Registered against what happened

| registered | what happened |
|---|---|
| the full design if the session's anchor is at or before 20:40 PST, budget 76 card-minutes | T0 17:52:59 PST: the full design; 73.9 card-minutes |
| the room rule (R0's rest die) sets K_S's period | 51.410 °C ≤ 51.5 °C: the plan period, 4.37 s; K_S ran 137 cycles, the median period 4.37 s, share 0.7891 (plan 0.7908) |
| natural chain holds | 90 (H_M) and 81-84 launches (the pool-6 holds), share 0.9610-0.9616 (plan 0.9655; the C log and the wrapper's hash sums take about 0.4%) |
| stops: gate 70 °C, hold 72 °C / 65 W, session 74 °C, on live samples | none fired in the pass: highest board 45.34 W (K_S), highest `minshire[0]` 66 °C, highest 34-sensor mean 67.54 °C (K_S) |
| every planned in-launch peak at or under 67.5 °C | K_S's peaked at 67.54 °C, 0.04 °C over the design line (A1 put it at 67.40 °C at a 51.5 °C room), 4.5 °C under the hold stop |
| the five stop tests in the smoke | all passed (`logs/smoke-gate.json`): no launch at a 1 °C gate; the hold's die and board lines ended a hold with no launch; a board line 4 W over the idle (27.57 W) ended the launch in flight 1 s in, at a live sample of 38.90 W; the session line ended the block with exit 6 |
| the smoke gate | GO (block ok, every stop test, each tile launched, a sound C log, the 34 raw codes in every line, 600 MHz, both config reads) |
| the C check, a validity label | 6,346 of 6,346 PASS: every hold "C verified" |
| no hold dropped, no departure after the data | none |

## Device commands sent

As registered ([`tools/claims-v3/e154/README.md`](../../../../tools/claims-v3/e154/README.md#device-commands-sent)); the preflight read GO on the
box at the session's start (`logs/dmcmd-preflight.txt`: 38 send sites, 0 disallowed, the one reviewed exception lib.sh:154):

| command | sent by | class |
|---|---|---|
| `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` (25), `…_TEMPERATURE_THRESHOLDS` (21), `…_POWER_STATE` (23) | `ettelem config` through E128's guard: the session's start and end, each block's start and end | READ (RAM copies; et-platform `836a4ab` thermal_pwr_mgmt.c:613-617, 665-669, 551-555) |
| `DM_CMD_GET_ASIC_FREQUENCIES` (53) | `ettelem config`, `pvt_sample.py` (10 Hz), lib.sh's `die_c` | READ (PLL register reads) |
| `DM_CMD_GET_ASIC_VOLTAGE` (32) | `ettelem config`, `pvt_sample.py`, `die_c` | READ (two PMIC voltage-register reads; allowed by the owner's rule of 2 November 2026) |
| `DM_CMD_GET_MODULE_POWER` (33), `DM_CMD_GET_SP_STATS` (60), `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` (27) | `pvt_sample.py`, `die_c` | READ (RAM copies; PVT register reads) |
| `DM_CMD_GET_MODULE_VOLTAGE` (31) | lib.sh's `die_c` at each block's start and end | READ (nine PMIC voltage-register reads; allowed) |
| `DM_CMD_GET_ASIC_PVT_SAMPLES` (74), group 0 only | `pvt_sample.py` at 10 Hz | READ, from the held patch source (E144's classification and residual) |
| the C-logging host (`sparsity_ccheck.sh` → `build/ccheck/b/host/sparsity_host`, E78's kernel) | every launch | no device-management command (ops node: code load, DMA, launches) |
| **not sent** | — | the statistics reset (`--reset-ms`), command 74's group 6, the firmware-revisions query, any residency read, any set, any reset, `dev_mngt_service` |

## The day's post

Tue 3 Nov's one `#community-lab` post, message `1567332504330051616`, under the discord lock with `EXPECT_TEXT`, dry run, save and read back:
- **claim, 17:52:43 PST:** from `<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~17:54 PST [doc](<…/horace-kinds-of-numbers>) — released`
  to `<ai> **Claude says:** using aifoundry3 for 1.5 h, until ~19:22 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`;
- **release, 19:07:58 PST:** the same text with ` — released` appended (the only card held), every word kept.

Mon 2 Nov's post was not touched, and no other post was made.

## What this cannot say

- **One session, one card, four kinds.** A 1σ from n = 4 has a wide interval: 0.37 °C rms gives 0.22-1.06 °C at 95% (χ², 4 degrees of freedom). The plateau moves
  0.3-0.8 °C between sessions on this card with nothing changed (E97), and the room's only proxy is the rest die; there is no inlet thermometer.
- **The 10-minute holds read 92-95% of their fixed points**, like for like in prediction and score, not a steady state. Three holds started on
  tails of 1.9-4.4 °C, which the chain carries; restarting it at the rest die instead would have been 1.8-5.4 °C wrong.
- **The bands do not separate the models** (Q139(e)'s D4): M8, M7 and M6 all PASS by the same rule on three or four holds.
- **The S-at-work reading is post hoc** and rests on E97's pooled leakage law at 53-67 °C.

## How to reproduce

```bash
# the C check (Q139(k)), on the two C logs, then the registered scorer and the post hoc readings (numpy 1.26.4, Python 3.9)
gunzip -k docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p154*.jsonl.gz
python3 tools/claims-v3/ccheck/ccheck.py check docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p15401.jsonl \
  docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/ccheck/c-log-p15420.jsonl --out /tmp/ccheck-all.json --jobs 6
python3 tools/claims-v3/e154/score_e154.py docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420 --json scored.json
python3 tools/claims-v3/e154/posthoc_e154.py docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420 --json posthoc.json
python3 tools/claims-v3/e154/score_e154.py --self-test
```

## Files

| file | what |
|---|---|
| `scored.json` | the registered scorer's output: every arm per hold, the verdicts, the session figure |
| `posthoc.json` | the post hoc readings (power over minutes, S at work, the tail, the room) |
| `aifoundry3/e154/p15420/` | the measured pass: `telemetry.jsonl.gz` (the 10 Hz sampler with the 34 raw codes), `marks.jsonl` (rests, holds, launches, `rest_die`, `room`), `runs.jsonl` (one record per dispatch), `run.log`, `configs.json`, the config reads, `block.json`, `gen.sha256`, `binaries.sha256`, `manifest.txt` |
| `aifoundry3/e154-smoke/p15401/` | the smoke and the five stop tests, in the same layout |
| `ccheck/` | the two C logs (`c-log-p15401.jsonl.gz`, `c-log-p15420.jsonl.gz`; moved here from the pass directories, byte-identical) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `logs/` | the session log, the session's config reads with their times, the device-command preflight, the smoke gate |
