# Dated note 1 to the frozen terms' E215 scores: the verifier's corrections, and how to read the README with them

*Thu 19 Nov 2026, Pacific time. Written by land-score-terms-e215 (round Q231) from 16:08 PST, after verify-score-terms-e215 held this
folder WITH FIXES (15:24-15:51 PST). Desk only: no card, no simulator. Interpreter `/usr/bin/python3` 3.12.3, standard library only,
single-threaded. This note changes no file of the folder: the README, the declaration, the scorer and its outputs are committed byte for
byte as score-terms-e215 left them. Every number in it is REPORTED, as in the README; the readings it adds or relabels are post hoc.*

## What is committed here

- **The folder** is score-terms-e215's land, byte for byte: 10 files and `SHA256SUMS` (sha256 `a26493186fa67319...`, 10 of 10 OK),
  last written at 15:22 PST.
- **The verification.** verify-score-terms-e215 re-derived every figure with its own code, from E215's raw session files and the
  frozen files:
  - the measured side: 1,710 of 1,710 run fields equal `data-e215.json`, and 1,880 of 1,880 point fields equal the card lanes' scorer
    outputs;
  - the four CSVs: 6,946 of 6,946 cells equal its values at their printed precision;
  - the scorer, re-run from its own lab-shaped tree, re-made the 5 text files byte for byte and the JSON equal but its `made` time;
  - sha256 first: the 6 frozen files equal their posts (09:32:02, 09:32:47 and 10:31:36 PST), all before E215's first card commands
    (12:05:24 and 13:41:24 PST).

  Its fixes are wording and labels. No number changes, and none of them changes a verdict.
- **This note** and `SHA256SUMS-note1` (its sha256) are the only new files beside the land.

## 1. The headline (the verifier's finding 1, low)

Read the README's title and answer 1 ("the gemmLnc term held blind, in direction and roughly in size") as:

**The gemmLnc term cut the W error at E215's five gemmLnc points from 34.7% to 8.2% rms (TOO FEW for a sign test). Its size held at card
1's one point and is 1.4-1.55x too large on aifoundry3.**

- **The direction was expected before the data.** E215.md section 7 (at 4cb2c2ad) states, before any datum: "at the committed gemmLnc
  points the measured W over idle is 1.13-1.80x MM1-v3.1's in sample (1.13-1.82x held out; 9 points)". So the 5 of 5 positive excesses
  test MM1-v3.1's known gap more than the term.
- **The size held at one point only.** That point is b013 on card 1 (F3 +0.8%). Its two runs differ by 1.5% in W.
- **On aifoundry3 the term is too large at 4 of 4 points.** The measured excess is 0.645-0.709 of the term there, and the W bias is
  -8.62%.

## 2. 'Both' against MM1-v3 re-counts part 1 (finding 2, low)

This concerns part 3's registered cells "**CLOSER 11/2/37 (p 0.022)**" (H4) and "**CLOSER 11/1/38 (p 0.0063)**" (H5), and answer 6's
"closer than MM1-v3 at 11/2/37 (p 0.022)".

- **What 'both' is there.** Every registered point is on the full chip, where F1's factor is exactly 1. So on the registered points
  'both' is F3 at the 5 gemmLnc points and MM1-v3.1 everywhere else.
- **Where the 11 come from.** They are part 1's 5 plus MM1-v3.1's own lead over MM1-v3, which is H4 6/2/42 (TOO FEW).
- **Without the five gemmLnc points** 'both' against MM1-v3 is TOO FEW: H4 6/2/37 (p 0.29) and H5 6/1/38 (p 0.125).

Read those cells with this beside them. They are not independent evidence for the composition.

## 3. Readings beyond the declaration (finding 3, low)

`DECLARED-scoring-terms-e215.md` names only part 1's quantities, its sign tests and the sibling forms. README line 20 says the post hoc
label marks every reading beyond the declaration, but these readings carry no such label. Read each one as **post hoc, beyond the
declaration**:

1. **The cooperative twins' W and wall ratios** (part 1, "The cooperative twins").
2. **verify-lnc's nearest-analog comparison** (answer 3; the "analog - measured" column of part 1's size table and its bullets).
3. **The measured / predicted excess ratios** behind answer 2 ("The NB form held") and the ratio columns of part 1's size table.
   Answer 2 reads 4 points on one card (aifoundry3), two shapes per NB regime: a024 and a026 at NB 15 and 12, and a031 and a032 at NB 1.
4. **The card-factor reading** (answer 2's "What stays open", and part 1's size bullets on the two cards).
5. **The c1/c2 split** (part 1, "What the data do not separate").

