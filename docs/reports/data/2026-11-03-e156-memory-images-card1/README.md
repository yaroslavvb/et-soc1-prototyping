# E156: E139's encoded memory term holds on a second card and on two new images - 0.03 W out of sample, and it is a 64-bit count (aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 10, the memory path**; it answers **rank 15 of Q138's final critic** ("E139's encoded term on another card and other images"; its rule: the
frozen price predicts each new image within 0.05 W). Tue 3 Nov 2026 (week 45), Q139, lane `a1c1-e156-memory-images`. Pre-registered in
**`d55744a5`** ([`tools/claims-v3/e156/README.md`](../../../../tools/claims-v3/e156/README.md), committed 05:46:30 PST and pushed by `commit_lab.sh`)
before the claim (05:47:41-05:47:55) and before any device opened (05:48:01). **aifoundry1 card 1** (`V3_DEVICE=1`, its own lock), release 1.4.0 (BL1
and BL2 0.22.0), 600 MHz in every one of 19,655 samples, 499 mV. `ettelem config` read under card 1's lock with `timeout 10`, through E128's allow-list,
at the session's start (05:48:01) and end (06:23:09): TDP 65 W, threshold 65 C, 600 MHz, 499 mV both times (power state `low_power`, then
`managed_power`, as E124, E128 and E155 saw), never set. **Every device-management command sent was a read** (nine kinds, two of them PMIC
voltage-register reads, which the owner's rule of 2 November 2026 allows; `since_reset_ms` −1 in every sample). **Card session 05:48:01-06:23:09
PST, 35.1 of the 40 card-minutes allowed**: the stop-path test 15602, the smoke 15601 and its gate, the warm-up 15610 and **nine headline passes,
15611-15619**, none set aside.*

**In plain words.** When the chip reads memory, the DRAM bus re-encodes some bytes (data-bus inversion) so that fewer wires switch. E139 found, on
another card, that those *encoded* changes cost power of their own, about 0.46 pJ for each encoded bit that changes between consecutive 64-bit
pieces of a memory line. E156 used that number, frozen, to predict two images it had never seen, on a card it had never been measured on. **Both
predictions held: the new 64-bit image read +0.117 W against a predicted +0.152 W, and the new 32-bit image read −0.030 W against a predicted 0
(N1 PASS, errors −0.035 and −0.030 W against the critic's ±0.05 W).** E139's own two images read +0.199 and +0.169 W on this card against +0.213 W
(C1 PASS). The 32-bit image also answers *which* width the cost lives at: its encoded bytes change 420 more times a line at 32 bits than its twin's
and not once at 64 bits, and it costs nothing beyond its pins, so the cost follows the 64-bit count, not the 32-bit one, the pins or the line edge (**N2: A ONLY**).

## Results

Nine headline passes, all kept on the registered primary (the board meter's dips removed, leakage `auto`; [`e156.json`](e156.json)). The session's
line rate was 1.17259 × 10⁹ lines a second (E139's 1.17294 × 10⁹), so every prediction is E139's price × count × 1.17259 × 10⁹.

**1. N1, the critic's rule on the two new images** (`e156.json` › `verdicts.N1_new_images`):

| pair | what it is | encoded 64-bit toggles a line | predicted (A) | measured, 95% | error | verdict |
|---|---|---:|---:|---:|---:|---|
| **`E7`** = `e7_64` − `e2_64` | new bytes (0x07/0x1F against 0x0F/0x1E), 64-bit blocks | +280 | +0.152 W | **+0.117 [0.036, 0.199]** | **−0.035** | **PASS** |
| **`E32`** = `eh_32` − `el_32` | E56's bytes, 32-bit blocks | 0 (+420 at 32 bits) | 0.000 W | **−0.030 [−0.101, +0.041]** | **−0.030** | **PASS** |

**N1 PASS.** Each interval contains its prediction and straddles the prediction ± 0.05 W, so the pass rests on the point errors, as the critic's rule
is written; at nine passes the half-widths are 0.08 and 0.07 W.

**2. C1, E139's own images on this card** (`verdicts.C1_card_transfer`): `E56` **+0.199 W [0.153, 0.246]**, error −0.013; `E448` **+0.169 W
[0.080, 0.257]**, error −0.044; both against +0.213 W: **PASS**. E132's R4 class reading on this card: **PAYS** (both present). Against E132's frozen
+0.185 W: +0.014 and −0.016 W.

**3. N2, the width, inside the session** (`verdicts.N2_width`; d_X = the pair − k_X × this card's mean of `E56` and `E448`, consistent when its
interval holds 0):

| reading (each fitted to E56 and E448) | k on `E32` | d on `E32`, W | k on `E192` | d on `E192`, W | consistent on both |
|---|---:|---|---:|---|---|
| **A, per encoded 64-bit toggle (E139's)** | 0 | −0.030 [−0.101, +0.041] | 0.429 | +0.041 [−0.042, +0.124] | **yes** |
| B, per encoded 32-bit toggle | 2.143 | −0.425 [−0.542, −0.307] | 0.429 | +0.041 [−0.042, +0.124] | no |
| C, 64-bit plus 128-bit toggles | 0 | −0.030 [−0.101, +0.041] | 1.286 | −0.117 [−0.198, −0.035] | no |
| E, the pins mispriced | 2.143 | −0.425 [−0.542, −0.307] | 0.429 | +0.041 [−0.042, +0.124] | no |
| F, the line edge | 1.000 | −0.214 [−0.295, −0.133] | 1.000 | −0.064 [−0.144, +0.016] | no |

**N2: A ONLY.** `E32` alone rules out B, E and F; `E192` (+0.120 W [0.029, 0.211], 128-bit blocks) rules out C. My frozen expectation was
`SEVERAL: A,C`: `E192` separated C, which I expected it could not at this precision. `E7`'s d is −0.014 [−0.101, +0.072] W in every reading (k = 5/7).

**4. D: read DBI evident on this card** (`verdicts.D_dbi_evident`): `Hp` +0.397 W [0.326, 0.468] present: **EVIDENT**.

**At every arm** (leakage 0.2936, 0.3803 and Q139(u)'s card-1 slope 0.3134 W/C: `e156-leak*.json`) every verdict and every number above is
unchanged to the third decimal (launches at 58 C within 0.5 C and equal windows make the within-pass contrasts nearly blind to the slope). **With the
board meter's dips kept** (`e156-unfiltered.json`) the verdicts move: N1 FAIL (`E7` +0.130 [−0.141, +0.400], `E32` +0.075 [−0.143, +0.292]), C1
FAIL (`E56` +0.361, `E448` +0.084), N2 `SEVERAL: A,C,F`, R4 UNRESOLVED. On this card 17 dip samples fell inside run windows over the nine headline
passes ([`dips.json`](dips.json)); the registered primary removes them by E82 A2's rule, which was defined on this card, as E139's primary did.

**5. Reported, not scored.** *The ties against aifoundry3* (`verdicts.ties_vs_E139`, card 1 minus E139): `U4z` +0.002, `V64` +0.020, `S128` +0.005,
`V128` +0.031 W, but the pin prices are higher on this card: `V16` +0.540 W against 0.458 (+0.082), `Hp` +0.397 against 0.308 (+0.089), `S64` +0.074.
*The DDR die rail* (`verdicts.ddr_die_rail`; whole millivolts): `RE64` −0.99 mV, `RE448` −0.98, `RE128` −0.88 and `RE7` −0.98 *move*, `RE32` −0.19
[−0.35, −0.03] does not reach the −0.30 mV line, and the pins held high are *still* (`RH64` +0.01, `RH128` −0.01): the encoded 64-bit toggles move the
memory shire's die supply on this card too, and the 32-bit image's do not. Over zeros the rail steps by whole millivolts: −3.0 mV for `vl_64` (896
raw plus encoded 64-bit toggles a line), −2.0 for `wl_64`, `c3_64`, `eh_64` and `e7_64` (504 each) and −1.9 for `vl_128` (384), −1.0 for `el_64`,
`e2_64`, `wl_128` and `c3_128` (112-224) and also for the two images whose beats toggle but whose 64-bit pieces do not (`dm_a44`, `eh_32`), −0.8 for
`el_32`, −0.5 and −0.2 for the constant images `dm_u4` and `dm_l08`. Unlike aifoundry3, `el_64z` moves here (−0.98 mV), so E132's R3 logic (its raw
control `el_64z` still) would read OTHER on this card. *Where it is paid*
(`verdicts.where`): `E56`, `E7` and `E32` sit off every metered rail (rails' sum −0.031, +0.001, −0.045 W). The warm-up pass 15610 read `E7` +0.137
and `E32` −0.066 W.

## What it does to predicting power and heat

**The term tested:** the memory path's encoded term, E139's **0.4630 pJ per encoded 64-bit toggle** × the image's count × the line rate, frozen
before the run, on a second card and on two images no model had seen. **Out-of-sample error** ([`posthoc/posthoc.txt`](posthoc/posthoc.txt) §1,
post hoc arithmetic on the registered numbers):

| | the two new pairs, rms | E56, E448, E7, E32, rms | all five with E192, rms |
|---|---:|---:|---:|
| the model without an encoded term (every residual predicted 0) | 0.086 W | 0.144 W | 0.140 W |
| **with E139's frozen term (reading A)** | **0.033 W** | **0.033 W** | **0.032 W** |
| reading B or E instead (the 32-bit count, or the pins) | | | 0.219 W (`E32` off by −0.486) |
| reading F instead (the line edge) | | | 0.119 W (`E32` off by −0.243) |
| reading C instead (the 128-bit toggles counted too) | | | 0.075 W (`E192` off by −0.153) |

So the term carries to a second card and to new bytes, counts and raw levels with an error of about 0.03 W, a quarter of what is left without it,
and its count is settled: **count the encoded toggles between consecutive 64-bit pieces of a line**, not at 32 bits (which would mispredict a
32-bit-structured image by about 0.5 W) and not at 128 bits. For random data the 64-bit and 32-bit counts are nearly equal (56 and 60 byte edges a
line), so the wrong width would have doubled the term on every random tensor. **On this card the price itself** reads 0.389 pJ [0.286, 0.493] when
fitted per pass on `E56`, `E448` and `E7` together (post hoc, §2), against aifoundry3's 0.463 [0.323, 0.603]: a card ratio of 0.84, inside both
intervals, so no card term is resolved for the encoded part, while the pins' prices (`V16`, `Hp`) read 18-29% higher here. **Heat:** the term enters
only through board power; at card 1's 0.1151 C per board W (M7's H2) the whole encoded part of these images (0.1-0.2 W) is 0.01-0.02 C and the
remaining 0.03 W error 0.004 C, below what the 4.5 s readout resolves. No heat term was measured or changed.

## Registered against what happened

| | registered (`d55744a5`) | happened |
|---|---|---|
| passes | stop test 15602, smoke 15601, warm-up 15610, headline 15611 onward as the budget allows (projected about seven) | all three, warm-up and **nine** headline passes (15611-15619): passes took 184-193 s, not the 330 s first estimate, so the queue's rule (start only if it ends by T0 + 2,250 s) let all ten run; the last ended at T0 + 2,108 s |
| card time | ≤ 40 min from the first config read to the last | 35.1 min |
| stops | live samples: board 66 W, any minion-shire field 72 C, a line 1.5 s old; runitems' cap 70 C on the shire mean | board max 59.55 W, the hottest field 65 C (its latched value), the mean 61 C, the largest sample gap 101 ms (`posthoc.txt` §3); no stop fired |
| stop-path test | die at 1.0 C, board at 1.0 W, watcher at 1.0 W, stale at 0.0 s, each exit 6 with a STOP line from a live sample | **PASS**: all four exit 6, each STOP line read 0.04-0.07 s after its sample was taken ([`passes/p15602/`](passes/p15602/) `STOP.*`, `logs/session.log`) |
| smoke gate | E110's | PASS: 60 launch records, 984 telemetry samples |
| condition (the form check) | config and telemetry in E155's form | TDP 65 W, 65 C, 600 MHz, 499 mV at both ends; `since_reset_ms` −1 in all 19,655 samples; one clock |
| expectation | C1 PASS, D EVIDENT, `E7` near +0.15, `E32` near 0, N1 PASS, N2 `SEVERAL: A,C` | C1, D, N1 as expected; `E7` +0.117; N2 `A ONLY` |
| departures | — | **D1**: nine headline passes, two more than projected, as the queue's registered rule allowed. **D2**: the release script's read-back reported "not confirmed" (exit 18) because the channel listing's source text lagged the save; the post's own edit box, read by a dry run at 06:24:43, holds the released text (§ Card and post). No departure touches the design, a rule, a prediction or the reduction |

## Device commands sent

As registered (the registration's § Device commands sent): `ettelem config` at the session's start and end and `ettelem sample` through every
block, all through E128's allow-list `ettelem_guard.sh`; all nine command kinds are READs (`GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`,
`GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`, `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`,
`GET_MODULE_VOLTAGE`), two of them PMIC voltage-register reads, classified at et-platform `836a4ab` (BL2 0.22.0). The checker on the box at the
session's start: **GO, 32 send sites, 0 disallowed** ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)). The host programs (E99's
`enercat_host` built on this box, `e2463274…`; the heater and anchor `sparsity_host`, `e0fbecce…`; [`logs/binaries.sha256`](logs/binaries.sha256))
open the ops node only. **Never sent:** the statistics reset (`since_reset_ms` −1 in every sample), `dev_mngt_service` (refused in `block_e156.sh`),
any `SET_*`, the firmware-revisions query, a residency read; no governor, TDP, threshold or clock set, no reset, no power cycle.

## Card and post

`et-who` at the session's start and end, and at the claim and the release: no process held a device node or card lock. The card was claimed by
rewriting Tue 3 Nov's one card post in `#community-lab` (message `1567153765390487573`) under the discord lock with `EXPECT_TEXT` (dry run, save,
read back), 05:47:41-05:47:55 PST, from "using aifoundry2 for 1 h, until ~06:33 PST [doc](…); using aifoundry3 for 1 h, until ~06:46 PST [doc](…)" to
that text plus "; using aifoundry1 card 1 for 1 h, until ~06:47 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)". It was
released at 06:23:25-06:23:48: the listing still named aifoundry3, so `EXPECT_TEXT` refused (exit 7); the edit box held only this card's clause
(the other lanes had dropped theirs), so " — released" was appended and saved: "<ai> **Claude says:** using aifoundry1 card 1 for 1 h, until ~06:47
PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released", read back from the edit box at 06:24:43. Mon 2 Nov's post
`1566837317765963987` was not touched.

## What it changes

- **Item 10 (the memory path)**: the encoded part's term is no longer one card's fit. It carries to aifoundry1 card 1 and to two new images within
  0.04 W each, and its count is settled as the encoded toggles between consecutive 64-bit pieces of a line (N2 A ONLY). Still open on item 10: the
  1.0 pJ split between the memory shires' logic, the PHY and the DRAM, and where the 256-bit path is (no meter reaches them).
- **Rank 15 of Q138's final critic**: answered as the critic wrote it (the rule passes on both new images), and the width question it did not ask is
  answered too.
- **The power model**: keep E139's term as frozen (0.463 pJ an encoded 64-bit toggle); count it at 64 bits; no card term on it is resolved (card 1
  0.389 [0.286, 0.493] pJ, post hoc). The pins' prices differ between the cards by about a fifth.

## Files

`README.md` (this), `e156.json` (the registered primary), `runs.csv`, `e156-leak0.2936.json`, `e156-leak0.3803.json`, `e156-leak0.3134.json`, `e156-unfiltered.json`
(dips kept), `dips.json`, `gen/` (the images, `counts.json`, `gen.sha256`, committed with the registration), `passes/p156*` (raw: per-run records,
telemetry, block.json, binaries; `p15601` the smoke, `p15602` the stop-path test with its four STOP lines), `logs/` (session log, queue, smoke, the
two config reads, the preflight, binaries), `posthoc/posthoc_e156.py` and `posthoc.txt` (post hoc, labelled: the before/after errors, the one-price
fit, the session's peaks).
