# E96 data: the speed of more real tensors under aifoundry2's own governor, and whether real int8 sustains differently (Q132, Sun 1 Nov 2026)

Q132(r)'s 25 tier-1 real tiles, cut from six public models ([`tools/claims-v3/kinds/real2/`](../../../../tools/claims-v3/kinds/real2/README.md)), on aifoundry2 card 0 under the card's own governor. E87's six anchors ran again in the same session, and E87's three real int8 tiles ran against int8 full in four paired rounds. Every new tile and anchor got a **burst on a cool die**, run twice. Eleven new tiles and the anchors got a **sustained run** of about 76 s. **Nothing was set on the card**: the TDP and the threshold read 65 W and 65 °C at all 100 per-run reads of `ettelem config`, at the sessions' start and end queries, and at the queue's reads under the card lock at both ends of the card time. The sampler ran without `--reset-ms`.

The pre-registration is [`tools/claims-v3/kspeed/e96/`](../../../../tools/claims-v3/kspeed/e96/README.md) (`0c187e12`, pushed 01:13:09 PDT, 1 h 53 min before the first launch; clocks went back at 02:00 PDT that night). Its frozen predictions are [`predictions.json`](../../../../tools/claims-v3/kspeed/e96/predictions.json), sha256 `fd01c532…`: `claims.E96` of Q132(r)'s `predictions-real2.json` (sha256 `0957e0c2…`) verbatim, the anchors' tie cells, and the arm's rule. The card was under E98's lane's one claim for the night, `#community-lab` message `1566355908076765257`; E96 made no post and no release. **No amendment and no departure from the registered design.** This lane read nothing of the session while it ran; the reduction first ran on the complete session, after the slot's end.

| session | PST (UTC) | what |
|---|---|---|
| `smoke/` | 02:05:00–02:06:38 (10:05–10:06) | 75 s of the idle card with no launch (the rest reading), then three 2 s launches of real2 tiles, one at each gating level: 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; checked by the queue, not analysed |
| `s1/` | 02:06:38–03:15:20 (10:06–11:15) | the registered session, 96 of 96 runs, exit 0, **68.7 card-minutes** (70.3 with the smoke): `BURST` 62 runs (02:06:39–02:20:39), `SUS` 34 runs (02:20:44–03:15:14). The card was free 279 s before the slot's end |

## Results first

### 1. Every registered rule passes. Real int8 shows no difference that counts

