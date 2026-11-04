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

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 16:20-17:10 PST; desk only: no card, no device command, nothing re-run on
a box). An independent verifier re-derived what this README reports and found the registered verdicts sound: N1 PASS, C1 PASS, N2 A ONLY, D
EVIDENT, no WRITE sent. It re-ran the registered reduction bit for bit, ran an independent estimator (equal to 4 decimals) and recounted every
pair from the images' bytes. It found one major fault in the files and six minor ones in what this README draws from them. None changes a
measured, frozen or registered number, prediction or verdict. Each is corrected by a dated note beside the text it concerns, the text itself
left as it was, and set out in full in [§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The
numbers are printed by [`posthoc/corrections_e156.py`](posthoc/corrections_e156.py) → [`posthoc/corrections.txt`](posthoc/corrections.txt)
([`posthoc/corrections.json`](posthoc/corrections.json)), labelled post hoc.*
- ***C1 (major):*** *four committed JSONs recorded their input directories as absolute paths on the desk machine. Their `dirs` now read
  `build/e156-dipwork/p156xx`, as the registered `reduce_e156.sh` writes them with its default work dir. No number changed.*
- ***C4:*** *N1 applies the critic's 0.05 W line to the frozen term per image (E139's price × each image's count, registered before any
  pass), not to a fixed "+0.185 W per image" as the critic's rule is written. Read literally, both new images fail (−0.068 and −0.215 W). The
  header's "the frozen price predicts each new image within 0.05 W" paraphrases the rule that way.*
- ***C3:*** *the count is not settled at 128 bits. The 32-bit count and the pins are excluded at every arm, and the line edge on the primary.
  The 128-bit addition is excluded only on this card's primary, by one pair in one session. So 64 bits is the reading on present evidence, and 64 + 128 bits is not yet excluded
  across cards.*
- ***C2:*** *the pins' prices read 18-29% higher here, but the difference is not resolved.*
- *C5-C7 and one post hoc observation (O1) are in the section.*

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

*(Dated note, Tue 3 Nov 2026, after verification, C4.)* N1 is the critic's 0.05 W line applied to **the frozen term per image**: E139's
0.4630 pJ × each image's encoded 64-bit count × the session's line rate, +0.152 W for `E7` and 0 for `E32`, as `d55744a5` registered before
any pass. The critic's rule as written says "the frozen +0.185 W per image": E132's frozen value, for E139's 392-toggle images. Read that
way, **the new images miss by −0.068 W (`E7`) and −0.215 W (`E32`): FAIL**. E139's own images pass it on this card (+0.014 and −0.016 W, §2).
The registered reading is the physically meaningful one: `E32` is built to carry no encoded 64-bit toggle, so one fixed value per image cannot
fit both it and E139's images. But it is a reading of the rule, not the rule as written ([`posthoc/corrections.txt`](posthoc/corrections.txt) C4).

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

*(Dated note, Tue 3 Nov 2026, after verification, C3.)* `A ONLY` is the registered verdict on this card's primary, and it holds at the three
leakage arms. The readings it excludes are not excluded equally (post hoc, [`posthoc/corrections.txt`](posthoc/corrections.txt) C3):
- **the 32-bit count and the pins (B, E):** excluded by `E32` on every arm, the dips kept included (−0.401 [−0.747, −0.056] W there);
- **the line edge (F):** excluded by `E32` on the primary and at the leakage arms, but not with the dips kept (−0.147 [−0.387, +0.092]);
- **the 128-bit addition (C):** excluded by one pair, `E192`, on the primary and at the leakage arms (−0.117 [−0.198, −0.035]), but not with
  the dips kept (−0.108 [−0.382, +0.166]). On aifoundry3's E139 passes it is consistent on E139's primary (−0.094 [−0.264, +0.076]),
  excluded at E139's 0.2936 W/C arm (−0.210 [−0.386, −0.034]) and only just consistent at its 0.3803 arm (−0.246 [−0.493, +0.002]).

So 64 bits is the reading on present evidence; 64 + 128 bits is not yet excluded across cards. The difference matters for prediction. On a
random line, C adds the encoded 128-bit toggles (about 200 a line) to the 64-bit ones (about 233): 1.86 times the term, about +0.11 W at this
session's full read rate (reading A 0.127 W, reading C 0.235 W).

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

*(Dated note, Tue 3 Nov 2026, after verification, C2.)* "The pin prices are higher on this card" overstates. They **read 18-29% higher on
card 1 (`V16` 1.18 times, `Hp` 1.29 times), not resolved**. Card 1 minus aifoundry3, Welch over the two sessions' headline passes (nine and
eight): `V16` +0.082 [−0.021, +0.184] W (p 0.10), `Hp` +0.089 [−0.006, +0.183] W (p 0.06), `S64` +0.074 [−0.042, +0.190] W (p 0.19). No tie's
card difference is resolved at 95% ([`posthoc/corrections.txt`](posthoc/corrections.txt) C2), and there is one session per card.

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

