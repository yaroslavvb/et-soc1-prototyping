# E96 data: the speed of more real tensors under aifoundry2's own governor, and whether real int8 sustains differently (Q132, Sun 1 Nov 2026)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "More real tensors" (old item 3), its speed half.*

Q132(r)'s 25 tier-1 real tiles, cut from six public models ([`tools/claims-v3/kinds/real2/`](../../../../tools/claims-v3/kinds/real2/README.md)), on aifoundry2 card 0 under the card's own governor. E87's six anchors ran again in the same session, and E87's three real int8 tiles ran against int8 full in four paired rounds. Every new tile and anchor got a **burst on a cool die**, run twice. Eleven new tiles and the anchors got a **sustained run** of about 76 s. **Nothing was set on the card**: the TDP and the threshold read 65 W and 65 °C at all 100 per-run reads of `ettelem config`, at the sessions' start and end queries, and at the queue's reads under the card lock at both ends of the card time. The sampler ran without `--reset-ms`.

The pre-registration is [`tools/claims-v3/kspeed/e96/`](../../../../tools/claims-v3/kspeed/e96/README.md) (`0c187e12`, pushed 01:13:09 PDT, 1 h 52 min before this lane's first read of the card and 1 h 53 min before its first launch; clocks went back at 02:00 PDT that night). Its frozen predictions are [`predictions.json`](../../../../tools/claims-v3/kspeed/e96/predictions.json), sha256 `fd01c532…`: `claims.E96` of Q132(r)'s `predictions-real2.json` (sha256 `0957e0c2…`) verbatim, the anchors' tie cells, and the arm's rule. The card was under E98's lane's one claim for the night, `#community-lab` message `1566355908076765257`, posted 00:39 PDT, 34 min before this registration: the brief asks for registration first, the claim is another lane's, and nothing of E96 touched the card under it until E96 was registered. E96 made no post and no release. **No amendment and no departure from the registered design.** This lane read nothing of the session while it ran; the reduction first ran on the complete session, after the slot's end. An independent verifier recomputed every run and rule from the raw telemetry with its own code and reproduced every derived file byte for byte; the text it found wrong is corrected in place, listed at the end (Corrections after verification), and no number or verdict changed.

| session | PST (UTC) | what |
|---|---|---|
| `smoke/` | 02:05:00–02:06:38 (10:05–10:06) | 75 s of the idle card with no launch (the rest reading), then three 2 s launches of real2 tiles, one at each gating level: 546.0 / 546.0 / 318.0 cycles per op, config 65 W / 65 °C; checked by the queue, not analysed |
| `s1/` | 02:06:38–03:15:20 (10:06–11:15) | the registered session, 96 of 96 runs, exit 0, **68.7 card-minutes** (70.3 with the smoke): `BURST` 62 runs (02:06:39–02:20:39), `SUS` 34 runs (02:20:44–03:15:14). The card was free 279 s before the slot's end |

## Results first

### 1. Every registered rule passes. Near the cap, real int8 shows no difference that counts

[`results.json`](results.json) `rules`, [`reduce.txt`](reduce.txt). Rules S1–S5 are `claims.E96`, scored as frozen; T and I1–I3 are this lane's own, frozen in the pre-registration. The sustained halves of S1 and S5, and S4, hold the 11 float tiles that ran sustained: `sustained_first`'s last four, all int8, were cut before the data, as the pre-registration says.

| rule | verdict | what the data say |
|---|---|---|
| **E96-S1** E83's relation fed (a) holds the clocks | **PASS** | bursts **25 of 25** inside their scoring intervals, sustained **10 of 11**. The miss is fp32 `t5small_l0_down`, 795.4 MHz against the single point 800: limit `none`, die 59.2 °C, 2.6% of the window in launch ramps ([`checks.txt`](checks.txt) K3). Inside the frozen D-propagated ranges: 24 of 25 and 9 of 11. "Real = random" puts 9 of 17 float tiles' bursts inside and 4 of 11 sustained ([`corrections-check.txt`](corrections-check.txt) C6), so this rule discriminates |
| **E96-S2** the gate buys burst clock | **PASS** | all six tiles read 800.0 MHz in both passes, **+96.1 MHz** in fp32 (randn 703.9) and **+77.3 MHz** in fp16 (randn 722.7): the cap minus randn's two cells, so two numbers, not six; the bar is +40 |
| **E96-S2b** and sustained clock | **PASS** | the smallest is fp32 `resnet18_l3c1`, **+75.4 MHz**; the largest fp32 `t5small_l0_down`, +193.6, which is the cap minus the floor; the bar is +50 |
| **E96-S3** no-zero real tiles burst at random's speed | **PASS** | fp32 **−3.4 MHz** (700.5 against 703.9), fp16 **+10.2 MHz** (732.9 against 722.7); the bar is ±15 |
| **E96-S4** the sustained limit called right | **PASS** | **10 of 11, a PASS that does not discriminate**: a constant `thermal` guess scores 9 of 11, 81.8%, also a PASS (C6). The miss is fp32 `vgg16_fc2`, `thermal` at 784.1 MHz against a predicted `none`: its c read 0.81 W above (a)'s. The relation on the measured c gives 784.0–786.1 by estimator, and one run is ±15.6 MHz, so that agreement is not precision |
| **E96-S5** the relation on measured c | **PASS** | burst **7.9 MHz** rms over 25, sustained **10.3 MHz** rms over 11; the bar is 15. Its input is this session's measured c, not the tile's bytes (§2) |
| **E96-T** the sessions tie | **PASS** | all twelve anchor rows within 25 MHz of the mean of E80's, E83's and E87's cells; the largest is fp32 randn's burst, −7.0 MHz. int8 full's sustained cell, 789.4, reads +4.5 |
| **E96-I1** real int8 against random int8, the clock | **`SAME_WITHIN_BAR`** | **+6.1 MHz, 95% [−0.8, +13.1]**, four whole rounds: it holds 0 and lies inside ±15. **Near the cap**: 15 of 16 runs read `none`, and on these runs the difference could not exceed +10.6 MHz (§4). The flag `at_the_cap` reads false by one run |
| **E96-I2** the board W | **`BELOW`** | **−2.18 W, 95% [−2.69, −1.68]**; expected at a fixed 800 MHz, −2.11 |
| **E96-I3** the die | **`BELOW`** | **−0.85 °C, 95% [−1.47, −0.23]**; −0.61 with each round's first run left out (§4); expected at a fixed 800 MHz, −0.96 |

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

- **Frozen from each tile's bytes, the predictions hold.** Over these seven tiles, rms MHz ([`corrections-check.txt`](corrections-check.txt) C2):

  | | burst | sustained | sustained, the five under 90% at 800 MHz |
  |---|---:|---:|---:|
  | frozen (a), from the tile's bytes | **5.41** | **17.65** (mean −10.3) | 20.66 |
  | frozen gate law, from the tile's bytes, no fit | **3.60** | **12.37** (mean −3.1) | 14.32 |
  | E83's relation, given the power measured in the same session | 4.75 | 11.61 (mean −3.3) | 13.39 |
  | "real = random" | 81.96 | 140.6 | 115.12 |

  A prediction frozen from the bytes alone beats "real = random" by 8× sustained, and the frozen gate law does as well as the relation fed measured power. The relation's row is not a clock from the data: its c comes from this session's bursts, the same two runs in the burst and other runs of the session sustained. Its burst figure is one tile: six of the seven sit at the cap, and `resnet18_l2c1`'s −12.5 MHz over √7 is 4.72.
- **The burst.** The six tiles whose (a) is under 15 W sit at the card's 800 MHz cap in all 12 passes, so the burst says they are below the power limit and cannot rank them. S2's +96.1 and +77.3 are two numbers, 800 minus randn. The one mid-power tile, `resnet18_l2c1`, lands between the cap and random data at 741.2 MHz.
- **Sustained, only five tiles rank, one run each** (C5). `t5small_l0_down` in both formats is cap-limited: 97% of the window at 800 MHz, limit `none`, die 59–62 °C, the deficit in launch ramps. So 795 MHz at 87–95% gated says nothing about 87 against 95. fp32 `vgg16_fc2` is near the cap, 84% at 800. fp16 `vgg16_fc2` (50%), both `resnet18_l3c1` (19–23%) and `resnet18_l2c1` (6%) are on the slope. The reference is at the floor: fp32 randn 98–99% of the window at 600 MHz, fp16 randn 87–96%, so +186 and +194 are the cap minus the floor.
- **Within a format, more gated lanes read a higher clock**: fp32 650, 677, 784 MHz at 19, 45, 72%; fp16 690, 745 MHz at 37, 55%. Across formats they do not: fp16 at 37% reads 689.5 above fp32 at 45%, 677.2, with c 15.15 and 15.29 W, inside one run's ±15.6 MHz.
- **The largest sustained misses against the relation are the two ResNet fp32 tiles, +19.9 and −19.9 MHz, one run each on the slope, and the first has a named cause** (C7). `resnet18_l2c1` ran straight after fp16 zeros (35.5 W), its gate held 0 s, and it launched from 54 °C where the other ten launched from 57. §5's carryover gives about −0.7 °C of line, about +14 MHz at its 8.8 MHz per W. On the five slope tiles the miss against the previous run's W reads r = −0.89 (post hoc, n = 5). The order was fixed and no rule moves.
- **The frozen sustained points read high on six of the seven**; `resnet18_l2c1`'s reads 18.3 MHz low. Q130(n)'s predictor reads these tiles' power low: the measured c lies above (a) on all seven, by 0.79 W on average, which explains about 13 of the 17.7 MHz in quadrature, and 11.6 remains with the measured c. **The gate law, stated separately in the freeze, lies nearer on six of the seven**: rms 0.25 W against 0.89 W, mean miss −0.01 W ([`checks.txt`](checks.txt) K4). On c from the 800 MHz power alone it is seven of seven, 0.23 W against 0.78 W (C8). This is c on this card, labelled. E95 holds the energy claims.

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
- **Clock against random.** At this session's burst noise, a cell's 6.9 MHz (E83's was 5.3), fp32's −3.4 MHz is −0.4 σ and fp16's +10.2 MHz is +1.3 σ for a three-tile mean minus one cell. E87 read +7.8 MHz for three other tiles, so the two sessions together read +9.0 ± 5.0 (1 σ), against +4.5 from the relation on the measured c. **Perhaps 1% in fp16, seen twice, still not established** (C9).
- **The sustained differences are floor readings.** BERT's −0.3 and ViT fp16's +3.2 MHz are single runs with 98% and 90% of the window at 600 MHz. T5's `l0_up` and ViT's last block read 98% and 86% there (C4). They say both sit at the floor, not that the two run alike.
- **These clock rules do not test the power predictor** on these tiles, as E87's correction C1 found: the no-model baseline scores 15.4 MHz in the burst and 7.1 sustained, against the relation's 11.8 and 7.5 (`posthoc.rms_by_group`). The shares: fp32 0.980–1.000, mean 0.993, t = 1.56 on 3 df against 1.000; fp16 0.956–0.995, mean 0.978, t = 1.88 on 2 df. **A little below random, not established here either.** E95 is the test of that.
- **Having no zero word does not settle it.** T5's `l0_up` has a full-mantissa A, and weights whose low 16 mantissa bits are all zero: it switches 0.889 of random (predicted 0.908) and bursts 21 MHz faster, on fewer moving bits. The ViT tile, 64.1% of its A words −0.0 (55% of the whole block's activations), has no zero word, because −0.0 is the word 0x80000000: **its c reads 21.40 W against 21.49 predicted if the gate is blind to −0.0, and 10.61 W if it were not**, so on this real tile the gate stays open. It still bursts 36 MHz faster, on fewer moving bits. "Fewer moving bits" is an inference from the stream statistic and c, not a measurement.
- **The fp16 forward pass** costs what rounding costs, within what this can see: c 22.95 W and share 0.994 here, 22.92 W and 0.990 for the rounded tile in E87's session. Its burst, 708.2 MHz (passes 718.4 and 698.0), is the one no-zero cell near its interval's low end, 704.8. E95's C11 is the test ([`checks.txt`](checks.txt) K9).
- **int8 calibrations have no speed reading here.** Every int8 burst sits at 800.0 MHz, int8 full and zeros included, so the burst separates nothing, and these tiles had no sustained run, the cut registered before the data. Whether a calibration moves a sustained clock is untested. Their power is read: from the 800 MHz power alone, GPT-2 layer 11's 99.9th percentile clip draws 5.84 W more than its max-abs scaling, and VGG's asymmetric activations 1.55 W more than its symmetric ones ([`checks.txt`](checks.txt) K2, K9).

### 4. int8: no difference that counts, near the cap, on a cool night

**The clock, sustained MHz, board W, die °C, limit**, by round, each round's runs back to back in a shuffled order ([`results.json`](results.json) `posthoc.arm_rounds_detail`, `rules.E96-I1`):

| round | int8 full | `l0_mlp_up` | `l6_mlp_down` | `l6_attn_qk` | mean(real) − full |
|---|---|---|---|---|---:|
| 1 | 791.6 / 52.66 / 64.7 / none | 800.0 / 51.94 / 64.4 / none | 800.0 / 49.90 / 62.8 / none | 793.9 / 49.59 / 63.5 / none | +6.4 |
| 2 | 793.4 / 53.19 / 64.9 / none | 789.7 / 51.51 / 64.9 / none | 800.0 / 50.87 / 64.5 / none | 800.0 / 50.39 / 64.2 / none | +3.2 |
| 3 | 777.2 / 51.65 / 65.0 / **thermal** | 789.3 / 51.30 / 64.6 / none | 789.7 / 49.77 / 64.1 / none | 789.2 / 48.59 / 62.7 / none | +12.2 |
| 4 | 795.4 / 53.32 / 64.9 / none | 794.4 / 51.57 / 64.5 / none | 800.0 / 50.41 / 63.8 / none | 800.0 / 50.41 / 64.3 / none | +2.7 |
| cell | 789.4 / 52.7 / 64.9 | 793.4 / 51.6 / 64.6 | 797.4 / 50.2 / 63.8 | 795.8 / 49.8 / 63.7 | **+6.1 [−0.8, +13.1]** |

- **The registered answer.** Real int8 sustains 6.1 MHz above random int8, 0.8%, with an interval that holds 0 and stops short of the 15 MHz that would count. The relation on E87's measured c expected +9.1 MHz (+8.2 on E87's c from the 800 MHz power, C8), or +10.1 at this session's heat path, which the interval holds ([`checks.txt`](checks.txt) K6).
- **It is a near-cap result** (C1). 15 of 16 runs read limit `none`, and 6 of the 12 real runs read exactly 800.0, with no sample below it. A real tile cannot pass 800, so each round's difference is bounded by 800 − F_r: 8.4, 6.6, 22.8, 4.6 MHz, **mean +10.6 MHz**. The measured +6.1 is 58% of that ceiling, the interval's top lies above it, and `DIFFERENT_BEYOND_BAR` was out of reach. One run's sd, 6.1 MHz pooled over the four kinds (8.3 for full, about 5.1 for each real tile), sits at E83's clamp class, 5.6: the pre-registration said `INCONCLUSIVE` was likely unless the card sat near the clamp, and it sat near the clamp.
- **What that verdict is worth.** The rule simulated at this night's spreads, with the clamp, returns `SAME_WITHIN_BAR` 49–81% of the time at a true 0, 31–59% at +6, 13–36% at +12 and 7–27% at an uncapped +21 (C1). So it is real evidence against a large gap and weak evidence against +6 to +12. **E87's single-run +21.3 MHz is neither reproduced nor refuted: this night's runs could not have shown it.**
- **Step-downs: 4 of 4 against 1 of 12** (C3). int8 full read 66 °C and stepped down in all four rounds, for 2.8–14.8% of the window, once enough to be labelled `thermal`. The real tiles did so in one run of twelve, `l0_mlp_up` in round 2, for 4.6%. Post hoc, that has a hypergeometric p of 0.0027, where the labels' 1 of 4 against 0 of 12 has 0.25. The whole int8 row sat at 63–65 °C.
- **Real int8 draws 2.0–2.2 W less and runs 0.6–0.85 °C cooler**, all intervals clear of 0 and all close to the fixed-clock expectations. int8 full was never first in a round, and a run that follows a low-power run reads cool, so the lower figures leave each round's first run out: +6.5 MHz [−0.4, +13.5], −1.98 W [−2.99, −0.96] and −0.61 °C [−0.79, −0.44] ([`checks.txt`](checks.txt) K6, K7).
- **Labelled, never a verdict.** Dips left out, +6.6 MHz [−0.4, +13.6]. The pooled two-way interval, which assumes one spread on and off the clamp, +6.1 MHz [+1.2, +11.0]. Each tile alone against full: `l0_mlp_up` +4.0 [−8.0, +15.9], `l6_mlp_down` +8.0 [+2.7, +13.4], `l6_attn_qk` +6.4 [−0.2, +13.0]. E98's fine W at 800 MHz, −2.13 W [−2.80, −1.45] (`posthoc.arm_labelled`).
- **Where the +6 MHz comes from, post hoc.** A run's samples below 800 MHz fall in two groups ([`checks.txt`](checks.txt) K6). **Launch ramps**, within 1.5 s of a process's start: a run has about 12–29 of them in its window or next to none, whatever the data (all four kinds in round 3), which fits Q132(g)'s heartbeat in the gap between kernels. **Later samples**: 102 of 1,599 for int8 full, 19 of 4,796 for the real tiles, the one idle-reset dip left out. That difference, 6.0 points of share, 95% [+0.1, +11.9], is at 100 MHz a step the arm's whole +6 MHz. So a small real difference looks likely: random int8 touches the trip more often. The registered verdict stands as scored.
- **What this covers.** Three tiles of one model, one card, one cool night near the cap, 02:20–03:07 PST. The heat path ran 0.5 °C cooler than E87's on shared kinds (§5). A warmer night puts the whole row further into the trip and lifts the ceiling, and there the relation expects a larger difference (+14.0 MHz at E87's W*). That stays open.

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

