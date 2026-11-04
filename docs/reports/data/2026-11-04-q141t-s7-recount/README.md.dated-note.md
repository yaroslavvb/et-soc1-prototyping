# Dated note beside README.md (Wed 4 Nov 2026, about 12:20 PST; Q141(t)'s fix pass)

*README.md (`67d5e44f`) stays as committed. This note corrects three of its statements, all found by the lane's verifier before any
pool-7 data existed. No count, prediction, rule or frozen number changes. The readings' amendment is
[`REGISTRATION.md.dated-note-2.md`](REGISTRATION.md.dated-note-2.md) (A1), committed with this note.*

## 1. The direction of the 27-point move

README Results 1 and 5 call k = P3 − P27 the move. The move from the three-point counts to the 27-point counts is P27 − P3 = −k, the
opposite sign.

| tiles | k = P3 − P27 (the README's figures) | what the 27-point counts do to D (P27 − P3) |
|---|---|---|
| S7, aifoundry3 | −0.520 to +0.301 W | **−0.301 to +0.520 W** |
| S7, card 1 | −0.500 to +0.289 W | **−0.289 to +0.500 W** |
| b20-on-1/3 under A = 1.5 | +0.390 W (card 1 +0.375) | **−0.390 W** (card 1 −0.375) |
| the 4.5 s rise, the 8 tiles | k_dT −0.061 to +0.046 °C (card 1 −0.058 to +0.043) | **−0.046 to +0.061 °C** (card 1 −0.043 to +0.058) |

**Per tile on aifoundry3:**
- The 27-point counts **raise** D on:
  - b22_third (+0.520 W);
  - b20_seventh (+0.341);
  - b20_pi (+0.311);
  - fp16 b8_pi (+0.091);
  - b20_full (+0.090).
- They **lower** it on:
  - b20-on-1/3 (−0.390);
  - b20_one (−0.301);
  - fp16 b9_one (−0.109).
- So where counting is the cause, E163's measured D should sit above M9's frozen P3 on the first five and below it on the last three.

**What was right:** every k in the README's table, the 0.29 W rms, and "the three-point counts read these tiles 0.135 ± 0.085 W low".

**For the records:** use the k wording, "k = P3 − P27 runs −0.52 to +0.30 W".

**The commit message:** `67d5e44f`'s pushed message carries the same inverted wording and cannot change:
- "move M9's D by -0.52 to +0.30 W";
- "+0.39 W on b20-on-1/3";
- "the rise moves by -0.06 to +0.05 C".

## 2. Which scorer reads which hand-off file

**What the README says:** Results 1 and its Files table say `arm/arm27-aifoundry3.json` "(and `arm27-aifoundry1c1.json`)" is the
form `score_e163.py --arm27` reads.

**What is so:** `score_e163.py` is aifoundry3's scorer only. E164's `score_e164.py` has no `--arm27`. It reads card 1's file through
`--s-recount`, whose `load_recount` takes {tile: float}.

**The three routes:**

| run | command | reported in |
|---|---|---|
| E163 (aifoundry3) | `bash tools/claims-v3/e163/collect_e163.sh <raw copy> docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json`, which passes `score_e163.py --arm27` | scored.json `primary.primary.reported_arm27` |
| E164 (aifoundry1 card 1) | `E164_S_RECOUNT=docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json bash tools/claims-v3/e164/collect_e164.sh <raw dir> …`, which passes `score_e164.py --s-recount` | scored.json `primary.reported_s_recount_arm` |
| R1-R6 and heat, both cards | `python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/score_s7arm_a1.py --a3 <E163 scored.json> --c1 <E164 scored.json> --out <score-s7arm-a1.json>` | A1's readings |

- `score_s7arm.py` and its wrapper read both scored forms: E163's rows sit under `primary.primary` and E164's under `primary`. The
  wrapper's self-test (T5) runs both scorers on simulated sessions and reads all 8 tiles from each, with M9's predictions equal to P3.
- `score_s7arm.py --a3 … --c1 …` (README § Re-run) still runs, but its R5 and heat lines are superseded by A1. Use the wrapper.
- `67d5e44f`'s message says "arm/arm27-<card>.json is the form score_e163.py --arm27 reads". It cannot change.

## 3. Two nits

**e(27)/e(81)'s median** (`step81/`):
- Over the 10 tiles it is **1.75**: 1.7536, the mean of the 5th and 6th values.
- The figure 1.76 is the upper middle value, the 6th (`run_recount_rule.py` takes `sorted(rats)[len(rats) // 2]`). It appears in
  `summary81.json` (`e27_over_e81_median`), `summary81.txt`, `step81/README.md` and `9c7ae1f2`'s message.
- Either way the ratio is near the 1/√N law's 1.73.
- Records quote "median 1.75 (upper middle 1.76)". [`step81/README.md.dated-note.md`](step81/README.md.dated-note.md) says the same
  beside that file.

**u on aifoundry3, two rows of the README's table:**
- There u equals e(27) by definition, yet two rows print them 0.001 apart:
  - `fp32.b_onebit_b20_seventh`: e(27) 0.241, u 0.240;
  - `fp32.b_onebit_b20_third_a1p5`: e(27) 0.196, u 0.197.
- That is double rounding: `arm-s7.json` stores u to 4 decimals (0.2405 and 0.1965), and the table prints those to 3.
- To 3 decimals both are **0.241** and **0.196** (e(27) is 0.24055 and 0.19650 in `recount-s7.json`).
- Card 1's u (0.231 and 0.189) is right, and the frozen `u_w` values the scorers use are unchanged.

## 4. The readings are amended (A1)

[`REGISTRATION.md.dated-note-2.md`](REGISTRATION.md.dated-note-2.md) makes three changes:
- **A1-1:** R5 is read only where R2-R4 are, and over all four bit-20 tiles. A 3-tile R5 is reported as the departure R5-3, never
  read.
- **A1-2:** heat gets power's R1 and R2, with intervals, per card and pooled.
- **A1-3:** R5m is reported beside R5. When no base-word price exists, R5 reads M9's ordinary per-tile error as one in 36-39% of
  draws; R5m reads at 5.5-6.3%.

The wrapper is [`score_s7arm_a1.py`](score_s7arm_a1.py). Its self-test, [`selftest-score-s7arm-a1.txt`](selftest-score-s7arm-a1.txt)
with the JSON beside it, gives PASS. It was made with macOS's `/usr/bin/python3` 3.9, as the lane's other outputs were. Under 3.13 the
text is identical but for the version line, and a few JSON floats differ in their last digit.

```
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/score_s7arm_a1.py --selftest \
    --out docs/reports/data/2026-11-04-q141t-s7-recount/selftest-score-s7arm-a1.json \
    > docs/reports/data/2026-11-04-q141t-s7-recount/selftest-score-s7arm-a1.txt
```
