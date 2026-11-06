# E180's data README, dated note 2 (Fri 6 Nov 2026; after the data commit and its fix): october-forecast-model's reported arm, read by dated note M2's reader as M2 gives it - its +0.0042 W for his pair lies inside E180-H's interval (+0.027 W [−0.050, +0.104]), and so does 0, so the card cannot tell the model from no difference; it lies inside on the net minion rail and for 4s and 5s above the zeros too, where 0 is inside as well and P above all four; the ladder's price per result bit (E180-L, +0.0097 W [+0.0027, +0.0167]) is the sharper comparison, but M1 and M2 give no per-bit figure for the model, so it is not read there. Reported, never a verdict

*Written on the Intel from about 15:30 PST on Fri 6 Nov 2026, desk only, by the card day's arms lane for E180 (Q149(f), `arms-e180`),
after the data commit `c8a3a6ee` (13:47:01 PST) and the data fix's [dated note 1](README.md.dated-note-1.md) (`210d756e`, 14:49:04).
[`README.md`](README.md), [`SHA256SUMS`](SHA256SUMS), dated note 1 with its list, and every file of step 22 v3's collection and score stay
as committed. The note answers the first bullet of the README's "Not read here" (lines 99-102): october-forecast-model's arm, read after
the data commit by its own registered reader. **It is not a verdict of E180: no E180 rule, threshold or verdict reads it, and no E180
number, rule, verdict or gate reading changes.** The arm's figures were frozen by dated note
[M1](../../../../tools/claims-v3/e180/E180.md.dated-note-M1.md) (`b38d09e3`, 09:49:37 PST), and the way they are read was fixed by dated
note [M2](../../../../tools/claims-v3/e180/E180.md.dated-note-M2.md) (`2b32db9d`, 10:42:13 PST), both before the session's opening config
read (12:54:50 PST, its first datum). The figures come from M2's reader [`arm_m1_e180.py`](../../../../tools/claims-v3/e180/arm_m1_e180.py),
run once into this directory as M2 section 1 gives it (15:32:25 PST, exit 0). It wrote [`arm-m1-e180.md`](arm-m1-e180.md) and
[`arm-m1-e180.json`](arm-m1-e180.json) ("output" below). [`SHA256SUMS-note2`](SHA256SUMS-note2) pins this note and those two files. For the
kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