Everything ran as registered: 96 of 96 runs, including all of G3, the five sustained runs that ran only if the clock allowed. At 13.6 s a burst and 96.4 s a sustained run the session was a little under E87's rates. The plan was about 65 card-minutes; with G3 it took 70.3, and the card was free 279 s before the slot's end, 24.7 min before P3's rest reading. No cap was reached, no stop-file was touched and no SIGTERM was sent. No safety stop (peaks: die 67 °C, board 88.45 W; stops 85 °C and 97 W on three samples). Every launch rc 0, all 100 samplers started on attempt 1 and stopped with rc 0, every gate reached, 109.8 s held before bursts and 444.1 s before sustained runs ([`checks.txt`](checks.txt) K1). The box's tree was `0c187e12`; every file the session ran matched a desk machine's by sha256; the binaries are E87's (`7adadf4f…`, `990807f4…`, `77a46171…`). `kspeed.json`'s `git_dirty` lists another lane's untracked files, none of which this session ran.

**No login stopped or held this session.** The queue found the card free at the slot's start, 0.1 s late, with no wait. The runner's other-user check passed before all 368 work processes, and `marks.jsonl` holds no `other_user` mark.

**One expectation was wrong and one estimator caught us out; neither touches a rule.**
- The rest reading, §5.
- **E64's c is not fit for a tile that holds 800 MHz in a burst.** It fits all three clocks the burst touched, and such a tile has only one or two ramp samples at 700 MHz, whose reading can sit at 600's. int8 `vgg16_fc2`'s P700 read 36.96 and then 31.65 W, and its c 5.856 and then 4.756, while its P800 read 44.30 and 44.36 W. Three int8 tiles' like-with-like shares differ by 0.16–0.19 between passes for this reason (`vgg16_fc2`, `gpt2_l6_down_p9999`, `gpt2_l11_down_p999`; `checks.txt` K2 calls the passes rounds); every other tile's differ by at most 0.03. Six of the seven gated float tiles hold 800 too, with 0 or 1 samples in P700, and their c moves at most 0.30 W against the 800 MHz reading (C8). It moves no rule: S5 reads 6.85 and 10.39 MHz rms with c from the 800 MHz power alone, 7.86 and 10.29 from 600 and 800, against 7.90 and 10.29 registered. For int8 read the shares from the 800 MHz power ([`checks.txt`](checks.txt) K2): `resnet18_l3c1` 0.608, `vgg16_fc2` 0.546, `gpt2_l11_down_maxabs` 0.338, against (a)'s 0.512, 0.383, 0.164 and the gate law's 0.834, 0.683, 0.400. The cells keep the registered c.