**One rule for verify-lnc's two unposted desk readings.** The nearest-analog reading was never frozen in a posted file. Nor were the
forms G1-G6 and the step at NB of 3 or less. So none of them is a blind test here.

- The analog's numbers stay as post hoc context. Read answer 3's "held" and "did not hold" as "agreed" and "disagreed", post hoc.
- G1-G6 and the step stay NOT SCORED.

## 4. The layout reading leaves out MM1-v3 (finding 4, low)

Add these two head-to-heads to part 2. They are REPORTED and post hoc: the verifier's run of the declared rule on the same 28 subset-mask
points (wall cycles, candidate / MM1-v3 / ties, tie 0.005; the seconds give the same verdicts).

| candidate against MM1-v3 | pooled (28) | arm A (20) | arm B (8) |
|---|---|---|---|
| N1+N2 | **MM1-v3 CLOSER 6/17/5 (p 0.035)** | NOT DECIDED 5/12/3 | TOO FEW 1/5/2 |
| G1+N1 | **MM1-v3 CLOSER 6/18/4 (p 0.023)** | MM1-v3 CLOSER 4/13/3 (p 0.049) | TOO FEW 2/5/1 |

**Where MM1-v3 gains.** The gain sits at the 24-28-shire rows (14): MM1-v3 8.12%, N1+N2 8.93% and MM1-v3.1 9.90% rms. At the 2-15-shire
rows (14), MM1-v3 and MM1-v3.1 both read 9.14%.

**The reading, tempered.** N1+N2 is the one candidate decided closer than MM1-v3.1 (18/4/6), but no frozen layout form beats MM1-v3 on
these points. MM1-v3's own fit, with no shire-count term, does better still.

## 5. Wording, counts and rounding (findings 5-8, nits)

1. **"It moved the wrong way at 12 of 14"** (answer 4, the 14 rows of 2-15 shires). Read: *F1 ended farther from the measurement at 12
   of 14.*
   - At 11 it moved the wrong way.
   - At b005 it moved toward the measurement and overshot it: +0.25% became -1.12%.
   - At 2 it moved closer.

   Part 2's "it moved away from the measurement at 12 of 14" and the by-shire table's "2 of 14" closer say the same.