**Labels.** The arm is **reported**, never a verdict. Its figures are **frozen** (M1's freeze line, below) and its reading is **blind**: M1
and M2 were both committed before E180's first datum. The reader prints E180.md section 5's SIZE words as placements (M2 section 1):
**PASS** means the arm's value lies inside the interval, **FAIL HIGH** above it, **FAIL LOW** below it. Here they say only where a value
lies. They are not E180's verdicts, and the records write "inside", never "it passed". Readings marked **beside** are arithmetic on the
committed record and decide nothing.

The freeze line, as M1 section 1 gives it:

`october-forecast-model, frozen Fri 6 Nov 2026 09:29:14 PST, sha256 498454bda6f5c0658008f5ca1751a515cd19d95a58fdb96c10b0fb011adefb10, covering E180's fadd.ps one-number kinds 4s and 5s (his pair), per instruction (8 lanes), above the fadd.ps zeros, on aifoundry3 and aifoundry1 card 1`

## 1. The reading, as the reader wrote it

Six kept passes (18010-18015), aifoundry3 card 0 at 600 MHz pinned. Before it printed a word, the reader recomputed each statistic from
`reduced-e180-v3.json` and found it equal to `scored-e180.json` to 1e-9 W (M2 section 1). Its table and its five lines, unchanged from
the output:

| reading | statistic per kept pass | mean (W) | 95% interval (W) | the arm (W) | words |
|---|---|---:|---|---:|---|
| E180-H, the board | D(fadd.ps/f_5) - D(fadd.ps/f_4) in each kept pass (E180-H's, on the board) | +0.0270 | -0.0503 to +0.1043 | +0.0042 | **PASS** |
| RA2, the net minion rail | R(fadd.ps/f_5) - R(fadd.ps/f_4) in each kept pass with a rail reading (A1's RA2, the net minion rail) | -0.0160 | -0.0773 to +0.0452 | +0.0042 | **PASS** |
| 4s above zeros, the board | D(fadd.ps/f_4) - D(fadd.ps/zeros) in each kept pass (the scorer's footing for every kind) | +0.0221 | -0.0985 to +0.1427 | +0.0298 | **PASS** |
| 5s above zeros, the board | D(fadd.ps/f_5) - D(fadd.ps/zeros) in each kept pass (the scorer's footing for every kind) | +0.0491 | -0.0602 to +0.1583 | +0.0340 | **PASS** |

- **Beside E180-H:** against 0 it reads NOT RESOLVED (E180-H's SIGN; the scorer's E180-H: NOT RESOLVED, SIZE FAIL HIGH). Placed as the arm is, no difference (0 W) reads PASS and the arm PASS: they read alike (they read differently only when an end of the interval falls between 0 and the arm). The half-width, 0.0773 W, is 19x the arm.
- **The 00:00:55 frozen sentence's bracket** (5s - 4s 8.8 to 10.4 fJ, +0.0040 to +0.0048 W): PASS at its low end, PASS at its high end; the same words across it as at M1's value.
- **The footing:** each kind is read as D(kind) - D(fadd.ps/zeros). D(4s) alone averages 10.7969 W over idle and is never compared with the arm.
- **Beside the arm:** the arm is a near-cancellation: the bubble term, 3x the net (+27.38 fJ against +9.09 fJ), is labelled 'assumed' in the model's ledger ('modelled' in its per-instruction table), and the model gives no band; 10% on the bubble term moves the arm by 30%, 10% on the leakage term by 20%.
- **The power, as the records quote it:** A1 section 2: with no difference E180-H reads POSITIVE 0.02 at 6 passes at every noise level; its half-width is 0.103-0.198 W at 6 passes (0.121-0.232 W at 5), 25-48x the arm (29-56x at 5).

## 2. What it says: inside, and so is no difference

1. **His pair.** october-forecast-model's +0.0042 W for 5s − 4s lies inside E180-H's interval, +0.0270 W [−0.0503, +0.1043]. **So does
   0 W.** The card cannot tell the model from no difference here. Placed the same way, the two read alike, as M1 section 6 and M2 section
   3 said they would unless an end of the interval fell between 0 and +0.0042 W; neither end does. E180-H's own reading against 0 is NOT
   RESOLVED. Nor does the interval tell the model from E180's arms E (+0.0687 W), F (+0.0352 W) or A (+0.0192 W): they lie inside too
   (`scored-e180.json` › `rules` › `E180-H` › `size`).
2. **What the card does tell apart is the model from P.** P's registered +0.1649 W lies above the interval (E180-H's SIZE FAIL HIGH), and
   so does C's +0.2197 W. M2 section 3 said this was what E180 could tell.
3. **The same on the other three readings.** Beside, each forecast is placed against the interval the reader printed. The rail's forecasts
   are the scorer's for RA2 (`reported_v2` › `RA2_his_pair` › `R`); the kinds' are its reported forecasts (`reported` › `kinds`).

   | reading | interval (W) | october-forecast-model | 0 W | P | C, E, F, A |
   |---|---|---|---|---|---|
   | E180-H, the board | −0.0503 to +0.1043 | +0.0042, inside | inside | +0.1649, above | C above; E, F, A inside |
   | RA2, the net minion rail | −0.0773 to +0.0452 | +0.0042, inside | inside | +0.1277, above | C, E above; F, A inside |
   | 4s above zeros, the board | −0.0985 to +0.1427 | +0.0298, inside | inside | +0.3298, above | C above; E, F, A inside |
   | 5s above zeros, the board | −0.0602 to +0.1583 | +0.0340, inside | inside | +0.4947, above | C, E above; F, A inside |

   On all four, 0 lies inside with the model, and P lies above.
4. **The 00:00:55 frozen sentence's bracket** (+0.0040 to +0.0048 W) reads inside at both ends, as M1's own value does. So the reading at
   M1's frozen value is the reading at every value the frozen sentence allows. In M2 section 2's words, M1's figures are "consistent with
   the 00:00:55 frozen sentence at its rounding (5s - 4s 8.8-10.4 fJ, +0.0040 to +0.0048 W)", never "the same".
5. **The resolution.** M2 section 3's sentence, which it asked the README to carry: "With no difference E180-H reads POSITIVE 0.02 at 6
   passes at every noise level (A1 section 2); its 6-pass half-width, 0.103-0.198 W, is 25-48x the arm." Those are A1's half-widths,
   expected before the data. The session's own was smaller, **0.0773 W, 19x the arm** (the six passes' sd 0.074 W). The arm is still
   about a nineteenth of the half-width, so this reading cannot separate it from 0.
6. **The arm itself.** M2 section 4's line: "The arm is a near-cancellation: the bubble term, 3x the net, is labelled assumed in the
   model's ledger, and the model gives no band." In the output's figures, the bubbles give +27.38 fJ against a net of +9.09 fJ, and 10%
   on the bubble term moves the arm by 30%.

## 3. The sharper comparison is the ladder's price per result bit, and M1 and M2 give the model no figure there

- **The ladder resolves what his pair cannot.** E180-L, the OLS slope of D(kind) − D(zeros) on the result's 1-bits over the 21 fadd.ps
  one-number kinds, reads **+0.0097 W a result 1-bit [+0.0027, +0.0167]** (`scored-e180.json` › `rules` › `E180-L`: +0.009693
  [+0.002734, +0.016652]). Its interval lies above 0 and below every registered arm: P 0.1649, C 0.2197, E 0.0687, F 0.0352 and A
  0.0192 W a bit, SIZE FAIL HIGH for every arm, inside none. Its half-width, 0.0070 W a bit, is about an eleventh of his pair's 0.0773 W.
  On the net minion rail, A1's reported RA3 reads the ladder at +0.0093 W a bit [+0.0060, +0.0125], with every arm above. So it is the
  ladder, not his pair, where a model's value-dependent price can be told from no difference and from P.
- **Neither M1 nor M2 gives october-forecast-model's figure per result bit.** M1 section 5: "It gives numbers for 4s and 5s only. This
  note derives none for any other kind, so E180-L, E180-O, E180-R, E180-E, E180-I, E180-X and E180-A are not read against it." M1 quotes
  the model's rule for other constants (the bubbles between instructions, 2 x the popcount of the sum per bubble, and the held state's
  leakage), but no energy per result bit. M2 adds none: its reader reads the four lines of section 1 and nothing else.
- **So E180-L is not read against the model here,** and no per-bit figure is derived from its 4s and 5s after the data. That would be
  post hoc, and M1 rules it out. If the model states a per-bit figure and it is frozen before the data it is read against, the ladder
  becomes the model's test. The next one-number fadd.ps registration, with the price near 0.0097 W a result bit as its blind number, is
  the place for it.

## Lines for the records

1. **october-forecast-model on E180** (a reported arm, frozen by M1 at 09:29:14 PST and read by M2's reader; blind): his pair's 5s − 4s,
   +0.0042 W, lies inside E180-H's +0.027 W [−0.050, +0.104], **and so does 0**, so the card cannot tell the model from no difference
   there. It lies inside on the net minion rail (−0.016 W [−0.077, +0.045]) and for 4s and 5s above the zeros (+0.030 against +0.022 W
   [−0.099, +0.143]; +0.034 against +0.049 W [−0.060, +0.158]); 0 lies inside all four, and P above all four. The 00:00:55 sentence's
   bracket reads the same. Never "it passed", and never one of E180's verdict words for the model.
2. **The ladder** (E180-L, +0.0097 W a result 1-bit [+0.0027, +0.0167]) is the sharper comparison, but M1 and M2 give no per-bit figure
   for the model, so the model is not read there; none is derived after the data.
3. M1's figures are "consistent with the 00:00:55 frozen sentence at its rounding", never "the same" (M2 section 2). The arm is a
   near-cancellation whose bubble term is labelled assumed (M2 section 4).
4. This note answers the first bullet of the README's "Not read here". The model is named october-forecast-model only.

## Departures and disclosures

- **None from M2's command.** From the top of the tree, at 15:32:25 PST, under Python 3.13.11 as PATH resolves it on the Intel:
  `python3 -B tools/claims-v3/e180/arm_m1_e180.py read --session docs/reports/data/2026-11-06-e180-vector-add-aifoundry3 --write docs/reports/data/2026-11-06-e180-vector-add-aifoundry3`,
  exit 0. Its `check` read CHECK PASS first (M1's JSON and `power_e180.py` at their pinned sha256). A second run into this directory was
  refused (exit 4) and changed nothing.
- **Before anything was written here,** the reader ran into a scratch directory under both of the Intel's interpreters. Under 3.13 its
  two outputs and its printed lines equal those written here byte for byte, and equal critic-q149's own scratch run of the same command
  (15:02:37 PST). M2's self-test re-ran 15 of 15 under both, its output byte for byte
  [`logs/selftest-arm-m1-e180.txt`](../../../../tools/claims-v3/e180/logs/selftest-arm-m1-e180.txt).
- **The interpreter.** Under the Intel's `/usr/bin/python3` (3.9.6), `arm-m1-e180.md` and the printed lines are byte for byte these.
  `arm-m1-e180.json` differs in three numbers of the 5s reading (its interval's two ends and its half-width), by 2.8e-17 W. The cause is
  the last bit of the standard library's `statistics.stdev`: 3.13 gives 0.10409890391025307 and 3.9 gives 0.10409890391025306, the value
  `scored-e180.json` holds. No printed figure or word moves.
- **Compute:** the round's local slot, nice 10, one core, a few seconds a job. No card, lab box or post.

## What does not change

Every reading, verdict, gate, stop and figure of the README and of dated note 1 stands. With this note's four files in the directory,
`SHA256SUMS` reads 89 of 89 OK, `SHA256SUMS-note1` 4 of 4 and `SHA256SUMS-note2` 3 of 3. E180's hash lists (registration 71, kit 55, A1
41, kit note 1 90, kit note 2 96, M1 6, M2 30) read OK. The scorer reads none of these files, so no scored figure can move.

## Files and re-run

| file | what |
|---|---|
| `README.md.dated-note-2.md` | this note |
| [`arm-m1-e180.md`](arm-m1-e180.md) | the reader's table and its five lines, as written |
| [`arm-m1-e180.json`](arm-m1-e180.json) | the same readings with each pass's figure, the arm's values, the bracket, and its inputs' names and sha256 |
| [`SHA256SUMS-note2`](SHA256SUMS-note2) | the three files above |

From the top of the tree, standard library only, a second or two:
- `python3 -B tools/claims-v3/e180/arm_m1_e180.py check`;
- `python3 -B tools/claims-v3/e180/arm_m1_e180.py read --session docs/reports/data/2026-11-06-e180-vector-add-aifoundry3 --write <an empty directory>`.
  It never writes over a file, so a run into this directory now exits 4. Under Python 3.13 it writes both files byte for byte these;
- in this directory, `shasum -a 256 -c SHA256SUMS-note2`.

SPDX-License-Identifier: Apache-2.0