Three files were added after the pre-registration and decide nothing: [`checks.py`](checks.py), [`checks.txt`](checks.txt), and the cut of the box's history, [`history.jsonl.gz`](history.jsonl.gz). [`tables_e96.py`](../../../../tools/claims-v3/kspeed/e96/tables_e96.py) was already in the pre-registration. The reduction ran on a desk machine (arm64, Python 3.12.15) because another was overloaded; a second run there gave `results.json`, `reduce.txt`, `tables.md` and `cells.json` byte for byte the same, and so did the verifier's run from a fresh `git archive` of `8072d31b`. Its own code on a desk machine (x86-64) recomputed all 96 runs and every rule from the raw telemetry with no difference.

## What it closes, narrows and leaves open

**Item 3 of the kinds page's section 11, the speed half: narrowed, not closed.**
- **Measured, one card, one night:** fp32 and fp16 tiles with exact zeros (ResNet-18, VGG-16, T5-small), burst and one sustained run each. More layers and models with no zero word (GPT-2 layers 3 and 9, BERT, ViT) in the burst. Four sustained runs per kind for three real int8 tiles against int8 full, near the cap.
- **Weak:** no-zero sustained, four single runs at or near the 600 MHz floor. fp16's +1%.
- **No speed reading:** other int8 calibrations and int8 tiles with zero words, because every int8 burst sits at the cap and they had no sustained run. The fp16 forward pass has one burst cell, no sustained run.
- **Open:** the energy half (E95); real int8 on a warmer heat path, where the ceiling lifts; real int8 beyond GPT-2's three tiles.