2. **"-9% to -11% at the 28-shire masks"** (part 2's "Every model runs E215's subset points too slow", the pairs section's "shared
   offset at these masks is 9-11%", and part 3's Reading).
   - It holds for MM1-v3.1, F1, N3, G1 and fresh24: -9.1% to -11.3%.
   - The other models' ranges: MM1-v3 -7.2% to -9.8%, T7 -7.9% to -10.1%, N1+N2 -8.3% to -10.4% and G1+N1 -8.8% to -11.2%.
   - The pooled bias range "-6.4% to -7.8%" holds for every model but T7, which reads -1.27%.
3. **"MM1-v3.1 at the other 61"** ("The models as scored"). Read 57 scored points; 61 counts the 4 references.
4. **"At or after 595fcb59"** (the re-run line under "Files"). Read *at or after 4f648f24*: arm B's data commit, the last of the score's
   inputs. 595fcb59 predates it.
5. **"Posted sha256 10 of 10 equal"** (line 2 of `scores-terms-e215.txt`).
   - What the 10 are: the 6 posted frozen files, plus E215's 4 data files (`data-e215.json` and `labels-e215.json` of each arm) checked
     against their folders' SHA256SUMS.
   - What they leave out: the two posted hashes that do not re-verify, the layout land's `d5ec254d` and the controls' maker's `4fb92de3`
     (README, "Inputs and their checks").
6. **Naming.** In answer 2 and part 1, F1, F2 and F4 mean *gemmLnc form F1, F2, F4*: the gemmLnc term's sibling forms. This covers the
   F1, F2 and F4 columns, the rms table's "form F1/F2/F4" rows, the size table's ratio columns, and "Against its sibling forms F1, F2 and
   F4". Everywhere else (answers 4-6, parts 2 and 3) F1 is the contention term.
7. **Rounding.** Every figure is to be rounded once, from full precision.
   - **How the double rounding arose.** The scorer stores its statistics at 3 decimals, and the README rounded some of those values
     again, to 2. Where the 3-decimal value ends in 5, the print can be 0.01 off.
   - **The check.** This lane extracted the committed inputs itself, from the lab's git objects at 8bde0182, 2c971828, aaeaa495,
     595fcb59, 8355db15 and 4f648f24. From that tree the landed scorer, unchanged, re-made this folder's 5 text files byte for byte,
     and its JSON equal but `made`. A copy of the scorer with its two rounding helpers made the identity then gave every statistic at
     full precision.
   - **What it found.** All 570 two-decimal cells were checked: the statistics tables of parts 1-3, the per-arm sentence under part 1's
     rms table, and part 2's per-point table. **27 cells differ, each by 0.01 in the last digit**, and every one is a double rounding.
     None changes a verdict, a comparison or a reading. The verifier named 7 of them (marked V); this check found the other 20.

| README line | table, row | column | printed | read |
|---|---|---|---|---|
| 147 | part 1 rms, MM1-v3.1 | J at rest, t forecast | 13.21% | 13.20% |
| 148 | part 1 rms, MM1-v3 | J over idle given t, bias | +31.27 | +31.28 |
| 149 | part 1 rms, F3 | J at rest given t | 4.33% | 4.34% (V) |
| 152 | part 1 rms, form F4 | J over idle, t forecast, bias | -6.55 | -6.56 (V) |
| 154 | part 1, by arm | arm A, F3's W bias | -8.63% | -8.62% |
| 238 | part 2 points, a003 | N1+N2 | -8.88 | -8.87 |
| 241 | part 2 points, a006 | F1 | -9.22 | -9.23 |
| 243 | part 2 points, a008 | G1 | -9.12 | -9.11 |
| 247 | part 2 points, a012 | G1+N1 | +0.48 | +0.49 |
| 248 | part 2 points, a013 | G1+N1 | -12.06 | -12.07 |
| 249 | part 2 points, a014 | G1+N1 | +4.82 | +4.81 |
| 252 | part 2 points, a017 | N3 | +6.87 | +6.86 |
| 252 | part 2 points, a017 | fresh24 | +7.54 | +7.55 |
| 254 | part 2 points, a019 | F1 | -3.73 | -3.74 |
| 258 | part 2 points, b003 | MM1-v3.1 | -11.24 | -11.25 |
| 259 | part 2 points, b004 | MM1-v3 | -9.40 | -9.41 |
| 259 | part 2 points, b004 | G1 | -10.99 | -11.00 |
| 274 | part 2 rms, F1 | arm B wall (8) | 10.49% | 10.50% |
| 276 | part 2 rms, N1+N2 | seconds, bias | -6.97 | -6.98 |
| 278 | part 2 rms, G1+N1 | arm A wall (20) | 8.94% | 8.93% |
| 278 | part 2 rms, G1+N1 | arm B wall (8) | 9.68% | 9.67% |
| 280 | part 2 rms, T7 | seconds, bias | -1.19 | -1.18 |
| 341 | part 3, registered, both | J over idle, t forecast, bias | -2.35 | -2.36 (V) |
| 341 | part 3, registered, both | J at rest given t, bias | -1.12 | -1.13 (V) |
| 347 | part 3, all 90, both | counter mean | 8.40% | 8.41% (V) |
| 368 | part 3 per arm, registered B, both | J at rest, t forecast | 5.23% | 5.22% (V) |
| 369 | part 3 per arm, post hoc A, MM1-v3.1 | wall cycles | 9.17 | 9.16 (V; part 2's 9.16% is right) |

## 6. Two items for the record (findings 9 and 10, info)

1. **The pair noise** ("What this cannot say"). On arm B the README's "if anything wide" is about 13x wide.
   - **Where the noise comes from.** The declared noise is arm B's pooled within-point sd, 0.00207, and 91% of it comes from b013, the
     gemmLnc point, whose two runs differ by 1.7% in wall cycles.
   - **Narrower measures.** Without the gemmLnc points the sd is 0.00063. The 8 subset points' own two runs give 0.00016 (8 degrees of
     freedom).
   - **On the narrowest noise.** All 6 of arm B's pairs differ beyond noise (22 of 35 overall). G1 then orders 6, misorders 15 and cannot
     tell 1 apart (G1+N1 not re-counted).

   The reading stands: the models that give each set one value cannot order any pair, and G1 misorders more pairs than it orders.
2. **E216's registration** ("The models as scored": "that registration was not yet on GitHub main when this was written").
   - **It has landed since.** It reached GitHub main as 1e3e02b0 at 15:32:32 PST, with its kit at 59f5288b (15:32:42).
   - **Its composition is the one scored here.** Its `composed()` and docstring equal reg-e216's 10:53:35 PST draft byte for byte, and
     equal the 'both' scored here, by the verifier's check.

   So the README's 'both' is E216's registered composition.

SPDX-License-Identifier: Apache-2.0