*(Dated note, Tue 3 Nov 2026, after verification, C2 and C3.)* Two readings here go further than the data.
- **(a) "Its count is settled … not at 128 bits."** The 32-bit count and the pins are excluded, and so is the line edge on the primary. The
  128-bit addition is excluded only on this card's primary, by one pair in one session: not with the dips kept, and not on aifoundry3's
  primary (the note to §3). So count the encoded toggles between consecutive 64-bit pieces on present evidence. Whether 128-bit toggles add
  to them is open across cards; on random data they would make the term 1.86 times as large, about +0.11 W at full read rate. The table's
  "reading C instead" row (0.075 W) is card 1's primary.
- **(b) "The pins' prices (`V16`, `Hp`) read 18-29% higher here."** Not resolved (the note to §5). No card term on the pins or the raw path
  is justified yet.

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

*(Dated note, Tue 3 Nov 2026, after verification, C6 and C7.)*
- **D1 (C7):** the registration projected about seven passes, the warm-up and six headline (`tools/claims-v3/e156/README.md`, its item 5,
  Budget and gates). Nine headline passes ran: **three more than projected**, not two.
- **The stops row (C6):** no telemetry field reads the PMIC's own temperature, which its 75 °C over-temperature alarm compares, so the margin
  to that alarm was not measured. The guard against over-temperature was the registered 72 °C die stop; the hottest-shire latch read 65 °C.
  E142's corrected README (its C3) says the same for this card. This session ran cooler and lower than E142 did on card 1: board 59.55 W and
  shire mean 61 °C here, against 62.09 W and 63 °C there, with no alarm.

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

*(Dated note, Tue 3 Nov 2026, after verification, C7.)* Three `et-who` reads are on record:
- one just before the claim, at 05:47:34 (the lane's claim log, not committed);
- the session's start and end, at 05:48:01 and 06:23:09 ([`logs/session.log`](logs/session.log) lines 4 and 26).

The release (06:23:25-06:23:48) ran no `et-who` of its own, so its last read is the session end's, 16 s before it. The lane's result named an
`et-who` at 06:23:24, which no log holds. After the release, E160's claim rewrote the same post at 06:41. The post has since gone from the
channel, and no clause of E156's is held anywhere.

## What it changes

- **Item 10 (the memory path)**: the encoded part's term is no longer one card's fit. It carries to aifoundry1 card 1 and to two new images within
  0.04 W each, and its count is settled as the encoded toggles between consecutive 64-bit pieces of a line (N2 A ONLY). Still open on item 10: the
  1.0 pJ split between the memory shires' logic, the PHY and the DRAM, and where the 256-bit path is (no meter reaches them).
- **Rank 15 of Q138's final critic**: answered as the critic wrote it (the rule passes on both new images), and the width question it did not ask is
  answered too.
- **The power model**: keep E139's term as frozen (0.463 pJ an encoded 64-bit toggle); count it at 64 bits; no card term on it is resolved (card 1
  0.389 [0.286, 0.493] pJ, post hoc). The pins' prices differ between the cards by about a fifth.

*(Dated note, Tue 3 Nov 2026, after verification, C2-C5.)* Read the three bullets with these corrections.
- **Item 10.** The encoded term carries to card 1: the two new images within 0.035 W each (N1), E139's own within 0.044 W (C1). Its count
  is the 64-bit one on present evidence. The 32-bit count, the pins and the line edge are excluded on this card's primary; the 128-bit addition is excluded only there, by
  one pair in one session, so 64 + 128 bits is not yet excluded across cards (C3). Still open on item 10:
  - the 1.0 pJ split between the memory shires' logic, the PHY and the DRAM;
  - where the 256-bit path is;
  - whether the 128-bit toggles add (a second card's `E192`, or an image built for it);
  - **a refit of E99's account with the encoded term** (C5). The kinds page's item 10 lists it, and E156 does not answer it.
- **Rank 15.** The rule passes on both new images with the critic's 0.05 W line applied to the frozen term per image (price × count,
  registered before the run). That is not "as the critic wrote it". Read literally, "+0.185 W per image" fails both new images (−0.068 and
  −0.215 W) and passes E139's (C4).
- **The power model.** Keep E139's term as frozen and count it at 64 bits, with the 128-bit addition open. No card term on it is resolved.
  The pins' prices read 18-29% higher on card 1, not resolved (the intervals of the difference include 0; one session per card), so they do
  not yet justify a card term (C2).