It also feeds item 4 (a real −0.0 tile: the gate stays open, on c), item 6 (the gate law beats the predictor on gated float c on this card; E95 scores it), item 9 (one line reading at a known rest; E98 is the test) and item 10 (one idle-reset dip in 368 work processes, against about 2% in E80 and E87, and launch ramps that come by the run).

**What the post may say**, each on aifoundry2 card 0, one night (`results.json`, `corrections-check.txt`):

- On aifoundry2 card 0, one night: gated ReLU-network tiles held the 800 MHz cap through a 6 s burst, where random fp32 and fp16 read 704 and 723 MHz (`rules.E96-S2`). *(Dated note, Sun 1 Nov 2026, from the kinds page's verifier: this line and the next are the six tiles gating 37–95%. The one gating 19%, fp32 `resnet18_l2c1`, read 741.2 and 650.1 MHz, §2's table.)*
- On aifoundry2 card 0, one night: held 76 s, they ran 677–795 MHz against random's 602 and 609, which sit at or near the 600 MHz floor; one run per tile, about ±16 MHz (`rules.E96-S2b`, C5).
- On aifoundry2 card 0, one night: predictions frozen from each tile's bytes landed to about 5 MHz rms in the burst, where six of seven simply sit at the cap, and about 18 MHz sustained, or about 12 with the gate law. Given the power measured in the same session, the relation also lands to about 12. "Real = random" misses by 82 and 141 MHz (C2).
- On aifoundry2 card 0, one night: GPT-2, BERT and ViT tiles with no exact zeros burst within 15 MHz of random numbers: −3.4 MHz in fp32, +10.2 in fp16 (`rules.E96-S3`).
- On aifoundry2 card 0, one night: a ViT tile with 64% of its A words −0.0 reads 21.4 W of switching, where a gate that took −0.0 would give 10.6 W (`checks.txt` K9).
- On aifoundry2 card 0, one night: three real GPT-2 tiles in int8 ran 2.0–2.2 W cheaper and 0.6–0.85 °C cooler than uniform random int8. On a cool night near the cap they sustained +6 MHz, 95% from −1 to +13, and could not have shown more than +11. They stepped down off the trip in 1 run of 12, random int8 in 4 of 4 (`rules.E96-I1`, `I2`, `I3`, C1, C3).