[`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt). Rules S1–S5 are `claims.E96`, scored as frozen; T and I1–I3 are this lane's own, frozen in the pre-registration. The sustained halves of S1 and S5, and S4, hold the 11 float tiles that ran sustained: `sustained_first`'s last four, all int8, were cut before the data, as the pre-registration says.

| rule | verdict | what the data say |
|---|---|---|
| **E96-S1** E83's relation fed (a) holds the clocks | **PASS** | bursts **25 of 25** inside their scoring intervals, sustained **10 of 11**. The miss is fp32 `t5small_l0_down`, 795.4 MHz against the single point 800: limit `none`, die 59.2 °C, 2.6% of the window in launch ramps ([`checks.txt`](checks.txt) K3). Inside the frozen D-propagated ranges: 24 of 25 and 9 of 11 |
| **E96-S2** the gate buys burst clock | **PASS** | all six tiles read 800.0 MHz in both passes, **+96.1 MHz** in fp32 (randn 703.9) and **+77.3 MHz** in fp16 (randn 722.7); the bar is +40 |
| **E96-S2b** and sustained clock | **PASS** | the smallest is fp32 `resnet18_l3c1`, **+75.4 MHz**; the largest fp32 `t5small_l0_down`, +193.6; the bar is +50 |
| **E96-S3** no-zero real tiles burst at random's speed | **PASS** | fp32 **−3.4 MHz** (700.5 against 703.9), fp16 **+10.2 MHz** (732.9 against 722.7); the bar is ±15 |
| **E96-S4** the sustained limit called right | **PASS** | **10 of 11**. The miss is fp32 `vgg16_fc2`, `thermal` at 784.1 MHz against a predicted `none`: its c read 0.81 W above (a)'s, and the relation on the measured c gives 784.0 |
| **E96-S5** the relation on measured c | **PASS** | burst **7.9 MHz** rms over 25, sustained **10.3 MHz** rms over 11; the bar is 15 |
| **E96-T** the sessions tie | **PASS** | all twelve anchor rows within 25 MHz of the mean of E80's, E83's and E87's cells; the largest is fp32 randn's burst, −7.0 MHz. int8 full's sustained cell, 789.4, reads +4.5 |
| **E96-I1** real int8 against random int8, the clock | **`SAME_WITHIN_BAR`** | **+6.1 MHz, 95% [−0.8, +13.1]**, four whole rounds: it holds 0 and lies inside ±15. Not at the cap: one int8 full run tripped |
| **E96-I2** the board W | **`BELOW`** | **−2.18 W, 95% [−2.69, −1.68]**; expected at a fixed 800 MHz, −2.11 |
| **E96-I3** the die | **`BELOW`** | **−0.85 °C, 95% [−1.47, −0.23]**; expected at a fixed 800 MHz, −0.96 |

### 2. The ReLU tiles: the lower power buys clock, as the relation says, in the burst and sustained

All on aifoundry2 card 0, its own governor, 1,024 minions repeating one 16×16 TensorFMA on the tile pair. A burst cell is two 6 s runs from a die ≤ 55 °C; a sustained cell is the last 40 s of nine 8 s processes from ≤ 57 °C, one run per tile, two for randn. One sustained run's 1 σ is ±15.6 MHz on the thermal slope and ±5.6 MHz at a clamp (E83's corrections-check C3). The whole table, with p800 and pJ per operation, is [`tables.md`](tables.md); the blog's cells are [`cells.json`](cells.json).

| tile | gate closes | c W | burst MHz (− randn) | sustained MHz (− randn) | relation on measured c: burst, sustained | sustained rate | board W | die °C | limit |
|---|---|---|---:|---:|---|---:|---:|---:|---|
| fp32 randn | 0 | 25.56 | 703.9 | 601.8 | | 9.23 TFLOPS | 53.8 | 66.1 | thermal |
| fp32 `resnet18_l2c1` | 0.191 | 20.91 | 741.2 (+37.3) | 650.1 (+48.3) | 753.7, 630.2 | 9.85 | 55.4 | 65.6 | thermal |
| fp32 `resnet18_l3c1` | 0.445 | 15.29 | 800.0 (+96.1) | 677.2 (+75.4) | 798.9, 697.1 | 10.26 | 51.5 | 65.5 | thermal |
| fp32 `vgg16_fc2` | 0.723 | 9.15 | 800.0 (+96.1) | 784.1 (+182.3) | 800.0, 784.0 | 11.96 | 52.8 | 65.1 | thermal |
| fp32 `t5small_l0_down` | 0.949 | 3.19 | 800.0 (+96.1) | 795.4 (+193.6) | 800.0, 800.0 | 12.20 | 39.5 | 59.2 | none |
| fp16 randn | 0 | 23.07 | 722.7 | 608.8 | | 18.63 TFLOPS | 52.1 | 65.9 | thermal |
| fp16 `resnet18_l3c1` | 0.367 | 15.15 | 800.0 (+77.3) | 689.5 (+80.7) | 799.1, 699.0 | 20.79 | 52.6 | 65.6 | thermal |
| fp16 `vgg16_fc2` | 0.551 | 11.46 | 800.0 (+77.3) | 744.8 (+136.0) | 800.0, 748.5 | 22.50 | 53.1 | 65.4 | thermal |
| fp16 `t5small_l0_down` | 0.871 | 4.99 | 800.0 (+77.3) | 794.9 (+186.1) | 800.0, 800.0 | 24.38 | 43.8 | 61.9 | none |

(`results.json` `cells.<tile>`, `rules.E96-S2`, `rules.E96-S2b`, `posthoc.diff_from_random_rows`. The rate counts every multiply-add the kernel issues, the ones the gate skips included.)

- **The burst.** The six tiles under 15 W sit at the card's 800 MHz cap in all 12 passes, so the burst says they are below the power limit and cannot rank them. The one mid-power tile, `resnet18_l2c1`, lands between the cap and random data at 741.2 MHz, 12.5 below the relation.
- **Sustained, the clock follows the gate.** 677–690 MHz with 37–45% of the lanes gated, 745–784 MHz with 55–72%, 795 MHz with 87–95%.
- **The relation on each tile's measured power gives these seven tiles' clocks to 4.8 MHz rms in the burst and 11.6 MHz sustained. A baseline with no model, each tile at same-session random data's clock, misses by 82 and 141 MHz** (`posthoc.rms_by_group`). So unlike E87's, this clock test separates a model from "real = random". The largest sustained misses are the two ResNet fp32 tiles, +19.9 and −19.9 MHz, one run each on the slope.
- **The frozen sustained points read high on the gated tiles** (17.7 MHz rms) because Q130(n)'s predictor reads their power low: the measured c lies above (a) on all seven, by 0.79 W on average. **The gate law, stated separately in the freeze, lies nearer on six of the seven**: rms 0.25 W against 0.89 W, mean miss −0.01 W ([`checks.txt`](checks.txt) K4). This is c on this card, labelled. E95 holds the energy claims.

### 3. No exact zeros: GPT-2, BERT and ViT run at random data's speed. "No zero word" is not the whole condition

| tile | what | share of randn's switching | burst MHz (− randn) | sustained MHz (− randn) |
|---|---|---:|---:|---:|
| fp32 `gpt2_l3_mlp_down` | no exact zeros | 0.997 | 702.0 (−1.9) | |
| fp32 `gpt2_l9_attn_qk` | no exact zeros | 0.980 | 695.2 (−8.7) | |
| fp32 `bert_l6_up` | no exact zeros | 0.995 | 702.0 (−1.9) | 601.5 (−0.3) |
| fp32 `vit_l5_down` | no exact zeros | 1.000 | 703.0 (−0.9) | |
| fp16 `gpt2_l9_attn_qk` | no exact zeros | 0.956 | 732.6 (+9.9) | |
| fp16 `bert_l6_up` | no exact zeros | 0.995 | 731.2 (+8.5) | |
| fp16 `vit_l5_down` | no exact zeros | 0.984 | 734.9 (+12.2) | 612.0 (+3.2) |
| fp32 `t5small_l0_up` | no zero word, weights on the bf16 grid | 0.889 | 725.2 (+21.3) | 603.1 (+1.3) |
| fp32 `vit_l11_down` | no zero word, 64% −0.0 | 0.827 | 740.2 (+36.3) | 615.6 (+13.8) |
| fp16 `gpt2_l6_mlp_down_fp16fwd` | an fp16 forward pass | 0.994 | 708.2 (−14.5) | |

(`posthoc.like_with_like_ratios`, `posthoc.diff_from_random_rows`; share = (c − c_zeros) / (c_randn − c_zeros), all this session.)

- **S3's seven tiles are three of the six models.** GPT-2, BERT and ViT. ResNet-18's and VGG-16's tiles in this set all carry zero words, and T5-small's one no-zero tile is out of family, so "across six models" is not what S3 shows.
- **Clock against random.** fp32's −3.4 MHz is −0.6 σ. fp16's +10.2 MHz is +1.7 σ for a three-tile mean minus one cell, and E87 read +7.8 MHz for three other tiles, so the two sessions together read +9.0 ± 4.3 (1 σ), against +4.5 from the relation on the measured c. **Perhaps 1% in fp16, seen twice, still not established** ([`checks.txt`](checks.txt) K5).
- **These clock rules do not test the power predictor** on these tiles, as E87's correction C1 found: the no-model baseline scores 15.4 MHz in the burst and 7.1 sustained, against the relation's 11.8 and 7.5 (`posthoc.rms_by_group`). The shares: fp32 0.980–1.000, mean 0.993, t = 1.56 on 3 df against 1.000; fp16 0.956–0.995, mean 0.978, t = 1.88 on 2 df. **A little below random, not established here either.** E95 is the test of that.
- **What matters is how many bits move, not whether a zero word exists.** T5's `l0_up` has a full-mantissa A, and weights whose low 16 mantissa bits are all zero: it switches 0.889 of random (predicted 0.908) and bursts 21 MHz faster. ViT's last block has no zero word, because −0.0 is the word 0x80000000: **its c reads 21.40 W against 21.49 predicted if the gate is blind to −0.0, and 10.61 W if it were not**, so on this real tile the gate stays open. It still bursts 36 MHz faster, on fewer moving bits. Sustained, both sit at or near random data's floor.
- **The fp16 forward pass** costs what rounding costs, within what this can see: c 22.95 W and share 0.994 here, 22.92 W and 0.990 for the rounded tile in E87's session. Its burst, 708.2 MHz (passes 718.4 and 698.0), is the one no-zero cell near its interval's low end, 704.8. E95's C11 is the test ([`checks.txt`](checks.txt) K9).
- **int8 calibrations: all eight tier-1 int8 tiles burst at 800.0 MHz in all 16 passes**, whatever the calibration, so none of it moves the burst clock. From the 800 MHz power alone, GPT-2 layer 11's 99.9th percentile clip draws 5.84 W more than its max-abs scaling, and VGG's asymmetric activations 1.55 W more than its symmetric ones ([`checks.txt`](checks.txt) K2, K9). They had no sustained run: that was the cut registered before the data.

### 4. int8: no difference that counts, at one card's run-to-run spread, on a cool night

**The clock, sustained MHz, board W, die °C, limit**, by round, each round's runs back to back in a shuffled order ([`results.json`](results.json) `posthoc.arm_rounds_detail`, `rules.E96-I1`):

| round | int8 full | `l0_mlp_up` | `l6_mlp_down` | `l6_attn_qk` | mean(real) − full |
|---|---|---|---|---|---:|
| 1 | 791.6 / 52.66 / 64.7 / none | 800.0 / 51.94 / 64.4 / none | 800.0 / 49.90 / 62.8 / none | 793.9 / 49.59 / 63.5 / none | +6.4 |
| 2 | 793.4 / 53.19 / 64.9 / none | 789.7 / 51.51 / 64.9 / none | 800.0 / 50.87 / 64.5 / none | 800.0 / 50.39 / 64.2 / none | +3.2 |
| 3 | 777.2 / 51.65 / 65.0 / **thermal** | 789.3 / 51.30 / 64.6 / none | 789.7 / 49.77 / 64.1 / none | 789.2 / 48.59 / 62.7 / none | +12.2 |
| 4 | 795.4 / 53.32 / 64.9 / none | 794.4 / 51.57 / 64.5 / none | 800.0 / 50.41 / 63.8 / none | 800.0 / 50.41 / 64.3 / none | +2.7 |
| cell | 789.4 / 52.7 / 64.9 | 793.4 / 51.6 / 64.6 | 797.4 / 50.2 / 63.8 | 795.8 / 49.8 / 63.7 | **+6.1 [−0.8, +13.1]** |

- **The registered answer.** Real int8 sustains 6.1 MHz above random int8, 0.8%, with an interval that holds 0 and stops short of the 15 MHz that would count. **E87's single-run +21.3 MHz is not reproduced at that size.** The relation on E87's measured c expected +9.1 MHz, or +10.1 at this session's heat path, which the interval holds ([`checks.txt`](checks.txt) K6).
- **It is not a clamp result.** int8 full read `thermal` in one round of four, and it read 66 °C and stepped down in all four, for 2.8–14.8% of the window; the real tiles did so in one run of twelve, `l0_mlp_up` in round 2, for 4.6% (`runs[].sus_last`, `die_max`). The whole int8 row sat at 63–65 °C. The run-to-run spread was one run's sd 6.1 MHz, pooled over the four kinds (8.3 for full, about 5.1 for each real tile), near the low end of the 5.6–15.6 MHz the rule was planned on, which is why it resolved.
- **Real int8 draws 2.18 W less and runs 0.85 °C cooler**, both intervals clear of 0 and both close to the fixed-clock expectations. Leaving each round's first run out, since int8 full was never first and a run that follows a low-power run reads cool, gives +6.5 MHz [−0.4, +13.5], −1.98 W [−2.99, −0.96] and −0.61 °C [−0.79, −0.44] ([`checks.txt`](checks.txt) K6, K7).
- **Labelled, never a verdict.** Dips left out, +6.6 MHz [−0.4, +13.6]. The pooled two-way interval, which assumes one spread on and off the clamp, +6.1 MHz [+1.2, +11.0]. Each tile alone against full: `l0_mlp_up` +4.0 [−8.0, +15.9], `l6_mlp_down` +8.0 [+2.7, +13.4], `l6_attn_qk` +6.4 [−0.2, +13.0]. E98's fine W at 800 MHz, −2.13 W [−2.80, −1.45]. Trips: full 1 of 4, real 0 of 12, one-sided p = 0.25 (`posthoc.arm_labelled`).
- **Where the +6 MHz comes from, post hoc.** A run's samples below 800 MHz fall in two groups ([`checks.txt`](checks.txt) K6). **Launch ramps**, within 1.5 s of a process's start: a run has about 12–29 of them in its window or next to none, whatever the data (all four kinds in round 3), which fits Q132(g)'s heartbeat in the gap between kernels. **Later samples**: 102 of 1,599 for int8 full, 19 of 4,796 for the real tiles, the one idle-reset dip left out. That difference, 6.0 points of share, 95% [+0.1, +11.9], is at 100 MHz a step the arm's whole +6 MHz. So the difference looks real and small: random int8 touches the trip a little more often. The registered verdict stands as scored.
- **What this covers.** Three tiles of one model, one card, one night, 02:20–03:07 PST. The heat path ran 0.5 °C cooler than E87's on shared kinds (§5). A warmer night puts the whole row further into the trip, where the relation expects a larger difference (+14.0 MHz at E87's W*). That is not tested here.

### 5. The heat path and the rest readings, for E98

- **The pre-registration expected the 60 s reading not to be a true rest. It was one.** E98's probe P2 ended early at 09:37:54 UTC (01:37:54 PST), on the runner's other-user rule: another user had logged in. So the card had been idle 27.1 min when this queue took its first snapshot ([`checks.txt`](checks.txt) K8). That user was gone by then: E96's queue found nobody at 10:05 UTC, and its own session was never stopped.

| moment | reading (`posthoc.rest`) | rows | since the last busy row | board W | raw die °C | NIC °C | NVMe °C |
|---|---|---:|---:|---:|---:|---:|---:|
| E98 P2's rest reading, 09:30 UTC | E98's rule on the history | 240 | 36.2 min | 22.066 | 46.67 | 44.43 | 37.61 |
| **before E96's first launch, 10:05 UTC** | E98's rule on the history | 204 | 27.0 min | **22.145** | 46.79 | 44.45 | 37.60 |
| the same, 10 Hz | the last 60 s of the smoke's no-launch run | 600 | 27–28 min | 22.146 | 47 | | |
| E98 P3's rest reading, 11:40 UTC | E98's rule on the history | 177 | 24.7 min | 21.897 | 46.09 | 43.92 | 36.90 |

- **The die line for the session**, over all 34 sustained runs: **die = 41.408 + 0.4539 W, rms 0.589 °C**, 65.5 °C at 53.08 W. Its shift at E80's slope is **+0.12 °C**, against E87's +0.515 and E83's −0.149 (`posthoc.die_line_e96`). Arm (a-adj E96) puts W* at 49.50 W (E87's 48.47): sustained rms 13.6 MHz on the frozen c and 9.8 on the measured c, against 14.6 and 10.3 unadjusted.
- **E98's line**, die − 0.4573 W, on the four kinds E96 shares with E98's gated line and with E80, E83 and E87 (fp16 zeros, int8 zeros, int8 full, fp32 randn; [`checks.txt`](checks.txt) K7, labelled):

| session | first run | the line, °C | shift from E80 | rest W | raw rest die, °C | rest die from E80 |
|---|---|---:|---:|---:|---:|---:|
| E80 | Sat 31 Oct 12:22 PDT | 41.123 | 0 | 21.76 | 45.58 | 0 |
| E83 | Sat 31 Oct 13:46 PDT | 40.970 | −0.153 | 22.03 | 46.42 | +0.84 |
| E87 | Sat 31 Oct 19:49 PDT | 41.665 | +0.542 | 22.17 | 47.15 | +1.57 |
| **E96** | Sun 1 Nov 02:06 PST | **41.160** | **+0.037** | 22.145 | 46.79 | +1.21 |

  (Rest readings of the first three: the desk lane's table, [`2026-11-01-q132-governor-desk`](../2026-11-01-q132-governor-desk/README.md).) **E96 reads +0.04 °C of line for +1.21 °C of rest die, +0.03 per °C**, against the desk's 0.25–0.35, 95% roughly 0–0.6. It sits about 0.3 °C below that fit. One run's rms about a line is about 0.42 °C, so such a four-kind mean carries about ±0.2 °C and a difference of two about ±0.25 °C: a little over 1 σ. This is one point, and E98's night is the test. Beside it, the line's per-run values span 39.98–42.54 °C, and its trend through the session is +0.011 °C/min.
- **Heat carries over, post hoc.** A run's line rises with the previous run's board W: +0.043 ± 0.020 °C per W over 33 pairs, so about −0.7 °C after a zeros run against after a full-power one, whatever the gate reads ([`checks.txt`](checks.txt) K7).
- **The switching term stays put**: fp32 randn's c 25.56 W (25.55, 25.59, 25.59 in E80, E83, E87), fp16 randn's 23.07 (23.07, 23.05, 23.15), int8 full's 8.88 (8.99, 8.98, 8.88).

## What was registered, and what happened

Everything ran as registered: 96 of 96 runs, including all of G3, the five sustained runs that ran only if the clock allowed. At 13.6 s a burst and 96.4 s a sustained run the session was a little under E87's rates. The plan was about 65 card-minutes; with G3 it took 70.3, and the card was free 279 s before the slot's end, 24.7 min before P3's rest reading. No cap was reached, no stop-file was touched and no SIGTERM was sent. No safety stop (peaks: die 67 °C, board 88.45 W; stops 85 °C and 97 W on three samples). Every launch rc 0, all 100 samplers started on attempt 1 and stopped with rc 0, every gate reached, 109.8 s held before bursts and 444.1 s before sustained runs ([`checks.txt`](checks.txt) K1). The box's tree was `0c187e12`; every file the session ran matched the Intel's by sha256; the binaries are E87's (`7adadf4f…`, `990807f4…`, `77a46171…`). `kspeed.json`'s `git_dirty` lists another lane's untracked files, none of which this session ran.

**No login stopped or held this session.** The queue found the card free at the slot's start, 0.1 s late, with no wait. The runner's other-user check passed before all 368 work processes, and `marks.jsonl` holds no `other_user` mark.

**One expectation was wrong and one estimator caught us out; neither touches a rule.**
- The rest reading, §5.
- **E64's c is not fit for a tile that holds 800 MHz in a burst.** It fits all three clocks the burst touched, and such a tile has only one or two ramp samples at 700 MHz, whose reading can sit at 600's. int8 `vgg16_fc2`'s P700 read 36.96 and then 31.65 W, and its c 5.856 and then 4.756, while its P800 read 44.30 and 44.36 W. Three int8 tiles' like-with-like shares differ by 0.16–0.19 between rounds for this reason (`vgg16_fc2`, `gpt2_l6_down_p9999`, `gpt2_l11_down_p999`); every other tile's differ by at most 0.03. It moves no rule: each of those clocks sits at 800 whatever c reads. For int8 read the shares from the 800 MHz power ([`checks.txt`](checks.txt) K2): `resnet18_l3c1` 0.608, `vgg16_fc2` 0.546, `gpt2_l11_down_maxabs` 0.338, against (a)'s 0.512, 0.383, 0.164 and the gate law's 0.834, 0.683, 0.400. The cells keep the registered c.

Three files were added after the pre-registration and decide nothing: [`checks.py`](checks.py), [`checks.txt`](checks.txt), and the cut of the box's history, [`history.jsonl.gz`](history.jsonl.gz). [`tables_e96.py`](../../../../tools/claims-v3/kspeed/e96/tables_e96.py) was already in the pre-registration. The reduction ran on the mini (arm64, Python 3.12.15) because the Intel was overloaded; a second run there gave `results.json`, `reduce.txt`, `tables.md` and `cells.json` byte for byte the same.

## What it closes, narrows and leaves open

**Item 3 of the kinds page's section 11, the speed half.**
- **Closed for speed:** a layer with exact zeros (ResNet-18, VGG-16, T5-small); more layers and models (GPT-2 layers 3 and 9, BERT, ViT); several sustained runs per kind for real int8, on one night.
- **Burst only, no sustained run:** other int8 calibrations and the fp16 forward pass.
- **Open:** the energy half (E95); real int8 beyond GPT-2's three tiles and on a warmer heat path; whether fp16's +1% is real.

It also feeds item 4 (a real −0.0 tile: the gate stays open, on c), item 6 (the gate law beats the predictor on gated float c on this card; E95 scores it), item 9 (one line reading at a known rest; E98 is the test) and item 10 (one idle-reset dip in 368 work processes, against about 2% in E80 and E87, and launch ramps that come by the run).

**For the blog**, each sentence standing on the file named:

- Tiles cut from ReLU networks, on which the zero gate closes 37–95% of the lanes, ran every 6 s burst at the card's 800 MHz cap, 77–96 MHz above random numbers in the same session (`results.json` `rules.E96-S2`).
- Held for 76 s they sustained 75–194 MHz above random numbers, and the more lanes the gate closes the higher the clock: 677–690 MHz at 37–45%, 745–784 MHz at 55–72%, 795 MHz at 87–95% (`rules.E96-S2b`).
- The clock follows the measured power: a power-to-clock relation fixed on synthetic data gives those seven tiles' clocks to 5 MHz rms in the burst and 12 MHz sustained, where "real = random" misses by 82 and 141 MHz (`posthoc.rms_by_group`).
- GPT-2, BERT and ViT tensors with no exact zeros burst within 15 MHz of random numbers: 3 MHz below in fp32, 10 MHz above in fp16 (`rules.E96-S3`).
- Having no zero word does not make a tensor run like random numbers. T5-small's weights, on a bf16 grid, burst 21 MHz faster, and ViT's last block, 64% negative zero, 36 MHz faster, because fewer bits move (`posthoc.diff_from_random_rows`).
- Negative zero does not close the gate, on this real tile: its switching term reads 21.4 W, where a gate that took it would give 10.6 W (`checks.txt` K9).
- In four paired rounds, three real GPT-2 tiles in int8 sustained 6 MHz above uniform random int8, 95% from 1 below to 13 above, under the 15 MHz that would count. They drew 2.2 W less and ran 0.85 °C cooler. One of four random runs tripped the 65 °C limit and none of twelve real runs did (`rules.E96-I1`, `I2`, `I3`, `posthoc.arm_labelled.limits`).
- Changing one GPT-2 layer's int8 calibration from max-abs to a 99.9th percentile clip adds 5.8 W at 800 MHz and leaves the burst at 800 MHz either way (`checks.txt` K9).

## Card state

aifoundry2 card 0 was left free at 03:15:20 PST (11:15:20 UTC), after a read-only `ettelem config` under the card lock (low_power, 600 MHz, 519 mV, TDP 65 W, threshold 65 °C; [`config-end.txt`](config-end.txt), `snapshot-end.json`). The claim stays E98's lane's to release. The run directories `build/e96/runs/{smoke,s1}` remain on the box.

## Files

| file | what |
|---|---|
| `s1/`, `smoke/` | the raw sessions as the runner wrote them (telemetry and launches gzipped): `session.json`, `kspeed.json`, `e96.json`, `runs.jsonl`, `queries.jsonl`, `marks.jsonl`, `tel/`, `sp/`, `manifest.txt`, `run.log` |
| `queue.jsonl`, `queue.out`, `status.json`, `s1.out`, `smoke.out` | the detached queue's records and the sessions' printed lines. The queue passed absolute paths; in the committed `queue.jsonl`, `queue.out` and the two sessions' `session.json` and `e96.json`, the checkout's path is made relative, and nothing else was changed. Nothing here carries another user's login |
| `snapshot-{start,end}.json`, `sensors-{start,end}.json`, `config-{start,end}.txt` | the box before the first launch and after the last |
| `history-before.jsonl.gz`, `history.jsonl.gz` | the box's own 5 s history: the 40 min the queue copied before the first launch, and 08:48:20–11:41:40 UTC, cut afterwards; card and host readings only |
| `results.json`, `reduce.txt` | the registered reduction's output |
| `tables.md`, `cells.json` | the tables and the blog's cells (formatting only) |
| `checks.py`, `checks.txt` | post-hoc checks K1–K9, labelled |

Reproduce from the top of the repository:

```bash
D=docs/reports/data/2026-11-01-e96-real-tensors-speed
python3 tools/claims-v3/kspeed/e96/reduce_e96.py $D/s1 --smoke $D/smoke --history $D/history.jsonl.gz --rest-at first_launch=1793527500058 p2=1793525400054 p3=1793533200051 --out /tmp/results.json > /tmp/reduce.txt
python3 tools/claims-v3/kspeed/e96/tables_e96.py $D/results.json --cells /tmp/cells.json > /tmp/tables.md
python3 $D/checks.py > /tmp/checks.txt
```