## Files

`README.md` (this), `e156.json` (the registered primary), `runs.csv`, `e156-leak0.2936.json`, `e156-leak0.3803.json`, `e156-leak0.3134.json`, `e156-unfiltered.json`
(dips kept), `dips.json`, `gen/` (the images, `counts.json`, `gen.sha256`, committed with the registration), `passes/p156*` (raw: per-run records,
telemetry, block.json, binaries; `p15601` the smoke, `p15602` the stop-path test with its four STOP lines), `logs/` (session log, queue, smoke, the
two config reads, the preflight, binaries), `posthoc/posthoc_e156.py` and `posthoc.txt` (post hoc, labelled: the before/after errors, the one-price
fit, the session's peaks).

*(Dated note, Tue 3 Nov 2026, after verification.)* Added: `posthoc/corrections_e156.py`, `posthoc/corrections.txt` and
`posthoc/corrections.json` (post hoc, labelled: the numbers of the corrections below), and a dated note beside the registration,
[`tools/claims-v3/e156/README.md.dated-note.md`](../../../../tools/claims-v3/e156/README.md.dated-note.md). The registration's bytes stay as
registered.

## Corrections after verification (Tue 3 Nov 2026)

*Desk only, about 16:20-17:10 PST: no card, no device command, nothing re-run on a box. An independent verifier re-derived E156 from the
committed data and found its registered verdicts sound. Below are the faults it found, each checked again here, and how each is corrected. No
measured, frozen or registered number, prediction or verdict changes. The numbers are in [`posthoc/corrections.txt`](posthoc/corrections.txt),
printed by [`posthoc/corrections_e156.py`](posthoc/corrections_e156.py) (standard library, committed inputs only).*

- **C1 (major): Mac home paths in four committed JSONs.**
  - *The fault:* `e156.json`, `e156-leak0.2936.json`, `e156-leak0.3803.json` and `e156-leak0.3134.json` recorded their input directories
    (the `dirs` field, 10 each) as absolute paths in the desk machine's scratch, where the lane had pointed the registered reduction's work
    dir. They were the only files in the repo with such a path.
  - *The check:* the registered `reduce_e156.sh`, unchanged, was re-run from the top of the repo with its default work dir, `build/e156-dipwork`.
    It writes `dirs` as `build/e156-dipwork/p15610` … `p15619`. It reproduces every number and key of the four files (6,907 numbers in
    each, none different), `e156-unfiltered.json` in every value, and `dips.json` and `runs.csv` byte for byte. `posthoc.txt` also
    reproduces byte for byte.
  - *The correction:* the four files now carry the re-run's `dirs`, and every other byte is the lane's. The reducer builds its over-zeros
    contrasts from a set, so a re-run's key order follows Python's hash seed; the lane's order is kept. No text file in this data dir holds a
    Mac home path (`corrections.txt` C1).
- **C2 (minor): an unresolved card difference stated as fact.**
  - *Where:* §5 ("the pin prices are higher on this card"), What it does ("read 18-29% higher here") and What it changes ("differ between
    the cards by about a fifth"), and the lane's blog point that they "cost 18-29% more".
  - *The data:* card 1 minus aifoundry3, Welch over E156's nine and E139's eight headline passes, board W. `V16` +0.082 [−0.021, +0.184]
    (t 1.81, p 0.10); `Hp` +0.089 [−0.006, +0.183] (t 2.00, p 0.06); `S64` +0.074 [−0.042, +0.190] (p 0.19). No tie's difference is
    resolved: `RH128` reads +0.141 [−0.035, +0.318], and the rest are within ±0.04 W of zero.
  - *Read instead:* the pins' prices read 18-29% higher on card 1, not resolved (the intervals of the difference include 0; one session per
    card).
- **C3 (minor): "its count is settled … not at 128 bits" overstates.**
  - *Reading C* (the 64- plus 128-bit encoded toggles) is excluded only on card 1's primary and its leakage arms, by one pair (`E192`,
    d −0.117 [−0.198, −0.035] W). It is consistent with the dips kept (−0.108 [−0.382, +0.166]). On aifoundry3's E139 passes, with E156's
    k = 1.2857, it is consistent on E139's primary (−0.094 [−0.264, +0.076]), excluded at the 0.2936 W/C arm (−0.210 [−0.386, −0.034]) and
    only just consistent at 0.3803 (−0.246 [−0.493, +0.002]).
  - *The other readings:* the 32-bit count and the pins (B, E) are excluded by `E32` on every arm, the dips kept included. The line edge (F)
    is excluded on the primary and at the leakage arms, but not with the dips kept.
  - *Why it matters for prediction:* on random data reading C would raise the term 1.86 times, by the 128-bit edges' 48 bytes added to the
    64-bit edges' 56. At this session's full read rate that is about +0.11 W: 0.235 W against reading A's 0.127 W, with 4.16 of a byte's
    9 encoded pins differing across an edge.
  - *Read instead:* the 32-bit and pin counts are excluded, and the line edge on the primary; the 128-bit addition is excluded on this card's
    primary only (one pair, one session; not with the dips kept, not on aifoundry3's primary). 64 bits is the reading on present evidence; 64 + 128 bits is not yet
    excluded across cards.
- **C4 (minor): rank 15's rule was applied as price × count, and the README did not say so.**
  - *The difference:* the critic wrote "the frozen +0.185 W per image predicts within 0.05 W": E132's frozen value, for E139's 392-toggle
    images. E156 registered price × count per image instead (+0.152 W for `E7`, 0 for `E32`), quoting the critic exactly. But the header
    here paraphrased the rule as "the frozen price predicts each new image within 0.05 W", and the lane's result said "answered as the critic
    wrote it".
  - *Under the literal +0.185 W:* the new images miss by −0.068 W (`E7`) and −0.215 W (`E32`), FAIL, while E139's images pass on this card
    (+0.014, −0.016 W).
  - *Read instead:* rank 15's next test ran with the critic's 0.05 W line applied to the frozen term per image (price × count, registered
    before the run). It passes there (−0.035 and −0.030 W). E139's images also pass the literal +0.185 W.
- **C5 (minor): an open clause of item 10 was dropped.**
  - *The fault:* What it changes' item-10 bullet, and the lane's suggested wording for the kinds page, left open only the 1.0 pJ split and the
    256-bit path.
  - *What the kinds page lists:* item 10 also lists "a refit of E99's account with it", with the encoded term. E156 does not answer that,
    and it stays open (the note to What it changes).
- **C6 (minor): the PMIC's over-temperature margin was not disclosed as unmeasured.** No telemetry field reads the PMIC's own temperature,
  which its 75 °C alarm compares. The guard against over-temperature was the registered 72 °C die stop, as E142's corrected README (C3) says
  for this card. E156 ran cooler and lower than E142 did on card 1: board max 59.55 W and shire mean 61 °C, against 62.09 W and 63 °C there,
  with no alarm.
- **C7 (minor): record slips.** None changes an order or a verdict.
  - **(a)** D1 said "two more than projected". It was three: six headline passes projected, nine ran.
  - **(b)** The registration says "Pre-registered … about 05:55 PST". In fact `d55744a5` was committed at 05:46:30 PST and pushed at
    05:46:34 (GitHub's record of the push, 13:46:34 UTC). Both precede the claim (05:47:41-05:47:55), the first device open (05:48:01) and
    the first launch (a heater burn-in at 05:48:24, `passes/p15601/marks.jsonl`). A dated note sits beside the registration, whose bytes
    stay as registered.
  - **(c)** The lane's result said the registration was "pushed 05:46:30". That is its commit time.
  - **(d)** The result named an `et-who` at 06:23:24, which no log holds. The session's closing `et-who` is 06:23:09 (`logs/session.log`
    line 26), and the release ran none of its own (the note to Card and post).
- **O1 (an observation, post hoc, not a fault): why the dips-kept arm moves.**
  - *Where the dips fall:* the 17 in-window dips over the nine headline passes cluster on the encoded-quiet twins (`el_64`, `c3_64`,
    `c3_128`, `e2_64`, `el_32`). 10 of the 17 fall there, though the twins are 5 of the 18 runs a pass (one-sided binomial p 0.007).
  - *The effect:* a dip lowers the power of the run it falls in, and on a twin that raises its pair's contrast. With the dips kept, four of
    the five pairs read higher: `E56` +0.361 W against +0.199, `E32` +0.075 against −0.030, `E192` +0.177 against +0.120, `E7` +0.130
    against +0.117. `E448` reads lower (+0.084 against +0.169), because its own image, `vl_64`, took three dips. So the dips-kept arm is
    biased pair by pair, mostly upward, not only noisier. The registered primary removes dips by E82 A2's rule, which does not look at the
    item, so the primary is unaffected.

**What the corrections do to predicting power and heat.**
- *The term:* none changes. The term tested is still E139's frozen encoded term, and its out-of-sample error on this card and the two new
  images is still 0.033 W rms, against 0.086-0.144 W without it.
- *The description of the model changes twice.* The 128-bit addition is open across cards (C3), and would raise the random-data term about
  1.86 times, about +0.11 W at full read rate. The pins' card difference is unresolved, so it does not justify a card term (C2).
- *Heat:* unchanged, 0.01-0.02 °C for the whole encoded part at card 1's 0.1151 °C per board W.