**What it may not say:**

- that real and random int8 run at the same speed in general or at the trip's edge, or that E87's +21 MHz is refuted: a warmer heat path is untested;
- that the relation predicts clocks from data alone at 5 and 12 MHz: its input is power measured in the same session;
- anything about int8 calibrations and speed: every int8 burst sits at the cap;
- "six models" at random data's speed: three;
- any ranking among the 87–95% tiles;
- that sustained no-zero tiles equal random, beyond "both at the floor";
- that item 3 is closed for speed;
- any claim beyond this card.

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
| `corrections-check.py`, `corrections-check.txt` | the desk check behind Corrections after verification: every number it quotes, from the committed files (standard library only) |

Reproduce from the top of the repository:

```bash
D=docs/reports/data/2026-11-01-e96-real-tensors-speed
python3 tools/claims-v3/kspeed/e96/reduce_e96.py $D/s1 --smoke $D/smoke --history $D/history.jsonl.gz --rest-at first_launch=1793527500058 p2=1793525400054 p3=1793533200051 --out /tmp/results.json > /tmp/reduce.txt
python3 tools/claims-v3/kspeed/e96/tables_e96.py $D/results.json --cells /tmp/cells.json > /tmp/tables.md
python3 $D/checks.py > /tmp/checks.txt
python3 $D/corrections-check.py > /tmp/corrections-check.txt
```

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E96 after the data commit (`8072d31b`). It read the scorer line by line, recomputed all 96 runs and every rule from the raw telemetry with its own code, with no difference, reproduced every derived file byte for byte from a fresh `git archive`, and found no lab user's login in any committed file, `.gz` and `.bin` included. It found the measurement, its timing and its safety sound, and one major and ten minor faults in what the prose says the numbers mean. Each is corrected above, desk only: no card was touched, nothing was re-run, and no frozen file, data file, registered number or verdict changed. Every number below is printed by [`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt), under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **Major: "It is not a clamp result" and "Not at the cap".** `at_the_cap` reads false by one run, round 3's int8 full. 15 of 16 runs read `none`, and 6 of the 12 real runs read exactly 800.0. A real tile cannot pass 800, so the difference is bounded at 8.4, 6.6, 22.8, 4.6 MHz by round, mean +10.6; the measured +6.1 is 58% of it, the interval's top lies above it, and `DIFFERENT_BEYOND_BAR` was out of reach. "E87's +21.3 MHz is not reproduced at that size" was unfair for the same reason | §1 and §4: a near-cap result, with the ceiling. The rule simulated with the clamp returns `SAME_WITHIN_BAR` 49–81% at a true 0, 31–59% at +6, 13–36% at +12, 7–27% at an uncapped +21: real evidence against a large gap, weak against +6 to +12. E87's +21.3 is neither reproduced nor refuted. The verdict and the flag stand as scored |
| C2 | **The relation's headline.** "Gives these seven tiles' clocks to 4.8 and 11.6 MHz" compared a relation fed this session's measured power with a no-input baseline, and the blog sentence said "fixed on synthetic data" without saying so. In the burst, c comes from the same two runs, and 4.75 is one tile | §2 leads with the rows frozen from the tile's bytes: (a) 5.41 and 17.65, the gate law 3.60 and 12.37. The relation's 4.75 and 11.61 always say "given the power measured in the same session" |
| C3 | **"One of four random runs tripped and none of twelve real runs did"** against §4's own text, and "0.85 °C cooler" with int8 full never first in a round | Step-downs, 4 of 4 against 1 of 12, post hoc p 0.0027 (the labels' 1 of 4 against 0 of 12: 0.25). The die reads 0.6–0.85 °C, the watts 2.0–2.2 |
| C4 | **"Closed for speed."** int8's zero-word and calibration tiles have bursts at the cap only; no-zero sustained is four single runs 86–98% at the floor; the warmer heat path was listed open in the same section. "So none of it moves the burst clock" was vacuous: every int8 burst sits at 800, int8 full and zeros included | "Narrowed", item by item. int8 calibrations have no speed reading |
| C5 | **Cap and floor not named.** 14 of 25 bursts sit at exactly 800. `t5small_l0_down` in both formats is cap-limited; fp32 randn is 98–99% at 600 MHz, fp16 randn 87–96%; BERT's −0.3 and ViT's +3.2 are floor readings. "The more lanes the gate closes the higher the clock" holds within a format: across formats fp16 at 37% reads 689.5 above fp32 at 45%, 677.2 | §2 and §3 name them. Only five tiles rank sustained, one run each; the 87–95% tiles rank nothing; +186 and +194 are the cap minus the floor |
| C6 | **S4's PASS was given with no baseline.** A constant `thermal` guess scores 9 of 11, 81.8%, also a PASS | §1 says so. S1 does discriminate: "real = random" puts 9 of 17 float bursts inside, 4 of 11 sustained |
| C7 | **The ±19.9 MHz misses had a named cause not stated.** `resnet18_l2c1` followed fp16 zeros (35.5 W), gate 0 s, launching from 54 °C against 57 | §2 states it: about −0.7 °C of line, about +14 MHz at 8.8 MHz per W; on the five slope tiles r = −0.89 against the previous run's W, post hoc, n = 5 |
| C8 | **Wording around c.** "Read high" holds on six of seven; "(a) reads their power low" explains about 13 of the 17.7 MHz in quadrature. The estimator warning named only int8, but six of the seven gated float tiles hold 800 too, with 0 or 1 samples in P700. S4's "784.0" read as precision | §2 and What was registered. It moves no rule: S5 reads 6.85 and 10.39 on c from the 800 MHz power, 7.86 and 10.29 from 600 and 800. Float c moves at most 0.30 W, the gate law's lead grows (7 of 7, 0.23 W against 0.78 W), and the arm's expected +9.1 becomes +8.2 |
| C9 | **"+1.7 σ"** used E83's 5.3 MHz a cell; this session's is 6.9 | fp16 +1.3 σ, fp32 −0.4 σ, the two sessions +9.0 ± 5.0. "Not established" stands |
| C10 | **The order against the claim was not stated.** The registration came 34 min after the shared claim, which is E98's lane's. The brief asks for registration first | The header says so: it precedes every E96 touch of the card by 1 h 52 min |
| C11 | **Small wording.** "Six tiles under 15 W": (a) is, two measured c are not. "Rounds" for burst passes. "ViT's last block, 64%": the tile is 64.1%, the block 55%. "Because fewer bits move": an inference | Reworded. `checks.txt` K2 keeps its label and the text names it |

All eleven were taken as written; none was rejected. Two of the verifier's small figures differ here by rounding of the estimator's inputs: S5's sustained rms on c800 and on c from 600 and 800 read 10.39 and 10.29 from the committed `p_ref58_w` (it read 10.40 and 10.31), and c800 moves at most 0.03 W pass to pass on these seven tiles (it read at most 0.12 W across its wider set). Nothing turns on either.
